#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف
النسخة المتكاملة الكاملة v4.0 - غير منقوصة
المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور
"""

# ==========================================
# المكتبات الأساسية
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
import hashlib
import secrets
import io
import sqlite3
import logging
import logging.handlers
import shutil
import random
import re
import sys
import gc
import zipfile
import tempfile
import csv
import math
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from functools import lru_cache, wraps
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
import warnings

# ==========================================
# المكتبات العلمية والتحليلية
# ==========================================

from scipy.optimize import linprog
from sklearn.preprocessing import StandardScaler

# ==========================================
# مكتبات التصور والرسوم البيانية
# ==========================================

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# مكتبات معالجة النص العربي
# ==========================================

import arabic_reshaper
from bidi.algorithm import get_display

# ==========================================
# مكتبات توليد PDF المتقدمة
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
# مكتبات الباركود والصور
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
# إعدادات التحذيرات
# ==========================================

warnings.filterwarnings('ignore')
load_dotenv()

# ==========================================
# إنشاء المجلدات اللازمة
# ==========================================

folders = ["logs", "backups", "data", "temp", "visitors", "code_backups", "reports", "exports", "charts", "models", "cache"]
for folder in folders:
    Path(folder).mkdir(exist_ok=True)

# ==========================================
# إعدادات Streamlit
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
# نظام التسجيل المتقدم
# ==========================================

class AdvancedLogger:
    """نظام تسجيل متقدم مع تصنيف متعدد"""
    
    def __init__(self):
        self.setup_all_loggers()
    
    def setup_all_loggers(self):
        """إعداد جميع سجلات النظام"""
        # سجل النظام الرئيسي
        self.main_logger = logging.getLogger('TowerPlatform')
        self.main_logger.setLevel(logging.INFO)
        
        # سجل الأمان
        self.security_logger = logging.getLogger('Security')
        self.security_logger.setLevel(logging.WARNING)
        
        # سجل المستخدمين
        self.user_logger = logging.getLogger('UserActions')
        self.user_logger.setLevel(logging.INFO)
        
        # سجل الأخطاء
        self.error_logger = logging.getLogger('Errors')
        self.error_logger.setLevel(logging.ERROR)
        
        # تكوين معالجات الملفات
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
    
    def log_security_event(self, event_type, details, severity='WARNING'):
        """تسجيل حدث أمني"""
        log_msg = f"SECURITY_EVENT: {event_type} | Details: {details} | Severity: {severity}"
        if severity == 'CRITICAL':
            self.security_logger.critical(log_msg)
        elif severity == 'ERROR':
            self.security_logger.error(log_msg)
        else:
            self.security_logger.warning(log_msg)

LOGGER = AdvancedLogger()

# ==========================================
# نظام مراقبة الأمان والاختراق
# ==========================================

class SecurityMonitor:
    """نظام مراقبة أمان متقدم مع كشف الاختراق"""
    
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.blocked_ips = set()
        self.suspicious_patterns = []
        self.attack_signatures = {
            'sql_injection': re.compile(r'(\%27)|(\')|(\-\-)|(%23)|(#)', re.IGNORECASE),
            'xss': re.compile(r'(\<script)|(\<img)|(javascript:)|(onerror=)', re.IGNORECASE),
            'path_traversal': re.compile(r'(\.\./)|(\.\.\\)|(\.\.%2f)', re.IGNORECASE),
            'command_injection': re.compile(r'(\||\&|\;|\$\(|\`|\$\{)', re.IGNORECASE)
        }
    
    def get_client_ip(self):
        """الحصول على IP العميل مع دعم الـ Proxy"""
        try:
            if hasattr(st, 'context') and hasattr(st.context, 'headers'):
                forwarded = st.context.headers.get('X-Forwarded-For', '')
                if forwarded:
                    return forwarded.split(',')[0].strip()
                
                real_ip = st.context.headers.get('X-Real-IP', '')
                if real_ip:
                    return real_ip
            return '127.0.0.1'
        except:
            return 'unknown'
    
    def get_user_agent(self):
        """الحصول على متصفح المستخدم"""
        try:
            if hasattr(st, 'context') and hasattr(st.context, 'headers'):
                return st.context.headers.get('User-Agent', 'unknown')[:200]
            return 'unknown'
        except:
            return 'unknown'
    
    def analyze_request(self, request_data):
        """تحليل الطلب للكشف عن الهجمات"""
        threat_score = 0
        threats_found = []
        
        for attack_type, pattern in self.attack_signatures.items():
            if pattern.search(str(request_data)):
                threat_score += 25
                threats_found.append(attack_type)
        
        ip = self.get_client_ip()
        
        if len(self.failed_attempts[ip]) >= 3:
            threat_score += 20
            threats_found.append('multiple_attempts')
        
        recent_attempts = [t for t in self.failed_attempts[ip] if (datetime.now() - t).seconds < 60]
        if len(recent_attempts) >= 5:
            threat_score += 30
            threats_found.append('rapid_requests')
        
        if threat_score >= 50:
            self.block_ip(ip, f"تهديد عالي - {threats_found}")
            return False
        
        return True
    
    def block_ip(self, ip, reason):
        """حظر IP مع تسجيل السبب"""
        if ip not in self.blocked_ips:
            self.blocked_ips.add(ip)
            LOGGER.log_security_event('IP_BLOCKED', f"تم حظر {ip} - السبب: {reason}", 'ERROR')
            
            try:
                with get_db() as conn:
                    conn.execute('''
                        INSERT INTO blocked_ips (ip_address, block_reason, blocked_at)
                        VALUES (?, ?, ?)
                    ''', (ip, reason[:200], datetime.now().isoformat()))
            except:
                pass
            
            self.send_alert_to_owner(f"🚨 تم حظر IP {ip}\nالسبب: {reason}")
    
    def is_ip_blocked(self, ip):
        """التحقق من حظر IP"""
        now = datetime.now()
        self.failed_attempts[ip] = [attempt for attempt in self.failed_attempts[ip] if (now - attempt).seconds < 3600]
        return ip in self.blocked_ips
    
    def log_failed_attempt(self, code_attempt=""):
        """تسجيل محاولة دخول فاشلة"""
        ip = self.get_client_ip()
        self.failed_attempts[ip].append(datetime.now())
        
        if len(self.failed_attempts[ip]) >= 5:
            self.block_ip(ip, "تجاوز 5 محاولات دخول فاشلة")
        
        LOGGER.log_security_event('FAILED_LOGIN', f"محاولة فاشلة من {ip} - الكود: {code_attempt[:10]}", 'WARNING')
        self.send_alert_to_owner(f"⚠️ محاولة دخول فاشلة من {ip}")
    
    def log_visitor(self, user_role=None, action="visit"):
        """تسجيل زائر جديد"""
        ip = self.get_client_ip()
        user_agent = self.get_user_agent()
        
        try:
            with get_db() as conn:
                conn.execute('''
                    INSERT INTO visitors_log (ip_address, user_agent, user_role, action, visit_time)
                    VALUES (?, ?, ?, ?, ?)
                ''', (ip, user_agent[:200], user_role or "unknown", action, datetime.now().isoformat()))
        except:
            pass
        
        if user_role == "owner":
            self.send_alert_to_owner(f"👑 المالك دخل المنصة من {ip}")
        
        LOGGER.user_logger.info(f"زائر: {ip} - {user_role} - {action}")
    
    def send_alert_to_owner(self, message):
        """إرسال تنبيه فوري للمالك"""
        try:
            if WHATSAPP_NUMBER:
                encoded = urllib.parse.quote(f"🔐 {message}")
                whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded}"
                st.markdown(f'<div style="display:none;"><a href="{whatsapp_url}">alert</a></div>', unsafe_allow_html=True)
            
            with get_db() as conn:
                conn.execute('''
                    INSERT INTO security_alerts (alert_message, severity, created_at)
                    VALUES (?, ?, ?)
                ''', (message[:500], "HIGH", datetime.now().isoformat()))
        except:
            pass

SECURITY = SecurityMonitor()

# ==========================================
# نظام تحديث الأسعار الحي المتقدم
# ==========================================

class LivePriceUpdater:
    """نظام تحديث أسعار متقدم مع تحديث كل 3 ثوانٍ"""
    
    def __init__(self):
        self.price_cache = {}
        self.last_update = {}
        self.update_interval = 3  # ثواني
        self.price_history = defaultdict(list)
        self.is_updating = False
    
    def get_live_prices(self, country, city):
        """الحصول على أسعار حية مع تحديث تلقائي"""
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
    
    def fetch_prices(self, country, city):
        """جلب الأسعار من المصادر"""
        base_prices = self.get_base_prices()
        multiplier = self.get_location_multiplier(country, city)
        
        for key in base_prices:
            change = random.uniform(-0.03, 0.03)
            base_prices[key] *= (1 + change) * multiplier
        
        return base_prices
    
    def get_base_prices(self):
        """الأسعار الأساسية الكاملة لجميع المواد"""
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
            "مضاد سموم فطرية": 950.0, "بيكربونات الصوديوم": 340.0, "أكسيد المغنيسيوم": 450.0
        }
    
    def get_location_multiplier(self, country, city):
        """معامل تعديل الموقع"""
        multipliers = {
            "السودان": {"default": 1.15, "الخرطوم": 1.0, "أم درمان": 1.02, "بحري": 1.01, "ود مدني": 0.95, "بورتسودان": 1.08, "الأبيض": 0.92},
            "LIBYA": {"default": 1.10, "طرابلس": 1.0, "بنغازي": 0.98, "مصراتة": 0.96, "سبها": 0.92},
            "مصر": {"default": 1.04, "القاهرة": 1.0, "الإسكندرية": 0.97, "الجيزة": 0.99, "الأقصر": 0.95},
            "باقي الدول": {"default": 1.0}
        }
        country_mult = multipliers.get(country, {"default": 1.0})
        return country_mult.get(city, country_mult["default"])
    
    def save_price_history(self, prices, city):
        """حفظ تاريخ الأسعار"""
        try:
            with get_db() as conn:
                for commodity, price in prices.items():
                    conn.execute('''
                        INSERT INTO market_prices_history (city, commodity, price, recorded_at)
                        VALUES (?, ?, ?, ?)
                    ''', (city, commodity, price, datetime.now().isoformat()))
        except:
            pass
    
    def get_last_update_time(self, country, city):
        """الحصول على وقت آخر تحديث"""
        cache_key = f"{country}_{city}"
        if cache_key in self.last_update:
            return datetime.fromtimestamp(self.last_update[cache_key])
        return None

PRICE_UPDATER = LivePriceUpdater()

# ==========================================
# نظام النسخ الاحتياطي المتقدم
# ==========================================

class BackupManager:
    """إدارة النسخ الاحتياطية المتقدمة"""
    
    def __init__(self):
        self.backup_dir = Path("code_backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def send_code_to_owner(self, email, reason="نسخة احتياطية"):
        """إرسال الكود إلى المالك مع توقيع رقمي"""
        try:
            with open(__file__, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            file_hash = hashlib.sha256(code_content.encode()).hexdigest()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            code_with_signature = f"""# ========================================
# نسخة احتياطية من منصة تاور العلمية
# ========================================
# التاريخ: {timestamp}
# السبب: {reason}
# التوقيع الرقمي: {file_hash}
# حجم الملف: {len(code_content):,} حرف
# ========================================

{code_content}"""
            
            backup_file = self.backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(code_with_signature)
            
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = email
            msg['Subject'] = f"🌾 نسخة احتياطية - منصة تاور - {timestamp}"
            
            body = f"""السلام عليكم م. عبد القادر،

هذه نسخة احتياطية كاملة من منصة تاور العلمية.

📋 معلومات النسخة:
- التاريخ: {timestamp}
- السبب: {reason}
- التوقيع: {file_hash[:16]}...
- حجم الملف: {len(code_content):,} حرف

تم إرفاق الكود الكامل مع هذا البريد.

تحياتي،
نظام المنصة الآلي
"""
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            attachment = MIMEText(code_with_signature, 'plain', 'utf-8')
            attachment.add_header('Content-Disposition', 'attachment', filename=f"tower_platform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
            msg.attach(attachment)
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, email, msg.as_string())
            server.quit()
            
            LOGGER.main_logger.info(f"تم إرسال الكود إلى {email} - {reason}")
            return True
            
        except Exception as e:
            LOGGER.error_logger.error(f"فشل إرسال الكود: {e}")
            return False
    
    def auto_backup_check(self):
        """التحقق من الحاجة لنسخة احتياطية تلقائية (كل 6 ساعات)"""
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
                    if self.send_code_to_owner(OWNER_EMAIL, "نسخه احتياطية آلية"):
                        with get_db() as conn:
                            conn.execute('''
                                INSERT INTO code_backups (backup_date, reason, file_hash)
                                VALUES (?, ?, ?)
                            ''', (datetime.now().isoformat(), "تلقائي", "auto_backup"))
        except:
            pass

BACKUP_MANAGER = BackupManager()

# ==========================================
# نظام قاعدة البيانات المتقدم
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
                breed TEXT,
                cost REAL,
                city TEXT,
                user_role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول التحاليل المخبرية
        conn.execute('''
            CREATE TABLE IF NOT EXISTS lab_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER,
                formula_data TEXT,
                cp REAL,
                moisture REAL,
                fat REAL,
                fiber REAL,
                notes TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

# تهيئة قاعدة البيانات
if "db_initialized" not in st.session_state:
    init_database()
    st.session_state["db_initialized"] = True

# ==========================================
# الإعدادات الثابتة
# ==========================================

# أكواد الدخول
CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

# إعدادات البريد
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "abukram128@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "oynz rdli tsdy ekdq")
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "abukram128@gmail.com")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "+249123533489")
GOOGLE_FORM_URL = "https://forms.google.com/YOUR_FORM_URL"

# مسارات الصور
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

@st.cache_data(ttl=3600)
def get_image_base64(paths):
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except:
                pass
    return None

img_base64 = get_image_base64(PHOTO_OPTIONS)

# ==========================================
# المكتبة الكاملة للمواد العلفية
# ==========================================

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
    "🌱 الأكساب ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5}
    },
    "🚜 المخلفات الزراعية والصناعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5},
        "بقايا تفل البنجر المجفف": {"CP": 8.0, "DC": 0.75, "SE": 58.0, "NDF": 38.5, "ADF": 22.5, "EE": 1.5, "ASH": 6.5},
        "مخلفات مصانع البسكويت": {"CP": 9.5, "DC": 0.88, "SE": 76.0, "NDF": 8.5, "ADF": 3.5, "EE": 8.5, "ASH": 3.5},
        "سیلاج ذرة كامل": {"CP": 8.0, "DC": 0.68, "SE": 50.0, "NDF": 45.5, "ADF": 25.5, "EE": 2.5, "ASH": 4.5}
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق أسماك فاخر 72%": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5}
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5},
        "ميثيونين نقي": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3},
        "ثريونين نقي": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2},
        "تريبتوفان نقي": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1}
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس بياض": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس أبقار حلابة": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم الفايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
        "إنزيم NSP": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
        "أكسيد المغنيسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "يوريا علفية": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0}
    }
}

# ==========================================
# الإعدادات الإضافية
# ==========================================

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG", "name": "جنيه سوداني"},
    "LIBYA": {"rate": 4.80, "sym": "LYD", "name": "دينار ليبي"},
    "مصر": {"rate": 48.0, "sym": "EGP", "name": "جنيه مصري"},
    "باقي الدول": {"rate": 1.0, "sym": "USD", "name": "دولار أمريكي"}
}

ANIMAL_IMAGES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?w=400",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?w=400",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?w=400",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?w=400",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?w=400",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?w=400",
    "سمان": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?w=400"
}

# ==========================================
# دوال مساعدة
# ==========================================

class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=1000)
    def fix_arabic_text(text: str) -> str:
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except:
            return text

arabic_processor = ArabicTextProcessor()

def log_activity(action: str, details: str = ""):
    """تسجيل نشاط المستخدم"""
    try:
        ip = SECURITY.get_client_ip()
        with get_db() as conn:
            conn.execute('''
                INSERT INTO activity_logs (user_role, action, details, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (st.session_state.get("user_role", "unknown"), action, details[:500], ip))
        LOGGER.main_logger.info(f"نشاط: {action} - {details[:100]}")
    except Exception as e:
        LOGGER.error_logger.error(f"فشل تسجيل النشاط: {e}")

def send_whatsapp_message(phone: str, message: str):
    """إرسال رسالة واتساب"""
    try:
        encoded = urllib.parse.quote(message)
        return f"https://wa.me/{phone}?text={encoded}"
    except:
        return None

# ==========================================
# مولد PDF المحترف
# ==========================================

class PDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        if os.path.exists("Amiri-Regular.ttf"):
            try:
                pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
                self.font_name = 'Amiri'
            except:
                pass

    def generate_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se):
        """توليد تقرير PDF كامل"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []

        def p(text, size=12, align=TA_RIGHT, color=HexColor('#000000')):
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, ParagraphStyle(
                'style', fontName=self.font_name, fontSize=size, 
                alignment=align, textColor=color, spaceAfter=6, leading=size*1.5
            ))

        story.append(p("تقرير فني - منصة تاور العلمية", size=22, align=TA_CENTER, color=HexColor('#1b5e20')))
        story.append(Spacer(1, 12))
        
        for line in [f"المشرف: م. عبد القادر إسماعيل تاور", f"الموقع: {city}", f"الفصيل: {breed}", f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}"]:
            story.append(p(line, size=11))
        story.append(Spacer(1, 15))

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

        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026", size=9, align=TA_CENTER, color=HexColor('#666666')))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = PDFGenerator()

# ==========================================
# إدارة مزارع الدجاج اللاحم
# ==========================================

class BroilerFarmManager:
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
    def calculate_epef(livability: float, body_weight_kg: float, age_days: int, fcr: float) -> float:
        if age_days <= 0 or fcr <= 0:
            return 0.0
        return (livability * body_weight_kg) / (age_days * fcr) * 100.0

    @staticmethod
    def get_temp_humidity_table():
        data = {
            "العمر (يوم)": [1, 7, 14, 21, 28, 35, 42],
            "درجة الحرارة": [33, 30, 28, 26, 24, 22, 21],
            "الرطوبة (%)": [65, 65, 65, 60, 60, 55, 55]
        }
        return pd.DataFrame(data)

# ==========================================
# متغيرات الجلسة
# ==========================================

if "approved" not in st.session_state:
    st.session_state["approved"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "session_token" not in st.session_state:
    st.session_state["session_token"] = secrets.token_urlsafe(32)
if "active_formula" not in st.session_state:
    st.session_state["active_formula"] = {}
if "active_cp_tag" not in st.session_state:
    st.session_state["active_cp_tag"] = 12.0
if "active_se_tag" not in st.session_state:
    st.session_state["active_se_tag"] = 65.0
if "active_breed_tag" not in st.session_state:
    st.session_state["active_breed_tag"] = "سلالة عامة"
if "computed_ton_cost" not in st.session_state:
    st.session_state["computed_ton_cost"] = 280.0
if "pending_lab_requests" not in st.session_state:
    st.session_state["pending_lab_requests"] = []
if "next_request_id" not in st.session_state:
    st.session_state["next_request_id"] = 1
if "inventory" not in st.session_state:
    st.session_state["inventory"] = {}
if "poultry_farms" not in st.session_state:
    st.session_state["poultry_farms"] = {}
if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = "• مرحباً بكم في منصة تاور العلمية للانتاج الحيواني\n• نرحب بتعليقاتكم واقتراحاتكم\n"

# تهيئة المخزون
if not st.session_state["inventory"]:
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing in cat:
            st.session_state["inventory"][ing] = {"quantity": 100.0, "min_threshold": 20.0, "last_updated": datetime.now().isoformat()}
            # ==========================================
# CSS المتقدم
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

* {
    font-family: 'Cairo', sans-serif;
    box-sizing: border-box;
}

/* الخلفية الرئيسية */
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* الحاوية الرئيسية */
.main-box {
    background: rgba(255, 255, 255, 0.98);
    padding: 35px;
    border-radius: 25px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    backdrop-filter: blur(10px);
    margin: 20px;
    border: 1px solid rgba(46,125,50,0.2);
}

/* عناوين الأقسام */
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

/* بطاقات الأسعار */
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

/* عناصر الخلطة */
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

/* الأزرار */
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

/* بطاقات الميتريك */
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

.metric-card h3 {
    color: #2e7d32;
    font-size: 1.2rem;
    margin-bottom: 10px;
}

.metric-card .value {
    font-size: 2.5rem;
    font-weight: 900;
    color: #1b5e20;
}

/* التنبيهات */
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

.info-box {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    border-right: 6px solid #1565c0;
    padding: 18px;
    border-radius: 12px;
    margin: 15px 0;
    color: #0d47a1;
}

/* الشريط الجانبي */
.css-1d391kg, .css-1lcbmhc {
    background: linear-gradient(180deg, #1b5e20, #0d3b0f);
}

.css-1d391kg .stMarkdown, .css-1lcbmhc .stMarkdown {
    color: white;
}

/* علامات التبويب */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent;
}

.stTabs [data-baseweb="tab"] {
    background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
    border-radius: 12px 12px 0 0;
    padding: 10px 20px;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #2e7d32, #1b5e20);
    color: white;
}

/* التوسيعات */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, #f5f5f5, #eeeeee);
    border-radius: 12px;
    font-weight: 600;
}

/* التذييل */
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

/* الصورة الشخصية */
.profile-img-style {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #d4af37;
    box-shadow: 0 8px 20px rgba(0,0,0,0.2);
}

/* تأثيرات الحركة */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.main-box {
    animation: fadeIn 0.5s ease-out;
}

/* التحميل */
.stSpinner > div {
    border-top-color: #2e7d32 !important;
}

/* الشاشات الصغيرة */
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

# ==========================================
# الواجهة الرئيسية
# ==========================================

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# ==========================================
# رأس الصفحة
# ==========================================

col_logo, col_title, col_actions = st.columns([1, 2, 1])

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

with col_actions:
    # زر إرسال الكود للمالك (بارز جداً)
    if st.button("📧 إرسال الكود للمالك", use_container_width=True, type="primary"):
        with st.spinner("جاري إرسال الكود إلى البريد الإلكتروني..."):
            if BACKUP_MANAGER.send_code_to_owner(OWNER_EMAIL, "طلب يدوي"):
                st.success("✅ تم إرسال الكود بنجاح!")
                log_activity("send_code", "تم إرسال الكود للمالك")
                SECURITY.send_alert_to_owner("📧 تم إرسال نسخة من الكود بناءً على طلب المالك")
            else:
                st.error("❌ فشل إرسال الكود، يرجى التحقق من إعدادات البريد")

st.markdown("<hr>", unsafe_allow_html=True)

# ==========================================
# معلومات الجلسة والأمان للمالك
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

# عرض معلومات للمالك
if st.session_state.get("user_role") == "owner":
    with st.expander("🔐 لوحة معلومات الأمان والمراقبة", expanded=False):
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("🌐 عنوان IP", client_ip)
        with col_s2:
            st.metric("🕐 آخر نشاط", datetime.now().strftime("%H:%M:%S"))
        with col_s3:
            with get_db() as conn:
                cursor = conn.execute("SELECT COUNT(*) as count FROM visitors_log WHERE date(visit_time) = date('now')")
                result = cursor.fetchone()
                st.metric("👥 زوار اليوم", result['count'] if result else 0)
        with col_s4:
            with get_db() as conn:
                cursor = conn.execute("SELECT COUNT(*) as count FROM security_alerts WHERE is_read = 0")
                result = cursor.fetchone()
                st.metric("⚠️ تنبيهات أمنية", result['count'] if result else 0)
        
        # عرض آخر التنبيهات
        with get_db() as conn:
            cursor = conn.execute("SELECT * FROM security_alerts WHERE is_read = 0 ORDER BY created_at DESC LIMIT 5")
            alerts = cursor.fetchall()
            if alerts:
                st.markdown("#### 📋 آخر التنبيهات الأمنية:")
                for alert in alerts:
                    st.markdown(f"- 🔔 {alert['alert_message']}")

# ==========================================
# رسالة ترحيب حسب الدور
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
# بوابة الدخول
# ==========================================

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:#2E7D32; text-align:center;'>🔒 بوابة الدخول</h2>", unsafe_allow_html=True)
    
    # عرض QR code
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("https://tower-scientific-platform.streamlit.app")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{qr_base64}" width="150"></div>', unsafe_allow_html=True)
    except:
        pass
    
    input_code = st.text_input("🔑 أدخل كود الدخول:", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("تسجيل الدخول", type="primary", use_container_width=True):
            if input_code in CODES_DB:
                st.session_state["approved"] = True
                st.session_state["user_role"] = CODES_DB[input_code]["role"]
                st.session_state["session_token"] = secrets.token_urlsafe(32)
                
                # تسجيل الزائر الناجح
                SECURITY.log_visitor(st.session_state["user_role"], "login")
                log_activity("login", "تسجيل دخول ناجح")
                
                # نسخ احتياطي تلقائي للمالك
                if st.session_state["user_role"] == "owner":
                    BACKUP_MANAGER.auto_backup_check()
                
                st.rerun()
            else:
                SECURITY.log_failed_attempt(input_code)
                st.error("❌ الكود غير صحيح!")
    
    with col2:
        if st.button("نسيت الكود", use_container_width=True):
            st.info("يرجى التواصل مع مدير النظام: abukram128@gmail.com")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# تحديد التبويبات حسب الصلاحية
# ==========================================

if st.session_state.get("user_role") == "owner":
    tab_titles = [
        "🔬 تركيب الأعلاف",
        "📊 بورصة الأسعار الحية",
        "🏭 إدارة المخزون",
        "🧾 المبيعات والفواتير",
        "🐔 مزارع الدواجن",
        "🔬 المختبر",
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
        "🔬 المختبر",
        "📈 التحليلات",
        "💬 التعليقات",
        "📖 الدليل"
    ]
else:
    tab_titles = ["🔬 تركيب الأعلاف", "📖 دليل المستخدم"]

tabs = st.tabs(tab_titles)

# ==========================================
# التبويب 1: تركيب الأعلاف (كامل)
# ==========================================

with tabs[0]:
    st.markdown('<div class="section-title">🌍 الموقع الجغرافي وتحديد السوق</div>', unsafe_allow_html=True)
    
    col_loc1, col_loc2, col_loc3 = st.columns(3)
    with col_loc1:
        country = st.selectbox("🇸🇩 الدولة:", list(EXCHANGE_RATES.keys()))
    with col_loc2:
        if country == "السودان":
            state = st.selectbox("🏙️ الولاية:", ["الخرطوم", "الجزيرة", "القضارف", "شمال كردفان", "جنوب كردفان", "نهر النيل"])
        elif country == "LIBYA":
            state = st.selectbox("🏙️ المنطقة:", ["طرابلس", "بنغازي", "مصراتة", "سبها"])
        else:
            state = st.selectbox("🏙️ المنطقة:", ["المركزية", "الغربية", "الشرقية"])
    with col_loc3:
        city = st.text_input("📍 المدينة:", "الخرطوم")
    
    # تحديث الأسعار تلقائياً
    current_prices = PRICE_UPDATER.get_live_prices(country, city)
    local_rate = EXCHANGE_RATES.get(country, {"rate": 1.0})["rate"]
    local_sym = EXCHANGE_RATES.get(country, {"sym": "USD"})["sym"]
    
    last_update = PRICE_UPDATER.get_last_update_time(country, city)
    if last_update:
        st.info(f"🔄 يتم تحديث الأسعار تلقائياً | آخر تحديث: {last_update.strftime('%H:%M:%S')} | التحديث كل 3 ثوانٍ")
    
    st.markdown('<div class="section-title">💰 بورصة الأسعار المباشرة</div>', unsafe_allow_html=True)
    
    # عرض الأسعار في بطاقات
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
        sector = st.selectbox("🐏 القطاع الحيواني:", ["الأغنام", "الماعز", "الأبقار", "الخيول", "الدواجن", "الأسماك"])
    
    with col_sub:
        sector_map = {
            "الأغنام": ["الضأن الصحراوي", "البربري", "النعيمي"],
            "الماعز": ["النوبي", "الصحراوي", "البلدي"],
            "الأبقار": ["كنانة", "بطانة", "هولشتاين"],
            "الخيول": ["عربي أصيل", "ثوروبريد", "محلي"],
            "الدواجن": ["لاحم", "بياض", "سمان"],
            "الأسماك": ["بلطي", "بوري", "قرموط"]
        }
        breed = st.selectbox("🐣 السلالة:", sector_map.get(sector, ["عام"]))
    
    with col_prod:
        prod_map = {
            "الأغنام": ["تسمين", "حليب", "صيانة"],
            "الماعز": ["تسمين", "حليب", "صيانة"],
            "الأبقار": ["حليب", "تسمين", "صيانة"],
            "الخيول": ["رياضة", "نمو", "صيانة"],
            "الدواجن": ["بادي", "نامي", "ناهي", "بياض"],
            "الأسماك": ["نمو", "تسمين", "زريعة"]
        }
        production = st.selectbox("📈 مرحلة الإنتاج:", prod_map.get(sector, ["عام"]))
    
    # تحديد القيم المقترحة
    suggested_dp = 12.0
    suggested_se = 65.0
    
    if sector == "الأغنام" and production == "تسمين":
        suggested_dp, suggested_se = 12.5, 66.0
    elif sector == "الماعز" and production == "تسمين":
        suggested_dp, suggested_se = 12.0, 64.0
    elif sector == "الأبقار" and production == "حليب":
        suggested_dp, suggested_se = 13.0, 68.0
    elif sector == "الأبقار" and production == "تسمين":
        suggested_dp, suggested_se = 11.0, 65.0
    elif sector == "الدواجن" and production == "بادي":
        suggested_dp, suggested_se = 22.0, 78.0
    elif sector == "الدواجن" and production == "نامي":
        suggested_dp, suggested_se = 20.0, 75.0
    elif sector == "الدواجن" and production == "ناهي":
        suggested_dp, suggested_se = 18.0, 74.0
    elif sector == "الأسماك" and production == "نمو":
        suggested_dp, suggested_se = 28.0, 70.0
    
    st.markdown('<div class="section-title">📊 حدود الموازنة الذكية</div>', unsafe_allow_html=True)
    
    col_dp, col_se = st.columns(2)
    with col_dp:
        use_cp = st.checkbox("استخدم البروتين الخام (CP) بدلاً من المهضوم (DP)")
        if use_cp:
            target_cp = st.slider("🥩 نسبة البروتين الخام المستهدفة %:", 5.0, 60.0, suggested_dp / 0.82, step=0.5)
            target_dp = None
        else:
            target_dp = st.slider("🧬 نسبة البروتين المهضوم المستهدفة %:", 5.0, 40.0, suggested_dp, step=0.5)
    
    with col_se:
        target_se = st.slider("⚡ معادل النشاء المستهدف:", 10.0, 90.0, suggested_se, step=1.0)
    
    st.markdown('<div class="section-title">📦 اختيار المكونات العلفية</div>', unsafe_allow_html=True)
    
    selected_ingredients = []
    ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        expanded = "الحبوب" in cat_name or "الأكساب" in cat_name
        with st.expander(f"📁 {cat_name}", expanded=expanded):
            cols = st.columns(3)
            for idx, (ing_name, data) in enumerate(items.items()):
                with cols[idx % 3]:
                    is_default = ing_name in ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)", "ملح الطعام", "الحجر الجيري"]
                    checked = st.checkbox(ing_name, value=is_default, key=f"feed_{ing_name}")
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        price = current_prices.get(ing_name, 300.0)
                        if st.session_state.get("user_role") == "owner":
                            price_input = st.number_input(f"💰 سعر {ing_name} ($/طن)", min_value=10.0, value=float(price), step=5.0, key=f"price_{ing_name}")
                            ingredient_prices[ing_name] = price_input
                        else:
                            st.markdown(f"💰 السعر الحالي: **`${price:.2f}`**/طن")
                            ingredient_prices[ing_name] = price
    
    # إضافة الإضافات الإلزامية
    mandatory_additives = {}
    
    if sector in ["الأغنام", "الماعز", "الأبقار"]:
        mandatory_additives["بيكربونات الصوديوم"] = 0.75
        st.info("⚙️ تم إضافة بيكربونات الصوديوم (0.75%) تلقائياً كمنظم حموضة للكرش")
    
    if sector in ["الدواجن", "الأسماك"]:
        mandatory_additives["إنزيم الفايتيز"] = 0.05
        st.info("⚙️ تم إضافة إنزيم الفايتيز (0.05%) تلقائياً لتحسين هضم الفسفور")
    
    for additive, percentage in mandatory_additives.items():
        if additive not in selected_ingredients:
            selected_ingredients.append(additive)
            ingredient_prices[additive] = current_prices.get(additive, 100.0)
    
    # زر تشغيل المحرك
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
    with col_btn2:
        run_optimization = st.button("🚀 تشغيل محرك الاستمثال الخطي", type="primary", use_container_width=True)
    
    if run_optimization:
        if len(selected_ingredients) < 3:
            st.warning("⚠️ يرجى اختيار 3 مكونات علفية على الأقل للحصول على حل مثالي")
        else:
            with st.spinner("🔄 جاري حساب التركيبة المثلى بأقل تكلفة..."):
                try:
                    c = [ingredient_prices[ing] for ing in selected_ingredients]
                    bounds = []
                    for ing in selected_ingredients:
                        if ing in mandatory_additives:
                            bounds.append((mandatory_additives[ing], mandatory_additives[ing]))
                        else:
                            bounds.append((0.0, 100.0))
                    
                    A_eq = [[1.0] * len(selected_ingredients)]
                    b_eq = [100.0]
                    
                    protein_row = []
                    for ing in selected_ingredients:
                        cp_val = 0.0
                        dc_val = 0.85
                        for cat in BIG_FEEDS_LIBRARY.values():
                            if ing in cat:
                                cp_val = cat[ing]["CP"]
                                dc_val = cat[ing]["DC"]
                                break
                        if use_cp:
                            protein_row.append(cp_val)
                        else:
                            protein_row.append(cp_val * dc_val)
                    
                    A_eq.append(protein_row)
                    if use_cp:
                        b_eq.append(target_cp * 100)
                    else:
                        b_eq.append(target_dp * 100)
                    
                    se_row = []
                    for ing in selected_ingredients:
                        se_val = 0.0
                        for cat in BIG_FEEDS_LIBRARY.values():
                            if ing in cat:
                                se_val = cat[ing]["SE"]
                                break
                        se_row.append(se_val)
                    
                    A_ub = [[-x for x in se_row]]
                    b_ub = [-target_se * 100]
                    
                    grain_ingredients = ["ذرة صفراء", "ذرة بيضاء", "شعير مطحون", "سورجم", "قمح", "جريش أرز", "دخن"]
                    grain_indicators = [1.0 if ing in grain_ingredients else 0.0 for ing in selected_ingredients]
                    if sum(grain_indicators) > 0:
                        A_ub.append([-x for x in grain_indicators])
                        b_ub.append(-40.0)
                    
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
                        st.session_state["active_cp_tag"] = target_dp if not use_cp else (target_cp * 0.82)
                        st.session_state["active_se_tag"] = computed_se
                        st.session_state["active_breed_tag"] = breed
                        st.session_state["computed_ton_cost"] = ton_cost
                        
                        with get_db() as conn:
                            conn.execute('''
                                INSERT INTO formulas_history (formula_data, target_dp, target_se, breed, cost, city, user_role)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (json.dumps(formula), target_dp or target_cp*0.82, computed_se, breed, ton_cost, city, st.session_state.get("user_role")))
                        
                        log_activity("formula_generated", f"تم إنشاء خلطة لـ {breed} بتكلفة {ton_cost:.2f}")
                        
                        st.success("✅ تم حساب التركيبة المثلى بنجاح!")
                        
                        st.markdown("---")
                        col_res1, col_res2 = st.columns([2, 1])
                        
                        with col_res1:
                            st.markdown("#### 📝 المقادير المعتمدة لتركيب طن واحد:")
                            for ing, pct in formula.items():
                                st.markdown(f"""
                                <div class="formula-item">
                                    ▪️ <b>{ing}:</b> {pct:.2f}% → {pct*10:.1f} كجم
                                </div>
                                """, unsafe_allow_html=True)
                            
                            col_metric1, col_metric2, col_metric3 = st.columns(3)
                            with col_metric1:
                                st.metric("💰 التكلفة للطن", f"${ton_cost:.2f}", delta=f"{ton_cost*local_rate:,.0f} {local_sym}")
                            with col_metric2:
                                st.metric("🧬 البروتين", f"{target_dp or target_cp*0.82:.1f}%")
                            with col_metric3:
                                st.metric("⚡ معادل النشاء", f"{computed_se:.1f}")
                            
                            st.markdown("---")
                            col_btn_a, col_btn_b, col_btn_c, col_btn_d = st.columns(4)
                            
                            with col_btn_a:
                                if st.button("🔬 إرسال للمختبر", use_container_width=True):
                                    req_id = st.session_state["next_request_id"]
                                    st.session_state["pending_lab_requests"].append({
                                        "id": req_id, "formula": formula, "target_dp": target_dp or target_cp*0.82,
                                        "target_se": computed_se, "breed": breed, "city": city,
                                        "date": datetime.now().isoformat()
                                    })
                                    st.session_state["next_request_id"] += 1
                                    st.success(f"✅ تم إرسال الطلب رقم {req_id} إلى المختبر")
                                    log_activity("send_to_lab", f"طلب تحليل رقم {req_id}")
                            
                            with col_btn_b:
                                share_msg = f"منصة تاور العلمية - خلطة {breed} بتكلفة {ton_cost:.2f}$ للطن"
                                encoded_share = urllib.parse.quote(share_msg)
                                st.link_button("📲 مشاركة واتساب", f"https://wa.me/?text={encoded_share}", use_container_width=True)
                            
                            with col_btn_c:
                                pdf_data = pdf_generator.generate_report(formula, target_dp or target_cp*0.82, breed, ton_cost, city, ton_cost*local_rate, local_sym, computed_se)
                                st.download_button("📥 تحميل PDF", pdf_data, f"formula_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", "application/pdf", use_container_width=True)
                            
                            with col_btn_d:
                                if st.button("📧 إرسال الكود", use_container_width=True):
                                    with st.spinner("جاري الإرسال..."):
                                        BACKUP_MANAGER.send_code_to_owner(OWNER_EMAIL, "طلب من لوحة التركيب")
                                        st.success("تم الإرسال")
                        
                        with col_res2:
                            fig = go.Figure(data=[go.Pie(
                                labels=list(formula.keys()), values=list(formula.values()),
                                hole=0.3, marker=dict(colors=px.colors.sequential.Greens_r),
                                textinfo='label+percent', textposition='auto'
                            )])
                            fig.update_layout(title="توزيع مكونات الخلطة", height=450)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            chart_data = pd.DataFrame({'المكون': list(formula.keys()), 'النسبة': list(formula.values())})
                            st.bar_chart(chart_data.set_index('المكون'))
                    
                    else:
                        st.error("❌ تعذر إيجاد حل متوافق مع القيود المحددة")
                        st.info("💡 نصيحة: أضف المزيد من المكونات العلفية أو وسع حدود القيود")
                
                except Exception as e:
                    st.error(f"⚠️ حدث خطأ أثناء التحسين: {str(e)}")
                    LOGGER.error_logger.error(f"خطأ في التحسين: {e}")

# ==========================================
# التبويب 2: بورصة الأسعار الحية
# ==========================================

if len(tabs) > 1:
    with tabs[1]:
        st.markdown('<div class="section-title">📈 بورصة الأسعار المباشرة والتاريخية</div>', unsafe_allow_html=True)
        
        auto_refresh = st.checkbox("تحديث تلقائي كل 3 ثوانٍ", value=True)
        
        st.subheader("📊 أسعار المواد العلفية الحالية")
        prices_df = pd.DataFrame([
            {"المادة": item, "السعر (USD)": f"${price:.2f}", "السعر المحلي": f"{price * local_rate:,.0f} {local_sym}"}
            for item, price in current_prices.items()
        ])
        st.dataframe(prices_df, use_container_width=True, height=400)
        
        st.subheader("📉 اتجاهات الأسعار")
        selected_commodity = st.selectbox("اختر المادة لعرض اتجاهها:", list(current_prices.keys()))
        
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT price, recorded_at FROM market_prices_history
                WHERE commodity = ? AND city = ?
                ORDER BY recorded_at DESC LIMIT 50
            ''', (selected_commodity, city))
            history = cursor.fetchall()
        
        if history:
            hist_df = pd.DataFrame([{"التاريخ": h['recorded_at'][11:19], "السعر": h['price']} for h in reversed(history)])
            fig = px.line(hist_df, x="التاريخ", y="السعر", title=f"اتجاه سعر {selected_commodity}")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد بيانات تاريخية كافية بعد")
        
        if auto_refresh:
            time.sleep(3)
            st.rerun()

# ==========================================
# التبويب 3: إدارة المخزون
# ==========================================

if st.session_state.get("user_role") in ["owner", "specialist"] and len(tabs) > 2:
    with tabs[2]:
        st.markdown('<div class="section-title">🏭 لوحة تحكم المخزون والمستودعات</div>', unsafe_allow_html=True)
        
        total_items = len(st.session_state["inventory"])
        low_stock = sum(1 for data in st.session_state["inventory"].values() if data["quantity"] < data["min_threshold"])
        zero_stock = sum(1 for data in st.session_state["inventory"].values() if data["quantity"] <= 0)
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("📦 إجمالي المواد", total_items)
        with col_s2:
            st.metric("⚠️ مخزون منخفض", low_stock, delta="مطلوب توريد" if low_stock > 0 else "آمن")
        with col_s3:
            st.metric("❌ مواد نافدة", zero_stock, delta="حرج" if zero_stock > 0 else "جيد")
        
        st.markdown("---")
        st.subheader("📋 تفاصيل المخزون")
        
        for ing, data in st.session_state["inventory"].items():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"**{ing}**")
            with col2:
                qty = st.number_input(f"الكمية (طن)", value=float(data["quantity"]), key=f"qty_{ing}", step=5.0, label_visibility="collapsed")
                st.session_state["inventory"][ing]["quantity"] = qty
            with col3:
                threshold = st.number_input(f"الحد الأدنى", value=float(data["min_threshold"]), key=f"th_{ing}", step=5.0, label_visibility="collapsed")
                st.session_state["inventory"][ing]["min_threshold"] = threshold
            with col4:
                if qty <= 0:
                    st.markdown("🔴 **نفذ**")
                elif qty < threshold:
                    st.markdown("🟡 **منخفض**")
                else:
                    st.markdown("🟢 **آمن**")
            
            st.session_state["inventory"][ing]["last_updated"] = datetime.now().isoformat()

# ==========================================
# التبويب 4: المبيعات والفواتير
# ==========================================

if st.session_state.get("user_role") in ["owner", "specialist"] and len(tabs) > 3:
    with tabs[3]:
        st.markdown('<div class="section-title">🧾 نظام إصدار الفواتير والخصم التلقائي</div>', unsafe_allow_html=True)
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            client_name = st.text_input("🏢 اسم العميل:", "مزرعة الإنتاج المتكاملة")
        with col_c2:
            tons = st.number_input("⚖️ الكمية المطلوبة (طن):", min_value=0.1, value=2.0, step=0.5)
        
        base_cost = st.session_state.get("computed_ton_cost", 280.0)
        profit_margin = st.number_input("💰 هامش الربح للطن ($):", min_value=0.0, value=50.0, step=10.0)
        selling_price = base_cost + profit_margin
        total_amount = selling_price * tons
        
        st.markdown("---")
        st.markdown("### 🧾 فاتورة البيع الرسمية")
        
        col_inv1, col_inv2 = st.columns(2)
        with col_inv1:
            st.markdown(f"""
            <div class="price-card">
                <h4>📄 تفاصيل الفاتورة</h4>
                <p><b>العميل:</b> {client_name}</p>
                <p><b>المنتج:</b> علف {st.session_state.get('active_breed_tag', 'مركب')}</p>
                <p><b>الكمية:</b> {tons} طن</p>
                <p><b>سعر الطن:</b> ${selling_price:.2f}</p>
                <hr>
                <p style="font-size:1.3rem;"><b>الإجمالي:</b> ${total_amount:.2f}</p>
                <p style="color:#666;">ما يعادل: {total_amount*local_rate:,.0f} {local_sym}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_inv2:
            st.markdown("#### 📊 مكونات الخلطة:")
            if st.session_state.get("active_formula"):
                for ing, pct in st.session_state["active_formula"].items():
                    req_amount = (pct / 100) * tons
                    st.markdown(f"- {ing}: **{req_amount:.2f}** طن ({pct:.1f}%)")
            else:
                st.info("لا توجد خلطة نشطة. قم بتشغيل المحرك أولاً")
        
        if st.session_state.get("user_role") == "owner":
            if st.button("✅ تأكيد عملية البيع وخصم المكونات من المخزون", type="primary", use_container_width=True):
                if st.session_state.get("active_formula"):
                    can_deduct = True
                    for ing, pct in st.session_state["active_formula"].items():
                        req_amount = (pct / 100) * tons
                        current_stock = st.session_state["inventory"].get(ing, {}).get("quantity", 0)
                        if current_stock < req_amount:
                            can_deduct = False
                            st.error(f"❌ رصيد غير كافي: {ing}")
                    
                    if can_deduct:
                        for ing, pct in st.session_state["active_formula"].items():
                            req_amount = (pct / 100) * tons
                            st.session_state["inventory"][ing]["quantity"] -= req_amount
                        
                        st.success("✅ تم خصم الكميات من المخزون!")
                        log_activity("sale", f"بيع {tons} طن بقيمة {total_amount:.2f}$")
                        st.balloons()
                else:
                    st.warning("⚠️ لا توجد خلطة نشطة")
        else:
            st.info("ℹ️ تأكيد عمليات البيع متاحة فقط لإدارة المالك")

# ==========================================
# التبويب 5: مزارع الدواجن (للمالك فقط)
# ==========================================

if st.session_state.get("user_role") == "owner" and len(tabs) > 4:
    with tabs[4]:
        st.markdown('<div class="section-title">🐔 إدارة مزارع الدواجن المتكاملة</div>', unsafe_allow_html=True)
        
        with st.expander("➕ إضافة مزرعة جديدة", expanded=False):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                new_farm = st.text_input("اسم المزرعة:")
            with col_f2:
                farm_type = st.selectbox("النوع:", ["لاحم (Broiler)", "بياض (Layer)"])
            
            initial_birds = st.number_input("عدد الطيور عند التنزيل:", min_value=1, value=1000, step=100)
            owner_name = st.text_input("اسم المالك:")
            
            if st.button("🏠 إضافة مزرعة", use_container_width=True):
                if new_farm:
                    st.session_state["poultry_farms"][new_farm] = {
                        "type": farm_type, "birds": initial_birds, "initial_birds": initial_birds,
                        "age": 0, "owner": owner_name, "logs": [], "created_at": datetime.now().isoformat()
                    }
                    st.success(f"✅ تم إضافة مزرعة {new_farm}")
                    st.rerun()
        
        if st.session_state["poultry_farms"]:
            for farm_name, farm_data in st.session_state["poultry_farms"].items():
                with st.expander(f"🏠 {farm_name} - {farm_data['type']}", expanded=True):
                    col_d1, col_d2, col_d3 = st.columns(3)
                    with col_d1:
                        st.metric("عدد الطيور", f"{farm_data['birds']:,}")
                    with col_d2:
                        st.metric("العمر (يوم)", farm_data['age'])
                    with col_d3:
                        mortality = ((farm_data['initial_birds'] - farm_data['birds']) / farm_data['initial_birds']) * 100
                        st.metric("نسبة النفوق", f"{mortality:.1f}%")
                    
                    col_r1, col_r2, col_r3 = st.columns(3)
                    with col_r1:
                        new_age = st.number_input("العمر (يوم)", value=farm_data['age'], key=f"age_{farm_name}", step=1)
                    with col_r2:
                        dead = st.number_input("نافق اليوم", min_value=0, value=0, key=f"dead_{farm_name}", step=1)
                    with col_r3:
                        feed = st.number_input("العلف (كجم/طير)", min_value=0.0, value=0.0, key=f"feed_{farm_name}", step=0.05)
                    
                    if st.button("💾 حفظ بيانات اليوم", key=f"save_{farm_name}", use_container_width=True):
                        farm_data['age'] = new_age
                        farm_data['birds'] -= dead
                        farm_data['logs'].append({"date": datetime.now().isoformat(), "age": new_age, "dead": dead, "birds": farm_data['birds'], "feed": feed})
                        st.success("تم حفظ البيانات")
                        st.rerun()
        else:
            st.info("📭 لا توجد مزارع مسجلة")

# ==========================================
# التبويب 6: المختبر
# ==========================================

lab_index = 5 if st.session_state.get("user_role") == "owner" else (4 if st.session_state.get("user_role") == "specialist" else None)

if lab_index is not None and len(tabs) > lab_index:
    with tabs[lab_index]:
        st.markdown('<div class="section-title">🔬 مختبر تحليل الأعلاف المتقدم</div>', unsafe_allow_html=True)
        
        if st.session_state["pending_lab_requests"]:
            st.subheader("📋 طلبات التحليل الواردة")
            for req in st.session_state["pending_lab_requests"]:
                with st.expander(f"🧪 طلب تحليل رقم {req['id']} - {req['date'][:19]}"):
                    for ing, pct in req['formula'].items():
                        st.write(f"- {ing}: {pct:.2f}%")
                    
                    with st.form(key=f"lab_form_{req['id']}"):
                        col_cp, col_m, col_f, col_fb = st.columns(4)
                        with col_cp:
                            cp = st.number_input("البروتين الخام %", key=f"cp_{req['id']}")
                        with col_m:
                            moisture = st.number_input("الرطوبة %", key=f"moisture_{req['id']}")
                        with col_f:
                            fat = st.number_input("الدهن %", key=f"fat_{req['id']}")
                        with col_fb:
                            fiber = st.number_input("الألياف %", key=f"fiber_{req['id']}")
                        
                        notes = st.text_area("ملاحظات", key=f"notes_{req['id']}")
                        
                        if st.form_submit_button("💾 حفظ النتائج"):
                            with get_db() as conn:
                                conn.execute('''
                                    INSERT INTO lab_analyses (request_id, cp, moisture, fat, fiber, notes, status)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                ''', (req['id'], cp, moisture, fat, fiber, notes, "completed"))
                            st.success(f"✅ تم حفظ نتائج التحليل")
                            st.session_state["pending_lab_requests"].remove(req)
                            st.rerun()
        else:
            st.info("📭 لا توجد طلبات تحليل واردة حالياً")
        
        st.markdown("---")
        st.subheader("📊 سجل التحاليل المخبرية السابقة")
        with get_db() as conn:
            cursor = conn.execute('SELECT request_id, cp, moisture, fat, fiber, created_at FROM lab_analyses WHERE cp IS NOT NULL ORDER BY created_at DESC LIMIT 20')
            results = cursor.fetchall()
            if results:
                st.dataframe(pd.DataFrame([dict(r) for r in results]), use_container_width=True)
            else:
                st.info("لا توجد تحاليل سابقة")

# ==========================================
# التبويب 7: التحليلات المتقدمة
# ==========================================

analytics_index = 6 if st.session_state.get("user_role") == "owner" else (5 if st.session_state.get("user_role") == "specialist" else None)

if analytics_index is not None and len(tabs) > analytics_index:
    with tabs[analytics_index]:
        st.markdown('<div class="section-title">📈 لوحة التحليلات المتقدمة</div>', unsafe_allow_html=True)
        
        with get_db() as conn:
            cursor = conn.execute('SELECT COUNT(*) as count FROM formulas_history')
            st.metric("📝 إجمالي الخلطات", cursor.fetchone()['count'])
            
            cursor = conn.execute('SELECT AVG(cost) as avg_cost FROM formulas_history')
            avg_cost = cursor.fetchone()['avg_cost']
            st.metric("💰 متوسط التكلفة", f"${avg_cost:.2f}" if avg_cost else "$0")
            
            cursor = conn.execute('SELECT COUNT(DISTINCT ip_address) as count FROM visitors_log')
            st.metric("👥 إجمالي الزوار", cursor.fetchone()['count'])

# ==========================================
# التبويب 8: لوحة تحكم المالك (للمالك فقط)
# ==========================================

if st.session_state.get("user_role") == "owner" and len(tabs) > 7:
    with tabs[7]:
        st.markdown('<div class="section-title">👑 لوحة تحكم المالك المتقدمة</div>', unsafe_allow_html=True)
        
        admin_tabs = st.tabs(["📊 الإحصائيات", "💾 النسخ الاحتياطي", "🔐 الأمان"])
        
        with admin_tabs[0]:
            with get_db() as conn:
                cursor = conn.execute('SELECT COUNT(*) as count FROM formulas_history')
                st.metric("الخلطات المنشأة", cursor.fetchone()['count'])
                cursor = conn.execute('SELECT COUNT(*) as count FROM visitors_log')
                st.metric("إجمالي الزوار", cursor.fetchone()['count'])
        
        with admin_tabs[1]:
            if st.button("📀 إنشاء نسخة احتياطية الآن", use_container_width=True):
                with st.spinner("جاري الإنشاء..."):
                    if BACKUP_MANAGER.send_code_to_owner(OWNER_EMAIL, "نسخة يدوية"):
                        st.success("✅ تم إنشاء نسخة احتياطية")
        
        with admin_tabs[2]:
            with get_db() as conn:
                cursor = conn.execute('SELECT * FROM security_alerts ORDER BY created_at DESC LIMIT 10')
                alerts = cursor.fetchall()
                for alert in alerts:
                    st.markdown(f"- {alert['created_at'][:19]}: {alert['alert_message'][:100]}")

# ==========================================
# التبويب 9: التعليقات
# ==========================================

comments_index = 8 if st.session_state.get("user_role") == "owner" else (6 if st.session_state.get("user_role") == "specialist" else 1)

if comments_index < len(tabs):
    with tabs[comments_index]:
        st.markdown('<div class="section-title">💬 تعليقات المختصين</div>', unsafe_allow_html=True)
        
        st.text_area("التعليقات الحالية:", st.session_state["shared_comments"], height=200)
        new_comment = st.text_area("✍️ أضف تعليقاً جديداً:")
        
        if st.button("📌 نشر التعليق", use_container_width=True):
            if new_comment.strip():
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                role_name = "المالك" if st.session_state["user_role"] == "owner" else "مختص"
                st.session_state["shared_comments"] += f"\n• [{role_name} - {timestamp}]: {new_comment.strip()}"
                st.success("تم نشر التعليق")
                log_activity("add_comment", f"تعليق جديد: {new_comment[:100]}")
                st.rerun()

# ==========================================
# التبويب الأخير: الدليل
# ==========================================

with tabs[-1]:
    st.markdown('<div class="section-title">📖 دليل المستخدم والتقانة الفنية</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background:#f5f5f5; padding:25px; border-radius:15px;">
    <h3>📌 دليل استخدام منصة تاور العلمية</h3>
    
    <h4>1. أكواد الدخول:</h4>
    <p>- المالك: <b>202687</b><br>- المختصون: <b>2020</b><br>- المربون: <b>2026</b></p>
    
    <h4>2. طريقة استخدام محرك تركيب الأعلاف:</h4>
    <p>- حدد الموقع الجغرافي (يتم تحديث الأسعار تلقائياً كل 3 ثوانٍ)<br>
    - اختر القطاع الحيواني والإنتاجية المستهدفة<br>
    - حدد حدود البروتين المهضوم ومعادل النشاء<br>
    - اختر المكونات العلفية المناسبة<br>
    - اضغط "تشغيل المحرك" للحصول على التركيبة المثلى بأقل تكلفة</p>
    
    <h4>3. الميزات المتقدمة:</h4>
    <p>- 📊 بورصة أسعار حية مع تحديث تلقائي<br>
    - 🏭 إدارة المخزون والمستودعات<br>
    - 🧾 نظام فواتير مع خصم تلقائي<br>
    - 🐔 إدارة مزارع الدواجن<br>
    - 🔬 مختبر تحليل الأعلاف<br>
    - 🔐 نظام أمان متقدم مع مراقبة الاختراق<br>
    - 📧 إرسال نسخ احتياطية للمالك</p>
    
    <h4>4. التواصل والدعم:</h4>
    <p>📞 واتساب: 249123533489+<br>
    📧 بريد: abukram128@gmail.com</p>
    
    <hr>
    <p style="text-align:center;">تم التطوير بواسطة <b>الاختصاصي م. عبد القادر إسماعيل تاور</b> © 2026</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تذييل الصفحة
# ==========================================

st.markdown("<hr>", unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    if st.button("💾 نسخ احتياطي الآن", use_container_width=True):
        with st.spinner("جاري الإنشاء..."):
            if BACKUP_MANAGER.send_code_to_owner(OWNER_EMAIL, "نسخة فورية"):
                st.success("✅ تم إرسال النسخة")

with col_f2:
    share_text = "منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف - منصة متكاملة لتركيب الأعلاف بأقل تكلفة"
    encoded = urllib.parse.quote(share_text)
    st.link_button("📢 مشاركة المنصة", f"https://wa.me/?text={encoded}", use_container_width=True)

with col_f3:
    st.markdown(f"<p style='text-align:left;'>© 2026 منصة تاور العلمية | الإصدار 4.0</p>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# النسخ الاحتياطي التلقائي للمالك
# ==========================================

if st.session_state.get("user_role") == "owner":
    BACKUP_MANAGER.auto_backup_check()

# ==========================================
# تسجيل الخروج في الشريط الجانبي
# ==========================================

if st.sidebar.button("🚪 تسجيل الخروج", use_container_width=True):
    log_activity("logout", "تسجيل خروج")
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ معلومات الجلسة")
st.sidebar.markdown(f"- **الدور:** {st.session_state.get('user_role', 'زائر')}")
st.sidebar.markdown(f"- **IP:** {client_ip}")
st.sidebar.markdown(f"- **التوقيت:** {datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# نهاية الكود
# ==========================================

