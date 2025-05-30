# 🚀 Railway Deployment Guide

## 📋 GEREKLI DOSYALAR (HAZIR!)

✅ `Procfile` - Railway start komutu
✅ `requirements.txt` - Python bağımlılıkları  
✅ `.env.example` - Environment variables örneği
✅ Kodda production Chrome ayarları

## 🚀 RAILWAY DEPLOYMENT ADIMLARI:

### 1. Railway Hesabı Oluştur
- https://railway.app adresine git
- GitHub ile giriş yap
- Ücretsiz plan ile başla

### 2. GitHub Repository Oluştur
```bash
# Terminal'de:
cd /Users/hikmettanriverdi/Desktop/AliExpressBot

# Git repository başlat
git init
git add .
git commit -m "🚀 AliExpress Bot - Railway deployment ready"

# GitHub'a push et (önce GitHub'da repo oluştur)
git remote add origin https://github.com/KULLANICI_ADI/aliexpress-bot
git push -u origin main
```

### 3. Railway'de Proje Oluştur
- Railway dashboard'da "New Project"
- "Deploy from GitHub repo" seç
- Repository'ni seç (`aliexpress-bot`)
- Railway otomatik deploy edecek

### 4. Environment Variables Ayarla
Railway dashboard'da Variables sekmesine git:

```bash
# Zorunlu değişkenler
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here

# Production ayarları
RAILWAY_ENVIRONMENT=true
CHROME_BIN=/usr/bin/google-chrome
CHROMEDRIVER_PATH=/usr/bin/chromedriver
```

### 5. Chrome Dependencies Ekle
Railway ayarlarda "Settings" > "Build Options":

**Nixpacks Build Args:**
```json
{
  "NIXPACKS_APT_PACKAGES": "chromium chromium-driver"
}
```

**YA DA** Railway `nixpacks.toml` dosyası:
```toml
[phases.setup]
aptPackages = ["chromium", "chromium-driver"]
```

### 6. Test Et!
- Railway size bir URL verecek: `https://aliexpress-bot-production.up.railway.app`
- Bu URL'yi açın ve test edin

## 🎯 MALİYET:
- **Hobby Plan**: $5/ay
- **500 saat/ay execution time**
- **8GB RAM, 8vCPU**
- **Otomatik SSL sertifikası**

## 🐛 SORUN GİDERME:

### Chrome/ChromeDriver Hatası:
```bash
# Railway logs'ta şu komutu çalıştır:
which google-chrome
which chromedriver

# Eğer bulunamazsa environment variables güncelle:
CHROME_BIN=/usr/bin/chromium
CHROMEDRIVER_PATH=/usr/bin/chromedriver
```

### Selenium Timeout:
Production'da headless mode daha yavaş, timeout'ları artır.

### Memory Issues:  
Chrome'da `--disable-images` ve `--disable-plugins` zaten var.

## 🎯 SONUÇ:
Railway deployment en kolay seçenek! 
- 5 dakikada deploy
- Otomatik SSL
- GitHub entegrasyonu
- $5/ay başlangıç

Netlify + Supabase için complete rewrite gerekiyor ama Railway mevcut kodunuzu hiç değiştirmeden deploy ediyor! 🚀
