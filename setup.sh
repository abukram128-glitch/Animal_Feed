#!/bin/bash

echo "============================================"
echo "🌾 منصة تاور العلمية - تثبيت المتطلبات"
echo "============================================"

echo ""
echo "📦 1. تثبيت المكتبات المطلوبة..."
pip install -r requirements.txt

echo ""
echo "📸 2. تثبيت مكتبات OCR..."
pip install pytesseract Pillow

echo ""
echo "🔍 3. تثبيت Tesseract OCR..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-fra tesseract-ocr-deu tesseract-ocr-nld
elif [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew &> /dev/null; then
        brew install tesseract tesseract-lang
    else
        echo "⚠️ يرجى تثبيت Homebrew أولاً"
        echo "ثم قم بتشغيل: brew install tesseract tesseract-lang"
    fi
fi

echo ""
echo "✅ تم الانتهاء من التثبيت!"
echo "🚀 لتشغيل المنصة: streamlit run tower_scientific_platform.py"
