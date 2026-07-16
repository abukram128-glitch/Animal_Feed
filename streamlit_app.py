# =====================================================================
# منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف - النسخة المطورة
# المشرف العام: الاختصاصي عبدالقادر إسماعيل تاور
# الإصدار: 3.0 - تطوير شامل
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
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
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
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

# =====================================================================
# قاعدة البيانات (SQLite)
# =====================================================================
import sqlite3
from contextlib import contextmanager

# =====================================================================
# تكوين الصفحة
# =====================================================================
st.set_page_config(
    page_title="منصة تاور العلمية - النسخة المطورة",
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

class ProductionPurpose(Enum):
    MILK = "حليب"
    MEAT = "لحم"
    WOOL = "صوف"
    EGGS = "بيض"
    BREEDING = "إكثار"
    SPORT = "رياضة"
    OTHER = "أخرى"

# إعدادات الأمان - يجب نقلها إلى st.secrets في الإنتاج الفعلي
if 'secrets' in dir(st):
    SENDER_EMAIL = st.secrets.get("email", {}).get("sender", "abukram128@gmail.com")
    SENDER_PASSWORD = st.secrets.get("email", {}).get("password", "")
else:
    # للاختبار المحلي - استخدم متغيرات البيئة
    SENDER_EMAIL = os.environ.get("EMAIL_SENDER", "abukram128@gmail.com")
    SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")

# تخزين كلمات المرور بشكل آمن (مشفر)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# المستخدمون المسموح لهم - بشكل آمن
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
# إدارة قاعدة البيانات
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
            
            # جدول التحصينات المقررة
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
    
    # ===== عمليات المجموعات الحيوانية =====
    
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
    
    # ===== التحليلات المتقدمة =====
    
    def get_group_performance(self, group_id: int, days: int = 30) -> dict:
        """تحليل أداء المجموعة للفترة المحددة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # أساسيات
            cursor.execute("SELECT * FROM animal_groups WHERE id = ?", (group_id,))
            group = cursor.fetchone()
            
            # السجلات اليومية
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT * FROM daily_records 
                WHERE group_id = ? AND record_date >= ?
                ORDER BY record_date
            ''', (group_id, cutoff_date))
            records = [dict(row) for row in cursor.fetchall()]
            
            if not records:
                return {'error': 'لا توجد سجلات كافية للتحليل'}
            
            # حساب المؤشرات الأساسية
            df = pd.DataFrame(records)
            
            # معدل النمو اليومي (ADG) - إذا كان هناك أوزان
            if 'average_weight' in df.columns and len(df) > 1:
                weight_gain = df['average_weight'].iloc[-1] - df['average_weight'].iloc[0]
                days_diff = (datetime.strptime(df['record_date'].iloc[-1], '%Y-%m-%d') - 
                            datetime.strptime(df['record_date'].iloc[0], '%Y-%m-%d')).days
                adg = weight_gain / max(days_diff, 1)
            else:
                adg = 0
            
            # معدل التحويل الغذائي (FCR)
            total_feed = df['feed_given'].sum() - df['feed_refused'].sum()
            total_gain = df['average_weight'].iloc[-1] - df['average_weight'].iloc[0]
            fcr = total_feed / max(total_gain, 0.001)
            
            # معدل النافق
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
# مكتبة الأعلاف - موسعة ومحسنة
# =====================================================================

FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6}
    },
    "🌱 الأكساب والبروتينات": {
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "أمباز الفول السوداني": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب عباد الشمس": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5}
    },
    "🧬 البروتين الحيواني والمركزات": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق أسماك 72%": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5},
        "مركز دواجن": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركز مجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5}
    },
    "🪨 المعادن والإضافات": {
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0}
    },
    "🧪 الإضافات التخصصية": {
        "خميرة الخبز": {"CP": 45.0, "DC": 0.90, "SE": 55.0, "NDF": 5.0, "ADF": 2.0, "EE": 2.0, "ASH": 6.0},
        "مسحوق الحليب": {"CP": 25.0, "DC": 0.95, "SE": 60.0, "NDF": 0.0, "ADF": 0.0, "EE": 26.0, "ASH": 8.0},
        "دهن نباتي": {"CP": 0.0, "DC": 0.0, "SE": 85.0, "NDF": 0.0, "ADF": 0.0, "EE": 99.0, "ASH": 0.5},
        "زيت سمك": {"CP": 0.0, "DC": 0.0, "SE": 80.0, "NDF": 0.0, "ADF": 0.0, "EE": 98.0, "ASH": 0.5}
    }
}

# =====================================================================
# معالجة النصوص العربية
# =====================================================================

class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=1000)
    def fix_arabic_text(text: str) -> str:
        """معالجة النص العربي للعرض"""
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
        """إزالة علامات التشكيل"""
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
    """تحويل النص إلى صوت"""
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

# =====================================================================
# توليد التقارير PDF
# =====================================================================

class PDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        try:
            pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
            self.font_name = 'Amiri'
        except:
            pass
    
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
                                                 textColor=color, spaceAfter=6, leading=size*1.5))
        
        # العنوان
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

pdf_generator = PDFGenerator()

# =====================================================================
# محرك تحسين الأعلاف
# =====================================================================

class FeedOptimizer:
    """محرك التحسين الخطي للأعلاف"""
    
    @staticmethod
    def optimize_feed(ingredients: List[str], prices: Dict[str, float],
                     target_dp: float, target_se: float,
                     fixed_additives: Dict[str, float] = None,
                     use_cp_basis: bool = False) -> Dict[str, Any]:
        """تحسين الخلطة باستخدام البرمجة الخطية"""
        
        if fixed_additives is None:
            fixed_additives = {}
        
        # إعداد المصفوفات
        n = len(ingredients)
        c_vector = [prices.get(ing, 100.0) for ing in ingredients]
        
        # حدود المكونات الثابتة
        bounds = []
        for ing in ingredients:
            if ing in fixed_additives:
                bounds.append((fixed_additives[ing], fixed_additives[ing]))
            else:
                bounds.append((0.0, 100.0))
        
        # معادلة المجموع الكلي = 100%
        A_eq = [[1.0] * n]
        b_eq = [100.0]
        
        # حساب البروتين والطاقة
        cp_row = []
        se_row = []
        for ing in ingredients:
            cp_val = 0.0
            dc_val = 0.0
            se_val = 0.0
            for category in FEEDS_LIBRARY.values():
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
        
        # قيود الطاقة (الحد الأدنى)
        A_ub = []
        b_ub = []
        A_ub.append([-1.0 * x for x in se_row])
        b_ub.append(-1.0 * target_se * 100.0)
        
        # قيود إضافية للمجترات
        grain_indicators = [1.0 if any(ing in cat for cat in FEEDS_LIBRARY["🌾 الحبوب ومصادر الطاقة"].keys()) else 0.0 
                           for ing in ingredients]
        if sum(grain_indicators) > 0:
            A_ub.append([-1.0 * x for x in grain_indicators])
            b_ub.append(-50.0)
        
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
                for category in FEEDS_LIBRARY.values():
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
# الواجهة الرئيسية
# =====================================================================

def main():
    """الوظيفة الرئيسية للتطبيق"""
    
    # تهيئة قاعدة البيانات
    db = DatabaseManager()
    
    # تهيئة حالة الجلسة
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    
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
    .metric-card { background: white; padding: 20px; border-radius: 15px; 
                   box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; }
    .formula-item { background: #f5f5f5; padding: 12px 20px; border-radius: 10px; 
                    margin-bottom: 8px; border-right: 4px solid #2e7d32; }
    .warning-box { background: #fff3e0; padding: 15px; border-radius: 10px; 
                   border-right: 5px solid #f57c00; margin: 10px 0; }
    .success-box { background: #e8f5e9; padding: 15px; border-radius: 10px; 
                   border-right: 5px solid #2e7d32; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    
    # رأس الصفحة
    col_logo, col_title = st.columns([0.2, 0.8])
    with col_logo:
        st.image("https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=150&h=150&fit=crop", 
                use_container_width=True)
    with col_title:
        st.markdown("<h1 style='color: #1b5e20;'>منصة تاور العلمية المطورة 🌾</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #1565C0; font-size: 1.2rem;'>نظام متكامل لإدارة الثروة الحيوانية وتركيب الأعلاف</p>")
        st.markdown(f"<p style='color: #c62828;'><strong>المشرف العام:</strong> {st.session_state.user.get('name', '')}</p>", 
                   unsafe_allow_html=True)
    
    # معلومات المستخدم
    col_user, col_logout = st.columns([0.8, 0.2])
    with col_user:
        st.info(f"👤 {st.session_state.user.get('name', '')} - {st.session_state.user.get('role', '').value}")
    with col_logout:
        if st.button("🚪 خروج", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    st.markdown("---")
    
    # ===== التبويبات =====
    if st.session_state.user['role'] == UserRole.OWNER:
        tabs = st.tabs(["🔬 تركيب الأعلاف", "📊 بورصة الأسعار", "🏭 إدارة المخزون",
                        "🐄 إدارة المزارع", "📈 التحليلات المتقدمة", "📖 دليل المستخدم"])
    elif st.session_state.user['role'] == UserRole.SPECIALIST:
        tabs = st.tabs(["🔬 تركيب الأعلاف", "📊 بورصة الأسعار", "🐄 إدارة المزارع",
                        "📖 دليل المستخدم"])
    else:
        tabs = st.tabs(["🔬 تركيب الأعلاف", "🐄 إدارة المزارع", "📖 دليل المستخدم"])
    
    # ===== التبويب 1: تركيب الأعلاف =====
    with tabs[0]:
        show_feed_formulation(db)
    
    # ===== التبويب 2: بورصة الأسعار =====
    if len(tabs) > 1 and "بورصة" in tabs[1].label:
        with tabs[1]:
            show_market_prices()
    
    # ===== التبويب 3: إدارة المزارع =====
    farm_tab_index = 1 if st.session_state.user['role'] == UserRole.BREEDER else 2
    if len(tabs) > farm_tab_index and "إدارة المزارع" in tabs[farm_tab_index].label:
        with tabs[farm_tab_index]:
            show_farm_management(db)
    
    # ===== التبويب الأخير: دليل المستخدم =====
    with tabs[-1]:
        show_user_guide()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # توقيع
    st.markdown("""
    <div style='position: fixed; bottom: 20px; left: 20px; background: linear-gradient(135deg, #1b5e20, #2e7d32);
                color: white; padding: 8px 20px; border-radius: 25px; font-size: 0.85rem; z-index: 9999;'>
        👨‍🔬 الاختصاصي عبدالقادر إسماعيل تاور © 2026
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# صفحة تسجيل الدخول
# =====================================================================

def show_login_page():
    """عرض صفحة تسجيل الدخول"""
    
    st.markdown("""
    <style>
    .login-box { max-width: 450px; margin: 100px auto; padding: 40px; 
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
        username = st.text_input("اسم المستخدم", placeholder="أدخل اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password", placeholder="أدخل كلمة المرور")
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
# تبويب تركيب الأعلاف
# =====================================================================

def show_feed_formulation(db: DatabaseManager):
    """عرض واجهة تركيب الأعلاف"""
    
    st.markdown('<div class="section-title">🎯 تركيب علف اقتصادي بأقل تكلفة</div>', unsafe_allow_html=True)
    
    # اختيار المعايير
    col1, col2, col3 = st.columns(3)
    with col1:
        animal_type = st.selectbox("نوع الحيوان", [t.value for t in AnimalType])
    with col2:
        purpose = st.selectbox("الغرض", [p.value for p in ProductionPurpose])
    with col3:
        target_dp = st.slider("البروتين المهضوم المستهدف (%)", 5.0, 40.0, 12.0, 0.5)
    
    # اختيار المكونات
    st.markdown("### 📦 اختيار المكونات")
    
    selected_ingredients = []
    prices = {}
    
    for category, items in FEEDS_LIBRARY.items():
        with st.expander(category, expanded=True):
            cols = st.columns(3)
            for idx, (name, _) in enumerate(items.items()):
                with cols[idx % 3]:
                    checked = st.checkbox(name, key=f"feed_{name}")
                    if checked:
                        selected_ingredients.append(name)
                        price = st.number_input(f"💰 {name} ($/طن)", min_value=1.0, 
                                               value=100.0, step=5.0, key=f"price_{name}")
                        prices[name] = price
    
    if not selected_ingredients:
        st.warning("⚠️ يرجى اختيار مكون واحد على الأقل")
        return
    
    # تشغيل المحرك
    if st.button("🚀 تشغيل محرك التحسين", type="primary", use_container_width=True):
        with st.spinner("جاري حساب الخلطة المثلى..."):
            result = FeedOptimizer.optimize_feed(
                ingredients=selected_ingredients,
                prices=prices,
                target_dp=target_dp,
                target_se=65.0,  # قيمة افتراضية
                fixed_additives={"ملح الطعام": 0.5}
            )
        
        if result['success']:
            st.success(result['message'])
            
            col_res1, col_res2 = st.columns([0.6, 0.4])
            with col_res1:
                st.markdown("### 📝 الخلطة المقترحة (لكل طن)")
                for name, pct in result['formula'].items():
                    st.markdown(f'<div class="formula-item">▪️ <b>{name}:</b> {pct:.2f}% ➡️ {pct*10:.1f} كجم</div>', 
                               unsafe_allow_html=True)
                
                st.metric("💰 التكلفة للطن", f"${result['cost_per_ton']:.2f}")
                st.metric("🌽 معادل النشاء الفعلي", f"{result['actual_se']:.1f} وحدة")
            
            with col_res2:
                # رسم بياني
                fig = px.pie(values=list(result['formula'].values()), 
                           names=list(result['formula'].keys()),
                           title="توزيع المكونات")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # تحميل PDF
                try:
                    pdf = pdf_generator.generate_farm_report(
                        {'name': 'خلطة علف محسنة', 'location': 'منصة تاور'},
                        [{'name': name, 'head_count': int(pct)} for name, pct in result['formula'].items()],
                        []
                    )
                    st.download_button("📥 تحميل التقرير PDF", pdf, 
                                     file_name="feed_formula.pdf", mime="application/pdf")
                except Exception as e:
                    st.error(f"⚠️ فشل توليد PDF: {e}")
        else:
            st.error(f"❌ {result['message']}")

# =====================================================================
# تبويب بورصة الأسعار
# =====================================================================

def show_market_prices():
    """عرض بورصة الأسعار"""
    
    st.markdown('<div class="section-title">📊 بورصة الأسعار المركزية</div>', unsafe_allow_html=True)
    
    # أسعار الماشية
    st.subheader("🐄 أسعار الماشية")
    livestock_prices = {
        "عجول تسمين": 1350.0,
        "أبقار محلية": 900.0,
        "ضأن": 180.0,
        "ماعز": 130.0,
        "خيول": 4500.0
    }
    
    cols = st.columns(len(livestock_prices))
    for idx, (name, price) in enumerate(livestock_prices.items()):
        with cols[idx]:
            st.metric(name, f"${price:.0f}")
    
    # أسعار المنتجات
    st.subheader("🥛 أسعار المنتجات")
    product_prices = {
        "لحم بقري": 7.50,
        "لحم ضأن": 9.00,
        "لحم دجاج": 3.80,
        "بيض (طبق)": 4.20,
        "حليب (لتر)": 0.90
    }
    
    cols = st.columns(len(product_prices))
    for idx, (name, price) in enumerate(product_prices.items()):
        with cols[idx]:
            st.metric(name, f"${price:.2f}")
    
    # تحديث الأسعار
    st.markdown("---")
    st.subheader("🔄 تحديث الأسعار")
    
    with st.expander("إعدادات تحديث الأسعار"):
        st.info("يمكن ربط النظام بمصادر خارجية للحصول على أسعار محدثة")
        feed_url = st.text_input("رابط JSON للأسعار", placeholder="https://example.com/prices.json")
        if st.button("جلب الأسعار"):
            try:
                response = requests.get(feed_url, timeout=10)
                if response.status_code == 200:
                    st.success("✅ تم جلب الأسعار بنجاح")
                    st.json(response.json())
                else:
                    st.error(f"❌ فشل الجلب: {response.status_code}")
            except Exception as e:
                st.error(f"❌ خطأ: {e}")

# =====================================================================
# تبويب إدارة المزارع - متقدم
# =====================================================================

def show_farm_management(db: DatabaseManager):
    """عرض واجهة إدارة المزارع المتقدمة"""
    
    st.markdown('<div class="section-title">🐄 إدارة المزارع والمجموعات الحيوانية</div>', unsafe_allow_html=True)
    
    # قائمة المزارع
    farms = db.get_farms()
    
    # عرض المزارع الحالية
    if farms:
        st.subheader("📋 المزارع المسجلة")
        df = pd.DataFrame(farms)
        display_cols = ['id', 'name', 'location', 'animal_type', 'breed', 'head_count']
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
    
    # إضافة مزرعة جديدة
    with st.expander("➕ إضافة مزرعة جديدة", expanded=not farms):
        with st.form("add_farm_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("اسم المزرعة *", placeholder="مزرعة الأمل")
                location = st.text_input("الموقع", placeholder="الخرطوم - أم درمان")
                animal_type = st.selectbox("نوع الحيوان", [t.value for t in AnimalType])
                breed = st.text_input("السلالة", placeholder="الهولشتاين")
            with col2:
                purpose = st.selectbox("الغرض", [p.value for p in ProductionPurpose])
                head_count = st.number_input("عدد الرؤوس", min_value=0, step=1, value=0)
                start_date = st.date_input("تاريخ البدء", value=datetime.now().date())
                area = st.number_input("المساحة (م²)", min_value=0.0, step=100.0, value=0.0)
            
            notes = st.text_area("ملاحظات", placeholder="أي معلومات إضافية عن المزرعة")
            
            submitted = st.form_submit_button("💾 حفظ المزرعة", use_container_width=True, type="primary")
            if submitted:
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
                        'area': area,
                        'notes': notes
                    })
                    st.success(f"✅ تم إضافة المزرعة '{name}' بنجاح (المعرف: {farm_id})")
                    st.rerun()
    
    st.markdown("---")
    
    # عرض تفاصيل المزرعة المختارة
    if farms:
        selected_farm_id = st.selectbox("اختر مزرعة للعرض", 
                                       options=[f['id'] for f in farms],
                                       format_func=lambda x: next(f['name'] for f in farms if f['id'] == x))
        
        if selected_farm_id:
            farm = db.get_farm(selected_farm_id)
            if farm:
                show_farm_details(db, farm)

# =====================================================================
# عرض تفاصيل المزرعة
# =====================================================================

def show_farm_details(db: DatabaseManager, farm: dict):
    """عرض تفاصيل المزرعة المتقدمة"""
    
    st.markdown(f"### 🏷️ {farm['name']}")
    
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
    
    # تبويبات داخلية للمزرعة
    farm_tabs = st.tabs(["📊 نظرة عامة", "🐄 المجموعات", "📈 السجلات اليومية", "🏥 السجلات الصحية", "🧬 التكاثر", "📊 التحليلات"])
    
    # ===== نظرة عامة =====
    with farm_tabs[0]:
        st.markdown("#### ملخص المزرعة")
        
        # إحصائيات سريعة
        groups = db.get_groups(farm['id'])
        total_head = sum(g.get('head_count', 0) for g in groups)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("عدد المجموعات", len(groups))
        with col2:
            st.metric("إجمالي الرؤوس", total_head)
        with col3:
            st.metric("متوسط الوزن", "غير محدد")
        
        # إنتاج PDF
        if st.button("📥 تحميل تقرير المزرعة PDF", use_container_width=True):
            records = db.get_daily_records(groups[0]['id']) if groups else []
            pdf = pdf_generator.generate_farm_report(farm, groups, records)
            st.download_button("تنزيل", pdf, file_name=f"farm_report_{farm['id']}.pdf", 
                             mime="application/pdf")
    
    # ===== المجموعات الحيوانية =====
    with farm_tabs[1]:
        show_groups_management(db, farm['id'])
    
    # ===== السجلات اليومية =====
    with farm_tabs[2]:
        show_daily_records(db, farm['id'])
    
    # ===== السجلات الصحية =====
    with farm_tabs[3]:
        show_health_records(db, farm['id'])
    
    # ===== التكاثر =====
    with farm_tabs[4]:
        show_reproduction_records(db, farm['id'])
    
    # ===== التحليلات =====
    with farm_tabs[5]:
        show_farm_analytics(db, farm['id'])

# =====================================================================
# إدارة المجموعات الحيوانية
# =====================================================================

def show_groups_management(db: DatabaseManager, farm_id: int):
    """إدارة المجموعات الحيوانية"""
    
    st.subheader("🐄 المجموعات الحيوانية")
    
    groups = db.get_groups(farm_id)
    
    if groups:
        df = pd.DataFrame(groups)
        display_cols = ['id', 'name', 'group_type', 'head_count', 'average_weight']
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
    
    # إضافة مجموعة جديدة
    with st.expander("➕ إضافة مجموعة جديدة", expanded=not groups):
        with st.form("add_group_form"):
            col1, col2 = st.columns(2)
            with col1:
                group_name = st.text_input("اسم المجموعة *", placeholder="قطيع الحلابة 1")
                group_type = st.text_input("نوع المجموعة", placeholder="حلابة / تسمين / صغار")
                head_count = st.number_input("عدد الرؤوس", min_value=0, step=1, value=0)
            with col2:
                avg_weight = st.number_input("متوسط الوزن (كجم)", min_value=0.0, step=1.0, value=0.0)
                birth_date = st.date_input("تاريخ الميلاد", value=datetime.now().date())
                purchase_date = st.date_input("تاريخ الشراء", value=datetime.now().date())
            
            group_notes = st.text_area("ملاحظات المجموعة")
            
            submitted = st.form_submit_button("💾 حفظ المجموعة", use_container_width=True)
            if submitted:
                if not group_name:
                    st.error("⚠️ يرجى إدخال اسم المجموعة")
                else:
                    db.create_group({
                        'farm_id': farm_id,
                        'name': group_name,
                        'group_type': group_type,
                        'head_count': head_count,
                        'average_weight': avg_weight,
                        'birth_date': birth_date.isoformat(),
                        'purchase_date': purchase_date.isoformat(),
                        'notes': group_notes
                    })
                    st.success(f"✅ تم إضافة المجموعة '{group_name}' بنجاح")
                    st.rerun()

# =====================================================================
# السجلات اليومية
# =====================================================================

def show_daily_records(db: DatabaseManager, farm_id: int):
    """عرض وإضافة السجلات اليومية"""
    
    st.subheader("📈 السجلات اليومية")
    
    # اختيار المجموعة
    groups = db.get_groups(farm_id)
    if not groups:
        st.warning("⚠️ لا توجد مجموعات حيوانية. يرجى إضافة مجموعة أولاً.")
        return
    
    group_options = {g['name']: g['id'] for g in groups}
    selected_group = st.selectbox("اختر المجموعة", list(group_options.keys()))
    group_id = group_options[selected_group]
    
    # عرض السجلات الحالية
    records = db.get_daily_records(group_id, 
                                  start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    
    if records:
        df = pd.DataFrame(records)
        display_cols = ['record_date', 'average_weight', 'feed_given', 'feed_refused', 
                       'deaths', 'health_score', 'production_amount']
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
    
    # إضافة سجل يومي
    with st.expander("➕ إضافة سجل يومي"):
        with st.form("add_daily_record"):
            col1, col2, col3 = st.columns(3)
            with col1:
                record_date = st.date_input("التاريخ", value=datetime.now().date())
                avg_weight = st.number_input("متوسط الوزن (كجم)", min_value=0.0, step=0.1)
                feed_given = st.number_input("العلف المقدم (كجم)", min_value=0.0, step=0.1)
            with col2:
                feed_refused = st.number_input("العلف المتبقي (كجم)", min_value=0.0, step=0.1, value=0.0)
                deaths = st.number_input("عدد النافق", min_value=0, step=1, value=0)
                health_score = st.slider("الحالة الصحية (1-5)", 1, 5, 5)
            with col3:
                production_amount = st.number_input("الإنتاج (لتر/كجم/عدد)", min_value=0.0, step=0.1)
                production_unit = st.text_input("وحدة الإنتاج", value="لتر")
                temperature = st.number_input("درجة الحرارة (مئوي)", min_value=-10.0, max_value=50.0, step=0.5)
            
            notes = st.text_area("ملاحظات")
            
            submitted = st.form_submit_button("💾 حفظ السجل", use_container_width=True)
            if submitted:
                db.add_daily_record({
                    'group_id': group_id,
                    'record_date': record_date.isoformat(),
                    'average_weight': avg_weight,
                    'feed_given': feed_given,
                    'feed_refused': feed_refused,
                    'deaths': deaths,
                    'health_score': health_score,
                    'production_amount': production_amount,
                    'production_unit': production_unit,
                    'temperature': temperature,
                    'notes': notes
                })
                st.success("✅ تم إضافة السجل اليومي بنجاح")
                st.rerun()

# =====================================================================
# السجلات الصحية
# =====================================================================

def show_health_records(db: DatabaseManager, farm_id: int):
    """عرض وإضافة السجلات الصحية"""
    
    st.subheader("🏥 السجلات الصحية")
    
    groups = db.get_groups(farm_id)
    if not groups:
        st.warning("⚠️ لا توجد مجموعات حيوانية")
        return
    
    group_options = {g['name']: g['id'] for g in groups}
    selected_group = st.selectbox("اختر المجموعة", list(group_options.keys()), key="health_group")
    group_id = group_options[selected_group]
    
    # عرض السجلات الصحية
    health_records = db.get_health_records(group_id)
    if health_records:
        df = pd.DataFrame(health_records)
        display_cols = ['event_date', 'event_type', 'diagnosis', 'treatment', 'veterinarian', 'cost']
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
    
    # إضافة سجل صحي
    with st.expander("➕ إضافة سجل صحي"):
        with st.form("add_health_record"):
            col1, col2 = st.columns(2)
            with col1:
                event_date = st.date_input("تاريخ الحدث", value=datetime.now().date())
                event_type = st.selectbox("نوع الحدث", ["مرض", "علاج", "لقاح", "فحص", "إصابة", "أخرى"])
                diagnosis = st.text_input("التشخيص")
            with col2:
                treatment = st.text_input("العلاج")
                veterinarian = st.text_input("الطبيب المعالج")
                cost = st.number_input("التكلفة ($)", min_value=0.0, step=5.0)
            
            notes = st.text_area("ملاحظات")
            
            submitted = st.form_submit_button("💾 حفظ السجل الصحي", use_container_width=True)
            if submitted:
                db.add_health_record({
                    'group_id': group_id,
                    'event_date': event_date.isoformat(),
                    'event_type': event_type,
                    'diagnosis': diagnosis,
                    'treatment': treatment,
                    'veterinarian': veterinarian,
                    'cost': cost,
                    'notes': notes
                })
                st.success("✅ تم إضافة السجل الصحي بنجاح")
                st.rerun()

# =====================================================================
# سجلات التكاثر
# =====================================================================

def show_reproduction_records(db: DatabaseManager, farm_id: int):
    """عرض وإضافة سجلات التكاثر"""
    
    st.subheader("🧬 سجلات التكاثر")
    
    groups = db.get_groups(farm_id)
    if not groups:
        st.warning("⚠️ لا توجد مجموعات حيوانية")
        return
    
    group_options = {g['name']: g['id'] for g in groups}
    selected_group = st.selectbox("اختر المجموعة", list(group_options.keys()), key="repro_group")
    group_id = group_options[selected_group]
    
    with st.form("add_repro_record"):
        col1, col2 = st.columns(2)
        with col1:
            insemination_date = st.date_input("تاريخ التلقيح", value=datetime.now().date())
            expected_birth = st.date_input("تاريخ الولادة المتوقع")
        with col2:
            birth_date = st.date_input("تاريخ الولادة الفعلي")
            offspring_count = st.number_input("عدد المواليد", min_value=0, step=1, value=0)
            offspring_weight = st.number_input("وزن المواليد (كجم)", min_value=0.0, step=0.1)
        
        success = st.checkbox("نجحت العملية")
        notes = st.text_area("ملاحظات")
        
        submitted = st.form_submit_button("💾 حفظ سجل التكاثر", use_container_width=True)
        if submitted:
            db.add_reproduction_record({
                'group_id': group_id,
                'insemination_date': insemination_date.isoformat(),
                'expected_birth': expected_birth.isoformat(),
                'birth_date': birth_date.isoformat(),
                'offspring_count': offspring_count,
                'offspring_weight': offspring_weight,
                'success': 1 if success else 0,
                'notes': notes
            })
            st.success("✅ تم إضافة سجل التكاثر بنجاح")
            st.rerun()

# =====================================================================
# تحليلات المزرعة المتقدمة
# =====================================================================

def show_farm_analytics(db: DatabaseManager, farm_id: int):
    """عرض تحليلات متقدمة للمزرعة"""
    
    st.subheader("📊 تحليلات متقدمة")
    
    groups = db.get_groups(farm_id)
    if not groups:
        st.warning("⚠️ لا توجد مجموعات لعرض التحليلات")
        return
    
    # اختيار المجموعة للتحليل
    group_options = {g['name']: g['id'] for g in groups}
    selected_group = st.selectbox("اختر المجموعة للتحليل", list(group_options.keys()), key="analytics_group")
    group_id = group_options[selected_group]
    
    # فترة التحليل
    days = st.slider("الفترة (أيام)", 7, 90, 30)
    
    # جلب البيانات
    records = db.get_daily_records(group_id, 
                                  start_date=(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'))
    
    if not records:
        st.info("ℹ️ لا توجد بيانات كافية للتحليل خلال هذه الفترة")
        return
    
    # تحويل إلى DataFrame
    df = pd.DataFrame(records)
    df['record_date'] = pd.to_datetime(df['record_date'])
    df = df.sort_values('record_date')
    
    # حساب المؤشرات
    performance = db.get_group_performance(group_id, days)
    
    if 'error' not in performance:
        st.success(f"📊 تحليل أداء المجموعة '{performance['group_name']}'")
        
        # عرض المؤشرات الرئيسية
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("معدل النمو اليومي (ADG)", f"{performance['adg']} كجم/يوم")
        with col2:
            st.metric("معدل التحويل الغذائي (FCR)", f"{performance['fcr']:.2f}")
        with col3:
            st.metric("معدل النافق", f"{performance['mortality_rate']:.1f}%")
        with col4:
            st.metric("متوسط الحالة الصحية", f"{performance['health_score_avg']:.1f}/5")
        
        # رسوم بيانية
        st.subheader("📈 تطور الوزن")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['record_date'], y=df['average_weight'], 
                                mode='lines+markers', name='الوزن',
                                line=dict(color='#2e7d32', width=3)))
        fig.update_layout(title='تطور الوزن خلال الفترة',
                         xaxis_title='التاريخ',
                         yaxis_title='الوزن (كجم)',
                         hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        
        # استهلاك العلف
        if 'feed_given' in df.columns:
            st.subheader("📊 استهلاك العلف")
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=df['record_date'], y=df['feed_given'], 
                                 name='العلف المقدم', marker_color='#1565C0'))
            if 'feed_refused' in df.columns:
                fig2.add_trace(go.Bar(x=df['record_date'], y=df['feed_refused'], 
                                     name='العلف المتبقي', marker_color='#ff6f00'))
            fig2.update_layout(title='استهلاك العلف اليومي',
                              xaxis_title='التاريخ',
                              yaxis_title='الكمية (كجم)',
                              barmode='group')
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning(performance['error'])

# =====================================================================
# دليل المستخدم
# =====================================================================

def show_user_guide():
    """عرض دليل المستخدم"""
    
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
    
    # تشغيل الصوت
    col_audio, col_video = st.columns(2)
    with col_audio:
        if st.button("🔊 تشغيل الدليل الصوتي", use_container_width=True):
            guide_text = """مرحباً بكم في دليل منصة تاور العلمية المطورة. هذه المنصة مصممة لمساعدة المربين والمختصين في تركيب أعلاف متوازنة بأقل تكلفة، وإدارة المزارع بشكل متكامل. يمكنكم استخدام التبويبات المختلفة للوصول إلى جميع الوظائف. نتمنى لكم تجربة مفيدة."""
            audio = text_to_speech(guide_text)
            if audio:
                st.audio(audio, format='audio/mp3')
    
    with col_video:
        if st.button("🎬 فيديو الشرح", use_container_width=True):
            st.info("سيتم إضافة فيديو شرح قريباً")
    
    # محتوى الدليل
    st.markdown("""
    <div style='background: #f5f5f5; padding: 25px; border-radius: 15px; direction: rtl;'>
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
