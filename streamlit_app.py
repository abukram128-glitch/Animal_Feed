# ============================================================================
# 🌾 تاور نولجي Tawornology العلمية - الإصدار النهائي v18.0
# ============================================================================
# 🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله
# 👨‍💻 المشرف: الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان
# ============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import json, os, base64, smtplib, time, urllib.parse, hashlib, secrets, io, sqlite3, warnings, re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scipy.optimize import linprog
from datetime import datetime, timedelta
from functools import lru_cache

warnings.filterwarnings('ignore')

# ========== PDF ==========
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import arabic_reshaper
from bidi.algorithm import get_display
import qrcode
from PIL import Image as PILImage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# ========== الصوت ==========
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# ========== OCR (اختياري) ==========
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ============================================================================
# الإعدادات
# ============================================================================
st.set_page_config(
    page_title="تاور نولجي Tawornology العلمية",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== أكواد الدخول ==========
CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2024": {"role": "veterinarian", "name": "الطبيب البيطري", "level": 2},
    "2025": {"role": "nutritionist", "name": "أخصائي التغذية", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

# ========== البريد ==========
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"
SENDER_PASSWORD = "oynz rdli tsdy ekdq"   # App Password
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

@st.cache_data(ttl=3600)
def get_image_base64(paths):
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                pass
    return None

img_base64 = get_image_base64(PHOTO_OPTIONS)

# ============================================================================
# معالج النصوص العربية
# ============================================================================
class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=2000)
    def fix(text):
        if not text:
            return ""
        try:
            return get_display(arabic_reshaper.reshape(str(text)))
        except Exception:
            return str(text)

ar = ArabicTextProcessor()

# ============================================================================
# قاعدة البيانات
# ============================================================================
class DatabaseManager:
    def __init__(self, db_path="tawornology_v18.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas (
            formula_id TEXT PRIMARY KEY, formula_name TEXT, animal_type TEXT,
            breed TEXT, stage TEXT, target_dp REAL, target_se REAL,
            ingredients TEXT, total_cost REAL, requester TEXT, created_date TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS lab_results (
            result_id TEXT PRIMARY KEY, sample_name TEXT, animal TEXT, stage TEXT,
            cp REAL, dp REAL, se REAL, ndf REAL, adf REAL, ee REAL, ash REAL,
            image_path TEXT, notes TEXT, analyst TEXT, created_date TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS invoices (
            invoice_id TEXT PRIMARY KEY, customer TEXT, formula_name TEXT,
            quantity REAL, unit_price REAL, total REAL, status TEXT, created_date TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS price_history (
            record_id TEXT PRIMARY KEY, ingredient TEXT, price REAL,
            country TEXT, city TEXT, recorded_date TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT PRIMARY KEY, item_name TEXT UNIQUE, quantity REAL,
            min_threshold REAL, unit TEXT, updated_date TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS daily_production (
            log_id TEXT PRIMARY KEY, farm TEXT, log_date TEXT,
            milk REAL, eggs INTEGER, weight_gain REAL, mortality INTEGER, notes TEXT
        )''')
        conn.commit()
        conn.close()
    
    def execute(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        result = c.execute(query, params)
        conn.commit()
        data = result.fetchall()
        conn.close()
        return data
    
    def insert(self, table, data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        cols = ', '.join(data.keys())
        phs = ', '.join(['?' for _ in data])
        c.execute(f"INSERT INTO {table} ({cols}) VALUES ({phs})", list(data.values()))
        conn.commit()
        conn.close()
    
    def get(self, table, conditions=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if conditions:
            where = ' AND '.join([f"{k}=?" for k in conditions.keys()])
            result = c.execute(f"SELECT * FROM {table} WHERE {where}", list(conditions.values()))
        else:
            result = c.execute(f"SELECT * FROM {table}")
        data = result.fetchall()
        conn.close()
        return data

DB = DatabaseManager()

# ============================================================================
# مكتبة الأعلاف
# ============================================================================
FEEDS_LIB = {
    "🌾 الحبوب والطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح محلي": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0},
        "جريش أرز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2},
        "دخن محلي": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2}
    },
    "🌱 الأكساب والبروتين": {
        "أمباز الفول السوداني": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8},
        "كسب السمسم": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5},
        "كسب جلوتين الذرة": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5}
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
        "تبن قمح": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5},
        "سرسة الأرز": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5},
        "مخلفات البسكويت": {"CP": 10.0, "DC": 0.80, "SE": 65.0, "NDF": 8.0, "ADF": 4.0, "EE": 12.0, "ASH": 3.0}
    },
    "🧬 البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق أسماك 72%": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5},
        "مركزات دواجن": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركزات مجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5},
        "بروتين مصل الحليب": {"CP": 80.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 3.0, "ASH": 3.0}
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5},
        "ميثيونين نقي": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3},
        "ثريونين نقي": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2}
    },
    "🔬 الإنزيمات والبريمكس": {
        "بريمكس دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس بياض": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس مجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم الفايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
        "إنزيم NSP": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0},
        "خميرة الخبز": {"CP": 45.0, "DC": 0.85, "SE": 35.0, "NDF": 5.0, "ADF": 2.0, "EE": 2.5, "ASH": 7.0}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
        "يوريا علفية": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0}
    },
    "🍼 بدائل الحليب": {
        "مصل الحليب (Whey)": {"CP": 12.0, "DC": 0.95, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.0},
        "حليب مجفف": {"CP": 34.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.5},
        "دهن نباتي": {"CP": 0.0, "DC": 0.0, "SE": 10.0, "NDF": 0.0, "ADF": 0.0, "EE": 99.0, "ASH": 0.0},
        "ليسيثين الصويا": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 95.0, "ASH": 0.5},
        "بروتين الصويا المركز": {"CP": 65.0, "DC": 0.90, "SE": 30.0, "NDF": 2.0, "ADF": 1.0, "EE": 1.0, "ASH": 5.5}
    }
}

FLAT_FEEDS = {}
for cat, items in FEEDS_LIB.items():
    for name, data in items.items():
        FLAT_FEEDS[name] = data

# ============================================================================
# المعايير القياسية
# ============================================================================
STANDARDS = {
    "أبقار": {
        "تسمين عجول": {"DP": 12.0, "SE": 68.0, "CP": 15.0},
        "حليب/إدرار": {"DP": 14.0, "SE": 70.0, "CP": 17.5},
        "حمل/دفع غذائي": {"DP": 11.0, "SE": 65.0, "CP": 13.8},
        "صيانة": {"DP": 9.0, "SE": 60.0, "CP": 11.3},
        "تسمين مكثف": {"DP": 13.0, "SE": 72.0, "CP": 16.3}
    },
    "أغنام": {
        "تسمين حملان": {"DP": 13.0, "SE": 66.0, "CP": 16.3},
        "نعاج مرضعات": {"DP": 14.5, "SE": 68.0, "CP": 18.1},
        "نعاج حامل": {"DP": 11.5, "SE": 62.0, "CP": 14.4},
        "نعاج جافة": {"DP": 8.5, "SE": 58.0, "CP": 10.6}
    },
    "ماعز": {
        "تسمين جديان": {"DP": 12.5, "SE": 64.0, "CP": 15.6},
        "عنزات حلابة": {"DP": 14.0, "SE": 66.0, "CP": 17.5},
        "عنزات حامل": {"DP": 11.0, "SE": 60.0, "CP": 13.8},
        "صيانة": {"DP": 8.0, "SE": 56.0, "CP": 10.0}
    },
    "خيول": {
        "راحة/صيانة": {"DP": 9.0, "SE": 58.0, "CP": 11.3},
        "عمل خفيف": {"DP": 10.0, "SE": 60.0, "CP": 12.5},
        "عمل متوسط": {"DP": 11.0, "SE": 62.0, "CP": 13.8},
        "عمل مكثف": {"DP": 13.0, "SE": 65.0, "CP": 16.3},
        "سباق": {"DP": 14.0, "SE": 68.0, "CP": 17.5},
        "أمهار نامية": {"DP": 13.0, "SE": 64.0, "CP": 16.3}
    },
    "إبل": {
        "راحة/صيانة": {"DP": 8.0, "SE": 55.0, "CP": 10.0},
        "حمل/رضاعة": {"DP": 10.0, "SE": 58.0, "CP": 12.5},
        "إنتاج حليب": {"DP": 12.0, "SE": 60.0, "CP": 15.0},
        "تسمين": {"DP": 11.0, "SE": 62.0, "CP": 13.8}
    },
    "دواجن": {
        "بادي (0-14 يوم)": {"DP": 22.0, "SE": 76.0, "CP": 27.5},
        "نامي (15-28 يوم)": {"DP": 20.0, "SE": 74.0, "CP": 25.0},
        "ناهي (29-42 يوم)": {"DP": 18.0, "SE": 72.0, "CP": 22.5},
        "بياض إنتاجي": {"DP": 16.0, "SE": 70.0, "CP": 20.0}
    },
    "أسماك": {
        "زريعة/بادئ": {"DP": 32.0, "SE": 70.0, "CP": 40.0},
        "نمو": {"DP": 28.0, "SE": 68.0, "CP": 35.0},
        "تسمين نهائي": {"DP": 26.0, "SE": 66.0, "CP": 32.5}
    }
}

# ============================================================================
# الأسعار
# ============================================================================
BASE_PRICES = {
    "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0,
    "سورجم (فتريتة)": 195.0, "قمح محلي": 240.0, "جريش أرز": 200.0,
    "دخن محلي": 220.0, "شوفان علفي": 250.0,
    "أمباز الفول السوداني": 460.0, "كسب فول صويا 44%": 440.0,
    "كسب فول صويا 48%": 480.0, "كسب عباد الشمس": 310.0,
    "كسب بذور القطن": 290.0, "كسب بذور الكتان": 400.0,
    "كسب السمسم": 420.0, "كسب جلوتين الذرة": 700.0, "كسب نواة النخيل": 250.0,
    "نخالة قمح (ردة)": 150.0, "البرسيم الجاف": 170.0, "مولاس قصب السكر": 120.0,
    "تبن قمح": 80.0, "سرسة الأرز": 60.0, "مخلفات البسكويت": 200.0,
    "مسحوق أسماك 60%": 850.0, "مسحوق أسماك 72%": 1100.0,
    "مسحوق اللحم والعظم": 550.0, "مركزات دواجن": 650.0,
    "مركزات مجترات": 600.0, "بروتين مصل الحليب": 1200.0,
    "ليسين نقي": 2500.0, "ميثيونين نقي": 3500.0, "ثريونين نقي": 3000.0,
    "بريمكس دواجن": 900.0, "بريمكس بياض": 950.0, "بريمكس مجترات": 850.0,
    "إنزيم الفايتيز": 1200.0, "إنزيم NSP": 1000.0, "خميرة الخبز": 450.0,
    "الحجر الجيري": 40.0, "فوسفات ثنائي الكالسيوم": 280.0,
    "ملح الطعام": 30.0, "مضاد سموم فطرية": 950.0,
    "بيكربونات الصوديوم": 340.0, "يوريا علفية": 350.0,
    "مصل الحليب (Whey)": 1200.0, "حليب مجفف": 1800.0,
    "دهن نباتي": 800.0, "ليسيثين الصويا": 1500.0, "بروتين الصويا المركز": 2000.0
}

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "LIBYA": {"rate": 4.80, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"},
    "دولار أمريكي": {"rate": 1.0, "sym": "USD"}
}

ANIMAL_IMAGES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?w=600",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?w=600",
    "إبل": "https://images.unsplash.com/photo-1502175353174-a7a70e73b362?w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1600"
}

# ============================================================================
# دوال الصوت
# ============================================================================
@st.cache_data(ttl=3600)
def tts_b64(text, lang="ar"):
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

def play_audio(b64):
    if b64:
        st.components.v1.html(
            f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mpeg"></audio>',
            height=0
        )
        return True
    return False

def voice_guide(messages, lang="ar", delay=2.5):
    if not GTTS_AVAILABLE:
        st.warning("⚠️ مكتبة gTTS غير مثبتة")
        return
    if isinstance(messages, str):
        messages = [messages]
    for i, msg in enumerate(messages):
        b64 = tts_b64(msg, lang)
        if b64:
            play_audio(b64)
            duration = max(2.0, len(msg.split()) * 0.35 + 1.0)
            time.sleep(duration)
            if i < len(messages) - 1:
                time.sleep(1.0)

def play_welcome_audio():
    voice_guide([
        "السلام عليكم ورحمة الله وبركاته،",
        "مرحباً بكم في تاور نولجي Tawornology العلمية،",
        "منصة الانتاج الحيواني وتركيب الاعلاف."
    ])

def play_full_guide():
    voice_guide([
        "مرحباً بك في منصة تاور نولجي العلمية،",
        "هذه المنصة متخصصة في الانتاج الحيواني وتركيب الاعلاف.",
        "تشمل أقساماً رئيسية لتركيب الأعلاف للأبقار والأغنام والماعز والخيول والإبل والدواجن والأسماك.",
        "كما تشمل المختبر الذكي وإدارة المزارع وبدائل الحليب ومواقيت الصلاة ومنبه الجرعات.",
        "نسأل الله التوفيق والسداد."
    ])

# ============================================================================
# إرسال البريد
# ============================================================================
def send_code_to_email(receiver_email):
    if receiver_email.strip().lower() != OWNER_EMAIL.strip().lower():
        return False, f"❌ الإرسال مسموح فقط للبريد: {OWNER_EMAIL}"
    if not SENDER_PASSWORD:
        return False, "⚠️ كلمة مرور البريد غير مُعدّة."
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception:
        code = "# تعذر قراءة الكود"
    
    file_hash = hashlib.md5(code.encode()).hexdigest()
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود - تاور نولجي Tawornology v18.0"
    body = f"""السلام عليكم ورحمة الله وبركاته،

مرفق السورس كود الكامل لمنصة تاور نولجي Tawornology العلمية.

📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔑 التوقيع الرقمي: {file_hash}
👨‍💻 المشرف: الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان
🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    attach = MIMEText(code, 'plain', 'utf-8')
    attach.add_header('Content-Disposition', 'attachment',
                      filename=f"tawornology_v18_{datetime.now().strftime('%Y%m%d')}.py")
    msg.attach(attach)
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True, f"✅ تم إرسال الكود إلى {receiver_email}"
    except smtplib.SMTPAuthenticationError:
        return False, "❌ فشل التحقق من البريد. تأكد من App Password."
    except Exception as e:
        return False, f"❌ فشل الإرسال: {str(e)}"

# ============================================================================
# تحميل الخط العربي
# ============================================================================
@st.cache_resource
def download_font():
    font_path = "Amiri-Regular.ttf"
    if os.path.exists(font_path):
        return font_path
    try:
        import requests
        url = "https://raw.githubusercontent.com/aliftype/amiri/master/fonts/Amiri-Regular.ttf"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            with open(font_path, "wb") as f:
                f.write(r.content)
            return font_path
    except Exception:
        pass
    for f in ["/usr/share/fonts/truetype/arabic/Amiri-Regular.ttf",
              "C:/Windows/Fonts/arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(f):
            return f
    return None

def ensure_font():
    p = download_font()
    if p and os.path.exists(p):
        try:
            pdfmetrics.registerFont(TTFont('ArabicFont', p))
            return 'ArabicFont'
        except Exception:
            pass
    return 'Helvetica'

# ============================================================================
# مولد PDF
# ============================================================================
class PDFGenerator:
    def __init__(self):
        self.font = ensure_font()
    
    def _p(self, text, size=11, align=TA_RIGHT, color='#333'):
        safe = ar.fix(str(text))
        style = ParagraphStyle('s', fontName=self.font, fontSize=size,
                              alignment=align, textColor=HexColor(color), leading=size*1.5)
        return Paragraph(safe, style)
    
    def feed_report(self, formula, dp, se, breed, stage, cost, requester, standard=None):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        
        story.append(self._p("🌾 تاور نولجي Tawornology العلمية", 22, TA_CENTER, '#1b5e20'))
        story.append(Spacer(1, 8))
        story.append(self._p("📄 تقرير تركيبة علفية معتمدة", 16, TA_CENTER, '#2e7d32'))
        story.append(Spacer(1, 15))
        
        for line in [
            f"👨‍💻 المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان",
            f"🐾 الفصيل: {breed}",
            f"📋 المرحلة: {stage}",
            f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ]:
            story.append(self._p(line))
        
        if requester:
            story.append(self._p(f"👤 طالب العلف: {requester}", 12, TA_RIGHT, '#1565C0'))
        
        story.append(Spacer(1, 15))
        
        # جدول النتائج
        tdata = [['المعيار', 'القيمة'],
                 ['البروتين المهضوم (DP)', f'{dp:.2f}%'],
                 ['معادل النشاء (SE)', f'{se:.2f}'],
                 ['التكلفة للطن', f'${cost:.2f}']]
        t = Table([[ar.fix(c) for c in row] for row in tdata], colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#2e7d32'))
        ]))
        story.append(t)
        story.append(Spacer(1, 15))
        
        # مقارنة المعايير
        if standard:
            story.append(self._p("📏 المقارنة مع المعايير القياسية:", 13, TA_RIGHT, '#1b5e20'))
            comp = [['المقياس', 'المحسوب', 'القياسي', 'الانحراف']]
            for key in ['DP', 'SE', 'CP']:
                if key in standard:
                    calc = dp if key == 'DP' else (se if key == 'SE' else dp/0.8)
                    dev = ((calc - standard[key]) / standard[key]) * 100 if standard[key] > 0 else 0
                    comp.append([key, f'{calc:.2f}', f'{standard[key]:.2f}', f'{dev:+.1f}%'])
            t2 = Table([[ar.fix(c) for c in row] for row in comp], colWidths=[110, 130, 130, 130])
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
                ('TEXTCOLOR', (0,0), (-1,0), white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,-1), self.font),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd'))
            ]))
            story.append(t2)
        
        story.append(PageBreak())
        story.append(self._p("📋 المكونات المعتمدة لتركيب الطن الواحد:", 14, TA_RIGHT, '#1b5e20'))
        story.append(Spacer(1, 10))
        
        ing = [['المكون', 'النسبة %', 'كجم/طن']]
        for k, v in formula.items():
            ing.append([k, f'{v:.2f}%', f'{v*10:.1f}'])
        t3 = Table([[ar.fix(c) for c in row] for row in ing], colWidths=[200, 150, 150])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')])
        ]))
        story.append(t3)
        story.append(Spacer(1, 20))
        
        # توقيع
        story.append(self._p("مع خالص التحية والتقدير،", 12))
        story.append(Spacer(1, 10))
        story.append(self._p("م. عبد القادر إسماعيل تاور", 14, TA_RIGHT, '#1b5e20'))
        story.append(self._p("اختصاصي تغذية الحيوان", 11, TA_RIGHT, '#666'))
        story.append(Spacer(1, 20))
        story.append(self._p("🌾 تاور نولجي Tawornology العلمية © 2026", 9, TA_CENTER, '#999'))
        story.append(self._p("🕊️ إهداء إلى روح إسماعيل تاور وابتسام", 9, TA_CENTER, '#999'))
        
        doc.build(story)
        buf.seek(0)
        return buf.getvalue()
    
    def lab_report(self, analysis, animal, stage, standard, evaluation, analyst):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        
        story.append(self._p("🔬 تقرير التحليل المخبري المتقدم", 22, TA_CENTER, '#1565C0'))
        story.append(Spacer(1, 8))
        story.append(self._p("تاور نولجي Tawornology العلمية", 14, TA_CENTER, '#2e7d32'))
        story.append(Spacer(1, 15))
        
        story.append(self._p(f"👨‍💻 المحلل: {analyst}"))
        story.append(self._p(f"🐾 الحيوان: {animal} - {stage}"))
        story.append(self._p(f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}"))
        story.append(Spacer(1, 15))
        
        # النتائج
        story.append(self._p("📊 النتائج المحسوبة:", 13, TA_RIGHT, '#1565C0'))
        res_data = [['العنصر', 'القيمة']]
        if 'cp' in analysis: res_data.append(['البروتين الخام (CP)', f"{analysis['cp']:.2f}%"])
        if 'dp' in analysis: res_data.append(['البروتين المهضوم (DP)', f"{analysis['dp']:.2f}%"])
        if 'se' in analysis: res_data.append(['معادل النشاء (SE)', f"{analysis['se']:.2f}"])
        
        t = Table([[ar.fix(c) for c in row] for row in res_data], colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1565C0')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#1565C0'))
        ]))
        story.append(t)
        story.append(Spacer(1, 15))
        
        # المقارنة
        if standard:
            story.append(self._p("📏 المقارنة مع المعايير:", 13, TA_RIGHT, '#1b5e20'))
            comp = [['المقياس', 'المحسوب', 'القياسي', 'الانحراف', 'التقييم']]
            for key in ['DP', 'SE', 'CP']:
                if key in standard:
                    calc = analysis.get(key.lower(), 0)
                    dev = ((calc - standard[key]) / standard[key]) * 100 if standard[key] > 0 else 0
                    grade = "ممتاز ✅" if abs(dev) <= 5 else ("جيد 👍" if abs(dev) <= 10 else "ضعيف ⚠️")
                    comp.append([key, f'{calc:.2f}', f'{standard[key]:.2f}', f'{dev:+.1f}%', grade])
            t2 = Table([[ar.fix(c) for c in row] for row in comp], colWidths=[80, 100, 100, 100, 120])
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
                ('TEXTCOLOR', (0,0), (-1,0), white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,-1), self.font),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd'))
            ]))
            story.append(t2)
            story.append(Spacer(1, 15))
            
            # رسم بياني
            try:
                fig, ax = plt.subplots(figsize=(6, 3))
                cats = ['DP', 'SE', 'CP']
                calc_vals = [analysis.get('dp', 0), analysis.get('se', 0), analysis.get('cp', 0)]
                std_vals = [standard.get('DP', 0), standard.get('SE', 0), standard.get('CP', 0)]
                x = np.arange(len(cats))
                w = 0.35
                ax.bar(x - w/2, calc_vals, w, label='المحسوب', color='#2e7d32')
                ax.bar(x + w/2, std_vals, w, label='القياسي', color='#1565C0')
                ax.set_xticks(x)
                ax.set_xticklabels(cats)
                ax.legend()
                ax.grid(axis='y', linestyle='--', alpha=0.5)
                plt.tight_layout()
                img_buf = io.BytesIO()
                plt.savefig(img_buf, format='png', dpi=120, bbox_inches='tight')
                plt.close()
                img_buf.seek(0)
                story.append(Image(img_buf, width=400, height=200))
            except Exception:
                pass
        
        story.append(Spacer(1, 20))
        story.append(self._p("م. عبد القادر إسماعيل تاور", 14, TA_RIGHT, '#1b5e20'))
        story.append(self._p("اختصاصي تغذية الحيوان", 11, TA_RIGHT, '#666'))
        story.append(Spacer(1, 15))
        story.append(self._p("🌾 تاور نولجي Tawornology © 2026", 9, TA_CENTER, '#999'))
        
        doc.build(story)
        buf.seek(0)
        return buf.getvalue()

PDF = PDFGenerator()

# ============================================================================
# CSS
# ============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

* { font-family: 'Cairo', 'Tajawal', sans-serif !important; }

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f5f7fa 0%, #e8eaf6 50%, #f1f8e9 100%) !important;
}

.stApp { background: transparent; }

.main-box {
    background: rgba(255,255,255,0.96);
    padding: 30px;
    border-radius: 24px;
    box-shadow: 0 25px 70px rgba(0,0,0,0.12);
    margin-bottom: 35px;
    backdrop-filter: blur(15px);
}

.section-title {
    color: #1b5e20 !important;
    border-right: 7px solid #2e7d32;
    padding: 16px 22px;
    text-align: right;
    font-size: 1.7rem;
    font-weight: 700;
    margin: 30px 0 25px 0;
    background: linear-gradient(to left, rgba(46,125,50,0.12), transparent);
    border-radius: 14px;
    box-shadow: 0 4px 15px rgba(46,125,50,0.08);
}

.formula-item {
    background: linear-gradient(135deg, #ffffff 0%, #e8f5e9 100%);
    padding: 15px 22px;
    border-radius: 14px;
    margin-bottom: 10px;
    font-weight: 600;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    box-shadow: 0 4px 18px rgba(46,125,50,0.1);
    display: flex;
    justify-content: space-between;
    transition: all 0.3s ease;
}
.formula-item:hover { transform: translateX(-8px); box-shadow: 0 8px 30px rgba(46,125,50,0.2); }

.profile-img {
    width: 140px; height: 140px; border-radius: 50%; object-fit: cover;
    border: 4px solid #d4af37; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.metric-card {
    background: linear-gradient(135deg, #ffffff, #f8f9fa);
    padding: 22px; border-radius: 18px;
    box-shadow: 0 6px 30px rgba(0,0,0,0.08);
    text-align: center; border: 1px solid rgba(46,125,50,0.1);
    transition: all 0.4s ease;
}
.metric-card:hover { transform: translateY(-8px); box-shadow: 0 15px 50px rgba(46,125,50,0.15); }
.metric-card .num { font-size: 2rem; font-weight: 900; color: #1b5e20; }
.metric-card .lbl { font-size: 0.9rem; color: #666; font-weight: 600; }

.stButton > button {
    background: linear-gradient(135deg, #2e7d32, #1b5e20) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 11px 24px !important;
    box-shadow: 0 6px 20px rgba(46,125,50,0.3) !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 30px rgba(46,125,50,0.5) !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 12px !important;
    border: 2px solid #e0e0e0 !important;
    transition: all 0.3s ease !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #2e7d32 !important;
    box-shadow: 0 0 0 4px rgba(46,125,50,0.15) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: linear-gradient(135deg, #ffffff, #f5f5f5);
    border-radius: 16px; padding: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    gap: 4px; flex-wrap: wrap;
}
.stTabs [data-baseweb="tab-list"] button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 10px 16px !important;
    transition: all 0.3s ease !important;
}
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #2e7d32, #1b5e20) !important;
    color: white !important;
    box-shadow: 0 6px 20px rgba(46,125,50,0.3) !important;
}

.warning-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 14px; border-radius: 12px;
    border-right: 5px solid #f57c00;
    margin-bottom: 12px; direction: rtl; text-align: right;
    color: #e65100 !important;
}

.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 18px; border-radius: 14px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 18px; direction: rtl;
}

@keyframes scrollDua {
    0%, 100% { transform: translateX(100%); opacity: 0; }
    5%, 85% { transform: translateX(0%); opacity: 1; }
    95% { transform: translateX(-100%); opacity: 0; }
}
.dua-text {
    display: inline-block; white-space: nowrap;
    animation: scrollDua 22s ease-in-out infinite;
    font-size: 1.5rem; font-weight: 800; color: #ffd700;
    padding: 0 25px; direction: rtl;
    text-shadow: 0 0 20px rgba(255,215,0,0.6);
}
.dua-container {
    background: linear-gradient(135deg, #0d1b2a, #1a237e, #4a148c, #0d1b2a);
    padding: 18px 0; border-radius: 20px;
    margin-bottom: 20px; overflow: hidden;
    border: 3px solid #ffd700;
    box-shadow: 0 8px 40px rgba(255,215,0,0.4);
    direction: rtl;
}

.stock-critical { background: #ffcdd2; padding: 5px 14px; border-radius: 20px; color: #c62828; font-weight: 700; }
.stock-normal { background: #c8e6c9; padding: 5px 14px; border-radius: 20px; color: #2e7d32; font-weight: 700; }
.stock-warning { background: #ffe0b2; padding: 5px 14px; border-radius: 20px; color: #e65100; font-weight: 700; }

.stDownloadButton > button {
    background: linear-gradient(135deg, #1565C0, #0d47a1) !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# الافتتاح الرسمي
# ============================================================================
def render_official_header():
    if img_base64:
        logo = f'<img src="data:image/jpeg;base64,{img_base64}" style="width:110px;height:110px;border-radius:50%;border:4px solid #d4af37;box-shadow:0 8px 25px rgba(212,175,55,0.4);">'
    else:
        logo = '<div style="font-size:80px;">🌾</div>'
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0d1b2a 0%, #1a237e 40%, #2e7d32 100%);
        border-radius: 24px; padding: 30px 25px; margin-bottom: 25px;
        border: 3px solid #d4af37;
        box-shadow: 0 15px 50px rgba(0,0,0,0.35);
        text-align: center; direction: rtl;
    ">
        <div style="font-size:2.2rem;color:#ffd700;font-weight:900;
            text-shadow:0 0 25px rgba(255,215,0,0.8);margin-bottom:12px;letter-spacing:3px;">
            ﷽
        </div>
        <div style="font-size:1rem;color:#e8eaf6;margin-bottom:20px;font-style:italic;">
            بسم الله الرحمن الرحيم، والصلاة والسلام على أشرف المرسلين
        </div>
        <div style="margin:15px 0;">{logo}</div>
        <div style="font-size:1.6rem;color:#ffffff;font-weight:900;
            text-shadow:0 3px 10px rgba(0,0,0,0.5);margin-bottom:6px;">
            🌾 تاور نولجي Tawornology العلمية
        </div>
        <div style="font-size:1rem;color:#b0bec5;margin-bottom:18px;">
            للانتاج الحيواني وتركيب الاعلاف
        </div>
        <div style="width:60%;height:3px;margin:18px auto;
            background:linear-gradient(to right,transparent,#ffd700,transparent);
            box-shadow:0 0 15px #ffd700;"></div>
        <div style="background:linear-gradient(135deg,rgba(255,215,0,0.15),rgba(255,215,0,0.05));
            border:2px solid #d4af37;border-radius:16px;padding:20px 15px;
            box-shadow:inset 0 0 30px rgba(255,215,0,0.1);">
            <div style="font-size:0.9rem;color:#ffd700;margin-bottom:8px;letter-spacing:2px;">
                ✦ المشرف العام ✦
            </div>
            <div style="font-size:1.8rem;color:#ffffff;font-weight:900;
                text-shadow:0 4px 15px rgba(255,215,0,0.6);line-height:1.4;">
                الاختصاصي م. عبد القادر إسماعيل تاور
            </div>
            <div style="font-size:1.05rem;color:#ffab40;margin-top:8px;font-weight:700;">
                🧬 اختصاصي تغذية الحيوان 🧬
            </div>
        </div>
        <div style="margin-top:22px;padding:14px;background:rgba(0,0,0,0.3);
            border-radius:12px;border-right:4px solid #ffd700;
            font-size:0.95rem;color:#e8eaf6;line-height:1.7;">
            🕊️ <b style="color:#ffd700;">إهداء:</b>
            إلى روح والدي <span style="color:#ffab40;font-weight:900;">إسماعيل تاور</span>
            وأختي <span style="color:#ffab40;font-weight:900;">ابتسام</span> - رحمهما الله
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_dua_bar():
    st.markdown("""
    <div class="dua-container">
        <div class="dua-text">
            ❤️ اللهم اغفر لإسماعيل تاور وابتسام وارحمهما وأدخلهما فسيح جناتك
            ❤️ اللهم اجعل قبرهما روضة من رياض الجنة ❤️
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_signature():
    st.markdown("""
    <div style="
        background:linear-gradient(135deg,#0d1b2a 0%,#1a237e 40%,#2e7d32 100%);
        border-radius:24px;padding:35px 25px;margin-top:50px;
        border:3px solid #d4af37;
        box-shadow:0 15px 50px rgba(0,0,0,0.35);
        text-align:center;direction:rtl;">
        <div style="font-size:1.4rem;color:#ffd700;font-weight:900;
            margin-bottom:20px;letter-spacing:2px;
            text-shadow:0 0 20px rgba(255,215,0,0.6);">
            ✦ التوقيع الرسمي ✦
        </div>
        <div style="width:50%;height:3px;margin:0 auto 25px;
            background:linear-gradient(to right,transparent,#ffd700,transparent);
            box-shadow:0 0 15px #ffd700;"></div>
        <div style="background:rgba(255,255,255,0.08);
            border:2px solid #d4af37;border-radius:18px;
            padding:22px;margin:0 auto;max-width:680px;">
            <div style="font-size:0.9rem;color:#ffd700;letter-spacing:2px;margin-bottom:10px;">
                المشرف العام للمنصة
            </div>
            <div style="font-size:1.9rem;color:#ffffff;font-weight:900;
                text-shadow:0 4px 20px rgba(255,215,0,0.6);line-height:1.5;margin-bottom:10px;">
                م. عبد القادر إسماعيل تاور
            </div>
            <div style="font-size:1.1rem;color:#ffab40;font-weight:700;margin-bottom:15px;">
                اختصاصي تغذية الحيوان
            </div>
            <div style="width:60%;height:2px;margin:15px auto;
                background:#d4af37;opacity:0.6;"></div>
            <div style="font-size:0.9rem;color:#b0bec5;font-style:italic;">
                ✍️ التوقيع الإلكتروني المعتمد ✍️
            </div>
        </div>
        <div style="margin-top:25px;padding:16px;background:rgba(0,0,0,0.3);
            border-radius:14px;color:#e8eaf6;font-size:0.95rem;line-height:1.7;">
            🕊️ <b style="color:#ffd700;">إهداء خاص:</b><br>
            إلى روح والدي <span style="color:#ffab40;font-weight:900;">إسماعيل تاور</span>
            وأختي <span style="color:#ffab40;font-weight:900;">ابتسام</span><br>
            <span style="font-size:0.85rem;color:#b0bec5;">
            اللهم اجعل قبرهما روضة من رياض الجنة واجمعنا بهما في الفردوس الأعلى
            </span>
        </div>
        <div style="margin-top:20px;font-size:0.85rem;color:#90a4ae;
            border-top:1px solid rgba(255,255,255,0.1);padding-top:12px;">
            🌾 تاور نولجي Tawornology العلمية v18.0 © 2026
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# حالة الجلسة
# ============================================================================
defaults = {
    "approved": False, "user_role": None, "user": {},
    "login_attempts": 0, "last_login_time": None,
    "welcome_shown": False, "audio_played": False,
    "active_formula": {}, "ton_cost": 0.0,
    "inventory": {}, "global_livestock": {
        "عجول تسمين ($)": 1350.0, "أبقار كنانة ($)": 900.0,
        "ضأن محلي ($)": 180.0, "ماعز نوبي ($)": 130.0,
        "خيول أصيلة ($)": 4500.0, "إبل عربية ($)": 2500.0,
    },
    "global_products": {
        "لحم بقري ($/كغ)": 7.50, "لحم ضأن ($/كغ)": 9.00,
        "لحم دجاج ($/كغ)": 3.80, "بيض (30) ($)": 4.20,
        "حليب خام ($/لتر)": 0.90,
    },
    "daily_logs": [], "comments": "• [توجيه المشرف]: يرجى من جميع الزملاء إضافة تعليقاتهم.\n"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# تهيئة المخزون
if not st.session_state["inventory"]:
    for name in FLAT_FEEDS:
        st.session_state["inventory"][name] = {"qty": 25.0, "min": 5.0}

# ============================================================================
# شاشة الدخول
# ============================================================================
if not st.session_state["approved"]:
    render_official_header()
    render_dua_bar()
    
    st.markdown('<div class="main-box" style="max-width:550px;margin:40px auto;direction:rtl;">', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align:center;color:#1a237e;'>🔐 بوابة الدخول</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#666;'>أدخل كود الدخول للوصول إلى المنصة</p>", unsafe_allow_html=True)
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        if st.button("🔊 استمع للترحيب", use_container_width=True):
            play_welcome_audio()
    with col_v2:
        if st.button("📖 شرح صوتي كامل", use_container_width=True):
            play_full_guide()
    
    input_code = st.text_input("🔑 كود الدخول:", type="password",
                              placeholder="أدخل كودك الخاص", key="login_code")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔓 دخول المالك/المختص", type="primary", use_container_width=True):
            if input_code.strip() in CODES_DB:
                info = CODES_DB[input_code.strip()]
                st.session_state["approved"] = True
                st.session_state["user_role"] = info["role"]
                st.session_state["user"] = {
                    'username': info["role"],
                    'role': info["role"],
                    'full_name': info["name"],
                    'level': info.get("level", 1)
                }
                st.session_state["login_attempts"] = 0
                st.session_state["welcome_shown"] = False
                voice_guide(f"مرحباً بك، {info['name']}")
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                st.error(f"❌ كود غير صحيح (محاولة {st.session_state['login_attempts']}/5)")
    
    with col2:
        if st.button("👤 دخول كزائر", use_container_width=True):
            st.session_state["approved"] = True
            st.session_state["user_role"] = "public"
            st.session_state["user"] = {
                'username': 'public', 'role': 'public',
                'full_name': 'زائر', 'level': 0
            }
            st.session_state["welcome_shown"] = False
            voice_guide("السلام عليكم، مرحباً بك زائراً.")
            st.rerun()
    
    st.markdown("""
    <div style='text-align:center;margin-top:20px;color:#999;font-size:0.85rem;'>
    💡 أكواد الدخول المتاحة للمالك والمختصين فقط<br>
    🕊️ إهداء إلى روح إسماعيل تاور وابتسام - رحمهما الله
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ============================================================================
# الواجهة الرئيسية
# ============================================================================
if not st.session_state["welcome_shown"]:
    role_msgs = {
        "owner": "👋 مرحباً بك، الاختصاصي م. عبد القادر",
        "specialist": "🔬 أهلاً بالمختصين",
        "veterinarian": "💊 أهلاً بالطبيب البيطري",
        "nutritionist": "🧬 أهلاً بأخصائي التغذية",
        "breeder": "🌾 أهلاً بالمربين",
        "public": "👤 مرحباً بك زائراً"
    }
    st.toast(role_msgs.get(st.session_state["user_role"], "مرحباً"), icon="🌾")
    st.session_state["welcome_shown"] = True

render_official_header()
render_dua_bar()

# ============================================================================
# ترويسة المستخدم
# ============================================================================
col1, col2 = st.columns([0.75, 0.25])
with col2:
    role_names = {
        "owner": "المالك 👑", "specialist": "مختص 👨‍🔬",
        "veterinarian": "بيطري 💊", "nutritionist": "تغذية 🧬",
        "breeder": "مربي 🌾", "public": "زائر 👤"
    }
    name = st.session_state["user"].get("full_name", "زائر")
    role = st.session_state["user_role"]
    
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#f5f5f5,#e0e0e0);
        padding:12px;border-radius:14px;text-align:left;">
        <div style="font-weight:700;">{name}</div>
        <div style="font-size:0.85rem;color:#555;">{role_names.get(role, "مستخدم")}</div>
        <div style="font-size:0.75rem;color:#888;">
            آخر دخول: {datetime.now().strftime('%H:%M')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k not in ["inventory", "global_livestock", "global_products"]:
                del st.session_state[k]
        st.session_state["approved"] = False
        st.rerun()

# ============================================================================
# لوحة التحكم السريعة
# ============================================================================
st.markdown("### 📊 لوحة التحكم السريعة")
c1, c2, c3, c4 = st.columns(4)
total_items = len(st.session_state["inventory"])
total_qty = sum(d["qty"] for d in st.session_state["inventory"].values())
low = sum(1 for d in st.session_state["inventory"].values() if d["qty"] < d["min"])

with c1:
    st.markdown(f"<div class='metric-card'><div class='num'>{total_items}</div><div class='lbl'>المواد العلفية</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='metric-card'><div class='num'>{total_qty:.0f}</div><div class='lbl'>المخزون (طن)</div></div>", unsafe_allow_html=True)
with c3:
    color = "#c62828" if low > 5 else "#e65100" if low > 0 else "#2e7d32"
    st.markdown(f"<div class='metric-card'><div class='num' style='color:{color};'>{low}</div><div class='lbl'>مواد منخفضة</div></div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='metric-card'><div class='num'>{len(st.session_state['active_formula'])}</div><div class='lbl'>مكونات الخلطة</div></div>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# التبويبات
# ============================================================================
role = st.session_state["user_role"]

if role == "owner":
    titles = ["🐾 القطاع الحيواني", "📸 المختبر الذكي", "🔬 المختبر المتقدم",
              "🍼 بدائل الحليب", "🕌 مواقيت الصلاة", "💊 منبه الجرعات",
              "📊 بورصة الأسعار", "🏭 المستودعات", "📈 الإنتاج اليومي",
              "📚 المراجع العلمية", "💬 التعليقات", "💡 المساعدة",
              "📖 دليل المستخدم", "📧 إرسال الكود"]
elif role in ["specialist", "veterinarian", "nutritionist"]:
    titles = ["🐾 القطاع الحيواني", "📸 المختبر الذكي", "🔬 المختبر المتقدم",
              "🍼 بدائل الحليب", "🕌 مواقيت الصلاة", "💊 منبه الجرعات",
              "📊 بورصة الأسعار", "🏭 المستودعات", "📈 الإنتاج اليومي",
              "📚 المراجع العلمية", "💬 التعليقات", "💡 المساعدة",
              "📖 دليل المستخدم"]
elif role == "breeder":
    titles = ["🐾 القطاع الحيواني", "📸 المختبر الذكي", "🍼 بدائل الحليب",
              "🕌 مواقيت الصلاة", "📚 المراجع العلمية", "💡 المساعدة",
              "📖 دليل المستخدم"]
else:  # public
    titles = ["📸 المختبر الذكي", "🍼 بدائل الحليب", "🕌 مواقيت الصلاة",
              "📚 المراجع العلمية", "💡 المساعدة", "📖 دليل المستخدم"]

tabs = st.tabs(titles)

def guide(text, name):
    with st.expander(f"📘 دليل {name}", expanded=False):
        st.markdown(f"<div style='background:#f0f8ff;padding:15px;border-radius:10px;direction:rtl;'>{text}</div>", unsafe_allow_html=True)
        if st.button(f"🔊 تشغيل صوتي", key=f"g_{name}"):
            voice_guide(text)

# ============================================================================
# تبويب القطاع الحيواني
# ============================================================================
tab_idx = 0
if "🐾 القطاع الحيواني" in titles:
    with tabs[tab_idx]:
        guide("اختر نوع الحيوان، السلالة، المرحلة، والمكونات.", "القطاع الحيواني")
        
        animal_tabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐴 خيول", "🐫 إبل", "🐔 دواجن", "🐟 أسماك"])
        
        def render_formulator(animal_key, name, breeds, stages, img_key, has_measure=True):
            st.markdown(f'<div class="section-title">{name} - تركيب العلف</div>', unsafe_allow_html=True)
            
            requester = st.text_input(f"👤 اسم طالب العلف ({name}):", key=f"{animal_key}_req",
                                     placeholder="أدخل اسمك/المزرعة")
            
            col1, col2 = st.columns([0.4, 0.6])
            
            with col1:
                if has_measure:
                    st.markdown("#### 📏 القياسات الجسدية")
                    g = st.number_input("محيط الصدر (سم)", 20.0, 300.0, 150.0, key=f"{animal_key}_g")
                    l = st.number_input("طول الجسم (سم)", 20.0, 300.0, 130.0, key=f"{animal_key}_l")
                    
                    wf = {"cattle": 10838, "sheep": 15500, "goat": 15000, "horse": 11877, "camel": 13000}.get(animal_key, 12000)
                    weight = (g**2 * l) / wf
                    st.success(f"الوزن التقديري: **{weight:.1f} كجم**")
            
            with col2:
                st.markdown("#### 🎯 السلالة والمرحلة")
                c1, c2 = st.columns(2)
                with c1: breed = st.selectbox("السلالة", breeds, key=f"{animal_key}_b")
                with c2: stage = st.selectbox("المرحلة", stages, key=f"{animal_key}_s")
                
                st.markdown("#### 🎯 البروتين والطاقة")
                basis = st.radio("الأساس:", ["DP", "CP"], horizontal=True, key=f"{animal_key}_basis")
                default_dp = STANDARDS.get(name, {}).get(stage, {}).get("DP", 12.0)
                default_se = STANDARDS.get(name, {}).get(stage, {}).get("SE", 65.0)
                
                c1, c2 = st.columns(2)
                with c1:
                    target = st.number_input(f"{basis} %", 5.0, 50.0, float(default_dp), 0.5, key=f"{animal_key}_t")
                with c2:
                    se_target = st.number_input("SE", 10.0, 90.0, float(default_se), 1.0, key=f"{animal_key}_se")
                
                actual_dp = target if basis == "DP" else target * 0.80
            
            st.markdown("#### 🌾 المكونات")
            selected = []
            prices = {}
            
            default_list = {
                "cattle": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                          "أمباز الفول السوداني", "مركزات مجترات", "ملح الطعام",
                          "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "بيكربونات الصوديوم"],
                "sheep": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                         "أمباز الفول السوداني", "مركزات مجترات", "ملح الطعام",
                         "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "بيكربونات الصوديوم"],
                "goat": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                        "أمباز الفول السوداني", "مركزات مجترات", "ملح الطعام",
                        "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "بيكربونات الصوديوم"],
                "horse": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                         "أمباز الفول السوداني", "مولاس قصب السكر", "مركزات مجترات",
                         "ملح الطعام", "الحجر الجيري", "فوسفات ثنائي الكالسيوم"],
                "camel": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                         "أمباز الفول السوداني", "البرسيم الجاف", "مركزات مجترات",
                         "ملح الطعام", "الحجر الجيري", "فوسفات ثنائي الكالسيوم"],
                "poultry": ["ذرة صفراء", "سورجم (فتريتة)", "كسب فول صويا 44%",
                           "كسب جلوتين الذرة", "مركزات دواجن", "بريمكس دواجن",
                           "ملح الطعام", "الحجر الجيري", "فوسفات ثنائي الكالسيوم",
                           "إنزيم الفايتيز"],
                "fish": ["ذرة صفراء", "كسب فول صويا 44%", "مسحوق أسماك 60%",
                        "كسب جلوتين الذرة", "مركزات دواجن", "ملح الطعام",
                        "فوسفات ثنائي الكالسيوم", "إنزيم الفايتيز"]
            }
            
            dflt = default_list.get(animal_key, [])
            for cat, items in FEEDS_LIB.items():
                with st.expander(f"📁 {cat}", expanded=False):
                    cols = st.columns(3)
                    for i, (ing_name, _) in enumerate(items.items()):
                        with cols[i % 3]:
                            chk = st.checkbox(ing_name, value=ing_name in dflt,
                                            key=f"{animal_key}_feed_{ing_name}")
                            if chk:
                                price = st.number_input(f"سعر ($)", 5.0,
                                                      float(BASE_PRICES.get(ing_name, 250.0)),
                                                      key=f"{animal_key}_pr_{ing_name}")
                                selected.append(ing_name)
                                prices[ing_name] = price
            
            col_btn = st.columns([1, 1, 1])
            with col_btn[0]:
                if st.button(f"🚀 تشغيل المحرك", type="primary",
                           use_container_width=True, key=f"{animal_key}_run"):
                    if len(selected) < 3:
                        st.warning("⚠️ اختر 3 مكونات على الأقل")
                    else:
                        voice_guide(f"جاري حساب الخلطة لـ {name}")
                        st.info("🔄 جاري الحساب...")
                        
                        c_vec = [prices[i] for i in selected]
                        bounds = [(0.0, 100.0) for _ in selected]
                        
                        dp_row = []
                        se_row = []
                        ndf_row = []
                        adf_row = []
                        for ing in selected:
                            fd = FLAT_FEEDS.get(ing, {})
                            dp_row.append(fd.get("CP", 0) * fd.get("DC", 0))
                            se_row.append(fd.get("SE", 0))
                            ndf_row.append(fd.get("NDF", 0))
                            adf_row.append(fd.get("ADF", 0))
                        
                        A_eq = [[1.0]*len(selected), dp_row]
                        b_eq = [100.0, actual_dp*100.0]
                        A_ub = [[-x for x in se_row]]
                        b_ub = [-se_target*100.0]
                        
                        if animal_key in ["cattle","sheep","goat","camel"]:
                            A_ub.append(ndf_row); b_ub.append(35.0*100.0)
                            A_ub.append(adf_row); b_ub.append(20.0*100.0)
                        elif animal_key == "horse":
                            A_ub.append(ndf_row); b_ub.append(40.0*100.0)
                        
                        # إضافات إلزامية
                        if animal_key in ["cattle","sheep","goat","camel"]:
                            if "بيكربونات الصوديوم" not in selected:
                                selected.append("بيكربونات الصوديوم")
                                prices["بيكربونات الصوديوم"] = 340.0
                                c_vec.append(340.0)
                                dp_row.append(0.0); se_row.append(0.0)
                                ndf_row.append(0.0); adf_row.append(0.0)
                                bounds.append((0.75, 0.75))
                                row = [0.0]*len(selected); row[-1]=1.0
                                A_ub.append(row); b_ub.append(0.75)
                                A_eq = [[1.0]*len(selected), dp_row]
                        
                        if animal_key in ["poultry","fish"]:
                            if "إنزيم الفايتيز" not in selected:
                                selected.append("إنزيم الفايتيز")
                                prices["إنزيم الفايتيز"] = 1200.0
                                c_vec.append(1200.0)
                                dp_row.append(0.0); se_row.append(0.0)
                                ndf_row.append(0.0); adf_row.append(0.0)
                                bounds.append((0.05, 0.05))
                                row = [0.0]*len(selected); row[-1]=1.0
                                A_ub.append(row); b_ub.append(0.05)
                                A_eq = [[1.0]*len(selected), dp_row]
                        
                        try:
                            res = linprog(c_vec, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                                        bounds=bounds, method='highs')
                            
                            if res.success:
                                formula = {}
                                comp_se = 0.0
                                comp_dp = 0.0
                                for i, ing in enumerate(selected):
                                    if res.x[i] > 0.0001:
                                        formula[ing] = res.x[i]
                                        fd = FLAT_FEEDS.get(ing, {})
                                        comp_se += (res.x[i]/100.0)*fd.get("SE", 0)
                                        comp_dp += (res.x[i]/100.0)*fd.get("CP",0)*fd.get("DC",0)
                                
                                cost = res.fun / 100.0
                                std = STANDARDS.get(name, {}).get(stage, {})
                                
                                # فحص 75%
                                warnings_list = []
                                if std:
                                    if 'DP' in std:
                                        r = comp_dp/std['DP']*100
                                        if r < 75: warnings_list.append(f"DP {r:.1f}% < 75%")
                                    if 'SE' in std:
                                        r = comp_se/std['SE']*100
                                        if r < 75: warnings_list.append(f"SE {r:.1f}% < 75%")
                                
                                if warnings_list:
                                    st.error("❌ الخلطة لا تلبي 75% من المعايير")
                                    for w in warnings_list: st.warning(w)
                                else:
                                    st.success(f"✅ التكلفة: ${cost:.2f}/طن")
                                    voice_guide(f"تم توليد الخلطة بنجاح")
                                    
                                    col_r1, col_r2 = st.columns([0.6, 0.4])
                                    with col_r1:
                                        st.write("#### 📋 المكونات:")
                                        for k, v in formula.items():
                                            st.markdown(f'<div class="formula-item"><span>{k}</span><span>{v:.2f}% ({v*10:.1f} كجم)</span></div>', unsafe_allow_html=True)
                                        
                                        st.metric("💰 التكلفة", f"${cost:.2f}")
                                        st.metric("🧬 DP", f"{comp_dp:.2f}%")
                                        st.metric("🌽 SE", f"{comp_se:.2f}")
                                        
                                        if std:
                                            st.write("#### 📊 المقارنة:")
                                            cmp = []
                                            for key in ['DP','SE','CP']:
                                                if key in std:
                                                    c = comp_dp if key=='DP' else (comp_se if key=='SE' else comp_dp/0.8)
                                                    dev = ((c-std[key])/std[key]*100) if std[key]>0 else 0
                                                    g = "✅" if abs(dev)<=5 else ("⚠️" if abs(dev)<=10 else "❌")
                                                    cmp.append({"المقياس":key,"المحسوب":f"{c:.2f}","القياسي":f"{std[key]:.2f}","الانحراف":f"{dev:+.1f}%","التقييم":g})
                                            st.dataframe(pd.DataFrame(cmp), use_container_width=True, hide_index=True)
                                        
                                        try:
                                            pdf = PDF.feed_report(formula, comp_dp, comp_se,
                                                                breed, f"{stage}", cost, requester, std)
                                            st.download_button("📄 تحميل PDF", pdf,
                                                             file_name=f"feed_{datetime.now().strftime('%Y%m%d')}.pdf",
                                                             mime="application/pdf",
                                                             use_container_width=True)
                                        except Exception as e:
                                            st.warning(f"PDF: {e}")
                                    
                                    with col_r2:
                                        try:
                                            fig = px.pie(values=list(formula.values()),
                                                        names=list(formula.keys()),
                                                        title="التوزيع",
                                                        color_discrete_sequence=px.colors.sequential.Greens)
                                            fig.update_layout(height=380, font=dict(family='Cairo'))
                                            st.plotly_chart(fig, use_container_width=True)
                                        except Exception:
                                            pass
                                    
                                    st.session_state["active_formula"] = formula
                                    st.session_state["ton_cost"] = cost
                            else:
                                st.error(f"❌ فشل الحل: {res.message}")
                        except Exception as e:
                            st.error(f"❌ خطأ: {e}")
            
            with col_btn[1]:
                if st.button(f"📋 المعايير القياسية", use_container_width=True, key=f"{animal_key}_std"):
                    std = STANDARDS.get(name, {}).get(stage, {})
                    if std:
                        st.info(f"DP={std.get('DP','-')}%, SE={std.get('SE','-')}, CP={std.get('CP','-')}%")
            
            with col_btn[2]:
                if st.button(f"🔊 تعليمات صوتية", use_container_width=True, key=f"{animal_key}_voice"):
                    voice_guide(f"مرحباً بك في قسم {name}. اختر السلالة والمكونات ثم اضغط تشغيل.")
        
        with animal_tabs[0]:
            render_formulator("cattle", "أبقار",
                ["كنانة","بطانة","هولشتاين"], 
                ["تسمين عجول","حليب/إدرار","حمل/دفع غذائي","صيانة","تسمين مكثف"],
                "أبقار")
        with animal_tabs[1]:
            render_formulator("sheep", "أغنام",
                ["الضأن الصحراوي","البربري","النعيمي"],
                ["تسمين حملان","نعاج مرضعات","نعاج حامل","نعاج جافة"],
                "أغنام")
        with animal_tabs[2]:
            render_formulator("goat", "ماعز",
                ["النوبي","الصحراوي","بور/محسن"],
                ["تسمين جديان","عنزات حلابة","عنزات حامل","صيانة"],
                "ماعز")
        with animal_tabs[3]:
            render_formulator("horse", "خيول",
                ["عربي أصيل","ثوروبريد","محلي هجين"],
                ["راحة/صيانة","عمل خفيف","عمل متوسط","عمل مكثف","سباق","أمهار نامية"],
                "خيول")
        with animal_tabs[4]:
            render_formulator("camel", "إبل",
                ["عربية","باختري","هجين"],
                ["راحة/صيانة","حمل/رضاعة","إنتاج حليب","تسمين"],
                "إبل")
        with animal_tabs[5]:
            render_formulator("poultry", "دواجن",
                ["لاحم Broiler","بياض Layer","سمان"],
                ["بادي (0-14 يوم)","نامي (15-28 يوم)","ناهي (29-42 يوم)","بياض إنتاجي"],
                "دواجن", has_measure=False)
        with animal_tabs[6]:
            render_formulator("fish", "أسماك",
                ["البلطي","القرموط"],
                ["زريعة/بادئ","نمو","تسمين نهائي"],
                "أسماك", has_measure=False)
    
    tab_idx += 1

# ============================================================================
# تبويب المختبر الذكي (OCR)
# ============================================================================
if "📸 المختبر الذكي" in titles:
    with tabs[titles.index("📸 المختبر الذكي")]:
        guide("ارفع صورة تركيبة، وسيستخرج النظام القيم الغذائية تلقائياً.", "المختبر الذكي")
        
        if not OCR_AVAILABLE and not EASYOCR_AVAILABLE:
            st.warning("⚠️ مكتبات OCR غير مثبتة. يمكنك الإدخال يدوياً.")
        
        uploaded = st.file_uploader("📸 ارفع صورة التركيبة",
                                    type=['png','jpg','jpeg'], key="ocr_up")
        
        ocr_data = {}
        if uploaded and EASYOCR_AVAILABLE:
            try:
                image = PILImage.open(uploaded)
                st.image(image, caption="الصورة", use_container_width=True)
                
                if st.button("🔍 تحليل الصورة", key="ocr_analyze"):
                    with st.spinner("جاري التحليل..."):
                        try:
                            reader = easyocr.Reader(['ar','en'], gpu=False, verbose=False)
                            result = reader.readtext(np.array(image))
                            text = " ".join([r[1] for r in result if r[2] > 0.3])
                            
                            patterns = {
                                'cp': r'(?:بروتين|CP)[\s:]*([\d.]+)',
                                'dc': r'(?:معامل الهضم|DC)[\s:]*([\d.]+)',
                                'se': r'(?:معادل النشاء|SE)[\s:]*([\d.]+)',
                                'ndf': r'NDF[\s:]*([\d.]+)',
                                'adf': r'ADF[\s:]*([\d.]+)',
                                'ee': r'(?:دهن|EE)[\s:]*([\d.]+)',
                                'ash': r'(?:رماد|ASH)[\s:]*([\d.]+)'
                            }
                            for k, p in patterns.items():
                                m = re.search(p, text, re.IGNORECASE)
                                if m:
                                    try: ocr_data[k] = float(m.group(1))
                                    except: pass
                            
                            st.success("✅ تم التحليل!")
                            voice_guide("تم تحليل الصورة")
                        except Exception as e:
                            st.error(f"خطأ: {e}")
            except Exception as e:
                st.error(f"خطأ في الصورة: {e}")
        
        st.markdown("### ✍️ البيانات (يدوي أو مستخرج)")
        c1, c2 = st.columns(2)
        with c1:
            sample_name = st.text_input("اسم العينة:", value=ocr_data.get('sample_name',''), key="ocr_sn")
            cp = st.number_input("CP %:", 0.0, 100.0, float(ocr_data.get('cp',0.0)), 0.1, key="ocr_cp")
            dc = st.number_input("DC:", 0.0, 1.0, float(ocr_data.get('dc',0.85)), 0.01, key="ocr_dc")
            se = st.number_input("SE:", 0.0, 100.0, float(ocr_data.get('se',0.0)), 0.1, key="ocr_se")
        with c2:
            ndf = st.number_input("NDF %:", 0.0, 100.0, float(ocr_data.get('ndf',0.0)), 0.1, key="ocr_ndf")
            adf = st.number_input("ADF %:", 0.0, 100.0, float(ocr_data.get('adf',0.0)), 0.1, key="ocr_adf")
            ee = st.number_input("EE %:", 0.0, 100.0, float(ocr_data.get('ee',0.0)), 0.1, key="ocr_ee")
            ash = st.number_input("ASH %:", 0.0, 100.0, float(ocr_data.get('ash',0.0)), 0.1, key="ocr_ash")
        
        if st.button("💾 حفظ النتيجة", key="ocr_save"):
            try:
                DB.insert('lab_results', {
                    'result_id': secrets.token_hex(8),
                    'sample_name': sample_name, 'animal': '', 'stage': '',
                    'cp': cp, 'dp': cp*dc, 'se': se, 'ndf': ndf, 'adf': adf,
                    'ee': ee, 'ash': ash, 'image_path': uploaded.name if uploaded else '',
                    'notes': '', 'analyst': st.session_state['user'].get('full_name','مستخدم'),
                    'created_date': datetime.now().isoformat()
                })
                st.success("✅ تم الحفظ!")
            except Exception as e:
                st.error(f"خطأ: {e}")
        
        # عرض النتائج السابقة
        st.markdown("---")
        st.markdown("### 📋 النتائج السابقة")
        try:
            results = DB.execute("SELECT * FROM lab_results ORDER BY created_date DESC LIMIT 20")
            if results:
                df = pd.DataFrame([{
                    'التاريخ': r[14][:16] if r[14] else '',
                    'العينة': r[1], 'CP': r[4], 'DP': r[5], 'SE': r[6]
                } for r in results])
                st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception:
            st.info("لا توجد نتائج سابقة.")

# ============================================================================
# تبويب المختبر المتقدم
# ============================================================================
if "🔬 المختبر المتقدم" in titles:
    with tabs[titles.index("🔬 المختبر المتقدم")]:
        guide("حلل خلطتك الحالية وقارنها بالمعايير القياسية.", "المختبر المتقدم")
        
        c1, c2 = st.columns(2)
        with c1:
            lab_animal = st.selectbox("الفصيل:",
                ["أبقار","أغنام","ماعز","خيول","إبل","دواجن","أسماك"], key="lab_an")
            stages = list(STANDARDS.get(lab_animal, {}).keys())
            lab_stage = st.selectbox("المرحلة:", stages, key="lab_st") if stages else "عام"
            std = STANDARDS.get(lab_animal, {}).get(lab_stage, {}) if stages else {}
            if std:
                st.info(f"📊 DP={std.get('DP','-')}%, SE={std.get('SE','-')}, CP={std.get('CP','-')}%")
        
        with c2:
            st.markdown("#### 🧪 أدخل أوزان المكونات (كجم)")
            st.caption("اترك الحقل صفراً للمكونات غير الموجودة.")
        
        lab_inputs = {}
        cols = st.columns(3)
        for i, ing in enumerate(list(FLAT_FEEDS.keys())[:30]):
            with cols[i % 3]:
                lab_inputs[ing] = st.number_input(f"{ing}", 0.0, 10000.0, 0.0, 10.0,
                                                 key=f"lab_in_{ing}")
        
        if st.button("🧪 تشغيل التحليل", type="primary", key="lab_run", use_container_width=True):
            total = sum(lab_inputs.values())
            if total <= 0:
                st.warning("⚠️ أدخل أوزان أكبر من صفر")
            else:
                voice_guide(f"جاري تحليل العينة")
                st.info("🔄 جاري التحليل...")
                
                cp_t, dp_t, se_t = 0.0, 0.0, 0.0
                for ing, w in lab_inputs.items():
                    if w > 0:
                        pct = w/total
                        fd = FLAT_FEEDS.get(ing, {})
                        cp = fd.get("CP",0)
                        dc = fd.get("DC",0)
                        se = fd.get("SE",0)
                        cp_t += pct*cp
                        dp_t += pct*(cp*dc)
                        se_t += pct*se
                
                st.success(f"🔬 تم التحليل! إجمالي: {total:.1f} كجم")
                voice_guide("تم التحليل بنجاح")
                
                # جدول النتائج
                res_df = pd.DataFrame([
                    {"العنصر":"CP","القيمة":f"{cp_t:.2f}%"},
                    {"العنصر":"DP","القيمة":f"{dp_t:.2f}%"},
                    {"العنصر":"SE","القيمة":f"{se_t:.2f}"}
                ])
                st.dataframe(res_df, use_container_width=True, hide_index=True)
                
                # المقارنة مع المعايير
                if std:
                    st.markdown("#### 📊 المقارنة مع المعايير القياسية")
                    
                    dp_dev = ((dp_t - std.get('DP',0))/std.get('DP',1))*100 if std.get('DP',0)>0 else 0
                    se_dev = ((se_t - std.get('SE',0))/std.get('SE',1))*100 if std.get('SE',0)>0 else 0
                    cp_dev = ((cp_t - std.get('CP',0))/std.get('CP',1))*100 if std.get('CP',0)>0 else 0
                    
                    dp_g = "✅ ممتاز" if abs(dp_dev)<=5 else ("👍 جيد" if abs(dp_dev)<=10 else "⚠️ يحتاج")
                    se_g = "✅ ممتاز" if abs(se_dev)<=5 else ("👍 جيد" if abs(se_dev)<=10 else "⚠️ يحتاج")
                    cp_g = "✅ ممتاز" if abs(cp_dev)<=5 else ("👍 جيد" if abs(cp_dev)<=10 else "⚠️ يحتاج")
                    
                    eval_df = pd.DataFrame([
                        {"المقياس":"DP","المحسوب":f"{dp_t:.2f}","القياسي":f"{std.get('DP',0):.2f}","الانحراف":f"{dp_dev:+.1f}%","التقييم":dp_g},
                        {"المقياس":"SE","المحسوب":f"{se_t:.2f}","القياسي":f"{std.get('SE',0):.2f}","الانحراف":f"{se_dev:+.1f}%","التقييم":se_g},
                        {"المقياس":"CP","المحسوب":f"{cp_t:.2f}","القياسي":f"{std.get('CP',0):.2f}","الانحراف":f"{cp_dev:+.1f}%","التقييم":cp_g}
                    ])
                    st.dataframe(eval_df, use_container_width=True, hide_index=True)
                    
                    # الرسم البياني للمقارنة
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=['DP %','SE وحدة','CP %'],
                        y=[dp_t, se_t, cp_t],
                        name='المحسوب',
                        marker_color='#2e7d32',
                        text=[f"{dp_t:.1f}", f"{se_t:.1f}", f"{cp_t:.1f}"],
                        textposition='auto',
                        textfont=dict(size=14, color='white', family='Cairo')
                    ))
                    fig.add_trace(go.Bar(
                        x=['DP %','SE وحدة','CP %'],
                        y=[std.get('DP',0), std.get('SE',0), std.get('CP',0)],
                        name='المعايير القياسية',
                        marker_color='#1565C0',
                        text=[f"{std.get('DP',0):.1f}", f"{std.get('SE',0):.1f}", f"{std.get('CP',0):.1f}"],
                        textposition='auto',
                        textfont=dict(size=14, color='white', family='Cairo')
                    ))
                    fig.update_layout(
                        title=dict(text=f"مقارنة القيم المحسوبة مع المعايير - {lab_animal} ({lab_stage})",
                                  font=dict(size=16, color='#1b5e20', family='Cairo')),
                        barmode='group', height=450,
                        plot_bgcolor='rgba(240,248,240,0.5)',
                        font=dict(family='Cairo'),
                        legend=dict(font=dict(size=13, family='Cairo'))
                    )
                    st.plotly_chart(fig, use_container_width=True, key="lab_chart")
                    
                    # رسم الانحرافات
                    colors_dev = ['#2e7d32' if abs(d)<=5 else ('#f57c00' if abs(d)<=10 else '#c62828') 
                                 for d in [dp_dev, se_dev, cp_dev]]
                    fig2 = go.Figure(go.Bar(
                        x=['DP','SE','CP'],
                        y=[dp_dev, se_dev, cp_dev],
                        marker_color=colors_dev,
                        text=[f"{d:+.1f}%" for d in [dp_dev, se_dev, cp_dev]],
                        textposition='auto',
                        textfont=dict(size=14, color='white', family='Cairo')
                    ))
                    fig2.add_hline(y=0, line_dash="solid", line_color="black", line_width=2)
                    fig2.add_hline(y=5, line_dash="dash", line_color="#2e7d32", line_width=1)
                    fig2.add_hline(y=-5, line_dash="dash", line_color="#2e7d32", line_width=1)
                    fig2.update_layout(
                        title=dict(text="نسب الانحراف عن المعايير",
                                  font=dict(size=16, color='#1b5e20', family='Cairo')),
                        height=400, font=dict(family='Cairo')
                    )
                    st.plotly_chart(fig2, use_container_width=True, key="lab_dev_chart")
                    
                    # التقدير النهائي
                    if all([abs(d)<=5 for d in [dp_dev, se_dev, cp_dev]]):
                        grade = "ممتاز ✅"; grade_c = "#2e7d32"
                    elif all([abs(d)<=10 for d in [dp_dev, se_dev, cp_dev]]):
                        grade = "جيد 👍"; grade_c = "#f57c00"
                    else:
                        grade = "يحتاج تحسين ⚠️"; grade_c = "#c62828"
                    
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg,#f1f8e9,#e8f5e9);
                                padding:20px;border-radius:16px;
                                border-right:6px solid {grade_c};
                                text-align:center;margin:20px 0;'>
                        <div style='font-size:1rem;color:#666;'>⭐ التقدير العام</div>
                        <div style='font-size:2rem;font-weight:900;color:{grade_c};'>{grade}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # تحميل PDF
                    try:
                        pdf = PDF.lab_report(
                            {'cp':cp_t,'dp':dp_t,'se':se_t},
                            lab_animal, lab_stage, std,
                            {'DP':dp_g,'SE':se_g,'CP':cp_g},
                            st.session_state['user'].get('full_name','مستخدم')
                        )
                        
                        col_d1, col_d2 = st.columns(2)
                        with col_d1:
                            st.download_button("📄 تحميل تقرير PDF", pdf,
                                             file_name=f"lab_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                             mime="application/pdf",
                                             use_container_width=True, key="lab_pdf_dl")
                        with col_d2:
                            msg = f"تقرير المختبر\n{lab_animal} - {lab_stage}\nCP:{cp_t:.2f}% DP:{dp_t:.2f}% SE:{se_t:.2f}\nالتقدير: {grade}"
                            st.markdown(f'<a href="https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(msg)}" target="_blank" style="display:block;background:#25D366;color:white;padding:11px;border-radius:8px;text-align:center;text-decoration:none;font-weight:bold;">📲 مشاركة واتساب</a>', unsafe_allow_html=True)
                    except Exception as e:
                        st.warning(f"PDF: {e}")

# ============================================================================
# تبويب بدائل الحليب
# ============================================================================
if "🍼 بدائل الحليب" in titles:
    with tabs[titles.index("🍼 بدائل الحليب")]:
        guide("تركيب بديل حليب للصغار حسب العمر.", "بدائل الحليب")
        
        st.markdown('<div class="section-title">🍼 تركيب بديل الحليب</div>', unsafe_allow_html=True)
        
        at = st.selectbox("نوع الحيوان:",
            ["عجل بقري","حملان أغنام","جديان ماعز","مهرات خيول","أطفال إبل"], key="mr_at")
        age = st.slider("العمر (يوم)", 1, 120, 30, key="mr_age")
        
        needs = {
            "عجل بقري":{"protein":22,"fat":18,"energy":75,"volume":8},
            "حملان أغنام":{"protein":24,"fat":20,"energy":72,"volume":4},
            "جديان ماعز":{"protein":23,"fat":19,"energy":70,"volume":3},
            "مهرات خيول":{"protein":20,"fat":15,"energy":68,"volume":5},
            "أطفال إبل":{"protein":21,"fat":17,"energy":66,"volume":6}
        }
        
        af = 1.2 if age<14 else (1.0 if age<30 else (0.85 if age<60 else 0.70))
        tp = needs[at]["protein"]*af
        tf = needs[at]["fat"]*af
        te = needs[at]["energy"]*af
        vol = needs[at]["volume"]*af
        
        st.info(f"📊 الاحتياجات: بروتين {tp:.1f}% | دهون {tf:.1f}% | طاقة {te:.1f}")
        
        replacer_ing = {
            "حليب مجفف":{"CP":34.0,"Fat":1.0,"SE":40.0,"Cost":18.0},
            "مصل الحليب (Whey)":{"CP":12.0,"Fat":1.0,"SE":35.0,"Cost":12.0},
            "دهن نباتي":{"CP":0.0,"Fat":99.0,"SE":10.0,"Cost":8.0},
            "ليسيثين الصويا":{"CP":0.0,"Fat":95.0,"SE":0.0,"Cost":15.0},
            "بروتين الصويا المركز":{"CP":65.0,"Fat":1.0,"SE":30.0,"Cost":20.0}
        }
        
        selected = []
        prices = {}
        cols = st.columns(3)
        for i, (ing, d) in enumerate(replacer_ing.items()):
            with cols[i % 3]:
                if st.checkbox(ing, value=(i<4), key=f"mr_{ing}"):
                    selected.append(ing)
                    prices[ing] = st.number_input(f"سعر", 1.0, 100.0, float(d["Cost"]), key=f"mrp_{ing}")
        
        if st.button("🍼 تشغيل المحرك", type="primary", key="mr_run"):
            if len(selected) < 3:
                st.warning("⚠️ اختر 3 مكونات على الأقل")
            else:
                with st.spinner("جاري الحساب..."):
                    try:
                        c = [prices[i] for i in selected]
                        bounds = [(0,100) for _ in selected]
                        pr = [replacer_ing[i]["CP"] for i in selected]
                        fat = [replacer_ing[i]["Fat"] for i in selected]
                        se = [replacer_ing[i]["SE"] for i in selected]
                        
                        A_eq = [[1]*len(selected)]
                        b_eq = [100]
                        
                        # قيود: بروتين قريب من الهدف، دهون لا تتجاوز
                        A_ub = [pr, [-x for x in pr], fat, [-x for x in se]]
                        b_ub = [tp*1.1, -tp*0.9, tf*1.15, -te*0.85]
                        
                        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                                    bounds=bounds, method='highs')
                        
                        if res.success:
                            formula = {selected[i]: res.x[i] for i in range(len(selected)) if res.x[i] > 0.0001}
                            cost_kg = res.fun/100.0
                            st.success(f"✅ التكلفة: ${cost_kg:.2f}/كجم")
                            voice_guide("تم توليد بديل الحليب بنجاح")
                            
                            for k, v in formula.items():
                                st.markdown(f'<div class="formula-item"><span>{k}</span><span>{v:.1f}% ({v*10:.1f} جم)</span></div>', unsafe_allow_html=True)
                            
                            st.info(f"🥛 الجرعة: {vol:.1f} لتر/يوم، التركيز: 100-150 جم/لتر")
                        else:
                            st.error("❌ تعذر إيجاد حل. حاول تعديل المكونات.")
                    except Exception as e:
                        st.error(f"خطأ: {e}")

# ============================================================================
# تبويب مواقيت الصلاة
# ============================================================================
if "🕌 مواقيت الصلاة" in titles:
    with tabs[titles.index("🕌 مواقيت الصلاة")]:
        guide("عرض مواقيت الصلاة حسب المدينة.", "مواقيت الصلاة")
        
        st.markdown('<div class="section-title">🕌 مواقيت الصلاة</div>', unsafe_allow_html=True)
        
        cities = ["مكة المكرمة","المدينة المنورة","الخرطوم","طرابلس","القاهرة",
                  "دبي","الرياض","صنعاء","عمان","بيروت","دمشق","بغداد","الكويت"]
        city = st.selectbox("اختر المدينة:", cities, key="prayer_city")
        
        times = {"الفجر":"05:00","الشروق":"06:30","الظهر":"12:00",
                 "العصر":"15:30","المغرب":"18:00","العشاء":"19:30"}
        
        cols = st.columns(3)
        for i, (name, t) in enumerate(times.items()):
            with cols[i % 3]:
                st.metric(name, t)
        
        if st.button("🔔 تشغيل التنبيه الصوتي", key="prayer_voice"):
            voice_guide(f"مواقيت الصلاة في {city}. الفجر الخامسة صباحاً.")
            st.success("✅ تم تشغيل التنبيه")

# ============================================================================
# تبويب منبه الجرعات
# ============================================================================
if "💊 منبه الجرعات" in titles:
    with tabs[titles.index("💊 منبه الجرعات")]:
        guide("تسجيل ومتابعة اللقاحات والفيتامينات.", "منبه الجرعات")
        
        st.markdown('<div class="section-title">💊 منبه الجرعات</div>', unsafe_allow_html=True)
        
        if "dose_reminders" not in st.session_state:
            st.session_state["dose_reminders"] = []
        
        with st.expander("➕ إضافة جرعة جديدة", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                a = st.selectbox("الحيوان:", ["أبقار","أغنام","ماعز","خيول","إبل","دواجن","أسماك"], key="dr_a")
                t = st.selectbox("النوع:", ["لقاح","فيتامين","دواء"], key="dr_t")
                n = st.text_input("الاسم:", key="dr_n")
            with c2:
                amt = st.number_input("الجرعة:", 0.0, 1000.0, 1.0, key="dr_amt")
                unit = st.selectbox("الوحدة:", ["مل","جم","مجم","قطرة"], key="dr_u")
                route = st.selectbox("الطريقة:", ["عضل","تحت الجلد","فموي","مياه الشرب"], key="dr_r")
            with c3:
                freq = st.number_input("التكرار (أيام):", 1, 365, 7, key="dr_f")
                start = st.date_input("البدء:", datetime.now(), key="dr_s")
                notes = st.text_area("ملاحظات:", key="dr_notes")
            
            if st.button("💾 حفظ", key="dr_save"):
                if n:
                    st.session_state["dose_reminders"].append({
                        'id': secrets.token_hex(4), 'animal': a, 'type': t, 'name': n,
                        'amount': amt, 'unit': unit, 'route': route,
                        'frequency': freq, 'start': start.isoformat(),
                        'next': (start + timedelta(days=freq)).isoformat(),
                        'notes': notes
                    })
                    st.success("✅ تم الحفظ")
                    voice_guide(f"تم حفظ جرعة {n}")
                    st.rerun()
        
        if st.session_state["dose_reminders"]:
            st.markdown("### 📋 الجرعات المسجلة")
            for r in st.session_state["dose_reminders"]:
                with st.expander(f"💊 {r['name']} - {r['animal']}"):
                    st.write(f"**النوع:** {r['type']}")
                    st.write(f"**الجرعة:** {r['amount']} {r['unit']} - {r['route']}")
                    st.write(f"**التكرار:** كل {r['frequency']} يوم")
                    st.write(f"**الجرعة القادمة:** {r['next'][:10]}")
                    if r['notes']: st.write(f"**ملاحظات:** {r['notes']}")

# ============================================================================
# تبويب بورصة الأسعار
# ============================================================================
if "📊 بورصة الأسعار" in titles:
    with tabs[titles.index("📊 بورصة الأسعار")]:
        guide("أسعار المواشي والمنتجات.", "بورصة الأسعار")
        
        st.markdown('<div class="section-title">📊 بورصة الأسعار</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🐄 أسعار المواشي")
            for name, price in list(st.session_state["global_livestock"].items()):
                if role == "owner":
                    new_p = st.number_input(name, value=float(price), step=5.0, key=f"ls_{name}")
                    st.session_state["global_livestock"][name] = new_p
                else:
                    st.write(f"▪️ {name}: **${price:.2f}**")
        
        with c2:
            st.subheader("🥩 أسعار المنتجات")
            for name, price in list(st.session_state["global_products"].items()):
                if role == "owner":
                    new_p = st.number_input(name, value=float(price), step=0.5, key=f"pr_{name}")
                    st.session_state["global_products"][name] = new_p
                else:
                    st.write(f"▪️ {name}: **${price:.2f}**")

# ============================================================================
# تبويب المستودعات
# ============================================================================
if "🏭 المستودعات" in titles:
    with tabs[titles.index("🏭 المستودعات")]:
        guide("متابعة المخزون.", "المستودعات")
        
        st.markdown('<div class="section-title">🏭 المستودعات</div>', unsafe_allow_html=True)
        
        inv_data = []
        for name, d in st.session_state["inventory"].items():
            qty = d["qty"]; mn = d["min"]
            status = "🔴" if qty<=0 else ("🟠" if qty<mn else "🟢")
            inv_data.append({"المادة":name, "الكمية (طن)":qty, "الحد الأدنى":mn, "الحالة":status})
        
        st.dataframe(pd.DataFrame(inv_data), use_container_width=True, hide_index=True)
        
        if role == "owner":
            with st.expander("تحديث المخزون"):
                sel = st.selectbox("المادة:", list(FLAT_FEEDS.keys()), key="inv_sel")
                new_q = st.number_input("الكمية:", 0.0, 10000.0,
                                       float(st.session_state["inventory"][sel]["qty"]),
                                       key="inv_q")
                if st.button("تحديث", key="inv_up"):
                    st.session_state["inventory"][sel]["qty"] = new_q
                    st.success("✅ تم التحديث")
                    st.rerun()

# ============================================================================
# تبويب الإنتاج اليومي
# ============================================================================
if "📈 الإنتاج اليومي" in titles:
    with tabs[titles.index("📈 الإنتاج اليومي")]:
        guide("تسجيل بيانات الإنتاج اليومي.", "الإنتاج اليومي")
        
        st.markdown('<div class="section-title">📈 الإنتاج اليومي</div>', unsafe_allow_html=True)
        
        with st.form("daily_prod"):
            c1, c2, c3 = st.columns(3)
            with c1:
                farm = st.text_input("المزرعة:", key="dp_farm")
                d = st.date_input("التاريخ:", datetime.now(), key="dp_date")
            with c2:
                milk = st.number_input("الحليب (لتر):", 0.0, 10000.0, 0.0, key="dp_milk")
                eggs = st.number_input("البيض:", 0, 100000, 0, key="dp_eggs")
            with c3:
                wg = st.number_input("زيادة الوزن (كجم):", 0.0, 10000.0, 0.0, key="dp_wg")
                mort = st.number_input("النافق:", 0, 10000, 0, key="dp_dead")
            notes = st.text_area("ملاحظات:", key="dp_notes")
            
            if st.form_submit_button("💾 حفظ"):
                st.session_state["daily_logs"].append({
                    "farm": farm, "date": d.isoformat(), "milk": milk,
                    "eggs": eggs, "weight_gain": wg, "mortality": mort, "notes": notes
                })
                st.success("✅ تم الحفظ")
        
        if st.session_state["daily_logs"]:
            st.markdown("### 📋 السجل")
            st.dataframe(pd.DataFrame(st.session_state["daily_logs"]),
                        use_container_width=True, hide_index=True)

# ============================================================================
# تبويب المراجع العلمية
# ============================================================================
if "📚 المراجع العلمية" in titles:
    with tabs[titles.index("📚 المراجع العلمية")]:
        guide("مراجع في تغذية الحيوان + بنك المعرفة.", "المراجع")
        
        st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
        
        refs = [
            {"authors":"McDonald et al.","year":2011,"title":"Animal Nutrition",
             "publisher":"Pearson","summary":"المرجع الأساسي في تغذية الحيوان"},
            {"authors":"NRC","year":2001,"title":"Nutrient Requirements of Dairy Cattle",
             "publisher":"National Academies","summary":"المرجع الأساسي لأبقار الحليب"},
            {"authors":"NRC","year":2000,"title":"Nutrient Requirements of Beef Cattle",
             "publisher":"National Academies","summary":"المرجع الأساسي لأبقار التسمين"},
            {"authors":"Van Soest, P.J.","year":1994,"title":"Nutritional Ecology of the Ruminant",
             "publisher":"Cornell","summary":"المرجع الكلاسيكي في تغذية المجترات"},
            {"authors":"Leeson & Summers","year":2009,"title":"Commercial Poultry Nutrition",
             "publisher":"Nottingham","summary":"المرجع العملي في تغذية الدواجن"},
            {"authors":"INRA","year":2007,"title":"INRA Feeding System for Ruminants",
             "publisher":"Wageningen","summary":"النظام الفرنسي لتغذية المجترات"}
        ]
        
        for r in refs:
            st.markdown(f"""
            <div style='background:#f8f9fa;padding:14px;border-radius:10px;
                margin-bottom:10px;border-right:4px solid #2e7d32;'>
                <b>{r['title']}</b> ({r['year']})<br>
                👤 {r['authors']}<br>
                📚 {r['publisher']}<br>
                <small>{r['summary']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🧠 بنك المعرفة السريع")
        q = st.text_input("اسأل:", key="kb_q", placeholder="مثال: ما هو البروتين المهضوم؟")
        if q:
            kb = {
                "البروتين المهضوم":"هو البروتين الذي يستطيع الحيوان هضمه وامتصاصه فعلياً. يُحسب بضرب CP × معامل الهضم.",
                "معادل النشاء":"مقياس للطاقة في العلف مقارنة بالنشاء النقي.",
                "EPEF":"مؤشر الأداء الأوروبي = (الحيوية × الوزن) / (العمر × FCR) × 100.",
                "FCR":"معامل التحويل الغذائي = كمية العلف / الوزن المكتسب."
            }
            for k, v in kb.items():
                if k in q:
                    st.success(f"📖 {v}")
                    break
            else:
                st.info("❓ لم أجد إجابة. حاول صياغة مختلفة.")

# ============================================================================
# تبويب التعليقات
# ============================================================================
if "💬 التعليقات" in titles:
    with tabs[titles.index("💬 التعليقات")]:
        guide("قناة لتبادل الخبرات.", "التعليقات")
        
        st.markdown('<div class="section-title">💬 تعليقات المختصين</div>', unsafe_allow_html=True)
        
        st.text_area("التعليقات:", value=st.session_state["comments"],
                     height=200, disabled=True, key="cmt_disp")
        
        new = st.text_area("أضف تعليقاً:", key="cmt_new")
        if st.button("📤 نشر", key="cmt_post"):
            if new:
                role_ar = {"owner":"المالك","specialist":"مختص","veterinarian":"بيطري",
                          "nutritionist":"تغذية","breeder":"مربي"}.get(role, "مستخدم")
                st.session_state["comments"] += f"\n• [{role_ar} {datetime.now().strftime('%Y-%m-%d %H:%M')}]: {new}"
                st.success("✅ تم النشر")
                st.rerun()

# ============================================================================
# تبويب المساعدة
# ============================================================================
if "💡 المساعدة" in titles:
    with tabs[titles.index("💡 المساعدة")]:
        guide("دليل سريع للمنصة.", "المساعدة")
        
        st.markdown('<div class="section-title">💡 المساعدة الذكية</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background:#e3f2fd;padding:20px;border-radius:12px;direction:rtl;'>
        <h3>🌟 خطوات الاستخدام:</h3>
        <ol>
        <li>اختر نوع الحيوان من تبويب القطاع الحيواني</li>
        <li>حدد السلالة والمرحلة الإنتاجية</li>
        <li>أدخل القياسات (إن توفرت)</li>
        <li>اختر المكونات وحدد أسعارها</li>
        <li>اضغط تشغيل المحرك للحصول على الخلطة</li>
        <li>حمّل تقرير PDF أو شاركه عبر واتساب</li>
        </ol>
        
        <h3>🔬 المختبر الذكي:</h3>
        <p>ارفع صورة تركيبة، والنظام يستخرج القيم الغذائية.</p>
        
        <h3>🔬 المختبر المتقدم:</h3>
        <p>أدخل أوزان مكونات خلطتك، واحصل على مقارنة مع المعايير و PDF.</p>
        
        <h3>📞 الدعم:</h3>
        <p>abukram128@gmail.com | +249123533489</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔊 دليل صوتي", key="help_voice"):
            play_full_guide()

# ============================================================================
# تبويب دليل المستخدم
# ============================================================================
if "📖 دليل المستخدم" in titles:
    with tabs[titles.index("📖 دليل المستخدم")]:
        guide("شرح مفصل.", "دليل المستخدم")
        
        st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background:#ffffff;padding:30px;border-radius:16px;
            box-shadow:0 8px 35px rgba(0,0,0,0.08);direction:rtl;'>
        
        <div style='background:linear-gradient(135deg,#1a237e,#283593);color:white;
            padding:15px;border-radius:10px;font-weight:bold;margin-top:15px;'>
            📘 الفصل 1: مقدمة
        </div>
        <div style='padding:20px;background:#f8f9fa;border-left:4px solid #3498db;
            border-radius:0 10px 10px 0;margin-bottom:15px;'>
        تاور نولجي منصة متكاملة لتركيب الأعلاف وإدارة الإنتاج الحيواني.
        تعتمد على البرمجة الخطية لحساب أقل تكلفة لخلطة تلبي الاحتياجات الغذائية.
        </div>
        
        <div style='background:linear-gradient(135deg,#1a237e,#283593);color:white;
            padding:15px;border-radius:10px;font-weight:bold;'>
            📗 الفصل 2: تركيب العلف
        </div>
        <div style='padding:20px;background:#f8f9fa;border-left:4px solid #3498db;
            border-radius:0 10px 10px 0;margin-bottom:15px;'>
        1. اختر نوع الحيوان<br>
        2. حدد السلالة والمرحلة<br>
        3. أدخل القياسات<br>
        4. اختر المكونات<br>
        5. اضغط تشغيل المحرك<br>
        6. حمّل التقرير PDF
        </div>
        
        <div style='background:linear-gradient(135deg,#1a237e,#283593);color:white;
            padding:15px;border-radius:10px;font-weight:bold;'>
            🔬 الفصل 3: المختبرات
        </div>
        <div style='padding:20px;background:#f8f9fa;border-left:4px solid #3498db;
            border-radius:0 10px 10px 0;margin-bottom:15px;'>
        <b>المختبر الذكي:</b> ارفع صورة لتحليلها بـ OCR.<br>
        <b>المختبر المتقدم:</b> أدخل أوزان مكوناتك واحصل على مقارنة + رسوم + PDF.
        </div>
        
        <div style='background:linear-gradient(135deg,#1a237e,#283593);color:white;
            padding:15px;border-radius:10px;font-weight:bold;'>
            🍼 الفصل 4: بدائل الحليب
        </div>
        <div style='padding:20px;background:#f8f9fa;border-left:4px solid #3498db;
            border-radius:0 10px 10px 0;'>
        اختر نوع الحيوان والعمر، وحدد المكونات، وسيقوم النظام بحساب التركيبة المثالية.
        </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# تبويب إرسال الكود (للمالك فقط)
# ============================================================================
if "📧 إرسال الكود" in titles:
    with tabs[titles.index("📧 إرسال الكود")]:
        guide("إرسال السورس كود إلى البريد.", "إرسال الكود")
        
        st.markdown('<div class="section-title">📧 إرسال السورس كود</div>', unsafe_allow_html=True)
        
        st.info("هذه الخاصية متاحة فقط للمالك.")
        
        email = st.text_input("البريد المستلم:", value=OWNER_EMAIL, key="send_email")
        
        if st.button("📤 إرسال الكود", type="primary", use_container_width=True, key="send_btn"):
            if email and '@' in email:
                with st.spinner("جاري الإرسال..."):
                    ok, msg = send_code_to_email(email)
                    if ok:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)
            else:
                st.warning("⚠️ أدخل بريداً صحيحاً")

# ============================================================================
# التوقيع النهائي
# ============================================================================
render_signature()

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# نهاية الكود
# ============================================================================
