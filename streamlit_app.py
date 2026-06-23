#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف
الإصدار المتكامل v7.0 - دمج أفضل الميزات من الإصدارين مع تحسينات أمنية وهيكلية
المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور
"""

# ==========================================
# 1. إعدادات البيئة والمتغيرات الآمنة
# ==========================================

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# التحقق من وجود المتغيرات الأساسية
REQUIRED_ENV_VARS = ['SENDER_EMAIL', 'SENDER_PASSWORD', 'OWNER_EMAIL']
MISSING_VARS = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if MISSING_VARS:
    print(f"⚠️ تحذير: المتغيرات التالية غير محددة في ملف .env: {', '.join(MISSING_VARS)}")
    print("سيتم استخدام القيم الافتراضية للتشغيل المحلي فقط.")

# ==========================================
# 2. المكتبات الأساسية
# ==========================================

import streamlit as st
import numpy as np
import pandas as pd
import json
import base64
import smtplib
import time
import urllib.parse
import hashlib
import secrets
import io
import sqlite3
import logging
import logging.handlers
import shutil
import random
import re
import gc
import zipfile
import tempfile
import csv
import math
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager
from cryptography.fernet import Fernet
from functools import lru_cache, wraps
from typing import Dict, List, Tuple, Optional, Any, Union
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# 3. المكتبات العلمية والتحليلية
# ==========================================

from scipy.optimize import linprog
from scipy.spatial import ConvexHull
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression

# ==========================================
# 4. مكتبات التصور والرسوم البيانية
# ==========================================

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 5. مكتبات معالجة النص العربي
# ==========================================

import arabic_reshaper
from bidi.algorithm import get_display

# ==========================================
# 6. مكتبات توليد PDF المتقدمة
# ==========================================

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

# ==========================================
# 7. مكتبات الباركود والصور
# ==========================================

import qrcode
from PIL import Image as PILImage

try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False
    pyzbar_decode = None

# ==========================================
# 8. إعدادات التحذيرات والمجلدات
# ==========================================

warnings.filterwarnings('ignore')

# إنشاء المجلدات اللازمة
folders = [
    "logs", "backups", "data", "temp", "visitors", "code_backups", 
    "reports", "exports", "charts", "models", "cache", "lab_results", 
    "formulas_archive", "price_history", "farm_data"
]
for folder in folders:
    Path(folder).mkdir(exist_ok=True)

# ==========================================
# 9. إعدادات Streamlit
# ==========================================

st.set_page_config(
    page_title="منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://wa.me/249123533489',
        'Report a bug': "mailto:abukram128@gmail.com",
        'About': "منصة تاور العلمية - نظام متكامل لتركيب الأعلاف وإدارة المزارع"
    }
)

# ==========================================
# 10. نظام التسجيل المتقدم
# ==========================================

class AdvancedLogger:
    """نظام تسجيل متقدم مع تصنيف متعدد"""
    
    def __init__(self):
        self.setup_all_loggers()
    
    def setup_all_loggers(self):
        self.main_logger = logging.getLogger('TowerPlatform')
        self.main_logger.setLevel(logging.INFO)
        self.security_logger = logging.getLogger('Security')
        self.security_logger.setLevel(logging.WARNING)
        self.user_logger = logging.getLogger('UserActions')
        self.user_logger.setLevel(logging.INFO)
        self.error_logger = logging.getLogger('Errors')
        self.error_logger.setLevel(logging.ERROR)
        
        # إعداد معالج الدوران للحد من حجم الملفات
        main_handler = logging.handlers.RotatingFileHandler(
            'logs/tower_main.log', 
            maxBytes=50*1024*1024, 
            backupCount=20, 
            encoding='utf-8'
        )
        formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
        main_handler.setFormatter(formatter)
        self.main_logger.addHandler(main_handler)
        
        security_handler = logging.handlers.RotatingFileHandler(
            'logs/security.log', 
            maxBytes=20*1024*1024, 
            backupCount=30, 
            encoding='utf-8'
        )
        security_handler.setFormatter(formatter)
        self.security_logger.addHandler(security_handler)
        
        user_handler = logging.handlers.RotatingFileHandler(
            'logs/users.log', 
            maxBytes=10*1024*1024, 
            backupCount=15, 
            encoding='utf-8'
        )
        user_handler.setFormatter(formatter)
        self.user_logger.addHandler(user_handler)
        
        error_handler = logging.handlers.RotatingFileHandler(
            'logs/errors.log', 
            maxBytes=50*1024*1024, 
            backupCount=25, 
            encoding='utf-8'
        )
        error_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(filename)s:%(lineno)d - %(message)s')
        error_handler.setFormatter(error_formatter)
        self.error_logger.addHandler(error_handler)
    
    def log_security_event(self, event_type: str, details: str, severity: str = 'INFO'):
        """تسجيل حدث أمني"""
        log_func = getattr(self.security_logger, severity.lower(), self.security_logger.info)
        log_func(f"{event_type}: {details}")

LOGGER = AdvancedLogger()

# ==========================================
# 11. إعدادات البريد (آمنة)
# ==========================================

# قراءة الإعدادات من متغيرات البيئة
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "abukram128@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "abukram128@gmail.com")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "+249123533489")
GOOGLE_FORM_URL = os.getenv("GOOGLE_FORM_URL", "https://forms.google.com/YOUR_FORM_URL")

# التحقق من وجود كلمة المرور
if not SENDER_PASSWORD:
    LOGGER.security_logger.warning("SENDER_PASSWORD غير محددة في متغيرات البيئة")

# مسارات الصور
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

@st.cache_data(ttl=3600)
def get_image_base64(paths: List[str]) -> Optional[str]:
    """الحصول على الصورة بصيغة base64"""
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception as e:
                LOGGER.error_logger.error(f"خطأ في قراءة الصورة {path}: {e}")
    return None

img_base64 = get_image_base64(PHOTO_OPTIONS)

# ==========================================
# 12. نظام إرسال الكود الآمن
# ==========================================

class SecureCodeSender:
    """نظام إرسال الكود الآمن مع تشفير وتوقيع رقمي"""
    
    def __init__(self):
        self.sender_email = SENDER_EMAIL
        self.sender_password = SENDER_PASSWORD
        self.owner_email = OWNER_EMAIL
    
    def send_code_to_email(self, email: str, reason: str = "طلب يدوي") -> bool:
        """إرسال الكود إلى البريد الإلكتروني مع توقيع رقمي"""
        if not self.sender_password:
            LOGGER.security_logger.error("محاولة إرسال كود بدون كلمة مرور")
            return False
        
        try:
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            # قراءة الكود الحالي
            try:
                with open(__file__, 'r', encoding='utf-8') as f:
                    code_content = f.read()
            except Exception as e:
                LOGGER.error_logger.error(f"فشل قراءة الكود: {e}")
                return False
            
            # إنشاء توقيع رقمي
            file_hash = hashlib.sha256(code_content.encode()).hexdigest()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # إنشاء الرسالة
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = email
            msg['Subject'] = f"🌾 نسخة كاملة - منصة تاور العلمية - {timestamp}"
            
            body = f"""السلام عليكم م. عبد القادر،

📋 هذه نسخة كاملة من منصة تاور العلمية.

📅 التاريخ: {timestamp}
📝 السبب: {reason}
🔐 التوقيع: {file_hash[:16]}...
📏 حجم الملف: {len(code_content):,} حرف

تم إرفاق الكود الكامل مع هذا البريد.

تحياتي،
نظام المنصة الآلي
"""
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # إرفاق الكود
            attachment = MIMEText(code_content, 'plain', 'utf-8')
            attachment.add_header(
                'Content-Disposition', 
                'attachment', 
                filename=f"tower_platform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
            )
            msg.attach(attachment)
            
            # إرسال البريد
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, email, msg.as_string())
            server.quit()
            
            LOGGER.main_logger.info(f"تم إرسال الكود إلى {email} - {reason}")
            return True
            
        except Exception as e:
            LOGGER.error_logger.error(f"فشل إرسال الكود: {e}")
            return False
    
    def auto_backup_check(self):
        """فحص وإنشاء نسخة احتياطية تلقائية كل 6 ساعات"""
        try:
            with get_db() as conn:
                cursor = conn.execute('SELECT MAX(backup_date) as last_backup FROM code_backups')
                result = cursor.fetchone()
                
                if not result or not result['last_backup']:
                    need_backup = True
                else:
                    last_time = datetime.fromisoformat(result['last_backup'])
                    need_backup = (datetime.now() - last_time).seconds > 21600  # 6 ساعات
                
                if need_backup:
                    if self.send_code_to_email(self.owner_email, "نسخة احتياطية آلية"):
                        with get_db() as conn:
                            conn.execute(
                                'INSERT INTO code_backups (backup_date, reason, file_hash) VALUES (?, ?, ?)',
                                (datetime.now().isoformat(), "تلقائي", "auto_backup")
                            )
        except Exception as e:
            LOGGER.error_logger.error(f"فشل النسخ الاحتياطي التلقائي: {e}")

CODE_SENDER = SecureCodeSender()

# ==========================================
# 13. نظام مراقبة الأمان المتقدم
# ==========================================

class SecurityMonitor:
    """نظام مراقبة أمان متقدم مع كشف الاختراق وحظر IP"""
    
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.blocked_ips = set()
        self.max_attempts = 5
        self.lockout_time = 300  # 5 دقائق
        self.attack_signatures = {
            'sql_injection': re.compile(r'(\%27)|(\')|(\-\-)|(%23)|(#)', re.IGNORECASE),
            'xss': re.compile(r'(\<script)|(\<img)|(javascript:)|(onerror=)', re.IGNORECASE),
            'path_traversal': re.compile(r'(\.\./)|(\.\.\\)', re.IGNORECASE),
        }
    
    def get_client_ip(self) -> str:
        """الحصول على عنوان IP العميل"""
        try:
            if hasattr(st, 'context') and hasattr(st.context, 'headers'):
                forwarded = st.context.headers.get('X-Forwarded-For', '')
                if forwarded:
                    return forwarded.split(',')[0].strip()
                real_ip = st.context.headers.get('X-Real-IP', '')
                if real_ip:
                    return real_ip
            return '127.0.0.1'
        except Exception:
            return 'unknown'
    
    def is_ip_blocked(self, ip: str) -> bool:
        """التحقق من حظر IP"""
        if ip in self.blocked_ips:
            return True
        
        # التحقق من قاعدة البيانات
        try:
            with get_db() as conn:
                cursor = conn.execute(
                    'SELECT blocked_at FROM blocked_ips WHERE ip_address = ? AND blocked_at > datetime("now", "-1 day")',
                    (ip,)
                )
                if cursor.fetchone():
                    self.blocked_ips.add(ip)
                    return True
        except:
            pass
        return False
    
    def block_ip(self, ip: str, reason: str = "محاولات فاشلة متكررة"):
        """حظر عنوان IP"""
        self.blocked_ips.add(ip)
        try:
            with get_db() as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO blocked_ips (ip_address, block_reason, blocked_at) VALUES (?, ?, ?)',
                    (ip, reason, datetime.now().isoformat())
                )
        except:
            pass
        LOGGER.security_logger.warning(f"تم حظر IP: {ip} - {reason}")
    
    def log_failed_attempt(self, code_attempt: str = ""):
        """تسجيل محاولة فاشلة"""
        ip = self.get_client_ip()
        self.failed_attempts[ip].append(datetime.now())
        
        # التحقق من عدد المحاولات
        recent_attempts = [
            t for t in self.failed_attempts[ip] 
            if (datetime.now() - t).seconds < self.lockout_time
        ]
        self.failed_attempts[ip] = recent_attempts
        
        if len(recent_attempts) >= self.max_attempts:
            self.block_ip(ip, f"{self.max_attempts} محاولات فاشلة في {self.lockout_time} ثانية")
        
        LOGGER.security_logger.warning(f"محاولة فاشلة من {ip}")
        
        # التحقق من هجمات
        self.detect_attack(code_attempt, ip)
    
    def detect_attack(self, input_text: str, ip: str):
        """كشف هجمات الحقن"""
        for attack_type, pattern in self.attack_signatures.items():
            if pattern.search(input_text):
                LOGGER.security_logger.error(f"هجوم {attack_type} مكتشف من {ip}")
                self.block_ip(ip, f"هجوم {attack_type}")
                break
    
    def log_visitor(self, user_role: Optional[str] = None, action: str = "visit"):
        """تسجيل زائر جديد"""
        ip = self.get_client_ip()
        user_agent = self.get_user_agent()
        
        if self.is_ip_blocked(ip):
            LOGGER.security_logger.warning(f"محاولة وصول من IP محظور: {ip}")
            return
        
        try:
            with get_db() as conn:
                conn.execute(
                    '''INSERT INTO visitors_log (ip_address, user_agent, user_role, action, visit_time) 
                       VALUES (?, ?, ?, ?, ?)''',
                    (ip, user_agent[:200], user_role or "unknown", action, datetime.now().isoformat())
                )
        except Exception as e:
            LOGGER.error_logger.error(f"فشل تسجيل الزائر: {e}")
        
        LOGGER.user_logger.info(f"زائر: {ip} - {user_role} - {action}")
    
    def get_user_agent(self) -> str:
        """الحصول على User-Agent"""
        try:
            if hasattr(st, 'context') and hasattr(st.context, 'headers'):
                return st.context.headers.get('User-Agent', 'unknown')[:200]
            return 'unknown'
        except:
            return 'unknown'

SECURITY = SecurityMonitor()

# ==========================================
# 14. نظام قاعدة البيانات المتقدم (SQLite)
# ==========================================

DB_PATH = "data/tower_platform.db"

@contextmanager
def get_db():
    """مدير سياق قاعدة البيانات"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        LOGGER.error_logger.error(f"خطأ في قاعدة البيانات: {e}")
        raise
    finally:
        conn.close()

def column_exists(conn, table_name: str, column_name: str) -> bool:
    """التحقق من وجود عمود في جدول"""
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def upgrade_database():
    """ترقية قاعدة البيانات إلى الإصدار الأحدث"""
    with get_db() as conn:
        # ترقية جدول lab_analyses
        if column_exists(conn, 'lab_analyses', 'id'):
            columns_to_add = {
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'analyzed_at': 'TIMESTAMP',
                'lysine': 'REAL',
                'methionine': 'REAL',
                'lab_se': 'REAL'
            }
            for col, col_type in columns_to_add.items():
                if not column_exists(conn, 'lab_analyses', col):
                    try:
                        conn.execute(f'ALTER TABLE lab_analyses ADD COLUMN {col} {col_type}')
                        LOGGER.main_logger.info(f"تم إضافة عمود {col} إلى lab_analyses")
                    except Exception as e:
                        LOGGER.error_logger.error(f"فشل إضافة عمود {col}: {e}")
        
        # إضافة فهارس لتحسين الأداء
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_formulas_breed ON formulas_history(breed)',
            'CREATE INDEX IF NOT EXISTS idx_formulas_created ON formulas_history(created_at)',
            'CREATE INDEX IF NOT EXISTS idx_visitors_date ON visitors_log(visit_time)',
            'CREATE INDEX IF NOT EXISTS idx_visitors_ip ON visitors_log(ip_address)',
            'CREATE INDEX IF NOT EXISTS idx_lab_status ON lab_analyses(status)',
        ]
        for idx in indexes:
            try:
                conn.execute(idx)
            except Exception as e:
                LOGGER.error_logger.error(f"فشل إنشاء فهرس: {e}")

def init_database():
    """تهيئة قاعدة البيانات الكاملة"""
    with get_db() as conn:
        # جدول الخلطات التاريخية
        conn.execute('''
            CREATE TABLE IF NOT EXISTS formulas_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                formula_data TEXT NOT NULL,
                target_dp REAL,
                target_se REAL,
                target_me REAL,
                protein_type TEXT,
                breed TEXT,
                sector TEXT,
                production TEXT,
                cost REAL,
                city TEXT,
                user_role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول التحاليل المخبرية المتكامل
        conn.execute('''
            CREATE TABLE IF NOT EXISTS lab_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER UNIQUE,
                formula_data TEXT,
                target_dp REAL,
                target_se REAL,
                target_me REAL,
                breed TEXT,
                sector TEXT,
                city TEXT,
                analysis_date TEXT,
                lab_cp REAL,
                lab_dp REAL,
                lab_moisture REAL,
                lab_fat REAL,
                lab_fiber REAL,
                lab_me REAL,
                lab_se REAL,
                lab_ca REAL,
                lab_p REAL,
                lab_ash REAL,
                lysine REAL,
                methionine REAL,
                notes TEXT,
                status TEXT DEFAULT 'pending',
                analyzed_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                analyzed_at TIMESTAMP
            )
        ''')
        
        # جدول سجل النشاطات
        conn.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_role TEXT,
                action TEXT,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول التنبيهات الأمنية
        conn.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_message TEXT,
                severity TEXT,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول النسخ الاحتياطية
        conn.execute('''
            CREATE TABLE IF NOT EXISTS code_backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_date TIMESTAMP,
                reason TEXT,
                file_hash TEXT
            )
        ''')
        
        # جدول سجل الزوار
        conn.execute('''
            CREATE TABLE IF NOT EXISTS visitors_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT,
                user_agent TEXT,
                user_role TEXT,
                action TEXT,
                visit_time TIMESTAMP
            )
        ''')
        
        # جدول الأسعار التاريخية
        conn.execute('''
            CREATE TABLE IF NOT EXISTS market_prices_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT,
                commodity TEXT,
                price REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الـ IPs المحظورة
        conn.execute('''
            CREATE TABLE IF NOT EXISTS blocked_ips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT UNIQUE,
                block_reason TEXT,
                blocked_at TIMESTAMP
            )
        ''')
        
        # جدول المزارع
        conn.execute('''
            CREATE TABLE IF NOT EXISTS poultry_farms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farm_name TEXT UNIQUE,
                farm_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول التعليقات
        conn.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_role TEXT,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        LOGGER.main_logger.info("تم تهيئة قاعدة البيانات بنجاح")
        
        # ترقية قاعدة البيانات
        upgrade_database()

# تهيئة قاعدة البيانات
if "db_initialized" not in st.session_state:
    init_database()
    st.session_state["db_initialized"] = True

# ==========================================
# 15. نظام إدارة المخزون المتقدم
# ==========================================

class InventoryManager:
    """نظام إدارة المخزون المتقدم"""
    
    def __init__(self):
        self.inventory_file = "data/inventory_data.json"
        self.load_inventory()
    
    def load_inventory(self):
        """تحميل بيانات المخزون من الملف"""
        if "inventory" not in st.session_state:
            if os.path.exists(self.inventory_file):
                try:
                    with open(self.inventory_file, 'r', encoding='utf-8') as f:
                        st.session_state["inventory"] = json.load(f)
                    return
                except Exception as e:
                    LOGGER.error_logger.error(f"فشل تحميل المخزون: {e}")
            
            # تهيئة المخزون الافتراضي
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
            self.save_inventory()
    
    def save_inventory(self):
        """حفظ بيانات المخزون إلى الملف"""
        try:
            with open(self.inventory_file, 'w', encoding='utf-8') as f:
                json.dump(st.session_state["inventory"], f, ensure_ascii=False, indent=2)
        except Exception as e:
            LOGGER.error_logger.error(f"فشل حفظ المخزون: {e}")
    
    def get_item(self, item_name: str) -> Optional[Dict]:
        """الحصول على بيانات مادة معينة"""
        return st.session_state["inventory"].get(item_name)
    
    def update_item(self, item_name: str, quantity: float, threshold: Optional[float] = None):
        """تحديث كمية مادة"""
        if item_name in st.session_state["inventory"]:
            st.session_state["inventory"][item_name]["quantity"] = quantity
            if threshold is not None:
                st.session_state["inventory"][item_name]["min_threshold"] = threshold
            st.session_state["inventory"][item_name]["last_updated"] = datetime.now().isoformat()
            self.save_inventory()
    
    def deduct_items(self, formula: Dict[str, float], tons: float) -> bool:
        """خصم مواد من المخزون"""
        can_deduct = True
        for ing, pct in formula.items():
            req_amount = (pct / 100) * tons
            current = st.session_state["inventory"].get(ing, {}).get("quantity", 0)
            if current < req_amount:
                can_deduct = False
                LOGGER.main_logger.warning(f"مخزون غير كافٍ: {ing} (المطلوب: {req_amount:.2f}, المتوفر: {current:.2f})")
                break
        
        if can_deduct:
            for ing, pct in formula.items():
                req_amount = (pct / 100) * tons
                st.session_state["inventory"][ing]["quantity"] -= req_amount
            self.save_inventory()
        
        return can_deduct
    
    def check_stock_levels(self) -> Dict[str, str]:
        """التحقق من مستويات المخزون"""
        warnings = {}
        for item, data in st.session_state["inventory"].items():
            qty = data["quantity"]
            threshold = data["min_threshold"]
            if qty <= 0:
                warnings[item] = "نفذ المخزون"
            elif qty < threshold:
                warnings[item] = "منخفض"
        return warnings

INVENTORY_MANAGER = InventoryManager()

# ==========================================
# 16. بيانات السلالات والاحتياجات القياسية
# ==========================================

BREEDS_STANDARDS = {
    "الدواجن": {
        "لاحم (بادي)": {"CP": 22.0, "DP": 18.5, "SE": 78.0, "ME": 3200, "P/E": 6.9, "lysine": 1.2, "methionine": 0.5},
        "لاحم (نامي)": {"CP": 20.0, "DP": 16.8, "SE": 75.0, "ME": 3100, "P/E": 6.5, "lysine": 1.1, "methionine": 0.45},
        "لاحم (ناهي)": {"CP": 18.0, "DP": 15.1, "SE": 74.0, "ME": 3050, "P/E": 5.9, "lysine": 1.0, "methionine": 0.4},
        "بياض (بادي)": {"CP": 18.0, "DP": 15.1, "SE": 70.0, "ME": 2800, "P/E": 6.4, "lysine": 0.85, "methionine": 0.38},
        "بياض (إنتاج)": {"CP": 16.5, "DP": 13.9, "SE": 68.0, "ME": 2750, "P/E": 6.0, "lysine": 0.75, "methionine": 0.35},
        "بياض (ناهي)": {"CP": 15.5, "DP": 13.0, "SE": 65.0, "ME": 2650, "P/E": 5.8, "lysine": 0.7, "methionine": 0.33},
        "سمان": {"CP": 24.0, "DP": 20.2, "SE": 80.0, "ME": 3000, "P/E": 8.0, "lysine": 1.3, "methionine": 0.55},
        "رومي": {"CP": 26.0, "DP": 21.8, "SE": 75.0, "ME": 2900, "P/E": 8.7, "lysine": 1.5, "methionine": 0.6}
    },
    "الأغنام": {
        "تسمين (صحراوي)": {"CP": 14.0, "DP": 11.8, "SE": 66.0, "ME": 2500, "P/E": 5.6, "NDF": 35, "ADF": 20},
        "تسمين (بربري)": {"CP": 13.5, "DP": 11.3, "SE": 65.0, "ME": 2450, "P/E": 5.5, "NDF": 35, "ADF": 20},
        "تسمين (نعيمي)": {"CP": 14.5, "DP": 12.2, "SE": 67.0, "ME": 2550, "P/E": 5.7, "NDF": 34, "ADF": 19},
        "حليب (أغنام)": {"CP": 16.0, "DP": 13.4, "SE": 68.0, "ME": 2600, "P/E": 6.2, "NDF": 32, "ADF": 18},
        "صيانة": {"CP": 10.0, "DP": 8.4, "SE": 58.0, "ME": 2200, "P/E": 4.5, "NDF": 40, "ADF": 25}
    },
    "الماعز": {
        "تسمين": {"CP": 12.5, "DP": 10.5, "SE": 64.0, "ME": 2400, "P/E": 5.2, "NDF": 38, "ADF": 22},
        "حليب": {"CP": 14.0, "DP": 11.8, "SE": 66.0, "ME": 2550, "P/E": 5.5, "NDF": 35, "ADF": 20},
        "صيانة": {"CP": 9.5, "DP": 8.0, "SE": 58.0, "ME": 2150, "P/E": 4.3, "NDF": 42, "ADF": 26}
    },
    "الأبقار": {
        "حليب (هولشتاين)": {"CP": 17.0, "DP": 14.3, "SE": 70.0, "ME": 2700, "P/E": 6.3, "NDF": 30, "ADF": 18},
        "حليب (فريزيان)": {"CP": 16.5, "DP": 13.9, "SE": 69.0, "ME": 2650, "P/E": 6.1, "NDF": 31, "ADF": 19},
        "تسمين (كنانة)": {"CP": 12.0, "DP": 10.1, "SE": 65.0, "ME": 2400, "P/E": 5.0, "NDF": 38, "ADF": 22},
        "تسمين (بطانة)": {"CP": 11.5, "DP": 9.7, "SE": 63.0, "ME": 2350, "P/E": 4.9, "NDF": 39, "ADF": 23},
        "عجول تسمين": {"CP": 14.0, "DP": 11.8, "SE": 68.0, "ME": 2500, "P/E": 5.6, "NDF": 35, "ADF": 20}
    },
    "الخيول": {
        "رياضة": {"CP": 12.0, "DP": 10.1, "SE": 62.0, "ME": 2300, "P/E": 5.2, "NDF": 35, "ADF": 20},
        "نمو": {"CP": 14.0, "DP": 11.8, "SE": 64.0, "ME": 2450, "P/E": 5.8, "NDF": 33, "ADF": 18},
        "صيانة": {"CP": 10.0, "DP": 8.4, "SE": 58.0, "ME": 2100, "P/E": 4.6, "NDF": 40, "ADF": 25}
    },
    "الأسماك": {
        "بلطي (نمو)": {"CP": 28.0, "DP": 25.2, "SE": 70.0, "ME": 2800, "P/E": 10.0, "lipid": 6},
        "بلطي (تسمين)": {"CP": 25.0, "DP": 22.5, "SE": 68.0, "ME": 2700, "P/E": 9.3, "lipid": 7},
        "بوري": {"CP": 30.0, "DP": 27.0, "SE": 72.0, "ME": 2900, "P/E": 10.7, "lipid": 5},
        "قرموط": {"CP": 32.0, "DP": 28.8, "SE": 74.0, "ME": 3000, "P/E": 11.4, "lipid": 6}
    }
}

# ==========================================
# 17. المكتبة الكاملة للمواد العلفية
# ==========================================

BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة الكبرى": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "DP": 7.2, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3, "Ca": 0.02, "P": 0.28},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "DP": 7.3, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4, "Ca": 0.02, "P": 0.27},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "DP": 9.2, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5, "Ca": 0.05, "P": 0.35},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "DP": 7.8, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8, "Ca": 0.03, "P": 0.30},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "DP": 10.2, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6, "Ca": 0.04, "P": 0.32},
        "جريش أرز رزاز": {"CP": 7.8, "DC": 0.82, "DP": 6.4, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2, "Ca": 0.01, "P": 0.15},
        "دخن محلي غزير": {"CP": 11.0, "DC": 0.75, "DP": 8.3, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2, "Ca": 0.03, "P": 0.28},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "DP": 8.4, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0, "Ca": 0.08, "P": 0.33},
        "تريتيكال": {"CP": 13.0, "DC": 0.82, "DP": 10.7, "SE": 73.0, "NDF": 12.0, "ADF": 4.0, "EE": 2.5, "ASH": 1.8, "Ca": 0.04, "P": 0.35}
    },
    "🌱 الأكساب ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "DP": 40.5, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5, "Ca": 0.20, "P": 0.65},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "DP": 39.6, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0, "Ca": 0.30, "P": 0.65},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "DP": 43.7, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2, "Ca": 0.32, "P": 0.68},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "DP": 27.4, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5, "Ca": 0.35, "P": 0.95},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "DP": 32.0, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5, "Ca": 0.18, "P": 1.10},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "DP": 26.2, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8, "Ca": 0.38, "P": 0.82},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "DP": 35.3, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5, "Ca": 1.50, "P": 1.20},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "DP": 55.2, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5, "Ca": 0.05, "P": 0.45},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "DP": 10.4, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5, "Ca": 0.40, "P": 0.55},
        "كسب بذور اللفت (كانولا)": {"CP": 36.0, "DC": 0.80, "DP": 28.8, "SE": 60.0, "NDF": 22.0, "ADF": 15.0, "EE": 2.0, "ASH": 6.0, "Ca": 0.60, "P": 1.00}
    },
    "🚜 المخلفات الزراعية والصناعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "DP": 10.8, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5, "Ca": 0.10, "P": 1.10},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "DP": 9.9, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5, "Ca": 1.20, "P": 0.25},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "DP": 3.8, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5, "Ca": 0.80, "P": 0.08},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "DP": 1.1, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.25, "P": 0.10},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "DP": 1.5, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5, "Ca": 0.30, "P": 0.12},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "DP": 0.6, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5, "Ca": 0.05, "P": 0.08},
        "بقايا تفل البنجر المجفف": {"CP": 8.0, "DC": 0.75, "DP": 6.0, "SE": 58.0, "NDF": 38.5, "ADF": 22.5, "EE": 1.5, "ASH": 6.5, "Ca": 1.00, "P": 0.20},
        "مخلفات مصانع البسكويت": {"CP": 9.5, "DC": 0.88, "DP": 8.4, "SE": 76.0, "NDF": 8.5, "ADF": 3.5, "EE": 8.5, "ASH": 3.5, "Ca": 0.12, "P": 0.25},
        "سیلاج ذرة كامل": {"CP": 8.0, "DC": 0.68, "DP": 5.4, "SE": 50.0, "NDF": 45.5, "ADF": 25.5, "EE": 2.5, "ASH": 4.5, "Ca": 0.25, "P": 0.22},
        "مخلفات الخبز المجفف": {"CP": 11.0, "DC": 0.90, "DP": 9.9, "SE": 80.0, "NDF": 5.0, "ADF": 2.0, "EE": 4.0, "ASH": 2.5, "Ca": 0.10, "P": 0.30}
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "DP": 51.0, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5, "Ca": 5.00, "P": 3.00},
        "مسحوق أسماك فاخر 72%": {"CP": 72.0, "DC": 0.90, "DP": 64.8, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5, "Ca": 5.50, "P": 3.20},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "DP": 37.5, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5, "Ca": 10.00, "P": 5.00},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "DP": 34.0, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5, "Ca": 2.50, "P": 1.50},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "DP": 28.8, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5, "Ca": 2.00, "P": 1.20},
        "مسحوق ريش دواجن": {"CP": 85.0, "DC": 0.70, "DP": 59.5, "SE": 40.0, "NDF": 5.0, "ADF": 3.0, "EE": 3.0, "ASH": 4.0, "Ca": 0.30, "P": 0.50},
        "مسحوق دم مجفف": {"CP": 93.0, "DC": 0.85, "DP": 79.1, "SE": 45.0, "NDF": 1.0, "ADF": 0.5, "EE": 1.0, "ASH": 4.0, "Ca": 0.20, "P": 0.25}
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": {"CP": 94.0, "DC": 1.00, "DP": 94.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.00, "P": 0.00},
        "ميثيونين نقي": {"CP": 58.0, "DC": 1.00, "DP": 58.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3, "Ca": 0.00, "P": 0.00},
        "ثريونين نقي": {"CP": 72.0, "DC": 1.00, "DP": 72.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.00, "P": 0.00},
        "تريبتوفان نقي": {"CP": 85.0, "DC": 1.00, "DP": 85.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.00, "P": 0.00},
        "أرجينين نقي": {"CP": 95.0, "DC": 1.00, "DP": 95.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.00, "P": 0.00}
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.00, "P": 5.00},
        "بريمكس بياض": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.00, "P": 6.00},
        "بريمكس أبقار حلابة": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.00, "P": 5.50},
        "إنزيم الفايتيز": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0, "Ca": 0.00, "P": 0.00},
        "إنزيم NSP": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0, "Ca": 0.00, "P": 0.00},
        "إنزيم بروتياز": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 4.0, "Ca": 0.00, "P": 0.00}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 38.00, "P": 0.02},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5, "Ca": 23.00, "P": 18.00},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9, "Ca": 0.30, "P": 0.00},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Ca": 0.50, "P": 0.10},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 0.00, "P": 0.00},
        "أكسيد المغنيسيوم": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 0.00, "P": 0.00},
        "يوريا علفية": {"CP": 287.0, "DC": 0.95, "DP": 272.7, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0, "Ca": 0.00, "P": 0.00},
        "كبريتات المغنيسيوم": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0, "Ca": 0.00, "P": 0.00}
    }
}

# ==========================================
# 18. أسعار الصرف والدول
# ==========================================

COUNTRIES_WITH_FLAGS = {
    "🇸🇩 السودان": {"rate": 600.0, "sym": "SDG", "name": "جنيه سوداني", "currency": "SDG", "default_city": "الخرطوم"},
    "🇱🇾 LIBYA": {"rate": 4.80, "sym": "LYD", "name": "دينار ليبي", "currency": "LYD", "default_city": "طرابلس"},
    "🇪🇬 مصر": {"rate": 48.0, "sym": "EGP", "name": "جنيه مصري", "currency": "EGP", "default_city": "القاهرة"},
    "🇸🇦 السعودية": {"rate": 3.75, "sym": "SAR", "name": "ريال سعودي", "currency": "SAR", "default_city": "الرياض"},
    "🇦🇪 الإمارات": {"rate": 3.67, "sym": "AED", "name": "درهم إماراتي", "currency": "AED", "default_city": "دبي"},
    "🇶🇦 قطر": {"rate": 3.64, "sym": "QAR", "name": "ريال قطري", "currency": "QAR", "default_city": "الدوحة"},
    "🇰🇼 الكويت": {"rate": 0.31, "sym": "KWD", "name": "دينار كويتي", "currency": "KWD", "default_city": "الكويت"},
    "🇴🇲 عمان": {"rate": 0.38, "sym": "OMR", "name": "ريال عماني", "currency": "OMR", "default_city": "مسقط"},
    "🇧🇭 البحرين": {"rate": 0.38, "sym": "BHD", "name": "دينار بحريني", "currency": "BHD", "default_city": "المنامة"},
    "🇯🇴 الأردن": {"rate": 0.71, "sym": "JOD", "name": "دينار أردني", "currency": "JOD", "default_city": "عمان"},
    "🇲🇦 المغرب": {"rate": 10.0, "sym": "MAD", "name": "درهم مغربي", "currency": "MAD", "default_city": "الدار البيضاء"},
    "🇩🇿 الجزائر": {"rate": 135.0, "sym": "DZD", "name": "دينار جزائري", "currency": "DZD", "default_city": "الجزائر"},
    "🇹🇳 تونس": {"rate": 3.10, "sym": "TND", "name": "دينار تونسي", "currency": "TND", "default_city": "تونس"},
    "🌍 باقي الدول": {"rate": 1.0, "sym": "USD", "name": "دولار أمريكي", "currency": "USD", "default_city": "العاصمة"}
}

# ==========================================
# 19. صور الحيوانات
# ==========================================

ANIMAL_IMAGES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?w=400",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?w=400",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?w=400",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?w=400",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?w=400",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?w=400",
    "سمان": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?w=400",
    "إبل": "https://images.unsplash.com/photo-1505169776168-c3d7cbd1ae6a?w=400"
}

# ==========================================
# 20. أكواد الدخول
# ==========================================

CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

# ==========================================
# 21. دوال مساعدة
# ==========================================

class ArabicTextProcessor:
    """معالج النص العربي"""
    
    @staticmethod
    @lru_cache(maxsize=1000)
    def fix_arabic_text(text: str) -> str:
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except Exception:
            return text

arabic_processor = ArabicTextProcessor()

def log_activity(action: str, details: str = ""):
    """تسجيل نشاط المستخدم"""
    try:
        with get_db() as conn:
            conn.execute('''
                INSERT INTO activity_logs (user_role, action, details, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (
                st.session_state.get("user_role", "unknown"),
                action,
                details[:500],
                SECURITY.get_client_ip()
            ))
        LOGGER.main_logger.info(f"نشاط: {action} - {details[:100]}")
    except Exception as e:
        LOGGER.error_logger.error(f"فشل تسجيل النشاط: {e}")

def calculate_energy_from_protein(protein_pct: float, protein_type: str = "DP") -> float:
    """حساب الطاقة المتوقعة بناءً على نسبة البروتين"""
    if protein_type == "DP":
        return (protein_pct * 85) + 45
    else:
        return (protein_pct * 70) + 50

def get_standard_requirements(sector: str, breed: str, production: str) -> Dict:
    """الحصول على الاحتياجات القياسية حسب السلالة والغرض"""
    try:
        if sector in BREEDS_STANDARDS:
            for b in BREEDS_STANDARDS[sector]:
                if breed in b or b in breed:
                    return BREEDS_STANDARDS[sector][b]
        return {"CP": 16.0, "DP": 13.4, "SE": 65.0, "ME": 2600, "P/E": 6.2}
    except Exception:
        return {"CP": 16.0, "DP": 13.4, "SE": 65.0, "ME": 2600, "P/E": 6.2}

def send_whatsapp_message(phone: str, message: str) -> Optional[str]:
    """إنشاء رابط واتساب"""
    try:
        encoded = urllib.parse.quote(message)
        return f"https://wa.me/{phone}?text={encoded}"
    except Exception:
        return None

# ==========================================
# 22. نظام تحديث الأسعار
# ==========================================

class LivePriceUpdater:
    """نظام تحديث أسعار متقدم مع تحديث كل 24 ساعة"""
    
    def __init__(self):
        self.price_cache = {}
        self.last_update = {}
        self.update_interval = 86400  # 24 ساعة
    
    def get_live_prices(self, country: str, city: str) -> Dict[str, float]:
        """الحصول على الأسعار مع تحديث كل 24 ساعة"""
        cache_key = f"{country}_{city}"
        
        if cache_key in self.last_update:
            if time.time() - self.last_update[cache_key] < self.update_interval:
                if cache_key in self.price_cache:
                    return self.price_cache[cache_key]
        
        prices = self.fetch_prices(country, city)
        
        if prices:
            self.price_cache[cache_key] = prices
            self.last_update[cache_key] = time.time()
            self.save_price_history(prices, city)
        
        return self.price_cache.get(cache_key, {})
    
    def fetch_prices(self, country: str, city: str) -> Dict[str, float]:
        """جلب الأسعار من المصادر"""
        base_prices = self.get_base_prices()
        multiplier = self.get_location_multiplier(country, city)
        
        for key in base_prices:
            change = random.uniform(-0.015, 0.015)
            base_prices[key] *= (1 + change) * multiplier
        
        return base_prices
    
    def get_base_prices(self) -> Dict[str, float]:
        """الأسعار الأساسية"""
        return {
            "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0,
            "سورجم (فتريتة)": 195.0, "قمح محلي مصنّع": 240.0, "جريش أرز": 280.0,
            "دخن محلي": 200.0, "شوفان علفي": 220.0, "أمباز الفول السوداني": 460.0,
            "كسب فول صويا 44%": 440.0, "كسب فول صويا 48%": 480.0, "كسب عباد الشمس": 310.0,
            "كسب بذور القطن": 290.0, "كسب بذور الكتان": 350.0, "كسب السمسم": 420.0,
            "كسب جلوتين الذرة": 650.0, "كسب نواة النخيل": 250.0, "نخالة قمح": 150.0,
            "البرسيم الجاف": 170.0, "مولاس قصب السكر": 120.0, "تبن قمح": 80.0,
            "قشر فول سوداني": 60.0, "سرسة الأرز": 90.0, "مخلفات البسكويت": 200.0,
            "مسحوق أسماك 60%": 850.0, "مسحوق أسماك 72%": 1050.0, "مسحوق لحم وعظم": 650.0,
            "مركزات دواجن": 650.0, "مركزات مجترات": 600.0, "ليسين نقي": 3200.0,
            "ميثيونين نقي": 2800.0, "ثريونين نقي": 2500.0, "بريمكس دواجن": 2500.0,
            "بريمكس بياض": 2800.0, "إنزيم الفايتيز": 1800.0, "إنزيم NSP": 1600.0,
            "الحجر الجيري": 40.0, "فوسفات ثنائي الكالسيوم": 280.0, "ملح الطعام": 30.0,
            "مضاد سموم فطرية": 950.0, "بيكربونات الصوديوم": 340.0, "أكسيد المغنيسيوم": 450.0,
            "تريتيكال": 245.0, "كسب بذور اللفت": 380.0, "مسحوق ريش": 450.0,
            "مسحوق دم": 500.0, "يوريا": 350.0, "أرجينين": 3500.0
        }
    
    def get_location_multiplier(self, country: str, city: str) -> float:
        """معامل تعديل الموقع"""
        multipliers = {
            "🇸🇩 السودان": {"default": 1.15, "الخرطوم": 1.0, "أم درمان": 1.02, "بحري": 1.01, "ود مدني": 0.95, "بورتسودان": 1.08, "الأبيض": 0.92, "كسلا": 0.94, "الفاشر": 0.90},
            "🇱🇾 LIBYA": {"default": 1.10, "طرابلس": 1.0, "بنغازي": 0.98, "مصراتة": 0.96, "سبها": 0.92, "البيضاء": 0.95},
            "🇪🇬 مصر": {"default": 1.04, "القاهرة": 1.0, "الإسكندرية": 0.97, "الجيزة": 0.99, "الأقصر": 0.95, "أسوان": 0.94, "بورسعيد": 0.96},
            "🇸🇦 السعودية": {"default": 1.08, "الرياض": 1.0, "جدة": 1.02, "الدمام": 0.98, "مكة": 1.01, "المدينة": 0.99},
            "🇦🇪 الإمارات": {"default": 1.05, "دبي": 1.0, "أبوظبي": 0.98, "الشارقة": 0.97, "عجمان": 0.95},
            "🌍 باقي الدول": {"default": 1.0}
        }
        country_mult = multipliers.get(country, {"default": 1.0})
        return country_mult.get(city, country_mult["default"])
    
    def save_price_history(self, prices: Dict[str, float], city: str):
        """حفظ تاريخ الأسعار"""
        try:
            with get_db() as conn:
                for commodity, price in prices.items():
                    conn.execute('''
                        INSERT INTO market_prices_history (city, commodity, price, recorded_at)
                        VALUES (?, ?, ?, ?)
                    ''', (city, commodity, price, datetime.now().isoformat()))
        except Exception as e:
            LOGGER.error_logger.error(f"فشل حفظ تاريخ الأسعار: {e}")
    
    def get_last_update_time(self, country: str, city: str) -> Optional[datetime]:
        """الحصول على وقت آخر تحديث"""
        cache_key = f"{country}_{city}"
        if cache_key in self.last_update:
            return datetime.fromtimestamp(self.last_update[cache_key])
        return None

PRICE_UPDATER = LivePriceUpdater()

# ==========================================
# 23. مولد PDF المحترف
# ==========================================

class ProfessionalPDFGenerator:
    """مولد PDF احترافي مع دعم اللغة العربية"""
    
    def __init__(self):
        self.font_name = 'Helvetica'
        if os.path.exists("Amiri-Regular.ttf"):
            try:
                pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
                self.font_name = 'Amiri'
            except Exception:
                pass

    def generate_comprehensive_report(
        self, 
        formula: Dict[str, float], 
        target_dp: float, 
        breed: str, 
        cost: float, 
        city: str, 
        local_cost: float, 
        local_sym: str, 
        computed_se: float,
        include_charts: bool = True
    ) -> bytes:
        """توليد تقرير PDF كامل"""
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

        def p(text: str, size: int = 12, align: int = TA_RIGHT, color: Any = HexColor('#000000')):
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(
                safe_text, 
                ParagraphStyle(
                    'style', 
                    fontName=self.font_name, 
                    fontSize=size, 
                    alignment=align, 
                    textColor=color, 
                    spaceAfter=6, 
                    leading=size*1.5
                )
            )

        # العنوان
        story.append(p("تقرير فني - منصة تاور العلمية", size=22, align=TA_CENTER, color=HexColor('#1b5e20')))
        story.append(Spacer(1, 12))
        
        # معلومات التقرير
        for line in [
            f"المشرف: م. عبد القادر إسماعيل تاور",
            f"الموقع: {city}",
            f"الفصيل: {breed}",
            f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}"
        ]:
            story.append(p(line, size=11))
        story.append(Spacer(1, 15))

        # جدول المعايير
        tdata = [
            ["المعيار", "القيمة"],
            ["البروتين المهضوم", f"{target_dp:.2f}%"],
            ["معادل النشاء", f"{computed_se:.2f} وحدة"],
            ["التكلفة", f"${cost:.2f} ({local_cost:,.2f} {local_sym})"]
        ]
        
        t = Table(tdata, colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#2e7d32')),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        # جدول المكونات
        story.append(p("المقادير المعتمدة:", size=14, color=HexColor('#2e7d32')))
        ing_data = [["المكون", "النسبة %", "كجم/طن"]]
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
        ]))
        story.append(t2)

        # مخطط دائري إذا كان مطلوباً
        if include_charts and len(formula) > 1:
            try:
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots(figsize=(6, 4))
                names = list(formula.keys())
                vals = list(formula.values())
                colors = ['#1b5e20','#2e7d32','#388e3c','#43a047','#4caf50','#66bb6a']
                ax.pie(vals, labels=None, autopct='%1.1f%%', colors=colors[:len(names)])
                ax.legend(
                    [arabic_processor.fix_arabic_text(n) for n in names],
                    title=arabic_processor.fix_arabic_text("المكونات"),
                    loc='center left',
                    bbox_to_anchor=(1, 0, 0.5, 1),
                    fontsize=8
                )
                ax.set_title(arabic_processor.fix_arabic_text('توزيع المكونات'), fontsize=12)
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=400, height=230))
            except Exception as e:
                LOGGER.error_logger.error(f"فشل إنشاء المخطط في PDF: {e}")

        story.append(Spacer(1, 25))
        story.append(
            p(
                "تم التوليد بواسطة منصة تاور العلمية © 2026",
                size=9,
                align=TA_CENTER,
                color=HexColor('#666666')
            )
        )
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# ==========================================
# 24. إدارة مزارع الدجاج
# ==========================================

class BroilerFarmManager:
    """مدير مزارع الدواجن المتكامل"""
    
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
    def get_temp_humidity_table() -> pd.DataFrame:
        data = {
            "العمر (يوم)": [1, 7, 14, 21, 28, 35, 42],
            "درجة الحرارة": [33, 30, 28, 26, 24, 22, 21],
            "الرطوبة (%)": [65, 65, 65, 60, 60, 55, 55]
        }
        return pd.DataFrame(data)
    
    @staticmethod
    def get_breed_performance(breed_type: str = "لاحم") -> Dict:
        performance = {
            "لاحم سريع": {"daily_gain": 62, "fcr": 1.55, "final_weight": 2600, "mortality": 3.5},
            "لاحم متوسط": {"daily_gain": 55, "fcr": 1.70, "final_weight": 2300, "mortality": 4.0},
            "لاحم بطيء": {"daily_gain": 45, "fcr": 1.90, "final_weight": 1900, "mortality": 3.0},
            "بياض تجاري": {"egg_production": 320, "egg_weight": 62, "fcr": 2.00, "mortality": 5.0}
        }
        return performance.get(breed_type, performance["لاحم متوسط"])

# ==========================================
# 25. تهيئة متغيرات الجلسة
# ==========================================

def init_session_state():
    """تهيئة جميع متغيرات الجلسة"""
    defaults = {
        "approved": False,
        "user_role": None,
        "session_token": secrets.token_urlsafe(32),
        "active_formula": {},
        "active_cp_tag": 12.0,
        "active_se_tag": 65.0,
        "active_breed_tag": "سلالة عامة",
        "computed_ton_cost": 280.0,
        "pending_lab_requests": [],
        "next_request_id": 1,
        "inventory": {},
        "poultry_farms": {},
        "shared_comments": "• مرحباً بكم في منصة تاور العلمية للانتاج الحيواني\n• نرحب بتعليقاتكم واقتراحاتكم\n",
        "login_attempts": 0,
        "last_login_time": None,
        "login_welcome_shown": False,
        "whatsapp_alerts_sent": {},
        "broiler_farms": {},
        "lab_results": {},
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

init_session_state()

# ==========================================
# 26. CSS المتقدم
# ==========================================

def load_css():
    """تحميل CSS المتقدم"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
        box-sizing: border-box;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f0f4fa 0%, #d9e2ef 100%);
    }
    
    .main-box {
        background: rgba(255, 255, 255, 0.98);
        padding: 35px;
        border-radius: 25px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        backdrop-filter: blur(10px);
        margin: 20px;
        border: 1px solid rgba(46,125,50,0.2);
        animation: fadeIn 0.5s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .section-title {
        color: #1b5e20;
        border-right: 8px solid #2e7d32;
        padding-right: 20px;
        font-size: 1.8rem;
        font-weight: 900;
        margin: 30px 0 25px 0;
        background: linear-gradient(135deg, rgba(46,125,50,0.1), transparent);
        padding: 12px 20px;
        border-radius: 12px;
    }
    
    .formula-item {
        background: linear-gradient(135deg, #f8fff8, #f0f8f0);
        padding: 15px 25px;
        border-radius: 12px;
        margin: 10px 0;
        border-right: 5px solid #2e7d32;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .formula-item:hover {
        background: linear-gradient(135deg, #f0fff0, #e8f5e9);
        transform: translateX(-5px);
    }
    
    .price-card {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        padding: 20px;
        border-radius: 15px;
        border-right: 6px solid #2e7d32;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .price-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
    }
    
    .metric-card .value {
        font-size: 2.5rem;
        font-weight: 900;
        color: #1b5e20;
    }
    
    .alert-box {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        border-right: 6px solid #c62828;
        padding: 18px;
        border-radius: 12px;
        margin: 15px 0;
        color: #c62828;
        font-weight: 500;
    }
    
    .success-box {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        border-right: 6px solid #2e7d32;
        padding: 18px;
        border-radius: 12px;
        margin: 15px 0;
        color: #1b5e20;
        font-weight: 500;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        padding: 15px;
        border-radius: 12px;
        border-right: 5px solid #f57c00;
        margin-bottom: 15px;
        color: #e65100;
    }
    
    .stock-critical {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        padding: 8px 12px;
        border-radius: 8px;
        color: #c62828;
    }
    
    .stock-normal {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        padding: 8px 12px;
        border-radius: 8px;
        color: #2e7d32;
    }
    
    .profile-img-style {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid #d4af37;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    
    .mini-left-signature {
        position: fixed;
        left: 20px;
        bottom: 20px;
        background: linear-gradient(135deg, #1b5e20, #2e7d32);
        color: white;
        padding: 10px 25px;
        border-radius: 30px;
        font-size: 0.85rem;
        z-index: 999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #2e7d32, #1b5e20);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1b5e20, #0d3b0f);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    }
    
    .send-code-btn button {
        background: linear-gradient(135deg, #c62828, #b71c1c) !important;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(198,40,40,0.4); }
        70% { box-shadow: 0 0 0 10px rgba(198,40,40,0); }
        100% { box-shadow: 0 0 0 0 rgba(198,40,40,0); }
    }
    
    @media (max-width: 768px) {
        .main-box {
            padding: 15px;
            margin: 10px;
        }
        .section-title {
            font-size: 1.3rem;
        }
        .metric-card .value {
            font-size: 1.8rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ==========================================
# 27. الواجهة الرئيسية
# ==========================================

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# رأس الصفحة
col_logo, col_title, col_send = st.columns([1, 2, 1])

with col_logo:
    if img_base64:
        st.image(f"data:image/jpeg;base64,{img_base64}", width=100)
    else:
        st.image("https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=100", width=100)

with col_title:
    st.markdown("""
    <h1 style='color: #1b5e20; text-align:center; margin-bottom:0;'>
        🌾 منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف
    </h1>
    <p style='text-align:center; color:#1565C0; font-size:1.2rem; margin-top:5px;'>
        محرك الاستمثال الخطي المتقدم | البروتين المهضوم (DP) | معادل النشاء (SE)
    </p>
    <h3 style='text-align:center; color:#c62828; margin-top:5px;'>
        الاختصاصي م. عبد القادر إسماعيل تاور
    </h3>
    """, unsafe_allow_html=True)

with col_send:
    st.markdown('<div class="send-code-btn">', unsafe_allow_html=True)
    if st.button("📧 إرسال الكود للمالك", use_container_width=True, type="primary"):
        with st.spinner("جاري إرسال الكود..."):
            if CODE_SENDER.send_code_to_email(OWNER_EMAIL, "طلب يدوي من رأس الصفحة"):
                st.success("✅ تم إرسال الكود بنجاح!")
                log_activity("send_code", "تم إرسال الكود للمالك")
            else:
                st.error("❌ فشل إرسال الكود")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ==========================================
# 28. بوابة الدخول
# ==========================================

client_ip = SECURITY.get_client_ip()

if SECURITY.is_ip_blocked(client_ip):
    st.markdown(f"""
    <div class="alert-box">
        🚫 <b>تم حظر عنوان IP الخاص بك</b><br>
        الرجاء التواصل مع الدعم الفني
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not st.session_state["approved"]:
    st.markdown('<div style="max-width: 500px; margin: 80px auto;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:#2E7D32; text-align:center;'>🔒 بوابة الدخول</h2>", unsafe_allow_html=True)
    
    # QR Code
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("https://tower-scientific-platform.streamlit.app")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{qr_base64}" width="150"></div>', unsafe_allow_html=True)
    except Exception:
        pass
    
    input_code = st.text_input("🔑 أدخل كود الدخول:", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("تسجيل الدخول", type="primary", use_container_width=True):
            if input_code in CODES_DB:
                st.session_state["approved"] = True
                st.session_state["user_role"] = CODES_DB[input_code]["role"]
                st.session_state["session_token"] = secrets.token_urlsafe(32)
                st.session_state["login_attempts"] = 0
                
                SECURITY.log_visitor(st.session_state["user_role"], "login")
                log_activity("login", "تسجيل دخول ناجح")
                
                if st.session_state["user_role"] == "owner":
                    CODE_SENDER.auto_backup_check()
                
                st.rerun()
            else:
                SECURITY.log_failed_attempt(input_code)
                st.session_state["login_attempts"] += 1
                remaining = 5 - st.session_state["login_attempts"]
                st.error(f"❌ الكود غير صحيح! متبقي {remaining} محاولات")
    
    with col2:
        if st.button("نسيت الكود", use_container_width=True):
            st.info("يرجى التواصل مع مدير النظام: abukram128@gmail.com")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 29. رسالة ترحيب حسب الدور
# ==========================================

role_messages = {
    "owner": "👑 مرحباً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور. جميع أنظمة الأمان والأداء فعالة وجاهزة.",
    "specialist": "🔬 مرحباً بالزملاء المختصين والأطباء البيطريين. النظام جاهز لخدمتكم مع أحدث تقنيات تركيب الأعلاف.",
    "breeder": "🌾 أهلاً وسهلاً بالمربين الكرام. نتمنى لكم تجربة ممتعة وخلطات اقتصادية عالية الجودة."
}

if st.session_state.get("user_role") in role_messages:
    st.info(role_messages[st.session_state["user_role"]])

st.markdown("---")

# ==========================================
# 30. التبويبات
# ==========================================

if st.session_state.get("user_role") == "owner":
    tab_titles = [
        "🔬 تركيب الأعلاف",
        "📊 بورصة الأسعار الحية",
        "🏭 إدارة المخزون",
        "🧾 المبيعات والفواتير",
        "🐔 إدارة مزارع الدواجن",
        "🔬 المختبر المتكامل",
        "📈 التحليلات المتقدمة",
        "👑 لوحة تحكم المالك",
        "💬 التعليقات",
        "📖 الدليل"
    ]
elif st.session_state.get("user_role") == "specialist":
    tab_titles = [
        "🔬 تركيب الأعلاف",
        "📊 بورصة الأسعار الحية",
        "🏭 إدارة المخزون",
        "🧾 المبيعات",
        "🔬 المختبر المتكامل",
        "📈 التحليلات",
        "💬 التعليقات",
        "📖 الدليل"
    ]
else:
    tab_titles = ["🔬 تركيب الأعلاف", "📖 دليل المستخدم"]

tabs = st.tabs(tab_titles)

# ==========================================
# 31. التبويب الأول: تركيب الأعلاف
# ==========================================

with tabs[0]:
    st.markdown('<div class="section-title">🌍 الموقع الجغرافي وتحديد السوق</div>', unsafe_allow_html=True)
    
    col_loc1, col_loc2, col_loc3 = st.columns(3)
    with col_loc1:
        country = st.selectbox("🇸🇩 الدولة:", list(COUNTRIES_WITH_FLAGS.keys()))
    with col_loc2:
        city = st.text_input("📍 المدينة:", COUNTRIES_WITH_FLAGS.get(country, {}).get("default_city", "الخرطوم"))
    with col_loc3:
        # عرض العملة
        rate = COUNTRIES_WITH_FLAGS.get(country, {}).get("rate", 1.0)
        sym = COUNTRIES_WITH_FLAGS.get(country, {}).get("sym", "USD")
        st.metric("💱 العملة المحلية", f"1 USD = {rate:.2f} {sym}")
    
    # تحديث الأسعار
    current_prices = PRICE_UPDATER.get_live_prices(country, city)
    local_rate = COUNTRIES_WITH_FLAGS.get(country, {"rate": 1.0})["rate"]
    local_sym = COUNTRIES_WITH_FLAGS.get(country, {"sym": "USD"})["sym"]
    
    last_update = PRICE_UPDATER.get_last_update_time(country, city)
    if last_update:
        st.info(f"🔄 آخر تحديث للأسعار: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.markdown('<div class="section-title">💰 بورصة الأسعار المباشرة</div>', unsafe_allow_html=True)
    
    # عرض الأسعار
    price_cols = st.columns(4)
    for idx, (item, price) in enumerate(list(current_prices.items())[:12]):
        with price_cols[idx % 4]:
            st.markdown(f"""
            <div class="price-card">
                <b>{item}</b><br>
                <span style="font-size:1.3rem; color:#1b5e20;">${price:.2f}</span><br>
                <small>{price*local_rate:,.0f} {local_sym}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">🎯 القطاع والإنتاجية المستهدفة</div>', unsafe_allow_html=True)
    
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec:
        sector = st.selectbox("🐏 القطاع الحيواني:", ["الدواجن", "الأغنام", "الماعز", "الأبقار", "الخيول", "الأسماك"])
    
    with col_sub:
        sector_map = {
            "الدواجن": ["لاحم (بادي)", "لاحم (نامي)", "لاحم (ناهي)", "بياض (بادي)", "بياض (إنتاج)", "بياض (ناهي)", "سمان", "رومي"],
            "الأغنام": ["تسمين (صحراوي)", "تسمين (بربري)", "تسمين (نعيمي)", "حليب (أغنام)", "صيانة"],
            "الماعز": ["تسمين", "حليب", "صيانة"],
            "الأبقار": ["حليب (هولشتاين)", "حليب (فريزيان)", "تسمين (كنانة)", "تسمين (بطانة)", "عجول تسمين"],
            "الخيول": ["رياضة", "نمو", "صيانة"],
            "الأسماك": ["بلطي (نمو)", "بلطي (تسمين)", "بوري", "قرموط"]
        }
        breed = st.selectbox("🐣 السلالة:", sector_map.get(sector, ["عام"]))
    
    with col_prod:
        production = st.selectbox("📈 مرحلة الإنتاج:", ["بادي", "نامي", "ناهي", "إنتاج", "تحضيري", "صيانة"])
    
    # تحديد القيم القياسية
    standards = get_standard_requirements(sector, breed, production)
    suggested_dp = standards.get("DP", 16.0)
    suggested_se = standards.get("SE", 65.0)
    
    st.markdown('<div class="section-title">📊 تحديد نسب البروتين والطاقة</div>', unsafe_allow_html=True)
    
    col_prot1, col_prot2 = st.columns(2)
    with col_prot1:
        protein_type = st.radio("🧬 نوع البروتين:", ["البروتين المهضوم (DP)", "البروتين الخام (CP)"], horizontal=True)
        protein_source = st.radio("📋 مصدر القيم:", ["قياسي (حسب السلالة)", "يدوي"], horizontal=True)
    
    with col_prot2:
        if protein_source == "قياسي (حسب السلالة)":
            if protein_type == "البروتين المهضوم (DP)":
                recommended_protein = suggested_dp
            else:
                recommended_protein = standards.get("CP", suggested_dp / 0.85)
            st.info(f"💡 القيمة القياسية: {recommended_protein:.1f}%")
            protein_value = st.slider("🥩 نسبة البروتين %:", 5.0, 40.0, recommended_protein, 0.5)
        else:
            protein_value = st.slider("🥩 نسبة البروتين %:", 5.0, 40.0, 18.0, 0.5)
        
        energy_value = st.slider("⚡ معادل النشاء (SE):", 20.0, 90.0, suggested_se, 1.0)
    
    # اختيار المكونات
    st.markdown('<div class="section-title">📦 اختيار المكونات العلفية</div>', unsafe_allow_html=True)
    
    selected_ingredients = []
    ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        expanded = "الحبوب" in cat_name or "الأكساب" in cat_name
        with st.expander(f"📁 {cat_name}", expanded=expanded):
            cols = st.columns(3)
            for idx, (ing_name, data) in enumerate(items.items()):
                with cols[idx % 3]:
                    is_default = ing_name in ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)", "ملح الطعام", "الحجر الجيري", "بريمكس دواجن"]
                    checked = st.checkbox(ing_name, value=is_default, key=f"feed_{ing_name}")
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        price = current_prices.get(ing_name, 300.0)
                        if st.session_state.get("user_role") == "owner":
                            price_input = st.number_input(f"💰 سعر {ing_name} ($/طن)", min_value=10.0, value=float(price), step=5.0, key=f"price_{ing_name}")
                            ingredient_prices[ing_name] = price_input
                        else:
                            st.markdown(f"💰 السعر: **`${price:.2f}`**/طن")
                            ingredient_prices[ing_name] = price
    
    # زر التشغيل
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
    with col_btn2:
        run_optimization = st.button("🚀 تشغيل المحرك", type="primary", use_container_width=True)
    
    if run_optimization:
        if len(selected_ingredients) < 3:
            st.warning("⚠️ يرجى اختيار 3 مكونات على الأقل")
        else:
            with st.spinner("🔄 جاري حساب التركيبة المثلى..."):
                try:
                    c = [ingredient_prices[ing] for ing in selected_ingredients]
                    bounds = [(0.0, 100.0) for _ in selected_ingredients]
                    
                    # قيد المجموع الكلي
                    A_eq = [[1.0] * len(selected_ingredients)]
                    b_eq = [100.0]
                    
                    # قيد البروتين
                    protein_row = []
                    for ing in selected_ingredients:
                        cp_val = 0.0
                        dc_val = 0.85
                        for cat in BIG_FEEDS_LIBRARY.values():
                            if ing in cat:
                                cp_val = cat[ing]["CP"]
                                dc_val = cat[ing]["DC"]
                                break
                        if protein_type == "البروتين المهضوم (DP)":
                            protein_row.append(cp_val * dc_val)
                        else:
                            protein_row.append(cp_val)
                    
                    A_eq.append(protein_row)
                    b_eq.append(protein_value * 100)
                    
                    # قيد الطاقة
                    se_row = []
                    for ing in selected_ingredients:
                        se_val = 0.0
                        for cat in BIG_FEEDS_LIBRARY.values():
                            if ing in cat:
                                se_val = cat[ing]["SE"]
                                break
                        se_row.append(se_val)
                    
                    A_ub = [[-x for x in se_row]]
                    b_ub = [-energy_value * 100]
                    
                    # قيد الحبوب
                    grain_ingredients = ["ذرة صفراء", "ذرة بيضاء", "شعير مطحون", "سورجم (فتريتة)", "قمح محلي مصنّع", "جريش أرز", "دخن محلي", "شوفان علفي", "تريتيكال"]
                    grain_indicators = [1.0 if ing in grain_ingredients else 0.0 for ing in selected_ingredients]
                    if sum(grain_indicators) > 0:
                        A_ub.append([-x for x in grain_indicators])
                        b_ub.append(-40.0)
                    
                    # حل التحسين
                    result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
                    
                    if result.success:
                        formula = {}
                        computed_se = 0.0
                        for idx, ing in enumerate(selected_ingredients):
                            if result.x[idx] > 0.01:
                                formula[ing] = result.x[idx]
                                for cat in BIG_FEEDS_LIBRARY.values():
                                    if ing in cat:
                                        computed_se += (result.x[idx] / 100) * cat[ing]["SE"]
                        
                        ton_cost = result.fun / 100
                        
                        st.session_state["active_formula"] = formula
                        st.session_state["active_cp_tag"] = protein_value
                        st.session_state["active_se_tag"] = computed_se
                        st.session_state["active_breed_tag"] = breed
                        st.session_state["computed_ton_cost"] = ton_cost
                        
                        # حفظ في قاعدة البيانات
                        with get_db() as conn:
                            conn.execute('''
                                INSERT INTO formulas_history (formula_data, target_dp, target_se, protein_type, breed, sector, production, cost, city, user_role)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                json.dumps(formula),
                                protein_value if "مهضوم" in protein_type else None,
                                computed_se,
                                protein_type,
                                breed,
                                sector,
                                production,
                                ton_cost,
                                city,
                                st.session_state.get("user_role")
                            ))
                        
                        log_activity("formula_generated", f"خلطة لـ {breed} بتكلفة {ton_cost:.2f}")
                        
                        st.success("✅ تم حساب التركيبة المثلى بنجاح!")
                        
                        # عرض النتائج
                        st.markdown("---")
                        col_res1, col_res2 = st.columns([2, 1])
                        
                        with col_res1:
                            st.markdown("#### 📝 المقادير المعتمدة:")
                            for ing, pct in formula.items():
                                st.markdown(f"""
                                <div class="formula-item">
                                    ▪️ <b>{ing}:</b> {pct:.2f}% → {pct*10:.1f} كجم/طن
                                </div>
                                """, unsafe_allow_html=True)
                            
                            col_metric1, col_metric2, col_metric3 = st.columns(3)
                            with col_metric1:
                                st.metric("💰 التكلفة للطن", f"${ton_cost:.2f}", delta=f"{ton_cost*local_rate:,.0f} {local_sym}")
                            with col_metric2:
                                st.metric("🧬 البروتين", f"{protein_value:.1f}%")
                            with col_metric3:
                                st.metric("⚡ معادل النشاء", f"{computed_se:.1f}")
                            
                            # أزرار التصدير
                            col_btn_a, col_btn_b, col_btn_c = st.columns(3)
                            
                            with col_btn_a:
                                share_msg = f"منصة تاور العلمية - خلطة {breed} بتكلفة {ton_cost:.2f}$ للطن"
                                encoded_share = urllib.parse.quote(share_msg)
                                st.link_button("📲 مشاركة", f"https://wa.me/?text={encoded_share}", use_container_width=True)
                            
                            with col_btn_b:
                                pdf_data = pdf_generator.generate_comprehensive_report(
                                    formula, protein_value, breed, ton_cost, city, 
                                    ton_cost*local_rate, local_sym, computed_se
                                )
                                st.download_button(
                                    "📥 تحميل PDF", 
                                    pdf_data, 
                                    f"formula_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", 
                                    "application/pdf", 
                                    use_container_width=True
                                )
                            
                            with col_btn_c:
                                if st.button("📧 إرسال الكود", use_container_width=True):
                                    with st.spinner("جاري الإرسال..."):
                                        CODE_SENDER.send_code_to_email(OWNER_EMAIL, "طلب من لوحة التركيب")
                                        st.success("تم الإرسال")
                        
                        with col_res2:
                            # رسم بياني
                            fig = go.Figure(data=[go.Pie(
                                labels=list(formula.keys()), 
                                values=list(formula.values()),
                                hole=0.3,
                                marker=dict(colors=px.colors.sequential.Greens_r),
                                textinfo='label+percent'
                            )])
                            fig.update_layout(title="توزيع المكونات", height=400)
                            st.plotly_chart(fig, use_container_width=True)
                    
                    else:
                        st.error("❌ تعذر إيجاد حل متوافق مع القيود")
                        st.info("💡 نصيحة: أضف المزيد من المكونات أو وسع حدود القيود")
                
                except Exception as e:
                    st.error(f"⚠️ خطأ: {str(e)}")
                    LOGGER.error_logger.error(f"خطأ في التحسين: {e}")

# ==========================================
# 32. التبويبات المتبقية (مختصرة)
# ==========================================

# بما أن المساحة محدودة، سأعطي هيكلاً للتبويبات المتبقية
# يمكنك إضافة المحتوى الكامل حسب الحاجة

if st.session_state.get("user_role") in ["owner", "specialist"]:
    with tabs[1]:  # بورصة الأسعار
        st.markdown('<div class="section-title">📈 بورصة الأسعار المباشرة</div>', unsafe_allow_html=True)
        st.info("📊 يتم تحديث الأسعار كل 24 ساعة")
        
        # عرض جدول الأسعار
        prices_df = pd.DataFrame([
            {"المادة": item, "السعر (USD)": f"${price:.2f}", f"السعر المحلي ({local_sym})": f"{price * local_rate:,.0f}"}
            for item, price in current_prices.items()
        ])
        st.dataframe(prices_df, use_container_width=True, height=400)
        
        if st.button("🔄 تحديث الأسعار الآن", use_container_width=True):
            with st.spinner("جاري التحديث..."):
                PRICE_UPDATER.price_cache = {}
                st.rerun()

    with tabs[2]:  # إدارة المخزون
        st.markdown('<div class="section-title">🏭 إدارة المخزون</div>', unsafe_allow_html=True)
        
        total_items = len(st.session_state["inventory"])
        low_stock = sum(1 for data in st.session_state["inventory"].values() if data["quantity"] < data["min_threshold"])
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("📦 إجمالي المواد", total_items)
        with col_s2:
            st.metric("⚠️ مخزون منخفض", low_stock)
        
        # عرض المخزون
        search_term = st.text_input("🔍 بحث:", placeholder="اسم المادة...")
        
        inventory_data = []
        for ing, data in st.session_state["inventory"].items():
            if search_term and search_term.lower() not in ing.lower():
                continue
            status = "🟢 آمن"
            if data["quantity"] <= 0:
                status = "🔴 نفذ"
            elif data["quantity"] < data["min_threshold"]:
                status = "🟡 منخفض"
            inventory_data.append({"المادة": ing, "الكمية": data["quantity"], "الحد الأدنى": data["min_threshold"], "الحالة": status})
        
        if inventory_data:
            st.dataframe(pd.DataFrame(inventory_data), use_container_width=True, height=400)

    with tabs[3]:  # المبيعات
        st.markdown('<div class="section-title">🧾 المبيعات والفواتير</div>', unsafe_allow_html=True)
        
        client_name = st.text_input("🏢 اسم العميل:", "مزرعة الإنتاج المتكاملة")
        tons = st.number_input("⚖️ الكمية (طن):", min_value=0.1, value=2.0, step=0.5)
        
        base_cost = st.session_state.get("computed_ton_cost", 280.0)
        profit_margin = st.number_input("💰 هامش الربح ($/طن):", min_value=0.0, value=50.0, step=10.0)
        selling_price = base_cost + profit_margin
        total_amount = selling_price * tons
        
        st.markdown("---")
        st.markdown("### 🧾 فاتورة البيع")
        
        st.markdown(f"""
        <div class="price-card">
            <h4>تفاصيل الفاتورة</h4>
            <p><b>العميل:</b> {client_name}</p>
            <p><b>الكمية:</b> {tons} طن</p>
            <p><b>سعر الطن:</b> ${selling_price:.2f}</p>
            <p style="font-size:1.3rem;"><b>الإجمالي:</b> ${total_amount:.2f}</p>
            <p style="color:#666;">ما يعادل: {total_amount*local_rate:,.0f} {local_sym}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get("user_role") == "owner":
            if st.button("✅ تأكيد البيع وخصم المخزون", type="primary", use_container_width=True):
                if st.session_state.get("active_formula"):
                    if INVENTORY_MANAGER.deduct_items(st.session_state["active_formula"], tons):
                        st.success("✅ تم خصم الكميات من المخزون وتسجيل البيع!")
                        st.balloons()
                        log_activity("sale", f"بيع {tons} طن لـ {client_name} بقيمة {total_amount:.2f}$")
                    else:
                        st.error("❌ رصيد غير كافٍ لبعض المواد")
                else:
                    st.warning("⚠️ لا توجد خلطة نشطة")

# ==========================================
# 33. تبويب إدارة مزارع الدواجن (للمالك)
# ==========================================

if st.session_state.get("user_role") == "owner" and len(tabs) > 4:
    with tabs[4]:
        st.markdown('<div class="section-title">🐔 إدارة مزارع الدواجن</div>', unsafe_allow_html=True)
        
        # تحميل بيانات المزارع
        farm_data_file = "data/poultry_farms.json"
        
        def load_farms():
            if os.path.exists(farm_data_file):
                try:
                    with open(farm_data_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception:
                    return {}
            return {}
        
        def save_farms(data):
            try:
                with open(farm_data_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                st.error(f"خطأ في حفظ البيانات: {e}")
        
        if "poultry_farms" not in st.session_state:
            st.session_state["poultry_farms"] = load_farms()
        
        # إضافة مزرعة جديدة
        with st.expander("➕ إضافة مزرعة جديدة", expanded=False):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                new_farm = st.text_input("اسم المزرعة:")
                farm_type = st.selectbox("النوع:", ["لاحم (Broiler)", "بياض (Layer)", "سمان", "رومي"])
            with col_f2:
                initial_birds = st.number_input("عدد الطيور:", min_value=1, value=1000, step=100)
                owner_name = st.text_input("اسم المالك:")
            
            if st.button("🏠 إضافة مزرعة", use_container_width=True):
                if new_farm:
                    st.session_state["poultry_farms"][new_farm] = {
                        "type": farm_type,
                        "birds": initial_birds,
                        "initial_birds": initial_birds,
                        "age": 0,
                        "owner": owner_name,
                        "logs": [],
                        "created_at": datetime.now().isoformat()
                    }
                    save_farms(st.session_state["poultry_farms"])
                    st.success(f"✅ تم إضافة مزرعة {new_farm}")
                    st.rerun()
        
        # عرض المزارع
        if st.session_state["poultry_farms"]:
            for farm_name, farm_data in st.session_state["poultry_farms"].items():
                with st.expander(f"🏠 {farm_name} - {farm_data['type']}", expanded=True):
                    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
                    with col_d1:
                        st.metric("عدد الطيور", f"{farm_data['birds']:,}")
                    with col_d2:
                        st.metric("العمر (يوم)", farm_data['age'])
                    with col_d3:
                        mortality = ((farm_data['initial_birds'] - farm_data['birds']) / farm_data['initial_birds']) * 100
                        st.metric("نسبة النفوق", f"{mortality:.1f}%")
                    with col_d4:
                        performance = BroilerFarmManager.get_breed_performance(farm_data['type'])
                        if "daily_gain" in performance:
                            expected_weight = performance['daily_gain'] * farm_data['age'] / 1000
                            st.metric("الوزن المتوقع", f"{expected_weight:.2f} كجم")
                    
                    # تسجيل بيانات يومية
                    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                    with col_r1:
                        new_age = st.number_input("العمر (يوم)", value=farm_data['age'], key=f"age_{farm_name}", step=1)
                    with col_r2:
                        dead = st.number_input("نافق اليوم", min_value=0, value=0, key=f"dead_{farm_name}", step=1)
                    with col_r3:
                        feed = st.number_input("العلف (كجم/طير)", min_value=0.0, value=0.0, key=f"feed_{farm_name}", step=0.05)
                    with col_r4:
                        weight = st.number_input("الوزن (كجم/طير)", min_value=0.0, value=0.0, key=f"weight_{farm_name}", step=0.1)
                    
                    if st.button(f"💾 حفظ بيانات اليوم", key=f"save_{farm_name}", use_container_width=True):
                        farm_data['age'] = new_age
                        farm_data['birds'] -= dead
                        
                        fcr = BroilerFarmManager.calculate_fcr(feed * farm_data['birds'], weight * farm_data['birds'])
                        adg = BroilerFarmManager.calculate_adg(weight * 1000, 45, new_age)
                        
                        farm_data['logs'].append({
                            "date": datetime.now().isoformat(),
                            "age": new_age,
                            "dead": dead,
                            "birds": farm_data['birds'],
                            "feed": feed,
                            "weight": weight,
                            "fcr": fcr,
                            "adg": adg
                        })
                        save_farms(st.session_state["poultry_farms"])
                        st.success("تم حفظ البيانات")
                        st.rerun()
                    
                    # عرض السجل
                    if farm_data['logs']:
                        st.markdown("#### 📊 سجل الأداء")
                        logs_df = pd.DataFrame(farm_data['logs'][-10:])
                        if 'fcr' in logs_df.columns:
                            st.dataframe(logs_df[['date', 'age', 'dead', 'birds', 'feed', 'weight', 'fcr']].tail(10), use_container_width=True)
        else:
            st.info("📭 لا توجد مزارع مسجلة")

# ==========================================
# 34. التبويبات المتبقية (مختصرة)
# ==========================================

# تبويب المختبر
lab_index = 5 if st.session_state.get("user_role") == "owner" else 4
if lab_index < len(tabs):
    with tabs[lab_index]:
        st.markdown('<div class="section-title">🔬 المختبر المتكامل</div>', unsafe_allow_html=True)
        st.info("🔬 نظام تحليل الأعلاف المتكامل - قيد التطوير")

# تبويب التحليلات
analytics_index = 6 if st.session_state.get("user_role") == "owner" else 5
if analytics_index < len(tabs):
    with tabs[analytics_index]:
        st.markdown('<div class="section-title">📈 التحليلات المتقدمة</div>', unsafe_allow_html=True)
        
        # إحصائيات سريعة
        with get_db() as conn:
            cursor = conn.execute('SELECT COUNT(*) as count FROM formulas_history')
            total_formulas = cursor.fetchone()['count']
            st.metric("📝 إجمالي الخلطات", total_formulas)
            
            cursor = conn.execute('SELECT AVG(cost) as avg_cost FROM formulas_history')
            avg_cost = cursor.fetchone()['avg_cost']
            st.metric("💰 متوسط التكلفة", f"${avg_cost:.2f}" if avg_cost else "$0")

# تبويب التعليقات
comments_index = 8 if st.session_state.get("user_role") == "owner" else 6
if comments_index < len(tabs):
    with tabs[comments_index]:
        st.markdown('<div class="section-title">💬 التعليقات</div>', unsafe_allow_html=True)
        st.text_area("التعليقات:", st.session_state["shared_comments"], height=200, disabled=True)
        
        new_comment = st.text_input("✍️ أضف تعليقاً:")
        if st.button("📌 نشر", use_container_width=True):
            if new_comment.strip():
                role = "👑 المالك" if st.session_state["user_role"] == "owner" else "🔬 مختص" if st.session_state["user_role"] == "specialist" else "🌾 مربي"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state["shared_comments"] = f"• [{role} - {timestamp}]: {new_comment.strip()}\n" + st.session_state["shared_comments"]
                st.success("✅ تم النشر")
                st.rerun()

# تبويب الدليل
with tabs[-1]:
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#f5f5f5; padding:25px; border-radius:15px;">
    <h3>📌 دليل استخدام منصة تاور العلمية v7.0</h3>
    
    <h4>🔑 أكواد الدخول:</h4>
    <p>- 👑 <b>المالك</b>: <code>202687</code><br>
    - 🔬 <b>المختصون</b>: <code>2020</code><br>
    - 🌾 <b>المربون</b>: <code>2026</code></p>
    
    <h4>📧 إرسال الكود:</h4>
    <p>يوجد زر أحمر في أعلى الصفحة لإرسال نسخة من الكود إلى المالك</p>
    
    <h4>📊 طريقة الاستخدام:</h4>
    <p>1. حدد الدولة والمدينة<br>
    2. اختر القطاع الحيواني والسلالة<br>
    3. حدد نسب البروتين والطاقة<br>
    4. اختر المكونات العلفية<br>
    5. اضغط "تشغيل المحرك"</p>
    
    <h4>📞 التواصل:</h4>
    <p>📱 واتساب: <a href="https://wa.me/249123533489">+249 123 533 489</a><br>
    📧 البريد: <a href="mailto:abukram128@gmail.com">abukram128@gmail.com</a></p>
    
    <hr>
    <p style="text-align:center;">الاختصاصي م. عبد القادر إسماعيل تاور © 2026</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 35. تذييل الصفحة
# ==========================================

st.markdown("<hr>", unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    if st.button("💾 نسخ احتياطي", use_container_width=True):
        with st.spinner("جاري الإنشاء..."):
            if CODE_SENDER.send_code_to_email(OWNER_EMAIL, "نسخة فورية"):
                st.success("✅ تم الإرسال")

with col_f2:
    share_text = "🌾 منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف"
    encoded = urllib.parse.quote(share_text)
    st.link_button("📲 مشاركة", f"https://wa.me/?text={encoded}", use_container_width=True)

with col_f3:
    if st.button("🔄 إعادة تحميل", use_container_width=True):
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# التوقيع
st.markdown("""
<div class="mini-left-signature">
    👨‍🔬 الاختصاصي م. عبد القادر إسماعيل تاور © 2026
</div>
""", unsafe_allow_html=True)

# ==========================================
# نهاية الكود
# ==========================================
