import os
import re
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any

import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss

# New imports for images
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO

# New imports for tables
import csv
import pdfplumber


def extract_text_pages(pdf_path: str) -> List[str]:
    reader = PdfReader(pdf_path)
    page_texts: List[str] = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        page_texts.append(txt)
    return page_texts


def clean_text(raw_text: str) -> str:
    text = raw_text
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[\t\x0b\x0c\u00A0]+", " ", text)
    text = re.sub(r"[ ]{2,}", " ", text)
    lines = [ln.strip() for ln in text.split("\n")]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)


def save_text(text: str, out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)


def split_page_text_into_chunks(text: str, page_num: int, chunk_size: int = 800, chunk_overlap: int = 150) -> List[Dict[str, Any]]:
    if chunk_overlap >= chunk_size:
        chunk_overlap = max(0, chunk_size // 4)
    words = text.split()
    chunks: List[Dict[str, Any]] = []
    start = 0
    while start < len(words):
        end = min(len(words), start + chunk_size)
        chunk_text = " ".join(words[start:end])
        chunks.append({"text": chunk_text, "page": page_num})
        if end == len(words):
            break
        start = end - chunk_overlap
    return chunks


def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    return index


def embed_texts(texts: List[str], model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> np.ndarray:
    if not texts:
        return np.zeros((0, 384), dtype="float32")
    model = SentenceTransformer(model_name)
    vectors = model.encode(texts, batch_size=64, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=False)
    return vectors.astype("float32")

# ---------------- Image pipeline ----------------

def extract_images_from_pdf(pdf_path: str, out_dir: str) -> List[Dict[str, Any]]:
    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    images_meta: List[Dict[str, Any]] = []
    for page_index in range(len(doc)):
        page = doc[page_index]
        images = page.get_images(full=True)
        for image_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image.get("image")
            img_ext = base_image.get("ext", "png")
            image = Image.open(BytesIO(img_bytes)).convert("RGB")
            out_path = os.path.join(out_dir, f"page{page_index+1}_img{image_index+1}.{img_ext}")
            image.save(out_path, format="PNG" if img_ext.lower() == "png" else "JPEG", optimize=True)
            images_meta.append({"path": out_path, "page": page_index + 1})
    doc.close()
    return images_meta


def embed_images(image_paths: List[str], model_name: str = "clip-ViT-B-32") -> np.ndarray:
    if not image_paths:
        return np.zeros((0, 512), dtype="float32")
    model = SentenceTransformer(model_name)
    images = [Image.open(p).convert("RGB") for p in image_paths]
    vectors = model.encode(images, batch_size=16, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=False)
    return vectors.astype("float32")


def persist_faiss(index: faiss.Index, meta: List[Dict[str, Any]], out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    faiss.write_index(index, os.path.join(out_dir, "index.faiss"))
    with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump({"items": meta}, f, ensure_ascii=False, indent=2)

# ---------------- Table pipeline ----------------

def table_to_markdown(table_rows: List[List[str]]) -> str:
    if not table_rows:
        return ""
    headers = [str(h) if h is not None else "" for h in table_rows[0]]
    md_lines = ["| " + " | ".join(headers) + " |",
                "| " + " | ".join(["---" for _ in headers]) + " |"]
    for row in table_rows[1:]:
        cells = [str(c) if c is not None else "" for c in row]
        md_lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(md_lines)


def extract_tables_from_pdf(pdf_path: str, out_dir: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    os.makedirs(out_dir, exist_ok=True)
    csv_paths: List[str] = []
    tables_meta: List[Dict[str, Any]] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages, start=1):
            try:
                tables = []
                single = page.extract_table()
                if single:
                    tables.append(single)
                multi = page.extract_tables() or []
                tables.extend([t for t in multi if t])
                for t_idx, t in enumerate(tables, start=1):
                    if not t:
                        continue
                    csv_path = os.path.join(out_dir, f"page{page_idx}_table{t_idx}.csv")
                    with open(csv_path, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        for row in t:
                            writer.writerow(["" if cell is None else str(cell).strip() for cell in row])
                    csv_paths.append(csv_path)
                    md = table_to_markdown(t)
                    tables_meta.append({"markdown": md, "page": page_idx, "csv_path": csv_path})
            except Exception:
                continue
    with open(os.path.join(out_dir, "tables.json"), "w", encoding="utf-8") as jf:
        json.dump({"csv_files": csv_paths, "tables": tables_meta}, jf, ensure_ascii=False, indent=2)
    return csv_paths, tables_meta



def process(pdf_path: str) -> None:
    pdf_path = str(Path(pdf_path).expanduser())
    base = Path(pdf_path).with_suffix("")
    txt_path = f"{base}.txt"
    vectordb_dir = f"{base}_faiss"
    images_dir = f"{base}_images"
    image_index_dir = f"{base}_faiss_images"
    tables_dir = f"{base}_tables"
    table_index_dir = f"{base}_faiss_tables"

    # Text pipeline with page-aware chunking
    page_texts_raw = extract_text_pages(pdf_path)
    page_texts_clean = [clean_text(t) for t in page_texts_raw]
    save_text("\n\n".join(page_texts_clean), txt_path)

    text_items: List[Dict[str, Any]] = []
    for i, page_text in enumerate(page_texts_clean, start=1):
        chunks = split_page_text_into_chunks(page_text, page_num=i)
        text_items.extend(chunks)
    text_vectors = embed_texts([it["text"] for it in text_items])
    text_index = build_faiss_index(text_vectors)
    persist_faiss(text_index, text_items, vectordb_dir)

    # Image pipeline
    image_items = extract_images_from_pdf(pdf_path, images_dir)
    img_vectors = embed_images([im["path"] for im in image_items])
    if img_vectors.shape[0] > 0:
        img_index = build_faiss_index(img_vectors)
        persist_faiss(img_index, image_items, image_index_dir)

    # Table pipeline
    _, tables_meta = extract_tables_from_pdf(pdf_path, tables_dir)
    tbl_vectors = embed_texts([t["markdown"] for t in tables_meta])
    if tbl_vectors.shape[0] > 0:
        tbl_index = build_faiss_index(tbl_vectors)
        persist_faiss(tbl_index, tables_meta, table_index_dir)

    print(json.dumps({
        "txt_path": txt_path,
        "faiss_text_dir": vectordb_dir,
        "num_text_chunks": len(text_items),
        "images_dir": images_dir,
        "faiss_image_dir": image_index_dir,
        "num_images": len(image_items),
        "tables_dir": tables_dir,
        "faiss_table_dir": table_index_dir,
        "num_tables": len(tables_meta)
    }, ensure_ascii=False))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path", type=str, help="Path to PDF file")
    args = parser.parse_args()
    process(args.pdf_path)
