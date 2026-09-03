# ============================================================================
# تاور نولجي Tawornology العلمية - الإصدار المتكامل الشامل 18.0
# ============================================================================
# 🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله
# 🕊️ اللهم اجعل قبرهما روضة من رياض الجنة واجمعنا بهما في الفردوس الأعلى
# ============================================================================
# جميع المشاكل السابقة تم حلها:
# 1. تداخل الأصوات - تم إلغاء الصوت السابق
# 2. PDF يعمل على جميع الأجهزة مع خط عربي مضمّن
# 3. تبويبات الزائر تحتوي على محتوى كامل
# 4. المختبر يصدر PDF كامل مع جميع البيانات
# 5. إرسال الكود يعمل مع كلمة المرور المحفوظة
# 6. التركيب وفق المعايير الدولية NRC/INRA/FAO
# 7. دعم كامل لإنتاج الحليب
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
from reportlab.lib.colors import HexColor, black, white, grey, blue, red, green, orange, purple, teal, gold
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
# إعدادات البريد الإلكتروني (مع كلمة المرور المحفوظة)
# =====================================================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"

# كلمة المرور المحفوظة
DEFAULT_EMAIL_PASSWORD = "kccq khzn enlx bpcy"

if "email_password" not in st.session_state:
    try:
        st.session_state["email_password"] = st.secrets["email"]["password"]
    except:
        st.session_state["email_password"] = DEFAULT_EMAIL_PASSWORD

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
# تحميل الخط العربي للـ PDF
# =====================================================================
def download_arabic_font():
    font_path = "Amiri-Regular.ttf"
    if os.path.exists(font_path):
        return font_path
    try:
        import requests
        url = "https://raw.githubusercontent.com/aliftype/amiri/master/fonts/Amiri-Regular.ttf"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            with open(font_path, "wb") as f:
                f.write(response.content)
            return font_path
    except:
        pass
    system_fonts = [
        "/usr/share/fonts/truetype/arabic/Amiri-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/tahoma.ttf"
    ]
    for f in system_fonts:
        if os.path.exists(f):
            return f
    return None

# =====================================================================
# دوال الصوت (مع إلغاء الصوت السابق)
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

def voice_guide(message, lang="ar"):
    """تشغيل صوت مع إلغاء أي صوت سابق"""
    if not GTTS_AVAILABLE or not message:
        return
    
    # إلغاء أي صوت سابق
    st.components.v1.html(
        """
        <script>
        (function() {
            try {
                var audios = document.querySelectorAll('audio');
                audios.forEach(function(audio) {
                    audio.pause();
                    audio.currentTime = 0;
                    audio.remove();
                });
            } catch(e) {
                console.warn('خطأ في إلغاء الصوت:', e);
            }
        })();
        </script>
        """,
        height=0
    )
    time.sleep(0.1)
    
    audio_b64 = text_to_speech_base64(message, lang)
    if audio_b64:
        play_audio_b64(audio_b64)

def voice_guide_sequential(messages, lang="ar", delay_between=1.2):
    if not GTTS_AVAILABLE:
        st.warning("⚠️ الصوت غير متاح")
        return
    for i, msg in enumerate(messages):
        if msg:
            voice_guide(msg, lang)
            if i < len(messages) - 1:
                time.sleep(delay_between)

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
# دوال إرسال الكود (مع كلمة المرور المحفوظة)
# =====================================================================
def send_code_to_email(receiver_email):
    if receiver_email.strip().lower() != OWNER_EMAIL.strip().lower():
        return False, "❌ عذراً، الإرسال مسموح فقط للبريد: " + OWNER_EMAIL
    
    if not st.session_state.get("email_password"):
        st.session_state["email_password"] = DEFAULT_EMAIL_PASSWORD
    
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

عدد الأسطر: ~4500 سطر
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
        return False, f"❌ فشل الإرسال: {str(e)}. تأكد من كلمة المرور."

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
# نظام إدارة المزارع (مبسط)
# =====================================================================
class FarmManagementSystem:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_farm(self, farm_name: str, farm_type: str, owner_name: str, 
                   owner_phone: str, location: str = "", area: float = 0.0) -> str:
        farm_id = secrets.token_hex(16)
        data = {
            'farm_id': farm_id,
            'farm_name': farm_name,
            'farm_type': farm_type,
            'owner_name': owner_name,
            'owner_phone': owner_phone,
            'location': location,
            'area': area,
            'created_date': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        self.db.insert_record('farms', data)
        return farm_id
    
    def create_production_cycle(self, farm_id: str, cycle_type: str, 
                               initial_count: int, breed: str,
                               target_weight: float = 0.0, 
                               target_age: int = 0) -> str:
        cycle_id = secrets.token_hex(16)
        data = {
            'cycle_id': cycle_id,
            'farm_id': farm_id,
            'cycle_type': cycle_type,
            'start_date': datetime.now().isoformat(),
            'end_date': '',
            'initial_count': initial_count,
            'breed': breed,
            'target_weight': target_weight,
            'target_age': target_age,
            'status': 'active',
            'notes': ''
        }
        self.db.insert_record('production_cycles', data)
        return cycle_id
    
    def add_daily_record(self, cycle_id: str, record_data: dict) -> str:
        record_id = secrets.token_hex(16)
        live_birds = record_data.get('live_birds', 0)
        avg_weight = record_data.get('avg_weight', 0)
        feed_consumed = record_data.get('feed_consumed', 0)
        dead_count = record_data.get('dead_count', 0)
        initial_count = record_data.get('initial_count', live_birds + dead_count)
        total_gain = live_birds * avg_weight
        feed_conversion = feed_consumed / total_gain if total_gain > 0 else 0
        mortality_rate = (dead_count / initial_count) * 100 if initial_count > 0 else 0
        data = {
            'record_id': record_id,
            'cycle_id': cycle_id,
            'record_date': datetime.now().isoformat(),
            'age_days': record_data.get('age_days', 0),
            'live_birds': live_birds,
            'avg_weight': avg_weight,
            'min_weight': record_data.get('min_weight', avg_weight * 0.9),
            'max_weight': record_data.get('max_weight', avg_weight * 1.1),
            'feed_consumed': feed_consumed,
            'water_consumed': record_data.get('water_consumed', 0),
            'dead_count': dead_count,
            'culled_count': record_data.get('culled_count', 0),
            'temperature': record_data.get('temperature', 0),
            'humidity': record_data.get('humidity', 0),
            'ventilation_status': record_data.get('ventilation_status', 'جيدة'),
            'litter_quality': record_data.get('litter_quality', 'جيدة'),
            'feed_conversion': feed_conversion,
            'mortality_rate': mortality_rate,
            'notes': record_data.get('notes', '')
        }
        self.db.insert_record('daily_records', data)
        self._create_performance_comparison(cycle_id, record_data)
        return record_id
    
    def _create_performance_comparison(self, cycle_id: str, record_data: dict):
        age_days = record_data.get('age_days', 0)
        avg_weight = record_data.get('avg_weight', 0)
        feed_conversion = record_data.get('feed_conversion', 0)
        mortality_rate = record_data.get('mortality_rate', 0)
        standard_weights = {1: 0.045, 7: 0.180, 14: 0.450, 21: 0.850, 28: 1.350, 35: 1.950, 42: 2.550}
        standard_fcr = {1: 1.0, 7: 1.2, 14: 1.4, 21: 1.6, 28: 1.7, 35: 1.8, 42: 1.9}
        standard_mortality = {1: 0.5, 7: 0.8, 14: 1.0, 21: 1.2, 28: 1.5, 35: 1.8, 42: 2.0}
        ages = sorted(standard_weights.keys())
        closest_age = min(ages, key=lambda x: abs(x - age_days))
        std_weight = standard_weights.get(closest_age, avg_weight)
        std_fcr = standard_fcr.get(closest_age, feed_conversion)
        std_mortality = standard_mortality.get(closest_age, mortality_rate)
        metrics = [
            ('وزن الجسم', avg_weight, std_weight, ((avg_weight - std_weight) / std_weight) * 100 if std_weight > 0 else 0),
            ('معامل التحويل', feed_conversion, std_fcr, ((feed_conversion - std_fcr) / std_fcr) * 100 if std_fcr > 0 else 0),
            ('نسبة النفوق', mortality_rate, std_mortality, ((mortality_rate - std_mortality) / std_mortality) * 100 if std_mortality > 0 else 0)
        ]
        for metric_name, farm_val, std_val, deviation in metrics:
            status = 'ممتاز' if abs(deviation) < 5 else ('جيد' if abs(deviation) < 10 else 'بحاجة إلى تحسين')
            comp_id = secrets.token_hex(16)
            comp_data = {
                'comparison_id': comp_id,
                'cycle_id': cycle_id,
                'comparison_date': datetime.now().isoformat(),
                'metric_type': metric_name,
                'farm_value': farm_val,
                'standard_value': std_val,
                'deviation': deviation,
                'status': status
            }
            self.db.insert_record('performance_comparisons', comp_data)
    
    def get_farm_data(self, farm_id: str) -> dict:
        farm_data = self.db.get_records('farms', {'farm_id': farm_id})
        if not farm_data:
            return None
        farm = farm_data[0]
        cycles = self.db.get_records('production_cycles', {'farm_id': farm_id})
        result = {
            'farm_id': farm[0],
            'farm_name': farm[1],
            'farm_type': farm[2],
            'owner_name': farm[3],
            'owner_phone': farm[4],
            'location': farm[5],
            'area': farm[6],
            'created_date': farm[7],
            'cycles': []
        }
        for cycle in cycles:
            cycle_id = cycle[0]
            daily_records = self.db.get_records('daily_records', {'cycle_id': cycle_id})
            comparisons = self.db.get_records('performance_comparisons', {'cycle_id': cycle_id})
            result['cycles'].append({
                'cycle_id': cycle_id,
                'cycle_type': cycle[2],
                'start_date': cycle[3],
                'end_date': cycle[4],
                'initial_count': cycle[5],
                'breed': cycle[6],
                'target_weight': cycle[7],
                'target_age': cycle[8],
                'status': cycle[9],
                'daily_records': daily_records,
                'comparisons': comparisons
            })
        return result
    
    def get_performance_summary(self, cycle_id: str) -> dict:
        records = self.db.get_records('daily_records', {'cycle_id': cycle_id})
        if not records:
            return None
        latest_record = records[-1] if records else None
        first_record = records[0] if records else None
        total_dead = sum(r[11] for r in records)
        total_culled = sum(r[12] for r in records)
        initial_count = first_record[0] if first_record else 0
        summary = {
            'total_days': latest_record[3] if latest_record else 0,
            'final_weight': latest_record[5] if latest_record else 0,
            'total_feed': sum(r[9] for r in records),
            'total_dead': total_dead,
            'total_culled': total_culled,
            'mortality_rate': (total_dead / initial_count * 100) if initial_count > 0 else 0,
            'final_livability': ((initial_count - total_dead - total_culled) / initial_count * 100) if initial_count > 0 else 0,
            'avg_fcr': sum(r[15] for r in records) / len(records) if records else 0
        }
        livability = summary['final_livability']
        final_weight = summary['final_weight']
        total_days = summary['total_days']
        avg_fcr = summary['avg_fcr']
        epef = (livability * final_weight) / (total_days * avg_fcr) * 100 if total_days > 0 and avg_fcr > 0 else 0
        summary['epef'] = epef
        return summary

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
# نظام المراجع العلمية
# =====================================================================
class ScientificReferenceSystem:
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان",
            "icon": "📚",
            "references": [
                {"id": "REF001", "authors": "McDonald, P., Edwards, R.A., Greenhalgh, J.F.D., Morgan, C.A.",
                 "year": 2011, "title": "Animal Nutrition", "publisher": "Pearson Education",
                 "edition": "7th Edition", "summary": "المرجع الأساسي في تغذية الحيوان."}
            ]
        },
        "nrc": {
            "title": "المعايير القياسية NRC",
            "icon": "📊",
            "references": [
                {"id": "NRC001", "authors": "NRC (National Research Council)",
                 "year": 2001, "title": "Nutrient Requirements of Dairy Cattle",
                 "publisher": "National Academies Press", "summary": "المرجع الرسمي لمتطلبات أبقار الحليب."},
                {"id": "NRC002", "authors": "NRC (National Research Council)",
                 "year": 2007, "title": "Nutrient Requirements of Small Ruminants",
                 "publisher": "National Academies Press", "summary": "المرجع الرسمي لمتطلبات الأغنام والماعز."},
                {"id": "NRC003", "authors": "NRC (National Research Council)",
                 "year": 2007, "title": "Nutrient Requirements of Horses",
                 "publisher": "National Academies Press", "summary": "المرجع الرسمي لمتطلبات الخيول."},
                {"id": "NRC004", "authors": "NRC (National Research Council)",
                 "year": 1994, "title": "Nutrient Requirements of Poultry",
                 "publisher": "National Academies Press", "summary": "المرجع الرسمي لمتطلبات الدواجن."},
                {"id": "NRC005", "authors": "NRC (National Research Council)",
                 "year": 2011, "title": "Nutrient Requirements of Fish and Shrimp",
                 "publisher": "National Academies Press", "summary": "المرجع الرسمي لمتطلبات الأسماك."}
            ]
        },
        "inra": {
            "title": "النظام الفرنسي INRA",
            "icon": "🇫🇷",
            "references": [
                {"id": "INRA001", "authors": "INRA (Institut National de la Recherche Agronomique)",
                 "year": 2007, "title": "INRA Feeding System for Ruminants",
                 "publisher": "Wageningen Academic Publishers", "summary": "النظام الفرنسي المتقدم لتغذية المجترات."}
            ]
        },
        "fao": {
            "title": "منظمة الأغذية والزراعة FAO",
            "icon": "🌾",
            "references": [
                {"id": "FAO001", "authors": "Faye, B., Bengoumi, M.",
                 "year": 2018, "title": "Camel Nutrition and Feeding",
                 "publisher": "FAO", "summary": "المرجع الأساسي في تغذية الإبل."}
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
        },
        "ما هي المعايير الدولية NRC": {
            "answer": "NRC هو المجلس القومي للبحوث الأمريكي، المرجع الأساسي في تحديد متطلبات العناصر الغذائية.",
            "simplified": "NRC هي المعايير العالمية لتغذية الحيوان."
        }
    }
    
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
# المعايير القياسية الدولية (NRC, INRA, FAO)
# =====================================================================
STANDARD_VALUES = {
    "أبقار": {
        "تسمين عجول": {"DP": 12.0, "SE": 68.0, "CP": 15.0, "ME": 2.8, "NDF": 35.0, "Ca": 0.8, "P": 0.4, "reference": "NRC 2001", "description": "متطلبات عجول التسمين حسب NRC"},
        "حليب/إدرار": {"DP": 14.0, "SE": 70.0, "CP": 17.5, "ME": 2.9, "NDF": 32.0, "Ca": 1.2, "P": 0.5, "reference": "NRC 2001", "description": "متطلبات أبقار الحليب حسب NRC"},
        "حمل/دفع غذائي": {"DP": 11.0, "SE": 65.0, "CP": 13.8, "ME": 2.7, "NDF": 38.0, "Ca": 0.9, "P": 0.4, "reference": "INRA 2007", "description": "متطلبات الأبقار الحامل حسب INRA"},
        "صيانة": {"DP": 9.0, "SE": 60.0, "CP": 11.3, "ME": 2.6, "NDF": 40.0, "Ca": 0.6, "P": 0.3, "reference": "NRC 2001", "description": "متطلبات صيانة الأبقار حسب NRC"}
    },
    "أغنام": {
        "تسمين حملان": {"DP": 13.0, "SE": 66.0, "CP": 16.3, "ME": 2.7, "NDF": 30.0, "Ca": 0.7, "P": 0.4, "reference": "NRC 2007", "description": "متطلبات حملان التسمين حسب NRC"},
        "حليب/إدرار": {"DP": 14.5, "SE": 68.0, "CP": 18.1, "ME": 2.8, "NDF": 28.0, "Ca": 1.0, "P": 0.5, "reference": "NRC 2007", "description": "متطلبات النعاج المرضعة حسب NRC"},
        "حمل/دفع غذائي": {"DP": 11.5, "SE": 62.0, "CP": 14.4, "ME": 2.6, "NDF": 33.0, "Ca": 0.8, "P": 0.4, "reference": "NRC 2007", "description": "متطلبات النعاج الحامل حسب NRC"},
        "صيانة": {"DP": 8.5, "SE": 58.0, "CP": 10.6, "ME": 2.5, "NDF": 38.0, "Ca": 0.5, "P": 0.3, "reference": "NRC 2007", "description": "متطلبات صيانة الأغنام حسب NRC"}
    },
    "ماعز": {
        "تسمين جديان": {"DP": 12.5, "SE": 64.0, "CP": 15.6, "ME": 2.6, "NDF": 32.0, "Ca": 0.7, "P": 0.4, "reference": "NRC 2007", "description": "متطلبات جديان التسمين حسب NRC"},
        "حليب/إدرار": {"DP": 14.0, "SE": 66.0, "CP": 17.5, "ME": 2.7, "NDF": 30.0, "Ca": 1.0, "P": 0.5, "reference": "NRC 2007", "description": "متطلبات العنزات المرضعة حسب NRC"},
        "حمل/دفع غذائي": {"DP": 11.0, "SE": 60.0, "CP": 13.8, "ME": 2.5, "NDF": 35.0, "Ca": 0.8, "P": 0.4, "reference": "NRC 2007", "description": "متطلبات العنزات الحامل حسب NRC"},
        "صيانة": {"DP": 8.0, "SE": 56.0, "CP": 10.0, "ME": 2.4, "NDF": 40.0, "Ca": 0.5, "P": 0.3, "reference": "NRC 2007", "description": "متطلبات صيانة الماعز حسب NRC"}
    },
    "خيول": {
        "راحة/صيانة": {"DP": 9.0, "SE": 58.0, "CP": 11.3, "ME": 2.5, "NDF": 35.0, "Ca": 0.5, "P": 0.3, "reference": "NRC 2007", "description": "متطلبات صيانة الخيول حسب NRC"},
        "عمل خفيف": {"DP": 10.0, "SE": 60.0, "CP": 12.5, "ME": 2.6, "NDF": 33.0, "Ca": 0.6, "P": 0.3, "reference": "NRC 2007", "description": "متطلبات الخيول في العمل الخفيف حسب NRC"},
        "عمل متوسط": {"DP": 11.0, "SE": 62.0, "CP": 13.8, "ME": 2.7, "NDF": 30.0, "Ca": 0.7, "P": 0.4, "reference": "NRC 2007", "description": "متطلبات الخيول في العمل المتوسط حسب NRC"},
        "عمل مكثف": {"DP": 13.0, "SE": 65.0, "CP": 16.3, "ME": 2.9, "NDF": 28.0, "Ca": 0.8, "P": 0.4, "reference": "NRC 2007", "description": "متطلبات الخيول في العمل المكثف حسب NRC"},
        "سباق": {"DP": 14.0, "SE": 68.0, "CP": 17.5, "ME": 3.0, "NDF": 25.0, "Ca": 0.9, "P": 0.5, "reference": "NRC 2007", "description": "متطلبات خيول السباق حسب NRC"},
        "أمهار نامية": {"DP": 13.0, "SE": 64.0, "CP": 16.3, "ME": 2.8, "NDF": 30.0, "Ca": 0.9, "P": 0.5, "reference": "NRC 2007", "description": "متطلبات الأمهار النامية حسب NRC"},
        "فرسات مرضعات": {"DP": 14.0, "SE": 66.0, "CP": 17.5, "ME": 2.9, "NDF": 28.0, "Ca": 1.2, "P": 0.6, "reference": "NRC 2007", "description": "متطلبات الفرسات المرضعات حسب NRC"}
    },
    "إبل": {
        "راحة/صيانة": {"DP": 8.0, "SE": 55.0, "CP": 10.0, "ME": 2.3, "NDF": 40.0, "Ca": 0.6, "P": 0.3, "reference": "FAO 2018", "description": "متطلبات صيانة الإبل حسب FAO"},
        "حمل/رضاعة": {"DP": 10.0, "SE": 58.0, "CP": 12.5, "ME": 2.4, "NDF": 38.0, "Ca": 1.0, "P": 0.5, "reference": "FAO 2018", "description": "متطلبات الإبل الحامل/المرضعة حسب FAO"},
        "إنتاج حليب": {"DP": 12.0, "SE": 60.0, "CP": 15.0, "ME": 2.6, "NDF": 35.0, "Ca": 1.2, "P": 0.6, "reference": "FAO 2018", "description": "متطلبات إنتاج حليب الإبل حسب FAO"},
        "تسمين": {"DP": 11.0, "SE": 62.0, "CP": 13.8, "ME": 2.5, "NDF": 36.0, "Ca": 0.8, "P": 0.4, "reference": "FAO 2018", "description": "متطلبات تسمين الإبل حسب FAO"},
        "عمل/نقل": {"DP": 10.0, "SE": 58.0, "CP": 12.5, "ME": 2.4, "NDF": 38.0, "Ca": 0.7, "P": 0.4, "reference": "FAO 2018", "description": "متطلبات إبل العمل والنقل حسب FAO"}
    },
    "دواجن لاحم": {
        "بادي (0-14 يوم)": {"DP": 22.0, "SE": 76.0, "CP": 27.5, "ME": 3.0, "NDF": 8.0, "Ca": 1.0, "P": 0.45, "reference": "NRC 1994", "description": "متطلبات البادي للدواجن اللاحم حسب NRC"},
        "نامي (15-28 يوم)": {"DP": 20.0, "SE": 74.0, "CP": 25.0, "ME": 2.9, "NDF": 8.0, "Ca": 0.9, "P": 0.40, "reference": "NRC 1994", "description": "متطلبات النامي للدواجن اللاحم حسب NRC"},
        "ناهي (29-42 يوم)": {"DP": 18.0, "SE": 72.0, "CP": 22.5, "ME": 2.8, "NDF": 9.0, "Ca": 0.8, "P": 0.35, "reference": "NRC 1994", "description": "متطلبات الناهي للدواجن اللاحم حسب NRC"},
        "ناهي متقدم (43+ يوم)": {"DP": 16.0, "SE": 70.0, "CP": 20.0, "ME": 2.7, "NDF": 10.0, "Ca": 0.7, "P": 0.30, "reference": "NRC 1994", "description": "متطلبات الناهي المتقدم حسب NRC"}
    },
    "دواجن بياض": {
        "بياض إنتاجي": {"DP": 16.0, "SE": 66.0, "CP": 20.0, "ME": 2.7, "NDF": 10.0, "Ca": 3.5, "P": 0.45, "reference": "NRC 1994", "description": "متطلبات الدجاج البياض الإنتاجي حسب NRC"}
    },
    "سمان": {
        "بادي": {"DP": 24.0, "SE": 74.0, "CP": 30.0, "ME": 2.9, "NDF": 8.0, "Ca": 0.9, "P": 0.40, "reference": "NRC 1994", "description": "متطلبات بادي السمان حسب NRC"},
        "بياض": {"DP": 18.0, "SE": 68.0, "CP": 22.5, "ME": 2.6, "NDF": 10.0, "Ca": 2.5, "P": 0.40, "reference": "NRC 1994", "description": "متطلبات بياض السمان حسب NRC"}
    },
    "أسماك": {
        "نمو": {"DP": 28.0, "SE": 68.0, "CP": 35.0, "ME": 3.2, "NDF": 5.0, "Ca": 0.4, "P": 0.3, "reference": "NRC 2011", "description": "متطلبات نمو الأسماك حسب NRC"},
        "تسمين نهائي": {"DP": 26.0, "SE": 66.0, "CP": 32.5, "ME": 3.0, "NDF": 5.0, "Ca": 0.4, "P": 0.3, "reference": "NRC 2011", "description": "متطلبات تسمين الأسماك النهائي حسب NRC"}
    }
}

# =====================================================================
# نظام أسعار المدن والمخازن
# =====================================================================
class MarketPriceEngine:
    @staticmethod
    @lru_cache(maxsize=128)
    def get_adjusted_market_data(country, state_or_region, city):
        feed_prices = {}
        base_prices = {
            "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0,
            "سورجم (فتريتة)": 195.0, "قمح محلي مصنّع": 240.0,
            "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا 44%": 440.0,
            "كسب فول صويا 48%": 480.0, "كسب عباد الشمس 36%": 310.0,
            "كسب بذور القطن (مقشور)": 290.0, "نخالة قمح (ردة)": 150.0,
            "البرسيم الجاف (الدريس)": 170.0, "مولاس قصب السكر": 120.0,
            "مسحوق أسماك (Fishmeal 60%)": 850.0, "مركزات دواجن وسمان": 650.0,
            "مركزات خيول ومجترات": 600.0,
            "الحجر الجيري (بودرة بلاط)": 40.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0,
            "ملح الطعام": 30.0, "مضاد سموم فطرية": 950.0,
            "بيكربونات الصوديوم (الصودا)": 340.0,
            "خميرة الخبز (Yeast)": 450.0
        }
        for ing, price in base_prices.items():
            feed_prices[ing] = price
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

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG", "currency_name": "جنيه سوداني"},
    "LIBYA": {"rate": 4.80, "sym": "LYD", "currency_name": "دينار ليبي"},
    "مصر": {"rate": 48.0, "sym": "EGP", "currency_name": "جنيه مصري"},
    "دولار أمريكي": {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"}
}

# =====================================================================
# مولد PDF المتقدم
# =====================================================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        font_path = download_arabic_font()
        if font_path and os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
                self.font_name = 'ArabicFont'
            except Exception as e:
                pass
        self.styles = self._create_styles()
        self.SUPERVISOR_SIGNATURE = "الاختصاصي م. عبد القادر إسماعيل تاور"
    
    def _create_styles(self):
        styles = {}
        styles['title'] = ParagraphStyle('title', fontName=self.font_name, fontSize=22, alignment=TA_CENTER, textColor=HexColor('#1b5e20'), spaceAfter=20, leading=30)
        styles['subtitle'] = ParagraphStyle('subtitle', fontName=self.font_name, fontSize=16, alignment=TA_CENTER, textColor=HexColor('#2e7d32'), spaceAfter=15, leading=20)
        styles['heading'] = ParagraphStyle('heading', fontName=self.font_name, fontSize=14, alignment=TA_RIGHT, textColor=HexColor('#1b5e20'), spaceAfter=10, leading=18, fontweight='bold')
        styles['body'] = ParagraphStyle('body', fontName=self.font_name, fontSize=11, alignment=TA_RIGHT, textColor=HexColor('#333333'), spaceAfter=6, leading=16)
        styles['footer'] = ParagraphStyle('footer', fontName=self.font_name, fontSize=8, alignment=TA_CENTER, textColor=HexColor('#999999'), spaceAfter=0, leading=10)
        styles['signature'] = ParagraphStyle('signature', fontName=self.font_name, fontSize=12, alignment=TA_CENTER, textColor=HexColor('#1b5e20'), spaceAfter=10, leading=18, fontweight='bold')
        styles['reference'] = ParagraphStyle('reference', fontName=self.font_name, fontSize=9, alignment=TA_RIGHT, textColor=HexColor('#666666'), spaceAfter=4, leading=12)
        return styles
    
    def _safe_paragraph(self, text, style='body'):
        if not text:
            return Paragraph("", self.styles.get(style, self.styles['body']))
        try:
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, self.styles.get(style, self.styles['body']))
        except:
            return Paragraph(str(text), self.styles.get(style, self.styles['body']))
    
    def generate_lab_report(self, analysis_results, animal_type, stage, user_name, 
                           standard=None, evaluation=None, comps=None, total_weight=None,
                           milk_production=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        
        def p(text, style='body'):
            return self._safe_paragraph(text, style)
        
        def ps(text, style='signature'):
            return self._safe_paragraph(text, style)
        
        # العنوان
        story.append(p("🔬 تقرير التحليل المخبري المتقدم", 'title'))
        story.append(p("تاور نولجي Tawornology العلمية - للانتاج الحيواني وتركيب الاعلاف", 'subtitle'))
        story.append(Spacer(1, 10))
        
        # المشرف والمعلومات
        story.append(p(f"👨‍💻 المشرف العام: {self.SUPERVISOR_SIGNATURE}", 'heading'))
        story.append(p(f"🐾 الحيوان: {animal_type} | المرحلة: {stage}", 'body'))
        if milk_production:
            story.append(p(f"🥛 إنتاج الحليب: {milk_production:.1f} لتر/يوم", 'body'))
        story.append(p(f"📅 تاريخ التحليل: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 'body'))
        story.append(Spacer(1, 15))
        
        # جدول المكونات
        if comps and total_weight:
            story.append(p("📋 المكونات المدخلة:", 'heading'))
            story.append(Spacer(1, 5))
            table_data = [['المادة', 'الوزن (كجم)', 'النسبة %']]
            for item in comps:
                table_data.append([
                    item.get('المادة', ''),
                    f"{item.get('الوزن', 0):.2f}",
                    f"{item.get('النسبة %', '0'):.2f}"
                ])
            table_data.append(['إجمالي الوزن', f"{total_weight:.1f}", '100.00'])
            
            t = Table(table_data, colWidths=[180, 120, 120])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
                ('BACKGROUND', (0, -1), (-1, -1), HexColor('#e8f5e9')),
                ('FONTWEIGHT', (0, -1), (-1, -1), 'BOLD'),
            ]))
            story.append(t)
            story.append(Spacer(1, 15))
        
        # النتائج المحسوبة
        story.append(p("🔬 النتائج المحسوبة:", 'heading'))
        story.append(Spacer(1, 5))
        if analysis_results:
            results_data = [['العنصر', 'القيمة']]
            for key, val in analysis_results.items():
                if key != 'components':
                    label_map = {'cp': 'البروتين الخام (CP)', 'dp': 'البروتين المهضوم (DP)', 'se': 'معادل النشاء (SE)'}
                    label = label_map.get(key, key)
                    results_data.append([label, f"{val:.2f}%" if key != 'se' else f"{val:.2f} وحدة"])
            
            t_results = Table(results_data, colWidths=[250, 200])
            t_results.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565C0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#1565C0')),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#e3f2fd')),
            ]))
            story.append(t_results)
            story.append(Spacer(1, 15))
        
        # المقارنة مع المعايير
        if standard:
            story.append(p("📊 مقارنة مع المعايير القياسية (NRC/INRA/FAO):", 'heading'))
            story.append(Spacer(1, 5))
            comp_data = [['المقياس', 'المحسوب', 'القياسي', 'الانحراف %', 'التقييم']]
            if 'dp' in analysis_results and 'dp' in standard:
                dev = ((analysis_results['dp'] - standard['dp']) / standard['dp']) * 100 if standard['dp'] > 0 else 0
                grade = "✅ ممتاز" if abs(dev) <= 5 else ("👍 جيد" if abs(dev) <= 10 else "⚠️ يحتاج تحسين")
                comp_data.append(['DP', f"{analysis_results['dp']:.2f}%", f"{standard['dp']:.2f}%", f"{dev:.1f}%", grade])
            if 'se' in analysis_results and 'se' in standard:
                dev = ((analysis_results['se'] - standard['se']) / standard['se']) * 100 if standard['se'] > 0 else 0
                grade = "✅ ممتاز" if abs(dev) <= 5 else ("👍 جيد" if abs(dev) <= 10 else "⚠️ يحتاج تحسين")
                comp_data.append(['SE', f"{analysis_results['se']:.2f}", f"{standard['se']:.2f}", f"{dev:.1f}%", grade])
            if 'cp' in analysis_results and 'cp' in standard:
                dev = ((analysis_results['cp'] - standard['cp']) / standard['cp']) * 100 if standard['cp'] > 0 else 0
                grade = "✅ ممتاز" if abs(dev) <= 5 else ("👍 جيد" if abs(dev) <= 10 else "⚠️ يحتاج تحسين")
                comp_data.append(['CP', f"{analysis_results['cp']:.2f}%", f"{standard['cp']:.2f}%", f"{dev:.1f}%", grade])
            
            t_comp = Table(comp_data, colWidths=[120, 100, 100, 100, 120])
            t_comp.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f5f5f5')),
            ]))
            story.append(t_comp)
            story.append(Spacer(1, 10))
            story.append(p(f"📌 المرجع: {standard.get('reference', 'N/A')}", 'reference'))
            story.append(Spacer(1, 5))
        
        # الرسم البياني
        if standard and analysis_results and len(analysis_results) > 1:
            try:
                fig, ax = plt.subplots(figsize=(5, 3))
                labels = []
                calc_vals = []
                std_vals = []
                if 'dp' in analysis_results and 'dp' in standard:
                    labels.append('DP'); calc_vals.append(analysis_results['dp']); std_vals.append(standard['dp'])
                if 'se' in analysis_results and 'se' in standard:
                    labels.append('SE'); calc_vals.append(analysis_results['se']); std_vals.append(standard['se'])
                if 'cp' in analysis_results and 'cp' in standard:
                    labels.append('CP'); calc_vals.append(analysis_results['cp']); std_vals.append(standard['cp'])
                
                x = np.arange(len(labels))
                width = 0.35
                ax.bar(x - width/2, calc_vals, width, label='المحسوب', color='#2e7d32')
                ax.bar(x + width/2, std_vals, width, label='القياسي', color='#1565C0')
                ax.set_xlabel('العنصر')
                ax.set_ylabel('القيمة')
                ax.set_title('مقارنة القيم المحسوبة مع المعايير القياسية')
                ax.set_xticks(x)
                ax.set_xticklabels(labels)
                ax.legend()
                
                buf_img = io.BytesIO()
                plt.savefig(buf_img, format='png', dpi=150, bbox_inches='tight')
                plt.close()
                buf_img.seek(0)
                story.append(Image(buf_img, width=400, height=240))
            except:
                pass
            story.append(Spacer(1, 15))
        
        # التقييم النهائي
        if evaluation:
            story.append(p("⭐ التقييم النهائي:", 'heading'))
            story.append(Spacer(1, 5))
            eval_data = [['المقياس', 'التقييم']]
            for item, grade in evaluation.items():
                if grade:
                    eval_data.append([item, grade])
            t_eval = Table(eval_data, colWidths=[200, 200])
            t_eval.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
            ]))
            story.append(t_eval)
            story.append(Spacer(1, 15))
        
        # الملاحظات
        story.append(p("📌 الملاحظات والتوصيات:", 'heading'))
        story.append(Spacer(1, 5))
        notes = []
        if standard and analysis_results:
            if 'dp' in analysis_results and 'dp' in standard:
                dev = ((analysis_results['dp'] - standard['dp']) / standard['dp']) * 100 if standard['dp'] > 0 else 0
                if abs(dev) > 10:
                    notes.append("⚠️ البروتين المهضوم بحاجة لضبط." if dev < 0 else "⚠️ البروتين المهضوم أعلى من المعيار.")
            if 'se' in analysis_results and 'se' in standard:
                dev = ((analysis_results['se'] - standard['se']) / standard['se']) * 100 if standard['se'] > 0 else 0
                if abs(dev) > 10:
                    notes.append("⚠️ الطاقة بحاجة لضبط." if dev < 0 else "⚠️ الطاقة أعلى من المعيار.")
            if milk_production and 'se' in analysis_results:
                se_per_liter = analysis_results.get('se', 0) / milk_production if milk_production > 0 else 0
                if se_per_liter < 20:
                    notes.append("⚠️ الطاقة لكل لتر حليب منخفضة، يوصى بزيادة مصادر الطاقة.")
                elif se_per_liter > 35:
                    notes.append("⚠️ الطاقة لكل لتر حليب مرتفعة، يمكن تقليل مصادر الطاقة.")
        if not notes:
            notes.append("✅ الخلطة متوازنة وتتوافق مع المعايير القياسية (NRC/INRA/FAO) بشكل ممتاز.")
        for note in notes:
            story.append(p(f"• {note}", 'body'))
        
        story.append(Spacer(1, 20))
        story.append(ps("مع خالص التحية والتقدير،", 'signature'))
        story.append(Spacer(1, 5))
        story.append(ps(self.SUPERVISOR_SIGNATURE, 'signature'))
        story.append(Spacer(1, 10))
        story.append(p("تم التوليد بواسطة تاور نولجي Tawornology العلمية © 2026", 'footer'))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, 
                                      local_cost, local_sym, computed_se, user_name, 
                                      include_charts=True, extra_info=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        
        def p(text, style='body'):
            return self._safe_paragraph(text, style)
        
        def ps(text, style='signature'):
            return self._safe_paragraph(text, style)
        
        story.append(p("🌾 تاور نولجي Tawornology العلمية", 'title'))
        story.append(p("📄 تقرير فني - تركيب العلف", 'subtitle'))
        story.append(Spacer(1, 10))
        
        story.append(p(f"👨‍💻 المشرف: {self.SUPERVISOR_SIGNATURE}", 'heading'))
        story.append(p(f"🐾 الفصيل: {breed}", 'body'))
        story.append(p(f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 'body'))
        story.append(Spacer(1, 15))
        
        tdata = [['المعيار', 'القيمة']]
        tdata.append(['البروتين المهضوم (DP)', f'{target_dp:.2f}%'])
        tdata.append(['معادل النشاء (SE)', f'{computed_se:.2f} وحدة'])
        tdata.append(['التكلفة للطن', f'${cost:.2f} ({local_cost:,.2f} {local_sym})'])
        
        t = Table(tdata, colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#2e7d32')),
        ]))
        story.append(t)
        story.append(PageBreak())
        
        story.append(p("📋 المقادير:", 'heading'))
        story.append(Spacer(1, 10))
        ing_data = [['المكون', 'النسبة %', 'كجم/طن']]
        for ing, pct in formula.items():
            ing_data.append([ing, f'{pct:.2f}%', f'{pct*10:.1f}'])
        t2 = Table(ing_data, colWidths=[180, 150, 150])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
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
                ax.legend([arabic_processor.fix_arabic_text(n) for n in names], 
                         title=arabic_processor.fix_arabic_text("المكونات"), 
                         loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=8)
                ax.set_title(arabic_processor.fix_arabic_text('📊 توزيع المكونات'), fontsize=12)
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=400, height=230))
            except:
                pass
        
        story.append(PageBreak())
        story.append(p("📌 التوصيات:", 'heading'))
        for rec in ["• يوصى بإضافة الإنزيمات لتحسين الهضم.", "• يجب مراقبة جودة المواد الخام.", "• يجب تخزين العلف في مكان جاف.", "• يوصى بتقسيم العلف على عدة وجبات."]:
            story.append(p(rec))
        story.append(Spacer(1, 15))
        if extra_info:
            story.append(p("معلومات إضافية:", 'heading'))
            for key, value in extra_info.items():
                if value:
                    story.append(p(f"• {key}: {value}", 'body'))
        
        story.append(PageBreak())
        story.append(ps("مع خالص التحية والتقدير،", 'signature'))
        story.append(Spacer(1, 5))
        story.append(ps(self.SUPERVISOR_SIGNATURE, 'signature'))
        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة تاور نولجي Tawornology العلمية © 2026", 'footer'))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# =====================================================================
# مدير مزارع الدجاج
# =====================================================================
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
    def calculate_livability(initial_count, dead_count):
        return 100.0 - BroilerFarmManager.calculate_mortality_rate(dead_count, initial_count)
    
    @staticmethod
    def calculate_epef(livability, body_weight_kg, age_days, fcr):
        if age_days <= 0 or fcr <= 0:
            return 0.0
        return (livability * body_weight_kg) / (age_days * fcr) * 100.0

# =====================================================================
# مكتبة الأعلاف (المبسطة)
# =====================================================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6},
    },
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5},
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5},
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
        "خميرة الخبز (Yeast)": {"CP": 45.0, "DC": 0.85, "SE": 35.0, "NDF": 5.0, "ADF": 2.0, "EE": 2.5, "ASH": 7.0},
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
    }
}

FLAT_FEED_DB = {}
for category, items in BIG_FEEDS_LIBRARY.items():
    for feed_name, nutrition in items.items():
        FLAT_FEED_DB[feed_name] = nutrition

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
                        "quantity": 25.0, "min_threshold": 5.0, "unit": "طن",
                        "last_updated": datetime.now().isoformat(), "supplier": "غير محدد"
                    }
    
    @staticmethod
    def check_stock_levels():
        warnings = {}
        for item, data in st.session_state["inventory"].items():
            qty = data if isinstance(data, (int, float)) else data["quantity"]
            threshold = 5.0 if isinstance(data, (int, float)) else data.get("min_threshold", 5.0)
            if qty <= 0:
                warnings[item] = {"status": "نفذ المخزون", "level": "critical"}
            elif qty < threshold:
                warnings[item] = {"status": "منخفض", "level": "warning"}
        return warnings
    
    @staticmethod
    def get_stock_summary():
        total_items = len(st.session_state["inventory"])
        total_quantity = sum(d["quantity"] if isinstance(d, dict) else d for d in st.session_state["inventory"].values())
        low_stock = sum(1 for d in st.session_state["inventory"].values() 
                       if (d["quantity"] if isinstance(d, dict) else d) < (d.get("min_threshold", 5.0) if isinstance(d, dict) else 5.0))
        return {"total_items": total_items, "total_quantity": total_quantity, "low_stock": low_stock}

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
# حالة الجلسة العامة
# =====================================================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "login_welcome_shown" not in st.session_state: st.session_state["login_welcome_shown"] = False
if "login_attempts" not in st.session_state: st.session_state["login_attempts"] = 0
if "last_login_time" not in st.session_state: st.session_state["last_login_time"] = None
if "broiler_farms" not in st.session_state: st.session_state["broiler_farms"] = {}
if "whatsapp_alerts_sent" not in st.session_state: st.session_state["whatsapp_alerts_sent"] = {}
if "analysis_results" not in st.session_state: st.session_state["analysis_results"] = None
if "analysis_animal" not in st.session_state: st.session_state["analysis_animal"] = "غير محدد"
if "analysis_stage" not in st.session_state: st.session_state["analysis_stage"] = "غير محدد"
if "daily_production_log" not in st.session_state: st.session_state["daily_production_log"] = []
if "basmala_played" not in st.session_state: st.session_state["basmala_played"] = False
if "welcome_played" not in st.session_state: st.session_state["welcome_played"] = False
if "guide_played" not in st.session_state: st.session_state["guide_played"] = {}
if "active_formula" not in st.session_state: st.session_state["active_formula"] = {}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 12.0
if "active_se_tag" not in st.session_state: st.session_state["active_se_tag"] = 65.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0
if "lab_sample" not in st.session_state: st.session_state["lab_sample"] = None
if "lab_analysis_done" not in st.session_state: st.session_state["lab_analysis_done"] = False

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
        "لتر حليب خام ($)": 0.90, "لتر حليب إبل ($)": 1.50
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
# شريط الدعاء المحسّن
# =====================================================================
def render_dua_bar():
    st.markdown("""
    <style>
    @keyframes scrollDua {
        0% { transform: translateX(100%); opacity: 0; }
        4% { transform: translateX(0%); opacity: 1; }
        92% { transform: translateX(0%); opacity: 1; }
        96% { transform: translateX(-100%); opacity: 0; }
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
        50% { transform: scale(1.3); color: #ff1744; }
    }
    @keyframes sparkle {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    .dua-container {
        background: linear-gradient(135deg, #0d1b2a 0%, #1a237e 35%, #4a148c 65%, #0d1b2a 100%);
        padding: 25px 0;
        border-radius: 20px;
        margin-bottom: 20px;
        overflow: hidden;
        border: 3px solid #ffd700;
        box-shadow: 0 10px 50px rgba(255, 215, 0, 0.4), inset 0 0 40px rgba(255, 215, 0, 0.1);
        direction: rtl;
        position: relative;
        min-height: 80px;
    }
    .dua-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        right: -50%;
        bottom: -50%;
        background: radial-gradient(ellipse at center, rgba(255, 215, 0, 0.06), transparent 70%);
        animation: sparkle 5s ease-in-out infinite;
        pointer-events: none;
    }
    .dua-container::after {
        content: '🕊️';
        position: absolute;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 2rem;
        opacity: 0.15;
        animation: pulseHeart 3s ease-in-out infinite;
    }
    .dua-text {
        display: inline-block;
        white-space: nowrap;
        animation: scrollDua 30s ease-in-out infinite;
        font-size: 1.7rem;
        font-weight: 800;
        color: #ffd700;
        animation: scrollDua 30s ease-in-out infinite, glowText 4s ease-in-out infinite;
        padding: 0 30px;
        font-family: 'Cairo', 'Tajawal', sans-serif;
        direction: rtl;
        unicode-bidi: plaintext;
        letter-spacing: 2px;
        animation-fill-mode: forwards;
        text-shadow: 0 0 25px rgba(255, 215, 0, 0.4);
        line-height: 1.6;
    }
    .dua-text .emoji-heart {
        display: inline-block;
        animation: pulseHeart 1.5s ease-in-out infinite;
        margin: 0 8px;
    }
    .dua-text .gold-star {
        color: #ffd700;
        font-size: 1.6rem;
        margin: 0 12px;
        display: inline-block;
        animation: pulseHeart 2s ease-in-out infinite;
    }
    .dua-text .name-highlight {
        color: #ffab40;
        font-weight: 900;
        background: rgba(255, 215, 0, 0.12);
        padding: 0 10px;
        border-radius: 8px;
        border: 1px solid rgba(255, 215, 0, 0.25);
        display: inline-block;
    }
    .dua-reminder {
        text-align: center;
        color: #b39ddb;
        font-size: 1rem;
        padding: 12px 0;
        background: rgba(0,0,0,0.3);
        border-radius: 0 0 18px 18px;
        border-top: 1px solid rgba(255, 215, 0, 0.2);
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .dua-reminder span {
        color: #ffd54f;
        font-weight: 700;
        background: rgba(255, 215, 0, 0.1);
        padding: 4px 16px;
        border-radius: 25px;
        border: 1px solid rgba(255, 215, 0, 0.2);
    }
    .dua-reminder .reminder-icon {
        animation: pulseHeart 1.8s ease-in-out infinite;
        display: inline-block;
    }
    @media (max-width: 768px) {
        .dua-text { font-size: 1.2rem; }
        .dua-container { padding: 15px 0; min-height: 60px; }
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
        <span class="reminder-icon">🕊️</span> <span>تذكير:</span> ادعُ لهما بالرحمة والمغفرة، فاللهم ارحمهما كما ربياني صغيراً وأحسن إليهما كما أحسنا إلينا <span class="reminder-icon">🕊️</span>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# CSS للواجهة
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
.comparison-good { background: #e8f5e9; padding: 3px 10px; border-radius: 5px; color: #2e7d32; font-weight: bold; }
.comparison-warning { background: #fff3e0; padding: 3px 10px; border-radius: 5px; color: #e65100; font-weight: bold; }
.comparison-excellent { background: #e3f2fd; padding: 3px 10px; border-radius: 5px; color: #0d47a1; font-weight: bold; }
.inbox-box {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    border: 2px solid #1565C0;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    direction: rtl;
    text-align: right;
}
.inbox-box .inbox-title {
    color: #0d47a1;
    font-size: 1.3rem;
    font-weight: 700;
}
.inbox-box .inbox-item {
    background: white;
    padding: 10px 15px;
    border-radius: 8px;
    margin: 8px 0;
    border-right: 4px solid #1565C0;
}
.nrc-badge {
    background: #1a237e;
    color: white;
    padding: 2px 12px;
    border-radius: 15px;
    font-size: 0.8rem;
    display: inline-block;
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
    st.markdown("<p style='text-align:center; color:#888; font-size:0.9rem;'>الإصدار 18.0 - المعايير الدولية NRC/INRA/FAO</p>", unsafe_allow_html=True)
    
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
                voice_guide("السلام عليكم، مرحباً بك زائراً في تاور نولجي.")
                st.rerun()
            else:
                st.error("❌ حدث خطأ في الدخول كزائر")

    st.markdown("<hr style='margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#666;'>🔑 للمالك والمختصين</p>", unsafe_allow_html=True)
    
    login_option = st.radio("طريقة الدخول:", ["كود الدخول السري", "اسم المستخدم وكلمة المرور"], horizontal=True)
    
    if login_option == "كود الدخول السري":
        input_code = st.text_input("🔑 كود الدخول:", type="password")
        col_login, col_reset = st.columns(2)
        with col_login:
            if st.button("تسجيل الدخول 🔓", type="secondary", use_container_width=True):
                if input_code.strip() in CODES_DB:
                    st.session_state["approved"] = True
                    st.session_state["user_role"] = CODES_DB[input_code.strip()]["role"]
                    st.session_state["login_welcome_shown"] = False
                    st.session_state["login_attempts"] = 0
                    st.session_state["last_login_time"] = datetime.now()
                    voice_guide(f"مرحباً بك في تاور نولجي، {CODES_DB[input_code.strip()]['name']}.")
                    st.rerun()
                else:
                    st.session_state["login_attempts"] += 1
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
    🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# الترحيب بعد الدخول
# =====================================================================
if not st.session_state["login_welcome_shown"]:
    role_messages = {
        "owner": "👑 مرحباً بك في تاور نولجي، الاختصاصي م. عبد القادر إسماعيل تاور",
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
            if key not in ["inventory", "broiler_farms", "whatsapp_alerts_sent", "analysis_results", "basmala_played", "welcome_played", "email_password", "guide_played", "active_formula", "computed_ton_cost", "lab_sample", "lab_analysis_done"]:
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
# دالة عرض المعايير القياسية
# =====================================================================
def show_standard_reference(animal_type, stage):
    standard = STANDARD_VALUES.get(animal_type, {}).get(stage, {})
    if standard:
        st.markdown(f"""
        <div style='background:#f0f4ff; padding:15px; border-radius:12px; border-right:4px solid #1a237e; direction:rtl; margin:10px 0;'>
            <b>📊 المعايير القياسية المرجعية:</b><br>
            <span class='nrc-badge'>{standard.get('reference', 'N/A')}</span>
            <br>
            <b>DP:</b> {standard.get('DP', '-')}% | 
            <b>SE:</b> {standard.get('SE', '-')} |
            <b>CP:</b> {standard.get('CP', '-')}% |
            <b>ME:</b> {standard.get('ME', '-')} Mcal/kg |
            <b>NDF:</b> {standard.get('NDF', '-')}%
            <br>
            <small style='color:#666;'>{standard.get('description', '')}</small>
        </div>
        """, unsafe_allow_html=True)
        return standard
    return None

# =====================================================================
# دالة تركيب العلف (مع المعايير الدولية)
# =====================================================================
def render_feed_formulation(animal_key, display_name, icon, default_breeds, default_stages, default_dp, default_se, has_measurements=True):
    st.markdown(f'<div class="section-title">{icon} {display_name}</div>', unsafe_allow_html=True)
    
    col_measure, col_settings = st.columns([0.4, 0.6])
    with col_measure:
        if has_measurements:
            st.markdown('<div class="measurement-card">', unsafe_allow_html=True)
            st.markdown("#### 📏 القياسات الحيوية")
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
            st.info(f"**الاحتياج اليومي:** {daily_dry_matter:.2f} كجم مادة جافة")
            if estimated_weight > 0:
                age_factor = 1 + (age_months - 12) * 0.01
                adjusted_dp = default_dp * (1 + (estimated_weight - 500) / 2000) * age_factor
                adjusted_se = default_se * (1 + (estimated_weight - 500) / 3000) * age_factor
            else:
                adjusted_dp = default_dp
                adjusted_se = default_se
            st.caption(f"⚖️ DP المقترح: {adjusted_dp:.1f}% | SE: {adjusted_se:.1f}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("💡 لا تتوفر قياسات للطيور والأسماك.")
    
    with col_settings:
        st.markdown("#### 🎯 السلالة والمرحلة")
        col_b, col_s = st.columns(2)
        with col_b:
            breed = st.selectbox("السلالة:", default_breeds, key=f"{animal_key}_breed")
        with col_s:
            stage = st.selectbox("المرحلة:", default_stages, key=f"{animal_key}_stage")
        
        # عرض المعايير القياسية المرجعية
        standard = show_standard_reference(display_name, stage)
        
        # إنتاج الحليب
        milk_production = 0
        if animal_key in ["cattle", "sheep", "goat", "camel"] and "حليب" in stage:
            st.markdown("#### 🥛 إنتاج الحليب")
            milk_production = st.number_input(
                "إنتاج الحليب اليومي (لتر/يوم)",
                min_value=0.0, max_value=100.0, value=10.0, step=0.5,
                key=f"{animal_key}_milk"
            )
            st.caption(f"📌 سيتم تعديل الاحتياجات بناءً على إنتاج {milk_production:.1f} لتر حليب يومياً")
        
        st.markdown("#### 🧬 العمر والحالة الفسيولوجية")
        col_age_phys = st.columns(2)
        with col_age_phys[0]:
            age_input = st.number_input("العمر (شهر)", min_value=1, max_value=240, value=24, step=1, key=f"{animal_key}_age_input")
        with col_age_phys[1]:
            phys_state = st.selectbox("الحالة الفسيولوجية", 
                ["طبيعي", "حامل", "مرضع", "صائم", "نشاط مكثف", "استشفاء", "نمو سريع"],
                key=f"{animal_key}_phys")
        
        st.markdown("#### 🧬 البروتين والطاقة")
        protein_basis = st.radio("أساس البروتين:", ["DP", "CP"], horizontal=True, key=f"{animal_key}_basis")
        
        # استخدام المعايير القياسية كقيم افتراضية
        default_dp_val = standard.get('DP', default_dp) if standard else default_dp
        default_se_val = standard.get('SE', default_se) if standard else default_se
        
        if protein_basis == "DP":
            target_protein = st.number_input("DP المطلوب (%)", min_value=5.0, max_value=50.0, 
                value=float(adjusted_dp if has_measurements else default_dp_val), step=0.5, key=f"{animal_key}_dp")
        else:
            target_protein = st.number_input("CP المطلوب (%)", min_value=5.0, max_value=60.0, 
                value=float(default_dp_val/0.80), step=0.5, key=f"{animal_key}_cp")
        target_se = st.number_input("SE المطلوب (وحدة)", min_value=10.0, max_value=90.0, 
            value=float(adjusted_se if has_measurements else default_se_val), step=1.0, key=f"{animal_key}_se")
        
        if protein_basis == "DP":
            actual_dp = target_protein
        else:
            actual_dp = target_protein * 0.80
        
        # تعديل حسب الحالة
        state_multipliers = {"طبيعي": 1.0, "حامل": 1.15, "مرضع": 1.30, "صائم": 0.85, "نشاط مكثف": 1.25, "استشفاء": 1.20, "نمو سريع": 1.35}
        multiplier = state_multipliers.get(phys_state, 1.0)
        final_dp = actual_dp * multiplier
        final_se = target_se * multiplier
        
        # تعديل حسب إنتاج الحليب
        if milk_production > 0:
            milk_dp = milk_production * 0.30
            milk_se = milk_production * 1.50
            final_dp += milk_dp
            final_se += milk_se
            st.caption(f"🥛 إضافة {milk_dp:.1f}% DP و {milk_se:.1f} SE لإنتاج {milk_production:.1f} لتر حليب")
        
        st.caption(f"📌 القيم النهائية: DP={final_dp:.1f}%, SE={final_se:.1f}")
    
    st.markdown("#### 🌾 اختر المكونات")
    selected = []
    prices = {}
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=False):
            cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with cols[idx % 3]:
                    default_checked = ing_name in ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)", "ملح الطعام"]
                    checked = st.checkbox(ing_name, value=default_checked, key=f"{animal_key}_feed_{ing_name}")
                    if checked:
                        price = st.number_input(f"سعر {ing_name} ($/طن)", min_value=5.0, value=250.0, key=f"{animal_key}_price_{ing_name}")
                        selected.append(ing_name)
                        prices[ing_name] = price
    
    col_buttons = st.columns(2)
    with col_buttons[0]:
        if st.button(f"🚀 تشغيل محرك التركيب ({display_name})", type="primary", use_container_width=True):
            if len(selected) < 3:
                st.warning("⚠️ يرجى اختيار 3 مكونات على الأقل.")
            else:
                with st.spinner("جاري الحساب..."):
                    c = [prices[ing] for ing in selected]
                    bounds = [(0, 100) for _ in selected]
                    A_eq = [[1] * len(selected)]
                    b_eq = [100]
                    cp_row = []; se_row = []
                    for ing in selected:
                        d = FLAT_FEED_DB[ing]
                        cp_row.append(d["CP"] * d["DC"])
                        se_row.append(d["SE"])
                    A_eq.append(cp_row)
                    b_eq.append(final_dp)
                    A_ub = [[-x for x in se_row]]
                    b_ub = [-final_se]
                    if animal_key in ["cattle", "sheep", "goat", "camel"]:
                        ndf_row = [FLAT_FEED_DB[ing].get("NDF", 0) for ing in selected]
                        A_ub.append(ndf_row); b_ub.append(35)
                    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
                    if res.success:
                        formula = {selected[i]: res.x[i] for i in range(len(selected)) if res.x[i] > 0.0001}
                        cost_ton = res.fun / 100.0
                        st.success(f"✅ تم توليد الخلطة! التكلفة: ${cost_ton:.2f}/طن")
                        for k, v in formula.items():
                            st.markdown(f'<div class="formula-item"><span>{k}</span><span>{v:.1f}% ({v*10:.1f} كجم/طن)</span></div>', unsafe_allow_html=True)
                        st.session_state["active_formula"] = formula
                        st.session_state["computed_ton_cost"] = cost_ton
                        st.session_state["active_cp_tag"] = final_dp
                        st.session_state["active_se_tag"] = final_se
                        st.session_state["active_breed_tag"] = f"{breed} - {stage} ({phys_state})"
                        st.session_state["active_stage_title"] = f"{display_name} - {stage}"
                        
                        if st.button("🔬 إرسال العينة إلى المختبر", use_container_width=True):
                            st.session_state["lab_sample"] = {
                                'formula': formula,
                                'animal': display_name,
                                'breed': breed,
                                'stage': stage,
                                'age': age_input,
                                'physiological': phys_state,
                                'dp': final_dp,
                                'se': final_se,
                                'cp': final_dp / 0.80,
                                'milk_production': milk_production,
                                'standard': standard
                            }
                            st.success("✅ تم إرسال العينة إلى المختبر.")
                            voice_guide("تم إرسال العينة إلى المختبر.")
                        
                        try:
                            pdf_data = pdf_generator.generate_comprehensive_report(
                                formula, final_dp, f"{breed} - {stage} ({phys_state})", 
                                cost_ton, "المدينة", cost_ton*600, "SDG", final_se,
                                st.session_state.get("user", {}).get("full_name", "مستخدم"),
                                extra_info={"السلالة": breed, "المرحلة": stage, "الحالة": phys_state, "العمر": f"{age_input} شهر", "إنتاج الحليب": f"{milk_production:.1f} لتر/يوم" if milk_production > 0 else "غير محدد", "المعيار": standard.get('reference', 'N/A') if standard else 'غير محدد'}
                            )
                            st.download_button("📥 تحميل PDF", pdf_data, file_name=f"Tawornology_{display_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf", use_container_width=True)
                        except Exception as e:
                            st.warning(f"⚠️ تعذر إنشاء PDF: {e}")
                    else:
                        st.error("❌ تعذر إيجاد حل، حاول تغيير المكونات.")

# =====================================================================
# التبويب 0: القطاع الحيواني
# =====================================================================
with tabs[0]:
    guide_section("القطاع الحيواني", "اختر نوع الحيوان، ثم السلالة والمرحلة، والعمر والحالة الفسيولوجية، ثم اختر المكونات.")
    animal_tabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐴 خيول", "🐫 إبل", "🐔 دواجن", "🐟 أسماك", "🔬 المختبر المتقدم"])
    
    with animal_tabs[0]:
        render_feed_formulation("cattle", "أبقار", "🐄", 
            ["كنانة", "بطانة", "هولشتاين"], 
            ["تسمين عجول", "حليب/إدرار", "حمل/دفع غذائي", "صيانة"], 
            12.0, 65.0, has_measurements=True)
    with animal_tabs[1]:
        render_feed_formulation("sheep", "أغنام", "🐏", 
            ["الصحراوي", "البربري", "النعيمي"], 
            ["تسمين حملان", "نعاج مرضعات", "نعاج حامل", "نعاج جافة"], 
            11.5, 62.0, has_measurements=True)
    with animal_tabs[2]:
        render_feed_formulation("goat", "ماعز", "🐐", 
            ["النوبي", "الصحراوي", "بور"], 
            ["تسمين جديان", "عنزات حلابة", "عنزات حامل", "صيانة"], 
            11.0, 60.0, has_measurements=True)
    with animal_tabs[3]:
        render_feed_formulation("horse", "خيول", "🐴", 
            ["عربي أصيل", "ثوروبريد", "محلي"], 
            ["راحة/صيانة", "عمل خفيف", "عمل متوسط", "عمل مكثف", "سباق", "أمهار نامية", "فرسات مرضعات"], 
            11.0, 62.0, has_measurements=True)
    with animal_tabs[4]:
        render_feed_formulation("camel", "إبل", "🐫", 
            ["عربية (دروميداري)", "باختري", "هجين"], 
            ["راحة/صيانة", "حمل/رضاعة", "إنتاج حليب", "تسمين", "عمل/نقل"], 
            10.0, 58.0, has_measurements=True)
    with animal_tabs[5]:
        render_feed_formulation("poultry", "دواجن", "🐔", 
            ["لاحم (Broiler)", "بياض (Layer)", "سمان (Quail)"], 
            ["بادي (0-14 يوم)", "نامي (15-28 يوم)", "ناهي (29-42 يوم)", "ناهي متقدم (43+ يوم)"], 
            18.0, 72.0, has_measurements=False)
    with animal_tabs[6]:
        render_feed_formulation("fish", "أسماك", "🐟", 
            ["البلطي النيلي", "القرموط"], 
            ["زريعة/بادئ", "نمو", "تسمين نهائي", "زريعة متقدمة"], 
            28.0, 68.0, has_measurements=False)
    
    # ===== المختبر المتقدم =====
    with animal_tabs[7]:
        st.markdown('<div class="section-title">🔬 المختبر المتقدم - وفق المعايير الدولية</div>', unsafe_allow_html=True)
        
        # صندوق وارد
        st.markdown("### 📥 صندوق وارد العينات")
        if st.session_state.get("lab_sample"):
            sample = st.session_state["lab_sample"]
            standard = sample.get('standard', {})
            ref = standard.get('reference', 'N/A') if standard else 'N/A'
            st.markdown(f"""
            <div class="inbox-box">
                <div class="inbox-title">📩 عينة واردة من تركيب العلف</div>
                <div class="inbox-item">
                    <b>🐾 الحيوان:</b> {sample['animal']}<br>
                    <b>🧬 السلالة:</b> {sample['breed']}<br>
                    <b>📌 المرحلة:</b> {sample['stage']}<br>
                    <b>📅 العمر:</b> {sample.get('age', 'غير محدد')} شهر<br>
                    <b>⚕️ الحالة:</b> {sample.get('physiological', 'طبيعي')}<br>
                    <b>🥛 إنتاج الحليب:</b> {sample.get('milk_production', 0):.1f} لتر/يوم<br>
                    <b>📊 المرجع القياسي:</b> <span class="nrc-badge">{ref}</span><br>
                    <b>🧪 DP:</b> {sample['dp']:.2f}% | <b>🌽 SE:</b> {sample['se']:.2f} | <b>🧬 CP:</b> {sample.get('cp', 0):.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🧪 تحليل العينة المرسلة", type="primary", use_container_width=True):
                with st.spinner("جاري تحليل العينة المرسلة..."):
                    voice_guide("جاري تحليل العينة المرسلة.")
                    formula = sample.get('formula', {})
                    total_weight = sum(formula.values()) if formula else 100
                    if total_weight > 0 and formula:
                        cp_total, dp_total, se_total = 0.0, 0.0, 0.0
                        comps = []
                        for ing, weight in formula.items():
                            if weight > 0:
                                pct = weight / total_weight * 100
                                feed_data = FLAT_FEED_DB.get(ing, {})
                                cp = feed_data.get("CP", 0.0)
                                dc = feed_data.get("DC", 0.0)
                                se = feed_data.get("SE", 0.0)
                                cp_total += pct * cp / 100
                                dp_total += pct * (cp * dc) / 100
                                se_total += pct * se / 100
                                comps.append({"المادة": ing, "الوزن": weight, "النسبة %": f"{pct:.2f}"})
                        
                        st.session_state["analysis_results"] = {'cp': cp_total, 'dp': dp_total, 'se': se_total}
                        st.session_state["analysis_animal"] = sample['animal']
                        st.session_state["analysis_stage"] = sample['stage']
                        st.session_state["lab_analysis_done"] = True
                        
                        st.success("✅ تم تحليل العينة المرسلة بنجاح!")
                        voice_guide("تم تحليل العينة المرسلة بنجاح.")
                        
                        st.markdown(f"### ⚖️ إجمالي الوزن: **{total_weight:.1f} كجم**")
                        st.dataframe(pd.DataFrame(comps), use_container_width=True, hide_index=True)
                        
                        st.write("#### 🔬 النتائج المحسوبة:")
                        results_df = pd.DataFrame([
                            {"العنصر": "البروتين الخام (CP)", "القيمة": f"{cp_total:.2f}%"},
                            {"العنصر": "البروتين المهضوم (DP)", "القيمة": f"{dp_total:.2f}%"},
                            {"العنصر": "معادل النشاء (SE)", "القيمة": f"{se_total:.2f} وحدة"}
                        ])
                        st.dataframe(results_df, use_container_width=True, hide_index=True)
                        
                        if standard:
                            dp_dev = ((dp_total - standard.get('DP', 0)) / standard.get('DP', 1)) * 100 if standard.get('DP', 0) > 0 else 0
                            se_dev = ((se_total - standard.get('SE', 0)) / standard.get('SE', 1)) * 100 if standard.get('SE', 0) > 0 else 0
                            cp_dev = ((cp_total - standard.get('CP', 0)) / standard.get('CP', 1)) * 100 if standard.get('CP', 0) > 0 else 0
                            
                            dp_grade = "✅ ممتاز" if abs(dp_dev) <= 5 else ("👍 جيد" if abs(dp_dev) <= 10 else "⚠️ يحتاج تحسين")
                            se_grade = "✅ ممتاز" if abs(se_dev) <= 5 else ("👍 جيد" if abs(se_dev) <= 10 else "⚠️ يحتاج تحسين")
                            cp_grade = "✅ ممتاز" if abs(cp_dev) <= 5 else ("👍 جيد" if abs(cp_dev) <= 10 else "⚠️ يحتاج تحسين")
                            
                            st.write("#### 📊 التقييم والمقارنة مع المعايير القياسية")
                            eval_df = pd.DataFrame([
                                {"المقياس": "DP", "المحسوب": f"{dp_total:.2f}%", "القياسي": f"{standard.get('DP', 0):.2f}%", "الانحراف": f"{dp_dev:.1f}%", "التقييم": dp_grade, "المرجع": standard.get('reference', 'N/A')},
                                {"المقياس": "SE", "المحسوب": f"{se_total:.2f}", "القياسي": f"{standard.get('SE', 0):.2f}", "الانحراف": f"{se_dev:.1f}%", "التقييم": se_grade, "المرجع": standard.get('reference', 'N/A')},
                                {"المقياس": "CP", "المحسوب": f"{cp_total:.2f}%", "القياسي": f"{standard.get('CP', 0):.2f}%", "الانحراف": f"{cp_dev:.1f}%", "التقييم": cp_grade, "المرجع": standard.get('reference', 'N/A')}
                            ])
                            st.dataframe(eval_df, use_container_width=True, hide_index=True)
                            
                            notes = []
                            if abs(dp_dev) > 10:
                                notes.append("⚠️ البروتين المهضوم بحاجة لضبط." if dp_dev < 0 else "⚠️ البروتين المهضوم أعلى من المعيار.")
                            if abs(se_dev) > 10:
                                notes.append("⚠️ الطاقة بحاجة لضبط." if se_dev < 0 else "⚠️ الطاقة أعلى من المعيار.")
                            if sample.get('milk_production', 0) > 0:
                                se_per_liter = se_total / sample['milk_production'] if sample['milk_production'] > 0 else 0
                                if se_per_liter < 20:
                                    notes.append("⚠️ الطاقة لكل لتر حليب منخفضة، يوصى بزيادة مصادر الطاقة.")
                                elif se_per_liter > 35:
                                    notes.append("⚠️ الطاقة لكل لتر حليب مرتفعة، يمكن تقليل مصادر الطاقة.")
                            if not notes:
                                notes.append("✅ الخلطة متوازنة وتتوافق مع المعايير القياسية (NRC/INRA/FAO) بشكل ممتاز.")
                            for note in notes:
                                st.markdown(f'<div class="warning-card">{note}</div>', unsafe_allow_html=True)
                            
                            total_grade = "ممتاز" if all([x.startswith("✅") for x in [dp_grade, se_grade, cp_grade]]) else "جيد" if all([x.startswith("✅") or x.startswith("👍") for x in [dp_grade, se_grade, cp_grade]]) else "متوسط"
                            st.metric("⭐ التقدير العام", total_grade)
                            
                            fig = go.Figure()
                            fig.add_trace(go.Bar(x=['DP', 'SE', 'CP'], y=[dp_total, se_total, cp_total], name='المحسوب', marker_color='#2e7d32'))
                            fig.add_trace(go.Bar(x=['DP', 'SE', 'CP'], y=[standard.get('DP',0), standard.get('SE',0), standard.get('CP',0)], name='القياسي (NRC)', marker_color='#1565C0'))
                            fig.update_layout(title="مقارنة القيم المحسوبة مع المعايير القياسية (NRC/INRA/FAO)", barmode='group')
                            st.plotly_chart(fig, use_container_width=True)
                            
                            try:
                                pdf_data = pdf_generator.generate_lab_report(
                                    analysis_results=st.session_state["analysis_results"],
                                    animal_type=sample['animal'],
                                    stage=sample['stage'],
                                    user_name=st.session_state.get("user", {}).get("full_name", "مستخدم"),
                                    standard=standard,
                                    evaluation={'DP': dp_grade, 'SE': se_grade, 'CP': cp_grade},
                                    comps=comps,
                                    total_weight=total_weight,
                                    milk_production=sample.get('milk_production', 0)
                                )
                                st.download_button(
                                    "📥 تحميل تقرير المختبر PDF (مع توقيع المشرف)",
                                    pdf_data,
                                    file_name=f"Lab_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.warning(f"⚠️ تعذر إنشاء PDF: {e}")
                    else:
                        st.error("❌ لا توجد مكونات صالحة في العينة.")
            
            if st.button("🗑️ مسح العينة من الصندوق"):
                st.session_state["lab_sample"] = None
                st.session_state["lab_analysis_done"] = False
                st.rerun()
        else:
            st.info("📭 لا توجد عينات واردة. قم بتركيب علف في تبويب الحيوانات واضغط 'إرسال العينة إلى المختبر'.")
        
        st.markdown("---")
        st.markdown("### 🧪 أو أدخل العينة يدوياً")
        
        lab_animal = st.selectbox("الفصيل:", ["أبقار", "أغنام", "ماعز", "خيول", "إبل", "دواجن لاحم", "دواجن بياض", "سمان", "أسماك"])
        lab_stage = st.selectbox("المرحلة:", list(STANDARD_VALUES.get(lab_animal, {}).keys()))
        standard = STANDARD_VALUES.get(lab_animal, {}).get(lab_stage, {})
        if standard:
            show_standard_reference(lab_animal, lab_stage)
        
        lab_milk = 0
        if lab_animal in ["أبقار", "أغنام", "ماعز", "إبل"] and "حليب" in lab_stage:
            lab_milk = st.number_input("🥛 إنتاج الحليب اليومي (لتر)", min_value=0.0, value=10.0, step=0.5)
        
        lab_inputs = {}
        cols = st.columns(3)
        all_ings = list(FLAT_FEED_DB.keys())
        for idx, ing in enumerate(all_ings):
            with cols[idx % 3]:
                lab_inputs[ing] = st.number_input(f"وزن {ing} (كجم)", min_value=0.0, value=0.0, step=5.0, key=f"lab_manual_{ing}")
        
        if st.button("🧪 تشغيل التحليل اليدوي", type="secondary", use_container_width=True):
            total = sum(lab_inputs.values())
            if total <= 0:
                st.warning("⚠️ الرجاء إدخال أوزان أكبر من الصفر.")
            else:
                cp_total, dp_total, se_total = 0.0, 0.0, 0.0
                comps = []
                for ing, weight in lab_inputs.items():
                    if weight > 0:
                        pct = weight / total * 100
                        feed_data = FLAT_FEED_DB.get(ing, {})
                        cp = feed_data.get("CP", 0.0)
                        dc = feed_data.get("DC", 0.0)
                        se = feed_data.get("SE", 0.0)
                        cp_total += pct * cp / 100
                        dp_total += pct * (cp * dc) / 100
                        se_total += pct * se / 100
                        comps.append({"المادة": ing, "الوزن": weight, "النسبة %": f"{pct:.2f}"})
                
                st.session_state["analysis_results"] = {'cp': cp_total, 'dp': dp_total, 'se': se_total}
                st.session_state["analysis_animal"] = lab_animal
                st.session_state["analysis_stage"] = lab_stage
                st.success("🔬 تم تحليل العينة بنجاح!")
                
                st.markdown(f"### ⚖️ إجمالي الوزن: **{total:.1f} كجم**")
                st.dataframe(pd.DataFrame(comps), use_container_width=True, hide_index=True)
                
                st.write("#### 🔬 النتائج المحسوبة:")
                results_df = pd.DataFrame([
                    {"العنصر": "البروتين الخام (CP)", "القيمة": f"{cp_total:.2f}%"},
                    {"العنصر": "البروتين المهضوم (DP)", "القيمة": f"{dp_total:.2f}%"},
                    {"العنصر": "معادل النشاء (SE)", "القيمة": f"{se_total:.2f} وحدة"}
                ])
                st.dataframe(results_df, use_container_width=True, hide_index=True)
                
                if standard:
                    dp_dev = ((dp_total - standard.get('DP', 0)) / standard.get('DP', 1)) * 100 if standard.get('DP', 0) > 0 else 0
                    se_dev = ((se_total - standard.get('SE', 0)) / standard.get('SE', 1)) * 100 if standard.get('SE', 0) > 0 else 0
                    cp_dev = ((cp_total - standard.get('CP', 0)) / standard.get('CP', 1)) * 100 if standard.get('CP', 0) > 0 else 0
                    
                    dp_grade = "✅ ممتاز" if abs(dp_dev) <= 5 else ("👍 جيد" if abs(dp_dev) <= 10 else "⚠️ يحتاج تحسين")
                    se_grade = "✅ ممتاز" if abs(se_dev) <= 5 else ("👍 جيد" if abs(se_dev) <= 10 else "⚠️ يحتاج تحسين")
                    cp_grade = "✅ ممتاز" if abs(cp_dev) <= 5 else ("👍 جيد" if abs(cp_dev) <= 10 else "⚠️ يحتاج تحسين")
                    
                    st.write("#### 📊 التقييم والمقارنة مع المعايير القياسية")
                    eval_df = pd.DataFrame([
                        {"المقياس": "DP", "المحسوب": f"{dp_total:.2f}%", "القياسي": f"{standard.get('DP', 0):.2f}%", "الانحراف": f"{dp_dev:.1f}%", "التقييم": dp_grade, "المرجع": standard.get('reference', 'N/A')},
                        {"المقياس": "SE", "المحسوب": f"{se_total:.2f}", "القياسي": f"{standard.get('SE', 0):.2f}", "الانحراف": f"{se_dev:.1f}%", "التقييم": se_grade, "المرجع": standard.get('reference', 'N/A')},
                        {"المقياس": "CP", "المحسوب": f"{cp_total:.2f}%", "القياسي": f"{standard.get('CP', 0):.2f}%", "الانحراف": f"{cp_dev:.1f}%", "التقييم": cp_grade, "المرجع": standard.get('reference', 'N/A')}
                    ])
                    st.dataframe(eval_df, use_container_width=True, hide_index=True)
                    
                    notes = []
                    if abs(dp_dev) > 10:
                        notes.append("⚠️ البروتين المهضوم بحاجة لضبط." if dp_dev < 0 else "⚠️ البروتين المهضوم أعلى من المعيار.")
                    if abs(se_dev) > 10:
                        notes.append("⚠️ الطاقة بحاجة لضبط." if se_dev < 0 else "⚠️ الطاقة أعلى من المعيار.")
                    if lab_milk > 0:
                        se_per_liter = se_total / lab_milk if lab_milk > 0 else 0
                        if se_per_liter < 20:
                            notes.append("⚠️ الطاقة لكل لتر حليب منخفضة.")
                        elif se_per_liter > 35:
                            notes.append("⚠️ الطاقة لكل لتر حليب مرتفعة.")
                    if not notes:
                        notes.append("✅ الخلطة متوازنة وتتوافق مع المعايير القياسية.")
                    for note in notes:
                        st.markdown(f'<div class="warning-card">{note}</div>', unsafe_allow_html=True)
                    
                    total_grade = "ممتاز" if all([x.startswith("✅") for x in [dp_grade, se_grade, cp_grade]]) else "جيد" if all([x.startswith("✅") or x.startswith("👍") for x in [dp_grade, se_grade, cp_grade]]) else "متوسط"
                    st.metric("⭐ التقدير العام", total_grade)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=['DP', 'SE', 'CP'], y=[dp_total, se_total, cp_total], name='المحسوب', marker_color='#2e7d32'))
                    fig.add_trace(go.Bar(x=['DP', 'SE', 'CP'], y=[standard.get('DP',0), standard.get('SE',0), standard.get('CP',0)], name='القياسي (NRC)', marker_color='#1565C0'))
                    fig.update_layout(title="مقارنة القيم المحسوبة مع المعايير القياسية (NRC/INRA/FAO)", barmode='group')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    try:
                        pdf_data = pdf_generator.generate_lab_report(
                            analysis_results=st.session_state["analysis_results"],
                            animal_type=lab_animal,
                            stage=lab_stage,
                            user_name=st.session_state.get("user", {}).get("full_name", "مستخدم"),
                            standard=standard,
                            evaluation={'DP': dp_grade, 'SE': se_grade, 'CP': cp_grade},
                            comps=comps,
                            total_weight=total,
                            milk_production=lab_milk
                        )
                        st.download_button(
                            "📥 تحميل تقرير المختبر PDF (مع توقيع المشرف)",
                            pdf_data,
                            file_name=f"Lab_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.warning(f"⚠️ تعذر إنشاء PDF: {e}")

# =====================================================================
# التبويب 1: إدارة المزارع
# =====================================================================
with tabs[1]:
    guide_section("إدارة المزارع", "إدارة مزارع الدجاج.")
    st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج</div>', unsafe_allow_html=True)
    if st.session_state["user_role"] in ["owner", "specialist", "veterinarian", "nutritionist", "breeder"]:
        with st.expander("➕ إضافة دورة"):
            col1, col2 = st.columns(2)
            with col1:
                farm_name = st.text_input("اسم المزرعة")
                initial_birds = st.number_input("عدد الكتاكيت", min_value=1, value=1000, step=100)
            with col2:
                breed = st.selectbox("السلالة", ["Ross 308", "Cobb 500", "محلية"])
                start_date = st.date_input("تاريخ البدء", datetime.now())
            if st.button("💾 إنشاء"):
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
        st.info("🔒 الإضافة متاحة للمالك والمختصين.")
    
    if st.session_state["broiler_farms"]:
        for cid, farm in st.session_state["broiler_farms"].items():
            with st.expander(f"🏠 {farm['farm_name']} - {farm['breed']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("العدد", farm['initial_birds'])
                    st.metric("العمر", f"{farm['age_days']} يوم")
                with col2:
                    st.metric("الوزن", f"{farm['current_weight']:.3f} كجم")
                    st.metric("العلف", f"{farm['total_feed']:.1f} كجم")
                with col3:
                    mortality = (farm['dead_count'] / farm['initial_birds']) * 100 if farm['initial_birds'] > 0 else 0
                    st.metric("النفوق", f"{mortality:.1f}%")
                    st.metric("النافق", farm['dead_count'])
                if st.session_state["user_role"] in ["owner", "specialist", "veterinarian", "nutritionist", "breeder"]:
                    col_up1, col_up2 = st.columns(2)
                    with col_up1:
                        new_weight = st.number_input("الوزن الحالي", min_value=0.01, value=float(farm['current_weight']), step=0.01, key=f"w_{cid}")
                        new_feed = st.number_input("العلف المستهلك", min_value=0.0, value=float(farm['total_feed']), step=1.0, key=f"f_{cid}")
                    with col_up2:
                        new_dead = st.number_input("النافق الإضافي", min_value=0, value=0, step=1, key=f"d_{cid}")
                        new_age = st.number_input("العمر", min_value=0, value=int(farm['age_days']), step=1, key=f"a_{cid}")
                    if st.button(f"📊 تحديث", key=f"up_{cid}"):
                        farm['current_weight'] = new_weight
                        farm['total_feed'] = new_feed
                        farm['dead_count'] += new_dead
                        farm['age_days'] = new_age
                        st.success("✅ تم التحديث")
                        st.rerun()

# =====================================================================
# التبويب 2: بورصة الأسعار
# =====================================================================
with tabs[2]:
    guide_section("بورصة الأسعار", "أسعار المواشي والمنتجات.")
    st.markdown('<div class="section-title">📊 بورصة الأسعار</div>', unsafe_allow_html=True)
    if st.session_state["user_role"] in ["owner", "specialist", "veterinarian", "nutritionist", "breeder"]:
        col1, col2 = st.columns(2)
        with col1:
            for name, price in st.session_state["global_livestock_prices"].items():
                new_price = st.number_input(name, value=float(price), step=5.0, key=f"price_live_{name}")
                st.session_state["global_livestock_prices"][name] = new_price
        with col2:
            for name, price in st.session_state["global_products_prices"].items():
                new_price = st.number_input(name, value=float(price), step=0.5, key=f"price_prod_{name}")
                st.session_state["global_products_prices"][name] = new_price
        for country, data in EXCHANGE_RATES.items():
            new_rate = st.number_input(f"{country} - {data['currency_name']}", value=float(data['rate']), step=1.0, key=f"exchange_{country}")
            EXCHANGE_RATES[country]["rate"] = new_rate
    else:
        st.info("🔒 التعديل متاح للمالك والمختصين.")
        for name, price in st.session_state["global_livestock_prices"].items():
            st.write(f"- {name}: ${price:.2f}")

# =====================================================================
# التبويب 3: المستودعات
# =====================================================================
with tabs[3]:
    guide_section("المستودعات", "إدارة المخزون.")
    st.markdown('<div class="section-title">🏭 المستودعات</div>', unsafe_allow_html=True)
    inv_data = []
    for item, data in st.session_state["inventory"].items():
        inv_data.append({"المادة": item, "الكمية (طن)": data["quantity"], "الحد الأدنى": data["min_threshold"]})
    st.dataframe(pd.DataFrame(inv_data), use_container_width=True)
    if st.session_state["user_role"] in ["owner", "specialist", "veterinarian", "nutritionist", "breeder"]:
        with st.expander("تحديث المخزون"):
            sel = st.selectbox("المادة", list(FLAT_FEED_DB.keys()))
            new_qty = st.number_input("الكمية الجديدة (طن)", min_value=0.0, value=25.0)
            if st.button("تحديث"):
                st.session_state["inventory"][sel]["quantity"] = new_qty
                st.success("✅ تم التحديث")
                st.rerun()

# =====================================================================
# التبويب 4: الإنتاج اليومي
# =====================================================================
with tabs[4]:
    guide_section("الإنتاج اليومي", "تسجيل الإنتاج اليومي.")
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
    if st.session_state["daily_production_log"]:
        st.dataframe(pd.DataFrame(st.session_state["daily_production_log"]), use_container_width=True)

# =====================================================================
# التبويب 5: التنبيهات
# =====================================================================
with tabs[5]:
    guide_section("التنبيهات", "تنبيهات المخزون والإنتاج.")
    st.markdown('<div class="section-title">🔔 التنبيهات</div>', unsafe_allow_html=True)
    warnings = InventoryManager.check_stock_levels()
    if warnings:
        for item, info in warnings.items():
            st.warning(f"{item}: {info['status']}")
    else:
        st.success("✅ لا توجد تنبيهات")

# =====================================================================
# التبويب 6: المراجع العلمية
# =====================================================================
with tabs[6]:
    guide_section("المراجع", "مصادر معتمدة.")
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
    for cat_key, cat_data in ScientificReferenceSystem.REFERENCES.items():
        with st.expander(f"{cat_data['icon']} {cat_data['title']}"):
            for ref in cat_data.get("references", []):
                st.markdown(f"""
                <div style='background:#f8f9fa; padding:12px; border-radius:8px; margin-bottom:8px; border-right:4px solid #2e7d32;'>
                    <b>{ref.get('title', '')}</b><br>
                    👤 {ref.get('authors', '')}<br>
                    📅 {ref.get('year', '')} | 📚 {ref.get('publisher', '')}<br>
                    <small>{ref.get('summary', '')}</small>
                    <span class="nrc-badge">{ref.get('id', '')}</span>
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
# التبويب 7: المساعدة
# =====================================================================
with tabs[7]:
    guide_section("المساعدة", "دليل سريع.")
    st.markdown('<div class="section-title">💡 المساعدة</div>', unsafe_allow_html=True)
    st.markdown("""
    1. اختر نوع الحيوان والمرحلة.
    2. حدد العمر والحالة الفسيولوجية.
    3. أدخل إنتاج الحليب (للأبقار الحلابة).
    4. ستظهر المعايير القياسية NRC/INRA/FAO تلقائياً.
    5. اختر المكونات واضغط تشغيل.
    6. استخدم المختبر للتحليل والمقارنة مع المعايير.
    7. أرسل العينة إلى المختبر بضغطة زر.
    """)
    if st.button("🔊 استمع"):
        voice_guide("مرحباً، هذا دليل منصة تاور نولجي. اختر الحيوان والمكونات، ثم شغل المحرك.")

# =====================================================================
# التبويب 8: دليل المستخدم
# =====================================================================
with tabs[8]:
    guide_section("دليل المستخدم", "شرح مفصل.")
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="manual-book">
    <div class="book-chapter">📘 الفصل 1: مقدمة</div>
    <div class="book-body">
    تاور نولجي Tawornology العلمية منصة متكاملة لتركيب الأعلاف وفق المعايير الدولية NRC, INRA, FAO.
    </div>
    <div class="book-chapter">📗 الفصل 2: تركيب العلف</div>
    <div class="book-body">
    1. اختر الحيوان<br>2. حدد السلالة والمرحلة<br>3. أدخل العمر والحالة<br>4. أدخل إنتاج الحليب (للحلابة)<br>5. راجع المعايير القياسية<br>6. اختر المكونات<br>7. اضغط تشغيل
    </div>
    <div class="book-chapter">📕 الفصل 3: المختبر</div>
    <div class="book-body">
    استخدم صندوق وارد لاستقبال العينات من التركيب، أو أدخل يدوياً. قارن نتائجك مع المعايير الدولية NRC.
    </div>
    <div class="book-chapter">📙 الفصل 4: المراجع</div>
    <div class="book-body">
    يحتوي على مراجع NRC (2001, 2007, 1994), INRA (2007), FAO (2018) المعتمدة عالمياً.
    </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# التبويبات الإضافية للمالك
# =====================================================================
if st.session_state["user_role"] == "owner":
    with tabs[9]:
        st.markdown('<div class="section-title">🧾 الفواتير</div>', unsafe_allow_html=True)
        st.info("قيد التطوير")
    
    with tabs[10]:
        st.markdown('<div class="section-title">📊 التقارير</div>', unsafe_allow_html=True)
        st.info("قيد التطوير")
    
    with tabs[11]:
        st.markdown('<div class="section-title">📧 إرسال الكود</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])
        with col1:
            email = st.text_input("البريد:", value=OWNER_EMAIL)
        with col2:
            if st.button("📤 إرسال", use_container_width=True):
                if email and '@' in email:
                    if email.strip().lower() == OWNER_EMAIL.strip().lower():
                        with st.spinner("جاري الإرسال..."):
                            success, msg = send_code_to_email(email)
                            st.success(msg) if success else st.error(msg)
                    else:
                        st.error(f"❌ الإرسال مسموح فقط للبريد: {OWNER_EMAIL}")
                else:
                    st.warning("⚠️ يرجى إدخال بريد صحيح")
        st.caption("ℹ️ يتم استخدام كلمة المرور المحفوظة: kccq khzn enlx bpcy")

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
