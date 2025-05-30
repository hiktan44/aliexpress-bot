# CAPTCHA Düzeltme Kodu - İki aşamalı sistem

def scrape_do_captcha_bypass(self, link):
    """Scrape.do ile CAPTCHA bypass denemesi"""
    try:
        print("🔧 Scrape.do CAPTCHA bypass deneniyor...")
        
        # Scrape.do API endpoint
        scrape_api_url = "https://api.scrape.do"
        
        # API key check
        scrape_api_key = os.getenv('SCRAPE_API_KEY')
        if not scrape_api_key:
            print("⚠️ Scrape.do API key bulunamadı")
            return False
        
        # Scrape.do request
        params = {
            'url': link,
            'token': scrape_api_key,
            'render': True,
            'country': 'US'
        }
        
        response = requests.get(scrape_api_url, params=params, timeout=30)
        
        if response.status_code == 200:
            # HTML'i kontrol et - CAPTCHA var mı?
            html_content = response.text
            
            # CAPTCHA indicators
            captcha_indicators = [
                'captcha', 'geetest', 'recaptcha', 'slider',
                'verify', 'challenge', 'robot'
            ]
            
            # HTML'de CAPTCHA var mı kontrol et
            has_captcha = any(indicator in html_content.lower() for indicator in captcha_indicators)
            
            if not has_captcha:
                print("✅ Scrape.do CAPTCHA'yı geçti!")
                
                # HTML'den veri çek
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Ürün adı
                title = soup.find('title')
                urun_adi = title.text.strip() if title else "Bilgi bulunamadı"
                
                # Fiyat
                fiyat = "Fiyat bulunamadı"
                price_elements = soup.find_all(text=lambda text: text and ('$' in text or '₺' in text or 'TL' in text))
                for price_text in price_elements:
                    if any(char.isdigit() for char in price_text):
                        fiyat = price_text.strip()
                        break
                
                # Resim
                resim_url = "Resim bulunamadı"
                img_tags = soup.find_all('img')
                for img in img_tags:
                    src = img.get('src', '')
                    if src and ('alicdn' in src or 'aliexpress' in src):
                        resim_url = src
                        break
                
                return {
                    'success': True,
                    'data': {
                        'Ürün Adı': urun_adi,
                        'Fiyat': fiyat,
                        'Resim URL': resim_url
                    }
                }
            else:
                print("❌ Scrape.do CAPTCHA geçemedi")
                return False
                
        else:
            print(f"❌ Scrape.do API hatası: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Scrape.do hatası: {e}")
        return False

def improved_captcha_handler(self):
    """İyileştirilmiş 2 aşamalı CAPTCHA handler"""
    
    # CAPTCHA kontrol selectors
    captcha_selectors = [
        "iframe[src*='captcha']",
        ".nc_wrapper", 
        ".geetest",
        "[class*='captcha']",
        "[id*='captcha']", 
        ".slider-track",
        ".verify-code",
        "[data-sitekey]",
        ".captcha-container"
    ]
    
    # CAPTCHA var mı kontrol et
    captcha_detected = False
    captcha_type = ""
    
    for selector in captcha_selectors:
        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            captcha_detected = True
            captcha_type = selector
            print(f"\n🤖 CAPTCHA TESPİT EDİLDİ: {selector}")
            break
    
    if captcha_detected:
        current_url = self.driver.current_url
        
        # 1. AŞAMA: Scrape.do ile bypass denemesi
        print("🔧 1. AŞAMA: Scrape.do ile CAPTCHA bypass deneniyor...")
        
        scrape_result = self.scrape_do_captcha_bypass(current_url)
        
        if scrape_result and scrape_result.get('success'):
            print("✅ Scrape.do CAPTCHA'yı başarıyla geçti!")
            return scrape_result['data']
        
        # 2. AŞAMA: Manuel çözme (Web Modal)
        print("🌐 2. AŞAMA: Manuel CAPTCHA çözme sistemi aktif")
        
        # Railway production check
        is_production = (
            os.environ.get('RAILWAY_ENVIRONMENT') or 
            os.environ.get('PORT') or
            os.path.exists('/app')
        )
        
        if is_production:
            print("🌐 RAILWAY: Web Modal CAPTCHA sistemi")
            
            # CAPTCHA screenshot al
            try:
                screenshot_data = self.driver.get_screenshot_as_base64()
                page_url = self.driver.current_url
                page_title = self.driver.title
                
                # CAPTCHA bilgilerini global değişkende sakla
                global captcha_waiting, captcha_data
                captcha_waiting = True
                captcha_data = {
                    'detected': True,
                    'type': captcha_type,
                    'screenshot': screenshot_data,
                    'url': page_url,
                    'title': page_title,
                    'timestamp': time.time()
                }
                
                print("📸 CAPTCHA screenshot alındı")
                print("🌐 Web arayüzünde CAPTCHA modal açılacak...")
                print("👤 Kullanıcı müdahalesini bekliyorum...")
                
                # Web modal'dan yanıt bekle
                max_wait = 300  # 5 dakika
                waited = 0
                
                while captcha_waiting and waited < max_wait:
                    time.sleep(3)
                    waited += 3
                    
                    # Kullanıcı aksiyonu kontrol et
                    global captcha_action
                    if captcha_action == 'solved':
                        print("✅ Kullanıcı CAPTCHA'ı çözdü!")
                        captcha_waiting = False
                        captcha_action = None
                        captcha_data = None
                        
                        # Sayfa yenilenmesini bekle
                        time.sleep(3)
                        return True
                        
                    elif captcha_action == 'skip':
                        print("⏭️ Kullanıcı ürünü atlamayı seçti")
                        captcha_waiting = False
                        captcha_action = None
                        captcha_data = None
                        return "skip"
                    
                    # Progress göster
                    if waited % 30 == 0:
                        remaining = max_wait - waited
                        print(f"⏰ CAPTCHA çözme bekleniyor... Kalan: {remaining}s")
                
                print("⏰ CAPTCHA bekleme süresi doldu")
                captcha_waiting = False
                captcha_data = None
                return "skip"
                
            except Exception as e:
                print(f"❌ CAPTCHA screenshot hatası: {e}")
                return "skip"
        else:
            # Local development - Visible mode
            print("💻 LOCAL: Visible mode CAPTCHA çözme")
            
            # Visible mode'a geç
            if hasattr(self, 'driver'):
                self.driver.quit()
            
            self.driver = self.setup_chrome_driver_hybrid(visible_mode=True)
            self.driver.get(current_url)
            
            print("👁️ Visible Chrome açıldı - Manuel CAPTCHA çözün!")
            print("⏳ CAPTCHA çözülmesini bekliyorum...")
            
            # CAPTCHA çözülmesini bekle
            max_wait = 300
            waited = 0
            
            while waited < max_wait:
                time.sleep(5)
                waited += 5
                
                # CAPTCHA hala var mı kontrol et
                captcha_still_exists = False
                for selector in captcha_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        captcha_still_exists = True
                        break
                
                if not captcha_still_exists:
                    print("✅ CAPTCHA çözüldü! (Visible mode)")
                    return True
                
                if waited % 30 == 0:
                    remaining = max_wait - waited
                    print(f"⏰ CAPTCHA çözme bekleniyor... Kalan: {remaining}s")
            
            print("⏰ CAPTCHA bekleme süresi doldu")
            return "skip"
    
    return False