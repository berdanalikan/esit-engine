# Render 502 Bad Gateway Çözümü

## 🔧 Adım Adım Çözüm

### 1. Render Dashboard'da Ayarları Kontrol Et

#### Service Settings:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python start_render.py`
- **Python Version**: `3.12.0`

#### Environment Variables:
```
PORT=10000
OPENAI_API_KEY=sk-your-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ-your-anon-key-here
FEEDBACK_DIR=/opt/render/project/src/data
```

### 2. Logs Kontrolü
Render dashboard → Logs sekmesinde şunları ara:
- ❌ `ModuleNotFoundError`
- ❌ `ImportError`
- ❌ `Port already in use`
- ❌ `Permission denied`

### 3. Yaygın Hatalar ve Çözümleri

#### Hata: "ModuleNotFoundError: No module named 'faiss'"
**Çözüm**: requirements.txt'de faiss-cpu yerine faiss-cpu kullan

#### Hata: "Port already in use"
**Çözüm**: PORT environment variable'ını 10000 olarak ayarla

#### Hata: "Permission denied"
**Çözüm**: Start command'ı `python start_render.py` olarak değiştir

### 4. Manuel Deploy
Eğer otomatik deploy çalışmıyorsa:
1. Render dashboard → "Manual Deploy"
2. "Deploy latest commit" tıkla
3. Logs'ları takip et

### 5. Health Check
Deploy sonrası test et:
```
https://your-app.onrender.com/health
```

Beklenen yanıt:
```json
{
  "status": "ok",
  "system": "ESİT Technical Support AI",
  "pdf_available": true,
  "supabase_enabled": true
}
```

### 6. Troubleshooting

#### PDF Dosyası Bulunamıyor:
- PDF dosyasını repository'ye commit ettiğinden emin ol
- Dosya adında Türkçe karakter olmasın

#### Supabase Bağlantı Hatası:
- SUPABASE_URL ve SUPABASE_ANON_KEY doğru mu kontrol et
- Supabase dashboard'da RLS policy'leri aktif mi?

#### OpenAI API Hatası:
- OPENAI_API_KEY geçerli mi?
- API quota'sı var mı?

## 🚀 Hızlı Test

Deploy sonrası şu URL'leri test et:
1. `https://your-app.onrender.com/` - Ana sayfa
2. `https://your-app.onrender.com/health` - Health check
3. `https://your-app.onrender.com/test-supabase` - Supabase test
