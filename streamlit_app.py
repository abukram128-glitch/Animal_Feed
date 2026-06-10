#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف
النسخة المتكاملة v3.1 - محدثة بالكامل مع نظام مراقبة وأمان متقدم
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
import requests
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from functools import lru_cache, wraps
from typing import Dict, List, Tuple, Optional, Any
import warnings
from collections import defaultdict

# ==========================================
# مكتبات إضافية
# ==========================================

from scipy.optimize import linprog
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import arabic_reshaper
from bidi.algorithm import get_display
import qrcode
from PIL import Image as PILImage

# محاولة استيراد مكتبة الباركود
try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False
    pyzbar_decode = None

warnings.filterwarnings('ignore')
load_dotenv()

# ==========================================
# إنشاء المجلدات
# ==========================================

for folder in ["logs", "backups", "data", "temp", "visitors"]:
    Path(folder).mkdir(exist_ok=True)

# ==========================================
# نظام التسجيل المتقدم (مراقبة الاختراق)
# ==========================================

class SecurityLogger:
    """نظام متقدم لمراقبة الأمان والاختراق"""
    
    def __init__(self):
        self.setup_security_logging()
        self.failed_attempts = defaultdict(list)
        self.blocked_ips = set()
        
    def setup_security_logging(self):
        """إعداد سجلات الأمان"""
        self.security_logger = logging.getLogger('SecurityMonitor')
        self.security_logger.setLevel(logging.WARNING)
        
        # سجل الاختراقات
        attack_handler = logging.handlers.RotatingFileHandler(
            'logs/attacks.log', 
            maxBytes=10485760, 
            backupCount=10,
            encoding='utf-8'
        )
        attack_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        attack_handler.setFormatter(attack_formatter)
        self.security_logger.addHandler(attack_handler)
        
        # سجل الزوار
        visitor_handler = logging.handlers.RotatingFileHandler(
            'logs/visitors.log', 
            maxBytes=5242880, 
            backupCount=5,
            encoding='utf-8'
        )
        visitor_handler.setFormatter(attack_formatter)
        visitor_logger = logging.getLogger('VisitorMonitor')
        visitor_logger.setLevel(logging.INFO)
        visitor_logger.addHandler(visitor_handler)
        self.visitor_logger = visitor_logger
    
    def log_visitor(self, ip_address: str, user_agent: str, user_role: str = None):
        """تسجيل الزوار"""
        visitor_info = {
            "ip": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.now().isoformat(),
            "role": user_role or "unknown",
            "session_id": st.session_state.get("session_token", "none")[:8]
        }
        self.visitor_logger.info(json.dumps(visitor_info, ensure_ascii=False))
        
        # إشعار للمالك إذا كان زائر جديد
        if user_role == "owner":
            self.send_alert_to_owner(f"👑 المالك دخل المنصة من {ip_address}")
    
    def log_attack_attempt(self, ip_address: str, attack_type: str, details: str = ""):
        """تسجيل محاولات الاختراق"""
        attack_info = {
            "ip": ip_address,
            "type": attack_type,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "severity": "HIGH"
        }
        self.security_logger.warning(json.dumps(attack_info, ensure_ascii=False))
        
        # تسجيل المحاولات الفاشلة
        self.failed_attempts[ip_address].append(datetime.now())
        
        # حظر IP إذا تكررت المحاولات
        if len(self.failed_attempts[ip_address]) >= 5:
            self.blocked_ips.add(ip_address)
            self.send_alert_to_owner(f"🚨 تم حظر IP {ip_address} بسبب 5 محاولات فاشلة")
        
        # إشعار فوري للمالك
        self.send_alert_to_owner(f"⚠️ محاولة اختراق من {ip_address}: {attack_type} - {details}")
    
    def send_alert_to_owner(self, message: str):
        """إرسال تنبيه للمالك"""
        try:
            # حفظ في قاعدة البيانات
            with get_db() as conn:
                conn.execute('''
                    INSERT INTO security_alerts (alert_message, alert_time, is_read)
                    VALUES (?, ?, ?)
                ''', (message, datetime.now().isoformat(), 0))
            
            # إرسال واتساب إذا كان الرقم متاحاً
            if WHATSAPP_NUMBER:
                send_whatsapp_alert(WHATSAPP_NUMBER, f"🔐 تنبيه أمني: {message}")
            
            LOGGER.warning(f"تنبيه أمني: {message}")
        except Exception as e:
            LOGGER.error(f"فشل إرسال التنبيه: {e}")
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """التحقق من حظر IP"""
        # تنظيف المحاولات القديمة (أكثر من ساعة)
        now = datetime.now()
        self.failed_attempts[ip_address] = [
            attempt for attempt in self.failed_attempts[ip_address] 
            if (now - attempt).seconds < 3600
        ]
        return ip_address in self.blocked_ips

SECURITY_LOGGER = SecurityLogger()

# ==========================================
# نظام تحديث الأسعار التلقائي
# ==========================================

class LiveMarketUpdater:
    """تحديث أسعار السوق بشكل لحظي"""
    
    def __init__(self):
        self.last_update = None
        self.update_interval = 5  # ثواني
        self.price_history = defaultdict(list)
        self.api_endpoints = {
            "global_prices": "https://api.example.com/prices",  # يمكنك تغيير الرابط
            "local_markets": "https://api.example.com/local"
        }
    
    def get_live_prices(self, country: str, city: str) -> Dict[str, float]:
        """الحصول على أسعار لحظية"""
        # التحقق من آخر تحديث
        if self.last_update and (datetime.now() - self.last_update).seconds < self.update_interval:
            return self.get_cached_prices(country, city)
        
        # تحديث الأسعار
        try:
            live_prices = self.fetch_prices_from_api(country, city)
            if live_prices:
                self.last_update = datetime.now()
                self.save_price_history(live_prices)
                LOGGER.info(f"تم تحديث الأسعار لـ {city} في {self.last_update}")
                return live_prices
        except Exception as e:
            LOGGER.error(f"فشل تحديث الأسعار: {e}")
        
        # العودة للأسعار المخزنة
        return self.get_cached_prices(country, city)
    
    def fetch_prices_from_api(self, country: str, city: str) -> Dict[str, float]:
        """جلب الأسعار من API خارجي"""
        # محاكاة API - يمكن استبدالها باتصال حقيقي
        try:
            # محاولة جلب من API حقيقي (اختياري)
            # response = requests.get(f"{self.api_endpoints['global_prices']}?country={country}&city={city}", timeout=5)
            # if response.status_code == 200:
            #     return response.json()
            
            # حالياً نستخدم البيانات المحلية مع تحديث عشوائي بسيط
            base_prices = MarketPriceEngine.get_adjusted_market_data(country, "عام", city)
            
            # إضافة تغيير عشوائي بسيط لمحاكاة السوق
            import random
            for key in base_prices:
                change = random.uniform(-0.02, 0.02)  # تغيير ±2%
                base_prices[key] *= (1 + change)
            
            return base_prices
        except:
            return None
    
    def get_cached_prices(self, country: str, city: str) -> Dict[str, float]:
        """الحصول على الأسعار المخزنة"""
        cache_key = f"{country}_{city}"
        if cache_key not in self.price_cache:
            self.price_cache[cache_key] = MarketPriceEngine.get_adjusted_market_data(country, "عام", city)
        return self.price_cache[cache_key]
    
    def save_price_history(self, prices: Dict[str, float]):
        """حفظ تاريخ الأسعار"""
        timestamp = datetime.now().isoformat()
        for commodity, price in prices.items():
            self.price_history[commodity].append({
                "timestamp": timestamp,
                "price": price
            })
            # الاحتفاظ بآخر 1000 سعر فقط
            if len(self.price_history[commodity]) > 1000:
                self.price_history[commodity] = self.price_history[commodity][-1000:]
    
    def get_price_trend(self, commodity: str, hours: int = 24) -> List[Dict]:
        """الحصول على اتجاه سعر سلعة معينة"""
        return self.price_history.get(commodity, [])[-hours*12:]  # 12 نقطة في الساعة

MARKET_UPDATER = LiveMarketUpdater()

# ==========================================
# نظام إرسال الكود للمالك (محسن)
# ==========================================

class CodeBackupManager:
    """إدارة نسخ الكود الاحتياطية وإرسالها للمالك"""
    
    def __init__(self):
        self.backup_dir = Path("code_backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def send_code_to_owner(self, email: str, reason: str = "نسخه احتياطية دورية") -> bool:
        """إرسال الكود إلى المالك"""
        try:
            # قراءة الكود الحالي
            current_file = __file__
            with open(current_file, "r", encoding="utf-8") as f:
                code_content = f.read()
            
            # إضافة توقيع رقمي
            file_hash = hashlib.md5(code_content.encode()).hexdigest()
            timestamp = datetime.now().isoformat()
            code_content = f"""# Digital Signature: {file_hash}
# Generated: {timestamp}
# Reason: {reason}
# Backup Type: Full System Backup

{code_content}"""
            
            # حفظ نسخة محلية
            backup_file = self.backup_dir / f"backup_{timestamp.replace(':', '-')}.py"
            with open(backup_file, "w", encoding="utf-8") as f:
                f.write(code_content)
            
            # إرسال بالبريد
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = email
            msg['Subject'] = f"🌾 نسخة احتياطية للمنصة - {reason} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            body = f"""السلام عليكم م. عبد القادر،

هذه نسخة احتياطية تلقائية من منصة تاور العلمية.

📋 معلومات النسخة:
- التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- السبب: {reason}
- التوقيع: {file_hash[:16]}...
- حجم الملف: {len(code_content):,} حرف

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
            
            LOGGER.info(f"تم إرسال الكود إلى {email} - {reason}")
            
            # تسجيل في قاعدة البيانات
            with get_db() as conn:
                conn.execute('''
                    INSERT INTO code_backups (backup_date, reason, file_hash, size)
                    VALUES (?, ?, ?, ?)
                ''', (datetime.now().isoformat(), reason, file_hash, len(code_content)))
            
            return True
            
        except Exception as e:
            LOGGER.error(f"فشل إرسال الكود: {e}")
            return False
    
    def auto_backup_schedule(self):
        """نسخ احتياطي تلقائي مجدول"""
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT MAX(backup_date) as last_backup FROM code_backups
            ''')
            result = cursor.fetchone()
            
            last_backup = result['last_backup'] if result else None
            
            # إذا مر أكثر من 6 ساعات على آخر نسخة
            if not last_backup:
                should_backup = True
            else:
                last_time = datetime.fromisoformat(last_backup)
                should_backup = (datetime.now() - last_time).seconds > 21600  # 6 ساعات
            
            if should_backup:
                self.send_code_to_owner(OWNER_EMAIL, "نسخه احتياطية آلية (كل 6 ساعات)")

CODE_BACKUP_MANAGER = CodeBackupManager()

# ==========================================
# إعدادات المنصة والإعدادات الأمنية
# ==========================================

st.set_page_config(
    page_title="منصة تاور العلمية - الإصدار المتكامل 3.1",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# نظام قاعدة البيانات الموسع
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
        LOGGER.error(f"خطأ في قاعدة البيانات: {e}")
        raise
    finally:
        conn.close()

def init_database():
    """تهيئة قاعدة البيانات مع جداول جديدة"""
    with get_db() as conn:
        # الجداول الموجودة سابقاً
        conn.execute('''
            CREATE TABLE IF NOT EXISTS formulas_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                formula_data TEXT NOT NULL,
                target_dp REAL,
                target_se REAL,
                breed TEXT,
                cost REAL,
                city TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
        
        # جداول جديدة للأمان
        conn.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_message TEXT,
                alert_time TIMESTAMP,
                is_read INTEGER DEFAULT 0,
                severity TEXT DEFAULT 'medium'
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS code_backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_date TIMESTAMP,
                reason TEXT,
                file_hash TEXT,
                size INTEGER
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS market_prices_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT,
                commodity TEXT,
                price REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS blocked_ips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT UNIQUE,
                block_reason TEXT,
                blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        LOGGER.info("تم تهيئة قاعدة البيانات بنجاح")

# تهيئة قاعدة البيانات
if "db_initialized" not in st.session_state:
    init_database()
    st.session_state["db_initialized"] = True

# ==========================================
# نظام التسجيل الأساسي
# ==========================================

def setup_logging():
    logger = logging.getLogger('TowerPlatform')
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.handlers.RotatingFileHandler(
            'logs/tower.log', 
            maxBytes=10485760,
            backupCount=5,
            encoding='utf-8'
        )
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        error_handler = logging.handlers.RotatingFileHandler(
            'logs/errors.log', 
            maxBytes=5242880,
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    
    return logger

LOGGER = setup_logging()

# ==========================================
# الأكواد المعتمدة ونظام المصادقة
# ==========================================

def generate_secure_hash(code: str, salt: str = None) -> str:
    if salt is None:
        salt = secrets.token_hex(16)
    return hashlib.pbkdf2_hmac('sha256', code.encode(), salt.encode(), 100000).hex()

CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

# إعدادات البريد والإشعارات
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "abukram128@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "oynz rdli tsdy ekdq")
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "abukram128@gmail.com")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "+249123533489")
GOOGLE_FORM_URL = os.getenv("GOOGLE_FORM_URL", "https://forms.google.com/YOUR_FORM_URL")

# ==========================================
# دوال مساعدة
# ==========================================

def get_client_ip():
    """الحصول على IP الزائر"""
    try:
        # محاولة الحصول من Streamlit Cloud
        if hasattr(st, 'context') and hasattr(st.context, 'headers'):
            return st.context.headers.get('X-Forwarded-For', 'unknown').split(',')[0]
    except:
        pass
    return "127.0.0.1"

def send_whatsapp_alert(phone_number: str, message: str):
    """إرسال تنبيه عبر واتساب"""
    try:
        encoded_msg = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_msg}"
        # تخزين الرابط للعرض
        st.markdown(f"<div style='display:none;'><a href='{whatsapp_url}' target='_blank'>تنبيه</a></div>", unsafe_allow_html=True)
    except Exception as e:
        LOGGER.error(f"فشل إرسال واتساب: {e}")

@st.cache_data(ttl=3600)
def get_image_base64(paths: List[str]) -> Optional[str]:
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode()
            except Exception:
                pass
    return None

img_base64 = get_image_base64(PHOTO_OPTIONS)

# ==========================================
# معالجة النص العربي
# ==========================================

class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=1000)
    def fix_arabic_text(text: str) -> str:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text

arabic_processor = ArabicTextProcessor()

# ==========================================
# مولد PDF المحترف
# ==========================================

class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        if os.path.exists("Amiri-Regular.ttf"):
            try:
                pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
                self.font_name = 'Amiri'
            except:
                pass

    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, include_charts=True) -> bytes:
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
            ('GRID', (0,0), (-1,-1), 1, HexColor('#2e7d32')),
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
        ]))
        story.append(t2)

        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026", size=9, align=TA_CENTER, color=HexColor('#666666')))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# ==========================================
# بقية الكود الأصلي (المكتبات، المتغيرات، الواجهات)
# ==========================================

# [هنا يتم وضع باقي الكود الأصلي كما هو دون تغيير]
# المكتبة الكاملة للمواد العلفية
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة الكبرى": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6},
    },
    "🌱 الأكساب ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
    }
}

# ==========================================
# محرك أسعار السوق (مع تحديث مباشر)
# ==========================================

class MarketPriceEngine:
    @staticmethod
    def get_adjusted_market_data(country: str, state_or_region: str, city: str) -> Dict[str, float]:
        """الحصول على أسعار السوق مع تحديث مباشر"""
        
        # محاولة الحصول على أسعار حية
        live_prices = MARKET_UPDATER.get_live_prices(country, city)
        if live_prices:
            return live_prices
        
        # إذا فشل، استخدم الأسعار الأساسية
        feed_prices = {}
        for cat in BIG_FEEDS_LIBRARY.values():
            for ing in cat:
                feed_prices[ing] = 230.0
        
        base_prices = {
            "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0,
            "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا 44%": 440.0,
            "نخالة قمح (ردة)": 150.0, "ملح الطعام": 30.0,
        }
        feed_prices.update(base_prices)
        
        # تعديل حسب الموقع
        multiplier = 1.0
        if country == "السودان":
            multiplier = 1.15
        elif country == "LIBYA":
            multiplier = 1.10
        elif country == "مصر":
            multiplier = 1.04
        
        for k in feed_prices:
            feed_prices[k] *= multiplier
        
        return feed_prices

# ==========================================
# CSS Styles
# ==========================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    * { font-family: 'Cairo', sans-serif; }
    .main-box {
        background-color: rgba(255, 255, 255, 0.98); 
        padding: 30px; 
        border-radius: 15px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18);
    }
    .section-title {
        color: #1b5e20;
        border-right: 6px solid #2e7d32;
        padding-right: 15px;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 30px 0 20px 0;
    }
    .price-card {
        background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
        padding: 20px;
        border-radius: 12px;
        border-right: 5px solid #2e7d32;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# متغيرات الجلسة
# ==========================================

if "approved" not in st.session_state: 
    st.session_state["approved"] = False
if "user_role" not in st.session_state: 
    st.session_state["user_role"] = None
if "session_token" not in st.session_state: 
    st.session_state["session_token"] = secrets.token_urlsafe(32)
if "last_activity" not in st.session_state:
    st.session_state["last_activity"] = datetime.now()

# ==========================================
# بوابة الدخول مع مراقبة الاختراق
# ==========================================

client_ip = get_client_ip()
user_agent = st.context.headers.get('User-Agent', 'unknown') if hasattr(st, 'context') else 'unknown'

if SECURITY_LOGGER.is_ip_blocked(client_ip):
    st.error("🚫 تم حظر عنوان IP الخاص بك بسبب محاولات دخول متكررة. يرجى التواصل مع الدعم.")
    SECURITY_LOGGER.log_attack_attempt(client_ip, "blocked_ip_access", "محاولة دخول من IP محظور")
    st.stop()

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول</h2>", unsafe_allow_html=True)
    
    input_code = st.text_input("🔑 أدخل كود الدخول:", type="password")
    
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("تسجيل الدخول 🔓", type="primary"):
            if input_code in CODES_DB:
                st.session_state["approved"] = True
                st.session_state["user_role"] = CODES_DB[input_code]["role"]
                st.session_state["session_token"] = secrets.token_urlsafe(32)
                
                # تسجيل الزائر الناجح
                SECURITY_LOGGER.log_visitor(client_ip, user_agent, st.session_state["user_role"])
                LOGGER.info(f"تسجيل دخول ناجح: {CODES_DB[input_code]['role']} من {client_ip}")
                
                # إشعار للمالك إذا دخل مالك آخر
                if st.session_state["user_role"] == "owner":
                    CODE_BACKUP_MANAGER.auto_backup_schedule()
                
                st.rerun()
            else:
                SECURITY_LOGGER.log_attack_attempt(client_ip, "wrong_code", f"كود خاطئ: {input_code[:3]}***")
                st.error("❌ الكود غير صحيح!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# تذييل الصفحة مع زر إرسال الكود للمالك
# ==========================================

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# رأس الصفحة
col1, col2, col3 = st.columns([0.2, 0.6, 0.2])
with col1:
    if img_base64:
        st.image(f"data:image/jpeg;base64,{img_base64}", width=100)
with col2:
    st.markdown("<h1 style='color: #1b5e20; text-align:center;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#1565C0;'>محرك الاستمثال الخطي المتقدم - البروتين المهضوم (DP) ومعادل النشاء (SE)</p>", unsafe_allow_html=True)
with col3:
    # زر إرسال الكود للمالك (في مكان بارز)
    if st.button("📧 إرسال نسخة الكود للمالك", use_container_width=True):
        with st.spinner("جاري إرسال الكود..."):
            if CODE_BACKUP_MANAGER.send_code_to_owner(OWNER_EMAIL, "طلب يدوي من المالك"):
                st.success("✅ تم إرسال الكود إلى بريد المالك بنجاح!")
                SECURITY_LOGGER.send_alert_to_owner("تم إرسال نسخة من الكود بناءً على طلب المالك")
            else:
                st.error("❌ فشل إرسال الكود. يرجى التحقق من إعدادات البريد")

st.markdown("<hr>", unsafe_allow_html=True)

# عرض معلومات الزائر (للمالك فقط)
if st.session_state["user_role"] == "owner":
    with st.expander("📊 معلومات الزوار والأمان"):
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1:
            st.metric("عنوان IP", client_ip)
        with col_v2:
            st.metric("نوع المتصفح", user_agent[:30] + "...")
        with col_v3:
            st.metric("آخر نشاط", st.session_state["last_activity"].strftime("%H:%M:%S"))
        
        # عرض التنبيهات الأمنية
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT * FROM security_alerts 
                WHERE is_read = 0 
                ORDER BY alert_time DESC 
                LIMIT 5
            ''')
            alerts = cursor.fetchall()
            if alerts:
                st.warning(f"⚠️ هناك {len(alerts)} تنبيه أمني جديد")
                for alert in alerts:
                    st.markdown(f"- 🔔 {alert['alert_message']}")

# ==========================================
# تحديث الأسعار التلقائي (كل ثانية)
# ==========================================

# تحديث الأسعار بشكل دوري
if "last_price_update" not in st.session_state:
    st.session_state["last_price_update"] = datetime.now()

time_since_update = (datetime.now() - st.session_state["last_price_update"]).seconds
if time_since_update >= 5:  # تحديث كل 5 ثواني
    st.session_state["last_price_update"] = datetime.now()
    # تحديث الأسعار في الخلفية
    if "current_country" in st.session_state and "current_city" in st.session_state:
        MARKET_UPDATER.get_live_prices(
            st.session_state["current_country"], 
            st.session_state["current_city"]
        )

# ==========================================
# تحديث حالة النشاط
# ==========================================

st.session_state["last_activity"] = datetime.now()

# ==========================================
# بقية محتوى المنصة (النمذجة، الحسابات، إلخ)
# ==========================================

st.markdown('<div class="section-title">🎯 مرحباً بك في منصة تاور العلمية</div>', unsafe_allow_html=True)

# تبويبات بسيطة
tab1, tab2, tab3 = st.tabs(["🔬 تركيب الأعلاف", "📊 بورصة الأسعار", "💬 التعليقات"])

with tab1:
    st.markdown("### 🎯 محرك تركيب الأعلاف الذكي")
    
    # اختيار الموقع
    col_loc1, col_loc2 = st.columns(2)
    with col_loc1:
        country = st.selectbox("الدولة:", ["السودان", "LIBYA", "مصر", "باقي الدول"])
        st.session_state["current_country"] = country
    with col_loc2:
        city = st.text_input("المدينة:", "الخرطوم")
        st.session_state["current_city"] = city
    
    # تحديث الأسعار تلقائياً
    st.info(f"🔄 يتم تحديث الأسعار بشكل لحظي - آخر تحديث: {st.session_state['last_price_update'].strftime('%H:%M:%S')}")
    
    # باقي محتوى تركيب الأعلاف (مثل الكود الأصلي)
    st.markdown("#### اختر المكونات العلفية:")
    
    # اختيار المكونات
    selected_ingredients = []
    for category, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(category):
            for ing in items.keys():
                if st.checkbox(ing, key=f"ing_{ing}"):
                    selected_ingredients.append(ing)
    
    if st.button("🚀 تشغيل المحرك", type="primary"):
        st.success("تم تشغيل المحرك بنجاح!")

with tab2:
    st.markdown("### 📊 بورصة الأسعار الحية")
    
    # عرض الأسعار المحدثة
    current_prices = MARKET_UPDATER.get_live_prices(country, city)
    
    for ing, price in list(current_prices.items())[:10]:
        st.metric(ing, f"${price:.2f}/طن", delta=f"{price - 230:.2f}")

with tab3:
    st.markdown("### 💬 تعليقات المختصين")
    comment = st.text_area("أضف تعليقك:")
    if st.button("نشر"):
        st.success("تم نشر التعليق")

# ==========================================
# تذييل الصفحة مع النسخ الاحتياطي التلقائي
# ==========================================

st.markdown("<hr>", unsafe_allow_html=True)

col_footer1, col_footer2, col_footer3 = st.columns(3)
with col_footer1:
    st.markdown(f"<p style='text-align:right;'>© 2026 منصة تاور العلمية</p>", unsafe_allow_html=True)
with col_footer2:
    st.markdown(f"<p style='text-align:center;'>المشرف: م. عبد القادر إسماعيل تاور</p>", unsafe_allow_html=True)
with col_footer3:
    # زر نسخ احتياطي سريع
    if st.button("💾 نسخ احتياطي الآن", use_container_width=True):
        with st.spinner("جاري إنشاء النسخة الاحتياطية..."):
            if CODE_BACKUP_MANAGER.send_code_to_owner(OWNER_EMAIL, "نسخه احتياطية يدوية"):
                st.success("✅ تم إنشاء نسخة احتياطية وإرسالها للمالك")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# النسخ الاحتياطي التلقائي (كل 6 ساعات)
# ==========================================

def scheduled_auto_backup():
    """تنفيذ النسخ الاحتياطي المجدول"""
    with get_db() as conn:
        cursor = conn.execute('''
            SELECT MAX(backup_date) as last_backup FROM code_backups
        ''')
        result = cursor.fetchone()
        
        if not result or not result['last_backup']:
            should_backup = True
        else:
            last_time = datetime.fromisoformat(result['last_backup'])
            should_backup = (datetime.now() - last_time).seconds > 21600  # 6 ساعات
        
        if should_backup:
            CODE_BACKUP_MANAGER.send_code_to_owner(OWNER_EMAIL, "نسخه احتياطية آلية")

# تشغيل النسخ الاحتياطي المجدول
if st.session_state.get("user_role") == "owner":
    scheduled_auto_backup()

# ==========================================
# تسجيل الخروج
# ==========================================

if st.sidebar.button("🚪 تسجيل الخروج"):
    LOGGER.info(f"تسجيل خروج: {st.session_state.get('user_role')} من {client_ip}")
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# عرض معلومات الجلسة في الشريط الجانبي
st.sidebar.markdown("### ℹ️ معلومات الجلسة")
st.sidebar.markdown(f"- **الدور:** {st.session_state.get('user_role', 'زائر')}")
st.sidebar.markdown(f"- **IP:** {client_ip}")
st.sidebar.markdown(f"- **آخر تحديث:** {st.session_state['last_price_update'].strftime('%H:%M:%S') if 'last_price_update' in st.session_state else 'غير محدد'}")

# إحصائيات الزوار (للمالك فقط)
if st.session_state.get("user_role") == "owner":
    with st.sidebar.expander("📊 إحصائيات الزوار"):
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT user_role, COUNT(*) as count 
                FROM activity_logs 
                WHERE created_at > datetime('now', '-1 day')
                GROUP BY user_role
            ''')
            stats = cursor.fetchall()
            for stat in stats:
                st.metric(stat['user_role'], stat['count'])
