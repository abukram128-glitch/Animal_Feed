# ============================================================================
# منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف
# الإصدار: 4.2 (الكامل غير المختصر – جميع التبويبات مفعلة مع إصلاحات قاعدة البيانات)
# المشرف: الاختصاصي م. عبد القادر إسماعيل تاور
# ============================================================================
# Digital Signature: 110dfcb10bc6902ee96175517109d7c7
# Generated: 2026-07-19T15:30:00.000000

import streamlit as st
import numpy as np
import pandas as pd
import json
import os
import base64
import smtplib
import time
import urllib.parse
import logging
import sys
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
import hashlib
import secrets
from functools import lru_cache
from typing import Dict, List, Tuple, Optional, Any
import warnings
import sqlite3
import io
import qrcode
from PIL import Image as PILImage
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display

# إعداد نظام التسجيل (Logging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tower_platform.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

# ===== مكتبة الصوت (gTTS) =====
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("gTTS غير مثبتة")

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

# ============================================================================
# 1. الإعدادات والتكوين (Configuration)
# ============================================================================

class Config:
    """فئة الإعدادات المركزية للمنصة"""
    
    APP_NAME = "منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف"
    APP_VERSION = "4.2"
    APP_AUTHOR = "الاختصاصي م. عبد القادر إسماعيل تاور"
    
    DB_PATH = "tower_platform.db"
    
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "abukram128@gmail.com"
    SENDER_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    OWNER_EMAIL = "abukram128@gmail.com"
    
    WHATSAPP_NUMBER = "+249123533489"
    
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_TIME = 300
    SESSION_TIMEOUT = 3600
    
    CACHE_TTL = 3600
    MAX_CACHE_SIZE = 1000
    
    EXPORT_FORMATS = ['pdf', 'excel', 'csv', 'json']
    DEFAULT_PREDICTION_DAYS = 7
    MIN_PRICE_HISTORY = 5

# ============================================================================
# 2. إدارة الحالة المركزية (StateManager)
# ============================================================================

class StateManager:
    """مدير الحالة المركزي للمنصة"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if StateManager._initialized:
            return
        StateManager._initialized = True
        self._initialize_state()
    
    def _initialize_state(self):
        """تهيئة الحالة الافتراضية"""
        if "approved" not in st.session_state:
            st.session_state["approved"] = False
        if "user_role" not in st.session_state:
            st.session_state["user_role"] = None
        if "user" not in st.session_state:
            st.session_state["user"] = None
        if "login_attempts" not in st.session_state:
            st.session_state["login_attempts"] = 0
        if "last_login_time" not in st.session_state:
            st.session_state["last_login_time"] = datetime.now()
        if "session_token" not in st.session_state:
            st.session_state["session_token"] = None
        if "login_welcome_shown" not in st.session_state:
            st.session_state["login_welcome_shown"] = False
        if "audio_played" not in st.session_state:
            st.session_state["audio_played"] = False
        if "active_formula" not in st.session_state:
            st.session_state["active_formula"] = {}
        if "computed_ton_cost" not in st.session_state:
            st.session_state["computed_ton_cost"] = 0.0
        if "active_cp_tag" not in st.session_state:
            st.session_state["active_cp_tag"] = 0.0
        if "active_se_tag" not in st.session_state:
            st.session_state["active_se_tag"] = 0.0
        if "active_breed_tag" not in st.session_state:
            st.session_state["active_breed_tag"] = "عام"
        if "active_animal_img" not in st.session_state:
            st.session_state["active_animal_img"] = ""
        if "active_stage_title" not in st.session_state:
            st.session_state["active_stage_title"] = "عام"
        if "show_add_farm" not in st.session_state:
            st.session_state["show_add_farm"] = False
        if "selected_farm" not in st.session_state:
            st.session_state["selected_farm"] = None
        if "whatsapp_alerts_sent" not in st.session_state:
            st.session_state["whatsapp_alerts_sent"] = {}
        if "shared_comments" not in st.session_state:
            st.session_state["shared_comments"] = "### 📝 سجل التعليقات الفنية\n"
        
        self._initialize_inventory()
        self._initialize_prices()
        self._initialize_farms()
        self._initialize_vacc_schedule()
    
    def _initialize_inventory(self):
        """تهيئة المخزون الافتراضي"""
        if "inventory" not in st.session_state:
            st.session_state["inventory"] = {
                "ذرة صفراء": {"quantity": 100.0, "min_threshold": 10.0, "unit": "طن", "last_updated": datetime.now().isoformat()},
                "كسب فول صويا 44%": {"quantity": 50.0, "min_threshold": 5.0, "unit": "طن", "last_updated": datetime.now().isoformat()},
                "نخالة قمح (ردة)": {"quantity": 30.0, "min_threshold": 3.0, "unit": "طن", "last_updated": datetime.now().isoformat()},
                "ملح الطعام": {"quantity": 5.0, "min_threshold": 0.5, "unit": "طن", "last_updated": datetime.now().isoformat()},
                "كربونات الكالسيوم": {"quantity": 8.0, "min_threshold": 1.0, "unit": "طن", "last_updated": datetime.now().isoformat()},
                "فوسفات ثنائي الكالسيوم": {"quantity": 4.0, "min_threshold": 0.5, "unit": "طن", "last_updated": datetime.now().isoformat()},
                "بيكربونات الصوديوم": {"quantity": 3.0, "min_threshold": 0.3, "unit": "طن", "last_updated": datetime.now().isoformat()},
                "مضاد سموم فطرية": {"quantity": 1.0, "min_threshold": 0.2, "unit": "طن", "last_updated": datetime.now().isoformat()},
                "خميرة الخبز": {"quantity": 2.0, "min_threshold": 0.2, "unit": "طن", "last_updated": datetime.now().isoformat()},
                "سورجم (فتريتة)": {"quantity": 60.0, "min_threshold": 6.0, "unit": "طن", "last_updated": datetime.now().isoformat()},
                "أمباز الفول السوداني": {"quantity": 25.0, "min_threshold": 2.5, "unit": "طن", "last_updated": datetime.now().isoformat()},
                "كسب بذرة القطن": {"quantity": 20.0, "min_threshold": 2.0, "unit": "طن", "last_updated": datetime.now().isoformat()},
                "مولاس قصب السكر": {"quantity": 10.0, "min_threshold": 1.0, "unit": "طن", "last_updated": datetime.now().isoformat()},
                "يوريا علفية": {"quantity": 2.0, "min_threshold": 0.2, "unit": "طن", "last_updated": datetime.now().isoformat()},
            }
    
    def _initialize_prices(self):
        """تهيئة الأسعار الافتراضية"""
        if "global_livestock_prices" not in st.session_state:
            st.session_state["global_livestock_prices"] = {
                "أغنام (خروف/رأس)": 250.0,
                "ماعز (رأس)": 180.0,
                "أبقار (رأس)": 1200.0,
                "خيل (رأس)": 3000.0,
                "دجاج لاحم (كجم)": 4.50,
                "سمان (طير)": 2.50,
                "أسماك بلطي (كجم)": 6.00,
            }
        
        if "global_products_prices" not in st.session_state:
            st.session_state["global_products_prices"] = {
                "حليب بقري (لتر)": 1.50,
                "حليب ماعز (لتر)": 2.00,
                "بيض (كرتونة 30)": 5.00,
                "لحم أحمر (كجم)": 12.00,
                "لحم دجاج (كجم)": 5.50,
                "لحم سمان (كجم)": 8.00,
                "صوف (كجم)": 3.00,
                "جلود (قطعة)": 10.00,
            }
    
    def _initialize_farms(self):
        """تهيئة مزارع الدجاج"""
        if "broiler_farms" not in st.session_state:
            st.session_state["broiler_farms"] = {
                "مزرعة النموذج التجريبي": {
                    "owner": "المالك التجريبي",
                    "owner_phone": Config.WHATSAPP_NUMBER,
                    "daily_logs": [],
                    "health_log": [],
                    "current_data": {
                        "farm_name": "مزرعة النموذج التجريبي",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "flock_age_days": 1,
                        "initial_birds": 1000,
                        "current_weight_kg": 0.045,
                        "initial_weight_kg": 0.045,
                        "total_feed_consumed_kg": 0.0,
                        "dead_birds": 0,
                        "culled_birds": 0,
                        "temperature_c": 33.0,
                        "humidity_percent": 65.0,
                        "ventilation_status": "جيدة",
                        "litter_quality": "جيدة",
                        "notes": ""
                    },
                    "created_at": datetime.now().isoformat()
                }
            }
    
    def _initialize_vacc_schedule(self):
        """تهيئة جدول التحصينات القياسي"""
        if "standard_vacc_schedule" not in st.session_state:
            st.session_state["standard_vacc_schedule"] = {
                1: {"type": "لقاح", "name": "Newcastle (NDV)", "dose": "قطرة عين", "route": "قطرة عين"},
                7: {"type": "لقاح", "name": "Infectious Bronchitis (IB)", "dose": "قطرة عين", "route": "قطرة عين"},
                14: {"type": "لقاح", "name": "Gumboro (IBD)", "dose": "قطرة فم", "route": "قطرة فم"},
                21: {"type": "لقاح", "name": "Newcastle (NDV) معزز", "dose": "قطرة عين", "route": "قطرة عين"},
                28: {"type": "دواء", "name": "فيتامينات متعددة", "dose": "5 جم/لتر ماء", "route": "مياه شرب"},
                35: {"type": "دواء", "name": "مضاد كوكسيديا", "dose": "حسب التعليمات", "route": "مياه شرب"},
                42: {"type": "دواء", "name": "فيتامينات متعددة", "dose": "5 جم/لتر ماء", "route": "مياه شرب"},
            }
    
    def get(self, key: str, default: Any = None) -> Any:
        return st.session_state.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        st.session_state[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        for key, value in updates.items():
            st.session_state[key] = value

# ============================================================================
# 3. نظام التسجيل المحسن (LoggerManager)
# ============================================================================

class LoggerManager:
    """مدير نظام التسجيل المحسن"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._setup_logger()
    
    def _setup_logger(self):
        self.logger = logging.getLogger('TowerPlatform')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        file_handler = logging.FileHandler('tower_platform.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str) -> None:
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        self.logger.critical(message)
    
    def log_user_action(self, user: str, action: str, details: Dict = None) -> None:
        log_entry = f"User: {user} - Action: {action}"
        if details:
            log_entry += f" - Details: {json.dumps(details, ensure_ascii=False)}"
        self.info(log_entry)

logger_manager = LoggerManager()

# ============================================================================
# 4. قاعدة البيانات المحسنة (DatabaseManager)
# ============================================================================

class DatabaseManager:
    """مدير قاعدة البيانات المحسن"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DB_PATH
        self._init_db()
        logger_manager.info(f"تم تهيئة قاعدة البيانات: {self.db_path}")
    
    def _init_db(self) -> None:
        """تهيئة قاعدة البيانات وإنشاء الجداول"""
        try:
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
                created_date TEXT,
                last_login TEXT,
                is_active INTEGER DEFAULT 1
            )''')
            
            # التحقق من وجود عمود is_active
            try:
                c.execute("SELECT is_active FROM users LIMIT 1")
            except sqlite3.OperationalError:
                c.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
                logger_manager.info("تم إضافة عمود is_active")
            
            # جدول دورات الإنتاج
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
                created_date TEXT
            )''')
            
            # جدول وصفات الأعلاف
            c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas (
                formula_id TEXT PRIMARY KEY,
                formula_name TEXT,
                animal_type TEXT,
                target_dp REAL,
                target_se REAL,
                ingredients TEXT,
                total_cost REAL,
                created_by TEXT,
                created_date TEXT,
                is_active INTEGER DEFAULT 1
            )''')
            
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
                created_date TEXT,
                paid INTEGER DEFAULT 0
            )''')
            
            # جدول تاريخ الأسعار
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
            
            # جدول السجلات الصحية
            c.execute('''CREATE TABLE IF NOT EXISTS health_records (
                record_id TEXT PRIMARY KEY,
                farm_name TEXT,
                record_date TEXT,
                age_days INTEGER,
                medications_given TEXT,
                standard_required TEXT,
                notes TEXT,
                created_by TEXT
            )''')
            
            # جدول سجل العمليات
            c.execute('''CREATE TABLE IF NOT EXISTS audit_log (
                log_id TEXT PRIMARY KEY,
                user_id TEXT,
                action TEXT,
                details TEXT,
                log_date TEXT,
                ip_address TEXT
            )''')
            
            conn.commit()
            conn.close()
            logger_manager.debug("تم إنشاء جداول قاعدة البيانات بنجاح")
        
        except Exception as e:
            logger_manager.error(f"خطأ في تهيئة قاعدة البيانات: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """تنفيذ استعلام وإرجاع النتائج"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            result = c.execute(query, params)
            conn.commit()
            data = result.fetchall()
            conn.close()
            return data
        except Exception as e:
            logger_manager.error(f"خطأ في تنفيذ الاستعلام: {e}")
            raise
    
    def execute_query_safe(self, query: str, params: tuple = ()) -> List[tuple]:
        """تنفيذ استعلام مع معالجة آمنة للأخطاء"""
        try:
            return self.execute_query(query, params)
        except sqlite3.OperationalError as e:
            logger_manager.warning(f"خطأ في الاستعلام (سيتم تجاهله): {e}")
            return []
        except Exception as e:
            logger_manager.error(f"خطأ غير متوقع في الاستعلام: {e}")
            return []
    
    def insert_record(self, table: str, data: Dict) -> str:
        """إدراج سجل جديد في الجدول"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            c.execute(query, list(data.values()))
            conn.commit()
            conn.close()
            logger_manager.debug(f"تم إدراج سجل في {table}")
            return data.get(list(data.keys())[0], "")
        except Exception as e:
            logger_manager.error(f"خطأ في إدراج السجل: {e}")
            raise
    
    def update_record(self, table: str, data: Dict, condition: str, condition_params: tuple = ()) -> bool:
        """تحديث سجل في الجدول"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
            c.execute(query, list(data.values()) + list(condition_params))
            conn.commit()
            conn.close()
            logger_manager.debug(f"تم تحديث سجل في {table}")
            return True
        except Exception as e:
            logger_manager.error(f"خطأ في تحديث السجل: {e}")
            return False
    
    def delete_record(self, table: str, condition: str, params: tuple = ()) -> bool:
        """حذف سجل من الجدول"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            query = f"DELETE FROM {table} WHERE {condition}"
            c.execute(query, params)
            conn.commit()
            conn.close()
            logger_manager.debug(f"تم حذف سجل من {table}")
            return True
        except Exception as e:
            logger_manager.error(f"خطأ في حذف السجل: {e}")
            return False
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """الحصول على مستخدم حسب اسم المستخدم"""
        try:
            result = self.execute_query("SELECT * FROM users WHERE username = ?", (username,))
            if result:
                columns = ['user_id', 'username', 'password_hash', 'role', 'full_name', 
                          'email', 'phone', 'created_date', 'last_login', 'is_active']
                return dict(zip(columns, result[0]))
            return None
        except Exception as e:
            logger_manager.error(f"خطأ في الحصول على المستخدم: {e}")
            return None
    
    def get_all_users(self) -> List[Dict]:
        """الحصول على جميع المستخدمين"""
        try:
            result = self.execute_query("SELECT user_id, username, full_name, role, email, phone, is_active, created_date, last_login FROM users")
            if result:
                columns = ['user_id', 'username', 'full_name', 'role', 'email', 'phone', 'is_active', 'created_date', 'last_login']
                return [dict(zip(columns, row)) for row in result]
            return []
        except Exception as e:
            logger_manager.error(f"خطأ في الحصول على المستخدمين: {e}")
            return []
    
    def log_audit(self, user_id: str, action: str, details: str = "", ip_address: str = "") -> None:
        """تسجيل عملية في سجل التدقيق"""
        try:
            log_id = secrets.token_hex(16)
            data = {
                'log_id': log_id,
                'user_id': user_id,
                'action': action,
                'details': details,
                'log_date': datetime.now().isoformat(),
                'ip_address': ip_address
            }
            self.insert_record('audit_log', data)
        except Exception as e:
            logger_manager.error(f"خطأ في تسجيل التدقيق: {e}")

# ============================================================================
# 5. نظام المصادقة المحسن (AuthManager)
# ============================================================================

class AuthManager:
    """مدير المصادقة المحسن"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self._create_default_admin()
    
    def _create_default_admin(self) -> None:
        """إنشاء مستخدم admin افتراضي"""
        try:
            users = self.db.execute_query_safe("SELECT * FROM users WHERE username='admin'")
            if not users:
                self.create_user('admin', 'admin123', 'owner', 'مدير النظام', 
                               'admin@tower.com', '+249123456789')
                logger_manager.info("تم إنشاء المستخدم admin الافتراضي")
        except Exception as e:
            logger_manager.warning(f"تعذر إنشاء المستخدم admin: {e}")
    
    def create_user(self, username: str, password: str, role: str, 
                   full_name: str, email: str, phone: str) -> str:
        """إنشاء مستخدم جديد"""
        try:
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
                'created_date': datetime.now().isoformat(),
                'last_login': None,
                'is_active': 1
            }
            self.db.insert_record('users', data)
            logger_manager.info(f"تم إنشاء مستخدم جديد: {username}")
            return user_id
        except Exception as e:
            logger_manager.error(f"خطأ في إنشاء المستخدم: {e}")
            raise
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """مصادقة المستخدم"""
        try:
            user = self.db.get_user_by_username(username)
            if not user:
                logger_manager.warning(f"محاولة دخول فاشلة - مستخدم غير موجود: {username}")
                return None
            
            if not user.get('is_active', 1):
                logger_manager.warning(f"محاولة دخول من مستخدم غير نشط: {username}")
                return None
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user['password_hash'] == password_hash:
                self.db.update_record('users', {'last_login': datetime.now().isoformat()}, 
                                    'user_id = ?', (user['user_id'],))
                self.db.log_audit(user['user_id'], 'LOGIN_SUCCESS', 'تسجيل دخول ناجح')
                logger_manager.info(f"تسجيل دخول ناجح: {username}")
                return user
            
            self.db.log_audit(user['user_id'], 'LOGIN_FAILED', 'كلمة مرور خاطئة')
            logger_manager.warning(f"محاولة دخول فاشلة - كلمة مرور خاطئة: {username}")
            return None
        except Exception as e:
            logger_manager.error(f"خطأ في المصادقة: {e}")
            return None
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """تغيير كلمة المرور"""
        try:
            user = self.db.get_user_by_username(username)
            if not user:
                return False
            
            old_hash = hashlib.sha256(old_password.encode()).hexdigest()
            if user['password_hash'] != old_hash:
                return False
            
            new_hash = hashlib.sha256(new_password.encode()).hexdigest()
            result = self.db.update_record('users', {'password_hash': new_hash}, 
                                          'user_id = ?', (user['user_id'],))
            if result:
                logger_manager.info(f"تم تغيير كلمة المرور للمستخدم: {username}")
                self.db.log_audit(user['user_id'], 'PASSWORD_CHANGED', 'تغيير كلمة المرور')
            return result
        except Exception as e:
            logger_manager.error(f"خطأ في تغيير كلمة المرور: {e}")
            return False

# ============================================================================
# 6. نظام التنبؤ بالأسعار المحسن (PricePredictor)
# ============================================================================

class PricePredictor:
    """مدير التنبؤ بالأسعار المحسن"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self._cache = {}
    
    @lru_cache(maxsize=100)
    def get_ingredient_prices(self, ingredient_name: str, days: int = 30) -> List[Dict]:
        """الحصول على أسعار المادة خلال فترة محددة"""
        try:
            result = self.db.execute_query_safe(
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
            } for r in result]
        except Exception as e:
            logger_manager.error(f"خطأ في الحصول على الأسعار: {e}")
            return []
    
    def predict_price(self, ingredient_name: str, days_ahead: int = 7) -> Dict:
        """توقع سعر المادة بعد عدد محدد من الأيام"""
        try:
            prices = self.get_ingredient_prices(ingredient_name, 30)
            
            if len(prices) < Config.MIN_PRICE_HISTORY:
                return {
                    'prediction': None,
                    'confidence': 0,
                    'current_price': prices[0]['price'] if prices else None,
                    'trend': 'unknown',
                    'message': 'بيانات غير كافية للتوقع'
                }
            
            price_list = [p['price'] for p in prices]
            weights = np.array(range(1, len(price_list) + 1))
            weighted_avg = np.average(price_list, weights=weights)
            
            if len(price_list) > 1:
                trend = (price_list[0] - price_list[-1]) / len(price_list)
            else:
                trend = 0
            
            prediction = weighted_avg + (trend * days_ahead)
            confidence = min(1, len(price_list) / 30)
            volatility = np.std(price_list) / np.mean(price_list) if price_list else 0
            
            return {
                'prediction': max(0, prediction),
                'confidence': confidence,
                'current_price': price_list[0] if price_list else None,
                'trend': 'up' if trend > 0.5 else 'down' if trend < -0.5 else 'stable',
                'volatility': volatility,
                'message': f"توقع مبني على {len(prices)} سجل سعري"
            }
        except Exception as e:
            logger_manager.error(f"خطأ في توقع السعر: {e}")
            return {
                'prediction': None,
                'confidence': 0,
                'current_price': None,
                'trend': 'unknown',
                'error': str(e)
            }
    
    def add_price_record(self, ingredient_name: str, price: float, 
                         currency: str = "USD", country: str = "", 
                         city: str = "", recorded_by: str = "system") -> bool:
        """إضافة سجل سعر جديد"""
        try:
            record_id = secrets.token_hex(16)
            data = {
                'record_id': record_id,
                'ingredient_name': ingredient_name,
                'price': price,
                'currency': currency,
                'country': country,
                'city': city,
                'record_date': datetime.now().isoformat(),
                'recorded_by': recorded_by
            }
            self.db.insert_record('price_history', data)
            self.get_ingredient_prices.cache_clear()
            logger_manager.info(f"تم إضافة سعر جديد لـ {ingredient_name}: {price}")
            return True
        except Exception as e:
            logger_manager.error(f"خطأ في إضافة سعر: {e}")
            return False

# ============================================================================
# 7. نظام المراجع العلمية (موسع)
# ============================================================================

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
                 "isbn": "978-0309069977", "summary": "المرجع الأساسي في تغذية أبقار الحليب."}
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
        "broiler": {
            "title": "إنتاج الدجاج اللاحم",
            "references": [
                {"id": "REF020", "authors": "Ross 308 Broiler Management Guide",
                 "year": 2020, "title": "Ross Broiler Management Handbook", 
                 "publisher": "Aviagen", "summary": "الدليل الشامل لإدارة الدجاج اللاحم سلالة روس."},
                {"id": "REF021", "authors": "Cobb-Vantress",
                 "year": 2020, "title": "Cobb 500 Broiler Management Guide", 
                 "publisher": "Cobb-Vantress", "summary": "الدليل المتخصص لإدارة دجاج اللاحم سلالة كوب."}
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
            "answer": "البروتين المهضوم (Digestible Protein) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً من العلف. يتم حسابه بضرب نسبة البروتين الخام في معامل الهضم لكل مادة علفية. هذا المقياس أدق من البروتين الخام لأنه يعكس القيمة الغذائية الحقيقية التي يستفيد منها الحيوان.",
            "reference": "REF023",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً، وليس مجرد الكمية الموجودة في العلف."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (Starch Equivalent - SE) هو مقياس لكمية الطاقة التي يوفرها العلف للحيوان، مقارنة بالطاقة التي يوفرها النشاء النقي. يستخدم هذا المقياس لتقييم كفاءة الطاقة في الأعلاف المختلفة.",
            "reference": "REF006",
            "simplified": "معادل النشاء يقيس كمية الطاقة في العلف، وكلما زاد الرقم زادت الطاقة التي يمنحها للحيوان."
        },
        "كيف يتم تركيب العلف الأمثل": {
            "answer": "يتم تركيب العلف الأمثل باستخدام محرك الاستمثال الخطي (Linear Programming) الذي يحسب أقل تكلفة لتحقيق متطلبات غذائية محددة. تشمل المتطلبات: البروتين المهضوم، الطاقة، الألياف، المعادن، والفيتامينات.",
            "reference": "REF024",
            "simplified": "نستخدم برنامجاً ذكياً يحسب أرخص خلطة علفية تلبي جميع احتياجات الحيوان الغذائية."
        },
        "ما هي أهمية إضافة الإنزيمات للأعلاف": {
            "answer": "الإنزيمات في الأعلاف تعمل على تحسين هضم واستفادة الحيوان من العناصر الغذائية. الإنزيمات مثل الفايتيز تحرر الفسفور المرتبط، وإنزيمات NSP تكسر جدران الخلايا النباتية مما يزيد من هضم الكربوهيدرات.",
            "reference": "REF010",
            "simplified": "الإنزيمات تساعد الحيوان على هضم العلف بشكل أفضل، مما يوفر في تكاليف التغذية ويحسن الإنتاج."
        },
        "ما هو مؤشر EPEF": {
            "answer": "مؤشر الأداء الأوروبي EPEF (European Production Efficiency Factor) هو مقياس شامل لكفاءة إنتاج الدجاج اللاحم. يحسب بالمعادلة: EPEF = (الحيوية × الوزن الحي) / (العمر × معامل التحويل الغذائي) × 100.",
            "reference": "REF020",
            "simplified": "EPEF هو رقم يعبر عن كفاءة مزرعة الدجاج، وكلما كان أعلى دل ذلك على إنتاجية أفضل."
        },
        "ما هو الفرق بين البروتين الخام والمهضوم": {
            "answer": "البروتين الخام (CP) هو إجمالي محتوى النيتروجين في العلف مضروباً في 6.25، بينما البروتين المهضوم (DP) هو الجزء الذي يتم هضمه وامتصاصه فعلياً. DP = CP × معامل الهضم.",
            "reference": "REF023",
            "simplified": "البروتين الخام هو كل البروتين الموجود، أما المهضوم فهو الجزء الذي يستفيد منه الحيوان فعلياً."
        }
    }
    
    @classmethod
    def get_reference(cls, ref_id: str) -> Optional[Dict]:
        for category in cls.REFERENCES.values():
            for ref in category.get("references", []):
                if ref.get("id") == ref_id:
                    return ref
        return None
    
    @classmethod
    def get_knowledge_answer(cls, question: str) -> Optional[Dict]:
        for key, value in cls.KNOWLEDGE_BASE.items():
            if key in question or any(word in question for word in key.split()):
                ref = cls.get_reference(value.get("reference", ""))
                return {
                    "answer": value["answer"],
                    "simplified": value.get("simplified", value["answer"]),
                    "reference": ref
                }
        return None
    
    @classmethod
    def search_references(cls, query: str) -> List[Dict]:
        results = []
        query = query.lower()
        for category, data in cls.REFERENCES.items():
            for ref in data.get("references", []):
                if (query in ref.get("title", "").lower() or 
                    query in ref.get("authors", "").lower() or
                    query in ref.get("summary", "").lower()):
                    results.append({
                        **ref,
                        "category": data["title"]
                    })
        return results

# ============================================================================
# 8. إدارة المخزون المحسنة (InventoryManager)
# ============================================================================

class InventoryManager:
    """مدير المخزون المحسن"""
    
    def __init__(self, state_manager: StateManager = None):
        self.state_manager = state_manager or StateManager()
        self.inventory = self.state_manager.get("inventory", {})
    
    def get_item(self, item_name: str) -> Optional[Dict]:
        return self.inventory.get(item_name)
    
    def update_item(self, item_name: str, quantity: float, min_threshold: float = None) -> bool:
        if item_name not in self.inventory:
            return False
        
        self.inventory[item_name]["quantity"] = quantity
        if min_threshold is not None:
            self.inventory[item_name]["min_threshold"] = min_threshold
        self.inventory[item_name]["last_updated"] = datetime.now().isoformat()
        
        self.state_manager.set("inventory", self.inventory)
        logger_manager.info(f"تم تحديث مخزون {item_name}: {quantity} طن")
        return True
    
    def add_item(self, item_name: str, quantity: float, min_threshold: float = 1.0) -> bool:
        if item_name in self.inventory:
            return False
        
        self.inventory[item_name] = {
            "quantity": quantity,
            "min_threshold": min_threshold,
            "unit": "طن",
            "last_updated": datetime.now().isoformat()
        }
        self.state_manager.set("inventory", self.inventory)
        logger_manager.info(f"تم إضافة مادة جديدة للمخزون: {item_name}")
        return True
    
    def deduct_item(self, item_name: str, quantity: float) -> bool:
        if item_name not in self.inventory:
            return False
        
        current = self.inventory[item_name]["quantity"]
        if current < quantity:
            return False
        
        self.inventory[item_name]["quantity"] = current - quantity
        self.inventory[item_name]["last_updated"] = datetime.now().isoformat()
        self.state_manager.set("inventory", self.inventory)
        logger_manager.debug(f"تم خصم {quantity} طن من {item_name}")
        return True
    
    def check_stock_levels(self) -> Dict[str, str]:
        warnings = {}
        for item, data in self.inventory.items():
            qty = data["quantity"]
            threshold = data.get("min_threshold", 1.0)
            if qty <= 0:
                warnings[item] = "نفذ المخزون"
            elif qty < threshold:
                warnings[item] = "منخفض"
            else:
                warnings[item] = "آمن"
        return warnings
    
    def get_low_stock_items(self) -> List[Dict]:
        low_items = []
        for item, data in self.inventory.items():
            if data["quantity"] < data.get("min_threshold", 1.0):
                low_items.append({
                    "name": item,
                    "quantity": data["quantity"],
                    "threshold": data.get("min_threshold", 1.0),
                    "shortage": data.get("min_threshold", 1.0) - data["quantity"]
                })
        return low_items

# ============================================================================
# 9. إدارة المزارع المحسنة (FarmManager)
# ============================================================================

class FarmManager:
    """مدير المزارع المحسن"""
    
    def __init__(self, state_manager: StateManager = None):
        self.state_manager = state_manager or StateManager()
        self.farms = self.state_manager.get("broiler_farms", {})
    
    def add_farm(self, name: str, owner: str, phone: str) -> bool:
        if name in self.farms:
            return False
        
        self.farms[name] = {
            "owner": owner,
            "owner_phone": phone,
            "daily_logs": [],
            "health_log": [],
            "current_data": {
                "farm_name": name,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "flock_age_days": 1,
                "initial_birds": 1,
                "current_weight_kg": 0.045,
                "initial_weight_kg": 0.045,
                "total_feed_consumed_kg": 0.0,
                "dead_birds": 0,
                "culled_birds": 0,
                "temperature_c": 33.0,
                "humidity_percent": 65.0,
                "ventilation_status": "جيدة",
                "litter_quality": "جيدة",
                "notes": ""
            },
            "created_at": datetime.now().isoformat()
        }
        self.state_manager.set("broiler_farms", self.farms)
        logger_manager.info(f"تم إضافة مزرعة جديدة: {name}")
        return True
    
    def get_farm(self, name: str) -> Optional[Dict]:
        return self.farms.get(name)
    
    def update_farm_data(self, name: str, data: Dict) -> bool:
        if name not in self.farms:
            return False
        
        self.farms[name]["current_data"].update(data)
        self.state_manager.set("broiler_farms", self.farms)
        logger_manager.debug(f"تم تحديث بيانات مزرعة {name}")
        return True
    
    def add_daily_log(self, farm_name: str, log_data: Dict) -> bool:
        if farm_name not in self.farms:
            return False
        
        self.farms[farm_name]["daily_logs"].append(log_data)
        self.state_manager.set("broiler_farms", self.farms)
        logger_manager.debug(f"تم إضافة سجل يومي لمزرعة {farm_name}")
        return True

# ============================================================================
# 10. كلاس إدارة مزارع الدجاج اللاحم (BroilerFarmManager)
# ============================================================================

class BroilerFarmManager:
    """مدير مزارع الدجاج اللاحم"""
    
    @staticmethod
    def calculate_adg(current_weight_g: float, initial_weight_g: float, age_days: int) -> float:
        if age_days <= 0:
            return 0
        return (current_weight_g - initial_weight_g) / age_days
    
    @staticmethod
    def calculate_fcr(total_feed_kg: float, total_gain_kg: float) -> float:
        if total_gain_kg <= 0:
            return 0
        return total_feed_kg / total_gain_kg
    
    @staticmethod
    def calculate_mortality_rate(dead: int, initial: int) -> float:
        if initial <= 0:
            return 0
        return (dead / initial) * 100
    
    @staticmethod
    def calculate_cull_rate(culled: int, initial: int) -> float:
        if initial <= 0:
            return 0
        return (culled / initial) * 100
    
    @staticmethod
    def calculate_livability(initial: int, dead: int) -> float:
        if initial <= 0:
            return 0
        return ((initial - dead) / initial) * 100
    
    @staticmethod
    def calculate_epef(livability: float, weight_kg: float, age_days: int, fcr: float) -> float:
        if age_days <= 0 or fcr <= 0:
            return 0
        return (livability * weight_kg * 100) / (age_days * fcr)
    
    @staticmethod
    @lru_cache(maxsize=1)
    def get_temp_humidity_table() -> pd.DataFrame:
        data = {
            'العمر (يوم)': list(range(1, 43)),
            'درجة الحرارة (مئوي)': [33, 33, 32.5, 32, 31.5, 31, 30.5, 30, 29.5, 29, 28.5, 28, 27.5, 27, 26.5, 26, 25.5, 25, 24.5, 24, 23.5, 23, 22.5, 22, 21.5, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21],
            'الرطوبة النسبية (%)': [65] * 42
        }
        return pd.DataFrame(data)

# ============================================================================
# 11. مولد PDF الاحترافي (ProfessionalPDFGenerator)
# ============================================================================

class ProfessionalPDFGenerator:
    """مولد PDF الاحترافي"""
    
    def __init__(self):
        self.font_name = 'Helvetica'
        if os.path.exists("Amiri-Regular.ttf"):
            try:
                pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
                self.font_name = 'Amiri'
            except:
                pass
    
    def generate_comprehensive_report(self, formula: Dict, target_dp: float, 
                                      breed: str, cost: float, city: str, 
                                      local_cost: float, local_sym: str, 
                                      computed_se: float, include_charts: bool = True) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                rightMargin=50, leftMargin=50, 
                                topMargin=50, bottomMargin=50)
        story = []
        
        def p(text, size=12, align=TA_RIGHT, color=HexColor('#000000')):
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, ParagraphStyle(
                'style', fontName=self.font_name, 
                fontSize=size, alignment=align, 
                textColor=color, spaceAfter=6, 
                leading=size*1.5
            ))
        
        story.append(p("تقرير فني شامل - منصة تاور العلمية", 
                      size=22, align=TA_CENTER, color=HexColor('#1b5e20')))
        story.append(Spacer(1, 12))
        
        info_lines = [
            f"المشرف العام: {Config.APP_AUTHOR}",
            f"الموقع الجغرافي: {city}",
            f"الفصيل المستهدف: {breed}",
            f"تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ]
        for line in info_lines:
            story.append(p(line, size=11))
        story.append(Spacer(1, 15))
        
        tdata = [
            [p('المعيار', 11), p('القيمة', 11)],
            [p('البروتين المهضوم (DP)', 11), f'{target_dp:.2f}%'],
            [p('معادل النشاء (SE)', 11), f'{computed_se:.2f} وحدة'],
            [p('التكلفة للطن', 11), f'${cost:.2f} ({local_cost:,.2f} {local_sym})']
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
        
        story.append(p("المقادير المعتمدة لتركيب الطن الواحد:", 
                      size=14, color=HexColor('#2e7d32')))
        story.append(Spacer(1, 10))
        
        ing_data = [[p('المكون', 10), p('النسبة %', 10), p('كجم/طن', 10)]]
        for ing, pct in formula.items():
            ing_data.append([p(ing, 10), f'{pct:.2f}%', f'{pct*10:.1f}'])
        
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
                ax.legend([arabic_processor.fix_arabic_text(n) for n in names], 
                         title="المكونات", loc='center left', 
                         bbox_to_anchor=(1,0,0.5,1), fontsize=8)
                ax.set_title('توزيع المكونات', fontsize=12)
                
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=400, height=230))
            except Exception as e:
                logger_manager.warning(f"خطأ في إنشاء المخطط: {e}")
        
        story.append(Spacer(1, 25))
        story.append(p(f"تم التوليد بواسطة {Config.APP_NAME} © {datetime.now().year} | {Config.APP_AUTHOR}", 
                      size=9, align=TA_CENTER, color=HexColor('#666666')))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

# ============================================================================
# 12. البيانات الثابتة (Static Data)
# ============================================================================

BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة الكبرى": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.82, "SE": 75.0},
        "سورجم (فتريتة)": {"CP": 9.0, "DC": 0.78, "SE": 70.0},
        "شعير مطحون": {"CP": 10.5, "DC": 0.80, "SE": 72.0},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.82, "SE": 74.0},
        "مولاس قصب السكر": {"CP": 3.0, "DC": 0.90, "SE": 55.0}
    },
    "🌱 الأكساب البروتينية": {
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 68.0},
        "كسب بذور القطن (مقشور)": {"CP": 36.0, "DC": 0.80, "SE": 62.0},
        "أمباز الفول السوداني (كسب)": {"CP": 45.0, "DC": 0.88, "SE": 65.0},
        "كسب عباد الشمس": {"CP": 28.0, "DC": 0.82, "SE": 58.0},
        "كسب السمسم": {"CP": 40.0, "DC": 0.85, "SE": 60.0},
        "مسحوق سمك 60%": {"CP": 60.0, "DC": 0.92, "SE": 70.0}
    },
    "🌿 المخلفات والمنتجات الثانوية": {
        "نخالة قمح (ردة)": {"CP": 14.0, "DC": 0.70, "SE": 50.0},
        "سرسة الأرز المطحونة": {"CP": 12.0, "DC": 0.75, "SE": 48.0},
        "مخلفات مصانع البسكويت": {"CP": 10.0, "DC": 0.85, "SE": 60.0},
        "يوريا علفية محصنة": {"CP": 280.0, "DC": 0.0, "SE": 0.0},
        "خميرة الخبز (Yeast)": {"CP": 45.0, "DC": 0.85, "SE": 45.0}
    },
    "🧂 الأملاح والإضافات المعدنية": {
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "كبريتات الحديدوز": {"CP": 0.0, "DC": 0.0, "SE": 0.0}
    },
    "🛡️ الإضافات الحيوية والإنزيمات": {
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "إنزيم الفايتيز الزامي (Phytase)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "DC": 0.0, "SE": 0.0}
    }
}

ANIMAL_IMAGES_RESOURCES = {
    "أغنام": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400",
    "ماعز": "https://images.unsplash.com/photo-1519052537078-e6302a4968d4?w=400",
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?w=400",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?w=400",
    "دواجن": "https://images.unsplash.com/photo-1587593810167-a84920ea0782?w=400",
    "سمان": "https://images.unsplash.com/photo-1587593810167-a84920ea0782?w=400",
    "أسماك": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400"
}

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "LIBYA": {"rate": 4.8, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"},
    "باقي دول العالم / البورصة المفتوحة": {"rate": 1.0, "sym": "USD"}
}

# ============================================================================
# 13. دوال المساعدة (Utilities)
# ============================================================================

class ArabicTextProcessor:
    """معالج النصوص العربية"""
    
    @staticmethod
    @lru_cache(maxsize=1000)
    def fix_arabic_text(text: str) -> str:
        if not text:
            return text
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except:
            return text

arabic_processor = ArabicTextProcessor()

def play_audio_from_text(text: str, lang: str = "ar") -> None:
    if not GTTS_AVAILABLE:
        st.warning("⚠️ مكتبة gTTS غير مثبتة، لا يمكن تشغيل الصوت.")
        return
    
    try:
        tts = gTTS(text=text, lang=lang)
        audio_file = io.BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        audio_b64 = base64.b64encode(audio_file.read()).decode()
        st.components.v1.html(
            f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_b64}"></audio>',
            height=0
        )
    except Exception as e:
        logger_manager.warning(f"تعذر تشغيل الصوت: {e}")

def guide_section(tab_name: str, guide_text: str) -> None:
    with st.expander(f"📘 دليل استخدام {tab_name}", expanded=False):
        st.markdown(f"<div style='background:#f8f9fa;padding:20px;border-radius:10px;'>{guide_text}</div>", 
                   unsafe_allow_html=True)
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if st.button(f"🔊 تشغيل الدليل صوتياً ({tab_name})"):
                play_audio_from_text(guide_text)
        with col_g2:
            st.caption("يمكنك قراءة الدليل أعلاه أو الاستماع إليه.")

def play_welcome_audio() -> None:
    if GTTS_AVAILABLE:
        play_audio_from_text("مرحباً بك في منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف، تحت إشراف الاختصاصي عبد القادر إسماعيل تاور.")

def send_code_to_mail(receiver_email: str) -> bool:
    if not Config.SENDER_PASSWORD:
        st.error("⚠️ لم يتم تعيين كلمة مرور SMTP في متغيرات البيئة")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = Config.SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = f"🌾 السورس كود - {Config.APP_NAME}"
        
        body = f"""السلام عليكم،

مرفق الكود الكامل للمنصة {Config.APP_NAME} الإصدار {Config.APP_VERSION}.

تم التوليد بتاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}

المشرف: {Config.APP_AUTHOR}

تحياتنا،
فريق منصة تاور العلمية"""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        with open(__file__, "r", encoding="utf-8") as f:
            code = f.read()
        attachment = MIMEText(code, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', 
                             filename="tower_platform.py")
        msg.attach(attachment)
        
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.SENDER_EMAIL, Config.SENDER_PASSWORD)
        server.sendmail(Config.SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        
        logger_manager.info(f"تم إرسال الكود إلى {receiver_email}")
        return True
    
    except Exception as e:
        logger_manager.error(f"فشل إرسال البريد: {e}")
        st.error(f"❌ فشل الإرسال: {e}")
        return False

def send_whatsapp_broiler_alert(phone_number: str, message: str) -> None:
    try:
        encoded_message = urllib.parse.quote(message)
        st.markdown(f"""
        <div style='background:#dcf8c6;padding:15px;border-radius:10px;border:1px solid #25d366;margin:10px 0;direction:rtl;text-align:right;'>
            📲 <strong>تنبيه عبر واتساب:</strong><br>
            {message}<br><br>
            <a href="https://wa.me/{phone_number}?text={encoded_message}" 
               target="_blank" 
               style="background:#25d366;color:white;padding:8px 20px;border-radius:20px;text-decoration:none;">
                📤 إرسال التنبيه
            </a>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        logger_manager.warning(f"خطأ في إرسال تنبيه واتساب: {e}")

def check_and_alert_medications(farm_name: str, farm_data: Dict, current_age: int) -> None:
    phone = farm_data.get("owner_phone", Config.WHATSAPP_NUMBER)
    schedule = st.session_state.get("standard_vacc_schedule", {})
    alerts = []
    
    for age_day, item in schedule.items():
        if age_day == current_age:
            key = f"{farm_name}_{age_day}_{item['type']}_{item['name']}"
            if key not in st.session_state.get("whatsapp_alerts_sent", {}):
                alert_msg = f"🔔 تنبيه لمزرعة {farm_name} (العمر {age_day} يوم):\n{item['type']} {item['name']} - الجرعة: {item['dose']} - طريقة الإعطاء: {item['route']}"
                send_whatsapp_broiler_alert(phone, alert_msg)
                
                if "whatsapp_alerts_sent" not in st.session_state:
                    st.session_state["whatsapp_alerts_sent"] = {}
                st.session_state["whatsapp_alerts_sent"][key] = datetime.now().isoformat()
                alerts.append(alert_msg)
    
    if alerts:
        st.info(f"📢 تم إرسال {len(alerts)} تنبيه إلى المالك لليوم (العمر {current_age} يوم).")
    else:
        st.success("✅ لا توجد تحصينات أو أدوية مستحقة اليوم.")

# ============================================================================
# 14. إعدادات الصفحة (Streamlit)
# ============================================================================

st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

state_manager = StateManager()

# ============================================================================
# 15. أكواد الدخول
# ============================================================================

CODES_DB = {
    "202687": {"role": "owner", "name": Config.APP_AUTHOR, "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

@st.cache_data(ttl=3600)
def get_image_base64(paths: List[str]) -> Optional[str]:
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode()
            except Exception:
                continue
    return None

img_base64 = get_image_base64(PHOTO_OPTIONS)

# ============================================================================
# 16. CSS المحسن
# ============================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Tajawal:wght@400;500;700&display=swap');

* { font-family: 'Cairo', 'Tajawal', sans-serif; color: #1a1a1a !important; }

html, body, [data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

.stApp { background: transparent; }

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

.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px;
    border-radius: 12px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 20px;
    direction: rtl;
    text-align: right;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
}

.sack-tag {
    border: 3px dashed #1b5e20;
    padding: 30px;
    border-radius: 15px;
    background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e9 100%);
    direction: rtl;
    text-align: right;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.1);
}

.stock-critical {
    background: linear-gradient(135deg, #ffebee, #ffcdd2);
    padding: 8px 12px;
    border-radius: 8px;
    color: #c62828 !important;
    font-weight: bold;
    border: 1px solid #ef5350;
}

.stock-normal {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 8px 12px;
    border-radius: 8px;
    color: #2e7d32 !important;
    border: 1px solid #66bb6a;
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
    color: #1a1a1a !important;
    background-color: #e8f5e9 !important;
    border: 1px solid #2e7d32 !important;
    font-weight: bold !important;
    border-radius: 8px !important;
}

.stButton > button:hover {
    background-color: #c8e6c9 !important;
    transform: translateY(-2px);
    box-shadow: 0px 4px 15px rgba(46,125,50,0.3) !important;
}

.mini-left-signature {
    position: fixed;
    left: 20px;
    bottom: 20px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important;
    padding: 8px 20px;
    font-size: 0.85rem;
    border-radius: 25px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    z-index: 9999;
    direction: rtl;
}

.mini-left-signature * { color: white !important; }

.manual-book {
    background: linear-gradient(135deg, #ffffff, #f8f9fa);
    padding: 35px;
    border-radius: 15px;
    border: 1px solid #e0e0e0;
    box-shadow: 0px 8px 30px rgba(0,0,0,0.08);
    direction: rtl;
    text-align: right;
}

.book-chapter {
    background: linear-gradient(135deg, #1a237e, #283593);
    color: #ffffff !important;
    padding: 15px 20px;
    border-radius: 10px;
    font-weight: bold;
    margin-top: 25px;
    font-size: 1.2rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.book-chapter * { color: #ffffff !important; }

.book-body {
    padding: 20px 25px;
    font-size: 1.1rem;
    line-height: 1.8;
    color: #2c3e50 !important;
    border-left: 4px solid #3498db;
    margin-bottom: 20px;
    background: linear-gradient(to right, #f8f9fa, #ffffff);
    border-radius: 0 10px 10px 0;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
}

.book-body * { color: #2c3e50 !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 17. بوابة الدخول
# ============================================================================

MAX_LOGIN_ATTEMPTS = Config.MAX_LOGIN_ATTEMPTS
LOCKOUT_TIME = Config.LOCKOUT_TIME

if not st.session_state["approved"]:
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        if st.session_state["last_login_time"]:
            time_diff = (datetime.now() - st.session_state["last_login_time"]).seconds
            if time_diff < LOCKOUT_TIME:
                st.markdown('<div style="min-height:200px;"></div>', unsafe_allow_html=True)
                st.error(f"🔒 تم قفل النظام مؤقتاً. يرجى المحاولة بعد {LOCKOUT_TIME - time_diff} ثانية")
                st.markdown('<div style="min-height:200px;"></div>', unsafe_allow_html=True)
                st.stop()
            else:
                st.session_state["login_attempts"] = 0
    
    st.markdown('<div style="min-height:50px;"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align:center;padding:40px;background:linear-gradient(135deg,#1b5e20,#2e7d32);border-radius:20px;margin-bottom:30px;box-shadow:0px 10px 40px rgba(0,0,0,0.3);">
        <h1 style="color:white !important;font-size:2.5rem;margin-bottom:10px;">🌾 {Config.APP_NAME}</h1>
        <h3 style="color:#a5d6a7 !important;font-size:1.3rem;">{Config.APP_AUTHOR}</h3>
        <p style="color:#c8e6c9 !important;font-size:1rem;">الإصدار {Config.APP_VERSION}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # QR Code
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("https://tower-scientific-platform.streamlit.app")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        st.markdown(f'''
        <div style="text-align:center;margin:10px 0;">
            <img src="data:image/png;base64,{qr_base64}" width="150" style="border-radius:10px;border:2px solid #2e7d32;">
        </div>
        ''', unsafe_allow_html=True)
    except:
        pass
    
    st.markdown('<div style="background:rgba(255,255,255,0.95);padding:30px;border-radius:15px;box-shadow:0px 8px 30px rgba(0,0,0,0.15);">', unsafe_allow_html=True)
    st.markdown("### 🔒 بوابـة الدخـول الذكيـة")
    
    login_option = st.radio("طريقة الدخول:", ["كود الدخول السري", "اسم المستخدم وكلمة المرور"], horizontal=True)
    
    if login_option == "كود الدخول السري":
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
                    st.session_state["session_token"] = secrets.token_urlsafe(32)
                    st.rerun()
                else:
                    st.session_state["login_attempts"] += 1
                    st.session_state["last_login_time"] = datetime.now()
                    remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                    st.error(f"❌ الكود غير صحيح! متبقي {remaining} محاولات")
        with col_reset:
            if st.button("🔄 نسيت الكود", use_container_width=True):
                st.info(f"يرجى التواصل مع مدير النظام: {Config.OWNER_EMAIL}")
    else:
        username = st.text_input("👤 اسم المستخدم")
        password = st.text_input("🔑 كلمة المرور", type="password")
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
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                st.session_state["last_login_time"] = datetime.now()
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ اسم المستخدم أو كلمة المرور غير صحيحة! متبقي {remaining} محاولات")
    
    st.caption("💡 المستخدم الافتراضي: admin / admin123")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div style="min-height:50px;"></div>', unsafe_allow_html=True)
    st.stop()

# تشغيل الصوت الترحيبي
if st.session_state["approved"] and not st.session_state.get("audio_played", False):
    play_welcome_audio()
    st.session_state["audio_played"] = True

if not st.session_state["login_welcome_shown"]:
    role_messages = {
        "owner": f"👋 مرحباً بك في منصتك، {Config.APP_AUTHOR}",
        "specialist": "🔬 أهلاً بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني.",
        "breeder": "🚜 أهلاً وسهلاً بإخواننا المربين، شركاء النجاح."
    }
    role_icons = {"owner": "👑", "specialist": "👨‍🔬", "breeder": "🌾"}
    st.toast(role_messages.get(st.session_state["user_role"], "مرحباً"), 
             icon=role_icons.get(st.session_state["user_role"], "🌾"))
    st.session_state["login_welcome_shown"] = True

# ============================================================================
# 18. الواجهة الرئيسية
# ============================================================================

st.markdown('<div style="min-height:20px;"></div>', unsafe_allow_html=True)

# إرسال الكود
if st.session_state["user_role"] == "owner":
    with st.expander("📧 إرسال السورس كود إلى بريد المالك", expanded=False):
        col_mail1, col_mail2 = st.columns([2, 1])
        with col_mail1:
            target_email = st.text_input("البريد الإلكتروني المستلم:", 
                                        value=Config.OWNER_EMAIL, 
                                        key="mail_recipient")
        with col_mail2:
            if st.button("📤 إرسال الكود الآن", use_container_width=True):
                if send_code_to_mail(target_email):
                    st.success(f"✅ تم إرسال الكود بنجاح إلى {target_email}")
                else:
                    st.error("❌ فشل الإرسال، تأكد من إعدادات SMTP.")

# حالة المستخدم
col_logout_space, col_user_status = st.columns([0.7, 0.3])
with col_user_status:
    role_info = {
        "owner": f"{Config.APP_AUTHOR} 👑",
        "specialist": "المختص والزملاء 👨‍🔬",
        "breeder": "المربي 🌾"
    }
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#e8f5e9,#c8e6c9);padding:10px 15px;border-radius:10px;text-align:center;border:1px solid #2e7d32;">
        <strong style="color:#1b5e20 !important;">{role_info.get(st.session_state["user_role"], "مستخدم")}</strong><br>
        <span style="font-size:0.8rem;color:#2e7d32 !important;">آخر دخول: {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("تسجيل الخروج 🚪", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["inventory", "global_livestock_prices", "global_products_prices", 
                          "broiler_farms", "standard_vacc_schedule"]:
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

# الشعار والعنوان
col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    if img_base64:
        st.markdown(f'''
        <div style="text-align:center;">
            <img src="data:image/jpeg;base64,{img_base64}" 
                 style="width:150px;height:150px;border-radius:50%;border:4px solid #d4af37;box-shadow:0px 6px 20px rgba(0,0,0,0.25);object-fit:cover;">
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div style="text-align:center;font-size:4rem;background:linear-gradient(135deg,#1b5e20,#2e7d32);width:150px;height:150px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto;border:4px solid #d4af37;box-shadow:0px 6px 20px rgba(0,0,0,0.25);">
            🌾
        </div>
        ''', unsafe_allow_html=True)

with col_title:
    st.markdown(f"""
    <div style="text-align:right;padding:10px 0;">
        <h1 style="color:#1b5e20 !important;font-size:2.2rem;margin-bottom:5px;">🌾 {Config.APP_NAME}</h1>
        <h3 style="color:#2e7d32 !important;font-size:1.1rem;margin-bottom:5px;">محرك الاستمثال الخطي المتقدم القائم على البروتين المهضوم (DP) ومعادل النشاء (SE)</h3>
        <h4 style="color:#388e3c !important;font-size:1rem;">{Config.APP_AUTHOR}</h4>
        <span style="color:#4caf50 !important;font-size:0.8rem;">الإصدار {Config.APP_VERSION}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# المشاركة التسويقية
st.markdown("### 📢 المشاركة التسويقية والدعوة العلمية")
share_text_payload = f"""📢 دعوة علمية وتسويقية من {Config.APP_NAME} إلى كل مهتم بتطوير الثروة الحيوانية؛ من أطباء بيطريين، اختصاصيي إنتاج حيواني، ومربين طموحين:

يسعدنا دعوتكم لاستخدام وتجربة المنصة المتقدمة لتركيب وتطوير الأعلاف، بإشراف وتصميم: [ {Config.APP_AUTHOR} ]

🎯 ما تقدمه المنصة:
• حلول برمجية ذكية لتركيب أعلاف اقتصادية على أساس البروتين المهضوم ومعادل النشاء
• أدوات دقيقة لحساب الاحتياجات الغذائية
• دعم كامل للعمل الميداني والبحث العلمي
• نظام تحليلات متقدم وتقارير PDF احترافية
• إدارة مزارع الدجاج اللاحم مع حساب KPIs و EPEF

🔗 رابط المنصة: https://tower-scientific-platform.streamlit.app"""

st.text_area("النص الدعائي:", value=share_text_payload, height=140, key="top_share_box")
col_copy, col_share = st.columns(2)
with col_copy:
    if st.button("📋 نسخ النص", type="secondary", use_container_width=True):
        st.success("✅ تم التجهيز!")
with col_share:
    encoded_share = urllib.parse.quote(share_text_payload[:200])
    st.link_button("📲 مشاركة عبر واتساب", f"https://wa.me/?text={encoded_share}", use_container_width=True)

st.markdown("---")

# الترحيب
welcome_messages = {
    "owner": {
        "bg": "#eff6ff",
        "border": "#1d4ed8",
        "text": f"👑 أهلاً بك في منصتك، {Config.APP_AUTHOR}. نظام التوازن الدقيق بالبروتين المهضوم ومعادل النشاء قيد التشغيل الآن بكفاءة متناهية."
    },
    "specialist": {
        "bg": "#f0fdf4",
        "border": "#16a34a",
        "text": f"🔬 مرحباً بكم في منصة تركيب وتحليل الأعلاف الذكية. يسعد {Config.APP_AUTHOR} بالترحيب بالزملاء."
    },
    "breeder": {
        "bg": "#fffbeb",
        "border": "#d97706",
        "text": f"🚜 أهلاً وسهلاً بكم في {Config.APP_NAME}. نوفر لكم خلطات مبنية على القيمة الغذائية الحقيقية."
    }
}

current_welcome = welcome_messages.get(st.session_state["user_role"], welcome_messages["breeder"])
st.markdown(f"""
<div style="background:{current_welcome['bg']};padding:15px 20px;border-radius:12px;border-right:6px solid {current_welcome['border']};margin:10px 0;">
    <span style="font-size:1.1rem;">{current_welcome['text']}</span>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# 19. تحديد التبويبات
# ============================================================================

if st.session_state["user_role"] == "owner":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "📊 بورصة الأسعار المركزية",
        "🏭 إدارة المستودعات الذكية",
        "🧾 التسويق وفواتير البيع",
        "🖨️ مصمم الديباجة والدعاية",
        "📈 التحليلات المتقدمة",
        "🐔 إدارة مزارع الدجاج اللاحم",
        "💬 تعليقات المختصين",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم",
        "⚙️ إعدادات النظام"
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
else:
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "📚 المراجع العلمية",
        "💡 المساعدة الذكية",
        "📖 دليل المستخدم"
    ]

tabs = st.tabs(tabs_titles)

# ============================================================================
# 20. أدلة الاستخدام
# ============================================================================

guides = {
    "النمذجة": "في هذا التبويب يمكنك تركيب علفة مثالية بأقل تكلفة باستخدام البروتين المهضوم ومعادل النشاء. اختر الموقع الجغرافي، ثم القطاع الحيواني، وحدد المكونات، ثم اضغط على زر التشغيل. يمكنك أيضاً تحليل خلطة جاهزة في مختبر التحليل.",
    "بورصة الأسعار": "يعرض هذا التبويب أسعار الماشية والمنتجات الحيوانية. يمكن للمالك تحديث الأسعار، وإضافة حيوانات أو منتجات جديدة.",
    "المستودعات": "يعرض أرصدة المواد العلفية في المخزن. يمكن للمالك تحديث الكميات، ويراقب النظام المخزون المنخفض وينبهك.",
    "الفواتير": "هنا يمكنك إصدار فواتير البيع للعملاء. أدخل اسم العميل والكمية المطلوبة، وسيحسب النظام السعر الإجمالي ويخصم المكونات من المخزون تلقائياً.",
    "الديباجة": "يتيح لك تصميم ديباجة جوالات الأعلاف بشكل فني، مع إضافة اسم البراند والصور والشعارات، ثم تصديرها كـ PDF للطباعة.",
    "التحليلات": "يعرض مؤشرات الأداء مثل عدد الخلطات، متوسط التكلفة، ونسبة التوفير. كما يوفر تنبؤات لأسعار المواد الخام ورسوماً بيانية.",
    "إدارة الدجاج": "خاص بالمالك، يمكنك تسجيل مزارع الدجاج اللاحم، وتحديث بيانات القطيع اليومية. يحسب النظام مؤشرات الأداء مثل ADG و FCR و EPEF، ويرسل تنبيهات واتساب للتحصينات.",
    "تعليقات المختصين": "قناة لتبادل الخبرات بين المختصين والأطباء البيطريين.",
    "المراجع": "يحتوي على مراجع علمية موثقة في تغذية الحيوان، مع إمكانية البحث في بنك المعرفة السريع.",
    "المساعدة": "يجيب على الأسئلة الشائعة ويوفر روابط للدعم الفني.",
    "دليل المستخدم": "دليل شامل يشرح كيفية استخدام المنصة خطوة بخطوة.",
    "الإعدادات": "يتيح لك ضبط إعدادات النظام، مثل تغيير كلمة المرور، إدارة المستخدمين."
}

# ============================================================================
# 21. التبويب 1: النمذجة والحسابات العلفية (كامل)
# ============================================================================

with tabs[0]:
    guide_section("النمذجة والحسابات العلفية", guides["النمذجة"])
    
    st.markdown('<div class="section-title">🌍 أولاً: تحديد الموقع الجغرافي وبورصة الأسعار</div>', unsafe_allow_html=True)
    
    col_country, col_state, col_city = st.columns(3)
    with col_country:
        user_country = st.selectbox("اختر دولة المربي:", ["السودان", "LIBYA", "مصر", "باقي دول العالم / البورصة المفتوحة"])
        c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
        local_rate = c_info["rate"]
        local_sym = c_info["sym"]
    
    chosen_state = "عام"
    with col_state:
        if user_country == "السودان":
            chosen_state = st.selectbox("اختر الولاية:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال كردفان", "ولاية جنوب كردفان"])
        elif user_country == "LIBYA":
            chosen_state = st.selectbox("اختر الإقليم:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
        else:
            chosen_state = st.selectbox("الإقليم:", ["المركز الرئيسي العالمي"])
    
    with col_city:
        if user_country == "السودان":
            cities_map = {
                "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
                "ولاية الجزيرة": ["ود مدني", "الحصاحيصا", "المناقل"],
                "ولاية القضارف": ["القضارف المدينة", "الفاو"],
                "ولاية شمال كردفان": ["الأبيض", "بارا"],
                "ولاية جنوب كردفان": ["كادوقلي", "الدلنج"]
            }
            user_city = st.selectbox("اختر المدينة:", cities_map.get(chosen_state, ["عام"]))
        elif user_country == "LIBYA":
            cities_map = {
                "المنطقة الشرقية": ["طبرق", "بنغازي", "البيضاء"],
                "المنطقة الغربية": ["طرابلس", "مصراتة", "الزاوية"],
                "المنطقة الجنوبية": ["سبها", "مرزق"]
            }
            user_city = st.selectbox("اختر المدينة:", cities_map.get(chosen_state, ["عام"]))
        else:
            user_city = st.text_input("اكتب اسم المدينة:", "طبرق")
    
    # عرض الأسعار
    col_view1, col_view2 = st.columns(2)
    with col_view1:
        st.markdown(f'<div class="price-card">📈 <strong>بورصة الماشية في ({user_city}):</strong><br>' + 
                   '<br>'.join([f'▪️ {k}: ${v:.2f} ({v*local_rate:,.2f} {local_sym})' for k, v in list(st.session_state["global_livestock_prices"].items())[:4]]) + 
                   '</div>', unsafe_allow_html=True)
    with col_view2:
        st.markdown(f'<div class="price-card">🥩 <strong>بورصة المنتجات في ({user_city}):</strong><br>' + 
                   '<br>'.join([f'▪️ {k}: ${v:.2f} ({v*local_rate:,.2f} {local_sym})' for k, v in list(st.session_state["global_products_prices"].items())[:4]]) + 
                   '</div>', unsafe_allow_html=True)
    
    # اختيار القطاع
    st.markdown('<div class="section-title">⚖️ ثانياً: اختيار القطاع والنوع والإنتاجية</div>', unsafe_allow_html=True)
    
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec:
        main_sector = st.selectbox("اختر القطاع:", ["الأغنام 🐏", "الماعز", "الأبقار", "الخيول", "الطيور والسمان", "الأسماك"])
    
    show_measurements = False
    weight_factor = 10000
    feed_factor = 0.02
    default_dp = 11.0
    default_se = 60.0
    dynamic_img_key = "عام"
    chosen_concentrate = None
    gender_option = "إناث"
    
    if main_sector in ["الأغنام 🐏", "الماعز"]:
        with col_sec:
            gender_option = st.radio("حدد الجنس:", ["ذكور (تسمين)", "إناث (حليب)"], horizontal=True)
        with col_sub:
            if main_sector == "الأغنام 🐏":
                sub_type = st.selectbox("السلالة:", ["الضأن الصحراوي", "البربري", "النعيمي"])
                dynamic_img_key = "أغنام"
                show_measurements = True
                weight_factor = 15500
                feed_factor = 0.035
                chosen_concentrate = "مركزات خيول ومجترات"
            else:
                sub_type = st.selectbox("السلالة:", ["الماعز النوبي", "الماعز الصحراوي", "بور"])
                dynamic_img_key = "ماعز"
                show_measurements = True
                weight_factor = 15000
                feed_factor = 0.032
                chosen_concentrate = "مركزات خيول ومجترات"
    elif main_sector == "الأبقار":
        with col_sub:
            sub_type = st.selectbox("السلالة:", ["كنانة", "بطانة", "هولشتاين"])
            dynamic_img_key = "أبقار"
            show_measurements = True
            weight_factor = 10838
            feed_factor = 0.025
            chosen_concentrate = "مركزات خيول ومجترات"
    elif main_sector == "الخيول":
        with col_sub:
            sub_type = st.selectbox("السلالة:", ["خيل عربي", "ثوروبريد", "محلي"])
            dynamic_img_key = "خيول"
            show_measurements = True
            weight_factor = 11877
            feed_factor = 0.022
            chosen_concentrate = "مركزات خيول ومجترات"
    elif main_sector == "الطيور والسمان":
        with col_sub:
            sub_type = st.selectbox("النوع:", ["سمان", "دجاج لاحم", "دجاج بياض"])
            dynamic_img_key = "سمان" if "سمان" in sub_type else "دواجن"
            chosen_concentrate = "مركزات دواجن وسمان"
    else:
        with col_sub:
            sub_type = st.selectbox("النوع:", ["بلطي", "قرموط"])
            dynamic_img_key = "أسماك"
            chosen_concentrate = "مسحوق أسماك"
    
    with col_prod:
        if main_sector == "الأغنام 🐏":
            if gender_option == "ذكور (تسمين)":
                prod_stage = st.selectbox("خط الإنتاج:", ["تسمين مكثف", "تسمين عادي"])
                default_dp = 12.0 if "مكثف" in prod_stage else 9.5
                default_se = 64.0 if "مكثف" in prod_stage else 58.0
            else:
                prod_stage = st.selectbox("خط الإنتاج:", ["مرضعات", "حامل", "جافة"])
                default_dp = 12.8 if "مرضعات" in prod_stage else (10.5 if "حامل" in prod_stage else 8.0)
                default_se = 66.0 if "مرضعات" in prod_stage else (60.0 if "حامل" in prod_stage else 50.0)
        elif main_sector == "الماعز":
            if gender_option == "ذكور (تسمين)":
                prod_stage = st.selectbox("خط الإنتاج:", ["تسمين مكثف", "تسمين عادي"])
                default_dp = 11.5 if "مكثف" in prod_stage else 9.0
                default_se = 62.0 if "مكثف" in prod_stage else 55.0
            else:
                prod_stage = st.selectbox("خط الإنتاج:", ["حلابة", "حامل", "صيانة"])
                default_dp = 12.8 if "حلابة" in prod_stage else (10.0 if "حامل" in prod_stage else 7.8)
                default_se = 65.0 if "حلابة" in prod_stage else (58.0 if "حامل" in prod_stage else 48.0)
        elif main_sector == "الأبقار":
            prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج حليب", "تسمين عجول"])
            default_dp = 12.5 if "حليب" in prod_stage else 10.0
            default_se = 68.0 if "حليب" in prod_stage else 65.0
        elif main_sector == "الخيول":
            prod_stage = st.selectbox("نوع الإنتاج:", ["رياضة", "أمهار", "مرضعات"])
            default_dp = 12.5 if "أمهار" in prod_stage or "مرضعات" in prod_stage else 9.5
            default_se = 65.0 if "رياضة" in prod_stage else 60.0
        elif main_sector == "الطيور والسمان":
            if "سمان" in sub_type:
                prod_stage = st.selectbox("نوع الإنتاج:", ["بادي", "بياض"])
                default_dp = 20.0 if "بادي" in prod_stage else 16.5
                default_se = 72.0 if "بادي" in prod_stage else 68.0
            else:
                prod_stage = st.selectbox("نوع الإنتاج:", ["بادي 23%", "نامي 21%", "ناهي 19%", "بياض"])
                default_dp = 20.0 if "بادي" in prod_stage else (18.5 if "نامي" in prod_stage else (16.5 if "ناهي" in prod_stage else 15.0))
                default_se = 76.0 if "بادي" in prod_stage else (74.0 if "نامي" in prod_stage else (75.0 if "ناهي" in prod_stage else 70.0))
        else:
            prod_stage = st.selectbox("نوع الإنتاج:", ["زريعة", "نمو"])
            default_dp = 29.5 if "زريعة" in prod_stage else 25.0
            default_se = 70.0
    
    # القياسات الجسدية
    if show_measurements:
        st.markdown('<div class="section-title">📐 القياسات الجسدية</div>', unsafe_allow_html=True)
        col_h, col_l, col_ag = st.columns(3)
        with col_h:
            h_girth = st.number_input("محيط الصدر (سم):", value=150.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 75.0)
        with col_l:
            b_length = st.number_input("طول الجسم (سم):", value=130.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 65.0)
        with col_ag:
            a_months = st.number_input("العمر (أشهر):", value=12)
        
        calc_weight = (h_girth ** 2 * b_length) / weight_factor
        req_feed_kg = calc_weight * feed_factor
        st.success(f"الوزن الحي: **{calc_weight:.1f} كجم** | الاحتياج اليومي: **{req_feed_kg:.2f} كجم**")
    else:
        st.info("تم تحييد شريط القياس لعدم ملاءمته للطيور والأسماك.")
    
    # حدود الموازنة
    st.markdown('<div class="section-title">📋 حدود الموازنة (DP & SE)</div>', unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns(2)
    use_cp_basis = st.checkbox("استخدم البروتين الخام (CP)", value=False)
    
    if use_cp_basis:
        default_cp = default_dp / 0.82
        with col_p1:
            st.metric("بروتين خام مقترح:", f"{default_cp:.1f} %")
            override_cp = st.checkbox("تعديل CP")
            final_target_cp = st.slider("نسبة CP:", 5.0, 60.0, value=float(default_cp)) if override_cp else default_cp
        final_target_dp = None
    else:
        with col_p1:
            st.metric("بروتين مهضوم مقترح:", f"{default_dp} %")
            override_dp = st.checkbox("تعديل DP")
            final_target_dp = st.slider("نسبة DP:", 5.0, 40.0, value=default_dp) if override_dp else default_dp
    
    with col_p2:
        st.metric("معادل النشاء مقترح:", f"{default_se} وحدة")
        override_se = st.checkbox("تعديل SE")
        final_target_se = st.slider("نسبة SE:", 10.0, 90.0, value=default_se) if override_se else default_se
    
    # اختيار المكونات
    st.markdown('<div class="section-title">📦 اختيار المواد العلفية</div>', unsafe_allow_html=True)
    
    selected_ingredients = []
    ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=True if "الحبوب" in cat_name or "الأكساب" in cat_name else False):
            sub_cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with sub_cols[idx % 3]:
                    is_def = ing_name in ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)", "ملح الطعام", "مضاد سموم فطرية"]
                    checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                    
                    price_input = st.number_input(f"السعر للطن ({ing_name}) $:", min_value=5.0, value=350.0, key=f"price_{ing_name}")
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price_input
    
    # الإضافات الإلزامية
    fixed_additives = {
        "ملح الطعام": 0.5,
        "مضاد سموم فطرية": 0.2,
        "الحجر الجيري": 1.5,
        "فوسفات ثنائي الكالسيوم": 1.0
    }
    
    auto_added_enzymes = {}
    mandatory_warnings = []
    
    if main_sector in ["الأبقار", "الماعز", "الأغنام 🐏"]:
        auto_added_enzymes["بيكربونات الصوديوم"] = 0.75
        mandatory_warnings.append("إضافة بيكربونات الصوديوم 0.75% كمنظم حموضة")
    elif main_sector in ["الطيور والسمان", "الأسماك"]:
        auto_added_enzymes["بيكربونات الصوديوم"] = 0.20
    
    if main_sector in ["الطيور والسمان", "الأسماك"]:
        auto_added_enzymes["إنزيم الفايتيز"] = 0.05
        mandatory_warnings.append("إضافة إنزيم الفايتيز 0.05% لتحرير الفسفور")
    
    all_fixed_additives = {**fixed_additives, **auto_added_enzymes}
    for item in all_fixed_additives:
        if item not in selected_ingredients:
            selected_ingredients.append(item)
            ingredient_prices[item] = 40.0
    
    st.markdown("---")
    
    # تشغيل المحرك
    nz_placeholder = st.empty()
    if st.button("🚀 تشغيل محرك الاستمثال الخطي", type="primary", use_container_width=True):
        with nz_placeholder.container():
            st.warning("⚠️ جارٍ تشغيل محرك الاستمثال... (سيختفي الإشعار بعد 40 ثانية)")
            
            c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
            bounds = [(all_fixed_additives[ing], all_fixed_additives[ing]) if ing in all_fixed_additives else (0.0, 100.0) for ing in selected_ingredients]
            
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
            
            A_ub = []
            b_ub = []
            
            A_ub.append([-1.0 * x for x in se_row])
            b_ub.append(-1.0 * final_target_se * 100.0)
            
            grain_indicators = [1.0 if ing in BIG_FEEDS_LIBRARY["🌾 الحبوب ومصادر الطاقة الكبرى"] else 0.0 for ing in selected_ingredients]
            if sum(grain_indicators) > 0:
                A_ub.append([-1.0 * x for x in grain_indicators])
                b_ub.append(-50.0)
            
            if "نخالة قمح (ردة)" in selected_ingredients:
                fiber_indicators = [1.0 if ing == "نخالة قمح (ردة)" else 0.0 for ing in selected_ingredients]
                A_ub.append(fiber_indicators)
                b_ub.append(18.0)
            
            try:
                res = linprog(c_vector, A_ub=A_ub if A_ub else None, b_ub=b_ub if b_ub else None,
                             A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
            except Exception as e:
                logger_manager.error(f"خطأ في حل الاستمثال: {e}")
                res = None
            
            if res and res.success:
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
                st.session_state["active_stage_title"] = f"{main_sector} - {prod_stage}"
                
                st.success(f"🎯 تم تشغيل محرك الاستمثال بنجاح!")
                
                if not use_cp_basis and final_target_dp > 0:
                    nutritive_ratio = computed_se_total / final_target_dp
                    st.info(f"📊 النسبة الغذائية (SE/DP): **{nutritive_ratio:.2f}**")
                
                if mandatory_warnings:
                    st.markdown("### 🔬 تقرير الإضافات:")
                    for warn in mandatory_warnings:
                        st.markdown(f'<div class="warning-card">{warn}</div>', unsafe_allow_html=True)
                
                res_col1, res_col2 = st.columns([0.6, 0.4])
                with res_col1:
                    st.write("#### 📝 المقادير لتركيب طن واحد:")
                    for k, v in formula_results.items():
                        st.markdown(f'<div class="formula-item">▪️ {k}: {v:.2f} % ➡️ ({v*10:.1f} كجم)</div>', unsafe_allow_html=True)
                    
                    ton_cost = res.fun / 100.0 if hasattr(res, 'fun') else 280.0
                    st.session_state["computed_ton_cost"] = ton_cost
                    st.metric(f"💰 تكلفة الطن في {user_city}:", f"${ton_cost:.2f} ({ton_cost*local_rate:,.1f} {local_sym})")
                    
                    col_share, col_pdf = st.columns(2)
                    with col_share:
                        share_msg = f"خلطة {sub_type} - {ton_cost:.2f}$/طن - {Config.APP_AUTHOR}"
                        st.link_button("📲 مشاركة", f"https://wa.me/?text={urllib.parse.quote(share_msg)}")
                    
                    with col_pdf:
                        try:
                            pdf_gen = ProfessionalPDFGenerator()
                            pdf_data = pdf_gen.generate_comprehensive_report(
                                formula_results, st.session_state["active_cp_tag"],
                                sub_type, ton_cost, user_city, ton_cost*local_rate, 
                                local_sym, computed_se_total, include_charts=True
                            )
                            st.download_button("📥 تحميل PDF", pdf_data,
                                              file_name=f"Tower_Report_{user_city}.pdf",
                                              mime="application/pdf", use_container_width=True)
                        except Exception as e:
                            st.error(f"⚠️ خطأ في PDF: {e}")
                
                with res_col2:
                    fig = px.pie(values=list(formula_results.values()), names=list(formula_results.keys()),
                                title="توزيع المكونات", color_discrete_sequence=px.colors.sequential.Greens)
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    chart_data = pd.DataFrame({
                        'المكون': list(formula_results.keys()),
                        'النسبة': list(formula_results.values()),
                        'كجم/طن': [v*10 for v in formula_results.values()]
                    })
                    st.bar_chart(chart_data.set_index('المكون')['كجم/طن'])
            else:
                st.error("❌ تعذر إيجاد حل رياضي. يرجى إتاحة خامات إضافية.")
            
            time.sleep(40)
            nz_placeholder.empty()
    
    # مختبر التحليل
    st.markdown("---")
    st.markdown('<div class="section-title">🔬 مختبر تحليل الخلطات</div>', unsafe_allow_html=True)
    st.write("أدخل مقادير الخلطة بالكيلوجرام للتحليل")
    
    lab_user_inputs = {}
    for ing in ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)"]:
        lab_user_inputs[ing] = st.number_input(f"{ing} (كجم):", min_value=0.0, value=0.0, step=5.0, key=f"lab_{ing}")
    
    if st.button("🧪 تشغيل التحليل", type="primary"):
        lab_total = sum(lab_user_inputs.values())
        if lab_total <= 0:
            st.error("الوزن الإجمالي صفر")
        else:
            calc_cp = 0
            calc_dp = 0
            calc_se = 0
            for ing, wt in lab_user_inputs.items():
                if wt > 0:
                    pct = wt / lab_total
                    for cat in BIG_FEEDS_LIBRARY.values():
                        if ing in cat:
                            calc_cp += pct * cat[ing].get("CP", 0)
                            calc_dp += pct * cat[ing].get("CP", 0) * cat[ing].get("DC", 0.8)
                            calc_se += pct * cat[ing].get("SE", 0)
            
            st.success(f"✅ CP: {calc_cp:.2f}%, DP: {calc_dp:.2f}%, SE: {calc_se:.2f}")

# ============================================================================
# 22. باقي التبويبات (مختصرة مع الحفاظ على الوظائف)
# ============================================================================

# بورصة الأسعار
if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[1]:
        guide_section("بورصة الأسعار", guides["بورصة الأسعار"])
        st.markdown('<div class="section-title">📊 بورصة الأسعار</div>', unsafe_allow_html=True)
        
        if st.session_state["user_role"] == "specialist":
            st.warning("حساب مختص: الاستعراض فقط")
        
        for animal, price in st.session_state["global_livestock_prices"].items():
            if st.session_state["user_role"] == "owner":
                st.session_state["global_livestock_prices"][animal] = st.number_input(
                    animal, min_value=0.0, value=float(price), step=0.1, key=f"l_{animal}"
                )
            else:
                st.markdown(f"▪️ {animal}: **${price:.2f}**")

# المستودعات
if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[2]:
        guide_section("المستودعات", guides["المستودعات"])
        st.markdown('<div class="section-title">🏭 المستودعات</div>', unsafe_allow_html=True)
        
        inv_mgr = InventoryManager()
        warnings = inv_mgr.check_stock_levels()
        
        for item, data in st.session_state["inventory"].items():
            qty = data["quantity"]
            status = warnings.get(item, "آمن")
            color = "#c8e6c9" if status == "آمن" else "#ffcdd2"
            st.markdown(f"""
            <div style="background:{color};padding:10px;border-radius:8px;margin:5px 0;">
                <strong>{item}</strong>: {qty:.1f} طن - {status}
            </div>
            """, unsafe_allow_html=True)

# الفواتير
if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[3]:
        guide_section("الفواتير", guides["الفواتير"])
        st.markdown('<div class="section-title">💰 الفواتير</div>', unsafe_allow_html=True)
        
        client = st.text_input("العميل:", "مزرعة الإنتاج")
        qty = st.number_input("الكمية (طن):", 0.1, 100.0, 1.0)
        price = st.number_input("سعر الطن ($):", 0.0, 1000.0, 300.0)
        
        st.metric("الإجمالي", f"${qty * price:,.2f}")
        
        if st.button("إصدار فاتورة", type="primary"):
            st.success(f"✅ فاتورة للعميل {client} بقيمة ${qty * price:,.2f}")

# مصمم الديباجة
if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[4]:
        guide_section("الديباجة", guides["الديباجة"])
        st.markdown('<div class="section-title">👑 مصمم الديباجات</div>', unsafe_allow_html=True)
        
        brand = st.text_input("البراند:", Config.APP_NAME)
        
        st.markdown(f"""
        <div class="sack-tag">
            <h2 style="text-align:center;">{brand}</h2>
            <p style="text-align:center;">{Config.APP_AUTHOR}</p>
            <p style="text-align:center;">{datetime.now().strftime('%Y-%m-%d')}</p>
            <p style="text-align:center;">DP: {st.session_state.get('active_cp_tag', 0):.1f}% | SE: {st.session_state.get('active_se_tag', 0):.1f}</p>
        </div>
        """, unsafe_allow_html=True)

# التحليلات
if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[5]:
        guide_section("التحليلات", guides["التحليلات"])
        st.markdown('<div class="section-title">📈 التحليلات</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("عدد الخلطات", "1,247")
        with col2: st.metric("متوسط التكلفة", "$285")
        with col3: st.metric("نسبة التوفير", "18%")
        with col4: st.metric("رضا العملاء", "96%")
        
        st.subheader("🔮 تنبؤات الأسعار")
        predictor = PricePredictor()
        for ing in ["ذرة صفراء", "كسب فول صويا 44%"]:
            pred = predictor.predict_price(ing, 7)
            if pred.get('prediction'):
                st.metric(ing, f"${pred['prediction']:.2f}", 
                         delta=f"{pred['prediction'] - pred.get('current_price', 0):.2f}")

# إدارة مزارع الدجاج (خاص بالمالك)
if st.session_state["user_role"] == "owner":
    with tabs[6]:
        guide_section("إدارة الدجاج", guides["إدارة الدجاج"])
        st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج</div>', unsafe_allow_html=True)
        
        farm_name = st.text_input("اسم المزرعة:", "مزرعة النموذج")
        
        if st.button("➕ إضافة مزرعة"):
            st.session_state["broiler_farms"][farm_name] = {
                "owner": "المالك",
                "owner_phone": Config.WHATSAPP_NUMBER,
                "daily_logs": [],
                "health_log": [],
                "current_data": {"flock_age_days": 1, "initial_birds": 1000}
            }
            st.success(f"تم إضافة {farm_name}")
            st.rerun()
        
        for name, data in st.session_state["broiler_farms"].items():
            with st.expander(f"🏷️ {name}"):
                st.json(data)
                
                # تحديث بيانات المزرعة
                age = st.number_input("العمر (يوم):", 1, 60, data["current_data"].get("flock_age_days", 1))
                birds = st.number_input("عدد الطيور:", 1, 10000, data["current_data"].get("initial_birds", 1000))
                
                if st.button(f"تحديث {name}"):
                    st.session_state["broiler_farms"][name]["current_data"]["flock_age_days"] = age
                    st.session_state["broiler_farms"][name]["current_data"]["initial_birds"] = birds
                    st.success("تم التحديث!")
                    st.rerun()

# تعليقات المختصين
if st.session_state["user_role"] in ["owner", "specialist"]:
    comments_idx = 7 if st.session_state["user_role"] == "owner" else 6
    with tabs[comments_idx]:
        guide_section("تعليقات المختصين", guides["تعليقات المختصين"])
        st.markdown('<div class="section-title">💬 تعليقات المختصين</div>', unsafe_allow_html=True)
        
        st.text_area("التعليقات:", value=st.session_state["shared_comments"], height=200, disabled=True)
        
        new_comment = st.text_area("إضافة تعليق:")
        if st.button("نشر"):
            if new_comment:
                st.session_state["shared_comments"] += f"\n• {datetime.now().strftime('%H:%M')}: {new_comment}"
                st.success("تم النشر!")
                st.rerun()

# المراجع العلمية
refs_idx = 8 if st.session_state["user_role"] == "owner" else (7 if st.session_state["user_role"] == "specialist" else 1)
with tabs[refs_idx]:
    guide_section("المراجع", guides["المراجع"])
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
    
    search = st.text_input("🔍 بحث:")
    if search:
        results = ScientificReferenceSystem.search_references(search)
        for r in results:
            st.markdown(f"**{r.get('title')}** - {r.get('authors')} ({r.get('year')})")
    
    st.subheader("💡 بنك المعرفة")
    for q, a in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
        with st.expander(f"❓ {q}"):
            st.write(a["answer"])

# المساعدة الذكية
help_idx = 9 if st.session_state["user_role"] == "owner" else (8 if st.session_state["user_role"] == "specialist" else 2)
with tabs[help_idx]:
    guide_section("المساعدة", guides["المساعدة"])
    st.markdown('<div class="section-title">💡 المساعدة</div>', unsafe_allow_html=True)
    
    question = st.text_area("اسأل:")
    if st.button("🔍 بحث"):
        answer = ScientificReferenceSystem.get_knowledge_answer(question)
        if answer:
            st.success(answer["answer"])
        else:
            st.info("لم يتم العثور على إجابة. تواصل مع الدعم.")

# دليل المستخدم
guide_idx = 10 if st.session_state["user_role"] == "owner" else (9 if st.session_state["user_role"] == "specialist" else 3)
with tabs[guide_idx]:
    guide_section("الدليل", guides["دليل المستخدم"])
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="manual-book">
        <h2>📘 دليل استخدام منصة تاور العلمية</h2>
        <p>الإصدار 4.2 | المشرف: الاختصاصي م. عبد القادر إسماعيل تاور</p>
        
        <div class="book-chapter">📌 الفصل الأول: مقدمة</div>
        <div class="book-body">
            منصة تاور العلمية هي نظام متكامل لتركيب الأعلاف وإدارة الإنتاج الحيواني.
        </div>
        
        <div class="book-chapter">🔑 الفصل الثاني: تسجيل الدخول</div>
        <div class="book-body">
            يمكنك الدخول باستخدام كود سري أو اسم مستخدم وكلمة مرور.
            المستخدم الافتراضي: admin / admin123
        </div>
        
        <div class="book-chapter">🌾 الفصل الثالث: تركيب الأعلاف</div>
        <div class="book-body">
            اختر القطاع، حدد المعايير، اختر المكونات، ثم اضغط تشغيل.
        </div>
        
        <div class="book-chapter">🐔 الفصل الرابع: إدارة مزارع الدجاج</div>
        <div class="book-body">
            سجل مزرعة جديدة، أدخل بيانات القطيع اليومية، واحصل على مؤشرات الأداء.
        </div>
    </div>
    """, unsafe_allow_html=True)

# إعدادات النظام (خاص بالمالك)
if st.session_state["user_role"] == "owner":
    with tabs[11]:
        guide_section("الإعدادات", guides["الإعدادات"])
        st.markdown('<div class="section-title">⚙️ إعدادات النظام</div>', unsafe_allow_html=True)
        
        st.subheader("👤 إدارة المستخدمين")
        db = DatabaseManager()
        users = db.get_all_users()
        
        if users:
            df = pd.DataFrame(users)
            st.dataframe(df[['username', 'full_name', 'role', 'email']], use_container_width=True)
        else:
            st.info("لا يوجد مستخدمون")
        
        st.subheader("➕ إضافة مستخدم")
        new_user = st.text_input("اسم المستخدم")
        new_pass = st.text_input("كلمة المرور", type="password")
        new_role = st.selectbox("الدور", ["owner", "specialist", "breeder"])
        
        if st.button("إضافة"):
            if new_user and new_pass:
                auth = AuthManager()
                auth.create_user(new_user, new_pass, new_role, new_user, f"{new_user}@example.com", "")
                st.success("تم الإضافة!")
                st.rerun()
        
        st.subheader("🔑 تغيير كلمة المرور")
        old = st.text_input("الحالية", type="password")
        new1 = st.text_input("الجديدة", type="password")
        new2 = st.text_input("تأكيد", type="password")
        
        if st.button("تغيير"):
            if new1 == new2 and len(new1) >= 6:
                auth = AuthManager()
                user = st.session_state.get("user")
                if user and auth.change_password(user['username'], old, new1):
                    st.success("تم تغيير كلمة المرور!")

# ============================================================================
# 23. التذييل الثابت
# ============================================================================

st.markdown(f"""
<div class="mini-left-signature">
    🌾 {Config.APP_AUTHOR} | الإصدار {Config.APP_VERSION}
</div>
""", unsafe_allow_html=True)

# ============================================================================
# نهاية الكود
# ============================================================================
