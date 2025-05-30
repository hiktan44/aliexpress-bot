# Railway Chrome Fix - Optimized Dockerfile
FROM python:3.11-slim-bullseye

# System dependencies ve Chrome kurulumu
RUN apt-get update && apt-get install -y \
    # Chrome ve driver dependencies  
    chromium \
    chromium-driver \
    # Web scraping dependencies
    wget \
    curl \
    gnupg \
    unzip \
    # System utilities
    xvfb \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# App dosyalarını kopyala  
COPY . .

# Chrome environment variables
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV DISPLAY=:99

# Permissions düzelt
RUN chmod +x /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromium

# Railway port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Non-root user oluştur (güvenlik için)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# App başlat
CMD ["python", "aliexpress_bot_web_entegre.py"]