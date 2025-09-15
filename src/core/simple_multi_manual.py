#!/usr/bin/env python3
"""
Basit çoklu PDF desteği - Fine-tune edilmiş API için
PDF arama sistemi olmadan, sadece çoklu PDF bilgisi sağlar
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class SimpleMultiManual:
    """Basit çoklu PDF yöneticisi - Fine-tune API için"""
    
    def __init__(self, manuals_dir: str = "data/manuals", metadata_file: str = "data/processed/simple_manuals_metadata.json"):
        self.manuals_dir = Path(manuals_dir)
        self.metadata_file = metadata_file
        self.manuals_info = self._load_manuals_info()
        
    def _load_manuals_info(self) -> List[Dict[str, str]]:
        """Kullanma kılavuzları klasöründeki PDF dosyalarını yükle"""
        manuals = []
        
        if not self.manuals_dir.exists():
            return manuals
            
        for pdf_file in self.manuals_dir.glob("*.pdf"):
            product_info = self._extract_product_info(pdf_file)
            manuals.append(product_info)
            
        return manuals
    
    def _extract_product_info(self, pdf_path: Path) -> Dict[str, str]:
        """PDF dosyasından ürün bilgilerini çıkar"""
        filename = pdf_path.stem
        
        # Ürün adı mapping'i
        product_mapping = {
            "ART-2-ENG-R00": "ART-2 Scale",
            "ART-EN": "ART Scale", 
            "AWS-Aircraft Weighing System_EN_rev1": "AWS Aircraft Weighing System",
            "Esit_ECI_User_Manual_Automatic_ENG_v1_7": "ECI Automatic Scale",
            "ESIT-AS-Axle-Scale-Manual-EN": "AS Axle Scale",
            "Esit-LCA-User-Manual-EN": "LCA Load Cell",
            "LCA-B-AR-User Manual-EN": "LCA-B Load Cell",
            "PWI-SERIES-INDICATOR-USER-MANUAL-EN": "PWI Series Indicator",
            "SMART-2 USER MANUAL ENG - R02": "SMART-2 Scale",
            "TR-3-Kilavuz-ENG": "TR-3 Scale",
            "TR4-User-Manual": "TR-4 Scale",
            "Weighfly-User-Manual": "Weighfly Scale"
        }
        
        # Ürün adını bul
        product_name = filename
        for pattern, name in product_mapping.items():
            if pattern in filename:
                product_name = name
                break
        
        # Kategori belirle
        category = self._categorize_product(product_name)
        
        return {
            "filename": pdf_path.name,
            "product_name": product_name,
            "product_category": category,
            "language": "English",
            "file_path": str(pdf_path)
        }
    
    def _categorize_product(self, product_name: str) -> str:
        """Ürünü kategorize et"""
        if "Scale" in product_name or "Weigh" in product_name:
            return "Weighing Scale"
        elif "Load Cell" in product_name or "LCA" in product_name:
            return "Load Cell"
        elif "Indicator" in product_name:
            return "Indicator"
        elif "Aircraft" in product_name:
            return "Aircraft Weighing"
        else:
            return "General Equipment"
    
    def get_all_products(self) -> List[Dict[str, str]]:
        """Tüm ürünleri getir"""
        return self.manuals_info
    
    def get_products_by_category(self, category: str) -> List[Dict[str, str]]:
        """Kategoriye göre ürünleri getir"""
        return [p for p in self.manuals_info if p["product_category"] == category]
    
    def get_categories(self) -> List[str]:
        """Tüm kategorileri getir"""
        categories = set()
        for manual in self.manuals_info:
            categories.add(manual["product_category"])
        return sorted(list(categories))
    
    def get_product_context(self) -> str:
        """Tüm ürünler için bağlam metni oluştur"""
        if not self.manuals_info:
            return "Henüz ürün bilgisi yüklenmedi."
        
        context_parts = []
        context_parts.append("ESİT Ürün Portföyü:")
        
        # Kategoriye göre grupla
        categories = {}
        for manual in self.manuals_info:
            category = manual["product_category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(manual["product_name"])
        
        for category, products in categories.items():
            context_parts.append(f"\n{category}:")
            for product in products:
                context_parts.append(f"  - {product}")
        
        return "\n".join(context_parts)
    
    def save_metadata(self, filename: str = "data/processed/simple_manuals_metadata.json") -> None:
        """Metadata'yı JSON dosyasına kaydet"""
        metadata = {
            "generated_date": datetime.now().isoformat(),
            "total_manuals": len(self.manuals_info),
            "manuals": self.manuals_info,
            "categories": self.get_categories()
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"Metadata saved to: {filename}")


def main():
    """Test fonksiyonu"""
    multi_manual = SimpleMultiManual()
    
    print("=== ESİT Çoklu PDF Desteği ===")
    print(f"Toplam ürün sayısı: {len(multi_manual.get_all_products())}")
    print(f"Kategoriler: {multi_manual.get_categories()}")
    
    print("\n=== Tüm Ürünler ===")
    for product in multi_manual.get_all_products():
        print(f"- {product['product_name']} ({product['product_category']})")
    
    print("\n=== Ürün Bağlamı ===")
    print(multi_manual.get_product_context())
    
    # Metadata'yı kaydet
    multi_manual.save_metadata()


if __name__ == "__main__":
    main()
