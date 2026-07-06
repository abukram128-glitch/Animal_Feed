"""
منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف
النسخة المتكاملة الكاملة v3.1 - تم تصحيح جميع الأخطاء
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
import sys
from functools import lru_cache
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import warnings
import io
import random
import string
import csv
import pickle
import zipfile
from io import BytesIO
import tempfile
import shutil

# ==========================================
# 0.1 معالجة استثناءات المكتبات الاختيارية
# ==========================================
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    # استخدام SHA256 كبديل مؤقت
    import hashlib

try:
    from itsdangerous import URLSafeTimedSerializer
    ITS_DANGEROUS_AVAILABLE = True
except ImportError:
    ITS_DANGEROUS_AVAILABLE = False

try:
    from scipy.optimize import linprog
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import altair as alt
    ALTAIR_AVAILABLE = True
except ImportError:
    ALTAIR_AVAILABLE = False

try:
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
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import arabic_reshaper
    ARABIC_RESHAPER_AVAILABLE = True
except ImportError:
    ARABIC_RESHAPER_AVAILABLE = False

try:
    from bidi.algorithm import get_display
    BIDI_AVAILABLE = True
except ImportError:
    BIDI_AVAILABLE = False

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    import matplotlib.font_manager as fm
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

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
    # القيم الافتراضية للاختبار المحلي
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
# 2. معالجة النصوص العربية (مع Fallback)
# ==========================================
class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=2000)
    def fix_arabic_text(text: str) -> str:
        try:
            if ARABIC_RESHAPER_AVAILABLE and BIDI_AVAILABLE:
                reshaped = arabic_reshaper.reshape(str(text))
                bidi = get_display(reshaped)
                return bidi
            else:
                return str(text)
        except:
            return str(text)

arabic_processor = ArabicTextProcessor()

# ==========================================
# 3. نظام إدارة قواعد البيانات
# ==========================================
class DatabaseManager:
    """مدير قاعدة البيانات المتكامل"""
    
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
        
        conn.commit()
        conn.close()
    
    def _initialize_default_data(self):
        """تهيئة البيانات الافتراضية"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # إعدادات النظام الافتراضية
        default_settings = [
            ('backup_interval_hours', '24', 'الفاصل الزمني للنسخ الاحتياطي بالساعات'),
            ('default_currency', 'USD', 'العملة الافتراضية'),
            ('default_profit_margin', '10', 'هامش الربح الافتراضي (%)'),
        ]
        for key, value, desc in default_settings:
            c.execute('INSERT OR IGNORE INTO system_settings (setting_key, setting_value, description, updated_date) VALUES (?, ?, ?, ?)',
                      (key, value, desc, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """تنفيذ استعلام مع حماية من SQL Injection"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            result = c.execute(query, params)
            conn.commit()
            data = result.fetchall()
            conn.close()
            return data
        except Exception as e:
            st.error(f"خطأ في قاعدة البيانات: {e}")
            return []
    
    def insert_record(self, table: str, data: dict) -> None:
        """إدراج سجل مع تنظيف أسماء الأعمدة"""
        try:
            columns = ', '.join([f'"{col}"' for col in data.keys()])
            placeholders = ', '.join(['?' for _ in data])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(query, list(data.values()))
            conn.commit()
            conn.close()
        except Exception as e:
            st.error(f"خطأ في إدراج السجل: {e}")
    
    def update_record(self, table: str, data: dict, condition: str, condition_params: tuple) -> None:
        """تحديث سجل مع شرط"""
        try:
            set_clause = ', '.join([f'"{k}" = ?' for k in data.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(query, list(data.values()) + list(condition_params))
            conn.commit()
            conn.close()
        except Exception as e:
            st.error(f"خطأ في تحديث السجل: {e}")
    
    def get_record(self, table: str, condition: str, params: tuple) -> Optional[tuple]:
        """استرجاع سجل واحد"""
        try:
            query = f"SELECT * FROM {table} WHERE {condition}"
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            result = c.execute(query, params).fetchone()
            conn.close()
            return result
        except:
            return None
    
    def get_inventory(self) -> dict:
        """استرجاع جميع عناصر المخزون"""
        try:
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
        except:
            return {}
    
    def update_inventory(self, item_name: str, new_qty: float, user_id: str = "system") -> bool:
        """تحديث كمية عنصر في المخزون"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("UPDATE inventory_items SET quantity = ?, last_updated = ? WHERE item_name = ?",
                      (new_qty, datetime.now().isoformat(), item_name))
            self.log_audit(user_id, "UPDATE_INVENTORY", f"'{item_name}' quantity set to {new_qty}")
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def deduct_inventory(self, item_name: str, amount: float, user_id: str = "system") -> bool:
        """خصم كمية من المخزون مع التحقق من الكفاية"""
        try:
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
        except:
            return False
    
    def add_inventory_item(self, item_name: str, quantity: float = 0.0, min_threshold: float = 5.0,
                           unit: str = "طن", supplier: str = "غير محدد", purchase_price: float = 0.0,
                           expiry_date: str = None, batch: str = None) -> None:
        """إضافة عنصر جديد إلى المخزون"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''INSERT OR REPLACE INTO inventory_items 
                         (item_name, quantity, min_threshold, unit, supplier, purchase_price, expiry_date, batch_number, last_updated)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (item_name, quantity, min_threshold, unit, supplier, purchase_price, expiry_date, batch, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except:
            pass
    
    def log_audit(self, user_id: str, action: str, details: str, ip: str = "0.0.0.0") -> None:
        """تسجيل إجراء في سجل التدقيق"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            username = st.session_state.get("user", {}).get("username", "unknown")
            c.execute("INSERT INTO audit_log (user_id, username, action, details, ip_address, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                      (user_id, username, action, details, ip, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except:
            pass
    
    def get_audit_log(self, limit: int = 100, user_id: str = None) -> List[tuple]:
        """استرجاع سجل التدقيق"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            if user_id:
                c.execute("SELECT * FROM audit_log WHERE user_id = ? ORDER BY log_id DESC LIMIT ?", (user_id, limit))
            else:
                c.execute("SELECT * FROM audit_log ORDER BY log_id DESC LIMIT ?", (limit,))
            data = c.fetchall()
            conn.close()
            return data
        except:
            return []
    
    def backup_database(self) -> bytes:
        """إنشاء نسخة احتياطية مضغوطة"""
        try:
            backup_buffer = BytesIO()
            with zipfile.ZipFile(backup_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(self.db_path, os.path.basename(self.db_path))
                meta = {
                    "backup_date": datetime.now().isoformat(),
                    "db_file": os.path.basename(self.db_path),
                    "version": "3.0"
                }
                zipf.writestr("metadata.json", json.dumps(meta, ensure_ascii=False))
            backup_buffer.seek(0)
            return backup_buffer.getvalue()
        except:
            return b""
    
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
        except:
            return False
    
    def save_production_cycle(self, cycle_data: dict) -> str:
        """حفظ دورة إنتاج جديدة"""
        try:
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
        except:
            return ""
    
    def get_production_cycles(self, farm_name: str = None) -> List[dict]:
        """استرجاع دورات الإنتاج"""
        try:
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
        except:
            return []
    
    def save_farm(self, farm_data: dict) -> str:
        """حفظ مزرعة جديدة"""
        try:
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
        except:
            return ""
    
    def get_farms(self) -> List[dict]:
        """استرجاع جميع المزارع"""
        try:
            rows = self.execute_query("SELECT * FROM farms ORDER BY created_date DESC")
            return [
                {
                    'farm_id': r[0], 'farm_name': r[1], 'owner_name': r[2],
                    'owner_phone': r[3], 'location': r[4], 'animal_type': r[5],
                    'capacity': r[6], 'created_date': r[7], 'created_by': r[8]
                } for r in rows
            ]
        except:
            return []
    
    def save_daily_log(self, log_data: dict) -> int:
        """حفظ سجل يومي لمزرعة"""
        try:
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
            return 1
        except:
            return 0
    
    def get_daily_logs(self, farm_id: str) -> List[dict]:
        """استرجاع السجلات اليومية لمزرعة"""
        try:
            rows = self.execute_query("SELECT * FROM farm_daily_logs WHERE farm_id = ? ORDER BY date DESC", (farm_id,))
            return [
                {
                    'log_id': r[0], 'farm_id': r[1], 'date': r[2], 'age_days': r[3],
                    'avg_weight_kg': r[4], 'feed_consumed_kg': r[5], 'dead_birds': r[6],
                    'culled_birds': r[7], 'temperature_c': r[8], 'humidity_percent': r[9],
                    'ventilation_status': r[10], 'litter_quality': r[11], 'notes': r[12]
                } for r in rows
            ]
        except:
            return []

# ==========================================
# 4. نظام المصادقة
# ==========================================
class AuthManager:
    """نظام إدارة المصادقة"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self._create_default_admin()
    
    def _hash_password(self, password: str) -> str:
        """تشفير كلمة المرور"""
        if BCRYPT_AVAILABLE:
            try:
                salt = bcrypt.gensalt(rounds=12)
                return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            except:
                pass
        # Fallback إلى SHA256
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """التحقق من كلمة المرور"""
        if BCRYPT_AVAILABLE:
            try:
                return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
            except:
                pass
        # Fallback إلى SHA256
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    def _create_default_admin(self):
        """إنشاء مستخدم admin افتراضي"""
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
        return user_id
    
    def authenticate(self, username: str, password: str, ip: str = "0.0.0.0") -> Optional[dict]:
        """مصادقة المستخدم"""
        users = self.db.execute_query("SELECT * FROM users WHERE username=? AND is_active=1", (username,))
        if users:
            user = users[0]
            if self._verify_password(password, user[2]):
                self.db.update_record('users', {'last_login': datetime.now().isoformat()}, 'user_id = ?', (user[0],))
                return {
                    'user_id': user[0],
                    'username': user[1],
                    'role': user[3],
                    'full_name': user[4],
                    'email': user[5],
                    'phone': user[6]
                }
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
        return True

# ==========================================
# 5. مكتبة الأعلاف الكاملة
# ==========================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة الكبرى": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3, "Lys": 0.25, "Met": 0.18, "Thr": 0.30},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4, "Lys": 0.26, "Met": 0.17, "Thr": 0.31},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5, "Lys": 0.40, "Met": 0.20, "Thr": 0.35},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8, "Lys": 0.22, "Met": 0.16, "Thr": 0.28},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6, "Lys": 0.35, "Met": 0.20, "Thr": 0.33},
        "جريش أرز رزاز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2, "Lys": 0.20, "Met": 0.15, "Thr": 0.25},
        "دخن محلي غزير": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2, "Lys": 0.30, "Met": 0.18, "Thr": 0.29},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0, "Lys": 0.42, "Met": 0.21, "Thr": 0.36}
    },
    "🌱 الأكساب وأمبازات مصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5, "Lys": 1.6, "Met": 0.5, "Thr": 1.2},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0, "Lys": 2.8, "Met": 0.7, "Thr": 1.8},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2, "Lys": 3.0, "Met": 0.75, "Thr": 1.9},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5, "Lys": 1.4, "Met": 0.6, "Thr": 1.1},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5, "Lys": 1.5, "Met": 0.5, "Thr": 1.2},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 9.5, "EE": 2.8, "ASH": 5.8, "Lys": 1.2, "Met": 0.6, "Thr": 1.0},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5, "Lys": 1.3, "Met": 0.6, "Thr": 1.1},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5, "Lys": 1.2, "Met": 2.0, "Thr": 1.8},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5, "Lys": 0.6, "Met": 0.3, "Thr": 0.5}
    },
    "🚜 المخلفات الزراعية والصناعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5, "Lys": 0.6, "Met": 0.2, "Thr": 0.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5, "Lys": 0.8, "Met": 0.3, "Thr": 0.7},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5, "Lys": 0.1, "Met": 0.05, "Thr": 0.1},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5, "Lys": 0.1, "Met": 0.05, "Thr": 0.1},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5, "Lys": 0.2, "Met": 0.1, "Thr": 0.2},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5, "Lys": 0.1, "Met": 0.05, "Thr": 0.1}
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5, "Lys": 4.5, "Met": 1.8, "Thr": 2.6},
        "مسحوق أسماك فاخر (72%)": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5, "Lys": 5.2, "Met": 2.2, "Thr": 3.0},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5, "Lys": 3.5, "Met": 1.0, "Thr": 2.0},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5, "Lys": 2.8, "Met": 1.2, "Thr": 1.8},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5, "Lys": 2.2, "Met": 0.9, "Thr": 1.5}
    },
    "🧪 الأحماض الأمينية البلورية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Lys": 94.0, "Met": 0.0, "Thr": 0.0},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3, "Lys": 0.0, "Met": 58.0, "Thr": 0.0},
        "ثريونين نقي (L-Threonine)": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Lys": 0.0, "Met": 0.0, "Thr": 72.0},
        "تريبتوفان نقي (L-Tryptophan)": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "فالين نقي (L-Valine)": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Lys": 0.0, "Met": 0.0, "Thr": 0.0}
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "بريمكس بياض وبشاير": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0, "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0, "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "كبريتات الحديدوز (معادل الجوسيبول)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0, "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "مستخلص الخمائر والجدر الخلوية (MOS)": {"CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5, "EE": 1.5, "ASH": 8.5, "Lys": 0.5, "Met": 0.2, "Thr": 0.4}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5, "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9, "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "أكسيد المغنيسيوم العلفي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Lys": 0.0, "Met": 0.0, "Thr": 0.0},
        "يوريا علفية محصنة (المجترات فقط)": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0, "Lys": 0.0, "Met": 0.0, "Thr": 0.0}
    }
}

# ==========================================
# 6. دوال الطاقة المتقدمة
# ==========================================
def calculate_me(cp: float, ee: float, nfe: float) -> float:
    """حساب الطاقة الأيضية (ME) للدواجن"""
    return (cp * 0.155) + (ee * 0.355) + (nfe * 0.155)

def calculate_ne_milk(cp: float, ee: float, ndf: float, se: float) -> float:
    """حساب صافي الطاقة للحليب (NEl) للمجترات"""
    return 0.6 * se - 0.2 * ndf + 0.1 * cp

def calculate_ne_gain(cp: float, ee: float, ndf: float, se: float) -> float:
    """حساب صافي الطاقة للتسمين (NEg) للمجترات"""
    return 0.5 * se - 0.3 * ndf + 0.05 * cp

# ==========================================
# 7. نظام إدارة المخزون
# ==========================================
class InventoryManager:
    db = DatabaseManager()
    
    @classmethod
    def get_inventory(cls) -> dict:
        return cls.db.get_inventory()
    
    @classmethod
    def check_stock_levels(cls) -> Dict[str, str]:
        inventory = cls.get_inventory()
        warnings = {}
        for item, data in inventory.items():
            qty = data.get("quantity", 0)
            threshold = data.get("min_threshold", 5.0)
            if qty <= 0:
                warnings[item] = "نفذ المخزون"
            elif qty < threshold:
                warnings[item] = "منخفض"
        return warnings
    
    @classmethod
    def update_stock(cls, item: str, qty: float, user_id: str = "system") -> bool:
        return cls.db.update_inventory(item, qty, user_id)
    
    @classmethod
    def deduct_stock(cls, item: str, amount: float, user_id: str = "system") -> bool:
        return cls.db.deduct_inventory(item, amount, user_id)
    
    @classmethod
    def add_item(cls, item_name: str, quantity: float = 0.0, min_threshold: float = 5.0,
                 unit: str = "طن", supplier: str = "غير محدد", purchase_price: float = 0.0) -> None:
        cls.db.add_inventory_item(item_name, quantity, min_threshold, unit, supplier, purchase_price)

# ==========================================
# 8. نظام التنبؤ بالأسعار
# ==========================================
class PricePredictor:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_ingredient_prices(self, ingredient_name: str, days: int = 30) -> List[dict]:
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
    
    def predict_price(self, ingredient_name: str, days_ahead: int = 7) -> dict:
        prices = self.get_ingredient_prices(ingredient_name, 30)
        if len(prices) < 5:
            return {'prediction': None, 'confidence': 0}
        
        price_list = [p['price'] for p in prices]
        weights = np.array(range(1, len(price_list) + 1))
        weighted_avg = np.average(price_list, weights=weights)
        trend = (price_list[0] - price_list[-1]) / len(price_list) if len(price_list) > 1 else 0
        prediction = weighted_avg + (trend * days_ahead)
        
        return {
            'prediction': max(0, prediction),
            'confidence': min(1, len(price_list) / 30),
            'current_price': price_list[0] if price_list else None,
            'trend': 'up' if trend > 0 else 'down' if trend < 0 else 'stable'
        }

# ==========================================
# 9. نظام إدارة مزارع الدجاج
# ==========================================
class BroilerFarmManager:
    db = DatabaseManager()
    
    @staticmethod
    def calculate_adg(current_weight_g: float, initial_weight_g: float, age_days: int) -> float:
        if age_days <= 0:
            return 0.0
        return (current_weight_g - initial_weight_g) / age_days
    
    @staticmethod
    def calculate_fcr(total_feed_kg: float, total_weight_gain_kg: float) -> float:
        if total_weight_gain_kg <= 0:
            return 0.0
        return total_feed_kg / total_weight_gain_kg
    
    @staticmethod
    def calculate_mortality_rate(dead_count: int, initial_count: int) -> float:
        if initial_count <= 0:
            return 0.0
        return (dead_count / initial_count) * 100.0
    
    @staticmethod
    def calculate_livability(initial_count: int, dead_count: int) -> float:
        return 100.0 - BroilerFarmManager.calculate_mortality_rate(dead_count, initial_count)
    
    @staticmethod
    def calculate_epef(livability: float, body_weight_kg: float, age_days: int, fcr: float) -> float:
        if age_days <= 0 or fcr <= 0:
            return 0.0
        return (livability * body_weight_kg) / (age_days * fcr) * 100.0
    
    @staticmethod
    def get_temp_humidity_table():
        data = {
            "العمر (يوم)": [1, 7, 14, 21, 28, 35, 42],
            "درجة الحرارة (مئوي)": [33, 30, 28, 26, 24, 22, 21],
            "الرطوبة النسبية (%)": [65, 65, 65, 60, 60, 55, 55]
        }
        return pd.DataFrame(data)
    
    @classmethod
    def save_cycle(cls, cycle_data: dict, user_id: str = "system") -> str:
        return cls.db.save_production_cycle(cycle_data)
    
    @classmethod
    def get_cycles(cls, farm_name: str = None) -> List[dict]:
        return cls.db.get_production_cycles(farm_name)
    
    @classmethod
    def save_farm(cls, farm_data: dict) -> str:
        return cls.db.save_farm(farm_data)
    
    @classmethod
    def get_farms(cls) -> List[dict]:
        return cls.db.get_farms()
    
    @classmethod
    def save_daily_log(cls, log_data: dict) -> int:
        return cls.db.save_daily_log(log_data)
    
    @classmethod
    def get_daily_logs(cls, farm_id: str) -> List[dict]:
        return cls.db.get_daily_logs(farm_id)

# ==========================================
# 10. مولد PDF (مع Fallback)
# ==========================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        if os.path.exists("Amiri-Regular.ttf") and REPORTLAB_AVAILABLE:
            try:
                pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
                self.font_name = 'Amiri'
            except:
                pass
    
    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, include_charts=True) -> bytes:
        if not REPORTLAB_AVAILABLE:
            # إرجاع ملف PDF بسيط
            return self._generate_simple_report(formula, target_dp, breed, cost, city)
        
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
            story = []
            
            def p(text, size=12, align=TA_RIGHT, color=HexColor('#000000')):
                safe_text = arabic_processor.fix_arabic_text(str(text))
                return Paragraph(safe_text, ParagraphStyle('style', fontName=self.font_name, fontSize=size, alignment=align, textColor=color, spaceAfter=6, leading=size*1.5))
            
            story.append(p("تقرير فني شامل - منصة تاور العلمية", size=22, align=TA_CENTER, color=HexColor('#1b5e20')))
            story.append(Spacer(1, 12))
            for line in [f"المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور", f"الموقع الجغرافي: {city}", f"الفصيل المستهدف: {breed}", f"تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"]:
                story.append(p(line, size=11))
            story.append(Spacer(1, 15))
            
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
            
            story.append(p("المقادير المعتمدة:", size=14, color=HexColor('#2e7d32')))
            story.append(Spacer(1, 10))
            ing_data = [[arabic_processor.fix_arabic_text('المكون'), arabic_processor.fix_arabic_text('النسبة %'), arabic_processor.fix_arabic_text('كجم/طن')]]
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
            
            story.append(Spacer(1, 25))
            story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026", size=9, align=TA_CENTER, color=HexColor('#666666')))
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
        except:
            return self._generate_simple_report(formula, target_dp, breed, cost, city)
    
    def _generate_simple_report(self, formula, target_dp, breed, cost, city) -> bytes:
        """توليد تقرير بسيط في حال تعذر استخدام ReportLab"""
        buffer = io.BytesIO()
        buffer.write(f"""
        ========================================
        تقرير فني - منصة تاور العلمية
        ========================================
        المشرف: م. عبد القادر إسماعيل تاور
        الفصيل: {breed}
        الموقع: {city}
        التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        
        البروتين المهضوم: {target_dp:.2f}%
        التكلفة للطن: ${cost:.2f}
        
        المكونات:
        """.encode('utf-8'))
        for ing, pct in formula.items():
            buffer.write(f"  {ing}: {pct:.2f}% ({pct*10:.1f} كجم)\n".encode('utf-8'))
        buffer.write(b"\n========================================\n")
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# ==========================================
# 11. نظام المراجع العلمية
# ==========================================
class ScientificReferenceSystem:
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان",
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
            "title": "البروتين والأحماض الأمينية",
            "references": [
                {"id": "REF003", "authors": "NRC (National Research Council)",
                 "year": 2012, "title": "Nutrient Requirements of Swine",
                 "publisher": "National Academies Press", "edition": "11th Revised Edition",
                 "isbn": "978-0309214230", "summary": "متطلبات الخنازير."},
                {"id": "REF004", "authors": "NRC (National Research Council)",
                 "year": 2001, "title": "Nutrient Requirements of Dairy Cattle",
                 "publisher": "National Academies Press", "edition": "7th Revised Edition",
                 "isbn": "978-0309069977", "summary": "متطلبات أبقار الحليب."}
            ]
        }
    }
    
    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً.",
            "reference": "REF003",
            "simplified": "البروتين الذي يستفيد منه الحيوان فعلياً."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء هو مقياس لكمية الطاقة التي يوفرها العلف.",
            "reference": "REF006",
            "simplified": "معادل النشاء يقيس كمية الطاقة في العلف."
        }
    }
    
    @staticmethod
    def get_reference(ref_id: str) -> Optional[dict]:
        for category in ScientificReferenceSystem.REFERENCES.values():
            for ref in category.get("references", []):
                if ref.get("id") == ref_id:
                    return ref
        return None
    
    @staticmethod
    def get_knowledge_answer(question: str) -> Optional[dict]:
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
# 12. دوال الإرسال
# ==========================================
def send_code_to_mail(receiver_email: str, attachment_type: str = "full") -> bool:
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = "🌾 السورس كود - منصة تاور العلمية"
        body = """السلام عليكم، مرفق الكود المصدري للمنصة."""
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        try:
            with open(__file__, "r", encoding="utf-8") as f:
                code_content = f.read()
        except:
            code_content = "# الكود غير متاح"
        
        attachment = MIMEText(code_content, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', filename="tower_scientific_platform.py")
        msg.attach(attachment)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ فشل الإرسال: {e}")
        return False

def send_whatsapp_alert(phone_number: str, message: str):
    encoded_msg = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_msg}"
    st.markdown(f"""
    <div style='background:#e8f5e9; padding:10px; border-radius:8px;'>
        📲 <b>واتساب:</b> <a href='{whatsapp_url}' target='_blank'>اضغط للإرسال</a>
        <br>{message}
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 13. دوال إضافية
# ==========================================
def load_city_prices() -> dict:
    if os.path.exists(CITY_PRICES_FILE):
        try:
            with open(CITY_PRICES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_city_prices(data: dict):
    try:
        with open(CITY_PRICES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

@st.cache_data(ttl=3600)
def get_image_base64(paths: List[str]) -> Optional[str]:
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode()
            except:
                pass
    return None

class MarketPriceEngine:
    @staticmethod
    @lru_cache(maxsize=128)
    def get_adjusted_market_data(country: str, state_or_region: str, city: str) -> Dict[str, float]:
        feed_prices = {}
        for cat in BIG_FEEDS_LIBRARY.values():
            for ing in cat:
                feed_prices[ing] = 250.0
        
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
        
        multiplier = 1.0
        if country == "السودان":
            multiplier = 1.15
        elif country == "LIBYA":
            multiplier = 1.10
        elif country == "مصر":
            multiplier = 1.04
        
        for k in feed_prices:
            feed_prices[k] *= multiplier
        
        city_key = f"{country}|||{state_or_region}|||{city}"
        custom_prices = load_city_prices().get(city_key, {})
        for k, v in custom_prices.items():
            if k in feed_prices:
                feed_prices[k] = v
        
        return feed_prices

# ==========================================
# 14. تكوين الصفحة
# ==========================================
st.set_page_config(
    page_title="منصة تاور العلمية",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 15. تهيئة حالة الجلسة
# ==========================================
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
if "broiler_farms" not in st.session_state:
    st.session_state["broiler_farms"] = {}
if "selected_farm" not in st.session_state:
    st.session_state["selected_farm"] = None
if "standard_vacc_schedule" not in st.session_state:
    st.session_state["standard_vacc_schedule"] = {
        1: {"type": "فيتامين", "name": "فيتامين AD3E", "dose": "1 مل/لتر ماء", "route": "مياه الشرب"},
        7: {"type": "لقاح", "name": "نيوكاسل (Lasota)", "dose": "قطرة عين", "route": "قطرة عين/أنف"},
        14: {"type": "لقاح", "name": "Gumboro", "dose": "قطرة فم", "route": "مياه الشرب"},
        21: {"type": "دواء", "name": "مضاد كوكسيديا", "dose": "1 جم/لتر", "route": "مياه الشرب"},
    }
if "whatsapp_alerts_sent" not in st.session_state:
    st.session_state["whatsapp_alerts_sent"] = {}
if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = "مرحباً بكم في قناة التواصل الفنية\n"

# ==========================================
# 16. CSS المخصص
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
* { font-family: 'Cairo', sans-serif; }
.main-box {
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
.section-title {
    color: #1b5e20;
    border-right: 6px solid #2e7d32;
    padding-right: 15px;
    font-size: 1.4rem;
    font-weight: bold;
    margin: 20px 0;
}
.formula-item {
    background: #f1f8e9;
    padding: 10px 15px;
    border-radius: 8px;
    margin-bottom: 6px;
    border-right: 4px solid #2e7d32;
}
.stock-critical { background: #ffebee; color: #c62828; padding: 3px 10px; border-radius: 5px; }
.stock-normal { background: #e8f5e9; color: #2e7d32; padding: 3px 10px; border-radius: 5px; }
.price-card { background: #f5f5f5; padding: 15px; border-radius: 10px; border-right: 4px solid #1565C0; }
.warning-card { background: #fff3e0; padding: 10px; border-radius: 8px; border-right: 4px solid #f57c00; }
.profile-img-style {
    width: 120px; height: 120px; border-radius: 50%; object-fit: cover;
    border: 4px solid #d4af37; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.sack-tag {
    border: 3px dashed #1b5e20; padding: 25px; border-radius: 15px;
    background: #f1f8e9; text-align: center;
}
.metric-card {
    background: white; padding: 15px; border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08); text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 17. بوابة الدخول
# ==========================================
if not st.session_state["approved"]:
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        if st.session_state["last_login_time"]:
            time_diff = (datetime.now() - st.session_state["last_login_time"]).seconds
            if time_diff < LOCKOUT_TIME:
                st.markdown(f'<div class="main-box" style="max-width:500px;margin:100px auto;text-align:center;">', unsafe_allow_html=True)
                st.error(f"🔒 تم قفل النظام. حاول بعد {LOCKOUT_TIME - time_diff} ثانية")
                st.markdown('</div>', unsafe_allow_html=True)
                st.stop()
            else:
                st.session_state["login_attempts"] = 0
    
    st.markdown('<div class="main-box" style="max-width:500px;margin:100px auto;text-align:center;">', unsafe_allow_html=True)
    st.markdown("<h1 style='color:#1b5e20;'>🌾 منصة تاور العلمية</h1>")
    st.markdown("<p>للانتاج الحيواني وتركيب الاعلاف</p>")
    
    login_option = st.radio("طريقة الدخول:", ["كود الدخول السري", "اسم المستخدم وكلمة المرور"], horizontal=True)
    
    if login_option == "كود الدخول السري":
        input_code = st.text_input("🔑 أدخل الكود:", type="password")
        if st.button("تسجيل الدخول", type="primary", use_container_width=True):
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
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ كود غير صحيح! متبقي {remaining} محاولات")
    else:
        username = st.text_input("👤 اسم المستخدم")
        password = st.text_input("🔑 كلمة المرور", type="password")
        if st.button("تسجيل الدخول", type="primary", use_container_width=True):
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
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ بيانات غير صحيحة! متبقي {remaining} محاولات")
        st.caption("💡 admin / admin123")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 18. الواجهة الرئيسية
# ==========================================
if not st.session_state["login_welcome_shown"]:
    st.toast("مرحباً بك في منصة تاور العلمية", icon="🌾")
    st.session_state["login_welcome_shown"] = True

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# رأس الصفحة
col_logo, col_title = st.columns([0.2, 0.8])
with col_logo:
    img_data = get_image_base64(PHOTO_OPTIONS)
    if img_data:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_data}" class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:4rem;text-align:center;">🌾</div>', unsafe_allow_html=True)

with col_title:
    st.markdown("""
    <h1 style="color:#1b5e20;">منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</h1>
    <p style="color:#1565C0;font-size:1.1rem;">محرك الاستمثال الخطي المتقدم</p>
    <h3 style="color:#c62828;">الاختصاصي م. عبد القادر إسماعيل تاور</h3>
    """, unsafe_allow_html=True)

# معلومات المستخدم
col_user, col_logout = st.columns([0.85, 0.15])
with col_user:
    role_names = {
        "owner": "👑 المالك - الاختصاصي م. عبد القادر إسماعيل تاور",
        "specialist": "🔬 مختص - طبيب بيطري / إنتاج حيواني",
        "breeder": "🌾 مربي"
    }
    st.markdown(f'<div style="background:#f5f5f5;padding:10px;border-radius:8px;text-align:right;">✅ {role_names.get(st.session_state["user_role"], "مستخدم")}</div>', unsafe_allow_html=True)
with col_logout:
    if st.button("🚪 خروج", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["inventory_cache", "broiler_farms"]:
                try:
                    del st.session_state[key]
                except:
                    pass
        st.session_state["approved"] = False
        st.rerun()

st.markdown("---")

# ==========================================
# 19. التبويبات
# ==========================================
if st.session_state["user_role"] == "owner":
    tabs_titles = ["🔬 تركيب الأعلاف", "📊 بورصة الأسعار", "🏭 المخزون", "🧾 الفواتير", "🖨️ الديباجة", "📈 التحليلات", "🐔 مزارع الدجاج", "💬 التعليقات", "📚 المراجع", "💡 المساعدة"]
elif st.session_state["user_role"] == "specialist":
    tabs_titles = ["🔬 تركيب الأعلاف", "📊 بورصة الأسعار", "🏭 المخزون", "🧾 الفواتير", "🖨️ الديباجة", "📈 التحليلات", "💬 التعليقات", "📚 المراجع", "💡 المساعدة"]
else:
    tabs_titles = ["🔬 تركيب الأعلاف", "📚 المراجع", "💡 المساعدة"]

tabs = st.tabs(tabs_titles)

# ==========================================
# 20. التبويب: تركيب الأعلاف
# ==========================================
with tabs[0]:
    st.markdown('<div class="section-title">🌍 تحديد الموقع وبورصة الأسعار</div>', unsafe_allow_html=True)
    
    col_country, col_state, col_city = st.columns(3)
    with col_country:
        user_country = st.selectbox("الدولة:", ["السودان", "LIBYA", "مصر", "باقي دول العالم"])
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    local_rate = c_info["rate"]
    local_sym = c_info["sym"]
    
    with col_state:
        if user_country == "السودان":
            chosen_state = st.selectbox("الولاية:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف"])
        elif user_country == "LIBYA":
            chosen_state = st.selectbox("المنطقة:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
        else:
            chosen_state = st.selectbox("الإقليم:", ["المركز الرئيسي", "الأسواق المفتوحة"])
    
    with col_city:
        user_city = st.text_input("المدينة:", "طبرق")
    
    live_prices = MarketPriceEngine.get_adjusted_market_data(user_country, chosen_state, user_city)
    
    # اختيار القطاع
    st.markdown('<div class="section-title">⚖️ اختيار القطاع والإنتاج</div>', unsafe_allow_html=True)
    col_sector, col_sub, col_stage = st.columns(3)
    with col_sector:
        main_sector = st.selectbox("القطاع:", ["الأغنام", "الماعز", "الأبقار", "الخيول", "الدواجن", "الأسماك"])
    with col_sub:
        if main_sector == "الأغنام":
            sub_type = st.selectbox("السلالة:", ["ضأن صحراوي", "بربري"])
        elif main_sector == "الماعز":
            sub_type = st.selectbox("السلالة:", ["نوبي", "صحراوي"])
        elif main_sector == "الأبقار":
            sub_type = st.selectbox("السلالة:", ["كنانة", "بطانة", "هولشتاين"])
        elif main_sector == "الدواجن":
            sub_type = st.selectbox("النوع:", ["لاحم", "بياض", "سمان"])
        else:
            sub_type = st.selectbox("النوع:", ["عام"])
    with col_stage:
        stages = {
            "الأغنام": ["تسمين", "حليب"],
            "الماعز": ["تسمين", "حليب"],
            "الأبقار": ["حليب", "تسمين"],
            "الدواجن": ["بادي", "نامي", "ناهي"],
            "الأسماك": ["نمو", "تسمين"]
        }
        prod_stage = st.selectbox("المرحلة:", stages.get(main_sector, ["عام"]))
    
    # حدود الموازنة
    st.markdown('<div class="section-title">📋 حدود الموازنة</div>', unsafe_allow_html=True)
    col_dp, col_se = st.columns(2)
    with col_dp:
        target_dp = st.slider("البروتين المهضوم (%)", 5.0, 40.0, 12.0, 0.5)
    with col_se:
        target_se = st.slider("معادل النشاء", 10.0, 90.0, 65.0, 1.0)
    
    # اختيار المكونات
    st.markdown("### 📦 المواد العلفية")
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
    if st.button("🚀 تشغيل المحرك", type="primary", use_container_width=True):
        if len(selected_ingredients) < 3 or not SCIPY_AVAILABLE:
            if not SCIPY_AVAILABLE:
                st.error("❌ مكتبة scipy غير مثبتة. يرجى تثبيتها: pip install scipy")
            else:
                st.error("❌ يرجى اختيار 3 مواد علفية على الأقل")
        else:
            try:
                c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
                bounds = [(mandatory_additives.get(ing, 0.0), mandatory_additives.get(ing, 100.0)) if ing in mandatory_additives else (0.0, 100.0) for ing in selected_ingredients]
                
                A_eq = [[1.0 for _ in selected_ingredients]]
                b_eq = [100.0]
                
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
                
                A_ub = [[-1.0 * x for x in se_row]]
                b_ub = [-1.0 * target_se * 100.0]
                
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
                    
                    col_res1, col_res2 = st.columns([0.6, 0.4])
                    with col_res1:
                        st.markdown("#### 📝 مكونات الخلطة (كجم/طن):")
                        for ing, pct in formula.items():
                            st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.2f}% ({pct*10:.1f} كجم)</div>', unsafe_allow_html=True)
                        
                        ton_cost = res.fun / 100.0
                        st.session_state["computed_ton_cost"] = ton_cost
                        st.metric(f"💰 تكلفة الطن:", f"${ton_cost:.2f} ({ton_cost*local_rate:,.2f} {local_sym})")
                        
                        try:
                            pdf_data = pdf_generator.generate_comprehensive_report(
                                formula, target_dp, sub_type, ton_cost, user_city,
                                ton_cost*local_rate, local_sym, computed_se
                            )
                            st.download_button("📥 تحميل PDF", pdf_data, file_name=f"خلطة_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf")
                        except Exception as e:
                            st.warning(f"⚠️ PDF: {e}")
                    
                    with col_res2:
                        if PLOTLY_AVAILABLE and len(formula) > 1:
                            fig = px.pie(values=list(formula.values()), names=list(formula.keys()), 
                                       title="توزيع المكونات", color_discrete_sequence=px.colors.sequential.Greens)
                            fig.update_layout(height=350)
                            st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("❌ تعذر إيجاد حل رياضي. يرجى إضافة مواد علفية أخرى.")
            except Exception as e:
                st.error(f"❌ خطأ في المحرك: {e}")

# ==========================================
# 21. التبويب: بورصة الأسعار
# ==========================================
if "📊 بورصة الأسعار" in tabs_titles:
    tab_idx = tabs_titles.index("📊 بورصة الأسعار")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">📊 بورصة الأسعار</div>', unsafe_allow_html=True)
        
        st.subheader("🐄 أسعار الماشية")
        livestock = {"عجول تسمين": 1350, "أبقار محلية": 900, "ضأن": 180, "ماعز": 130, "خيول": 4500}
        cols = st.columns(3)
        for idx, (item, price) in enumerate(livestock.items()):
            with cols[idx % 3]:
                st.metric(item, f"${price:.2f}")
        
        st.subheader("🥛 أسعار المنتجات")
        products = {"لحم بقري": 7.50, "لحم ضأن": 9.00, "لحم دجاج": 3.80, "بيض": 4.20, "حليب": 0.90}
        cols = st.columns(3)
        for idx, (item, price) in enumerate(products.items()):
            with cols[idx % 3]:
                st.metric(item, f"${price:.2f}")

# ==========================================
# 22. التبويب: المخزون
# ==========================================
if "🏭 المخزون" in tabs_titles:
    tab_idx = tabs_titles.index("🏭 المخزون")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">🏭 إدارة المخزون</div>', unsafe_allow_html=True)
        
        inventory = InventoryManager.get_inventory()
        stock_warnings = InventoryManager.check_stock_levels()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("إجمالي المواد", len(inventory))
        with col2: 
            critical = sum(1 for v in stock_warnings.values() if v == "نفذ المخزون")
            st.metric("نفذ", critical)
        with col3:
            low = sum(1 for v in stock_warnings.values() if v == "منخفض")
            st.metric("منخفض", low)
        with col4:
            st.metric("آمن", len(inventory) - critical - low)
        
        st.markdown("---")
        cols = st.columns(3)
        for idx, (item, data) in enumerate(list(inventory.items())[:30]):
            with cols[idx % 3]:
                qty = data.get("quantity", 0)
                threshold = data.get("min_threshold", 5.0)
                if qty <= 0:
                    status = f'<span class="stock-critical">⚠️ نفذ: {qty:.2f} طن</span>'
                elif qty < threshold:
                    status = f'<span class="stock-critical">⚠️ حرج: {qty:.2f} طن</span>'
                else:
                    status = f'<span class="stock-normal">✅ {qty:.2f} طن</span>'
                st.markdown(f"**{item}** | {status}", unsafe_allow_html=True)

# ==========================================
# 23. التبويب: الفواتير
# ==========================================
if "🧾 الفواتير" in tabs_titles:
    tab_idx = tabs_titles.index("🧾 الفواتير")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">🧾 نظام الفواتير</div>', unsafe_allow_html=True)
        
        customer = st.text_input("اسم العميل:", "مزرعة الإنتاج")
        quantity = st.number_input("الكمية (طن):", min_value=0.1, value=1.0, step=0.5)
        profit_margin = st.number_input("هامش الربح ($/طن):", min_value=0.0, value=50.0)
        
        selling_price = st.session_state["computed_ton_cost"] + profit_margin
        total = selling_price * quantity
        
        st.markdown("### 🧾 الفاتورة")
        st.markdown(f"""
        <div class="price-card">
            <p>العميل: <b>{customer}</b></p>
            <p>الكمية: <b>{quantity} طن</b></p>
            <p>سعر الطن: <b>${selling_price:.2f}</b></p>
            <p style="font-size:1.2rem;color:#1b5e20;">الإجمالي: <b>${total:.2f}</b></p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 24. التبويب: مصمم الديباجة
# ==========================================
if "🖨️ الديباجة" in tabs_titles:
    tab_idx = tabs_titles.index("🖨️ الديباجة")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">🖨️ مصمم الديباجة</div>', unsafe_allow_html=True)
        
        brand = st.text_input("العلامة التجارية:", "منصة تاور العلمية")
        st.markdown(f"""
        <div class="sack-tag">
            <h2 style="color:#1b5e20;">🌟 {brand} 🌟</h2>
            <h3 style="color:#c62828;">الاختصاصي م. عبد القادر إسماعيل تاور</h3>
            <p style="background:#e8f5e9;padding:10px;border-radius:8px;">
                DP: {st.session_state.get('active_cp_tag', 12):.1f}% | 
                SE: {st.session_state.get('active_se_tag', 65):.1f} وحدة
            </p>
            <small>{datetime.now().strftime('%Y-%m-%d')}</small>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 25. التبويب: التحليلات
# ==========================================
if "📈 التحليلات" in tabs_titles:
    tab_idx = tabs_titles.index("📈 التحليلات")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">📈 التحليلات</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.markdown('<div class="metric-card"><h3>الخلطات</h3><h2>1,247</h2></div>', unsafe_allow_html=True)
        with col2: st.markdown('<div class="metric-card"><h3>التكلفة</h3><h2>$285</h2></div>', unsafe_allow_html=True)
        with col3: st.markdown('<div class="metric-card"><h3>التوفير</h3><h2>18%</h2></div>', unsafe_allow_html=True)
        with col4: st.markdown('<div class="metric-card"><h3>الرضا</h3><h2>96%</h2></div>', unsafe_allow_html=True)

# ==========================================
# 26. التبويب: مزارع الدجاج
# ==========================================
if "🐔 مزارع الدجاج" in tabs_titles:
    tab_idx = tabs_titles.index("🐔 مزارع الدجاج")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">🐔 مزارع الدجاج</div>', unsafe_allow_html=True)
        
        if st.session_state["user_role"] != "owner":
            st.warning("⚠️ هذه الصلاحية للمالك فقط.")
        else:
            with st.expander("➕ إضافة مزرعة", expanded=False):
                farm_name = st.text_input("اسم المزرعة")
                owner_name = st.text_input("اسم المالك")
                if st.button("💾 حفظ") and farm_name:
                    farm_data = {"farm_name": farm_name, "owner_name": owner_name}
                    BroilerFarmManager.save_farm(farm_data)
                    st.success("تمت الإضافة!")
                    st.rerun()
            
            farms = BroilerFarmManager.get_farms()
            if farms:
                selected = st.selectbox("اختر مزرعة:", [f["farm_name"] for f in farms])
                farm = next((f for f in farms if f["farm_name"] == selected), None)
                if farm:
                    st.markdown(f"### 🏷️ {farm['farm_name']}")
                    
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        age = st.number_input("العمر (يوم)", min_value=1, value=1)
                        weight = st.number_input("الوزن (كجم)", min_value=0.0, value=0.045, step=0.01)
                    with col_d2:
                        feed = st.number_input("العلف (كجم)", min_value=0.0, value=0.0)
                        dead = st.number_input("النافق", min_value=0, value=0)
                    
                    if st.button("💾 حفظ اليوم"):
                        log_data = {
                            "farm_id": farm["farm_id"],
                            "age_days": age,
                            "avg_weight_kg": weight,
                            "feed_consumed_kg": feed,
                            "dead_birds": dead
                        }
                        BroilerFarmManager.save_daily_log(log_data)
                        st.success("تم حفظ اليوم!")
                        st.rerun()
            else:
                st.info("👈 أضف مزرعة جديدة")

# ==========================================
# 27. التبويب: التعليقات
# ==========================================
if "💬 التعليقات" in tabs_titles:
    tab_idx = tabs_titles.index("💬 التعليقات")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">💬 التعليقات</div>', unsafe_allow_html=True)
        st.text_area("التعليقات:", value=st.session_state["shared_comments"], height=200)
        new_comment = st.text_area("إضافة تعليق:")
        if st.button("➕ إضافة") and new_comment:
            st.session_state["shared_comments"] += f"\n• {datetime.now().strftime('%H:%M')} {st.session_state['user']['full_name']}: {new_comment}"
            st.rerun()

# ==========================================
# 28. التبويب: المراجع
# ==========================================
if "📚 المراجع" in tabs_titles:
    tab_idx = tabs_titles.index("📚 المراجع")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
        for category, cat_data in ScientificReferenceSystem.REFERENCES.items():
            with st.expander(f"📖 {cat_data['title']}"):
                for ref in cat_data["references"]:
                    st.markdown(f"""
                    <div style="background:#f5f5f5;padding:10px;border-radius:8px;margin:5px 0;">
                        <b>{ref['id']}</b> - {ref['authors']} ({ref['year']})
                        <br><i>{ref['title']}</i>
                    </div>
                    """, unsafe_allow_html=True)

# ==========================================
# 29. التبويب: المساعدة
# ==========================================
if "💡 المساعدة" in tabs_titles:
    tab_idx = tabs_titles.index("💡 المساعدة")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">💡 المساعدة</div>', unsafe_allow_html=True)
        question = st.text_input("❓ اسأل:")
        if question:
            answer = ScientificReferenceSystem.get_knowledge_answer(question)
            if answer:
                st.markdown(f"""
                <div style="background:#e8f5e9;padding:15px;border-radius:8px;">
                    <p>{answer['answer']}</p>
                    <small>{answer['simplified']}</small>
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# 30. التذييل
# ==========================================
st.markdown("""
<hr>
<div style="text-align:center;color:#666;padding:15px 0;">
    🌾 منصة تاور العلمية © 2026 | الاختصاصي م. عبد القادر إسماعيل تاور
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# نهاية الكود
# ==========================================
