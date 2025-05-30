                    'Resim URL': 'Atlandı',
                    'YZ HS Kod': 'Atlandı',
                    'Durum': 'CAPTCHA Skip'
                }
            elif captcha_result:
                print("✅ 2. AŞAMA: Manuel CAPTCHA çözüldü!")
                # Normal selenium scraping devam et
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
                
                fiyat = self.tum_fiyatlari_bul()
                resim_url = self.tum_resimleri_bul()
            
            else:
                # CAPTCHA yok, normal scraping
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
                
                fiyat = self.tum_fiyatlari_bul()
                resim_url = self.tum_resimleri_bul()
            
            # Başarı kontrolü
            is_successful = (
                urun_adi != "Bilgi bulunamadı" and 
                fiyat != "Fiyat bulunamadı" and 
                len(urun_adi) > 10 and
                "bulunamadı" not in urun_adi.lower()
            )
            
            if not is_successful:
                print("❌ BAŞARISIZ: Bilgi bulunamadı...")
                
                sonuc = {
                    'Link': link,
                    'Ürün Adı': urun_adi,
                    'Fiyat': fiyat,
                    'Resim URL': resim_url,
                    'YZ HS Kod': 'Veri yetersiz',
                    'Durum': 'Başarısız - Bilgi eksik'
                }
                
                print(f"💰 Fiyat: {fiyat}")
                print(f"🖼️ Resim: {'✅' if resim_url != 'Resim bulunamadı' else '❌'}")
                print(f"🧠 HS Kod: Veri yetersiz")
                print(f"❌ BAŞARISIZ: Başarısız - Bilgi eksik")
                
                return sonuc
            
            # HS Kodu AI ile tespit et
            hs_kod = "API Key gerekli"
            if self.gemini_api_key or self.openai_api_key:
                hs_kod = self.ai_hs_kod_tespit(urun_adi, resim_url)
            
            # Başarılı sonuç
            sonuc = {
                'Link': link,
                'Ürün Adı': urun_adi,
                'Fiyat': fiyat,
                'Resim URL': resim_url,
                'YZ HS Kod': hs_kod,
                'Durum': 'Başarılı'
            }
            
            print(f"✅ Ürün: {urun_adi[:40]}...")
            print(f"💰 Fiyat: {fiyat}")
            print(f"🖼️ Resim: {'✅' if resim_url != 'Resim bulunamadı' else '❌'}")
            print(f"🧠 HS Kod: {hs_kod}")
            print(f"✅ BAŞARILI: {urun_adi[:40]}...")
            
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
            print("🚀 İyileştirilmiş AliExpress Bot başlıyor!")
            print("🔧 2 Aşamalı CAPTCHA Sistemi aktif!")
            
            if not self.browser_baslat():
                return
            
            # Her ürün için işlem
            for i, link in enumerate(self.linkler):
                if not self.is_running:
                    break
                    
                self.current_index = i + 1
                
                # İyileştirilmiş veri çekme
                sonuc = self.improved_veri_cek(link)
                
                # Başarı durumunu kontrol et
                if sonuc and sonuc['Durum'] == 'Başarılı':
                    self.sonuclar.append(sonuc)
                    self.basarili += 1
                    
                    # Excel'i güncelle
                    self.excel_verisini_guncelle(i, sonuc)
                    
                    print(f"✅ BAŞARILI: {sonuc['Ürün Adı'][:30]}...")
                    
                elif sonuc and 'Başarısız' in sonuc['Durum']:
                    self.sonuclar.append(sonuc)
                    self.basarisiz += 1
                    
                    print(f"❌ BAŞARISIZ: {sonuc['Durum']}")
                    
                else:
                    self.basarisiz += 1
                    
                    print(f"❌ HATA: {sonuc.get('Durum', 'Bilinmeyen hata') if sonuc else 'Sonuç alınamadı'}")
                
                # Web arayüzüne gönder
                self.web_sonuc_ekle(sonuc)
                self.web_durumu_guncelle()
                
                # Bekleme
                time.sleep(random.uniform(4, 8))
            
            # Bitirme
            self.is_running = False
            
            # Final kayıt
            df_final = pd.DataFrame(self.sonuclar)
            df_final.to_excel('sonuclar_improved.xlsx', index=False)
            
            print(f"\n🏁 İŞLEM BİTTİ!")
            print(f"✅ Başarılı: {self.basarili}")
            print(f"❌ Başarısız: {self.basarisiz}")
            print(f"💾 Excel: sonuclar_improved.xlsx")
            
            self.web_durumu_guncelle()
            
        except Exception as e:
            print(f"❌ Bot hatası: {e}")
            self.is_running = False
            self.web_durumu_guncelle()
        finally:
            if self.driver:
                self.driver.quit()

# Global CAPTCHA state
captcha_waiting = False
captcha_action = None
captcha_data = None

# Global uygulama instance
uygulama = AliExpressVeriCekmeUygulamasi()

# Flask routes
@app.route('/')
def index():
    return render_template('bot_arayuz.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print("Upload request received")
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Dosya seçilmedi'})
        
        file = request.files['file']
        print(f"File received: {file.filename}")
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Dosya seçilmedi'})
        
        if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            return jsonify({'success': False, 'message': 'Geçersiz dosya formatı'})
        
        # Dosyayı kaydet
        temp_path = f"temp_{file.filename}"
        file.save(temp_path)
        print(f"File saved to: {temp_path}")
        
        # Excel'i oku
        df = pd.read_excel(temp_path)
        print(f"Excel read successfully. Shape: {df.shape}")
        
        # Orijinal Excel'i sakla
        uygulama.original_df = df.copy()
        uygulama.excel_columns = df.columns.tolist()
        
        # Link sütununu bul
        link_column = None
        if 'Link' in df.columns:
            link_column = 'Link'
        else:
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
        
        # Link'leri al
        uygulama.linkler = df[link_column].dropna().tolist()
        uygulama.total_links = len(uygulama.linkler)
        print(f"Links extracted: {uygulama.total_links}")
        
        # Temp dosyayı sil
        os.remove(temp_path)
        
        # Durumu güncelle
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
        return jsonify({'success': False, 'message': f'Dosya yükleme hatası: {str(e)}'})

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
        
        # Thread'de çalıştır
        Thread(target=uygulama.bot_calistir, daemon=True).start()
        
        return jsonify({'success': True, 'message': 'İyileştirilmiş 2 Aşamalı CAPTCHA sistemi başlatıldı!'})
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
        
        uygulama.column_mapping = mapping
        print(f"Column mapping saved: {mapping}")
        
        return jsonify({'success': True, 'message': 'Sütun eşleştirmesi kaydedildi'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Sütun eşleştirme hatası: {str(e)}'})

@app.route('/set_ai_model', methods=['POST'])
def set_ai_model():
    try:
        data = request.get_json()
        model_type = data.get('model', '').strip()
        
        if not model_type or model_type not in ['gemini', 'openai']:
            return jsonify({'success': False, 'message': 'Geçersiz model tipi'})
        
        uygulama.selected_ai_model = model_type
        
        if model_type == 'gemini':
            if not uygulama.gemini_api_key:
                return jsonify({'success': False, 'message': 'Gemini API key .env dosyasında bulunamadı'})
            return jsonify({'success': True, 'message': '🤖 Gemini 2.5 Pro aktif! HS kod analizi hazır.'})
            
        elif model_type == 'openai':
            if not uygulama.openai_api_key:
                return jsonify({'success': False, 'message': 'OpenAI API key .env dosyasında bulunamadı'})
            return jsonify({'success': True, 'message': '🧠 ChatGPT-4o aktif! HS kod analizi hazır.'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'AI model ayarlama hatası: {str(e)}'})

@app.route('/download')
def download_results():
    try:
        if uygulama.original_df is not None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f'guncellenmis_excel_{timestamp}.xlsx'
            
            uygulama.original_df.to_excel(filename, index=False)
            
            return jsonify({
                'success': True,
                'message': f'Güncellenmiş Excel dosyası hazırlandı: {len(uygulama.original_df)} satır',
                'filename': filename,
                'count': len(uygulama.original_df),
                'type': 'updated_excel',
                'download_url': f'/download_file/{filename}'
            })
        elif uygulama.sonuclar:
            df = pd.DataFrame(uygulama.sonuclar)
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f'aliexpress_improved_{timestamp}.xlsx'
            
            df.to_excel(filename, index=False)
            
            return jsonify({
                'success': True,
                'message': f'Excel dosyası hazırlandı: {len(uygulama.sonuclar)} kayıt',
                'filename': filename,
                'count': len(uygulama.sonuclar),
                'type': 'results_only',
                'download_url': f'/download_file/{filename}'
            })
        else:
            return jsonify({'success': False, 'message': 'İndirilecek veri yok'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'İndirme hatası: {str(e)}'})

@app.route('/captcha_status')
def get_captcha_status():
    global captcha_waiting, captcha_data
    
    if captcha_waiting and captcha_data:
        return jsonify({
            'captcha_detected': True,
            'captcha_type': captcha_data['type'],
            'screenshot': captcha_data['screenshot'],
            'url': captcha_data['url'],
            'title': captcha_data['title'],
            'timestamp': captcha_data['timestamp']
        })
    else:
        return jsonify({'captcha_detected': False})

@app.route('/captcha_solved', methods=['POST'])
def captcha_solved():
    global captcha_waiting, captcha_action
    
    try:
        data = request.get_json()
        action = data.get('action', '')
        
        if action in ['continue', 'solved']:
            captcha_action = 'solved'
            print("🌐 Web arayüzünden: CAPTCHA çözüldü")
            return jsonify({'success': True, 'message': 'CAPTCHA çözüldü olarak işaretlendi'})
            
        elif action == 'skip':
            captcha_action = 'skip'
            print("🌐 Web arayüzünden: Ürün atla")
            return jsonify({'success': True, 'message': 'Ürün atlanacak'})
        else:
            return jsonify({'success': False, 'message': 'Geçersiz aksiyon'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'CAPTCHA aksiyon hatası: {str(e)}'})

@app.route('/download_file/<filename>')
def download_file(filename):
    try:
        if not os.path.exists(filename):
            return jsonify({'success': False, 'message': 'Dosya bulunamadı'}), 404
        
        return send_file(
            filename,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({'success': False, 'message': f'Dosya indirme hatası: {str(e)}'}), 500

if __name__ == "__main__":
    import socket
    
    # Port belirleme
    port = int(os.environ.get('PORT', 0))
    
    if port == 0:
        def find_free_port():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', 0))
                s.listen(1)
                port = s.getsockname()[1]
            return port
        
        port = find_free_port()
        print(f"💻 Local development mode")
    else:
        print(f"🌍 Production mode (Railway/Cloud)")
    
    print("🚀 İyileştirilmiş AliExpress Bot başlatılıyor...")
    print("🔧 2 Aşamalı CAPTCHA Sistemi:")
    print("   1️⃣ Scrape.do bypass")
    print("   2️⃣ Manuel web modal")
    print(f"📱 Tarayıcıda: http://localhost:{port}")
    print(f"🚀 Port {port} kullanılıyor")
    
    app.run(host='0.0.0.0', port=port, debug=False)
