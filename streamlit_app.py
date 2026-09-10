# ============================================================================
# 🌾 تاور نولجي Tawornology العلمية - الإصدار النهائي 17.0
# ============================================================================
# بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ
# 
# منصة تاور نولجي Tawornology العلمية للانتاج الحيواني وتركيب الاعلاف
# 
# 🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله
# 
# المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور
#           اختصاصي تغذية الحيوان - Tawornology
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
import hashlib
import secrets
import io
import sqlite3
import warnings
import re
import math
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from scipy.optimize import linprog
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Tuple, Optional, Any

# =====================================================================
# استيرادات PDF والعربية
# =====================================================================
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import (Table, TableStyle, Paragraph, Spacer, 
                                 Image, SimpleDocTemplate, PageBreak)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import arabic_reshaper
from bidi.algorithm import get_display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

# =====================================================================
# مكتبات الصوت
# =====================================================================
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# =====================================================================
# مكتبات OCR
# =====================================================================
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

import plotly.express as px
import plotly.graph_objects as go

# =====================================================================
# إعدادات الصفحة
# =====================================================================
st.set_page_config(
    page_title="تاور نولجي Tawornology العلمية",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================================
# ثوابت النظام
# =====================================================================
OWNER_PASSWORD = "202687"  # كلمة مرور المالك الوحيدة
OWNER_NAME = "الاختصاصي م. عبد القادر إسماعيل تاور"
OWNER_TITLE = "اختصاصي تغذية الحيوان - Tawornology"
OWNER_EMAIL = "abukram128@gmail.com"
SENDER_EMAIL = "abukram128@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
WHATSAPP_NUMBER = "+249123533489"
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

# =====================================================================
# كلمة مرور البريد (من secrets لتجنب تخزينها في الكود)
# =====================================================================
def get_email_password():
    """استرجاع كلمة مرور البريد من secrets"""
    try:
        return st.secrets["email"]["password"]
    except Exception:
        return st.session_state.get("email_pwd_input", None)

# =====================================================================
# تحميل صورة المشرف
# =====================================================================
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

# =====================================================================
# معالج النصوص العربية
# =====================================================================
class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=2000)
    def fix(text):
        if not text:
            return ""
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)

arabic_processor = ArabicTextProcessor()

# =====================================================================
# دوال الصوت
# =====================================================================
@st.cache_data(ttl=3600)
def text_to_speech_b64(text, lang="ar"):
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
            f'<audio autoplay><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mpeg"></audio>',
            height=0
        )
        return True
    return False

def voice_guide(message, lang="ar"):
    """تشغيل رسالة صوتية واحدة"""
    if not GTTS_AVAILABLE or not message:
        return
    b64 = text_to_speech_b64(message, lang)
    if b64:
        play_audio_b64(b64)

def voice_guide_sequential(messages, lang="ar"):
    """تشغيل رسائل صوتية متتالية"""
    if not GTTS_AVAILABLE:
        return
    for i, msg in enumerate(messages):
        if msg:
            b64 = text_to_speech_b64(msg, lang)
            if b64:
                play_audio_b64(b64)
                word_count = len(msg.split())
                duration = max(2.0, word_count * 0.35 + 1.0)
                time.sleep(duration)

def voice_welcome(role="public"):
    msgs = {
        "owner": [f"مرحباً بك، {OWNER_NAME}."],
        "public": ["مرحباً بك زائراً في تاور نولجي."]
    }
    voice_guide_sequential(msgs.get(role, msgs["public"]))

# =====================================================================
# دوال الأمان
# =====================================================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

# =====================================================================
# دوال إرسال البريد
# =====================================================================
def send_code_to_email(receiver_email: str) -> Tuple[bool, str]:
    """إرسال السورس كود إلى البريد"""
    if receiver_email.strip().lower() != OWNER_EMAIL.strip().lower():
        return False, f"❌ الإرسال مسموح فقط للبريد: {OWNER_EMAIL}"
    
    password = get_email_password()
    if not password:
        st.session_state["need_email_pwd"] = True
        return False, "⚠️ يرجى إدخال كلمة مرور البريد أدناه."
    
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception:
        code_content = "# تعذر قراءة الكود من الملف الحالي"
    
    file_hash = hashlib.md5(code_content.encode()).hexdigest()
    lines_count = len(code_content.split('\n'))
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 تاور نولجي Tawornology v17.0 - السورس كود"
    
    body = f"""بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ

السلام عليكم ورحمة الله وبركاته،

مرفق السورس كود الكامل لمنصة تاور نولجي Tawornology العلمية.

📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔑 التوقيع الرقمي: {file_hash}
📄 عدد الأسطر: {lines_count}
👨‍💻 المشرف العام: {OWNER_NAME}
🎓 الصفة: {OWNER_TITLE}

🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    attachment = MIMEText(code_content, 'plain', 'utf-8')
    attachment.add_header('Content-Disposition', 'attachment',
                          filename="tawornology_v17.py")
    msg.attach(attachment)
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, password)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True, f"✅ تم إرسال الكود بنجاح إلى {receiver_email}"
    except Exception as e:
        return False, f"❌ فشل الإرسال: {str(e)}"
        # =====================================================================
# نظام قاعدة البيانات
# =====================================================================
class DatabaseManager:
    def __init__(self, db_path="tawornology.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # جدول المستخدمين
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            created_date TEXT,
            last_login TEXT
        )''')
        
        # جدول المزارع
        c.execute('''CREATE TABLE IF NOT EXISTS farms (
            farm_id TEXT PRIMARY KEY,
            farm_name TEXT,
            farm_type TEXT,
            owner_name TEXT,
            owner_phone TEXT,
            location TEXT,
            created_date TEXT
        )''')
        
        # جدول دورات الإنتاج
        c.execute('''CREATE TABLE IF NOT EXISTS cycles (
            cycle_id TEXT PRIMARY KEY,
            farm_id TEXT,
            cycle_type TEXT,
            start_date TEXT,
            end_date TEXT,
            initial_count INTEGER,
            breed TEXT,
            status TEXT
        )''')
        
        # جدول السجلات اليومية
        c.execute('''CREATE TABLE IF NOT EXISTS daily_records (
            record_id TEXT PRIMARY KEY,
            cycle_id TEXT,
            record_date TEXT,
            age_days INTEGER,
            live_count INTEGER,
            avg_weight REAL,
            feed_consumed REAL,
            dead_count INTEGER,
            temperature REAL,
            humidity REAL,
            notes TEXT
        )''')
        
        # جدول التحصينات
        c.execute('''CREATE TABLE IF NOT EXISTS vaccinations (
            vax_id TEXT PRIMARY KEY,
            cycle_id TEXT,
            vax_date TEXT,
            age_days INTEGER,
            vax_type TEXT,
            vax_name TEXT,
            dose TEXT,
            route TEXT
        )''')
        
        # جدول التركيبات المحفوظة
        c.execute('''CREATE TABLE IF NOT EXISTS saved_formulas (
            formula_id TEXT PRIMARY KEY,
            formula_name TEXT,
            animal_type TEXT,
            breed TEXT,
            stage TEXT,
            requester_name TEXT,
            target_dp REAL,
            target_se REAL,
            ingredients TEXT,
            total_cost REAL,
            created_by TEXT,
            created_date TEXT
        )''')
        
        # جدول نتائج المختبر
        c.execute('''CREATE TABLE IF NOT EXISTS lab_results (
            result_id TEXT PRIMARY KEY,
            sample_name TEXT,
            animal_type TEXT,
            stage TEXT,
            cp REAL,
            dp REAL,
            se REAL,
            ndf REAL,
            adf REAL,
            ee REAL,
            ash REAL,
            moisture REAL,
            notes TEXT,
            performed_by TEXT,
            result_date TEXT
        )''')
        
        # جدول المخزون
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT PRIMARY KEY,
            item_name TEXT UNIQUE,
            quantity REAL,
            min_threshold REAL,
            unit TEXT,
            last_updated TEXT
        )''')
        
        # جدول الأسعار
        c.execute('''CREATE TABLE IF NOT EXISTS price_history (
            record_id TEXT PRIMARY KEY,
            item_name TEXT,
            price REAL,
            currency TEXT,
            record_date TEXT
        )''')
        
        # جدول الفواتير
        c.execute('''CREATE TABLE IF NOT EXISTS invoices (
            invoice_id TEXT PRIMARY KEY,
            customer_name TEXT,
            customer_phone TEXT,
            formula_id TEXT,
            quantity_ton REAL,
            unit_price REAL,
            total_price REAL,
            status TEXT,
            created_by TEXT,
            created_date TEXT
        )''')
        
        # جدول منبه الجرعات
        c.execute('''CREATE TABLE IF NOT EXISTS dose_reminders (
            reminder_id TEXT PRIMARY KEY,
            animal_type TEXT,
            dose_type TEXT,
            dose_name TEXT,
            dose_amount REAL,
            dose_unit TEXT,
            administration_route TEXT,
            frequency_days INTEGER,
            start_date TEXT,
            next_dose_date TEXT,
            notes TEXT,
            active INTEGER DEFAULT 1
        )''')
        
        # جدول بدائل الحليب
        c.execute('''CREATE TABLE IF NOT EXISTS milk_replacers (
            replacer_id TEXT PRIMARY KEY,
            animal_type TEXT,
            age_days INTEGER,
            formula_name TEXT,
            ingredients TEXT,
            instructions TEXT,
            created_by TEXT,
            created_date TEXT
        )''')
        
        conn.commit()
        conn.close()
    
    def execute(self, query: str, params: tuple = ()):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        result = c.execute(query, params)
        conn.commit()
        data = result.fetchall()
        conn.close()
        return data
    
    def insert(self, table: str, data: dict) -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        cols = ', '.join(data.keys())
        phs = ', '.join(['?' for _ in data])
        try:
            c.execute(f"INSERT INTO {table} ({cols}) VALUES ({phs})", 
                      list(data.values()))
            conn.commit()
            conn.close()
            return True
        except Exception:
            conn.close()
            return False
    
    def get(self, table: str, conditions: dict = None):
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
    
    def update(self, table: str, data: dict, condition: dict) -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        set_clause = ', '.join([f"{k}=?" for k in data.keys()])
        where = ' AND '.join([f"{k}=?" for k in condition.keys()])
        try:
            c.execute(f"UPDATE {table} SET {set_clause} WHERE {where}",
                     list(data.values()) + list(condition.values()))
            conn.commit()
            conn.close()
            return True
        except Exception:
            conn.close()
            return False
    
    def delete(self, table: str, condition: dict) -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        where = ' AND '.join([f"{k}=?" for k in condition.keys()])
        try:
            c.execute(f"DELETE FROM {table} WHERE {where}",
                     list(condition.values()))
            conn.commit()
            conn.close()
            return True
        except Exception:
            conn.close()
            return False

# =====================================================================
# نظام إدارة المزارع
# =====================================================================
class FarmManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_farm(self, name, ftype, owner, phone, location=""):
        fid = secrets.token_hex(8)
        self.db.insert('farms', {
            'farm_id': fid, 'farm_name': name, 'farm_type': ftype,
            'owner_name': owner, 'owner_phone': phone, 'location': location,
            'created_date': datetime.now().isoformat()
        })
        return fid
    
    def create_cycle(self, farm_id, ctype, count, breed):
        cid = secrets.token_hex(8)
        self.db.insert('cycles', {
            'cycle_id': cid, 'farm_id': farm_id, 'cycle_type': ctype,
            'start_date': datetime.now().isoformat(), 'end_date': '',
            'initial_count': count, 'breed': breed, 'status': 'active'
        })
        return cid
    
    def add_daily(self, cycle_id, data):
        rid = secrets.token_hex(8)
        self.db.insert('daily_records', {
            'record_id': rid, 'cycle_id': cycle_id,
            'record_date': datetime.now().isoformat(),
            'age_days': data.get('age_days', 0),
            'live_count': data.get('live_count', 0),
            'avg_weight': data.get('avg_weight', 0),
            'feed_consumed': data.get('feed_consumed', 0),
            'dead_count': data.get('dead_count', 0),
            'temperature': data.get('temperature', 0),
            'humidity': data.get('humidity', 0),
            'notes': data.get('notes', '')
        })
        return rid
    
    def get_farms(self):
        return self.db.get('farms')
    
    def get_cycles(self, farm_id=None):
        if farm_id:
            return self.db.get('cycles', {'farm_id': farm_id})
        return self.db.get('cycles')
    
    def get_active_cycles(self):
        return self.db.get('cycles', {'status': 'active'})
    
    def close_cycle(self, cycle_id):
        self.db.update('cycles', {
            'status': 'completed',
            'end_date': datetime.now().isoformat()
        }, {'cycle_id': cycle_id})

# =====================================================================
# مكتبة الأعلاف الشاملة (95+ مادة علفية)
# =====================================================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح محلي": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6},
        "جريش أرز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2},
        "دخن": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2},
        "شوفان": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0},
        "تفل العنب": {"CP": 12.0, "DC": 0.50, "SE": 45.0, "NDF": 45.0, "ADF": 30.0, "EE": 5.0, "ASH": 8.0},
        "نخالة أرز": {"CP": 12.5, "DC": 0.70, "SE": 55.0, "NDF": 30.0, "ADF": 15.0, "EE": 15.0, "ASH": 8.0},
        "شعير مستنبت": {"CP": 15.0, "DC": 0.75, "SE": 60.0, "NDF": 25.0, "ADF": 12.0, "EE": 3.0, "ASH": 5.0}
    },
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8},
        "كسب السمسم": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5},
        "كسب جلوتين الذرة": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5},
        "كسب كانولا": {"CP": 38.0, "DC": 0.82, "SE": 62.0, "NDF": 28.0, "ADF": 18.0, "EE": 3.5, "ASH": 7.5},
        "كسب زهرة الشمس": {"CP": 30.0, "DC": 0.74, "SE": 40.0, "NDF": 42.0, "ADF": 28.0, "EE": 3.0, "ASH": 6.0}
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
        "تبن قمح": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5},
        "قشر فول سوداني": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5},
        "سرسة أرز": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5},
        "مخلفات بسكويت": {"CP": 10.0, "DC": 0.80, "SE": 65.0, "NDF": 8.0, "ADF": 4.0, "EE": 12.0, "ASH": 3.0},
        "قش الأرز المعالج": {"CP": 4.0, "DC": 0.40, "SE": 25.0, "NDF": 65.0, "ADF": 40.0, "EE": 1.5, "ASH": 12.0}
    },
    "🧬 البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق أسماك 72%": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5},
        "مركزات دواجن": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركزات مجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5},
        "بروتين مصل الحليب": {"CP": 80.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 3.0, "ASH": 3.0},
        "بروتين الدم": {"CP": 85.0, "DC": 0.92, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.5, "ASH": 5.0}
    },
    "🧪 الأحماض الأمينية": {
        "ليسين": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5},
        "ميثيونين": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3},
        "ثريونين": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2},
        "تريبتوفان": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1},
        "فالين": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1}
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس بياض": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس أبقار": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم فايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
        "إنزيم NSP": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0},
        "كبريتات حديدوز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0},
        "خميرة الخبز": {"CP": 45.0, "DC": 0.85, "SE": 35.0, "NDF": 5.0, "ADF": 2.0, "EE": 2.5, "ASH": 7.0}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
        "أكسيد المغنيسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "يوريا علفية": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0},
        "كلوريد الكولين": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 75.0}
    },
    "🍼 مكونات بدائل الحليب": {
        "مصل الحليب المجفف": {"CP": 12.0, "DC": 0.95, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.0},
        "حليب مجفف خالي الدسم": {"CP": 34.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.5},
        "دهن نباتي": {"CP": 0.0, "DC": 0.0, "SE": 10.0, "NDF": 0.0, "ADF": 0.0, "EE": 99.0, "ASH": 0.0},
        "ليسيثين الصويا": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 95.0, "ASH": 0.5},
        "بروتين الصويا المركز": {"CP": 65.0, "DC": 0.90, "SE": 30.0, "NDF": 2.0, "ADF": 1.0, "EE": 1.0, "ASH": 5.5}
    }
}

# تسطيح المكتبة للوصول السريع
FLAT_FEED_DB = {}
for cat, items in BIG_FEEDS_LIBRARY.items():
    for name, data in items.items():
        FLAT_FEED_DB[name] = data
        # =====================================================================
# المعايير القياسية للعناصر الغذائية
# =====================================================================
STANDARD_VALUES = {
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
        "أمهار نامية": {"DP": 13.0, "SE": 64.0, "CP": 16.3},
        "فرسات مرضعات": {"DP": 14.0, "SE": 66.0, "CP": 17.5}
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
        "ناهي متقدم": {"DP": 16.0, "SE": 70.0, "CP": 20.0}
    },
    "أسماك": {
        "بادئ": {"DP": 32.0, "SE": 70.0, "CP": 40.0},
        "نمو": {"DP": 28.0, "SE": 68.0, "CP": 35.0},
        "تسمين": {"DP": 26.0, "SE": 66.0, "CP": 32.5}
    }
}

# =====================================================================
# معادلات NRC الإنتاجية المتقدمة
# =====================================================================
class AdvancedProductionEquations:
    """معادلات NRC 2000/2001 لحساب الاحتياجات الغذائية"""
    
    @staticmethod
    def milk_protein(milk_kg, milk_protein_pct=3.3):
        return (milk_kg * (milk_protein_pct / 100)) / 0.65
    
    @staticmethod
    def maintenance_protein(weight):
        return 2.5 * (weight ** 0.75)
    
    @staticmethod
    def metabolic_protein(weight):
        return 1.2 * (weight ** 0.75)
    
    @staticmethod
    def dairy_protein(weight, milk_kg, fat_pct=3.5):
        m = AdvancedProductionEquations.maintenance_protein(weight)
        meta = AdvancedProductionEquations.metabolic_protein(weight)
        p = AdvancedProductionEquations.milk_protein(milk_kg)
        total = m + meta + p
        return {
            'maintenance': m, 'metabolic': meta, 'production': p,
            'total': total,
            'dp_requirement': (total / (weight * 10)) * 100
        }
    
    @staticmethod
    def dairy_energy(weight, milk_kg, fat_pct=3.5):
        m = 0.08 * (weight ** 0.75)
        correction = 1 + 0.15 * (fat_pct - 3.5)
        p = 5.3 * milk_kg * correction
        total = m + p
        return {
            'maintenance_energy': m, 'production_energy': p,
            'total_energy': total, 'se_requirement': total * 10
        }
    
    @staticmethod
    def gain_protein(daily_gain_kg, protein_pct=18.0):
        return (daily_gain_kg * (protein_pct / 100)) / 0.65
    
    @staticmethod
    def gain_energy(daily_gain_kg, gain_energy_pct=5.0):
        return (daily_gain_kg * gain_energy_pct) / 0.70
    
    @staticmethod
    def fattening_protein(weight, daily_gain):
        m = 2.0 * (weight ** 0.75)
        meta = 1.0 * (weight ** 0.75)
        p = AdvancedProductionEquations.gain_protein(daily_gain)
        total = m + meta + p
        return {
            'maintenance': m, 'metabolic': meta, 'production': p,
            'total': total,
            'dp_requirement': (total / (weight * 8)) * 100
        }
    
    @staticmethod
    def fattening_energy(weight, daily_gain):
        m = 0.07 * (weight ** 0.75)
        p = AdvancedProductionEquations.gain_energy(daily_gain)
        total = m + p
        return {
            'maintenance_energy': m, 'production_energy': p,
            'total_energy': total, 'se_requirement': total * 10
        }

# =====================================================================
# نظام المختبر الذكي (OCR)
# =====================================================================
class SmartLabSystem:
    """تحليل صور تركيبات الأعلاف باستخدام OCR"""
    
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
            return None, "مكتبات OCR غير مثبتة"
        results = []
        try:
            if EASYOCR_AVAILABLE and self.reader:
                res = self.reader.readtext(np.array(image))
                for (bbox, text, prob) in res:
                    if prob > 0.3:
                        results.append(text)
            elif OCR_AVAILABLE:
                img = PILImage.open(image) if not isinstance(image, PILImage.Image) else image
                text = pytesseract.image_to_string(img, lang='ara+eng')
                results = text.split('\n')
            return self._parse(results), None
        except Exception as e:
            return None, f"خطأ: {str(e)}"
    
    def _parse(self, texts):
        data = {'sample_name': '', 'cp': None, 'dc': None, 'se': None,
                'ndf': None, 'adf': None, 'ee': None, 'ash': None, 'moisture': None}
        patterns = {
            'cp': [r'بروتين\s*خام\s*[:=]?\s*([\d.]+)', r'CP\s*[:=]?\s*([\d.]+)'],
            'dc': [r'معامل\s*الهضم\s*[:=]?\s*([\d.]+)', r'DC\s*[:=]?\s*([\d.]+)'],
            'se': [r'معادل\s*النشاء\s*[:=]?\s*([\d.]+)', r'SE\s*[:=]?\s*([\d.]+)'],
            'ndf': [r'NDF\s*[:=]?\s*([\d.]+)'],
            'adf': [r'ADF\s*[:=]?\s*([\d.]+)'],
            'ee': [r'دهن\s*خام\s*[:=]?\s*([\d.]+)', r'EE\s*[:=]?\s*([\d.]+)'],
            'ash': [r'رماد\s*[:=]?\s*([\d.]+)', r'ASH\s*[:=]?\s*([\d.]+)'],
            'moisture': [r'رطوبة\s*[:=]?\s*([\d.]+)']
        }
        for t in texts:
            t = t.strip()
            if 'اسم' in t and not data['sample_name']:
                parts = t.split(':')
                if len(parts) > 1:
                    data['sample_name'] = parts[1].strip()
            for key, plist in patterns.items():
                if data[key] is None:
                    for p in plist:
                        m = re.search(p, t, re.IGNORECASE)
                        if m:
                            try:
                                data[key] = float(m.group(1))
                                break
                            except Exception:
                                pass
        return data
    
    def save(self, data):
        rid = secrets.token_hex(8)
        try:
            self.db.insert('lab_results', {
                'result_id': rid,
                'sample_name': data.get('sample_name', ''),
                'animal_type': data.get('animal_type', ''),
                'stage': data.get('stage', ''),
                'cp': data.get('cp', 0.0),
                'dp': data.get('dp', 0.0),
                'se': data.get('se', 0.0),
                'ndf': data.get('ndf', 0.0),
                'adf': data.get('adf', 0.0),
                'ee': data.get('ee', 0.0),
                'ash': data.get('ash', 0.0),
                'moisture': data.get('moisture', 0.0),
                'notes': data.get('notes', ''),
                'performed_by': data.get('performed_by', ''),
                'result_date': datetime.now().isoformat()
            })
        except Exception:
            pass
        return rid

# =====================================================================
# مدير المخزون
# =====================================================================
class InventoryManager:
    @staticmethod
    def init():
        if "inventory" not in st.session_state:
            st.session_state["inventory"] = {}
            for cat in BIG_FEEDS_LIBRARY.values():
                for name in cat:
                    st.session_state["inventory"][name] = {
                        "quantity": 25.0,
                        "min_threshold": 5.0,
                        "unit": "طن",
                        "last_updated": datetime.now().isoformat()
                    }
    
    @staticmethod
    def check():
        warns = {}
        for item, data in st.session_state["inventory"].items():
            qty = data["quantity"] if isinstance(data, dict) else data
            thr = data.get("min_threshold", 5.0) if isinstance(data, dict) else 5.0
            if qty <= 0:
                warns[item] = "نفذ"
            elif qty < thr:
                warns[item] = "منخفض"
        return warns
    
    @staticmethod
    def summary():
        total_items = len(st.session_state["inventory"])
        total_qty = sum(
            d["quantity"] if isinstance(d, dict) else d
            for d in st.session_state["inventory"].values()
        )
        low = len(InventoryManager.check())
        return {"total": total_items, "qty": total_qty, "low": low}

# =====================================================================
# نظام مواقيت الصلاة
# =====================================================================
PRAYER_CITIES = {
    "مكة المكرمة": {"lat": 21.4225, "lng": 39.8262},
    "المدينة المنورة": {"lat": 24.4672, "lng": 39.6112},
    "الخرطوم": {"lat": 15.5007, "lng": 32.5599},
    "طرابلس": {"lat": 32.8872, "lng": 13.1913},
    "القاهرة": {"lat": 30.0444, "lng": 31.2357},
    "الرياض": {"lat": 24.7136, "lng": 46.6753},
    "دبي": {"lat": 25.2048, "lng": 55.2708},
    "بغداد": {"lat": 33.3152, "lng": 44.3661},
    "عمان": {"lat": 31.9539, "lng": 35.9106}
}

def get_prayer_times(city):
    """مواقيت تقديرية"""
    if city not in PRAYER_CITIES:
        return None
    return {
        "الفجر": "05:00", "الشروق": "06:30",
        "الظهر": "12:00", "العصر": "15:30",
        "المغرب": "18:00", "العشاء": "19:30"
    }

# =====================================================================
# نظام منبه الجرعات
# =====================================================================
class DoseReminderSystem:
    def __init__(self):
        if "dose_reminders" not in st.session_state:
            st.session_state["dose_reminders"] = []
        self.reminders = st.session_state["dose_reminders"]
    
    def add(self, animal, dtype, name, amount, unit, route, freq, start, notes=""):
        r = {
            'id': secrets.token_hex(8),
            'animal_type': animal,
            'dose_type': dtype,
            'dose_name': name,
            'dose_amount': amount,
            'dose_unit': unit,
            'administration_route': route,
            'frequency_days': freq,
            'start_date': start,
            'next_dose_date': (datetime.strptime(start, "%Y-%m-%d") + timedelta(days=freq)).isoformat(),
            'notes': notes,
            'active': True
        }
        self.reminders.append(r)
        st.session_state["dose_reminders"] = self.reminders
        return r
    
    def get_due(self):
        today = datetime.now().date()
        return [r for r in self.reminders 
                if r.get('active', True) 
                and datetime.fromisoformat(r['next_dose_date']).date() <= today]
    
    def complete(self, rid):
        for r in self.reminders:
            if r['id'] == rid:
                nd = datetime.fromisoformat(r['next_dose_date']).date()
                r['next_dose_date'] = (nd + timedelta(days=r['frequency_days'])).isoformat()
                st.session_state["dose_reminders"] = self.reminders
                return True
        return False
        # =====================================================================
# تحميل الخط العربي
# =====================================================================
@st.cache_resource
def ensure_arabic_font():
    font_path = "Amiri-Regular.ttf"
    if not os.path.exists(font_path):
        try:
            import requests
            url = "https://raw.githubusercontent.com/aliftype/amiri/master/fonts/Amiri-Regular.ttf"
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                with open(font_path, "wb") as f:
                    f.write(r.content)
        except Exception:
            pass
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('Amiri', font_path))
            return 'Amiri'
        except Exception:
            pass
    return 'Helvetica'

# =====================================================================
# مولد PDF الاحترافي
# =====================================================================
class PDFGenerator:
    def __init__(self):
        self.font = ensure_arabic_font()
    
    def _p(self, text, size=11, align=TA_RIGHT, color="#1a1a1a", bold=False):
        safe = arabic_processor.fix(str(text))
        return Paragraph(safe, ParagraphStyle(
            'p', fontName=self.font, fontSize=size, alignment=align,
            textColor=HexColor(color), spaceAfter=6, leading=size*1.5
        ))
    
    def _basmala_header(self, story):
        """البسملة والترويسة مع اسم المشرف"""
        story.append(self._p("بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ", 20, TA_CENTER, "#1b5e20"))
        story.append(Spacer(1, 8))
        story.append(self._p("🌾 تاور نولجي Tawornology العلمية", 18, TA_CENTER, "#1a237e"))
        story.append(self._p("للانتاج الحيواني وتركيب الاعلاف", 14, TA_CENTER, "#1565C0"))
        story.append(Spacer(1, 10))
        story.append(self._p(f"المشرف العام: {OWNER_NAME}", 13, TA_CENTER, "#c62828"))
        story.append(self._p(f"الصفة: {OWNER_TITLE}", 11, TA_CENTER, "#666666"))
        story.append(Spacer(1, 6))
        story.append(self._p(
            "🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله",
            10, TA_CENTER, "#777777"
        ))
        story.append(Spacer(1, 15))
        story.append(Paragraph("<hr/>", ParagraphStyle('hr')))
    
    def _signature_footer(self, story):
        """توقيع المشرف في النهاية"""
        story.append(Spacer(1, 30))
        story.append(self._p("مع خالص التحية والتقدير،", 11, TA_RIGHT))
        story.append(Spacer(1, 8))
        story.append(self._p(f"✍️ {OWNER_NAME}", 13, TA_RIGHT, "#1b5e20"))
        story.append(self._p(f"🎓 {OWNER_TITLE}", 11, TA_RIGHT, "#666666"))
        story.append(Spacer(1, 10))
        story.append(self._p(
            f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')} | ⏰ {datetime.now().strftime('%H:%M')}",
            9, TA_RIGHT, "#888"
        ))
        story.append(Spacer(1, 15))
        story.append(self._p(
            f"© 2026 تاور نولجي Tawornology العلمية - جميع الحقوق محفوظة",
            8, TA_CENTER, "#999"
        ))
    
    def formula_report(self, formula, target_dp, target_se, breed, stage,
                        cost, city, requester, standard=None, extra=None):
        """تقرير تركيبة علفية كامل"""
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                rightMargin=50, leftMargin=50,
                                topMargin=50, bottomMargin=50)
        story = []
        
        # الترويسة
        self._basmala_header(story)
        
        story.append(self._p("📄 تقرير تركيبة علفية معتمدة", 16, TA_CENTER, "#2e7d32"))
        story.append(Spacer(1, 10))
        
        # معلومات أساسية
        info = [
            ("الفصيل المستهدف", breed),
            ("المرحلة الإنتاجية", stage),
            ("الموقع الجغرافي", city),
            ("طالب العلف", requester or "غير محدد"),
            ("تاريخ الإصدار", datetime.now().strftime('%Y-%m-%d %H:%M'))
        ]
        for k, v in info:
            story.append(self._p(f"• {k}: {v}", 11))
        
        story.append(Spacer(1, 15))
        
        # جدول الملخص
        summary_data = [
            ["المعيار", "القيمة"],
            ["البروتين المهضوم (DP)", f"{target_dp:.2f}%"],
            ["معادل النشاء (SE)", f"{target_se:.2f} وحدة"],
            ["التكلفة للطن", f"${cost:.2f}"]
        ]
        t = Table([[arabic_processor.fix(c) for c in row] for row in summary_data],
                  colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#2e7d32')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f5f5f5')])
        ]))
        story.append(t)
        story.append(Spacer(1, 15))
        
        # جدول المكونات
        story.append(self._p("📋 المكونات المعتمدة لطن واحد:", 13, TA_RIGHT, "#2e7d32"))
        story.append(Spacer(1, 8))
        ing_data = [["المكون", "النسبة %", "كجم/طن"]]
        for ing, pct in sorted(formula.items(), key=lambda x: -x[1]):
            ing_data.append([ing, f"{pct:.2f}%", f"{pct*10:.1f}"])
        
        t2 = Table([[arabic_processor.fix(c) for c in row] for row in ing_data],
                   colWidths=[200, 150, 150])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f5f5f5')])
        ]))
        story.append(t2)
        story.append(Spacer(1, 15))
        
        # المقارنة مع المعايير
        if standard:
            story.append(self._p("📊 المقارنة مع المعايير القياسية:", 13, TA_RIGHT, "#1565C0"))
            story.append(Spacer(1, 8))
            comp_data = [["المقياس", "المحسوب", "القياسي", "الانحراف %", "التقييم"]]
            
            if 'DP' in standard:
                dev = ((target_dp - standard['DP']) / standard['DP']) * 100
                grade = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                comp_data.append(["DP", f"{target_dp:.2f}%",
                                   f"{standard['DP']:.2f}%", f"{dev:.1f}%", grade])
            
            if 'SE' in standard:
                dev = ((target_se - standard['SE']) / standard['SE']) * 100
                grade = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                comp_data.append(["SE", f"{target_se:.2f}",
                                   f"{standard['SE']:.2f}", f"{dev:.1f}%", grade])
            
            if 'CP' in standard:
                cp_calc = target_dp / 0.80
                dev = ((cp_calc - standard['CP']) / standard['CP']) * 100
                grade = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                comp_data.append(["CP", f"{cp_calc:.2f}%",
                                   f"{standard['CP']:.2f}%", f"{dev:.1f}%", grade])
            
            t3 = Table([[arabic_processor.fix(c) for c in row] for row in comp_data],
                       colWidths=[90, 100, 100, 100, 60])
            t3.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f5f5f5')])
            ]))
            story.append(t3)
            story.append(Spacer(1, 15))
            
            # الرسم البياني
            try:
                fig, ax = plt.subplots(figsize=(6, 3))
                categories = []
                calculated = []
                standard_vals = []
                if 'DP' in standard:
                    categories.append('DP')
                    calculated.append(target_dp)
                    standard_vals.append(standard['DP'])
                if 'SE' in standard:
                    categories.append('SE')
                    calculated.append(target_se)
                    standard_vals.append(standard['SE'])
                if 'CP' in standard:
                    categories.append('CP')
                    calculated.append(target_dp/0.80)
                    standard_vals.append(standard['CP'])
                x = np.arange(len(categories))
                w = 0.35
                ax.bar(x - w/2, calculated, w, label='المحسوب', color='#2e7d32')
                ax.bar(x + w/2, standard_vals, w, label='القياسي', color='#1565C0')
                ax.set_xticks(x)
                ax.set_xticklabels(categories)
                ax.legend(loc='best')
                ax.set_title('مقارنة التركيبة بالمعايير القياسية')
                ax.grid(axis='y', linestyle='--', alpha=0.5)
                img_buf = io.BytesIO()
                plt.tight_layout()
                plt.savefig(img_buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                img_buf.seek(0)
                story.append(Image(img_buf, width=450, height=230))
            except Exception:
                pass
        
        # معلومات إضافية
        if extra:
            story.append(Spacer(1, 10))
            story.append(self._p("📌 معلومات إضافية:", 12, TA_RIGHT, "#1565C0"))
            for k, v in extra.items():
                if v:
                    story.append(self._p(f"• {k}: {v}", 10))
        
        # التوقيع
        self._signature_footer(story)
        
        doc.build(story)
        buf.seek(0)
        return buf.getvalue()
    
    def lab_report(self, results, animal, stage, standard=None,
                    evaluation=None, components=None):
        """تقرير المختبر مع الرسم البياني"""
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                rightMargin=40, leftMargin=40,
                                topMargin=40, bottomMargin=40)
        story = []
        
        self._basmala_header(story)
        
        story.append(self._p("🔬 تقرير التحليل المخبري المتقدم", 16, TA_CENTER, "#1565C0"))
        story.append(Spacer(1, 10))
        
        story.append(self._p(f"الفصيل: {animal} | المرحلة: {stage}", 11))
        story.append(self._p(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 11))
        story.append(Spacer(1, 12))
        
        # المكونات
        if components:
            story.append(self._p("📦 المكونات المدخلة:", 13, TA_RIGHT, "#2e7d32"))
            story.append(Spacer(1, 8))
            total = sum(components.values())
            comp_data = [["المادة", "الوزن (كجم)", "النسبة %"]]
            for name, weight in components.items():
                if weight > 0:
                    pct = (weight / total) * 100
                    comp_data.append([name, f"{weight:.1f}", f"{pct:.2f}"])
            t = Table([[arabic_processor.fix(c) for c in row] for row in comp_data],
                      colWidths=[200, 120, 120])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd'))
            ]))
            story.append(t)
            story.append(Spacer(1, 12))
        
        # النتائج
        story.append(self._p("📊 النتائج المحسوبة:", 13, TA_RIGHT, "#1565C0"))
        story.append(Spacer(1, 8))
        res_data = [["العنصر", "القيمة"]]
        for key, label in [('cp', 'بروتين خام (CP)'),
                            ('dp', 'بروتين مهضوم (DP)'),
                            ('se', 'معادل النشاء (SE)')]:
            if key in results and results[key] is not None:
                unit = '%' if key in ['cp', 'dp'] else 'وحدة'
                res_data.append([label, f"{results[key]:.2f} {unit}"])
        
        t2 = Table([[arabic_processor.fix(c) for c in row] for row in res_data],
                   colWidths=[250, 250])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565C0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#1565C0'))
        ]))
        story.append(t2)
        story.append(Spacer(1, 12))
        
        # المقارنة
        if standard:
            story.append(self._p("📏 المقارنة مع المعايير القياسية:", 13, TA_RIGHT, "#2e7d32"))
            story.append(Spacer(1, 8))
            comp_data = [["المقياس", "المحسوب", "القياسي", "الانحراف %", "التقييم"]]
            for key, std_key in [('dp', 'DP'), ('se', 'SE'), ('cp', 'CP')]:
                if key in results and std_key in standard:
                    calc = results[key]
                    std_v = standard[std_key]
                    dev = ((calc - std_v) / std_v) * 100 if std_v > 0 else 0
                    grade = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                    comp_data.append([std_key, f"{calc:.2f}", f"{std_v:.2f}",
                                       f"{dev:.1f}%", grade])
            
            t3 = Table([[arabic_processor.fix(c) for c in row] for row in comp_data],
                       colWidths=[80, 100, 100, 100, 70])
            t3.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f5f5f5')])
            ]))
            story.append(t3)
            story.append(Spacer(1, 15))
            
            # الرسم البياني - مهم جداً
            try:
                fig, ax = plt.subplots(figsize=(6.5, 3.5))
                cats = []
                calc_vals = []
                std_vals = []
                for k, sk in [('dp', 'DP'), ('se', 'SE'), ('cp', 'CP')]:
                    if k in results and sk in standard:
                        cats.append(sk)
                        calc_vals.append(results[k])
                        std_vals.append(standard[sk])
                
                x = np.arange(len(cats))
                w = 0.35
                bars1 = ax.bar(x - w/2, calc_vals, w, label='المحسوب',
                                color='#2e7d32', edgecolor='#1b5e20')
                bars2 = ax.bar(x + w/2, std_vals, w, label='القياسي',
                                color='#1565C0', edgecolor='#0d47a1')
                
                # إضافة القيم على الأعمدة
                for bar in bars1:
                    h = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2, h,
                            f'{h:.1f}', ha='center', va='bottom',
                            fontsize=9, fontweight='bold')
                for bar in bars2:
                    h = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2, h,
                            f'{h:.1f}', ha='center', va='bottom',
                            fontsize=9, fontweight='bold')
                
                ax.set_xticks(x)
                ax.set_xticklabels(cats)
                ax.set_title('مقارنة النتائج المحسوبة مع المعايير القياسية',
                              fontsize=12, fontweight='bold')
                ax.legend(loc='best')
                ax.grid(axis='y', linestyle='--', alpha=0.4)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                
                img_buf = io.BytesIO()
                plt.tight_layout()
                plt.savefig(img_buf, format='png', dpi=120, bbox_inches='tight',
                            facecolor='white')
                plt.close()
                img_buf.seek(0)
                story.append(Image(img_buf, width=480, height=250))
            except Exception:
                pass
            
            # التقييم
            if evaluation:
                story.append(Spacer(1, 10))
                story.append(self._p("⭐ التقييم النهائي:", 13, TA_RIGHT, "#1b5e20"))
                story.append(Spacer(1, 6))
                for k, v in evaluation.items():
                    story.append(self._p(f"• {k}: {v}", 11))
        
        # التوصيات
        story.append(Spacer(1, 12))
        story.append(self._p("📌 التوصيات الفنية:", 13, TA_RIGHT, "#e65100"))
        recs = [
            "• يوصى بإعادة التحليل بعد أي تعديل على الخلطة.",
            "• يجب مراقبة جودة المواد الخام بشكل دوري.",
            "• يوصى بالتواصل مع أخصائي التغذية لتعديل الخلطة حسب النتائج.",
            "• يُخزَّن العلف في مكان جاف بعيداً عن الرطوبة."
        ]
        for r in recs:
            story.append(self._p(r, 10))
        
        self._signature_footer(story)
        
        doc.build(story)
        buf.seek(0)
        return buf.getvalue()
    
    def milk_replacer_report(self, formula, animal, age, instructions):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                rightMargin=50, leftMargin=50,
                                topMargin=50, bottomMargin=50)
        story = []
        
        self._basmala_header(story)
        
        story.append(self._p("🍼 تقرير تركيب بديل الحليب", 16, TA_CENTER, "#1b5e20"))
        story.append(Spacer(1, 10))
        story.append(self._p(f"نوع الحيوان: {animal}", 11))
        story.append(self._p(f"العمر: {age} يوم", 11))
        story.append(self._p(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 11))
        story.append(Spacer(1, 12))
        
        story.append(self._p("📋 مكونات بديل الحليب:", 13, TA_RIGHT, "#2e7d32"))
        story.append(Spacer(1, 8))
        
        ing_data = [["المكون", "النسبة %", "جم/كجم"]]
        for ing, pct in formula.items():
            ing_data.append([ing, f"{pct:.2f}%", f"{pct*10:.1f}"])
        
        t = Table([[arabic_processor.fix(c) for c in row] for row in ing_data],
                  colWidths=[200, 130, 130])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd'))
        ]))
        story.append(t)
        story.append(Spacer(1, 12))
        
        story.append(self._p("📌 تعليمات التقديم:", 13, TA_RIGHT, "#e65100"))
        for line in instructions.split('\n'):
            if line.strip():
                story.append(self._p(f"• {line.strip()}", 10))
        
        self._signature_footer(story)
        
        doc.build(story)
        buf.seek(0)
        return buf.getvalue()

# نسخة عالمية
pdf_gen = PDFGenerator()

# =====================================================================
# CSS التصميم الأنيق
# =====================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');

* { font-family: 'Cairo', 'Tajawal', sans-serif; }

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #e8f5e9 100%);
    background-attachment: fixed;
}
.stApp { background: transparent; }

.main-box {
    background: rgba(255, 255, 255, 0.97);
    padding: 30px;
    border-radius: 22px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
    backdrop-filter: blur(12px);
    margin-bottom: 30px;
    border: 1px solid rgba(46, 125, 50, 0.1);
}

.basmala-header {
    text-align: center;
    padding: 20px 0;
    background: linear-gradient(135deg, #1b5e20, #2e7d32, #1b5e20);
    border-radius: 18px;
    margin-bottom: 25px;
    box-shadow: 0 8px 30px rgba(27, 94, 32, 0.3);
    position: relative;
    overflow: hidden;
}
.basmala-header::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 30% 20%, rgba(212, 175, 55, 0.2), transparent 60%);
    pointer-events: none;
}
.basmala-header h1 {
    color: #ffd700 !important;
    font-family: 'Amiri', serif !important;
    font-size: 2.2rem !important;
    margin: 5px 0 !important;
    text-shadow: 0 3px 12px rgba(0,0,0,0.4);
    font-weight: 700;
}
.basmala-header h2 {
    color: #ffffff !important;
    font-size: 1.4rem !important;
    margin: 5px 0 !important;
}
.basmala-header .owner-name {
    color: #ffd700 !important;
    font-size: 1.5rem !important;
    font-weight: 900;
    text-shadow: 0 2px 8px rgba(0,0,0,0.5);
    margin-top: 10px;
}
.basmala-header .owner-title {
    color: #e0e0e0 !important;
    font-size: 1rem !important;
    letter-spacing: 1px;
    margin-bottom: 8px;
}
.basmala-header .dedication {
    color: #c8e6c9 !important;
    font-size: 0.9rem !important;
    font-style: italic;
    padding-top: 8px;
    border-top: 1px solid rgba(255,255,255,0.15);
    margin-top: 10px;
}

.section-title {
    color: #1b5e20 !important;
    border-right: 6px solid #2e7d32;
    padding-right: 18px;
    text-align: right;
    font-size: 1.6rem;
    font-weight: 700;
    margin: 25px 0 20px 0;
    background: linear-gradient(to left, rgba(46,125,50,0.12), transparent);
    padding: 12px 20px;
    border-radius: 12px;
}

.formula-item {
    background: linear-gradient(135deg, #ffffff, #e8f5e9);
    padding: 14px 20px;
    border-radius: 12px;
    margin-bottom: 8px;
    font-weight: 600;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    box-shadow: 0 3px 12px rgba(0,0,0,0.06);
    transition: all 0.3s ease;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.formula-item:hover {
    transform: translateX(-6px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
}

.profile-img-style {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #d4af37;
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    transition: transform 0.4s ease;
    display: block;
    margin: 0 auto;
}
.profile-img-style:hover { transform: scale(1.06) rotate(3deg); }

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 5px 25px rgba(0,0,0,0.08);
    text-align: center;
    transition: all 0.3s ease;
    border: 1px solid rgba(46, 125, 50, 0.1);
}
.metric-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.15);
}
.metric-card .number {
    font-size: 2rem;
    font-weight: 900;
    color: #1b5e20;
    margin: 5px 0;
}
.metric-card .label {
    font-size: 0.9rem;
    color: #666;
    font-weight: 600;
}

.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 18px;
    border-radius: 12px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 15px;
    direction: rtl;
    text-align: right;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.warning-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 14px;
    border-radius: 12px;
    border-right: 5px solid #f57c00;
    margin-bottom: 12px;
    direction: rtl;
    text-align: right;
    color: #e65100 !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.success-card {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 14px;
    border-radius: 12px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 12px;
    direction: rtl;
    text-align: right;
    color: #1b5e20 !important;
}

.info-card {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 14px;
    border-radius: 12px;
    border-right: 5px solid #1565C0;
    margin-bottom: 12px;
    direction: rtl;
    text-align: right;
    color: #0d47a1 !important;
}

.stock-critical {
    background: linear-gradient(135deg, #ffebee, #ffcdd2);
    padding: 6px 14px;
    border-radius: 22px;
    color: #c62828;
    font-weight: 700;
    display: inline-block;
}
.stock-normal {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 6px 14px;
    border-radius: 22px;
    color: #2e7d32;
    font-weight: 700;
    display: inline-block;
}
.stock-warning {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 6px 14px;
    border-radius: 22px;
    color: #e65100;
    font-weight: 700;
    display: inline-block;
}

.mini-signature {
    position: fixed;
    left: 20px;
    bottom: 20px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important;
    padding: 8px 18px;
    font-size: 0.85rem;
    border-radius: 22px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    z-index: 9999;
    direction: rtl;
    backdrop-filter: blur(5px);
    font-weight: 600;
}

.dua-bar {
    background: linear-gradient(135deg, #0d1b2a 0%, #1a237e 40%, #4a148c 70%, #0d1b2a 100%);
    padding: 18px 0;
    border-radius: 20px;
    margin-bottom: 20px;
    overflow: hidden;
    border: 2px solid #ffd700;
    box-shadow: 0 8px 40px rgba(255, 215, 0, 0.35);
    direction: rtl;
    position: relative;
}
@keyframes scrollDua {
    0% { transform: translateX(100%); opacity: 0; }
    10% { transform: translateX(0%); opacity: 1; }
    90% { transform: translateX(0%); opacity: 1; }
    100% { transform: translateX(-100%); opacity: 0; }
}
.dua-text {
    display: inline-block;
    white-space: nowrap;
    animation: scrollDua 22s ease-in-out infinite;
    font-size: 1.3rem;
    font-weight: 700;
    color: #ffd700;
    padding: 0 30px;
    letter-spacing: 1px;
    text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
}
.dua-text .name {
    color: #ffab40;
    background: rgba(255, 215, 0, 0.15);
    padding: 0 8px;
    border-radius: 6px;
}

.book-chapter {
    background: linear-gradient(135deg, #1a237e, #283593);
    color: white !important;
    padding: 14px 20px;
    border-radius: 10px;
    font-weight: bold;
    margin-top: 20px;
    font-size: 1.15rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.book-chapter * { color: white !important; }

.book-body {
    padding: 18px 22px;
    font-size: 1.05rem;
    line-height: 1.8;
    color: #2c3e50 !important;
    border-right: 4px solid #3498db;
    margin-bottom: 15px;
    background: linear-gradient(to right, #f8f9fa, #ffffff);
    border-radius: 0 10px 10px 0;
}

.book-body * { color: #2c3e50 !important; }

.measurement-card {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 20px;
    border-radius: 14px;
    border-right: 5px solid #1565C0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    margin-bottom: 15px;
}

.comparison-good {
    background: #e8f5e9;
    padding: 3px 10px;
    border-radius: 5px;
    color: #2e7d32;
    font-weight: bold;
}
.comparison-warning {
    background: #fff3e0;
    padding: 3px 10px;
    border-radius: 5px;
    color: #e65100;
    font-weight: bold;
}
.comparison-excellent {
    background: #e3f2fd;
    padding: 3px 10px;
    border-radius: 5px;
    color: #0d47a1;
    font-weight: bold;
}

.stButton > button {
    background: linear-gradient(135deg, #2e7d32, #1b5e20) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 10px 20px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(46, 125, 50, 0.4) !important;
    background: linear-gradient(135deg, #388e3c, #2e7d32) !important;
    color: white !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #1565C0, #0d47a1) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 15px rgba(21, 101, 192, 0.3) !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: rgba(255,255,255,0.5);
    padding: 8px;
    border-radius: 14px;
    flex-wrap: wrap;
}
.stTabs [data-baseweb="tab"] {
    background: white !important;
    border-radius: 10px !important;
    padding: 8px 16px !important;
    font-weight: 600 !important;
    color: #1a237e !important;
    border: 1px solid rgba(46, 125, 50, 0.15) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #2e7d32, #1b5e20) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3) !important;
}

h1, h2, h3, h4, h5 { color: #1b5e20 !important; }

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > select,
.stTextArea textarea {
    border-radius: 10px !important;
    border: 1px solid rgba(46, 125, 50, 0.2) !important;
}

/* تحسين الموبايل */
@media (max-width: 768px) {
    .main-box { padding: 15px; }
    .basmala-header h1 { font-size: 1.4rem !important; }
    .basmala-header .owner-name { font-size: 1.1rem !important; }
    .section-title { font-size: 1.2rem; }
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# شريط الدعاء المتحرك
# =====================================================================
def render_dua_bar():
    st.markdown("""
    <div class="dua-bar">
        <div class="dua-text">
            ✦ ❤️ اللهم اغفر لـ <span class="name">إسماعيل تاور</span> و <span class="name">ابتسام</span> وارحمهما وأدخلهما فسيح جناتك ❤️ ✦
            ❤️ اللهم اجعل قبرهما روضة من رياض الجنة ❤️
            ❤️ اللهم ارحم موتانا وموتى المسلمين ❤️
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# الترويسة الكاملة (البسملة + اسم المشرف)
# =====================================================================
def render_header():
    st.markdown(f"""
    <div class="basmala-header">
        <h1>بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</h1>
        <h2>🌾 تاور نولجي Tawornology العلمية 🌾</h2>
        <div style="color:#ffffff; font-size:1rem; margin:5px 0;">
            للانتاج الحيواني وتركيب الاعلاف
        </div>
        <div style="color:#ffffff; font-size:0.9rem; margin-top:8px;">
            🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله 🕊️
        </div>
        <div class="owner-name">✍️ {OWNER_NAME}</div>
        <div class="owner-title">🎓 {OWNER_TITLE}</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_img, col_info = st.columns([0.25, 0.75])
    with col_img:
        if img_base64:
            st.markdown(
                f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div style="width:150px;height:150px;border-radius:50%;'
                'background:linear-gradient(135deg,#2e7d32,#1b5e20);'
                'color:white;display:flex;align-items:center;'
                'justify-content:center;font-size:3rem;margin:0 auto;'
                'border:4px solid #d4af37;">🌾</div>',
                unsafe_allow_html=True
            )
    with col_info:
        st.markdown(f"""
        <div class="info-card" style="padding:20px;">
            <h3 style="margin-top:0; color:#1b5e20;">👨‍💻 {OWNER_NAME}</h3>
            <p style="font-size:1.05rem; color:#1565C0; font-weight:600; margin:5px 0;">
                🎓 {OWNER_TITLE}
            </p>
            <p style="color:#555; line-height:1.7; margin-top:10px;">
                منصة علمية متكاملة لتركيب الأعلاف بأقل تكلفة مع تحقيق التوازن 
                الغذائي الدقيق، تعتمد على البروتين المهضوم (DP) ومعادل النشاء (SE)، 
                وتضم مختبراً ذكياً، وإدارة متكاملة للمزارع، ومعادلات NRC الإنتاجية.
            </p>
        </div>
        """, unsafe_allow_html=True)

# =====================================================================
# شاشة الدخول (كلمة مرور واحدة فقط)
# =====================================================================
if "approved" not in st.session_state:
    st.session_state["approved"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "login_attempts" not in st.session_state:
    st.session_state["login_attempts"] = 0
if "lockout_time" not in st.session_state:
    st.session_state["lockout_time"] = None

render_dua_bar()

if not st.session_state["approved"]:
    MAX_ATTEMPTS = 5
    LOCKOUT_SECONDS = 300
    
    if st.session_state["login_attempts"] >= MAX_ATTEMPTS:
        if st.session_state["lockout_time"]:
            elapsed = (datetime.now() - st.session_state["lockout_time"]).seconds
            if elapsed < LOCKOUT_SECONDS:
                st.markdown('<div class="main-box" style="max-width:520px;margin:80px auto;direction:rtl;">', unsafe_allow_html=True)
                st.error(f"🔒 تم قفل النظام مؤقتاً. المتبقي: {LOCKOUT_SECONDS - elapsed} ثانية")
                st.markdown('</div>', unsafe_allow_html=True)
                st.stop()
            else:
                st.session_state["login_attempts"] = 0
    
    st.markdown('<div class="main-box" style="max-width:560px;margin:60px auto;direction:rtl;">', unsafe_allow_html=True)
    
    # الترويسة داخل شاشة الدخول
    st.markdown(f"""
    <div style="text-align:center; padding:20px 0;">
        <h2 style="color:#1b5e20; font-family:'Amiri',serif; font-size:1.8rem;">
            بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ
        </h2>
        <h3 style="color:#1a237e; margin:5px 0;">🌾 تاور نولجي Tawornology العلمية</h3>
        <p style="color:#1565C0; font-size:1rem;">للانتاج الحيواني وتركيب الاعلاف</p>
        <p style="color:#c62828; font-weight:700; font-size:1.1rem; margin-top:10px;">
            {OWNER_NAME}
        </p>
        <p style="color:#666; font-size:0.9rem;">{OWNER_TITLE}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if img_base64:
        st.markdown(
            f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style" style="margin:10px auto;">',
            unsafe_allow_html=True
        )
    
    st.markdown("<hr style='border-top:2px solid #2e7d32; margin:20px 0;'>", unsafe_allow_html=True)
    
    # خيارات الدخول
    login_mode = st.radio(
        "🔐 اختر طريقة الدخول:",
        ["👤 دخول كزائر", "🔑 دخول المالك"],
        horizontal=True,
        key="login_mode"
    )
    
    if login_mode == "👤 دخول كزائر":
        st.info("""
        **🆓 الدخول كزائر يمنحك:**
        - ✅ استخدام محرك تركيب الأعلاف
        - ✅ استخدام المختبر الذكي
        - ✅ الاطلاع على المراجع العلمية
        - ✅ تحميل التقارير PDF
        
        **❌ مقيّد عن:**
        - إدارة المزارع المتقدمة
        - تعديل الأسعار والمخزون
        - الفواتير والتقارير الإدارية
        """)
        
        if st.button("🚪 دخول كزائر", type="primary", use_container_width=True):
            st.session_state["approved"] = True
            st.session_state["user_role"] = "public"
            st.session_state["login_attempts"] = 0
            voice_guide("أهلاً بك زائراً في منصة تاور نولجي العلمية.")
            st.rerun()
    
    else:
        st.markdown("""
        <div style="background:#fff3e0; padding:12px; border-radius:10px;
                    border-right:4px solid #f57c00; direction:rtl; margin-bottom:15px;">
            <b style="color:#e65100;">⚠️ ملاحظة:</b>
            <span style="color:#555;">هذه الصفحة مخصصة للمالك فقط - أي شخص آخر يستخدم زر "دخول كزائر".</span>
        </div>
        """, unsafe_allow_html=True)
        
        pwd = st.text_input("🔑 كلمة مرور المالك:", type="password", key="owner_pwd")
        
        col_login, col_clear = st.columns(2)
        with col_login:
            if st.button("🔓 دخول", type="primary", use_container_width=True):
                if pwd == OWNER_PASSWORD:
                    st.session_state["approved"] = True
                    st.session_state["user_role"] = "owner"
                    st.session_state["login_attempts"] = 0
                    st.session_state["lockout_time"] = None
                    voice_guide(f"مرحباً بك {OWNER_NAME} في منصة تاور نولجي العلمية.")
                    st.rerun()
                else:
                    st.session_state["login_attempts"] += 1
                    st.session_state["lockout_time"] = datetime.now()
                    remaining = MAX_ATTEMPTS - st.session_state["login_attempts"]
                    if remaining > 0:
                        st.error(f"❌ كلمة المرور غير صحيحة! المتبقي: {remaining} محاولات")
                    else:
                        st.error("🔒 تم قفل النظام لمدة 5 دقائق")
                    st.rerun()
        with col_clear:
            if st.button("🔄 مسح", use_container_width=True):
                st.rerun()
    
    st.markdown(f"""
    <div style="text-align:center; margin-top:20px; color:#999; font-size:0.85rem;">
        <p>🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b> - رحمهما الله</p>
        <p style="color:#b39ddb; font-size:0.8rem;">اللهم اجعل قبرهما روضة من رياض الجنة</p>
        <p style="margin-top:15px; color:#bbb; font-size:0.75rem;">
            © 2026 تاور نولجي Tawornology العلمية
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()
    # =====================================================================
# تهيئة حالة الجلسة
# =====================================================================
def init_session_defaults():
    defaults = {
        "inventory": {},
        "farms_db": [],
        "dose_reminders": [],
        "milk_replacers": [],
        "active_formula": {},
        "active_cp_tag": 12.0,
        "active_se_tag": 65.0,
        "active_breed_tag": "سلالة عامة",
        "active_stage_title": "إنتاج عام",
        "computed_ton_cost": 280.0,
        "lab_sample": None,
        "lab_result": None,
        "ocr_result": {},
        "daily_production_log": [],
        "saved_formulas": [],
        "email_pwd_input": None,
        "need_email_pwd": False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_defaults()
InventoryManager.init()

# قواعد البيانات
db = DatabaseManager()
farm_mgr = FarmManager()

# بيانات افتراضية
if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين ($)": 1350.0,
        "أبقار كنانة محلية ($)": 900.0,
        "ضأن وستيرلنغ ($)": 180.0,
        "ماعز نوبي ($)": 130.0,
        "خيول عربية أصيلة ($)": 4500.0,
        "إبل عربية ($)": 2500.0,
        "كتكوت لاحم ($)": 0.65
    }

if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري ($)": 7.50,
        "كيلو لحم ضأن ($)": 9.00,
        "كيلو لحم دجاج ($)": 3.80,
        "طبق بيض 30 بيضة ($)": 4.20,
        "لتر حليب خام ($)": 0.90,
        "لتر حليب إبل ($)": 1.50
    }

if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = (
        "• [توجيه الاختصاصي م. عبد القادر إسماعيل تاور]: "
        "يرجى من جميع الزملاء إضافة تعليقاتهم وملاحظاتهم الفنية هنا.\n"
    )

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG", "name": "جنيه سوداني"},
    "ليبيا": {"rate": 4.80, "sym": "LYD", "name": "دينار ليبي"},
    "مصر": {"rate": 48.0, "sym": "EGP", "name": "جنيه مصري"},
    "دولار أمريكي": {"rate": 1.0, "sym": "USD", "name": "دولار أمريكي"}
}

ANIMAL_IMAGES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "إبل": "https://images.unsplash.com/photo-1502175353174-a7a70e73b362?q=80&w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600"
}

# =====================================================================
# الترويسة الرئيسية بعد الدخول
# =====================================================================
render_dua_bar()
render_header()

st.markdown("<hr style='border-top:3px solid #2e7d32; margin:20px 0;'>", unsafe_allow_html=True)

# شريط حالة المستخدم
col_user, col_logout = st.columns([0.75, 0.25])
with col_user:
    role_label = "👑 المالك" if st.session_state["user_role"] == "owner" else "👤 زائر"
    role_color = "#1b5e20" if st.session_state["user_role"] == "owner" else "#1565C0"
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#f5f5f5,#e0e0e0);
                padding:12px; border-radius:12px; direction:rtl;
                border-right:4px solid {role_color};">
        <b style="color:{role_color};">{role_label}</b>
        <span style="color:#555; margin-right:15px;">
            | آخر دخول: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </span>
    </div>
    """, unsafe_allow_html=True)
with col_logout:
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k not in ["inventory", "global_livestock_prices",
                         "global_products_prices", "shared_comments"]:
                del st.session_state[k]
        st.rerun()

st.markdown("---")

# =====================================================================
# لوحة الإحصائيات السريعة
# =====================================================================
st.markdown("### 📊 لوحة التحكم السريعة")
col_s1, col_s2, col_s3, col_s4 = st.columns(4)

summary = InventoryManager.summary()
with col_s1:
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size:2rem;">🏭</div>
        <div class="number">{summary['total']}</div>
        <div class="label">إجمالي المواد</div>
    </div>
    """, unsafe_allow_html=True)
with col_s2:
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size:2rem;">⚖️</div>
        <div class="number">{summary['qty']:.1f}</div>
        <div class="label">المخزون (طن)</div>
    </div>
    """, unsafe_allow_html=True)
with col_s3:
    color = "#c62828" if summary['low'] > 5 else ("#e65100" if summary['low'] > 0 else "#2e7d32")
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size:2rem;">⚠️</div>
        <div class="number" style="color:{color};">{summary['low']}</div>
        <div class="label">مواد منخفضة</div>
    </div>
    """, unsafe_allow_html=True)
with col_s4:
    farms_count = len(farm_mgr.get_farms())
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size:2rem;">🐔</div>
        <div class="number">{farms_count}</div>
        <div class="label">مزارع مسجلة</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# =====================================================================
# زر الشرح الصوتي
# =====================================================================
col_v1, col_v2, col_v3 = st.columns(3)
with col_v1:
    if st.button("🔊 شرح صوتي كامل للمنصة", use_container_width=True):
        voice_guide_sequential([
            "مرحباً بك في منصة تاور نولجي العلمية.",
            "هذه المنصة متخصصة في الانتاج الحيواني وتركيب الاعلاف.",
            "تحتوي على 16 قسماً رئيسياً:",
            "القطاع الحيواني لتركيب الأعلاف لثمانية أنواع من الحيوانات.",
            "المختبر الذكي لتحليل صور الأعلاف.",
            "إدارة المزارع ومتابعة الدورات.",
            "بدائل الحليب لرضاعة الصغار.",
            "مواقيت الصلاة.",
            "منبه الجرعات.",
            "بورصة الأسعار.",
            "المستودعات.",
            "الفواتير.",
            "الإنتاج اليومي.",
            "التقارير.",
            "التنبيهات.",
            "المراجع العلمية.",
            "المساعدة الذكية.",
            "دليل المستخدم.",
            "نسأل الله التوفيق."
        ])
with col_v2:
    if st.button("🕊️ استمع للدعاء", use_container_width=True):
        voice_guide_sequential([
            "اللهم اغفر لإسماعيل تاور وابتسام،",
            "وارحمهما وأدخلهما فسيح جناتك."
        ])
with col_v3:
    if st.button("ℹ️ اختبار الصوت", use_container_width=True):
        voice_guide("بسم الله الرحمن الرحيم. هذا اختبار للنظام الصوتي.")

st.markdown("---")

# =====================================================================
# تحديد التبويبات حسب الصلاحية
# =====================================================================
is_owner = st.session_state["user_role"] == "owner"

if is_owner:
    tab_titles = [
        "🐾 القطاع الحيواني",
        "🔬 المختبر الذكي",
        "🧮 معادلات NRC",
        "🐔 إدارة المزارع",
        "🍼 بدائل الحليب",
        "🕌 مواقيت الصلاة",
        "💊 منبه الجرعات",
        "📊 بورصة الأسعار",
        "🏭 المستودعات",
        "🧾 الفواتير",
        "📈 الإنتاج اليومي",
        "📊 التقارير",
        "🔔 التنبيهات",
        "💬 التعليقات",
        "📚 المراجع العلمية",
        "💡 المساعدة",
        "📖 دليل المستخدم",
        "📧 إرسال الكود"
    ]
else:
    tab_titles = [
        "🐾 القطاع الحيواني",
        "🔬 المختبر الذكي",
        "🧮 معادلات NRC",
        "🍼 بدائل الحليب",
        "🕌 مواقيت الصلاة",
        "💊 منبه الجرعات",
        "📊 بورصة الأسعار",
        "📚 المراجع العلمية",
        "💡 المساعدة",
        "📖 دليل المستخدم"
    ]

tabs = st.tabs(tab_titles)

# =====================================================================
# دالة دليل التبويب
# =====================================================================
def guide_section(name, text):
    with st.expander(f"📘 دليل استخدام {name}", expanded=False):
        st.markdown(f"""
        <div style="background:#f0f8ff; padding:14px; border-radius:10px;
                    direction:rtl; border-right:4px solid #1565C0;">
            {text}
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🔊 تشغيل الدليل صوتياً", key=f"voice_{name}"):
            voice_guide(text)

# =====================================================================
# دالة تركيب العلف الرئيسية
# =====================================================================
def render_formulation(animal_key, display_name, icon, breeds, stages,
                        default_dp, default_se, img_key, has_measurements=True):
    
    st.markdown(f'<div class="section-title">{icon} {display_name} - تركيب العلف</div>',
                unsafe_allow_html=True)
    
    # اسم طالب العلف
    requester = st.text_input(
        "👤 اسم طالب العلف (المربي / المزرعة):",
        placeholder="أدخل اسم المربي أو المزرعة",
        key=f"{animal_key}_requester"
    )
    
    col_measure, col_settings = st.columns([0.4, 0.6])
    
    with col_measure:
        if has_measurements:
            st.markdown('<div class="measurement-card">', unsafe_allow_html=True)
            st.markdown("#### 📏 شريط القياس الحيوي")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                girth = st.number_input("محيط الصدر (سم)", 20.0, 300.0,
                                        150.0 if animal_key in ["cattle", "horse", "camel"] else 75.0,
                                        key=f"{animal_key}_girth")
            with c2:
                length = st.number_input("طول الجسم (سم)", 20.0, 300.0,
                                          130.0 if animal_key in ["cattle", "horse", "camel"] else 65.0,
                                          key=f"{animal_key}_length")
            with c3:
                age_m = st.number_input("العمر (شهر)", 1, 120, 12,
                                         key=f"{animal_key}_age_m")
            
            weight_factors = {
                "cattle": 10838, "sheep": 15500, "goat": 15000,
                "horse": 11877, "camel": 13000
            }
            feed_factors = {
                "cattle": 0.025, "sheep": 0.035, "goat": 0.032,
                "horse": 0.022, "camel": 0.020
            }
            
            wf = weight_factors.get(animal_key, 12000)
            ff = feed_factors.get(animal_key, 0.03)
            est_weight = (girth ** 2 * length) / wf
            daily_dm = est_weight * ff
            
            st.success(f"**الوزن التقديري:** {est_weight:.1f} كجم")
            st.info(f"**الاحتياج اليومي (مادة جافة):** {daily_dm:.2f} كجم")
            
            adjusted_dp = default_dp * (1 + (est_weight - 500) / 2000)
            adjusted_se = default_se * (1 + (est_weight - 500) / 3000)
            
            st.caption(f"⚖️ DP مقترح: {adjusted_dp:.1f}% | SE مقترح: {adjusted_se:.1f}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            adjusted_dp = default_dp
            adjusted_se = default_se
            st.info("💡 لا تتوفر قياسات جسدية لهذا القطاع.")
    
    with col_settings:
        st.markdown("#### 🎯 السلالة والمرحلة")
        c1, c2 = st.columns(2)
        with c1:
            breed = st.selectbox("السلالة:", breeds, key=f"{animal_key}_breed")
        with c2:
            stage = st.selectbox("المرحلة:", stages, key=f"{animal_key}_stage")
        
        st.markdown("#### 🧬 الحالة الفسيولوجية")
        phys_state = st.selectbox(
            "الحالة:", 
            ["طبيعي", "حامل", "مرضع", "نشاط مكثف", "نمو سريع"],
            key=f"{animal_key}_phys"
        )
        
        multipliers = {
            "طبيعي": 1.0, "حامل": 1.15, "مرضع": 1.30,
            "نشاط مكثف": 1.25, "نمو سريع": 1.35
        }
        mult = multipliers.get(phys_state, 1.0)
        
        st.markdown("#### 🧬 حدود الموازنة")
        protein_basis = st.radio("أساس البروتين:", ["DP", "CP"],
                                  horizontal=True, key=f"{animal_key}_basis")
        
        if protein_basis == "DP":
            target_dp_in = st.number_input(
                "نسبة DP المستهدفة (%)", 5.0, 40.0,
                float(adjusted_dp * mult), step=0.5,
                key=f"{animal_key}_dp_in"
            )
            target_dp = target_dp_in
        else:
            target_cp_in = st.number_input(
                "نسبة CP المستهدفة (%)", 5.0, 60.0,
                float(adjusted_dp * mult / 0.80), step=0.5,
                key=f"{animal_key}_cp_in"
            )
            target_dp = target_cp_in * 0.80
        
        target_se = st.number_input(
            "معادل النشاء (SE)", 10.0, 90.0,
            float(adjusted_se * mult), step=1.0,
            key=f"{animal_key}_se_in"
        )
        
        st.caption(f"📌 معامل الحالة: {mult:.2f}")
    
    # اختيار المكونات
    st.markdown("#### 🌾 اختر المكونات العلفية")
    
    default_ingredients = {
        "cattle": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)",
                   "كسب فول صويا 44%", "أمباز الفول السوداني",
                   "مركزات مجترات", "ملح الطعام",
                   "الحجر الجيري", "فوسفات ثنائي الكالسيوم",
                   "بيكربونات الصوديوم"],
        "sheep": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)",
                  "كسب فول صويا 44%", "أمباز الفول السوداني",
                  "مركزات مجترات", "ملح الطعام",
                  "الحجر الجيري", "فوسفات ثنائي الكالسيوم",
                  "بيكربونات الصوديوم"],
        "goat": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)",
                 "كسب فول صويا 44%", "أمباز الفول السوداني",
                 "مركزات مجترات", "ملح الطعام",
                 "الحجر الجيري", "فوسفات ثنائي الكالسيوم",
                 "بيكربونات الصوديوم"],
        "horse": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)",
                  "كسب فول صويا 44%", "أمباز الفول السوداني",
                  "مولاس قصب السكر", "مركزات مجترات",
                  "ملح الطعام", "الحجر الجيري",
                  "فوسفات ثنائي الكالسيوم"],
        "camel": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)",
                  "كسب فول صويا 44%", "أمباز الفول السوداني",
                  "البرسيم الجاف", "مركزات مجترات",
                  "ملح الطعام", "الحجر الجيري",
                  "فوسفات ثنائي الكالسيوم"],
        "poultry": ["ذرة صفراء", "سورجم (فتريتة)", "كسب فول صويا 44%",
                    "كسب جلوتين الذرة", "مركزات دواجن",
                    "بريمكس دواجن", "ملح الطعام",
                    "الحجر الجيري", "فوسفات ثنائي الكالسيوم",
                    "إنزيم فايتيز"],
        "fish": ["ذرة صفراء", "كسب فول صويا 44%", "مسحوق أسماك 60%",
                 "كسب جلوتين الذرة", "مركزات دواجن",
                 "ملح الطعام", "فوسفات ثنائي الكالسيوم",
                 "إنزيم فايتيز"]
    }
    
    default_list = default_ingredients.get(animal_key, [])
    selected_ingredients = []
    ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=False):
            cols = st.columns(3)
            for idx, ing in enumerate(items.keys()):
                with cols[idx % 3]:
                    is_def = ing in default_list
                    if st.checkbox(ing, value=is_def, key=f"{animal_key}_chk_{ing}"):
                        default_price = 350.0
                        if "نخالة" in ing or "ملح" in ing:
                            default_price = 200.0
                        elif "مركزات" in ing or "بريمكس" in ing:
                            default_price = 600.0
                        elif "أسماك" in ing:
                            default_price = 900.0
                        
                        price = st.number_input(
                            f"سعر {ing} ($/طن)", 5.0,
                            value=default_price, step=10.0,
                            key=f"{animal_key}_p_{ing}"
                        )
                        selected_ingredients.append(ing)
                        ingredient_prices[ing] = price
    
    # أزرار التشغيل
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button(f"🚀 تشغيل محرك التركيب", type="primary",
                      use_container_width=True, key=f"{animal_key}_run"):
            if len(selected_ingredients) < 3:
                st.warning("⚠️ اختر 3 مكونات على الأقل.")
                voice_guide("يرجى اختيار 3 مكونات علفية على الأقل.")
            else:
                voice_guide(f"جاري تركيب العلف لـ {display_name}")
                st.info("🔄 جاري الحساب...")
                
                c_vec = [ingredient_prices[ing] for ing in selected_ingredients]
                bounds = [(0.0, 100.0) for _ in selected_ingredients]
                
                A_eq = [[1.0 for _ in selected_ingredients]]
                b_eq = [100.0]
                
                cp_row, se_row, ndf_row, adf_row = [], [], [], []
                for ing in selected_ingredients:
                    fd = FLAT_FEED_DB.get(ing, {})
                    cp = fd.get("CP", 0.0)
                    dc = fd.get("DC", 0.0)
                    se = fd.get("SE", 0.0)
                    ndf = fd.get("NDF", 0.0)
                    adf = fd.get("ADF", 0.0)
                    cp_row.append(cp * dc)
                    se_row.append(se)
                    ndf_row.append(ndf)
                    adf_row.append(adf)
                
                A_eq.append(cp_row)
                b_eq.append(target_dp * 100.0)
                
                A_ub, b_ub = [], []
                A_ub.append([-x for x in se_row])
                b_ub.append(-target_se * 100.0)
                
                if animal_key in ["cattle", "sheep", "goat", "camel"]:
                    A_ub.append(ndf_row)
                    b_ub.append(3500.0)
                    A_ub.append(adf_row)
                    b_ub.append(2000.0)
                elif animal_key == "horse":
                    A_ub.append(ndf_row)
                    b_ub.append(4000.0)
                
                if "نخالة قمح (ردة)" in selected_ingredients:
                    idx = selected_ingredients.index("نخالة قمح (ردة)")
                    row = [0.0] * len(selected_ingredients)
                    row[idx] = 1.0
                    A_ub.append(row)
                    b_ub.append(25.0 if animal_key in ["cattle", "sheep", "goat"] else 15.0)
                
                # إضافات إلزامية
                if animal_key in ["cattle", "sheep", "goat", "camel"]:
                    if "بيكربونات الصوديوم" not in selected_ingredients:
                        selected_ingredients.append("بيكربونات الصوديوم")
                        ingredient_prices["بيكربونات الصوديوم"] = 340.0
                        c_vec.append(340.0)
                        cp_row.append(0.0)
                        se_row.append(0.0)
                        ndf_row.append(0.0)
                        adf_row.append(0.0)
                        bounds.append((0.5, 0.5))
                
                if animal_key in ["poultry", "fish"]:
                    if "إنزيم فايتيز" not in selected_ingredients:
                        selected_ingredients.append("إنزيم فايتيز")
                        ingredient_prices["إنزيم فايتيز"] = 1200.0
                        c_vec.append(1200.0)
                        cp_row.append(0.0)
                        se_row.append(0.0)
                        ndf_row.append(0.0)
                        adf_row.append(0.0)
                        bounds.append((0.05, 0.05))
                
                try:
                    res = linprog(c_vec, A_ub=A_ub, b_ub=b_ub,
                                   A_eq=A_eq, b_eq=b_eq,
                                   bounds=bounds, method='highs')
                    
                    if res.success:
                        formula = {}
                        computed_se = 0.0
                        for idx, ing in enumerate(selected_ingredients):
                            if res.x[idx] > 0.0001:
                                formula[ing] = res.x[idx]
                                fd = FLAT_FEED_DB.get(ing, {})
                                computed_se += (res.x[idx] / 100.0) * fd.get("SE", 0.0)
                        
                        ton_cost = res.fun / 100.0
                        
                        # حفظ
                        st.session_state["active_formula"] = formula
                        st.session_state["computed_ton_cost"] = ton_cost
                        st.session_state["active_cp_tag"] = target_dp
                        st.session_state["active_se_tag"] = computed_se
                        st.session_state["active_breed_tag"] = f"{breed} - {stage}"
                        st.session_state["active_stage_title"] = phys_state
                        
                        st.success(f"✅ تم توليد الخلطة! التكلفة: ${ton_cost:.2f}/طن")
                        voice_guide(f"تم توليد الخلطة العلفية بتكلفة {ton_cost:.2f} دولار للطن")
                        
                        # عرض النتائج
                        col_r1, col_r2 = st.columns([0.6, 0.4])
                        with col_r1:
                            st.markdown("#### 📝 المقادير المعتمدة لطن واحد:")
                            for k, v in sorted(formula.items(), key=lambda x: -x[1]):
                                st.markdown(f"""
                                <div class="formula-item">
                                    <span><b>{k}</b></span>
                                    <span><b>{v:.2f}%</b> ({v*10:.1f} كجم)</span>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            c_m1, c_m2, c_m3 = st.columns(3)
                            c_m1.metric("💰 التكلفة/طن", f"${ton_cost:.2f}")
                            c_m2.metric("🧬 DP", f"{target_dp:.2f}%")
                            c_m3.metric("🌽 SE", f"{computed_se:.2f}")
                            
                            if requester:
                                st.info(f"👤 طالب العلف: {requester}")
                            
                            # المقارنة مع المعايير
                            std = STANDARD_VALUES.get(display_name, {}).get(stage, {})
                            if std:
                                st.markdown("#### 📊 المقارنة مع المعايير القياسية:")
                                comp = []
                                if 'DP' in std:
                                    dev = ((target_dp - std['DP']) / std['DP']) * 100
                                    grade = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                                    comp.append({"المقياس": "DP",
                                                  "المحسوب": f"{target_dp:.2f}%",
                                                  "القياسي": f"{std['DP']:.2f}%",
                                                  "الانحراف": f"{dev:.1f}%",
                                                  "التقييم": grade})
                                if 'SE' in std:
                                    dev = ((computed_se - std['SE']) / std['SE']) * 100
                                    grade = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                                    comp.append({"المقياس": "SE",
                                                  "المحسوب": f"{computed_se:.2f}",
                                                  "القياسي": f"{std['SE']:.2f}",
                                                  "الانحراف": f"{dev:.1f}%",
                                                  "التقييم": grade})
                                if 'CP' in std:
                                    cp_calc = target_dp / 0.80
                                    dev = ((cp_calc - std['CP']) / std['CP']) * 100
                                    grade = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                                    comp.append({"المقياس": "CP",
                                                  "المحسوب": f"{cp_calc:.2f}%",
                                                  "القياسي": f"{std['CP']:.2f}%",
                                                  "الانحراف": f"{dev:.1f}%",
                                                  "التقييم": grade})
                                st.table(pd.DataFrame(comp))
                            
                            # أزرار
                            c_btn1, c_btn2 = st.columns(2)
                            with c_btn1:
                                if st.button("🔬 إرسال للمختبر", key=f"{animal_key}_to_lab"):
                                    st.session_state["lab_sample"] = {
                                        'animal': display_name,
                                        'breed': breed,
                                        'stage': stage,
                                        'phys': phys_state,
                                        'dp': target_dp,
                                        'se': computed_se,
                                        'cp': target_dp / 0.80,
                                        'requester': requester,
                                        'formula': formula
                                    }
                                    st.success("✅ تم الإرسال. اذهب لتبويب المختبر.")
                                    voice_guide("تم إرسال العينة إلى المختبر")
                            
                            with c_btn2:
                                try:
                                    pdf = pdf_gen.formula_report(
                                        formula, target_dp, computed_se,
                                        breed, stage, ton_cost, "غير محدد",
                                        requester, std,
                                        {"الحالة": phys_state,
                                         "البروتين": protein_basis}
                                    )
                                    st.download_button(
                                        "📥 تحميل PDF",
                                        pdf,
                                        file_name=f"Tawornology_{display_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                        mime="application/pdf",
                                        key=f"{animal_key}_pdf"
                                    )
                                except Exception as e:
                                    st.warning(f"⚠️ تعذر إنشاء PDF: {e}")
                        
                        with col_r2:
                            if len(formula) > 1:
                                fig = px.pie(
                                    values=list(formula.values()),
                                    names=list(formula.keys()),
                                    title="توزيع المكونات",
                                    color_discrete_sequence=px.colors.sequential.Greens
                                )
                                fig.update_layout(height=400)
                                st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("❌ تعذر إيجاد حل رياضي. أضف مكونات أخرى.")
                        voice_guide("تعذر إيجاد حل رياضي متزن")
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")
    
    with col_btn2:
        if st.button("📋 عرض المعايير القياسية", use_container_width=True,
                      key=f"{animal_key}_std"):
            std = STANDARD_VALUES.get(display_name, {}).get(stage, {})
            if std:
                st.info(f"📊 المعايير: DP={std.get('DP','-')}% | "
                        f"SE={std.get('SE','-')} | CP={std.get('CP','-')}%")
            else:
                st.warning("⚠️ لا توجد معايير لهذه المرحلة.")
    
    with col_btn3:
        if st.button("🔊 تعليمات صوتية", use_container_width=True,
                      key=f"{animal_key}_voice"):
            voice_guide(f"مرحباً بك في قسم {display_name}. اختر السلالة والمرحلة، "
                        f"ثم اختر المكونات، واضغط على زر التشغيل.")

# =====================================================================
# دالة معادلات NRC
# =====================================================================
def render_nrc(animal_type):
    st.markdown(f'<div class="section-title">🧮 معادلات NRC - {animal_type}</div>',
                unsafe_allow_html=True)
    
    st.info("📊 حساب الاحتياجات الغذائية وفق NRC 2000/2001 "
            "من الوزن الحي والإنتاج الفعلي")
    
    c1, c2 = st.columns(2)
    with c1:
        default_w = 450.0 if animal_type == "أبقار" else (60.0 if animal_type in ["أغنام", "ماعز"] else 400.0)
        weight = st.number_input("⚖️ الوزن الحي (كجم):", 10.0,
                                   value=default_w, step=5.0,
                                   key=f"nrc_w_{animal_type}")
        
        prod = st.radio("نوع الإنتاج:", ["🥛 إنتاج حليب", "📈 تسمين"],
                         horizontal=True, key=f"nrc_p_{animal_type}")
    
    with c2:
        if prod == "🥛 إنتاج حليب":
            milk = st.number_input("🥛 الحليب اليومي (لتر):", 0.0,
                                     value=20.0 if animal_type == "أبقار" else 2.0,
                                     step=0.5, key=f"nrc_m_{animal_type}")
            fat = st.slider("دهن الحليب (%)", 2.5, 6.0, 3.5, 0.1,
                             key=f"nrc_f_{animal_type}")
        else:
            gain = st.number_input("📈 الزيادة اليومية (كجم):", 0.0,
                                     value=1.0 if animal_type == "أبقار" else 0.15,
                                     step=0.05, key=f"nrc_g_{animal_type}")
    
    if st.button(f"🧮 حساب الاحتياجات", type="primary",
                  key=f"nrc_calc_{animal_type}"):
        if prod == "🥛 إنتاج حليب":
            pr = AdvancedProductionEquations.dairy_protein(weight, milk, fat)
            er = AdvancedProductionEquations.dairy_energy(weight, milk, fat)
            ratio = er['total_energy'] / pr['total'] if pr['total'] > 0 else 0
            
            st.success("✅ وفق NRC 2001 (Dairy Cattle)")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("🧬 DP", f"{pr['dp_requirement']:.2f}%")
            c2.metric("🌽 SE", f"{er['se_requirement']:.0f}")
            c3.metric("📊 SE/DP", f"{ratio:.2f}")
            
            st.markdown(f"""
            <div class="price-card">
                <b>📊 احتياجات البروتين (جم/يوم):</b><br>
                ▪️ الإدامة: <b>{pr['maintenance']:.1f} جم</b><br>
                ▪️ الأيض: <b>{pr['metabolic']:.1f} جم</b><br>
                ▪️ الإنتاج: <b>{pr['production']:.1f} جم</b><br>
                ▪️ <b>الإجمالي: {pr['total']:.1f} جم/يوم</b><br><br>
                <b>⚡ احتياجات الطاقة (ميجا جول/يوم):</b><br>
                ▪️ الإدامة: <b>{er['maintenance_energy']:.2f}</b><br>
                ▪️ الإنتاج: <b>{er['production_energy']:.2f}</b><br>
                ▪️ <b>الإجمالي: {er['total_energy']:.2f}</b>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📐 المعادلات (NRC 2001)"):
                st.code("""
1. بروتين الإدامة = 2.5 × (الوزن^0.75)
2. بروتين الأيض = 1.2 × (الوزن^0.75)
3. بروتين الإنتاج = (الحليب × % بروتين) / 0.65
4. طاقة الإدامة = 0.08 × (الوزن^0.75)
5. طاقة الإنتاج = 5.3 × الحليب × (1 + 0.15 × (دهن-3.5))
                """)
            
            voice_guide(f"DP: {pr['dp_requirement']:.1f}% و SE: {er['se_requirement']:.0f}")
        else:
            pr = AdvancedProductionEquations.fattening_protein(weight, gain)
            er = AdvancedProductionEquations.fattening_energy(weight, gain)
            ratio = er['total_energy'] / pr['total'] if pr['total'] > 0 else 0
            
            st.success("✅ وفق NRC 2000 (Beef Cattle)")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("🧬 DP", f"{pr['dp_requirement']:.2f}%")
            c2.metric("🌽 SE", f"{er['se_requirement']:.0f}")
            c3.metric("📊 SE/DP", f"{ratio:.2f}")
            
            if 4.5 <= ratio <= 6.0:
                st.success(f"✅ النسبة مثالية للتسمين (4.5-6.0)")
            elif ratio > 6.0:
                st.warning(f"⚠️ النسبة مرتفعة ({ratio:.2f}) - طاقة زائدة")
            else:
                st.warning(f"⚠️ النسبة منخفضة ({ratio:.2f}) - بروتين زائد")
            
            st.markdown(f"""
            <div class="price-card">
                <b>📊 احتياجات البروتين (جم/يوم):</b><br>
                ▪️ الإدامة: <b>{pr['maintenance']:.1f} جم</b><br>
                ▪️ الأيض: <b>{pr['metabolic']:.1f} جم</b><br>
                ▪️ الإنتاج: <b>{pr['production']:.1f} جم</b><br>
                ▪️ <b>الإجمالي: {pr['total']:.1f} جم/يوم</b>
            </div>
            """, unsafe_allow_html=True)
            
            voice_guide(f"DP: {pr['dp_requirement']:.1f}% و SE: {er['se_requirement']:.0f}")

# =====================================================================
# تبويب 0: القطاع الحيواني
# =====================================================================
with tabs[0]:
    guide_section("القطاع الحيواني",
                  "اختر نوع الحيوان، السلالة، المرحلة، وأدخل البيانات المطلوبة.")
    
    animal_tabs = st.tabs([
        "🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐴 خيول",
        "🐫 إبل", "🐔 دواجن", "🐟 أسماك"
    ])
    
    with animal_tabs[0]:
        render_formulation(
            "cattle", "أبقار", "🐄",
            ["كنانة (سوداني)", "بطانة (مدر)", "هولشتاين / محسن"],
            ["تسمين عجول", "حليب/إدرار", "حمل/دفع غذائي", "صيانة", "تسمين مكثف"],
            12.0, 65.0, "أبقار"
        )
    with animal_tabs[1]:
        render_formulation(
            "sheep", "أغنام", "🐏",
            ["الضأن الصحراوي", "البربري", "النعيمي", "محلية/هجين"],
            ["تسمين حملان", "نعاج مرضعات", "نعاج حامل", "نعاج جافة"],
            11.5, 62.0, "أغنام"
        )
    with animal_tabs[2]:
        render_formulation(
            "goat", "ماعز", "🐐",
            ["الماعز النوبي", "الصحراوي", "بور / محسن"],
            ["تسمين جديان", "عنزات حلابة", "عنزات حامل", "صيانة"],
            11.0, 60.0, "ماعز"
        )
    with animal_tabs[3]:
        render_formulation(
            "horse", "خيول", "🐴",
            ["خيل عربي أصيل", "ثوروبريد", "خيول محلية"],
            ["راحة/صيانة", "عمل خفيف", "عمل متوسط", "عمل مكثف",
             "سباق", "أمهار نامية", "فرسات مرضعات"],
            11.0, 62.0, "خيول"
        )
    with animal_tabs[4]:
        render_formulation(
            "camel", "إبل", "🐫",
            ["عربية (دروميداري)", "باختري", "هجين"],
            ["راحة/صيانة", "حمل/رضاعة", "إنتاج حليب", "تسمين"],
            10.0, 58.0, "إبل"
        )
    with animal_tabs[5]:
        render_formulation(
            "poultry", "دواجن", "🐔",
            ["دواجن لاحم (Broiler)", "دواجن بياض (Layer)", "طائر السمان"],
            ["بادي (0-14 يوم)", "نامي (15-28 يوم)",
             "ناهي (29-42 يوم)", "ناهي متقدم"],
            18.0, 72.0, "دواجن", has_measurements=False
        )
    with animal_tabs[6]:
        render_formulation(
            "fish", "أسماك", "🐟",
            ["البلطي النيلي", "القرموط"],
            ["بادئ", "نمو", "تسمين"],
            28.0, 68.0, "أسماك", has_measurements=False
        )

# =====================================================================
# تبويب 1: المختبر الذكي
# =====================================================================
with tabs[1]:
    guide_section("المختبر الذكي",
                  "ارفع صورة تركيبة علفية لاستخراج القيم الغذائية تلقائياً، "
                  "أو أدخل البيانات يدوياً لتحليلها ومقارنتها بالمعايير.")
    
    st.markdown('<div class="section-title">🔬 المختبر الذكي</div>',
                unsafe_allow_html=True)
    
    # عينة قادمة من التركيب
    if st.session_state.get("lab_sample"):
        sample = st.session_state["lab_sample"]
        st.success(f"📥 عينة مستلمة من: {sample['animal']} - {sample['breed']} - {sample['stage']}")
        st.write(f"**DP:** {sample['dp']:.2f}% | "
                 f"**SE:** {sample['se']:.2f} | "
                 f"**طالب:** {sample.get('requester', 'غير محدد')}")
        if st.button("🗑️ مسح العينة"):
            st.session_state["lab_sample"] = None
            st.rerun()
    
    # رفع صورة للـ OCR
    st.markdown("### 📸 تحليل صورة (OCR)")
    
    if not OCR_AVAILABLE and not EASYOCR_AVAILABLE:
        st.warning("⚠️ مكتبات OCR غير مثبتة. يمكنك إدخال البيانات يدوياً.")
    
    uploaded = st.file_uploader(
        "ارفع صورة لتركيبة علفية (كتاب، ورقة، هاتف)",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
        key="lab_upload"
    )
    
    if uploaded is not None:
        try:
            img = PILImage.open(uploaded)
            st.image(img, caption="الصورة المرفوعة", use_container_width=True)
            
            if st.button("🔍 استخراج البيانات من الصورة", type="primary"):
                if not OCR_AVAILABLE and not EASYOCR_AVAILABLE:
                    st.error("❌ مكتبات OCR غير متوفرة")
                else:
                    with st.spinner("جاري التحليل..."):
                        try:
                            lab = SmartLabSystem()
                            result, err = lab.analyze_image(img)
                            if err:
                                st.error(f"❌ {err}")
                            else:
                                st.session_state["ocr_result"] = result
                                st.success("✅ تم التحليل!")
                                voice_guide("تم تحليل الصورة بنجاح")
                        except Exception as e:
                            st.error(f"خطأ: {e}")
        except Exception as e:
            st.error(f"خطأ في الصورة: {e}")
    
    # إدخال / تعديل
    st.markdown("### ✍️ البيانات المستخرجة / للإدخال اليدوي")
    ocr = st.session_state.get("ocr_result", {})
    
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("اسم العينة:", value=ocr.get('sample_name', ''),
                       key="lab_name")
        st.number_input("بروتين خام (CP %):", 0.0,
                         value=float(ocr.get('cp') or 0.0),
                         step=0.1, key="lab_cp")
        st.number_input("معامل الهضم (DC):", 0.0, 1.0,
                         value=float(ocr.get('dc') or 0.0),
                         step=0.01, key="lab_dc")
        st.number_input("معادل النشاء (SE):", 0.0,
                         value=float(ocr.get('se') or 0.0),
                         step=0.1, key="lab_se")
    with c2:
        st.number_input("NDF %:", 0.0, value=float(ocr.get('ndf') or 0.0),
                         step=0.1, key="lab_ndf")
        st.number_input("ADF %:", 0.0, value=float(ocr.get('adf') or 0.0),
                         step=0.1, key="lab_adf")
        st.number_input("دهن خام (EE %):", 0.0,
                         value=float(ocr.get('ee') or 0.0),
                         step=0.1, key="lab_ee")
        st.number_input("رماد (ASH %):", 0.0,
                         value=float(ocr.get('ash') or 0.0),
                         step=0.1, key="lab_ash")
    
    # اختيار الفصيل للمقارنة
    st.markdown("### 🎯 اختر الفصيل والمرحلة للمقارنة")
    c1, c2 = st.columns(2)
    with c1:
        lab_animal = st.selectbox("الفصيل:",
                                   ["أبقار", "أغنام", "ماعز", "خيول",
                                    "إبل", "دواجن", "أسماك"],
                                   key="lab_animal")
    with c2:
        lab_stages = list(STANDARD_VALUES.get(lab_animal, {}).keys())
        lab_stage = st.selectbox("المرحلة:", lab_stages if lab_stages else ["عام"],
                                  key="lab_stage")
    
    # زر التحليل
    if st.button("🧪 تشغيل التحليل والمقارنة", type="primary",
                  use_container_width=True, key="run_lab"):
        cp = st.session_state.get("lab_cp", 0.0)
        dc = st.session_state.get("lab_dc", 0.0)
        se = st.session_state.get("lab_se", 0.0)
        ndf = st.session_state.get("lab_ndf", 0.0)
        adf = st.session_state.get("lab_adf", 0.0)
        ee = st.session_state.get("lab_ee", 0.0)
        ash = st.session_state.get("lab_ash", 0.0)
        
        dp_calc = cp * dc if dc > 0 else cp * 0.75
        
        if cp == 0 and se == 0:
            st.warning("⚠️ أدخل قيم CP و SE على الأقل.")
        else:
            st.success("✅ تم التحليل!")
            voice_guide("تم التحليل بنجاح")
            
            st.markdown("### 📊 النتائج المحسوبة")
            c1, c2, c3 = st.columns(3)
            c1.metric("🧬 CP", f"{cp:.2f}%")
            c2.metric("🧪 DP", f"{dp_calc:.2f}%")
            c3.metric("🌽 SE", f"{se:.2f}")
            
            # المقارنة
            std = STANDARD_VALUES.get(lab_animal, {}).get(lab_stage, {})
            if std:
                st.markdown("### 📏 المقارنة مع المعايير القياسية")
                
                comp_data = []
                eval_dict = {}
                
                if 'DP' in std:
                    dev = ((dp_calc - std['DP']) / std['DP']) * 100
                    grade = "✅ ممتاز" if abs(dev) <= 5 else ("⚠️ جيد" if abs(dev) <= 10 else "❌ يحتاج تحسين")
                    comp_data.append({
                        "المقياس": "DP",
                        "المحسوب": f"{dp_calc:.2f}%",
                        "القياسي": f"{std['DP']:.2f}%",
                        "الانحراف": f"{dev:.1f}%",
                        "التقييم": grade
                    })
                    eval_dict["DP"] = grade
                
                if 'SE' in std:
                    dev = ((se - std['SE']) / std['SE']) * 100
                    grade = "✅ ممتاز" if abs(dev) <= 5 else ("⚠️ جيد" if abs(dev) <= 10 else "❌ يحتاج تحسين")
                    comp_data.append({
                        "المقياس": "SE",
                        "المحسوب": f"{se:.2f}",
                        "القياسي": f"{std['SE']:.2f}",
                        "الانحراف": f"{dev:.1f}%",
                        "التقييم": grade
                    })
                    eval_dict["SE"] = grade
                
                if 'CP' in std:
                    dev = ((cp - std['CP']) / std['CP']) * 100
                    grade = "✅ ممتاز" if abs(dev) <= 5 else ("⚠️ جيد" if abs(dev) <= 10 else "❌ يحتاج تحسين")
                    comp_data.append({
                        "المقياس": "CP",
                        "المحسوب": f"{cp:.2f}%",
                        "القياسي": f"{std['CP']:.2f}%",
                        "الانحراف": f"{dev:.1f}%",
                        "التقييم": grade
                    })
                    eval_dict["CP"] = grade
                
                st.table(pd.DataFrame(comp_data))
                
                # الرسم البياني
                st.markdown("### 📊 الرسم البياني - محسوب vs قياسي")
                
                try:
                    fig = go.Figure()
                    
                    cats = []
                    calc_vals = []
                    std_vals = []
                    
                    if 'DP' in std:
                        cats.append('DP')
                        calc_vals.append(dp_calc)
                        std_vals.append(std['DP'])
                    if 'SE' in std:
                        cats.append('SE')
                        calc_vals.append(se)
                        std_vals.append(std['SE'])
                    if 'CP' in std:
                        cats.append('CP')
                        calc_vals.append(cp)
                        std_vals.append(std['CP'])
                    
                    fig.add_trace(go.Bar(
                        x=cats, y=calc_vals, name='المحسوب',
                        marker_color='#2e7d32',
                        text=[f"{v:.1f}" for v in calc_vals],
                        textposition='outside'
                    ))
                    fig.add_trace(go.Bar(
                        x=cats, y=std_vals, name='القياسي',
                        marker_color='#1565C0',
                        text=[f"{v:.1f}" for v in std_vals],
                        textposition='outside'
                    ))
                    
                    fig.update_layout(
                        title="مقارنة النتائج المحسوبة مع المعايير القياسية",
                        xaxis_title="المقياس",
                        yaxis_title="القيمة",
                        barmode='group',
                        height=400,
                        legend=dict(orientation="h", yanchor="bottom",
                                     y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"تعذر الرسم: {e}")
                
                # تحميل PDF
                try:
                    pdf = pdf_gen.lab_report(
                        {'cp': cp, 'dp': dp_calc, 'se': se},
                        lab_animal, lab_stage, std,
                        eval_dict, None
                    )
                    st.download_button(
                        "📥 تحميل تقرير المختبر PDF",
                        pdf,
                        file_name=f"Lab_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        key="lab_pdf_download"
                    )
                except Exception as e:
                    st.warning(f"⚠️ تعذر إنشاء PDF: {e}")
                
                # حفظ في قاعدة البيانات
                if st.button("💾 حفظ نتيجة التحليل", key="save_lab_result"):
                    try:
                        db.insert('lab_results', {
                            'result_id': secrets.token_hex(8),
                            'sample_name': st.session_state.get("lab_name", ""),
                            'animal_type': lab_animal,
                            'stage': lab_stage,
                            'cp': cp, 'dp': dp_calc, 'se': se,
                            'ndf': ndf, 'adf': adf, 'ee': ee, 'ash': ash,
                            'moisture': 0.0, 'notes': '',
                            'performed_by': st.session_state.get("user_role", "public"),
                            'result_date': datetime.now().isoformat()
                        })
                        st.success("✅ تم الحفظ!")
                    except Exception as e:
                        st.error(f"خطأ: {e}")
            else:
                st.info("ℹ️ لا توجد معايير لهذا الفصيل/المرحلة.")
    
    # نتائج المختبر السابقة
    st.markdown("---")
    st.markdown("### 📋 نتائج المختبر السابقة")
    try:
        rows = db.get('lab_results')
        if rows:
            df = pd.DataFrame(rows, columns=[
                'ID', 'العينة', 'الفصيل', 'المرحلة', 'CP', 'DP', 'SE',
                'NDF', 'ADF', 'EE', 'ASH', 'الرطوبة', 'ملاحظات',
                'المحلل', 'التاريخ'
            ])
            df_show = df[['العينة', 'الفصيل', 'CP', 'DP', 'SE', 'التاريخ']].tail(20)
            st.dataframe(df_show, use_container_width=True)
        else:
            st.info("📭 لا توجد نتائج سابقة.")
    except Exception:
        st.info("📭 لا توجد نتائج سابقة.")

# =====================================================================
# تبويب 2: معادلات NRC
# =====================================================================
with tabs[2]:
    guide_section("معادلات NRC",
                  "احسب الاحتياجات الغذائية الدقيقة وفق معادلات NRC الأمريكية.")
    
    nrc_tabs = st.tabs([
        "🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐴 خيول", "🐫 إبل"
    ])
    with nrc_tabs[0]:
        render_nrc("أبقار")
    with nrc_tabs[1]:
        render_nrc("أغنام")
    with nrc_tabs[2]:
        render_nrc("ماعز")
    with nrc_tabs[3]:
        render_nrc("خيول")
    with nrc_tabs[4]:
        render_nrc("إبل")

# =====================================================================
# تبويب 3: إدارة المزارع (للمالك)
# =====================================================================
if is_owner:
    with tabs[3]:
        guide_section("إدارة المزارع",
                      "أنشئ مزارع، أضف دورات إنتاجية، وسجل بيانات يومية.")
        
        st.markdown('<div class="section-title">🐔 إدارة المزارع</div>',
                    unsafe_allow_html=True)
        
        # إنشاء مزرعة
        with st.expander("➕ إضافة مزرعة جديدة", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                fname = st.text_input("اسم المزرعة:", key="farm_name_input")
                ftype = st.selectbox("النوع:",
                                      ["دواجن لاحم", "دواجن بياض", "أبقار",
                                       "أغنام", "ماعز", "إبل", "مختلط"],
                                      key="farm_type_input")
            with c2:
                owner = st.text_input("المالك:", key="farm_owner_input")
                phone = st.text_input("الهاتف:",
                                        value=WHATSAPP_NUMBER,
                                        key="farm_phone_input")
            with c3:
                location = st.text_input("الموقع:", key="farm_loc_input")
            
            if st.button("💾 إنشاء المزرعة", type="primary",
                          key="create_farm_btn"):
                if fname and owner:
                    fid = farm_mgr.create_farm(fname, ftype, owner, phone, location)
                    st.success(f"✅ تم إنشاء المزرعة '{fname}'")
                    voice_guide(f"تم إنشاء مزرعة {fname}")
                    st.rerun()
                else:
                    st.warning("⚠️ أدخل اسم المزرعة والمالك.")
        
        # عرض المزارع
        farms = farm_mgr.get_farms()
        if farms:
            st.markdown("#### 🏠 المزارع المسجلة:")
            for f in farms:
                fid, fname, ftype, owner, phone = f[0], f[1], f[2], f[3], f[4]
                with st.expander(f"🏠 {fname} - {ftype} (المالك: {owner})"):
                    st.write(f"**الهاتف:** {phone}")
                    
                    # إضافة دورة
                    with st.form(f"cycle_form_{fid}"):
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            ctype = st.selectbox("نوع الدورة:", ["لاحم", "بياض", "تسمين"],
                                                   key=f"ct_{fid}")
                        with c2:
                            count = st.number_input("العدد الابتدائي:", 1, 100000,
                                                     1000, key=f"cnt_{fid}")
                        with c3:
                            breed = st.text_input("السلالة:",
                                                    value="Ross 308",
                                                    key=f"br_{fid}")
                        if st.form_submit_button("➕ إنشاء دورة"):
                            cid = farm_mgr.create_cycle(fid, ctype, count, breed)
                            st.success(f"✅ تم إنشاء الدورة: {cid[:8]}")
                            st.rerun()
                    
                    # عرض الدورات
                    cycles = farm_mgr.get_cycles(fid)
                    if cycles:
                        st.markdown("**الدورات:**")
                        for cyc in cycles:
                            cid, ctype2, st_date, initial, brd, status = (
                                cyc[0], cyc[2], cyc[3], cyc[5], cyc[6], cyc[7]
                            )
                            status_icon = "🟢" if status == "active" else "🔴"
                            st.markdown(f"""
                            <div class="info-card">
                                {status_icon} <b>{ctype2} - {brd}</b> | 
                                العدد: {initial} | 
                                بدأت: {st_date[:10]} | 
                                ID: {cid[:8]}
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("📭 لا توجد مزارع. أضف مزرعة جديدة.")

# =====================================================================
# تبويب بدائل الحليب
# =====================================================================
milk_tab_idx = 4 if is_owner else 3
with tabs[milk_tab_idx]:
    guide_section("بدائل الحليب",
                  "قم بتركيب بديل حليب متكامل لرضاعة الصغار.")
    
    st.markdown('<div class="section-title">🍼 تركيب بدائل الحليب</div>',
                unsafe_allow_html=True)
    
    st.info("""
    **🧬 هذا القسم لتركيب بدائل الحليب للصغار:**
    عجول، حملان، جديان، مهرات، وأطفال الإبل،
    في حالة عدم توفر الحليب الطبيعي.
    """)
    
    c1, c2 = st.columns(2)
    with c1:
        animal_m = st.selectbox("نوع الحيوان:",
                                 ["عجل بقري", "حملان أغنام", "جديان ماعز",
                                  "مهرات خيول", "أطفال إبل"],
                                 key="milk_animal")
        age = st.slider("العمر (يوم)", 1, 120, 30, key="milk_age")
    with c2:
        st.markdown("**الاحتياجات المقدرة:**")
        needs = {
            "عجل بقري": {"protein": 22, "fat": 18, "energy": 75, "volume": 8},
            "حملان أغنام": {"protein": 24, "fat": 20, "energy": 72, "volume": 4},
            "جديان ماعز": {"protein": 23, "fat": 19, "energy": 70, "volume": 3},
            "مهرات خيول": {"protein": 20, "fat": 15, "energy": 68, "volume": 5},
            "أطفال إبل": {"protein": 21, "fat": 17, "energy": 66, "volume": 6}
        }
        
        if age < 14:
            af = 1.2
        elif age < 30:
            af = 1.0
        elif age < 60:
            af = 0.85
        else:
            af = 0.70
        
        target_p = needs[animal_m]["protein"] * af
        target_f = needs[animal_m]["fat"] * af
        target_e = needs[animal_m]["energy"] * af
        daily_vol = needs[animal_m]["volume"] * af
        
        st.metric("البروتين المطلوب", f"{target_p:.1f}%")
        st.metric("الدهون المطلوبة", f"{target_f:.1f}%")
        st.metric("الطاقة المطلوبة", f"{target_e:.1f}")
        st.metric("الحجم اليومي", f"{daily_vol:.1f} لتر")
    
    st.markdown("#### 🥛 اختر المكونات:")
    
    replacer_ing = {
        "حليب مجفف خالي الدسم": {"CP": 34.0, "Fat": 1.0, "SE": 40.0, "Cost": 18.0},
        "مصل الحليب المجفف": {"CP": 12.0, "Fat": 1.0, "SE": 35.0, "Cost": 12.0},
        "دهن نباتي": {"CP": 0.0, "Fat": 99.0, "SE": 10.0, "Cost": 8.0},
        "ليسيثين الصويا": {"CP": 0.0, "Fat": 95.0, "SE": 0.0, "Cost": 15.0},
        "بروتين الصويا المركز": {"CP": 65.0, "Fat": 1.0, "SE": 30.0, "Cost": 20.0}
    }
    
    selected_r = []
    prices_r = {}
    
    cols = st.columns(3)
    for i, (ing, data) in enumerate(replacer_ing.items()):
        with cols[i % 3]:
            if st.checkbox(ing, value=True if i < 4 else False,
                            key=f"milk_{ing}"):
                p = st.number_input(f"سعر {ing} ($/كجم)", 1.0,
                                     value=float(data["Cost"]),
                                     step=0.5, key=f"milk_p_{ing}")
                selected_r.append(ing)
                prices_r[ing] = p
    
    if st.button("🍼 توليد تركيبة بديل الحليب", type="primary",
                  use_container_width=True, key="milk_run"):
        if len(selected_r) < 3:
            st.warning("⚠️ اختر 3 مكونات على الأقل")
        else:
            with st.spinner("جاري الحساب..."):
                c = [prices_r[ing] for ing in selected_r]
                bounds = [(0, 100) for _ in selected_r]
                
                A_eq = [[1] * len(selected_r)]
                b_eq = [100]
                
                protein_row = [replacer_ing[ing]["CP"] for ing in selected_r]
                A_eq.append(protein_row)
                b_eq.append(target_p)
                
                A_ub = []
                b_ub = []
                fat_row = [replacer_ing[ing]["Fat"] for ing in selected_r]
                A_ub.append([-x for x in fat_row])
                b_ub.append(-target_f)
                
                energy_row = [replacer_ing[ing]["SE"] for ing in selected_r]
                A_ub.append([-x for x in energy_row])
                b_ub.append(-target_e)
                
                res = linprog(c, A_ub=A_ub, b_ub=b_ub,
                               A_eq=A_eq, b_eq=b_eq,
                               bounds=bounds, method='highs')
                
                if res.success:
                    formula = {selected_r[i]: res.x[i]
                                for i in range(len(selected_r))
                                if res.x[i] > 0.0001}
                    cost_kg = res.fun / 100.0
                    
                    st.success(f"✅ تم التوليد! التكلفة: ${cost_kg:.2f}/كجم")
                    voice_guide("تم توليد بديل الحليب")
                    
                    st.markdown("#### 📝 المقادير لكل كجم:")
                    for k, v in formula.items():
                        st.markdown(f"""
                        <div class="formula-item">
                            <span><b>{k}</b></span>
                            <span><b>{v:.1f}%</b> ({v*10:.1f} جم)</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    instructions = f"""الجرعة اليومية: {daily_vol:.1f} لتر مقسمة على 3-4 وجبات
التركيز: 100-150 جم مسحوق لكل لتر ماء دافئ (40-45°م)
درجة الحرارة: يجب أن يكون الحليب 38-40°م عند التقديم
التخزين: يحفظ بارداً وجافاً، ويستخدم خلال 24 ساعة"""
                    
                    st.markdown("#### 📋 تعليمات التقديم:")
                    st.info(instructions)
                    
                    # PDF
                    try:
                        pdf = pdf_gen.milk_replacer_report(
                            formula, animal_m, age, instructions
                        )
                        st.download_button(
                            "📥 تحميل تقرير PDF",
                            pdf,
                            file_name=f"MilkReplacer_{animal_m}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            key="milk_pdf"
                        )
                    except Exception as e:
                        st.warning(f"⚠️ {e}")
                else:
                    st.error("❌ تعذر إيجاد تركيبة مناسبة.")

# =====================================================================
# تبويب مواقيت الصلاة
# =====================================================================
prayer_tab_idx = 5 if is_owner else 4
with tabs[prayer_tab_idx]:
    guide_section("مواقيت الصلاة", "اعرض مواقيت الصلاة حسب المدينة.")
    
    st.markdown('<div class="section-title">🕌 مواقيت الصلاة</div>',
                unsafe_allow_html=True)
    
    city = st.selectbox("اختر المدينة:", list(PRAYER_CITIES.keys()),
                         key="prayer_city")
    
    if city:
        times = get_prayer_times(city)
        if times:
            st.markdown(f"#### 📍 مواقيت الصلاة في {city}")
            cols = st.columns(3)
            for i, (name, time_val) in enumerate(times.items()):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="font-size:1.5rem;">🕌</div>
                        <h3 style="color:#1b5e20; margin:5px 0;">{name}</h3>
                        <div class="number">{time_val}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            if st.button("🔔 تفعيل تنبيه الصلاة القادمة", key="prayer_alert"):
                now = datetime.now().strftime("%H:%M")
                next_p = None
                for name, tv in times.items():
                    if tv > now:
                        next_p = name
                        break
                if next_p:
                    voice_guide(f"حان وقت صلاة {next_p} في {city}")
                    st.success(f"✅ تم تشغيل التنبيه لصلاة {next_p}")
                else:
                    st.info("جميع صلوات اليوم انتهت")

# =====================================================================
# تبويب منبه الجرعات
# =====================================================================
dose_tab_idx = 6 if is_owner else 5
with tabs[dose_tab_idx]:
    guide_section("منبه الجرعات",
                  "سجل اللقاحات والفيتامينات وتلقَّ تنبيهات.")
    
    st.markdown('<div class="section-title">💊 منبه الجرعات</div>',
                unsafe_allow_html=True)
    
    rs = DoseReminderSystem()
    due = rs.get_due()
    
    if due:
        st.warning(f"⚠️ هناك {len(due)} جرعة مستحقة!")
        for r in due:
            st.markdown(f"""
            <div class="warning-card">
                <b>🔔 {r['dose_name']}</b> - {r['animal_type']}<br>
                الجرعة: {r['dose_amount']} {r['dose_unit']} | 
                الطريقة: {r['administration_route']}<br>
                التاريخ: {r['next_dose_date'][:10]}
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"✅ تم الإعطاء", key=f"done_{r['id']}"):
                    rs.complete(r['id'])
                    voice_guide(f"تم تسجيل إعطاء {r['dose_name']}")
                    st.rerun()
            with c2:
                msg = f"🔔 جرعة: {r['dose_name']} | {r['animal_type']} | {r['dose_amount']} {r['dose_unit']}"
                enc = urllib.parse.quote(msg)
                st.markdown(f'<a href="https://wa.me/{WHATSAPP_NUMBER}?text={enc}" target="_blank"><button style="background:#25D366; color:white; padding:8px 16px; border:none; border-radius:20px; font-weight:bold;">📲 واتساب</button></a>', unsafe_allow_html=True)
    else:
        st.success("✅ لا توجد جرعات مستحقة حالياً")
    
    with st.expander("➕ إضافة جرعة جديدة"):
        c1, c2, c3 = st.columns(3)
        with c1:
            animal_d = st.selectbox("الحيوان:",
                                     ["أبقار", "أغنام", "ماعز", "خيول", "إبل", "دواجن", "أسماك"],
                                     key="dose_animal")
            dtype = st.selectbox("النوع:",
                                  ["لقاح", "فيتامين", "دواء", "مضاد طفيليات"],
                                  key="dose_type")
            dname = st.text_input("اسم الجرعة:", key="dose_name")
        with c2:
            damount = st.number_input("الجرعة:", 0.0, value=1.0, step=0.1,
                                        key="dose_amount")
            dunit = st.selectbox("الوحدة:", ["مل", "جم", "مجم", "قطرة"],
                                  key="dose_unit")
            droute = st.selectbox("الطريقة:",
                                   ["عضل", "تحت الجلد", "فموي", "مياه الشرب",
                                    "رش", "قطرة عين"],
                                   key="dose_route")
        with c3:
            dfreq = st.number_input("التكرار (أيام):", 1, 365, 7,
                                     key="dose_freq")
            dstart = st.date_input("تاريخ البدء", datetime.now(),
                                     key="dose_start")
            dnotes = st.text_area("ملاحظات:", key="dose_notes")
        
        if st.button("💾 حفظ الجرعة", type="primary"):
            if dname:
                rs.add(animal_d, dtype, dname, damount, dunit, droute,
                        dfreq, dstart.isoformat(), dnotes)
                st.success(f"✅ تم إضافة منبه لـ {dname}")
                voice_guide(f"تم إضافة منبه للجرعة {dname}")
                st.rerun()
            else:
                st.warning("أدخل اسم الجرعة")
    
    if st.session_state.get("dose_reminders"):
        st.markdown("#### 📋 الجرعات المسجلة")
        for r in st.session_state["dose_reminders"]:
            with st.expander(f"💊 {r['dose_name']} - {r['animal_type']}"):
                st.write(f"**النوع:** {r['dose_type']}")
                st.write(f"**الجرعة:** {r['dose_amount']} {r['dose_unit']}")
                st.write(f"**الطريقة:** {r['administration_route']}")
                st.write(f"**التكرار:** كل {r['frequency_days']} يوم")
                st.write(f"**الجرعة القادمة:** {r['next_dose_date'][:10]}")

# =====================================================================
# تبويب بورصة الأسعار
# =====================================================================
price_tab_idx = 7 if is_owner else 6
with tabs[price_tab_idx]:
    guide_section("بورصة الأسعار", "متابعة أسعار المواشي والمنتجات.")
    
    st.markdown('<div class="section-title">📊 بورصة الأسعار</div>',
                unsafe_allow_html=True)
    
    if is_owner:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🐄 أسعار المواشي")
            for name, price in list(st.session_state["global_livestock_prices"].items()):
                new_p = st.number_input(name, value=float(price), step=5.0,
                                          key=f"lsp_{name}")
                st.session_state["global_livestock_prices"][name] = new_p
        with c2:
            st.subheader("🥩 أسعار المنتجات")
            for name, price in list(st.session_state["global_products_prices"].items()):
                new_p = st.number_input(name, value=float(price), step=0.5,
                                          key=f"pp_{name}")
                st.session_state["global_products_prices"][name] = new_p
        
        st.subheader("💱 أسعار الصرف")
        for country, data in EXCHANGE_RATES.items():
            new_r = st.number_input(f"{country} ({data['name']})",
                                     value=float(data['rate']), step=1.0,
                                     key=f"ex_{country}")
            EXCHANGE_RATES[country]["rate"] = new_r
    else:
        st.info("🔒 عرض فقط للزوار")
        st.markdown("#### 🐄 أسعار المواشي")
        for name, price in st.session_state["global_livestock_prices"].items():
            st.markdown(f"▪️ {name}: **${price:.2f}**")
        st.markdown("#### 🥩 أسعار المنتجات")
        for name, price in st.session_state["global_products_prices"].items():
            st.markdown(f"▪️ {name}: **${price:.2f}**")

# =====================================================================
# تبويبات المالك فقط
# =====================================================================
if is_owner:
    # تبويب المستودعات
    with tabs[8]:
        guide_section("المستودعات", "إدارة المخزون.")
        
        st.markdown('<div class="section-title">🏭 إدارة المستودعات</div>',
                    unsafe_allow_html=True)
        
        inv_data = []
        warns = InventoryManager.check()
        for item, data in st.session_state["inventory"].items():
            status = "🔴 نفذ" if item in warns and warns[item] == "نفذ" else (
                "🟠 منخفض" if item in warns else "🟢 آمن"
            )
            inv_data.append({
                "المادة": item,
                "الكمية (طن)": data["quantity"],
                "الحد الأدنى": data["min_threshold"],
                "الحالة": status
            })
        
        st.dataframe(pd.DataFrame(inv_data), use_container_width=True,
                      height=400)
        
        with st.expander("✏️ تحديث كمية مادة"):
            sel = st.selectbox("المادة:", list(FLAT_FEED_DB.keys()),
                                key="inv_sel")
            new_q = st.number_input("الكمية الجديدة (طن)", 0.0,
                                     value=float(st.session_state["inventory"][sel]["quantity"]),
                                     step=1.0, key="inv_q")
            if st.button("💾 تحديث", key="inv_update"):
                st.session_state["inventory"][sel]["quantity"] = new_q
                st.session_state["inventory"][sel]["last_updated"] = datetime.now().isoformat()
                st.success("✅ تم التحديث")
                st.rerun()
    
    # تبويب الفواتير
    with tabs[9]:
        guide_section("الفواتير", "إصدار فواتير للعملاء.")
        
        st.markdown('<div class="section-title">🧾 الفواتير</div>',
                    unsafe_allow_html=True)
        
        if not st.session_state.get("active_formula"):
            st.info("💡 قم أولاً بتوليد خلطة في تبويب القطاع الحيواني.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                client = st.text_input("العميل:", key="inv_client")
                cphone = st.text_input("الهاتف:", key="inv_phone")
            with c2:
                qty = st.number_input("الكمية (طن):", 0.1,
                                        value=2.0, step=0.5, key="inv_qty")
                profit = st.number_input("هامش الربح ($/طن):", 0.0,
                                          value=50.0, step=10.0, key="inv_profit")
            with c3:
                st.metric("تكلفة الطن", f"${st.session_state['computed_ton_cost']:.2f}")
                selling = st.session_state['computed_ton_cost'] + profit
                st.metric("سعر البيع/طن", f"${selling:.2f}")
            
            total = selling * qty
            st.markdown(f"""
            <div class="price-card">
                <h4>💰 تفاصيل الفاتورة</h4>
                <p>العميل: <b>{client}</b></p>
                <p>الكمية: <b>{qty} طن</b> × <b>${selling:.2f}</b></p>
                <p style="font-size:1.4rem; color:#1b5e20;">
                    <b>الإجمالي: ${total:.2f}</b>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("✅ تأكيد البيع وخصم المخزون", type="primary"):
                can = True
                for name, pct in st.session_state["active_formula"].items():
                    need = (pct / 100) * qty
                    cur = st.session_state["inventory"].get(name, {}).get("quantity", 0.0)
                    if cur < need:
                        st.error(f"❌ رصيد غير كافٍ: {name} (المطلوب {need:.2f}، المتوفر {cur:.2f})")
                        can = False
                        break
                if can:
                    for name, pct in st.session_state["active_formula"].items():
                        need = (pct / 100) * qty
                        st.session_state["inventory"][name]["quantity"] -= need
                    st.success("🔥 تم الخصم!")
                    st.balloons()
                    voice_guide("تم تأكيد البيع وخصم المخزون")
    
    # تبويب الإنتاج اليومي
    with tabs[10]:
        guide_section("الإنتاج اليومي", "سجل بيانات الإنتاج اليومية.")
        
        st.markdown('<div class="section-title">📈 الإنتاج اليومي</div>',
                    unsafe_allow_html=True)
        
        with st.form("daily_prod"):
            c1, c2, c3 = st.columns(3)
            with c1:
                farm = st.text_input("المزرعة:", key="prod_farm")
                d = st.date_input("التاريخ:", datetime.now(), key="prod_date")
            with c2:
                milk = st.number_input("الحليب (لتر):", 0.0, value=0.0,
                                         step=1.0, key="prod_milk")
                eggs = st.number_input("البيض (عدد):", 0, value=0,
                                         step=10, key="prod_eggs")
            with c3:
                wg = st.number_input("زيادة الوزن (كجم):", 0.0,
                                       value=0.0, step=0.5, key="prod_wg")
                dead = st.number_input("النافق:", 0, value=0,
                                        step=1, key="prod_dead")
            
            notes = st.text_area("ملاحظات:", key="prod_notes")
            
            if st.form_submit_button("💾 حفظ السجل"):
                st.session_state["daily_production_log"].append({
                    'farm': farm, 'date': d.isoformat(), 'milk': milk,
                    'eggs': eggs, 'wg': wg, 'dead': dead, 'notes': notes
                })
                st.success("✅ تم الحفظ")
                st.rerun()
        
        if st.session_state["daily_production_log"]:
            st.markdown("#### 📋 السجل")
            df = pd.DataFrame(st.session_state["daily_production_log"])
            st.dataframe(df, use_container_width=True)
    
    # تبويب التقارير
    with tabs[11]:
        guide_section("التقارير", "تقارير الأداء والتحليلات.")
        
        st.markdown('<div class="section-title">📊 التقارير</div>',
                    unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown('<div class="metric-card"><h3>الخلطات</h3><h2>1,247</h2></div>',
                        unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="metric-card"><h3>متوسط التكلفة</h3><h2>$285</h2></div>',
                        unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="metric-card"><h3>التوفير</h3><h2>18%</h2></div>',
                        unsafe_allow_html=True)
        with c4:
            st.markdown('<div class="metric-card"><h3>الرضا</h3><h2>96%</h2></div>',
                        unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("📈 اتجاه الأسعار")
        
        # رسم بياني وهمي للتوضيح
        dates = pd.date_range(start='2024-01-01', periods=12, freq='ME')
        trend = pd.DataFrame({
            'التاريخ': dates,
            'الذرة': [220, 225, 230, 228, 235, 240, 238, 242, 245, 248, 250, 252],
            'الصويا': [440, 445, 442, 448, 450, 455, 452, 458, 460, 462, 465, 468]
        })
        st.line_chart(trend.set_index('التاريخ'))
    
    # تبويب التنبيهات
    with tabs[12]:
        guide_section("التنبيهات", "تنبيهات المخزون والإنتاج.")
        
        st.markdown('<div class="section-title">🔔 التنبيهات</div>',
                    unsafe_allow_html=True)
        
        warns = InventoryManager.check()
        if warns:
            for item, status in warns.items():
                st.markdown(f"""
                <div class="warning-card">
                    <b>⚠️ {item}:</b> {status}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ لا توجد تنبيهات")
    
    # تبويب التعليقات
    with tabs[13]:
        guide_section("التعليقات", "قناة لتبادل الخبرات.")
        
        st.markdown('<div class="section-title">💬 التعليقات</div>',
                    unsafe_allow_html=True)
        
        st.text_area("التعليقات الحالية:",
                      value=st.session_state["shared_comments"],
                      height=200, disabled=True, key="com_display")
        
        new_c = st.text_area("إضافة تعليق:", key="com_new")
        if st.button("➕ نشر", key="com_publish"):
            if new_c:
                st.session_state["shared_comments"] += (
                    f"\n• [المالك {datetime.now().strftime('%Y-%m-%d %H:%M')}]: {new_c}"
                )
                st.success("تم!")
                st.rerun()

# =====================================================================
# تبويب المراجع (للمالك: 14، للزائر: 7)
# =====================================================================
ref_idx = 14 if is_owner else 7
with tabs[ref_idx]:
    guide_section("المراجع العلمية", "مصادر معتمدة في تغذية الحيوان.")
    
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>',
                unsafe_allow_html=True)
    
    refs_data = {
        "🧬 تغذية عامة": [
            ("Animal Nutrition", "McDonald et al.", 2011, "Pearson", "7th Edition"),
            ("Comparative Animal Nutrition", "Cheeke & Dierenfeld", 2010, "CABI", "")
        ],
        "🐄 تغذية المجترات": [
            ("The Ruminant Animal", "Church, D.C.", 1993, "Waveland Press", ""),
            ("Nutrient Requirements of Dairy Cattle", "NRC", 2001, "National Academies", "7th Edition")
        ],
        "🐔 تغذية الدواجن": [
            ("Commercial Poultry Nutrition", "Leeson & Summers", 2009, "Nottingham", "3rd Edition"),
            ("Nutrient Requirements of Poultry", "NRC", 1994, "National Academies", "9th Edition")
        ],
        "🧪 البروتين المهضوم": [
            ("INRA Feeding System for Ruminants", "INRA", 2007, "Wageningen", ""),
            ("Least-Cost Feed Formulation", "Pesti & Miller", 2009, "Univ. Georgia", "")
        ],
        "🐏 تغذية الأغنام والماعز": [
            ("Nutrient Requirements of Small Ruminants", "NRC", 2007, "National Academies", "")
        ],
        "🐴 تغذية الخيول": [
            ("Nutrient Requirements of Horses", "NRC", 2007, "National Academies", "6th Edition")
        ],
        "🐫 تغذية الإبل": [
            ("Camel Nutrition and Feeding", "Faye & Bengoumi", 2018, "FAO", "")
        ],
        "🐟 تغذية الأسماك": [
            ("Fish Nutrition", "Halver & Hardy", 2002, "Academic Press", "3rd Edition")
        ]
    }
    
    for cat, refs in refs_data.items():
        with st.expander(cat):
            for title, authors, year, pub, edition in refs:
                st.markdown(f"""
                <div style="background:#f8f9fa; padding:12px; border-radius:8px;
                            margin-bottom:8px; border-right:4px solid #2e7d32;">
                    <b>{title}</b><br>
                    👤 {authors} | 📅 {year}<br>
                    📚 {pub} {f'| 📖 {edition}' if edition else ''}
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("💡 بنك المعرفة السريع")
    q = st.text_input("اسأل عن مصطلح:", key="kb_q")
    if q:
        kbase = {
            "البروتين المهضوم": "البروتين الذي يستطيع الحيوان هضمه وامتصاصه فعلياً. أدق من البروتين الخام.",
            "معادل النشاء": "مقياس كمية الطاقة في العلف مقارنة بالنشاء النقي.",
            "EPEF": "مؤشر الأداء الأوروبي = (الحيوية × الوزن) / (العمر × FCR) × 100.",
            "FCR": "معامل التحويل الغذائي = العلف المستهلك / الوزن المكتسب.",
            "ADG": "معدل النمو اليومي = الزيادة الوزنية / عدد الأيام."
        }
        for k, v in kbase.items():
            if k in q:
                st.success(f"📖 **{k}**: {v}")
                break
        else:
            st.info("لم أجد إجابة، جرّب كلمة أخرى.")

# =====================================================================
# تبويب المساعدة
# =====================================================================
help_idx = 15 if is_owner else 8
with tabs[help_idx]:
    guide_section("المساعدة", "دليل سريع للمنصة.")
    
    st.markdown('<div class="section-title">💡 المساعدة</div>',
                unsafe_allow_html=True)
    
    st.markdown("""
    ### 🎯 خطوات الاستخدام
    1. اختر نوع الحيوان من تبويب **القطاع الحيواني**
    2. حدد السلالة والمرحلة الإنتاجية
    3. أدخل القياسات الجسدية إن أمكن
    4. اختر المكونات العلفية
    5. اضغط **تشغيل محرك التركيب**
    6. حمّل التقرير PDF أو أرسله للمختبر
    
    ### 🔬 المختبر الذكي
    - ارفع صورة تركيبة لاستخراج القيم تلقائياً
    - أو أدخل البيانات يدوياً
    - قارن النتائج مع المعايير القياسية
    - حمّل تقرير PDF مع الرسم البياني
    
    ### 🧮 معادلات NRC
    - احسب الاحتياجات الغذائية من الوزن والإنتاج
    - مناسب للألبان والتسمين
    
    ### 📞 للدعم الفني
    - البريد: abukram128@gmail.com
    - واتساب: +249123533489
    """)

# =====================================================================
# تبويب دليل المستخدم
# =====================================================================
guide_idx = 16 if is_owner else 9
with tabs[guide_idx]:
    guide_section("دليل المستخدم", "شرح مفصل خطوة بخطوة.")
    
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>',
                unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="book-chapter">📘 الفصل الأول: مقدمة</div>
    <div class="book-body">
    <b>تاور نولجي Tawornology العلمية</b> منصة متكاملة لتركيب الأعلاف
    وإدارة الإنتاج الحيواني، بإشراف {OWNER_NAME} - {OWNER_TITLE}.
    </div>
    
    <div class="book-chapter">📗 الفصل الثاني: تركيب العلف</div>
    <div class="book-body">
    <ol>
    <li>اختر نوع الحيوان (أبقار، أغنام، ماعز، خيول، إبل، دواجن، أسماك)</li>
    <li>حدد السلالة والمرحلة الإنتاجية</li>
    <li>أدخل القياسات الجسدية (محيط الصدر، الطول، العمر)</li>
    <li>اختر المكونات العلفية المطلوبة</li>
    <li>اضغط زر تشغيل المحرك</li>
    <li>ستحصل على الخلطة المثالية بأقل تكلفة</li>
    </ol>
    </div>
    
    <div class="book-chapter">📕 الفصل الثالث: المختبر الذكي</div>
    <div class="book-body">
    ارفع صورة تركيبة، أو أدخل القيم يدوياً، وسيقوم النظام بمقارنتها مع
    المعايير القياسية وإعطائك تقريراً كاملاً مع رسم بياني.
    </div>
    
    <div class="book-chapter">🧮 الفصل الرابع: معادلات NRC</div>
    <div class="book-body">
    احسب الاحتياجات الغذائية الدقيقة بناءً على الوزن الحي والإنتاج الفعلي،
    مع توصيات لنسب DP و SE المثالية.
    </div>
    
    <div class="book-chapter">🍼 الفصل الخامس: بدائل الحليب</div>
    <div class="book-body">
    قم بتركيب بديل حليب للرضاعة حسب العمر والاحتياجات.
    </div>
    
    <div class="book-chapter">🕊️ إهداء</div>
    <div class="book-body">
    هذه المنصة إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b> -
    رحمهما الله وغفر لهما وأسكنهما فسيح جناته.
    </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# تبويب إرسال الكود (للمالك فقط - التبويب الأخير)
# =====================================================================
if is_owner and len(tabs) > 17:
    with tabs[17]:
        guide_section("إرسال الكود", "إرسال السورس كود إلى البريد.")
        
        st.markdown('<div class="section-title">📧 إرسال السورس كود</div>',
                    unsafe_allow_html=True)
        
        st.info(f"هذه الخاصية متاحة للمالك فقط: {OWNER_NAME}")
        
        email_to = st.text_input("البريد المستلم:", value=OWNER_EMAIL,
                                   key="send_email")
        
        if st.session_state.get("need_email_pwd"):
            pwd = st.text_input("🔑 كلمة مرور البريد (App Password):",
                                 type="password", key="email_pwd_input")
            if pwd:
                st.session_state["need_email_pwd"] = False
        
        if st.button("📤 إرسال الكود", type="primary"):
            if not email_to or '@' not in email_to:
                st.warning("⚠️ أدخل بريداً صحيحاً")
            else:
                with st.spinner("جاري الإرسال..."):
                    ok, msg = send_code_to_email(email_to)
                    if ok:
                        st.success(msg)
                        voice_guide("تم إرسال الكود بنجاح")
                    else:
                        st.error(msg)
                   # =====================================================================
# التذييل النهائي
# =====================================================================
st.markdown("---")

st.markdown(f"""
<div style="text-align:center; padding:30px 20px; margin-top:30px;
            background: linear-gradient(135deg, #f5f7fa, #e8f5e9);
            border-radius: 18px; direction:rtl;
            box-shadow: 0 8px 30px rgba(0,0,0,0.08);">

    <h3 style="color:#1b5e20; font-family:'Amiri',serif; margin:10px 0;">
        ✍️ توقيع المشرف العام
    </h3>
    <h2 style="color:#c62828; margin:8px 0; font-size:1.5rem;">
        {OWNER_NAME}
    </h2>
    <p style="color:#1565C0; font-weight:600; margin:5px 0; font-size:1.1rem;">
        🎓 {OWNER_TITLE}
    </p>

    <hr style="border-top:1px solid #ccc; margin:20px 40px;">

    <p style="color:#555; font-size:0.95rem;">
        🌾 <b>تاور نولجي Tawornology العلمية</b> - للانتاج الحيواني وتركيب الاعلاف
    </p>
    <p style="color:#777; font-size:0.85rem;">
        © 2026 - جميع الحقوق محفوظة للمشرف العام
    </p>

    <p style="color:#b39ddb; font-size:0.85rem; font-style:italic;
              margin-top:15px; padding-top:15px;
              border-top:1px dashed #ccc;">
        🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b><br>
        رحمهما الله وغفر لهما وأسكنهما فسيح جناته
    </p>
</div>
""", unsafe_allow_html=True)

# التوقيع الجانبي الثابت
st.markdown(f"""
<div class="mini-signature">
    🌾 تاور نولجي Tawornology<br>
    ✍️ {OWNER_NAME}
</div>
""", unsafe_allow_html=True)

# إغلاق الصندوق الرئيسي
st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# نهاية الكود
# =====================================================================
# بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ
# تم بحمد الله إتمام منصة تاور نولجي Tawornology العلمية - الإصدار 17.0
# 🕊️ اللهم اغفر لوالدي إسماعيل تاور وأختي ابتسام وارحمهما
# =====================================================================     
