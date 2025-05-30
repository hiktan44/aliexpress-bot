#!/bin/bash

# 🚀 GitHub Repository Oluşturma ve Upload Script

echo "🤖 AliExpress Bot - GitHub Upload Script"
echo "========================================"

# Proje dizinine git
cd /Users/hikmettanriverdi/Desktop/AliExpressBot

# Git repository başlat
echo "📦 Git repository başlatılıyor..."
git init

# Dosyaları stage'e ekle
echo "📁 Dosyalar ekleniyor..."
git add .

# İlk commit
echo "💾 İlk commit yapılıyor..."
git commit -m "🚀 Initial commit - AliExpress Bot with Railway deployment ready

✨ Features:
- Excel file upload & column mapping system
- AI-powered HS code analysis (Gemini 2.5 Pro + ChatGPT-4o)
- Real-time web interface with live data tracking
- Selenium-based web scraping with anti-detection
- Production deployment ready for Railway/Render
- Auto-download updated Excel files

🔧 Technical:
- Flask web framework
- Selenium WebDriver
- Google Gemini & OpenAI integration
- Responsive web UI
- Chrome headless mode for production

🌍 Deployment:
- Railway/Render cloud deployment ready
- Environment variables configured
- Production Chrome settings
- Procfile and requirements.txt included"

echo ""
echo "✅ Git repository hazırlandı!"
echo ""
echo "🌍 Şimdi GitHub'da repository oluşturun:"
echo "1. https://github.com/new adresine gidin"
echo "2. Repository name: 'aliexpress-bot'"
echo "3. Description: 'AI-powered AliExpress product scraper with Excel integration'"
echo "4. Public/Private seçin"
echo "5. 'Create repository' tıklayın"
echo ""
echo "📤 Sonra bu komutu çalıştırın:"
echo "git remote add origin https://github.com/KULLANICI_ADI/aliexpress-bot.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "🎯 Railway deployment için:"
echo "1. https://railway.app adresine gidin"
echo "2. GitHub ile giriş yapın"
echo "3. 'New Project' → 'Deploy from GitHub repo'"
echo "4. 'aliexpress-bot' repository'sini seçin"
echo "5. Environment variables ekleyin (OPENAI_API_KEY, GEMINI_API_KEY)"
echo "6. Deploy!"
echo ""
echo "📋 Gerekli dosyalar hazırlandı:"
echo "✅ README.md - Detaylı dokümantasyon"
echo "✅ .gitignore - Git ignore kuralları"
echo "✅ requirements.txt - Python bağımlılıkları"
echo "✅ Procfile - Railway deployment"
echo "✅ .env.example - Environment variables örneği"
echo "✅ RAILWAY_DEPLOYMENT.md - Deployment guide"
echo ""
echo "🚀 Hadi GitHub'a yükleyin!"
