# ESİT Technical Support AI System

## 📋 Proje Özeti

ESİT Technical Support AI System, ESİT şirketinin tüm ürünleri için akıllı teknik destek sağlayan bir yapay zeka sistemidir. Sistem, 12 farklı ESİT ürününün kullanım kılavuzlarını entegre ederek, kullanıcılara Türkçe teknik destek hizmeti sunar.

## 🎯 Özellikler

- **Çoklu PDF Desteği**: 12 farklı ESİT ürününü destekler
- **Akıllı Kategorileme**: Weighing Scale, Load Cell, Indicator kategorileri
- **Fine-tune API Uyumlu**: OpenAI fine-tune edilmiş model ile çalışır
- **RESTful API**: FastAPI tabanlı modern web API
- **Gerçek Zamanlı Chat**: Web arayüzü ile interaktif destek
- **Ürün Arama**: Ürün adı ve kategoriye göre arama
- **Feedback Sistemi**: Kullanıcı geri bildirimleri toplama

## 🏗️ Proje Yapısı

```
esit-engine/
├── src/                          # Kaynak kodlar
│   ├── api/                      # API katmanı
│   │   └── app.py               # Ana FastAPI uygulaması
│   ├── core/                     # Ana iş mantığı
│   │   ├── tech_support_ai.py   # AI sistem sınıfı
│   │   └── simple_multi_manual.py # Çoklu PDF yöneticisi
│   └── utils/                    # Yardımcı araçlar
│       ├── process_pdf.py        # PDF işleme araçları
│       ├── search_unified.py     # Birleşik arama sistemi
│       └── search_multi_manuals.py # Çoklu PDF arama
├── data/                         # Veri dosyaları
│   ├── manuals/                  # PDF kullanım kılavuzları
│   └── processed/               # İşlenmiş veriler
├── config/                       # Konfigürasyon dosyaları
│   └── esit_beyaz kopyası.png   # ESİT logosu
├── deployment/                   # Deployment dosyaları
│   ├── render/                  # Render.com deployment
│   ├── docs/                    # Dokümantasyon
│   └── legacy/                  # Eski deployment dosyaları
├── scripts/                      # Yardımcı scriptler
│   └── start.sh                 # Başlatma scripti
├── tests/                        # Test dosyaları
├── requirements.txt             # Python bağımlılıkları
├── Dockerfile                   # Docker konfigürasyonu
└── README.md                    # Bu dosya
```

## 🚀 Kurulum

### Gereksinimler

- Python 3.12+
- OpenAI API Key
- FastAPI
- Uvicorn

### Adım 1: Repository'yi Klonlayın

```bash
git clone <repository-url>
cd esit-engine
```

### Adım 2: Sanal Ortam Oluşturun

```bash
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows
```

### Adım 3: Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### Adım 4: Environment Variables Ayarlayın

`.env` dosyası oluşturun:

```bash
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

### Adım 5: Uygulamayı Başlatın

```bash
python src/api/app.py
```

Uygulama `http://localhost:8000` adresinde çalışacaktır.

## 📚 API Dokümantasyonu

### Ana Endpoint'ler

#### 1. Chat Endpoint
```http
POST /chat
Content-Type: application/json

{
    "message": "SMART-2 cihazımda kalibrasyon sorunu var"
}
```

**Yanıt:**
```json
{
    "response": "SMART-2 cihazınızda kalibrasyon sorununu çözmek için...",
    "classification": {
        "primary_category": "calibration",
        "is_howto": false,
        "has_problem": true
    },
    "available_products": ["SMART-2 Scale", "ART-2 Scale", ...],
    "product_categories": ["Weighing Scale", "Load Cell", "Indicator"],
    "total_products": 12,
    "success": true
}
```

#### 2. Ürünleri Listele
```http
GET /products
```

**Yanıt:**
```json
{
    "status": "success",
    "products": [
        {
            "filename": "SMART-2 USER MANUAL ENG - R02.pdf",
            "product_name": "SMART-2 Scale",
            "product_category": "Weighing Scale",
            "language": "English",
            "file_path": "data/manuals/SMART-2 USER MANUAL ENG - R02.pdf"
        }
    ],
    "categories": ["Weighing Scale", "Load Cell", "Indicator"],
    "total_products": 12,
    "total_categories": 3
}
```

#### 3. Ürün Arama
```http
GET /search?query=Load%20Cell&category=Load%20Cell
```

**Yanıt:**
```json
{
    "status": "success",
    "query": "Load Cell",
    "category": "Load Cell",
    "matching_products": [
        {
            "product_name": "LCA Load Cell",
            "product_category": "Load Cell"
        },
        {
            "product_name": "LCA-B Load Cell", 
            "product_category": "Load Cell"
        }
    ],
    "total_matches": 2
}
```

#### 4. Sistem Durumu
```http
GET /health
```

**Yanıt:**
```json
{
    "status": "ok",
    "system": "ESİT Technical Support AI",
    "multi_manual_enabled": true,
    "available_products": 12,
    "product_categories": ["Indicator", "Load Cell", "Weighing Scale"],
    "supabase_enabled": false
}
```

## 🎮 Kullanım

### Web Arayüzü

1. Uygulamayı başlatın: `python src/api/app.py`
2. Tarayıcıda `http://localhost:8000` adresine gidin
3. Chat arayüzünde sorularınızı sorun

### API Kullanımı

```python
import requests

# Chat API kullanımı
response = requests.post('http://localhost:8000/chat', 
                        json={'message': 'ART-2 cihazımda sorun var'})
result = response.json()
print(result['response'])

# Ürünleri listele
products = requests.get('http://localhost:8000/products')
print(products.json()['products'])
```

## 📦 Desteklenen Ürünler

### Weighing Scale (9 ürün)
- **TR-4 Scale**: TR4-User-Manual.pdf
- **ART-2 Scale**: ART-2-ENG-R00.pdf
- **ECI Automatic Scale**: Esit_ECI_User_Manual_Automatic_ENG_v1_7 kopyası.pdf
- **Weighfly Scale**: Weighfly-User-Manual.pdf
- **SMART-2 Scale**: SMART-2 USER MANUAL ENG - R02.pdf
- **ART Scale**: ART-EN.pdf
- **AS Axle Scale**: ESIT-AS-Axle-Scale-Manual-EN.pdf
- **AWS Aircraft Weighing System**: AWS-Aircraft Weighing System_EN_rev1.pdf
- **TR-3 Scale**: TR-3-Kilavuz-ENG.pdf

### Load Cell (2 ürün)
- **LCA Load Cell**: Esit-LCA-User-Manual-EN.pdf
- **LCA-B Load Cell**: LCA-B-AR-User Manual-EN.pdf

### Indicator (1 ürün)
- **PWI Series Indicator**: PWI-SERIES-INDICATOR-USER-MANUAL-EN.pdf

## 🔧 Konfigürasyon

### Environment Variables

| Değişken | Açıklama | Gerekli |
|----------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API anahtarı | ✅ |
| `SUPABASE_URL` | Supabase URL (opsiyonel) | ❌ |
| `SUPABASE_ANON_KEY` | Supabase anon key (opsiyonel) | ❌ |
| `PORT` | Uygulama portu (varsayılan: 8000) | ❌ |

### AI Model Konfigürasyonu

`src/core/tech_support_ai.py` dosyasında AI model ayarları:

```python
response = self.client.chat.completions.create(
    model="gpt-4o-mini",  # Fine-tune model ID'nizi buraya yazın
    messages=messages,
    temperature=0.1,
    max_tokens=800,
    top_p=0.9,
    frequency_penalty=0.1
)
```

## 🚀 Deployment

### Render.com ile Deployment

1. Render.com hesabınızda yeni Web Service oluşturun
2. Repository'nizi bağlayın
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python src/api/app.py`
5. Environment variables'ları ekleyin

### Docker ile Deployment

```bash
# Docker image oluştur
docker build -t esit-ai .

# Container çalıştır
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key esit-ai
```

## 🧪 Test

### Manuel Test

```bash
# Health check
curl http://localhost:8000/health

# Chat test
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "SMART-2 kalibrasyonu nasıl yapılır?"}'

# Ürün listesi
curl http://localhost:8000/products
```

### Otomatik Test

```bash
# Test dosyalarını çalıştır (gelecekte eklenecek)
python -m pytest tests/
```

## 📊 Monitoring ve Logging

### Log Dosyaları

- `data/processed/feedback.log`: Kullanıcı geri bildirimleri
- `data/processed/feedback_data.json`: Feedback verileri

### Metrics

- `/health` endpoint'i sistem durumunu izler
- `/feedback/analysis` endpoint'i kullanıcı memnuniyetini analiz eder

## 🔒 Güvenlik

- API anahtarları environment variables ile korunur
- CORS middleware aktif
- Input validation mevcut
- Rate limiting (gelecekte eklenecek)

## 🐛 Sorun Giderme

### Yaygın Sorunlar

1. **Port zaten kullanımda**
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

2. **OpenAI API Key hatası**
   - `.env` dosyasında `OPENAI_API_KEY` kontrol edin
   - API key'in geçerli olduğundan emin olun

3. **PDF dosyaları bulunamıyor**
   - `data/manuals/` klasöründe PDF dosyalarının olduğunu kontrol edin
   - Dosya izinlerini kontrol edin

### Debug Modu

```bash
# Debug logları ile çalıştır
PYTHONPATH=. python -u src/api/app.py
```

## 📈 Gelecek Geliştirmeler

- [ ] Unit testler ekleme
- [ ] Rate limiting implementasyonu
- [ ] Database entegrasyonu
- [ ] Multi-language desteği
- [ ] Advanced analytics dashboard
- [ ] Mobile app desteği

## 👥 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📞 İletişim

- **ESİT Teknik Destek**: (0216) 585 18 18
- **Email**: servis@esit.com.tr
- **Proje Repository**: [GitHub Link]

## 📄 Lisans

Bu proje ESİT şirketi için özel olarak geliştirilmiştir. Tüm hakları saklıdır.

---

**Not**: Bu sistem fine-tune edilmiş OpenAI modeli ile çalışmak üzere tasarlanmıştır. Kendi fine-tune modelinizi kullanmak için `src/core/tech_support_ai.py` dosyasındaki model ID'yi güncelleyin.
