#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AliExpress Bot - Hibrit Sistem V2 + Railway Web Entegrasyonu
Manuel CAPTCHA çözme + Gelişmiş veri çekme + Web Arayüzü
"""

import pandas as pd
import time
import random
import os
import threading
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Flask web server için
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)
PORT = int(os.getenv('PORT', 5000))

class AliExpressBotHibritV2:
    def __init__(self, web_mode=False):
        self.driver = None
        self.sonuclar = []
        self.basarili = 0
        self.basarisiz = 0
        self.manuel_captcha = 0
        self.web_mode = web_mode
        self.running = False
        self.current_progress = ""
        
    def browser_baslat(self):
        """Railway için Chrome browser (headless + normal mod)"""
        try:
            chrome_options = Options()
            
            if self.web_mode:
                # Railway için headless ayarlar
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            else:
                # Lokal için görünür mod
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--window-size=1200,800")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            mode = "Railway Headless" if self.web_mode else "Lokal Görünür"
            self.log(f"✅ Chrome browser başlatıldı ({mode})")
            return True
            
        except Exception as e:
            self.log(f"❌ Browser hatası: {e}")
            return False
    
    def log(self, message):
        """Loglama sistemi"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        self.current_progress = log_msg
    
    def captcha_bekle(self):
        """CAPTCHA kontrolü - Railway'de otomatik skip"""
        if self.web_mode:
            # Railway'de CAPTCHA varsa skip et
            return False
            
        captcha_selectors = [
            "iframe[src*='captcha']",
            ".nc_wrapper",
            ".geetest"
        ]
        
        for selector in captcha_selectors:
            if self.driver.find_elements(By.CSS_SELECTOR, selector):
                self.log("🤖 CAPTCHA tespit edildi!")
                if not self.web_mode:
                    self.log("👤 Manuel CAPTCHA çözümü bekleniyor...")
                    input("✅ CAPTCHA çözüldü mü? ENTER'a basın...")
                    self.manuel_captcha += 1
                return True
        return False
    
    def detayli_veri_cek(self, link):
        """Gelişmiş veri çekme - hibrit v2 sistemi"""
        try:
            self.log(f"📦 Ürün sayfası açılıyor...")
            
            self.driver.get(link)
            time.sleep(3)
            
            # CAPTCHA kontrolü
            if self.captcha_bekle():
                self.log("✅ CAPTCHA işlendi, veri çekiliyor...")
                time.sleep(3)
            
            # Sayfa yüklenme bekleme
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                pass
            
            self.log("🔍 Detaylı ürün bilgileri aranıyor...")
            
            # Veri çekme
            urun_adi = "Bilgi bulunamadı"
            fiyat = "Bilgi bulunamadı"
            resim_url = "Bilgi bulunamadı"
            
            # 1. ÜRÜN ADI
            isim_selectors = [
                "h1[data-pl='product-title']",
                ".product-title-text",
                "h1.x-item-title-label", 
                ".pdp-product-name",
                "h1",
                ".title"
            ]
            
            for selector in isim_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    text = element.text.strip()
                    if text and len(text) > 10:
                        urun_adi = text[:200]
                        self.log(f"✅ Ürün adı bulundu")
                        break
                except:
                    continue
            
            # 2. FİYAT
            fiyat_selectors = [
                ".product-price-current",
                ".price-current",
                "[data-pl='price']",
                ".price",
                ".notranslate"
            ]
            
            for selector in fiyat_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and any(char in text for char in ['$', '₺', '€', 'US']):
                            if len(text) > 1 and len(text) < 50:
                                fiyat = text
                                self.log(f"✅ Fiyat bulundu: {fiyat}")
                                break
                    if fiyat != "Bilgi bulunamadı":
                        break
                except:
                    continue
            
            # 3. RESİM
            resim_selectors = [
                "img.magnifier-image",
                ".pdp-main-image img",
                "img[src*='aliexpress']"
            ]
            
            for selector in resim_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    src = element.get_attribute("src")
                    if src and 'http' in src:
                        resim_url = src
                        self.log(f"✅ Resim bulundu")
                        break
                except:
                    continue
            
            # Sonuç hazırla
            sonuc = {
                'Link': link,
                'Ürün Adı': urun_adi,
                'Fiyat': fiyat,
                'Resim URL': resim_url,
                'Durum': 'Başarılı',
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.log("📋 Ürün bilgileri toplandı")
            return sonuc
            
        except Exception as e:
            self.log(f"❌ Veri çekme hatası: {e}")
            return {
                'Link': link,
                'Ürün Adı': 'Hata',
                'Fiyat': 'Hata',
                'Resim URL': 'Hata',
                'Durum': f'Hata: {str(e)[:30]}',
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def run_bot(self, linkler):
        """Bot'u çalıştır"""
        try:
            self.running = True
            self.log("🤝 Hibrit V2 Bot başlatılıyor!")
            
            if not self.browser_baslat():
                return False
            
            self.log(f"📊 {len(linkler)} ürün işlenecek")
            
            for i, link in enumerate(linkler, 1):
                if not self.running:
                    break
                    
                self.log(f"🔄 Ürün {i}/{len(linkler)} işleniyor...")
                
                sonuc = self.detayli_veri_cek(link)
                
                if sonuc and sonuc['Durum'] == 'Başarılı':
                    self.sonuclar.append(sonuc)
                    self.basarili += 1
                else:
                    self.basarisiz += 1
                
                self.log(f"📊 Başarılı: {self.basarili}, Başarısız: {self.basarisiz}")
                
                # Bekleme
                if i < len(linkler):
                    time.sleep(random.uniform(2, 4))
            
            self.log("🏁 Bot işlemi tamamlandı!")
            return True
            
        except Exception as e:
            self.log(f"❌ Bot hatası: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
            self.running = False

# Global bot instance
bot_instance = None
bot_status = {
    "running": False,
    "progress": "",
    "results": [],
    "stats": {"basarili": 0, "basarisiz": 0, "captcha": 0}
}

# Web arayüzü HTML
WEB_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AliExpress Bot Hibrit V2 - Railway</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #333; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .status { background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #28a745; }
        .running { border-left-color: #ffc107; background: #fff3cd; }
        .btn { display: inline-block; padding: 12px 24px; margin: 8px; background: #007bff; color: white; text-decoration: none; border-radius: 8px; border: none; cursor: pointer; font-weight: bold; }
        .btn:hover { background: #0056b3; }
        .btn.success { background: #28a745; }
        .btn.warning { background: #ffc107; color: #212529; }
        .btn.danger { background: #dc3545; }
        .results { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0; max-height: 400px; overflow-y: auto; }
        textarea { width: 100%; height: 120px; margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-family: monospace; }
        .progress { background: #e9ecef; padding: 10px; border-radius: 5px; margin: 10px 0; font-family: monospace; font-size: 12px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-card { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤝 AliExpress Bot</h1>
            <h2>Hibrit Sistem V2 - Railway</h2>
            <p>🔍 Gelişmiş veri çekme + 💰 Fiyat + 🖼️ Resim sistemi</p>
        </div>

        <div class="status {{ 'running' if bot_running else '' }}">
            <h3>{{ '🔄 Bot Çalışıyor...' if bot_running else '✅ Hibrit V2 Hazır' }}</h3>
            <p><strong>Durum:</strong> {{ 'Aktif olarak çalışıyor' if bot_running else 'Beklemede' }}</p>
            <p><strong>Son Güncelleme:</strong> {{ datetime.now().strftime('%H:%M:%S') }}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h4>✅ Başarılı</h4>
                <h2>{{ stats.basarili }}</h2>
            </div>
            <div class="stat-card">
                <h4>❌ Başarısız</h4>
                <h2>{{ stats.basarisiz }}</h2>
            </div>
            <div class="stat-card">
                <h4>🤖 CAPTCHA</h4>
                <h2>{{ stats.captcha }}</h2>
            </div>
            <div class="stat-card">
                <h4>📊 Toplam</h4>
                <h2>{{ stats.basarili + stats.basarisiz }}</h2>
            </div>
        </div>

        <h3>🔧 Bot Kontrolleri</h3>
        <button onclick="runBot()" class="btn success" {{ 'disabled' if bot_running else '' }}>
            🚀 {{ 'Bot Çalışıyor...' if bot_running else 'Hibrit Bot Başlat' }}
        </button>
        <button onclick="stopBot()" class="btn danger">⏹️ Bot Durdur</button>
        <a href="/status" class="btn">📊 Status API</a>
        <a href="/results" class="btn">📈 Sonuçlar</a>
        <a href="/health" class="btn">🏥 Health</a>

        <h3>📝 Test URL'leri (AliExpress)</h3>
        <textarea id="test_urls" placeholder="AliExpress URL'lerini buraya yapıştırın (her satıra bir URL)...">
https://www.aliexpress.com/item/1005004356847433.html
https://www.aliexpress.com/item/1005003456789012.html</textarea>
        
        <button onclick="testUrls()" class="btn warning">🔍 URL'leri İşle</button>
        <button onclick="clearResults()" class="btn">🗑️ Sonuçları Temizle</button>

        {% if progress %}
        <div class="progress">
            <strong>📈 Canlı Progress:</strong><br>
            {{ progress }}
        </div>
        {% endif %}

        <div class="results">
            <h4>📋 Son Sonuçlar:</h4>
            {% if results %}
                {% for result in results[-5:] %}
                <div style="border-bottom: 1px solid #ddd; padding: 10px 0;">
                    <strong>🔗 {{ result.get('Link', '')[:50] }}...</strong><br>
                    📝 <strong>Ürün:</strong> {{ result.get('Ürün Adı', 'N/A')[:60] }}...<br>
                    💰 <strong>Fiyat:</strong> {{ result.get('Fiyat', 'N/A') }}<br>
                    🖼️ <strong>Resim:</strong> {{ '✅ Var' if result.get('Resim URL') != 'Bilgi bulunamadı' else '❌ Yok' }}<br>
                    ⏰ {{ result.get('Timestamp', '') }}
                </div>
                {% endfor %}
            {% else %}
                <p>Henüz sonuç yok. Bot'u başlatın!</p>
            {% endif %}
        </div>

        <div style="margin-top: 30px; padding: 20px; background: #e9ecef; border-radius: 8px;">
            <h4>🎯 Hibrit V2 Özellikleri:</h4>
            <ul>
                <li>✅ Railway deployment ile cloud çalışma</li>
                <li>✅ Detaylı ürün bilgisi çekme (ad, fiyat, resim)</li>
                <li>✅ JavaScript ile gelişmiş arama</li>
                <li>✅ Gerçek zamanlı progress takibi</li>
                <li>✅ Headless browser Railway uyumluluğu</li>
                <li>✅ Manuel CAPTCHA desteği (lokal mod)</li>
            </ul>
        </div>
    </div>

    <script>
        function runBot() {
            const urls = document.getElementById('test_urls').value;
            const urlList = urls.split('\\n').filter(url => url.trim() && url.includes('aliexpress'));
            
            if (urlList.length === 0) {
                alert('Geçerli AliExpress URL\'leri girin!');
                return;
            }
            
            fetch('/run-hibrit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({urls: urlList})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`Hibrit Bot başlatıldı! ${urlList.length} URL işlenecek.`);
                    setTimeout(() => location.reload(), 2000);
                } else {
                    alert('Hata: ' + data.error);
                }
            });
        }

        function stopBot() {
            fetch('/stop-hibrit', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                location.reload();
            });
        }

        function testUrls() { runBot(); }

        function clearResults() {
            fetch('/clear-results', {method: 'POST'})
            .then(() => location.reload());
        }

        // 3 saniyede bir otomatik güncelleme (bot çalışıyorsa)
        {% if bot_running %}
        setTimeout(() => location.reload(), 3000);
        {% endif %}
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(WEB_TEMPLATE,
                                bot_running=bot_status["running"],
                                progress=bot_status["progress"],
                                results=bot_status["results"],
                                stats=bot_status["stats"],
                                datetime=datetime)

@app.route('/run-hibrit', methods=['POST'])
def run_hibrit():
    global bot_instance, bot_status
    
    if bot_status["running"]:
        return jsonify({"success": False, "error": "Bot zaten çalışıyor"})
    
    data = request.get_json()
    urls = data.get('urls', [])
    
    if not urls:
        return jsonify({"success": False, "error": "URL listesi boş"})
    
    # Bot'u thread'de başlat
    def hibrit_thread():
        global bot_instance, bot_status
        try:
            bot_status["running"] = True
            bot_instance = AliExpressBotHibritV2(web_mode=True)
            
            if bot_instance.run_bot(urls):
                bot_status["results"] = bot_instance.sonuclar
                bot_status["stats"] = {
                    "basarili": bot_instance.basarili,
                    "basarisiz": bot_instance.basarisiz,
                    "captcha": bot_instance.manuel_captcha
                }
        except Exception as e:
            bot_status["progress"] = f"Hata: {e}"
        finally:
            bot_status["running"] = False
    
    thread = threading.Thread(target=hibrit_thread)
    thread.daemon = True
    thread.start()
    
    return jsonify({"success": True, "message": f"Hibrit V2 başlatıldı - {len(urls)} URL işlenecek"})

@app.route('/stop-hibrit', methods=['POST'])
def stop_hibrit():
    global bot_instance, bot_status
    bot_status["running"] = False
    if bot_instance:
        bot_instance.running = False
    return jsonify({"message": "Hibrit bot durduruldu"})

@app.route('/clear-results', methods=['POST'])
def clear_results():
    global bot_status
    bot_status["results"] = []
    bot_status["stats"] = {"basarili": 0, "basarisiz": 0, "captcha": 0}
    return jsonify({"message": "Sonuçlar temizlendi"})

@app.route('/status')
def status():
    return jsonify(bot_status)

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "hibrit_v2": "active",
        "railway": True,
        "bot_ready": True
    })

@app.route('/results')
def get_results():
    return jsonify({"results": bot_status["results"], "count": len(bot_status["results"])})

if __name__ == '__main__':
    print(f"🚀 AliExpress Bot Hibrit V2 + Railway Web Server")
    print(f"🌐 Port: {PORT}")
    print(f"🤝 Hibrit sistem hazır!")
    
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)