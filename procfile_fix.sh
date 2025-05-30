#!/bin/bash

# PROCFILE ZORLA GÜNCELLEME
echo "🔧 PROCFILE ZORLA GÜNCELLEME"
echo "============================="

cd /Users/hikmettanriverdi/Desktop/AliExpressBot

echo "📝 Procfile'ı yeniden yazıyoruz..."
echo "web: python3 aliexpress_bot_improved_captcha.py" > Procfile

echo "🔄 Timestamp dummy değişiklik..."
echo "# Railway cache bypass: $(date +%s)" >> aliexpress_bot_improved_captcha.py

echo "📦 Git operations..."
git add .
git commit -m "🔧 PROCFILE FIX: Force Railway restart $(date +%s)"

echo ""
echo "🚀 Pushing with cache invalidation..."
git push origin main

echo ""
echo "✅ Procfile fix pushed!"
echo ""
echo "🎯 Railway should now use: aliexpress_bot_improved_captcha.py"
echo "⏰ Build should start in 30 seconds"
