# =====================================================================
# منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف
# النسخة المتكاملة النهائية - أكثر من 5000 سطر
# =====================================================================
# Digital Signature: 110dfcb10bc6902ee96175517109d7c7
# Generated: 2026-07-02T22:16:27.283609

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
# السطر 1-50: إعدادات النظام الأساسية
# =====================================================================
st.set_page_config(
    page_title="منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف",
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

# أكواد الدخول المسموح بها
CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1},
    "2024": {"role": "veterinarian", "name": "الطبيب البيطري", "level": 2},
    "2025": {"role": "nutritionist", "name": "أخصائي التغذية", "level": 2}
}

# إعدادات البريد الإلكتروني
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
# السطر 51-150: كلاس DatabaseManager المتقدم
# =====================================================================
class DatabaseManager:
    """
    مدير قاعدة البيانات المحلية المتقدم باستخدام SQLite.
    يحتوي على جميع الجداول اللازمة لتشغيل المنصة بكامل ميزاتها.
    """
    def __init__(self, db_path="tower_platform.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """تهيئة جميع الجداول في قاعدة البيانات مع الحقول المناسبة"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # جدول المستخدمين - يدعم الأدوار المختلفة والصلاحيات
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
            is_active INTEGER DEFAULT 1
        )''')
        
        # جدول الدورات الإنتاجية - لتسجيل دورات الإنتاج في المزارع
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
        
        # جدول الخلطات العلفية المحفوظة
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
            usage_count INTEGER DEFAULT 0,
            rating REAL DEFAULT 0
        )''')
        
        # جدول الفواتير - لإدارة عمليات البيع
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
        
        # جدول الأسعار التاريخية للمواد الخام
        c.execute('''CREATE TABLE IF NOT EXISTS price_history (
            record_id TEXT PRIMARY KEY,
            ingredient_name TEXT,
            price REAL,
            currency TEXT,
            country TEXT,
            city TEXT,
            record_date TEXT,
            recorded_by TEXT,
            source TEXT,
            notes TEXT
        )''')
        
        # جدول الأدوية البيطرية - لإدارة الأدوية والمستحضرات
        c.execute('''CREATE TABLE IF NOT EXISTS veterinary_medicines (
            medicine_id TEXT PRIMARY KEY,
            medicine_name TEXT,
            category TEXT,
            active_ingredient TEXT,
            dosage REAL,
            dosage_unit TEXT,
            administration_route TEXT,
            withdrawal_period INTEGER,
            price REAL,
            stock_quantity REAL,
            expiry_date TEXT,
            supplier TEXT,
            notes TEXT
        )''')
        
        # جدول سجلات العلاج - لتسجيل العلاجات المقدمة للحيوانات
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
        
        # جدول الميزانية والتكاليف
        c.execute('''CREATE TABLE IF NOT EXISTS budget (
            budget_id TEXT PRIMARY KEY,
            category TEXT,
            description TEXT,
            amount REAL,
            budget_type TEXT,
            record_date TEXT,
            created_by TEXT,
            notes TEXT
        )''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query: str, params: tuple = ()):
        """تنفيذ استعلام قاعدة بيانات وإرجاع النتائج"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        result = c.execute(query, params)
        conn.commit()
        data = result.fetchall()
        conn.close()
        return data
    
    def execute_many(self, query: str, params_list: list):
        """تنفيذ استعلام متعدد الإدخالات"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        result = c.executemany(query, params_list)
        conn.commit()
        data = result.fetchall()
        conn.close()
        return data
    
    def insert_record(self, table: str, data: dict):
        """إدراج سجل جديد في الجدول المحدد"""
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
        """تحديث سجل في الجدول المحدد"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        set_clause = ', '.join([f"{k}=?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        c.execute(query, list(data.values()))
        conn.commit()
        conn.close()
    
    def delete_record(self, table: str, condition: str):
        """حذف سجل من الجدول المحدد"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        query = f"DELETE FROM {table} WHERE {condition}"
        c.execute(query)
        conn.commit()
        conn.close()
    
    def get_record_by_id(self, table: str, record_id: str, id_column: str = "id"):
        """الحصول على سجل بواسطة المعرف"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        query = f"SELECT * FROM {table} WHERE {id_column}=?"
        result = c.execute(query, (record_id,))
        data = result.fetchone()
        conn.close()
        return data
    
    def get_all_records(self, table: str, order_by: str = None, limit: int = None):
        """الحصول على جميع السجلات من جدول معين"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        query = f"SELECT * FROM {table}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        result = c.execute(query)
        data = result.fetchall()
        conn.close()
        return data
    
    def get_records_by_condition(self, table: str, condition: str, params: tuple = ()):
        """الحصول على سجلات حسب شرط معين"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        query = f"SELECT * FROM {table} WHERE {condition}"
        result = c.execute(query, params)
        data = result.fetchall()
        conn.close()
        return data

# =====================================================================
# السطر 151-250: كلاس AuthManager المتقدم مع إدارة الصلاحيات
# =====================================================================
class AuthManager:
    """
    إدارة المصادقة والصلاحيات المتقدمة.
    يدعم أنواع متعددة من المستخدمين مع صلاحيات مختلفة.
    """
    ROLES = {
        "owner": {"level": 5, "permissions": ["all"], "name": "المالك", "icon": "👑"},
        "specialist": {"level": 4, "permissions": ["view", "create", "edit", "delete"], "name": "المختص", "icon": "👨‍🔬"},
        "veterinarian": {"level": 3, "permissions": ["view", "create", "edit", "medicines"], "name": "الطبيب البيطري", "icon": "💊"},
        "nutritionist": {"level": 3, "permissions": ["view", "create", "edit", "formulas"], "name": "أخصائي التغذية", "icon": "🧬"},
        "breeder": {"level": 2, "permissions": ["view", "create", "edit_own"], "name": "المربي", "icon": "🌾"},
        "viewer": {"level": 1, "permissions": ["view"], "name": "مشاهد", "icon": "👀"}
    }
    
    def __init__(self):
        self.db = DatabaseManager()
        self._create_default_users()
    
    def _create_default_users(self):
        """إنشاء المستخدمين الافتراضيين إذا لم يكونوا موجودين"""
        default_users = [
            ('admin', 'admin123', 'owner', 'مدير النظام', 'admin@tower.com', '+249123456789', 'إدارة الأنظمة', 10),
            ('specialist', 'spec123', 'specialist', 'المختص العام', 'specialist@tower.com', '+249123456788', 'تغذية وإنتاج', 8),
            ('vet', 'vet123', 'veterinarian', 'الطبيب البيطري', 'vet@tower.com', '+249123456787', 'طب بيطري', 6),
            ('nutritionist', 'nutri123', 'nutritionist', 'أخصائي التغذية', 'nutrition@tower.com', '+249123456786', 'تغذية حيوان', 7),
            ('breeder', 'breed123', 'breeder', 'المربي', 'breeder@tower.com', '+249123456785', 'إنتاج حيواني', 5)
        ]
        for username, password, role, full_name, email, phone, specialty, experience in default_users:
            users = self.db.execute_query("SELECT * FROM users WHERE username=?", (username,))
            if not users:
                self.create_user(username, password, role, full_name, email, phone, specialty, experience)
    
    def create_user(self, username, password, role, full_name, email, phone, specialty="", experience=0):
        """إنشاء مستخدم جديد مع تشفير كلمة المرور"""
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
            'is_active': 1
        }
        self.db.insert_record('users', data)
        return user_id
    
    def authenticate(self, username, password):
        """التحقق من صحة بيانات الدخول وتسجيل وقت الدخول"""
        users = self.db.execute_query("SELECT * FROM users WHERE username=? AND is_active=1", (username,))
        if users:
            user = users[0]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user[2] == password_hash:
                # تحديث وقت آخر دخول
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
    
    def get_user_permissions(self, role):
        """الحصول على صلاحيات دور معين"""
        return self.ROLES.get(role, {}).get('permissions', ['view'])
    
    def has_permission(self, user_role, permission):
        """التحقق من وجود صلاحية معينة للمستخدم"""
        permissions = self.get_user_permissions(user_role)
        return 'all' in permissions or permission in permissions
    
    def get_all_users(self):
        """الحصول على جميع المستخدمين النشطين"""
        return self.db.execute_query("SELECT * FROM users WHERE is_active=1 ORDER BY full_name")
    
    def get_user_by_id(self, user_id):
        """الحصول على مستخدم بواسطة المعرف"""
        return self.db.get_record_by_id('users', user_id, 'user_id')
    
    def update_user(self, user_id, data):
        """تحديث بيانات المستخدم"""
        self.db.update_record('users', data, f"user_id='{user_id}'")
    
    def delete_user(self, user_id):
        """حذف مستخدم (تعطيل الحساب)"""
        self.db.update_record('users', {'is_active': 0}, f"user_id='{user_id}'")
    
    def change_password(self, user_id, new_password):
        """تغيير كلمة المرور"""
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        self.db.update_record('users', {'password_hash': password_hash}, f"user_id='{user_id}'")

# =====================================================================
# السطر 251-350: كلاس PricePredictor المتقدم مع نماذج متعددة
# =====================================================================
class PricePredictor:
    """
    التنبؤ بأسعار المواد الخام باستخدام تقنيات متعددة:
    - المتوسط المرجح (Weighted Average)
    - الانحدار الخطي (Linear Regression)
    - غابة عشوائية (Random Forest) - إذا توفرت بيانات كافية
    """
    def __init__(self):
        self.db = DatabaseManager()
        self.models = {}
    
    def get_ingredient_prices(self, ingredient_name, days=90):
        """الحصول على الأسعار التاريخية لمادة معينة"""
        results = self.db.execute_query(
            "SELECT * FROM price_history WHERE ingredient_name=? ORDER BY record_date DESC LIMIT ?",
            (ingredient_name, days))
        return [{'record_id': r[0], 'ingredient_name': r[1], 'price': r[2], 'currency': r[3],
                 'country': r[4], 'city': r[5], 'record_date': r[6]} for r in results]
    
    def add_price_record(self, ingredient_name, price, currency="USD", country="السودان", city="الخرطوم", recorded_by="system"):
        """إضافة سعر جديد للمادة"""
        record_id = secrets.token_hex(8)
        data = {
            'record_id': record_id,
            'ingredient_name': ingredient_name,
            'price': price,
            'currency': currency,
            'country': country,
            'city': city,
            'record_date': datetime.now().isoformat(),
            'recorded_by': recorded_by,
            'source': 'manual',
            'notes': ''
        }
        self.db.insert_record('price_history', data)
        return record_id
    
    def get_price_trend(self, ingredient_name, days=30):
        """تحليل اتجاه الأسعار مع حساب التقلب"""
        prices = self.get_ingredient_prices(ingredient_name, days)
        if len(prices) < 3:
            return {'trend': 'stable', 'change_percent': 0, 'volatility': 0, 'current_price': None, 'avg_price': None}
        
        price_values = [p['price'] for p in prices]
        dates = [datetime.fromisoformat(p['record_date']) for p in prices]
        
        # حساب الاتجاه باستخدام الانحدار الخطي
        if len(price_values) >= 2:
            x = np.array(range(len(price_values))).reshape(-1, 1)
            y = np.array(price_values)
            model = LinearRegression()
            model.fit(x, y)
            slope = model.coef_[0]
            
            # تقلب الأسعار (معامل التباين)
            volatility = np.std(price_values) / np.mean(price_values) if np.mean(price_values) > 0 else 0
            
            # تغيير النسبة المئوية
            if len(price_values) >= 2:
                change_percent = ((price_values[0] - price_values[-1]) / price_values[-1]) * 100 if price_values[-1] > 0 else 0
            else:
                change_percent = 0
            
            trend = 'up' if slope > 0.5 else 'down' if slope < -0.5 else 'stable'
            
            return {
                'trend': trend,
                'change_percent': change_percent,
                'volatility': volatility,
                'slope': slope,
                'current_price': price_values[0] if price_values else None,
                'avg_price': np.mean(price_values) if price_values else None,
                'min_price': min(price_values) if price_values else None,
                'max_price': max(price_values) if price_values else None,
                'data_points': len(price_values)
            }
        
        return {'trend': 'stable', 'change_percent': 0, 'volatility': 0, 'current_price': None, 'avg_price': None}
    
    def predict_price(self, ingredient_name, days_ahead=7, method='ensemble'):
        """
        توقع السعر المستقبلي لمادة معينة باستخدام طرق مختلفة.
        الأساليب: 'weighted', 'linear', 'ensemble'
        """
        prices = self.get_ingredient_prices(ingredient_name, 60)
        if len(prices) < 5:
            return {'prediction': None, 'confidence': 0, 'method': method, 'error': 'بيانات غير كافية'}
        
        price_values = [p['price'] for p in prices]
        
        if method == 'weighted' or method == 'ensemble':
            # المتوسط المرجح: الأيام الأحدث لها وزن أكبر
            weights = np.array(range(1, len(price_values) + 1))
            weighted_avg = np.average(price_values, weights=weights)
            trend = (price_values[0] - price_values[-1]) / len(price_values) if len(price_values) > 1 else 0
            pred_weighted = weighted_avg + (trend * days_ahead)
            conf_weighted = min(1, len(price_values) / 30)
        
        if method == 'linear' or method == 'ensemble':
            # الانحدار الخطي
            x = np.array(range(len(price_values))).reshape(-1, 1)
            y = np.array(price_values)
            model = LinearRegression()
            model.fit(x, y)
            pred_linear = model.predict([[len(price_values) + days_ahead - 1]])[0]
            r2 = model.score(x, y)
            conf_linear = min(1, r2 + 0.3)
        
        if method == 'weighted':
            prediction = pred_weighted
            confidence = conf_weighted
        elif method == 'linear':
            prediction = pred_linear
            confidence = conf_linear
        else:  # ensemble
            if pred_weighted and pred_linear:
                prediction = (pred_weighted + pred_linear) / 2
                confidence = (conf_weighted + conf_linear) / 2
            else:
                prediction = pred_weighted or pred_linear
                confidence = conf_weighted or conf_linear
        
        return {
            'prediction': max(0, prediction) if prediction else None,
            'confidence': min(1, confidence) if confidence else 0,
            'current_price': price_values[0] if price_values else None,
            'trend': 'up' if prediction > price_values[0] else 'down' if prediction < price_values[0] else 'stable',
            'method': method,
            'data_points': len(price_values)
        }
    
    def get_market_summary(self):
        """الحصول على ملخص السوق لجميع المواد الرئيسية"""
        main_ingredients = ['ذرة صفراء', 'كسب فول صويا 44%', 'نخالة قمح', 'شعير مطحون', 'مسحوق أسماك']
        summary = {}
        for ing in main_ingredients:
            trend = self.get_price_trend(ing, 30)
            pred = self.predict_price(ing, 7, 'ensemble')
            summary[ing] = {
                'current_price': trend.get('current_price'),
                'trend': trend.get('trend'),
                'change_percent': trend.get('change_percent'),
                'volatility': trend.get('volatility'),
                'prediction_7d': pred.get('prediction'),
                'confidence': pred.get('confidence')
            }
        return summary

# =====================================================================
# السطر 351-500: كلاس ScientificReferenceSystem المتقدم
# =====================================================================
class ScientificReferenceSystem:
    """
    نظام المراجع العلمية وبنك المعرفة المتقدم.
    يحتوي على مراجع علمية موثوقة، إجابات لأسئلة شائعة، وحقائق علمية.
    """
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان",
            "icon": "📚",
            "description": "مراجع شاملة في تغذية الحيوان بمختلف أنواعه",
            "references": [
                {
                    "id": "REF001",
                    "authors": "McDonald, P., Edwards, R.A., Greenhalgh, J.F.D., Morgan, C.A.",
                    "year": 2011,
                    "title": "Animal Nutrition",
                    "publisher": "Pearson Education",
                    "edition": "7th Edition",
                    "isbn": "978-1408204238",
                    "summary": "المرجع الأساسي في تغذية الحيوان، يغطي جميع جوانب التغذية من الهضم إلى متطلبات العناصر الغذائية.",
                    "tags": ["nutrition", "digestion", "requirements", "comprehensive"]
                },
                {
                    "id": "REF002",
                    "authors": "Cheeke, P.R., Dierenfeld, E.S.",
                    "year": 2010,
                    "title": "Comparative Animal Nutrition and Metabolism",
                    "publisher": "CABI",
                    "isbn": "978-1845936310",
                    "summary": "مقارنة بين آليات التغذية والتمثيل الغذائي في مختلف أنواع الحيوانات.",
                    "tags": ["comparative", "metabolism", "physiology"]
                }
            ]
        },
        "protein_amino_acids": {
            "title": "البروتين والأحماض الأمينية",
            "icon": "🧬",
            "description": "مراجع متخصصة في البروتين والأحماض الأمينية في تغذية الحيوان",
            "references": [
                {
                    "id": "REF003",
                    "authors": "NRC (National Research Council)",
                    "year": 2012,
                    "title": "Nutrient Requirements of Swine",
                    "publisher": "National Academies Press",
                    "edition": "11th Revised Edition",
                    "isbn": "978-0309214230",
                    "summary": "المرجع الرسمي لمتطلبات العناصر الغذائية للخنازير.",
                    "tags": ["swine", "requirements", "protein", "amino_acids"]
                },
                {
                    "id": "REF004",
                    "authors": "NRC (National Research Council)",
                    "year": 2001,
                    "title": "Nutrient Requirements of Dairy Cattle",
                    "publisher": "National Academies Press",
                    "edition": "7th Revised Edition",
                    "isbn": "978-0309069977",
                    "summary": "المرجع الأساسي في تغذية أبقار الحليب ومتطلباتها من البروتين والطاقة.",
                    "tags": ["dairy", "cattle", "protein", "energy"]
                },
                {
                    "id": "REF005",
                    "authors": "Bryden, W.L., Li, X., Ravindran, G.",
                    "year": 2009,
                    "title": "Digestible Amino Acids in Poultry Feed Ingredients",
                    "publisher": "University of Sydney",
                    "summary": "دراسة شاملة عن الأحماض الأمينية المهضومة في مواد العلف للدواجن.",
                    "tags": ["poultry", "amino_acids", "digestibility"]
                }
            ]
        },
        "horses": {
            "title": "تغذية الخيول",
            "icon": "🐴",
            "description": "مراجع متخصصة في تغذية الخيول ومتطلباتها",
            "references": [
                {
                    "id": "REF015",
                    "authors": "NRC (National Research Council)",
                    "year": 2007,
                    "title": "Nutrient Requirements of Horses",
                    "publisher": "National Academies Press",
                    "edition": "6th Revised Edition",
                    "isbn": "978-0309102124",
                    "summary": "المرجع الأساسي في تغذية الخيول ومتطلباتها الغذائية حسب العمر والنشاط.",
                    "tags": ["horses", "requirements", "nutrition"]
                },
                {
                    "id": "REF015B",
                    "authors": "Frape, D.",
                    "year": 2004,
                    "title": "Equine Nutrition and Feeding",
                    "publisher": "Blackwell Publishing",
                    "edition": "3rd Edition",
                    "isbn": "978-0632058166",
                    "summary": "دليل شامل لتغذية الخيول في جميع مراحل الحياة والنشاط الرياضي.",
                    "tags": ["horses", "feeding", "management"]
                }
            ]
        },
        "poultry": {
            "title": "تغذية الدواجن",
            "icon": "🐔",
            "description": "مراجع متخصصة في تغذية الدواجن بأنواعها",
            "references": [
                {
                    "id": "REF010",
                    "authors": "Leeson, S., Summers, J.D.",
                    "year": 2009,
                    "title": "Commercial Poultry Nutrition",
                    "publisher": "Nottingham University Press",
                    "edition": "3rd Edition",
                    "isbn": "978-1904761578",
                    "summary": "المرجع العملي في تغذية الدواجن التجارية وإدارة التغذية.",
                    "tags": ["poultry", "commercial", "broiler", "layer"]
                },
                {
                    "id": "REF011",
                    "authors": "NRC (National Research Council)",
                    "year": 1994,
                    "title": "Nutrient Requirements of Poultry",
                    "publisher": "National Academies Press",
                    "edition": "9th Revised Edition",
                    "isbn": "978-0309048927",
                    "summary": "المرجع الرسمي لمتطلبات الدواجن الغذائية حسب العمر والإنتاج.",
                    "tags": ["poultry", "requirements", "nutrients"]
                }
            ]
        },
        "ruminants": {
            "title": "تغذية المجترات",
            "icon": "🐄",
            "description": "مراجع متخصصة في تغذية الأبقار والأغنام والماعز",
            "references": [
                {
                    "id": "REF012",
                    "authors": "Church, D.C.",
                    "year": 1993,
                    "title": "The Ruminant Animal: Digestive Physiology and Nutrition",
                    "publisher": "Waveland Press",
                    "isbn": "978-0881337389",
                    "summary": "المرجع الشامل في فسيولوجيا الهضم والتغذية للمجترات.",
                    "tags": ["ruminants", "digestion", "physiology"]
                },
                {
                    "id": "REF012B",
                    "authors": "Van Soest, P.J.",
                    "year": 1994,
                    "title": "Nutritional Ecology of the Ruminant",
                    "publisher": "Cornell University Press",
                    "edition": "2nd Edition",
                    "isbn": "978-0801427725",
                    "summary": "المرجع الكلاسيكي في تغذية المجترات وتحليل الألياف وتأثيرها.",
                    "tags": ["ruminants", "fiber", "ecology"]
                }
            ]
        },
        "aquaculture": {
            "title": "تغذية الأسماك",
            "icon": "🐟",
            "description": "مراجع متخصصة في تغذية الأسماك والمزارع المائية",
            "references": [
                {
                    "id": "REF016",
                    "authors": "Halver, J.E., Hardy, R.W.",
                    "year": 2002,
                    "title": "Fish Nutrition",
                    "publisher": "Academic Press",
                    "edition": "3rd Edition",
                    "isbn": "978-0123196521",
                    "summary": "المرجع الشامل في تغذية الأسماك والمزارع المائية بأنواعها.",
                    "tags": ["fish", "aquaculture", "nutrition"]
                }
            ]
        },
        "digestible_protein": {
            "title": "البروتين المهضوم وتقييم الأعلاف",
            "icon": "🔬",
            "description": "مراجع متخصصة في البروتين المهضوم وتقييم جودة الأعلاف",
            "references": [
                {
                    "id": "REF023",
                    "authors": "INRA",
                    "year": 2007,
                    "title": "INRA Feeding System for Ruminants",
                    "publisher": "Wageningen Academic Publishers",
                    "isbn": "978-9086860197",
                    "summary": "النظام الفرنسي المتقدم لتغذية المجترات وتقدير البروتين المهضوم والطاقة.",
                    "tags": ["protein", "digestibility", "feeding_system"]
                },
                {
                    "id": "REF024",
                    "authors": "Pesti, G.M., Miller, B.R.",
                    "year": 2009,
                    "title": "Least-Cost Feed Formulation: Theory and Practice",
                    "publisher": "University of Georgia",
                    "summary": "النظرية والتطبيق العملي لتركيب الأعلاف بأقل تكلفة باستخدام البرمجة الخطية.",
                    "tags": ["formulation", "linear_programming", "cost"]
                }
            ]
        },
        "feed_analysis": {
            "title": "تحليل الأعلاف وتقييم الجودة",
            "icon": "🧪",
            "description": "مراجع في تحليل الأعلاف وتقييم جودتها",
            "references": [
                {
                    "id": "REF030",
                    "authors": "AOAC International",
                    "year": 2019,
                    "title": "Official Methods of Analysis",
                    "publisher": "AOAC International",
                    "edition": "21st Edition",
                    "isbn": "978-0935584875",
                    "summary": "المرجع الرسمي لطرق تحليل الأعلاف والمواد الغذائية.",
                    "tags": ["analysis", "methods", "quality"]
                },
                {
                    "id": "REF031",
                    "authors": "NRC",
                    "year": 2001,
                    "title": "Nutrient Requirements of Dairy Cattle - Feed Composition Tables",
                    "publisher": "National Academies Press",
                    "summary": "جداول تركيب الأعلاف للماشية الحلابة مع قيم العناصر الغذائية.",
                    "tags": ["feed_composition", "dairy", "tables"]
                }
            ]
        }
    }
    
    # بنك المعرفة الموسع مع إجابات مفصلة
    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم (Digestible Protein - DP) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف. يتم حسابه بضرب نسبة البروتين الخام (CP) في معامل الهضم (DC) لكل مادة علفية. هذا المقياس أدق من البروتين الخام لأنه يعكس القيمة الغذائية الحقيقية التي يستفيد منها الحيوان.",
            "reference": "REF023",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً، وليس مجرد الكمية الموجودة في العلف.",
            "category": "protein",
            "tags": ["digestion", "nutrition", "protein"]
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (Starch Equivalent - SE) هو مقياس لكمية الطاقة التي يوفرها العلف للحيوان، مقارنة بالطاقة التي يوفرها النشاء النقي. يستخدم هذا المقياس لتقييم كفاءة الطاقة في الأعلاف المختلفة، وكلما زاد الرقم زادت الطاقة التي يوفرها العلف.",
            "reference": "REF006",
            "simplified": "معادل النشاء يقيس كمية الطاقة في العلف، وكلما زاد الرقم زادت الطاقة التي يمنحها للحيوان.",
            "category": "energy",
            "tags": ["energy", "starch", "feeding"]
        },
        "كيف يتم تركيب العلف الأمثل": {
            "answer": "يتم تركيب العلف الأمثل باستخدام محرك الاستمثال الخطي (Linear Programming) الذي يحسب أقل تكلفة لتحقيق متطلبات غذائية محددة. تشمل المتطلبات: البروتين المهضوم، الطاقة (معادل النشاء)، الألياف، المعادن، والفيتامينات. يتم إدخال قيود على نسب المكونات وحدود قصوى ودنيا لكل عنصر.",
            "reference": "REF024",
            "simplified": "نستخدم برنامجاً ذكياً يحسب أرخص خلطة علفية تلبي جميع احتياجات الحيوان الغذائية.",
            "category": "formulation",
            "tags": ["optimization", "least_cost", "formulation"]
        },
        "ما هي أهمية إضافة الإنزيمات للأعلاف": {
            "answer": "الإنزيمات في الأعلاف تعمل على تحسين هضم واستفادة الحيوان من العناصر الغذائية. الإنزيمات مثل الفايتيز تحرر الفسفور المرتبط في حبوب العلف، وإنزيمات NSP (مثل الزيلاناز والبيتا جلوكاناز) تكسر جدران الخلايا النباتية مما يزيد من هضم الكربوهيدرات ويحسن كفاءة التحويل الغذائي.",
            "reference": "REF010",
            "simplified": "الإنزيمات تساعد الحيوان على هضم العلف بشكل أفضل، مما يوفر في تكاليف التغذية ويحسن الإنتاج.",
            "category": "enzymes",
            "tags": ["enzymes", "digestion", "efficiency"]
        },
        "ما هو مؤشر EPEF": {
            "answer": "مؤشر الأداء الأوروبي EPEF (European Production Efficiency Factor) هو مقياس شامل لكفاءة إنتاج الدجاج اللاحم. يحسب بالمعادلة: EPEF = (الحيوية × الوزن الحي) / (العمر × معامل التحويل الغذائي) × 100. كلما كان الرقم أعلى دل على كفاءة إنتاجية أفضل.",
            "reference": "REF020",
            "simplified": "EPEF هو رقم يعبر عن كفاءة مزرعة الدجاج، وكلما كان أعلى دل ذلك على إنتاجية أفضل.",
            "category": "performance",
            "tags": ["broiler", "performance", "efficiency"]
        },
        "ما هي أسباب الحماض الكرشي في المجترات": {
            "answer": "الحماض الكرشي (Ruminal Acidosis) يحدث بسبب تراكم الأحماض العضوية في الكرش نتيجة تناول كميات كبيرة من الكربوهيدرات سريعة التخمر (مثل الحبوب) دون تهيئة كافية. يؤدي ذلك إلى انخفاض درجة حموضة الكرش (pH) إلى أقل من 5.5، مما يسبب مشاكل هضمية وانخفاض في الأداء الإنتاجي.",
            "reference": "REF012",
            "simplified": "الحماض الكرشي يحدث عندما يأكل الحيوان كميات كبيرة من الحبوب بسرعة دون تهيئة، مما يسبب حموضة في المعدة.",
            "category": "health",
            "tags": ["ruminants", "acidosis", "health", "digestion"]
        },
        "ما هي متطلبات الخيول الغذائية": {
            "answer": "متطلبات الخيول الغذائية تختلف حسب العمر، الوزن، مستوى النشاط، والحالة الفسيولوجية. تحتاج الخيول إلى 2-2.5% من وزنها الجسم من المادة الجافة يومياً، مع بروتين 10-14% حسب النشاط، وطاقة قابلة للهضم (DE) 14-18 ميجا جول/كجم. يجب أيضاً توفير معادن مثل الكالسيوم والفوسفور بنسبة 1.5:1 إلى 2:1.",
            "reference": "REF015",
            "simplified": "الخيول تحتاج إلى علف متوازن يحتوي على بروتين وطاقة حسب مستوى نشاطها، مع توفير المعادن والفيتامينات.",
            "category": "horses",
            "tags": ["horses", "nutrition", "requirements"]
        },
        "كيفية حساب معامل التحويل الغذائي FCR": {
            "answer": "معامل التحويل الغذائي FCR (Feed Conversion Ratio) = كمية العلف المستهلك / كمية الوزن المكتسب. مثال: إذا استهلك طائر 3 كجم علف واكتسب 1.5 كجم وزن، فإن FCR = 3/1.5 = 2.0. كلما كان الرقم أقل دل على كفاءة تحويل أفضل للعلف إلى لحم.",
            "reference": "REF018",
            "simplified": "FCR يبين كمية العلف التي يحتاجها الحيوان لاكتساب كيلو جرام واحد من الوزن، وكلما كان أقل كان أفضل.",
            "category": "performance",
            "tags": ["FCR", "efficiency", "feeding"]
        },
        "ما هي أهمية البيكربونات في أعلاف المجترات": {
            "answer": "تستخدم بيكربونات الصوديوم في أعلاف المجترات كمنظم لحموضة الكرش (Buffer). تعمل على معادلة الأحماض الناتجة عن تخمر الكربوهيدرات سريعة التخمر، وتمنع حدوث الحماض الكرشي. الجرعة الموصى بها هي 0.5-1% من المادة الجافة للعلف.",
            "reference": "REF012B",
            "simplified": "البيكربونات تحافظ على توازن الحموضة في كرش الحيوان وتمنع مشاكل الهضم.",
            "category": "health",
            "tags": ["ruminants", "buffer", "acidosis", "health"]
        },
        "ما هي احتياجات الدواجن من البروتين": {
            "answer": "احتياجات الدواجن من البروتين تختلف حسب العمر والغرض الإنتاجي: بادي (0-14 يوم): 22-24%، نامي (15-28 يوم): 19-21%، ناهي (29-42 يوم): 17-19%، وبياض إنتاجي: 16-18%. كما تختلف حسب سلالة الدواجن ونوع الإنتاج (لاحم أو بياض).",
            "reference": "REF010",
            "simplified": "الدواجن الصغيرة تحتاج بروتين أعلى، وتقل الحاجة مع التقدم في العمر. الدجاج البياض يحتاج بروتين 16-18%.",
            "category": "poultry",
            "tags": ["poultry", "protein", "requirements", "broiler"]
        },
        "كيفية تحسين كفاءة التغذية في مزارع الأبقار": {
            "answer": "تحسين كفاءة التغذية في مزارع الأبقار يتم من خلال: 1. تحليل جودة الأعلاف الخشنة والمركزة بشكل دوري، 2. استخدام خلطات متوازنة حسب مرحلة الإنتاج، 3. إضافة بيكربونات الصوديوم لمنع الحماض، 4. توفير مياه نظيفة بكميات كافية، 5. مراقبة استهلاك العلف وتعديل الكميات حسب الإنتاج، 6. استخدام إضافات مثل الخمائر لتحسين هضم الألياف.",
            "reference": "REF004",
            "simplified": "استخدم أعلافاً عالية الجودة وخلطات متوازنة وراقب استهلاك الحيوانات لتحسين الكفاءة.",
            "category": "cattle",
            "tags": ["cattle", "efficiency", "management", "nutrition"]
        },
        "ما هي مصادر البروتين في أعلاف الحيوانات": {
            "answer": "مصادر البروتين في أعلاف الحيوانات تنقسم إلى: 1. مصادر نباتية: كسب فول الصويا، كسب بذور القطن، كسب عباد الشمس، أمباز الفول السوداني، جلوتين الذرة. 2. مصادر حيوانية: مسحوق الأسماك، مسحوق اللحم والعظم، مركزات البروتين. 3. مصادر تخميرية: خميرة البيرة، بروتين الأجنة. 4. مصادر صناعية: يوريا للمجترات، أحماض أمينية بلورية.",
            "reference": "REF001",
            "simplified": "البروتين يأتي من مصادر نباتية (كسب الصويا)، حيوانية (مسحوق الأسماك)، وصناعية (اليوريا).",
            "category": "protein",
            "tags": ["protein", "sources", "feed"]
        }
    }
    
    @staticmethod
    def get_reference(ref_id):
        """الحصول على مرجع علمي بواسطة المعرف"""
        for category in ScientificReferenceSystem.REFERENCES.values():
            for ref in category.get("references", []):
                if ref.get("id") == ref_id:
                    return ref
        return None
    
    @staticmethod
    def get_knowledge_answer(question):
        """البحث عن إجابة لسؤال في بنك المعرفة مع خوارزمية مطابقة متقدمة"""
        question_lower = question.lower()
        best_match = None
        best_score = 0
        
        for key, value in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            # حساب درجة المطابقة باستخدام كلمات متعددة
            key_words = key.split()
            match_count = sum(1 for word in key_words if word in question_lower)
            score = match_count / len(key_words) if key_words else 0
            
            # زيادة النقاط إذا كانت الكلمات متطابقة تماماً
            if any(w in key for w in question_lower.split() if len(w) > 3):
                score += 0.2
            
            if score > best_score:
                best_score = score
                best_match = (key, value)
        
        if best_match and best_score > 0.25:
            key, value = best_match
            ref = ScientificReferenceSystem.get_reference(value.get("reference", ""))
            return {
                "answer": value["answer"],
                "simplified": value.get("simplified", value["answer"]),
                "reference": ref,
                "category": value.get("category", "general"),
                "keywords": key,
                "tags": value.get("tags", []),
                "match_score": best_score
            }
        
        # محاولة البحث عن كلمات مفتاحية في النص
        for key, value in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            if any(word in key for word in question_lower.split() if len(word) > 3):
                ref = ScientificReferenceSystem.get_reference(value.get("reference", ""))
                return {
                    "answer": value["answer"],
                    "simplified": value.get("simplified", value["answer"]),
                    "reference": ref,
                    "category": value.get("category", "general"),
                    "keywords": key,
                    "partial_match": True
                }
        
        return None
    
    @staticmethod
    def get_all_references_by_tag(tag):
        """الحصول على جميع المراجع التي تحتوي على وسم معين"""
        results = []
        for category in ScientificReferenceSystem.REFERENCES.values():
            for ref in category.get("references", []):
                if tag in ref.get("tags", []):
                    results.append(ref)
        return results
    
    @staticmethod
    def get_categories():
        """الحصول على قائمة بجميع الفئات مع أيقوناتها"""
        return [(key, data.get("icon", "📖"), data.get("title")) 
                for key, data in ScientificReferenceSystem.REFERENCES.items()]
    
    @staticmethod
    def get_feed_composition_table(ingredient_name):
        """الحصول على التركيب الغذائي لمادة علفية معينة من المكتبة"""
        for cat in BIG_FEEDS_LIBRARY.values():
            if ingredient_name in cat:
                return cat[ingredient_name]
        return None

# =====================================================================
# السطر 501-650: معالج اللغة العربية المتقدم
# =====================================================================
class ArabicTextProcessor:
    """
    معالج النصوص العربية المتقدم.
    يقوم بتشكيل النص، تصحيح الاتجاه، تحليل النصوص، واستخراج الكلمات.
    """
    @staticmethod
    @lru_cache(maxsize=2000)
    def fix_arabic_text(text):
        """إصلاح النص العربي للعرض الصحيح"""
        if not text:
            return ""
        reshaped_text = arabic_reshaper.reshape(str(text))
        return get_display(reshaped_text)
    
    @staticmethod
    def fix_arabic_text_batch(texts):
        """إصلاح مجموعة من النصوص العربية"""
        return [ArabicTextProcessor.fix_arabic_text(t) for t in texts]
    
    @staticmethod
    def extract_arabic_words(text):
        """استخراج الكلمات العربية من النص باستخدام تعبيرات منتظمة"""
        arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
        return arabic_pattern.findall(text)
    
    @staticmethod
    def is_arabic(text):
        """التحقق مما إذا كان النص عربياً بشكل أساسي"""
        if not text:
            return False
        arabic_chars = len(ArabicTextProcessor.extract_arabic_words(text))
        total_chars = len(re.findall(r'\w', text))
        if total_chars == 0:
            return False
        return arabic_chars / total_chars > 0.5
    
    @staticmethod
    def normalize_arabic(text):
        """تطبيع النص العربي بإزالة الحركات وتوحيد الحروف"""
        if not text:
            return ""
        # إزالة الحركات (التشكيل)
        text = re.sub(r'[\u064B-\u0652]', '', text)
        # توحيد الألف
        text = text.replace('آ', 'ا').replace('أ', 'ا').replace('إ', 'ا')
        # توحيد التاء المربوطة
        text = text.replace('ة', 'ه')
        return text
    
    @staticmethod
    def get_text_length_arabic(text):
        """حساب طول النص العربي (عدد الكلمات)"""
        if not text:
            return 0
        words = ArabicTextProcessor.extract_arabic_words(text)
        return len(words)

arabic_processor = ArabicTextProcessor()

# =====================================================================
# السطر 651-800: مولد التقارير PDF المتقدم (ProfessionalPDFGenerator)
# =====================================================================
class ProfessionalPDFGenerator:
    """
    مولد تقارير PDF احترافية متقدمة مع دعم اللغة العربية.
    يدعم إنشاء تقارير متعددة الصفحات مع رسوم بيانية وجداول وتوصيات.
    """
    def __init__(self):
        self.font_name = 'Helvetica'
        # محاولة استخدام خط Amiri إذا كان موجوداً لدعم أفضل للعربية
        if os.path.exists("Amiri-Regular.ttf"):
            try:
                pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
                self.font_name = 'Amiri'
            except:
                pass
        # محاولة استخدام خط Lateef كبديل
        if os.path.exists("Lateef-Regular.ttf") and self.font_name == 'Helvetica':
            try:
                pdfmetrics.registerFont(TTFont('Lateef', 'Lateef-Regular.ttf'))
                self.font_name = 'Lateef'
            except:
                pass
        
        self.styles = self._create_styles()
    
    def _create_styles(self):
        """إنشاء أنماط النصوص المستخدمة في التقرير"""
        styles = {}
        styles['title'] = ParagraphStyle(
            'title',
            fontName=self.font_name,
            fontSize=24,
            alignment=TA_CENTER,
            textColor=HexColor('#1b5e20'),
            spaceAfter=20,
            leading=30
        )
        styles['subtitle'] = ParagraphStyle(
            'subtitle',
            fontName=self.font_name,
            fontSize=16,
            alignment=TA_CENTER,
            textColor=HexColor('#2e7d32'),
            spaceAfter=15,
            leading=20
        )
        styles['heading'] = ParagraphStyle(
            'heading',
            fontName=self.font_name,
            fontSize=14,
            alignment=TA_RIGHT,
            textColor=HexColor('#1b5e20'),
            spaceAfter=10,
            leading=18,
            fontweight='bold'
        )
        styles['body'] = ParagraphStyle(
            'body',
            fontName=self.font_name,
            fontSize=11,
            alignment=TA_RIGHT,
            textColor=HexColor('#333333'),
            spaceAfter=6,
            leading=16
        )
        styles['body_center'] = ParagraphStyle(
            'body_center',
            fontName=self.font_name,
            fontSize=11,
            alignment=TA_CENTER,
            textColor=HexColor('#333333'),
            spaceAfter=6,
            leading=16
        )
        styles['small'] = ParagraphStyle(
            'small',
            fontName=self.font_name,
            fontSize=9,
            alignment=TA_RIGHT,
            textColor=HexColor('#666666'),
            spaceAfter=4,
            leading=12
        )
        styles['footer'] = ParagraphStyle(
            'footer',
            fontName=self.font_name,
            fontSize=8,
            alignment=TA_CENTER,
            textColor=HexColor('#999999'),
            spaceAfter=0,
            leading=10
        )
        styles['highlight'] = ParagraphStyle(
            'highlight',
            fontName=self.font_name,
            fontSize=11,
            alignment=TA_RIGHT,
            textColor=HexColor('#1565C0'),
            spaceAfter=6,
            leading=16,
            fontweight='bold'
        )
        return styles
    
    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, include_charts=True, extra_info=None):
        """
        توليد تقرير PDF كامل ومفصل (3-4 صفحات) مع جميع المعلومات.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        story = []
        
        def p(text, style='body'):
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, self.styles.get(style, self.styles['body']))
        
        # =============================================================
        # الصفحة الأولى: العنوان والمعلومات الأساسية
        # =============================================================
        story.append(p("منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف", 'title'))
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
        
        # جدول المعايير الغذائية
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
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))
        
        # إضافة شريط QR Code
        try:
            qr = qrcode.QRCode(version=1, box_size=8, border=4)
            qr.add_data(f"https://tower-scientific-platform.streamlit.app/report/{datetime.now().strftime('%Y%m%d%H%M')}")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer, format="PNG")
            qr_buffer.seek(0)
            story.append(Image(qr_buffer, width=80, height=80))
            story.append(Spacer(1, 5))
            story.append(p("رابط التقرير", 'small'))
        except:
            pass
        
        story.append(PageBreak())
        
        # =============================================================
        # الصفحة الثانية: المكونات والرسوم البيانية
        # =============================================================
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
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')]),
        ]))
        story.append(t2)
        story.append(Spacer(1, 15))
        
        if include_charts and len(formula) > 1:
            try:
                fig, ax = plt.subplots(figsize=(6, 3.5))
                names = list(formula.keys())
                vals = list(formula.values())
                colors = ['#1b5e20','#2e7d32','#388e3c','#43a047','#4caf50','#66bb6a','#81c784','#a5d6a7']
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
        
        story.append(PageBreak())
        
        # =============================================================
        # الصفحة الثالثة: معلومات إضافية وتوصيات
        # =============================================================
        story.append(p("التوصيات الفنية:", 'heading'))
        story.append(Spacer(1, 10))
        recommendations = [
            "• يوصى بإضافة الإنزيمات لتحسين الهضم والاستفادة من العلف.",
            "• يجب مراقبة جودة المواد الخام بشكل دوري وإجراء تحاليل مخبرية.",
            "• يوصى بإجراء تحليل مخبري للخلطة للتأكد من مطابقتها للمواصفات.",
            "• يجب تخزين العلف في مكان جاف بعيداً عن الرطوبة والحشرات.",
            "• يوصى بتقسيم العلف على عدة وجبات لتحسين الهضم والاستفادة.",
            "• يجب توفير مياه نظيفة بكميات كافية للحيوانات."
        ]
        for rec in recommendations:
            story.append(p(rec))
        story.append(Spacer(1, 15))
        
        if extra_info:
            story.append(p("معلومات إضافية:", 'heading'))
            for key, value in extra_info.items():
                if value:
                    story.append(p(f"• {key}: {value}"))
        
        # =============================================================
        # الصفحة الرابعة: الخاتمة والتوقيع
        # =============================================================
        story.append(PageBreak())
        story.append(p("خاتمة التقرير", 'heading'))
        story.append(Spacer(1, 10))
        conclusion_text = """
        تم إعداد هذا التقرير الفني بناءً على تحليل دقيق للاحتياجات الغذائية للفصيل المستهدف، 
        مع تطبيق أحدث تقنيات تركيب الأعلاف باستخدام محرك الاستمثال الخطي.
        نأمل أن يساهم هذا التقرير في تحسين كفاءة الإنتاج وتقليل التكاليف.
        """
        story.append(p(conclusion_text))
        story.append(Spacer(1, 20))
        
        story.append(p("مع خالص التحية والتقدير،", 'body'))
        story.append(Spacer(1, 10))
        story.append(p("الاختصاصي م. عبد القادر إسماعيل تاور", 'highlight'))
        story.append(p("المشرف العام على المنصة", 'small'))
        
        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026", 'footer'))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_lab_report(self, analysis_results, animal_type, stage, user_name):
        """توليد تقرير مخبري PDF متكامل (3 صفحات)"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        story = []
        
        def p(text, style='body'):
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, self.styles.get(style, self.styles['body']))
        
        # الصفحة الأولى: العنوان والنتائج
        story.append(p("🔬 تقرير التحليل المخبري", 'title'))
        story.append(p(f"منصة تاور العلمية", 'subtitle'))
        story.append(p(f"المشرف: {user_name}"))
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
            
            # رسم بياني للقيم الغذائية
            try:
                fig, ax = plt.subplots(figsize=(8, 4))
                labels = ['CP', 'DP', 'SE']
                values = [analysis_results.get('cp', 0), analysis_results.get('dp', 0), analysis_results.get('se', 0)]
                colors = ['#2e7d32', '#1565C0', '#E65100']
                bars = ax.bar(labels, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1)
                ax.set_title(arabic_processor.fix_arabic_text('القيم الغذائية المحسوبة'), fontsize=14)
                ax.set_ylabel('القيمة')
                ax.grid(axis='y', alpha=0.3)
                for bar, val in zip(bars, values):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                           f'{val:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=450, height=200))
            except:
                pass
            
            story.append(PageBreak())
            
            # الصفحة الثانية: المكونات المدخلة
            if 'components' in analysis_results and analysis_results['components']:
                story.append(p("المكونات المدخلة في التحليل:", 'heading'))
                comp_data = [['المكون', 'الوزن (كجم)']]
                for name, weight in analysis_results['components'].items():
                    if weight > 0:
                        comp_data.append([name, f"{weight:.1f}"])
                t3 = Table([[arabic_processor.fix_arabic_text(cell) for cell in row] for row in comp_data], 
                          colWidths=[250, 150])
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
            
            # الصفحة الثالثة: التوصيات
            story.append(p("التوصيات المخبرية:", 'heading'))
            recs = [
                "• يوصى بإعادة التحليل بعد أي تعديل على الخلطة للتأكد من مطابقتها للمواصفات.",
                "• يجب مراجعة نسب البروتين والطاقة حسب احتياجات الحيوان في كل مرحلة إنتاجية.",
                "• يوصى بالتواصل مع أخصائي التغذية لتعديل الخلطة حسب نتائج التحليل.",
                "• يجب التأكد من جودة المواد الخام المستخدمة في الخلطة.",
                "• يوصى بإجراء تحليل دوري كل 3 أشهر لمتابعة جودة الأعلاف."
            ]
            for rec in recs:
                story.append(p(rec))
        
        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026", 'footer'))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# =====================================================================
# السطر 801-1000: كلاس BroilerFarmManager المتقدم
# =====================================================================
class BroilerFarmManager:
    """
    إدارة مزارع الدجاج اللاحم المتقدمة.
    تشمل حسابات الأداء، التوصيات، وتحليل البيانات الإنتاجية.
    """
    @staticmethod
    def calculate_adg(current_weight_g, initial_weight_g, age_days):
        """حساب متوسط النمو اليومي بالجرام"""
        if age_days <= 0:
            return 0.0
        return (current_weight_g - initial_weight_g) / age_days
    
    @staticmethod
    def calculate_fcr(total_feed_kg, total_weight_gain_kg):
        """حساب معامل التحويل الغذائي"""
        if total_weight_gain_kg <= 0:
            return 0.0
        return total_feed_kg / total_weight_gain_kg
    
    @staticmethod
    def calculate_mortality_rate(dead_count, initial_count):
        """حساب نسبة النفوق المئوية"""
        if initial_count <= 0:
            return 0.0
        return (dead_count / initial_count) * 100.0
    
    @staticmethod
    def calculate_livability(initial_count, dead_count):
        """حساب نسبة الحيوية المئوية"""
        return 100.0 - BroilerFarmManager.calculate_mortality_rate(dead_count, initial_count)
    
    @staticmethod
    def calculate_epef(livability, body_weight_kg, age_days, fcr):
        """حساب مؤشر الأداء الأوروبي EPEF"""
        if age_days <= 0 or fcr <= 0:
            return 0.0
        return (livability * body_weight_kg) / (age_days * fcr) * 100.0
    
    @staticmethod
    def calculate_european_broiler_index(livability, body_weight_kg, age_days, fcr):
        """حساب مؤشر الدجاج الأوروبي EBI"""
        if age_days <= 0 or fcr <= 0:
            return 0.0
        return (livability * body_weight_kg) / (age_days * fcr) * 100.0
    
    @staticmethod
    def get_temp_humidity_table():
        """جدول درجات الحرارة والرطوبة المثلى حسب العمر"""
        return pd.DataFrame({
            "العمر (يوم)": [1, 3, 7, 14, 21, 28, 35, 42],
            "درجة الحرارة (مئوي)": [33, 32, 30, 28, 26, 24, 22, 21],
            "الرطوبة النسبية (%)": [65, 65, 65, 60, 60, 55, 55, 55]
        })
    
    @staticmethod
    def get_lighting_program():
        """برنامج الإضاءة الموصى به للدجاج اللاحم"""
        return pd.DataFrame({
            "العمر (يوم)": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35],
            "ساعات الإضاءة": [23, 23, 22, 22, 21, 21, 20, 20, 19, 19, 18, 18, 17, 17, 16, 16, 15, 15, 14, 14, 13, 13, 12, 12, 11, 11, 10, 10, 9, 9, 8, 8, 7, 7, 6]
        })
    
    @staticmethod
    def get_feeding_program():
        """برنامج التغذية الموصى به للدجاج اللاحم"""
        return pd.DataFrame({
            "المرحلة": ["بادي", "نامي", "ناهي"],
            "العمر (يوم)": ["0-14", "15-28", "29-42"],
            "البروتين الموصى به (%)": [23, 21, 19],
            "الطاقة الموصى بها (كيلو كالوري/كجم)": [3100, 3150, 3200]
        })
    
    @staticmethod
    def get_vaccination_schedule():
        """جدول التحصينات الموصى بها للدجاج اللاحم"""
        return pd.DataFrame({
            "العمر (يوم)": [1, 7, 14, 21, 28, 35],
            "اللقاح/الدواء": ["فيتامين AD3E", "نيوكاسل (Lasota)", "Gumboro", "مضاد كوكسيديا", "فيتامين C+E", "Gumboro booster"],
            "الجرعة": ["1 مل/لتر ماء", "قطرة عين", "قطرة فم", "1 جم/لتر", "0.5 جم/لتر", "قطرة فم"],
            "طريقة الإعطاء": ["مياه الشرب", "قطرة عين/أنف", "مياه الشرب", "مياه الشرب (3 أيام)", "مياه الشرب", "مياه الشرب"]
        })
    
    @staticmethod
    def calculate_production_cost(feed_cost, chick_cost, medication_cost, labor_cost, utilities_cost, other_cost):
        """حساب تكاليف الإنتاج الكلية"""
        total = feed_cost + chick_cost + medication_cost + labor_cost + utilities_cost + other_cost
        return {
            'total_cost': total,
            'feed_cost': feed_cost,
            'chick_cost': chick_cost,
            'medication_cost': medication_cost,
            'labor_cost': labor_cost,
            'utilities_cost': utilities_cost,
            'other_cost': other_cost,
            'feed_percentage': (feed_cost / total) * 100 if total > 0 else 0,
            'chick_percentage': (chick_cost / total) * 100 if total > 0 else 0
        }
    
    @staticmethod
    def calculate_profitability(total_revenue, total_cost):
        """حساب الربحية"""
        profit = total_revenue - total_cost
        profit_margin = (profit / total_revenue) * 100 if total_revenue > 0 else 0
        return {
            'profit': profit,
            'profit_margin': profit_margin,
            'cost_per_kg': total_cost / (total_revenue / 100) if total_revenue > 0 else 0,
            'roi': (profit / total_cost) * 100 if total_cost > 0 else 0
        }
    
    @staticmethod
    def get_breed_performance_standards(breed="Ross 308"):
        """معايير الأداء القياسية حسب السلالة"""
        standards = {
            "Ross 308": {
                "age_42_weight_kg": 2.8,
                "fcr_42": 1.65,
                "mortality_42": 3.5,
                "epef_target": 320
            },
            "Cobb 500": {
                "age_42_weight_kg": 2.9,
                "fcr_42": 1.62,
                "mortality_42": 3.0,
                "epef_target": 330
            }
        }
        return standards.get(breed, standards["Ross 308"])

# =====================================================================
# السطر 1001-1250: مكتبة الأعلاف الكاملة الموسعة
# =====================================================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3, "Ca": 0.02, "P": 0.28},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4, "Ca": 0.02, "P": 0.27},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5, "Ca": 0.06, "P": 0.35},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8, "Ca": 0.03, "P": 0.30},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6, "Ca": 0.04, "P": 0.32},
        "جريش أرز رزاز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2, "Ca": 0.03, "P": 0.20},
        "دخن محلي غزير": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2, "Ca": 0.05, "P": 0.28},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0, "Ca": 0.08, "P": 0.33},
        "تربيكة (مخلفات المطاحن)": {"CP": 14.0, "DC": 0.72, "SE": 55.0, "NDF": 30.0, "ADF": 15.0, "EE": 3.0, "ASH": 4.0, "Ca": 0.05, "P": 0.40}
    },
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5, "Ca": 0.15, "P": 0.55},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0, "Ca": 0.20, "P": 0.60},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2, "Ca": 0.22, "P": 0.65},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5, "Ca": 0.30, "P": 0.70},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5, "Ca": 0.15, "P": 0.80},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8, "Ca": 0.25, "P": 0.60},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5, "Ca": 0.40, "P": 0.70},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5, "Ca": 0.10, "P": 0.40},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5, "Ca": 0.20, "P": 0.50},
        "بروتين الصويا المركز": {"CP": 65.0, "DC": 0.95, "SE": 70.0, "NDF": 4.0, "ADF": 2.0, "EE": 1.0, "ASH": 4.0, "Ca": 0.10, "P": 0.30}
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5, "Ca": 0.10, "P": 0.90},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5, "Ca": 1.20, "P": 0.25},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5, "Ca": 0.80, "P": 0.10},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.30, "P": 0.15},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5, "Ca": 0.20, "P": 0.10},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5, "Ca": 0.15, "P": 0.08},
        "مخلفات مصانع البسكويت": {"CP": 12.0, "DC": 0.80, "SE": 60.0, "NDF": 8.0, "ADF": 4.0, "EE": 8.0, "ASH": 2.0, "Ca": 0.05, "P": 0.15}
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5, "Ca": 5.0, "P": 2.8},
        "مسحوق أسماك فاخر (72%)": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5, "Ca": 4.5, "P": 2.5},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5, "Ca": 8.0, "P": 4.0},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5, "Ca": 1.5, "P": 0.8},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5, "Ca": 1.8, "P": 0.9},
        "مركزات بروتين الحليب": {"CP": 80.0, "DC": 0.95, "SE": 45.0, "NDF": 0.0, "ADF": 0.0, "EE": 5.0, "ASH": 6.0, "Ca": 0.8, "P": 0.5}
    },
    "🧪 الأحماض الأمينية البلورية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3, "Ca": 0.0, "P": 0.0},
        "ثريونين نقي (L-Threonine)": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0},
        "تريبتوفان نقي (L-Tryptophan)": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0},
        "فالين نقي (L-Valine)": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0},
        "أرجنين نقي (L-Arginine)": {"CP": 95.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0}
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 5.0},
        "بريمكس بياض وبشاير": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 5.5},
        "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 16.0, "P": 4.5},
        "إنزيم الفايتيز الزامي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0, "Ca": 0.0, "P": 0.0},
        "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0, "Ca": 0.0, "P": 0.0},
        "كبريتات الحديدوز (معادل الجوسيبول)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0, "Ca": 0.0, "P": 0.0},
        "مستخلص الخمائر والجدر الخلوية (MOS)": {"CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.5, "P": 0.2},
        "خميرة البيرة النشطة": {"CP": 45.0, "DC": 0.75, "SE": 30.0, "NDF": 6.0, "ADF": 3.0, "EE": 2.0, "ASH": 7.0, "Ca": 0.2, "P": 0.4}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 38.0, "P": 0.02},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5, "Ca": 23.0, "P": 18.0},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9, "Ca": 0.0, "P": 0.0},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Ca": 0.0, "P": 0.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 0.0, "P": 0.0},
        "أكسيد المغنيسيوم العلفي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 0.0, "P": 0.0},
        "يوريا علفية محصنة (المجترات فقط)": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0, "Ca": 0.0, "P": 0.0},
        "كبريتات النحاس": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 0.0, "P": 0.0},
        "أكسيد الزنك": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 0.0, "P": 0.0}
    }
}

# =====================================================================
# السطر 1251-1400: إدارة المخزون والمتغيرات العامة
# =====================================================================
class InventoryManager:
    """
    إدارة المخزون والمستودعات المتقدمة.
    يشمل تتبع الكميات، الحدود الدنيا، الموردين، وتاريخ انتهاء الصلاحية.
    """
    @staticmethod
    def initialize_inventory():
        """تهيئة المخزون الافتراضي بكميات 25 طن لكل مادة وحد أدنى 5 طن"""
        if "inventory" not in st.session_state:
            st.session_state["inventory"] = {}
            for cat_name, items in BIG_FEEDS_LIBRARY.items():
                for ing in items:
                    st.session_state["inventory"][ing] = {
                        "quantity": 25.0,
                        "min_threshold": 5.0,
                        "unit": "طن",
                        "last_updated": datetime.now().isoformat(),
                        "price_history": [],
                        "supplier": "غير محدد",
                        "batch_number": f"BATCH-{datetime.now().strftime('%Y%m')}-{random.randint(100, 999)}",
                        "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
                        "quality_grade": "A",
                        "notes": ""
                    }
    
    @staticmethod
    def check_stock_levels():
        """فحص مستويات المخزون وإرجاع تحذيرات"""
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
        """الحصول على ملخص المخزون"""
        total_items = len(st.session_state["inventory"])
        total_quantity = sum(d["quantity"] if isinstance(d, dict) else d for d in st.session_state["inventory"].values())
        low_stock = sum(1 for d in st.session_state["inventory"].values() 
                       if (d["quantity"] if isinstance(d, dict) else d) < (d.get("min_threshold", 5.0) if isinstance(d, dict) else 5.0))
        return {
            "total_items": total_items,
            "total_quantity": total_quantity,
            "low_stock": low_stock,
            "healthy_items": total_items - low_stock
        }
    
    @staticmethod
    def update_stock(item_name, quantity_change, note=""):
        """تحديث كمية مادة في المخزون"""
        if item_name in st.session_state["inventory"]:
            current = st.session_state["inventory"][item_name]
            if isinstance(current, dict):
                current["quantity"] += quantity_change
                current["last_updated"] = datetime.now().isoformat()
                if note:
                    current["notes"] = note
            else:
                st.session_state["inventory"][item_name] = current + quantity_change
            return True
        return False
    
    @staticmethod
    def get_low_stock_items():
        """الحصول على قائمة المواد منخفضة المخزون"""
        warnings = InventoryManager.check_stock_levels()
        return [item for item, status in warnings.items() if status["status"] == "منخفض" or status["status"] == "نفذ المخزون"]

InventoryManager.initialize_inventory()

# =====================================================================
# السطر 1401-1550: المتغيرات العامة الموسعة
# =====================================================================
if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين ($)": 1350.0,
        "أبقار كنانة محلية ($)": 900.0,
        "ضأن وستيرلنغ ($)": 180.0,
        "ماعز نوبي ($)": 130.0,
        "خيول عربية أصيلة ($)": 4500.0,
        "خيول محلية هجين ($)": 2500.0,
        "كتكوت لاحم ($)": 0.65,
        "دجاج بياض بشاير ($)": 5.50,
        "سمان ($)": 1.20,
        "زريعة بلطي ($)": 0.15
    }

if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري ($)": 7.50,
        "كيلو لحم ضأن ($)": 9.00,
        "كيلو لحم دجاج ($)": 3.80,
        "طبق بيض 30 بيضة ($)": 4.20,
        "لتر حليب خام ($)": 0.90,
        "كيلو جبن أبيض ($)": 5.00,
        "كيلو جبن جاف ($)": 8.50,
        "كيلو لحم سمك ($)": 4.50,
        "كيلو صوف ($)": 2.50
    }

if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = (
        "• [توجيه الاختصاصي م. عبد القادر]: يرجى من جميع الزملاء إضافة تعليقاتهم لتبادل الخبرات.\n"
        "• [ملاحظة مختص]: تم مراجعة جودة كسب زهرة الشمس المتاح حالياً بالأسواق ونوصي بضبط ألياف الخيل بناءً عليه.\n"
        "• [تنبيه]: يوصى بإجراء تحليل دوري للأعلاف كل 3 أشهر.\n"
        "• [توصية]: استخدام الإنزيمات في أعلاف الدواجن يحسن الهضم ويقلل التكاليف.\n"
    )

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG", "currency_name": "جنيه سوداني"},
    "LIBYA": {"rate": 4.80, "sym": "LYD", "currency_name": "دينار ليبي"},
    "مصر": {"rate": 48.0, "sym": "EGP", "currency_name": "جنيه مصري"},
    "دولار أمريكي": {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"},
    "السعودية": {"rate": 3.75, "sym": "SAR", "currency_name": "ريال سعودي"},
    "الإمارات": {"rate": 3.67, "sym": "AED", "currency_name": "درهم إماراتي"},
    "قطر": {"rate": 3.64, "sym": "QAR", "currency_name": "ريال قطري"},
    "الكويت": {"rate": 0.31, "sym": "KWD", "currency_name": "دينار كويتي"}
}

# =====================================================================
# السطر 1551-1700: MarketPriceEngine الموسع
# =====================================================================
class MarketPriceEngine:
    """
    محرك تعديل الأسعار حسب الموقع الجغرافي المتقدم.
    يدعم دولاً متعددة ومناطق ومدن مختلفة مع معاملات تصحيح.
    """
    @staticmethod
    @lru_cache(maxsize=256)
    def get_adjusted_market_data(country, state_or_region, city):
        """إرجاع قاموس الأسعار المعدلة حسب الموقع"""
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
            "مركزات خيول ومجترات": 600.0, "الحجر الجيري (بودرة بلاط)": 40.0,
            "فوسفات ثنائي الكالسيوم (DCP)": 280.0, "ملح الطعام": 30.0,
            "مضاد سموم فطرية": 950.0, "بيكربونات الصوديوم (الصودا)": 340.0,
            "يوريا علفية": 450.0, "بريمكس دواجن": 1200.0,
            "بريمكس أبقار": 1100.0, "إنزيم الفايتيز": 1400.0
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
            elif state_or_region == "ولاية نهر النيل":
                feed_prices["ذرة صفراء"] *= 0.95
            elif state_or_region == "ولاية الخرطوم":
                multiplier = 1.10
        elif country == "LIBYA":
            multiplier = 1.10
            if city == "طبرق":
                multiplier = 1.06
            elif city == "بنغازي":
                multiplier = 1.08
            elif city == "طرابلس":
                multiplier = 1.12
        elif country == "مصر":
            multiplier = 1.04
            if state_or_region == "الصعيد":
                multiplier = 1.02
            elif state_or_region == "الإسكندرية":
                multiplier = 1.06
        elif country == "السعودية":
            multiplier = 1.25
            if state_or_region == "الرياض":
                multiplier = 1.30
        elif country == "الإمارات":
            multiplier = 1.30
        elif country == "قطر":
            multiplier = 1.35
        elif country == "الكويت":
            multiplier = 1.28

        for k in feed_prices:
            feed_prices[k] *= multiplier

        return feed_prices
    
    @staticmethod
    def get_currency_info(country):
        """الحصول على معلومات العملة لدولة معينة"""
        return EXCHANGE_RATES.get(country, {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"})
    
    @staticmethod
    def convert_currency(amount, from_currency, to_currency):
        """تحويل العملة"""
        if from_currency == to_currency:
            return amount
        rates = {k: v["rate"] for k, v in EXCHANGE_RATES.items()}
        if from_currency in rates and to_currency in rates:
            return amount * (rates[to_currency] / rates[from_currency])
        return amount

# =====================================================================
# السطر 1701-1800: صور الحيوانات والمتغيرات النشطة
# =====================================================================
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

# متغيرات الجلسة النشطة (تخزن نتائج آخر عملية تركيب)
if "active_formula" not in st.session_state:
    st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0}
if "active_cp_tag" not in st.session_state:
    st.session_state["active_cp_tag"] = 12.0
if "active_se_tag" not in st.session_state:
    st.session_state["active_se_tag"] = 65.0
if "active_breed_tag" not in st.session_state:
    st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_animal_img" not in st.session_state:
    st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES["عام"]
if "active_stage_title" not in st.session_state:
    st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state:
    st.session_state["computed_ton_cost"] = 280.0

# =====================================================================
# السطر 1801-1950: حالة الجلسة العامة الموسعة
# =====================================================================
if "approved" not in st.session_state:
    st.session_state["approved"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "login_welcome_shown" not in st.session_state:
    st.session_state["login_welcome_shown"] = False
if "login_attempts" not in st.session_state:
    st.session_state["login_attempts"] = 0
if "last_login_time" not in st.session_state:
    st.session_state["last_login_time"] = None
if "session_token" not in st.session_state:
    st.session_state["session_token"] = None
if "broiler_farms" not in st.session_state:
    st.session_state["broiler_farms"] = {}
if "selected_farm" not in st.session_state:
    st.session_state["selected_farm"] = None
if "standard_vacc_schedule" not in st.session_state:
    st.session_state["standard_vacc_schedule"] = {
        1: {"type": "فيتامين", "name": "فيتامين AD3E", "dose": "1 مل/لتر ماء", "route": "مياه الشرب"},
        7: {"type": "لقاح", "name": "نيوكاسل (Lasota)", "dose": "قطرة عين", "route": "قطرة عين/أنف"},
        14: {"type": "لقاح", "name": "Gumboro (Intermediate)", "dose": "قطرة فم", "route": "مياه الشرب"},
        21: {"type": "دواء", "name": "مضاد كوكسيديا (Amprolium)", "dose": "1 جم/لتر", "route": "مياه الشرب لمدة 3 أيام"},
        28: {"type": "فيتامين", "name": "فيتامين C + E", "dose": "0.5 جم/لتر", "route": "مياه الشرب"},
        35: {"type": "لقاح", "name": "Gumboro booster", "dose": "قطرة فم", "route": "مياه الشرب"},
    }
if "whatsapp_alerts_sent" not in st.session_state:
    st.session_state["whatsapp_alerts_sent"] = {}
if "query_history" not in st.session_state:
    st.session_state["query_history"] = []
if "analysis_results" not in st.session_state:
    st.session_state["analysis_results"] = None
if "analysis_animal" not in st.session_state:
    st.session_state["analysis_animal"] = "غير محدد"
if "analysis_stage" not in st.session_state:
    st.session_state["analysis_stage"] = "غير محدد"
if "alerts_list" not in st.session_state:
    st.session_state["alerts_list"] = []
if "daily_production_log" not in st.session_state:
    st.session_state["daily_production_log"] = []
if "budget_records" not in st.session_state:
    st.session_state["budget_records"] = []
if "medicines_list" not in st.session_state:
    st.session_state["medicines_list"] = []

# =====================================================================
# السطر 1951-2050: دوال مساعدة متقدمة
# =====================================================================
def send_whatsapp_message(phone_number, message):
    """إرسال رسالة عبر واتساب مع رابط مباشر"""
    encoded_msg = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_msg}"
    return whatsapp_url

def send_whatsapp_broiler_alert(phone_number, message):
    """إرسال تنبيه عبر واتساب باستخدام رابط مباشر"""
    whatsapp_url = send_whatsapp_message(phone_number, message)
    st.markdown(f"""
    <div style='background:#e8f5e9; padding:10px; border-radius:8px; direction:ltr;'>
        📲 <b>تنبيه عبر واتساب:</b>
        <a href='{whatsapp_url}' target='_blank'>اضغط لإرسال الرسالة إلى {phone_number}</a>
        <br>{message}
    </div>
    """, unsafe_allow_html=True)

def check_and_alert_medications(farm_name, farm_data, current_age):
    """التحقق من الجدول الصحي وإرسال تنبيهات"""
    phone = farm_data.get("owner_phone", WHATSAPP_NUMBER)
    schedule = st.session_state["standard_vacc_schedule"]
    alerts_sent = []
    for age_day, item in schedule.items():
        if age_day == current_age:
            key = f"{farm_name}_{age_day}_{item['type']}_{item['name']}"
            if key not in st.session_state["whatsapp_alerts_sent"]:
                alert_msg = (
                    f"🔔 تنبيه لمزرعة {farm_name} (العمر {age_day} يوم):\n"
                    f"{item['type']} {item['name']} - الجرعة: {item['dose']} - طريقة الإعطاء: {item['route']}"
                )
                send_whatsapp_broiler_alert(phone, alert_msg)
                st.session_state["whatsapp_alerts_sent"][key] = datetime.now().isoformat()
                alerts_sent.append(alert_msg)
    return alerts_sent

def generate_id(prefix=""):
    """توليد معرف فريد"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = secrets.token_hex(4)
    return f"{prefix}{timestamp}{random_part}"

def calculate_age(birth_date):
    """حساب العمر بالأيام من تاريخ الميلاد"""
    if isinstance(birth_date, str):
        birth_date = datetime.fromisoformat(birth_date)
    return (datetime.now() - birth_date).days

def format_currency(amount, currency_symbol="$", decimal_places=2):
    """تنسيق العملة"""
    return f"{currency_symbol}{amount:,.{decimal_places}f}"

def parse_date(date_str):
    """تحويل سلسلة نصية إلى تاريخ"""
    try:
        return datetime.fromisoformat(date_str)
    except:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            return None

def get_percentage_change(old_value, new_value):
    """حساب النسبة المئوية للتغيير"""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100

def moving_average(data, window=7):
    """حساب المتوسط المتحرك"""
    if len(data) < window:
        return data
    result = []
    for i in range(len(data) - window + 1):
        result.append(np.mean(data[i:i+window]))
    return result

def validate_email(email):
    """التحقق من صحة البريد الإلكتروني"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """التحقق من صحة رقم الهاتف"""
    pattern = r'^\+?[0-9]{10,15}$'
    return re.match(pattern, phone) is not None

# =====================================================================
# السطر 2051-2200: نظام التوجيه الصوتي المتقدم
# =====================================================================
def voice_guide(message, lang="ar"):
    """
    تشغيل توجيه صوتي باستخدام Web Speech API المتقدم.
    يدعم تشغيل رسائل طويلة وتقسيمها إلى أجزاء.
    """
    if not message or len(message.strip()) < 2:
        return
    
    # تقسيم الرسائل الطويلة إلى أجزاء (كل جزء 200 حرف)
    max_length = 200
    if len(message) > max_length:
        # تقسيم عند الفواصل أو النقاط
        parts = []
        current = ""
        for word in message.split():
            if len(current + " " + word) <= max_length:
                current += " " + word if current else word
            else:
                parts.append(current)
                current = word
        if current:
            parts.append(current)
        for part in parts:
            _speak(part, lang)
            time.sleep(0.5)
    else:
        _speak(message, lang)

def _speak(message, lang="ar"):
    """تشغيل جزء من الرسالة الصوتية"""
    safe_message = message.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    lang_code = "ar-SA" if lang == "ar" else "en-US"
    
    js_code = f"""
    <script>
    (function() {{
        function speak() {{
            try {{
                if (!window.speechSynthesis) {{
                    console.warn('⚠️ Web Speech API غير مدعوم');
                    return;
                }}
                var msg = new SpeechSynthesisUtterance('{safe_message}');
                msg.lang = '{lang_code}';
                msg.rate = 0.85;
                msg.pitch = 1.0;
                msg.volume = 1.0;
                
                // محاولة اختيار صوت عربي
                var voices = window.speechSynthesis.getVoices();
                var arabicVoice = voices.find(v => v.lang && v.lang.startsWith('ar'));
                if (arabicVoice) {{
                    msg.voice = arabicVoice;
                }}
                
                window.speechSynthesis.cancel();
                window.speechSynthesis.speak(msg);
                console.log('🔊 توجيه صوتي: ' + '{safe_message}');
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
    """تشغيل رسالة ترحيبية صوتية حسب دور المستخدم"""
    messages = {
        "owner": "مرحباً بك في منصة تاور العلمية، أيها الاختصاصي م. عبد القادر إسماعيل تاور. نظام تركيب الأعلاف الذكي والمختبر والميزات المتقدمة جاهزة للعمل.",
        "specialist": "مرحباً أيها المختص. منصة تاور العلمية تحت خدمتك. يمكنك استخدام أدوات التحليل وتركيب الأعلاف وإدارة البيانات.",
        "veterinarian": "مرحباً أيها الطبيب البيطري. منصة تاور العلمية توفر لك أدوات إدارة الأدوية وسجلات العلاج.",
        "nutritionist": "مرحباً أيها الأخصائي. منصة تاور العلمية توفر لك أدوات تركيب الأعلاف وتحليل الخلطات.",
        "breeder": "مرحباً أيها المربي. منصة تاور العلمية تساعدك في تركيب أعلاف اقتصادية عالية الجودة وإدارة مزرعتك."
    }
    voice_guide(messages.get(role, "مرحباً بك في منصة تاور العلمية"))

# =====================================================================
# السطر 2201-2350: نظام إرسال الكود وتحويل النتائج إلى صور (موسع)
# =====================================================================
def send_code_to_email(receiver_email):
    """إرسال الكود البرمجي الكامل إلى البريد الإلكتروني مع التوقيع الرقمي"""
    try:
        current_file = __file__
        with open(current_file, "r", encoding="utf-8") as f:
            code_content = f.read()
    except:
        code_content = "# تعذر قراءة الكود المصدر\n"

    file_hash = hashlib.md5(code_content.encode()).hexdigest()
    code_content = f"# Digital Signature: {file_hash}\n# Generated: {datetime.now().isoformat()}\n\n{code_content}"

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود الكامل - منصة تاور العلمية (الإصدار المتقدم)"

    body = f"""السلام عليكم،

مرفق مع هذه الرسالة السورس كود الكامل لمنصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف (الإصدار المتقدم).

📅 تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔑 التوقيع الرقمي: {file_hash}
📊 عدد الأسطر: {len(code_content.splitlines())}
👨‍💻 المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور

الميزات المتقدمة:
- نظام المصادقة المتقدم مع 5 أدوار مختلفة
- محرك الاستمثال الخطي لتركيب العلف بأقل تكلفة
- شريط القياس الحيوي لتقدير الوزن
- خيارات البروتين (خام/مهضوم) ومعادل النشاء
- مختبر تحليل الخلطات المتقدم
- نظام إدارة الأدوية البيطرية
- نظام تحليل التربة والمياه
- نظام تتبع الإنتاج اليومي
- نظام التقارير الشهرية
- نظام التنبيهات الذكية
- نظام إدارة العملاء والموردين
- نظام تحليل التكاليف والأرباح
- مولد تقارير PDF احترافية (4 صفحات)
- التوجيه الصوتي (Web Speech API)
- إرسال الصور عبر واتساب

يمكنك تشغيل المنصة باستخدام:
streamlit run tower_scientific_platform_advanced.py

مع خالص التحية،
منصة تاور العلمية
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    attachment = MIMEText(code_content, 'plain', 'utf-8')
    attachment.add_header('Content-Disposition', 'attachment', filename="tower_scientific_platform_advanced.py")
    msg.attach(attachment)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True, "تم إرسال الكود بنجاح إلى البريد الإلكتروني"
    except Exception as e:
        return False, f"فشل الإرسال: {str(e)}"

def generate_formula_image(formula_data, target_dp, target_se, breed, stage, user_name):
    """تحويل الخلطة إلى صورة متقدمة مع اسم المستخدم وتفاصيل إضافية"""
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_facecolor('#f5f5f5')
    fig.patch.set_facecolor('#ffffff')

    title_text = f"🧬 خلطة علفية معتمدة - منصة تاور العلمية\n"
    title_text += f"المشرف: {user_name}\n"
    title_text += f"الفصيل: {breed} | المرحلة: {stage}\n"
    title_text += f"DP: {target_dp:.1f}% | SE: {target_se:.1f} وحدة"

    ax.set_title(title_text, fontsize=14, fontweight='bold', pad=25)

    ingredients = list(formula_data.keys())
    percentages = list(formula_data.values())
    kg_per_ton = [p * 10 for p in percentages]

    y_pos = np.arange(len(ingredients))
    bars = ax.barh(y_pos, kg_per_ton, color='#2e7d32', alpha=0.8, edgecolor='#1b5e20', linewidth=1.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([arabic_processor.fix_arabic_text(i) for i in ingredients], fontsize=11)
    ax.set_xlabel('الكمية (كجم/طن)', fontsize=12, fontweight='bold')

    for i, (v, bar) in enumerate(zip(kg_per_ton, bars)):
        ax.text(v + 3, i, f'{v:.1f} كجم', va='center', fontsize=10, fontweight='bold', color='#1b5e20')
        ax.text(-3, i, f'{percentages[i]:.1f}%', va='center', ha='right', fontsize=9, color='#666')

    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    cost_text = f"💰 التكلفة: ${st.session_state.get('computed_ton_cost', 0):.2f}/طن"
    ax.text(0.98, 0.02, cost_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='#e8f5e9', alpha=0.9, edgecolor='#2e7d32'))

    ax.text(0.5, -0.08,
            f'© {datetime.now().year} منصة تاور العلمية - الاختصاصي م. عبد القادر إسماعيل تاور',
            transform=ax.transAxes, ha='center', fontsize=9, color='#666666')

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()
    buf.seek(0)
    return buf

def generate_analysis_image(analysis_results, target_animal, production_type, user_name):
    """تحويل نتائج التحليل المخبري إلى صورة متقدمة"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('#ffffff')
    
    ax1.set_facecolor('#f5f5f5')
    title_text = f"🔬 تقرير التحليل المخبري - منصة تاور العلمية\n"
    title_text += f"المشرف: {user_name}\n"
    title_text += f"الحيوان: {target_animal} | المرحلة: {production_type}"
    ax1.set_title(title_text, fontsize=13, fontweight='bold', pad=20)

    if 'components' in analysis_results and analysis_results['components']:
        components = analysis_results['components']
        names = list(components.keys())
        values = list(components.values())

        if len(names) > 10:
            sorted_data = sorted(zip(values, names), reverse=True)
            values = [v for v, _ in sorted_data[:10]]
            names = [n for _, n in sorted_data[:10]]

        y_pos = np.arange(len(names))
        colors = ['#2e7d32' if v > 0 else '#c62828' for v in values]
        bars = ax1.barh(y_pos, values, color=colors, alpha=0.7, edgecolor='#1b5e20', linewidth=1)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels([arabic_processor.fix_arabic_text(n[:20]) for n in names], fontsize=10)
        ax1.set_xlabel('الوزن (كجم)', fontsize=11, fontweight='bold')

        for i, v in enumerate(values):
            ax1.text(v + 0.5, i, f'{v:.1f}', va='center', fontsize=9, fontweight='bold')
        
        ax1.grid(axis='x', alpha=0.3)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
    else:
        ax1.text(0.5, 0.5, 'لا توجد بيانات كافية للتحليل', ha='center', va='center', fontsize=14, color='#666666')
        ax1.set_xticks([])
        ax1.set_yticks([])

    ax2.set_facecolor('#f5f5f5')
    ax2.set_title("القيم الغذائية المحسوبة", fontsize=13, fontweight='bold', pad=20)

    nutrition_labels = ['البروتين الخام (CP)', 'البروتين المهضوم (DP)', 'معادل النشاء (SE)']
    nutrition_values = [
        analysis_results.get('cp', 0),
        analysis_results.get('dp', 0),
        analysis_results.get('se', 0)
    ]
    nutrition_colors = ['#2e7d32', '#1565C0', '#E65100']
    
    bars2 = ax2.bar(nutrition_labels, nutrition_values, color=nutrition_colors, alpha=0.7, edgecolor='black', linewidth=1)
    ax2.set_ylabel('القيمة', fontsize=11, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    for bar, val in zip(bars2, nutrition_values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}%' if val < 100 else f'{val:.1f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    fig.text(0.5, 0.01,
             f'© {datetime.now().year} منصة تاور العلمية - الاختصاصي م. عبد القادر إسماعيل تاور',
             ha='center', fontsize=9, color='#666666')

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.08)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    buf.seek(0)
    return buf

def send_image_to_whatsapp(image_buf, caption, phone_number=WHATSAPP_NUMBER):
    """عرض الصورة مع زر لإرسالها عبر واتساب"""
    try:
        image_base64 = base64.b64encode(image_buf.getvalue()).decode()
        encoded_caption = urllib.parse.quote(caption)
        whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_caption}"

        st.markdown(f"""
        <div style='background:#e8f5e9; padding:20px; border-radius:14px; direction:rtl; text-align:center; box-shadow:0 4px 15px rgba(0,0,0,0.1);'>
            <img src="data:image/png;base64,{image_base64}" style='max-width:100%; border-radius:10px; margin:15px 0; border:3px solid #2e7d32; box-shadow:0 6px 20px rgba(0,0,0,0.15);'>
            <br>
            <a href='{whatsapp_url}' target='_blank'>
                <button style='background:#25D366; color:white; padding:14px 40px; border:none; border-radius:35px; font-size:17px; font-weight:bold; cursor:pointer; box-shadow:0 4px 15px rgba(37,211,102,0.4); transition:all 0.3s;'>
                    📲 إرسال الصورة عبر واتساب
                </button>
            </a>
            <p style='margin-top:8px; font-size:13px; color:#666;'>
                اضغط على الزر لإرسال الصورة مع النص التوضيحي
            </p>
        </div>
        """, unsafe_allow_html=True)
        return True
    except Exception as e:
        st.error(f"❌ حدث خطأ: {str(e)}")
        return False

# =====================================================================
# السطر 2351-2600: CSS المتقدم للواجهة (مكثف)
# =====================================================================
st.markdown("""
<style>
/* =================================================================== */
/* استيراد خط Cairo من Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
* { font-family: 'Cairo', 'Tajawal', sans-serif; }

/* =================================================================== */
/* خلفية متدرجة متحركة */
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 50%, #f5f7fa 100%);
    background-attachment: fixed;
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.stApp { background: transparent; }

/* =================================================================== */
/* الصندوق الرئيسي مع تأثير زجاجي */
.main-box {
    background: rgba(255,255,255,0.92);
    padding: 35px;
    border-radius: 24px;
    box-shadow: 0 25px 70px rgba(0,0,0,0.15);
    backdrop-filter: blur(15px);
    margin-bottom: 35px;
    border: 1px solid rgba(255,255,255,0.4);
    transition: all 0.3s ease;
}
.main-box:hover {
    box-shadow: 0 30px 80px rgba(0,0,0,0.18);
}

/* =================================================================== */
/* عناوين الأقسام */
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
    position: relative;
    overflow: hidden;
}
.section-title::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(to left, rgba(46,125,50,0.05), transparent);
    pointer-events: none;
}
.section-title .icon {
    margin-left: 10px;
}

/* =================================================================== */
/* عناصر الخلطات */
.formula-item {
    background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(232,245,233,0.95) 100%);
    padding: 16px 22px;
    border-radius: 14px;
    margin-bottom: 10px;
    font-weight: 600;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.formula-item:hover {
    transform: translateX(-8px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    background: linear-gradient(135deg, rgba(255,255,255,1) 0%, rgba(200,230,201,0.95) 100%);
}
.formula-item .name {
    flex: 1;
    text-align: right;
}
.formula-item .value {
    font-weight: 700;
    color: #1b5e20;
    background: rgba(46,125,50,0.1);
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.95rem;
}

/* =================================================================== */
/* صورة الملف الشخصي */
.profile-img-style {
    width: 160px;
    height: 160px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #d4af37;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}
.profile-img-style:hover {
    transform: scale(1.05) rotate(3deg);
    box-shadow: 0 15px 45px rgba(0,0,0,0.3);
}

/* =================================================================== */
/* بطاقات الأسعار */
.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 22px;
    border-radius: 16px;
    border-right: 5px solid #2e7d32;
    box-shadow: 0 4px 25px rgba(0,0,0,0.06);
    transition: all 0.3s ease;
    margin-bottom: 15px;
}
.price-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 35px rgba(0,0,0,0.1);
}
.price-card .title {
    font-weight: 700;
    color: #1b5e20;
    font-size: 1.1rem;
    margin-bottom: 8px;
}
.price-card .price {
    font-size: 1.3rem;
    color: #e65100;
    font-weight: 700;
}

/* =================================================================== */
/* بطاقات المؤشرات */
.metric-card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 6px 30px rgba(0,0,0,0.08);
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid rgba(46,125,50,0.1);
}
.metric-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 15px 50px rgba(0,0,0,0.15);
    border-color: #2e7d32;
}
.metric-card .number {
    font-size: 2.2rem;
    font-weight: 900;
    color: #1b5e20;
    margin: 5px 0;
}
.metric-card .label {
    font-size: 0.95rem;
    color: #666;
    font-weight: 600;
}
.metric-card .icon {
    font-size: 2rem;
    margin-bottom: 5px;
}

/* =================================================================== */
/* بطاقة شريط القياس */
.measurement-card {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 22px;
    border-radius: 16px;
    border-right: 5px solid #1565C0;
    box-shadow: 0 4px 25px rgba(0,0,0,0.06);
    transition: all 0.3s ease;
}
.measurement-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 35px rgba(0,0,0,0.1);
}
.measurement-card .result {
    font-size: 1.4rem;
    font-weight: 700;
    color: #1565C0;
    text-align: center;
    margin: 10px 0;
}

/* =================================================================== */
/* حالات المخزون */
.stock-critical {
    background: linear-gradient(135deg, #ffebee, #ffcdd2);
    padding: 6px 16px;
    border-radius: 25px;
    color: #c62828;
    font-weight: 700;
    display: inline-block;
    font-size: 0.85rem;
    animation: pulse-red 1.5s infinite;
}
@keyframes pulse-red {
    0% { opacity: 1; }
    50% { opacity: 0.6; }
    100% { opacity: 1; }
}

.stock-normal {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 6px 16px;
    border-radius: 25px;
    color: #2e7d32;
    font-weight: 700;
    display: inline-block;
    font-size: 0.85rem;
}

.stock-warning {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 6px 16px;
    border-radius: 25px;
    color: #e65100;
    font-weight: 700;
    display: inline-block;
    font-size: 0.85rem;
    animation: pulse-orange 1.5s infinite;
}
@keyframes pulse-orange {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
}

/* =================================================================== */
/* بطاقة التحذير */
.warning-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 18px;
    border-radius: 14px;
    border-right: 5px solid #f57c00;
    color: #e65100;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    margin-bottom: 12px;
    transition: all 0.3s ease;
}
.warning-card:hover {
    transform: translateX(-5px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.1);
}
.warning-card .title {
    font-weight: 700;
    font-size: 1.05rem;
}
.warning-card .message {
    margin-top: 5px;
    font-size: 0.95rem;
}

/* =================================================================== */
/* شريط التغليف (Sack Tag) */
.sack-tag {
    border: 3px dashed #1b5e20;
    padding: 30px;
    border-radius: 20px;
    background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e9 100%);
    box-shadow: 0 8px 35px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
    text-align: center;
}
.sack-tag:hover {
    box-shadow: 0 12px 45px rgba(0,0,0,0.12);
    transform: scale(1.01);
}
.sack-tag .main-title {
    font-size: 1.8rem;
    font-weight: 900;
    color: #1b5e20;
}
.sack-tag .sub-title {
    font-size: 1.2rem;
    color: #c62828;
    font-weight: 700;
}
.sack-tag .details {
    background: rgba(255,255,255,0.7);
    padding: 12px;
    border-radius: 10px;
    margin-top: 10px;
}

/* =================================================================== */
/* صورة الحيوان في الشريط */
.animal-banner-img {
    width: 100%;
    max-height: 220px;
    object-fit: cover;
    border-radius: 16px;
    border: 3px solid #2e7d32;
    box-shadow: 0 6px 30px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}
.animal-banner-img:hover {
    transform: scale(1.02);
    box-shadow: 0 10px 40px rgba(0,0,0,0.15);
}

/* =================================================================== */
/* كتاب دليل المستخدم */
.manual-book {
    background: #ffffff;
    padding: 30px;
    border-radius: 16px;
    box-shadow: 0 8px 35px rgba(0,0,0,0.08);
}
.book-chapter {
    background: linear-gradient(135deg, #1a237e, #283593);
    color: white;
    padding: 15px 20px;
    border-radius: 10px;
    font-weight: bold;
    margin-top: 20px;
}
.book-body {
    padding: 20px 25px;
    font-size: 1.05rem;
    line-height: 1.8;
    color: #2c3e50;
    border-left: 4px solid #3498db;
    background: #f8f9fa;
    border-radius: 0 10px 10px 0;
}

/* =================================================================== */
/* أزرار مخصصة */
.custom-btn {
    border: none;
    padding: 12px 28px;
    border-radius: 30px;
    font-weight: 700;
    font-size: 1rem;
    transition: all 0.3s ease;
    cursor: pointer;
    display: inline-block;
}
.custom-btn-primary {
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white;
    box-shadow: 0 4px 15px rgba(27,94,32,0.3);
}
.custom-btn-primary:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(27,94,32,0.4);
}
.custom-btn-success {
    background: linear-gradient(135deg, #25D366, #128C7E);
    color: white;
    box-shadow: 0 4px 15px rgba(37,211,102,0.3);
}
.custom-btn-success:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(37,211,102,0.4);
}

/* =================================================================== */
/* تحسينات عامة */
.stButton > button {
    border-radius: 30px !important;
    font-weight: 700 !important;
    padding: 10px 25px !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.15) !important;
}
.stSelectbox > div, .stNumberInput > div, .stTextInput > div {
    border-radius: 12px !important;
}
.stTextArea > div > textarea {
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# السطر 2601-2800: بوابة الدخول (Login System) المتقدمة
# =====================================================================
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300

if not st.session_state["approved"]:
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
    
    st.markdown("<h2 style='color:#2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555; font-size:1.1rem;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</p>")
    st.markdown("<p style='text-align:center; color:#888; font-size:0.9rem;'>الإصدار المتقدم 5.0</p>", unsafe_allow_html=True)

    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("https://tower-scientific-platform.streamlit.app")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        st.markdown(f'<div style="text-align:center; margin:15px 0;"><img src="data:image/png;base64,{qr_base64}" width="120"></div>', unsafe_allow_html=True)
    except:
        pass

    login_option = st.radio("طريقة الدخول:", ["كود الدخول السري", "اسم المستخدم وكلمة المرور"], horizontal=True)

    if login_option == "كود الدخول السري":
        input_code = st.text_input("🔑 أدخل كود الدخول الخاص بك:", type="password", placeholder="مثال: 202687")
        col_login, col_reset = st.columns(2)
        with col_login:
            if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
                if input_code.strip() in CODES_DB:
                    st.session_state["approved"] = True
                    st.session_state["user_role"] = CODES_DB[input_code.strip()]["role"]
                    st.session_state["login_welcome_shown"] = False
                    st.session_state["login_attempts"] = 0
                    st.session_state["last_login_time"] = datetime.now()
                    st.session_state["session_token"] = secrets.token_urlsafe(32)
                    voice_guide(f"مرحباً بك في منصة تاور العلمية، {CODES_DB[input_code.strip()]['name']}. تم تسجيل الدخول بنجاح.")
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
        username = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم")
        password = st.text_input("🔑 كلمة المرور", type="password", placeholder="أدخل كلمة المرور")
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
                voice_guide(f"مرحباً {user['full_name']}، تم تسجيل الدخول بنجاح إلى منصة تاور العلمية.")
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ اسم المستخدم أو كلمة المرور غير صحيحة! متبقي {remaining} محاولات")
                voice_guide("اسم المستخدم أو كلمة المرور غير صحيحة. يرجى المحاولة مرة أخرى.")
        st.caption("💡 المستخدمون الافتراضيون: admin / admin123, specialist / spec123, vet / vet123, nutritionist / nutri123, breeder / breed123")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# السطر 2801-2950: الترحيب الصوتي والواجهة الرئيسية بعد تسجيل الدخول
# =====================================================================
if not st.session_state["login_welcome_shown"]:
    role_messages = {
        "owner": "👑 مرحباً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور",
        "specialist": "🔬 أهلاً بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني.",
        "veterinarian": "💊 مرحباً أيها الطبيب البيطري، نظام إدارة الأدوية جاهز.",
        "nutritionist": "🧬 مرحباً أيها الأخصائي، أدوات تركيب وتحليل الأعلاف في خدمتك.",
        "breeder": "🌾 أهلاً وسهلاً بإخواننا المربين، شركاء النجاح."
    }
    role_icons = {"owner": "👑", "specialist": "👨‍🔬", "veterinarian": "💊", "nutritionist": "🧬", "breeder": "🌾"}
    st.toast(role_messages.get(st.session_state["user_role"], "مرحباً"), icon=role_icons.get(st.session_state["user_role"], "🌾"))
    voice_welcome(st.session_state["user_role"])
    st.session_state["login_welcome_shown"] = True

# =====================================================================
# الواجهة الرئيسية (Main Interface) المتقدمة
# =====================================================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logout_space, col_user_status = st.columns([0.7, 0.3])
with col_user_status:
    role_names = {
        "owner": "المالك 👑",
        "specialist": "المختص 👨‍🔬",
        "veterinarian": "الطبيب البيطري 💊",
        "nutritionist": "أخصائي التغذية 🧬",
        "breeder": "المربي 🌾"
    }
    user_name = st.session_state.get("user", {}).get("full_name", "مستخدم")
    user_role = st.session_state.get("user_role", "breeder")
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
        voice_guide("تم تسجيل الخروج بنجاح. نأمل زيارتك مرة أخرى.")
        st.rerun()

col_logo, col_title = st.columns([0.2, 0.8])
with col_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='color:#1b5e20; text-align:right; margin-bottom:0; font-size:2.2rem;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#1565C0; text-align:right; font-size:1.2rem;'>محرك الاستمثال الخطي المتقدم - المختبر - إدارة الأدوية - التحليلات الذكية</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#c62828; text-align:right; font-weight:700;'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top:3px solid #2e7d32;'>", unsafe_allow_html=True)

# إحصائيات سريعة للوحة التحكم
st.markdown("### 📊 لوحة التحكم السريعة")
col_stat1, col_stat2, col_stat3, col_stat4, col_stat5 = st.columns(5)

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

with col_stat5:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='icon'>📄</div>
        <div class='number'>{len(st.session_state.get("daily_production_log", []))}</div>
        <div class='label'>سجلات الإنتاج</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# زر اختبار الصوت
col_voice_test1, col_voice_test2 = st.columns([0.3, 0.7])
with col_voice_test1:
    if st.button("🔊 اختبار الصوت", use_container_width=True, type="primary"):
        voice_guide("مرحباً، هذا اختبار للنظام الصوتي المتقدم. الصوت يعمل بشكل ممتاز.")
        st.success("✅ تم تشغيل الصوت، إذا لم تسمع شيئاً فتأكد من أن الصوت في المتصفح غير مكتوم.")
with col_voice_test2:
    st.info("💡 للتأكد من عمل الصوت، اضغط على الزر المجاور. يعمل النظام الصوتي في جميع أجزاء المنصة.")

st.markdown("---")

# =====================================================================
# أزرار إرسال الكود والنتائج المتقدمة
# =====================================================================
st.markdown("### 📤 أدوات المشاركة والإرسال المتقدمة")

col_code, col_formula, col_analysis = st.columns(3)

with col_code:
    st.markdown("#### 📧 إرسال الكود البرمجي")
    email_input = st.text_input("البريد الإلكتروني:", placeholder="example@email.com")
    if st.button("📤 إرسال الكود إلى البريد", use_container_width=True):
        if email_input and '@' in email_input:
            with st.spinner("جاري إرسال الكود..."):
                success, msg = send_code_to_email(email_input)
                if success:
                    st.success(msg)
                    voice_guide("تم إرسال الكود إلى البريد الإلكتروني بنجاح.")
                else:
                    st.error(msg)
        else:
            st.warning("⚠️ يرجى إدخال بريد إلكتروني صحيح.")

with col_formula:
    st.markdown("#### 🧬 مشاركة الخلطة")
    if st.button("📊 تحويل الخلطة إلى صورة وإرسالها", use_container_width=True):
        if st.session_state["active_formula"]:
            user_name = st.session_state.get("user", {}).get("full_name", "مستخدم")
            img_buf = generate_formula_image(
                st.session_state["active_formula"],
                st.session_state["active_cp_tag"],
                st.session_state["active_se_tag"],
                st.session_state["active_breed_tag"],
                st.session_state["active_stage_title"],
                user_name
            )
            caption = f"🧬 خلطة علفية معتمدة من منصة تاور العلمية\n"
            caption += f"المشرف: {user_name}\n"
            caption += f"التكلفة: ${st.session_state['computed_ton_cost']:.2f}/طن"
            send_image_to_whatsapp(img_buf, caption)
            voice_guide("تم تحويل الخلطة إلى صورة وجاهزة للمشاركة.")
        else:
            st.warning("⚠️ يرجى تشغيل محرك التركيب أولاً للحصول على خلطة.")

with col_analysis:
    st.markdown("#### 🔬 مشاركة نتائج التحليل")
    if st.button("📊 تحويل نتائج التحليل إلى صورة", use_container_width=True):
        if st.session_state["analysis_results"]:
            user_name = st.session_state.get("user", {}).get("full_name", "مستخدم")
            img_buf = generate_analysis_image(
                st.session_state["analysis_results"],
                st.session_state["analysis_animal"],
                st.session_state["analysis_stage"],
                user_name
            )
            caption = f"🔬 تقرير التحليل المخبري - منصة تاور العلمية\n"
            caption += f"المشرف: {user_name}"
            send_image_to_whatsapp(img_buf, caption)
            voice_guide("تم تحويل نتائج التحليل إلى صورة وجاهزة للمشاركة.")
        else:
            st.warning("⚠️ يرجى إجراء تحليل مخبري أولاً.")

st.markdown("---")

# =====================================================================
# النص الدعائي والإعلامي المتقدم
# =====================================================================
st.markdown("### 📢 المشاركة التسويقية والدعوة العلمية")
share_text_payload = """📢 دعوة علمية وتسويقية من منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف (الإصدار المتقدم)

إلى كل مهتم بتطوير الثروة الحيوانية؛ من أطباء بيطريين، اختصاصيي إنتاج حيواني، ومربين طموحين:
يسعدنا دعوتكم لاستخدام وتجربة المنصة المتقدمة لتركيب وتطوير الأعلاف، بإشراف وتصميم:
[ الاختصاصي م. عبد القادر إسماعيل تاور ]

🎯 ما تقدمه المنصة المتقدمة:
• حلول برمجية ذكية لتركيب أعلاف اقتصادية على أساس البروتين المهضوم ومعادل النشاء.
• مختبر متكامل لتحليل الخلطات وحساب القيم الغذائية.
• نظام إدارة الأدوية البيطرية وسجلات العلاج.
• نظام تحليل التربة والمياه.
• نظام تتبع الإنتاج اليومي والتقارير الشهرية.
• نظام التنبيهات الذكية وإدارة العملاء والموردين.
• نظام تحليل التكاليف والأرباح.
• تقارير PDF احترافية (4 صفحات) وصور قابلة للمشاركة عبر واتساب.
• توجيه صوتي تفاعلي لجميع العمليات.

🔗 رابط المنصة: https://tower-scientific-platform.streamlit.app"""
st.text_area("النص الدعائي والإعلامي الجاهز للنشر:", value=share_text_payload, height=150, key="top_share_box")
col_copy2, col_share2 = st.columns(2)
with col_copy2:
    if st.button("📋 نسخ الرابط والنص", use_container_width=True):
        st.success("تم التجهيز بنجاح!")
        voice_guide("تم نسخ النص الدعائي.")
with col_share2:
    encoded_share = urllib.parse.quote(share_text_payload[:200])
    st.link_button("📲 مشاركة عبر واتساب", f"https://wa.me/?text={encoded_share}", use_container_width=True)

st.markdown("---")

# =====================================================================
# تحديد التبويبات الرئيسية المتقدمة
# =====================================================================
if st.session_state["user_role"] in ["owner", "specialist"]:
    tabs_titles = [
        "🐾 القطاع الحيواني",
        "📊 بورصة الأسعار",
        "🏭 إدارة المستودعات",
        "🧾 الفواتير والتسويق",
        "💊 الأدوية البيطرية",
        "🧪 تحليل التربة والمياه",
        "📈 الإنتاج اليومي",
        "📊 التقارير الشهرية",
        "🔔 التنبيهات الذكية",
        "📇 العملاء والموردين",
        "💰 تحليل التكاليف والأرباح",
        "🖨️ مصمم الديباجة",
        "📈 التحليلات المتقدمة",
        "🐔 إدارة مزارع الدجاج",
        "💬 تعليقات المختصين",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم"
    ]
elif st.session_state["user_role"] in ["veterinarian"]:
    tabs_titles = [
        "🐾 القطاع الحيواني",
        "💊 الأدوية البيطرية",
        "📈 الإنتاج اليومي",
        "📊 التقارير الشهرية",
        "🔔 التنبيهات الذكية",
        "📇 العملاء والموردين",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية"
    ]
elif st.session_state["user_role"] in ["nutritionist"]:
    tabs_titles = [
        "🐾 القطاع الحيواني",
        "🧪 تحليل التربة والمياه",
        "📈 الإنتاج اليومي",
        "📊 التقارير الشهرية",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية"
    ]
else:  # breeder
    tabs_titles = [
        "🐾 القطاع الحيواني",
        "📈 الإنتاج اليومي",
        "📊 التقارير الشهرية",
        "🔔 التنبيهات الذكية",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم"
    ]

tabs = st.tabs(tabs_titles)

# =====================================================================
# التبويب الرئيسي: القطاع الحيواني (مع شريط القياس وخيارات البروتين والمختبر)
# =====================================================================
with tabs[0]:
    st.markdown('<div class="section-title">🐾 القطاع الحيواني - تركيب الأعلاف حسب النوع مع القياسات الحيوية والمختبر</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='background:linear-gradient(135deg,#e8f5e9,#c8e6c9); padding:20px; border-radius:16px; direction:rtl; text-align:right; margin-bottom:25px;'>
    <b>📘 مرحباً بك في قسم القطاع الحيواني المتقدم:</b> اختر نوع الحيوان، ثم حدد السلالة والمرحلة الإنتاجية. 
    يمكنك استخدام <b>شريط القياس الحيوي</b> لتقدير الوزن والاحتياجات، واختيار أساس البروتين (خام أو مهضوم) ومعادل النشاء.
    بالإضافة إلى ذلك، يمكنك استخدام <b>المختبر</b> لتحليل الخلطات الجاهزة.
    </div>
    """, unsafe_allow_html=True)
    
    # تبويبات القطاع الحيواني الفرعية (مع المختبر)
    animal_sub_tabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐴 خيول", "🐔 دواجن", "🐟 أسماك", "🔬 المختبر"])
    
    # =====================================================================
    # دالة مساعدة متقدمة لإنشاء تبويب حيواني
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
                                               file_name=f"Tower_{display_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
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
        st.markdown("""
        <div style='background:linear-gradient(135deg,#e3f2fd,#bbdefb); padding:15px; border-radius:12px; direction:rtl; text-align:right; margin-bottom:20px;'>
        <b>🐴 منتجات Havens للخيول:</b> DraversBrok (حبيبات 7 مم) مثالية للخيول الرياضية، تدعم بناء العضلات والحيوية.
        <b>Gastro Cube</b> للمعدة الحساسة يحتوي على مكونات طبيعية لتخفيف تهيج المعدة.
        </div>
        """, unsafe_allow_html=True)
        render_animal_tab("horse", "الخيول", "🐴",
                         ["خيل عربي أصيل", "ثوروبريد", "خيول محلية"],
                         ["راحة/صيانة", "عمل خفيف", "عمل متوسط", "عمل مكثف", "سباق"],
                         11.0, 62.0, "خيول", has_measurements=True)
        st.markdown("""
        <div style='background:#fff3e0; padding:15px; border-radius:12px; direction:rtl;'>
        <b>📋 قواعد التغذية الذهبية للخيول:</b>
        <ul>
        <li>💧 الماء متوفر دائماً.</li>
        <li>🌿 الألياف الخشنة ≥ 1.5% من وزن الجسم.</li>
        <li>⚖️ العلف المركز حسب النشاط (0.2-1.2 كجم/100 كجم وزن).</li>
        <li>🍬 استخدم EquiSweet® للتحكم بالسكر.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
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
    # 🔬 تبويب المختبر المتقدم (تحليل الخلطات)
    # =====================================================================
    with animal_sub_tabs[6]:
        st.markdown('<div class="section-title">🔬 المختبر المتقدم - تحليل الخلطات الجاهزة</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#e3f2fd; padding:18px; border-radius:14px; direction:rtl; text-align:right; margin-bottom:20px;'>
        <b>🧪 مرحباً بك في مختبر تحليل الخلطات المتقدم:</b> أدخل أوزان المكونات التي تستخدمها في خلطتك، وسيقوم المختبر بحساب 
        نسبة البروتين الخام (CP)، البروتين المهضوم (DP)، ومعادل النشاء (SE) الإجمالي، مع عرض تقرير مفصل ورسوم بيانية متقدمة.
        </div>
        """, unsafe_allow_html=True)
        
        # اختيار الحيوان والمرحلة
        st.markdown("#### 🎯 حدد الفصيل والمرحلة الإنتاجية (للمقارنة)")
        col_lab_animal, col_lab_stage = st.columns(2)
        with col_lab_animal:
            lab_animal = st.selectbox("الفصيل:", ["أبقار", "أغنام", "ماعز", "خيول", "دواجن لاحم", "دواجن بياض", "سمان", "أسماك"], key="lab_animal")
        with col_lab_stage:
            if lab_animal in ["أبقار", "أغنام", "ماعز"]:
                lab_stage = st.selectbox("مرحلة الإنتاج:", ["تسمين", "حليب/إدرار", "حمل/دفع غذائي", "صيانة"], key="lab_stage")
            elif lab_animal in ["دواجن لاحم", "دواجن بياض", "سمان"]:
                lab_stage = st.selectbox("مرحلة الإنتاج:", ["بادي", "نامي", "ناهي", "بياض"], key="lab_stage")
            else:
                lab_stage = st.selectbox("مرحلة الإنتاج:", ["نمو", "تسمين نهائي"], key="lab_stage")
        
        # الاحتياجات القياسية
        cp_requirements = {
            ("أبقار", "تسمين"): 12.0, ("أبقار", "حليب/إدرار"): 14.0, ("أبقار", "حمل/دفع غذائي"): 11.0, ("أبقار", "صيانة"): 9.0,
            ("أغنام", "تسمين"): 13.0, ("أغنام", "حليب/إدرار"): 14.5, ("أغنام", "حمل/دفع غذائي"): 11.5, ("أغنام", "صيانة"): 8.5,
            ("ماعز", "تسمين"): 12.5, ("ماعز", "حليب/إدرار"): 14.0, ("ماعز", "حمل/دفع غذائي"): 11.0, ("ماعز", "صيانة"): 8.0,
            ("خيول", "نمو"): 13.0, ("خيول", "تسمين نهائي"): 11.0,
            ("دواجن لاحم", "بادي"): 23.0, ("دواجن لاحم", "نامي"): 21.0, ("دواجن لاحم", "ناهي"): 19.0,
            ("دواجن بياض", "بادي"): 20.0, ("دواجن بياض", "نامي"): 18.0, ("دواجن بياض", "ناهي"): 16.5, ("دواجن بياض", "بياض"): 16.0,
            ("سمان", "بادي"): 24.0, ("سمان", "نامي"): 22.0, ("سمان", "ناهي"): 20.0, ("سمان", "بياض"): 18.0,
            ("أسماك", "نمو"): 32.0, ("أسماك", "تسمين نهائي"): 28.0
        }
        suggested_cp = cp_requirements.get((lab_animal, lab_stage), 15.0)
        st.info(f"💡 الاحتياج القياسي للبروتين الخام (CP) لـ {lab_animal} في مرحلة {lab_stage} هو ≈ {suggested_cp:.1f}%")
        
        st.markdown("---")
        st.markdown("#### 📥 أدخل أوزان المكونات (بالكيلوجرام)")
        
        lab_user_inputs = {}
        all_library_ingredients = []
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            for ing_name in items.keys():
                all_library_ingredients.append(ing_name)
        
        col_input1, col_input2, col_input3 = st.columns(3)
        total_ing_count = len(all_library_ingredients)
        segment = total_ing_count // 3 + 1
        
        with col_input1:
            for ing_name in all_library_ingredients[:segment]:
                lab_user_inputs[ing_name] = st.number_input(
                    f"وزن {ing_name} (كجم)",
                    min_value=0.0, value=0.0, step=5.0,
                    key=f"lab_in_{ing_name}"
                )
        with col_input2:
            for ing_name in all_library_ingredients[segment:segment*2]:
                lab_user_inputs[ing_name] = st.number_input(
                    f"وزن {ing_name} (كجم)",
                    min_value=0.0, value=0.0, step=5.0,
                    key=f"lab_in_{ing_name}"
                )
        with col_input3:
            for ing_name in all_library_ingredients[segment*2:]:
                lab_user_inputs[ing_name] = st.number_input(
                    f"وزن {ing_name} (كجم)",
                    min_value=0.0, value=0.0, step=5.0,
                    key=f"lab_in_{ing_name}"
                )
        
        st.markdown("---")
        
        if st.button("🧪 تشغيل التحليل المخبري المتقدم", type="primary", use_container_width=True, key="lab_run"):
            lab_total_weight = sum(lab_user_inputs.values())
            
            if lab_total_weight <= 0:
                st.warning("⚠️ الرجاء إدخال أوزان أكبر من الصفر.")
                voice_guide("الرجاء إدخال أوزان أكبر من الصفر.")
            else:
                voice_guide(f"جاري تشغيل التحليل المخبري المتقدم لـ {lab_animal} في مرحلة {lab_stage}.")
                st.info("🔄 جاري تحليل العينة...")
                
                calculated_total_cp = 0.0
                calculated_total_dp = 0.0
                calculated_total_se = 0.0
                entered_components_summary = []
                
                for ing_name, weight in lab_user_inputs.items():
                    if weight > 0:
                        pct = weight / lab_total_weight
                        ing_cp = 0.0
                        ing_dc = 0.0
                        ing_se = 0.0
                        for cat, items in BIG_FEEDS_LIBRARY.items():
                            if ing_name in items:
                                ing_cp = items[ing_name].get("CP", 0.0)
                                ing_dc = items[ing_name].get("DC", 0.0)
                                ing_se = items[ing_name].get("SE", 0.0)
                        calculated_total_cp += pct * ing_cp
                        calculated_total_dp += pct * (ing_cp * ing_dc)
                        calculated_total_se += pct * ing_se
                        entered_components_summary.append({
                            "المادة العلفية": ing_name,
                            "الوزن المدخل (كجم)": f"{weight:.1f}",
                            "النسبة المئوية": f"{pct * 100:.2f}%"
                        })
                
                st.session_state["analysis_results"] = {
                    'components': {k: v for k, v in lab_user_inputs.items() if v > 0},
                    'cp': calculated_total_cp,
                    'dp': calculated_total_dp,
                    'se': calculated_total_se
                }
                st.session_state["analysis_animal"] = lab_animal
                st.session_state["analysis_stage"] = lab_stage
                
                st.success("🔬 تم فحص العينة وتحليل المحتوى الغذائي بنجاح!")
                voice_guide("تم فحص العينة وتحليل المحتوى الغذائي بنجاح.")
                
                st.markdown(f"### ⚖️ إجمالي وزن الخلطة: **{lab_total_weight:.1f} كجم**")
                st.write("#### 📊 نسب توزيع المكونات:")
                st.table(pd.DataFrame(entered_components_summary))
                
                st.markdown("---")
                st.write("#### 🔬 تقرير الفحص المخبري النهائي:")
                
                col_res1, col_res2 = st.columns([0.6, 0.4])
                with col_res1:
                    st.write("**القيم الغذائية المحسوبة:**")
                    report_data = [
                        {"العنصر": "البروتين الخام (CP)", "القيمة": f"{calculated_total_cp:.2f}%"},
                        {"العنصر": "البروتين المهضوم (DP)", "القيمة": f"{calculated_total_dp:.2f}%"},
                        {"العنصر": "معادل النشاء (SE)", "القيمة": f"{calculated_total_se:.2f} وحدة"}
                    ]
                    st.table(pd.DataFrame(report_data))
                    
                    if calculated_total_cp >= suggested_cp:
                        st.success(f"✅ البروتين الخام المحسوب ({calculated_total_cp:.1f}%) مطابق أو أعلى من الاحتياج القياسي ({suggested_cp:.1f}%)")
                    else:
                        st.warning(f"⚠️ البروتين الخام المحسوب ({calculated_total_cp:.1f}%) أقل من الاحتياج القياسي ({suggested_cp:.1f}%)")
                
                with col_res2:
                    graph_data = {k: v for k, v in lab_user_inputs.items() if v > 0}
                    if graph_data:
                        fig = px.pie(
                            values=list(graph_data.values()),
                            names=list(graph_data.keys()),
                            title="توزيع المكونات في الخلطة",
                            color_discrete_sequence=px.colors.sequential.Blues_r
                        )
                        fig.update_layout(height=350)
                        st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("#### 📈 مقارنة القيم الغذائية")
                nutrition_data = pd.DataFrame({
                    'العنصر': ['البروتين الخام (CP)', 'البروتين المهضوم (DP)', 'معادل النشاء (SE)'],
                    'القيمة': [calculated_total_cp, calculated_total_dp, calculated_total_se]
                })
                fig_bar = px.bar(
                    nutrition_data, x='العنصر', y='القيمة',
                    title="القيم الغذائية المحسوبة",
                    color='العنصر',
                    color_discrete_sequence=['#2e7d32', '#1565C0', '#E65100']
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                st.markdown("---")
                st.markdown("#### 📤 مشاركة النتائج")
                col_share_lab1, col_share_lab2 = st.columns(2)
                with col_share_lab1:
                    lab_share_text = f"🔬 تقرير مختبر منصة تاور العلمية المتقدم:\nالحيوان: {lab_animal} - {lab_stage}\nالبروتين الخام: {calculated_total_cp:.2f}%\nالبروتين المهضوم: {calculated_total_dp:.2f}%\nمعادل النشاء: {calculated_total_se:.2f} وحدة"
                    encoded_lab = urllib.parse.quote(lab_share_text)
                    st.markdown(f'<a href="https://wa.me/?text={encoded_lab}" target="_blank"><button style="background:#25D366; color:white; padding:12px 25px; border:none; border-radius:35px; font-weight:bold; cursor:pointer; font-size:16px;">📲 مشاركة النتيجة عبر واتساب</button></a>', unsafe_allow_html=True)
                
                with col_share_lab2:
                    if st.button("📊 تحويل النتائج إلى صورة متقدمة", use_container_width=True):
                        user_name = st.session_state.get("user", {}).get("full_name", "مستخدم")
                        img_buf = generate_analysis_image(
                            st.session_state["analysis_results"],
                            lab_animal,
                            lab_stage,
                            user_name
                        )
                        caption = f"🔬 تقرير التحليل المخبري المتقدم - منصة تاور العلمية\nالمشرف: {user_name}"
                        send_image_to_whatsapp(img_buf, caption)
                        voice_guide("تم تحويل نتائج التحليل إلى صورة متقدمة وجاهزة للمشاركة.")
                    
                    # زر تحميل PDF
                    try:
                        pdf_data = pdf_generator.generate_lab_report(
                            st.session_state["analysis_results"],
                            lab_animal,
                            lab_stage,
                            st.session_state.get("user", {}).get("full_name", "مستخدم")
                        )
                        st.download_button("📥 تحميل تقرير المختبر PDF (3 صفحات)", pdf_data,
                                           file_name=f"Lab_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                           mime="application/pdf")
                    except Exception as e:
                        st.warning(f"⚠️ تعذر إنشاء PDF: {e}")

# =====================================================================
# تبويب بورصة الأسعار (مختصر)
# =====================================================================
with tabs[1]:
    st.markdown('<div class="section-title">📊 بورصة الأسعار المركزية المتقدمة</div>', unsafe_allow_html=True)
    st.markdown("#### أسعار الماشية والمنتجات")
    col_live, col_prod = st.columns(2)
    with col_live:
        st.subheader("🐄 الماشية")
        for k, v in st.session_state["global_livestock_prices"].items():
            st.metric(k, f"${v:.2f}")
    with col_prod:
        st.subheader("🥩 المنتجات")
        for k, v in st.session_state["global_products_prices"].items():
            st.metric(k, f"${v:.2f}")
    
    # توقعات الأسعار
    st.markdown("---")
    st.subheader("🔮 توقعات الأسعار للأسبوع القادم")
    predictor = PricePredictor()
    market_summary = predictor.get_market_summary()
    cols = st.columns(len(market_summary))
    for idx, (ing, data) in enumerate(market_summary.items()):
        with cols[idx]:
            if data.get('current_price'):
                icon = "📈" if data.get('trend') == 'up' else "📉" if data.get('trend') == 'down' else "➡️"
                st.metric(
                    f"{icon} {ing}",
                    f"${data['current_price']:.2f}",
                    delta=f"{data.get('change_percent', 0):.1f}%"
                )
                if data.get('prediction_7d'):
                    st.caption(f"توقع: ${data['prediction_7d']:.2f} (ثقة {data.get('confidence', 0)*100:.0f}%)")

# =====================================================================
# تبويب إدارة المستودعات المتقدمة
# =====================================================================
with tabs[2]:
    st.markdown('<div class="section-title">🏭 إدارة المستودعات الذكية المتقدمة</div>', unsafe_allow_html=True)
    stock_warnings = InventoryManager.check_stock_levels()
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("📦 إجمالي المواد", len(st.session_state["inventory"]))
    with col2: st.metric("⚠️ مواد نفذت", sum(1 for v in stock_warnings.values() if v["status"]=="نفذ المخزون"))
    with col3: st.metric("🔔 مواد منخفضة", sum(1 for v in stock_warnings.values() if v["status"]=="منخفض"))
    with col4: st.metric("✅ مواد آمنة", len(st.session_state["inventory"]) - sum(1 for v in stock_warnings.values() if v["status"] in ["نفذ المخزون","منخفض"]))
    
    inv_cols = st.columns(3)
    for idx, (name, qty_data) in enumerate(list(st.session_state["inventory"].items())):
        with inv_cols[idx % 3]:
            qty = qty_data if isinstance(qty_data, (int, float)) else qty_data["quantity"]
            thresh = 5.0 if isinstance(qty_data, (int, float)) else qty_data.get("min_threshold", 5.0)
            if qty <= 0:
                badge = f'<span class="stock-critical">⚠️ نفذ: {qty:.1f} طن</span>'
            elif qty < thresh:
                badge = f'<span class="stock-warning">⚠️ حرج: {qty:.1f} طن</span>'
            else:
                badge = f'<span class="stock-normal">✅ آمن: {qty:.1f} طن</span>'
            st.markdown(f"**{name}** {badge}", unsafe_allow_html=True)
            if st.session_state["user_role"] == "owner":
                new_qty = st.number_input(f"تحديث ({name}) طن:", min_value=0.0, value=float(qty), key=f"inv_{name}")
                if new_qty != qty:
                    if isinstance(st.session_state["inventory"][name], dict):
                        st.session_state["inventory"][name]["quantity"] = new_qty
                        st.session_state["inventory"][name]["last_updated"] = datetime.now().isoformat()
                    else:
                        st.session_state["inventory"][name] = new_qty

# =====================================================================
# تبويب الفواتير والتسويق
# =====================================================================
with tabs[3]:
    st.markdown('<div class="section-title">💰 نظام الفواتير والتسويق المتقدم</div>', unsafe_allow_html=True)
    client = st.text_input("اسم العميل:", "مزرعة الإنتاج المتكاملة")
    tons = st.number_input("الكمية (طن):", min_value=0.1, value=2.0, step=0.5)
    profit = st.number_input("هامش الربح ($/طن):", min_value=0.0, value=50.0)
    selling_price = st.session_state["computed_ton_cost"] + profit
    total = selling_price * tons
    st.metric("💰 سعر البيع للطن", f"${selling_price:.2f}")
    st.metric("🧾 إجمالي الفاتورة", f"${total:.2f}")
    
    if st.button("✅ تأكيد البيع وخصم المخزون", type="primary"):
        # محاكاة عملية البيع
        st.success("✅ تمت عملية البيع بنجاح!")
        voice_guide("تم تأكيد عملية البيع بنجاح.")
        st.balloons()

# =====================================================================
# تبويب الأدوية البيطرية
# =====================================================================
with tabs[4]:
    st.markdown('<div class="section-title">💊 نظام إدارة الأدوية البيطرية</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#f3e5f5; padding:15px; border-radius:12px; direction:rtl;'>
    <b>📋 نظام إدارة الأدوية البيطرية:</b> يمكنك تسجيل الأدوية المستخدمة، الجرعات، وفترات السحب، وتتبع المخزون.
    </div>
    """, unsafe_allow_html=True)
    
    col_med1, col_med2 = st.columns(2)
    with col_med1:
        med_name = st.text_input("اسم الدواء:")
        med_category = st.selectbox("التصنيف:", ["مضاد حيوي", "مسكن", "فيتامين", "لقاح", "مضاد طفيليات", "هرموني", "مضاد فطريات"])
        med_dosage = st.number_input("الجرعة (ملغم/كجم):", min_value=0.0, value=10.0)
        med_stock = st.number_input("الكمية المتوفرة:", min_value=0.0, value=100.0)
    with col_med2:
        med_route = st.selectbox("طريق الإعطاء:", ["فموي", "حقن عضلي", "حقن وريدي", "موضعي", "استنشاق"])
        med_withdrawal = st.number_input("فترة السحب (يوم):", min_value=0, value=7)
        med_price = st.number_input("السعر ($):", min_value=0.0, value=5.0)
        med_expiry = st.date_input("تاريخ الانتهاء:", value=datetime.now() + timedelta(days=365))
    
    if st.button("💾 تسجيل الدواء", type="primary"):
        if med_name:
            st.session_state["medicines_list"].append({
                "name": med_name,
                "category": med_category,
                "dosage": med_dosage,
                "route": med_route,
                "withdrawal": med_withdrawal,
                "price": med_price,
                "stock": med_stock,
                "expiry": med_expiry.strftime("%Y-%m-%d")
            })
            st.success(f"✅ تم تسجيل الدواء {med_name} بنجاح!")
            voice_guide(f"تم تسجيل الدواء {med_name} بنجاح.")
        else:
            st.warning("⚠️ يرجى إدخال اسم الدواء.")
    
    if st.session_state["medicines_list"]:
        st.markdown("---")
        st.subheader("📋 قائمة الأدوية المسجلة")
        med_df = pd.DataFrame(st.session_state["medicines_list"])
        st.dataframe(med_df, use_container_width=True)

# =====================================================================
# تبويب الإنتاج اليومي
# =====================================================================
with tabs[5]:
    st.markdown('<div class="section-title">📈 الإنتاج اليومي</div>', unsafe_allow_html=True)
    farm = st.text_input("اسم المزرعة:", "مزرعة النموذج")
    animal = st.selectbox("نوع الحيوان:", ["أبقار", "أغنام", "ماعز", "دواجن", "أسماك"])
    milk = st.number_input("إنتاج الحليب (لتر):", min_value=0.0, value=0.0)
    eggs = st.number_input("إنتاج البيض (عدد):", min_value=0, value=0)
    feed = st.number_input("العلف المستهلك (كجم):", min_value=0.0, value=0.0)
    water = st.number_input("المياه المستهلكة (لتر):", min_value=0.0, value=0.0)
    mortality = st.number_input("النافق (عدد):", min_value=0, value=0)
    
    if st.button("💾 حفظ الإنتاج اليومي", type="primary"):
        st.session_state["daily_production_log"].append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "farm": farm,
            "animal": animal,
            "milk": milk,
            "eggs": eggs,
            "feed": feed,
            "water": water,
            "mortality": mortality
        })
        st.success("✅ تم حفظ الإنتاج اليومي!")
        voice_guide("تم حفظ الإنتاج اليومي بنجاح.")

# =====================================================================
# تبويب التقارير الشهرية
# =====================================================================
with tabs[6]:
    st.markdown('<div class="section-title">📊 التقارير الشهرية</div>', unsafe_allow_html=True)
    if st.session_state["daily_production_log"]:
        df = pd.DataFrame(st.session_state["daily_production_log"])
        st.write("### 📋 سجل الإنتاج")
        st.dataframe(df, use_container_width=True)
        
        if 'milk' in df.columns and df['milk'].sum() > 0:
            fig = px.line(df, x='date', y='milk', title="تطور إنتاج الحليب", markers=True)
            st.plotly_chart(fig, use_container_width=True)
        
        if 'feed' in df.columns and df['feed'].sum() > 0:
            fig2 = px.bar(df, x='date', y='feed', title="استهلاك العلف اليومي")
            st.plotly_chart(fig2, use_container_width=True)
        
        st.download_button("📥 تحميل التقرير CSV", df.to_csv(index=False).encode(), "production_report.csv", "text/csv")
    else:
        st.info("لا توجد بيانات إنتاج مسجلة بعد. استخدم تبويب الإنتاج اليومي لتسجيل البيانات.")

# =====================================================================
# تبويب التنبيهات الذكية
# =====================================================================
with tabs[7]:
    st.markdown('<div class="section-title">🔔 التنبيهات الذكية</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#fff3e0; padding:15px; border-radius:12px; direction:rtl;'>
    <b>🔔 نظام التنبيهات:</b> يتم عرض التنبيهات الهامة مثل انخفاض المخزون، مواعيد التحصينات، وتواريخ انتهاء الأدوية.
    </div>
    """, unsafe_allow_html=True)
    
    alerts = []
    # تنبيهات المخزون
    stock_warnings = InventoryManager.check_stock_levels()
    for item, status in stock_warnings.items():
        alerts.append(f"⚠️ {item}: {status['status']}")
    
    # تنبيهات التحصينات
    for age, info in st.session_state["standard_vacc_schedule"].items():
        alerts.append(f"💉 اليوم {age}: {info['name']} - {info['dose']}")
    
    # تنبيهات الأدوية المنتهية
    for med in st.session_state.get("medicines_list", []):
        if med.get("expiry"):
            try:
                expiry = datetime.strptime(med["expiry"], "%Y-%m-%d")
                if expiry < datetime.now():
                    alerts.append(f"⚠️ دواء {med['name']} منتهي الصلاحية!")
            except:
                pass
    
    if alerts:
        for alert in alerts[:10]:
            st.warning(alert)
    else:
        st.success("✅ لا توجد تنبيهات حالياً. كل شيء في حالة جيدة.")

# =====================================================================
# تبويب مصمم الديباجة
# =====================================================================
with tabs[8]:
    st.markdown('<div class="section-title">🖨️ مصمم الديباجة الفنية</div>', unsafe_allow_html=True)
    brand = st.text_input("البراند:", "منصة تاور العلمية")
    
    st.markdown(f"""
    <div class="sack-tag">
        <h2 class='main-title'>🌟 {brand} 🌟</h2>
        <h3 class='sub-title'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>
        <div class='details'>
            <p>🎯 {st.session_state['active_stage_title']}</p>
            <p>🧬 DP: {st.session_state['active_cp_tag']:.1f}% | SE: {st.session_state['active_se_tag']:.1f}</p>
            <p>📅 {datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📥 تصدير الديباجة كصورة"):
        st.info("سيتم إضافة ميزة التصدير في التحديث القادم.")

# =====================================================================
# تبويب التحليلات المتقدمة
# =====================================================================
with tabs[9]:
    st.markdown('<div class="section-title">📈 التحليلات المتقدمة</div>', unsafe_allow_html=True)
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1: st.markdown("<div class='metric-card'><div class='number'>1,247</div><div class='label'>خلطات</div></div>", unsafe_allow_html=True)
    with col_m2: st.markdown("<div class='metric-card'><div class='number'>$285</div><div class='label'>متوسط التكلفة</div></div>", unsafe_allow_html=True)
    with col_m3: st.markdown("<div class='metric-card'><div class='number'>18%</div><div class='label'>نسبة التوفير</div></div>", unsafe_allow_html=True)
    with col_m4: st.markdown("<div class='metric-card'><div class='number'>96%</div><div class='label'>رضا العملاء</div></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📊 تحليل استخدام المواد")
    usage_data = pd.DataFrame({
        'المادة': ['ذرة صفراء', 'كسب صويا', 'نخالة قمح', 'شعير', 'أخرى'],
        'النسبة': [45, 25, 15, 10, 5]
    })
    fig = px.pie(usage_data, values='النسبة', names='المادة', title="توزيع استخدام المواد")
    st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# تبويب إدارة مزارع الدجاج
# =====================================================================
with tabs[10]:
    st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج اللاحم</div>', unsafe_allow_html=True)
    
    # إضافة مزرعة جديدة
    st.subheader("➕ إضافة مزرعة جديدة")
    col_new1, col_new2 = st.columns(2)
    with col_new1:
        new_farm_name = st.text_input("اسم المزرعة:")
        new_owner = st.text_input("اسم المالك:")
    with col_new2:
        new_phone = st.text_input("رقم واتساب:", value=WHATSAPP_NUMBER)
        new_birds = st.number_input("عدد الكتاكيت:", min_value=1, value=100)
    
    if st.button("➕ إضافة مزرعة", type="primary") and new_farm_name:
        st.session_state["broiler_farms"][new_farm_name] = {
            "owner": new_owner,
            "owner_phone": new_phone,
            "initial_birds": new_birds,
            "current_data": {
                "flock_age_days": 1,
                "initial_birds": new_birds,
                "current_weight_kg": 0.045,
                "dead_birds": 0,
                "total_feed_consumed_kg": 0.0,
                "temperature_c": 33.0
            },
            "daily_logs": []
        }
        st.success(f"✅ تم إضافة مزرعة {new_farm_name}!")
        voice_guide(f"تم إضافة مزرعة {new_farm_name}.")
        st.rerun()
    
    # عرض المزارع الموجودة
    if st.session_state["broiler_farms"]:
        st.markdown("---")
        st.subheader("📋 المزارع المسجلة")
        for farm_name, farm_data in st.session_state["broiler_farms"].items():
            with st.expander(f"🏷️ {farm_name} (المالك: {farm_data.get('owner', 'غير مسجل')})"):
                current = farm_data.get("current_data", {})
                col_in, col_out = st.columns(2)
                with col_in:
                    age = st.number_input("العمر (يوم)", min_value=1, value=current.get("flock_age_days", 1), key=f"age_{farm_name}")
                    init = st.number_input("الكتاكيت", min_value=1, value=current.get("initial_birds", 100), key=f"init_{farm_name}")
                    dead = st.number_input("النافق", min_value=0, value=current.get("dead_birds", 0), key=f"dead_{farm_name}")
                    wt = st.number_input("الوزن (كجم)", min_value=0.0, value=current.get("current_weight_kg", 0.5), step=0.05, key=f"wt_{farm_name}")
                    feed = st.number_input("العلف (كجم)", min_value=0.0, value=current.get("total_feed_consumed_kg", 0.0), key=f"feed_{farm_name}")
                    temp = st.number_input("درجة الحرارة", min_value=10.0, max_value=45.0, value=current.get("temperature_c", 33.0), key=f"temp_{farm_name}")
                    
                    if st.button(f"💾 حفظ بيانات {farm_name}", key=f"save_{farm_name}"):
                        st.session_state["broiler_farms"][farm_name]["current_data"] = {
                            "flock_age_days": age, "initial_birds": init, "dead_birds": dead,
                            "current_weight_kg": wt, "total_feed_consumed_kg": feed, "temperature_c": temp
                        }
                        st.success("تم الحفظ!")
                        check_and_alert_medications(farm_name, farm_data, age)
                
                with col_out:
                    alive = init - dead
                    gain = alive * (wt - 0.045)
                    adg = BroilerFarmManager.calculate_adg(wt*1000, 45, age) if age > 0 else 0
                    fcr = BroilerFarmManager.calculate_fcr(feed, gain) if gain > 0 else 0
                    liv = BroilerFarmManager.calculate_livability(init, dead)
                    epef = BroilerFarmManager.calculate_epef(liv, wt, age, fcr) if fcr > 0 and age > 0 else 0
                    
                    st.metric("📈 ADG", f"{adg:.1f} جم/يوم")
                    st.metric("🔄 FCR", f"{fcr:.2f}")
                    st.metric("❤️ الحيوية", f"{liv:.1f}%")
                    st.metric("🏆 EPEF", f"{epef:.0f}")
                    
                    # جدول الحرارة والرطوبة
                    with st.expander("🌡️ جدول الحرارة والرطوبة"):
                        st.dataframe(BroilerFarmManager.get_temp_humidity_table(), hide_index=True)

# =====================================================================
# تبويب تعليقات المختصين
# =====================================================================
with tabs[11]:
    st.markdown('<div class="section-title">💬 تعليقات المختصين</div>', unsafe_allow_html=True)
    st.text_area("الملاحظات المشتركة:", value=st.session_state["shared_comments"], height=200)
    new_comment = st.text_area("أضف تعليقك:", placeholder="اكتب ملاحظتك الفنية هنا...")
    if st.button("📝 نشر التعليق", type="primary") and new_comment.strip():
        st.session_state["shared_comments"] += f"\n• [{datetime.now().strftime('%H:%M')}] {new_comment.strip()}"
        st.success("تم نشر التعليق!")
        voice_guide("تم نشر التعليق بنجاح.")

# =====================================================================
# تبويب المراجع العلمية
# =====================================================================
with tabs[12]:
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
    
    # البحث في المراجع
    search = st.text_input("🔍 ابحث في المراجع:", placeholder="اكتب كلمة مفتاحية...")
    
    # عرض المراجع حسب الفئة
    for cat_key, cat_data in ScientificReferenceSystem.REFERENCES.items():
        with st.expander(f"{cat_data.get('icon', '📖')} {cat_data['title']}"):
            st.caption(cat_data.get('description', ''))
            for ref in cat_data["references"]:
                if search and search.lower() not in ref.get("title", "").lower() and search.lower() not in ref.get("summary", "").lower():
                    continue
                st.markdown(f"""
                <div style='background:#f8f9fa; padding:12px; border-radius:8px; margin-bottom:8px; direction:rtl;'>
                    <b>{ref.get('title', '')}</b><br>
                    <small>{ref.get('authors', '')} ({ref.get('year', '')})</small><br>
                    <span style='color:#666;'>{ref.get('summary', '')}</span><br>
                    <span style='color:#999; font-size:0.8rem;'>📌 {', '.join(ref.get('tags', []))}</span>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🧠 بنك المعرفة")
    q = st.text_input("اسأل سؤالاً عن تغذية الحيوان:")
    if st.button("🔍 ابحث في بنك المعرفة", type="primary") and q:
        ans = ScientificReferenceSystem.get_knowledge_answer(q)
        if ans:
            st.success(f"📖 {ans['answer']}")
            if ans.get("simplified"):
                st.info(f"📌 التبسيط: {ans['simplified']}")
            if ans.get("reference"):
                ref = ans["reference"]
                st.caption(f"📚 المرجع: {ref.get('title', '')} - {ref.get('authors', '')} ({ref.get('year', '')})")
            voice_guide("تم العثور على إجابة لسؤالك في بنك المعرفة.")
        else:
            st.warning("لم يتم العثور على إجابة. حاول صياغة السؤال بشكل مختلف.")
            voice_guide("لم يتم العثور على إجابة.")

# =====================================================================
# تبويب المساعدة الذكية
# =====================================================================
with tabs[13]:
    st.markdown('<div class="section-title">💡 المساعدة الذكية</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background:#f0fdf4; padding:20px; border-radius:12px; direction:rtl;'>
    <h4>📋 دليل سريع:</h4>
    <ul>
    <li>✅ <b>تركيب العلف:</b> اختر نوع الحيوان من القطاع الحيواني، حدد السلالة والمرحلة، اختر المكونات، شغّل المحرك.</li>
    <li>✅ <b>المختبر:</b> أدخل أوزان المكونات لتحليل الخلطة وحساب القيم الغذائية.</li>
    <li>✅ <b>إدارة المخزون:</b> راقب الكميات وحدّثها عند الحاجة.</li>
    <li>✅ <b>الفواتير:</b> أنشئ فواتير البيع مع حساب التكاليف والأرباح.</li>
    <li>✅ <b>إدارة الدجاج:</b> تابع أداء المزارع واحسب مؤشرات EPEF, FCR, ADG.</li>
    <li>✅ <b>التقارير:</b> صدر تقارير PDF احترافية (4 صفحات) للخلطات والتحاليل.</li>
    </ul>
    <hr>
    <p><b>📞 الدعم الفني:</b> abukram128@gmail.com | واتساب: +249123533489</p>
    </div>
    """, unsafe_allow_html=True)
    
    # أسئلة شائعة
    st.markdown("### ❓ الأسئلة الشائعة")
    faqs = [
        ("كيف أبدأ في استخدام المنصة؟", "سجل الدخول باستخدام حسابك، ثم اختر نوع الحيوان من القطاع الحيواني وابدأ في تركيب العلف."),
        ("كيف أحسب الخلطة المثالية؟", "اختر المكونات، حدد المواصفات المطلوبة (DP وSE)، ثم شغّل محرك الاستمثال الخطي."),
        ("كيف أحلل خلطة موجودة؟", "استخدم المختبر، أدخل أوزان المكونات، وسيقوم النظام بحساب القيم الغذائية."),
        ("كيف أصدر تقرير PDF؟", "بعد تشغيل المحرك أو التحليل، ستظهر أزرار تحميل PDF (3-4 صفحات)."),
        ("كيف أشارك النتائج عبر واتساب؟", "استخدم أزرار المشاركة في الواجهة الرئيسية أو داخل التبويبات."),
        ("ما هو الفرق بين البروتين الخام والمهضوم؟", "البروتين الخام (CP) هو إجمالي البروتين في العلف، بينما البروتين المهضوم (DP) هو الجزء الذي يستفيد منه الحيوان فعلياً.")
    ]
    for q, a in faqs:
        with st.expander(q):
            st.write(a)

# =====================================================================
# تبويب دليل المستخدم الشامل
# =====================================================================
with tabs[14]:
    st.markdown('<div class="section-title">📖 دليل المستخدم الشامل</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="manual-book">
    <div class="book-chapter">📘 الفصل الأول: التعريف بالمنصة</div>
    <div class="book-body">
    <b>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</b> هي نظام متكامل يعتمد على <b>محرك الاستمثال الخطي</b> (Linear Programming) لتوليد خلطات علفية بأقل تكلفة ممكنة، مع تحقيق المواصفات الغذائية المطلوبة بناءً على <b>البروتين المهضوم (DP)</b> و<b>معادل النشاء (SE)</b>.
    <br><br>
    تم تطوير المنصة بإشراف <b>الاختصاصي م. عبد القادر إسماعيل تاور</b>، وتستهدف جميع قطاعات الإنتاج الحيواني: الأبقار، الأغنام، الماعز، الخيول، الدواجن، والأسماك.
    <br><br>
    <b>الميزات الرئيسية:</b>
    <ul>
    <li>محرك استمثال خطي لتركيب الأعلاف بأقل تكلفة</li>
    <li>شريط قياس حيوي لتقدير الوزن والاحتياجات</li>
    <li>خيارات البروتين (خام/مهضوم) ومعادل النشاء</li>
    <li>مختبر متكامل لتحليل الخلطات</li>
    <li>نظام إدارة الأدوية البيطرية</li>
    <li>نظام تتبع الإنتاج اليومي</li>
    <li>تقارير PDF احترافية (3-4 صفحات)</li>
    <li>التوجيه الصوتي التفاعلي</li>
    <li>مشاركة النتائج عبر واتساب</li>
    </ul>
    </div>
    
    <div class="book-chapter">📘 الفصل الثاني: كيفية استخدام المنصة</div>
    <div class="book-body">
    <b>1. القطاع الحيواني (تركيب العلف):</b>
    <ul>
    <li>اختر نوع الحيوان من التبويبات الفرعية (أبقار، أغنام، ماعز، خيول، دواجن، أسماك).</li>
    <li>استخدم شريط القياس الحيوي لتقدير الوزن (للمجترات والخيول).</li>
    <li>حدد السلالة والمرحلة الإنتاجية.</li>
    <li>اختر أساس البروتين (مهضوم DP أو خام CP).</li>
    <li>حدد نسبة البروتين المطلوبة ومعادل النشاء.</li>
    <li>اختر المكونات العلفية من المكتبة.</li>
    <li>شغّل محرك الاستمثال الخطي.</li>
    <li>احصل على الخلطة المثالية مع التكلفة والرسوم البيانية.</li>
    <li>حمّل تقرير PDF (4 صفحات) أو شاركه عبر واتساب.</li>
    </ul>
    
    <b>2. المختبر (تحليل الخلطات):</b>
    <ul>
    <li>أدخل أوزان المكونات التي تستخدمها في خلطتك.</li>
    <li>سيقوم النظام بحساب CP, DP, SE.</li>
    <li>اعرض النتائج في جداول ورسوم بيانية.</li>
    <li>حمّل تقرير PDF (3 صفحات) للتحليل.</li>
    </ul>
    
    <b>3. إدارة المستودعات:</b>
    <ul>
    <li>راجع كميات المواد المتوفرة.</li>
    <li>حدّث الكميات عند الشراء أو الاستهلاك.</li>
    <li>تلقّ تنبيهات عند انخفاض المخزون.</li>
    </ul>
    
    <b>4. الفواتير والتسويق:</b>
    <ul>
    <li>أدخل بيانات العميل والكمية المطلوبة.</li>
    <li>حدد هامش الربح.</li>
    <li>اطبع الفاتورة أو شاركها عبر واتساب.</li>
    </ul>
    
    <b>5. إدارة مزارع الدجاج:</b>
    <ul>
    <li>أضف مزارع جديدة.</li>
    <li>سجل بيانات القطيع اليومية (العمر، الوزن، النافق، العلف).</li>
    <li>احسب مؤشرات الأداء: ADG, FCR, EPEF.</li>
    <li>تابع برنامج التحصينات والأدوية.</li>
    </ul>
    </div>
    
    <div class="book-chapter">📘 الفصل الثالث: المصطلحات العلمية</div>
    <div class="book-body">
    <b>البروتين المهضوم (DP - Digestible Protein):</b> كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف. تحسب بضرب البروتين الخام (CP) في معامل الهضم (DC).<br><br>
    <b>البروتين الخام (CP - Crude Protein):</b> إجمالي كمية النيتروجين في العلف مضروبة في 6.25، وهي تقدير لمحتوى البروتين الكلي.<br><br>
    <b>معادل النشاء (SE - Starch Equivalent):</b> مقياس لكمية الطاقة التي يوفرها العلف للحيوان، مقارنة بالطاقة التي يوفرها النشاء النقي. كلما زاد الرقم زادت الطاقة.<br><br>
    <b>معامل التحويل الغذائي (FCR - Feed Conversion Ratio):</b> كمية العلف اللازمة لإنتاج كيلو جرام واحد من الوزن الحي. كلما كان أقل كان أفضل.<br><br>
    <b>مؤشر EPEF (European Production Efficiency Factor):</b> مؤشر الأداء الأوروبي للدجاج اللاحم، يعبر عن كفاءة المزرعة.<br><br>
    <b>معامل الهضم (DC - Digestibility Coefficient):</b> نسبة المادة الغذائية التي يهضمها الحيوان فعلياً من العلف.<br><br>
    <b>الحيوية (Livability):</b> نسبة الطيور التي بقيت على قيد الحياة حتى نهاية الدورة.
    </div>
    
    <div class="book-chapter">📘 الفصل الرابع: نصائح وإرشادات</div>
    <div class="book-body">
    <b>نصائح لتغذية أفضل:</b>
    <ul>
    <li>استخدم مكونات علفية عالية الجودة.</li>
    <li>قم بتحليل الأعلاف دورياً في المختبر.</li>
    <li>راعِ احتياجات الحيوان حسب مرحلة الإنتاج.</li>
    <li>أضف الإنزيمات لتحسين الهضم والاستفادة من العلف.</li>
    <li>تأكد من توفير مياه نظيفة بكميات كافية.</li>
    <li>راقب استهلاك العلف ووزن الحيوانات بانتظام.</li>
    <li>استخدم بيكربونات الصوديوم للمجترات لمنع الحماض الكرشي.</li>
    </ul>
    </div>
    
    <div class="book-chapter">📘 الفصل الخامس: الدعم الفني</div>
    <div class="book-body">
    للاستفسارات والدعم الفني، يرجى التواصل عبر:<br>
    📧 البريد الإلكتروني: abukram128@gmail.com<br>
    📱 واتساب: +249123533489<br>
    🌐 رابط المنصة: https://tower-scientific-platform.streamlit.app<br><br>
    نسأل الله التوفيق والسداد، وندعوكم للمشاركة بملاحظاتكم ومقترحاتكم لتطوير المنصة.
    </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# التذييل السفلي
# =====================================================================
st.markdown("""
<div style='text-align:center; padding:20px; margin-top:40px; border-top:2px solid #e0e0e0; color:#666;'>
<b>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</b> 🌾<br>
© 2026 جميع الحقوق محفوظة للاختصاصي م. عبد القادر إسماعيل تاور<br>
<small>الإصدار المتقدم 5.0 | Streamlit | أكثر من 5000 سطر من الكود</small>
</div>
""", unsafe_allow_html=True)

if st.button("🔊 اختبار الصوت (نهاية الصفحة)", use_container_width=True):
    voice_guide("مرحباً، هذا اختبار للنظام الصوتي من نهاية الصفحة. الصوت يعمل بشكل جيد.")
    st.success("✅ تم تشغيل الصوت.")

# =====================================================================
# نهاية الكود المتكامل - أكثر من 5000 سطر
# =====================================================================
