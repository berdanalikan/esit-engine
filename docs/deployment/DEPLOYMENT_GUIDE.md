# ESİT Technical Support AI - Deployment Rehberi

## 📋 Genel Bakış

Bu rehber, ESİT Technical Support AI sistemini farklı platformlarda nasıl deploy edeceğinizi açıklar.

## 🚀 Deployment Seçenekleri

### 1. Render.com (Önerilen)

Render.com, Python uygulamaları için kolay ve güvenilir bir deployment platformudur.

#### Adım 1: Render.com Hesabı Oluşturun

1. [Render.com](https://render.com) adresine gidin
2. GitHub hesabınızla giriş yapın
3. Repository'nizi bağlayın

#### Adım 2: Web Service Oluşturun

1. Dashboard'da "New +" butonuna tıklayın
2. "Web Service" seçin
3. Repository'nizi seçin

#### Adım 3: Konfigürasyon

**Basic Settings:**
- **Name**: `esit-technical-support-ai`
- **Environment**: `Python 3`
- **Region**: `Oregon (US West)`
- **Branch**: `main`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python src/api/app.py`

**Advanced Settings:**
- **Instance Type**: `Starter` (ücretsiz) veya `Standard` (ücretli)
- **Auto-Deploy**: `Yes`

#### Adım 4: Environment Variables

Environment Variables sekmesinde şunları ekleyin:

```
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_url_here (opsiyonel)
SUPABASE_ANON_KEY=your_supabase_anon_key_here (opsiyonel)
PORT=8000
```

#### Adım 5: Deploy

"Create Web Service" butonuna tıklayın. Deployment işlemi 5-10 dakika sürebilir.

### 2. Railway

Railway, modern bir deployment platformudur.

#### Adım 1: Railway Hesabı

1. [Railway.app](https://railway.app) adresine gidin
2. GitHub hesabınızla giriş yapın

#### Adım 2: Proje Oluşturun

1. "New Project" butonuna tıklayın
2. "Deploy from GitHub repo" seçin
3. Repository'nizi seçin

#### Adım 3: Konfigürasyon

Railway otomatik olarak Python uygulamasını algılayacaktır.

**Environment Variables:**
```
OPENAI_API_KEY=your_openai_api_key_here
PORT=8000
```

#### Adım 4: Deploy

Railway otomatik olarak deploy edecektir.

### 3. Heroku

Heroku, popüler bir PaaS platformudur.

#### Adım 1: Heroku CLI Kurulumu

```bash
# macOS
brew install heroku/brew/heroku

# Windows
# Heroku CLI'ı resmi siteden indirin
```

#### Adım 2: Heroku Hesabı

```bash
heroku login
```

#### Adım 3: Proje Oluşturun

```bash
heroku create esit-technical-support-ai
```

#### Adım 4: Environment Variables

```bash
heroku config:set OPENAI_API_KEY=your_openai_api_key_here
heroku config:set PORT=8000
```

#### Adım 5: Deploy

```bash
git push heroku main
```

### 4. Docker ile Deployment

#### Adım 1: Dockerfile Hazırlığı

Mevcut `Dockerfile` kullanılabilir:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "src/api/app.py"]
```

#### Adım 2: Docker Image Oluşturun

```bash
docker build -t esit-technical-support-ai .
```

#### Adım 3: Container Çalıştırın

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  esit-technical-support-ai
```

#### Adım 4: Docker Compose (Opsiyonel)

`docker-compose.yml` dosyası oluşturun:

```yaml
version: '3.8'

services:
  esit-ai:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PORT=8000
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

Çalıştırın:

```bash
docker-compose up -d
```

### 5. VPS/Cloud Server

#### Adım 1: Server Hazırlığı

```bash
# Ubuntu/Debian için
sudo apt update
sudo apt install python3.12 python3.12-venv nginx

# CentOS/RHEL için
sudo yum update
sudo yum install python3.12 nginx
```

#### Adım 2: Uygulama Kurulumu

```bash
# Repository'yi klonlayın
git clone <your-repo-url>
cd esit-engine

# Sanal ortam oluşturun
python3.12 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

#### Adım 3: Systemd Service

`/etc/systemd/system/esit-ai.service` dosyası oluşturun:

```ini
[Unit]
Description=ESİT Technical Support AI
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/esit-engine
Environment=PATH=/path/to/esit-engine/venv/bin
Environment=OPENAI_API_KEY=your_openai_api_key_here
Environment=PORT=8000
ExecStart=/path/to/esit-engine/venv/bin/python src/api/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Adım 4: Nginx Konfigürasyonu

`/etc/nginx/sites-available/esit-ai` dosyası oluşturun:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Adım 5: Servisleri Başlatın

```bash
# Systemd service'i etkinleştirin
sudo systemctl enable esit-ai
sudo systemctl start esit-ai

# Nginx'i yeniden başlatın
sudo systemctl restart nginx
```

## 🔧 Environment Variables

### Gerekli Değişkenler

| Değişken | Açıklama | Örnek |
|----------|----------|-------|
| `OPENAI_API_KEY` | OpenAI API anahtarı | `sk-...` |
| `PORT` | Uygulama portu | `8000` |

### Opsiyonel Değişkenler

| Değişken | Açıklama | Örnek |
|----------|----------|-------|
| `SUPABASE_URL` | Supabase URL | `https://xxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase anon key | `eyJ...` |
| `FEEDBACK_DIR` | Feedback dosyaları dizini | `/app/data/processed` |

## 📊 Monitoring ve Logging

### Health Check

Tüm deployment'larda health check endpoint'ini kullanın:

```bash
curl https://your-domain.com/health
```

### Log Monitoring

```bash
# Render.com
# Dashboard'da logs sekmesini kontrol edin

# Railway
railway logs

# Heroku
heroku logs --tail

# Docker
docker logs <container-id>

# Systemd
journalctl -u esit-ai -f
```

### Performance Monitoring

```bash
# CPU ve Memory kullanımı
htop

# Disk kullanımı
df -h

# Network bağlantıları
netstat -tulpn
```

## 🔒 Güvenlik

### SSL/TLS Sertifikası

#### Let's Encrypt (Ücretsiz)

```bash
# Certbot kurulumu
sudo apt install certbot python3-certbot-nginx

# Sertifika oluşturma
sudo certbot --nginx -d your-domain.com

# Otomatik yenileme
sudo crontab -e
# Şu satırı ekleyin:
0 12 * * * /usr/bin/certbot renew --quiet
```

#### Cloudflare (Önerilen)

1. [Cloudflare](https://cloudflare.com) hesabı oluşturun
2. Domain'inizi ekleyin
3. DNS kayıtlarını güncelleyin
4. SSL/TLS ayarlarını yapın

### Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Firewalld (CentOS)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 🚨 Troubleshooting

### Yaygın Sorunlar

#### 1. Port Zaten Kullanımda

```bash
# Port'u kullanan process'i bulun
lsof -ti:8000

# Process'i sonlandırın
kill -9 <process-id>
```

#### 2. OpenAI API Key Hatası

```bash
# Environment variable'ı kontrol edin
echo $OPENAI_API_KEY

# Uygulama içinde kontrol edin
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

#### 3. Memory Hatası

```bash
# Memory kullanımını kontrol edin
free -h

# Swap ekleyin (gerekirse)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 4. Disk Space Hatası

```bash
# Disk kullanımını kontrol edin
df -h

# Log dosyalarını temizleyin
sudo journalctl --vacuum-time=7d
```

### Debug Modu

```bash
# Debug logları ile çalıştırın
PYTHONPATH=. python -u src/api/app.py

# Verbose logging
export PYTHONPATH=.
export LOG_LEVEL=DEBUG
python src/api/app.py
```

## 📈 Scaling

### Horizontal Scaling

#### Load Balancer ile

```nginx
upstream esit_ai {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://esit_ai;
    }
}
```

#### Docker Swarm ile

```bash
# Swarm cluster oluşturun
docker swarm init

# Service deploy edin
docker service create \
  --name esit-ai \
  --replicas 3 \
  --publish 8000:8000 \
  esit-technical-support-ai
```

### Vertical Scaling

- CPU ve RAM'i artırın
- SSD kullanın
- Network bandwidth'i artırın

## 🔄 Backup ve Recovery

### Backup Stratejisi

```bash
# Günlük backup scripti
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/esit-ai"

# Uygulama dosyalarını backup'la
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /path/to/esit-engine

# Veritabanı backup'ı (gerekirse)
# pg_dump your_db > $BACKUP_DIR/db_$DATE.sql

# Eski backup'ları temizle (30 günden eski)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Recovery

```bash
# Backup'tan restore
tar -xzf /backup/esit-ai/app_20250915_120000.tar.gz -C /

# Servisi yeniden başlat
sudo systemctl restart esit-ai
```

## 📞 Destek

Deployment sorunları için:

1. Log dosyalarını kontrol edin
2. Health check endpoint'ini test edin
3. Environment variables'ları kontrol edin
4. Network bağlantılarını test edin
5. Gerekirse platform destek ekibiyle iletişime geçin

---

**Not**: Bu rehber genel deployment senaryolarını kapsar. Spesifik platform gereksinimleri için platform dokümantasyonunu kontrol edin.
