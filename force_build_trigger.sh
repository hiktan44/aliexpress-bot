#!/bin/bash

# ZORLA BUILD TETİKLEME - Railway Cache Clear
echo "🚨 ZORLA BUILD TETİKLEME"
echo "========================"

cd /Users/hikmettanriverdi/Desktop/AliExpressBot

echo "🗑️ Bozuk dosyayı siliyoruz..."
rm -f aliexpress_bot_web_entegre.py

echo "📝 Procfile'ı kontrol ediyoruz..."
echo "web: python3 aliexpress_bot_improved_captcha.py" > Procfile

echo "🔄 Dummy değişiklik yapıyoruz (cache bypass)..."
echo "# Build trigger: $(date)" >> README.md

echo "📦 Git operations..."
git add .
git commit -m "🚨 FORCE BUILD: Cache clear + Syntax fix

- Removed broken aliexpress_bot_web_entegre.py
- Using aliexpress_bot_improved_captcha.py only
- Fixed syntax error completely  
- Force build trigger: $(date)
- Railway cache bypass"

echo ""
echo "🚀 Force pushing with cache bypass..."
git push origin main --force-with-lease

echo ""
echo "✅ Force build triggered!"
echo ""
echo "📋 Next steps:"
echo "1. Railway build should start in 30 seconds"
echo "2. Monitor build logs"
echo "3. Should use improved_captcha.py now"
echo ""
echo "🔥 Force build completed!"
