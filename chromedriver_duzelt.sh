#!/bin/bash

echo "🔧 ChromeDriver Sorun Giderme Başlatılıyor..."
echo "============================================="

# WebDriver Manager cache'ini temizle
echo "🗑️ WebDriver Manager cache temizleniyor..."
rm -rf ~/.wdm/drivers/chromedriver
echo "✅ Cache temizlendi"

# Homebrew ChromeDriver'ı da temizle ve yeniden kur
echo "🔄 Homebrew ChromeDriver yeniden kuruluyor..."
brew uninstall chromedriver 2>/dev/null || true
brew install chromedriver

# ChromeDriver'ı yetkilendir
echo "🔐 ChromeDriver yetkilendiriliyor..."
if [ -f "/opt/homebrew/bin/chromedriver" ]; then
    xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver 2>/dev/null || true
    chmod +x /opt/homebrew/bin/chromedriver
    echo "✅ ChromeDriver yetkilendirildi (Apple Silicon)"
fi

if [ -f "/usr/local/bin/chromedriver" ]; then
    xattr -d com.apple.quarantine /usr/local/bin/chromedriver 2>/dev/null || true
    chmod +x /usr/local/bin/chromedriver
    echo "✅ ChromeDriver yetkilendirildi (Intel Mac)"
fi

# Chrome sürümünü kontrol et
echo "🌐 Chrome sürümü kontrol ediliyor..."
CHROME_VERSION=$(/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version 2>/dev/null || echo "Chrome bulunamadı")
echo "Chrome sürümü: $CHROME_VERSION"

echo ""
echo "🎉 ChromeDriver temizleme tamamlandı!"
echo "Şimdi botu tekrar deneyin."

read -p "Devam etmek için ENTER'a basın..."
