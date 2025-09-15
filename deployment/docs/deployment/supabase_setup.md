# Supabase Kurulum Rehberi

## 1. Supabase Projesi Oluşturma
1. https://supabase.com adresine git
2. "Start your project" butonuna tıkla
3. GitHub ile giriş yap
4. "New Project" oluştur
5. Proje adı: `esit-tech-support`
6. Database password: Güçlü bir şifre seç
7. Region: Europe (Frankfurt) seç

## 2. Veritabanı Tablosu Oluşturma
SQL Editor'da şu komutu çalıştır:

```sql
-- Feedback tablosu
CREATE TABLE feedback (
    id BIGSERIAL PRIMARY KEY,
    message_id TEXT NOT NULL,
    feedback_type TEXT NOT NULL CHECK (feedback_type IN ('positive', 'negative')),
    user_message TEXT,
    bot_response TEXT,
    timestamp TIMESTAMPTZ,
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    server_timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_agent TEXT
);

-- İndeksler
CREATE INDEX idx_feedback_message_id ON feedback(message_id);
CREATE INDEX idx_feedback_type ON feedback(feedback_type);
CREATE INDEX idx_feedback_created_at ON feedback(created_at);

-- RLS (Row Level Security) aktif et
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Herkesin insert yapabilmesi için policy
CREATE POLICY "Enable insert for all users" ON feedback
    FOR INSERT WITH CHECK (true);

-- Herkesin select yapabilmesi için policy  
CREATE POLICY "Enable select for all users" ON feedback
    FOR SELECT USING (true);
```

## 3. API Keys Alma
1. Settings > API sekmesine git
2. Project URL'yi kopyala
3. anon/public key'i kopyala

## 4. Environment Variables
Bu değerleri deployment platformunda ayarla:
- `SUPABASE_URL`: Project URL
- `SUPABASE_ANON_KEY`: anon/public key
