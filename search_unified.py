import os
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

import numpy as np
import faiss
from PIL import Image
from sentence_transformers import SentenceTransformer


class ModalityIndex:
    def __init__(self, index_dir: str):
        self.index_dir = index_dir
        self.index = faiss.read_index(os.path.join(index_dir, "index.faiss"))
        with open(os.path.join(index_dir, "meta.json"), "r", encoding="utf-8") as f:
            meta = json.load(f)
        if "items" in meta:
            self.items = meta["items"]
        elif "texts" in meta:
            self.items = [{"text": t} for t in meta["texts"]]
        elif "images" in meta:
            self.items = [{"path": p} for p in meta["images"]]
        elif "tables_markdown" in meta:
            self.items = [{"markdown": m} for m in meta["tables_markdown"]]
        else:
            raise ValueError("Unsupported meta.json schema")


class UnifiedSearcher:
    def __init__(self, base_path: str, w_text: float = 1.0, w_tables: float = 1.0, w_images: float = 1.5):
        base = Path(base_path).with_suffix("")
        self.text_idx = ModalityIndex(f"{base}_faiss").__dict__
        self.image_idx = ModalityIndex(f"{base}_faiss_images").__dict__
        self.table_idx = ModalityIndex(f"{base}_faiss_tables").__dict__
        self.text_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.clip_model = SentenceTransformer("clip-ViT-B-32")
        self.w_text = float(w_text)
        self.w_tables = float(w_tables)
        self.w_images = float(w_images)

    @staticmethod
    def _cosine_search(index: faiss.Index, query_vec: np.ndarray, top_k: int) -> Tuple[np.ndarray, np.ndarray]:
        faiss.normalize_L2(query_vec)
        scores, idxs = index.search(query_vec, top_k)
        return scores[0], idxs[0]

    @staticmethod
    def _normalize_scores(scores: np.ndarray) -> np.ndarray:
        if scores.size == 0:
            return scores
        s = scores - scores.min()
        if s.max() > 0:
            s = s / s.max()
        return s

    def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        q_text_vec = self.text_model.encode([query], convert_to_numpy=True).astype("float32")
        q_clip_vec = self.clip_model.encode([query], convert_to_numpy=True).astype("float32")

        text_scores, text_idxs = self._cosine_search(self.text_idx["index"], q_text_vec, top_k)
        table_scores, table_idxs = self._cosine_search(self.table_idx["index"], q_text_vec, top_k)
        image_scores, image_idxs = self._cosine_search(self.image_idx["index"], q_clip_vec, top_k)

        text_scores = self._normalize_scores(text_scores)
        table_scores = self._normalize_scores(table_scores)
        image_scores = self._normalize_scores(image_scores)

        page_scores: Dict[int, float] = {}
        results: Dict[str, List[Dict[str, Any]]] = {"text": [], "tables": [], "images": []}

        for s, i in zip(text_scores, text_idxs):
            item = self.text_idx["items"][int(i)]
            page = int(item.get("page", -1))
            results["text"].append({"score": float(s), "page": page, "text": item.get("text", "")})
            if page >= 1:
                page_scores[page] = page_scores.get(page, 0.0) + float(s) * self.w_text

        for s, i in zip(table_scores, table_idxs):
            item = self.table_idx["items"][int(i)]
            page = int(item.get("page", -1))
            results["tables"].append({"score": float(s), "page": page, "markdown": item.get("markdown", ""), "csv_path": item.get("csv_path")})
            if page >= 1:
                page_scores[page] = page_scores.get(page, 0.0) + float(s) * self.w_tables

        for s, i in zip(image_scores, image_idxs):
            item = self.image_idx["items"][int(i)]
            page = int(item.get("page", -1))
            results["images"].append({"score": float(s), "page": page, "path": item.get("path")})
            if page >= 1:
                page_scores[page] = page_scores.get(page, 0.0) + float(s) * self.w_images

        fused_pages = sorted([{"page": p, "score": sc} for p, sc in page_scores.items()], key=lambda x: x["score"], reverse=True)[:top_k]

        return {"by_modality": results, "by_page": fused_pages, "weights": {"text": self.w_text, "tables": self.w_tables, "images": self.w_images}}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path", type=str)
    parser.add_argument("query", type=str)
    parser.add_argument("--top_k", type=int, default=5)
    parser.add_argument("--w_text", type=float, default=1.0)
    parser.add_argument("--w_tables", type=float, default=1.0)
    parser.add_argument("--w_images", type=float, default=1.5)
    args = parser.parse_args()
    searcher = UnifiedSearcher(args.pdf_path, w_text=args.w_text, w_tables=args.w_tables, w_images=args.w_images)
    out = searcher.search(args.query, top_k=args.top_k)
    print(json.dumps(out, ensure_ascii=False, indent=2))
