# ============================================================================
# منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف
# الإصدار: 4.5 (مطور بالكامل - إضافة إدارة المزارع الشاملة)
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

# ============================================================
# 1. نظام الأمان المحسن (مع الحفاظ على البساطة)
# ============================================================
class EnhancedSecurityManager:
    """نظام أمان متطور مع توازن بين القوة والبساطة"""
    
    @staticmethod
    def generate_secure_token(length=32):
        """توليد رمز آمن"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_password(password, salt=None):
        """تشفير كلمة المرور باستخدام خوارزمية قوية"""
        if salt is None:
            salt = secrets.token_hex(16)
        iterations = 100000
        hash_value = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations
        ).hex()
        return f"{salt}${iterations}${hash_value}"
    
    @staticmethod
    def verify_password(password, stored_hash):
        """التحقق من كلمة المرور"""
        try:
            salt, iterations, hash_value = stored_hash.split('$')
            computed = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                int(iterations)
            ).hex()
            return computed == hash_value
        except:
            return False
    
    @staticmethod
    def generate_2fa_code():
        """توليد كود تحقق من خطوتين"""
        return str(secrets.randbelow(900000) + 100000)
    
    @staticmethod
    def encrypt_sensitive_data(data, key=None):
        """تشفير البيانات الحساسة (مبسط)"""
        if key is None:
            key = secrets.token_hex(16)
        # تشفير بسيط للعرض (يمكن استبدالها بـ AES للتطبيقات الحقيقية)
        return base64.b64encode(json.dumps(data).encode()).decode()

# ============================================================
# 2. نظام إدارة المزارع الشامل
# ============================================================
class FarmManagementSystem:
    """نظام متكامل لإدارة المزارع بأنواعها المختلفة"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self._init_farm_tables()
    
    def _init_farm_tables(self):
        """إنشاء جداول المزارع المتخصصة"""
        conn = sqlite3.connect(self.db.db_path)
        c = conn.cursor()
        
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
                     status TEXT,
                     notes TEXT,
                     FOREIGN KEY (farm_id) REFERENCES farms(farm_id))''')
        
        # جدول الدواجن (لاحم)
        c.execute('''CREATE TABLE IF NOT EXISTS poultry_broiler (
                     record_id TEXT PRIMARY KEY,
                     farm_id TEXT,
                     cycle_number INTEGER,
                     breed TEXT,
                     initial_birds INTEGER,
                     current_birds INTEGER,
                     daily_mortality INTEGER,
                     total_mortality INTEGER,
                     average_weight REAL,
                     feed_consumption REAL,
                     water_consumption REAL,
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
                     initial_birds INTEGER,
                     current_birds INTEGER,
                     daily_mortality INTEGER,
                     total_mortality INTEGER,
                     daily_eggs INTEGER,
                     total_eggs INTEGER,
                     egg_weight REAL,
                     egg_color TEXT,
                     feed_consumption REAL,
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
                     total_animals INTEGER,
                     daily_mortality INTEGER,
                     total_mortality INTEGER,
                     average_weight REAL,
                     feed_consumption REAL,
                     water_consumption REAL,
                     milk_production REAL,
                     wool_production REAL,
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
                     total_animals INTEGER,
                     daily_mortality INTEGER,
                     total_mortality INTEGER,
                     average_weight REAL,
                     feed_consumption REAL,
                     water_consumption REAL,
                     milk_production REAL,
                     fat_percentage REAL,
                     protein_percentage REAL,
                     vaccination_records TEXT,
                     medication_records TEXT,
                     record_date TEXT,
                     notes TEXT,
                     FOREIGN KEY (farm_id) REFERENCES farms(farm_id))''')
        
        conn.commit()
        conn.close()
    
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
            'email': farm_data['email'],
            'established_date': farm_data['established_date'],
            'total_area': farm_data['total_area'],
            'notes': farm_data.get('notes', ''),
            'created_by': st.session_state.get('user_id', 'system'),
            'created_date': datetime.now().isoformat()
        }
        self.db.insert_record('farms', data)
        return farm_id
    
    def add_production_type(self, farm_id, production_type, sub_type):
        """إضافة نوع إنتاج للمزرعة"""
        type_id = secrets.token_hex(16)
        data = {
            'type_id': type_id,
            'farm_id': farm_id,
            'production_type': production_type,
            'sub_type': sub_type,
            'start_date': datetime.now().isoformat(),
            'status': 'نشط',
            'notes': ''
        }
        self.db.insert_record('production_types', data)
        return type_id
    
    def add_poultry_broiler_record(self, data):
        """إضافة سجل دواجن لاحم"""
        record_id = secrets.token_hex(16)
        data['record_id'] = record_id
        data['record_date'] = datetime.now().isoformat()
        self.db.insert_record('poultry_broiler', data)
        return record_id
    
    def add_poultry_layer_record(self, data):
        """إضافة سجل دواجن بياض"""
        record_id = secrets.token_hex(16)
        data['record_id'] = record_id
        data['record_date'] = datetime.now().isoformat()
        self.db.insert_record('poultry_layer', data)
        return record_id
    
    def add_sheep_goat_record(self, data):
        """إضافة سجل أغنام وماعز"""
        record_id = secrets.token_hex(16)
        data['record_id'] = record_id
        data['record_date'] = datetime.now().isoformat()
        self.db.insert_record('sheep_goats', data)
        return record_id
    
    def add_cattle_record(self, data):
        """إضافة سجل أبقار"""
        record_id = secrets.token_hex(16)
        data['record_id'] = record_id
        data['record_date'] = datetime.now().isoformat()
        self.db.insert_record('cattle', data)
        return record_id
    
    def get_farms(self):
        """الحصول على قائمة المزارع"""
        return self.db.execute_query("SELECT * FROM farms ORDER BY created_date DESC")
    
    def get_farm_by_id(self, farm_id):
        """الحصول على مزرعة محددة"""
        result = self.db.execute_query("SELECT * FROM farms WHERE farm_id=?", (farm_id,))
        return result[0] if result else None
    
    def get_production_types(self, farm_id):
        """الحصول على أنواع الإنتاج لمزرعة"""
        return self.db.execute_query(
            "SELECT * FROM production_types WHERE farm_id=? ORDER BY start_date DESC",
            (farm_id,)
        )
    
    def get_poultry_broiler_records(self, farm_id, limit=30):
        """الحصول على سجلات الدواجن اللاحم"""
        return self.db.execute_query(
            "SELECT * FROM poultry_broiler WHERE farm_id=? ORDER BY record_date DESC LIMIT ?",
            (farm_id, limit)
        )
    
    def get_poultry_layer_records(self, farm_id, limit=30):
        """الحصول على سجلات الدواجن البياض"""
        return self.db.execute_query(
            "SELECT * FROM poultry_layer WHERE farm_id=? ORDER BY record_date DESC LIMIT ?",
            (farm_id, limit)
        )
    
    def get_sheep_goat_records(self, farm_id, limit=30):
        """الحصول على سجلات الأغنام والماعز"""
        return self.db.execute_query(
            "SELECT * FROM sheep_goats WHERE farm_id=? ORDER BY record_date DESC LIMIT ?",
            (farm_id, limit)
        )
    
    def get_cattle_records(self, farm_id, limit=30):
        """الحصول على سجلات الأبقار"""
        return self.db.execute_query(
            "SELECT * FROM cattle WHERE farm_id=? ORDER BY record_date DESC LIMIT ?",
            (farm_id, limit)
        )

# ============================================================
# 3. تحسين نظام قاعدة البيانات (إضافة الفهارس)
# ============================================================
class DatabaseManager:
    def __init__(self, db_path="tower_platform.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # جداول المستخدمين (محسنة)
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
        
        # جدول المزارع (مضاف)
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
                     status TEXT,
                     notes TEXT,
                     FOREIGN KEY (farm_id) REFERENCES farms(farm_id))''')
        
        # جدول الدواجن اللاحم
        c.execute('''CREATE TABLE IF NOT EXISTS poultry_broiler (
                     record_id TEXT PRIMARY KEY,
                     farm_id TEXT,
                     cycle_number INTEGER,
                     breed TEXT,
                     initial_birds INTEGER,
                     current_birds INTEGER,
                     daily_mortality INTEGER,
                     total_mortality INTEGER,
                     average_weight REAL,
                     feed_consumption REAL,
                     water_consumption REAL,
                     temperature REAL,
                     humidity REAL,
                     vaccination_records TEXT,
                     medication_records TEXT,
                     lighting_schedule TEXT,
                     feeding_schedule TEXT,
                     record_date TEXT,
                     notes TEXT,
                     FOREIGN KEY (farm_id) REFERENCES farms(farm_id))''')
        
        # جدول الدواجن البياض
        c.execute('''CREATE TABLE IF NOT EXISTS poultry_layer (
                     record_id TEXT PRIMARY KEY,
                     farm_id TEXT,
                     flock_id TEXT,
                     breed TEXT,
                     initial_birds INTEGER,
                     current_birds INTEGER,
                     daily_mortality INTEGER,
                     total_mortality INTEGER,
                     daily_eggs INTEGER,
                     total_eggs INTEGER,
                     egg_weight REAL,
                     egg_color TEXT,
                     feed_consumption REAL,
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
                     total_animals INTEGER,
                     daily_mortality INTEGER,
                     total_mortality INTEGER,
                     average_weight REAL,
                     feed_consumption REAL,
                     water_consumption REAL,
                     milk_production REAL,
                     wool_production REAL,
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
                     total_animals INTEGER,
                     daily_mortality INTEGER,
                     total_mortality INTEGER,
                     average_weight REAL,
                     feed_consumption REAL,
                     water_consumption REAL,
                     milk_production REAL,
                     fat_percentage REAL,
                     protein_percentage REAL,
                     vaccination_records TEXT,
                     medication_records TEXT,
                     record_date TEXT,
                     notes TEXT,
                     FOREIGN KEY (farm_id) REFERENCES farms(farm_id))''')
        
        # الفهارس المحسنة
        c.execute('CREATE INDEX IF NOT EXISTS idx_farms_name ON farms(farm_name)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_production_type ON production_types(production_type)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_broiler_date ON poultry_broiler(record_date)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_layer_date ON poultry_layer(record_date)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_sheep_date ON sheep_goats(record_date)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_cattle_date ON cattle(record_date)')
        
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

# ============================================================
# 4. نظام المصادقة المحسن
# ============================================================
class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.security = EnhancedSecurityManager()
        self._create_default_admin()
    
    def _create_default_admin(self):
        users = self.db.execute_query("SELECT * FROM users WHERE username='admin'")
        if not users:
            self.create_user('admin', 'admin123', 'owner', 'مدير النظام', 'admin@tower.com', '+249123456789')
    
    def create_user(self, username, password, role, full_name, email, phone):
        user_id = secrets.token_hex(16)
        # استخدام نظام التشفير المحسن
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
            # التحقق من القفل
            if user[11] == 1:  # is_locked
                return None, "الحساب مقفل. يرجى التواصل مع المسؤول."
            
            # التحقق من المحاولات
            if user[10] >= 5:  # login_attempts
                self.db.update_record('users', user[0], {'is_locked': 1})
                return None, "تم قفل الحساب لكثرة المحاولات الفاشلة."
            
            # التحقق من كلمة المرور باستخدام التشفير المحسن
            salt = user[3]
            iterations = user[4]
            hash_value = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                iterations
            ).hex()
            
            if hash_value == user[2]:
                # تحديث معلومات الدخول
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
                # زيادة عدد المحاولات
                new_attempts = user[10] + 1
                self.db.update_record('users', user[0], {'login_attempts': new_attempts})
                return None, f"كلمة مرور غير صحيحة. متبقي {5 - new_attempts} محاولات."
        
        return None, "اسم المستخدم غير موجود."

# ============================================================
# 5. تبويب إدارة المزارع (الواجهة الكاملة)
# ============================================================
def render_farm_management():
    """عرض واجهة إدارة المزارع المتكاملة"""
    
    st.markdown('<div class="section-title">🏢 إدارة المزارع - النظام المتكامل</div>', unsafe_allow_html=True)
    
    # تهيئة مدير المزارع
    farm_manager = FarmManagementSystem()
    
    # تبويبات إدارة المزارع
    farm_tabs = st.tabs([
        "🏢 المزارع", 
        "🐔 الدواجن اللاحم", 
        "🥚 الدواجن البياض",
        "🐑 الأغنام والماعز",
        "🐄 الأبقار",
        "📊 الإحصائيات"
    ])
    
    # ===== التبويب 1: المزارع =====
    with farm_tabs[0]:
        st.markdown("#### 📝 إضافة مزرعة جديدة")
        
        with st.form("add_farm_form"):
            col1, col2 = st.columns(2)
            with col1:
                farm_name = st.text_input("اسم المزرعة*", placeholder="مزرعة النجاح")
                farm_type = st.selectbox("نوع المزرعة*", ["دواجن", "أغنام وماعز", "أبقار", "مختلط"])
                owner_name = st.text_input("اسم المالك*", placeholder="فلان بن فلان")
                location = st.text_input("الموقع*", placeholder="الخرطوم - بحري")
                
            with col2:
                phone = st.text_input("رقم الهاتف*", placeholder="+249123456789")
                email = st.text_input("البريد الإلكتروني", placeholder="farm@example.com")
                established_date = st.date_input("تاريخ التأسيس", datetime.now())
                total_area = st.number_input("المساحة الكلية (فدان)", min_value=0.1, value=10.0, step=0.5)
            
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
                            'notes': notes
                        })
                        st.success(f"✅ تمت إضافة المزرعة '{farm_name}' بنجاح!")
                        
                        # إضافة نوع الإنتاج تلقائياً
                        if farm_type != "مختلط":
                            farm_manager.add_production_type(farm_id, farm_type, "عام")
                        
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ حدث خطأ: {e}")
                else:
                    st.error("⚠️ يرجى تعبئة الحقول المطلوبة (*)")
        
        # عرض المزارع الموجودة
        st.markdown("#### 📋 قائمة المزارع")
        farms = farm_manager.get_farms()
        if farms:
            for farm in farms:
                with st.expander(f"🏢 {farm[1]} - {farm[3]}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**النوع:** {farm[2]}")
                        st.write(f"**الموقع:** {farm[4]}")
                    with col2:
                        st.write(f"**الهاتف:** {farm[5]}")
                        st.write(f"**البريد:** {farm[6]}")
                    with col3:
                        st.write(f"**المساحة:** {farm[8]} فدان")
                        st.write(f"**تاريخ التأسيس:** {farm[7]}")
                    
                    # عرض أنواع الإنتاج
                    prod_types = farm_manager.get_production_types(farm[0])
                    if prod_types:
                        st.write("**أنواع الإنتاج:**")
                        for pt in prod_types:
                            st.caption(f"• {pt[2]} - {pt[3]} ({pt[4]})")
                    
                    # زر إضافة نوع إنتاج
                    if st.button(f"➕ إضافة نوع إنتاج", key=f"add_prod_{farm[0]}"):
                        with st.popover("إضافة نوع إنتاج"):
                            prod_type = st.selectbox("نوع الإنتاج", ["دواجن لاحم", "دواجن بياض", "أغنام", "ماعز", "أبقار حليب", "أبقار تسمين"])
                            sub_type = st.text_input("النوع الفرعي", "عام")
                            if st.button("إضافة"):
                                farm_manager.add_production_type(farm[0], prod_type, sub_type)
                                st.rerun()
        else:
            st.info("لا توجد مزارع مسجلة. قم بإضافة مزرعة جديدة.")
    
    # ===== التبويب 2: الدواجن اللاحم =====
    with farm_tabs[1]:
        st.markdown("#### 🐔 سجلات الدواجن اللاحم")
        
        # اختيار المزرعة
        farms = farm_manager.get_farms()
        if farms:
            farm_options = {f[1]: f[0] for f in farms if "دواجن" in f[2] or "مختلط" in f[2]}
            if farm_options:
                selected_farm = st.selectbox("اختر المزرعة:", list(farm_options.keys()))
                farm_id = farm_options[selected_farm]
                
                # نموذج إضافة سجل
                with st.expander("📝 إضافة سجل جديد"):
                    with st.form("add_broiler_record"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            cycle_number = st.number_input("رقم الدورة", min_value=1, value=1)
                            breed = st.selectbox("السلالة", ["روس 308", "كوب 500", "محلية", "أخرى"])
                            initial_birds = st.number_input("عدد الطيور في البداية", min_value=1, value=1000)
                        with col2:
                            current_birds = st.number_input("العدد الحالي", min_value=0, value=950)
                            daily_mortality = st.number_input("النفوق اليومي", min_value=0, value=5)
                            total_mortality = st.number_input("النفوق الكلي", min_value=0, value=50)
                        with col3:
                            avg_weight = st.number_input("متوسط الوزن (كجم)", min_value=0.0, value=1.5, step=0.1)
                            feed_consumption = st.number_input("استهلاك العلف (كجم)", min_value=0.0, value=100.0)
                            water_consumption = st.number_input("استهلاك الماء (لتر)", min_value=0.0, value=200.0)
                        
                        col4, col5 = st.columns(2)
                        with col4:
                            temperature = st.number_input("درجة الحرارة (مئوية)", min_value=0.0, value=25.0)
                            humidity = st.number_input("الرطوبة (%)", min_value=0.0, max_value=100.0, value=60.0)
                        with col5:
                            vaccination = st.text_area("سجلات التطعيم", placeholder="تاريخ ولقاحات")
                            medication = st.text_area("سجلات العلاج", placeholder="الأدوية المستخدمة")
                        
                        notes = st.text_area("ملاحظات")
                        
                        submit_record = st.form_submit_button("💾 حفظ السجل")
                        if submit_record:
                            try:
                                data = {
                                    'farm_id': farm_id,
                                    'cycle_number': cycle_number,
                                    'breed': breed,
                                    'initial_birds': initial_birds,
                                    'current_birds': current_birds,
                                    'daily_mortality': daily_mortality,
                                    'total_mortality': total_mortality,
                                    'average_weight': avg_weight,
                                    'feed_consumption': feed_consumption,
                                    'water_consumption': water_consumption,
                                    'temperature': temperature,
                                    'humidity': humidity,
                                    'vaccination_records': vaccination,
                                    'medication_records': medication,
                                    'lighting_schedule': '',
                                    'feeding_schedule': '',
                                    'notes': notes
                                }
                                farm_manager.add_poultry_broiler_record(data)
                                st.success("✅ تم حفظ السجل بنجاح!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ حدث خطأ: {e}")
                
                # عرض السجلات
                records = farm_manager.get_poultry_broiler_records(farm_id)
                if records:
                    df = pd.DataFrame(records, columns=[
                        'الرقم', 'المزرعة', 'الدورة', 'السلالة', 'البداية', 
                        'الحالي', 'نفوق يومي', 'نفوق كلي', 'متوسط الوزن',
                        'استهلاك العلف', 'استهلاك الماء', 'درجة الحرارة',
                        'الرطوبة', 'التطعيمات', 'العلاج', 'الإضاءة', 
                        'التغذية', 'التاريخ', 'ملاحظات'
                    ])
                    st.dataframe(df[['الدورة', 'السلالة', 'البداية', 'الحالي', 'متوسط الوزن', 'التاريخ']], 
                                use_container_width=True)
                else:
                    st.info("لا توجد سجلات مسجلة.")
            else:
                st.warning("⚠️ لا توجد مزارع دواجن مسجلة. قم بإضافة مزرعة أولاً.")
        else:
            st.warning("⚠️ لا توجد مزارع مسجلة. قم بإضافة مزرعة أولاً.")
    
    # ===== التبويب 3: الدواجن البياض =====
    with farm_tabs[2]:
        st.markdown("#### 🥚 سجلات الدواجن البياض")
        
        farms = farm_manager.get_farms()
        if farms:
            farm_options = {f[1]: f[0] for f in farms if "دواجن" in f[2] or "مختلط" in f[2]}
            if farm_options:
                selected_farm = st.selectbox("اختر المزرعة:", list(farm_options.keys()), key="layer_farm")
                farm_id = farm_options[selected_farm]
                
                with st.expander("📝 إضافة سجل جديد"):
                    with st.form("add_layer_record"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            flock_id = st.text_input("رقم القطيع", "F001")
                            breed = st.selectbox("السلالة", ["لومان", "هاي لاين", "محلية", "أخرى"])
                            initial_birds = st.number_input("عدد الطيور في البداية", min_value=1, value=1000)
                        with col2:
                            current_birds = st.number_input("العدد الحالي", min_value=0, value=950)
                            daily_mortality = st.number_input("النفوق اليومي", min_value=0, value=2)
                            total_mortality = st.number_input("النفوق الكلي", min_value=0, value=50)
                        with col3:
                            daily_eggs = st.number_input("الإنتاج اليومي (بيضة)", min_value=0, value=800)
                            total_eggs = st.number_input("الإنتاج الكلي", min_value=0, value=24000)
                            egg_weight = st.number_input("متوسط وزن البيضة (جم)", min_value=0.0, value=60.0)
                        
                        col4, col5 = st.columns(2)
                        with col4:
                            egg_color = st.selectbox("لون البيض", ["أبيض", "بني", "مختلط"])
                            feed_consumption = st.number_input("استهلاك العلف (كجم)", min_value=0.0, value=120.0)
                        with col5:
                            water_consumption = st.number_input("استهلاك الماء (لتر)", min_value=0.0, value=250.0)
                            temperature = st.number_input("درجة الحرارة (مئوية)", min_value=0.0, value=22.0)
                        
                        notes = st.text_area("ملاحظات")
                        
                        submit_record = st.form_submit_button("💾 حفظ السجل")
                        if submit_record:
                            try:
                                data = {
                                    'farm_id': farm_id,
                                    'flock_id': flock_id,
                                    'breed': breed,
                                    'initial_birds': initial_birds,
                                    'current_birds': current_birds,
                                    'daily_mortality': daily_mortality,
                                    'total_mortality': total_mortality,
                                    'daily_eggs': daily_eggs,
                                    'total_eggs': total_eggs,
                                    'egg_weight': egg_weight,
                                    'egg_color': egg_color,
                                    'feed_consumption': feed_consumption,
                                    'water_consumption': water_consumption,
                                    'temperature': temperature,
                                    'humidity': 60.0,
                                    'vaccination_records': '',
                                    'medication_records': '',
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
                    df = pd.DataFrame(records, columns=[
                        'الرقم', 'المزرعة', 'القطيع', 'السلالة', 'البداية',
                        'الحالي', 'نفوق يومي', 'نفوق كلي', 'بيض يومي',
                        'بيض كلي', 'وزن البيضة', 'لون البيض', 'استهلاك العلف',
                        'استهلاك الماء', 'الحرارة', 'الرطوبة', 'التطعيمات',
                        'العلاج', 'الإضاءة', 'التاريخ', 'ملاحظات'
                    ])
                    st.dataframe(df[['القطيع', 'السلالة', 'البداية', 'الحالي', 'بيض يومي', 'وزن البيضة', 'التاريخ']], 
                                use_container_width=True)
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
                
                with st.expander("📝 إضافة سجل جديد"):
                    with st.form("add_sheep_record"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            flock_id = st.text_input("رقم القطيع", "S001")
                            animal_type = st.selectbox("نوع الحيوان", ["أغنام", "ماعز"])
                            breed = st.selectbox("السلالة", ["محلية", "محسنة", "هجين"])
                        with col2:
                            total_animals = st.number_input("العدد الكلي", min_value=1, value=100)
                            daily_mortality = st.number_input("النفوق اليومي", min_value=0, value=1)
                            total_mortality = st.number_input("النفوق الكلي", min_value=0, value=10)
                        with col3:
                            avg_weight = st.number_input("متوسط الوزن (كجم)", min_value=0.0, value=35.0)
                            feed_consumption = st.number_input("استهلاك العلف (كجم)", min_value=0.0, value=150.0)
                            water_consumption = st.number_input("استهلاك الماء (لتر)", min_value=0.0, value=200.0)
                        
                        col4, col5 = st.columns(2)
                        with col4:
                            milk_production = st.number_input("إنتاج الحليب (لتر/يوم)", min_value=0.0, value=0.0)
                            wool_production = st.number_input("إنتاج الصوف (كجم)", min_value=0.0, value=0.0)
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
                                    'total_animals': total_animals,
                                    'daily_mortality': daily_mortality,
                                    'total_mortality': total_mortality,
                                    'average_weight': avg_weight,
                                    'feed_consumption': feed_consumption,
                                    'water_consumption': water_consumption,
                                    'milk_production': milk_production,
                                    'wool_production': wool_production,
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
                    df = pd.DataFrame(records, columns=[
                        'الرقم', 'المزرعة', 'القطيع', 'النوع', 'السلالة',
                        'العدد', 'نفوق يومي', 'نفوق كلي', 'متوسط الوزن',
                        'استهلاك العلف', 'استهلاك الماء', 'إنتاج الحليب',
                        'إنتاج الصوف', 'التطعيمات', 'العلاج', 'التاريخ', 'ملاحظات'
                    ])
                    st.dataframe(df[['القطيع', 'النوع', 'السلالة', 'العدد', 'متوسط الوزن', 'التاريخ']], 
                                use_container_width=True)
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
                
                with st.expander("📝 إضافة سجل جديد"):
                    with st.form("add_cattle_record"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            herd_id = st.text_input("رقم القطيع", "C001")
                            breed = st.selectbox("السلالة", ["كنانة", "بطانة", "هولشتاين", "فريزيان", "محلية"])
                            total_animals = st.number_input("العدد الكلي", min_value=1, value=50)
                        with col2:
                            daily_mortality = st.number_input("النفوق اليومي", min_value=0, value=0)
                            total_mortality = st.number_input("النفوق الكلي", min_value=0, value=5)
                            avg_weight = st.number_input("متوسط الوزن (كجم)", min_value=0.0, value=450.0)
                        with col3:
                            feed_consumption = st.number_input("استهلاك العلف (كجم)", min_value=0.0, value=500.0)
                            water_consumption = st.number_input("استهلاك الماء (لتر)", min_value=0.0, value=800.0)
                            milk_production = st.number_input("إنتاج الحليب (لتر/يوم)", min_value=0.0, value=20.0)
                        
                        col4, col5 = st.columns(2)
                        with col4:
                            fat_percentage = st.number_input("نسبة الدهن (%)", min_value=0.0, max_value=10.0, value=3.5)
                            protein_percentage = st.number_input("نسبة البروتين (%)", min_value=0.0, max_value=10.0, value=3.2)
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
                                    'total_animals': total_animals,
                                    'daily_mortality': daily_mortality,
                                    'total_mortality': total_mortality,
                                    'average_weight': avg_weight,
                                    'feed_consumption': feed_consumption,
                                    'water_consumption': water_consumption,
                                    'milk_production': milk_production,
                                    'fat_percentage': fat_percentage,
                                    'protein_percentage': protein_percentage,
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
                    df = pd.DataFrame(records, columns=[
                        'الرقم', 'المزرعة', 'القطيع', 'السلالة', 'العدد',
                        'نفوق يومي', 'نفوق كلي', 'متوسط الوزن', 'استهلاك العلف',
                        'استهلاك الماء', 'إنتاج الحليب', 'نسبة الدهن',
                        'نسبة البروتين', 'التطعيمات', 'العلاج', 'التاريخ', 'ملاحظات'
                    ])
                    st.dataframe(df[['القطيع', 'السلالة', 'العدد', 'متوسط الوزن', 'إنتاج الحليب', 'التاريخ']], 
                                use_container_width=True)
                else:
                    st.info("لا توجد سجلات مسجلة.")
    
    # ===== التبويب 6: الإحصائيات =====
    with farm_tabs[5]:
        st.markdown("#### 📊 الإحصائيات والتقارير")
        
        farms = farm_manager.get_farms()
        if farms:
            # إحصائيات عامة
            total_farms = len(farms)
            st.metric("إجمالي المزارع", total_farms)
            
            # توزيع المزارع حسب النوع
            farm_types = {}
            for farm in farms:
                f_type = farm[2]
                farm_types[f_type] = farm_types.get(f_type, 0) + 1
            
            if farm_types:
                fig = px.pie(values=list(farm_types.values()), 
                           names=list(farm_types.keys()),
                           title="توزيع المزارع حسب النوع")
                st.plotly_chart(fig, use_container_width=True)
            
            # إحصائيات الدواجن اللاحم
            total_broiler_birds = 0
            total_broiler_records = 0
            for farm in farms:
                if "دواجن" in farm[2] or "مختلط" in farm[2]:
                    records = farm_manager.get_poultry_broiler_records(farm[0])
                    total_broiler_records += len(records)
                    for record in records:
                        total_broiler_birds += record[5]  # current_birds
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("إجمالي سجلات الدواجن اللاحم", total_broiler_records)
            with col2:
                st.metric("إجمالي الطيور الحالية", f"{total_broiler_birds:,}")
            
            # إحصائيات الدواجن البياض
            total_layer_birds = 0
            total_eggs_daily = 0
            for farm in farms:
                if "دواجن" in farm[2] or "مختلط" in farm[2]:
                    records = farm_manager.get_poultry_layer_records(farm[0])
                    for record in records:
                        total_layer_birds += record[5]  # current_birds
                        total_eggs_daily += record[8]  # daily_eggs
            
            col3, col4 = st.columns(2)
            with col3:
                st.metric("إجمالي الطيور البياضة", f"{total_layer_birds:,}")
            with col4:
                st.metric("إنتاج البيض اليومي", f"{total_eggs_daily:,}")
            
            # إحصائيات الأغنام والماعز
            total_sheep = 0
            total_milk = 0
            for farm in farms:
                if "أغنام" in farm[2] or "ماعز" in farm[2] or "مختلط" in farm[2]:
                    records = farm_manager.get_sheep_goat_records(farm[0])
                    for record in records:
                        total_sheep += record[5]  # total_animals
                        total_milk += record[10]  # milk_production
            
            col5, col6 = st.columns(2)
            with col5:
                st.metric("إجمالي الأغنام والماعز", f"{total_sheep:,}")
            with col6:
                st.metric("إنتاج الحليب (لتر/يوم)", f"{total_milk:.1f}")
            
            # إحصائيات الأبقار
            total_cattle = 0
            total_cattle_milk = 0
            for farm in farms:
                if "أبقار" in farm[2] or "مختلط" in farm[2]:
                    records = farm_manager.get_cattle_records(farm[0])
                    for record in records:
                        total_cattle += record[4]  # total_animals
                        total_cattle_milk += record[9]  # milk_production
            
            col7, col8 = st.columns(2)
            with col7:
                st.metric("إجمالي الأبقار", f"{total_cattle:,}")
            with col8:
                st.metric("إنتاج الحليب (لتر/يوم)", f"{total_cattle_milk:.1f}")
        else:
            st.info("لا توجد بيانات إحصائية. قم بإضافة المزارع والسجلات.")

# ============================================================
# 6. تحديث التبويبات الرئيسية
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
        "🏢 إدارة المزارع",  # التبويب الجديد
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
        "🏢 إدارة المزارع",  # التبويب الجديد
        "💬 تعليقات المختصين",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية"
    ]
else:
    tabs_titles = [
        "🔬 النمذجة والحسابات",
        "🏢 إدارة المزارع",  # التبويب الجديد للمربين
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية"
    ]

tabs = st.tabs(tabs_titles)

# ============================================================
# 7. التبويب 1: النمذجة والحسابات (نفس الكود السابق)
# ============================================================
with tabs[0]:
    # ... (نفس الكود السابق للتبويب الأول) ...
    pass

# ============================================================
# 8. التبويب الجديد: إدارة المزارع
# ============================================================
with tabs[tabs_titles.index("🏢 إدارة المزارع")]:
    render_farm_management()

# ============================================================
# 9. باقي التبويبات (مختصرة)
# ============================================================
# ... (باقي التبويبات بنفس الكود السابق) ...

# ============================================================
# 10. خاتمة التطبيق
# ============================================================
st.markdown("""
<div style='text-align:center; margin-top:50px; padding:20px; border-top:2px solid #e0e0e0;'>
    <small>© 2026 منصة تاور العلمية | الإصدار 4.5 | تحت إشراف الاختصاصي م. عبد القادر إسماعيل تاور</small>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
