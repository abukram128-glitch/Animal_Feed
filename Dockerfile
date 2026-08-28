# Dockerfile لمنصة تاور العلمية
FROM python:3.9-slim

# تعيين مجلد العمل
WORKDIR /app

# تثبيت Tesseract و dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    tesseract-ocr-deu \
    tesseract-ocr-nld \
    libtesseract-dev \
    libleptonica-dev \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات
COPY requirements.txt .

# تثبيت المكتبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الملفات
COPY . .

# فتح المنفذ
EXPOSE 8501

# تشغيل التطبيق
CMD ["streamlit", "run", "tower_scientific_platform.py", "--server.port=8501", "--server.address=0.0.0.0"]
