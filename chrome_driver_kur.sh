#!/bin/bash
# Chrome Driver Otomatik Kurulum Scripti (Mac ARM64)

echo "🔧 Mac ARM64 için ChromeDriver kuruluyor..."

# Homebrew ile kur (en kolay yol)
if command -v brew &> /dev/null; then
    echo "🍺 Homebrew ile ChromeDriver kuruluyor..."
    brew install chromedriver
    
    # Güvenlik izni ver
    if [ -f "/opt/homebrew/bin/chromedriver" ]; then
        sudo xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver 2>/dev/null || true
        echo "✅ ChromeDriver kuruldu: /opt/homebrew/bin/chromedriver"
    elif [ -f "/usr/local/bin/chromedriver" ]; then
        sudo xattr -d com.apple.quarantine /usr/local/bin/chromedriver 2>/dev/null || true
        echo "✅ ChromeDriver kuruldu: /usr/local/bin/chromedriver"
    fi
else
    echo "❌ Homebrew bulunamadı. Manual kurulum..."
    
    # Manuel kurulum
    echo "📥 ChromeDriver indiriliyor..."
    curl -L https://chromedriver.storage.googleapis.com/120.0.6099.71/chromedriver_mac_arm64.zip -o /tmp/chromedriver.zip
    
    cd /tmp && unzip -o chromedriver.zip
    sudo mv chromedriver /usr/local/bin/
    sudo chmod +x /usr/local/bin/chromedriver
    sudo xattr -d com.apple.quarantine /usr/local/bin/chromedriver 2>/dev/null || true
    
    echo "✅ ChromeDriver manuel olarak kuruldu!"
fi

# Kurulum kontrolü
if command -v chromedriver &> /dev/null; then
    echo "🎉 ChromeDriver başarıyla kuruldu!"
    chromedriver --version
else
    echo "❌ ChromeDriver kurulumu başarısız"
fi
