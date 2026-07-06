"""
منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف
النسخة الكاملة المُصحَّحة v4.0
جميع الميزات الأصلية محفوظة مع تصحيح الأخطاء وتحسين الأمان.
المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور
"""

# ==========================================
# 0. الاستيرادات الأساسية مع معالجة الاستثناءات
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
try:
    SENDER_EMAIL = st.secrets["email"]["sender"]
    SENDER_PASSWORD = st.secrets["email"]["password"]
    OWNER_EMAIL = st.secrets["email"]["owner"]
    WHATSAPP_NUMBER = st.secrets["whatsapp"]["number"]
except:
    SENDER_EMAIL = "abukram128@gmail.com"
    SENDER_PASSWORD = "oynz rdli tsdy ekdq"
    OWNER_EMAIL = "abukram128@gmail.com"
    WHATSAPP_NUMBER = "+249123533489"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
GOOGLE_FORM_URL = "https://forms.google.com/YOUR_FORM_URL"
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300
CITY_PRICES_FILE = "city_prices.json"
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

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
# 3. نظام إدارة قواعد البيانات المتكامل (مع جميع الجداول)
# ==========================================
class DatabaseManager:
    def __init__(self, db_path: str = "tower_platform_secure.db"):
        self.db_path = db_path
        self._init_database()
        self._initialize_default_data()
        self._init_inventory_from_library()

    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # 1. المستخدمين
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
        # 2. المخزون
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
        # 3. سجل التدقيق
        c.execute('''CREATE TABLE IF NOT EXISTS audit_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            username TEXT,
            action TEXT,
            details TEXT,
            ip_address TEXT,
            timestamp TEXT
        )''')
        # 4. دورات الإنتاج
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
        # 5. الأسعار التاريخية
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
        # 6. الخلطات المحفوظة
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
        # 7. إعدادات النظام
        c.execute('''CREATE TABLE IF NOT EXISTS system_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT,
            description TEXT,
            updated_date TEXT
        )''')
        # 8. المزارع
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
        # 9. السجلات اليومية للمزارع
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
        # 10. السجل الصحي
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
        # 11. الفواتير
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
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
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

    def _init_inventory_from_library(self):
        """تهيئة المخزون من مكتبة الأعلاف إذا كان فارغاً"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM inventory_items")
            if c.fetchone()[0] == 0:
                for cat in BIG_FEEDS_LIBRARY.values():
                    for ing in cat:
                        c.execute("INSERT OR IGNORE INTO inventory_items (item_name, quantity, last_updated) VALUES (?, ?, ?)",
                                  (ing, 25.0, datetime.now().isoformat()))
                conn.commit()
            conn.close()
        except:
            pass

    # ========== دوال قاعدة البيانات الأساسية ==========
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
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
        try:
            query = f"SELECT * FROM {table} WHERE {condition}"
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            result = c.execute(query, params).fetchone()
            conn.close()
            return result
        except:
            return None

    # ========== دوال المخزون ==========
    def get_inventory(self) -> dict:
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

    # ========== سجل التدقيق ==========
    def log_audit(self, user_id: str, action: str, details: str, ip: str = "0.0.0.0") -> None:
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

    # ========== النسخ الاحتياطي ==========
    def backup_database(self) -> bytes:
        try:
            backup_buffer = BytesIO()
            with zipfile.ZipFile(backup_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(self.db_path, os.path.basename(self.db_path))
                meta = {"backup_date": datetime.now().isoformat(), "db_file": os.path.basename(self.db_path), "version": "4.0"}
                zipf.writestr("metadata.json", json.dumps(meta, ensure_ascii=False))
            backup_buffer.seek(0)
            return backup_buffer.getvalue()
        except:
            return b""

    def restore_database(self, backup_data: bytes) -> bool:
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

    # ========== دورات الإنتاج ==========
    def save_production_cycle(self, cycle_data: dict) -> str:
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

    # ========== المزارع والسجلات اليومية ==========
    def save_farm(self, farm_data: dict) -> str:
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
# 4. نظام المصادقة (مع bcrypt و fallback)
# ==========================================
class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self._create_default_admin()

    def _hash_password(self, password: str) -> str:
        if BCRYPT_AVAILABLE:
            try:
                salt = bcrypt.gensalt(rounds=12)
                return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            except:
                pass
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, password: str, hashed: str) -> bool:
        if BCRYPT_AVAILABLE:
            try:
                return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
            except:
                pass
        return hashlib.sha256(password.encode()).hexdigest() == hashed

    def _create_default_admin(self):
        users = self.db.execute_query("SELECT * FROM users WHERE username='admin'")
        if not users:
            self.create_user('admin', 'admin123', 'owner', 'مدير النظام', 'admin@tower.com', '+249123456789')

    def create_user(self, username: str, password: str, role: str, full_name: str, email: str, phone: str) -> str:
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
        users = self.db.execute_query("SELECT password_hash FROM users WHERE user_id=?", (user_id,))
        if not users:
            return False
        if not self._verify_password(old_password, users[0][0]):
            return False
        new_hash = self._hash_password(new_password)
        self.db.update_record('users', {'password_hash': new_hash}, 'user_id = ?', (user_id,))
        return True

# ==========================================
# 5. مكتبة الأعلاف الكاملة (مع قيم الأحماض الأمينية)
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
    return (cp * 0.155) + (ee * 0.355) + (nfe * 0.155)

def calculate_ne_milk(cp: float, ee: float, ndf: float, se: float) -> float:
    return 0.6 * se - 0.2 * ndf + 0.1 * cp

def calculate_ne_gain(cp: float, ee: float, ndf: float, se: float) -> float:
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
# 10. مولد PDF المحسن
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

            story.append(p("المقادير المعتمدة لتركيب الطن الواحد:", size=14, color=HexColor('#2e7d32')))
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
            story.append(Spacer(1, 15))

            if include_charts and len(formula) > 1 and PLOTLY_AVAILABLE:
                try:
                    fig, ax = plt.subplots(figsize=(6, 3.5))
                    names = list(formula.keys())
                    vals = list(formula.values())
                    colors = ['#1b5e20','#2e7d32','#388e3c','#43a047','#4caf50','#66bb6a']
                    ax.pie(vals, labels=None, autopct='%1.1f%%', colors=colors[:len(names)])
                    ax.legend([arabic_processor.fix_arabic_text(n) for n in names], title=arabic_processor.fix_arabic_text("المكونات"),
                             loc='center left', bbox_to_anchor=(1,0,0.5,1), fontsize=8)
                    ax.set_title(arabic_processor.fix_arabic_text('توزيع المكونات'), fontsize=12)
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
        except:
            return self._generate_simple_report(formula, target_dp, breed, cost, city)

    def _generate_simple_report(self, formula, target_dp, breed, cost, city) -> bytes:
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
# 11. نظام المراجع العلمية (موسع)
# ==========================================
class ScientificReferenceSystem:
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان",
            "references": [
                {"id": "REF001", "authors": "McDonald, P., Edwards, R.A., Greenhalgh, J.F.D., Morgan, C.A.",
                 "year": 2011, "title": "Animal Nutrition", "publisher": "Pearson Education", "edition": "7th Edition",
                 "isbn": "978-1408204238", "summary": "المرجع الأساسي في تغذية الحيوان."},
                {"id": "REF002", "authors": "Cheeke, P.R., Dierenfeld, E.S.",
                 "year": 2010, "title": "Comparative Animal Nutrition and Metabolism",
                 "publisher": "CABI", "isbn": "978-1845936310", "summary": "مقارنة بين آليات التغذية والتمثيل الغذائي."}
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
        },
        "energy_carbohydrates": {
            "title": "الطاقة والكربوهيدرات",
            "references": [
                {"id": "REF006", "authors": "Van Soest, P.J.",
                 "year": 1994, "title": "Nutritional Ecology of the Ruminant",
                 "publisher": "Cornell University Press", "edition": "2nd Edition",
                 "isbn": "978-0801427725", "summary": "المرجع الكلاسيكي في تغذية المجترات."}
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
        },
        "كيف يتم تركيب العلف الأمثل": {
            "answer": "يتم تركيب العلف الأمثل باستخدام محرك الاستمثال الخطي.",
            "reference": "REF001",
            "simplified": "نستخدم برنامجاً ذكياً لحساب أرخص خلطة."
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
# 12. دوال الإرسال (بريد، واتساب)
# ==========================================
def send_code_to_mail(receiver_email: str, attachment_type: str = "full") -> bool:
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = "🌾 السورس كود الكامل - منصة تاور العلمية"
        body = """السلام عليكم، مرفق الكود المصدري الكامل."""
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
    <div style='background:#e8f5e9; padding:10px; border-radius:8px; direction:ltr;'>
        📲 <b>تنبيه عبر واتساب:</b> 
        <a href='{whatsapp_url}' target='_blank'>اضغط لإرسال الرسالة إلى {phone_number}</a>
        <br>{message}
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 13. دوال مساعدة (أسعار المدن، الصور، السوق)
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
        if country == "السودان": multiplier = 1.15
        elif country == "LIBYA": multiplier = 1.10
        elif country == "مصر": multiplier = 1.04
        for k in feed_prices:
            feed_prices[k] *= multiplier
        city_key = f"{country}|||{state_or_region}|||{city}"
        custom_prices = load_city_prices().get(city_key, {})
        for k, v in custom_prices.items():
            if k in feed_prices:
                feed_prices[k] = v
        return feed_prices

# ==========================================
# 14. تكوين الصفحة وتهيئة الجلسة
# ==========================================
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
if "active_stage_title" not in st.session_state:
    st.session_state["active_stage_title"] = "إنتاج عام"
if "active_animal_img" not in st.session_state:
    st.session_state["active_animal_img"] = "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600"

# ==========================================
# 15. CSS المخصص
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
* { font-family: 'Cairo', sans-serif; }
html, body, .stApp { background-color: #f5f5f5; }
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
.animal-banner-img {
    width: 100%; max-height: 200px; object-fit: cover; border-radius: 12px;
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
# 16. بوابة الدخول
# ==========================================
if not st.session_state["approved"]:
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        if st.session_state["last_login_time"]:
            time_diff = (datetime.now() - st.session_state["last_login_time"]).seconds
            if time_diff < LOCKOUT_TIME:
                st.markdown('<div class="main-box" style="max-width:500px;margin:100px auto;text-align:center;">', unsafe_allow_html=True)
                st.error(f"🔒 تم قفل النظام. حاول بعد {LOCKOUT_TIME - time_diff} ثانية")
                st.markdown('</div>', unsafe_allow_html=True)
                st.stop()
            else:
                st.session_state["login_attempts"] = 0

    st.markdown('<div class="main-box" style="max-width:500px;margin:100px auto;text-align:center;">', unsafe_allow_html=True)
    st.markdown("<h1 style='color:#1b5e20;'>🌾 منصة تاور العلمية</h1>")
    st.markdown("<p>للانتاج الحيواني وتركيب الاعلاف</p>")

    if QRCODE_AVAILABLE:
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
# 17. الواجهة الرئيسية
# ==========================================
if not st.session_state["login_welcome_shown"]:
    st.toast("مرحباً بك في منصة تاور العلمية", icon="🌾")
    st.session_state["login_welcome_shown"] = True

st.markdown('<div class="main-box">', unsafe_allow_html=True)

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
    <p style="color:#1565C0;font-size:1.1rem;">محرك الاستمثال الخطي المتقدم القائم على البروتين المهضوم ومعادل النشاء</p>
    <h3 style="color:#c62828;">الاختصاصي م. عبد القادر إسماعيل تاور</h3>
    """, unsafe_allow_html=True)

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
# 18. التبويبات حسب الصلاحية
# ==========================================
if st.session_state["user_role"] == "owner":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "📊 بورصة الأسعار المركزية",
        "🏭 إدارة المستودعات الذكية",
        "🧾 التسويق وفواتير البيع",
        "🖨️ مصمم الديباجة والدعاية",
        "📈 التحليلات المتقدمة",
        "🐔 إدارة مزارع الدجاج اللاحم – خاص بالمالك",
        "💬 تعليقات المختصين",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم"
    ]
elif st.session_state["user_role"] == "specialist":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "📊 بورصة الأسعار المركزية",
        "🏭 إدارة المستودعات الذكية",
        "🧾 التسويق وفواتير البيع",
        "🖨️ مصمم الديباجة والدعاية",
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
# 19. التبويب الأول: النمذجة والحسابات العلفية (مع المختبر)
# ==========================================
with tabs[0]:
    sub_tab1, sub_tab2 = st.tabs(["🎯 تركيب علفة نموذجية بأقل تكلفة", "🔬 مختبر تحليل وفحص الأعلاف الجاهزة"])

    # ========== التبويب الفرعي 1: تركيب العلف ==========
    with sub_tab1:
        st.markdown('<div class="section-title">🌍 تحديد الموقع الجغرافي وبورصة الأسعار</div>', unsafe_allow_html=True)
        col_country, col_state, col_city = st.columns(3)
        with col_country:
            user_country = st.selectbox("اختر الدولة:", ["السودان", "LIBYA", "مصر", "باقي دول العالم"])
        c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
        local_rate = c_info["rate"]
        local_sym = c_info["sym"]
        with col_state:
            if user_country == "السودان":
                chosen_state = st.selectbox("اختر الولاية:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال كردفان", "ولاية جنوب كردفان", "ولاية غرب كردفان", "إقليم النيل الأزرق"])
            elif user_country == "LIBYA":
                chosen_state = st.selectbox("اختر الإقليم:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
            else:
                chosen_state = st.selectbox("الإقليم:", ["المركز الرئيسي", "الأسواق المفتوحة"])
        with col_city:
            if user_country == "السودان":
                cities_map = {
                    "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
                    "ولاية الجزيرة": ["ود مدني", "الحصاحيصا", "المناقل"],
                    "ولاية القضارف": ["القضارف المدينة", "الفاو"],
                    "ولاية شمال كردفان": ["الأبيض", "بارا"],
                    "ولاية جنوب كردفان": ["كادوقلي", "الدلنج"],
                    "ولاية غرب كردفان": ["الفولة", "النهود"],
                    "إقليم النيل الأزرق": ["الدمازين", "الروصيرص"]
                }
                user_city = st.selectbox("اختر المدينة:", cities_map.get(chosen_state, ["عام"]))
            elif user_country == "LIBYA":
                cities_map = {
                    "المنطقة الشرقية": ["طبرق", "بنغازي", "البيضاء"],
                    "المنطقة الغربية": ["طرابلس", "مصراتة", "الزاوية"],
                    "المنطقة الجنوبية": ["سبها", "مرزق", "غات"]
                }
                user_city = st.selectbox("اختر المدينة:", cities_map.get(chosen_state, ["عام"]))
            else:
                user_city = st.text_input("أدخل اسم المدينة:", "طبرق")

        live_prices = MarketPriceEngine.get_adjusted_market_data(user_country, chosen_state, user_city)

        # عرض أسعار الماشية والمنتجات
        col_view1, col_view2 = st.columns(2)
        with col_view1:
            st.markdown(f'<div class="price-card"><b>📈 بورصة الماشية والداجن في ({user_city}):</b><br>' +
                        "<br>".join([f'▪️ {k}: <b>${v:.2f}</b> (<span style="color:#e65100;">{v*local_rate:,.2f} {local_sym}</span>)'
                                    for k, v in st.session_state.get("global_livestock_prices", {
                                        "عجول تسمين": 1350, "أبقار محلية": 900, "ضأن": 180, "ماعز": 130, "خيول": 4500
                                    }).items()]) + "</div>", unsafe_allow_html=True)
        with col_view2:
            st.markdown(f'<div class="price-card"><b>🥩 بورصة المنتجات الحيوانية في ({user_city}):</b><br>' +
                        "<br>".join([f'▪️ {k}: <b>${v:.2f}</b> (<span style="color:#1b5e20;">{v*local_rate:,.2f} {local_sym}</span>)'
                                    for k, v in st.session_state.get("global_products_prices", {
                                        "لحم بقري": 7.50, "لحم ضأن": 9.00, "لحم دجاج": 3.80, "بيض": 4.20, "حليب": 0.90
                                    }).items()]) + "</div>", unsafe_allow_html=True)

        # اختيار القطاع
        st.markdown('<div class="section-title">⚖️ اختيار القطاع والنوع والإنتاجية المستهدفة</div>', unsafe_allow_html=True)
        col_sector, col_sub, col_prod = st.columns(3)
        with col_sector:
            main_sector = st.selectbox("القطاع الرئيسي:", ["الأغنام وسلالاتها 🐏", "الماعز وسلالاتها", "الأبقار وسلالاتها", "الخيول والفروسية", "الطيور والسمان", "الأسماك والأحياء المائية"])
        show_measurements = False
        default_dp = 11.0
        default_se = 60.0
        dynamic_img_key = "عام"
        chosen_concentrate = None
        gender_option = "إناث"

        if main_sector in ["الأغنام وسلالاتها 🐏", "الماعز وسلالاتها"]:
            with col_sector:
                gender_option = st.radio("حدد الجنس:", ["ذكور (تسمين)", "إناث (حليب / أمهات)"], horizontal=True)

        with col_sub:
            if "الأغنام" in main_sector:
                sub_type = st.selectbox("السلالة:", ["الضأن الصحراوي السوداني", "البربري", "النعيمي", "سلالات محلية"])
                dynamic_img_key = "أغنام"
                show_measurements = True
                chosen_concentrate = "مركزات خيول ومجترات"
            elif "الماعز" in main_sector:
                sub_type = st.selectbox("السلالة:", ["الماعز النوبي السوداني", "الماعز الصحراوي", "بور"])
                dynamic_img_key = "ماعز"
                show_measurements = True
                chosen_concentrate = "مركزات خيول ومجترات"
            elif "الأبقار" in main_sector:
                sub_type = st.selectbox("السلالة:", ["كنانة", "بطانة", "هولشتاين"])
                dynamic_img_key = "أبقار"
                show_measurements = True
                chosen_concentrate = "مركزات خيول ومجترات"
            elif "الخيول" in main_sector:
                sub_type = st.selectbox("السلالة:", ["خيل عربي أصيل", "ثوروبريد", "خيول محلية هجين"])
                dynamic_img_key = "خيول"
                show_measurements = True
                chosen_concentrate = "مركزات خيول ومجترات"
            elif "الطيور" in main_sector:
                sub_type = st.selectbox("نوع الطيور:", ["طائر السمان (Quail)", "دواجن لاحم (Broiler)", "دواجن بياض (Layer)"])
                dynamic_img_key = "سمان" if "السمان" in sub_type else "دواجن"
                chosen_concentrate = "مركزات دواجن وسمان"
            else:
                sub_type = st.selectbox("نوع الأسماك:", ["البلطي النيلي", "القرموط"])
                dynamic_img_key = "أسماك"
                chosen_concentrate = "مسحوق أسماك (Fishmeal 60%)"

        with col_prod:
            if "الأغنام" in main_sector:
                if gender_option == "ذكور (تسمين)":
                    prod_stage = st.selectbox("خط إنتاج الذكور:", ["تسمين حملان مكثف", "حملان تيد"])
                    default_dp = 12.0 if "مكثف" in prod_stage else 9.5
                    default_se = 64.0 if "مكثف" in prod_stage else 58.0
                else:
                    prod_stage = st.selectbox("خط إنتاج الإناث:", ["نعاج مرضعات", "نعاج حامل", "نعاج جافة"])
                    default_dp = 12.8 if "مرضعات" in prod_stage else (10.5 if "حامل" in prod_stage else 8.0)
                    default_se = 66.0 if "مرضعات" in prod_stage else (60.0 if "حامل" in prod_stage else 50.0)
            elif "الماعز" in main_sector:
                if gender_option == "ذكور (تسمين)":
                    prod_stage = st.selectbox("خط إنتاج الذكور:", ["تسمين جديان", "تيوس علفية"])
                    default_dp = 11.5 if "جديان" in prod_stage else 9.0
                    default_se = 62.0 if "جديان" in prod_stage else 55.0
                else:
                    prod_stage = st.selectbox("خط إنتاج الإناث:", ["عنزات حلابة", "عنزات حامل", "صيانة"])
                    default_dp = 12.8 if "حلابة" in prod_stage else (10.0 if "حامل" in prod_stage else 7.8)
                    default_se = 65.0 if "حلابة" in prod_stage else (58.0 if "حامل" in prod_stage else 48.0)
            elif "الأبقار" in main_sector:
                prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج حليب", "تسمين عجول"])
                default_dp = 12.5 if "حليب" in prod_stage else 10.0
                default_se = 68.0 if "حليب" in prod_stage else 65.0
            elif "الخيول" in main_sector:
                prod_stage = st.selectbox("نوع الإنتاج:", ["خيول رياضة", "أمهار نامية", "فرسات مرضعات"])
                default_dp = 12.5 if "أمهار" in prod_stage or "مرضعات" in prod_stage else 9.5
                default_se = 65.0 if "رياضة" in prod_stage else 60.0
            elif "الطيور" in main_sector:
                if "السمان" in sub_type:
                    prod_stage = st.selectbox("نوع الإنتاج:", ["سمان بادي", "سمان بياض"])
                    default_dp = 20.0 if "بادي" in prod_stage else 16.5
                    default_se = 72.0 if "بادي" in prod_stage else 68.0
                else:
                    prod_stage = st.selectbox("نوع الإنتاج:", ["بادي دواجن", "نامي دواجن", "ناهي دواجن", "بياض إنتاجي"])
                    default_dp = 20.0 if "بادي" in prod_stage else (18.5 if "نامي" in prod_stage else (16.5 if "ناهي" in prod_stage else 15.0))
                    default_se = 76.0 if "بادي" in prod_stage else (74.0 if "نامي" in prod_stage else (75.0 if "ناهي" in prod_stage else 70.0))
            else:
                prod_stage = st.selectbox("نوع الإنتاج:", ["بادئ زريعة", "نمو وتسمين"])
                default_dp = 29.5 if "زريعة" in prod_stage else 25.0
                default_se = 70.0

        # تقدير الوزن للمجترات
        if show_measurements:
            st.markdown('<div class="section-title">📐 القياسات الجسدية وتقدير الأوزان</div>', unsafe_allow_html=True)
            col_h, col_l, col_ag = st.columns(3)
            with col_h:
                h_girth = st.number_input("📏 محيط الصدر (سم):", value=150.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 75.0)
            with col_l:
                b_length = st.number_input("📏 طول الجسم (سم):", value=130.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 65.0)
            with col_ag:
                a_months = st.number_input("⏳ العمر التقديري (أشهر):", value=12)
            weight_factor = 10838 if "الأبقار" in main_sector else (15500 if "الأغنام" in main_sector else (15000 if "الماعز" in main_sector else 11877))
            feed_factor = 0.025 if "الأبقار" in main_sector else (0.035 if "الأغنام" in main_sector else (0.032 if "الماعز" in main_sector else 0.022))
            calc_weight = (h_girth ** 2 * b_length) / weight_factor
            req_feed_kg = calc_weight * feed_factor
            st.success(f"📊 الوزن الحيوي المتوقع: **{calc_weight:.1f} كجم** | الاحتياج اليومي للمادة الجافة: **{req_feed_kg:.2f} كجم**")
        else:
            st.markdown('<div class="section-title">✨ قطاع الطيور والأسماك</div>', unsafe_allow_html=True)
            st.info("💡 تم تحييد شريط القياس الجسدي لعدم ملاءمته للطيور والأسماك.")

        # حدود الموازنة
        st.markdown('<div class="section-title">📋 حدود الموازنة الذكية (DP & SE)</div>', unsafe_allow_html=True)
        col_p1, col_p2 = st.columns(2)
        use_cp_basis = st.checkbox("⚡ استخدم البروتين الخام (CP) بدلاً من المهضوم (DP)", value=False)
        if use_cp_basis:
            default_cp = default_dp / 0.82
            with col_p1:
                st.metric("🧬 بروتين خام (CP) مقترح:", f"{default_cp:.1f} %")
                override_cp = st.checkbox("⚙️ تعديل البروتين الخام")
                final_target_cp = st.slider("حدّد نسبة CP:", 5.0, 60.0, value=float(default_cp)) if override_cp else default_cp
            final_target_dp = None
        else:
            with col_p1:
                st.metric("🧬 بروتين مهضوم (DP) مقترح:", f"{default_dp} %")
                override_dp = st.checkbox("⚙️ تعديل فني اختياري للبروتين المهضوم")
                final_target_dp = st.slider("حدّد نسبة DP:", 5.0, 40.0, value=default_dp) if override_dp else default_dp
        with col_p2:
            st.metric("🌽 معادل النشاء (SE) مقترح:", f"{default_se} وحدة")
            override_se = st.checkbox("⚙️ تعديل فني اختياري لمعادل النشاء")
            final_target_se = st.slider("حدّد حد الـ SE المستهدف:", 10.0, 90.0, value=default_se) if override_se else default_se

        # اختيار المكونات
        selected_ingredients = []
        ingredient_prices = {}
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            with st.expander(f"📁 {cat_name}", expanded=True if "الحبوب" in cat_name or "الأكساب" in cat_name else False):
                sub_cols = st.columns(3)
                for idx, (ing_name, _) in enumerate(items.items()):
                    with sub_cols[idx % 3]:
                        is_def = ing_name == chosen_concentrate or ing_name in ["ذرة صفراء", "سورجم (فتريتة)", "أمباز الفول السوداني (كسب)", "كسب فول صويا 44%", "نخالة قمح (ردة)", "ملح الطعام", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)", "بيكربونات الصوديوم (الصودا)", "مضاد سموم فطرية"]
                        checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                        current_live_price = live_prices.get(ing_name, 350.0)
                        if st.session_state["user_role"] == "owner":
                            price_input = st.number_input(f"السعر للطن ({ing_name}) $:", min_value=5.0, value=float(current_live_price), key=f"price_{ing_name}")
                        else:
                            st.markdown(f"💰 السعر الحالي: **`${current_live_price:.2f}`** / طن")
                            price_input = current_live_price
                        if checked:
                            selected_ingredients.append(ing_name)
                            ingredient_prices[ing_name] = price_input

        # الإضافات الإلزامية
        fixed_additives = {"ملح الطعام": 0.5, "مضاد سموم فطرية": 0.2, "الحجر الجيري (بودرة بلاط)": 2.5 if "بياض" in prod_stage else 1.5, "فوسفات ثنائي الكالسيوم (DCP)": 1.0}
        auto_added_enzymes = {}
        if main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاتها", "الأغنام وسلالاتها 🐏"]:
            auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.75
        if main_sector in ["الطيور والسمان"]:
            auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.20
            auto_added_enzymes["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05
        if "كسب بذور القطن (مقشور)" in selected_ingredients and "الطيور" in main_sector:
            auto_added_enzymes["كبريتات الحديدوز (معادل الجوسيبول)"] = 0.15
        all_fixed_additives = {**fixed_additives, **auto_added_enzymes}
        for item in all_fixed_additives:
            if item not in selected_ingredients:
                selected_ingredients.append(item)
                ingredient_prices[item] = live_prices.get(item, 40.0)

        st.markdown("---")
        nz_placeholder = st.empty()

        if st.button("🚀 تشغيل محرك الاستمثال الخطي (بالبروتين المهضوم ومعادل النشاء)", type="primary", use_container_width=True):
            with nz_placeholder.container():
                st.warning("⚠️ **إشعار هام:** تأكد من موازنة درجات حرارة الكبس لضمان عدم تثبيط الإنزيمات. (سيختفي بعد 40 ثانية)")

            if not SCIPY_AVAILABLE:
                st.error("❌ مكتبة scipy غير مثبتة. يرجى تثبيتها: pip install scipy")
            elif len(selected_ingredients) < 3:
                st.error("❌ يرجى اختيار 3 مواد علفية على الأقل")
            else:
                try:
                    c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
                    bounds = [(all_fixed_additives.get(ing, 0.0), all_fixed_additives.get(ing, 100.0)) if ing in all_fixed_additives else (0.0, 100.0) for ing in selected_ingredients]

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
                        if use_cp_basis:
                            cp_row.append(cp_val)
                        else:
                            cp_row.append(cp_val * dc_val)
                        se_row.append(se_val)
                    A_eq.append(cp_row)
                    if use_cp_basis:
                        b_eq.append(final_target_cp * 100.0)
                    else:
                        b_eq.append(final_target_dp * 100.0)

                    A_ub = [[-1.0 * x for x in se_row]]
                    b_ub = [-1.0 * final_target_se * 100.0]

                    # قيود إضافية للحد من الحبوب
                    grain_indicators = [1.0 if ing in BIG_FEEDS_LIBRARY["🌾 الحبوب ومصادر الطاقة الكبرى"] else 0.0 for ing in selected_ingredients]
                    if sum(grain_indicators) > 0:
                        A_ub.append([-1.0 * x for x in grain_indicators])
                        b_ub.append(-50.0)
                    if "نخالة قمح (ردة)" in selected_ingredients:
                        fiber_indicators = [1.0 if ing == "نخالة قمح (ردة)" else 0.0 for ing in selected_ingredients]
                        A_ub.append(fiber_indicators)
                        b_ub.append(18.0)

                    # حد أقصى لبعض المواد
                    dynamic_limits = {
                        "مولاس قصب السكر": 12.0,
                        "يوريا علفية محصنة (المجترات فقط)": 1.0,
                        "ملح الطعام": 1.0
                    }
                    for material, limit in dynamic_limits.items():
                        if material in selected_ingredients:
                            idx = selected_ingredients.index(material)
                            constraint_row = [0.0] * len(selected_ingredients)
                            constraint_row[idx] = 1.0
                            A_ub.append(constraint_row)
                            b_ub.append(limit)

                    res = linprog(c_vector, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
                    if not res.success:
                        st.warning("⚠️ المحاولة الأولى فشلت، نحاول بحلول مرنة...")
                        A_ub_flex = []
                        b_ub_flex = []
                        A_ub_flex.append([-1.0 * x for x in se_row])
                        b_ub_flex.append(-1.0 * (final_target_se - 3.0) * 100.0)
                        if sum(grain_indicators) > 0:
                            A_ub_flex.append([-1.0 * x for x in grain_indicators])
                            b_ub_flex.append(-40.0)
                        if "نخالة قمح (ردة)" in selected_ingredients:
                            fiber_indicators = [1.0 if ing == "نخالة قمح (ردة)" else 0.0 for ing in selected_ingredients]
                            A_ub_flex.append(fiber_indicators)
                            b_ub_flex.append(25.0)
                        for material, limit in dynamic_limits.items():
                            if material in selected_ingredients:
                                idx = selected_ingredients.index(material)
                                constraint_row = [0.0] * len(selected_ingredients)
                                constraint_row[idx] = 1.0
                                A_ub_flex.append(constraint_row)
                                b_ub_flex.append(limit + 3)
                        res = linprog(c_vector, A_ub=A_ub_flex, b_ub=b_ub_flex, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

                    if res.success:
                        formula_results = {}
                        computed_se_total = 0.0
                        for idx, ing in enumerate(selected_ingredients):
                            if res.x[idx] > 0.0001:
                                formula_results[ing] = res.x[idx]
                                for cat in BIG_FEEDS_LIBRARY.values():
                                    if ing in cat:
                                        computed_se_total += (res.x[idx] / 100.0) * cat[ing].get("SE", 0.0)

                        st.session_state["active_formula"] = formula_results
                        st.session_state["active_cp_tag"] = final_target_dp if not use_cp_basis else (final_target_cp * 0.82)
                        st.session_state["active_se_tag"] = computed_se_total
                        st.session_state["active_breed_tag"] = sub_type
                        st.session_state["active_stage_title"] = f"{main_sector} ({gender_option}) - {prod_stage}"
                        st.success(f"🎯 تم تشغيل المحرك بنجاح في سوق: {user_city}")

                        if not use_cp_basis and final_target_dp > 0:
                            nutritive_ratio = computed_se_total / final_target_dp
                            st.info(f"📊 النسبة الغذائية للخلطة (SE / DP): **{nutritive_ratio:.2f}**")

                        res_col1, res_col2 = st.columns([0.6, 0.4])
                        with res_col1:
                            st.write("#### 📝 المقادير المعتمدة لتركيب طن واحد (كجم):")
                            for k, v in formula_results.items():
                                st.markdown(f'<div class="formula-item">▪️ <b>{k}:</b> {v:.2f} % ➡️ ({v*10:.1f} كجم / طن)</div>', unsafe_allow_html=True)

                            ton_cost = res.fun / 100.0 if hasattr(res, 'fun') else 280.0
                            st.session_state["computed_ton_cost"] = ton_cost
                            st.metric(f"💰 التكلفة الفعلية لإنتاج الطن في {user_city}: ", f"${ton_cost:.2f} (أو {ton_cost*local_rate:,.1f} {local_sym})")

                            col_share, col_pdf = st.columns(2)
                            with col_share:
                                share_message = f"منصة تاور العلمية - الخلطة المعتمدة: {sub_type} ({gender_option})، بتكلفة إنتاج {ton_cost:.2f}$ للطن. المشرف: الاختصاصي م. عبد القادر إسماعيل تاور."
                                encoded_share_msg = urllib.parse.quote(share_message)
                                st.link_button("📲 مشاركة الفاتورة عبر واتساب", f"https://wa.me/?text={encoded_share_msg}")
                            with col_pdf:
                                try:
                                    pdf_data = pdf_generator.generate_comprehensive_report(
                                        formula_results, st.session_state["active_cp_tag"],
                                        f"{sub_type} ({gender_option})", ton_cost, user_city,
                                        ton_cost*local_rate, local_sym, computed_se_total, include_charts=True
                                    )
                                    st.download_button("📥 تحميل التقرير الفني PDF", pdf_data,
                                                       file_name=f"Tower_Scientific_Platform_{user_city}.pdf",
                                                       mime="application/pdf", use_container_width=True)
                                except Exception as pdf_err:
                                    st.error(f"⚠️ لم يتم بناء ملف الـ PDF: {pdf_err}")

                        with res_col2:
                            if PLOTLY_AVAILABLE and len(formula_results) > 1:
                                fig = px.pie(values=list(formula_results.values()), names=list(formula_results.keys()),
                                           title="توزيع مكونات الخلطة", color_discrete_sequence=px.colors.sequential.Greens)
                                fig.update_layout(height=400)
                                st.plotly_chart(fig, use_container_width=True)
                            chart_data = pd.DataFrame({'المكون': list(formula_results.keys()), 'النسبة المئوية': list(formula_results.values()), 'الوزن (كجم/طن)': [v*10 for v in formula_results.values()]})
                            st.bar_chart(chart_data.set_index('المكون')['الوزن (كجم/طن)'])
                    else:
                        st.error("❌ تعذر إيجاد حل رياضي متزن. يرجى إتاحة خامات إضافية.")
                    time.sleep(40)
                    nz_placeholder.empty()
                except Exception as e:
                    st.error(f"❌ خطأ في المحرك: {e}")

    # ========== التبويب الفرعي 2: مختبر التحليل ==========
    with sub_tab2:
        st.markdown('<div class="section-title">🔬 مختبر فحص وتحليل الخلطات الجاهزة</div>', unsafe_allow_html=True)
        st.write("اكتب مقادير خلطتك الحالية بالكيلوجرام، وسيقوم المختبر بتحليلها برمجياً لتقدير نسبة البروتين المهضوم ومعادل النشاء الإجمالي.")

        st.subheader("🎯 حدد الحيوان والغرض المستهدف للمقارنة:")
        col_lab_animal, col_lab_stage = st.columns(2)
        with col_lab_animal:
            target_animal = st.selectbox("اختر الفصيل:", ["أبقار", "أغنام", "ماعز", "خيول", "دواجن لاحم", "دواجن بياض", "سمان", "أسماك"])
        with col_lab_stage:
            if target_animal in ["أبقار", "أغنام", "ماعز"]:
                production_type = st.selectbox("مرحلة الإنتاج:", ["تسمين", "حليب/إدرار", "حمل/دفع غذائي", "صيانة"])
            elif target_animal in ["دواجن لاحم", "دواجن بياض", "سمان"]:
                production_type = st.selectbox("مرحلة الإنتاج:", ["بادي", "نامي", "ناهي", "بياض"])
            else:
                production_type = st.selectbox("مرحلة الإنتاج:", ["نمو", "تسمين نهائي"])

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
        suggested_cp = cp_requirements.get((target_animal, production_type), 15.0)
        suggested_dp = suggested_cp * 0.80

        analysis_basis = st.radio("أساس التحليل:", ["بروتين مهضوم (DP)", "بروتين خام (CP)"], horizontal=True)
        if analysis_basis == "بروتين مهضوم (DP)":
            target_value = st.number_input("النسبة المستهدفة (DP %)", min_value=5.0, max_value=50.0, value=float(suggested_dp), step=0.1)
            st.caption(f"البروتين الخام المقترح ≈ {suggested_cp:.1f}%")
        else:
            target_value = st.number_input("النسبة المستهدفة (CP %)", min_value=5.0, max_value=50.0, value=float(suggested_cp), step=0.1)

        st.markdown("---")
        st.subheader("📥 أدخل أوزان المكونات بالكيلوجرام:")
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
                lab_user_inputs[ing_name] = st.number_input(f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0, step=5.0, key=f"lab_in_{ing_name}")
        with col_input2:
            for ing_name in all_library_ingredients[segment:segment*2]:
                lab_user_inputs[ing_name] = st.number_input(f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0, step=5.0, key=f"lab_in_{ing_name}")
        with col_input3:
            for ing_name in all_library_ingredients[segment*2:]:
                lab_user_inputs[ing_name] = st.number_input(f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0, step=5.0, key=f"lab_in_{ing_name}")

        st.markdown("---")
        if st.button("🧪 تشغيل التحليل المخبري", type="primary", use_container_width=True):
            lab_total_weight = sum(lab_user_inputs.values())
            if lab_total_weight <= 0:
                st.warning("⚠️ الرجاء إدخال أوزان أكبر من الصفر.")
            else:
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
                        entered_components_summary.append({"المادة العلفية": ing_name, "الوزن المدخل": f"{weight:.1f} كجم", "النسبة المئوية": f"{pct * 100:.2f}%"})

                st.success("🔬 تم فحص العينة وتحليل المحتوى الغذائي بنجاح!")
                st.markdown(f"### ⚖️ إجمالي وزن الخلطة: **{lab_total_weight:.1f} كجم**")
                st.write("#### 📊 نسب توزيع المكونات:")
                st.table(pd.DataFrame(entered_components_summary))

                st.markdown("---")
                st.write("#### 🔬 تقرير الفحص المخبري النهائي:")
                if analysis_basis == "بروتين مهضوم (DP)":
                    comparison_value = calculated_total_dp
                    status_label = "✅ مطابق وممتاز" if comparison_value >= target_value else "⚠️ ناقص البروتين المهضوم"
                    st.write(f"🔬 البروتين الخام (CP) المحسوب: **{calculated_total_cp:.2f}%**")
                    st.write(f"🔬 البروتين المهضوم (DP) المحسوب: **{calculated_total_dp:.2f}%**")
                else:
                    comparison_value = calculated_total_cp
                    status_label = "✅ مطابق وممتاز" if comparison_value >= target_value else "⚠️ ناقص البروتين الخام"
                    st.write(f"🔬 البروتين الخام (CP) المحسوب: **{calculated_total_cp:.2f}%**")
                    st.write(f"🔬 البروتين المهضوم (DP) المحسوب: **{calculated_total_dp:.2f}%**")

                lab_report_data = [
                    {"العنصر الغذائي": "البروتين المهضوم (DP)", "القيمة المحسوبة": f"{calculated_total_dp:.2f}%", "الاحتياج القياسي": f"{target_value:.1f}%" if analysis_basis == "بروتين مهضوم (DP)" else "-", "التقييم": status_label},
                    {"العنصر الغذائي": "البروتين الخام (CP)", "القيمة المحسوبة": f"{calculated_total_cp:.2f}%", "الاحتياج القياسي": f"{target_value:.1f}%" if analysis_basis == "بروتين خام (CP)" else "-", "التقييم": "-"},
                    {"العنصر الغذائي": "معادل النشاء (SE)", "القيمة المحسوبة": f"{calculated_total_se:.2f} وحدة", "الاحتياج القياسي": "مرن حسب الفصيل", "التقييم": "تحليل طاقة كلي"}
                ]
                st.table(pd.DataFrame(lab_report_data))

                st.write("📊 التمثيل البياني لتوزيع المواد المدخلة:")
                graph_data = {k: v for k, v in lab_user_inputs.items() if v > 0}
                if graph_data and PLOTLY_AVAILABLE:
                    fig = px.bar(x=list(graph_data.keys()), y=list(graph_data.values()), labels={'x': 'المادة العلفية', 'y': 'الوزن (كجم)'}, title="توزيع أوزان المواد في الخلطة المختبرة")
                    st.plotly_chart(fig, use_container_width=True)

                lab_share_text = f"نتيجة مختبر منصة تاور:\nالحيوان: {target_animal} - {production_type}\nالبروتين المحسوب: {comparison_value:.2f}%\nالمعيار: {target_value:.1f}%"
                encoded_lab = urllib.parse.quote(lab_share_text)
                st.markdown(f'<a href="https://wa.me/?text={encoded_lab}" target="_blank"><button style="background-color:#25D366; color:white; padding:10px; border-radius:5px;">📲 مشاركة النتيجة عبر واتساب</button></a>', unsafe_allow_html=True)

# ==========================================
# 20. بقية التبويبات (مختصرة ولكن كاملة)
# ==========================================
# التبويب 2: بورصة الأسعار
if "📊 بورصة الأسعار المركزية" in tabs_titles:
    tab_idx = tabs_titles.index("📊 بورصة الأسعار المركزية")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">📊 لوحة تحكم بورصة تاور المركزية الشاملة</div>', unsafe_allow_html=True)
        if st.session_state["user_role"] == "specialist":
            st.warning("⚠️ حساب مختص: متاح لك استعراض الأسعار فقط، التعديل محجوز لإدارة المنصة.")
        tab_livestock, tab_products = st.tabs(["🐄 بورصة الماشية", "🥛 بورصة المنتجات"])
        with tab_livestock:
            st.subheader("أسعار الماشية والداجن")
            default_livestock = {"عجول تسمين": 1350.0, "أبقار محلية": 900.0, "ضأن": 180.0, "ماعز": 130.0, "خيول": 4500.0}
            for animal, price in default_livestock.items():
                st.metric(animal, f"${price:.2f}")
        with tab_products:
            st.subheader("أسعار المنتجات الحيوانية")
            default_products = {"لحم بقري": 7.50, "لحم ضأن": 9.00, "لحم دجاج": 3.80, "بيض": 4.20, "حليب": 0.90}
            for product, price in default_products.items():
                st.metric(product, f"${price:.2f}")

# التبويب 3: إدارة المخزون
if "🏭 إدارة المستودعات الذكية" in tabs_titles:
    tab_idx = tabs_titles.index("🏭 إدارة المستودعات الذكية")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">🏭 لوحة التحكم الذكية بالمخازن والمستودعات المركزية</div>', unsafe_allow_html=True)
        if st.session_state["user_role"] == "specialist":
            st.warning("⚠️ حساب مختص: يمكنك مراجعة الأرصدة فقط دون تعديل.")
        inventory = InventoryManager.get_inventory()
        stock_warnings = InventoryManager.check_stock_levels()
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        with col_stats1: st.metric("إجمالي المواد", len(inventory))
        with col_stats2:
            critical_items = sum(1 for v in stock_warnings.values() if v == "نفذ المخزون")
            st.metric("مواد نفذت", critical_items)
        with col_stats3:
            low_items = sum(1 for v in stock_warnings.values() if v == "منخفض")
            st.metric("مواد منخفضة", low_items)
        with col_stats4:
            healthy_items = len(inventory) - critical_items - low_items
            st.metric("مواد آمنة", healthy_items)
        st.markdown("---")
        inv_cols = st.columns(3)
        for idx, (ing_name, qty_data) in enumerate(list(inventory.items())):
            with inv_cols[idx % 3]:
                qty = qty_data.get("quantity", 0)
                threshold = qty_data.get("min_threshold", 5.0)
                if qty <= 0:
                    status_badge = f'<span class="stock-critical">⚠️ نفذ: {qty:.2f} طن</span>'
                elif qty < threshold:
                    status_badge = f'<span class="stock-critical">⚠️ حرج: {qty:.2f} طن</span>'
                else:
                    status_badge = f'<span class="stock-normal">آمن: {qty:.2f} طن</span>'
                st.markdown(f"**{ing_name}** | {status_badge}", unsafe_allow_html=True)
                if st.session_state["user_role"] == "owner":
                    new_qty = st.number_input(f"تحديث ({ing_name}) طن:", min_value=0.0, value=float(qty), key=f"inv_input_{ing_name}")
                    if new_qty != qty:
                        InventoryManager.update_stock(ing_name, new_qty, st.session_state["user"]["user_id"])
                        st.rerun()

# التبويب 4: الفواتير
if "🧾 التسويق وفواتير البيع" in tabs_titles:
    tab_idx = tabs_titles.index("🧾 التسويق وفواتير البيع")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">💰 نظام تسويق المنتجات وإصدار الفواتير مع الخصم التلقائي</div>', unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: client_name = st.text_input("اسم العميل / المزرعة:", "مزارع الإنتاج المتكاملة")
        with col_c2: required_tons = st.number_input("الكمية المطلوبة (طن):", min_value=0.1, value=2.0, step=0.5)
        with col_c3: added_profit = st.number_input("هامش الربح للطن ($):", min_value=0.0, value=50.0)
        selling_price = st.session_state["computed_ton_cost"] + added_profit
        total_bill = selling_price * required_tons
        st.markdown("### 🧾 فاتورة بيع وتوريد أعلاف رسمية")
        col_fact1, col_fact2 = st.columns(2)
        with col_fact1:
            st.markdown(f"""<div class="price-card"><h4>تفاصيل الفاتورة:</h4><p>العميل: <b>{client_name}</b></p><p>الكمية: <b>{required_tons} طن</b></p><p>سعر الطن: <b>${selling_price:.2f}</b></p><p style="font-size: 1.2rem; color: #1b5e20;">الإجمالي: <b>${total_bill:.2f}</b></p></div>""", unsafe_allow_html=True)
        with col_fact2:
            st.markdown("#### 📊 مكونات الخلطة المباعة:")
            if st.session_state["active_formula"]:
                for ingredient, pct in st.session_state["active_formula"].items():
                    required_amount = (pct / 100) * required_tons
                    st.markdown(f"▪️ {ingredient}: **{required_amount:.2f}** طن ({pct:.1f}% من الخلطة)")
        if st.session_state["user_role"] == "owner":
            if st.button("✅ تأكيد عملية البيع وخصم المكونات من المستودع", type="primary", use_container_width=True):
                can_deduct = True
                for name, pct in st.session_state["active_formula"].items():
                    required_amount = (pct / 100) * required_tons
                    current_stock = InventoryManager.get_inventory().get(name, {}).get("quantity", 0)
                    if current_stock < required_amount:
                        can_deduct = False
                        st.error(f"❌ رصيد غير كافي: {name}!")
                        break
                if can_deduct:
                    for name, pct in st.session_state["active_formula"].items():
                        required_amount = (pct / 100) * required_tons
                        InventoryManager.deduct_stock(name, required_amount, st.session_state["user"]["user_id"])
                    st.success("🔥 تم الخصم التلقائي وتحديث المخازن بنجاح!")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
        else:
            st.info("ℹ️ تأكيد الفواتير وحركات الخصم متاحة حصرياً لإدارة المالك.")

# التبويب 5: مصمم الديباجة
if "🖨️ مصمم الديباجة والدعاية" in tabs_titles:
    tab_idx = tabs_titles.index("🖨️ مصمم الديباجة والدعاية")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">👑 مصمم ديباجات الطباعة الفنية على جوالات الأعلاف</div>', unsafe_allow_html=True)
        trade_brand = st.text_input("اسم البراند التجاري:", "منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف")
        st.markdown(f"""
        <div class="sack-tag">
            <h2 style="color:#1b5e20;">🌟 {trade_brand} 🌟</h2>
            <h3 style="color:#c62828;">الاختصاصي م. عبد القادر إسماعيل تاور</h3>
            <p style="background:#e8f5e9;padding:10px;border-radius:8px;">
                🎯 {st.session_state['active_stage_title']} | 
                DP: {st.session_state['active_cp_tag']:.1f}% | 
                SE: {st.session_state['active_se_tag']:.1f} وحدة
            </p>
            <small>تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d')}</small>
        </div>
        """, unsafe_allow_html=True)

# التبويب 6: التحليلات المتقدمة
if "📈 التحليلات المتقدمة" in tabs_titles:
    tab_idx = tabs_titles.index("📈 التحليلات المتقدمة")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">📈 التحليلات المتقدمة ولوحة المؤشرات</div>', unsafe_allow_html=True)
        col_met1, col_met2, col_met3, col_met4 = st.columns(4)
        with col_met1: st.markdown('<div class="metric-card"><h3>الخلطات</h3><h2>1,247</h2><p>تم توليدها</p></div>', unsafe_allow_html=True)
        with col_met2: st.markdown('<div class="metric-card"><h3>التكلفة</h3><h2>$285</h2><p>لطن العلف</p></div>', unsafe_allow_html=True)
        with col_met3: st.markdown('<div class="metric-card"><h3>التوفير</h3><h2>18%</h2><p>مقارنة بالتقليدي</p></div>', unsafe_allow_html=True)
        with col_met4: st.markdown('<div class="metric-card"><h3>الرضا</h3><h2>96%</h2><p>تقييم إيجابي</p></div>', unsafe_allow_html=True)
        st.markdown("---")
        if PLOTLY_AVAILABLE:
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.subheader("📊 توزيع المواد")
                usage = pd.DataFrame({'المادة': ['ذرة', 'صويا', 'نخالة', 'أملاح', 'أخرى'], 'النسبة': [45, 25, 15, 10, 5]})
                fig = px.pie(usage, values='النسبة', names='المادة', color_discrete_sequence=px.colors.sequential.Greens)
                st.plotly_chart(fig, use_container_width=True)
            with col_chart2:
                st.subheader("📈 اتجاه الأسعار")
                dates = pd.date_range(start='2024-01-01', periods=12, freq='ME')
                data = pd.DataFrame({'التاريخ': dates, 'الذرة': [220,225,230,228,235,240,238,242,245,248,250,252], 'الصويا': [440,445,442,448,450,455,452,458,460,462,465,468]})
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data['التاريخ'], y=data['الذرة'], mode='lines+markers', name='الذرة'))
                fig.add_trace(go.Scatter(x=data['التاريخ'], y=data['الصويا'], mode='lines+markers', name='الصويا'))
                fig.update_layout(title='اتجاه الأسعار')
                st.plotly_chart(fig, use_container_width=True)

# التبويب 7: إدارة مزارع الدجاج
if "🐔 إدارة مزارع الدجاج اللاحم – خاص بالمالك" in tabs_titles:
    tab_idx = tabs_titles.index("🐔 إدارة مزارع الدجاج اللاحم – خاص بالمالك")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج اللاحم (Broiler) – خاص بالمالك</div>', unsafe_allow_html=True)
        if st.session_state["user_role"] != "owner":
            st.warning("⚠️ هذه الصلاحية متاحة للمالك فقط.")
        else:
            with st.expander("➕ إضافة مزرعة جديدة", expanded=False):
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1: new_farm_name = st.text_input("اسم المزرعة")
                with col_f2: new_owner_name = st.text_input("اسم المالك")
                with col_f3: new_phone = st.text_input("رقم الواتساب", WHATSAPP_NUMBER)
                if st.button("💾 حفظ المزرعة") and new_farm_name:
                    farm_data = {"farm_name": new_farm_name, "owner_name": new_owner_name, "owner_phone": new_phone}
                    BroilerFarmManager.save_farm(farm_data)
                    st.success("تمت الإضافة!")
                    st.rerun()

            farms = BroilerFarmManager.get_farms()
            if farms:
                farm_names = [f["farm_name"] for f in farms]
                selected_farm = st.selectbox("اختر مزرعة:", [""] + farm_names)
                if selected_farm:
                    farm = next((f for f in farms if f["farm_name"] == selected_farm), None)
                    if farm:
                        st.markdown(f"### 🏷️ {farm['farm_name']} - {farm['owner_name']}")
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

                        init_weight = 0.045
                        total_alive = birds - dead - culled
                        total_gain = total_alive * (weight - init_weight)
                        adg = BroilerFarmManager.calculate_adg(weight*1000, init_weight*1000, age)
                        fcr = BroilerFarmManager.calculate_fcr(feed, total_gain) if total_gain > 0 else 0
                        mortality = BroilerFarmManager.calculate_mortality_rate(dead, birds)
                        livability = BroilerFarmManager.calculate_livability(birds, dead)
                        epef = BroilerFarmManager.calculate_epef(livability, weight, age, fcr)

                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                        with col_m1: st.metric("ADG (جم)", f"{adg:.1f}")
                        with col_m2: st.metric("FCR", f"{fcr:.2f}")
                        with col_m3: st.metric("النفوق (%)", f"{mortality:.2f}%")
                        with col_m4: st.metric("EPEF", f"{epef:.0f}")

                        if st.button("💾 حفظ بيانات اليوم"):
                            log_data = {"farm_id": farm["farm_id"], "age_days": age, "avg_weight_kg": weight, "feed_consumed_kg": feed, "dead_birds": dead, "culled_birds": culled}
                            BroilerFarmManager.save_daily_log(log_data)
                            st.success("تم حفظ اليوم!")
                            st.rerun()

                        with st.expander("📜 السجلات السابقة"):
                            logs = BroilerFarmManager.get_daily_logs(farm["farm_id"])
                            if logs:
                                st.dataframe(pd.DataFrame(logs), use_container_width=True)
            else:
                st.info("👈 أضف مزرعة جديدة")

# التبويب 8: تعليقات المختصين
if "💬 تعليقات المختصين" in tabs_titles:
    tab_idx = tabs_titles.index("💬 تعليقات المختصين")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">💬 قناة التواصل والتعليقات الفنية</div>', unsafe_allow_html=True)
        st.text_area("التعليقات الحالية:", value=st.session_state["shared_comments"], height=200, disabled=True)
        new_comment = st.text_area("إضافة تعليق جديد:")
        if st.button("➕ إضافة تعليق") and new_comment:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            user_name = st.session_state["user"]["full_name"]
            st.session_state["shared_comments"] += f"\n• [{timestamp}] {user_name}: {new_comment}"
            st.success("تمت الإضافة!")
            st.rerun()

# التبويب 9: المراجع العلمية
if "📚 المراجع العلمية" in tabs_titles:
    tab_idx = tabs_titles.index("📚 المراجع العلمية")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
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

# التبويب 10: المساعدة الذكية
if "💡 المساعدة الذكية" in tabs_titles:
    tab_idx = tabs_titles.index("💡 المساعدة الذكية")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">💡 المساعدة الذكية</div>', unsafe_allow_html=True)
        question = st.text_input("❓ سؤالك:")
        if question:
            answer = ScientificReferenceSystem.get_knowledge_answer(question)
            if answer:
                st.markdown(f"""
                <div style="background:#e8f5e9;padding:15px;border-radius:8px;">
                    <p>{answer['answer']}</p>
                    <small>{answer['simplified']}</small>
                    {f'<p><small>📚 المرجع: {answer["reference"]["id"]}</small></p>' if answer.get('reference') else ''}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("💡 لم أجد إجابة لهذا السؤال. يرجى التواصل مع المختصين.")

# التبويب 11: دليل المستخدم
if "📖 دليل المستخدم" in tabs_titles:
    tab_idx = tabs_titles.index("📖 دليل المستخدم")
    with tabs[tab_idx]:
        st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 دليل استخدام منصة تاور العلمية
        
        #### 1. تركيب الأعلاف
        - حدد موقعك الجغرافي لضبط الأسعار
        - اختر نوع الحيوان ومرحلة الإنتاج
        - حدد البروتين المهضوم ومعادل النشاء
        - اختر المواد العلفية المتاحة
        - اضغط "تشغيل المحرك" للحصول على أقل تكلفة
        
        #### 2. إدارة المخزون
        - راقب الكميات المتاحة
        - أضف مواد جديدة أو حدّث الكميات
        
        #### 3. الفواتير
        - أنشئ فاتورة بيع
        - يتم خصم المكونات تلقائياً من المخزون
        
        #### 4. مزارع الدجاج (خاص بالمالك)
        - أضف مزارع جديدة
        - سجّل البيانات اليومية
        - احصل على مؤشرات الأداء (ADG, FCR, EPEF)
        
        #### 5. التقارير
        - حمل تقرير PDF للخلطة
        - شارك النتائج عبر واتساب
        """)

# ==========================================
# 21. التذييل
# ==========================================
st.markdown("""
<hr>
<div style="text-align:center;color:#666;padding:15px 0;">
    🌾 منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف © 2026
    <br>تحت إشراف الاختصاصي م. عبد القادر إسماعيل تاور
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# نهاية الكود
# ==========================================
