# ============================================================================
# ████████████████████████████████████████████████████████████████████████████
# █       تاور نولجي TAWOR NOLOGY — الإصدار 20.0 النهائي المدمج            █
# █       للإنتاج الحيواني وتركيب وتحليل الأعلاف وتصميم الحظائر              █
# █       إشراف: م. عبدالقادر إسماعيل تاور                                   █
# █       🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌                    █
# █   ✨ 23 تبويب  ✨ معمل تحليل شامل  ✨ مصمم حظائر  ✨ مستشار AI          █
# █   ✨ واجهة محسّنة بدون تداخل حروف  ✨ تقارير صوتية  ✨ PDF احترافي      █
# ████████████████████████████████████████████████████████████████████████████
# ============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import json, os, base64, time, re, io, sqlite3, hashlib, secrets, warnings
import urllib.parse, urllib.request, smtplib, math, random
from datetime import datetime, timedelta, date
from functools import lru_cache
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, asdict, field
from collections import defaultdict

warnings.filterwarnings('ignore')

# مكتبات علمية
try:
    from scipy.optimize import linprog
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from sklearn.linear_model import LinearRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Wedge, Rectangle
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image as PILImage
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor, white
    from reportlab.platypus import (Table, TableStyle, Paragraph, Spacer,
                                     Image as RLImage, SimpleDocTemplate,
                                     PageBreak, HRFlowable)
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_AVAILABLE = True
except ImportError:
    ARABIC_AVAILABLE = False

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

try:
    from PIL import Image as PILImage_module
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ═════════════════════════════════════════════════════════════════════════════
# القسم 1: الدعاء
# ═════════════════════════════════════════════════════════════════════════════

DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي ابتسام"
DUA_FULL = ("رحم الله والدي إسماعيل تاور وأختي ابتسام، وأسكنهما فسيح جناته، "
            "وجعل قبرهما روضة من رياض الجنة")
DUA_QURAN = "﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾"
DUA_VERSE = "﴿ وَقُل رَّبِّ ارْحَمْهُمَا كَمَا رَبَّيَانِي صَغِيرًا ﴾"
DUA_VISITOR_BANNER = """
🕌 <b>إلى زوارنا الكرام:</b><br>
هذه المنصة صدقةٌ جارية عن <b>والدي إسماعيل تاور</b> و<b>أختي ابتسام</b>.<br>
نسألكم بظهر الغيب أن تشاركونا الدعاء لهما. 🤲
"""


# ═════════════════════════════════════════════════════════════════════════════
# القسم 2: الإعدادات العامة
# ═════════════════════════════════════════════════════════════════════════════

APP_NAME = "تاور نولجي Tawor Nology"
APP_TAGLINE = "للإنتاج الحيواني وتغذية الحيوان"
APP_VERSION = "20.0"
SUPERVISOR = "م. عبدالقادر إسماعيل تاور"
SUPERVISOR_TITLE = "اختصاصي تغذية الحيوان"
OWNER_CODE = "202687"
PLATFORM_URL = "https://tawor-nology.streamlit.app"
WHATSAPP_NUMBER = "+249123533489"
OWNER_EMAIL = "abukram128@gmail.com"
SENDER_EMAIL = "abukram128@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]
LOGO_OPTIONS = ["logo.png", "logo.jpg", "14686.jpg"]

st.set_page_config(
    page_title=f"{APP_NAME} | {APP_TAGLINE}",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 3: معالج النصوص العربية (إصلاح تداخل الحروف)
# ═════════════════════════════════════════════════════════════════════════════

FONT_DIR = "fonts"
os.makedirs(FONT_DIR, exist_ok=True)

ARABIC_FONT_URLS = [
    ("https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf",
     "Amiri-Regular.ttf"),
]


class ArabicFontManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.font_name = 'Helvetica'
        self.font_bold = 'Helvetica-Bold'
        self.ready = False
        if not REPORTLAB_AVAILABLE:
            return
        paths = [
            os.path.join(FONT_DIR, "Amiri-Regular.ttf"),
            "Amiri-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
        for p in paths:
            if os.path.exists(p):
                if self._register(p):
                    return
        for url, fn in ARABIC_FONT_URLS:
            try:
                target = os.path.join(FONT_DIR, fn)
                if not os.path.exists(target):
                    urllib.request.urlretrieve(url, target)
                if self._register(target):
                    return
            except Exception:
                continue

    def _register(self, path):
        try:
            pdfmetrics.registerFont(TTFont('TaworArabic', path))
            self.font_name = 'TaworArabic'
            self.font_bold = 'TaworArabic'
            self.ready = True
            return True
        except Exception:
            return False


font_mgr = ArabicFontManager()


class ArabicProcessor:
    """معالج النصوص العربية — يحل مشكلة تداخل الحروف في PDF"""
    @staticmethod
    @lru_cache(maxsize=5000)
    def fix(text):
        if text is None or text == "":
            return ""
        text = str(text)
        if not ARABIC_AVAILABLE:
            return text
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped, base_dir='R')
        except Exception:
            return text


arp = ArabicProcessor()


def ar(text):
    """يُستخدم فقط قبل reportlab (PDF)"""
    return arp.fix(text)


# ═════════════════════════════════════════════════════════════════════════════
# دوال عرض النصوص العربية بدون تداخل (للاستخدام في Streamlit)
# ═════════════════════════════════════════════════════════════════════════════

def md_ar(text, size=14, color="#1a1a1a", align="right", bold=False,
           margin_bottom=8):
    """عرض نص عربي في Streamlit بدون تداخل حروف"""
    weight = "700" if bold else "400"
    st.markdown(
        f'<div style="direction:rtl; text-align:{align}; '
        f'font-size:{size}px; color:{color}; font-weight:{weight}; '
        f'font-family:Tajawal, Cairo, sans-serif; line-height:1.85; '
        f'margin-bottom:{margin_bottom}px;">{text}</div>',
        unsafe_allow_html=True)


def card_ar(title, body, bg="#e8f5e9", border="#2e7d32", title_color="#1b5e20"):
    """بطاقة عربية بتنسيق صحيح بدون تداخل"""
    st.markdown(
        f'<div style="direction:rtl; text-align:right; background:{bg}; '
        f'padding:16px 20px; border-radius:12px; margin-bottom:10px; '
        f'border-right:5px solid {border}; '
        f'font-family:Tajawal, Cairo, sans-serif;">'
        f'<b style="font-size:16px; color:{title_color};">{title}</b>'
        f'<div style="font-size:14px; color:#333; margin-top:6px; '
        f'line-height:1.7;">{body}</div></div>',
        unsafe_allow_html=True)


def metric_ar(label, value, color="#2e7d32", icon=""):
    """عرض بطاقة قياس عربية"""
    st.markdown(
        f'<div style="direction:rtl; text-align:center; background:white; '
        f'padding:16px 12px; border-radius:14px; border-top:4px solid {color}; '
        f'box-shadow:0 4px 14px rgba(0,0,0,0.08); '
        f'font-family:Tajawal, Cairo, sans-serif; margin-bottom:8px;">'
        f'<div style="font-size:0.95rem; color:#666; font-weight:600;">'
        f'{icon} {label}</div>'
        f'<div style="font-size:1.7rem; color:{color}; font-weight:900; '
        f'margin-top:6px;">{value}</div></div>',
        unsafe_allow_html=True)


def h_ar(text, level=3, color="#1b5e20", margin_top=20):
    """عنوان عربي"""
    sizes = {1: 28, 2: 22, 3: 18, 4: 16, 5: 14}
    st.markdown(
        f'<h{level} style="direction:rtl; text-align:right; '
        f'color:{color}; font-family:Tajawal, Cairo, sans-serif; '
        f'font-weight:800; margin-top:{margin_top}px; '
        f'margin-bottom:12px;">{text}</h{level}>',
        unsafe_allow_html=True)


def list_ar(items, bullet="▪️", color="#333"):
    """قائمة عربية"""
    html = "".join(
        f'<li style="margin-bottom:6px; color:{color};">{bullet} {item}</li>'
        for item in items)
    st.markdown(
        f'<ul style="direction:rtl; text-align:right; list-style:none; '
        f'padding-right:0; font-family:Tajawal, Cairo, sans-serif; '
        f'font-size:14px; line-height:1.7;">{html}</ul>',
        unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 4: مكتبة الأعلاف
# ═════════════════════════════════════════════════════════════════════════════

BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3, "Ca": 0.02, "P": 0.27},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4, "Ca": 0.02, "P": 0.26},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5, "Ca": 0.05, "P": 0.35},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8, "Ca": 0.03, "P": 0.30},
        "قمح محلي": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6, "Ca": 0.04, "P": 0.32},
        "جريش أرز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2, "Ca": 0.06, "P": 0.30},
        "دخن محلي": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2, "Ca": 0.05, "P": 0.31},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0, "Ca": 0.08, "P": 0.35},
    },
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5, "Ca": 0.20, "P": 0.65},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0, "Ca": 0.35, "P": 0.65},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2, "Ca": 0.35, "P": 0.65},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5, "Ca": 0.40, "P": 1.00},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5, "Ca": 0.20, "P": 1.10},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8, "Ca": 0.35, "P": 0.85},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5, "Ca": 2.00, "P": 1.20},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5, "Ca": 0.15, "P": 0.50},
        "كسب بذور اللفت (كانولا)": {"CP": 36.0, "DC": 0.82, "SE": 60.0, "NDF": 28.0, "ADF": 18.0, "EE": 3.5, "ASH": 6.5, "Ca": 0.65, "P": 1.10},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5, "Ca": 0.30, "P": 0.55},
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5, "Ca": 0.12, "P": 1.10},
        "نخالة ذرة": {"CP": 9.5, "DC": 0.65, "SE": 40.0, "NDF": 40.0, "ADF": 15.0, "EE": 4.0, "ASH": 2.0, "Ca": 0.10, "P": 0.75},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5, "Ca": 1.50, "P": 0.25},
        "برسيم حجازي": {"CP": 18.0, "DC": 0.62, "SE": 38.0, "NDF": 40.0, "ADF": 30.0, "EE": 2.2, "ASH": 11.0, "Ca": 1.60, "P": 0.26},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5, "Ca": 0.70, "P": 0.05},
        "تبن قمح": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.30, "P": 0.08},
        "تبن فول": {"CP": 4.5, "DC": 0.40, "SE": 22.0, "NDF": 68.0, "ADF": 42.0, "EE": 1.2, "ASH": 7.5, "Ca": 0.35, "P": 0.10},
        "قشور الفول السوداني": {"CP": 6.5, "DC": 0.40, "SE": 22.0, "NDF": 58.0, "ADF": 38.0, "EE": 2.5, "ASH": 4.0, "Ca": 0.20, "P": 0.12},
        "سرسة الأرز": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5, "Ca": 0.15, "P": 0.08},
        "مخلفات النخيل": {"CP": 6.5, "DC": 0.70, "SE": 60.0, "NDF": 25.0, "ADF": 15.0, "EE": 5.0, "ASH": 3.5, "Ca": 0.15, "P": 0.15},
        "نخالة الأرز الدهنية": {"CP": 12.5, "DC": 0.70, "SE": 55.0, "NDF": 30.0, "ADF": 15.0, "EE": 15.0, "ASH": 8.0, "Ca": 0.10, "P": 1.40},
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5, "Ca": 5.50, "P": 3.20},
        "مسحوق أسماك 72%": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5, "Ca": 4.80, "P": 2.80},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5, "Ca": 9.00, "P": 4.50},
        "مسحوق الدم": {"CP": 80.0, "DC": 0.65, "SE": 55.0, "NDF": 1.0, "ADF": 0.5, "EE": 1.5, "ASH": 6.0, "Ca": 0.30, "P": 0.30},
        "مسحوق ريش": {"CP": 82.0, "DC": 0.70, "SE": 60.0, "NDF": 1.5, "ADF": 1.0, "EE": 3.0, "ASH": 4.0, "Ca": 0.25, "P": 0.35},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5, "Ca": 2.50, "P": 1.20},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5, "Ca": 3.00, "P": 1.50},
        "بروتين مصل الحليب (WPC)": {"CP": 80.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 3.0, "ASH": 3.0, "Ca": 0.50, "P": 0.40},
    },
    "🌿 الأعلاف الخضراء المائية": {
        "أزولا مجففة": {"CP": 24.0, "DC": 0.65, "SE": 45.0, "NDF": 38.0, "ADF": 25.0, "EE": 3.5, "ASH": 18.0, "Ca": 2.00, "P": 0.60},
        "سبيرولينا": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 5.0, "ADF": 3.0, "EE": 6.0, "ASH": 10.0, "Ca": 1.20, "P": 0.90},
        "كلوريلا": {"CP": 55.0, "DC": 0.80, "SE": 60.0, "NDF": 6.0, "ADF": 3.5, "EE": 8.0, "ASH": 12.0, "Ca": 0.50, "P": 1.20},
        "طحالب بحرية": {"CP": 15.0, "DC": 0.60, "SE": 30.0, "NDF": 25.0, "ADF": 15.0, "EE": 2.0, "ASH": 30.0, "Ca": 1.50, "P": 0.30},
    },
    "🌰 الزيوت النباتية والحيوانية": {
        "زيت ذرة": {"CP": 0.0, "DC": 0.0, "SE": 220.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "طاقة عالية (9000 kcal/kg)", "max_poultry": 6.0, "max_ruminant": 5.0, "source": "NRC 2012"},
        "زيت فول الصويا": {"CP": 0.0, "DC": 0.0, "SE": 215.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "أشهر زيوت الأعلاف", "max_poultry": 8.0, "max_ruminant": 5.0, "source": "Ross 308"},
        "زيت عباد الشمس": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "غني بأوميغا 6", "max_poultry": 6.0, "max_ruminant": 4.0, "source": "NRC 2007"},
        "زيت الكتان": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "غني بأوميغا 3", "max_poultry": 3.0, "max_ruminant": 3.0, "source": "NRC 2007 Horses"},
        "زيت جوز الهند": {"CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "دهون MCT", "max_poultry": 5.0, "max_ruminant": 3.0, "source": "NRC 2012"},
        "زيت النخيل": {"CP": 0.0, "DC": 0.0, "SE": 215.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "مقاوم للأكسدة", "max_poultry": 6.0, "max_ruminant": 5.0, "source": "NRC 2012"},
        "زيت الكانولا": {"CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "متوازن أوميغا", "max_poultry": 5.0, "max_ruminant": 5.0, "source": "NRC 2012"},
        "زيت السمسم": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "مضادات أكسدة", "max_poultry": 4.0, "max_ruminant": 3.0, "source": "NRC 2007"},
        "زيت الزيتون": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "أوميغا 9، مضاد أكسدة", "max_poultry": 4.0, "max_ruminant": 4.0, "source": "INRA 2018"},
        "زيت بذرة القطن": {"CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "جوسيبول", "max_poultry": 3.0, "max_ruminant": 5.0, "source": "NRC 2012"},
        "زيت القرطم": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "أوميغا 6 عالي", "max_poultry": 4.0, "max_ruminant": 3.0, "source": "NRC 2012"},
        "زيت الفول السوداني": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "طاقة عالية", "max_poultry": 5.0, "max_ruminant": 4.0, "source": "NRC 2012"},
        "شحم حيواني (Tallow)": {"CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "طاقة عالية", "max_poultry": 6.0, "max_ruminant": 5.0, "source": "NRC 2012"},
        "زيت السمك (Fish Oil)": {"CP": 0.0, "DC": 0.0, "SE": 235.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "EPA/DHA", "max_poultry": 2.0, "max_ruminant": 2.0, "source": "NRC Fish"},
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3, "Ca": 0.0, "P": 0.0},
        "ثريونين نقي": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0},
        "تريبتوفان نقي": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0},
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 8.0},
        "بريمكس بياض": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 22.0, "P": 7.0},
        "بريمكس أبقار": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0},
        "بريمكس مجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 9.0},
        "بريمكس خيول": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 8.0},
        "بريمكس إبل": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0},
        "بريمكس أسماك": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 7.0},
        "إنزيم الفايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0, "Ca": 0.0, "P": 0.0},
        "إنزيم NSP": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0, "Ca": 0.0, "P": 0.0},
        "خمائر حية": {"CP": 45.0, "DC": 0.75, "SE": 30.0, "NDF": 8.0, "ADF": 4.0, "EE": 1.0, "ASH": 8.0, "Ca": 0.15, "P": 1.20},
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 38.0, "P": 0.0},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5, "Ca": 23.0, "P": 18.0},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9, "Ca": 0.0, "P": 0.0},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 0.0, "P": 0.0},
        "أكسيد المغنيسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 0.0, "P": 0.0},
        "يوريا علفية محصنة": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0, "Ca": 0.0, "P": 0.0},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Ca": 0.0, "P": 0.0},
    },
    "🍼 مكونات بدائل الحليب": {
        "مصل الحليب المجفف (Whey)": {"CP": 12.0, "DC": 0.95, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.0, "Ca": 0.70, "P": 0.60},
        "حليب مجفف خالي الدسم": {"CP": 34.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.5, "Ca": 1.30, "P": 1.00},
        "حليب مجفف كامل الدسم": {"CP": 26.0, "DC": 0.95, "SE": 55.0, "NDF": 0.0, "ADF": 0.0, "EE": 28.0, "ASH": 6.0, "Ca": 0.95, "P": 0.75},
        "دهن نباتي": {"CP": 0.0, "DC": 0.0, "SE": 10.0, "NDF": 0.0, "ADF": 0.0, "EE": 99.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0},
        "بروتين الصويا المركز": {"CP": 65.0, "DC": 0.90, "SE": 30.0, "NDF": 2.0, "ADF": 1.0, "EE": 1.0, "ASH": 5.5, "Ca": 0.30, "P": 0.70},
        "مالتودكسترين": {"CP": 0.0, "DC": 0.0, "SE": 90.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0},
        "لاكتوز نقي": {"CP": 0.0, "DC": 0.0, "SE": 85.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0},
    },
}

FLAT_FEED_DB = {}
for category, items in BIG_FEEDS_LIBRARY.items():
    for feed_name, nutrition in items.items():
        FLAT_FEED_DB[feed_name] = nutrition


# ═════════════════════════════════════════════════════════════════════════════
# القسم 5: معايير الزيوت
# ═════════════════════════════════════════════════════════════════════════════

MAX_OIL_PERCENTAGE = {
    "دواجن_بادي": {"max": 8.0, "optimal": 5.0, "source": "Ross 308 2020"},
    "دواجن_نامي": {"max": 7.0, "optimal": 4.5, "source": "Ross 308 2020"},
    "دواجن_ناهي": {"max": 7.0, "optimal": 4.0, "source": "Ross 308 2020"},
    "دواجن_بياض": {"max": 5.0, "optimal": 2.5, "source": "NRC 1994"},
    "سمان_بادي": {"max": 6.0, "optimal": 4.0, "source": "NRC Quail"},
    "أبقار_حليب_عالي": {"max": 6.0, "optimal": 4.0, "source": "NRC 2001"},
    "أبقار_حليب_متوسط": {"max": 5.0, "optimal": 3.5, "source": "NRC 2001"},
    "أبقار_حليب_منخفض": {"max": 5.0, "optimal": 3.0, "source": "NRC 2001"},
    "أبقار_تسمين_مكثف": {"max": 6.0, "optimal": 4.5, "source": "NRC 2001"},
    "أبقار_تسمين_عادي": {"max": 5.0, "optimal": 3.5, "source": "NRC 2001"},
    "أغنام_تسمين_مكثف": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "أغنام_تسمين_عادي": {"max": 4.5, "optimal": 3.0, "source": "NRC 2007"},
    "أغنام_حليب": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "أغنام_صيانة": {"max": 3.5, "optimal": 2.0, "source": "NRC 2007"},
    "ماعز_تسمين": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "ماعز_حليب": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "ماعز_صيانة": {"max": 3.5, "optimal": 2.0, "source": "NRC 2007"},
    "إبل_نمو": {"max": 5.0, "optimal": 3.5, "source": "FAO 2010"},
    "إبل_تسمين": {"max": 6.0, "optimal": 4.0, "source": "FAO 2010"},
    "إبل_حليب": {"max": 5.0, "optimal": 3.5, "source": "FAO 2010"},
    "إبل_سباق": {"max": 8.0, "optimal": 6.0, "source": "FAO 2010"},
    "إبل_صيانة": {"max": 3.5, "optimal": 2.0, "source": "FAO 2010"},
    "خيول_رياضة_مكثف": {"max": 10.0, "optimal": 7.0, "source": "NRC 2007 Horses"},
    "خيول_رياضة_عادي": {"max": 8.0, "optimal": 5.0, "source": "NRC 2007 Horses"},
    "خيول_نمو": {"max": 8.0, "optimal": 5.0, "source": "NRC 2007 Horses"},
    "خيول_مرضعات": {"max": 8.0, "optimal": 5.5, "source": "NRC 2007 Horses"},
    "خيول_صيانة": {"max": 5.0, "optimal": 3.0, "source": "NRC 2007 Horses"},
    "أسماك_بادئ": {"max": 15.0, "optimal": 10.0, "source": "NRC Fish Nutrition"},
    "أسماك_نمو": {"max": 12.0, "optimal": 8.0, "source": "NRC Fish Nutrition"},
    "أسماك_تسمين": {"max": 12.0, "optimal": 8.0, "source": "NRC Fish Nutrition"},
}

OIL_CATEGORIES = {
    "زيوت غنية بأوميغا 6": ["زيت ذرة", "زيت عباد الشمس", "زيت القرطم", "زيت فول الصويا"],
    "زيوت غنية بأوميغا 3": ["زيت الكتان", "زيت الكانولا", "زيت السمك (Fish Oil)"],
    "زيوت متوازنة": ["زيت النخيل", "زيت جوز الهند", "زيت الزيتون", "زيت السمسم", "زيت الفول السوداني"],
    "دهون حيوانية": ["شحم حيواني (Tallow)"],
    "زيوت خاصة": ["زيت بذرة القطن"],
}


def get_oil_standard(standard_key):
    return MAX_OIL_PERCENTAGE.get(
        standard_key,
        {"max": 5.0, "optimal": 3.0, "source": "معيار عام — NRC"})


def get_oil_ingredients():
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت النباتية والحيوانية", {})


# ═════════════════════════════════════════════════════════════════════════════
# القسم 6: المعايير القياسية
# ═════════════════════════════════════════════════════════════════════════════

STANDARD_VALUES = {
    "أبقار": {
        "تسمين عجول": {"DP": 12.0, "SE": 68.0, "CP": 15.0},
        "حليب/إدرار": {"DP": 14.0, "SE": 70.0, "CP": 17.5},
        "صيانة": {"DP": 9.0, "SE": 60.0, "CP": 11.3},
    },
    "أغنام": {
        "تسمين حملان": {"DP": 13.0, "SE": 66.0, "CP": 16.3},
        "حليب/إدرار": {"DP": 14.5, "SE": 68.0, "CP": 18.1},
        "صيانة": {"DP": 8.5, "SE": 58.0, "CP": 10.6},
    },
    "ماعز": {
        "تسمين جديان": {"DP": 12.5, "SE": 64.0, "CP": 15.6},
        "حليب/إدرار": {"DP": 14.0, "SE": 66.0, "CP": 17.5},
        "صيانة": {"DP": 8.0, "SE": 56.0, "CP": 10.0},
    },
    "خيول": {
        "راحة/صيانة": {"DP": 9.0, "SE": 58.0, "CP": 11.3},
        "عمل متوسط": {"DP": 11.0, "SE": 62.0, "CP": 13.8},
        "سباق": {"DP": 14.0, "SE": 68.0, "CP": 17.5},
    },
    "إبل": {
        "راحة/صيانة": {"DP": 8.0, "SE": 55.0, "CP": 10.0},
        "إنتاج حليب": {"DP": 12.0, "SE": 60.0, "CP": 15.0},
        "تسمين": {"DP": 11.0, "SE": 62.0, "CP": 13.8},
    },
    "دواجن لاحم": {
        "بادي (0-14 يوم)": {"DP": 22.0, "SE": 76.0, "CP": 27.5},
        "نامي (15-28 يوم)": {"DP": 20.0, "SE": 74.0, "CP": 25.0},
        "ناهي (29-42 يوم)": {"DP": 18.0, "SE": 72.0, "CP": 22.5},
    },
    "دواجن بياض": {
        "بادي": {"DP": 20.0, "SE": 72.0, "CP": 25.0},
        "بياض إنتاجي": {"DP": 16.0, "SE": 66.0, "CP": 20.0},
    },
    "سمان": {
        "بادي": {"DP": 24.0, "SE": 74.0, "CP": 30.0},
        "بياض": {"DP": 18.0, "SE": 68.0, "CP": 22.5},
    },
    "أسماك": {
        "زريعة/بادئ": {"DP": 32.0, "SE": 70.0, "CP": 40.0},
        "نمو": {"DP": 28.0, "SE": 68.0, "CP": 35.0},
        "تسمين نهائي": {"DP": 26.0, "SE": 66.0, "CP": 32.5},
    }
}


# ═════════════════════════════════════════════════════════════════════════════
# القسم 7: dataclass + دوال الاحتياجات
# ═════════════════════════════════════════════════════════════════════════════

@dataclass
class AnimalRequirement:
    DP: float
    CP: float
    SE: float
    NDF: float
    ADF: float
    EE: float
    ASH: float
    Ca: float
    P: float
    name_ar: str = ""
    note: str = ""


def get_cattle_requirements(production_type, milk_yield=20.0, weight_kg=500.0):
    if production_type == "حليب_عالي":
        dp = 12.5 + (milk_yield * 0.30); cp = dp / 0.70
        return AnimalRequirement(DP=round(dp, 2), CP=round(cp, 2),
            SE=round(60 + milk_yield * 0.35, 1), NDF=30.0, ADF=19.0,
            EE=5.5, ASH=8.0, Ca=round(0.55 + milk_yield * 0.003, 3),
            P=round(0.33 + milk_yield * 0.0015, 3),
            name_ar="أبقار حلابة عالية",
            note=f"إنتاج {milk_yield} كجم/يوم | الوزن {weight_kg} كجم")
    elif production_type == "حليب_متوسط":
        dp = 11.0 + (milk_yield * 0.25); cp = dp / 0.72
        return AnimalRequirement(DP=round(dp, 2), CP=round(cp, 2),
            SE=round(55 + milk_yield * 0.30, 1), NDF=33.0, ADF=21.0,
            EE=4.5, ASH=8.0, Ca=round(0.50 + milk_yield * 0.0025, 3),
            P=round(0.30 + milk_yield * 0.0012, 3),
            name_ar="أبقار حلابة متوسطة",
            note=f"إنتاج {milk_yield} كجم/يوم")
    elif production_type == "حليب_منخفض":
        dp = 9.5 + (milk_yield * 0.20); cp = dp / 0.75
        return AnimalRequirement(DP=round(dp, 2), CP=round(cp, 2),
            SE=round(50 + milk_yield * 0.25, 1), NDF=38.0, ADF=24.0,
            EE=4.0, ASH=8.5, Ca=round(0.45 + milk_yield * 0.002, 3),
            P=round(0.28 + milk_yield * 0.001, 3),
            name_ar="أبقار حلابة منخفضة",
            note=f"إنتاج {milk_yield} كجم/يوم")
    elif production_type == "تسمين_مكثف":
        return AnimalRequirement(DP=11.5, CP=14.5, SE=72.0, NDF=32.0,
            ADF=20.0, EE=4.5, ASH=7.5, Ca=0.65, P=0.38,
            name_ar="تسمين عجول مكثف", note="ADG >1.3 كجم/يوم")
    elif production_type == "تسمين_عادي":
        return AnimalRequirement(DP=9.5, CP=12.0, SE=65.0, NDF=38.0,
            ADF=24.0, EE=4.0, ASH=7.5, Ca=0.55, P=0.32,
            name_ar="تسمين عجول عادي", note="ADG ~0.8 كجم/يوم")
    elif production_type == "حمل_أخير":
        return AnimalRequirement(DP=11.5, CP=14.5, SE=67.0, NDF=35.0,
            ADF=22.0, EE=4.2, ASH=8.0, Ca=0.70, P=0.42,
            name_ar="حمل آخر", note="دفع غذائي جنيني")
    else:
        return AnimalRequirement(DP=7.5, CP=10.0, SE=53.0, NDF=45.0,
            ADF=28.0, EE=3.0, ASH=8.5, Ca=0.42, P=0.26,
            name_ar="أبقار صيانة", note="بدون إنتاج")


def get_sheep_requirements(production_type, is_male=True,
                             weight_kg=50.0, litter_size=1):
    if is_male:
        if production_type == "تسمين_مكثف":
            return AnimalRequirement(DP=11.5, CP=14.5, SE=64.0, NDF=28.0,
                ADF=17.0, EE=4.0, ASH=8.0, Ca=0.65, P=0.36,
                name_ar="تسمين حملان مكثف", note="ADG >250 جم/يوم")
        elif production_type == "تسمين_عادي":
            return AnimalRequirement(DP=9.5, CP=12.0, SE=59.0, NDF=33.0,
                ADF=21.0, EE=3.6, ASH=8.0, Ca=0.55, P=0.32,
                name_ar="تسمين حملان عادي", note="ADG ~180 جم/يوم")
        else:
            return AnimalRequirement(DP=8.5, CP=11.0, SE=55.0, NDF=38.0,
                ADF=24.0, EE=3.2, ASH=8.5, Ca=0.50, P=0.30,
                name_ar="حملان تيد", note="تسمين نهائي")
    else:
        if production_type == "مرضعات":
            dp = 10.5 + (litter_size - 1) * 1.5; cp = dp / 0.72
            return AnimalRequirement(DP=round(dp, 2), CP=round(cp, 2),
                SE=round(60 + (litter_size - 1) * 5, 1), NDF=30.0, ADF=19.0,
                EE=4.5, ASH=8.5,
                Ca=round(0.65 + (litter_size - 1) * 0.10, 3),
                P=round(0.38 + (litter_size - 1) * 0.05, 3),
                name_ar=f"نعاج مرضعات ({litter_size} مواليد)",
                note="إنتاج حليب مرتفع")
        elif production_type == "حامل_أخير":
            return AnimalRequirement(DP=10.5, CP=13.5, SE=62.0, NDF=32.0,
                ADF=20.0, EE=3.8, ASH=8.0, Ca=0.60, P=0.35,
                name_ar="نعاج حامل (شهر 4-5)", note="تغذية جنين")
        elif production_type == "حامل_متوسط":
            return AnimalRequirement(DP=8.5, CP=11.0, SE=55.0, NDF=38.0,
                ADF=24.0, EE=3.4, ASH=8.0, Ca=0.50, P=0.30,
                name_ar="نعاج حامل (شهر 1-3)", note="نمو جنيني مبكر")
        else:
            return AnimalRequirement(DP=7.2, CP=9.5, SE=48.0, NDF=45.0,
                ADF=28.0, EE=3.0, ASH=8.5, Ca=0.42, P=0.26,
                name_ar="نعاج صيانة", note="بدون إنتاج")


def get_goat_requirements(production_type, is_male=True, milk_yield=2.0):
    if is_male:
        if production_type == "تسمين_جديان":
            return AnimalRequirement(DP=11.0, CP=14.0, SE=62.0, NDF=30.0,
                ADF=19.0, EE=3.8, ASH=8.0, Ca=0.62, P=0.34,
                name_ar="تسمين جديان", note="نمو سريع")
        else:
            return AnimalRequirement(DP=9.0, CP=11.5, SE=57.0, NDF=36.0,
                ADF=22.0, EE=3.5, ASH=8.0, Ca=0.55, P=0.30,
                name_ar="تيوس تسمين", note="تسمين نهائي")
    else:
        if production_type == "حلابة_عالي":
            dp = 11.5 + (milk_yield * 0.45); cp = dp / 0.70
            return AnimalRequirement(DP=round(dp, 2), CP=round(cp, 2),
                SE=round(58 + milk_yield * 0.45, 1), NDF=29.0, ADF=18.0,
                EE=4.5, ASH=8.5, Ca=round(0.60 + milk_yield * 0.008, 3),
                P=round(0.35 + milk_yield * 0.004, 3),
                name_ar=f"عنزات حلابة عالي ({milk_yield} كجم)",
                note="إدرار عالي")
        elif production_type == "حلابة_متوسط":
            dp = 10.0 + (milk_yield * 0.35); cp = dp / 0.72
            return AnimalRequirement(DP=round(dp, 2), CP=round(cp, 2),
                SE=round(55 + milk_yield * 0.40, 1), NDF=32.0, ADF=20.0,
                EE=4.0, ASH=8.5, Ca=round(0.55 + milk_yield * 0.006, 3),
                P=round(0.32 + milk_yield * 0.003, 3),
                name_ar=f"عنزات حلابة متوسط",
                note="إدرار متوسط")
        elif production_type == "حامل_أخير":
            return AnimalRequirement(DP=10.0, CP=13.0, SE=60.0, NDF=33.0,
                ADF=21.0, EE=3.8, ASH=8.0, Ca=0.60, P=0.35,
                name_ar="عنزات حامل", note="دفع غذائي")
        else:
            return AnimalRequirement(DP=6.8, CP=9.0, SE=46.0, NDF=46.0,
                ADF=28.0, EE=3.0, ASH=8.5, Ca=0.42, P=0.26,
                name_ar="عنزات صيانة", note="بدون إنتاج")


def get_camel_requirements(production_type, weight_kg=400.0, milk_yield=5.0):
    dm_kg = weight_kg * 0.025
    if production_type == "نمو":
        return AnimalRequirement(DP=10.5, CP=13.5, SE=60.0, NDF=38.0,
            ADF=24.0, EE=4.0, ASH=8.0, Ca=0.65, P=0.38,
            name_ar="إبل نمو (حوار)",
            note=f"وزن {weight_kg} كجم | DM {dm_kg:.1f} كجم/يوم")
    elif production_type == "تسمين":
        return AnimalRequirement(DP=9.5, CP=12.0, SE=65.0, NDF=35.0,
            ADF=22.0, EE=4.5, ASH=7.5, Ca=0.60, P=0.35,
            name_ar="إبل تسمين", note=f"وزن {weight_kg} كجم")
    elif production_type == "حليب":
        dp = 12.0 + (milk_yield * 0.25); cp = dp / 0.70
        return AnimalRequirement(DP=round(dp, 2), CP=round(cp, 2),
            SE=round(62 + milk_yield * 0.40, 1), NDF=32.0, ADF=20.0,
            EE=5.0, ASH=8.5, Ca=round(0.70 + milk_yield * 0.006, 3),
            P=round(0.40 + milk_yield * 0.003, 3),
            name_ar=f"إبل حلابة ({milk_yield} لتر)", note="دهن عالي")
    elif production_type == "سباق":
        return AnimalRequirement(DP=14.0, CP=17.0, SE=72.0, NDF=28.0,
            ADF=17.0, EE=6.0, ASH=9.0, Ca=0.85, P=0.50,
            name_ar="إبل سباق (هجن)", note="طاقة عالية")
    else:
        return AnimalRequirement(DP=7.0, CP=9.0, SE=48.0, NDF=48.0,
            ADF=30.0, EE=3.5, ASH=9.0, Ca=0.42, P=0.26,
            name_ar="إبل صيانة", note=f"وزن {weight_kg} كجم")


def get_horse_requirements(production_type, weight_kg=450.0):
    if production_type == "رياضة_مكثف":
        return AnimalRequirement(DP=10.5, CP=13.5, SE=70.0, NDF=30.0,
            ADF=18.0, EE=7.0, ASH=7.5, Ca=0.70, P=0.40,
            name_ar="خيول رياضة مكثف", note="جهد عالي")
    elif production_type == "رياضة_عادي":
        return AnimalRequirement(DP=9.0, CP=11.5, SE=63.0, NDF=36.0,
            ADF=22.0, EE=5.0, ASH=7.5, Ca=0.55, P=0.32,
            name_ar="خيول رياضة عادي", note="نشاط متوسط")
    elif production_type == "نمو_أمهار":
        return AnimalRequirement(DP=12.0, CP=15.0, SE=65.0, NDF=30.0,
            ADF=18.0, EE=5.0, ASH=8.0, Ca=0.75, P=0.42,
            name_ar="أمهار نمو", note="نمو هيكلي")
    elif production_type == "مرضعات":
        return AnimalRequirement(DP=12.5, CP=16.0, SE=68.0, NDF=32.0,
            ADF=20.0, EE=5.5, ASH=8.0, Ca=0.80, P=0.45,
            name_ar="فرسات مرضعات", note="إنتاج حليب")
    else:
        return AnimalRequirement(DP=7.2, CP=9.5, SE=53.0, NDF=46.0,
            ADF=29.0, EE=3.5, ASH=8.0, Ca=0.45, P=0.28,
            name_ar="خيول صيانة", note="بدون جهد")


def get_poultry_requirements(strain, age_weeks=1):
    if strain == "لاحم":
        if age_weeks <= 1:
            return AnimalRequirement(DP=20.0, CP=23.0, SE=76.0, NDF=8.0,
                ADF=4.0, EE=5.0, ASH=6.5, Ca=1.00, P=0.50,
                name_ar="بادي لاحم", note="Energy 3000 kcal/kg")
        elif age_weeks <= 3:
            return AnimalRequirement(DP=18.5, CP=21.0, SE=74.0, NDF=9.0,
                ADF=5.0, EE=5.0, ASH=6.0, Ca=0.90, P=0.45,
                name_ar="نامي لاحم", note="Energy 3100 kcal/kg")
        elif age_weeks <= 5:
            return AnimalRequirement(DP=17.0, CP=19.5, SE=75.0, NDF=10.0,
                ADF=5.5, EE=4.5, ASH=6.0, Ca=0.87, P=0.43,
                name_ar="ناهي لاحم", note="Energy 3150 kcal/kg")
        else:
            return AnimalRequirement(DP=16.5, CP=19.0, SE=75.0, NDF=10.0,
                ADF=5.5, EE=4.5, ASH=6.0, Ca=0.85, P=0.42,
                name_ar="ناهي لاحم متقدم", note="Energy 3200 kcal/kg")
    else:
        if age_weeks <= 6:
            return AnimalRequirement(DP=17.0, CP=20.0, SE=72.0, NDF=10.0,
                ADF=5.5, EE=4.0, ASH=7.0, Ca=1.00, P=0.50,
                name_ar="بادي بياض", note="تحضير للبيض")
        elif age_weeks <= 18:
            return AnimalRequirement(DP=14.5, CP=17.0, SE=70.0, NDF=12.0,
                ADF=6.5, EE=4.0, ASH=9.0, Ca=1.50, P=0.45,
                name_ar="نامي بياض", note="نمو هيكلي")
        else:
            return AnimalRequirement(DP=15.5, CP=18.0, SE=72.0, NDF=11.0,
                ADF=6.0, EE=4.2, ASH=11.5, Ca=3.80, P=0.45,
                name_ar="بياض إنتاجي", note="إنتاج بيض")


def get_quail_requirements(strain, age_weeks=1):
    if strain == "بياض":
        return AnimalRequirement(DP=15.0, CP=18.0, SE=68.0, NDF=11.0,
            ADF=5.5, EE=4.5, ASH=9.0, Ca=2.50, P=0.45,
            name_ar="سمان بياض", note="إنتاج بيض")
    else:
        if age_weeks <= 2:
            return AnimalRequirement(DP=20.5, CP=24.0, SE=74.0, NDF=8.0,
                ADF=4.0, EE=5.5, ASH=6.5, Ca=1.00, P=0.55,
                name_ar="سمان بادي", note="نمو سريع")
        elif age_weeks <= 4:
            return AnimalRequirement(DP=18.5, CP=22.0, SE=72.0, NDF=9.0,
                ADF=4.5, EE=5.0, ASH=6.0, Ca=0.90, P=0.50,
                name_ar="سمان نامي", note="نمو متوسط")
        else:
            return AnimalRequirement(DP=17.0, CP=20.0, SE=70.0, NDF=10.0,
                ADF=5.0, EE=4.5, ASH=6.0, Ca=0.85, P=0.45,
                name_ar="سمان ناهي", note="تسمين نهائي")


def get_fish_requirements(species, stage):
    if "زريعة" in stage or "بادئ" in stage:
        return AnimalRequirement(DP=32.0, CP=40.0, SE=72.0, NDF=8.0,
            ADF=4.0, EE=10.0, ASH=11.0, Ca=1.50, P=0.90,
            name_ar=f"{species} — بادئ", note="بروتين عالٍ")
    elif "نمو" in stage:
        return AnimalRequirement(DP=25.0, CP=32.0, SE=70.0, NDF=12.0,
            ADF=6.0, EE=8.0, ASH=9.0, Ca=1.00, P=0.70,
            name_ar=f"{species} — نمو", note="بروتين متوسط")
    else:
        return AnimalRequirement(DP=22.0, CP=28.0, SE=68.0, NDF=13.0,
            ADF=7.0, EE=8.0, ASH=9.5, Ca=0.90, P=0.65,
            name_ar=f"{species} — تسمين", note="طاقة عالية")


def requirement_to_standard(req):
    return {
        "CP": req.CP, "DP": req.DP, "SE": req.SE,
        "NDF": req.NDF, "ADF": req.ADF, "EE": req.EE,
        "ASH": req.ASH, "Ca": req.Ca, "P": req.P,
    }


# ═════════════════════════════════════════════════════════════════════════════
# القسم 8: الحسابات الغذائية
# ═════════════════════════════════════════════════════════════════════════════

def compute_formula_nutrients(formula):
    totals = {"CP": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
              "EE": 0.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0}
    for ing, pct in formula.items():
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat:
                d = cat[ing]
                f = pct / 100.0
                totals["CP"] += f * d.get("CP", 0.0)
                totals["DP"] += f * d.get("CP", 0.0) * d.get("DC", 0.0)
                totals["SE"] += f * d.get("SE", 0.0)
                totals["NDF"] += f * d.get("NDF", 0.0)
                totals["ADF"] += f * d.get("ADF", 0.0)
                totals["EE"] += f * d.get("EE", 0.0)
                totals["ASH"] += f * d.get("ASH", 0.0)
                totals["Ca"] += f * d.get("Ca", 0.0)
                totals["P"] += f * d.get("P", 0.0)
                break
    return totals


def compute_total_oil_percentage(formula):
    oils = set(get_oil_ingredients().keys())
    return sum(pct for ing, pct in formula.items() if ing in oils)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 9: التقييم والمحرك الذكي
# ═════════════════════════════════════════════════════════════════════════════

def evaluate_difference(pct_diff):
    a = abs(pct_diff)
    if a <= 0.5: return {"label": "🎯 مطابق", "color": "#0d5302", "bg": "#c8e6c9", "score": 100}
    elif a <= 2.0: return {"label": "🌟 ممتاز", "color": "#1b5e20", "bg": "#dcedc8", "score": 95}
    elif a <= 5.0: return {"label": "✅ جيد جداً", "color": "#2e7d32", "bg": "#e8f5e9", "score": 85}
    elif a <= 10.0: return {"label": "🟢 جيد", "color": "#558b2f", "bg": "#f1f8e9", "score": 75}
    elif a <= 15.0: return {"label": "⭐ مقبول", "color": "#f9a825", "bg": "#fff8e1", "score": 65}
    elif a <= 25.0: return {"label": "⚠️ تحفظ", "color": "#ef6c00", "bg": "#fff3e0", "score": 50}
    elif a <= 40.0: return {"label": "🟠 ضعيف", "color": "#e65100", "bg": "#ffe0b2", "score": 35}
    else: return {"label": "❌ غير مطابق", "color": "#c62828", "bg": "#ffebee", "score": 20}


def get_overall_rating(compare_rows):
    if not compare_rows:
        return {"label": "غير محدد", "color": "#666", "score": 0}
    scores = [r.get("score", 50) for r in compare_rows]
    avg = sum(scores) / len(scores)
    if avg >= 95: return {"label": "🏆 ممتازة", "color": "#1b5e20", "score": avg}
    elif avg >= 85: return {"label": "🌟 جيدة جداً", "color": "#2e7d32", "score": avg}
    elif avg >= 70: return {"label": "✅ جيدة", "color": "#558b2f", "score": avg}
    elif avg >= 55: return {"label": "⭐ مقبولة", "color": "#f9a825", "score": avg}
    else: return {"label": "⚠️ تحتاج تحسين", "color": "#e65100", "score": avg}


def auto_formulate_smart(available_ingredients, prices, custom_standard,
                          standard_key, tolerance=0.3, max_iterations=50):
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "scipy غير مثبتة"}
    ing_data = {}
    for ing in available_ingredients:
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat:
                ing_data[ing] = cat[ing]
                break
    valid = [i for i in available_ingredients if i in ing_data]
    if len(valid) < 3:
        return {"success": False, "message": "اختر 3 مكونات على الأقل"}

    n = len(valid)
    c = [prices.get(i, 300.0) for i in valid]
    rows = {}
    for nutrient in ["CP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
        rows[nutrient] = [ing_data[i].get(nutrient, 0) for i in valid]
    rows["DP"] = [ing_data[i].get("CP", 0) * ing_data[i].get("DC", 0) for i in valid]

    targets = {k: custom_standard.get(k, 0) for k in ["DP", "SE", "NDF", "ADF", "Ca", "P"]}
    oil_std = get_oil_standard(standard_key)
    oil_max = oil_std["max"]

    bounds = []
    for i in valid:
        if i in get_oil_ingredients(): bounds.append((0.0, oil_max * 0.6))
        elif "يوريا" in i: bounds.append((0.0, 1.0))
        elif "مولاس" in i: bounds.append((0.0, 10.0))
        elif "ملح الطعام" in i: bounds.append((0.3, 0.7))
        elif "بيكربونات" in i: bounds.append((0.0, 1.5))
        elif "مضاد سموم" in i: bounds.append((0.05, 0.25))
        elif "بريمكس" in i: bounds.append((0.15, 0.5))
        elif "إنزيم" in i: bounds.append((0.02, 0.10))
        elif "الحجر الجيري" in i: bounds.append((0.0, 8.5))
        elif "فوسفات" in i: bounds.append((0.0, 2.5))
        elif "سرسة" in i: bounds.append((0.0, 8.0))
        elif "تبن" in i or "قش" in i: bounds.append((0.0, 25.0))
        else: bounds.append((0.0, 100.0))

    oil_indicator = [1.0 if i in get_oil_ingredients() else 0.0 for i in valid]
    has_oils = sum(oil_indicator) > 0

    A_eq = [[1.0] * n, rows["DP"]]
    b_eq = [100.0, targets["DP"] * 100.0]
    A_ub = [[-1.0 * x for x in rows["SE"]],
            [1.0 * x for x in rows["NDF"]],
            [1.0 * x for x in rows["ADF"]]]
    b_ub = [-1.0 * targets["SE"] * 100.0,
            targets["NDF"] * 1.15 * 100.0,
            targets["ADF"] * 1.15 * 100.0]
    if has_oils:
        A_ub.append(oil_indicator)
        b_ub.append(oil_max * 100.0)

    try:
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                      bounds=bounds, method='highs')
    except Exception:
        res = type('obj', (), {'success': False})()

    if not res.success:
        for relax in [1.05, 1.10, 1.20, 1.30]:
            b_ub_r = [-1.0 * targets["SE"] * 100.0 * (2 - relax),
                      targets["NDF"] * relax * 100.0,
                      targets["ADF"] * relax * 100.0]
            if has_oils:
                b_ub_r.append(oil_max * 100.0)
            try:
                res = linprog(c, A_ub=A_ub, b_ub=b_ub_r, A_eq=A_eq,
                              b_eq=b_eq, bounds=bounds, method='highs')
                if res.success: break
            except Exception:
                continue

    if not res.success:
        return {"success": False, "message": "تعذر إيجاد حل"}

    best = None
    best_score = float('inf')
    cur_dp, cur_se = targets["DP"], targets["SE"]
    cur_ndf, cur_adf = targets["NDF"], targets["ADF"]

    for iteration in range(max_iterations):
        A_eq = [[1.0] * n, rows["DP"], rows["Ca"], rows["P"]]
        b_eq = [100.0, cur_dp * 100.0, targets["Ca"] * 100.0, targets["P"] * 100.0]
        A_ub = [[-1.0 * x for x in rows["SE"]],
                [1.0 * x for x in rows["NDF"]],
                [1.0 * x for x in rows["ADF"]]]
        b_ub = [-1.0 * cur_se * 100.0,
                cur_ndf * 1.10 * 100.0,
                cur_adf * 1.10 * 100.0]
        if has_oils:
            A_ub.append(oil_indicator)
            b_ub.append(oil_max * 100.0)

        try:
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method='highs',
                          options={'presolve': True, 'time_limit': 15})
        except Exception:
            res = type('obj', (), {'success': False})()

        if not res.success:
            A_eq = [[1.0] * n, rows["DP"], rows["Ca"]]
            b_eq = [100.0, cur_dp * 100.0, targets["Ca"] * 100.0]
            try:
                res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                              bounds=bounds, method='highs')
            except Exception:
                res = type('obj', (), {'success': False})()

        if not res.success:
            cur_ndf *= 1.05
            cur_adf *= 1.05
            continue

        formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
        actual = compute_formula_nutrients(formula)
        total_oil_actual = compute_total_oil_percentage(formula)

        errors = {}
        for k in ["DP", "SE", "NDF", "ADF", "Ca", "P"]:
            tv = targets.get(k, 0)
            errors[k] = abs(actual.get(k, 0) - tv) / tv if tv > 0 else 0

        weights = {"DP": 5.0, "SE": 3.0, "NDF": 1.5, "ADF": 1.0, "Ca": 1.0, "P": 1.0}
        score = sum(errors.get(k, 0) * weights[k] for k in errors)

        if score < best_score:
            best_score = score
            best = {
                "success": True, "formula": formula, "cost": res.fun / 100.0,
                "actual_nutrients": actual,
                "dp_error": abs(actual["DP"] - targets["DP"]),
                "se_error": abs(actual["SE"] - targets["SE"]),
                "ndf_error": abs(actual["NDF"] - targets["NDF"]),
                "adf_error": abs(actual["ADF"] - targets["ADF"]),
                "ca_error": abs(actual.get("Ca", 0) - targets["Ca"]),
                "p_error": abs(actual.get("P", 0) - targets["P"]),
                "total_oil": total_oil_actual, "oil_std": oil_std,
                "iterations": iteration + 1, "targets": targets,
            }

        if (errors.get("DP", 1) * 100 <= tolerance and
            errors.get("SE", 1) * 100 <= tolerance * 2 and
            errors.get("NDF", 1) * 100 <= tolerance * 5 and
            errors.get("Ca", 1) * 100 <= tolerance * 15):
            best["perfect_match"] = True
            break

        cur_dp += (targets["DP"] - actual["DP"]) * 0.25
        cur_se += (targets["SE"] - actual["SE"]) * 0.20
        cur_ndf += (targets["NDF"] - actual["NDF"]) * 0.15
        cur_adf += (targets["ADF"] - actual["ADF"]) * 0.15
        cur_dp = max(5.0, min(40.0, cur_dp))
        cur_se = max(10.0, min(90.0, cur_se))
        cur_ndf = max(5.0, min(70.0, cur_ndf))
        cur_adf = max(3.0, min(50.0, cur_adf))

    if best:
        return best
    return {"success": False, "message": "تعذر حل دقيق"}


def auto_add_salts_and_minerals(animal_type, requirement=None):
    salt = {}
    if animal_type in ["أغنام", "ماعز", "أبقار", "إبل"]:
        salt["بيكربونات الصوديوم"] = 0.75
    salt["مضاد سموم فطرية"] = 0.20
    salt["ملح الطعام"] = 0.50
    if animal_type in ["دواجن", "سمان"]:
        if requirement and requirement.Ca > 2.0:
            salt["الحجر الجيري (بودرة بلاط)"] = 8.0
        else:
            salt["الحجر الجيري (بودرة بلاط)"] = 1.5
        salt["فوسفات ثنائي الكالسيوم (DCP)"] = 1.5
        salt["بريمكس تسمين دواجن"] = 0.30
    elif animal_type == "أسماك":
        salt["الحجر الجيري (بودرة بلاط)"] = 1.0
        salt["فوسفات ثنائي الكالسيوم (DCP)"] = 1.5
        salt["بريمكس أسماك"] = 0.30
    elif animal_type == "خيول":
        salt["الحجر الجيري (بودرة بلاط)"] = 1.5
        salt["فوسفات ثنائي الكالسيوم (DCP)"] = 1.5
        salt["بريمكس خيول"] = 0.30
    elif animal_type == "إبل":
        salt["الحجر الجيري (بودرة بلاط)"] = 2.0
        salt["فوسفات ثنائي الكالسيوم (DCP)"] = 1.5
        salt["بريمكس إبل"] = 0.30
    else:
        salt["الحجر الجيري (بودرة بلاط)"] = 2.0
        salt["فوسفات ثنائي الكالسيوم (DCP)"] = 1.5
        salt["بريمكس مجترات"] = 0.30
    return salt


# ═════════════════════════════════════════════════════════════════════════════
# القسم 10: تقويم معايير الحظائر العلمي
# ═════════════════════════════════════════════════════════════════════════════

BARN_STANDARDS = {
    "أبقار_حلابة": {
        "space_per_head_m2": 12.0, "cubicle_width_cm": 120,
        "cubicle_length_cm": 250, "feeding_space_cm": 75,
        "water_space_cm": 50, "height_m": 4.0, "ridge_height_m": 5.5,
        "ventilation_m3_h": 200, "air_space_m3": 20,
        "alley_width_m": 3.5, "feeding_alley_m": 4.5,
        "temp_range": "5-25°م", "humidity_max": "75%",
        "source": "NRC 2001 / EFSA / Lactanet"},
    "أبقار_تسمين": {
        "space_per_head_m2": 13.0, "feeding_space_cm": 60,
        "water_space_cm": 45, "height_m": 3.5, "ridge_height_m": 5.0,
        "ventilation_m3_h": 180, "air_space_m3": 18,
        "alley_width_m": 3.0, "feeding_alley_m": 4.0,
        "temp_range": "5-25°م", "humidity_max": "75%",
        "source": "EFSA / Saskatchewan Ministry"},
    "أغنام": {
        "space_per_head_m2": 2.0, "feeding_space_cm": 20,
        "water_space_cm": 30, "height_m": 3.0, "ridge_height_m": 4.0,
        "ventilation_m3_h": 70, "air_space_m3": 7,
        "alley_width_m": 1.3, "feeding_alley_m": 2.5,
        "temp_range": "5-25°م", "humidity_max": "70%",
        "source": "NRC 2007 / FAO"},
    "ماعز": {
        "space_per_head_m2": 2.0, "feeding_space_cm": 20,
        "water_space_cm": 30, "height_m": 3.0, "ridge_height_m": 4.0,
        "ventilation_m3_h": 70, "air_space_m3": 7,
        "alley_width_m": 1.3, "feeding_alley_m": 2.5,
        "temp_range": "5-25°م", "humidity_max": "70%",
        "source": "NRC 2007"},
    "خيول": {
        "space_per_head_m2": 12.0, "feeding_space_cm": 90,
        "water_space_cm": 60, "height_m": 3.0, "ridge_height_m": 4.0,
        "ventilation_m3_h": 250, "air_space_m3": 30,
        "alley_width_m": 2.5, "feeding_alley_m": 3.5,
        "stall_width_m": 3.6, "stall_length_m": 3.6,
        "temp_range": "5-25°م", "humidity_max": "70%",
        "source": "NRC 2007 Horses"},
    "إبل": {
        "space_per_head_m2": 15.0, "feeding_space_cm": 90,
        "water_space_cm": 60, "height_m": 3.5, "ridge_height_m": 4.5,
        "ventilation_m3_h": 200, "air_space_m3": 20,
        "alley_width_m": 3.0, "feeding_alley_m": 4.0,
        "temp_range": "5-40°م", "humidity_max": "60%",
        "source": "FAO 2010"},
    "دواجن_لاحم": {
        "space_per_head_m2": 0.10, "feeding_space_cm": 10,
        "water_space_cm": 4, "height_m": 2.5, "ridge_height_m": 3.5,
        "ventilation_m3_h": 8, "air_space_m3": 1.5,
        "house_width_m": 8.0, "alley_width_m": 1.0,
        "temp_range": "20-34°م", "humidity_max": "70%",
        "source": "Ross 308 / FAO"},
    "دواجن_بياض": {
        "space_per_head_m2": 0.15, "feeding_space_cm": 12,
        "water_space_cm": 4, "height_m": 2.8, "ridge_height_m": 3.8,
        "ventilation_m3_h": 8, "air_space_m3": 2.0,
        "house_width_m": 8.0, "alley_width_m": 1.0,
        "temp_range": "18-25°م", "humidity_max": "70%",
        "source": "NRC 1994 / FAO"},
    "سمان": {
        "space_per_head_m2": 0.02, "feeding_space_cm": 5,
        "water_space_cm": 2, "height_m": 2.0, "ridge_height_m": 3.0,
        "ventilation_m3_h": 4, "air_space_m3": 0.5,
        "house_width_m": 6.0, "alley_width_m": 0.8,
        "temp_range": "22-37°م", "humidity_max": "65%",
        "source": "NRC Quail"},
    "أسماك": {
        "space_per_head_m2": 0.05, "tank_depth_m": 1.5,
        "water_flow_m3_h": 20, "oxygen_mg_l": 5,
        "temp_range": "25-30°م", "ph_range": "6.5-8.5",
        "source": "NRC Fish / FAO Aquaculture"},
        }
# ═════════════════════════════════════════════════════════════════════════════
# القسم 11: بدائل الحليب
# ═════════════════════════════════════════════════════════════════════════════

MILK_REPLACER_STANDARDS = {
    "عجول (Calves)": {"CP": 24.0, "Fat": 24.0, "Lactose": 45.0,
                      "Ca": 0.75, "P": 0.70, "notes": "عمر 1-6 أسابيع"},
    "حملان (Lambs)": {"CP": 24.0, "Fat": 24.0, "Lactose": 40.0,
                      "Ca": 0.80, "P": 0.70, "notes": "≥ 24% دهن"},
    "جديان (Goat Kids)": {"CP": 24.0, "Fat": 24.0, "Lactose": 42.0,
                          "Ca": 0.80, "P": 0.70, "notes": "بديل الجديان"},
    "إبل (Camel Calves)": {"CP": 26.0, "Fat": 28.0, "Lactose": 38.0,
                           "Ca": 0.85, "P": 0.75, "notes": "بروتين ودهن أعلى"},
    "أمهار (Foals)": {"CP": 22.0, "Fat": 20.0, "Lactose": 45.0,
                      "Ca": 0.90, "P": 0.80, "notes": "توازن للخيول"},
}

MILK_REPLACER_INGREDIENTS = {
    "حليب مجفف منزوع الدسم": {"CP": 34.0, "Fat": 1.0, "Lactose": 52.0, "price": 3200},
    "حليب مجفف كامل الدسم": {"CP": 26.0, "Fat": 28.0, "Lactose": 38.0, "price": 3800},
    "شرش حليب مجفف": {"CP": 12.0, "Fat": 1.5, "Lactose": 75.0, "price": 1800},
    "بروتين شرش WPC 80%": {"CP": 80.0, "Fat": 5.0, "Lactose": 8.0, "price": 8500},
    "كازين": {"CP": 85.0, "Fat": 2.0, "Lactose": 2.0, "price": 9000},
    "مركز بروتين صويا": {"CP": 66.0, "Fat": 1.0, "Lactose": 0.0, "price": 2800},
    "زيت جوز الهند": {"CP": 0.0, "Fat": 100.0, "Lactose": 0.0, "price": 2200},
    "زيت النخيل": {"CP": 0.0, "Fat": 100.0, "Lactose": 0.0, "price": 1200},
    "مالتودكسترين": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "price": 900},
    "لاكتوز نقي": {"CP": 0.0, "Fat": 0.0, "Lactose": 100.0, "price": 1400},
    "بريمكس فيتامينات": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "price": 6500},
    "كالسيوم كربونات": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "price": 200},
    "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "price": 1100},
    "ملح طعام": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "price": 150},
}


def formulate_milk_replacer(animal_type, target_volume_kg=100.0,
                             selected_ingredients=None):
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "scipy غير مثبتة"}
    standard = MILK_REPLACER_STANDARDS.get(animal_type)
    if not standard:
        return {"success": False, "message": "غير مدعوم"}
    valid = [i for i in (selected_ingredients or list(MILK_REPLACER_INGREDIENTS.keys()))
             if i in MILK_REPLACER_INGREDIENTS]
    if len(valid) < 3:
        return {"success": False, "message": "اختر 3 مكونات على الأقل"}
    n = len(valid)
    c = [MILK_REPLACER_INGREDIENTS[i]["price"] for i in valid]
    bounds = [(0.0, 100.0) for _ in range(n)]
    A_eq = [[1.0] * n,
            [MILK_REPLACER_INGREDIENTS[i]["CP"] for i in valid],
            [MILK_REPLACER_INGREDIENTS[i]["Fat"] for i in valid]]
    b_eq = [100.0, standard["CP"] * 100, standard["Fat"] * 100]
    try:
        res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    except Exception:
        return {"success": False, "message": "خطأ في الحساب"}
    if not res.success:
        return {"success": False, "message": "تعذر التركيب"}
    formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
    actual = {"CP": 0, "Fat": 0, "Lactose": 0}
    for ing, pct in formula.items():
        d = MILK_REPLACER_INGREDIENTS[ing]
        actual["CP"] += pct / 100.0 * d["CP"]
        actual["Fat"] += pct / 100.0 * d["Fat"]
        actual["Lactose"] += pct / 100.0 * d["Lactose"]
    return {"success": True, "formula": formula,
            "cost_per_100kg": res.fun / 100.0,
            "cost_per_kg": res.fun / 10000.0,
            "standard": standard, "actual": actual, "animal": animal_type}


# ═════════════════════════════════════════════════════════════════════════════
# القسم 12: التحليل المعملي الشامل (Weende + Van Soest + Energy + Amino)
# ═════════════════════════════════════════════════════════════════════════════

# المعايير المرجعية لتحليل Weende حسب نوع الحيوان
FEED_ANALYSIS_REFERENCE = {
    "أبقار": {
        "حليب": {"CP": 18.0, "DP": 13.0, "SE": 72, "NDF": 30, "ADF": 19,
                 "EE": 5.0, "ASH": 8.0, "Ca": 0.70, "P": 0.45, "TDN": 72},
        "تسمين": {"CP": 14.5, "DP": 11.5, "SE": 72, "NDF": 32, "ADF": 20,
                  "EE": 4.5, "ASH": 7.5, "Ca": 0.65, "P": 0.38, "TDN": 74},
        "صيانة": {"CP": 10.0, "DP": 7.5, "SE": 53, "NDF": 45, "ADF": 28,
                  "EE": 3.0, "ASH": 8.5, "Ca": 0.42, "P": 0.26, "TDN": 55},
    },
    "أغنام": {
        "حليب": {"CP": 18.0, "DP": 14.5, "SE": 68, "NDF": 30, "ADF": 19,
                 "EE": 4.5, "ASH": 8.5, "Ca": 0.75, "P": 0.42, "TDN": 72},
        "تسمين": {"CP": 14.5, "DP": 11.5, "SE": 64, "NDF": 28, "ADF": 17,
                  "EE": 4.0, "ASH": 8.0, "Ca": 0.65, "P": 0.36, "TDN": 70},
        "صيانة": {"CP": 9.5, "DP": 7.2, "SE": 48, "NDF": 45, "ADF": 28,
                  "EE": 3.0, "ASH": 8.5, "Ca": 0.42, "P": 0.26, "TDN": 52},
    },
    "ماعز": {
        "حليب": {"CP": 17.5, "DP": 14.0, "SE": 66, "NDF": 30, "ADF": 19,
                 "EE": 4.5, "ASH": 8.5, "Ca": 0.75, "P": 0.42, "TDN": 70},
        "تسمين": {"CP": 14.0, "DP": 11.0, "SE": 62, "NDF": 30, "ADF": 19,
                  "EE": 3.8, "ASH": 8.0, "Ca": 0.62, "P": 0.34, "TDN": 68},
        "صيانة": {"CP": 9.0, "DP": 6.8, "SE": 46, "NDF": 46, "ADF": 28,
                  "EE": 3.0, "ASH": 8.5, "Ca": 0.42, "P": 0.26, "TDN": 50},
    },
    "دواجن": {
        "بادي": {"CP": 23.0, "DP": 20.0, "SE": 76, "NDF": 8, "ADF": 4,
                 "EE": 5.0, "ASH": 6.5, "Ca": 1.00, "P": 0.50, "TDN": 80},
        "نامي": {"CP": 21.0, "DP": 18.5, "SE": 74, "NDF": 9, "ADF": 5,
                 "EE": 5.0, "ASH": 6.0, "Ca": 0.90, "P": 0.45, "TDN": 78},
        "ناهي": {"CP": 19.5, "DP": 17.0, "SE": 75, "NDF": 10, "ADF": 5.5,
                 "EE": 4.5, "ASH": 6.0, "Ca": 0.87, "P": 0.43, "TDN": 79},
    },
    "سمان": {
        "بادي": {"CP": 24.0, "DP": 20.5, "SE": 74, "NDF": 8, "ADF": 4,
                 "EE": 5.5, "ASH": 6.5, "Ca": 1.00, "P": 0.55, "TDN": 80},
        "بياض": {"CP": 18.0, "DP": 15.0, "SE": 68, "NDF": 11, "ADF": 5.5,
                 "EE": 4.5, "ASH": 9.0, "Ca": 2.50, "P": 0.45, "TDN": 74},
    },
    "أسماك": {
        "بادئ": {"CP": 40.0, "DP": 32.0, "SE": 72, "NDF": 8, "ADF": 4,
                 "EE": 10.0, "ASH": 11.0, "Ca": 1.50, "P": 0.90, "TDN": 78},
        "نمو": {"CP": 32.0, "DP": 25.0, "SE": 70, "NDF": 12, "ADF": 6,
                "EE": 8.0, "ASH": 9.0, "Ca": 1.00, "P": 0.70, "TDN": 75},
        "تسمين": {"CP": 28.0, "DP": 22.0, "SE": 68, "NDF": 13, "ADF": 7,
                  "EE": 8.0, "ASH": 9.5, "Ca": 0.90, "P": 0.65, "TDN": 73},
    },
    "خيول": {
        "رياضة": {"CP": 13.5, "DP": 10.5, "SE": 70, "NDF": 30, "ADF": 18,
                  "EE": 7.0, "ASH": 7.5, "Ca": 0.70, "P": 0.40, "TDN": 72},
        "صيانة": {"CP": 9.5, "DP": 7.2, "SE": 53, "NDF": 46, "ADF": 29,
                  "EE": 3.5, "ASH": 8.0, "Ca": 0.45, "P": 0.28, "TDN": 55},
    },
    "إبل": {
        "حليب": {"CP": 15.0, "DP": 12.0, "SE": 62, "NDF": 32, "ADF": 20,
                 "EE": 5.0, "ASH": 8.5, "Ca": 0.70, "P": 0.40, "TDN": 68},
        "تسمين": {"CP": 12.0, "DP": 9.5, "SE": 65, "NDF": 35, "ADF": 22,
                  "EE": 4.5, "ASH": 7.5, "Ca": 0.60, "P": 0.35, "TDN": 70},
        "صيانة": {"CP": 9.0, "DP": 7.0, "SE": 48, "NDF": 48, "ADF": 30,
                  "EE": 3.5, "ASH": 9.0, "Ca": 0.42, "P": 0.26, "TDN": 52},
    },
}

# معاملات الهضم حسب نوع الحيوان
DIGESTIBILITY_COEFFICIENTS = {
    "default": {"DM": 0.85, "CP": 0.80, "EE": 0.85, "CF": 0.55, "NFE": 0.80},
    "أبقار": {"DM": 0.72, "CP": 0.75, "EE": 0.80, "CF": 0.60, "NFE": 0.78},
    "أغنام": {"DM": 0.70, "CP": 0.72, "EE": 0.78, "CF": 0.58, "NFE": 0.76},
    "ماعز": {"DM": 0.68, "CP": 0.70, "EE": 0.76, "CF": 0.60, "NFE": 0.74},
    "خيول": {"DM": 0.68, "CP": 0.75, "EE": 0.75, "CF": 0.45, "NFE": 0.80},
    "إبل": {"DM": 0.65, "CP": 0.70, "EE": 0.72, "CF": 0.55, "NFE": 0.72},
    "دواجن": {"DM": 0.85, "CP": 0.85, "EE": 0.90, "CF": 0.20, "NFE": 0.85},
    "سمان": {"DM": 0.85, "CP": 0.85, "EE": 0.90, "CF": 0.20, "NFE": 0.85},
    "أسماك": {"DM": 0.80, "CP": 0.88, "EE": 0.92, "CF": 0.25, "NFE": 0.75},
}


def compute_proximate_analysis(formula):
    """التحليل التقريبي الكامل (Weende)"""
    total_moisture = 0.0
    total_cp = 0.0
    total_ee = 0.0
    total_cf = 0.0
    total_ash = 0.0
    total_ndf = 0.0
    total_adf = 0.0
    total_ca = 0.0
    total_p = 0.0

    for ing, pct in formula.items():
        feed_data = FLAT_FEED_DB.get(ing, {})
        f = pct / 100.0
        total_moisture += f * 10.0
        total_cp += f * feed_data.get("CP", 0)
        total_ee += f * feed_data.get("EE", 0)
        total_ndf += f * feed_data.get("NDF", 0)
        total_adf += f * feed_data.get("ADF", 0)
        total_ash += f * feed_data.get("ASH", 0)
        total_ca += f * feed_data.get("Ca", 0)
        total_p += f * feed_data.get("P", 0)
        total_cf += f * (feed_data.get("ADF", 0) * 0.6)

    dm = 100.0 - total_moisture
    nfe = max(0, dm - total_cp - total_ee - total_cf - total_ash)

    return {
        "الرطوبة": total_moisture,
        "المادة الجافة (DM)": dm,
        "البروتين الخام (CP)": total_cp,
        "الدهن الخام (EE)": total_ee,
        "الألياف الخام (CF)": total_cf,
        "الرماد (Ash)": total_ash,
        "الكربوهيدرات الذائبة (NFE)": nfe,
        "NDF": total_ndf,
        "ADF": total_adf,
        "ADL": total_adf * 0.25,
        "السيليلوز": total_adf * 0.75,
        "الهيميسيليلوز": total_ndf - total_adf,
        "Ca": total_ca,
        "P": total_p,
    }


def compute_energy_values(proximate_data, animal_type="default"):
    """حساب قيم الطاقة المتعددة"""
    dm = proximate_data.get("المادة الجافة (DM)", 90)
    cp = proximate_data.get("البروتين الخام (CP)", 15)
    ee = proximate_data.get("الدهن الخام (EE)", 4)
    cf = proximate_data.get("الألياف الخام (CF)", 10)
    nfe = proximate_data.get("الكربوهيدرات الذائبة (NFE)", 60)

    coef = DIGESTIBILITY_COEFFICIENTS.get(
        animal_type, DIGESTIBILITY_COEFFICIENTS["default"])
    dcp = cp * coef["CP"]
    dee = ee * coef["EE"]
    dcf = cf * coef["CF"]
    dnfe = nfe * coef["NFE"]

    tdn = dcp + 2.25 * dee + dcf + dnfe
    tdn_pct = (tdn / dm) * 100 if dm > 0 else 0
    de = tdn_pct * 0.04409

    if animal_type in ["دواجن", "سمان"]:
        me = de * 0.90
    elif animal_type in ["أبقار", "أغنام", "ماعز", "إبل"]:
        me = de * 0.82
    elif animal_type == "خيول":
        me = de * 0.85
    elif animal_type == "أسماك":
        me = de * 0.88
    else:
        me = de * 0.85

    ne_lact = me * 0.64 if animal_type in ["أبقار", "أغنام", "ماعز"] else 0
    ne_gain = me * 0.55
    ne_maint = me * 0.70

    return {
        "TDN %": tdn_pct,
        "DE (Mcal/kg)": de,
        "ME (Mcal/kg)": me,
        "NE_lactation (Mcal/kg)": ne_lact,
        "NE_gain (Mcal/kg)": ne_gain,
        "NE_maintenance (Mcal/kg)": ne_maint,
    }


def predict_amino_acids(formula, animal_type="default"):
    """تقدير الأحماض الأمينية الأساسية"""
    cp_total = 0.0
    for ing, pct in formula.items():
        feed_data = FLAT_FEED_DB.get(ing, {})
        cp_total += (pct / 100.0) * feed_data.get("CP", 0)

    if animal_type in ["دواجن", "سمان"]:
        ratios = {"الليسين": 0.052, "الميثيونين": 0.022,
                  "الميثيونين + السيستين": 0.038,
                  "الثريونين": 0.034, "التريبتوفان": 0.010,
                  "الفالين": 0.042, "الأرجينين": 0.062}
    elif animal_type == "أسماك":
        ratios = {"الليسين": 0.058, "الميثيونين": 0.026,
                  "الميثيونين + السيستين": 0.042,
                  "الثريونين": 0.038, "التريبتوفان": 0.012,
                  "الفالين": 0.045, "الأرجينين": 0.055}
    else:
        ratios = {"الليسين": 0.045, "الميثيونين": 0.018,
                  "الميثيونين + السيستين": 0.032,
                  "الثريونين": 0.030, "التريبتوفان": 0.009,
                  "الفالين": 0.036, "الأرجينين": 0.048}

    return {k: cp_total * v for k, v in ratios.items()}


def predict_performance(proximate, energy, animal_type, weight_kg=500,
                          milk_yield=20):
    """توقع الأداء الإنتاجي"""
    cp = proximate.get("البروتين الخام (CP)", 0)
    tdn = energy.get("TDN %", 0)
    me = energy.get("ME (Mcal/kg)", 0)
    predictions = {}

    if animal_type in ["أبقار", "أغنام", "ماعز"]:
        dm_intake = weight_kg * 0.025
        ne_lact = energy.get("NE_lactation (Mcal/kg)", 1.5)
        ne_intake = dm_intake * ne_lact
        ne_maint = 0.08 * (weight_kg ** 0.75)
        ne_for_milk = max(0, ne_intake - ne_maint)
        predicted_milk = ne_for_milk / 0.75 if ne_for_milk > 0 else 0
        predictions["🥛 إنتاج حليب متوقع (لتر/يوم)"] = predicted_milk
        predictions["🌾 استهلاك مادة جافة (كجم/يوم)"] = dm_intake

    if animal_type in ["أبقار", "أغنام", "ماعز", "إبل"]:
        gain_energy = energy.get("NE_gain (Mcal/kg)", 1.2)
        dm_intake = weight_kg * 0.025
        ne_gain_intake = dm_intake * gain_energy
        predicted_adg = ne_gain_intake / 3.5 if ne_gain_intake > 0 else 0
        predictions["📈 زيادة وزن يومية متوقعة (كجم)"] = predicted_adg

    if animal_type in ["دواجن", "سمان"]:
        me_actual = energy.get("ME (Mcal/kg)", 3.0)
        if me_actual > 0:
            fcr_expected = 3.0 / me_actual * 1.8
            predictions["⚖️ معامل تحويل متوقع (FCR)"] = fcr_expected

    if tdn > 0:
        efficiency = min(100, (tdn / 75) * 100)
        predictions["🎯 كفاءة الطاقة"] = f"{efficiency:.1f}%"

    quality_score = 0
    if 14 <= cp <= 20: quality_score += 25
    elif 12 <= cp <= 22: quality_score += 20
    if tdn >= 65: quality_score += 25
    elif tdn >= 55: quality_score += 15
    if 30 <= proximate.get("NDF", 30) <= 45: quality_score += 25
    if 8 <= proximate.get("الرطوبة", 10) <= 12: quality_score += 25

    predictions["🏆 مؤشر الجودة العام"] = f"{quality_score}/100"
    return predictions


def generate_ai_recommendations(proximate, energy, amino_acids,
                                  animal_type, requirement=None,
                                  reference=None):
    """توصيات ذكية"""
    recommendations = []
    cp = proximate.get("البروتين الخام (CP)", 0)
    ee = proximate.get("الدهن الخام (EE)", 0)
    ndf = proximate.get("NDF", 0)
    ash = proximate.get("الرماد (Ash)", 0)
    tdn = energy.get("TDN %", 0)
    lysine = amino_acids.get("الليسين", 0)
    methionine = amino_acids.get("الميثيونين", 0)
    moisture = proximate.get("الرطوبة", 0)

    if reference:
        if cp < reference.get("CP", 0) * 0.95:
            recommendations.append({
                "type": "warning", "priority": "عالية",
                "title": "🔴 البروتين الخام منخفض",
                "text": f"CP الحالي {cp:.2f}% أقل من المعيار "
                        f"{reference.get('CP', 0):.2f}%. أضف كسب صويا 44%."})
        elif cp > reference.get("CP", 0) * 1.15:
            recommendations.append({
                "type": "warning", "priority": "متوسطة",
                "title": "🟡 البروتين الخام مرتفع",
                "text": f"CP الحالي {cp:.2f}% أعلى من المعيار — قلل الأكساب."})

        if tdn < reference.get("TDN", 0) * 0.90:
            recommendations.append({
                "type": "warning", "priority": "عالية",
                "title": "🔴 الطاقة منخفضة",
                "text": f"TDN الحالي {tdn:.1f}% أقل من المعيار "
                        f"{reference.get('TDN', 0)}%. أضف ذرة أو زيت."})

    if ee > 6.0:
        recommendations.append({
            "type": "warning", "priority": "عالية",
            "title": "🟡 الدهون مرتفعة",
            "text": f"EE الحالي {ee:.2f}% — خطر Milk Fat Depression."})
    elif ee < 2.5:
        recommendations.append({
            "type": "info", "priority": "منخفضة",
            "title": "⚡ فرصة لتحسين الطاقة",
            "text": f"EE الحالي {ee:.2f}% — أضف 2-3% زيت."})

    if animal_type in ["أبقار", "أغنام", "ماعز", "إبل"]:
        if ndf < 28:
            recommendations.append({
                "type": "warning", "priority": "عالية",
                "title": "🔴 NDF منخفض",
                "text": f"NDF الحالي {ndf:.1f}% — خطر حموضة الكرش."})
        elif ndf > 48:
            recommendations.append({
                "type": "warning", "priority": "متوسطة",
                "title": "🟡 NDF مرتفع",
                "text": f"NDF الحالي {ndf:.1f}% — يحد من الاستهلاك."})

    if ash > 12:
        recommendations.append({
            "type": "info", "priority": "منخفضة",
            "title": "ℹ️ الرماد مرتفع",
            "text": f"Ash {ash:.2f}% — افحص جودة المواد."})

    if animal_type in ["دواجن", "سمان"]:
        if lysine < 1.0:
            recommendations.append({
                "type": "warning", "priority": "عالية",
                "title": "🔴 الليسين منخفض",
                "text": f"الليسين {lysine:.3f}% — أضف L-Lysine."})
        if methionine < 0.4:
            recommendations.append({
                "type": "warning", "priority": "عالية",
                "title": "🔴 الميثيونين منخفض",
                "text": f"الميثيونين {methionine:.3f}% — أضف DL-Methionine."})

    if moisture > 13:
        recommendations.append({
            "type": "warning", "priority": "عالية",
            "title": "🔴 رطوبة عالية",
            "text": f"الرطوبة {moisture:.1f}% — خطر الفطريات."})

    if not recommendations:
        recommendations.append({
            "type": "success", "priority": "لا يوجد",
            "title": "✅ التركيبة متوازنة",
            "text": "جميع العناصر ضمن النطاق المثالي."})

    return recommendations


def compute_comprehensive_lab_analysis(formula, animal_type,
                                         weight_kg=500, milk_yield=20,
                                         requirement=None, reference=None):
    """التحليل الشامل الكامل"""
    proximate = compute_proximate_analysis(formula)
    energy = compute_energy_values(proximate, animal_type)
    amino_acids = predict_amino_acids(formula, animal_type)
    performance = predict_performance(proximate, energy, animal_type,
                                        weight_kg, milk_yield)
    recommendations = generate_ai_recommendations(
        proximate, energy, amino_acids, animal_type,
        requirement, reference)
    return {
        "proximate": proximate,
        "energy": energy,
        "amino_acids": amino_acids,
        "performance": performance,
        "recommendations": recommendations,
    }


# ═════════════════════════════════════════════════════════════════════════════
# القسم 13: المستشار الذكي (SmartFeedAdvisor)
# ═════════════════════════════════════════════════════════════════════════════

class SmartFeedAdvisor:
    KNOWLEDGE_PATTERNS = {
        "قلة الحليب": {
            "symptoms": ["انخفاض", "قلة", "ضعف", "إدرار", "حليب"],
            "causes": ["نقص الطاقة", "نقص البروتين", "نقص الأملاح",
                        "الإجهاد الحراري", "التهاب الضرع"],
            "solutions": [
                "زد معادل النشاء إلى 70-72 وحدة",
                "أضف 2-3% زيت صويا لرفع الطاقة",
                "تأكد من توازن الكالسيوم/الفسفور",
                "أضف بيكربونات الصوديوم 0.75%",
                "وفر ماء بارداً نظيفاً باستمرار",
                "افحص الضرع يومياً"],
        },
        "ضعف النمو": {
            "symptoms": ["ضعف نمو", "بطء", "نحافة", "هزال", "نمو"],
            "causes": ["نقص بروتين", "نقص طاقة", "طفيليات",
                        "مشاكل هضمية"],
            "solutions": [
                "ارفع DP إلى المعيار المطلوب",
                "أضف 5-10% كسب صويا للخلطة",
                "استخدم إنزيمات هاضمة",
                "اعمل برنامج تجريع ضد الطفيليات",
                "تأكد من نظافة المعالف"],
        },
        "مشاكل هضمية": {
            "symptoms": ["إسهال", "انتفاخ", "حموضة", "كرش", "هضم"],
            "causes": ["نقص ألياف", "زيادة حبوب سريعة",
                        "انتقال مفاجئ", "تلوث"],
            "solutions": [
                "زد NDF إلى 30-35% (أضف دريس/برسيم)",
                "أضف بيكربونات الصوديوم 1%",
                "قلل الحبوب إلى أقل من 60%",
                "انتقل تدريجياً للعلف الجديد (7-10 أيام)",
                "أضف خمائر حية ومنشطات"],
        },
        "ضعف البيض": {
            "symptoms": ["قلة بيض", "بيض ضعيف", "قشرة", "بيض"],
            "causes": ["نقص كالسيوم", "نقص بروتين", "نقص فيتامين D",
                        "إجهاد"],
            "solutions": [
                "ارفع الكالسيوم إلى 3.8-4%",
                "أضف مسحوق صدف أو حجر جيري خشن",
                "أضف كسب صويا لتوازن الليسين",
                "أضف 2500 IU/kg فيتامين D3",
                "قلل الإجهاد والازدحام"],
        },
    }

    @staticmethod
    def advise(problem_description):
        problem_lower = problem_description.strip().lower()
        matches = []
        for issue, data in SmartFeedAdvisor.KNOWLEDGE_PATTERNS.items():
            for sym in data["symptoms"]:
                if sym in problem_lower:
                    matches.append({"issue": issue, **data})
                    break
        if not matches:
            return {
                "found": False,
                "suggestions": [
                    "يرجى وصف المشكلة بمزيد من التفاصيل",
                    "اذكر نوع الحيوان والعمر والأعراض",
                    "أمثلة: قلة الحليب، ضعف النمو، إسهال، قلة بيض"]}
        return {"found": True, "matches": matches}


# ═════════════════════════════════════════════════════════════════════════════
# القسم 14: قاعدة البيانات
# ═════════════════════════════════════════════════════════════════════════════

class DatabaseManager:
    def __init__(self, db_path="tawornology_platform.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT,
            role TEXT, full_name TEXT, email TEXT, phone TEXT, specialty TEXT,
            experience_years INTEGER, created_date TEXT, last_login TEXT,
            is_active INTEGER DEFAULT 1)''')
        c.execute('''CREATE TABLE IF NOT EXISTS farms (
            farm_id TEXT PRIMARY KEY, farm_name TEXT, farm_type TEXT,
            owner_name TEXT, owner_phone TEXT, location TEXT, area REAL,
            created_date TEXT, last_updated TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas (
            formula_id TEXT PRIMARY KEY, formula_name TEXT, animal_type TEXT,
            breed TEXT, stage TEXT, target_dp REAL, target_se REAL,
            ingredients TEXT, total_cost REAL, cost_per_ton REAL,
            created_by TEXT, created_date TEXT, requester_name TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS lab_results (
            result_id TEXT PRIMARY KEY, sample_name TEXT, sample_type TEXT,
            cp REAL, dc REAL, se REAL, ndf REAL, adf REAL, ee REAL,
            ash REAL, moisture REAL, analysis_date TEXT, analyzed_by TEXT,
            notes TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS barns (
            barn_id TEXT PRIMARY KEY, barn_name TEXT, animal_type TEXT,
            purpose TEXT, capacity INTEGER, area_m2 REAL, length_m REAL,
            width_m REAL, height_m REAL, ventilation_m3_h REAL,
            created_date TEXT, notes TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS dose_reminders (
            reminder_id TEXT PRIMARY KEY, animal_type TEXT, dose_type TEXT,
            dose_name TEXT, dose_amount REAL, dose_unit TEXT,
            administration_route TEXT, frequency_days INTEGER,
            start_date TEXT, next_dose_date TEXT, notes TEXT, active BOOLEAN,
            created_by TEXT, created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS price_history (
            record_id TEXT PRIMARY KEY, ingredient_name TEXT, price REAL,
            currency TEXT, country TEXT, city TEXT, record_date TEXT,
            recorded_by TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT PRIMARY KEY, item_name TEXT UNIQUE, quantity REAL,
            min_threshold REAL, unit TEXT, last_updated TEXT)''')
        conn.commit()
        conn.close()

    def execute_query(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        result = c.execute(query, params)
        conn.commit()
        data = result.fetchall()
        conn.close()
        return data

    def insert_record(self, table, data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        c.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
                  list(data.values()))
        conn.commit()
        conn.close()
        return True

    def get_records(self, table, conditions=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if conditions:
            where = ' AND '.join([f"{k}=?" for k in conditions.keys()])
            result = c.execute(f"SELECT * FROM {table} WHERE {where}",
                                list(conditions.values()))
        else:
            result = c.execute(f"SELECT * FROM {table}")
        data = result.fetchall()
        conn.close()
        return data


# ═════════════════════════════════════════════════════════════════════════════
# القسم 15: نظام التنبؤ بالأسعار
# ═════════════════════════════════════════════════════════════════════════════

class PricePredictor:
    def __init__(self):
        self.db = DatabaseManager()

    def predict_price(self, ingredient_name, days_ahead=7):
        prices = self.db.execute_query(
            "SELECT price FROM price_history WHERE ingredient_name=? "
            "ORDER BY record_date DESC LIMIT 30", (ingredient_name,))
        if len(prices) < 5:
            return {'prediction': None, 'confidence': 0,
                    'current_price': None, 'trend': 'stable'}
        price_list = [p[0] for p in prices]
        weights = np.array(range(1, len(price_list) + 1))
        weighted_avg = np.average(price_list, weights=weights)
        trend = (price_list[0] - price_list[-1]) / len(price_list) \
            if len(price_list) > 1 else 0
        prediction = weighted_avg + (trend * days_ahead)
        return {'prediction': max(0, prediction),
                'confidence': min(1, len(price_list) / 30),
                'current_price': price_list[0] if price_list else None,
                'trend': trend}


# ═════════════════════════════════════════════════════════════════════════════
# القسم 16: OCR المختبر الذكي
# ═════════════════════════════════════════════════════════════════════════════

def match_ingredient_name(text):
    if not text:
        return None
    tl = text.strip().lower()
    for cat in BIG_FEEDS_LIBRARY.values():
        for name in cat.keys():
            if name.lower() in tl or tl in name.lower():
                return name
    kw = {"ذرة": "ذرة صفراء", "صويا": "كسب فول صويا 44%",
          "شعير": "شعير مطحون", "قمح": "قمح محلي",
          "نخالة": "نخالة قمح (ردة)",
          "فول سوداني": "أمباز الفول السوداني (كسب)",
          "ملح": "ملح الطعام",
          "حجر": "الحجر الجيري (بودرة بلاط)",
          "فوسفات": "فوسفات ثنائي الكالسيوم (DCP)",
          "بيكربونات": "بيكربونات الصوديوم",
          "زيت": "زيت فول الصويا"}
    for k, m in kw.items():
        if k in tl:
            return m
    return None


def extract_ingredients_from_image(image_bytes):
    if not OCR_AVAILABLE or not CV2_AVAILABLE:
        return {"success": False, "message": "مكتبات OCR غير مثبتة"}
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"success": False, "message": "تعذر قراءة الصورة"}
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)
        _, t2 = cv2.threshold(gray, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        try:
            txt = pytesseract.image_to_string(t2, lang='ara+eng',
                config=r'--oem 3 --psm 6')
        except Exception:
            return {"success": False, "message": "فشل OCR"}
        ingredients = {}
        for line in txt.split('\n'):
            line = line.strip()
            if len(line) < 3:
                continue
            for pat in [r'([\u0600-\u06FFa-zA-Z\s\(\)%]+?)[\s:\-=]+(\d+\.?\d*)\s*%',
                        r'([\u0600-\u06FFa-zA-Z\s\(\)%]+?)\s+(\d+\.?\d*)\s*%']:
                m = re.search(pat, line)
                if m:
                    name, val = m.group(1).strip(), float(m.group(2))
                    if 0.1 < val <= 100 and len(name) > 2:
                        matched = match_ingredient_name(name)
                        if matched:
                            ingredients[matched] = val
                            break
        return {"success": True, "ingredients": ingredients,
                "raw_text": txt, "count": len(ingredients)}
    except Exception as e:
        return {"success": False, "message": f"خطأ: {str(e)}"}


# ═════════════════════════════════════════════════════════════════════════════
# القسم 17: الرسوم البيانية
# ═════════════════════════════════════════════════════════════════════════════

def create_colorful_bar_chart(standard, actual):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        nutrients = [n for n in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH"]
                     if n in standard]
        if not nutrients:
            return None
        std_vals = [standard[n] for n in nutrients]
        act_vals = [actual.get(n, 0) for n in nutrients]
        fig, ax = plt.subplots(figsize=(9, 4.5))
        x = np.arange(len(nutrients))
        width = 0.35
        ax.bar(x - width/2, std_vals, width, label='المعيار',
               color='#1976d2', edgecolor='#0d47a1', linewidth=1.5)
        ax.bar(x + width/2, act_vals, width, label='المحسوب',
               color='#43a047', edgecolor='#1b5e20', linewidth=1.5)
        ax.set_xlabel('العنصر', fontsize=11, fontweight='bold')
        ax.set_ylabel('القيمة', fontsize=11, fontweight='bold')
        ax.set_title('مقارنة العناصر', fontsize=13,
                     fontweight='bold', color='#1b5e20')
        ax.set_xticks(x)
        ax.set_xticklabels(nutrients, fontsize=10)
        ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_colorful_pie_chart(formula):
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2:
        return None
    try:
        colors = ['#e53935', '#8e24aa', '#3949ab', '#1e88e5', '#00897b',
                  '#43a047', '#7cb342', '#fdd835', '#fb8c00', '#6d4c41']
        names = list(formula.keys())
        vals = list(formula.values())
        fig, ax = plt.subplots(figsize=(8, 5))
        wedges, texts, autotexts = ax.pie(vals, autopct='%1.1f%%',
            colors=colors[:len(names)], startangle=90, pctdistance=0.75,
            wedgeprops=dict(edgecolor='white', linewidth=2))
        for t in autotexts:
            t.set_color('white')
            t.set_fontweight('bold')
        ax.legend(names, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
                  fontsize=9)
        ax.set_title('توزيع المكونات', fontsize=13, fontweight='bold',
                     color='#1b5e20')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_radar_chart(standard, actual):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        nutrients = [n for n in ["CP", "DP", "SE", "NDF", "ADF", "EE", "Ca", "P"]
                     if n in standard and standard[n] > 0]
        if len(nutrients) < 3:
            return None
        std_norm = [100.0 for _ in nutrients]
        act_norm = [(actual.get(n, 0) / standard[n]) * 100 for n in nutrients]
        angles = np.linspace(0, 2 * np.pi, len(nutrients),
                              endpoint=False).tolist()
        std_norm += std_norm[:1]
        act_norm += act_norm[:1]
        angles += angles[:1]
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, std_norm, 'o-', linewidth=2.5,
                color='#1976d2', label='المعيار')
        ax.fill(angles, std_norm, alpha=0.15, color='#1976d2')
        ax.plot(angles, act_norm, 'o-', linewidth=2.5,
                color='#43a047', label='المحسوب')
        ax.fill(angles, act_norm, alpha=0.25, color='#43a047')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(nutrients, fontsize=10)
        ax.set_title('المقارنة الشاملة', fontsize=12,
                     fontweight='bold', color='#1b5e20', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_gauge_chart(score):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        fig, ax = plt.subplots(figsize=(4, 4),
                                subplot_kw=dict(aspect='equal'))
        colors_g = ['#c62828', '#ef6c00', '#f9a825',
                    '#7cb342', '#43a047', '#1b5e20']
        for i, c in enumerate(colors_g):
            theta1 = 180 - (i * 30)
            theta2 = 180 - ((i + 1) * 30)
            ax.add_patch(Wedge((0, 0), 1, theta2, theta1, width=0.3,
                               facecolor=c, edgecolor='white', linewidth=2))
        angle = 180 - (score / 100) * 180
        rad = np.radians(angle)
        ax.plot([0, 0.85 * np.cos(rad)], [0, 0.85 * np.sin(rad)],
                color='#1a1a1a', linewidth=3, zorder=10)
        ax.add_patch(Circle((0, 0), 0.08, color='#1a1a1a', zorder=11))
        ax.text(0, -0.25, f'{score:.0f}%', ha='center', fontsize=20,
                fontweight='bold', color='#1b5e20')
        ax.text(0, -0.5, 'التقييم', ha='center', fontsize=11, color='#666')
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.7, 1.2)
        ax.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


# ═════════════════════════════════════════════════════════════════════════════
# القسم 18: مولد PDF
# ═════════════════════════════════════════════════════════════════════════════

class PDFGenerator:
    def __init__(self):
        self.font_name = font_mgr.font_name
        self.font_bold = font_mgr.font_bold

    def _ar(self, text):
        return ar(text)

    def _draw_page(self, canvas_obj, doc):
        canvas_obj.saveState()
        w, h = doc.pagesize
        # ترويسة
        canvas_obj.setFillColor(HexColor('#1b5e20'))
        canvas_obj.rect(0, h-90, w, 90, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor('#d4af37'))
        canvas_obj.rect(0, h-95, w, 5, fill=1, stroke=0)
        canvas_obj.setFillColor(white)
        canvas_obj.setFont(self.font_name, 22)
        canvas_obj.drawCentredString(w/2, h-38,
            self._ar("تاور نولجي  Tawor Nology"))
        canvas_obj.setFont(self.font_name, 12)
        canvas_obj.setFillColor(HexColor('#e8f5e9'))
        canvas_obj.drawCentredString(w/2, h-58,
            self._ar("للإنتاج الحيواني وتغذية الحيوان"))
        canvas_obj.setFont(self.font_name, 10)
        canvas_obj.setFillColor(HexColor('#d4af37'))
        canvas_obj.drawCentredString(w/2, h-76,
            self._ar(f"إشراف: {SUPERVISOR} — {SUPERVISOR_TITLE}"))
        # تذييل الدعاء
        canvas_obj.setFillColor(HexColor('#1b5e20'))
        canvas_obj.rect(0, 42, w, 42, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor('#ffeb3b'))
        canvas_obj.setFont(self.font_name, 10)
        canvas_obj.drawCentredString(w/2, 68, self._ar(f"🤲 {DUA_SHORT} 🤲"))
        # تذييل سفلي
        canvas_obj.setFillColor(HexColor('#1b5e20'))
        canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)
        canvas_obj.setFillColor(white)
        canvas_obj.setFont(self.font_name, 8)
        canvas_obj.drawCentredString(w/2, 27,
            self._ar("تاور نولجي Tawor Nology © 2026"))
        canvas_obj.setFont(self.font_name, 7)
        canvas_obj.drawCentredString(w/2, 12,
            self._ar(f"صفحة {canvas_obj.getPageNumber()}"))
        canvas_obj.restoreState()

    def _comparison_table(self, standard, calculated):
        labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم",
                  "SE": "معادل النشاء", "NDF": "NDF", "ADF": "ADF",
                  "EE": "دهن", "ASH": "رماد", "Ca": "كالسيوم", "P": "فسفور"}
        header = [self._ar(x) for x in ["العنصر", "المعيار", "المحسوب",
                                          "الفرق", "التقييم"]]
        data = [header]
        cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#9e9e9e'))]
        row = 1
        for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
            if k not in standard:
                continue
            sv = standard[k]
            cv = calculated.get(k, 0.0)
            diff = cv - sv
            pct = (diff / sv * 100) if sv else 0
            ev = evaluate_difference(pct)
            data.append([self._ar(labels.get(k, k)), f"{sv:.2f}",
                         f"{cv:.2f}", f"{diff:+.3f}",
                         self._ar(ev["label"])])
            cmds.append(('BACKGROUND', (0, row), (-1, row),
                         HexColor(ev["bg"])))
            row += 1
        t = Table(data, colWidths=[120, 80, 80, 80, 130])
        t.setStyle(TableStyle(cmds))
        return t

    def generate_report(self, formula, requirement, animal_type, breed,
                        cost, city, local_cost, local_sym,
                        requester_name="", protein_basis="DP",
                        standard_key="", include_charts=True):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
            rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text),
                ParagraphStyle('s', fontName=self.font_name, fontSize=size,
                    alignment=align, textColor=HexColor(color),
                    spaceAfter=6, leading=size * 1.6))

        story.append(P("تقرير فني رسمي", size=20,
                       align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
                                color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))

        client_data = [
            [self._ar("طالب الخدمة:"),
             self._ar(requester_name or "........................")],
            [self._ar("الموقع:"), self._ar(city)],
            [self._ar("الفصيل:"), self._ar(f"{animal_type} — {breed}")],
            [self._ar("أساس الحساب:"), self._ar(protein_basis)],
            [self._ar("التاريخ:"),
             datetime.now().strftime('%Y-%m-%d | %H:%M')]]
        ct = Table(client_data, colWidths=[150, 340])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 9)]))
        story.append(ct)
        story.append(Spacer(1, 15))

        standard_vals = requirement_to_standard(requirement)
        calculated_vals = compute_formula_nutrients(formula)

        story.append(P("جدول مقارنة العناصر", size=14,
                       align=TA_RIGHT, color='#1b5e20'))
        story.append(Spacer(1, 8))
        story.append(self._comparison_table(standard_vals, calculated_vals))
        story.append(Spacer(1, 15))

        # التحليل التقريبي
        prox = compute_proximate_analysis(formula)
        story.append(P("التحليل التقريبي (Weende)", size=14,
                       align=TA_RIGHT, color='#1565c0'))
        story.append(Spacer(1, 8))
        prox_rows = [[self._ar("العنصر"), self._ar("القيمة")]]
        for k, v in prox.items():
            prox_rows.append([self._ar(k), f"{v:.2f}%"])
        pt = Table(prox_rows, colWidths=[250, 250])
        pt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565c0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#1565c0'))]))
        story.append(pt)
        story.append(Spacer(1, 12))

        # الطاقة
        energy = compute_energy_values(prox, animal_type)
        story.append(P("تحليل الطاقة", size=14,
                       align=TA_RIGHT, color='#e65100'))
        story.append(Spacer(1, 8))
        e_rows = [[self._ar("النوع"), self._ar("القيمة")]]
        for k, v in energy.items():
            e_rows.append([self._ar(k), f"{v:.3f}"])
        et = Table(e_rows, colWidths=[250, 250])
        et.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e65100')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e65100'))]))
        story.append(et)
        story.append(Spacer(1, 12))

        if include_charts:
            c1 = create_colorful_bar_chart(standard_vals, calculated_vals)
            if c1:
                story.append(RLImage(c1, width=450, height=250))
                story.append(Spacer(1, 12))
            c2 = create_colorful_pie_chart(formula)
            if c2:
                story.append(RLImage(c2, width=400, height=280))

        story.append(PageBreak())

        # التكاليف
        story.append(P("التكاليف", size=14, align=TA_RIGHT, color='#1b5e20'))
        story.append(Spacer(1, 8))
        cost_data = [[self._ar("البند"), self._ar("القيمة")],
                     [self._ar("التكلفة للطن (دولار)"), f"${cost:.2f}"],
                     [self._ar(f"التكلفة ({local_sym})"),
                      f"{local_cost:,.2f}"]]
        tc = Table(cost_data, colWidths=[280, 210])
        tc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#2e7d32')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name)]))
        story.append(tc)
        story.append(Spacer(1, 18))

        # المكونات
        if formula:
            story.append(P("المكونات للطن", size=14,
                           align=TA_RIGHT, color='#1b5e20'))
            story.append(Spacer(1, 8))
            ing_data = [[self._ar("المكون"), self._ar("النسبة %"),
                         self._ar("كجم/طن")]]
            for ing, pct in formula.items():
                ing_data.append([self._ar(ing), f"{pct:.2f}%",
                                 f"{pct*10:.1f}"])
            ti = Table(ing_data, colWidths=[270, 110, 110])
            ti.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd'))]))
            story.append(ti)

        doc.build(story, onFirstPage=self._draw_page,
                  onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()


pdf_gen = PDFGenerator()


# ═════════════════════════════════════════════════════════════════════════════
# القسم 19: تصدير Excel
# ═════════════════════════════════════════════════════════════════════════════

def export_comparison_to_excel(standard, calculated, requester_name="",
                                animal="", stage="", formula=None,
                                standard_key=""):
    if not OPENPYXL_AVAILABLE:
        return b""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "مقارنة"
    ws.sheet_view.rightToLeft = True
    hf = Font(name='Arial', size=12, bold=True, color='FFFFFF')
    hfill = PatternFill('solid', fgColor='1B5E20')
    ct = Alignment(horizontal='center', vertical='center', wrap_text=True)
    thin = Side(border_style='thin', color='9E9E9E')
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    ws.merge_cells('A1:F1')
    ws['A1'] = APP_NAME
    ws['A1'].font = Font(name='Arial', size=14, bold=True, color='1B5E20')
    ws['A1'].alignment = ct
    headers = ["العنصر", "المعيار", "المحسوب", "الفرق", "% الفرق", "التقييم"]
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=c, value=h)
        cell.font = hf
        cell.fill = hfill
        cell.alignment = ct
        cell.border = bd
    labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم", "SE": "معادل النشاء",
              "NDF": "NDF", "ADF": "ADF", "EE": "دهن", "ASH": "رماد",
              "Ca": "كالسيوم", "P": "فسفور"}
    row = 4
    for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
        if k not in standard:
            continue
        sv = standard[k]
        cv = calculated.get(k, 0.0)
        diff = cv - sv
        pct = (diff / sv * 100) if sv else 0
        ev = evaluate_difference(pct)
        vals = [labels[k], round(sv, 2), round(cv, 2), round(diff, 3),
                round(pct, 2), ev["label"]]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.alignment = ct
            cell.border = bd
            cell.fill = PatternFill('solid',
                fgColor=ev["bg"].replace('#', ''))
        row += 1
    for c in range(1, 7):
        ws.column_dimensions[get_column_letter(c)].width = 22
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


# ═════════════════════════════════════════════════════════════════════════════
# القسم 20: السوق والصور
# ═════════════════════════════════════════════════════════════════════════════

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "LIBYA": {"rate": 4.80, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"},
    "السعودية": {"rate": 3.75, "sym": "SAR"},
    "الإمارات": {"rate": 3.67, "sym": "AED"},
    "باقي دول العالم": {"rate": 1.0, "sym": "USD"},
}


def get_market_prices(country, city, state=""):
    base = {ing: 280.0 for cat in BIG_FEEDS_LIBRARY.values() for ing in cat}
    base.update({
        "ذرة صفراء": 230, "شعير مطحون": 210, "سورجم (فتريتة)": 195,
        "قمح محلي": 240, "أمباز الفول السوداني (كسب)": 460,
        "كسب فول صويا 44%": 440, "كسب عباد الشمس 36%": 310,
        "نخالة قمح (ردة)": 150, "البرسيم الجاف (الدريس)": 170,
        "مولاس قصب السكر": 120, "مسحوق أسماك 60%": 850,
        "مركزات دواجن وسمان": 650, "الحجر الجيري (بودرة بلاط)": 40,
        "فوسفات ثنائي الكالسيوم (DCP)": 280, "ملح الطعام": 30,
        "زيت فول الصويا": 1350, "زيت ذرة": 1500,
        "زيت النخيل": 1100})
    m = 1.0
    if country == "السودان":
        m = 1.15
    elif country == "LIBYA":
        m = 1.10
    elif country == "مصر":
        m = 1.04
    elif country == "السعودية":
        m = 1.08
    elif country == "الإمارات":
        m = 1.12
    return {k: v * m for k, v in base.items()}


ANIMAL_IMAGES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "إبل": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600",
    "سمان": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600",
}


@st.cache_data(ttl=3600)
def get_img_b64(paths):
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                pass
    return None


img_base64 = get_img_b64(tuple(PHOTO_OPTIONS))


# ═════════════════════════════════════════════════════════════════════════════
# القسم 21: دوال الصوت
# ═════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def text_to_speech_base64(text, lang="ar"):
    if not GTTS_AVAILABLE or not text:
        return None
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return base64.b64encode(audio_bytes.read()).decode()
    except Exception:
        return None


def play_audio_b64(audio_b64):
    if audio_b64:
        st.components.v1.html(
            f'<audio autoplay><source src="data:audio/mp3;base64,{audio_b64}" '
            f'type="audio/mpeg"></audio>', height=0)
        return True
    return False


def voice_guide_sequential(messages, lang="ar", delay_between=2.0):
    if not GTTS_AVAILABLE:
        st.warning("⚠️ الصوت غير متاح")
        return
    for i, msg in enumerate(messages):
        if msg:
            audio_b64 = text_to_speech_base64(msg, lang)
            if audio_b64:
                play_audio_b64(audio_b64)
                time.sleep(max(2.0, len(msg.split()) * 0.3 + 1.0))
                if i < len(messages) - 1:
                    time.sleep(1.0)


def voice_guide(message, lang="ar"):
    if not GTTS_AVAILABLE or not message:
        return
    audio_b64 = text_to_speech_base64(message, lang)
    if audio_b64:
        play_audio_b64(audio_b64)


def play_welcome_audio():
    voice_guide_sequential([
        "السلام عليكم ورحمة الله وبركاته،",
        "مرحباً بكم في تاور نولجي Tawor Nology العلمية،",
        "منصة الإنتاج الحيواني وتركيب الأعلاف."])


def play_dua_audio():
    voice_guide_sequential([
        "اللهم اغفر لإسماعيل تاور وابتسام،",
        "وارحمهما وأدخلهما فسيح جناتك."])


def play_full_guide_audio():
    voice_guide_sequential([
        "مرحباً بك في منصة تاور نولجي Tawor Nology العلمية،",
        "هذه المنصة متخصصة في الإنتاج الحيواني وتركيب الأعلاف.",
        "معمل تحليل شامل، مصمم حظائر، تركيب أعلاف لثمانية أنواع حيوانات،",
        "مكتبة زيوت، بدائل حليب، مختبر ذكي، مستشار ذكي.",
        "نسأل الله التوفيق والسداد."])


def generate_voice_report(formula, actual, requirement, animal_type,
                            cost, requester=""):
    messages = []
    if requester:
        messages.append(f"أهلاً {requester}، هذا تقرير خلطة {animal_type}.")
    else:
        messages.append(f"هذا تقرير خلطة {animal_type}.")
    messages.append(f"تحتوي الخلطة على {len(formula)} مكوناً.")
    messages.append(
        f"نسبة البروتين الخام {actual.get('CP', 0):.1f} بالمائة، "
        f"والبرومين المهضوم {actual.get('DP', 0):.1f} بالمائة.")
    messages.append(f"معادل النشاء {actual.get('SE', 0):.0f} وحدة.")
    oil_pct = compute_total_oil_percentage(formula)
    if oil_pct > 0:
        messages.append(f"تحتوي الخلطة على {oil_pct:.1f} بالمائة زيوت.")
    messages.append(f"التكلفة {cost:.2f} دولار للطن الواحد.")
    messages.append("نسأل الله التوفيق والسداد.")
    voice_guide_sequential(messages, delay_between=1.5)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 22: الحالة الأولية للجلسة
# ═════════════════════════════════════════════════════════════════════════════

DEFAULTS = {
    "approved": False, "user_role": None,
    "login_welcome_shown": False,
    "active_formula": {},
    "active_stage_title": "إنتاج عام",
    "active_animal_img": ANIMAL_IMAGES["عام"],
    "computed_ton_cost": 280.0,
    "inventory": {},
    "shared_comments": f"• مرحباً بكم في {APP_NAME}\n• {DUA_SHORT}\n",
    "broiler_farms": {},
    "dose_reminders": [],
    "daily_production_log": [],
    "lab_sample": None,
    "lab_sample_name": "",
    "lab_cp": 0.0, "lab_dc": 0.0, "lab_se": 0.0,
    "lab_ndf": 0.0, "lab_adf": 0.0, "lab_ee": 0.0,
    "lab_ash": 0.0, "lab_moisture": 0.0, "lab_notes": "",
    "barns": {},
    "livestock_prices": {
        "عجول تسمين ($)": 1350.0, "أبقار كنانة ($)": 900.0,
        "ضأن محلي ($)": 180.0, "ماعز نوبي ($)": 130.0,
        "إبل حاشي ($)": 1200.0, "كتكوت لاحم ($)": 0.65},
    "products_prices": {
        "كيلو لحم بقري ($)": 7.50, "كيلو لحم ضأن ($)": 9.00,
        "كيلو لحم دجاج ($)": 3.80, "طبق بيض 30 ($)": 4.20,
        "لتر حليب بقر ($)": 0.90, "لتر حليب إبل ($)": 3.50}}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state["inventory"]:
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing in cat:
            st.session_state["inventory"][ing] = {
                "quantity": 25.0, "min_threshold": 5.0, "unit": "طن"}


def is_owner():
    return st.session_state.get("user_role") == "owner"
    # ═════════════════════════════════════════════════════════════════════════════
# القسم 23: CSS المتقدم
# ═════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&family=Tajawal:wght@400;500;700;900&display=swap');
* { font-family: 'Tajawal', 'Cairo', 'Amiri', sans-serif !important; color: #1a1a1a !important; }
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 50%, #e0f2f1 100%);
    background-attachment: fixed; direction: rtl;
}
.stApp { background: transparent; }
.main-box {
    background-color: rgba(255,255,255,0.98); padding: 35px 30px;
    border-radius: 20px; box-shadow: 0 12px 40px rgba(27,94,32,0.15);
    margin-bottom: 60px; backdrop-filter: blur(8px);
    border: 1px solid rgba(46,125,50,0.1);
}
h1, h2, h3, h4, h5, p, span, li, div, label { color: #1a1a1a !important; }

.stButton > button {
    color: #1a1a1a !important;
    background: linear-gradient(135deg, #ffffff, #e8f5e9) !important;
    border: 2px solid #2e7d32 !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 12px 24px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 3px 10px rgba(46,125,50,0.15) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #c8e6c9, #a5d6a7) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(46,125,50,0.3) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1b5e20, #2e7d32) !important;
    color: #ffffff !important;
    border-color: #0d3011 !important;
}
.stButton > button[kind="primary"] * { color: #ffffff !important; }

.stTabs [data-baseweb="tab-list"] {
    gap: 8px; background: rgba(255,255,255,0.5);
    padding: 8px; border-radius: 14px; flex-wrap: wrap;
}
.stTabs [data-baseweb="tab"] {
    background: linear-gradient(135deg, #ffffff, #f5f5f5) !important;
    border-radius: 10px !important;
    padding: 10px 18px !important;
    font-weight: 700 !important;
    border: 2px solid transparent !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9) !important;
    transform: translateY(-2px);
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1b5e20, #2e7d32) !important;
    border-color: #0d3011 !important;
    box-shadow: 0 4px 15px rgba(27,94,32,0.4) !important;
}
.stTabs [aria-selected="true"] * { color: #ffffff !important; }

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select {
    border: 2px solid #c8e6c9 !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    background: #ffffff !important;
}

.streamlit-expanderHeader {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9) !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 12px 18px !important;
    border-right: 5px solid #2e7d32 !important;
}

.metric-card {
    background: linear-gradient(135deg, #ffffff, #f1f8e9);
    padding: 22px 18px; border-radius: 16px;
    box-shadow: 0 6px 20px rgba(27,94,32,0.1);
    text-align: center;
    border-top: 4px solid #2e7d32;
}
.metric-card .number { font-size: 2.2rem; font-weight: 900; color: #1b5e20; }
.metric-card .label { font-size: 0.95rem; color: #555; font-weight: 600; }

.section-title {
    color: #1b5e20 !important;
    border-right: 6px solid #2e7d32;
    padding: 14px 22px; text-align: right;
    font-size: 1.6rem; font-weight: 800;
    margin-top: 35px; margin-bottom: 25px;
    background: linear-gradient(to left, rgba(46,125,50,0.18), rgba(46,125,50,0.02));
    border-radius: 12px;
}
.formula-item {
    background: linear-gradient(135deg, #ffffff, #e8f5e9);
    padding: 16px 22px; border-radius: 14px;
    margin-bottom: 10px; font-weight: 700;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    text-align: right;
}
.oil-item {
    background: linear-gradient(135deg, #fff8e1, #ffe0b2);
    padding: 14px 20px; border-radius: 12px;
    margin-bottom: 8px; font-weight: 700;
    color: #bf360c !important;
    border-right: 5px solid #e65100;
    text-align: right;
}
.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 22px 25px; border-radius: 14px;
    border-right: 5px solid #2e7d32; margin-bottom: 20px;
}
.oil-info-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 18px; border-radius: 12px;
    border-right: 5px solid #e65100;
    margin-bottom: 18px; text-align: right;
}
.profile-img-style {
    width: 150px; height: 150px; border-radius: 50%;
    object-fit: cover; border: 5px solid #d4af37;
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    display: block; margin: 0 auto;
}

.dua-main-box {
    background: linear-gradient(135deg, #0d3011, #1b5e20 25%, #2e7d32 50%, #1b5e20 75%, #0d3011);
    background-size: 200% 200%;
    padding: 30px 25px; border-radius: 22px;
    border: 4px solid #d4af37; text-align: center;
    margin: 25px 0; box-shadow: 0 15px 40px rgba(0,0,0,0.4);
}
.dua-main-box * { color: #ffffff !important; }
.dua-main-box h3 {
    color: #d4af37 !important; font-size: 1.85rem;
    margin-bottom: 18px; font-weight: 900;
}
.dua-main-box .names {
    display: inline-block;
    background: linear-gradient(90deg, rgba(212,175,55,0.15), rgba(212,175,55,0.4), rgba(212,175,55,0.15));
    font-size: 1.55rem; font-weight: 900;
    color: #ffeb3b !important;
    margin: 20px 0; padding: 16px 30px;
    border: 2px solid #d4af37; border-radius: 15px;
    font-family: 'Amiri', serif !important;
}
.dua-main-box p.quran {
    font-family: 'Amiri', serif !important;
    font-size: 1.15rem; color: #d4af37 !important;
    margin-top: 18px; padding: 16px 22px;
    background: rgba(0,0,0,0.25); border-radius: 12px;
    border-right: 5px solid #d4af37;
    border-left: 5px solid #d4af37;
}
.visitor-dua-banner {
    background: linear-gradient(135deg, #fff8e1, #ffecb3, #ffe082);
    padding: 20px 28px; border-radius: 18px;
    border: 3px solid #d4af37; margin: 22px 0;
    text-align: center;
}
.visitor-dua-banner * { color: #4e342e !important; }
.visitor-dua-banner b { color: #c62828 !important; font-family: 'Amiri', serif !important; }

.dua-fixed-banner {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32, #1b5e20, #0d3011);
    background-size: 200% 100%;
    padding: 12px 20px; z-index: 9998; text-align: center;
    border-top: 3px solid #d4af37;
    font-family: 'Amiri', serif !important;
    font-size: 1.1rem; font-weight: bold;
}
.dua-fixed-banner * { color: #ffeb3b !important; font-family: 'Amiri', serif !important; }

.mini-signature {
    position: fixed; left: 20px; bottom: 70px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important; padding: 10px 24px;
    font-size: 0.9rem; border-radius: 25px;
    z-index: 9997; direction: rtl;
    border: 2px solid #d4af37; font-weight: 700;
}
.mini-signature * { color: white !important; }

.alert-critical {
    background: linear-gradient(135deg, #ffebee, #ffcdd2);
    padding: 14px 20px; border-radius: 12px;
    border-right: 5px solid #c62828;
    margin-bottom: 10px; color: #b71c1c !important; font-weight: 700;
}
.alert-warning {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 14px 20px; border-radius: 12px;
    border-right: 5px solid #ef6c00;
    margin-bottom: 10px; color: #e65100 !important; font-weight: 700;
}
.alert-success {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 14px 20px; border-radius: 12px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 10px; color: #1b5e20 !important; font-weight: 700;
}
.prayer-card {
    background: linear-gradient(135deg, #e0f2f1, #b2dfdb);
    padding: 22px; border-radius: 14px;
    border-right: 6px solid #00695c;
    text-align: center; margin-bottom: 15px;
}
.prayer-card .time { font-size: 1.9rem; font-weight: 900; color: #004d40 !important; }

.book-chapter {
    background: linear-gradient(135deg, #1a237e, #283593);
    color: white !important; padding: 15px 20px;
    border-radius: 10px; font-weight: bold; margin-top: 20px;
}
.book-chapter * { color: white !important; }
.book-body {
    padding: 20px 25px; font-size: 1.05rem;
    line-height: 1.8; color: #2c3e50;
    border-left: 4px solid #3498db;
    background: #f8f9fa; border-radius: 0 10px 10px 0;
}

@media (max-width: 768px) {
    .main-box { padding: 20px 15px; }
    .section-title { font-size: 1.3rem; padding: 10px 15px; }
    .dua-main-box .names { font-size: 1.15rem; padding: 12px 18px; }
    .dua-fixed-banner { font-size: 0.85rem; padding: 8px 12px; }
    .mini-signature { font-size: 0.75rem; padding: 8px 16px; }
}
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 24: بوابة الدخول
# ═════════════════════════════════════════════════════════════════════════════

def render_dua_bar():
    st.markdown(f"""
    <div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <p style="font-size:1.1rem; color:#a5d6a7 !important;">نبدأ باسم الله، ونسألُه أن يتقبّلَ هذا العملَ صدقةً جاريةً عن:</p>
        <div class="names">🕊️ رحم الله والدي إسماعيل تاور وأختي ابتسام 🕊️</div>
        <p class="quran">{DUA_QURAN}</p>
        <p class="quran" style="margin-top:10px;">{DUA_VERSE}</p>
    </div>
    """, unsafe_allow_html=True)


if not st.session_state["approved"]:
    render_dua_bar()
    st.markdown('<div class="main-box" style="max-width: 780px; margin: 30px auto; direction: rtl;">', unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 2px solid #d4af37; margin: 25px 0;'>", unsafe_allow_html=True)

    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        if img_base64:
            st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
        else:
            st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)
    with col_title:
        st.markdown(f"<h2 style='color:#2E7D32; text-align:right;'>🌾 {APP_NAME}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.1rem;'>{APP_TAGLINE}</p>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#c62828; text-align:right;'>{SUPERVISOR} — {SUPERVISOR_TITLE}</h4>", unsafe_allow_html=True)

    st.markdown("<hr style='border-top: 2px solid #d4af37; margin: 25px 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#1b5e20;'>🔐 بوابة الدخول</h3>", unsafe_allow_html=True)

    col_audio1, col_audio2, col_audio3 = st.columns(3)
    with col_audio1:
        if st.button("🔊 الشرح الكامل", use_container_width=True):
            play_full_guide_audio()
    with col_audio2:
        if st.button("🎙️ استمع للترحيب", use_container_width=True):
            play_welcome_audio()
    with col_audio3:
        if st.button("🕊️ استمع للدعاء", use_container_width=True):
            play_dua_audio()

    st.markdown("<hr style='border-top: 1px dashed #ccc; margin: 20px 0;'>", unsafe_allow_html=True)

    col_owner, col_guest = st.columns(2)
    with col_owner:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        padding: 20px; border-radius: 12px; border: 2px solid #2e7d32;
        text-align: center; margin-bottom: 10px;">
        <h4 style="color: #1b5e20;">👑 المالك</h4>
        <p style="font-size: 0.9rem; color: #555;">الدخول بكود خاص</p>
        </div>
        """, unsafe_allow_html=True)
        owner_code = st.text_input("🔑 كود المالك:", type="password", key="owner_code")
        if st.button("👑 دخول المالك", type="primary", use_container_width=True):
            if owner_code.strip() == OWNER_CODE:
                st.session_state.update({"approved": True, "user_role": "owner"})
                st.rerun()
            else:
                st.error("❌ كود غير صحيح")

    with col_guest:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fff8e1, #ffecb3);
        padding: 20px; border-radius: 12px; border: 2px solid #d4af37;
        text-align: center; margin-bottom: 10px;">
        <h4 style="color: #e65100;">👥 زائر</h4>
        <p style="font-size: 0.9rem; color: #555;">دخول مجاني</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True):
            st.session_state.update({"approved": True, "user_role": "guest"})
            st.rerun()

    st.markdown("""
    <div style='text-align:center; margin-top:25px; color:#999; font-size:0.85rem;'>
    <p>🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b> - رحمهما الله</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
# القسم 25: الواجهة الرئيسية
# ═════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="main-box">', unsafe_allow_html=True)

c1, c2 = st.columns([0.7, 0.3])
with c2:
    role_label = "المالك 👑" if is_owner() else "زائر 👥"
    st.markdown(f"<div style='text-align:left; padding:10px; background:#f5f5f5; border-radius:10px;'>الحساب: <b>{role_label}</b></div>", unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k != "inventory":
                del st.session_state[k]
        st.session_state["approved"] = False
        st.rerun()

c3, c4 = st.columns([0.3, 0.7])
with c3:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <h1 style='color:#0d3011; text-align:right; margin-bottom:0; font-weight:900; font-size:2.3rem;'>
    🌾 {APP_NAME}
    </h1>
    <p style='color:#1565C0; text-align:right; font-size:1.25rem; font-weight:600; margin-top:8px;'>{APP_TAGLINE}</p>
    <div style='background:linear-gradient(135deg, #fff8e1, #ffe082); padding:12px 20px; border-radius:12px; border-right:6px solid #c62828; border-left:6px solid #c62828; margin-top:10px;'>
        <h3 style='color:#b71c1c; text-align:right; margin:0; font-weight:900; font-size:1.55rem;'>👨‍🔬 {SUPERVISOR}</h3>
        <p style='color:#0d47a1; text-align:right; margin:5px 0 0 0; font-weight:700; font-size:1.15rem;'>✨ {SUPERVISOR_TITLE}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="visitor-dua-banner">{DUA_VISITOR_BANNER}</div>', unsafe_allow_html=True)

# لوحة إحصائية
st.markdown("### 📊 لوحة التحكم السريعة")
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
inv = st.session_state.get("inventory", {})
with col_stat1:
    st.markdown(f"<div class='metric-card'><div class='number'>{len(inv)}</div><div class='label'>إجمالي المواد</div></div>", unsafe_allow_html=True)
with col_stat2:
    total_qty = sum(d["quantity"] if isinstance(d, dict) else d for d in inv.values())
    st.markdown(f"<div class='metric-card'><div class='number'>{total_qty:.0f}</div><div class='label'>إجمالي المخزون (طن)</div></div>", unsafe_allow_html=True)
with col_stat3:
    low = sum(1 for d in inv.values() if (d["quantity"] if isinstance(d, dict) else d) < 5)
    color = "#c62828" if low > 5 else ("#e65100" if low > 0 else "#2e7d32")
    st.markdown(f"<div class='metric-card'><div class='number' style='color:{color};'>{low}</div><div class='label'>مواد منخفضة</div></div>", unsafe_allow_html=True)
with col_stat4:
    st.markdown(f"<div class='metric-card'><div class='number'>{len(st.session_state.get('barns', {}))}</div><div class='label'>حظائر مصممة</div></div>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 26: دوال مساعدة
# ═════════════════════════════════════════════════════════════════════════════

def guide_section(tab_name, guide_text):
    with st.expander(f"📘 دليل استخدام {tab_name}", expanded=False):
        st.markdown(
            f'<div style="background:#f0f8ff; padding:15px; '
            f'border-radius:10px; direction:rtl; text-align:right; '
            f'font-family:Tajawal, Cairo, sans-serif; line-height:1.8;">'
            f'{guide_text}</div>',
            unsafe_allow_html=True)


def generate_formula_image(formula_data, target_dp, target_se, breed,
                             stage, user_name):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.set_facecolor('#f5f5f5')
        fig.patch.set_facecolor('#ffffff')
        title_text = (f"خلطة علفية - {APP_NAME}\n"
                      f"المشرف: {user_name}\n"
                      f"الفصيل: {breed} | DP: {target_dp:.1f}% | "
                      f"SE: {target_se:.1f}")
        ax.set_title(title_text, fontsize=14, fontweight='bold', pad=25)
        ingredients = list(formula_data.keys())
        kg_per_ton = [p * 10 for p in formula_data.values()]
        y_pos = np.arange(len(ingredients))
        ax.barh(y_pos, kg_per_ton, color='#2e7d32', alpha=0.8,
                edgecolor='#1b5e20', linewidth=1.5)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(ingredients, fontsize=11)
        ax.set_xlabel('الكمية (كجم/طن)', fontsize=12, fontweight='bold')
        for i, v in enumerate(kg_per_ton):
            ax.text(v + 3, i, f'{v:.1f} كجم', va='center', fontsize=10,
                    fontweight='bold', color='#1b5e20')
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=200, bbox_inches='tight',
                    facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


# ═════════════════════════════════════════════════════════════════════════════
# القسم 27: معمل تحليل الخلطات العلفية (النسخة المحسّنة الشاملة)
# ═════════════════════════════════════════════════════════════════════════════

def render_feed_analysis_lab():
    """معمل تحليل الخلطات العلفية — 5 تبويبات فرعية شاملة"""
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0d47a1,#1565c0);
                padding:25px; border-radius:18px; text-align:center;
                margin-bottom:20px; box-shadow:0 8px 30px rgba(13,71,161,0.4);">
        <h2 style="color:white; margin:0; font-size:1.9rem;">
        🧪 معمل تحليل الخلطات العلفية
        </h2>
        <p style="color:#bbdefb; margin-top:10px; font-size:1.05rem;">
        نظام Weende + Van Soest + الطاقة + الأحماض الأمينية + مقارنة NRC
        </p>
    </div>
    """, unsafe_allow_html=True)

    # المدخلات الأساسية
    st.markdown("### 📋 إعدادات التحليل")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        analysis_animal = st.selectbox(
            "🐾 نوع الحيوان:",
            list(FEED_ANALYSIS_REFERENCE.keys()),
            key="analysis_animal_v20")
    with col2:
        purposes = list(FEED_ANALYSIS_REFERENCE.get(analysis_animal, {}).keys())
        analysis_purpose = st.selectbox("🎯 الغرض:", purposes,
                                          key="analysis_purpose_v20")
    with col3:
        analysis_weight = st.number_input("⚖️ الوزن (كجم):",
                                            1.0, 900.0, 500.0, 5.0,
                                            key="analysis_weight_v20")
    with col4:
        analysis_milk = 20.0
        if analysis_animal in ["أبقار", "أغنام", "ماعز"]:
            analysis_milk = st.number_input("🥛 إنتاج الحليب (كجم):",
                                              0.0, 60.0, 20.0, 1.0,
                                              key="analysis_milk_v20")

    st.markdown("---")
    st.markdown("### 🌾 إدخال مكونات الخلطة (كجم)")
    st.caption("أدخل وزن كل مكوّن — اترك الصفر للمكونات غير المستخدمة.")

    # إدخال المكونات في 4 أعمدة
    formula_input = {}
    all_feed_items = list(FLAT_FEED_DB.keys())
    cols_input = st.columns(4)
    for idx, feed_name in enumerate(all_feed_items):
        with cols_input[idx % 4]:
            w = st.number_input(
                feed_name, min_value=0.0, value=0.0, step=1.0,
                key=f"lab_input_v20_{feed_name}")
            if w > 0:
                formula_input[feed_name] = w

    if not formula_input:
        st.info("💡 أدخل أوزان المكونات أعلاه ثم اضغط 'تشغيل التحليل'.")
        return

    total_weight = sum(formula_input.values())
    formula_pct = {k: (v / total_weight) * 100.0
                   for k, v in formula_input.items()}

    st.success(f"✅ إجمالي وزن الخلطة: **{total_weight:.1f} كجم** "
               f"| عدد المكونات: **{len(formula_input)}**")

    # تنفيذ التحليل
    proximate = compute_proximate_analysis(formula_pct)
    energy = compute_energy_values(proximate, analysis_animal)
    amino = predict_amino_acids(formula_pct, analysis_animal)
    reference = FEED_ANALYSIS_REFERENCE.get(analysis_animal, {}).get(
        analysis_purpose, {})
    performance = predict_performance(proximate, energy, analysis_animal,
                                        analysis_weight, analysis_milk)
    recommendations = generate_ai_recommendations(
        proximate, energy, amino, analysis_animal, None, reference)

    # التبويبات الفرعية
    sub_tabs = st.tabs([
        "📊 Weende", "🌿 Van Soest", "⚡ الطاقة",
        "🧬 الأحماض الأمينية", "📈 الأداء", "🧠 التوصيات"])

    # ═══ Weende ═══
    with sub_tabs[0]:
        st.markdown("### 📊 التحليل التقريبي (Weende)")
        st.caption("النظام الكلاسيكي لتقسيم مكونات العلف إلى 6 مجموعات.")
        weende_data = [
            ("الرطوبة", proximate["الرطوبة"], "%", "#1565c0",
             "Moisture — تجفيف 105°م"),
            ("المادة الجافة (DM)", proximate["المادة الجافة (DM)"], "%", "#2e7d32",
             "Dry Matter = 100 - الرطوبة"),
            ("البروتين الخام (CP)", proximate["البروتين الخام (CP)"], "%", "#c62828",
             "Crude Protein = N × 6.25"),
            ("الدهن الخام (EE)", proximate["الدهن الخام (EE)"], "%", "#e65100",
             "Ether Extract — استخلاص بالأثير"),
            ("الألياف الخام (CF)", proximate["الألياف الخام (CF)"], "%", "#6a1b9a",
             "Crude Fiber — الهضم الحمضي/القاعدي"),
            ("الرماد (Ash)", proximate["الرماد (Ash)"], "%", "#795548",
             "حرق عند 550°م"),
            ("الكربوهيدرات الذائبة (NFE)", proximate["الكربوهيدرات الذائبة (NFE)"], "%", "#00897b",
             "Nitrogen-Free Extract = DM - CP - EE - CF - Ash"),
        ]
        cols_w = st.columns(3)
        for i, (name, val, unit, color, desc) in enumerate(weende_data):
            with cols_w[i % 3]:
                st.markdown(
                    f'<div style="background:white; padding:16px; '
                    f'border-radius:14px; border-right:5px solid {color}; '
                    f'margin-bottom:10px; direction:rtl; text-align:right; '
                    f'box-shadow:0 3px 12px rgba(0,0,0,0.06);">'
                    f'<b style="color:{color}; font-size:0.95rem;">{name}</b>'
                    f'<div style="font-size:1.8rem; font-weight:900; '
                    f'color:{color}; margin:6px 0;">{val:.2f}{unit}</div>'
                    f'<small style="color:#888; font-size:0.75rem;">'
                    f'{desc}</small></div>',
                    unsafe_allow_html=True)

        # جدول المقارنة
        if reference:
            st.markdown("### 📏 المقارنة مع المعيار")
            compare_rows = []
            for key_ref, key_actual in [
                ("CP", "البروتين الخام (CP)"),
                ("EE", "الدهن الخام (EE)"),
                ("NDF", "NDF"), ("ADF", "ADF"),
                ("ASH", "الرماد (Ash)")]:
                if key_ref in reference:
                    actual_val = proximate.get(key_actual, 0)
                    diff = actual_val - reference[key_ref]
                    pct = (diff / reference[key_ref] * 100) if reference[key_ref] else 0
                    grade = "✅" if abs(pct) <= 5 else ("⚠️" if abs(pct) <= 10 else "❌")
                    compare_rows.append({
                        "العنصر": key_ref,
                        "المعيار": f"{reference[key_ref]:.2f}",
                        "المحسوب": f"{actual_val:.2f}",
                        "الفرق": f"{diff:+.2f}",
                        "% الفرق": f"{pct:+.1f}%",
                        "التقييم": grade})
            if compare_rows:
                st.dataframe(pd.DataFrame(compare_rows),
                             use_container_width=True, hide_index=True)

    # ═══ Van Soest ═══
    with sub_tabs[1]:
        st.markdown("### 🌿 تحليل الألياف (Van Soest)")
        st.caption("نظام Van Soest لفصل الألياف إلى مكوناتها.")
        vs_data = [
            ("NDF", proximate["NDF"], "%", "#558b2f",
             "Neutral Detergent Fiber — الألياف المتعادلة"),
            ("ADF", proximate["ADF"], "%", "#33691e",
             "Acid Detergent Fiber — الألياف الحمضية"),
            ("ADL", proximate["ADL"], "%", "#6d4c41",
             "Acid Detergent Lignin — الليغنين"),
            ("السيليلوز", proximate["السيليلوز"], "%", "#8d6e63",
             "Cellulose = ADF - ADL"),
            ("الهيميسيليلوز", proximate["الهيميسيليلوز"], "%", "#2e7d32",
             "Hemicellulose = NDF - ADF"),
        ]
        cols_v = st.columns(3)
        for i, (name, val, unit, color, desc) in enumerate(vs_data):
            with cols_v[i % 3]:
                st.markdown(
                    f'<div style="background:white; padding:16px; '
                    f'border-radius:14px; border-right:5px solid {color}; '
                    f'margin-bottom:10px; direction:rtl; text-align:right;">'
                    f'<b style="color:{color};">{name}</b>'
                    f'<div style="font-size:1.8rem; font-weight:900; '
                    f'color:{color};">{val:.2f}{unit}</div>'
                    f'<small style="color:#888;">{desc}</small></div>',
                    unsafe_allow_html=True)

        # تفسير القيم
        st.markdown("### 📖 تفسير القيم")
        st.markdown(f"""
        - **NDF ({proximate['NDF']:.1f}%)**: يُقدّر استهلاك المادة الجافة
        - **ADF ({proximate['ADF']:.1f}%)**: يُقدّر هضم المادة الجافة
        - **ADL ({proximate['ADL']:.1f}%)**: الليغنين غير مهضوم
        - **السيليلوز ({proximate['السيليلوز']:.1f}%)**: مصدر طاقة مهم
        - **الهيميسيليلوز ({proximate['الهيميسيليلوز']:.1f}%)**: سريع الهضم
        """)

    # ═══ الطاقة ═══
    with sub_tabs[2]:
        st.markdown("### ⚡ تحليل الطاقة المتقدم")
        st.caption("حساب قيم الطاقة وفق معادلات NRC و INRA.")
        e_cols = st.columns(3)
        with e_cols[0]:
            st.metric("TDN", f"{energy['TDN %']:.2f}%",
                       help="إجمالي المواد المهضومة")
        with e_cols[1]:
            st.metric("DE", f"{energy['DE (Mcal/kg)']:.3f}",
                       help="الطاقة المهضومة (Mcal/kg)")
        with e_cols[2]:
            st.metric("ME", f"{energy['ME (Mcal/kg)']:.3f}",
                       help="الطاقة الممثلة (Mcal/kg)")
        e_cols2 = st.columns(3)
        with e_cols2[0]:
            st.metric("NE-lactation",
                       f"{energy['NE_lactation (Mcal/kg)']:.3f}",
                       help="الطاقة الصافية للحليب")
        with e_cols2[1]:
            st.metric("NE-gain",
                       f"{energy['NE_gain (Mcal/kg)']:.3f}",
                       help="الطاقة الصافية للنمو")
        with e_cols2[2]:
            st.metric("NE-maintenance",
                       f"{energy['NE_maintenance (Mcal/kg)']:.3f}",
                       help="الطاقة الصافية للصيانة")

        st.markdown("### 📊 المعايير المرجعية")
        if reference and "TDN" in reference:
            diff_tdn = energy['TDN %'] - reference['TDN']
            pct_tdn = diff_tdn / reference['TDN'] * 100 if reference['TDN'] else 0
            color = "#2e7d32" if abs(pct_tdn) <= 5 else ("#f9a825" if abs(pct_tdn) <= 10 else "#c62828")
            st.markdown(
                f'<div style="background:#e8f5e9; padding:16px; '
                f'border-radius:12px; border-right:5px solid {color}; '
                f'direction:rtl;">'
                f'<b>TDN المعيار:</b> {reference["TDN"]}% | '
                f'<b>المحسوب:</b> {energy["TDN %"]:.2f}% | '
                f'<b>الفرق:</b> {pct_tdn:+.1f}%</div>',
                unsafe_allow_html=True)

    # ═══ الأحماض الأمينية ═══
    with sub_tabs[3]:
        st.markdown("### 🧬 الأحماض الأمينية الأساسية")
        st.caption("تقدير الأحماض الأمينية من محتوى البروتين.")
        aa_cols = st.columns(4)
        for i, (name, val) in enumerate(amino.items()):
            with aa_cols[i % 4]:
                st.markdown(
                    f'<div style="background:linear-gradient(135deg, #f3e5f5, #e1bee7); '
                    f'padding:14px; border-radius:12px; '
                    f'border-right:5px solid #7b1fa2; direction:rtl; '
                    f'text-align:right; margin-bottom:8px;">'
                    f'<b style="color:#4a148c;">{name}</b>'
                    f'<div style="font-size:1.5rem; font-weight:900; '
                    f'color:#6a1b9a;">{val:.3f}%</div></div>',
                    unsafe_allow_html=True)

    # ═══ الأداء ═══
    with sub_tabs[4]:
        st.markdown("### 📈 توقعات الأداء الإنتاجي")
        st.caption("توقعات مبنية على محتوى الطاقة والبروتين.")
        for k, v in performance.items():
            st.markdown(
                f'<div style="background:linear-gradient(135deg,#e8f5e9,#c8e6c9);'
                f'padding:14px 20px; border-radius:12px; '
                f'margin-bottom:8px; border-right:5px solid #2e7d32; '
                f'direction:rtl; display:flex; justify-content:space-between;">'
                f'<b style="color:#1b5e20;">{k}</b>'
                f'<span style="font-size:1.3rem; color:#1b5e20; '
                f'font-weight:900;">'
                f'{v if isinstance(v, str) else f"{v:.2f}"}</span></div>',
                unsafe_allow_html=True)

    # ═══ التوصيات ═══
    with sub_tabs[5]:
        st.markdown("### 🧠 توصيات الذكاء الاصطناعي")
        if not recommendations:
            st.success("🎯 التركيبة متوازنة تماماً!")
        else:
            for rec in recommendations:
                if rec["type"] == "success":
                    bg, br = "#e8f5e9", "#2e7d32"
                elif rec["type"] == "warning":
                    bg, br = "#fff3e0", "#e65100"
                else:
                    bg, br = "#e3f2fd", "#1976d2"
                st.markdown(
                    f'<div style="background:{bg}; padding:15px 20px; '
                    f'border-radius:12px; margin-bottom:10px; '
                    f'border-right:5px solid {br}; direction:rtl;">'
                    f'<b style="font-size:1.05rem;">{rec["title"]}</b>'
                    f'<p style="margin-top:6px;">{rec["text"]}</p></div>',
                    unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 28: مصمم الحظائر العلمي
# ═════════════════════════════════════════════════════════════════════════════

def render_barn_designer():
    """مصمم الحظائر وفق المعايير العالمية"""
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1b5e20,#2e7d32);
                padding:25px; border-radius:18px; text-align:center;
                margin-bottom:20px; box-shadow:0 8px 30px rgba(27,94,32,0.4);">
        <h2 style="color:white; margin:0; font-size:1.9rem;">
        🏗️ مصمم الحظائر العلمي
        </h2>
        <p style="color:#c8e6c9; margin-top:10px; font-size:1.05rem;">
        وفق المعايير العالمية (NRC, FAO, EFSA, INRA)
        </p>
    </div>
    """, unsafe_allow_html=True)

    # المدخلات
    col1, col2, col3 = st.columns(3)
    with col1:
        barn_animal = st.selectbox("🐾 نوع الحيوان:",
            list(BARN_STANDARDS.keys()), key="barn_animal_v20")
    with col2:
        barn_purpose = st.selectbox(
            "🎯 الغرض من التربية:",
            ["إنتاج حليب", "تسمين", "تربية أمهات", "بيض",
             "نمو", "سباق", "استعراض"],
            key="barn_purpose_v20")
    with col3:
        barn_count = st.number_input(
            "🔢 عدد الحيوانات:", min_value=1, max_value=10000,
            value=50, step=1, key="barn_count_v20")

    col4, col5 = st.columns(2)
    with col4:
        barn_age = st.selectbox(
            "📅 الفئة العمرية:",
            ["صغار (0-6 أشهر)", "نامي (6-18 شهر)", "بالغ (18+ شهر)"],
            key="barn_age_v20")
    with col5:
        barn_climate = st.selectbox(
            "🌡️ المناخ:",
            ["حار جاف", "حار رطب", "معتدل", "بارد"],
            key="barn_climate_v20")

    std = BARN_STANDARDS.get(barn_animal, {})

    if std:
        st.markdown("---")
        st.markdown("### 📋 المعايير الأساسية الموصى بها")

        # بطاقات المعايير
        info_cols = st.columns(4)
        sp = std.get("space_per_head_m2", 0)
        with info_cols[0]:
            st.markdown(
                f'<div style="background:white; padding:16px; '
                f'border-radius:12px; border-top:4px solid #2e7d32; '
                f'text-align:center; direction:rtl;">'
                f'<b>المساحة/رأس</b><br>'
                f'<span style="font-size:1.5rem; color:#1b5e20;">'
                f'{sp} م²</span></div>',
                unsafe_allow_html=True)
        with info_cols[1]:
            h = std.get("height_m", 0)
            st.markdown(
                f'<div style="background:white; padding:16px; '
                f'border-radius:12px; border-top:4px solid #1565c0; '
                f'text-align:center; direction:rtl;">'
                f'<b>الارتفاع</b><br>'
                f'<span style="font-size:1.5rem; color:#1565c0;">'
                f'{h} م</span></div>',
                unsafe_allow_html=True)
        with info_cols[2]:
            v = std.get("ventilation_m3_h", 0)
            st.markdown(
                f'<div style="background:white; padding:16px; '
                f'border-radius:12px; border-top:4px solid #e65100; '
                f'text-align:center; direction:rtl;">'
                f'<b>التهوية/ساعة</b><br>'
                f'<span style="font-size:1.5rem; color:#e65100;">'
                f'{v} م³</span></div>',
                unsafe_allow_html=True)
        with info_cols[3]:
            f = std.get("feeding_space_cm", 0)
            st.markdown(
                f'<div style="background:white; padding:16px; '
                f'border-radius:12px; border-top:4px solid #6a1b9a; '
                f'text-align:center; direction:rtl;">'
                f'<b>مساحة المعلف/رأس</b><br>'
                f'<span style="font-size:1.5rem; color:#6a1b9a;">'
                f'{f} سم</span></div>',
                unsafe_allow_html=True)

        # الحسابات
        st.markdown("### 📐 الحسابات المقترحة")
        total_area = sp * barn_count
        total_with_service = total_area * 1.20

        # الأبعاد
        if barn_animal in ["دواجن_لاحم", "دواجن_بياض", "سمان"]:
            width = std.get("house_width_m", 8.0)
        elif barn_animal == "أسماك":
            width = 10.0
        else:
            width = 12.0
        length = total_with_service / width if width > 0 else 0

        dim_cols = st.columns(4)
        with dim_cols[0]:
            st.metric("المساحة الكلية", f"{total_area:.1f} م²")
        with dim_cols[1]:
            st.metric("مع الخدمات (+20%)", f"{total_with_service:.1f} م²")
        with dim_cols[2]:
            st.metric("العرض المقترح", f"{width:.1f} م")
        with dim_cols[3]:
            st.metric("الطول المقترح", f"{length:.1f} م")

        # التهوية
        ventilation_total = v * barn_count
        air_space = std.get("air_space_m3", 0) * barn_count
        st.markdown("### 🌬️ نظام التهوية")
        vent_cols = st.columns(3)
        with vent_cols[0]:
            st.metric("التهوية الكلية/ساعة", f"{ventilation_total:,.0f} م³")
        with vent_cols[1]:
            st.metric("حجم الهواء الداخلي", f"{air_space:,.0f} م³")
        with vent_cols[2]:
            vent_type = "طبيعية + مراوح"
            if barn_animal == "أسماك":
                vent_type = "مضخات أكسجين"
            st.metric("نوع التهوية", vent_type)

        # الارتفاع
        st.markdown("### 🏠 الارتفاع والسقف")
        ht_cols = st.columns(3)
        with ht_cols[0]:
            st.metric("ارتفاع الجدار", f"{std.get('height_m', 0)} م")
        with ht_cols[1]:
            st.metric("ارتفاع القمة", f"{std.get('ridge_height_m', 0)} م")
        with ht_cols[2]:
            slope = ((std.get('ridge_height_m', 0) - std.get('height_m', 0)) /
                     (width/2) * 100) if width > 0 else 0
            st.metric("ميل السقف", f"{slope:.0f}%")

        # المخطط
        if MATPLOTLIB_AVAILABLE:
            st.markdown("### 🗺️ المخطط المقترح")
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.set_xlim(0, length + 2)
            ax.set_ylim(0, width + 2)
            ax.set_aspect('equal')
            ax.set_facecolor('#f5f5f5')

            # الجدران
            ax.add_patch(Rectangle((0, 0), length, width,
                                    fill=False, edgecolor='#1b5e20',
                                    linewidth=3))

            # الممرات حسب النوع
            if barn_animal in ["أبقار_حلابة", "أبقار_تسمين", "خيول", "إبل"]:
                alley = std.get("feeding_alley_m", 4.0)
                ax.add_patch(Rectangle((0.5, width/2 - alley/2),
                                        length - 1, alley,
                                        fill=True, facecolor='#fff9c4',
                                        edgecolor='#f9a825', linewidth=1.5))
                ax.text(length/2, width/2, "ممر التغذية",
                        ha='center', va='center', fontsize=10,
                        fontweight='bold', color='#e65100')
                # معالف على الجانبين
                ax.add_patch(Rectangle((0.5, width/2 + alley/2),
                                        length - 1, 0.8,
                                        fill=True, facecolor='#ffccbc',
                                        edgecolor='#e65100', linewidth=1.5))
                ax.text(length/2, width/2 + alley/2 + 0.4, "معالف",
                        ha='center', va='center', fontsize=9,
                        fontweight='bold', color='#bf360c')
                ax.add_patch(Rectangle((0.5, width/2 - alley/2 - 0.8),
                                        length - 1, 0.8,
                                        fill=True, facecolor='#ffccbc',
                                        edgecolor='#e65100', linewidth=1.5))
                ax.text(length/2, width/2 - alley/2 - 0.4, "معالف",
                        ha='center', va='center', fontsize=9,
                        fontweight='bold', color='#bf360c')
            elif barn_animal in ["دواجن_لاحم", "دواجن_بياض", "سمان"]:
                # معالف دائرية
                for ix in range(3):
                    for iy in range(2):
                        x = (ix + 1) * length / 4
                        y = (iy + 1) * width / 3
                        circle = plt.Circle((x, y), 0.5,
                                             facecolor='#ffccbc',
                                             edgecolor='#e65100',
                                             linewidth=1.5)
                        ax.add_patch(circle)
                        ax.text(x, y, "معلف", ha='center', va='center',
                                fontsize=7, fontweight='bold',
                                color='#bf360c')
                # سقايات على الجوانب
                ax.add_patch(Rectangle((0.5, 0.5), length - 1, 0.5,
                                        fill=True, facecolor='#b3e5fc',
                                        edgecolor='#0288d1', linewidth=1.5))
                ax.text(length/2, 0.75, "سقايات", ha='center', va='center',
                        fontsize=8, fontweight='bold', color='#01579b')
            else:
                # معالف وسقايات على الحدود
                ax.add_patch(Rectangle((0.5, 0.5), length - 1, 0.6,
                                        fill=True, facecolor='#ffccbc',
                                        edgecolor='#e65100', linewidth=1.5))
                ax.text(length/2, 0.8, "معالف", ha='center', va='center',
                        fontsize=9, fontweight='bold', color='#bf360c')
                ax.add_patch(Rectangle((0.5, width - 1.1), length - 1, 0.6,
                                        fill=True, facecolor='#b3e5fc',
                                        edgecolor='#0288d1', linewidth=1.5))
                ax.text(length/2, width - 0.8, "سقايات",
                        ha='center', va='center', fontsize=9,
                        fontweight='bold', color='#01579b')

            # سقاية إضافية للأبقار/الخيول/الإبل
            if barn_animal in ["أبقار_حلابة", "أبقار_تسمين", "خيول", "إبل"]:
                ax.add_patch(Circle((length - 1.5, width/2), 0.4,
                                     facecolor='#b3e5fc',
                                     edgecolor='#0288d1', linewidth=1.5))
                ax.text(length - 1.5, width/2, "سقاية",
                        ha='center', va='center', fontsize=8,
                        fontweight='bold', color='#01579b')

            ax.set_title(f"مخطط حظيرة {barn_animal} — {barn_count} حيوان",
                         fontsize=13, fontweight='bold', color='#1b5e20',
                         pad=15)
            ax.set_xlabel("الطول (م)", fontsize=10)
            ax.set_ylabel("العرض (م)", fontsize=10)
            ax.grid(True, alpha=0.2)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

        # التوصيات
        st.markdown("### 📌 التوصيات الفنية")
        st.markdown(
            f'<div style="background:#e8f5e9; padding:18px; '
            f'border-radius:12px; border-right:5px solid #2e7d32; '
            f'direction:rtl; line-height:1.9;">'
            f'<b>✅ المساحة:</b> {sp} م² لكل رأس × {barn_count} = '
            f'{total_area:.1f} م²<br>'
            f'<b>✅ التهوية:</b> {ventilation_total:,.0f} م³/ساعة — '
            f'فتحات بمساحة {total_with_service * 0.05:.1f} م² على الأقل<br>'
            f'<b>✅ المعلف:</b> {std.get("feeding_space_cm", 0)} سم لكل رأس '
            f'— الإجمالي {std.get("feeding_space_cm", 0) * barn_count / 100:.1f} متر طولي<br>'
            f'<b>✅ السقاية:</b> {std.get("water_space_cm", 0)} سم لكل رأس '
            f'— الإجمالي {std.get("water_space_cm", 0) * barn_count / 100:.1f} متر طولي<br>'
            f'<b>✅ درجة الحرارة:</b> {std.get("temp_range", "غير محدد")}<br>'
            f'<b>✅ الرطوبة:</b> أقصى {std.get("humidity_max", "70%")}<br>'
            f'<b>📖 المرجع:</b> {std.get("source", "NRC")}</div>',
            unsafe_allow_html=True)

        # ملاحظات
        st.markdown("### ⚠️ ملاحظات مهمة")
        warnings = []
        if barn_climate == "حار رطب":
            warnings.append("في المناخ الحار الرطب، زد التهوية 30% "
                            "وقلل الكثافة 15%.")
        if barn_age.startswith("صغار"):
            warnings.append("الصغار يحتاجون حرارة أعلى (32-34°م) "
                            "وتهوية تدريجية.")
        if barn_animal == "أسماك":
            warnings.append("يجب تركيب مضخات أكسجين وفلاتر "
                            "ميكانيكية وبيولوجية.")
        if not warnings:
            warnings.append("الظروف مناسبة — اتبع المعايير الموصى بها.")
        for w in warnings:
            st.markdown(
                f'<div style="background:#fff3e0; padding:12px 18px; '
                f'border-radius:10px; margin-bottom:8px; '
                f'border-right:5px solid #ef6c00; direction:rtl;">'
                f'⚠️ {w}</div>',
                unsafe_allow_html=True)

        # حفظ الحظيرة
        st.markdown("---")
        col_save1, col_save2 = st.columns([3, 1])
        with col_save1:
            barn_name = st.text_input("📝 اسم الحظيرة للحفظ:",
                                       placeholder="مثال: حظيرة أبقار الحليب - مزرعة الأمل")
        with col_save2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 حفظ الحظيرة", use_container_width=True,
                         key="save_barn_v20"):
                if barn_name:
                    if "barns" not in st.session_state:
                        st.session_state["barns"] = {}
                    st.session_state["barns"][barn_name] = {
                        "animal": barn_animal, "purpose": barn_purpose,
                        "count": barn_count, "area_m2": total_area,
                        "length_m": length, "width_m": width,
                        "height_m": std.get("height_m", 0),
                        "ventilation_m3_h": ventilation_total,
                        "date": datetime.now().isoformat()}
                    st.success(f"✅ تم حفظ حظيرة {barn_name}")
                else:
                    st.warning("⚠️ أدخل اسم الحظيرة")

        # عرض الحظائر المحفوظة
        if st.session_state.get("barns"):
            st.markdown("### 📚 الحظائر المحفوظة")
            barn_rows = []
            for name, data in st.session_state["barns"].items():
                barn_rows.append({
                    "الاسم": name,
                    "الحيوان": data["animal"],
                    "الغرض": data["purpose"],
                    "العدد": data["count"],
                    "المساحة": f"{data['area_m2']:.1f} م²",
                    "الأبعاد": f"{data['length_m']:.1f}×{data['width_m']:.1f} م"})
            st.dataframe(pd.DataFrame(barn_rows),
                         use_container_width=True, hide_index=True)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 29: دوال التبويبات الأخرى
# ═════════════════════════════════════════════════════════════════════════════

def render_ai_advisor():
    st.markdown("### 🧠 المستشار الذكي — تشخيص المشاكل")
    st.info("اكتب وصفاً للمشكلة وسيقدم النظام توصيات مبنية على قواعد علمية.")
    problem = st.text_area("🔍 وصف المشكلة:",
        placeholder="مثال: عندي بقرة قلة الحليب وضعف الشهية",
        height=100, key="ai_problem_v20")
    if st.button("🧠 تحليل المشكلة", type="primary",
                 use_container_width=True, key="run_advisor_v20"):
        if not problem.strip():
            st.warning("⚠️ يرجى وصف المشكلة أولاً")
        else:
            result = SmartFeedAdvisor.advise(problem)
            if result["found"]:
                for match in result["matches"]:
                    st.markdown(
                        f'<div style="background:linear-gradient(135deg, '
                        f'#fff3e0, #ffe0b2); padding:18px; '
                        f'border-radius:14px; margin-bottom:15px; '
                        f'border-right:5px solid #e65100; direction:rtl;">'
                        f'<h3 style="color:#bf360c;">🎯 {match["issue"]}</h3>'
                        f'<h4>🔍 الأسباب المحتملة:</h4>'
                        f'<ul>{"".join(f"<li>{c}</li>" for c in match["causes"])}</ul>'
                        f'<h4>✅ الحلول المقترحة:</h4>'
                        f'<ol>{"".join(f"<li>{s}</li>" for s in match["solutions"])}</ol>'
                        f'</div>',
                        unsafe_allow_html=True)
            else:
                st.info("ℹ️ " + " | ".join(result["suggestions"]))


def render_prayer_times():
    st.markdown('<div class="section-title">🕌 مواقيت الصلاة</div>',
                unsafe_allow_html=True)
    st.info("🕌 مواقيت تقريبية للاسترشاد — يُفضل التحقق من المسجد المحلي.")
    cities = ["مكة المكرمة", "المدينة المنورة", "الخرطوم", "طرابلس",
              "القاهرة", "دبي", "الرياض", "صنعاء", "عمان", "بيروت",
              "دمشق", "بغداد", "الكويت", "مسقط", "المنامة", "الدوحة", "أبوظبي"]
    city = st.selectbox("📍 اختر المدينة:", cities, key="prayer_city_v20")
    prayer_times = {
        "مكة المكرمة": {"الفجر": "05:00", "الشروق": "06:30",
                        "الظهر": "12:15", "العصر": "15:30",
                        "المغرب": "18:10", "العشاء": "19:30"},
        "الخرطوم": {"الفجر": "04:50", "الشروق": "06:00",
                    "الظهر": "12:00", "العصر": "15:20",
                    "المغرب": "18:20", "العشاء": "19:40"},
        "طرابلس": {"الفجر": "05:30", "الشروق": "07:00",
                   "الظهر": "13:00", "العصر": "16:30",
                   "المغرب": "19:00", "العشاء": "20:30"},
        "القاهرة": {"الفجر": "05:00", "الشروق": "06:30",
                    "الظهر": "12:30", "العصر": "16:00",
                    "المغرب": "18:50", "العشاء": "20:20"}}
    default_times = {"الفجر": "05:00", "الشروق": "06:30",
                     "الظهر": "12:00", "العصر": "15:30",
                     "المغرب": "18:00", "العشاء": "19:30"}
    times = prayer_times.get(city, default_times)
    st.markdown(f"### 📍 مواقيت الصلاة في {city}")
    cols = st.columns(3)
    for i, (name, t) in enumerate(times.items()):
        with cols[i % 3]:
            st.markdown(
                f'<div class="prayer-card">'
                f'<div style="font-size:1.2rem; color:#004d40; '
                f'font-weight:700;">🕐 {name}</div>'
                f'<div class="time">{t}</div></div>',
                unsafe_allow_html=True)


def render_dose_reminders():
    st.markdown('<div class="section-title">💊 نظام منبه الجرعات</div>',
                unsafe_allow_html=True)
    if "dose_reminders" not in st.session_state:
        st.session_state["dose_reminders"] = []
    reminders = st.session_state["dose_reminders"]
    with st.expander("➕ إضافة جرعة جديدة", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            animal = st.selectbox("🐾 نوع الحيوان:",
                ["أبقار", "أغنام", "ماعز", "خيول", "إبل", "دواجن", "أسماك"],
                key="dr_animal_v20")
            dtype = st.selectbox("💉 نوع الجرعة:",
                ["لقاح", "فيتامين", "دواء", "مضاد طفيليات", "هرمون"],
                key="dr_type_v20")
            dname = st.text_input("📝 اسم الجرعة:", key="dr_name_v20")
        with c2:
            dose = st.number_input("الجرعة:", 0.0, 1000.0, 1.0, 0.1,
                                     key="dr_dose_v20")
            unit = st.selectbox("الوحدة:", ["مل", "جم", "مجم", "قطرة"],
                                 key="dr_unit_v20")
            route = st.selectbox("الطريقة:",
                ["عضل", "تحت الجلد", "فموي", "مياه الشرب", "رش"],
                key="dr_route_v20")
        with c3:
            freq = st.number_input("التكرار (أيام):", 1, 365, 7, 1,
                                     key="dr_freq_v20")
            start = st.date_input("📅 تاريخ البدء:", datetime.now(),
                                    key="dr_start_v20")
            notes = st.text_area("ملاحظات:", key="dr_notes_v20", height=80)
        if st.button("💾 حفظ الجرعة", use_container_width=True,
                     key="dr_save_v20"):
            if not dname:
                st.error("⚠️ أدخل اسم الجرعة")
            else:
                reminders.append({
                    "id": secrets.token_hex(6), "animal": animal,
                    "type": dtype, "name": dname, "dose": dose,
                    "unit": unit, "route": route, "freq": freq,
                    "start": start.isoformat(),
                    "next": (start + timedelta(days=freq)).isoformat(),
                    "notes": notes, "active": True})
                st.success(f"✅ تم إضافة {dname}")
                st.rerun()
    if reminders:
        st.markdown("### 📋 الجرعات المسجلة")
        today = datetime.now().date()
        for r in reminders:
            next_date = datetime.fromisoformat(r["next"]).date()
            days_left = (next_date - today).days
            badge = "🔴" if days_left < 0 else ("🟡" if days_left == 0
                else ("🟠" if days_left <= 3 else "🟢"))
            with st.expander(f"{badge} 💊 {r['name']} — {r['animal']}"):
                cc1, cc2, cc3 = st.columns(3)
                cc1.metric("النوع", r["type"])
                cc2.metric("الجرعة", f"{r['dose']} {r['unit']}")
                cc3.metric("التكرار", f"كل {r['freq']} يوم")
                st.write(f"**الطريقة:** {r['route']}")
                st.write(f"**القادمة:** {r['next'][:10]} ({days_left} يوم)")
    else:
        st.info("📭 لا توجد جرعات مسجلة.")


def render_daily_production():
    st.markdown('<div class="section-title">📈 الإنتاج اليومي</div>',
                unsafe_allow_html=True)
    if "daily_production_log" not in st.session_state:
        st.session_state["daily_production_log"] = []
    with st.form("daily_prod_form_v20", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            farm = st.text_input("🏠 المزرعة:")
            ddate = st.date_input("📅 التاريخ:", datetime.now())
        with c2:
            milk = st.number_input("🥛 الحليب (لتر):", 0.0, 100000.0, 0.0, 1.0)
            eggs = st.number_input("🥚 البيض (عدد):", 0, 1000000, 0, 1)
        with c3:
            wgain = st.number_input("⚖️ زيادة الوزن (كجم):",
                                     0.0, 10000.0, 0.0, 0.5)
            mort = st.number_input("💀 النافق:", 0, 100000, 0, 1)
        notes = st.text_area("📝 ملاحظات:")
        if st.form_submit_button("💾 حفظ اليوم",
                                   use_container_width=True):
            st.session_state["daily_production_log"].append({
                "farm": farm, "date": ddate.isoformat(), "milk": milk,
                "eggs": eggs, "weight_gain": wgain,
                "mortality": mort, "notes": notes})
            st.success("✅ تم الحفظ")
            st.rerun()
    if st.session_state["daily_production_log"]:
        st.markdown("### 📋 السجل اليومي")
        st.dataframe(pd.DataFrame(st.session_state["daily_production_log"]),
                     use_container_width=True, hide_index=True)


def render_alerts():
    st.markdown('<div class="section-title">🔔 التنبيهات</div>',
                unsafe_allow_html=True)
    inv = st.session_state.get("inventory", {})
    alerts = []
    for name, d in inv.items():
        q = d["quantity"] if isinstance(d, dict) else d
        thr = d.get("min_threshold", 5.0) if isinstance(d, dict) else 5.0
        if q <= 0:
            alerts.append((name, "نفذ المخزون", "critical"))
        elif q < thr:
            alerts.append((name, f"منخفض ({q:.1f} طن < {thr})", "warning"))
    if alerts:
        st.markdown(f"### ⚠️ {len(alerts)} تنبيه نشط")
        for name, msg, level in alerts:
            cls = "alert-critical" if level == "critical" else "alert-warning"
            icon = "🔴" if level == "critical" else "🟡"
            st.markdown(f'<div class="{cls}">{icon} <b>{name}:</b> {msg}</div>',
                        unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-success">✅ لا توجد تنبيهات</div>',
                    unsafe_allow_html=True)


def render_send_code():
    st.markdown('<div class="section-title">📧 إرسال السورس كود</div>',
                unsafe_allow_html=True)
    st.info(f"🔒 خاص بالمالك: {SUPERVISOR}")
    st.warning(f"📮 البريد الوحيد المسموح: **{OWNER_EMAIL}**")
    email_in = st.text_input("📧 البريد المستلم:", value=OWNER_EMAIL,
                              key="send_code_email_v20")
    if st.button("📤 إرسال الكود الآن", type="primary",
                 use_container_width=True, key="send_code_btn_v20"):
        if email_in.strip().lower() != OWNER_EMAIL.lower():
            st.error("❌ الإرسال مسموح فقط لبريد المالك")
        else:
            st.warning("⚠️ تحتاج إعداد App Password في secrets.toml")
            st.code("""
# .streamlit/secrets.toml
[email]
password = "your_gmail_app_password"
            """, language="toml")


def render_deployment_guide():
    st.markdown('<div class="section-title">🚀 دليل النشر على '
                'Streamlit Cloud</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:linear-gradient(135deg, #e3f2fd, #bbdefb);
                padding:25px; border-radius:16px;
                border-right:5px solid #1565c0; margin-bottom:20px;
                direction:rtl;">
        <h3>📋 نظرة عامة</h3>
        <p>سيمكنك نشر المنصة على الإنترنت مجاناً عبر Streamlit Cloud.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📌 الخطوة 1: التحضير المحلي", expanded=True):
        st.markdown("""
        **1. ثبّت المكتبات:**
        ```bash
        pip install streamlit numpy pandas scipy scikit-learn \\
                    plotly matplotlib gtts pytesseract \\
                    opencv-python-headless openpyxl reportlab \\
                    arabic-reshaper python-bidi qrcode Pillow
        ```
        **2. اختبر المنصة:**
        ```bash
        streamlit run tawornology_v20.py
        ```
        """)
    with st.expander("📌 الخطوة 2: requirements.txt"):
        st.code("""streamlit>=1.28.0
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.11.0
scikit-learn>=1.3.0
plotly>=5.17.0
matplotlib>=3.7.0
gtts>=2.4.0
pytesseract>=0.3.10
opencv-python-headless>=4.8.0
openpyxl>=3.1.0
reportlab>=4.0.0
arabic-reshaper>=3.0.0
python-bidi>=0.4.2
qrcode>=7.4.2
Pillow>=10.0.0""", language="text")
    with st.expander("📌 الخطوة 3: GitHub"):
        st.markdown("""
        ```bash
        git init
        git add .
        git commit -m "Tawor Nology v20"
        git branch -M main
        git remote add origin https://github.com/USERNAME/tawornology.git
        git push -u origin main
        ```
        """)
    with st.expander("📌 الخطوة 4: Streamlit Cloud"):
        st.markdown("""
        1. اذهب إلى [share.streamlit.io](https://share.streamlit.io)
        2. سجل بحساب GitHub
        3. اضغط "New app"
        4. اختر Repository و Branch = main
        5. Main file = `tawornology_v20.py`
        6. اضغط "Deploy"
        """)
    with st.expander("📌 الخطوة 5: Secrets"):
        st.code("""[email]
password = "your_gmail_app_password"

[general]
owner_email = "abukram128@gmail.com" """, language="toml")
    with st.expander("📌 الخطوة 6: Gmail App Password"):
        st.markdown("""
        1. [myaccount.google.com](https://myaccount.google.com)
        2. Security → 2-Step Verification → **فعّلها**
        3. Security → App passwords
        4. أنشئ كلمة مرور جديدة
        5. انسخها والصقها في Secrets
        """)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 30: قائمة التبويبات
# ═════════════════════════════════════════════════════════════════════════════

if is_owner():
    tabs_titles = [
        "🔬 تركيب الأعلاف",       # 0
        "🧪 معمل التحليل",         # 1
        "🏗️ مصمم الحظائر",        # 2 ✨ جديد
        "🌰 مكتبة الزيوت",         # 3
        "🍼 بدائل الحليب",         # 4
        "📷 المختبر الذكي",         # 5
        "🔬 المختبر المتقدم",       # 6
        "🕌 مواقيت الصلاة",         # 7
        "💊 منبه الجرعات",          # 8
        "📈 الإنتاج اليومي",        # 9
        "🔔 التنبيهات",            # 10
        "📊 البورصة",              # 11
        "🏭 المستودعات",           # 12
        "🧾 الفواتير",             # 13
        "🖨️ الديباجة",            # 14
        "📈 التحليلات",            # 15
        "🐔 مزارع الدجاج",         # 16
        "💬 التعليقات",            # 17
        "📚 المراجع",              # 18
        "💡 المساعدة",             # 19
        "📖 الدليل",               # 20
        "🚀 دليل النشر",           # 21
        "📧 إرسال الكود",           # 22
    ]
else:
    tabs_titles = [
        "🔬 تركيب الأعلاف",
        "🧪 معمل التحليل",
        "🏗️ مصمم الحظائر",
        "🌰 مكتبة الزيوت",
        "🍼 بدائل الحليب",
        "📷 المختبر الذكي",
        "🕌 مواقيت الصلاة",
        "📚 المراجع",
        "💡 المساعدة",
        "📖 الدليل",
    ]

tabs = st.tabs(tabs_titles)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 31: تبويب 0 — تركيب الأعلاف
# ═════════════════════════════════════════════════════════════════════════════

with tabs[0]:
    guide_section("تركيب الأعلاف",
                   "اختر الدولة، ثم الحيوان، وحدد حالته الفسيولوجية، "
                   "وفعّل ✅ الاعتماد، ثم اختر المكونات وشغّل المحرك.")

    st.markdown('<div class="section-title">🌍 الموقع الجغرافي</div>',
                unsafe_allow_html=True)
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        country = st.selectbox("🌍 الدولة:",
                                 list(EXCHANGE_RATES.keys()),
                                 key="country_v20")
    with cc2:
        state = st.text_input("🗺️ الولاية:", "الخرطوم", key="state_v20")
    with cc3:
        city = st.text_input("🏙️ المدينة:", "الخرطوم", key="city_v20")
    rate = EXCHANGE_RATES.get(country, {"rate": 1.0, "sym": "USD"})
    local_rate, local_sym = rate["rate"], rate["sym"]
    live_prices = get_market_prices(country, city, state)

    st.markdown('<div class="section-title">🧬 أساس حساب البروتين</div>',
                unsafe_allow_html=True)
    protein_basis_choice = st.radio("اختر أساس الحساب:",
        ["البروتين المهضوم (DP) — الأدق علمياً",
         "البروتين الخام (CP) — الأسهل ميدانياً"],
        horizontal=True, key="protein_basis_v20")
    use_dp = "DP" in protein_basis_choice
    if use_dp:
        st.success("🎯 تستخدم الآن **DP** — الأدق علمياً")
    else:
        st.info("📊 تستخدم الآن **CP** — الأسهل ميدانياً")

    st.markdown('<div class="section-title">🐾 اختر الحيوان والحالة '
                'الفسيولوجية</div>', unsafe_allow_html=True)
    animal_tabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐪 إبل",
                            "🐎 خيول", "🐔 دواجن", "🦆 سمان", "🐟 أسماك"])

    animal_choice = None
    requirement = None
    img_key = "عام"
    std_key_global = ""

    with animal_tabs[0]:
        st.markdown("### 🐄 احتياجات الأبقار — NRC 2001")
        cattle_type = st.selectbox("الحالة الفسيولوجية:",
            ["حليب_عالي", "حليب_متوسط", "حليب_منخفض",
             "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"],
            format_func=lambda x: {
                "حليب_عالي": "🐄 حلابة عالية",
                "حليب_متوسط": "🐄 حلابة متوسطة",
                "حليب_منخفض": "🐄 حلابة منخفضة",
                "تسمين_مكثف": "💪 تسمين مكثف",
                "تسمين_عادي": "💪 تسمين عادي",
                "حمل_أخير": "🤰 حمل آخر",
                "صيانة": "🌿 صيانة"}.get(x, x),
            key="cattle_type_v20")
        c1_, c2_ = st.columns(2)
        cattle_params = {}
        with c1_:
            if "حليب" in cattle_type:
                cattle_params["milk_yield"] = st.number_input(
                    "🥛 إنتاج الحليب (كجم):", 5.0, 60.0, 20.0, 1.0,
                    key="cattle_milk_v20")
            cattle_params["weight_kg"] = st.number_input(
                "⚖️ الوزن (كجم):", 200.0, 900.0, 500.0, 25.0,
                key="cattle_wt_v20")
        with c2_:
            req_pre = get_cattle_requirements(cattle_type, **cattle_params)
            st.metric("🧬 DP", f"{req_pre.DP}%")
            st.metric("🧬 CP", f"{req_pre.CP}%")
            st.metric("🌽 SE", f"{req_pre.SE}")
        if st.checkbox("✅ اعتماد الأبقار", key="use_cattle_v20"):
            animal_choice = "أبقار"
            requirement = req_pre
            img_key = "أبقار"
            std_key_global = f"أبقار_{cattle_type}"

    with animal_tabs[1]:
        st.markdown("### 🐏 احتياجات الأغنام — NRC 2007")
        sg = st.radio("الجنس:", ["ذكر (تسمين)", "أنثى (أمهات)"],
                       horizontal=True, key="sheep_gender_v20")
        is_male_s = "ذكر" in sg
        litter = 1
        if is_male_s:
            sheep_type = st.selectbox("الحالة:",
                ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد"],
                format_func=lambda x: {
                    "تسمين_مكثف": "💪 مكثف", "تسمين_عادي": "💪 عادي",
                    "حملان_تيد": "🐑 تيد"}.get(x, x), key="sheep_t_m_v20")
        else:
            sheep_type = st.selectbox("الحالة:",
                ["مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
                format_func=lambda x: {
                    "مرضعات": "🍼 مرضعات", "حامل_أخير": "🤰 حامل 4-5",
                    "حامل_متوسط": "🤰 حامل 1-3",
                    "صيانة": "🌿 صيانة"}.get(x, x), key="sheep_t_f_v20")
            if sheep_type == "مرضعات":
                litter = st.number_input("👶 عدد المواليد:", 1, 3, 1, 1,
                                          key="sheep_litter_v20")
        weight_s = st.number_input("⚖️ الوزن (كجم):", 15.0, 120.0, 50.0,
                                     5.0, key="sheep_wt_v20")
        req_pre = get_sheep_requirements(sheep_type, is_male=is_male_s,
                                          weight_kg=weight_s,
                                          litter_size=litter)
        p1, p2, p3 = st.columns(3)
        p1.metric("🧬 DP", f"{req_pre.DP}%")
        p2.metric("🧬 CP", f"{req_pre.CP}%")
        p3.metric("🌽 SE", f"{req_pre.SE}")
        if st.checkbox("✅ اعتماد الأغنام", key="use_sheep_v20"):
            animal_choice = "أغنام"
            requirement = req_pre
            img_key = "أغنام"
            std_key_global = f"أغنام_{sheep_type}"

    with animal_tabs[2]:
        st.markdown("### 🐐 احتياجات الماعز — NRC 2007")
        gg = st.radio("الجنس:", ["ذكر (تسمين)", "أنثى (حلابة)"],
                       horizontal=True, key="goat_gender_v20")
        is_male_g = "ذكر" in gg
        milk_g = 0
        if is_male_g:
            goat_type = st.selectbox("الحالة:",
                ["تسمين_جديان", "تيوس"],
                format_func=lambda x: {"تسمين_جديان": "💪 جديان",
                                        "تيوس": "🐐 تيوس"}.get(x, x),
                key="goat_t_m_v20")
        else:
            goat_type = st.selectbox("الحالة:",
                ["حلابة_عالي", "حلابة_متوسط", "حامل_أخير", "صيانة"],
                format_func=lambda x: {"حلابة_عالي": "🍼 عالي",
                                        "حلابة_متوسط": "🍼 متوسط",
                                        "حامل_أخير": "🤰 حامل",
                                        "صيانة": "🌿 صيانة"}.get(x, x),
                key="goat_t_f_v20")
            if "حلابة" in goat_type:
                milk_g = st.number_input("🥛 إنتاج الحليب (كجم):",
                                           0.5, 8.0, 2.0, 0.25,
                                           key="goat_milk_v20")
        req_pre = get_goat_requirements(goat_type, is_male=is_male_g,
                                          milk_yield=milk_g)
        p1, p2, p3 = st.columns(3)
        p1.metric("🧬 DP", f"{req_pre.DP}%")
        p2.metric("🧬 CP", f"{req_pre.CP}%")
        p3.metric("🌽 SE", f"{req_pre.SE}")
        if st.checkbox("✅ اعتماد الماعز", key="use_goat_v20"):
            animal_choice = "ماعز"
            requirement = req_pre
            img_key = "ماعز"
            std_key_global = f"ماعز_{goat_type}"

    with animal_tabs[3]:
        st.markdown("### 🐪 احتياجات الإبل — FAO 2010")
        camel_type = st.selectbox("الحالة:",
            ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
            format_func=lambda x: {"نمو": "🐪 نمو", "تسمين": "💪 تسمين",
                                    "حليب": "🍼 حلابة", "سباق": "🏃 سباق",
                                    "صيانة": "🌿 صيانة"}.get(x, x),
            key="camel_type_v20")
        camel_wt = st.number_input("⚖️ الوزن (كجم):", 100.0, 800.0,
                                     400.0, 25.0, key="camel_wt_v20")
        camel_milk = 5.0
        if camel_type == "حليب":
            camel_milk = st.number_input("🥛 إنتاج الحليب (لتر):",
                                           2.0, 20.0, 5.0, 0.5,
                                           key="camel_milk_v20")
        req_pre = get_camel_requirements(camel_type, weight_kg=camel_wt,
                                           milk_yield=camel_milk)
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("🧬 DP", f"{req_pre.DP}%")
        p2.metric("🧬 CP", f"{req_pre.CP}%")
        p3.metric("🌽 SE", f"{req_pre.SE}")
        p4.metric("🌾 NDF", f"{req_pre.NDF}%")
        if st.checkbox("✅ اعتماد الإبل", key="use_camel_v20"):
            animal_choice = "إبل"
            requirement = req_pre
            img_key = "إبل"
            std_key_global = f"إبل_{camel_type}"

    with animal_tabs[4]:
        st.markdown("### 🐎 احتياجات الخيول — NRC 2007")
        horse_type = st.selectbox("الحالة:",
            ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار", "مرضعات", "صيانة"],
            format_func=lambda x: {"رياضة_مكثف": "🏇 مكثف",
                                    "رياضة_عادي": "🏇 عادي",
                                    "نمو_أمهار": "🐎 نمو",
                                    "مرضعات": "🍼 مرضعات",
                                    "صيانة": "🌿 صيانة"}.get(x, x),
            key="horse_type_v20")
        horse_wt = st.number_input("⚖️ الوزن (كجم):", 200.0, 800.0,
                                     450.0, 25.0, key="horse_wt_v20")
        req_pre = get_horse_requirements(horse_type, weight_kg=horse_wt)
        p1, p2, p3 = st.columns(3)
        p1.metric("🧬 DP", f"{req_pre.DP}%")
        p2.metric("🧬 CP", f"{req_pre.CP}%")
        p3.metric("🌽 SE", f"{req_pre.SE}")
        if st.checkbox("✅ اعتماد الخيول", key="use_horse_v20"):
            animal_choice = "خيول"
            requirement = req_pre
            img_key = "خيول"
            std_key_global = f"خيول_{horse_type}"

    with animal_tabs[5]:
        st.markdown("### 🐔 احتياجات الدواجن — Ross 308")
        poultry_strain = st.radio("السلالة:", ["لاحم", "بياض"],
                                    horizontal=True,
                                    key="poultry_strain_v20")
        poultry_age = st.number_input("العمر (أسبوع):", 1, 20, 1, 1,
                                        key="poultry_age_v20")
        req_pre = get_poultry_requirements(poultry_strain, poultry_age)
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("🧬 DP", f"{req_pre.DP}%")
        p2.metric("🧬 CP", f"{req_pre.CP}%")
        p3.metric("🌽 SE", f"{req_pre.SE}")
        p4.metric("Ca", f"{req_pre.Ca}%")
        if st.checkbox("✅ اعتماد الدواجن", key="use_poultry_v20"):
            animal_choice = "دواجن"
            requirement = req_pre
            img_key = "دواجن"
            if poultry_strain == "لاحم":
                std_key_global = ("دواجن_بادي" if poultry_age <= 1
                    else ("دواجن_نامي" if poultry_age <= 3 else "دواجن_ناهي"))
            else:
                std_key_global = "دواجن_بياض"

    with animal_tabs[6]:
        st.markdown("### 🦆 احتياجات السمان")
        quail_strain = st.radio("النوع:", ["تسمين", "بياض"],
                                  horizontal=True, key="quail_strain_v20")
        quail_age = st.number_input("العمر (أسبوع):", 1, 8, 1, 1,
                                      key="quail_age_v20")
        req_pre = get_quail_requirements(quail_strain, quail_age)
        p1, p2, p3 = st.columns(3)
        p1.metric("🧬 DP", f"{req_pre.DP}%")
        p2.metric("🧬 CP", f"{req_pre.CP}%")
        p3.metric("🌽 SE", f"{req_pre.SE}")
        if st.checkbox("✅ اعتماد السمان", key="use_quail_v20"):
            animal_choice = "سمان"
            requirement = req_pre
            img_key = "سمان"
            std_key_global = f"سمان_{quail_strain}"

    with animal_tabs[7]:
        st.markdown("### 🐟 احتياجات الأسماك")
        fish_species = st.selectbox("النوع:",
            ["البلطي النيلي", "القرموط الأفريقي", "الكارب"],
            key="fish_sp_v20")
        fish_stage = st.selectbox("المرحلة:",
            ["بادئ زريعة", "نمو", "تسمين"], key="fish_stage_v20")
        req_pre = get_fish_requirements(fish_species, fish_stage)
        p1, p2, p3 = st.columns(3)
        p1.metric("🧬 DP", f"{req_pre.DP}%")
        p2.metric("🧬 CP", f"{req_pre.CP}%")
        p3.metric("🌽 SE", f"{req_pre.SE}")
        if st.checkbox("✅ اعتماد الأسماك", key="use_fish_v20"):
            animal_choice = "أسماك"
            requirement = req_pre
            img_key = "أسماك"
            if "زريعة" in fish_stage or "بادئ" in fish_stage:
                std_key_global = "أسماك_بادئ"
            elif "نمو" in fish_stage:
                std_key_global = "أسماك_نمو"
            else:
                std_key_global = "أسماك_تسمين"

    if not animal_choice or not requirement:
        st.warning("⚠️ اختر حيواناً، وفعّل خيار ✅ الاعتماد للمتابعة")
        st.stop()

    st.markdown(f'<div class="section-title">🎯 المختار: {animal_choice} '
                f'— {requirement.name_ar}</div>', unsafe_allow_html=True)
    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
    info_col1.metric("🧬 DP", f"{requirement.DP}%")
    info_col2.metric("🧬 CP", f"{requirement.CP}%")
    info_col3.metric("🌽 SE", f"{requirement.SE}")
    info_col4.metric("🌾 NDF", f"{requirement.NDF}%")
    st.info(f"📝 {requirement.note}")

    oil_std_info = get_oil_standard(std_key_global)
    st.markdown('<div class="section-title">🌰 معيار الزيوت لهذا '
                'الحيوان</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="oil-info-card">'
        f'<b>📊 الحدود القياسية للزيوت:</b><br>'
        f'▪️ الحد الأقصى: <b>{oil_std_info["max"]}%</b><br>'
        f'▪️ النسبة المثالية: <b>{oil_std_info["optimal"]}%</b><br>'
        f'▪️ المرجع: <b>{oil_std_info["source"]}</b></div>',
        unsafe_allow_html=True)

    requester_name = st.text_input("👤 اسم طالب العلفة:",
        placeholder="مثال: مزرعة الأمل — أحمد محمد", key="requester_v20")

    st.markdown('<div class="section-title">🌾 اختيار المكونات</div>',
                unsafe_allow_html=True)
    selected_ingredients = []
    ingredient_prices = {}

    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        expanded = ("الحبوب" in cat_name or "الأكساب" in cat_name
                    or "الزيوت" in cat_name)
        with st.expander(f"📁 {cat_name}", expanded=expanded):
            sub = st.columns(3)
            for i, (ing_name, ing_data) in enumerate(items.items()):
                with sub[i % 3]:
                    default_check = ing_name in [
                        "ملح الطعام", "الحجر الجيري (بودرة بلاط)",
                        "فوسفات ثنائي الكالسيوم (DCP)", "مضاد سموم فطرية"]
                    if animal_choice in ["أغنام", "ماعز", "أبقار", "إبل"]:
                        default_check = default_check or (
                            ing_name == "بيكربونات الصوديوم")
                    if animal_choice in ["دواجن", "سمان"]:
                        default_check = default_check or ("بريمكس" in ing_name)

                    if cat_name == "🌰 الزيوت النباتية والحيوانية":
                        st.markdown(f"**{ing_name}**")
                        st.caption(f"⚡ SE={ing_data.get('SE', 0):.0f} | EE=100%")
                        checked = st.checkbox("إضافة", value=False,
                            key=f"ck_{animal_choice}_{ing_name}_v20")
                    else:
                        checked = st.checkbox(ing_name, value=default_check,
                            key=f"ck_{animal_choice}_{ing_name}_v20")

                    price = live_prices.get(ing_name, 300.0)
                    if is_owner():
                        price = st.number_input("$", min_value=5.0,
                            value=float(price),
                            key=f"p_{animal_choice}_{ing_name}_v20",
                            label_visibility="collapsed")
                    else:
                        st.caption(f"💰 ${price:.0f}/طن")

                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price

    st.markdown("---")

    if st.button("🚀 تشغيل المحرك الذكي", type="primary",
                 use_container_width=True, key="run_smart_v20"):
        if len(selected_ingredients) < 3:
            st.error("⚠️ اختر 3 مكونات على الأقل")
        else:
            auto_salts = auto_add_salts_and_minerals(animal_choice,
                                                       requirement)
            for sname, spct in auto_salts.items():
                if sname not in selected_ingredients:
                    selected_ingredients.append(sname)
                    ingredient_prices[sname] = live_prices.get(sname, 300.0)

            custom_standard = requirement_to_standard(requirement)
            basis_label = "DP" if use_dp else "CP"

            with st.spinner(f"⏳ جاري التركيب على أساس {basis_label}..."):
                result = auto_formulate_smart(
                    selected_ingredients, ingredient_prices,
                    custom_standard, standard_key=std_key_global,
                    tolerance=0.3, max_iterations=50)

            if result["success"]:
                formula = result["formula"]
                actual = result["actual_nutrients"]
                cost = result["cost"]
                total_oil = result.get("total_oil", 0.0)
                oil_std = result.get("oil_std", oil_std_info)

                compare_rows = []
                compare_scores = []
                labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم",
                    "SE": "معادل النشاء", "NDF": "NDF", "ADF": "ADF",
                    "EE": "دهن", "ASH": "رماد", "Ca": "كالسيوم",
                    "P": "فسفور"}

                for k, sv in custom_standard.items():
                    cv = actual.get(k, 0.0)
                    diff = cv - sv
                    pct = (diff / sv * 100) if sv else 0
                    ev = evaluate_difference(pct)
                    compare_scores.append({"score": ev["score"]})
                    compare_rows.append({"العنصر": labels.get(k, k),
                        "المعيار": f"{sv:.2f}",
                        "المحسوب": f"{cv:.2f}",
                        "الفرق": f"{diff:+.3f}",
                        "الفرق %": f"{pct:+.2f}%",
                        "التقييم": ev["label"]})

                overall = get_overall_rating(compare_scores)
                perfect = result.get("perfect_match", False)

                if perfect:
                    st.success(f"🎯 **مطابقة كاملة!** — أساس {basis_label}")
                else:
                    st.success(f"✅ تم التركيب — أساس {basis_label}")
                st.info(f"🔁 التكرارات: {result['iterations']} | "
                        f"التقييم: **{overall['label']}** "
                        f"({overall['score']:.0f}%)")

                e1, e2, e3, e4 = st.columns(4)
                e1.metric("خطأ DP", f"{result['dp_error']:.3f}%")
                e2.metric("خطأ SE", f"{result['se_error']:.3f}")
                e3.metric("خطأ NDF", f"{result['ndf_error']:.2f}%")
                e4.metric("خطأ Ca", f"{result['ca_error']:.3f}%")

                st.markdown("### 📊 جدول المقارنة الشامل")
                st.dataframe(pd.DataFrame(compare_rows),
                             use_container_width=True, hide_index=True)

                st.markdown("### 🌰 تقييم الزيوت")
                if total_oil > 0:
                    if total_oil > oil_std["max"]:
                        st.error(f"⚠️ **تجاوز الحد الأقصى!** "
                                 f"{total_oil:.2f}% > {oil_std['max']}%")
                    elif total_oil > oil_std["optimal"] * 1.2:
                        st.warning(f"⚡ مرتفع قليلاً ({total_oil:.2f}%)")
                    else:
                        st.success(f"✅ مطابق — {total_oil:.2f}%")
                else:
                    st.info("ℹ️ لم تستخدم أي زيوت")

                st.markdown("#### 🌾 المكونات:")
                for ing, pct in formula.items():
                    st.markdown(
                        f'<div class="formula-item">▪️ <b>{ing}:</b> '
                        f'{pct:.2f}% ({pct*10:.1f} كجم/طن)</div>',
                        unsafe_allow_html=True)

                st.metric("💰 التكلفة الفعلية للطن:",
                          f"${cost:.2f} ({cost*local_rate:,.0f} {local_sym})")

                st.session_state["active_formula"] = formula
                st.session_state["computed_ton_cost"] = cost
                st.session_state["active_animal_img"] = ANIMAL_IMAGES.get(
                    img_key, ANIMAL_IMAGES["عام"])
                st.session_state["active_stage_title"] = (
                    f"{animal_choice} — {requirement.name_ar}")

                # تحميل التقارير
                st.markdown("### 📥 تحميل التقارير")
                dl1, dl2 = st.columns(2)
                with dl1:
                    try:
                        pdf = pdf_gen.generate_report(
                            formula=formula, requirement=requirement,
                            animal_type=animal_choice,
                            breed=requirement.name_ar, cost=cost,
                            city=city, local_cost=cost * local_rate,
                            local_sym=local_sym,
                            requester_name=requester_name,
                            protein_basis=basis_label,
                            standard_key=std_key_global,
                            include_charts=True)
                        fname = (f"TaworNology_{animal_choice}_"
                                 f"{datetime.now():%Y%m%d_%H%M}.pdf")
                        st.download_button("📥 تحميل PDF", pdf,
                            file_name=fname, mime="application/pdf",
                            use_container_width=True)
                    except Exception as e:
                        st.error(f"⚠️ خطأ PDF: {e}")
                with dl2:
                    try:
                        xl = export_comparison_to_excel(
                            custom_standard, actual, requester_name,
                            animal_choice, requirement.name_ar,
                            formula, std_key_global)
                        if xl:
                            fname = (f"TaworNology_{animal_choice}_"
                                     f"{datetime.now():%Y%m%d_%H%M}.xlsx")
                            st.download_button("📊 تحميل Excel", xl,
                                file_name=fname,
                                mime="application/vnd.openxmlformats-"
                                     "officedocument.spreadsheetml.sheet",
                                use_container_width=True)
                    except Exception as e:
                        st.error(f"⚠️ خطأ Excel: {e}")

                col_act1, col_act2, col_act3 = st.columns(3)
                with col_act1:
                    if st.button("🔬 إرسال لمعمل التحليل",
                                 use_container_width=True,
                                 key="send_to_lab_v20"):
                        st.session_state["lab_sample"] = {
                            'animal': animal_choice,
                            'breed': requirement.name_ar,
                            'formula': formula}
                        st.success("✅ تم الإرسال — اذهب لتبويب معمل التحليل")
                with col_act2:
                    if st.button("📲 مشاركة كصورة",
                                 use_container_width=True,
                                 key="share_v20"):
                        img_buf = generate_formula_image(
                            formula, actual['DP'], actual['SE'],
                            requirement.name_ar, requirement.name_ar,
                            st.session_state.get("user", {}).get(
                                "full_name", "مستخدم"))
                        if img_buf:
                            st.image(img_buf)
                with col_act3:
                    if st.button("🔊 تقرير صوتي", use_container_width=True,
                                 key="voice_report_v20"):
                        generate_voice_report(formula, actual, requirement,
                            animal_choice, cost, requester_name)

                if PLOTLY_AVAILABLE and len(formula) > 1:
                    try:
                        fig = px.pie(values=list(formula.values()),
                                     names=list(formula.keys()),
                                     title=f"توزيع المكونات — {animal_choice}",
                                     color_discrete_sequence=px.colors.sequential.Greens)
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass
            else:
                st.error(f"❌ {result['message']}")


# ═════════════════════════════════════════════════════════════════════════════
# القسم 32: تبويب 1 — معمل التحليل
# ═════════════════════════════════════════════════════════════════════════════

with tabs[1]:
    guide_section("معمل التحليل",
                   "تحليل شامل للتركيبات وفق Weende و Van Soest + "
                   "الطاقة + الأحماض الأمينية + مقارنة NRC.")
    render_feed_analysis_lab()


# ═════════════════════════════════════════════════════════════════════════════
# القسم 33: تبويب 2 — مصمم الحظائر
# ═════════════════════════════════════════════════════════════════════════════

with tabs[2]:
    guide_section("مصمم الحظائر",
                   "تصميم حظائر وفق المعايير العالمية مع حسابات "
                   "المساحة والتهوية والارتفاع ومواضع المعالف والسقايات.")
    render_barn_designer()


# ═════════════════════════════════════════════════════════════════════════════
# القسم 34: تبويب 3 — مكتبة الزيوت
# ═════════════════════════════════════════════════════════════════════════════

with tabs[3]:
    st.markdown('<div class="section-title">🌰 مكتبة الزيوت النباتية '
                'والحيوانية</div>', unsafe_allow_html=True)
    st.write("جميع الزيوت المعتمدة وفق المعايير العالمية.")

    st.markdown("### 📊 الحدود القياسية للزيوت")
    oil_std_rows = [{"الحيوان/الحالة": k,
                     "الحد الأقصى %": f"{v['max']}%",
                     "المثالي %": f"{v['optimal']}%",
                     "المرجع": v["source"]}
                    for k, v in MAX_OIL_PERCENTAGE.items()]
    st.dataframe(pd.DataFrame(oil_std_rows),
                 use_container_width=True, hide_index=True)

    st.markdown("### 🌰 الزيوت المتوفرة")
    oils = get_oil_ingredients()
    for category, oil_list in OIL_CATEGORIES.items():
        st.markdown(f"#### {category}")
        for ing_name in oil_list:
            if ing_name in oils:
                ing_data = oils[ing_name]
                with st.expander(f"🌰 {ing_name}"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("معادل النشاء",
                                  f"{ing_data.get('SE', 0):.0f}")
                        st.metric("الدهن", "100%")
                    with c2:
                        st.metric("طاقة تقديرية",
                                  f"{ing_data.get('SE', 0) * 41:.0f} kcal/kg")
                    with c3:
                        st.metric("أقصى للدواجن",
                                  f"{ing_data.get('max_poultry', 'N/A')}%")
                        st.metric("أقصى للمجترات",
                                  f"{ing_data.get('max_ruminant', 'N/A')}%")
                    st.info(f"📝 {ing_data.get('desc', '')}")


# ═════════════════════════════════════════════════════════════════════════════
# القسم 35: تبويب 4 — بدائل الحليب
# ═════════════════════════════════════════════════════════════════════════════

with tabs[4]:
    st.markdown('<div class="section-title">🍼 مختبر بدائل الحليب</div>',
                unsafe_allow_html=True)
    mr1, mr2 = st.columns(2)
    with mr1:
        mr_animal = st.selectbox("نوع الحيوان:",
                                   list(MILK_REPLACER_STANDARDS.keys()),
                                   key="mr_a_v20")
        mr_volume = st.number_input("الكمية (كجم):", 1.0, 10000.0, 100.0,
                                      10.0, key="mr_v_v20")
    with mr2:
        std_mr = MILK_REPLACER_STANDARDS[mr_animal]
        st.markdown(
            f'<div class="price-card">'
            f'<b>📊 المعيار — {mr_animal}:</b><br>'
            f'▪️ بروتين: <b>{std_mr["CP"]}%</b><br>'
            f'▪️ دهن: <b>{std_mr["Fat"]}%</b><br>'
            f'▪️ لاكتوز: <b>{std_mr["Lactose"]}%</b></div>',
            unsafe_allow_html=True)
    mr_selected = []
    mr_cols = st.columns(3)
    for i, (name, data) in enumerate(MILK_REPLACER_INGREDIENTS.items()):
        with mr_cols[i % 3]:
            default_mr = name in ["حليب مجفف منزوع الدسم",
                "حليب مجفف كامل الدسم", "شرش حليب مجفف",
                "زيت جوز الهند", "زيت النخيل", "بريمكس فيتامينات",
                "كالسيوم كربونات", "فوسفات ثنائي الكالسيوم", "ملح طعام"]
            if st.checkbox(f"{name} — ${data['price']}",
                            value=default_mr, key=f"mr_{name}_v20"):
                mr_selected.append(name)
    if st.button("🧪 تشغيل التركيب", type="primary",
                 use_container_width=True, key="mr_run_v20"):
        if len(mr_selected) < 3:
            st.warning("⚠️ اختر 3 مكونات على الأقل")
        else:
            r = formulate_milk_replacer(mr_animal, mr_volume, mr_selected)
            if r["success"]:
                st.success(f"✅ تم التركيب لـ ({mr_animal})")
                for ing, pct in r["formula"].items():
                    kg = pct * mr_volume / 100.0
                    st.markdown(
                        f'<div class="formula-item">▪️ <b>{ing}:</b> '
                        f'{pct:.2f}% ({kg:.2f} كجم)</div>',
                        unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                m1.metric("💰 التكلفة لـ 100 كجم:",
                          f"${r['cost_per_100kg']:.2f}")
                m2.metric("💰 التكلفة لكل كجم:",
                          f"${r['cost_per_kg']:.3f}")
            else:
                st.error(f"❌ {r['message']}")


# ═════════════════════════════════════════════════════════════════════════════
# القسم 36: تبويب 5 — المختبر الذكي OCR
# ═════════════════════════════════════════════════════════════════════════════

with tabs[5]:
    guide_section("المختبر الذكي",
                   "ارفع صورة تركيبة علفية لاستخراج البيانات تلقائياً.")
    st.markdown('<div class="section-title">📷 المختبر الذكي (OCR)</div>',
                unsafe_allow_html=True)
    if not OCR_AVAILABLE:
        st.warning("⚠️ مكتبة pytesseract غير مثبتة")
    else:
        uploaded = st.file_uploader("📤 ارفع صورة:",
                                     type=["jpg", "jpeg", "png"],
                                     key="smart_upload_v20")
        if uploaded:
            st.image(uploaded, caption="الصورة المرفوعة",
                     use_container_width=True)
            if st.button("🔍 تحليل", type="primary",
                         use_container_width=True, key="smart_analyze_v20"):
                with st.spinner("جاري التحليل..."):
                    r = extract_ingredients_from_image(uploaded.read())
                if r["success"]:
                    st.success(f"✅ تم استخراج {r['count']} مادة")
                    if r["ingredients"]:
                        st.dataframe(pd.DataFrame([
                            {"المادة": k, "النسبة": f"{v:.2f}%"}
                            for k, v in r["ingredients"].items()]),
                            use_container_width=True, hide_index=True)
                        nutrients = compute_formula_nutrients(r["ingredients"])
                        n1, n2, n3, n4 = st.columns(4)
                        n1.metric("CP", f"{nutrients['CP']:.2f}%")
                        n2.metric("DP", f"{nutrients['DP']:.2f}%")
                        n3.metric("SE", f"{nutrients['SE']:.2f}")
                        n4.metric("NDF", f"{nutrients['NDF']:.2f}%")
                else:
                    st.error(f"❌ {r['message']}")


# ═════════════════════════════════════════════════════════════════════════════
# القسم 37: تبويبات المالك
# ═════════════════════════════════════════════════════════════════════════════

if is_owner():
    with tabs[6]:
        guide_section("المختبر المتقدم",
                       "تحليل خلطات مخصصة + المستشار الذكي.")
        st.markdown('<div class="section-title">🔬 المختبر المتقدم</div>',
                    unsafe_allow_html=True)
        render_ai_advisor()

    with tabs[7]:
        guide_section("مواقيت الصلاة", "عرض مواقيت الصلاة.")
        render_prayer_times()

    with tabs[8]:
        guide_section("منبه الجرعات", "إدارة منبهات اللقاحات.")
        render_dose_reminders()

    with tabs[9]:
        guide_section("الإنتاج اليومي", "تسجيل بيانات الإنتاج اليومي.")
        render_daily_production()

    with tabs[10]:
        guide_section("التنبيهات", "تنبيهات المخزون.")
        render_alerts()

    with tabs[11]:
        st.markdown('<div class="section-title">📊 البورصة</div>',
                    unsafe_allow_html=True)
        t1, t2 = st.tabs(["🐄 الماشية", "🥩 المنتجات"])
        with t1:
            for animal, price in list(st.session_state["livestock_prices"].items()):
                new_p = st.number_input(f"تحديث: {animal}", min_value=0.0,
                    value=float(price), step=0.1, key=f"lv_{animal}_v20")
                st.session_state["livestock_prices"][animal] = new_p
        with t2:
            for product, price in list(st.session_state["products_prices"].items()):
                new_p = st.number_input(f"تحديث: {product}", min_value=0.0,
                    value=float(price), step=0.05, key=f"pr_{product}_v20")
                st.session_state["products_prices"][product] = new_p

    with tabs[12]:
        st.markdown('<div class="section-title">🏭 المستودعات</div>',
                    unsafe_allow_html=True)
        inv = st.session_state["inventory"]
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("إجمالي", len(inv))
        low = sum(1 for v in inv.values() if v.get("quantity", 0) < 5)
        col_b.metric("منخفضة", low)
        crit = sum(1 for v in inv.values() if v.get("quantity", 0) <= 0)
        col_c.metric("نفذت", crit)
        col_d.metric("آمنة", len(inv) - low - crit)
        cols = st.columns(3)
        for i, (name, data) in enumerate(list(inv.items())[:60]):
            with cols[i % 3]:
                q = data["quantity"] if isinstance(data, dict) else data
                badge = "🔴" if q <= 0 else ("🟡" if q < 5 else "🟢")
                st.markdown(f"{badge} **{name}**: {q:.1f} طن")
                new_q = st.number_input("تحديث:", min_value=0.0,
                    value=float(q), key=f"inv_{name}_v20",
                    label_visibility="collapsed")
                if isinstance(inv[name], dict):
                    inv[name]["quantity"] = new_q

    with tabs[13]:
        st.markdown('<div class="section-title">🧾 الفواتير</div>',
                    unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            client = st.text_input("العميل:", "مزرعة الأمل", key="inv_client_v20")
        with fc2:
            tons = st.number_input("الكمية (طن):", 0.1, 1000.0, 2.0, 0.5,
                                     key="inv_tons_v20")
        with fc3:
            profit = st.number_input("هامش الربح ($/طن):", 0.0, 1000.0, 50.0,
                                       key="inv_profit_v20")
        sell = st.session_state["computed_ton_cost"] + profit
        total = sell * tons
        st.markdown(
            f'<div class="price-card"><h4>🧾 فاتورة</h4>'
            f'<p><b>العميل:</b> {client}</p>'
            f'<p><b>الكمية:</b> {tons} طن</p>'
            f'<p><b>سعر الطن:</b> ${sell:.2f}</p>'
            f'<p style="font-size:1.3rem; color:#1b5e20;">'
            f'<b>الإجمالي:</b> ${total:.2f}</p></div>',
            unsafe_allow_html=True)

    with tabs[14]:
        st.markdown('<div class="section-title">🖨️ الديباجة</div>',
                    unsafe_allow_html=True)
        brand = st.text_input("اسم البراند:", APP_NAME, key="brand_v20")
        st.markdown(
            f'<div style="border:3px dashed #1b5e20; padding:30px; '
            f'border-radius:15px; background:linear-gradient(135deg, '
            f'#f1f8e9, #e8f5e9); text-align:center;">'
            f'<img src="{st.session_state["active_animal_img"]}" '
            f'style="width:100%; max-height:200px; object-fit:cover; '
            f'border-radius:12px; margin-bottom:15px;">'
            f'<h2 style="color:#1b5e20;">🌟 {brand} 🌟</h2>'
            f'<h3 style="color:#c62828;">{SUPERVISOR} — '
            f'{SUPERVISOR_TITLE}</h3>'
            f'<p style="background:#e8f5e9; padding:12px; '
            f'border-radius:8px; color:#1b5e20; font-weight:bold;">'
            f'🎯 {st.session_state["active_stage_title"]}</p>'
            f'<small>📅 {datetime.now():%Y-%m-%d}</small></div>',
            unsafe_allow_html=True)

    with tabs[15]:
        st.markdown('<div class="section-title">📈 التحليلات المتقدمة</div>',
                    unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("الخلطات", "1,247")
        m2.metric("متوسط التكلفة", "$285")
        m3.metric("التوفير", "18%")
        m4.metric("رضا العملاء", "96%")
        if PLOTLY_AVAILABLE:
            usage = pd.DataFrame({
                'المادة': ['ذرة', 'صويا', 'نخالة', 'زيوت', 'أملاح', 'أخرى'],
                'نسبة الاستخدام': [42, 23, 14, 8, 8, 5]})
            fig = px.pie(usage, values='نسبة الاستخدام', names='المادة',
                         color_discrete_sequence=px.colors.sequential.Greens)
            st.plotly_chart(fig, use_container_width=True)

    with tabs[16]:
        st.markdown('<div class="section-title">🐔 مزارع الدجاج</div>',
                    unsafe_allow_html=True)
        with st.expander("➕ إضافة مزرعة"):
            nf_name = st.text_input("اسم المزرعة:", key="nf_name_v20")
            nf_owner = st.text_input("المالك:", key="nf_owner_v20")
            if st.button("💾 حفظ", key="nf_save_v20") and nf_name:
                st.session_state["broiler_farms"][nf_name] = {
                    "owner": nf_owner,
                    "data": {"age": 1, "birds": 1000,
                             "weight_kg": 0.045, "feed_kg": 0.0,
                             "dead": 0, "temp": 33.0, "hum": 65.0}}
                st.success(f"✅ تمت إضافة {nf_name}")
                st.rerun()
        if st.session_state["broiler_farms"]:
            farms = list(st.session_state["broiler_farms"].keys())
            sel = st.selectbox("اختر مزرعة:", [""] + farms,
                                key="bf_select_v20")
            if sel:
                d = st.session_state["broiler_farms"][sel]["data"]
                b1, b2 = st.columns(2)
                with b1:
                    d["age"] = st.number_input("العمر (يوم):", 1, 60,
                        d["age"], key="bf_age_v20")
                    d["birds"] = st.number_input("الطيور:", 1,
                        value=d["birds"], key="bf_birds_v20")
                    d["weight_kg"] = st.number_input("الوزن (كجم):",
                        0.0, 10.0, float(d["weight_kg"]), 0.01,
                        key="bf_w_v20")
                    d["feed_kg"] = st.number_input("العلف (كجم):", 0.0,
                        float(d["feed_kg"]), 100.0, key="bf_f_v20")
                with b2:
                    d["dead"] = st.number_input("النافق:", 0,
                        value=d["dead"], key="bf_d_v20")
                    d["temp"] = st.number_input("الحرارة:", 10.0, 45.0,
                        float(d["temp"]), key="bf_t_v20")
                    d["hum"] = st.number_input("الرطوبة:", 20.0, 90.0,
                        float(d["hum"]), key="bf_h_v20")
                alive = d["birds"] - d["dead"]
                gain = alive * (d["weight_kg"] - 0.045)
                adg = ((d["weight_kg"] - 0.045) * 1000 / d["age"]) \
                    if d["age"] > 0 else 0
                fcr = (d["feed_kg"] / gain) if gain > 0 else 0
                liv = 100 - (d["dead"] / d["birds"] * 100)
                epef = ((liv * d["weight_kg"]) / (d["age"] * fcr) * 100) \
                    if d["age"] > 0 and fcr > 0 else 0
                k1, k2, k3 = st.columns(3)
                k1.metric("ADG (جم)", f"{adg:.1f}")
                k2.metric("FCR", f"{fcr:.2f}")
                k3.metric("EPEF", f"{epef:.0f}")

    with tabs[17]:
        st.markdown('<div class="section-title">💬 تعليقات المختصين</div>',
                    unsafe_allow_html=True)
        st.text_area("الحالية:",
                     value=st.session_state["shared_comments"],
                     height=200, disabled=True, key="comments_view_v20")
        nc = st.text_area("📝 إضافة تعليق جديد:", key="comments_new_v20")
        if st.button("➕ نشر", key="comments_post_v20"):
            if nc:
                st.session_state["shared_comments"] += (
                    f"\n• [{datetime.now():%Y-%m-%d %H:%M}]: {nc}")
                st.success("✅ تم النشر!")
                st.rerun()

    with tabs[18]:
        guide_section("المراجع العلمية", "مصادر معتمدة.")
        st.markdown('<div class="section-title">📚 المراجع العلمية</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        - **NRC (2012)** — Swine Nutrition
        - **NRC (2007)** — Small Ruminants
        - **NRC (2001)** — Dairy Cattle
        - **NRC (2007)** — Horses
        - **NRC (1994)** — Poultry
        - **INRA (2018)** — Ruminants
        - **FAO (2010)** — Camel Nutrition
        - **Ross 308 (2020)** — Broiler Management
        - **Van Soest (1994)** — Ruminant Ecology
        - **EFSA** — Animal Housing Standards
        """)

    with tabs[19]:
        guide_section("المساعدة", "دليل سريع.")
        st.markdown(f"""
        ### خطوات الاستخدام:
        1. **تركيب الأعلاف** — اختر حيوان، اختر مكونات، شغّل المحرك
        2. **معمل التحليل** — أدخل أوزان للتحليل الشامل
        3. **مصمم الحظائر** — صمم حظيرة بالمعايير العلمية
        4. **بدائل الحليب** — للرضاعة الصناعية
        5. **المختبر الذكي** — OCR للصور

        ### 🔧 الدعم
        📧 {OWNER_EMAIL}
        📱 {WHATSAPP_NUMBER}
        """)

    with tabs[20]:
        guide_section("دليل المستخدم", "شرح مفصل.")
        st.markdown(f"""
        <div style="background:#fff; padding:30px; border-radius:16px;">
        <div class="book-chapter">📘 الفصل 1: تركيب الأعلاف</div>
        <div class="book-body">
        نظام ذكي يحسب أقل تكلفة للخلطة وفق NRC و INRA.
        </div>
        <div class="book-chapter">🧪 الفصل 2: معمل التحليل</div>
        <div class="book-body">
        نظام Weende و Van Soest للتحليل التقريبي، الطاقة، والأحماض الأمينية.
        </div>
        <div class="book-chapter">🏗️ الفصل 3: مصمم الحظائر</div>
        <div class="book-body">
        تصميم حظائر وفق المعايير العالمية مع مخططات المعالف والسقايات.
        </div>
        <div class="book-chapter">🌰 الفصل 4: الزيوت</div>
        <div class="book-body">
        15 زيتاً بمعايير عالمية مع حد أقصى لكل حيوان.
        </div>
        <div class="book-chapter">🍼 الفصل 5: بدائل الحليب</div>
        <div class="book-body">
        تركيب بدائل حليب للعجول والحملان والجديان والأمهار والإبل.
        </div>
        </div>
        """, unsafe_allow_html=True)

    with tabs[21]:
        guide_section("دليل النشر", "خطوات النشر.")
        render_deployment_guide()

    with tabs[22]:
        guide_section("إرسال الكود", "إرسال السورس كود.")
        render_send_code()


# ═════════════════════════════════════════════════════════════════════════════
# القسم 38: تبويبات الزائر
# ═════════════════════════════════════════════════════════════════════════════

if not is_owner():
    with tabs[6]:
        guide_section("مواقيت الصلاة", "عرض مواقيت الصلاة.")
        render_prayer_times()

    with tabs[7]:
        guide_section("المراجع العلمية", "مصادر معتمدة.")
        st.markdown('<div class="section-title">📚 المراجع</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        - NRC 2012 — Swine
        - NRC 2007 — Small Ruminants
        - NRC 2001 — Dairy Cattle
        - INRA 2018 — Ruminants
        - FAO 2010 — Camel Nutrition
        - Ross 308 — Broiler
        - EFSA — Housing Standards
        """)

    with tabs[8]:
        guide_section("المساعدة", "دليل سريع.")
        st.markdown(f"""
        ### الميزات المتاحة:
        - 🔬 تركيب الأعلاف
        - 🧪 معمل التحليل
        - 🏗️ مصمم الحظائر
        - 🌰 مكتبة الزيوت
        - 🍼 بدائل الحليب
        - 📷 المختبر الذكي

        ### 🔧 الدعم
        📧 {OWNER_EMAIL}
        """)

    with tabs[9]:
        guide_section("دليل المستخدم", "شرح.")
        st.markdown(f"""
        ### عن المنصة
        {APP_NAME} — منصة تركيب وتحليل الأعلاف وتصميم الحظائر.
        تعتمد على NRC، INRA، FAO، EFSA.
        """)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 39: التذييل الثابت
# ═════════════════════════════════════════════════════════════════════════════

st.markdown(
    f'<div class="mini-signature">🌾 {APP_NAME} | {SUPERVISOR} © 2026</div>',
    unsafe_allow_html=True)
st.markdown(
    f'<div class="dua-fixed-banner">🤲 {DUA_SHORT} 🤲</div>',
    unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if st.button("🔊 اختبار الصوت"):
    voice_guide("بسم الله الرحمن الرحيم، هذا اختبار للنظام الصوتي.")


# ═════════════════════════════════════════════════════════════════════════════
# نهاية الملف — تاور نولجي Tawor Nology v20.0 | © 2026
# إشراف: م. عبدالقادر إسماعيل تاور - اختصاصي تغذية الحيوان
# 🕊️ رحم الله والدي إسماعيل تاور وأختي ابتسام 🕊️
# ═════════════════════════════════════════════════════════════════════════════
