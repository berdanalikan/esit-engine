# Supabase API Keys Nasıl Bulunur

## 📍 Supabase Dashboard'da API Keys Bulma

### 1. Supabase Projesine Giriş
1. https://supabase.com adresine git
2. "Sign in" ile giriş yap
3. Projenizi seçin

### 2. API Keys'e Erişim
1. Sol menüden **"Settings"** (⚙️) tıkla
2. **"API"** sekmesine tıkla
3. Burada 2 önemli key göreceksin:

### 3. Gerekli Keys

#### 🔑 **Project URL**
```
https://your-project-id.supabase.co
```
- Bu URL'yi kopyala
- Environment variable: `SUPABASE_URL`

#### 🔑 **anon/public key**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlvdXItcHJvamVjdC1pZCIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNjQ5OTk5OTk5LCJleHAiOjE5NjU1NzU5OTl9.example-signature
```
- Bu uzun JWT token'ı kopyala
- Environment variable: `SUPABASE_ANON_KEY`

### 4. Service Role Key (Opsiyonel)
- **service_role** key'i de var ama bu daha güçlü
- Sadece backend'de kullan, frontend'de kullanma
- Environment variable: `SUPABASE_SERVICE_ROLE_KEY`

## 🚨 Güvenlik Uyarıları

### ✅ Güvenli Kullanım
- `anon/public` key'i frontend'de kullanabilirsin
- Row Level Security (RLS) aktif olduğu sürece güvenli
- Environment variables'da sakla

### ❌ Güvenlik Riskleri
- `service_role` key'ini frontend'de kullanma
- Keys'leri kod içinde hardcode etme
- Public repository'lerde paylaşma

## 📝 Environment Variables Örneği

```bash
# Railway/Render/Fly.io'da şunları ayarla:
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
OPENAI_API_KEY=sk-proj-...
```

## 🔍 Keys'i Test Etme

Supabase dashboard'da **"API"** sekmesinde:
- **"REST API"** bölümünde test endpoint'leri var
- **"GraphQL"** endpoint'i de mevcut
- **"Realtime"** için WebSocket URL'i var

## 📱 Mobile/Web App için

### Frontend (React/Vue/Angular)
```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://your-project.supabase.co'
const supabaseKey = 'your-anon-key'

export const supabase = createClient(supabaseUrl, supabaseKey)
```

### Backend (Python/FastAPI)
```python
import os
from supabase import create_client, Client

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)
```
