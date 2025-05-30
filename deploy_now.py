#!/usr/bin/env python3
import subprocess
import os

print("🚀 DEPLOY BAŞLATIYOR!")
print("=" * 40)

# Proje dizinine geç
os.chdir("/Users/hikmettanriverdi/Desktop/AliExpressBot")

try:
    # Script'i çalıştırılabilir yap
    subprocess.run(["chmod", "+x", "critical_fix_push.sh"], check=True)
    print("✅ Script izinleri ayarlandı")
    
    # Deploy script'ini çalıştır
    result = subprocess.run(["./critical_fix_push.sh"], 
                          capture_output=True, 
                          text=True, 
                          check=True)
    
    print("📤 DEPLOY ÇIKTISI:")
    print("-" * 30)
    print(result.stdout)
    
    if result.stderr:
        print("⚠️ UYARILAR:")
        print(result.stderr)
    
    print("\n🎉 DEPLOY BAŞARILI!")
    print("🚀 Railway'de build başladı!")
    
except subprocess.CalledProcessError as e:
    print(f"❌ Deploy hatası: {e}")
    print(f"Stdout: {e.stdout}")
    print(f"Stderr: {e.stderr}")
except Exception as e:
    print(f"🚨 Genel hata: {e}")

print("\n🔥 Railway dashboard'u kontrol edin!")
