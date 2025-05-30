#!/bin/bash

# NUCLEAR OPTION - RAILWAY CACHE CLEAR
echo "🚨 NUCLEAR OPTION - CACHE CLEAR"
echo "================================"

cd /Users/hikmettanriverdi/Desktop/AliExpressBot

echo "🗑️ Procfile'ı tamamen silip yeniden oluşturuyoruz..."
rm -f Procfile

echo "📝 Yeni Procfile oluşturuluyor..."
cat > Procfile << 'EOF'
web: python3 aliexpress_bot_improved_captcha.py
EOF

echo "🔄 Git cache clear..."
git rm --cached -r . 2>/dev/null || true
git reset --hard HEAD

echo "📦 Fresh git operations..."
git add -A
git commit -m "🚨 NUCLEAR FIX: Complete Railway cache clear

- Deleted and recreated Procfile
- Cleared git cache completely  
- Using aliexpress_bot_improved_captcha.py
- Timestamp: $(date)
- Force new build"

echo ""
echo "🚀 Nuclear push with cache invalidation..."
git push origin main --force

echo ""
echo "✅ Nuclear option completed!"
echo ""
echo "📋 Expected result:"
echo "   Railway should completely rebuild"
echo "   Use: aliexpress_bot_improved_captcha.py"
echo "   Clear all cache"
echo ""
echo "⏰ Wait 2-3 minutes for complete rebuild"
