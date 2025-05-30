#!/bin/bash

# 🎯 GitHub'a Sadece Gerekli Dosyaları Yükle

echo "🤖 AliExpress Bot - GitHub Upload (Clean Version)"
echo "================================================="

# Dizin kontrolü
cd /Users/hikmettanriverdi/Desktop/AliExpressBot

echo "📋 Yüklenecek dosyalar:"
echo "✅ aliexpress_bot_web_entegre.py (Ana uygulama)"
echo "✅ templates/ (Web arayüzü)"
echo "✅ requirements.txt"
echo "✅ Procfile"
echo "✅ .env.example"
echo "✅ README.md"
echo "✅ .gitignore"
echo "✅ RAILWAY_DEPLOYMENT.md"
echo "✅ chrome_driver_kur.sh"
echo "✅ chromedriver_duzelt.sh"
echo ""

# Git başlat
git init

# Sadece önemli dosyaları ekle
git add aliexpress_bot_web_entegre.py
git add templates/
git add requirements.txt
git add Procfile
git add .env.example
git add README.md
git add .gitignore
git add RAILWAY_DEPLOYMENT.md
git add GITHUB_UPLOAD_REHBERI.md
git add chrome_driver_kur.sh
git add chromedriver_duzelt.sh

# Commit
git commit -m "🚀 AliExpress Bot - Clean deployment ready

✨ Core Features:
- AI-powered product scraping with Selenium
- Excel integration with column mapping
- Real-time web interface
- Gemini 2.5 Pro + ChatGPT-4o support
- Railway deployment ready

📁 Project Structure:
- aliexpress_bot_web_entegre.py: Main Flask application
- templates/bot_arayuz.html: Web interface
- requirements.txt: Python dependencies
- Procfile: Railway deployment configuration
- .env.example: Environment variables template

🚀 Ready for Railway deployment!"

echo ""
echo "✅ Git repository hazırlandı!"
echo ""
echo "🌍 Şimdi GitHub'da repository oluşturun:"
echo "1. https://github.com/new"
echo "2. Name: 'aliexpress-bot'"
echo "3. Public/Private seçin"
echo "4. 'Create repository'"
echo ""
echo "📤 Sonra bu komutları çalıştırın:"
echo "git remote add origin https://github.com/KULLANICI_ADI/aliexpress-bot.git"
echo "git branch -M main"
echo "git push -u origin main"
