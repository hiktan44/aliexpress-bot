🚀 GitHub'a Yükleme Rehberi

ADIM 1: GitHub'da Repository Oluşturun
=====================================
1. https://github.com/new adresine gidin
2. Repository name: "aliexpress-bot"
3. Description: "🤖 AI-powered AliExpress product scraper with Excel integration and Railway deployment"
4. Public seçin (ya da Private)
5. "Create repository" tıklayın

ADIM 2: Terminal Komutları
=========================
Terminal'de şu komutları sırayla çalıştırın:

cd /Users/hikmettanriverdi/Desktop/AliExpressBot

# Git repository başlat
git init

# Dosyaları ekle
git add .

# İlk commit
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

# GitHub remote ekle (KULLANICI_ADI'nı kendi GitHub kullanıcı adınızla değiştirin)
git remote add origin https://github.com/KULLANICI_ADI/aliexpress-bot.git

# Main branch oluştur
git branch -M main

# GitHub'a yükle
git push -u origin main

ADIM 3: Railway Deployment
=========================
1. https://railway.app adresine gidin
2. GitHub ile giriş yapın
3. "New Project" tıklayın
4. "Deploy from GitHub repo" seçin
5. "aliexpress-bot" repository'sini seçin
6. Variables sekmesine gidin ve ekleyin:
   - OPENAI_API_KEY=your_openai_key_here
   - GEMINI_API_KEY=your_gemini_key_here
   - RAILWAY_ENVIRONMENT=true

7. Deploy tamamlanacak ve size URL verilecek!

🎯 HAZIR DOSYALAR:
✅ aliexpress_bot_web_entegre.py (Ana uygulama)
✅ templates/bot_arayuz.html (Web arayüzü)
✅ requirements.txt (Python bağımlılıkları)
✅ Procfile (Railway deployment)
✅ .env.example (Environment variables)
✅ README.md (Dokümantasyon)
✅ .gitignore (Git ignore kuralları)
✅ RAILWAY_DEPLOYMENT.md (Deployment rehberi)

🚀 Hadi GitHub'a yükleyin ve Railway'de deploy edin!
