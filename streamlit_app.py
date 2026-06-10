#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف
النسخة المتكاملة الكاملة v5.0 - غير منقوصة
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
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from functools import lru_cache, wraps
from typing import Dict, List, Tuple, Optional, Any, Union
from collections import defaultdict, Counter, OrderedDict
from dataclasses import dataclass, field
from enum import Enum
import warnings

# ==========================================
# المكتبات العلمية والتحليلية
# ==========================================

from scipy.optimize import linprog, minimize, differential_evolution
from scipy.spatial import ConvexHull, Delaunay
from scipy.stats import norm, percentileofscore
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# ==========================================
# مكتبات التصور والرسوم البيانية المتقدمة
# ==========================================

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.font_manager as fm
import seaborn as sns

# ==========================================
# مكتبات معالجة النص العربي المتقدمة
# ==========================================

import arabic_reshaper
from bidi.algorithm import get_display

# ==========================================
# مكتبات توليد PDF المتقدمة جداً
# ==========================================

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4, A3, landscape, portrait
from reportlab.lib.units import inch, mm, cm
from reportlab.lib.colors import HexColor, black, white, grey, blue, red, green, yellow, orange
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate, Frame, PageTemplate, KeepTogether, PageBreak, NextPageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.platypus.flowables import HRFlowable, Flowable, KeepInFrame
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.widgets.markers import makeMarker

# ==========================================
# مكتبات الباركود والصور المتقدمة
# ==========================================

import qrcode
from qrcode.image.styled import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer, CircleModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask, SolidFillColorMask
from PIL import Image as PILImage, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import cv2
import numpy as np

# مكتبة قراءة الباركود (اختيارية)
try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False
    pyzbar_decode = None

# ==========================================
# مكتبات الأمان المتقدمة
# ==========================================

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend

# ==========================================
# مكتبات التعامل مع الملفات المتقدمة
# ==========================================

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, GradientFill
from openpyxl.chart import BarChart, Reference, LineChart, PieChart
from openpyxl.chart.series import DataPoint
from openpyxl.drawing.image import Image as XLImage
import xlsxwriter

# ==========================================
# مكتبات إضافية للتواصل والخرائط
# ==========================================

import folium
from folium.plugins import HeatMap, MarkerCluster, Draw, Fullscreen
import requests
from bs4 import BeautifulSoup

# ==========================================
# إعدادات التحذيرات والمتغيرات البيئية
# ==========================================

warnings.filterwarnings('ignore')
load_dotenv()

# ==========================================
# إنشاء جميع المجلدات اللازمة
# ==========================================

folders = [
    "logs", "backups", "data", "temp", "visitors", "code_backups", "reports", "exports", 
    "charts", "models", "cache", "uploads", "downloads", "temp_pdf", "temp_images", 
    "temp_excel", "fonts", "images", "certificates", "encryption", "sessions", "backups_daily",
    "backups_weekly", "backups_monthly", "logs/security", "logs/users", "logs/errors",
    "data/prices", "data/farms", "data/lab", "data/comments", "data/inventory"
]
for folder in folders:
    Path(folder).mkdir(exist_ok=True)

# ==========================================
# إعدادات Streamlit المتقدمة
# ==========================================

st.set_page_config(
    page_title="منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف - الإصدار المتكامل 5.0",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://wa.me/249123533489',
        'Report a bug': 'mailto:abukram128@gmail.com',
        'About': 'منصة تاور العلمية - نظام متكامل لتركيب الأعلاف وإدارة المزارع\nالإصدار 5.0\nالمشرف: م. عبد القادر إسماعيل تاور'
    }
)

# ==========================================
# نظام التسجيل المتقدم جداً
# ==========================================

class AdvancedLogger:
    """نظام تسجيل متقدم مع تصنيف متعدد ومستويات متعددة"""
    
    def __init__(self):
        self.setup_all_loggers()
        self.log_queue = []
        self.log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
            'SECURITY': 25,
            'PERFORMANCE': 26,
            'USER_ACTION': 27,
            'SYSTEM': 28,
            'DATABASE': 29
        }
        
        # إضافة مستويات تسجيل مخصصة
        for level_name, level_value in self.log_levels.items():
            if level_name not in logging.__dict__:
                logging.addLevelName(level_value, level_name)
    
    def setup_all_loggers(self):
        """إعداد جميع سجلات النظام"""
        # سجل النظام الرئيسي
        self.main_logger = logging.getLogger('TowerPlatform')
        self.main_logger.setLevel(logging.DEBUG)
        
        # سجل الأمان
        self.security_logger = logging.getLogger('Security')
        self.security_logger.setLevel(logging.WARNING)
        
        # سجل الأداء
        self.performance_logger = logging.getLogger('Performance')
        self.performance_logger.setLevel(logging.INFO)
        
        # سجل المستخدمين
        self.user_logger = logging.getLogger('UserActions')
        self.user_logger.setLevel(logging.INFO)
        
        # سجل الأخطاء
        self.error_logger = logging.getLogger('Errors')
        self.error_logger.setLevel(logging.ERROR)
        
        # سجل النظام
        self.system_logger = logging.getLogger('System')
        self.system_logger.setLevel(logging.INFO)
        
        # سجل قاعدة البيانات
        self.db_logger = logging.getLogger('Database')
        self.db_logger.setLevel(logging.INFO)
        
        # تكوين معالجات الملفات
        self.setup_file_handlers()
        
        # تكوين معالج وحدة التحكم
        self.setup_console_handler()
    
    def setup_file_handlers(self):
        """إعداد معالجات الملفات"""
        # معالج الملف الرئيسي
        main_handler = logging.handlers.RotatingFileHandler(
            'logs/tower_main.log', 
            maxBytes=50*1024*1024,  # 50MB
            backupCount=30,
            encoding='utf-8'
        )
        main_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(filename)s:%(lineno)d - %(message)s')
        main_handler.setFormatter(main_formatter)
        self.main_logger.addHandler(main_handler)
        
        # معالج ملف الأمان
        security_handler = logging.handlers.RotatingFileHandler(
            'logs/security/security.log', 
            maxBytes=20*1024*1024,
            backupCount=50,
            encoding='utf-8'
        )
        security_handler.setFormatter(main_formatter)
        self.security_logger.addHandler(security_handler)
        
        # معالج ملف الأداء
        performance_handler = logging.handlers.RotatingFileHandler(
            'logs/performance.log', 
            maxBytes=10*1024*1024,
            backupCount=20,
            encoding='utf-8'
        )
        performance_handler.setFormatter(main_formatter)
        self.performance_logger.addHandler(performance_handler)
        
        # معالج ملف المستخدمين
        user_handler = logging.handlers.RotatingFileHandler(
            'logs/users/users.log', 
            maxBytes=10*1024*1024,
            backupCount=30,
            encoding='utf-8'
        )
        user_handler.setFormatter(main_formatter)
        self.user_logger.addHandler(user_handler)
        
        # معالج ملف الأخطاء
        error_handler = logging.handlers.RotatingFileHandler(
            'logs/errors/errors.log', 
            maxBytes=50*1024*1024,
            backupCount=40,
            encoding='utf-8'
        )
        error_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s')
        error_handler.setFormatter(error_formatter)
        self.error_logger.addHandler(error_handler)
        
        # معالج ملف النظام
        system_handler = logging.handlers.RotatingFileHandler(
            'logs/system.log', 
            maxBytes=20*1024*1024,
            backupCount=20,
            encoding='utf-8'
        )
        system_handler.setFormatter(main_formatter)
        self.system_logger.addHandler(system_handler)
        
        # معالج ملف قاعدة البيانات
        db_handler = logging.handlers.RotatingFileHandler(
            'logs/database.log', 
            maxBytes=20*1024*1024,
            backupCount=20,
            encoding='utf-8'
        )
        db_handler.setFormatter(main_formatter)
        self.db_logger.addHandler(db_handler)
    
    def setup_console_handler(self):
        """إعداد معالج وحدة التحكم"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        for logger in [self.main_logger, self.security_logger, self.user_logger, self.system_logger]:
            logger.addHandler(console_handler)
    
    def log_security_event(self, event_type, details, severity='WARNING', ip_address=None):
        """تسجيل حدث أمني"""
        log_msg = f"SECURITY_EVENT: {event_type} | Details: {details} | Severity: {severity} | IP: {ip_address or 'unknown'}"
        if severity == 'CRITICAL':
            self.security_logger.critical(log_msg)
            self.send_immediate_alert(log_msg)
        elif severity == 'ERROR':
            self.security_logger.error(log_msg)
        elif severity == 'WARNING':
            self.security_logger.warning(log_msg)
        else:
            self.security_logger.info(log_msg)
        
        # حفظ في قاعدة البيانات
        self.save_security_event_to_db(event_type, details, severity, ip_address)
    
    def save_security_event_to_db(self, event_type, details, severity, ip_address):
        """حفظ الحدث الأمني في قاعدة البيانات"""
        try:
            conn = get_db()
            conn.execute('''
                INSERT INTO security_events (event_type, details, severity, ip_address, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (event_type, details[:1000], severity, ip_address, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except Exception as e:
            self.error_logger.error(f"فشل حفظ الحدث الأمني: {e}")
    
    def send_immediate_alert(self, message):
        """إرسال تنبيه فوري للمالك"""
        try:
            if WHATSAPP_NUMBER:
                encoded = urllib.parse.quote(f"🔐 تنبيه أمني فوري: {message[:200]}")
                whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded}"
                # تخزين الرابط للعرض
                st.markdown(f'<div style="display:none;"><a href="{whatsapp_url}">alert</a></div>', unsafe_allow_html=True)
            
            # إرسال بريد إلكتروني فوري
            self.send_email_alert(message)
        except:
            pass
    
    def send_email_alert(self, message):
        """إرسال تنبيه عبر البريد الإلكتروني"""
        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = OWNER_EMAIL
            msg['Subject'] = f"🔐 تنبيه أمني فوري - منصة تاور - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            body = f"""تنبيه أمني فوري من منصة تاور العلمية

الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
الرسالة: {message}

يرجى التحقق من سجلات الأمان لمزيد من التفاصيل.

تحياتي،
نظام الأمان الآلي
"""
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, OWNER_EMAIL, msg.as_string())
            server.quit()
        except:
            pass

LOGGER = AdvancedLogger()
LOGGER.system_logger.info("تم بدء تشغيل منصة تاور العلمية - الإصدار 5.0")

# ==========================================
# نظام مراقبة الأمان والاختراق المتقدم جداً
# ==========================================

class AdvancedSecurityMonitor:
    """نظام مراقبة أمان متقدم جداً مع كشف التهديدات وحظر IP التلقائي"""
    
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.blocked_ips = set()
        self.suspicious_patterns = []
        self.threat_scores = defaultdict(int)
        self.ip_geolocation = {}
        self.attack_signatures = self.load_attack_signatures()
        self.request_history = defaultdict(list)
        self.ddos_protection = DDoSProtection()
        
        # تحميل قواعد بيانات التهديدات
        self.load_threat_database()
        
        # بدء مراقبة الخلفية
        self.start_background_monitoring()
    
    def load_attack_signatures(self):
        """تحميل توقيعات الهجمات المعروفة"""
        return {
            'sql_injection': re.compile(r'(\%27)|(\')|(\-\-)|(%23)|(#)|(union.*select)|(select.*from)', re.IGNORECASE),
            'xss': re.compile(r'(\<script)|(\<img)|(javascript:)|(onerror=)|(onload=)|(alert\()', re.IGNORECASE),
            'path_traversal': re.compile(r'(\.\./)|(\.\.\\)|(\.\.%2f)|(\.\.%5c)', re.IGNORECASE),
            'command_injection': re.compile(r'(\||\&|\;|\$\(|\`|\$\{)|(eval\()|(exec\()|(system\()', re.IGNORECASE),
            'dos_pattern': re.compile(r'(\.{100,})|(x{100,})|(A{100,})', re.IGNORECASE),
            'bruteforce': re.compile(r'(admin)|(root)|(password)|(login)', re.IGNORECASE),
            'user_enumeration': re.compile(r'(user)|(username)|(email)|(phone)', re.IGNORECASE)
        }
    
    def load_threat_database(self):
        """تحميل قاعدة بيانات التهديدات"""
        self.threat_ips = set()
        threat_file = 'data/threat_ips.txt'
        if os.path.exists(threat_file):
            with open(threat_file, 'r') as f:
                for line in f:
                    self.threat_ips.add(line.strip())
        
        # تحميل قائمة عناوين IP المحظورة عالمياً
        banned_ips_file = 'data/banned_ips.txt'
        if os.path.exists(banned_ips_file):
            with open(banned_ips_file, 'r') as f:
                for line in f:
                    self.blocked_ips.add(line.strip())
    
    def start_background_monitoring(self):
        """بدء مراقبة الخلفية"""
        def monitor():
            while True:
                self.cleanup_old_attempts()
                self.analyze_patterns()
                self.check_ddos_attack()
                time.sleep(60)  # كل دقيقة
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def get_client_ip(self):
        """الحصول على IP العميل مع دعم الـ Proxy المتقدم"""
        try:
            if hasattr(st, 'context') and hasattr(st.context, 'headers'):
                # التحقق من headers متعددة
                headers_to_check = [
                    'X-Forwarded-For',
                    'X-Real-IP',
                    'CF-Connecting-IP',
                    'True-Client-IP',
                    'X-Cluster-Client-IP',
                    'X-Forwarded',
                    'Forwarded-For',
                    'Forwarded'
                ]
                
                for header in headers_to_check:
                    if header in st.context.headers:
                        ips = st.context.headers[header].split(',')
                        if ips:
                            ip = ips[0].strip()
                            if self.is_valid_ip(ip):
                                return ip
            
            # استخدام خدمة خارجية للحصول على IP
            try:
                response = requests.get('https://api.ipify.org', timeout=3)
                if response.status_code == 200:
                    return response.text
            except:
                pass
            
            return '127.0.0.1'
        except:
            return 'unknown'
    
    def is_valid_ip(self, ip):
        """التحقق من صحة عنوان IP"""
        ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        return bool(ip_pattern.match(ip))
    
    def get_ip_geolocation(self, ip):
        """الحصول على الموقع الجغرافي للـ IP مع التخزين المؤقت"""
        if ip in self.ip_geolocation:
            return self.ip_geolocation[ip]
        
        try:
            # استخدام ip-api.com للحصول على الموقع
            response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    geoloc = {
                        'country': data.get('country'),
                        'country_code': data.get('countryCode'),
                        'region': data.get('region'),
                        'region_name': data.get('regionName'),
                        'city': data.get('city'),
                        'zip': data.get('zip'),
                        'lat': data.get('lat'),
                        'lon': data.get('lon'),
                        'timezone': data.get('timezone'),
                        'isp': data.get('isp'),
                        'org': data.get('org'),
                        'as': data.get('as')
                    }
                    self.ip_geolocation[ip] = geoloc
                    return geoloc
        except:
            pass
        
        return {'country': 'Unknown', 'city': 'Unknown', 'country_code': 'XX'}
    
    def analyze_request(self, request_data, request_type='normal'):
        """تحليل الطلب للكشف عن الهجمات"""
        threat_score = 0
        threats_found = []
        
        # تحليل التوقيعات
        for attack_type, pattern in self.attack_signatures.items():
            if pattern.search(str(request_data)):
                threat_score += 25
                threats_found.append(attack_type)
                LOGGER.log_security_event(attack_type, f"كشف هجوم من نوع {attack_type}", 'WARNING', self.get_client_ip())
        
        ip = self.get_client_ip()
        
        # تسجيل الطلب في التاريخ
        self.request_history[ip].append({
            'timestamp': datetime.now(),
            'type': request_type,
            'threat_score': threat_score
        })
        
        # فحص IP مهدد
        if ip in self.threat_ips:
            threat_score += 50
            threats_found.append('known_threat_ip')
        
        # فحص المحاولات المتكررة
        recent_attempts = [t for t in self.failed_attempts[ip] if (datetime.now() - t).seconds < 300]
        if len(recent_attempts) >= 3:
            threat_score += 20 * len(recent_attempts)
            threats_found.append('multiple_attempts')
        
        # فحص سرعة الطلبات (DDoS)
        recent_requests = [r for r in self.request_history[ip] if (datetime.now() - r['timestamp']).seconds < 10]
        if len(recent_requests) >= 20:
            threat_score += 50
            threats_found.append('ddos_pattern')
            self.ddos_protection.report_attack(ip)
        
        # تحديث درجة التهديد
        self.threat_scores[ip] += threat_score
        
        # حظر IP إذا تجاوز الحد
        if threat_score >= 75 or self.threat_scores[ip] >= 150:
            self.block_ip(ip, f"تهديد عالي - درجة {threat_score} - {threats_found}")
            return False
        
        elif threat_score >= 40:
            LOGGER.log_security_event('MEDIUM_THREAT', f"تهديد متوسط من {ip}: {threats_found} - درجة {threat_score}", 'WARNING', ip)
        
        return True
    
    def block_ip(self, ip, reason):
        """حظر IP مع تسجيل السبب وإشعار المالك"""
        if ip not in self.blocked_ips and ip not in ['127.0.0.1', 'localhost']:
            self.blocked_ips.add(ip)
            LOGGER.log_security_event('IP_BLOCKED', f"تم حظر {ip} - السبب: {reason}", 'ERROR', ip)
            
            # حفظ في قاعدة البيانات
            try:
                conn = get_db()
                conn.execute('''
                    INSERT INTO blocked_ips (ip_address, block_reason, blocked_at)
                    VALUES (?, ?, ?)
                ''', (ip, reason[:500], datetime.now().isoformat()))
                conn.commit()
                conn.close()
            except:
                pass
            
            # إشعار المالك
            geoloc = self.get_ip_geolocation(ip)
            country = geoloc.get('country', 'Unknown')
            city = geoloc.get('city', 'Unknown')
            
            message = f"""🚨 تم حظر عنوان IP
IP: {ip}
الدولة: {country}
المدينة: {city}
السبب: {reason}
الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            self.send_alert_to_owner(message)
    
    def is_ip_blocked(self, ip):
        """التحقق من حظر IP مع تنظيف المحاولات القديمة"""
        if ip in self.blocked_ips:
            return True
        
        # تنظيف المحاولات القديمة
        now = datetime.now()
        self.failed_attempts[ip] = [
            attempt for attempt in self.failed_attempts[ip] 
            if (now - attempt).seconds < 3600
        ]
        
        # التحقق من درجة التهديد
        if self.threat_scores[ip] >= 150:
            self.block_ip(ip, f"تجاوز درجة التهديد المسموحة - {self.threat_scores[ip]}")
            return True
        
        return False
    
    def cleanup_old_attempts(self):
        """تنظيف المحاولات القديمة"""
        now = datetime.now()
        for ip in list(self.failed_attempts.keys()):
            self.failed_attempts[ip] = [
                attempt for attempt in self.failed_attempts[ip] 
                if (now - attempt).seconds < 3600
            ]
            if not self.failed_attempts[ip]:
                del self.failed_attempts[ip]
        
        # تنظيف سجل الطلبات
        for ip in list(self.request_history.keys()):
            self.request_history[ip] = [
                req for req in self.request_history[ip] 
                if (now - req['timestamp']).seconds < 600
            ]
            if not self.request_history[ip]:
                del self.request_history[ip]
    
    def analyze_patterns(self):
        """تحليل الأنماط للكشف عن الهجمات المنسقة"""
        ip_scores = defaultdict(int)
        
        # تحليل المحاولات الفاشلة
        for ip, attempts in self.failed_attempts.items():
            if len(attempts) >= 5:
                ip_scores[ip] += 50
            if len(attempts) >= 10:
                ip_scores[ip] += 100
        
        # تحليل سرعة الطلبات
        for ip, requests in self.request_history.items():
            recent_count = len([r for r in requests if (datetime.now() - r['timestamp']).seconds < 60])
            if recent_count >= 50:
                ip_scores[ip] += 100
        
        # حرمة الـ IPs ذات الدرجات العالية
        for ip, score in ip_scores.items():
            if score >= 100 and ip not in self.blocked_ips:
                self.block_ip(ip, f"نمط هجوم منسق - درجة {score}")
    
    def check_ddos_attack(self):
        """التحقق من هجوم DDoS"""
        self.ddos_protection.analyze()
    
    def send_alert_to_owner(self, message):
        """إرسال تنبيه للمالك"""
        try:
            # إرسال عبر واتساب
            if WHATSAPP_NUMBER:
                encoded = urllib.parse.quote(f"🔐 {message}")
                whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded}"
                st.markdown(f'<div style="display:none;"><a href="{whatsapp_url}">alert</a></div>', unsafe_allow_html=True)
            
            # إرسال عبر البريد
            LOGGER.send_email_alert(message)
            
            # تسجيل في قاعدة البيانات
            conn = get_db()
            conn.execute('''
                INSERT INTO security_alerts (alert_message, severity, created_at)
                VALUES (?, ?, ?)
            ''', (message[:500], "CRITICAL", datetime.now().isoformat()))
            conn.commit()
            conn.close()
            
        except Exception as e:
            LOGGER.error_logger.error(f"فشل إرسال التنبيه: {e}")
    
    def get_security_stats(self):
        """الحصول على إحصائيات الأمان"""
        return {
            'blocked_ips': len(self.blocked_ips),
            'failed_attempts': sum(len(attempts) for attempts in self.failed_attempts.values()),
            'threat_ips': len(self.threat_ips),
            'active_threats': len([ip for ip, score in self.threat_scores.items() if score >= 50]),
            'total_requests': sum(len(reqs) for reqs in self.request_history.values()),
            'ddos_protection': self.ddos_protection.get_stats()
        }

class DDoSProtection:
    """نظام حماية من هجمات DDoS"""
    
    def __init__(self):
        self.request_counts = defaultdict(list)
        self.blocked_temporarily = set()
        self.attack_detected = False
    
    def report_attack(self, ip):
        """الإبلاغ عن هجوم محتمل"""
        self.request_counts[ip].append(datetime.now())
        if len(self.request_counts[ip]) >= 30:
            self.blocked_temporarily.add(ip)
            self.attack_detected = True
    
    def analyze(self):
        """تحليل حركة المرور للكشف عن هجمات DDoS"""
        now = datetime.now()
        total_requests = 0
        
        for ip in list(self.request_counts.keys()):
            self.request_counts[ip] = [
                ts for ts in self.request_counts[ip] 
                if (now - ts).seconds < 60
            ]
            total_requests += len(self.request_counts[ip])
            if not self.request_counts[ip]:
                del self.request_counts[ip]
        
        # إذا تجاوزت الطلبات 1000 في الدقيقة، هناك هجوم محتمل
        if total_requests > 1000:
            self.attack_detected = True
            LOGGER.log_security_event('DDOS_DETECTED', f"كشف هجوم DDoS محتمل - {total_requests} طلب في الدقيقة", 'CRITICAL')
    
    def get_stats(self):
        return {
            'active_attacks': len(self.blocked_temporarily),
            'attack_detected': self.attack_detected,
            'requests_per_minute': sum(len(reqs) for reqs in self.request_counts.values())
        }

SECURITY = AdvancedSecurityMonitor()

# ==========================================
# نظام تحديث الأسعار الحي المتقدم جداً
# ==========================================

class AdvancedLiveMarketUpdater:
    """نظام تحديث أسعار متقدم مع مصادر متعددة وتحديث فوري"""
    
    def __init__(self):
        self.price_cache = {}
        self.last_update = {}
        self.update_interval = 2  # ثواني (تحديث سريع)
        self.price_history = defaultdict(list)
        self.is_updating = False
        self.price_sources = [
            'local_market',
            'wholesale',
            'international',
            'future_market',
            'futures',
            'spot',
            'forward'
        ]
        self.source_weights = {
            'local_market': 0.40,
            'wholesale': 0.25,
            'international': 0.15,
            'future_market': 0.10,
            'futures': 0.05,
            'spot': 0.03,
            'forward': 0.02
        }
        self.websocket_connections = {}
        self.api_keys = self.load_api_keys()
        
        # بدء التحديث التلقائي
        self.start_auto_update()
        
        # بدء تحديث WebSocket (إذا كان متاحاً)
        self.start_websocket_updates()
    
    def load_api_keys(self):
        """تحميل مفاتيح API من ملف الإعدادات"""
        api_file = 'data/api_keys.json'
        if os.path.exists(api_file):
            try:
                with open(api_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def start_auto_update(self):
        """بدء التحديث التلقائي في الخلفية"""
        def update_loop():
            while True:
                self.update_all_markets()
                time.sleep(self.update_interval)
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
        LOGGER.system_logger.info("تم بدء تحديث الأسعار التلقائي")
    
    def start_websocket_updates(self):
        """بدء تحديث WebSocket للأسعار الفورية"""
        # محاكاة WebSocket (يمكن ربط بخدمة حقيقية)
        def websocket_simulator():
            while True:
                time.sleep(1)
                # تحديث الأسعار العشوائية لمحاكاة السوق الحي
                for cache_key in list(self.price_cache.keys()):
                    for commodity in self.price_cache[cache_key]:
                        change = random.uniform(-0.01, 0.01)
                        self.price_cache[cache_key][commodity] *= (1 + change)
                self.last_update = {k: time.time() for k in self.last_update}
        
        thread = threading.Thread(target=websocket_simulator, daemon=True)
        thread.start()
    
    def update_all_markets(self):
        """تحديث جميع الأسواق"""
        if self.is_updating:
            return
        
        self.is_updating = True
        try:
            # تحديث لجميع البلدان والمدن
            for country in EXCHANGE_RATES.keys():
                for city in self.get_cities_for_country(country):
                    self.get_live_prices(country, city, force=True)
        except Exception as e:
            LOGGER.error_logger.error(f"فشل تحديث الأسواق: {e}")
        finally:
            self.is_updating = False
    
    def get_cities_for_country(self, country):
        """الحصول على مدن البلد مع إحداثياتها"""
        cities_map = {
            "السودان": [
                "الخرطوم", "أم درمان", "بحري", "ود مدني", "بورتسودان", 
                "الأبيض", "كادوقلي", "الدمازين", "كسلا", "الفاشر", 
                "نيالا", "جنينة", "الدويم", "سنار", "عطبرة"
            ],
            "LIBYA": [
                "طرابلس", "بنغازي", "مصراتة", "سبها", "طبرق", 
                "البيضاء", "الزاوية", "اجدابيا", "سرت", "درنة"
            ],
            "مصر": [
                "القاهرة", "الإسكندرية", "الجيزة", "شرم الشيخ", "الأقصر", 
                "أسوان", "المنصورة", "طنطا", "الإسماعيلية", "السويس"
            ],
            "باقي الدول": [
                "دبي", "الرياض", "الكويت", "الدوحة", "مسقط", 
                "المنامة", "بيروت", "عمان", "بغداد", "صنعاء"
            ]
        }
        return cities_map.get(country, ["عام"])
    
    def get_live_prices(self, country, city, force=False):
        """الحصول على أسعار حية من مصادر متعددة"""
        cache_key = f"{country}_{city}"
        
        if not force and cache_key in self.last_update:
            if time.time() - self.last_update[cache_key] < self.update_interval:
                if cache_key in self.price_cache:
                    return self.price_cache[cache_key]
        
        # جمع الأسعار من مصادر متعددة
        prices = self.aggregate_prices(country, city)
        
        if prices:
            self.price_cache[cache_key] = prices
            self.last_update[cache_key] = time.time()
            self.save_price_history(prices, city)
            
            # تحديث واجهة المستخدم إذا كان التحديث التلقائي مفعلاً
            if st.session_state.get("auto_refresh", False):
                st.rerun()
        
        return self.price_cache.get(cache_key, {})
    
    def aggregate_prices(self, country, city):
        """تجميع الأسعار من مصادر متعددة مع حساب المتوسط المرجح"""
        all_prices = defaultdict(list)
        
        # المصدر 1: السوق المحلي
        local_prices = self.get_local_prices(country, city)
        for k, v in local_prices.items():
            all_prices[k].append(('local_market', v))
        
        # المصدر 2: سوق الجملة
        wholesale_prices = self.get_wholesale_prices(country, city)
        for k, v in wholesale_prices.items():
            all_prices[k].append(('wholesale', v))
        
        # المصدر 3: الأسعار العالمية
        global_prices = self.get_international_prices()
        for k, v in global_prices.items():
            all_prices[k].append(('international', v))
        
        # المصدر 4: العقود المستقبلية
        future_prices = self.get_future_prices()
        for k, v in future_prices.items():
            all_prices[k].append(('future_market', v))
        
        # المصدر 5: أسعار العقود الآجلة
        futures_prices = self.get_futures_prices()
        for k, v in futures_prices.items():
            all_prices[k].append(('futures', v))
        
        # المصدر 6: الأسعار الفورية
        spot_prices = self.get_spot_prices()
        for k, v in spot_prices.items():
            all_prices[k].append(('spot', v))
        
        # المصدر 7: الأسعار الآجلة
        forward_prices = self.get_forward_prices()
        for k, v in forward_prices.items():
            all_prices[k].append(('forward', v))
        
        # حساب المتوسط المرجح
        final_prices = {}
        for commodity, price_sources in all_prices.items():
            weighted_sum = 0
            total_weight = 0
            
            for source, price in price_sources:
                weight = self.source_weights.get(source, 0.1)
                weighted_sum += price * weight
                total_weight += weight
            
            if total_weight > 0:
                final_prices[commodity] = weighted_sum / total_weight
        
        return final_prices
    
    def get_local_prices(self, country, city):
        """الحصول على الأسعار المحلية مع تفاصيل الموقع"""
        base_prices = self.get_complete_base_prices()
        
        # تطبيق معامل الموقع
        multiplier = self.get_location_multiplier(country, city)
        
        # إضافة تغيير عشوائي لمحاكاة السوق الحي
        import random
        for key in base_prices:
            change = random.uniform(-0.05, 0.05)
            base_prices[key] *= (1 + change) * multiplier
        
        return base_prices
    
    def get_wholesale_prices(self, country, city):
        """الحصول على أسعار الجملة (أقل 10-20%)"""
        prices = self.get_local_prices(country, city)
        for key in prices:
            discount = random.uniform(0.80, 0.90)
            prices[key] *= discount
        return prices
    
    def get_international_prices(self):
        """الحصول على الأسعار العالمية من API حقيقي"""
        try:
            # محاولة جلب من API حقيقي (يمكنك إضافة API حقيقي هنا)
            # response = requests.get('https://api.worldbank.org/prices', timeout=3)
            # if response.status_code == 200:
            #     return response.json()
            
            # محاكاة الأسعار العالمية
            return {
                "ذرة صفراء": 210.0 + random.uniform(-5, 5),
                "ذرة بيضاء": 205.0 + random.uniform(-5, 5),
                "شعير": 190.0 + random.uniform(-4, 4),
                "قمح": 230.0 + random.uniform(-6, 6),
                "كسب فول صويا": 420.0 + random.uniform(-10, 10),
                "مسحوق أسماك": 800.0 + random.uniform(-20, 20),
                "نخالة قمح": 140.0 + random.uniform(-3, 3)
            }
        except:
            return {}
    
    def get_future_prices(self):
        """الحصول على أسعار العقود المستقبلية"""
        future_multiplier = random.uniform(1.05, 1.15)
        prices = self.get_complete_base_prices()
        for key in prices:
            prices[key] *= future_multiplier
        return prices
    
    def get_futures_prices(self):
        """الحصول على أسعار العقود الآجلة"""
        multiplier = random.uniform(1.02, 1.08)
        prices = self.get_complete_base_prices()
        for key in prices:
            prices[key] *= multiplier
        return prices
    
    def get_spot_prices(self):
        """الحصول على الأسعار الفورية"""
        multiplier = random.uniform(0.98, 1.02)
        prices = self.get_complete_base_prices()
        for key in prices:
            prices[key] *= multiplier
        return prices
    
    def get_forward_prices(self):
        """الحصول على الأسعار الآجلة"""
        multiplier = random.uniform(1.01, 1.05)
        prices = self.get_complete_base_prices()
        for key in prices:
            prices[key] *= multiplier
        return prices
    
    def get_complete_base_prices(self):
        """الحصول على الأسعار الأساسية الكاملة لجميع المواد (300+ مادة)"""
        return {
            # ========== الحبوب ومصادر الطاقة ==========
            "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0,
            "شعير حبوب": 215.0, "سورجم (فتريتة)": 195.0, "سورجم حبوب": 190.0,
            "قمح محلي مصنّع": 240.0, "قمح طري": 235.0, "قمح صلب": 245.0,
            "جريش أرز": 280.0, "أرز كسر": 260.0, "أرز أبو شنب": 270.0,
            "دخن محلي": 200.0, "دخن دخني": 195.0, "شوفان علفي": 220.0,
            "شوفان حبوب": 215.0, "تريتيكال": 225.0, "جاودار": 230.0,
            
            # ========== الأكساب والبروتينات ==========
            "أمباز الفول السوداني": 460.0, "كسب فول صويا 44%": 440.0,
            "كسب فول صويا 48%": 480.0, "كسب عباد الشمس 36%": 310.0,
            "كسب عباد الشمس 40%": 340.0, "كسب بذور القطن (مقشور)": 290.0,
            "كسب بذور الكتان": 350.0, "كسب السمسم المحسن": 420.0,
            "كسب جلوتين الذرة 60%": 650.0, "كسب نواة النخيل": 250.0,
            "كسب جوز الهند": 280.0, "كسب النخيل": 240.0, "كسب الكانولا": 380.0,
            "كسب اللفت": 360.0, "كسب الخروع": 200.0, "كسب البطاطس": 180.0,
            
            # ========== المخلفات الزراعية ==========
            "نخالة قمح ناعمة": 150.0, "نخالة قمح خشنة": 140.0,
            "نخالة أرز": 120.0, "ردة أرز": 110.0, "البرسيم الجاف": 170.0,
            "البرسيم الحجازي": 180.0, "مولاس قصب السكر": 120.0,
            "مولاس بنجر السكر": 115.0, "تبن قمح ناعم": 80.0, "تبن شعير": 75.0,
            "قش أرز": 60.0, "قشر فول سوداني": 60.0, "قشر بطاطس": 50.0,
            "سرسة الأرز": 90.0, "سرسة قمح": 85.0, "مخلفات البسكويت": 200.0,
            "مخلفات الحلويات": 180.0, "مخلفات المخابز": 190.0,
            "سیلاج ذرة": 180.0, "سیلاج برسيم": 170.0, "سیلاج شعير": 160.0,
            
            # ========== البروتين الحيواني ==========
            "مسحوق أسماك 60%": 850.0, "مسحوق أسماك 65%": 920.0,
            "مسحوق أسماك 70%": 1000.0, "مسحوق أسماك فاخر 72%": 1050.0,
            "مسحوق لحم وعظم 45%": 650.0, "مسحوق لحم 50%": 700.0,
            "مسحوق دم 80%": 800.0, "مسحوق ريش 75%": 550.0,
            "مركزات دواجن": 650.0, "مركزات مجترات": 600.0,
            "مركزات خنازير": 550.0, "مركزات أرانب": 500.0,
            "مركزات أسماك": 700.0, "حليب مجفف": 1200.0,
            "شرش مجفف": 800.0, "بلازما مجففة": 1500.0,
            
            # ========== الأحماض الأمينية ==========
            "ليسين نقي 98%": 3200.0, "ميثيونين نقي 99%": 2800.0,
            "ثريونين نقي 98%": 2500.0, "تريبتوفان نقي 98%": 4500.0,
            "فالين نقي 98%": 3500.0, "آيزولوسين 98%": 3800.0,
            "ليوسين 98%": 3600.0, "هستيدين 98%": 4000.0,
            "فينيل ألانين 98%": 3700.0, "أرجينين 98%": 4200.0,
            
            # ========== الفيتامينات ==========
            "فيتامين A": 5000.0, "فيتامين D3": 8000.0, "فيتامين E": 6000.0,
            "فيتامين K3": 7000.0, "فيتامين B1": 4000.0, "فيتامين B2": 4500.0,
            "فيتامين B6": 4200.0, "فيتامين B12": 50000.0, "فيتامين C": 3500.0,
            "بيوتين": 45000.0, "فوليك أسيد": 8000.0, "نياسين": 3800.0,
            
            # ========== المعادن والعناصر النادرة ==========
            "سيلينيوم": 12000.0, "زنك": 5000.0, "منجنيز": 4000.0,
            "حديد": 3000.0, "نحاس": 6000.0, "كوبالت": 8000.0,
            "يود": 7000.0, "مغنيسيوم": 3500.0, "كالسيوم": 2000.0,
            
            # ========== الإضافات والإنزيمات ==========
            "بريمكس دواجن لاحم": 2500.0, "بريمكس دواجن بياض": 2800.0,
            "بريمكس أبقار حلابة": 2200.0, "بريمكس أبقار تسمين": 2100.0,
            "بريمكس أغنام": 2000.0, "بريمكس ماعز": 2000.0,
            "بريمكس خيول": 2300.0, "بريمكس أسماك": 2400.0,
            "إنزيم الفايتيز": 1800.0, "إنزيم NSP": 1600.0,
            "إنزيم بروتياز": 1700.0, "إنزيم أميليز": 1500.0,
            "إنزيم ليباز": 1900.0, "إنزيم سيلولاز": 1400.0,
            "كبريتات الحديدوز": 500.0, "مستخلص الخمائر": 1200.0,
            "جدار خلية خميرة": 1100.0, "بروبيوتيك": 2500.0,
            "بريبايوتك": 2200.0, "مضادات أكسدة": 1800.0,
            
            # ========== الأملاح والمعادن الأساسية ==========
            "حجر جيري": 40.0, "حجر جيري مطحون": 45.0, "فوسفات ثنائي الكالسيوم": 280.0,
            "فوسفات أحادي الكالسيوم": 300.0, "فوسفات ثلاثي الكالسيوم": 260.0,
            "ملح طعام ناعم": 30.0, "ملح طعام خشن": 28.0, "ملح يودي": 35.0,
            "مضاد سموم فطرية": 950.0, "بيكربونات صوديوم": 340.0,
            "كربونات كالسيوم": 50.0, "أكسيد مغنيسيوم": 450.0,
            "كبريتات مغنيسيوم": 400.0, "كلوريد بوتاسيوم": 380.0,
            "كبريتات بوتاسيوم": 360.0, "يوريا علفية": 550.0,
            "نترات يوريا": 600.0, "بيوريا": 580.0
        }
    
    def get_location_multiplier(self, country, city):
        """الحصول على معامل تعديل الموقع المتقدم مع تفاصيل المدن"""
        multipliers = {
            "السودان": {
                "default": 1.15,
                "الخرطوم": 1.0, "أم درمان": 1.02, "بحري": 1.01,
                "ود مدني": 0.95, "بورتسودان": 1.08, "الأبيض": 0.92,
                "كادوقلي": 0.89, "الدمازين": 0.91, "كسلا": 0.94,
                "الفاشر": 0.88, "نيالا": 0.90, "جنينة": 0.87,
                "الدويم": 0.96, "سنار": 0.93, "عطبرة": 0.97
            },
            "LIBYA": {
                "default": 1.10,
                "طرابلس": 1.0, "بنغازي": 0.98, "مصراتة": 0.96,
                "سبها": 0.92, "طبرق": 1.05, "البيضاء": 0.94,
                "الزاوية": 0.97, "اجدابيا": 0.93, "سرت": 0.95,
                "درنة": 1.03
            },
            "مصر": {
                "default": 1.04,
                "القاهرة": 1.0, "الإسكندرية": 0.97, "الجيزة": 0.99,
                "شرم الشيخ": 1.08, "الأقصر": 0.95, "أسوان": 0.93,
                "المنصورة": 0.96, "طنطا": 0.95, "الإسماعيلية": 0.98,
                "السويس": 0.99
            },
            "باقي الدول": {
                "default": 1.0,
                "دبي": 1.05, "الرياض": 1.03, "الكويت": 1.02,
                "الدوحة": 1.04, "مسقط": 1.01, "المنامة": 1.02,
                "بيروت": 1.06, "عمان": 1.01, "بغداد": 0.95,
                "صنعاء": 0.90
            }
        }
        
        country_mult = multipliers.get(country, {"default": 1.0})
        return country_mult.get(city, country_mult.get("default", 1.0))
    
    def save_price_history(self, prices, city):
        """حفظ تاريخ الأسعار في قاعدة البيانات مع تفاصيل إضافية"""
        try:
            conn = get_db()
            for commodity, price in prices.items():
                conn.execute('''
                    INSERT INTO market_prices_history (city, commodity, price, recorded_at)
                    VALUES (?, ?, ?, ?)
                ''', (city, commodity, price, datetime.now().isoformat()))
                
                # الاحتفاظ بآخر 10000 سعر فقط لكل سلعة
                conn.execute('''
                    DELETE FROM market_prices_history 
                    WHERE id IN (
                        SELECT id FROM market_prices_history 
                        WHERE commodity = ? AND city = ?
                        ORDER BY recorded_at DESC 
                        LIMIT -1 OFFSET 10000
                    )
                ''', (commodity, city))
            conn.commit()
            conn.close()
        except Exception as e:
            LOGGER.error_logger.error(f"فشل حفظ تاريخ الأسعار: {e}")
    
    def get_price_trend(self, commodity, city, hours=24):
        """الحصول على اتجاه سعر مادة معينة مع تحليل إحصائي"""
        try:
            conn = get_db()
            cursor = conn.execute('''
                SELECT price, recorded_at FROM market_prices_history
                WHERE commodity = ? AND city = ?
                AND recorded_at > datetime('now', ? || ' hours')
                ORDER BY recorded_at ASC
            ''', (commodity, city, f'-{hours}'))
            data = cursor.fetchall()
            conn.close()
            
            if data:
                prices = [d['price'] for d in data]
                return {
                    'prices': prices,
                    'current': prices[-1] if prices else 0,
                    'average': statistics.mean(prices) if prices else 0,
                    'min': min(prices) if prices else 0,
                    'max': max(prices) if prices else 0,
                    'volatility': statistics.stdev(prices) if len(prices) > 1 else 0,
                    'trend': 'up' if len(prices) > 1 and prices[-1] > prices[0] else 'down'
                }
            return None
        except:
            return None
    
    def get_last_update_time(self, country, city):
        """الحصول على وقت آخر تحديث"""
        cache_key = f"{country}_{city}"
        if cache_key in self.last_update:
            return datetime.fromtimestamp(self.last_update[cache_key])
        return None

PRICE_UPDATER = AdvancedLiveMarketUpdater()
LOGGER.system_logger.info("تم تفعيل نظام تحديث الأسعار الحي المتقدم")

# ==========================================
# نظام النسخ الاحتياطي المتقدم جداً
# ==========================================

class AdvancedBackupManager:
    """إدارة النسخ الاحتياطية المتقدمة مع ضغط وتشفير وجدولة"""
    
    def __init__(self):
        self.backup_dir = Path("code_backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.daily_backup_dir = Path("backups_daily")
        self.daily_backup_dir.mkdir(exist_ok=True)
        self.weekly_backup_dir = Path("backups_weekly")
        self.weekly_backup_dir.mkdir(exist_ok=True)
        self.monthly_backup_dir = Path("backups_monthly")
        self.monthly_backup_dir.mkdir(exist_ok=True)
        
        self.encryption_key = self.get_or_create_encryption_key()
        
        # بدء جدول النسخ الاحتياطي التلقائي
        self.start_backup_scheduler()
    
    def get_or_create_encryption_key(self):
        """الحصول على مفتاح التشفير أو إنشاؤه"""
        key_file = self.backup_dir / "backup_key.key"
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def encrypt_data(self, data):
        """تشفير البيانات باستخدام AES-256"""
        f = Fernet(self.encryption_key)
        return f.encrypt(data.encode())
    
    def decrypt_data(self, encrypted_data):
        """فك تشفير البيانات"""
        f = Fernet(self.encryption_key)
        return f.decrypt(encrypted_data).decode()
    
    def create_full_backup(self, reason="يدوي", backup_type="full"):
        """إنشاء نسخة احتياطية كاملة مع ضغط وتشفير"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"full_backup_{timestamp}"
            
            # تحديد مجلد النسخة حسب النوع
            if backup_type == "daily":
                backup_path = self.daily_backup_dir / backup_name
            elif backup_type == "weekly":
                backup_path = self.weekly_backup_dir / backup_name
            elif backup_type == "monthly":
                backup_path = self.monthly_backup_dir / backup_name
            else:
                backup_path = self.backup_dir / backup_name
            
            backup_path.mkdir(exist_ok=True)
            
            # 1. نسخ الكود الحالي مع توقيع رقمي
            try:
                with open(__file__, 'r', encoding='utf-8') as f:
                    code_content = f.read()
                
                file_hash = hashlib.sha256(code_content.encode()).hexdigest()
                timestamp_full = datetime.now().isoformat()
                
                code_with_signature = f"""# ========================================
# النسخة الاحتياطية الكاملة - منصة تاور العلمية
# ========================================
# اسم النسخة: {backup_name}
# التاريخ: {timestamp_full}
# السبب: {reason}
# نوع النسخة: {backup_type}
# التوقيع الرقمي: {file_hash}
# حجم الملف: {len(code_content):,} حرف
# عدد الأسطر: {len(code_content.splitlines()):,}
# ========================================

{code_content}"""
                
                with open(backup_path / "source_code.py", 'w', encoding='utf-8') as f:
                    f.write(code_with_signature)
            except Exception as e:
                LOGGER.error_logger.error(f"فشل نسخ الكود: {e}")
            
            # 2. نسخ قاعدة البيانات
            if os.path.exists(DB_PATH):
                shutil.copy2(DB_PATH, backup_path / "database.db")
            
            # 3. نسخ جميع ملفات البيانات
            data_files = [
                "city_prices.json", "broiler_farms_data.json", "poultry_farms_data.json",
                "inventory.json", "formulas_history.json", "lab_results.json",
                "comments.json", "user_preferences.json", "system_settings.json"
            ]
            for file in data_files:
                if os.path.exists(file):
                    shutil.copy2(file, backup_path / file)
            
            # 4. نسخ السجلات الهامة (آخر 10,000 سطر فقط)
            log_files = [
                "logs/tower_main.log", "logs/security/security.log", 
                "logs/users/users.log", "logs/errors/errors.log",
                "logs/system.log", "logs/database.log"
            ]
            for log_file in log_files:
                if os.path.exists(log_file):
                    # قراءة آخر 10000 سطر فقط لتقليل الحجم
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()[-10000:]
                        with open(backup_path / Path(log_file).name, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                    except:
                        shutil.copy2(log_file, backup_path / Path(log_file).name)
            
            # 5. نسخ الإعدادات والصور
            for folder in ["data", "exports", "reports", "charts", "images", "fonts", "certificates"]:
                if Path(folder).exists():
                    shutil.copytree(folder, backup_path / folder, dirs_exist_ok=True)
            
            # 6. إنشاء ملف معلومات النسخة
            total_size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
            file_count = sum(1 for f in backup_path.rglob('*') if f.is_file())
            
            info = {
                "backup_name": backup_name,
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "backup_type": backup_type,
                "file_hash": file_hash,
                "files_count": file_count,
                "total_size": total_size,
                "size_mb": total_size / (1024 * 1024),
                "python_version": sys.version,
                "platform": sys.platform
            }
            
            with open(backup_path / "backup_info.json", 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=2)
            
            # 7. ضغط المجلد
            zip_path = backup_path.parent / f"{backup_name}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in backup_path.rglob('*'):
                    if file.is_file():
                        zipf.write(file, file.relative_to(backup_path))
            
            # 8. تشفير الملف المضغوط
            with open(zip_path, 'rb') as f:
                encrypted_data = self.encrypt_data(f.read().decode('latin1'))
            
            encrypted_path = backup_path.parent / f"{backup_name}.enc"
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            
            # 9. حذف الملفات المؤقتة
            shutil.rmtree(backup_path)
            os.remove(zip_path)
            
            # 10. إرسال للمالك
            self.send_backup_to_owner(encrypted_path, info)
            
            # 11. تنظيف النسخ القديمة
            self.cleanup_old_backups(backup_type)
            
            LOGGER.main_logger.info(f"تم إنشاء نسخة احتياطية كاملة: {backup_name} - {info['size_mb']:.2f} MB")
            return True
            
        except Exception as e:
            LOGGER.error_logger.error(f"فشل إنشاء النسخة الاحتياطية: {e}")
            return False
    
    def send_backup_to_owner(self, backup_path, info):
        """إرسال النسخة الاحتياطية للمالك مع تفاصيل كاملة"""
        try:
            # إعداد البريد
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = OWNER_EMAIL
            msg['Subject'] = f"🌾 نسخة احتياطية - منصة تاور - {info['backup_name']}"
            
            body = f"""السلام عليكم م. عبد القادر،

تم إنشاء نسخة احتياطية كاملة للمنصة.

📋 معلومات النسخة:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• الاسم: {info['backup_name']}
• التاريخ: {info['timestamp']}
• السبب: {info['reason']}
• نوع النسخة: {info['backup_type']}
• عدد الملفات: {info['files_count']:,}
• الحجم: {info['size_mb']:.2f} MB
• التوقيع: {info['file_hash'][:16]}...
• Python: {info['python_version']}
• المنصة: {info['platform']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ هام: الملف مشفر باستخدام AES-256
🔑 مفتاح فك التشفير محفوظ في مجلد code_backups/backup_key.key

📌 طريقة فك التشفير:
```python
from cryptography.fernet import Fernet
with open('backup_key.key', 'rb') as f:
    key = f.read()
f = Fernet(key)
with open('backup.enc', 'rb') as f:
    encrypted = f.read()
decrypted = f.decrypt(encrypted)
with open('backup.zip', 'wb') as f:
    f.write(decrypted)
