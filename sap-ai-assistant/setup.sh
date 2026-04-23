#!/bin/bash

# SAP ABAP AI Assistant - Kurulum ve Çalıştırma Scripti

echo "🚀 SAP ABAP AI Assistant Kurulumu"
echo "=================================="

# Python bağımlılıklarını kontrol et
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 bulunamadı. Lütfen Python 3.8+ yükleyin."
    exit 1
fi

echo "✓ Python versiyonu: $(python3 --version)"

# NVIDIA GPU kontrolü
if command -v nvidia-smi &> /dev/null; then
    echo "✓ NVIDIA GPU tespit edildi:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo "⚠️  NVIDIA GPU bulunamadı. Model CPU üzerinde çalışacak (yavaş)."
fi

# Backend bağımlılıklarını yükle
echo ""
echo "📦 Backend bağımlılıkları yükleniyor..."
cd backend
pip3 install -r requirements.txt

# Model dizinini oluştur
echo ""
echo "📁 Model dizini oluşturuluyor..."
mkdir -p ../models

# Qwen modelini indir (isteğe bağlı)
echo ""
read -p "Qwen Coder modelini indirmek ister misiniz? (7GB+ disk alanı gerekir) (y/n): " download_model
if [ "$download_model" = "y" ]; then
    echo "🤖 Qwen Coder modeli indiriliyor..."
    if command -v git-lfs &> /dev/null; then
        git lfs install
        git clone https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct ../models/Qwen-Coder-7B-Instruct
    else
        echo "❌ git-lfs bulunamadı. Lütfen git-lfs yükleyin veya modeli manuel indirin."
    fi
fi

# .env dosyası oluştur
echo ""
echo "⚙️  Ortam değişkenleri yapılandırılıyor..."
cat > .env << EOF
MODEL_PATH=../models/Qwen-Coder-7B-Instruct
SAP_HOST=localhost
SAP_PORT=3300
SAP_CLIENT=100
SAP_USER=
SAP_PASSWORD=
AZURE_DEVOPS_REPO=
EOF

echo "✓ .env dosyası oluşturuldu. Lütfen SAP bilgilerini doldurun."

# Servisleri başlat
echo ""
echo "🎯 Servisler başlatılıyor..."
echo ""
echo "Backend http://localhost:8000 adresinde çalışacak"
echo "Frontend'i açmak için: python3 -m http.server 3000 (frontend dizininde)"
echo ""
echo "Backend'i başlatmak için:"
echo "  cd backend && python3 main.py"
echo ""
echo "✅ Kurulum tamamlandı!"
