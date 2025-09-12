# Railway Deployment Rehberi

## 1. Railway Hesabı Oluşturma
1. https://railway.app adresine git
2. GitHub ile giriş yap
3. "New Project" oluştur

## 2. Proje Deployment
1. "Deploy from GitHub repo" seç
2. `esit-engine` repository'sini seç
3. Railway otomatik olarak Dockerfile'ı algılayacak

## 3. Environment Variables Ayarlama
Railway dashboard'da Variables sekmesine git ve şunları ekle:

```
OPENAI_API_KEY=sk-your-openai-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
PORT=8000
```

## 4. Persistent Storage
PDF dosyaları için persistent storage ekle:
1. Railway dashboard'da "Volumes" sekmesi
2. "Create Volume" 
3. Mount path: `/app/data`
4. Size: 1GB (başlangıç için yeterli)

## 5. Custom Domain (Opsiyonel)
1. Settings > Domains
2. Custom domain ekle
3. DNS ayarlarını yap

## 6. Monitoring
Railway otomatik olarak şunları sağlar:
- Logs monitoring
- Metrics dashboard
- Health checks
- Auto-scaling
