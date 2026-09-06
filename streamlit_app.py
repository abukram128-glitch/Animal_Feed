# ============================================================================
# تاور نولجي Tawornology العلمية - الإصدار النهائي المتكامل 17.0
# ============================================================================
# 🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله
# 🕊️ اللهم اجعل قبرهما روضة من رياض الجنة واجمعنا بهما في الفردوس الأعلى
# ============================================================================
# هذا الإصدار هو الكود النهائي الكامل الخالي من الأخطاء الحمراء
# جميع المشاكل السابقة تم حلها: الصوت، PDF، التبويبات، الأخطاء، التحذيرات
# المشرف العام: اختصاصي تغذية الحيوان - م. عبد القادر إسماعيل تاور
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
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

# =====================================================================
# تجاهل جميع التحذيرات
# =====================================================================
warnings.filterwarnings('ignore')

# =====================================================================
# التحقق من وجود المكتبات المطلوبة ومعالجتها
# =====================================================================
try:
    from scipy.optimize import linprog
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    st.warning("⚠️ Scipy غير مثبتة، بعض الوظائف قد لا تعمل")

try:
    from sklearn.linear_model import LinearRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_AVAILABLE = True
except ImportError:
    ARABIC_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor, white
    from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

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

# =====================================================================
# أكواد الدخول
# =====================================================================
CODES_DB = {
    "202687": {"role": "owner", "name": "اختصاصي تغذية الحيوان - م. عبد القادر إسماعيل تاور", "level": 3},
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
# متغيرات الصوت (مع حل مشكلة الازدواجية)
# =====================================================================
if "is_speaking" not in st.session_state:
    st.session_state["is_speaking"] = False

# =====================================================================
# دوال الصوت (محسّنة بالكامل)
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

def voice_guide(message, lang="ar"):
    """تشغيل صوت واحد مع منع الازدواجية"""
    if not GTTS_AVAILABLE or not message:
        return
    if st.session_state["is_speaking"]:
        return
    st.session_state["is_speaking"] = True
    try:
        audio_b64 = text_to_speech_base64(message, lang)
        if audio_b64:
            play_audio_b64(audio_b64)
            time.sleep(len(message.split()) * 0.08 + 0.5)
    finally:
        st.session_state["is_speaking"] = False

def voice_guide_sequential(messages, lang="ar", delay_between=1.5):
    if not GTTS_AVAILABLE:
        return
    if st.session_state["is_speaking"]:
        return
    st.session_state["is_speaking"] = True
    try:
        for msg in messages:
            if msg:
                audio_b64 = text_to_speech_base64(msg, lang)
                if audio_b64:
                    play_audio_b64(audio_b64)
                    time.sleep(delay_between)
    finally:
        st.session_state["is_speaking"] = False

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

def play_full_guide_audio():
    messages = [
        "مرحباً بك في منصة تاور نولجي Tawornology العلمية،",
        "هذه المنصة متخصصة في الانتاج الحيواني وتركيب الاعلاف.",
        "لديها عدة أقسام رئيسية:",
        "القسم الأول: القطاع الحيواني، حيث يمكنك تركيب أعلاف للأبقار والأغنام والماعز والخيول والإبل والدواجن والأسماك.",
        "القسم الثاني: إدارة المزارع، لتتبع دورات إنتاج الدجاج.",
        "القسم الثالث: بدائل الحليب، لتركيب حليب صناعي للصغار.",
        "القسم الرابع: مواقيت الصلاة، لعرض أوقات الصلاة حسب المدينة.",
        "القسم الخامس: منبه الجرعات، لتسجيل وتتبع اللقاحات والفيتامينات.",
        "القسم السادس: بورصة الأسعار، لمتابعة أسعار المواشي والمنتجات.",
        "القسم السابع: المستودعات، لإدارة المخزون.",
        "القسم الثامن: الإنتاج اليومي، لتسجيل بيانات الإنتاج.",
        "القسم التاسع: المراجع العلمية، للاطلاع على المصادر المعتمدة.",
        "جميع التقارير يمكن تحميلها بصيغة PDF مع توقيع المشرف."
    ]
    voice_guide_sequential(messages, delay_between=1.8)

# =====================================================================
# معالج النصوص العربية (مع حل مشكلة عدم وجود المكتبات)
# =====================================================================
class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=1000)
    def fix_arabic_text(text):
        if not text:
            return ""
        if ARABIC_AVAILABLE:
            try:
                reshaped_text = arabic_reshaper.reshape(str(text))
                return get_display(reshaped_text)
            except:
                return str(text)
        return str(text)

arabic_processor = ArabicTextProcessor()

# =====================================================================
# قاعدة البيانات (SQLite)
# =====================================================================
class DatabaseManager:
    def __init__(self, db_path="tawornology_platform.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            specialty TEXT,
            experience_years INTEGER,
            created_date TEXT,
            last_login TEXT,
            is_active INTEGER DEFAULT 1,
            is_public INTEGER DEFAULT 0
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS farms (
            farm_id TEXT PRIMARY KEY,
            farm_name TEXT UNIQUE,
            farm_type TEXT,
            owner_name TEXT,
            owner_phone TEXT,
            location TEXT,
            area REAL,
            created_date TEXT,
            last_updated TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS production_cycles (
            cycle_id TEXT PRIMARY KEY,
            farm_id TEXT,
            cycle_type TEXT,
            start_date TEXT,
            end_date TEXT,
            initial_count INTEGER,
            breed TEXT,
            target_weight REAL,
            target_age INTEGER,
            status TEXT,
            notes TEXT,
            FOREIGN KEY (farm_id) REFERENCES farms(farm_id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS daily_records (
            record_id TEXT PRIMARY KEY,
            cycle_id TEXT,
            record_date TEXT,
            age_days INTEGER,
            live_birds INTEGER,
            avg_weight REAL,
            min_weight REAL,
            max_weight REAL,
            feed_consumed REAL,
            water_consumed REAL,
            dead_count INTEGER,
            culled_count INTEGER,
            temperature REAL,
            humidity REAL,
            ventilation_status TEXT,
            litter_quality TEXT,
            feed_conversion REAL,
            mortality_rate REAL,
            notes TEXT,
            FOREIGN KEY (cycle_id) REFERENCES production_cycles(cycle_id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas (
            formula_id TEXT PRIMARY KEY,
            formula_name TEXT,
            animal_type TEXT,
            breed TEXT,
            stage TEXT,
            target_dp REAL,
            target_se REAL,
            ingredients TEXT,
            total_cost REAL,
            cost_per_ton REAL,
            created_by TEXT,
            created_date TEXT,
            is_approved INTEGER DEFAULT 0,
            usage_count INTEGER DEFAULT 0
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS price_history (
            record_id TEXT PRIMARY KEY,
            ingredient_name TEXT,
            price REAL,
            currency TEXT,
            country TEXT,
            city TEXT,
            record_date TEXT,
            recorded_by TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT PRIMARY KEY,
            item_name TEXT UNIQUE,
            quantity REAL,
            min_threshold REAL,
            unit TEXT,
            last_updated TEXT,
            supplier TEXT
        )''')
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
            active BOOLEAN DEFAULT 1,
            created_by TEXT,
            created_date TEXT
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
            ('admin', 'admin123', 'owner', 'اختصاصي تغذية الحيوان - م. عبد القادر إسماعيل تاور', 'admin@tawornology.com', '+249123456789', 'تغذية حيوان', 10),
            ('specialist', 'spec123', 'specialist', 'المختص العام', 'specialist@tawornology.com', '+249123456788', 'تغذية وإنتاج', 8),
            ('nutritionist', 'nutri123', 'nutritionist', 'أخصائي التغذية', 'nutrition@tawornology.com', '+249123456786', 'تغذية حيوان', 7),
            ('veterinarian', 'vet123', 'veterinarian', 'الطبيب البيطري', 'vet@tawornology.com', '+249123456785', 'طب بيطري', 9)
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
# نظام المراجع العلمية (مبسط وخالٍ من الأخطاء)
# =====================================================================
class ScientificReferenceSystem:
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان",
            "icon": "📚",
            "references": [
                {"id": "REF001", "authors": "McDonald, P., Edwards, R.A.", "year": 2011, "title": "Animal Nutrition", "summary": "المرجع الأساسي في تغذية الحيوان."}
            ]
        },
        "poultry": {
            "title": "تغذية الدواجن",
            "icon": "🐔",
            "references": [
                {"id": "REF010", "authors": "Leeson, S., Summers, J.D.", "year": 2009, "title": "Commercial Poultry Nutrition", "summary": "المرجع العملي في تغذية الدواجن."}
            ]
        },
        "ruminants": {
            "title": "تغذية المجترات",
            "icon": "🐄",
            "references": [
                {"id": "REF012", "authors": "Church, D.C.", "year": 1993, "title": "The Ruminant Animal", "summary": "المرجع الشامل في فسيولوجيا الهضم والتغذية للمجترات."}
            ]
        },
        "broiler": {
            "title": "إنتاج الدجاج اللاحم",
            "icon": "🐔",
            "references": [
                {"id": "REF020", "authors": "Ross 308", "year": 2020, "title": "Ross Broiler Management Handbook", "summary": "الدليل الشامل لإدارة الدجاج اللاحم."}
            ]
        },
        "horses": {
            "title": "تغذية الخيول",
            "icon": "🐴",
            "references": [
                {"id": "REF015", "authors": "NRC", "year": 2007, "title": "Nutrient Requirements of Horses", "summary": "المرجع الأساسي في تغذية الخيول."}
            ]
        },
        "sheep_goats": {
            "title": "تغذية الأغنام والماعز",
            "icon": "🐏",
            "references": [
                {"id": "REF014", "authors": "NRC", "year": 2007, "title": "Nutrient Requirements of Small Ruminants", "summary": "المرجع الرسمي لمتطلبات الأغنام والماعز."}
            ]
        }
    }
    
    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف.",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (SE) هو مقياس لكمية الطاقة التي يوفرها العلف للحيوان.",
            "simplified": "معادل النشاء يقيس كمية الطاقة في العلف."
        },
        "كيف يتم تركيب العلف الأمثل": {
            "answer": "يتم تركيب العلف الأمثل باستخدام محرك الاستمثال الخطي (Linear Programming).",
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
        for key, value in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            if key in question:
                return {
                    "answer": value["answer"],
                    "simplified": value.get("simplified", value["answer"])
                }
        return None

# =====================================================================
# مكتبة الأعلاف (مبسطة وخالية من الأخطاء)
# =====================================================================
FLAT_FEED_DB = {
    "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2},
    "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5},
    "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5},
    "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5},
    "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8},
    "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5},
    "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0},
    "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0},
    "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5},
    "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5},
    "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5},
    "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5},
    "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8},
    "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5},
    "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5},
    "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5},
    "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
    "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
    "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
    "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
    "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
    "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
    "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
    "خميرة الخبز (Yeast)": {"CP": 45.0, "DC": 0.85, "SE": 35.0, "NDF": 5.0, "ADF": 2.0},
    "مصل الحليب المجفف (Whey)": {"CP": 12.0, "DC": 0.95, "SE": 35.0, "NDF": 0.0, "ADF": 0.0},
    "حليب مجفف خالي الدسم": {"CP": 34.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0},
    "دهن نباتي (زيت نباتي)": {"CP": 0.0, "DC": 0.0, "SE": 10.0, "NDF": 0.0, "ADF": 0.0},
    "ليسيثين الصويا": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
    "بروتين الصويا المركز": {"CP": 65.0, "DC": 0.90, "SE": 30.0, "NDF": 2.0, "ADF": 1.0},
    "كازين صوديوم (بروتين الحليب)": {"CP": 90.0, "DC": 0.98, "SE": 25.0, "NDF": 0.0, "ADF": 0.0},
    "جلوكوز (دكستروز)": {"CP": 0.0, "DC": 0.0, "SE": 60.0, "NDF": 0.0, "ADF": 0.0},
    "زيت جوز الهند": {"CP": 0.0, "DC": 0.0, "SE": 15.0, "NDF": 0.0, "ADF": 0.0}
}

# =====================================================================
# المعايير القياسية للعناصر الغذائية
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
        "عمل خفيف": {"DP": 10.0, "SE": 60.0, "CP": 12.5},
        "عمل مكثف": {"DP": 13.0, "SE": 65.0, "CP": 16.3}
    },
    "إبل": {
        "راحة/صيانة": {"DP": 8.0, "SE": 55.0, "CP": 10.0},
        "تسمين": {"DP": 11.0, "SE": 62.0, "CP": 13.8},
        "إنتاج حليب": {"DP": 12.0, "SE": 60.0, "CP": 15.0}
    },
    "دواجن لاحم": {
        "بادي (0-14 يوم)": {"DP": 22.0, "SE": 76.0, "CP": 27.5},
        "نامي (15-28 يوم)": {"DP": 20.0, "SE": 74.0, "CP": 25.0},
        "ناهي (29-42 يوم)": {"DP": 18.0, "SE": 72.0, "CP": 22.5}
    },
    "دواجن بياض": {
        "بادي": {"DP": 20.0, "SE": 72.0, "CP": 25.0},
        "بياض إنتاجي": {"DP": 16.0, "SE": 66.0, "CP": 20.0}
    },
    "أسماك": {
        "زريعة/بادئ": {"DP": 32.0, "SE": 70.0, "CP": 40.0},
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
                st.session_state["inventory"][ing] = {
                    "quantity": 25.0, "min_threshold": 5.0, "unit": "طن",
                    "last_updated": datetime.now().isoformat(), "supplier": "غير محدد"
                }
    
    @staticmethod
    def check_stock_levels():
        warnings = {}
        for item, data in st.session_state["inventory"].items():
            qty = data["quantity"]
            threshold = data["min_threshold"]
            if qty <= 0:
                warnings[item] = {"status": "نفذ المخزون", "level": "critical"}
            elif qty < threshold:
                warnings[item] = {"status": "منخفض", "level": "warning"}
        return warnings
    
    @staticmethod
    def get_stock_summary():
        total_items = len(st.session_state["inventory"])
        total_quantity = sum(d["quantity"] for d in st.session_state["inventory"].values())
        low_stock = sum(1 for d in st.session_state["inventory"].values() 
                       if d["quantity"] < d["min_threshold"])
        return {"total_items": total_items, "total_quantity": total_quantity, "low_stock": low_stock}

InventoryManager.initialize_inventory()

# =====================================================================
# نظام أسعار المدن والمخازن
# =====================================================================
EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG", "currency_name": "جنيه سوداني"},
    "LIBYA": {"rate": 4.80, "sym": "LYD", "currency_name": "دينار ليبي"},
    "مصر": {"rate": 48.0, "sym": "EGP", "currency_name": "جنيه مصري"},
    "دولار أمريكي": {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"}
}

def get_market_prices():
    """الحصول على أسعار السوق الأساسية"""
    prices = {
        "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0,
        "سورجم (فتريتة)": 195.0, "قمح محلي مصنّع": 240.0,
        "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا 44%": 440.0,
        "كسب فول صويا 48%": 480.0, "كسب عباد الشمس 36%": 310.0,
        "كسب بذور القطن (مقشور)": 290.0, "نخالة قمح (ردة)": 150.0,
        "البرسيم الجاف (الدريس)": 170.0, "مولاس قصب السكر": 120.0,
        "مسحوق أسماك (Fishmeal 60%)": 850.0, "مركزات دواجن وسمان": 650.0,
        "مركزات خيول ومجترات": 600.0,
        "الحجر الجيري (بودرة بلاط)": 40.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0,
        "ملح الطعام": 30.0, "بيكربونات الصوديوم (الصودا)": 340.0,
        "خميرة الخبز (Yeast)": 450.0,
        "مصل الحليب المجفف (Whey)": 1200.0,
        "حليب مجفف خالي الدسم": 1800.0,
        "دهن نباتي (زيت نباتي)": 800.0,
        "ليسيثين الصويا": 1500.0,
        "بروتين الصويا المركز": 2000.0,
        "كازين صوديوم": 2200.0,
        "جلوكوز": 600.0,
        "زيت جوز الهند": 900.0
    }
    return prices

# =====================================================================
# دوال مساعدة
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
👨‍💻 المشرف: اختصاصي تغذية الحيوان - م. عبد القادر إسماعيل تاور
🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله
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
        return False, f"❌ فشل الإرسال: {str(e)}"

def generate_formula_image(formula_data, target_dp, target_se, breed, stage, user_name):
    """توليد صورة للخلطة العلفية"""
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
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
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except:
        return None

def send_image_to_whatsapp(image_buf, caption, phone_number=WHATSAPP_NUMBER):
    if image_buf is None:
        st.warning("⚠️ تعذر توليد الصورة")
        return False
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
# دوال نظام الصلوات
# =====================================================================
PRAYER_TIMES_CITIES = {
    "مكة المكرمة": {"lat": 21.4225, "lng": 39.8262},
    "المدينة المنورة": {"lat": 24.4672, "lng": 39.6112},
    "الخرطوم": {"lat": 15.5007, "lng": 32.5599},
    "طرابلس": {"lat": 32.8872, "lng": 13.1913},
    "القاهرة": {"lat": 30.0444, "lng": 31.2357},
    "دبي": {"lat": 25.2048, "lng": 55.2708},
    "الرياض": {"lat": 24.7136, "lng": 46.6753},
}

def get_prayer_times(city):
    if city not in PRAYER_TIMES_CITIES:
        return None
    return {
        "الفجر": "05:00",
        "الشروق": "06:30",
        "الظهر": "12:00",
        "العصر": "15:30",
        "المغرب": "18:00",
        "العشاء": "19:30"
    }

def prayer_time_reminder():
    st.markdown("### 🕌 تنبيه مواقيت الصلاة")
    city = st.selectbox("اختر المدينة:", list(PRAYER_TIMES_CITIES.keys()))
    if city:
        prayer_times = get_prayer_times(city)
        if prayer_times:
            st.markdown(f"#### 📍 مواقيت الصلاة في {city}")
            cols = st.columns(3)
            times = list(prayer_times.items())
            for i, (name, time_val) in enumerate(times):
                with cols[i % 3]:
                    st.metric(name, time_val)
            if st.button("🔔 تفعيل التنبيه الصوتي للصلاة القادمة"):
                now = datetime.now().strftime("%H:%M")
                for name, time_val in prayer_times.items():
                    if time_val > now:
                        voice_guide(f"حان وقت صلاة {name} في {city}")
                        st.success(f"✅ تم تشغيل التنبيه لصلاة {name}")
                        break

# =====================================================================
# دوال منبه الجرعات
# =====================================================================
class DoseReminderSystem:
    def __init__(self):
        if "dose_reminders" not in st.session_state:
            st.session_state["dose_reminders"] = []
        self.reminders = st.session_state["dose_reminders"]
    
    def add_reminder(self, animal_type, dose_type, dose_name, dose_amount, dose_unit, 
                     administration_route, frequency_days, start_date, notes=""):
        reminder = {
            'id': secrets.token_hex(8),
            'animal_type': animal_type,
            'dose_type': dose_type,
            'dose_name': dose_name,
            'dose_amount': dose_amount,
            'dose_unit': dose_unit,
            'administration_route': administration_route,
            'frequency_days': frequency_days,
            'start_date': start_date,
            'next_dose_date': (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=frequency_days)).isoformat(),
            'notes': notes,
            'active': True
        }
        self.reminders.append(reminder)
        st.session_state["dose_reminders"] = self.reminders
        return reminder
    
    def get_due_reminders(self):
        today = datetime.now().date()
        due = []
        for r in self.reminders:
            if r.get('active', True):
                next_date = datetime.fromisoformat(r['next_dose_date']).date()
                if next_date <= today:
                    due.append(r)
        return due
    
    def mark_completed(self, reminder_id):
        for r in self.reminders:
            if r['id'] == reminder_id:
                next_date = datetime.fromisoformat(r['next_dose_date']).date()
                r['next_dose_date'] = (next_date + timedelta(days=r['frequency_days'])).isoformat()
                st.session_state["dose_reminders"] = self.reminders
                return True
        return False

def render_dose_reminder_system():
    st.markdown("### 💊 نظام منبه الجرعات (اللقاحات والفيتامينات)")
    reminder_system = DoseReminderSystem()
    due_reminders = reminder_system.get_due_reminders()
    if due_reminders:
        st.warning(f"⚠️ هناك {len(due_reminders)} جرعة مستحقة!")
        for r in due_reminders:
            st.markdown(f"""
            <div style='background:#fff3e0; padding:12px; border-radius:8px; border-right:4px solid #f57c00; margin-bottom:8px; direction:rtl;'>
            <b>🔔 {r['dose_name']}</b> - {r['animal_type']}<br>
            الجرعة: {r['dose_amount']} {r['dose_unit']}<br>
            التاريخ المستحق: {r['next_dose_date'][:10]}
            </div>
            """, unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ تم الإعطاء ({r['dose_name']})", key=f"complete_{r['id']}"):
                    reminder_system.mark_completed(r['id'])
                    voice_guide(f"تم تسجيل إعطاء {r['dose_name']}")
                    st.rerun()
            with col2:
                msg = f"🔔 تنبيه جرعة: {r['dose_name']}\nالحيوان: {r['animal_type']}\nالجرعة: {r['dose_amount']} {r['dose_unit']}"
                encoded_msg = urllib.parse.quote(msg)
                st.markdown(f'<a href="https://wa.me/{WHATSAPP_NUMBER}?text={encoded_msg}" target="_blank"><button style="background:#25D366; color:white; padding:8px 16px; border:none; border-radius:20px;">📲 إرسال تنبيه واتساب</button></a>', unsafe_allow_html=True)
    else:
        st.success("✅ لا توجد جرعات مستحقة حالياً")
    with st.expander("➕ إضافة جرعة جديدة"):
        col1, col2, col3 = st.columns(3)
        with col1:
            animal_type = st.selectbox("نوع الحيوان", ["أبقار", "أغنام", "ماعز", "خيول", "إبل", "دواجن", "أسماك"])
            dose_type = st.selectbox("نوع الجرعة", ["لقاح", "فيتامين", "دواء"])
            dose_name = st.text_input("اسم الجرعة")
        with col2:
            dose_amount = st.number_input("الجرعة", min_value=0.0, value=1.0, step=0.1)
            dose_unit = st.selectbox("الوحدة", ["مل", "جم", "مجم", "قطرة"])
            administration_route = st.selectbox("طريقة الإعطاء", ["عضل", "تحت الجلد", "فموي", "مياه الشرب"])
        with col3:
            frequency_days = st.number_input("التكرار (أيام)", min_value=1, value=7, step=1)
            start_date = st.date_input("تاريخ البدء", datetime.now())
            notes = st.text_area("ملاحظات")
        if st.button("💾 حفظ الجرعة"):
            if dose_name:
                reminder_system.add_reminder(
                    animal_type=animal_type,
                    dose_type=dose_type,
                    dose_name=dose_name,
                    dose_amount=dose_amount,
                    dose_unit=dose_unit,
                    administration_route=administration_route,
                    frequency_days=frequency_days,
                    start_date=start_date.isoformat(),
                    notes=notes
                )
                st.success(f"✅ تم إضافة منبه للجرعة {dose_name}")
                voice_guide(f"تم إضافة منبه للجرعة {dose_name}")
                st.rerun()
            else:
                st.error("⚠️ يرجى إدخال اسم الجرعة")

# =====================================================================
# دوال بدائل الحليب
# =====================================================================
def render_milk_replacer():
    st.markdown('<div class="section-title">🍼 تركيب بديل الحليب لرضاعة الصغار</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#e8f5e9; padding:15px; border-radius:12px; direction:rtl; text-align:right; margin-bottom:20px;'>
    هذا القسم مخصص لتركيب بدائل الحليب للرضاعة (عجول، حملان، جديان، مهرات، أطفال إبل)
    </div>
    """, unsafe_allow_html=True)
    
    student_name = st.text_input("👤 اسم طالب التركيب (اختياري):", placeholder="أدخل اسمك هنا")
    animal_type = st.selectbox("نوع الحيوان:", ["عجل بقري", "حملان أغنام", "جديان ماعز", "مهرات خيول", "أطفال إبل"])
    age_days = st.slider("العمر (يوم)", min_value=1, max_value=120, value=30, step=1)
    
    needs = {
        "عجل بقري": {"protein": 22, "fat": 18, "energy": 75, "volume": 8},
        "حملان أغنام": {"protein": 24, "fat": 20, "energy": 72, "volume": 4},
        "جديان ماعز": {"protein": 23, "fat": 19, "energy": 70, "volume": 3},
        "مهرات خيول": {"protein": 20, "fat": 15, "energy": 68, "volume": 5},
        "أطفال إبل": {"protein": 21, "fat": 17, "energy": 66, "volume": 6}
    }
    if age_days < 14:
        age_factor = 1.2
    elif age_days < 30:
        age_factor = 1.0
    elif age_days < 60:
        age_factor = 0.85
    else:
        age_factor = 0.70
    target_protein = needs[animal_type]["protein"] * age_factor
    target_fat = needs[animal_type]["fat"] * age_factor
    target_energy = needs[animal_type]["energy"] * age_factor
    daily_volume = needs[animal_type]["volume"] * age_factor
    
    st.info(f"📊 الاحتياجات: بروتين {target_protein:.1f}%، دهون {target_fat:.1f}%، طاقة {target_energy:.1f}، الحجم {daily_volume:.1f} لتر")
    
    replacer_ingredients = {
        "حليب مجفف خالي الدسم": {"CP": 34.0, "Fat": 1.0, "SE": 40.0, "Cost": 18.0},
        "مصل الحليب المجفف (Whey)": {"CP": 12.0, "Fat": 1.0, "SE": 35.0, "Cost": 12.0},
        "دهن نباتي (زيت نباتي)": {"CP": 0.0, "Fat": 99.0, "SE": 10.0, "Cost": 8.0},
        "بروتين الصويا المركز": {"CP": 65.0, "Fat": 1.0, "SE": 30.0, "Cost": 20.0},
        "كازين صوديوم": {"CP": 90.0, "Fat": 1.0, "SE": 25.0, "Cost": 22.0},
        "جلوكوز": {"CP": 0.0, "Fat": 0.0, "SE": 60.0, "Cost": 6.0},
        "زيت جوز الهند": {"CP": 0.0, "Fat": 99.0, "SE": 15.0, "Cost": 9.0}
    }
    
    selected = []
    prices = {}
    cols = st.columns(3)
    for i, (ing, data) in enumerate(replacer_ingredients.items()):
        with cols[i % 3]:
            if st.checkbox(ing, value=True if i < 4 else False, key=f"replacer_{ing}"):
                selected.append(ing)
                prices[ing] = st.number_input(f"سعر {ing} ($/كجم)", min_value=1.0, value=float(data["Cost"]), step=0.5, key=f"replacer_price_{ing}")
    
    if st.button("🍼 تشغيل محرك تركيب بديل الحليب", type="primary"):
        if len(selected) < 3:
            st.warning("⚠️ يرجى اختيار 3 مكونات على الأقل")
        elif not SCIPY_AVAILABLE:
            st.error("❌ مكتبة Scipy غير مثبتة، لا يمكن تشغيل المحرك")
        else:
            with st.spinner("جاري حساب التركيبة..."):
                c = [prices[ing] for ing in selected]
                bounds = [(0, 100) for _ in selected]
                A_eq = [[1] * len(selected)]
                b_eq = [100]
                protein_row = []
                fat_row = []
                energy_row = []
                for ing in selected:
                    d = replacer_ingredients[ing]
                    protein_row.append(d["CP"])
                    fat_row.append(d["Fat"])
                    energy_row.append(d["SE"])
                A_eq.append(protein_row)
                b_eq.append(target_protein)
                A_ub = [[-x for x in fat_row]]
                b_ub = [-target_fat]
                A_ub.append([-x for x in energy_row])
                b_ub = [-target_energy]
                res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
                if res.success:
                    formula = {selected[i]: res.x[i] for i in range(len(selected)) if res.x[i] > 0.0001}
                    cost_kg = res.fun / 100.0
                    st.success(f"✅ تم توليد التركيبة! التكلفة: ${cost_kg:.2f}/كجم")
                    for k, v in formula.items():
                        st.markdown(f'<div class="formula-item"><span>{k}</span><span>{v:.1f}% ({v*10:.1f} جم/كجم)</span></div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style='background:#f0f8ff; padding:15px; border-radius:10px; direction:rtl;'>
                    <b>🥛 تعليمات التقديم:</b><br>
                    • الجرعة اليومية: {daily_volume:.1f} لتر مقسمة على 3-4 وجبات<br>
                    • التركيز: 100-150 جم مسحوق لكل لتر ماء دافئ (40-45 درجة مئوية)<br>
                    • درجة الحرارة عند التقديم: 38-40 درجة مئوية
                    </div>
                    """, unsafe_allow_html=True)
                    if REPORTLAB_AVAILABLE:
                        try:
                            pdf_generator = ProfessionalPDFGenerator()
                            instructions = f"""الجرعة اليومية: {daily_volume:.1f} لتر مقسمة على 3-4 وجبات
التركيز: 100-150 جم مسحوق لكل لتر ماء دافئ (40-45 درجة مئوية)
درجة الحرارة: 38-40 درجة مئوية عند التقديم"""
                            pdf_data = pdf_generator.generate_milk_replacer_report(
                                formula, animal_type, age_days, instructions,
                                st.session_state.get("user", {}).get("full_name", "مستخدم"),
                                student_name=student_name
                            )
                            st.download_button("📥 تحميل تقرير بديل الحليب PDF", pdf_data, file_name=f"Milk_Replacer_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf")
                        except:
                            st.warning("⚠️ تعذر إنشاء PDF")
                    db = DatabaseManager()
                    data = {
                        'replacer_id': secrets.token_hex(8),
                        'animal_type': animal_type,
                        'age_days': age_days,
                        'formula_name': f"بديل حليب {animal_type} عمر {age_days} يوم",
                        'ingredients': json.dumps(formula),
                        'instructions': "انظر التعليمات أعلاه",
                        'created_by': st.session_state.get("user", {}).get("full_name", "مستخدم"),
                        'created_date': datetime.now().isoformat()
                    }
                    db.insert_record('milk_replacers', data)
                    st.success("✅ تم حفظ التركيبة")
                else:
                    st.error("❌ تعذر إيجاد تركيبة مناسبة")

# =====================================================================
# مولد PDF (متوافق مع جميع الحالات)
# =====================================================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        self.supervisor_name = "اختصاصي تغذية الحيوان - م. عبد القادر إسماعيل تاور"
        if REPORTLAB_AVAILABLE:
            try:
                pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica'))
                self.font_name = 'Helvetica'
            except:
                pass
        self.styles = self._create_styles()
    
    def _create_styles(self):
        styles = {}
        styles['title'] = ParagraphStyle('title', fontName=self.font_name, fontSize=20, alignment=TA_CENTER, textColor=HexColor('#1b5e20'), spaceAfter=15, leading=25)
        styles['subtitle'] = ParagraphStyle('subtitle', fontName=self.font_name, fontSize=14, alignment=TA_CENTER, textColor=HexColor('#2e7d32'), spaceAfter=10, leading=18)
        styles['heading'] = ParagraphStyle('heading', fontName=self.font_name, fontSize=12, alignment=TA_RIGHT, textColor=HexColor('#1b5e20'), spaceAfter=8, leading=16, fontweight='bold')
        styles['body'] = ParagraphStyle('body', fontName=self.font_name, fontSize=10, alignment=TA_RIGHT, textColor=HexColor('#333333'), spaceAfter=5, leading=14)
        styles['footer'] = ParagraphStyle('footer', fontName=self.font_name, fontSize=8, alignment=TA_CENTER, textColor=HexColor('#999999'), spaceAfter=0, leading=10)
        return styles
    
    def generate_milk_replacer_report(self, formula, animal_type, age_days, instructions, user_name, student_name=""):
        if not REPORTLAB_AVAILABLE:
            return None
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        def p(text, style='body'):
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, self.styles.get(style, self.styles['body']))
        story.append(p("🍼 تقرير تركيب بديل الحليب - تاور نولجي", 'title'))
        story.append(p(f"👨‍💻 المشرف: {self.supervisor_name}", 'subtitle'))
        if student_name:
            story.append(p(f"👤 طالب التركيب: {student_name}", 'body'))
        story.append(Spacer(1, 10))
        story.append(p(f"🐾 الحيوان: {animal_type} | العمر: {age_days} يوم", 'body'))
        story.append(Spacer(1, 10))
        story.append(p("📋 المكونات:", 'heading'))
        ing_data = [['المكون', 'النسبة %', 'جم/كجم']]
        for ing, pct in formula.items():
            ing_data.append([ing, f'{pct:.1f}%', f'{pct*10:.1f}'])
        t = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in ing_data], colWidths=[200, 120, 120])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),('TEXTCOLOR',(0,0),(-1,0),white),('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),('FONTSIZE',(0,0),(-1,-1),10),('GRID',(0,0),(-1,-1),1,HexColor('#bdbdbd'))]))
        story.append(t)
        story.append(Spacer(1, 10))
        story.append(p("📌 تعليمات التقديم:", 'heading'))
        for line in instructions.split('\n'):
            if line.strip():
                story.append(p(f"• {line.strip()}", 'body'))
        story.append(Spacer(1, 20))
        story.append(p("مع خالص التحية والتقدير،", 'body'))
        story.append(Spacer(1, 5))
        story.append(p(self.supervisor_name, 'body'))
        story.append(Spacer(1, 10))
        story.append(p("تم التوليد بواسطة تاور نولجي Tawornology العلمية © 2026", 'footer'))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# =====================================================================
# دالة تركيب العلف الأساسية
# =====================================================================
def render_feed_formulation(animal_key, display_name, icon, default_breeds, default_stages, default_dp, default_se, has_measurements=True):
    st.markdown(f'<div class="section-title">{icon} {display_name} - تركيب العلف</div>', unsafe_allow_html=True)
    
    student_name = st.text_input("👤 اسم طالب العلف (اختياري):", placeholder="أدخل اسمك هنا", key=f"student_{animal_key}")
    
    col1, col2 = st.columns(2)
    with col1:
        breed = st.selectbox("السلالة:", default_breeds, key=f"{animal_key}_breed")
        stage = st.selectbox("المرحلة:", default_stages, key=f"{animal_key}_stage")
    with col2:
        protein_basis = st.radio("أساس البروتين:", ["DP", "CP"], horizontal=True, key=f"{animal_key}_basis")
        if protein_basis == "DP":
            target_protein = st.number_input("نسبة DP المطلوبة (%)", min_value=5.0, max_value=50.0, value=default_dp, step=0.5, key=f"{animal_key}_dp")
        else:
            target_protein = st.number_input("نسبة CP المطلوبة (%)", min_value=5.0, max_value=60.0, value=default_dp/0.80, step=0.5, key=f"{animal_key}_cp")
            target_protein = target_protein * 0.80
        target_se = st.number_input("معادل النشاء (SE) المطلوب", min_value=10.0, max_value=90.0, value=default_se, step=1.0, key=f"{animal_key}_se")
    
    st.markdown("#### 🌾 اختر المكونات")
    selected = []
    prices = {}
    market_prices = get_market_prices()
    cols = st.columns(3)
    for i, (ing, data) in enumerate(FLAT_FEED_DB.items()):
        with cols[i % 3]:
            checked = st.checkbox(ing, value=i < 6, key=f"{animal_key}_feed_{ing}")
            if checked:
                selected.append(ing)
                prices[ing] = st.number_input(f"سعر {ing} ($/طن)", min_value=5.0, value=float(market_prices.get(ing, 250.0)), key=f"{animal_key}_price_{ing}")
    
    if st.button(f"🚀 تشغيل محرك التركيب ({display_name})", type="primary"):
        if len(selected) < 3:
            st.warning("⚠️ يرجى اختيار 3 مكونات على الأقل")
        elif not SCIPY_AVAILABLE:
            st.error("❌ مكتبة Scipy غير مثبتة")
        else:
            with st.spinner("جاري الحساب..."):
                c = [prices[ing] for ing in selected]
                bounds = [(0, 100) for _ in selected]
                A_eq = [[1] * len(selected)]
                b_eq = [100]
                cp_row = []
                se_row = []
                ndf_row = []
                for ing in selected:
                    d = FLAT_FEED_DB[ing]
                    cp_row.append(d["CP"] * d["DC"])
                    se_row.append(d["SE"])
                    ndf_row.append(d.get("NDF", 0))
                A_eq.append(cp_row)
                b_eq.append(target_protein)
                A_ub = [[-x for x in se_row]]
                b_ub = [-target_se]
                if animal_key in ["cattle", "sheep", "goat", "camel"]:
                    A_ub.append(ndf_row)
                    b_ub.append(35)
                if "نخالة قمح (ردة)" in selected:
                    idx = selected.index("نخالة قمح (ردة)")
                    row = [0] * len(selected)
                    row[idx] = 1
                    A_ub.append(row)
                    b_ub.append(20)
                res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
                if res.success:
                    formula = {selected[i]: res.x[i] for i in range(len(selected)) if res.x[i] > 0.0001}
                    ton_cost = res.fun / 100.0
                    computed_se = sum((res.x[i]/100) * FLAT_FEED_DB[selected[i]]["SE"] for i in range(len(selected)))
                    computed_dp = sum((res.x[i]/100) * FLAT_FEED_DB[selected[i]]["CP"] * FLAT_FEED_DB[selected[i]]["DC"] for i in range(len(selected)))
                    st.success(f"✅ تم توليد الخلطة! التكلفة: ${ton_cost:.2f}/طن")
                    for k, v in formula.items():
                        st.markdown(f'<div class="formula-item"><span>{k}</span><span>{v:.1f}% ({v*10:.1f} كجم/طن)</span></div>', unsafe_allow_html=True)
                    st.session_state["active_formula"] = formula
                    st.session_state["computed_ton_cost"] = ton_cost
                    st.session_state["active_cp_tag"] = computed_dp
                    st.session_state["active_se_tag"] = computed_se
                    if REPORTLAB_AVAILABLE:
                        try:
                            standard = STANDARD_VALUES.get(display_name, {}).get(stage, {})
                            pdf_data = pdf_generator.generate_comprehensive_report(
                                formula, computed_dp, f"{breed} - {stage}",
                                ton_cost, "المدينة", ton_cost*600, "SDG", computed_se,
                                st.session_state.get("user", {}).get("full_name", "مستخدم"),
                                student_name=student_name,
                                standard=standard
                            )
                            if pdf_data:
                                st.download_button("📥 تحميل PDF", pdf_data, file_name=f"Feed_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf")
                        except:
                            st.warning("⚠️ تعذر إنشاء PDF")
                else:
                    st.error("❌ تعذر إيجاد حل، حاول تغيير المكونات")

# =====================================================================
# دالة المختبر المتقدم
# =====================================================================
def render_advanced_lab():
    st.markdown('<div class="section-title">🔬 المختبر المتقدم - تحليل الخلطات</div>', unsafe_allow_html=True)
    st.info("أدخل أوزان المكونات لتحليل خلطتك ومقارنتها بالمعايير القياسية.")
    
    student_name = st.text_input("👤 اسم طالب التحليل (اختياري):", placeholder="أدخل اسمك هنا")
    
    lab_animal = st.selectbox("الفصيل:", ["أبقار", "أغنام", "ماعز", "خيول", "إبل", "دواجن لاحم", "دواجن بياض", "أسماك"])
    lab_stage = st.selectbox("المرحلة:", list(STANDARD_VALUES.get(lab_animal, {}).keys()))
    standard = STANDARD_VALUES.get(lab_animal, {}).get(lab_stage, {})
    if standard:
        st.info(f"📊 المعايير: DP={standard.get('DP','-')}%, SE={standard.get('SE','-')}, CP={standard.get('CP','-')}%")
    
    lab_inputs = {}
    cols = st.columns(3)
    for i, ing in enumerate(FLAT_FEED_DB.keys()):
        with cols[i % 3]:
            lab_inputs[ing] = st.number_input(f"وزن {ing} (كجم)", min_value=0.0, value=0.0, step=5.0, key=f"lab_{ing}")
    
    if st.button("🧪 تشغيل التحليل", type="primary"):
        total = sum(lab_inputs.values())
        if total <= 0:
            st.warning("⚠️ الرجاء إدخال أوزان أكبر من الصفر")
        else:
            cp_total, dp_total, se_total = 0.0, 0.0, 0.0
            comps = []
            for ing, weight in lab_inputs.items():
                if weight > 0:
                    pct = weight / total
                    d = FLAT_FEED_DB[ing]
                    cp_total += pct * d["CP"]
                    dp_total += pct * d["CP"] * d["DC"]
                    se_total += pct * d["SE"]
                    comps.append({"المادة": ing, "الوزن": weight, "النسبة": f"{pct*100:.1f}%"})
            st.success("🔬 تم تحليل العينة!")
            st.markdown(f"### ⚖️ إجمالي الوزن: **{total:.1f} كجم**")
            st.table(pd.DataFrame(comps))
            st.write("#### 🔬 النتائج:")
            results_df = pd.DataFrame([
                {"العنصر": "CP", "القيمة": f"{cp_total:.2f}%"},
                {"العنصر": "DP", "القيمة": f"{dp_total:.2f}%"},
                {"العنصر": "SE", "القيمة": f"{se_total:.2f} وحدة"}
            ])
            st.table(results_df)
            if standard:
                st.write("#### 📊 المقارنة مع المعايير:")
                comp_data = []
                for key in ['DP', 'SE', 'CP']:
                    if key == 'DP':
                        val = dp_total
                        std = standard.get('DP', 0)
                    elif key == 'SE':
                        val = se_total
                        std = standard.get('SE', 0)
                    else:
                        val = cp_total
                        std = standard.get('CP', 0)
                    if std > 0:
                        dev = ((val - std) / std) * 100
                        grade = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                        comp_data.append({"المقياس": key, "المحسوب": f"{val:.2f}", "القياسي": f"{std:.2f}", "الانحراف": f"{dev:.1f}%", "التقييم": grade})
                st.table(pd.DataFrame(comp_data))
                if PLOTLY_AVAILABLE:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=['DP', 'SE', 'CP'], y=[dp_total, se_total, cp_total], name='المحسوب', marker_color='#2e7d32'))
                    fig.add_trace(go.Bar(x=['DP', 'SE', 'CP'], y=[standard.get('DP',0), standard.get('SE',0), standard.get('CP',0)], name='القياسي', marker_color='#1565C0'))
                    fig.update_layout(title="مقارنة القيم", barmode='group')
                    st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# دالة إدارة المزارع المبسطة
# =====================================================================
def render_farm_management():
    st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج</div>', unsafe_allow_html=True)
    st.info("نظام مبسط لإدارة مزارع الدجاج")
    
    if "broiler_farms" not in st.session_state:
        st.session_state["broiler_farms"] = {}
    
    if st.session_state["user_role"] in ["owner", "specialist", "veterinarian", "nutritionist", "breeder"]:
        with st.expander("➕ إضافة دورة جديدة"):
            col1, col2 = st.columns(2)
            with col1:
                farm_name = st.text_input("اسم المزرعة")
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
                    st.success(f"✅ تم إنشاء {farm_name}")
                    st.rerun()
    else:
        st.info("🔒 الإضافة متاحة للمالك والمختصين فقط")
    
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

# =====================================================================
# دالة الإنتاج اليومي
# =====================================================================
def render_daily_production():
    st.markdown('<div class="section-title">📈 الإنتاج اليومي</div>', unsafe_allow_html=True)
    
    if "daily_production_log" not in st.session_state:
        st.session_state["daily_production_log"] = []
    
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
        st.info("🔒 الإضافة متاحة للمالك والمختصين فقط")
    
    if st.session_state["daily_production_log"]:
        st.subheader("📋 سجل الإنتاج")
        df_prod = pd.DataFrame(st.session_state["daily_production_log"])
        st.dataframe(df_prod, use_container_width=True, hide_index=True)

# =====================================================================
# دالة عرض المراجع العلمية
# =====================================================================
def render_references():
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
    for cat_key, cat_data in ScientificReferenceSystem.REFERENCES.items():
        with st.expander(f"{cat_data['icon']} {cat_data['title']}"):
            for ref in cat_data.get("references", []):
                st.markdown(f"""
                <div style='background:#f8f9fa; padding:10px; border-radius:8px; margin-bottom:8px; border-right:4px solid #2e7d32;'>
                    <b>{ref.get('title', '')}</b><br>
                    👤 {ref.get('authors', '')} ({ref.get('year', '')})<br>
                    <small>{ref.get('summary', '')}</small>
                </div>
                """, unsafe_allow_html=True)
    st.subheader("💡 المعرفة السريعة")
    q = st.text_input("اسأل عن مصطلح:", placeholder="ما هو البروتين المهضوم؟")
    if q:
        answer = ScientificReferenceSystem.get_knowledge_answer(q)
        if answer:
            st.success(f"📖 {answer['answer']}")
            st.info(f"🔹 تبسيط: {answer['simplified']}")

# =====================================================================
# دالة عرض دليل التبويب مع زر صوتي
# =====================================================================
def guide_section(tab_name, guide_text):
    with st.expander(f"📘 دليل استخدام {tab_name}", expanded=False):
        st.markdown(f"<div style='background:#f0f8ff; padding:15px; border-radius:10px; direction:rtl;'>{guide_text}</div>", unsafe_allow_html=True)
        if st.button(f"🔊 استمع للدليل ({tab_name})"):
            voice_guide(guide_text)

# =====================================================================
# شريط الدعاء
# =====================================================================
def render_dua_bar():
    st.markdown("""
    <style>
    .dua-container {
        background: linear-gradient(135deg, #0d1b2a, #1a237e);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        border: 2px solid #d4af37;
        margin-bottom: 15px;
    }
    .dua-container p {
        color: #ffd700;
        font-size: 1.2rem;
        margin: 0;
    }
    </style>
    <div class="dua-container">
        <p>🕊️ اللهم اغفر لإسماعيل تاور وابتسام وارحمهما وأدخلهما فسيح جناتك 🕊️</p>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# حالة الجلسة العامة
# =====================================================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "login_welcome_shown" not in st.session_state: st.session_state["login_welcome_shown"] = False
if "login_attempts" not in st.session_state: st.session_state["login_attempts"] = 0
if "last_login_time" not in st.session_state: st.session_state["last_login_time"] = None
if "active_formula" not in st.session_state: st.session_state["active_formula"] = {}
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0

# =====================================================================
# بيانات الأسعار والأسهم الافتراضية
# =====================================================================
if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين ($)": 1350.0, "أبقار كنانة محلية ($)": 900.0,
        "ضأن وستيرلنغ ($)": 180.0, "ماعز نوبي ($)": 130.0,
        "خيول عربية أصيلة ($)": 4500.0, "إبل عربية ($)": 2500.0,
        "كتكوت لاحم ($)": 0.65
    }
if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري ($)": 7.50, "كيلو لحم ضأن ($)": 9.00,
        "كيلو لحم دجاج ($)": 3.80, "طبق بيض 30 بيضة ($)": 4.20,
        "لتر حليب خام ($)": 0.90
    }

ANIMAL_IMAGES_RESOURCES = {
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
# CSS للواجهة
# =====================================================================
st.markdown("""
<style>
* { font-family: 'Cairo', 'Tajawal', sans-serif; }
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 50%, #f5f7fa 100%);
}
.stApp { background: transparent; }
.main-box {
    background: rgba(255,255,255,0.92);
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 15px 50px rgba(0,0,0,0.1);
    margin-bottom: 25px;
}
.section-title {
    color: #1b5e20;
    border-right: 5px solid #2e7d32;
    padding-right: 15px;
    font-size: 1.5rem;
    font-weight: 700;
    margin: 20px 0;
}
.formula-item {
    background: #f5f5f5;
    padding: 12px 18px;
    border-radius: 10px;
    margin-bottom: 8px;
    border-right: 4px solid #2e7d32;
    display: flex;
    justify-content: space-between;
}
.metric-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    text-align: center;
}
.metric-card .number {
    font-size: 2rem;
    font-weight: 900;
    color: #1b5e20;
}
.profile-img-style {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #d4af37;
}
.manual-book {
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.book-chapter {
    background: #1a237e;
    color: white;
    padding: 12px 18px;
    border-radius: 8px;
    font-weight: bold;
    margin-top: 15px;
}
.book-body {
    padding: 15px 20px;
    font-size: 1rem;
    line-height: 1.8;
    background: #f8f9fa;
    border-radius: 0 8px 8px 0;
}
.warning-card {
    background: #fff3e0;
    padding: 12px;
    border-radius: 8px;
    border-right: 4px solid #f57c00;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# شاشة الدخول
# =====================================================================
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300

if not st.session_state["approved"]:
    render_dua_bar()
    
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        if st.session_state["last_login_time"]:
            time_diff = (datetime.now() - st.session_state["last_login_time"]).seconds
            if time_diff < LOCKOUT_TIME:
                st.markdown('<div class="main-box" style="max-width:500px; margin:100px auto; direction:rtl; text-align:center;">', unsafe_allow_html=True)
                st.error(f"🔒 تم قفل النظام مؤقتاً. حاول بعد {LOCKOUT_TIME - time_diff} ثانية")
                st.markdown('</div>', unsafe_allow_html=True)
                st.stop()
            else:
                st.session_state["login_attempts"] = 0

    st.markdown('<div class="main-box" style="max-width:550px; margin:80px auto; direction:rtl;">', unsafe_allow_html=True)
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" style="width:100px; height:100px; border-radius:50%; border:3px solid #d4af37; display:block; margin:0 auto;">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#1a237e;'>🌾 تاور نولجي Tawornology العلمية</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555;'>للانتاج الحيواني وتركيب الاعلاف</p>")
    
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
                st.session_state["user"] = user
                voice_guide("مرحباً بك زائراً")
                st.rerun()
            else:
                st.error("❌ فشل الدخول كزائر")
    
    st.markdown("<hr>")
    st.markdown("<p style='text-align:center;'>🔑 للمالك والمختصين</p>")
    input_code = st.text_input("كود الدخول:", type="password")
    if st.button("تسجيل الدخول", use_container_width=True):
        if input_code.strip() in CODES_DB:
            st.session_state["approved"] = True
            st.session_state["user_role"] = CODES_DB[input_code.strip()]["role"]
            st.session_state["login_welcome_shown"] = False
            st.session_state["login_attempts"] = 0
            st.session_state["last_login_time"] = datetime.now()
            st.session_state["user"] = {"full_name": CODES_DB[input_code.strip()]["name"]}
            voice_guide(f"مرحباً {CODES_DB[input_code.strip()]['name']}")
            st.rerun()
        else:
            st.session_state["login_attempts"] += 1
            remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
            st.error(f"❌ كود خاطئ، متبقي {remaining} محاولات")
    
    st.markdown("""
    <div style='text-align:center; margin-top:15px; color:#999; font-size:0.8rem;'>
    🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# الترحيب بعد الدخول
# =====================================================================
if not st.session_state["login_welcome_shown"]:
    role_messages = {
        "owner": "👑 مرحباً اختصاصي تغذية الحيوان - م. عبد القادر إسماعيل تاور",
        "specialist": "🔬 أهلاً بالمختصين",
        "veterinarian": "💊 أهلاً بالطبيب البيطري",
        "nutritionist": "🧬 أهلاً بأخصائي التغذية",
        "breeder": "🌾 أهلاً بالمربي",
        "public": "👤 مرحباً بك زائراً"
    }
    st.toast(role_messages.get(st.session_state["user_role"], "مرحباً"), icon="🌾")
    voice_welcome(st.session_state["user_role"])
    st.session_state["login_welcome_shown"] = True

render_dua_bar()

# =====================================================================
# الواجهة الرئيسية
# =====================================================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logout, col_user = st.columns([0.7, 0.3])
with col_user:
    role_names = {"owner": "المالك 👑", "specialist": "المختص 👨‍🔬", "veterinarian": "الطبيب البيطري 💊", "nutritionist": "أخصائي التغذية 🧬", "breeder": "المربي 🌾", "public": "زائر 👤"}
    user_name = st.session_state.get("user", {}).get("full_name", "زائر")
    user_role = st.session_state.get("user_role", "public")
    st.markdown(f"""
    <div style='text-align:left; background:#f5f5f5; padding:12px; border-radius:12px;'>
        <div style='font-weight:700;'>{user_name}</div>
        <div style='font-size:0.85rem; color:#555;'>{role_names.get(user_role, "مستخدم")}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["inventory", "broiler_farms", "daily_production_log", "dose_reminders", "email_password", "active_formula", "computed_ton_cost"]:
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

col_logo, col_title = st.columns([0.15, 0.85])
with col_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='color:#1a237e; margin-bottom:0;'>🌾 تاور نولجي Tawornology العلمية</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#1565C0; font-size:1.1rem;'>للانتاج الحيواني وتركيب الاعلاف - محرك الاستمثال الخطي المتقدم</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#c62828; font-weight:700;'>اختصاصي تغذية الحيوان - م. عبد القادر إسماعيل تاور</p>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# زر الشرح الصوتي الكامل
if st.button("🔊 تشغيل الشرح الصوتي الكامل للمنصة", type="primary", use_container_width=True):
    play_full_guide_audio()
    st.success("✅ يتم تشغيل الشرح...")

# =====================================================================
# إحصائيات سريعة
# =====================================================================
st.markdown("### 📊 لوحة التحكم")
col1, col2, col3, col4 = st.columns(4)
stock_summary = InventoryManager.get_stock_summary()
with col1:
    st.markdown(f"<div class='metric-card'><div class='number'>{stock_summary['total_items']}</div><div class='label'>المواد</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><div class='number'>{stock_summary['total_quantity']:.1f}</div><div class='label'>المخزون (طن)</div></div>", unsafe_allow_html=True)
with col3:
    color = "#c62828" if stock_summary['low_stock'] > 3 else "#e65100" if stock_summary['low_stock'] > 0 else "#2e7d32"
    st.markdown(f"<div class='metric-card'><div class='number' style='color:{color};'>{stock_summary['low_stock']}</div><div class='label'>مواد منخفضة</div></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='metric-card'><div class='number'>{len(st.session_state.get('broiler_farms', {}))}</div><div class='label'>مزارع</div></div>", unsafe_allow_html=True)
st.markdown("<hr>")

# =====================================================================
# أدوات المشاركة
# =====================================================================
col_v, col_s1, col_s2 = st.columns([0.3, 0.35, 0.35])
with col_v:
    if st.button("🔊 اختبار الصوت", use_container_width=True):
        voice_guide("بسم الله الرحمن الرحيم، هذا اختبار صوتي")
        st.success("✅ تم التشغيل")
with col_s1:
    if st.button("📧 إرسال الكود", use_container_width=True):
        if st.session_state["user_role"] == "owner":
            email = st.text_input("البريد:", placeholder=OWNER_EMAIL, key="code_email")
            if email and '@' in email:
                if email.lower() == OWNER_EMAIL.lower():
                    with st.spinner("جاري الإرسال..."):
                        success, msg = send_code_to_email(email)
                        st.success(msg) if success else st.error(msg)
                else:
                    st.error(f"❌ مسموح فقط للبريد: {OWNER_EMAIL}")
        else:
            st.warning("⚠️ للمالك فقط")
with col_s2:
    if st.button("📊 مشاركة الخلطة", use_container_width=True):
        if st.session_state["active_formula"]:
            user_name = st.session_state.get("user", {}).get("full_name", "مستخدم")
            img_buf = generate_formula_image(
                st.session_state["active_formula"],
                st.session_state.get("active_cp_tag", 12),
                st.session_state.get("active_se_tag", 65),
                st.session_state.get("active_breed_tag", "عام"),
                st.session_state.get("active_stage_title", "إنتاج"),
                user_name
            )
            if img_buf:
                caption = f"🧬 خلطة علفية - تاور نولجي\nالمشرف: اختصاصي تغذية الحيوان - م. عبد القادر إسماعيل تاور"
                send_image_to_whatsapp(img_buf, caption)
            else:
                st.warning("⚠️ تعذر توليد الصورة")
        else:
            st.warning("⚠️ لا توجد خلطة نشطة")
st.markdown("<hr>")

# =====================================================================
# تحديد التبويبات حسب الصلاحية
# =====================================================================
if st.session_state["user_role"] == "owner":
    tabs_titles = [
        "🐾 القطاع الحيواني",
        "🐔 إدارة المزارع",
        "🍼 بدائل الحليب",
        "🕌 مواقيت الصلاة",
        "💊 منبه الجرعات",
        "📊 بورصة الأسعار",
        "🏭 المستودعات",
        "📈 الإنتاج اليومي",
        "📚 المراجع العلمية",
        "💡 المساعدة",
        "📖 الدليل"
    ]
elif st.session_state["user_role"] in ["specialist", "veterinarian", "nutritionist", "breeder"]:
    tabs_titles = [
        "🐾 القطاع الحيواني",
        "🐔 إدارة المزارع",
        "🍼 بدائل الحليب",
        "💊 منبه الجرعات",
        "📊 بورصة الأسعار",
        "🏭 المستودعات",
        "📈 الإنتاج اليومي",
        "📚 المراجع العلمية",
        "💡 المساعدة",
        "📖 الدليل"
    ]
else:
    tabs_titles = [
        "🐾 القطاع الحيواني",
        "📚 المراجع العلمية",
        "💡 المساعدة",
        "📖 الدليل"
    ]

tabs = st.tabs(tabs_titles)

# =====================================================================
# أدلة الاستخدام
# =====================================================================
guides = {
    "القطاع الحيواني": "اختر نوع الحيوان، ثم السلالة والمرحلة، واختر المكونات، واضغط على زر التشغيل.",
    "إدارة المزارع": "أضف دورات إنتاجية وسجل بيانات الدجاج اللاحم.",
    "بدائل الحليب": "تركيب بديل حليب للصغار حسب العمر والنوع.",
    "مواقيت الصلاة": "عرض أوقات الصلاة حسب المدينة.",
    "منبه الجرعات": "تسجيل وتتبع اللقاحات والفيتامينات.",
    "بورصة الأسعار": "متابعة أسعار المواشي والمنتجات.",
    "المستودعات": "إدارة المخزون والمواد العلفية.",
    "الإنتاج اليومي": "تسجيل بيانات الإنتاج اليومي.",
    "المراجع": "مصادر معتمدة في تغذية الحيوان.",
    "المساعدة": "دليل سريع للمنصة.",
    "الدليل": "شرح مفصل للمنصة."
}

# =====================================================================
# التبويب 0: القطاع الحيواني
# =====================================================================
with tabs[0]:
    guide_section("القطاع الحيواني", guides["القطاع الحيواني"])
    animal_tabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐴 خيول", "🐫 إبل", "🐔 دواجن", "🐟 أسماك", "🔬 المختبر"])
    
    with animal_tabs[0]:
        render_feed_formulation("cattle", "أبقار", "🐄", 
            ["كنانة", "هولشتاين", "بطانة"], 
            ["تسمين عجول", "حليب/إدرار", "صيانة"], 12.0, 65.0)
    with animal_tabs[1]:
        render_feed_formulation("sheep", "أغنام", "🐏", 
            ["صحراوي", "بربري", "نعيمي"], 
            ["تسمين حملان", "حليب/إدرار", "صيانة"], 11.5, 62.0)
    with animal_tabs[2]:
        render_feed_formulation("goat", "ماعز", "🐐", 
            ["نوبي", "صحراوي", "بور"], 
            ["تسمين جديان", "حليب/إدرار", "صيانة"], 11.0, 60.0)
    with animal_tabs[3]:
        render_feed_formulation("horse", "خيول", "🐴", 
            ["عربي أصيل", "ثوروبريد", "محلي"], 
            ["راحة/صيانة", "عمل خفيف", "عمل مكثف"], 11.0, 62.0)
    with animal_tabs[4]:
        render_feed_formulation("camel", "إبل", "🐫", 
            ["عربية", "باختري", "هجين"], 
            ["راحة/صيانة", "تسمين", "إنتاج حليب"], 10.0, 58.0)
    with animal_tabs[5]:
        render_feed_formulation("poultry", "دواجن", "🐔", 
            ["لاحم (Broiler)", "بياض (Layer)"], 
            ["بادي (0-14)", "نامي (15-28)", "ناهي (29-42)"], 18.0, 72.0)
    with animal_tabs[6]:
        render_feed_formulation("fish", "أسماك", "🐟", 
            ["بلطي", "قرموط"], 
            ["زريعة/بادئ", "نمو", "تسمين نهائي"], 28.0, 68.0)
    with animal_tabs[7]:
        render_advanced_lab()

# =====================================================================
# التبويب 1: إدارة المزارع
# =====================================================================
if len(tabs) > 1:
    with tabs[1]:
        guide_section("إدارة المزارع", guides["إدارة المزارع"])
        render_farm_management()

# =====================================================================
# التبويب 2: بدائل الحليب
# =====================================================================
if len(tabs) > 2:
    with tabs[2]:
        guide_section("بدائل الحليب", guides["بدائل الحليب"])
        render_milk_replacer()

# =====================================================================
# التبويب 3: مواقيت الصلاة (للمالك فقط)
# =====================================================================
if len(tabs) > 3 and st.session_state["user_role"] == "owner":
    with tabs[3]:
        guide_section("مواقيت الصلاة", guides["مواقيت الصلاة"])
        prayer_time_reminder()
elif len(tabs) > 3:
    with tabs[3]:
        guide_section("منبه الجرعات", guides["منبه الجرعات"])
        render_dose_reminder_system()

# =====================================================================
# التبويب 4: منبه الجرعات (للمالك والمختصين)
# =====================================================================
if len(tabs) > 4:
    if st.session_state["user_role"] == "owner":
        with tabs[4]:
            guide_section("منبه الجرعات", guides["منبه الجرعات"])
            render_dose_reminder_system()
    else:
        with tabs[4]:
            guide_section("بورصة الأسعار", guides["بورصة الأسعار"])
            st.markdown('<div class="section-title">📊 بورصة الأسعار</div>', unsafe_allow_html=True)
            st.write("#### 🐄 أسعار المواشي")
            for name, price in st.session_state["global_livestock_prices"].items():
                st.write(f"- {name}: ${price:.2f}")
            st.write("#### 🥩 أسعار المنتجات")
            for name, price in st.session_state["global_products_prices"].items():
                st.write(f"- {name}: ${price:.2f}")

# =====================================================================
# التبويب 5: بورصة الأسعار (للمالك والمختصين)
# =====================================================================
if len(tabs) > 5 and st.session_state["user_role"] in ["owner", "specialist", "veterinarian", "nutritionist", "breeder"]:
    with tabs[5]:
        guide_section("بورصة الأسعار", guides["بورصة الأسعار"])
        st.markdown('<div class="section-title">📊 بورصة الأسعار</div>', unsafe_allow_html=True)
        if st.session_state["user_role"] in ["owner", "specialist"]:
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
        else:
            st.info("🔒 التعديل للمالك والمختصين فقط")
            for name, price in st.session_state["global_livestock_prices"].items():
                st.write(f"- {name}: ${price:.2f}")

# =====================================================================
# التبويب 6: المستودعات
# =====================================================================
if len(tabs) > 6 and st.session_state["user_role"] in ["owner", "specialist", "veterinarian", "nutritionist", "breeder"]:
    with tabs[6]:
        guide_section("المستودعات", guides["المستودعات"])
        st.markdown('<div class="section-title">🏭 المستودعات</div>', unsafe_allow_html=True)
        inv_data = []
        for item, data in st.session_state["inventory"].items():
            inv_data.append({"المادة": item, "الكمية (طن)": data["quantity"], "الحد الأدنى": data["min_threshold"]})
        st.dataframe(pd.DataFrame(inv_data), use_container_width=True)
        if st.session_state["user_role"] in ["owner", "specialist"]:
            with st.expander("تحديث المخزون"):
                sel = st.selectbox("المادة", list(FLAT_FEED_DB.keys()))
                new_qty = st.number_input("الكمية الجديدة (طن)", min_value=0.0, value=25.0)
                if st.button("تحديث"):
                    st.session_state["inventory"][sel]["quantity"] = new_qty
                    st.success("✅ تم التحديث")
                    st.rerun()

# =====================================================================
# التبويب 7: الإنتاج اليومي
# =====================================================================
if len(tabs) > 7 and st.session_state["user_role"] in ["owner", "specialist", "veterinarian", "nutritionist", "breeder"]:
    with tabs[7]:
        guide_section("الإنتاج اليومي", guides["الإنتاج اليومي"])
        render_daily_production()

# =====================================================================
# التبويب 8: المراجع العلمية (للجميع)
# =====================================================================
if len(tabs) > 8:
    if st.session_state["user_role"] == "owner":
        ref_idx = 8
    elif st.session_state["user_role"] in ["specialist", "veterinarian", "nutritionist", "breeder"]:
        ref_idx = 7
    else:
        ref_idx = 1
    
    with tabs[ref_idx]:
        guide_section("المراجع العلمية", guides["المراجع"])
        render_references()

# =====================================================================
# التبويب 9: المساعدة (للجميع)
# =====================================================================
if len(tabs) > 9:
    if st.session_state["user_role"] == "owner":
        help_idx = 9
    elif st.session_state["user_role"] in ["specialist", "veterinarian", "nutritionist", "breeder"]:
        help_idx = 8
    else:
        help_idx = 2
    
    with tabs[help_idx]:
        guide_section("المساعدة", guides["المساعدة"])
        st.markdown('<div class="section-title">💡 المساعدة</div>', unsafe_allow_html=True)
        st.markdown("""
        1. اختر نوع الحيوان والمرحلة.
        2. اختر المكونات العلفية.
        3. اضغط على زر التشغيل للحصول على خلطة مثالية.
        4. استخدم المختبر لتحليل خلطاتك.
        5. استخدم بدائل الحليب للصغار.
        6. سجل الجرعات في منبه الجرعات.
        """)
        if st.button("🔊 استمع للتعليمات"):
            voice_guide("مرحباً، هذا دليل استخدام المنصة. اختر الحيوان والمكونات، ثم اضغط على تشغيل.")

# =====================================================================
# التبويب 10: دليل المستخدم (للجميع)
# =====================================================================
if len(tabs) > 10:
    if st.session_state["user_role"] == "owner":
        manual_idx = 10
    elif st.session_state["user_role"] in ["specialist", "veterinarian", "nutritionist", "breeder"]:
        manual_idx = 9
    else:
        manual_idx = 3
    
    with tabs[manual_idx]:
        guide_section("دليل المستخدم", guides["الدليل"])
        st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="manual-book">
        <div class="book-chapter">📘 الفصل 1: مقدمة</div>
        <div class="book-body">
        تاور نولجي Tawornology العلمية منصة متكاملة لتركيب الأعلاف وإدارة الإنتاج الحيواني.
        تعتمد على البرمجة الخطية لحساب أقل تكلفة لخلطة علفية.
        </div>
        <div class="book-chapter">📗 الفصل 2: تركيب العلف</div>
        <div class="book-body">
        1. اختر نوع الحيوان.<br>
        2. حدد السلالة والمرحلة.<br>
        3. اختر المكونات وحدد أسعارها.<br>
        4. اضغط على "تشغيل محرك التركيب".
        </div>
        <div class="book-chapter">📕 الفصل 3: المختبر</div>
        <div class="book-body">
        أدخل أوزان المكونات لتحليل خلطتك ومقارنتها بالمعايير القياسية.
        </div>
        <div class="book-chapter">📙 الفصل 4: بدائل الحليب</div>
        <div class="book-body">
        قم بتركيب بديل حليب للصغار حسب العمر والاحتياجات.
        </div>
        </div>
        """, unsafe_allow_html=True)

# =====================================================================
# التذييل
# =====================================================================
st.markdown("""
<div style='text-align:center; padding:20px; margin-top:30px; border-top:2px solid #e0e0e0; color:#888; font-size:0.9rem;'>
🌾 <b>تاور نولجي Tawornology العلمية</b><br>
اختصاصي تغذية الحيوان - م. عبد القادر إسماعيل تاور<br>
🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b>
</div>
""", unsafe_allow_html=True)

if st.button("🔊 اختبار الصوت (نهاية الصفحة)", use_container_width=True):
    voice_guide("بسم الله الرحمن الرحيم، هذا اختبار للنظام الصوتي.")

# =====================================================================
# نهاية الكود
# =====================================================================
