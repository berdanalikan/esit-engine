# ESİT Technical Support AI - Kullanıcı Rehberi

## 📋 Genel Bakış

ESİT Technical Support AI, ESİT ürünleri için akıllı teknik destek sağlayan bir yapay zeka sistemidir. Bu rehber, sistemi nasıl kullanacağınızı açıklar.

## 🎯 Sistem Özellikleri

- **12 Farklı ESİT Ürünü**: Tüm ESİT ürünlerini destekler
- **Türkçe Destek**: Türkçe sorularınızı yanıtlar
- **Akıllı Kategorileme**: Sorunlarınızı otomatik kategorize eder
- **Adım Adım Rehberlik**: Detaylı çözüm adımları sunar
- **Gerçek Zamanlı Chat**: Anında yanıt alırsınız

## 🚀 Sisteme Erişim

### Web Arayüzü

1. Tarayıcınızda `http://localhost:8000` adresine gidin
2. Chat arayüzü otomatik olarak açılacaktır
3. Sorularınızı yazıp Enter tuşuna basın

### API Erişimi

Geliştiriciler için API endpoint'leri mevcuttur:
- Base URL: `http://localhost:8000`
- Dokümantasyon: `/docs/api/API_DOCUMENTATION.md`

## 📦 Desteklenen Ürünler

### Weighing Scale (Tartım Cihazları)

| Ürün | Açıklama |
|------|----------|
| **TR-4 Scale** | TR-4 serisi tartım cihazı |
| **ART-2 Scale** | ART-2 serisi tartım cihazı |
| **ECI Automatic Scale** | ECI otomatik tartım cihazı |
| **Weighfly Scale** | Weighfly tartım cihazı |
| **SMART-2 Scale** | SMART-2 serisi tartım cihazı |
| **ART Scale** | ART serisi tartım cihazı |
| **AS Axle Scale** | AS aks tartım cihazı |
| **AWS Aircraft Weighing System** | Uçak tartım sistemi |
| **TR-3 Scale** | TR-3 serisi tartım cihazı |

### Load Cell (Yük Hücreleri)

| Ürün | Açıklama |
|------|----------|
| **LCA Load Cell** | LCA yük hücresi |
| **LCA-B Load Cell** | LCA-B yük hücresi |

### Indicator (Göstergeler)

| Ürün | Açıklama |
|------|----------|
| **PWI Series Indicator** | PWI serisi gösterge |

## 💬 Nasıl Soru Sorulur?

### 1. Ürün Adını Belirtin

**✅ İyi Örnekler:**
- "SMART-2 cihazımda kalibrasyon sorunu var"
- "ART-2 Scale'de ekran problemi yaşıyorum"
- "TR-4 cihazımda ağırlık ölçüm hatası alıyorum"

**❌ Kötü Örnekler:**
- "Cihazımda sorun var" (hangi ürün?)
- "Kalibrasyon nasıl yapılır?" (hangi cihaz?)

### 2. Sorunun Detaylarını Açıklayın

**✅ İyi Örnekler:**
- "SMART-2 cihazımda kalibrasyon yaparken hata alıyorum"
- "ART-2 Scale'in ekranı açılmıyor, güç düğmesine bastığımda hiçbir şey olmuyor"
- "TR-4 cihazında ölçüm yaparken sürekli 'E' hatası çıkıyor"

**❌ Kötü Örnekler:**
- "Çalışmıyor" (ne çalışmıyor?)
- "Hata veriyor" (hangi hata?)

### 3. Soru Türleri

#### Sorun Çözme Soruları

```
"SMART-2 cihazımda kalibrasyon sorunu var"
"ART-2 Scale'in ekranı açılmıyor"
"TR-4 cihazında ölçüm hatası alıyorum"
```

#### Nasıl Yapılır Soruları

```
"SMART-2 kalibrasyonu nasıl yapılır?"
"ART-2 Scale'de ağırlık birimi nasıl değiştirilir?"
"TR-4 cihazında bakım nasıl yapılır?"
```

#### Kurulum Soruları

```
"LCA Load Cell nasıl kurulur?"
"PWI Series Indicator bağlantısı nasıl yapılır?"
"AS Axle Scale montajı nasıl yapılır?"
```

## 🔧 Sorun Kategorileri

Sistem sorunlarınızı otomatik olarak kategorize eder:

### 1. Power (Güç Sorunları)
- Cihaz açılmıyor
- Güç kesintisi
- Elektrik bağlantı sorunları

**Anahtar Kelimeler:** güç, power, açılmıyor, kapanıyor, elektrik, enerji

### 2. Calibration (Kalibrasyon)
- Kalibrasyon hatası
- Ağırlık ayarı
- Ölçüm doğruluğu

**Anahtar Kelimeler:** kalibrasyon, calibration, ayar, setting, ölçüm, measurement

### 3. Display (Ekran Sorunları)
- Ekran açılmıyor
- Görüntü sorunları
- Gösterge problemleri

**Anahtar Kelimeler:** ekran, display, gösterge, screen, görünmüyor

### 4. Connection (Bağlantı Sorunları)
- Kablo bağlantıları
- Network sorunları
- Veri transferi

**Anahtar Kelimeler:** bağlantı, connection, kablo, cable, ethernet, network

### 5. Error (Hata Kodları)
- Sistem hataları
- Alarm mesajları
- Uyarılar

**Anahtar Kelimeler:** hata, error, alarm, uyarı, warning, sorun, problem

### 6. Installation (Kurulum)
- Montaj sorunları
- Setup problemleri
- Konfigürasyon

**Anahtar Kelimeler:** kurulum, installation, setup, montaj

### 7. Maintenance (Bakım)
- Temizlik
- Servis
- Bakım işlemleri

**Anahtar Kelimeler:** bakım, maintenance, temizlik, cleaning, servis

## 📱 Web Arayüzü Kullanımı

### Ana Ekran

1. **Chat Alanı**: Sorularınızı yazdığınız alan
2. **Gönder Butonu**: Soruyu göndermek için
3. **Sesli Yanıt Butonu**: TTS özelliği (gelecekte aktif olacak)
4. **Menü Butonu**: Sol üst köşedeki hamburger menü

### Menü Özellikleri

#### Sohbet Geçmişi
- Önceki sorularınızı görüntüleyin
- Geçmiş konuşmaları tekrar açın

#### Teknik Destek
- Genel destek
- Kalibrasyon adımları
- Ağırlık göstergesi
- Bağlantı sorunları
- Ekran problemleri

#### Ürün Kategorileri
- ART Serisi
- SMART Serisi
- ECI Serisi
- Ölçüm Cihazları
- Yedek Parçalar

#### Hızlı Erişim
- Sık sorulan sorular
- Hata kodları
- İletişim bilgileri
- Kullanım kılavuzu
- Video eğitimler

### Feedback Sistemi

Her AI yanıtının altında feedback butonları bulunur:

- **👍 İyi**: Yanıt yararlıydı
- **👎 Kötü**: Yanıt yararlı değildi

Kötü feedback verdiğinizde:
1. Neden seçin (yanlış bilgi, eksik açıklama, vb.)
2. Ek açıklama yazın (isteğe bağlı)
3. Gönder butonuna tıklayın

## 🔍 Arama Özellikleri

### Ürün Arama

API üzerinden ürün arama yapabilirsiniz:

```bash
# Tüm ürünleri listele
curl http://localhost:8000/products

# Belirli bir ürün ara
curl "http://localhost:8000/search?query=SMART-2"

# Kategoriye göre ara
curl "http://localhost:8000/search?category=Weighing%20Scale"
```

### Arama Sonuçları

Arama sonuçları şunları içerir:
- Ürün adı
- Kategori
- Dosya yolu
- Dil bilgisi

## 📊 Sistem Durumu

### Health Check

Sistemin durumunu kontrol etmek için:

```bash
curl http://localhost:8000/health
```

Yanıt:
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

## 🚨 Sorun Giderme

### Yaygın Sorunlar

#### 1. Sistem Yanıt Vermiyor

**Çözüm:**
- Sayfayı yenileyin
- Internet bağlantınızı kontrol edin
- Sistem durumunu kontrol edin: `http://localhost:8000/health`

#### 2. Yanlış Ürün Tanıma

**Çözüm:**
- Ürün adını daha spesifik yazın
- Tam model adını kullanın (örn: "SMART-2 Scale" yerine "SMART-2")

#### 3. Eksik Bilgi

**Çözüm:**
- Sorunuzu daha detaylı açıklayın
- Hata mesajlarını tam olarak yazın
- Cihazın durumunu belirtin

### Feedback Verme

Yanlış veya eksik yanıtlar için:

1. 👎 butonuna tıklayın
2. Neden seçin:
   - Yanlış bilgi verdi
   - Eksik açıklama
   - Anlaşılmaz
   - Konuyla alakasız
   - Çok uzun
   - Diğer
3. Ek açıklama yazın
4. Gönder butonuna tıklayın

## 📞 İletişim

### Acil Durumlar

Sistem çalışmıyorsa:

- **Telefon**: (0216) 585 18 18
- **Email**: servis@esit.com.tr

### Teknik Destek

- **Web**: [ESİT Web Sitesi]
- **Email**: teknik@esit.com.tr

## 💡 İpuçları

### 1. Etkili Soru Sorma

- Ürün adını her zaman belirtin
- Sorunun detaylarını açıklayın
- Hata mesajlarını tam olarak yazın
- Cihazın durumunu belirtin

### 2. Hızlı Çözüm

- Önce basit çözümleri deneyin
- AI'ın önerdiği adımları sırayla takip edin
- Her adımdan sonra sonucu kontrol edin

### 3. Feedback Verme

- Yararlı yanıtlar için 👍 verin
- Eksik yanıtlar için 👎 verin ve nedenini belirtin
- Bu, sistemin gelişmesine yardımcı olur

## 🔄 Sistem Güncellemeleri

Sistem düzenli olarak güncellenir:

- Yeni ürün desteği
- Geliştirilmiş AI yanıtları
- Yeni özellikler
- Hata düzeltmeleri

Güncellemeler otomatik olarak uygulanır, herhangi bir işlem yapmanız gerekmez.

---

**Not**: Bu sistem sürekli geliştirilmektedir. Önerileriniz için feedback sistemini kullanın.
