# =====================================================================
# منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف - النسخة المتكاملة
# المشرف العام: الاختصاصي عبدالقادر إسماعيل تاور
# الإصدار: 3.0 - تطوير شامل مع كافة الأساسيات
# =====================================================================

import os
import streamlit as st
import pandas as pd
import numpy as np
import json
import base64
import hashlib
import secrets
import re
import io
import time
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from functools import lru_cache
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# =====================================================================
# المكتبات العلمية
# =====================================================================
from scipy.optimize import linprog
from scipy.spatial import ConvexHull
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
import requests
import qrcode
from PIL import Image as PILImage

# =====================================================================
# مكتبات معالجة النصوص العربية والصوت
# =====================================================================
import arabic_reshaper
from bidi.algorithm import get_display
from gtts import gTTS

# =====================================================================
# مكتبات PDF
# =====================================================================
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
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.font_manager as fm

# =====================================================================
# قاعدة البيانات (SQLite)
# =====================================================================
import sqlite3
from contextlib import contextmanager

# =====================================================================
# تكوين الصفحة
# =====================================================================
st.set_page_config(
    page_title="منصة تاور العلمية - النسخة المتكاملة",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================================
# الثوابت والإعدادات
# =====================================================================

class UserRole(Enum):
    OWNER = "owner"
    SPECIALIST = "specialist"
    BREEDER = "breeder"

class AnimalType(Enum):
    CATTLE = "أبقار"
    SHEEP = "أغنام"
    GOAT = "ماعز"
    HORSE = "خيول"
    POULTRY = "دواجن"
    FISH = "أسماك"
    QUAIL = "سمان"
    OTHER = "أخرى"

# إعدادات الأمان
if 'secrets' in dir(st):
    SENDER_EMAIL = st.secrets.get("email", {}).get("sender", "abukram128@gmail.com")
    SENDER_PASSWORD = st.secrets.get("email", {}).get("password", "")
else:
    SENDER_EMAIL = os.environ.get("EMAIL_SENDER", "abukram128@gmail.com")
    SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")

OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"
GOOGLE_FORM_URL = "https://forms.google.com/YOUR_FORM_URL"

# إعدادات SMTP
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# دوال التشفير
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# المستخدمون المسموح لهم
AUTH_USERS = {
    "abukram": {
        "password_hash": hash_password("Admin@2026"),
        "role": UserRole.OWNER,
        "name": "الاختصاصي عبدالقادر إسماعيل تاور",
        "email": "abukram128@gmail.com"
    },
    "specialist": {
        "password_hash": hash_password("Specialist@2026"),
        "role": UserRole.SPECIALIST,
        "name": "المختص والزملاء",
        "email": "specialist@tower.com"
    },
    "breeder": {
        "password_hash": hash_password("Breeder@2026"),
        "role": UserRole.BREEDER,
        "name": "المربي",
        "email": "breeder@tower.com"
    }
}

# =====================================================================
# مكتبة الأعلاف الموسعة (كما في الأصل)
# =====================================================================

BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة الكبرى": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6},
        "جريش أرز رزاز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2},
        "دخن محلي غزير": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0}
    },
    "🌱 الأكساب وأمبازات مصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5}
    },
    "🚜 المخلفات الزراعية والصناعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5},
        "بقايا تفل البنجر المجفف": {"CP": 8.0, "DC": 0.75, "SE": 58.0, "NDF": 38.5, "ADF": 22.5, "EE": 1.5, "ASH": 6.5},
        "مخلفات مصانع البسكويت": {"CP": 9.5, "DC": 0.88, "SE": 76.0, "NDF": 8.5, "ADF": 3.5, "EE": 8.5, "ASH": 3.5}
    },
    "🧬 مصادر البروتين الحيواني والمركزات": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق أسماك فاخر (72%)": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5}
    },
    "🧪 الأحماض الأمينية البلورية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3},
        "ثريونين نقي (L-Threonine)": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2},
        "تريبتوفان نقي (L-Tryptophan)": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1}
    },
    "🔬 الإنزيمات والإضافات التخصصية": {
        "بريمكس تسمين دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس بياض وبشاير": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس أبقار حلابة": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم الفايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
        "إنزيم الـ NSP": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0},
        "خميرة الخبز": {"CP": 45.0, "DC": 0.90, "SE": 55.0, "NDF": 5.0, "ADF": 2.0, "EE": 2.0, "ASH": 6.0},
        "مسحوق الحليب (كامل الدسم)": {"CP": 25.0, "DC": 0.95, "SE": 60.0, "NDF": 0.0, "ADF": 0.0, "EE": 26.0, "ASH": 8.0},
        "دهن نباتي": {"CP": 0.0, "DC": 0.0, "SE": 85.0, "NDF": 0.0, "ADF": 0.0, "EE": 99.0, "ASH": 0.5},
        "زيت سمك": {"CP": 0.0, "DC": 0.0, "SE": 80.0, "NDF": 0.0, "ADF": 0.0, "EE": 98.0, "ASH": 0.5}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
        "يوريا علفية محصنة": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0}
    }
}

# =====================================================================
# الأسعار العالمية والمواقع
# =====================================================================

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG", "currency_name": "جنيه سوداني"},
    "LIBYA": {"rate": 4.80, "sym": "LYD", "currency_name": "دينار ليبي"},
    "مصر": {"rate": 48.0, "sym": "EGP", "currency_name": "جنيه مصري"},
    "باقي دول العالم": {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"}
}

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

# =====================================================================
# إدارة قاعدة البيانات المتكاملة
# =====================================================================

class DatabaseManager:
    """مدير قاعدة البيانات المتكامل"""
    
    def __init__(self, db_path: str = "tower_platform.db"):
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_database(self):
        """تهيئة قاعدة البيانات وجداولها"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # جدول المزارع
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS farms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT,
                    animal_type TEXT,
                    breed TEXT,
                    purpose TEXT,
                    head_count INTEGER DEFAULT 0,
                    start_date DATE,
                    feeding_system TEXT,
                    owner_id TEXT,
                    area REAL,
                    workers_count INTEGER DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول المجموعات الحيوانية
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS animal_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farm_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    group_type TEXT,
                    head_count INTEGER DEFAULT 0,
                    average_weight REAL DEFAULT 0,
                    birth_date DATE,
                    purchase_date DATE,
                    expected_sale_date DATE,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
                )
            ''')
            
            # جدول السجلات اليومية
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    record_date DATE NOT NULL,
                    average_weight REAL DEFAULT 0,
                    feed_given REAL DEFAULT 0,
                    feed_refused REAL DEFAULT 0,
                    deaths INTEGER DEFAULT 0,
                    sold INTEGER DEFAULT 0,
                    health_score INTEGER DEFAULT 5,
                    production_amount REAL DEFAULT 0,
                    production_unit TEXT,
                    temperature REAL,
                    humidity REAL,
                    water_consumption REAL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES animal_groups (id) ON DELETE CASCADE
                )
            ''')
            
            # جدول السجلات الصحية
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    event_date DATE NOT NULL,
                    event_type TEXT,
                    diagnosis TEXT,
                    treatment TEXT,
                    veterinarian TEXT,
                    cost REAL DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES animal_groups (id) ON DELETE CASCADE
                )
            ''')
            
            # جدول التلقيح والتكاثر
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reproduction_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    insemination_date DATE,
                    expected_birth DATE,
                    birth_date DATE,
                    offspring_count INTEGER DEFAULT 0,
                    offspring_weight REAL,
                    success BOOLEAN DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES animal_groups (id) ON DELETE CASCADE
                )
            ''')
            
            # جدول استهلاك الأعلاف
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feed_consumption (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    feed_date DATE NOT NULL,
                    feed_type TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    cost REAL DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES animal_groups (id) ON DELETE CASCADE
                )
            ''')
            
            # جدول المعاملات المالية
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS financial_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farm_id INTEGER NOT NULL,
                    transaction_date DATE NOT NULL,
                    type TEXT NOT NULL,
                    category TEXT,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (farm_id) REFERENCES farms (id) ON DELETE CASCADE
                )
            ''')
            
            # جدول التحصينات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vaccination_schedule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    vaccine_name TEXT NOT NULL,
                    due_date DATE NOT NULL,
                    administered BOOLEAN DEFAULT 0,
                    administration_date DATE,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES animal_groups (id) ON DELETE CASCADE
                )
            ''')
            
            # جدول المخزون
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL UNIQUE,
                    quantity REAL DEFAULT 0,
                    unit TEXT DEFAULT 'طن',
                    min_threshold REAL DEFAULT 5.0,
                    supplier TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            ''')
            
            conn.commit()
            
            # تهيئة المخزون إذا كان فارغاً
            cursor.execute("SELECT COUNT(*) FROM inventory")
            if cursor.fetchone()[0] == 0:
                for category, items in BIG_FEEDS_LIBRARY.items():
                    for item_name in items:
                        cursor.execute('''
                            INSERT INTO inventory (item_name, quantity, unit, min_threshold)
                            VALUES (?, ?, ?, ?)
                        ''', (item_name, 25.0, 'طن', 5.0))
                conn.commit()
    
    # ===== عمليات CRUD للمزارع =====
    
    def create_farm(self, data: dict) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO farms (name, location, animal_type, breed, purpose, 
                                  head_count, start_date, feeding_system, area, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('name'),
                data.get('location'),
                data.get('animal_type'),
                data.get('breed'),
                data.get('purpose'),
                data.get('head_count', 0),
                data.get('start_date'),
                data.get('feeding_system'),
                data.get('area', 0),
                data.get('notes')
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_farms(self, filters: dict = None) -> List[dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM farms"
            params = []
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(f"{key} = ?")
                    params.append(value)
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_farm(self, farm_id: int) -> Optional[dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM farms WHERE id = ?", (farm_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_farm(self, farm_id: int, data: dict):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            values = list(data.values()) + [farm_id]
            cursor.execute(f"UPDATE farms SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
            conn.commit()
    
    def delete_farm(self, farm_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM farms WHERE id = ?", (farm_id,))
            conn.commit()
    
    # ===== عمليات المجموعات =====
    
    def create_group(self, data: dict) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO animal_groups (farm_id, name, group_type, head_count, 
                                          average_weight, birth_date, purchase_date, 
                                          expected_sale_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('farm_id'),
                data.get('name'),
                data.get('group_type'),
                data.get('head_count', 0),
                data.get('average_weight', 0),
                data.get('birth_date'),
                data.get('purchase_date'),
                data.get('expected_sale_date'),
                data.get('notes')
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_groups(self, farm_id: int = None) -> List[dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if farm_id:
                cursor.execute("SELECT * FROM animal_groups WHERE farm_id = ?", (farm_id,))
            else:
                cursor.execute("SELECT * FROM animal_groups")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_group(self, group_id: int) -> Optional[dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM animal_groups WHERE id = ?", (group_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_group(self, group_id: int, data: dict):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            values = list(data.values()) + [group_id]
            cursor.execute(f"UPDATE animal_groups SET {set_clause} WHERE id = ?", values)
            conn.commit()
    
    # ===== عمليات السجلات اليومية =====
    
    def add_daily_record(self, data: dict) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO daily_records (group_id, record_date, average_weight, feed_given,
                                          feed_refused, deaths, sold, health_score,
                                          production_amount, production_unit, temperature,
                                          humidity, water_consumption, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('group_id'),
                data.get('record_date'),
                data.get('average_weight', 0),
                data.get('feed_given', 0),
                data.get('feed_refused', 0),
                data.get('deaths', 0),
                data.get('sold', 0),
                data.get('health_score', 5),
                data.get('production_amount', 0),
                data.get('production_unit'),
                data.get('temperature'),
                data.get('humidity'),
                data.get('water_consumption'),
                data.get('notes')
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_daily_records(self, group_id: int, start_date: str = None, end_date: str = None) -> List[dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM daily_records WHERE group_id = ?"
            params = [group_id]
            if start_date:
                query += " AND record_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND record_date <= ?"
                params.append(end_date)
            query += " ORDER BY record_date DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # ===== عمليات السجلات الصحية =====
    
    def add_health_record(self, data: dict) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO health_records (group_id, event_date, event_type, diagnosis,
                                           treatment, veterinarian, cost, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('group_id'),
                data.get('event_date'),
                data.get('event_type'),
                data.get('diagnosis'),
                data.get('treatment'),
                data.get('veterinarian'),
                data.get('cost', 0),
                data.get('notes')
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_health_records(self, group_id: int) -> List[dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM health_records WHERE group_id = ? ORDER BY event_date DESC", (group_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ===== عمليات التكاثر =====
    
    def add_reproduction_record(self, data: dict) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reproduction_records (group_id, insemination_date, expected_birth,
                                                  birth_date, offspring_count, offspring_weight,
                                                  success, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('group_id'),
                data.get('insemination_date'),
                data.get('expected_birth'),
                data.get('birth_date'),
                data.get('offspring_count', 0),
                data.get('offspring_weight'),
                data.get('success', 0),
                data.get('notes')
            ))
            conn.commit()
            return cursor.lastrowid
    
    # ===== عمليات استهلاك الأعلاف =====
    
    def add_feed_consumption(self, data: dict) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feed_consumption (group_id, feed_date, feed_type, quantity, cost, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data.get('group_id'),
                data.get('feed_date'),
                data.get('feed_type'),
                data.get('quantity', 0),
                data.get('cost', 0),
                data.get('notes')
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_feed_consumption(self, group_id: int, start_date: str = None, end_date: str = None) -> List[dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM feed_consumption WHERE group_id = ?"
            params = [group_id]
            if start_date:
                query += " AND feed_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND feed_date <= ?"
                params.append(end_date)
            query += " ORDER BY feed_date DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # ===== عمليات المخزون =====
    
    def get_inventory(self) -> List[dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inventory ORDER BY item_name")
            return [dict(row) for row in cursor.fetchall()]
    
    def update_inventory(self, item_name: str, quantity: float):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE inventory SET quantity = ?, last_updated = CURRENT_TIMESTAMP
                WHERE item_name = ?
            ''', (quantity, item_name))
            conn.commit()
    
    def get_inventory_item(self, item_name: str) -> Optional[dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inventory WHERE item_name = ?", (item_name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def deduct_inventory(self, item_name: str, quantity: float) -> bool:
        """خصم من المخزون مع التحقق من الكفاية"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM inventory WHERE item_name = ?", (item_name,))
            row = cursor.fetchone()
            if row and row[0] >= quantity:
                cursor.execute('''
                    UPDATE inventory SET quantity = quantity - ?, last_updated = CURRENT_TIMESTAMP
                    WHERE item_name = ?
                ''', (quantity, item_name))
                conn.commit()
                return True
            return False
    
    # ===== التحليلات المتقدمة =====
    
    def get_group_performance(self, group_id: int, days: int = 30) -> dict:
        """تحليل أداء المجموعة للفترة المحددة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM animal_groups WHERE id = ?", (group_id,))
            group = cursor.fetchone()
            if not group:
                return {'error': 'المجموعة غير موجودة'}
            
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT * FROM daily_records 
                WHERE group_id = ? AND record_date >= ?
                ORDER BY record_date
            ''', (group_id, cutoff_date))
            records = [dict(row) for row in cursor.fetchall()]
            
            if not records:
                return {'error': 'لا توجد سجلات كافية للتحليل'}
            
            df = pd.DataFrame(records)
            
            # حساب المؤشرات
            if 'average_weight' in df.columns and len(df) > 1:
                weight_gain = df['average_weight'].iloc[-1] - df['average_weight'].iloc[0]
                days_diff = (datetime.strptime(df['record_date'].iloc[-1], '%Y-%m-%d') - 
                            datetime.strptime(df['record_date'].iloc[0], '%Y-%m-%d')).days
                adg = weight_gain / max(days_diff, 1)
            else:
                adg = 0
            
            total_feed = df['feed_given'].sum() - df['feed_refused'].sum()
            total_gain = df['average_weight'].iloc[-1] - df['average_weight'].iloc[0]
            fcr = total_feed / max(total_gain, 0.001)
            
            total_deaths = df['deaths'].sum()
            mortality_rate = (total_deaths / max(group['head_count'], 1)) * 100
            
            return {
                'group_name': group['name'],
                'period_days': days,
                'adg': round(adg, 2),
                'fcr': round(fcr, 2),
                'mortality_rate': round(mortality_rate, 2),
                'average_weight_start': round(df['average_weight'].iloc[0], 2),
                'average_weight_end': round(df['average_weight'].iloc[-1], 2),
                'total_feed_consumed': round(total_feed, 2),
                'total_deaths': total_deaths,
                'health_score_avg': round(df['health_score'].mean(), 1) if 'health_score' in df else 0,
                'records_count': len(records)
            }

# =====================================================================
# معالجة النصوص العربية
# =====================================================================

class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=1000)
    def fix_arabic_text(text: str) -> str:
        if not text:
            return ""
        try:
            reshaped = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped)
            return bidi_text
        except:
            return text
    
    @staticmethod
    def remove_diacritics(text: str) -> str:
        diacritics = re.compile(r'[\u064B-\u0652\u0670]')
        text = re.sub(diacritics, '', text)
        text = re.sub(r'([.،])', r'\1 ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

arabic_processor = ArabicTextProcessor()

# =====================================================================
# توليد الصوت
# =====================================================================

def text_to_speech(text: str, lang: str = 'ar') -> Optional[io.BytesIO]:
    try:
        cleaned = arabic_processor.remove_diacritics(text)
        tts = gTTS(text=cleaned, lang=lang, slow=False)
        audio = io.BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)
        return audio
    except Exception as e:
        st.error(f"⚠️ فشل توليد الصوت: {e}")
        return None

def play_welcome_audio():
    welcome_text = """السلام عليكم ورحمة الله وبركاته. مرحباً بكم في منصة تاور العلمية المطورة للانتاج الحيواني وتركيب الاعلاف. هذه المنصة تقدم حلولاً متقدمة لتركيب الأعلاف بأقل تكلفة باستخدام الذكاء الاصطناعي والتحليل الكمي. كما توفر إدارة متكاملة للمزارع وبورصة الأسعار وتحليلات متقدمة. مع تحيات الاختصاصي عبدالقادر إسماعيل تاور."""
    audio = text_to_speech(welcome_text)
    if audio:
        st.audio(audio, format='audio/mp3')

def play_guide_audio():
    guide_text = """مرحباً بكم في دليل منصة تاور العلمية المطورة. هذه المنصة مصممة لمساعدة المربين والمختصين في تركيب أعلاف متوازنة بأقل تكلفة، وإدارة المزارع بشكل متكامل. يمكنكم استخدام التبويبات المختلفة للوصول إلى جميع الوظائف. نتمنى لكم تجربة مفيدة."""
    audio = text_to_speech(guide_text)
    if audio:
        st.audio(audio, format='audio/mp3')

# =====================================================================
# توليد التقارير PDF المتقدمة
# =====================================================================

class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        try:
            pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
            self.font_name = 'Amiri'
        except:
            pass
    
    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, 
                                     local_cost, local_sym, computed_se, include_charts=True) -> bytes:
        """توليد تقرير فني شامل للخلطة"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50,
                               topMargin=50, bottomMargin=50)
        story = []
        
        def p(text, size=12, align=TA_RIGHT, color=HexColor('#000000')):
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, ParagraphStyle('style', fontName=self.font_name,
                                                       fontSize=size, alignment=align,
                                                       textColor=color, spaceAfter=6, 
                                                       leading=size*1.5))
        
        # العنوان
        story.append(p("تقرير فني شامل - منصة تاور العلمية", size=22, align=TA_CENTER,
                      color=HexColor('#1b5e20')))
        story.append(Spacer(1, 12))
        
        # معلومات أساسية
        for line in [
            f"المشرف العام: الاختصاصي عبدالقادر إسماعيل تاور",
            f"الموقع الجغرافي: {city}",
            f"الفصيل المستهدف: {breed}",
            f"تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ]:
            story.append(p(line, size=11))
        story.append(Spacer(1, 15))
        
        # الجدول الأساسي
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
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        
        # المكونات
        story.append(p("المقادير المعتمدة لتركيب الطن الواحد:", size=14, color=HexColor('#2e7d32')))
        story.append(Spacer(1, 10))
        
        ing_data = [[arabic_processor.fix_arabic_text('المكون'), 
                     arabic_processor.fix_arabic_text('النسبة %'), 
                     arabic_processor.fix_arabic_text('كجم/طن')]]
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
        ]))
        story.append(t2)
        story.append(Spacer(1, 15))
        
        # الرسوم البيانية
        if include_charts and len(formula) > 1:
            try:
                fig, ax = plt.subplots(figsize=(6, 3.5))
                names = list(formula.keys())
                vals = list(formula.values())
                colors = ['#1b5e20','#2e7d32','#388e3c','#43a047','#4caf50','#66bb6a']
                ax.pie(vals, labels=None, autopct='%1.1f%%', colors=colors[:len(names)])
                ax.legend([arabic_processor.fix_arabic_text(n) for n in names], 
                         title=arabic_processor.fix_arabic_text("المكونات"),
                         loc='center left', bbox_to_anchor=(1,0,0.5,1), fontsize=8)
                ax.set_title(arabic_processor.fix_arabic_text('توزيع المكونات'), fontsize=12)
                
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=400, height=230))
            except:
                pass
        
        # تذييل
        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026 | تحت إشراف الاختصاصي عبدالقادر إسماعيل تاور",
                      size=9, align=TA_CENTER, color=HexColor('#666666')))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_farm_report(self, farm: dict, groups: List[dict], records: List[dict]) -> bytes:
        """توليد تقرير شامل للمزرعة"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50,
                               topMargin=50, bottomMargin=50)
        story = []
        
        def p(text, size=12, align=TA_RIGHT, color=HexColor('#000000')):
            safe = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe, ParagraphStyle('style', fontName=self.font_name,
                                                 fontSize=size, alignment=align,
                                                 textColor=color, spaceAfter=6, 
                                                 leading=size*1.5))
        
        story.append(p("تقرير المزرعة الشامل - منصة تاور العلمية", size=22, align=TA_CENTER,
                      color=HexColor('#1b5e20')))
        story.append(Spacer(1, 12))
        
        # معلومات المزرعة
        story.append(p(f"اسم المزرعة: {farm.get('name', 'غير محدد')}", size=12))
        story.append(p(f"الموقع: {farm.get('location', 'غير محدد')}", size=12))
        story.append(p(f"نوع الحيوان: {farm.get('animal_type', 'غير محدد')}", size=12))
        story.append(p(f"السلالة: {farm.get('breed', 'غير محدد')}", size=12))
        story.append(Spacer(1, 15))
        
        # المجموعات
        story.append(p("المجموعات الحيوانية:", size=14, color=HexColor('#2e7d32')))
        if groups:
            for group in groups:
                story.append(p(f"• {group.get('name')}: {group.get('head_count')} رأس", size=11))
        story.append(Spacer(1, 15))
        
        # الإحصائيات
        if records:
            df = pd.DataFrame(records)
            story.append(p("ملخص الإحصائيات:", size=14, color=HexColor('#2e7d32')))
            story.append(p(f"عدد السجلات: {len(records)}", size=11))
            if 'average_weight' in df.columns:
                story.append(p(f"متوسط الوزن: {df['average_weight'].mean():.1f} كجم", size=11))
            if 'feed_given' in df.columns:
                story.append(p(f"إجمالي العلف المقدم: {df['feed_given'].sum():.1f} كجم", size=11))
            if 'production_amount' in df.columns:
                story.append(p(f"متوسط الإنتاج: {df['production_amount'].mean():.1f}", size=11))
        
        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026", size=9, align=TA_CENTER,
                      color=HexColor('#666666')))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# =====================================================================
# محرك تحسين الأعلاف المتقدم
# =====================================================================

class FeedOptimizer:
    """محرك التحسين الخطي المتقدم للأعلاف"""
    
    @staticmethod
    def optimize_feed(ingredients: List[str], prices: Dict[str, float],
                     target_dp: float, target_se: float,
                     fixed_additives: Dict[str, float] = None,
                     use_cp_basis: bool = False,
                     additional_constraints: Dict[str, float] = None) -> Dict[str, Any]:
        """تحسين الخلطة باستخدام البرمجة الخطية"""
        
        if fixed_additives is None:
            fixed_additives = {}
        if additional_constraints is None:
            additional_constraints = {}
        
        n = len(ingredients)
        c_vector = [prices.get(ing, 100.0) for ing in ingredients]
        
        # حدود المكونات
        bounds = []
        for ing in ingredients:
            if ing in fixed_additives:
                bounds.append((fixed_additives[ing], fixed_additives[ing]))
            else:
                bounds.append((0.0, 100.0))
        
        # معادلة المجموع = 100%
        A_eq = [[1.0] * n]
        b_eq = [100.0]
        
        # حساب البروتين والطاقة
        cp_row = []
        se_row = []
        for ing in ingredients:
            cp_val = 0.0
            dc_val = 0.0
            se_val = 0.0
            for category in BIG_FEEDS_LIBRARY.values():
                if ing in category:
                    cp_val = category[ing].get("CP", 0.0)
                    dc_val = category[ing].get("DC", 0.0)
                    se_val = category[ing].get("SE", 0.0)
                    break
            
            if use_cp_basis:
                cp_row.append(cp_val)
            else:
                cp_row.append(cp_val * dc_val)
            se_row.append(se_val)
        
        A_eq.append(cp_row)
        if use_cp_basis:
            b_eq.append(target_dp * 100.0)
        else:
            b_eq.append(target_dp * 100.0)
        
        # قيود الطاقة
        A_ub = []
        b_ub = []
        A_ub.append([-1.0 * x for x in se_row])
        b_ub.append(-1.0 * target_se * 100.0)
        
        # قيود الحبوب للمجترات
        grain_indicators = [1.0 if any(ing in cat for cat in BIG_FEEDS_LIBRARY["🌾 الحبوب ومصادر الطاقة الكبرى"].keys()) 
                           else 0.0 for ing in ingredients]
        if sum(grain_indicators) > 0:
            A_ub.append([-1.0 * x for x in grain_indicators])
            b_ub.append(-50.0)
        
        # قيود إضافية
        for constraint_name, limit in additional_constraints.items():
            if constraint_name in ingredients:
                idx = ingredients.index(constraint_name)
                row = [0.0] * n
                row[idx] = 1.0
                A_ub.append(row)
                b_ub.append(limit)
        
        # حل المشكلة
        res = linprog(c_vector, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                     bounds=bounds, method='highs')
        
        if not res.success:
            # محاولة مع قيود مخففة
            A_ub_flex = []
            b_ub_flex = []
            A_ub_flex.append([-1.0 * x for x in se_row])
            b_ub_flex.append(-1.0 * (target_se - 3.0) * 100.0)
            if sum(grain_indicators) > 0:
                A_ub_flex.append([-1.0 * x for x in grain_indicators])
                b_ub_flex.append(-40.0)
            
            res = linprog(c_vector, A_ub=A_ub_flex, b_ub=b_ub_flex,
                         A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        
        if res.success:
            formula = {}
            for idx, ing in enumerate(ingredients):
                if res.x[idx] > 0.0001:
                    formula[ing] = res.x[idx]
            
            total_cost = res.fun / 100.0
            
            # حساب SE الفعلي
            actual_se = 0.0
            for ing, pct in formula.items():
                for category in BIG_FEEDS_LIBRARY.values():
                    if ing in category:
                        actual_se += (pct / 100.0) * category[ing].get("SE", 0.0)
                        break
            
            return {
                'success': True,
                'formula': formula,
                'cost_per_ton': total_cost,
                'actual_se': actual_se,
                'message': 'تم تحسين الخلطة بنجاح'
            }
        else:
            return {
                'success': False,
                'message': 'تعذر إيجاد حل رياضي متزن. يرجى إضافة خامات أخرى أو تعديل المعايير.'
            }

# =====================================================================
# إدارة المخزون الذكية
# =====================================================================

class InventoryManager:
    @staticmethod
    def check_stock_levels(db: DatabaseManager) -> Dict[str, str]:
        """فحص مستويات المخزون"""
        inventory = db.get_inventory()
        warnings = {}
        for item in inventory:
            if item['quantity'] <= 0:
                warnings[item['item_name']] = "نفذ المخزون"
            elif item['quantity'] < item['min_threshold']:
                warnings[item['item_name']] = "منخفض"
        return warnings
    
    @staticmethod
    def get_low_stock_items(db: DatabaseManager, threshold: float = 5.0) -> List[dict]:
        """الحصول على المواد منخفضة المخزون"""
        inventory = db.get_inventory()
        return [item for item in inventory if item['quantity'] < threshold]

# =====================================================================
# بورصة الأسعار والمواقع
# =====================================================================

class MarketPriceEngine:
    @staticmethod
    @lru_cache(maxsize=128)
    def get_adjusted_market_data(country: str, state_or_region: str, city: str) -> Dict[str, float]:
        """الحصول على أسعار السوق المعدلة حسب الموقع"""
        feed_prices = {}
        for category in BIG_FEEDS_LIBRARY.values():
            for ing in category:
                feed_prices[ing] = 230.0
        
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
            "خميرة الخبز": 500.0, "مسحوق الحليب": 850.0,
            "دهن نباتي": 650.0, "زيت سمك": 1200.0
        }
        feed_prices.update(base_prices)
        
        multiplier = 1.0
        if country == "السودان":
            multiplier = 1.15
            if "كردفان" in state_or_region or state_or_region == "إقليم النيل الأزرق":
                multiplier = 1.20
                feed_prices["سورجم (فتريتة)"] *= 0.85
                feed_prices["أمباز الفول السوداني (كسب)"] *= 0.85
            elif state_or_region in ["ولاية القضارف", "ولاية الجزيرة"]:
                feed_prices["سورجم (فتريتة)"] *= 0.82
                feed_prices["أمباز الفول السوداني (كسب)"] *= 0.88
        elif country == "LIBYA":
            multiplier = 1.10
            if city == "طبرق":
                multiplier = 1.06
        elif country == "مصر":
            multiplier = 1.04
        
        for k in feed_prices:
            feed_prices[k] *= multiplier
        
        return feed_prices

# =====================================================================
# دوال جلب الأسعار من الروابط
# =====================================================================

def fetch_prices_from_url(url: str, mapping: Dict[str, str]) -> Dict[str, float]:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        result = {}
        for key, json_key in mapping.items():
            if json_key in data:
                result[key] = float(data[json_key])
        return result
    except Exception as e:
        st.error(f"⚠️ فشل جلب البيانات من {url}: {e}")
        return {}

def update_all_prices_from_feeds():
    """تحديث جميع الأسعار من الروابط المحفوظة"""
    if 'price_feeds' not in st.session_state:
        st.session_state.price_feeds = {}
    
    feeds = st.session_state.price_feeds
    updated = False
    
    for region, urls in feeds.items():
        if "livestock" in urls and urls["livestock"]:
            mapping = {
                "عجول تسمين هولشتاين": "beef",
                "أبقار كنانة": "local_cattle",
                "ضأن وستيرلنغ": "sheep",
                "ماعز نوبي": "goat",
                "خيول عربية": "horse"
            }
            new_prices = fetch_prices_from_url(urls["livestock"], mapping)
            if new_prices:
                for k, v in new_prices.items():
                    if 'global_livestock_prices' in st.session_state:
                        st.session_state.global_livestock_prices[k] = v
                updated = True
        
        if "products" in urls and urls["products"]:
            mapping = {
                "كيلو لحم بقري": "beef_meat",
                "كيلو لحم ضأن": "lamb_meat",
                "كيلو لحم دجاج": "chicken_meat",
                "طبق بيض": "eggs",
                "لتر حليب": "milk"
            }
            new_prices = fetch_prices_from_url(urls["products"], mapping)
            if new_prices:
                for k, v in new_prices.items():
                    if 'global_products_prices' in st.session_state:
                        st.session_state.global_products_prices[k] = v
                updated = True
        
        if "feeds" in urls and urls["feeds"]:
            mapping = {
                "ذرة صفراء": "corn",
                "كسب فول صويا": "soybean",
                "نخالة قمح": "wheat_bran"
            }
            new_prices = fetch_prices_from_url(urls["feeds"], mapping)
            if new_prices:
                if 'live_feed_prices' in st.session_state:
                    st.session_state.live_feed_prices.update(new_prices)
                updated = True
    
    if updated:
        st.session_state.last_price_update = datetime.now().isoformat()
        st.success(f"✅ تم تحديث الأسعار بنجاح في {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info("ℹ️ لم يتم تحديث أي أسعار (تأكد من الروابط).")

# =====================================================================
# دوال إرسال البريد الإلكتروني
# =====================================================================

def send_code_to_mail(receiver_email: str, attachment_type: str = "full") -> bool:
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        st.error("⚠️ خطأ إعدادات: يرجى تحديث بيانات الـ SMTP")
        return False
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود الكامل - منصة تاور العلمية"
    
    body = """السلام عليكم الاختصاصي عبدالقادر،

مرفق مع هذه الرسالة النسخة البرمجية الكاملة والمستقرة لمنصتكم الذكية (منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف).

تحياتي الهندسية."""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        # إرفاق الكود
        try:
            current_file = __file__
            with open(current_file, "r", encoding="utf-8") as f:
                code_content = f.read()
        except NameError:
            code_content = "# كود المنصة مأرشيف داخلياً\n"
        
        file_hash = hashlib.md5(code_content.encode()).hexdigest()
        code_content = f"# Digital Signature: {file_hash}\n# Generated: {datetime.now().isoformat()}\n\n{code_content}"
        
        attachment = MIMEText(code_content, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', 
                            filename="tower_scientific_platform.py")
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

# =====================================================================
# الواجهة الرئيسية
# =====================================================================

def main():
    """الوظيفة الرئيسية للتطبيق"""
    
    db = DatabaseManager()
    
    # تهيئة حالة الجلسة
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'active_formula' not in st.session_state:
        st.session_state.active_formula = {}
    if 'computed_ton_cost' not in st.session_state:
        st.session_state.computed_ton_cost = 0.0
    if 'global_livestock_prices' not in st.session_state:
        st.session_state.global_livestock_prices = {
            "عجول تسمين هولشتاين": 1350.0,
            "أبقار كنانة": 900.0,
            "ضأن وستيرلنغ": 180.0,
            "ماعز نوبي": 130.0,
            "خيول عربية": 4500.0
        }
    if 'global_products_prices' not in st.session_state:
        st.session_state.global_products_prices = {
            "كيلو لحم بقري": 7.50,
            "كيلو لحم ضأن": 9.00,
            "كيلو لحم دجاج": 3.80,
            "طبق بيض": 4.20,
            "لتر حليب": 0.90
        }
    if 'live_feed_prices' not in st.session_state:
        st.session_state.live_feed_prices = {}
    if 'shared_comments' not in st.session_state:
        st.session_state.shared_comments = "• [توجيه الاختصاصي]: يرجى من جميع الزملاء إضافة تعليقاتهم هنا لتبادل الخبرات.\n"
    
    # ===== واجهة تسجيل الدخول =====
    if not st.session_state.authenticated:
        show_login_page()
        return
    
    # ===== تشغيل الصوت الترحيبي =====
    if 'welcome_played' not in st.session_state:
        play_welcome_audio()
        st.session_state.welcome_played = True
    
    # ===== الواجهة الرئيسية =====
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    * { font-family: 'Cairo', sans-serif; }
    .main-box { background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.15); margin-bottom: 30px; }
    .section-title { color: #1b5e20; border-right: 5px solid #2e7d32; padding-right: 15px; 
                     font-size: 1.5rem; font-weight: bold; margin: 30px 0 20px 0; }
    .formula-item { background: linear-gradient(135deg, #f5f5f5, #e8f5e9); padding: 12px 20px; 
                    border-radius: 10px; margin-bottom: 8px; border-right: 4px solid #2e7d32; 
                    font-weight: bold; color: #1b5e20; }
    .price-card { background: linear-gradient(135deg, #f1f8e9, #e8f5e9); padding: 20px; 
                  border-radius: 12px; border-right: 5px solid #2e7d32; margin-bottom: 20px; }
    .warning-card { background: linear-gradient(135deg, #fff3e0, #ffe0b2); padding: 15px; 
                    border-radius: 12px; border-right: 5px solid #f57c00; margin-bottom: 15px; 
                    color: #e65100; }
    .metric-card { background: white; padding: 20px; border-radius: 15px; 
                   box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; 
                   transition: transform 0.3s ease; }
    .metric-card:hover { transform: translateY(-5px); }
    .profile-img { width: 150px; height: 150px; border-radius: 50%; object-fit: cover; 
                   border: 4px solid #d4af37; box-shadow: 0 6px 20px rgba(0,0,0,0.25); 
                   display: block; margin: 0 auto; }
    .sack-tag { border: 3px dashed #1b5e20; padding: 30px; border-radius: 15px; 
                background: linear-gradient(135deg, #f1f8e9, #e8f5e9); text-align: right; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    
    # رأس الصفحة
    col_logo, col_title = st.columns([0.2, 0.8])
    with col_logo:
        st.image("https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=150&h=150&fit=crop", 
                use_container_width=True)
    with col_title:
        st.markdown("<h1 style='color: #1b5e20; text-align:right;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف 🌾</h1>", 
                   unsafe_allow_html=True)
        st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.2rem;'>محرك الاستمثال الخطي المتقدم القائم على البروتين المهضوم (DP) ومعادل النشاء (SE)</p>", 
                   unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: #c62828; text-align:right; font-weight: bold;'>المشرف العام: {st.session_state.user.get('name', '')}</h3>", 
                   unsafe_allow_html=True)
    
    st.markdown("---")
    
    # معلومات المستخدم
    col_user, col_logout = st.columns([0.8, 0.2])
    with col_user:
        role_icons = {"owner": "👑", "specialist": "👨‍🔬", "breeder": "🌾"}
        role_names = {"owner": "المالك", "specialist": "المختص", "breeder": "المربي"}
        icon = role_icons.get(st.session_state.user['role'].value, "👤")
        role_name = role_names.get(st.session_state.user['role'].value, "مستخدم")
        st.info(f"{icon} {st.session_state.user.get('name', '')} - {role_name}")
    with col_logout:
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    st.markdown("---")
    
    # ===== رسالة ترحيبية =====
    welcome_messages = {
        "owner": "👑 أهلاً بك في منصتك، الاختصاصي عبدالقادر إسماعيل تاور. نظام التوازن الدقيق بالبروتين المهضوم ومعادل النشاء قيد التشغيل الآن بكفاءة متناهية.",
        "specialist": "🔬 مرحباً بكم في منصة تركيب وتحليل الأعلاف الذكية. يسعد الاختصاصي بالترحيب بالزملاء.",
        "breeder": "🚜 أهلاً وسهلاً بكم في منصة تاور العلمية. نوفر لكم خلطات مبنية على القيمة الغذائية الحقيقية."
    }
    current_welcome = welcome_messages.get(st.session_state.user['role'].value, "")
    if current_welcome:
        st.markdown(f"""<div style='background: #e8f5e9; padding: 15px; border-radius: 8px; 
                    border-right: 5px solid #2e7d32; text-align: right; margin-bottom: 20px;'>
                    <b>{current_welcome}</b></div>""", unsafe_allow_html=True)
    
    # ===== تحديد التبويبات حسب الدور =====
    if st.session_state.user['role'] == UserRole.OWNER:
        tabs = st.tabs([
            "🔬 تركيب الأعلاف",
            "📊 بورصة الأسعار",
            "🏭 إدارة المخزون",
            "🧾 التسويق والفواتير",
            "🖨️ مصمم الديباجة",
            "📈 التحليلات المتقدمة",
            "🐄 إدارة المزارع",
            "💬 تعليقات المختصين",
            "📖 دليل المستخدم"
        ])
    elif st.session_state.user['role'] == UserRole.SPECIALIST:
        tabs = st.tabs([
            "🔬 تركيب الأعلاف",
            "📊 بورصة الأسعار",
            "🏭 إدارة المخزون",
            "🧾 التسويق والفواتير",
            "📈 التحليلات المتقدمة",
            "🐄 إدارة المزارع",
            "💬 تعليقات المختصين",
            "📖 دليل المستخدم"
        ])
    else:
        tabs = st.tabs([
            "🔬 تركيب الأعلاف",
            "🐄 إدارة المزارع",
            "📖 دليل المستخدم"
        ])
    
    # =====================================================================
    # التبويب 1: تركيب الأعلاف
    # =====================================================================
    with tabs[0]:
        show_feed_formulation(db)
    
    # =====================================================================
    # التبويب 2: بورصة الأسعار
    # =====================================================================
    if len(tabs) > 1:
        with tabs[1]:
            show_market_prices()
    
    # =====================================================================
    # التبويب 3: إدارة المخزون
    # =====================================================================
    if len(tabs) > 2 and st.session_state.user['role'] in [UserRole.OWNER, UserRole.SPECIALIST]:
        with tabs[2]:
            show_inventory_management(db)
    
    # =====================================================================
    # التبويب 4: التسويق والفواتير
    # =====================================================================
    if len(tabs) > 3 and st.session_state.user['role'] in [UserRole.OWNER, UserRole.SPECIALIST]:
        with tabs[3]:
            show_marketing_invoicing()
    
    # =====================================================================
    # التبويب 5: مصمم الديباجة
    # =====================================================================
    if len(tabs) > 4 and st.session_state.user['role'] in [UserRole.OWNER, UserRole.SPECIALIST]:
        with tabs[4]:
            show_designer()
    
    # =====================================================================
    # التبويب 6: التحليلات المتقدمة
    # =====================================================================
    if len(tabs) > 5 and st.session_state.user['role'] in [UserRole.OWNER, UserRole.SPECIALIST]:
        with tabs[5]:
            show_advanced_analytics(db)
    
    # =====================================================================
    # التبويب 7: إدارة المزارع
    # =====================================================================
    farm_tab_index = 6 if st.session_state.user['role'] in [UserRole.OWNER, UserRole.SPECIALIST] else 1
    if len(tabs) > farm_tab_index:
        with tabs[farm_tab_index]:
            show_farm_management(db)
    
    # =====================================================================
    # التبويب 8: تعليقات المختصين
    # =====================================================================
    if len(tabs) > 7 and st.session_state.user['role'] in [UserRole.OWNER, UserRole.SPECIALIST]:
        with tabs[7]:
            show_comments()
    
    # =====================================================================
    # التبويب الأخير: دليل المستخدم
    # =====================================================================
    with tabs[-1]:
        show_user_guide()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== أرشفة الكود للمالك =====
    if st.session_state.user['role'] == UserRole.OWNER:
        st.markdown("---")
        st.markdown("<h3 style='color: #1565C0; text-align:right;'>📨 أرشفة شفرة المصدر</h3>", unsafe_allow_html=True)
        col_mail, col_btn = st.columns([0.7, 0.3])
        with col_mail:
            st.info(f"🔒 سيتم إرسال ملف الكود إلى: {OWNER_EMAIL}")
        with col_btn:
            if st.button("🚀 إرسال نسخة الكود للمالك", use_container_width=True):
                with st.spinner("جاري الإرسال..."):
                    if send_code_to_mail(OWNER_EMAIL):
                        st.success("✅ تم الإرسال بنجاح!")
    
    # ===== توقيع =====
    st.markdown("""
    <div style='position: fixed; bottom: 20px; left: 20px; background: linear-gradient(135deg, #1b5e20, #2e7d32);
                color: white; padding: 8px 20px; border-radius: 25px; font-size: 0.85rem; z-index: 9999;'>
        👨‍🔬 الاختصاصي عبدالقادر إسماعيل تاور © 2026
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# دالة عرض صفحة تسجيل الدخول
# =====================================================================

def show_login_page():
    """عرض صفحة تسجيل الدخول"""
    
    st.markdown("""
    <style>
    .login-box { max-width: 450px; margin: 80px auto; padding: 40px; 
                 background: rgba(255,255,255,0.95); border-radius: 20px; 
                 box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
    .login-title { text-align: center; color: #1b5e20; margin-bottom: 30px; }
    </style>
    <div class="login-box">
    """, unsafe_allow_html=True)
    
    st.markdown("<h2 class='login-title'>🔒 منصة تاور العلمية</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>نظام إدارة الثروة الحيوانية وتركيب الأعلاف</p>", 
                unsafe_allow_html=True)
    
    # عرض QR Code
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("https://tower-scientific-platform.streamlit.app")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        st.markdown(f'<div style="text-align: center; margin: 20px 0;">'
                   f'<img src="data:image/png;base64,{qr_base64}" width="150"></div>', 
                   unsafe_allow_html=True)
    except:
        pass
    
    # نموذج الدخول
    with st.form("login_form"):
        username = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم")
        password = st.text_input("🔑 كلمة المرور", type="password", placeholder="أدخل كلمة المرور")
        submitted = st.form_submit_button("🔓 تسجيل الدخول", use_container_width=True, type="primary")
        
        if submitted:
            if username in AUTH_USERS:
                user_data = AUTH_USERS[username]
                if hash_password(password) == user_data["password_hash"]:
                    st.session_state.authenticated = True
                    st.session_state.user = {
                        "username": username,
                        "name": user_data["name"],
                        "role": user_data["role"],
                        "email": user_data["email"]
                    }
                    st.rerun()
                else:
                    st.error("❌ كلمة المرور غير صحيحة")
            else:
                st.error("❌ اسم المستخدم غير موجود")
    
    st.markdown("""
    <div style='text-align: center; margin-top: 20px; color: #999; font-size: 0.9rem;'>
        <p>🔑 للمالك: abukram / Admin@2026</p>
        <p>👨‍🔬 للمختص: specialist / Specialist@2026</p>
        <p>🌾 للمربي: breeder / Breeder@2026</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================================
# دالة عرض تركيب الأعلاف
# =====================================================================

def show_feed_formulation(db: DatabaseManager):
    """عرض واجهة تركيب الأعلاف"""
    
    st.markdown('<div class="section-title">🌍 أولاً: تحديد الموقع الجغرافي</div>', unsafe_allow_html=True)
    
    col_country, col_state, col_city = st.columns(3)
    with col_country:
        user_country = st.selectbox("اختر الدولة:", list(EXCHANGE_RATES.keys()))
    with col_state:
        if user_country == "السودان":
            chosen_state = st.selectbox("اختر الولاية:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", 
                                                         "ولاية شمال كردفان", "ولاية جنوب كردفان"])
        elif user_country == "LIBYA":
            chosen_state = st.selectbox("اختر الإقليم:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
        else:
            chosen_state = st.selectbox("الإقليم:", ["المركز الرئيسي", "الأسواق المفتوحة"])
    with col_city:
        user_city = st.text_input("المدينة:", "الخرطوم")
    
    # أسعار السوق
    live_prices = MarketPriceEngine.get_adjusted_market_data(user_country, chosen_state, user_city)
    
    # عرض أسعار الماشية والمنتجات
    col_view1, col_view2 = st.columns(2)
    with col_view1:
        st.markdown(f'<div class="price-card"><b>📈 بورصة الماشية في ({user_city}):</b><br>' + 
                   "<br>".join([f'▪️ {k}: <b>${v:.2f}</b>' for k, v in st.session_state.global_livestock_prices.items()]) + 
                   "</div>", unsafe_allow_html=True)
    with col_view2:
        st.markdown(f'<div class="price-card"><b>🥩 بورصة المنتجات في ({user_city}):</b><br>' + 
                   "<br>".join([f'▪️ {k}: <b>${v:.2f}</b>' for k, v in st.session_state.global_products_prices.items()]) + 
                   "</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">⚖️ ثانياً: اختيار القطاع والإنتاج</div>', unsafe_allow_html=True)
    
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec:
        main_sector = st.selectbox("القطاع الإنتاجي:", 
                                   ["الأغنام", "الماعز", "الأبقار", "الخيول", "الدواجن", "الأسماك"])
    with col_sub:
        if main_sector == "الأغنام":
            sub_type = st.selectbox("السلالة:", ["الضأن الصحراوي", "البربري", "النعيمي"])
        elif main_sector == "الماعز":
            sub_type = st.selectbox("السلالة:", ["الماعز النوبي", "الماعز الصحراوي"])
        elif main_sector == "الأبقار":
            sub_type = st.selectbox("السلالة:", ["كنانة", "بطانة", "هولشتاين"])
        elif main_sector == "الخيول":
            sub_type = st.selectbox("السلالة:", ["خيل عربي أصيل", "ثوروبريد"])
        elif main_sector == "الدواجن":
            sub_type = st.selectbox("النوع:", ["لاحم", "بياض"])
        else:
            sub_type = st.selectbox("النوع:", ["بلطي", "قرموط"])
    
    with col_prod:
        if main_sector in ["الأغنام", "الماعز"]:
            prod_stage = st.selectbox("مرحلة الإنتاج:", ["تسمين", "حليب", "صيانة"])
            default_dp = 12.0 if "تسمين" in prod_stage else 11.0
        elif main_sector == "الأبقار":
            prod_stage = st.selectbox("مرحلة الإنتاج:", ["حليب", "تسمين"])
            default_dp = 12.5 if "حليب" in prod_stage else 10.0
        elif main_sector == "الدواجن":
            prod_stage = st.selectbox("مرحلة الإنتاج:", ["بادي", "نامي", "ناهي"])
            default_dp = 20.0 if "بادي" in prod_stage else (18.5 if "نامي" in prod_stage else 16.5)
        else:
            prod_stage = st.selectbox("مرحلة الإنتاج:", ["نمو", "تسمين"])
            default_dp = 12.0
    
    st.markdown('<div class="section-title">📋 رابعاً: حدود الموازنة</div>', unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        target_dp = st.slider("البروتين المهضوم المستهدف (DP %)", 5.0, 40.0, default_dp, 0.5)
    with col_p2:
        target_se = st.slider("معادل النشاء المستهدف (SE)", 10.0, 90.0, 65.0, 1.0)
    
    # اختيار المكونات
    st.markdown('<div class="section-title">📦 خامساً: اختيار المواد العلفية</div>', unsafe_allow_html=True)
    
    selected_ingredients = []
    ingredient_prices = {}
    
    for category, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(category, expanded=True):
            cols = st.columns(3)
            for idx, (name, _) in enumerate(items.items()):
                with cols[idx % 3]:
                    checked = st.checkbox(name, key=f"feed_{name}")
                    if checked:
                        selected_ingredients.append(name)
                        price = st.number_input(f"💰 {name} ($/طن)", min_value=1.0, 
                                               value=float(live_prices.get(name, 100.0)),
                                               step=5.0, key=f"price_{name}")
                        ingredient_prices[name] = price
    
    if not selected_ingredients:
        st.warning("⚠️ يرجى اختيار مكون واحد على الأقل")
        return
    
    # تشغيل المحرك
    if st.button("🚀 تشغيل محرك الاستمثال الخطي", type="primary", use_container_width=True):
        with st.spinner("جاري حساب الخلطة المثلى..."):
            result = FeedOptimizer.optimize_feed(
                ingredients=selected_ingredients,
                prices=ingredient_prices,
                target_dp=target_dp,
                target_se=target_se,
                fixed_additives={"ملح الطعام": 0.5}
            )
        
        if result['success']:
            st.success(f"✅ {result['message']}")
            
            st.session_state.active_formula = result['formula']
            st.session_state.computed_ton_cost = result['cost_per_ton']
            
            col_res1, col_res2 = st.columns([0.6, 0.4])
            with col_res1:
                st.markdown("### 📝 المقادير المعتمدة (لكل طن)")
                for name, pct in result['formula'].items():
                    st.markdown(f'<div class="formula-item">▪️ <b>{name}:</b> {pct:.2f}% ➡️ ({pct*10:.1f} كجم/طن)</div>', 
                               unsafe_allow_html=True)
                
                st.metric(f"💰 التكلفة للطن في {user_city}", f"${result['cost_per_ton']:.2f}")
                st.metric("🌽 معادل النشاء الفعلي", f"{result['actual_se']:.1f} وحدة")
                
                # مشاركة واتساب
                share_msg = f"منصة تاور العلمية - خلطة {sub_type} - {prod_stage}\nالتكلفة: ${result['cost_per_ton']:.2f}/طن\nالمشرف: الاختصاصي عبدالقادر إسماعيل تاور"
                encoded = urllib.parse.quote(share_msg)
                st.link_button("📲 مشاركة عبر واتساب", f"https://wa.me/?text={encoded}")
            
            with col_res2:
                # رسم بياني
                fig = px.pie(values=list(result['formula'].values()), 
                           names=list(result['formula'].keys()),
                           title="توزيع المكونات",
                           color_discrete_sequence=px.colors.sequential.Greens_r)
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # تحميل PDF
                try:
                    pdf = pdf_generator.generate_comprehensive_report(
                        result['formula'], target_dp, f"{sub_type} - {prod_stage}",
                        result['cost_per_ton'], user_city,
                        result['cost_per_ton'] * EXCHANGE_RATES.get(user_country, {}).get('rate', 1),
                        EXCHANGE_RATES.get(user_country, {}).get('sym', 'USD'),
                        result['actual_se']
                    )
                    st.download_button("📥 تحميل التقرير PDF", pdf, 
                                     file_name=f"feed_formula_{datetime.now().strftime('%Y%m%d')}.pdf",
                                     mime="application/pdf")
                except Exception as e:
                    st.error(f"⚠️ فشل توليد PDF: {e}")
        else:
            st.error(f"❌ {result['message']}")

# =====================================================================
# دالة عرض بورصة الأسعار
# =====================================================================

def show_market_prices():
    """عرض بورصة الأسعار"""
    
    st.markdown('<div class="section-title">📊 بورصة الأسعار المركزية</div>', unsafe_allow_html=True)
    
    tab_livestock, tab_products = st.tabs(["🐄 أسعار الماشية", "🥛 أسعار المنتجات"])
    
    with tab_livestock:
        st.subheader("أسعار الماشية")
        cols = st.columns(3)
        for idx, (name, price) in enumerate(st.session_state.global_livestock_prices.items()):
            with cols[idx % 3]:
                if st.session_state.user['role'] == UserRole.OWNER:
                    new_price = st.number_input(name, min_value=0.0, value=price, step=10.0, key=f"lv_{name}")
                    st.session_state.global_livestock_prices[name] = new_price
                else:
                    st.metric(name, f"${price:,.0f}")
    
    with tab_products:
        st.subheader("أسعار المنتجات")
        cols = st.columns(3)
        for idx, (name, price) in enumerate(st.session_state.global_products_prices.items()):
            with cols[idx % 3]:
                if st.session_state.user['role'] == UserRole.OWNER:
                    new_price = st.number_input(name, min_value=0.0, value=price, step=0.5, key=f"pr_{name}")
                    st.session_state.global_products_prices[name] = new_price
                else:
                    st.metric(name, f"${price:.2f}")
    
    # إدارة روابط البورصة
    st.markdown("---")
    with st.expander("🌐 إدارة روابط البورصة", expanded=False):
        st.info("يمكن ربط النظام بمصادر خارجية للحصول على أسعار محدثة")
        
        if 'price_feeds' not in st.session_state:
            st.session_state.price_feeds = {}
        
        region_key = f"{st.selectbox('الدولة', list(EXCHANGE_RATES.keys()))}"
        
        col_url1, col_url2, col_url3 = st.columns(3)
        with col_url1:
            livestock_url = st.text_input("رابط أسعار الحيوانات", 
                                        value=st.session_state.price_feeds.get(region_key, {}).get('livestock', ''))
        with col_url2:
            products_url = st.text_input("رابط أسعار المنتجات",
                                       value=st.session_state.price_feeds.get(region_key, {}).get('products', ''))
        with col_url3:
            feeds_url = st.text_input("رابط أسعار الخامات",
                                    value=st.session_state.price_feeds.get(region_key, {}).get('feeds', ''))
        
        if st.button("💾 حفظ الروابط"):
            st.session_state.price_feeds[region_key] = {
                'livestock': livestock_url,
                'products': products_url,
                'feeds': feeds_url
            }
            st.success("✅ تم حفظ الروابط")
        
        if st.button("🔄 تحديث الأسعار من الروابط"):
            with st.spinner("جاري جلب البيانات..."):
                update_all_prices_from_feeds()
            st.rerun()

# =====================================================================
# دالة عرض إدارة المخزون
# =====================================================================

def show_inventory_management(db: DatabaseManager):
    """عرض واجهة إدارة المخزون"""
    
    st.markdown('<div class="section-title">🏭 إدارة المخزون والمستودعات</div>', unsafe_allow_html=True)
    
    if st.session_state.user['role'] == UserRole.SPECIALIST:
        st.warning("⚠️ حساب مختص: يمكنك مراجعة الأرصدة فقط")
    
    # إحصائيات المخزون
    inventory = db.get_inventory()
    warnings = InventoryManager.check_stock_levels(db)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("إجمالي المواد", len(inventory))
    with col2:
        critical = sum(1 for v in warnings.values() if v == "نفذ المخزون")
        st.metric("مواد نفذت", critical, delta=f"-{critical}" if critical > 0 else "")
    with col3:
        low = sum(1 for v in warnings.values() if v == "منخفض")
        st.metric("مواد منخفضة", low, delta=f"-{low}" if low > 0 else "")
    with col4:
        healthy = len(inventory) - critical - low
        st.metric("مواد آمنة", healthy)
    
    st.markdown("---")
    
    # عرض المخزون
    st.subheader("📋 قائمة المواد")
    
    # تحويل إلى DataFrame للعرض
    df = pd.DataFrame(inventory)
    df['status'] = df.apply(lambda row: 
        "🔴 نفذ" if row['quantity'] <= 0 
        else "🟡 منخفض" if row['quantity'] < row['min_threshold'] 
        else "🟢 آمن", axis=1)
    
    display_cols = ['item_name', 'quantity', 'unit', 'min_threshold', 'status']
    st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
    
    # تحديث الكميات (للمالك فقط)
    if st.session_state.user['role'] == UserRole.OWNER:
        st.subheader("✏️ تحديث الكميات")
        
        selected_item = st.selectbox("اختر المادة", options=[item['item_name'] for item in inventory])
        if selected_item:
            item_data = db.get_inventory_item(selected_item)
            if item_data:
                new_qty = st.number_input("الكمية الجديدة (طن)", min_value=0.0, 
                                         value=item_data['quantity'], step=0.5)
                if st.button("💾 تحديث الكمية", use_container_width=True):
                    db.update_inventory(selected_item, new_qty)
                    st.success("✅ تم تحديث الكمية")
                    st.rerun()

# =====================================================================
# دالة عرض التسويق والفواتير
# =====================================================================

def show_marketing_invoicing():
    """عرض واجهة التسويق والفواتير"""
    
    st.markdown('<div class="section-title">💰 نظام التسويق والفواتير</div>', unsafe_allow_html=True)
    
    if not st.session_state.active_formula:
        st.warning("⚠️ يرجى تشغيل محرك تركيب الأعلاف أولاً")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        client_name = st.text_input("اسم العميل", "مزرعة الإنتاج المتكاملة")
    with col2:
        required_tons = st.number_input("الكمية المطلوبة (طن)", min_value=0.1, value=1.0, step=0.5)
    with col3:
        profit_margin = st.number_input("هامش الربح ($/طن)", min_value=0.0, value=50.0, step=10.0)
    
    cost_per_ton = st.session_state.computed_ton_cost
    selling_price = cost_per_ton + profit_margin
    total_bill = selling_price * required_tons
    
    st.markdown("### 🧾 فاتورة البيع")
    
    col_fact1, col_fact2 = st.columns(2)
    with col_fact1:
        st.markdown(f"""
        <div class="price-card">
            <h4>تفاصيل الفاتورة</h4>
            <p>العميل: <b>{client_name}</b></p>
            <p>الكمية: <b>{required_tons} طن</b></p>
            <p>سعر الطن: <b>${selling_price:.2f}</b></p>
            <p style="font-size: 1.3rem; color: #1b5e20;">
                <b>الإجمالي: ${total_bill:,.2f}</b>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_fact2:
        st.markdown("#### 📊 مكونات الخلطة")
        for name, pct in st.session_state.active_formula.items():
            amount = (pct / 100) * required_tons
            st.markdown(f"▪️ {name}: **{amount:.2f}** طن ({pct:.1f}%)")
    
    if st.session_state.user['role'] == UserRole.OWNER:
        if st.button("✅ تأكيد البيع وخصم المخزون", type="primary", use_container_width=True):
            can_deduct = True
            for name, pct in st.session_state.active_formula.items():
                amount = (pct / 100) * required_tons
                item = db.get_inventory_item(name)
                if not item or item['quantity'] < amount:
                    st.error(f"❌ رصيد غير كافي: {name}")
                    can_deduct = False
                    break
            
            if can_deduct:
                for name, pct in st.session_state.active_formula.items():
                    amount = (pct / 100) * required_tons
                    db.deduct_inventory(name, amount)
                st.success("🔥 تم الخصم التلقائي وتحديث المخازن")
                st.balloons()
                time.sleep(1)
                st.rerun()
    else:
        st.info("ℹ️ تأكيد الفواتير متاح للمالك فقط")

# =====================================================================
# دالة عرض مصمم الديباجة
# =====================================================================

def show_designer():
    """عرض واجهة مصمم الديباجة"""
    
    st.markdown('<div class="section-title">👑 مصمم ديباجات الأعلاف</div>', unsafe_allow_html=True)
    
    brand_name = st.text_input("اسم البراند التجاري", "منصة تاور العلمية للانتاج الحيواني")
    
    col_preview, col_options = st.columns([0.7, 0.3])
    with col_preview:
        # صورة الحيوان
        animal_img = ANIMAL_IMAGES_RESOURCES.get(
            st.session_state.get('active_animal', 'عام'),
            ANIMAL_IMAGES_RESOURCES['عام']
        )
        
        st.markdown(f"""
        <div class="sack-tag">
            <img src="{animal_img}" style="width:100%; max-height:200px; object-fit:cover; border-radius:12px; margin-bottom:15px;">
            <h2 style="text-align:center; color:#1b5e20;">🌟 {brand_name} 🌟</h2>
            <h3 style="text-align:center; color:#c62828;">الاختصاصي عبدالقادر إسماعيل تاور</h3>
            <p style="text-align:center; background:#e8f5e9; padding:10px; border-radius:8px; color:#1b5e20;">
                🎯 {st.session_state.get('active_stage', 'إنتاج حيواني')} | 
                DP: {st.session_state.get('active_cp_tag', 12.0):.1f}% | 
                SE: {st.session_state.get('active_se_tag', 65.0):.1f}
            </p>
            <div style="text-align:center; color:#666; font-size:0.9rem;">
                تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_options:
        st.markdown("#### خيارات التخصيص")
        show_qr = st.checkbox("إضافة QR Code", value=True)
        show_date = st.checkbox("إظهار التاريخ", value=True)
        font_size = st.slider("حجم الخط", 12, 24, 16)
        
        if st.button("📥 تصدير كـ PDF", use_container_width=True):
            st.success("تم تجهيز الديباجة للطباعة")

# =====================================================================
# دالة عرض التحليلات المتقدمة
# =====================================================================

def show_advanced_analytics(db: DatabaseManager):
    """عرض التحليلات المتقدمة"""
    
    st.markdown('<div class="section-title">📈 التحليلات المتقدمة</div>', unsafe_allow_html=True)
    
    # مؤشرات عامة
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>عدد الخلطات</h3>
            <h2 style="color:#2e7d32;">1,247</h2>
            <p>خلطة تم توليدها</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>متوسط التكلفة</h3>
            <h2 style="color:#1565C0;">$285</h2>
            <p>لطن العلف</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>نسبة التوفير</h3>
            <h2 style="color:#E65100;">18%</h2>
            <p>مقارنة بالتقليدي</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>رضا العملاء</h3>
            <h2 style="color:#388E3C;">96%</h2>
            <p>تقييم إيجابي</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # رسوم بيانية
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader("📊 توزيع استخدام المواد")
        usage_data = pd.DataFrame({
            'المادة': ['ذرة', 'صويا', 'نخالة', 'أملاح', 'أخرى'],
            'النسبة': [45, 25, 15, 10, 5]
        })
        fig = px.pie(usage_data, values='النسبة', names='المادة', 
                    title='المواد الأكثر استخداماً',
                    color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_chart2:
        st.subheader("📈 اتجاه أسعار المواد")
        dates = pd.date_range(start='2024-01-01', periods=12, freq='ME')
        trend_data = pd.DataFrame({
            'التاريخ': dates,
            'الذرة': [220, 225, 230, 228, 235, 240, 238, 242, 245, 248, 250, 252],
            'الصويا': [440, 445, 442, 448, 450, 455, 452, 458, 460, 462, 465, 468]
        })
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend_data['التاريخ'], y=trend_data['الذرة'],
                                mode='lines+markers', name='الذرة'))
        fig.add_trace(go.Scatter(x=trend_data['التاريخ'], y=trend_data['الصويا'],
                                mode='lines+markers', name='الصويا'))
        fig.update_layout(title='اتجاه أسعار المواد الخام', xaxis_title='التاريخ',
                         yaxis_title='السعر ($/طن)')
        st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# دالة عرض إدارة المزارع
# =====================================================================

def show_farm_management(db: DatabaseManager):
    """عرض واجهة إدارة المزارع المتكاملة"""
    
    st.markdown('<div class="section-title">🐄 إدارة المزارع والمجموعات</div>', unsafe_allow_html=True)
    
    # قائمة المزارع
    farms = db.get_farms()
    
    if farms:
        st.subheader("📋 المزارع المسجلة")
        df = pd.DataFrame(farms)
        display_cols = ['id', 'name', 'location', 'animal_type', 'breed', 'head_count']
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
    
    # إضافة مزرعة
    with st.expander("➕ إضافة مزرعة جديدة", expanded=not farms):
        with st.form("add_farm_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("اسم المزرعة *")
                location = st.text_input("الموقع")
                animal_type = st.selectbox("نوع الحيوان", [t.value for t in AnimalType])
                breed = st.text_input("السلالة")
            with col2:
                purpose = st.selectbox("الغرض", ["حليب", "لحم", "صوف", "بيض", "إكثار", "أخرى"])
                head_count = st.number_input("عدد الرؤوس", min_value=0, step=1, value=0)
                start_date = st.date_input("تاريخ البدء", value=datetime.now().date())
            
            notes = st.text_area("ملاحظات")
            
            if st.form_submit_button("💾 حفظ المزرعة", use_container_width=True):
                if not name:
                    st.error("⚠️ يرجى إدخال اسم المزرعة")
                else:
                    farm_id = db.create_farm({
                        'name': name,
                        'location': location,
                        'animal_type': animal_type,
                        'breed': breed,
                        'purpose': purpose,
                        'head_count': head_count,
                        'start_date': start_date.isoformat(),
                        'notes': notes
                    })
                    st.success(f"✅ تم إضافة المزرعة '{name}' بنجاح")
                    st.rerun()
    
    st.markdown("---")
    
    # عرض تفاصيل المزرعة
    if farms:
        selected_farm = st.selectbox("اختر مزرعة للعرض", 
                                    options=[f['id'] for f in farms],
                                    format_func=lambda x: next(f['name'] for f in farms if f['id'] == x))
        
        if selected_farm:
            farm = db.get_farm(selected_farm)
            if farm:
                # معلومات المزرعة
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("نوع الحيوان", farm.get('animal_type', 'غير محدد'))
                with col2:
                    st.metric("السلالة", farm.get('breed', 'غير محدد'))
                with col3:
                    st.metric("عدد الرؤوس", farm.get('head_count', 0))
                with col4:
                    st.metric("الغرض", farm.get('purpose', 'غير محدد'))
                
                # تبويبات داخلية
                farm_tabs = st.tabs(["📊 نظرة عامة", "🐄 المجموعات", "📈 السجلات", "🏥 الصحة", "📊 التحليلات"])
                
                # نظرة عامة
                with farm_tabs[0]:
                    groups = db.get_groups(farm['id'])
                    total_head = sum(g.get('head_count', 0) for g in groups)
                    st.metric("إجمالي المجموعات", len(groups))
                    st.metric("إجمالي الرؤوس", total_head)
                    
                    if st.button("📥 تحميل تقرير المزرعة PDF", use_container_width=True):
                        records = db.get_daily_records(groups[0]['id']) if groups else []
                        pdf = pdf_generator.generate_farm_report(farm, groups, records)
                        st.download_button("تنزيل", pdf, 
                                         file_name=f"farm_report_{farm['id']}.pdf",
                                         mime="application/pdf")
                
                # المجموعات
                with farm_tabs[1]:
                    show_groups_management(db, farm['id'])
                
                # السجلات اليومية
                with farm_tabs[2]:
                    show_daily_records(db, farm['id'])
                
                # السجلات الصحية
                with farm_tabs[3]:
                    show_health_records(db, farm['id'])
                
                # التحليلات
                with farm_tabs[4]:
                    show_farm_analytics(db, farm['id'])

# =====================================================================
# دوال إدارة المجموعات
# =====================================================================

def show_groups_management(db: DatabaseManager, farm_id: int):
    """إدارة المجموعات الحيوانية"""
    
    groups = db.get_groups(farm_id)
    
    if groups:
        df = pd.DataFrame(groups)
        st.dataframe(df[['id', 'name', 'group_type', 'head_count', 'average_weight']], 
                    use_container_width=True, hide_index=True)
    
    with st.expander("➕ إضافة مجموعة", expanded=not groups):
        with st.form("add_group_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("اسم المجموعة *")
                group_type = st.text_input("نوع المجموعة")
                head_count = st.number_input("عدد الرؤوس", min_value=0, step=1, value=0)
            with col2:
                avg_weight = st.number_input("متوسط الوزن (كجم)", min_value=0.0, step=1.0)
                birth_date = st.date_input("تاريخ الميلاد", value=datetime.now().date())
            
            notes = st.text_area("ملاحظات")
            
            if st.form_submit_button("💾 حفظ المجموعة", use_container_width=True):
                if not name:
                    st.error("⚠️ يرجى إدخال اسم المجموعة")
                else:
                    db.create_group({
                        'farm_id': farm_id,
                        'name': name,
                        'group_type': group_type,
                        'head_count': head_count,
                        'average_weight': avg_weight,
                        'birth_date': birth_date.isoformat(),
                        'notes': notes
                    })
                    st.success(f"✅ تم إضافة المجموعة '{name}'")
                    st.rerun()

# =====================================================================
# دوال السجلات اليومية
# =====================================================================

def show_daily_records(db: DatabaseManager, farm_id: int):
    """عرض وإضافة السجلات اليومية"""
    
    groups = db.get_groups(farm_id)
    if not groups:
        st.info("ℹ️ لا توجد مجموعات. أضف مجموعة أولاً")
        return
    
    group_options = {g['name']: g['id'] for g in groups}
    selected = st.selectbox("اختر المجموعة", list(group_options.keys()))
    group_id = group_options[selected]
    
    # عرض السجلات
    records = db.get_daily_records(group_id, 
                                  start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    if records:
        df = pd.DataFrame(records)
        display_cols = ['record_date', 'average_weight', 'feed_given', 'deaths', 'health_score']
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
    
    # إضافة سجل
    with st.expander("➕ إضافة سجل يومي"):
        with st.form("add_record_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                date = st.date_input("التاريخ", value=datetime.now().date())
                weight = st.number_input("متوسط الوزن (كجم)", min_value=0.0, step=0.1)
            with col2:
                feed = st.number_input("العلف المقدم (كجم)", min_value=0.0, step=0.1)
                deaths = st.number_input("عدد النافق", min_value=0, step=1, value=0)
            with col3:
                health = st.slider("الحالة الصحية (1-5)", 1, 5, 5)
                production = st.number_input("الإنتاج", min_value=0.0, step=0.1)
            
            notes = st.text_area("ملاحظات")
            
            if st.form_submit_button("💾 حفظ السجل", use_container_width=True):
                db.add_daily_record({
                    'group_id': group_id,
                    'record_date': date.isoformat(),
                    'average_weight': weight,
                    'feed_given': feed,
                    'deaths': deaths,
                    'health_score': health,
                    'production_amount': production,
                    'notes': notes
                })
                st.success("✅ تم إضافة السجل")
                st.rerun()

# =====================================================================
# دوال السجلات الصحية
# =====================================================================

def show_health_records(db: DatabaseManager, farm_id: int):
    """عرض وإضافة السجلات الصحية"""
    
    groups = db.get_groups(farm_id)
    if not groups:
        st.info("ℹ️ لا توجد مجموعات")
        return
    
    group_options = {g['name']: g['id'] for g in groups}
    selected = st.selectbox("اختر المجموعة", list(group_options.keys()), key="health_select")
    group_id = group_options[selected]
    
    records = db.get_health_records(group_id)
    if records:
        df = pd.DataFrame(records)
        st.dataframe(df[['event_date', 'event_type', 'diagnosis', 'treatment']], 
                    use_container_width=True, hide_index=True)
    
    with st.expander("➕ إضافة سجل صحي"):
        with st.form("add_health_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("التاريخ", value=datetime.now().date())
                event_type = st.selectbox("نوع الحدث", ["مرض", "علاج", "لقاح", "فحص"])
                diagnosis = st.text_input("التشخيص")
            with col2:
                treatment = st.text_input("العلاج")
                veterinarian = st.text_input("الطبيب المعالج")
                cost = st.number_input("التكلفة ($)", min_value=0.0, step=5.0)
            
            notes = st.text_area("ملاحظات")
            
            if st.form_submit_button("💾 حفظ السجل الصحي", use_container_width=True):
                db.add_health_record({
                    'group_id': group_id,
                    'event_date': date.isoformat(),
                    'event_type': event_type,
                    'diagnosis': diagnosis,
                    'treatment': treatment,
                    'veterinarian': veterinarian,
                    'cost': cost,
                    'notes': notes
                })
                st.success("✅ تم إضافة السجل الصحي")
                st.rerun()

# =====================================================================
# دوال تحليلات المزرعة
# =====================================================================

def show_farm_analytics(db: DatabaseManager, farm_id: int):
    """عرض تحليلات المزرعة المتقدمة"""
    
    groups = db.get_groups(farm_id)
    if not groups:
        st.info("ℹ️ لا توجد مجموعات للتحليل")
        return
    
    group_options = {g['name']: g['id'] for g in groups}
    selected = st.selectbox("اختر المجموعة للتحليل", list(group_options.keys()), key="analytics_select")
    group_id = group_options[selected]
    
    days = st.slider("الفترة (أيام)", 7, 90, 30)
    
    performance = db.get_group_performance(group_id, days)
    
    if 'error' not in performance:
        st.success(f"📊 أداء المجموعة '{performance['group_name']}'")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("معدل النمو اليومي", f"{performance['adg']} كجم/يوم")
        with col2:
            st.metric("معامل التحويل الغذائي", f"{performance['fcr']:.2f}")
        with col3:
            st.metric("معدل النافق", f"{performance['mortality_rate']:.1f}%")
        with col4:
            st.metric("متوسط الصحة", f"{performance['health_score_avg']}/5")
        
        # رسم بياني
        records = db.get_daily_records(group_id, 
                                      start_date=(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'))
        if records:
            df = pd.DataFrame(records)
            df['record_date'] = pd.to_datetime(df['record_date'])
            df = df.sort_values('record_date')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['record_date'], y=df['average_weight'],
                                    mode='lines+markers', name='الوزن',
                                    line=dict(color='#2e7d32', width=3)))
            fig.update_layout(title='تطور الوزن خلال الفترة', xaxis_title='التاريخ',
                             yaxis_title='الوزن (كجم)', hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(performance['error'])

# =====================================================================
# دالة عرض تعليقات المختصين
# =====================================================================

def show_comments():
    """عرض تعليقات المختصين"""
    
    st.markdown('<div class="section-title">💬 تعليقات المختصين</div>', unsafe_allow_html=True)
    
    st.text_area("التعليقات الحالية:", value=st.session_state.shared_comments, 
                height=200, disabled=True)
    
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        new_comment = st.text_input("✍️ أضف تعليقك")
    with col2:
        if st.button("📌 نشر التعليق", use_container_width=True):
            if new_comment.strip():
                prefix = "• [توجيه الاختصاصي]" if st.session_state.user['role'] == UserRole.OWNER else "• [ملاحظة مختص]"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.shared_comments += f"{prefix} ({timestamp}): {new_comment.strip()}\n"
                st.success("✅ تم نشر التعليق")
                st.rerun()

# =====================================================================
# دالة عرض دليل المستخدم
# =====================================================================

def show_user_guide():
    """عرض دليل المستخدم"""
    
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
    
    col_audio, col_video = st.columns(2)
    with col_audio:
        if st.button("🔊 تشغيل الدليل الصوتي", use_container_width=True):
            play_guide_audio()
    
    with col_video:
        if st.button("🎬 تشغيل فيديو الشرح", use_container_width=True):
            st.info("سيتم إضافة فيديو شرح قريباً")
    
    st.markdown("""
    <div style='background: #f8f9fa; padding: 30px; border-radius: 15px; direction: rtl;'>
        <h3 style='color: #1b5e20;'>📌 نظرة عامة</h3>
        <p>منصة تاور العلمية هي نظام متكامل لإدارة الثروة الحيوانية وتركيب الأعلاف، تشمل:</p>
        <ul>
            <li><b>تركيب الأعلاف:</b> محرك تحسين خطي يحسب الخلطة المثلى بأقل تكلفة</li>
            <li><b>إدارة المزارع:</b> نظام متكامل لإدارة المزارع والمجموعات الحيوانية</li>
            <li><b>السجلات اليومية:</b> تسجيل الأوزان، استهلاك العلف، الإنتاج، والصحة</li>
            <li><b>التحليلات:</b> مؤشرات أداء متقدمة ورسوم بيانية</li>
            <li><b>بورصة الأسعار:</b> متابعة أسعار الماشية والمنتجات</li>
        </ul>
        
        <h3 style='color: #1b5e20; margin-top: 20px;'>🚀 خطوات العمل</h3>
        <ol>
            <li>تسجيل الدخول باستخدام اسم المستخدم وكلمة المرور</li>
            <li>إضافة مزرعة جديدة من تبويب إدارة المزارع</li>
            <li>إضافة مجموعات حيوانية داخل المزرعة</li>
            <li>تسجيل السجلات اليومية للمتابعة</li>
            <li>استخدام محرك تركيب الأعلاف للحصول على خلطات محسنة</li>
            <li>متابعة التحليلات والمؤشرات لاتخاذ القرارات</li>
        </ol>
        
        <h3 style='color: #1b5e20; margin-top: 20px;'>🔑 الأدوار والمستخدمين</h3>
        <ul>
            <li><b>👑 المالك:</b> صلاحيات كاملة - abukram / Admin@2026</li>
            <li><b>👨‍🔬 المختص:</b> صلاحيات متقدمة - specialist / Specialist@2026</li>
            <li><b>🌾 المربي:</b> صلاحيات أساسية - breeder / Breeder@2026</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# تشغيل التطبيق
# =====================================================================

if __name__ == "__main__":
    main()
