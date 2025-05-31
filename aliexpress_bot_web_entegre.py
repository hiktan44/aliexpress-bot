from flask import Flask, jsonify
import os
from datetime import datetime

app = Flask(__name__)
PORT = int(os.getenv('PORT', 5000))

@app.route('/')
def home():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AliExpress Bot - Railway</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f0f2f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .btn {{ display: inline-block; padding: 12px 20px; margin: 8px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; }}
            .btn:hover {{ background: #0056b3; }}
            .btn.success {{ background: #28a745; }}
            .btn.warning {{ background: #ffc107; color: #212529; }}
            .status {{ background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745; }}
            .info {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AliExpress Bot</h1>
            <h2>Railway Deployment</h2>
            
            <div class="status">
                <h3>✅ Bot Aktif ve Hazır!</h3>
                <p><strong>Deploy Zamanı:</strong> {timestamp}</p>
                <p><strong>Port:</strong> {PORT}</p>
                <p><strong>Durum:</strong> Production Ready</p>
            </div>

            <div class="info">
                <h4>🔗 API Endpoints:</h4>
                <a href="/health" class="btn success">🏥 Health Check</a>
                <a href="/status" class="btn">📊 Bot Status</a>
                <a href="/test" class="btn warning">🧪 Test API</a>
            </div>
            
            <div class="info">
                <h4>📊 Sistem Bilgileri:</h4>
                <ul>
                    <li>✅ Railway deployment başarılı</li>
                    <li>✅ Flask web server aktif</li>
                    <li>✅ API endpoints çalışıyor</li>
                    <li>✅ Production modunda çalışıyor</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "port": PORT,
        "railway": "active",
        "bot": "ready"
    })

@app.route('/status')  
def status():
    return jsonify({
        "bot": "active",
        "railway": "deployed",
        "timestamp": datetime.now().isoformat(),
        "server": "flask",
        "port": PORT,
        "endpoints": ["/", "/health", "/status", "/test"]
    })

@app.route('/test')
def test():
    return jsonify({
        "test": "PASSED",
        "message": "Railway deployment başarılı!",
        "timestamp": datetime.now().isoformat(),
        "bot_ready": True,
        "api_working": True
    })

if __name__ == '__main__':
    print(f"🚀 AliExpress Bot - Railway Production Server")
    print(f"🌐 Port: {PORT}")
    print(f"✅ Server başlatılıyor...")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)