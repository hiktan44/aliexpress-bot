#!/bin/bash

# AliExpress Bot - Docker Fix GitHub Push Script
echo "🚀 AliExpress Bot Docker Fix - GitHub Push Script"
echo "=================================================="

# Proje dizinine git
cd /Users/hikmettanriverdi/Desktop/AliExpressBot

echo "📂 Current directory: $(pwd)"

# Git status kontrol
echo ""
echo "📋 Git Status:"
git status

echo ""
echo "📤 Adding all files..."
git add .

echo ""
echo "📝 Creating commit..."
git commit -m "🐳 Railway Dockerfile Fix - Native Chromium + Multi-Strategy Chrome Setup

✅ Dockerfile optimized for Railway
✅ Native Chromium + ChromeDriver (Debian)
✅ Multi-strategy Chrome detection
✅ Docker environment variables
✅ Health check added
✅ Non-root user security
✅ Permission fixes
✅ Production environment detection
✅ Chrome binary path priority (Docker first)
✅ ChromeDriver path priority (Docker first)

This should fix all Chrome driver issues in Railway deployment!"

echo ""
echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Push completed!"
echo "🕐 Railway will start building automatically in 1-2 minutes..."
echo "📊 Check Railway dashboard for build logs."

echo ""
echo "🎯 Expected logs in Railway:"
echo "   🐳 Docker Build Starting..."
echo "   ✅ Chromium installed"
echo "   ✅ ChromeDriver ready"
echo "   🐧 Railway Production Mode - Ultimate Chrome Setup"
echo "   ✅ Chrome binary found: /usr/bin/chromium"
echo "   ✅ System ChromeDriver success"
echo "   ✅ Chrome browser başarıyla başlatıldı"

echo ""
echo "🔥 Ready for Excel testing after deploy!"
