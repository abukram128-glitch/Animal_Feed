#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف
النسخة المتكاملة الكاملة v6.0 - أكثر من 2200 سطر
مع شريط القياس المتقدم والمختبر المتكامل وأحدث التقنيات
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
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression

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

folders = ["logs", "backups", "data", "temp", "visitors", "code_backups", "reports", "exports", "charts", "models", "cache", "lab_results", "formulas_archive", "price_history"]
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
# نظام إرسال الكود للمالك
# ==========================================

class CodeSender:
    """نظام إرسال الكود إلى المالك بسهولة"""
    
    def send_code_to_email(self, email, reason="طلب يدوي"):
        try:
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            with open(__file__, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            file_hash = hashlib.sha256(code_content.encode()).hexdigest()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
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
    
    def auto_backup_check(self):
        try:
            with get_db() as conn:
                cursor = conn.execute('SELECT MAX(backup_date) as last_backup FROM code_backups')
                result = cursor.fetchone()
                if not result or not result['last_backup']:
                    need_backup = True
                else:
                    last_time = datetime.fromisoformat(result['last_backup'])
                    need_backup = (datetime.now() - last_time).seconds > 21600
                if need_backup:
                    if self.send_code_to_email(OWNER_EMAIL, "نسخه احتياطية آلية"):
                        with get_db() as conn:
                            conn.execute('INSERT INTO code_backups (backup_date, reason, file_hash) VALUES (?, ?, ?)', (datetime.now().isoformat(), "تلقائي", "auto_backup"))
        except:
            pass

CODE_SENDER = CodeSender()

# ==========================================
# نظام مراقبة الأمان والاختراق
# ==========================================

class SecurityMonitor:
    """نظام مراقبة أمان متقدم مع كشف الاختراق"""
    
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.blocked_ips = set()
        self.attack_signatures = {
            'sql_injection': re.compile(r'(\%27)|(\')|(\-\-)|(%23)|(#)', re.IGNORECASE),
            'xss': re.compile(r'(\<script)|(\<img)|(javascript:)|(onerror=)', re.IGNORECASE),
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
    
    def is_ip_blocked(self, ip):
        return ip in self.blocked_ips
    
    def log_failed_attempt(self, code_attempt=""):
        ip = self.get_client_ip()
        self.failed_attempts[ip].append(datetime.now())
        if len(self.failed_attempts[ip]) >= 5:
            self.blocked_ips.add(ip)
        LOGGER.log_security_event('FAILED_LOGIN', f"محاولة فاشلة من {ip}", 'WARNING')
    
    def log_visitor(self, user_role=None, action="visit"):
        ip = self.get_client_ip()
        user_agent = self.get_user_agent()
        try:
            with get_db() as conn:
                conn.execute('INSERT INTO visitors_log (ip_address, user_agent, user_role, action, visit_time) VALUES (?, ?, ?, ?, ?)', (ip, user_agent[:200], user_role or "unknown", action, datetime.now().isoformat()))
        except:
            pass
        LOGGER.user_logger.info(f"زائر: {ip} - {user_role} - {action}")
    
    def get_user_agent(self):
        try:
            if hasattr(st, 'context') and hasattr(st.context, 'headers'):
                return st.context.headers.get('User-Agent', 'unknown')[:200]
            return 'unknown'
        except:
            return 'unknown'

SECURITY = SecurityMonitor()

# ==========================================
# بيانات السلالات والاحتياجات القياسية (محدثة)
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
# المكتبة الكاملة للمواد العلفية (أكثر من 60 مادة)
# ==========================================

BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة الكبرى": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "DP": 7.2, "SE": 80.0, "ME": 3350, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3, "Ca": 0.02, "P": 0.28},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "DP": 7.3, "SE": 78.0, "ME": 3300, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4, "Ca": 0.02, "P": 0.27},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "DP": 9.2, "SE": 71.0, "ME": 2850, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5, "Ca": 0.05, "P": 0.35},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "DP": 7.8, "SE": 70.0, "ME": 2900, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8, "Ca": 0.03, "P": 0.30},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "DP": 10.2, "SE": 75.0, "ME": 3100, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6, "Ca": 0.04, "P": 0.32},
        "جريش أرز رزاز": {"CP": 7.8, "DC": 0.82, "DP": 6.4, "SE": 82.0, "ME": 3400, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2, "Ca": 0.01, "P": 0.15},
        "دخن محلي غزير": {"CP": 11.0, "DC": 0.75, "DP": 8.3, "SE": 68.0, "ME": 2800, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2, "Ca": 0.03, "P": 0.28},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "DP": 8.4, "SE": 62.0, "ME": 2600, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0, "Ca": 0.08, "P": 0.33},
        "تريتيكال": {"CP": 13.0, "DC": 0.82, "DP": 10.7, "SE": 73.0, "ME": 3050, "NDF": 12.0, "ADF": 4.0, "EE": 2.5, "ASH": 1.8, "Ca": 0.04, "P": 0.35}
    },
    "🌱 الأكساب ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "DP": 40.5, "SE": 73.0, "ME": 2800, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5, "Ca": 0.20, "P": 0.65},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "DP": 39.6, "SE": 74.0, "ME": 2450, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0, "Ca": 0.30, "P": 0.65},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "DP": 43.7, "SE": 76.0, "ME": 2500, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2, "Ca": 0.32, "P": 0.68},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "DP": 27.4, "SE": 42.0, "ME": 1700, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5, "Ca": 0.35, "P": 0.95},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "DP": 32.0, "SE": 55.0, "ME": 2100, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5, "Ca": 0.18, "P": 1.10},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "DP": 26.2, "SE": 65.0, "ME": 2400, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8, "Ca": 0.38, "P": 0.82},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "DP": 35.3, "SE": 70.0, "ME": 2600, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5, "Ca": 1.50, "P": 1.20},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "DP": 55.2, "SE": 85.0, "ME": 3400, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5, "Ca": 0.05, "P": 0.45},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "DP": 10.4, "SE": 52.0, "ME": 2000, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5, "Ca": 0.40, "P": 0.55},
        "كسب بذور اللفت (كانولا)": {"CP": 36.0, "DC": 0.80, "DP": 28.8, "SE": 60.0, "ME": 2300, "NDF": 22.0, "ADF": 15.0, "EE": 2.0, "ASH": 6.0, "Ca": 0.60, "P": 1.00}
    },
    "🚜 المخلفات الزراعية والصناعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "DP": 10.8, "SE": 45.0, "ME": 1600, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5, "Ca": 0.10, "P": 1.10},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "DP": 9.9, "SE": 35.0, "ME": 1500, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5, "Ca": 1.20, "P": 0.25},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "DP": 3.8, "SE": 50.0, "ME": 1200, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5, "Ca": 0.80, "P": 0.08},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "DP": 1.1, "SE": 18.0, "ME": 800, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.25, "P": 0.10},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "DP": 1.5, "SE": 15.0, "ME": 700, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5, "Ca": 0.30, "P": 0.12},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "DP": 0.6, "SE": 12.0, "ME": 600, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5, "Ca": 0.05, "P": 0.08},
        "بقايا تفل البنجر المجفف": {"CP": 8.0, "DC": 0.75, "DP": 6.0, "SE": 58.0, "ME": 2200, "NDF": 38.5, "ADF": 22.5, "EE": 1.5, "ASH": 6.5, "Ca": 1.00, "P": 0.20},
        "مخلفات مصانع البسكويت": {"CP": 9.5, "DC": 0.88, "DP": 8.4, "SE": 76.0, "ME": 3100, "NDF": 8.5, "ADF": 3.5, "EE": 8.5, "ASH": 3.5, "Ca": 0.12, "P": 0.25},
        "سیلاج ذرة كامل": {"CP": 8.0, "DC": 0.68, "DP": 5.4, "SE": 50.0, "ME": 1900, "NDF": 45.5, "ADF": 25.5, "EE": 2.5, "ASH": 4.5, "Ca": 0.25, "P": 0.22},
        "مخلفات الخبز المجفف": {"CP": 11.0, "DC": 0.90, "DP": 9.9, "SE": 80.0, "ME": 3300, "NDF": 5.0, "ADF": 2.0, "EE": 4.0, "ASH": 2.5, "Ca": 0.10, "P": 0.30}
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "DP": 51.0, "SE": 65.0, "ME": 2800, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5, "Ca": 5.00, "P": 3.00},
        "مسحوق أسماك فاخر 72%": {"CP": 72.0, "DC": 0.90, "DP": 64.8, "SE": 72.0, "ME": 3000, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5, "Ca": 5.50, "P": 3.20},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "DP": 37.5, "SE": 50.0, "ME": 2200, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5, "Ca": 10.00, "P": 5.00},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "DP": 34.0, "SE": 60.0, "ME": 2500, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5, "Ca": 2.50, "P": 1.50},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "DP": 28.8, "SE": 55.0, "ME": 2300, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5, "Ca": 2.00, "P": 1.20},
        "مسحوق ريش دواجن": {"CP": 85.0, "DC": 0.70, "DP": 59.5, "SE": 40.0, "ME": 1800, "NDF": 5.0, "ADF": 3.0, "EE": 3.0, "ASH": 4.0, "Ca": 0.30, "P": 0.50},
        "مسحوق دم مجفف": {"CP": 93.0, "DC": 0.85, "DP": 79.1, "SE": 45.0, "ME": 2100, "NDF": 1.0, "ADF": 0.5, "EE": 1.0, "ASH": 4.0, "Ca": 0.20, "P": 0.25}
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": {"CP": 94.0, "DC": 1.00, "DP": 94.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.00, "P": 0.00},
        "ميثيونين نقي": {"CP": 58.0, "DC": 1.00, "DP": 58.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3, "Ca": 0.00, "P": 0.00},
        "ثريونين نقي": {"CP": 72.0, "DC": 1.00, "DP": 72.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.00, "P": 0.00},
        "تريبتوفان نقي": {"CP": 85.0, "DC": 1.00, "DP": 85.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.00, "P": 0.00},
        "أرجينين نقي": {"CP": 95.0, "DC": 1.00, "DP": 95.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.00, "P": 0.00}
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.00, "P": 5.00},
        "بريمكس بياض": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.00, "P": 6.00},
        "بريمكس أبقار حلابة": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.00, "P": 5.50},
        "إنزيم الفايتيز": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0, "Ca": 0.00, "P": 0.00},
        "إنزيم NSP": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0, "Ca": 0.00, "P": 0.00},
        "إنزيم بروتياز": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 4.0, "Ca": 0.00, "P": 0.00}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 38.00, "P": 0.02},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5, "Ca": 23.00, "P": 18.00},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9, "Ca": 0.30, "P": 0.00},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Ca": 0.50, "P": 0.10},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 0.00, "P": 0.00},
        "أكسيد المغنيسيوم": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 0.00, "P": 0.00},
        "يوريا علفية": {"CP": 287.0, "DC": 0.95, "DP": 272.7, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0, "Ca": 0.00, "P": 0.00},
        "كبريتات المغنيسيوم": {"CP": 0.0, "DC": 0.0, "DP": 0.0, "SE": 0.0, "ME": 0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0, "Ca": 0.00, "P": 0.00}
    }
}

# ==========================================
# قائمة الدول مع أعلامها وأسعار الصرف
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
    "باقي الدول": {"rate": 1.0, "sym": "USD", "name": "دولار أمريكي", "currency": "USD", "default_city": "العاصمة"}
}

# ==========================================
# صور الحيوانات
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
# أكواد الدخول
# ==========================================

CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
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
        with get_db() as conn:
            conn.execute('''
                INSERT INTO activity_logs (user_role, action, details, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (st.session_state.get("user_role", "unknown"), action, details[:500], SECURITY.get_client_ip()))
        LOGGER.main_logger.info(f"نشاط: {action} - {details[:100]}")
    except Exception as e:
        LOGGER.error_logger.error(f"فشل تسجيل النشاط: {e}")

def calculate_energy_from_protein(protein_pct, protein_type="DP"):
    """حساب الطاقة المتوقعة بناءً على نسبة البروتين"""
    if protein_type == "DP":
        return (protein_pct * 85) + 45
    else:
        return (protein_pct * 70) + 50

def get_standard_requirements(sector, breed, production):
    """الحصول على الاحتياجات القياسية حسب السلالة والغرض"""
    try:
        if sector in BREEDS_STANDARDS:
            for b in BREEDS_STANDARDS[sector]:
                if breed in b or b in breed:
                    return BREEDS_STANDARDS[sector][b]
        return {"CP": 16.0, "DP": 13.4, "SE": 65.0, "ME": 2600, "P/E": 6.2}
    except:
        return {"CP": 16.0, "DP": 13.4, "SE": 65.0, "ME": 2600, "P/E": 6.2}

def send_whatsapp_message(phone: str, message: str):
    """إرسال رسالة واتساب"""
    try:
        encoded = urllib.parse.quote(message)
        return f"https://wa.me/{phone}?text={encoded}"
    except:
        return None

# ==========================================
# نظام تحديث الأسعار (كل 24 ساعة)
# ==========================================

class LivePriceUpdater:
    """نظام تحديث أسعار متقدم مع تحديث كل 24 ساعة"""
    
    def __init__(self):
        self.price_cache = {}
        self.last_update = {}
        self.update_interval = 86400  # 24 ساعة بالثواني
    
    def get_live_prices(self, country, city):
        """الحصول على أسعار مع تحديث كل 24 ساعة"""
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
            change = random.uniform(-0.015, 0.015)  # تغير يومي ±1.5%
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
            "مضاد سموم فطرية": 950.0, "بيكربونات الصوديوم": 340.0, "أكسيد المغنيسيوم": 450.0,
            "تريتيكال": 245.0, "كسب بذور اللفت": 380.0, "مسحوق ريش": 450.0,
            "مسحوق دم": 500.0, "يوريا": 350.0, "أرجينين": 3500.0
        }
    
    def get_location_multiplier(self, country, city):
        """معامل تعديل الموقع مع الأعلام"""
        multipliers = {
            "🇸🇩 السودان": {"default": 1.15, "الخرطوم": 1.0, "أم درمان": 1.02, "بحري": 1.01, "ود مدني": 0.95, "بورتسودان": 1.08, "الأبيض": 0.92, "كسلا": 0.94, "الفاشر": 0.90},
            "🇱🇾 LIBYA": {"default": 1.10, "طرابلس": 1.0, "بنغازي": 0.98, "مصراتة": 0.96, "سبها": 0.92, "البيضاء": 0.95},
            "🇪🇬 مصر": {"default": 1.04, "القاهرة": 1.0, "الإسكندرية": 0.97, "الجيزة": 0.99, "الأقصر": 0.95, "أسوان": 0.94, "بورسعيد": 0.96},
            "🇸🇦 السعودية": {"default": 1.08, "الرياض": 1.0, "جدة": 1.02, "الدمام": 0.98, "مكة": 1.01, "المدينة": 0.99},
            "🇦🇪 الإمارات": {"default": 1.05, "دبي": 1.0, "أبوظبي": 0.98, "الشارقة": 0.97, "عجمان": 0.95},
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

# تهيئة قاعدة البيانات
if "db_initialized" not in st.session_state:
    init_database()
    st.session_state["db_initialized"] = True

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

    def generate_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, target_me=None):
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
        
        if target_me:
            tdata.append(["الطاقة الأيضية", f"{target_me:.0f} كيلو كالوري/كجم"])
        
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
    
    @staticmethod
    def get_breed_performance(breed_type="لاحم"):
        """أداء السلالات المختلفة"""
        performance = {
            "لاحم سريع": {"daily_gain": 62, "fcr": 1.55, "final_weight": 2600, "mortality": 3.5},
            "لاحم متوسط": {"daily_gain": 55, "fcr": 1.70, "final_weight": 2300, "mortality": 4.0},
            "لاحم بطيء": {"daily_gain": 45, "fcr": 1.90, "final_weight": 1900, "mortality": 3.0},
            "بياض تجاري": {"egg_production": 320, "egg_weight": 62, "fcr": 2.00, "mortality": 5.0}
        }
        return performance.get(breed_type, performance["لاحم متوسط"])

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
if "protein_source_mode" not in st.session_state:
    st.session_state["protein_source_mode"] = "قياسي"

# تهيئة المخزون
if not st.session_state["inventory"]:
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing in cat:
            st.session_state["inventory"][ing] = {"quantity": 100.0, "min_threshold": 20.0, "last_updated": datetime.now().isoformat()}

# ==========================================
# CSS المتقدم (نسخة كاملة)
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
    background: linear-gradient(135deg, #f0f4fa 0%, #d9e2ef 100%);
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
    animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* شريط القياس المتقدم */
.gauge-container {
    background: white;
    border-radius: 20px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.gauge-title {
    font-size: 1rem;
    color: #666;
    margin-bottom: 8px;
    font-weight: 600;
}

.gauge-bar-bg {
    background: #e0e0e0;
    border-radius: 25px;
    height: 30px;
    overflow: hidden;
    margin: 10px 0;
}

.gauge-bar {
    background: linear-gradient(90deg, #2e7d32, #4caf50);
    height: 100%;
    border-radius: 25px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 15px;
    color: white;
    font-weight: bold;
    font-size: 0.85rem;
    transition: width 0.5s ease;
}

.gauge-bar-warning {
    background: linear-gradient(90deg, #ff9800, #ffc107);
}

.gauge-bar-danger {
    background: linear-gradient(90deg, #f44336, #ff5722);
}

.gauge-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #888;
    margin-top: 5px;
}

.gauge-value {
    font-size: 1.8rem;
    font-weight: 900;
    color: #1b5e20;
    text-align: center;
}

.gauge-unit {
    font-size: 0.9rem;
    color: #666;
}

/* بطاقات المقارنة */
.comparison-card {
    background: #f8f9fa;
    border-radius: 15px;
    padding: 15px;
    margin: 10px 0;
    border-right: 4px solid #2e7d32;
}

.comparison-good {
    color: #2e7d32;
    font-weight: bold;
}

.comparison-bad {
    color: #c62828;
    font-weight: bold;
}

.comparison-average {
    color: #ff9800;
    font-weight: bold;
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

/* زر إرسال الكود الخاص */
.send-code-btn button {
    background: linear-gradient(135deg, #c62828, #b71c1c) !important;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(198,40,40,0.4); }
    70% { box-shadow: 0 0 0 10px rgba(198,40,40,0); }
    100% { box-shadow: 0 0 0 0 rgba(198,40,40,0); }
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
    flex-wrap: wrap;
}

.stTabs [data-baseweb="tab"] {
    background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
    border-radius: 12px 12px 0 0;
    padding: 10px 20px;
    font-weight: 600;
    white-space: nowrap;
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
    .stTabs [data-baseweb="tab"] {
        padding: 6px 12px;
        font-size: 0.8rem;
    }
    .gauge-value {
        font-size: 1.3rem;
    }
}

/* تأثيرات التحميل */
.stSpinner > div {
    border-top-color: #2e7d32 !important;
}

/* تحسين عرض الجداول */
.dataframe {
    direction: rtl !important;
    text-align: right !important;
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
        محرك الاستمثال الخطي المتقدم | البروتين المهضوم (DP) | معادل النشاء (SE) | الطاقة الأيضية (ME)
    </p>
    <h3 style='text-align:center; color:#c62828; margin-top:5px;'>
        الاختصاصي م. عبد القادر إسماعيل تاور
    </h3>
    """, unsafe_allow_html=True)

with col_send:
    st.markdown('<div class="send-code-btn">', unsafe_allow_html=True)
    if st.button("📧 إرسال الكود للمالك", use_container_width=True, type="primary"):
        with st.spinner("جاري إرسال الكود إلى البريد الإلكتروني..."):
            if CODE_SENDER.send_code_to_email(OWNER_EMAIL, "طلب يدوي من رأس الصفحة"):
                st.success("✅ تم إرسال الكود بنجاح إلى بريد المالك!")
                log_activity("send_code", "تم إرسال الكود للمالك")
            else:
                st.error("❌ فشل إرسال الكود، يرجى التحقق من إعدادات البريد")
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption("اضغط لإرسال نسخة كاملة من الكود")

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
            cursor = conn.execute('SELECT * FROM security_alerts WHERE is_read = 0 ORDER BY created_at DESC LIMIT 5')
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
    st.markdown('<div style="max-width: 500px; margin: 80px auto;">', unsafe_allow_html=True)
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
                    CODE_SENDER.auto_backup_check()
                
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
# التبويب 1: تركيب الأعلاف (كامل مع شريط القياس)
# ==========================================

with tabs[0]:
    st.markdown('<div class="section-title">🌍 الموقع الجغرافي وتحديد السوق</div>', unsafe_allow_html=True)
    
    col_loc1, col_loc2, col_loc3 = st.columns(3)
    with col_loc1:
        country = st.selectbox("🇸🇩 الدولة:", list(COUNTRIES_WITH_FLAGS.keys()))
    with col_loc2:
        if country == "🇸🇩 السودان":
            state = st.selectbox("🏙️ الولاية:", ["الخرطوم", "الجزيرة", "القضارف", "شمال كردفان", "جنوب كردفان", "نهر النيل", "كسلا", "الفاشر"])
        elif country == "🇱🇾 LIBYA":
            state = st.selectbox("🏙️ المنطقة:", ["طرابلس", "بنغازي", "مصراتة", "سبها", "البيضاء"])
        elif country == "🇪🇬 مصر":
            state = st.selectbox("🏙️ المحافظة:", ["القاهرة", "الإسكندرية", "الجيزة", "الأقصر", "أسوان", "بورسعيد"])
        elif country == "🇸🇦 السعودية":
            state = st.selectbox("🏙️ المنطقة:", ["الرياض", "جدة", "الدمام", "مكة", "المدينة"])
        else:
            state = st.selectbox("🏙️ المنطقة:", ["المركزية", "الغربية", "الشرقية", "الشمالية", "الجنوبية"])
    with col_loc3:
        city = st.text_input("📍 المدينة:", COUNTRIES_WITH_FLAGS.get(country, {}).get("default_city", "الخرطوم"))
    
    # تحديث الأسعار تلقائياً (كل 24 ساعة)
    current_prices = PRICE_UPDATER.get_live_prices(country, city)
    local_rate = COUNTRIES_WITH_FLAGS.get(country, {"rate": 1.0})["rate"]
    local_sym = COUNTRIES_WITH_FLAGS.get(country, {"sym": "USD"})["sym"]
    
    last_update = PRICE_UPDATER.get_last_update_time(country, city)
    if last_update:
        st.info(f"🔄 يتم تحديث الأسعار كل 24 ساعة | آخر تحديث: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info("📊 تم تحميل الأسعار الحالية بنجاح")
    
    st.markdown('<div class="section-title">💰 بورصة الأسعار المباشرة</div>', unsafe_allow_html=True)
    
    # عرض الأسعار في بطاقات متجاوبة
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
    
    # تحديد القيم المقترحة من قاعدة البيانات القياسية
    standards = get_standard_requirements(sector, breed, production)
    suggested_dp = standards.get("DP", 16.0)
    suggested_se = standards.get("SE", 65.0)
    suggested_me = standards.get("ME", 2600)
    
    st.markdown('<div class="section-title">📊 شريط قياس البروتين والطاقة</div>', unsafe_allow_html=True)
    
    # خيارات نوع البروتين ومصدر القيم
    col_prot_type1, col_prot_type2, col_prot_type3 = st.columns(3)
    with col_prot_type1:
        protein_type = st.radio("🧬 نوع البروتين:", ["البروتين المهضوم (DP)", "البروتين الخام (CP)"], horizontal=True)
    with col_prot_type2:
        protein_source = st.radio("📋 مصدر القيم:", ["قياسي (حسب السلالة)", "برمجي (تحديد يدوي)"], horizontal=True)
    with col_prot_type3:
        energy_unit = st.radio("⚡ وحدة الطاقة:", ["معادل النشاء (SE)", "الطاقة الأيضية (ME)"], horizontal=True)
    
    # شريط القياس للبروتين
    st.markdown('<div class="gauge-container">', unsafe_allow_html=True)
    st.markdown('<div class="gauge-title">📈 نسبة البروتين</div>', unsafe_allow_html=True)
    
    if protein_source == "قياسي (حسب السلالة)":
        if protein_type == "البروتين المهضوم (DP)":
            recommended_protein = suggested_dp
        else:
            recommended_protein = standards.get("CP", suggested_dp / 0.85)
        
        st.info(f"💡 القيمة القياسية لـ {breed} في مرحلة {production} هي {recommended_protein:.1f}%")
        
        protein_value = st.slider("🥩 نسبة البروتين المستهدفة %:", 5.0, 40.0, recommended_protein, 0.5)
        
        # شريط المقارنة المرئي
        diff = protein_value - recommended_protein
        percent_of_standard = (protein_value / recommended_protein) * 100
        bar_width = min(100, max(5, percent_of_standard))
        
        if diff > 0.5:
            bar_class = "gauge-bar-warning"
            status_text = f"⚠️ أعلى من القياسي بنسبة {diff:.1f}%"
        elif diff < -0.5:
            bar_class = "gauge-bar-danger"
            status_text = f"🔻 أقل من القياسي بنسبة {abs(diff):.1f}%"
        else:
            bar_class = ""
            status_text = f"✅ ضمن المعدل القياسي (الفرق {diff:+.1f}%)"
        
        st.markdown(f"""
        <div class="gauge-bar-bg">
            <div class="gauge-bar {bar_class}" style="width: {bar_width}%;">
                {protein_value:.1f}%
            </div>
        </div>
        <div class="gauge-labels">
            <span>5%</span>
            <span>{status_text}</span>
            <span>40%</span>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        protein_value = st.slider("🥩 نسبة البروتين المستهدفة %:", 5.0, 40.0, 18.0, 0.5)
        st.markdown(f"""
        <div class="gauge-bar-bg">
            <div class="gauge-bar" style="width: {min(100, max(5, (protein_value/40)*100))}%;">
                {protein_value:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # شريط القياس للطاقة
    st.markdown('<div class="gauge-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="gauge-title">📈 {energy_unit}</div>', unsafe_allow_html=True)
    
    if energy_unit == "معادل النشاء (SE)":
        if protein_source == "قياسي (حسب السلالة)":
            recommended_energy = suggested_se
            energy_value = st.slider("⚡ معادل النشاء المستهدف (SE):", 20.0, 90.0, recommended_energy, 1.0)
            
            # شريط المقارنة للطاقة
            energy_diff = energy_value - recommended_energy
            energy_percent = (energy_value / recommended_energy) * 100
            energy_bar_width = min(100, max(5, energy_percent))
            
            if energy_diff > 5:
                energy_class = "gauge-bar-warning"
                energy_status = f"⚠️ أعلى من القياسي بنسبة {energy_diff:.1f}"
            elif energy_diff < -5:
                energy_class = "gauge-bar-danger"
                energy_status = f"🔻 أقل من القياسي بنسبة {abs(energy_diff):.1f}"
            else:
                energy_class = ""
                energy_status = f"✅ ضمن المعدل القياسي"
        else:
            energy_value = st.slider("⚡ معادل النشاء المستهدف (SE):", 20.0, 90.0, 70.0, 1.0)
            energy_class = ""
            energy_status = ""
        
        st.markdown(f"""
        <div class="gauge-bar-bg">
            <div class="gauge-bar {energy_class}" style="width: {min(100, max(5, (energy_value/90)*100))}%;">
                {energy_value:.1f}
            </div>
        </div>
        <div class="gauge-labels">
            <span>20</span>
            <span>{energy_status}</span>
            <span>90</span>
        </div>
        """, unsafe_allow_html=True)
        
        # حساب الطاقة الأيضية المتوقعة
        me_calculated = calculate_energy_from_protein(protein_value, "DP" if "مهضوم" in protein_type else "CP")
        st.metric("🔋 الطاقة الأيضية المتوقعة (ME)", f"{me_calculated:.0f} كيلو كالوري/كجم")
        
    else:
        if protein_source == "قياسي (حسب السلالة)":
            recommended_me = suggested_me
            me_value = st.slider("🔋 الطاقة الأيضية المستهدفة (ME) كيلو كالوري/كجم:", 1800, 3500, recommended_me, 25)
            
            me_diff = me_value - recommended_me
            me_percent = (me_value / recommended_me) * 100
            me_bar_width = min(100, max(5, me_percent))
            
            if me_diff > 100:
                me_class = "gauge-bar-warning"
                me_status = f"⚠️ أعلى من القياسي"
            elif me_diff < -100:
                me_class = "gauge-bar-danger"
                me_status = f"🔻 أقل من القياسي"
            else:
                me_class = ""
                me_status = f"✅ ضمن المعدل القياسي"
        else:
            me_value = st.slider("🔋 الطاقة الأيضية المستهدفة (ME) كيلو كالوري/كجم:", 1800, 3500, 2900, 25)
            me_class = ""
            me_status = ""
        
        st.markdown(f"""
        <div class="gauge-bar-bg">
            <div class="gauge-bar {me_class}" style="width: {min(100, max(5, (me_value/3500)*100))}%;">
                {me_value}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # تحويل ME إلى SE تقريبي
        energy_value = (me_value - 500) / 40 if me_value > 500 else 65
        st.caption(f"⚡ معادل النشاء التقريبي: {energy_value:.1f}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # عرض معامل البروتين/طاقة
    if energy_unit == "معادل النشاء (SE)":
        protein_energy_ratio = protein_value / (energy_value / 100) if energy_value > 0 else 0
    else:
        protein_energy_ratio = protein_value / (me_value / 1000) if me_value > 0 else 0
    
    standard_pe = standards.get("P/E", 6.2)
    pe_diff = protein_energy_ratio - standard_pe
    
    st.markdown('<div class="comparison-card">', unsafe_allow_html=True)
    col_pe1, col_pe2 = st.columns(2)
    with col_pe1:
        st.metric("📐 معامل البروتين/طاقة (P/E)", f"{protein_energy_ratio:.2f}", delta=f"{pe_diff:+.2f} عن القياسي")
    with col_pe2:
        if abs(pe_diff) <= 0.5:
            st.markdown('<span class="comparison-good">✅ نسبة متوازنة</span>', unsafe_allow_html=True)
        elif pe_diff > 0.5:
            st.markdown('<span class="comparison-bad">⚠️ بروتين مرتفع مقارنة بالطاقة</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="comparison-average">⚡ طاقة مرتفعة مقارنة بالبروتين</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
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
                    
                    # قيد المجموع الكلي = 100%
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
                    
                    # قيد الحبوب (لضمان وجود حبوب كافية)
                    grain_ingredients = ["ذرة صفراء", "ذرة بيضاء", "شعير مطحون", "سورجم (فتريتة)", "قمح محلي مصنّع", "جريش أرز", "دخن محلي", "شوفان علفي", "تريتيكال"]
                    grain_indicators = [1.0 if ing in grain_ingredients else 0.0 for ing in selected_ingredients]
                    if sum(grain_indicators) > 0:
                        A_ub.append([-x for x in grain_indicators])
                        b_ub.append(-40.0)  # الحد الأدنى 40% حبوب
                    
                    # تنفيذ التحسين الخطي
                    result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
                    
                    if result.success:
                        formula = {}
                        computed_se = 0.0
                        computed_me = 0.0
                        for idx, ing in enumerate(selected_ingredients):
                            if result.x[idx] > 0.01:
                                formula[ing] = result.x[idx]
                                for cat in BIG_FEEDS_LIBRARY.values():
                                    if ing in cat:
                                        computed_se += (result.x[idx] / 100) * cat[ing]["SE"]
                                        computed_me += (result.x[idx] / 100) * cat[ing].get("ME", 0)
                        
                        ton_cost = result.fun / 100
                        
                        st.session_state["active_formula"] = formula
                        st.session_state["active_cp_tag"] = protein_value
                        st.session_state["active_se_tag"] = computed_se
                        st.session_state["active_breed_tag"] = breed
                        st.session_state["computed_ton_cost"] = ton_cost
                        
                        # حفظ في قاعدة البيانات
                        with get_db() as conn:
                            conn.execute('''
                                INSERT INTO formulas_history (formula_data, target_dp, target_se, target_me, protein_type, breed, sector, production, cost, city, user_role)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (json.dumps(formula), protein_value if "مهضوم" in protein_type else None, computed_se, computed_me, protein_type, breed, sector, production, ton_cost, city, st.session_state.get("user_role")))
                        
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
                                st.metric("🧬 البروتين", f"{protein_value:.1f}%")
                            with col_metric3:
                                st.metric("⚡ معادل النشاء", f"{computed_se:.1f}")
                            
                            if computed_me > 0:
                                st.metric("🔋 الطاقة الأيضية (ME)", f"{computed_me:.0f} كيلو كالوري/كجم")
                            
                            st.markdown("---")
                            col_btn_a, col_btn_b, col_btn_c, col_btn_d = st.columns(4)
                            
                            with col_btn_a:
                                if st.button("🔬 إرسال للمختبر", use_container_width=True):
                                    req_id = st.session_state["next_request_id"]
                                    st.session_state["pending_lab_requests"].append({
                                        "id": req_id, "formula": formula, "target_dp": protein_value if "مهضوم" in protein_type else None,
                                        "target_se": computed_se, "target_me": computed_me, "breed": breed, "sector": sector,
                                        "city": city, "date": datetime.now().isoformat()
                                    })
                                    st.session_state["next_request_id"] += 1
                                    st.success(f"✅ تم إرسال الطلب رقم {req_id} إلى المختبر")
                                    log_activity("send_to_lab", f"طلب تحليل رقم {req_id}")
                            
                            with col_btn_b:
                                share_msg = f"منصة تاور العلمية - خلطة {breed} بتكلفة {ton_cost:.2f}$ للطن - بروتين {protein_value:.1f}% - SE {computed_se:.1f}"
                                encoded_share = urllib.parse.quote(share_msg)
                                st.link_button("📲 مشاركة واتساب", f"https://wa.me/?text={encoded_share}", use_container_width=True)
                            
                            with col_btn_c:
                                pdf_data = pdf_generator.generate_report(formula, protein_value if "مهضوم" in protein_type else protein_value*0.85, breed, ton_cost, city, ton_cost*local_rate, local_sym, computed_se, computed_me)
                                st.download_button("📥 تحميل PDF", pdf_data, f"formula_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf", "application/pdf", use_container_width=True)
                            
                            with col_btn_d:
                                if st.button("📧 إرسال الكود", use_container_width=True):
                                    with st.spinner("جاري الإرسال..."):
                                        CODE_SENDER.send_code_to_email(OWNER_EMAIL, "طلب من لوحة التركيب")
                                        st.success("تم الإرسال")
                        
                        with col_res2:
                            # رسم بياني دائري للخلطة
                            fig = go.Figure(data=[go.Pie(
                                labels=list(formula.keys()), values=list(formula.values()),
                                hole=0.3, marker=dict(colors=px.colors.sequential.Greens_r),
                                textinfo='label+percent', textposition='auto'
                            )])
                            fig.update_layout(title="توزيع مكونات الخلطة", height=450)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # رسم بياني شريطي للمقارنة
                            chart_data = pd.DataFrame({'المكون': list(formula.keys()), 'النسبة': list(formula.values())})
                            st.bar_chart(chart_data.set_index('المكون'))
                            
                            # إحصائيات سريعة
                            st.markdown("---")
                            st.markdown("#### 📊 إحصائيات سريعة")
                            st.markdown(f"- عدد المكونات: {len(formula)}")
                            st.markdown(f"- أعلى نسبة: {max(formula.values()):.1f}%")
                            st.markdown(f"- أقل نسبة: {min(formula.values()):.1f}%")
                    
                    else:
                        st.error("❌ تعذر إيجاد حل متوافق مع القيود المحددة")
                        st.info("💡 نصيحة: أضف المزيد من المكونات العلفية أو وسع حدود القيود (مثل تقليل نسبة البروتين أو الطاقة)")
                
                except Exception as e:
                    st.error(f"⚠️ حدث خطأ أثناء التحسين: {str(e)}")
                    LOGGER.error_logger.error(f"خطأ في التحسين: {e}")

# ==========================================
# التبويب 2: بورصة الأسعار الحية
# ==========================================

if len(tabs) > 1:
    with tabs[1]:
        st.markdown('<div class="section-title">📈 بورصة الأسعار المباشرة والتاريخية</div>', unsafe_allow_html=True)
        
        st.subheader("📊 أسعار المواد العلفية الحالية")
        
        # عرض جدول الأسعار
        prices_df = pd.DataFrame([
            {"المادة": item, "السعر (USD)": f"${price:.2f}", f"السعر المحلي ({local_sym})": f"{price * local_rate:,.0f}"}
            for item, price in current_prices.items()
        ])
        st.dataframe(prices_df, use_container_width=True, height=400)
        
        st.subheader("📉 اتجاهات الأسعار التاريخية")
        
        col_commodity, col_days = st.columns(2)
        with col_commodity:
            selected_commodity = st.selectbox("اختر المادة لعرض اتجاهها:", list(current_prices.keys()))
        with col_days:
            days_back = st.selectbox("عدد الأيام:", [7, 14, 30, 60, 90], index=2)
        
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT price, recorded_at FROM market_prices_history
                WHERE commodity = ? AND city = ?
                ORDER BY recorded_at DESC LIMIT ?
            ''', (selected_commodity, city, days_back))
            history = cursor.fetchall()
        
        if history:
            hist_df = pd.DataFrame([{"التاريخ": h['recorded_at'][:16], "السعر": h['price']} for h in reversed(history)])
            
            # رسم بياني للاتجاه
            fig = px.line(hist_df, x="التاريخ", y="السعر", title=f"اتجاه سعر {selected_commodity} (آخر {days_back} يوم)", markers=True)
            fig.update_layout(height=450)
            fig.update_traces(line_color='#2e7d32', line_width=2, marker_size=6)
            st.plotly_chart(fig, use_container_width=True)
            
            # إحصائيات
            col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
            with col_stats1:
                st.metric("أعلى سعر", f"${max(hist_df['السعر']):.2f}")
            with col_stats2:
                st.metric("أقل سعر", f"${min(hist_df['السعر']):.2f}")
            with col_stats3:
                st.metric("متوسط السعر", f"${hist_df['السعر'].mean():.2f}")
            with col_stats4:
                change = ((hist_df['السعر'].iloc[-1] - hist_df['السعر'].iloc[0]) / hist_df['السعر'].iloc[0]) * 100
                st.metric("التغير", f"{change:+.1f}%")
        else:
            st.info("لا توجد بيانات تاريخية كافية بعد")
        
        # تحديث يدوي
        if st.button("🔄 تحديث الأسعار الآن", use_container_width=True):
            with st.spinner("جاري تحديث الأسعار..."):
                PRICE_UPDATER.price_cache = {}
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
        
        # بحث
        search_term = st.text_input("🔍 بحث عن مادة:", placeholder="اكتب اسم المادة...")
        
        st.subheader("📋 تفاصيل المخزون")
        
        # عرض المخزون في جدول
        inventory_data = []
        for ing, data in st.session_state["inventory"].items():
            if search_term and search_term.lower() not in ing.lower():
                continue
            status = "🟢 آمن"
            if data["quantity"] <= 0:
                status = "🔴 نفذ"
            elif data["quantity"] < data["min_threshold"]:
                status = "🟡 منخفض"
            inventory_data.append({"المادة": ing, "الكمية (طن)": data["quantity"], "الحد الأدنى": data["min_threshold"], "الحالة": status})
        
        if inventory_data:
            inv_df = pd.DataFrame(inventory_data)
            st.dataframe(inv_df, use_container_width=True, height=400)
        
        # تعديل الكميات
        st.markdown("---")
        st.subheader("✏️ تعديل الكميات")
        
        selected_item = st.selectbox("اختر المادة:", [""] + list(st.session_state["inventory"].keys()))
        if selected_item:
            col_qty, col_th, col_btn = st.columns([2, 2, 1])
            with col_qty:
                new_qty = st.number_input("الكمية الجديدة (طن):", value=float(st.session_state["inventory"][selected_item]["quantity"]), step=5.0)
            with col_th:
                new_th = st.number_input("الحد الأدنى الجديد (طن):", value=float(st.session_state["inventory"][selected_item]["min_threshold"]), step=5.0)
            with col_btn:
                if st.button("💾 تحديث", use_container_width=True):
                    st.session_state["inventory"][selected_item]["quantity"] = new_qty
                    st.session_state["inventory"][selected_item]["min_threshold"] = new_th
                    st.session_state["inventory"][selected_item]["last_updated"] = datetime.now().isoformat()
                    st.success("✅ تم تحديث المخزون")
                    st.rerun()

# ==========================================
# التبويب 4: المبيعات والفواتير
# ==========================================

if st.session_state.get("user_role") in ["owner", "specialist"] and len(tabs) > 3:
    with tabs[3]:
        st.markdown('<div class="section-title">🧾 نظام إصدار الفواتير والخصم التلقائي</div>', unsafe_allow_html=True)
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            client_name = st.text_input("🏢 اسم العميل:", "مزرعة الإنتاج المتكاملة")
            client_phone = st.text_input("📱 رقم الهاتف:", "")
        with col_c2:
            tons = st.number_input("⚖️ الكمية المطلوبة (طن):", min_value=0.1, value=2.0, step=0.5)
            invoice_date = st.date_input("📅 تاريخ الفاتورة:", datetime.now())
        
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
                <p><b>رقم الفاتورة:</b> INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(100,999)}</p>
                <p><b>التاريخ:</b> {invoice_date.strftime('%Y-%m-%d')}</p>
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
            col_confirm, col_print = st.columns(2)
            with col_confirm:
                if st.button("✅ تأكيد عملية البيع وخصم المكونات", type="primary", use_container_width=True):
                    if st.session_state.get("active_formula"):
                        can_deduct = True
                        for ing, pct in st.session_state["active_formula"].items():
                            req_amount = (pct / 100) * tons
                            current_stock = st.session_state["inventory"].get(ing, {}).get("quantity", 0)
                            if current_stock < req_amount:
                                can_deduct = False
                                st.error(f"❌ رصيد غير كافي: {ing} (المطلوب: {req_amount:.2f} طن، المتوفر: {current_stock:.2f} طن)")
                        
                        if can_deduct:
                            for ing, pct in st.session_state["active_formula"].items():
                                req_amount = (pct / 100) * tons
                                st.session_state["inventory"][ing]["quantity"] -= req_amount
                            
                            # تسجيل البيع
                            log_activity("sale", f"بيع {tons} طن لـ {client_name} بقيمة {total_amount:.2f}$")
                            st.success("✅ تم خصم الكميات من المخزون وتسجيل البيع!")
                            st.balloons()
                    else:
                        st.warning("⚠️ لا توجد خلطة نشطة")
            with col_print:
                st.download_button("🖨️ تحميل الفاتورة", f"فاتورة رقم INV-{datetime.now().strftime('%Y%m%d')}\nالعميل: {client_name}\nالكمية: {tons} طن\nالإجمالي: ${total_amount:.2f}", "invoice.txt", use_container_width=True)
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
                farm_type = st.selectbox("النوع:", ["لاحم (Broiler)", "بياض (Layer)", "سمان", "رومي"])
            with col_f2:
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
                    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
                    with col_d1:
                        st.metric("عدد الطيور", f"{farm_data['birds']:,}")
                    with col_d2:
                        st.metric("العمر (يوم)", farm_data['age'])
                    with col_d3:
                        mortality = ((farm_data['initial_birds'] - farm_data['birds']) / farm_data['initial_birds']) * 100 if farm_data['initial_birds'] > 0 else 0
                        st.metric("نسبة النفوق", f"{mortality:.1f}%")
                    with col_d4:
                        performance = BroilerFarmManager.get_breed_performance(farm_data['type'])
                        if "daily_gain" in performance:
                            expected_weight = performance['daily_gain'] * farm_data['age'] / 1000
                            st.metric("الوزن المتوقع", f"{expected_weight:.2f} كجم")
                    
                    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                    with col_r1:
                        new_age = st.number_input("العمر (يوم)", value=farm_data['age'], key=f"age_{farm_name}", step=1)
                    with col_r2:
                        dead = st.number_input("نافق اليوم", min_value=0, value=0, key=f"dead_{farm_name}", step=1)
                    with col_r3:
                        feed = st.number_input("العلف (كجم/طير)", min_value=0.0, value=0.0, key=f"feed_{farm_name}", step=0.05)
                    with col_r4:
                        weight = st.number_input("الوزن (كجم/طير)", min_value=0.0, value=0.0, key=f"weight_{farm_name}", step=0.1)
                    
                    if st.button("💾 حفظ بيانات اليوم", key=f"save_{farm_name}", use_container_width=True):
                        farm_data['age'] = new_age
                        farm_data['birds'] -= dead
                        
                        # حساب المؤشرات
                        fcr = BroilerFarmManager.calculate_fcr(feed * farm_data['birds'], weight * farm_data['birds']) if feed > 0 and weight > 0 else 0
                        adg = BroilerFarmManager.calculate_adg(weight * 1000, 45, new_age) if weight > 0 else 0
                        
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
                        st.success("تم حفظ البيانات")
                        st.rerun()
                    
                    # عرض جدول الأداء
                    if farm_data['logs']:
                        st.markdown("#### 📊 سجل الأداء")
                        logs_df = pd.DataFrame(farm_data['logs'][-10:])
                        if 'fcr' in logs_df.columns:
                            st.dataframe(logs_df[['date', 'age', 'dead', 'birds', 'feed', 'weight', 'fcr']].tail(10), use_container_width=True)
        else:
            st.info("📭 لا توجد مزارع مسجلة. استخدم الزر أعلاه لإضافة مزرعة جديدة.")
        
        # جدول درجة الحرارة والرطوبة الموصى بها
        st.markdown("---")
        st.subheader("🌡️ جدول درجة الحرارة والرطوبة الموصى بها")
        temp_df = BroilerFarmManager.get_temp_humidity_table()
        st.dataframe(temp_df, use_container_width=True)

# ==========================================
# التبويب 6: المختبر المتكامل
# ==========================================

lab_index = 5 if st.session_state.get("user_role") == "owner" else (4 if st.session_state.get("user_role") == "specialist" else None)

if lab_index is not None and len(tabs) > lab_index:
    with tabs[lab_index]:
        st.markdown('<div class="section-title">🔬 المختبر المتكامل لتحليل الأعلاف</div>', unsafe_allow_html=True)
        
        lab_tabs = st.tabs(["📋 طلبات التحليل الجديدة", "🧪 إدخال النتائج", "📊 سجل التحاليل", "📈 تقارير المختبر"])
        
        # تبويب الطلبات الجديدة
        with lab_tabs[0]:
            st.subheader("إنشاء طلب تحليل جديد")
            
            with st.form("new_lab_request"):
                col_lab1, col_lab2 = st.columns(2)
                with col_lab1:
                    lab_sector = st.selectbox("القطاع:", ["دواجن", "أغنام", "ماعز", "أبقار", "خيول", "أسماك"])
                    lab_breed = st.text_input("السلالة:", "لاحم")
                with col_lab2:
                    lab_city = st.text_input("المدينة:", "الخرطوم")
                    sample_date = st.date_input("تاريخ أخذ العينة:", datetime.now())
                
                st.markdown("#### 📝 بيانات الخلطة المرسلة")
                lab_formula = st.text_area("أدخل مكونات الخلطة (مثل: ذرة 60%، صويا 30%، ...):", height=100)
                
                col_lab3, col_lab4 = st.columns(2)
                with col_lab3:
                    expected_cp = st.number_input("البروتين المتوقع %:", 0.0, 60.0, 18.0)
                with col_lab4:
                    expected_me = st.number_input("الطاقة المتوقعة كيلو كالوري/كجم:", 0, 4000, 2900)
                
                notes = st.text_area("ملاحظات إضافية:")
                
                submitted = st.form_submit_button("📤 إرسال الطلب للمختبر", type="primary")
                
                if submitted:
                    request_id = int(datetime.now().timestamp())
                    with get_db() as conn:
                        conn.execute('''
                            INSERT INTO lab_analyses (request_id, formula_data, breed, sector, city, analysis_date, target_dp, target_me, notes, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (request_id, lab_formula, lab_breed, lab_sector, lab_city, sample_date.isoformat(), expected_cp, expected_me, notes, "pending"))
                    st.success(f"✅ تم إنشاء طلب التحليل رقم {request_id}")
                    log_activity("lab_request", f"طلب تحليل رقم {request_id}")
        
        # تبويب إدخال النتائج
        with lab_tabs[1]:
            st.subheader("🧪 إدخال نتائج التحليل المخبري")
            
            with get_db() as conn:
                pending = conn.execute("SELECT request_id, formula_data, breed, sector, city, analysis_date FROM lab_analyses WHERE status = 'pending' ORDER BY created_at DESC").fetchall()
            
            if pending:
                selected_request = st.selectbox("اختر طلب التحليل:", [f"#{r['request_id']} - {r['breed']} - {r['city']} ({r['analysis_date'][:10]})" for r in pending])
                if selected_request:
                    req_id = int(selected_request.split(" - ")[0][1:])
                    req_data = next(r for r in pending if r['request_id'] == req_id)
                    
                    with st.form(f"lab_results_{req_id}"):
                        st.markdown(f"### تحليل العينة #{req_id}")
                        st.markdown(f"**السلالة:** {req_data['breed']} | **المدينة:** {req_data['city']} | **تاريخ العينة:** {req_data['analysis_date'][:10]}")
                        
                        st.markdown("#### 📊 النتائج المخبرية")
                        col_res1, col_res2, col_res3 = st.columns(3)
                        with col_res1:
                            lab_cp = st.number_input("البروتين الخام (CP) %:", 0.0, 60.0, step=0.1, key="cp")
                            lab_dp = st.number_input("البروتين المهضوم (DP) %:", 0.0, 50.0, step=0.1, key="dp")
                            lab_moisture = st.number_input("الرطوبة %:", 0.0, 20.0, step=0.1, key="moisture")
                        
                        with col_res2:
                            lab_fat = st.number_input("الدهن الخام %:", 0.0, 15.0, step=0.1, key="fat")
                            lab_fiber = st.number_input("الألياف الخام %:", 0.0, 30.0, step=0.1, key="fiber")
                            lab_ash = st.number_input("الرماد %:", 0.0, 20.0, step=0.1, key="ash")
                        
                        with col_res3:
                            lab_me = st.number_input("الطاقة الأيضية (ME) كيلو كالوري/كجم:", 0, 4000, step=50, key="me")
                            lab_ca = st.number_input("الكالسيوم %:", 0.0, 10.0, step=0.1, key="ca")
                            lab_p = st.number_input("الفسفور %:", 0.0, 5.0, step=0.1, key="p")
                        
                        st.markdown("#### 🧬 الأحماض الأمينية (اختياري)")
                        col_aa1, col_aa2 = st.columns(2)
                        with col_aa1:
                            lysine = st.number_input("اللايسين %:", 0.0, 5.0, step=0.05, key="lys")
                        with col_aa2:
                            methionine = st.number_input("الميثيونين %:", 0.0, 3.0, step=0.05, key="met")
                        
                        lab_notes = st.text_area("ملاحظات إضافية:", height=80)
                        analyst_name = st.text_input("اسم المحلل:", "المختبر المركزي")
                        
                        if st.form_submit_button("💾 حفظ نتائج التحليل", type="primary"):
                            with get_db() as conn:
                                conn.execute('''
                                    UPDATE lab_analyses 
                                    SET lab_cp = ?, lab_dp = ?, lab_moisture = ?, lab_fat = ?, lab_fiber = ?,
                                        lab_me = ?, lab_ca = ?, lab_p = ?, lab_ash = ?, lysine = ?, methionine = ?,
                                        notes = ?, analyzed_by = ?, status = 'completed', analyzed_at = ?
                                    WHERE request_id = ?
                                ''', (lab_cp, lab_dp, lab_moisture, lab_fat, lab_fiber, lab_me, lab_ca, lab_p, lab_ash, lysine, methionine, lab_notes, analyst_name, datetime.now().isoformat(), req_id))
                            st.success(f"✅ تم حفظ نتائج التحليل للطلب #{req_id}")
                            log_activity("lab_results", f"نتائج تحليل #{req_id}")
                            st.rerun()
            else:
                st.info("📭 لا توجد طلبات تحليل معلقة")
        
        # تبويب سجل التحاليل
        with lab_tabs[2]:
            st.subheader("📊 سجل التحاليل المخبرية السابقة")
            
            with get_db() as conn:
                completed = conn.execute('''
                    SELECT request_id, breed, sector, city, analysis_date, 
                           lab_cp, lab_dp, lab_me, lab_moisture, lab_fat, lab_fiber, lab_ca, lab_p,
                           lysine, methionine, notes, analyzed_by, analyzed_at
                    FROM lab_analyses 
                    WHERE status = 'completed' 
                    ORDER BY analyzed_at DESC LIMIT 50
                ''').fetchall()
            
            if completed:
                for record in completed:
                    with st.expander(f"🧪 تحليل #{record['request_id']} - {record['breed']} - {record['city']} ({record['analysis_date'][:10]})"):
                        col_d1, col_d2, col_d3 = st.columns(3)
                        with col_d1:
                            st.metric("البروتين الخام", f"{record['lab_cp']:.1f}%" if record['lab_cp'] else "---")
                            st.metric("البروتين المهضوم", f"{record['lab_dp']:.1f}%" if record['lab_dp'] else "---")
                            st.metric("الرطوبة", f"{record['lab_moisture']:.1f}%" if record['lab_moisture'] else "---")
                        with col_d2:
                            st.metric("الدهن", f"{record['lab_fat']:.1f}%" if record['lab_fat'] else "---")
                            st.metric("الألياف", f"{record['lab_fiber']:.1f}%" if record['lab_fiber'] else "---")
                            st.metric("الرماد", f"{record['lab_ash']:.1f}%" if record['lab_ash'] else "---")
                        with col_d3:
                            st.metric("الطاقة الأيضية", f"{record['lab_me']:.0f}" if record['lab_me'] else "---")
                            st.metric("الكالسيوم", f"{record['lab_ca']:.2f}%" if record['lab_ca'] else "---")
                            st.metric("الفسفور", f"{record['lab_p']:.2f}%" if record['lab_p'] else "---")
                        
                        if record['lysine'] or record['methionine']:
                            st.markdown(f"**الأحماض الأمينية:** لايسين {record['lysine']:.2f}% | ميثيونين {record['methionine']:.2f}%")
                        
                        if record['notes']:
                            st.caption(f"📝 ملاحظات: {record['notes']}")
                        
                        st.caption(f"👨‍🔬 المحلل: {record['analyzed_by']} | التاريخ: {record['analyzed_at'][:16]}")
                        
                        # رسم بياني للمقارنة
                        if record['lab_cp'] and record['lab_dp']:
                            fig = go.Figure(data=[
                                go.Bar(name="النتائج المخبرية", x=["CP", "DP"], y=[record['lab_cp'], record['lab_dp']], marker_color="#2e7d32"),
                                go.Bar(name="القيم المرجعية", x=["CP", "DP"], y=[record['lab_cp']*0.9, record['lab_dp']*0.9], marker_color="#ff9800")
                            ])
                            fig.update_layout(title="مقارنة النتائج", height=300)
                            st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("لا توجد تحاليل سابقة")
        
        # تبويب التقارير
        with lab_tabs[3]:
            st.subheader("📈 تقارير المختبر")
            
            with get_db() as conn:
                stats = conn.execute('''
                    SELECT 
                        COUNT(*) as total_analyses,
                        AVG(lab_cp) as avg_cp,
                        AVG(lab_dp) as avg_dp,
                        AVG(lab_me) as avg_me,
                        AVG(lab_moisture) as avg_moisture,
                        sector,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count
                    FROM lab_analyses 
                    GROUP BY sector
                ''').fetchall()
            
            if stats:
                st.markdown("#### 📊 إحصائيات التحاليل حسب القطاع")
                stats_df = pd.DataFrame([dict(s) for s in stats])
                st.dataframe(stats_df, use_container_width=True)
                
                # رسم بياني
                fig = go.Figure(data=[
                    go.Bar(name="متوسط البروتين", x=stats_df['sector'], y=stats_df['avg_cp'], marker_color="#2e7d32"),
                    go.Bar(name="متوسط الطاقة", x=stats_df['sector'], y=stats_df['avg_me'], marker_color="#ff9800")
                ])
                fig.update_layout(title="متوسط القيم حسب القطاع", height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("لا توجد بيانات كافية لإحصائيات المختبر")

# ==========================================
# التبويب 7: التحليلات المتقدمة
# ==========================================

analytics_index = 6 if st.session_state.get("user_role") == "owner" else (5 if st.session_state.get("user_role") == "specialist" else None)

if analytics_index is not None and len(tabs) > analytics_index:
    with tabs[analytics_index]:
        st.markdown('<div class="section-title">📈 لوحة التحليلات المتقدمة</div>', unsafe_allow_html=True)
        
        # إحصائيات سريعة
        with get_db() as conn:
            # إجمالي الخلطات
            cursor = conn.execute('SELECT COUNT(*) as count FROM formulas_history')
            total_formulas = cursor.fetchone()['count']
            st.metric("📝 إجمالي الخلطات المنشأة", total_formulas)
            
            # متوسط التكلفة
            cursor = conn.execute('SELECT AVG(cost) as avg_cost FROM formulas_history')
            avg_cost = cursor.fetchone()['avg_cost']
            st.metric("💰 متوسط التكلفة", f"${avg_cost:.2f}" if avg_cost else "$0")
            
            # إجمالي الزوار
            cursor = conn.execute('SELECT COUNT(DISTINCT ip_address) as count FROM visitors_log')
            st.metric("👥 إجمالي الزوار", cursor.fetchone()['count'])
            
            # عدد التحاليل
            cursor = conn.execute('SELECT COUNT(*) as count FROM lab_analyses WHERE status = "completed"')
            st.metric("🔬 التحاليل المخبرية", cursor.fetchone()['count'])
        
        st.markdown("---")
        
        # رسم بياني لتوزيع الخلطات حسب القطاع
        with get_db() as conn:
            cursor = conn.execute('SELECT sector, COUNT(*) as count FROM formulas_history GROUP BY sector ORDER BY count DESC')
            sectors = cursor.fetchall()
            if sectors:
                sector_df = pd.DataFrame([dict(s) for s in sectors])
                fig = px.pie(sector_df, values='count', names='sector', title="توزيع الخلطات حسب القطاع", color_discrete_sequence=px.colors.sequential.Greens_r)
                st.plotly_chart(fig, use_container_width=True)
        
        # رسم بياني لتوزيع الخلطات حسب السلالة
        with get_db() as conn:
            cursor = conn.execute('SELECT breed, COUNT(*) as count FROM formulas_history GROUP BY breed ORDER BY count DESC LIMIT 10')
            breeds = cursor.fetchall()
            if breeds:
                breed_df = pd.DataFrame([dict(b) for b in breeds])
                fig = px.bar(breed_df, x="breed", y="count", title="الخلطات حسب السلالة (أعلى 10)", color_discrete_sequence=["#2e7d32"])
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # اتجاه التكلفة
        with get_db() as conn:
            cursor = conn.execute('SELECT cost, created_at FROM formulas_history ORDER BY created_at DESC LIMIT 30')
            costs = cursor.fetchall()
            if costs:
                cost_df = pd.DataFrame([{"التاريخ": c['created_at'][:16], "التكلفة": c['cost']} for c in reversed(costs)])
                fig = px.line(cost_df, x="التاريخ", y="التكلفة", title="اتجاه تكلفة الخلطات (آخر 30 خلطة)", markers=True)
                fig.update_traces(line_color='#2e7d32', line_width=2)
                st.plotly_chart(fig, use_container_width=True)

# ==========================================
# التبويب 8: لوحة تحكم المالك (للمالك فقط)
# ==========================================

if st.session_state.get("user_role") == "owner" and len(tabs) > 7:
    with tabs[7]:
        st.markdown('<div class="section-title">👑 لوحة تحكم المالك المتقدمة</div>', unsafe_allow_html=True)
        
        admin_tabs = st.tabs(["📊 الإحصائيات", "💾 النسخ الاحتياطي", "🔐 الأمان", "👥 الزوار", "⚙️ الإعدادات"])
        
        with admin_tabs[0]:
            with get_db() as conn:
                cursor = conn.execute('SELECT COUNT(*) as count FROM formulas_history')
                st.metric("الخلطات المنشأة", cursor.fetchone()['count'])
                cursor = conn.execute('SELECT COUNT(*) as count FROM visitors_log')
                st.metric("إجمالي الزوار", cursor.fetchone()['count'])
                cursor = conn.execute('SELECT COUNT(*) as count FROM security_alerts')
                st.metric("التنبيهات الأمنية", cursor.fetchone()['count'])
                cursor = conn.execute('SELECT COUNT(*) as count FROM lab_analyses')
                st.metric("طلبات التحليل", cursor.fetchone()['count'])
        
        with admin_tabs[1]:
            st.subheader("💾 إدارة النسخ الاحتياطية")
            
            col_back1, col_back2 = st.columns(2)
            with col_back1:
                if st.button("📀 إنشاء نسخة احتياطية وإرسالها للمالك", use_container_width=True, type="primary"):
                    with st.spinner("جاري الإنشاء والإرسال..."):
                        if CODE_SENDER.send_code_to_email(OWNER_EMAIL, "نسخة يدوية من لوحة المالك"):
                            st.success("✅ تم إنشاء وإرسال النسخة الاحتياطية بنجاح")
                        else:
                            st.error("❌ فشل إرسال النسخة")
            
            with col_back2:
                backup_reason = st.text_input("سبب النسخة الاحتياطية:", "نسخة يدوية")
                if st.button("📧 إرسال الكود مع سبب", use_container_width=True):
                    CODE_SENDER.send_code_to_email(OWNER_EMAIL, backup_reason)
                    st.success("تم الإرسال")
            
            st.info("💡 يتم إنشاء نسخ احتياطية تلقائياً كل 6 ساعات")
        
        with admin_tabs[2]:
            st.subheader("🔐 سجل الأمان")
            
            with get_db() as conn:
                cursor = conn.execute('SELECT * FROM security_alerts ORDER BY created_at DESC LIMIT 30')
                alerts = cursor.fetchall()
                if alerts:
                    for alert in alerts:
                        st.markdown(f"- {alert['created_at'][:19]}: {alert['alert_message'][:100]}")
                else:
                    st.info("لا توجد تنبيهات أمنية")
        
        with admin_tabs[3]:
            st.subheader("👥 سجل الزوار")
            
            with get_db() as conn:
                cursor = conn.execute('SELECT ip_address, user_role, action, visit_time FROM visitors_log ORDER BY visit_time DESC LIMIT 100')
                visitors = cursor.fetchall()
                if visitors:
                    visitors_df = pd.DataFrame([dict(v) for v in visitors])
                    st.dataframe(visitors_df, use_container_width=True, height=400)
                    
                    # إحصائيات الزوار
                    st.markdown("#### 📊 إحصائيات الزوار")
                    col_v1, col_v2 = st.columns(2)
                    with col_v1:
                        st.metric("الزوار الفريدون", visitors_df['ip_address'].nunique())
                    with col_v2:
                        st.metric("آخر زائر", visitors_df['visit_time'].iloc[0][:16] if len(visitors_df) > 0 else "---")
                else:
                    st.info("لا توجد بيانات زوار")
        
        with admin_tabs[4]:
            st.subheader("⚙️ إعدادات النظام")
            
            # عرض معلومات النظام
            st.markdown("#### ℹ️ معلومات النظام")
            col_sys1, col_sys2, col_sys3 = st.columns(3)
            with col_sys1:
                st.metric("إصدار المنصة", "6.0")
            with col_sys2:
                st.metric("عدد المواد العلفية", len(BIG_FEEDS_LIBRARY))
            with col_sys3:
                st.metric("عدد السلالات", sum(len(v) for v in BREEDS_STANDARDS.values()))
            
            st.markdown("#### 🗑️ إدارة البيانات")
            if st.button("🧹 تنظيف قاعدة البيانات (حذف السجلات القديمة)", use_container_width=True):
                with get_db() as conn:
                    # حذف السجلات الأقدم من 90 يوماً
                    conn.execute("DELETE FROM activity_logs WHERE created_at < date('now', '-90 days')")
                    conn.execute("DELETE FROM visitors_log WHERE visit_time < date('now', '-90 days')")
                st.success("✅ تم تنظيف قاعدة البيانات")

# ==========================================
# التبويب 9: التعليقات
# ==========================================

comments_index = 8 if st.session_state.get("user_role") == "owner" else (6 if st.session_state.get("user_role") == "specialist" else 1)

if comments_index < len(tabs):
    with tabs[comments_index]:
        st.markdown('<div class="section-title">💬 تعليقات المختصين والمربين</div>', unsafe_allow_html=True)
        
        # عرض التعليقات الحالية
        st.markdown("#### 📝 التعليقات السابقة")
        st.text_area("التعليقات الحالية:", st.session_state["shared_comments"], height=200, disabled=True)
        
        st.markdown("---")
        
        # إضافة تعليق جديد
        st.markdown("#### ✍️ أضف تعليقاً جديداً")
        new_comment = st.text_area("تعليقك:", height=100, placeholder="اكتب تعليقك هنا...")
        
        col_comment1, col_comment2 = st.columns(2)
        with col_comment1:
            if st.button("📌 نشر التعليق", use_container_width=True, type="primary"):
                if new_comment.strip():
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    role_name = "👑 المالك" if st.session_state["user_role"] == "owner" else "🔬 مختص" if st.session_state["user_role"] == "specialist" else "🌾 مربي"
                    st.session_state["shared_comments"] = f"• [{role_name} - {timestamp}]: {new_comment.strip()}\n" + st.session_state["shared_comments"]
                    st.success("✅ تم نشر التعليق")
                    log_activity("add_comment", f"تعليق جديد: {new_comment[:100]}")
                    st.rerun()
        
        with col_comment2:
            if st.button("🗑️ مسح جميع التعليقات", use_container_width=True):
                if st.session_state.get("user_role") == "owner":
                    st.session_state["shared_comments"] = "• تم مسح التعليقات بواسطة المالك\n"
                    st.success("تم مسح التعليقات")
                    st.rerun()
                else:
                    st.warning("⚠️ فقط المالك يمكنه مسح جميع التعليقات")

# ==========================================
# التبويب الأخير: الدليل
# ==========================================

with tabs[-1]:
    st.markdown('<div class="section-title">📖 دليل المستخدم والتقانة الفنية</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background:#f5f5f5; padding:25px; border-radius:15px;">
    <h3>📌 دليل استخدام منصة تاور العلمية v6.0</h3>
    
    <h4>🔑 أكواد الدخول:</h4>
    <p>- 👑 <b>المالك (كامل الصلاحيات)</b>: <code style="background:#1b5e20;color:white;padding:2px 8px;border-radius:5px;">202687</code><br>
    - 🔬 <b>المختصون والزملاء</b>: <code style="background:#1b5e20;color:white;padding:2px 8px;border-radius:5px;">2020</code><br>
    - 🌾 <b>المربون</b>: <code style="background:#1b5e20;color:white;padding:2px 8px;border-radius:5px;">2026</code></p>
    
    <h4>📧 إرسال الكود للمالك:</h4>
    <p>يوجد زر أحمر بارز في أعلى الصفحة لإرسال نسخة كاملة من الكود إلى بريد المالك الإلكتروني.<br>
    كما توجد أزرار إضافية في لوحة المالك وفي الشريط الجانبي.</p>
    
    <h4>🇸🇩 الأعلام حسب الدولة:</h4>
    <p>تم إضافة أعلام الدول: 🇸🇩 السودان، 🇱🇾 ليبيا، 🇪🇬 مصر، 🇸🇦 السعودية، 🇦🇪 الإمارات، 🇶🇦 قطر، 🇰🇼 الكويت، 🇴🇲 عمان، 🇧🇭 البحرين، 🇯🇴 الأردن، 🇲🇦 المغرب، 🇩🇿 الجزائر، 🇹🇳 تونس.</p>
    
    <h4>📊 شريط قياس البروتين والطاقة:</h4>
    <p>- يمكنك اختيار بين <b>البروتين المهضوم (DP)</b> أو <b>البروتين الخام (CP)</b><br>
    - يمكنك الاختيار بين <b>القيم القياسية (حسب السلالة)</b> أو <b>القيم البرمجية (تحديد يدوي)</b><br>
    - يظهر شريط ملون للمقارنة مع المعدل القياسي (أخضر/أصفر/أحمر)<br>
    - يتم حساب <b>معامل البروتين/طاقة (P/E)</b> تلقائياً<br>
    - يتم حساب <b>الطاقة الأيضية المتوقعة (ME)</b> من البروتين</p>
    
    <h4>📈 تحديث الأسعار:</h4>
    <p>يتم تحديث أسعار البورصة <b>مرة واحدة كل 24 ساعة</b> فقط للحفاظ على استقرار النظام وعدم التأثير على نشاط المنصة.<br>
    يمكنك تحديث الأسعار يدوياً عبر زر "تحديث الأسعار الآن".</p>
    
    <h4>⚙️ طريقة استخدام محرك تركيب الأعلاف:</h4>
    <p>1. حدد <b>الدولة والمدينة</b> (يتم تحديث الأسعار يومياً)<br>
    2. اختر <b>القطاع الحيواني</b> (دواجن/أغنام/ماعز/أبقار/خيول/أسماك)<br>
    3. اختر <b>السلالة ومرحلة الإنتاج</b><br>
    4. حدد <b>نوع البروتين ومصدر القيم</b> (قياسي/برمجي)<br>
    5. حرك <b>شريط القياس</b> لتحديد النسب المطلوبة<br>
    6. اختر <b>المكونات العلفية</b> المناسبة (اختر 3 مكونات على الأقل)<br>
    7. اضغط <b>"تشغيل محرك الاستمثال الخطي"</b> للحصول على التركيبة المثلى بأقل تكلفة</p>
    
    <h4>🔬 المختبر المتكامل:</h4>
    <p>- <b>إنشاء طلبات تحليل</b> جديدة مع حفظ بيانات الخلطة<br>
    - <b>إدخال نتائج التحليل الفعلية</b> (CP, DP, ME, رطوبة، دهن، ألياف، كالسيوم، فسفور، أحماض أمينية)<br>
    - <b>عرض سجل التحاليل</b> مع مقارنة رسومية بين النتائج والقيم المرجعية<br>
    - <b>تقارير المختبر</b> وإحصائيات حسب القطاع</p>
    
    <h4>🏭 إدارة المخزون:</h4>
    <p>- متابعة كميات المواد العلفية<br>
    - تنبيهات للمواد منخفضة المخزون أو النافدة<br>
    - بحث سريع عن المواد<br>
    - تعديل الكميات والحدود الدنيا</p>
    
    <h4>🐔 إدارة مزارع الدواجن:</h4>
    <p>- إضافة مزارع متعددة (لاحم/بياض/سمان/رومي)<br>
    - تسجيل بيانات يومية (العمر، النافق، استهلاك العلف، الوزن)<br>
    - حساب مؤشرات الأداء (FCR, ADG, نسبة النفوق, EPEF)<br>
    - جدول درجة الحرارة والرطوبة الموصى بها</p>
    
    <h4>🧾 نظام الفواتير:</h4>
    <p>- إنشاء فواتير بيع مع خصم تلقائي من المخزون<br>
    - دعم العملات المحلية (SDG, LYD, EGP, SAR, AED, ...)<br>
    - تحميل الفاتورة كملف نصي<br>
    - مشاركة الفاتورة عبر واتساب</p>
    
    <h4>📈 التحليلات المتقدمة:</h4>
    <p>- رسوم بيانية تفاعلية لتوزيع الخلطات حسب القطاع والسلالة<br>
    - اتجاه تكلفة الخلطات مع مرور الوقت<br>
    - إحصائيات المختبر وتحليل النتائج</p>
    
    <h4>🔐 الأمان والحماية:</h4>
    <p>- نظام تسجيل متقدم لجميع الأنشطة<br>
    - مراقبة محاولات الدخول الفاشلة وحظر IP<br>
    - تسجيل جميع الزوار مع عناوين IP<br>
    - تنبيهات أمنية للمالك</p>
    
    <h4>📞 التواصل والدعم الفني:</h4>
    <p>📱 <b>واتساب</b>: <a href="https://wa.me/249123533489" target="_blank">+249 123 533 489</a><br>
    📧 <b>البريد الإلكتروني</b>: <a href="mailto:abukram128@gmail.com">abukram128@gmail.com</a><br>
    🌐 <b>المنصة</b>: <a href="https://tower-scientific-platform.streamlit.app" target="_blank">tower-scientific-platform.streamlit.app</a></p>
    
    <hr>
    <p style="text-align:center;">تم التطوير بواسطة <b>الاختصاصي م. عبد القادر إسماعيل تاور</b> © 2026</p>
    <p style="text-align:center;">الإصدار 6.0 - مع شريط القياس المتقدم، المختبر المتكامل، تحديث يومي للأسعار، وأعلام الدول</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# تذييل الصفحة
# ==========================================

st.markdown("<hr>", unsafe_allow_html=True)

col_f1, col_f2, col_f3, col_f4 = st.columns(4)

with col_f1:
    if st.button("💾 نسخ احتياطي الآن", use_container_width=True):
        with st.spinner("جاري الإنشاء والإرسال..."):
            if CODE_SENDER.send_code_to_email(OWNER_EMAIL, "نسخة فورية من التذييل"):
                st.success("✅ تم إرسال النسخة إلى بريد المالك")
            else:
                st.error("❌ فشل الإرسال")

with col_f2:
    share_text = "🌾 منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف - منصة متكاملة لتركيب الأعلاف بأقل تكلفة باستخدام الذكاء الاصطناعي"
    encoded = urllib.parse.quote(share_text)
    st.link_button("📢 مشاركة المنصة", f"https://wa.me/?text={encoded}", use_container_width=True)

with col_f3:
    st.markdown(f"<p style='text-align:center;'>© 2026 منصة تاور العلمية</p>", unsafe_allow_html=True)

with col_f4:
    st.markdown(f"<p style='text-align:center;'>الإصدار 6.0</p>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# النسخ الاحتياطي التلقائي للمالك
# ==========================================

if st.session_state.get("user_role") == "owner":
    CODE_SENDER.auto_backup_check()

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
st.sidebar.markdown(f"- **الإصدار:** 6.0")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📧 إرسال الكود")

if st.sidebar.button("📧 إرسال الكود للمالك", use_container_width=True):
    with st.spinner("جاري الإرسال..."):
        CODE_SENDER.send_code_to_email(OWNER_EMAIL, "طلب من الشريط الجانبي")
        st.success("تم الإرسال")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 روابط سريعة")
st.sidebar.markdown("[📞 واتساب الدعم](https://wa.me/249123533489)")
st.sidebar.markdown("[📧 البريد الإلكتروني](mailto:abukram128@gmail.com)")

# ==========================================
# نهاية الكود
# ==========================================
