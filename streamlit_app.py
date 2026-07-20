# ============================================================================
# منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف
# الإصدار: 4.5 (كامل متكامل - جميع التبويبات مع إدارة المزارع الشاملة)
# المشرف: الاختصاصي م. عبد القادر إسماعيل تاور
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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scipy.optimize import linprog
from scipy.spatial import ConvexHull
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
from datetime import datetime, timedelta
import hashlib
import secrets
from functools import lru_cache
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# ===== مكتبة الصوت =====
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# ===== مكتبات PDF واللغة العربية =====
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import arabic_reshaper
from bidi.algorithm import get_display
import io
import qrcode
from PIL import Image as PILImage
import matplotlib.pyplot as plt
import sqlite3
from dataclasses import dataclass, asdict

# ============================================================
# 1. تحسينات الأداء - التخزين المؤقت الذكي
# ============================================================
class SmartCache:
    """نظام تخزين مؤقت متطور مع إدارة ذكية"""
    _cache = {}
    _timestamps = {}
    
    @classmethod
    def get(cls, key: str, ttl: int = 300):
        if key in cls._cache:
            if (datetime.now() - cls._timestamps[key]).seconds < ttl:
                return cls._cache[key]
        return None
    
    @classmethod
    def set(cls, key: str, value):
        cls._cache[key] = value
        cls._timestamps[key] = datetime.now()
    
    @classmethod
    def clear(cls):
        cls._cache.clear()
        cls._timestamps.clear()

# ============================================================
# 2. دوال الصوت والنصوص (محسنة)
# ============================================================
def play_audio_from_text(text, lang="ar", speed=1.0):
    """توليد وتشغيل صوت من نص مع تحكم بالسرعة"""
    if not GTTS_AVAILABLE:
        st.warning("⚠️ مكتبة gTTS غير مثبتة")
        return
    try:
        tts = gTTS(text=text, lang=lang, slow=(speed < 1.0))
        audio_file = io.BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        audio_b64 = base64.b64encode(audio_file.read()).decode()
        st.components.v1.html(
            f'<audio autoplay controls style="width:100%;"><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>',
            height=60
        )
    except Exception as e:
        st.warning(f"⚠️ تعذر تشغيل الصوت: {e}")

def guide_section(tab_name, guide_text):
    """عرض دليل استخدام للتبويب مع خيار صوتي ونصي"""
    with st.expander(f"📘 دليل استخدام {tab_name}", expanded=False):
        st.markdown(f"<div style='background:#f0f8ff; padding:15px; border-radius:10px; direction:rtl;'>{guide_text}</div>", unsafe_allow_html=True)
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if st.button(f"🔊 تشغيل الدليل صوتياً ({tab_name})"):
                play_audio_from_text(guide_text)
        with col_g2:
            st.caption("يمكنك قراءة الدليل أعلاه أو الاستماع إليه.")

def play_welcome_audio():
    if GTTS_AVAILABLE:
        play_audio_from_text("مرحباً بك في منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف، تحت إشراف الاختصاصي عبد القادر إسماعيل تاور.")

# ============================================================
# 3. نظام قاعدة البيانات (كامل مع فهارس)
# ============================================================
class DatabaseManager:
    def __init__(self, db_path="tower_platform.db"):
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
                     salt TEXT,
                     iterations INTEGER,
                     role TEXT,
                     full_name TEXT,
                     email TEXT,
                     phone TEXT,
                     two_factor_secret TEXT,
                     last_login TEXT,
                     login_attempts INTEGER DEFAULT 0,
                     is_locked BOOLEAN DEFAULT 0,
                     created_date TEXT)''')
        
        # جدول دورات المزارع
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
                     created_date TEXT)''')
        
        # جدول خلطات الأعلاف
        c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas (
                     formula_id TEXT PRIMARY KEY,
                     formula_name TEXT,
                     animal_type TEXT,
                     target_dp REAL,
                     target_se REAL,
                     ingredients TEXT,
                     total_cost REAL,
                     created_by TEXT,
                     created_date TEXT)''')
        
        # جدول الفواتير
        c.execute('''CREATE TABLE IF NOT EXISTS invoices (
                     invoice_id TEXT PRIMARY KEY,
                     customer_name TEXT,
                     formula_id TEXT,
                     quantity_ton REAL,
                     unit_price REAL,
                     total_price REAL,
                     status TEXT,
                     created_by TEXT,
                     created_date TEXT)''')
        
        # جدول تاريخ الأسعار
        c.execute('''CREATE TABLE IF NOT EXISTS price_history (
                     record_id TEXT PRIMARY KEY,
                     ingredient_name TEXT,
                     price REAL,
                     currency TEXT,
                     country TEXT,
                     city TEXT,
                     record_date TEXT,
                     recorded_by TEXT)''')
        
        # جدول سجل التدقيق
        c.execute('''CREATE TABLE IF NOT EXISTS audit_log (
                     log_id TEXT PRIMARY KEY,
                     user_id TEXT,
                     action TEXT,
                     details TEXT,
                     timestamp TEXT)''')
        
        # ===== جداول إدارة المزارع (المضافة) =====
        # جدول المزارع الرئيسي
        c.execute('''CREATE TABLE IF NOT EXISTS farms (
                     farm_id TEXT PRIMARY KEY,
                     farm_name TEXT UNIQUE,
                     farm_type TEXT,
                     owner_name TEXT,
                     location TEXT,
                     phone TEXT,
                     email TEXT,
                     established_date TEXT,
                     total_area REAL,
                     latitude REAL,
                     longitude REAL,
                     status TEXT DEFAULT 'نشط',
                     notes TEXT,
                     created_by TEXT,
                     created_date TEXT)''')
        
        # جدول أنواع الإنتاج
        c.execute('''CREATE TABLE IF NOT EXISTS production_types (
                     type_id TEXT PRIMARY KEY,
                     farm_id TEXT,
                     production_type TEXT,
                     sub_type TEXT,
                     start_date TEXT,
                     expected_end_date TEXT,
                     status TEXT,
                     notes TEXT,
                     FOREIGN KEY (farm_id) REFERENCES farms(farm_id))''')
        
        # جدول الدواجن (لاحم)
        c.execute('''CREATE TABLE IF NOT EXISTS poultry_broiler (
                     record_id TEXT PRIMARY KEY,
                     farm_id TEXT,
                     cycle_number INTEGER,
                     breed TEXT,
                     source TEXT,
                     initial_birds INTEGER,
                     current_birds INTEGER,
                     daily_mortality INTEGER,
                     total_mortality INTEGER,
                     culled_birds INTEGER,
                     average_weight REAL,
                     feed_consumption REAL,
                     feed_conversion_ratio REAL,
                     water_consumption REAL,
                     water_conversion_ratio REAL,
                     temperature REAL,
                     humidity REAL,
                     vaccination_records TEXT,
                     medication_records TEXT,
                     lighting_schedule TEXT,
                     feeding_schedule TEXT,
                     record_date TEXT,
                     notes TEXT,
                     FOREIGN KEY (farm_id) REFERENCES farms(farm_id))''')
        
        # جدول الدواجن (بياض)
        c.execute('''CREATE TABLE IF NOT EXISTS poultry_layer (
                     record_id TEXT PRIMARY KEY,
                     farm_id TEXT,
                     flock_id TEXT,
                     breed TEXT,
                     source TEXT,
                     initial_birds INTEGER,
                     current_birds INTEGER,
                     daily_mortality INTEGER,
                     total_mortality INTEGER,
                     daily_eggs INTEGER,
                     total_eggs INTEGER,
                     egg_weight REAL,
                     egg_color TEXT,
                     egg_size TEXT,
                     shell_quality TEXT,
                     feed_consumption REAL,
                     feed_conversion_ratio REAL,
                     water_consumption REAL,
                     temperature REAL,
                     humidity REAL,
                     vaccination_records TEXT,
                     medication_records TEXT,
                     lighting_schedule TEXT,
                     record_date TEXT,
                     notes TEXT,
                     FOREIGN KEY (farm_id) REFERENCES farms(farm_id))''')
        
        # جدول الأغنام والماعز
        c.execute('''CREATE TABLE IF NOT EXISTS sheep_goats (
                     record_id TEXT PRIMARY KEY,
                     farm_id TEXT,
                     flock_id TEXT,
                     animal_type TEXT,
                     breed TEXT,
                     source TEXT,
                     total_animals INTEGER,
                     daily_mortality INTEGER,
                     total_mortality INTEGER,
                     average_weight REAL,
                     feed_consumption REAL,
                     water_consumption REAL,
                     milk_production REAL,
                     wool_production REAL,
                     wool_quality TEXT,
                     lambing_rate REAL,
                     vaccination_records TEXT,
                     medication_records TEXT,
                     record_date TEXT,
                     notes TEXT,
                     FOREIGN KEY (farm_id) REFERENCES farms(farm_id))''')
        
        # جدول الأبقار
        c.execute('''CREATE TABLE IF NOT EXISTS cattle (
                     record_id TEXT PRIMARY KEY,
                     farm_id TEXT,
                     herd_id TEXT,
                     breed TEXT,
                     source TEXT,
                     total_animals INTEGER,
                     daily_mortality INTEGER,
                     total_mortality INTEGER,
                     average_weight REAL,
                     feed_consumption REAL,
                     water_consumption REAL,
                     milk_production REAL,
                     fat_percentage REAL,
                     protein_percentage REAL,
                     somatic_cell_count INTEGER,
                     calving_interval REAL,
                     vaccination_records TEXT,
                     medication_records TEXT,
                     record_date TEXT,
                     notes TEXT,
                     FOREIGN KEY (farm_id) REFERENCES farms(farm_id))''')
        
        # جدول الأسماك
        c.execute('''CREATE TABLE IF NOT EXISTS fish (
                     record_id TEXT PRIMARY KEY,
                     farm_id TEXT,
                     pond_id TEXT,
                     species TEXT,
                     initial_fish INTEGER,
                     current_fish INTEGER,
                     daily_mortality INTEGER,
                     total_mortality INTEGER,
                     average_weight REAL,
                     feed_consumption REAL,
                     water_temperature REAL,
                     oxygen_level REAL,
                     ph_level REAL,
                     vaccination_records TEXT,
                     medication_records TEXT,
                     record_date TEXT,
                     notes TEXT,
                     FOREIGN KEY (farm_id) REFERENCES farms(farm_id))''')
        
        # جدول السجل اليومي
        c.execute('''CREATE TABLE IF NOT EXISTS daily_production (
                     record_id TEXT PRIMARY KEY,
                     farm_id TEXT,
                     production_type TEXT,
                     date TEXT,
                     morning_observations TEXT,
                     evening_observations TEXT,
                     feed_amount REAL,
                     water_amount REAL,
                     health_status TEXT,
                     special_notes TEXT,
                     recorded_by TEXT,
                     FOREIGN KEY (farm_id) REFERENCES farms(farm_id))''')
        
        # إنشاء الفهارس لتحسين الأداء
        c.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_farm_cycles_date ON farm_cycles(start_date)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(created_date)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_farms_name ON farms(farm_name)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_farms_type ON farms(farm_type)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_production_type ON production_types(production_type)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_broiler_date ON poultry_broiler(record_date)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_layer_date ON poultry_layer(record_date)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_sheep_date ON sheep_goats(record_date)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_cattle_date ON cattle(record_date)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_fish_date ON fish(record_date)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_daily_production ON daily_production(date)')
        
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
    
    def update_record(self, table: str, record_id: str, data: dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        set_clause = ', '.join([f"{k}=?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE record_id=?"
        c.execute(query, list(data.values()) + [record_id])
        conn.commit()
        conn.close()
    
    def log_action(self, user_id: str, action: str, details: str = ""):
        """تسجيل إجراءات المستخدم"""
        log_id = secrets.token_hex(16)
        self.insert_record('audit_log', {
            'log_id': log_id,
            'user_id': user_id,
            'action': action,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })

# ============================================================
# 4. نظام المصادقة المحسن
# ============================================================
class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self._create_default_admin()
    
    def _create_default_admin(self):
        users = self.db.execute_query("SELECT * FROM users WHERE username='admin'")
        if not users:
            self.create_user('admin', 'admin123', 'owner', 'مدير النظام', 'admin@tower.com', '+249123456789')
    
    def create_user(self, username, password, role, full_name, email, phone):
        user_id = secrets.token_hex(16)
        salt = secrets.token_hex(16)
        iterations = 100000
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations
        ).hex()
        
        data = {
            'user_id': user_id,
            'username': username,
            'password_hash': password_hash,
            'salt': salt,
            'iterations': iterations,
            'role': role,
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'two_factor_secret': secrets.token_hex(16),
            'last_login': datetime.now().isoformat(),
            'login_attempts': 0,
            'is_locked': 0,
            'created_date': datetime.now().isoformat()
        }
        self.db.insert_record('users', data)
        return user_id
    
    def authenticate(self, username, password):
        users = self.db.execute_query("SELECT * FROM users WHERE username=?", (username,))
        if users:
            user = users[0]
            if user[11] == 1:  # is_locked
                return None, "الحساب مقفل. يرجى التواصل مع المسؤول."
            
            if user[10] >= 5:  # login_attempts
                self.db.update_record('users', user[0], {'is_locked': 1})
                return None, "تم قفل الحساب لكثرة المحاولات الفاشلة."
            
            salt = user[3]
            iterations = user[4]
            hash_value = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                iterations
            ).hex()
            
            if hash_value == user[2]:
                self.db.update_record('users', user[0], {
                    'last_login': datetime.now().isoformat(),
                    'login_attempts': 0,
                    'is_locked': 0
                })
                return {
                    'user_id': user[0],
                    'username': user[1],
                    'role': user[5],
                    'full_name': user[6],
                    'email': user[7],
                    'phone': user[8]
                }, None
            else:
                new_attempts = user[10] + 1
                self.db.update_record('users', user[0], {'login_attempts': new_attempts})
                return None, f"كلمة مرور غير صحيحة. متبقي {5 - new_attempts} محاولات."
        
        return None, "اسم المستخدم غير موجود."

# ============================================================
# 5. نظام التنبؤ بالأسعار
# ============================================================
class PricePredictor:
    def __init__(self):
        self.db = DatabaseManager()
    
    @lru_cache(maxsize=128)
    def get_ingredient_prices(self, ingredient_name, days=30):
        results = self.db.execute_query(
            "SELECT * FROM price_history WHERE ingredient_name=? ORDER BY record_date DESC LIMIT ?",
            (ingredient_name, days)
        )
        return [{
            'record_id': r[0],
            'ingredient_name': r[1],
            'price': r[2],
            'currency': r[3],
            'country': r[4],
            'city': r[5],
            'record_date': r[6]
        } for r in results]
    
    def predict_price(self, ingredient_name, days_ahead=7):
        prices = self.get_ingredient_prices(ingredient_name, 30)
        if len(prices) < 5:
            return {'prediction': None, 'confidence': 0}
        
        price_list = [p['price'] for p in prices]
        weights = np.exp(np.linspace(0, 1, len(price_list)))
        weighted_avg = np.average(price_list, weights=weights)
        
        if len(price_list) > 1:
            x = np.arange(len(price_list))
            slope = np.polyfit(x, price_list, 1)[0]
            trend = slope / np.mean(price_list) if np.mean(price_list) > 0 else 0
        else:
            trend = 0
        
        prediction = weighted_avg + (trend * weighted_avg * days_ahead / 30)
        
        return {
            'prediction': max(0, prediction),
            'confidence': min(1, len(price_list) / 30),
            'current_price': price_list[0] if price_list else None,
            'trend': 'up' if trend > 0.01 else 'down' if trend < -0.01 else 'stable',
            'trend_percent': trend * 100
        }

# ============================================================
# 6. نظام إدارة المزارع الشامل
# ============================================================
class FarmManagementSystem:
    """نظام متكامل لإدارة المزارع بأنواعها المختلفة"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    # ===== دوال إدارة المزارع =====
    def add_farm(self, farm_data):
        """إضافة مزرعة جديدة"""
        farm_id = secrets.token_hex(16)
        data = {
            'farm_id': farm_id,
            'farm_name': farm_data['farm_name'],
            'farm_type': farm_data['farm_type'],
            'owner_name': farm_data['owner_name'],
            'location': farm_data['location'],
            'phone': farm_data['phone'],
            'email': farm_data.get('email', ''),
            'established_date': farm_data['established_date'],
            'total_area': farm_data.get('total_area', 0.0),
            'latitude': farm_data.get('latitude', 0.0),
            'longitude': farm_data.get('longitude', 0.0),
            'status': 'نشط',
            'notes': farm_data.get('notes', ''),
            'created_by': st.session_state.get('user_id', 'system'),
            'created_date': datetime.now().isoformat()
        }
        self.db.insert_record('farms', data)
        return farm_id
    
    def update_farm(self, farm_id, farm_data):
        """تحديث بيانات مزرعة"""
        self.db.update_record('farms', farm_id, farm_data)
    
    def delete_farm(self, farm_id):
        """حذف مزرعة (تعطيل فقط)"""
        self.db.update_record('farms', farm_id, {'status': 'محذوف'})
    
    def get_farms(self, status='نشط'):
        """الحصول على قائمة المزارع"""
        if status == 'الكل':
            return self.db.execute_query("SELECT * FROM farms ORDER BY created_date DESC")
        return self.db.execute_query(
            "SELECT * FROM farms WHERE status=? ORDER BY created_date DESC",
            (status,)
        )
    
    def get_farm_by_id(self, farm_id):
        """الحصول على مزرعة محددة"""
        result = self.db.execute_query("SELECT * FROM farms WHERE farm_id=?", (farm_id,))
        return result[0] if result else None
    
    def search_farms(self, keyword):
        """البحث في المزارع"""
        return self.db.execute_query(
            "SELECT * FROM farms WHERE farm_name LIKE ? OR owner_name LIKE ? OR location LIKE ?",
            (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%')
        )
    
    # ===== دوال إدارة أنواع الإنتاج =====
    def add_production_type(self, farm_id, production_type, sub_type, expected_end_date=None):
        """إضافة نوع إنتاج للمزرعة"""
        type_id = secrets.token_hex(16)
        data = {
            'type_id': type_id,
            'farm_id': farm_id,
            'production_type': production_type,
            'sub_type': sub_type,
            'start_date': datetime.now().isoformat(),
            'expected_end_date': expected_end_date or '',
            'status': 'نشط',
            'notes': ''
        }
        self.db.insert_record('production_types', data)
        return type_id
    
    def get_production_types(self, farm_id):
        """الحصول على أنواع الإنتاج لمزرعة"""
        return self.db.execute_query(
            "SELECT * FROM production_types WHERE farm_id=? AND status='نشط' ORDER BY start_date DESC",
            (farm_id,)
        )
    
    def update_production_status(self, type_id, status):
        """تحديث حالة نوع الإنتاج"""
        self.db.update_record('production_types', type_id, {'status': status})
    
    # ===== دوال الدواجن اللاحم =====
    def add_poultry_broiler_record(self, data):
        """إضافة سجل دواجن لاحم"""
        record_id = secrets.token_hex(16)
        if data.get('feed_consumption', 0) > 0 and data.get('average_weight', 0) > 0 and data.get('current_birds', 1) > 0:
            fcr = data['feed_consumption'] / (data['average_weight'] * data.get('current_birds', 1))
        else:
            fcr = 0.0
        
        data['record_id'] = record_id
        data['record_date'] = datetime.now().isoformat()
        data['feed_conversion_ratio'] = fcr
        data['water_conversion_ratio'] = data.get('water_consumption', 0) / data.get('feed_consumption', 1) if data.get('feed_consumption', 0) > 0 else 0
        
        self.db.insert_record('poultry_broiler', data)
        return record_id
    
    def get_poultry_broiler_records(self, farm_id, limit=30):
        """الحصول على سجلات الدواجن اللاحم"""
        return self.db.execute_query(
            "SELECT * FROM poultry_broiler WHERE farm_id=? ORDER BY record_date DESC LIMIT ?",
            (farm_id, limit)
        )
    
    def get_poultry_broiler_summary(self, farm_id):
        """الحصول على ملخص الدواجن اللاحم"""
        records = self.get_poultry_broiler_records(farm_id, limit=100)
        if not records:
            return None
        
        summary = {
            'total_cycles': len(set(r[2] for r in records)),
            'total_birds': sum(r[5] for r in records),
            'current_birds': sum(r[6] for r in records),
            'avg_weight': sum(r[10] for r in records) / len(records) if records else 0,
            'avg_fcr': sum(r[12] for r in records) / len(records) if records else 0,
            'total_mortality': sum(r[8] for r in records),
        }
        return summary
    
    # ===== دوال الدواجن البياض =====
    def add_poultry_layer_record(self, data):
        """إضافة سجل دواجن بياض"""
        record_id = secrets.token_hex(16)
        data['record_id'] = record_id
        data['record_date'] = datetime.now().isoformat()
        self.db.insert_record('poultry_layer', data)
        return record_id
    
    def get_poultry_layer_records(self, farm_id, limit=30):
        """الحصول على سجلات الدواجن البياض"""
        return self.db.execute_query(
            "SELECT * FROM poultry_layer WHERE farm_id=? ORDER BY record_date DESC LIMIT ?",
            (farm_id, limit)
        )
    
    def get_poultry_layer_summary(self, farm_id):
        """الحصول على ملخص الدواجن البياض"""
        records = self.get_poultry_layer_records(farm_id, limit=100)
        if not records:
            return None
        
        summary = {
            'total_flocks': len(set(r[2] for r in records)),
            'total_birds': sum(r[5] for r in records),
            'current_birds': sum(r[6] for r in records),
            'avg_eggs_daily': sum(r[9] for r in records) / len(records) if records else 0,
            'avg_egg_weight': sum(r[11] for r in records) / len(records) if records else 0,
            'total_eggs': sum(r[9] for r in records),
        }
        return summary
    
    # ===== دوال الأغنام والماعز =====
    def add_sheep_goat_record(self, data):
        """إضافة سجل أغنام وماعز"""
        record_id = secrets.token_hex(16)
        data['record_id'] = record_id
        data['record_date'] = datetime.now().isoformat()
        self.db.insert_record('sheep_goats', data)
        return record_id
    
    def get_sheep_goat_records(self, farm_id, limit=30):
        """الحصول على سجلات الأغنام والماعز"""
        return self.db.execute_query(
            "SELECT * FROM sheep_goats WHERE farm_id=? ORDER BY record_date DESC LIMIT ?",
            (farm_id, limit)
        )
    
    # ===== دوال الأبقار =====
    def add_cattle_record(self, data):
        """إضافة سجل أبقار"""
        record_id = secrets.token_hex(16)
        data['record_id'] = record_id
        data['record_date'] = datetime.now().isoformat()
        self.db.insert_record('cattle', data)
        return record_id
    
    def get_cattle_records(self, farm_id, limit=30):
        """الحصول على سجلات الأبقار"""
        return self.db.execute_query(
            "SELECT * FROM cattle WHERE farm_id=? ORDER BY record_date DESC LIMIT ?",
            (farm_id, limit)
        )
    
    # ===== دوال الأسماك =====
    def add_fish_record(self, data):
        """إضافة سجل أسماك"""
        record_id = secrets.token_hex(16)
        data['record_id'] = record_id
        data['record_date'] = datetime.now().isoformat()
        self.db.insert_record('fish', data)
        return record_id
    
    def get_fish_records(self, farm_id, limit=30):
        """الحصول على سجلات الأسماك"""
        return self.db.execute_query(
            "SELECT * FROM fish WHERE farm_id=? ORDER BY record_date DESC LIMIT ?",
            (farm_id, limit)
        )
    
    # ===== دوال السجل اليومي =====
    def add_daily_production(self, data):
        """إضافة سجل إنتاج يومي"""
        record_id = secrets.token_hex(16)
        data['record_id'] = record_id
        data['date'] = datetime.now().isoformat()
        data['recorded_by'] = st.session_state.get('user_id', 'system')
        self.db.insert_record('daily_production', data)
        return record_id
    
    def get_daily_production(self, farm_id, days=7):
        """الحصول على السجلات اليومية"""
        return self.db.execute_query(
            "SELECT * FROM daily_production WHERE farm_id=? ORDER BY date DESC LIMIT ?",
            (farm_id, days)
        )
    
    # ===== دوال التقارير والإحصائيات =====
    def get_farm_statistics(self, farm_id):
        """الحصول على إحصائيات شاملة للمزرعة"""
        stats = {
            'farm_info': self.get_farm_by_id(farm_id),
            'production_types': self.get_production_types(farm_id),
            'broiler': self.get_poultry_broiler_summary(farm_id),
            'layer': self.get_poultry_layer_summary(farm_id),
            'daily_records': self.get_daily_production(farm_id)
        }
        return stats
    
    def generate_farm_report(self, farm_id):
        """توليد تقرير شامل للمزرعة"""
        stats = self.get_farm_statistics(farm_id)
        farm_info = stats['farm_info']
        if not farm_info:
            return "المزرعة غير موجودة"
        
        report = f"""
        ===== تقرير المزرعة =====
        اسم المزرعة: {farm_info[1]}
        المالك: {farm_info[3]}
        الموقع: {farm_info[4]}
        التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        
        --- أنواع الإنتاج ---
        """
        
        for pt in stats.get('production_types', []):
            report += f"\n- {pt[2]} ({pt[3]}) - {pt[4]}"
        
        if stats.get('broiler'):
            broiler = stats['broiler']
            report += f"""
        
        --- الدواجن اللاحم ---
        إجمالي الدورات: {broiler['total_cycles']}
        إجمالي الطيور: {broiler['total_birds']}
        الطيور الحالية: {broiler['current_birds']}
        متوسط الوزن: {broiler['avg_weight']:.2f} كجم
        معامل التحويل: {broiler['avg_fcr']:.2f}
        """
        
        if stats.get('layer'):
            layer = stats['layer']
            report += f"""
        
        --- الدواجن البياض ---
        عدد القطعان: {layer['total_flocks']}
        إجمالي الطيور: {layer['total_birds']}
        الطيور الحالية: {layer['current_birds']}
        متوسط البيض اليومي: {layer['avg_eggs_daily']:.0f}
        متوسط وزن البيضة: {layer['avg_egg_weight']:.1f} جم
        """
        
        return report

# ============================================================
# 7. المراجع العلمية
# ============================================================
class ScientificReferenceSystem:
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان",
            "references": [
                {"id": "REF001", "authors": "McDonald, P., Edwards, R.A., Greenhalgh, J.F.D., Morgan, C.A.",
                 "year": 2011, "title": "Animal Nutrition", "publisher": "Pearson Education",
                 "edition": "7th Edition", "isbn": "978-1408204238",
                 "summary": "المرجع الأساسي في تغذية الحيوان، يغطي جميع جوانب التغذية من الهضم إلى متطلبات العناصر الغذائية."},
                {"id": "REF002", "authors": "Cheeke, P.R., Dierenfeld, E.S.",
                 "year": 2010, "title": "Comparative Animal Nutrition and Metabolism",
                 "publisher": "CABI", "isbn": "978-1845936310",
                 "summary": "مقارنة بين آليات التغذية والتمثيل الغذائي في مختلف أنواع الحيوانات."}
            ]
        },
        "protein_amino_acids": {
            "title": "البروتين والأحماض الأمينية",
            "references": [
                {"id": "REF003", "authors": "NRC (National Research Council)",
                 "year": 2012, "title": "Nutrient Requirements of Swine",
                 "publisher": "National Academies Press", "edition": "11th Revised Edition",
                 "isbn": "978-0309214230", "summary": "المرجع الرسمي لمتطلبات الخنازير."},
                {"id": "REF004", "authors": "NRC (National Research Council)",
                 "year": 2001, "title": "Nutrient Requirements of Dairy Cattle",
                 "publisher": "National Academies Press", "edition": "7th Revised Edition",
                 "isbn": "978-0309069977", "summary": "المرجع الأساسي في تغذية أبقار الحليب."}
            ]
        },
        "poultry": {
            "title": "تغذية الدواجن",
            "references": [
                {"id": "REF010", "authors": "Leeson, S., Summers, J.D.",
                 "year": 2009, "title": "Commercial Poultry Nutrition",
                 "publisher": "Nottingham University Press", "edition": "3rd Edition",
                 "isbn": "978-1904761578", "summary": "المرجع العملي في تغذية الدواجن التجارية."},
                {"id": "REF020", "authors": "Ross 308 Broiler Management Guide",
                 "year": 2020, "title": "Ross Broiler Management Handbook",
                 "publisher": "Aviagen", "summary": "الدليل الشامل لإدارة الدجاج اللاحم سلالة روس."}
            ]
        }
    }
    
    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم (Digestible Protein) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف. يتم حسابه بضرب نسبة البروتين الخام في معامل الهضم لكل مادة علفية.",
            "reference": "REF001",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (Starch Equivalent - SE) هو مقياس لكمية الطاقة التي يوفرها العلف للحيوان، مقارنة بالطاقة التي يوفرها النشاء النقي.",
            "reference": "REF006",
            "simplified": "معادل النشاء يقيس كمية الطاقة في العلف."
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
                ref = ScientificReferenceSystem.get_reference(value.get("reference", ""))
                return {
                    "answer": value["answer"],
                    "simplified": value.get("simplified", value["answer"]),
                    "reference": ref
                }
        return None

# ============================================================
# 8. مكتبة الأعلاف الكاملة
# ============================================================
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
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5}
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5}
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0}
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم الفايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
        "خميرة الخبز (Yeast)": {"CP": 45.0, "DC": 0.85, "SE": 35.0, "NDF": 5.0, "ADF": 2.0, "EE": 2.5, "ASH": 7.0}
    }
}

# ============================================================
# 9. نظام أسعار المدن والمخازن
# ============================================================
CITY_PRICES_FILE = "city_prices.json"

def load_city_prices():
    if os.path.exists(CITY_PRICES_FILE):
        try:
            with open(CITY_PRICES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_city_prices(data):
    with open(CITY_PRICES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

CITY_CUSTOM_PRICES = load_city_prices()

# ============================================================
# 10. إدارة المخزون
# ============================================================
class InventoryManager:
    @staticmethod
    def initialize_inventory():
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
                        "supplier": "غير محدد"
                    }
    
    @staticmethod
    def check_stock_levels():
        warnings = {}
        for item, data in st.session_state["inventory"].items():
            qty = data["quantity"]
            threshold = data["min_threshold"]
            if qty <= 0:
                warnings[item] = "نفذ المخزون"
            elif qty < threshold:
                warnings[item] = "منخفض"
        return warnings
    
    @staticmethod
    def update_stock(item, quantity):
        if item in st.session_state["inventory"]:
            st.session_state["inventory"][item]["quantity"] = quantity
            st.session_state["inventory"][item]["last_updated"] = datetime.now().isoformat()
            return True
        return False

InventoryManager.initialize_inventory()

# ============================================================
# 11. مولد PDF الاحترافي
# ============================================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        if os.path.exists("Amiri-Regular.ttf"):
            try:
                pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
                self.font_name = 'Amiri'
            except:
                pass
    
    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, include_charts=True):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        
        def p(text, size=12, align=TA_RIGHT, color=HexColor('#000000')):
            safe_text = self._fix_arabic_text(str(text))
            return Paragraph(safe_text, ParagraphStyle('style', fontName=self.font_name, fontSize=size, alignment=align, textColor=color, spaceAfter=6, leading=size*1.5))
        
        story.append(p("تقرير فني شامل - منصة تاور العلمية", size=22, align=TA_CENTER, color=HexColor('#1b5e20')))
        story.append(Spacer(1, 12))
        
        for line in [
            f"المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور",
            f"الموقع الجغرافي: {city}",
            f"الفصيل المستهدف: {breed}",
            f"تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ]:
            story.append(p(line, size=11))
        
        story.append(Spacer(1, 15))
        
        tdata = [
            [self._fix_arabic_text('المعيار'), self._fix_arabic_text('القيمة')],
            [self._fix_arabic_text('البروتين المهضوم (DP)'), f'{target_dp:.2f}%'],
            [self._fix_arabic_text('معادل النشاء (SE)'), f'{computed_se:.2f} وحدة'],
            [self._fix_arabic_text('التكلفة للطن'), f'${cost:.2f} ({local_cost:,.2f} {local_sym})']
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
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        
        story.append(p("المقادير المعتمدة لتركيب الطن الواحد:", size=14, color=HexColor('#2e7d32')))
        story.append(Spacer(1, 10))
        
        ing_data = [[self._fix_arabic_text('المكون'), self._fix_arabic_text('النسبة %'), self._fix_arabic_text('كجم/طن')]]
        for ing, pct in formula.items():
            ing_data.append([self._fix_arabic_text(ing), f'{pct:.2f}%', f'{pct*10:.1f}'])
        
        t2 = Table(ing_data, colWidths=[200, 150, 150])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')]),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
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
                ax.legend([self._fix_arabic_text(n) for n in names], title=self._fix_arabic_text("المكونات"),
                         loc='center left', bbox_to_anchor=(1,0,0.5,1), fontsize=8)
                ax.set_title(self._fix_arabic_text('توزيع المكونات'), fontsize=12)
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=400, height=230))
            except:
                pass
        
        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026 | تحت إشراف م. عبد القادر إسماعيل تاور", size=9, align=TA_CENTER, color=HexColor('#666666')))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _fix_arabic_text(self, text):
        try:
            reshaped = arabic_reshaper.reshape(str(text))
            return get_display(reshaped)
        except:
            return str(text)

pdf_generator = ProfessionalPDFGenerator()

# ============================================================
# 12. واجهة إدارة المزارع (وظيفة العرض الكاملة)
# ============================================================
def render_farm_management():
    """عرض واجهة إدارة المزارع المتكاملة"""
    
    st.markdown('<div class="section-title">🏢 إدارة المزارع - النظام المتكامل</div>', unsafe_allow_html=True)
    
    farm_manager = FarmManagementSystem()
    
    farm_tabs = st.tabs([
        "🏢 المزارع", 
        "🐔 الدواجن اللاحم", 
        "🥚 الدواجن البياض",
        "🐑 الأغنام والماعز",
        "🐄 الأبقار",
        "🐟 الأسماك",
        "📊 الإحصائيات",
        "📋 السجل اليومي"
    ])
    
    # ===== التبويب 1: المزارع =====
    with farm_tabs[0]:
        st.markdown("#### 📝 إضافة مزرعة جديدة")
        
        with st.form("add_farm_form"):
            col1, col2 = st.columns(2)
            with col1:
                farm_name = st.text_input("اسم المزرعة*", placeholder="مزرعة النجاح")
                farm_type = st.selectbox("نوع المزرعة*", ["دواجن", "أغنام وماعز", "أبقار", "أسماك", "مختلط"])
                owner_name = st.text_input("اسم المالك*", placeholder="فلان بن فلان")
                location = st.text_input("الموقع*", placeholder="الخرطوم - بحري")
                phone = st.text_input("رقم الهاتف*", placeholder="+249123456789")
                
            with col2:
                email = st.text_input("البريد الإلكتروني", placeholder="farm@example.com")
                established_date = st.date_input("تاريخ التأسيس", datetime.now())
                total_area = st.number_input("المساحة الكلية (فدان)", min_value=0.1, value=10.0, step=0.5)
                latitude = st.number_input("خط العرض", min_value=-90.0, max_value=90.0, value=15.0, step=0.001)
                longitude = st.number_input("خط الطول", min_value=-180.0, max_value=180.0, value=30.0, step=0.001)
            
            notes = st.text_area("ملاحظات", placeholder="أي معلومات إضافية عن المزرعة")
            
            submit_farm = st.form_submit_button("➕ إضافة مزرعة", type="primary")
            if submit_farm:
                if farm_name and owner_name and location and phone:
                    try:
                        farm_id = farm_manager.add_farm({
                            'farm_name': farm_name,
                            'farm_type': farm_type,
                            'owner_name': owner_name,
                            'location': location,
                            'phone': phone,
                            'email': email,
                            'established_date': established_date.isoformat(),
                            'total_area': total_area,
                            'latitude': latitude,
                            'longitude': longitude,
                            'notes': notes
                        })
                        st.success(f"✅ تمت إضافة المزرعة '{farm_name}' بنجاح!")
                        if farm_type != "مختلط":
                            farm_manager.add_production_type(farm_id, farm_type, "عام")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ حدث خطأ: {e}")
                else:
                    st.error("⚠️ يرجى تعبئة الحقول المطلوبة (*)")
        
        st.markdown("#### 📋 قائمة المزارع")
        
        col_search, col_filter = st.columns([3, 1])
        with col_search:
            search_keyword = st.text_input("🔍 بحث في المزارع", placeholder="اسم المزرعة، المالك، أو الموقع...")
        with col_filter:
            filter_status = st.selectbox("الحالة", ["نشط", "الكل", "محذوف"])
        
        if search_keyword:
            farms = farm_manager.search_farms(search_keyword)
        else:
            farms = farm_manager.get_farms(status=filter_status)
        
        if farms:
            for farm in farms:
                prod_types = farm_manager.get_production_types(farm[0])
                with st.expander(f"🏢 {farm[1]} - {farm[3]} ({len(prod_types)} أنواع)"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**النوع:** {farm[2]}")
                        st.write(f"**الموقع:** {farm[4]}")
                        st.write(f"**الهاتف:** {farm[5]}")
                    with col2:
                        st.write(f"**البريد:** {farm[6]}")
                        st.write(f"**المساحة:** {farm[8]} فدان")
                        st.write(f"**تاريخ التأسيس:** {farm[7]}")
                    with col3:
                        st.write(f"**الحالة:** {farm[11]}")
                        if farm[9] and farm[10]:
                            st.write(f"**الموقع الجغرافي:** {farm[9]}, {farm[10]}")
                    
                    if prod_types:
                        st.write("**أنواع الإنتاج:**")
                        for pt in prod_types:
                            st.caption(f"• {pt[2]} - {pt[3]} (منذ: {pt[4]})")
                    
                    col_actions1, col_actions2, col_actions3 = st.columns(3)
                    with col_actions1:
                        if st.button(f"📊 تقرير", key=f"report_{farm[0]}"):
                            report = farm_manager.generate_farm_report(farm[0])
                            st.code(report, language="txt")
                    with col_actions2:
                        if st.button(f"➕ نوع إنتاج", key=f"add_type_{farm[0]}"):
                            with st.popover("إضافة نوع إنتاج"):
                                prod_type = st.selectbox("نوع الإنتاج", 
                                    ["دواجن لاحم", "دواجن بياض", "أغنام", "ماعز", "أبقار حليب", "أبقار تسمين", "أسماك"])
                                sub_type = st.text_input("النوع الفرعي", "عام")
                                if st.button("إضافة"):
                                    farm_manager.add_production_type(farm[0], prod_type, sub_type)
                                    st.rerun()
                    with col_actions3:
                        if st.button(f"🗑️ حذف", key=f"delete_{farm[0]}"):
                            if st.checkbox("تأكيد الحذف", key=f"confirm_{farm[0]}"):
                                farm_manager.delete_farm(farm[0])
                                st.rerun()
        else:
            st.info("لا توجد مزارع مسجلة. قم بإضافة مزرعة جديدة.")
    
    # ===== التبويب 2: الدواجن اللاحم =====
    with farm_tabs[1]:
        st.markdown("#### 🐔 سجلات الدواجن اللاحم")
        
        farms = farm_manager.get_farms()
        if farms:
            farm_options = {f[1]: f[0] for f in farms if "دواجن" in f[2] or "مختلط" in f[2]}
            if farm_options:
                selected_farm = st.selectbox("اختر المزرعة:", list(farm_options.keys()), key="broiler_farm")
                farm_id = farm_options[selected_farm]
                
                summary = farm_manager.get_poultry_broiler_summary(farm_id)
                if summary:
                    cols = st.columns(4)
                    with cols[0]:
                        st.metric("📊 الدورات", summary['total_cycles'])
                    with cols[1]:
                        st.metric("🐔 الطيور الحالية", f"{summary['current_birds']:,}")
                    with cols[2]:
                        st.metric("⚖️ متوسط الوزن", f"{summary['avg_weight']:.2f} كجم")
                    with cols[3]:
                        st.metric("📈 معامل التحويل", f"{summary['avg_fcr']:.2f}")
                
                with st.expander("📝 إضافة سجل جديد", expanded=False):
                    with st.form("add_broiler_record"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            cycle_number = st.number_input("رقم الدورة", min_value=1, value=1)
                            breed = st.selectbox("السلالة", ["روس 308", "كوب 500", "محلية", "هجين", "أخرى"])
                            source = st.text_input("مصدر الطيور", placeholder="المفرخة أو المورد")
                            initial_birds = st.number_input("عدد الطيور في البداية", min_value=1, value=1000)
                        with col2:
                            current_birds = st.number_input("العدد الحالي", min_value=0, value=950)
                            daily_mortality = st.number_input("النفوق اليومي", min_value=0, value=5)
                            total_mortality = st.number_input("النفوق الكلي", min_value=0, value=50)
                            culled_birds = st.number_input("الطيور المستبعدة", min_value=0, value=0)
                        with col3:
                            avg_weight = st.number_input("متوسط الوزن (كجم)", min_value=0.0, value=1.5, step=0.1)
                            feed_consumption = st.number_input("استهلاك العلف (كجم)", min_value=0.0, value=100.0)
                            water_consumption = st.number_input("استهلاك الماء (لتر)", min_value=0.0, value=200.0)
                        
                        col4, col5 = st.columns(2)
                        with col4:
                            temperature = st.number_input("درجة الحرارة (مئوية)", min_value=0.0, value=25.0)
                            humidity = st.number_input("الرطوبة (%)", min_value=0.0, max_value=100.0, value=60.0)
                            vaccination = st.text_area("سجلات التطعيم", placeholder="التاريخ واللقاحات")
                        with col5:
                            medication = st.text_area("سجلات العلاج", placeholder="الأدوية المستخدمة")
                            lighting = st.text_area("جدول الإضاءة", placeholder="ساعات الإضاءة")
                            feeding = st.text_area("جدول التغذية", placeholder="مواعيد التغذية")
                        
                        notes = st.text_area("ملاحظات")
                        
                        submit_record = st.form_submit_button("💾 حفظ السجل")
                        if submit_record:
                            try:
                                data = {
                                    'farm_id': farm_id,
                                    'cycle_number': cycle_number,
                                    'breed': breed,
                                    'source': source,
                                    'initial_birds': initial_birds,
                                    'current_birds': current_birds,
                                    'daily_mortality': daily_mortality,
                                    'total_mortality': total_mortality,
                                    'culled_birds': culled_birds,
                                    'average_weight': avg_weight,
                                    'feed_consumption': feed_consumption,
                                    'water_consumption': water_consumption,
                                    'temperature': temperature,
                                    'humidity': humidity,
                                    'vaccination_records': vaccination,
                                    'medication_records': medication,
                                    'lighting_schedule': lighting,
                                    'feeding_schedule': feeding,
                                    'notes': notes
                                }
                                farm_manager.add_poultry_broiler_record(data)
                                st.success("✅ تم حفظ السجل بنجاح!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ حدث خطأ: {e}")
                
                records = farm_manager.get_poultry_broiler_records(farm_id)
                if records:
                    df_data = []
                    for r in records:
                        df_data.append({
                            'الدورة': r[2],
                            'السلالة': r[3],
                            'البداية': r[5],
                            'الحالي': r[6],
                            'الوزن': r[10],
                            'العلف': r[11],
                            'FCR': r[12],
                            'التاريخ': r[21][:10] if r[21] else ''
                        })
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True)
                    
                    if len(df) > 1:
                        fig = px.line(df, x='التاريخ', y='الوزن', title='تطور الوزن خلال الدورة')
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("لا توجد سجلات مسجلة.")
            else:
                st.warning("⚠️ لا توجد مزارع دواجن مسجلة.")
        else:
            st.warning("⚠️ لا توجد مزارع مسجلة.")
    
    # ===== التبويب 3: الدواجن البياض =====
    with farm_tabs[2]:
        st.markdown("#### 🥚 سجلات الدواجن البياض")
        
        farms = farm_manager.get_farms()
        if farms:
            farm_options = {f[1]: f[0] for f in farms if "دواجن" in f[2] or "مختلط" in f[2]}
            if farm_options:
                selected_farm = st.selectbox("اختر المزرعة:", list(farm_options.keys()), key="layer_farm")
                farm_id = farm_options[selected_farm]
                
                summary = farm_manager.get_poultry_layer_summary(farm_id)
                if summary:
                    cols = st.columns(4)
                    with cols[0]:
                        st.metric("📊 القطعان", summary['total_flocks'])
                    with cols[1]:
                        st.metric("🐔 الطيور الحالية", f"{summary['current_birds']:,}")
                    with cols[2]:
                        st.metric("🥚 البيض اليومي", f"{summary['avg_eggs_daily']:.0f}")
                    with cols[3]:
                        st.metric("⚖️ وزن البيضة", f"{summary['avg_egg_weight']:.1f} جم")
                
                with st.expander("📝 إضافة سجل جديد", expanded=False):
                    with st.form("add_layer_record"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            flock_id = st.text_input("رقم القطيع", "F001")
                            breed = st.selectbox("السلالة", ["لومان", "هاي لاين", "محلية", "أخرى"])
                            source = st.text_input("مصدر الطيور")
                            initial_birds = st.number_input("عدد الطيور في البداية", min_value=1, value=1000)
                        with col2:
                            current_birds = st.number_input("العدد الحالي", min_value=0, value=950)
                            daily_mortality = st.number_input("النفوق اليومي", min_value=0, value=2)
                            total_mortality = st.number_input("النفوق الكلي", min_value=0, value=50)
                            daily_eggs = st.number_input("الإنتاج اليومي (بيضة)", min_value=0, value=800)
                        with col3:
                            total_eggs = st.number_input("الإنتاج الكلي", min_value=0, value=24000)
                            egg_weight = st.number_input("متوسط وزن البيضة (جم)", min_value=0.0, value=60.0)
                            egg_color = st.selectbox("لون البيض", ["أبيض", "بني", "مختلط"])
                            egg_size = st.selectbox("حجم البيض", ["صغير", "متوسط", "كبير", "مختلط"])
                        
                        col4, col5 = st.columns(2)
                        with col4:
                            shell_quality = st.selectbox("جودة القشرة", ["جيدة", "متوسطة", "ضعيفة"])
                            feed_consumption = st.number_input("استهلاك العلف (كجم)", min_value=0.0, value=120.0)
                            water_consumption = st.number_input("استهلاك الماء (لتر)", min_value=0.0, value=250.0)
                        with col5:
                            temperature = st.number_input("درجة الحرارة (مئوية)", min_value=0.0, value=22.0)
                            humidity = st.number_input("الرطوبة (%)", min_value=0.0, max_value=100.0, value=60.0)
                            vaccination = st.text_area("سجلات التطعيم")
                            medication = st.text_area("سجلات العلاج")
                        
                        notes = st.text_area("ملاحظات")
                        
                        submit_record = st.form_submit_button("💾 حفظ السجل")
                        if submit_record:
                            try:
                                data = {
                                    'farm_id': farm_id,
                                    'flock_id': flock_id,
                                    'breed': breed,
                                    'source': source,
                                    'initial_birds': initial_birds,
                                    'current_birds': current_birds,
                                    'daily_mortality': daily_mortality,
                                    'total_mortality': total_mortality,
                                    'daily_eggs': daily_eggs,
                                    'total_eggs': total_eggs,
                                    'egg_weight': egg_weight,
                                    'egg_color': egg_color,
                                    'egg_size': egg_size,
                                    'shell_quality': shell_quality,
                                    'feed_consumption': feed_consumption,
                                    'water_consumption': water_consumption,
                                    'temperature': temperature,
                                    'humidity': humidity,
                                    'vaccination_records': vaccination,
                                    'medication_records': medication,
                                    'lighting_schedule': '',
                                    'notes': notes
                                }
                                farm_manager.add_poultry_layer_record(data)
                                st.success("✅ تم حفظ السجل بنجاح!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ حدث خطأ: {e}")
                
                records = farm_manager.get_poultry_layer_records(farm_id)
                if records:
                    df_data = []
                    for r in records:
                        df_data.append({
                            'القطيع': r[2],
                            'السلالة': r[3],
                            'البداية': r[5],
                            'الحالي': r[6],
                            'بيض يومي': r[9],
                            'وزن البيضة': r[11],
                            'التاريخ': r[21][:10] if r[21] else ''
                        })
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True)
                    
                    if len(df) > 1:
                        fig = px.line(df, x='التاريخ', y='بيض يومي', title='تطور إنتاج البيض')
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("لا توجد سجلات مسجلة.")
    
    # ===== التبويب 4: الأغنام والماعز =====
    with farm_tabs[3]:
        st.markdown("#### 🐑 سجلات الأغنام والماعز")
        
        farms = farm_manager.get_farms()
        if farms:
            farm_options = {f[1]: f[0] for f in farms if "أغنام" in f[2] or "ماعز" in f[2] or "مختلط" in f[2]}
            if farm_options:
                selected_farm = st.selectbox("اختر المزرعة:", list(farm_options.keys()), key="sheep_farm")
                farm_id = farm_options[selected_farm]
                
                with st.expander("📝 إضافة سجل جديد", expanded=False):
                    with st.form("add_sheep_record"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            flock_id = st.text_input("رقم القطيع", "S001")
                            animal_type = st.selectbox("نوع الحيوان", ["أغنام", "ماعز"])
                            breed = st.selectbox("السلالة", ["محلية", "محسنة", "هجين"])
                            source = st.text_input("مصدر الحيوانات")
                        with col2:
                            total_animals = st.number_input("العدد الكلي", min_value=1, value=100)
                            daily_mortality = st.number_input("النفوق اليومي", min_value=0, value=1)
                            total_mortality = st.number_input("النفوق الكلي", min_value=0, value=10)
                            avg_weight = st.number_input("متوسط الوزن (كجم)", min_value=0.0, value=35.0)
                        with col3:
                            feed_consumption = st.number_input("استهلاك العلف (كجم)", min_value=0.0, value=150.0)
                            water_consumption = st.number_input("استهلاك الماء (لتر)", min_value=0.0, value=200.0)
                            milk_production = st.number_input("إنتاج الحليب (لتر/يوم)", min_value=0.0, value=0.0)
                            wool_production = st.number_input("إنتاج الصوف (كجم)", min_value=0.0, value=0.0)
                        
                        col4, col5 = st.columns(2)
                        with col4:
                            wool_quality = st.selectbox("جودة الصوف", ["جيد", "متوسط", "ضعيف"])
                            lambing_rate = st.number_input("معدل الولادات (%)", min_value=0.0, max_value=200.0, value=100.0)
                        with col5:
                            vaccination = st.text_area("سجلات التطعيم")
                            medication = st.text_area("سجلات العلاج")
                        
                        notes = st.text_area("ملاحظات")
                        
                        submit_record = st.form_submit_button("💾 حفظ السجل")
                        if submit_record:
                            try:
                                data = {
                                    'farm_id': farm_id,
                                    'flock_id': flock_id,
                                    'animal_type': animal_type,
                                    'breed': breed,
                                    'source': source,
                                    'total_animals': total_animals,
                                    'daily_mortality': daily_mortality,
                                    'total_mortality': total_mortality,
                                    'average_weight': avg_weight,
                                    'feed_consumption': feed_consumption,
                                    'water_consumption': water_consumption,
                                    'milk_production': milk_production,
                                    'wool_production': wool_production,
                                    'wool_quality': wool_quality,
                                    'lambing_rate': lambing_rate,
                                    'vaccination_records': vaccination,
                                    'medication_records': medication,
                                    'notes': notes
                                }
                                farm_manager.add_sheep_goat_record(data)
                                st.success("✅ تم حفظ السجل بنجاح!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ حدث خطأ: {e}")
                
                records = farm_manager.get_sheep_goat_records(farm_id)
                if records:
                    df_data = []
                    for r in records:
                        df_data.append({
                            'القطيع': r[2],
                            'النوع': r[3],
                            'السلالة': r[4],
                            'العدد': r[6],
                            'الوزن': r[9],
                            'الحليب': r[11],
                            'التاريخ': r[17][:10] if r[17] else ''
                        })
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("لا توجد سجلات مسجلة.")
    
    # ===== التبويب 5: الأبقار =====
    with farm_tabs[4]:
        st.markdown("#### 🐄 سجلات الأبقار")
        
        farms = farm_manager.get_farms()
        if farms:
            farm_options = {f[1]: f[0] for f in farms if "أبقار" in f[2] or "مختلط" in f[2]}
            if farm_options:
                selected_farm = st.selectbox("اختر المزرعة:", list(farm_options.keys()), key="cattle_farm")
                farm_id = farm_options[selected_farm]
                
                with st.expander("📝 إضافة سجل جديد", expanded=False):
                    with st.form("add_cattle_record"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            herd_id = st.text_input("رقم القطيع", "C001")
                            breed = st.selectbox("السلالة", ["كنانة", "بطانة", "هولشتاين", "فريزيان", "محلية"])
                            source = st.text_input("مصدر الحيوانات")
                            total_animals = st.number_input("العدد الكلي", min_value=1, value=50)
                        with col2:
                            daily_mortality = st.number_input("النفوق اليومي", min_value=0, value=0)
                            total_mortality = st.number_input("النفوق الكلي", min_value=0, value=5)
                            avg_weight = st.number_input("متوسط الوزن (كجم)", min_value=0.0, value=450.0)
                            feed_consumption = st.number_input("استهلاك العلف (كجم)", min_value=0.0, value=500.0)
                        with col3:
                            water_consumption = st.number_input("استهلاك الماء (لتر)", min_value=0.0, value=800.0)
                            milk_production = st.number_input("إنتاج الحليب (لتر/يوم)", min_value=0.0, value=20.0)
                            fat_percentage = st.number_input("نسبة الدهن (%)", min_value=0.0, max_value=10.0, value=3.5)
                            protein_percentage = st.number_input("نسبة البروتين (%)", min_value=0.0, max_value=10.0, value=3.2)
                        
                        col4, col5 = st.columns(2)
                        with col4:
                            somatic_cell_count = st.number_input("عدد الخلايا الجسدية", min_value=0, value=200000)
                            calving_interval = st.number_input("فترة الولادة (أشهر)", min_value=0.0, value=12.0)
                        with col5:
                            vaccination = st.text_area("سجلات التطعيم")
                            medication = st.text_area("سجلات العلاج")
                        
                        notes = st.text_area("ملاحظات")
                        
                        submit_record = st.form_submit_button("💾 حفظ السجل")
                        if submit_record:
                            try:
                                data = {
                                    'farm_id': farm_id,
                                    'herd_id': herd_id,
                                    'breed': breed,
                                    'source': source,
                                    'total_animals': total_animals,
                                    'daily_mortality': daily_mortality,
                                    'total_mortality': total_mortality,
                                    'average_weight': avg_weight,
                                    'feed_consumption': feed_consumption,
                                    'water_consumption': water_consumption,
                                    'milk_production': milk_production,
                                    'fat_percentage': fat_percentage,
                                    'protein_percentage': protein_percentage,
                                    'somatic_cell_count': somatic_cell_count,
                                    'calving_interval': calving_interval,
                                    'vaccination_records': vaccination,
                                    'medication_records': medication,
                                    'notes': notes
                                }
                                farm_manager.add_cattle_record(data)
                                st.success("✅ تم حفظ السجل بنجاح!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ حدث خطأ: {e}")
                
                records = farm_manager.get_cattle_records(farm_id)
                if records:
                    df_data = []
                    for r in records:
                        df_data.append({
                            'القطيع': r[2],
                            'السلالة': r[3],
                            'العدد': r[5],
                            'الوزن': r[8],
                            'الحليب': r[10],
                            'الدهن': r[11],
                            'التاريخ': r[17][:10] if r[17] else ''
                        })
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("لا توجد سجلات مسجلة.")
    
    # ===== التبويب 6: الأسماك =====
    with farm_tabs[5]:
        st.markdown("#### 🐟 سجلات الأسماك")
        
        farms = farm_manager.get_farms()
        if farms:
            farm_options = {f[1]: f[0] for f in farms if "أسماك" in f[2] or "مختلط" in f[2]}
            if farm_options:
                selected_farm = st.selectbox("اختر المزرعة:", list(farm_options.keys()), key="fish_farm")
                farm_id = farm_options[selected_farm]
                
                with st.expander("📝 إضافة سجل جديد", expanded=False):
                    with st.form("add_fish_record"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            pond_id = st.text_input("رقم الحوض", "P001")
                            species = st.selectbox("النوع", ["البلطي", "البوري", "القرموط", "أخرى"])
                            initial_fish = st.number_input("عدد الأسماك في البداية", min_value=1, value=1000)
                        with col2:
                            current_fish = st.number_input("العدد الحالي", min_value=0, value=950)
                            daily_mortality = st.number_input("النفوق اليومي", min_value=0, value=5)
                            total_mortality = st.number_input("النفوق الكلي", min_value=0, value=50)
                        with col3:
                            avg_weight = st.number_input("متوسط الوزن (جم)", min_value=0.0, value=200.0)
                            feed_consumption = st.number_input("استهلاك العلف (كجم)", min_value=0.0, value=100.0)
                        
                        col4, col5 = st.columns(2)
                        with col4:
                            water_temperature = st.number_input("درجة حرارة الماء (مئوية)", min_value=0.0, value=25.0)
                            oxygen_level = st.number_input("مستوى الأكسجين (ملجم/لتر)", min_value=0.0, value=5.0)
                        with col5:
                            ph_level = st.number_input("مستوى الحموضة (pH)", min_value=0.0, max_value=14.0, value=7.0)
                            medication = st.text_area("سجلات العلاج")
                        
                        notes = st.text_area("ملاحظات")
                        
                        submit_record = st.form_submit_button("💾 حفظ السجل")
                        if submit_record:
                            try:
                                data = {
                                    'farm_id': farm_id,
                                    'pond_id': pond_id,
                                    'species': species,
                                    'initial_fish': initial_fish,
                                    'current_fish': current_fish,
                                    'daily_mortality': daily_mortality,
                                    'total_mortality': total_mortality,
                                    'average_weight': avg_weight,
                                    'feed_consumption': feed_consumption,
                                    'water_temperature': water_temperature,
                                    'oxygen_level': oxygen_level,
                                    'ph_level': ph_level,
                                    'vaccination_records': '',
                                    'medication_records': medication,
                                    'notes': notes
                                }
                                farm_manager.add_fish_record(data)
                                st.success("✅ تم حفظ السجل بنجاح!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ حدث خطأ: {e}")
                
                records = farm_manager.get_fish_records(farm_id)
                if records:
                    df_data = []
                    for r in records:
                        df_data.append({
                            'الحوض': r[2],
                            'النوع': r[3],
                            'البداية': r[4],
                            'الحالي': r[5],
                            'الوزن': r[8],
                            'درجة الحرارة': r[10],
                            'التاريخ': r[15][:10] if r[15] else ''
                        })
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("لا توجد سجلات مسجلة.")
    
    # ===== التبويب 7: الإحصائيات =====
    with farm_tabs[6]:
        st.markdown("#### 📊 الإحصائيات والتقارير")
        
        farms = farm_manager.get_farms()
        if farms:
            total_farms = len(farms)
            st.metric("إجمالي المزارع", total_farms)
            
            farm_types = {}
            for farm in farms:
                f_type = farm[2]
                farm_types[f_type] = farm_types.get(f_type, 0) + 1
            
            if farm_types:
                fig = px.pie(values=list(farm_types.values()), 
                           names=list(farm_types.keys()),
                           title="توزيع المزارع حسب النوع")
                st.plotly_chart(fig, use_container_width=True)
            
            total_broiler_birds = 0
            for farm in farms:
                if "دواجن" in farm[2] or "مختلط" in farm[2]:
                    records = farm_manager.get_poultry_broiler_records(farm[0])
                    for record in records:
                        total_broiler_birds += record[6]
            
            total_layer_birds = 0
            total_eggs_daily = 0
            for farm in farms:
                if "دواجن" in farm[2] or "مختلط" in farm[2]:
                    records = farm_manager.get_poultry_layer_records(farm[0])
                    for record in records:
                        total_layer_birds += record[6]
                        total_eggs_daily += record[9]
            
            total_sheep = 0
            total_milk = 0
            for farm in farms:
                if "أغنام" in farm[2] or "ماعز" in farm[2] or "مختلط" in farm[2]:
                    records = farm_manager.get_sheep_goat_records(farm[0])
                    for record in records:
                        total_sheep += record[6]
                        total_milk += record[11]
            
            total_cattle = 0
            total_cattle_milk = 0
            for farm in farms:
                if "أبقار" in farm[2] or "مختلط" in farm[2]:
                    records = farm_manager.get_cattle_records(farm[0])
                    for record in records:
                        total_cattle += record[5]
                        total_cattle_milk += record[10]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🐔 طيور لاحم", f"{total_broiler_birds:,}")
            with col2:
                st.metric("🥚 بيض يومي", f"{total_eggs_daily:,}")
            with col3:
                st.metric("🐑 أغنام/ماعز", f"{total_sheep:,}")
            with col4:
                st.metric("🐄 أبقار", f"{total_cattle:,}")
        else:
            st.info("لا توجد بيانات إحصائية.")
    
    # ===== التبويب 8: السجل اليومي =====
    with farm_tabs[7]:
        st.markdown("#### 📋 السجل اليومي للإنتاج")
        
        farms = farm_manager.get_farms()
        if farms:
            farm_options = {f[1]: f[0] for f in farms}
            selected_farm = st.selectbox("اختر المزرعة:", list(farm_options.keys()), key="daily_farm")
            farm_id = farm_options[selected_farm]
            
            with st.form("add_daily_record"):
                production_type = st.selectbox("نوع الإنتاج", 
                    ["دواجن لاحم", "دواجن بياض", "أغنام", "ماعز", "أبقار حليب", "أبقار تسمين", "أسماك"])
                col1, col2 = st.columns(2)
                with col1:
                    morning_obs = st.text_area("ملاحظات الصباح")
                    feed_amount = st.number_input("كمية العلف (كجم)", min_value=0.0, value=0.0)
                with col2:
                    evening_obs = st.text_area("ملاحظات المساء")
                    water_amount = st.number_input("كمية الماء (لتر)", min_value=0.0, value=0.0)
                health_status = st.selectbox("الحالة الصحية العامة", ["جيدة", "متوسطة", "ضعيفة", "تحت المراقبة"])
                special_notes = st.text_area("ملاحظات خاصة")
                
                submit_daily = st.form_submit_button("💾 حفظ السجل اليومي")
                if submit_daily:
                    try:
                        data = {
                            'farm_id': farm_id,
                            'production_type': production_type,
                            'morning_observations': morning_obs,
                            'evening_observations': evening_obs,
                            'feed_amount': feed_amount,
                            'water_amount': water_amount,
                            'health_status': health_status,
                            'special_notes': special_notes
                        }
                        farm_manager.add_daily_production(data)
                        st.success("✅ تم حفظ السجل اليومي بنجاح!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ حدث خطأ: {e}")
            
            records = farm_manager.get_daily_production(farm_id)
            if records:
                df_data = []
                for r in records:
                    df_data.append({
                        'التاريخ': r[3][:10] if r[3] else '',
                        'النوع': r[2],
                        'الحالة الصحية': r[7],
                        'العلف': r[5],
                        'الماء': r[6],
                        'ملاحظات الصباح': r[4][:50] if r[4] else '',
                        'ملاحظات المساء': r[4][:50] if r[4] else ''
                    })
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("لا توجد سجلات يومية.")

# ============================================================
# 13. إعدادات المنصة والواجهة
# ============================================================
st.set_page_config(
    page_title="منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# تهيئة حالة الجلسة
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
if "active_formula" not in st.session_state:
    st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0}
if "active_cp_tag" not in st.session_state:
    st.session_state["active_cp_tag"] = 12.0
if "active_se_tag" not in st.session_state:
    st.session_state["active_se_tag"] = 65.0
if "computed_ton_cost" not in st.session_state:
    st.session_state["computed_ton_cost"] = 280.0
if "broiler_farms" not in st.session_state:
    st.session_state["broiler_farms"] = {}
if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = "• [توجيه الاختصاصي م. عبد القادر إسماعيل تاور]: يرجى من جميع الزملاء إضافة تعليقاتهم هنا لتبادل الخبرات التركيبية."

# ============================================================
# 14. بوابة الدخول
# ============================================================
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300

if not st.session_state["approved"]:
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        if st.session_state["last_login_time"]:
            time_diff = (datetime.now() - st.session_state["last_login_time"]).seconds
            if time_diff < LOCKOUT_TIME:
                st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
                st.error(f"🔒 تم قفل النظام مؤقتاً. يرجى المحاولة بعد {LOCKOUT_TIME - time_diff} ثانية")
                st.markdown('</div>', unsafe_allow_html=True)
                st.stop()
            else:
                st.session_state["login_attempts"] = 0
    
    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#1a1a1a;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</p>", unsafe_allow_html=True)
    
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("https://tower-scientific-platform.streamlit.app")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        st.markdown(f'<div style="text-align:center; margin:20px 0;"><img src="data:image/png;base64,{qr_base64}" width="150"></div>', unsafe_allow_html=True)
    except:
        pass
    
    login_option = st.radio("طريقة الدخول:", ["كود الدخول السري", "اسم المستخدم وكلمة المرور"], horizontal=True)
    
    if login_option == "كود الدخول السري":
        CODES_DB = {
            "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
            "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
            "2026": {"role": "breeder", "name": "المربي", "level": 1}
        }
        input_code = st.text_input("🔑 أدخل كود الدخول الخاص بك:", type="password")
        col_login, col_reset = st.columns(2)
        with col_login:
            if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
                input_code_stripped = input_code.strip()
                if input_code_stripped in CODES_DB:
                    st.session_state["approved"] = True
                    st.session_state["user_role"] = CODES_DB[input_code_stripped]["role"]
                    st.session_state["login_welcome_shown"] = False
                    st.session_state["login_attempts"] = 0
                    st.session_state["last_login_time"] = datetime.now()
                    st.rerun()
                else:
                    st.session_state["login_attempts"] += 1
                    st.session_state["last_login_time"] = datetime.now()
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
            user, error = auth.authenticate(username, password)
            if user:
                st.session_state["approved"] = True
                st.session_state["user_role"] = user['role']
                st.session_state["login_welcome_shown"] = False
                st.session_state["login_attempts"] = 0
                st.session_state["last_login_time"] = datetime.now()
                st.session_state["user"] = user
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                st.session_state["last_login_time"] = datetime.now()
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ {error} متبقي {remaining} محاولات")
        
        st.caption("💡 المستخدم الافتراضي: admin / admin123")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# تشغيل الصوت الترحيبي
if st.session_state["approved"] and not st.session_state.get("audio_played", False):
    play_welcome_audio()
    st.session_state["audio_played"] = True

if not st.session_state["login_welcome_shown"]:
    role_messages = {
        "owner": "👋 مرحباً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور",
        "specialist": "🔬 أهلاً بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني.",
        "breeder": "🚜 أهلاً وسهلاً بإخواننا المربين، شركاء النجاح."
    }
    st.toast(role_messages.get(st.session_state["user_role"], "مرحباً"))
    st.session_state["login_welcome_shown"] = True

# ============================================================
# 15. CSS المحسّن
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
* { font-family: 'Cairo', sans-serif; }
.main-box {
    background-color: rgba(255, 255, 255, 0.98);
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18);
    margin-bottom: 50px;
    backdrop-filter: blur(5px);
}
.formula-item {
    background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(232,245,233,0.95) 100%);
    padding: 15px 20px;
    border-radius: 12px;
    margin-bottom: 10px;
    font-weight: bold;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    text-align: right;
}
.section-title {
    color: #1b5e20 !important;
    border-right: 6px solid #2e7d32;
    padding-right: 15px;
    text-align: right;
    font-size: 1.5rem;
    font-weight: bold;
    margin-top: 30px;
    margin-bottom: 20px;
    background: linear-gradient(to left, rgba(46,125,50,0.1), transparent);
    padding: 10px 15px;
    border-radius: 8px;
}
.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px;
    border-radius: 12px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 20px;
    direction: rtl;
    text-align: right;
}
.warning-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 15px;
    border-radius: 12px;
    border-right: 5px solid #f57c00;
    margin-bottom: 15px;
    direction: rtl;
    text-align: right;
}
.metric-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
    text-align: center;
    transition: transform 0.3s ease;
}
.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0px 8px 30px rgba(0,0,0,0.15);
}
.stButton > button {
    background: linear-gradient(135deg, #2e7d32, #1b5e20) !important;
    color: white !important;
    border: none !important;
    padding: 10px 20px !important;
    border-radius: 8px !important;
    font-weight: bold !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 15px rgba(46, 125, 50, 0.4) !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 16. الواجهة الرئيسية
# ============================================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logout, col_user_status = st.columns([0.7, 0.3])
with col_user_status:
    role_info = {
        "owner": "الاختصاصي م. عبد القادر إسماعيل تاور 👑",
        "specialist": "المختص والزملاء 👨‍🔬",
        "breeder": "المربي 🌾"
    }
    st.markdown(f"""
    <div style='text-align: left; font-size:0.9rem; color:#1a1a1a; background: linear-gradient(135deg, #f5f5f5, #e0e0e0); padding: 10px; border-radius: 10px;'>
        الحساب: <b>{role_info.get(st.session_state["user_role"], "مستخدم")}</b><br>
        <small>آخر دخول: {datetime.now().strftime('%Y-%m-%d %H:%M')}</small>
    </div>
    """, unsafe_allow_html=True)
    if st.button("تسجيل الخروج 🚪", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["inventory", "broiler_farms"]:
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

st.markdown("""
<h1 style='color: #1b5e20; text-align:right;'>🌾 منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</h1>
<h3 style='color: #c62828; text-align:right;'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>
<hr style='border-top: 3px solid #2e7d32;'>
""", unsafe_allow_html=True)

# ============================================================
# 17. التبويبات الرئيسية
# ============================================================
if st.session_state["user_role"] == "owner":
    tabs_titles = [
        "🔬 النمذجة والحسابات",
        "📊 بورصة الأسعار",
        "🏭 إدارة المستودعات",
        "🧾 الفواتير والمبيعات",
        "🖨️ مصمم الديباجة",
        "📈 التحليلات المتقدمة",
        "🐔 إدارة مزارع الدجاج",
        "🏢 إدارة المزارع",
        "💬 تعليقات المختصين",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية"
    ]
elif st.session_state["user_role"] == "specialist":
    tabs_titles = [
        "🔬 النمذجة والحسابات",
        "📊 بورصة الأسعار",
        "🏭 إدارة المستودعات",
        "🧾 الفواتير والمبيعات",
        "🖨️ مصمم الديباجة",
        "📈 التحليلات المتقدمة",
        "🏢 إدارة المزارع",
        "💬 تعليقات المختصين",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية"
    ]
else:
    tabs_titles = [
        "🔬 النمذجة والحسابات",
        "🏢 إدارة المزارع",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية"
    ]

tabs = st.tabs(tabs_titles)

# ============================================================
# 18. التبويب 1: النمذجة والحسابات العلفية
# ============================================================
with tabs[0]:
    guide_section("النمذجة والحسابات العلفية", 
        "في هذا التبويب يمكنك تركيب علفة مثالية بأقل تكلفة باستخدام البروتين المهضوم ومعادل النشاء. "
        "اختر الموقع الجغرافي، ثم القطاع الحيواني، وحدد المكونات، ثم اضغط على زر التشغيل.")
    
    st.markdown('<div class="section-title">🌍 أولاً: تحديد الموقع الجغرافي</div>', unsafe_allow_html=True)
    
    col_country, col_state, col_city = st.columns(3)
    with col_country:
        user_country = st.selectbox("اختر الدولة:", ["السودان", "LIBYA", "مصر", "باقي دول العالم"])
    
    EXCHANGE_RATES = {
        "السودان": {"rate": 600.0, "sym": "SDG", "name": "جنيه سوداني"},
        "LIBYA": {"rate": 4.80, "sym": "LYD", "name": "دينار ليبي"},
        "مصر": {"rate": 48.0, "sym": "EGP", "name": "جنيه مصري"},
        "باقي دول العالم": {"rate": 1.0, "sym": "USD", "name": "دولار أمريكي"}
    }
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD", "name": "دولار أمريكي"})
    local_rate = c_info["rate"]
    local_sym = c_info["sym"]
    
    chosen_state = "عام"
    with col_state:
        if user_country == "السودان":
            chosen_state = st.selectbox("الولاية:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال كردفان"])
        elif user_country == "LIBYA":
            chosen_state = st.selectbox("المنطقة:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
        else:
            chosen_state = st.selectbox("الإقليم:", ["المركز الرئيسي", "الأسواق المفتوحة"])
    
    with col_city:
        if user_country == "السودان":
            cities_map = {
                "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
                "ولاية الجزيرة": ["ود مدني", "الحصاحيصا"],
                "ولاية القضارف": ["القضارف", "الفاو"],
                "ولاية شمال كردفان": ["الأبيض", "بارا"]
            }
            user_city = st.selectbox("المدينة:", cities_map.get(chosen_state, ["عام"]))
        elif user_country == "LIBYA":
            cities_map = {
                "المنطقة الشرقية": ["طبرق", "بنغازي", "البيضاء"],
                "المنطقة الغربية": ["طرابلس", "مصراتة"],
                "المنطقة الجنوبية": ["سبها", "مرزق"]
            }
            user_city = st.selectbox("المدينة:", cities_map.get(chosen_state, ["عام"]))
        else:
            user_city = st.text_input("المدينة:", "طبرق")
    
    st.markdown('<div class="section-title">⚖️ ثانياً: اختيار القطاع الحيواني</div>', unsafe_allow_html=True)
    
    col_sector, col_breed, col_stage = st.columns(3)
    with col_sector:
        main_sector = st.selectbox("القطاع:", [
            "الأغنام", "الماعز", "الأبقار", "الخيول", "الدواجن اللاحمة", "الدواجن البياضة", "السمان", "الأسماك"
        ])
    
    if main_sector in ["الأغنام", "الماعز"]:
        with col_breed:
            breed = st.selectbox("السلالة:", ["محلية", "محسنة", "هجين"])
        with col_stage:
            stage = st.selectbox("المرحلة:", ["تسمين", "حليب/إدرار", "حمل/دفع غذائي", "صيانة"])
        default_dp = 12.0 if stage == "تسمين" else 12.8 if stage == "حليب/إدرار" else 10.5
        default_se = 64.0 if stage == "تسمين" else 66.0 if stage == "حليب/إدرار" else 60.0
    elif main_sector == "الأبقار":
        with col_breed:
            breed = st.selectbox("السلالة:", ["كنانة", "بطانة", "هولشتاين"])
        with col_stage:
            stage = st.selectbox("المرحلة:", ["حليب", "تسمين"])
        default_dp = 12.5 if stage == "حليب" else 10.0
        default_se = 68.0 if stage == "حليب" else 65.0
    elif main_sector == "الدواجن اللاحمة":
        with col_breed:
            breed = st.selectbox("السلالة:", ["روس 308", "كوب 500", "محلية"])
        with col_stage:
            stage = st.selectbox("المرحلة:", ["بادئ (1-10 يوم)", "نامي (11-24 يوم)", "ناهي (25-42 يوم)"])
        default_dp = 20.0 if "بادئ" in stage else 18.5 if "نامي" in stage else 16.5
        default_se = 76.0 if "بادئ" in stage else 74.0 if "نامي" in stage else 75.0
    else:
        with col_breed:
            breed = st.selectbox("النوع:", ["عام"])
        with col_stage:
            stage = st.selectbox("المرحلة:", ["نمو", "إنتاج"])
        default_dp = 15.0
        default_se = 65.0
    
    st.markdown('<div class="section-title">📋 ثالثاً: حدود الموازنة</div>', unsafe_allow_html=True)
    
    col_dp, col_se = st.columns(2)
    with col_dp:
        target_dp = st.slider("البروتين المهضوم المستهدف (DP %):", 5.0, 35.0, value=default_dp, step=0.5)
    with col_se:
        target_se = st.slider("معادل النشاء المستهدف (SE):", 20.0, 90.0, value=default_se, step=1.0)
    
    st.markdown('<div class="section-title">📦 رابعاً: اختيار المكونات</div>', unsafe_allow_html=True)
    
    selected_ingredients = []
    ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded="الحبوب" in cat_name or "البروتين" in cat_name):
            cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with cols[idx % 3]:
                    is_default = ing_name in ["ذرة صفراء", "سورجم (فتريتة)", "أمباز الفول السوداني (كسب)", 
                                              "كسب فول صويا 44%", "نخالة قمح (ردة)", "ملح الطعام", 
                                              "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)"]
                    checked = st.checkbox(ing_name, value=is_default, key=f"feed_{ing_name}")
                    
                    current_price = 250.0
                    if st.session_state["user_role"] == "owner":
                        price = st.number_input(f"${ing_name[:10]}", min_value=5.0, value=current_price, 
                                                key=f"price_{ing_name}", step=10.0)
                    else:
                        price = current_price
                        st.caption(f"السعر: ${price}/طن")
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price
    
    st.markdown("---")
    if st.button("🚀 تشغيل محرك الاستمثال الخطي", type="primary", use_container_width=True):
        if len(selected_ingredients) < 3:
            st.warning("⚠️ يرجى اختيار 3 مكونات على الأقل")
        else:
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
            b_eq.append(target_dp * 100.0)
            
            A_ub = []
            b_ub = []
            A_ub.append([-1.0 * x for x in se_row])
            b_ub.append(-1.0 * target_se * 100.0)
            
            res = linprog(c_vector, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
            
            if res.success:
                formula_results = {}
                computed_se = 0.0
                for idx, ing in enumerate(selected_ingredients):
                    if res.x[idx] > 0.0001:
                        formula_results[ing] = res.x[idx]
                        for cat in BIG_FEEDS_LIBRARY.values():
                            if ing in cat:
                                computed_se += (res.x[idx] / 100.0) * cat[ing].get("SE", 0.0)
                
                st.session_state["active_formula"] = formula_results
                st.session_state["active_cp_tag"] = target_dp
                st.session_state["active_se_tag"] = computed_se
                st.session_state["computed_ton_cost"] = res.fun / 100.0
                
                st.success("✅ تم تشغيل المحرك بنجاح!")
                
                col_res1, col_res2 = st.columns([0.6, 0.4])
                with col_res1:
                    st.write("#### 📝 المقادير المعتمدة (كجم/طن):")
                    for ing, pct in formula_results.items():
                        st.markdown(f'<div class="formula-item">▪️ {ing}: {pct:.2f}% ➡️ {pct*10:.1f} كجم</div>', unsafe_allow_html=True)
                    
                    cost = st.session_state["computed_ton_cost"]
                    st.metric(f"💰 التكلفة للطن في {user_city}:", f"${cost:.2f} ({cost*local_rate:,.1f} {local_sym})")
                    
                    try:
                        pdf_data = pdf_generator.generate_comprehensive_report(
                            formula_results, target_dp, f"{breed} - {stage}", 
                            cost, user_city, cost*local_rate, local_sym, computed_se
                        )
                        st.download_button("📥 تحميل التقرير PDF", pdf_data, 
                                          file_name=f"Tower_Feed_{datetime.now().strftime('%Y%m%d')}.pdf", 
                                          mime="application/pdf")
                    except Exception as e:
                        st.warning(f"⚠️ تعذر إنشاء PDF: {e}")
                
                with col_res2:
                    fig = px.pie(values=list(formula_results.values()), 
                                names=list(formula_results.keys()),
                                title="توزيع المكونات")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("❌ تعذر إيجاد حل رياضي. حاول إضافة مكونات أخرى أو تعديل الحدود.")

# ============================================================
# 19. التبويب 2: بورصة الأسعار (مختصر)
# ============================================================
with tabs[1]:
    guide_section("بورصة الأسعار", "هذا التبويب يعرض أسعار المواد الخام في الأسواق المحلية والعالمية مع توقعات الأسعار.")
    st.info("📊 يتم عرض أسعار المواد الخام حسب المدينة والدولة.")
    # تبسيط للعرض

# ============================================================
# 20. التبويب 3: إدارة المستودعات (مختصر)
# ============================================================
with tabs[2]:
    guide_section("إدارة المستودعات", "إدارة المخزون والمواد الخام مع تنبيهات نقص المخزون.")
    warnings = InventoryManager.check_stock_levels()
    if warnings:
        st.warning("⚠️ تنبيهات المخزون:")
        for item, status in warnings.items():
            st.write(f"- {item}: {status}")
    else:
        st.success("✅ جميع المواد متوفرة بكميات كافية.")

# ============================================================
# 21. التبويب 7 (الجديد): إدارة المزارع
# ============================================================
# نبحث عن مؤشر التبويب "🏢 إدارة المزارع"
farm_tab_index = tabs_titles.index("🏢 إدارة المزارع") if "🏢 إدارة المزارع" in tabs_titles else 7
with tabs[farm_tab_index]:
    render_farm_management()

# ============================================================
# 22. باقي التبويبات (مختصرة للعرض)
# ============================================================
for i in range(3, len(tabs)):
    if i != farm_tab_index and i < len(tabs):
        with tabs[i]:
            st.info(f"📌 هذا التبويب قيد التطوير. سيتم إضافة محتواه قريباً.")
            st.caption(f"تبويب: {tabs_titles[i]}")

# ============================================================
# 23. خاتمة التطبيق
# ============================================================
st.markdown("""
<div style='text-align:center; margin-top:50px; padding:20px; border-top:2px solid #e0e0e0;'>
    <small>© 2026 منصة تاور العلمية | الإصدار 4.5 | تحت إشراف الاختصاصي م. عبد القادر إسماعيل تاور</small>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
