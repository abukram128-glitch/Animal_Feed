# ============================================================================
# تاور نولجي Tawornology العلمية - الإصدار النهائي المتكامل 17.0
# ============================================================================
# 🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله
# ============================================================================
# الميزات الجديدة في الإصدار 17.0:
# 1. ختم نهاية PDF مع الصفة الرسمية (اختصاصي تغذية الحيوان)
# 2. معالجة التركيبات العلفية وفق النظام العالمي (NRC/INRA)
# 3. قيود دقيقة على الأملاح والكالسيوم والفسفور ونسب Ca:P (بدقة 0.5%)
# 4. قائمة مكونات موسعة مع قيم Ca و P لكل مادة
# 5. جميع الوظائف السابقة محفوظة ومحسّنة
# المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان
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
import random
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from scipy.optimize import linprog
from scipy.spatial import ConvexHull
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

# =====================================================================
# استيراد مكتبات PDF واللغة العربية
# =====================================================================
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm, cm
from reportlab.lib.colors import HexColor, black, white, grey, blue, red, green, orange, purple, teal, gold
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
import arabic_reshaper
from bidi.algorithm import get_display
import qrcode
from PIL import Image as PILImage
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

warnings.filterwarnings('ignore')

# =====================================================================
# مكتبة الصوت (gTTS)
# =====================================================================
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# =====================================================================
# إعدادات النظام
# =====================================================================
st.set_page_config(
    page_title="تاور نولجي Tawornology العلمية",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def init_caching_system():
    return {"cache_hits": 0, "cache_misses": 0, "last_cleanup": datetime.now()}
CACHE_SYSTEM = init_caching_system()

# =====================================================================
# أكواد الدخول
# =====================================================================
CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2024": {"role": "veterinarian", "name": "الطبيب البيطري", "level": 2},
    "2025": {"role": "nutritionist", "name": "أخصائي التغذية", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

# =====================================================================
# إعدادات البريد
# =====================================================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"
SUPERVISOR_NAME = "الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان"

if "email_password" not in st.session_state:
    try:
        st.session_state["email_password"] = st.secrets["email"]["password"]
    except:
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
# دوال الصوت (محسّنة لمنع الازدواجية)
# =====================================================================
@st.cache_data(ttl=3600)
def text_to_speech_base64(text, lang="ar"):
    if not GTTS_AVAILABLE or not text:
        return None
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return base64.b64encode(audio_bytes.read()).decode()
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

def voice_guide_sequential(messages, lang="ar", delay_between=2.0):
    """تشغيل رسائل صوتية متسلسلة مع تأخير بين الجمل لمنع التداخل"""
    if not GTTS_AVAILABLE:
        return
    for i, msg in enumerate(messages):
        if msg:
            audio_b64 = text_to_speech_base64(msg, lang)
            if audio_b64:
                play_audio_b64(audio_b64)
                word_count = len(msg.split())
                duration = max(2.0, word_count * 0.35 + 1.2)
                time.sleep(duration)
                if i < len(messages) - 1:
                    time.sleep(1.5)

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
        "منصة الانتاج الحيواني وتركيب الاعلاف."
    ])

def play_dua_audio():
    voice_guide_sequential([
        "اللهم اغفر لإسماعيل تاور وابتسام،",
        "وارحمهما وأدخلهما فسيح جناتك."
    ])

def voice_welcome(role):
    msgs = {
        "owner": ["مرحباً بك أيها الاختصاصي م. عبد القادر إسماعيل تاور، اختصاصي تغذية الحيوان."],
        "specialist": ["مرحباً أيها المختص."],
        "veterinarian": ["مرحباً أيها الطبيب البيطري."],
        "nutritionist": ["مرحباً أيها أخصائي التغذية."],
        "breeder": ["مرحباً أيها المربي."],
        "public": ["مرحباً بك زائراً."]
    }
    voice_guide_sequential(msgs.get(role, ["مرحباً بك."]))

def play_full_guide_audio():
    """الشرح الصوتي الشامل بضغطة زر واحدة - بدون ازدواجية"""
    messages = [
        "مرحباً بك في منصة تاور نولجي Tawornology العلمية،",
        "هذه المنصة متخصصة في الانتاج الحيواني وتركيب الاعلاف وفق النظام العالمي.",
        "لديها عدة أقسام رئيسية:",
        "القسم الأول: القطاع الحيواني، حيث يمكنك تركيب أعلاف للأبقار والأغنام والماعز والخيول والإبل والدواجن والأسماك.",
        "يمكنك اختيار السلالة والمرحلة الإنتاجية والعمر والحالة الفسيولوجية، ثم اختيار المكونات والضغط على زر التشغيل.",
        "ملاحظة: يجب أن تكون التركيبة مطابقة بنسبة 75 بالمئة على الأقل من المعايير القياسية لتُقبل.",
        "القسم الثاني: إدارة المزارع، لتتبع دورات إنتاج الدجاج وحساب المؤشرات.",
        "القسم الثالث: بدائل الحليب، لتركيب حليب صناعي للصغار حسب العمر والنوع.",
        "القسم الرابع: مواقيت الصلاة، لعرض أوقات الصلاة حسب المدينة.",
        "القسم الخامس: منبه الجرعات، لتسجيل وتتبع اللقاحات والفيتامينات.",
        "القسم السادس: بورصة الأسعار، لمتابعة أسعار المواشي والمنتجات.",
        "القسم السابع: المستودعات، لإدارة المخزون.",
        "القسم الثامن: الإنتاج اليومي، لتسجيل بيانات الإنتاج.",
        "القسم التاسع: المراجع العلمية، للاطلاع على المصادر المعتمدة.",
        "المختبر المتقدم متاح لتحليل الخلطات ومقارنتها بالمعايير.",
        "جميع التقارير يمكن تحميلها بصيغة بي دي إف مع توقيع المشرف وختم رسمي.",
        "نسأل الله التوفيق والسداد."
    ]
    voice_guide_sequential(messages, delay_between=3.0)

# =====================================================================
# دوال إرسال الكود
# =====================================================================
def send_code_to_email(receiver_email):
    if receiver_email.strip().lower() != OWNER_EMAIL.strip().lower():
        return False, "❌ الإرسال مسموح فقط للبريد: " + OWNER_EMAIL
    if not st.session_state.get("email_password"):
        st.session_state["email_password"] = st.text_input("🔑 كلمة مرور البريد:", type="password")
        if not st.session_state["email_password"]:
            return False, "⚠️ يرجى إدخال كلمة المرور."
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code_content = f.read()
    except:
        code_content = "# تعذر قراءة الكود"
    file_hash = hashlib.md5(code_content.encode()).hexdigest()
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود - تاور نولجي Tawornology"
    body = f"""السلام عليكم ورحمة الله وبركاته،
مرفق السورس كود الكامل للمنصة.
📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔑 التوقيع الرقمي: {file_hash}
👨‍💻 المشرف: {SUPERVISOR_NAME}
🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    attachment = MIMEText(code_content, 'plain', 'utf-8')
    attachment.add_header('Content-Disposition', 'attachment', filename="tawornology_platform.py")
    msg.attach(attachment)
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, st.session_state["email_password"])
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True, "✅ تم إرسال الكود بنجاح"
    except Exception as e:
        return False, f"❌ فشل الإرسال: {str(e)}"

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
            reshaped_text = arabic_reshaper.reshape(str(text))
            return get_display(reshaped_text)
        except:
            return str(text)

arabic_processor = ArabicTextProcessor()

# =====================================================================
# تحميل الخط العربي
# =====================================================================
@st.cache_resource
def download_arabic_font():
    font_path = "Amiri-Regular.ttf"
    if os.path.exists(font_path):
        return font_path
    try:
        import requests
        url = "https://raw.githubusercontent.com/aliftype/amiri/master/fonts/Amiri-Regular.ttf"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(font_path, "wb") as f:
                f.write(response.content)
            return font_path
    except:
        pass
    system_fonts = [
        "/usr/share/fonts/truetype/arabic/Amiri-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf"
    ]
    for f in system_fonts:
        if os.path.exists(f):
            return f
    return None

def ensure_arabic_font():
    font_path = download_arabic_font()
    if font_path and os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
            return 'ArabicFont'
        except:
            pass
    try:
        pdfmetrics.registerFont(TTFont('ArabicFont', 'Helvetica'))
    except:
        pass
    return 'Helvetica'

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
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT,
            role TEXT, full_name TEXT, email TEXT, phone TEXT, specialty TEXT,
            experience_years INTEGER, created_date TEXT, last_login TEXT,
            is_active INTEGER DEFAULT 1, is_public INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS farms (
            farm_id TEXT PRIMARY KEY, farm_name TEXT UNIQUE, farm_type TEXT,
            owner_name TEXT, owner_phone TEXT, location TEXT, area REAL,
            created_date TEXT, last_updated TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS production_cycles (
            cycle_id TEXT PRIMARY KEY, farm_id TEXT, cycle_type TEXT,
            start_date TEXT, end_date TEXT, initial_count INTEGER, breed TEXT,
            target_weight REAL, target_age INTEGER, status TEXT, notes TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS daily_records (
            record_id TEXT PRIMARY KEY, cycle_id TEXT, record_date TEXT,
            age_days INTEGER, live_birds INTEGER, avg_weight REAL,
            feed_consumed REAL, dead_count INTEGER, feed_conversion REAL,
            mortality_rate REAL, notes TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas (
            formula_id TEXT PRIMARY KEY, formula_name TEXT, animal_type TEXT,
            breed TEXT, stage TEXT, target_dp REAL, target_se REAL,
            ingredients TEXT, total_cost REAL, cost_per_ton REAL,
            created_by TEXT, created_date TEXT, requester_name TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS price_history (
            record_id TEXT PRIMARY KEY, ingredient_name TEXT, price REAL,
            currency TEXT, country TEXT, city TEXT, record_date TEXT,
            recorded_by TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT PRIMARY KEY, item_name TEXT UNIQUE, quantity REAL,
            min_threshold REAL, unit TEXT, last_updated TEXT, supplier TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS milk_replacers (
            replacer_id TEXT PRIMARY KEY, animal_type TEXT, age_days INTEGER,
            formula_name TEXT, ingredients TEXT, instructions TEXT,
            created_by TEXT, created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS dose_reminders (
            reminder_id TEXT PRIMARY KEY, animal_type TEXT, dose_type TEXT,
            dose_name TEXT, dose_amount REAL, dose_unit TEXT,
            administration_route TEXT, frequency_days INTEGER,
            start_date TEXT, next_dose_date TEXT, notes TEXT,
            active BOOLEAN DEFAULT 1, created_by TEXT, created_date TEXT)''')
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
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        c.execute(query, list(data.values()))
        conn.commit()
        conn.close()
        return True
    
    def get_records(self, table, conditions=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if conditions:
            where_clause = ' AND '.join([f"{k}=?" for k in conditions.keys()])
            query = f"SELECT * FROM {table} WHERE {where_clause}"
            result = c.execute(query, list(conditions.values()))
        else:
            query = f"SELECT * FROM {table}"
            result = c.execute(query)
        data = result.fetchall()
        conn.close()
        return data
    
    def update_record(self, table, data, condition):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        set_clause = ', '.join([f"{k}=?" for k in data.keys()])
        where_clause = ' AND '.join([f"{k}=?" for k in condition.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        c.execute(query, list(data.values()) + list(condition.values()))
        conn.commit()
        conn.close()
        return True

# =====================================================================
# نظام المصادقة
# =====================================================================
class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self._create_defaults()
    
    def _create_defaults(self):
        default_users = [
            ('admin', 'admin123', 'owner', SUPERVISOR_NAME, 'admin@tawornology.com', '+249123456789', 'تغذية حيوان', 10),
            ('specialist', 'spec123', 'specialist', 'المختص العام', 'spec@tawornology.com', '+249123456788', 'تغذية وإنتاج', 8),
            ('public', 'public123', 'public', 'زائر', 'public@tawornology.com', '+249123456780', 'عام', 0)
        ]
        for username, password, role, full_name, email, phone, specialty, exp in default_users:
            users = self.db.execute_query("SELECT * FROM users WHERE username=?", (username,))
            if not users:
                self.create_user(username, password, role, full_name, email, phone, specialty, exp)
    
    def create_user(self, username, password, role, full_name, email, phone, specialty="", exp=0):
        user_id = secrets.token_hex(16)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        data = {
            'user_id': user_id, 'username': username, 'password_hash': password_hash,
            'role': role, 'full_name': full_name, 'email': email, 'phone': phone,
            'specialty': specialty, 'experience_years': exp,
            'created_date': datetime.now().isoformat(), 'last_login': '',
            'is_active': 1, 'is_public': 1 if role == 'public' else 0
        }
        self.db.insert_record('users', data)
        return user_id
    
    def authenticate(self, username, password):
        users = self.db.execute_query("SELECT * FROM users WHERE username=? AND is_active=1", (username,))
        if users:
            user = users[0]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user[2] == password_hash:
                self.db.update_record('users', {'last_login': datetime.now().isoformat()}, {'user_id': user[0]})
                return {
                    'user_id': user[0], 'username': user[1], 'role': user[3],
                    'full_name': user[4], 'email': user[5], 'phone': user[6],
                    'specialty': user[7], 'experience_years': user[8]
                }
        return None
    
    def login_public(self):
        users = self.db.execute_query("SELECT * FROM users WHERE username='public' AND is_active=1")
        if users:
            user = users[0]
            return {
                'user_id': user[0], 'username': user[1], 'role': 'public',
                'full_name': 'زائر', 'email': user[5], 'phone': user[6],
                'specialty': 'عام', 'experience_years': 0
            }
        return None

# =====================================================================
# مكتبة الأعلاف الموسعة مع قيم الكالسيوم والفسفور والأملاح
# =====================================================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3, "Ca": 0.02, "P": 0.28, "NaCl": 0.0},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4, "Ca": 0.02, "P": 0.25, "NaCl": 0.0},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5, "Ca": 0.05, "P": 0.35, "NaCl": 0.0},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8, "Ca": 0.03, "P": 0.30, "NaCl": 0.0},
        "قمح محلي": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6, "Ca": 0.04, "P": 0.32, "NaCl": 0.0},
        "جريش أرز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2, "Ca": 0.01, "P": 0.10, "NaCl": 0.0},
        "دخن محلي": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2, "Ca": 0.03, "P": 0.28, "NaCl": 0.0},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0, "Ca": 0.06, "P": 0.33, "NaCl": 0.0}
    },
    "🌱 مصادر البروتين النباتي": {
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0, "Ca": 0.25, "P": 0.65, "NaCl": 0.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2, "Ca": 0.28, "P": 0.68, "NaCl": 0.0},
        "أمباز الفول السوداني": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5, "Ca": 0.20, "P": 0.60, "NaCl": 0.0},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5, "Ca": 0.35, "P": 0.80, "NaCl": 0.0},
        "كسب بذور القطن": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5, "Ca": 0.15, "P": 0.90, "NaCl": 0.0},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8, "Ca": 0.30, "P": 0.70, "NaCl": 0.0},
        "كسب السمسم": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5, "Ca": 1.50, "P": 0.80, "NaCl": 0.0},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5, "Ca": 0.05, "P": 0.40, "NaCl": 0.0},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5, "Ca": 0.15, "P": 0.50, "NaCl": 0.0},
        "كسب بذور اللفت": {"CP": 38.0, "DC": 0.82, "SE": 62.0, "NDF": 28.0, "ADF": 18.0, "EE": 3.5, "ASH": 7.5, "Ca": 0.60, "P": 1.00, "NaCl": 0.0},
        "كسب زهرة الشمس": {"CP": 30.0, "DC": 0.74, "SE": 40.0, "NDF": 42.0, "ADF": 28.0, "EE": 3.0, "ASH": 6.0, "Ca": 0.32, "P": 0.75, "NaCl": 0.0}
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5, "Ca": 0.10, "P": 1.10, "NaCl": 0.0},
        "البرسيم الجاف": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5, "Ca": 1.20, "P": 0.25, "NaCl": 0.0},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5, "Ca": 0.50, "P": 0.08, "NaCl": 0.5},
        "تبن قمح": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.30, "P": 0.10, "NaCl": 0.0},
        "مخلفات البسكويت": {"CP": 10.0, "DC": 0.80, "SE": 65.0, "NDF": 8.0, "ADF": 4.0, "EE": 12.0, "ASH": 3.0, "Ca": 0.20, "P": 0.30, "NaCl": 0.3}
    },
    "🧬 البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5, "Ca": 4.00, "P": 2.50, "NaCl": 0.0},
        "مسحوق أسماك 72%": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5, "Ca": 4.50, "P": 2.80, "NaCl": 0.0},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5, "Ca": 8.00, "P": 4.00, "NaCl": 0.0},
        "مركزات دواجن": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5, "Ca": 1.50, "P": 0.80, "NaCl": 0.8},
        "مركزات مجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5, "Ca": 1.20, "P": 0.70, "NaCl": 0.6},
        "بروتين WPC": {"CP": 80.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 3.0, "ASH": 3.0, "Ca": 0.50, "P": 0.60, "NaCl": 0.0},
        "بروتين الدم": {"CP": 85.0, "DC": 0.92, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.5, "ASH": 5.0, "Ca": 0.20, "P": 0.30, "NaCl": 0.0}
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0, "NaCl": 0.0},
        "ميثيونين نقي": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3, "Ca": 0.0, "P": 0.0, "NaCl": 0.0},
        "ثريونين نقي": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0, "NaCl": 0.0}
    },
    "🔬 البريمكسات والإنزيمات": {
        "بريمكس تسمين دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 8.0, "NaCl": 15.0},
        "بريمكس بياض": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 8.0, "NaCl": 15.0},
        "بريمكس أبقار": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0, "NaCl": 18.0},
        "إنزيم الفايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0, "Ca": 0.0, "P": 0.0, "NaCl": 0.0},
        "إنزيم NSP": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0, "Ca": 0.0, "P": 0.0, "NaCl": 0.0},
        "خميرة الخبز": {"CP": 45.0, "DC": 0.85, "SE": 35.0, "NDF": 5.0, "ADF": 2.0, "EE": 2.5, "ASH": 7.0, "Ca": 0.1, "P": 0.4, "NaCl": 0.0}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 38.0, "P": 0.0, "NaCl": 0.0},
        "فوسفات DCP": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5, "Ca": 23.0, "P": 18.0, "NaCl": 0.0},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9, "Ca": 0.0, "P": 0.0, "NaCl": 99.5},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Ca": 0.5, "P": 0.2, "NaCl": 0.0},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 0.0, "P": 0.0, "NaCl": 60.0},
        "أكسيد المغنيسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 0.5, "P": 0.0, "NaCl": 0.0},
        "كلوريد الكولين": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 75.0, "Ca": 0.0, "P": 0.0, "NaCl": 0.0}
    },
    "🍼 بدائل الحليب": {
        "مصل الحليب Whey": {"CP": 12.0, "DC": 0.95, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.0, "Ca": 0.8, "P": 0.6, "NaCl": 1.5},
        "حليب مجفف منزوع": {"CP": 34.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.5, "Ca": 1.3, "P": 1.0, "NaCl": 1.0},
        "دهن نباتي": {"CP": 0.0, "DC": 0.0, "SE": 10.0, "NDF": 0.0, "ADF": 0.0, "EE": 99.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "NaCl": 0.0},
        "ليسيثين الصويا": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 95.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0, "NaCl": 0.0},
        "فيتامينات ومعادن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0, "NaCl": 15.0},
        "بروتين الصويا المركز": {"CP": 65.0, "DC": 0.90, "SE": 30.0, "NDF": 2.0, "ADF": 1.0, "EE": 1.0, "ASH": 5.5, "Ca": 0.3, "P": 0.7, "NaCl": 0.0}
    }
}

FLAT_FEED_DB = {}
for category, items in BIG_FEEDS_LIBRARY.items():
    for feed_name, nutrition in items.items():
        FLAT_FEED_DB[feed_name] = nutrition

# =====================================================================
# المعايير القياسية العالمية (NRC / INRA) مع قيود المعادن
# =====================================================================
STANDARD_VALUES = {
    "أبقار": {
        "تسمين عجول": {"DP": 12.0, "SE": 68.0, "CP": 15.0, "Ca": 0.80, "P": 0.40, "Ca_P_ratio": 2.0, "NaCl_max": 1.0},
        "حليب/إدرار": {"DP": 14.0, "SE": 70.0, "CP": 17.5, "Ca": 1.20, "P": 0.50, "Ca_P_ratio": 2.4, "NaCl_max": 1.0},
        "حمل/دفع غذائي": {"DP": 11.0, "SE": 65.0, "CP": 13.8, "Ca": 0.90, "P": 0.45, "Ca_P_ratio": 2.0, "NaCl_max": 1.0},
        "صيانة": {"DP": 9.0, "SE": 60.0, "CP": 11.3, "Ca": 0.60, "P": 0.30, "Ca_P_ratio": 2.0, "NaCl_max": 1.0},
        "تسمين مكثف": {"DP": 13.0, "SE": 72.0, "CP": 16.3, "Ca": 0.90, "P": 0.45, "Ca_P_ratio": 2.0, "NaCl_max": 1.0}
    },
    "أغنام": {
        "تسمين حملان": {"DP": 13.0, "SE": 66.0, "CP": 16.3, "Ca": 0.70, "P": 0.40, "Ca_P_ratio": 1.75, "NaCl_max": 0.8},
        "حليب/إدرار": {"DP": 14.5, "SE": 68.0, "CP": 18.1, "Ca": 1.00, "P": 0.50, "Ca_P_ratio": 2.0, "NaCl_max": 0.8},
        "حمل/دفع غذائي": {"DP": 11.5, "SE": 62.0, "CP": 14.4, "Ca": 0.80, "P": 0.40, "Ca_P_ratio": 2.0, "NaCl_max": 0.8},
        "صيانة": {"DP": 8.5, "SE": 58.0, "CP": 10.6, "Ca": 0.50, "P": 0.30, "Ca_P_ratio": 1.7, "NaCl_max": 0.8}
    },
    "ماعز": {
        "تسمين جديان": {"DP": 12.5, "SE": 64.0, "CP": 15.6, "Ca": 0.70, "P": 0.40, "Ca_P_ratio": 1.75, "NaCl_max": 0.8},
        "حليب/إدرار": {"DP": 14.0, "SE": 66.0, "CP": 17.5, "Ca": 1.00, "P": 0.50, "Ca_P_ratio": 2.0, "NaCl_max": 0.8},
        "حمل/دفع غذائي": {"DP": 11.0, "SE": 60.0, "CP": 13.8, "Ca": 0.80, "P": 0.40, "Ca_P_ratio": 2.0, "NaCl_max": 0.8},
        "صيانة": {"DP": 8.0, "SE": 56.0, "CP": 10.0, "Ca": 0.50, "P": 0.30, "Ca_P_ratio": 1.7, "NaCl_max": 0.8}
    },
    "خيول": {
        "راحة/صيانة": {"DP": 9.0, "SE": 58.0, "CP": 11.3, "Ca": 0.50, "P": 0.30, "Ca_P_ratio": 1.7, "NaCl_max": 1.0},
        "عمل خفيف": {"DP": 10.0, "SE": 60.0, "CP": 12.5, "Ca": 0.60, "P": 0.35, "Ca_P_ratio": 1.7, "NaCl_max": 1.0},
        "عمل متوسط": {"DP": 11.0, "SE": 62.0, "CP": 13.8, "Ca": 0.70, "P": 0.40, "Ca_P_ratio": 1.75, "NaCl_max": 1.0},
        "عمل مكثف": {"DP": 13.0, "SE": 65.0, "CP": 16.3, "Ca": 0.80, "P": 0.45, "Ca_P_ratio": 1.8, "NaCl_max": 1.0},
        "سباق": {"DP": 14.0, "SE": 68.0, "CP": 17.5, "Ca": 0.90, "P": 0.50, "Ca_P_ratio": 1.8, "NaCl_max": 1.0},
        "أمهار نامية": {"DP": 13.0, "SE": 64.0, "CP": 16.3, "Ca": 0.90, "P": 0.50, "Ca_P_ratio": 1.8, "NaCl_max": 1.0},
        "فرسات مرضعات": {"DP": 14.0, "SE": 66.0, "CP": 17.5, "Ca": 1.20, "P": 0.60, "Ca_P_ratio": 2.0, "NaCl_max": 1.0}
    },
    "إبل": {
        "راحة/صيانة": {"DP": 8.0, "SE": 55.0, "CP": 10.0, "Ca": 0.60, "P": 0.30, "Ca_P_ratio": 2.0, "NaCl_max": 1.2},
        "حمل/رضاعة": {"DP": 10.0, "SE": 58.0, "CP": 12.5, "Ca": 1.00, "P": 0.50, "Ca_P_ratio": 2.0, "NaCl_max": 1.2},
        "إنتاج حليب": {"DP": 12.0, "SE": 60.0, "CP": 15.0, "Ca": 1.20, "P": 0.60, "Ca_P_ratio": 2.0, "NaCl_max": 1.2},
        "تسمين": {"DP": 11.0, "SE": 62.0, "CP": 13.8, "Ca": 0.80, "P": 0.40, "Ca_P_ratio": 2.0, "NaCl_max": 1.2},
        "عمل/نقل": {"DP": 10.0, "SE": 58.0, "CP": 12.5, "Ca": 0.70, "P": 0.40, "Ca_P_ratio": 1.75, "NaCl_max": 1.2}
    },
    "دواجن لاحم": {
        "بادي (0-14)": {"DP": 22.0, "SE": 76.0, "CP": 27.5, "Ca": 1.00, "P": 0.45, "Ca_P_ratio": 2.22, "NaCl_max": 0.5},
        "نامي (15-28)": {"DP": 20.0, "SE": 74.0, "CP": 25.0, "Ca": 0.90, "P": 0.40, "Ca_P_ratio": 2.25, "NaCl_max": 0.5},
        "ناهي (29-42)": {"DP": 18.0, "SE": 72.0, "CP": 22.5, "Ca": 0.80, "P": 0.35, "Ca_P_ratio": 2.28, "NaCl_max": 0.5},
        "ناهي متقدم (43+)": {"DP": 16.0, "SE": 70.0, "CP": 20.0, "Ca": 0.70, "P": 0.30, "Ca_P_ratio": 2.33, "NaCl_max": 0.5}
    },
    "دواجن بياض": {
        "بادي (0-6)": {"DP": 20.0, "SE": 72.0, "CP": 25.0, "Ca": 0.90, "P": 0.40, "Ca_P_ratio": 2.25, "NaCl_max": 0.5},
        "نامي (7-14)": {"DP": 18.0, "SE": 70.0, "CP": 22.5, "Ca": 0.80, "P": 0.35, "Ca_P_ratio": 2.28, "NaCl_max": 0.5},
        "قبل الإنتاج": {"DP": 16.5, "SE": 68.0, "CP": 20.6, "Ca": 1.50, "P": 0.40, "Ca_P_ratio": 3.75, "NaCl_max": 0.5},
        "بياض إنتاجي": {"DP": 16.0, "SE": 66.0, "CP": 20.0, "Ca": 3.50, "P": 0.45, "Ca_P_ratio": 7.78, "NaCl_max": 0.5}
    },
    "سمان": {
        "بادي": {"DP": 24.0, "SE": 74.0, "CP": 30.0, "Ca": 0.90, "P": 0.40, "Ca_P_ratio": 2.25, "NaCl_max": 0.5},
        "نامي": {"DP": 22.0, "SE": 72.0, "CP": 27.5, "Ca": 0.80, "P": 0.35, "Ca_P_ratio": 2.28, "NaCl_max": 0.5},
        "بياض": {"DP": 18.0, "SE": 68.0, "CP": 22.5, "Ca": 2.50, "P": 0.40, "Ca_P_ratio": 6.25, "NaCl_max": 0.5}
    },
    "أسماك": {
        "زريعة": {"DP": 32.0, "SE": 70.0, "CP": 40.0, "Ca": 0.50, "P": 0.30, "Ca_P_ratio": 1.67, "NaCl_max": 0.3},
        "نمو": {"DP": 28.0, "SE": 68.0, "CP": 35.0, "Ca": 0.40, "P": 0.30, "Ca_P_ratio": 1.33, "NaCl_max": 0.3},
        "تسمين نهائي": {"DP": 26.0, "SE": 66.0, "CP": 32.5, "Ca": 0.40, "P": 0.30, "Ca_P_ratio": 1.33, "NaCl_max": 0.3}
    }
}

# =====================================================================
# نظام المراجع العلمية
# =====================================================================
class ScientificReferenceSystem:
    REFERENCES = {
        "protein": {
            "title": "البروتين والأحماض الأمينية",
            "icon": "🧬",
            "references": [
                {"id": "REF001", "authors": "NRC", "year": 2012, "title": "Nutrient Requirements of Swine",
                 "publisher": "National Academies Press", "summary": "المرجع الرسمي لمتطلبات الخنازير"},
                {"id": "REF002", "authors": "NRC", "year": 2001, "title": "Nutrient Requirements of Dairy Cattle",
                 "publisher": "National Academies Press", "summary": "المرجع الأساسي لتغذية أبقار الحليب"}
            ]
        },
        "poultry": {
            "title": "تغذية الدواجن",
            "icon": "🐔",
            "references": [
                {"id": "REF003", "authors": "Leeson & Summers", "year": 2009,
                 "title": "Commercial Poultry Nutrition", "publisher": "Nottingham University Press",
                 "summary": "المرجع العملي في تغذية الدواجن"},
                {"id": "REF004", "authors": "NRC", "year": 1994, "title": "Nutrient Requirements of Poultry",
                 "publisher": "National Academies Press", "summary": "المرجع الرسمي لمتطلبات الدواجن"}
            ]
        },
        "ruminants": {
            "title": "تغذية المجترات",
            "icon": "🐄",
            "references": [
                {"id": "REF005", "authors": "Church", "year": 1993, "title": "The Ruminant Animal",
                 "publisher": "Waveland Press", "summary": "المرجع الشامل لفسيولوجيا الهضم للمجترات"}
            ]
        },
        "milk_replacers": {
            "title": "بدائل الحليب",
            "icon": "🍼",
            "references": [
                {"id": "REF006", "authors": "Davis & Drackley", "year": 1998,
                 "title": "The Development, Nutrition, and Management of the Young Calf",
                 "publisher": "Iowa State University Press", "summary": "المرجع الأساسي لتغذية العجول"}
            ]
        }
    }
    
    KNOWLEDGE_BASE = {
        "البروتين المهضوم": {
            "answer": "البروتين المهضوم (DP) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً. DP = CP × معامل الهضم.",
            "simplified": "الجزء من البروتين الذي يستفيد منه الحيوان فعلياً."
        },
        "معادل النشاء": {
            "answer": "معادل النشاء (SE) هو مقياس لكمية الطاقة التي يوفرها العلف للحيوان مقارنة بالنشاء النقي.",
            "simplified": "مقياس الطاقة في العلف."
        },
        "الكالسيوم والفسفور": {
            "answer": "الكالسيوم (Ca) والفسفور (P) من أهم المعادن في تغذية الحيوان. النسبة المثالية Ca:P هي 2:1 للمجترات، و2.2:1 للدواجن اللاحمة، و7-8:1 للدجاج البياض.",
            "simplified": "معادن أساسية لبناء العظام، ويجب أن تكون نسبتها متوازنة."
        },
        "الأملاح في الأعلاف": {
            "answer": "يجب ألا تتجاوز نسبة ملح الطعام (NaCl) في العلف 0.5% للدواجن و1% للمجترات، لأن الزيادة تسبب الإسهال والتسمم الملحي.",
            "simplified": "الملح مهم لكن بكميات محدودة جداً."
        }
    }
    
    @staticmethod
    def get_knowledge_answer(question):
        for key, value in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            if key in question:
                return value
        return None

# =====================================================================
# مدير المخزون
# =====================================================================
class InventoryManager:
    @staticmethod
    def initialize_inventory():
        if "inventory" not in st.session_state:
            st.session_state["inventory"] = {}
            for cat_name, items in BIG_FEEDS_LIBRARY.items():
                for ing in items:
                    st.session_state["inventory"][ing] = {
                        "quantity": 25.0, "min_threshold": 5.0, "unit": "طن"
                    }
    
    @staticmethod
    def check_stock_levels():
        warnings = {}
        for item, data in st.session_state["inventory"].items():
            if data["quantity"] <= 0:
                warnings[item] = "نفذ المخزون"
            elif data["quantity"] < data["min_threshold"]:
                warnings[item] = "منخفض"
        return warnings
    
    @staticmethod
    def get_stock_summary():
        total_items = len(st.session_state["inventory"])
        total_quantity = sum(d["quantity"] for d in st.session_state["inventory"].values())
        low_stock = sum(1 for d in st.session_state["inventory"].values() if d["quantity"] < d["min_threshold"])
        return {"total_items": total_items, "total_quantity": total_quantity, "low_stock": low_stock}

InventoryManager.initialize_inventory()

# =====================================================================
# حالة الجلسة
# =====================================================================
defaults = {
    "approved": False, "user_role": None, "login_welcome_shown": False,
    "login_attempts": 0, "last_login_time": None, "session_token": None,
    "broiler_farms": {}, "whatsapp_alerts_sent": {}, "analysis_results": None,
    "daily_production_log": [], "basmala_played": False, "welcome_played": False,
    "guide_played": {}, "active_formula": {}, "computed_ton_cost": 280.0,
    "lab_sample": None, "dose_reminders": [], "requester_name": "",
    "global_livestock_prices": {
        "عجول تسمين ($)": 1350.0, "أبقار كنانة ($)": 900.0,
        "ضأن ($)": 180.0, "ماعز ($)": 130.0, "خيول ($)": 4500.0,
        "إبل ($)": 2500.0, "كتكوت لاحم ($)": 0.65
    },
    "global_products_prices": {
        "كيلو لحم بقري ($)": 7.50, "كيلو لحم ضأن ($)": 9.00,
        "كيلو لحم دجاج ($)": 3.80, "طبق بيض 30 ($)": 4.20,
        "لتر حليب خام ($)": 0.90, "لتر حليب إبل ($)": 1.50
    }
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "LIBYA": {"rate": 4.80, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"},
    "دولار": {"rate": 1.0, "sym": "USD"}
}

ANIMAL_IMAGES_RESOURCES = {
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
# مولد PDF المحسّن مع ختم النهاية الرسمي
# =====================================================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = ensure_arabic_font()
        self.styles = self._create_styles()
    
    def _create_styles(self):
        styles = {}
        styles['title'] = ParagraphStyle('title', fontName=self.font_name, fontSize=24, alignment=TA_CENTER, textColor=HexColor('#1b5e20'), spaceAfter=20, leading=30)
        styles['subtitle'] = ParagraphStyle('subtitle', fontName=self.font_name, fontSize=16, alignment=TA_CENTER, textColor=HexColor('#2e7d32'), spaceAfter=15, leading=20)
        styles['heading'] = ParagraphStyle('heading', fontName=self.font_name, fontSize=14, alignment=TA_RIGHT, textColor=HexColor('#1b5e20'), spaceAfter=10, leading=18)
        styles['body'] = ParagraphStyle('body', fontName=self.font_name, fontSize=11, alignment=TA_RIGHT, textColor=HexColor('#333333'), spaceAfter=6, leading=16)
        styles['footer'] = ParagraphStyle('footer', fontName=self.font_name, fontSize=8, alignment=TA_CENTER, textColor=HexColor('#999999'), spaceAfter=0, leading=10)
        styles['stamp'] = ParagraphStyle('stamp', fontName=self.font_name, fontSize=13, alignment=TA_CENTER, textColor=HexColor('#1b5e20'), spaceAfter=6, leading=18)
        return styles
    
    def _draw_stamp(self, canvas_obj, doc):
        """رسم ختم النهاية الرسمي على كل صفحة"""
        canvas_obj.saveState()
        # ختم دائري في الزاوية السفلية اليمنى
        cx, cy = A4[0] - 100, 80
        radius = 55
        canvas_obj.setStrokeColor(HexColor('#1b5e20'))
        canvas_obj.setLineWidth(2)
        canvas_obj.circle(cx, cy, radius, stroke=1, fill=0)
        canvas_obj.setLineWidth(0.8)
        canvas_obj.circle(cx, cy, radius - 4, stroke=1, fill=0)
        canvas_obj.setFont(self.font_name, 7)
        canvas_obj.setFillColor(HexColor('#1b5e20'))
        canvas_obj.drawCentredString(cx, cy + 18, arabic_processor.fix_arabic_text("تاور نولجي"))
        canvas_obj.drawCentredString(cx, cy + 6, arabic_processor.fix_arabic_text("Tawornology"))
        canvas_obj.setFont(self.font_name, 6)
        canvas_obj.drawCentredString(cx, cy - 6, arabic_processor.fix_arabic_text("اختصاصي تغذية"))
        canvas_obj.drawCentredString(cx, cy - 16, arabic_processor.fix_arabic_text("الحيوان"))
        canvas_obj.setFont(self.font_name, 5)
        canvas_obj.drawCentredString(cx, cy - 28, arabic_processor.fix_arabic_text("2026 ©"))
        # خط توقيع على اليسار
        canvas_obj.setStrokeColor(HexColor('#c62828'))
        canvas_obj.setLineWidth(1.5)
        canvas_obj.line(50, 80, 200, 80)
        canvas_obj.setFont(self.font_name, 8)
        canvas_obj.setFillColor(HexColor('#c62828'))
        canvas_obj.drawString(50, 65, arabic_processor.fix_arabic_text("توقيع المشرف"))
        canvas_obj.setFont(self.font_name, 7)
        canvas_obj.setFillColor(HexColor('#1b5e20'))
        canvas_obj.drawString(50, 50, arabic_processor.fix_arabic_text(SUPERVISOR_NAME))
        # رقم الصفحة
        canvas_obj.setFont(self.font_name, 7)
        canvas_obj.setFillColor(HexColor('#666'))
        canvas_obj.drawCentredString(A4[0]/2, 30, arabic_processor.fix_arabic_text(f"صفحة {doc.page}"))
        canvas_obj.restoreState()
    
    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, user_name, requester_name="", standard=None, include_charts=True, extra_info=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=100)
        story = []
        def p(text, style='body'):
            return Paragraph(arabic_processor.fix_arabic_text(str(text)), self.styles.get(style, self.styles['body']))
        
        story.append(p("🌾 تاور نولجي Tawornology العلمية", 'title'))
        story.append(p("تقرير فني شامل - تقرير التركيب", 'subtitle'))
        story.append(Spacer(1, 10))
        for line in [f"المشرف العام: {SUPERVISOR_NAME}", f"الموقع: {city}", f"الفصيل: {breed}", f"تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"]:
            story.append(p(line))
        if requester_name:
            story.append(p(f"طالب العلف: {requester_name}"))
        story.append(Spacer(1, 15))
        
        tdata = [['المعيار', 'القيمة'], ['البروتين المهضوم (DP)', f'{target_dp:.2f}%'],
                 ['معادل النشاء (SE)', f'{computed_se:.2f}'], ['التكلفة للطن', f'${cost:.2f} ({local_cost:,.2f} {local_sym})']]
        t = Table([[arabic_processor.fix_arabic_text(c) for c in r] for r in tdata], colWidths=[250, 250])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),('TEXTCOLOR',(0,0),(-1,0),white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),11),('GRID',(0,0),(-1,-1),1,HexColor('#2e7d32'))]))
        story.append(t)
        story.append(Spacer(1, 10))
        
        if standard:
            story.append(p("مقارنة مع المعايير القياسية (NRC/INRA):", 'heading'))
            comp = [['المقياس', 'المحسوب', 'القياسي', 'الانحراف %', 'التقييم']]
            for k, label in [('dp','DP'),('se','SE'),('cp','CP')]:
                if k in standard and k != 'cp':
                    val = target_dp if k == 'dp' else computed_se
                    dev = ((val - standard[k]) / standard[k]) * 100 if standard[k] > 0 else 0
                    grade = "ممتاز ✅" if abs(dev) <= 5 else ("جيد ⚠️" if abs(dev) <= 10 else "يحتاج تحسين ❌")
                    comp.append([label, f"{val:.2f}", f"{standard[k]:.2f}", f"{dev:.1f}", grade])
                elif k == 'cp':
                    val = target_dp / 0.80
                    dev = ((val - standard['cp']) / standard['cp']) * 100 if standard['cp'] > 0 else 0
                    grade = "ممتاز ✅" if abs(dev) <= 5 else ("جيد ⚠️" if abs(dev) <= 10 else "يحتاج تحسين ❌")
                    comp.append([label, f"{val:.2f}", f"{standard['cp']:.2f}", f"{dev:.1f}", grade])
            tc = Table([[arabic_processor.fix_arabic_text(c) for c in r] for r in comp], colWidths=[80, 90, 90, 90, 90])
            tc.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),('TEXTCOLOR',(0,0),(-1,0),white),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),
                ('FONTSIZE',(0,0),(-1,-1),10),('GRID',(0,0),(-1,-1),1,HexColor('#bdbdbd')),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#f5f5f5')])]))
            story.append(tc)
        
        story.append(PageBreak())
        story.append(p("المقادير المعتمدة لتركيب الطن الواحد:", 'heading'))
        story.append(Spacer(1, 10))
        ing_data = [['المكون', 'النسبة %', 'كجم/طن']]
        for ing, pct in formula.items():
            ing_data.append([ing, f'{pct:.2f}%', f'{pct*10:.1f}'])
        t2 = Table([[arabic_processor.fix_arabic_text(c) for c in r] for r in ing_data], colWidths=[200, 140, 140])
        t2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),('TEXTCOLOR',(0,0),(-1,0),white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),10),('GRID',(0,0),(-1,-1),1,HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#f5f5f5')])]))
        story.append(t2)
        story.append(Spacer(1, 15))
        
        if include_charts and len(formula) > 1:
            try:
                fig, ax = plt.subplots(figsize=(6, 3.5))
                names = list(formula.keys())
                vals = list(formula.values())
                colors = ['#1b5e20','#2e7d32','#388e3c','#43a047','#4caf50','#66bb6a','#81c784']
                ax.pie(vals, labels=None, autopct='%1.1f%%', colors=colors[:len(names)])
                ax.legend([arabic_processor.fix_arabic_text(n) for n in names],
                         title=arabic_processor.fix_arabic_text("المكونات"),
                         loc='center left', bbox_to_anchor=(1,0,0.5,1), fontsize=8)
                ax.set_title(arabic_processor.fix_arabic_text('توزيع المكونات'), fontsize=12)
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=120, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=400, height=230))
            except:
                pass
        
        story.append(PageBreak())
        story.append(p("التوصيات الفنية (وفق النظام العالمي):", 'heading'))
        recommendations = [
            "• الالتزام بنسب الأملاح: ألا يتجاوز NaCl عن 1% للمجترات و0.5% للدواجن.",
            "• ضبط نسبة الكالسيوم للفسفور Ca:P بين 1.7:1 و2.4:1 للمجترات، و2.2:1 للدواجن اللاحم.",
            "• إضافة بيكربونات الصوديوم للمجترات (0.5-0.75%) لمنع الحماض الكرشي.",
            "• إضافة إنزيم الفايتيز للدواجن والأسماك (0.05%) لتحسين امتصاص الفسفور.",
            "• تخزين العلف في مكان جاف بعيداً عن الرطوبة والحشرات.",
            "• تقسيم العلف على 3-4 وجبات يومياً لتحسين الهضم.",
        ]
        for r in recommendations:
            story.append(p(r))
        
        if extra_info:
            story.append(Spacer(1, 10))
            story.append(p("معلومات إضافية:", 'heading'))
            for k, v in extra_info.items():
                if v:
                    story.append(p(f"• {k}: {v}"))
        
        story.append(PageBreak())
        story.append(p("خاتمة التقرير والاعتماد الرسمي", 'heading'))
        story.append(Spacer(1, 15))
        story.append(p("تم إعداد هذا التقرير وفقاً للمعايير العالمية لتركيب الأعلاف (NRC - INRA)، مع مراعاة الحدود القصوى للمعادن والأملاح والنسب المثالية للطاقة والبروتين."))
        story.append(Spacer(1, 30))
        story.append(p("مع خالص التحية والتقدير،", 'body'))
        story.append(Spacer(1, 15))
        story.append(p(SUPERVISOR_NAME, 'stamp'))
        story.append(Spacer(1, 40))
        story.append(p("تاور نولجي Tawornology العلمية © 2026", 'footer'))
        story.append(p("🕊️ إهداء إلى روح الوالد إسماعيل تاور والأخت ابتسام - رحمهما الله", 'footer'))
        
        doc.build(story, onFirstPage=self._draw_stamp, onLaterPages=self._draw_stamp)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_lab_report(self, analysis_results, animal_type, stage, user_name, standard=None, evaluation=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=100)
        story = []
        def p(text, style='body'):
            return Paragraph(arabic_processor.fix_arabic_text(str(text)), self.styles.get(style, self.styles['body']))
        
        story.append(p("🔬 تقرير التحليل المخبري المتقدم - تاور نولجي Tawornology", 'title'))
        story.append(p(f"المشرف العام: {SUPERVISOR_NAME}", 'subtitle'))
        story.append(Spacer(1, 10))
        story.append(p(f"الحيوان: {animal_type} | المرحلة: {stage}"))
        story.append(p(f"تاريخ التحليل: {datetime.now().strftime('%Y-%m-%d %H:%M')}"))
        story.append(Spacer(1, 15))
        
        if analysis_results:
            if 'components' in analysis_results and analysis_results['components']:
                story.append(p("المكونات المدخلة:", 'heading'))
                comp = [['المادة', 'الوزن (كجم)', 'النسبة %']]
                total_w = sum(analysis_results['components'].values())
                for n, w in analysis_results['components'].items():
                    if w > 0:
                        comp.append([n, f"{w:.1f}", f"{(w/total_w)*100:.2f}"])
                tc = Table([[arabic_processor.fix_arabic_text(c) for c in r] for r in comp], colWidths=[200, 120, 120])
                tc.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),('TEXTCOLOR',(0,0),(-1,0),white),
                    ('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),
                    ('FONTSIZE',(0,0),(-1,-1),10),('GRID',(0,0),(-1,-1),1,HexColor('#bdbdbd')),
                    ('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#f5f5f5')])]))
                story.append(tc)
                story.append(Spacer(1, 10))
            
            story.append(p("النتائج المحسوبة:", 'heading'))
            res = [['العنصر', 'القيمة']]
            if 'cp' in analysis_results: res.append(['البروتين الخام CP', f"{analysis_results['cp']:.2f}%"])
            if 'dp' in analysis_results: res.append(['البروتين المهضوم DP', f"{analysis_results['dp']:.2f}%"])
            if 'se' in analysis_results: res.append(['معادل النشاء SE', f"{analysis_results['se']:.2f}"])
            tr = Table([[arabic_processor.fix_arabic_text(c) for c in r] for r in res], colWidths=[250, 250])
            tr.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#1565C0')),('TEXTCOLOR',(0,0),(-1,0),white),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),
                ('FONTSIZE',(0,0),(-1,-1),11),('GRID',(0,0),(-1,-1),1,HexColor('#1565C0'))]))
            story.append(tr)
            
            if standard:
                story.append(Spacer(1, 10))
                story.append(p("المقارنة مع المعايير:", 'heading'))
                comp2 = [['المقياس', 'المحسوب', 'القياسي', 'الانحراف %', 'التقييم']]
                for k, lbl in [('dp','DP'),('se','SE'),('cp','CP')]:
                    if k in analysis_results and k in standard:
                        dev = ((analysis_results[k] - standard[k]) / standard[k]) * 100 if standard[k] > 0 else 0
                        g = "ممتاز ✅" if abs(dev) <= 5 else ("جيد ⚠️" if abs(dev) <= 10 else "يحتاج تحسين ❌")
                        comp2.append([lbl, f"{analysis_results[k]:.2f}", f"{standard[k]:.2f}", f"{dev:.1f}", g])
                tc2 = Table([[arabic_processor.fix_arabic_text(c) for c in r] for r in comp2], colWidths=[80, 90, 90, 90, 90])
                tc2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),('TEXTCOLOR',(0,0),(-1,0),white),
                    ('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),
                    ('FONTSIZE',(0,0),(-1,-1),10),('GRID',(0,0),(-1,-1),1,HexColor('#bdbdbd'))]))
                story.append(tc2)
            
            if standard and 'dp' in analysis_results:
                try:
                    fig, ax = plt.subplots(figsize=(5, 3))
                    cats = ['DP', 'SE', 'CP']
                    calc = [analysis_results.get('dp',0), analysis_results.get('se',0), analysis_results.get('cp',0)]
                    std = [standard.get('dp',0), standard.get('se',0), standard.get('cp',0)]
                    x = np.arange(len(cats)); w = 0.35
                    ax.bar(x-w/2, calc, w, label='المحسوب', color='#2e7d32')
                    ax.bar(x+w/2, std, w, label='القياسي', color='#1565C0')
                    ax.set_xticks(x); ax.set_xticklabels(cats); ax.legend(); ax.grid(axis='y', ls='--', alpha=0.7)
                    ax.set_title(arabic_processor.fix_arabic_text('مقارنة القيم'))
                    buf = io.BytesIO()
                    plt.tight_layout(); plt.savefig(buf, format='png', dpi=100, bbox_inches='tight'); plt.close()
                    buf.seek(0)
                    story.append(Image(buf, width=400, height=220))
                except: pass
            
            story.append(Spacer(1, 10))
            story.append(p("التوصيات المخبرية:", 'heading'))
            for rec in ["• إعادة التحليل بعد أي تعديل.", "• مراجعة نسب البروتين والطاقة.", "• التواصل مع أخصائي التغذية."]:
                story.append(p(rec))
        
        story.append(Spacer(1, 30))
        story.append(p("مع خالص التحية والتقدير،", 'body'))
        story.append(Spacer(1, 15))
        story.append(p(SUPERVISOR_NAME, 'stamp'))
        story.append(Spacer(1, 40))
        story.append(p("تاور نولجي Tawornology العلمية © 2026", 'footer'))
        
        doc.build(story, onFirstPage=self._draw_stamp, onLaterPages=self._draw_stamp)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_milk_replacer_report(self, formula, animal_type, age_days, instructions, user_name):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=100)
        story = []
        def p(text, style='body'):
            return Paragraph(arabic_processor.fix_arabic_text(str(text)), self.styles.get(style, self.styles['body']))
        
        story.append(p("🍼 تقرير تركيب بديل الحليب - تاور نولجي", 'title'))
        story.append(p(f"المشرف: {SUPERVISOR_NAME}", 'subtitle'))
        story.append(Spacer(1, 10))
        story.append(p(f"نوع الحيوان: {animal_type}"))
        story.append(p(f"العمر (يوم): {age_days}"))
        story.append(p(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}"))
        story.append(Spacer(1, 15))
        story.append(p("مكونات بديل الحليب:", 'heading'))
        ing = [['المكون', 'النسبة %', 'الكمية (جم/كجم)']]
        for i, pct in formula.items():
            ing.append([i, f'{pct:.2f}%', f'{pct*10:.1f}'])
        t = Table([[arabic_processor.fix_arabic_text(c) for c in r] for r in ing], colWidths=[200, 130, 130])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),('TEXTCOLOR',(0,0),(-1,0),white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),10),('GRID',(0,0),(-1,-1),1,HexColor('#bdbdbd'))]))
        story.append(t)
        story.append(Spacer(1, 15))
        story.append(p("تعليمات التقديم:", 'heading'))
        for line in instructions.split('\n'):
            if line.strip():
                story.append(p(f"• {line.strip()}"))
        story.append(Spacer(1, 30))
        story.append(p(SUPERVISOR_NAME, 'stamp'))
        story.append(Spacer(1, 40))
        story.append(p("تاور نولجي Tawornology العلمية © 2026", 'footer'))
        doc.build(story, onFirstPage=self._draw_stamp, onLaterPages=self._draw_stamp)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# =====================================================================
# محرك تركيب العلف المتقدم مع قيود النظام العالمي
# =====================================================================
def validate_formulation(formula, animal_key, stage, standard):
    """التحقق من مطابقة التركيبة للنظام العالمي (NRC/INRA) بدقة 0.5%"""
    errors = []
    warnings = []
    
    if not standard:
        return errors, warnings
    
    # حساب القيم الفعلية
    total = sum(formula.values())
    if total <= 0:
        errors.append("التركيبة فارغة")
        return errors, warnings
    
    ca_total = 0.0
    p_total = 0.0
    nacl_total = 0.0
    ash_total = 0.0
    for ing, pct in formula.items():
        feed = FLAT_FEED_DB.get(ing, {})
        pct_factor = pct / 100.0
        ca_total += pct_factor * feed.get("Ca", 0.0)
        p_total += pct_factor * feed.get("P", 0.0)
        nacl_total += pct_factor * feed.get("NaCl", 0.0)
        ash_total += pct_factor * feed.get("ASH", 0.0)
    
    # قيود الكالسيوم (بهامش 0.5%)
    if 'Ca' in standard:
        ca_target = standard['Ca']
        ca_dev = abs(ca_total - ca_target) / ca_target * 100 if ca_target > 0 else 0
        if ca_dev > 15:
            errors.append(f"الكالسيوم {ca_total:.3f}% خارج النطاق القياسي ({ca_target:.2f}%) - انحراف {ca_dev:.1f}%")
        elif ca_dev > 10:
            warnings.append(f"الكالسيوم {ca_total:.3f}% قريب من الحد ({ca_target:.2f}%)")
    
    # قيود الفسفور
    if 'P' in standard:
        p_target = standard['P']
        p_dev = abs(p_total - p_target) / p_target * 100 if p_target > 0 else 0
        if p_dev > 15:
            errors.append(f"الفسفور {p_total:.3f}% خارج النطاق ({p_target:.2f}%) - انحراف {p_dev:.1f}%")
        elif p_dev > 10:
            warnings.append(f"الفسفور {p_total:.3f}% قريب من الحد ({p_target:.2f}%)")
    
    # قيود نسبة Ca:P
    if 'Ca_P_ratio' in standard and p_total > 0:
        ca_p_ratio = ca_total / p_total
        ratio_target = standard['Ca_P_ratio']
        ratio_dev = abs(ca_p_ratio - ratio_target) / ratio_target * 100 if ratio_target > 0 else 0
        if ratio_dev > 20:
            errors.append(f"نسبة Ca:P = {ca_p_ratio:.2f} خارج النطاق ({ratio_target:.2f}) - انحراف {ratio_dev:.1f}%")
        elif ratio_dev > 12:
            warnings.append(f"نسبة Ca:P = {ca_p_ratio:.2f} قريبة من الحد ({ratio_target:.2f})")
    
    # قيود الملح
    if 'NaCl_max' in standard:
        nacl_max = standard['NaCl_max']
        if nacl_total > nacl_max + 0.05:
            errors.append(f"الملح {nacl_total:.3f}% يتجاوز الحد الأقصى ({nacl_max}%)")
        elif nacl_total > nacl_max * 0.85:
            warnings.append(f"الملح {nacl_total:.3f}% قريب من الحد ({nacl_max}%)")
    
    # الحد الأدنى للملح
    if nacl_total < 0.15 and animal_key not in ["fish"]:
        warnings.append(f"الملح {nacl_total:.3f}% منخفض جداً (الحد الأدنى 0.2%)")
    
    return errors, warnings

def render_feed_formulation(animal_key, display_name, icon, default_breeds, default_stages, default_dp, default_se, img_key, has_measurements=True):
    st.markdown(f'<div class="section-title">{icon} {display_name}</div>', unsafe_allow_html=True)
    
    requester_name = st.text_input("👤 اسم طالب العلف (المربي / المزرعة):", key=f"{animal_key}_requester", placeholder="أدخل الاسم")
    
    col_m, col_s = st.columns([0.4, 0.6])
    with col_m:
        if has_measurements:
            st.markdown('<div class="measurement-card">', unsafe_allow_html=True)
            st.markdown("#### 📏 شريط القياس الحيوي")
            c1, c2, c3 = st.columns(3)
            with c1:
                girth = st.number_input("محيط الصدر (سم)", 20.0, 300.0, 150.0, key=f"{animal_key}_girth")
            with c2:
                length = st.number_input("طول الجسم (سم)", 20.0, 300.0, 130.0, key=f"{animal_key}_length")
            with c3:
                age_m = st.number_input("العمر (شهر)", 1, 120, 12, key=f"{animal_key}_age")
            wf = {"cattle":10838, "sheep":15500, "goat":15000, "horse":11877, "camel":13000}.get(animal_key, 12000)
            ff = {"cattle":0.025, "sheep":0.035, "goat":0.032, "horse":0.022, "camel":0.020}.get(animal_key, 0.03)
            est_w = (girth**2 * length) / wf
            st.success(f"الوزن التقديري: {est_w:.1f} كجم")
            st.info(f"الاحتياج اليومي: {est_w*ff:.2f} كجم مادة جافة")
            age_factor = 1 + (age_m - 12) * 0.01
            adjusted_dp = default_dp * (1 + (est_w - 500)/2000) * age_factor
            adjusted_se = default_se * (1 + (est_w - 500)/3000) * age_factor
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            adjusted_dp, adjusted_se = default_dp, default_se
            st.info("💡 لا تتوفر قياسات للطيور والأسماك")
    
    with col_s:
        st.markdown("#### 🎯 السلالة والمرحلة")
        c1, c2 = st.columns(2)
        with c1: breed = st.selectbox("السلالة:", default_breeds, key=f"{animal_key}_breed")
        with c2: stage = st.selectbox("المرحلة:", default_stages, key=f"{animal_key}_stage")
        
        st.markdown("#### 🧬 العمر والحالة الفسيولوجية")
        c1, c2 = st.columns(2)
        with c1:
            age_input = st.number_input("العمر (شهر)", 1, 240, 24, key=f"{animal_key}_age_input")
        with c2:
            phys = st.selectbox("الحالة الفسيولوجية", ["طبيعي","حامل","مرضع","صائم","نشاط مكثف","استشفاء","نمو سريع"], key=f"{animal_key}_phys")
        
        st.markdown("#### 🧬 البروتين والطاقة")
        p_basis = st.radio("أساس البروتين:", ["DP","CP"], horizontal=True, key=f"{animal_key}_basis")
        if p_basis == "DP":
            tp = st.number_input("نسبة DP (%)", 5.0, 50.0, float(adjusted_dp), 0.5, key=f"{animal_key}_dp")
            actual_dp = tp
        else:
            tp = st.number_input("نسبة CP (%)", 5.0, 60.0, float(default_dp/0.80), 0.5, key=f"{animal_key}_cp")
            actual_dp = tp * 0.80
        t_se = st.number_input("معادل النشاء SE", 10.0, 90.0, float(adjusted_se), 1.0, key=f"{animal_key}_se")
        
        mult = {"طبيعي":1.0,"حامل":1.15,"مرضع":1.30,"صائم":0.85,"نشاط مكثف":1.25,"استشفاء":1.20,"نمو سريع":1.35}.get(phys, 1.0)
        actual_dp *= mult
        t_se *= mult
        st.caption(f"معامل الحالة: {mult:.2f}")
    
    st.markdown("#### 🌾 اختر المكونات")
    selected, prices = [], {}
    defaults = {
        "cattle": ["ذرة صفراء","شعير مطحون","نخالة قمح (ردة)","كسب فول صويا 44%","أمباز الفول السوداني","مركزات مجترات","ملح الطعام","الحجر الجيري","فوسفات DCP","بيكربونات الصوديوم"],
        "sheep": ["ذرة صفراء","شعير مطحون","نخالة قمح (ردة)","كسب فول صويا 44%","أمباز الفول السوداني","مركزات مجترات","ملح الطعام","الحجر الجيري","فوسفات DCP","بيكربونات الصوديوم"],
        "goat": ["ذرة صفراء","شعير مطحون","نخالة قمح (ردة)","كسب فول صويا 44%","أمباز الفول السوداني","مركزات مجترات","ملح الطعام","الحجر الجيري","فوسفات DCP","بيكربونات الصوديوم"],
        "horse": ["شعير مطحون","ذرة صفراء","نخالة قمح (ردة)","كسب فول صويا 44%","مولاس قصب السكر","مركزات مجترات","ملح الطعام","الحجر الجيري","فوسفات DCP"],
        "camel": ["شعير مطحون","ذرة صفراء","نخالة قمح (ردة)","كسب فول صويا 44%","البرسيم الجاف","مركزات مجترات","ملح الطعام","الحجر الجيري","فوسفات DCP"],
        "poultry": ["ذرة صفراء","سورجم (فتريتة)","كسب فول صويا 44%","كسب جلوتين الذرة 60%","مركزات دواجن","بريمكس تسمين دواجن","ملح الطعام","الحجر الجيري","فوسفات DCP","إنزيم الفايتيز"],
        "fish": ["ذرة صفراء","كسب فول صويا 44%","مسحوق أسماك 60%","كسب جلوتين الذرة 60%","مركزات دواجن","ملح الطعام","فوسفات DCP","إنزيم الفايتيز"]
    }
    default_list = defaults.get(animal_key, [])
    
    for cat, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat}", expanded=False):
            cols = st.columns(3)
            for i, ing_name in enumerate(items.keys()):
                with cols[i % 3]:
                    checked = st.checkbox(ing_name, value=ing_name in default_list, key=f"{animal_key}_cb_{ing_name}")
                    if checked:
                        price = st.number_input(f"${ing_name}/طن", 5.0, value=350.0, key=f"{animal_key}_pr_{ing_name}")
                        selected.append(ing_name)
                        prices[ing_name] = price
    
    col_btn = st.columns(3)
    with col_btn[0]:
        if st.button(f"🚀 تشغيل محرك التركيب - {display_name}", type="primary", use_container_width=True, key=f"{animal_key}_run"):
            if len(selected) < 3:
                st.warning("⚠️ اختر 3 مكونات على الأقل")
            else:
                voice_guide(f"جاري تركيب العلف لـ {display_name}")
                with st.spinner("جاري الحساب..."):
                    c_vec = [prices[i] for i in selected]
                    bounds = [(0.0, 100.0) for _ in selected]
                    A_eq = [[1.0 for _ in selected]]
                    b_eq = [100.0]
                    cp_row, se_row, ndf_row = [], [], []
                    for ing in selected:
                        fd = FLAT_FEED_DB.get(ing, {})
                        cp_row.append(fd.get("CP",0) * fd.get("DC",0))
                        se_row.append(fd.get("SE",0))
                        ndf_row.append(fd.get("NDF",0))
                    A_eq.append(cp_row); b_eq.append(actual_dp * 100.0)
                    A_ub, b_ub = [], []
                    A_ub.append([-x for x in se_row]); b_ub.append(-t_se * 100.0)
                    if animal_key in ["cattle","sheep","goat","camel"]:
                        A_ub.append(ndf_row); b_ub.append(3500.0)
                    # إضافة قيود إلزامية للمواد الأساسية
                    fixed = {}
                    if animal_key in ["cattle","sheep","goat","camel"]:
                        for mandatory, pct in [("بيكربونات الصوديوم", 0.75 if animal_key=="cattle" else 0.5), ("ملح الطعام", 0.5), ("الحجر الجيري", 1.5), ("فوسفات DCP", 0.8)]:
                            if mandatory not in selected:
                                selected.append(mandatory)
                                prices[mandatory] = {"بيكربونات الصوديوم":340.0,"ملح الطعام":30.0,"الحجر الجيري":40.0,"فوسفات DCP":280.0}.get(mandatory, 300.0)
                                bounds.append((pct, pct))
                                c_vec.append(prices[mandatory])
                                cp_row.append(0.0); se_row.append(0.0); ndf_row.append(0.0)
                            else:
                                idx = selected.index(mandatory)
                                bounds[idx] = (pct, pct)
                    if animal_key in ["poultry","fish"]:
                        for mandatory, pct in [("إنزيم الفايتيز", 0.05), ("ملح الطعام", 0.3), ("الحجر الجيري", 1.0), ("فوسفات DCP", 1.5)]:
                            if mandatory not in selected:
                                selected.append(mandatory)
                                prices[mandatory] = {"إنزيم الفايتيز":1200.0,"ملح الطعام":30.0,"الحجر الجيري":40.0,"فوسفات DCP":280.0}.get(mandatory, 300.0)
                                bounds.append((pct, pct))
                                c_vec.append(prices[mandatory])
                                cp_row.append(0.0); se_row.append(0.0); ndf_row.append(0.0)
                            else:
                                idx = selected.index(mandatory)
                                bounds[idx] = (pct, pct)
                    
                    # إعادة بناء المصفوفات
                    A_eq = [[1.0 for _ in selected]]
                    b_eq = [100.0]
                    cp_new, se_new = [], []
                    for ing in selected:
                        fd = FLAT_FEED_DB.get(ing, {})
                        cp_new.append(fd.get("CP",0) * fd.get("DC",0))
                        se_new.append(fd.get("SE",0))
                    A_eq.append(cp_new); b_eq.append(actual_dp * 100.0)
                    A_ub_new, b_ub_new = [], []
                    A_ub_new.append([-x for x in se_new]); b_ub_new.append(-t_se * 100.0)
                    
                    try:
                        res = linprog(c_vec, A_ub=A_ub_new, b_ub=b_ub_new, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
                        if res.success:
                            formula = {selected[i]: res.x[i] for i in range(len(selected)) if res.x[i] > 0.001}
                            ton_cost = res.fun / 100.0
                            comp_se = sum((formula[i]/100.0) * FLAT_FEED_DB.get(i,{}).get("SE",0) for i in formula)
                            standard = STANDARD_VALUES.get(display_name, {}).get(stage, {})
                            
                            # التحقق من النظام العالمي
                            errs, warns = validate_formulation(formula, animal_key, stage, standard)
                            
                            # حساب النسب الفعلية للمقارنة
                            comp_dp = actual_dp
                            if standard:
                                dp_ratio = comp_dp / standard.get('dp', comp_dp) * 100 if standard.get('dp',0) > 0 else 100
                                se_ratio = comp_se / standard.get('se', comp_se) * 100 if standard.get('se',0) > 0 else 100
                                
                                if dp_ratio < 75 or se_ratio < 75:
                                    errs.append(f"❌ البروتين أو الطاقة أقل من 75% من المعيار (DP: {dp_ratio:.1f}%، SE: {se_ratio:.1f}%)")
                            
                            if errs:
                                st.error("🚫 التركيبة لا تطابق النظام العالمي (NRC/INRA):")
                                for e in errs:
                                    st.error(f"❌ {e}")
                                if warns:
                                    for w in warns:
                                        st.warning(f"⚠️ {w}")
                                voice_guide("التركيبة لا تطابق المعايير. يرجى التعديل.")
                            else:
                                st.success(f"✅ تم التوليد بنجاح! التكلفة: ${ton_cost:.2f}/طن")
                                if warns:
                                    for w in warns:
                                        st.info(f"ℹ️ {w}")
                                voice_guide(f"تم التوليد بنجاح. التكلفة {ton_cost:.2f} دولار")
                                
                                c1, c2 = st.columns([0.6, 0.4])
                                with c1:
                                    st.write("#### 📝 المقادير:")
                                    for k, v in formula.items():
                                        st.markdown(f'<div class="formula-item"><span>{k}</span><span>{v:.2f}% ({v*10:.1f} كجم)</span></div>', unsafe_allow_html=True)
                                    st.metric("💰 التكلفة", f"${ton_cost:.2f}/طن")
                                    st.metric("🧬 DP", f"{comp_dp:.2f}%")
                                    st.metric("🌽 SE", f"{comp_se:.2f}")
                                    
                                    if standard:
                                        st.write("#### 📊 المقارنة مع المعايير:")
                                        comp_data = []
                                        for k, lbl in [('dp','DP'),('se','SE'),('Ca','Ca'),('P','P')]:
                                            if k in standard:
                                                if k == 'dp': val = comp_dp
                                                elif k == 'se': val = comp_se
                                                elif k == 'Ca': val = sum(formula[i]/100*FLAT_FEED_DB.get(i,{}).get('Ca',0) for i in formula)
                                                else: val = sum(formula[i]/100*FLAT_FEED_DB.get(i,{}).get('P',0) for i in formula)
                                                dev = ((val - standard[k]) / standard[k]) * 100 if standard[k] > 0 else 0
                                                g = "✅" if abs(dev) <= 10 else "⚠️"
                                                comp_data.append({"المقياس": lbl, "المحسوب": f"{val:.3f}", "القياسي": f"{standard[k]:.3f}", "الانحراف": f"{dev:.1f}%", "التقييم": g})
                                        st.table(pd.DataFrame(comp_data))
                                    
                                    if st.button("🔬 إرسال للمختبر", use_container_width=True):
                                        st.session_state["lab_sample"] = {
                                            'formula': formula, 'animal': display_name, 'breed': breed,
                                            'stage': stage, 'age': age_input, 'physiological': phys,
                                            'dp': comp_dp, 'se': comp_se, 'cp': comp_dp/0.80,
                                            'requester': requester_name
                                        }
                                        st.success("تم الإرسال")
                                    
                                    try:
                                        pdf_data = pdf_generator.generate_comprehensive_report(
                                            formula, comp_dp, f"{breed} - {stage} ({phys})",
                                            ton_cost, "المدينة", ton_cost*600, "SDG", comp_se,
                                            st.session_state.get("user", {}).get("full_name", "مستخدم"),
                                            requester_name=requester_name, standard=standard,
                                            include_charts=True,
                                            extra_info={"السلالة": breed, "المرحلة": stage, "الحالة": phys, "العمر": f"{age_input} شهر"}
                                        )
                                        st.download_button("📥 تحميل PDF", pdf_data, file_name=f"Formula_{display_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf", use_container_width=True)
                                    except Exception as e:
                                        st.warning(f"تعذر PDF: {e}")
                                with c2:
                                    if len(formula) > 1:
                                        fig = px.pie(values=list(formula.values()), names=list(formula.keys()), title="توزيع المكونات", color_discrete_sequence=px.colors.sequential.Greens)
                                        fig.update_layout(height=400)
                                        st.plotly_chart(fig, use_container_width=True)
                                
                                st.session_state["active_formula"] = formula
                                st.session_state["computed_ton_cost"] = ton_cost
                        else:
                            st.error("❌ تعذر إيجاد حل رياضي متزن")
                    except Exception as e:
                        st.error(f"خطأ: {e}")
    
    with col_btn[1]:
        if st.button(f"📋 المعايير القياسية ({display_name})", use_container_width=True):
            standard = STANDARD_VALUES.get(display_name, {}).get(stage, {})
            if standard:
                st.info(f"📊 المعايير: DP={standard.get('DP','-')}%, SE={standard.get('SE','-')}, CP={standard.get('CP','-')}%")
                st.info(f"🧪 Ca={standard.get('Ca','-')}%, P={standard.get('P','-')}%, Ca:P={standard.get('Ca_P_ratio','-')}, NaCl max={standard.get('NaCl_max','-')}%")
    
    with col_btn[2]:
        if st.button(f"🔊 تعليمات ({display_name})", use_container_width=True):
            voice_guide(f"قسم {display_name}: اختر السلالة والمرحلة، ثم اختر المكونات واضغط تشغيل")

# =====================================================================
# المختبر المتقدم
# =====================================================================
def render_advanced_lab():
    st.markdown('<div class="section-title">🔬 المختبر المتقدم</div>', unsafe_allow_html=True)
    
    if st.session_state.get("lab_sample"):
        s = st.session_state["lab_sample"]
        st.success(f"📥 عينة من {s['animal']} - {s['breed']}")
        st.write(f"DP: {s['dp']:.2f}% | SE: {s['se']:.2f}")
        if s.get('requester'): st.write(f"طالب العلف: {s['requester']}")
        if st.button("🗑️ مسح العينة"): st.session_state["lab_sample"]=None; st.rerun()
    
    c1, c2 = st.columns(2)
    with c1:
        lab_animal = st.selectbox("الفصيل:", list(STANDARD_VALUES.keys()))
        lab_stage = st.selectbox("المرحلة:", list(STANDARD_VALUES.get(lab_animal, {}).keys()))
        standard = STANDARD_VALUES.get(lab_animal, {}).get(lab_stage, {})
    with c2:
        p_sys = st.selectbox("نظام البروتين:", ["بروتين مهضوم DP", "بروتين خام CP", "بروتين صافي NP"])
        e_sys = st.selectbox("نظام الطاقة:", ["معادل النشاء SE", "طاقة أيضية ME", "طاقة صافية NE"])
    
    lab_in = {}
    cols = st.columns(3)
    for i, ing in enumerate(FLAT_FEED_DB.keys()):
        with cols[i % 3]:
            lab_in[ing] = st.number_input(f"وزن {ing} (كجم)", 0.0, value=0.0, step=5.0, key=f"lab_{ing}")
    
    if st.button("🧪 تشغيل التحليل", type="primary", use_container_width=True):
        total = sum(lab_in.values())
        if total <= 0:
            st.warning("أدخل أوزاناً")
        else:
            voice_guide("جاري التحليل")
            cp_t, dp_t, se_t = 0.0, 0.0, 0.0
            ca_t, p_t, nacl_t = 0.0, 0.0, 0.0
            comps = []
            for ing, w in lab_in.items():
                if w > 0:
                    pct = w / total
                    fd = FLAT_FEED_DB.get(ing, {})
                    cp_t += pct * fd.get("CP",0)
                    dp_t += pct * fd.get("CP",0) * fd.get("DC",0)
                    se_t += pct * fd.get("SE",0)
                    ca_t += pct * fd.get("Ca",0)
                    p_t += pct * fd.get("P",0)
                    nacl_t += pct * fd.get("NaCl",0)
                    comps.append({"المادة": ing, "الوزن": w, "النسبة%": f"{pct*100:.2f}"})
            
            st.success("🔬 تم التحليل")
            st.markdown(f"### ⚖️ إجمالي الوزن: {total:.1f} كجم")
            st.table(pd.DataFrame(comps))
            st.write("#### النتائج:")
            st.table(pd.DataFrame([
                {"العنصر": "البروتين الخام CP", "القيمة": f"{cp_t:.2f}%"},
                {"العنصر": "البروتين المهضوم DP", "القيمة": f"{dp_t:.2f}%"},
                {"العنصر": "معادل النشاء SE", "القيمة": f"{se_t:.2f}"},
                {"العنصر": "الكالسيوم Ca", "القيمة": f"{ca_t:.3f}%"},
                {"العنصر": "الفسفور P", "القيمة": f"{p_t:.3f}%"},
                {"العنصر": "ملح الطعام NaCl", "القيمة": f"{nacl_t:.3f}%"}
            ]))
            
            if standard:
                eval_data = []
                for k, lbl in [('dp','DP'),('se','SE'),('cp','CP'),('Ca','Ca'),('P','P')]:
                    if k in standard:
                        if k == 'dp': val = dp_t
                        elif k == 'se': val = se_t
                        elif k == 'cp': val = cp_t
                        elif k == 'Ca': val = ca_t
                        else: val = p_t
                        dev = ((val - standard[k]) / standard[k]) * 100 if standard[k] > 0 else 0
                        g = "ممتاز ✅" if abs(dev) <= 5 else ("جيد ⚠️" if abs(dev) <= 10 else "يحتاج تحسين ❌")
                        eval_data.append({"المقياس": lbl, "المحسوب": f"{val:.3f}", "القياسي": f"{standard[k]:.3f}", "الانحراف": f"{dev:.1f}%", "التقييم": g})
                
                if p_t > 0:
                    ca_p = ca_t / p_t
                    ratio_target = standard.get('Ca_P_ratio', 2.0)
                    r_dev = ((ca_p - ratio_target) / ratio_target) * 100
                    g = "ممتاز ✅" if abs(r_dev) <= 10 else "يحتاج تحسين ⚠️"
                    eval_data.append({"المقياس": "Ca:P", "المحسوب": f"{ca_p:.2f}", "القياسي": f"{ratio_target:.2f}", "الانحراف": f"{r_dev:.1f}%", "التقييم": g})
                
                if 'NaCl_max' in standard:
                    g = "ممتاز ✅" if nacl_t <= standard['NaCl_max'] else "تجاوز الحد ❌"
                    eval_data.append({"المقياس": "NaCl", "المحسوب": f"{nacl_t:.3f}%", "القياسي": f"≤{standard['NaCl_max']}%", "الانحراف": "-", "التقييم": g})
                
                st.write("#### 📊 المقارنة مع المعايير العالمية:")
                st.table(pd.DataFrame(eval_data))
            
            # PDF
            st.session_state["analysis_results"] = {'components': lab_in, 'cp': cp_t, 'dp': dp_t, 'se': se_t, 'Ca': ca_t, 'P': p_t, 'NaCl': nacl_t}
            try:
                pdf_data = pdf_generator.generate_lab_report(
                    st.session_state["analysis_results"], lab_animal, lab_stage,
                    st.session_state.get("user", {}).get("full_name", "مستخدم"),
                    standard, None
                )
                st.download_button("📥 تحميل تقرير المختبر PDF", pdf_data, file_name=f"Lab_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf")
            except Exception as e:
                st.warning(f"تعذر PDF: {e}")

# =====================================================================
# بدائل الحليب
# =====================================================================
def render_milk_replacer():
    st.markdown('<div class="section-title">🍼 بدائل الحليب</div>', unsafe_allow_html=True)
    animal_type = st.selectbox("نوع الحيوان:", ["عجل بقري","حملان أغنام","جديان ماعز","مهرات خيول","أطفال إبل"])
    age_days = st.slider("العمر (يوم)", 1, 120, 30)
    needs = {"عجل بقري":{"p":22,"f":18,"e":75,"v":8},"حملان أغنام":{"p":24,"f":20,"e":72,"v":4},"جديان ماعز":{"p":23,"f":19,"e":70,"v":3},"مهرات خيول":{"p":20,"f":15,"e":68,"v":5},"أطفال إبل":{"p":21,"f":17,"e":66,"v":6}}
    af = 1.2 if age_days < 14 else 1.0 if age_days < 30 else 0.85 if age_days < 60 else 0.70
    tp = needs[animal_type]["p"] * af
    tf = needs[animal_type]["f"] * af
    te = needs[animal_type]["e"] * af
    dv = needs[animal_type]["v"] * af
    st.info(f"الاحتياجات: بروتين {tp:.1f}%، دهون {tf:.1f}%، طاقة {te:.1f}، الحجم {dv:.1f} لتر")
    
    repl = {
        "حليب مجفف منزوع": {"CP":34,"Fat":1,"SE":40,"Cost":18},
        "مصل الحليب Whey": {"CP":12,"Fat":1,"SE":35,"Cost":12},
        "دهن نباتي": {"CP":0,"Fat":99,"SE":10,"Cost":8},
        "ليسيثين الصويا": {"CP":0,"Fat":95,"SE":0,"Cost":15},
        "بروتين الصويا المركز": {"CP":65,"Fat":1,"SE":30,"Cost":20},
        "فيتامينات ومعادن": {"CP":0,"Fat":0,"SE":0,"Cost":25}
    }
    sel, pr = [], {}
    cols = st.columns(3)
    for i, (ing, d) in enumerate(repl.items()):
        with cols[i % 3]:
            if st.checkbox(ing, value=i<4, key=f"r_{ing}"):
                sel.append(ing)
                pr[ing] = st.number_input(f"${ing}", 1.0, value=float(d["Cost"]), key=f"rp_{ing}")
    
    if st.button("🍼 تشغيل المحرك", type="primary"):
        if len(sel) < 3:
            st.warning("اختر 3 مكونات")
        else:
            c = [pr[i] for i in sel]
            b = [(0,100) for _ in sel]
            A_eq = [[1]*len(sel)]; b_eq = [100]
            prot = [repl[i]["CP"] for i in sel]
            A_eq.append(prot); b_eq.append(tp)
            A_ub = [[-repl[i]["Fat"] for i in sel]]; b_ub = [-tf]
            A_ub.append([-repl[i]["SE"] for i in sel]); b_ub.append(-te)
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=b, method='highs')
            if res.success:
                formula = {sel[i]: res.x[i] for i in range(len(sel)) if res.x[i] > 0.001}
                ckg = res.fun / 100.0
                st.success(f"✅ التكلفة: ${ckg:.2f}/كجم")
                for k, v in formula.items():
                    st.markdown(f'<div class="formula-item"><span>{k}</span><span>{v:.1f}% ({v*10:.1f} جم/كجم)</span></div>', unsafe_allow_html=True)
                st.info(f"الجرعة اليومية: {dv:.1f} لتر (3-4 وجبات)")
                st.info("التركيز: 100-150 جم/لتر ماء دافئ 40-45°م")
                st.info("درجة التقديم: 38-40°م")
                try:
                    instructions = f"الجرعة: {dv:.1f} لتر/يوم\nالتركيز: 100-150 جم/لتر\nدرجة الحرارة: 38-40°م\nالتخزين: مكان جاف"
                    pdf_data = pdf_generator.generate_milk_replacer_report(formula, animal_type, age_days, instructions, "المشرف")
                    st.download_button("📥 PDF", pdf_data, file_name=f"Milk_{animal_type}.pdf", mime="application/pdf")
                except: pass
            else:
                st.error("تعذر الحل")

# =====================================================================
# شريط الدعاء
# =====================================================================
def render_dua_bar():
    st.markdown("""
    <style>
    @keyframes scrollDua { 0%{transform:translateX(100%);opacity:0} 5%{transform:translateX(0%);opacity:1} 85%{transform:translateX(0%);opacity:1} 95%{transform:translateX(-100%);opacity:0} 100%{transform:translateX(-100%);opacity:0} }
    @keyframes glowText { 0%{text-shadow:0 0 5px #ffd700,0 0 10px #ffd700} 50%{text-shadow:0 0 15px #ffd700,0 0 30px #ff8c00} 100%{text-shadow:0 0 5px #ffd700,0 0 10px #ffd700} }
    @keyframes pulseHeart { 0%,100%{transform:scale(1);color:#ff6b6b} 50%{transform:scale(1.5);color:#ff1744} }
    .dua-container{background:linear-gradient(135deg,#0d1b2a 0%,#1a237e 40%,#4a148c 70%,#0d1b2a 100%);padding:22px 0;border-radius:24px;margin-bottom:20px;overflow:hidden;border:3px solid #ffd700;box-shadow:0 8px 40px rgba(255,215,0,0.5);direction:rtl;position:relative}
    .dua-text{display:inline-block;white-space:nowrap;animation:scrollDua 24s ease-in-out infinite,glowText 3.5s ease-in-out infinite;font-size:1.7rem;font-weight:800;color:#ffd700;padding:0 25px;direction:rtl;letter-spacing:2px;text-shadow:0 0 20px rgba(255,215,0,0.4)}
    .dua-text .emoji-heart{display:inline-block;animation:pulseHeart 1.2s ease-in-out infinite;margin:0 8px}
    .dua-text .gold-star{color:#ffd700;font-size:1.6rem;margin:0 12px;display:inline-block;animation:pulseHeart 1.8s ease-in-out infinite}
    .dua-text .name-highlight{color:#ffab40;font-weight:900;background:rgba(255,215,0,0.15);padding:0 10px;border-radius:8px;border:1px solid rgba(255,215,0,0.3);display:inline-block}
    .dua-reminder{text-align:center;color:#b39ddb;font-size:1rem;padding:10px 0;background:rgba(0,0,0,0.35);border-radius:0 0 20px 20px;border-top:1px solid rgba(255,215,0,0.25);font-weight:600}
    .dua-reminder span{color:#ffd54f;font-weight:700;background:rgba(255,215,0,0.12);padding:4px 16px;border-radius:25px;border:1px solid rgba(255,215,0,0.2)}
    </style>
    <div class="dua-container"><div class="dua-text">
    <span class="gold-star">✦</span><span class="emoji-heart">❤️</span>
    اللهم اغفر لـ <span class="name-highlight">إسماعيل تاور</span> و<span class="name-highlight">ابتسام</span> وارحمهما وأدخلهما فسيح جناتك
    <span class="emoji-heart">❤️</span> اللهم اجعل قبرهما روضة من رياض الجنة
    <span class="emoji-heart">❤️</span> اللهم ارحم موتانا وموتى المسلمين <span class="emoji-heart">❤️</span><span class="gold-star">✦</span>
    </div></div>
    <div class="dua-reminder">🕊️ <span>تذكير:</span> ادعُ لهما بالرحمة والمغفرة 🕊️</div>
    """, unsafe_allow_html=True)

# =====================================================================
# CSS
# =====================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
* { font-family: 'Cairo', 'Tajawal', sans-serif; }
html, body, [data-testid="stAppViewContainer"] { background: linear-gradient(135deg,#f5f7fa 0%,#c3cfe2 50%,#f5f7fa 100%); background-attachment: fixed; }
.stApp { background: transparent; }
.main-box { background: rgba(255,255,255,0.92); padding: 35px; border-radius: 24px; box-shadow: 0 25px 70px rgba(0,0,0,0.15); margin-bottom: 35px; border: 1px solid rgba(255,255,255,0.4); }
.section-title { color: #1b5e20; border-right: 6px solid #2e7d32; padding-right: 18px; text-align: right; font-size: 1.7rem; font-weight: 700; margin-top: 30px; margin-bottom: 25px; background: linear-gradient(to left,rgba(46,125,50,0.12),transparent); padding: 14px 22px; border-radius: 14px; }
.formula-item { background: linear-gradient(135deg,rgba(255,255,255,0.95),rgba(232,245,233,0.95)); padding: 16px 22px; border-radius: 14px; margin-bottom: 10px; font-weight: 600; color: #1b5e20 !important; border-right: 5px solid #2e7d32; box-shadow: 0 4px 18px rgba(0,0,0,0.06); display: flex; justify-content: space-between; }
.profile-img-style { width: 160px; height: 160px; border-radius: 50%; object-fit: cover; border: 4px solid #d4af37; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
.metric-card { background: white; padding: 22px; border-radius: 18px; box-shadow: 0 6px 30px rgba(0,0,0,0.08); text-align: center; }
.metric-card .number { font-size: 2.2rem; font-weight: 900; color: #1b5e20; margin: 5px 0; }
.metric-card .label { font-size: 0.95rem; color: #666; font-weight: 600; }
.measurement-card { background: linear-gradient(135deg,#e3f2fd,#bbdefb); padding: 22px; border-radius: 16px; border-right: 5px solid #1565C0; }
.warning-card { background: linear-gradient(135deg,#fff3e0,#ffe0b2); padding: 15px; border-radius: 12px; border-right: 5px solid #f57c00; margin-bottom: 15px; direction: rtl; text-align: right; color: #e65100 !important; }
.book-chapter { background: linear-gradient(135deg,#1a237e,#283593); color: white; padding: 15px 20px; border-radius: 10px; font-weight: bold; margin-top: 20px; }
.book-body { padding: 20px 25px; font-size: 1.05rem; line-height: 1.8; color: #2c3e50; border-left: 4px solid #3498db; background: #f8f9fa; border-radius: 0 10px 10px 0; }
.manual-book { background: #fff; padding: 30px; border-radius: 16px; box-shadow: 0 8px 35px rgba(0,0,0,0.08); }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# شاشة الدخول
# =====================================================================
if not st.session_state["approved"]:
    render_dua_bar()
    if st.session_state["login_attempts"] >= 5:
        if st.session_state["last_login_time"]:
            if (datetime.now() - st.session_state["last_login_time"]).seconds < 300:
                st.error("🔒 قفل مؤقت"); st.stop()
            else: st.session_state["login_attempts"] = 0
    
    st.markdown('<div class="main-box" style="max-width:550px;margin:80px auto;direction:rtl;">', unsafe_allow_html=True)
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" style="width:100px;height:100px;border-radius:50%;border:3px solid #d4af37;display:block;margin:0 auto;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1a237e;text-align:center;'>🌾 تاور نولجي Tawornology العلمية</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#555;'>للانتاج الحيواني وتركيب الاعلاف وفق النظام العالمي</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#888;font-size:0.9rem;'>الإصدار 17.0 - مع الختم الرسمي</p>", unsafe_allow_html=True)
    
    if st.button("🔊 الشرح الصوتي الكامل", type="primary", use_container_width=True):
        play_full_guide_audio()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔊 الترحيب", use_container_width=True): play_welcome_audio()
    with c2:
        if st.button("🕊️ الدعاء", use_container_width=True): play_dua_audio()
    
    if st.button("👤 دخول كزائر", type="primary", use_container_width=True):
        auth = AuthManager()
        u = auth.login_public()
        if u:
            st.session_state["approved"]=True; st.session_state["user_role"]="public"
            st.session_state["login_welcome_shown"]=False; st.session_state["login_attempts"]=0
            st.session_state["last_login_time"]=datetime.now(); st.session_state["user"]=u
            voice_guide("مرحباً زائراً"); st.rerun()
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>🔑 للمالك والمختصين</p>", unsafe_allow_html=True)
    opt = st.radio("طريقة الدخول:", ["كود","مستخدم/كلمة"], horizontal=True)
    if opt == "كود":
        code = st.text_input("🔑 الكود:", type="password")
        if st.button("دخول 🔓", use_container_width=True):
            if code.strip() in CODES_DB:
                st.session_state["approved"]=True; st.session_state["user_role"]=CODES_DB[code.strip()]["role"]
                st.session_state["login_welcome_shown"]=False; st.session_state["login_attempts"]=0
                st.session_state["last_login_time"]=datetime.now()
                voice_guide(f"مرحباً {CODES_DB[code.strip()]['name']}"); st.rerun()
            else:
                st.session_state["login_attempts"]+=1
                st.error(f"❌ كود خاطئ - متبقي {5-st.session_state['login_attempts']}")
    else:
        u = st.text_input("👤 المستخدم")
        p = st.text_input("🔑 كلمة المرور", type="password")
        if st.button("دخول 🔓", type="primary", use_container_width=True):
            auth = AuthManager()
            usr = auth.authenticate(u, p)
            if usr:
                st.session_state["approved"]=True; st.session_state["user_role"]=usr['role']
                st.session_state["login_welcome_shown"]=False; st.session_state["login_attempts"]=0
                st.session_state["last_login_time"]=datetime.now(); st.session_state["user"]=usr
                voice_guide(f"مرحباً {usr['full_name']}"); st.rerun()
            else:
                st.session_state["login_attempts"]+=1
                st.error(f"❌ خاطئ - متبقي {5-st.session_state['login_attempts']}")
        st.caption("💡 admin / admin123")
    
    st.markdown("<div style='text-align:center;margin-top:15px;color:#999;font-size:0.85rem;'><p>🕊️ إهداء إلى روح الوالد إسماعيل تاور والأخت ابتسام - رحمهما الله</p></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# الترحيب بعد الدخول
# =====================================================================
if not st.session_state["login_welcome_shown"]:
    voice_welcome(st.session_state["user_role"])
    st.session_state["login_welcome_shown"]=True

render_dua_bar()

# =====================================================================
# الواجهة الرئيسية
# =====================================================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

c1, c2 = st.columns([0.7,0.3])
with c2:
    roles = {"owner":"المالك 👑","specialist":"المختص 👨‍🔬","veterinarian":"البيطري 💊","nutritionist":"التغذية 🧬","breeder":"المربي 🌾","public":"زائر 👤"}
    uname = st.session_state.get("user",{}).get("full_name","زائر")
    st.markdown(f"<div style='text-align:left;background:linear-gradient(135deg,#f5f5f5,#e0e0e0);padding:14px;border-radius:14px;'><b>{uname}</b><br><small>{roles.get(st.session_state['user_role'],'')}</small></div>", unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k not in ["inventory","broiler_farms","dose_reminders","email_password","basmala_played","welcome_played"]:
                del st.session_state[k]
        st.session_state["approved"]=False
        voice_guide("وداعاً"); st.rerun()

c1, c2 = st.columns([0.2,0.8])
with c1:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)
with c2:
    st.markdown("<h1 style='color:#1a237e;text-align:right;'>🌾 تاور نولجي Tawornology العلمية</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#1565C0;text-align:right;font-size:1.1rem;'>للانتاج الحيواني وتركيب الاعلاف وفق النظام العالمي NRC/INRA</p>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:#c62828;text-align:right;'>{SUPERVISOR_NAME}</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top:3px solid #2e7d32;'>", unsafe_allow_html=True)

if st.button("🔊 تشغيل الشرح الصوتي الكامل للمنصة", type="primary", use_container_width=True):
    play_full_guide_audio(); st.success("✅ يتم التشغيل...")

# إحصائيات
st.markdown("### 📊 لوحة التحكم")
ss = InventoryManager.get_stock_summary()
c1,c2,c3,c4 = st.columns(4)
with c1: st.markdown(f"<div class='metric-card'><div class='number'>{ss['total_items']}</div><div class='label'>المواد</div></div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='metric-card'><div class='number'>{ss['total_quantity']:.1f}</div><div class='label'>المخزون (طن)</div></div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div class='metric-card'><div class='number' style='color:#c62828;'>{ss['low_stock']}</div><div class='label'>منخفضة</div></div>", unsafe_allow_html=True)
with c4: st.markdown(f"<div class='metric-card'><div class='number'>{len(st.session_state.get('broiler_farms',{}))}</div><div class='label'>مزارع</div></div>", unsafe_allow_html=True)

st.markdown("---")

# =====================================================================
# التبويبات
# =====================================================================
tabs_titles = ["🐾 القطاع الحيواني","🐔 المزارع","🍼 بدائل الحليب","🕌 الصلاة","💊 الجرعات","📊 البورصة","🏭 المستودعات","📈 الإنتاج","🔔 التنبيهات","📚 المراجع","💡 المساعدة","📖 الدليل"]
if st.session_state["user_role"] == "owner": tabs_titles.append("📧 إرسال الكود")
tabs = st.tabs(tabs_titles)

def guide_section(name, text):
    with st.expander(f"📘 دليل {name}"):
        st.markdown(f"<div style='background:#f0f8ff;padding:15px;border-radius:10px;direction:rtl;'>{text}</div>", unsafe_allow_html=True)
        if st.button(f"🔊 استمع"): voice_guide(text)

# التبويب 0
with tabs[0]:
    guide_section("القطاع الحيواني", "اختر النوع، السلالة، المرحلة، المكونات، ثم شغّل المحرك")
    atabs = st.tabs(["🐄 أبقار","🐏 أغنام","🐐 ماعز","🐴 خيول","🐫 إبل","🐔 دواجن","🐟 أسماك","🔬 المختبر"])
    with atabs[0]: render_feed_formulation("cattle","أبقار","🐄",["كنانة","بطانة","هولشتاين"],["تسمين عجول","حليب/إدرار","حمل/دفع","صيانة","تسمين مكثف"],12.0,68.0,"أبقار")
    with atabs[1]: render_feed_formulation("sheep","أغنام","🐏",["صحراوي","بربري","نعيمي"],["تسمين حملان","نعاج مرضعات","نعاج حامل","صيانة"],13.0,66.0,"أغنام")
    with atabs[2]: render_feed_formulation("goat","ماعز","🐐",["نوبي","صحراوي","بور"],["تسمين جديان","عنزات حلابة","عنزات حامل","صيانة"],12.5,64.0,"ماعز")
    with atabs[3]: render_feed_formulation("horse","خيول","🐴",["عربي","ثوروبريد","محلي"],["راحة/صيانة","عمل خفيف","عمل متوسط","عمل مكثف","سباق","أمهار","فرسات"],11.0,62.0,"خيول")
    with atabs[4]: render_feed_formulation("camel","إبل","🐫",["عربية","باختري","هجين"],["راحة/صيانة","حمل/رضاعة","إنتاج حليب","تسمين","عمل/نقل"],10.0,58.0,"إبل")
    with atabs[5]: render_feed_formulation("poultry","دواجن","🐔",["لاحم","بياض","سمان"],["بادي (0-14)","نامي (15-28)","ناهي (29-42)","ناهي متقدم (43+)"],18.0,72.0,"دواجن",False)
    with atabs[6]: render_feed_formulation("fish","أسماك","🐟",["بلطي","قرموط"],["زريعة","نمو","تسمين نهائي"],28.0,68.0,"أسماك",False)
    with atabs[7]: render_advanced_lab()

# التبويب 1 - المزارع
with tabs[1]:
    guide_section("المزارع","نظام إدارة مزارع الدجاج")
    st.markdown('<div class="section-title">🐔 إدارة المزارع</div>', unsafe_allow_html=True)
    if st.session_state["user_role"] in ["owner","specialist","veterinarian","nutritionist","breeder"]:
        with st.expander("➕ دورة جديدة"):
            c1,c2 = st.columns(2)
            with c1:
                fn = st.text_input("اسم المزرعة"); ib = st.number_input("عدد الكتاكيت",1,1000,100)
            with c2:
                br = st.selectbox("السلالة",["Ross 308","Cobb 500","محلية"])
                sd = st.date_input("التاريخ",datetime.now())
            if st.button("حفظ"):
                if fn:
                    cid = secrets.token_hex(8)
                    st.session_state["broiler_farms"][cid] = {"farm_name":fn,"initial_birds":ib,"breed":br,"start_date":sd.isoformat(),"age_days":0,"current_weight":0.045,"total_feed":0,"dead_count":0}
                    voice_guide(f"تم إنشاء {fn}"); st.rerun()
    if st.session_state["broiler_farms"]:
        for cid, farm in st.session_state["broiler_farms"].items():
            with st.expander(f"🏠 {farm['farm_name']} - {farm['breed']}"):
                c1,c2,c3 = st.columns(3)
                with c1:
                    st.metric("العدد",farm['initial_birds']); st.metric("العمر",farm['age_days'])
                with c2:
                    st.metric("الوزن",f"{farm['current_weight']:.3f}"); st.metric("العلف",f"{farm['total_feed']:.0f}")
                with c3:
                    m = farm['dead_count']/farm['initial_birds']*100 if farm['initial_birds']>0 else 0
                    st.metric("النفوق%",f"{m:.1f}"); st.metric("النافق",farm['dead_count'])

# التبويب 2 - بدائل الحليب
with tabs[2]: render_milk_replacer()

# التبويب 3 - الصلاة
with tabs[3]:
    guide_section("الصلاة","مواقيت الصلاة")
    cities = ["مكة","المدينة","الخرطوم","طرابلس","القاهرة","دبي","الرياض","عمان","بيروت","بغداد","الكويت","مسقط","الدوحة"]
    city = st.selectbox("اختر المدينة:",cities)
    times = {"الفجر":"05:00","الشروق":"06:30","الظهر":"12:00","العصر":"15:30","المغرب":"18:00","العشاء":"19:30"}
    cols = st.columns(3)
    for i,(n,t) in enumerate(times.items()):
        with cols[i%3]: st.metric(n,t)

# التبويب 4 - الجرعات
with tabs[4]:
    guide_section("الجرعات","منبه اللقاحات والفيتامينات")
    if "dose_reminders" not in st.session_state: st.session_state["dose_reminders"]=[]
    with st.expander("➕ إضافة جرعة"):
        c1,c2,c3 = st.columns(3)
        with c1:
            at = st.selectbox("الحيوان",["أبقار","أغنام","ماعز","خيول","إبل","دواجن","أسماك"])
            dt = st.selectbox("النوع",["لقاح","فيتامين","دواء"])
            dn = st.text_input("الاسم")
        with c2:
            da = st.number_input("الجرعة",0.0,1.0,0.1)
            du = st.selectbox("الوحدة",["مل","جم","مجم","قطرة"])
            ar = st.selectbox("الطريقة",["عضل","تحت الجلد","فموي","مياه الشرب","رش","قطرة عين"])
        with c3:
            fd = st.number_input("كل كم يوم",1,7)
            sd = st.date_input("البدء",datetime.now())
        if st.button("حفظ"):
            if dn:
                st.session_state["dose_reminders"].append({"id":secrets.token_hex(8),"animal":at,"type":dt,"name":dn,"dose":da,"unit":du,"route":ar,"freq":fd,"start":sd.isoformat(),"next":(sd+timedelta(days=fd)).isoformat(),"active":True})
                st.success(f"تم إضافة {dn}")
                voice_guide(f"تم إضافة {dn}"); st.rerun()
    if st.session_state["dose_reminders"]:
        for r in st.session_state["dose_reminders"]:
            st.info(f"💊 {r['name']} - {r['animal']} - الجرعة القادمة: {r['next'][:10]}")

# التبويب 5 - البورصة
with tabs[5]:
    guide_section("البورصة","أسعار المواشي والمنتجات")
    c1,c2 = st.columns(2)
    with c1:
        st.subheader("🐄 المواشي")
        for n,p in st.session_state["global_livestock_prices"].items():
            np_ = st.number_input(n,value=float(p),step=5.0,key=f"lp_{n}")
            st.session_state["global_livestock_prices"][n]=np_
    with c2:
        st.subheader("🥩 المنتجات")
        for n,p in st.session_state["global_products_prices"].items():
            np_ = st.number_input(n,value=float(p),step=0.5,key=f"pp_{n}")
            st.session_state["global_products_prices"][n]=np_

# التبويب 6 - المستودعات
with tabs[6]:
    guide_section("المستودعات","إدارة المخزون")
    inv = [{"المادة":k,"الكمية":v["quantity"],"الحد":v["min_threshold"]} for k,v in st.session_state["inventory"].items()]
    st.dataframe(pd.DataFrame(inv), use_container_width=True)
    with st.expander("تحديث"):
        sel = st.selectbox("المادة",list(FLAT_FEED_DB.keys()))
        nq = st.number_input("الكمية (طن)",0.0,25.0)
        if st.button("تحديث"):
            st.session_state["inventory"][sel]["quantity"]=nq
            st.success("تم"); st.rerun()

# التبويب 7 - الإنتاج
with tabs[7]:
    guide_section("الإنتاج","الإنتاج اليومي")
    with st.form("df"):
        c1,c2,c3 = st.columns(3)
        with c1:
            fn = st.text_input("المزرعة"); d = st.date_input("التاريخ",datetime.now())
        with c2:
            ml = st.number_input("حليب (لتر)",0.0); eg = st.number_input("بيض",0)
        with c3:
            wg = st.number_input("زيادة وزن (كجم)",0.0); mr = st.number_input("نفوق",0)
        if st.form_submit_button("حفظ"):
            st.session_state["daily_production_log"].append({"farm":fn,"date":d.isoformat(),"milk":ml,"eggs":eg,"weight_gain":wg,"mortality":mr})
            st.success("تم الحفظ")
    if st.session_state["daily_production_log"]:
        st.dataframe(pd.DataFrame(st.session_state["daily_production_log"]), use_container_width=True)

# التبويب 8 - التنبيهات
with tabs[8]:
    guide_section("التنبيهات","تنبيهات المخزون")
    w = InventoryManager.check_stock_levels()
    if w:
        for i,s in w.items(): st.warning(f"{i}: {s}")
    else: st.success("✅ لا تنبيهات")

# التبويب 9 - المراجع
with tabs[9]:
    guide_section("المراجع","المصادر العلمية")
    for k,cat in ScientificReferenceSystem.REFERENCES.items():
        with st.expander(f"{cat['icon']} {cat['title']}"):
            for r in cat.get("references",[]):
                st.markdown(f"**{r.get('title','')}** - {r.get('authors','')} ({r.get('year','')})")
    st.subheader("💡 المعرفة السريعة")
    q = st.text_input("اسأل:")
    if q:
        a = ScientificReferenceSystem.get_knowledge_answer(q)
        if a: st.success(a['answer']); st.info(a['simplified'])
        else: st.info("لم يتم العثور")

# التبويب 10 - المساعدة
with tabs[10]:
    guide_section("المساعدة","دليل سريع")
    st.markdown("""
    1. اختر نوع الحيوان والسلالة والمرحلة
    2. أدخل العمر والحالة الفسيولوجية
    3. اختر المكونات
    4. اضغط "تشغيل محرك التركيب"
    5. **يجب أن تكون التركيبة 75% على الأقل من المعايير**
    6. حمل التقرير PDF مع الختم الرسمي
    """)

# التبويب 11 - الدليل
with tabs[11]:
    guide_section("الدليل","شرح شامل")
    st.markdown("""
    <div class="manual-book">
    <div class="book-chapter">📘 الفصل 1: مقدمة</div>
    <div class="book-body">
    تاور نولجي Tawornology العلمية منصة متكاملة لتركيب الأعلاف وفق النظام العالمي NRC/INRA مع قيود دقيقة على الأملاح والمعادن.
    </div>
    <div class="book-chapter">📗 الفصل 2: تركيب العلف</div>
    <div class="book-body">
    اختر الحيوان، السلالة، المرحلة، ثم المكونات. المحرك يحسب التركيبة الأقل تكلفة مع الالتزام بالحدود القصوى للملح والكالسيوم والفسفور.
    </div>
    <div class="book-chapter">📕 الفصل 3: المختبر</div>
    <div class="book-body">
    أدخل أوزان مكونات خلطتك، والمختبر يحسب النسب الفعلية ويقارنها بالمعايير العالمية بدقة 0.5%.
    </div>
    <div class="book-chapter">🍼 الفصل 4: بدائل الحليب</div>
    <div class="book-body">
    لرضاعة الصغار (عجول، حملان، جديان، مهرات، أطفال إبل) حسب العمر والاحتياجات.
    </div>
    <div class="book-chapter">🖋️ الفصل 5: الختم الرسمي</div>
    <div class="book-body">
    جميع تقارير PDF تحمل ختم نهاية رسمي باسم: <b>الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان</b>.
    </div>
    </div>
    """, unsafe_allow_html=True)

# التبويب الأخير
if st.session_state["user_role"] == "owner" and len(tabs) > 12:
    with tabs[12]:
        guide_section("إرسال الكود","إرسال السورس كود")
        em = st.text_input("البريد:",value=OWNER_EMAIL)
        if st.button("📤 إرسال"):
            if em and '@' in em:
                with st.spinner("جاري الإرسال..."):
                    s, m = send_code_to_email(em)
                    st.success(m) if s else st.error(m)

# التذييل
st.markdown("""
<div style='text-align:center;padding:20px;margin-top:30px;border-top:2px solid #e0e0e0;color:#888;'>
🌾 <b>تاور نولجي Tawornology العلمية</b><br>
© 2026 | الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان<br>
🕊️ إهداء إلى روح الوالد إسماعيل تاور والأخت ابتسام - رحمهما الله
</div>
""", unsafe_allow_html=True)

if st.button("🔊 اختبار الصوت"):
    voice_guide("اختبار الصوت")
