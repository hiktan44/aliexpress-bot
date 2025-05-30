#!/bin/bash

# Hızlı Fix - Railway Push Script
echo "🚀 Critical Fixes - Railway Push"
echo "================================"

cd /Users/hikmettanriverdi/Desktop/AliExpressBot

echo "📤 Adding critical fixes..."
git add .

echo ""
echo "📝 Committing fixes..."
git commit -m "🚨 Critical Fixes: Web Modal CAPTCHA + Success Control

✅ Railway: Only web modal CAPTCHA (no visible Chrome)
✅ Production mode: Screenshot + user action system
✅ Removed broken visible mode attempt in Railway
✅ CAPTCHA detection: iframe, slider, geetest support
✅ Success control: Bilgi bulunamadı → BAŞARISIZ
✅ Log improvements for better debugging

Railway'de GUI olmadığı için sadece web modal kullanılıyor!"

echo ""
echo "🚀 Pushing to Railway..."
git push origin main

echo ""
echo "✅ Critical fixes deployed!"
echo ""
echo "🎯 Expected behavior:"
echo "   📱 CAPTCHA → Web modal screenshot"
echo "   ❌ Bilgi bulunamadı → BAŞARISIZ"
echo "   🌐 No visible Chrome in Railway"
echo "   📸 Screenshot + user action system"
echo ""
echo "🔥 Ready for testing!"
