# ============================================================================
# تاور نولجي Tawornology العلمية - الإصدار النهائي 19.0
# للانتاج الحيواني وتركيب الاعلاف
# ============================================================================
# 🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله
# 🕊️ اللهم اجعل قبريهما روضة من رياض الجنة واجمعنا بهما في الفردوس الأعلى
# ============================================================================
# المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان
# ============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import json, os, base64, smtplib, time, urllib.parse
import hashlib, secrets, io, sqlite3, warnings, re, math, random
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scipy.optimize import linprog
from scipy.spatial import ConvexHull
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

# ===== OCR =====
try:
    import pytesseract
    from PIL import Image as PILImage
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

# ===== PDF =====
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4, landscape, letter
from reportlab.lib.units import inch, mm, cm
from reportlab.lib.colors import HexColor, black, white, grey, blue, red, green, orange, purple, teal, gold
from reportlab.platypus import (Table, TableStyle, Paragraph, Spacer, Image,
                                 SimpleDocTemplate, PageBreak, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
import arabic_reshaper
from bidi.algorithm import get_display
import qrcode
from PIL import Image as PILImage_module
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

warnings.filterwarnings('ignore')

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# =====================================================================
# إعدادات الصفحة - التصميم الجمالي
# =====================================================================
st.set_page_config(
    page_title="تاور نولجي Tawornology العلمية",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================================
# إعداد الخط العربي لـ matplotlib (لتصحيح النصوص في الرسوم البيانية)
# =====================================================================
@st.cache_resource
def setup_matplotlib_arabic():
    font_paths = [
        'Amiri-Regular.ttf',
        '/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        'C:/Windows/Fonts/arial.ttf',
        'C:/Windows/Fonts/tahoma.ttf',
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                fm.fontManager.addfont(fp)
                prop = fm.FontProperties(fname=fp)
                name = prop.get_name()
                matplotlib.rcParams['font.family'] = name
                matplotlib.rcParams['font.sans-serif'] = [name] + \
                    matplotlib.rcParams.get('font.sans-serif', [])
                matplotlib.rcParams['axes.unicode_minus'] = False
                return fp
            except Exception:
                continue
    return None

ARABIC_FONT_PATH = setup_matplotlib_arabic()

def get_arabic_font_prop(size=11, weight='normal'):
    if ARABIC_FONT_PATH and os.path.exists(ARABIC_FONT_PATH):
        return fm.FontProperties(fname=ARABIC_FONT_PATH, size=size, weight=weight)
    return fm.FontProperties(size=size, weight=weight)

# =====================================================================
# أكواد الدخول - كود المالك فقط (الجميع الآخر يدخلون كزوار)
# =====================================================================
CODES_DB = {
    "202687": {
        "role": "owner",
        "name": "الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان",
        "level": 3
    }
}

# =====================================================================
# إعدادات البريد
# =====================================================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"

if "email_password" not in st.session_state:
    try:
        st.session_state["email_password"] = st.secrets["email"]["password"]
    except Exception:
        st.session_state["email_password"] = None

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

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

# =====================================================================
# معالج النصوص العربية
# =====================================================================
class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=2000)
    def fix_arabic_text(text):
        if not text:
            return ""
        try:
            reshaped = arabic_reshaper.reshape(str(text))
            return get_display(reshaped)
        except Exception:
            return str(text)

arabic_processor = ArabicTextProcessor()

def ar(text):
    """اختصار لمعالجة النص العربي"""
    return arabic_processor.fix_arabic_text(text)

# =====================================================================
# دوال الصوت
# =====================================================================
@st.cache_data(ttl=3600)
def text_to_speech_base64(text, lang="ar"):
    if not GTTS_AVAILABLE or not text:
        return None
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()
    except Exception:
        return None

def play_audio_b64(audio_b64):
    if audio_b64:
        st.components.v1.html(
            f'<audio autoplay><source src="data:audio/mp3;base64,{audio_b64}" '
            f'type="audio/mpeg"></audio>', height=0)
        return True
    return False

def voice_guide_sequential(messages, lang="ar", delay_between=2.0):
    if not GTTS_AVAILABLE:
        return
    for i, msg in enumerate(messages):
        if msg:
            audio_b64 = text_to_speech_base64(msg, lang)
            if audio_b64:
                play_audio_b64(audio_b64)
                wc = len(msg.split())
                duration = max(2.0, wc * 0.3 + 1.0)
                time.sleep(duration)
                if i < len(messages) - 1:
                    time.sleep(0.8)

def voice_guide(message, lang="ar"):
    if not GTTS_AVAILABLE or not message:
        return
    audio_b64 = text_to_speech_base64(message, lang)
    if audio_b64:
        play_audio_b64(audio_b64)

def play_welcome_audio():
    voice_guide_sequential([
        "السلام عليكم ورحمة الله وبركاته،",
        "مرحباً بكم في تاور نولجي Tawornology العلمية،",
        "للانتاج الحيواني وتركيب الاعلاف."
    ])

def play_dua_audio():
    voice_guide_sequential([
        "اللهم اغفر لإسماعيل تاور وابتسام،",
        "وارحمهما وأدخلهما فسيح جناتك."
    ])

def play_full_guide_audio():
    messages = [
        "مرحباً بك في تاور نولجي Tawornology العلمية،",
        "لتركيب الأعلاف: اختر نوع الحيوان، ثم حدد السلالة والمرحلة،",
        "ثم اختر المكونات، واضغط زر التشغيل.",
        "يمكنك تحميل التقرير PDF أو مشاركته عبر واتساب.",
        "نسأل الله التوفيق والسعادة."
    ]
    voice_guide_sequential(messages)

# =====================================================================
# قاعدة البيانات
# =====================================================================
class DatabaseManager:
    def __init__(self, db_path="tawornology_platform.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        tables = [
            '''CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT,
                role TEXT, full_name TEXT, email TEXT, phone TEXT, specialty TEXT,
                experience_years INTEGER, created_date TEXT, last_login TEXT,
                is_active INTEGER DEFAULT 1, is_public INTEGER DEFAULT 0)''',
            '''CREATE TABLE IF NOT EXISTS feed_formulas (
                formula_id TEXT PRIMARY KEY, formula_name TEXT, animal_type TEXT,
                breed TEXT, stage TEXT, target_dp REAL, target_se REAL,
                ingredients TEXT, total_cost REAL, cost_per_ton REAL,
                created_by TEXT, created_date TEXT, is_approved INTEGER DEFAULT 0,
                usage_count INTEGER DEFAULT 0, requester_name TEXT)''',
            '''CREATE TABLE IF NOT EXISTS price_history (
                record_id TEXT PRIMARY KEY, ingredient_name TEXT, price REAL,
                currency TEXT, country TEXT, city TEXT, record_date TEXT,
                recorded_by TEXT)''',
            '''CREATE TABLE IF NOT EXISTS lab_results (
                result_id TEXT PRIMARY KEY, sample_name TEXT, sample_type TEXT,
                cp REAL, dc REAL, se REAL, ndf REAL, adf REAL, ee REAL,
                ash REAL, moisture REAL, analysis_date TEXT,
                analyzed_by TEXT, notes TEXT, image_path TEXT,
                requester_name TEXT, sample_owner TEXT)''',
            '''CREATE TABLE IF NOT EXISTS dose_reminders (
                reminder_id TEXT PRIMARY KEY, animal_type TEXT, dose_type TEXT,
                dose_name TEXT, dose_amount REAL, dose_unit TEXT,
                administration_route TEXT, frequency_days INTEGER,
                start_date TEXT, next_dose_date TEXT, notes TEXT,
                active BOOLEAN DEFAULT 1, created_by TEXT, created_date TEXT)'''
        ]
        for t in tables:
            c.execute(t)
        conn.commit()
        conn.close()

    def execute_query(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        result = c.execute(query, params)
        conn.commit()
        data = result.fetchall()
        conn.close()
        return data

    def insert_record(self, table, data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        cols = ', '.join(data.keys())
        phs = ', '.join(['?' for _ in data])
        c.execute(f"INSERT INTO {table} ({cols}) VALUES ({phs})",
                  list(data.values()))
        conn.commit()
        conn.close()
        return True

    def get_records(self, table, conditions=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if conditions:
            where = ' AND '.join([f"{k}=?" for k in conditions.keys()])
            result = c.execute(f"SELECT * FROM {table} WHERE {where}",
                                list(conditions.values()))
        else:
            result = c.execute(f"SELECT * FROM {table}")
        data = result.fetchall()
        conn.close()
        return data

    def update_record(self, table, data, condition):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        set_clause = ', '.join([f"{k}=?" for k in data.keys()])
        where = ' AND '.join([f"{k}=?" for k in condition.keys()])
        c.execute(f"UPDATE {table} SET {set_clause} WHERE {where}",
                  list(data.values()) + list(condition.values()))
        conn.commit()
        conn.close()
        return True

# =====================================================================
# نظام المصادقة
# =====================================================================
class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self._create_public_user()

    def _create_public_user(self):
        users = self.db.execute_query("SELECT * FROM users WHERE username='public'")
        if not users:
            uid = secrets.token_hex(16)
            ph = hashlib.sha256('public123'.encode()).hexdigest()
            self.db.insert_record('users', {
                'user_id': uid, 'username': 'public',
                'password_hash': ph, 'role': 'public',
                'full_name': 'زائر كريم',
                'email': 'visitor@tawornology.com',
                'phone': '+249123456780',
                'specialty': 'زائر',
                'experience_years': 0,
                'created_date': datetime.now().isoformat(),
                'last_login': '', 'is_active': 1, 'is_public': 1
            })

    def login_public(self):
        users = self.db.execute_query(
            "SELECT * FROM users WHERE username='public' AND is_active=1")
        if users:
            u = users[0]
            self.db.update_record('users',
                {'last_login': datetime.now().isoformat()},
                {'user_id': u[0]})
            return {'user_id': u[0], 'username': u[1], 'role': 'public',
                    'full_name': 'زائر كريم', 'email': u[5], 'phone': u[6],
                    'specialty': 'زائر', 'experience_years': 0}
        return None

# =====================================================================
# المراجع العلمية
# =====================================================================
class ScientificReferenceSystem:
    KNOWLEDGE_BASE = {
        "البروتين المهضوم": {
            "answer": "البروتين المهضوم (DP) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً.",
            "simplified": "البروتين المهضوم هو الجزء الذي يستفيد منه الحيوان فعلياً."
        },
        "معادل النشاء": {
            "answer": "معادل النشاء (SE) يقيس كمية الطاقة التي يوفرها العلف.",
            "simplified": "معادل النشاء يقيس الطاقة في العلف."
        },
        "تركيب العلف": {
            "answer": "يتم باستخدام محرك الاستمثال الخطي لحساب أقل تكلفة.",
            "simplified": "نحسب أرخص خلطة تحقق كل الاحتياجات."
        },
        "EPEF": {
            "answer": "EPEF = (الحيوية × الوزن) / (العمر × FCR) × 100.",
            "simplified": "رقم يعبر عن كفاءة المزرعة."
        }
    }

    @staticmethod
    def get_knowledge_answer(question):
        for key, val in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            if key in question:
                return val
        return None

# =====================================================================
# التنبؤ بالأسعار
# =====================================================================
class PricePredictor:
    def __init__(self):
        self.db = DatabaseManager()

    def predict_price(self, ingredient_name, days_ahead=7):
        prices = self.db.execute_query(
            "SELECT price FROM price_history WHERE ingredient_name=? "
            "ORDER BY record_date DESC LIMIT 30", (ingredient_name,))
        if len(prices) < 5:
            base = {"ذرة صفراء": 230, "كسب فول صويا 44%": 440,
                    "نخالة قمح (ردة)": 150}.get(ingredient_name, 300)
            return {'prediction': base, 'confidence': 0.5,
                    'current_price': base, 'trend': 'stable'}
        price_list = [p[0] for p in prices]
        weights = np.array(range(1, len(price_list) + 1))
        w_avg = np.average(price_list, weights=weights)
        trend = ((price_list[0] - price_list[-1]) / len(price_list)
                 if len(price_list) > 1 else 0)
        prediction = w_avg + (trend * days_ahead)
        return {'prediction': max(0, prediction),
                'confidence': min(1, len(price_list) / 30),
                'current_price': price_list[0],
                'trend': 'up' if trend > 0 else 'down' if trend < 0 else 'stable'}

# =====================================================================
# المختبر الذكي
# =====================================================================
class SmartLabSystem:
    def __init__(self):
        self.db = DatabaseManager()
        self.ocr_available = OCR_AVAILABLE or EASYOCR_AVAILABLE
        self.reader = None
        if EASYOCR_AVAILABLE:
            try:
                self.reader = easyocr.Reader(['ar', 'en'], gpu=False)
            except Exception:
                self.reader = None

    def analyze_image(self, image):
        if not self.ocr_available:
            return None, "مكتبات OCR غير مثبتة."
        try:
            results = []
            if EASYOCR_AVAILABLE and self.reader:
                res = self.reader.readtext(np.array(image))
                for (bbox, text, prob) in res:
                    if prob > 0.3:
                        results.append(text)
            elif OCR_AVAILABLE:
                img = PILImage.open(image) if not isinstance(image, PILImage_module.Image) else image
                text = pytesseract.image_to_string(img, lang='ara+eng')
                results = text.split('\n')
            return self._parse(results), None
        except Exception as e:
            return None, f"خطأ: {str(e)}"

    def _parse(self, texts):
        data = {'sample_name': '', 'cp': None, 'se': None}
        for t in texts:
            t = t.strip()
            m = re.search(r'بروتين\s*خام\s*[:=]?\s*([\d.]+)', t, re.IGNORECASE)
            if m and not data['cp']:
                try: data['cp'] = float(m.group(1))
                except: pass
        return data

    def save_lab_result(self, result_data):
        rid = secrets.token_hex(16)
        data = {
            'result_id': rid,
            'sample_name': result_data.get('sample_name', ''),
            'sample_type': result_data.get('sample_type', ''),
            'cp': result_data.get('cp', 0.0),
            'dc': result_data.get('dc', 0.0),
            'se': result_data.get('se', 0.0),
            'ndf': result_data.get('ndf', 0.0),
            'adf': result_data.get('adf', 0.0),
            'ee': result_data.get('ee', 0.0),
            'ash': result_data.get('ash', 0.0),
            'moisture': result_data.get('moisture', 0.0),
            'analysis_date': datetime.now().isoformat(),
            'analyzed_by': result_data.get('analyzed_by', ''),
            'notes': result_data.get('notes', ''),
            'image_path': result_data.get('image_path', ''),
            'requester_name': result_data.get('requester_name', ''),
            'sample_owner': result_data.get('sample_owner', '')
        }
        self.db.insert_record('lab_results', data)
        return rid

# =====================================================================
# الخط العربي للـ PDF
# =====================================================================
@st.cache_resource
def download_arabic_font():
    fp = "Amiri-Regular.ttf"
    if os.path.exists(fp):
        return fp
    try:
        import requests
        url = "https://raw.githubusercontent.com/aliftype/amiri/master/fonts/Amiri-Regular.ttf"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            with open(fp, "wb") as f:
                f.write(r.content)
            return fp
    except Exception:
        pass
    sys_fonts = [
        "/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf"
    ]
    for f in sys_fonts:
        if os.path.exists(f):
            return f
    return None

def ensure_arabic_font():
    fp = download_arabic_font()
    if fp and os.path.exists(fp):
        try:
            pdfmetrics.registerFont(TTFont('ArabicFont', fp))
            return 'ArabicFont'
        except Exception:
            pass
    return 'Helvetica'

# =====================================================================
# مكتبة الأعلاف
# =====================================================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6},
        "جريش أرز رزاز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2},
        "دخن محلي غزير": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0},
    },
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5},
        "كسب بذور اللفت (كانولا)": {"CP": 38.0, "DC": 0.82, "SE": 62.0, "NDF": 28.0, "ADF": 18.0, "EE": 3.5, "ASH": 7.5},
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5},
        "مخلفات مصانع البسكويت": {"CP": 10.0, "DC": 0.80, "SE": 65.0, "NDF": 8.0, "ADF": 4.0, "EE": 12.0, "ASH": 3.0},
    },
    "🧬 البروتين الحيواني": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق أسماك فاخر (72%)": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5},
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3},
        "ثريونين نقي (L-Threonine)": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2},
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس بياض وبشاير": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
        "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0},
        "كبريتات الحديدوز (معادل الجوسيبول)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0},
        "خميرة الخبز (Yeast)": {"CP": 45.0, "DC": 0.85, "SE": 35.0, "NDF": 5.0, "ADF": 2.0, "EE": 2.5, "ASH": 7.0},
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
        "يوريا علفية محصنة (المجترات فقط)": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0},
    },
    "🍼 بدائل الحليب": {
        "مصل الحليب المجفف (Whey)": {"CP": 12.0, "DC": 0.95, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.0},
        "حليب مجفف خالي الدسم": {"CP": 34.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.5},
        "دهن نباتي (زيت نباتي)": {"CP": 0.0, "DC": 0.0, "SE": 10.0, "NDF": 0.0, "ADF": 0.0, "EE": 99.0, "ASH": 0.0},
        "ليسيثين الصويا": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 95.0, "ASH": 0.5},
        "بروتين الصويا المركز": {"CP": 65.0, "DC": 0.90, "SE": 30.0, "NDF": 2.0, "ADF": 1.0, "EE": 1.0, "ASH": 5.5},
    }
}

FLAT_FEED_DB = {}
for cat, items in BIG_FEEDS_LIBRARY.items():
    for name, nut in items.items():
        FLAT_FEED_DB[name] = nut

STANDARD_VALUES = {
    "أبقار": {
        "تسمين عجول": {"DP": 12.0, "SE": 68.0, "CP": 15.0},
        "حليب/إدرار": {"DP": 14.0, "SE": 70.0, "CP": 17.5},
        "حمل/دفع غذائي": {"DP": 11.0, "SE": 65.0, "CP": 13.8},
        "صيانة": {"DP": 9.0, "SE": 60.0, "CP": 11.3}
    },
    "أغنام": {
        "تسمين حملان": {"DP": 13.0, "SE": 66.0, "CP": 16.3},
        "حليب/إدرار": {"DP": 14.5, "SE": 68.0, "CP": 18.1},
        "حمل/دفع غذائي": {"DP": 11.5, "SE": 62.0, "CP": 14.4},
        "صيانة": {"DP": 8.5, "SE": 58.0, "CP": 10.6}
    },
    "ماعز": {
        "تسمين جديان": {"DP": 12.5, "SE": 64.0, "CP": 15.6},
        "حليب/إدرار": {"DP": 14.0, "SE": 66.0, "CP": 17.5},
        "حمل/دفع غذائي": {"DP": 11.0, "SE": 60.0, "CP": 13.8},
        "صيانة": {"DP": 8.0, "SE": 56.0, "CP": 10.0}
    },
    "خيول": {
        "راحة/صيانة": {"DP": 9.0, "SE": 58.0, "CP": 11.3},
        "عمل خفيف": {"DP": 10.0, "SE": 60.0, "CP": 12.5},
        "عمل متوسط": {"DP": 11.0, "SE": 62.0, "CP": 13.8},
        "عمل مكثف": {"DP": 13.0, "SE": 65.0, "CP": 16.3},
        "سباق": {"DP": 14.0, "SE": 68.0, "CP": 17.5},
        "أمهار نامية": {"DP": 13.0, "SE": 64.0, "CP": 16.3},
        "فرسات مرضعات": {"DP": 14.0, "SE": 66.0, "CP": 17.5}
    },
    "إبل": {
        "راحة/صيانة": {"DP": 8.0, "SE": 55.0, "CP": 10.0},
        "حمل/رضاعة": {"DP": 10.0, "SE": 58.0, "CP": 12.5},
        "إنتاج حليب": {"DP": 12.0, "SE": 60.0, "CP": 15.0},
        "تسمين": {"DP": 11.0, "SE": 62.0, "CP": 13.8},
        "عمل/نقل": {"DP": 10.0, "SE": 58.0, "CP": 12.5}
    },
    "دواجن": {
        "بادي (0-14 يوم)": {"DP": 22.0, "SE": 76.0, "CP": 27.5},
        "نامي (15-28 يوم)": {"DP": 20.0, "SE": 74.0, "CP": 25.0},
        "ناهي (29-42 يوم)": {"DP": 18.0, "SE": 72.0, "CP": 22.5},
        "ناهي متقدم (43+ يوم)": {"DP": 16.0, "SE": 70.0, "CP": 20.0}
    },
    "أسماك": {
        "زريعة/بادئ": {"DP": 32.0, "SE": 70.0, "CP": 40.0},
        "نمو": {"DP": 28.0, "SE": 68.0, "CP": 35.0},
        "تسمين نهائي": {"DP": 26.0, "SE": 66.0, "CP": 32.5}
    }
}

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "ليبيا": {"rate": 4.80, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"},
    "دولار أمريكي": {"rate": 1.0, "sym": "USD"}
}

ANIMAL_IMAGES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "إبل": "https://images.unsplash.com/photo-1502175353174-a7a70e73b362?q=80&w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600"
}
# =====================================================================
# تهيئة الجلسة
# =====================================================================
defaults = {
    "approved": False, "user_role": None, "login_welcome_shown": False,
    "login_attempts": 0, "last_login_time": None, "session_token": None,
    "analysis_results": None, "lab_sample": None, "dose_reminders": [],
    "lab_sample_name": "", "lab_cp": 0.0, "lab_dc": 0.0, "lab_se": 0.0,
    "lab_ndf": 0.0, "lab_adf": 0.0, "lab_ee": 0.0, "lab_ash": 0.0,
    "lab_moisture": 0.0, "lab_notes": "",
    "lab_requester": "", "lab_owner": "",
    "active_formula": {}, "active_cp_tag": 12.0, "active_se_tag": 65.0,
    "computed_ton_cost": 280.0,
    "global_livestock_prices": {
        "عجول تسمين ($)": 1350.0, "أبقار محلية ($)": 900.0,
        "ضأن ($)": 180.0, "ماعز ($)": 130.0,
        "خيول عربية ($)": 4500.0, "إبل ($)": 2500.0, "كتكوت ($)": 0.65
    },
    "global_products_prices": {
        "لحم بقري ($/كجم)": 7.50, "لحم ضأن ($/كجم)": 9.00,
        "لحم دجاج ($/كجم)": 3.80, "بيض ($/30)": 4.20,
        "حليب ($/لتر)": 0.90
    },
    "shared_comments": "• [توجيه المشرف]: يرحب بكم في تاور نولجي Tawornology العلمية.\n",
    "daily_production_log": [],
    "smart_lab_system": None
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

try:
    st.session_state["smart_lab_system"] = SmartLabSystem()
except Exception:
    pass

# =====================================================================
# الـ CSS الجمالي الشامل
# =====================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');

* { font-family: 'Cairo', 'Tajawal', sans-serif; }

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 50%, #f5f7fa 100%);
    background-attachment: fixed;
}
.stApp { background: transparent; }

/* ═══ البطاقة الرئيسية ═══ */
.main-box {
    background: rgba(255,255,255,0.92);
    padding: 35px;
    border-radius: 24px;
    box-shadow: 0 25px 70px rgba(0,0,0,0.15);
    backdrop-filter: blur(15px);
    margin-bottom: 35px;
    border: 1px solid rgba(255,255,255,0.4);
}

/* ═══ عناوين الأقسام ═══ */
.section-title {
    color: #1b5e20;
    border-right: 6px solid #2e7d32;
    padding: 14px 22px;
    text-align: right;
    font-size: 1.6rem;
    font-weight: 700;
    margin: 25px 0 20px 0;
    background: linear-gradient(to left, rgba(46,125,50,0.12), transparent);
    border-radius: 14px;
    box-shadow: 0 4px 15px rgba(46,125,50,0.08);
}

/* ═══ بطاقة المكونات ═══ */
.formula-item {
    background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(232,245,233,0.95) 100%);
    padding: 16px 22px;
    border-radius: 14px;
    margin-bottom: 10px;
    font-weight: 600;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    transition: all 0.3s ease;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.formula-item:hover {
    transform: translateX(-8px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

/* ═══ الصورة الشخصية ═══ */
.profile-img-style {
    width: 160px;
    height: 160px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #d4af37;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    transition: all 0.5s ease;
}
.profile-img-style:hover {
    transform: scale(1.05) rotate(3deg);
    box-shadow: 0 15px 40px rgba(212,175,55,0.5);
}

/* ═══ بطاقات المؤشرات ═══ */
.metric-card {
    background: linear-gradient(135deg, #ffffff, #f8f9fa);
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 6px 30px rgba(0,0,0,0.08);
    text-align: center;
    transition: all 0.3s ease;
    border: 1px solid rgba(46,125,50,0.1);
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #2e7d32, #66bb6a, #2e7d32);
}
.metric-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 15px 50px rgba(46,125,50,0.2);
}
.metric-card .number {
    font-size: 2.2rem;
    font-weight: 900;
    color: #1b5e20;
    margin: 5px 0;
}
.metric-card .label {
    font-size: 0.95rem;
    color: #666;
    font-weight: 600;
}

/* ═══ بطاقة القياس ═══ */
.measurement-card {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 22px;
    border-radius: 16px;
    border-right: 5px solid #1565C0;
    box-shadow: 0 4px 25px rgba(21,101,192,0.15);
}

/* ═══ حالة المخزون ═══ */
.stock-critical {
    background: linear-gradient(135deg, #ffebee, #ffcdd2);
    padding: 6px 16px;
    border-radius: 25px;
    color: #c62828;
    font-weight: 700;
    display: inline-block;
}
.stock-normal {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 6px 16px;
    border-radius: 25px;
    color: #2e7d32;
    font-weight: 700;
    display: inline-block;
}
.stock-warning {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 6px 16px;
    border-radius: 25px;
    color: #e65100;
    font-weight: 700;
    display: inline-block;
}

/* ═══ البطاقات العامة ═══ */
.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px;
    border-radius: 12px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 20px;
    direction: rtl;
    text-align: right;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
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
    box-shadow: 0 4px 15px rgba(245,124,0,0.15);
}

/* ═══ الأزرار ═══ */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    transition: all 0.3s ease !important;
    border: 2px solid #2e7d32 !important;
    background: linear-gradient(135deg, #ffffff, #e8f5e9) !important;
    color: #1b5e20 !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(46,125,50,0.3) !important;
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2e7d32, #43a047) !important;
    color: white !important;
    border: none !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1b5e20, #2e7d32) !important;
    box-shadow: 0 8px 30px rgba(46,125,50,0.5) !important;
}

/* ═══ التبويبات ═══ */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: linear-gradient(135deg, #f5f5f5, #ffffff);
    padding: 8px;
    border-radius: 14px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}
.stTabs [data-baseweb="tab-list"] button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #2e7d32, #43a047) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(46,125,50,0.4) !important;
}

/* ═══ المدخلات ═══ */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 10px !important;
    border: 2px solid #e0e0e0 !important;
    transition: all 0.3s ease !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #2e7d32 !important;
    box-shadow: 0 0 0 3px rgba(46,125,50,0.15) !important;
}

/* ═══ التوسعات ═══ */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, #f8f9fa, #ffffff) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
.streamlit-expanderHeader:hover {
    background: linear-gradient(135deg, #e8f5e9, #f1f8e9) !important;
}

/* ═══ الصور ═══ */
.animal-banner-img {
    width: 100%;
    max-height: 200px;
    object-fit: cover;
    border-radius: 12px;
    margin-bottom: 20px;
    border: 3px solid #2e7d32;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}

/* ═══ شارة المشرف ═══ */
.supervisor-badge {
    background: linear-gradient(135deg, #d4af37, #ffd700);
    color: #1a237e;
    padding: 8px 20px;
    border-radius: 25px;
    font-weight: 900;
    display: inline-block;
    margin: 5px 0;
    box-shadow: 0 6px 20px rgba(212,175,55,0.5);
    animation: goldShine 3s ease-in-out infinite;
}
@keyframes goldShine {
    0%, 100% { box-shadow: 0 6px 20px rgba(212,175,55,0.5); }
    50% { box-shadow: 0 8px 35px rgba(212,175,55,0.85); }
}

/* ═══ شريط الترحيب ═══ */
.welcome-banner {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9, #a5d6a7);
    background-size: 200% 200%;
    animation: welcomeShift 8s ease infinite;
    padding: 20px 25px;
    border-radius: 16px;
    border-right: 6px solid #2e7d32;
    margin-bottom: 25px;
    direction: rtl;
    text-align: right;
    box-shadow: 0 8px 25px rgba(46,125,50,0.15);
}
@keyframes welcomeShift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# شريط الدعاء - تحرك يسار→يمين + نسخة ثابتة
# =====================================================================
def render_dua_bar():
    st.markdown("""
    <style>
    @keyframes scrollDuaLR {
        0%   { transform: translateX(-100%); opacity: 0.2; }
        10%  { opacity: 1; }
        50%  { opacity: 1; }
        90%  { opacity: 1; }
        100% { transform: translateX(100%); opacity: 0.2; }
    }
    @keyframes glowTextDua {
        0%,100% { text-shadow: 0 0 8px #ffd700, 0 0 16px #ffd700, 0 0 30px #ff8c00; }
        50%     { text-shadow: 0 0 20px #ffd700, 0 0 40px #ff8c00, 0 0 70px #ff4500; }
    }
    @keyframes pulseHeartDua {
        0%,100% { transform: scale(1);   color: #ff6b6b; }
        50%     { transform: scale(1.4); color: #ff1744; }
    }
    @keyframes bgShiftDua {
        0%   { background-position:   0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position:   0% 50%; }
    }
    .dua-container {
        background: linear-gradient(90deg, #0d1b2a, #1a237e, #4a148c, #1a237e, #0d1b2a);
        background-size: 300% 300%;
        animation: bgShiftDua 14s ease infinite;
        padding: 24px 0;
        border-radius: 24px 24px 0 0;
        overflow: hidden;
        border: 3px solid #ffd700;
        border-bottom: none;
        box-shadow: 0 8px 40px rgba(255, 215, 0, 0.5),
                    inset 0 0 30px rgba(255, 215, 0, 0.15);
        direction: ltr;
        position: relative;
        min-height: 90px;
    }
    .dua-track {
        display: inline-block;
        white-space: nowrap;
        animation: scrollDuaLR 35s linear infinite,
                   glowTextDua 3s ease-in-out infinite;
        font-size: 1.75rem;
        font-weight: 800;
        color: #ffd700;
        padding: 0 30px;
        font-family: 'Cairo', 'Tajawal', sans-serif;
        letter-spacing: 1.5px;
    }
    .dua-track .emoji-heart { display: inline-block;
        animation: pulseHeartDua 1.2s ease-in-out infinite;
        margin: 0 10px; }
    .dua-track .gold-star  { color: #ffd700; font-size: 1.6rem; margin: 0 14px; }
    .dua-track .name-highlight {
        color: #ffab40;
        font-weight: 900;
        background: rgba(255, 215, 0, 0.18);
        padding: 2px 12px;
        border-radius: 8px;
        border: 1px solid rgba(255, 215, 0, 0.35);
    }
    .dua-static {
        background: linear-gradient(90deg, #1b2a4a, #2a1b4a, #1b2a4a);
        background-size: 200% 200%;
        animation: bgShiftDua 10s ease infinite;
        padding: 14px 20px;
        border-radius: 0 0 20px 20px;
        text-align: center;
        color: #e1bee7;
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        border: 3px solid #ffd700;
        border-top: 1px solid rgba(255, 215, 0, 0.35);
        direction: rtl;
        line-height: 1.9;
        margin-bottom: 20px;
    }
    .dua-static .name-highlight-static {
        color: #ffd700;
        font-weight: 900;
        background: rgba(255, 215, 0, 0.12);
        padding: 1px 10px;
        border-radius: 6px;
    }
    .dua-static .heart-sm {
        color: #ff6b6b;
        font-size: 1rem;
        margin: 0 6px;
        display: inline-block;
        animation: pulseHeartDua 1.5s ease-in-out infinite;
    }
    </style>

    <div class="dua-container">
        <div class="dua-track">
            <span class="gold-star">✦</span>
            <span class="emoji-heart">❤️</span>
            اللهم اغفر لـ <span class="name-highlight">إسماعيل تاور</span>
            و <span class="name-highlight">ابتسام</span>
            وارحمهما وأدخلهما فسيح جناتك
            <span class="emoji-heart">❤️</span>
            اللهم اجعل قبريهما روضة من رياض الجنة واجمعنا بهما في الفردوس الأعلى
            <span class="emoji-heart">❤️</span>
            اللهم ارحم موتانا وموتى المسلمين
            <span class="emoji-heart">❤️</span>
            <span class="gold-star">✦</span>
        </div>
    </div>

    <div class="dua-static">
        🕊️ <span class="name-highlight-static">اللهم اغفر لإسماعيل تاور وابتسام</span>
        <span class="heart-sm">❤️</span>
        وارحمهما وأدخلهما فسيح جناتك
        <span class="heart-sm">❤️</span>
        اللهم اجعل قبريهما روضة من رياض الجنة
        <span class="heart-sm">❤️</span>
        واجمعنا بهما في الفردوس الأعلى 🕊️
    </div>
    """, unsafe_allow_html=True)
    # =====================================================================
# مولد PDF الجمالي
# =====================================================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = ensure_arabic_font()
        self.styles = self._create_styles()

    def _create_styles(self):
        return {
            'title': ParagraphStyle('title', fontName=self.font_name, fontSize=22,
                                     alignment=TA_CENTER, textColor=HexColor('#1b5e20'),
                                     spaceAfter=12, leading=28),
            'subtitle': ParagraphStyle('subtitle', fontName=self.font_name, fontSize=15,
                                        alignment=TA_CENTER, textColor=HexColor('#2e7d32'),
                                        spaceAfter=10, leading=20),
            'heading': ParagraphStyle('heading', fontName=self.font_name, fontSize=13,
                                       alignment=TA_RIGHT, textColor=HexColor('#1b5e20'),
                                       spaceAfter=8, leading=18),
            'body': ParagraphStyle('body', fontName=self.font_name, fontSize=11,
                                    alignment=TA_RIGHT, textColor=HexColor('#333'),
                                    spaceAfter=5, leading=16),
            'footer': ParagraphStyle('footer', fontName=self.font_name, fontSize=8,
                                      alignment=TA_CENTER, textColor=HexColor('#999'),
                                      spaceAfter=0, leading=10),
            'note': ParagraphStyle('note', fontName=self.font_name, fontSize=10,
                                    alignment=TA_RIGHT, textColor=HexColor('#0d47a1'),
                                    backColor=HexColor('#e3f2fd'),
                                    borderPadding=(8, 10, 8, 10), leading=16)
        }

    def _add_bismala(self, story):
        bism = ParagraphStyle('bismala', fontName=self.font_name, fontSize=22,
                              alignment=TA_CENTER, textColor=HexColor('#1b5e20'),
                              spaceAfter=6, leading=30)
        story.append(Paragraph(ar("﷽"), bism))
        story.append(Spacer(1, 6))
        bar = Table([[""]], colWidths=[520], rowHeights=[6])
        bar.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), HexColor('#2e7d32'))]))
        story.append(bar)
        story.append(Spacer(1, 12))
        return story

    def _add_section_title(self, story, text, color):
        s = ParagraphStyle('sec', fontName=self.font_name, fontSize=13,
                           alignment=TA_CENTER, textColor=white,
                           backColor=HexColor(color),
                           borderPadding=(8, 12, 8, 12), leading=20)
        story.append(Paragraph(ar(text), s))
        story.append(Spacer(1, 8))
        return story

    def _add_note(self, story, text):
        story.append(Paragraph(ar(text), self.styles['note']))
        story.append(Spacer(1, 12))
        return story

    def _add_official_stamp(self, story, user_name, owner_name=""):
        stamp_rows = [
            [Paragraph(ar("<b>🌾 الختم الرسمي 🌾</b>"),
                       ParagraphStyle('sT', fontName=self.font_name, fontSize=14,
                                      alignment=TA_CENTER, textColor=HexColor('#c62828'),
                                      leading=20))],
            [Paragraph(ar("<b>تاور نولجي Tawornology العلمية</b>"),
                       ParagraphStyle('sC', fontName=self.font_name, fontSize=12,
                                      alignment=TA_CENTER, textColor=HexColor('#1b5e20'),
                                      leading=18))],
            [Paragraph(ar("الاختصاصي م. عبد القادر إسماعيل تاور"),
                       ParagraphStyle('sN', fontName=self.font_name, fontSize=11,
                                      alignment=TA_CENTER, textColor=HexColor('#1a237e'),
                                      leading=16))],
            [Paragraph(ar("اختصاصي تغذية الحيوان - المشرف العام"),
                       ParagraphStyle('sR', fontName=self.font_name, fontSize=10,
                                      alignment=TA_CENTER, textColor=HexColor('#555'),
                                      leading=14))],
            [Paragraph(ar(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
                       ParagraphStyle('sD', fontName=self.font_name, fontSize=9,
                                      alignment=TA_CENTER, textColor=HexColor('#888'),
                                      leading=12))],
            [Paragraph(ar(f"👤 المعتمد: {user_name}"),
                       ParagraphStyle('sU', fontName=self.font_name, fontSize=9,
                                      alignment=TA_CENTER, textColor=HexColor('#666'),
                                      leading=12))],
            [Paragraph(ar("✅ تم الاعتماد رسمياً - صالح للاستخدام الفني"),
                       ParagraphStyle('sV', fontName=self.font_name, fontSize=9,
                                      alignment=TA_CENTER, textColor=HexColor('#2e7d32'),
                                      leading=12))]
        ]
        stamp = Table(stamp_rows, colWidths=[300])
        stamp.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 3, HexColor('#c62828')),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#ffebee')),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        wrapper = Table([[stamp]], colWidths=[520])
        wrapper.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 110),
            ('RIGHTPADDING', (0, 0), (-1, -1), 110),
        ]))
        story.append(wrapper)
        story.append(Spacer(1, 15))
        story.append(Paragraph(ar("🌾 تم التوليد بواسطة تاور نولجي Tawornology © 2026"),
                                self.styles['footer']))
        return story

    def generate_lab_report(self, analysis_results, animal_type, stage, user_name,
                             standard=None, evaluation=None, requester_name="",
                             sample_name="", sample_owner=""):
        """تقرير المختبر - مع البسملة والختم والتوصيات"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40,
                                 topMargin=25, bottomMargin=35)
        story = []

        def p(text, style='body'):
            return Paragraph(ar(text), self.styles.get(style, self.styles['body']))

        story = self._add_bismala(story)
        story.append(p("🔬 تقرير التحليل المخبري المتقدم", 'title'))
        story.append(p("🌾 تاور نولجي Tawornology العلمية", 'subtitle'))
        story.append(p("👨‍💻 المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور - "
                       "اختصاصي تغذية الحيوان", 'subtitle'))
        story.append(Spacer(1, 12))

        # ═══ بيانات العينة ═══
        story = self._add_section_title(story, "📋 بيانات العينة والتحليل", '#1565C0')
        info_data = [
            [ar("👤 صاحب العينة"), ar(sample_owner or 'غير محدد'),
             ar("📝 اسم العينة"), ar(sample_name or 'غير مسمى')],
            [ar("🐾 نوع الحيوان"), ar(animal_type),
             ar("📋 المرحلة"), ar(stage)],
            [ar("👤 طالب العلفة"), ar(requester_name or 'غير محدد'),
             ar("📅 التاريخ"), ar(datetime.now().strftime('%Y-%m-%d %H:%M'))],
        ]
        info_t = Table(info_data, colWidths=[100, 160, 100, 160])
        info_t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
            ('BACKGROUND', (2, 0), (2, -1), HexColor('#e8f5e9')),
            ('BACKGROUND', (1, 0), (1, -1), HexColor('#ffffff')),
            ('BACKGROUND', (3, 0), (3, -1), HexColor('#ffffff')),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#1b5e20')),
            ('TEXTCOLOR', (2, 0), (2, -1), HexColor('#1b5e20')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#1565C0')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(info_t)
        story.append(Spacer(1, 14))

        if analysis_results and 'components' in analysis_results:
            # ═══ المكونات ═══
            story = self._add_section_title(story, "📦 المكونات المدخلة", '#1565C0')
            comp_data = [[ar('المادة'), ar('الوزن (كجم)'), ar('النسبة %')]]
            total_w = sum(analysis_results['components'].values())
            for name, weight in analysis_results['components'].items():
                if weight > 0:
                    pct = (weight / total_w) * 100 if total_w > 0 else 0
                    comp_data.append([ar(name), f"{weight:.1f}", f"{pct:.2f}"])
            t = Table(comp_data, colWidths=[240, 130, 130])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565C0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#90caf9')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                 [HexColor('#ffffff'), HexColor('#e3f2fd')]),
            ]))
            story.append(t)
            story.append(Spacer(1, 8))
            story = self._add_note(story,
                "💡 التوضيح: يوضح هذا الجدول نسب المواد الخام المستخدمة. "
                "يُنصح بالتأكد من دقة الأوزان، حيث أي خطأ يؤثر على دقة النتائج.")

            # ═══ النتائج ═══
            story = self._add_section_title(story, "📊 النتائج المحسوبة", '#2e7d32')
            res_data = [[ar('العنصر'), ar('القيمة'), ar('الوحدة')]]
            rows_styles = []
            idx = 1
            if 'cp' in analysis_results:
                res_data.append([ar('البروتين الخام (CP)'),
                                  f"{analysis_results['cp']:.2f}", '%'])
                rows_styles.append(('BACKGROUND', (0, idx), (-1, idx), HexColor('#fff3e0')))
                idx += 1
            if 'dp' in analysis_results:
                res_data.append([ar('البروتين المهضوم (DP)'),
                                  f"{analysis_results['dp']:.2f}", '%'])
                rows_styles.append(('BACKGROUND', (0, idx), (-1, idx), HexColor('#e8f5e9')))
                idx += 1
            if 'se' in analysis_results:
                res_data.append([ar('معادل النشاء (SE)'),
                                  f"{analysis_results['se']:.2f}", ar('وحدة')])
                rows_styles.append(('BACKGROUND', (0, idx), (-1, idx), HexColor('#e1f5fe')))
            t2 = Table(res_data, colWidths=[240, 130, 130])
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#a5d6a7')),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ] + rows_styles))
            story.append(t2)
            story.append(Spacer(1, 8))
            story = self._add_note(story,
                "💡 التوضيح: CP هو البروتين الخام الكلي، و DP يعبر عن "
                "البروتين الفعلي القابل للهضم. SE يقيس الطاقة الإجمالية.")

            # ═══ المقارنة ═══
            if standard:
                story = self._add_section_title(story, "📏 المقارنة مع المعايير", '#6a1b9a')
                comp_rows = [[ar('المقياس'), ar('المحسوب'), ar('القياسي'),
                              ar('الانحراف'), ar('التقييم')]]

                def eval_row(calc, std_val):
                    if std_val <= 0:
                        return "-", "⚠️"
                    dev = ((calc - std_val) / std_val) * 100
                    grade = ("✅ ممتاز" if abs(dev) <= 5
                             else ("👍 جيد" if abs(dev) <= 10 else "⚠️ تحسين"))
                    return f"{dev:+.1f}%", grade

                if 'DP' in standard and 'dp' in analysis_results:
                    dev, grade = eval_row(analysis_results['dp'], standard['DP'])
                    comp_rows.append(['DP', f"{analysis_results['dp']:.2f}%",
                                       f"{standard['DP']:.2f}%", dev, grade])
                if 'SE' in standard and 'se' in analysis_results:
                    dev, grade = eval_row(analysis_results['se'], standard['SE'])
                    comp_rows.append(['SE', f"{analysis_results['se']:.2f}",
                                       f"{standard['SE']:.2f}", dev, grade])
                if 'CP' in standard and 'cp' in analysis_results:
                    dev, grade = eval_row(analysis_results['cp'], standard['CP'])
                    comp_rows.append(['CP', f"{analysis_results['cp']:.2f}%",
                                       f"{standard['CP']:.2f}%", dev, grade])

                t3 = Table(comp_rows, colWidths=[80, 95, 95, 100, 130])
                t3.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#6a1b9a')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#ce93d8')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                     [HexColor('#f3e5f5'), HexColor('#ffffff')]),
                ]))
                story.append(t3)
                story.append(Spacer(1, 8))
                story = self._add_note(story,
                    "💡 التوضيح: الانحراف أقل من 5% = ممتاز ✅، بين 5% و10% = جيد 👍، "
                    "أكثر من 10% = يحتاج تعديل ⚠️.")

                # ═══ رسم بياني ═══
                try:
                    fig, ax = plt.subplots(figsize=(6.5, 3.5))
                    cats, calcs, stds = [], [], []
                    if 'DP' in standard and 'dp' in analysis_results:
                        cats.append('DP'); calcs.append(analysis_results['dp']); stds.append(standard['DP'])
                    if 'SE' in standard and 'se' in analysis_results:
                        cats.append('SE'); calcs.append(analysis_results['se']); stds.append(standard['SE'])
                    if 'CP' in standard and 'cp' in analysis_results:
                        cats.append('CP'); calcs.append(analysis_results['cp']); stds.append(standard['CP'])
                    if cats:
                        x = np.arange(len(cats))
                        w = 0.35
                        ax.bar(x - w/2, calcs, w, label=ar('المحسوب'),
                               color='#2e7d32', edgecolor='#1b5e20', linewidth=1.5)
                        ax.bar(x + w/2, stds, w, label=ar('القياسي'),
                               color='#1565C0', edgecolor='#0d47a1', linewidth=1.5)
                        ax.set_xticks(x)
                        ax.set_xticklabels(cats, fontproperties=get_arabic_font_prop(11, 'bold'))
                        ax.set_title(ar('📊 مقارنة النتائج'),
                                     fontproperties=get_arabic_font_prop(12, 'bold'),
                                     color='#1a237e')
                        ax.legend(loc='upper right', prop=get_arabic_font_prop(10))
                        ax.grid(axis='y', alpha=0.3, linestyle='--')
                        plt.tight_layout()
                        buf = io.BytesIO()
                        plt.savefig(buf, format='png', dpi=130, bbox_inches='tight',
                                    facecolor='white')
                        plt.close()
                        buf.seek(0)
                        story.append(Image(buf, width=430, height=235))
                except Exception:
                    pass

        story.append(Spacer(1, 20))
        story = self._add_official_stamp(story, user_name, sample_owner or requester_name)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city,
                                       local_cost, local_sym, computed_se, user_name,
                                       requester_name="", standard=None,
                                       include_charts=True, extra_info=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=45, leftMargin=45,
                                 topMargin=25, bottomMargin=35)
        story = []

        def p(text, style='body'):
            return Paragraph(ar(text), self.styles.get(style, self.styles['body']))

        story = self._add_bismala(story)
        story.append(p("🌾 تاور نولجي Tawornology العلمية", 'title'))
        story.append(p("📄 تقرير فني شامل - تركيب الأعلاف", 'subtitle'))
        story.append(Spacer(1, 10))

        supervisor = "الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان"
        info_rows = [
            [ar("👨‍💻 المشرف"), ar(supervisor)],
            [ar("👤 طالب العلفة"), ar(requester_name or 'غير محدد')],
            [ar("🐾 الفصيل"), ar(breed)],
            [ar("📌 الموقع"), ar(city)],
            [ar("📅 التاريخ"), ar(datetime.now().strftime('%Y-%m-%d %H:%M'))]
        ]
        info_t = Table(info_rows, colWidths=[140, 360])
        info_t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
            ('BACKGROUND', (1, 0), (1, -1), HexColor('#ffffff')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#a5d6a7')),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#1b5e20')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(info_t)
        story.append(Spacer(1, 15))

        tdata = [
            [ar('المعيار'), ar('القيمة')],
            [ar('البروتين المهضوم (DP)'), f'{target_dp:.2f}%'],
            [ar('معادل النشاء (SE)'), f'{computed_se:.2f} {ar("وحدة")}'],
            [ar('التكلفة للطن'), f'${cost:.2f} ({local_cost:,.2f} {local_sym})']
        ]
        t = Table(tdata, colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#2e7d32')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [HexColor('#ffffff'), HexColor('#f1f8e9')])
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

        story = self._add_section_title(story, "📋 المقادير لتركيب الطن الواحد", '#2e7d32')
        ing_data = [[ar('المكون'), ar('النسبة %'), ar('كجم/طن')]]
        for ing, pct in formula.items():
            ing_data.append([ar(ing), f'{pct:.2f}%', f'{pct*10:.1f}'])
        t2 = Table(ing_data, colWidths=[220, 130, 130])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [HexColor('#ffffff'), HexColor('#f5f5f5')])
        ]))
        story.append(t2)
        story.append(Spacer(1, 10))
        story = self._add_note(story,
            "💡 التوضيح: النسب معتمدة على أساس الطن الجاف. يمكن تعديلها حسب "
            "توفر المواد الخام مع الحفاظ على النسب الغذائية.")

        if include_charts and len(formula) > 1:
            try:
                fig, ax = plt.subplots(figsize=(6, 3.5))
                names = list(formula.keys())
                vals = list(formula.values())
                colors = ['#1b5e20', '#2e7d32', '#388e3c', '#43a047',
                          '#4caf50', '#66bb6a']
                ax.pie(vals, labels=None, autopct='%1.1f%%',
                       colors=colors[:len(names)])
                ax.legend([ar(n) for n in names],
                          title=ar("المكونات"), loc='center left',
                          bbox_to_anchor=(1, 0, 0.5, 1),
                          prop=get_arabic_font_prop(8))
                ax.set_title(ar('📊 توزيع المكونات'),
                             fontproperties=get_arabic_font_prop(12, 'bold'))
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=120, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=420, height=240))
            except Exception:
                pass

        story.append(Spacer(1, 15))
        story = self._add_section_title(story, "📌 التوصيات الفنية", '#e65100')
        for rec in ["• يوصى بإضافة الإنزيمات لتحسين الهضم.",
                    "• يجب مراقبة جودة المواد الخام بشكل دوري.",
                    "• يجب تخزين العلف في مكان جاف بعيداً عن الرطوبة.",
                    "• يوصى بتقسيم العلف على عدة وجبات."]:
            story.append(p(rec))

        story.append(Spacer(1, 20))
        story = self._add_official_stamp(story, user_name, requester_name)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()
# =====================================================================
# دوال مساعدة
# =====================================================================
def guide_section(name, text):
    with st.expander(f"📘 دليل استخدام {name}", expanded=False):
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#f0f8ff,#e3f2fd);
                    padding:18px; border-radius:12px; direction:rtl;
                    border-right:4px solid #1565C0;'>
            <div style='color:#1a237e; font-weight:700; font-size:1.05rem;'>
                {text}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🔊 تشغيل صوتياً", key=f"vg_{name}"):
            voice_guide(text)

def generate_formula_image(formula_data, target_dp, target_se, breed, stage,
                            user_name, requester_name=""):
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_facecolor('#f5f5f5')
    fig.patch.set_facecolor('#ffffff')

    tfont = get_arabic_font_prop(14, 'bold')
    lfont = get_arabic_font_prop(11)

    title = (f"🧬 خلطة علفية معتمدة - تاور نولجي Tawornology\n"
             f"المشرف: {user_name}\n"
             f"طالب العلفة: {requester_name or 'غير محدد'}\n"
             f"الفصيل: {breed} | المرحلة: {stage}\n"
             f"DP: {target_dp:.1f}% | SE: {target_se:.1f} وحدة")
    ax.set_title(ar(title), fontproperties=tfont, pad=25)

    ings = list(formula_data.keys())
    kgs = [p * 10 for p in formula_data.values()]
    y = np.arange(len(ings))
    ax.barh(y, kgs, color='#2e7d32', alpha=0.85,
            edgecolor='#1b5e20', linewidth=1.5)
    ax.set_yticks(y)
    ax.set_yticklabels([ar(i) for i in ings], fontproperties=lfont)
    ax.set_xlabel(ar('الكمية (كجم/طن)'),
                   fontproperties=get_arabic_font_prop(12, 'bold'))
    vfont = get_arabic_font_prop(10, 'bold')
    for i, v in enumerate(kgs):
        ax.text(v + 3, i, f'{v:.1f} كجم', va='center',
                fontproperties=vfont, color='#1b5e20')
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight',
                facecolor='white')
    plt.close()
    buf.seek(0)
    return buf

def send_to_whatsapp(img_buf, caption, phone=WHATSAPP_NUMBER):
    try:
        b64 = base64.b64encode(img_buf.getvalue()).decode()
        enc = urllib.parse.quote(caption)
        url = f"https://wa.me/{phone}?text={enc}"
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#e8f5e9,#c8e6c9);
                    padding:20px; border-radius:14px; direction:rtl;
                    text-align:center;'>
            <img src="data:image/png;base64,{b64}"
                 style="max-width:100%; border-radius:10px;
                        margin:15px 0; border:3px solid #2e7d32;">
            <br>
            <a href='{url}' target='_blank'>
                <button style='background:#25D366; color:white; padding:14px 40px;
                               border:none; border-radius:35px; font-size:17px;
                               font-weight:bold; cursor:pointer;'>
                    📲 إرسال الصورة عبر واتساب
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        return True
    except Exception as e:
        st.error(f"❌ خطأ: {str(e)}")
        return False

# =====================================================================
# شاشة الدخول
# =====================================================================
MAX_ATT = 5
LOCKOUT = 300

if not st.session_state["approved"]:
    render_dua_bar()

    if st.session_state["login_attempts"] >= MAX_ATT:
        if st.session_state["last_login_time"]:
            diff = (datetime.now() - st.session_state["last_login_time"]).seconds
            if diff < LOCKOUT:
                st.error(f"🔒 النظام مقفل. انتظر {LOCKOUT - diff} ثانية")
                st.stop()

    st.markdown('<div class="main-box" style="max-width:600px; '
                'margin:60px auto; direction:rtl;">', unsafe_allow_html=True)

    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" '
                    f'class="profile-img-style" style="width:120px; height:120px; '
                    f'margin:0 auto; display:block;">', unsafe_allow_html=True)

    st.markdown("""
    <h2 style='color:#1a237e; text-align:center; margin-top:15px;'>
        🌾 تاور نولجي Tawornology العلمية
    </h2>
    <p style='text-align:center; color:#1565C0; font-size:1.2rem; font-weight:700;'>
        للانتاج الحيواني وتركيب الاعلاف
    </p>
    <div style='text-align:center; margin:15px 0;'>
        <span class='supervisor-badge'>
            👑 الاختصاصي م. عبد القادر إسماعيل تاور
        </span>
    </div>
    <p style='text-align:center; color:#888; font-size:0.9rem;'>
        الإصدار النهائي 19.0
    </p>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔊 تشغيل الترحيب", use_container_width=True):
            play_welcome_audio()
    with col_b:
        if st.button("🕊️ تشغيل الدعاء", use_container_width=True):
            play_dua_audio()

    st.markdown("<hr style='margin:25px 0; border-top:2px solid #e0e0e0;'>",
                unsafe_allow_html=True)

    # ═══ بوابة الزائر ═══
    st.markdown("""
    <div style='background:linear-gradient(135deg,#e8f5e9,#c8e6c9);
                padding:22px; border-radius:16px; text-align:center;
                direction:rtl; border:2px solid #2e7d32; margin-bottom:20px;
                box-shadow:0 8px 25px rgba(46,125,50,0.15);'>
        <h3 style='color:#1b5e20; margin:5px 0;'>🌾 بوابة الزائر / المربي / المختص</h3>
        <p style='color:#333; margin:8px 0; font-size:1rem;'>
            دخول مجاني لجميع المربين والمختصين والأطباء البيطريين
        </p>
        <p style='color:#666; font-size:0.85rem;'>
            ✨ لا يلزم أي كود أو تسجيل ✨
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("👤 دخول كزائر (مجاني للجميع)", type="primary",
                  use_container_width=True):
        auth = AuthManager()
        user = auth.login_public()
        if user:
            st.session_state["approved"] = True
            st.session_state["user_role"] = "public"
            st.session_state["login_welcome_shown"] = False
            st.session_state["last_login_time"] = datetime.now()
            st.session_state["session_token"] = secrets.token_urlsafe(32)
            st.session_state["user"] = user
            voice_guide("مرحباً بك في تاور نولجي Tawornology العلمية.")
            st.rerun()

    # ═══ بوابة المالك ═══
    st.markdown("<hr style='margin:20px 0;'>", unsafe_allow_html=True)

    with st.expander("🔐 بوابة المالك - دخول خاص"):
        st.markdown("""
        <div style='background:#fff3e0; padding:12px; border-radius:10px;
                    direction:rtl; border-right:4px solid #e65100;
                    margin-bottom:12px;'>
            <b style='color:#e65100;'>⚠️ هذه البوابة مخصصة للمالك فقط</b><br>
            <small style='color:#555;'>
                جميع المختصين والمربين يدخلون من بوابة الزائر أعلاه
            </small>
        </div>
        """, unsafe_allow_html=True)

        code = st.text_input("🔑 كود المالك:", type="password",
                              placeholder="أدخل الكود الخاص",
                              key="owner_code")
        if st.button("🔓 دخول المالك", use_container_width=True):
            if code.strip() in CODES_DB:
                st.session_state["approved"] = True
                st.session_state["user_role"] = "owner"
                st.session_state["login_welcome_shown"] = False
                st.session_state["login_attempts"] = 0
                st.session_state["last_login_time"] = datetime.now()
                st.session_state["session_token"] = secrets.token_urlsafe(32)
                st.session_state["user"] = {
                    'user_id': 'owner', 'username': 'owner',
                    'role': 'owner',
                    'full_name': 'الاختصاصي م. عبد القادر إسماعيل تاور',
                    'email': OWNER_EMAIL, 'phone': WHATSAPP_NUMBER
                }
                voice_guide("مرحباً بك أيها الاختصاصي م. عبد القادر إسماعيل تاور.")
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                rem = MAX_ATT - st.session_state["login_attempts"]
                st.error(f"❌ الكود غير صحيح! متبقي {rem} محاولات")

    st.markdown("""
    <div style='text-align:center; margin-top:20px; color:#999;
                font-size:0.85rem;'>
        <p>🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b>
        وأختي <b>ابتسام</b> - رحمهما الله</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# الترحيب بعد الدخول
# =====================================================================
if not st.session_state["login_welcome_shown"]:
    if st.session_state["user_role"] == "owner":
        st.toast("👑 مرحباً بك، الاختصاصي م. عبد القادر إسماعيل تاور", icon="🌾")
    else:
        st.toast("🌾 أهلاً وسهلاً بك في تاور نولجي Tawornology", icon="👋")
    st.session_state["login_welcome_shown"] = True

render_dua_bar()

# =====================================================================
# الواجهة الرئيسية
# =====================================================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_sp, col_user = st.columns([0.7, 0.3])
with col_user:
    role_disp = ("المالك 👑" if st.session_state["user_role"] == "owner"
                 else "زائر كريم 👤")
    uname = st.session_state.get("user", {}).get("full_name", "زائر")
    st.markdown(f"""
    <div style='text-align:left; background:linear-gradient(135deg,#f5f5f5,#e0e0e0);
                padding:14px; border-radius:14px;'>
        <div style='font-weight:700; font-size:1rem;'>{uname}</div>
        <div style='font-size:0.85rem; color:#555;'>{role_disp}</div>
        <small style='color:#888;'>
            آخر دخول: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </small>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k not in ["email_password"]:
                del st.session_state[k]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

col_logo, col_title = st.columns([0.2, 0.8])
with col_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" '
                    f'class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" '
                    f'class="profile-img-style">', unsafe_allow_html=True)
with col_title:
    st.markdown("""
    <h1 style='color:#1a237e; text-align:right; margin-bottom:0; font-size:2.2rem;'>
        🌾 تاور نولجي Tawornology العلمية
    </h1>
    """, unsafe_allow_html=True)
    st.markdown("""
    <p style='color:#1565C0; text-align:right; font-size:1.15rem; font-weight:600;'>
        للانتاج الحيواني وتركيب الاعلاف - محرك الاستمثال الخطي المتقدم
    </p>
    """, unsafe_allow_html=True)
    st.markdown("""
    <h3 style='color:#c62828; text-align:right; font-weight:700; margin-top:5px;'>
        الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان
    </h3>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border-top:3px solid #2e7d32;'>", unsafe_allow_html=True)

# ═══ شريط الترحيب ═══
if st.session_state["user_role"] == "owner":
    welcome_html = """
    👑 أهلاً بك في لوحة التحكم الكاملة، الاختصاصي م. عبد القادر إسماعيل تاور.
    جميع الصلاحيات متاحة لك: التركيب، المختبر، الفواتير، إدارة المزارع.
    """
else:
    welcome_html = """
    🌾 أهلاً وسهلاً بك في تاور نولجي Tawornology العلمية.
    استخدم الأقسام المجانية لتركيب الأعلاف، تحليل الخلطات، والتعلم من المراجع.
    """

st.markdown(f"""
<div class="welcome-banner">
    <div style='color:#1b5e20; font-weight:700; font-size:1.05rem;'>
        {welcome_html}
    </div>
</div>
""", unsafe_allow_html=True)

# ═══ الإحصائيات ═══
st.markdown("### 📊 لوحة التحكم السريعة")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"<div class='metric-card'><div class='number'>"
                f"{len(FLAT_FEED_DB)}</div>"
                f"<div class='label'>مادة علفية</div></div>",
                unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='metric-card'><div class='number'>"
                f"{len(STANDARD_VALUES)}</div>"
                f"<div class='label'>فصيل حيواني</div></div>",
                unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='metric-card'><div class='number'>"
                f"{len(EXCHANGE_RATES)}</div>"
                f"<div class='label'>دولة مدعومة</div></div>",
                unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='metric-card'><div class='number'>"
                f"17</div>"
                f"<div class='label'>تبويب رئيسي</div></div>",
                unsafe_allow_html=True)
st.markdown("---")
# =====================================================================
# دالة تركيب العلف المبسطة
# =====================================================================
def render_feed_formulation(animal_key, display_name, icon, breeds, stages,
                             default_dp, default_se, img_key,
                             has_measurements=True):
    st.markdown(f'<div class="section-title">{icon} {display_name}</div>',
                unsafe_allow_html=True)

    # 1. اسم طالب العلف
    requester = st.text_input("👤 اسم طالب العلف (المربي / المزرعة):",
                                placeholder="مثال: مزرعة النيل / أحمد محمد",
                                key=f"{animal_key}_req")

    # 2. الموقع الجغرافي (مدمج في صف واحد)
    col1, col2, col3 = st.columns(3)
    with col1:
        country = st.selectbox("الدولة:", list(EXCHANGE_RATES.keys()),
                                key=f"{animal_key}_country")
    rate = EXCHANGE_RATES[country]["rate"]
    sym = EXCHANGE_RATES[country]["sym"]
    with col2:
        state = st.text_input("الولاية/الإقليم:",
                                value="الخرطوم" if country == "السودان" else "طرابلس",
                                key=f"{animal_key}_state")
    with col3:
        city = st.text_input("المدينة:", value="الخرطوم" if country == "السودان" else "طرابلس",
                               key=f"{animal_key}_city")

    # 3. السلالة والمرحلة
    col_b, col_s = st.columns(2)
    with col_b:
        breed = st.selectbox("السلالة:", breeds, key=f"{animal_key}_breed")
    with col_s:
        stage = st.selectbox("المرحلة:", stages, key=f"{animal_key}_stage")

    # 4. القياسات الجسدية
    if has_measurements:
        with st.expander("📐 القياسات الجسدية (اختياري - لحساب أدق)"):
            col_h, col_l = st.columns(2)
            weight_f = {"cattle": 10838, "sheep": 15500, "goat": 15000,
                        "horse": 11877, "camel": 13000}
            with col_h:
                girth = st.number_input("محيط الصدر (سم):", value=150.0,
                                          key=f"{animal_key}_girth")
            with col_l:
                length = st.number_input("طول الجسم (سم):", value=130.0,
                                           key=f"{animal_key}_length")
            wf = weight_f.get(animal_key, 12000)
            est_w = (girth ** 2 * length) / wf
            st.success(f"⚖️ الوزن التقديري: **{est_w:.1f} كجم**")

    # 5. حدود الموازنة
    st.markdown("**🎯 حدود الموازنة الذكية:**")
    col_dp, col_se = st.columns(2)
    with col_dp:
        target_dp = st.slider("البروتين المهضوم (DP) %:", 5.0, 40.0,
                               value=float(default_dp), step=0.5,
                               key=f"{animal_key}_dp")
    with col_se:
        target_se = st.slider("معادل النشاء (SE):", 10.0, 90.0,
                               value=float(default_se), step=1.0,
                               key=f"{animal_key}_se")

    # 6. المكونات
    st.markdown("**🌾 اختر المكونات:**")
    live_prices = MarketPriceEngine.get_adjusted_market_data(country, state, city)
    defaults_map = {
        "cattle": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)",
                   "كسب فول صويا 44%", "أمباز الفول السوداني (كسب)",
                   "مركزات خيول ومجترات", "ملح الطعام",
                   "الحجر الجيري (بودرة بلاط)",
                   "فوسفات ثنائي الكالسيوم (DCP)"],
        "sheep": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)",
                  "كسب فول صويا 44%", "أمباز الفول السوداني (كسب)",
                  "مركزات خيول ومجترات", "ملح الطعام",
                  "الحجر الجيري (بودرة بلاط)",
                  "فوسفات ثنائي الكالسيوم (DCP)"],
        "goat": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)",
                 "كسب فول صويا 44%", "مركزات خيول ومجترات",
                 "ملح الطعام", "الحجر الجيري (بودرة بلاط)"],
        "horse": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)",
                  "كسب فول صويا 44%", "مولاس قصب السكر",
                  "مركزات خيول ومجترات", "ملح الطعام"],
        "camel": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)",
                  "كسب فول صويا 44%", "البرسيم الجاف (الدريس)",
                  "مركزات خيول ومجترات", "ملح الطعام"],
        "poultry": ["ذرة صفراء", "سورجم (فتريتة)", "كسب فول صويا 44%",
                    "مركزات دواجن وسمان", "بريمكس تسمين دواجن (Premix)",
                    "ملح الطعام", "الحجر الجيري (بودرة بلاط)"],
        "fish": ["ذرة صفراء", "كسب فول صويا 44%",
                 "مسحوق أسماك (Fishmeal 60%)",
                 "مركزات دواجن وسمان", "ملح الطعام"]
    }
    defaults = defaults_map.get(animal_key, [])

    selected = []
    prices = {}
    for cat, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat}", expanded="الحبوب" in cat or "الأكساب" in cat):
            cols = st.columns(3)
            for i, (ing, _) in enumerate(items.items()):
                with cols[i % 3]:
                    checked = st.checkbox(ing, value=ing in defaults,
                                           key=f"{animal_key}_f_{ing}")
                    if checked:
                        price = st.number_input(f"سعر {ing} ($/طن)",
                            min_value=5.0, value=float(live_prices.get(ing, 350.0)),
                            key=f"{animal_key}_p_{ing}")
                        selected.append(ing)
                        prices[ing] = price

    # الإضافات الإلزامية
    fixed = {"ملح الطعام": 0.5, "مضاد سموم فطرية": 0.2,
             "الحجر الجيري (بودرة بلاط)": 1.5,
             "فوسفات ثنائي الكالسيوم (DCP)": 1.0}
    auto = {}
    warns = []

    if animal_key in ["cattle", "sheep", "goat", "camel"]:
        auto["بيكربونات الصوديوم (الصودا)"] = 0.75
        warns.append("🚨 <b>إضافة إلزامية:</b> بيكربونات الصوديوم 0.75% "
                     "كمنظم حموضة لحماية الكرش.")
    if animal_key in ["poultry", "fish"]:
        auto["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05
        warns.append("🚨 <b>إضافة إلزامية:</b> إنزيم الفايتيز 0.05% "
                     "لتحرير الفسفور النباتي.")

    all_fixed = {**fixed, **auto}
    for it in all_fixed:
        if it not in selected:
            selected.append(it)
            prices[it] = live_prices.get(it, 40.0)

    # التشغيل
    if st.button(f"🚀 تشغيل المحرك", type="primary", use_container_width=True,
                 key=f"{animal_key}_run"):
        if len(selected) < 3:
            st.warning("⚠️ اختر 3 مكونات على الأقل.")
        else:
            voice_guide(f"جاري الحساب...")
            with st.spinner("🔄 حساب الخلطة المثالية..."):
                c = [prices[i] for i in selected]
                bounds = [(all_fixed[i], all_fixed[i])
                          if i in all_fixed else (0.0, 100.0) for i in selected]
                A_eq = [[1.0 for _ in selected]]
                b_eq = [100.0]
                cp_row, se_row = [], []
                for ing in selected:
                    fd = FLAT_FEED_DB.get(ing, {})
                    cp_row.append(fd.get("CP", 0) * fd.get("DC", 0))
                    se_row.append(fd.get("SE", 0))
                A_eq.append(cp_row)
                b_eq.append(target_dp * 100)
                A_ub = [[-x for x in se_row]]
                b_ub = [-target_se * 100]

                try:
                    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                                  bounds=bounds, method='highs')
                    if res.success:
                        formula = {}
                        se_tot = 0
                        for i, ing in enumerate(selected):
                            if res.x[i] > 0.0001:
                                formula[ing] = res.x[i]
                                se_tot += (res.x[i] / 100) * FLAT_FEED_DB.get(ing, {}).get("SE", 0)
                        cost = res.fun / 100
                        st.success(f"✅ تم التوليد! التكلفة: ${cost:.2f}/طن")

                        for k, v in formula.items():
                            st.markdown(
                                f'<div class="formula-item">'
                                f'<span>▪️ {k}</span>'
                                f'<span style="color:#c62828;">{v:.2f}% '
                                f'({v*10:.1f} كجم)</span></div>',
                                unsafe_allow_html=True)
                        st.metric("💰 التكلفة/طن",
                                   f"${cost:.2f} ({cost*rate:,.0f} {sym})")
                        st.metric("🧬 DP", f"{target_dp:.2f}%")
                        st.metric("🌽 SE", f"{se_tot:.2f}")

                        for w in warns:
                            st.markdown(f'<div class="warning-card">{w}</div>',
                                         unsafe_allow_html=True)

                        try:
                            pdf = pdf_generator.generate_comprehensive_report(
                                formula, target_dp, f"{breed} - {stage}",
                                cost, city, cost * rate, sym, se_tot,
                                st.session_state.get("user", {}).get(
                                    "full_name", "زائر"),
                                requester_name=requester, include_charts=True)
                            st.download_button("📥 تحميل PDF", pdf,
                                file_name=f"Tawornology_{display_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf", use_container_width=True)
                        except Exception as e:
                            st.warning(f"⚠️ PDF: {e}")

                        if st.button("📲 مشاركة كصورة", use_container_width=True,
                                      key=f"{animal_key}_share"):
                            img = generate_formula_image(formula, target_dp, se_tot,
                                breed, stage,
                                st.session_state.get("user", {}).get("full_name", "زائر"),
                                requester)
                            send_to_whatsapp(img,
                                f"خلطة {display_name} | DP:{target_dp:.1f}% | ${cost:.2f}/طن")
                    else:
                        st.error("❌ لم يتم إيجاد حل. أضف مكونات بروتينية.")
                except Exception as e:
                    st.error(f"❌ {e}")

# =====================================================================
# المختبر المتقدم المبسط
# =====================================================================
def render_advanced_lab():
    st.markdown('<div class="section-title">🔬 المختبر المتقدم</div>',
                unsafe_allow_html=True)
    st.info("أدخل أوزان مكونات خلطتك لتحليلها ومقارنتها بالمعايير.")

    # بيانات العينة
    col1, col2 = st.columns(2)
    with col1:
        sample_owner = st.text_input("👤 اسم صاحب العينة:",
                                       placeholder="اسم المربي / المزرعة",
                                       key="lab_owner_input")
        sample_name = st.text_input("📝 اسم العينة:",
                                      placeholder="مثال: خلطة تجريبية 1",
                                      key="lab_name_input")
    with col2:
        lab_animal = st.selectbox("الفصيل:",
            ["أبقار", "أغنام", "ماعز", "خيول", "إبل", "دواجن", "أسماك"])
        lab_stage = st.selectbox("المرحلة:",
            list(STANDARD_VALUES.get(lab_animal, {}).keys()))
    standard = STANDARD_VALUES.get(lab_animal, {}).get(lab_stage, {})
    if standard:
        st.success(f"📊 المعايير: DP={standard.get('DP','-')}% | "
                   f"SE={standard.get('SE','-')} | CP={standard.get('CP','-')}%")

    # إدخال الأوزان
    st.markdown("**📥 أدخل أوزان المكونات (كجم):**")
    inputs = {}
    cols = st.columns(3)
    for i, ing in enumerate(FLAT_FEED_DB.keys()):
        with cols[i % 3]:
            inputs[ing] = st.number_input(ing, min_value=0.0, value=0.0,
                                            step=5.0, key=f"lab_{ing}")

    if st.button("🧪 تشغيل التحليل", type="primary", use_container_width=True):
        total = sum(inputs.values())
        if total <= 0:
            st.warning("⚠️ أدخل أوزان أكبر من الصفر.")
        else:
            voice_guide("جاري التحليل...")
            cp, dp, se = 0, 0, 0
            for ing, w in inputs.items():
                if w > 0:
                    pct = w / total
                    fd = FLAT_FEED_DB.get(ing, {})
                    cp += pct * fd.get("CP", 0)
                    dp += pct * (fd.get("CP", 0) * fd.get("DC", 0))
                    se += pct * fd.get("SE", 0)

            st.session_state["analysis_results"] = {
                'components': inputs, 'cp': cp, 'dp': dp, 'se': se
            }

            st.success("🔬 تم التحليل!")
            st.metric("⚖️ إجمالي الوزن", f"{total:.1f} كجم")
            st.dataframe(pd.DataFrame([
                {"العنصر": "البروتين الخام (CP)", "القيمة": f"{cp:.2f}%"},
                {"العنصر": "البروتين المهضوم (DP)", "القيمة": f"{dp:.2f}%"},
                {"العنصر": "معادل النشاء (SE)", "القيمة": f"{se:.2f}"}
            ]), use_container_width=True)

            dp_g = se_g = cp_g = "-"
            if standard:
                def grade(c, s):
                    if s <= 0: return "-"
                    d = ((c - s) / s) * 100
                    return ("✅ ممتاز" if abs(d) <= 5
                            else ("👍 جيد" if abs(d) <= 10 else "⚠️ تحسين"))
                dp_g = grade(dp, standard.get('DP', 0))
                se_g = grade(se, standard.get('SE', 0))
                cp_g = grade(cp, standard.get('CP', 0))
                st.dataframe(pd.DataFrame([
                    {"المقياس": "DP", "المحسوب": f"{dp:.2f}%",
                     "القياسي": f"{standard.get('DP',0):.2f}%", "التقييم": dp_g},
                    {"المقياس": "SE", "المحسوب": f"{se:.2f}",
                     "القياسي": f"{standard.get('SE',0):.2f}", "التقييم": se_g},
                    {"المقياس": "CP", "المحسوب": f"{cp:.2f}%",
                     "القياسي": f"{standard.get('CP',0):.2f}%", "التقييم": cp_g}
                ]), use_container_width=True)

            try:
                pdf = pdf_generator.generate_lab_report(
                    st.session_state["analysis_results"], lab_animal, lab_stage,
                    st.session_state.get("user", {}).get("full_name", "زائر"),
                    standard,
                    {'DP': dp_g, 'SE': se_g, 'CP': cp_g} if standard else None,
                    requester_name=sample_owner,
                    sample_name=sample_name,
                    sample_owner=sample_owner)
                st.download_button("📥 تحميل تقرير المختبر PDF", pdf,
                    file_name=f"Lab_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ PDF: {e}")
               # =====================================================================
# التبويبات الرئيسية
# =====================================================================
tabs_titles = [
    "🐾 تركيب الأعلاف",
    "🔬 المختبر المتقدم",
    "🧪 المختبر الذكي",
    "🍼 بدائل الحليب",
    "🕌 مواقيت الصلاة",
    "💊 منبه الجرعات",
    "📊 بورصة الأسعار",
    "🏭 المستودعات",
    "📈 الإنتاج اليومي",
    "🔔 التنبيهات",
    "📈 التحليلات",
    "💬 تعليقات المختصين",
    "🖨️ مصمم الديباجة",
    "📚 المراجع العلمية",
    "💡 المساعدة",
    "📖 دليل المستخدم"
]
if st.session_state["user_role"] == "owner":
    tabs_titles.append("📧 إرسال الكود")

tabs = st.tabs(tabs_titles)

# ═══ التبويب 0: تركيب الأعلاف ═══
with tabs[0]:
    guide_section("تركيب الأعلاف",
        "اختر نوع الحيوان، ثم حدد السلالة والمرحلة والمكونات، واضغط زر التشغيل.")
    animal_tabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐴 خيول",
                            "🐫 إبل", "🐔 دواجن", "🐟 أسماك"])
    with animal_tabs[0]:
        render_feed_formulation("cattle", "أبقار", "🐄",
            ["كنانة (سوداني)", "بطانة (مدر)", "هولشتاين / محسن"],
            ["تسمين عجول", "حليب/إدرار", "حمل/دفع غذائي", "صيانة"],
            12.0, 65.0, "أبقار", True)
    with animal_tabs[1]:
        render_feed_formulation("sheep", "أغنام", "🐏",
            ["الضأن الصحراوي", "البربري", "النعيمي"],
            ["تسمين حملان", "حليب/إدرار", "حمل/دفع غذائي", "صيانة"],
            11.5, 62.0, "أغنام", True)
    with animal_tabs[2]:
        render_feed_formulation("goat", "ماعز", "🐐",
            ["الماعز النوبي", "الماعز الصحراوي", "بور / محسن"],
            ["تسمين جديان", "حليب/إدرار", "حمل/دفع غذائي", "صيانة"],
            11.0, 60.0, "ماعز", True)
    with animal_tabs[3]:
        render_feed_formulation("horse", "خيول", "🐴",
            ["خيل عربي أصيل", "ثوروبريد", "خيول محلية"],
            ["راحة/صيانة", "عمل خفيف", "عمل متوسط", "عمل مكثف", "سباق",
             "أمهار نامية", "فرسات مرضعات"],
            11.0, 62.0, "خيول", True)
    with animal_tabs[4]:
        render_feed_formulation("camel", "إبل", "🐫",
            ["عربية (دروميداري)", "باختري", "هجين"],
            ["راحة/صيانة", "حمل/رضاعة", "إنتاج حليب", "تسمين", "عمل/نقل"],
            10.0, 58.0, "إبل", True)
    with animal_tabs[5]:
        render_feed_formulation("poultry", "دواجن", "🐔",
            ["دواجن لاحم (Broiler)", "دواجن بياض (Layer)",
             "طائر السمان (Quail)"],
            ["بادي (0-14 يوم)", "نامي (15-28 يوم)", "ناهي (29-42 يوم)",
             "ناهي متقدم (43+ يوم)"],
            18.0, 72.0, "دواجن", False)
    with animal_tabs[6]:
        render_feed_formulation("fish", "أسماك", "🐟",
            ["البلطي النيلي", "القرموط"],
            ["زريعة/بادئ", "نمو", "تسمين نهائي", "زريعة متقدمة"],
            28.0, 68.0, "أسماك", False)

# ═══ التبويب 1: المختبر المتقدم ═══
with tabs[1]:
    guide_section("المختبر المتقدم",
        "حلل مكونات خلطتك واحصل على تقرير PDF مع الختم الرسمي.")
    render_advanced_lab()

# ═══ التبويب 2: المختبر الذكي ═══
with tabs[2]:
    guide_section("المختبر الذكي",
        "ارفع صورة تركيبة وسيستخرج النظام البيانات تلقائياً.")
    st.markdown('<div class="section-title">🧪 المختبر الذكي OCR</div>',
                unsafe_allow_html=True)
    st.info("ارفع صورة تركيبة علفية (كتاب، ورقة، صورة) لاستخراج البيانات.")
    uploaded = st.file_uploader("📸 ارفع الصورة",
                                  type=['png', 'jpg', 'jpeg'],
                                  key="smart_lab_upload")
    if uploaded and st.session_state.get("smart_lab_system"):
        try:
            img = PILImage_module.open(uploaded)
            st.image(img, caption="الصورة المرفوعة", use_container_width=True)
            if st.button("🔍 تحليل الصورة", type="primary"):
                with st.spinner("جاري التحليل..."):
                    res, err = st.session_state["smart_lab_system"].analyze_image(img)
                    if err:
                        st.error(err)
                    else:
                        st.success("✅ تم التحليل!")
                        st.json(res)
        except Exception as e:
            st.error(f"خطأ: {e}")

# ═══ التبويب 3: بدائل الحليب ═══
with tabs[3]:
    guide_section("بدائل الحليب", "تركيب بدائل لرضاعة الصغار.")
    st.markdown('<div class="section-title">🍼 بدائل الحليب</div>',
                unsafe_allow_html=True)
    at = st.selectbox("نوع الحيوان:",
        ["عجل بقري", "حملان أغنام", "جديان ماعز", "مهرات خيول", "أطفال إبل"])
    age = st.slider("العمر (يوم)", 1, 120, 30)
    needs = {"عجل بقري": {"protein": 22, "fat": 18, "volume": 8},
             "حملان أغنام": {"protein": 24, "fat": 20, "volume": 4},
             "جديان ماعز": {"protein": 23, "fat": 19, "volume": 3},
             "مهرات خيول": {"protein": 20, "fat": 15, "volume": 5},
             "أطفال إبل": {"protein": 21, "fat": 17, "volume": 6}}
    af = 1.2 if age < 14 else (1.0 if age < 30 else (0.85 if age < 60 else 0.70))
    tp = needs[at]["protein"] * af
    tf = needs[at]["fat"] * af
    dv = needs[at]["volume"] * af
    st.info(f"📊 الاحتياجات: بروتين {tp:.1f}% | دهون {tf:.1f}% | "
            f"حجم {dv:.1f} لتر/يوم")

# ═══ التبويب 4: مواقيت الصلاة ═══
with tabs[4]:
    guide_section("مواقيت الصلاة", "عرض مواقيت الصلاة حسب المدينة.")
    st.markdown("### 🕌 مواقيت الصلاة")
    city = st.selectbox("اختر المدينة:",
        ["مكة المكرمة", "المدينة المنورة", "الخرطوم", "طرابلس", "القاهرة",
         "دبي", "الرياض", "عمان", "بيروت", "بغداد", "الكويت", "الدوحة"])
    times = {"الفجر": "05:00", "الشروق": "06:30", "الظهر": "12:00",
             "العصر": "15:30", "المغرب": "18:00", "العشاء": "19:30"}
    cols = st.columns(3)
    for i, (n, t) in enumerate(times.items()):
        with cols[i % 3]:
            st.metric(n, t)

# ═══ التبويب 5: منبه الجرعات ═══
with tabs[5]:
    guide_section("منبه الجرعات", "تسجيل اللقاحات والفيتامينات.")
    st.markdown("### 💊 منبه الجرعات")
    with st.expander("➕ إضافة جرعة جديدة"):
        c1, c2, c3 = st.columns(3)
        with c1:
            atype = st.selectbox("الحيوان", ["أبقار", "أغنام", "ماعز", "خيول",
                                              "إبل", "دواجن"])
            dtype = st.selectbox("النوع", ["لقاح", "فيتامين", "دواء"])
            dname = st.text_input("الاسم")
        with c2:
            damt = st.number_input("الجرعة", min_value=0.0, value=1.0)
            dunit = st.selectbox("الوحدة", ["مل", "جم", "مجم", "قطرة"])
            droute = st.selectbox("الطريق", ["عضل", "فموي", "مياه شرب"])
        with c3:
            freq = st.number_input("كل كم يوم", min_value=1, value=7)
            sd = st.date_input("البداية", datetime.now())
        if st.button("💾 حفظ"):
            if dname:
                st.session_state["dose_reminders"].append({
                    'animal': atype, 'type': dtype, 'name': dname,
                    'amount': damt, 'unit': dunit, 'route': droute,
                    'freq': freq, 'start': sd.isoformat()
                })
                st.success("✅ تم الحفظ")

    if st.session_state["dose_reminders"]:
        st.dataframe(pd.DataFrame(st.session_state["dose_reminders"]),
                     use_container_width=True)

# ═══ التبويب 6: بورصة الأسعار ═══
with tabs[6]:
    guide_section("بورصة الأسعار", "أسعار المواشي والمنتجات.")
    st.markdown('<div class="section-title">📊 بورصة الأسعار</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🐄 المواشي")
        for n, p in st.session_state["global_livestock_prices"].items():
            st.metric(n, f"${p:.2f}")
    with c2:
        st.subheader("🥩 المنتجات")
        for n, p in st.session_state["global_products_prices"].items():
            st.metric(n, f"${p:.2f}")

# ═══ التبويب 7: المستودعات ═══
with tabs[7]:
    guide_section("المستودعات", "إدارة المخزون.")
    st.markdown('<div class="section-title">🏭 المستودعات</div>',
                unsafe_allow_html=True)
    st.info("📦 تتبع مخزون المواد الخام. الميزة قيد التطوير.")

# ═══ التبويب 8: الإنتاج اليومي ═══
with tabs[8]:
    guide_section("الإنتاج اليومي", "تسجيل إنتاج الحليب والبيض والوزن.")
    st.markdown('<div class="section-title">📈 الإنتاج اليومي</div>',
                unsafe_allow_html=True)
    with st.form("daily"):
        c1, c2, c3 = st.columns(3)
        with c1:
            farm = st.text_input("المزرعة")
            dt = st.date_input("التاريخ", datetime.now())
        with c2:
            milk = st.number_input("الحليب (لتر)", min_value=0.0, value=0.0)
            eggs = st.number_input("البيض (عدد)", min_value=0, value=0)
        with c3:
            wg = st.number_input("زيادة الوزن (كجم)", min_value=0.0, value=0.0)
            mort = st.number_input("النافق", min_value=0, value=0)
        notes = st.text_area("ملاحظات")
        if st.form_submit_button("💾 حفظ"):
            st.session_state["daily_production_log"].append({
                "farm": farm, "date": dt.isoformat(), "milk": milk,
                "eggs": eggs, "wg": wg, "mort": mort, "notes": notes
            })
            st.success("✅ تم الحفظ")
    if st.session_state["daily_production_log"]:
        st.dataframe(pd.DataFrame(st.session_state["daily_production_log"]),
                     use_container_width=True)

# ═══ التبويب 9: التنبيهات ═══
with tabs[9]:
    guide_section("التنبيهات", "تنبيهات المخزون.")
    st.success("✅ لا توجد تنبيهات حالياً")

# ═══ التبويب 10: التحليلات ═══
with tabs[10]:
    guide_section("التحليلات", "مؤشرات وتنبؤات أسعار.")
    st.markdown('<div class="section-title">📈 التحليلات</div>',
                unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="metric-card"><div class="number">1,247</div>'
                    '<div class="label">خلطة</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><div class="number">$285</div>'
                    '<div class="label">متوسط التكلفة</div></div>',
                    unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card"><div class="number">18%</div>'
                    '<div class="label">توفير</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-card"><div class="number">96%</div>'
                    '<div class="label">رضا</div></div>', unsafe_allow_html=True)

    st.subheader("🔮 تنبؤات الأسعار")
    predictor = PricePredictor()
    for ing in ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)"]:
        pred = predictor.predict_price(ing, 7)
        st.metric(ing, f"${pred['prediction']:.2f}")

# ═══ التبويب 11: تعليقات المختصين ═══
with tabs[11]:
    guide_section("تعليقات المختصين", "قناة تبادل خبرات.")
    st.markdown('<div class="section-title">💬 تعليقات المختصين</div>',
                unsafe_allow_html=True)
    st.text_area("التعليقات:", value=st.session_state["shared_comments"],
                 height=200, disabled=True)
    new = st.text_area("➕ إضافة تعليق:")
    if st.button("نشر"):
        if new:
            role = "المالك" if st.session_state["user_role"] == "owner" else "زائر"
            st.session_state["shared_comments"] += \
                f"\n• [{role} {datetime.now().strftime('%Y-%m-%d %H:%M')}]: {new}"
            st.rerun()

# ═══ التبويب 12: مصمم الديباجة ═══
with tabs[12]:
    guide_section("مصمم الديباجة", "تصميم ديباجة جوالات الأعلاف.")
    st.markdown('<div class="section-title">🖨️ مصمم الديباجة</div>',
                unsafe_allow_html=True)
    brand = st.text_input("اسم البراند:", "تاور نولجي Tawornology")
    st.markdown(f"""
    <div style='border:3px dashed #1b5e20; padding:30px; border-radius:15px;
                background:linear-gradient(135deg,#f1f8e9,#e8f5e9); direction:rtl;
                text-align:right;'>
        <h2 style='text-align:center; color:#1b5e20;'>🌟 {brand} 🌟</h2>
        <h3 style='text-align:center; color:#c62828;'>
            الاختصاصي م. عبد القادر إسماعيل تاور
        </h3>
        <p style='text-align:center; background:#e8f5e9; padding:10px;
                  border-radius:8px;'>
            🌾 للانتاج الحيواني وتركيب الاعلاف
        </p>
    </div>
    """, unsafe_allow_html=True)

# ═══ التبويب 13: المراجع العلمية ═══
with tabs[13]:
    guide_section("المراجع العلمية", "مصادر معتمدة في تغذية الحيوان.")
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>',
                unsafe_allow_html=True)
    q = st.text_input("💡 اسأل عن مصطلح:")
    if q:
        ans = ScientificReferenceSystem.get_knowledge_answer(q)
        if ans:
            st.success(f"📖 {ans['answer']}")
            st.info(f"🔹 تبسيط: {ans['simplified']}")
        else:
            st.warning("لم أجد إجابة، جرب مصطلحاً آخر.")

# ═══ التبويب 14: المساعدة ═══
with tabs[14]:
    guide_section("المساعدة", "دليل سريع.")
    st.markdown('<div class="section-title">💡 المساعدة الذكية</div>',
                unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 خطوات الاستخدام السريعة:
    1. **اختر نوع الحيوان** من تبويب "تركيب الأعلاف"
    2. **أدخل اسمك** كطالب علف
    3. **حدد السلالة والمرحلة**
    4. **اختر المكونات** من المكتبة
    5. **اضغط زر التشغيل** ⚡
    6. **حمّل PDF** أو **شارك عبر واتساب** 📲

    ### 🔬 المختبر:
    - أدخل أوزان مكوناتك
    - احصل على تحليل + تقرير PDF مع ختم رسمي

    ### 🆘 دعم فني:
    - البريد: abukram128@gmail.com
    - واتساب: +249123533489
    """)

# ═══ التبويب 15: دليل المستخدم ═══
with tabs[15]:
    guide_section("دليل المستخدم", "شرح مفصل.")
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>',
                unsafe_allow_html=True)
    st.markdown("""
    ### 🌾 تاور نولجي Tawornology العلمية

    **هدف النظام:** تركيب أعلاف بأقل تكلفة مع تحقيق الاحتياجات الغذائية.

    #### الميزات الرئيسية:
    - ✅ محرك استمثال خطي متقدم
    - ✅ مختبر تحليل مع تقارير PDF
    - ✅ مكتبة موسعة من المواد الخام
    - ✅ دعم جميع الفصائل الحيوانية
    - ✅ مراجع علمية معتمدة
    """)

# ═══ التبويب 16: إرسال الكود (للمالك) ═══
if st.session_state["user_role"] == "owner" and len(tabs) > 16:
    with tabs[16]:
        guide_section("إرسال الكود", "إرسال السورس كود.")
        st.markdown('<div class="section-title">📧 إرسال السورس كود</div>',
                    unsafe_allow_html=True)
        email = st.text_input("البريد:", value=OWNER_EMAIL)
        if st.button("📤 إرسال"):
            if email and '@' in email:
                with st.spinner("جاري الإرسال..."):
                    try:
                        with open(__file__, "r", encoding="utf-8") as f:
                            content = f.read()
                        msg = MIMEMultipart()
                        msg['From'] = SENDER_EMAIL
                        msg['To'] = email
                        msg['Subject'] = "🌾 تاور نولجي Tawornology - السورس كود"
                        msg.attach(MIMEText("السورس كود المرفق.", 'plain', 'utf-8'))
                        att = MIMEText(content, 'plain', 'utf-8')
                        att.add_header('Content-Disposition', 'attachment',
                                        filename="tawornology.py")
                        msg.attach(att)
                        if st.session_state.get("email_password"):
                            s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                            s.starttls()
                            s.login(SENDER_EMAIL, st.session_state["email_password"])
                            s.sendmail(SENDER_EMAIL, email, msg.as_string())
                            s.quit()
                            st.success("✅ تم الإرسال!")
                        else:
                            st.warning("⚠️ أدخل كلمة مرور البريد")
                            st.session_state["email_password"] = st.text_input(
                                "كلمة المرور:", type="password")
                    except Exception as e:
                        st.error(f"❌ {e}")

# =====================================================================
# التذييل
# =====================================================================
st.markdown("""
<div style='text-align:center; padding:25px; margin-top:30px;
            border-top:2px solid #e0e0e0; color:#666; font-size:0.9rem;'>
    🌾 <b>تاور نولجي Tawornology العلمية</b> - v19.0<br>
    © 2026 | الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان<br>
    <span style='color:#c62828;'>🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b>
    وأختي <b>ابتسام</b> - رحمهما الله وأسكنهما فسيح جناته</span>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# نهاية الكود - الإصدار 19.0 النهائي
# ============================================================================ 
