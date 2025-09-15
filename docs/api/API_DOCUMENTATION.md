# ESİT Technical Support AI - API Dokümantasyonu

## 📋 Genel Bilgiler

**Base URL**: `http://localhost:8000` (development)  
**API Version**: v1.0.0  
**Content-Type**: `application/json`  
**Authentication**: OpenAI API Key (environment variable)

## 🔗 Endpoint'ler

### 1. Chat Endpoint

Teknik destek sorularınızı yanıtlar.

```http
POST /chat
```

**Request Body:**
```json
{
    "message": "SMART-2 cihazımda kalibrasyon sorunu var"
}
```

**Response:**
```json
{
    "response": "SMART-2 cihazınızda kalibrasyon sorununu çözmek için aşağıdaki adımları izleyebilirsiniz:\n\n1. **Cihazı Hazırlayın**: Cihazı düz ve sağlam bir yüzeye yerleştirin...",
    "classification": {
        "categories": ["calibration", "error"],
        "primary_category": "calibration",
        "is_howto": false,
        "has_problem": true
    },
    "has_manual_info": false,
    "search_results": {
        "error": "PDF search not available"
    },
    "success": true,
    "available_products": [
        "TR-4 Scale",
        "ART-2 Scale",
        "ECI Automatic Scale",
        "PWI Series Indicator",
        "Weighfly Scale",
        "LCA Load Cell",
        "SMART-2 Scale",
        "ART Scale",
        "AS Axle Scale",
        "LCA-B Load Cell",
        "AWS Aircraft Weighing System",
        "TR-3 Scale"
    ],
    "product_categories": ["Indicator", "Load Cell", "Weighing Scale"],
    "total_products": 12,
    "image_urls": []
}
```

**Response Fields:**
- `response`: AI'ın verdiği yanıt
- `classification`: Sorunun kategorilendirilmesi
- `available_products`: Mevcut tüm ürünler
- `product_categories`: Ürün kategorileri
- `total_products`: Toplam ürün sayısı
- `success`: İşlem başarı durumu

### 2. Ürünleri Listele

Tüm mevcut ürünleri ve kategorileri listeler.

```http
GET /products
```

**Response:**
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
    "categories": ["Indicator", "Load Cell", "Weighing Scale"],
    "total_products": 12,
    "total_categories": 3
}
```

### 3. Ürün Arama

Ürün adı veya kategoriye göre arama yapar.

```http
GET /search?query={query}&category={category}
```

**Parameters:**
- `query` (string): Arama terimi
- `category` (string, optional): Kategori filtresi

**Example:**
```http
GET /search?query=Load%20Cell&category=Load%20Cell
```

**Response:**
```json
{
    "status": "success",
    "query": "Load Cell",
    "category": "Load Cell",
    "matching_products": [
        {
            "filename": "Esit-LCA-User-Manual-EN.pdf",
            "product_name": "LCA Load Cell",
            "product_category": "Load Cell",
            "language": "English",
            "file_path": "data/manuals/Esit-LCA-User-Manual-EN.pdf"
        },
        {
            "filename": "LCA-B-AR-User Manual-EN.pdf",
            "product_name": "LCA-B Load Cell",
            "product_category": "Load Cell",
            "language": "English",
            "file_path": "data/manuals/LCA-B-AR-User Manual-EN.pdf"
        }
    ],
    "total_matches": 2
}
```

### 4. Sistem Durumu

Sistemin genel durumunu kontrol eder.

```http
GET /health
```

**Response:**
```json
{
    "status": "ok",
    "system": "ESİT Technical Support AI",
    "pdf_available": false,
    "multi_manual_enabled": true,
    "available_products": 12,
    "product_categories": ["Indicator", "Load Cell", "Weighing Scale"],
    "supabase_enabled": false
}
```

### 5. Feedback Gönder

Kullanıcı geri bildirimlerini toplar.

```http
POST /feedback
```

**Request Body:**
```json
{
    "message_id": "msg_1234567890_abc123",
    "feedback_type": "positive",
    "user_message": "SMART-2 kalibrasyonu nasıl yapılır?",
    "bot_response": "SMART-2 cihazınızda kalibrasyon...",
    "timestamp": "2025-09-15T08:54:16.677Z",
    "reason": null
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Feedback submitted successfully"
}
```

### 6. Feedback Analizi

Geri bildirim analizi ve öneriler.

```http
GET /feedback/analysis
```

**Response:**
```json
{
    "total_feedback": 25,
    "positive_count": 20,
    "negative_count": 5,
    "satisfaction_rate": 80.0,
    "suggestions": [
        "Overall satisfaction is good. Keep up the quality responses."
    ],
    "recent_negative_feedback": [
        "Response was too technical",
        "Missing specific steps"
    ]
}
```

### 7. Günlük Rapor

Günlük feedback raporu.

```http
GET /feedback/daily-report
```

**Response:**
```json
{
    "date": "2025-09-15",
    "daily_stats": {
        "total_feedback": 5,
        "positive_count": 4,
        "negative_count": 1,
        "satisfaction_rate": 80.0
    },
    "recent_negative_samples": [
        {
            "user_message": "ART-2 sorunu",
            "bot_response": "ART-2 cihazınızda...",
            "timestamp": "2025-09-15T08:54:16.677Z"
        }
    ],
    "overall_stats": {
        "total_all_time": 25,
        "positive_all_time": 20,
        "negative_all_time": 5
    }
}
```

### 8. Konuşmayı Sıfırla

AI konuşma geçmişini temizler.

```http
POST /reset
```

**Response:**
```json
{
    "success": true,
    "message": "Konuşma sıfırlandı"
}
```

### 9. Logo

ESİT logosunu döndürür.

```http
GET /logo
```

**Response:** PNG image file

## 🔧 Error Handling

### HTTP Status Codes

- `200 OK`: Başarılı işlem
- `400 Bad Request`: Geçersiz istek
- `404 Not Found`: Endpoint bulunamadı
- `500 Internal Server Error`: Sunucu hatası

### Error Response Format

```json
{
    "response": "Üzgünüm, şu anda teknik bir sorun yaşıyorum. Lütfen tekrar deneyin.",
    "error": "OpenAI API connection failed",
    "success": false
}
```

## 📝 Örnek Kullanımlar

### Python ile API Kullanımı

```python
import requests
import json

# Chat API
def ask_question(question):
    response = requests.post('http://localhost:8000/chat', 
                           json={'message': question})
    return response.json()

# Ürünleri listele
def get_products():
    response = requests.get('http://localhost:8000/products')
    return response.json()

# Ürün ara
def search_products(query, category=None):
    params = {'query': query}
    if category:
        params['category'] = category
    
    response = requests.get('http://localhost:8000/search', params=params)
    return response.json()

# Kullanım örnekleri
result = ask_question("SMART-2 kalibrasyonu nasıl yapılır?")
print(result['response'])

products = get_products()
print(f"Toplam {products['total_products']} ürün mevcut")

search_result = search_products("Load Cell", "Load Cell")
print(f"{search_result['total_matches']} ürün bulundu")
```

### JavaScript ile API Kullanımı

```javascript
// Chat API
async function askQuestion(question) {
    const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: question })
    });
    return await response.json();
}

// Ürünleri listele
async function getProducts() {
    const response = await fetch('http://localhost:8000/products');
    return await response.json();
}

// Kullanım örnekleri
askQuestion("ART-2 cihazımda sorun var")
    .then(result => console.log(result.response));

getProducts()
    .then(products => console.log(`${products.total_products} ürün mevcut`));
```

### cURL Örnekleri

```bash
# Chat sorusu
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "TR-4 cihazımda ekran sorunu var"}'

# Ürünleri listele
curl http://localhost:8000/products

# Ürün ara
curl "http://localhost:8000/search?query=Scale&category=Weighing%20Scale"

# Sistem durumu
curl http://localhost:8000/health

# Feedback gönder
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "msg_123",
    "feedback_type": "positive",
    "user_message": "SMART-2 sorunu",
    "bot_response": "SMART-2 çözümü...",
    "timestamp": "2025-09-15T08:54:16.677Z"
  }'
```

## 🔒 Rate Limiting

Şu anda rate limiting uygulanmamaktadır, ancak gelecekte eklenecektir.

## 📊 Monitoring

API kullanımını izlemek için:

1. `/health` endpoint'ini düzenli olarak kontrol edin
2. `/feedback/analysis` ile kullanıcı memnuniyetini izleyin
3. Log dosyalarını kontrol edin (`data/processed/feedback.log`)

## 🚀 Production Notları

- OpenAI API key'inizi güvenli bir şekilde saklayın
- Production'da HTTPS kullanın
- Rate limiting implementasyonu yapın
- Monitoring ve alerting sistemi kurun
- Database backup'ları düzenli olarak alın
