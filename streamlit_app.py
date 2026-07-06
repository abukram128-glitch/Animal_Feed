"""
منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف
النسخة المتكاملة الكاملة v3.0
تم التحديث بـ: الأمان المتقدم، استمرارية البيانات، المعادلات المتقدمة، سجل التدقيق
المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور
"""

# ==========================================
# 0. الاستيرادات الأساسية
# ==========================================
import streamlit as st
import numpy as np
import pandas as pd
import json
import os
import base64
import smtplib
import time
import urllib.parse
import sqlite3
import hashlib
import secrets
import bcrypt
from itsdangerous import URLSafeTimedSerializer
from functools import lru_cache
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
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
import warnings
import io
import qrcode
from PIL import Image as PILImage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.font_manager as fm
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
import arabic_reshaper
from bidi.algorithm import get_display
import random
import string
import csv
import pickle
import zipfile
from io import BytesIO
import tempfile
import shutil

# تجاهل التحذيرات
warnings.filterwarnings('ignore')

# ==========================================
# 1. إعدادات البيئة والثوابت
# ==========================================
# محاولة قراءة المتغيرات الحساسة من st.secrets
try:
    SENDER_EMAIL = st.secrets["email"]["sender"]
    SENDER_PASSWORD = st.secrets["email"]["password"]
    OWNER_EMAIL = st.secrets["email"]["owner"]
    WHATSAPP_NUMBER = st.secrets["whatsapp"]["number"]
except:
    # القيم الافتراضية للاختبار المحلي (يجب تغييرها في الإنتاج)
    SENDER_EMAIL = "abukram128@gmail.com"
    SENDER_PASSWORD = "oynz rdli tsdy ekdq"
    OWNER_EMAIL = "abukram128@gmail.com"
    WHATSAPP_NUMBER = "+249123533489"

# ثوابت النظام
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
GOOGLE_FORM_URL = "https://forms.google.com/YOUR_FORM_URL"
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300
CITY_PRICES_FILE = "city_prices.json"
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

# أكواد الدخول السريعة
CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

# أسعار الصرف
EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG", "currency_name": "جنيه سوداني"},
    "LIBYA": {"rate": 4.80, "sym": "LYD", "currency_name": "دينار ليبي"},
    "مصر": {"rate": 48.0, "sym": "EGP", "currency_name": "جنيه مصري"},
    "باقي دول العالم / البورصة المفتوحة": {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"}
}

# ==========================================
# 2. معالجة النصوص العربية
# ==========================================
class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=2000)
    def fix_arabic_text(text: str) -> str:
        try:
            reshaped = arabic_reshaper.reshape(str(text))
            bidi = get_display(reshaped)
            return bidi
        except:
            return str(text)

arabic_processor = ArabicTextProcessor()

# ==========================================
# 3. نظام إدارة قواعد البيانات المتكامل
# ==========================================
class DatabaseManager:
    """مدير قاعدة البيانات المتكامل مع جميع الجداول المطلوبة"""
    
    def __init__(self, db_path: str = "tower_platform_secure.db"):
        self.db_path = db_path
        self._init_database()
        self._initialize_default_data()
    
    def _init_database(self):
        """تهيئة جميع جداول قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 1. جدول المستخدمين
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            created_date TEXT,
            last_login TEXT,
            is_active INTEGER DEFAULT 1,
            reset_token TEXT,
            reset_token_expiry TEXT
        )''')
        
        # 2. جدول المخزون
        c.execute('''CREATE TABLE IF NOT EXISTS inventory_items (
            item_name TEXT PRIMARY KEY,
            quantity REAL NOT NULL DEFAULT 0,
            min_threshold REAL DEFAULT 5.0,
            unit TEXT DEFAULT 'طن',
            supplier TEXT DEFAULT 'غير محدد',
            purchase_price REAL DEFAULT 0.0,
            last_updated TEXT,
            expiry_date TEXT,
            batch_number TEXT
        )''')
        
        # 3. جدول سجل التدقيق
        c.execute('''CREATE TABLE IF NOT EXISTS audit_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            username TEXT,
            action TEXT,
            details TEXT,
            ip_address TEXT,
            timestamp TEXT
        )''')
        
        # 4. جدول دورات الإنتاج
        c.execute('''CREATE TABLE IF NOT EXISTS production_cycles (
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
            net_profit REAL,
            notes TEXT,
            created_by TEXT,
            created_date TEXT
        )''')
        
        # 5. جدول الأسعار التاريخية
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
        
        # 6. جدول الخلطات المحفوظة
        c.execute('''CREATE TABLE IF NOT EXISTS saved_formulas (
            formula_id TEXT PRIMARY KEY,
            formula_name TEXT,
            animal_type TEXT,
            target_dp REAL,
            target_se REAL,
            ingredients TEXT,
            total_cost REAL,
            created_by TEXT,
            created_date TEXT
        )''')
        
        # 7. جدول إعدادات النظام
        c.execute('''CREATE TABLE IF NOT EXISTS system_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT,
            description TEXT,
            updated_date TEXT
        )''')
        
        # 8. جدول المزارع
        c.execute('''CREATE TABLE IF NOT EXISTS farms (
            farm_id TEXT PRIMARY KEY,
            farm_name TEXT UNIQUE,
            owner_name TEXT,
            owner_phone TEXT,
            location TEXT,
            animal_type TEXT,
            capacity INTEGER,
            created_date TEXT,
            created_by TEXT
        )''')
        
        # 9. جدول السجلات اليومية للمزارع
        c.execute('''CREATE TABLE IF NOT EXISTS farm_daily_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            farm_id TEXT,
            date TEXT,
            age_days INTEGER,
            avg_weight_kg REAL,
            feed_consumed_kg REAL,
            dead_birds INTEGER,
            culled_birds INTEGER,
            temperature_c REAL,
            humidity_percent REAL,
            ventilation_status TEXT,
            litter_quality TEXT,
            notes TEXT,
            FOREIGN KEY (farm_id) REFERENCES farms(farm_id)
        )''')
        
        # 10. جدول السجل الصحي
        c.execute('''CREATE TABLE IF NOT EXISTS health_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            farm_id TEXT,
            date TEXT,
            age_days INTEGER,
            medication_given TEXT,
            standard_required TEXT,
            notes TEXT,
            FOREIGN KEY (farm_id) REFERENCES farms(farm_id)
        )''')
        
        # 11. جدول الفواتير
        c.execute('''CREATE TABLE IF NOT EXISTS invoices (
            invoice_id TEXT PRIMARY KEY,
            customer_name TEXT,
            formula_id TEXT,
            quantity_ton REAL,
            unit_price REAL,
            total_price REAL,
            status TEXT,
            created_by TEXT,
            created_date TEXT
        )''')
        
        # 12. جدول تنبيهات المخزون
        c.execute('''CREATE TABLE IF NOT EXISTS inventory_alerts (
            alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            alert_type TEXT,
            message TEXT,
            is_read INTEGER DEFAULT 0,
            created_date TEXT
        )''')
        
        conn.commit()
        conn.close()
    
    def _initialize_default_data(self):
        """تهيئة البيانات الافتراضية (المستخدمين، الإعدادات، المخزون)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # إعدادات النظام الافتراضية
        default_settings = [
            ('backup_interval_hours', '24', 'الفاصل الزمني للنسخ الاحتياطي بالساعات'),
            ('default_currency', 'USD', 'العملة الافتراضية'),
            ('default_profit_margin', '10', 'هامش الربح الافتراضي (%)'),
            ('alert_threshold', '5', 'حد التنبيه للمخزون (طن)')
        ]
        for key, value, desc in default_settings:
            c.execute('INSERT OR IGNORE INTO system_settings (setting_key, setting_value, description, updated_date) VALUES (?, ?, ?, ?)',
                      (key, value, desc, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    # ========== دوال قاعدة البيانات الأساسية ==========
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """تنفيذ استعلام مع حماية من SQL Injection"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        result = c.execute(query, params)
        conn.commit()
        data = result.fetchall()
        conn.close()
        return data
    
    def insert_record(self, table: str, data: dict) -> None:
        """إدراج سجل مع تنظيف أسماء الأعمدة"""
        columns = ', '.join([f'"{col}"' for col in data.keys()])
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(query, list(data.values()))
        conn.commit()
        conn.close()
    
    def update_record(self, table: str, data: dict, condition: str, condition_params: tuple) -> None:
        """تحديث سجل مع شرط"""
        set_clause = ', '.join([f'"{k}" = ?' for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(query, list(data.values()) + list(condition_params))
        conn.commit()
        conn.close()
    
    def delete_record(self, table: str, condition: str, params: tuple) -> None:
        """حذف سجل"""
        query = f"DELETE FROM {table} WHERE {condition}"
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(query, params)
        conn.commit()
        conn.close()
    
    def get_record(self, table: str, condition: str, params: tuple) -> Optional[tuple]:
        """استرجاع سجل واحد"""
        query = f"SELECT * FROM {table} WHERE {condition}"
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        result = c.execute(query, params).fetchone()
        conn.close()
        return result
    
    # ========== دوال المخزون ==========
    def get_inventory(self) -> dict:
        """استرجاع جميع عناصر المخزون"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT item_name, quantity, min_threshold, unit, supplier, purchase_price, expiry_date, batch_number FROM inventory_items")
        rows = c.fetchall()
        conn.close()
        return {
            row[0]: {
                "quantity": row[1],
                "min_threshold": row[2],
                "unit": row[3],
                "supplier": row[4],
                "purchase_price": row[5],
                "expiry_date": row[6],
                "batch_number": row[7]
            } for row in rows
        }
    
    def update_inventory(self, item_name: str, new_qty: float, user_id: str = "system", batch: str = None) -> bool:
        """تحديث كمية عنصر في المخزون"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("UPDATE inventory_items SET quantity = ?, last_updated = ?, batch_number = COALESCE(?, batch_number) WHERE item_name = ?",
                      (new_qty, datetime.now().isoformat(), batch, item_name))
            self.log_audit(user_id, "UPDATE_INVENTORY", f"'{item_name}' quantity set to {new_qty}")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"خطأ في تحديث المخزون: {e}")
            return False
    
    def deduct_inventory(self, item_name: str, amount: float, user_id: str = "system") -> bool:
        """خصم كمية من المخزون مع التحقق من الكفاية"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT quantity FROM inventory_items WHERE item_name = ?", (item_name,))
        row = c.fetchone()
        if not row or row[0] < amount:
            conn.close()
            return False
        new_qty = row[0] - amount
        c.execute("UPDATE inventory_items SET quantity = ?, last_updated = ? WHERE item_name = ?",
                  (new_qty, datetime.now().isoformat(), item_name))
        self.log_audit(user_id, "DEDUCT_INVENTORY", f"'{item_name}' deducted {amount}, remaining {new_qty}")
        conn.commit()
        conn.close()
        return True
    
    def add_inventory_item(self, item_name: str, quantity: float = 0.0, min_threshold: float = 5.0,
                           unit: str = "طن", supplier: str = "غير محدد", purchase_price: float = 0.0,
                           expiry_date: str = None, batch: str = None) -> None:
        """إضافة عنصر جديد إلى المخزون أو تحديثه"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO inventory_items 
                     (item_name, quantity, min_threshold, unit, supplier, purchase_price, expiry_date, batch_number, last_updated)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (item_name, quantity, min_threshold, unit, supplier, purchase_price, expiry_date, batch, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    # ========== دوال سجل التدقيق ==========
    def log_audit(self, user_id: str, action: str, details: str, ip: str = "0.0.0.0") -> None:
        """تسجيل إجراء في سجل التدقيق"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        username = st.session_state.get("user", {}).get("username", "unknown")
        c.execute("INSERT INTO audit_log (user_id, username, action, details, ip_address, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                  (user_id, username, action, details, ip, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_audit_log(self, limit: int = 100, user_id: str = None) -> List[tuple]:
        """استرجاع سجل التدقيق"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if user_id:
            c.execute("SELECT * FROM audit_log WHERE user_id = ? ORDER BY log_id DESC LIMIT ?", (user_id, limit))
        else:
            c.execute("SELECT * FROM audit_log ORDER BY log_id DESC LIMIT ?", (limit,))
        data = c.fetchall()
        conn.close()
        return data
    
    # ========== دوال النسخ الاحتياطي ==========
    def backup_database(self) -> bytes:
        """إنشاء نسخة احتياطية مضغوطة"""
        backup_buffer = BytesIO()
        with zipfile.ZipFile(backup_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(self.db_path, os.path.basename(self.db_path))
            # إضافة ملف JSON مع البيانات الوصفية
            meta = {
                "backup_date": datetime.now().isoformat(),
                "db_file": os.path.basename(self.db_path),
                "version": "3.0"
            }
            zipf.writestr("metadata.json", json.dumps(meta, ensure_ascii=False))
        backup_buffer.seek(0)
        return backup_buffer.getvalue()
    
    def restore_database(self, backup_data: bytes) -> bool:
        """استعادة النسخة الاحتياطية"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
                tmp.write(backup_data)
                tmp_path = tmp.name
            
            with zipfile.ZipFile(tmp_path, 'r') as zipf:
                zipf.extractall(tempfile.gettempdir())
                db_path = os.path.join(tempfile.gettempdir(), os.path.basename(self.db_path))
                if os.path.exists(db_path):
                    shutil.copy2(db_path, self.db_path)
                    os.unlink(db_path)
            os.unlink(tmp_path)
            return True
        except Exception as e:
            st.error(f"فشل الاستعادة: {e}")
            return False
    
    # ========== دوال دورات الإنتاج ==========
    def save_production_cycle(self, cycle_data: dict) -> str:
        """حفظ دورة إنتاج جديدة"""
        cycle_id = cycle_data.get('cycle_id', f"cycle_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        data = {
            'cycle_id': cycle_id,
            'farm_name': cycle_data.get('farm_name', ''),
            'animal_type': cycle_data.get('animal_type', ''),
            'breed': cycle_data.get('breed', ''),
            'start_date': cycle_data.get('start_date', datetime.now().isoformat()),
            'end_date': cycle_data.get('end_date', ''),
            'initial_birds': cycle_data.get('initial_birds', 0),
            'final_weight_kg': cycle_data.get('final_weight_kg', 0.0),
            'total_feed_kg': cycle_data.get('total_feed_kg', 0.0),
            'total_dead': cycle_data.get('total_dead', 0),
            'total_culled': cycle_data.get('total_culled', 0),
            'fcr': cycle_data.get('fcr', 0.0),
            'adg': cycle_data.get('adg', 0.0),
            'epef': cycle_data.get('epef', 0.0),
            'mortality_rate': cycle_data.get('mortality_rate', 0.0),
            'net_profit': cycle_data.get('net_profit', 0.0),
            'notes': cycle_data.get('notes', ''),
            'created_by': cycle_data.get('created_by', 'system'),
            'created_date': datetime.now().isoformat()
        }
        self.insert_record('production_cycles', data)
        return cycle_id
    
    def get_production_cycles(self, farm_name: str = None) -> List[dict]:
        """استرجاع دورات الإنتاج"""
        query = "SELECT * FROM production_cycles"
        params = ()
        if farm_name:
            query += " WHERE farm_name = ?"
            params = (farm_name,)
        rows = self.execute_query(query, params)
        return [
            {
                'cycle_id': r[0], 'farm_name': r[1], 'animal_type': r[2], 'breed': r[3],
                'start_date': r[4], 'end_date': r[5], 'initial_birds': r[6],
                'final_weight_kg': r[7], 'total_feed_kg': r[8], 'total_dead': r[9],
                'total_culled': r[10], 'fcr': r[11], 'adg': r[12], 'epef': r[13],
                'mortality_rate': r[14], 'net_profit': r[15], 'notes': r[16],
                'created_by': r[17], 'created_date': r[18]
            } for r in rows
        ]
    
    # ========== دوال الخلطات المحفوظة ==========
    def save_formula(self, formula_data: dict) -> str:
        """حفظ خلطة علفية"""
        formula_id = formula_data.get('formula_id', f"formula_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        data = {
            'formula_id': formula_id,
            'formula_name': formula_data.get('formula_name', 'خلطة جديدة'),
            'animal_type': formula_data.get('animal_type', 'عام'),
            'target_dp': formula_data.get('target_dp', 0.0),
            'target_se': formula_data.get('target_se', 0.0),
            'ingredients': json.dumps(formula_data.get('ingredients', {})),
            'total_cost': formula_data.get('total_cost', 0.0),
            'created_by': formula_data.get('created_by', 'system'),
            'created_date': datetime.now().isoformat()
        }
        self.insert_record('saved_formulas', data)
        return formula_id
    
    def get_saved_formulas(self) -> List[dict]:
        """استرجاع الخلطات المحفوظة"""
        rows = self.execute_query("SELECT * FROM saved_formulas ORDER BY created_date DESC")
        return [
            {
                'formula_id': r[0], 'formula_name': r[1], 'animal_type': r[2],
                'target_dp': r[3], 'target_se': r[4],
                'ingredients': json.loads(r[5]) if r[5] else {},
                'total_cost': r[6], 'created_by': r[7], 'created_date': r[8]
            } for r in rows
        ]
    
    # ========== دوال المزارع ==========
    def save_farm(self, farm_data: dict) -> str:
        """حفظ مزرعة جديدة"""
        farm_id = farm_data.get('farm_id', f"farm_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        data = {
            'farm_id': farm_id,
            'farm_name': farm_data.get('farm_name', ''),
            'owner_name': farm_data.get('owner_name', ''),
            'owner_phone': farm_data.get('owner_phone', ''),
            'location': farm_data.get('location', ''),
            'animal_type': farm_data.get('animal_type', ''),
            'capacity': farm_data.get('capacity', 0),
            'created_date': datetime.now().isoformat(),
            'created_by': farm_data.get('created_by', 'system')
        }
        self.insert_record('farms', data)
        return farm_id
    
    def get_farms(self) -> List[dict]:
        """استرجاع جميع المزارع"""
        rows = self.execute_query("SELECT * FROM farms ORDER BY created_date DESC")
        return [
            {
                'farm_id': r[0], 'farm_name': r[1], 'owner_name': r[2],
                'owner_phone': r[3], 'location': r[4], 'animal_type': r[5],
                'capacity': r[6], 'created_date': r[7], 'created_by': r[8]
            } for r in rows
        ]
    
    def save_daily_log(self, log_data: dict) -> int:
        """حفظ سجل يومي لمزرعة"""
        data = {
            'farm_id': log_data.get('farm_id', ''),
            'date': log_data.get('date', datetime.now().isoformat()),
            'age_days': log_data.get('age_days', 0),
            'avg_weight_kg': log_data.get('avg_weight_kg', 0.0),
            'feed_consumed_kg': log_data.get('feed_consumed_kg', 0.0),
            'dead_birds': log_data.get('dead_birds', 0),
            'culled_birds': log_data.get('culled_birds', 0),
            'temperature_c': log_data.get('temperature_c', 0.0),
            'humidity_percent': log_data.get('humidity_percent', 0.0),
            'ventilation_status': log_data.get('ventilation_status', ''),
            'litter_quality': log_data.get('litter_quality', ''),
            'notes': log_data.get('notes', '')
        }
        self.insert_record('farm_daily_logs', data)
        return len(self.execute_query("SELECT last_insert_rowid()"))  # يعيد آخر ID
    
    def get_daily_logs(self, farm_id: str) -> List[dict]:
        """استرجاع السجلات اليومية لمزرعة"""
        rows = self.execute_query("SELECT * FROM farm_daily_logs WHERE farm_id = ? ORDER BY date DESC", (farm_id,))
        return [
            {
                'log_id': r[0], 'farm_id': r[1], 'date': r[2], 'age_days': r[3],
                'avg_weight_kg': r[4], 'feed_consumed_kg': r[5], 'dead_birds': r[6],
                'culled_birds': r[7], 'temperature_c': r[8], 'humidity_percent': r[9],
                'ventilation_status': r[10], 'litter_quality': r[11], 'notes': r[12]
            } for r in rows
        ]

# ==========================================
# 4. نظام المصادقة المتقدم
# ==========================================
class AuthManager:
    """نظام إدارة المصادقة باستخدام bcrypt و JWT-like tokens"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.serializer = URLSafeTimedSerializer(secrets.token_urlsafe(32))
        self._create_default_admin()
    
    def _hash_password(self, password: str) -> str:
        """تشفير كلمة المرور باستخدام bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """التحقق من كلمة المرور مع bcrypt"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _create_default_admin(self):
        """إنشاء مستخدم admin افتراضي إذا لم يكن موجوداً"""
        users = self.db.execute_query("SELECT * FROM users WHERE username='admin'")
        if not users:
            self.create_user('admin', 'admin123', 'owner', 'مدير النظام', 'admin@tower.com', '+249123456789')
    
    def create_user(self, username: str, password: str, role: str, full_name: str, email: str, phone: str) -> str:
        """إنشاء مستخدم جديد"""
        user_id = secrets.token_hex(16)
        password_hash = self._hash_password(password)
        data = {
            'user_id': user_id,
            'username': username,
            'password_hash': password_hash,
            'role': role,
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'created_date': datetime.now().isoformat(),
            'last_login': '',
            'is_active': 1,
            'reset_token': '',
            'reset_token_expiry': ''
        }
        self.db.insert_record('users', data)
        self.db.log_audit(user_id, "USER_CREATED", f"New user {username} with role {role}")
        return user_id
    
    def authenticate(self, username: str, password: str, ip: str = "0.0.0.0") -> Optional[dict]:
        """مصادقة المستخدم"""
        users = self.db.execute_query("SELECT * FROM users WHERE username=? AND is_active=1", (username,))
        if users:
            user = users[0]
            if self._verify_password(password, user[2]):
                # تحديث آخر تسجيل دخول
                self.db.update_record('users', {'last_login': datetime.now().isoformat()}, 'user_id = ?', (user[0],))
                self.db.log_audit(user[0], "LOGIN_SUCCESS", f"User {username} logged in", ip)
                return {
                    'user_id': user[0],
                    'username': user[1],
                    'role': user[3],
                    'full_name': user[4],
                    'email': user[5],
                    'phone': user[6]
                }
        self.db.log_audit("system", "LOGIN_FAILED", f"Failed login attempt for {username}", ip)
        return None
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """تغيير كلمة المرور"""
        users = self.db.execute_query("SELECT password_hash FROM users WHERE user_id=?", (user_id,))
        if not users:
            return False
        if not self._verify_password(old_password, users[0][0]):
            return False
        new_hash = self._hash_password(new_password)
        self.db.update_record('users', {'password_hash': new_hash}, 'user_id = ?', (user_id,))
        self.db.log_audit(user_id, "PASSWORD_CHANGED", "User changed password")
        return True
    
    def reset_password_request(self, email: str) -> str:
        """إنشاء طلب إعادة تعيين كلمة المرور"""
        token = self.serializer.dumps(email, salt='password-reset')
        # حفظ الرمز في قاعدة البيانات مع صلاحية ساعة واحدة
        expiry = (datetime.now() + timedelta(hours=1)).isoformat()
        self.db.update_record('users', {'reset_token': token, 'reset_token_expiry': expiry}, 'email = ?', (email,))
        return token
    
    def reset_password_confirm(self, token: str, new_password: str) -> bool:
        """تأكيد إعادة تعيين كلمة المرور"""
        try:
            email = self.serializer.loads(token, salt='password-reset', max_age=3600)
            users = self.db.execute_query("SELECT user_id, reset_token, reset_token_expiry FROM users WHERE email=? AND reset_token=?", (email, token))
            if not users:
                return False
            user_id = users[0][0]
            expiry = users[0][2]
            if expiry and datetime.fromisoformat(expiry) < datetime.now():
                return False
            new_hash = self._hash_password(new_password)
            self.db.update_record('users', {'password_hash': new_hash, 'reset_token': '', 'reset_token_expiry': ''}, 'user_id = ?', (user_id,))
            self.db.log_audit(user_id, "PASSWORD_RESET", "Password reset via email link")
            return True
        except Exception as e:
            st.error(f"خطأ في إعادة تعيين كلمة المرور: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[dict]:
        """استرجاع معلومات المستخدم"""
        user = self.db.get_record('users', 'user_id = ?', (user_id,))
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'role': user[3],
                'full_name': user[4],
                'email': user[5],
                'phone': user[6]
            }
        return None

# ==========================================
# 5. مكتبة الأعلاف الكاملة (مع قيم الأحماض الأمينية)
# ==========================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة الكبرى": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3,
                      "Lys": 0.25, "Met": 0.18, "Thr": 0.30},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4,
                      "Lys": 0.26, "Met": 0.17, "Thr": 0.31},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5,
                       "Lys": 0.40, "Met": 0.20, "Thr": 0.35},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8,
                           "Lys": 0.22, "Met": 0.16, "Thr": 0.28},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6,
                           "Lys": 0.35, "Met": 0.20, "Thr": 0.33},
        "جريش أرز رزاز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2,
                          "Lys": 0.20, "Met": 0.15, "Thr": 0.25},
        "دخن محلي غزير": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2,
                          "Lys": 0.30, "Met": 0.18, "Thr": 0.29},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0,
                       "Lys": 0.42, "Met": 0.21, "Thr": 0.36}
    },
    "🌱 الأكساب وأمبازات مصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5,
                                       "Lys": 1.6, "Met": 0.5, "Thr": 1.2},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0,
                             "Lys": 2.8, "Met": 0.7, "Thr": 1.8},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2,
                             "Lys": 3.0, "Met": 0.75, "Thr": 1.9},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5,
                               "Lys": 1.4, "Met": 0.6, "Thr": 1.1},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5,
                                   "Lys": 1.5, "Met": 0.5, "Thr": 1.2},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 9.5, "EE": 2.8, "ASH": 5.8,
                            "Lys": 1.2, "Met": 0.6, "Thr": 1.0},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5,
                              "Lys": 1.3, "Met": 0.6, "Thr": 1.1},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5,
                                 "Lys": 1.2, "Met": 2.0, "Thr": 1.8},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5,
                            "Lys": 0.6, "Met": 0.3, "Thr": 0.5}
    },
    "🚜 المخلفات الزراعية والصناعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5,
                            "Lys": 0.6, "Met": 0.2, "Thr": 0.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5,
                                    "Lys": 0.8, "Met": 0.3, "Thr": 0.7},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5,
                            "Lys": 0.1, "Met": 0.05, "Thr": 0.1},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5,
                         "Lys": 0.1, "Met": 0.05, "Thr": 0.1},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5,
                                  "Lys": 0.2, "Met": 0.1, "Thr": 0.2},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5,
                                 "Lys": 0.1, "Met": 0.05, "Thr": 0.1}
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5,
                                        "Lys": 4.5, "Met": 1.8, "Thr": 2.6},
        "مسحوق أسماك فاخر (72%)": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5,
                                    "Lys": 5.2, "Met": 2.2, "Thr": 3.0},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5,
                                "Lys": 3.5, "Met": 1.0, "Thr": 2.0},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5,
                                "Lys": 2.8, "Met": 1.2, "Thr": 1.8},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5,
                                 "Lys": 2.2, "Met": 0.9, "Thr": 1.5}
    },
    "🧪 الأحماض الأمينية البلورية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5,
                                  "Lys": 94.0, "Met": 0.0, "Thr": 0.0},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3,
                                         "Lys": 0.0, "Met": 58.0, "Thr": 0.0},
        "ثريونين نقي (L-Threonine)": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2,
                                       "Lys": 0.0, "Met": 0.0, "Thr": 72.0},
        "تريبتوفان نقي (L-Tryptophan)": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1,
                                         "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "فالين نقي (L-Valine)": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1,
                                 "Lys": 0.0, "Met": 0.0, "Thr": 0.0}
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0,
                                        "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "بريمكس بياض وبشاير": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0,
                               "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0,
                                       "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0,
                                                    "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0,
                                                    "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "كبريتات الحديدوز (معادل الجوسيبول)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0,
                                               "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "مستخلص الخمائر والجدر الخلوية (MOS)": {"CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5, "EE": 1.5, "ASH": 8.5,
                                                "Lys": 0.5, "Met": 0.2, "Thr": 0.4}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5,
                                      "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5,
                                         "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9,
                       "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0,
                            "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0,
                                        "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "أكسيد المغنيسيوم العلفي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5,
                                    "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "يوريا علفية محصنة (المجترات فقط)": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0,
                                             "Lys": 0.0, "Met": 0.0, "Thr": 0.0}
    }
}

# ==========================================
# 6. دوال الطاقة المتقدمة والأحماض الأمينية
# ==========================================
def calculate_me(cp: float, ee: float, nfe: float) -> float:
    """حساب الطاقة الأيضية (ME) للدواجن بالكيلو كالوري/كجم"""
    return (cp * 0.155) + (ee * 0.355) + (nfe * 0.155)

def calculate_ne_milk(cp: float, ee: float, ndf: float, se: float) -> float:
    """حساب صافي الطاقة للحليب (NEl) للمجترات"""
    return 0.6 * se - 0.2 * ndf + 0.1 * cp

def calculate_ne_gain(cp: float, ee: float, ndf: float, se: float) -> float:
    """حساب صافي الطاقة للتسمين (NEg) للمجترات"""
    return 0.5 * se - 0.3 * ndf + 0.05 * cp

def get_amino_acid_value(ingredient: str, aa_type: str) -> float:
    """استرجاع نسبة حمض أميني معين من المكتبة"""
    for cat in BIG_FEEDS_LIBRARY.values():
        if ingredient in cat:
            return cat[ingredient].get(aa_type, 0.0)
    return 0.0

def add_amino_acid_constraints(A_ub: list, b_ub: list, selected_ingredients: list, 
                               target_aa: str, min_requirement: float) -> tuple:
    """إضافة قيود الأحماض الأمينية إلى مصفوفة الاستمثال"""
    aa_row = []
    for ing in selected_ingredients:
        aa_row.append(get_amino_acid_value(ing, target_aa))
    # قيد: sum(ai * xi) >= min_requirement * 100
    A_ub.append([-1.0 * x for x in aa_row])
    b_ub.append(-1.0 * min_requirement * 100.0)
    return A_ub, b_ub

# ==========================================
# 7. نظام إدارة المخزون
# ==========================================
class InventoryManager:
    """مدير المخزون المتكامل مع قاعدة البيانات"""
    
    db = DatabaseManager()
    
    @classmethod
    def get_inventory(cls) -> dict:
        """استرجاع المخزون من قاعدة البيانات"""
        return cls.db.get_inventory()
    
    @classmethod
    def check_stock_levels(cls) -> Dict[str, str]:
        """التحقق من مستويات المخزون وإرجاع التحذيرات"""
        inventory = cls.get_inventory()
        warnings = {}
        for item, data in inventory.items():
            qty = data["quantity"]
            threshold = data["min_threshold"]
            if qty <= 0:
                warnings[item] = "نفذ المخزون"
            elif qty < threshold:
                warnings[item] = "منخفض"
        return warnings
    
    @classmethod
    def update_stock(cls, item: str, qty: float, user_id: str = "system") -> bool:
        """تحديث كمية صنف معين"""
        result = cls.db.update_inventory(item, qty, user_id)
        if result and "inventory_cache" in st.session_state:
            if item in st.session_state["inventory_cache"]:
                st.session_state["inventory_cache"][item]["quantity"] = qty
        return result
    
    @classmethod
    def deduct_stock(cls, item: str, amount: float, user_id: str = "system") -> bool:
        """خصم كمية من المخزون"""
        result = cls.db.deduct_inventory(item, amount, user_id)
        if result and "inventory_cache" in st.session_state:
            if item in st.session_state["inventory_cache"]:
                st.session_state["inventory_cache"][item]["quantity"] -= amount
        return result
    
    @classmethod
    def add_item(cls, item_name: str, quantity: float = 0.0, min_threshold: float = 5.0,
                 unit: str = "طن", supplier: str = "غير محدد", purchase_price: float = 0.0,
                 expiry_date: str = None, batch: str = None) -> None:
        """إضافة صنف جديد إلى المخزون"""
        cls.db.add_inventory_item(item_name, quantity, min_threshold, unit, supplier, 
                                  purchase_price, expiry_date, batch)
        # تحديث الكاش
        if "inventory_cache" in st.session_state:
            st.session_state["inventory_cache"][item_name] = {
                "quantity": quantity,
                "min_threshold": min_threshold,
                "unit": unit,
                "supplier": supplier,
                "purchase_price": purchase_price,
                "expiry_date": expiry_date,
                "batch_number": batch
            }

# ==========================================
# 8. نظام التنبؤ بالأسعار
# ==========================================
class PricePredictor:
    """نظام التنبؤ بأسعار المواد الخام"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_ingredient_prices(self, ingredient_name: str, days: int = 30) -> List[dict]:
        """استرجاع الأسعار التاريخية لمادة معينة"""
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
    
    def record_price(self, ingredient_name: str, price: float, currency: str = "USD",
                     country: str = "", city: str = "", user_id: str = "system") -> None:
        """تسجيل سعر جديد لمادة علفية"""
        record_id = f"price_{datetime.now().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"
        data = {
            'record_id': record_id,
            'ingredient_name': ingredient_name,
            'price': price,
            'currency': currency,
            'country': country,
            'city': city,
            'record_date': datetime.now().isoformat(),
            'recorded_by': user_id
        }
        self.db.insert_record('price_history', data)
    
    def predict_price(self, ingredient_name: str, days_ahead: int = 7) -> dict:
        """التنبؤ بالسعر المستقبلي باستخدام المتوسط المرجح والاتجاه"""
        prices = self.get_ingredient_prices(ingredient_name, 30)
        if len(prices) < 5:
            return {'prediction': None, 'confidence': 0}
        
        price_list = [p['price'] for p in prices]
        # المتوسط المرجح (الأحدث وزن أكبر)
        weights = np.array(range(1, len(price_list) + 1))
        weighted_avg = np.average(price_list, weights=weights)
        # حساب الاتجاه البسيط
        trend = (price_list[0] - price_list[-1]) / len(price_list) if len(price_list) > 1 else 0
        prediction = weighted_avg + (trend * days_ahead)
        
        return {
            'prediction': max(0, prediction),
            'confidence': min(1, len(price_list) / 30),
            'current_price': price_list[0] if price_list else None,
            'trend': 'up' if trend > 0 else 'down' if trend < 0 else 'stable',
            'historical_data': price_list[:10]  # آخر 10 قيم للرسم
        }

# ==========================================
# 9. نظام إدارة مزارع الدجاج
# ==========================================
class BroilerFarmManager:
    """مدير مزارع الدجاج اللاحم"""
    
    db = DatabaseManager()
    
    @staticmethod
    def calculate_adg(current_weight_g: float, initial_weight_g: float, age_days: int) -> float:
        """حساب متوسط النمو اليومي بالجرام"""
        if age_days <= 0:
            return 0.0
        return (current_weight_g - initial_weight_g) / age_days
    
    @staticmethod
    def calculate_fcr(total_feed_kg: float, total_weight_gain_kg: float) -> float:
        """حساب معامل التحويل الغذائي"""
        if total_weight_gain_kg <= 0:
            return 0.0
        return total_feed_kg / total_weight_gain_kg
    
    @staticmethod
    def calculate_mortality_rate(dead_count: int, initial_count: int) -> float:
        """حساب نسبة النفوق"""
        if initial_count <= 0:
            return 0.0
        return (dead_count / initial_count) * 100.0
    
    @staticmethod
    def calculate_livability(initial_count: int, dead_count: int) -> float:
        """حساب نسبة الحيوية"""
        return 100.0 - BroilerFarmManager.calculate_mortality_rate(dead_count, initial_count)
    
    @staticmethod
    def calculate_epef(livability: float, body_weight_kg: float, age_days: int, fcr: float) -> float:
        """حساب مؤشر الأداء الأوروبي EPEF"""
        if age_days <= 0 or fcr <= 0:
            return 0.0
        return (livability * body_weight_kg) / (age_days * fcr) * 100.0
    
    @staticmethod
    def get_temp_humidity_table() -> pd.DataFrame:
        """جدول درجات الحرارة والرطوبة الموصى بها حسب العمر"""
        data = {
            "العمر (يوم)": [1, 7, 14, 21, 28, 35, 42],
            "درجة الحرارة (مئوي)": [33, 30, 28, 26, 24, 22, 21],
            "الرطوبة النسبية (%)": [65, 65, 65, 60, 60, 55, 55]
        }
        return pd.DataFrame(data)
    
    @classmethod
    def save_cycle(cls, farm_name: str, cycle_data: dict, user_id: str = "system") -> str:
        """حفظ دورة إنتاج كاملة"""
        return cls.db.save_production_cycle(cycle_data)
    
    @classmethod
    def get_cycles(cls, farm_name: str = None) -> List[dict]:
        """استرجاع دورات الإنتاج"""
        return cls.db.get_production_cycles(farm_name)
    
    @classmethod
    def save_farm(cls, farm_data: dict, user_id: str = "system") -> str:
        """حفظ مزرعة جديدة"""
        return cls.db.save_farm(farm_data)
    
    @classmethod
    def get_farms(cls) -> List[dict]:
        """استرجاع جميع المزارع"""
        return cls.db.get_farms()
    
    @classmethod
    def save_daily_log(cls, log_data: dict) -> int:
        """حفظ سجل يومي"""
        return cls.db.save_daily_log(log_data)
    
    @classmethod
    def get_daily_logs(cls, farm_id: str) -> List[dict]:
        """استرجاع السجلات اليومية لمزرعة"""
        return cls.db.get_daily_logs(farm_id)

# ==========================================
# 10. مولد التقارير PDF المحسن
# ==========================================
class ProfessionalPDFGenerator:
    """مولد تقارير PDF احترافية"""
    
    def __init__(self):
        self.font_name = 'Helvetica'
        # محاولة تحميل خط عربي
        if os.path.exists("Amiri-Regular.ttf"):
            try:
                pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
                self.font_name = 'Amiri'
            except:
                pass
    
    def generate_comprehensive_report(self, formula: dict, target_dp: float, breed: str, 
                                       cost: float, city: str, local_cost: float, 
                                       local_sym: str, computed_se: float, 
                                       include_charts: bool = True) -> bytes:
        """توليد تقرير شامل بتنسيق PDF"""
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
        
        # العنوان الرئيسي
        story.append(p("تقرير فني شامل - منصة تاور العلمية", size=22, align=TA_CENTER, 
                       color=HexColor('#1b5e20')))
        story.append(Spacer(1, 12))
        
        # معلومات التقرير
        info_lines = [
            f"المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور",
            f"الموقع الجغرافي: {city}",
            f"الفصيل المستهدف: {breed}",
            f"تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ]
        for line in info_lines:
            story.append(p(line, size=11))
        story.append(Spacer(1, 15))
        
        # جدول المؤشرات الرئيسية
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
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        
        # مكونات الخلطة
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
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t2)
        story.append(Spacer(1, 15))
        
        # الرسم البياني إن وجد
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
            except Exception as e:
                story.append(p(f"(تعذر إنشاء الرسم البياني: {str(e)})", size=9))
        
        # التوقيع
        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026", size=9, align=TA_CENTER, 
                       color=HexColor('#666666')))
        story.append(p("تحت إشراف م. عبد القادر إسماعيل تاور", size=9, align=TA_CENTER, 
                       color=HexColor('#666666')))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# ==========================================
# 11. نظام المراجع العلمية
# ==========================================
class ScientificReferenceSystem:
    """نظام المراجع العلمية الموسع"""
    
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
                 "isbn": "978-0309214230", "summary": "المرجع الرسمي لمتطلبات العناصر الغذائية للخنازير."},
                {"id": "REF004", "authors": "NRC (National Research Council)",
                 "year": 2001, "title": "Nutrient Requirements of Dairy Cattle",
                 "publisher": "National Academies Press", "edition": "7th Revised Edition",
                 "isbn": "978-0309069977", "summary": "المرجع الأساسي في تغذية أبقار الحليب."},
                {"id": "REF005", "authors": "Bryden, W.L., Li, X., Ravindran, G.",
                 "year": 2009, "title": "Digestible Amino Acids in Poultry Feed Ingredients",
                 "publisher": "University of Sydney", 
                 "summary": "دراسة شاملة عن الأحماض الأمينية المهضومة في مواد العلف للدواجن."}
            ]
        },
        "energy_carbohydrates": {
            "title": "الطاقة والكربوهيدرات",
            "references": [
                {"id": "REF006", "authors": "Van Soest, P.J.",
                 "year": 1994, "title": "Nutritional Ecology of the Ruminant",
                 "publisher": "Cornell University Press", "edition": "2nd Edition",
                 "isbn": "978-0801427725", "summary": "المرجع الكلاسيكي في تغذية المجترات وتحليل الألياف."},
                {"id": "REF007", "authors": "Blaxter, K.L.",
                 "year": 1989, "title": "Energy Metabolism in Animals and Man",
                 "publisher": "Cambridge University Press", "isbn": "978-0521369433",
                 "summary": "دراسة متعمقة في أيض الطاقة في الحيوانات والإنسان."}
            ]
        },
        "minerals_vitamins": {
            "title": "المعادن والفيتامينات",
            "references": [
                {"id": "REF008", "authors": "Underwood, E.J., Suttle, N.F.",
                 "year": 1999, "title": "The Mineral Nutrition of Livestock",
                 "publisher": "CABI", "edition": "3rd Edition", "isbn": "978-0851991283",
                 "summary": "المرجع الشامل في تغذية المعادن للثروة الحيوانية."},
                {"id": "REF009", "authors": "McDowell, L.R.",
                 "year": 2000, "title": "Vitamins in Animal Nutrition",
                 "publisher": "Academic Press", "isbn": "978-0124833724",
                 "summary": "دراسة متكاملة عن الفيتامينات ودورها في تغذية الحيوان."}
            ]
        },
        "poultry": {
            "title": "تغذية الدواجن",
            "references": [
                {"id": "REF010", "authors": "Leeson, S., Summers, J.D.",
                 "year": 2009, "title": "Commercial Poultry Nutrition",
                 "publisher": "Nottingham University Press", "edition": "3rd Edition",
                 "isbn": "978-1904761578", "summary": "المرجع العملي في تغذية الدواجن التجارية."},
                {"id": "REF011", "authors": "NRC (National Research Council)",
                 "year": 1994, "title": "Nutrient Requirements of Poultry",
                 "publisher": "National Academies Press", "edition": "9th Revised Edition",
                 "isbn": "978-0309048927", "summary": "المرجع الرسمي لمتطلبات الدواجن."}
            ]
        },
        "ruminants": {
            "title": "تغذية المجترات",
            "references": [
                {"id": "REF012", "authors": "Church, D.C.",
                 "year": 1993, "title": "The Ruminant Animal: Digestive Physiology and Nutrition",
                 "publisher": "Waveland Press", "isbn": "978-0881337389",
                 "summary": "المرجع الشامل في فسيولوجيا الهضم والتغذية للمجترات."},
                {"id": "REF013", "authors": "Minson, D.J.",
                 "year": 1990, "title": "Forage in Ruminant Nutrition",
                 "publisher": "Academic Press", "isbn": "978-0124983108",
                 "summary": "دراسة متخصصة في تغذية المجترات على الأعلاف الخشنة."}
            ]
        },
        "sheep_goats": {
            "title": "تغذية الأغنام والماعز",
            "references": [
                {"id": "REF014", "authors": "NRC (National Research Council)",
                 "year": 2007, "title": "Nutrient Requirements of Small Ruminants",
                 "publisher": "National Academies Press", "isbn": "978-0309102131",
                 "summary": "المرجع الرسمي لمتطلبات الأغنام والماعز والمجترات الصغيرة."}
            ]
        },
        "horses": {
            "title": "تغذية الخيول",
            "references": [
                {"id": "REF015", "authors": "NRC (National Research Council)",
                 "year": 2007, "title": "Nutrient Requirements of Horses",
                 "publisher": "National Academies Press", "edition": "6th Revised Edition",
                 "isbn": "978-0309102124", "summary": "المرجع الأساسي في تغذية الخيول ومتطلباتها الغذائية."}
            ]
        },
        "aquaculture": {
            "title": "تغذية الأسماك",
            "references": [
                {"id": "REF016", "authors": "Halver, J.E., Hardy, R.W.",
                 "year": 2002, "title": "Fish Nutrition",
                 "publisher": "Academic Press", "edition": "3rd Edition", "isbn": "978-0123196521",
                 "summary": "المرجع الشامل في تغذية الأسماك والمزارع المائية."}
            ]
        },
        "animal_production": {
            "title": "الإنتاج الحيواني",
            "references": [
                {"id": "REF017", "authors": "Ensminger, M.E., Parker, R.O.",
                 "year": 2002, "title": "Animal Science",
                 "publisher": "Pearson Education", "edition": "5th Edition", "isbn": "978-0131120417",
                 "summary": "المرجع الشامل في علوم الإنتاج الحيواني."}
            ]
        },
        "feed_formulation": {
            "title": "تركيب الأعلاف",
            "references": [
                {"id": "REF018", "authors": "Pond, W.G., Church, D.C., Pond, K.R.",
                 "year": 1995, "title": "Basic Animal Nutrition and Feeding",
                 "publisher": "Wiley", "edition": "4th Edition", "isbn": "978-0471308643",
                 "summary": "المرجع الأساسي في تغذية الحيوان وتركيب الأعلاف."},
                {"id": "REF019", "authors": "CNCPS (Cornell Net Carbohydrate and Protein System)",
                 "year": 2010, "title": "CNCPS Feed Library and Nutrient Requirements",
                 "publisher": "Cornell University", 
                 "summary": "النظام المتقدم لتحليل الأعلاف وتقدير الاحتياجات الغذائية."}
            ]
        },
        "broiler": {
            "title": "إنتاج الدجاج اللاحم",
            "references": [
                {"id": "REF020", "authors": "Ross 308 Broiler Management Guide",
                 "year": 2020, "title": "Ross Broiler Management Handbook",
                 "publisher": "Aviagen", "summary": "الدليل الشامل لإدارة الدجاج اللاحم سلالة روس."},
                {"id": "REF021", "authors": "Cobb-Vantress",
                 "year": 2020, "title": "Cobb 500 Broiler Management Guide",
                 "publisher": "Cobb-Vantress", "summary": "الدليل المتخصص لإدارة دجاج اللاحم سلالة كوب."},
                {"id": "REF022", "authors": "ASPCA",
                 "year": 2019, "title": "Poultry Welfare Standards",
                 "publisher": "ASPCA", "summary": "معايير رعاية الدواجن ورفاهيتها."}
            ]
        },
        "digestible_protein": {
            "title": "البروتين المهضوم",
            "references": [
                {"id": "REF023", "authors": "INRA (Institut National de la Recherche Agronomique)",
                 "year": 2007, "title": "INRA Feeding System for Ruminants",
                 "publisher": "Wageningen Academic Publishers", "isbn": "978-9086860197",
                 "summary": "النظام الفرنسي المتقدم لتغذية المجترات وتقدير البروتين المهضوم."},
                {"id": "REF024", "authors": "Pesti, G.M., Miller, B.R.",
                 "year": 2009, "title": "Least-Cost Feed Formulation: Theory and Practice",
                 "publisher": "University of Georgia", 
                 "summary": "النظرية والتطبيق العملي لتركيب الأعلاف بأقل تكلفة."}
            ]
        }
    }
    
    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم (Digestible Protein) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف. يتم حسابه بضرب نسبة البروتين الخام في معامل الهضم لكل مادة علفية.",
            "reference": "REF023",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (Starch Equivalent - SE) هو مقياس لكمية الطاقة التي يوفرها العلف للحيوان، مقارنة بالطاقة التي يوفرها النشاء النقي.",
            "reference": "REF006",
            "simplified": "معادل النشاء يقيس كمية الطاقة في العلف."
        },
        "كيف يتم تركيب العلف الأمثل": {
            "answer": "يتم تركيب العلف الأمثل باستخدام محرك الاستمثال الخطي (Linear Programming) الذي يحسب أقل تكلفة لتحقيق متطلبات غذائية محددة.",
            "reference": "REF024",
            "simplified": "نستخدم برنامجاً ذكياً يحسب أرخص خلطة علفية تلبي جميع احتياجات الحيوان."
        },
        "ما هي أهمية إضافة الإنزيمات للأعلاف": {
            "answer": "الإنزيمات في الأعلاف تعمل على تحسين هضم واستفادة الحيوان من العناصر الغذائية.",
            "reference": "REF010",
            "simplified": "الإنزيمات تساعد الحيوان على هضم العلف بشكل أفضل."
        },
        "ما هو مؤشر EPEF": {
            "answer": "مؤشر الأداء الأوروبي EPEF هو مقياس شامل لكفاءة إنتاج الدجاج اللاحم.",
            "reference": "REF020",
            "simplified": "EPEF هو رقم يعبر عن كفاءة مزرعة الدجاج."
        },
        "ما هو الفرق بين البروتين الخام والمهضوم": {
            "answer": "البروتين الخام (CP) هو إجمالي محتوى النيتروجين في العلف، بينما البروتين المهضوم (DP) هو الجزء الذي يتم هضمه وامتصاصه فعلياً.",
            "reference": "REF023",
            "simplified": "البروتين الخام هو كل البروتين الموجود، أما المهضوم فهو الجزء المستفاد منه."
        },
        "كيف يتم حساب معامل التحويل الغذائي FCR": {
            "answer": "معامل التحويل الغذائي FCR = كمية العلف المستهلك / كمية الوزن المكتسب.",
            "reference": "REF018",
            "simplified": "FCR يبين كمية العلف التي يحتاجها الحيوان ليكتسب كيلو جرام واحد من الوزن."
        },
        "كيف يمكن تحسين كفاءة مزرعة الدجاج": {
            "answer": "تحسين كفاءة مزرعة الدجاج يتم من خلال برامج تغذية دقيقة، تحصين صارم، تحكم في البيئة، ومراقبة جودة العلف والماء.",
            "reference": "REF021",
            "simplified": "لتحسين المزرعة: استخدم تغذية دقيقة، حافظ على النظافة، طبق تحصينات، وراقب الأداء يومياً."
        }
    }
    
    @staticmethod
    def get_reference(ref_id: str) -> Optional[dict]:
        """استرجاع مرجع معين"""
        for category in ScientificReferenceSystem.REFERENCES.values():
            for ref in category.get("references", []):
                if ref.get("id") == ref_id:
                    return ref
        return None
    
    @staticmethod
    def get_knowledge_answer(question: str) -> Optional[dict]:
        """استرجاع إجابة لسؤال معرفي"""
        for key, value in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            if key in question:
                ref = ScientificReferenceSystem.get_reference(value.get("reference", ""))
                return {
                    "answer": value["answer"],
                    "simplified": value.get("simplified", value["answer"]),
                    "reference": ref
                }
        return None

# ==========================================
# 12. دوال الإرسال (بريد، واتساب)
# ==========================================
def send_code_to_mail(receiver_email: str, attachment_type: str = "full") -> bool:
    """إرسال الكود المصدري عبر البريد الإلكتروني"""
    try:
        sender_email = SENDER_EMAIL
        sender_password = SENDER_PASSWORD
    except:
        st.error("⚠️ لم يتم العثور على بيانات البريد الإلكتروني")
        return False
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود الكامل - منصة تاور العلمية"
    
    body = """السلام عليكم،

مرفق مع هذه الرسالة النسخة البرمجية الكاملة والمستقرة لمنصة تاور العلمية.

مع تحيات
الاختصاصي م. عبد القادر إسماعيل تاور"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        # إرفاق الكود المصدري
        try:
            with open(__file__, "r", encoding="utf-8") as f:
                code_content = f.read()
        except:
            code_content = "# الكود غير متاح للقراءة المباشرة"
        
        attachment = MIMEText(code_content, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', filename="tower_scientific_platform.py")
        msg.attach(attachment)
        
        # إرسال البريد
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ فشل الإرسال: {e}")
        return False

def send_whatsapp_alert(phone_number: str, message: str) -> None:
    """إنشاء رابط واتساب لإرسال تنبيه"""
    encoded_msg = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_msg}"
    st.markdown(f"""
    <div style='background:#e8f5e9; padding:10px; border-radius:8px; direction:ltr;'>
        📲 <b>تنبيه عبر واتساب:</b> 
        <a href='{whatsapp_url}' target='_blank'>اضغط لإرسال الرسالة إلى {phone_number}</a>
        <br>{message}
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 13. دوال إضافية (معادلات متقدمة، تحليلات)
# ==========================================
def calculate_heritability(selection_response: float, selection_differential: float) -> float:
    """حساب معامل التوريث h² = R/S"""
    if selection_differential == 0:
        return 0.0
    return selection_response / selection_differential

def calculate_economic_weight(price_per_kg: float, feed_cost: float, fcr: float) -> float:
    """حساب الوزن الاقتصادي لتحسين FCR"""
    if feed_cost * fcr == 0:
        return 0.0
    return price_per_kg / (feed_cost * fcr)

def calculate_optimal_protein(energy: float, lysine_ratio: float = 0.06) -> float:
    """حساب البروتين الأمثل بناءً على الطاقة ونسبة اللايسين"""
    return energy * lysine_ratio / 0.06

def generate_random_feed_formula(num_ingredients: int = 5) -> dict:
    """توليد خلطة عشوائية للأغراض التعليمية"""
    ingredients = list(BIG_FEEDS_LIBRARY["🌾 الحبوب ومصادر الطاقة الكبرى"].keys())[:num_ingredients]
    weights = np.random.dirichlet(np.ones(num_ingredients)) * 100
    return {ing: w for ing, w in zip(ingredients, weights)}

def simulate_growth_curve(initial_weight: float, final_weight: float, days: int, curve_type: str = "linear") -> np.ndarray:
    """محاكاة منحنى النمو"""
    if curve_type == "linear":
        return np.linspace(initial_weight, final_weight, days)
    elif curve_type == "exponential":
        return initial_weight * (final_weight/initial_weight) ** (np.arange(days)/days)
    elif curve_type == "sigmoid":
        t = np.arange(days)
        return initial_weight + (final_weight - initial_weight) / (1 + np.exp(-0.1 * (t - days/2)))
    else:
        return np.linspace(initial_weight, final_weight, days)

def perform_sensitivity_analysis(base_formula: dict, ingredient: str, variation_range: float = 0.2) -> dict:
    """تحليل حساسية تغيير نسبة مكون معين على التكلفة"""
    results = {}
    base_cost = sum([BIG_FEEDS_LIBRARY["🌾 الحبوب ومصادر الطاقة الكبرى"].get(ing, {}).get("CP", 0) for ing in base_formula])
    for factor in [0.5, 0.75, 1.0, 1.25, 1.5]:
        modified = base_formula.copy()
        if ingredient in modified:
            modified[ingredient] = modified[ingredient] * factor
            # إعادة التوازن
            total = sum(modified.values())
            if total > 0:
                for k in modified:
                    modified[k] = (modified[k] / total) * 100
        results[f"{factor*100:.0f}%"] = modified
    return results

def calculate_water_requirement(animal_type: str, weight_kg: float, temperature_c: float) -> float:
    """حساب الاحتياج المائي اليومي حسب نوع الحيوان"""
    base_requirements = {
        "أبقار": 0.05,
        "أغنام": 0.04,
        "ماعز": 0.045,
        "خيول": 0.035,
        "دواجن": 0.08,
        "أسماك": 0.02
    }
    base = base_requirements.get(animal_type, 0.05)
    temp_factor = 1 + (temperature_c - 20) / 100
    return weight_kg * base * temp_factor

def calculate_floor_space(animal_type: str, weight_kg: float, density_factor: float = 1.0) -> float:
    """حساب المساحة الأرضية المطلوبة لكل حيوان"""
    space_requirements = {
        "أبقار": 4.0,
        "أغنام": 1.5,
        "ماعز": 1.2,
        "خيول": 8.0,
        "دواجن": 0.08,
        "أسماك": 0.01
    }
    base = space_requirements.get(animal_type, 2.0)
    return base * (weight_kg / 100) ** 0.7 * density_factor

def calculate_expected_milk_yield(breed: str, weight_kg: float, days_in_milk: int, parity: int) -> float:
    """حساب إنتاج الحليب المتوقع للأبقار"""
    base_yield = {"هولشتاين": 25, "كنانة": 15, "بطانة": 12, "محسن": 20}
    base = base_yield.get(breed, 15)
    weight_factor = weight_kg / 500
    parity_factor = 1 + 0.1 * min(parity, 5)
    return base * weight_factor * parity_factor * (days_in_milk / 305)

# ==========================================
# 14. دالة تحميل الصورة (مع Fallback)
# ==========================================
@st.cache_data(ttl=3600)
def get_image_base64(paths: List[str]) -> Optional[str]:
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode()
            except:
                pass
    # Fallback: استخدام صورة من الإنترنت
    try:
        import requests
        response = requests.get("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600", timeout=5)
        return base64.b64encode(response.content).decode()
    except:
        return None

# ==========================================
# 15. دوال تحميل وحفظ أسعار المدن
# ==========================================
def load_city_prices() -> dict:
    if os.path.exists(CITY_PRICES_FILE):
        try:
            with open(CITY_PRICES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_city_prices(data: dict) -> None:
    try:
        with open(CITY_PRICES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"خطأ في حفظ أسعار المدن: {e}")

# ==========================================
# 16. نظام أسعار السوق (Market Price Engine)
# ==========================================
class MarketPriceEngine:
    @staticmethod
    @lru_cache(maxsize=128)
    def get_adjusted_market_data(country: str, state_or_region: str, city: str) -> Dict[str, float]:
        """استرجاع أسعار السوق مع تعديلات حسب الموقع"""
        feed_prices = {}
        for cat in BIG_FEEDS_LIBRARY.values():
            for ing in cat:
                feed_prices[ing] = 250.0
        
        # أسعار أساسية
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
            "بيكربونات الصوديوم (الصودا)": 340.0
        }
        feed_prices.update(base_prices)
        
        # تعديلات حسب الموقع
        multiplier = 1.0
        if country == "السودان":
            multiplier = 1.15
            if "كردفان" in state_or_region:
                multiplier = 1.20
                feed_prices["سورجم (فتريتة)"] *= 0.85
                feed_prices["أمباز الفول السوداني (كسب)"] *= 0.85
        elif country == "LIBYA":
            multiplier = 1.10
            if city == "طبرق":
                multiplier = 1.06
        elif country == "مصر":
            multiplier = 1.04
        
        for k in feed_prices:
            feed_prices[k] *= multiplier
        
        # تطبيق الأسعار المخصصة إن وجدت
        city_key = f"{country}|||{state_or_region}|||{city}"
        custom_prices = load_city_prices().get(city_key, {})
        for k, v in custom_prices.items():
            if k in feed_prices:
                feed_prices[k] = v
        
        return feed_prices

# ==========================================
# 17. تكوين الصفحة وإعدادات Streamlit
# ==========================================
st.set_page_config(
    page_title="منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# تهيئة حالة الجلسة (Session State)
if "approved" not in st.session_state:
    st.session_state["approved"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None
if "login_welcome_shown" not in st.session_state:
    st.session_state["login_welcome_shown"] = False
if "login_attempts" not in st.session_state:
    st.session_state["login_attempts"] = 0
if "last_login_time" not in st.session_state:
    st.session_state["last_login_time"] = None

# متغيرات التطبيق
if "active_formula" not in st.session_state:
    st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0}
if "active_cp_tag" not in st.session_state:
    st.session_state["active_cp_tag"] = 12.0
if "active_se_tag" not in st.session_state:
    st.session_state["active_se_tag"] = 65.0
if "active_breed_tag" not in st.session_state:
    st.session_state["active_breed_tag"] = "سلالة عامة"
if "computed_ton_cost" not in st.session_state:
    st.session_state["computed_ton_cost"] = 280.0

# بيانات المزارع (للتوافق مع النسخة القديمة)
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

# ==========================================
# 18. CSS المخصص
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
* { font-family: 'Cairo', sans-serif; }
html, body, .stApp { background-color: #f5f5f5; }
.main-box {
    background: white;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
.section-title {
    color: #1b5e20;
    border-right: 6px solid #2e7d32;
    padding-right: 15px;
    font-size: 1.5rem;
    font-weight: bold;
    margin: 20px 0;
}
.formula-item {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 12px 18px;
    border-radius: 10px;
    margin-bottom: 8px;
    border-right: 4px solid #2e7d32;
}
.stock-critical {
    background: #ffebee;
    color: #c62828;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: bold;
}
.stock-normal {
    background: #e8f5e9;
    color: #2e7d32;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: bold;
}
.price-card {
    background: #f5f5f5;
    padding: 15px;
    border-radius: 10px;
    border-right: 4px solid #1565C0;
    margin: 10px 0;
}
.warning-card {
    background: #fff3e0;
    padding: 12px;
    border-radius: 8px;
    border-right: 4px solid #f57c00;
    margin: 8px 0;
}
.profile-img-style {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #d4af37;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.animal-banner-img {
    width: 100%;
    max-height: 200px;
    object-fit: cover;
    border-radius: 12px;
    margin: 10px 0;
}
.sack-tag {
    border: 3px dashed #1b5e20;
    padding: 30px;
    border-radius: 15px;
    background: #f1f8e9;
    text-align: center;
}
.metric-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    text-align: center;
    height: 100%;
}
.mini-left-signature {
    position: fixed;
    left: 20px;
    bottom: 20px;
    background: #1b5e20;
    color: white;
    padding: 8px 20px;
    border-radius: 25px;
    font-size: 0.8rem;
    z-index: 1000;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 19. بوابة الدخول (Login)
# ==========================================
if not st.session_state["approved"]:
    # التحقق من محاولات الدخول الفاشلة
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        if st.session_state["last_login_time"]:
            time_diff = (datetime.now() - st.session_state["last_login_time"]).seconds
            if time_diff < LOCKOUT_TIME:
                st.markdown('<div class="main-box" style="max-width:500px;margin:100px auto;text-align:center;">', unsafe_allow_html=True)
                st.error(f"🔒 تم قفل النظام مؤقتاً. يرجى المحاولة بعد {LOCKOUT_TIME - time_diff} ثانية")
                st.markdown('</div>', unsafe_allow_html=True)
                st.stop()
            else:
                st.session_state["login_attempts"] = 0
    
    st.markdown('<div class="main-box" style="max-width:500px;margin:100px auto;text-align:center;">', unsafe_allow_html=True)
    st.markdown("""
    <h1 style="color:#1b5e20;">🌾 منصة تاور العلمية</h1>
    <p style="color:#555;font-size:1.1rem;">للانتاج الحيواني وتركيب الاعلاف</p>
    <hr>
    """, unsafe_allow_html=True)
    
    # عرض رمز QR (إن أمكن)
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("https://tower-scientific-platform.streamlit.app")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        st.markdown(f'<img src="data:image/png;base64,{qr_base64}" width="150" style="margin:10px auto;display:block;">', unsafe_allow_html=True)
    except:
        pass
    
    login_option = st.radio("طريقة الدخول:", ["كود الدخول السري", "اسم المستخدم وكلمة المرور"], horizontal=True)
    
    if login_option == "كود الدخول السري":
        input_code = st.text_input("🔑 أدخل كود الدخول الخاص بك:", type="password")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
                if input_code.strip() in CODES_DB:
                    st.session_state["approved"] = True
                    st.session_state["user_role"] = CODES_DB[input_code.strip()]["role"]
                    st.session_state["user"] = {
                        "user_id": input_code.strip(),
                        "username": CODES_DB[input_code.strip()]["name"],
                        "role": CODES_DB[input_code.strip()]["role"],
                        "full_name": CODES_DB[input_code.strip()]["name"]
                    }
                    st.session_state["login_welcome_shown"] = False
                    st.session_state["login_attempts"] = 0
                    st.rerun()
                else:
                    st.session_state["login_attempts"] += 1
                    st.session_state["last_login_time"] = datetime.now()
                    remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                    st.error(f"❌ الكود غير صحيح! متبقي {remaining} محاولات")
        with col2:
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
                st.session_state["user"] = user
                st.session_state["login_welcome_shown"] = False
                st.session_state["login_attempts"] = 0
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                st.session_state["last_login_time"] = datetime.now()
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ اسم المستخدم أو كلمة المرور غير صحيحة! متبقي {remaining} محاولات")
        st.caption("💡 المستخدم الافتراضي: admin / admin123")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 20. الواجهة الرئيسية (بعد تسجيل الدخول)
# ==========================================
# عرض الترحيب
if not st.session_state["login_welcome_shown"]:
    role_messages = {
        "owner": "👋 مرحباً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور",
        "specialist": "🔬 أهلاً بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني",
        "breeder": "🚜 أهلاً وسهلاً بإخواننا المربين، شركاء النجاح"
    }
    st.toast(role_messages.get(st.session_state["user_role"], "مرحباً"), icon="🌾")
    st.session_state["login_welcome_shown"] = True

# الهيكل الرئيسي
st.markdown('<div class="main-box">', unsafe_allow_html=True)

# رأس الصفحة
col_logo, col_title = st.columns([0.2, 0.8])
with col_logo:
    img_data = get_image_base64(PHOTO_OPTIONS)
    if img_data:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_data}" class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown('<div style="width:150px;height:150px;border-radius:50%;background:#e8f5e9;display:flex;align-items:center;justify-content:center;font-size:4rem;">🌾</div>', unsafe_allow_html=True)

with col_title:
    st.markdown("""
    <h1 style="color:#1b5e20;font-size:2.5rem;">منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</h1>
    <p style="color:#1565C0;font-size:1.2rem;">محرك الاستمثال الخطي المتقدم - البروتين المهضوم ومعادل النشاء</p>
    <h3 style="color:#c62828;">الاختصاصي م. عبد القادر إسماعيل تاور</h3>
    """, unsafe_allow_html=True)

# معلومات المستخدم
col_user, col_logout = st.columns([0.85, 0.15])
with col_user:
    role_names = {
        "owner": "👑 المالك - الاختصاصي م. عبد القادر إسماعيل تاور",
        "specialist": "🔬 مختص - طبيب بيطري / إنتاج حيواني",
        "breeder": "🌾 مربي - شريك في الإنتاج"
    }
    st.markdown(f'<div style="background:#f5f5f5;padding:10px;border-radius:8px;text-align:right;">✅ {role_names.get(st.session_state["user_role"], "مستخدم")}</div>', unsafe_allow_html=True)
with col_logout:
    if st.button("🚪 خروج", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["inventory_cache", "broiler_farms"]:
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.session_state["user"] = None
        st.rerun()

st.markdown("---")

# ==========================================
# 21. التبويبات الرئيسية
# ==========================================
# تعريف التبويبات حسب الصلاحية
if st.session_state["user_role"] == "owner":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "📊 بورصة الأسعار",
        "🏭 إدارة المخزون",
        "🧾 الفواتير والمبيعات",
        "🖨️ مصمم الديباجة",
        "📈 التحليلات المتقدمة",
        "🐔 إدارة مزارع الدجاج",
        "💬 تعليقات المختصين",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم",
        "⚙️ إعدادات النظام"
    ]
elif st.session_state["user_role"] == "specialist":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "📊 بورصة الأسعار",
        "🏭 إدارة المخزون",
        "🧾 الفواتير والمبيعات",
        "🖨️ مصمم الديباجة",
        "📈 التحليلات المتقدمة",
        "💬 تعليقات المختصين",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم"
    ]
else:  # breeder
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم"
    ]

tabs = st.tabs(tabs_titles)

# ==========================================
# 22. التبويب الأول: النمذجة والحسابات العلفية
# ==========================================
with tabs[0]:
    sub_tab1, sub_tab2 = st.tabs(["🎯 تركيب علفة بأقل تكلفة", "🔬 مختبر تحليل الأعلاف"])
    
    # ----------------------------------------------------------------------
    # التبويب الفرعي 1: تركيب العلف
    # ----------------------------------------------------------------------
    with sub_tab1:
        st.markdown('<div class="section-title">🌍 تحديد الموقع الجغرافي وبورصة الأسعار</div>', unsafe_allow_html=True)
        
        col_country, col_state, col_city = st.columns(3)
        with col_country:
            user_country = st.selectbox("اختر الدولة:", ["السودان", "LIBYA", "مصر", "باقي دول العالم"])
        c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
        local_rate = c_info["rate"]
        local_sym = c_info["sym"]
        
        chosen_state = "عام"
        with col_state:
            if user_country == "السودان":
                chosen_state = st.selectbox("الولاية:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال كردفان", "ولاية جنوب كردفان", "ولاية غرب كردفان"])
            elif user_country == "LIBYA":
                chosen_state = st.selectbox("المنطقة:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
            else:
                chosen_state = st.selectbox("الإقليم:", ["المركز الرئيسي", "الأسواق المفتوحة"])
        
        with col_city:
            if user_country == "السودان":
                cities = {"ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"], "ولاية الجزيرة": ["ود مدني", "الحصاحيصا"]}
                user_city = st.selectbox("المدينة:", cities.get(chosen_state, ["عام"]))
            elif user_country == "LIBYA":
                cities = {"المنطقة الشرقية": ["طبرق", "بنغازي", "البيضاء"], "المنطقة الغربية": ["طرابلس", "مصراتة"]}
                user_city = st.selectbox("المدينة:", cities.get(chosen_state, ["عام"]))
            else:
                user_city = st.text_input("المدينة:", "طبرق")
        
        # عرض أسعار السوق
        live_prices = MarketPriceEngine.get_adjusted_market_data(user_country, chosen_state, user_city)
        
        # اختيار القطاع والإنتاج
        st.markdown('<div class="section-title">⚖️ اختيار القطاع والنوع</div>', unsafe_allow_html=True)
        col_sector, col_sub, col_stage = st.columns(3)
        with col_sector:
            main_sector = st.selectbox("القطاع الرئيسي:", ["الأغنام", "الماعز", "الأبقار", "الخيول", "الدواجن", "الأسماك"])
        with col_sub:
            if main_sector == "الأغنام":
                sub_type = st.selectbox("السلالة:", ["ضأن صحراوي", "بربري", "نعيمي"])
            elif main_sector == "الماعز":
                sub_type = st.selectbox("السلالة:", ["نوبي", "صحراوي", "بور"])
            elif main_sector == "الأبقار":
                sub_type = st.selectbox("السلالة:", ["كنانة", "بطانة", "هولشتاين"])
            elif main_sector == "الخيول":
                sub_type = st.selectbox("السلالة:", ["عربي أصيل", "ثوروبريد", "هجين"])
            elif main_sector == "الدواجن":
                sub_type = st.selectbox("النوع:", ["لاحم", "بياض", "سمان"])
            else:
                sub_type = st.selectbox("النوع:", ["بلطي", "قرموط"])
        with col_stage:
            stages = {
                "الأغنام": ["تسمين", "حليب", "حمل"],
                "الماعز": ["تسمين", "حليب", "حمل"],
                "الأبقار": ["حليب", "تسمين"],
                "الخيول": ["رياضة", "نمو", "مرضعات"],
                "الدواجن": ["بادي", "نامي", "ناهي", "بياض"],
                "الأسماك": ["زريعة", "نمو", "تسمين"]
            }
            prod_stage = st.selectbox("مرحلة الإنتاج:", stages.get(main_sector, ["عام"]))
        
        # حدود الموازنة
        st.markdown('<div class="section-title">📋 حدود الموازنة</div>', unsafe_allow_html=True)
        col_dp, col_se = st.columns(2)
        with col_dp:
            default_dp = 12.0 if "تسمين" in prod_stage else 10.0
            target_dp = st.slider("البروتين المهضوم المستهدف (%)", 5.0, 40.0, default_dp, 0.5)
        with col_se:
            default_se = 65.0 if "تسمين" in prod_stage else 60.0
            target_se = st.slider("معادل النشاء المستهدف (SE)", 10.0, 90.0, default_se, 1.0)
        
        # اختيار المكونات
        st.markdown("### 📦 اختيار المواد العلفية")
        selected_ingredients = []
        ingredient_prices = {}
        
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            with st.expander(f"📁 {cat_name}"):
                cols = st.columns(3)
                for idx, (ing_name, data) in enumerate(items.items()):
                    with cols[idx % 3]:
                        checked = st.checkbox(ing_name, value=ing_name in ["ذرة صفراء", "كسب فول صويا 44%"], key=f"sel_{ing_name}")
                        if checked:
                            selected_ingredients.append(ing_name)
                            price = live_prices.get(ing_name, 250.0)
                            ingredient_prices[ing_name] = st.number_input(f"سعر {ing_name}", min_value=0.0, value=float(price), key=f"pr_{ing_name}")
        
        # الإضافات الإلزامية
        mandatory_additives = {"ملح الطعام": 0.5, "مضاد سموم فطرية": 0.2, "الحجر الجيري (بودرة بلاط)": 1.5}
        if main_sector in ["الأغنام", "الماعز", "الأبقار"]:
            mandatory_additives["بيكربونات الصوديوم (الصودا)"] = 0.75
        if main_sector in ["الدواجن", "الأسماك"]:
            mandatory_additives["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05
        
        for item in mandatory_additives:
            if item not in selected_ingredients:
                selected_ingredients.append(item)
                ingredient_prices[item] = live_prices.get(item, 40.0)
        
        # زر التشغيل
        if st.button("🚀 تشغيل محرك الاستمثال", type="primary", use_container_width=True):
            if len(selected_ingredients) < 3:
                st.error("❌ يرجى اختيار 3 مواد علفية على الأقل")
            else:
                # بناء مصفوفة الاستمثال
                c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
                bounds = [(mandatory_additives.get(ing, 0.0), mandatory_additives.get(ing, 100.0)) if ing in mandatory_additives else (0.0, 100.0) for ing in selected_ingredients]
                
                # قيد المجموع = 100%
                A_eq = [[1.0 for _ in selected_ingredients]]
                b_eq = [100.0]
                
                # قيد البروتين المهضوم
                dp_row = []
                se_row = []
                for ing in selected_ingredients:
                    cp = 0.0
                    dc = 0.0
                    se = 0.0
                    for cat in BIG_FEEDS_LIBRARY.values():
                        if ing in cat:
                            cp = cat[ing].get("CP", 0.0)
                            dc = cat[ing].get("DC", 0.0)
                            se = cat[ing].get("SE", 0.0)
                    dp_row.append(cp * dc)
                    se_row.append(se)
                A_eq.append(dp_row)
                b_eq.append(target_dp * 100.0)
                
                # قيد معادل النشاء
                A_ub = [[-1.0 * x for x in se_row]]
                b_ub = [-1.0 * target_se * 100.0]
                
                # تشغيل المحرك
                res = linprog(c_vector, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
                
                if res.success:
                    formula = {}
                    computed_se = 0.0
                    for idx, ing in enumerate(selected_ingredients):
                        if res.x[idx] > 0.001:
                            formula[ing] = res.x[idx]
                            for cat in BIG_FEEDS_LIBRARY.values():
                                if ing in cat:
                                    computed_se += (res.x[idx] / 100.0) * cat[ing].get("SE", 0.0)
                    
                    st.session_state["active_formula"] = formula
                    st.session_state["active_cp_tag"] = target_dp
                    st.session_state["active_se_tag"] = computed_se
                    st.session_state["active_breed_tag"] = sub_type
                    
                    st.success("✅ تم توليد الخلطة المثلى!")
                    
                    # عرض النتائج
                    col_res1, col_res2 = st.columns([0.6, 0.4])
                    with col_res1:
                        st.markdown("#### 📝 مكونات الخلطة (كجم/طن):")
                        for ing, pct in formula.items():
                            st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.2f}% ({pct*10:.1f} كجم)</div>', unsafe_allow_html=True)
                        
                        ton_cost = res.fun / 100.0
                        st.metric(f"💰 تكلفة الطن في {user_city}:", f"${ton_cost:.2f} ({ton_cost*local_rate:,.2f} {local_sym})")
                        
                        # حساب الطاقة الأيضية
                        total_me = 0.0
                        for idx, ing in enumerate(selected_ingredients):
                            if res.x[idx] > 0:
                                for cat in BIG_FEEDS_LIBRARY.values():
                                    if ing in cat:
                                        cp = cat[ing].get("CP", 0)
                                        ee = cat[ing].get("EE", 0)
                                        nfe = max(0, 100 - cp - cat[ing].get("NDF", 0) - ee - cat[ing].get("ASH", 0))
                                        me = calculate_me(cp, ee, nfe)
                                        total_me += (res.x[idx] / 100) * me
                        st.metric("🔥 الطاقة الأيضية (ME)", f"{total_me:.0f} ك.كال/كجم")
                        
                        # زر تحميل PDF
                        try:
                            pdf_data = pdf_generator.generate_comprehensive_report(
                                formula, target_dp, sub_type, ton_cost, user_city,
                                ton_cost*local_rate, local_sym, computed_se
                            )
                            st.download_button("📥 تحميل التقرير PDF", pdf_data, 
                                             file_name=f"خلطة_{sub_type}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                             mime="application/pdf")
                        except Exception as e:
                            st.warning(f"⚠️ تعذر توليد PDF: {e}")
                    
                    with col_res2:
                        # رسم بياني
                        fig = px.pie(values=list(formula.values()), names=list(formula.keys()), 
                                   title="توزيع المكونات", color_discrete_sequence=px.colors.sequential.Greens)
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # شريط بياني
                        chart_data = pd.DataFrame({
                            'المكون': list(formula.keys()),
                            'النسبة': list(formula.values())
                        })
                        st.bar_chart(chart_data.set_index('المكون'))
                else:
                    st.error("❌ تعذر إيجاد حل رياضي. يرجى إضافة مواد علفية أخرى أو تخفيف القيود.")
    
    # ----------------------------------------------------------------------
    # التبويب الفرعي 2: مختبر التحليل
    # ----------------------------------------------------------------------
    with sub_tab2:
        st.markdown('<div class="section-title">🔬 مختبر تحليل الخلطات الجاهزة</div>', unsafe_allow_html=True)
        st.write("أدخل أوزان المكونات بالكيلوجرام لتحليل الخلطة الحالية:")
        
        # اختيار الحيوان المستهدف
        col_animal, col_stage_lab = st.columns(2)
        with col_animal:
            target_animal = st.selectbox("الحيوان المستهدف:", ["أبقار", "أغنام", "ماعز", "خيول", "دواجن", "سمان", "أسماك"])
        with col_stage_lab:
            if target_animal in ["أبقار", "أغنام", "ماعز"]:
                prod_type = st.selectbox("مرحلة الإنتاج:", ["تسمين", "حليب", "حمل"])
            elif target_animal in ["دواجن", "سمان"]:
                prod_type = st.selectbox("مرحلة الإنتاج:", ["بادي", "نامي", "ناهي"])
            else:
                prod_type = st.selectbox("مرحلة الإنتاج:", ["نمو", "تسمين"])
        
        # إدخال المكونات
        lab_inputs = {}
        all_ingredients = []
        for cat in BIG_FEEDS_LIBRARY.values():
            all_ingredients.extend(list(cat.keys()))
        
        cols = st.columns(4)
        for idx, ing in enumerate(all_ingredients):
            with cols[idx % 4]:
                lab_inputs[ing] = st.number_input(f"{ing}", min_value=0.0, value=0.0, step=5.0, key=f"lab_{ing}")
        
        if st.button("🧪 تحليل الخلطة", type="primary", use_container_width=True):
            total_weight = sum(lab_inputs.values())
            if total_weight <= 0:
                st.warning("⚠️ يرجى إدخال أوزان أكبر من الصفر")
            else:
                total_cp = 0.0
                total_dp = 0.0
                total_se = 0.0
                analysis_data = []
                
                for ing, weight in lab_inputs.items():
                    if weight > 0:
                        pct = weight / total_weight
                        cp = 0.0
                        dc = 0.0
                        se = 0.0
                        for cat in BIG_FEEDS_LIBRARY.values():
                            if ing in cat:
                                cp = cat[ing].get("CP", 0.0)
                                dc = cat[ing].get("DC", 0.0)
                                se = cat[ing].get("SE", 0.0)
                        total_cp += pct * cp
                        total_dp += pct * (cp * dc)
                        total_se += pct * se
                        analysis_data.append({"المادة": ing, "الوزن": weight, "النسبة": f"{pct*100:.1f}%"})
                
                st.success("✅ تم تحليل الخلطة بنجاح!")
                
                # عرض النتائج
                st.markdown("#### 📊 نتائج التحليل:")
                st.metric("البروتين الخام (CP)", f"{total_cp:.2f}%")
                st.metric("البروتين المهضوم (DP)", f"{total_dp:.2f}%")
                st.metric("معادل النشاء (SE)", f"{total_se:.2f} وحدة")
                
                # جدول المكونات
                st.dataframe(pd.DataFrame(analysis_data), use_container_width=True)

# ==========================================
# 23. تبويب بورصة الأسعار
# ==========================================
if "📊 بورصة الأسعار" in tabs_titles:
    tab_idx = tabs_titles.index("📊 بورصة الأسعار")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">📊 بورصة تاور المركزية</div>', unsafe_allow_html=True)
        
        # أسعار الماشية
        st.subheader("🐄 أسعار الماشية والداجن")
        livestock_data = {
            "عجول تسمين": 1350.0,
            "أبقار محلية": 900.0,
            "ضأن": 180.0,
            "ماعز": 130.0,
            "خيول عربية": 4500.0,
            "كتكوت لاحم": 0.65,
            "دجاج بياض": 5.50
        }
        
        cols = st.columns(3)
        for idx, (item, price) in enumerate(livestock_data.items()):
            with cols[idx % 3]:
                st.metric(item, f"${price:.2f}")
        
        # أسعار المنتجات
        st.subheader("🥛 أسعار المنتجات الحيوانية")
        products_data = {
            "لحم بقري (كجم)": 7.50,
            "لحم ضأن (كجم)": 9.00,
            "لحم دجاج (كجم)": 3.80,
            "بيض (30 طبق)": 4.20,
            "حليب خام (لتر)": 0.90,
            "جبن أبيض (كجم)": 5.00
        }
        
        cols = st.columns(3)
        for idx, (item, price) in enumerate(products_data.items()):
            with cols[idx % 3]:
                st.metric(item, f"${price:.2f}")
        
        # التنبؤ بالأسعار
        st.markdown("---")
        st.subheader("🔮 تنبؤات الأسعار")
        predictor = PricePredictor()
        
        pred_cols = st.columns(3)
        for idx, ing in enumerate(["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح"]):
            with pred_cols[idx]:
                pred = predictor.predict_price(ing, 7)
                if pred.get('prediction'):
                    icon = "📈" if pred.get('trend') == 'up' else "📉" if pred.get('trend') == 'down' else "➡️"
                    st.metric(f"{icon} {ing}", f"${pred['prediction']:.2f}",
                             delta=f"{pred['prediction'] - pred.get('current_price', 0):.2f}")

# ==========================================
# 24. تبويب إدارة المخزون
# ==========================================
if "🏭 إدارة المخزون" in tabs_titles:
    tab_idx = tabs_titles.index("🏭 إدارة المخزون")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">🏭 لوحة تحكم المخزون الذكية</div>', unsafe_allow_html=True)
        
        # تحديث المخزون من قاعدة البيانات
        inventory = InventoryManager.get_inventory()
        stock_warnings = InventoryManager.check_stock_levels()
        
        # إحصائيات
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("إجمالي المواد", len(inventory))
        with col2:
            critical = sum(1 for v in stock_warnings.values() if v == "نفذ المخزون")
            st.metric("نفذ المخزون", critical)
        with col3:
            low = sum(1 for v in stock_warnings.values() if v == "منخفض")
            st.metric("منخفض", low)
        with col4:
            safe = len(inventory) - critical - low
            st.metric("آمن", safe)
        
        st.markdown("---")
        
        # عرض المخزون
        cols = st.columns(3)
        for idx, (item, data) in enumerate(list(inventory.items())[:30]):
            with cols[idx % 3]:
                qty = data["quantity"]
                threshold = data["min_threshold"]
                if qty <= 0:
                    status = f'<span class="stock-critical">⚠️ نفذ: {qty:.2f} طن</span>'
                elif qty < threshold:
                    status = f'<span class="stock-critical">⚠️ حرج: {qty:.2f} طن</span>'
                else:
                    status = f'<span class="stock-normal">✅ {qty:.2f} طن</span>'
                st.markdown(f"**{item}** | {status}", unsafe_allow_html=True)
                
                if st.session_state["user_role"] == "owner":
                    new_qty = st.number_input(f"تحديث", min_value=0.0, value=float(qty), key=f"inv_{item}")
                    if new_qty != qty:
                        InventoryManager.update_stock(item, new_qty, st.session_state["user"]["user_id"])
                        st.rerun()

# ==========================================
# 25. تبويب الفواتير
# ==========================================
if "🧾 الفواتير والمبيعات" in tabs_titles:
    tab_idx = tabs_titles.index("🧾 الفواتير والمبيعات")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">🧾 نظام الفواتير والخصم التلقائي</div>', unsafe_allow_html=True)
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            customer = st.text_input("اسم العميل:", "مزرعة الإنتاج")
        with col_c2:
            quantity = st.number_input("الكمية (طن):", min_value=0.1, value=1.0, step=0.5)
        with col_c3:
            profit_margin = st.number_input("هامش الربح ($/طن):", min_value=0.0, value=50.0)
        
        selling_price = st.session_state["computed_ton_cost"] + profit_margin
        total = selling_price * quantity
        
        st.markdown("### 🧾 فاتورة البيع")
        col_inv1, col_inv2 = st.columns(2)
        with col_inv1:
            st.markdown(f"""
            <div class="price-card">
                <h4>تفاصيل الفاتورة</h4>
                <p>العميل: <b>{customer}</b></p>
                <p>الكمية: <b>{quantity} طن</b></p>
                <p>سعر الطن: <b>${selling_price:.2f}</b></p>
                <p style="font-size:1.2rem;color:#1b5e20;">الإجمالي: <b>${total:.2f}</b></p>
            </div>
            """, unsafe_allow_html=True)
        with col_inv2:
            st.markdown("#### المكونات المطلوبة:")
            if st.session_state["active_formula"]:
                for ing, pct in st.session_state["active_formula"].items():
                    qty_req = (pct / 100) * quantity
                    st.markdown(f"▪️ {ing}: **{qty_req:.2f}** طن")
        
        if st.session_state["user_role"] == "owner":
            if st.button("✅ تأكيد البيع وخصم المخزون", type="primary", use_container_width=True):
                can_deduct = True
                for ing, pct in st.session_state["active_formula"].items():
                    qty_req = (pct / 100) * quantity
                    inv = InventoryManager.get_inventory()
                    if ing not in inv or inv[ing]["quantity"] < qty_req:
                        can_deduct = False
                        st.error(f"❌ رصيد غير كافي: {ing}")
                        break
                
                if can_deduct:
                    for ing, pct in st.session_state["active_formula"].items():
                        qty_req = (pct / 100) * quantity
                        InventoryManager.deduct_stock(ing, qty_req, st.session_state["user"]["user_id"])
                    st.success("✅ تم الخصم التلقائي وإتمام البيع بنجاح!")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()

# ==========================================
# 26. تبويب مصمم الديباجة
# ==========================================
if "🖨️ مصمم الديباجة" in tabs_titles:
    tab_idx = tabs_titles.index("🖨️ مصمم الديباجة")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">👑 مصمم ديباجات الأعلاف</div>', unsafe_allow_html=True)
        
        brand = st.text_input("العلامة التجارية:", "منصة تاور العلمية")
        
        st.markdown(f"""
        <div class="sack-tag">
            <h2 style="color:#1b5e20;">🌟 {brand} 🌟</h2>
            <h3 style="color:#c62828;">الاختصاصي م. عبد القادر إسماعيل تاور</h3>
            <p style="background:#e8f5e9;padding:10px;border-radius:8px;">
                🎯 {st.session_state.get('active_stage_title', 'خلطة متوازنة')} | 
                DP: {st.session_state.get('active_cp_tag', 12):.1f}% | 
                SE: {st.session_state.get('active_se_tag', 65):.1f} وحدة
            </p>
            <small>تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d')}</small>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 27. تبويب التحليلات المتقدمة
# ==========================================
if "📈 التحليلات المتقدمة" in tabs_titles:
    tab_idx = tabs_titles.index("📈 التحليلات المتقدمة")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">📈 لوحة التحليلات المتقدمة</div>', unsafe_allow_html=True)
        
        # مؤشرات الأداء
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color:#1b5e20;">الخلطات</h3>
                <h2 style="color:#2e7d32;">1,247</h2>
                <p>تم توليدها</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color:#1565C0;">متوسط التكلفة</h3>
                <h2 style="color:#1976D2;">$285</h2>
                <p>للطن</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color:#E65100;">التوفير</h3>
                <h2 style="color:#F57C00;">18%</h2>
                <p>مقارنة بالتقليدي</p>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color:#2E7D32;">رضا العملاء</h3>
                <h2 style="color:#388E3C;">96%</h2>
                <p>تقييم إيجابي</p>
            </div>
            """, unsafe_allow_html=True)
        
        # الرسوم البيانية
        st.markdown("---")
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("📊 توزيع المواد")
            usage = pd.DataFrame({
                'المادة': ['ذرة', 'صويا', 'نخالة', 'أملاح', 'أخرى'],
                'النسبة': [45, 25, 15, 10, 5]
            })
            fig = px.pie(usage, values='النسبة', names='المادة', color_discrete_sequence=px.colors.sequential.Greens)
            st.plotly_chart(fig, use_container_width=True)
        
        with col_chart2:
            st.subheader("📈 اتجاه الأسعار")
            dates = pd.date_range(start='2024-01-01', periods=12, freq='ME')
            data = pd.DataFrame({
                'التاريخ': dates,
                'الذرة': [220, 225, 230, 228, 235, 240, 238, 242, 245, 248, 250, 252],
                'الصويا': [440, 445, 442, 448, 450, 455, 452, 458, 460, 462, 465, 468]
            })
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data['التاريخ'], y=data['الذرة'], mode='lines+markers', name='الذرة'))
            fig.add_trace(go.Scatter(x=data['التاريخ'], y=data['الصويا'], mode='lines+markers', name='الصويا'))
            fig.update_layout(title='اتجاه الأسعار')
            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 28. تبويب إدارة مزارع الدجاج (خاص بالمالك)
# ==========================================
if "🐔 إدارة مزارع الدجاج" in tabs_titles:
    tab_idx = tabs_titles.index("🐔 إدارة مزارع الدجاج")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج اللاحم</div>', unsafe_allow_html=True)
        
        if st.session_state["user_role"] != "owner":
            st.warning("⚠️ هذه الصلاحية متاحة للمالك فقط.")
        else:
            # إضافة مزرعة جديدة
            with st.expander("➕ إضافة مزرعة جديدة", expanded=False):
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    new_farm_name = st.text_input("اسم المزرعة")
                with col_f2:
                    new_owner_name = st.text_input("اسم المالك")
                with col_f3:
                    new_phone = st.text_input("رقم الواتساب", WHATSAPP_NUMBER)
                
                if st.button("💾 حفظ المزرعة"):
                    if new_farm_name:
                        farm_data = {
                            "farm_name": new_farm_name,
                            "owner_name": new_owner_name,
                            "owner_phone": new_phone,
                            "location": "",
                            "animal_type": "دواجن لاحم",
                            "capacity": 0,
                            "created_by": st.session_state["user"]["user_id"]
                        }
                        BroilerFarmManager.save_farm(farm_data)
                        st.success("تمت إضافة المزرعة بنجاح!")
                        st.rerun()
            
            # عرض المزارع
            farms = BroilerFarmManager.get_farms()
            if farms:
                farm_names = [f["farm_name"] for f in farms]
                selected_farm = st.selectbox("اختر مزرعة:", [""] + farm_names)
                
                if selected_farm:
                    farm = next((f for f in farms if f["farm_name"] == selected_farm), None)
                    if farm:
                        st.markdown(f"### 🏷️ {farm['farm_name']} - {farm['owner_name']}")
                        
                        # بيانات اليوم
                        st.markdown("#### 📝 إدخال بيانات اليوم")
                        col_d1, col_d2, col_d3 = st.columns(3)
                        with col_d1:
                            age = st.number_input("العمر (يوم)", min_value=1, value=1, step=1)
                            birds = st.number_input("عدد الطيور", min_value=1, value=100, step=100)
                        with col_d2:
                            weight = st.number_input("متوسط الوزن (كجم)", min_value=0.0, value=0.045, step=0.01)
                            feed = st.number_input("العلف المستهلك (كجم)", min_value=0.0, value=0.0, step=10.0)
                        with col_d3:
                            dead = st.number_input("النافق", min_value=0, value=0, step=1)
                            culled = st.number_input("المستبعد", min_value=0, value=0, step=1)
                        
                        # الحسابات
                        init_weight = 0.045
                        total_alive = birds - dead - culled
                        total_gain = total_alive * (weight - init_weight)
                        adg = BroilerFarmManager.calculate_adg(weight*1000, init_weight*1000, age)
                        fcr = BroilerFarmManager.calculate_fcr(feed, total_gain) if total_gain > 0 else 0
                        mortality = BroilerFarmManager.calculate_mortality_rate(dead, birds)
                        livability = BroilerFarmManager.calculate_livability(birds, dead)
                        epef = BroilerFarmManager.calculate_epef(livability, weight, age, fcr)
                        
                        # عرض المؤشرات
                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                        with col_m1:
                            st.metric("ADG (جم)", f"{adg:.1f}")
                        with col_m2:
                            st.metric("FCR", f"{fcr:.2f}")
                        with col_m3:
                            st.metric("النفوق (%)", f"{mortality:.2f}%")
                        with col_m4:
                            st.metric("EPEF", f"{epef:.0f}")
                        
                        # حفظ اليوم
                        if st.button("💾 حفظ بيانات اليوم"):
                            log_data = {
                                "farm_id": farm["farm_id"],
                                "age_days": age,
                                "avg_weight_kg": weight,
                                "feed_consumed_kg": feed,
                                "dead_birds": dead,
                                "culled_birds": culled,
                                "notes": ""
                            }
                            BroilerFarmManager.save_daily_log(log_data)
                            st.success("تم حفظ بيانات اليوم!")
                            st.rerun()
                        
                        # عرض السجلات السابقة
                        with st.expander("📜 السجلات السابقة"):
                            logs = BroilerFarmManager.get_daily_logs(farm["farm_id"])
                            if logs:
                                st.dataframe(pd.DataFrame(logs), use_container_width=True)
            else:
                st.info("👈 يرجى إضافة مزرعة جديدة")

# ==========================================
# 29. تبويب تعليقات المختصين
# ==========================================
if "💬 تعليقات المختصين" in tabs_titles:
    tab_idx = tabs_titles.index("💬 تعليقات المختصين")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">💬 قناة التواصل والتعليقات</div>', unsafe_allow_html=True)
        
        if "shared_comments" not in st.session_state:
            st.session_state["shared_comments"] = "• مرحباً بكم في قناة التواصل الفنية\n• يرجى إضافة ملاحظاتكم وخبراتكم"
        
        st.text_area("التعليقات:", value=st.session_state["shared_comments"], height=300)
        new_comment = st.text_area("إضافة تعليق جديد:")
        if st.button("➕ إضافة تعليق") and new_comment:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            user_name = st.session_state["user"]["full_name"]
            st.session_state["shared_comments"] += f"\n• [{timestamp}] {user_name}: {new_comment}"
            st.success("تمت الإضافة!")
            st.rerun()

# ==========================================
# 30. تبويب المراجع العلمية
# ==========================================
if "📚 المراجع العلمية" in tabs_titles:
    tab_idx = tabs_titles.index("📚 المراجع العلمية")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
        
        # عرض المراجع
        for category, cat_data in ScientificReferenceSystem.REFERENCES.items():
            with st.expander(f"📖 {cat_data['title']}"):
                for ref in cat_data["references"]:
                    st.markdown(f"""
                    <div style="background:#f5f5f5;padding:10px;border-radius:8px;margin:5px 0;">
                        <b>{ref['id']}</b> - {ref['authors']} ({ref['year']})
                        <br><i>{ref['title']}</i>
                        <br><small>{ref.get('summary', '')}</small>
                    </div>
                    """, unsafe_allow_html=True)

# ==========================================
# 31. تبويب المساعدة الذكية
# ==========================================
if "💡 المساعدة الذكية" in tabs_titles:
    tab_idx = tabs_titles.index("💡 المساعدة الذكية")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">💡 المساعدة الذكية</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### الأسئلة الشائعة
        اكتب سؤالك عن تغذية الحيوان وتركيب الأعلاف، وسنقدم لك الإجابة مع المرجع العلمي.
        """)
        
        question = st.text_input("❓ سؤالك:")
        if question:
            answer = ScientificReferenceSystem.get_knowledge_answer(question)
            if answer:
                st.markdown(f"""
                <div style="background:#e8f5e9;padding:15px;border-radius:8px;margin-top:10px;">
                    <h4>📝 الإجابة:</h4>
                    <p>{answer['answer']}</p>
                    <p><small>📌 المبسط: {answer['simplified']}</small></p>
                    {f'<p><small>📚 المرجع: {answer["reference"]["id"]} - {answer["reference"]["title"]}</small></p>' if answer.get('reference') else ''}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("💡 لم أجد إجابة لهذا السؤال. يرجى التواصل مع المختصين.")

# ==========================================
# 32. تبويب دليل المستخدم
# ==========================================
if "📖 دليل المستخدم" in tabs_titles:
    tab_idx = tabs_titles.index("📖 دليل المستخدم")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 🎯 دليل استخدام منصة تاور العلمية
        
        #### 1. تركيب الأعلاف
        - حدد موقعك الجغرافي لضبط الأسعار
        - اختر نوع الحيوان ومرحلة الإنتاج
        - حدد البروتين المهضوم ومعادل النشاء المطلوبين
        - اختر المواد العلفية المتاحة
        - اضغط "تشغيل محرك الاستمثال" للحصول على أقل تكلفة
        
        #### 2. إدارة المخزون
        - راقب الكميات المتاحة
        - أضف مواد جديدة أو حدّث الكميات
        - راقب التحذيرات عند نقص المخزون
        
        #### 3. الفواتير
        - أنشئ فاتورة بيع للعميل
        - يتم خصم المكونات تلقائياً من المخزون
        
        #### 4. مزارع الدجاج (خاص بالمالك)
        - أضف مزارع جديدة
        - سجّل البيانات اليومية (الوزن، العلف، النافق)
        - احصل على مؤشرات الأداء (ADG, FCR, EPEF)
        
        #### 5. التقارير
        - حمل تقرير PDF للخلطة
        - شارك النتائج عبر واتساب
        """)

# ==========================================
# 33. تبويب إعدادات النظام (خاص بالمالك)
# ==========================================
if "⚙️ إعدادات النظام" in tabs_titles:
    tab_idx = tabs_titles.index("⚙️ إعدادات النظام")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">⚙️ إعدادات النظام</div>', unsafe_allow_html=True)
        
        if st.session_state["user_role"] != "owner":
            st.warning("⚠️ هذه الصلاحية متاحة للمالك فقط.")
        else:
            st.subheader("📦 النسخ الاحتياطي")
            db = DatabaseManager()
            
            col_backup, col_restore = st.columns(2)
            with col_backup:
                if st.button("📥 إنشاء نسخة احتياطية", use_container_width=True):
                    backup_data = db.backup_database()
                    st.download_button("⬇️ تحميل النسخة الاحتياطية", backup_data,
                                     file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                     mime="application/zip")
            
            with col_restore:
                uploaded_file = st.file_uploader("📤 استعادة نسخة احتياطية", type=["zip"])
                if uploaded_file:
                    if st.button("⚠️ استعادة (سيتم استبدال البيانات)", use_container_width=True):
                        if db.restore_database(uploaded_file.getvalue()):
                            st.success("✅ تمت الاستعادة بنجاح! يرجى إعادة تشغيل التطبيق.")
                            st.rerun()
                        else:
                            st.error("❌ فشلت الاستعادة")
            
            st.subheader("👤 إدارة المستخدمين")
            auth = AuthManager()
            
            col_user1, col_user2 = st.columns(2)
            with col_user1:
                st.markdown("#### إضافة مستخدم جديد")
                new_user = st.text_input("اسم المستخدم")
                new_pass = st.text_input("كلمة المرور", type="password")
                new_role = st.selectbox("الصلاحية", ["breeder", "specialist"])
                new_full = st.text_input("الاسم الكامل")
                new_email = st.text_input("البريد الإلكتروني")
                new_phone = st.text_input("رقم الهاتف")
                
                if st.button("➕ إضافة مستخدم") and new_user and new_pass:
                    auth.create_user(new_user, new_pass, new_role, new_full, new_email, new_phone)
                    st.success("تم إضافة المستخدم بنجاح!")
                    st.rerun()

# ==========================================
# 34. التذييل (Footer)
# ==========================================
st.markdown("""
<hr>
<div style="text-align:center;color:#666;font-size:0.9rem;padding:20px 0;">
    🌾 منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف © 2026
    <br>
    تحت إشراف الاختصاصي م. عبد القادر إسماعيل تاور
    <br>
    <small>جميع الحقوق محفوظة - نسخة 3.0</small>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # إغلاق main-box

# ==========================================
# 35. التوقيع الثابت في الزاوية
# ==========================================
st.markdown("""
<div class="mini-left-signature">
    🌾 الاختصاصي م. عبد القادر إسماعيل تاور
</div>
""", unsafe_allow_html=True)

# ==========================================
# نهاية الكود
# ==========================================
