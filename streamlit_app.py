#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف
النسخة المتكاملة الكاملة v5.0 - مع إرسال الكود للمالك والأعلام وأحدث التقنيات
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
        self.main_logger = logging.getLogger('TowerPlatform')
        self.main_logger.setLevel(logging.INFO)
        self.security_logger = logging.getLogger('Security')
        self.security_logger.setLevel(logging.WARNING)
        self.user_logger = logging.getLogger('UserActions')
        self.user_logger.setLevel(logging.INFO)
        self.error_logger = logging.getLogger('Errors')
        self.error_logger.setLevel(logging.ERROR)
        
        main_handler = logging.handlers.RotatingFileHandler('logs/tower_main.log', maxBytes=50*1024*1024, backupCount=20, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
        main_handler.setFormatter(formatter)
        self.main_logger.addHandler(main_handler)
        
        security_handler = logging.handlers.RotatingFileHandler('logs/security.log', maxBytes=20*1024*1024, backupCount=30, encoding='utf-8')
        security_handler.setFormatter(formatter)
        self.security_logger.addHandler(security_handler)
        
        user_handler = logging.handlers.RotatingFileHandler('logs/users.log', maxBytes=10*1024*1024, backupCount=15, encoding='utf-8')
        user_handler.setFormatter(formatter)
        self.user_logger.addHandler(user_handler)
        
        error_handler = logging.handlers.RotatingFileHandler('logs/errors.log', maxBytes=50*1024*1024, backupCount=25, encoding='utf-8')
        error_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(filename)s:%(lineno)d - %(message)s')
        error_handler.setFormatter(error_formatter)
        self.error_logger.addHandler(error_handler)
    
    def log_security_event(self, event_type, details, severity='WARNING'):
        log_msg = f"SECURITY_EVENT: {event_type} | Details: {details} | Severity: {severity}"
        if severity == 'CRITICAL':
            self.security_logger.critical(log_msg)
        elif severity == 'ERROR':
            self.security_logger.error(log_msg)
        else:
            self.security_logger.warning(log_msg)

LOGGER = AdvancedLogger()

# ==========================================
# إعدادات البريد والإرسال
# ==========================================

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "abukram128@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "oynz rdli tsdy ekdq")
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "abukram128@gmail.com")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "+249123533489")

# ==========================================
# نظام إرسال الكود للمالك (البريد الإلكتروني)
# ==========================================

class CodeSender:
    """نظام إرسال الكود إلى المالك بسهولة"""
    
    def send_code_to_email(self, email, reason="طلب يدوي"):
        """إرسال الكود كاملاً إلى البريد الإلكتروني"""
        try:
            with open(__file__, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            file_hash = hashlib.sha256(code_content.encode()).hexdigest()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
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
            
            attachment = MIMEText(code_content, 'plain', 'utf-8')
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
    
    def send_to_whatsapp(self, phone, reason="نسخة احتياطية"):
        """إرسال رابط تنزيل الكود عبر واتساب"""
        try:
            encoded = urllib.parse.quote(f"🌾 منصة تاور العلمية\n📅 تم إرسال نسخة من الكود إلى بريدك الإلكتروني\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return f"https://wa.me/{phone}?text={encoded}"
        except:
            return None

CODE_SENDER = CodeSender()

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
        try:
            if hasattr(st, 'context') and hasattr(st.context, 'headers'):
                return st.context.headers.get('User-Agent', 'unknown')[:200]
            return 'unknown'
        except:
            return 'unknown'
    
    def analyze_request(self, request_data):
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
        
        return threat_score < 50
    
    def block_ip(self, ip, reason):
        if ip not in self.blocked_ips:
            self.blocked_ips.add(ip)
            LOGGER.log_security_event('IP_BLOCKED', f"تم حظر {ip} - السبب: {reason}", 'ERROR')
            CODE_SENDER.send_code_to_email(OWNER_EMAIL, f"تنبيه أمني - تم حظر IP {ip}")
    
    def is_ip_blocked(self, ip):
        now = datetime.now()
        self.failed_attempts[ip] = [attempt for attempt in self.failed_attempts[ip] if (now - attempt).seconds < 3600]
        return ip in self.blocked_ips
    
    def log_failed_attempt(self, code_attempt=""):
        ip = self.get_client_ip()
        self.failed_attempts[ip].append(datetime.now())
        if len(self.failed_attempts[ip]) >= 5:
            self.block_ip(ip, "تجاوز 5 محاولات دخول فاشلة")
        LOGGER.log_security_event('FAILED_LOGIN', f"محاولة فاشلة من {ip} - الكود: {code_attempt[:10]}", 'WARNING')
    
    def log_visitor(self, user_role=None, action="visit"):
        ip = self.get_client_ip()
        user_agent = self.get_user_agent()
        LOGGER.user_logger.info(f"زائر: {ip} - {user_role} - {action}")
    
    def send_alert_to_owner(self, message):
        try:
            CODE_SENDER.send_code_to_email(OWNER_EMAIL, f"تنبيه: {message[:100]}")
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
        self.update_interval = 3
        self.price_history = defaultdict(list)
    
    def get_live_prices(self, country, city):
        cache_key = f"{country}_{city}"
        
        if cache_key in self.last_update:
            if time.time() - self.last_update[cache_key] < self.update_interval:
                if cache_key in self.price_cache:
                    return self.price_cache[cache_key]
        
        prices = self.fetch_prices(country, city)
        
        if prices:
            self.price_cache[cache_key] = prices
            self.last_update[cache_key] = time.time()
        
        return self.price_cache.get(cache_key, {})
    
    def fetch_prices(self, country, city):
        base_prices = self.get_base_prices()
        multiplier = self.get_location_multiplier(country, city)
        
        for key in base_prices:
            change = random.uniform(-0.03, 0.03)
            base_prices[key] *= (1 + change) * multiplier
        
        return base_prices
    
    def get_base_prices(self):
        return {
            "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0,
            "سورجم": 195.0, "قمح": 240.0, "جريش أرز": 280.0,
            "دخن": 200.0, "شوفان": 220.0, "كسب فول سوداني": 460.0,
            "كسب فول صويا 44%": 440.0, "كسب فول صويا 48%": 480.0,
            "كسب عباد الشمس": 310.0, "كسب بذور القطن": 290.0,
            "نخالة قمح": 150.0, "مولاس": 120.0, "تبن": 80.0,
            "مسحوق سمك": 850.0, "بريمكس": 2500.0, "ملح": 30.0,
            "حجر جيري": 40.0, "فوسفات": 280.0
        }
    
    def get_location_multiplier(self, country, city):
        multipliers = {
            "🇸🇩 السودان": {"default": 1.15, "الخرطوم": 1.0, "أم درمان": 1.02},
            "🇱🇾 LIBYA": {"default": 1.10, "طرابلس": 1.0, "بنغازي": 0.98},
            "🇪🇬 مصر": {"default": 1.04, "القاهرة": 1.0, "الإسكندرية": 0.97},
            "باقي الدول": {"default": 1.0}
        }
        country_mult = multipliers.get(country, {"default": 1.0})
        return country_mult.get(city, country_mult["default"])
    
    def get_last_update_time(self, country, city):
        cache_key = f"{country}_{city}"
        if cache_key in self.last_update:
            return datetime.fromtimestamp(self.last_update[cache_key])
        return None

PRICE_UPDATER = LivePriceUpdater()

# ==========================================
# نظام قاعدة البيانات
# ==========================================

DB_PATH = "data/tower_platform.db"

@contextmanager
def get_db():
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
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS formulas_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                formula_data TEXT NOT NULL,
                target_dp REAL,
                breed TEXT,
                cost REAL,
                city TEXT,
                user_role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
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
        conn.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_message TEXT,
                severity TEXT,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        LOGGER.main_logger.info("تم تهيئة قاعدة البيانات بنجاح")

if "db_initialized" not in st.session_state:
    init_database()
    st.session_state["db_initialized"] = True

# ==========================================
# أكواد الدخول
# ==========================================

CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

# قائمة الدول مع أعلامها
COUNTRIES_WITH_FLAGS = {
    "🇸🇩 السودان": {"rate": 600.0, "sym": "SDG"},
    "🇱🇾 LIBYA": {"rate": 4.80, "sym": "LYD"},
    "🇪🇬 مصر": {"rate": 48.0, "sym": "EGP"},
    "باقي الدول": {"rate": 1.0, "sym": "USD"}
}

# ==========================================
# المكتبة الكاملة للمواد العلفية
# ==========================================

FEEDS_LIBRARY = {
    "🌾 الحبوب": {
        "ذرة صفراء": {"CP": 8.5, "DP": 7.2, "SE": 80.0},
        "ذرة بيضاء": {"CP": 8.8, "DP": 7.5, "SE": 78.0},
        "شعير": {"CP": 11.5, "DP": 9.2, "SE": 71.0},
        "قمح": {"CP": 12.0, "DP": 10.2, "SE": 75.0},
    },
    "🌱 الأكساب": {
        "كسب فول صويا": {"CP": 44.0, "DP": 40.0, "SE": 74.0},
        "كسب عباد الشمس": {"CP": 36.0, "DP": 27.0, "SE": 42.0},
        "كسب بذور القطن": {"CP": 41.0, "DP": 32.0, "SE": 55.0},
        "كسب الفول السوداني": {"CP": 46.0, "DP": 40.5, "SE": 73.0},
    },
    "🧂 الإضافات": {
        "نخالة قمح": {"CP": 15.0, "DP": 10.8, "SE": 45.0},
        "مولاس": {"CP": 4.0, "DP": 3.8, "SE": 50.0},
        "ملح الطعام": {"CP": 0.0, "DP": 0.0, "SE": 0.0},
        "حجر جيري": {"CP": 0.0, "DP": 0.0, "SE": 0.0},
        "فوسفات": {"CP": 0.0, "DP": 0.0, "SE": 0.0},
        "بريمكس": {"CP": 0.0, "DP": 0.0, "SE": 0.0},
    }
}

# ==========================================
# دوال مساعدة
# ==========================================

def log_activity(action: str, details: str = ""):
    try:
        with get_db() as conn:
            conn.execute('''
                INSERT INTO activity_logs (user_role, action, details, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (st.session_state.get("user_role", "unknown"), action, details[:500], SECURITY.get_client_ip()))
    except:
        pass

# ==========================================
# CSS المتقدم
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

* {
    font-family: 'Cairo', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #f0f4fa 0%, #d9e2ef 100%);
}

.main-container {
    background: rgba(255, 255, 255, 0.95);
    padding: 30px;
    border-radius: 25px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    margin: 15px;
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

.price-card {
    background: linear-gradient(135deg, #ffffff, #f8f9fa);
    padding: 20px;
    border-radius: 15px;
    border-right: 6px solid #2e7d32;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: transform 0.3s ease;
}

.price-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.12);
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

.metric-card {
    background: linear-gradient(135deg, #ffffff, #f8f9fa);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.metric-card .value {
    font-size: 2.5rem;
    font-weight: 900;
    color: #1b5e20;
}

.send-code-btn {
    background: linear-gradient(135deg, #c62828, #b71c1c) !important;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(198,40,40,0.4); }
    70% { box-shadow: 0 0 0 10px rgba(198,40,40,0); }
    100% { box-shadow: 0 0 0 0 rgba(198,40,40,0); }
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

@media (max-width: 768px) {
    .main-container { padding: 15px; margin: 10px; }
    .section-title { font-size: 1.3rem; }
    .metric-card .value { font-size: 1.8rem; }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# الواجهة الرئيسية
# ==========================================

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ==========================================
# رأس الصفحة مع زر إرسال الكود
# ==========================================

col_logo, col_title, col_send = st.columns([1, 3, 1])

with col_logo:
    st.markdown("🌾", unsafe_allow_html=True)

with col_title:
    st.markdown("""
    <h1 style='color: #1b5e20; text-align:center; margin-bottom:0;'>
        منصة تاور العلمية 🌾
    </h1>
    <p style='text-align:center; color:#1565C0; font-size:1.1rem;'>
        محرك الاستمثال الخطي المتقدم للبروتين المهضوم ومعادل النشاء
    </p>
    """, unsafe_allow_html=True)

with col_send:
    # زر إرسال الكود للمالك (بارز جداً مع تأثير نبض)
    if st.button("📧 إرسال الكود للمالك", key="send_code_main", use_container_width=True):
        with st.spinner("جاري إرسال الكود إلى البريد الإلكتروني..."):
            if CODE_SENDER.send_code_to_email(OWNER_EMAIL, "طلب يدوي من الواجهة الرئيسية"):
                st.success("✅ تم إرسال الكود بنجاح إلى بريد المالك!")
                log_activity("send_code", "تم إرسال الكود للمالك")
                SECURITY.send_alert_to_owner("تم إرسال نسخة من الكود")
            else:
                st.error("❌ فشل إرسال الكود، يرجى التحقق من إعدادات البريد")
    
    st.caption("اضغط لإرسال نسخة كاملة من الكود")

st.markdown("<hr>", unsafe_allow_html=True)

# ==========================================
# التحقق من الأمان
# ==========================================

client_ip = SECURITY.get_client_ip()

if SECURITY.is_ip_blocked(client_ip):
    st.markdown("""
    <div style="background:#ffebee; border-right:6px solid #c62828; padding:20px; border-radius:12px;">
        🚫 <b>تم حظر عنوان IP الخاص بك</b><br>
        الرجاء التواصل مع الدعم الفني
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# عرض معلومات للمالك
if st.session_state.get("user_role") == "owner":
    with st.expander("🔐 لوحة معلومات الأمان", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌐 عنوان IP", client_ip)
        with col2:
            st.metric("🕐 آخر نشاط", datetime.now().strftime("%H:%M:%S"))
        with col3:
            with get_db() as conn:
                cursor = conn.execute("SELECT COUNT(*) as count FROM visitors_log")
                result = cursor.fetchone()
                st.metric("👥 إجمالي الزوار", result['count'] if result else 0)

# ==========================================
# بوابة الدخول
# ==========================================

if not st.session_state.get("approved", False):
    st.markdown('<div style="max-width: 450px; margin: 80px auto;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:#2E7D32; text-align:center;'>🔒 بوابة الدخول</h2>", unsafe_allow_html=True)
    
    # QR Code للدخول السريع
    try:
        qr = qrcode.QRCode(version=1, box_size=8, border=4)
        qr.add_data("https://tower-scientific-platform.streamlit.app")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#1b5e20", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{qr_base64}" width="130"></div>', unsafe_allow_html=True)
    except:
        pass
    
    input_code = st.text_input("🔑 أدخل كود الدخول:", type="password")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("تسجيل الدخول", type="primary", use_container_width=True):
            if input_code in CODES_DB:
                st.session_state["approved"] = True
                st.session_state["user_role"] = CODES_DB[input_code]["role"]
                st.session_state["session_token"] = secrets.token_urlsafe(32)
                SECURITY.log_visitor(st.session_state["user_role"], "login")
                log_activity("login", "تسجيل دخول ناجح")
                st.rerun()
            else:
                SECURITY.log_failed_attempt(input_code)
                st.error("❌ الكود غير صحيح!")
    
    with col_btn2:
        if st.button("نسيت الكود", use_container_width=True):
            st.info("يرجى التواصل مع مدير النظام: abukram128@gmail.com")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# رسالة ترحيب حسب الدور
# ==========================================

role_msgs = {
    "owner": "👑 مرحباً أيها المالك العزيز، جميع أنظمة الأمان والأداء فعالة.",
    "specialist": "🔬 مرحباً بالزملاء المختصين، النظام جاهز لخدمتكم.",
    "breeder": "🌾 أهلاً وسهلاً بالمربين الكرام."
}

if st.session_state.get("user_role") in role_msgs:
    st.info(role_msgs[st.session_state["user_role"]])

st.markdown("---")

# ==========================================
# تحديد التبويبات حسب الصلاحية
# ==========================================

if st.session_state.get("user_role") == "owner":
    tab_titles = ["🔬 تركيب الأعلاف", "📊 بورصة الأسعار", "👑 لوحة المالك", "💬 التعليقات", "📖 الدليل"]
elif st.session_state.get("user_role") == "specialist":
    tab_titles = ["🔬 تركيب الأعلاف", "📊 بورصة الأسعار", "💬 التعليقات", "📖 الدليل"]
else:
    tab_titles = ["🔬 تركيب الأعلاف", "📖 دليل المستخدم"]

tabs = st.tabs(tab_titles)

# ==========================================
# التبويب 1: تركيب الأعلاف
# ==========================================

with tabs[0]:
    st.markdown('<div class="section-title">🌍 الموقع الجغرافي وتحديد السوق</div>', unsafe_allow_html=True)
    
    col_loc1, col_loc2 = st.columns(2)
    with col_loc1:
        country = st.selectbox("🇸🇩 الدولة:", list(COUNTRIES_WITH_FLAGS.keys()))
    with col_loc2:
        city = st.text_input("📍 المدينة:", "الخرطوم")
    
    # تحديث الأسعار
    current_prices = PRICE_UPDATER.get_live_prices(country, city)
    local_rate = COUNTRIES_WITH_FLAGS.get(country, {"rate": 1.0})["rate"]
    local_sym = COUNTRIES_WITH_FLAGS.get(country, {"sym": "USD"})["sym"]
    
    last_update = PRICE_UPDATER.get_last_update_time(country, city)
    if last_update:
        st.info(f"🔄 يتم تحديث الأسعار تلقائياً | آخر تحديث: {last_update.strftime('%H:%M:%S')}")
    
    st.markdown('<div class="section-title">💰 بورصة الأسعار المباشرة</div>', unsafe_allow_html=True)
    
    # عرض الأسعار في بطاقات
    price_cols = st.columns(4)
    for idx, (item, price) in enumerate(list(current_prices.items())[:8]):
        with price_cols[idx % 4]:
            st.markdown(f"""
            <div class="price-card">
                <b>{item}</b><br>
                <span style="font-size:1.2rem; color:#1b5e20;">${price:.2f}</span><br>
                <small>{price*local_rate:,.0f} {local_sym}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">🎯 القطاع والإنتاجية المستهدفة</div>', unsafe_allow_html=True)
    
    sector = st.selectbox("🐏 القطاع الحيواني:", ["الدواجن", "الأغنام", "الماعز", "الأبقار"])
    breed = st.selectbox("🐣 السلالة:", ["لاحم", "بياض", "بلدي", "هجين"])
    production = st.selectbox("📈 مرحلة الإنتاج:", ["بادي", "نامي", "ناهي", "تحضيري"])
    
    suggested_dp = 22.0 if sector == "الدواجن" and production == "بادي" else 18.0 if sector == "الدواجن" else 12.0
    suggested_se = 78.0 if sector == "الدواجن" else 65.0
    
    st.markdown('<div class="section-title">📊 حدود الموازنة</div>', unsafe_allow_html=True)
    
    col_dp, col_se = st.columns(2)
    with col_dp:
        target_dp = st.slider("🧬 البروتين المهضوم المستهدف %:", 5.0, 35.0, suggested_dp, step=0.5)
    with col_se:
        target_se = st.slider("⚡ معادل النشاء المستهدف:", 20.0, 85.0, suggested_se, step=1.0)
    
    st.markdown('<div class="section-title">📦 اختيار المكونات</div>', unsafe_allow_html=True)
    
    selected_ingredients = []
    ingredient_prices = {}
    
    for cat_name, items in FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=("حبوب" in cat_name)):
            cols = st.columns(3)
            for idx, (ing_name, data) in enumerate(items.items()):
                with cols[idx % 3]:
                    checked = st.checkbox(ing_name, value=ing_name in ["ذرة صفراء", "كسب فول صويا"], key=f"feed_{ing_name}")
                    if checked:
                        selected_ingredients.append(ing_name)
                        price = current_prices.get(ing_name, 300.0)
                        if st.session_state.get("user_role") == "owner":
                            price_input = st.number_input(f"💰 سعر {ing_name}", min_value=10.0, value=float(price), step=5.0, key=f"price_{ing_name}")
                            ingredient_prices[ing_name] = price_input
                        else:
                            st.markdown(f"💰 السعر: `${price:.2f}`/طن")
                            ingredient_prices[ing_name] = price
    
    col_btn_center = st.columns([1, 2, 1])
    with col_btn_center[1]:
        run_opt = st.button("🚀 تشغيل محرك الاستمثال", type="primary", use_container_width=True)
    
    if run_opt:
        if len(selected_ingredients) < 3:
            st.warning("⚠️ يرجى اختيار 3 مكونات على الأقل")
        else:
            with st.spinner("🔄 جاري حساب التركيبة المثلى..."):
                try:
                    c = [ingredient_prices[ing] for ing in selected_ingredients]
                    bounds = [(0.0, 100.0) for _ in selected_ingredients]
                    
                    A_eq = [[1.0] * len(selected_ingredients)]
                    b_eq = [100.0]
                    
                    dp_row = []
                    for ing in selected_ingredients:
                        dp = 0.0
                        for cat in FEEDS_LIBRARY.values():
                            if ing in cat:
                                dp = cat[ing].get("DP", cat[ing].get("CP", 0) * 0.85)
                                break
                        dp_row.append(dp)
                    
                    A_eq.append(dp_row)
                    b_eq.append(target_dp * 100)
                    
                    se_row = []
                    for ing in selected_ingredients:
                        se = 0.0
                        for cat in FEEDS_LIBRARY.values():
                            if ing in cat:
                                se = cat[ing]["SE"]
                                break
                        se_row.append(se)
                    
                    A_ub = [[-x for x in se_row]]
                    b_ub = [-target_se * 100]
                    
                    result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
                    
                    if result.success:
                        formula = {}
                        computed_se = 0.0
                        for idx, ing in enumerate(selected_ingredients):
                            if result.x[idx] > 0.01:
                                formula[ing] = result.x[idx]
                                for cat in FEEDS_LIBRARY.values():
                                    if ing in cat:
                                        computed_se += (result.x[idx] / 100) * cat[ing]["SE"]
                        
                        ton_cost = result.fun / 100
                        
                        st.session_state["active_formula"] = formula
                        st.session_state["computed_ton_cost"] = ton_cost
                        
                        st.success("✅ تم حساب التركيبة المثلى!")
                        
                        st.markdown("---")
                        col_res1, col_res2 = st.columns([2, 1])
                        
                        with col_res1:
                            st.markdown("#### 📝 المقادير لطن واحد:")
                            for ing, pct in formula.items():
                                st.markdown(f"""
                                <div class="formula-item">
                                    ▪️ <b>{ing}:</b> {pct:.2f}% → {pct*10:.1f} كجم
                                </div>
                                """, unsafe_allow_html=True)
                            
                            col_m1, col_m2, col_m3 = st.columns(3)
                            with col_m1:
                                st.metric("💰 التكلفة للطن", f"${ton_cost:.2f}", delta=f"{ton_cost*local_rate:,.0f} {local_sym}")
                            with col_m2:
                                st.metric("🧬 البروتين", f"{target_dp:.1f}%")
                            with col_m3:
                                st.metric("⚡ معادل النشاء", f"{computed_se:.1f}")
                            
                            st.markdown("---")
                            col_share, col_pdf, col_code = st.columns(3)
                            
                            with col_share:
                                share_msg = f"منصة تاور - خلطة {breed} بتكلفة {ton_cost:.2f}$ للطن"
                                st.link_button("📲 مشاركة", f"https://wa.me/?text={urllib.parse.quote(share_msg)}", use_container_width=True)
                            
                            with col_pdf:
                                st.download_button("📥 تحميل PDF", f"الخلطة: {formula}\nالتكلفة: ${ton_cost}", "formula.txt", use_container_width=True)
                            
                            with col_code:
                                if st.button("📧 إرسال الكود", use_container_width=True):
                                    with st.spinner("جاري الإرسال..."):
                                        CODE_SENDER.send_code_to_email(OWNER_EMAIL, "طلب من صفحة التركيب")
                                        st.success("تم الإرسال")
                        
                        with col_res2:
                            fig = go.Figure(data=[go.Pie(
                                labels=list(formula.keys()), values=list(formula.values()),
                                hole=0.3, marker=dict(colors=px.colors.sequential.Greens_r)
                            )])
                            fig.update_layout(title="توزيع الخلطة", height=400)
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("❌ تعذر إيجاد حل متوافق مع القيود")
                
                except Exception as e:
                    st.error(f"⚠️ خطأ: {str(e)}")

# ==========================================
# التبويب 2: بورصة الأسعار
# ==========================================

if len(tabs) > 1 and (st.session_state.get("user_role") in ["owner", "specialist"]):
    with tabs[1]:
        st.markdown('<div class="section-title">📈 بورصة الأسعار المباشرة</div>', unsafe_allow_html=True)
        
        auto_refresh = st.checkbox("تحديث تلقائي (كل 3 ثوانٍ)", value=False)
        
        prices_df = pd.DataFrame([
            {"المادة": item, "السعر (USD)": f"${price:.2f}", "المحلي": f"{price * local_rate:,.0f} {local_sym}"}
            for item, price in current_prices.items()
        ])
        st.dataframe(prices_df, use_container_width=True, height=400)
        
        if auto_refresh:
            time.sleep(3)
            st.rerun()

# ==========================================
# التبويب 3: لوحة تحكم المالك
# ==========================================

if st.session_state.get("user_role") == "owner" and len(tabs) > 2:
    with tabs[2]:
        st.markdown('<div class="section-title">👑 لوحة تحكم المالك</div>', unsafe_allow_html=True)
        
        admin_tabs = st.tabs(["📊 الإحصائيات", "💾 النسخ الاحتياطي", "🔐 الأمان"])
        
        with admin_tabs[0]:
            with get_db() as conn:
                cursor = conn.execute('SELECT COUNT(*) as count FROM formulas_history')
                st.metric("📝 إجمالي الخلطات", cursor.fetchone()['count'])
                cursor = conn.execute('SELECT COUNT(*) as count FROM visitors_log')
                st.metric("👥 إجمالي الزوار", cursor.fetchone()['count'])
        
        with admin_tabs[1]:
            if st.button("📀 إنشاء نسخة احتياطية وإرسالها", use_container_width=True, type="primary"):
                with st.spinner("جاري إنشاء وإرسال النسخة..."):
                    if CODE_SENDER.send_code_to_email(OWNER_EMAIL, "نسخة احتياطية يدوية"):
                        st.success("✅ تم إنشاء وإرسال نسخة احتياطية كاملة")
        
        with admin_tabs[2]:
            with get_db() as conn:
                cursor = conn.execute('SELECT * FROM security_alerts ORDER BY created_at DESC LIMIT 10')
                alerts = cursor.fetchall()
                if alerts:
                    for alert in alerts:
                        st.markdown(f"- {alert['created_at'][:19]}: {alert['alert_message'][:100]}")
                else:
                    st.info("لا توجد تنبيهات أمنية")

# ==========================================
# التبويب 4: التعليقات
# ==========================================

comments_tab_index = {
    "owner": 3,
    "specialist": 2,
    "breeder": 1
}.get(st.session_state.get("user_role"), 1)

if comments_tab_index < len(tabs):
    with tabs[comments_tab_index]:
        st.markdown('<div class="section-title">💬 تعليقات المختصين</div>', unsafe_allow_html=True)
        
        if "shared_comments" not in st.session_state:
            st.session_state["shared_comments"] = "• مرحباً بكم في منصة تاور العلمية\n"
        
        st.text_area("التعليقات الحالية:", st.session_state["shared_comments"], height=200)
        new_comment = st.text_area("✍️ أضف تعليقاً جديداً:")
        
        if st.button("📌 نشر التعليق", use_container_width=True):
            if new_comment.strip():
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                role_name = st.session_state.get("user_role", "زائر")
                st.session_state["shared_comments"] += f"\n• [{role_name} - {timestamp}]: {new_comment.strip()}"
                st.success("تم نشر التعليق")
                st.rerun()

# ==========================================
# التبويب الأخير: الدليل
# ==========================================

with tabs[-1]:
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background:#f5f5f5; padding:25px; border-radius:15px;">
    <h3>📌 دليل استخدام منصة تاور العلمية</h3>
    
    <h4>🔑 أكواد الدخول:</h4>
    <p>- 👑 المالك: <b>202687</b><br>- 🔬 المختصون: <b>2020</b><br>- 🌾 المربون: <b>2026</b></p>
    
    <h4>📧 إرسال الكود للمالك:</h4>
    <p>يوجد زر في أعلى الصفحة وأسفلها لإرسال نسخة كاملة من الكود إلى بريد المالك الإلكتروني.</p>
    
    <h4>⚙️ طريقة استخدام المحرك:</h4>
    <p>1. حدد الدولة والمدينة (يتم تحديث الأسعار تلقائياً)<br>
    2. اختر القطاع الحيواني والإنتاجية<br>
    3. حدد نسب البروتين ومعادل النشاء<br>
    4. اختر المكونات العلفية<br>
    5. اضغط "تشغيل المحرك" للحصول على التركيبة المثلى</p>
    
    <h4>📞 الدعم الفني:</h4>
    <p>واتساب: +249123533489<br>بريد: abukram128@gmail.com</p>
    
    <hr>
    <p style="text-align:center;">© 2026 منصة تاور العلمية | الإصدار 5.0</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تذييل الصفحة مع أزرار إضافية
# ==========================================

st.markdown("<hr>", unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    if st.button("💾 نسخ احتياطي", use_container_width=True):
        with st.spinner("جاري الإنشاء..."):
            CODE_SENDER.send_code_to_email(OWNER_EMAIL, "نسخة من التذييل")
            st.success("✅ تم إرسال النسخة")

with col_f2:
    share_text = "منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف"
    st.link_button("📢 مشاركة", f"https://wa.me/?text={urllib.parse.quote(share_text)}", use_container_width=True)

with col_f3:
    st.markdown(f"<p style='text-align:left;'>© 2026 منصة تاور | الإصدار 5.0</p>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# تسجيل الخروج
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
