class AliExpressParser:
    """Geliştirilmiş AliExpress JSON data parser"""
    
    @staticmethod
    def extract_json_data(html_content):
        """HTML içinden JSON datalarını çıkar - Geliştirilmiş"""
        try:
            extracted_data = {}
            
            # Method 1: window.runParams - Ana veri kaynağı
            runparams_patterns = [
                r'window\.runParams\s*=\s*({.*?});',
                r'runParams\s*:\s*({.*?}),',
                r'window\["runParams"\]\s*=\s*({.*?});'
            ]
            
            for pattern in runparams_patterns:
                matches = re.findall(pattern, html_content, re.DOTALL)
                for match in matches:
                    try:
                        # JSON temizle ve parse et
                        cleaned = re.sub(r'//.*?\n', '', match)  # Yorumları kaldır
                        cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)  # Block yorumları
                        data = json.loads(cleaned)
                        extracted_data.update(data)
                        print("✅ runParams JSON bulundu!")
                    except Exception as e:
                        print(f"runParams parse hatası: {e}")
                        continue
            
            # Method 2: Script tag içindeki JSON'lar
            script_patterns = [
                r'<script[^>]*>(.*?)</script>',
            ]
            
            for script_match in re.finditer(script_patterns[0], html_content, re.DOTALL | re.IGNORECASE):
                script_content = script_match.group(1)
                
                # İçinde JSON arama patterns
                json_patterns = [
                    r'"data"\s*:\s*({.*?"priceModule".*?})',
                    r'"priceModule"\s*:\s*({.*?})',
                    r'"titleModule"\s*:\s*({.*?})',
                    r'"imageModule"\s*:\s*({.*?})',
                    r'"skuModule"\s*:\s*({.*?})',
                    r'"storeModule"\s*:\s*({.*?})',
                    r'"feedbackModule"\s*:\s*({.*?})'
                ]
                
                for pattern in json_patterns:
                    matches = re.findall(pattern, script_content, re.DOTALL)
                    for match in matches:
                        try:
                            # Başına ve sonuna { } ekle
                            if not match.startswith('{'):
                                match = '{' + match
                            if not match.endswith('}'):
                                match = match + '}'
                            
                            data = json.loads(match)
                            extracted_data.update(data)
                            print(f"✅ Script JSON bulundu: {pattern[:20]}...")
                        except:
                            continue
            
            # Method 3: Direkt module arama
            module_patterns = [
                r'window\.runParams\s*=.*?"data"\s*:\s*({.*?})',
                r'__INITIAL_STATE__\s*=\s*({.*?});',
                r'window\.__moduleData__\s*=\s*({.*?});'
            ]
            
            for pattern in module_patterns:
                matches = re.findall(pattern, html_content, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        extracted_data.update(data)
                        print("✅ Module JSON bulundu!")
                    except:
                        continue
            
            print(f"📊 Toplam çıkarılan JSON keys: {list(extracted_data.keys())}")
            return extracted_data
            
        except Exception as e:
            print(f"❌ JSON extraction genel hatası: {e}")
            return {}
    
    @staticmethod
    def parse_product_data(json_data, html_content):
        """JSON data'dan ürün bilgilerini çıkar - Geliştirilmiş"""
        try:
            product_info = {
                'title': 'Bilgi bulunamadı',
                'price': 'Bilgi bulunamadı', 
                'image': 'Bilgi bulunamadı',
                'rating': 'Bilgi bulunamadı',
                'sold_count': 'Bilgi bulunamadı'
            }
            
            print(f"🔍 JSON data keys: {list(json_data.keys())}")
            
            # BAŞLIK - Çoklu kaynak arama
            title_sources = [
                # runParams içinden
                lambda d: d.get('data', {}).get('titleModule', {}).get('subject', ''),
                lambda d: d.get('titleModule', {}).get('subject', ''),
                # Direkt arama
                lambda d: d.get('subject', ''),
                lambda d: d.get('productTitle', ''),
                lambda d: d.get('title', ''),
                # İç içe arama
                lambda d: d.get('data', {}).get('subject', ''),
                lambda d: d.get('product', {}).get('title', ''),
                lambda d: d.get('product', {}).get('subject', '')
            ]
            
            for i, source in enumerate(title_sources):
                try:
                    title = source(json_data)
                    if title and len(title) > 10 and 'AliExpress' not in title:
                        product_info['title'] = title[:200]
                        print(f"✅ Başlık bulundu (method {i+1}): {title[:50]}...")
                        break
                except Exception as e:
                    print(f"Title source {i+1} hatası: {e}")
                    continue
            
            # FİYAT - Çoklu kaynak arama
            price_sources = [
                # runParams priceModule
                lambda d: d.get('data', {}).get('priceModule', {}).get('formatedPrice', ''),
                lambda d: d.get('priceModule', {}).get('formatedPrice', ''),
                lambda d: d.get('data', {}).get('priceModule', {}).get('minPrice', {}).get('formatedPrice', ''),
                lambda d: d.get('priceModule', {}).get('minPrice', {}).get('formatedPrice', ''),
                # skuModule
                lambda d: d.get('data', {}).get('skuModule', {}).get('skuPriceList', [{}])[0].get('skuVal', {}).get('skuAmount', {}).get('formatedAmount', ''),
                lambda d: d.get('skuModule', {}).get('skuPriceList', [{}])[0].get('skuVal', {}).get('skuAmount', {}).get('formatedAmount', ''),
                # Direkt price alanları
                lambda d: d.get('price', ''),
                lambda d: d.get('formatedPrice', ''),
                lambda d: d.get('minPrice', ''),
                lambda d: d.get('maxPrice', ''),
                # İç içe arama
                lambda d: d.get('data', {}).get('price', ''),
                lambda d: d.get('product', {}).get('price', '')
            ]
            
            for i, source in enumerate(price_sources):
                try:
                    price = source(json_data)
                    if price and price != '0' and len(str(price)) > 1:
                        product_info['price'] = str(price)
                        print(f"✅ Fiyat bulundu (method {i+1}): {price}")
                        break
                except Exception as e:
                    print(f"Price source {i+1} hatası: {e}")
                    continue
            
            # RESİM - Çoklu kaynak arama
            image_sources = [
                # imageModule
                lambda d: d.get('data', {}).get('imageModule', {}).get('imagePathList', [None])[0],
                lambda d: d.get('imageModule', {}).get('imagePathList', [None])[0],
                # Direkt image alanları
                lambda d: d.get('image', ''),
                lambda d: d.get('imageUrl', ''),
                lambda d: d.get('images', [None])[0] if d.get('images') else None,
                # İç içe arama
                lambda d: d.get('data', {}).get('image', ''),
                lambda d: d.get('product', {}).get('image', ''),
                lambda d: d.get('product', {}).get('images', [None])[0] if d.get('product', {}).get('images') else None
            ]
            
            for i, source in enumerate(image_sources):
                try:
                    image = source(json_data)
                    if image and 'http' in str(image):
                        # AliExpress resim URL'sini düzelt
                        if not image.startswith('http'):
                            if image.startswith('//'):
                                image = 'https:' + image
                            else:
                                image = 'https://ae01.alicdn.com/kf/' + image
                        product_info['image'] = image
                        print(f"✅ Resim bulundu (method {i+1}): {image[:50]}...")
                        break
                except Exception as e:
                    print(f"Image source {i+1} hatası: {e}")
                    continue
            
            # RATING ve SATIŞ SAYISI
            try:
                # Rating
                rating_sources = [
                    lambda d: d.get('data', {}).get('storeModule', {}).get('storeRating', ''),
                    lambda d: d.get('storeModule', {}).get('storeRating', ''),
                    lambda d: d.get('data', {}).get('feedbackModule', {}).get('averageStar', ''),
                    lambda d: d.get('feedbackModule', {}).get('averageStar', ''),
                    lambda d: d.get('rating', ''),
                    lambda d: d.get('averageRating', '')
                ]
                
                for source in rating_sources:
                    try:
                        rating = source(json_data)
                        if rating:
                            product_info['rating'] = str(rating)
                            print(f"✅ Rating bulundu: {rating}")
                            break
                    except:
                        continue
                
                # Satış sayısı
                sold_sources = [
                    lambda d: d.get('data', {}).get('tradeModule', {}).get('formatTradeCount', ''),
                    lambda d: d.get('tradeModule', {}).get('formatTradeCount', ''),
                    lambda d: d.get('data', {}).get('skuModule', {}).get('totalSoldCount', ''),
                    lambda d: d.get('skuModule', {}).get('totalSoldCount', ''),
                    lambda d: d.get('soldCount', ''),
                    lambda d: d.get('totalSold', '')
                ]
                
                for source in sold_sources:
                    try:
                        sold = source(json_data)
                        if sold:
                            product_info['sold_count'] = str(sold)
                            print(f"✅ Satış sayısı bulundu: {sold}")
                            break
                    except:
                        continue
                        
            except Exception as e:
                print(f"Rating/Sold parsing hatası: {e}")
            
            # Eğer JSON'dan hiçbir şey bulamazsak HTML fallback
            if all(v == 'Bilgi bulunamadı' for k, v in product_info.items() if k != 'rating' and k != 'sold_count'):
                print("⚠️ JSON'dan hiçbir veri bulunamadı, HTML fallback aktif...")
                return AliExpressParser.html_fallback_parsing(html_content)
            
            print(f"📋 Final product info: {product_info}")
            return product_info
            
        except Exception as e:
            print(f"❌ Product parsing hatası: {e}")
            # HTML fallback
            return AliExpressParser.html_fallback_parsing(html_content)
    
    @staticmethod
    def html_fallback_parsing(html_content):
        """Geliştirilmiş HTML fallback parsing"""
        try:
            print("🔍 Geliştirilmiş HTML parsing başlatılıyor...")
            
            product_info = {
                'title': 'Bilgi bulunamadı',
                'price': 'Bilgi bulunamadı', 
                'image': 'Bilgi bulunamadı',
                'rating': 'HTML parse',
                'sold_count': 'HTML parse'
            }
            
            # BAŞLIK - HTML'den
            title_patterns = [
                r'<title[^>]*>([^<]+)</title>',
                r'<h1[^>]*>([^<]+)</h1>',
                r'"product.*?title"\s*:\s*"([^"]+)"',
                r'"subject"\s*:\s*"([^"]+)"',
                r'property="og:title"\s+content="([^"]+)"'
            ]
            
            for pattern in title_patterns:
                try:
                    match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
                    if match:
                        title = match.group(1).strip()
                        if len(title) > 10 and 'AliExpress' not in title and 'Error' not in title:
                            product_info['title'] = title[:200]
                            print(f"✅ HTML Title bulundu: {title[:50]}...")
                            break
                except:
                    continue
            
            # FİYAT - HTML'den gelişmiş arama
            price_patterns = [
                r'"formatedPrice"\s*:\s*"([^"]+)"',
                r'"price"\s*:\s*"([^"]+)"',
                r'US\s*\$\s*([\d,.]+)',
                r'\$\s*([\d,.]+)',
                r'USD\s*([\d,.]+)',
                r'€\s*([\d,.]+)',
                r'£\s*([\d,.]+)',
                r'price[^>]*>.*?\$([^<]+)',
                r'class="[^"]*price[^"]*"[^>]*>.*?\$([^<]+)',
                r'data-[^=]*price[^=]*="[^"]*\$([^"]+)"'
            ]
            
            for pattern in price_patterns:
                try:
                    matches = re.findall(pattern, html_content, re.IGNORECASE)
                    for match in matches:
                        match = match.strip()
                        if match and match != '1' and match != '0' and len(match) > 1:
                            # $ işareti yoksa ekle
                            if not any(char in match for char in ['$', '€', '£', '¥']):
                                match = '$' + match
                            product_info['price'] = match
                            print(f"✅ HTML Price bulundu: {match}")
                            break
                    if product_info['price'] != 'Bilgi bulunamadı':
                        break
                except:
                    continue
            
            # RESİM - HTML'den
            image_patterns = [
                r'"imagePathList"\s*:\s*\[\s*"([^"]+)"',
                r'"image"\s*:\s*"([^"]+)"',
                r'<img[^>]+src="([^"]*alicdn[^"]*)"',
                r'<img[^>]+src="([^"]*aliexpress[^"]*)"',
                r'property="og:image"\s+content="([^"]+)"',
                r'src="(https://[^"]*ae[0-9]+\.alicdn\.com[^"]*)"'
            ]
            
            for pattern in image_patterns:
                try:
                    match = re.search(pattern, html_content, re.IGNORECASE)
                    if match:
                        image = match.group(1)
                        if 'http' in image:
                            if not image.startswith('http'):
                                if image.startswith('//'):
                                    image = 'https:' + image
                                else:
                                    image = 'https:' + image
                            product_info['image'] = image
                            print(f"✅ HTML Image bulundu: {image[:50]}...")
                            break
                except:
                    continue
            
            print(f"📋 HTML Fallback result: {product_info}")
            return product_info
            
        except Exception as e:
            print(f"❌ HTML fallback hatası: {e}")
            return {
                'title': 'HTML parse hatası',
                'price': 'HTML parse hatası', 
                'image': 'HTML parse hatası',
                'rating': 'HTML parse hatası',
                'sold_count': 'HTML parse hatası'
            }