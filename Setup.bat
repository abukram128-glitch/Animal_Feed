@echo off
echo ============================================
echo منصة تاور العلمية - تثبيت المتطلبات
echo ============================================

echo.
echo 📦 تثبيت المكتبات المطلوبة...
pip install -r requirements.txt

echo.
echo 📸 تثبيت مكتبات OCR...
pip install pytesseract Pillow

echo.
echo ✅ تم الانتهاء من التثبيت!
echo 🚀 لتشغيل المنصة: streamlit run tower_scientific_platform.py

pause
