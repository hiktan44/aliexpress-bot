#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AliExpress Bot - ChromeDriver Sorunlarını Çözen Versiyon
Manual ChromeDriver kurulumu ile çalışır
"""

import pandas as pd
import time
import random
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class AliExpressBotOtomatik:
    def __init__(self):
        print("🤖 AliExpress Bot - Otomatik CAPTCHA Çözme Başlatılıyor...")
        self.driver = None
        self.urun_sayisi = 0
        self.basarili_urunler = 0
        self.basarisiz_urunler = 0
        self.captcha_cozme_sayisi = 0
        self.sonuclar = []
        
        # User-Agent listesi (bot tespitini zorlaştırır)
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        ]
    
    def chrome_driver_yolu_bul(self):
        """ChromeDriver yolunu otomatik bul"""
        possible_paths = [
            "/usr/local/bin/chromedriver",
            "/opt/homebrew/bin/chromedriver",
            "/usr/bin/chromedriver",
            "./chromedriver",
            "chromedriver"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ ChromeDriver bulundu: {path}")
                return path
                
        # which komutunu dene
        try:
            result = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True)
            if result.returncode == 0:
                path = result.stdout.strip()
                print(f"✅ ChromeDriver bulundu: {path}")
                return path
        except:
            pass
            
        print("❌ ChromeDriver bulunamadı!")
        print("💡 Çözümler:")
        print("1. brew install chromedriver")
        print("2. Manual indirme: https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.49/mac-arm64/chromedriver-mac-arm64.zip")
        return None
    
    def browser_baslat(self):
        """Chrome browser başlatma (manuel ChromeDriver ile)"""
        try:
            print("🌐 Chrome browser başlatılıyor...")
            
            # ChromeDriver yolu bul
            driver_path = self.chrome_driver_yolu_bul()
            if not driver_path:
                return False
            
            chrome_options = Options()
            # Bot tespitini zorlaştıran ayarlar
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(f"--user-agent={random.choice(self.user_agents)}")
            
            # Mac ARM64 için özel ayarlar
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-gpu")
            
            # Chrome service oluştur
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Bot tespitini engelleme script'i
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Chrome browser başarıyla başlatıldı!")
            return True
            
        except Exception as e:
            print(f"❌ Browser başlatma hatası: {e}")
            print("💡 Çözüm önerileri:")
            print("1. Chrome'u güncelleyin")
            print("2. Terminal'de: brew install chromedriver")
            print("3. Güvenlik izni: sudo xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver")
            return False
    
    def captcha_tespit_et(self):
        """CAPTCHA varlığını tespit et"""
        captcha_seciciler = [
            ".nc_wrapper",  # Slider CAPTCHA
            ".geetest_radar_tip",  # GeeTest CAPTCHA
            "#nc_1_n1z",  # AliExpress slider
            "iframe[src*='captcha']",  # Captcha iframe
            ".captcha-container",
            "[data-spm*='captcha']",
            ".robot-mag-btn",  # Robot değilim butonu
            ".nc_scale"  # Slider scale
        ]
        
        for secici in captcha_seciciler:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, secici)
                if element.is_displayed():
                    print(f"🎯 CAPTCHA tespit edildi: {secici}")
                    return True, secici
            except:
                continue
        
        return False, None
    
    def slider_captcha_coz(self, secici):
        """Slider (kaydırma) CAPTCHA'sını çöz"""
        try:
            print("🧩 Slider CAPTCHA çözülüyor...")
            
            # Slider elementi bul
            slider = self.driver.find_element(By.CSS_SELECTOR, secici)
            
            # ActionChains ile insansı hareket
            from selenium.webdriver.common.action_chains import ActionChains
            action = ActionChains(self.driver)
            
            # Slider'ı sağa kaydır (300 pixel)
            action.click_and_hold(slider).perform()
            time.sleep(0.5)
            
            # İnsansı hareket: 5-10 adımda kaydır
            for i in range(10):
                action.move_by_offset(30 + random.randint(-5, 5), random.randint(-2, 2))
                time.sleep(random.uniform(0.1, 0.3))
            
            action.release().perform()
            
            # Başarıyı kontrol et
            time.sleep(2)
            captcha_var, _ = self.captcha_tespit_et()
            
            if not captcha_var:
                print("✅ Slider CAPTCHA başarıyla çözüldü!")
                self.captcha_cozme_sayisi += 1
                return True
            else:
                print("❌ Slider CAPTCHA çözülemedi")
                return False
                
        except Exception as e:
            print(f"❌ Slider CAPTCHA hatası: {e}")
            return False
    
    def checkbox_captcha_coz(self):
        """Checkbox ('Ben robot değilim') CAPTCHA'sını çöz"""
        try:
            print("☑️ Checkbox CAPTCHA çözülüyor...")
            
            checkbox_seciciler = [
                ".robot-mag-btn",
                "input[type='checkbox']",
                ".checkbox",
                "[data-testid='checkbox']"
            ]
            
            for secici in checkbox_seciciler:
                try:
                    checkbox = self.driver.find_element(By.CSS_SELECTOR, secici)
                    if checkbox.is_displayed():
                        # İnsansı tıklama
                        time.sleep(random.uniform(0.5, 1.5))
                        checkbox.click()
                        time.sleep(2)
                        
                        # Başarıyı kontrol et
                        captcha_var, _ = self.captcha_tespit_et()
                        if not captcha_var:
                            print("✅ Checkbox CAPTCHA başarıyla çözüldü!")
                            self.captcha_cozme_sayisi += 1
                            return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"❌ Checkbox CAPTCHA hatası: {e}")
            return False
    
    def captcha_coz(self, secici):
        """Ana CAPTCHA çözme fonksiyonu"""
        print(f"🎯 CAPTCHA çözme deneniyor... (Toplam çözülen: {self.captcha_cozme_sayisi})")
        
        # 2 farklı yöntem dene
        if 'slider' in secici.lower() or 'nc_' in secici:
            return self.slider_captcha_coz(secici)
        else:
            return self.checkbox_captcha_coz()
    
    def urun_bilgilerini_cek(self, link):
        """Ürün bilgilerini çek"""
        try:
            print(f"📦 Ürün bilgileri çekiliyor: {link[:50]}...")
            
            # Sayfaya git
            self.driver.get(link)
            
            # Sayfa yüklenmesini bekle
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # CAPTCHA kontrolü
            for deneme in range(3):
                captcha_var, secici = self.captcha_tespit_et()
                
                if captcha_var:
                    print(f"🚫 CAPTCHA tespit edildi (Deneme {deneme + 1}/3)")
                    
                    if self.captcha_coz(secici):
                        print("✅ CAPTCHA çözüldü, ürün bilgileri çekiliyor...")
                        time.sleep(2)
                        break
                    else:
                        if deneme < 2:
                            print("🔄 Sayfa yenileniyor...")
                            self.driver.refresh()
                            time.sleep(5)
                        else:
                            print("❌ CAPTCHA çözülemedi, ürün atlanıyor")
                            return None
                else:
                    break
            
            # Ürün bilgilerini çek
            urun_adi = "Bilgi bulunamadı"
            fiyat = "Bilgi bulunamadı"
            resim_url = "Bilgi bulunamadı"
            
            # Ürün adı
            isim_seciciler = [
                "h1[data-pl='product-title']",
                ".product-title-text",
                "h1.x-item-title-label",
                ".pdp-product-name",
                "h1"
            ]
            
            for secici in isim_seciciler:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, secici)
                    urun_adi = element.text.strip()
                    if urun_adi:
                        break
                except:
                    continue
            
            # Fiyat
            fiyat_seciciler = [
                ".product-price-current",
                ".pdp-price",
                ".price-current",
                "[data-pl='price']",
                ".price"
            ]
            
            for secici in fiyat_seciciler:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, secici)
                    fiyat = element.text.strip()
                    if fiyat:
                        break
                except:
                    continue
            
            # Resim URL
            resim_seciciler = [
                "img.magnifier-image",
                ".pdp-main-image img",
                ".product-image img",
                "img[data-pl='main-image']"
            ]
            
            for secici in resim_seciciler:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, secici)
                    resim_url = element.get_attribute("src")
                    if resim_url:
                        break
                except:
                    continue
            
            # Sonuç hazırla
            sonuc = {
                'Link': link,
                'Ürün Adı': urun_adi,
                'Fiyat': fiyat,
                'Resim URL': resim_url,
                'Durum': 'Başarılı'
            }
            
            print(f"✅ Ürün başarıyla çekildi: {urun_adi[:30]}...")
            return sonuc
            
        except Exception as e:
            print(f"❌ Ürün çekme hatası: {e}")
            return {
                'Link': link,
                'Ürün Adı': 'Hata',
                'Fiyat': 'Hata',
                'Resim URL': 'Hata',
                'Durum': f'Hata: {str(e)[:50]}'
            }
    
    def gecici_kaydet(self):
        """Geçici kayıt (her 10 üründe)"""
        try:
            if self.sonuclar:
                df = pd.DataFrame(self.sonuclar)
                df.to_excel('gecici_sonuclar.xlsx', index=False)
                print(f"💾 Geçici kayıt yapıldı: {len(self.sonuclar)} ürün")
        except Exception as e:
            print(f"❌ Geçici kayıt hatası: {e}")
    
    def browser_yenile(self):
        """Browser'ı tamamen yenile (her 50 üründe)"""
        try:
            print("🔄 Browser yenileniyor...")
            self.driver.quit()
            time.sleep(3)
            self.browser_baslat()
            print("✅ Browser başarıyla yenilendi!")
        except Exception as e:
            print(f"❌ Browser yenileme hatası: {e}")
    
    def uzun_mola(self):
        """Uzun mola (her 100 üründe)"""
        mola_suresi = random.randint(30, 60)
        print(f"😴 Uzun mola: {mola_suresi} saniye...")
        time.sleep(mola_suresi)
    
    def main(self):
        """Ana program"""
        try:
            print("🚀 AliExpress Bot Otomatik CAPTCHA Çözme başlıyor!")
            print("="*60)
            
            # Browser başlat
            if not self.browser_baslat():
                return
            
            # Excel'den linkleri oku
            try:
                df = pd.read_excel('linkler.xlsx')
                linkler = df['Link'].tolist()
                print(f"📊 {len(linkler)} ürün linki okundu")
            except Exception as e:
                print(f"❌ Excel okuma hatası: {e}")
                return
            
            # Her link için işlem yap
            for i, link in enumerate(linkler, 1):
                self.urun_sayisi = i
                
                print(f"\n🔄 İşlem {i}/{len(linkler)} - İlerleme: %{(i/len(linkler)*100):.1f}")
                
                # Ürün bilgilerini çek
                sonuc = self.urun_bilgilerini_cek(link)
                
                if sonuc:
                    self.sonuclar.append(sonuc)
                    self.basarili_urunler += 1
                else:
                    self.basarisiz_urunler += 1
                
                # İstatistikler
                print(f"📊 Başarılı: {self.basarili_urunler} | Başarısız: {self.basarisiz_urunler} | CAPTCHA: {self.captcha_cozme_sayisi}")
                
                # Geçici kayıt (her 10 üründe)
                if i % 10 == 0:
                    self.gecici_kaydet()
                
                # Browser yenileme (her 50 üründe)
                if i % 50 == 0:
                    self.browser_yenile()
                
                # Uzun mola (her 100 üründe)
                if i % 100 == 0:
                    self.uzun_mola()
                
                # Normal bekleme (ban önleme)
                bekleme = random.uniform(2, 6)
                print(f"⏳ {bekleme:.1f} saniye bekleniyor...")
                time.sleep(bekleme)
            
            # Final kayıt
            print("\n🏁 Tüm ürünler işlendi!")
            df_sonuc = pd.DataFrame(self.sonuclar)
            df_sonuc.to_excel('sonuclar_otomatik.xlsx', index=False)
            
            print("="*60)
            print(f"📊 FINAL İSTATİSTİKLER:")
            print(f"✅ Toplam işlenen: {len(linkler)}")
            print(f"✅ Başarılı: {self.basarili_urunler}")
            print(f"❌ Başarısız: {self.basarisiz_urunler}")
            print(f"🤖 CAPTCHA çözülen: {self.captcha_cozme_sayisi}")
            print(f"💾 Sonuçlar kaydedildi: sonuclar_otomatik.xlsx")
            
        except KeyboardInterrupt:
            print("\n⏹️ İşlem kullanıcı tarafından durduruldu")
            if self.sonuclar:
                df_gecici = pd.DataFrame(self.sonuclar)
                df_gecici.to_excel('kesintili_sonuclar.xlsx', index=False)
                print("💾 Kesintili sonuçlar kaydedildi: kesintili_sonuclar.xlsx")
                
        except Exception as e:
            print(f"❌ Genel hata: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
                print("🔚 Browser kapatıldı")

if __name__ == "__main__":
    bot = AliExpressBotOtomatik()
    bot.main()
