#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف
الإصدار المتكامل v7.1 - إصلاح مشكلة الترتيب
"""

# ==========================================
# 1. المكتبات الأساسية (كما هي)
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
from typing import Dict, List, Tuple, Optional, Any, Union
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# 2. المكتبات العلمية (كما هي)
# ==========================================

from scipy.optimize import linprog
from scipy.spatial import ConvexHull
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression

# ==========================================
# 3. مكتبات التصور (كما هي)
# ==========================================

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 4. مكتبات النص العربي (كما هي)
# ==========================================

import arabic_reshaper
from bidi.algorithm import get_display

# ==========================================
# 5. مكتبات PDF (كما هي)
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
# 6. مكتبات الباركود (كما هي)
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
# 7. إعدادات التحذيرات والمجلدات
# ==========================================

warnings.filterwarnings('ignore')
load_dotenv()

# إنشاء المجلدات
folders = [
    "logs", "backups", "data", "temp", "visitors", "code_backups", 
    "reports", "exports", "charts", "models", "cache", "lab_results", 
    "formulas_archive", "price_history", "farm_data"
]
for folder in folders:
    Path(folder).mkdir(exist_ok=True)

# ==========================================
# 8. إعدادات Streamlit
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
# 9. نظام التسجيل المتقدم
# ==========================================

class AdvancedLogger:
    """نظام تسجيل متقدم"""
    
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
        
        # معالج رئيسي
        main_handler = logging.handlers.RotatingFileHandler(
            'logs/tower_main.log', 
            maxBytes=50*1024*1024, 
            backupCount=20, 
            encoding='utf-8'
        )
        formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
        main_handler.setFormatter(formatter)
        self.main_logger.addHandler(main_handler)
        
        # معالج أمني
        security_handler = logging.handlers.RotatingFileHandler(
            'logs/security.log', 
            maxBytes=20*1024*1024, 
            backupCount=30, 
            encoding='utf-8'
        )
        security_handler.setFormatter(formatter)
        self.security_logger.addHandler(security_handler)
        
        # معالج المستخدمين
        user_handler = logging.handlers.RotatingFileHandler(
            'logs/users.log', 
            maxBytes=10*1024*1024, 
            backupCount=15, 
            encoding='utf-8'
        )
        user_handler.setFormatter(formatter)
        self.user_logger.addHandler(user_handler)
        
        # معالج الأخطاء
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
        log_func = getattr(self.security_logger, severity.lower(), self.security_logger.info)
        log_func(f"{event_type}: {details}")

LOGGER = AdvancedLogger()

# ==========================================
# 10. إعدادات البريد (آمنة)
# ==========================================

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "abukram128@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "abukram128@gmail.com")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "+249123533489")
GOOGLE_FORM_URL = os.getenv("GOOGLE_FORM_URL", "https://forms.google.com/YOUR_FORM_URL")

if not SENDER_PASSWORD:
    LOGGER.security_logger.warning("SENDER_PASSWORD غير محددة في متغيرات البيئة")

# مسارات الصور
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

@st.cache_data(ttl=3600)
def get_image_base64(paths: List[str]) -> Optional[str]:
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
# 11. المكتبات والبيانات (تُعرّف قبل أي كلاس يستخدمها)
# ==========================================

# ==========================================
# 11.1 بيانات السلالات والاحتياجات القياسية
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
# 11.2 المكتبة الكاملة للمواد العلفية
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
# 11.3 أكواد الدخول
# ==========================================

CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

# ==========================================
# 11.4 أسعار الصرف والدول
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
# 11.5 صور الحيوانات
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
# 12. نظام قاعدة البيانات
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

def column_exists(conn, table_name: str, column_name: str) -> bool:
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def init_database():
    with get_db() as conn:
        # جدول الخلطات
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
        
        # جدول التحاليل
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
        
        # جدول النشاطات
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
        
        # جدول الزوار
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
        
        # جدول الأسعار
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

if "db_initialized" not in st.session_state:
    init_database()
    st.session_state["db_initialized"] = True

# ==========================================
# 13. نظام إدارة المخزون (بعد تعريف BIG_FEEDS_LIBRARY)
# ==========================================

class InventoryManager:
    """نظام إدارة المخزون المتقدم"""
    
    def __init__(self):
        self.inventory_file = "data/inventory_data.json"
        self.load_inventory()
    
    def load_inventory(self):
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
        try:
            with open(self.inventory_file, 'w', encoding='utf-8') as f:
                json.dump(st.session_state["inventory"], f, ensure_ascii=False, indent=2)
        except Exception as e:
            LOGGER.error_logger.error(f"فشل حفظ المخزون: {e}")
    
    def get_item(self, item_name: str) -> Optional[Dict]:
        return st.session_state["inventory"].get(item_name)
    
    def update_item(self, item_name: str, quantity: float, threshold: Optional[float] = None):
        if item_name in st.session_state["inventory"]:
            st.session_state["inventory"][item_name]["quantity"] = quantity
            if threshold is not None:
                st.session_state["inventory"][item_name]["min_threshold"] = threshold
            st.session_state["inventory"][item_name]["last_updated"] = datetime.now().isoformat()
            self.save_inventory()
    
    def deduct_items(self, formula: Dict[str, float], tons: float) -> bool:
        can_deduct = True
        for ing, pct in formula.items():
            req_amount = (pct / 100) * tons
            current = st.session_state["inventory"].get(ing, {}).get("quantity", 0)
            if current < req_amount:
                can_deduct = False
                LOGGER.main_logger.warning(f"مخزون غير كافٍ: {ing}")
                break
        
        if can_deduct:
            for ing, pct in formula.items():
                req_amount = (pct / 100) * tons
                st.session_state["inventory"][ing]["quantity"] -= req_amount
            self.save_inventory()
        
        return can_deduct
    
    def check_stock_levels(self) -> Dict[str, str]:
        warnings = {}
        for item, data in st.session_state["inventory"].items():
            qty = data["quantity"]
            threshold = data["min_threshold"]
            if qty <= 0:
                warnings[item] = "نفذ المخزون"
            elif qty < threshold:
                warnings[item] = "منخفض"
        return warnings

# إنشاء مدير المخزون (الآن BIG_FEEDS_LIBRARY معرّفة)
INVENTORY_MANAGER = InventoryManager()

# ==========================================
# 14. بقية الكلاسات والدوال
# ==========================================

class SecureCodeSender:
    """نظام إرسال الكود الآمن"""
    
    def __init__(self):
        self.sender_email = SENDER_EMAIL
        self.sender_password = SENDER_PASSWORD
        self.owner_email = OWNER_EMAIL
    
    def send_code_to_email(self, email: str, reason: str = "طلب يدوي") -> bool:
        if not self.sender_password:
            LOGGER.security_logger.error("محاولة إرسال كود بدون كلمة مرور")
            return False
        
        try:
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            try:
                with open(__file__, 'r', encoding='utf-8') as f:
                    code_content = f.read()
            except Exception as e:
                LOGGER.error_logger.error(f"فشل قراءة الكود: {e}")
                return False
            
            file_hash = hashlib.sha256(code_content.encode()).hexdigest()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
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
            
            attachment = MIMEText(code_content, 'plain', 'utf-8')
            attachment.add_header(
                'Content-Disposition', 
                'attachment', 
                filename=f"tower_platform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
            )
            msg.attach(attachment)
            
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
# 15. بقية الكود (الأمان، المساعدات، PDF، إلخ)
# ==========================================

class SecurityMonitor:
    """نظام مراقبة الأمان"""
    
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.blocked_ips = set()
        self.max_attempts = 5
        self.lockout_time = 300
    
    def get_client_ip(self) -> str:
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
        if ip in self.blocked_ips:
            return True
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
    
    def log_failed_attempt(self, code_attempt: str = ""):
        ip = self.get_client_ip()
        self.failed_attempts[ip].append(datetime.now())
        
        recent_attempts = [
            t for t in self.failed_attempts[ip] 
            if (datetime.now() - t).seconds < self.lockout_time
        ]
        self.failed_attempts[ip] = recent_attempts
        
        if len(recent_attempts) >= self.max_attempts:
            self.blocked_ips.add(ip)
            try:
                with get_db() as conn:
                    conn.execute(
                        'INSERT OR REPLACE INTO blocked_ips (ip_address, block_reason, blocked_at) VALUES (?, ?, ?)',
                        (ip, f"{self.max_attempts} محاولات فاشلة", datetime.now().isoformat())
                    )
            except:
                pass
        
        LOGGER.security_logger.warning(f"محاولة فاشلة من {ip}")
    
    def log_visitor(self, user_role: Optional[str] = None, action: str = "visit"):
        ip = self.get_client_ip()
        user_agent = self.get_user_agent()
        
        if self.is_ip_blocked(ip):
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
    
    def get_user_agent(self) -> str:
        try:
            if hasattr(st, 'context') and hasattr(st.context, 'headers'):
                return st.context.headers.get('User-Agent', 'unknown')[:200]
            return 'unknown'
        except:
            return 'unknown'

SECURITY = SecurityMonitor()

# ==========================================
# 16. دوال مساعدة
# ==========================================

class ArabicTextProcessor:
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

def get_standard_requirements(sector: str, breed: str, production: str) -> Dict:
    try:
        if sector in BREEDS_STANDARDS:
            for b in BREEDS_STANDARDS[sector]:
                if breed in b or b in breed:
                    return BREEDS_STANDARDS[sector][b]
        return {"CP": 16.0, "DP": 13.4, "SE": 65.0, "ME": 2600, "P/E": 6.2}
    except Exception:
        return {"CP": 16.0, "DP": 13.4, "SE": 65.0, "ME": 2600, "P/E": 6.2}

# ==========================================
# 17. مولد PDF
# ==========================================

class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        if os.path.exists("Amiri-Regular.ttf"):
            try:
                pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
                self.font_name = 'Amiri'
            except Exception:
                pass

    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, include_charts=True) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []

        def p(text, size=12, align=TA_RIGHT, color=HexColor('#000000')):
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, ParagraphStyle('style', fontName=self.font_name, fontSize=size, alignment=align, textColor=color, spaceAfter=6, leading=size*1.5))

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

        if include_charts and len(formula) > 1:
            try:
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots(figsize=(6, 4))
                names = list(formula.keys())
                vals = list(formula.values())
                colors = ['#1b5e20','#2e7d32','#388e3c','#43a047','#4caf50','#66bb6a']
                ax.pie(vals, labels=None, autopct='%1.1f%%', colors=colors[:len(names)])
                ax.legend([arabic_processor.fix_arabic_text(n) for n in names], title=arabic_processor.fix_arabic_text("المكونات"), loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=8)
                ax.set_title(arabic_processor.fix_arabic_text('توزيع المكونات'), fontsize=12)
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=400, height=230))
            except Exception as e:
                LOGGER.error_logger.error(f"فشل إنشاء المخطط في PDF: {e}")

        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026", size=9, align=TA_CENTER, color=HexColor('#666666')))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# ==========================================
# 18. إدارة مزارع الدجاج
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
# 19. تهيئة متغيرات الجلسة
# ==========================================

def init_session_state():
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
        "poultry_farms": {},
        "shared_comments": "• مرحباً بكم في منصة تاور العلمية\n• نرحب بتعليقاتكم واقتراحاتكم\n",
        "login_attempts": 0,
        "last_login_time": None,
        "login_welcome_shown": False,
        "whatsapp_alerts_sent": {},
        "broiler_farms": {},
        "lab_results": {},
        "db_initialized": True,
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

init_session_state()

# ==========================================
# 20. بقية الواجهة (CSS، بوابة الدخول، التبويبات، إلخ)
# ==========================================

# ... (باقي الكود كما هو من الإصدار السابق)

print("✅ تم تحميل المنصة بنجاح!")
