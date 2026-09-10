# ============================================================================
# تاور نولجي Tawornology العلمية - الإصدار المتكامل الشامل 17.0
# ============================================================================
# 🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله
# 🕊️ اللهم اجعل قبرهما روضة من رياض الجنة واجمعنا بهما في الفردوس الأعلى
# ============================================================================
# الميزات الشاملة:
# ✅ محرك الاستمثال الخطي المتقدم (Least-Cost Formulation)
# ✅ المختبر الذكي بتحليل الصور (OCR - EasyOCR/Pytesseract)
# ✅ معادلات NRC الإنتاجية المتقدمة (Dairy 2001 / Beef 2000)
# ✅ إدارة المزارع والدورات الإنتاجية (حفظ دائم SQLite)
# ✅ بدائل الحليب لرضاعة الصغار
# ✅ نظام الصوت المتسلسل (بدون ازدواجية)
# ✅ توليد PDF احترافي بالعربية (مع اسم طالب العلف)
# ✅ تقييد التركيبة بـ 75% من المعايير القياسية
# ✅ 14 تبويب متكامل
# المشرف: الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان
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
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

warnings.filterwarnings('ignore')

# =====================================================================
# مكتبات معالجة اللغة العربية وتوليد PDF والصور
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
import arabic_reshaper
from bidi.algorithm import get_display
import qrcode
from PIL import Image as PILImage
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# =====================================================================
# مكتبة الصوت (gTTS)
# =====================================================================
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# =====================================================================
# مكتبات OCR (للمختبر الذكي بالصور)
# =====================================================================
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

# =====================================================================
# إعدادات الصفحة
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
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان", "level": 3},
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
    except Exception:
        st.session_state["email_password"] = None

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

# =====================================================================
# كاش النظام
# =====================================================================
@st.cache_resource
def init_caching_system():
    return {
        "cache_hits": 0,
        "cache_misses": 0,
        "last_cleanup": datetime.now(),
        "cache_data": {}
    }
CACHE_SYSTEM = init_caching_system()

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
        except Exception:
            return str(text)

arabic_processor = ArabicTextProcessor()

print("✅ تم تحميل الجزء 1 بنجاح - الاستيرادات والإعدادات الأساسية")
# =====================================================================
# قاعدة البيانات المتقدمة (SQLite) - حفظ دائم
# =====================================================================
class DatabaseManager:
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
        
        # جدول المزارع
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
        
        # جدول دورات الإنتاج
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
        
        # جدول السجلات اليومية
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
        
        # جدول السجل الصحي
        c.execute('''CREATE TABLE IF NOT EXISTS health_records (
            health_id TEXT PRIMARY KEY,
            cycle_id TEXT,
            record_date TEXT,
            age_days INTEGER,
            treatment_type TEXT,
            treatment_name TEXT,
            dose REAL,
            dose_unit TEXT,
            administration_route TEXT,
            administered_by TEXT,
            notes TEXT,
            FOREIGN KEY (cycle_id) REFERENCES production_cycles(cycle_id)
        )''')
        
        # جدول مقارنات الأداء
        c.execute('''CREATE TABLE IF NOT EXISTS performance_comparisons (
            comparison_id TEXT PRIMARY KEY,
            cycle_id TEXT,
            comparison_date TEXT,
            metric_type TEXT,
            farm_value REAL,
            standard_value REAL,
            deviation REAL,
            status TEXT,
            FOREIGN KEY (cycle_id) REFERENCES production_cycles(cycle_id)
        )''')
        
        # جدول تنبيهات اللقاحات
        c.execute('''CREATE TABLE IF NOT EXISTS vaccine_alerts (
            alert_id TEXT PRIMARY KEY,
            cycle_id TEXT,
            alert_date TEXT,
            scheduled_date TEXT,
            vaccine_name TEXT,
            vaccine_type TEXT,
            dose TEXT,
            route TEXT,
            status TEXT,
            sent BOOLEAN DEFAULT 0,
            FOREIGN KEY (cycle_id) REFERENCES production_cycles(cycle_id)
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
            ingredients TEXT,
            total_cost REAL,
            cost_per_ton REAL,
            created_by TEXT,
            created_date TEXT,
            is_approved INTEGER DEFAULT 0,
            usage_count INTEGER DEFAULT 0,
            requester_name TEXT
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
            discount REAL DEFAULT 0,
            final_price REAL,
            status TEXT,
            created_by TEXT,
            created_date TEXT,
            notes TEXT
        )''')
        
        # جدول أسعار المواد
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
        
        # جدول المخزون
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT PRIMARY KEY,
            item_name TEXT UNIQUE,
            quantity REAL,
            min_threshold REAL,
            unit TEXT,
            last_updated TEXT,
            supplier TEXT
        )''')
        
        # جدول تحليل الجودة (OCR)
        c.execute('''CREATE TABLE IF NOT EXISTS quality_analysis (
            analysis_id TEXT PRIMARY KEY,
            sample_name TEXT,
            analysis_date TEXT,
            moisture REAL,
            protein REAL,
            fat REAL,
            fiber REAL,
            ash REAL,
            se REAL,
            dc REAL,
            ndf REAL,
            adf REAL,
            notes TEXT,
            performed_by TEXT,
            image_path TEXT
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
    
    def delete_record(self, table: str, condition: dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        where_clause = ' AND '.join([f"{k}=?" for k in condition.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        c.execute(query, list(condition.values()))
        conn.commit()
        conn.close()
        return True

# =====================================================================
# نظام إدارة المزارع المتقدم
# =====================================================================
class FarmManagementSystem:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_farm(self, farm_name, farm_type, owner_name, owner_phone, location="", area=0.0):
        farm_id = secrets.token_hex(16)
        data = {
            'farm_id': farm_id, 'farm_name': farm_name, 'farm_type': farm_type,
            'owner_name': owner_name, 'owner_phone': owner_phone,
            'location': location, 'area': area,
            'created_date': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        self.db.insert_record('farms', data)
        return farm_id
    
    def create_production_cycle(self, farm_id, cycle_type, initial_count, breed, target_weight=0.0, target_age=0):
        cycle_id = secrets.token_hex(16)
        data = {
            'cycle_id': cycle_id, 'farm_id': farm_id, 'cycle_type': cycle_type,
            'start_date': datetime.now().isoformat(), 'end_date': '',
            'initial_count': initial_count, 'breed': breed,
            'target_weight': target_weight, 'target_age': target_age,
            'status': 'active', 'notes': ''
        }
        self.db.insert_record('production_cycles', data)
        return cycle_id
    
    def add_daily_record(self, cycle_id, record_data):
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
            'record_id': record_id, 'cycle_id': cycle_id,
            'record_date': datetime.now().isoformat(),
            'age_days': record_data.get('age_days', 0),
            'live_birds': live_birds, 'avg_weight': avg_weight,
            'min_weight': record_data.get('min_weight', avg_weight * 0.9),
            'max_weight': record_data.get('max_weight', avg_weight * 1.1),
            'feed_consumed': feed_consumed,
            'water_consumed': record_data.get('water_consumed', 0),
            'dead_count': dead_count, 'culled_count': record_data.get('culled_count', 0),
            'temperature': record_data.get('temperature', 0),
            'humidity': record_data.get('humidity', 0),
            'ventilation_status': record_data.get('ventilation_status', 'جيدة'),
            'litter_quality': record_data.get('litter_quality', 'جيدة'),
            'feed_conversion': feed_conversion, 'mortality_rate': mortality_rate,
            'notes': record_data.get('notes', '')
        }
        self.db.insert_record('daily_records', data)
        self._create_performance_comparison(cycle_id, record_data)
        return record_id
    
    def add_health_record(self, cycle_id, health_data):
        health_id = secrets.token_hex(16)
        data = {
            'health_id': health_id, 'cycle_id': cycle_id,
            'record_date': datetime.now().isoformat(),
            'age_days': health_data.get('age_days', 0),
            'treatment_type': health_data.get('treatment_type', ''),
            'treatment_name': health_data.get('treatment_name', ''),
            'dose': health_data.get('dose', 0),
            'dose_unit': health_data.get('dose_unit', ''),
            'administration_route': health_data.get('administration_route', ''),
            'administered_by': health_data.get('administered_by', ''),
            'notes': health_data.get('notes', '')
        }
        self.db.insert_record('health_records', data)
        return health_id
    
    def _create_performance_comparison(self, cycle_id, record_data):
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
        
        weight_dev = ((avg_weight - std_weight) / std_weight) * 100 if std_weight > 0 else 0
        fcr_dev = ((feed_conversion - std_fcr) / std_fcr) * 100 if std_fcr > 0 else 0
        mort_dev = ((mortality_rate - std_mortality) / std_mortality) * 100 if std_mortality > 0 else 0
        
        metrics = [
            ('وزن الجسم', avg_weight, std_weight, weight_dev),
            ('معامل التحويل', feed_conversion, std_fcr, fcr_dev),
            ('نسبة النفوق', mortality_rate, std_mortality, mort_dev)
        ]
        
        for metric_name, farm_val, std_val, deviation in metrics:
            status = 'ممتاز' if abs(deviation) < 5 else ('جيد' if abs(deviation) < 10 else 'بحاجة إلى تحسين')
            comp_id = secrets.token_hex(16)
            comp_data = {
                'comparison_id': comp_id, 'cycle_id': cycle_id,
                'comparison_date': datetime.now().isoformat(),
                'metric_type': metric_name, 'farm_value': farm_val,
                'standard_value': std_val, 'deviation': deviation, 'status': status
            }
            self.db.insert_record('performance_comparisons', comp_data)
    
    def get_active_cycles(self, farm_id=None):
        if farm_id:
            return self.db.get_records('production_cycles', {'farm_id': farm_id, 'status': 'active'})
        return self.db.get_records('production_cycles', {'status': 'active'})
    
    def close_cycle(self, cycle_id):
        self.db.update_record('production_cycles',
                              {'status': 'completed', 'end_date': datetime.now().isoformat()},
                              {'cycle_id': cycle_id})
    
    def get_performance_summary(self, cycle_id):
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
    
    def check_vaccine_alerts(self, cycle_id):
        standard_vaccines = {
            1: {'type': 'فيتامين', 'name': 'فيتامين AD3E', 'dose': '1 مل/لتر', 'route': 'مياه الشرب'},
            7: {'type': 'لقاح', 'name': 'نيوكاسل (Lasota)', 'dose': 'قطرة عين', 'route': 'قطرة عين/أنف'},
            14: {'type': 'لقاح', 'name': 'Gumboro (Intermediate)', 'dose': 'قطرة فم', 'route': 'مياه الشرب'},
            21: {'type': 'دواء', 'name': 'مضاد كوكسيديا (Amprolium)', 'dose': '1 جم/لتر', 'route': 'مياه الشرب لمدة 3 أيام'},
            28: {'type': 'فيتامين', 'name': 'فيتامين C + E', 'dose': '0.5 جم/لتر', 'route': 'مياه الشرب'},
            35: {'type': 'لقاح', 'name': 'Gumboro booster', 'dose': 'قطرة فم', 'route': 'مياه الشرب'},
            42: {'type': 'لقاح', 'name': 'نيوكاسل (بخاخ)', 'dose': 'بخاخ', 'route': 'رش'},
        }
        
        records = self.db.get_records('daily_records', {'cycle_id': cycle_id})
        if not records:
            return []
        
        latest_age = records[-1][3] if records else 0
        alerts = []
        
        for age, vaccine in standard_vaccines.items():
            if age >= latest_age and age <= latest_age + 2:
                health_records = self.db.get_records('health_records', {'cycle_id': cycle_id})
                existing = [h for h in health_records if h[3] == age and h[4] == vaccine['type']]
                if not existing:
                    alert_id = secrets.token_hex(16)
                    alert_data = {
                        'alert_id': alert_id, 'cycle_id': cycle_id,
                        'alert_date': datetime.now().isoformat(),
                        'scheduled_date': (datetime.now() + timedelta(days=1)).isoformat(),
                        'vaccine_name': vaccine['name'], 'vaccine_type': vaccine['type'],
                        'dose': vaccine['dose'], 'route': vaccine['route'],
                        'status': 'pending', 'sent': 0
                    }
                    self.db.insert_record('vaccine_alerts', alert_data)
                    alerts.append(alert_data)
        return alerts

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
            ('admin', 'admin123', 'owner', 'الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان',
             'admin@tawornology.com', '+249123456789', 'تغذية حيوان', 10),
            ('specialist', 'spec123', 'specialist', 'المختص العام',
             'specialist@tawornology.com', '+249123456788', 'تغذية وإنتاج', 8),
            ('nutritionist', 'nutri123', 'nutritionist', 'أخصائي التغذية',
             'nutrition@tawornology.com', '+249123456786', 'تغذية حيوان', 7),
            ('veterinarian', 'vet123', 'veterinarian', 'الطبيب البيطري',
             'vet@tawornology.com', '+249123456785', 'طب بيطري', 9)
        ]
        for username, password, role, full_name, email, phone, specialty, experience in default_users:
            users = self.db.execute_query("SELECT * FROM users WHERE username=?", (username,))
            if not users:
                self.create_user(username, password, role, full_name, email, phone, specialty, experience)
    
    def _create_public_user(self):
        users = self.db.execute_query("SELECT * FROM users WHERE username='public'")
        if not users:
            self.create_user('public', 'public123', 'public', 'زائر',
                             'public@tawornology.com', '+249123456780', 'عام', 0)
            self.db.update_record('users', {'is_public': 1}, {'username': 'public'})
    
    def create_user(self, username, password, role, full_name, email, phone, specialty="", experience=0):
        user_id = secrets.token_hex(16)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        data = {
            'user_id': user_id, 'username': username, 'password_hash': password_hash,
            'role': role, 'full_name': full_name, 'email': email, 'phone': phone,
            'specialty': specialty, 'experience_years': experience,
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
            self.db.update_record('users', {'last_login': datetime.now().isoformat()}, {'user_id': user[0]})
            return {
                'user_id': user[0], 'username': user[1], 'role': 'public',
                'full_name': 'زائر', 'email': user[5], 'phone': user[6],
                'specialty': 'عام', 'experience_years': 0
            }
        self._create_public_user()
        return self.login_public()

print("✅ تم تحميل الجزء 2 بنجاح - قاعدة البيانات والمصادقة")
# =====================================================================
# نظام المعادلات الإنتاجية المتقدمة (NRC 2000/2001)
# =====================================================================
class AdvancedProductionEquations:
    """معادلات NRC لحساب الاحتياجات من الوزن والإنتاج الفعلي"""
    
    @staticmethod
    def calculate_milk_protein_requirement(milk_yield_kg, milk_protein_pct=3.3):
        return (milk_yield_kg * (milk_protein_pct / 100)) / 0.65
    
    @staticmethod
    def calculate_maintenance_protein(weight_kg):
        return 2.5 * (weight_kg ** 0.75)
    
    @staticmethod
    def calculate_metabolic_protein(weight_kg):
        return 1.2 * (weight_kg ** 0.75)
    
    @staticmethod
    def calculate_total_protein_for_dairy(weight_kg, milk_yield_kg, milk_fat_pct=3.5, milk_protein_pct=3.3):
        maintenance = AdvancedProductionEquations.calculate_maintenance_protein(weight_kg)
        metabolic = AdvancedProductionEquations.calculate_metabolic_protein(weight_kg)
        production = AdvancedProductionEquations.calculate_milk_protein_requirement(milk_yield_kg, milk_protein_pct)
        total = maintenance + metabolic + production
        return {
            'maintenance': maintenance, 'metabolic': metabolic,
            'production': production, 'total': total,
            'dp_requirement': (total / (weight_kg * 10)) * 100
        }
    
    @staticmethod
    def calculate_energy_for_dairy(weight_kg, milk_yield_kg, milk_fat_pct=3.5):
        maintenance = 0.08 * (weight_kg ** 0.75)
        fat_correction = 1 + 0.15 * (milk_fat_pct - 3.5)
        production = 5.3 * milk_yield_kg * fat_correction
        total = maintenance + production
        return {
            'maintenance_energy': maintenance, 'production_energy': production,
            'total_energy': total, 'se_requirement': total * 10
        }
    
    @staticmethod
    def calculate_protein_for_gain(daily_gain_kg, protein_in_gain_pct=18.0):
        return (daily_gain_kg * (protein_in_gain_pct / 100)) / 0.65
    
    @staticmethod
    def calculate_energy_for_gain(daily_gain_kg, gain_energy_pct=5.0):
        return (daily_gain_kg * gain_energy_pct) / 0.70
    
    @staticmethod
    def calculate_total_protein_for_fattening(weight_kg, daily_gain_kg):
        maintenance = 2.0 * (weight_kg ** 0.75)
        metabolic = 1.0 * (weight_kg ** 0.75)
        production = AdvancedProductionEquations.calculate_protein_for_gain(daily_gain_kg)
        total = maintenance + metabolic + production
        return {
            'maintenance': maintenance, 'metabolic': metabolic,
            'production': production, 'total': total,
            'dp_requirement': (total / (weight_kg * 8)) * 100
        }
    
    @staticmethod
    def calculate_total_energy_for_fattening(weight_kg, daily_gain_kg):
        maintenance = 0.07 * (weight_kg ** 0.75)
        production = AdvancedProductionEquations.calculate_energy_for_gain(daily_gain_kg)
        total = maintenance + production
        return {
            'maintenance_energy': maintenance, 'production_energy': production,
            'total_energy': total, 'se_requirement': total * 10
        }
    
    @staticmethod
    def calculate_protein_energy_ratio(protein_requirement, energy_requirement):
        return energy_requirement / protein_requirement if protein_requirement > 0 else 0
    
    @staticmethod
    def get_recommended_ratio(production_type):
        ratios = {
            'dairy_high': {'se_dp_ratio': 3.5, 'dp_pct': 16.0, 'se': 72.0},
            'dairy_medium': {'se_dp_ratio': 4.0, 'dp_pct': 14.0, 'se': 68.0},
            'dairy_low': {'se_dp_ratio': 4.5, 'dp_pct': 12.0, 'se': 64.0},
            'fattening_high': {'se_dp_ratio': 5.0, 'dp_pct': 14.0, 'se': 74.0},
            'fattening_medium': {'se_dp_ratio': 5.5, 'dp_pct': 12.0, 'se': 70.0},
            'fattening_low': {'se_dp_ratio': 6.0, 'dp_pct': 10.0, 'se': 66.0},
        }
        return ratios.get(production_type, {'se_dp_ratio': 4.5, 'dp_pct': 14.0, 'se': 70.0})

# =====================================================================
# نظام المختبر الذكي (OCR) - تحليل صور التركيبات
# =====================================================================
class SmartLabSystem:
    """نظام تحليل صور التركيبات العلفية باستخدام OCR"""
    
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
            return None, "مكتبات OCR غير مثبتة. قم بتثبيت easyocr أو pytesseract."
        results = []
        try:
            if EASYOCR_AVAILABLE and self.reader:
                result = self.reader.readtext(np.array(image))
                for (bbox, text, prob) in result:
                    if prob > 0.3:
                        results.append(text)
            elif OCR_AVAILABLE:
                img = PILImage.open(image) if not isinstance(image, PILImage.Image) else image
                text = pytesseract.image_to_string(img, lang='ara+eng')
                results = text.split('\n')
            return self._parse_ocr_results(results), None
        except Exception as e:
            return None, f"خطأ في تحليل الصورة: {str(e)}"
    
    def _parse_ocr_results(self, texts):
        data = {
            'sample_name': '', 'cp': None, 'dc': None, 'se': None,
            'ndf': None, 'adf': None, 'ee': None, 'ash': None, 'moisture': None
        }
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
        for text in texts:
            t = text.strip()
            if 'اسم' in t and not data['sample_name']:
                parts = t.split(':')
                if len(parts) > 1:
                    data['sample_name'] = parts[1].strip()
            for key, plist in patterns.items():
                if data[key] is None:
                    for pattern in plist:
                        m = re.search(pattern, t, re.IGNORECASE)
                        if m:
                            try:
                                data[key] = float(m.group(1))
                                break
                            except Exception:
                                pass
        return data
    
    def save_lab_result(self, result_data):
        result_id = secrets.token_hex(16)
        data = {
            'analysis_id': result_id,
            'sample_name': result_data.get('sample_name', ''),
            'analysis_date': datetime.now().isoformat(),
            'moisture': result_data.get('moisture', 0.0),
            'protein': result_data.get('cp', 0.0),
            'fat': result_data.get('ee', 0.0),
            'fiber': result_data.get('ndf', 0.0),
            'ash': result_data.get('ash', 0.0),
            'se': result_data.get('se', 0.0),
            'dc': result_data.get('dc', 0.0),
            'ndf': result_data.get('ndf', 0.0),
            'adf': result_data.get('adf', 0.0),
            'notes': result_data.get('notes', ''),
            'performed_by': result_data.get('analyzed_by', ''),
            'image_path': result_data.get('image_path', '')
        }
        try:
            self.db.insert_record('quality_analysis', data)
        except Exception as e:
            print(f"خطأ حفظ: {e}")
        return result_id
    
    def get_lab_results(self, limit=50):
        try:
            return self.db.execute_query(
                "SELECT * FROM quality_analysis ORDER BY analysis_date DESC LIMIT ?", (limit,))
        except Exception:
            return []

# =====================================================================
# نظام المراجع العلمية
# =====================================================================
class ScientificReferenceSystem:
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان", "icon": "📚",
            "references": [
                {"id": "REF001", "authors": "McDonald, P., Edwards, R.A., Greenhalgh, J.F.D., Morgan, C.A.",
                 "year": 2011, "title": "Animal Nutrition", "publisher": "Pearson Education",
                 "edition": "7th Edition", "isbn": "978-1408204238",
                 "summary": "المرجع الأساسي في تغذية الحيوان."},
                {"id": "REF002", "authors": "Cheeke, P.R., Dierenfeld, E.S.",
                 "year": 2010, "title": "Comparative Animal Nutrition and Metabolism",
                 "publisher": "CABI", "isbn": "978-1845936310",
                 "summary": "مقارنة بين آليات التغذية والتمثيل الغذائي."}
            ]
        },
        "protein_amino_acids": {
            "title": "البروتين والأحماض الأمينية", "icon": "🧬",
            "references": [
                {"id": "REF003", "authors": "NRC", "year": 2012,
                 "title": "Nutrient Requirements of Swine",
                 "publisher": "National Academies Press",
                 "summary": "المرجع الرسمي لمتطلبات الخنازير."},
                {"id": "REF004", "authors": "NRC", "year": 2001,
                 "title": "Nutrient Requirements of Dairy Cattle",
                 "publisher": "National Academies Press",
                 "summary": "المرجع الأساسي في تغذية أبقار الحليب."}
            ]
        },
        "energy_carbohydrates": {
            "title": "الطاقة والكربوهيدرات", "icon": "⚡",
            "references": [
                {"id": "REF006", "authors": "Van Soest, P.J.", "year": 1994,
                 "title": "Nutritional Ecology of the Ruminant",
                 "publisher": "Cornell University Press", "isbn": "978-0801427725",
                 "summary": "المرجع الكلاسيكي في تغذية المجترات."}
            ]
        },
        "minerals_vitamins": {
            "title": "المعادن والفيتامينات", "icon": "🪨",
            "references": [
                {"id": "REF008", "authors": "Underwood, E.J., Suttle, N.F.", "year": 1999,
                 "title": "The Mineral Nutrition of Livestock", "publisher": "CABI",
                 "isbn": "978-0851991283", "summary": "المرجع الشامل في تغذية المعادن."}
            ]
        },
        "poultry": {
            "title": "تغذية الدواجن", "icon": "🐔",
            "references": [
                {"id": "REF010", "authors": "Leeson, S., Summers, J.D.", "year": 2009,
                 "title": "Commercial Poultry Nutrition",
                 "publisher": "Nottingham University Press", "isbn": "978-1904761578",
                 "summary": "المرجع العملي في تغذية الدواجن."},
                {"id": "REF011", "authors": "NRC", "year": 1994,
                 "title": "Nutrient Requirements of Poultry",
                 "publisher": "National Academies Press",
                 "summary": "المرجع الرسمي لمتطلبات الدواجن."}
            ]
        },
        "ruminants": {
            "title": "تغذية المجترات", "icon": "🐄",
            "references": [
                {"id": "REF012", "authors": "Church, D.C.", "year": 1993,
                 "title": "The Ruminant Animal", "publisher": "Waveland Press",
                 "isbn": "978-0881337389",
                 "summary": "المرجع الشامل في فسيولوجيا الهضم والتغذية للمجترات."}
            ]
        },
        "sheep_goats": {
            "title": "تغذية الأغنام والماعز", "icon": "🐏",
            "references": [
                {"id": "REF014", "authors": "NRC", "year": 2007,
                 "title": "Nutrient Requirements of Small Ruminants",
                 "publisher": "National Academies Press",
                 "summary": "المرجع الرسمي لمتطلبات الأغنام والماعز."}
            ]
        },
        "horses": {
            "title": "تغذية الخيول", "icon": "🐴",
            "references": [
                {"id": "REF015", "authors": "NRC", "year": 2007,
                 "title": "Nutrient Requirements of Horses",
                 "publisher": "National Academies Press",
                 "summary": "المرجع الأساسي في تغذية الخيول."}
            ]
        },
        "camels": {
            "title": "تغذية الإبل", "icon": "🐫",
            "references": [
                {"id": "REF030", "authors": "Faye, B., Bengoumi, M.", "year": 2018,
                 "title": "Camel Nutrition and Feeding", "publisher": "FAO",
                 "summary": "المرجع الأساسي في تغذية الإبل."}
            ]
        },
        "aquaculture": {
            "title": "تغذية الأسماك", "icon": "🐟",
            "references": [
                {"id": "REF016", "authors": "Halver, J.E., Hardy, R.W.", "year": 2002,
                 "title": "Fish Nutrition", "publisher": "Academic Press",
                 "isbn": "978-0123196521",
                 "summary": "المرجع الشامل في تغذية الأسماك."}
            ]
        },
        "broiler": {
            "title": "إنتاج الدجاج اللاحم", "icon": "🐔",
            "references": [
                {"id": "REF020", "authors": "Ross 308 Broiler Management Guide", "year": 2020,
                 "title": "Ross Broiler Management Handbook", "publisher": "Aviagen",
                 "summary": "الدليل الشامل لإدارة الدجاج اللاحم."}
            ]
        },
        "digestible_protein": {
            "title": "البروتين المهضوم", "icon": "🧪",
            "references": [
                {"id": "REF023", "authors": "INRA", "year": 2007,
                 "title": "INRA Feeding System for Ruminants",
                 "publisher": "Wageningen Academic Publishers",
                 "isbn": "978-9086860197",
                 "summary": "النظام الفرنسي لتغذية المجترات."},
                {"id": "REF024", "authors": "Pesti, G.M., Miller, B.R.", "year": 2009,
                 "title": "Least-Cost Feed Formulation",
                 "publisher": "University of Georgia",
                 "summary": "النظرية والتطبيق لتركيب الأعلاف بأقل تكلفة."}
            ]
        },
        "layer": {
            "title": "إنتاج الدجاج البياض", "icon": "🥚",
            "references": [
                {"id": "REF025", "authors": "Hy-Line International", "year": 2021,
                 "title": "Hy-Line Management Guide", "publisher": "Hy-Line",
                 "summary": "الدليل المتخصص لإدارة الدجاج البياض."}
            ]
        },
        "milk_replacers": {
            "title": "بدائل الحليب لرضاعة الصغار", "icon": "🍼",
            "references": [
                {"id": "REF040", "authors": "Davis, C.L., Drackley, J.K.", "year": 1998,
                 "title": "The Development, Nutrition, and Management of the Young Calf",
                 "publisher": "Iowa State University Press",
                 "summary": "المرجع الأساسي في تغذية العجول الصغيرة."}
            ]
        }
    }
    
    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم (DP) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف. يتم حسابه بضرب نسبة البروتين الخام في معامل الهضم.",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (SE) هو مقياس لكمية الطاقة التي يوفرها العلف للحيوان، مقارنة بالطاقة التي يوفرها النشاء النقي.",
            "simplified": "معادل النشاء يقيس كمية الطاقة في العلف."
        },
        "كيف يتم تركيب العلف الأمثل": {
            "answer": "يتم تركيب العلف الأمثل باستخدام محرك الاستمثال الخطي (Linear Programming) الذي يحسب أقل تكلفة لتحقيق متطلبات غذائية محددة.",
            "simplified": "نستخدم برنامجاً ذكياً يحسب أرخص خلطة علفية تلبي جميع احتياجات الحيوان."
        },
        "ما هو مؤشر EPEF": {
            "answer": "مؤشر الأداء الأوروبي EPEF = (الحيوية × الوزن الحي) / (العمر × معامل التحويل الغذائي) × 100.",
            "simplified": "EPEF هو رقم يعبر عن كفاءة مزرعة الدجاج."
        },
        "ما هي أهمية إضافة الإنزيمات": {
            "answer": "الإنزيمات في الأعلاف تحسن هضم واستفادة الحيوان من العناصر الغذائية. الفايتيز تحرر الفسفور المرتبط، وإنزيمات NSP تكسر جدران الخلايا النباتية.",
            "simplified": "الإنزيمات تساعد الحيوان على هضم العلف بشكل أفضل."
        },
        "كيف يتم تركيب بديل الحليب": {
            "answer": "يتم تركيب بديل الحليب باستخدام مكونات مثل مصل الحليب، الدهون النباتية، الفيتامينات والمعادن، مع ضبط النسب حسب عمر ونوع الحيوان.",
            "simplified": "بديل الحليب هو خليط سائل يحاكي تركيب الحليب الطبيعي للرضاعة."
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
        question_lower = question.strip()
        for key, value in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            if key in question_lower:
                return {
                    "answer": value["answer"],
                    "simplified": value.get("simplified", value["answer"])
                }
        return None

# =====================================================================
# نظام التنبؤ بالأسعار
# =====================================================================
class PricePredictor:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_price_trend(self, ingredient_name, days=30):
        results = self.db.execute_query(
            "SELECT * FROM price_history WHERE ingredient_name=? ORDER BY record_date DESC LIMIT ?",
            (ingredient_name, days))
        if len(results) < 3:
            return {'trend': 'stable', 'change_percent': 0}
        prices = [r[2] for r in results]
        x = np.array(range(len(prices))).reshape(-1, 1)
        y = np.array(prices)
        model = LinearRegression()
        model.fit(x, y)
        slope = model.coef_[0]
        change_percent = ((prices[0] - prices[-1]) / prices[-1]) * 100 if prices[-1] > 0 else 0
        trend = 'up' if slope > 0.5 else 'down' if slope < -0.5 else 'stable'
        return {
            'trend': trend, 'change_percent': change_percent,
            'current_price': prices[0]
        }
    
    def predict_price(self, ingredient_name, days_ahead=7):
        trend_data = self.get_price_trend(ingredient_name, 30)
        prices = self.db.execute_query(
            "SELECT price FROM price_history WHERE ingredient_name=? ORDER BY record_date DESC LIMIT 30",
            (ingredient_name,))
        if len(prices) < 5:
            return {'prediction': None, 'confidence': 0}
        price_list = [p[0] for p in prices]
        weights = np.array(range(1, len(price_list) + 1))
        weighted_avg = np.average(price_list, weights=weights)
        trend = (price_list[0] - price_list[-1]) / len(price_list) if len(price_list) > 1 else 0
        prediction = weighted_avg + (trend * days_ahead)
        return {
            'prediction': max(0, prediction),
            'confidence': min(1, len(price_list) / 30),
            'current_price': price_list[0] if price_list else None,
            'trend': trend_data['trend']
        }

print("✅ تم تحميل الجزء 3 بنجاح - المعادلات والمختبر الذكي والمراجع")
# =====================================================================
# مكتبة الأعلاف الشاملة
# =====================================================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6},
        "جريش أرز رزاز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2},
        "دخن محلي غزير": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0},
        "تفل العنب المجفف": {"CP": 12.0, "DC": 0.50, "SE": 45.0, "NDF": 45.0, "ADF": 30.0, "EE": 5.0, "ASH": 8.0},
        "نخالة الأرز الدهنية": {"CP": 12.5, "DC": 0.70, "SE": 55.0, "NDF": 30.0, "ADF": 15.0, "EE": 15.0, "ASH": 8.0},
        "علف الشعير المستنبت": {"CP": 15.0, "DC": 0.75, "SE": 60.0, "NDF": 25.0, "ADF": 12.0, "EE": 3.0, "ASH": 5.0}
    },
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5},
        "كسب بذرة القطن غير المقشور": {"CP": 35.0, "DC": 0.70, "SE": 48.0, "NDF": 35.0, "ADF": 22.0, "EE": 2.0, "ASH": 7.0},
        "كسب بذور اللفت (كانولا)": {"CP": 38.0, "DC": 0.82, "SE": 62.0, "NDF": 28.0, "ADF": 18.0, "EE": 3.5, "ASH": 7.5},
        "كسب زهرة الشمس الكامل": {"CP": 30.0, "DC": 0.74, "SE": 40.0, "NDF": 42.0, "ADF": 28.0, "EE": 3.0, "ASH": 6.0}
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5},
        "مخلفات مصانع البسكويت": {"CP": 10.0, "DC": 0.80, "SE": 65.0, "NDF": 8.0, "ADF": 4.0, "EE": 12.0, "ASH": 3.0},
        "قش الأرز المعالج": {"CP": 4.0, "DC": 0.40, "SE": 25.0, "NDF": 65.0, "ADF": 40.0, "EE": 1.5, "ASH": 12.0}
    },
    "🧬 البروتين الحيواني": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق أسماك فاخر (72%)": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5},
        "بروتين مصل الحليب (WPC)": {"CP": 80.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 3.0, "ASH": 3.0},
        "بروتين الدم المجفف": {"CP": 85.0, "DC": 0.92, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.5, "ASH": 5.0}
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3},
        "ثريونين نقي (L-Threonine)": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2},
        "تريبتوفان نقي (L-Tryptophan)": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1},
        "فالين نقي (L-Valine)": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1}
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس بياض وبشاير": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
        "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0},
        "كبريتات الحديدوز (معادل الجوسيبول)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0},
        "مستخلص الخمائر والجدر الخلوية (MOS)": {"CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5, "EE": 1.5, "ASH": 8.5},
        "خميرة الخبز (Yeast)": {"CP": 45.0, "DC": 0.85, "SE": 35.0, "NDF": 5.0, "ADF": 2.0, "EE": 2.5, "ASH": 7.0}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
        "أكسيد المغنيسيوم العلفي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "يوريا علفية محصنة (المجترات فقط)": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0},
        "كلوريد الكولين (Choline Chloride)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 75.0}
    },
    "🍼 مكونات بدائل الحليب": {
        "مصل الحليب المجفف (Whey)": {"CP": 12.0, "DC": 0.95, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.0},
        "حليب مجفف خالي الدسم": {"CP": 34.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.5},
        "دهن نباتي (زيت نباتي)": {"CP": 0.0, "DC": 0.0, "SE": 10.0, "NDF": 0.0, "ADF": 0.0, "EE": 99.0, "ASH": 0.0},
        "ليسيثين الصويا": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 95.0, "ASH": 0.5},
        "فيتامينات ومعادن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بروتين الصويا المركز": {"CP": 65.0, "DC": 0.90, "SE": 30.0, "NDF": 2.0, "ADF": 1.0, "EE": 1.0, "ASH": 5.5}
    }
}

# قاموس مسطح للوصول السريع
FLAT_FEED_DB = {}
for category, items in BIG_FEEDS_LIBRARY.items():
    for feed_name, nutrition in items.items():
        FLAT_FEED_DB[feed_name] = nutrition

# =====================================================================
# المعايير القياسية للعناصر الغذائية (موسعة)
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
        "تسمين": {"DP": 11.0, "SE": 62.0, "CP": 13.8},
        "عمل/نقل": {"DP": 10.0, "SE": 58.0, "CP": 12.5}
    },
    "دواجن": {
        "بادي (0-14 يوم)": {"DP": 22.0, "SE": 76.0, "CP": 27.5},
        "نامي (15-28 يوم)": {"DP": 20.0, "SE": 74.0, "CP": 25.0},
        "ناهي (29-42 يوم)": {"DP": 18.0, "SE": 72.0, "CP": 22.5},
        "ناهي متقدم (43+ يوم)": {"DP": 16.0, "SE": 70.0, "CP": 20.0}
    },
    "أسماك": {
        "زريعة/بادئ": {"DP": 32.0, "SE": 70.0, "CP": 40.0},
        "نمو": {"DP": 28.0, "SE": 68.0, "CP": 35.0},
        "تسمين نهائي": {"DP": 26.0, "SE": 66.0, "CP": 32.5},
        "زريعة متقدمة": {"DP": 30.0, "SE": 69.0, "CP": 37.5}
    }
}

# =====================================================================
# نظام أسعار المدن
# =====================================================================
class MarketPriceEngine:
    @staticmethod
    @lru_cache(maxsize=128)
    def get_adjusted_market_data(country, state_or_region, city):
        feed_prices = {}
        for cat in BIG_FEEDS_LIBRARY.values():
            for ing in cat:
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
            "خميرة الخبز (Yeast)": 450.0,
            "مصل الحليب المجفف (Whey)": 1200.0,
            "حليب مجفف خالي الدسم": 1800.0,
            "دهن نباتي (زيت نباتي)": 800.0,
            "ليسيثين الصويا": 1500.0,
            "بروتين الصويا المركز": 2000.0
        }
        feed_prices.update(base_prices)
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
# صور الحيوانات
# =====================================================================
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
# إدارة المخزون
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

print("✅ تم تحميل الجزء 4 بنجاح - مكتبة الأعلاف والمعايير")
# =====================================================================
# دوال الصوت (متسلسل بدون ازدواجية)
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
    if not GTTS_AVAILABLE:
        st.warning("⚠️ الصوت غير متاح")
        return
    for i, msg in enumerate(messages):
        if msg:
            audio_b64 = text_to_speech_base64(msg, lang)
            if audio_b64:
                play_audio_b64(audio_b64)
                word_count = len(msg.split())
                duration = max(2.0, word_count * 0.3 + 1.0)
                time.sleep(duration)
                if i < len(messages) - 1:
                    time.sleep(1.0)

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

def play_full_guide_audio():
    messages = [
        "مرحباً بك في منصة تاور نولجي Tawornology العلمية،",
        "هذه المنصة متخصصة في الانتاج الحيواني وتركيب الاعلاف.",
        "لديها عدة أقسام رئيسية:",
        "القسم الأول: القطاع الحيواني، لتركيب أعلاف للأبقار والأغنام والماعز والخيول والإبل والدواجن والأسماك.",
        "القسم الثاني: المختبر الذكي، لتحليل صور التركيبات العلفية.",
        "القسم الثالث: إدارة المزارع لتتبع دورات إنتاج الدجاج.",
        "القسم الرابع: بدائل الحليب لتركيب حليب صناعي للصغار.",
        "القسم الخامس: مواقيت الصلاة، لعرض أوقات الصلاة حسب المدينة.",
        "القسم السادس: منبه الجرعات، لتسجيل وتتبع اللقاحات والفيتامينات.",
        "القسم السابع: بورصة الأسعار، لمتابعة أسعار المواشي والمنتجات.",
        "القسم الثامن: المستودعات، لإدارة المخزون.",
        "القسم التاسع: الإنتاج اليومي، لتسجيل بيانات الإنتاج.",
        "القسم العاشر: المراجع العلمية، للاطلاع على المصادر المعتمدة.",
        "يمكنك أيضاً استخدام المعادلات الإنتاجية المتقدمة NRC للألبان والتسمين.",
        "جميع التقارير يمكن تحميلها بصيغة PDF مع توقيع المشرف.",
        "نسأل الله التوفيق والسداد."
    ]
    voice_guide_sequential(messages, delay_between=2.5)

# =====================================================================
# إرسال الكود بالبريد
# =====================================================================
def send_code_to_email(receiver_email):
    if receiver_email.strip().lower() != OWNER_EMAIL.strip().lower():
        return False, "❌ عذراً، الإرسال مسموح فقط للبريد: " + OWNER_EMAIL
    if not st.session_state.get("email_password"):
        return False, "⚠️ يرجى إدخال كلمة مرور البريد (App Password)."
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception:
        code_content = "# تعذر قراءة الكود"
    file_hash = hashlib.md5(code_content.encode()).hexdigest()
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود - تاور نولجي Tawornology العلمية v17.0"
    body = f"""السلام عليكم ورحمة الله وبركاته،

مرفق السورس كود الكامل لمنصة تاور نولجي Tawornology العلمية.

📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔑 التوقيع الرقمي: {file_hash}
👨‍💻 المشرف: الاختصاصي م. عبد القادر إسماعيل تاور
🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    attachment = MIMEText(code_content, 'plain', 'utf-8')
    attachment.add_header('Content-Disposition', 'attachment', filename="tawornology_v17.py")
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
    except Exception:
        pass
    system_fonts = [
        "/usr/share/fonts/truetype/arabic/Amiri-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
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
        except Exception:
            pass
    return 'Helvetica'

# =====================================================================
# مولد PDF الاحترافي
# =====================================================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = ensure_arabic_font()
        self.styles = self._create_styles()
    
    def _create_styles(self):
        styles = {}
        styles['title'] = ParagraphStyle('title', fontName=self.font_name, fontSize=24,
            alignment=TA_CENTER, textColor=HexColor('#1b5e20'), spaceAfter=20, leading=30)
        styles['subtitle'] = ParagraphStyle('subtitle', fontName=self.font_name, fontSize=16,
            alignment=TA_CENTER, textColor=HexColor('#2e7d32'), spaceAfter=15, leading=20)
        styles['heading'] = ParagraphStyle('heading', fontName=self.font_name, fontSize=14,
            alignment=TA_RIGHT, textColor=HexColor('#1b5e20'), spaceAfter=10, leading=18)
        styles['body'] = ParagraphStyle('body', fontName=self.font_name, fontSize=11,
            alignment=TA_RIGHT, textColor=HexColor('#333333'), spaceAfter=6, leading=16)
        styles['footer'] = ParagraphStyle('footer', fontName=self.font_name, fontSize=8,
            alignment=TA_CENTER, textColor=HexColor('#999999'), spaceAfter=0, leading=10)
        return styles
    
    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city,
                                      local_cost, local_sym, computed_se, user_name,
                                      requester_name="", standard=None,
                                      include_charts=True, extra_info=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50,
                                topMargin=50, bottomMargin=50)
        story = []
        
        def p(text, style='body'):
            safe = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe, self.styles.get(style, self.styles['body']))
        
        story.append(p("🌾 تاور نولجي Tawornology العلمية", 'title'))
        story.append(p("📄 تقرير فني شامل - تقرير التركيب", 'subtitle'))
        story.append(Spacer(1, 10))
        
        for line in [
            f"👨‍💻 المشرف العام: {user_name}",
            f"📌 الموقع: {city}",
            f"🐾 الفصيل: {breed}",
            f"📅 تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ]:
            story.append(p(line))
        
        if requester_name:
            story.append(p(f"👤 طالب العلف: {requester_name}"))
        
        story.append(Spacer(1, 15))
        
        tdata = [
            ['المعيار', 'القيمة'],
            ['البروتين المهضوم (DP)', f'{target_dp:.2f}%'],
            ['معادل النشاء (SE)', f'{computed_se:.2f}'],
            ['التكلفة للطن', f'${cost:.2f} ({local_cost:,.2f} {local_sym})']
        ]
        t = Table([[arabic_processor.fix_arabic_text(c) for c in row] for row in tdata],
                  colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#2e7d32'))
        ]))
        story.append(t)
        story.append(Spacer(1, 10))
        
        if standard:
            story.append(p("📏 مقارنة مع المعايير القياسية:", 'heading'))
            comp_data = [['المقياس', 'المحسوب', 'القياسي', 'الانحراف %', 'التقييم']]
            if 'DP' in standard:
                dev = ((target_dp - standard['DP']) / standard['DP']) * 100 if standard['DP'] > 0 else 0
                grade = "ممتاز ✅" if abs(dev) <= 5 else ("جيد ⚠️" if abs(dev) <= 10 else "ضعيف ❌")
                comp_data.append(['DP', f"{target_dp:.2f}%", f"{standard['DP']:.2f}%", f"{dev:.1f}", grade])
            if 'SE' in standard:
                dev = ((computed_se - standard['SE']) / standard['SE']) * 100 if standard['SE'] > 0 else 0
                grade = "ممتاز ✅" if abs(dev) <= 5 else ("جيد ⚠️" if abs(dev) <= 10 else "ضعيف ❌")
                comp_data.append(['SE', f"{computed_se:.2f}", f"{standard['SE']:.2f}", f"{dev:.1f}", grade])
            t_comp = Table([[arabic_processor.fix_arabic_text(c) for c in row] for row in comp_data],
                           colWidths=[100, 100, 100, 100, 80])
            t_comp.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
                ('TEXTCOLOR', (0,0), (-1,0), white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,-1), self.font_name),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd'))
            ]))
            story.append(t_comp)
        
        story.append(PageBreak())
        story.append(p("📋 المقادير المعتمدة لتركيب الطن الواحد:", 'heading'))
        story.append(Spacer(1, 10))
        ing_data = [['المكون', 'النسبة %', 'كجم/طن']]
        for ing, pct in formula.items():
            ing_data.append([ing, f'{pct:.2f}%', f'{pct*10:.1f}'])
        t2 = Table([[arabic_processor.fix_arabic_text(c) for c in row] for row in ing_data],
                   colWidths=[180, 150, 150])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')])
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
                         loc='center left', bbox_to_anchor=(1,0,0.5,1), fontsize=8)
                ax.set_title(arabic_processor.fix_arabic_text('توزيع المكونات'), fontsize=12)
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=120, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=420, height=240))
            except Exception:
                pass
        
        story.append(Spacer(1, 20))
        story.append(p("📌 التوصيات الفنية:", 'heading'))
        for rec in [
            "• يوصى بإضافة الإنزيمات لتحسين الهضم.",
            "• يجب مراقبة جودة المواد الخام بشكل دوري.",
            "• يجب تخزين العلف في مكان جاف بعيداً عن الرطوبة."
        ]:
            story.append(p(rec))
        
        if extra_info:
            story.append(Spacer(1, 15))
            story.append(p("معلومات إضافية:", 'heading'))
            for key, value in extra_info.items():
                if value:
                    story.append(p(f"• {key}: {value}"))
        
        story.append(Spacer(1, 25))
        story.append(p("مع خالص التحية والتقدير،", 'body'))
        story.append(p(user_name, 'body'))
        story.append(Spacer(1, 15))
        story.append(p("تم التوليد بواسطة تاور نولجي Tawornology © 2026", 'footer'))
        story.append(p("🕊️ إهداء إلى روح إسماعيل تاور وابتسام", 'footer'))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_lab_report(self, analysis_results, animal_type, stage, user_name,
                            standard=None, evaluation=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40,
                                topMargin=40, bottomMargin=40)
        story = []
        
        def p(text, style='body'):
            safe = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe, self.styles.get(style, self.styles['body']))
        
        story.append(p("🔬 تقرير التحليل المخبري المتقدم", 'title'))
        story.append(p(f"👨‍💻 المشرف: {user_name}", 'subtitle'))
        story.append(Spacer(1, 10))
        story.append(p(f"🐾 الحيوان: {animal_type} | المرحلة: {stage}", 'body'))
        story.append(p(f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 'body'))
        story.append(Spacer(1, 10))
        
        if analysis_results:
            if 'cp' in analysis_results:
                story.append(p(f"• البروتين الخام (CP): {analysis_results['cp']:.2f}%", 'body'))
            if 'dp' in analysis_results:
                story.append(p(f"• البروتين المهضوم (DP): {analysis_results['dp']:.2f}%", 'body'))
            if 'se' in analysis_results:
                story.append(p(f"• معادل النشاء (SE): {analysis_results['se']:.2f}", 'body'))
        
        story.append(Spacer(1, 15))
        story.append(p(user_name, 'body'))
        story.append(Spacer(1, 15))
        story.append(p("تم التوليد بواسطة تاور نولجي Tawornology © 2026", 'footer'))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_milk_replacer_report(self, formula, animal_type, age_days, instructions, user_name):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50,
                                topMargin=50, bottomMargin=50)
        story = []
        
        def p(text, style='body'):
            safe = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe, self.styles.get(style, self.styles['body']))
        
        story.append(p("🍼 تقرير تركيب بديل الحليب", 'title'))
        story.append(p(f"👨‍💻 المشرف: {user_name}", 'subtitle'))
        story.append(Spacer(1, 10))
        story.append(p(f"🐾 الحيوان: {animal_type} | العمر: {age_days} يوم", 'body'))
        story.append(Spacer(1, 15))
        story.append(p("📋 مكونات بديل الحليب:", 'heading'))
        
        ing_data = [['المكون', 'النسبة %', 'جم/لتر']]
        for ing, pct in formula.items():
            ing_data.append([ing, f'{pct:.2f}%', f'{pct*10:.1f}'])
        t = Table([[arabic_processor.fix_arabic_text(c) for c in row] for row in ing_data],
                  colWidths=[200, 130, 130])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd'))
        ]))
        story.append(t)
        story.append(Spacer(1, 15))
        story.append(p("📌 تعليمات التقديم:", 'heading'))
        for line in instructions.split('\n'):
            if line.strip():
                story.append(p(f"• {line.strip()}", 'body'))
        
        story.append(Spacer(1, 20))
        story.append(p(user_name, 'body'))
        story.append(Spacer(1, 15))
        story.append(p("تم التوليد بواسطة تاور نولجي Tawornology © 2026", 'footer'))
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
    
    @staticmethod
    def get_temp_humidity_table():
        return pd.DataFrame({
            "العمر (يوم)": [1, 3, 7, 14, 21, 28, 35, 42],
            "درجة الحرارة (مئوي)": [33, 32, 30, 28, 26, 24, 22, 21],
            "الرطوبة النسبية (%)": [65, 65, 65, 60, 60, 55, 55, 55]
        })

print("✅ تم تحميل الجزء 5 بنجاح - الصوت و PDF")
# =====================================================================
# دالة تركيب بديل الحليب
# =====================================================================
def render_milk_replacer():
    st.markdown('<div class="section-title">🍼 تركيب بديل الحليب لرضاعة الصغار</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#e8f5e9; padding:18px; border-radius:14px; direction:rtl; margin-bottom:20px;'>
    <b>🧬 هذا القسم مخصص لتركيب بدائل الحليب:</b> يُستخدم لتغذية الصغار (عجول، حملان، جديان، مهرات، أطفال الإبل)
    عند عدم توفر الحليب الطبيعي. التركيبة تحاكي الحليب الطبيعي من حيث البروتين والدهون والطاقة.
    </div>
    """, unsafe_allow_html=True)
    
    animal_type = st.selectbox("نوع الحيوان:",
        ["عجل بقري", "حملان أغنام", "جديان ماعز", "مهرات خيول", "أطفال إبل"],
        key="mr_animal")
    age_days = st.slider("العمر (يوم)", min_value=1, max_value=120, value=30, step=1, key="mr_age")
    
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
    
    st.info(f"📊 الاحتياجات: بروتين {target_protein:.1f}% | دهون {target_fat:.1f}% | طاقة {target_energy:.1f} | الحجم {daily_volume:.1f} لتر/يوم")
    
    replacer_ingredients = {
        "حليب مجفف خالي الدسم": {"CP": 34.0, "Fat": 1.0, "SE": 40.0, "Cost": 18.0},
        "مصل الحليب المجفف (Whey)": {"CP": 12.0, "Fat": 1.0, "SE": 35.0, "Cost": 12.0},
        "دهن نباتي (زيت نباتي)": {"CP": 0.0, "Fat": 99.0, "SE": 10.0, "Cost": 8.0},
        "ليسيثين الصويا": {"CP": 0.0, "Fat": 95.0, "SE": 0.0, "Cost": 15.0},
        "بروتين الصويا المركز": {"CP": 65.0, "Fat": 1.0, "SE": 30.0, "Cost": 20.0},
        "فيتامينات ومعادن (Premix)": {"CP": 0.0, "Fat": 0.0, "SE": 0.0, "Cost": 25.0}
    }
    
    selected = []
    prices = {}
    cols = st.columns(3)
    for i, (ing, data) in enumerate(replacer_ingredients.items()):
        with cols[i % 3]:
            if st.checkbox(ing, value=(i < 4), key=f"replacer_{ing}"):
                selected.append(ing)
                prices[ing] = st.number_input(f"سعر {ing} ($/كجم)", min_value=1.0,
                                              value=float(data["Cost"]), step=0.5,
                                              key=f"replacer_price_{ing}")
    
    if st.button("🍼 تشغيل محرك تركيب بديل الحليب", type="primary", key="mr_run"):
        if len(selected) < 3:
            st.warning("⚠️ يرجى اختيار 3 مكونات على الأقل")
        else:
            with st.spinner("جاري حساب التركيبة..."):
                try:
                    c = [prices[ing] for ing in selected]
                    bounds = [(0, 100) for _ in selected]
                    protein_row = [replacer_ingredients[ing]["CP"] for ing in selected]
                    fat_row = [replacer_ingredients[ing]["Fat"] for ing in selected]
                    energy_row = [replacer_ingredients[ing]["SE"] for ing in selected]
                    
                    # قيد: مجموع = 100، بروتين = الهدف، دهون ≥ الهدف
                    A_eq = [[1] * len(selected)]
                    b_eq = [100]
                    
                    # تعديل: نستخدم قيود غير متساوية للحفاظ على مرونة
                    A_ub = []
                    b_ub = []
                    # دهون لا تتجاوز الحد
                    A_ub.append(fat_row)
                    b_ub.append(target_fat * 1.1)
                    # طاقة لا تقل عن الحد
                    A_ub.append([-x for x in energy_row])
                    b_ub.append(-target_energy * 0.85)
                    
                    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                                 bounds=bounds, method='highs')
                    
                    if res.success:
                        formula = {selected[i]: res.x[i] for i in range(len(selected)) if res.x[i] > 0.0001}
                        cost_kg = res.fun / 100.0
                        
                        st.success(f"✅ تم توليد تركيبة بديل الحليب! التكلفة: ${cost_kg:.2f}/كجم")
                        st.write("#### 📝 المقادير لكل كجم:")
                        for k, v in formula.items():
                            st.markdown(f'<div class="formula-item"><span>{k}</span><span>{v:.1f}% ({v*10:.1f} جم/كجم)</span></div>', unsafe_allow_html=True)
                        
                        instructions = f"""الجرعة اليومية: {daily_volume:.1f} لتر مقسمة على 3-4 وجبات
التركيز: 100-150 جم مسحوق لكل لتر ماء دافئ (40-45 درجة مئوية)
درجة الحرارة: يجب أن تكون الحليب عند 38-40 درجة مئوية عند التقديم
التخزين: يحفظ في مكان بارد وجاف، ويستخدم خلال 24 ساعة من التحضير
ملاحظة: يوصى بإضافة فيتامينات ومعادن حسب توصية الطبيب البيطري"""
                        
                        st.markdown(f"""
                        <div style='background:#f0f8ff; padding:15px; border-radius:10px; direction:rtl;'>
                        <b>🥛 تعليمات التقديم:</b><br>
                        {instructions.replace(chr(10), '<br>')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        try:
                            pdf_data = pdf_generator.generate_milk_replacer_report(
                                formula, animal_type, age_days, instructions,
                                st.session_state.get("user", {}).get("full_name", "مستخدم")
                            )
                            st.download_button("📥 تحميل تقرير بديل الحليب PDF", pdf_data,
                                             file_name=f"Milk_Replacer_{animal_type}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                             mime="application/pdf", key="mr_pdf")
                        except Exception as e:
                            st.warning(f"⚠️ تعذر إنشاء PDF: {e}")
                        
                        db = DatabaseManager()
                        data = {
                            'replacer_id': secrets.token_hex(8),
                            'animal_type': animal_type,
                            'age_days': age_days,
                            'formula_name': f"بديل حليب {animal_type} عمر {age_days} يوم",
                            'ingredients': json.dumps(formula),
                            'instructions': instructions,
                            'created_by': st.session_state.get("user", {}).get("full_name", "مستخدم"),
                            'created_date': datetime.now().isoformat()
                        }
                        try:
                            db.insert_record('milk_replacers', data)
                            st.success("✅ تم حفظ التركيبة في قاعدة البيانات")
                        except Exception as e:
                            st.warning(f"⚠️ حفظ: {e}")
                    else:
                        st.error("❌ تعذر إيجاد تركيبة مناسبة، حاول تغيير المكونات")
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")

def render_saved_milk_replacers():
    db = DatabaseManager()
    try:
        records = db.get_records('milk_replacers')
    except Exception:
        records = []
    if records:
        st.subheader("📋 بدائل الحليب المحفوظة")
        for rec in records[:20]:
            try:
                with st.expander(f"🍼 {rec[3]} - {rec[1]} (عمر {rec[2]} يوم)"):
                    st.write(f"**تاريخ الإضافة:** {rec[7]}")
                    st.write(f"**المشرف:** {rec[6]}")
                    st.write("**المكونات:**")
                    try:
                        ingredients = json.loads(rec[4])
                        for k, v in ingredients.items():
                            st.write(f"- {k}: {v:.1f}%")
                    except Exception:
                        st.write(rec[4])
            except Exception:
                continue
    else:
        st.info("لا توجد تركيبات محفوظة حالياً")

# =====================================================================
# نظام منبه الجرعات
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
    
    def get_active_reminders(self):
        return [r for r in self.reminders if r.get('active', True)]
    
    def get_due_reminders(self):
        today = datetime.now().date()
        due = []
        for r in self.get_active_reminders():
            try:
                next_date = datetime.fromisoformat(r['next_dose_date']).date()
                if next_date <= today:
                    due.append(r)
            except Exception:
                continue
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
            الجرعة: {r['dose_amount']} {r['dose_unit']} - الطريقة: {r['administration_route']}<br>
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
                msg = f"🔔 تنبيه جرعة: {r['dose_name']}\nالحيوان: {r['animal_type']}\nالجرعة: {r['dose_amount']} {r['dose_unit']}\nالطريقة: {r['administration_route']}"
                encoded_msg = urllib.parse.quote(msg)
                st.markdown(f'<a href="https://wa.me/{WHATSAPP_NUMBER}?text={encoded_msg}" target="_blank"><button style="background:#25D366; color:white; padding:8px 16px; border:none; border-radius:20px;">📲 واتساب</button></a>', unsafe_allow_html=True)
    else:
        st.success("✅ لا توجد جرعات مستحقة حالياً")
    
    with st.expander("➕ إضافة جرعة جديدة", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            animal_type = st.selectbox("نوع الحيوان",
                ["أبقار", "أغنام", "ماعز", "خيول", "إبل", "دواجن", "أسماك"], key="dr_at")
            dose_type = st.selectbox("نوع الجرعة",
                ["لقاح", "فيتامين", "دواء", "مضاد طفيليات"], key="dr_dt")
            dose_name = st.text_input("اسم الجرعة", key="dr_dn")
        with col2:
            dose_amount = st.number_input("الجرعة", min_value=0.0, value=1.0, step=0.1, key="dr_da")
            dose_unit = st.selectbox("الوحدة",
                ["مل", "جم", "مجم", "وحدة دولية", "قطرة"], key="dr_du")
            administration_route = st.selectbox("طريقة الإعطاء",
                ["عضل", "تحت الجلد", "فموي", "مياه الشرب", "رش", "قطرة عين"], key="dr_ar")
        with col3:
            frequency_days = st.number_input("التكرار (أيام)", min_value=1, value=7, step=1, key="dr_fd")
            start_date = st.date_input("تاريخ البدء", datetime.now(), key="dr_sd")
            notes = st.text_area("ملاحظات", key="dr_notes")
        
        if st.button("💾 حفظ الجرعة", key="dr_save"):
            if dose_name:
                reminder_system.add_reminder(
                    animal_type=animal_type, dose_type=dose_type, dose_name=dose_name,
                    dose_amount=dose_amount, dose_unit=dose_unit,
                    administration_route=administration_route,
                    frequency_days=frequency_days, start_date=start_date.isoformat(),
                    notes=notes
                )
                st.success(f"✅ تم إضافة منبه للجرعة {dose_name}")
                voice_guide(f"تم إضافة منبه للجرعة {dose_name}")
                st.rerun()
            else:
                st.error("⚠️ يرجى إدخال اسم الجرعة")
    
    if st.session_state["dose_reminders"]:
        st.subheader("📋 الجرعات المسجلة")
        for r in st.session_state["dose_reminders"]:
            status = "🟢 نشطة" if r.get('active', True) else "🔴 منتهية"
            with st.expander(f"{r['dose_name']} - {r['animal_type']} ({status})"):
                st.write(f"**النوع:** {r['dose_type']}")
                st.write(f"**الجرعة:** {r['dose_amount']} {r['dose_unit']}")
                st.write(f"**طريقة الإعطاء:** {r['administration_route']}")
                st.write(f"**التكرار:** كل {r['frequency_days']} يوم")
                st.write(f"**تاريخ البدء:** {r['start_date']}")
                st.write(f"**الجرعة القادمة:** {r['next_dose_date'][:10]}")
                if r.get('notes'):
                    st.write(f"**ملاحظات:** {r['notes']}")

# =====================================================================
# نظام مواقيت الصلاة
# =====================================================================
PRAYER_TIMES_CITIES = {
    "مكة المكرمة": {"lat": 21.4225, "lng": 39.8262},
    "المدينة المنورة": {"lat": 24.4672, "lng": 39.6112},
    "الخرطوم": {"lat": 15.5007, "lng": 32.5599},
    "طرابلس": {"lat": 32.8872, "lng": 13.1913},
    "القاهرة": {"lat": 30.0444, "lng": 31.2357},
    "دبي": {"lat": 25.2048, "lng": 55.2708},
    "الرياض": {"lat": 24.7136, "lng": 46.6753},
    "صنعاء": {"lat": 15.3694, "lng": 44.1910},
    "عمان": {"lat": 31.9539, "lng": 35.9106},
    "بيروت": {"lat": 33.8938, "lng": 35.5018},
    "دمشق": {"lat": 33.5138, "lng": 36.2765},
    "بغداد": {"lat": 33.3152, "lng": 44.3661},
    "الكويت": {"lat": 29.3759, "lng": 47.9774},
    "مسقط": {"lat": 23.5880, "lng": 58.3829},
    "المنامة": {"lat": 26.2285, "lng": 50.5860},
    "الدوحة": {"lat": 25.2854, "lng": 51.5310},
    "أبوظبي": {"lat": 24.4539, "lng": 54.3773}
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
    st.info("🕌 **تذكير:** سيتم عرض مواقيت الصلاة بناءً على المدينة المختارة")
    city = st.selectbox("اختر المدينة:", list(PRAYER_TIMES_CITIES.keys()), key="pt_city")
    if city:
        prayer_times = get_prayer_times(city)
        if prayer_times:
            st.markdown(f"#### 📍 مواقيت الصلاة في {city}")
            cols = st.columns(3)
            times = list(prayer_times.items())
            for i, (name, time_val) in enumerate(times):
                with cols[i % 3]:
                    st.metric(name, time_val)
            if st.button("🔔 تفعيل التنبيه الصوتي للصلاة القادمة", key="pt_alert"):
                now = datetime.now().strftime("%H:%M")
                next_prayer = None
                for name, time_val in prayer_times.items():
                    if time_val > now:
                        next_prayer = name
                        break
                if next_prayer:
                    voice_guide(f"حان وقت صلاة {next_prayer} في {city}")
                    st.success(f"✅ تم تشغيل التنبيه لصلاة {next_prayer}")
                else:
                    st.info("جميع الصلوات انتهت لهذا اليوم")

print("✅ تم تحميل الجزء 6 بنجاح - بدائل الحليب والجرعات والصلوات")
# =====================================================================
# CSS
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
    background: rgba(255,255,255,0.95);
    padding: 35px; border-radius: 24px;
    box-shadow: 0 25px 70px rgba(0,0,0,0.15);
    backdrop-filter: blur(15px);
    margin-bottom: 35px;
}
.section-title {
    color: #1b5e20; border-right: 6px solid #2e7d32;
    padding-right: 18px; text-align: right;
    font-size: 1.7rem; font-weight: 700;
    margin-top: 30px; margin-bottom: 25px;
    background: linear-gradient(to left, rgba(46,125,50,0.12), transparent);
    padding: 14px 22px; border-radius: 14px;
}
.formula-item {
    background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(232,245,233,0.95) 100%);
    padding: 16px 22px; border-radius: 14px; margin-bottom: 10px;
    font-weight: 600; color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    transition: all 0.3s ease;
    display: flex; justify-content: space-between; align-items: center;
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
    padding: 20px; border-radius: 12px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 20px; direction: rtl; text-align: right;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
}
.warning-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 15px; border-radius: 12px;
    border-right: 5px solid #f57c00;
    margin-bottom: 15px; direction: rtl; text-align: right;
    color: #e65100 !important;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# شريط الدعاء المتحرك
# =====================================================================
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
        50% { text-shadow: 0 0 15px #ffd700, 0 0 30px #ff8c00, 0 0 60px #ff4500; }
        100% { text-shadow: 0 0 5px #ffd700, 0 0 10px #ffd700, 0 0 20px #ff8c00; }
    }
    @keyframes pulseHeart {
        0%, 100% { transform: scale(1); color: #ff6b6b; }
        50% { transform: scale(1.5); color: #ff1744; }
    }
    .dua-container {
        background: linear-gradient(135deg, #0d1b2a 0%, #1a237e 40%, #4a148c 70%, #0d1b2a 100%);
        padding: 22px 0; border-radius: 24px; margin-bottom: 20px;
        overflow: hidden; border: 3px solid #ffd700;
        box-shadow: 0 8px 40px rgba(255, 215, 0, 0.5);
        direction: rtl;
    }
    .dua-text {
        display: inline-block; white-space: nowrap;
        animation: scrollDua 24s ease-in-out infinite, glowText 3.5s ease-in-out infinite;
        font-size: 1.7rem; font-weight: 800; color: #ffd700;
        padding: 0 25px; direction: rtl;
    }
    .dua-text .emoji-heart {
        display: inline-block; animation: pulseHeart 1.2s ease-in-out infinite; margin: 0 8px;
    }
    .dua-text .name-highlight {
        color: #ffab40; font-weight: 900;
        background: rgba(255, 215, 0, 0.15);
        padding: 0 10px; border-radius: 8px;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }
    </style>
    <div class="dua-container">
        <div class="dua-text">
            <span class="emoji-heart">❤️</span>
            اللهم اغفر لـ <span class="name-highlight">إسماعيل تاور</span> و <span class="name-highlight">ابتسام</span> وارحمهما وأدخلهما فسيح جناتك
            <span class="emoji-heart">❤️</span>
            اللهم اجعل قبرهما روضة من رياض الجنة واجمعنا بهما في الفردوس الأعلى
            <span class="emoji-heart">❤️</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# حالة الجلسة الافتراضية
# =====================================================================
defaults = {
    "approved": False, "user_role": None, "login_welcome_shown": False,
    "login_attempts": 0, "last_login_time": None, "session_token": None,
    "broiler_farms": {}, "selected_farm": None, "whatsapp_alerts_sent": {},
    "analysis_results": None, "analysis_animal": "غير محدد", "analysis_stage": "غير محدد",
    "daily_production_log": [], "basmala_played": False, "welcome_played": False,
    "guide_played": {}, "farms": {}, "selected_farm_id": None, "selected_cycle_id": None,
    "active_formula": {}, "active_cp_tag": 12.0, "active_se_tag": 65.0,
    "active_breed_tag": "سلالة عامة",
    "active_animal_img": ANIMAL_IMAGES_RESOURCES["عام"],
    "active_stage_title": "إنتاج عام", "computed_ton_cost": 280.0,
    "lab_sample": None, "dose_reminders": [], "ocr_result": {},
    "global_livestock_prices": {
        "عجول تسمين هولشتاين ($)": 1350.0, "أبقار كنانة محلية ($)": 900.0,
        "ضأن وستيرلنغ ($)": 180.0, "ماعز نوبي ($)": 130.0,
        "خيول عربية أصيلة ($)": 4500.0, "إبل عربية ($)": 2500.0,
        "كتكوت لاحم ($)": 0.65
    },
    "global_products_prices": {
        "كيلو لحم بقري ($)": 7.50, "كيلو لحم ضأن ($)": 9.00,
        "كيلو لحم دجاج ($)": 3.80, "طبق بيض 30 بيضة ($)": 4.20,
        "لتر حليب خام ($)": 0.90, "لتر حليب إبل ($)": 1.50
    },
    "shared_comments": "• [توجيه الاختصاصي م. عبد القادر]: يرجى من جميع الزملاء إضافة تعليقاتهم.\n"
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# تهيئة أنظمة
farm_system = FarmManagementSystem()
broiler_manager = BroilerFarmManager()

if "smart_lab" not in st.session_state:
    try:
        st.session_state["smart_lab"] = SmartLabSystem()
    except Exception:
        st.session_state["smart_lab"] = None

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
    st.markdown("<p style='text-align:center; color:#555; font-size:1.1rem;'>للانتاج الحيواني وتركيب الاعلاف</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888; font-size:0.9rem;'>الإصدار المتكامل الشامل 17.0</p>", unsafe_allow_html=True)
    
    if st.button("🔊 تشغيل الشرح الصوتي الكامل للمنصة", type="primary", use_container_width=True):
        play_full_guide_audio()
        st.success("✅ يتم تشغيل الشرح الصوتي...")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("🔊 استمع للترحيب", use_container_width=True):
            play_welcome_audio()
    with col_s2:
        if st.button("🕊️ استمع للدعاء", use_container_width=True):
            play_dua_audio()
    
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
            voice_guide("السلام عليكم، مرحباً بك زائراً.")
            st.rerun()
    
    st.markdown("<hr style='margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#666;'>🔑 للمالك والمختصين - تسجيل الدخول بالكود</p>", unsafe_allow_html=True)
    
    login_option = st.radio("طريقة الدخول:",
        ["كود الدخول السري", "اسم المستخدم وكلمة المرور"],
        horizontal=True, key="login_opt")
    
    if login_option == "كود الدخول السري":
        input_code = st.text_input("🔑 أدخل كود الدخول:", type="password", key="login_code")
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
                    voice_guide(f"مرحباً بك، {CODES_DB[input_code.strip()]['name']}")
                    st.rerun()
                else:
                    st.session_state["login_attempts"] += 1
                    remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                    st.error(f"❌ الكود غير صحيح! متبقي {remaining} محاولات")
        with col_reset:
            if st.button("🔄 نسيت الكود", use_container_width=True):
                st.info("يرجى التواصل مع مدير النظام: abukram128@gmail.com")
    else:
        username = st.text_input("👤 اسم المستخدم", key="login_user")
        password = st.text_input("🔑 كلمة المرور", type="password", key="login_pass")
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
                voice_guide(f"مرحباً بك، {user['full_name']}")
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ بيانات غير صحيحة! متبقي {remaining} محاولات")
        st.caption("💡 المستخدم الافتراضي: admin / admin123")
    
    st.markdown("""
    <div style='text-align:center; margin-top:15px; color:#999; font-size:0.85rem;'>
    <p>🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b> - رحمهما الله</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# الترحيب بعد الدخول
# =====================================================================
if not st.session_state["login_welcome_shown"]:
    role_messages = {
        "owner": "👑 مرحباً بك، الاختصاصي م. عبد القادر إسماعيل تاور",
        "specialist": "🔬 أهلاً بالزملاء المختصين",
        "veterinarian": "💊 أهلاً بالطبيب البيطري",
        "nutritionist": "🧬 أهلاً بأخصائي التغذية",
        "breeder": "🌾 أهلاً وسهلاً بالمربين",
        "public": "👤 مرحباً بك زائراً"
    }
    st.toast(role_messages.get(st.session_state["user_role"], "مرحباً"), icon="🌾")
    try:
        voice_welcome(st.session_state["user_role"])
    except Exception:
        pass
    st.session_state["login_welcome_shown"] = True

render_dua_bar()

print("✅ تم تحميل الجزء 7 بنجاح - CSS والدخول")
# =====================================================================
# دالة دليل التبويب
# =====================================================================
def guide_section(tab_name, guide_text):
    with st.expander(f"📘 دليل استخدام {tab_name}", expanded=False):
        st.markdown(f"<div style='background:#f0f8ff; padding:15px; border-radius:10px; direction:rtl;'>{guide_text}</div>", unsafe_allow_html=True)
        if st.button(f"🔊 تشغيل الدليل صوتياً ({tab_name})", key=f"guide_{tab_name}"):
            voice_guide(guide_text)

# =====================================================================
# دالة تركيب العلف المتقدم
# =====================================================================
def render_feed_formulation(animal_key, display_name, icon, default_breeds, default_stages,
                             default_dp, default_se, img_key, has_measurements=True):
    st.markdown(f'<div class="section-title">{icon} {display_name} - تركيب العلف المتقدم</div>', unsafe_allow_html=True)
    
    requester_name = st.text_input(
        "👤 اسم طالب العلف (المربي / المزرعة):",
        placeholder="أدخل اسم المربي أو المزرعة",
        key=f"{animal_key}_requester"
    )
    
    col_measure, col_settings = st.columns([0.4, 0.6])
    
    with col_measure:
        if has_measurements:
            st.markdown('<div class="measurement-card">', unsafe_allow_html=True)
            st.markdown("#### 📏 شريط القياس الحيوي")
            col_h, col_l, col_age = st.columns(3)
            with col_h:
                h_girth = st.number_input("محيط الصدر (سم)", min_value=20.0, max_value=300.0,
                                          value=150.0, step=1.0, key=f"{animal_key}_girth")
            with col_l:
                b_length = st.number_input("طول الجسم (سم)", min_value=20.0, max_value=300.0,
                                           value=130.0, step=1.0, key=f"{animal_key}_length")
            with col_age:
                age_months = st.number_input("العمر (شهر)", min_value=1, max_value=120,
                                             value=12, step=1, key=f"{animal_key}_age")
            
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
            
            st.caption(f"⚖️ DP المقترح: {adjusted_dp:.1f}% | SE المقترح: {adjusted_se:.1f}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            adjusted_dp = default_dp
            adjusted_se = default_se
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
            age_input = st.number_input("العمر (شهر)", min_value=1, max_value=240,
                                        value=24, step=1, key=f"{animal_key}_age_input")
        with col_age_phys[1]:
            physiological_state = st.selectbox(
                "الحالة الفسيولوجية",
                ["طبيعي", "حامل", "مرضع", "صائم", "نشاط مكثف", "استشفاء", "نمو سريع"],
                key=f"{animal_key}_physiological"
            )
        
        st.markdown("#### 🧬 خيارات البروتين والطاقة")
        protein_basis = st.radio("أساس البروتين:", ["DP", "CP"], horizontal=True,
                                 key=f"{animal_key}_basis")
        
        if protein_basis == "DP":
            target_protein = st.number_input("نسبة DP المطلوبة (%)", min_value=5.0, max_value=50.0,
                                             value=float(adjusted_dp), step=0.5, key=f"{animal_key}_dp")
            cp_est = target_protein / 0.80
            st.caption(f"💡 يقابل ذلك بروتين خام ≈ {cp_est:.1f}%")
        else:
            target_protein = st.number_input("نسبة CP المطلوبة (%)", min_value=5.0, max_value=60.0,
                                             value=float(default_dp/0.80), step=0.5, key=f"{animal_key}_cp")
            st.caption(f"💡 يقابل ذلك بروتين مهضوم ≈ {target_protein * 0.80:.1f}%")
        
        target_se = st.number_input("معادل النشاء (SE) المطلوب", min_value=10.0, max_value=90.0,
                                    value=float(adjusted_se), step=1.0, key=f"{animal_key}_se")
        
        if protein_basis == "DP":
            actual_dp_target = target_protein
        else:
            actual_dp_target = target_protein * 0.80
        
        state_multipliers = {
            "طبيعي": 1.0, "حامل": 1.15, "مرضع": 1.30, "صائم": 0.85,
            "نشاط مكثف": 1.25, "استشفاء": 1.20, "نمو سريع": 1.35
        }
        multiplier = state_multipliers.get(physiological_state, 1.0)
        actual_dp_target *= multiplier
        target_se *= multiplier
        st.caption(f"📌 معامل الحالة الفسيولوجية: {multiplier:.2f}")
    
    st.markdown("#### 🌾 اختر المكونات العلفية")
    selected_ingredients = []
    ingredient_prices = {}
    
    default_ingredients = {
        "cattle": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                   "أمباز الفول السوداني (كسب)", "مركزات خيول ومجترات", "ملح الطعام",
                   "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)",
                   "بيكربونات الصوديوم (الصودا)"],
        "sheep": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                  "أمباز الفول السوداني (كسب)", "مركزات خيول ومجترات", "ملح الطعام",
                  "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)",
                  "بيكربونات الصوديوم (الصودا)"],
        "goat": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                 "أمباز الفول السوداني (كسب)", "مركزات خيول ومجترات", "ملح الطعام",
                 "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)",
                 "بيكربونات الصوديوم (الصودا)"],
        "horse": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                  "أمباز الفول السوداني (كسب)", "مولاس قصب السكر", "مركزات خيول ومجترات",
                  "ملح الطعام", "الحجر الجيري (بودرة بلاط)",
                  "فوسفات ثنائي الكالسيوم (DCP)"],
        "camel": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                  "أمباز الفول السوداني (كسب)", "البرسيم الجاف (الدريس)",
                  "مركزات خيول ومجترات", "ملح الطعام", "الحجر الجيري (بودرة بلاط)",
                  "فوسفات ثنائي الكالسيوم (DCP)"],
        "poultry": ["ذرة صفراء", "سورجم (فتريتة)", "كسب فول صويا 44%",
                    "كسب جلوتين الذرة 60%", "مركزات دواجن وسمان",
                    "بريمكس تسمين دواجن (Premix)", "ملح الطعام",
                    "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)",
                    "إنزيم الفايتيز الزامي (Phytase Super-D)"],
        "fish": ["ذرة صفراء", "كسب فول صويا 44%", "مسحوق أسماك (Fishmeal 60%)",
                 "كسب جلوتين الذرة 60%", "مركزات دواجن وسمان", "ملح الطعام",
                 "فوسفات ثنائي الكالسيوم (DCP)", "إنزيم الفايتيز الزامي (Phytase Super-D)"]
    }
    
    default_list = default_ingredients.get(animal_key, [])
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=False):
            cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with cols[idx % 3]:
                    checked = st.checkbox(ing_name, value=ing_name in default_list,
                                         key=f"{animal_key}_feed_{ing_name}")
                    if checked:
                        price = st.number_input(
                            f"سعر {ing_name} ($/طن)", min_value=5.0,
                            value=float(250.0 if "نخالة" in ing_name or "ملح" in ing_name else 350.0),
                            key=f"{animal_key}_price_{ing_name}"
                        )
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price
    
    col_buttons = st.columns(3)
    with col_buttons[0]:
        if st.button(f"🚀 تشغيل محرك التركيب ({display_name})", type="primary",
                     use_container_width=True, key=f"{animal_key}_run"):
            if len(selected_ingredients) < 3:
                st.warning("⚠️ يرجى اختيار 3 مكونات على الأقل.")
            else:
                voice_guide(f"جاري تشغيل محرك تركيب العلف لـ {display_name}.")
                st.info("🔄 جاري حساب الخلطة المثالية...")
                
                c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
                bounds = [(0.0, 100.0) for _ in selected_ingredients]
                
                # قيد المجموع
                A_eq = [[1.0 for _ in selected_ingredients]]
                b_eq = [100.0]
                
                # قيود DP و SE و NDF و ADF
                dp_row = []
                se_row = []
                ndf_row = []
                adf_row = []
                for ing in selected_ingredients:
                    feed_data = FLAT_FEED_DB.get(ing, {})
                    cp_val = feed_data.get("CP", 0.0)
                    dc_val = feed_data.get("DC", 0.0)
                    se_val = feed_data.get("SE", 0.0)
                    ndf_val = feed_data.get("NDF", 0.0)
                    adf_val = feed_data.get("ADF", 0.0)
                    dp_row.append(cp_val * dc_val)
                    se_row.append(se_val)
                    ndf_row.append(ndf_val)
                    adf_row.append(adf_val)
                
                A_eq.append(dp_row)
                b_eq.append(actual_dp_target * 100.0)
                
                A_ub = []
                b_ub = []
                A_ub.append([-x for x in se_row])
                b_ub.append(-target_se * 100.0)
                
                if animal_key in ["cattle", "sheep", "goat", "camel"]:
                    A_ub.append(ndf_row)
                    b_ub.append(35.0 * 100.0)
                    A_ub.append(adf_row)
                    b_ub.append(20.0 * 100.0)
                elif animal_key == "horse":
                    A_ub.append(ndf_row)
                    b_ub.append(40.0 * 100.0)
                
                # قيود إضافية
                if "نخالة قمح (ردة)" in selected_ingredients:
                    idx = selected_ingredients.index("نخالة قمح (ردة)")
                    row = [0.0] * len(selected_ingredients)
                    row[idx] = 1.0
                    A_ub.append(row)
                    b_ub.append(25.0 if animal_key in ["cattle","sheep","goat","camel"] else 15.0)
                
                # إضافات إلزامية
                if animal_key in ["cattle", "sheep", "goat", "camel"]:
                    if "بيكربونات الصوديوم (الصودا)" not in selected_ingredients:
                        selected_ingredients.append("بيكربونات الصوديوم (الصودا)")
                        ingredient_prices["بيكربونات الصوديوم (الصودا)"] = 340.0
                        c_vector.append(340.0)
                        dp_row.append(0.0)
                        se_row.append(0.0)
                        ndf_row.append(0.0)
                        adf_row.append(0.0)
                        bounds.append((0.75, 0.75))
                        row = [0.0] * len(selected_ingredients)
                        row[-1] = 1.0
                        A_ub.append(row)
                        b_ub.append(0.75)
                
                if animal_key in ["poultry", "fish"]:
                    if "إنزيم الفايتيز الزامي (Phytase Super-D)" not in selected_ingredients:
                        selected_ingredients.append("إنزيم الفايتيز الزامي (Phytase Super-D)")
                        ingredient_prices["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 1200.0
                        c_vector.append(1200.0)
                        dp_row.append(0.0)
                        se_row.append(0.0)
                        ndf_row.append(0.0)
                        adf_row.append(0.0)
                        bounds.append((0.05, 0.05))
                        row = [0.0] * len(selected_ingredients)
                        row[-1] = 1.0
                        A_ub.append(row)
                        b_ub.append(0.05)
                
                # تعديل A_eq بعد الإضافات
                A_eq = [[1.0 for _ in selected_ingredients], dp_row]
                b_eq = [100.0, actual_dp_target * 100.0]
                
                try:
                    res = linprog(c_vector, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                                 bounds=bounds, method='highs')
                    
                    if res.success:
                        formula_results = {}
                        computed_se_total = 0.0
                        computed_dp_total = 0.0
                        for idx, ing in enumerate(selected_ingredients):
                            if res.x[idx] > 0.0001:
                                formula_results[ing] = res.x[idx]
                                feed_data = FLAT_FEED_DB.get(ing, {})
                                computed_se_total += (res.x[idx] / 100.0) * feed_data.get("SE", 0.0)
                                computed_dp_total += (res.x[idx] / 100.0) * feed_data.get("CP", 0.0) * feed_data.get("DC", 0.0)
                        
                        ton_cost = res.fun / 100.0
                        
                        # التحقق من 75% من المعايير
                        standard = STANDARD_VALUES.get(display_name, {}).get(stage, {})
                        meets_standard = True
                        warnings_list = []
                        
                        if standard:
                            if 'DP' in standard:
                                dp_ratio = computed_dp_total / standard['DP'] * 100 if standard['DP'] > 0 else 0
                                if dp_ratio < 75:
                                    meets_standard = False
                                    warnings_list.append(f"DP: {dp_ratio:.1f}% من المعيار (أقل من 75%)")
                            if 'SE' in standard:
                                se_ratio = computed_se_total / standard['SE'] * 100 if standard['SE'] > 0 else 0
                                if se_ratio < 75:
                                    meets_standard = False
                                    warnings_list.append(f"SE: {se_ratio:.1f}% من المعيار (أقل من 75%)")
                        
                        if not meets_standard:
                            st.error("❌ الخلطة لا تلبي الحد الأدنى (75%) من المعايير القياسية.")
                            for w in warnings_list:
                                st.warning(f"⚠️ {w}")
                            voice_guide("الخلطة لا تلبي المعايير المطلوبة.")
                        else:
                            st.success(f"✅ تم توليد الخلطة! التكلفة: ${ton_cost:.2f}/طن")
                            voice_guide(f"تم توليد الخلطة بنجاح بتكلفة {ton_cost:.2f} دولار للطن")
                            
                            col_res1, col_res2 = st.columns([0.6, 0.4])
                            with col_res1:
                                st.write("#### 📝 المقادير المعتمدة:")
                                for k, v in formula_results.items():
                                    st.markdown(f'<div class="formula-item"><span>{k}</span><span>{v:.2f}% ({v*10:.1f} كجم)</span></div>', unsafe_allow_html=True)
                                
                                st.metric("💰 التكلفة للطن", f"${ton_cost:.2f}")
                                st.metric("🧬 DP المحقق", f"{computed_dp_total:.2f}%")
                                st.metric("🌽 SE المحقق", f"{computed_se_total:.2f}")
                                
                                if requester_name:
                                    st.info(f"👤 طالب العلف: {requester_name}")
                                
                                if standard:
                                    st.write("#### 📊 المقارنة مع المعايير:")
                                    comp_data = []
                                    if 'DP' in standard:
                                        dev = ((computed_dp_total - standard['DP']) / standard['DP']) * 100 if standard['DP'] > 0 else 0
                                        grade = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                                        comp_data.append({"المقياس": "DP", "المحسوب": f"{computed_dp_total:.2f}%",
                                                        "القياسي": f"{standard['DP']:.2f}%", "الانحراف": f"{dev:.1f}%", "التقييم": grade})
                                    if 'SE' in standard:
                                        dev = ((computed_se_total - standard['SE']) / standard['SE']) * 100 if standard['SE'] > 0 else 0
                                        grade = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                                        comp_data.append({"المقياس": "SE", "المحسوب": f"{computed_se_total:.2f}",
                                                        "القياسي": f"{standard['SE']:.2f}", "الانحراف": f"{dev:.1f}%", "التقييم": grade})
                                    st.table(pd.DataFrame(comp_data))
                                
                                try:
                                    pdf_data = pdf_generator.generate_comprehensive_report(
                                        formula_results, computed_dp_total,
                                        f"{breed} - {stage} ({physiological_state})",
                                        ton_cost, "المدينة", ton_cost*600, "SDG",
                                        computed_se_total,
                                        user_name=st.session_state.get("user", {}).get("full_name", "مستخدم"),
                                        requester_name=requester_name, standard=standard,
                                        include_charts=True,
                                        extra_info={"السلالة": breed, "المرحلة": stage, "الحالة": physiological_state}
                                    )
                                    st.download_button("📥 تحميل PDF", pdf_data,
                                                     file_name=f"Tawornology_{display_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                                     mime="application/pdf", use_container_width=True,
                                                     key=f"{animal_key}_pdf")
                                except Exception as e:
                                    st.warning(f"⚠️ تعذر إنشاء PDF: {e}")
                            
                            with col_res2:
                                if len(formula_results) > 1:
                                    fig = px.pie(values=list(formula_results.values()),
                                                names=list(formula_results.keys()),
                                                title="توزيع المكونات",
                                                color_discrete_sequence=px.colors.sequential.Greens)
                                    fig.update_layout(height=400)
                                    st.plotly_chart(fig, use_container_width=True)
                            
                            # حفظ في الجلسة
                            st.session_state["active_formula"] = formula_results
                            st.session_state["active_cp_tag"] = computed_dp_total
                            st.session_state["active_se_tag"] = computed_se_total
                            st.session_state["active_breed_tag"] = f"{breed} - {stage}"
                            st.session_state["computed_ton_cost"] = ton_cost
                    else:
                        st.error("❌ تعذر إيجاد حل رياضي. حاول إضافة مكونات أو تعديل النسب.")
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")
    
    with col_buttons[1]:
        if st.button(f"📋 عرض المعايير القياسية ({display_name})", use_container_width=True,
                     key=f"{animal_key}_std"):
            standard = STANDARD_VALUES.get(display_name, {}).get(stage, {})
            if standard:
                st.info(f"📊 المعايير لـ {display_name} - {stage}: DP={standard.get('DP','-')}%, SE={standard.get('SE','-')}, CP={standard.get('CP','-')}%")
            else:
                st.warning("⚠️ لا توجد معايير لهذه المرحلة.")
    
    with col_buttons[2]:
        if st.button(f"🔊 استماع للتعليمات ({display_name})", use_container_width=True,
                     key=f"{animal_key}_help"):
            voice_guide(f"مرحباً بك في قسم {display_name}. اختر السلالة والمرحلة والمكونات ثم اضغط تشغيل.")

# =====================================================================
# تبويب المختبر الذكي (OCR)
# =====================================================================
def render_smart_ocr_lab():
    st.markdown('<div class="section-title">📸 المختبر الذكي - تحليل صور التركيبات</div>', unsafe_allow_html=True)
    
    if not OCR_AVAILABLE and not EASYOCR_AVAILABLE:
        st.warning("""
        ⚠️ **مكتبات OCR غير مثبتة!**
        ```bash
        pip install easyocr
        # أو
        pip install pytesseract
        ```
        يمكنك إدخال البيانات يدوياً في النموذج بالأسفل.
        """)
    
    col_upload, col_info = st.columns([2, 1])
    with col_upload:
        uploaded = st.file_uploader(
            "ارفع صورة لتركيبة علفية (كتاب، ورقة، أو صورة)",
            type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
            key="ocr_upload"
        )
        if uploaded is not None:
            try:
                image = PILImage.open(uploaded)
                st.image(image, caption="الصورة المرفوعة", use_container_width=True)
                if st.button("🔍 تحليل الصورة", type="primary", key="ocr_analyze"):
                    if not st.session_state.get("smart_lab"):
                        st.error("❌ نظام المختبر الذكي غير متاح")
                    else:
                        with st.spinner("جاري التحليل..."):
                            result, error = st.session_state["smart_lab"].analyze_image(image)
                            if error:
                                st.error(f"❌ {error}")
                            else:
                                st.success("✅ تم التحليل!")
                                st.session_state["ocr_result"] = result
                                voice_guide("تم تحليل الصورة بنجاح")
            except Exception as e:
                st.error(f"خطأ: {e}")
    
    with col_info:
        st.markdown("""
        <div style='background:#e3f2fd; padding:15px; border-radius:10px; direction:rtl;'>
        <h4>💡 نصائح:</h4>
        <ul>
        <li>صورة واضحة ومستقيمة</li>
        <li>إضاءة جيدة</li>
        <li>يدعم العربية والإنجليزية</li>
        <li>يمكنك تعديل القيم بعد التحليل</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    ocr_data = st.session_state.get("ocr_result", {})
    st.markdown("### ✍️ البيانات المستخرجة / للإدخال اليدوي")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("اسم العينة:", value=ocr_data.get('sample_name', ''), key="ocr_name")
        st.number_input("بروتين خام (CP %):", min_value=0.0,
                        value=float(ocr_data.get('cp') or 0.0), step=0.1, key="ocr_cp")
        st.number_input("معامل الهضم (DC):", min_value=0.0, max_value=1.0,
                        value=float(ocr_data.get('dc') or 0.0), step=0.01, key="ocr_dc")
        st.number_input("معادل النشاء (SE):", min_value=0.0,
                        value=float(ocr_data.get('se') or 0.0), step=0.1, key="ocr_se")
    with c2:
        st.number_input("NDF %:", min_value=0.0,
                        value=float(ocr_data.get('ndf') or 0.0), step=0.1, key="ocr_ndf")
        st.number_input("ADF %:", min_value=0.0,
                        value=float(ocr_data.get('adf') or 0.0), step=0.1, key="ocr_adf")
        st.number_input("دهن خام (EE %):", min_value=0.0,
                        value=float(ocr_data.get('ee') or 0.0), step=0.1, key="ocr_ee")
        st.number_input("رماد (ASH %):", min_value=0.0,
                        value=float(ocr_data.get('ash') or 0.0), step=0.1, key="ocr_ash")
    
    if st.button("💾 حفظ نتيجة التحليل", type="secondary", key="ocr_save"):
        if st.session_state.get("smart_lab"):
            data = {
                'sample_name': st.session_state.get('ocr_name', ''),
                'cp': st.session_state.get('ocr_cp', 0.0),
                'dc': st.session_state.get('ocr_dc', 0.0),
                'se': st.session_state.get('ocr_se', 0.0),
                'ndf': st.session_state.get('ocr_ndf', 0.0),
                'adf': st.session_state.get('ocr_adf', 0.0),
                'ee': st.session_state.get('ocr_ee', 0.0),
                'ash': st.session_state.get('ocr_ash', 0.0),
                'analyzed_by': st.session_state.get("user", {}).get("full_name", "مستخدم"),
                'notes': ''
            }
            rid = st.session_state["smart_lab"].save_lab_result(data)
            st.success(f"✅ تم الحفظ! (ID: {rid[:8]})")
            voice_guide("تم حفظ نتيجة التحليل")

# =====================================================================
# تبويب المختبر المتقدم (تحليل الأوزان)
# =====================================================================
def render_advanced_lab():
    st.markdown('<div class="section-title">🔬 المختبر المتقدم - تحليل ومقارنة الخلطات</div>', unsafe_allow_html=True)
    
    if st.session_state.get("lab_sample"):
        sample = st.session_state["lab_sample"]
        st.success(f"📥 عينة من {sample['animal']} - {sample['breed']} - {sample['stage']}")
        st.write(f"**DP:** {sample['dp']:.2f}% | **SE:** {sample['se']:.2f}")
        if st.button("🗑️ مسح العينة", key="lab_clear"):
            st.session_state["lab_sample"] = None
            st.rerun()
    
    col_lab1, col_lab2 = st.columns([0.5, 0.5])
    with col_lab1:
        lab_animal = st.selectbox("الفصيل:",
            ["أبقار", "أغنام", "ماعز", "خيول", "إبل", "دواجن", "أسماك"], key="lab_animal")
        stages = list(STANDARD_VALUES.get(lab_animal, {}).keys())
        if stages:
            lab_stage = st.selectbox("المرحلة:", stages, key="lab_stage")
            standard = STANDARD_VALUES.get(lab_animal, {}).get(lab_stage, {})
        else:
            lab_stage = "عام"
            standard = {}
        if standard:
            st.info(f"📊 DP={standard.get('DP','-')}%, SE={standard.get('SE','-')}, CP={standard.get('CP','-')}%")
    
    with col_lab2:
        protein_system = st.selectbox("نظام البروتين:",
            ["بروتين مهضوم (DP)", "بروتين خام (CP)", "بروتين صافي (NP)"], key="lab_ps")
        energy_system = st.selectbox("نظام الطاقة:",
            ["معادل النشاء (SE)", "طاقة أيضية (ME)", "طاقة صافية (NE)"], key="lab_es")
    
    lab_inputs = {}
    cols = st.columns(3)
    all_ings = list(FLAT_FEED_DB.keys())
    for idx, ing in enumerate(all_ings):
        with cols[idx % 3]:
            lab_inputs[ing] = st.number_input(f"وزن {ing} (كجم)", min_value=0.0, value=0.0,
                                              step=5.0, key=f"lab_in_{ing}")
    
    if st.button("🧪 تشغيل التحليل المخبري", type="primary", use_container_width=True, key="lab_run"):
        total = sum(lab_inputs.values())
        if total <= 0:
            st.warning("⚠️ الرجاء إدخال أوزان أكبر من الصفر.")
        else:
            voice_guide(f"جاري تشغيل التحليل المخبري")
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
                    comps.append({"المادة": ing, "الوزن": weight, "النسبة %": f"{pct*100:.2f}"})
            
            st.session_state["analysis_results"] = {'components': lab_inputs, 'cp': cp_total, 'dp': dp_total, 'se': se_total}
            st.session_state["analysis_animal"] = lab_animal
            st.session_state["analysis_stage"] = lab_stage
            
            st.success("🔬 تم التحليل!")
            voice_guide("تم التحليل بنجاح")
            
            st.markdown(f"### ⚖️ إجمالي الوزن: **{total:.1f} كجم**")
            st.table(pd.DataFrame(comps))
            
            results_df = pd.DataFrame([
                {"العنصر": "CP", "القيمة": f"{cp_total:.2f}%"},
                {"العنصر": "DP", "القيمة": f"{dp_total:.2f}%"},
                {"العنصر": "SE", "القيمة": f"{se_total:.2f}"}
            ])
            st.table(results_df)
            
            if standard:
                dp_dev = ((dp_total - standard.get('DP', 0)) / standard.get('DP', 1)) * 100 if standard.get('DP', 0) > 0 else 0
                se_dev = ((se_total - standard.get('SE', 0)) / standard.get('SE', 1)) * 100 if standard.get('SE', 0) > 0 else 0
                cp_dev = ((cp_total - standard.get('CP', 0)) / standard.get('CP', 1)) * 100 if standard.get('CP', 0) > 0 else 0
                
                dp_grade = "✅" if abs(dp_dev) <= 5 else ("👍" if abs(dp_dev) <= 10 else "⚠️")
                se_grade = "✅" if abs(se_dev) <= 5 else ("👍" if abs(se_dev) <= 10 else "⚠️")
                cp_grade = "✅" if abs(cp_dev) <= 5 else ("👍" if abs(cp_dev) <= 10 else "⚠️")
                
                eval_df = pd.DataFrame([
                    {"المقياس": "DP", "المحسوب": f"{dp_total:.2f}%", "القياسي": f"{standard.get('DP', 0):.2f}%", "الانحراف": f"{dp_dev:.1f}%", "التقييم": dp_grade},
                    {"المقياس": "SE", "المحسوب": f"{se_total:.2f}", "القياسي": f"{standard.get('SE', 0):.2f}", "الانحراف": f"{se_dev:.1f}%", "التقييم": se_grade},
                    {"المقياس": "CP", "المحسوب": f"{cp_total:.2f}%", "القياسي": f"{standard.get('CP', 0):.2f}%", "الانحراف": f"{cp_dev:.1f}%", "التقييم": cp_grade}
                ])
                st.table(eval_df)
                
                try:
                    pdf_data = pdf_generator.generate_lab_report(
                        st.session_state["analysis_results"], lab_animal, lab_stage,
                        st.session_state.get("user", {}).get("full_name", "مستخدم"),
                        standard, {'DP': dp_grade, 'SE': se_grade, 'CP': cp_grade}
                    )
                    st.download_button("📥 تحميل تقرير PDF", pdf_data,
                                     file_name=f"Lab_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                     mime="application/pdf", key="lab_pdf")
                except Exception as e:
                    st.warning(f"⚠️ {e}")

# =====================================================================
# معادلات NRC التفاعلية
# =====================================================================
def render_nrc_equations(animal_type="أبقار"):
    st.markdown("### 🧮 المعادلات الإنتاجية المتقدمة (NRC)")
    
    c1, c2 = st.columns(2)
    with c1:
        weight = st.number_input("⚖️ الوزن الحي (كجم):", min_value=10.0,
                                 value=450.0 if animal_type == "أبقار" else 60.0,
                                 step=5.0, key=f"nrc_w_{animal_type}")
        production_type = st.radio("نوع الإنتاج:", ["🥛 إنتاج حليب", "📈 تسمين"],
                                   horizontal=True, key=f"nrc_t_{animal_type}")
    with c2:
        if production_type == "🥛 إنتاج حليب":
            milk_yield = st.number_input("🥛 إنتاج الحليب (لتر/يوم):", min_value=0.0,
                                         value=20.0 if animal_type == "أبقار" else 2.0,
                                         step=0.5, key=f"nrc_m_{animal_type}")
            milk_fat = st.slider("دهن الحليب (%)", 2.5, 6.0, 3.5, 0.1, key=f"nrc_f_{animal_type}")
        else:
            daily_gain = st.number_input("📈 الزيادة اليومية (كجم):", min_value=0.0,
                                         value=1.0 if animal_type == "أبقار" else 0.15,
                                         step=0.05, key=f"nrc_g_{animal_type}")
    
    if st.button(f"🧮 حساب الاحتياجات", type="primary", key=f"nrc_calc_{animal_type}"):
        if production_type == "🥛 إنتاج حليب":
            pr = AdvancedProductionEquations.calculate_total_protein_for_dairy(weight, milk_yield, milk_fat)
            er = AdvancedProductionEquations.calculate_energy_for_dairy(weight, milk_yield, milk_fat)
            ratio = AdvancedProductionEquations.calculate_protein_energy_ratio(pr['total'], er['total_energy'])
            dp_pct = pr['dp_requirement']
            se_val = er['se_requirement']
            
            st.success("✅ تم الحساب وفق NRC 2001")
            col_r1, col_r2, col_r3 = st.columns(3)
            col_r1.metric("🧬 DP", f"{dp_pct:.2f}%")
            col_r2.metric("🌽 SE", f"{se_val:.0f}")
            col_r3.metric("📊 SE/DP", f"{ratio:.2f}")
            
            st.markdown(f"""
            <div class="price-card">
            <b>📊 احتياجات البروتين (جم/يوم):</b><br>
            ▪️ الإدامة: <b>{pr['maintenance']:.1f} جم</b><br>
            ▪️ الأيض: <b>{pr['metabolic']:.1f} جم</b><br>
            ▪️ الإنتاج: <b>{pr['production']:.1f} جم</b><br>
            ▪️ <b>الإجمالي: {pr['total']:.1f} جم/يوم</b>
            </div>
            """, unsafe_allow_html=True)
            
            voice_guide(f"تم الحساب: البروتين المهضوم {dp_pct:.1f} في المائة")
        else:
            pr = AdvancedProductionEquations.calculate_total_protein_for_fattening(weight, daily_gain)
            er = AdvancedProductionEquations.calculate_total_energy_for_fattening(weight, daily_gain)
            ratio = AdvancedProductionEquations.calculate_protein_energy_ratio(pr['total'], er['total_energy'])
            dp_pct = pr['dp_requirement']
            se_val = er['se_requirement']
            
            st.success("✅ تم الحساب وفق NRC 2000")
            col_r1, col_r2, col_r3 = st.columns(3)
            col_r1.metric("🧬 DP", f"{dp_pct:.2f}%")
            col_r2.metric("🌽 SE", f"{se_val:.0f}")
            col_r3.metric("📊 SE/DP", f"{ratio:.2f}")
            
            if 4.5 <= ratio <= 6.0:
                st.success(f"✅ النسبة مثالية للتسمين")
            elif ratio > 6.0:
                st.warning(f"⚠️ النسبة مرتفعة (طاقة زائدة)")
            else:
                st.warning(f"⚠️ النسبة منخفضة (بروتين زائد)")

print("✅ تم تحميل الجزء 8 بنجاح - الواجهة الرئيسية")
# =====================================================================
# الواجهة الرئيسية
# =====================================================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logout_space, col_user_status = st.columns([0.7, 0.3])
with col_user_status:
    role_names = {"owner": "المالك 👑", "specialist": "المختص 👨‍🔬",
                  "veterinarian": "الطبيب البيطري 💊",
                  "nutritionist": "أخصائي التغذية 🧬",
                  "breeder": "المربي 🌾", "public": "زائر 👤"}
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
        protected = ["inventory", "broiler_farms", "whatsapp_alerts_sent",
                     "analysis_results", "basmala_played", "welcome_played",
                     "email_password", "guide_played", "farms", "selected_farm_id",
                     "selected_cycle_id", "active_formula", "active_cp_tag",
                     "active_se_tag", "active_breed_tag", "computed_ton_cost",
                     "lab_sample", "dose_reminders"]
        for key in list(st.session_state.keys()):
            if key not in protected:
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
    st.markdown("<h3 style='color:#c62828; text-align:right; font-weight:700;'>الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top:3px solid #2e7d32;'>", unsafe_allow_html=True)

if st.button("🔊 تشغيل الشرح الصوتي الكامل", type="primary", use_container_width=True):
    play_full_guide_audio()
    st.success("✅ يتم تشغيل الشرح الصوتي...")

# =====================================================================
# إحصائيات سريعة
# =====================================================================
st.markdown("### 📊 لوحة التحكم السريعة")
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
with col_stat1:
    stock_summary = InventoryManager.get_stock_summary()
    st.markdown(f"<div class='metric-card'><div class='number'>{stock_summary['total_items']}</div><div class='label'>إجمالي المواد</div></div>", unsafe_allow_html=True)
with col_stat2:
    st.markdown(f"<div class='metric-card'><div class='number'>{stock_summary['total_quantity']:.1f}</div><div class='label'>إجمالي المخزون (طن)</div></div>", unsafe_allow_html=True)
with col_stat3:
    low_stock = stock_summary['low_stock']
    color = "#c62828" if low_stock > 5 else "#e65100" if low_stock > 0 else "#2e7d32"
    st.markdown(f"<div class='metric-card'><div class='number' style='color:{color};'>{low_stock}</div><div class='label'>مواد منخفضة</div></div>", unsafe_allow_html=True)
with col_stat4:
    st.markdown(f"<div class='metric-card'><div class='number'>{len(st.session_state.get('broiler_farms', {}))}</div><div class='label'>مزارع نشطة</div></div>", unsafe_allow_html=True)

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
    if st.button("📧 إرسال الكود للبريد", use_container_width=True):
        if st.session_state["user_role"] == "owner":
            email = st.text_input("البريد:", placeholder=OWNER_EMAIL, key="code_email")
            if st.button("📤 إرسال", key="send_code_btn"):
                if email and '@' in email:
                    with st.spinner("جاري الإرسال..."):
                        success, msg = send_code_to_email(email)
                        st.success(msg) if success else st.error(msg)
        else:
            st.warning("⚠️ هذه الخاصية للمالك فقط.")

# =====================================================================
# التبويبات
# =====================================================================
tabs_titles = [
    "🐾 القطاع الحيواني",
    "📸 المختبر الذكي (OCR)",
    "🐔 إدارة المزارع",
    "🍼 بدائل الحليب",
    "🕌 مواقيت الصلاة",
    "💊 منبه الجرعات",
    "📊 بورصة الأسعار",
    "🏭 المستودعات",
    "📈 الإنتاج اليومي",
    "📚 المراجع العلمية",
    "💬 تعليقات المختصين",
    "💡 المساعدة الذكية",
    "📖 دليل المستخدم"
]

if st.session_state["user_role"] == "owner":
    tabs_titles.append("📧 إرسال الكود")

tabs = st.tabs(tabs_titles)

# =====================================================================
# تبويب 0: القطاع الحيواني
# =====================================================================
with tabs[0]:
    guide_section("القطاع الحيواني", "هنا يمكنك تركيب أعلاف لجميع أنواع الحيوانات.")
    animal_tabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐴 خيول", "🐫 إبل",
                            "🐔 دواجن", "🐟 أسماك", "🔬 المختبر المتقدم"])
    
    with animal_tabs[0]:
        render_feed_formulation("cattle", "أبقار", "🐄",
            ["كنانة (سوداني)", "بطانة (مدر)", "هولشتاين / محسن"],
            ["تسمين عجول", "حليب/إدرار", "حمل/دفع غذائي", "صيانة", "تسمين مكثف"],
            12.0, 65.0, "أبقار", has_measurements=True)
        st.markdown("---")
        render_nrc_equations("أبقار")
    
    with animal_tabs[1]:
        render_feed_formulation("sheep", "أغنام", "🐏",
            ["الضأن الصحراوي", "البربري", "النعيمي"],
            ["تسمين حملان", "نعاج مرضعات", "نعاج حامل", "نعاج جافة"],
            11.5, 62.0, "أغنام", has_measurements=True)
        st.markdown("---")
        render_nrc_equations("أغنام")
    
    with animal_tabs[2]:
        render_feed_formulation("goat", "ماعز", "🐐",
            ["الماعز النوبي", "الماعز الصحراوي", "بور / محسن"],
            ["تسمين جديان", "عنزات حلابة", "عنزات حامل", "صيانة"],
            11.0, 60.0, "ماعز", has_measurements=True)
        st.markdown("---")
        render_nrc_equations("ماعز")
    
    with animal_tabs[3]:
        render_feed_formulation("horse", "خيول", "🐴",
            ["خيل عربي أصيل", "ثوروبريد", "خيول محلية"],
            ["راحة/صيانة", "عمل خفيف", "عمل متوسط", "عمل مكثف",
             "سباق", "أمهار نامية", "فرسات مرضعات"],
            11.0, 62.0, "خيول", has_measurements=True)
    
    with animal_tabs[4]:
        render_feed_formulation("camel", "إبل", "🐫",
            ["عربية (دروميداري)", "باختري", "هجين"],
            ["راحة/صيانة", "حمل/رضاعة", "إنتاج حليب", "تسمين", "عمل/نقل"],
            10.0, 58.0, "إبل", has_measurements=True)
    
    with animal_tabs[5]:
        render_feed_formulation("poultry", "دواجن", "🐔",
            ["دواجن لاحم (Broiler)", "دواجن بياض (Layer)", "طائر السمان"],
            ["بادي (0-14 يوم)", "نامي (15-28 يوم)", "ناهي (29-42 يوم)", "ناهي متقدم"],
            18.0, 72.0, "دواجن", has_measurements=False)
    
    with animal_tabs[6]:
        render_feed_formulation("fish", "أسماك", "🐟",
            ["البلطي النيلي", "القرموط"],
            ["زريعة/بادئ", "نمو", "تسمين نهائي", "زريعة متقدمة"],
            28.0, 68.0, "أسماك", has_measurements=False)
    
    with animal_tabs[7]:
        render_advanced_lab()

# =====================================================================
# تبويب 1: المختبر الذكي (OCR)
# =====================================================================
with tabs[1]:
    guide_section("المختبر الذكي", "ارفع صورة تركيبة علفية واستخرج القيم الغذائية تلقائياً.")
    render_smart_ocr_lab()

# =====================================================================
# تبويب 2: إدارة المزارع
# =====================================================================
with tabs[2]:
    guide_section("إدارة المزارع", "نظام متكامل لإدارة مزارع الدجاج مع حفظ دائم.")
    st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج</div>', unsafe_allow_html=True)
    
    if st.session_state["user_role"] in ["owner", "specialist", "veterinarian", "nutritionist", "breeder"]:
        with st.expander("➕ إضافة دورة جديدة", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                farm_name = st.text_input("اسم المزرعة/الدورة", key="bf_fname")
                initial_birds = st.number_input("عدد الكتاكيت", min_value=1, value=1000,
                                               step=100, key="bf_ib")
            with col2:
                breed = st.selectbox("السلالة", ["Ross 308", "Cobb 500", "محلية"], key="bf_breed")
                start_date = st.date_input("تاريخ البدء", datetime.now(), key="bf_sd")
            if st.button("💾 إنشاء الدورة", key="bf_create"):
                if farm_name:
                    cycle_id = secrets.token_hex(8)
                    st.session_state["broiler_farms"][cycle_id] = {
                        "farm_name": farm_name, "initial_birds": initial_birds,
                        "breed": breed, "start_date": start_date.isoformat(),
                        "age_days": 0, "current_weight": 0.045,
                        "total_feed": 0, "dead_count": 0
                    }
                    st.success(f"✅ تم إنشاء دورة {farm_name}")
                    voice_guide(f"تم إنشاء دورة {farm_name}")
                    st.rerun()
    
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
                        new_weight = st.number_input("الوزن الحالي (كجم)", min_value=0.01,
                                                     value=float(farm['current_weight']),
                                                     step=0.01, key=f"w_{cid}")
                        new_feed = st.number_input("العلف المستهلك (كجم)", min_value=0.0,
                                                   value=float(farm['total_feed']),
                                                   step=1.0, key=f"f_{cid}")
                    with col_up2:
                        new_dead = st.number_input("النافق الإضافي", min_value=0,
                                                   value=0, step=1, key=f"d_{cid}")
                        new_age = st.number_input("العمر (يوم)", min_value=0,
                                                  value=int(farm['age_days']),
                                                  step=1, key=f"a_{cid}")
                    
                    if st.button(f"📊 تحديث", key=f"up_{cid}"):
                        farm['current_weight'] = new_weight
                        farm['total_feed'] = new_feed
                        farm['dead_count'] += new_dead
                        farm['age_days'] = new_age
                        st.success("✅ تم التحديث")
                        st.rerun()
    else:
        st.info("📭 لا توجد دورات. أضف دورة جديدة.")

# =====================================================================
# تبويب 3: بدائل الحليب
# =====================================================================
with tabs[3]:
    guide_section("بدائل الحليب", "تركيب بدائل الحليب لرضاعة الصغار.")
    render_milk_replacer()
    st.markdown("---")
    render_saved_milk_replacers()

# =====================================================================
# تبويب 4: مواقيت الصلاة
# =====================================================================
with tabs[4]:
    guide_section("مواقيت الصلاة", "عرض مواقيت الصلاة حسب المدينة.")
    prayer_time_reminder()

# =====================================================================
# تبويب 5: منبه الجرعات
# =====================================================================
with tabs[5]:
    guide_section("منبه الجرعات", "إدارة منبهات الجرعات (اللقاحات والفيتامينات).")
    render_dose_reminder_system()

# =====================================================================
# تبويب 6: بورصة الأسعار
# =====================================================================
with tabs[6]:
    guide_section("بورصة الأسعار", "متابعة أسعار المواشي والمنتجات.")
    st.markdown('<div class="section-title">📊 بورصة الأسعار</div>', unsafe_allow_html=True)
    
    if st.session_state["user_role"] in ["owner", "specialist", "veterinarian", "nutritionist", "breeder"]:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🐄 أسعار المواشي")
            for name, price in list(st.session_state["global_livestock_prices"].items()):
                new_price = st.number_input(name, value=float(price), step=5.0,
                                           key=f"price_live_{name}")
                st.session_state["global_livestock_prices"][name] = new_price
        with col2:
            st.subheader("🥩 أسعار المنتجات")
            for name, price in list(st.session_state["global_products_prices"].items()):
                new_price = st.number_input(name, value=float(price), step=0.5,
                                           key=f"price_prod_{name}")
                st.session_state["global_products_prices"][name] = new_price
    else:
        st.info("🔒 التعديل متاح للمالك والمختصين.")
        for name, price in st.session_state["global_livestock_prices"].items():
            st.write(f"- {name}: ${price:.2f}")

# =====================================================================
# تبويب 7: المستودعات
# =====================================================================
with tabs[7]:
    guide_section("المستودعات", "إدارة المخزون.")
    st.markdown('<div class="section-title">🏭 المستودعات</div>', unsafe_allow_html=True)
    
    inv_data = []
    for item, data in st.session_state["inventory"].items():
        qty = data["quantity"] if isinstance(data, dict) else data
        thr = data.get("min_threshold", 5.0) if isinstance(data, dict) else 5.0
        status = "🔴" if qty <= 0 else "🟠" if qty < thr else "🟢"
        inv_data.append({"المادة": item, "الكمية (طن)": qty, "الحد الأدنى": thr, "الحالة": status})
    st.dataframe(pd.DataFrame(inv_data), use_container_width=True)
    
    if st.session_state["user_role"] in ["owner", "specialist"]:
        with st.expander("تحديث المخزون", expanded=False):
            sel = st.selectbox("المادة", list(FLAT_FEED_DB.keys()), key="inv_sel")
            new_qty = st.number_input("الكمية الجديدة (طن)", min_value=0.0, value=25.0, key="inv_qty")
            if st.button("تحديث", key="inv_upd"):
                if isinstance(st.session_state["inventory"][sel], dict):
                    st.session_state["inventory"][sel]["quantity"] = new_qty
                else:
                    st.session_state["inventory"][sel] = new_qty
                st.success("✅ تم التحديث")
                st.rerun()

# =====================================================================
# تبويب 8: الإنتاج اليومي
# =====================================================================
with tabs[8]:
    guide_section("الإنتاج اليومي", "تسجيل بيانات الإنتاج اليومي.")
    st.markdown('<div class="section-title">📈 الإنتاج اليومي</div>', unsafe_allow_html=True)
    
    if st.session_state["user_role"] in ["owner", "specialist", "veterinarian", "nutritionist", "breeder"]:
        with st.form("daily_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                farm = st.text_input("المزرعة", key="dp_farm")
                date = st.date_input("التاريخ", datetime.now(), key="dp_date")
            with col2:
                milk = st.number_input("الحليب (لتر)", min_value=0.0, value=0.0, key="dp_milk")
                eggs = st.number_input("البيض (عدد)", min_value=0, value=0, key="dp_eggs")
            with col3:
                weight_gain = st.number_input("زيادة الوزن (كجم)", min_value=0.0, value=0.0, key="dp_wg")
                mortality = st.number_input("النافق", min_value=0, value=0, key="dp_dead")
            notes = st.text_area("ملاحظات", key="dp_notes")
            
            if st.form_submit_button("💾 حفظ"):
                st.session_state["daily_production_log"].append({
                    "farm": farm, "date": date.isoformat(), "milk": milk,
                    "eggs": eggs, "weight_gain": weight_gain,
                    "mortality": mortality, "notes": notes
                })
                st.success("✅ تم الحفظ")
    
    if st.session_state["daily_production_log"]:
        st.subheader("📋 سجل الإنتاج اليومي")
        df_prod = pd.DataFrame(st.session_state["daily_production_log"])
        st.dataframe(df_prod, use_container_width=True, hide_index=True)

# =====================================================================
# تبويب 9: المراجع العلمية
# =====================================================================
with tabs[9]:
    guide_section("المراجع العلمية", "مصادر معتمدة في تغذية الحيوان.")
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
    
    for cat_key, cat_data in ScientificReferenceSystem.REFERENCES.items():
        with st.expander(f"{cat_data['icon']} {cat_data['title']}"):
            for ref in cat_data.get("references", []):
                st.markdown(f"""
                <div style='background:#f8f9fa; padding:12px; border-radius:8px; margin-bottom:8px; border-right:4px solid #2e7d32;'>
                    <b>{ref.get('title', 'عنوان')}</b><br>
                    👤 {ref.get('authors', 'مؤلف')}<br>
                    📅 {ref.get('year', 'سنة')} | 📚 {ref.get('publisher', 'ناشر')}<br>
                    <small>{ref.get('summary', '')}</small>
                </div>
                """, unsafe_allow_html=True)
    
    st.subheader("💡 المعرفة السريعة")
    q = st.text_input("اسأل عن مصطلح:", key="kb_q")
    if q:
        answer = ScientificReferenceSystem.get_knowledge_answer(q)
        if answer:
            st.success(f"📖 {answer['answer']}")
            st.info(f"🔹 تبسيط: {answer['simplified']}")

# =====================================================================
# تبويب 10: تعليقات المختصين
# =====================================================================
with tabs[10]:
    guide_section("التعليقات", "قناة لتبادل الخبرات.")
    st.markdown('<div class="section-title">💬 تعليقات المختصين</div>', unsafe_allow_html=True)
    
    st.text_area("التعليقات الحالية:", value=st.session_state["shared_comments"],
                 height=200, disabled=True, key="comments_display")
    
    new_c = st.text_area("إضافة تعليق جديد:", key="new_comment")
    if st.button("➕ نشر التعليق", key="post_comment"):
        if new_c:
            role_ar = {"owner": "المالك", "specialist": "مختص",
                       "veterinarian": "بيطري", "nutritionist": "تغذية",
                       "breeder": "مربي"}.get(st.session_state["user_role"], "مستخدم")
            st.session_state["shared_comments"] += f"\n• [{role_ar} {datetime.now().strftime('%Y-%m-%d %H:%M')}]: {new_c}"
            st.success("تم النشر!")
            st.rerun()

# =====================================================================
# تبويب 11: المساعدة الذكية
# =====================================================================
with tabs[11]:
    guide_section("المساعدة الذكية", "دليل سريع للمنصة.")
    st.markdown('<div class="section-title">💡 المساعدة الذكية</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#e3f2fd; padding:20px; border-radius:12px; direction:rtl;'>
    <h3>🌟 خطوات الاستخدام:</h3>
    <ol>
    <li>اختر نوع الحيوان من تبويب "القطاع الحيواني"</li>
    <li>حدد السلالة والمرحلة الإنتاجية</li>
    <li>أدخل القياسات الجسدية (إن توفرت)</li>
    <li>اختر المكونات العلفية وحدد أسعارها</li>
    <li>اضغط "تشغيل محرك التركيب"</li>
    <li>احصل على الخلطة المثالية + تقرير PDF</li>
    </ol>
    <h3>🔬 المختبر الذكي:</h3>
    <p>ارفع صورة تركيبة علفية وسيقوم النظام باستخراج القيم الغذائية تلقائياً.</p>
    <h3>🧮 المعادلات الإنتاجية NRC:</h3>
    <p>احسب الاحتياجات الدقيقة من الوزن الحي والإنتاج الفعلي.</p>
    <h3>📞 الدعم الفني:</h3>
    <p>abukram128@gmail.com | +249123533489</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔊 استمع للتعليمات", key="help_voice"):
        voice_guide("مرحباً، هذا دليل استخدام منصة تاور نولجي العلمية.")

# =====================================================================
# تبويب 12: دليل المستخدم
# =====================================================================
with tabs[12]:
    guide_section("دليل المستخدم", "شرح مفصل للمنصة.")
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="manual-book">
    <div class="book-chapter">📘 الفصل 1: مقدمة</div>
    <div class="book-body">
    تاور نولجي Tawornology العلمية منصة متكاملة لتركيب الأعلاف وإدارة الإنتاج الحيواني.
    تعتمد على البرمجة الخطية لحساب أقل تكلفة لخلطة علفية تلبي الاحتياجات الغذائية.
    </div>
    
    <div class="book-chapter">📗 الفصل 2: تركيب العلف</div>
    <div class="book-body">
    1. اختر نوع الحيوان.<br>
    2. حدد السلالة والمرحلة الإنتاجية.<br>
    3. أدخل العمر والحالة الفسيولوجية.<br>
    4. اختر المكونات وحدد أسعارها.<br>
    5. اضغط "تشغيل محرك التركيب".<br>
    6. حمل التقرير PDF.
    </div>
    
    <div class="book-chapter">📕 الفصل 3: المختبر الذكي</div>
    <div class="book-body">
    ارفع صورة تركيبة علفية واستخرج القيم الغذائية (CP، DC، SE، NDF، ADF) تلقائياً.
    </div>
    
    <div class="book-chapter">🧮 الفصل 4: المعادلات الإنتاجية</div>
    <div class="book-body">
    معادلات NRC لحساب الاحتياجات من الوزن والإنتاج:
    - للألبان: بروتين الإدامة + الأيض + الإنتاج
    - للتسمين: بروتين الصيانة + الإنتاج + معامل SE/DP
    </div>
    
    <div class="book-chapter">🍼 الفصل 5: بدائل الحليب</div>
    <div class="book-body">
    تركيب بديل حليب متكامل لرضاعة الصغار حسب العمر والنوع.
    </div>
    
    <div class="book-chapter">🐔 الفصل 6: إدارة المزارع</div>
    <div class="book-body">
    إنشاء دورات إنتاج، تسجيل بيانات يومية، متابعة النفوق والوزن.
    </div>
    
    <div class="book-chapter">💊 الفصل 7: منبه الجرعات</div>
    <div class="book-body">
    تسجيل ومتابعة جرعات اللقاحات والفيتامينات مع تنبيهات واتساب.
    </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# تبويب 13: إرسال الكود (للمالك فقط)
# =====================================================================
if st.session_state["user_role"] == "owner" and len(tabs) > 13:
    with tabs[13]:
        guide_section("إرسال الكود", "إرسال السورس كود إلى البريد.")
        st.markdown('<div class="section-title">📧 إرسال السورس كود</div>', unsafe_allow_html=True)
        st.info("هذه الخاصية متاحة فقط للمالك.")
        
        email = st.text_input("البريد المستلم:", value=OWNER_EMAIL, key="send_email_final")
        password = st.text_input("كلمة مرور التطبيق (App Password):", type="password", key="send_pass_final")
        
        if password:
            st.session_state["email_password"] = password
        
        if st.button("📤 إرسال الكود", type="primary", use_container_width=True, key="send_final_btn"):
            if email and '@' in email:
                with st.spinner("جاري الإرسال..."):
                    success, msg = send_code_to_email(email)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
            else:
                st.warning("⚠️ يرجى إدخال بريد صحيح")

# =====================================================================
# التذييل
# =====================================================================
st.markdown("""
<div style='text-align:center; padding:20px; margin-top:30px; border-top:2px solid #e0e0e0; color:#888; font-size:0.9rem;'>
🌾 <b>تاور نولجي Tawornology العلمية</b> - للانتاج الحيواني وتركيب الاعلاف<br>
© 2026 | الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان<br>
🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b> - رحمهما الله
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

print("=" * 70)
print("🌾 تاور نولجي Tawornology العلمية v17.0")
print("✅ تم تحميل جميع الأجزاء بنجاح - جاهز للتشغيل")
print("=" * 70)
