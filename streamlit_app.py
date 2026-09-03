# ============================================================================
# تاور نولجي Tawornology العلمية - الإصدار المتكامل النهائي 13.0
# ============================================================================
# 🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله
# 🕊️ اللهم اجعل قبرهما روضة من رياض الجنة واجمعنا بهما في الفردوس الأعلى
# ============================================================================
# هذا الإصدار يحتوي على جميع التحسينات:
# 1. تقرير التركيب PDF مع مقارنات قياسية (مثل المختبر)
# 2. تحسين شكل وتصميم ملفات PDF (ألوان، تنسيق، رموز)
# 3. نظام تركيب الأعلاف السائلة (بديل الحليب) للرضاعة
# المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور
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
# استيراد مكتبات معالجة اللغة العربية وتوليد PDF والصور
# =====================================================================
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4, landscape, letter
from reportlab.lib.units import inch, mm, cm
from reportlab.lib.colors import HexColor, black, white, grey, blue, red, green, orange, purple, teal, gold, lightgrey
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
import arabic_reshaper
from bidi.algorithm import get_display
import qrcode
from PIL import Image as PILImage
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle

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
# إعدادات النظام الأساسية
# =====================================================================
st.set_page_config(
    page_title="تاور نولجي Tawornology العلمية - للانتاج الحيواني وتركيب الاعلاف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def init_caching_system():
    return {
        "cache_hits": 0,
        "cache_misses": 0,
        "last_cleanup": datetime.now(),
        "cache_data": {}
    }
CACHE_SYSTEM = init_caching_system()

# =====================================================================
# أكواد الدخول
# =====================================================================
CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2024": {"role": "veterinarian", "name": "الطبيب البيطري", "level": 2},
    "2025": {"role": "nutritionist", "name": "أخصائي التغذية", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

# =====================================================================
# إعدادات البريد الإلكتروني
# =====================================================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"

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
# دوال الصوت
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
    except Exception as e:
        return None

def play_audio_b64(audio_b64):
    if audio_b64:
        st.components.v1.html(
            f'<audio autoplay><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mpeg"></audio>',
            height=0
        )
        return True
    return False

def voice_guide_sequential(messages, lang="ar", delay_between=1.5):
    if not GTTS_AVAILABLE:
        st.warning("⚠️ الصوت غير متاح")
        return
    for msg in messages:
        if msg:
            audio_b64 = text_to_speech_base64(msg, lang)
            if audio_b64:
                play_audio_b64(audio_b64)
                time.sleep(delay_between)

def voice_guide(message, lang="ar"):
    if not GTTS_AVAILABLE or not message:
        return
    audio_b64 = text_to_speech_base64(message, lang)
    if audio_b64:
        play_audio_b64(audio_b64)

def voice_welcome(role):
    messages = {
        "owner": ["مرحباً بك في تاور نولجي، أيها الاختصاصي م. عبد القادر إسماعيل تاور."],
        "specialist": ["مرحباً أيها المختص."],
        "veterinarian": ["مرحباً أيها الطبيب البيطري."],
        "nutritionist": ["مرحباً أيها أخصائي التغذية."],
        "breeder": ["مرحباً أيها المربي."],
        "public": ["مرحباً بك زائراً في تاور نولجي."]
    }
    voice_guide_sequential(messages.get(role, ["مرحباً بك في تاور نولجي."]))

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

# =====================================================================
# دوال إرسال الكود
# =====================================================================
def send_code_to_email(receiver_email):
    if receiver_email.strip().lower() != OWNER_EMAIL.strip().lower():
        return False, "❌ عذراً، الإرسال مسموح فقط للبريد: " + OWNER_EMAIL
    if not st.session_state.get("email_password"):
        st.session_state["email_password"] = st.text_input("🔑 كلمة مرور البريد الإلكتروني (App Password):", type="password")
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
    msg['Subject'] = "🌾 السورس كود - تاور نولجي Tawornology العلمية"
    body = f"""السلام عليكم ورحمة الله وبركاته،

مرفق مع هذه الرسالة السورس كود الكامل لمنصة تاور نولجي Tawornology العلمية.

📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔑 التوقيع الرقمي: {file_hash}
👨‍💻 المشرف: الاختصاصي م. عبد القادر إسماعيل تاور
🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله

عدد الأسطر: ~4700 سطر
"""
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
        return True, "✅ تم إرسال الكود بنجاح إلى " + receiver_email
    except Exception as e:
        return False, f"❌ فشل الإرسال: {str(e)}. تأكد من كلمة المرور وتفعيل تطبيق البريد."

# =====================================================================
# معالج النصوص العربية
# =====================================================================
class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=2000)
    def fix_arabic_text(text):
        if not text:
            return ""
        reshaped_text = arabic_reshaper.reshape(str(text))
        return get_display(reshaped_text)

arabic_processor = ArabicTextProcessor()

# =====================================================================
# قاعدة البيانات (SQLite) - مختصرة
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
            is_active INTEGER DEFAULT 1, is_public INTEGER DEFAULT 0
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS farms (
            farm_id TEXT PRIMARY KEY, farm_name TEXT UNIQUE, farm_type TEXT,
            owner_name TEXT, owner_phone TEXT, location TEXT, area REAL,
            created_date TEXT, last_updated TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS production_cycles (
            cycle_id TEXT PRIMARY KEY, farm_id TEXT, cycle_type TEXT,
            start_date TEXT, end_date TEXT, initial_count INTEGER, breed TEXT,
            target_weight REAL, target_age INTEGER, status TEXT, notes TEXT,
            FOREIGN KEY (farm_id) REFERENCES farms(farm_id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS daily_records (
            record_id TEXT PRIMARY KEY, cycle_id TEXT, record_date TEXT,
            age_days INTEGER, live_birds INTEGER, avg_weight REAL,
            min_weight REAL, max_weight REAL, feed_consumed REAL,
            water_consumed REAL, dead_count INTEGER, culled_count INTEGER,
            temperature REAL, humidity REAL, ventilation_status TEXT,
            litter_quality TEXT, feed_conversion REAL, mortality_rate REAL,
            notes TEXT, FOREIGN KEY (cycle_id) REFERENCES production_cycles(cycle_id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas (
            formula_id TEXT PRIMARY KEY, formula_name TEXT, animal_type TEXT,
            breed TEXT, stage TEXT, target_dp REAL, target_se REAL,
            ingredients TEXT, total_cost REAL, cost_per_ton REAL,
            created_by TEXT, created_date TEXT, is_approved INTEGER DEFAULT 0,
            usage_count INTEGER DEFAULT 0
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS milk_replacers (
            formula_id TEXT PRIMARY KEY, formula_name TEXT, animal_type TEXT,
            age_days INTEGER, target_protein REAL, target_fat REAL,
            ingredients TEXT, total_cost REAL, cost_per_liter REAL,
            created_by TEXT, created_date TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS price_history (
            record_id TEXT PRIMARY KEY, ingredient_name TEXT, price REAL,
            currency TEXT, country TEXT, city TEXT, record_date TEXT,
            recorded_by TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT PRIMARY KEY, item_name TEXT UNIQUE, quantity REAL,
            min_threshold REAL, unit TEXT, last_updated TEXT, supplier TEXT
        )''')
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
        return True
    
    def get_records(self, table: str, conditions: dict = None):
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
    
    def update_record(self, table: str, data: dict, condition: dict):
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
# مدير المصادقة
# =====================================================================
class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self._create_default_users()
        self._create_public_user()
    
    def _create_default_users(self):
        default_users = [
            ('admin', 'admin123', 'owner', 'مدير النظام - م. عبد القادر إسماعيل تاور', 'admin@tawornology.com', '+249123456789', 'إدارة الأنظمة', 10),
            ('specialist', 'spec123', 'specialist', 'المختص العام', 'specialist@tawornology.com', '+249123456788', 'تغذية وإنتاج', 8),
        ]
        for username, password, role, full_name, email, phone, specialty, experience in default_users:
            users = self.db.execute_query("SELECT * FROM users WHERE username=?", (username,))
            if not users:
                self.create_user(username, password, role, full_name, email, phone, specialty, experience)
    
    def _create_public_user(self):
        users = self.db.execute_query("SELECT * FROM users WHERE username='public'")
        if not users:
            self.create_user('public', 'public123', 'public', 'زائر', 'public@tawornology.com', '+249123456780', 'عام', 0)
            self.db.update_record('users', {'is_public': 1}, {'username': 'public'})
    
    def create_user(self, username, password, role, full_name, email, phone, specialty="", experience=0):
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
            'specialty': specialty,
            'experience_years': experience,
            'created_date': datetime.now().isoformat(),
            'last_login': '',
            'is_active': 1,
            'is_public': 1 if role == 'public' else 0
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
                    'user_id': user[0],
                    'username': user[1],
                    'role': user[3],
                    'full_name': user[4],
                    'email': user[5],
                    'phone': user[6],
                    'specialty': user[7],
                    'experience_years': user[8]
                }
        return None
    
    def login_public(self):
        users = self.db.execute_query("SELECT * FROM users WHERE username='public' AND is_active=1")
        if users:
            user = users[0]
            self.db.update_record('users', {'last_login': datetime.now().isoformat()}, {'user_id': user[0]})
            return {
                'user_id': user[0],
                'username': user[1],
                'role': 'public',
                'full_name': 'زائر',
                'email': user[5],
                'phone': user[6],
                'specialty': 'عام',
                'experience_years': 0
            }
        self._create_public_user()
        return self.login_public()

# =====================================================================
# نظام المراجع العلمية (مختصر)
# =====================================================================
class ScientificReferenceSystem:
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان",
            "icon": "📚",
            "references": [
                {"id": "REF001", "authors": "McDonald, P., Edwards, R.A., Greenhalgh, J.F.D., Morgan, C.A.",
                 "year": 2011, "title": "Animal Nutrition", "publisher": "Pearson Education",
                 "summary": "المرجع الأساسي في تغذية الحيوان."}
            ]
        },
        "protein_amino_acids": {
            "title": "البروتين والأحماض الأمينية",
            "icon": "🧬",
            "references": [
                {"id": "REF003", "authors": "NRC (National Research Council)",
                 "year": 2012, "title": "Nutrient Requirements of Swine",
                 "publisher": "National Academies Press", "summary": "المرجع الرسمي لمتطلبات الخنازير."}
            ]
        },
        "poultry": {
            "title": "تغذية الدواجن",
            "icon": "🐔",
            "references": [
                {"id": "REF010", "authors": "Leeson, S., Summers, J.D.",
                 "year": 2009, "title": "Commercial Poultry Nutrition",
                 "publisher": "Nottingham University Press", "summary": "المرجع العملي في تغذية الدواجن."}
            ]
        },
        "ruminants": {
            "title": "تغذية المجترات",
            "icon": "🐄",
            "references": [
                {"id": "REF012", "authors": "Church, D.C.",
                 "year": 1993, "title": "The Ruminant Animal",
                 "publisher": "Waveland Press", "summary": "المرجع الشامل في فسيولوجيا الهضم والتغذية للمجترات."}
            ]
        },
        "horses": {
            "title": "تغذية الخيول",
            "icon": "🐴",
            "references": [
                {"id": "REF015", "authors": "NRC (National Research Council)",
                 "year": 2007, "title": "Nutrient Requirements of Horses",
                 "publisher": "National Academies Press", "summary": "المرجع الأساسي في تغذية الخيول."}
            ]
        },
        "camels": {
            "title": "تغذية الإبل",
            "icon": "🐫",
            "references": [
                {"id": "REF030", "authors": "Faye, B., Bengoumi, M.",
                 "year": 2018, "title": "Camel Nutrition and Feeding",
                 "publisher": "FAO", "summary": "المرجع الأساسي في تغذية الإبل."}
            ]
        },
        "broiler": {
            "title": "إنتاج الدجاج اللاحم",
            "icon": "🐔",
            "references": [
                {"id": "REF020", "authors": "Ross 308 Broiler Management Guide",
                 "year": 2020, "title": "Ross Broiler Management Handbook",
                 "publisher": "Aviagen", "summary": "الدليل الشامل لإدارة الدجاج اللاحم."}
            ]
        },
        "digestible_protein": {
            "title": "البروتين المهضوم",
            "icon": "🧪",
            "references": [
                {"id": "REF023", "authors": "INRA (Institut National de la Recherche Agronomique)",
                 "year": 2007, "title": "INRA Feeding System for Ruminants",
                 "publisher": "Wageningen Academic Publishers", "summary": "النظام الفرنسي لتغذية المجترات."}
            ]
        }
    }
    
    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف.",
            "reference": "REF023",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (SE) هو مقياس لكمية الطاقة التي يوفرها العلف للحيوان.",
            "reference": "REF006",
            "simplified": "معادل النشاء يقيس كمية الطاقة في العلف."
        },
        "كيف يتم تركيب العلف الأمثل": {
            "answer": "يتم تركيب العلف الأمثل باستخدام محرك الاستمثال الخطي (Linear Programming).",
            "reference": "REF024",
            "simplified": "نستخدم برنامجاً ذكياً يحسب أرخص خلطة علفية."
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
        question_lower = question.lower()
        for key, value in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            if key in question_lower:
                return {
                    "answer": value["answer"],
                    "simplified": value.get("simplified", value["answer"])
                }
        return None

# =====================================================================
# مولد PDF المتقدم (مع تحسينات كبيرة)
# =====================================================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        font_paths = ["Amiri-Regular.ttf", "Cairo-Regular.ttf", "arial.ttf"]
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
                    self.font_name = 'ArabicFont'
                    break
                except:
                    pass
        self.styles = self._create_styles()
    
    def _create_styles(self):
        styles = {}
        styles['title'] = ParagraphStyle('title', fontName=self.font_name, fontSize=26, alignment=TA_CENTER, textColor=HexColor('#1b5e20'), spaceAfter=25, leading=32, fontweight='bold')
        styles['subtitle'] = ParagraphStyle('subtitle', fontName=self.font_name, fontSize=16, alignment=TA_CENTER, textColor=HexColor('#2e7d32'), spaceAfter=15, leading=20)
        styles['heading'] = ParagraphStyle('heading', fontName=self.font_name, fontSize=15, alignment=TA_RIGHT, textColor=HexColor('#1b5e20'), spaceAfter=12, leading=20, fontweight='bold')
        styles['body'] = ParagraphStyle('body', fontName=self.font_name, fontSize=11, alignment=TA_RIGHT, textColor=HexColor('#333333'), spaceAfter=6, leading=16)
        styles['footer'] = ParagraphStyle('footer', fontName=self.font_name, fontSize=8, alignment=TA_CENTER, textColor=HexColor('#888888'), spaceAfter=0, leading=10)
        styles['highlight'] = ParagraphStyle('highlight', fontName=self.font_name, fontSize=11, alignment=TA_RIGHT, textColor=HexColor('#1565C0'), spaceAfter=6, leading=16, fontweight='bold')
        styles['good'] = ParagraphStyle('good', fontName=self.font_name, fontSize=11, alignment=TA_RIGHT, textColor=HexColor('#2e7d32'), spaceAfter=6, leading=16, fontweight='bold')
        styles['warning'] = ParagraphStyle('warning', fontName=self.font_name, fontSize=11, alignment=TA_RIGHT, textColor=HexColor('#e65100'), spaceAfter=6, leading=16, fontweight='bold')
        return styles
    
    def _get_grade_style(self, deviation):
        if abs(deviation) <= 5:
            return 'good', '✅ ممتاز'
        elif abs(deviation) <= 10:
            return 'warning', '👍 جيد'
        else:
            return 'body', '⚠️ يحتاج تحسين'
    
    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, user_name, standard=None, include_charts=True, extra_info=None):
        """تقرير تركيب العلف مع مقارنات قياسية (محسّن)"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        
        def p(text, style='body'):
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, self.styles.get(style, self.styles['body']))
        
        # العنوان
        story.append(p("🌾 تاور نولجي Tawornology العلمية", 'title'))
        story.append(p("📄 تقرير فني شامل - تقرير التركيب المتقدم", 'subtitle'))
        story.append(Spacer(1, 10))
        
        # معلومات عامة
        info_data = [
            ['👨‍💻 المشرف العام', 'الاختصاصي م. عبد القادر إسماعيل تاور'],
            ['📌 الموقع الجغرافي', city],
            ['🐾 الفصيل المستهدف', breed],
            ['📅 تاريخ الإصدار', datetime.now().strftime('%Y-%m-%d %H:%M')]
        ]
        if extra_info:
            for key, val in extra_info.items():
                if val:
                    info_data.append([key, val])
        t_info = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in info_data], colWidths=[200, 300])
        t_info.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#e8f5e9')),
            ('BACKGROUND',(0,1),(-1,-1),HexColor('#f5f5f5')),
            ('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),10),
            ('GRID',(0,0),(-1,-1),0.5,HexColor('#bdbdbd')),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ]))
        story.append(t_info)
        story.append(Spacer(1, 15))
        
        # النتائج الرئيسية
        story.append(p("📊 النتائج الرئيسية:", 'heading'))
        results_data = [
            ['البروتين المهضوم (DP)', f'{target_dp:.2f}%'],
            ['معادل النشاء (SE)', f'{computed_se:.2f} وحدة'],
            ['التكلفة للطن', f'${cost:.2f} ({local_cost:,.2f} {local_sym})']
        ]
        t_results = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in results_data], colWidths=[250, 250])
        t_results.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),11),
            ('GRID',(0,0),(-1,-1),1,HexColor('#2e7d32')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')])
        ]))
        story.append(t_results)
        story.append(Spacer(1, 15))
        
        # المقارنة مع المعايير القياسية (جديد)
        if standard:
            story.append(p("📏 مقارنة مع المعايير القياسية:", 'heading'))
            comp_data = [['المقياس', 'المحسوب', 'القياسي', 'الانحراف %', 'التقييم']]
            if 'dp' in standard:
                dev = ((target_dp - standard['dp']) / standard['dp']) * 100 if standard['dp'] > 0 else 0
                style_name, grade = self._get_grade_style(dev)
                comp_data.append(['البروتين المهضوم (DP)', f"{target_dp:.2f}%", f"{standard['dp']:.2f}%", f"{dev:.1f}", grade])
            if 'se' in standard:
                dev = ((computed_se - standard['se']) / standard['se']) * 100 if standard['se'] > 0 else 0
                style_name, grade = self._get_grade_style(dev)
                comp_data.append(['معادل النشاء (SE)', f"{computed_se:.2f}", f"{standard['se']:.2f}", f"{dev:.1f}", grade])
            if 'cp' in standard:
                cp_calc = target_dp / 0.80
                dev = ((cp_calc - standard['cp']) / standard['cp']) * 100 if standard['cp'] > 0 else 0
                style_name, grade = self._get_grade_style(dev)
                comp_data.append(['البروتين الخام (CP)', f"{cp_calc:.2f}%", f"{standard['cp']:.2f}%", f"{dev:.1f}", grade])
            
            t_comp = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in comp_data], colWidths=[120, 100, 100, 100, 100])
            t_comp.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),
                ('TEXTCOLOR',(0,0),(-1,0),white),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('FONTNAME',(0,0),(-1,-1),self.font_name),
                ('FONTSIZE',(0,0),(-1,-1),10),
                ('GRID',(0,0),(-1,-1),0.5,HexColor('#bdbdbd')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')])
            ]))
            story.append(t_comp)
            story.append(Spacer(1, 10))
            
            # تقييم عام
            total_dev = 0
            count = 0
            if 'dp' in standard:
                total_dev += abs(((target_dp - standard['dp']) / standard['dp']) * 100)
                count += 1
            if 'se' in standard:
                total_dev += abs(((computed_se - standard['se']) / standard['se']) * 100)
                count += 1
            avg_dev = total_dev / count if count > 0 else 0
            
            if avg_dev <= 5:
                story.append(p("⭐ التقييم العام: ممتاز - الخلطة متوافقة تماماً مع المعايير القياسية", 'good'))
            elif avg_dev <= 10:
                story.append(p("⭐ التقييم العام: جيد - الخلطة قريبة من المعايير القياسية", 'warning'))
            else:
                story.append(p("⭐ التقييم العام: يحتاج تحسين - يوصى بمراجعة النسب", 'body'))
            story.append(Spacer(1, 10))
        
        # المكونات
        story.append(PageBreak())
        story.append(p("📋 المقادير المعتمدة لتركيب الطن الواحد:", 'heading'))
        story.append(Spacer(1, 10))
        ing_data = [['المكون', 'النسبة %', 'كجم/طن']]
        for ing, pct in formula.items():
            ing_data.append([ing, f'{pct:.2f}%', f'{pct*10:.1f}'])
        t_ing = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in ing_data], colWidths=[180, 150, 150])
        t_ing.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),10),
            ('GRID',(0,0),(-1,-1),0.5,HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')])
        ]))
        story.append(t_ing)
        story.append(Spacer(1, 15))
        
        # المخطط البياني
        if include_charts and len(formula) > 1:
            try:
                fig, ax = plt.subplots(figsize=(6, 3.5))
                names = list(formula.keys())
                vals = list(formula.values())
                colors = ['#1b5e20','#2e7d32','#388e3c','#43a047','#4caf50','#66bb6a','#81c784','#a5d6a7']
                ax.pie(vals, labels=None, autopct='%1.1f%%', colors=colors[:len(names)], startangle=90)
                ax.legend([arabic_processor.fix_arabic_text(n) for n in names], title=arabic_processor.fix_arabic_text("المكونات"), loc='center left', bbox_to_anchor=(1,0,0.5,1), fontsize=8)
                ax.set_title(arabic_processor.fix_arabic_text('📊 توزيع المكونات'), fontsize=12, fontweight='bold')
                buf_img = io.BytesIO()
                plt.tight_layout()
                plt.savefig(buf_img, format='png', dpi=100, bbox_inches='tight', facecolor='white')
                plt.close()
                buf_img.seek(0)
                story.append(Image(buf_img, width=400, height=230))
            except:
                pass
        
        # التوصيات
        story.append(PageBreak())
        story.append(p("📌 التوصيات الفنية:", 'heading'))
        recommendations = [
            "• يوصى بإضافة الإنزيمات لتحسين الهضم والاستفادة من العلف.",
            "• يجب مراقبة جودة المواد الخام بشكل دوري وإجراء تحاليل مخبرية.",
            "• يجب تخزين العلف في مكان جاف بعيداً عن الرطوبة والحشرات.",
            "• يوصى بتقسيم العلف على عدة وجبات لتحسين الهضم والاستفادة."
        ]
        if standard and avg_dev > 10:
            recommendations.append("• ⚠️ يوصى بمراجعة نسب البروتين والطاقة لتقريب الخلطة من المعايير القياسية.")
        for rec in recommendations:
            story.append(p(rec))
        
        # الخاتمة والتوقيع
        story.append(Spacer(1, 20))
        story.append(p("📝 خاتمة التقرير", 'heading'))
        story.append(Spacer(1, 10))
        story.append(p("تم إعداد هذا التقرير الفني بناءً على تحليل دقيق للاحتياجات الغذائية للفصيل المستهدف."))
        story.append(Spacer(1, 20))
        story.append(p("مع خالص التحية والتقدير،", 'body'))
        story.append(Spacer(1, 10))
        story.append(p("الاختصاصي م. عبد القادر إسماعيل تاور", 'body'))
        story.append(Spacer(1, 15))
        story.append(p("تم التوليد بواسطة تاور نولجي Tawornology العلمية © 2026", 'footer'))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_lab_report(self, analysis_results, animal_type, stage, user_name, standard=None, evaluation=None):
        """تقرير المختبر المتقدم (محسّن)"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        
        def p(text, style='body'):
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, self.styles.get(style, self.styles['body']))
        
        story.append(p("🔬 تقرير التحليل المخبري المتقدم", 'title'))
        story.append(p("تاور نولجي Tawornology العلمية", 'subtitle'))
        story.append(Spacer(1, 5))
        story.append(p(f"👨‍💻 المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور", 'body'))
        story.append(p(f"🐾 الحيوان: {animal_type} | المرحلة: {stage}", 'body'))
        story.append(p(f"📅 تاريخ التحليل: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 'body'))
        story.append(Spacer(1, 15))
        
        if analysis_results:
            # جدول المكونات
            if 'components' in analysis_results and analysis_results['components']:
                story.append(p("📦 المكونات المدخلة:", 'heading'))
                comp_data = [['المادة', 'الوزن (كجم)', 'النسبة %']]
                total_weight = sum(analysis_results['components'].values())
                for name, weight in analysis_results['components'].items():
                    if weight > 0:
                        pct = (weight / total_weight) * 100
                        comp_data.append([name, f"{weight:.1f}", f"{pct:.2f}"])
                t_comp = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in comp_data], colWidths=[180, 120, 120])
                t_comp.setStyle(TableStyle([
                    ('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),
                    ('TEXTCOLOR',(0,0),(-1,0),white),
                    ('ALIGN',(0,0),(-1,-1),'CENTER'),
                    ('FONTNAME',(0,0),(-1,-1),self.font_name),
                    ('FONTSIZE',(0,0),(-1,-1),10),
                    ('GRID',(0,0),(-1,-1),0.5,HexColor('#bdbdbd')),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')])
                ]))
                story.append(t_comp)
                story.append(Spacer(1, 10))
            
            # النتائج المحسوبة
            story.append(p("📊 النتائج المحسوبة:", 'heading'))
            results_data = [['العنصر', 'القيمة']]
            if 'cp' in analysis_results:
                results_data.append(['البروتين الخام (CP)', f"{analysis_results['cp']:.2f}%"])
            if 'dp' in analysis_results:
                results_data.append(['البروتين المهضوم (DP)', f"{analysis_results['dp']:.2f}%"])
            if 'se' in analysis_results:
                results_data.append(['معادل النشاء (SE)', f"{analysis_results['se']:.2f} وحدة"])
            t_results = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in results_data], colWidths=[250, 250])
            t_results.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),HexColor('#1565C0')),
                ('TEXTCOLOR',(0,0),(-1,0),white),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('FONTNAME',(0,0),(-1,-1),self.font_name),
                ('FONTSIZE',(0,0),(-1,-1),11),
                ('GRID',(0,0),(-1,-1),1,HexColor('#1565C0'))
            ]))
            story.append(t_results)
            story.append(Spacer(1, 10))
            
            # المقارنة مع المعايير
            if standard:
                story.append(p("📏 مقارنة مع المعايير القياسية:", 'heading'))
                comp_data = [['المقياس', 'المحسوب', 'القياسي', 'الانحراف %', 'التقييم']]
                if 'dp' in analysis_results and 'dp' in standard:
                    dev = ((analysis_results['dp'] - standard['dp']) / standard['dp']) * 100 if standard['dp'] > 0 else 0
                    style_name, grade = self._get_grade_style(dev)
                    comp_data.append(['DP', f"{analysis_results['dp']:.2f}%", f"{standard['dp']:.2f}%", f"{dev:.1f}", grade])
                if 'se' in analysis_results and 'se' in standard:
                    dev = ((analysis_results['se'] - standard['se']) / standard['se']) * 100 if standard['se'] > 0 else 0
                    style_name, grade = self._get_grade_style(dev)
                    comp_data.append(['SE', f"{analysis_results['se']:.2f}", f"{standard['se']:.2f}", f"{dev:.1f}", grade])
                if 'cp' in analysis_results and 'cp' in standard:
                    dev = ((analysis_results['cp'] - standard['cp']) / standard['cp']) * 100 if standard['cp'] > 0 else 0
                    style_name, grade = self._get_grade_style(dev)
                    comp_data.append(['CP', f"{analysis_results['cp']:.2f}%", f"{standard['cp']:.2f}%", f"{dev:.1f}", grade])
                t_comp = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in comp_data], colWidths=[100, 100, 100, 100, 100])
                t_comp.setStyle(TableStyle([
                    ('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),
                    ('TEXTCOLOR',(0,0),(-1,0),white),
                    ('ALIGN',(0,0),(-1,-1),'CENTER'),
                    ('FONTNAME',(0,0),(-1,-1),self.font_name),
                    ('FONTSIZE',(0,0),(-1,-1),10),
                    ('GRID',(0,0),(-1,-1),0.5,HexColor('#bdbdbd')),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')])
                ]))
                story.append(t_comp)
                story.append(Spacer(1, 10))
            
            # التقييم النهائي
            if evaluation:
                story.append(p("⭐ التقييم النهائي:", 'heading'))
                eval_data = [['المقياس', 'التقييم']]
                for key, val in evaluation.items():
                    if val:
                        eval_data.append([key, val])
                t_eval = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in eval_data], colWidths=[200, 200])
                t_eval.setStyle(TableStyle([
                    ('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),
                    ('TEXTCOLOR',(0,0),(-1,0),white),
                    ('ALIGN',(0,0),(-1,-1),'CENTER'),
                    ('FONTNAME',(0,0),(-1,-1),self.font_name),
                    ('FONTSIZE',(0,0),(-1,-1),10),
                    ('GRID',(0,0),(-1,-1),0.5,HexColor('#bdbdbd'))
                ]))
                story.append(t_eval)
                story.append(Spacer(1, 10))
            
            # المخطط البياني
            if standard and 'dp' in analysis_results and 'se' in analysis_results:
                try:
                    fig, ax = plt.subplots(figsize=(5, 3))
                    categories = ['DP', 'SE', 'CP']
                    calculated = [analysis_results.get('dp', 0), analysis_results.get('se', 0), analysis_results.get('cp', 0)]
                    standard_vals = [standard.get('dp', 0), standard.get('se', 0), standard.get('cp', 0)]
                    x = np.arange(len(categories))
                    width = 0.35
                    ax.bar(x - width/2, calculated, width, label='المحسوب', color='#2e7d32')
                    ax.bar(x + width/2, standard_vals, width, label='القياسي', color='#1565C0')
                    ax.set_xticks(x)
                    ax.set_xticklabels(categories)
                    ax.legend(loc='upper left')
                    ax.set_title('مقارنة القيم المحسوبة مع المعايير القياسية')
                    ax.grid(axis='y', linestyle='--', alpha=0.7)
                    buf_img = io.BytesIO()
                    plt.tight_layout()
                    plt.savefig(buf_img, format='png', dpi=100, bbox_inches='tight')
                    plt.close()
                    buf_img.seek(0)
                    story.append(Image(buf_img, width=400, height=220))
                except:
                    pass
            
            # التوصيات
            story.append(Spacer(1, 10))
            story.append(p("📌 التوصيات المخبرية:", 'heading'))
            for rec in ["• يوصى بإعادة التحليل بعد أي تعديل على الخلطة.", "• يجب مراجعة نسب البروتين والطاقة حسب احتياجات الحيوان.", "• يوصى بالتواصل مع أخصائي التغذية لتعديل الخلطة حسب النتائج."]:
                story.append(p(rec))
        
        # التوقيع
        story.append(Spacer(1, 20))
        story.append(p("مع خالص التحية والتقدير،", 'body'))
        story.append(Spacer(1, 10))
        story.append(p("الاختصاصي م. عبد القادر إسماعيل تاور", 'body'))
        story.append(Spacer(1, 15))
        story.append(p("تم التوليد بواسطة تاور نولجي Tawornology العلمية © 2026", 'footer'))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_milk_replacer_report(self, formula, animal_type, age_days, target_protein, target_fat, cost_per_liter, user_name, extra_info=None):
        """تقرير بديل الحليب السائل"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        
        def p(text, style='body'):
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, self.styles.get(style, self.styles['body']))
        
        story.append(p("🥛 تاور نولجي Tawornology العلمية", 'title'))
        story.append(p("🍼 تقرير تركيب بديل الحليب السائل", 'subtitle'))
        story.append(Spacer(1, 10))
        
        info_data = [
            ['👨‍💻 المشرف العام', 'الاختصاصي م. عبد القادر إسماعيل تاور'],
            ['🐾 نوع الحيوان', animal_type],
            ['📅 العمر (يوم)', str(age_days)],
            ['📅 تاريخ الإصدار', datetime.now().strftime('%Y-%m-%d %H:%M')]
        ]
        t_info = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in info_data], colWidths=[200, 300])
        t_info.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#e8f5e9')),
            ('BACKGROUND',(0,1),(-1,-1),HexColor('#f5f5f5')),
            ('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),10),
            ('GRID',(0,0),(-1,-1),0.5,HexColor('#bdbdbd')),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ]))
        story.append(t_info)
        story.append(Spacer(1, 15))
        
        # النتائج
        story.append(p("📊 المواصفات الغذائية:", 'heading'))
        results_data = [
            ['البروتين الخام', f"{target_protein:.2f}%"],
            ['الدهون الخام', f"{target_fat:.2f}%"],
            ['التكلفة لكل لتر', f"${cost_per_liter:.2f}"]
        ]
        t_results = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in results_data], colWidths=[250, 250])
        t_results.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#1565C0')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),11),
            ('GRID',(0,0),(-1,-1),1,HexColor('#1565C0'))
        ]))
        story.append(t_results)
        story.append(Spacer(1, 15))
        
        # المكونات
        story.append(p("📋 مكونات بديل الحليب لكل 100 لتر:", 'heading'))
        ing_data = [['المكون', 'الكمية (كجم)']]
        for ing, qty in formula.items():
            if qty > 0:
                ing_data.append([ing, f"{qty:.2f}"])
        t_ing = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in ing_data], colWidths=[250, 250])
        t_ing.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),10),
            ('GRID',(0,0),(-1,-1),0.5,HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')])
        ]))
        story.append(t_ing)
        
        # التوصيات
        story.append(PageBreak())
        story.append(p("📌 توصيات التغذية:", 'heading'))
        recs = [
            f"• يوصى بتقديم بديل الحليب بدرجة حرارة 38-40 درجة مئوية.",
            f"• عدد الوجبات اليومية: 3-4 وجبات للصغار.",
            f"• يجب خلط المسحوق جيداً مع الماء الدافئ حتى يذوب تماماً.",
            f"• يجب تحضير الكمية اللازمة للاستهلاك اليومي فقط."
        ]
        for rec in recs:
            story.append(p(rec))
        
        story.append(Spacer(1, 20))
        story.append(p("مع خالص التحية والتقدير،", 'body'))
        story.append(Spacer(1, 10))
        story.append(p("الاختصاصي م. عبد القادر إسماعيل تاور", 'body'))
        story.append(Spacer(1, 15))
        story.append(p("تم التوليد بواسطة تاور نولجي Tawornology العلمية © 2026", 'footer'))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# =====================================================================
# مكتبة الأعلاف الجافة (مختصرة)
# =====================================================================
FLAT_FEED_DB = {
    "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
    "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
    "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
    "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
    "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6},
    "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
    "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
    "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
    "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
    "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
    "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
    "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
    "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
    "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5},
    "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
    "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
    "إنزيم الفايتيز الزامي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
    "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
    "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
    "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
    "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
}

# =====================================================================
# مكتبة الأعلاف السائلة (بديل الحليب)
# =====================================================================
LIQUID_FEED_DB = {
    "مسحوق حليب خالي الدسم": {"CP": 35.0, "Fat": 1.0, "Lactose": 50.0, "ASH": 8.0, "Price": 2.50},
    "مسحوق حليب كامل الدسم": {"CP": 26.0, "Fat": 26.0, "Lactose": 38.0, "ASH": 6.0, "Price": 3.00},
    "بروتين مصل الحليب (WPC 80%)": {"CP": 80.0, "Fat": 4.0, "Lactose": 5.0, "ASH": 3.0, "Price": 5.00},
    "مسحوق اللبن (Skim Milk)": {"CP": 34.0, "Fat": 0.8, "Lactose": 51.0, "ASH": 7.5, "Price": 2.20},
    "زيت نباتي (صويا / ذرة)": {"CP": 0.0, "Fat": 99.0, "Lactose": 0.0, "ASH": 0.0, "Price": 1.80},
    "دهون حيوانية": {"CP": 0.0, "Fat": 98.0, "Lactose": 0.0, "ASH": 0.5, "Price": 1.50},
    "مستحلب (ليسيثين)": {"CP": 0.0, "Fat": 90.0, "Lactose": 0.0, "ASH": 2.0, "Price": 2.20},
    "فيتامينات ومعادن (Premix)": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "ASH": 50.0, "Price": 4.00},
    "مضاد حيوي (مبيد بكتيري)": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "ASH": 10.0, "Price": 8.00},
    "بروبيوتيك (بكتيريا نافعة)": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "ASH": 5.0, "Price": 6.00},
}

# =====================================================================
# المعايير القياسية للعناصر الغذائية (موسعة)
# =====================================================================
STANDARD_VALUES = {
    "أبقار": {
        "تسمين عجول": {"DP": 12.0, "SE": 68.0, "CP": 15.0},
        "حليب/إدرار": {"DP": 14.0, "SE": 70.0, "CP": 17.5},
        "صيانة": {"DP": 9.0, "SE": 60.0, "CP": 11.3}
    },
    "أغنام": {
        "تسمين حملان": {"DP": 13.0, "SE": 66.0, "CP": 16.3},
        "حليب/إدرار": {"DP": 14.5, "SE": 68.0, "CP": 18.1},
        "صيانة": {"DP": 8.5, "SE": 58.0, "CP": 10.6}
    },
    "ماعز": {
        "تسمين جديان": {"DP": 12.5, "SE": 64.0, "CP": 15.6},
        "حليب/إدرار": {"DP": 14.0, "SE": 66.0, "CP": 17.5},
        "صيانة": {"DP": 8.0, "SE": 56.0, "CP": 10.0}
    },
    "خيول": {
        "راحة/صيانة": {"DP": 9.0, "SE": 58.0, "CP": 11.3},
        "عمل مكثف": {"DP": 13.0, "SE": 65.0, "CP": 16.3},
        "سباق": {"DP": 14.0, "SE": 68.0, "CP": 17.5}
    },
    "إبل": {
        "راحة/صيانة": {"DP": 8.0, "SE": 55.0, "CP": 10.0},
        "إنتاج حليب": {"DP": 12.0, "SE": 60.0, "CP": 15.0},
        "تسمين": {"DP": 11.0, "SE": 62.0, "CP": 13.8}
    },
    "دواجن لاحم": {
        "بادي": {"DP": 22.0, "SE": 76.0, "CP": 27.5},
        "نامي": {"DP": 20.0, "SE": 74.0, "CP": 25.0},
        "ناهي": {"DP": 18.0, "SE": 72.0, "CP": 22.5}
    },
    "أسماك": {
        "نمو": {"DP": 28.0, "SE": 68.0, "CP": 35.0},
        "تسمين نهائي": {"DP": 26.0, "SE": 66.0, "CP": 32.5}
    }
}

# =====================================================================
# مدير المخزون
# =====================================================================
class InventoryManager:
    @staticmethod
    def initialize_inventory():
        if "inventory" not in st.session_state:
            st.session_state["inventory"] = {}
            for ing in FLAT_FEED_DB.keys():
                st.session_state["inventory"][ing] = {"quantity": 25.0, "min_threshold": 5.0, "unit": "طن"}
            for ing in LIQUID_FEED_DB.keys():
                if ing not in st.session_state["inventory"]:
                    st.session_state["inventory"][ing] = {"quantity": 10.0, "min_threshold": 2.0, "unit": "كجم"}
    
    @staticmethod
    def check_stock_levels():
        warnings = {}
        for item, data in st.session_state["inventory"].items():
            qty = data["quantity"]
            threshold = data["min_threshold"]
            if qty <= 0:
                warnings[item] = {"status": "نفد", "level": "critical"}
            elif qty < threshold:
                warnings[item] = {"status": "منخفض", "level": "warning"}
        return warnings

InventoryManager.initialize_inventory()

# =====================================================================
# دوال مساعدة
# =====================================================================
def generate_formula_image(formula_data, target_dp, target_se, breed, stage, user_name):
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_facecolor('#f5f5f5')
    fig.patch.set_facecolor('#ffffff')
    title_text = f"🧬 خلطة علفية معتمدة - تاور نولجي Tawornology العلمية\nالمشرف: {user_name}\nالفصيل: {breed} | المرحلة: {stage}\nDP: {target_dp:.1f}% | SE: {target_se:.1f} وحدة"
    ax.set_title(title_text, fontsize=14, fontweight='bold', pad=25)
    ingredients = list(formula_data.keys())
    kg_per_ton = [p * 10 for p in formula_data.values()]
    y_pos = np.arange(len(ingredients))
    bars = ax.barh(y_pos, kg_per_ton, color='#2e7d32', alpha=0.8, edgecolor='#1b5e20', linewidth=1.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([arabic_processor.fix_arabic_text(i) for i in ingredients], fontsize=11)
    ax.set_xlabel('الكمية (كجم/طن)', fontsize=12, fontweight='bold')
    for i, v in enumerate(kg_per_ton):
        ax.text(v + 3, i, f'{v:.1f} كجم', va='center', fontsize=10, fontweight='bold', color='#1b5e20')
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    cost_text = f"💰 التكلفة: ${st.session_state.get('computed_ton_cost', 0):.2f}/طن"
    ax.text(0.98, 0.02, cost_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='#e8f5e9', alpha=0.9, edgecolor='#2e7d32'))
    ax.text(0.5, -0.08, f'© {datetime.now().year} تاور نولجي Tawornology العلمية\n🕊️ إهداء إلى روح إسماعيل تاور وابتسام',
            transform=ax.transAxes, ha='center', fontsize=9, color='#666666')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    buf.seek(0)
    return buf

def send_image_to_whatsapp(image_buf, caption, phone_number=WHATSAPP_NUMBER):
    try:
        image_base64 = base64.b64encode(image_buf.getvalue()).decode()
        encoded_caption = urllib.parse.quote(caption)
        whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_caption}"
        st.markdown(f"""
        <div style='background:#e8f5e9; padding:20px; border-radius:14px; direction:rtl; text-align:center;'>
            <img src="data:image/png;base64,{image_base64}" style='max-width:100%; border-radius:10px; margin:15px 0; border:3px solid #2e7d32;'>
            <br>
            <a href='{whatsapp_url}' target='_blank'>
                <button style='background:#25D366; color:white; padding:14px 40px; border:none; border-radius:35px; font-size:17px; font-weight:bold; cursor:pointer;'>
                    📲 إرسال الصورة عبر واتساب
                </button>
            </a>
            <p style='margin-top:8px; font-size:13px; color:#666;'>
                📱 الرقم: {phone_number}
            </p>
        </div>
        """, unsafe_allow_html=True)
        return True
    except Exception as e:
        st.error(f"❌ حدث خطأ: {str(e)}")
        return False

# =====================================================================
# حالة الجلسة
# =====================================================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "login_attempts" not in st.session_state: st.session_state["login_attempts"] = 0
if "last_login_time" not in st.session_state: st.session_state["last_login_time"] = None
if "guide_played" not in st.session_state: st.session_state["guide_played"] = {}
if "active_formula" not in st.session_state: st.session_state["active_formula"] = {}
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 0
if "analysis_results" not in st.session_state: st.session_state["analysis_results"] = None
if "lab_sample" not in st.session_state: st.session_state["lab_sample"] = None
if "daily_production_log" not in st.session_state: st.session_state["daily_production_log"] = []
if "broiler_farms" not in st.session_state: st.session_state["broiler_farms"] = {}
if "milk_replacer_formula" not in st.session_state: st.session_state["milk_replacer_formula"] = {}

# =====================================================================
# CSS (نفسه)
# =====================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
* { font-family: 'Cairo', 'Tajawal', sans-serif; }
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 50%, #f5f7fa 100%);
    background-attachment: fixed;
}
.stApp { background: transparent; }
.main-box {
    background: rgba(255,255,255,0.92);
    padding: 35px;
    border-radius: 24px;
    box-shadow: 0 25px 70px rgba(0,0,0,0.15);
    backdrop-filter: blur(15px);
    margin-bottom: 35px;
    border: 1px solid rgba(255,255,255,0.4);
}
.section-title {
    color: #1b5e20;
    border-right: 6px solid #2e7d32;
    padding-right: 18px;
    text-align: right;
    font-size: 1.7rem;
    font-weight: 700;
    margin-top: 30px;
    margin-bottom: 25px;
    background: linear-gradient(to left, rgba(46,125,50,0.12), transparent);
    padding: 14px 22px;
    border-radius: 14px;
}
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
.formula-item:hover { transform: translateX(-8px); box-shadow: 0 8px 30px rgba(0,0,0,0.12); }
.profile-img-style {
    width: 160px; height: 160px; border-radius: 50%; object-fit: cover;
    border: 4px solid #d4af37; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    transition: all 0.5s ease;
}
.profile-img-style:hover { transform: scale(1.05) rotate(3deg); }
.metric-card {
    background: white; padding: 22px; border-radius: 18px;
    box-shadow: 0 6px 30px rgba(0,0,0,0.08); text-align: center;
    transition: all 0.3s ease;
    border: 1px solid rgba(46,125,50,0.1);
}
.metric-card:hover { transform: translateY(-8px); box-shadow: 0 15px 50px rgba(0,0,0,0.15); }
.metric-card .number { font-size: 2.2rem; font-weight: 900; color: #1b5e20; margin: 5px 0; }
.metric-card .label { font-size: 0.95rem; color: #666; font-weight: 600; }
.measurement-card {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 22px; border-radius: 16px;
    border-right: 5px solid #1565C0;
    box-shadow: 0 4px 25px rgba(0,0,0,0.06);
}
.stock-critical { background: linear-gradient(135deg, #ffebee, #ffcdd2); padding: 6px 16px; border-radius: 25px; color: #c62828; font-weight: 700; display: inline-block; }
.stock-normal { background: linear-gradient(135deg, #e8f5e9, #c8e6c9); padding: 6px 16px; border-radius: 25px; color: #2e7d32; font-weight: 700; display: inline-block; }
.stock-warning { background: linear-gradient(135deg, #fff3e0, #ffe0b2); padding: 6px 16px; border-radius: 25px; color: #e65100; font-weight: 700; display: inline-block; }
.manual-book { background: #ffffff; padding: 30px; border-radius: 16px; box-shadow: 0 8px 35px rgba(0,0,0,0.08); }
.book-chapter { background: linear-gradient(135deg, #1a237e, #283593); color: white; padding: 15px 20px; border-radius: 10px; font-weight: bold; margin-top: 20px; }
.book-body { padding: 20px 25px; font-size: 1.05rem; line-height: 1.8; color: #2c3e50; border-left: 4px solid #3498db; background: #f8f9fa; border-radius: 0 10px 10px 0; }
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
</style>
""", unsafe_allow_html=True)

# =====================================================================
# شاشة الدخول (مختصرة)
# =====================================================================
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300

def render_dua_bar():
    st.markdown("""
    <style>
    @keyframes scrollDua {
        0% { transform: translateX(100%); opacity: 0; }
        5% { transform: translateX(0%); opacity: 1; }
        85% { transform: translateX(0%); opacity: 1; }
        95% { transform: translateX(-100%); opacity: 0; }
        100% { transform: translateX(-100%); opacity: 0; }
    }
    @keyframes glowText {
        0% { text-shadow: 0 0 5px #ffd700, 0 0 10px #ffd700, 0 0 20px #ff8c00; }
        25% { text-shadow: 0 0 10px #ffd700, 0 0 20px #ff8c00, 0 0 40px #ff6600; }
        50% { text-shadow: 0 0 15px #ffd700, 0 0 30px #ff8c00, 0 0 60px #ff4500; }
        75% { text-shadow: 0 0 10px #ffd700, 0 0 20px #ff8c00, 0 0 40px #ff6600; }
        100% { text-shadow: 0 0 5px #ffd700, 0 0 10px #ffd700, 0 0 20px #ff8c00; }
    }
    @keyframes pulseHeart {
        0%, 100% { transform: scale(1); color: #ff6b6b; }
        50% { transform: scale(1.5); color: #ff1744; }
    }
    .dua-container {
        background: linear-gradient(135deg, #0d1b2a 0%, #1a237e 40%, #4a148c 70%, #0d1b2a 100%);
        padding: 22px 0;
        border-radius: 24px;
        margin-bottom: 20px;
        overflow: hidden;
        border: 3px solid #ffd700;
        box-shadow: 0 8px 40px rgba(255, 215, 0, 0.5), inset 0 0 30px rgba(255, 215, 0, 0.15);
        direction: rtl;
        position: relative;
    }
    .dua-text {
        display: inline-block;
        white-space: nowrap;
        animation: scrollDua 24s ease-in-out infinite;
        font-size: 1.7rem;
        font-weight: 800;
        color: #ffd700;
        animation: scrollDua 24s ease-in-out infinite, glowText 3.5s ease-in-out infinite;
        padding: 0 25px;
        font-family: 'Cairo', 'Tajawal', sans-serif;
        direction: rtl;
        unicode-bidi: plaintext;
        letter-spacing: 2px;
        animation-fill-mode: forwards;
        text-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
    }
    .dua-text .emoji-heart {
        display: inline-block;
        animation: pulseHeart 1.2s ease-in-out infinite;
        margin: 0 8px;
    }
    .dua-text .gold-star {
        color: #ffd700;
        font-size: 1.6rem;
        margin: 0 12px;
        display: inline-block;
        animation: pulseHeart 1.8s ease-in-out infinite;
    }
    .dua-text .name-highlight {
        color: #ffab40;
        font-weight: 900;
        background: rgba(255, 215, 0, 0.15);
        padding: 0 10px;
        border-radius: 8px;
        border: 1px solid rgba(255, 215, 0, 0.3);
        display: inline-block;
    }
    .dua-reminder {
        text-align: center;
        color: #b39ddb;
        font-size: 1rem;
        padding: 10px 0;
        background: rgba(0,0,0,0.35);
        border-radius: 0 0 20px 20px;
        border-top: 1px solid rgba(255, 215, 0, 0.25);
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .dua-reminder span {
        color: #ffd54f;
        font-weight: 700;
        background: rgba(255, 215, 0, 0.12);
        padding: 4px 16px;
        border-radius: 25px;
        border: 1px solid rgba(255, 215, 0, 0.2);
    }
    </style>
    <div class="dua-container">
        <div class="dua-text">
            <span class="gold-star">✦</span>
            <span class="emoji-heart">❤️</span>
            اللهم اغفر لـ <span class="name-highlight">إسماعيل تاور</span> و <span class="name-highlight">ابتسام</span> وارحمهما وأدخلهما فسيح جناتك
            <span class="emoji-heart">❤️</span>
            اللهم اجعل قبرهما روضة من رياض الجنة واجمعنا بهما في الفردوس الأعلى
            <span class="emoji-heart">❤️</span>
            اللهم ارحم موتانا وموتى المسلمين
            <span class="emoji-heart">❤️</span>
            <span class="gold-star">✦</span>
        </div>
    </div>
    <div class="dua-reminder">
        <span>🕊️ تذكير:</span> ادعُ لهما بالرحمة والمغفرة، فاللهم ارحمهما كما ربياني صغيراً وأحسن إليهما كما أحسنا إلينا 🕊️
    </div>
    """, unsafe_allow_html=True)

if not st.session_state["approved"]:
    render_dua_bar()
    
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        if st.session_state["last_login_time"]:
            time_diff = (datetime.now() - st.session_state["last_login_time"]).seconds
            if time_diff < LOCKOUT_TIME:
                st.markdown('<div class="main-box" style="max-width:500px; margin:100px auto; direction:rtl; text-align:center;">', unsafe_allow_html=True)
                st.error(f"🔒 تم قفل النظام مؤقتاً. يرجى المحاولة بعد {LOCKOUT_TIME - time_diff} ثانية")
                st.markdown('</div>', unsafe_allow_html=True)
                st.stop()
            else:
                st.session_state["login_attempts"] = 0

    st.markdown('<div class="main-box" style="max-width:550px; margin:80px auto; direction:rtl;">', unsafe_allow_html=True)
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" style="width:100px; height:100px; border-radius:50%; border:3px solid #d4af37; display:block; margin:0 auto;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1a237e; text-align:center;'>🌾 تاور نولجي Tawornology العلمية</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555; font-size:1.1rem;'>للانتاج الحيواني وتركيب الاعلاف</p>")
    st.markdown("<p style='text-align:center; color:#888; font-size:0.9rem;'>الإصدار المتكامل 13.0 - مع بديل الحليب السائل</p>", unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("🔊 استمع للترحيب", use_container_width=True):
            play_welcome_audio()
    with col_s2:
        if st.button("🕊️ استمع للدعاء", use_container_width=True):
            play_dua_audio()

    col_public, col_space = st.columns([1, 1])
    with col_public:
        if st.button("👤 دخول كزائر (مجاني)", type="primary", use_container_width=True):
            auth = AuthManager()
            user = auth.login_public()
            if user:
                st.session_state["approved"] = True
                st.session_state["user_role"] = "public"
                st.session_state["login_welcome_shown"] = False
                st.session_state["login_attempts"] = 0
                st.session_state["last_login_time"] = datetime.now()
                st.session_state["session_token"] = secrets.token_urlsafe(32)
                st.session_state["user"] = user
                voice_guide("السلام عليكم، مرحباً بك زائراً في تاور نولجي Tawornology العلمية.")
                st.rerun()
            else:
                st.error("❌ حدث خطأ في الدخول كزائر")

    st.markdown("<hr style='margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#666;'>🔑 للمالك والمختصين - تسجيل الدخول بالكود</p>", unsafe_allow_html=True)
    
    login_option = st.radio("طريقة الدخول:", ["كود الدخول السري", "اسم المستخدم وكلمة المرور"], horizontal=True)
    
    if login_option == "كود الدخول السري":
        input_code = st.text_input("🔑 أدخل كود الدخول:", type="password", placeholder="أدخل الكود الخاص")
        col_login, col_reset = st.columns(2)
        with col_login:
            if st.button("تسجيل الدخول 🔓", type="secondary", use_container_width=True):
                if input_code.strip() in CODES_DB:
                    st.session_state["approved"] = True
                    st.session_state["user_role"] = CODES_DB[input_code.strip()]["role"]
                    st.session_state["login_welcome_shown"] = False
                    st.session_state["login_attempts"] = 0
                    st.session_state["last_login_time"] = datetime.now()
                    st.session_state["session_token"] = secrets.token_urlsafe(32)
                    voice_guide(f"مرحباً بك في تاور نولجي Tawornology العلمية، {CODES_DB[input_code.strip()]['name']}.")
                    st.rerun()
                else:
                    st.session_state["login_attempts"] += 1
                    remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                    st.error(f"❌ الكود غير صحيح! متبقي {remaining} محاولات")
                    voice_guide(f"الكود غير صحيح. متبقي {remaining} محاولات.")
        with col_reset:
            if st.button("🔄 نسيت الكود", use_container_width=True):
                st.info("يرجى التواصل مع مدير النظام: abukram128@gmail.com")
                voice_guide("يرجى التواصل مع مدير النظام عبر البريد الإلكتروني.")
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
                voice_guide(f"مرحباً بك، {user['full_name']}.")
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ اسم المستخدم أو كلمة المرور غير صحيحة! متبقي {remaining} محاولات")
        st.caption("💡 المستخدم الافتراضي: admin / admin123")

    st.markdown("""
    <div style='text-align:center; margin-top:15px; color:#999; font-size:0.85rem;'>
    <p>🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b> - رحمهما الله وغفر لهما</p>
    <p style='font-size:0.8rem; color:#b39ddb;'>اللهم اجعل قبرهما روضة من رياض الجنة</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# الترحيب بعد الدخول
# =====================================================================
if not st.session_state["login_welcome_shown"]:
    role_messages = {
        "owner": "👑 مرحباً بك في تاور نولجي Tawornology العلمية، الاختصاصي م. عبد القادر إسماعيل تاور",
        "specialist": "🔬 أهلاً بالزملاء المختصين.",
        "veterinarian": "💊 أهلاً بالطبيب البيطري.",
        "nutritionist": "🧬 أهلاً بأخصائي التغذية.",
        "breeder": "🌾 أهلاً وسهلاً بإخواننا المربين.",
        "public": "👤 مرحباً بك زائراً."
    }
    st.toast(role_messages.get(st.session_state["user_role"], "مرحباً"), icon="🌾")
    voice_welcome(st.session_state["user_role"])
    st.session_state["login_welcome_shown"] = True

render_dua_bar()

# =====================================================================
# الواجهة الرئيسية
# =====================================================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logout_space, col_user_status = st.columns([0.7, 0.3])
with col_user_status:
    role_names = {"owner": "المالك 👑", "specialist": "المختص 👨‍🔬", "veterinarian": "الطبيب البيطري 💊", "nutritionist": "أخصائي التغذية 🧬", "breeder": "المربي 🌾", "public": "زائر 👤"}
    user_name = st.session_state.get("user", {}).get("full_name", "زائر")
    user_role = st.session_state.get("user_role", "public")
    st.markdown(f"""
    <div style='text-align:left; background:linear-gradient(135deg,#f5f5f5,#e0e0e0); padding:14px; border-radius:14px;'>
        <div style='font-weight:700; font-size:1rem;'>{user_name}</div>
        <div style='font-size:0.85rem; color:#555;'>{role_names.get(user_role, "مستخدم")}</div>
        <small style='color:#888;'>آخر دخول: {datetime.now().strftime('%Y-%m-%d %H:%M')}</small>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["inventory", "broiler_farms", "whatsapp_alerts_sent", "analysis_results", "basmala_played", "welcome_played", "email_password", "guide_played", "farms", "selected_farm_id", "selected_cycle_id", "active_formula", "active_cp_tag", "active_se_tag", "active_breed_tag", "computed_ton_cost", "lab_sample", "milk_replacer_formula"]:
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        voice_guide("تم تسجيل الخروج. السلام عليكم.")
        st.rerun()

col_logo, col_title = st.columns([0.2, 0.8])
with col_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='color:#1a237e; text-align:right; margin-bottom:0; font-size:2.2rem;'>🌾 تاور نولجي Tawornology العلمية</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#1565C0; text-align:right; font-size:1.2rem;'>للانتاج الحيواني وتركيب الاعلاف - محرك الاستمثال الخطي المتقدم</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#c62828; text-align:right; font-weight:700;'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top:3px solid #2e7d32;'>", unsafe_allow_html=True)

# =====================================================================
# إحصائيات سريعة
# =====================================================================
st.markdown("### 📊 لوحة التحكم السريعة")
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
with col_stat1:
    stock_summary = InventoryManager.get_stock_summary()
    st.markdown(f"<div class='metric-card'><div class='icon'>🏭</div><div class='number'>{stock_summary['total_items']}</div><div class='label'>إجمالي المواد</div></div>", unsafe_allow_html=True)
with col_stat2:
    st.markdown(f"<div class='metric-card'><div class='icon'>⚖️</div><div class='number'>{stock_summary['total_quantity']:.1f}</div><div class='label'>إجمالي المخزون (طن)</div></div>", unsafe_allow_html=True)
with col_stat3:
    low_stock = stock_summary['low_stock']
    color = "#c62828" if low_stock > 5 else "#e65100" if low_stock > 0 else "#2e7d32"
    st.markdown(f"<div class='metric-card'><div class='icon'>⚠️</div><div class='number' style='color:{color};'>{low_stock}</div><div class='label'>مواد منخفضة</div></div>", unsafe_allow_html=True)
with col_stat4:
    st.markdown(f"<div class='metric-card'><div class='icon'>🐔</div><div class='number'>{len(st.session_state.get('broiler_farms', {}))}</div><div class='label'>مزارع نشطة</div></div>", unsafe_allow_html=True)
st.markdown("---")

# =====================================================================
# أدوات المشاركة
# =====================================================================
col_voice, col_share1, col_share2 = st.columns([0.3, 0.35, 0.35])
with col_voice:
    if st.button("🔊 اختبار الصوت", use_container_width=True):
        voice_guide("بسم الله الرحمن الرحيم. مرحباً، هذا اختبار للنظام الصوتي.")
        st.success("✅ تم تشغيل الصوت")
with col_share1:
    if st.button("📧 إرسال الكود إلى البريد", use_container_width=True):
        if st.session_state["user_role"] == "owner":
            email = st.text_input("البريد:", placeholder=OWNER_EMAIL, key="code_email")
            if email and '@' in email:
                if email.strip().lower() == OWNER_EMAIL.strip().lower():
                    with st.spinner("جاري إرسال الكود..."):
                        success, msg = send_code_to_email(email)
                        st.success(msg) if success else st.error(msg)
                else:
                    st.error(f"❌ عذراً، إرسال الكود مسموح فقط للبريد: {OWNER_EMAIL}")
        else:
            st.warning("⚠️ هذه الخاصية متاحة فقط للمالك.")
with col_share2:
    if st.button("📊 مشاركة الخلطة كصورة", use_container_width=True):
        if st.session_state["active_formula"]:
            user_name = st.session_state.get("user", {}).get("full_name", "مستخدم")
            img_buf = generate_formula_image(st.session_state["active_formula"], st.session_state["active_cp_tag"], st.session_state["active_se_tag"], st.session_state["active_breed_tag"], st.session_state["active_stage_title"], user_name)
            caption = f"🧬 خلطة علفية معتمدة - تاور نولجي Tawornology العلمية\nالمشرف: {user_name}"
            send_image_to_whatsapp(img_buf, caption)

st.markdown("---")

# =====================================================================
# تحديد التبويبات
# =====================================================================
tabs_titles = [
    "🐾 القطاع الحيواني",
    "🍼 بديل الحليب السائل",
    "🐔 إدارة المزارع",
    "📊 بورصة الأسعار",
    "🏭 المستودعات",
    "📈 الإنتاج اليومي",
    "🔔 التنبيهات",
    "📚 المراجع العلمية",
    "💡 المساعدة",
    "📖 الدليل"
]

if st.session_state["user_role"] == "owner":
    tabs_titles.append("📧 إرسال الكود")

tabs = st.tabs(tabs_titles)

# =====================================================================
# دالة guide_section
# =====================================================================
def guide_section(tab_name, guide_text):
    with st.expander(f"📘 دليل استخدام {tab_name}", expanded=False):
        st.markdown(f"<div style='background:#f0f8ff; padding:15px; border-radius:10px; direction:rtl;'>{guide_text}</div>", unsafe_allow_html=True)
        if st.button(f"🔊 استمع للدليل ({tab_name})"):
            voice_guide(guide_text)

# =====================================================================
# دالة تركيب العلف الجاف (مع مقارنات قياسية)
# =====================================================================
def render_feed_formulation(animal_key, display_name, icon, default_breeds, default_stages, default_dp, default_se, has_measurements=True):
    st.markdown(f'<div class="section-title">{icon} {display_name} - تركيب العلف المتقدم</div>', unsafe_allow_html=True)
    
    col_measure, col_settings = st.columns([0.4, 0.6])
    with col_measure:
        if has_measurements:
            st.markdown('<div class="measurement-card">', unsafe_allow_html=True)
            st.markdown("#### 📏 شريط القياس الحيوي")
            col_h, col_l, col_age = st.columns(3)
            with col_h:
                h_girth = st.number_input("محيط الصدر (سم)", min_value=20.0, max_value=300.0, value=150.0, step=1.0, key=f"{animal_key}_girth")
            with col_l:
                b_length = st.number_input("طول الجسم (سم)", min_value=20.0, max_value=300.0, value=130.0, step=1.0, key=f"{animal_key}_length")
            with col_age:
                age_months = st.number_input("العمر (شهر)", min_value=1, max_value=120, value=12, step=1, key=f"{animal_key}_age")
            weight_factors = {"cattle": 10838, "sheep": 15500, "goat": 15000, "horse": 11877, "camel": 13000}
            feed_factors = {"cattle": 0.025, "sheep": 0.035, "goat": 0.032, "horse": 0.022, "camel": 0.020}
            wf = weight_factors.get(animal_key, 12000)
            ff = feed_factors.get(animal_key, 0.03)
            estimated_weight = (h_girth ** 2 * b_length) / wf
            daily_dry_matter = estimated_weight * ff
            st.success(f"**الوزن التقديري:** {estimated_weight:.1f} كجم")
            st.info(f"**الاحتياج اليومي من المادة الجافة:** {daily_dry_matter:.2f} كجم")
            if estimated_weight > 0:
                age_factor = 1 + (age_months - 12) * 0.01
                adjusted_dp = default_dp * (1 + (estimated_weight - 500) / 2000) * age_factor
                adjusted_se = default_se * (1 + (estimated_weight - 500) / 3000) * age_factor
            else:
                adjusted_dp = default_dp
                adjusted_se = default_se
            st.caption(f"⚖️ البروتين المهضوم المقترح: {adjusted_dp:.1f}% | معادل النشاء: {adjusted_se:.1f}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("💡 لا تتوفر قياسات جسدية للطيور والأسماك.")
    
    with col_settings:
        st.markdown("#### 🎯 اختيار السلالة والمرحلة")
        col_b, col_s = st.columns(2)
        with col_b:
            breed = st.selectbox("السلالة:", default_breeds, key=f"{animal_key}_breed")
        with col_s:
            stage = st.selectbox("مرحلة الإنتاج:", default_stages, key=f"{animal_key}_stage")
        
        st.markdown("#### 🧬 العمر والحالة الفسيولوجية")
        col_age_phys = st.columns(2)
        with col_age_phys[0]:
            age_input = st.number_input("العمر (شهر)", min_value=1, max_value=240, value=24, step=1, key=f"{animal_key}_age_input")
        with col_age_phys[1]:
            physiological_state = st.selectbox(
                "الحالة الفسيولوجية",
                ["طبيعي", "حامل", "مرضع", "صائم", "نشاط مكثف", "استشفاء", "نمو سريع"],
                key=f"{animal_key}_physiological"
            )
        
        st.markdown("#### 🧬 خيارات البروتين والطاقة")
        protein_basis = st.radio("أساس البروتين:", ["DP", "CP"], horizontal=True, key=f"{animal_key}_basis")
        if protein_basis == "DP":
            target_protein = st.number_input("نسبة DP المطلوبة (%)", min_value=5.0, max_value=50.0, value=float(adjusted_dp if has_measurements else default_dp), step=0.5, key=f"{animal_key}_dp")
            cp_est = target_protein / 0.80
            st.caption(f"💡 يقابل ذلك بروتين خام ≈ {cp_est:.1f}%")
        else:
            target_protein = st.number_input("نسبة CP المطلوبة (%)", min_value=5.0, max_value=60.0, value=float(default_dp/0.80), step=0.5, key=f"{animal_key}_cp")
            dp_est = target_protein * 0.80
            st.caption(f"💡 يقابل ذلك بروتين مهضوم ≈ {dp_est:.1f}%")
        target_se = st.number_input("معادل النشاء (SE) المطلوب (وحدة)", min_value=10.0, max_value=90.0, value=float(adjusted_se if has_measurements else default_se), step=1.0, key=f"{animal_key}_se")
        if protein_basis == "DP":
            actual_dp_target = target_protein
        else:
            actual_dp_target = target_protein * 0.80
        
        state_multipliers = {
            "طبيعي": 1.0,
            "حامل": 1.15,
            "مرضع": 1.30,
            "صائم": 0.85,
            "نشاط مكثف": 1.25,
            "استشفاء": 1.20,
            "نمو سريع": 1.35
        }
        multiplier = state_multipliers.get(physiological_state, 1.0)
        actual_dp_target *= multiplier
        target_se *= multiplier
        st.caption(f"📌 تم تعديل الاحتياجات: {physiological_state} (معامل {multiplier:.2f})")
    
    st.markdown("#### 🌾 اختر المكونات العلفية")
    selected_ingredients = []
    ingredient_prices = {}
    default_ingredients = {
        "cattle": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%", "أمباز الفول السوداني (كسب)", "مركزات خيول ومجترات", "ملح الطعام", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)", "بيكربونات الصوديوم (الصودا)"],
        "sheep": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%", "أمباز الفول السوداني (كسب)", "مركزات خيول ومجترات", "ملح الطعام", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)", "بيكربونات الصوديوم (الصودا)"],
        "goat": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%", "أمباز الفول السوداني (كسب)", "مركزات خيول ومجترات", "ملح الطعام", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)", "بيكربونات الصوديوم (الصودا)"],
        "horse": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)", "كسب فول صويا 44%", "أمباز الفول السوداني (كسب)", "مولاس قصب السكر", "مركزات خيول ومجترات", "ملح الطعام", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)"],
        "camel": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)", "كسب فول صويا 44%", "أمباز الفول السوداني (كسب)", "البرسيم الجاف (الدريس)", "مركزات خيول ومجترات", "ملح الطعام", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)"],
        "poultry": ["ذرة صفراء", "سورجم (فتريتة)", "كسب فول صويا 44%", "كسب جلوتين الذرة 60%", "مركزات دواجن وسمان", "بريمكس تسمين دواجن (Premix)", "ملح الطعام", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)", "إنزيم الفايتيز الزامي"],
        "fish": ["ذرة صفراء", "كسب فول صويا 44%", "مسحوق أسماك (Fishmeal 60%)", "كسب جلوتين الذرة 60%", "مركزات دواجن وسمان", "ملح الطعام", "فوسفات ثنائي الكالسيوم (DCP)", "إنزيم الفايتيز الزامي"]
    }
    default_list = default_ingredients.get(animal_key, [])
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=False):
            cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with cols[idx % 3]:
                    checked = st.checkbox(ing_name, value=ing_name in default_list, key=f"{animal_key}_feed_{ing_name}")
                    if checked:
                        price = st.number_input(f"سعر {ing_name} ($/طن)", min_value=5.0, value=float(250.0 if "نخالة" in ing_name or "ملح" in ing_name else 350.0), key=f"{animal_key}_price_{ing_name}")
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price
    
    col_buttons = st.columns(3)
    with col_buttons[0]:
        if st.button(f"🚀 تشغيل محرك التركيب ({display_name})", type="primary", use_container_width=True, key=f"{animal_key}_run"):
            if len(selected_ingredients) < 3:
                st.warning("⚠️ يرجى اختيار 3 مكونات على الأقل.")
                voice_guide(f"يرجى اختيار 3 مكونات علفية على الأقل لـ {display_name}.")
            else:
                voice_guide(f"جاري تشغيل محرك تركيب العلف لـ {display_name}.")
                st.info("🔄 جاري حساب الخلطة المثالية...")
                c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
                bounds = [(0.0, 100.0) for _ in selected_ingredients]
                A_eq = [[1.0 for _ in selected_ingredients]]
                b_eq = [100.0]
                cp_row = []; se_row = []; ndf_row = []; adf_row = []
                for ing in selected_ingredients:
                    feed_data = FLAT_FEED_DB.get(ing, {})
                    cp_val = feed_data.get("CP", 0.0)
                    dc_val = feed_data.get("DC", 0.0)
                    se_val = feed_data.get("SE", 0.0)
                    ndf_val = feed_data.get("NDF", 0.0)
                    adf_val = feed_data.get("ADF", 0.0)
                    cp_row.append(cp_val * dc_val)
                    se_row.append(se_val)
                    ndf_row.append(ndf_val)
                    adf_row.append(adf_val)
                A_eq.append(cp_row)
                b_eq.append(actual_dp_target * 100.0)
                A_ub = []; b_ub = []
                A_ub.append([-1.0 * x for x in se_row])
                b_ub.append(-1.0 * target_se * 100.0)
                if animal_key in ["cattle", "sheep", "goat", "camel"]:
                    A_ub.append(ndf_row); b_ub.append(35.0 * 100.0)
                    A_ub.append(adf_row); b_ub.append(20.0 * 100.0)
                elif animal_key == "horse":
                    A_ub.append(ndf_row); b_ub.append(40.0 * 100.0)
                if "نخالة قمح (ردة)" in selected_ingredients:
                    idx = selected_ingredients.index("نخالة قمح (ردة)")
                    row = [0.0] * len(selected_ingredients); row[idx] = 1.0
                    A_ub.append(row); b_ub.append(25.0 if animal_key in ["cattle","sheep","goat","camel"] else 15.0)
                if "مولاس قصب السكر" in selected_ingredients and animal_key == "horse":
                    idx = selected_ingredients.index("مولاس قصب السكر")
                    row = [0.0] * len(selected_ingredients); row[idx] = 1.0
                    A_ub.append(row); b_ub.append(8.0)
                fixed_additives = {}
                if animal_key in ["cattle","sheep","goat","camel"]:
                    if "بيكربونات الصوديوم (الصودا)" not in selected_ingredients:
                        selected_ingredients.append("بيكربونات الصوديوم (الصودا)")
                        ingredient_prices["بيكربونات الصوديوم (الصودا)"] = 340.0
                        fixed_additives["بيكربونات الصوديوم (الصودا)"] = 0.75 if animal_key in ["cattle","camel"] else 0.5
                        bounds.append((fixed_additives["بيكربونات الصوديوم (الصودا)"], fixed_additives["بيكربونات الصوديوم (الصودا)"]))
                    else:
                        idx = selected_ingredients.index("بيكربونات الصوديوم (الصودا)")
                        bounds[idx] = (0.5, 0.5)
                if animal_key in ["poultry", "fish"]:
                    if "إنزيم الفايتيز الزامي" not in selected_ingredients:
                        selected_ingredients.append("إنزيم الفايتيز الزامي")
                        ingredient_prices["إنزيم الفايتيز الزامي"] = 1200.0
                        fixed_additives["إنزيم الفايتيز الزامي"] = 0.05
                        bounds.append((0.05, 0.05))
                    else:
                        idx = selected_ingredients.index("إنزيم الفايتيز الزامي")
                        bounds[idx] = (0.05, 0.05)
                try:
                    res = linprog(c_vector, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
                    if res.success:
                        formula_results = {}
                        computed_se_total = 0.0
                        for idx, ing in enumerate(selected_ingredients):
                            if res.x[idx] > 0.0001:
                                formula_results[ing] = res.x[idx]
                                feed_data = FLAT_FEED_DB.get(ing, {})
                                computed_se_total += (res.x[idx] / 100.0) * feed_data.get("SE", 0.0)
                        ton_cost = res.fun / 100.0
                        st.success(f"✅ تم توليد الخلطة العلفية لـ {display_name} بنجاح! التكلفة: ${ton_cost:.2f}/طن")
                        voice_guide(f"تم توليد الخلطة العلفية لـ {display_name} بنجاح بتكلفة {ton_cost:.2f} دولار للطن.")
                        col_res1, col_res2 = st.columns([0.6, 0.4])
                        with col_res1:
                            st.write("#### 📝 المقادير المعتمدة لتركيب طن واحد:")
                            for k, v in formula_results.items():
                                st.markdown(f'<div class="formula-item"><span class="name">{k}</span><span class="value">{v:.2f}% ({v*10:.1f} كجم)</span></div>', unsafe_allow_html=True)
                            st.metric("💰 التكلفة الفعلية للطن", f"${ton_cost:.2f}")
                            st.metric("🧬 البروتين المحقق", f"{actual_dp_target:.2f}% ({protein_basis})")
                            st.metric("🌽 معادل النشاء المحقق", f"{computed_se_total:.2f} وحدة")
                            
                            # المعايير القياسية للخلطة
                            standard = STANDARD_VALUES.get(display_name, {}).get(stage, {})
                            if standard:
                                st.write("#### 📊 مقارنة مع المعايير القياسية:")
                                std_data = [['المقياس', 'المحسوب', 'القياسي', 'الانحراف %', 'التقييم']]
                                dp_dev = ((actual_dp_target - standard.get('DP', actual_dp_target)) / standard.get('DP', 1)) * 100 if standard.get('DP', 0) > 0 else 0
                                se_dev = ((computed_se_total - standard.get('SE', computed_se_total)) / standard.get('SE', 1)) * 100 if standard.get('SE', 0) > 0 else 0
                                cp_calc = actual_dp_target / 0.80
                                cp_dev = ((cp_calc - standard.get('CP', cp_calc)) / standard.get('CP', 1)) * 100 if standard.get('CP', 0) > 0 else 0
                                
                                dp_grade = "✅" if abs(dp_dev) <= 5 else ("⚠️" if abs(dp_dev) <= 10 else "❌")
                                se_grade = "✅" if abs(se_dev) <= 5 else ("⚠️" if abs(se_dev) <= 10 else "❌")
                                cp_grade = "✅" if abs(cp_dev) <= 5 else ("⚠️" if abs(cp_dev) <= 10 else "❌")
                                
                                std_data.append(['DP', f"{actual_dp_target:.2f}%", f"{standard.get('DP', 0):.2f}%", f"{dp_dev:.1f}", dp_grade])
                                std_data.append(['SE', f"{computed_se_total:.2f}", f"{standard.get('SE', 0):.2f}", f"{se_dev:.1f}", se_grade])
                                std_data.append(['CP', f"{cp_calc:.2f}%", f"{standard.get('CP', 0):.2f}%", f"{cp_dev:.1f}", cp_grade])
                                st.table(pd.DataFrame(std_data[1:], columns=std_data[0]))
                                
                                avg_dev = (abs(dp_dev) + abs(se_dev) + abs(cp_dev)) / 3
                                if avg_dev <= 5:
                                    st.success("⭐ التقييم العام: ممتاز - الخلطة متوافقة مع المعايير")
                                elif avg_dev <= 10:
                                    st.warning("⭐ التقييم العام: جيد - الخلطة قريبة من المعايير")
                                else:
                                    st.error("⭐ التقييم العام: يحتاج تحسين - يوصى بمراجعة النسب")
                            
                            # أزرار إضافية
                            col_actions = st.columns(3)
                            with col_actions[0]:
                                if st.button("🔬 إرسال إلى المختبر", use_container_width=True):
                                    st.session_state["lab_sample"] = {
                                        'formula': formula_results,
                                        'animal': display_name,
                                        'breed': breed,
                                        'stage': stage,
                                        'age': age_input,
                                        'physiological': physiological_state,
                                        'dp': actual_dp_target,
                                        'se': computed_se_total,
                                        'cp': actual_dp_target / 0.80
                                    }
                                    st.success("✅ تم إرسال العينة إلى المختبر.")
                                    voice_guide("تم إرسال العينة إلى المختبر.")
                            with col_actions[1]:
                                try:
                                    standard = STANDARD_VALUES.get(display_name, {}).get(stage, {})
                                    pdf_data = pdf_generator.generate_comprehensive_report(
                                        formula_results, actual_dp_target, f"{breed} - {stage} ({physiological_state})", 
                                        ton_cost, "المدينة", ton_cost*600, "SDG", computed_se_total, 
                                        user_name=st.session_state.get("user", {}).get("full_name", "مستخدم"),
                                        standard=standard,
                                        include_charts=True, 
                                        extra_info={"السلالة": breed, "المرحلة": stage, "الحالة": physiological_state, "العمر": f"{age_input} شهر"}
                                    )
                                    st.download_button("📥 تحميل PDF", pdf_data, file_name=f"Tawornology_{display_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf", use_container_width=True)
                                except Exception as e:
                                    st.warning(f"⚠️ تعذر إنشاء PDF: {e}")
                            with col_actions[2]:
                                if st.button("🔊 استمع للنتيجة", use_container_width=True):
                                    voice_guide(f"تم توليد الخلطة بتكلفة {ton_cost:.2f} دولار للطن، البروتين المهضوم {actual_dp_target:.2f} بالمئة، ومعادل النشاء {computed_se_total:.2f} وحدة.")
                        with col_res2:
                            if len(formula_results) > 1:
                                fig = px.pie(values=list(formula_results.values()), names=list(formula_results.keys()), title="توزيع مكونات الخلطة", color_discrete_sequence=px.colors.sequential.Greens)
                                fig.update_layout(height=400)
                                st.plotly_chart(fig, use_container_width=True)
                        st.session_state["active_formula"] = formula_results
                        st.session_state["active_cp_tag"] = actual_dp_target
                        st.session_state["active_se_tag"] = computed_se_total
                        st.session_state["active_breed_tag"] = f"{breed} - {stage} ({physiological_state})"
                        st.session_state["computed_ton_cost"] = ton_cost
                    else:
                        st.error("❌ تعذر إيجاد حل رياضي متزن. يرجى إضافة المزيد من المكونات أو تعديل النسب.")
                        voice_guide(f"تعذر إيجاد حل رياضي متزن لـ {display_name}.")
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء التشغيل: {e}")
                    voice_guide(f"حدث خطأ أثناء تشغيل المحرك لـ {display_name}.")
    
    with col_buttons[1]:
        if st.button(f"📋 عرض المعايير القياسية ({display_name})", use_container_width=True):
            standard = STANDARD_VALUES.get(display_name, {}).get(stage, {})
            if standard:
                st.info(f"📊 المعايير القياسية لـ {display_name} - {stage}: DP={standard.get('DP','-')}%, SE={standard.get('SE','-')} وحدة, CP={standard.get('CP','-')}%")
            else:
                st.warning("⚠️ لا توجد معايير قياسية لهذه المرحلة.")
    
    with col_buttons[2]:
        if st.button(f"🔊 استماع للتعليمات ({display_name})", use_container_width=True):
            voice_guide(f"مرحباً بك في قسم {display_name}. اختر السلالة والمرحلة، والعمر والحالة الفسيولوجية، ثم اختر المكونات، واضغط على زر التشغيل.")

# =====================================================================
# دالة تركيب بديل الحليب السائل (جديد)
# =====================================================================
def render_milk_replacer_formulation():
    st.markdown('<div class="section-title">🍼 تركيب بديل الحليب السائل للرضاعة</div>', unsafe_allow_html=True)
    
    st.info("""
    📘 **نظام تركيب بديل الحليب السائل:**
    يستخدم هذا القسم لتركيب خلطات سائلة بديلة للحليب الطبيعي،
    مخصصة لتغذية الصغار (عجول، حملان، جديان، مهرات، صغار الإبل).
    يمكنك اختيار المكونات السائلة والمسحوقية، وتحديد الاحتياجات الغذائية.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        animal_type = st.selectbox("نوع الحيوان:", ["عجول (أبقار)", "حملان (أغنام)", "جديان (ماعز)", "مهرات (خيول)", "صغار إبل"])
        age_days = st.number_input("العمر (يوم)", min_value=1, max_value=120, value=7, step=1)
        target_protein = st.number_input("البروتين المستهدف (%)", min_value=10.0, max_value=30.0, value=20.0, step=0.5)
    with col2:
        target_fat = st.number_input("الدهون المستهدفة (%)", min_value=5.0, max_value=30.0, value=15.0, step=0.5)
        total_liters = st.number_input("إجمالي حجم الخلطة (لتر)", min_value=10.0, max_value=1000.0, value=100.0, step=10.0)
    
    st.markdown("#### 🧪 اختر مكونات بديل الحليب")
    selected_ingredients = []
    ingredient_prices = {}
    
    for ing_name, data in LIQUID_FEED_DB.items():
        cols = st.columns([0.6, 0.2, 0.2])
        with cols[0]:
            checked = st.checkbox(ing_name, key=f"milk_{ing_name}")
        with cols[1]:
            qty = st.number_input(f"كمية {ing_name[:10]}", min_value=0.0, value=0.0, step=0.5, key=f"milk_qty_{ing_name}", label_visibility="collapsed") if checked else 0.0
        with cols[2]:
            price = st.number_input(f"سعر {ing_name[:10]}", min_value=0.0, value=float(data.get("Price", 2.0)), step=0.1, key=f"milk_price_{ing_name}", label_visibility="collapsed") if checked else 0.0
        if checked and qty > 0:
            selected_ingredients.append(ing_name)
            ingredient_prices[ing_name] = price * qty / 100.0  # تكلفة لكل لتر
    
    if st.button("🍼 تشغيل محرك تركيب بديل الحليب", type="primary", use_container_width=True):
        if len(selected_ingredients) < 2:
            st.warning("⚠️ يرجى اختيار 2 مكونات على الأقل.")
            voice_guide("يرجى اختيار مكونين على الأقل لبديل الحليب.")
        else:
            voice_guide(f"جاري تركيب بديل الحليب لـ {animal_type} بعمر {age_days} يوم.")
            st.info("🔄 جاري حساب الخلطة السائلة...")
            
            # حساب كميات المكونات
            total_quantity = sum(qty for ing, qty in zip(selected_ingredients, [st.session_state.get(f"milk_qty_{ing}", 0) for ing in selected_ingredients]))
            if total_quantity <= 0:
                st.warning("⚠️ يرجى إدخال كميات أكبر من الصفر.")
                voice_guide("يرجى إدخال كميات أكبر من الصفر.")
                return
            
            # حساب القيم الغذائية
            total_protein = 0.0
            total_fat = 0.0
            formula_results = {}
            
            for ing in selected_ingredients:
                qty = st.session_state.get(f"milk_qty_{ing}", 0)
                if qty > 0:
                    pct = qty / total_quantity
                    data = LIQUID_FEED_DB.get(ing, {})
                    protein = data.get("CP", 0.0) * pct
                    fat = data.get("Fat", 0.0) * pct
                    total_protein += protein
                    total_fat += fat
                    formula_results[ing] = qty
            
            # حساب التكلفة
            total_cost = sum(ingredient_prices.get(ing, 0) * (st.session_state.get(f"milk_qty_{ing}", 0) / total_quantity) for ing in selected_ingredients)
            cost_per_liter = total_cost / total_liters
            
            st.success(f"✅ تم توليد بديل الحليب لـ {animal_type} بنجاح!")
            voice_guide(f"تم توليد بديل الحليب لـ {animal_type} بتكلفة {cost_per_liter:.2f} دولار لكل لتر.")
            
            col_res1, col_res2 = st.columns([0.6, 0.4])
            with col_res1:
                st.write("#### 📝 مكونات بديل الحليب لكل 100 لتر:")
                for ing, qty in formula_results.items():
                    pct = (qty / total_quantity) * 100
                    st.markdown(f'<div class="formula-item"><span class="name">{ing}</span><span class="value">{qty:.2f} كجم ({pct:.1f}%)</span></div>', unsafe_allow_html=True)
                st.metric("💰 التكلفة لكل لتر", f"${cost_per_liter:.2f}")
                st.metric("🧬 البروتين المحقق", f"{total_protein:.2f}%")
                st.metric("🧈 الدهون المحققة", f"{total_fat:.2f}%")
            
            with col_res2:
                if len(formula_results) > 1:
                    fig = px.pie(values=list(formula_results.values()), names=list(formula_results.keys()), title="توزيع مكونات بديل الحليب", color_discrete_sequence=px.colors.sequential.Blues)
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            # حفظ النتيجة
            st.session_state["milk_replacer_formula"] = {
                'formula': formula_results,
                'animal': animal_type,
                'age': age_days,
                'protein': total_protein,
                'fat': total_fat,
                'cost_per_liter': cost_per_liter,
                'total_protein': target_protein,
                'total_fat': target_fat
            }
            
            # تحميل PDF
            try:
                pdf_data = pdf_generator.generate_milk_replacer_report(
                    formula_results, animal_type, age_days, total_protein, total_fat, cost_per_liter,
                    user_name=st.session_state.get("user", {}).get("full_name", "مستخدم")
                )
                st.download_button("📥 تحميل تقرير بديل الحليب PDF", pdf_data, file_name=f"Milk_Replacer_{animal_type}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf")
            except Exception as e:
                st.warning(f"⚠️ تعذر إنشاء PDF: {e}")

# =====================================================================
# التبويب 0: القطاع الحيواني
# =====================================================================
with tabs[0]:
    guide_section("القطاع الحيواني", "هنا يمكنك تركيب أعلاف لجميع أنواع الحيوانات مع مقارنات قياسية.")
    animal_tabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐴 خيول", "🐫 إبل", "🐔 دواجن", "🐟 أسماك", "🔬 المختبر المتقدم"])
    
    with animal_tabs[0]:
        render_feed_formulation("cattle", "أبقار", "🐄", 
            ["كنانة (سوداني)", "بطانة (مدر)", "هولشتاين / محسن"], 
            ["تسمين عجول", "حليب/إدرار", "صيانة"], 
            12.0, 65.0, has_measurements=True)
    with animal_tabs[1]:
        render_feed_formulation("sheep", "أغنام", "🐏", 
            ["الضأن الصحراوي", "البربري", "النعيمي"], 
            ["تسمين حملان", "حليب/إدرار", "صيانة"], 
            11.5, 62.0, has_measurements=True)
    with animal_tabs[2]:
        render_feed_formulation("goat", "ماعز", "🐐", 
            ["الماعز النوبي", "الماعز الصحراوي", "بور / محسن"], 
            ["تسمين جديان", "حليب/إدرار", "صيانة"], 
            11.0, 60.0, has_measurements=True)
    with animal_tabs[3]:
        render_feed_formulation("horse", "خيول", "🐴", 
            ["خيل عربي أصيل", "ثوروبريد", "خيول محلية"], 
            ["راحة/صيانة", "عمل مكثف", "سباق"], 
            11.0, 62.0, has_measurements=True)
    with animal_tabs[4]:
        render_feed_formulation("camel", "إبل", "🐫", 
            ["عربية (دروميداري)", "باختري (ذو سنامين)", "هجين"], 
            ["راحة/صيانة", "إنتاج حليب", "تسمين"], 
            10.0, 58.0, has_measurements=True)
    with animal_tabs[5]:
        render_feed_formulation("poultry", "دواجن", "🐔", 
            ["دواجن لاحم (Broiler)", "دواجن بياض (Layer)", "طائر السمان (Quail)"], 
            ["بادي", "نامي", "ناهي"], 
            18.0, 72.0, has_measurements=False)
    with animal_tabs[6]:
        render_feed_formulation("fish", "أسماك", "🐟", 
            ["البلطي النيلي", "القرموط"], 
            ["نمو", "تسمين نهائي"], 
            28.0, 68.0, has_measurements=False)
    
    # المختبر المتقدم
    with animal_tabs[7]:
        st.markdown('<div class="section-title">🔬 المختبر المتقدم</div>', unsafe_allow_html=True)
        st.info("تحليل الخلطات ومقارنتها مع المعايير القياسية.")
        
        if st.session_state.get("lab_sample"):
            sample = st.session_state["lab_sample"]
            st.success(f"📥 عينة من {sample['animal']} - {sample['breed']}")
            st.write(f"**البروتين المهضوم:** {sample['dp']:.2f}% | **معادل النشاء:** {sample['se']:.2f}")
            if st.button("🗑️ مسح العينة"):
                st.session_state["lab_sample"] = None
                st.rerun()
        
        lab_animal = st.selectbox("الفصيل:", ["أبقار", "أغنام", "ماعز", "خيول", "إبل", "دواجن لاحم", "دواجن بياض", "سمان", "أسماك"])
        lab_stage = st.selectbox("المرحلة:", list(STANDARD_VALUES.get(lab_animal, {}).keys()))
        standard = STANDARD_VALUES.get(lab_animal, {}).get(lab_stage, {})
        if standard:
            st.info(f"📊 المعايير القياسية لـ {lab_animal} - {lab_stage}: DP={standard.get('DP','-')}%, SE={standard.get('SE','-')} وحدة, CP={standard.get('CP','-')}%")
        lab_inputs = {}
        cols = st.columns(3)
        for idx, ing in enumerate(FLAT_FEED_DB.keys()):
            with cols[idx % 3]:
                lab_inputs[ing] = st.number_input(f"وزن {ing} (كجم)", min_value=0.0, value=0.0, step=5.0, key=f"lab_{ing}")
        
        if st.button("🧪 تشغيل التحليل المخبري", type="primary", use_container_width=True):
            total = sum(lab_inputs.values())
            if total <= 0:
                st.warning("⚠️ الرجاء إدخال أوزان أكبر من الصفر.")
                voice_guide("الرجاء إدخال أوزان أكبر من الصفر.")
            else:
                voice_guide(f"جاري تشغيل التحليل المخبري لـ {lab_animal}.")
                st.info("🔄 جاري تحليل العينة...")
                cp_total, dp_total, se_total = 0.0, 0.0, 0.0
                comps = []
                for ing, weight in lab_inputs.items():
                    if weight > 0:
                        pct = weight / total
                        feed_data = FLAT_FEED_DB.get(ing, {})
                        cp = feed_data.get("CP", 0.0)
                        dc = feed_data.get("DC", 0.0)
                        se = feed_data.get("SE", 0.0)
                        cp_total += pct * cp
                        dp_total += pct * (cp * dc)
                        se_total += pct * se
                        comps.append({"المادة": ing, "الوزن (كجم)": weight, "النسبة %": f"{pct*100:.2f}"})
                st.session_state["analysis_results"] = {'components': lab_inputs, 'cp': cp_total, 'dp': dp_total, 'se': se_total}
                st.success("🔬 تم تحليل العينة بنجاح!")
                voice_guide("تم تحليل العينة بنجاح.")
                st.markdown(f"### ⚖️ إجمالي الوزن: **{total:.1f} كجم**")
                st.table(pd.DataFrame(comps))
                st.write("#### 🔬 النتائج المحسوبة:")
                st.table(pd.DataFrame([
                    {"العنصر": "CP", "القيمة": f"{cp_total:.2f}%"},
                    {"العنصر": "DP", "القيمة": f"{dp_total:.2f}%"},
                    {"العنصر": "SE", "القيمة": f"{se_total:.2f} وحدة"}
                ]))
                
                if standard:
                    dp_dev = ((dp_total - standard.get('DP', 0)) / standard.get('DP', 1)) * 100 if standard.get('DP', 0) > 0 else 0
                    se_dev = ((se_total - standard.get('SE', 0)) / standard.get('SE', 1)) * 100 if standard.get('SE', 0) > 0 else 0
                    cp_dev = ((cp_total - standard.get('CP', 0)) / standard.get('CP', 1)) * 100 if standard.get('CP', 0) > 0 else 0
                    
                    dp_grade = "✅ ممتاز" if abs(dp_dev) <= 5 else ("👍 جيد" if abs(dp_dev) <= 10 else "⚠️ يحتاج تحسين")
                    se_grade = "✅ ممتاز" if abs(se_dev) <= 5 else ("👍 جيد" if abs(se_dev) <= 10 else "⚠️ يحتاج تحسين")
                    cp_grade = "✅ ممتاز" if abs(cp_dev) <= 5 else ("👍 جيد" if abs(cp_dev) <= 10 else "⚠️ يحتاج تحسين")
                    
                    eval_df = pd.DataFrame([
                        {"المقياس": "DP", "المحسوب": f"{dp_total:.2f}%", "القياسي": f"{standard.get('DP', 0):.2f}%", "الانحراف": f"{dp_dev:.1f}%", "التقييم": dp_grade},
                        {"المقياس": "SE", "المحسوب": f"{se_total:.2f}", "القياسي": f"{standard.get('SE', 0):.2f}", "الانحراف": f"{se_dev:.1f}%", "التقييم": se_grade},
                        {"المقياس": "CP", "المحسوب": f"{cp_total:.2f}%", "القياسي": f"{standard.get('CP', 0):.2f}%", "الانحراف": f"{cp_dev:.1f}%", "التقييم": cp_grade}
                    ])
                    st.table(eval_df)
                    
                    notes = []
                    if abs(dp_dev) > 10:
                        notes.append("⚠️ البروتين المهضوم بحاجة لضبط.")
                    if abs(se_dev) > 10:
                        notes.append("⚠️ الطاقة بحاجة لضبط.")
                    if not notes:
                        notes.append("✅ الخلطة متوازنة.")
                    for note in notes:
                        st.markdown(f'<div class="warning-card">{note}</div>', unsafe_allow_html=True)
                    
                    total_grade = "ممتاز" if all([x.startswith("✅") for x in [dp_grade, se_grade, cp_grade]]) else "جيد" if all([x.startswith("✅") or x.startswith("👍") for x in [dp_grade, se_grade, cp_grade]]) else "متوسط"
                    st.metric("⭐ التقدير العام", total_grade)
                    
                    # رسم بياني
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=['DP', 'SE', 'CP'], y=[dp_total, se_total, cp_total], name='المحسوب', marker_color='#2e7d32'))
                    fig.add_trace(go.Bar(x=['DP', 'SE', 'CP'], y=[standard.get('DP',0), standard.get('SE',0), standard.get('CP',0)], name='القياسي', marker_color='#1565C0'))
                    fig.update_layout(title="مقارنة القيم المحسوبة مع المعايير القياسية", barmode='group')
                    st.plotly_chart(fig, use_container_width=True)
                
                # PDF
                try:
                    pdf_data = pdf_generator.generate_lab_report(
                        st.session_state["analysis_results"], lab_animal, lab_stage,
                        st.session_state.get("user", {}).get("full_name", "مستخدم"),
                        standard,
                        {'DP': dp_grade, 'SE': se_grade, 'CP': cp_grade} if standard else None
                    )
                    st.download_button("📥 تحميل تقرير المختبر PDF", pdf_data, file_name=f"Lab_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf")
                except Exception as e:
                    st.warning(f"⚠️ تعذر إنشاء PDF للمختبر: {e}")

# =====================================================================
# التبويب 1: بديل الحليب السائل (جديد)
# =====================================================================
with tabs[1]:
    guide_section("بديل الحليب السائل", "تركيب بديل حليب سائل للرضاعة.")
    render_milk_replacer_formulation()

# =====================================================================
# التبويب 2: إدارة المزارع
# =====================================================================
with tabs[2]:
    guide_section("إدارة المزارع", "نظام متكامل لإدارة مزارع الدجاج.")
    st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج</div>', unsafe_allow_html=True)
    st.info("نظام متكامل لإدارة مزارع الدجاج مع حفظ دائم للبيانات.")
    
    if st.session_state["user_role"] in ["owner", "specialist", "veterinarian", "nutritionist", "breeder"]:
        with st.expander("➕ إضافة دورة جديدة"):
            col1, col2 = st.columns(2)
            with col1:
                farm_name = st.text_input("اسم المزرعة/الدورة")
                initial_birds = st.number_input("عدد الكتاكيت", min_value=1, value=1000, step=100)
            with col2:
                breed = st.selectbox("السلالة", ["Ross 308", "Cobb 500", "محلية"])
                start_date = st.date_input("تاريخ البدء", datetime.now())
            if st.button("💾 إنشاء الدورة"):
                if farm_name:
                    cycle_id = secrets.token_hex(8)
                    st.session_state["broiler_farms"][cycle_id] = {
                        "farm_name": farm_name,
                        "initial_birds": initial_birds,
                        "breed": breed,
                        "start_date": start_date.isoformat(),
                        "age_days": 0,
                        "current_weight": 0.045,
                        "total_feed": 0,
                        "dead_count": 0
                    }
                    st.success(f"✅ تم إنشاء دورة {farm_name}")
                    voice_guide(f"تم إنشاء دورة {farm_name}")
                    st.rerun()
    else:
        st.info("🔒 للمالك والمختصين فقط إضافة دورات جديدة.")
    
    if st.session_state["broiler_farms"]:
        for cid, farm in st.session_state["broiler_farms"].items():
            with st.expander(f"🏠 {farm['farm_name']} - {farm['breed']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("العدد", farm['initial_birds'])
                    st.metric("العمر (يوم)", farm['age_days'])
                with col2:
                    st.metric("الوزن (كجم)", f"{farm['current_weight']:.3f}")
                    st.metric("العلف (كجم)", f"{farm['total_feed']:.1f}")
                with col3:
                    mortality = (farm['dead_count'] / farm['initial_birds']) * 100 if farm['initial_birds'] > 0 else 0
                    st.metric("النفوق %", f"{mortality:.1f}")
                    st.metric("النافق", farm['dead_count'])
                if st.session_state["user_role"] in ["owner", "specialist", "veterinarian", "nutritionist", "breeder"]:
                    col_up1, col_up2 = st.columns(2)
                    with col_up1:
                        new_weight = st.number_input("الوزن الحالي (كجم)", min_value=0.01, value=float(farm['current_weight']), step=0.01, key=f"w_{cid}")
                        new_feed = st.number_input("العلف المستهلك (كجم)", min_value=0.0, value=float(farm['total_feed']), step=1.0, key=f"f_{cid}")
                    with col_up2:
                        new_dead = st.number_input("النافق الإضافي", min_value=0, value=0, step=1, key=f"d_{cid}")
                        new_age = st.number_input("العمر (يوم)", min_value=0, value=int(farm['age_days']), step=1, key=f"a_{cid}")
                    if st.button(f"📊 تحديث {farm['farm_name']}", key=f"up_{cid}"):
                        farm['current_weight'] = new_weight
                        farm['total_feed'] = new_feed
                        farm['dead_count'] += new_dead
                        farm['age_days'] = new_age
                        st.success("✅ تم التحديث")
                        st.rerun()
                else:
                    st.caption("🔒 التحديث متاح للمالك والمختصين فقط.")

# =====================================================================
# التبويب 3: بورصة الأسعار
# =====================================================================
with tabs[3]:
    guide_section("بورصة الأسعار", "متابعة أسعار المواشي والمنتجات.")
    st.markdown('<div class="section-title">📊 بورصة الأسعار</div>', unsafe_allow_html=True)
    if st.session_state["user_role"] in ["owner", "specialist", "veterinarian", "nutritionist", "breeder"]:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🐄 أسعار المواشي")
            for name, price in st.session_state["global_livestock_prices"].items():
                new_price = st.number_input(name, value=float(price), step=5.0, key=f"price_live_{name}")
                st.session_state["global_livestock_prices"][name] = new_price
        with col2:
            st.subheader("🥩 أسعار المنتجات")
            for name, price in st.session_state["global_products_prices"].items():
                new_price = st.number_input(name, value=float(price), step=0.5, key=f"price_prod_{name}")
                st.session_state["global_products_prices"][name] = new_price
        st.subheader("💱 أسعار الصرف")
        for country, data in EXCHANGE_RATES.items():
            new_rate = st.number_input(f"{country} - {data['currency_name']}", value=float(data['rate']), step=1.0, key=f"exchange_{country}")
            EXCHANGE_RATES[country]["rate"] = new_rate
    else:
        st.info("🔒 التعديل متاح للمالك والمختصين فقط.")

# =====================================================================
# التبويب 4: المستودعات
# =====================================================================
with tabs[4]:
    guide_section("المستودعات", "إدارة المخزون.")
    st.markdown('<div class="section-title">🏭 المستودعات</div>', unsafe_allow_html=True)
    inv_data = []
    for item, data in st.session_state["inventory"].items():
        inv_data.append({"المادة": item, "الكمية (طن/كجم)": data["quantity"], "الحد الأدنى": data["min_threshold"]})
    st.dataframe(pd.DataFrame(inv_data), use_container_width=True)
    
    if st.session_state["user_role"] in ["owner", "specialist", "veterinarian", "nutritionist", "breeder"]:
        with st.expander("تحديث المخزون"):
            sel = st.selectbox("المادة", list(FLAT_FEED_DB.keys()) + list(LIQUID_FEED_DB.keys()))
            new_qty = st.number_input("الكمية الجديدة", min_value=0.0, value=25.0)
            if st.button("تحديث"):
                st.session_state["inventory"][sel]["quantity"] = new_qty
                st.success("✅ تم التحديث")
                st.rerun()
    else:
        st.caption("🔒 التحديث متاح للمالك والمختصين فقط.")

# =====================================================================
# التبويب 5: الإنتاج اليومي
# =====================================================================
with tabs[5]:
    guide_section("الإنتاج اليومي", "تسجيل بيانات الإنتاج اليومي.")
    st.markdown('<div class="section-title">📈 الإنتاج اليومي</div>', unsafe_allow_html=True)
    
    if st.session_state["user_role"] in ["owner", "specialist", "veterinarian", "nutritionist", "breeder"]:
        with st.form("daily_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                farm = st.text_input("المزرعة")
                date = st.date_input("التاريخ", datetime.now())
            with col2:
                milk = st.number_input("الحليب (لتر)", min_value=0.0, value=0.0)
                eggs = st.number_input("البيض (عدد)", min_value=0, value=0)
            with col3:
                weight_gain = st.number_input("زيادة الوزن (كجم)", min_value=0.0, value=0.0)
                mortality = st.number_input("النافق", min_value=0, value=0)
            notes = st.text_area("ملاحظات")
            if st.form_submit_button("💾 حفظ"):
                st.session_state["daily_production_log"].append({
                    "farm": farm, "date": date.isoformat(), "milk": milk, "eggs": eggs,
                    "weight_gain": weight_gain, "mortality": mortality, "notes": notes
                })
                st.success("✅ تم الحفظ")
    else:
        st.info("🔒 الإضافة متاحة للمالك والمختصين فقط.")
    
    if st.session_state["daily_production_log"]:
        st.subheader("📋 سجل الإنتاج اليومي")
        df_prod = pd.DataFrame(st.session_state["daily_production_log"])
        st.dataframe(df_prod, use_container_width=True, hide_index=True)

# =====================================================================
# التبويب 6: التنبيهات
# =====================================================================
with tabs[6]:
    guide_section("التنبيهات", "تنبيهات المخزون والإنتاج.")
    st.markdown('<div class="section-title">🔔 التنبيهات</div>', unsafe_allow_html=True)
    warnings = InventoryManager.check_stock_levels()
    if warnings:
        for item, info in warnings.items():
            st.warning(f"{item}: {info['status']}")
    else:
        st.success("✅ لا توجد تنبيهات")

# =====================================================================
# التبويب 7: المراجع العلمية
# =====================================================================
with tabs[7]:
    guide_section("المراجع العلمية", "مصادر معتمدة في تغذية الحيوان.")
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
    for cat_key, cat_data in ScientificReferenceSystem.REFERENCES.items():
        with st.expander(f"{cat_data['icon']} {cat_data['title']}"):
            for ref in cat_data.get("references", []):
                st.markdown(f"""
                <div style='background:#f8f9fa; padding:12px; border-radius:8px; margin-bottom:8px; border-right:4px solid #2e7d32;'>
                    <b>{ref.get('title', 'عنوان غير محدد')}</b><br>
                    👤 {ref.get('authors', 'مؤلف غير محدد')}<br>
                    📅 {ref.get('year', 'سنة غير محددة')} | 📚 {ref.get('publisher', 'ناشر غير محدد')}<br>
                    <small>{ref.get('summary', '')}</small>
                </div>
                """, unsafe_allow_html=True)
    st.subheader("💡 المعرفة السريعة")
    q = st.text_input("اسأل عن مصطلح:")
    if q:
        answer = ScientificReferenceSystem.get_knowledge_answer(q)
        if answer:
            st.success(f"📖 {answer['answer']}")
            st.info(f"🔹 تبسيط: {answer['simplified']}")

# =====================================================================
# التبويب 8: المساعدة
# =====================================================================
with tabs[8]:
    guide_section("المساعدة", "دليل سريع للمنصة.")
    st.markdown('<div class="section-title">💡 المساعدة</div>', unsafe_allow_html=True)
    st.markdown("""
    1. اختر نوع الحيوان والمرحلة.
    2. حدد العمر والحالة الفسيولوجية.
    3. اختر المكونات العلفية.
    4. اضغط على زر التشغيل للحصول على خلطة مثالية.
    5. استخدم المختبر لتحليل خلطاتك.
    6. يمكنك إرسال العينة إلى المختبر بضغطة زر.
    7. استخدم تبويب بديل الحليب السائل للرضاعة.
    """)
    if st.button("🔊 استمع للتعليمات"):
        voice_guide("مرحباً، هذا دليل استخدام منصة تاور نولجي العلمية. اختر نوع الحيوان، ثم المرحلة، والعمر، والحالة الفسيولوجية، واختر المكونات، ثم اضغط على زر التشغيل.")

# =====================================================================
# التبويب 9: الدليل
# =====================================================================
with tabs[9]:
    guide_section("دليل المستخدم", "شرح مفصل للمنصة.")
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="manual-book">
    <div class="book-chapter">📘 الفصل 1: مقدمة</div>
    <div class="book-body">
    تاور نولجي Tawornology العلمية منصة متكاملة لتركيب الأعلاف وإدارة الإنتاج الحيواني.
    تعتمد على البرمجة الخطية لحساب أقل تكلفة لخلطة علفية تلبي الاحتياجات الغذائية.
    </div>
    <div class="book-chapter">📗 الفصل 2: تركيب العلف الجاف</div>
    <div class="book-body">
    1. اختر نوع الحيوان.<br>
    2. حدد السلالة والمرحلة الإنتاجية.<br>
    3. أدخل العمر والحالة الفسيولوجية.<br>
    4. اختر المكونات العلفية وحدد أسعارها.<br>
    5. اضغط على "تشغيل محرك التركيب" للحصول على الخلطة المثالية.
    </div>
    <div class="book-chapter">🍼 الفصل 3: بديل الحليب السائل</div>
    <div class="book-body">
    يستخدم لتركيب خلطات سائلة بديلة للحليب الطبيعي لتغذية الصغار.
    اختر المكونات، وحدد الاحتياجات الغذائية، واحصل على الخلطة المثالية.
    </div>
    <div class="book-chapter">📕 الفصل 4: المختبر المتقدم</div>
    <div class="book-body">
    أدخل أوزان المكونات أو استخدم العينة المرسلة من التركيب، وقارن نتائجك مع المعايير القياسية.
    </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# التبويب 10: إرسال الكود (للمالك فقط)
# =====================================================================
if st.session_state["user_role"] == "owner" and len(tabs) > 10:
    with tabs[10]:
        guide_section("إرسال الكود", "إرسال السورس كود إلى البريد.")
        st.markdown('<div class="section-title">📧 إرسال السورس كود</div>', unsafe_allow_html=True)
        st.info("هذه الخاصية متاحة فقط للمالك (الاختصاصي م. عبد القادر إسماعيل تاور)")
        col1, col2 = st.columns([2, 1])
        with col1:
            email = st.text_input("البريد الإلكتروني المستلم:", value=OWNER_EMAIL)
        with col2:
            if st.button("📤 إرسال الكود", use_container_width=True):
                if email and '@' in email:
                    if email.strip().lower() == OWNER_EMAIL.strip().lower():
                        with st.spinner("جاري الإرسال..."):
                            success, msg = send_code_to_email(email)
                            st.success(msg) if success else st.error(msg)
                    else:
                        st.error(f"❌ الإرسال مسموح فقط للبريد: {OWNER_EMAIL}")
                else:
                    st.warning("⚠️ يرجى إدخال بريد صحيح")
        st.caption("ℹ️ يتم استخدام كلمة مرور تطبيق Gmail (App Password) لإرسال البريد. أدخلها عند الطلب.")

# =====================================================================
# التذييل
# =====================================================================
st.markdown("""
<div style='text-align:center; padding:20px; margin-top:30px; border-top:2px solid #e0e0e0; color:#888; font-size:0.9rem;'>
🌾 <b>تاور نولجي Tawornology العلمية</b> - للانتاج الحيواني وتركيب الاعلاف<br>
© 2026 | الاختصاصي م. عبد القادر إسماعيل تاور<br>
🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b> - رحمهما الله
</div>
""", unsafe_allow_html=True)

if st.button("🔊 اختبار الصوت"):
    voice_guide("بسم الله الرحمن الرحيم، هذا اختبار للنظام الصوتي.")

# =====================================================================
# نهاية الكود
# =====================================================================
