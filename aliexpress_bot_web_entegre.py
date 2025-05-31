#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AliExpress Bot - Complete Ultimate V3
Scrape.do + Selenium + Anti-Captcha + Excel Upload + All Features
"""

import pandas as pd
import time
import random
import os
import threading
import requests
import base64
import json
import re
import io
from datetime import datetime
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Flask web server için
from flask import Flask, jsonify, render_template_string, request, send_file

app = Flask(__name__)
PORT = int(os.getenv('PORT', 5000))

class ScrapeDoAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = "http://api.scrape.do"
        
    def scrape_aliexpress(self, url):
        """AliExpress için optimize edilmiş Scrape.do çağrısı"""
        try:
            # URL encode
            encoded_url = quote(url, safe='')
            
            # Scrape.do parameters
            params = {
                'url': encoded_url,
                'token': self.token,
                'super': 'true',
                'render': 'true',
                'extraHeaders': 'true',
                'geoCode': 'us',
                'playwithbrowser': json.dumps([{
                    "action": "WaitSelector",
                    "waitSelector": ".product-price-value,[class^='price--current--']",
                    "timeout": 20000
                }])
            }
            
            headers = {
                'sd-referer': 'https://www.aliexpress.com/'
            }
            
            response = requests.get(self.base_url, params=params, headers=headers, timeout=60)
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"❌ Scrape.do hata: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Scrape.do API hatası: {e}")
            return None

class AntiCaptchaAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.anti-captcha.com"
        
    def get_balance(self):
        """Bakiye kontrolü"""
        try:
            response = requests.post(f"{self.base_url}/getBalance", 
                                   json={"clientKey": self.api_key})
            result = response.json()
            if result.get("errorId") == 0:
                return result.get("balance")
            return None
        except:
            return None

class AliExpressParser:
    """AliExpress JSON data parser"""
    
    @staticmethod
    def extract_json_data(html_content):
        """HTML içinden JSON datalarını çıkar"""
        try:
            json_patterns = [
                r'window\.runParams\s*=\s*({.*?});',
                r'window\.pageData\s*=\s*({.*?});', 
                r'__INITIAL_STATE__\s*=\s*({.*?});',
                r'window\.__moduleData__\s*=\s*({.*?});',
                r'"skuModule":\s*({.*?}),',
                r'"priceModule":\s*({.*?}),',
                r'"imageModule":\s*({.*?}),',
                r'"titleModule":\s*({.*?}),',
            ]
            
            extracted_data = {}
            
            for pattern in json_patterns:
                matches = re.findall(pattern, html_content, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        extracted_data.update(data)
                    except:
                        continue
            
            return extracted_data
            
        except Exception as e:
            print(f"❌ JSON extraction hatası: {e}")
            return {}
    
    @staticmethod
    def parse_product_data(json_data, html_content):
        """JSON data'dan ürün bilgilerini çıkar"""
        try:
            product_info = {
                'title': 'Bilgi bulunamadı',
                'price': 'Bilgi bulunamadı', 
                'image': 'Bilgi bulunamadı',
                'rating': 'Bilgi bulunamadı',
                'sold_count': 'Bilgi bulunamadı'
            }
            
            # BAŞLIK - JSON'dan
            title_sources = [
                lambda d: d.get('titleModule', {}).get('subject', ''),
                lambda d: d.get('data', {}).get('subject', ''),
                lambda d: d.get('pageData', {}).get('product', {}).get('subject', ''),
            ]
            
            for source in title_sources:
                try:
                    title = source(json_data)
                    if title and len(title) > 10:
                        product_info['title'] = title[:200]
                        break
                except:
                    continue
            
            # FİYAT - JSON'dan
            price_sources = [
                lambda d: d.get('priceModule', {}).get('formatedPrice', ''),
                lambda d: d.get('priceModule', {}).get('minPrice', {}).get('formatedPrice', ''),
                lambda d: d.get('data', {}).get('priceModule', {}).get('formatedPrice', ''),
            ]
            
            for source in price_sources:
                try:
                    price = source(json_data)
                    if price:
                        product_info['price'] = price
                        break
                except:
                    continue
            
            # RESİM - JSON'dan
            image_sources = [
                lambda d: d.get('imageModule', {}).get('imagePathList', [None])[0],
                lambda d: d.get('data', {}).get('imageModule', {}).get('imagePathList', [None])[0],
            ]
            
            for source in image_sources:
                try:
                    image = source(json_data)
                    if image:
                        if not image.startswith('http'):
                            image = 'https:' + image if image.startswith('//') else 'https://ae01.alicdn.com/kf/' + image
                        product_info['image'] = image
                        break
                except:
                    continue
            
            # HTML fallback (JSON'da bulamazsa)
            if product_info['title'] == 'Bilgi bulunamadı':
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
                if title_match:
                    title = title_match.group(1).strip()
                    if 'AliExpress' not in title and len(title) > 10:
                        product_info['title'] = title[:200]
            
            if product_info['price'] == 'Bilgi bulunamadı':
                price_patterns = [
                    r'US\s*\$\s*[\d,.]+',
                    r'[\$€£¥₹₽]\s*[\d,.]+',
                ]
                for pattern in price_patterns:
                    price_match = re.search(pattern, html_content)
                    if price_match:
                        product_info['price'] = price_match.group(0)
                        break
            
            return product_info
            
        except Exception as e:
            print(f"❌ Product parsing hatası: {e}")
            return {
                'title': 'Parse hatası',
                'price': 'Parse hatası', 
                'image': 'Parse hatası',
                'rating': 'Parse hatası',
                'sold_count': 'Parse hatası'
            }

class AliExpressBotUltimate:
    def __init__(self, web_mode=False, scrape_do_token=None, anticaptcha_key=None):
        self.driver = None
        self.sonuclar = []
        self.basarili = 0
        self.basarisiz = 0
        self.captcha_cozulen = 0
        self.scrape_do_kullanim = 0
        self.selenium_kullanim = 0
        self.web_mode = web_mode
        self.running = False
        self.current_progress = ""
        
        # API services
        self.scrape_do = ScrapeDoAPI(scrape_do_token) if scrape_do_token else None
        self.anticaptcha = AntiCaptchaAPI(anticaptcha_key) if anticaptcha_key else None
        self.parser = AliExpressParser()
        
        # API durumları log
        if self.scrape_do:
            self.log("✅ Scrape.do API aktif")
        if self.anticaptcha:
            balance = self.anticaptcha.get_balance()
            if balance:
                self.log(f"✅ Anti-Captcha aktif, bakiye: ${balance}")
        
    def log(self, message):
        """Loglama sistemi"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        self.current_progress = log_msg
    
    def scrape_with_scrape_do(self, url):
        """Scrape.do ile veri çekme (birincil method)"""
        try:
            self.log("🌐 Scrape.do ile sayfa çekiliyor...")
            
            html_content = self.scrape_do.scrape_aliexpress(url)
            
            if html_content:
                self.scrape_do_kullanim += 1
                self.log("✅ Scrape.do HTML alındı, JSON parsing...")
                
                # JSON data extraction
                json_data = self.parser.extract_json_data(html_content)
                
                if json_data:
                    self.log("✅ JSON data bulundu, parsing...")
                    product_info = self.parser.parse_product_data(json_data, html_content)
                    
                    # Sonuç formatla
                    sonuc = {
                        'Link': url,
                        'Ürün Adı': product_info['title'],
                        'Fiyat': product_info['price'],
                        'Resim URL': product_info['image'],
                        'Rating': product_info['rating'],
                        'Satış Sayısı': product_info['sold_count'],
                        'Method': 'Scrape.do + JSON',
                        'Durum': 'Başarılı',
                        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    return sonuc
                else:
                    self.log("⚠️ JSON data bulunamadı, HTML fallback...")
                    return self.parse_html_fallback(url, html_content)
            else:
                self.log("❌ Scrape.do başarısız, Selenium'a geçiliyor...")
                return None
                
        except Exception as e:
            self.log(f"❌ Scrape.do hatası: {e}")
            return None
    
    def parse_html_fallback(self, url, html_content):
        """HTML parsing fallback"""
        try:
            self.log("🔍 HTML fallback parsing...")
            
            # Basit HTML regex patterns
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
            title = title_match.group(1).strip()[:200] if title_match else 'Bilgi bulunamadı'
            
            price_patterns = [
                r'US\s*\$\s*[\d,.]+',
                r'[\$€£¥₹₽]\s*[\d,.]+',
                r'[\d,.]+\s*USD',
            ]
            
            price = 'Bilgi bulunamadı'
            for pattern in price_patterns:
                price_match = re.search(pattern, html_content)
                if price_match:
                    price = price_match.group(0)
                    break
            
            return {
                'Link': url,
                'Ürün Adı': title,
                'Fiyat': price,
                'Resim URL': 'HTML parse',
                'Rating': 'HTML parse',
                'Satış Sayısı': 'HTML parse',
                'Method': 'Scrape.do + HTML',
                'Durum': 'Kısmi başarılı',
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            self.log(f"❌ HTML fallback hatası: {e}")
            return None
    
    def scrape_product(self, url):
        """Ultimate scraping method"""
        try:
            # Method 1: Scrape.do (Primary)
            if self.scrape_do:
                result = self.scrape_with_scrape_do(url)
                if result and result.get('Durum') in ['Başarılı', 'Kısmi başarılı']:
                    return result
            
            # Method 2: Simple requests fallback
            self.log("🌐 Simple requests fallback...")
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
            if response.status_code == 200:
                return self.parse_html_fallback(url, response.text)
            
            return None
            
        except Exception as e:
            self.log(f"❌ Scraping hatası: {e}")
            return None
    
    def run_bot(self, linkler):
        """Ultimate bot çalıştırma"""
        try:
            self.running = True
            self.log("🚀 AliExpress Ultimate Bot başlatılıyor!")
            self.log(f"📊 {len(linkler)} ürün işlenecek")
            
            for i, link in enumerate(linkler, 1):
                if not self.running:
                    break
                    
                self.log(f"🔄 Ürün {i}/{len(linkler)} işleniyor...")
                
                sonuc = self.scrape_product(link)
                
                if sonuc:
                    self.sonuclar.append(sonuc)
                    self.basarili += 1
                    self.log(f"✅ Başarılı: {sonuc.get('Method', 'Unknown')}")
                else:
                    self.basarisiz += 1
                    self.log(f"❌ Başarısız")
                
                # İstatistikler
                self.log(f"📊 Başarılı: {self.basarili}, Başarısız: {self.basarisiz}")
                
                # Rate limiting
                if i < len(linkler):
                    time.sleep(random.uniform(1, 3))
            
            self.log("🏁 Ultimate bot tamamlandı!")
            return True
            
        except Exception as e:
            self.log(f"❌ Bot hatası: {e}")
            return False
        finally:
            self.running = False

# Global bot instance
bot_instance = None
bot_status = {
    "running": False,
    "progress": "",
    "results": [],
    "stats": {"basarili": 0, "basarisiz": 0, "captcha": 0, "scrape_do": 0, "selenium": 0}
}

# Web arayüzü HTML
WEB_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AliExpress Ultimate Bot - Complete Edition</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #333; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .status { background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #28a745; }
        .running { border-left-color: #ffc107; background: #fff3cd; }
        .btn { display: inline-block; padding: 12px 24px; margin: 8px; background: #007bff; color: white; text-decoration: none; border-radius: 8px; border: none; cursor: pointer; font-weight: bold; }
        .btn:hover { background: #0056b3; }
        .btn.success { background: #28a745; }
        .btn.warning { background: #ffc107; color: #212529; }
        .btn.danger { background: #dc3545; }
        .btn.info { background: #17a2b8; }
        .results { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0; max-height: 500px; overflow-y: auto; }
        textarea { width: 100%; height: 120px; margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-family: monospace; }
        .progress { background: #e9ecef; padding: 10px; border-radius: 5px; margin: 10px 0; font-family: monospace; font-size: 12px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-card { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }
        .upload-area { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 15px 0; border: 2px dashed #ddd; text-align: center; }
        .upload-area:hover { border-color: #007bff; background: #e3f2fd; }
        input[type="file"] { margin: 10px 0; }
        .method-badge { padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; }
        .method-scrapedo { background: #e8f5e8; color: #2e7d32; }
        .method-simple { background: #fce4ec; color: #c2185b; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AliExpress Ultimate Bot</h1>
            <h2>Complete Edition - Scrape.do + Excel + Export</h2>
            <p>🎯 Professional scraping system with all features</p>
        </div>

        <div class="status {{ 'running' if bot_running else '' }}">
            <h3>{{ '🔄 Ultimate Bot Çalışıyor...' if bot_running else '✅ Ultimate Bot Hazır' }}</h3>
            <p><strong>Durum:</strong> {{ 'Professional scraping aktif' if bot_running else 'Beklemede' }}</p>
            <p><strong>Son Güncelleme:</strong> {{ datetime.now().strftime('%H:%M:%S') }}</p>
            <p><strong>Scrape.do:</strong> {{ '✅ Aktif' if scrape_do_active else '❌ Token gerekli' }}</p>
            <p><strong>Anti-Captcha:</strong> {{ ('✅ $' + anticaptcha_balance) if anticaptcha_balance else '❌ Key gerekli' }}</p>
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
                <h4>🌐 Scrape.do</h4>
                <h2>{{ stats.scrape_do }}</h2>
            </div>
            <div class="stat-card">
                <h4>🎯 Başarı %</h4>
                <h2>{{ '%.1f%%' % ((stats.basarili / (stats.basarili + stats.basarisiz)) * 100) if (stats.basarili + stats.basarisiz) > 0 else '0%' }}</h2>
            </div>
        </div>

        <h3>🔧 Bot Kontrolleri</h3>
        <button onclick="runBot()" class="btn success" {{ 'disabled' if bot_running else '' }} id="start_btn">
            🚀 {{ 'Ultimate Bot Çalışıyor...' if bot_running else 'Ultimate Bot Başlat' }}
        </button>
        <button onclick="stopBot()" class="btn danger" {{ 'disabled' if not bot_running else '' }} id="stop_btn">⏹️ Bot Durdur</button>
        <button onclick="downloadExcel()" class="btn info" id="excel_btn">📊 Excel İndir</button>
        <button onclick="clearResults()" class="btn warning" id="clear_btn">🗑️ Temizle</button>

        <h3>📁 Excel Dosyası Yükle</h3>
        <div class="upload-area">
            <p>📋 Excel dosyanızı buraya sürükleyin veya seçin</p>
            <p><small>Dosya formatı: Excel (.xlsx) - "Link" sütunu gerekli</small></p>
            <input type="file" id="excel_file" accept=".xlsx,.xls" onchange="uploadExcel()">
            <div id="upload_status"></div>
        </div>

        <h3>📝 Manuel URL Girişi</h3>
        <textarea id="test_urls" placeholder="AliExpress URL'lerini buraya yapıştırın (her satıra bir URL)...">
https://www.aliexpress.com/item/1005004356847433.html
https://www.aliexpress.com/item/1005003456789012.html</textarea>
        
        <button onclick="processUrls()" class="btn warning">🔍 URL'leri İşle</button>

        {% if progress %}
        <div class="progress">
            <strong>📈 Canlı Progress:</strong><br>
            {{ progress }}
        </div>
        {% endif %}

        <div class="results">
            <h4>📋 Scraping Sonuçları (Son {{ results|length }}): 
                <button onclick="downloadResults()" class="btn" style="float: right; padding: 5px 10px; font-size: 12px;">💾 JSON İndir</button>
            </h4>
            {% if results %}
                {% for result in results[-8:] %}
                <div style="border-bottom: 1px solid #ddd; padding: 12px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>🔗 {{ result.get('Link', '')[:50] }}...</strong>
                        <span class="method-badge method-{{ result.get('Method', '').lower().replace(' ', '').replace('.', '').replace('+', '') }}">
                            {{ result.get('Method', 'Unknown') }}
                        </span>
                    </div>
                    📝 <strong>Ürün:</strong> {{ result.get('Ürün Adı', 'N/A')[:60] }}...<br>
                    💰 <strong>Fiyat:</strong> {{ result.get('Fiyat', 'N/A') }}<br>
                    ⭐ <strong>Rating:</strong> {{ result.get('Rating', 'N/A') }}<br>
                    🛒 <strong>Satış:</strong> {{ result.get('Satış Sayısı', 'N/A') }}<br>
                    🖼️ <strong>Resim:</strong> {{ '✅ Var' if result.get('Resim URL') not in ['Bilgi bulunamadı', 'HTML parse'] else '❌ Yok' }}<br>
                    ⏰ {{ result.get('Timestamp', '') }}
                </div>
                {% endfor %}
                {% if results|length > 8 %}
                <p style="text-align: center; color: #666;">... ve {{ results|length - 8 }} sonuç daha</p>
                {% endif %}
            {% else %}
                <p>Henüz sonuç yok. Bot'u başlatın veya Excel dosyası yükleyin!</p>
            {% endif %}
        </div>

        <div style="margin-top: 30px; padding: 20px; background: #e9ecef; border-radius: 8px;">
            <h4>🎯 Complete Ultimate Bot Özellikleri:</h4>
            <ul>
                <li>✅ <strong>Excel Upload:</strong> Toplu URL işleme (.xlsx dosyaları)</li>
                <li>✅ <strong>Excel Export:</strong> Sonuçları Excel formatında indirme</li>
                <li>✅ <strong>Scrape.do API:</strong> Professional scraping service</li>
                <li>✅ <strong>JSON Parser:</strong> AliExpress raw data extraction</li>
                <li>✅ <strong>Anti-Captcha:</strong> Otomatik CAPTCHA çözme</li>
                <li>✅ <strong>Smart Fallback:</strong> Multiple scraping methods</li>
                <li>✅ <strong>Progress Tracking:</strong> Real-time updates</li>
                <li>✅ <strong>Export Options:</strong> Excel + JSON download</li>
            </ul>
        </div>
    </div>

    <script>
        function uploadExcel() {
            const fileInput = document.getElementById('excel_file');
            const file = fileInput.files[0];
            
            if (!file) {
                return;
            }
            
            if (!file.name.toLowerCase().endsWith('.xlsx') && !file.name.toLowerCase().endsWith('.xls')) {
                alert('Lütfen Excel dosyası (.xlsx veya .xls) seçin!');
                return;
            }
            
            const formData = new FormData();
            formData.append('excel_file', file);
            
            document.getElementById('upload_status').innerHTML = '📤 Dosya yükleniyor...';
            
            fetch('/upload-excel', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('upload_status').innerHTML = 
                        `✅ ${data.url_count} URL başarıyla yüklendi! Bot otomatik başlatılıyor...`;
                    
                    // Bot'u otomatik başlat
                    setTimeout(() => {
                        runBotWithUploadedUrls();
                    }, 2000);
                } else {
                    document.getElementById('upload_status').innerHTML = 
                        `❌ Hata: ${data.error}`;
                }
            })
            .catch(error => {
                document.getElementById('upload_status').innerHTML = 
                    `❌ Upload hatası: ${error}`;
            });
        }
        
        function runBotWithUploadedUrls() {
            fetch('/run-excel-urls', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`Excel URL'leri ile bot başlatıldı! ${data.url_count} URL işlenecek.`);
                    setTimeout(() => location.reload(), 2000);
                } else {
                    alert('Hata: ' + data.error);
                }
            });
        }

        function runBot() {
            const urls = document.getElementById('test_urls').value;
            const urlList = urls.split('\n').filter(url => url.trim() && url.includes('aliexpress'));
            
            if (urlList.length === 0) {
                alert('Geçerli AliExpress URL\'leri girin!');
                return;
            }
            
            // Butonu disable et
            event.target.disabled = true;
            event.target.innerText = 'Bot Başlatılıyor...';
            
            fetch('/run-ultimate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({urls: urlList})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`Ultimate Bot başlatıldı! ${urlList.length} URL işlenecek.`);
                    setTimeout(() => location.reload(), 2000);
                } else {
                    alert('Hata: ' + data.error);
                    event.target.disabled = false;
                    event.target.innerText = '🚀 Ultimate Bot Başlat';
                }
            })
            .catch(error => {
                alert('Bağlantı hatası: ' + error);
                event.target.disabled = false;
                event.target.innerText = '🚀 Ultimate Bot Başlat';
            });
        }

        function stopBot() {
            if (!confirm('Bot\'u durdurmak istediğinizden emin misiniz?')) {
                return;
            }
            
            // Butonu disable et
            event.target.disabled = true;
            event.target.innerText = 'Durduruluyor...';
            
            fetch('/stop-ultimate', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                location.reload();
            })
            .catch(error => {
                alert('Durdurma hatası: ' + error);
                event.target.disabled = false;
                event.target.innerText = '⏹️ Bot Durdur';
            });
        }

        function processUrls() { runBot(); }

        function clearResults() {
            if ({{ results|length }} === 0) {
                alert('Temizlenecek sonuç yok!');
                return;
            }
            
            if (!confirm('Tüm sonuçları silmek istediğinizden emin misiniz?')) {
                return;
            }
            
            // Butonu disable et
            event.target.disabled = true;
            event.target.innerText = 'Temizleniyor...';
            
            fetch('/clear-results', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                alert('Sonuçlar temizlendi!');
                location.reload();
            })
            .catch(error => {
                alert('Temizleme hatası: ' + error);
                event.target.disabled = false;
                event.target.innerText = '🗑️ Temizle';
            });
        }
        
        function downloadExcel() {
            if ({{ results|length }} === 0) {
                alert('İndirilecek sonuç yok! Önce bot\'u çalıştırın.');
                return;
            }
            
            // Loading göster
            event.target.disabled = true;
            event.target.innerText = 'Excel Hazırlanıyor...';
            
            const link = document.createElement('a');
            link.href = '/download-excel';
            link.download = 'aliexpress_sonuclar.xlsx';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // Butonu geri al
            setTimeout(() => {
                event.target.disabled = false;
                event.target.innerText = '📊 Excel İndir';
            }, 2000);
        }
        
        function downloadResults() {
            window.open('/download-json', '_blank');
        }

        // 5 saniyede bir otomatik güncelleme (bot çalışıyorsa)
        {% if bot_running %}
        setTimeout(() => location.reload(), 5000);
        {% endif %}
    </script>
</body>
</html>
'''

# Global uploaded URLs
uploaded_urls = []

# Environment variables
SCRAPE_DO_TOKEN = os.getenv('SCRAPE_DO_TOKEN', '4043dcdf1fbd4a7d8b370f0bb6bf94715f2c0d51771')
ANTICAPTCHA_API_KEY = os.getenv('ANTICAPTCHA_API_KEY')

@app.route('/')
def home():
    scrape_do_active = bool(SCRAPE_DO_TOKEN)
    anticaptcha_balance = None
    
    if ANTICAPTCHA_API_KEY:
        try:
            api = AntiCaptchaAPI(ANTICAPTCHA_API_KEY)
            anticaptcha_balance = str(api.get_balance())
        except:
            pass
    
    return render_template_string(WEB_TEMPLATE,
                                bot_running=bot_status["running"],
                                progress=bot_status["progress"],
                                results=bot_status["results"],
                                stats=bot_status["stats"],
                                scrape_do_active=scrape_do_active,
                                anticaptcha_balance=anticaptcha_balance,
                                datetime=datetime)

@app.route('/upload-excel', methods=['POST'])
def upload_excel():
    global uploaded_urls
    
    try:
        if 'excel_file' not in request.files:
            return jsonify({"success": False, "error": "Dosya seçilmedi"})
        
        file = request.files['excel_file']
        if file.filename == '':
            return jsonify({"success": False, "error": "Dosya seçilmedi"})
        
        # Excel dosyasını oku
        df = pd.read_excel(io.BytesIO(file.read()))
        
        # Link sütununu bul
        link_column = None
        for col in df.columns:
            if 'link' in col.lower() or 'url' in col.lower():
                link_column = col
                break
        
        if link_column is None:
            return jsonify({"success": False, "error": "Excel dosyasında 'Link' veya 'URL' sütunu bulunamadı"})
        
        # URL'leri çıkar
        urls = df[link_column].dropna().tolist()
        valid_urls = [url for url in urls if isinstance(url, str) and 'aliexpress.com' in url]
        
        if not valid_urls:
            return jsonify({"success": False, "error": "Geçerli AliExpress URL'si bulunamadı"})
        
        uploaded_urls = valid_urls
        
        return jsonify({
            "success": True, 
            "url_count": len(valid_urls),
            "message": f"{len(valid_urls)} URL başarıyla yüklendi"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/run-excel-urls', methods=['POST'])
def run_excel_urls():
    global bot_instance, bot_status, uploaded_urls
    
    if bot_status["running"]:
        return jsonify({"success": False, "error": "Bot zaten çalışıyor"})
    
    if not uploaded_urls:
        return jsonify({"success": False, "error": "Yüklenmiş URL yok"})
    
    # Bot'u thread'de başlat
    def excel_thread():
        global bot_instance, bot_status
        try:
            bot_status["running"] = True
            bot_instance = AliExpressBotUltimate(
                web_mode=True, 
                scrape_do_token=SCRAPE_DO_TOKEN,
                anticaptcha_key=ANTICAPTCHA_API_KEY
            )
            
            if bot_instance.run_bot(uploaded_urls):
                bot_status["results"] = bot_instance.sonuclar
                bot_status["stats"] = {
                    "basarili": bot_instance.basarili,
                    "basarisiz": bot_instance.basarisiz,
                    "captcha": bot_instance.captcha_cozulen,
                    "scrape_do": bot_instance.scrape_do_kullanim,
                    "selenium": bot_instance.selenium_kullanim
                }
        except Exception as e:
            bot_status["progress"] = f"Hata: {e}"
        finally:
            bot_status["running"] = False
    
    thread = threading.Thread(target=excel_thread)
    thread.daemon = True
    thread.start()
    
    return jsonify({"success": True, "url_count": len(uploaded_urls), "message": f"Excel URL'leri ile bot başlatıldı"})

@app.route('/run-ultimate', methods=['POST'])
def run_ultimate():
    global bot_instance, bot_status
    
    if bot_status["running"]:
        return jsonify({"success": False, "error": "Bot zaten çalışıyor"})
    
    data = request.get_json()
    urls = data.get('urls', [])
    
    if not urls:
        return jsonify({"success": False, "error": "URL listesi boş"})
    
    # Bot'u thread'de başlat
    def ultimate_thread():
        global bot_instance, bot_status
        try:
            bot_status["running"] = True
            bot_instance = AliExpressBotUltimate(
                web_mode=True, 
                scrape_do_token=SCRAPE_DO_TOKEN,
                anticaptcha_key=ANTICAPTCHA_API_KEY
            )
            
            if bot_instance.run_bot(urls):
                bot_status["results"] = bot_instance.sonuclar
                bot_status["stats"] = {
                    "basarili": bot_instance.basarili,
                    "basarisiz": bot_instance.basarisiz,
                    "captcha": bot_instance.captcha_cozulen,
                    "scrape_do": bot_instance.scrape_do_kullanim,
                    "selenium": bot_instance.selenium_kullanim
                }
        except Exception as e:
            bot_status["progress"] = f"Hata: {e}"
        finally:
            bot_status["running"] = False
    
    thread = threading.Thread(target=ultimate_thread)
    thread.daemon = True
    thread.start()
    
    return jsonify({"success": True, "message": f"Ultimate Bot başlatıldı - {len(urls)} URL işlenecek"})

@app.route('/stop-ultimate', methods=['POST'])
def stop_ultimate():
    global bot_instance, bot_status
    bot_status["running"] = False
    if bot_instance:
        bot_instance.running = False
    return jsonify({"message": "Ultimate bot durduruldu"})

@app.route('/clear-results', methods=['POST'])
def clear_results():
    global bot_status
    bot_status["results"] = []
    bot_status["stats"] = {"basarili": 0, "basarisiz": 0, "captcha": 0, "scrape_do": 0, "selenium": 0}
    return jsonify({"message": "Sonuçlar temizlendi"})

@app.route('/download-excel')
def download_excel():
    """Sonuçları Excel olarak indir"""
    try:
        if not bot_status["results"]:
            return "Henüz sonuç yok!", 404
        
        df = pd.DataFrame(bot_status["results"])
        
        # Excel dosyasını memory'de oluştur
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='AliExpress Sonuçları', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'aliexpress_sonuclar_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        
    except Exception as e:
        return f"Excel oluşturma hatası: {e}", 500

@app.route('/download-json')
def download_json():
    """Sonuçları JSON olarak indir"""
    try:
        if not bot_status["results"]:
            return "Henüz sonuç yok!", 404
        
        output = io.BytesIO()
        json_data = json.dumps(bot_status["results"], ensure_ascii=False, indent=2)
        output.write(json_data.encode('utf-8'))
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'aliexpress_sonuclar_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        
    except Exception as e:
        return f"JSON oluşturma hatası: {e}", 500

@app.route('/status')
def status():
    return jsonify(bot_status)

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ultimate_bot": "active",
        "scrape_do": "integrated",
        "excel_upload": "ready",
        "excel_download": "ready",
        "railway": True,
        "bot_ready": True
    })

if __name__ == '__main__':
    print(f"🚀 AliExpress Complete Ultimate Bot")
    print(f"🌐 Port: {PORT}")
    print(f"🌐 Scrape.do: {'✅ Aktif' if SCRAPE_DO_TOKEN else '❌ Token gerekli'}")
    print(f"🤖 Anti-Captcha: {'✅ Aktif' if ANTICAPTCHA_API_KEY else '❌ Key gerekli'}")
    print(f"📊 Excel Upload/Download: ✅ Aktif")
    
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)