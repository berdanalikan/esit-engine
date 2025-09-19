"""
ESİT Technical Support AI Tool
PDF tabanlı akıllı teknik destek sistemi
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv
from .simple_multi_manual import SimpleMultiManual

# Load environment
load_dotenv()

class TechnicalSupportAI:
    """ESİT Teknik Destek AI Aracı"""
    
    def __init__(self, pdf_path: str = None):
        """
        Initialize technical support AI
        
        Args:
            pdf_path: Path to the user manual PDF (legacy support)
        """
        self.pdf_path = pdf_path
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize multi-manual system
        self.multi_manual = SimpleMultiManual()
        
        # Initialize PDF search system (legacy)
        self._init_pdf_search()
        
        # Conversation history for context
        self.conversation_history = []
        # Kullanıcının üzerinde çalıştığı ürün (sohbet boyunca tutulur)
        self.current_product: Optional[str] = None
        
        # Technical categories for better problem classification
        self.tech_categories = {
            "power": ["güç", "power", "açılmıyor", "kapanıyor", "elektrik", "enerji"],
            "calibration": ["kalibrasyon", "calibration", "ayar", "setting", "ölçüm", "measurement"],
            "display": ["ekran", "display", "gösterge", "screen", "görünmüyor"],
            "connection": ["bağlantı", "connection", "kablo", "cable", "ethernet", "network"],
            "error": ["hata", "error", "alarm", "uyarı", "warning", "sorun", "problem"],
            "installation": ["kurulum", "installation", "setup", "montaj"],
            "maintenance": ["bakım", "maintenance", "temizlik", "cleaning", "servis"]
        }
    
    def _init_pdf_search(self):
        """Initialize PDF search system"""
        try:
            from search_unified import UnifiedSearcher
            self.searcher = UnifiedSearcher(self.pdf_path)
            print(f"✅ PDF search system initialized for: {Path(self.pdf_path).name}")
        except ImportError as e:
            print(f"❌ PDF search initialization failed: Missing dependencies ({e})")
            self.searcher = None
        except Exception as e:
            print(f"❌ PDF search initialization failed: {e}")
            self.searcher = None
    
    def classify_problem(self, user_input: str) -> Dict[str, Any]:
        """
        Classify user problem into technical categories
        
        Args:
            user_input: User's problem description
            
        Returns:
            Dictionary with classification results
        """
        user_lower = user_input.lower()
        
        # Find matching categories
        matched_categories = []
        for category, keywords in self.tech_categories.items():
            if any(keyword in user_lower for keyword in keywords):
                matched_categories.append(category)
        
        # Determine problem type
        problem_type = "general"
        if matched_categories:
            problem_type = matched_categories[0]  # Take first match
        
        # Check if it's a how-to question
        is_howto = any(word in user_lower for word in ["nasıl", "how", "ne zaman", "when", "nerede", "where"])
        
        return {
            "categories": matched_categories,
            "primary_category": problem_type,
            "is_howto": is_howto,
            "has_problem": len(matched_categories) > 0 or any(word in user_lower for word in ["sorun", "problem", "hata", "error"])
        }
    
    def search_manual(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search in the technical manual
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            Search results from the manual
        """
        if not self.searcher:
            return {"error": "PDF search not available"}
        
        try:
            results = self.searcher.search(query, top_k=max_results)
            
            # Extract relevant information
            context_parts = []
            
            # Process text results
            if "by_modality" in results and "text" in results["by_modality"]:
                for item in results["by_modality"]["text"][:3]:
                    page = item.get("page", "N/A")
                    text = item.get("text", "")
                    if text.strip():
                        context_parts.append(f"[Sayfa {page}] {text}")
            
            # Process table results
            if "by_modality" in results and "tables" in results["by_modality"]:
                for item in results["by_modality"]["tables"][:2]:
                    page = item.get("page", "N/A")
                    markdown = item.get("markdown", "")
                    if markdown.strip():
                        context_parts.append(f"[Tablo - Sayfa {page}] {markdown}")
            
            # Process image results
            image_references = []
            if "by_modality" in results and "images" in results["by_modality"]:
                for item in results["by_modality"]["images"][:2]:
                    page = item.get("page", "N/A")
                    path = item.get("path", "")
                    score = item.get("score", 0)
                    if path and score > 0.3:  # Only include relevant images
                        image_references.append(f"[Görsel - Sayfa {page}]")
            
            # Add image references to context
            if image_references:
                context_parts.append(f"İlgili görseller: {', '.join(image_references)}")
            
            # Build image URLs for frontend if paths exist
            image_urls = []
            try:
                if "by_modality" in results and "images" in results["by_modality"]:
                    for item in results["by_modality"]["images"][:3]:
                        path = item.get("path", "")
                        score = item.get("score", 0)
                        if path and score > 0.3:
                            # Path format: /.../<pdf>_images/pageX_imgY.ext → expose as /images/filename
                            filename = Path(path).name
                            image_urls.append(f"/images/{filename}")
            except Exception:
                pass

            return {
                "context": "\n\n".join(context_parts),
                "total_results": len(context_parts),
                "raw_results": results,
                "image_references": image_references,
                "image_urls": image_urls
            }
            
        except Exception as e:
            print(f"Search error: {e}")
            return {"error": str(e), "context": "", "total_results": 0}
    
    def _process_multi_manual_results(self, multi_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process multi-manual search results into single context
        
        Args:
            multi_results: Results from MultiManualSearcher
            
        Returns:
            Processed search results in single manual format
        """
        context_parts = []
        image_urls = []
        image_references = []
        
        try:
            # Process text results from all manuals
            if "by_modality" in multi_results and "text" in multi_results["by_modality"]:
                for item in multi_results["by_modality"]["text"][:5]:  # Top 5 text results
                    product_name = item.get("product_name", "Unknown")
                    page = item.get("page", "N/A")
                    text = item.get("text", "")
                    if text.strip():
                        context_parts.append(f"[{product_name} - Sayfa {page}] {text}")
            
            # Process table results
            if "by_modality" in multi_results and "tables" in multi_results["by_modality"]:
                for item in multi_results["by_modality"]["tables"][:3]:  # Top 3 table results
                    product_name = item.get("product_name", "Unknown")
                    page = item.get("page", "N/A")
                    markdown = item.get("markdown", "")
                    if markdown.strip():
                        context_parts.append(f"[{product_name} - Tablo Sayfa {page}] {markdown}")
            
            # Process image results
            if "by_modality" in multi_results and "images" in multi_results["by_modality"]:
                for item in multi_results["by_modality"]["images"][:3]:  # Top 3 image results
                    product_name = item.get("product_name", "Unknown")
                    page = item.get("page", "N/A")
                    path = item.get("path", "")
                    score = item.get("score", 0)
                    if path and score > 0.3:
                        image_references.append(f"[{product_name} - Görsel Sayfa {page}]")
                        # Build image URL
                        try:
                            filename = Path(path).name
                            # Extract product name from path for URL
                            product_slug = product_name.lower().replace(" ", "-").replace("_", "-")
                            image_urls.append(f"/images/{product_slug}/{filename}")
                        except Exception:
                            pass
            
            # Add product context
            if "by_product" in multi_results:
                relevant_products = []
                for product_name, product_data in multi_results["by_product"].items():
                    if product_data["relevant_results"]["total"] > 0:
                        relevant_products.append(product_name)
                
                if relevant_products:
                    context_parts.append(f"İlgili Ürünler: {', '.join(relevant_products)}")
            
            # Add image references to context
            if image_references:
                context_parts.append(f"İlgili görseller: {', '.join(image_references)}")
            
            return {
                "context": "\n\n".join(context_parts),
                "total_results": len(context_parts),
                "image_references": image_references,
                "image_urls": image_urls,
                "raw_results": multi_results
            }
            
        except Exception as e:
            print(f"Multi-manual processing error: {e}")
            return {"error": str(e), "context": "", "total_results": 0}
    
    def generate_response(self, user_input: str, search_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate AI response for technical support
        
        Args:
            user_input: User's question or problem
            
        Returns:
            AI response with technical information
        """
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Ürün tespiti (mesaj + geçmiş üzerinden)
        detected_product = self._detect_product_from_text(user_input)
        if detected_product:
            self.current_product = detected_product

        # Eğer ürün belirlenmediyse, ilk etapta kullanıcıdan cihazı netleştirmesini iste
        if not self.current_product:
            return self._ask_for_product_clarification()

        # Classify the problem
        classification = self.classify_problem(user_input)
        
        # Use provided search results or search manually
        if search_results is None:
            # Fine-tuned model için opsiyonel PDF arama
            # Model zaten fine-tuned olduğu için PDF araması opsiyonel
            search_results = {"context": "", "total_results": 0}
            
            # Teknik sorular için PDF arama yap (görsel arama dahil)
            if classification["has_problem"] and classification["primary_category"] in ["calibration", "installation", "maintenance", "display", "connection"]:
                search_results = self.search_manual(user_input)
        else:
            # Process multi-manual search results
            search_results = self._process_multi_manual_results(search_results)
        
        # Build context for AI
        context = search_results.get("context", "")
        has_manual_info = search_results.get("total_results", 0) > 0
        
        # Create AI prompt
        system_prompt = self._build_system_prompt(classification, context, has_manual_info)
        
        try:
            # Fine-tuned model için optimize edilmiş parametreler
            # Derin hafıza: Son 8 mesajı bağlama dahil et
            history_messages = []
            if self.conversation_history:
                # Sadece son N mesajı al (token güvenliği için)
                for m in self.conversation_history[-8:]:
                    # İçeriği aşırı uzunsa kısalt
                    content = m.get("content", "")
                    if isinstance(content, str) and len(content) > 1200:
                        content = content[:1200] + " …"
                    history_messages.append({"role": m.get("role", "user"), "content": content})

            messages = [{"role": "system", "content": system_prompt}] + history_messages + [
                {"role": "user", "content": user_input}
            ]

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fine-tuned model ID'niz varsa burayı değiştirin
                messages=messages,
                temperature=0.1,  # Fine-tuned model için daha düşük
                max_tokens=800,   # Daha odaklı yanıtlar
                top_p=0.9,        # Daha deterministik
                frequency_penalty=0.1  # Tekrar azaltma
            )
            
            ai_response = response.choices[0].message.content
            
            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return {
                "response": ai_response,
                "classification": classification,
                "product": self.current_product,
                "has_manual_info": has_manual_info,
                "search_results": search_results,
                "success": True
            }
            
        except Exception as e:
            print(f"AI response error: {e}")
            return {
                "response": "Üzgünüm, şu anda teknik bir sorun yaşıyorum. Lütfen tekrar deneyin.",
                "error": str(e),
                "success": False
            }

    def _ask_for_product_clarification(self) -> Dict[str, Any]:
        """Kullanıcıdan ürün adını/cihazı netleştirmesini ister."""
        try:
            products = self.multi_manual.get_all_products()
            # Kısa bir öneri listesi (azami 8 öğe)
            top_products = [p.get("product_name") for p in products][:8]
            suggestion_line = "; ".join(top_products)
            prompt = (
                "🔧 ESİT Teknik Destek'e hoş geldiniz!\n\n"
                "Size en iyi şekilde yardımcı olabilmem için hangi ESİT cihazı ile çalıştığınızı belirtmeniz gerekiyor.\n\n"
                "Mevcut ürünlerimiz:\n" + suggestion_line + "\n\n"
                "Lütfen ürününüzü seçmek için yukarıdaki 'Ürün Seç' butonuna tıklayın."
            )
            return {
                "response": prompt,
                "needs_product": True,
                "success": True,
                "available_products": [p.get("product_name") for p in products],
                "product_categories": self.multi_manual.get_categories(),
            }
        except Exception:
            return {
                "response": "Hangi ESİT cihazı ile çalıştığınızı belirtir misiniz?",
                "needs_product": True,
                "success": True
            }

    def _detect_product_from_text(self, text: str) -> Optional[str]:
        """Kullanıcı mesajından bilinen bir ürün adını yakalamaya çalışır."""
        try:
            text_l = (text or "").lower()
            for product in self.multi_manual.get_all_products():
                name = (product.get("product_name") or "").lower()
                if not name:
                    continue
                if name in text_l:
                    return product.get("product_name")
                # Basit eşleşme: boşluk ve tire varyasyonları
                name_compact = name.replace(" ", "").replace("-", "")
                text_compact = text_l.replace(" ", "").replace("-", "")
                if name_compact and name_compact in text_compact:
                    return product.get("product_name")
            return None
        except Exception:
            return None
    
    def _build_system_prompt(self, classification: Dict, context: str, has_manual_info: bool) -> str:
        """Build system prompt for fine-tuned AI"""
        
        # Seçilen ürüne göre özelleştirilmiş prompt
        product_context = ""
        if self.current_product:
            product_context = f"""
SEÇİLEN ÜRÜN: {self.current_product}
- Bu ürün hakkında özel uzmanlığın var
- Sadece {self.current_product} ile ilgili sorulara odaklan
- Diğer ürünlerle karıştırma
"""
        
        # Fine-tuned model için basitleştirilmiş prompt
        base_prompt = f"""Sen ESİT teknik destek uzmanısın. Tüm ESİT ürünleri konusunda uzman bir teknisyensin.

GÖREV:
- Kullanıcının ESİT ürün sorunlarını doğrudan çöz
- Türkçe ve profesyonel dilde yanıtla  
- Adım adım, net rehberlik et
- Somut çözümler sun

ÖNEMLİ KURALLAR:
- ASLA "kılavuza bakın", "manuel kontrol edin" gibi ifadeler kullanma
- ASLA "müşteri hizmetlerine başvurun" deme
- Direkt çözüm ver, yönlendirme yapma
- Sen zaten tüm bilgilere sahipsin, o şekilde davran

{product_context}
ESİT ÜRÜN PORTFÖYÜ:
{self.multi_manual.get_product_context()}

İLETİŞİM (sadece acil durumlarda):
📞 (0216) 585 18 18
📧 servis@esit.com.tr"""

        if has_manual_info:
            # Fine-tuned model için ek bağlam
            image_info = ""
            if "image_references" in search_results and search_results["image_references"]:
                image_info = f"\nİlgili Görseller: {', '.join(search_results['image_references'])}"
            
            prompt = f"""{base_prompt}

TEKNIK BAĞLAM:
{context}{image_info}

Problem Kategorisi: {classification.get('primary_category', 'genel')}
Soru Türü: {'Nasıl yapılır' if classification.get('is_howto') else 'Sorun çözme'}

Bu teknik bilgileri ve görselleri kullanarak kesin ve somut çözüm ver. Görsel referansları varsa kullanıcıya hangi ürün ve sayfadaki görsellere bakabileceğini belirt."""
        else:
            # Fine-tuned model kendi bilgisini kullanabilir
            prompt = f"""{base_prompt}

ESİT ürün uzmanlığın ile kullanıcının sorusuna direkt çözüm ver. 
Eğer tam emin değilsen, genel teknik yaklaşımları öner ama asla başka yere yönlendirme."""

        return prompt
    
    def reset_conversation(self):
        """Reset conversation history and product selection"""
        self.conversation_history = []
        self.current_product = None
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary"""
        return {
            "total_messages": len(self.conversation_history),
            "last_message": self.conversation_history[-1] if self.conversation_history else None
        }


# Global instance
tech_support_ai = None

def get_tech_support_ai(pdf_path: str = None) -> TechnicalSupportAI:
    """Get or create technical support AI instance"""
    global tech_support_ai
    
    if tech_support_ai is None and pdf_path:
        tech_support_ai = TechnicalSupportAI(pdf_path)
    
    return tech_support_ai


if __name__ == "__main__":
    # Test the system
    pdf_path = "Esit_ECI_User_Manual_Automatic_ENG_v1_7 kopyası.pdf"
    
    if Path(pdf_path).exists():
        ai = TechnicalSupportAI(pdf_path)
        
        # Test queries
        test_queries = [
            "ECI cihazım açılmıyor",
            "Kalibrasyon nasıl yapılır?",
            "Ekranda hata görüyorum",
            "Fiyat bilgisi alabilir miyim?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Test: {query}")
            result = ai.generate_response(query)
            print(f"✅ Response: {result['response'][:100]}...")
    else:
        print("Şu anda hizmet veremiyorum. Lütfen daha sonra tekrar deneyin.")
