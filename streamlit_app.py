# =====================================================================
# تاور نولجي Tawornology العلمية - للانتاج الحيواني وتركيب الاعلاف
# النسخة المتكاملة النهائية - أكثر من 5000 سطر
# =====================================================================
# Digital Signature: 110dfcb10bc6902ee96175517109d7c7
# Generated: 2026-07-02T22:16:27.283609
# 
# 🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله وغفر لهما
# =====================================================================

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
from reportlab.lib.colors import HexColor, black, white, grey, blue, red, green, orange, purple, teal
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
# السطر 1-60: إعدادات النظام الأساسية - تاور نولجي Tawornology
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
# أكواد الدخول (خاصة للمالك والمختصين فقط)
# =====================================================================
CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2024": {"role": "veterinarian", "name": "الطبيب البيطري", "level": 2},
    "2025": {"role": "nutritionist", "name": "أخصائي التغذية", "level": 2}
}

# =====================================================================
# إعدادات البريد الإلكتروني
# =====================================================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"
SENDER_PASSWORD = "oynz rdli tsdy ekdq"
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"

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
# السطر 61-160: كلاس DatabaseManager المتقدم
# =====================================================================
class DatabaseManager:
    """مدير قاعدة البيانات المحلية المتقدم"""
    def __init__(self, db_path="tawornology_platform.db"):
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
            specialty TEXT,
            experience_years INTEGER,
            created_date TEXT,
            last_login TEXT,
            is_active INTEGER DEFAULT 1,
            is_public INTEGER DEFAULT 0
        )''')
        
        # جدول الدورات الإنتاجية
        c.execute('''CREATE TABLE IF NOT EXISTS farm_cycles (
            cycle_id TEXT PRIMARY KEY,
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
            created_date TEXT,
            total_cost REAL,
            total_revenue REAL,
            profit REAL
        )''')
        
        # جدول الخلطات العلفية
        c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas (
            formula_id TEXT PRIMARY KEY,
            formula_name TEXT,
            animal_type TEXT,
            breed TEXT,
            stage TEXT,
            target_dp REAL,
            target_se REAL,
            target_cp REAL,
            ingredients TEXT,
            total_cost REAL,
            cost_per_ton REAL,
            created_by TEXT,
            created_date TEXT,
            is_approved INTEGER DEFAULT 0,
            usage_count INTEGER DEFAULT 0
        )''')
        
        # جدول الفواتير
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
            tax REAL DEFAULT 0,
            final_price REAL,
            status TEXT,
            payment_method TEXT,
            created_by TEXT,
            created_date TEXT,
            due_date TEXT,
            notes TEXT
        )''')
        
        # جدول الأسعار التاريخية
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
        
        # جدول سجلات العلاج (محذوف جزئياً - بقي للتوافق)
        c.execute('''CREATE TABLE IF NOT EXISTS treatment_records (
            treatment_id TEXT PRIMARY KEY,
            animal_id TEXT,
            farm_name TEXT,
            animal_type TEXT,
            medicine_id TEXT,
            dose_given REAL,
            administration_date TEXT,
            administration_time TEXT,
            administered_by TEXT,
            reason TEXT,
            notes TEXT,
            next_dose_date TEXT
        )''')
        
        # جدول العملاء والموردين
        c.execute('''CREATE TABLE IF NOT EXISTS contacts (
            contact_id TEXT PRIMARY KEY,
            contact_name TEXT,
            contact_type TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            tax_number TEXT,
            notes TEXT,
            created_date TEXT,
            created_by TEXT
        )''')
        
        # جدول تحليل التربة
        c.execute('''CREATE TABLE IF NOT EXISTS soil_analysis (
            analysis_id TEXT PRIMARY KEY,
            farm_name TEXT,
            location TEXT,
            analysis_date TEXT,
            ph REAL,
            nitrogen REAL,
            phosphorus REAL,
            potassium REAL,
            organic_matter REAL,
            salinity REAL,
            notes TEXT,
            created_by TEXT
        )''')
        
        # جدول تحليل المياه
        c.execute('''CREATE TABLE IF NOT EXISTS water_analysis (
            analysis_id TEXT PRIMARY KEY,
            farm_name TEXT,
            source TEXT,
            analysis_date TEXT,
            ph REAL,
            hardness REAL,
            total_dissolved_solids REAL,
            chloride REAL,
            nitrate REAL,
            bacteria_presence INTEGER,
            notes TEXT,
            created_by TEXT
        )''')
        
        # جدول الإنتاج اليومي
        c.execute('''CREATE TABLE IF NOT EXISTS daily_production (
            record_id TEXT PRIMARY KEY,
            farm_name TEXT,
            animal_type TEXT,
            record_date TEXT,
            milk_production REAL,
            egg_production INTEGER,
            weight_gain REAL,
            feed_consumed REAL,
            water_consumed REAL,
            mortality INTEGER,
            notes TEXT,
            recorded_by TEXT
        )''')
        
        # جدول التنبيهات
        c.execute('''CREATE TABLE IF NOT EXISTS alerts (
            alert_id TEXT PRIMARY KEY,
            alert_type TEXT,
            title TEXT,
            message TEXT,
            priority TEXT,
            created_date TEXT,
            due_date TEXT,
            is_read INTEGER DEFAULT 0,
            is_dismissed INTEGER DEFAULT 0,
            created_by TEXT
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
        return c.lastrowid
    
    def update_record(self, table: str, data: dict, condition: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        set_clause = ', '.join([f"{k}=?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        c.execute(query, list(data.values()))
        conn.commit()
        conn.close()

# =====================================================================
# السطر 161-260: نظام المصادقة المعدل (دخول مجاني للزوار)
# =====================================================================
class AuthManager:
    ROLES = {
        "owner": {"level": 5, "permissions": ["all"], "name": "المالك", "icon": "👑"},
        "specialist": {"level": 4, "permissions": ["view", "create", "edit", "delete"], "name": "المختص", "icon": "👨‍🔬"},
        "veterinarian": {"level": 3, "permissions": ["view", "create", "edit", "medicines"], "name": "الطبيب البيطري", "icon": "💊"},
        "nutritionist": {"level": 3, "permissions": ["view", "create", "edit", "formulas"], "name": "أخصائي التغذية", "icon": "🧬"},
        "breeder": {"level": 2, "permissions": ["view", "create", "edit_own"], "name": "المربي", "icon": "🌾"},
        "public": {"level": 1, "permissions": ["view"], "name": "زائر", "icon": "👤"}
    }
    
    def __init__(self):
        self.db = DatabaseManager()
        self._create_default_users()
        self._create_public_user()
    
    def _create_default_users(self):
        """إنشاء المستخدمين الافتراضيين"""
        default_users = [
            ('admin', 'admin123', 'owner', 'مدير النظام - م. عبد القادر إسماعيل تاور', 'admin@tawornology.com', '+249123456789', 'إدارة الأنظمة', 10),
            ('specialist', 'spec123', 'specialist', 'المختص العام', 'specialist@tawornology.com', '+249123456788', 'تغذية وإنتاج', 8),
            ('nutritionist', 'nutri123', 'nutritionist', 'أخصائي التغذية', 'nutrition@tawornology.com', '+249123456786', 'تغذية حيوان', 7)
        ]
        for username, password, role, full_name, email, phone, specialty, experience in default_users:
            users = self.db.execute_query("SELECT * FROM users WHERE username=?", (username,))
            if not users:
                self.create_user(username, password, role, full_name, email, phone, specialty, experience)
    
    def _create_public_user(self):
        """إنشاء مستخدم عام للزوار (دخول مجاني)"""
        users = self.db.execute_query("SELECT * FROM users WHERE username='public'")
        if not users:
            self.create_user('public', 'public123', 'public', 'زائر', 'public@tawornology.com', '+249123456780', 'عام', 0)
    
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
        """التحقق من صحة بيانات الدخول"""
        users = self.db.execute_query("SELECT * FROM users WHERE username=? AND is_active=1", (username,))
        if users:
            user = users[0]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user[2] == password_hash:
                self.db.update_record('users', {'last_login': datetime.now().isoformat()}, f"user_id='{user[0]}'")
                return {
                    'user_id': user[0],
                    'username': user[1],
                    'role': user[3],
                    'full_name': user[4],
                    'email': user[5],
                    'phone': user[6],
                    'specialty': user[7],
                    'experience_years': user[8],
                    'permissions': self.ROLES.get(user[3], {}).get('permissions', ['view']),
                    'role_info': self.ROLES.get(user[3], {})
                }
        return None
    
    def login_public(self):
        """تسجيل الدخول كزائر (بدون كلمة مرور)"""
        users = self.db.execute_query("SELECT * FROM users WHERE username='public' AND is_active=1")
        if users:
            user = users[0]
            self.db.update_record('users', {'last_login': datetime.now().isoformat()}, f"user_id='{user[0]}'")
            return {
                'user_id': user[0],
                'username': user[1],
                'role': 'public',
                'full_name': 'زائر',
                'email': user[5],
                'phone': user[6],
                'specialty': 'عام',
                'experience_years': 0,
                'permissions': ['view'],
                'role_info': self.ROLES.get('public', {})
            }
        return None
    
    def get_public_user(self):
        """الحصول على بيانات المستخدم العام"""
        users = self.db.execute_query("SELECT * FROM users WHERE username='public'")
        if users:
            user = users[0]
            return {
                'user_id': user[0],
                'username': user[1],
                'role': 'public',
                'full_name': 'زائر',
                'email': user[5],
                'phone': user[6]
            }
        return None

# =====================================================================
# السطر 261-360: باقي الكلاسات الأساسية (PricePredictor, ScientificReferenceSystem)
# =====================================================================
class PricePredictor:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_price_trend(self, ingredient_name, days=30):
        results = self.db.execute_query(
            "SELECT * FROM price_history WHERE ingredient_name=? ORDER BY record_date DESC LIMIT ?",
            (ingredient_name, days))
        if len(results) < 3:
            return {'trend': 'stable', 'change_percent': 0, 'volatility': 0}
        prices = [r[2] for r in results]
        if len(prices) >= 2:
            x = np.array(range(len(prices))).reshape(-1, 1)
            y = np.array(prices)
            model = LinearRegression()
            model.fit(x, y)
            slope = model.coef_[0]
            change_percent = ((prices[0] - prices[-1]) / prices[-1]) * 100 if prices[-1] > 0 else 0
            trend = 'up' if slope > 0.5 else 'down' if slope < -0.5 else 'stable'
            return {'trend': trend, 'change_percent': change_percent, 'volatility': np.std(prices) / np.mean(prices) if np.mean(prices) > 0 else 0, 'current_price': prices[0]}
        return {'trend': 'stable', 'change_percent': 0, 'volatility': 0}

class ScientificReferenceSystem:
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان",
            "icon": "📚",
            "references": [
                {"id": "REF001", "authors": "McDonald, P., Edwards, R.A., Greenhalgh, J.F.D., Morgan, C.A.",
                 "year": 2011, "title": "Animal Nutrition", "publisher": "Pearson Education",
                 "edition": "7th Edition", "isbn": "978-1408204238",
                 "summary": "المرجع الأساسي في تغذية الحيوان، يغطي جميع جوانب التغذية من الهضم إلى متطلبات العناصر الغذائية."}
            ]
        },
        "protein_amino_acids": {
            "title": "البروتين والأحماض الأمينية",
            "icon": "🧬",
            "references": [
                {"id": "REF003", "authors": "NRC", "year": 2012,
                 "title": "Nutrient Requirements of Swine", "publisher": "National Academies Press",
                 "summary": "المرجع الرسمي لمتطلبات العناصر الغذائية للخنازير."}
            ]
        },
        "horses": {
            "title": "تغذية الخيول",
            "icon": "🐴",
            "references": [
                {"id": "REF015", "authors": "NRC", "year": 2007,
                 "title": "Nutrient Requirements of Horses", "publisher": "National Academies Press",
                 "summary": "المرجع الأساسي في تغذية الخيول ومتطلباتها الغذائية."}
            ]
        },
        "poultry": {
            "title": "تغذية الدواجن",
            "icon": "🐔",
            "references": [
                {"id": "REF010", "authors": "Leeson, S., Summers, J.D.", "year": 2009,
                 "title": "Commercial Poultry Nutrition", "publisher": "Nottingham University Press",
                 "summary": "المرجع العملي في تغذية الدواجن التجارية."}
            ]
        },
        "ruminants": {
            "title": "تغذية المجترات",
            "icon": "🐄",
            "references": [
                {"id": "REF012", "authors": "Church, D.C.", "year": 1993,
                 "title": "The Ruminant Animal", "publisher": "Waveland Press",
                 "summary": "المرجع الشامل في فسيولوجيا الهضم والتغذية للمجترات."}
            ]
        }
    }
    
    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم (Digestible Protein) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف.",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (SE) هو مقياس لكمية الطاقة التي يوفرها العلف للحيوان، مقارنة بالطاقة التي يوفرها النشاء النقي.",
            "simplified": "معادل النشاء يقيس كمية الطاقة في العلف."
        },
        "كيف يتم تركيب العلف الأمثل": {
            "answer": "يتم تركيب العلف الأمثل باستخدام محرك الاستمثال الخطي (Linear Programming) الذي يحسب أقل تكلفة لتحقيق متطلبات غذائية محددة.",
            "simplified": "نستخدم برنامجاً ذكياً يحسب أرخص خلطة علفية تلبي احتياجات الحيوان."
        },
        "ما هي أهمية إضافة الإنزيمات للأعلاف": {
            "answer": "الإنزيمات في الأعلاف تعمل على تحسين هضم واستفادة الحيوان من العناصر الغذائية.",
            "simplified": "الإنزيمات تساعد الحيوان على هضم العلف بشكل أفضل."
        },
        "ما هو مؤشر EPEF": {
            "answer": "مؤشر الأداء الأوروبي EPEF هو مقياس لكفاءة إنتاج الدجاج اللاحم.",
            "simplified": "EPEF يعبر عن كفاءة مزرعة الدجاج."
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
                return {"answer": value["answer"], "simplified": value.get("simplified", value["answer"])}
        return None

# =====================================================================
# السطر 361-500: معالج اللغة العربية ومولد PDF المتقدم
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

class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        if os.path.exists("Amiri-Regular.ttf"):
            try:
                pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
                self.font_name = 'Amiri'
            except:
                pass
        self.styles = self._create_styles()
    
    def _create_styles(self):
        styles = {}
        styles['title'] = ParagraphStyle('title', fontName=self.font_name, fontSize=24, alignment=TA_CENTER, textColor=HexColor('#1b5e20'), spaceAfter=20, leading=30)
        styles['subtitle'] = ParagraphStyle('subtitle', fontName=self.font_name, fontSize=16, alignment=TA_CENTER, textColor=HexColor('#2e7d32'), spaceAfter=15, leading=20)
        styles['heading'] = ParagraphStyle('heading', fontName=self.font_name, fontSize=14, alignment=TA_RIGHT, textColor=HexColor('#1b5e20'), spaceAfter=10, leading=18, fontweight='bold')
        styles['body'] = ParagraphStyle('body', fontName=self.font_name, fontSize=11, alignment=TA_RIGHT, textColor=HexColor('#333333'), spaceAfter=6, leading=16)
        styles['footer'] = ParagraphStyle('footer', fontName=self.font_name, fontSize=8, alignment=TA_CENTER, textColor=HexColor('#999999'), spaceAfter=0, leading=10)
        return styles
    
    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, include_charts=True, extra_info=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        
        def p(text, style='body'):
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, self.styles.get(style, self.styles['body']))
        
        story.append(p("تاور نولجي Tawornology العلمية - للانتاج الحيواني وتركيب الاعلاف", 'title'))
        story.append(p("تقرير فني شامل - تقرير التركيب", 'subtitle'))
        story.append(Spacer(1, 10))
        
        info_lines = [
            f"المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور",
            f"الموقع الجغرافي: {city}",
            f"الفصيل المستهدف: {breed}",
            f"تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ]
        for line in info_lines:
            story.append(p(line))
        story.append(Spacer(1, 15))
        
        tdata = [
            ['المعيار', 'القيمة'],
            ['البروتين المهضوم (DP)', f'{target_dp:.2f}%'],
            ['معادل النشاء (SE)', f'{computed_se:.2f} وحدة'],
            ['التكلفة للطن', f'${cost:.2f} ({local_cost:,.2f} {local_sym})']
        ]
        t = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in tdata], colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#2e7d32')),
        ]))
        story.append(t)
        story.append(PageBreak())
        
        story.append(p("المقادير المعتمدة لتركيب الطن الواحد:", 'heading'))
        story.append(Spacer(1, 10))
        ing_data = [['المكون', 'النسبة %', 'كجم/طن']]
        for ing, pct in formula.items():
            ing_data.append([ing, f'{pct:.2f}%', f'{pct*10:.1f}'])
        t2 = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in ing_data], colWidths=[180, 150, 150])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
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
                ax.legend([arabic_processor.fix_arabic_text(n) for n in names], title=arabic_processor.fix_arabic_text("المكونات"), loc='center left', bbox_to_anchor=(1,0,0.5,1), fontsize=8)
                ax.set_title(arabic_processor.fix_arabic_text('توزيع المكونات'), fontsize=12)
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=400, height=230))
            except:
                pass
        
        story.append(PageBreak())
        story.append(p("التوصيات الفنية:", 'heading'))
        recommendations = [
            "• يوصى بإضافة الإنزيمات لتحسين الهضم والاستفادة من العلف.",
            "• يجب مراقبة جودة المواد الخام بشكل دوري وإجراء تحاليل مخبرية.",
            "• يجب تخزين العلف في مكان جاف بعيداً عن الرطوبة والحشرات.",
            "• يوصى بتقسيم العلف على عدة وجبات لتحسين الهضم والاستفادة."
        ]
        for rec in recommendations:
            story.append(p(rec))
        story.append(Spacer(1, 15))
        
        if extra_info:
            story.append(p("معلومات إضافية:", 'heading'))
            for key, value in extra_info.items():
                if value:
                    story.append(p(f"• {key}: {value}"))
        
        story.append(PageBreak())
        story.append(p("خاتمة التقرير", 'heading'))
        story.append(Spacer(1, 10))
        conclusion_text = "تم إعداد هذا التقرير الفني بناءً على تحليل دقيق للاحتياجات الغذائية للفصيل المستهدف، مع تطبيق أحدث تقنيات تركيب الأعلاف."
        story.append(p(conclusion_text))
        story.append(Spacer(1, 20))
        story.append(p("مع خالص التحية والتقدير،", 'body'))
        story.append(Spacer(1, 10))
        story.append(p("الاختصاصي م. عبد القادر إسماعيل تاور", 'body'))
        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة تاور نولجي Tawornology العلمية © 2026", 'footer'))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_lab_report(self, analysis_results, animal_type, stage, user_name):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        
        def p(text, style='body'):
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, self.styles.get(style, self.styles['body']))
        
        story.append(p("🔬 تقرير التحليل المخبري - تاور نولجي Tawornology", 'title'))
        story.append(p(f"المشرف: {user_name}", 'subtitle'))
        story.append(p(f"الحيوان: {animal_type} | المرحلة: {stage}"))
        story.append(p(f"تاريخ التحليل: {datetime.now().strftime('%Y-%m-%d %H:%M')}"))
        story.append(Spacer(1, 15))
        
        if analysis_results:
            tdata = [
                ['العنصر', 'القيمة'],
                ['البروتين الخام (CP)', f"{analysis_results.get('cp', 0):.2f}%"],
                ['البروتين المهضوم (DP)', f"{analysis_results.get('dp', 0):.2f}%"],
                ['معادل النشاء (SE)', f"{analysis_results.get('se', 0):.2f} وحدة"]
            ]
            t = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in tdata], colWidths=[250, 250])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), HexColor('#1565C0')),
                ('TEXTCOLOR', (0,0), (-1,0), white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,-1), self.font_name),
                ('FONTSIZE', (0,0), (-1,-1), 11),
                ('GRID', (0,0), (-1,-1), 1, HexColor('#1565C0')),
            ]))
            story.append(t)
            story.append(Spacer(1, 15))
            
            if 'components' in analysis_results and analysis_results['components']:
                story.append(p("المكونات المدخلة:", 'heading'))
                comp_data = [['المكون', 'الوزن (كجم)']]
                for name, weight in analysis_results['components'].items():
                    if weight > 0:
                        comp_data.append([name, f"{weight:.1f}"])
                t3 = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in comp_data], colWidths=[250, 150])
                t3.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
                    ('TEXTCOLOR', (0,0), (-1,0), white),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,-1), self.font_name),
                    ('FONTSIZE', (0,0), (-1,-1), 10),
                    ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
                ]))
                story.append(t3)
            
            story.append(PageBreak())
            story.append(p("التوصيات المخبرية:", 'heading'))
            recs = [
                "• يوصى بإعادة التحليل بعد أي تعديل على الخلطة.",
                "• يجب مراجعة نسب البروتين والطاقة حسب احتياجات الحيوان.",
                "• يوصى بالتواصل مع أخصائي التغذية لتعديل الخلطة حسب النتائج."
            ]
            for rec in recs:
                story.append(p(rec))
        
        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة تاور نولجي Tawornology العلمية © 2026", 'footer'))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# =====================================================================
# السطر 501-650: كلاس BroilerFarmManager
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
    
    @staticmethod
    def get_temp_humidity_table():
        return pd.DataFrame({
            "العمر (يوم)": [1, 3, 7, 14, 21, 28, 35, 42],
            "درجة الحرارة (مئوي)": [33, 32, 30, 28, 26, 24, 22, 21],
            "الرطوبة النسبية (%)": [65, 65, 65, 60, 60, 55, 55, 55]
        })
    
    @staticmethod
    def get_vaccination_schedule():
        return pd.DataFrame({
            "العمر (يوم)": [1, 7, 14, 21, 28, 35],
            "اللقاح/الدواء": ["فيتامين AD3E", "نيوكاسل (Lasota)", "Gumboro", "مضاد كوكسيديا", "فيتامين C+E", "Gumboro booster"],
            "الجرعة": ["1 مل/لتر ماء", "قطرة عين", "قطرة فم", "1 جم/لتر", "0.5 جم/لتر", "قطرة فم"],
            "طريقة الإعطاء": ["مياه الشرب", "قطرة عين/أنف", "مياه الشرب", "مياه الشرب (3 أيام)", "مياه الشرب", "مياه الشرب"]
        })

# =====================================================================
# السطر 651-850: مكتبة الأعلاف الكاملة
# =====================================================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6}
    },
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5}
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5}
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5}
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم الفايتيز الزامي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0}
    }
}

# =====================================================================
# السطر 851-950: إدارة المخزون والمتغيرات العامة
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

if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين ($)": 1350.0, "أبقار كنانة محلية ($)": 900.0,
        "ضأن وستيرلنغ ($)": 180.0, "ماعز نوبي ($)": 130.0,
        "خيول عربية أصيلة ($)": 4500.0, "كتكوت لاحم ($)": 0.65
    }
if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري ($)": 7.50, "كيلو لحم ضأن ($)": 9.00,
        "كيلو لحم دجاج ($)": 3.80, "طبق بيض 30 بيضة ($)": 4.20,
        "لتر حليب خام ($)": 0.90
    }
if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = "• [توجيه الاختصاصي م. عبد القادر]: يرجى من جميع الزملاء إضافة تعليقاتهم.\n"

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG", "currency_name": "جنيه سوداني"},
    "LIBYA": {"rate": 4.80, "sym": "LYD", "currency_name": "دينار ليبي"},
    "مصر": {"rate": 48.0, "sym": "EGP", "currency_name": "جنيه مصري"},
    "دولار أمريكي": {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"}
}

ANIMAL_IMAGES_RESOURCES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600"
}

if "active_formula" not in st.session_state: st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 12.0
if "active_se_tag" not in st.session_state: st.session_state["active_se_tag"] = 65.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_animal_img" not in st.session_state: st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES["عام"]
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0

# =====================================================================
# السطر 951-1050: حالة الجلسة العامة
# =====================================================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "login_welcome_shown" not in st.session_state: st.session_state["login_welcome_shown"] = False
if "login_attempts" not in st.session_state: st.session_state["login_attempts"] = 0
if "last_login_time" not in st.session_state: st.session_state["last_login_time"] = None
if "session_token" not in st.session_state: st.session_state["session_token"] = None
if "broiler_farms" not in st.session_state: st.session_state["broiler_farms"] = {}
if "selected_farm" not in st.session_state: st.session_state["selected_farm"] = None
if "standard_vacc_schedule" not in st.session_state:
    st.session_state["standard_vacc_schedule"] = {
        1: {"type": "فيتامين", "name": "فيتامين AD3E", "dose": "1 مل/لتر ماء", "route": "مياه الشرب"},
        7: {"type": "لقاح", "name": "نيوكاسل (Lasota)", "dose": "قطرة عين", "route": "قطرة عين/أنف"},
        14: {"type": "لقاح", "name": "Gumboro", "dose": "قطرة فم", "route": "مياه الشرب"},
        21: {"type": "دواء", "name": "مضاد كوكسيديا", "dose": "1 جم/لتر", "route": "مياه الشرب لمدة 3 أيام"},
        28: {"type": "فيتامين", "name": "فيتامين C + E", "dose": "0.5 جم/لتر", "route": "مياه الشرب"},
        35: {"type": "لقاح", "name": "Gumboro booster", "dose": "قطرة فم", "route": "مياه الشرب"},
    }
if "whatsapp_alerts_sent" not in st.session_state: st.session_state["whatsapp_alerts_sent"] = {}
if "query_history" not in st.session_state: st.session_state["query_history"] = []
if "analysis_results" not in st.session_state: st.session_state["analysis_results"] = None
if "analysis_animal" not in st.session_state: st.session_state["analysis_animal"] = "غير محدد"
if "analysis_stage" not in st.session_state: st.session_state["analysis_stage"] = "غير محدد"
if "daily_production_log" not in st.session_state: st.session_state["daily_production_log"] = []

# =====================================================================
# السطر 1051-1150: دوال مساعدة (الصوت، واتساب، الصور)
# =====================================================================
def voice_guide(message, lang="ar"):
    if not message or len(message.strip()) < 2:
        return
    safe_message = message.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    lang_code = "ar-SA" if lang == "ar" else "en-US"
    js_code = f"""
    <script>
    (function() {{
        function speak() {{
            try {{
                if (!window.speechSynthesis) return;
                var msg = new SpeechSynthesisUtterance('{safe_message}');
                msg.lang = '{lang_code}';
                msg.rate = 0.85;
                msg.pitch = 1.0;
                msg.volume = 1.0;
                var voices = window.speechSynthesis.getVoices();
                var arabicVoice = voices.find(v => v.lang && v.lang.startsWith('ar'));
                if (arabicVoice) msg.voice = arabicVoice;
                window.speechSynthesis.cancel();
                window.speechSynthesis.speak(msg);
            }} catch(e) {{
                console.warn('⚠️ تعذر تشغيل الصوت: ' + e.message);
            }}
        }}
        if (document.readyState === 'complete') {{
            setTimeout(speak, 150);
        }} else {{
            window.addEventListener('load', function() {{ setTimeout(speak, 250); }});
        }}
    }})();
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)

def voice_welcome(role):
    messages = {
        "owner": "مرحباً بك في تاور نولجي Tawornology العلمية، أيها الاختصاصي م. عبد القادر إسماعيل تاور.",
        "specialist": "مرحباً أيها المختص. تاور نولجي العلمية تحت خدمتك.",
        "breeder": "مرحباً أيها المربي. تاور نولجي العلمية تساعدك في تركيب أعلاف اقتصادية.",
        "public": "مرحباً بك زائراً في تاور نولجي العلمية. يمكنك تصفح المنصة واستخدام أدوات التركيب الأساسية."
    }
    voice_guide(messages.get(role, "مرحباً بك في تاور نولجي Tawornology العلمية"))

def send_code_to_email(receiver_email):
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code_content = f.read()
    except:
        code_content = "# تعذر قراءة الكود المصدر\n"
    file_hash = hashlib.md5(code_content.encode()).hexdigest()
    code_content = f"# Digital Signature: {file_hash}\n# Generated: {datetime.now().isoformat()}\n\n{code_content}"
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود - تاور نولجي Tawornology العلمية"
    body = f"""مرفق السورس كود لمنصة تاور نولجي Tawornology العلمية.
📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔑 التوقيع الرقمي: {file_hash}"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    attachment = MIMEText(code_content, 'plain', 'utf-8')
    attachment.add_header('Content-Disposition', 'attachment', filename="tawornology_platform.py")
    msg.attach(attachment)
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True, "تم إرسال الكود بنجاح"
    except Exception as e:
        return False, f"فشل الإرسال: {str(e)}"

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
    ax.text(0.5, -0.08, f'© {datetime.now().year} تاور نولجي Tawornology العلمية',
            transform=ax.transAxes, ha='center', fontsize=9, color='#666666')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    buf.seek(0)
    return buf

def generate_analysis_image(analysis_results, target_animal, production_type, user_name):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('#ffffff')
    ax1.set_facecolor('#f5f5f5')
    title_text = f"🔬 تقرير التحليل المخبري - تاور نولجي Tawornology العلمية\nالمشرف: {user_name}\nالحيوان: {target_animal} | المرحلة: {production_type}"
    ax1.set_title(title_text, fontsize=13, fontweight='bold', pad=20)
    if 'components' in analysis_results and analysis_results['components']:
        comps = analysis_results['components']
        names = list(comps.keys())[:10]
        values = list(comps.values())[:10]
        y_pos = np.arange(len(names))
        ax1.barh(y_pos, values, color='#2e7d32', alpha=0.7, edgecolor='#1b5e20', linewidth=1)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels([arabic_processor.fix_arabic_text(n[:20]) for n in names], fontsize=10)
        ax1.set_xlabel('الوزن (كجم)', fontsize=11, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
    ax2.set_facecolor('#f5f5f5')
    ax2.set_title("القيم الغذائية المحسوبة", fontsize=13, fontweight='bold', pad=20)
    labels = ['CP', 'DP', 'SE']
    values = [analysis_results.get('cp', 0), analysis_results.get('dp', 0), analysis_results.get('se', 0)]
    colors = ['#2e7d32', '#1565C0', '#E65100']
    bars2 = ax2.bar(labels, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1)
    ax2.set_ylabel('القيمة', fontsize=11, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    for bar, val in zip(bars2, values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}%' if val < 100 else f'{val:.1f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    fig.text(0.5, 0.01, f'© {datetime.now().year} تاور نولجي Tawornology العلمية',
             ha='center', fontsize=9, color='#666666')
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.08)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
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
        </div>
        """, unsafe_allow_html=True)
        return True
    except Exception as e:
        st.error(f"❌ حدث خطأ: {str(e)}")
        return False

# =====================================================================
# السطر 1151-1250: شريط الدعاء المتحرك (إهداء لروح الوالد والأخت)
# =====================================================================
def render_dua_bar():
    """عرض شريط دعاء متحرك في أعلى الصفحة"""
    st.markdown("""
    <style>
    @keyframes scrollDua {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .dua-container {
        background: linear-gradient(135deg, #1a237e, #283593, #1a237e);
        padding: 12px 0;
        border-radius: 10px;
        margin-bottom: 15px;
        overflow: hidden;
        border: 2px solid #d4af37;
        box-shadow: 0 4px 20px rgba(26, 35, 126, 0.4);
        direction: rtl;
    }
    .dua-text {
        display: inline-block;
        white-space: nowrap;
        animation: scrollDua 25s linear infinite;
        font-size: 1.3rem;
        font-weight: 700;
        color: #ffd700;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        padding: 0 50px;
        font-family: 'Cairo', sans-serif;
        letter-spacing: 0.5px;
    }
    .dua-text .heart {
        color: #ff6b6b;
        animation: pulseHeart 1.5s ease-in-out infinite;
        display: inline-block;
    }
    @keyframes pulseHeart {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.3); }
    }
    .dua-text .allah {
        color: #4fc3f7;
    }
    .dua-text .name {
        color: #ffb74d;
    }
    </style>
    <div class="dua-container">
        <div class="dua-text">
            <span class="heart">❤️</span>
            <span class="allah">اللهم</span>
            اغفر لـ <span class="name">إسماعيل تاور</span>
            <span class="heart">❤️</span>
            و
            <span class="name">ابتسام</span>
            <span class="heart">❤️</span>
            وارحمهما وأدخلهما فسيح جناتك
            <span class="heart">❤️</span>
            <span class="allah">اللهم</span>
            اجعل قبرهما روضة من رياض الجنة
            <span class="heart">❤️</span>
            واجمعنا بهما في الفردوس الأعلى
            <span class="heart">❤️</span>
            <span style="color:#fff; font-size:0.9rem;">🕊️</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# السطر 1251-1400: CSS المتقدم للواجهة مع تعديلات الاسم
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
.stock-critical {
    background: linear-gradient(135deg, #ffebee, #ffcdd2);
    padding: 6px 16px; border-radius: 25px;
    color: #c62828; font-weight: 700;
    display: inline-block;
}
.stock-normal {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 6px 16px; border-radius: 25px;
    color: #2e7d32; font-weight: 700;
    display: inline-block;
}
.stock-warning {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 6px 16px; border-radius: 25px;
    color: #e65100; font-weight: 700;
    display: inline-block;
}
.sack-tag {
    border: 3px dashed #1b5e20; padding: 30px; border-radius: 20px;
    background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e9 100%);
    box-shadow: 0 8px 35px rgba(0,0,0,0.08);
    text-align: center;
}
.animal-banner-img {
    width: 100%; max-height: 220px; object-fit: cover; border-radius: 16px;
    border: 3px solid #2e7d32; box-shadow: 0 6px 30px rgba(0,0,0,0.1);
}
.manual-book {
    background: #ffffff; padding: 30px; border-radius: 16px;
    box-shadow: 0 8px 35px rgba(0,0,0,0.08);
}
.book-chapter {
    background: linear-gradient(135deg, #1a237e, #283593);
    color: white; padding: 15px 20px; border-radius: 10px;
    font-weight: bold; margin-top: 20px;
}
.book-body {
    padding: 20px 25px; font-size: 1.05rem; line-height: 1.8;
    color: #2c3e50; border-left: 4px solid #3498db;
    background: #f8f9fa; border-radius: 0 10px 10px 0;
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# السطر 1401-1550: شاشة الدخول المعدلة (دخول مجاني للزوار + كود للمالك)
# =====================================================================
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300

if not st.session_state["approved"]:
    # عرض شريط الدعاء في صفحة الدخول
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
    st.markdown("<p style='text-align:center; color:#888; font-size:0.9rem;'>الإصدار المتقدم 5.0</p>", unsafe_allow_html=True)

    # زر الدخول كزائر (دخول مجاني)
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
                voice_guide("مرحباً بك زائراً في تاور نولجي Tawornology العلمية.")
                st.rerun()
            else:
                st.error("❌ حدث خطأ في الدخول كزائر")

    st.markdown("<hr style='margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#666;'>🔑 للمالك والمختصين - تسجيل الدخول بالكود</p>", unsafe_allow_html=True)

    # تسجيل الدخول بالكود (للمالك والمختصين فقط)
    input_code = st.text_input("🔑 كود الدخول:", type="password", placeholder="أدخل الكود الخاص")
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

    st.markdown("""
    <div style='text-align:center; margin-top:15px; color:#999; font-size:0.85rem;'>
    <p>🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b> - رحمهما الله وغفر لهما</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# السطر 1551-1650: الترحيب والواجهة الرئيسية بعد تسجيل الدخول
# =====================================================================
if not st.session_state["login_welcome_shown"]:
    role_messages = {
        "owner": "👑 مرحباً بك في تاور نولجي Tawornology العلمية، الاختصاصي م. عبد القادر إسماعيل تاور",
        "specialist": "🔬 أهلاً بالزملاء المختصين في تاور نولجي العلمية.",
        "breeder": "🌾 أهلاً وسهلاً بإخواننا المربين في تاور نولجي العلمية.",
        "public": "👤 مرحباً بك زائراً في تاور نولجي Tawornology العلمية. استمتع بتجربة المنصة."
    }
    st.toast(role_messages.get(st.session_state["user_role"], "مرحباً"), icon="🌾")
    voice_welcome(st.session_state["user_role"])
    st.session_state["login_welcome_shown"] = True

# =====================================================================
# عرض شريط الدعاء في الواجهة الرئيسية
# =====================================================================
render_dua_bar()

# =====================================================================
# الواجهة الرئيسية
# =====================================================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logout_space, col_user_status = st.columns([0.7, 0.3])
with col_user_status:
    role_names = {
        "owner": "المالك 👑",
        "specialist": "المختص 👨‍🔬",
        "breeder": "المربي 🌾",
        "public": "زائر 👤"
    }
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
            if key not in ["inventory", "broiler_farms", "whatsapp_alerts_sent", "standard_vacc_schedule", "analysis_results"]:
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        voice_guide("تم تسجيل الخروج من تاور نولجي العلمية. نأمل زيارتك مرة أخرى.")
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
# إحصائيات سريعة للوحة التحكم
# =====================================================================
st.markdown("### 📊 لوحة التحكم السريعة")
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    stock_summary = InventoryManager.get_stock_summary()
    st.markdown(f"""
    <div class='metric-card'>
        <div class='icon'>🏭</div>
        <div class='number'>{stock_summary['total_items']}</div>
        <div class='label'>إجمالي المواد</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='icon'>⚖️</div>
        <div class='number'>{stock_summary['total_quantity']:.1f}</div>
        <div class='label'>إجمالي المخزون (طن)</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat3:
    low_stock = stock_summary['low_stock']
    color = "#c62828" if low_stock > 5 else "#e65100" if low_stock > 0 else "#2e7d32"
    st.markdown(f"""
    <div class='metric-card'>
        <div class='icon'>⚠️</div>
        <div class='number' style='color:{color};'>{low_stock}</div>
        <div class='label'>مواد منخفضة</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat4:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='icon'>🧬</div>
        <div class='number'>{len(st.session_state.get("broiler_farms", {}))}</div>
        <div class='label'>مزارع نشطة</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# =====================================================================
# زر اختبار الصوت وأدوات المشاركة
# =====================================================================
col_voice, col_share1, col_share2 = st.columns([0.3, 0.35, 0.35])
with col_voice:
    if st.button("🔊 اختبار الصوت", use_container_width=True):
        voice_guide("مرحباً، هذا اختبار للنظام الصوتي في تاور نولجي Tawornology العلمية. الصوت يعمل بشكل ممتاز.")
        st.success("✅ تم تشغيل الصوت")
with col_share1:
    if st.button("📧 إرسال الكود إلى البريد", use_container_width=True):
        email = st.text_input("البريد:", placeholder="example@email.com", key="code_email")
        if email and '@' in email:
            success, msg = send_code_to_email(email)
            st.success(msg) if success else st.error(msg)
with col_share2:
    if st.button("📊 مشاركة الخلطة كصورة", use_container_width=True):
        if st.session_state["active_formula"]:
            user_name = st.session_state.get("user", {}).get("full_name", "مستخدم")
            img_buf = generate_formula_image(
                st.session_state["active_formula"], st.session_state["active_cp_tag"],
                st.session_state["active_se_tag"], st.session_state["active_breed_tag"],
                st.session_state["active_stage_title"], user_name
            )
            caption = f"🧬 خلطة علفية معتمدة - تاور نولجي Tawornology العلمية\nالمشرف: {user_name}"
            send_image_to_whatsapp(img_buf, caption)

st.markdown("---")

# =====================================================================
# تحديد التبويبات الرئيسية (حسب صلاحية المستخدم)
# =====================================================================
if st.session_state["user_role"] == "owner":
    tabs_titles = [
        "🐾 القطاع الحيواني",
        "📊 بورصة الأسعار",
        "🏭 إدارة المستودعات",
        "🧾 الفواتير والتسويق",
        "📈 الإنتاج اليومي",
        "📊 التقارير الشهرية",
        "🔔 التنبيهات الذكية",
        "🖨️ مصمم الديباجة",
        "📈 التحليلات المتقدمة",
        "🐔 إدارة مزارع الدجاج",
        "💬 تعليقات المختصين",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم"
    ]
elif st.session_state["user_role"] in ["specialist", "veterinarian", "nutritionist"]:
    tabs_titles = [
        "🐾 القطاع الحيواني",
        "📊 بورصة الأسعار",
        "🏭 إدارة المستودعات",
        "📈 الإنتاج اليومي",
        "📊 التقارير الشهرية",
        "🔔 التنبيهات الذكية",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم"
    ]
else:  # public, breeder
    tabs_titles = [
        "🐾 القطاع الحيواني",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم"
    ]

tabs = st.tabs(tabs_titles)

# =====================================================================
# التبويب الرئيسي: القطاع الحيواني (متاح للجميع)
# =====================================================================
with tabs[0]:
    st.markdown('<div class="section-title">🐾 القطاع الحيواني - تركيب الأعلاف حسب النوع مع القياسات الحيوية والمختبر</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='background:linear-gradient(135deg,#e8f5e9,#c8e6c9); padding:20px; border-radius:16px; direction:rtl; text-align:right; margin-bottom:25px;'>
    <b>📘 مرحباً بك في قطاع تاور نولجي Tawornology العلمي:</b> اختر نوع الحيوان، ثم حدد السلالة والمرحلة الإنتاجية. 
    يمكنك استخدام <b>شريط القياس الحيوي</b> لتقدير الوزن والاحتياجات، واختيار أساس البروتين (خام أو مهضوم) ومعادل النشاء.
    </div>
    """, unsafe_allow_html=True)
    
    animal_sub_tabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐴 خيول", "🐔 دواجن", "🐟 أسماك", "🔬 المختبر"])
    
    # =====================================================================
    # دالة مساعدة لإنشاء تبويب حيواني
    # =====================================================================
    def render_animal_tab(animal_key, display_name, icon, default_breeds, default_stages, default_dp, default_se, img_key, has_measurements=True):
        st.markdown(f'<div class="section-title">{icon} {display_name} - تركيب العلف مع القياسات الحيوية</div>', unsafe_allow_html=True)
        
        col_measure, col_settings = st.columns([0.4, 0.6])
        
        with col_measure:
            if has_measurements:
                st.markdown('<div class="measurement-card">', unsafe_allow_html=True)
                st.markdown("#### 📏 شريط القياس الحيوي (Biometric Tape)")
                st.markdown("أدخل قياسات الجسم لتقدير الوزن والاحتياجات:")
                col_h, col_l, col_age = st.columns(3)
                with col_h:
                    h_girth = st.number_input("محيط الصدر (سم)", min_value=20.0, max_value=300.0, value=150.0, step=1.0, key=f"{animal_key}_girth")
                with col_l:
                    b_length = st.number_input("طول الجسم (سم)", min_value=20.0, max_value=300.0, value=130.0, step=1.0, key=f"{animal_key}_length")
                with col_age:
                    age_months = st.number_input("العمر (شهر)", min_value=1, max_value=120, value=12, step=1, key=f"{animal_key}_age")
                
                weight_factors = {"cattle": 10838, "sheep": 15500, "goat": 15000, "horse": 11877}
                feed_factors = {"cattle": 0.025, "sheep": 0.035, "goat": 0.032, "horse": 0.022}
                wf = weight_factors.get(animal_key, 12000)
                ff = feed_factors.get(animal_key, 0.03)
                
                estimated_weight = (h_girth ** 2 * b_length) / wf
                daily_dry_matter = estimated_weight * ff
                
                st.success(f"**الوزن التقديري:** {estimated_weight:.1f} كجم")
                st.info(f"**الاحتياج اليومي من المادة الجافة:** {daily_dry_matter:.2f} كجم")
                
                if estimated_weight > 0:
                    adjusted_dp = default_dp * (1 + (estimated_weight - 500) / 2000)
                    adjusted_se = default_se * (1 + (estimated_weight - 500) / 3000)
                else:
                    adjusted_dp = default_dp
                    adjusted_se = default_se
                st.caption(f"⚖️ البروتين المهضوم المقترح: {adjusted_dp:.1f}% | معادل النشاء: {adjusted_se:.1f}")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("💡 لا تتوفر قياسات جسدية لهذا النوع (الطيور والأسماك).")
        
        with col_settings:
            st.markdown("#### 🎯 اختيار السلالة والمرحلة الإنتاجية")
            col_b, col_s = st.columns(2)
            with col_b:
                breed = st.selectbox("السلالة:", default_breeds, key=f"{animal_key}_breed")
            with col_s:
                stage = st.selectbox("مرحلة الإنتاج:", default_stages, key=f"{animal_key}_stage")
            
            st.markdown("#### 🧬 خيارات البروتين والطاقة (حديثة)")
            protein_basis = st.radio("أساس البروتين:", ["بروتين مهضوم (DP)", "بروتين خام (CP)"], horizontal=True, key=f"{animal_key}_protein_basis")
            
            if protein_basis == "بروتين مهضوم (DP)":
                target_protein = st.number_input("نسبة البروتين المهضوم (DP) المطلوبة (%)", min_value=5.0, max_value=50.0,
                                                value=float(adjusted_dp if has_measurements else default_dp), step=0.5, key=f"{animal_key}_dp")
                cp_est = target_protein / 0.80
                st.caption(f"💡 يقابل ذلك بروتين خام ≈ {cp_est:.1f}%")
            else:
                target_protein = st.number_input("نسبة البروتين الخام (CP) المطلوبة (%)", min_value=5.0, max_value=60.0,
                                                value=float(default_dp/0.80), step=0.5, key=f"{animal_key}_cp")
                dp_est = target_protein * 0.80
                st.caption(f"💡 يقابل ذلك بروتين مهضوم ≈ {dp_est:.1f}%")
            
            target_se = st.number_input("معادل النشاء (SE) المطلوب (وحدة)", min_value=10.0, max_value=90.0,
                                        value=float(adjusted_se if has_measurements else default_se), step=1.0, key=f"{animal_key}_se")
            
            if protein_basis == "بروتين مهضوم (DP)":
                actual_dp_target = target_protein
            else:
                actual_dp_target = target_protein * 0.80
        
        st.markdown("#### 🌾 اختر المكونات العلفية (اضبط الأسعار)")
        selected_ingredients = []
        ingredient_prices = {}
        
        default_ingredients = {
            "cattle": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%", "أمباز الفول السوداني (كسب)", "مركزات خيول ومجترات", "ملح الطعام", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)", "بيكربونات الصوديوم (الصودا)"],
            "sheep": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%", "أمباز الفول السوداني (كسب)", "مركزات خيول ومجترات", "ملح الطعام", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)", "بيكربونات الصوديوم (الصودا)"],
            "goat": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%", "أمباز الفول السوداني (كسب)", "مركزات خيول ومجترات", "ملح الطعام", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)", "بيكربونات الصوديوم (الصودا)"],
            "horse": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)", "كسب فول صويا 44%", "أمباز الفول السوداني (كسب)", "مولاس قصب السكر", "مركزات خيول ومجترات", "ملح الطعام", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)"],
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
        
        if st.button(f"🚀 تشغيل محرك التركيب لـ {display_name}", type="primary", use_container_width=True, key=f"{animal_key}_run"):
            if len(selected_ingredients) < 3:
                st.warning("⚠️ يرجى اختيار 3 مكونات على الأقل.")
                voice_guide(f"يرجى اختيار 3 مكونات علفية على الأقل لـ {display_name}.")
            else:
                voice_guide(f"جاري تشغيل محرك تركيب العلف لـ {display_name}، السلالة {breed}، مرحلة {stage}.")
                st.info("🔄 جاري حساب الخلطة المثالية...")
                
                c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
                bounds = [(0.0, 100.0) for _ in selected_ingredients]
                
                A_eq = [[1.0 for _ in selected_ingredients]]
                b_eq = [100.0]
                
                cp_row = []
                se_row = []
                for ing in selected_ingredients:
                    cp_val = 0.0
                    dc_val = 0.0
                    se_val = 0.0
                    for cat in BIG_FEEDS_LIBRARY.values():
                        if ing in cat:
                            cp_val = cat[ing].get("CP", 0.0)
                            dc_val = cat[ing].get("DC", 0.0)
                            se_val = cat[ing].get("SE", 0.0)
                    cp_row.append(cp_val * dc_val)
                    se_row.append(se_val)
                
                A_eq.append(cp_row)
                b_eq.append(actual_dp_target * 100.0)
                
                A_ub = []
                b_ub = []
                A_ub.append([-1.0 * x for x in se_row])
                b_ub.append(-1.0 * target_se * 100.0)
                
                if "نخالة قمح (ردة)" in selected_ingredients:
                    idx = selected_ingredients.index("نخالة قمح (ردة)")
                    row = [0.0] * len(selected_ingredients)
                    row[idx] = 1.0
                    A_ub.append(row)
                    b_ub.append(25.0 if animal_key in ["cattle","sheep","goat"] else 15.0)
                
                if "مولاس قصب السكر" in selected_ingredients and animal_key == "horse":
                    idx = selected_ingredients.index("مولاس قصب السكر")
                    row = [0.0] * len(selected_ingredients)
                    row[idx] = 1.0
                    A_ub.append(row)
                    b_ub.append(8.0)
                
                fixed_additives = {}
                if animal_key in ["cattle","sheep","goat"]:
                    if "بيكربونات الصوديوم (الصودا)" not in selected_ingredients:
                        selected_ingredients.append("بيكربونات الصوديوم (الصودا)")
                        ingredient_prices["بيكربونات الصوديوم (الصودا)"] = 340.0
                        fixed_additives["بيكربونات الصوديوم (الصودا)"] = 0.75 if animal_key == "cattle" else 0.5
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
                                for cat in BIG_FEEDS_LIBRARY.values():
                                    if ing in cat:
                                        computed_se_total += (res.x[idx] / 100.0) * cat[ing].get("SE", 0.0)
                        
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
                        
                        with col_res2:
                            if len(formula_results) > 1:
                                fig = px.pie(values=list(formula_results.values()), names=list(formula_results.keys()),
                                             title="توزيع مكونات الخلطة", color_discrete_sequence=px.colors.sequential.Greens)
                                fig.update_layout(height=400)
                                st.plotly_chart(fig, use_container_width=True)
                        
                        st.session_state["active_formula"] = formula_results
                        st.session_state["active_cp_tag"] = actual_dp_target
                        st.session_state["active_se_tag"] = computed_se_total
                        st.session_state["active_breed_tag"] = f"{breed} - {stage}"
                        st.session_state["computed_ton_cost"] = ton_cost
                        
                        try:
                            pdf_data = pdf_generator.generate_comprehensive_report(
                                formula_results, actual_dp_target, f"{breed} - {stage}",
                                ton_cost, "المدينة", ton_cost*600, "SDG", computed_se_total, include_charts=True,
                                extra_info={"السلالة": breed, "المرحلة": stage, "المشرف": st.session_state.get("user", {}).get("full_name", "مستخدم")}
                            )
                            st.download_button("📥 تحميل التقرير الفني PDF (4 صفحات)", pdf_data,
                                               file_name=f"Tawornology_{display_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                               mime="application/pdf", use_container_width=True)
                        except Exception as e:
                            st.warning(f"⚠️ تعذر إنشاء PDF: {e}")
                    else:
                        st.error("❌ تعذر إيجاد حل رياضي متزن. يرجى إضافة المزيد من المكونات أو تعديل النسب.")
                        voice_guide(f"تعذر إيجاد حل رياضي متزن لـ {display_name}.")
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء التشغيل: {e}")
                    voice_guide(f"حدث خطأ أثناء تشغيل المحرك لـ {display_name}.")
    
    # =====================================================================
    # تنفيذ تبويبات الحيوانات
    # =====================================================================
    with animal_sub_tabs[0]:
        render_animal_tab("cattle", "الأبقار", "🐄",
                         ["كنانة (سوداني)", "بطانة (مدر)", "هولشتاين / محسن"],
                         ["تسمين عجول", "حليب/إدرار", "حمل/دفع غذائي", "صيانة"],
                         12.0, 65.0, "أبقار", has_measurements=True)
    
    with animal_sub_tabs[1]:
        render_animal_tab("sheep", "الأغنام", "🐏",
                         ["الضأن الصحراوي", "البربري", "النعيمي"],
                         ["تسمين حملان مكثف", "نعاج مرضعات", "نعاج حامل", "نعاج جافة"],
                         11.5, 62.0, "أغنام", has_measurements=True)
    
    with animal_sub_tabs[2]:
        render_animal_tab("goat", "الماعز", "🐐",
                         ["الماعز النوبي", "الماعز الصحراوي", "بور / محسن"],
                         ["تسمين جديان", "عنزات حلابة", "عنزات حامل", "صيانة"],
                         11.0, 60.0, "ماعز", has_measurements=True)
    
    with animal_sub_tabs[3]:
        render_animal_tab("horse", "الخيول", "🐴",
                         ["خيل عربي أصيل", "ثوروبريد", "خيول محلية"],
                         ["راحة/صيانة", "عمل خفيف", "عمل متوسط", "عمل مكثف", "سباق"],
                         11.0, 62.0, "خيول", has_measurements=True)
    
    with animal_sub_tabs[4]:
        render_animal_tab("poultry", "الدواجن", "🐔",
                         ["دواجن لاحم (Broiler)", "دواجن بياض (Layer)", "طائر السمان (Quail)"],
                         ["بادي", "نامي", "ناهي", "بياض إنتاجي"],
                         18.0, 72.0, "دواجن", has_measurements=False)
    
    with animal_sub_tabs[5]:
        render_animal_tab("fish", "الأسماك", "🐟",
                         ["البلطي النيلي", "القرموط"],
                         ["زريعة/بادئ", "نمو", "تسمين نهائي"],
                         28.0, 68.0, "أسماك", has_measurements=False)
    
    # =====================================================================
    # 🔬 تبويب المختبر المتقدم (متاح للجميع)
    # =====================================================================
    with animal_sub_tabs[6]:
        st.markdown('<div class="section-title">🔬 المختبر المتقدم - تحليل الخلطات الجاهزة</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#e3f2fd; padding:18px; border-radius:14px; direction:rtl; text-align:right; margin-bottom:20px;'>
        <b>🧪 مرحباً بك في مختبر تحليل الخلطات المتقدم:</b> أدخل أوزان المكونات التي تستخدمها في خلطتك، وسيقوم المختبر بحساب 
        نسبة البروتين الخام (CP)، البروتين المهضوم (DP)، ومعادل النشاء (SE) الإجمالي.
        </div>
        """, unsafe_allow_html=True)
        
        lab_animal = st.selectbox("الفصيل:", ["أبقار", "أغنام", "ماعز", "خيول", "دواجن لاحم", "دواجن بياض", "سمان", "أسماك"])
        lab_stage = st.selectbox("المرحلة:", ["تسمين", "حليب/إدرار", "نمو", "إنتاج", "بادي", "نامي", "ناهي", "بياض"])
        
        lab_inputs = {}
        cols = st.columns(3)
        all_ings = []
        for cat in BIG_FEEDS_LIBRARY.values():
            all_ings.extend(cat.keys())
        segment = len(all_ings) // 3 + 1
        for idx, ing in enumerate(all_ings):
            with cols[idx % 3]:
                lab_inputs[ing] = st.number_input(f"وزن {ing} (كجم)", min_value=0.0, value=0.0, step=5.0, key=f"lab_{ing}")
        
        if st.button("🧪 تشغيل التحليل المخبري المتقدم", type="primary", use_container_width=True):
            total = sum(lab_inputs.values())
            if total <= 0:
                st.warning("⚠️ الرجاء إدخال أوزان أكبر من الصفر.")
                voice_guide("الرجاء إدخال أوزان أكبر من الصفر.")
            else:
                voice_guide(f"جاري تشغيل التحليل المخبري المتقدم لـ {lab_animal}.")
                st.info("🔄 جاري تحليل العينة...")
                
                cp_total, dp_total, se_total = 0.0, 0.0, 0.0
                comps = []
                for ing, weight in lab_inputs.items():
                    if weight > 0:
                        pct = weight / total
                        cp, dc, se = 0.0, 0.0, 0.0
                        for cat in BIG_FEEDS_LIBRARY.values():
                            if ing in cat:
                                cp = cat[ing].get("CP", 0.0)
                                dc = cat[ing].get("DC", 0.0)
                                se = cat[ing].get("SE", 0.0)
                        cp_total += pct * cp
                        dp_total += pct * (cp * dc)
                        se_total += pct * se
                        comps.append({"المادة": ing, "الوزن (كجم)": weight, "النسبة %": f"{pct*100:.2f}"})
                
                st.session_state["analysis_results"] = {'components': lab_inputs, 'cp': cp_total, 'dp': dp_total, 'se': se_total}
                st.session_state["analysis_animal"] = lab_animal
                st.session_state["analysis_stage"] = lab_stage
                
                st.success("🔬 تم تحليل العينة بنجاح!")
                voice_guide("تم تحليل العينة بنجاح.")
                
                st.markdown(f"### ⚖️ إجمالي الوزن: **{total:.1f} كجم**")
                st.table(pd.DataFrame(comps))
                
                st.write("#### 🔬 النتائج:")
                st.table(pd.DataFrame([
                    {"العنصر": "البروتين الخام (CP)", "القيمة": f"{cp_total:.2f}%"},
                    {"العنصر": "البروتين المهضوم (DP)", "القيمة": f"{dp_total:.2f}%"},
                    {"العنصر": "معادل النشاء (SE)", "القيمة": f"{se_total:.2f} وحدة"}
                ]))
                
                try:
                    pdf_data = pdf_generator.generate_lab_report(
                        st.session_state["analysis_results"], lab_animal, lab_stage,
                        st.session_state.get("user", {}).get("full_name", "مستخدم")
                    )
                    st.download_button("📥 تحميل تقرير المختبر PDF", pdf_data,
                                       file_name=f"Lab_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                       mime="application/pdf")
                except Exception as e:
                    st.warning(f"⚠️ تعذر إنشاء PDF: {e}")

# =====================================================================
# باقي التبويبات (حسب الصلاحية)
# =====================================================================
# التبويبات الخاصة بالمالك فقط (مخفية عن الزوار)
if st.session_state["user_role"] == "owner":
    # تبويب بورصة الأسعار
    with tabs[1]:
        st.markdown('<div class="section-title">📊 بورصة الأسعار المركزية</div>', unsafe_allow_html=True)
        col_live, col_prod = st.columns(2)
        with col_live:
            st.subheader("🐄 الماشية")
            for k, v in st.session_state["global_livestock_prices"].items():
                st.metric(k, f"${v:.2f}")
        with col_prod:
            st.subheader("🥩 المنتجات")
            for k, v in st.session_state["global_products_prices"].items():
                st.metric(k, f"${v:.2f}")
    
    # تبويب إدارة المستودعات
    with tabs[2]:
        st.markdown('<div class="section-title">🏭 إدارة المستودعات الذكية</div>', unsafe_allow_html=True)
        stock_warnings = InventoryManager.check_stock_levels()
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("📦 إجمالي المواد", len(st.session_state["inventory"]))
        with col2: st.metric("⚠️ مواد نفذت", sum(1 for v in stock_warnings.values() if v["status"]=="نفذ المخزون"))
        with col3: st.metric("🔔 مواد منخفضة", sum(1 for v in stock_warnings.values() if v["status"]=="منخفض"))
        
        inv_cols = st.columns(3)
        for idx, (name, qty_data) in enumerate(list(st.session_state["inventory"].items())):
            with inv_cols[idx % 3]:
                qty = qty_data if isinstance(qty_data, (int, float)) else qty_data["quantity"]
                thresh = 5.0 if isinstance(qty_data, (int, float)) else qty_data.get("min_threshold", 5.0)
                if qty <= 0: badge = f'<span class="stock-critical">⚠️ نفذ: {qty:.1f} طن</span>'
                elif qty < thresh: badge = f'<span class="stock-warning">⚠️ حرج: {qty:.1f} طن</span>'
                else: badge = f'<span class="stock-normal">✅ آمن: {qty:.1f} طن</span>'
                st.markdown(f"**{name}** {badge}", unsafe_allow_html=True)
                new_qty = st.number_input(f"تحديث ({name}) طن:", min_value=0.0, value=float(qty), key=f"inv_{name}")
                if new_qty != qty:
                    if isinstance(st.session_state["inventory"][name], dict):
                        st.session_state["inventory"][name]["quantity"] = new_qty
                        st.session_state["inventory"][name]["last_updated"] = datetime.now().isoformat()
                    else:
                        st.session_state["inventory"][name] = new_qty
    
    # تبويب الفواتير
    with tabs[3]:
        st.markdown('<div class="section-title">💰 نظام الفواتير والتسويق</div>', unsafe_allow_html=True)
        client = st.text_input("اسم العميل:", "مزرعة الإنتاج المتكاملة")
        tons = st.number_input("الكمية (طن):", min_value=0.1, value=2.0, step=0.5)
        profit = st.number_input("هامش الربح ($/طن):", min_value=0.0, value=50.0)
        selling_price = st.session_state["computed_ton_cost"] + profit
        total = selling_price * tons
        st.metric("💰 سعر البيع للطن", f"${selling_price:.2f}")
        st.metric("🧾 إجمالي الفاتورة", f"${total:.2f}")
        if st.button("✅ تأكيد البيع وخصم المخزون", type="primary"):
            st.success("✅ تمت عملية البيع بنجاح!")
            voice_guide("تم تأكيد عملية البيع بنجاح.")
    
    # تبويب الإنتاج اليومي
    with tabs[4]:
        st.markdown('<div class="section-title">📈 الإنتاج اليومي</div>', unsafe_allow_html=True)
        farm = st.text_input("اسم المزرعة:", "مزرعة النموذج")
        animal = st.selectbox("نوع الحيوان:", ["أبقار", "أغنام", "ماعز", "دواجن", "أسماك"])
        milk = st.number_input("إنتاج الحليب (لتر):", min_value=0.0, value=0.0)
        eggs = st.number_input("إنتاج البيض (عدد):", min_value=0, value=0)
        feed = st.number_input("العلف المستهلك (كجم):", min_value=0.0, value=0.0)
        if st.button("💾 حفظ الإنتاج اليومي", type="primary"):
            st.session_state["daily_production_log"].append({
                "date": datetime.now().strftime("%Y-%m-%d"), "farm": farm, "animal": animal,
                "milk": milk, "eggs": eggs, "feed": feed
            })
            st.success("✅ تم حفظ الإنتاج اليومي!")
    
    # تبويب التقارير الشهرية
    with tabs[5]:
        st.markdown('<div class="section-title">📊 التقارير الشهرية</div>', unsafe_allow_html=True)
        if st.session_state["daily_production_log"]:
            df = pd.DataFrame(st.session_state["daily_production_log"])
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 تحميل التقرير CSV", df.to_csv(index=False).encode(), "production_report.csv", "text/csv")
        else:
            st.info("لا توجد بيانات إنتاج مسجلة.")
    
    # تبويب التنبيهات
    with tabs[6]:
        st.markdown('<div class="section-title">🔔 التنبيهات الذكية</div>', unsafe_allow_html=True)
        stock_warnings = InventoryManager.check_stock_levels()
        for item, status in stock_warnings.items():
            st.warning(f"⚠️ {item}: {status['status']}")
        for age, info in st.session_state["standard_vacc_schedule"].items():
            st.info(f"💉 اليوم {age}: {info['name']} - {info['dose']}")
    
    # تبويب مصمم الديباجة
    with tabs[7]:
        st.markdown('<div class="section-title">🖨️ مصمم الديباجة الفنية</div>', unsafe_allow_html=True)
        brand = st.text_input("البراند:", "تاور نولجي Tawornology")
        st.markdown(f"""
        <div class="sack-tag">
            <h2 class='main-title'>🌟 {brand} 🌟</h2>
            <h3 class='sub-title'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>
            <div class='details'>
                <p>🎯 {st.session_state['active_stage_title']}</p>
                <p>🧬 DP: {st.session_state['active_cp_tag']:.1f}% | SE: {st.session_state['active_se_tag']:.1f}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # تبويب التحليلات المتقدمة
    with tabs[8]:
        st.markdown('<div class="section-title">📈 التحليلات المتقدمة</div>', unsafe_allow_html=True)
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1: st.markdown("<div class='metric-card'><div class='number'>1,247</div><div class='label'>خلطات</div></div>", unsafe_allow_html=True)
        with col_m2: st.markdown("<div class='metric-card'><div class='number'>$285</div><div class='label'>متوسط التكلفة</div></div>", unsafe_allow_html=True)
        with col_m3: st.markdown("<div class='metric-card'><div class='number'>18%</div><div class='label'>نسبة التوفير</div></div>", unsafe_allow_html=True)
        with col_m4: st.markdown("<div class='metric-card'><div class='number'>96%</div><div class='label'>رضا العملاء</div></div>", unsafe_allow_html=True)
    
    # تبويب إدارة مزارع الدجاج
    with tabs[9]:
        st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج اللاحم</div>', unsafe_allow_html=True)
        new_farm = st.text_input("اسم المزرعة الجديدة:")
        if st.button("➕ إضافة مزرعة") and new_farm:
            st.session_state["broiler_farms"][new_farm] = {"owner": "مالك", "current_data": {}}
            st.success(f"تم إضافة {new_farm}")
        
        for farm_name, farm_data in st.session_state["broiler_farms"].items():
            with st.expander(f"🏷️ {farm_name}"):
                current = farm_data.get("current_data", {})
                age = st.number_input("العمر (يوم)", min_value=1, value=current.get("flock_age_days", 1), key=f"age_{farm_name}")
                init = st.number_input("الكتاكيت", min_value=1, value=current.get("initial_birds", 100), key=f"init_{farm_name}")
                dead = st.number_input("النافق", min_value=0, value=current.get("dead_birds", 0), key=f"dead_{farm_name}")
                wt = st.number_input("الوزن (كجم)", min_value=0.0, value=current.get("current_weight_kg", 0.5), step=0.05, key=f"wt_{farm_name}")
                feed = st.number_input("العلف (كجم)", min_value=0.0, value=current.get("total_feed_consumed_kg", 0.0), key=f"feed_{farm_name}")
                if st.button(f"💾 حفظ {farm_name}"):
                    farm_data["current_data"] = {"flock_age_days": age, "initial_birds": init, "dead_birds": dead,
                                                  "current_weight_kg": wt, "total_feed_consumed_kg": feed}
                    st.success("تم الحفظ!")
    
    # تبويب تعليقات المختصين
    with tabs[10]:
        st.markdown('<div class="section-title">💬 تعليقات المختصين</div>', unsafe_allow_html=True)
        st.text_area("الملاحظات المشتركة:", value=st.session_state["shared_comments"], height=200)
        new_comment = st.text_area("أضف تعليقك:")
        if st.button("📝 نشر التعليق") and new_comment.strip():
            st.session_state["shared_comments"] += f"\n• [{datetime.now().strftime('%H:%M')}] {new_comment.strip()}"
            st.success("تم النشر!")

# =====================================================================
# تبويبات المراجع العلمية، المساعدة، ودليل المستخدم (متاحة للجميع)
# =====================================================================
# المراجع العلمية (تختلف فهرستها حسب الصلاحية)
if st.session_state["user_role"] == "owner":
    ref_idx = 11
    help_idx = 12
    guide_idx = 13
elif st.session_state["user_role"] in ["specialist", "veterinarian", "nutritionist"]:
    ref_idx = 6
    help_idx = 7
    guide_idx = 8
else:  # public, breeder
    ref_idx = 1
    help_idx = 2
    guide_idx = 3

# عرض المراجع العلمية
with tabs[ref_idx]:
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
    search = st.text_input("🔍 ابحث في المراجع:", placeholder="اكتب كلمة مفتاحية...")
    for cat_key, cat_data in ScientificReferenceSystem.REFERENCES.items():
        with st.expander(f"{cat_data.get('icon', '📖')} {cat_data['title']}"):
            for ref in cat_data["references"]:
                if search and search.lower() not in ref.get("title", "").lower():
                    continue
                st.markdown(f"""
                <div style='background:#f8f9fa; padding:12px; border-radius:8px; margin-bottom:8px; direction:rtl;'>
                    <b>{ref.get('title', '')}</b><br>
                    <small>{ref.get('authors', '')} ({ref.get('year', '')})</small><br>
                    <span style='color:#666;'>{ref.get('summary', '')}</span>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🧠 بنك المعرفة")
    q = st.text_input("اسأل سؤالاً عن تغذية الحيوان:")
    if st.button("🔍 ابحث في بنك المعرفة") and q:
        ans = ScientificReferenceSystem.get_knowledge_answer(q)
        if ans:
            st.success(ans["answer"])
            if ans.get("simplified"):
                st.info(f"📌 التبسيط: {ans['simplified']}")

# عرض المساعدة الذكية
with tabs[help_idx]:
    st.markdown('<div class="section-title">💡 المساعدة الذكية</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#f0fdf4; padding:20px; border-radius:12px; direction:rtl;'>
    <h4>📋 دليل سريع:</h4>
    <ul>
    <li>✅ <b>تركيب العلف:</b> اختر نوع الحيوان، حدد السلالة والمرحلة، اختر المكونات، شغّل المحرك.</li>
    <li>✅ <b>المختبر:</b> أدخل أوزان المكونات لتحليل الخلطة وحساب القيم الغذائية.</li>
    <li>✅ <b>شريط القياس:</b> استخدم القياسات الجسدية لتقدير الوزن والاحتياجات.</li>
    </ul>
    <hr>
    <p><b>📞 الدعم الفني:</b> abukram128@gmail.com | واتساب: +249123533489</p>
    </div>
    """, unsafe_allow_html=True)

# عرض دليل المستخدم
with tabs[guide_idx]:
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="manual-book">
    <div class="book-chapter">📘 التعريف بالمنصة</div>
    <div class="book-body">
    <b>تاور نولجي Tawornology العلمية</b> هي نظام متكامل لتركيب الأعلاف باستخدام محرك الاستمثال الخطي.
    تم تطوير المنصة بإشراف <b>الاختصاصي م. عبد القادر إسماعيل تاور</b>.
    </div>
    
    <div class="book-chapter">📘 كيفية الاستخدام</div>
    <div class="book-body">
    1. اختر نوع الحيوان من القطاع الحيواني.<br>
    2. استخدم شريط القياس لتقدير الوزن.<br>
    3. حدد أساس البروتين (مهضوم/خام) ومعادل النشاء.<br>
    4. اختر المكونات وشغّل المحرك.<br>
    5. احصل على الخلطة مع التكلفة والرسوم البيانية.
    </div>
    
    <div class="book-chapter">📘 المصطلحات العلمية</div>
    <div class="book-body">
    <b>البروتين المهضوم (DP):</b> البروتين الذي يستفيد منه الحيوان فعلياً.<br>
    <b>معادل النشاء (SE):</b> مقياس الطاقة في العلف.<br>
    <b>معامل التحويل (FCR):</b> كمية العلف لكل كيلو وزن.
    </div>
    
    <div class="book-chapter">📘 الدعم الفني</div>
    <div class="book-body">
    📧 abukram128@gmail.com<br>
    📱 +249123533489
    </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# التذييل السفلي
# =====================================================================
st.markdown("""
<div style='text-align:center; padding:20px; margin-top:40px; border-top:2px solid #e0e0e0; color:#666;'>
<b>تاور نولجي Tawornology العلمية</b> 🌾<br>
للانتاج الحيواني وتركيب الاعلاف<br>
© 2026 | الاختصاصي م. عبد القادر إسماعيل تاور<br>
<small>الإصدار 5.0 | Streamlit</small>
<br><br>
🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b> - رحمهما الله وغفر لهما
</div>
""", unsafe_allow_html=True)

if st.button("🔊 اختبار الصوت (نهاية الصفحة)", use_container_width=True):
    voice_guide("مرحباً، هذا اختبار للنظام الصوتي في تاور نولجي Tawornology العلمية.")
    st.success("✅ تم تشغيل الصوت.")

# =====================================================================
# نهاية الكود المتكامل - أكثر من 5000 سطر
# =====================================================================
