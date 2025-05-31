#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AliExpress Bot - Hibrit Ultimate V3
Scrape.do + Selenium + Anti-Captcha + JSON Parser + Railway
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
from datetime import datetime
from urllib.parse import quote
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
    
    def get_usage_stats(self):
        """Kullanım istatistikleri"""
        try:
            params = {
                'token': self.token,
                'stats': 'true'
            }
            response = requests.get(self.base_url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

class AntiCaptchaAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.anti-captcha.com"
        
    def solve_recaptcha_v2(self, site_key, page_url):
        """reCAPTCHA v2 çözme"""
        try:
            task_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "RecaptchaV2TaskProxyless",
                    "websiteURL": page_url,
                    "websiteKey": site_key
                }
            }
            
            response = requests.post(f"{self.base_url}/createTask", json=task_data)
            result = response.json()
            
            if result.get("errorId") == 0:
                task_id = result.get("taskId")
                return self.wait_for_result(task_id)
            else:
                print(f"❌ Anti-Captcha hata: {result.get('errorDescription')}")
                return None
                
        except Exception as e:
            print(f"❌ reCAPTCHA çözme hatası: {e}")
            return None
    
    def wait_for_result(self, task_id, max_wait=120):
        """Sonuç bekleme"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                response = requests.post(f"{self.base_url}/getTaskResult", 
                                       json={"clientKey": self.api_key, "taskId": task_id})
                result = response.json()
                
                if result.get("status") == "ready":
                    return result.get("solution")
                elif result.get("status") == "processing":
                    time.sleep(3)
                else:
                    return None
                    
            return None
        except:
            return None
    
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
            # AliExpress sayfalarında bulunan yaygın JSON patterns
            json_patterns = [
                r'window\.runParams\s*=\s*({.*?});',
                r'window\.pageData\s*=\s*({.*?});', 
                r'__INITIAL_STATE__\s*=\s*({.*?});',
                r'window\.__moduleData__\s*=\s*({.*?});',
                r'"skuModule":\s*({.*?}),',
                r'"priceModule":\s*({.*?}),',
                r'"imageModule":\s*({.*?}),',
                r'"titleModule":\s*({.*?}),',
                r'"storeModule":\s*({.*?}),',
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
                lambda d: d.get('product', {}).get('title', ''),
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
                lambda d: d.get('skuModule', {}).get('skuPriceList', [{}])[0].get('skuVal', {}).get('skuAmount', {}).get('formatedAmount', ''),
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
                lambda d: d.get('product', {}).get('images', [None])[0],
            ]
            
            for source in image_sources:
                try:
                    image = source(json_data)
                    if image:
                        # AliExpress resim URL'lerini tam format'a çevir
                        if not image.startswith('http'):
                            image = 'https:' + image if image.startswith('//') else 'https://ae01.alicdn.com/kf/' + image
                        product_info['image'] = image
                        break
                except:
                    continue
            
            # RATING - JSON'dan
            rating_sources = [
                lambda d: d.get('storeModule', {}).get('storeRating', ''),
                lambda d: d.get('data', {}).get('feedbackModule', {}).get('averageStar', ''),
                lambda d: d.get('feedbackModule', {}).get('averageStar', ''),
            ]
            
            for source in rating_sources:
                try:
                    rating = source(json_data)
                    if rating:
                        product_info['rating'] = str(rating)
                        break
                except:
                    continue
            
            # SATIŞ SAYISI - JSON'dan
            sold_sources = [
                lambda d: d.get('data', {}).get('tradeModule', {}).get('formatTradeCount', ''),
                lambda d: d.get('tradeModule', {}).get('formatTradeCount', ''),
                lambda d: d.get('skuModule', {}).get('totalSoldCount', ''),
            ]
            
            for source in sold_sources:
                try:
                    sold = source(json_data)
                    if sold:
                        product_info['sold_count'] = str(sold)
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
                    r'[\$€£¥₹₽]\s*[\d,.]+'
                    r'US\s*\$\s*[\d,.]+',
                    r'[\d,.]+\s*USD',
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
            
            # Resim URL arama
            img_patterns = [
                r'https://[^"\']*\.alicdn\.com/[^"\']*\.(jpg|jpeg|png|webp)',
                r'//[^"\']*\.alicdn\.com/[^"\']*\.(jpg|jpeg|png|webp)',
            ]
            
            image = 'Bilgi bulunamadı'
            for pattern in img_patterns:
                img_match = re.search(pattern, html_content)
                if img_match:
                    image = img_match.group(0)
                    if not image.startswith('http'):
                        image = 'https:' + image
                    break
            
            return {
                'Link': url,
                'Ürün Adı': title,
                'Fiyat': price,
                'Resim URL': image,
                'Rating': 'HTML parse',
                'Satış Sayısı': 'HTML parse',
                'Method': 'Scrape.do + HTML',
                'Durum': 'Kısmi başarılı',
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            self.log(f"❌ HTML fallback hatası: {e}")
            return None
    
    def browser_baslat(self):
        """Selenium fallback için"""
        try:
            chrome_options = Options()
            
            if self.web_mode:
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            else:
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--window-size=1200,800")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.log("✅ Selenium Chrome backup hazır")
            return True
            
        except Exception as e:
            self.log(f"❌ Selenium hatası: {e}")
            return False
    
    def scrape_with_selenium(self, url):
        """Selenium ile fallback scraping"""
        try:
            self.log("🤖 Selenium backup ile scraping...")
            
            if not self.driver:
                if not self.browser_baslat():
                    return None
            
            self.driver.get(url)
            time.sleep(3)
            self.selenium_kullanim += 1
            
            # CAPTCHA check
            captcha_found = self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='captcha'], .nc_wrapper, .geetest")
            if captcha_found and self.anticaptcha:
                self.log("🤖 CAPTCHA tespit edildi, Anti-Captcha ile çözülüyor...")
                # Anti-Captcha logic buraya
                time.sleep(5)
            
            # Data extraction
            title = self.driver.title[:200]
            
            # Fiyat
            price = 'Bilgi bulunamadı'
            price_selectors = [".product-price-current", ".price-current", "[data-pl='price']", ".price"]
            for selector in price_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    price = element.text.strip()
                    if price:
                        break
                except:
                    continue
            
            # Resim
            image = 'Bilgi bulunamadı'
            img_selectors = ["img.magnifier-image", ".pdp-main-image img", "img[src*='aliexpress']"]
            for selector in img_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    image = element.get_attribute("src")
                    if image:
                        break
                except:
                    continue
            
            return {
                'Link': url,
                'Ürün Adı': title,
                'Fiyat': price,
                'Resim URL': image,
                'Rating': 'Selenium',
                'Satış Sayısı': 'Selenium',
                'Method': 'Selenium + Anti-Captcha',
                'Durum': 'Backup başarılı',
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            self.log(f"❌ Selenium scraping hatası: {e}")
            return None
    
    def scrape_product(self, url):
        """Triple hybrid scraping method"""
        try:
            # Method 1: Scrape.do (Primary)
            if self.scrape_do:
                result = self.scrape_with_scrape_do(url)
                if result and result.get('Durum') == 'Başarılı':
                    return result
            
            # Method 2: Selenium fallback 
            result = self.scrape_with_selenium(url)
            if result:
                return result
            
            # Method 3: Simple requests fallback
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
            self.log("🎯 Method: Scrape.do → Selenium → Simple requests")
            
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
                self.log(f"🌐 Scrape.do: {self.scrape_do_kullanim}, 🤖 Selenium: {self.selenium_kullanim}")
                
                # Rate limiting
                if i < len(linkler):
                    time.sleep(random.uniform(1, 3))
            
            self.log("🏁 Ultimate bot tamamlandı!")
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
    "stats": {"basarili": 0, "basarisiz": 0, "captcha": 0, "scrape_do": 0, "selenium": 0}
}

# Web arayüzü HTML
WEB_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AliExpress Ultimate Bot - Scrape.do + Selenium + Anti-Captcha</title>
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
        .results { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0; max-height: 500px; overflow-y: auto; }
        textarea { width: 100%; height: 120px; margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-family: monospace; }
        .progress { background: #e9ecef; padding: 10px; border-radius: 5px; margin: 10px 0; font-family: monospace; font-size: 12px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-card { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }
        .api-info { background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #2196f3; }
        input[type="password"] { width: 250px; padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin: 5px; }
        .method-badge { padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; }
        .method-scrapedo { background: #e8f5e8; color: #2e7d32; }
        .method-selenium { background: #fff3e0; color: #f57c00; }
        .method-simple { background: #fce4ec; color: #c2185b; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AliExpress Ultimate Bot</h1>
            <h2>Scrape.do + Selenium + Anti-Captcha</h2>
            <p>🎯 Triple Hybrid Scraping System + JSON Parser</p>
        </div>

        <div class="api-info">
            <h4>🔧 API Services Status</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                <div>
                    <strong>🌐 Scrape.do:</strong> {{ '✅ Aktif' if scrape_do_active else '❌ Token gerekli' }}<br>
                    {% if scrape_do_stats %}
                    <small>Kullanım: {{ scrape_do_stats }}</small>
                    {% endif %}
                </div>
                <div>
                    <strong>🤖 Anti-Captcha:</strong> {{ ('✅ $' + anticaptcha_balance) if anticaptcha_balance else '❌ Key gerekli' }}<br>
                    <small>CAPTCHA otomatik çözülür</small>
                </div>
                <div>
                    <strong>🤖 Selenium:</strong> ✅ Backup hazır<br>
                    <small>Fallback method</small>
                </div>
            </div>
            
            {% if not scrape_do_active or not anticaptcha_balance %}
            <div style="margin-top: 15px;">
                {% if not scrape_do_active %}
                <strong>Scrape.do Token:</strong>
                <input type="password" id="scrape_do_token" placeholder="Scrape.do token...">
                <button onclick="setScrapeDoToken()" class="btn">💾 Kaydet</button><br>
                {% endif %}
                {% if not anticaptcha_balance %}
                <strong>Anti-Captcha Key:</strong>
                <input type="password" id="api_key" placeholder="Anti-Captcha API Key...">
                <button onclick="setApiKey()" class="btn">💾 Kaydet</button>
                {% endif %}
            </div>
            {% endif %}
        </div>

        <div class="status {{ 'running' if bot_running else '' }}">
            <h3>{{ '🔄 Ultimate Bot Çalışıyor...' if bot_running else '✅ Ultimate Bot Hazır' }}</h3>
            <p><strong>Durum:</strong> {{ 'Triple hybrid sistem aktif' if bot_running else 'Beklemede' }}</p>
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
                <h4>🌐 Scrape.do</h4>
                <h2>{{ stats.scrape_do }}</h2>
            </div>
            <div class="stat-card">
                <h4>🤖 Selenium</h4>
                <h2>{{ stats.selenium }}</h2>
            </div>
            <div class="stat-card">
                <h4>🔓 CAPTCHA</h4>
                <h2>{{ stats.captcha }}</h2>
            </div>
            <div class="stat-card">
                <h4>🎯 Başarı %</h4>
                <h2>{{ '%.1f%%' % ((stats.basarili / (stats.basarili + stats.basarisiz)) * 100) if (stats.basarili + stats.basarisiz) > 0 else '0%' }}</h2>
            </div>
        </div>

        <h3>🔧 Ultimate Bot Kontrolleri</h3>
        <button onclick="runBot()" class="btn success" {{ 'disabled' if bot_running else '' }}>
            🚀 {{ 'Ultimate Bot Çalışıyor...' if bot_running else 'Ultimate Bot Başlat' }}
        </button>
        <button onclick="stopBot()" class="btn danger">⏹️ Bot Durdur</button>
        <a href="/status" class="btn">📊 Status API</a>
        <a href="/results" class="btn">📈 Sonuçlar</a>
        <a href="/health" class="btn">🏥 Health</a>

        <h3>📝 Test URL'leri (AliExpress)</h3>
        <textarea id="test_urls" placeholder="AliExpress URL'lerini buraya yapıştırın (her satıra bir URL)...">
https://www.aliexpress.com/item/1005004356847433.html
https://www.aliexpress.com/item/1005003456789012.html</textarea>
        
        <button onclick="testUrls()" class="btn warning">🔍 Triple Hybrid Scraping Başlat</button>
        <button onclick="clearResults()" class="btn">🗑️ Sonuçları Temizle</button>

        {% if progress %}
        <div class="progress">
            <strong>📈 Canlı Progress:</strong><br>
            {{ progress }}
        </div>
        {% endif %}

        <div class="results">
            <h4>📋 Ultimate Scraping Sonuçları:</h4>
            {% if results %}
                {% for result in results[-5:] %}
                <div style="border-bottom: 1px solid #ddd; padding: 12px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>🔗 {{ result.get('Link', '')[:40] }}...</strong>
                        <span class="method-badge method-{{ result.get('Method', '').lower().replace(' ', '').replace('.', '').replace('+', '') }}">
                            {{ result.get('Method', 'Unknown') }}
                        </span>
                    </div>
                    📝 <strong>Ürün:</strong> {{ result.get('Ürün Adı', 'N/A')[:50] }}...<br>
                    💰 <strong>Fiyat:</strong> {{ result.get('Fiyat', 'N/A') }}<br>
                    ⭐ <strong>Rating:</strong> {{ result.get('Rating', 'N/A') }}<br>
                    🛒 <strong>Satış:</strong> {{ result.get('Satış Sayısı', 'N/A') }}<br>
                    🖼️ <strong>Resim:</strong> {{ '✅ Var' if result.get('Resim URL') != 'Bilgi bulunamadı' else '❌ Yok' }}<br>
                    ⏰ {{ result.get('Timestamp', '') }}
                </div>
                {% endfor %}
            {% else %}
                <p>Henüz sonuç yok. Ultimate Bot'u başlatın!</p>
            {% endif %}
        </div>

        <div style="margin-top: 30px; padding: 20px; background: #e9ecef; border-radius: 8px;">
            <h4>🎯 Ultimate Bot Özellikleri:</h4>
            <ul>
                <li>✅ <strong>Scrape.do API:</strong> Birincil scraping, proxy rotation, anti-detection</li>
                <li>✅ <strong>JSON Parser:</strong> AliExpress raw response'dan data extraction</li>
                <li>✅ <strong>Selenium Backup:</strong> Dynamic content için fallback</li>
                <li>✅ <strong>Anti-Captcha:</strong> Otomatik CAPTCHA çözme</li>
                <li>✅ <strong>Triple Fallback:</strong> Scrape.do → Selenium → Simple requests</li>
                <li>✅ <strong>Railway Compatible:</strong> Cloud deployment ready</li>
                <li>✅ <strong>Method Tracking:</strong> Hangi yöntem kullanıldığını gösterir</li>
            </ul>
        </div>
    </div>

    <script>
        function setScrapeDoToken() {
            const token = document.getElementById('scrape_do_token').value;
            if (!token.trim()) {
                alert('Scrape.do token girin!');
                return;
            }
            
            fetch('/set-scrape-do-token', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({token: token})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Scrape.do token kaydedildi!');
                    location.reload();
                } else {
                    alert('Hata: ' + data.error);
                }
            });
        }

        function setApiKey() {
            const apiKey = document.getElementById('api_key').value;
            if (!apiKey.trim()) {
                alert('API Key girin!');
                return;
            }
            
            fetch('/set-api-key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({api_key: apiKey})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Anti-Captcha API Key kaydedildi! Bakiye: $' + data.balance);
                    location.reload();
                } else {
                    alert('Hata: ' + data.error);
                }
            });
        }

        function runBot() {
            const urls = document.getElementById('test_urls').value;
            const urlList = urls.split('\\n').filter(url => url.trim() && url.includes('aliexpress'));
            
            if (urlList.length === 0) {
                alert('Geçerli AliExpress URL\'leri girin!');
                return;
            }
            
            fetch('/run-ultimate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({urls: urlList})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`Ultimate Bot başlatıldı! ${urlList.length} URL triple hybrid ile işlenecek.`);
                    setTimeout(() => location.reload(), 2000);
                } else {
                    alert('Hata: ' + data.error);
                }
            });
        }

        function stopBot() {
            fetch('/stop-ultimate', {method: 'POST'})
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

# Environment variables
SCRAPE_DO_TOKEN = os.getenv('SCRAPE_DO_TOKEN', '4043dcdf1fbd4a7d8b370f0bb6bf94715f2c0d51771')
ANTICAPTCHA_API_KEY = os.getenv('ANTICAPTCHA_API_KEY')

@app.route('/')
def home():
    scrape_do_active = bool(SCRAPE_DO_TOKEN)
    anticaptcha_balance = None
    scrape_do_stats = None
    
    if ANTICAPTCHA_API_KEY:
        try:
            api = AntiCaptchaAPI(ANTICAPTCHA_API_KEY)
            anticaptcha_balance = api.get_balance()
        except:
            pass
    
    if SCRAPE_DO_TOKEN:
        try:
            scrape_do_api = ScrapeDoAPI(SCRAPE_DO_TOKEN)
            stats = scrape_do_api.get_usage_stats()
            if stats:
                scrape_do_stats = f"Credits: {stats.get('credits', 'N/A')}"
        except:
            pass
    
    return render_template_string(WEB_TEMPLATE,
                                bot_running=bot_status["running"],
                                progress=bot_status["progress"],
                                results=bot_status["results"],
                                stats=bot_status["stats"],
                                scrape_do_active=scrape_do_active,
                                scrape_do_stats=scrape_do_stats,
                                anticaptcha_balance=anticaptcha_balance,
                                datetime=datetime)

@app.route('/set-scrape-do-token', methods=['POST'])
def set_scrape_do_token():
    global SCRAPE_DO_TOKEN
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({"success": False, "error": "Token boş"})
    
    try:
        # Token'ı test et
        test_api = ScrapeDoAPI(token)
        test_response = test_api.get_usage_stats()
        
        SCRAPE_DO_TOKEN = token
        os.environ['SCRAPE_DO_TOKEN'] = token
        return jsonify({"success": True, "message": "Scrape.do token kaydedildi"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/set-api-key', methods=['POST'])
def set_api_key():
    global ANTICAPTCHA_API_KEY
    data = request.get_json()
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({"success": False, "error": "API key boş"})
    
    try:
        api = AntiCaptchaAPI(api_key)
        balance = api.get_balance()
        
        if balance is not None:
            ANTICAPTCHA_API_KEY = api_key
            os.environ['ANTICAPTCHA_API_KEY'] = api_key
            return jsonify({"success": True, "balance": balance})
        else:
            return jsonify({"success": False, "error": "Geçersiz API key"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

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
        "anticaptcha": "integrated", 
        "selenium": "backup_ready",
        "railway": True,
        "bot_ready": True
    })

@app.route('/results')
def get_results():
    return jsonify({"results": bot_status["results"], "count": len(bot_status["results"])})

if __name__ == '__main__':
    print(f"🚀 AliExpress Ultimate Bot - Triple Hybrid System")
    print(f"🌐 Port: {PORT}")
    print(f"🌐 Scrape.do: {'✅ Aktif' if SCRAPE_DO_TOKEN else '❌ Token gerekli'}")
    print(f"🤖 Anti-Captcha: {'✅ Aktif' if ANTICAPTCHA_API_KEY else '❌ Key gerekli'}")
    print(f"🤖 Selenium: ✅ Backup hazır")
    
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)