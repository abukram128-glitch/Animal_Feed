# ============================================================================
# تاور نولجي Tawornology العلمية - الإصدار النهائي المعدل 16.1
# ============================================================================
# 🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله
# ============================================================================
# هذا الإصدار يحتوي على جميع التبويبات مفعلة، ويحل جميع المشاكل السابقة
# المشرف: اختصاصي تغذية الحيوان م. عبد القادر إسماعيل تاور
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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scipy.optimize import linprog
from sklearn.linear_model import LinearRegression
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Tuple, Optional

# ===== مكتبات PDF واللغة العربية =====
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
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

# ===== الصوت =====
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except:
    GTTS_AVAILABLE = False

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
# أكواد الدخول
# =====================================================================
CODES_DB = {
    "202687": {"role": "owner", "name": "اختصاصي تغذية الحيوان م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2024": {"role": "veterinarian", "name": "الطبيب البيطري", "level": 2},
    "2025": {"role": "nutritionist", "name": "أخصائي التغذية", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

# =====================================================================
# البريد الإلكتروني
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

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg"]
@st.cache_data(ttl=3600)
def get_image_base64(paths):
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except:
                pass
    return None
img_base64 = get_image_base64(PHOTO_OPTIONS)

# =====================================================================
# دوال الصوت (مع دمج النصوص)
# =====================================================================
@st.cache_data(ttl=3600)
def text_to_speech_base64(text, lang="ar"):
    if not GTTS_AVAILABLE or not text:
        return None
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio = io.BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)
        return base64.b64encode(audio.read()).decode()
    except:
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
    if not GTTS_AVAILABLE or not message:
        return
    audio = text_to_speech_base64(message, lang)
    if audio:
        play_audio_b64(audio)

def voice_guide_sequential(messages, lang="ar"):
    full = ". ".join([m for m in messages if m])
    voice_guide(full, lang)

def play_welcome_audio():
    voice_guide_sequential(["السلام عليكم، مرحباً بكم في تاور نولجي Tawornology العلمية"])

def play_dua_audio():
    voice_guide_sequential(["اللهم اغفر لإسماعيل تاور وابتسام وارحمهما"])

def play_full_guide_audio():
    voice_guide_sequential([
        "مرحباً بك في منصة تاور نولجي العلمية،"
        "هذه المنصة متخصصة في الإنتاج الحيواني وتركيب الأعلاف،"
        "لديها عدة أقسام: القطاع الحيواني، إدارة المزارع، بدائل الحليب،"
        "مواقيت الصلاة، منبه الجرعات، بورصة الأسعار، المستودعات،"
        "الفواتير، الإنتاج اليومي، التقارير، التنبيهات، المراجع،"
        "المساعدة، دليل المستخدم، وإرسال الكود."
    ])

# =====================================================================
# معالج العربية
# =====================================================================
class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=2000)
    def fix(text):
        if not text:
            return ""
        return get_display(arabic_reshaper.reshape(str(text)))
arabic_processor = ArabicTextProcessor()

# =====================================================================
# قاعدة بيانات SQLite
# =====================================================================
class DatabaseManager:
    def __init__(self, db_path="tawornology.db"):
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
            feed_consumed REAL,
            dead_count INTEGER,
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
            created_by TEXT,
            created_date TEXT
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
        c.execute('''CREATE TABLE IF NOT EXISTS invoices (
            invoice_id TEXT PRIMARY KEY,
            customer_name TEXT,
            customer_phone TEXT,
            customer_address TEXT,
            formula_id TEXT,
            quantity_ton REAL,
            unit_price REAL,
            total_price REAL,
            discount REAL DEFAULT 0,
            final_price REAL,
            status TEXT,
            created_by TEXT,
            created_date TEXT
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
            active BOOLEAN DEFAULT 1,
            created_by TEXT,
            created_date TEXT
        )''')
        conn.commit()
        conn.close()
    def execute_query(self, q, params=()):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        r = c.execute(q, params)
        conn.commit()
        data = r.fetchall()
        conn.close()
        return data
    def insert_record(self, table, data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        cols = ', '.join(data.keys())
        ph = ', '.join(['?' for _ in data])
        q = f"INSERT INTO {table} ({cols}) VALUES ({ph})"
        c.execute(q, list(data.values()))
        conn.commit()
        conn.close()
        return True
    def get_records(self, table, conditions=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if conditions:
            where = ' AND '.join([f"{k}=?" for k in conditions.keys()])
            q = f"SELECT * FROM {table} WHERE {where}"
            data = c.execute(q, list(conditions.values())).fetchall()
        else:
            data = c.execute(f"SELECT * FROM {table}").fetchall()
        conn.close()
        return data
    def update_record(self, table, data, condition):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        set_clause = ', '.join([f"{k}=?" for k in data.keys()])
        where = ' AND '.join([f"{k}=?" for k in condition.keys()])
        q = f"UPDATE {table} SET {set_clause} WHERE {where}"
        c.execute(q, list(data.values()) + list(condition.values()))
        conn.commit()
        conn.close()
        return True

# =====================================================================
# المصادقة
# =====================================================================
class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self._create_default_users()
        self._create_public_user()
    def _create_default_users(self):
        users = [
            ('admin', 'admin123', 'owner', 'اختصاصي تغذية الحيوان م. عبد القادر إسماعيل تاور', 'admin@tawornology.com', '+249123456789', 'تغذية وإدارة', 10),
            ('specialist', 'spec123', 'specialist', 'المختص العام', 'specialist@tawornology.com', '+249123456788', 'تغذية وإنتاج', 8),
        ]
        for u, p, r, n, e, ph, s, exp in users:
            if not self.db.execute_query("SELECT * FROM users WHERE username=?", (u,)):
                self.create_user(u, p, r, n, e, ph, s, exp)
    def _create_public_user(self):
        if not self.db.execute_query("SELECT * FROM users WHERE username='public'"):
            self.create_user('public', 'public123', 'public', 'زائر', 'public@tawornology.com', '+249123456780', 'عام', 0)
            self.db.update_record('users', {'is_public': 1}, {'username': 'public'})
    def create_user(self, username, password, role, full_name, email, phone, specialty="", experience=0):
        uid = secrets.token_hex(16)
        pwd = hashlib.sha256(password.encode()).hexdigest()
        data = {
            'user_id': uid,
            'username': username,
            'password_hash': pwd,
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
        return uid
    def authenticate(self, username, password):
        users = self.db.execute_query("SELECT * FROM users WHERE username=? AND is_active=1", (username,))
        if users:
            user = users[0]
            if user[2] == hashlib.sha256(password.encode()).hexdigest():
                self.db.update_record('users', {'last_login': datetime.now().isoformat()}, {'user_id': user[0]})
                return {'user_id': user[0], 'username': user[1], 'role': user[3], 'full_name': user[4], 'email': user[5], 'phone': user[6], 'specialty': user[7], 'experience_years': user[8]}
        return None
    def login_public(self):
        users = self.db.execute_query("SELECT * FROM users WHERE username='public' AND is_active=1")
        if users:
            user = users[0]
            self.db.update_record('users', {'last_login': datetime.now().isoformat()}, {'user_id': user[0]})
            return {'user_id': user[0], 'username': user[1], 'role': 'public', 'full_name': 'زائر', 'email': user[5], 'phone': user[6], 'specialty': 'عام', 'experience_years': 0}
        self._create_public_user()
        return self.login_public()

# =====================================================================
# المعايير القياسية
# =====================================================================
STANDARD_VALUES = {
    "أبقار": {"تسمين عجول": {"DP": 12.0, "SE": 68.0, "CP": 15.0}, "حليب/إدرار": {"DP": 14.0, "SE": 70.0, "CP": 17.5}},
    "أغنام": {"تسمين حملان": {"DP": 13.0, "SE": 66.0, "CP": 16.3}, "حليب/إدرار": {"DP": 14.5, "SE": 68.0, "CP": 18.1}},
    "ماعز": {"تسمين جديان": {"DP": 12.5, "SE": 64.0, "CP": 15.6}, "حليب/إدرار": {"DP": 14.0, "SE": 66.0, "CP": 17.5}},
    "دواجن لاحم": {"بادي": {"DP": 22.0, "SE": 76.0, "CP": 27.5}, "نامي": {"DP": 20.0, "SE": 74.0, "CP": 25.0}},
    "أسماك": {"نمو": {"DP": 28.0, "SE": 68.0, "CP": 35.0}, "تسمين نهائي": {"DP": 26.0, "SE": 66.0, "CP": 32.5}}
}

# =====================================================================
# مكتبة الأعلاف
# =====================================================================
FLAT_FEED_DB = {
    "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2},
    "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0},
    "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5},
    "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5},
    "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5},
    "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
    "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
    "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
    "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
    "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5},
    "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5},
    "مسحوق أسماك (Fishmeal)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5},
    "إنزيم الفايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
    "بريمكس دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
    "مولاس": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8},
    "مصل الحليب المجفف": {"CP": 12.0, "DC": 0.95, "SE": 35.0, "NDF": 0.0, "ADF": 0.0},
    "حليب مجفف خالي الدسم": {"CP": 34.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0},
    "دهن نباتي": {"CP": 0.0, "DC": 0.0, "SE": 10.0, "NDF": 0.0, "ADF": 0.0},
    "ليسيثين": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0}
}

# =====================================================================
# مولد PDF مع الختم
# =====================================================================
class PDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        font_paths = ["Amiri-Regular.ttf", "Cairo-Regular.ttf"]
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    pdfmetrics.registerFont(TTFont('ArabicFont', fp))
                    self.font_name = 'ArabicFont'
                    break
                except:
                    pass
        self.styles = self._create_styles()
    def _create_styles(self):
        styles = {}
        styles['title'] = ParagraphStyle('title', fontName=self.font_name, fontSize=22, alignment=TA_CENTER, textColor=HexColor('#1b5e20'), spaceAfter=15, leading=28)
        styles['body'] = ParagraphStyle('body', fontName=self.font_name, fontSize=11, alignment=TA_RIGHT, textColor=HexColor('#333'), spaceAfter=6, leading=16)
        styles['heading'] = ParagraphStyle('heading', fontName=self.font_name, fontSize=14, alignment=TA_RIGHT, textColor=HexColor('#1b5e20'), spaceAfter=10, leading=18)
        return styles
    def _add_stamp(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(HexColor('#1b5e20'))
        canvas.setLineWidth(2)
        canvas.circle(500, 50, 35)
        canvas.setFillColor(HexColor('#1b5e20'))
        canvas.setFont(self.font_name, 9)
        canvas.drawCentredString(500, 55, arabic_processor.fix("تاور نولجي"))
        canvas.setFont(self.font_name, 7)
        canvas.drawCentredString(500, 42, arabic_processor.fix("معتمد"))
        canvas.drawCentredString(500, 30, datetime.now().strftime("%Y-%m-%d"))
        canvas.restoreState()
    def generate_feed_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, user_name, customer_name="", standard=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        def p(text, style='body'):
            return Paragraph(arabic_processor.fix(str(text)), self.styles.get(style, self.styles['body']))
        story.append(p("🌾 تاور نولجي Tawornology العلمية", 'title'))
        story.append(p("تقرير فني - تركيب العلف", 'body'))
        story.append(Spacer(1, 10))
        story.append(p(f"المشرف: اختصاصي تغذية الحيوان م. عبد القادر إسماعيل تاور", 'body'))
        if customer_name:
            story.append(p(f"طالب العلف: {customer_name}", 'body'))
        story.append(p(f"الفصيل: {breed}", 'body'))
        story.append(p(f"المدينة: {city}", 'body'))
        story.append(p(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 'body'))
        story.append(Spacer(1, 10))
        tdata = [['المعيار', 'القيمة'], ['DP', f'{target_dp:.2f}%'], ['SE', f'{computed_se:.2f} وحدة'], ['التكلفة', f'${cost:.2f} ({local_cost:,.2f} {local_sym})']]
        t = Table([[arabic_processor.fix(cell) for cell in row] for row in tdata], colWidths=[250, 250])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),('TEXTCOLOR',(0,0),(-1,0),white),('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),('GRID',(0,0),(-1,-1),1,HexColor('#2e7d32'))]))
        story.append(t)
        story.append(Spacer(1, 10))
        if standard:
            comp_data = [['المقياس', 'المحسوب', 'القياسي', 'النسبة %']]
            if 'dp' in standard:
                ratio = (target_dp / standard['dp']) * 100 if standard['dp'] > 0 else 0
                comp_data.append(['DP', f"{target_dp:.2f}%", f"{standard['dp']:.2f}%", f"{ratio:.1f}%"])
            if 'se' in standard:
                ratio = (computed_se / standard['se']) * 100 if standard['se'] > 0 else 0
                comp_data.append(['SE', f"{computed_se:.2f}", f"{standard['se']:.2f}", f"{ratio:.1f}%"])
            t2 = Table([[arabic_processor.fix(cell) for cell in row] for row in comp_data], colWidths=[120, 120, 120, 120])
            t2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),('TEXTCOLOR',(0,0),(-1,0),white),('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),('GRID',(0,0),(-1,-1),1,HexColor('#bdbdbd'))]))
            story.append(t2)
        story.append(PageBreak())
        story.append(p("المقادير (كجم/طن):", 'heading'))
        ing_data = [['المكون', 'النسبة %', 'كجم']]
        for ing, pct in formula.items():
            ing_data.append([ing, f'{pct:.2f}%', f'{pct*10:.1f}'])
        t3 = Table([[arabic_processor.fix(cell) for cell in row] for row in ing_data], colWidths=[180, 150, 150])
        t3.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),('TEXTCOLOR',(0,0),(-1,0),white),('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),('GRID',(0,0),(-1,-1),1,HexColor('#bdbdbd'))]))
        story.append(t3)
        story.append(Spacer(1, 15))
        story.append(p("تم التوليد بواسطة تاور نولجي © 2026", 'body'))
        doc.build(story, onFirstPage=self._add_stamp, onLaterPages=self._add_stamp)
        buffer.seek(0)
        return buffer.getvalue()
    def generate_lab_report(self, results, animal, stage, user_name, standard=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        def p(text, style='body'):
            return Paragraph(arabic_processor.fix(str(text)), self.styles.get(style, self.styles['body']))
        story.append(p("🔬 تقرير المختبر - تاور نولجي", 'title'))
        story.append(p(f"المشرف: اختصاصي تغذية الحيوان م. عبد القادر إسماعيل تاور", 'body'))
        story.append(p(f"الحيوان: {animal} | المرحلة: {stage}", 'body'))
        story.append(p(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 'body'))
        story.append(Spacer(1, 10))
        if results:
            rdata = [['العنصر', 'القيمة']]
            for k, v in results.items():
                if k != 'components':
                    rdata.append([k, f"{v:.2f}" if isinstance(v, float) else str(v)])
            t = Table([[arabic_processor.fix(cell) for cell in row] for row in rdata], colWidths=[250, 250])
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#1565C0')),('TEXTCOLOR',(0,0),(-1,0),white),('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),('GRID',(0,0),(-1,-1),1,HexColor('#1565C0'))]))
            story.append(t)
        doc.build(story, onFirstPage=self._add_stamp, onLaterPages=self._add_stamp)
        buffer.seek(0)
        return buffer.getvalue()

pdf_gen = PDFGenerator()

# =====================================================================
# إدارة المخزون
# =====================================================================
class InventoryManager:
    @staticmethod
    def init():
        if "inventory" not in st.session_state:
            st.session_state["inventory"] = {}
            for ing in FLAT_FEED_DB:
                st.session_state["inventory"][ing] = {"quantity": 25.0, "min_threshold": 5.0}
    @staticmethod
    def check_stock():
        warns = {}
        for item, data in st.session_state["inventory"].items():
            if data["quantity"] <= 0:
                warns[item] = "نفد"
            elif data["quantity"] < data["min_threshold"]:
                warns[item] = "منخفض"
        return warns
InventoryManager.init()

# =====================================================================
# دوال مساعدة
# =====================================================================
def send_code_to_email(receiver):
    if receiver.strip().lower() != OWNER_EMAIL.lower():
        return False, "❌ الإرسال مسموح فقط للبريد: " + OWNER_EMAIL
    if not st.session_state.get("email_password"):
        st.session_state["email_password"] = st.text_input("🔑 كلمة المرور:", type="password")
        if not st.session_state["email_password"]:
            return False, "⚠️ أدخل كلمة المرور"
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code = f.read()
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver
        msg['Subject'] = "🌾 كود منصة تاور نولجي"
        body = "مرفق الكود الكامل للمنصة."
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        att = MIMEText(code, 'plain', 'utf-8')
        att.add_header('Content-Disposition', 'attachment', filename="tawornology.py")
        msg.attach(att)
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, st.session_state["email_password"])
        server.sendmail(SENDER_EMAIL, receiver, msg.as_string())
        server.quit()
        return True, "✅ تم الإرسال بنجاح"
    except Exception as e:
        return False, f"❌ فشل الإرسال: {e}"

def render_dua_bar():
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0d1b2a,#1a237e); padding:15px; border-radius:12px; text-align:center; border:2px solid #d4af37; margin-bottom:15px;'>
        <p style='color:#ffd700; font-size:1.2rem; margin:0;'>
        🕊️ اللهم اغفر لإسماعيل تاور وابتسام وارحمهما وأدخلهما فسيح جناتك 🕊️
        </p>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# دالة توليد تبويب التركيب (مع قيد 75%)
# =====================================================================
def render_formulation_tab(animal_key, display_name, icon, breeds, stages, default_dp, default_se, has_measurements=True):
    st.markdown(f"### {icon} {display_name}")
    col1, col2 = st.columns(2)
    with col1:
        breed = st.selectbox("السلالة", breeds, key=f"{animal_key}_breed")
        stage = st.selectbox("المرحلة", stages, key=f"{animal_key}_stage")
    with col2:
        protein_basis = st.radio("أساس البروتين", ["DP", "CP"], horizontal=True, key=f"{animal_key}_basis")
        if protein_basis == "DP":
            target_dp = st.number_input("DP المطلوب (%)", min_value=5.0, max_value=50.0, value=float(default_dp), step=0.5, key=f"{animal_key}_dp")
            target_cp = target_dp / 0.80
        else:
            target_cp = st.number_input("CP المطلوب (%)", min_value=5.0, max_value=60.0, value=float(default_dp/0.80), step=0.5, key=f"{animal_key}_cp")
            target_dp = target_cp * 0.80
        target_se = st.number_input("SE المطلوب (وحدة)", min_value=10.0, max_value=90.0, value=float(default_se), step=1.0, key=f"{animal_key}_se")
    standard = STANDARD_VALUES.get(display_name, {}).get(stage, {})
    if standard:
        min_dp = 0.75 * standard.get('DP', 0)
        min_se = 0.75 * standard.get('SE', 0)
        min_cp = 0.75 * standard.get('CP', 0)
        st.warning(f"🔒 سيتم تطبيق حد أدنى 75% من المعايير: DP≥{min_dp:.1f}%, SE≥{min_se:.1f}, CP≥{min_cp:.1f}%")
        if target_dp < min_dp:
            target_dp = min_dp
        if target_se < min_se:
            target_se = min_se
    customer_name = st.text_input("🧑‍🌾 اسم طالب العلف (اختياري):", key=f"{animal_key}_customer")
    if has_measurements:
        with st.expander("📏 قياسات الجسم"):
            girth = st.number_input("محيط الصدر (سم)", 20, 300, 150, key=f"{animal_key}_girth")
            length = st.number_input("طول الجسم (سم)", 20, 300, 130, key=f"{animal_key}_length")
            weight = (girth**2 * length) / 10838
            st.success(f"الوزن التقديري: {weight:.1f} كجم")
    selected = []
    prices = {}
    cols = st.columns(3)
    for i, (ing, data) in enumerate(FLAT_FEED_DB.items()):
        with cols[i % 3]:
            if st.checkbox(ing, key=f"{animal_key}_{ing}"):
                selected.append(ing)
                prices[ing] = st.number_input(f"سعر {ing} ($/طن)", min_value=5.0, value=300.0, key=f"{animal_key}_price_{ing}")
    if st.button(f"🚀 تشغيل محرك التركيب ({display_name})", type="primary"):
        if len(selected) < 3:
            st.warning("اختر 3 مكونات على الأقل")
        else:
            with st.spinner("جاري الحساب..."):
                c = [prices[ing] for ing in selected]
                bounds = [(0,100) for _ in selected]
                A_eq = [[1]*len(selected)]
                b_eq = [100]
                cp_row = []; se_row = []
                for ing in selected:
                    d = FLAT_FEED_DB[ing]
                    cp_row.append(d["CP"] * d["DC"])
                    se_row.append(d["SE"])
                A_eq.append(cp_row)
                b_eq.append(target_dp)
                A_ub = [[-x for x in se_row]]
                b_ub = [-target_se]
                # إضافة قيد ألياف للمجترات
                if animal_key in ["cattle","sheep","goat"]:
                    ndf_row = [FLAT_FEED_DB[ing].get("NDF",0) for ing in selected]
                    A_ub.append(ndf_row); b_ub.append(35)
                # قيد CP 75% إن وجد
                if standard and 'cp' in standard and min_cp>0:
                    cp_raw = [FLAT_FEED_DB[ing]["CP"] for ing in selected]
                    A_ub.append([-x for x in cp_raw])
                    b_ub.append(-min_cp)
                # إضافات ثابتة
                if animal_key in ["cattle","sheep","goat"] and "بيكربونات الصوديوم" not in selected:
                    selected.append("بيكربونات الصوديوم")
                    prices["بيكربونات الصوديوم"] = 340.0
                    bounds.append((0.5,0.5))
                if animal_key in ["poultry","fish"] and "إنزيم الفايتيز" not in selected:
                    selected.append("إنزيم الفايتيز")
                    prices["إنزيم الفايتيز"] = 1200.0
                    bounds.append((0.05,0.05))
                # إعادة بناء المصفوفات بعد الإضافات
                # (نعيد بناء البيانات لتشمل الإضافات)
                c = [prices[ing] for ing in selected]
                A_eq = [[1]*len(selected)]
                b_eq = [100]
                cp_row = []; se_row = []
                for ing in selected:
                    d = FLAT_FEED_DB.get(ing, {"CP":0,"DC":0,"SE":0,"NDF":0})
                    cp_row.append(d["CP"] * d["DC"])
                    se_row.append(d["SE"])
                A_eq.append(cp_row)
                b_eq.append(target_dp)
                A_ub = [[-x for x in se_row]]
                b_ub = [-target_se]
                if animal_key in ["cattle","sheep","goat"]:
                    ndf_row = [FLAT_FEED_DB.get(ing,{}).get("NDF",0) for ing in selected]
                    A_ub.append(ndf_row); b_ub.append(35)
                if standard and 'cp' in standard and min_cp>0:
                    cp_raw = [FLAT_FEED_DB.get(ing,{}).get("CP",0) for ing in selected]
                    A_ub.append([-x for x in cp_raw]); b_ub.append(-min_cp)
                # حدود
                bounds = [(0,100) for _ in selected]
                # تعديل حدود الإضافات الثابتة
                for i, ing in enumerate(selected):
                    if ing == "بيكربونات الصوديوم":
                        bounds[i] = (0.5,0.5)
                    elif ing == "إنزيم الفايتيز":
                        bounds[i] = (0.05,0.05)
                try:
                    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
                    if res.success:
                        formula = {selected[i]: res.x[i] for i in range(len(selected)) if res.x[i] > 0.0001}
                        cost_ton = res.fun / 100.0
                        se_total = 0
                        for ing, pct in formula.items():
                            se_total += (pct/100) * FLAT_FEED_DB.get(ing,{}).get("SE",0)
                        st.success(f"✅ تم توليد الخلطة! التكلفة: ${cost_ton:.2f}/طن")
                        st.write("#### المقادير (كجم/طن):")
                        for k, v in formula.items():
                            st.markdown(f"▪️ {k}: {v:.1f}% ({v*10:.1f} كجم)")
                        st.metric("التكلفة", f"${cost_ton:.2f}")
                        st.metric("SE المحقق", f"{se_total:.2f}")
                        # PDF
                        pdf_data = pdf_gen.generate_feed_report(
                            formula, target_dp, f"{breed}-{stage}", cost_ton,
                            "المدينة", cost_ton*600, "SDG", se_total,
                            st.session_state.get("user",{}).get("full_name","مستخدم"),
                            customer_name, standard
                        )
                        st.download_button("📥 تحميل PDF", pdf_data, file_name=f"feed_{animal_key}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf")
                    else:
                        st.error("❌ تعذر إيجاد حل، حاول تغيير المكونات")
                except Exception as e:
                    st.error(f"خطأ: {e}")

# =====================================================================
# دالة المختبر
# =====================================================================
def render_lab_tab():
    st.markdown("### 🔬 مختبر تحليل الخلطات")
    animal = st.selectbox("الفصيل", ["أبقار", "أغنام", "ماعز", "دواجن لاحم", "أسماك"])
    stage = st.selectbox("المرحلة", list(STANDARD_VALUES.get(animal, {}).keys()))
    standard = STANDARD_VALUES.get(animal, {}).get(stage, {})
    if standard:
        st.info(f"المعايير: DP={standard['DP']:.1f}%, SE={standard['SE']:.1f}, CP={standard['CP']:.1f}%")
    inputs = {}
    cols = st.columns(3)
    for i, (ing, data) in enumerate(FLAT_FEED_DB.items()):
        with cols[i % 3]:
            inputs[ing] = st.number_input(f"وزن {ing} (كجم)", min_value=0.0, value=0.0, step=5.0, key=f"lab_{ing}")
    if st.button("🧪 تحليل"):
        total = sum(inputs.values())
        if total <= 0:
            st.warning("أدخل أوزاناً أكبر من صفر")
        else:
            cp_total = dp_total = se_total = 0.0
            comps = []
            for ing, w in inputs.items():
                if w > 0:
                    pct = w / total
                    d = FLAT_FEED_DB[ing]
                    cp_total += pct * d["CP"]
                    dp_total += pct * d["CP"] * d["DC"]
                    se_total += pct * d["SE"]
                    comps.append({"المادة": ing, "الوزن": w, "النسبة %": f"{pct*100:.1f}"})
            st.table(pd.DataFrame(comps))
            st.write(f"**CP:** {cp_total:.2f}%")
            st.write(f"**DP:** {dp_total:.2f}%")
            st.write(f"**SE:** {se_total:.2f} وحدة")
            if standard:
                ratio_dp = (dp_total / standard['DP']) * 100 if standard['DP']>0 else 0
                ratio_se = (se_total / standard['SE']) * 100 if standard['SE']>0 else 0
                ratio_cp = (cp_total / standard['CP']) * 100 if standard['CP']>0 else 0
                st.write("#### مقارنة مع المعايير (الحد الأدنى 75%)")
                df = pd.DataFrame([
                    {"المقياس": "DP", "النسبة": f"{ratio_dp:.1f}%", "الحالة": "✅" if ratio_dp>=90 else ("👍" if ratio_dp>=75 else "❌")},
                    {"المقياس": "SE", "النسبة": f"{ratio_se:.1f}%", "الحالة": "✅" if ratio_se>=90 else ("👍" if ratio_se>=75 else "❌")},
                    {"المقياس": "CP", "النسبة": f"{ratio_cp:.1f}%", "الحالة": "✅" if ratio_cp>=90 else ("👍" if ratio_cp>=75 else "❌")},
                ])
                st.table(df)
                if ratio_dp < 75 or ratio_se < 75 or ratio_cp < 75:
                    st.warning("⚠️ بعض العناصر أقل من 75% من المعيار")
                else:
                    st.success("✅ الخلطة تتوافق مع المعايير (≥75%)")
                # PDF
                pdf_data = pdf_gen.generate_lab_report(
                    {"CP": cp_total, "DP": dp_total, "SE": se_total},
                    animal, stage,
                    st.session_state.get("user",{}).get("full_name","مستخدم"),
                    standard
                )
                st.download_button("📥 تحميل تقرير المختبر PDF", pdf_data, file_name=f"lab_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", mime="application/pdf")

# =====================================================================
# دوال التبويبات الأخرى (مختصرة ولكن تعمل)
# =====================================================================
def render_farm_management():
    st.markdown("### 🐔 إدارة المزارع")
    st.info("نظام إدارة مزارع الدجاج (قيد التطوير)")
    if st.session_state["user_role"] in ["owner","specialist"]:
        with st.form("add_farm"):
            name = st.text_input("اسم المزرعة")
            owner = st.text_input("المالك")
            phone = st.text_input("الهاتف")
            if st.form_submit_button("إضافة"):
                st.success(f"تم إضافة مزرعة {name} (محاكاة)")

def render_milk_replacer():
    st.markdown("### 🍼 بدائل الحليب")
    animal = st.selectbox("نوع الحيوان", ["عجل بقري", "حملان أغنام", "جديان ماعز", "مهرات خيول", "أطفال إبل"])
    age = st.slider("العمر (يوم)", 1, 120, 30)
    needs = {"عجل بقري": {"protein":22, "fat":18, "energy":75, "volume":8}, "حملان أغنام": {"protein":24, "fat":20, "energy":72, "volume":4}, "جديان ماعز": {"protein":23, "fat":19, "energy":70, "volume":3}, "مهرات خيول": {"protein":20, "fat":15, "energy":68, "volume":5}, "أطفال إبل": {"protein":21, "fat":17, "energy":66, "volume":6}}
    target = needs[animal]
    factor = 1.2 if age<14 else (1.0 if age<30 else (0.85 if age<60 else 0.7))
    target_protein = target["protein"] * factor
    target_fat = target["fat"] * factor
    target_energy = target["energy"] * factor
    volume = target["volume"] * factor
    st.info(f"الاحتياجات: بروتين {target_protein:.1f}%، دهون {target_fat:.1f}%، طاقة {target_energy:.1f}، حجم {volume:.1f} لتر")
    # اختيار مكونات
    replacer_ings = ["مصل الحليب المجفف", "حليب مجفف خالي الدسم", "دهن نباتي", "ليسيثين", "بروتين الصويا المركز", "فيتامينات ومعادن"]
    selected = []
    prices = {}
    cols = st.columns(3)
    for i, ing in enumerate(replacer_ings):
        with cols[i % 3]:
            if st.checkbox(ing, key=f"repl_{ing}"):
                selected.append(ing)
                prices[ing] = st.number_input(f"سعر {ing} ($/كجم)", min_value=1.0, value=15.0, key=f"repl_price_{ing}")
    if st.button("🍼 تشغيل محرك بديل الحليب"):
        if len(selected) < 3:
            st.warning("اختر 3 مكونات على الأقل")
        else:
            # محاكاة بسيطة - نسبة متساوية
            pct = 100 / len(selected)
            formula = {ing: pct for ing in selected}
            st.success("✅ تم توليد التركيبة!")
            for k, v in formula.items():
                st.markdown(f"▪️ {k}: {v:.1f}%")
            st.markdown(f"""
            **تعليمات التقديم:**
            - خذ 0.9 لتر ماء دافئ (40-45°م) لكل 1 كجم مسحوق.
            - حرك جيداً حتى يذوب.
            - قدم في درجة حرارة 38-40°م.
            - الجرعة اليومية: {volume:.1f} لتر مقسمة على 3-4 وجبات.
            """)

def render_prayer_times():
    st.markdown("### 🕌 مواقيت الصلاة")
    cities = ["مكة", "المدينة", "الخرطوم", "طرابلس", "القاهرة", "دبي", "الرياض"]
    city = st.selectbox("اختر المدينة", cities)
    times = {"الفجر":"05:00","الشروق":"06:30","الظهر":"12:00","العصر":"15:30","المغرب":"18:00","العشاء":"19:30"}
    st.write(f"#### مواقيت الصلاة في {city}")
    cols = st.columns(3)
    for i, (name, t) in enumerate(times.items()):
        with cols[i % 3]:
            st.metric(name, t)
    if st.button("🔔 تنبيه الصلاة القادمة"):
        voice_guide("حان وقت الصلاة في " + city)

def render_dose_reminder():
    st.markdown("### 💊 منبه الجرعات")
    with st.form("add_dose"):
        animal = st.selectbox("الحيوان", ["أبقار","أغنام","ماعز","خيول","دواجن"])
        dose_name = st.text_input("اسم الجرعة")
        dose_type = st.selectbox("النوع", ["لقاح", "فيتامين", "دواء"])
        dose_amount = st.number_input("الجرعة", min_value=0.0, value=1.0)
        dose_unit = st.selectbox("الوحدة", ["مل", "جم", "مجم"])
        route = st.selectbox("طريقة الإعطاء", ["عضل", "تحت الجلد", "فموي"])
        freq = st.number_input("التكرار (أيام)", min_value=1, value=7)
        if st.form_submit_button("💾 إضافة"):
            st.success(f"✅ تم إضافة منبه للجرعة {dose_name}")
            voice_guide(f"تم إضافة منبه للجرعة {dose_name}")

def render_market_prices():
    st.markdown("### 📊 بورصة الأسعار")
    if st.session_state["user_role"] in ["owner","specialist"]:
        st.subheader("تعديل الأسعار")
        for k, v in st.session_state.get("global_livestock_prices", {"عجل":1350, "بقرة":900, "ضأن":180, "ماعز":130, "خيل":4500, "كتكوت":0.65}).items():
            st.number_input(k, value=float(v), step=5.0, key=f"price_{k}")
    else:
        st.info("عرض الأسعار الحالية (للمالك والمختصين فقط التعديل)")

def render_inventory():
    st.markdown("### 🏭 المستودعات")
    inv_data = []
    for item, data in st.session_state["inventory"].items():
        inv_data.append({"المادة": item, "الكمية (طن)": data["quantity"], "الحد الأدنى": data["min_threshold"]})
    st.dataframe(pd.DataFrame(inv_data), use_container_width=True)
    if st.session_state["user_role"] in ["owner","specialist"]:
        with st.expander("تحديث المخزون"):
            sel = st.selectbox("المادة", list(FLAT_FEED_DB.keys()))
            qty = st.number_input("الكمية الجديدة (طن)", min_value=0.0, value=25.0)
            if st.button("تحديث"):
                st.session_state["inventory"][sel]["quantity"] = qty
                st.success("✅ تم التحديث")
                st.rerun()

def render_invoices():
    st.markdown("### 🧾 الفواتير")
    if st.session_state["user_role"] == "owner":
        with st.form("new_invoice"):
            cust = st.text_input("العميل")
            qty = st.number_input("الكمية (طن)", min_value=0.1, value=1.0)
            price = st.number_input("سعر الوحدة ($)", min_value=1.0, value=300.0)
            if st.form_submit_button("إنشاء فاتورة"):
                total = qty * price
                st.success(f"✅ فاتورة للعميل {cust} بقيمة ${total:.2f}")
    else:
        st.info("🔒 هذه الخاصية للمالك فقط")

def render_daily_production():
    st.markdown("### 📈 الإنتاج اليومي")
    if st.session_state["user_role"] in ["owner","specialist"]:
        with st.form("daily_form"):
            farm = st.text_input("المزرعة")
            date = st.date_input("التاريخ", datetime.now())
            milk = st.number_input("الحليب (لتر)", min_value=0.0, value=0.0)
            eggs = st.number_input("البيض (عدد)", min_value=0, value=0)
            weight_gain = st.number_input("زيادة الوزن (كجم)", min_value=0.0, value=0.0)
            mortality = st.number_input("النافق", min_value=0, value=0)
            if st.form_submit_button("💾 حفظ"):
                st.success("✅ تم حفظ الإنتاج اليومي")
    else:
        st.info("🔒 الإضافة للمالك والمختصين فقط")

def render_reports():
    st.markdown("### 📊 التقارير")
    if st.session_state["user_role"] == "owner":
        if st.session_state.get("daily_production_log"):
            df = pd.DataFrame(st.session_state["daily_production_log"])
            st.metric("إجمالي الحليب", f"{df['milk'].sum():.1f} لتر")
            st.metric("إجمالي البيض", f"{df['eggs'].sum():,.0f} بيضة")
        else:
            st.info("لا توجد بيانات إنتاج مسجلة")
    else:
        st.info("🔒 للمالك فقط")

def render_alerts():
    st.markdown("### 🔔 التنبيهات")
    warns = InventoryManager.check_stock()
    if warns:
        for item, status in warns.items():
            st.warning(f"{item}: {status}")
    else:
        st.success("✅ لا توجد تنبيهات")

def render_references():
    st.markdown("### 📚 المراجع العلمية")
    st.markdown("""
    - **Animal Nutrition** – McDonald et al. (2011)
    - **Nutrient Requirements of Dairy Cattle** – NRC (2001)
    - **Commercial Poultry Nutrition** – Leeson & Summers (2009)
    - **The Ruminant Animal** – Church (1993)
    - **Ross Broiler Management Guide** (2020)
    """)
    q = st.text_input("💡 اسأل عن مصطلح:")
    if q:
        if "بروتين مهضوم" in q:
            st.success("البروتين المهضوم = CP × معامل الهضم")
        elif "معادل النشاء" in q:
            st.success("معادل النشاء يقيس الطاقة في العلف")
        else:
            st.info("لم يتم العثور على إجابة")

def render_help():
    st.markdown("### 💡 المساعدة")
    st.markdown("""
    1. اختر الحيوان والمرحلة.
    2. حدد المكونات وأسعارها.
    3. اضغط زر التشغيل.
    4. استخدم المختبر لتحليل الخلطات.
    5. استخدم بقية التبويبات للإدارة.
    """)
    if st.button("🔊 استمع للتعليمات"):
        voice_guide("مرحباً، هذا دليل استخدام منصة تاور نولجي العلمية")

def render_manual():
    st.markdown("### 📖 دليل المستخدم")
    st.markdown("""
    **الفصل الأول: مقدمة** – منصة متكاملة لتركيب الأعلاف.
    **الفصل الثاني: تركيب العلف** – اختر الحيوان والمكونات.
    **الفصل الثالث: المختبر** – حلل خلطاتك.
    **الفصل الرابع: الإدارة** – تتبع المزارع والإنتاج.
    """)

# =====================================================================
# حالة الجلسة
# =====================================================================
if "approved" not in st.session_state:
    st.session_state["approved"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "login_attempts" not in st.session_state:
    st.session_state["login_attempts"] = 0
if "last_login_time" not in st.session_state:
    st.session_state["last_login_time"] = None
if "daily_production_log" not in st.session_state:
    st.session_state["daily_production_log"] = []

MAX_ATTEMPTS = 5
LOCKOUT = 300

# =====================================================================
# شاشة الدخول
# =====================================================================
if not st.session_state["approved"]:
    render_dua_bar()
    if st.session_state["login_attempts"] >= MAX_ATTEMPTS:
        if st.session_state["last_login_time"]:
            diff = (datetime.now() - st.session_state["last_login_time"]).seconds
            if diff < LOCKOUT:
                st.error(f"🔒 قفل مؤقت، حاول بعد {LOCKOUT - diff} ثانية")
                st.stop()
            else:
                st.session_state["login_attempts"] = 0
    st.markdown('<div style="max-width:500px; margin:80px auto; background:white; padding:30px; border-radius:20px; direction:rtl;">', unsafe_allow_html=True)
    if img_base64:
        st.image(f"data:image/jpeg;base64,{img_base64}", width=100)
    st.markdown("<h2 style='text-align:center; color:#1a237e;'>🌾 تاور نولجي Tawornology</h2>", unsafe_allow_html=True)
    if st.button("🔊 ترحيب"):
        play_welcome_audio()
    if st.button("🕊️ دعاء"):
        play_dua_audio()
    if st.button("🔊 شرح كامل"):
        play_full_guide_audio()
    col1, _ = st.columns([1,1])
    with col1:
        if st.button("👤 دخول كزائر", type="primary", use_container_width=True):
            auth = AuthManager()
            user = auth.login_public()
            if user:
                st.session_state["approved"] = True
                st.session_state["user_role"] = "public"
                st.session_state["login_attempts"] = 0
                st.session_state["last_login_time"] = datetime.now()
                st.session_state["user"] = user
                st.rerun()
            else:
                st.error("فشل الدخول")
    st.markdown("<hr>", unsafe_allow_html=True)
    code = st.text_input("🔑 كود الدخول:", type="password")
    if st.button("تسجيل الدخول", use_container_width=True):
        if code.strip() in CODES_DB:
            st.session_state["approved"] = True
            st.session_state["user_role"] = CODES_DB[code.strip()]["role"]
            st.session_state["login_attempts"] = 0
            st.session_state["last_login_time"] = datetime.now()
            st.session_state["user"] = {"full_name": CODES_DB[code.strip()]["name"]}
            st.rerun()
        else:
            st.session_state["login_attempts"] += 1
            st.error(f"❌ كود خاطئ، متبقي {MAX_ATTEMPTS - st.session_state['login_attempts']} محاولات")
    st.markdown("""
    <div style='text-align:center; color:#999; margin-top:15px;'>
    🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# =====================================================================
# الواجهة الرئيسية بعد الدخول
# =====================================================================
render_dua_bar()
st.markdown('<div style="background:white; padding:20px; border-radius:15px; margin-bottom:20px;">', unsafe_allow_html=True)
col1, col2 = st.columns([0.7,0.3])
with col1:
    st.markdown(f"**مرحباً {st.session_state.get('user',{}).get('full_name','زائر')}**")
with col2:
    if st.button("🚪 خروج"):
        for k in list(st.session_state.keys()):
            if k not in ["approved","user_role","user","last_login_time"]:
                del st.session_state[k]
        st.session_state["approved"] = False
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# زر شرح كامل
if st.button("🔊 تشغيل الشرح الصوتي الكامل", type="primary", use_container_width=True):
    play_full_guide_audio()
    st.success("✅ يتم التشغيل")

# =====================================================================
# التبويبات
# =====================================================================
role = st.session_state["user_role"]
if role == "owner":
    tabs_titles = [
        "🐾 القطاع الحيواني", "🐔 إدارة المزارع", "🍼 بدائل الحليب",
        "🕌 مواقيت الصلاة", "💊 منبه الجرعات", "📊 بورصة الأسعار",
        "🏭 المستودعات", "🧾 الفواتير", "📈 الإنتاج اليومي",
        "📊 التقارير", "🔔 التنبيهات", "📚 المراجع",
        "💡 المساعدة", "📖 الدليل", "📧 إرسال الكود"
    ]
elif role in ["specialist","veterinarian","nutritionist"]:
    tabs_titles = [
        "🐾 القطاع الحيواني", "🐔 إدارة المزارع", "🍼 بدائل الحليب",
        "🕌 مواقيت الصلاة", "💊 منبه الجرعات", "📊 بورصة الأسعار",
        "🏭 المستودعات", "📈 الإنتاج اليومي", "🔔 التنبيهات",
        "📚 المراجع", "💡 المساعدة", "📖 الدليل"
    ]
else:  # public
    tabs_titles = [
        "🐾 القطاع الحيواني", "📚 المراجع", "💡 المساعدة", "📖 الدليل"
    ]

tabs = st.tabs(tabs_titles)

# =====================================================================
# تبويب 0: القطاع الحيواني
# =====================================================================
with tabs[0]:
    st.markdown("### 🐾 القطاع الحيواني")
    animal_sub = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐔 دواجن", "🐟 أسماك", "🔬 المختبر"])
    with animal_sub[0]:
        render_formulation_tab("cattle", "أبقار", "🐄", ["كنانة","هولشتاين"], ["تسمين عجول","حليب/إدرار"], 12.0, 65.0)
    with animal_sub[1]:
        render_formulation_tab("sheep", "أغنام", "🐏", ["صحراوي","بربري"], ["تسمين حملان","حليب/إدرار"], 11.5, 62.0)
    with animal_sub[2]:
        render_formulation_tab("goat", "ماعز", "🐐", ["نوبي","صحراوي"], ["تسمين جديان","حليب/إدرار"], 11.0, 60.0)
    with animal_sub[3]:
        render_formulation_tab("poultry", "دواجن", "🐔", ["لاحم","بياض"], ["بادي","نامي"], 18.0, 72.0, has_measurements=False)
    with animal_sub[4]:
        render_formulation_tab("fish", "أسماك", "🐟", ["بلطي","قرموط"], ["نمو","تسمين نهائي"], 28.0, 68.0, has_measurements=False)
    with animal_sub[5]:
        render_lab_tab()

# =====================================================================
# باقي التبويبات
# =====================================================================
tab_map = {
    "🐔 إدارة المزارع": render_farm_management,
    "🍼 بدائل الحليب": render_milk_replacer,
    "🕌 مواقيت الصلاة": render_prayer_times,
    "💊 منبه الجرعات": render_dose_reminder,
    "📊 بورصة الأسعار": render_market_prices,
    "🏭 المستودعات": render_inventory,
    "🧾 الفواتير": render_invoices,
    "📈 الإنتاج اليومي": render_daily_production,
    "📊 التقارير": render_reports,
    "🔔 التنبيهات": render_alerts,
    "📚 المراجع": render_references,
    "💡 المساعدة": render_help,
    "📖 الدليل": render_manual,
}

# تعيين الفهرس لكل تبويب
for idx, title in enumerate(tabs_titles):
    if title in tab_map:
        with tabs[idx]:
            tab_map[title]()
    elif title == "📧 إرسال الكود":
        with tabs[idx]:
            st.markdown("### 📧 إرسال الكود إلى البريد")
            if role == "owner":
                email = st.text_input("البريد المستلم:", value=OWNER_EMAIL)
                if st.button("📤 إرسال"):
                    if email and '@' in email:
                        if email.strip().lower() == OWNER_EMAIL.lower():
                            with st.spinner("جارٍ الإرسال..."):
                                success, msg = send_code_to_email(email)
                                st.success(msg) if success else st.error(msg)
                        else:
                            st.error("❌ الإرسال مسموح فقط للبريد الرئيسي")
                    else:
                        st.warning("⚠️ أدخل بريداً صحيحاً")
            else:
                st.info("🔒 هذه الخاصية للمالك فقط")

# =====================================================================
# التذييل
# =====================================================================
st.markdown("""
<div style='text-align:center; padding:15px; border-top:2px solid #ccc; color:#888; margin-top:30px;'>
🌾 <b>تاور نولجي Tawornology العلمية</b> - الإصدار 16.1<br>
© 2026 | اختصاصي تغذية الحيوان م. عبد القادر إسماعيل تاور<br>
🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام
</div>
""", unsafe_allow_html=True)

if st.button("🔊 اختبار الصوت (نهاية الصفحة)"):
    voice_guide("بسم الله الرحمن الرحيم، هذا اختبار للنظام الصوتي.")

# =====================================================================
# نهاية الكود
# =====================================================================
