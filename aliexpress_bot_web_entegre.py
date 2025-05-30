#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AliExpress Bot - Web Arayüzü ile Entegre
Gerçek bot + Canlı web arayüzü
"""

import pandas as pd
import time
import random
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, render_template, jsonify, request, send_file
from threading import Thread
import logging
import requests
import base64
from io import BytesIO
from dotenv import load_dotenv
import google.generativeai as genai

# .env dosyasını yükle
load_dotenv()

# Flask app oluştur
app = Flask(__name__)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

class AliExpressVeriCekmeUygulamasi:
    def __init__(self):
        self.driver = None
        self.sonuclar = []
        self.basarili = 0
        self.basarisiz = 0
        self.manuel_captcha = 0
        self.current_index = 0
        self.total_links = 0
        self.is_running = False
        self.linkler = []
        
        # Excel veri eşleştirme
        self.original_df = None  # Orijinal Excel verisi
        self.column_mapping = {}  # Sütun eşleştirmesi
        self.excel_columns = []   # Excel sütun başlıkları
        
        # AI API Keys (.env dosyasından yükle)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.selected_ai_model = 'gemini'  # Varsayılan gemini
        
        # Gemini'yi yapılandır
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            print(f"✅ Gemini API key yüklendi")
        
        if self.openai_api_key:
            print(f"✅ OpenAI API key yüklendi")
        
        # Web arayüzü için durum dosyası
        self.status_file = 'bot_status.json'
        self.results_file = 'live_results.json'
        
    def web_durumu_guncelle(self):
        """Web arayüzü için durum güncelle"""
        durum = {
            'is_running': self.is_running,
            'current_index': self.current_index,
            'total_links': self.total_links,
            'basarili': self.basarili,
            'basarisiz': self.basarisiz,
            'captcha': self.manuel_captcha,
            'progress': (self.current_index / self.total_links * 100) if self.total_links > 0 else 0
        }
        
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(durum, f, ensure_ascii=False)
    
    def resim_base64_yap(self, resim_url):
        """Resmi base64 formatına çevir"""
        try:
            if resim_url == "Resim bulunamadı" or not resim_url:
                return None
                
            response = requests.get(resim_url, timeout=10)
            if response.status_code == 200:
                image_base64 = base64.b64encode(response.content).decode('utf-8')
                return image_base64
            return None
        except Exception as e:
            print(f"Resim base64 hatası: {e}")
            return None
    
    def gemini_hs_kod_tespit(self, urun_adi, resim_url):
        """Google Gemini 2.5 Pro ile HS kodu tespit et"""
        try:
            if not self.gemini_api_key:
                return "Gemini API Key yok"
            
            print(f"🤖 Gemini 2.5 Pro ile HS kodu analiz ediliyor...")
            
            # Gemini modeli
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Prompt oluştur
            prompt = f"""
Şu ürün için doğru HS (Harmonized System) kodunu tespit et:

ÜRÜN ADI: {urun_adi}

Görevin:
1. Ürün adını ve fotoğrafını analiz et
2. Ürünün hangi kategoriye ait olduğunu belirle  
3. Türkiye Gümrük Tarife Cetveli'ne göre 8 haneli HS kodunu ver
4. Sadece rakamları ver, açıklama yapma

Cevabın sadece 8 haneli HS kodu olsun. Örnek: 85171100
"""
            
            # Eğer resim varsa ekle
            if resim_url and resim_url != "Resim bulunamadı":
                try:
                    # Resmi indir
                    response = requests.get(resim_url, timeout=10)
                    if response.status_code == 200:
                        # Gemini'ye resim ve prompt gönder
                        import PIL.Image
                        from io import BytesIO
                        
                        image = PIL.Image.open(BytesIO(response.content))
                        result = model.generate_content([prompt, image])
                    else:
                        # Sadece metin gönder
                        result = model.generate_content(prompt)
                except:
                    # Resim hatasında sadece metin
                    result = model.generate_content(prompt)
            else:
                # Sadece metin gönder
                result = model.generate_content(prompt)
            
            if result and result.text:
                hs_kod = result.text.strip()
                
                # Sadece rakamları al
                hs_kod_temiz = ''.join(filter(str.isdigit, hs_kod))
                
                if len(hs_kod_temiz) >= 6:
                    print(f"✅ Gemini HS Kodu: {hs_kod_temiz}")
                    return hs_kod_temiz[:8]  # İlk 8 hanesi al
                else:
                    print(f"⚠️ Gemini geçersiz HS: {hs_kod}")
                    return "Tespit edilemedi"
            else:
                return "Gemini cevap vermedi"
                
        except Exception as e:
            print(f"❌ Gemini HS kod hatası: {str(e)}")
            return "Gemini Hatası"
    
    def gpt4o_hs_kod_tespit(self, urun_adi, resim_url):
        try:
            if not self.openai_api_key:
                return "API Key yok"
            
            print(f"🧠 GPT-4o ile HS kodu analiz ediliyor...")
            
            # Resmi base64'e çevir
            image_base64 = self.resim_base64_yap(resim_url)
            
            # ChatGPT-4o prompt'u
            prompt = f"""
Şu ürün için doğru HS (Harmonized System) kodunu tespit et:

ÜRÜN ADI: {urun_adi}

Görevin:
1. Ürün adını ve fotoğrafını analiz et
2. Ürünün hangi kategoriye ait olduğunu belirle
3. Türkiye Gümrük Tarife Cetveli'ne göre 8 haneli HS kodunu ver
4. Sadece rakamları ver, açıklama yapma

Cevabın sadece 8 haneli HS kodu olsun. Örnek: 85171100
"""
            
            # OpenAI API isteği
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            # Mesaj içeriği
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
            
            # Eğer resim varsa ekle
            if image_base64:
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                })
            
            data = {
                "model": "gpt-4o",
                "messages": messages,
                "max_tokens": 100,
                "temperature": 0.1
            }
            
            # API çağrısı
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                hs_kod = result['choices'][0]['message']['content'].strip()
                
                # Sadece rakamları al
                hs_kod_temiz = ''.join(filter(str.isdigit, hs_kod))
                
                if len(hs_kod_temiz) >= 6:
                    print(f"✅ HS Kodu tespit edildi: {hs_kod_temiz}")
                    return hs_kod_temiz[:8]  # İlk 8 hanesi al
                else:
                    print(f"⚠️ Geçersiz HS kodu: {hs_kod}")
                    return "Tespit edilemedi"
            else:
                print(f"❌ OpenAI API hatası: {response.status_code}")
                return "API Hatası"
                
        except Exception as e:
            print(f"❌ GPT-4o HS kod hatası: {str(e)}")
            return "Hata"
    
    def excel_verisini_guncelle(self, index, sonuc):
        """Orijinal Excel verisini çekilen verilerle güncelle - Yeni sütunları referans sütunların yanına ekleyerek"""
        try:
            if self.original_df is None or not self.column_mapping:
                return
            
            # Yeni sütunları referans sütunların yanına ekle
            for field, excel_column in self.column_mapping.items():
                if excel_column and excel_column != '-- Seçiniz --':
                    # Yeni sütun adı
                    new_column_name = f"{excel_column}_Çekilen"
                    
                    # Eğer yeni sütun yoksa oluştur ve referans sütunun yanına ekle
                    if new_column_name not in self.original_df.columns:
                        # Referans sütunun pozisyonunu bul
                        ref_col_index = list(self.original_df.columns).index(excel_column)
                        
                        # Yeni sütunu referans sütunun yanına ekle
                        cols = list(self.original_df.columns)
                        cols.insert(ref_col_index + 1, new_column_name)
                        
                        # Boş sütun ekle
                        self.original_df[new_column_name] = ''
                        
                        # Sütunları yeniden sırala
                        self.original_df = self.original_df.reindex(columns=cols)
                        
                        print(f"Yeni sütun '{new_column_name}' '{excel_column}' sütununun yanına eklendi")
                    
                    # Çekilen veriyi yeni sütuna yaz
                    if field == 'urun_adi':
                        self.original_df.loc[index, new_column_name] = sonuc.get('Ürün Adı', '')
                    elif field == 'fiyat':
                        self.original_df.loc[index, new_column_name] = sonuc.get('Fiyat', '')
                    elif field == 'resim_url':
                        self.original_df.loc[index, new_column_name] = sonuc.get('Resim URL', '')
                    elif field == 'hs_kod':
                        self.original_df.loc[index, new_column_name] = sonuc.get('YZ HS Kod', '')
            
            print(f"Excel row {index} updated with adjacent columns")
            
        except Exception as e:
            print(f"Excel güncelleme hatası: {e}")
    
    def ai_hs_kod_tespit(self, urun_adi, resim_url):
        if self.selected_ai_model == 'gemini' and self.gemini_api_key:
            return self.gemini_hs_kod_tespit(urun_adi, resim_url)
        elif self.selected_ai_model == 'openai' and self.openai_api_key:
            return self.gpt4o_hs_kod_tespit(urun_adi, resim_url)
        else:
            # Mevcut olanı kullan
            if self.gemini_api_key:
                return self.gemini_hs_kod_tespit(urun_adi, resim_url)
            elif self.openai_api_key:
                return self.gpt4o_hs_kod_tespit(urun_adi, resim_url)
            else:
                return "API Key gerekli"
    
    def web_sonuc_ekle(self, sonuc):
        """Web arayüzü için sonuç ekle"""
        try:
            # Mevcut sonuçları oku
            if os.path.exists(self.results_file):
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
            else:
                results = []
            
            # Yeni sonucu ekle
            results.append({
                'id': self.current_index,
                'name': sonuc.get('Ürün Adı', 'N/A')[:80],
                'price': sonuc.get('Fiyat', 'N/A'),
                'image': sonuc.get('Resim URL', ''),
                'link': sonuc.get('Link', ''),  # Gerçek linki kullan
                'hs_kod': sonuc.get('YZ HS Kod', 'Analiz ediliyor...'),  # HS kodu ekledik
                'status': sonuc.get('Durum', 'Bilinmiyor'),
                'time': time.strftime('%H:%M:%S')
            })
            
            # Dosyaya kaydet
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Web sonuç ekleme hatası: {e}")
    
    def browser_baslat(self):
        """Chrome browser başlat"""
        try:
            # Production environment check
            is_production = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RENDER') or os.environ.get('PORT')
            
            if is_production:
                # Cloud deployment Chrome options
                chrome_options = Options()
                chrome_options.add_argument('--headless=new')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--disable-web-security')
                chrome_options.add_argument('--disable-features=VizDisplayCompositor')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-plugins')
                chrome_options.add_argument('--disable-images')
                
                # Chrome binary path for Railway/Render
                chrome_bin = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')
                chrome_options.binary_location = chrome_bin
                
                # ChromeDriver path
                driver_path = os.environ.get('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
                
                print(f"🐧 Production mode: Chrome binary = {chrome_bin}")
                print(f"🐧 Production mode: ChromeDriver = {driver_path}")
                
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Local development
                driver_path = "/opt/homebrew/bin/chromedriver"
                if not os.path.exists(driver_path):
                    driver_path = "/usr/local/bin/chromedriver"
                
                chrome_options = Options()
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--window-size=1200,800")
                
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print("✅ Chrome browser başlatıldı")
            return True
            
        except Exception as e:
            print(f"❌ Browser hatası: {e}")
            return False
    
    def captcha_bekle(self):
        """CAPTCHA manuel çözme"""
        captcha_selectors = ["iframe[src*='captcha']", ".nc_wrapper", ".geetest"]
        
        for selector in captcha_selectors:
            if self.driver.find_elements(By.CSS_SELECTOR, selector):
                print("\n🤖 CAPTCHA TESPİT EDİLDİ!")
                print("👤 Chrome'da CAPTCHA'yı çözün ve ENTER'a basın...")
                input("✅ CAPTCHA çözüldü mü? ENTER: ")
                self.manuel_captcha += 1
                self.web_durumu_guncelle()
                return True
        return False
    
    def sayfa_tamamen_yukle(self):
        """Sayfayı tamamen yükle"""
        time.sleep(5)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
    
    def tum_fiyatlari_bul(self):
        """Sayfadaki TÜM fiyat bilgilerini bul"""
        try:
            all_text_with_price = self.driver.execute_script("""
                var priceTexts = [];
                var allElements = document.querySelectorAll('*');
                
                for (var i = 0; i < allElements.length; i++) {
                    var text = allElements[i].innerText || allElements[i].textContent || '';
                    if (text && text.length < 100 && text.length > 2) {
                        if (text.includes('TL') || text.includes('₺') || text.includes('$') || 
                            text.includes('€') || text.includes('US') || text.includes('USD')) {
                            var numbers = text.match(/[0-9.,]+/g);
                            if (numbers && numbers.length > 0) {
                                priceTexts.push(text.trim());
                            }
                        }
                    }
                }
                return priceTexts;
            """)
            
            for text in all_text_with_price:
                if any(currency in text for currency in ['TL', '₺', '$', '€', 'US']):
                    if 3 <= len(text) <= 50 and any(char.isdigit() for char in text):
                        return text
            
            return "Fiyat bulunamadı"
            
        except Exception as e:
            return "Fiyat bulunamadı"
    
    def tum_resimleri_bul(self):
        """Sayfadaki TÜM ürün resimlerini bul"""
        try:
            all_images = self.driver.execute_script("""
                var imageUrls = [];
                var allImages = document.querySelectorAll('img');
                
                for (var i = 0; i < allImages.length; i++) {
                    var src = allImages[i].src;
                    if (src && src.includes('http') && 
                        (src.includes('aliexpress') || src.includes('alicdn'))) {
                        if (src.includes('.jpg') || src.includes('.png') || src.includes('.webp')) {
                            imageUrls.push(src);
                        }
                    }
                }
                return imageUrls;
            """)
            
            for img_url in all_images:
                if any(size in img_url for size in ['_640x640', '_500x500', '_400x400', '.jpg']):
                    return img_url
            
            if all_images:
                return all_images[0]
            
            return "Resim bulunamadı"
            
        except Exception as e:
            return "Resim bulunamadı"
    
    def ultra_guclu_veri_cek(self, link):
        """Ultra güçlü veri çekme"""
        try:
            print(f"\n💪 ÜRÜN {self.current_index + 1}/{self.total_links}")
            print(f"🔗 {link[:60]}...")
            
            # Sayfaya git
            self.driver.get(link)
            
            # CAPTCHA kontrolü
            if self.captcha_bekle():
                print("✅ CAPTCHA çözüldü")
            
            # Sayfayı tamamen yükle
            self.sayfa_tamamen_yukle()
            
            # Ürün adı
            urun_adi = "Bilgi bulunamadı"
            try:
                title = self.driver.title
                if title and len(title) > 10 and 'AliExpress' not in title:
                    urun_adi = title[:200]
                else:
                    h1_elements = self.driver.find_elements(By.TAG_NAME, "h1")
                    for h1 in h1_elements:
                        text = h1.text.strip()
                        if text and len(text) > 10:
                            urun_adi = text[:200]
                            break
            except:
                pass
            
            # Fiyat ve resim
            fiyat = self.tum_fiyatlari_bul()
            resim_url = self.tum_resimleri_bul()
            
            # HS Kodu AI ile tespit et
            hs_kod = "API Key gerekli"
            if self.gemini_api_key or self.openai_api_key:
                hs_kod = self.ai_hs_kod_tespit(urun_adi, resim_url)
            
            # Sonuç
            sonuc = {
                'Link': link,  # Gerçek linki kaydet
                'Ürün Adı': urun_adi,
                'Fiyat': fiyat,
                'Resim URL': resim_url,
                'YZ HS Kod': hs_kod,  # HS kodu ekledik
                'Durum': 'Başarılı'
            }
            
            print(f"✅ Ürün: {urun_adi[:40]}...")
            print(f"💰 Fiyat: {fiyat}")
            print(f"🖼️ Resim: {'✅' if resim_url != 'Resim bulunamadı' else '❌'}")
            print(f"🧠 HS Kod: {hs_kod}")
            
            return sonuc
            
        except Exception as e:
            print(f"❌ Hata: {str(e)[:50]}")
            return {
                'Link': link,
                'Ürün Adı': 'Hata',
                'Fiyat': 'Hata',
                'Resim URL': 'Hata',
                'YZ HS Kod': 'Hata',
                'Durum': f'Hata: {str(e)[:30]}'
            }
    
    def bot_calistir(self):
        """Ana bot fonksiyonu"""
        try:
            print("💪 AliExpress Veri Çekme Uygulaması başlıyor!")
            
            if not self.browser_baslat():
                return
            
            # Her ürün için işlem
            for i, link in enumerate(self.linkler):
                if not self.is_running:
                    break
                    
                self.current_index = i + 1
                
                # Ürün bilgilerini çek
                sonuc = self.ultra_guclu_veri_cek(link)
                
                if sonuc and sonuc['Durum'] == 'Başarılı':
                    self.sonuclar.append(sonuc)
                    self.basarili += 1
                    
                    # Orijinal Excel'i güncelle
                    self.excel_verisini_guncelle(i, sonuc)
                else:
                    self.basarisiz += 1
                
                # Web arayüzüne gönder
                self.web_sonuc_ekle(sonuc)
                self.web_durumu_guncelle()
                
                # Bekleme
                time.sleep(random.uniform(4, 8))
            
            # Bitirme
            self.is_running = False
            
            # Final kayıt
            df_final = pd.DataFrame(self.sonuclar)
            df_final.to_excel('sonuclar_web_entegre.xlsx', index=False)
            
            print(f"\n🏁 İŞLEM BİTTİ!")
            print(f"✅ Başarılı: {self.basarili}")
            print(f"❌ Başarısız: {self.basarisiz}")
            print(f"💾 Excel: sonuclar_web_entegre.xlsx")
            
            self.web_durumu_guncelle()
            
        except Exception as e:
            print(f"❌ Bot hatası: {e}")
            self.is_running = False
            self.web_durumu_guncelle()
        finally:
            if self.driver:
                self.driver.quit()

# Global veri çekme uygulaması instance
uygulama = AliExpressVeriCekmeUygulamasi()

# Flask routes
@app.route('/')
def index():
    return render_template('bot_arayuz.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print("Upload request received")
        
        # Check if file exists in request
        if 'file' not in request.files:
            print("No file in request")
            return jsonify({
                'success': False,
                'message': 'Dosya seçilmedi'
            })
        
        file = request.files['file']
        print(f"File received: {file.filename}")
        
        # Check if file is selected
        if file.filename == '':
            print("Empty filename")
            return jsonify({
                'success': False,
                'message': 'Dosya seçilmedi'
            })
        
        # Check file extension
        if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            print(f"Invalid file type: {file.filename}")
            return jsonify({
                'success': False,
                'message': 'Geçersiz dosya formatı. Sadece .xlsx ve .xls desteklenir'
            })
        
        # Save file temporarily
        temp_path = f"temp_{file.filename}"
        file.save(temp_path)
        print(f"File saved to: {temp_path}")
        
        # Read Excel file
        df = pd.read_excel(temp_path)
        print(f"Excel read successfully. Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Orijinal Excel verisini sakla
        uygulama.original_df = df.copy()
        uygulama.excel_columns = df.columns.tolist()
        
        # Check if 'Link' column exists
        link_column = None
        if 'Link' in df.columns:
            link_column = 'Link'
        else:
            # Try alternative column names
            link_columns = [col for col in df.columns if 'link' in col.lower() or 'url' in col.lower()]
            if link_columns:
                link_column = link_columns[0]
                print(f"Found link column: '{link_column}'")
            else:
                os.remove(temp_path)
                return jsonify({
                    'success': False,
                    'message': f"'Link' sütunu bulunamadı. Mevcut sütunlar: {', '.join(df.columns)}",
                    'columns': df.columns.tolist()
                })
        
        # Get links
        uygulama.linkler = df[link_column].dropna().tolist()
        uygulama.total_links = len(uygulama.linkler)
        print(f"Links extracted: {uygulama.total_links}")
        
        # Clean up temp file
        os.remove(temp_path)
        
        # Update web status
        uygulama.web_durumu_guncelle()
        
        return jsonify({
            'success': True,
            'count': len(uygulama.linkler),
            'message': f'{len(uygulama.linkler)} ürün linki yüklendi',
            'columns': uygulama.excel_columns,
            'link_column': link_column
        })
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        # Clean up temp file if exists
        temp_path = f"temp_{request.files.get('file', type('obj', (object,), {'filename': 'unknown'})).filename}"
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return jsonify({
            'success': False,
            'message': f'Dosya yükleme hatası: {str(e)}'
        })

@app.route('/start', methods=['POST'])
def start_process():
    if not uygulama.is_running and uygulama.linkler:
        uygulama.is_running = True
        uygulama.current_index = 0
        uygulama.basarili = 0
        uygulama.basarisiz = 0
        uygulama.manuel_captcha = 0
        uygulama.sonuclar = []
        
        # Önceki sonuçları temizle
        if os.path.exists(uygulama.results_file):
            os.remove(uygulama.results_file)
        
        # İşlemi ayrı thread'de çalıştır
        Thread(target=uygulama.bot_calistir, daemon=True).start()
        
        return jsonify({'success': True, 'message': 'Veri çekme işlemi başlatıldı'})
    else:
        return jsonify({'success': False, 'message': 'İşlem zaten çalışıyor veya link yok'})

@app.route('/stop', methods=['POST'])
def stop_process():
    uygulama.is_running = False
    return jsonify({'success': True, 'message': 'İşlem durduruldu'})

@app.route('/status')
def get_status():
    try:
        if os.path.exists(uygulama.status_file):
            with open(uygulama.status_file, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        else:
            return jsonify({
                'is_running': False,
                'current_index': 0,
                'total_links': 0,
                'basarili': 0,
                'basarisiz': 0,
                'captcha': 0,
                'progress': 0
            })
    except:
        return jsonify({'error': 'Status okunamadı'})

@app.route('/results')
def get_results():
    try:
        if os.path.exists(uygulama.results_file):
            with open(uygulama.results_file, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        else:
            return jsonify([])
    except:
        return jsonify([])

@app.route('/set_column_mapping', methods=['POST'])
def set_column_mapping():
    try:
        data = request.get_json()
        mapping = data.get('mapping', {})
        
        # Sütun eşleştirmesini kaydet
        uygulama.column_mapping = mapping
        print(f"Column mapping saved: {mapping}")
        
        return jsonify({
            'success': True,
            'message': 'Sütun eşleştirmesi kaydedildi'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Sütun eşleştirme hatası: {str(e)}'
        })

@app.route('/set_ai_model', methods=['POST'])
def set_ai_model():
    try:
        data = request.get_json()
        model_type = data.get('model', '').strip()  # 'gemini' veya 'openai'
        
        if not model_type or model_type not in ['gemini', 'openai']:
            return jsonify({
                'success': False,
                'message': 'Geçersiz model tipi'
            })
        
        # Model seçimini güncelle
        uygulama.selected_ai_model = model_type
        
        # Seçilen modelin API key'ini kontrol et
        if model_type == 'gemini':
            if not uygulama.gemini_api_key:
                return jsonify({
                    'success': False,
                    'message': 'Gemini API key .env dosyasında bulunamadı'
                })
            return jsonify({
                'success': True,
                'message': '🤖 Gemini 2.5 Pro aktif! HS kod analizi hazır.'
            })
            
        elif model_type == 'openai':
            if not uygulama.openai_api_key:
                return jsonify({
                    'success': False,
                    'message': 'OpenAI API key .env dosyasında bulunamadı'
                })
            return jsonify({
                'success': True,
                'message': '🧠 ChatGPT-4o aktif! HS kod analizi hazır.'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'AI model ayarlama hatası: {str(e)}'
        })

@app.route('/download')
def download_results():
    try:
        # Eğer orijinal Excel verisi varsa onu indir, yoksa çekilen verileri indir
        if uygulama.original_df is not None:
            # Orijinal Excel verisini güncellenmiş haliyle indir
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f'guncellenmis_excel_{timestamp}.xlsx'
            
            # Orijinal Excel'i kaydet
            uygulama.original_df.to_excel(filename, index=False)
            
            print(f"Güncellenmiş Excel dosyası oluşturuldu: {filename}")
            print(f"Toplam satır: {len(uygulama.original_df)}")
            print(f"Sütunlar: {uygulama.original_df.columns.tolist()}")
            
            return jsonify({
                'success': True,
                'message': f'Güncellenmiş Excel dosyası hazırlandı: {len(uygulama.original_df)} satır',
                'filename': filename,
                'count': len(uygulama.original_df),
                'type': 'updated_excel',
                'download_url': f'/download_file/{filename}'
            })
        elif uygulama.sonuclar:
            # Sadece çekilen verileri indir
            df = pd.DataFrame(uygulama.sonuclar)
            
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f'aliexpress_sonuclar_{timestamp}.xlsx'
            
            df.to_excel(filename, index=False)
            
            print(f"Sonuç Excel dosyası oluşturuldu: {filename}")
            print(f"Toplam kayıt: {len(df)}")
            print(f"Sütunlar: {df.columns.tolist()}")
            
            return jsonify({
                'success': True,
                'message': f'Excel dosyası hazırlandı: {len(uygulama.sonuclar)} kayıt',
                'filename': filename,
                'count': len(uygulama.sonuclar),
                'type': 'results_only',
                'download_url': f'/download_file/{filename}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'İndirilecek veri yok'
            })
    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'İndirme hatası: {str(e)}'
        })

@app.route('/download_file/<filename>')
def download_file(filename):
    try:
        import os
        
        # Dosya var mı kontrol et
        if not os.path.exists(filename):
            return jsonify({
                'success': False,
                'message': 'Dosya bulunamadı'
            }), 404
        
        # Dosyayı indir
        return send_file(
            filename,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        print(f"File download error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Dosya indirme hatası: {str(e)}'
        }), 500

if __name__ == "__main__":
    import socket
    
    # Port seçimi: Railway/Render için PORT env variable, local için boş port
    port = int(os.environ.get('PORT', 0))
    
    if port == 0:
        # Boş port bul (local development)
        def find_free_port():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', 0))
                s.listen(1)
                port = s.getsockname()[1]
            return port
        
        port = find_free_port()
        print(f"💻 Local development mode")
    else:
        print(f"🌍 Production mode (Railway/Render)")
    
    print("🌐 AliExpress Veri Çekme Uygulaması başlatılıyor...")
    print(f"📱 Tarayıcıda: http://localhost:{port}")
    print("📈 Veri çekme sistemi entegreli canlı arayüz!")
    print(f"🚀 Port {port} kullanılıyor")
    
    app.run(host='0.0.0.0', port=port, debug=False)
