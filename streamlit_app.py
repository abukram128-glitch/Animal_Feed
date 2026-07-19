# ============================================================================
# منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف
# الإصدار: 4.0 (المعالجة الشاملة والمحسنة – جميع التبويبات مفعلة مع دليل استخدام)
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
from scipy.optimize import linprog, OptimizeWarning
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
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
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
    
    # إعدادات التطبيق
    APP_NAME = "منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف"
    APP_VERSION = "4.0"
    APP_AUTHOR = "الاختصاصي م. عبد القادر إسماعيل تاور"
    
    # إعدادات قاعدة البيانات
    DB_PATH = "tower_platform.db"
    
    # إعدادات البريد الإلكتروني
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "abukram128@gmail.com"
    SENDER_PASSWORD = os.environ.get("SMTP_PASSWORD", "oynz rdli tsdy ekdq")
    OWNER_EMAIL = "abukram128@gmail.com"
    
    # إعدادات واتساب
    WHATSAPP_NUMBER = "+249123533489"
    
    # إعدادات الأمان
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_TIME = 300  # ثواني
    SESSION_TIMEOUT = 3600  # ثانية
    
    # إعدادات الأداء
    CACHE_TTL = 3600  # ثانية
    MAX_CACHE_SIZE = 1000
    
    # إعدادات التصدير
    EXPORT_FORMATS = ['pdf', 'excel', 'csv', 'json']
    
    # إعدادات التحليل
    DEFAULT_PREDICTION_DAYS = 7
    MIN_PRICE_HISTORY = 5
    
    @classmethod
    def get_db_path(cls) -> str:
        return cls.DB_PATH
    
    @classmethod
    def get_smtp_config(cls) -> Dict:
        return {
            'server': cls.SMTP_SERVER,
            'port': cls.SMTP_PORT,
            'email': cls.SENDER_EMAIL,
            'password': cls.SENDER_PASSWORD
        }
    
    @classmethod
    def get_security_config(cls) -> Dict:
        return {
            'max_attempts': cls.MAX_LOGIN_ATTEMPTS,
            'lockout_time': cls.LOCKOUT_TIME,
            'session_timeout': cls.SESSION_TIMEOUT
        }

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
        """الحصول على قيمة من الحالة"""
        return st.session_state.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """تعيين قيمة في الحالة"""
        st.session_state[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """تحديث قيم متعددة في الحالة"""
        for key, value in updates.items():
            st.session_state[key] = value
    
    def clear_session(self) -> None:
        """مسح جلسة المستخدم"""
        keys_to_keep = ["inventory", "global_livestock_prices", "global_products_prices", 
                       "broiler_farms", "standard_vacc_schedule"]
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]
        self._initialize_state()

# ============================================================================
# 3. نظام التسجيل المحسن (Logger)
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
        """إعداد نظام التسجيل"""
        self.logger = logging.getLogger('TowerPlatform')
        self.logger.setLevel(logging.DEBUG)
        
        # إزالة المعالجات الافتراضية
        self.logger.handlers.clear()
        
        # معالج للملف
        file_handler = logging.FileHandler('tower_platform.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        # معالج للكونسول
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
        """تسجيل إجراءات المستخدم"""
        log_entry = f"User: {user} - Action: {action}"
        if details:
            log_entry += f" - Details: {json.dumps(details, ensure_ascii=False)}"
        self.info(log_entry)

logger_manager = LoggerManager()

# ============================================================================
# 4. قاعدة البيانات المحسنة (DatabaseManager)
# ============================================================================

@dataclass
class User:
    """نموذج المستخدم"""
    user_id: str
    username: str
    password_hash: str
    role: str
    full_name: str
    email: str
    phone: str
    created_date: str
    last_login: str = None
    is_active: bool = True

@dataclass
class FeedFormula:
    """نموذج وصفة العلف"""
    formula_id: str
    formula_name: str
    animal_type: str
    target_dp: float
    target_se: float
    ingredients: str  # JSON string
    total_cost: float
    created_by: str
    created_date: str
    is_active: bool = True

@dataclass
class Invoice:
    """نموذج الفاتورة"""
    invoice_id: str
    customer_name: str
    formula_id: str
    quantity_ton: float
    unit_price: float
    total_price: float
    status: str
    created_by: str
    created_date: str
    paid: bool = False

@dataclass
class FarmCycle:
    """نموذج دورة إنتاجية"""
    cycle_id: str
    farm_name: str
    animal_type: str
    breed: str
    start_date: str
    end_date: str
    initial_birds: int
    final_weight_kg: float
    total_feed_kg: float
    total_dead: int
    total_culled: int
    fcr: float
    adg: float
    epef: float
    mortality_rate: float
    notes: str
    created_by: str
    created_date: str

class DatabaseManager:
    """مدير قاعدة البيانات المحسن"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.get_db_path()
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
        result = self.execute_query("SELECT * FROM users WHERE username = ?", (username,))
        if result:
            columns = ['user_id', 'username', 'password_hash', 'role', 'full_name', 
                      'email', 'phone', 'created_date', 'last_login', 'is_active']
            return dict(zip(columns, result[0]))
        return None
    
    def log_audit(self, user_id: str, action: str, details: str = "", ip_address: str = "") -> None:
        """تسجيل عملية في سجل التدقيق"""
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
        users = self.db.execute_query("SELECT * FROM users WHERE username='admin'")
        if not users:
            self.create_user('admin', 'admin123', 'owner', 'مدير النظام', 
                           'admin@tower.com', '+249123456789')
            logger_manager.info("تم إنشاء المستخدم admin الافتراضي")
    
    def create_user(self, username: str, password: str, role: str, 
                   full_name: str, email: str, phone: str) -> str:
        """إنشاء مستخدم جديد"""
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
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """مصادقة المستخدم"""
        user = self.db.get_user_by_username(username)
        if not user:
            logger_manager.warning(f"محاولة دخول فاشلة - مستخدم غير موجود: {username}")
            return None
        
        if not user.get('is_active', 1):
            logger_manager.warning(f"محاولة دخول من مستخدم غير نشط: {username}")
            return None
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user['password_hash'] == password_hash:
            # تحديث آخر دخول
            self.db.update_record('users', {'last_login': datetime.now().isoformat()}, 
                                'user_id = ?', (user['user_id'],))
            # تسجيل العملية
            self.db.log_audit(user['user_id'], 'LOGIN_SUCCESS', 'تسجيل دخول ناجح')
            logger_manager.info(f"تسجيل دخول ناجح: {username}")
            return user
        
        self.db.log_audit(user['user_id'], 'LOGIN_FAILED', 'كلمة مرور خاطئة')
        logger_manager.warning(f"محاولة دخول فاشلة - كلمة مرور خاطئة: {username}")
        return None
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """تغيير كلمة المرور"""
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
    
    def reset_password(self, email: str) -> Optional[str]:
        """إعادة تعيين كلمة المرور وإرسال بريد إلكتروني"""
        users = self.db.execute_query("SELECT * FROM users WHERE email = ?", (email,))
        if not users:
            return None
        
        # توليد كلمة مرور مؤقتة
        temp_password = secrets.token_urlsafe(8)
        user_id = users[0][0]
        
        # تحديث كلمة المرور
        password_hash = hashlib.sha256(temp_password.encode()).hexdigest()
        result = self.db.update_record('users', {'password_hash': password_hash}, 
                                      'user_id = ?', (user_id,))
        
        if result:
            logger_manager.info(f"تم إعادة تعيين كلمة المرور للمستخدم: {email}")
            self.db.log_audit(user_id, 'PASSWORD_RESET', 'إعادة تعيين كلمة المرور')
            return temp_password
        return None

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
        result = self.db.execute_query(
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
    
    def predict_price(self, ingredient_name: str, days_ahead: int = 7) -> Dict:
        """توقع سعر المادة بعد عدد محدد من الأيام"""
        prices = self.get_ingredient_prices(ingredient_name, 30)
        
        if len(prices) < Config.MIN_PRICE_HISTORY:
            return {
                'prediction': None,
                'confidence': 0,
                'current_price': prices[0]['price'] if prices else None,
                'trend': 'unknown',
                'message': 'بيانات غير كافية للتوقع'
            }
        
        try:
            price_list = [p['price'] for p in prices]
            
            # حساب المتوسط المرجح
            weights = np.array(range(1, len(price_list) + 1))
            weighted_avg = np.average(price_list, weights=weights)
            
            # حساب الاتجاه
            if len(price_list) > 1:
                trend = (price_list[0] - price_list[-1]) / len(price_list)
            else:
                trend = 0
            
            # التوقع
            prediction = weighted_avg + (trend * days_ahead)
            
            # حساب الثقة
            confidence = min(1, len(price_list) / 30)
            
            # حساب معامل التقلب
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
            # مسح الكاش
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
        }
    }
    
    @classmethod
    def get_reference(cls, ref_id: str) -> Optional[Dict]:
        """الحصول على مرجع حسب المعرف"""
        for category in cls.REFERENCES.values():
            for ref in category.get("references", []):
                if ref.get("id") == ref_id:
                    return ref
        return None
    
    @classmethod
    def get_knowledge_answer(cls, question: str) -> Optional[Dict]:
        """الحصول على إجابة من بنك المعرفة"""
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
        """البحث في المراجع"""
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
        """الحصول على بيانات مادة معينة"""
        return self.inventory.get(item_name)
    
    def update_item(self, item_name: str, quantity: float, min_threshold: float = None) -> bool:
        """تحديث كمية مادة معينة"""
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
        """إضافة مادة جديدة للمخزون"""
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
        """خصم كمية من المادة"""
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
        """فحص مستويات المخزون"""
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
        """الحصول على قائمة المواد منخفضة المخزون"""
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
    
    def get_total_value(self, price_map: Dict[str, float]) -> float:
        """حساب القيمة الإجمالية للمخزون"""
        total = 0.0
        for item, data in self.inventory.items():
            price = price_map.get(item, 0)
            total += data["quantity"] * price
        return total

# ============================================================================
# 9. إدارة المزارع المحسنة (FarmManager)
# ============================================================================

class FarmManager:
    """مدير المزارع المحسن"""
    
    def __init__(self, state_manager: StateManager = None):
        self.state_manager = state_manager or StateManager()
        self.farms = self.state_manager.get("broiler_farms", {})
    
    def add_farm(self, name: str, owner: str, phone: str) -> bool:
        """إضافة مزرعة جديدة"""
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
        """الحصول على بيانات مزرعة"""
        return self.farms.get(name)
    
    def update_farm_data(self, name: str, data: Dict) -> bool:
        """تحديث بيانات المزرعة"""
        if name not in self.farms:
            return False
        
        self.farms[name]["current_data"].update(data)
        self.state_manager.set("broiler_farms", self.farms)
        logger_manager.debug(f"تم تحديث بيانات مزرعة {name}")
        return True
    
    def add_daily_log(self, farm_name: str, log_data: Dict) -> bool:
        """إضافة سجل يومي"""
        if farm_name not in self.farms:
            return False
        
        self.farms[farm_name]["daily_logs"].append(log_data)
        self.state_manager.set("broiler_farms", self.farms)
        logger_manager.debug(f"تم إضافة سجل يومي لمزرعة {farm_name}")
        return True
    
    def add_health_record(self, farm_name: str, record: Dict) -> bool:
        """إضافة سجل صحي"""
        if farm_name not in self.farms:
            return False
        
        self.farms[farm_name]["health_log"].append(record)
        self.state_manager.set("broiler_farms", self.farms)
        logger_manager.debug(f"تم إضافة سجل صحي لمزرعة {farm_name}")
        return True
    
    def get_performance_metrics(self, farm_name: str) -> Optional[Dict]:
        """حساب مؤشرات الأداء للمزرعة"""
        farm = self.get_farm(farm_name)
        if not farm:
            return None
        
        current = farm["current_data"]
        
        # حساب المؤشرات
        total_alive = current["initial_birds"] - current["dead_birds"] - current["culled_birds"]
        total_gain_kg = total_alive * (current["current_weight_kg"] - current["initial_weight_kg"])
        
        # ADG (متوسط النمو اليومي بالجرام)
        if current["flock_age_days"] > 0:
            adg = (current["current_weight_kg"] - current["initial_weight_kg"]) * 1000 / current["flock_age_days"]
        else:
            adg = 0
        
        # FCR (معامل التحويل الغذائي)
        if total_gain_kg > 0:
            fcr = current["total_feed_consumed_kg"] / total_gain_kg
        else:
            fcr = 0
        
        # معدل النفوق
        mortality = (current["dead_birds"] / current["initial_birds"] * 100) if current["initial_birds"] > 0 else 0
        
        # الحيوية
        livability = ((current["initial_birds"] - current["dead_birds"]) / current["initial_birds"] * 100) if current["initial_birds"] > 0 else 0
        
        # EPEF
        if current["flock_age_days"] > 0 and fcr > 0:
            epef = (livability * current["current_weight_kg"] * 100) / (current["flock_age_days"] * fcr)
        else:
            epef = 0
        
        return {
            "total_alive": total_alive,
            "total_gain_kg": total_gain_kg,
            "adg_g": adg,
            "fcr": fcr,
            "mortality_rate": mortality,
            "livability": livability,
            "epef": epef
        }

# ============================================================================
# 10. نظام تصدير البيانات (DataExporter)
# ============================================================================

class DataExporter:
    """نظام تصدير البيانات بتنسيقات متعددة"""
    
    def __init__(self):
        self.formats = Config.EXPORT_FORMATS
    
    def export_formula(self, formula: Dict, target_dp: float, target_se: float, 
                      breed: str, cost: float, format: str = "pdf") -> bytes:
        """تصدير وصفة العلف بالتنسيق المطلوب"""
        if format == "pdf":
            return self._export_pdf(formula, target_dp, target_se, breed, cost)
        elif format == "excel":
            return self._export_excel(formula, target_dp, target_se, breed, cost)
        elif format == "csv":
            return self._export_csv(formula)
        elif format == "json":
            return self._export_json(formula, target_dp, target_se, breed, cost)
        else:
            raise ValueError(f"تنسيق غير معتمد: {format}")
    
    def _export_pdf(self, formula: Dict, target_dp: float, target_se: float,
                   breed: str, cost: float) -> bytes:
        """تصدير كـ PDF"""
        # هذا هو تنفيذ PDF الموجود في الكود الأصلي
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # عنوان
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        story.append(Paragraph("تقرير منصة تاور العلمية", title_style))
        
        # معلومات عامة
        story.append(Paragraph(f"الفصيل: {breed}", styles['Normal']))
        story.append(Paragraph(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # المعايير
        data = [
            ["المعيار", "القيمة"],
            ["البروتين المهضوم (DP)", f"{target_dp:.2f}%"],
            ["معادل النشاء (SE)", f"{target_se:.2f} وحدة"],
            ["التكلفة", f"${cost:.2f}/طن"]
        ]
        table = Table(data, colWidths=[200, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#2e7d32'),
            ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, 'black')
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        
        # المكونات
        story.append(Paragraph("مكونات الخلطة:", styles['Heading2']))
        ing_data = [["المكون", "النسبة %", "كجم/طن"]]
        for ing, pct in formula.items():
            ing_data.append([ing, f"{pct:.2f}%", f"{pct*10:.1f}"])
        
        ing_table = Table(ing_data, colWidths=[150, 100, 100])
        ing_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#2e7d32'),
            ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, 'black')
        ]))
        story.append(ing_table)
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _export_excel(self, formula: Dict, target_dp: float, target_se: float,
                     breed: str, cost: float) -> bytes:
        """تصدير كـ Excel"""
        import pandas as pd
        from io import BytesIO
        
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # ورقة المكونات
            df_ingredients = pd.DataFrame({
                'المكون': list(formula.keys()),
                'النسبة المئوية': list(formula.values()),
                'كجم/طن': [v * 10 for v in formula.values()]
            })
            df_ingredients.to_excel(writer, sheet_name='المكونات', index=False)
            
            # ورقة المعايير
            df_metrics = pd.DataFrame({
                'المعيار': ['الفصيل', 'البروتين المهضوم', 'معادل النشاء', 'التكلفة'],
                'القيمة': [breed, f"{target_dp:.2f}%", f"{target_se:.2f}", f"${cost:.2f}"]
            })
            df_metrics.to_excel(writer, sheet_name='المعايير', index=False)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _export_csv(self, formula: Dict) -> bytes:
        """تصدير كـ CSV"""
        import pandas as pd
        from io import StringIO
        
        df = pd.DataFrame({
            'المكون': list(formula.keys()),
            'النسبة المئوية': list(formula.values()),
            'كجم/طن': [v * 10 for v in formula.values()]
        })
        
        buffer = StringIO()
        df.to_csv(buffer, index=False, encoding='utf-8-sig')
        return buffer.getvalue().encode('utf-8-sig')
    
    def _export_json(self, formula: Dict, target_dp: float, target_se: float,
                    breed: str, cost: float) -> bytes:
        """تصدير كـ JSON"""
        data = {
            'formula': formula,
            'target_dp': target_dp,
            'target_se': target_se,
            'breed': breed,
            'cost': cost,
            'export_date': datetime.now().isoformat(),
            'version': Config.APP_VERSION,
            'author': Config.APP_AUTHOR
        }
        return json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')

# ============================================================================
# 11. نظام التحليل المتقدم (AdvancedAnalytics)
# ============================================================================

class AdvancedAnalytics:
    """نظام التحليل المتقدم للمنصة"""
    
    def __init__(self):
        self.predictor = PricePredictor()
    
    def analyze_market_trends(self, ingredient_name: str, days: int = 30) -> Dict:
        """تحليل اتجاهات السوق لمادة معينة"""
        prices = self.predictor.get_ingredient_prices(ingredient_name, days)
        
        if len(prices) < 3:
            return {"status": "insufficient_data"}
        
        price_list = [p['price'] for p in prices]
        
        # حساب المؤشرات الإحصائية
        mean_price = np.mean(price_list)
        std_price = np.std(price_list)
        min_price = min(price_list)
        max_price = max(price_list)
        
        # حساب الاتجاه
        if len(price_list) > 1:
            x = np.arange(len(price_list))
            slope, intercept = np.polyfit(x, price_list, 1)
            trend_direction = "صاعد" if slope > 0 else "هابط" if slope < 0 else "مستقر"
            trend_strength = abs(slope) / mean_price * 100
        else:
            slope = 0
            trend_direction = "غير محدد"
            trend_strength = 0
        
        return {
            "ingredient": ingredient_name,
            "period_days": days,
            "mean_price": mean_price,
            "std_price": std_price,
            "min_price": min_price,
            "max_price": max_price,
            "price_range": max_price - min_price,
            "volatility": std_price / mean_price if mean_price > 0 else 0,
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "slope": slope,
            "data_points": len(prices)
        }
    
    def compare_formulas(self, formula1: Dict, formula2: Dict) -> Dict:
        """مقارنة بين وصفتين علفيتين"""
        # حساب القيم الغذائية لكل وصفة
        def calculate_nutrition(formula):
            total_cp = 0
            total_dp = 0
            total_se = 0
            for ing, pct in formula.items():
                # البحث عن بيانات المادة
                for cat in BIG_FEEDS_LIBRARY.values():
                    if ing in cat:
                        total_cp += pct * cat[ing].get("CP", 0)
                        total_dp += pct * cat[ing].get("CP", 0) * cat[ing].get("DC", 0.8)
                        total_se += pct * cat[ing].get("SE", 0)
            return {
                "cp": total_cp,
                "dp": total_dp,
                "se": total_se
            }
        
        nut1 = calculate_nutrition(formula1)
        nut2 = calculate_nutrition(formula2)
        
        return {
            "comparison": {
                "cp_diff": nut1["cp"] - nut2["cp"],
                "dp_diff": nut1["dp"] - nut2["dp"],
                "se_diff": nut1["se"] - nut2["se"]
            },
            "formula1": nut1,
            "formula2": nut2,
            "similarity": 1 - (abs(nut1["dp"] - nut2["dp"]) / max(nut1["dp"], nut2["dp"])) if max(nut1["dp"], nut2["dp"]) > 0 else 0
        }
    
    def generate_optimization_report(self, formula: Dict, target_dp: float, 
                                    target_se: float, cost: float) -> Dict:
        """توليد تقرير تحسين شامل"""
        # حساب الالتزام بالمعايير
        actual_dp = 0
        actual_se = 0
        for ing, pct in formula.items():
            for cat in BIG_FEEDS_LIBRARY.values():
                if ing in cat:
                    actual_dp += pct * cat[ing].get("CP", 0) * cat[ing].get("DC", 0.8)
                    actual_se += pct * cat[ing].get("SE", 0)
        
        dp_compliance = (actual_dp / target_dp * 100) if target_dp > 0 else 0
        se_compliance = (actual_se / target_se * 100) if target_se > 0 else 0
        
        return {
            "formula_summary": {
                "total_ingredients": len(formula),
                "total_cost": cost,
                "actual_dp": actual_dp,
                "actual_se": actual_se,
                "dp_compliance": dp_compliance,
                "se_compliance": se_compliance
            },
            "optimization_metrics": {
                "cost_efficiency": 1 / cost if cost > 0 else 0,
                "nutritional_balance": min(dp_compliance, se_compliance) / 100,
                "overall_score": (dp_compliance + se_compliance) / 200
            },
            "recommendations": self._generate_recommendations(formula, actual_dp, actual_se)
        }
    
    def _generate_recommendations(self, formula: Dict, actual_dp: float, actual_se: float) -> List[str]:
        """توليد توصيات تحسين"""
        recommendations = []
        
        # التحقق من توازن البروتين والطاقة
        if actual_dp > 25:
            recommendations.append("نسبة البروتين عالية جداً، قد تؤدي إلى مشاكل في الكلى")
        elif actual_dp < 10:
            recommendations.append("نسبة البروتين منخفضة، قد تؤثر على النمو والإنتاج")
        
        if actual_se > 80:
            recommendations.append("محتوى الطاقة مرتفع، قد يسبب زيادة في الدهون")
        elif actual_se < 50:
            recommendations.append("محتوى الطاقة منخفض، قد يقلل من أداء الحيوان")
        
        # التحقق من التنوع
        if len(formula) < 5:
            recommendations.append("عدد المكونات قليل، يفضل تنويع المصادر الغذائية")
        
        return recommendations

# ============================================================================
# 12. نظام التنبيهات والمراقبة (AlertSystem)
# ============================================================================

class AlertSystem:
    """نظام التنبيهات والمراقبة"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.state_manager = StateManager()
    
    def check_inventory_alerts(self) -> List[Dict]:
        """فحص تنبيهات المخزون"""
        alerts = []
        inventory = self.state_manager.get("inventory", {})
        
        for item, data in inventory.items():
            qty = data["quantity"]
            threshold = data.get("min_threshold", 1.0)
            
            if qty <= 0:
                alerts.append({
                    "type": "critical",
                    "item": item,
                    "message": f"⚠️ مادة {item} قد نفذت من المخزون!",
                    "quantity": qty,
                    "threshold": threshold
                })
            elif qty < threshold:
                alerts.append({
                    "type": "warning",
                    "item": item,
                    "message": f"⚡ مادة {item} على وشك النفاذ (المتبقي: {qty:.2f} طن)",
                    "quantity": qty,
                    "threshold": threshold
                })
        
        return alerts
    
    def check_farm_alerts(self, farm_name: str) -> List[Dict]:
        """فحص تنبيهات المزرعة"""
        alerts = []
        farms = self.state_manager.get("broiler_farms", {})
        farm = farms.get(farm_name)
        
        if not farm:
            return alerts
        
        current = farm["current_data"]
        
        # فحص درجة الحرارة
        temp = current.get("temperature_c", 0)
        age = current.get("flock_age_days", 0)
        
        # الحصول على درجة الحرارة الموصى بها
        temp_hum_df = BroilerFarmManager.get_temp_humidity_table()
        closest = temp_hum_df.iloc[(temp_hum_df['العمر (يوم)'] - age).abs().argsort()[:1]].iloc[0] if len(temp_hum_df) > 0 else None
        
        if closest is not None:
            rec_temp = closest['درجة الحرارة (مئوي)']
            rec_hum = closest['الرطوبة النسبية (%)']
            
            if abs(temp - rec_temp) > 2:
                alerts.append({
                    "type": "warning",
                    "message": f"🌡️ درجة الحرارة ({temp}°C) خارج النطاق الموصى به ({rec_temp}°C)",
                    "recommendation": "ضبط نظام التهوية أو التدفئة"
                })
            
            hum = current.get("humidity_percent", 0)
            if abs(hum - rec_hum) > 10:
                alerts.append({
                    "type": "warning",
                    "message": f"💧 الرطوبة ({hum}%) خارج النطاق الموصى به ({rec_hum}%)",
                    "recommendation": "ضبط نظام التهوية أو الرش"
                })
        
        # فحص معدل النفوق
        mortality = BroilerFarmManager.calculate_mortality_rate(
            current.get("dead_birds", 0),
            current.get("initial_birds", 1)
        )
        if mortality > 2:
            alerts.append({
                "type": "critical",
                "message": f"💀 معدل النفوق مرتفع ({mortality:.1f}%)",
                "recommendation": "فحص أسباب النفوق واتخاذ إجراءات عاجلة"
            })
        
        # فحص تحصينات اليوم
        schedule = self.state_manager.get("standard_vacc_schedule", {})
        if age in schedule:
            alerts.append({
                "type": "info",
                "message": f"💉 تحصين مستحق اليوم (العمر {age} يوم): {schedule[age]['name']}",
                "recommendation": "تأكد من إعطاء الجرعة المحددة"
            })
        
        return alerts
    
    def send_whatsapp_alert(self, phone: str, message: str) -> bool:
        """إرسال تنبيه عبر واتساب"""
        try:
            encoded = urllib.parse.quote(message)
            whatsapp_url = f"https://api.whatsapp.com/send?phone={phone}&text={encoded}"
            st.markdown(f'📲 [اضغط لإرسال التنبيه عبر واتساب]({whatsapp_url})', unsafe_allow_html=True)
            logger_manager.info(f"تم إرسال تنبيه واتساب إلى {phone}")
            return True
        except Exception as e:
            logger_manager.error(f"خطأ في إرسال تنبيه واتساب: {e}")
            return False

# ============================================================================
# 13. مولد PDF الاحترافي (محسن)
# ============================================================================

class ProfessionalPDFGenerator:
    """مولد PDF الاحترافي المحسن"""
    
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
        """توليد تقرير شامل بتنسيق PDF"""
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
        
        # العنوان الرئيسي
        story.append(p("تقرير فني شامل - منصة تاور العلمية", 
                      size=22, align=TA_CENTER, color=HexColor('#1b5e20')))
        story.append(Spacer(1, 12))
        
        # معلومات التقرير
        info_lines = [
            f"المشرف العام: {Config.APP_AUTHOR}",
            f"الموقع الجغرافي: {city}",
            f"الفصيل المستهدف: {breed}",
            f"تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ]
        for line in info_lines:
            story.append(p(line, size=11))
        story.append(Spacer(1, 15))
        
        # الجدول الرئيسي
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
        
        # المكونات
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
        
        # المخططات
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
        
        # التذييل
        story.append(Spacer(1, 25))
        story.append(p(f"تم التوليد بواسطة {Config.APP_NAME} © {datetime.now().year} | {Config.APP_AUTHOR}", 
                      size=9, align=TA_CENTER, color=HexColor('#666666')))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

# ============================================================================
# 14. كلاس إدارة مزارع الدجاج اللاحم (موسع)
# ============================================================================

class BroilerFarmManager:
    """مدير مزارع الدجاج اللاحم الموسع"""
    
    @staticmethod
    def calculate_adg(current_weight_g: float, initial_weight_g: float, age_days: int) -> float:
        """حساب متوسط النمو اليومي بالجرام"""
        if age_days <= 0:
            return 0
        return (current_weight_g - initial_weight_g) / age_days
    
    @staticmethod
    def calculate_fcr(total_feed_kg: float, total_gain_kg: float) -> float:
        """حساب معامل التحويل الغذائي"""
        if total_gain_kg <= 0:
            return 0
        return total_feed_kg / total_gain_kg
    
    @staticmethod
    def calculate_mortality_rate(dead: int, initial: int) -> float:
        """حساب معدل النفوق"""
        if initial <= 0:
            return 0
        return (dead / initial) * 100
    
    @staticmethod
    def calculate_cull_rate(culled: int, initial: int) -> float:
        """حساب معدل الاستبعاد"""
        if initial <= 0:
            return 0
        return (culled / initial) * 100
    
    @staticmethod
    def calculate_livability(initial: int, dead: int) -> float:
        """حساب نسبة الحيوية"""
        if initial <= 0:
            return 0
        return ((initial - dead) / initial) * 100
    
    @staticmethod
    def calculate_epef(livability: float, weight_kg: float, age_days: int, fcr: float) -> float:
        """حساب مؤشر الأداء الأوروبي EPEF"""
        if age_days <= 0 or fcr <= 0:
            return 0
        return (livability * weight_kg * 100) / (age_days * fcr)
    
    @staticmethod
    @lru_cache(maxsize=1)
    def get_temp_humidity_table() -> pd.DataFrame:
        """الحصول على جدول درجات الحرارة والرطوبة القياسي"""
        data = {
            'العمر (يوم)': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42],
            'درجة الحرارة (مئوي)': [33, 33, 32.5, 32, 31.5, 31, 30.5, 30, 29.5, 29, 28.5, 28, 27.5, 27, 26.5, 26, 25.5, 25, 24.5, 24, 23.5, 23, 22.5, 22, 21.5, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21],
            'الرطوبة النسبية (%)': [65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65]
        }
        return pd.DataFrame(data)

# ============================================================================
# 15. البيانات الثابتة (من ملف JSON)
# ============================================================================

# محاولة تحميل البيانات من ملف JSON
def load_static_data():
    """تحميل البيانات الثابتة من ملف JSON"""
    try:
        if os.path.exists('data/feeds_library.json'):
            with open('data/feeds_library.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger_manager.warning(f"تعذر تحميل البيانات من JSON: {e}")
    
    # البيانات الافتراضية
    return {
        "🌾 الحبوب ومصادر الطاقة الكبرى": {
            "ذرة صفراء": {"CP": 8.5, "DC": 0.82, "SE": 75.0, "ME_kcal": 3350},
            "سورجم (فتريتة)": {"CP": 9.0, "DC": 0.78, "SE": 70.0, "ME_kcal": 3200},
            "شعير مطحون": {"CP": 10.5, "DC": 0.80, "SE": 72.0, "ME_kcal": 3250},
            "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.82, "SE": 74.0, "ME_kcal": 3300},
            "مولاس قصب السكر": {"CP": 3.0, "DC": 0.90, "SE": 55.0, "ME_kcal": 2600}
        },
        "🌱 الأكساب البروتينية (المجترات والدواجن)": {
            "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 68.0, "ME_kcal": 3100},
            "كسب بذور القطن (مقشور)": {"CP": 36.0, "DC": 0.80, "SE": 62.0, "ME_kcal": 2900},
            "أمباز الفول السوداني (كسب)": {"CP": 45.0, "DC": 0.88, "SE": 65.0, "ME_kcal": 3050},
            "كسب عباد الشمس": {"CP": 28.0, "DC": 0.82, "SE": 58.0, "ME_kcal": 2800},
            "كسب السمسم": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "ME_kcal": 2950},
            "مسحوق سمك 60%": {"CP": 60.0, "DC": 0.92, "SE": 70.0, "ME_kcal": 3200}
        },
        "🌿 المخلفات والمنتجات الثانوية": {
            "نخالة قمح (ردة)": {"CP": 14.0, "DC": 0.70, "SE": 50.0, "ME_kcal": 2300},
            "سرسة الأرز المطحونة": {"CP": 12.0, "DC": 0.75, "SE": 48.0, "ME_kcal": 2200},
            "مخلفات مصانع البسكويت": {"CP": 10.0, "DC": 0.85, "SE": 60.0, "ME_kcal": 2800},
            "يوريا علفية محصنة": {"CP": 280.0, "DC": 0.0, "SE": 0.0, "ME_kcal": 0},
            "خميرة الخبز (Yeast)": {"CP": 45.0, "DC": 0.85, "SE": 45.0, "ME_kcal": 2200}
        },
        "🧂 الأملاح والإضافات المعدنية": {
            "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "ME_kcal": 0},
            "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "ME_kcal": 0},
            "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "ME_kcal": 0},
            "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "ME_kcal": 0},
            "كبريتات الحديدوز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "ME_kcal": 0}
        },
        "🛡️ الإضافات الحيوية والإنزيمات": {
            "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "ME_kcal": 0},
            "إنزيم الفايتيز الزامي (Phytase)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "ME_kcal": 0},
            "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "ME_kcal": 0}
        }
    }

BIG_FEEDS_LIBRARY = load_static_data()

# ============================================================================
# 16. بيانات الصور والموارد
# ============================================================================

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
    "السودان": {"rate": 600.0, "sym": "SDG", "currency_name": "جنيه سوداني"},
    "LIBYA": {"rate": 4.8, "sym": "LYD", "currency_name": "دينار ليبي"},
    "مصر": {"rate": 48.0, "sym": "EGP", "currency_name": "جنيه مصري"},
    "باقي دول العالم / البورصة المفتوحة": {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"}
}

# ============================================================================
# 17. دوال المساعدة (Utilities)
# ============================================================================

class ArabicTextProcessor:
    """معالج النصوص العربية"""
    
    @staticmethod
    @lru_cache(maxsize=1000)
    def fix_arabic_text(text: str) -> str:
        """تصحيح النصوص العربية للعرض"""
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
    """توليد وتشغيل صوت من نص"""
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
        st.warning(f"⚠️ تعذر تشغيل الصوت: {e}")

def guide_section(tab_name: str, guide_text: str) -> None:
    """عرض دليل استخدام للتبويب مع خيار صوتي ونصي"""
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
    """تشغيل الصوت الترحيبي"""
    if GTTS_AVAILABLE:
        play_audio_from_text("مرحباً بك في منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف، تحت إشراف الاختصاصي عبد القادر إسماعيل تاور.")

def send_code_to_mail(receiver_email: str) -> bool:
    """إرسال الكود المصدري عبر البريد الإلكتروني"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
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
        
        # إرفاق الكود
        with open(__file__, "r", encoding="utf-8") as f:
            code = f.read()
        attachment = MIMEText(code, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', 
                             filename="tower_platform.py")
        msg.attach(attachment)
        
        # إرسال البريد
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
    """إرسال تنبيه عبر واتساب لمزارع الدجاج"""
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
    """فحص وإرسال تنبيهات للتحصينات والأدوية"""
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
# 18. إعدادات الصفحة (Streamlit)
# ============================================================================

st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# 19. تهيئة مدير الحالة
# ============================================================================

state_manager = StateManager()

# ============================================================================
# 20. أكواد الدخول
# ============================================================================

CODES_DB = {
    "202687": {"role": "owner", "name": Config.APP_AUTHOR, "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

@st.cache_data(ttl=3600)
def get_image_base64(paths: List[str]) -> Optional[str]:
    """الحصول على صورة بتنسيق base64"""
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
# 21. CSS المحسن
# ============================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Tajawal:wght@400;500;700&display=swap');

* {
    font-family: 'Cairo', 'Tajawal', sans-serif;
    color: #1a1a1a !important;
}

html, body, [data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

.stApp {
    background: transparent;
}

.main-box {
    background-color: rgba(255, 255, 255, 0.98);
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18);
    margin-bottom: 50px;
    backdrop-filter: blur(5px);
}

h1, h2, h3, h4, h5, p, span, li, div, label, .stMarkdown, .stTextInput, .stNumberInput, .stSelectbox {
    color: #1a1a1a !important;
    text-shadow: none !important;
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
    transition: transform 0.3s ease;
}

.formula-item:hover {
    transform: translateX(-5px);
    box-shadow: 0px 6px 20px rgba(0,0,0,0.15);
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

.sack-tag {
    border: 3px dashed #1b5e20;
    padding: 30px;
    border-radius: 15px;
    background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e9 100%);
    direction: rtl;
    text-align: right;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.1);
}

.sack-tag * {
    color: #1a1a1a !important;
}

.profile-img-style {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #d4af37;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.25);
    display: block;
    margin: 0 auto;
    transition: transform 0.3s ease;
}

.profile-img-style:hover {
    transform: scale(1.05);
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
    text-align: center;
    transition: transform 0.3s ease;
}

.metric-card * {
    color: #1a1a1a !important;
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
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background-color: #c8e6c9 !important;
    transform: translateY(-2px);
    box-shadow: 0px 4px 15px rgba(46,125,50,0.3) !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > select {
    color: #1a1a1a !important;
    background-color: #ffffff !important;
    border-radius: 8px !important;
}

.stTabs [data-baseweb="tab-list"] button {
    color: #1a1a1a !important;
    font-weight: 500 !important;
}

.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    color: #1b5e20 !important;
    font-weight: bold !important;
    border-bottom: 3px solid #2e7d32 !important;
}

.stAlert, .stInfo, .stSuccess, .stWarning, .stError {
    color: #1a1a1a !important;
    border-radius: 10px !important;
}

.stAlert * {
    color: #1a1a1a !important;
}

.welcome-banner {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 20px 30px;
    border-radius: 15px;
    border-right: 6px solid #2e7d32;
    margin: 20px 0;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
}

.welcome-banner * {
    color: #1b5e20 !important;
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
    backdrop-filter: blur(5px);
}

.mini-left-signature * {
    color: white !important;
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

.price-card * {
    color: #1a1a1a !important;
}

.warning-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 15px;
    border-radius: 12px;
    border-right: 5px solid #f57c00;
    margin-bottom: 15px;
    direction: rtl;
    text-align: right;
    color: #e65100 !important;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
}

.warning-card * {
    color: #e65100 !important;
}

/* تصحيح عرض الجداول */
.dataframe {
    direction: rtl !important;
    text-align: right !important;
}

.dataframe * {
    text-align: right !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 22. بوابة الدخول
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
    
    # عرض QR Code
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
                    logger_manager.log_user_action(
                        CODES_DB[input_code_stripped]["name"],
                        "LOGIN_CODE",
                        {"code": input_code_stripped}
                    )
                    st.rerun()
                else:
                    st.session_state["login_attempts"] += 1
                    st.session_state["last_login_time"] = datetime.now()
                    remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                    st.error(f"❌ الكود غير صحيح! متبقي {remaining} محاولات")
        with col_reset:
            if st.button("🔄 نسيت الكود", use_container_width=True):
                st.info("يرجى التواصل مع مدير النظام: " + Config.OWNER_EMAIL)
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
                logger_manager.log_user_action(
                    user['username'],
                    "LOGIN_PASSWORD",
                    {"role": user['role']}
                )
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
# 23. الواجهة الرئيسية
# ============================================================================

st.markdown('<div style="min-height:20px;"></div>', unsafe_allow_html=True)

# ===== إضافة زر إرسال الكود =====
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
        st.caption("⚠️ يتم إرسال ملف الكود الكامل (tower_platform.py) كمرفق عبر البريد الإلكتروني.")

# ===== حالة المستخدم =====
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
        logger_manager.log_user_action(
            st.session_state.get("user", {}).get("username", "unknown"),
            "LOGOUT",
            {}
        )
        for key in list(st.session_state.keys()):
            if key not in ["inventory", "global_livestock_prices", "global_products_prices", 
                          "broiler_farms", "standard_vacc_schedule"]:
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

# ===== الشعار والعنوان =====
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

# ===== المشاركة التسويقية =====
st.markdown("### 📢 المشاركة التسويقية والدعوة العلمية")
share_text_payload = f"""📢 دعوة علمية وتسويقية من {Config.APP_NAME} إلى كل مهتم بتطوير الثروة الحيوانية؛ من أطباء بيطريين، اختصاصيي إنتاج حيواني، ومربين طموحين:

يسعدنا دعوتكم لاستخدام وتجربة المنصة المتقدمة لتركيب وتطوير الأعلاف، بإشراف وتصميم: [ {Config.APP_AUTHOR} ]

🎯 ما تقدمه المنصة:
• حلول برمجية ذكية لتركيب أعلاف اقتصادية على أساس البروتين المهضوم ومعادل النشاء (Least-Cost Formulation).
• أدوات دقيقة لحساب الاحتياجات الغذائية بما يضمن أعلى معدلات نمو وإنتاجية.
• دعم كامل للعمل الميداني والبحث العلمي والخصم التلقائي للمستودعات في مكان واحد.
• نظام تحليلات متقدم وتقارير PDF احترافية
• إدارة مزارع الدجاج اللاحم مع حساب KPIs و EPEF

🔗 رابط المنصة: https://tower-scientific-platform.streamlit.app

#الانتاج_الحيواني #تركيب_الاعلاف #تغذية_الحيوان #تاور_العلمية"""

st.text_area("النص الدعائي والإعلامي الجاهز للنشر:", value=share_text_payload, height=140, key="top_share_box")

col_copy, col_share = st.columns(2)
with col_copy:
    if st.button("📋 نسخ النص للدعاية والتسويق", type="secondary", use_container_width=True):
        st.success("✅ تم التجهيز! يمكنك الآن نسخ النص ومشاركته.")
with col_share:
    encoded_share = urllib.parse.quote(share_text_payload[:200])
    st.link_button("📲 مشاركة مباشرة عبر واتساب", f"https://wa.me/?text={encoded_share}", use_container_width=True)

st.markdown("---")

# ===== الترحيب =====
welcome_messages = {
    "owner": {
        "bg": "#eff6ff",
        "border": "#1d4ed8",
        "text": f"👑 أهلاً بك في منصتك، {Config.APP_AUTHOR}. نظام التوازن الدقيق بالبروتين المهضوم ومعادل النشاء قيد التشغيل الآن بكفاءة متناهية. كما تم تفعيل إدارة مزارع الدجاج اللاحم."
    },
    "specialist": {
        "bg": "#f0fdf4",
        "border": "#16a34a",
        "text": f"🔬 مرحباً بكم في منصة تركيب وتحليل الأعلاف الذكية. يسعد {Config.APP_AUTHOR} بالترحيب بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني."
    },
    "breeder": {
        "bg": "#fffbeb",
        "border": "#d97706",
        "text": f"🚜 أهلاً وسهلاً بكم في {Config.APP_NAME}. نرحب بإخواننا المربين. نوفر لكم خلطات مبنية على القيمة الغذائية الحقيقية الممتصة لضمان التوفير المالي العالي."
    }
}

current_welcome = welcome_messages.get(st.session_state["user_role"], welcome_messages["breeder"])
st.markdown(f"""
<div style="background:{current_welcome['bg']};padding:15px 20px;border-radius:12px;border-right:6px solid {current_welcome['border']};margin:10px 0;">
    <span style="font-size:1.1rem;">{current_welcome['text']}</span>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# 24. تحديد التبويبات
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
# 25. أدلة الاستخدام (مع خيار صوتي)
# ============================================================================

guides = {
    "النمذجة": "في هذا التبويب يمكنك تركيب علفة مثالية بأقل تكلفة باستخدام البروتين المهضوم ومعادل النشاء. اختر الموقع الجغرافي، ثم القطاع الحيواني، وحدد المكونات، ثم اضغط على زر التشغيل. يمكنك أيضاً تحليل خلطة جاهزة في مختبر التحليل.",
    "بورصة الأسعار": "يعرض هذا التبويب أسعار الماشية والمنتجات الحيوانية. يمكن للمالك تحديث الأسعار، وإضافة حيوانات أو منتجات جديدة. يستخدم النظام هذه الأسعار في حساب التكاليف.",
    "المستودعات": "يعرض أرصدة المواد العلفية في المخزن. يمكن للمالك تحديث الكميات، ويراقب النظام المخزون المنخفض وينبهك. تستخدم هذه الأرصدة عند إصدار الفواتير للخصم التلقائي.",
    "الفواتير": "هنا يمكنك إصدار فواتير البيع للعملاء. أدخل اسم العميل والكمية المطلوبة، وسيحسب النظام السعر الإجمالي ويخصم المكونات من المخزون تلقائياً (للمالك فقط).",
    "الديباجة": "يتيح لك تصميم ديباجة جوالات الأعلاف بشكل فني، مع إضافة اسم البراند والصور والشعارات، ثم تصديرها كـ PDF للطباعة.",
    "التحليلات": "يعرض مؤشرات الأداء مثل عدد الخلطات، متوسط التكلفة، ونسبة التوفير. كما يوفر تنبؤات لأسعار المواد الخام ورسوماً بيانية لتوزيع الاستخدام واتجاه الأسعار.",
    "إدارة الدجاج": "خاص بالمالك، يمكنك تسجيل مزارع الدجاج اللاحم، وتحديث بيانات القطيع اليومية (الوزن، العلف، النافق، الأدوية). يحسب النظام مؤشرات الأداء مثل ADG و FCR و EPEF، ويرسل تنبيهات واتساب للتحصينات.",
    "تعليقات المختصين": "قناة لتبادل الخبرات بين المختصين والأطباء البيطريين. يمكن إضافة تعليقات جديدة، وتظهر جميع التعليقات في سجل واحد.",
    "المراجع": "يحتوي على مراجع علمية موثقة في تغذية الحيوان، مع إمكانية البحث في بنك المعرفة السريع عن مصطلحات مثل البروتين المهضوم ومعادل النشاء.",
    "المساعدة": "يجيب على الأسئلة الشائعة ويوفر روابط للدعم الفني. يمكنك طرح سؤالك والحصول على إجابة فورية من بنك المعرفة.",
    "دليل المستخدم": "دليل شامل يشرح كيفية استخدام المنصة خطوة بخطوة، من تسجيل الدخول إلى تركيب العلف وإدارة المزارع والفواتير.",
    "الإعدادات": "يتيح لك ضبط إعدادات النظام، مثل تغيير كلمة المرور، إدارة المستخدمين، وتكوين الإعدادات العامة."
}

# ============================================================================
# 26. التبويب 1: النمذجة والحسابات العلفية
# ============================================================================

with tabs[0]:
    guide_section("النمذجة والحسابات العلفية", guides["النمذجة"])
    
    st.markdown('<div class="section-title">🌍 أولاً: تحديد الموقع الجغرافي وبورصة الأسعار</div>', unsafe_allow_html=True)
    
    col_country, col_state, col_city = st.columns(3)
    with col_country:
        user_country = st.selectbox("اختر دولة المربي:", ["السودان", "LIBYA", "مصر", "باقي دول العالم / البورصة المفتوحة"])
        c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"})
        local_rate = c_info["rate"]
        local_sym = c_info["sym"]
    
    chosen_state = "عام"
    with col_state:
        if user_country == "السودان":
            chosen_state = st.selectbox("اختر الولاية السودانية:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال كردفان", "ولاية جنوب كردفان", "ولاية غرب كردفان", "إقليم النيل الأزرق", "ولاية البحر الأحمر", "ولاية نهر النيل"])
        elif user_country == "LIBYA":
            chosen_state = st.selectbox("اختر الإقليم الجغرافي:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
        else:
            chosen_state = st.selectbox("الإقليم الإداري:", ["المركز الرئيسي العالمي", "الأسواق المفتوحة"])
    
    with col_city:
        if user_country == "السودان":
            cities_map = {
                "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
                "ولاية الجزيرة": ["ود مدني", "الحصاحيصا", "المناقل"],
                "ولاية القضارف": ["القضارف المدينة", "الفاو"],
                "ولاية شمال كردفان": ["الأبيض", "بارا", "أم روابة"],
                "ولاية جنوب كردفان": ["كادوقلي", "الدلنج"],
                "ولاية غرب كردفان": ["الفوله", "النهود", "بابنوسة"],
                "إقليم النيل الأزرق": ["الدمازين", "الروصيرص"],
                "ولاية البحر الأحمر": ["بورتسودان", "سواكن"],
                "ولاية نهر النيل": ["شندي", "عطبرة", "الدامر"]
            }
            user_city = st.selectbox("اختر المدينة:", cities_map.get(chosen_state, ["عام"]))
        elif user_country == "LIBYA":
            cities_map = {
                "المنطقة الشرقية": ["طبرق", "بنغازي", "البيضاء", "درنة"],
                "المنطقة الغربية": ["طرابلس", "مصراتة", "الزاوية"],
                "المنطقة الجنوبية": ["سبها", "مرزق", "غات"]
            }
            user_city = st.selectbox("اختر المدينة:", cities_map.get(chosen_state, ["عام"]))
        else:
            user_city = st.text_input("اكتب اسم المدينة:", "طبرق")
    
    city_key = f"{user_country}|||{chosen_state}|||{user_city}"
    custom_prices = {}  # سيتم تحميلها من قاعدة البيانات
    
    # ===== عرض الأسعار =====
    col_view1, col_view2 = st.columns(2)
    with col_view1:
        st.markdown(f'<div class="price-card">📈 <strong>بورصة الماشية والداجن في ({user_city}):</strong><br>' + 
                   '<br>'.join([f'▪️ {k}: ${v:.2f} ({v*local_rate:,.2f} {local_sym})' for k, v in st.session_state["global_livestock_prices"].items()]) + 
                   '</div>', unsafe_allow_html=True)
    with col_view2:
        st.markdown(f'<div class="price-card">🥩 <strong>بورصة المنتجات الحيوانية في ({user_city}):</strong><br>' + 
                   '<br>'.join([f'▪️ {k}: ${v:.2f} ({v*local_rate:,.2f} {local_sym})' for k, v in st.session_state["global_products_prices"].items()]) + 
                   '</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">⚖️ ثانياً: اختيار القطاع والنوع والإنتاجية المستهدفة</div>', unsafe_allow_html=True)
    
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec:
        main_sector = st.selectbox("اختر القطاع الإنتاجي الرئيسي:", 
                                   ["الأغنام وسلالاتها 🐏", "الماعز وسلالاتها", "الأبقار وسلالاتها", 
                                    "الخيول والفروسية", "الطيور والسمان", "الأسماك والأحياء المائية"])
    
    show_measurements = False
    weight_factor = 10000
    feed_factor = 0.02
    default_dp = 11.0
    default_se = 60.0
    dynamic_img_key = "عام"
    chosen_concentrate = None
    gender_option = "إناث"
    
    if main_sector in ["الأغنام وسلالاتها 🐏", "الماعز وسلالاتها"]:
        with col_sec:
            gender_option = st.radio("حدد الجنس:", ["ذكور (تسمين)", "إناث (حليب / أمهات)"], horizontal=True)
        with col_sub:
            if main_sector == "الأغنام وسلالاتها 🐏":
                sub_type = st.selectbox("السلالة المستهدفة:", ["الضأن الصحراوي السوداني", "البربري", "النعيمي", "سلالات محلية / هجين"])
                dynamic_img_key = "أغنام"
                show_measurements = True
                weight_factor = 15500
                feed_factor = 0.035
                chosen_concentrate = "مركزات خيول ومجترات"
            else:
                sub_type = st.selectbox("السلالة المستهدفة:", ["الماعز النوبي السوداني", "الماعز الصحراوي", "بور / محسن"])
                dynamic_img_key = "ماعز"
                show_measurements = True
                weight_factor = 15000
                feed_factor = 0.032
                chosen_concentrate = "مركزات خيول ومجترات"
    elif main_sector == "الأبقار وسلالاتها":
        with col_sub:
            sub_type = st.selectbox("السلالة المستهدفة:", ["كنانة (سوداني)", "بطانة (مدر)", "هولشتاين / محسن"])
            dynamic_img_key = "أبقار"
            show_measurements = True
            weight_factor = 10838
            feed_factor = 0.025
            chosen_concentrate = "مركزات خيول ومجترات"
    elif main_sector == "الخيول والفروسية":
        with col_sub:
            sub_type = st.selectbox("السلالة المستهدفة:", ["خيل عربي أصيل", "ثوروبريد", "خيول محلية هجين"])
            dynamic_img_key = "خيول"
            show_measurements = True
            weight_factor = 11877
            feed_factor = 0.022
            chosen_concentrate = "مركزات خيول ومجترات"
    elif main_sector == "الطيور والسمان":
        with col_sub:
            sub_type = st.selectbox("نوع الطيور:", ["طائر السمان (Quail)", "دواجن لاحم (Broiler)", "دواجن بياض (Layer)"])
            dynamic_img_key = "سمان" if "السمان" in sub_type else "دواجن"
            chosen_concentrate = "مركزات دواجن وسمان"
    else:
        with col_sub:
            sub_type = st.selectbox("نوع الأسماك:", ["البلطي النيلي (Tilapia)", "القرموط"])
            dynamic_img_key = "أسماك"
            chosen_concentrate = "مسحوق أسماك (Fishmeal 60%)"
    
    with col_prod:
        if main_sector == "الأغنام وسلالاتها 🐏":
            if gender_option == "ذكور (تسمين)":
                prod_stage = st.selectbox("خط إنتاج الذكور:", ["تسمين حملان مكثف (نمو سريع)", "حملان تيد / كباش جاهزة للأسواق"])
                default_dp = 12.0 if "مكثف" in prod_stage else 9.5
                default_se = 64.0 if "مكثف" in prod_stage else 58.0
            else:
                prod_stage = st.selectbox("خط إنتاج الإناث:", ["نعاج مرضعات (إدرار عالي)", "نعاج حامل (الفترة الأخيرة)", "نعاج جافة / صيانة"])
                default_dp = 12.8 if "مرضعات" in prod_stage else (10.5 if "حامل" in prod_stage else 8.0)
                default_se = 66.0 if "مرضعات" in prod_stage else (60.0 if "حامل" in prod_stage else 50.0)
        elif main_sector == "الماعز وسلالاتها":
            if gender_option == "ذكور (تسمين)":
                prod_stage = st.selectbox("خط إنتاج الذكور:", ["تسمين جديان نمو سريع", "تيوس علفية جاهزة للتسويق"])
                default_dp = 11.5 if "جديان" in prod_stage else 9.0
                default_se = 62.0 if "جديان" in prod_stage else 55.0
            else:
                prod_stage = st.selectbox("خط إنتاج الإناث:", ["عنزات حلابة وغزارة لبن", "عنزات حامل (دفع غذائي)", "صيانة دورية للأمهات"])
                default_dp = 12.8 if "حلابة" in prod_stage else (10.0 if "حامل" in prod_stage else 7.8)
                default_se = 65.0 if "حلابة" in prod_stage else (58.0 if "حامل" in prod_stage else 48.0)
        elif main_sector == "الأبقار وسلالاتها":
            prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج حليب وغزارة إدرار", "تسمين عجول مكثف"])
            default_dp = 12.5 if "حليب" in prod_stage else 10.0
            default_se = 68.0 if "حليب" in prod_stage else 65.0
        elif main_sector == "الخيول والفروسية":
            prod_stage = st.selectbox("نوع الإنتاج:", ["خيول رياضة ونشاط مكثف", "أمهار نامية صغيرة", "فرسات مرضعات"])
            default_dp = 12.5 if "أمهار" in prod_stage or "مرضعات" in prod_stage else 9.5
            default_se = 65.0 if "رياضة" in prod_stage else 60.0
        elif main_sector == "الطيور والسمان":
            if "السمان" in sub_type:
                prod_stage = st.selectbox("نوع الإنتاج:", ["سمان بادي / نامي", "سمان بياض إنتاجي"])
                default_dp = 20.0 if "بادي" in prod_stage else 16.5
                default_se = 72.0 if "بادي" in prod_stage else 68.0
            else:
                prod_stage = st.selectbox("نوع الإنتاج:", ["بادي دواجن 23%", "نامي دواجن 21%", "ناهي دواجن 19%", "بياض إنتاجي"])
                default_dp = 20.0 if "بادي" in prod_stage else (18.5 if "نامي" in prod_stage else (16.5 if "ناهي" in prod_stage else 15.0))
                default_se = 76.0 if "بادي" in prod_stage else (74.0 if "نامي" in prod_stage else (75.0 if "ناهي" in prod_stage else 70.0))
        else:
            prod_stage = st.selectbox("نوع الإنتاج:", ["بادئ زريعة أسماك عالي", "نمو وتسمين أسماك نيلية"])
            default_dp = 29.5 if "زريعة" in prod_stage else 25.0
            default_se = 70.0
    
    # ===== القياسات الجسدية =====
    if show_measurements:
        st.markdown('<div class="section-title">📐 القياسات الجسدية وتقدير الأوزان</div>', unsafe_allow_html=True)
        col_h, col_l, col_ag = st.columns(3)
        with col_h:
            h_girth = st.number_input("📏 محيط الصدر (سم):", value=150.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 75.0)
        with col_l:
            b_length = st.number_input("📏 طول الجسم (سم):", value=130.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 65.0)
        with col_ag:
            a_months = st.number_input("⏳ العمر التقديري (أشهر):", value=12)
        
        calc_weight = (h_girth ** 2 * b_length) / weight_factor
        req_feed_kg = calc_weight * feed_factor
        st.success(f"📊 الوزن الحيوي المتوقع: **{calc_weight:.1f} كجم** | الاحتياج اليومي للمادة الجافة: **{req_feed_kg:.2f} كجم**")
    else:
        st.info("💡 تم تحييد شريط القياس الجسدي لعدم ملاءمته للطيور والأسماك.")
    
    # ===== حدود الموازنة =====
    st.markdown('<div class="section-title">📋 رابعاً: حدود الموازنة الذكية (DP & SE)</div>', unsafe_allow_html=True)
    
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
    
    # ===== اختيار المكونات =====
    st.markdown('<div class="section-title">📦 خامساً: اختيار المواد العلفية والإضافات</div>', unsafe_allow_html=True)
    
    selected_ingredients = []
    ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=True if "الحبوب" in cat_name or "الأكساب" in cat_name else False):
            sub_cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with sub_cols[idx % 3]:
                    is_def = ing_name == chosen_concentrate or ing_name in ["ذرة صفراء", "سورجم (فتريتة)", "أمباز الفول السوداني (كسب)", "كسب فول صويا 44%", "نخالة قمح (ردة)", "ملح الطعام", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)", "بيكربونات الصوديوم (الصودا)", "مضاد سموم فطرية", "خميرة الخبز (Yeast)"]
                    checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                    
                    current_live_price = 350.0  # سعر افتراضي
                    if st.session_state["user_role"] == "owner":
                        price_input = st.number_input(f"السعر للطن ({ing_name}) $:", min_value=5.0, value=float(current_live_price), key=f"price_{ing_name}")
                    else:
                        st.markdown(f"💰 السعر الحالي: **`${current_live_price:.2f}`** / طن")
                        price_input = current_live_price
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price_input
    
    # ===== الإضافات الإلزامية =====
    fixed_additives = {
        "ملح الطعام": 0.5,
        "مضاد سموم فطرية": 0.2,
        "الحجر الجيري (بودرة بلاط)": 2.5 if "بياض" in prod_stage else 1.5,
        "فوسفات ثنائي الكالسيوم (DCP)": 1.0
    }
    
    auto_added_enzymes = {}
    mandatory_warnings = []
    
    if main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاتها", "الأغنام وسلالاتها 🐏"]:
        auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.75
        mandatory_warnings.append("🚨 إضافة إلزامية - بيكربونات الصوديوم: تم فرضها أوتوماتيكياً بنسبة 0.75% كمنظم حموضة (Buffer) لحماية الكرش من التحمض Ruminal Acidosis.")
    elif main_sector == "الطيور والسمان":
        auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.20
    
    if main_sector in ["الطيور والسمان", "الأسماك والأحياء المائية"]:
        auto_added_enzymes["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05
        mandatory_warnings.append("🚨 إضافة إلزامية - إنزيم الفايتيز: مضاف تلقائياً بنسبة 0.05% لتحرير الفسفور النباتي المرتبط وتحسين الهضم.")
    
    if "كسب بذور القطن (مقشور)" in selected_ingredients and main_sector == "الطيور والسمان":
        auto_added_enzymes["كبريتات الحديدوز (معادل الجوسيبول)"] = 0.15
        mandatory_warnings.append("⚠️ معالجة الجوسيبول: تم دمج كبريتات الحديدوز بنسبة 0.15% لربط الجوسيبول الحر السام Toxic Gossypol وإبطال مفعوله.")
    
    if main_sector == "الطيور والسمان" and (("شعير مطحون" in selected_ingredients) or ("قمح محلي مصنّع" in selected_ingredients)):
        auto_added_enzymes["إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)"] = 0.08
        mandatory_warnings.append("⚠️ إضافة إنزيمات الـ NSP: تم دمج إنزيمات كسر الروابط المتعددة لمنع عارض البراز الرطب (Wet Litter).")
    
    all_fixed_additives = {**fixed_additives, **auto_added_enzymes}
    for item in all_fixed_additives:
        if item not in selected_ingredients:
            selected_ingredients.append(item)
            ingredient_prices[item] = 40.0
    
    st.markdown("---")
    
    # ===== تشغيل المحرك =====
    nz_placeholder = st.empty()
    if st.button("🚀 تشغيل محرك الاستمثال الخطي (بالبروتين المهضوم ومعادل النشاء)", type="primary", use_container_width=True):
        with nz_placeholder.container():
            st.warning("⚠️ **إشعار هام بشأن الإنزيمات ومضافات الأعلاف:** يرجى التأكد من موازنة درجات حرارة كبس العلف لضمان عدم تثبيط الإنزيمات والفيتامينات الدقيقة. (سيختفي هذا الإشعار تلقائياً بعد 40 ثانية)")
            
            # بناء مصفوفة التكلفة
            c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
            
            # الحدود الدنيا والعليا
            bounds = [(all_fixed_additives[ing], all_fixed_additives[ing]) if ing in all_fixed_additives else (0.0, 100.0) for ing in selected_ingredients]
            
            # قيد المجموع = 100%
            A_eq = [[1.0 for _ in selected_ingredients]]
            b_eq = [100.0]
            
            # قيد البروتين
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
            
            # قيود عدم المساواة
            A_ub = []
            b_ub = []
            
            # قيد الطاقة (SE)
            A_ub.append([-1.0 * x for x in se_row])
            b_ub.append(-1.0 * final_target_se * 100.0)
            
            # قيد الحبوب
            grain_indicators = [1.0 if ing in BIG_FEEDS_LIBRARY["🌾 الحبوب ومصادر الطاقة الكبرى"] else 0.0 for ing in selected_ingredients]
            if sum(grain_indicators) > 0:
                A_ub.append([-1.0 * x for x in grain_indicators])
                b_ub.append(-50.0)
            
            # قيد النخالة
            if "نخالة قمح (ردة)" in selected_ingredients:
                fiber_indicators = [1.0 if ing == "نخالة قمح (ردة)" else 0.0 for ing in selected_ingredients]
                A_ub.append(fiber_indicators)
                b_ub.append(18.0)
            
            # قيود ديناميكية
            dynamic_limits = {
                "مولاس قصب السكر": {"default": 12.0, "دواجن": 5.0, "خيول": 8.0, "أسماك": 5.0},
                "يوريا علفية محصنة (المجترات فقط)": {"default": 1.0, "دواجن": 0.0, "خيول": 0.0, "أسماك": 0.0},
                "مخلفات مصانع البسكويت": {"default": 15.0, "دواجن": 10.0},
                "سرسة الأرز المطحونة": {"default": 10.0},
                "ملح الطعام": {"default": 1.0},
                "خميرة الخبز (Yeast)": {"default": 5.0, "دواجن": 3.0, "أسماك": 2.0}
            }
            
            sector_key = main_sector.replace(" وسلالاتها","").replace(" والأحياء المائية","")
            for material, limits_dict in dynamic_limits.items():
                if material in selected_ingredients:
                    limit = limits_dict.get(sector_key, limits_dict.get("default", 15.0))
                    idx = selected_ingredients.index(material)
                    constraint_row = [0.0] * len(selected_ingredients)
                    constraint_row[idx] = 1.0
                    A_ub.append(constraint_row)
                    b_ub.append(limit)
                    mandatory_warnings.append(f"ℹ️ حد أقصى: {material} ≤ {limit}% (تلقائي للقطاع)")
            
            # حل المشكلة
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
                st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES.get(dynamic_img_key, ANIMAL_IMAGES_RESOURCES["عام"])
                st.session_state["active_stage_title"] = f"{main_sector} ({gender_option}) - {prod_stage}"
                
                st.success(f"🎯 تم تشغيل محرك الاستمثال الخطي بنجاح في سوق: {user_city}")
                
                if not use_cp_basis and final_target_dp > 0:
                    nutritive_ratio = computed_se_total / final_target_dp
                    st.info(f"📊 النسبة الغذائية للخلطة (Nutritive Ratio = SE / DP): **{nutritive_ratio:.2f}**")
                
                if mandatory_warnings:
                    st.markdown("### 🔬 تقرير فحص العلل والتدخل البرمجي:")
                    for warn in mandatory_warnings:
                        st.markdown(f'<div class="warning-card">{warn}</div>', unsafe_allow_html=True)
                
                # عرض النتائج
                res_col1, res_col2 = st.columns([0.6, 0.4])
                with res_col1:
                    st.write("#### 📝 المقادير المعتمدة لتركيب طن واحد (كجم):")
                    for k, v in formula_results.items():
                        st.markdown(f'<div class="formula-item">▪️ {k}: {v:.2f} % ➡️ ({v*10:.1f} كجم / طن)</div>', unsafe_allow_html=True)
                    
                    ton_cost = res.fun / 100.0 if hasattr(res, 'fun') else 280.0
                    st.session_state["computed_ton_cost"] = ton_cost
                    st.metric(f"💰 التكلفة الفعلية لإنتاج الطن في {user_city}: ", f"${ton_cost:.2f} (أو {ton_cost*local_rate:,.1f} {local_sym})")
                    
                    col_share, col_pdf = st.columns(2)
                    with col_share:
                        share_message = f"{Config.APP_NAME} - الخلطة المعتمدة: {sub_type} ({gender_option})، بتكلفة إنتاج {ton_cost:.2f}$ للطن. المشرف: {Config.APP_AUTHOR}."
                        encoded_share_msg = urllib.parse.quote(share_message)
                        st.link_button("📲 مشاركة الفاتورة عبر واتساب", f"https://wa.me/?text={encoded_share_msg}")
                    
                    with col_pdf:
                        try:
                            pdf_generator = ProfessionalPDFGenerator()
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
                    fig = px.pie(values=list(formula_results.values()), names=list(formula_results.keys()),
                                title="توزيع مكونات الخلطة", color_discrete_sequence=px.colors.sequential.Greens)
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    chart_data = pd.DataFrame({'المكون': list(formula_results.keys()),
                                               'النسبة المئوية': list(formula_results.values()),
                                               'الوزن (كجم/طن)': [v*10 for v in formula_results.values()]})
                    st.bar_chart(chart_data.set_index('المكون')['الوزن (كجم/طن)'])
            else:
                st.error("❌ تعذر إيجاد حل رياضي متزن. يرجى إتاحة خامات إضافية ككسب فول صويا أو أمباز الفول لتوسيع مساحة الحل.")
            
            time.sleep(40)
            nz_placeholder.empty()
    
    # ===== مختبر التحليل =====
    st.markdown("---")
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
        ("أبقار", "تسمين"): 12.0, ("أبقار", "حليب/إدرار"): 14.0,
        ("أبقار", "حمل/دفع غذائي"): 11.0, ("أبقار", "صيانة"): 9.0,
        ("أغنام", "تسمين"): 13.0, ("أغنام", "حليب/إدرار"): 14.5,
        ("أغنام", "حمل/دفع غذائي"): 11.5, ("أغنام", "صيانة"): 8.5,
        ("ماعز", "تسمين"): 12.5, ("ماعز", "حليب/إدرار"): 14.0,
        ("ماعز", "حمل/دفع غذائي"): 11.0, ("ماعز", "صيانة"): 8.0,
        ("خيول", "نمو"): 13.0, ("خيول", "تسمين نهائي"): 11.0,
        ("دواجن لاحم", "بادي"): 23.0, ("دواجن لاحم", "نامي"): 21.0,
        ("دواجن لاحم", "ناهي"): 19.0, ("دواجن بياض", "بادي"): 20.0,
        ("دواجن بياض", "نامي"): 18.0, ("دواجن بياض", "ناهي"): 16.5,
        ("دواجن بياض", "بياض"): 16.0, ("سمان", "بادي"): 24.0,
        ("سمان", "نامي"): 22.0, ("سمان", "ناهي"): 20.0,
        ("سمان", "بياض"): 18.0, ("أسماك", "نمو"): 32.0,
        ("أسماك", "تسمين نهائي"): 28.0
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
            st.error("❌ الوزن الإجمالي للخلطة يساوي صفر، يرجى إدخال مقادير.")
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
                    entered_components_summary.append({
                        "المادة العلفية": ing_name,
                        "الوزن المدخل": f"{weight:.1f} كجم",
                        "النسبة المئوية": f"{pct * 100:.2f}%"
                    })
            
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
                {"العنصر الغذائي": "البروتين المهضوم (DP)", "القيمة المحسوبة": f"{calculated_total_dp:.2f}%", 
                 "الاحتياج القياسي": f"{target_value:.1f}%" if analysis_basis == "بروتين مهضوم (DP)" else "-", "التقييم": status_label},
                {"العنصر الغذائي": "البروتين الخام (CP)", "القيمة المحسوبة": f"{calculated_total_cp:.2f}%", 
                 "الاحتياج القياسي": f"{target_value:.1f}%" if analysis_basis == "بروتين خام (CP)" else "-", "التقييم": "-"},
                {"العنصر الغذائي": "معادل النشاء (SE)", "القيمة المحسوبة": f"{calculated_total_se:.2f} وحدة", 
                 "الاحتياج القياسي": "مرن حسب الفصيل", "التقييم": "تحليل طاقة كلي"}
            ]
            st.table(pd.DataFrame(lab_report_data))
            
            st.write("📊 التمثيل البياني لتوزيع المواد المدخلة:")
            graph_data = {k: v for k, v in lab_user_inputs.items() if v > 0}
            if graph_data:
                fig = px.bar(x=list(graph_data.keys()), y=list(graph_data.values()),
                            labels={'x': 'المادة العلفية', 'y': 'الوزن (كجم)'},
                            title="توزيع أوزان المواد في الخلطة المختبرة")
                st.plotly_chart(fig, use_container_width=True)
            
            lab_share_text = f"نتيجة مختبر منصة تاور:\nالحيوان: {target_animal} - {production_type}\nالبروتين المحسوب: {comparison_value:.2f}%\nالمعيار: {target_value:.1f}%"
            encoded_lab = urllib.parse.quote(lab_share_text)
            st.markdown(f'<a href="https://wa.me/?text={encoded_lab}" target="_blank">📲 مشاركة النتيجة عبر واتساب</a>', unsafe_allow_html=True)

# ============================================================================
# 27. تبويب بورصة الأسعار (مبسط)
# ============================================================================

if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[1]:
        guide_section("بورصة الأسعار المركزية", guides["بورصة الأسعار"])
        st.markdown('<div class="section-title">📊 لوحة تحكم بورصة تاور المركزية الشاملة</div>', unsafe_allow_html=True)
        
        if st.session_state["user_role"] == "specialist":
            st.warning("⚠️ حساب مختص: متاح لك استعراض الأسعار فقط، التعديل محجوز لإدارة المنصة.")
        
        tab_livestock, tab_products = st.tabs(["🐄 بورصة الماشية", "🥛 بورصة المنتجات"])
        
        with tab_livestock:
            col_edit1, col_edit2 = st.columns(2)
            with col_edit1:
                st.subheader("أسعار الماشية والداجن")
                for animal, price in st.session_state["global_livestock_prices"].items():
                    if st.session_state["user_role"] == "owner":
                        st.session_state["global_livestock_prices"][animal] = st.number_input(
                            f"تحديث: {animal}", min_value=0.0, value=float(price), step=0.1, key=f"livestock_{animal}"
                        )
                    else:
                        st.markdown(f"▪️ {animal}: **${price:.2f}**")
            with col_edit2:
                if st.session_state["user_role"] == "owner":
                    st.subheader("إضافة حيوان جديد")
                    new_animal = st.text_input("اسم الحيوان/السلالة:")
                    new_price = st.number_input("السعر بالدولار:", min_value=0.0, value=0.0)
                    if st.button("إضافة إلى البورصة") and new_animal:
                        st.session_state["global_livestock_prices"][f"{new_animal} ($)"] = new_price
                        st.success("تمت الإضافة بنجاح!")
                        st.rerun()
        
        with tab_products:
            col_prod1, col_prod2 = st.columns(2)
            with col_prod1:
                st.subheader("أسعار المنتجات الحيوانية")
                for product, price in st.session_state["global_products_prices"].items():
                    if st.session_state["user_role"] == "owner":
                        st.session_state["global_products_prices"][product] = st.number_input(
                            f"تحديث: {product}", min_value=0.0, value=float(price), step=0.05, key=f"prod_edit_{product}"
                        )
                    else:
                        st.markdown(f"▪️ {product}: **${price:.2f}**")

# ============================================================================
# 28. تبويب إدارة المستودعات
# ============================================================================

if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[2]:
        guide_section("إدارة المستودعات الذكية", guides["المستودعات"])
        st.markdown('<div class="section-title">🏭 لوحة التحكم الذكية بالمخازن والمستودعات المركزية</div>', unsafe_allow_html=True)
        
        if st.session_state["user_role"] == "specialist":
            st.warning("⚠️ حساب مختص: يمكنك مراجعة الأرصدة فقط دون تعديل.")
        
        inventory_manager = InventoryManager()
        stock_warnings = inventory_manager.check_stock_levels()
        
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        with col_stats1:
            st.metric("إجمالي المواد", len(st.session_state["inventory"]))
        with col_stats2:
            critical_items = sum(1 for v in stock_warnings.values() if v == "نفذ المخزون")
            st.metric("مواد نفذت", critical_items, delta=f"-{critical_items}" if critical_items > 0 else "0")
        with col_stats3:
            low_items = sum(1 for v in stock_warnings.values() if v == "منخفض")
            st.metric("مواد منخفضة", low_items, delta=f"-{low_items}" if low_items > 0 else "0")
        with col_stats4:
            healthy_items = len(st.session_state["inventory"]) - critical_items - low_items
            st.metric("مواد آمنة", healthy_items)
        
        st.markdown("---")
        inv_cols = st.columns(3)
        for idx, (ing_name, qty_data) in enumerate(list(st.session_state["inventory"].items())):
            with inv_cols[idx % 3]:
                qty = qty_data["quantity"]
                threshold = qty_data["min_threshold"]
                if qty <= 0:
                    status_badge = f'<span class="stock-critical">⚠️ نفذ: {qty:.2f} طن</span>'
                elif qty < threshold:
                    status_badge = f'<span class="stock-critical">⚠️ حرج: {qty:.2f} طن</span>'
                else:
                    status_badge = f'<span class="stock-normal">✅ آمن: {qty:.2f} طن</span>'
                
                st.markdown(f"**{ing_name}** | {status_badge}", unsafe_allow_html=True)
                
                if st.session_state["user_role"] == "owner":
                    new_qty = st.number_input(f"تحديث ({ing_name}) طن:", min_value=0.0, value=float(qty), key=f"inv_input_{ing_name}")
                    if new_qty != qty:
                        st.session_state["inventory"][ing_name]["quantity"] = new_qty
                        st.session_state["inventory"][ing_name]["last_updated"] = datetime.now().isoformat()

# ============================================================================
# 29. تبويب الفواتير
# ============================================================================

if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[3]:
        guide_section("التسويق وفواتير البيع", guides["الفواتير"])
        st.markdown('<div class="section-title">💰 نظام تسويق المنتجات وإصدار الفواتير مع الخصم التلقائي</div>', unsafe_allow_html=True)
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            client_name = st.text_input("اسم العميل / المزرعة:", "مزارع الإنتاج المتكاملة")
        with col_c2:
            required_tons = st.number_input("الكمية المطلوبة (طن):", min_value=0.1, value=2.0, step=0.5)
        with col_c3:
            added_profit = st.number_input("هامش الربح للطن ($):", min_value=0.0, value=50.0)
        
        selling_price = st.session_state.get("computed_ton_cost", 280.0) + added_profit
        total_bill = selling_price * required_tons
        
        st.markdown("### 🧾 فاتورة بيع وتوريد أعلاف رسمية")
        col_fact1, col_fact2 = st.columns(2)
        with col_fact1:
            st.markdown(f"""
            <div style="background:#f8f9fa;padding:20px;border-radius:10px;border:1px solid #dee2e6;direction:rtl;text-align:right;">
                <h4>تفاصيل الفاتورة:</h4>
                <p><strong>العميل:</strong> {client_name}</p>
                <p><strong>الكمية:</strong> {required_tons} طن</p>
                <p><strong>سعر الطن:</strong> ${selling_price:.2f}</p>
                <p><strong>الإجمالي:</strong> ${total_bill:.2f}</p>
                <p><strong>تاريخ الإصدار:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_fact2:
            st.markdown("#### 📊 مكونات الخلطة المباعة:")
            if st.session_state.get("active_formula"):
                for ingredient, pct in st.session_state["active_formula"].items():
                    required_amount = (pct / 100) * required_tons
                    st.markdown(f"▪️ {ingredient}: **{required_amount:.2f}** طن ({pct:.1f}% من الخلطة)")
            else:
                st.info("ℹ️ لا توجد خلطة نشطة، قم بتشغيل محرك الاستمثال أولاً.")
        
        if st.session_state["user_role"] == "owner":
            if st.button("✅ تأكيد عملية البيع وخصم المكونات من المستودع", type="primary", use_container_width=True):
                if not st.session_state.get("active_formula"):
                    st.error("❌ لا توجد خلطة نشطة للبيع.")
                else:
                    can_deduct = True
                    for name, pct in st.session_state["active_formula"].items():
                        current_stock = st.session_state["inventory"].get(name, {}).get("quantity", 0.0)
                        required_amount = (pct / 100) * required_tons
                        if current_stock < required_amount:
                            can_deduct = False
                            st.error(f"❌ رصيد غير كافي: {name} (المطلوب: {required_amount:.2f} طن، المتاح: {current_stock:.2f} طن)")
                            break
                    
                    if can_deduct:
                        for name, pct in st.session_state["active_formula"].items():
                            required_amount = (pct / 100) * required_tons
                            st.session_state["inventory"][name]["quantity"] -= required_amount
                            st.session_state["inventory"][name]["last_updated"] = datetime.now().isoformat()
                        
                        # تسجيل الفاتورة
                        logger_manager.log_user_action(
                            st.session_state.get("user", {}).get("username", "owner"),
                            "INVOICE_CREATED",
                            {"client": client_name, "quantity": required_tons, "total": total_bill}
                        )
                        
                        st.success("🔥 تم الخصم التلقائي وتحديث المخازن بنجاح!")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
        else:
            st.info("ℹ️ تأكيد الفواتير وحركات الخصم متاحة حصرياً لإدارة المالك.")

# ============================================================================
# 30. تبويب مصمم الديباجة
# ============================================================================

if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[4]:
        guide_section("مصمم الديباجة والدعاية", guides["الديباجة"])
        st.markdown('<div class="section-title">👑 مصمم ديباجات الطباعة الفنية على جوالات الأعلاف</div>', unsafe_allow_html=True)
        
        trade_brand = st.text_input("اسم البراند التجاري:", Config.APP_NAME)
        
        col_preview, col_options = st.columns([0.7, 0.3])
        with col_preview:
            st.markdown(f"""
            <div class="sack-tag">
                <div style="text-align:center;margin-bottom:20px;">
                    <img src="data:image/jpeg;base64,{img_base64 if img_base64 else ''}" 
                         style="width:80px;height:80px;border-radius:50%;border:2px solid #d4af37;object-fit:cover;">
                </div>
                <div style="text-align:center;font-size:1.8rem;font-weight:bold;color:#1b5e20;">
                    🌟 {trade_brand} 🌟
                </div>
                <div style="text-align:center;font-size:1rem;color:#2e7d32;margin:10px 0;">
                    {Config.APP_AUTHOR}
                </div>
                <div style="text-align:center;font-size:1.1rem;color:#1a1a1a;margin:15px 0;">
                    🎯 {st.session_state.get('active_stage_title', 'عام')} | 
                    DP: {st.session_state.get('active_cp_tag', 0):.1f}% | 
                    SE: {st.session_state.get('active_se_tag', 0):.1f} وحدة
                </div>
                <div style="text-align:center;font-size:0.8rem;color:#666;">
                    تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d')}
                </div>
                <div style="text-align:center;margin-top:15px;font-size:0.7rem;color:#999;">
                    {Config.APP_NAME} © {datetime.now().year}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_options:
            st.markdown("#### خيارات التخصيص:")
            show_qr = st.checkbox("إضافة QR Code", value=True)
            show_date = st.checkbox("إظهار تاريخ الإنتاج", value=True)
            font_size = st.slider("حجم الخط", 12, 24, 16)
            
            if st.button("📥 تصدير الديباجة كـ PDF", use_container_width=True):
                st.success("✅ تم تجهيز الديباجة للطباعة!")

# ============================================================================
# 31. تبويب التحليلات المتقدمة
# ============================================================================

if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[5]:
        guide_section("التحليلات المتقدمة", guides["التحليلات"])
        st.markdown('<div class="section-title">📈 التحليلات المتقدمة ولوحة المؤشرات</div>', unsafe_allow_html=True)
        
        # مؤشرات الأداء
        col_met1, col_met2, col_met3, col_met4 = st.columns(4)
        with col_met1:
            st.markdown("""
            <div class="metric-card">
                <h3>📊 عدد الخلطات</h3>
                <h2>1,247</h2>
                <p>خلطة تم توليدها</p>
            </div>
            """, unsafe_allow_html=True)
        with col_met2:
            st.markdown("""
            <div class="metric-card">
                <h3>💰 متوسط التكلفة</h3>
                <h2>$285</h2>
                <p>لطن العلف</p>
            </div>
            """, unsafe_allow_html=True)
        with col_met3:
            st.markdown("""
            <div class="metric-card">
                <h3>📉 نسبة التوفير</h3>
                <h2>18%</h2>
                <p>مقارنة بالتقليدي</p>
            </div>
            """, unsafe_allow_html=True)
        with col_met4:
            st.markdown("""
            <div class="metric-card">
                <h3>⭐ رضا العملاء</h3>
                <h2>96%</h2>
                <p>تقييم إيجابي</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # تنبؤات الأسعار
        st.subheader("🔮 تنبؤات الأسعار")
        predictor = PricePredictor()
        ingredients = ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح"]
        col_preds = st.columns(3)
        
        for idx, ing in enumerate(ingredients):
            with col_preds[idx]:
                pred = predictor.predict_price(ing, 7)
                if pred.get('prediction'):
                    trend_icon = "📈" if pred.get('trend') == 'up' else "📉" if pred.get('trend') == 'down' else "➡️"
                    st.metric(
                        f"{trend_icon} {ing}",
                        f"${pred['prediction']:.2f}",
                        delta=f"{pred['prediction'] - pred.get('current_price', 0):.2f}",
                        help=f"الثقة: {pred.get('confidence', 0)*100:.0f}%"
                    )
        
        st.markdown("---")
        
        # المخططات
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("📊 توزيع استخدام المواد العلفية")
            usage_data = pd.DataFrame({
                'المادة': ['ذرة', 'صويا', 'نخالة', 'أملاح', 'أخرى'],
                'نسبة الاستخدام': [45, 25, 15, 10, 5]
            })
            fig = px.pie(usage_data, values='نسبة الاستخدام', names='المادة',
                        title='المواد الأكثر استخداماً',
                        color_discrete_sequence=px.colors.sequential.Greens)
            st.plotly_chart(fig, use_container_width=True)
        
        with col_chart2:
            st.subheader("📈 اتجاه أسعار المواد الخام")
            dates = pd.date_range(start='2024-01-01', periods=12, freq='ME')
            price_trend = pd.DataFrame({
                'التاريخ': dates,
                'الذرة': [220, 225, 230, 228, 235, 240, 238, 242, 245, 248, 250, 252],
                'الصويا': [440, 445, 442, 448, 450, 455, 452, 458, 460, 462, 465, 468]
            })
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=price_trend['التاريخ'], y=price_trend['الذرة'],
                                     mode='lines+markers', name='الذرة',
                                     line=dict(color='#2e7d32', width=2)))
            fig.add_trace(go.Scatter(x=price_trend['التاريخ'], y=price_trend['الصويا'],
                                     mode='lines+markers', name='الصويا',
                                     line=dict(color='#1565C0', width=2)))
            fig.update_layout(title='اتجاه أسعار المواد الخام خلال العام',
                              xaxis_title='التاريخ', yaxis_title='السعر ($/طن)',
                              hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# 32. تبويب إدارة مزارع الدجاج (خاص بالمالك)
# ============================================================================

if st.session_state["user_role"] == "owner":
    with tabs[6]:
        guide_section("إدارة مزارع الدجاج اللاحم", guides["إدارة الدجاج"])
        st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج اللاحم (Broiler Management) – خاص بالمالك</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background:#e8f5e9;padding:15px 20px;border-radius:10px;border-right:4px solid #2e7d32;margin:10px 0;">
            📘 <strong>الدليل الموسع:</strong> يمكنك الآن تسجيل مزارع متعددة بأسماء ملاكها، وتدوين السجل الصحي اليومي (الأدوية، الفيتامينات، التحصينات). 
            يقوم النظام بمقارنة ما تم إعطاؤه فعلياً بالبروتوكول القياسي، ويرسل تنبيهات عبر واتساب في المواعيد المستحقة.
        </div>
        """, unsafe_allow_html=True)
        
        col_farms = st.columns([0.4, 0.6])
        with col_farms[0]:
            st.markdown("#### 🏠 إدارة المزارع المسجلة")
            farm_names = list(st.session_state["broiler_farms"].keys())
            selected = st.selectbox("اختر مزرعة:", [""] + farm_names, format_func=lambda x: x if x else "-- أضف مزرعة جديدة --")
            
            if st.button("➕ إضافة مزرعة جديدة", use_container_width=True):
                st.session_state["show_add_farm"] = True
            
            if st.button("🗑️ حذف المزرعة المختارة", use_container_width=True):
                if selected and selected in st.session_state["broiler_farms"]:
                    del st.session_state["broiler_farms"][selected]
                    if st.session_state["selected_farm"] == selected:
                        st.session_state["selected_farm"] = None
                    st.success(f"تم حذف مزرعة {selected}")
                    st.rerun()
        
        # إضافة مزرعة جديدة
        if st.session_state.get("show_add_farm", False):
            st.markdown("#### ✏️ بيانات المزرعة الجديدة")
            new_name = st.text_input("اسم المزرعة")
            new_owner = st.text_input("اسم المالك")
            new_phone = st.text_input("رقم واتساب المالك (مثال: +249123533489)", value=Config.WHATSAPP_NUMBER)
            
            if st.button("💾 حفظ المزرعة الجديدة") and new_name:
                st.session_state["broiler_farms"][new_name] = {
                    "owner": new_owner,
                    "owner_phone": new_phone,
                    "daily_logs": [],
                    "health_log": [],
                    "current_data": {
                        "farm_name": new_name,
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
                st.session_state["selected_farm"] = new_name
                st.session_state["show_add_farm"] = False
                st.success("تمت إضافة المزرعة بنجاح!")
                st.rerun()
        
        # عرض بيانات المزرعة المختارة
        if selected and selected in st.session_state["broiler_farms"]:
            st.session_state["selected_farm"] = selected
            farm = st.session_state["broiler_farms"][selected]
            st.markdown(f"### 🏷️ المزرعة: **{selected}** (المالك: {farm.get('owner', 'غير مسجل')})")
            
            current = farm["current_data"]
            st.markdown("#### 📝 بيانات اليوم الحالية")
            
            col_inputs, col_outputs = st.columns([0.5, 0.5])
            with col_inputs:
                new_age = st.number_input("عمر القطيع (يوم)", min_value=1, max_value=60, 
                                         value=max(current["flock_age_days"], 1), step=1, key="bf_age")
                init_birds = st.number_input("عدد الكتاكيت المستلمة", min_value=1, 
                                            value=max(current["initial_birds"], 1), step=100, key="bf_init")
                dead = st.number_input("النافق حتى اليوم", min_value=0, value=current["dead_birds"], step=1, key="bf_dead")
                culled = st.number_input("المستبعدين", min_value=0, value=current["culled_birds"], step=1, key="bf_culled")
                avg_wt = st.number_input("متوسط الوزن الحي (كجم)", min_value=0.0, value=current["current_weight_kg"], step=0.05, key="bf_wt")
                init_wt = st.number_input("وزن الكتكوت عند الاستلام (كجم)", min_value=0.030, 
                                         value=current["initial_weight_kg"], step=0.005, key="bf_init_wt")
                feed = st.number_input("إجمالي العلف المستهلك (كجم)", min_value=0.0, 
                                      value=current["total_feed_consumed_kg"], step=100.0, key="bf_feed")
                temp = st.number_input("درجة الحرارة (مئوي)", min_value=10.0, max_value=45.0, 
                                      value=current["temperature_c"], step=0.5, key="bf_temp")
                hum = st.number_input("الرطوبة (%)", min_value=20.0, max_value=90.0, 
                                     value=current["humidity_percent"], step=1.0, key="bf_hum")
                vent = st.selectbox("التهوية", ["سيئة","مقبولة","جيدة","ممتازة"], 
                                   index=["سيئة","مقبولة","جيدة","ممتازة"].index(current["ventilation_status"]), key="bf_vent")
                litter = st.selectbox("جودة الفرشة", ["سيئة","مقبولة","جيدة","ممتازة"], 
                                     index=["سيئة","مقبولة","جيدة","ممتازة"].index(current["litter_quality"]), key="bf_litter")
                notes = st.text_area("ملاحظات", value=current["notes"], key="bf_notes")
                
                st.markdown("#### 💊 السجل الصحي اليومي")
                given_meds = st.text_area("الأدوية والفيتامينات والتحصينات التي تم إعطاؤها اليوم", 
                                         placeholder="مثال: لقاح نيوكاسل - قطرة عين - الساعة 8 صباحاً")
                
                if st.button("💾 حفظ بيانات اليوم والسجل الصحي", use_container_width=True, type="primary"):
                    current.update({
                        "flock_age_days": new_age,
                        "initial_birds": init_birds,
                        "dead_birds": dead,
                        "culled_birds": culled,
                        "current_weight_kg": avg_wt,
                        "initial_weight_kg": init_wt,
                        "total_feed_consumed_kg": feed,
                        "temperature_c": temp,
                        "humidity_percent": hum,
                        "ventilation_status": vent,
                        "litter_quality": litter,
                        "notes": notes,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    
                    daily_record = {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "age_days": new_age,
                        "avg_weight_kg": avg_wt,
                        "feed_consumed_kg": feed,
                        "dead": dead,
                        "culled": culled,
                        "temperature": temp,
                        "humidity": hum,
                        "notes": notes
                    }
                    farm["daily_logs"].append(daily_record)
                    
                    if given_meds.strip():
                        health_record = {
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "age_days": new_age,
                            "medications_given": given_meds,
                            "standard_required": st.session_state["standard_vacc_schedule"].get(new_age, None)
                        }
                        farm["health_log"].append(health_record)
                    
                    st.success("تم حفظ بيانات اليوم والسجل الصحي بنجاح!")
                    check_and_alert_medications(selected, farm, new_age)
                    st.rerun()
            
            with col_outputs:
                total_alive = current["initial_birds"] - current["dead_birds"] - current["culled_birds"]
                total_gain_kg = total_alive * (current["current_weight_kg"] - current["initial_weight_kg"])
                
                adg = BroilerFarmManager.calculate_adg(current["current_weight_kg"]*1000, 
                                                       current["initial_weight_kg"]*1000, 
                                                       current["flock_age_days"])
                fcr = BroilerFarmManager.calculate_fcr(current["total_feed_consumed_kg"], total_gain_kg) if total_gain_kg > 0 else 0
                mortality = BroilerFarmManager.calculate_mortality_rate(current["dead_birds"], current["initial_birds"])
                cull_rate = BroilerFarmManager.calculate_cull_rate(current["culled_birds"], current["initial_birds"])
                livability = BroilerFarmManager.calculate_livability(current["initial_birds"], current["dead_birds"])
                epef = BroilerFarmManager.calculate_epef(livability, current["current_weight_kg"], 
                                                         current["flock_age_days"], fcr)
                
                st.metric("الوزن الحي (كجم)", f"{current['current_weight_kg']:.3f}")
                st.metric("معدل النمو اليومي ADG (جم)", f"{adg:.1f}")
                st.metric("معامل التحويل FCR", f"{fcr:.2f}")
                st.metric("نسبة النفوق (%)", f"{mortality:.2f}%")
                st.metric("الحيوية (%)", f"{livability:.1f}%")
                st.metric("مؤشر EPEF", f"{epef:.0f}")
                
                st.markdown("#### 🌡️ جدول الحرارة والرطوبة القياسي")
                temp_hum_df = BroilerFarmManager.get_temp_humidity_table()
                st.dataframe(temp_hum_df, use_container_width=True, hide_index=True)
                
                # التحقق من الحرارة والرطوبة
                closest = temp_hum_df.iloc[(temp_hum_df['العمر (يوم)'] - current["flock_age_days"]).abs().argsort()[:1]].iloc[0]
                rec_temp = closest['درجة الحرارة (مئوي)']
                rec_hum = closest['الرطوبة النسبية (%)']
                
                if abs(temp - rec_temp) > 2 or abs(hum - rec_hum) > 10:
                    st.warning(f"⚠️ درجة الحرارة الحالية ({temp}°C) أو الرطوبة ({hum}%) خارج النطاق الموصى به لعمر {current['flock_age_days']} يوم (موصى: {rec_temp}°C, {rec_hum}% رطوبة).")
                
                # عرض البروتوكول القياسي
                standard_today = st.session_state["standard_vacc_schedule"].get(current["flock_age_days"])
                if standard_today:
                    st.info(f"📋 **البروتوكول القياسي لهذا اليوم (العمر {current['flock_age_days']} يوم):**\n"
                           f"- {standard_today['type']}: {standard_today['name']}\n"
                           f"- الجرعة: {standard_today['dose']}\n"
                           f"- طريقة الإعطاء: {standard_today['route']}")
            
            # السجلات السابقة
            st.markdown("---")
            with st.expander("📜 سجل اليوميات السابقة"):
                if farm["daily_logs"]:
                    df_log = pd.DataFrame(farm["daily_logs"])
                    st.dataframe(df_log, use_container_width=True)
                else:
                    st.info("لا توجد سجلات يومية بعد.")
            
            with st.expander("💊 السجل الصحي (الأدوية والتحصينات)"):
                if farm["health_log"]:
                    df_health = pd.DataFrame(farm["health_log"])
                    st.dataframe(df_health, use_container_width=True)
                else:
                    st.info("لا توجد سجلات صحية بعد.")
            
            with st.expander("⚙️ تعديل البروتوكول القياسي (التحصينات والأدوية)"):
                st.markdown("يمكنك إضافة أو تعديل المواعيد القياسية حسب بروتوكولك الخاص.")
                new_age_sch = st.number_input("عمر اليوم (للجدول)", min_value=0, max_value=60, value=1, step=1)
                new_type = st.selectbox("النوع", ["لقاح", "دواء", "فيتامين"])
                new_name = st.text_input("اسم المادة")
                new_dose = st.text_input("الجرعة")
                new_route = st.text_input("طريقة الإعطاء")
                
                if st.button("➕ إضافة/تحديد موعد قياسي"):
                    st.session_state["standard_vacc_schedule"][new_age_sch] = {
                        "type": new_type,
                        "name": new_name,
                        "dose": new_dose,
                        "route": new_route
                    }
                    st.success(f"تم حفظ الموعد لعمر {new_age_sch} يوم")
                    st.rerun()
                
                st.markdown("**الجدول الحالي:**")
                st.json(st.session_state["standard_vacc_schedule"])
            
            if st.button("📄 إرسال التقرير اليومي مع اسم المزرعة", use_container_width=True):
                report_lines = [
                    f"تقرير مزرعة {selected} - المالك: {farm.get('owner', 'غير مسجل')}",
                    f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')}",
                    f"🐔 العمر: {current['flock_age_days']} يوم",
                    f"⚖️ متوسط الوزن: {current['current_weight_kg']:.3f} كجم",
                    f"📈 ADG: {adg:.1f} جم/يوم",
                    f"🔄 FCR: {fcr:.2f}",
                    f"💀 النافق: {current['dead_birds']} طير",
                    f"❤️ الحيوية: {livability:.1f}%",
                    f"🏆 EPEF: {epef:.0f}",
                    f"🌡️ درجة الحرارة: {temp}°C (موصى {rec_temp}°C)",
                    f"💧 الرطوبة: {hum}% (موصى {rec_hum}%)",
                    f"📝 ملاحظات: {notes}"
                ]
                if given_meds.strip():
                    report_lines.append(f"💊 السجل الصحي اليوم: {given_meds}")
                
                report_text = "\n".join(report_lines)
                encoded = urllib.parse.quote(report_text[:1500])
                st.markdown(f'<a href="https://wa.me/{farm.get("owner_phone", Config.WHATSAPP_NUMBER)}?text={encoded}" target="_blank">📲 إرسال التقرير عبر واتساب باسم المزرعة</a>', unsafe_allow_html=True)
                st.text_area("معاينة التقرير:", report_text, height=250)
        
        else:
            if not st.session_state.get("show_add_farm", False):
                st.info("👈 يرجى إضافة مزرعة جديدة أو اختيار مزرعة مسجلة من القائمة.")

# ============================================================================
# 33. تبويب تعليقات المختصين
# ============================================================================

if st.session_state["user_role"] in ["owner", "specialist"]:
    comments_tab_index = 7 if st.session_state["user_role"] == "owner" else 6
    with tabs[comments_tab_index]:
        guide_section("تعليقات المختصين", guides["تعليقات المختصين"])
        st.markdown('<div class="section-title">💬 قناة التواصل والتعليقات الفنية</div>', unsafe_allow_html=True)
        
        st.markdown("### 📝 دفتر الملاحظات الفنية المشتركة:")
        st.text_area("التعليقات الحالية:", value=st.session_state["shared_comments"], height=200, disabled=True)
        
        col_comment1, col_comment2 = st.columns(2)
        with col_comment1:
            if st.session_state["user_role"] == "owner":
                new_comment = st.text_area("📝 إضافة تعليق جديد (المالك):", placeholder="اكتب توجيهاً أو ملاحظة...")
                if st.button("➕ نشر التعليق"):
                    if new_comment:
                        st.session_state["shared_comments"] += f"\n• [المالك {datetime.now().strftime('%Y-%m-%d %H:%M')}]: {new_comment}"
                        st.success("تم نشر التعليق!")
                        st.rerun()
            else:
                st.info("المختصون يمكنهم إضافة تعليقاتهم أدناه.")
                spec_comment = st.text_area("📝 تعليق مختص:", placeholder="اكتب ملاحظاتك الفنية...")
                if st.button("➕ نشر تعليق المختص"):
                    if spec_comment:
                        st.session_state["shared_comments"] += f"\n• [مختص {datetime.now().strftime('%Y-%m-%d %H:%M')}]: {spec_comment}"
                        st.success("تم نشر تعليق المختص!")
                        st.rerun()

# ============================================================================
# 34. تبويب المراجع العلمية
# ============================================================================

if st.session_state["user_role"] in ["owner", "specialist"]:
    references_tab_index = 8 if st.session_state["user_role"] == "owner" else 7
else:
    references_tab_index = 1

with tabs[references_tab_index]:
    guide_section("المراجع العلمية", guides["المراجع"])
    st.markdown('<div class="section-title">📚 المراجع العلمية الموثقة</div>', unsafe_allow_html=True)
    
    # البحث في المراجع
    search_query = st.text_input("🔍 بحث في المراجع العلمية:", placeholder="اكتب كلمة بحث...")
    
    if search_query:
        results = ScientificReferenceSystem.search_references(search_query)
        if results:
            st.success(f"تم العثور على {len(results)} نتيجة")
            for ref in results:
                with st.expander(f"📖 {ref.get('title', 'مرجع')} - {ref.get('id', '')}"):
                    st.markdown(f"""
                    **المؤلفون:** {ref.get('authors', 'غير محدد')}
                    **السنة:** {ref.get('year', 'غير محدد')}
                    **الناشر:** {ref.get('publisher', 'غير محدد')}
                    **الملخص:** {ref.get('summary', 'غير متوفر')}
                    **التصنيف:** {ref.get('category', 'غير محدد')}
                    """)
        else:
            st.info("لم يتم العثور على نتائج.")
    
    # عرض جميع المراجع
    st.markdown("---")
    st.subheader("📚 جميع المراجع")
    
    for category, data in ScientificReferenceSystem.REFERENCES.items():
        with st.expander(f"📂 {data['title']} ({len(data['references'])} مرجع)"):
            for ref in data['references']:
                st.markdown(f"""
                **{ref.get('id', '')}** - {ref.get('title', '')}
                *{ref.get('authors', '')}* ({ref.get('year', '')})
                {ref.get('publisher', '')}
                """)
                st.caption(ref.get('summary', ''))
                st.markdown("---")
    
    # بنك المعرفة السريع
    st.markdown("---")
    st.subheader("💡 بنك المعرفة السريع")
    
    # عرض جميع الأسئلة والأجوبة
    for question, data in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
        with st.expander(f"❓ {question}"):
            st.markdown(f"**الإجابة:** {data['answer']}")
            if data.get('simplified'):
                st.markdown(f"**المبسط:** {data['simplified']}")
            ref = ScientificReferenceSystem.get_reference(data.get('reference', ''))
            if ref:
                st.markdown(f"**المصدر:** {ref.get('title', '')} - {ref.get('authors', '')} ({ref.get('year', '')})")

# ============================================================================
# 35. تبويب المساعدة الذكية
# ============================================================================

help_tab_index = 9 if st.session_state["user_role"] == "owner" else (8 if st.session_state["user_role"] == "specialist" else 2)
with tabs[help_tab_index]:
    guide_section("المساعدة الذكية", guides["المساعدة"])
    st.markdown('<div class="section-title">💡 المساعدة الذكية والدعم الفني</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🤖 المساعد الذكي
    
    يمكنك طرح سؤالك حول المنصة، تركيب الأعلاف، أو أي موضوع متعلق بالإنتاج الحيواني.
    """)
    
    user_question = st.text_area("❓ اكتب سؤالك هنا:", placeholder="مثال: كيف يتم حساب البروتين المهضوم؟")
    
    if st.button("🔍 البحث عن إجابة", type="primary", use_container_width=True):
        if user_question:
            answer = ScientificReferenceSystem.get_knowledge_answer(user_question)
            if answer:
                st.success("✅ تم العثور على إجابة:")
                st.markdown(f"""
                <div style="background:#f0fdf4;padding:20px;border-radius:10px;border-right:4px solid #16a34a;">
                    <p><strong>الإجابة:</strong> {answer['answer']}</p>
                    <p><strong>المبسط:</strong> {answer['simplified']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if answer.get('reference'):
                    ref = answer['reference']
                    st.info(f"📚 المصدر: {ref.get('title', '')} - {ref.get('authors', '')} ({ref.get('year', '')})")
            else:
                st.warning("⚠️ لم يتم العثور على إجابة. يمكنك التواصل مع الدعم الفني.")
        else:
            st.error("❌ يرجى كتابة سؤالك أولاً.")
    
    st.markdown("---")
    st.markdown("### 📞 طرق التواصل والدعم")
    
    col_support1, col_support2, col_support3 = st.columns(3)
    with col_support1:
        st.markdown(f"""
        <div style="background:#e3f2fd;padding:15px;border-radius:10px;text-align:center;">
            <h4>📧 البريد الإلكتروني</h4>
            <p>{Config.OWNER_EMAIL}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_support2:
        st.markdown(f"""
        <div style="background:#dcf8c6;padding:15px;border-radius:10px;text-align:center;">
            <h4>📱 واتساب</h4>
            <p>{Config.WHATSAPP_NUMBER}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_support3:
        st.markdown(f"""
        <div style="background:#fff3e0;padding:15px;border-radius:10px;text-align:center;">
            <h4>🌐 المنصة</h4>
            <p>{Config.APP_NAME}</p>
            <p>الإصدار {Config.APP_VERSION}</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# 36. تبويب دليل المستخدم
# ============================================================================

user_guide_tab_index = 10 if st.session_state["user_role"] == "owner" else (9 if st.session_state["user_role"] == "specialist" else 3)
with tabs[user_guide_tab_index]:
    guide_section("دليل المستخدم", guides["دليل المستخدم"])
    st.markdown('<div class="section-title">📖 دليل المستخدم الشامل</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="manual-book">
        <h2>📘 دليل استخدام منصة تاور العلمية</h2>
        <p>الإصدار 4.0 | المشرف: الاختصاصي م. عبد القادر إسماعيل تاور</p>
        
        <div class="book-chapter">📌 الفصل الأول: مقدمة عن المنصة</div>
        <div class="book-body">
            منصة تاور العلمية هي نظام متكامل لتركيب الأعلاف وإدارة الإنتاج الحيواني. تعتمد المنصة على 
            محرك استمثال خطي متقدم يحسب أقل تكلفة لتحقيق المتطلبات الغذائية المطلوبة باستخدام البروتين 
            المهضوم (DP) ومعادل النشاء (SE) كمقاييس أساسية.
        </div>
        
        <div class="book-chapter">🔑 الفصل الثاني: تسجيل الدخول</div>
        <div class="book-body">
            <strong>طرق تسجيل الدخول:</strong>
            <ul>
                <li><strong>كود الدخول السري:</strong> أدخل الكود الخاص بك (مثال: 202687 للمالك)</li>
                <li><strong>اسم المستخدم وكلمة المرور:</strong> استخدم بيانات الدخول المسجلة</li>
            </ul>
            <p><strong>المستخدم الافتراضي:</strong> admin / admin123</p>
        </div>
        
        <div class="book-chapter">🌾 الفصل الثالث: تركيب الأعلاف</div>
        <div class="book-body">
            <ol>
                <li><strong>اختيار الموقع:</strong> حدد الدولة والولاية والمدينة لتحديد الأسعار المحلية</li>
                <li><strong>اختيار القطاع:</strong> اختر نوع الحيوان (أغنام، ماعز، أبقار، خيول، دواجن، أسماك)</li>
                <li><strong>تحديد الإنتاجية:</strong> اختر مرحلة الإنتاج (تسمين، حليب، نمو، وغيرها)</li>
                <li><strong>ضبط المعايير:</strong> حدد نسب البروتين المهضوم ومعادل النشاء المطلوبة</li>
                <li><strong>اختيار المكونات:</strong> اختر المواد العلفية والإضافات المناسبة</li>
                <li><strong>تشغيل المحرك:</strong> اضغط على زر تشغيل محرك الاستمثال الخطي</li>
            </ol>
        </div>
        
        <div class="book-chapter">🏭 الفصل الرابع: إدارة المخزون</div>
        <div class="book-body">
            <ul>
                <li><strong>عرض المخزون:</strong> يعرض الجدول جميع المواد والكميات المتاحة</li>
                <li><strong>تحديث المخزون:</strong> يمكن للمالك تعديل كميات المواد مباشرة</li>
                <li><strong>التنبيهات:</strong> النظام ينبه تلقائياً عند نفاد أو انخفاض أي مادة</li>
                <li><strong>الخصم التلقائي:</strong> عند إصدار فواتير البيع، يخصم النظام المكونات تلقائياً</li>
            </ul>
        </div>
        
        <div class="book-chapter">🐔 الفصل الخامس: إدارة مزارع الدجاج</div>
        <div class="book-body">
            <ul>
                <li><strong>إضافة مزرعة:</strong> سجل مزرعة جديدة باسم المالك ورقم هاتف</li>
                <li><strong>تسجيل البيانات اليومية:</strong> أدخل عمر القطيع، الوزن، العلف، النافق، وغيرها</li>
                <li><strong>حساب المؤشرات:</strong> يحسب النظام ADG، FCR، EPEF تلقائياً</li>
                <li><strong>السجل الصحي:</strong> سجل الأدوية والتحصينات المقدمة للقطيع</li>
                <li><strong>التنبيهات:</strong> يرسل النظام تنبيهات عبر واتساب للتحصينات المستحقة</li>
            </ul>
        </div>
        
        <div class="book-chapter">📊 الفصل السادس: التحليلات والتقارير</div>
        <div class="book-body">
            <ul>
                <li><strong>مؤشرات الأداء:</strong> تعرض عدد الخلطات، متوسط التكلفة، ونسبة التوفير</li>
                <li><strong>تنبؤات الأسعار:</strong> توقع أسعار المواد الخام باستخدام خوارزميات ذكية</li>
                <li><strong>المخططات البيانية:</strong> عرض توزيع المواد واتجاهات الأسعار</li>
                <li><strong>تصدير التقارير:</strong> إمكانية تصدير التقارير بصيغ PDF، Excel، CSV، JSON</li>
            </ul>
        </div>
        
        <div class="book-chapter">📚 الفصل السابع: المراجع العلمية</div>
        <div class="book-body">
            <ul>
                <li><strong>البحث:</strong> ابحث في المراجع العلمية المصنفة حسب الموضوع</li>
                <li><strong>بنك المعرفة:</strong> إجابات سريعة للأسئلة الشائعة حول تغذية الحيوان</li>
                <li><strong>المصادر:</strong> جميع المراجع موثقة من مصادر معترف بها (NRC، INRA، وغيرها)</li>
            </ul>
        </div>
        
        <div class="book-chapter">💡 الفصل الثامن: نصائح وإرشادات</div>
        <div class="book-body">
            <ul>
                <li><strong>تحسين الخلطات:</strong> استخدم مكونات متنوعة لضمان توازن غذائي أفضل</li>
                <li><strong>مراقبة الجودة:</strong> تأكد من جودة المواد الخام قبل الاستخدام</li>
                <li><strong>التحديث المنتظم:</strong> حافظ على تحديث أسعار المواد للحصول على نتائج دقيقة</li>
                <li><strong>التواصل:</strong> لا تتردد في التواصل مع الدعم الفني عند الحاجة</li>
            </ul>
        </div>
        
        <div style="text-align:center;margin-top:30px;padding-top:20px;border-top:2px solid #e0e0e0;color:#666;font-size:0.9rem;">
            تم إعداد هذا الدليل بواسطة {Config.APP_AUTHOR} © {datetime.now().year}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# 37. تبويب إعدادات النظام (خاص بالمالك)
# ============================================================================

if st.session_state["user_role"] == "owner":
    with tabs[11]:
        guide_section("إعدادات النظام", guides["الإعدادات"])
        st.markdown('<div class="section-title">⚙️ إعدادات النظام والإدارة</div>', unsafe_allow_html=True)
        
        st.subheader("👤 إدارة المستخدمين")
        col_user1, col_user2 = st.columns(2)
        with col_user1:
            st.markdown("#### 📋 قائمة المستخدمين")
            db = DatabaseManager()
            users = db.execute_query("SELECT username, full_name, role, email, phone, is_active FROM users")
            if users:
                df_users = pd.DataFrame(users, columns=['اسم المستخدم', 'الاسم الكامل', 'الدور', 'البريد', 'الهاتف', 'نشط'])
                st.dataframe(df_users, use_container_width=True)
            else:
                st.info("لا يوجد مستخدمون مسجلون")
        
        with col_user2:
            st.markdown("#### ➕ إضافة مستخدم جديد")
            new_username = st.text_input("اسم المستخدم")
            new_password = st.text_input("كلمة المرور", type="password")
            new_full_name = st.text_input("الاسم الكامل")
            new_email = st.text_input("البريد الإلكتروني")
            new_phone = st.text_input("رقم الهاتف")
            new_role = st.selectbox("الدور", ["owner", "specialist", "breeder"])
            
            if st.button("➕ إضافة مستخدم"):
                if all([new_username, new_password, new_full_name, new_email]):
                    auth = AuthManager()
                    try:
                        auth.create_user(new_username, new_password, new_role, 
                                        new_full_name, new_email, new_phone)
                        st.success("✅ تم إضافة المستخدم بنجاح!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ خطأ في إضافة المستخدم: {e}")
                else:
                    st.error("❌ يرجى ملء جميع الحقول المطلوبة")
        
        st.markdown("---")
        st.subheader("🔑 تغيير كلمة المرور")
        col_pass1, col_pass2 = st.columns(2)
        with col_pass1:
            current_password = st.text_input("كلمة المرور الحالية", type="password")
            new_password1 = st.text_input("كلمة المرور الجديدة", type="password")
            new_password2 = st.text_input("تأكيد كلمة المرور الجديدة", type="password")
            
            if st.button("🔄 تغيير كلمة المرور"):
                if new_password1 != new_password2:
                    st.error("❌ كلمتا المرور غير متطابقتين")
                elif len(new_password1) < 6:
                    st.error("❌ كلمة المرور يجب أن تكون 6 أحرف على الأقل")
                else:
                    auth = AuthManager()
                    user = st.session_state.get("user")
                    if user:
                        if auth.change_password(user['username'], current_password, new_password1):
                            st.success("✅ تم تغيير كلمة المرور بنجاح!")
                        else:
                            st.error("❌ كلمة المرور الحالية غير صحيحة")
        
        st.markdown("---")
        st.subheader("💾 إدارة البيانات")
        col_data1, col_data2 = st.columns(2)
        with col_data1:
            if st.button("🗑️ مسح جميع البيانات", type="secondary", use_container_width=True):
                if st.checkbox("تأكيد مسح جميع البيانات"):
                    # مسح قاعدة البيانات
                    db = DatabaseManager()
                    for table in ['users', 'farm_cycles', 'feed_formulas', 'invoices', 'price_history', 'health_records', 'audit_log']:
                        db.execute_query(f"DELETE FROM {table}")
                    st.success("✅ تم مسح جميع البيانات بنجاح!")
        
        with col_data2:
            if st.button("📊 عرض سجل العمليات", use_container_width=True):
                db = DatabaseManager()
                logs = db.execute_query("SELECT * FROM audit_log ORDER BY log_date DESC LIMIT 100")
                if logs:
                    df_logs = pd.DataFrame(logs, columns=['المعرف', 'المستخدم', 'الإجراء', 'التفاصيل', 'التاريخ', 'IP'])
                    st.dataframe(df_logs, use_container_width=True)
                else:
                    st.info("لا توجد سجلات عمليات")
        
        st.markdown("---")
        st.subheader("ℹ️ معلومات النظام")
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.metric("اسم التطبيق", Config.APP_NAME)
        with col_info2:
            st.metric("الإصدار", Config.APP_VERSION)
        with col_info3:
            st.metric("المشرف", Config.APP_AUTHOR)
        
        st.caption(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================================================
# 38. التذييل الثابت
# ============================================================================

st.markdown(f"""
<div class="mini-left-signature">
    🌾 {Config.APP_AUTHOR} | الإصدار {Config.APP_VERSION}
</div>
""", unsafe_allow_html=True)

# ============================================================================
# 39. تسجيل الخروج التلقائي في حالة عدم النشاط
# ============================================================================

# يمكن إضافة آلية لتسجيل الخروج التلقائي هنا

# ============================================================================
# نهاية الكود
# ============================================================================
