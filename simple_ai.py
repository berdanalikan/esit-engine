"""
ESİT Technical Support AI - Simplified for Fine-tuned Model
Fine-tuned model için basitleştirilmiş teknik destek sistemi
"""

import os
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

# Load environment
load_dotenv()

class SimpleTechSupportAI:
    """Fine-tuned model için basitleştirilmiş teknik destek AI"""
    
    def __init__(self):
        """Initialize with fine-tuned model optimizations"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation_history = []
        
        # Problem kategorileri (fine-tuned model için basit)
        self.categories = {
            "power": ["güç", "power", "açılmıyor", "kapanıyor", "elektrik"],
            "calibration": ["kalibrasyon", "calibration", "ayar", "ölçüm"],
            "display": ["ekran", "display", "gösterge", "görünmüyor"],
            "connection": ["bağlantı", "connection", "kablo", "ethernet"],
            "error": ["hata", "error", "alarm", "uyarı", "sorun"],
            "installation": ["kurulum", "installation", "setup", "montaj"],
            "maintenance": ["bakım", "maintenance", "temizlik", "servis"]
        }
    
    def classify_problem(self, text: str) -> str:
        """Basit problem sınıflandırması"""
        text_lower = text.lower()
        
        for category, keywords in self.categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return "general"
    
    def generate_response(self, user_input: str) -> Dict[str, Any]:
        """Fine-tuned model ile yanıt üret"""
        
        # Konuşma geçmişine ekle
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Problem kategorisi
        category = self.classify_problem(user_input)
        
        # Fine-tuned model için optimize edilmiş prompt
        system_prompt = f"""Sen ESİT teknik destek uzmanısın. ECI ürünleri konusunda fine-tune edilmiş bir modelsin.

GÖREV:
- Kullanıcının ECI ürün sorunlarını çöz
- Türkçe ve profesyonel dilde yanıtla
- Adım adım rehberlik et
- Sayfa referansları ver (varsa)

Problem kategorisi: {category}

TEMEL KURALLAR:
1. Fine-tuned bilgini kullan
2. Adım adım açıkla
3. Sayfa numaralarını belirt: [Sayfa X]
4. Kesin bilgi yoksa müşteri hizmetlerine yönlendir

İLETİŞİM:
📞 (0216) 585 18 18
📧 servis@esit.com.tr
🌐 www.esit.com.tr"""

        try:
            # Fine-tuned model için optimize edilmiş parametreler
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fine-tuned model ID'niz varsa değiştirin
                messages=[
                    {"role": "system", "content": system_prompt},
                    *self.conversation_history[-6:],  # Son 6 mesaj (3 soru-cevap)
                ],
                temperature=0.1,        # Çok düşük - deterministik
                max_tokens=800,         # Odaklı yanıtlar
                top_p=0.9,             # Daha deterministik
                frequency_penalty=0.1   # Tekrar azaltma
            )
            
            ai_response = response.choices[0].message.content
            
            # Konuşma geçmişine ekle
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return {
                "response": ai_response,
                "category": category,
                "success": True,
                "model_type": "fine_tuned"
            }
            
        except Exception as e:
            print(f"AI error: {e}")
            return {
                "response": "Üzgünüm, şu anda teknik bir sorun yaşıyorum. Lütfen tekrar deneyin veya müşteri hizmetlerimizle iletişime geçin: (0216) 585 18 18",
                "error": str(e),
                "success": False
            }
    
    def reset_conversation(self):
        """Konuşmayı sıfırla"""
        self.conversation_history = []
    
    def get_status(self) -> Dict[str, Any]:
        """Sistem durumu"""
        return {
            "model": "fine_tuned_eci",
            "conversation_length": len(self.conversation_history),
            "api_key_set": bool(os.getenv("OPENAI_API_KEY"))
        }


# Global instance
simple_ai = None

def get_simple_ai() -> SimpleTechSupportAI:
    """Get or create simple AI instance"""
    global simple_ai
    if simple_ai is None:
        simple_ai = SimpleTechSupportAI()
    return simple_ai


if __name__ == "__main__":
    # Test sistemi
    ai = SimpleTechSupportAI()
    
    test_queries = [
        "ECI cihazım açılmıyor",
        "Kalibrasyon nasıl yapılır?",
        "Ekranda hata görüyorum",
        "Menü 2.5'e nasıl girerim?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Test: {query}")
        result = ai.generate_response(query)
        print(f"✅ Kategori: {result.get('category', 'N/A')}")
        print(f"📝 Yanıt: {result['response'][:100]}...")
