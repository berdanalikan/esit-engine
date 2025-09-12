# ESİT Technical Support AI Tool

PDF tabanlı akıllı teknik destek sistemi. ECI ürün kullanma kılavuzunu kullanarak otomatik teknik destek sağlar.

## 🚀 Özellikler

- **PDF Tabanlı Bilgi**: Kullanma kılavuzundan doğrudan bilgi çeker
- **Akıllı Problem Sınıflandırma**: Sorunları otomatik kategorilere ayırır
- **Çok Modlu Arama**: Metin, tablo ve görsel arama
- **OpenAI Entegrasyonu**: Doğal dil işleme ve TTS
- **Web Arayüzü**: Modern, kullanıcı dostu interface
- **Türkçe Destek**: Tam Türkçe dil desteği

## 📋 Gereksinimler

- Python 3.8+
- OpenAI API Key
- PDF dosyası (kullanma kılavuzu)

## 🛠️ Kurulum

1. **Depoyu klonlayın:**
```bash
git clone <repo-url>
cd esit-engine
```

2. **Sanal ortam oluşturun:**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# veya
.venv\Scripts\activate  # Windows
```

3. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

4. **OpenAI API key'ini ayarlayın:**
```bash
# .env dosyası oluşturun
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

5. **PDF'i işleyin (ilk kez):**
```bash
python process_pdf.py
```

## 🚀 Kullanım

### Web Uygulaması

```bash
python app.py
```

Tarayıcıda `http://127.0.0.1:8000` adresine gidin.

### Komut Satırı Testi

```bash
python tech_support_ai.py
```

## 🏗️ Sistem Mimarisi

```
├── app.py                 # FastAPI web uygulaması
├── tech_support_ai.py     # Ana AI sınıfı
├── search_unified.py      # PDF arama sistemi
├── process_pdf.py         # PDF işleme ve indeksleme
└── requirements.txt       # Python bağımlılıkları
```

## 🔧 API Endpoints

- `GET /` - Web arayüzü
- `POST /chat` - Sohbet endpoint'i
- `POST /reset` - Konuşma sıfırlama
- `POST /tts` - Text-to-Speech
- `GET /health` - Sistem durumu

## 📝 Örnek Kullanım

### Sohbet API'si

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"ECI cihazım açılmıyor"}'
```

### Yanıt Formatı

```json
{
  "response": "ECI cihazınızın açılmaması için...",
  "classification": {
    "primary_category": "power",
    "has_problem": true
  },
  "has_manual_info": true,
  "success": true
}
```

## 🎯 Problem Kategorileri

- **power**: Güç ve enerji sorunları
- **calibration**: Kalibrasyon ve ayar
- **display**: Ekran ve gösterge
- **connection**: Bağlantı sorunları
- **error**: Hata ve alarm
- **installation**: Kurulum
- **maintenance**: Bakım

## 📚 Teknik Detaylar

### PDF İşleme
- PyPDF ile metin çıkarma
- PyMuPDF ile görsel çıkarma
- pdfplumber ile tablo çıkarma

### Arama Sistemi
- FAISS vektör veritabanı
- Sentence Transformers embeddings
- CLIP görsel embeddings

### AI Sistemi
- OpenAI GPT-4o-mini
- Problem sınıflandırma
- Bağlam tabanlı yanıt üretimi

## 🔒 Güvenlik

- API key'leri .env dosyasında
- CORS koruması
- Input validation
- Error handling

## 📞 Destek

Teknik destek için:
- 📧 E-posta: servis@esit.com.tr
- 📞 Telefon: (0216) 585 18 18
- 🌐 Web: www.esit.com.tr

## 📄 Lisans

Bu proje ESİT firması tarafından geliştirilmiştir.