# ============================================================================
# ملف تثبيت متطلبات منصة تاور العلمية
# ============================================================================

import subprocess
import sys
import os
import platform

def install_requirements():
    """تثبيت جميع المتطلبات اللازمة للمنصة"""
    
    print("=" * 60)
    print("🌾 منصة تاور العلمية - تثبيت المتطلبات")
    print("=" * 60)
    
    # التحقق من نظام التشغيل
    system = platform.system()
    print(f"🖥️ نظام التشغيل: {system}")
    
    # 1. تثبيت المكتبات الأساسية
    print("\n📦 1. تثبيت المكتبات الأساسية...")
    libraries = [
        "streamlit",
        "pandas",
        "numpy", 
        "scipy",
        "plotly",
        "matplotlib",
        "reportlab",
        "arabic-reshaper",
        "python-bidi",
        "scikit-learn",
        "altair",
        "qrcode",
        "gTTS"
    ]
    
    for lib in libraries:
        print(f"   - تثبيت {lib}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
        except Exception as e:
            print(f"   ❌ خطأ في تثبيت {lib}: {e}")
    
    # 2. تثبيت مكتبات OCR
    print("\n📸 2. تثبيت مكتبات OCR...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytesseract", "Pillow"])
        print("   ✅ تم تثبيت pytesseract و Pillow")
    except Exception as e:
        print(f"   ❌ خطأ في تثبيت مكتبات OCR: {e}")
    
    # 3. تثبيت Tesseract حسب نظام التشغيل
    print("\n🔍 3. تثبيت Tesseract OCR...")
    
    if system == "Windows":
        print("   ⚠️ لـ Windows: قم بتحميل وتثبيت Tesseract من:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        print("   ثم أضف مسار التثبيت إلى متغيرات البيئة PATH")
        
    elif system == "Linux":
        print("   🐧 تثبيت Tesseract على Linux...")
        try:
            subprocess.check_call(["sudo", "apt-get", "update"])
            subprocess.check_call(["sudo", "apt-get", "install", "-y", "tesseract-ocr", "tesseract-ocr-eng", "tesseract-ocr-fra", "tesseract-ocr-deu", "tesseract-ocr-nld"])
            print("   ✅ تم تثبيت Tesseract بنجاح")
        except Exception as e:
            print(f"   ❌ خطأ في تثبيت Tesseract: {e}")
            print("   يمكنك التثبيت يدوياً باستخدام: sudo apt-get install tesseract-ocr")
            
    elif system == "Darwin":  # Mac
        print("   🍎 تثبيت Tesseract على Mac...")
        try:
            # التحقق من وجود Homebrew
            subprocess.check_call(["brew", "--version"])
            subprocess.check_call(["brew", "install", "tesseract"])
            subprocess.check_call(["brew", "install", "tesseract-lang"])
            print("   ✅ تم تثبيت Tesseract بنجاح")
        except:
            print("   ⚠️ يرجى تثبيت Homebrew أولاً: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            print("   ثم قم بتشغيل: brew install tesseract tesseract-lang")
    
    # 4. التحقق من التثبيت
    print("\n✅ 4. التحقق من التثبيت...")
    
    try:
        import streamlit
        print(f"   ✅ Streamlit: {streamlit.__version__}")
    except:
        print("   ❌ Streamlit غير مثبت")
    
    try:
        import pytesseract
        print("   ✅ pytesseract مثبت")
    except:
        print("   ⚠️ pytesseract غير مثبت")
    
    try:
        import PIL
        print(f"   ✅ Pillow: {PIL.__version__}")
    except:
        print("   ❌ Pillow غير مثبت")
    
    print("\n" + "=" * 60)
    print("🎉 تم الانتهاء من تثبيت المتطلبات!")
    print("🚀 لتشغيل المنصة: streamlit run tower_scientific_platform.py")
    print("=" * 60)

if __name__ == "__main__":
    install_requirements()
