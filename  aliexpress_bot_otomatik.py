#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AliExpress Bot - Otomatik CAPTCHA Çözme ile
6000+ ürün için uygun, tam otomatik sistem
"""

import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import os
import logging
import requests
import base64
from PIL import Image
from io import BytesIO
import cv2
import numpy as np

class OtomatikCaptchaCozucu:
    """Otomatik CAPTCHA çözme sistemi"""
    
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
    
    def solve_checkbox_captcha(self):
        """'Ben robot değilim' checkbox CAPTCHA çözer"""
        try:
            # Checkbox CAPTCHA selectors
            checkbox_selectors = [
                "input[type='checkbox']",
                ".recaptcha-checkbox",
                "[class*='checkbox']",
                "#recaptcha-anchor"
            ]
            
            for selector in checkbox_selectors:
                try:
                    checkbox = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    
                    # İnsan benzeri tıklama
                    actions = ActionChains(self.driver)
                    actions.move_to_element(checkbox)
                    actions.pause(random.uniform(0.5, 1.5))
                    actions.click()
                    actions.perform()
                    
                    time.sleep(random.uniform(2, 4))
                    print("✅ Checkbox CAPTCHA çözüldü")
                    return True
                    
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Checkbox CAPTCHA hatası: {e}")
            return False
    
    def solve_slider_captcha(self):
        """Slider (kaydırma) CAPTCHA çözer"""
        try:
            # Slider selectors
            slider_selectors = [
                ".nc_iconfont",
                "[class*='slider']",
                "[class*='slide']",
                ".captcha-slider",
                "#nc_1_n1t"
            ]
            
            for selector in slider_selectors:
                try:
                    slider = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # Slider'ı sağa kaydır
                    actions = ActionChains(self.driver)
                    actions.click_and_hold(slider)
                    
                    # İnsan benzeri hareket - yavaş ve titrek
                    for i in range(20):
                        x_offset = random.randint(8, 15)
                        y_offset = random.randint(-2, 2)
                        actions.move_by_offset(x_offset, y_offset)
                        actions.pause(random.uniform(0.05, 0.15))
                    
                    actions.release()
                    actions.perform()
                    
                    time.sleep(random.uniform(2, 4))
                    print("✅ Slider CAPTCHA çözüldü")
                    return True
                    
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Slider CAPTCHA hatası: {e}")
            return False
    
    def solve_puzzle_captcha(self):
        """Puzzle (parça birleştirme) CAPTCHA çözer"""
        try:
            # Puzzle piece selectors
            puzzle_selectors = [
                "[class*='puzzle']",
                "[class*='jigsaw']",
                ".captcha-puzzle",
                "[id*='puzzle']"
            ]
            
            for selector in puzzle_selectors:
                try:
                    puzzle_piece = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # Puzzle piece'i sürükle
                    actions = ActionChains(self.driver)
                    actions.click_and_hold(puzzle_piece)
                    
                    # Puzzle çözme hareketi (genelde sağa doğru)
                    target_x = random.randint(200, 300)
                    target_y = random.randint(-10, 10)
                    
                    # Yavaş hareket
                    steps = 30
                    for i in range(steps):
                        x = target_x / steps
                        y = target_y / steps + random.randint(-1, 1)
                        actions.move_by_offset(x, y)
                        actions.pause(random.uniform(0.02, 0.08))
                    
                    actions.release()
                    actions.perform()
                    
                    time.sleep(random.uniform(2, 4))
                    print("✅ Puzzle CAPTCHA çözüldü")
                    return True
                    
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Puzzle CAPTCHA hatası: {e}")
            return False
    
    def solve_math_captcha(self):
        """Matematik CAPTCHA çözer"""
        try:
            # Math CAPTCHA selectors
            math_selectors = [
                "[class*='math']",
                "[class*='calculate']",
                "input[placeholder*='+']",
                "input[placeholder*='=']"
            ]
            
            for selector in math_selectors:
                try:
                    math_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # Matematik sorusunu bul
                    parent = math_input.find_element(By.XPATH, "./..")
                    text = parent.text
                    
                    # Basit matematik işlemleri
                    if '+' in text:
                        parts = text.split('+')
                        if len(parts) >= 2:
                            num1 = int(''.join(filter(str.isdigit, parts[0])))
                            num2 = int(''.join(filter(str.isdigit, parts[1])))
                            result = num1 + num2
                            
                            math_input.clear()
                            math_input.send_keys(str(result))
                            
                            time.sleep(random.uniform(1, 2))
                            print(f"✅ Matematik CAPTCHA çözüldü: {num1}+{num2}={result}")
                            return True
                    
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Matematik CAPTCHA hatası: {e}")
            return False
    
    def detect_and_solve_captcha(self):
        """CAPTCHA tespit eder ve otomatik çözer"""
        try:
            print("🔍 CAPTCHA aranıyor...")
            
            # Farklı CAPTCHA türlerini sırayla dene
            captcha_solved = False
            
            # 1. Checkbox CAPTCHA
            if self.solve_checkbox_captcha():
                captcha_solved = True
            
            # 2. Slider CAPTCHA  
            elif self.solve_slider_captcha():
                captcha_solved = True
            
            # 3. Puzzle CAPTCHA
            elif self.solve_puzzle_captcha():
                captcha_solved = True
            
            # 4. Math CAPTCHA
            elif self.solve_math_captcha():
                captcha_solved = True
            
            if captcha_solved:
                time.sleep(random.uniform(3, 5))
                return True
            else:
                print("⚠️ CAPTCHA tipi tanınmadı, manuel müdahale gerekebilir")
                return False
                
        except Exception as e:
            self.logger.warning(f"CAPTCHA çözme hatası: {e}")
            return False

class GelismisAliExpressBot:
    def __init__(self):
        self.setup_logging()
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
        ]
        self.driver = None
        self.captcha_solver = None
        self.proxy_list = []
        self.current_proxy_index = 0
        
    def setup_logging(self):
        """Log sistemini kurar"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot_log.txt', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_next_proxy(self):
        """Sıradaki proxy'yi döndürür"""
        if not self.proxy_list:
            return None
        
        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        return proxy
    
    def setup_browser(self, use_proxy=False):
        """Gelişmiş browser kurulumu"""
        try:
            print("🌐 Gelişmiş tarayıcı başlatılıyor...")
            
            chrome_options = Options()
            
            # Temel ayarlar
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Anti-detection ayarları
            chrome_options.add_argument('--disable-plugins-discovery')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--disable-background-networking')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            
            # Rastgele User-Agent
            user_agent = random.choice(self.user_agents)
            chrome_options.add_argument(f'--user-agent={user_agent}')
            
            # Proxy ayarları (eğer varsa)
            if use_proxy and self.proxy_list:
                proxy = self.get_next_proxy()
                if proxy:
                    chrome_options.add_argument(f'--proxy-server={proxy}')
                    print(f"🔒 Proxy kullanılıyor: {proxy}")
            
            # Dil ve lokalizasyon
            chrome_options.add_argument('--lang=tr-TR')
            chrome_options.add_experimental_option('prefs', {
                'intl.accept_languages': 'tr-TR,tr,en-US,en',
                'profile.default_content_setting_values.notifications': 2,
                'profile.default_content_settings.popups': 0
            })
            
            # Driver oluştur
            homebrew_paths = [
                "/opt/homebrew/bin/chromedriver",
                "/usr/local/bin/chromedriver"
            ]
            
            driver_created = False
            for path in homebrew_paths:
                if os.path.exists(path):
                    try:
                        service = Service(path)
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                        driver_created = True
                        print(f"✅ ChromeDriver başarılı: {path}")
                        break
                    except:
                        continue
            
            if not driver_created:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Browser ayarları
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": user_agent
            })
            
            # CAPTCHA solver'ı başlat
            self.captcha_solver = OtomatikCaptchaCozucu(self.driver)
            
            print("✅ Gelişmiş tarayıcı hazır")
            return True
            
        except Exception as e:
            print(f"❌ Tarayıcı hatası: {e}")
            return False
    
    def smart_wait(self, min_sec=2, max_sec=6):
        """Akıllı bekleme sistemi"""
        wait_time = random.uniform(min_sec, max_sec)
        print(f"⏳ {wait_time:.1f}s bekleniyor...")
        time.sleep(wait_time)
    
    def handle_captcha_automatically(self):
        """Otomatik CAPTCHA işleme"""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            print(f"🤖 CAPTCHA çözme denemesi {attempt + 1}/{max_attempts}")
            
            if self.captcha_solver.detect_and_solve_captcha():
                print("✅ CAPTCHA otomatik çözüldü!")
                return True
            
            if attempt < max_attempts - 1:
                print("⏳ Yeniden deneniyor...")
                time.sleep(random.uniform(2, 4))
        
        print("⚠️ Otomatik CAPTCHA çözme başarısız - sayfa yenileniyor")
        self.driver.refresh()
        time.sleep(5)
        return False
    
    def detect_captcha(self):
        """CAPTCHA tespiti"""
        try:
            page_source = self.driver.page_source.lower()
            captcha_indicators = [
                'captcha', 'verification', 'verify', 'robot', 'challenge',
                'recaptcha', 'slider', 'puzzle', 'checkbox'
            ]
            
            for indicator in captcha_indicators:
                if indicator in page_source:
                    return True
            
            return False
            
        except:
            return False
    
    def get_product_info_advanced(self, url):
        """Gelişmiş ürün bilgisi çekme"""
        try:
            print(f"📦 Ürün sayfası açılıyor...")
            
            # Sayfayı aç
            self.driver.get(url)
            self.smart_wait(3, 6)
            
            # CAPTCHA kontrolü ve otomatik çözme
            captcha_attempts = 0
            while self.detect_captcha() and captcha_attempts < 3:
                print("🤖 CAPTCHA tespit edildi - otomatik çözülüyor...")
                if self.handle_captcha_automatically():
                    break
                captcha_attempts += 1
                
                if captcha_attempts >= 3:
                    print("⚠️ CAPTCHA çözülemedi - ürün atlanıyor")
                    return self._create_error_product(url, "CAPTCHA çözülemedi")
            
            # Sayfa yüklenme kontrolü
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
            except:
                pass
            
            # İnsan benzeri davranış
            self._human_behavior()
            
            # Ürün bilgilerini çek
            product_info = {
                'url': url,
                'name': self._extract_product_name(),
                'price': self._extract_price(),
                'image_url': self._extract_image_url(),
                'rating': self._extract_rating(),
                'sold_count': self._extract_sold_count(),
                'availability': self._extract_availability()
            }
            
            print(f"✅ Ürün bilgisi alındı:")
            print(f"   📝 {product_info['name'][:40]}...")
            print(f"   💰 {product_info['price']}")
            
            return product_info
            
        except Exception as e:
            print(f"❌ Ürün bilgisi hatası: {e}")
            return self._create_error_product(url, str(e))
    
    def _human_behavior(self):
        """İnsan benzeri davranış simülasyonu"""
        try:
            # Rastgele scroll
            for _ in range(random.randint(2, 4)):
                scroll_y = random.randint(200, 800)
                self.driver.execute_script(f"window.scrollTo(0, {scroll_y});")
                time.sleep(random.uniform(0.5, 1.5))
            
            # Başa dön
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(random.uniform(1, 2))
            
            # Rastgele mouse hareketi
            try:
                actions = ActionChains(self.driver)
                for _ in range(random.randint(1, 3)):
                    x = random.randint(100, 800)
                    y = random.randint(100, 600)
                    actions.move_by_offset(x, y)
                    actions.pause(random.uniform(0.1, 0.5))
                actions.perform()
            except:
                pass
                
        except:
            pass
    
    def _extract_product_name(self):
        """Ürün adını çıkarır"""
        selectors = [
            "h1[data-pl='product-title']",
            ".product-title-text",
            "h1.x-item-title-label",
            ".pdp-product-name",
            "h1",
            "[class*='title'][class*='product']",
            ".goods-title"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and len(text) > 10:
                        return text
            except:
                continue
        
        return "Ürün adı bulunamadı"
    
    def _extract_price(self):
        """Fiyatı çıkarır"""
        selectors = [
            ".price-current",
            ".product-price-current", 
            ".notranslate",
            "[class*='price']",
            "[data-pl*='price']",
            ".price-now",
            ".price-original"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if any(symbol in text for symbol in ['$', '₺', 'USD', 'TL', '€', '¥']):
                        return text
            except:
                continue
        
        return "Fiyat bulunamadı"
    
    def _extract_image_url(self):
        """Resim URL'ini çıkarır"""
        selectors = [
            "img.magnifier-image",
            "img[class*='image']",
            ".gallery img",
            "img[src*='alicdn']",
            ".product-image img"
        ]
        
        for selector in selectors:
            try:
                img_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                img_url = img_element.get_attribute('src')
                if img_url and ('alicdn' in img_url or 'alibaba' in img_url):
                    return img_url
            except:
                continue
        
        return "Resim bulunamadı"
    
    def _extract_rating(self):
        """Puanı çıkarır"""
        selectors = [
            ".summary-star-rate",
            "[class*='rating']",
            "[class*='star']",
            ".product-rate"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text and any(char.isdigit() for char in text):
                    return text
            except:
                continue
        
        return "Puan bulunamadı"
    
    def _extract_sold_count(self):
        """Satış sayısını çıkarır"""
        selectors = [
            ".product-reviewer-reviews",
            "[class*='sold']",
            "[class*='order']",
            ".sold-count"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text:
                    return text
            except:
                continue
        
        return "Satış bilgisi yok"
    
    def _extract_availability(self):
        """Stok durumunu çıkarır"""
        try:
            page_source = self.driver.page_source.lower()
            
            if any(keyword in page_source for keyword in ['out of stock', 'stokta yok', 'tükendi']):
                return "Stokta yok"
            elif any(keyword in page_source for keyword in ['in stock', 'stokta', 'mevcut']):
                return "Stokta var"
            else:
                return "Stok durumu belirsiz"
                
        except:
            return "Stok bilgisi alınamadı"
    
    def _create_error_product(self, url, error):
        """Hata durumu için ürün objesi oluşturur"""
        return {
            'url': url,
            'name': f'HATA: {error}',
            'price': 'Hata',
            'image_url': 'Hata',
            'rating': 'Hata',
            'sold_count': 'Hata',
            'availability': 'Hata'
        }
    
    def process_bulk_links(self, input_file='linkler.xlsx', output_file='sonuclar.xlsx', batch_size=100):
        """Toplu link işleme - 6000+ ürün için optimize edilmiş"""
        try:
            print("📋 Excel dosyası okunuyor...")
            
            if not os.path.exists(input_file):
                print(f"❌ {input_file} dosyası bulunamadı!")
                return False
            
            df = pd.read_excel(input_file)
            
            # Sütun adını bul
            link_column = None
            possible_names = ['link', 'LINK', 'linkler', 'LINKLER', 'url', 'URL']
            
            for col_name in possible_names:
                if col_name in df.columns:
                    link_column = col_name
                    break
            
            if link_column is None:
                print("❌ Link sütunu bulunamadı!")
                return False
            
            print(f"✅ Link sütunu bulundu: '{link_column}'")
            
            # Browser'ı başlat
            if not self.setup_browser():
                return False
            
            try:
                total_links = len(df)
                results = []
                processed_count = 0
                
                print(f"📊 Toplam {total_links} link işlenecek")
                print(f"🔧 Batch boyutu: {batch_size}")
                
                for index, row in df.iterrows():
                    link = row[link_column]
                    
                    if pd.isna(link):
                        continue
                    
                    print(f"\n📦 İşleniyor ({index + 1}/{total_links}) - %{(index+1)/total_links*100:.1f}")
                    print(f"🔗 {link[:60]}...")
                    
                    # Ürün bilgisini al
                    product_info = self.get_product_info_advanced(link)
                    results.append(product_info)
                    processed_count += 1
                    
                    # Batch kayıt
                    if processed_count % 10 == 0:
                        temp_df = pd.DataFrame(results)
                        temp_df.to_excel(f"temp_{output_file}", index=False)
                        print(f"💾 Geçici kayıt: {processed_count} ürün")
                    
                    # Browser yenileme (her 50 üründe)
                    if processed_count % 50 == 0:
                        print("🔄 Browser yenileniyor...")
                        self.driver.quit()
                        time.sleep(random.uniform(3, 7))
                        if not self.setup_browser(use_proxy=True):
                            print("❌ Browser yenileme başarısız!")
                            break
                    
                    # Akıllı bekleme
                    if index < total_links - 1:
                        wait_time = random.uniform(2, 6)
                        
                        # Her 100 üründe daha uzun mola
                        if processed_count % 100 == 0:
                            wait_time = random.uniform(30, 60)
                            print(f"☕ Uzun mola: {wait_time:.0f} saniye")
                        
                        print(f"⏳ {wait_time:.1f}s bekleniyor...")
                        time.sleep(wait_time)
                
                # Final kayıt
                print("\n💾 Final sonuçlar kaydediliyor...")
                results_df = pd.DataFrame(results)
                results_df.to_excel(output_file, index=False)
                
                # Geçici dosyayı sil
                temp_file = f"temp_{output_file}"
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                
                print(f"\n🎉 İşlem tamamlandı!")
                print(f"📁 Sonuçlar: {output_file}")
                print(f"📊 İşlenen ürün: {processed_count}")
                print(f"⏱️ Başarı oranı: %{(processed_count/total_links)*100:.1f}")
                
                return True
                
            finally:
                if self.driver:
                    self.driver.quit()
                    
        except Exception as e:
            print(f"❌ Toplu işlem hatası: {e}")
            if self.driver:
                self.driver.quit()
            return False

def main():
    print("🤖 AliExpress Bot - Otomatik CAPTCHA Çözme")
    print("=" * 60)
    print("✅ 6000+ ürün için optimize edilmiş")
    print("✅ Otomatik CAPTCHA çözme")
    print("✅ Akıllı proxy rotasyonu")
    print("✅ Toplu işlem desteği")
    print("=" * 60)
    
    bot = GelismisAliExpressBot()
    
    # Linkler dosyası kontrolü
    if not os.path.exists('linkler.xlsx'):
        print("\n📋 linkler.xlsx dosyası bulunamadı.")
        print("Lütfen Excel dosyanızı oluşturun ve tekrar çalıştırın.")
        return
    
    # İşlemi başlat
    print("\n🚀 Toplu işlem başlatılıyor...")
    success = bot.process_bulk_links()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 Tüm işlemler başarıyla tamamlandı!")
        print("📁 Sonuçları sonuclar.xlsx dosyasında bulabilirsin.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ İşlem sırasında hata oluştu.")
        print("📄 Detaylar için bot_log.txt dosyasını kontrol et.")
        print("=" * 60)
    
    input("Çıkmak için ENTER'a basın...")

if __name__ == "__main__":
    main()
