# ============================================================================
# منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف
# الإصدار: 2.1 (مع وحدة تغذية الخيل والتحقق من المتطلبات)
# المشرف: الاختصاصي م. عبد القادر إسماعيل تاور
# ============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import json
import os
import base64
import smtplib
import time
import urllib.parse
import re
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scipy.optimize import linprog
from scipy.spatial import ConvexHull
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
from datetime import datetime, timedelta
import hashlib
import secrets
from functools import lru_cache
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 0. التحقق من المتطلبات (تمت الإضافة)
# ============================================================

def check_requirements():
    """
    التحقق من تثبيت جميع المتطلبات الضرورية لتشغيل المنصة
    تعرض تقريراً مفصلاً عن المكتبات المثبتة والمفقودة
    """
    
    print("=" * 70)
    print("🔍 التحقق من متطلبات منصة تاور العلمية...")
    print("=" * 70)
    
    # المكتبات الأساسية (إلزامية للتشغيل)
    required_libraries = {
        "streamlit": "Streamlit - واجهة المستخدم",
        "pandas": "Pandas - معالجة البيانات",
        "numpy": "NumPy - الحسابات العددية",
        "scipy": "SciPy - الاستمثال الخطي",
        "plotly": "Plotly - الرسوم البيانية التفاعلية",
        "reportlab": "ReportLab - إنشاء ملفات PDF",
        "arabic_reshaper": "Arabic Reshaper - معالجة النصوص العربية",
        "bidi": "Bidi - عرض النصوص العربية",
        "matplotlib": "Matplotlib - الرسوم البيانية",
        "sklearn": "Scikit-learn - التحليلات المتقدمة",
        "altair": "Altair - الرسوم البيانية الإحصائية",
        "qrcode": "QR Code - إنشاء رموز QR"
    }
    
    # المكتبات الاختيارية (وظائف إضافية)
    optional_libraries = {
        "pytesseract": "Tesseract OCR - قراءة بطاقات الأعلاف",
        "PIL": "Pillow - معالجة الصور",
        "gtts": "gTTS - تحويل النص إلى صوت"
    }
    
    # قوائم للمكتبات المفقودة
    missing_required = []
    missing_optional = []
    installed_required = []
    installed_optional = []
    
    print("\n📚 المكتبات الأساسية:")
    print("-" * 50)
    
    # التحقق من المكتبات الأساسية
    for lib, description in required_libraries.items():
        try:
            __import__(lib)
            installed_required.append(lib)
            print(f"   ✅ {lib:<20} - {description}")
        except ImportError:
            missing_required.append(lib)
            print(f"   ❌ {lib:<20} - {description} (غير مثبتة)")
    
    print("\n📚 المكتبات الاختيارية:")
    print("-" * 50)
    
    # التحقق من المكتبات الاختيارية
    for lib, description in optional_libraries.items():
        try:
            __import__(lib)
            installed_optional.append(lib)
            print(f"   ✅ {lib:<20} - {description}")
        except ImportError:
            missing_optional.append(lib)
            print(f"   ⚠️ {lib:<20} - {description} (غير مثبتة - اختيارية)")
    
    # ============================================================
    # التحقق من Tesseract OCR (نظام التشغيل)
    # ============================================================
    print("\n🔍 التحقق من Tesseract OCR:")
    print("-" * 50)
    
    import platform
    system = platform.system()
    tesseract_installed = False
    
    if system == "Windows":
        # التحقق من وجود Tesseract في المسارات الشائعة
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
        ]
        for path in common_paths:
            if os.path.exists(path):
                tesseract_installed = True
                print(f"   ✅ Tesseract موجود في: {path}")
                break
        if not tesseract_installed:
            print("   ⚠️ Tesseract غير مثبت. قم بتحميله من:")
            print("      https://github.com/UB-Mannheim/tesseract/wiki")
            
    elif system == "Linux":
        # التحقق من وجود Tesseract على Linux
        try:
            import subprocess
            result = subprocess.run(["which", "tesseract"], capture_output=True, text=True)
            if result.returncode == 0:
                tesseract_installed = True
                print(f"   ✅ Tesseract موجود في: {result.stdout.strip()}")
            else:
                print("   ⚠️ Tesseract غير مثبت. قم بتشغيل:")
                print("      sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-fra tesseract-ocr-deu tesseract-ocr-nld")
        except:
            print("   ⚠️ تعذر التحقق من Tesseract")
            
    elif system == "Darwin":  # Mac
        try:
            import subprocess
            result = subprocess.run(["which", "tesseract"], capture_output=True, text=True)
            if result.returncode == 0:
                tesseract_installed = True
                print(f"   ✅ Tesseract موجود في: {result.stdout.strip()}")
            else:
                print("   ⚠️ Tesseract غير مثبت. قم بتشغيل:")
                print("      brew install tesseract tesseract-lang")
        except:
            print("   ⚠️ تعذر التحقق من Tesseract")
    
    # ============================================================
    # تقرير نهائي
    # ============================================================
    print("\n" + "=" * 70)
    print("📊 تقرير التحقق النهائي:")
    print("=" * 70)
    
    total_required = len(required_libraries)
    total_installed = len(installed_required)
    
    print(f"\n📦 المكتبات الأساسية: {total_installed}/{total_required} مثبتة")
    
    if missing_required:
        print("\n❌ المكتبات المفقودة (إلزامية):")
        for lib in missing_required:
            print(f"   - {lib}")
        print("\nلتثبيت جميع المتطلبات، قم بتشغيل:")
        print("   pip install -r requirements.txt")
        print("\nأو قم بتشغيل ملف التثبيت التلقائي:")
        if system == "Windows":
            print("   setup.bat")
        else:
            print("   ./setup.sh")
        return False
    else:
        print("\n✅ جميع المكتبات الأساسية مثبتة بنجاح!")
    
    if missing_optional:
        print("\n⚠️ المكتبات الاختيارية المفقودة:")
        for lib in missing_optional:
            print(f"   - {lib}")
        print("\nبعض الوظائف قد لا تعمل بدون هذه المكتبات.")
    
    if not tesseract_installed and "pytesseract" in installed_optional:
        print("\n⚠️ Tesseract غير مثبت. ميزة OCR لن تعمل.")
        print("   يرجى تثبيت Tesseract حسب نظام التشغيل.")
    
    print("\n" + "=" * 70)
    print("🚀 يمكنك تشغيل المنصة الآن!")
    print("   streamlit run tower_scientific_platform.py")
    print("=" * 70)
    
    return True

# ============================================================
# تنفيذ التحقق عند بدء البرنامج (مع إمكانية تخطي)
# ============================================================

# التحقق من عدم تشغيل التحقق في بيئة Streamlit (لتجنب التكرار)
if not hasattr(st, 'session_state') or 'requirements_checked' not in st.session_state:
    # تشغيل التحقق مرة واحدة فقط
    requirements_ok = check_requirements()
    if hasattr(st, 'session_state'):
        st.session_state['requirements_checked'] = True
        st.session_state['requirements_ok'] = requirements_ok
    
    # إذا كانت المكتبات الأساسية مفقودة، عرض تحذير في الواجهة
    if not requirements_ok and hasattr(st, 'session_state'):
        st.warning("""
        ⚠️ بعض المكتبات الأساسية غير مثبتة!
        
        يرجى تثبيت المتطلبات بتشغيل:
        ```bash
        pip install -r requirements.txt
        ```
        
        أو استخدام ملف التثبيت التلقائي.
        """)

# ===== مكتبة الصوت (gTTS) =====
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# ===== مكتبات PDF واللغة العربية =====
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus.flowables import HRFlowable
import arabic_reshaper
from bidi.algorithm import get_display
import io
import qrcode
from PIL import Image as PILImage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.font_manager as fm

# ===== مكتبة OCR لقراءة بطاقات الأعلاف =====
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ============================================================
# دالة عرض حالة المتطلبات في الواجهة (اختياري)
# ============================================================

def render_requirements_status():
    """عرض حالة المتطلبات في شريط جانبي أو في الواجهة"""
    
    with st.expander("🔍 حالة المتطلبات", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**المكتبات الأساسية:**")
            required = ["streamlit", "pandas", "numpy", "scipy", "plotly", "reportlab", "arabic_reshaper", "bidi"]
            for lib in required:
                try:
                    __import__(lib)
                    st.success(f"✅ {lib}")
                except ImportError:
                    st.error(f"❌ {lib}")
        
        with col2:
            st.markdown("**المكتبات الاختيارية:**")
            optional = ["pytesseract", "PIL", "gtts"]
            for lib in optional:
                try:
                    __import__(lib)
                    st.success(f"✅ {lib}")
                except ImportError:
                    st.warning(f"⚠️ {lib}")
        
        # حالة Tesseract
        st.markdown("**Tesseract OCR:**")
        if OCR_AVAILABLE:
            try:
                import platform
                import subprocess
                system = platform.system()
                if system == "Windows":
                    paths = [r"C:\Program Files\Tesseract-OCR\tesseract.exe", r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"]
                    tesseract_found = any(os.path.exists(p) for p in paths)
                else:
                    result = subprocess.run(["which", "tesseract"], capture_output=True, text=True)
                    tesseract_found = result.returncode == 0
                
                if tesseract_found:
                    st.success("✅ Tesseract مثبت")
                else:
                    st.warning("⚠️ Tesseract غير مثبت")
            except:
                st.warning("⚠️ تعذر التحقق من Tesseract")
        else:
            st.warning("⚠️ pytesseract غير مثبت")

# ===== دوال الصوت =====
def play_welcome_audio():
    """تشغيل صوت ترحيبي (توليد تلقائي أو ملف موجود)."""
    audio_file = "welcome.mp3"
    if not os.path.exists(audio_file):
        if GTTS_AVAILABLE:
            try:
                tts = gTTS(
                    text="مرحباً بك في منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف، تحت إشراف الاختصاصي عبد القادر إسماعيل تاور",
                    lang="ar"
                )
                tts.save(audio_file)
            except Exception as e:
                st.warning(f"⚠️ تعذر توليد الصوت: {e}")
                return
        else:
            st.warning("⚠️ مكتبة gTTS غير مثبتة، يرجى تثبيتها: pip install gtts")
            return
    if os.path.exists(audio_file):
        try:
            with open(audio_file, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode()
            st.components.v1.html(
                f'<audio autoplay><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>',
                height=0
            )
        except Exception as e:
            st.warning(f"⚠️ تعذر تشغيل الصوت: {e}")

# ============================================================
# 1. نظام قاعدة البيانات المحلية (SQLite)
# ============================================================
import sqlite3
from dataclasses import dataclass, asdict

class DatabaseManager:
    def __init__(self, db_path="tower_platform.db"):
        self.db_path = db_path
        self._init_db()
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id TEXT PRIMARY KEY,
                      username TEXT UNIQUE,
                      password_hash TEXT,
                      role TEXT,
                      full_name TEXT,
                      email TEXT,
                      phone TEXT,
                      created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS farm_cycles
                     (cycle_id TEXT PRIMARY KEY,
                      farm_name TEXT,
                      animal_type TEXT,
                      breed TEXT,
                      start_date TEXT,
                      end_date TEXT,
                      initial_birds INTEGER,
                      final_weight_kg REAL,
                      total_feed_kg REAL,
                      total_dead INTEGER,
                      total_culled INTEGER,
                      fcr REAL,
                      adg REAL,
                      epef REAL,
                      mortality_rate REAL,
                      notes TEXT,
                      created_by TEXT,
                      created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas
                     (formula_id TEXT PRIMARY KEY,
                      formula_name TEXT,
                      animal_type TEXT,
                      target_dp REAL,
                      target_se REAL,
                      ingredients TEXT,
                      total_cost REAL,
                      created_by TEXT,
                      created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS invoices
                     (invoice_id TEXT PRIMARY KEY,
                      customer_name TEXT,
                      formula_id TEXT,
                      quantity_ton REAL,
                      unit_price REAL,
                      total_price REAL,
                      status TEXT,
                      created_by TEXT,
                      created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS price_history
                     (record_id TEXT PRIMARY KEY,
                      ingredient_name TEXT,
                      price REAL,
                      currency TEXT,
                      country TEXT,
                      city TEXT,
                      record_date TEXT,
                      recorded_by TEXT)''')
        # جدول جديد لتغذية الخيل
        c.execute('''CREATE TABLE IF NOT EXISTS horse_feeds
                     (feed_id TEXT PRIMARY KEY,
                      feed_name TEXT,
                      brand TEXT,
                      protein REAL,
                      fiber REAL,
                      fat REAL,
                      starch REAL,
                      sugar REAL,
                      min_rate REAL,
                      max_rate REAL,
                      is_gastric_safe INTEGER,
                      notes TEXT,
                      created_date TEXT)''')
        conn.commit()
        conn.close()
    def execute_query(self, query: str, params: tuple = ()):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        result = c.execute(query, params)
        conn.commit()
        data = result.fetchall()
        conn.close()
        return data
    def insert_record(self, table: str, data: dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        c.execute(query, list(data.values()))
        conn.commit()
        conn.close()

# ============================================================
# 2. نظام المصادقة
# ============================================================
class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self._create_default_admin()
    def _create_default_admin(self):
        users = self.db.execute_query("SELECT * FROM users WHERE username='admin'")
        if not users:
            self.create_user('admin', 'admin123', 'owner', 'مدير النظام', 'admin@tower.com', '+249123456789')
    def create_user(self, username, password, role, full_name, email, phone):
        user_id = secrets.token_hex(16)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        data = {
            'user_id': user_id,
            'username': username,
            'password_hash': password_hash,
            'role': role,
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'created_date': datetime.now().isoformat()
        }
        self.db.insert_record('users', data)
        return user_id
    def authenticate(self, username, password):
        users = self.db.execute_query("SELECT * FROM users WHERE username=?", (username,))
        if users:
            user = users[0]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user[2] == password_hash:
                return {
                    'user_id': user[0],
                    'username': user[1],
                    'role': user[3],
                    'full_name': user[4],
                    'email': user[5],
                    'phone': user[6]
                }
        return None

# ============================================================
# 3. نظام التنبؤ بالأسعار (مبسط)
# ============================================================
class PricePredictor:
    def __init__(self):
        self.db = DatabaseManager()
    def get_ingredient_prices(self, ingredient_name, days=30):
        results = self.db.execute_query(
            "SELECT * FROM price_history WHERE ingredient_name=? ORDER BY record_date DESC LIMIT ?",
            (ingredient_name, days)
        )
        return [{
            'record_id': r[0],
            'ingredient_name': r[1],
            'price': r[2],
            'currency': r[3],
            'country': r[4],
            'city': r[5],
            'record_date': r[6]
        } for r in results]
    def predict_price(self, ingredient_name, days_ahead=7):
        prices = self.get_ingredient_prices(ingredient_name, 30)
        if len(prices) < 5:
            return {'prediction': None, 'confidence': 0}
        price_list = [p['price'] for p in prices]
        weights = np.array(range(1, len(price_list) + 1))
        weighted_avg = np.average(price_list, weights=weights)
        trend = (price_list[0] - price_list[-1]) / len(price_list) if len(price_list) > 1 else 0
        prediction = weighted_avg + (trend * days_ahead)
        return {
            'prediction': max(0, prediction),
            'confidence': min(1, len(price_list) / 30),
            'current_price': price_list[0] if price_list else None,
            'trend': 'up' if trend > 0 else 'down' if trend < 0 else 'stable'
        }

# ============================================================
# 4. نظام المراجع العلمية
# ============================================================
class ScientificReferenceSystem:
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان",
            "references": [
                {"id": "REF001", "authors": "McDonald, P., Edwards, R.A., Greenhalgh, J.F.D., Morgan, C.A.",
                 "year": 2011, "title": "Animal Nutrition", "publisher": "Pearson Education",
                 "edition": "7th Edition", "isbn": "978-1408204238",
                 "summary": "المرجع الأساسي في تغذية الحيوان، يغطي جميع جوانب التغذية من الهضم إلى متطلبات العناصر الغذائية."}
            ]
        },
        "equine_nutrition": {
            "title": "تغذية الخيول",
            "references": [
                {"id": "REF015", "authors": "NRC (National Research Council)",
                 "year": 2007, "title": "Nutrient Requirements of Horses",
                 "publisher": "National Academies Press", "edition": "6th Revised Edition",
                 "isbn": "978-0309102124", "summary": "المرجع الأساسي في تغذية الخيول ومتطلباتها الغذائية."},
                {"id": "REF016", "authors": "Frape, D.",
                 "year": 2010, "title": "Equine Nutrition and Feeding",
                 "publisher": "Wiley-Blackwell", "edition": "4th Edition",
                 "summary": "دليل شامل لتغذية الخيول وإدارة العلائق."}
            ]
        }
    }
    KNOWLEDGE_BASE = {
        "تغذية الخيول": {
            "answer": "تتطلب الخيول نظاماً غذائياً متوازناً يعتمد على الأعلاف الخشنة (الدريس) كمصدر أساسي، مع إضافة مركزات حسب مستوى النشاط. يجب مراعاة نسبة النشا والسكر لتجنب مشاكل الجهاز الهضمي.",
            "reference": "REF015",
            "simplified": "الخيول تحتاج إلى علف خشن بنسبة 1.5% من وزن الجسم يومياً، مع إضافة مركزات حسب النشاط."
        },
        "قرحة المعدة عند الخيول": {
            "answer": "قرحة المعدة من المشاكل الشائعة عند الخيول، خاصة رياضية الأداء. يوصى بتقليل النشا والسكر في العلف، وتقديم وجبات صغيرة متعددة، واستخدام أعلاف عالية الألياف.",
            "reference": "REF016",
            "simplified": "لتجنب قرحة المعدة، قلل النشا والسكر، وقدم وجبات صغيرة، واستخدم أعلاف غنية بالألياف."
        }
    }
    @staticmethod
    def get_reference(ref_id):
        for category in ScientificReferenceSystem.REFERENCES.values():
            for ref in category.get("references", []):
                if ref.get("id") == ref_id:
                    return ref
        return None
    @staticmethod
    def get_knowledge_answer(question):
        for key, value in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            if key in question:
                ref = ScientificReferenceSystem.get_reference(value.get("reference", ""))
                return {
                    "answer": value["answer"],
                    "simplified": value.get("simplified", value["answer"]),
                    "reference": ref
                }
        return None

# ============================================================
# 5. وحدة تغذية الخيل (المدمجة)
# ============================================================

@dataclass
class FeedProduct:
    name: str
    brand: str
    protein: float
    fiber: float
    fat: float
    starch: Optional[float]
    sugar: Optional[float]
    min_rate: float  # كجم لكل 100 كجم وزن جسم
    max_rate: float
    is_gastric_safe: bool
    notes: str

# قاعدة بيانات المنتجات التجارية للخيول
PRODUCTS_DB: Dict[str, FeedProduct] = {
    "HAVENS DraversBrok": FeedProduct(
        name="DraversBrok", brand="HAVENS",
        protein=12.5, fiber=10.0, fat=4.0, starch=28.0, sugar=5.0,
        min_rate=0.2, max_rate=1.0, is_gastric_safe=False,
        notes="مناسب للأداء الرياضي العام وبناء العضلات والصيانة."
    ),
    "HAVENS Gastro Cube": FeedProduct(
        name="Gastro Cube", brand="HAVENS",
        protein=11.5, fiber=18.0, fat=6.0, starch=8.0, sugar=4.0,
        min_rate=0.3, max_rate=0.8, is_gastric_safe=True,
        notes="تركيبة خافضة للنشا وعالية الألياف مخصصة لحساسية المعدة والقرحة."
    ),
    "Equine Senior": FeedProduct(
        name="Senior Feed", brand="Equine",
        protein=14.0, fiber=16.0, fat=8.0, starch=12.0, sugar=5.0,
        min_rate=0.3, max_rate=0.7, is_gastric_safe=True,
        notes="مخصص للخيول المسنة، سهل الهضم، غني بالألياف والدهون."
    ),
    "Performance Plus": FeedProduct(
        name="Performance Plus", brand="Equine",
        protein=16.0, fiber=8.0, fat=10.0, starch=25.0, sugar=6.0,
        min_rate=0.5, max_rate=1.2, is_gastric_safe=False,
        notes="تركيبة عالية الطاقة للأداء الرياضي المكثف."
    )
}

class OCRFeedParser:
    @staticmethod
    def parse_image(image_file) -> Dict[str, Any]:
        """استخراج القيم التغذوية من الصورة المرفوعة"""
        text = ""
        if OCR_AVAILABLE and pytesseract and PILImage:
            try:
                img = PILImage.open(image_file)
                text = pytesseract.image_to_string(img, lang='eng+fra+deu+nld')
            except Exception as e:
                text = f"خطأ في OCR: {str(e)}"
        else:
            # نص افتراضي محاكى في حالة عدم تثبيت Tesseract
            text = "HAVENS Gastro Cube Crude Protein 11.5% Crude Fibre 18.0% Starch 8.0% Sensitive Stomach"

        # استخراج القيم باستخدام التعبيرات النمطية (Regex)
        return {
            "protein": OCRFeedParser._extract_num(r"(?:protein|eiwit|proteine)[\s:]*([0-9]+[.,]?[0-9]*)\s*%", text),
            "fiber": OCRFeedParser._extract_num(r"(?:fibre|fiber|celstof|rohfaser)[\s:]*([0-9]+[.,]?[0-9]*)\s*%", text),
            "starch": OCRFeedParser._extract_num(r"(?:starch|zetmeel|amidon|starke)[\s:]*([0-9]+[.,]?[0-9]*)\s*%", text),
            "is_sensitive": bool(re.search(r"(?:sensitive|gastro|maag|معدة|قرحة)", text, re.IGNORECASE)),
            "raw_text": text
        }

    @staticmethod
    def _extract_num(pattern: str, text: str) -> Optional[float]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(',', '.'))
            except ValueError:
                return None
        return None

class EquineNutritionEngine:
    @staticmethod
    def calculate_forage_requirement(weight_kg: float) -> float:
        """حساب الحد الأدنى للعلف الخشن (1.5% من وزن الجسم)"""
        return weight_kg * 0.015
    
    @staticmethod
    def calculate_concentrate_range(weight_kg: float, activity_level: str) -> Tuple[float, float]:
        """حساب نطاق العلف المركز حسب النشاط"""
        if "صيانة" in activity_level or "خفيف" in activity_level:
            rate_min, rate_max = 0.2, 0.5
        else:
            rate_min, rate_max = 0.5, 1.0
        return (rate_min * (weight_kg / 100.0), rate_max * (weight_kg / 100.0))
    
    @staticmethod
    def get_meal_frequency(concentrate_kg: float) -> int:
        """تحديد عدد الوجبات اليومية حسب كمية المركزات"""
        if concentrate_kg > 3.0:
            return 4
        elif concentrate_kg > 2.0:
            return 3
        else:
            return 2
    
    @staticmethod
    def evaluate_gastric_risk(starch_percent: float, is_gastric_safe: bool, has_ulcer: bool) -> Dict:
        """تقييم خطر القرحة المعدية"""
        risk_level = "منخفض"
        recommendation = "العلف مناسب للخيول ذات المعدة الحساسة."
        
        if has_ulcer and not is_gastric_safe:
            risk_level = "مرتفع"
            recommendation = "⚠️ هذا العلف غير مناسب للخيول المصابة بقرحة المعدة. يوصى باستخدام علف منخفض النشا (أقل من 12%)."
        elif has_ulcer and is_gastric_safe:
            risk_level = "منخفض"
            recommendation = "✅ العلف مناسب للخيول ذات المعدة الحساسة."
        elif not has_ulcer and starch_percent > 15:
            risk_level = "متوسط"
            recommendation = "⚠️ نسبة النشا مرتفعة نسبياً. راقب علامات المغص أو الانزعاج الهضمي."
        
        return {
            "risk_level": risk_level,
            "recommendation": recommendation,
            "starch_percent": starch_percent
        }

# ============================================================
# 6. إعدادات المنصة
# ============================================================
st.set_page_config(
    page_title="منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def init_caching_system():
    return {"cache_hits": 0, "cache_misses": 0, "last_cleanup": datetime.now()}
CACHE_SYSTEM = init_caching_system()

CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"
SENDER_PASSWORD = "oynz rdli tsdy ekdq"
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"

@st.cache_data(ttl=3600)
def get_image_base64(paths):
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode()
            except Exception:
                pass
    return None
img_base64 = get_image_base64(PHOTO_OPTIONS)

def send_code_to_mail(receiver_email, attachment_type="full"):
    if SENDER_EMAIL == "YOUR_EMAIL@gmail.com" or not SENDER_PASSWORD:
        st.error("⚠️ خطأ إعدادات: يرجى تحديث بيانات الـ SMTP داخل السورس كود أولاً.")
        return False
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود الكامل والمطور - منصة تاور العلمية"
    body = """السلام عليكم م. عبد القادر،

مرفق مع هذه الرسالة النسخة البرمجية الكاملة والمستقرة لمنصتكم الذكية."""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        try:
            current_file = __file__
            with open(current_file, "r", encoding="utf-8") as f:
                code_content = f.read()
        except NameError:
            code_content = "# كود المنصة مأرشيف داخلياً\n"
        file_hash = hashlib.md5(code_content.encode()).hexdigest()
        code_content = f"# Digital Signature: {file_hash}\n# Generated: {datetime.now().isoformat()}\n\n{code_content}"
        attachment = MIMEText(code_content, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', filename="tower_scientific_platform.py")
        msg.attach(attachment)
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ فشل الإرسال بسبب: {e}")
        return False

class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=1000)
    def fix_arabic_text(text):
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text

arabic_processor = ArabicTextProcessor()

# ============================================================
# 7. مولد PDF
# ============================================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        if os.path.exists("Amiri-Regular.ttf"):
            try:
                pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
                self.font_name = 'Amiri'
            except:
                pass
    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, include_charts=True):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        def p(text, size=12, align=TA_RIGHT, color=HexColor('#000000')):
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, ParagraphStyle('style', fontName=self.font_name, fontSize=size, alignment=align, textColor=color, spaceAfter=6, leading=size*1.5))
        story.append(p("تقرير فني شامل - منصة تاور العلمية", size=22, align=TA_CENTER, color=HexColor('#1b5e20')))
        story.append(Spacer(1, 12))
        for line in [f"المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور", f"الموقع الجغرافي: {city}", f"الفصيل المستهدف: {breed}", f"تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"]:
            story.append(p(line, size=11))
        story.append(Spacer(1, 15))
        tdata = [
            [arabic_processor.fix_arabic_text('المعيار'), arabic_processor.fix_arabic_text('القيمة')],
            [arabic_processor.fix_arabic_text('البروتين المهضوم (DP)'), f'{target_dp:.2f}%'],
            [arabic_processor.fix_arabic_text('معادل النشاء (SE)'), f'{computed_se:.2f} وحدة'],
            [arabic_processor.fix_arabic_text('التكلفة للطن'), f'${cost:.2f} ({local_cost:,.2f} {local_sym})']
        ]
        t = Table(tdata, colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('BACKGROUND', (0,1), (-1,-1), HexColor('#f5f5f5')),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#2e7d32')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        story.append(p("المقادير المعتمدة لتركيب الطن الواحد:", size=14, color=HexColor('#2e7d32')))
        story.append(Spacer(1, 10))
        ing_data = [[arabic_processor.fix_arabic_text('المكون'), arabic_processor.fix_arabic_text('النسبة %'), arabic_processor.fix_arabic_text('كجم/طن')]]
        for ing, pct in formula.items():
            ing_data.append([arabic_processor.fix_arabic_text(ing), f'{pct:.2f}%', f'{pct*10:.1f}'])
        t2 = Table(ing_data, colWidths=[200, 150, 150])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')]),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t2)
        story.append(Spacer(1, 15))
        if include_charts and len(formula) > 1:
            try:
                fig, ax = plt.subplots(figsize=(6, 3.5))
                names = list(formula.keys())
                vals = list(formula.values())
                colors = ['#1b5e20','#2e7d32','#388e3c','#43a047','#4caf50','#66bb6a']
                ax.pie(vals, labels=None, autopct='%1.1f%%', colors=colors[:len(names)])
                ax.legend([arabic_processor.fix_arabic_text(n) for n in names], title=arabic_processor.fix_arabic_text("المكونات"),
                         loc='center left', bbox_to_anchor=(1,0,0.5,1), fontsize=8)
                ax.set_title(arabic_processor.fix_arabic_text('توزيع المكونات'), fontsize=12)
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=400, height=230))
            except:
                pass
        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026 | تحت إشراف م. عبد القادر إسماعيل تاور", size=9, align=TA_CENTER, color=HexColor('#666666')))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# ============================================================
# 8. كلاس إدارة مزارع الدجاج اللاحم
# ============================================================
class BroilerFarmManager:
    @staticmethod
    def calculate_adg(current_weight_g, initial_weight_g, age_days):
        if age_days <= 0:
            return 0.0
        return (current_weight_g - initial_weight_g) / age_days
    @staticmethod
    def calculate_fcr(total_feed_kg, total_weight_gain_kg):
        if total_weight_gain_kg <= 0:
            return 0.0
        return total_feed_kg / total_weight_gain_kg
    @staticmethod
    def calculate_mortality_rate(dead_count, initial_count):
        if initial_count <= 0:
            return 0.0
        return (dead_count / initial_count) * 100.0
    @staticmethod
    def calculate_cull_rate(culled_count, initial_count):
        if initial_count <= 0:
            return 0.0
        return (culled_count / initial_count) * 100.0
    @staticmethod
    def calculate_livability(initial_count, dead_count):
        return 100.0 - BroilerFarmManager.calculate_mortality_rate(dead_count, initial_count)
    @staticmethod
    def calculate_epef(livability, body_weight_kg, age_days, fcr):
        if age_days <= 0 or fcr <= 0:
            return 0.0
        return (livability * body_weight_kg) / (age_days * fcr) * 100.0
    @staticmethod
    def get_temp_humidity_table():
        return pd.DataFrame({
            "العمر (يوم)": [1, 7, 14, 21, 28, 35, 42],
            "درجة الحرارة (مئوي)": [33, 30, 28, 26, 24, 22, 21],
            "الرطوبة النسبية (%)": [65, 65, 65, 60, 60, 55, 55]
        })

# ============================================================
# 9. مكتبة الأعلاف الكاملة
# ============================================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة الكبرى": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6}
    },
    "🌱 الأكساب وأمبازات مصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5}
    },
    "🚜 المخلفات الزراعية والصناعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5}
    },
    "🧪 الأحماض الأمينية البلورية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9}
    }
}

# نظام أسعار المدن
CITY_PRICES_FILE = "city_prices.json"
def load_city_prices():
    if os.path.exists(CITY_PRICES_FILE):
        try:
            with open(CITY_PRICES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}
def save_city_prices(data):
    with open(CITY_PRICES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

CITY_CUSTOM_PRICES = load_city_prices()

class InventoryManager:
    @staticmethod
    def initialize_inventory():
        if "inventory" not in st.session_state:
            st.session_state["inventory"] = {}
            for cat_name, items in BIG_FEEDS_LIBRARY.items():
                for ing in items:
                    st.session_state["inventory"][ing] = {
                        "quantity": 25.0,
                        "min_threshold": 5.0,
                        "unit": "طن",
                        "last_updated": datetime.now().isoformat(),
                        "price_history": [],
                        "supplier": "غير محدد"
                    }
    @staticmethod
    def check_stock_levels():
        warnings = {}
        for item, data in st.session_state["inventory"].items():
            qty = data if isinstance(data, (int, float)) else data["quantity"]
            threshold = 5.0 if isinstance(data, (int, float)) else data["min_threshold"]
            if qty <= 0:
                warnings[item] = "نفذ المخزون"
            elif qty < threshold:
                warnings[item] = "منخفض"
        return warnings

InventoryManager.initialize_inventory()

if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين / محسن ($)": 1350.0, "أبقار كنانة وبطانة محلية ($)": 900.0,
        "ضأن وستيرلنغ / محلي ($)": 180.0, "ماعز نوبي وصحراوي ($)": 130.0,
        "خيول عربية أصيلة وهجين ($)": 4500.0, "كتكوت لاحم عمر يوم ($)": 0.65, "دجاج بياض عمر البشاير ($)": 5.50
    }
if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري صافي ($)": 7.50, "كيلو لحم ضأن طازج ($)": 9.00,
        "كيلو لحم دجاج لاحم صافي ($)": 3.80, "طبق بيض مائدة 30 بيضة ($)": 4.20,
        "رطل / لتر حليب خام ($)": 0.90, "كيلو جبن أبيض محلي ($)": 5.00,
        "كيلو جبن جاف / شيدر ($)": 8.50
    }
if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = (
        "• [توجيه الاختصاصي م. عبد القادر إسماعيل تاور]: يرجى من جميع الزملاء إضافة تعليقاتهم هنا لتبادل الخبرات التركيبية.\n"
        "• [ملاحظة مختص]: تم مراجعة جودة كسب زهرة الشمس المتاح حالياً بالأسواق ونوصي بضبط ألياف الخيل بناءً عليه.\n"
    )

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG", "currency_name": "جنيه سوداني"},
    "LIBYA": {"rate": 4.80, "sym": "LYD", "currency_name": "دينار ليبي"},
    "مصر": {"rate": 48.0, "sym": "EGP", "currency_name": "جنيه مصري"},
    "باقي دول العالم / البورصة المفتوحة": {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"}
}

class MarketPriceEngine:
    @staticmethod
    @lru_cache(maxsize=128)
    def get_adjusted_market_data(country, state_or_region, city):
        feed_prices = {}
        for cat in BIG_FEEDS_LIBRARY.values():
            for ing in cat:
                feed_prices[ing] = 230.0
        base_prices = {
            "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0,
            "سورجم (فتريتة)": 195.0, "قمح محلي مصنّع": 240.0,
            "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا 44%": 440.0,
            "كسب فول صويا 48%": 480.0, "كسب عباد الشمس 36%": 310.0,
            "نخالة قمح (ردة)": 150.0, "البرسيم الجاف (الدريس)": 170.0, "مولاس قصب السكر": 120.0,
            "الحجر الجيري (بودرة بلاط)": 40.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0,
            "ملح الطعام": 30.0
        }
        feed_prices.update(base_prices)
        multiplier = 1.0
        if country == "السودان":
            multiplier = 1.15
        elif country == "LIBYA":
            multiplier = 1.10
        elif country == "مصر":
            multiplier = 1.04
        for k in feed_prices:
            feed_prices[k] *= multiplier
        return feed_prices

ANIMAL_IMAGES_RESOURCES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600",
    "سمان": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600"
}

if "active_formula" not in st.session_state: st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 12.0
if "active_se_tag" not in st.session_state: st.session_state["active_se_tag"] = 65.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_animal_img" not in st.session_state: st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES["عام"]
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0

# ============================================================
# 10. حالة الجلسة
# ============================================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "login_welcome_shown" not in st.session_state: st.session_state["login_welcome_shown"] = False
if "login_attempts" not in st.session_state: st.session_state["login_attempts"] = 0
if "last_login_time" not in st.session_state: st.session_state["last_login_time"] = None
if "session_token" not in st.session_state: st.session_state["session_token"] = None
if "broiler_farms" not in st.session_state:
    st.session_state["broiler_farms"] = {}
if "selected_farm" not in st.session_state:
    st.session_state["selected_farm"] = None
if "standard_vacc_schedule" not in st.session_state:
    st.session_state["standard_vacc_schedule"] = {
        1: {"type": "فيتامين", "name": "فيتامين AD3E", "dose": "1 مل/لتر ماء", "route": "مياه الشرب"},
        7: {"type": "لقاح", "name": "نيوكاسل (Lasota)", "dose": "قطرة عين", "route": "قطرة عين/أنف"},
        14: {"type": "لقاح", "name": "Gumboro (Intermediate)", "dose": "قطرة فم", "route": "مياه الشرب"},
        21: {"type": "دواء", "name": "مضاد كوكسيديا (Amprolium)", "dose": "1 جم/لتر", "route": "مياه الشرب لمدة 3 أيام"},
        28: {"type": "فيتامين", "name": "فيتامين C + E", "dose": "0.5 جم/لتر", "route": "مياه الشرب"},
        35: {"type": "لقاح", "name": "Gumboro booster", "dose": "قطرة فم", "route": "مياه الشرب"},
    }
if "whatsapp_alerts_sent" not in st.session_state:
    st.session_state["whatsapp_alerts_sent"] = {}
if "query_history" not in st.session_state:
    st.session_state["query_history"] = []
if "audio_played" not in st.session_state:
    st.session_state["audio_played"] = False

def send_whatsapp_broiler_alert(phone_number, message):
    encoded_msg = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_msg}"
    st.markdown(f"<div style='background:#e8f5e9; padding:10px; border-radius:8px; direction:ltr;'>📲 <b>تنبيه عبر واتساب:</b> <a href='{whatsapp_url}' target='_blank'>اضغط لإرسال الرسالة إلى {phone_number}</a><br>{message}</div>", unsafe_allow_html=True)

def check_and_alert_medications(farm_name, farm_data, current_age):
    phone = farm_data.get("owner_phone", WHATSAPP_NUMBER)
    schedule = st.session_state["standard_vacc_schedule"]
    alerts = []
    for age_day, item in schedule.items():
        if age_day == current_age:
            key = f"{farm_name}_{age_day}_{item['type']}_{item['name']}"
            if key not in st.session_state["whatsapp_alerts_sent"]:
                alert_msg = f"🔔 تنبيه لمزرعة {farm_name} (العمر {age_day} يوم):\n{item['type']} {item['name']} - الجرعة: {item['dose']} - طريقة الإعطاء: {item['route']}"
                send_whatsapp_broiler_alert(phone, alert_msg)
                st.session_state["whatsapp_alerts_sent"][key] = datetime.now().isoformat()
                alerts.append(alert_msg)
    if alerts:
        st.info(f"📢 تم إرسال {len(alerts)} تنبيه إلى المالك لليوم (العمر {current_age} يوم).")
    else:
        st.success("✅ لا توجد تحصينات أو أدوية مستحقة اليوم.")

# ============================================================
# 11. CSS المحسّن (ألوان ثابتة وواضحة)
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Tajawal:wght@400;500;700&display=swap');
    
    * {
        font-family: 'Cairo', 'Tajawal', sans-serif;
        color: #1a1a1a !important;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .stApp { 
        background: transparent; 
    }
    
    .main-box {
        background-color: rgba(255, 255, 255, 0.98);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18);
        margin-bottom: 50px;
        backdrop-filter: blur(5px);
    }
    
    h1, h2, h3, h4, h5, p, span, li, div, label, .stMarkdown, .stTextInput, .stNumberInput, .stSelectbox {
        color: #1a1a1a !important;
        text-shadow: none !important;
    }
    
    .formula-item {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(232,245,233,0.95) 100%);
        padding: 15px 20px;
        border-radius: 12px;
        margin-bottom: 10px;
        font-weight: bold;
        color: #1b5e20 !important;
        border-right: 5px solid #2e7d32;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        text-align: right;
        transition: transform 0.3s ease;
    }
    
    .formula-item:hover {
        transform: translateX(-5px);
        box-shadow: 0px 6px 20px rgba(0,0,0,0.15);
    }
    
    .section-title {
        color: #1b5e20 !important;
        border-right: 6px solid #2e7d32;
        padding-right: 15px;
        text-align: right;
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 20px;
        background: linear-gradient(to left, rgba(46,125,50,0.1), transparent);
        padding: 10px 15px;
        border-radius: 8px;
    }
    
    .sack-tag {
        border: 3px dashed #1b5e20;
        padding: 30px;
        border-radius: 15px;
        background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e9 100%);
        direction: rtl;
        text-align: right;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.1);
    }
    .sack-tag * {
        color: #1a1a1a !important;
    }
    
    .profile-img-style {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid #d4af37;
        box-shadow: 0px 6px 20px rgba(0,0,0,0.25);
        display: block;
        margin: 0 auto;
        transition: transform 0.3s ease;
    }
    
    .profile-img-style:hover {
        transform: scale(1.05);
    }
    
    .animal-banner-img {
        width: 100%;
        max-height: 200px;
        object-fit: cover;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 3px solid #2e7d32;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
    }
    
    .mini-left-signature {
        position: fixed;
        left: 20px;
        bottom: 20px;
        background: linear-gradient(135deg, #1b5e20, #2e7d32);
        color: white !important;
        padding: 8px 20px;
        font-size: 0.85rem;
        border-radius: 25px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
        z-index: 9999;
        direction: rtl;
        backdrop-filter: blur(5px);
    }
    .mini-left-signature * {
        color: white !important;
    }
    
    .stock-critical { 
        background: linear-gradient(135deg, #ffebee, #ffcdd2); 
        padding: 8px 12px; 
        border-radius: 8px; 
        color: #c62828 !important; 
        font-weight: bold;
        border: 1px solid #ef5350;
    }
    
    .stock-normal { 
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9); 
        padding: 8px 12px; 
        border-radius: 8px; 
        color: #2e7d32 !important;
        border: 1px solid #66bb6a;
    }
    
    .price-card {
        background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
        padding: 20px;
        border-radius: 12px;
        border-right: 5px solid #2e7d32;
        margin-bottom: 20px;
        direction: rtl;
        text-align: right;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    .price-card * {
        color: #1a1a1a !important;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        padding: 15px;
        border-radius: 12px;
        border-right: 5px solid #f57c00;
        margin-bottom: 15px;
        direction: rtl;
        text-align: right;
        color: #e65100 !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    .warning-card * {
        color: #e65100 !important;
    }
    
    .horse-card {
        background: linear-gradient(135deg, #e8eaf6, #c5cae9);
        padding: 20px;
        border-radius: 12px;
        border-right: 5px solid #3949ab;
        margin-bottom: 20px;
        direction: rtl;
        text-align: right;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    .horse-card * {
        color: #1a1a1a !important;
    }
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }
    .metric-card * {
        color: #1a1a1a !important;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 8px 30px rgba(0,0,0,0.15);
    }
    
    .stButton > button {
        color: #1a1a1a !important;
        background-color: #e8f5e9 !important;
        border: 1px solid #2e7d32 !important;
        font-weight: bold !important;
    }
    .stButton > button:hover {
        background-color: #c8e6c9 !important;
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        color: #1a1a1a !important;
        background-color: #ffffff !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        color: #1a1a1a !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #1b5e20 !important;
        font-weight: bold;
    }
    
    .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
        color: #1a1a1a !important;
    }
    .stAlert * {
        color: #1a1a1a !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 12. بوابة الدخول
# ============================================================
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300

if not st.session_state["approved"]:
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        if st.session_state["last_login_time"]:
            time_diff = (datetime.now() - st.session_state["last_login_time"]).seconds
            if time_diff < LOCKOUT_TIME:
                st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
                st.error(f"🔒 تم قفل النظام مؤقتاً. يرجى المحاولة بعد {LOCKOUT_TIME - time_diff} ثانية")
                st.markdown('</div>', unsafe_allow_html=True)
                st.stop()
            else:
                st.session_state["login_attempts"] = 0

    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#1a1a1a;'>منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف</p>", unsafe_allow_html=True)

    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("https://tower-scientific-platform.streamlit.app")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        st.markdown(f'<div style="text-align:center; margin:20px 0;"><img src="data:image/png;base64,{qr_base64}" width="150"></div>', unsafe_allow_html=True)
    except:
        pass

    login_option = st.radio("طريقة الدخول:", ["كود الدخول السري", "اسم المستخدم وكلمة المرور"], horizontal=True)
    
    if login_option == "كود الدخول السري":
        input_code = st.text_input("🔑 أدخل كود الدخول الخاص بك:", type="password")
        col_login, col_reset = st.columns(2)
        with col_login:
            if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
                input_code_stripped = input_code.strip()
                if input_code_stripped in CODES_DB:
                    st.session_state["approved"] = True
                    st.session_state["user_role"] = CODES_DB[input_code_stripped]["role"]
                    st.session_state["login_welcome_shown"] = False
                    st.session_state["login_attempts"] = 0
                    st.session_state["last_login_time"] = datetime.now()
                    st.session_state["session_token"] = secrets.token_urlsafe(32)
                    st.rerun()
                else:
                    st.session_state["login_attempts"] += 1
                    st.session_state["last_login_time"] = datetime.now()
                    remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                    st.error(f"❌ الكود غير صحيح! متبقي {remaining} محاولات")
        with col_reset:
            if st.button("🔄 نسيت الكود", use_container_width=True):
                st.info("يرجى التواصل مع مدير النظام: abukram128@gmail.com")
    else:
        username = st.text_input("👤 اسم المستخدم")
        password = st.text_input("🔑 كلمة المرور", type="password")
        if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
            auth = AuthManager()
            user = auth.authenticate(username, password)
            if user:
                st.session_state["approved"] = True
                st.session_state["user_role"] = user['role']
                st.session_state["login_welcome_shown"] = False
                st.session_state["login_attempts"] = 0
                st.session_state["last_login_time"] = datetime.now()
                st.session_state["session_token"] = secrets.token_urlsafe(32)
                st.session_state["user"] = user
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                st.session_state["last_login_time"] = datetime.now()
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ اسم المستخدم أو كلمة المرور غير صحيحة! متبقي {remaining} محاولات")
        
        st.caption("💡 المستخدم الافتراضي: admin / admin123")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# تشغيل الصوت الترحيبي بعد المصادقة (مرة واحدة)
if st.session_state["approved"] and not st.session_state.get("audio_played", False):
    play_welcome_audio()
    st.session_state["audio_played"] = True

if not st.session_state["login_welcome_shown"]:
    role_messages = {
        "owner": "👋 مرحباً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور",
        "specialist": "🔬 أهلاً بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني.",
        "breeder": "🚜 أهلاً وسهلاً بإخواننا المربين، شركاء النجاح."
    }
    role_icons = {"owner": "👑", "specialist": "👨‍🔬", "breeder": "🌾"}
    st.toast(role_messages.get(st.session_state["user_role"], "مرحباً"), icon=role_icons.get(st.session_state["user_role"], "🌾"))
    st.session_state["login_welcome_shown"] = True

# ============================================================
# 13. الواجهة الرئيسية
# ============================================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logout_space, col_user_status = st.columns([0.7, 0.3])
with col_user_status:
    role_info = {"owner": "الاختصاصي م. عبد القادر إسماعيل تاور 👑", "specialist": "المختص والزملاء 👨‍🔬", "breeder": "المربي 🌾"}
    st.markdown(f"""<div style='text-align: left; font-size:0.9rem; color:#1a1a1a; background: linear-gradient(135deg, #f5f5f5, #e0e0e0); padding: 10px; border-radius: 10px;'>الحساب: <b>{role_info.get(st.session_state["user_role"], "مستخدم")}</b><br><small>آخر دخول: {datetime.now().strftime('%Y-%m-%d %H:%M')}</small></div>""", unsafe_allow_html=True)
    if st.button("تسجيل الخروج 🚪", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key != "inventory":
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style pulse-animation">', unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.2rem; margin-top:5px; margin-bottom:0;'>محرك الاستمثال الخطي المتقدم القائم على البروتين المهضوم (DP) ومعادل النشاء (SE)</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)

st.markdown("### 📢 المشاركة التسويقية والدعوة العلمية")
share_text_payload = """📢 دعوة علمية وتسويقية من منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف

إلى كل مهتم بتطوير الثروة الحيوانية؛ من أطباء بيطريين، اختصاصيي إنتاج حيواني، ومربين طموحين:
يسعدنا دعوتكم لاستخدام وتجربة المنصة المتقدمة لتركيب وتطوير الأعلاف، بإشراف وتصميم:
[ الاختصاصي م. عبد القادر إسماعيل تاور ]

🎯 ما تقدمه المنصة:
• حلول برمجية ذكية لتركيب أعلاف اقتصادية على أساس البروتين المهضوم ومعادل النشاء (Least-Cost Formulation).
• أدوات دقيقة لحساب الاحتياجات الغذائية بما يضمن أعلى معدلات نمو وإنتاجية.
• دعم كامل للعمل الميداني والبحث العلمي والخصم التلقائي للمستودعات في مكان واحد.
• نظام تحليلات متقدم وتقارير PDF احترافية
• إدارة مزارع الدجاج اللاحم مع حساب KPIs و EPEF (خاص بالمالك)
• وحدة متخصصة لتغذية الخيول مع تحليل OCR لبطاقات الأعلاف

🔗 رابط المنصة: [ضع رابط موقعك هنا]"""
st.text_area("النص الدعائي والإعلامي الجاهز للنشر:", value=share_text_payload, height=140, key="top_share_box")
col_copy, col_share = st.columns(2)
with col_copy:
    if st.button("📋 نسخ الرابط والنص للدعاية والتسويق", type="secondary", use_container_width=True):
        st.success("تم التجهيز بنجاح! يمكنك الآن نسخ النص ومشاركته عبر المجموعات والمنصات.")
with col_share:
    encoded_share = urllib.parse.quote(share_text_payload[:200])
    st.link_button("📲 مشاركة مباشرة عبر واتساب", f"https://wa.me/?text={encoded_share}", use_container_width=True)

st.markdown("---")

welcome_messages = {
    "owner": {"bg": "#eff6ff", "border": "#1d4ed8", "text": "👑 أهلاً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور. نظام التوازن الدقيق بالبروتين المهضوم ومعادل النشاء قيد التشغيل الآن بكفاءة متناهية. كما تم تفعيل إدارة مزارع الدجاج اللاحم ووحدة تغذية الخيل."},
    "specialist": {"bg": "#f0fdf4", "border": "#16a34a", "text": "🔬 مرحباً بكم في منصة تركيب وتحليل الأعلاف الذكية. يسعد الاختصاصي م. عبد القادر إسماعيل تاور بالترحيب بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني."},
    "breeder": {"bg": "#fffbeb", "border": "#d97706", "text": "🚜 أهلاً وسهلاً بكم في منصة تاور العلمية. نرحب بإخواننا المربين. نوفر لكم خلطات مبنية على القيمة الغذائية الحقيقية الممتصة لضمان التوفير المالي العالي."}
}
current_welcome = welcome_messages.get(st.session_state["user_role"], welcome_messages["breeder"])
st.markdown(f"""<div style='background-color: {current_welcome["bg"]}; padding: 15px; border-radius: 8px; border-right: 5px solid {current_welcome["border"]}; text-align: right; direction: rtl; margin-bottom: 20px;'><b>{current_welcome["text"]}</b></div>""", unsafe_allow_html=True)

# ============================================================
# 14. تحديد التبويبات (مع إضافة تبويب الخيل)
# ============================================================
if st.session_state["user_role"] == "owner":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "🐴 تغذية الخيل والتحليل الذكي",
        "📊 بورصة الأسعار المركزية",
        "🏭 إدارة المستودعات الذكية",
        "🧾 التسويق وفواتير البيع",
        "🖨️ مصمم الديباجة والدعاية",
        "📈 التحليلات المتقدمة",
        "🐔 إدارة مزارع الدجاج اللاحم (Broiler) – خاص بالمالك",
        "💬 تعليقات المختصين",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم"
    ]
elif st.session_state["user_role"] == "specialist":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "🐴 تغذية الخيل والتحليل الذكي",
        "📊 بورصة الأسعار المركزية",
        "🏭 إدارة المستودعات الذكية",
        "🧾 التسويق وفواتير البيع",
        "🖨️ مصمم الديباجة والدعاية",
        "📈 التحليلات المتقدمة",
        "💬 تعليقات المختصين",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم"
    ]
else:  # breeder
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "🐴 تغذية الخيل والتحليل الذكي",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم"
    ]

tabs = st.tabs(tabs_titles)

# ============================================================
# 15. التبويب الأول: النمذجة والحسابات العلفية (مختصر)
# ============================================================
with tabs[0]:
    st.markdown('<div class="section-title">🔬 محرك تركيب الأعلاف الذكي</div>', unsafe_allow_html=True)
    st.info("استخدم هذا المحرك لحساب أقل تكلفة لخلطة علفية بناءً على البروتين المهضوم ومعادل النشاء.")
    
    # اختيار المكونات (مبسط)
    st.markdown("### اختر المكونات المتاحة")
    selected_ingredients = []
    ingredient_prices = []
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=True if "الحبوب" in cat_name or "الأكساب" in cat_name else False):
            cols = st.columns(3)
            for idx, (ing_name, data) in enumerate(items.items()):
                with cols[idx % 3]:
                    checked = st.checkbox(ing_name, value=ing_name in ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)"], key=f"feed_{ing_name}")
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices.append(data.get("price", 300.0))
    
    # الإضافات التلقائية
    default_additives = ["ملح الطعام", "الحجر الجيري (بودرة بلاط)"]
    for add in default_additives:
        if add not in selected_ingredients:
            selected_ingredients.append(add)
            ingredient_prices.append(40.0)
    
    col1, col2 = st.columns(2)
    with col1:
        target_dp = st.slider("البروتين المهضوم المستهدف (%)", 8.0, 30.0, 18.0, 0.5)
    with col2:
        target_se = st.slider("معادل النشاء المستهدف", 40.0, 85.0, 70.0, 1.0)
    
    if st.button("🚀 حساب الخلطة المثلى", type="primary", use_container_width=True):
        if len(selected_ingredients) < 3:
            st.warning("⚠️ يرجى اختيار 3 مكونات على الأقل")
        else:
            # بناء مصفوفات المحرك
            c = ingredient_prices
            A_eq = [[1.0] * len(selected_ingredients)]
            b_eq = [100.0]
            
            cp_row = []
            se_row = []
            for ing in selected_ingredients:
                cp = 0
                se = 0
                for cat in BIG_FEEDS_LIBRARY.values():
                    if ing in cat:
                        cp = cat[ing].get("CP", 0) * cat[ing].get("DC", 0)
                        se = cat[ing].get("SE", 0)
                        break
                cp_row.append(cp)
                se_row.append(se)
            
            A_eq.append(cp_row)
            b_eq.append(target_dp * 100.0)
            
            A_ub = [[-s for s in se_row]]
            b_ub = [-target_se * 100.0]
            
            bounds = [(0, 100) for _ in selected_ingredients]
            
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
            
            if res.success:
                formula = {}
                for i, ing in enumerate(selected_ingredients):
                    if res.x[i] > 0.001:
                        formula[ing] = round(res.x[i], 2)
                
                # حساب SE الفعلي
                actual_se = 0
                for ing, pct in formula.items():
                    for cat in BIG_FEEDS_LIBRARY.values():
                        if ing in cat:
                            actual_se += (pct / 100) * cat[ing].get("SE", 0)
                            break
                
                st.success("✅ تم حساب الخلطة بنجاح!")
                st.session_state["active_formula"] = formula
                st.session_state["computed_ton_cost"] = res.fun / 100
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("التكلفة للطن", f"${res.fun/100:.2f}")
                with col2:
                    st.metric("معادل النشاء الفعلي", f"{actual_se:.1f}")
                
                st.write("#### 📝 مقادير الخلطة (كجم/طن):")
                for k, v in formula.items():
                    st.markdown(f'<div class="formula-item">▪️ <b>{k}:</b> {v:.2f}% ➡️ ({v*10:.1f} كجم)</div>', unsafe_allow_html=True)
            else:
                st.error("❌ لم يتم العثور على حل. حاول تغيير المكونات أو الأهداف.")

# ============================================================
# 16. التبويب الثاني: تغذية الخيل (المدمج)
# ============================================================
with tabs[1]:
    st.markdown('<div class="section-title">🐴 وحدة تغذية الخيل والتحليل الذكي</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='background: #e8eaf6; padding:15px; border-radius:12px; border-right:5px solid #3949ab; margin-bottom:20px;'>
    <b>📘 عن الوحدة:</b> يمكنك حساب احتياجات الحصان الغذائية، اختيار العلف المناسب، 
    أو مسح بطاقة العلف لاستخراج المعلومات التغذوية تلقائياً باستخدام تقنية OCR.
    </div>
    """, unsafe_allow_html=True)
    
    # تقسيم الصفحة إلى شقين
    col_input, col_calc = st.columns([1, 1])
    
    with col_input:
        st.subheader("1. مصدر العلف المركز")
        source_mode = st.radio("اختر طريقة إدخال البيانات:", ["قاعدة بيانات المنتجات", "مسح صورة العبوات (OCR)"])
        
        selected_protein = 0.0
        selected_fiber = 0.0
        selected_starch = 0.0
        is_gastric_safe = False
        feed_name = ""
        feed_brand = ""
        
        if source_mode == "قاعدة بيانات المنتجات":
            prod_choice = st.selectbox("اختر المنتج التجاري:", list(PRODUCTS_DB.keys()))
            prod = PRODUCTS_DB[prod_choice]
            
            selected_protein = prod.protein
            selected_fiber = prod.fiber
            selected_starch = prod.starch or 0.0
            is_gastric_safe = prod.is_gastric_safe
            feed_name = prod.name
            feed_brand = prod.brand
            
            st.info(f"**ملاحظات المنتج:** {prod.notes}")
            
            # عرض تفاصيل المنتج
            st.markdown("#### 📊 التحليل الغذائي:")
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1: st.metric("البروتين", f"{prod.protein}%")
            with col_p2: st.metric("الألياف", f"{prod.fiber}%")
            with col_p3: st.metric("النشا", f"{prod.starch or 0}%")
            
        else:
            st.info("📸 ارفع صورة لبطاقة العلف (Bag Tag) لاستخراج البيانات تلقائياً")
            uploaded_file = st.file_uploader("ارفع صورة بطاقة التحليل التغذوي", type=["jpg", "png", "jpeg"])
            
            if uploaded_file:
                st.image(uploaded_file, caption="الصورة المرفوعة", use_column_width=True)
                
                if st.button("🔍 تحليل الصورة", type="primary"):
                    with st.spinner("جاري تحليل النص واستخراج القيم التغذوية..."):
                        parsed_data = OCRFeedParser.parse_image(uploaded_file)
                        
                        # عرض النص المستخرج
                        with st.expander("📝 النص المستخرج من الصورة"):
                            st.text(parsed_data.get("raw_text", "لا يوجد نص"))
                        
                        # تعيين القيم المستخرجة
                        selected_protein = parsed_data.get("protein") or 0.0
                        selected_fiber = parsed_data.get("fiber") or 0.0
                        selected_starch = parsed_data.get("starch") or 0.0
                        is_gastric_safe = parsed_data.get("is_sensitive", False)
                        
                        # عرض النتائج
                        if selected_protein > 0 or selected_fiber > 0:
                            st.success("✅ تم تحليل الصورة بنجاح!")
                        else:
                            st.warning("⚠️ لم يتم التعرف على القيم. يرجى إدخالها يدوياً.")
        
        # عرض المكونات المستخرجة للتأكيد
        st.write("---")
        st.markdown("**التحليل المعياري للعلف المختار:**")
        col_confirm1, col_confirm2, col_confirm3 = st.columns(3)
        with col_confirm1:
            protein_manual = st.number_input("البروتين الخام (%)", value=selected_protein, step=0.5)
        with col_confirm2:
            fiber_manual = st.number_input("الألياف الخام (%)", value=selected_fiber, step=0.5)
        with col_confirm3:
            starch_manual = st.number_input("النشا (%)", value=selected_starch, step=0.5)
        
        gastric_safe = st.checkbox("العلف آمن للمعدة (منخفض النشا)", value=is_gastric_safe)
        
        if source_mode == "قاعدة بيانات المنتجات":
            st.info(f"🏷️ المنتج: {feed_brand} - {feed_name}")
    
    with col_calc:
        st.subheader("2. بيانات الحصان والحسابات")
        
        weight = st.number_input("وزن الحصان (كجم):", min_value=100, max_value=1000, value=500, step=25)
        activity = st.selectbox("مستوى النشاط البدني:", [
            "صيانة / رياضة خفيفة (Maintenance / Light Work)",
            "رياضة شاقة / أداء عالي (Top Sport / Heavy Work)"
        ])
        has_ulcer = st.checkbox("الحصان يعاني من حساسيات هضمية / قرحة معدة", value=gastric_safe)
        
        if st.button("🧮 حساب العليقة والتوصيات", type="primary", use_container_width=True):
            # حساب الاحتياجات
            min_forage_kg = EquineNutritionEngine.calculate_forage_requirement(weight)
            
            if "صيانة" in activity:
                conc_min, conc_max = EquineNutritionEngine.calculate_concentrate_range(weight, "صيانة")
            else:
                conc_min, conc_max = EquineNutritionEngine.calculate_concentrate_range(weight, "شاقة")
            
            # عدد الوجبات
            meals = EquineNutritionEngine.get_meal_frequency(conc_max)
            
            # تقييم خطر القرحة
            risk_eval = EquineNutritionEngine.evaluate_gastric_risk(starch_manual, gastric_safe, has_ulcer)
            
            # عرض النتائج
            st.markdown("### 📊 نتائج الحسابات")
            
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("الحد الأدنى للعلف الخشن", f"{min_forage_kg:.2f} كجم/يوم")
            with col_r2:
                st.metric("نطاق العلف المركز", f"{conc_min:.2f} - {conc_max:.2f} كجم/يوم")
            with col_r3:
                st.metric("عدد الوجبات اليومية", f"{meals} وجبات")
            
            # التوصيات
            st.markdown("### 💡 التوصيات العلمية والتشغيلية:")
            
            st.write(f"- **تقسيم الوجبات:** يجب تقسيم كمية المركزات على **{meals} وجبات يومية** على الأقل.")
            st.write(f"- **العلف الخشن:** تأكد من توفير {min_forage_kg:.2f} كجم من الدريس أو العلف الخشن يومياً.")
            
            # تحذيرات القرحة
            if risk_eval["risk_level"] == "مرتفع":
                st.error(f"⚠️ {risk_eval['recommendation']}")
            elif risk_eval["risk_level"] == "متوسط":
                st.warning(f"⚠️ {risk_eval['recommendation']}")
            else:
                st.success(f"✅ {risk_eval['recommendation']}")
            
            # جدول التوصيات
            st.markdown("#### 📋 جدول التغذية اليومي:")
            feed_table = pd.DataFrame({
                "الوجبة": [f"الوجبة {i+1}" for i in range(meals)],
                "العلف المركز (كجم)": [round(conc_max/meals, 2) for _ in range(meals)],
                "العلف الخشن (كجم)": [round(min_forage_kg/meals, 2) for _ in range(meals)]
            })
            st.table(feed_table)
            
            # نسبة النشا
            if starch_manual > 0:
                st.metric("نسبة النشا في العلف", f"{starch_manual}%")
                if starch_manual > 15 and has_ulcer:
                    st.error("❌ يُنصح بتقليل نسبة النشا والسكر إلى أقل من 10-12% لهذه الحالة.")
                elif starch_manual > 15:
                    st.warning("⚠️ نسبة النشا مرتفعة نسبياً. راقب علامات المغص أو الانزعاج الهضمي.")
    
    # القسم السفلي: مراجع الخيل
    st.markdown("---")
    st.markdown("### 📚 مراجع علمية لتغذية الخيول")
    
    col_ref1, col_ref2 = st.columns(2)
    with col_ref1:
        st.markdown("""
        <div class="horse-card">
        <b>📖 NRC (2007). Nutrient Requirements of Horses</b><br>
        المرجع الأساسي في تغذية الخيول ومتطلباتها الغذائية.<br>
        <small>ISBN: 978-0309102124</small>
        </div>
        """, unsafe_allow_html=True)
    with col_ref2:
        st.markdown("""
        <div class="horse-card">
        <b>📖 Frape, D. (2010). Equine Nutrition and Feeding</b><br>
        دليل شامل لتغذية الخيول وإدارة العلائق.<br>
        <small>4th Edition, Wiley-Blackwell</small>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# 17. بقية التبويبات (مختصرة)
# ============================================================

# تبويب بورصة الأسعار
if st.session_state["user_role"] in ["owner", "specialist"]:
    tab_idx = 2
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">📊 لوحة تحكم بورصة تاور المركزية</div>', unsafe_allow_html=True)
        st.info("عرض أسعار الماشية والمنتجات الحيوانية")

# تبويب إدارة المخازن
if st.session_state["user_role"] in ["owner", "specialist"]:
    tab_idx = 3
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">🏭 إدارة المستودعات الذكية</div>', unsafe_allow_html=True)
        stock_warnings = InventoryManager.check_stock_levels()
        st.write("حالة المخزون:")
        for item, status in stock_warnings.items():
            st.write(f"- {item}: {status}")

# تبويب الفواتير
if st.session_state["user_role"] in ["owner", "specialist"]:
    tab_idx = 4
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">💰 نظام التسويق والفواتير</div>', unsafe_allow_html=True)
        st.info("قم بإصدار فواتير البيع مع الخصم التلقائي من المستودع")

# تبويب مصمم الديباجة
if st.session_state["user_role"] in ["owner", "specialist"]:
    tab_idx = 5
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">👑 مصمم ديباجات الطباعة</div>', unsafe_allow_html=True)
        st.info("صمم ديباجات جوالات الأعلاف بشكل احترافي")

# تبويب التحليلات
if st.session_state["user_role"] in ["owner", "specialist"]:
    tab_idx = 6
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">📈 التحليلات المتقدمة</div>', unsafe_allow_html=True)
        st.info("عرض المؤشرات والتحليلات الإحصائية")

# تبويب مزارع الدجاج (خاص بالمالك)
if st.session_state["user_role"] == "owner":
    tab_idx = 7
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج اللاحم</div>', unsafe_allow_html=True)
        st.info("نظام متكامل لإدارة مزارع الدجاج اللاحم مع حساب EPEF")

# تبويب تعليقات المختصين
if st.session_state["user_role"] in ["owner", "specialist"]:
    if st.session_state["user_role"] == "owner":
        tab_idx = 8
    else:
        tab_idx = 7
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">💬 قناة التواصل والتعليقات الفنية</div>', unsafe_allow_html=True)
        st.text_area("التعليقات الحالية:", value=st.session_state["shared_comments"], height=200, disabled=True)

# تبويب المراجع العلمية
if st.session_state["user_role"] in ["owner", "specialist"]:
    if st.session_state["user_role"] == "owner":
        tab_idx = 9
    else:
        tab_idx = 8
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">📚 المراجع العلمية المعتمدة</div>', unsafe_allow_html=True)
        st.info("مراجع علمية في التغذية والإنتاج الحيواني")

# تبويب المساعدة
if st.session_state["user_role"] in ["owner", "specialist"]:
    if st.session_state["user_role"] == "owner":
        tab_idx = 10
    else:
        tab_idx = 9
else:
    tab_idx = 3
with tabs[tab_idx if st.session_state["user_role"] != "breeder" else 3]:
    st.markdown('<div class="section-title">💡 المساعدة الذكية والأسئلة الشائعة</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='background: #e3f2fd; padding:20px; border-radius:12px; direction: rtl; text-align: right;'>
    <h3>🌟 الأسئلة المتكررة:</h3>
    <ul>
    <li><b>كيف أبدأ في تركيب علفة؟</b> اختر المكونات، حدد الأهداف، واضغط على زر التشغيل.</li>
    <li><b>ما هو البروتين المهضوم؟</b> هو البروتين الذي يستطيع الحيوان هضمه فعلياً.</li>
    <li><b>ما هي وحدة تغذية الخيل؟</b> وحدة متخصصة لحساب احتياجات الخيول مع دعم OCR.</li>
    <li><b>كيف أحصل على تقرير PDF؟</b> بعد تشغيل المحرك، ستجد زر تحميل التقرير.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# تبويب دليل المستخدم
if st.session_state["user_role"] in ["owner", "specialist"]:
    if st.session_state["user_role"] == "owner":
        tab_idx = 11
    else:
        tab_idx = 10
else:
    tab_idx = 4
with tabs[tab_idx if st.session_state["user_role"] != "breeder" else 4]:
    st.markdown('<div class="section-title">📖 دليل المستخدم الشامل</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='direction: rtl; text-align: right;'>
    <h3>🎯 الغرض من المنصة</h3>
    <p>منصة تاور العلمية هي أداة ذكية لتركيب الأعلاف الحيوانية بأقل تكلفة.</p>
    
    <h3>🐴 وحدة تغذية الخيل</h3>
    <p>حساب احتياجات الخيول الغذائية، اختيار العلف المناسب، أو مسح بطاقة العلف باستخدام OCR.</p>
    
    <h3>📞 الدعم الفني</h3>
    <p>للتواصل: abukram128@gmail.com</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 18. عرض حالة المتطلبات في الواجهة (اختياري)
# ============================================================
with st.sidebar:
    st.markdown("---")
    with st.expander("🔍 حالة المتطلبات", expanded=False):
        render_requirements_status()
    
    st.markdown("---")
    st.markdown("""
    <div style="direction: rtl; text-align: center; font-size: 0.8rem; color: #666;">
        <p>🌾 منصة تاور العلمية</p>
        <p>الإصدار 2.1</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 19. التذييل
# ============================================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; direction: rtl; color: #666; font-size: 0.9rem;">
    <p>🌾 منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف © {datetime.now().year}</p>
    <p>المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور</p>
    <p style="font-size: 0.8rem; color: #999;">الإصدار 2.1 | مع وحدة تغذية الخيل والتحقق من المتطلبات</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# نهاية الكود
# ============================================================
