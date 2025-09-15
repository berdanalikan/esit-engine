#!/usr/bin/env python3
"""
Multi-manual search system that can search across all processed user manuals.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

# Try to import faiss, fallback to simple search if not available
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️ FAISS not available, using simple search fallback")

from search_unified import ModalityIndex


class MultiManualSearcher:
    def __init__(self, metadata_file: str = "manuals_metadata.json"):
        self.metadata_file = metadata_file
        self.manuals_data = self._load_metadata()
        self.text_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.clip_model = SentenceTransformer("clip-ViT-B-32")
        
        # Load all manual indices
        self.manual_searchers = self._load_manual_searchers()
        
        logger = logging.getLogger(__name__)
        logger.info(f"Loaded {len(self.manual_searchers)} manual searchers")
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load manuals metadata"""
        if not os.path.exists(self.metadata_file):
            return {"manuals": []}
        
        with open(self.metadata_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _load_manual_searchers(self) -> Dict[str, Any]:
        """Load searchers for all processed manuals"""
        searchers = {}
        
        for manual in self.manuals_data.get("manuals", []):
            try:
                pdf_path = manual["pdf_path"]
                product_name = manual["product_info"]["product_name"]
                
                # Create searcher for this manual
                searcher = UnifiedSearcher(pdf_path)
                searchers[product_name] = {
                    "searcher": searcher,
                    "product_info": manual["product_info"],
                    "pdf_path": pdf_path
                }
                
            except Exception as e:
                logging.error(f"Failed to load searcher for {manual.get('product_info', {}).get('product_name', 'Unknown')}: {e}")
        
        return searchers
    
    def search_all_manuals(self, query: str, top_k: int = 10, 
                          w_text: float = 1.0, w_tables: float = 1.0, w_images: float = 1.5) -> Dict[str, Any]:
        """Search across all manuals and return unified results"""
        
        all_results = []
        
        for product_name, searcher_data in self.manual_searchers.items():
            try:
                searcher = searcher_data["searcher"]
                product_info = searcher_data["product_info"]
                
                # Search this manual
                results = searcher.search(query, top_k=top_k)
                
                # Add product context to results
                for modality in ["text", "tables", "images"]:
                    for item in results["by_modality"][modality]:
                        item["product_name"] = product_name
                        item["product_category"] = product_info["product_category"]
                        item["pdf_path"] = searcher_data["pdf_path"]
                
                # Add product context to page results
                for page_result in results["by_page"]:
                    page_result["product_name"] = product_name
                    page_result["product_category"] = product_info["product_category"]
                    page_result["pdf_path"] = searcher_data["pdf_path"]
                
                all_results.append({
                    "product_name": product_name,
                    "product_info": product_info,
                    "results": results
                })
                
            except Exception as e:
                logging.error(f"Search failed for {product_name}: {e}")
        
        # Merge and rank results across all manuals
        return self._merge_results(all_results, top_k)
    
    def _merge_results(self, all_results: List[Dict[str, Any]], top_k: int) -> Dict[str, Any]:
        """Merge results from all manuals and rank them"""
        
        merged_text = []
        merged_tables = []
        merged_images = []
        merged_pages = []
        
        # Collect all results
        for manual_result in all_results:
            results = manual_result["results"]
            
            merged_text.extend(results["by_modality"]["text"])
            merged_tables.extend(results["by_modality"]["tables"])
            merged_images.extend(results["by_modality"]["images"])
            merged_pages.extend(results["by_page"])
        
        # Sort by score and limit
        merged_text = sorted(merged_text, key=lambda x: x["score"], reverse=True)[:top_k]
        merged_tables = sorted(merged_tables, key=lambda x: x["score"], reverse=True)[:top_k]
        merged_images = sorted(merged_images, key=lambda x: x["score"], reverse=True)[:top_k]
        merged_pages = sorted(merged_pages, key=lambda x: x["score"], reverse=True)[:top_k]
        
        return {
            "by_modality": {
                "text": merged_text,
                "tables": merged_tables,
                "images": merged_images
            },
            "by_page": merged_pages,
            "by_product": self._group_by_product(all_results),
            "total_manuals_searched": len(all_results),
            "weights": {"text": 1.0, "tables": 1.0, "images": 1.5}
        }
    
    def _group_by_product(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Group results by product for easier analysis"""
        product_groups = {}
        
        for manual_result in all_results:
            product_name = manual_result["product_name"]
            product_info = manual_result["product_info"]
            results = manual_result["results"]
            
            # Count relevant results for this product
            text_count = len([r for r in results["by_modality"]["text"] if r["score"] > 0.1])
            table_count = len([r for r in results["by_modality"]["tables"] if r["score"] > 0.1])
            image_count = len([r for r in results["by_modality"]["images"] if r["score"] > 0.1])
            
            product_groups[product_name] = {
                "product_info": product_info,
                "relevant_results": {
                    "text": text_count,
                    "tables": table_count,
                    "images": image_count,
                    "total": text_count + table_count + image_count
                },
                "top_pages": results["by_page"][:3]  # Top 3 pages from this product
            }
        
        return product_groups
    
    def search_by_product_category(self, query: str, category: str, top_k: int = 5) -> Dict[str, Any]:
        """Search only in manuals of a specific product category"""
        
        category_manuals = {
            name: data for name, data in self.manual_searchers.items()
            if data["product_info"]["product_category"] == category
        }
        
        if not category_manuals:
            return {"error": f"No manuals found for category: {category}"}
        
        # Search only in category manuals
        all_results = []
        for product_name, searcher_data in category_manuals.items():
            try:
                searcher = searcher_data["searcher"]
                product_info = searcher_data["product_info"]
                
                results = searcher.search(query, top_k=top_k)
                
                # Add product context
                for modality in ["text", "tables", "images"]:
                    for item in results["by_modality"][modality]:
                        item["product_name"] = product_name
                        item["product_category"] = product_info["product_category"]
                
                for page_result in results["by_page"]:
                    page_result["product_name"] = product_name
                    page_result["product_category"] = product_info["product_category"]
                
                all_results.append({
                    "product_name": product_name,
                    "product_info": product_info,
                    "results": results
                })
                
            except Exception as e:
                logging.error(f"Search failed for {product_name}: {e}")
        
        return self._merge_results(all_results, top_k)
    
    def get_available_products(self) -> List[Dict[str, str]]:
        """Get list of all available products"""
        products = []
        for searcher_data in self.manual_searchers.values():
            products.append({
                "name": searcher_data["product_info"]["product_name"],
                "category": searcher_data["product_info"]["product_category"],
                "filename": searcher_data["product_info"]["filename"]
            })
        return products
    
    def get_product_categories(self) -> List[str]:
        """Get list of all available product categories"""
        categories = set()
        for searcher_data in self.manual_searchers.values():
            categories.add(searcher_data["product_info"]["product_category"])
        return sorted(list(categories))


class UnifiedSearcher:
    """Wrapper class to maintain compatibility with existing search_unified.py"""
    def __init__(self, pdf_path: str, w_text: float = 1.0, w_tables: float = 1.0, w_images: float = 1.5):
        base = Path(pdf_path).with_suffix("")
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
        if not FAISS_AVAILABLE:
            return self._simple_search(query, top_k)
        
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
    
    def _simple_search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Simple text-based search fallback when FAISS is not available"""
        query_lower = query.lower()
        results = {"text": [], "tables": [], "images": []}
        
        # Simple text search
        for i, item in enumerate(self.text_idx["items"]):
            text = item.get("text", "").lower()
            if query_lower in text:
                score = text.count(query_lower) / len(text.split())  # Simple scoring
                results["text"].append({
                    "score": score,
                    "page": item.get("page", -1),
                    "text": item.get("text", "")
                })
        
        # Sort by score and limit
        results["text"] = sorted(results["text"], key=lambda x: x["score"], reverse=True)[:top_k]
        
        return {"by_modality": results, "by_page": [], "weights": {"text": 1.0, "tables": 1.0, "images": 1.0}}


def main():
    """Main function for testing the multi-manual search"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--top_k", type=int, default=10, help="Number of results to return")
    parser.add_argument("--category", type=str, help="Filter by product category")
    parser.add_argument("--list-products", action="store_true", help="List available products")
    parser.add_argument("--list-categories", action="store_true", help="List available categories")
    args = parser.parse_args()
    
    searcher = MultiManualSearcher()
    
    if args.list_products:
        products = searcher.get_available_products()
        print("Available Products:")
        for product in products:
            print(f"  - {product['name']} ({product['category']})")
        return
    
    if args.list_categories:
        categories = searcher.get_product_categories()
        print("Available Categories:")
        for category in categories:
            print(f"  - {category}")
        return
    
    if args.category:
        results = searcher.search_by_product_category(args.query, args.category, args.top_k)
    else:
        results = searcher.search_all_manuals(args.query, args.top_k)
    
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
