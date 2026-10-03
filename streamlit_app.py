# ============================================================================
# ████████████████████████████████████████████████████████████████████████████
# █                                                                          █
# █        تاور نولجي TAWOR NOLOGY — الإصدار 18.0 المتكامل النهائي          █
# █        للإنتاج الحيواني وتركيب الأعلاف                                   █
# █                                                                          █
# █        إشراف: م. عبدالقادر إسماعيل تاور                                   █
# █        اختصاصي تغذية الحيوان                                              █
# █                                                                          █
# █   🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌                        █
# █                                                                          █
# █   ال merger الكامل: v17.0 + v10.0                                        █
# █   ✓ 21 تبويب متكامل   ✓ 15 زيت   ✓ مختبر ذكي   ✓ PDF احترافي            █
# █   ✓ منبه جرعات   ✓ مواقيت صلاة   ✓ إنتاج يومي   ✓ قاعدة بيانات          █
# █                                                                          █
# ████████████████████████████████████████████████████████████████████████████
# ============================================================================

# ─── المكتبات الأساسية ─────────────────────────────────────────────────────
import streamlit as st
import numpy as np
import pandas as pd
import json, os, base64, time, re, io, sqlite3, hashlib, secrets, warnings
import urllib.parse, urllib.request, smtplib
import math, random
from datetime import datetime, timedelta, date
from functools import lru_cache
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, asdict, field
from collections import defaultdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

warnings.filterwarnings('ignore')

# ─── المكتبات العلمية ──────────────────────────────────────────────────────
try:
    from scipy.optimize import linprog
    from scipy.spatial import ConvexHull
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import altair as alt
    ALTAIR_AVAILABLE = True
except ImportError:
    ALTAIR_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
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
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

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
    from reportlab.lib.pagesizes import A4, landscape, letter
    from reportlab.lib.units import inch, mm, cm
    from reportlab.lib.colors import (HexColor, black, white, grey, blue,
                                       red, green, orange, purple, teal, gold)
    from reportlab.platypus import (Table, TableStyle, Paragraph, Spacer,
                                     Image as RLImage, SimpleDocTemplate,
                                     PageBreak, KeepTogether, HRFlowable)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
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
# القسم 1: الدعاء — إهداء روحي
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

CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2024": {"role": "veterinarian", "name": "الطبيب البيطري", "level": 2},
    "2025": {"role": "nutritionist", "name": "أخصائي التغذية", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

st.set_page_config(
    page_title=f"{APP_NAME} | {APP_TAGLINE}",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 3: إدارة الخطوط العربية
# ═════════════════════════════════════════════════════════════════════════════

FONT_DIR = "fonts"
os.makedirs(FONT_DIR, exist_ok=True)

ARABIC_FONT_URLS = [
    ("https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf",
     "Amiri-Regular.ttf"),
    ("https://github.com/google/fonts/raw/main/ofl/cairo/Cairo%5Bslnt%2Cwght%5D.ttf",
     "Cairo-Regular.ttf"),
]


class ArabicFontManager:
    """مدير الخطوط العربية — يحل مشكلة العربية في PDF"""
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
            "/usr/share/fonts/truetype/arabic/Amiri-Regular.ttf",
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

    @staticmethod
    def norm(text):
        if not text:
            return ""
        text = str(text).strip()
        for a, b in [('أ','ا'),('إ','ا'),('آ','ا'),('ى','ي'),('ة','ه')]:
            text = text.replace(a, b)
        return text


arp = ArabicProcessor()

def ar(text):
    return arp.fix(text)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 4: مكتبة الأعلاف الشاملة (مع 15 زيت)
# ═════════════════════════════════════════════════════════════════════════════

BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3, "Ca": 0.02, "P": 0.27},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4, "Ca": 0.02, "P": 0.26},
        "ذرة شامية": {"CP": 8.3, "DC": 0.86, "SE": 82.0, "NDF": 9.0, "ADF": 3.0, "EE": 4.0, "ASH": 1.2, "Ca": 0.02, "P": 0.28},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5, "Ca": 0.05, "P": 0.35},
        "شعير كامل": {"CP": 10.8, "DC": 0.75, "SE": 68.0, "NDF": 22.0, "ADF": 9.0, "EE": 2.0, "ASH": 2.8, "Ca": 0.05, "P": 0.33},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8, "Ca": 0.03, "P": 0.30},
        "قمح محلي": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6, "Ca": 0.04, "P": 0.32},
        "قمح مستورد": {"CP": 11.5, "DC": 0.87, "SE": 78.0, "NDF": 11.0, "ADF": 3.5, "EE": 1.9, "ASH": 1.5, "Ca": 0.04, "P": 0.33},
        "جريش أرز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2, "Ca": 0.06, "P": 0.30},
        "دخن محلي": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2, "Ca": 0.05, "P": 0.31},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0, "Ca": 0.08, "P": 0.35},
        "كسرة خبز": {"CP": 10.5, "DC": 0.82, "SE": 75.0, "NDF": 8.0, "ADF": 3.5, "EE": 5.5, "ASH": 3.5, "Ca": 0.10, "P": 0.20},
        "بسكويت مكسر": {"CP": 8.5, "DC": 0.85, "SE": 85.0, "NDF": 4.0, "ADF": 2.0, "EE": 12.0, "ASH": 2.5, "Ca": 0.08, "P": 0.18},
    },

    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5, "Ca": 0.20, "P": 0.65},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0, "Ca": 0.35, "P": 0.65},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2, "Ca": 0.35, "P": 0.65},
        "كسب فول صويا 46%": {"CP": 46.0, "DC": 0.905, "SE": 75.0, "NDF": 12.5, "ADF": 7.5, "EE": 1.6, "ASH": 6.1, "Ca": 0.35, "P": 0.65},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5, "Ca": 0.40, "P": 1.00},
        "كسب عباد الشمس 32%": {"CP": 32.0, "DC": 0.72, "SE": 38.0, "NDF": 42.0, "ADF": 28.0, "EE": 2.0, "ASH": 7.0, "Ca": 0.42, "P": 0.95},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5, "Ca": 0.20, "P": 1.10},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8, "Ca": 0.35, "P": 0.85},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5, "Ca": 2.00, "P": 1.20},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5, "Ca": 0.15, "P": 0.50},
        "كسب جلوتين الذرة 40%": {"CP": 40.0, "DC": 0.88, "SE": 72.0, "NDF": 15.0, "ADF": 8.0, "EE": 3.0, "ASH": 5.0, "Ca": 0.18, "P": 0.55},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5, "Ca": 0.30, "P": 0.55},
        "كسب بذور العنب": {"CP": 12.0, "DC": 0.55, "SE": 30.0, "NDF": 45.0, "ADF": 32.0, "EE": 7.5, "ASH": 6.0, "Ca": 0.25, "P": 0.40},
        "كسب بذور القرطم": {"CP": 24.0, "DC": 0.70, "SE": 45.0, "NDF": 35.0, "ADF": 22.0, "EE": 2.0, "ASH": 6.0, "Ca": 0.35, "P": 0.75},
        "كسب بذور اللفت (كانولا)": {"CP": 36.0, "DC": 0.82, "SE": 60.0, "NDF": 28.0, "ADF": 18.0, "EE": 3.5, "ASH": 6.5, "Ca": 0.65, "P": 1.10},
        "كسب بذور الأفوكادو": {"CP": 18.0, "DC": 0.65, "SE": 50.0, "NDF": 40.0, "ADF": 28.0, "EE": 8.0, "ASH": 5.5, "Ca": 0.30, "P": 0.45},
    },

    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5, "Ca": 0.12, "P": 1.10},
        "نخالة ذرة": {"CP": 9.5, "DC": 0.65, "SE": 40.0, "NDF": 40.0, "ADF": 15.0, "EE": 4.0, "ASH": 2.0, "Ca": 0.10, "P": 0.75},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5, "Ca": 1.50, "P": 0.25},
        "برسيم حجازي": {"CP": 18.0, "DC": 0.62, "SE": 38.0, "NDF": 40.0, "ADF": 30.0, "EE": 2.2, "ASH": 11.0, "Ca": 1.60, "P": 0.26},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5, "Ca": 0.70, "P": 0.05},
        "تبن قمح": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.30, "P": 0.08},
        "تبن فول": {"CP": 4.5, "DC": 0.40, "SE": 22.0, "NDF": 68.0, "ADF": 42.0, "EE": 1.2, "ASH": 7.5, "Ca": 0.35, "P": 0.10},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5, "Ca": 0.25, "P": 0.10},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5, "Ca": 0.15, "P": 0.08},
        "قش أرز معالج": {"CP": 3.5, "DC": 0.30, "SE": 15.0, "NDF": 70.0, "ADF": 45.0, "EE": 1.5, "ASH": 12.0, "Ca": 0.20, "P": 0.06},
        "مخلفات النخيل": {"CP": 6.5, "DC": 0.70, "SE": 60.0, "NDF": 25.0, "ADF": 15.0, "EE": 5.0, "ASH": 3.5, "Ca": 0.15, "P": 0.15},
        "قشور الفول السوداني": {"CP": 6.5, "DC": 0.40, "SE": 22.0, "NDF": 58.0, "ADF": 38.0, "EE": 2.5, "ASH": 4.0, "Ca": 0.20, "P": 0.12},
        "تفل العنب المجفف": {"CP": 12.0, "DC": 0.50, "SE": 45.0, "NDF": 45.0, "ADF": 30.0, "EE": 5.0, "ASH": 8.0, "Ca": 0.40, "P": 0.30},
        "نخالة الأرز الدهنية": {"CP": 12.5, "DC": 0.70, "SE": 55.0, "NDF": 30.0, "ADF": 15.0, "EE": 15.0, "ASH": 8.0, "Ca": 0.10, "P": 1.40},
        "علف الشعير المستنبت": {"CP": 15.0, "DC": 0.75, "SE": 60.0, "NDF": 25.0, "ADF": 12.0, "EE": 3.0, "ASH": 5.0, "Ca": 0.10, "P": 0.40},
    },

    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5, "Ca": 5.50, "P": 3.20},
        "مسحوق أسماك 72%": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5, "Ca": 4.80, "P": 2.80},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5, "Ca": 9.00, "P": 4.50},
        "مسحوق الدم": {"CP": 80.0, "DC": 0.65, "SE": 55.0, "NDF": 1.0, "ADF": 0.5, "EE": 1.5, "ASH": 6.0, "Ca": 0.30, "P": 0.30},
        "مسحوق ريش": {"CP": 82.0, "DC": 0.70, "SE": 60.0, "NDF": 1.5, "ADF": 1.0, "EE": 3.0, "ASH": 4.0, "Ca": 0.25, "P": 0.35},
        "مسحوق مخلفات دواجن": {"CP": 55.0, "DC": 0.78, "SE": 58.0, "NDF": 5.0, "ADF": 3.0, "EE": 12.0, "ASH": 15.0, "Ca": 3.00, "P": 1.80},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5, "Ca": 2.50, "P": 1.20},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5, "Ca": 3.00, "P": 1.50},
        "بروتين بلازما الدم المجفف": {"CP": 78.0, "DC": 0.90, "SE": 62.0, "NDF": 0.5, "ADF": 0.0, "EE": 2.0, "ASH": 10.0, "Ca": 0.15, "P": 0.20},
        "بروتين مصل الحليب (WPC)": {"CP": 80.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 3.0, "ASH": 3.0, "Ca": 0.50, "P": 0.40},
    },

    "🌿 الأعلاف الخضراء المائية": {
        "أزولا مجففة": {"CP": 24.0, "DC": 0.65, "SE": 45.0, "NDF": 38.0, "ADF": 25.0, "EE": 3.5, "ASH": 18.0, "Ca": 2.00, "P": 0.60},
        "سبيرولينا": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 5.0, "ADF": 3.0, "EE": 6.0, "ASH": 10.0, "Ca": 1.20, "P": 0.90},
        "كلوريلا": {"CP": 55.0, "DC": 0.80, "SE": 60.0, "NDF": 6.0, "ADF": 3.5, "EE": 8.0, "ASH": 12.0, "Ca": 0.50, "P": 1.20},
        "طحالب بحرية": {"CP": 15.0, "DC": 0.60, "SE": 30.0, "NDF": 25.0, "ADF": 15.0, "EE": 2.0, "ASH": 30.0, "Ca": 1.50, "P": 0.30},
    },

    # ═══════════════════════════════════════════════════════════════════
    # 🌰 الزيوت النباتية والحيوانية — 15 زيتاً بمعايير NRC/INRA/FAO
    # ═══════════════════════════════════════════════════════════════════
    "🌰 الزيوت النباتية والحيوانية": {
        "زيت ذرة": {
            "CP": 0.0, "DC": 0.0, "SE": 220.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
            "desc": "طاقة عالية (9000 kcal/kg)، غني بأوميغا 6",
            "max_poultry": 6.0, "max_ruminant": 5.0, "max_fish": 10.0,
            "max_horse": 8.0, "source": "NRC 2012"
        },
        "زيت فول الصويا": {
            "CP": 0.0, "DC": 0.0, "SE": 215.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
            "desc": "أشهر زيوت الأعلاف، متوازن، طاقة 8800 kcal/kg",
            "max_poultry": 8.0, "max_ruminant": 5.0, "max_fish": 12.0,
            "max_horse": 10.0, "source": "Ross 308 / NRC 2012"
        },
        "زيت عباد الشمس": {
            "CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
            "desc": "غني بأوميغا 6، رخيص نسبياً، طاقة 8500 kcal/kg",
            "max_poultry": 6.0, "max_ruminant": 4.0, "max_fish": 8.0,
            "max_horse": 8.0, "source": "NRC 2007"
        },
        "زيت بذرة القطن": {
            "CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
            "desc": "يحتوي جوسيبول (يجب معادلة)، طاقة 8000 kcal/kg",
            "max_poultry": 3.0, "max_ruminant": 5.0, "max_fish": 6.0,
            "max_horse": 5.0, "source": "NRC 2012"
        },
        "زيت الكتان": {
            "CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
            "desc": "غني جداً بأوميغا 3، ممتاز للخيول والمناعة",
            "max_poultry": 3.0, "max_ruminant": 3.0, "max_fish": 6.0,
            "max_horse": 8.0, "source": "NRC 2007 Horses"
        },
        "زيت جوز الهند": {
            "CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
            "desc": "دهون متوسطة السلسلة MCT، سهل الهضم، مضاد بكتيري",
            "max_poultry": 5.0, "max_ruminant": 3.0, "max_fish": 8.0,
            "max_horse": 6.0, "source": "NRC 2012"
        },
        "زيت النخيل": {
            "CP": 0.0, "DC": 0.0, "SE": 215.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
            "desc": "طاقة عالية، مقاوم للأكسدة، طاقة 8700 kcal/kg",
            "max_poultry": 6.0, "max_ruminant": 5.0, "max_fish": 8.0,
            "max_horse": 8.0, "source": "NRC 2012"
        },
        "زيت الكانولا": {
            "CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
            "desc": "متوازن أوميغا 3 و6، مناسب للمجترات والدواجن",
            "max_poultry": 5.0, "max_ruminant": 5.0, "max_fish": 8.0,
            "max_horse": 6.0, "source": "NRC 2012"
        },
        "زيت السمسم": {
            "CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
            "desc": "غني بمضادات الأكسدة الطبيعية، طاقة 8500 kcal/kg",
            "max_poultry": 4.0, "max_ruminant": 3.0, "max_fish": 6.0,
            "max_horse": 5.0, "source": "NRC 2007"
        },
        "زيت الزيتون": {
            "CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
            "desc": "غني بأوميغا 9، مضاد أكسدة قوي، مكلف نسبياً",
            "max_poultry": 4.0, "max_ruminant": 4.0, "max_fish": 5.0,
            "max_horse": 5.0, "source": "INRA 2018"
        },
        "زيت الأفوكادو": {
            "CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
            "desc": "غني بفيتامين E، مضاد أكسدة قوي",
            "max_poultry": 3.0, "max_ruminant": 3.0, "max_fish": 4.0,
            "max_horse": 4.0, "source": "NRC 2012"
        },
        "زيت القرطم": {
            "CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
            "desc": "غني جداً بأوميغا 6 (75%)، للحيوانات عالية الطاقة",
            "max_poultry": 4.0, "max_ruminant": 3.0, "max_fish": 5.0,
            "max_horse": 5.0, "source": "NRC 2012"
        },
        "زيت الفول السوداني": {
            "CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
            "desc": "طاقة عالية جداً، نكهة مقبولة، طاقة 8900 kcal/kg",
            "max_poultry": 5.0, "max_ruminant": 4.0, "max_fish": 6.0,
            "max_horse": 6.0, "source": "NRC 2012"
        },
        "شحم حيواني (Tallow)": {
            "CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
            "desc": "طاقة عالية (9500 kcal/kg)، صلب، مقاوم للأكسدة",
            "max_poultry": 6.0, "max_ruminant": 5.0, "max_fish": 6.0,
            "max_horse": 8.0, "source": "NRC 2012"
        },
        "دهن الدجاج": {
            "CP": 0.0, "DC": 0.0, "SE": 225.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
            "desc": "شحم الدواجن المعاد تدويره، اقتصادي",
            "max_poultry": 6.0, "max_ruminant": 0.0, "max_fish": 5.0,
            "max_horse": 6.0, "source": "NRC 2012"
        },
        "زيت السمك (Fish Oil)": {
            "CP": 0.0, "DC": 0.0, "SE": 235.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
            "desc": "غني بأوميغا 3 EPA/DHA، ممتاز للأسماك والمناعة",
            "max_poultry": 2.0, "max_ruminant": 2.0, "max_fish": 8.0,
            "max_horse": 3.0, "source": "NRC Fish Nutrition"
        },
    },

    "🧪 الأحماض الأمينية البلورية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0},
        "ليسين سلفات": {"CP": 79.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3, "Ca": 0.0, "P": 0.0},
        "ميثيونين هيدروكسي": {"CP": 88.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0},
        "ثريونين نقي (L-Threonine)": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0},
        "تريبتوفان نقي (L-Tryptophan)": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0},
        "فالين نقي (L-Valine)": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0},
        "أرجينين": {"CP": 98.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0},
        "هيستيدين": {"CP": 96.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0},
        "إيزوليوسين": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0},
        "ليوسين": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0},
    },

    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 8.0},
        "بريمكس بياض وبشاير": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 22.0, "P": 7.0},
        "بريمكس أبقار حلابة": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0},
        "بريمكس مجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 9.0},
        "بريمكس خيول": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 8.0},
        "بريمكس إبل": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0},
        "بريمكس أسماك": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 7.0},
        "إنزيم الفايتيز (Phytase Super-D)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0, "Ca": 0.0, "P": 0.0},
        "إنزيم NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0, "Ca": 0.0, "P": 0.0},
        "إنزيم بروتييز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 2.0, "Ca": 0.0, "P": 0.0},
        "إنزيم أميليز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0, "Ca": 0.0, "P": 0.0},
        "كبريتات الحديدوز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0, "Ca": 0.0, "P": 0.0},
        "مستخلص الخمائر MOS": {"CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.10, "P": 0.20},
        "خمائر حية": {"CP": 45.0, "DC": 0.75, "SE": 30.0, "NDF": 8.0, "ADF": 4.0, "EE": 1.0, "ASH": 8.0, "Ca": 0.15, "P": 1.20},
        "بروبيوتيك": {"CP": 15.0, "DC": 0.60, "SE": 20.0, "NDF": 5.0, "ADF": 3.0, "EE": 2.0, "ASH": 15.0, "Ca": 0.30, "P": 0.50},
        "بريبيوتيك FOS": {"CP": 0.0, "DC": 0.0, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 2.0, "Ca": 0.0, "P": 0.0},
    },

    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 38.0, "P": 0.0},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5, "Ca": 23.0, "P": 18.0},
        "فوسفات أحادي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 17.0, "P": 22.0},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9, "Ca": 0.0, "P": 0.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 0.0, "P": 0.0},
        "أكسيد المغنيسيوم العلفي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 0.0, "P": 0.0},
        "كبريتات المغنيسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0, "Ca": 0.0, "P": 0.0},
        "يوريا علفية محصنة": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0, "Ca": 0.0, "P": 0.0},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Ca": 0.0, "P": 0.0},
        "مضاد أكسدة BHT": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0},
        "كلوريد الكولين (Choline)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0},
    },

    "🍼 مكونات بدائل الحليب": {
        "مصل الحليب المجفف (Whey)": {"CP": 12.0, "DC": 0.95, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.0, "Ca": 0.70, "P": 0.60},
        "حليب مجفف خالي الدسم": {"CP": 34.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.5, "Ca": 1.30, "P": 1.00},
        "حليب مجفف كامل الدسم": {"CP": 26.0, "DC": 0.95, "SE": 55.0, "NDF": 0.0, "ADF": 0.0, "EE": 28.0, "ASH": 6.0, "Ca": 0.95, "P": 0.75},
        "دهن نباتي (زيت نباتي)": {"CP": 0.0, "DC": 0.0, "SE": 10.0, "NDF": 0.0, "ADF": 0.0, "EE": 99.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0},
        "ليسيثين الصويا": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 95.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0},
        "فيتامينات ومعادن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0},
        "بروتين الصويا المركز": {"CP": 65.0, "DC": 0.90, "SE": 30.0, "NDF": 2.0, "ADF": 1.0, "EE": 1.0, "ASH": 5.5, "Ca": 0.30, "P": 0.70},
        "مالتودكسترين": {"CP": 0.0, "DC": 0.0, "SE": 90.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0},
        "لاكتوز نقي": {"CP": 0.0, "DC": 0.0, "SE": 85.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0},
        "كازين": {"CP": 85.0, "DC": 0.95, "SE": 45.0, "NDF": 0.0, "ADF": 0.0, "EE": 2.0, "ASH": 2.0, "Ca": 0.40, "P": 0.60},
    },
}

# قاموس مسطح للبحث السريع
FLAT_FEED_DB = {}
for category, items in BIG_FEEDS_LIBRARY.items():
    for feed_name, nutrition in items.items():
        FLAT_FEED_DB[feed_name] = nutrition


# ═════════════════════════════════════════════════════════════════════════════
# القسم 5: معايير الزيوت العالمية
# ═════════════════════════════════════════════════════════════════════════════

MAX_OIL_PERCENTAGE = {
    "دواجن_بادي":    {"max": 8.0, "optimal": 5.0, "source": "Ross 308 2020"},
    "دواجن_نامي":    {"max": 7.0, "optimal": 4.5, "source": "Ross 308 2020"},
    "دواجن_ناهي":    {"max": 7.0, "optimal": 4.0, "source": "Ross 308 2020"},
    "دواجن_بياض":    {"max": 5.0, "optimal": 2.5, "source": "NRC 1994"},
    "سمان_بادي":     {"max": 6.0, "optimal": 4.0, "source": "NRC Quail"},
    "سمان_بياض":     {"max": 5.0, "optimal": 2.5, "source": "NRC Quail"},
    "أبقار_حليب_عالي":   {"max": 6.0, "optimal": 4.0, "source": "NRC 2001"},
    "أبقار_حليب_متوسط":  {"max": 5.0, "optimal": 3.5, "source": "NRC 2001"},
    "أبقار_حليب_منخفض":  {"max": 5.0, "optimal": 3.0, "source": "NRC 2001"},
    "أبقار_تسمين_مكثف":  {"max": 6.0, "optimal": 4.5, "source": "NRC 2001"},
    "أبقار_تسمين_عادي":  {"max": 5.0, "optimal": 3.5, "source": "NRC 2001"},
    "أغنام_تسمين_مكثف":  {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "أغنام_تسمين_عادي":  {"max": 4.5, "optimal": 3.0, "source": "NRC 2007"},
    "أغنام_حليب":        {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "أغنام_صيانة":       {"max": 3.5, "optimal": 2.0, "source": "NRC 2007"},
    "ماعز_تسمين":        {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "ماعز_حليب":         {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "ماعز_صيانة":        {"max": 3.5, "optimal": 2.0, "source": "NRC 2007"},
    "إبل_نمو":           {"max": 5.0, "optimal": 3.5, "source": "FAO 2010"},
    "إبل_تسمين":         {"max": 6.0, "optimal": 4.0, "source": "FAO 2010"},
    "إبل_حليب":          {"max": 5.0, "optimal": 3.5, "source": "FAO 2010"},
    "إبل_سباق":          {"max": 8.0, "optimal": 6.0, "source": "FAO 2010"},
    "إبل_صيانة":         {"max": 3.5, "optimal": 2.0, "source": "FAO 2010"},
    "خيول_رياضة_مكثف":   {"max": 10.0, "optimal": 7.0, "source": "NRC 2007 Horses"},
    "خيول_رياضة_عادي":   {"max": 8.0, "optimal": 5.0, "source": "NRC 2007 Horses"},
    "خيول_نمو":          {"max": 8.0, "optimal": 5.0, "source": "NRC 2007 Horses"},
    "خيول_مرضعات":       {"max": 8.0, "optimal": 5.5, "source": "NRC 2007 Horses"},
    "خيول_صيانة":        {"max": 5.0, "optimal": 3.0, "source": "NRC 2007 Horses"},
    "أسماك_بادئ":        {"max": 15.0, "optimal": 10.0, "source": "NRC Fish Nutrition"},
    "أسماك_نمو":         {"max": 12.0, "optimal": 8.0, "source": "NRC Fish Nutrition"},
    "أسماك_تسمين":       {"max": 12.0, "optimal": 8.0, "source": "NRC Fish Nutrition"},
    "أسماك_أمهات":       {"max": 15.0, "optimal": 10.0, "source": "NRC Fish Nutrition"},
}

OIL_CATEGORIES = {
    "زيوت نباتية غنية بأوميغا 6": [
        "زيت ذرة", "زيت عباد الشمس", "زيت القرطم", "زيت فول الصويا"
    ],
    "زيوت نباتية غنية بأوميغا 3": [
        "زيت الكتان", "زيت الكانولا", "زيت السمك (Fish Oil)"
    ],
    "زيوت نباتية متوازنة": [
        "زيت النخيل", "زيت جوز الهند", "زيت الزيتون",
        "زيت السمسم", "زيت الفول السوداني", "زيت الأفوكادو"
    ],
    "دهون حيوانية": [
        "شحم حيواني (Tallow)", "دهن الدجاج"
    ],
    "زيوت خاصة": [
        "زيت بذرة القطن"
    ],
}


def get_oil_standard(standard_key: str) -> dict:
    return MAX_OIL_PERCENTAGE.get(
        standard_key,
        {"max": 5.0, "optimal": 3.0, "source": "معيار عام — NRC"})


def get_oil_ingredients() -> dict:
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت النباتية والحيوانية", {})


# ═════════════════════════════════════════════════════════════════════════════
# القسم 6: المعايير القياسية (v17 - للتوافق)
# ═════════════════════════════════════════════════════════════════════════════

STANDARD_VALUES = {
    "أبقار": {
        "تسمين عجول": {"DP": 12.0, "SE": 68.0, "CP": 15.0, "Energy": 2.8},
        "حليب/إدرار": {"DP": 14.0, "SE": 70.0, "CP": 17.5, "Energy": 3.0},
        "حمل/دفع غذائي": {"DP": 11.0, "SE": 65.0, "CP": 13.8, "Energy": 2.7},
        "صيانة": {"DP": 9.0, "SE": 60.0, "CP": 11.3, "Energy": 2.5},
        "تسمين مكثف": {"DP": 13.0, "SE": 72.0, "CP": 16.3, "Energy": 2.9}
    },
    "أغنام": {
        "تسمين حملان": {"DP": 13.0, "SE": 66.0, "CP": 16.3, "Energy": 2.7},
        "حليب/إدرار": {"DP": 14.5, "SE": 68.0, "CP": 18.1, "Energy": 2.9},
        "حمل/دفع غذائي": {"DP": 11.5, "SE": 62.0, "CP": 14.4, "Energy": 2.6},
        "صيانة": {"DP": 8.5, "SE": 58.0, "CP": 10.6, "Energy": 2.4}
    },
    "ماعز": {
        "تسمين جديان": {"DP": 12.5, "SE": 64.0, "CP": 15.6, "Energy": 2.7},
        "حليب/إدرار": {"DP": 14.0, "SE": 66.0, "CP": 17.5, "Energy": 2.8},
        "حمل/دفع غذائي": {"DP": 11.0, "SE": 60.0, "CP": 13.8, "Energy": 2.6},
        "صيانة": {"DP": 8.0, "SE": 56.0, "CP": 10.0, "Energy": 2.4}
    },
    "خيول": {
        "راحة/صيانة": {"DP": 9.0, "SE": 58.0, "CP": 11.3, "Energy": 2.4},
        "عمل خفيف": {"DP": 10.0, "SE": 60.0, "CP": 12.5, "Energy": 2.5},
        "عمل متوسط": {"DP": 11.0, "SE": 62.0, "CP": 13.8, "Energy": 2.6},
        "عمل مكثف": {"DP": 13.0, "SE": 65.0, "CP": 16.3, "Energy": 2.8},
        "سباق": {"DP": 14.0, "SE": 68.0, "CP": 17.5, "Energy": 3.0},
        "أمهار نامية": {"DP": 13.0, "SE": 64.0, "CP": 16.3, "Energy": 2.7},
        "فرسات مرضعات": {"DP": 14.0, "SE": 66.0, "CP": 17.5, "Energy": 2.9}
    },
    "إبل": {
        "راحة/صيانة": {"DP": 8.0, "SE": 55.0, "CP": 10.0, "Energy": 2.3},
        "حمل/رضاعة": {"DP": 10.0, "SE": 58.0, "CP": 12.5, "Energy": 2.5},
        "إنتاج حليب": {"DP": 12.0, "SE": 60.0, "CP": 15.0, "Energy": 2.7},
        "تسمين": {"DP": 11.0, "SE": 62.0, "CP": 13.8, "Energy": 2.6},
        "عمل/نقل": {"DP": 10.0, "SE": 58.0, "CP": 12.5, "Energy": 2.5}
    },
    "دواجن لاحم": {
        "بادي (0-14 يوم)": {"DP": 22.0, "SE": 76.0, "CP": 27.5, "Energy": 3.0},
        "نامي (15-28 يوم)": {"DP": 20.0, "SE": 74.0, "CP": 25.0, "Energy": 3.1},
        "ناهي (29-42 يوم)": {"DP": 18.0, "SE": 72.0, "CP": 22.5, "Energy": 3.2},
        "ناهي متقدم (43+ يوم)": {"DP": 16.0, "SE": 70.0, "CP": 20.0, "Energy": 3.0}
    },
    "دواجن بياض": {
        "بادي (0-6 أسبوع)": {"DP": 20.0, "SE": 72.0, "CP": 25.0, "Energy": 2.9},
        "نامي (7-14 أسبوع)": {"DP": 18.0, "SE": 70.0, "CP": 22.5, "Energy": 2.8},
        "قبل الإنتاج (15-18 أسبوع)": {"DP": 16.5, "SE": 68.0, "CP": 20.6, "Energy": 2.7},
        "بياض إنتاجي": {"DP": 16.0, "SE": 66.0, "CP": 20.0, "Energy": 2.8}
    },
    "سمان": {
        "بادي": {"DP": 24.0, "SE": 74.0, "CP": 30.0, "Energy": 3.0},
        "نامي": {"DP": 22.0, "SE": 72.0, "CP": 27.5, "Energy": 2.9},
        "بياض": {"DP": 18.0, "SE": 68.0, "CP": 22.5, "Energy": 2.8}
    },
    "أسماك": {
        "زريعة/بادئ": {"DP": 32.0, "SE": 70.0, "CP": 40.0, "Energy": 3.2},
        "نمو": {"DP": 28.0, "SE": 68.0, "CP": 35.0, "Energy": 3.0},
        "تسمين نهائي": {"DP": 26.0, "SE": 66.0, "CP": 32.5, "Energy": 2.9},
        "زريعة متقدمة": {"DP": 30.0, "SE": 69.0, "CP": 37.5, "Energy": 3.1}
    }
}


# ═════════════════════════════════════════════════════════════════════════════
# القسم 7: dataclass للاحتياجات + دوال الاحتياج المتخصصة
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


# ─── الأبقار ──────────────────────────────────────────────────────────────
def get_cattle_requirements(production_type, milk_yield=20.0, weight_kg=500.0):
    if production_type == "حليب_عالي":
        dp = 12.5 + (milk_yield * 0.30)
        cp = dp / 0.70
        return AnimalRequirement(
            DP=round(dp, 2), CP=round(cp, 2),
            SE=round(60 + milk_yield * 0.35, 1),
            NDF=30.0, ADF=19.0, EE=5.5, ASH=8.0,
            Ca=round(0.55 + milk_yield * 0.003, 3),
            P=round(0.33 + milk_yield * 0.0015, 3),
            name_ar="أبقار حلابة عالية",
            note=f"إنتاج {milk_yield} كجم/يوم | الوزن {weight_kg} كجم")
    elif production_type == "حليب_متوسط":
        dp = 11.0 + (milk_yield * 0.25)
        cp = dp / 0.72
        return AnimalRequirement(
            DP=round(dp, 2), CP=round(cp, 2),
            SE=round(55 + milk_yield * 0.30, 1),
            NDF=33.0, ADF=21.0, EE=4.5, ASH=8.0,
            Ca=round(0.50 + milk_yield * 0.0025, 3),
            P=round(0.30 + milk_yield * 0.0012, 3),
            name_ar="أبقار حلابة متوسطة",
            note=f"إنتاج {milk_yield} كجم/يوم")
    elif production_type == "حليب_منخفض":
        dp = 9.5 + (milk_yield * 0.20)
        cp = dp / 0.75
        return AnimalRequirement(
            DP=round(dp, 2), CP=round(cp, 2),
            SE=round(50 + milk_yield * 0.25, 1),
            NDF=38.0, ADF=24.0, EE=4.0, ASH=8.5,
            Ca=round(0.45 + milk_yield * 0.002, 3),
            P=round(0.28 + milk_yield * 0.001, 3),
            name_ar="أبقار حلابة منخفضة",
            note=f"إنتاج {milk_yield} كجم/يوم")
    elif production_type == "تسمين_مكثف":
        return AnimalRequirement(
            DP=11.5, CP=14.5, SE=72.0, NDF=32.0, ADF=20.0,
            EE=4.5, ASH=7.5, Ca=0.65, P=0.38,
            name_ar="تسمين عجول مكثف", note="ADG مستهدف >1.3 كجم/يوم")
    elif production_type == "تسمين_عادي":
        return AnimalRequirement(
            DP=9.5, CP=12.0, SE=65.0, NDF=38.0, ADF=24.0,
            EE=4.0, ASH=7.5, Ca=0.55, P=0.32,
            name_ar="تسمين عجول عادي", note="ADG ~0.8 كجم/يوم")
    elif production_type == "حمل_أخير":
        return AnimalRequirement(
            DP=11.5, CP=14.5, SE=67.0, NDF=35.0, ADF=22.0,
            EE=4.2, ASH=8.0, Ca=0.70, P=0.42,
            name_ar="حمل آخر (شهر 7-9)", note="دفع غذائي جنيني")
    else:
        return AnimalRequirement(
            DP=7.5, CP=10.0, SE=53.0, NDF=45.0, ADF=28.0,
            EE=3.0, ASH=8.5, Ca=0.42, P=0.26,
            name_ar="أبقار صيانة", note="بدون إنتاج")


# ─── الأغنام ──────────────────────────────────────────────────────────────
def get_sheep_requirements(production_type, is_male=True,
                            weight_kg=50.0, litter_size=1):
    if is_male:
        if production_type == "تسمين_مكثف":
            return AnimalRequirement(
                DP=11.5, CP=14.5, SE=64.0, NDF=28.0, ADF=17.0,
                EE=4.0, ASH=8.0, Ca=0.65, P=0.36,
                name_ar="تسمين حملان مكثف", note="ADG >250 جم/يوم")
        elif production_type == "تسمين_عادي":
            return AnimalRequirement(
                DP=9.5, CP=12.0, SE=59.0, NDF=33.0, ADF=21.0,
                EE=3.6, ASH=8.0, Ca=0.55, P=0.32,
                name_ar="تسمين حملان عادي", note="ADG ~180 جم/يوم")
        else:
            return AnimalRequirement(
                DP=8.5, CP=11.0, SE=55.0, NDF=38.0, ADF=24.0,
                EE=3.2, ASH=8.5, Ca=0.50, P=0.30,
                name_ar="حملان تيد", note="تسمين نهائي")
    else:
        if production_type == "مرضعات":
            dp = 10.5 + (litter_size - 1) * 1.5
            cp = dp / 0.72
            return AnimalRequirement(
                DP=round(dp, 2), CP=round(cp, 2),
                SE=round(60 + (litter_size - 1) * 5, 1),
                NDF=30.0, ADF=19.0, EE=4.5, ASH=8.5,
                Ca=round(0.65 + (litter_size - 1) * 0.10, 3),
                P=round(0.38 + (litter_size - 1) * 0.05, 3),
                name_ar=f"نعاج مرضعات ({litter_size} مواليد)",
                note="إنتاج حليب مرتفع")
        elif production_type == "حامل_أخير":
            return AnimalRequirement(
                DP=10.5, CP=13.5, SE=62.0, NDF=32.0, ADF=20.0,
                EE=3.8, ASH=8.0, Ca=0.60, P=0.35,
                name_ar="نعاج حامل (شهر 4-5)", note="تغذية جنين")
        elif production_type == "حامل_متوسط":
            return AnimalRequirement(
                DP=8.5, CP=11.0, SE=55.0, NDF=38.0, ADF=24.0,
                EE=3.4, ASH=8.0, Ca=0.50, P=0.30,
                name_ar="نعاج حامل (شهر 1-3)", note="نمو جنيني مبكر")
        else:
            return AnimalRequirement(
                DP=7.2, CP=9.5, SE=48.0, NDF=45.0, ADF=28.0,
                EE=3.0, ASH=8.5, Ca=0.42, P=0.26,
                name_ar="نعاج صيانة / جافة", note="بدون إنتاج")


# ─── الماعز ───────────────────────────────────────────────────────────────
def get_goat_requirements(production_type, is_male=True, milk_yield=2.0):
    if is_male:
        if production_type == "تسمين_جديان":
            return AnimalRequirement(
                DP=11.0, CP=14.0, SE=62.0, NDF=30.0, ADF=19.0,
                EE=3.8, ASH=8.0, Ca=0.62, P=0.34,
                name_ar="تسمين جديان", note="نمو سريع")
        else:
            return AnimalRequirement(
                DP=9.0, CP=11.5, SE=57.0, NDF=36.0, ADF=22.0,
                EE=3.5, ASH=8.0, Ca=0.55, P=0.30,
                name_ar="تيوس تسمين", note="تسمين نهائي")
    else:
        if production_type == "حلابة_عالي":
            dp = 11.5 + (milk_yield * 0.45)
            cp = dp / 0.70
            return AnimalRequirement(
                DP=round(dp, 2), CP=round(cp, 2),
                SE=round(58 + milk_yield * 0.45, 1),
                NDF=29.0, ADF=18.0, EE=4.5, ASH=8.5,
                Ca=round(0.60 + milk_yield * 0.008, 3),
                P=round(0.35 + milk_yield * 0.004, 3),
                name_ar=f"عنزات حلابة عالي ({milk_yield} كجم)",
                note="إدرار عالي")
        elif production_type == "حلابة_متوسط":
            dp = 10.0 + (milk_yield * 0.35)
            cp = dp / 0.72
            return AnimalRequirement(
                DP=round(dp, 2), CP=round(cp, 2),
                SE=round(55 + milk_yield * 0.40, 1),
                NDF=32.0, ADF=20.0, EE=4.0, ASH=8.5,
                Ca=round(0.55 + milk_yield * 0.006, 3),
                P=round(0.32 + milk_yield * 0.003, 3),
                name_ar=f"عنزات حلابة متوسط ({milk_yield} كجم)",
                note="إدرار متوسط")
        elif production_type == "حامل_أخير":
            return AnimalRequirement(
                DP=10.0, CP=13.0, SE=60.0, NDF=33.0, ADF=21.0,
                EE=3.8, ASH=8.0, Ca=0.60, P=0.35,
                name_ar="عنزات حامل", note="دفع غذائي")
        else:
            return AnimalRequirement(
                DP=6.8, CP=9.0, SE=46.0, NDF=46.0, ADF=28.0,
                EE=3.0, ASH=8.5, Ca=0.42, P=0.26,
                name_ar="عنزات صيانة", note="بدون إنتاج")


# ─── الإبل ────────────────────────────────────────────────────────────────
def get_camel_requirements(production_type, weight_kg=400.0, milk_yield=5.0):
    dm_kg = weight_kg * 0.025
    if production_type == "نمو":
        return AnimalRequirement(
            DP=10.5, CP=13.5, SE=60.0, NDF=38.0, ADF=24.0,
            EE=4.0, ASH=8.0, Ca=0.65, P=0.38,
            name_ar="إبل نمو (حوار)",
            note=f"وزن {weight_kg} كجم | DM {dm_kg:.1f} كجم/يوم")
    elif production_type == "تسمين":
        return AnimalRequirement(
            DP=9.5, CP=12.0, SE=65.0, NDF=35.0, ADF=22.0,
            EE=4.5, ASH=7.5, Ca=0.60, P=0.35,
            name_ar="إبل تسمين", note=f"وزن {weight_kg} كجم")
    elif production_type == "حليب":
        dp = 12.0 + (milk_yield * 0.25)
        cp = dp / 0.70
        return AnimalRequirement(
            DP=round(dp, 2), CP=round(cp, 2),
            SE=round(62 + milk_yield * 0.40, 1),
            NDF=32.0, ADF=20.0, EE=5.0, ASH=8.5,
            Ca=round(0.70 + milk_yield * 0.006, 3),
            P=round(0.40 + milk_yield * 0.003, 3),
            name_ar=f"إبل حلابة ({milk_yield} لتر)",
            note="دهن الحليب عالي (3-5%)")
    elif production_type == "سباق":
        return AnimalRequirement(
            DP=14.0, CP=17.0, SE=72.0, NDF=28.0, ADF=17.0,
            EE=6.0, ASH=9.0, Ca=0.85, P=0.50,
            name_ar="إبل سباق (هجن)", note="طاقة عالية")
    else:
        return AnimalRequirement(
            DP=7.0, CP=9.0, SE=48.0, NDF=48.0, ADF=30.0,
            EE=3.5, ASH=9.0, Ca=0.42, P=0.26,
            name_ar="إبل صيانة", note=f"وزن {weight_kg} كجم")


# ─── الخيول ──────────────────────────────────────────────────────────────
def get_horse_requirements(production_type, weight_kg=450.0):
    if production_type == "رياضة_مكثف":
        return AnimalRequirement(
            DP=10.5, CP=13.5, SE=70.0, NDF=30.0, ADF=18.0,
            EE=7.0, ASH=7.5, Ca=0.70, P=0.40,
            name_ar="خيول رياضة مكثف", note="جهد عالي + دهون عالية")
    elif production_type == "رياضة_عادي":
        return AnimalRequirement(
            DP=9.0, CP=11.5, SE=63.0, NDF=36.0, ADF=22.0,
            EE=5.0, ASH=7.5, Ca=0.55, P=0.32,
            name_ar="خيول رياضة عادي", note="نشاط متوسط")
    elif production_type == "نمو_أمهار":
        return AnimalRequirement(
            DP=12.0, CP=15.0, SE=65.0, NDF=30.0, ADF=18.0,
            EE=5.0, ASH=8.0, Ca=0.75, P=0.42,
            name_ar="أمهار نمو", note="نمو هيكلي")
    elif production_type == "مرضعات":
        return AnimalRequirement(
            DP=12.5, CP=16.0, SE=68.0, NDF=32.0, ADF=20.0,
            EE=5.5, ASH=8.0, Ca=0.80, P=0.45,
            name_ar="فرسات مرضعات", note="إنتاج حليب مرتفع")
    else:
        return AnimalRequirement(
            DP=7.2, CP=9.5, SE=53.0, NDF=46.0, ADF=29.0,
            EE=3.5, ASH=8.0, Ca=0.45, P=0.28,
            name_ar="خيول صيانة", note="بدون جهد")


# ─── الدواجن ─────────────────────────────────────────────────────────────
def get_poultry_requirements(strain, age_weeks=1):
    if strain == "لاحم":
        if age_weeks <= 1:
            return AnimalRequirement(
                DP=20.0, CP=23.0, SE=76.0, NDF=8.0, ADF=4.0,
                EE=5.0, ASH=6.5, Ca=1.00, P=0.50,
                name_ar="بادي لاحم (0-1 أسبوع)", note="Energy 3000 kcal/kg")
        elif age_weeks <= 3:
            return AnimalRequirement(
                DP=18.5, CP=21.0, SE=74.0, NDF=9.0, ADF=5.0,
                EE=5.0, ASH=6.0, Ca=0.90, P=0.45,
                name_ar="نامي لاحم (2-3 أسابيع)", note="Energy 3100 kcal/kg")
        elif age_weeks <= 5:
            return AnimalRequirement(
                DP=17.0, CP=19.5, SE=75.0, NDF=10.0, ADF=5.5,
                EE=4.5, ASH=6.0, Ca=0.87, P=0.43,
                name_ar="ناهي لاحم (4-5 أسابيع)", note="Energy 3150 kcal/kg")
        else:
            return AnimalRequirement(
                DP=16.5, CP=19.0, SE=75.0, NDF=10.0, ADF=5.5,
                EE=4.5, ASH=6.0, Ca=0.85, P=0.42,
                name_ar="ناهي لاحم (6+ أسابيع)", note="Energy 3200 kcal/kg")
    else:
        if age_weeks <= 6:
            return AnimalRequirement(
                DP=17.0, CP=20.0, SE=72.0, NDF=10.0, ADF=5.5,
                EE=4.0, ASH=7.0, Ca=1.00, P=0.50,
                name_ar="بادي بياض", note="تحضير للبيض")
        elif age_weeks <= 18:
            return AnimalRequirement(
                DP=14.5, CP=17.0, SE=70.0, NDF=12.0, ADF=6.5,
                EE=4.0, ASH=9.0, Ca=1.50, P=0.45,
                name_ar="نامي بياض", note="نمو هيكلي")
        else:
            return AnimalRequirement(
                DP=15.5, CP=18.0, SE=72.0, NDF=11.0, ADF=6.0,
                EE=4.2, ASH=11.5, Ca=3.80, P=0.45,
                name_ar="بياض إنتاجي", note="إنتاج بيض تجاري")


# ─── السمان ──────────────────────────────────────────────────────────────
def get_quail_requirements(strain, age_weeks=1):
    if strain == "بياض":
        return AnimalRequirement(
            DP=15.0, CP=18.0, SE=68.0, NDF=11.0, ADF=5.5,
            EE=4.5, ASH=9.0, Ca=2.50, P=0.45,
            name_ar="سمان بياض", note="إنتاج بيض السمان")
    else:
        if age_weeks <= 2:
            return AnimalRequirement(
                DP=20.5, CP=24.0, SE=74.0, NDF=8.0, ADF=4.0,
                EE=5.5, ASH=6.5, Ca=1.00, P=0.55,
                name_ar="سمان بادي", note="نمو سريع جداً")
        elif age_weeks <= 4:
            return AnimalRequirement(
                DP=18.5, CP=22.0, SE=72.0, NDF=9.0, ADF=4.5,
                EE=5.0, ASH=6.0, Ca=0.90, P=0.50,
                name_ar="سمان نامي", note="نمو متوسط")
        else:
            return AnimalRequirement(
                DP=17.0, CP=20.0, SE=70.0, NDF=10.0, ADF=5.0,
                EE=4.5, ASH=6.0, Ca=0.85, P=0.45,
                name_ar="سمان ناهي", note="تسمين نهائي")


# ─── الأسماك ─────────────────────────────────────────────────────────────
def get_fish_requirements(species, stage):
    if "زريعة" in stage or "بادئ" in stage:
        return AnimalRequirement(
            DP=32.0, CP=40.0, SE=72.0, NDF=8.0, ADF=4.0,
            EE=10.0, ASH=11.0, Ca=1.50, P=0.90,
            name_ar=f"{species} — بادئ زريعة", note="بروتين عالٍ جداً")
    elif "نمو" in stage:
        return AnimalRequirement(
            DP=25.0, CP=32.0, SE=70.0, NDF=12.0, ADF=6.0,
            EE=8.0, ASH=9.0, Ca=1.00, P=0.70,
            name_ar=f"{species} — نمو", note="بروتين متوسط")
    else:
        return AnimalRequirement(
            DP=22.0, CP=28.0, SE=68.0, NDF=13.0, ADF=7.0,
            EE=8.0, ASH=9.5, Ca=0.90, P=0.65,
            name_ar=f"{species} — تسمين", note="تركيز طاقة عالٍ")


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


def validate_oil_percentage(formula, standard_key):
    total_oil = compute_total_oil_percentage(formula)
    std = get_oil_standard(standard_key)
    status = "ok"
    if total_oil > std["max"]:
        status = "exceeded"
    elif total_oil > std["optimal"] * 1.2:
        status = "high"
    return {"total": total_oil, "max": std["max"],
            "optimal": std["optimal"], "source": std["source"],
            "status": status}


# ═════════════════════════════════════════════════════════════════════════════
# القسم 9: نظام التقييم
# ═════════════════════════════════════════════════════════════════════════════

def evaluate_difference(pct_diff):
    a = abs(pct_diff)
    if a <= 0.5:
        return {"label": "🎯 مطابق تماماً", "color": "#0d5302", "bg": "#c8e6c9", "score": 100}
    elif a <= 2.0:
        return {"label": "🌟 ممتاز", "color": "#1b5e20", "bg": "#dcedc8", "score": 95}
    elif a <= 5.0:
        return {"label": "✅ جيد جداً", "color": "#2e7d32", "bg": "#e8f5e9", "score": 85}
    elif a <= 10.0:
        return {"label": "🟢 جيد", "color": "#558b2f", "bg": "#f1f8e9", "score": 75}
    elif a <= 15.0:
        return {"label": "⭐ مقبول", "color": "#f9a825", "bg": "#fff8e1", "score": 65}
    elif a <= 25.0:
        return {"label": "⚠️ مقبول بتحفظ", "color": "#ef6c00", "bg": "#fff3e0", "score": 50}
    elif a <= 40.0:
        return {"label": "🟠 ضعيف", "color": "#e65100", "bg": "#ffe0b2", "score": 35}
    else:
        return {"label": "❌ غير مطابق", "color": "#c62828", "bg": "#ffebee", "score": 20}


def get_overall_rating(compare_rows):
    if not compare_rows:
        return {"label": "غير محدد", "color": "#666", "score": 0}
    scores = [r.get("score", 50) for r in compare_rows]
    avg = sum(scores) / len(scores)
    if avg >= 95:
        return {"label": "🏆 خلطة ممتازة", "color": "#1b5e20", "score": avg}
    elif avg >= 85:
        return {"label": "🌟 خلطة جيدة جداً", "color": "#2e7d32", "score": avg}
    elif avg >= 70:
        return {"label": "✅ خلطة جيدة", "color": "#558b2f", "score": avg}
    elif avg >= 55:
        return {"label": "⭐ خلطة مقبولة", "color": "#f9a825", "score": avg}
    else:
        return {"label": "⚠️ تحتاج تحسين", "color": "#e65100", "score": avg}


# ═════════════════════════════════════════════════════════════════════════════
# القسم 10: محرك التركيب الذكي
# ═════════════════════════════════════════════════════════════════════════════

def auto_formulate_smart(available_ingredients, prices, custom_standard,
                          standard_key, tolerance=0.3, max_iterations=50):
    """محرك التركيب الذكي — يطابق DP + SE + NDF + ADF + Ca + P + EE"""
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "مكتبة scipy غير مثبتة"}

    standard = custom_standard
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

    targets = {k: standard.get(k, 0) for k in ["DP", "SE", "NDF", "ADF", "Ca", "P"]}

    oil_std = get_oil_standard(standard_key)
    oil_max = oil_std["max"]
    oil_optimal = oil_std["optimal"]

    bounds = []
    for i in valid:
        if i in get_oil_ingredients():
            bounds.append((0.0, oil_max * 0.6))
        elif "يوريا" in i:
            bounds.append((0.0, 1.0))
        elif "مولاس" in i:
            bounds.append((0.0, 10.0))
        elif "ملح الطعام" in i:
            bounds.append((0.3, 0.7))
        elif "بيكربونات" in i:
            bounds.append((0.0, 1.5))
        elif "مضاد سموم" in i:
            bounds.append((0.05, 0.25))
        elif "بريمكس" in i:
            bounds.append((0.15, 0.5))
        elif "إنزيم" in i:
            bounds.append((0.02, 0.10))
        elif "الحجر الجيري" in i:
            bounds.append((0.0, 8.5))
        elif "فوسفات" in i:
            bounds.append((0.0, 2.5))
        elif "سرسة" in i:
            bounds.append((0.0, 8.0))
        elif "تبن" in i or "قش" in i:
            bounds.append((0.0, 25.0))
        else:
            bounds.append((0.0, 100.0))

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

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method='highs')

    if not res.success:
        for relax in [1.05, 1.10, 1.20, 1.30]:
            b_ub_r = [-1.0 * targets["SE"] * 100.0 * (2 - relax),
                      targets["NDF"] * relax * 100.0,
                      targets["ADF"] * relax * 100.0]
            if has_oils:
                b_ub_r.append(oil_max * 100.0)
            res = linprog(c, A_ub=A_ub, b_ub=b_ub_r, A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method='highs')
            if res.success:
                break

    if not res.success:
        return {"success": False, "message": "تعذر إيجاد حل — أضف مكونات متنوعة"}

    best = None
    best_score = float('inf')
    cur_dp, cur_se = targets["DP"], targets["SE"]
    cur_ndf, cur_adf = targets["NDF"], targets["ADF"]
    log = []

    for iteration in range(max_iterations):
        A_eq = [[1.0] * n, rows["DP"], rows["Ca"], rows["P"]]
        b_eq = [100.0, cur_dp * 100.0,
                targets["Ca"] * 100.0, targets["P"] * 100.0]
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
            log.append(f"تكرار {iteration+1}: تخفيف")
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

        log.append(f"تكرار {iteration+1}: DP={actual['DP']:.2f} "
                   f"SE={actual['SE']:.2f} EE={actual['EE']:.2f}")

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
                "total_oil": total_oil_actual,
                "oil_std": oil_std,
                "iterations": iteration + 1, "log": log[-10:], "targets": targets,
            }

        if (errors.get("DP", 1) * 100 <= tolerance and
            errors.get("SE", 1) * 100 <= tolerance * 2 and
            errors.get("NDF", 1) * 100 <= tolerance * 5 and
            errors.get("Ca", 1) * 100 <= tolerance * 15):
            log.append(f"✅ مطابقة كاملة في التكرار {iteration+1}")
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
        best["log"] = log
        return best
    return {"success": False, "message": "تعذر حل دقيق", "log": log}


def auto_add_salts_and_minerals(animal_type, requirement=None):
    salt = {}
    if animal_type in ["أغنام", "ماعز", "أبقار", "إبل"]:
        salt["بيكربونات الصوديوم (الصودا)"] = 0.75
    salt["مضاد سموم فطرية"] = 0.20
    salt["ملح الطعام"] = 0.50
    if animal_type in ["دواجن", "سمان"]:
        if requirement and requirement.Ca > 2.0:
            salt["الحجر الجيري (بودرة بلاط)"] = 8.0
        else:
            salt["الحجر الجيري (بودرة بلاط)"] = 1.5
        salt["فوسفات ثنائي الكالسيوم (DCP)"] = 1.5
        salt["بريمكس تسمين دواجن (Premix)"] = 0.30
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


def get_recommended_oils(standard_key):
    std = get_oil_standard(standard_key)
    recommended = []
    for cat, oils in OIL_CATEGORIES.items():
        for oil in oils:
            oil_data = get_oil_ingredients().get(oil, {})
            if oil_data:
                max_for_animal = oil_data.get(
                    "max_poultry", oil_data.get("max_ruminant", 5.0))
                recommended.append({
                    "oil": oil, "category": cat,
                    "SE": oil_data.get("SE", 0),
                    "max_animal": max_for_animal,
                    "desc": oil_data.get("desc", ""),
                })
    return recommended
    # ═════════════════════════════════════════════════════════════════════════════
# القسم 11: بدائل الحليب
# ═════════════════════════════════════════════════════════════════════════════

MILK_REPLACER_STANDARDS = {
    "عجول (Calves)": {"CP": 24.0, "Fat": 24.0, "Lactose": 45.0,
                      "Lysine": 2.1, "Ca": 0.75, "P": 0.70,
                      "Fiber_max": 0.15, "Ash_max": 10.0,
                      "notes": "عمر 1-6 أسابيع، مادة جافة 12-15%"},
    "حملان (Lambs)": {"CP": 24.0, "Fat": 24.0, "Lactose": 40.0,
                      "Lysine": 2.1, "Ca": 0.80, "P": 0.70,
                      "Fiber_max": 0.15, "Ash_max": 10.0,
                      "notes": "≥ 24% دهن"},
    "جديان (Goat Kids)": {"CP": 24.0, "Fat": 24.0, "Lactose": 42.0,
                          "Lysine": 2.1, "Ca": 0.80, "P": 0.70,
                          "Fiber_max": 0.15, "Ash_max": 10.0,
                          "notes": "بديل الجديان"},
    "إبل (Camel Calves)": {"CP": 26.0, "Fat": 28.0, "Lactose": 38.0,
                           "Lysine": 2.3, "Ca": 0.85, "P": 0.75,
                           "Fiber_max": 0.10, "Ash_max": 9.0,
                           "notes": "بروتين ودهن أعلى"},
    "أمهار (Foals)": {"CP": 22.0, "Fat": 20.0, "Lactose": 45.0,
                      "Lysine": 1.9, "Ca": 0.90, "P": 0.80,
                      "Fiber_max": 0.15, "Ash_max": 9.0,
                      "notes": "توازن للخيول"},
}

MILK_REPLACER_INGREDIENTS = {
    "حليب مجفف منزوع الدسم": {"CP": 34.0, "Fat": 1.0, "Lactose": 52.0, "price": 3200},
    "حليب مجفف كامل الدسم": {"CP": 26.0, "Fat": 28.0, "Lactose": 38.0, "price": 3800},
    "شرش حليب مجفف": {"CP": 12.0, "Fat": 1.5, "Lactose": 75.0, "price": 1800},
    "بروتين شرش WPC 80%": {"CP": 80.0, "Fat": 5.0, "Lactose": 8.0, "price": 8500},
    "كازين": {"CP": 85.0, "Fat": 2.0, "Lactose": 2.0, "price": 9000},
    "مركز بروتين صويا": {"CP": 66.0, "Fat": 1.0, "Lactose": 0.0, "price": 2800},
    "دقيق الصويا": {"CP": 38.0, "Fat": 20.0, "Lactose": 0.0, "price": 1500},
    "زيت جوز الهند": {"CP": 0.0, "Fat": 100.0, "Lactose": 0.0, "price": 2200},
    "زيت النخيل": {"CP": 0.0, "Fat": 100.0, "Lactose": 0.0, "price": 1200},
    "دهن حيواني": {"CP": 0.0, "Fat": 100.0, "Lactose": 0.0, "price": 1000},
    "مالتودكسترين": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "price": 900},
    "لاكتوز نقي": {"CP": 0.0, "Fat": 0.0, "Lactose": 100.0, "price": 1400},
    "ليسين L-Lysine": {"CP": 94.0, "Fat": 0.0, "Lactose": 0.0, "price": 4200},
    "ميثيونين": {"CP": 58.0, "Fat": 0.0, "Lactose": 0.0, "price": 5800},
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
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
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
# القسم 12: OCR المختبر الذكي
# ═════════════════════════════════════════════════════════════════════════════

def match_ingredient_name(text):
    if not text:
        return None
    tl = text.strip().lower()
    for cat in BIG_FEEDS_LIBRARY.values():
        for name in cat.keys():
            if name.lower() in tl or tl in name.lower():
                return name
    kw = {"ذرة": "ذرة صفراء", "corn": "ذرة صفراء",
          "صويا": "كسب فول صويا 44%", "شعير": "شعير مطحون",
          "قمح": "قمح محلي", "سورجم": "سورجم (فتريتة)",
          "نخالة": "نخالة قمح (ردة)", "فول سوداني": "أمباز الفول السوداني (كسب)",
          "قطن": "كسب بذور القطن (مقشور)", "عباد": "كسب عباد الشمس 36%",
          "سمسم": "كسب السمسم المحسن", "جلوتين": "كسب جلوتين الذرة 60%",
          "سمك": "مسحوق أسماك 60%", "لحم": "مسحوق اللحم والعظم",
          "دم": "مسحوق الدم", "ليسين": "ليسين نقي (L-Lysine)",
          "ميثيونين": "ميثيونين نقي (DL-Methionine)",
          "ملح": "ملح الطعام",
          "حجر": "الحجر الجيري (بودرة بلاط)",
          "فوسفات": "فوسفات ثنائي الكالسيوم (DCP)",
          "بيكربونات": "بيكربونات الصوديوم (الصودا)",
          "مولاس": "مولاس قصب السكر",
          "برسيم": "البرسيم الجاف (الدريس)", "تبن": "تبن قمح",
          "يوريا": "يوريا علفية محصنة", "زيت": "زيت فول الصويا"}
    for k, m in kw.items():
        if k in tl:
            return m
    return None


def extract_ingredients_from_image(image_bytes):
    if not OCR_AVAILABLE:
        return {"success": False, "message": "pytesseract غير مثبتة"}
    if not CV2_AVAILABLE:
        return {"success": False, "message": "opencv غير مثبتة"}
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"success": False, "message": "تعذر قراءة الصورة"}
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)
        t1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 11, 2)
        _, t2 = cv2.threshold(gray, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        texts = []
        for t in [t1, t2, gray]:
            try:
                txt = pytesseract.image_to_string(
                    t, lang='ara+eng', config=r'--oem 3 --psm 6')
                if txt.strip():
                    texts.append(txt)
            except Exception:
                continue
        if not texts:
            return {"success": False, "message": "لم يتم استخراج نص"}
        full = "\n".join(texts)
        ingredients = {}
        for line in full.split('\n'):
            line = line.strip()
            if len(line) < 3:
                continue
            for pat in [
                r'([\u0600-\u06FFa-zA-Z\s\(\)%]+?)[\s:\-=]+(\d+\.?\d*)\s*%',
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
                "raw_text": full, "count": len(ingredients)}
    except Exception as e:
        return {"success": False, "message": f"خطأ: {str(e)}"}


# ═════════════════════════════════════════════════════════════════════════════
# القسم 13: قاعدة البيانات المتقدمة (SQLite)
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
            is_active INTEGER DEFAULT 1, is_public INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS farms (
            farm_id TEXT PRIMARY KEY, farm_name TEXT UNIQUE, farm_type TEXT,
            owner_name TEXT, owner_phone TEXT, location TEXT, area REAL,
            created_date TEXT, last_updated TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS production_cycles (
            cycle_id TEXT PRIMARY KEY, farm_id TEXT, cycle_type TEXT,
            start_date TEXT, end_date TEXT, initial_count INTEGER, breed TEXT,
            target_weight REAL, target_age INTEGER, status TEXT, notes TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS daily_records (
            record_id TEXT PRIMARY KEY, cycle_id TEXT, record_date TEXT,
            age_days INTEGER, live_birds INTEGER, avg_weight REAL,
            min_weight REAL, max_weight REAL, feed_consumed REAL,
            water_consumed REAL, dead_count INTEGER, culled_count INTEGER,
            temperature REAL, humidity REAL, ventilation_status TEXT,
            litter_quality TEXT, feed_conversion REAL, mortality_rate REAL,
            notes TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS health_records (
            health_id TEXT PRIMARY KEY, cycle_id TEXT, record_date TEXT,
            age_days INTEGER, treatment_type TEXT, treatment_name TEXT,
            dose REAL, dose_unit TEXT, administration_route TEXT,
            administered_by TEXT, notes TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS vaccine_alerts (
            alert_id TEXT PRIMARY KEY, cycle_id TEXT, alert_date TEXT,
            scheduled_date TEXT, vaccine_name TEXT, vaccine_type TEXT,
            dose TEXT, route TEXT, status TEXT, sent BOOLEAN DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas (
            formula_id TEXT PRIMARY KEY, formula_name TEXT, animal_type TEXT,
            breed TEXT, stage TEXT, target_dp REAL, target_se REAL,
            ingredients TEXT, total_cost REAL, cost_per_ton REAL,
            created_by TEXT, created_date TEXT, is_approved INTEGER DEFAULT 0,
            usage_count INTEGER DEFAULT 0, requester_name TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS invoices (
            invoice_id TEXT PRIMARY KEY, customer_name TEXT,
            customer_phone TEXT, customer_address TEXT, formula_id TEXT,
            quantity_ton REAL, unit_price REAL, total_price REAL,
            discount REAL DEFAULT 0, tax REAL DEFAULT 0, final_price REAL,
            status TEXT, payment_method TEXT, created_by TEXT,
            created_date TEXT, due_date TEXT, notes TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS price_history (
            record_id TEXT PRIMARY KEY, ingredient_name TEXT, price REAL,
            currency TEXT, country TEXT, city TEXT, record_date TEXT,
            recorded_by TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT PRIMARY KEY, item_name TEXT UNIQUE, quantity REAL,
            min_threshold REAL, unit TEXT, last_updated TEXT, supplier TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS lab_results (
            result_id TEXT PRIMARY KEY, sample_name TEXT, sample_type TEXT,
            cp REAL, dc REAL, se REAL, ndf REAL, adf REAL, ee REAL,
            ash REAL, moisture REAL, analysis_date TEXT, analyzed_by TEXT,
            notes TEXT, image_path TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS milk_replacers (
            replacer_id TEXT PRIMARY KEY, animal_type TEXT, age_days INTEGER,
            formula_name TEXT, ingredients TEXT, instructions TEXT,
            created_by TEXT, created_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS dose_reminders (
            reminder_id TEXT PRIMARY KEY, animal_type TEXT, dose_type TEXT,
            dose_name TEXT, dose_amount REAL, dose_unit TEXT,
            administration_route TEXT, frequency_days INTEGER,
            start_date TEXT, next_dose_date TEXT, notes TEXT,
            active BOOLEAN DEFAULT 1, created_by TEXT, created_date TEXT)''')
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

    def update_record(self, table, data, condition):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        set_clause = ', '.join([f"{k}=?" for k in data.keys()])
        where = ' AND '.join([f"{k}=?" for k in condition.keys()])
        c.execute(f"UPDATE {table} SET {set_clause} WHERE {where}",
                  list(data.values()) + list(condition.values()))
        conn.commit()
        conn.close()
        return True

    def delete_record(self, table, condition):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        where = ' AND '.join([f"{k}=?" for k in condition.keys()])
        c.execute(f"DELETE FROM {table} WHERE {where}",
                  list(condition.values()))
        conn.commit()
        conn.close()
        return True


# ═════════════════════════════════════════════════════════════════════════════
# القسم 14: نظام إدارة المزارع
# ═════════════════════════════════════════════════════════════════════════════

class FarmManagementSystem:
    def __init__(self):
        self.db = DatabaseManager()

    def create_farm(self, farm_name, farm_type, owner_name, owner_phone,
                     location="", area=0.0):
        farm_id = secrets.token_hex(16)
        data = {'farm_id': farm_id, 'farm_name': farm_name,
                'farm_type': farm_type, 'owner_name': owner_name,
                'owner_phone': owner_phone, 'location': location,
                'area': area, 'created_date': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()}
        self.db.insert_record('farms', data)
        return farm_id

    def create_production_cycle(self, farm_id, cycle_type, initial_count,
                                 breed, target_weight=0.0, target_age=0):
        cycle_id = secrets.token_hex(16)
        data = {'cycle_id': cycle_id, 'farm_id': farm_id,
                'cycle_type': cycle_type,
                'start_date': datetime.now().isoformat(), 'end_date': '',
                'initial_count': initial_count, 'breed': breed,
                'target_weight': target_weight, 'target_age': target_age,
                'status': 'active', 'notes': ''}
        self.db.insert_record('production_cycles', data)
        return cycle_id

    def add_daily_record(self, cycle_id, record_data):
        record_id = secrets.token_hex(16)
        live_birds = record_data.get('live_birds', 0)
        avg_weight = record_data.get('avg_weight', 0)
        feed_consumed = record_data.get('feed_consumed', 0)
        dead_count = record_data.get('dead_count', 0)
        initial_count = record_data.get('initial_count',
                                         live_birds + dead_count)
        total_gain = live_birds * avg_weight
        feed_conversion = feed_consumed / total_gain if total_gain > 0 else 0
        mortality_rate = (dead_count / initial_count) * 100 if initial_count > 0 else 0
        data = {'record_id': record_id, 'cycle_id': cycle_id,
                'record_date': datetime.now().isoformat(),
                'age_days': record_data.get('age_days', 0),
                'live_birds': live_birds, 'avg_weight': avg_weight,
                'min_weight': record_data.get('min_weight', avg_weight * 0.9),
                'max_weight': record_data.get('max_weight', avg_weight * 1.1),
                'feed_consumed': feed_consumed,
                'water_consumed': record_data.get('water_consumed', 0),
                'dead_count': dead_count,
                'culled_count': record_data.get('culled_count', 0),
                'temperature': record_data.get('temperature', 0),
                'humidity': record_data.get('humidity', 0),
                'ventilation_status': record_data.get('ventilation_status', 'جيدة'),
                'litter_quality': record_data.get('litter_quality', 'جيدة'),
                'feed_conversion': feed_conversion,
                'mortality_rate': mortality_rate,
                'notes': record_data.get('notes', '')}
        self.db.insert_record('daily_records', data)
        return record_id

    def get_performance_summary(self, cycle_id):
        records = self.db.get_records('daily_records', {'cycle_id': cycle_id})
        if not records:
            return None
        latest_record = records[-1]
        first_record = records[0]
        total_dead = sum(r[11] for r in records)
        total_culled = sum(r[12] for r in records)
        initial_count = first_record[5] if first_record else 0
        summary = {'total_days': latest_record[3],
                   'final_weight': latest_record[5],
                   'total_feed': sum(r[9] for r in records),
                   'total_dead': total_dead, 'total_culled': total_culled,
                   'mortality_rate': (total_dead / initial_count * 100) if initial_count > 0 else 0,
                   'final_livability': ((initial_count - total_dead - total_culled) / initial_count * 100) if initial_count > 0 else 0,
                   'avg_fcr': sum(r[15] for r in records) / len(records) if records else 0}
        livability = summary['final_livability']
        final_weight = summary['final_weight']
        total_days = summary['total_days']
        avg_fcr = summary['avg_fcr']
        epef = (livability * final_weight) / (total_days * avg_fcr) * 100 if total_days > 0 and avg_fcr > 0 else 0
        summary['epef'] = epef
        return summary


# ═════════════════════════════════════════════════════════════════════════════
# القسم 15: نظام المصادقة
# ═════════════════════════════════════════════════════════════════════════════

class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self._create_default_users()

    def _create_default_users(self):
        default_users = [
            ('admin', 'admin123', 'owner',
             'الاختصاصي م. عبد القادر إسماعيل تاور',
             'admin@tawornology.com', '+249123456789',
             'تغذية حيوان', 10),
            ('specialist', 'spec123', 'specialist', 'المختص العام',
             'specialist@tawornology.com', '+249123456788',
             'تغذية وإنتاج', 8),
            ('nutritionist', 'nutri123', 'nutritionist', 'أخصائي التغذية',
             'nutrition@tawornology.com', '+249123456786',
             'تغذية حيوان', 7),
            ('veterinarian', 'vet123', 'veterinarian', 'الطبيب البيطري',
             'vet@tawornology.com', '+249123456785',
             'طب بيطري', 9),
        ]
        for u in default_users:
            users = self.db.execute_query(
                "SELECT * FROM users WHERE username=?", (u[0],))
            if not users:
                self.create_user(*u)

    def create_user(self, username, password, role, full_name, email,
                     phone, specialty="", experience=0):
        user_id = secrets.token_hex(16)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        data = {'user_id': user_id, 'username': username,
                'password_hash': password_hash, 'role': role,
                'full_name': full_name, 'email': email, 'phone': phone,
                'specialty': specialty, 'experience_years': experience,
                'created_date': datetime.now().isoformat(), 'last_login': '',
                'is_active': 1, 'is_public': 1 if role == 'public' else 0}
        self.db.insert_record('users', data)
        return user_id

    def authenticate(self, username, password):
        users = self.db.execute_query(
            "SELECT * FROM users WHERE username=? AND is_active=1",
            (username,))
        if users:
            user = users[0]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user[2] == password_hash:
                self.db.update_record(
                    'users', {'last_login': datetime.now().isoformat()},
                    {'user_id': user[0]})
                return {'user_id': user[0], 'username': user[1],
                        'role': user[3], 'full_name': user[4],
                        'email': user[5], 'phone': user[6],
                        'specialty': user[7], 'experience_years': user[8]}
        return None


# ═════════════════════════════════════════════════════════════════════════════
# القسم 16: نظام التنبؤ بالأسعار
# ═════════════════════════════════════════════════════════════════════════════

class PricePredictor:
    def __init__(self):
        self.db = DatabaseManager()

    def get_price_trend(self, ingredient_name, days=30):
        results = self.db.execute_query(
            "SELECT * FROM price_history WHERE ingredient_name=? "
            "ORDER BY record_date DESC LIMIT ?",
            (ingredient_name, days))
        if len(results) < 3:
            return {'trend': 'stable', 'change_percent': 0,
                    'volatility': 0, 'current_price': None}
        prices = [r[2] for r in results]
        x = np.array(range(len(prices))).reshape(-1, 1)
        y = np.array(prices)
        if SKLEARN_AVAILABLE:
            model = LinearRegression()
            model.fit(x, y)
            slope = model.coef_[0]
        else:
            slope = 0
        change_percent = ((prices[0] - prices[-1]) / prices[-1]) * 100 if prices[-1] > 0 else 0
        trend = 'up' if slope > 0.5 else ('down' if slope < -0.5 else 'stable')
        return {'trend': trend, 'change_percent': change_percent,
                'volatility': np.std(prices) / np.mean(prices) if np.mean(prices) > 0 else 0,
                'current_price': prices[0]}

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
        trend = (price_list[0] - price_list[-1]) / len(price_list) if len(price_list) > 1 else 0
        prediction = weighted_avg + (trend * days_ahead)
        return {'prediction': max(0, prediction),
                'confidence': min(1, len(price_list) / 30),
                'current_price': price_list[0] if price_list else None,
                'trend': trend}


# ═════════════════════════════════════════════════════════════════════════════
# القسم 17: نظام المختبر الذكي
# ═════════════════════════════════════════════════════════════════════════════

class SmartLabSystem:
    def __init__(self):
        self.db = DatabaseManager()
        self.ocr_available = OCR_AVAILABLE or EASYOCR_AVAILABLE
        self.reader = None
        if EASYOCR_AVAILABLE:
            try:
                self.reader = easyocr.Reader(['ar', 'en'], gpu=False)
            except Exception:
                self.reader = None

    def analyze_image(self, image):
        if not self.ocr_available:
            return None, "مكتبات OCR غير مثبتة"
        results = []
        try:
            if EASYOCR_AVAILABLE and self.reader:
                result = self.reader.readtext(np.array(image))
                for (bbox, text, prob) in result:
                    if prob > 0.3:
                        results.append(text)
            elif OCR_AVAILABLE:
                img = PILImage.open(image) if not isinstance(
                    image, PILImage_module.Image) else image
                text = pytesseract.image_to_string(img, lang='ara+eng')
                results = text.split('\n')
            return self._parse_ocr_results(results), None
        except Exception as e:
            return None, f"خطأ في تحليل الصورة: {str(e)}"

    def _parse_ocr_results(self, texts):
        data = {'sample_name': '', 'cp': None, 'dc': None, 'se': None,
                'ndf': None, 'adf': None, 'ee': None, 'ash': None,
                'moisture': None}
        patterns = {
            'cp': [r'بروتين\s*خام\s*[:=]?\s*([\d.]+)',
                   r'CP\s*[:=]?\s*([\d.]+)'],
            'dc': [r'معامل\s*الهضم\s*[:=]?\s*([\d.]+)',
                   r'DC\s*[:=]?\s*([\d.]+)'],
            'se': [r'معادل\s*النشاء\s*[:=]?\s*([\d.]+)',
                   r'SE\s*[:=]?\s*([\d.]+)'],
            'ndf': [r'NDF\s*[:=]?\s*([\d.]+)'],
            'adf': [r'ADF\s*[:=]?\s*([\d.]+)'],
            'ee': [r'دهن\s*خام\s*[:=]?\s*([\d.]+)',
                   r'EE\s*[:=]?\s*([\d.]+)'],
            'ash': [r'رماد\s*[:=]?\s*([\d.]+)',
                    r'ASH\s*[:=]?\s*([\d.]+)'],
            'moisture': [r'رطوبة\s*[:=]?\s*([\d.]+)'],
        }
        for text in texts:
            text_clean = text.strip()
            if 'اسم' in text_clean and not data['sample_name']:
                parts = text_clean.split(':')
                if len(parts) > 1:
                    data['sample_name'] = parts[1].strip()
            for key, pattern_list in patterns.items():
                if data[key] is None:
                    for pattern in pattern_list:
                        match = re.search(pattern, text_clean, re.IGNORECASE)
                        if match:
                            try:
                                data[key] = float(match.group(1))
                                break
                            except Exception:
                                pass
        return data

    def save_lab_result(self, result_data):
        result_id = secrets.token_hex(16)
        data = {'result_id': result_id,
                'sample_name': result_data.get('sample_name', ''),
                'sample_type': result_data.get('sample_type', ''),
                'cp': result_data.get('cp', 0.0),
                'dc': result_data.get('dc', 0.0),
                'se': result_data.get('se', 0.0),
                'ndf': result_data.get('ndf', 0.0),
                'adf': result_data.get('adf', 0.0),
                'ee': result_data.get('ee', 0.0),
                'ash': result_data.get('ash', 0.0),
                'moisture': result_data.get('moisture', 0.0),
                'analysis_date': datetime.now().isoformat(),
                'analyzed_by': result_data.get('analyzed_by', ''),
                'notes': result_data.get('notes', ''),
                'image_path': result_data.get('image_path', '')}
        self.db.insert_record('lab_results', data)
        return result_id

    def get_lab_results(self, limit=50):
        return self.db.execute_query(
            "SELECT * FROM lab_results ORDER BY analysis_date DESC LIMIT ?",
            (limit,))


# ═════════════════════════════════════════════════════════════════════════════
# القسم 18: المراجع العلمية
# ═════════════════════════════════════════════════════════════════════════════

class ScientificReferenceSystem:
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان", "icon": "📚",
            "references": [
                {"id": "REF001",
                 "authors": "McDonald, P., Edwards, R.A., Greenhalgh, J.F.D.",
                 "year": 2011, "title": "Animal Nutrition",
                 "publisher": "Pearson Education", "edition": "7th Edition",
                 "summary": "المرجع الأساسي في تغذية الحيوان."},
                {"id": "REF002",
                 "authors": "Cheeke, P.R., Dierenfeld, E.S.", "year": 2010,
                 "title": "Comparative Animal Nutrition and Metabolism",
                 "publisher": "CABI",
                 "summary": "مقارنة بين آليات التغذية والتمثيل الغذائي."}
            ]
        },
        "protein_amino_acids": {
            "title": "البروتين والأحماض الأمينية", "icon": "🧬",
            "references": [
                {"id": "REF003", "authors": "NRC (National Research Council)",
                 "year": 2012, "title": "Nutrient Requirements of Swine",
                 "publisher": "National Academies Press",
                 "summary": "المرجع الرسمي لمتطلبات الخنازير."},
                {"id": "REF004", "authors": "NRC (National Research Council)",
                 "year": 2001,
                 "title": "Nutrient Requirements of Dairy Cattle",
                 "publisher": "National Academies Press",
                 "summary": "المرجع الأساسي في تغذية أبقار الحليب."}
            ]
        },
        "energy_carbohydrates": {
            "title": "الطاقة والكربوهيدرات", "icon": "⚡",
            "references": [
                {"id": "REF006", "authors": "Van Soest, P.J.", "year": 1994,
                 "title": "Nutritional Ecology of the Ruminant",
                 "publisher": "Cornell University Press",
                 "summary": "المرجع الكلاسيكي في تغذية المجترات."}
            ]
        },
        "minerals_vitamins": {
            "title": "المعادن والفيتامينات", "icon": "🪨",
            "references": [
                {"id": "REF008",
                 "authors": "Underwood, E.J., Suttle, N.F.", "year": 1999,
                 "title": "The Mineral Nutrition of Livestock",
                 "publisher": "CABI",
                 "summary": "المرجع الشامل في تغذية المعادن."}
            ]
        },
        "poultry": {
            "title": "تغذية الدواجن", "icon": "🐔",
            "references": [
                {"id": "REF010", "authors": "Leeson, S., Summers, J.D.",
                 "year": 2009, "title": "Commercial Poultry Nutrition",
                 "publisher": "Nottingham University Press",
                 "summary": "المرجع العملي في تغذية الدواجن."},
                {"id": "REF011", "authors": "NRC (National Research Council)",
                 "year": 1994,
                 "title": "Nutrient Requirements of Poultry",
                 "publisher": "National Academies Press",
                 "summary": "المرجع الرسمي لمتطلبات الدواجن."}
            ]
        },
        "ruminants": {
            "title": "تغذية المجترات", "icon": "🐄",
            "references": [
                {"id": "REF012", "authors": "Church, D.C.", "year": 1993,
                 "title": "The Ruminant Animal",
                 "publisher": "Waveland Press",
                 "summary": "المرجع الشامل في فسيولوجيا الهضم للمجترات."}
            ]
        },
        "sheep_goats": {
            "title": "تغذية الأغنام والماعز", "icon": "🐏",
            "references": [
                {"id": "REF014", "authors": "NRC (National Research Council)",
                 "year": 2007,
                 "title": "Nutrient Requirements of Small Ruminants",
                 "publisher": "National Academies Press",
                 "summary": "المرجع الرسمي لمتطلبات الأغنام والماعز."}
            ]
        },
        "horses": {
            "title": "تغذية الخيول", "icon": "🐴",
            "references": [
                {"id": "REF015", "authors": "NRC (National Research Council)",
                 "year": 2007,
                 "title": "Nutrient Requirements of Horses",
                 "publisher": "National Academies Press",
                 "summary": "المرجع الأساسي في تغذية الخيول."}
            ]
        },
        "camels": {
            "title": "تغذية الإبل", "icon": "🐫",
            "references": [
                {"id": "REF030", "authors": "Faye, B., Bengoumi, M.",
                 "year": 2018, "title": "Camel Nutrition and Feeding",
                 "publisher": "FAO",
                 "summary": "المرجع الأساسي في تغذية الإبل."}
            ]
        },
        "aquaculture": {
            "title": "تغذية الأسماك", "icon": "🐟",
            "references": [
                {"id": "REF016", "authors": "Halver, J.E., Hardy, R.W.",
                 "year": 2002, "title": "Fish Nutrition",
                 "publisher": "Academic Press",
                 "summary": "المرجع الشامل في تغذية الأسماك."}
            ]
        },
        "broiler": {
            "title": "إنتاج الدجاج اللاحم", "icon": "🐔",
            "references": [
                {"id": "REF020",
                 "authors": "Ross 308 Broiler Management Guide", "year": 2020,
                 "title": "Ross Broiler Management Handbook",
                 "publisher": "Aviagen",
                 "summary": "الدليل الشامل لإدارة الدجاج اللاحم."}
            ]
        },
        "oils": {
            "title": "الزيوت والدهون في الأعلاف", "icon": "🌰",
            "references": [
                {"id": "REF050",
                 "authors": "Palmquist, D.L.", "year": 2006,
                 "title": "Milk Fat Depression in Dairy Cows",
                 "publisher": "Journal of Dairy Science",
                 "summary": "المرجع الأساسي لمشكلة انخفاض دهن الحليب."},
                {"id": "REF051", "authors": "NRC", "year": 2012,
                 "title": "Fat in Animal Nutrition",
                 "publisher": "National Academies Press",
                 "summary": "فصل الزيوت في تغذية الحيوان."}
            ]
        },
    }

    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً.",
            "reference": "REF023",
            "simplified": "البروتين المهضوم هو الجزء من البروتين الذي يستفيد منه الحيوان."},
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (SE) هو مقياس لكمية الطاقة التي يوفرها العلف.",
            "reference": "REF006",
            "simplified": "معادل النشاء يقيس كمية الطاقة في العلف."},
        "كيف يتم تركيب العلف الأمثل": {
            "answer": "يتم تركيب العلف الأمثل باستخدام محرك الاستمثال الخطي (Linear Programming).",
            "reference": "REF024",
            "simplified": "نستخدم برنامجاً ذكياً يحسب أرخص خلطة علفية."},
        "ما هو EPEF": {
            "answer": "مؤشر الأداء الأوروبي EPEF = (الحيوية × الوزن الحي) / (العمر × معامل التحويل) × 100.",
            "reference": "REF020",
            "simplified": "EPEF يعبر عن كفاءة مزرعة الدجاج."},
        "كيف يتم تركيب بديل الحليب": {
            "answer": "يتم تركيب بديل الحليب باستخدام مصل الحليب والدهون النباتية والفيتامينات.",
            "reference": "REF040",
            "simplified": "بديل الحليب هو خليط سائل يحاكي تركيب الحليب الطبيعي."},
        "ما هي الزيوت المناسبة للدواجن": {
            "answer": "زيت فول الصويا (حتى 8%) وزيت الذرة (حتى 6%) هي الأفضل للدواجن.",
            "reference": "REF020",
            "simplified": "زيت الصويا والذرة ممتازان للدواجن."},
        "لماذا تتجنب بعض الزيوت في المجترات": {
            "answer": "الزيوت غير المشبعة بكميات كبيرة تسبب انخفاض دهن الحليب (Milk Fat Depression).",
            "reference": "REF050",
            "simplified": "الإكثار من الزيوت يقلل دهن الحليب في الأبقار."},
    }

    @staticmethod
    def get_reference(ref_id):
        for category in ScientificReferenceSystem.REFERENCES.values():
            for ref in category.get("references", []):
                if ref.get("id") == ref_id:
                    return ref
        return None

    @staticmethod
    def get_knowledge_answer(question):
        question_lower = question.lower()
        for key, value in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            if key in question_lower:
                return {"answer": value["answer"],
                        "simplified": value.get("simplified", value["answer"])}
        return None


# ═════════════════════════════════════════════════════════════════════════════
# القسم 19: المعادلات الإنتاجية المتقدمة (NRC)
# ═════════════════════════════════════════════════════════════════════════════

class AdvancedProductionEquations:
    @staticmethod
    def calculate_milk_protein_requirement(milk_yield_kg,
                                            milk_protein_pct=3.3):
        return (milk_yield_kg * (milk_protein_pct / 100)) / 0.65

    @staticmethod
    def calculate_maintenance_protein(weight_kg):
        return 2.5 * (weight_kg ** 0.75)

    @staticmethod
    def calculate_metabolic_protein(weight_kg):
        return 1.2 * (weight_kg ** 0.75)

    @staticmethod
    def calculate_total_protein_for_dairy(weight_kg, milk_yield_kg,
                                            milk_fat_pct=3.5,
                                            milk_protein_pct=3.3):
        maintenance = AdvancedProductionEquations.calculate_maintenance_protein(weight_kg)
        metabolic = AdvancedProductionEquations.calculate_metabolic_protein(weight_kg)
        production = AdvancedProductionEquations.calculate_milk_protein_requirement(
            milk_yield_kg, milk_protein_pct)
        total = maintenance + metabolic + production
        return {'maintenance': maintenance, 'metabolic': metabolic,
                'production': production, 'total': total,
                'dp_requirement': (total / (weight_kg * 10)) * 100}

    @staticmethod
    def calculate_energy_for_dairy(weight_kg, milk_yield_kg,
                                     milk_fat_pct=3.5):
        maintenance = 0.08 * (weight_kg ** 0.75)
        fat_correction = 1 + 0.15 * (milk_fat_pct - 3.5)
        production = 5.3 * milk_yield_kg * fat_correction
        total = maintenance + production
        return {'maintenance_energy': maintenance,
                'production_energy': production,
                'total_energy': total, 'se_requirement': total * 10}

    @staticmethod
    def calculate_protein_for_gain(daily_gain_kg,
                                     protein_in_gain_pct=18.0):
        return (daily_gain_kg * (protein_in_gain_pct / 100)) / 0.65

    @staticmethod
    def calculate_energy_for_gain(daily_gain_kg, gain_energy_pct=5.0):
        return (daily_gain_kg * gain_energy_pct) / 0.70


# ═════════════════════════════════════════════════════════════════════════════
# القسم 20: الرسوم البيانية للـ PDF
# ═════════════════════════════════════════════════════════════════════════════

def create_colorful_bar_chart(standard, actual):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        nutrients = ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH"]
        nutrients = [n for n in nutrients if n in standard]
        if not nutrients:
            return None
        std_vals = [standard[n] for n in nutrients]
        act_vals = [actual.get(n, 0) for n in nutrients]
        fig, ax = plt.subplots(figsize=(9, 4.5))
        x = np.arange(len(nutrients))
        width = 0.35
        bars1 = ax.bar(x - width/2, std_vals, width,
                       label='المعيار القياسي', color='#1976d2',
                       edgecolor='#0d47a1', linewidth=1.5)
        bars2 = ax.bar(x + width/2, act_vals, width,
                       label='القيمة المحسوبة', color='#43a047',
                       edgecolor='#1b5e20', linewidth=1.5)
        for bar in bars1:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h, f'{h:.1f}',
                    ha='center', va='bottom', fontsize=9,
                    color='#0d47a1', fontweight='bold')
        for bar in bars2:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h, f'{h:.1f}',
                    ha='center', va='bottom', fontsize=9,
                    color='#1b5e20', fontweight='bold')
        ax.set_xlabel('العنصر الغذائي', fontsize=11, fontweight='bold')
        ax.set_ylabel('القيمة', fontsize=11, fontweight='bold')
        ax.set_title('مقارنة العناصر الغذائية', fontsize=13,
                     fontweight='bold', color='#1b5e20')
        ax.set_xticks(x)
        ax.set_xticklabels(nutrients, fontsize=10)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_facecolor('#fafafa')
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
                  '#43a047', '#7cb342', '#fdd835', '#fb8c00', '#6d4c41',
                  '#c62828', '#6a1b9a', '#283593', '#0277bd', '#00695c',
                  '#004d40', '#3e2723', '#bf360c', '#e65100', '#ff6f00']
        names = list(formula.keys())
        vals = list(formula.values())
        fig, ax = plt.subplots(figsize=(8, 5))
        wedges, texts, autotexts = ax.pie(
            vals, autopct='%1.1f%%', colors=colors[:len(names)],
            startangle=90, pctdistance=0.75,
            wedgeprops=dict(edgecolor='white', linewidth=2))
        for t in autotexts:
            t.set_color('white')
            t.set_fontweight('bold')
            t.set_fontsize(9)
        ax.legend(names, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
                  fontsize=9, title="المكونات", title_fontsize=10)
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
        nutrients = ["CP", "DP", "SE", "NDF", "ADF", "EE", "Ca", "P"]
        nutrients = [n for n in nutrients
                     if n in standard and standard[n] > 0]
        if len(nutrients) < 3:
            return None
        std_norm = [100.0 for _ in nutrients]
        act_norm = [(actual.get(n, 0) / standard[n]) * 100
                    for n in nutrients]
        angles = np.linspace(0, 2 * np.pi, len(nutrients),
                              endpoint=False).tolist()
        std_norm += std_norm[:1]
        act_norm += act_norm[:1]
        angles += angles[:1]
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, std_norm, 'o-', linewidth=2.5, color='#1976d2',
                label='المعيار (100%)')
        ax.fill(angles, std_norm, alpha=0.15, color='#1976d2')
        ax.plot(angles, act_norm, 'o-', linewidth=2.5, color='#43a047',
                label='المحسوب')
        ax.fill(angles, act_norm, alpha=0.25, color='#43a047')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(nutrients, fontsize=10)
        ax.set_ylim(0, max(max(std_norm), max(act_norm)) * 1.2)
        ax.set_title('المقارنة الشاملة %', fontsize=12,
                     fontweight='bold', color='#1b5e20', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#fafafa')
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
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect='equal'))
        colors_g = ['#c62828', '#ef6c00', '#f9a825', '#7cb342',
                    '#43a047', '#1b5e20']
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
        ax.text(0, -0.5, 'التقييم العام', ha='center', fontsize=11,
                color='#666')
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.7, 1.2)
        ax.axis('off')
        ax.set_facecolor('white')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


# ═════════════════════════════════════════════════════════════════════════════
# القسم 21: مولد PDF الاحترافي
# ═════════════════════════════════════════════════════════════════════════════

class PDFGenerator:
    def __init__(self):
        self.font_name = font_mgr.font_name
        self.font_bold = font_mgr.font_bold
        self.logo_path = None
        for lp in LOGO_OPTIONS + PHOTO_OPTIONS:
            if os.path.exists(lp):
                self.logo_path = lp
                break

    def _ar(self, text):
        if text is None:
            return ""
        try:
            reshaped = arabic_reshaper.reshape(str(text))
            return get_display(reshaped, base_dir='R')
        except Exception:
            return str(text)

    def _draw_page(self, canvas_obj, doc):
        canvas_obj.saveState()
        w, h = doc.pagesize
        canvas_obj.setFillColor(HexColor('#e8f5e9'))
        canvas_obj.setFont(self.font_name, 60)
        try:
            canvas_obj.setFillAlpha(0.07)
        except Exception:
            pass
        canvas_obj.saveState()
        canvas_obj.translate(w/2, h/2)
        canvas_obj.rotate(45)
        canvas_obj.drawCentredString(0, 0, self._ar("تاور نولجي"))
        canvas_obj.restoreState()
        try:
            canvas_obj.setFillAlpha(1)
        except Exception:
            pass
        canvas_obj.setFillColor(HexColor('#1b5e20'))
        canvas_obj.rect(0, h-90, w, 90, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor('#d4af37'))
        canvas_obj.rect(0, h-95, w, 5, fill=1, stroke=0)
        try:
            if self.logo_path:
                canvas_obj.drawImage(self.logo_path, 30, h-78,
                                      width=60, height=60,
                                      preserveAspectRatio=True,
                                      anchor='sw', mask='auto')
        except Exception:
            pass
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

        canvas_obj.setFillColor(HexColor('#1b5e20'))
        canvas_obj.rect(0, 42, w, 42, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor('#d4af37'))
        canvas_obj.rect(0, 84, w, 3, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor('#ffeb3b'))
        canvas_obj.setFont(self.font_name, 10)
        canvas_obj.drawCentredString(w/2, 68, self._ar(f"🤲 {DUA_SHORT} 🤲"))
        canvas_obj.setFillColor(HexColor('#c8e6c9'))
        canvas_obj.setFont(self.font_name, 8)
        canvas_obj.drawCentredString(w/2, 52,
            self._ar("اللهم اجعل قبرهما روضة من رياض الجنة"))

        canvas_obj.setFillColor(HexColor('#1b5e20'))
        canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)
        canvas_obj.setFillColor(white)
        canvas_obj.setFont(self.font_name, 8)
        canvas_obj.drawCentredString(w/2, 27,
            self._ar("تاور نولجي Tawor Nology © 2026"))
        canvas_obj.setFont(self.font_name, 7)
        canvas_obj.drawCentredString(w/2, 12,
            self._ar(f"صفحة {canvas_obj.getPageNumber()} | جميع الحقوق محفوظة"))

        if QRCODE_AVAILABLE:
            try:
                qr = qrcode.QRCode(version=1, box_size=3, border=1)
                qr.add_data(PLATFORM_URL)
                qr.make(fit=True)
                qi = qr.make_image(fill_color="#1b5e20", back_color="white")
                buf = io.BytesIO()
                qi.save(buf, format="PNG")
                buf.seek(0)
                canvas_obj.drawImage(RLImage(buf), w/2-20, 46,
                                      width=40, height=40)
            except Exception:
                pass

        sx, sy = w - 105, 145
        canvas_obj.setStrokeColor(HexColor('#c62828'))
        canvas_obj.setLineWidth(3.0)
        canvas_obj.circle(sx, sy, 70, stroke=1, fill=0)
        canvas_obj.setLineWidth(1.5)
        canvas_obj.circle(sx, sy, 62, stroke=1, fill=0)
        canvas_obj.setLineWidth(0.6)
        canvas_obj.circle(sx, sy, 56, stroke=1, fill=0)
        canvas_obj.setFillColor(HexColor('#c62828'))
        canvas_obj.setFont(self.font_name, 9)
        canvas_obj.drawCentredString(sx, sy+40, self._ar("تاور نولجي"))
        canvas_obj.drawCentredString(sx, sy+28, self._ar("Tawor Nology"))
        canvas_obj.setFont(self.font_name, 7.5)
        canvas_obj.drawCentredString(sx, sy+10, self._ar("م. عبدالقادر"))
        canvas_obj.drawCentredString(sx, sy-1, self._ar("إسماعيل تاور"))
        canvas_obj.setFont(self.font_name, 6)
        canvas_obj.drawCentredString(sx, sy-17,
            self._ar("اختصاصي تغذية الحيوان"))
        canvas_obj.drawCentredString(sx, sy-30, self._ar("معتمد رسمياً"))
        canvas_obj.drawCentredString(sx, sy-42, self._ar("© 2026"))
        canvas_obj.restoreState()

    def _comparison_table(self, standard, calculated):
        labels = {"CP": "بروتين خام CP", "DP": "بروتين مهضوم DP",
                  "SE": "معادل النشاء SE", "NDF": "ألياف NDF",
                  "ADF": "ألياف ADF", "EE": "دهن EE", "ASH": "رماد ASH",
                  "Ca": "كالسيوم Ca", "P": "فسفور P"}
        header = [self._ar(x) for x in
                  ["العنصر", "المعيار", "المحسوب", "الفرق",
                   "الفرق %", "التقييم"]]
        data = [header]
        cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#9e9e9e')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
        ]
        row = 1
        for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
            if k not in standard:
                continue
            sv = standard[k]
            cv = calculated.get(k, 0.0)
            diff = cv - sv
            pct = (diff / sv * 100) if sv else 0
            ev = evaluate_difference(pct)
            unit = "%" if k in ("CP", "DP", "NDF", "ADF", "EE",
                                 "ASH", "Ca", "P") else ""
            data.append([
                self._ar(labels.get(k, k)),
                f"{sv:.2f}{unit}", f"{cv:.2f}{unit}",
                f"{diff:+.3f}", f"{pct:+.2f}%",
                self._ar(ev["label"])])
            cmds.append(('BACKGROUND', (0, row), (-1, row),
                         HexColor(ev["bg"])))
            cmds.append(('TEXTCOLOR', (5, row), (5, row),
                         HexColor(ev["color"])))
            row += 1
        t = Table(data, colWidths=[100, 70, 70, 70, 70, 105])
        t.setStyle(TableStyle(cmds))
        return t

    def _oil_table(self, formula, standard_key):
        oils = get_oil_ingredients()
        oil_rows = []
        for ing, pct in formula.items():
            if ing in oils:
                oil_rows.append([ing, pct])
        if not oil_rows:
            return None
        oil_std = get_oil_standard(standard_key)
        total_oil = sum(p for _, p in oil_rows)
        header = [self._ar("الزيت"), self._ar("النسبة %"),
                  self._ar("kcal/kg تقديري")]
        data = [header]
        for ing, pct in oil_rows:
            kcal = pct * 90.0
            data.append([self._ar(ing), f"{pct:.2f}%", f"{kcal:.0f}"])
        data.append([self._ar("الإجمالي"), f"{total_oil:.2f}%",
                     f"{total_oil * 90:.0f}"])
        cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e65100')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bf360c')),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#ffe0b2')),
            ('TEXTCOLOR', (0, -1), (-1, -1), HexColor('#bf360c')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]
        t = Table(data, colWidths=[250, 100, 135])
        t.setStyle(TableStyle(cmds))
        return t, total_oil, oil_std

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

        story.append(P("تقرير فني رسمي — تركيب علفة", size=20,
                       align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
                                color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))

        client_data = [
            [self._ar("👤 اسم طالب الخدمة:"),
             self._ar(requester_name or "........................")],
            [self._ar("📍 الموقع:"), self._ar(city)],
            [self._ar("🐾 الفصيل:"), self._ar(f"{animal_type} — {breed}")],
            [self._ar("🧬 أساس الحساب:"),
             self._ar("البروتين المهضوم DP" if protein_basis == "DP"
                      else "البروتين الخام CP")],
            [self._ar("📅 تاريخ الإصدار:"),
             datetime.now().strftime('%Y-%m-%d | %H:%M')],
        ]
        ct = Table(client_data, colWidths=[150, 340])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
            ('BACKGROUND', (1, 0), (1, -1), HexColor('#fafafa')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')),
            ('INNERGRID', (0, 0), (-1, -1), 0.6, HexColor('#c8e6c9')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ]))
        story.append(ct)
        story.append(Spacer(1, 15))

        standard_vals = requirement_to_standard(requirement)
        calculated_vals = compute_formula_nutrients(formula)

        scores = []
        for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
            if k not in standard_vals:
                continue
            sv = standard_vals[k]
            cv = calculated_vals.get(k, 0.0)
            pct = ((cv - sv) / sv * 100) if sv else 0
            scores.append({"score": evaluate_difference(pct)["score"]})
        overall = get_overall_rating(scores)

        story.append(P("📊 جدول مقارنة العناصر الغذائية", size=14,
                       align=TA_RIGHT, color='#1b5e20'))
        story.append(Spacer(1, 8))
        story.append(self._comparison_table(standard_vals, calculated_vals))
        story.append(Spacer(1, 12))

        summary_data = [
            [self._ar("التقييم العام"), self._ar("عدد المطابقة"),
             self._ar("المتوسط")],
            [self._ar(overall["label"]),
             f"{sum(1 for s in scores if s['score'] >= 85)}/{len(scores)}",
             f"{overall['score']:.0f}%"],
        ]
        st_tbl = Table(summary_data, colWidths=[160, 165, 165])
        st_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565c0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#e3f2fd')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#1976d2')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(st_tbl)
        story.append(Spacer(1, 15))

        oil_result = self._oil_table(formula, standard_key)
        if oil_result:
            oil_tbl, total_oil, oil_std = oil_result
            story.append(P("🌰 جدول الزيوت النباتية والحيوانية", size=14,
                           align=TA_RIGHT, color='#e65100'))
            story.append(Spacer(1, 8))
            story.append(oil_tbl)
            story.append(Spacer(1, 8))
            oil_note = (f"الحد الأقصى المسموح: {oil_std['max']}% | "
                        f"المثالي: {oil_std['optimal']}% | "
                        f"المرجع: {oil_std['source']}")
            if total_oil > oil_std['max']:
                oil_note = f"⚠️ تجاوز الحد الأقصى! {oil_note}"
            elif total_oil > oil_std['optimal'] * 1.2:
                oil_note = f"⚡ مرتفع قليلاً — {oil_note}"
            else:
                oil_note = f"✅ مطابق — {oil_note}"
            story.append(P(oil_note, size=10, align=TA_RIGHT,
                           color='#bf360c'))
            story.append(Spacer(1, 15))

        if include_charts:
            story.append(P("📈 الرسوم البيانية", size=14,
                           align=TA_RIGHT, color='#1b5e20'))
            story.append(Spacer(1, 10))
            c1 = create_colorful_bar_chart(standard_vals, calculated_vals)
            if c1:
                story.append(RLImage(c1, width=450, height=250))
                story.append(Spacer(1, 12))
            c2 = create_colorful_pie_chart(formula)
            c3 = create_radar_chart(standard_vals, calculated_vals)
            if c2 and c3:
                row = [[RLImage(c2, width=210, height=200),
                        RLImage(c3, width=210, height=200)]]
                rt = Table(row, colWidths=[230, 230])
                rt.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(rt)
                story.append(Spacer(1, 12))
            elif c2:
                story.append(RLImage(c2, width=350, height=280))
                story.append(Spacer(1, 12))
            gauge = create_gauge_chart(overall["score"])
            if gauge:
                story.append(P("🎯 مؤشر التقييم", size=12,
                               align=TA_CENTER, color='#1b5e20'))
                story.append(RLImage(gauge, width=200, height=200))
                story.append(Spacer(1, 12))

        story.append(PageBreak())

        story.append(P("💰 التكاليف", size=14, align=TA_RIGHT,
                       color='#1b5e20'))
        story.append(Spacer(1, 8))
        cost_data = [
            [self._ar("البند"), self._ar("القيمة")],
            [self._ar("التكلفة للطن (دولار)"), f"${cost:.2f}"],
            [self._ar(f"التكلفة ({local_sym})"), f"{local_cost:,.2f}"],
            [self._ar("البروتين المستهدف"),
             f"{requirement.DP if protein_basis == 'DP' else requirement.CP:.2f}%"],
            [self._ar("الدهن EE"), f"{calculated_vals['EE']:.2f}%"],
        ]
        tc = Table(cost_data, colWidths=[280, 210])
        tc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f5f5f5')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#2e7d32')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(tc)
        story.append(Spacer(1, 18))

        if formula:
            story.append(P("🌾 المكونات للطن", size=14,
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
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                 [HexColor('#ffffff'), HexColor('#f5f5f5')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(ti)
            story.append(Spacer(1, 25))

        sign = [
            [self._ar("توقيع طالب الخدمة"), self._ar("توقيع المختص")],
            [self._ar("........................"), self._ar(SUPERVISOR)],
            [self._ar("التاريخ: ..../..../........"),
             self._ar(SUPERVISOR_TITLE)],
        ]
        ts = Table(sign, colWidths=[245, 245])
        ts.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f5e9')),
        ]))
        story.append(ts)

        doc.build(story, onFirstPage=self._draw_page,
                  onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_lab_report(self, analysis_results, animal_type, stage,
                             user_name, standard=None, evaluation=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
            rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text),
                ParagraphStyle('s', fontName=self.font_name, fontSize=size,
                    alignment=align, textColor=HexColor(color),
                    spaceAfter=6, leading=size * 1.6))

        story.append(P("🔬 تقرير التحليل المخبري المتقدم", size=18,
                       align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 10))
        story.append(P(f"🐾 الحيوان: {animal_type} | المرحلة: {stage}"))
        story.append(P(f"📅 تاريخ التحليل: {datetime.now().strftime('%Y-%m-%d %H:%M')}"))
        story.append(Spacer(1, 15))

        if analysis_results:
            story.append(P("📊 النتائج المحسوبة:", size=14,
                           align=TA_RIGHT, color='#1b5e20'))
            rows = [[self._ar("العنصر"), self._ar("القيمة")]]
            for k, label in [("cp", "CP"), ("dp", "DP"), ("se", "SE")]:
                if k in analysis_results:
                    rows.append([self._ar(label),
                                 f"{analysis_results[k]:.2f}"])
            t = Table(rows, colWidths=[250, 250])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565C0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#1565C0')),
            ]))
            story.append(t)

        story.append(Spacer(1, 25))
        story.append(P("الاختصاصي م. عبد القادر إسماعيل تاور", size=12))
        story.append(P(SUPERVISOR_TITLE, size=10))
        doc.build(story, onFirstPage=self._draw_page,
                  onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_milk_replacer_report(self, formula, animal_type, age_days,
                                        instructions, user_name):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
            rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text),
                ParagraphStyle('s', fontName=self.font_name, fontSize=size,
                    alignment=align, textColor=HexColor(color),
                    spaceAfter=6, leading=size * 1.6))

        story.append(P("🍼 تقرير تركيب بديل الحليب", size=18,
                       align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 10))
        story.append(P(f"🐾 نوع الحيوان: {animal_type}"))
        story.append(P(f"📅 العمر (يوم): {age_days}"))
        story.append(Spacer(1, 15))

        rows = [[self._ar("المكون"), self._ar("النسبة %"),
                 self._ar("جم/كجم")]]
        for ing, pct in formula.items():
            rows.append([self._ar(ing), f"{pct:.2f}%", f"{pct*10:.1f}"])
        t = Table(rows, colWidths=[240, 130, 130])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))
        story.append(P("📌 تعليمات التقديم:", size=13))
        for line in instructions.split('\n'):
            if line.strip():
                story.append(P(f"• {line.strip()}"))
        doc.build(story, onFirstPage=self._draw_page,
                  onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()


pdf_gen = PDFGenerator()


# ═════════════════════════════════════════════════════════════════════════════
# القسم 22: تصدير Excel
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
    tf = Font(name='Arial', size=14, bold=True, color='1B5E20')
    ct = Alignment(horizontal='center', vertical='center', wrap_text=True)
    rt = Alignment(horizontal='right', vertical='center', wrap_text=True)
    thin = Side(border_style='thin', color='9E9E9E')
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)

    ws.merge_cells('A1:F1')
    ws['A1'] = f"{APP_NAME}"
    ws['A1'].font = tf
    ws['A1'].alignment = ct
    ws.merge_cells('A2:F2')
    ws['A2'] = f"🤲 {DUA_SHORT} 🤲"
    ws['A2'].font = Font(name='Arial', size=10, bold=True, color='C62828')
    ws['A2'].alignment = ct
    ws['A4'] = "طالب:"
    ws['A4'].font = Font(bold=True)
    ws['A4'].alignment = rt
    ws.merge_cells('B4:D4')
    ws['B4'] = requester_name
    ws['E4'] = "التاريخ:"
    ws['E4'].font = Font(bold=True)
    ws['E4'].alignment = rt
    ws['F4'] = datetime.now().strftime('%Y-%m-%d')

    headers = ["العنصر", "المعيار", "المحسوب", "الفرق", "% الفرق", "التقييم"]
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=6, column=c, value=h)
        cell.font = hf
        cell.fill = hfill
        cell.alignment = ct
        cell.border = bd

    labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم",
              "SE": "معادل النشاء", "NDF": "NDF", "ADF": "ADF",
              "EE": "دهن", "ASH": "رماد",
              "Ca": "كالسيوم", "P": "فسفور"}
    row = 7
    for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
        if k not in standard:
            continue
        sv = standard[k]
        cv = calculated.get(k, 0.0)
        diff = cv - sv
        pct = (diff / sv * 100) if sv else 0
        ev = evaluate_difference(pct)
        vals = [labels[k], round(sv, 2), round(cv, 2),
                round(diff, 3), round(pct, 2), ev["label"]]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.alignment = ct
            cell.border = bd
            cell.fill = PatternFill('solid',
                                     fgColor=ev["bg"].replace('#', ''))
        row += 1

    if formula:
        oil_rows = [(ing, pct) for ing, pct in formula.items()
                    if ing in get_oil_ingredients()]
        if oil_rows:
            row += 2
            ws.merge_cells(start_row=row, start_column=1,
                           end_row=row, end_column=6)
            ws.cell(row=row, column=1,
                    value="🌰 الزيوت المستخدمة").font = tf
            ws.cell(row=row, column=1).alignment = ct
            row += 1
            for c, h in enumerate(["الزيت", "النسبة %",
                                    "kcal/kg", "", "", ""], 1):
                cell = ws.cell(row=row, column=c, value=h)
                cell.font = hf
                cell.fill = PatternFill('solid', fgColor='E65100')
                cell.alignment = ct
                cell.border = bd
            row += 1
            for ing, pct in oil_rows:
                ws.cell(row=row, column=1, value=ing).border = bd
                ws.cell(row=row, column=1).alignment = rt
                ws.cell(row=row, column=2, value=round(pct, 2)).border = bd
                ws.cell(row=row, column=2).alignment = ct
                ws.cell(row=row, column=3, value=round(pct * 90, 0)).border = bd
                ws.cell(row=row, column=3).alignment = ct
                row += 1

    for c in range(1, 7):
        ws.column_dimensions[get_column_letter(c)].width = 22
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


# ═════════════════════════════════════════════════════════════════════════════
# القسم 23: السوق والأسعار
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
        "ذرة صفراء": 230, "ذرة بيضاء": 225, "شعير مطحون": 210,
        "سورجم (فتريتة)": 195, "قمح محلي": 240,
        "أمباز الفول السوداني (كسب)": 460, "كسب فول صويا 44%": 440,
        "كسب فول صويا 48%": 480, "كسب عباد الشمس 36%": 310,
        "كسب بذور القطن (مقشور)": 290, "نخالة قمح (ردة)": 150,
        "البرسيم الجاف (الدريس)": 170, "مولاس قصب السكر": 120,
        "مسحوق أسماك 60%": 850, "مركزات دواجن وسمان": 650,
        "مركزات خيول ومجترات": 600, "الحجر الجيري (بودرة بلاط)": 40,
        "فوسفات ثنائي الكالسيوم (DCP)": 280, "ملح الطعام": 30,
        "بيكربونات الصوديوم (الصودا)": 340,
        "مضاد سموم فطرية": 950,
        "بريمكس تسمين دواجن (Premix)": 4800,
        "بريمكس مجترات": 4500,
        "ليسين نقي (L-Lysine)": 4200,
        "ميثيونين نقي (DL-Methionine)": 5800,
        "زيت ذرة": 1500, "زيت فول الصويا": 1350,
        "زيت عباد الشمس": 1300, "زيت بذرة القطن": 1400,
        "زيت الكتان": 1700, "زيت جوز الهند": 1900,
        "زيت النخيل": 1100, "زيت الكانولا": 1450,
        "زيت السمسم": 2100, "زيت الزيتون": 3500,
        "زيت الأفوكادو": 4200, "زيت القرطم": 1800,
        "زيت الفول السوداني": 2200,
        "شحم حيواني (Tallow)": 900, "دهن الدجاج": 800,
        "زيت السمك (Fish Oil)": 3800,
    })
    m = 1.0
    if country == "السودان":
        m = 1.15
        if "كردفان" in state:
            m = 1.20
    elif country == "LIBYA":
        m = 1.10
    elif country == "مصر":
        m = 1.04
    elif country == "السعودية":
        m = 1.08
    elif country == "الإمارات":
        m = 1.12
    return {k: v * m for k, v in base.items()}


# ═════════════════════════════════════════════════════════════════════════════
# القسم 24: مدير المخزون
# ═════════════════════════════════════════════════════════════════════════════

class InventoryManager:
    @staticmethod
    def initialize_inventory():
        if "inventory" not in st.session_state or not st.session_state["inventory"]:
            st.session_state["inventory"] = {}
            for cat_name, items in BIG_FEEDS_LIBRARY.items():
                for ing in items:
                    st.session_state["inventory"][ing] = {
                        "quantity": 25.0, "min_threshold": 5.0,
                        "unit": "طن",
                        "last_updated": datetime.now().isoformat(),
                        "supplier": "غير محدد"
                    }

    @staticmethod
    def check_stock_levels():
        warnings = {}
        for item, data in st.session_state["inventory"].items():
            qty = data if isinstance(data, (int, float)) else data["quantity"]
            threshold = 5.0 if isinstance(data, (int, float)) else data.get("min_threshold", 5.0)
            if qty <= 0:
                warnings[item] = {"status": "نفذ المخزون", "level": "critical"}
            elif qty < threshold:
                warnings[item] = {"status": "منخفض", "level": "warning"}
        return warnings

    @staticmethod
    def get_stock_summary():
        inv = st.session_state.get("inventory", {})
        total_items = len(inv)
        total_quantity = sum(
            d["quantity"] if isinstance(d, dict) else d
            for d in inv.values())
        low_stock = sum(
            1 for d in inv.values()
            if (d["quantity"] if isinstance(d, dict) else d) <
               (d.get("min_threshold", 5.0) if isinstance(d, dict) else 5.0))
        return {"total_items": total_items,
                "total_quantity": total_quantity,
                "low_stock": low_stock}


# ═════════════════════════════════════════════════════════════════════════════
# القسم 25: نظام التنبيهات والجرعات
# ═════════════════════════════════════════════════════════════════════════════

def get_vaccine_schedule(animal_type, age_days):
    schedules = {
        "دواجن": {
            1: {"type": "فيتامين", "name": "فيتامين AD3E",
                "dose": "1 مل/لتر", "route": "مياه الشرب"},
            7: {"type": "لقاح", "name": "نيوكاسل (Lasota)",
                "dose": "قطرة عين", "route": "قطرة عين/أنف"},
            14: {"type": "لقاح", "name": "Gumboro (Intermediate)",
                 "dose": "قطرة فم", "route": "مياه الشرب"},
            21: {"type": "دواء", "name": "مضاد كوكسيديا (Amprolium)",
                 "dose": "1 جم/لتر", "route": "مياه الشرب"},
            28: {"type": "فيتامين", "name": "فيتامين C + E",
                 "dose": "0.5 جم/لتر", "route": "مياه الشرب"},
            35: {"type": "لقاح", "name": "Gumboro booster",
                 "dose": "قطرة فم", "route": "مياه الشرب"},
            42: {"type": "لقاح", "name": "نيوكاسل (بخاخ)",
                 "dose": "بخاخ", "route": "رش"},
        },
        "أبقار": {
            30: {"type": "لقاح", "name": "الحمى القلاعية",
                 "dose": "2 مل", "route": "عضل"},
            60: {"type": "لقاح", "name": "الجمرة الخبيثة",
                 "dose": "1 مل", "route": "تحت الجلد"},
            90: {"type": "دواء", "name": "إزالة الطفيليات الداخلية",
                 "dose": "حسب الوزن", "route": "فموي"},
            180: {"type": "لقاح", "name": "حمى الوادي المتصدع",
                  "dose": "2 مل", "route": "عضل"},
        },
        "أغنام": {
            15: {"type": "فيتامين", "name": "فيتامين E + Se",
                 "dose": "1 مل", "route": "عضل"},
            30: {"type": "لقاح", "name": "طاعون المجترات الصغيرة",
                 "dose": "1 مل", "route": "تحت الجلد"},
            60: {"type": "دواء", "name": "مضاد طفيليات",
                 "dose": "حسب الوزن", "route": "فموي"},
        },
    }
    return schedules.get(animal_type, {})


# ═════════════════════════════════════════════════════════════════════════════
# القسم 26: الحالة الأولية + الصور + الصوت
# ═════════════════════════════════════════════════════════════════════════════

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


# ─── دوال الصوت ─────────────────────────────────────────────────────────────
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
                word_count = len(msg.split())
                duration = max(2.0, word_count * 0.3 + 1.0)
                time.sleep(duration)
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
        "منصة الإنتاج الحيواني وتركيب الأعلاف."
    ])


def play_dua_audio():
    voice_guide_sequential([
        "اللهم اغفر لإسماعيل تاور وابتسام،",
        "وارحمهما وأدخلهما فسيح جناتك."
    ])


def play_full_guide_audio():
    messages = [
        "مرحباً بك في منصة تاور نولجي Tawor Nology العلمية،",
        "هذه المنصة متخصصة في الإنتاج الحيواني وتركيب الأعلاف.",
        "أقسامها الرئيسية:",
        "القسم الأول: تركيب الأعلاف لثمانية أنواع من الحيوانات.",
        "القسم الثاني: مكتبة الزيوت النباتية والحيوانية.",
        "القسم الثالث: بدائل الحليب لرضاعة الصغار.",
        "القسم الرابع: المختبر الذكي لتحليل الصور.",
        "القسم الخامس: إدارة المزارع والإنتاج.",
        "القسم السادس: المستودعات والفواتير.",
        "القسم السابع: مواقيت الصلاة ومنبه الجرعات.",
        "جميع التقارير قابلة للتحميل بصيغة PDF مع توقيع المشرف.",
        "نسأل الله التوفيق والسداد."
    ]
    voice_guide_sequential(messages, delay_between=2.5)


# ─── إرسال الكود بالبريد ────────────────────────────────────────────────────
def send_code_to_email(receiver_email):
    if receiver_email.strip().lower() != OWNER_EMAIL.strip().lower():
        return False, "❌ عذراً، الإرسال مسموح فقط للبريد: " + OWNER_EMAIL
    if not st.session_state.get("email_password"):
        return False, "⚠️ يرجى إعداد App Password في secrets.toml"
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception:
        code_content = "# تعذر قراءة الكود"
    file_hash = hashlib.md5(code_content.encode()).hexdigest()
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = f"🌾 السورس كود - {APP_NAME}"
    body = f"""السلام عليكم ورحمة الله وبركاته،

مرفق السورس كود الكامل لمنصة {APP_NAME}.

📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔑 التوقيع الرقمي: {file_hash}
👨‍💻 المشرف: {SUPERVISOR} - {SUPERVISOR_TITLE}
🕊️ {DUA_SHORT}
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    attachment = MIMEText(code_content, 'plain', 'utf-8')
    attachment.add_header('Content-Disposition', 'attachment',
                          filename="tawornology_platform_v18.py")
    msg.attach(attachment)
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, st.session_state["email_password"])
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True, "✅ تم إرسال الكود بنجاح إلى " + receiver_email
    except Exception as e:
        return False, f"❌ فشل الإرسال: {str(e)}"


# ═════════════════════════════════════════════════════════════════════════════
# القسم 27: تهيئة الجلسة
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
    "livestock_prices": {
        "عجول تسمين هولشتاين ($)": 1350.0,
        "أبقار كنانة ($)": 900.0,
        "ضأن محلي ($)": 180.0,
        "ماعز نوبي ($)": 130.0,
        "إبل حاشي ($)": 1200.0,
        "كتكوت لاحم يوم ($)": 0.65,
        "دجاج بياض ($)": 5.50,
    },
    "products_prices": {
        "كيلو لحم بقري ($)": 7.50,
        "كيلو لحم ضأن ($)": 9.00,
        "كيلو لحم إبل ($)": 8.50,
        "كيلو لحم دجاج ($)": 3.80,
        "طبق بيض 30 ($)": 4.20,
        "لتر حليب بقر ($)": 0.90,
        "لتر حليب إبل ($)": 3.50,
    },
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

InventoryManager.initialize_inventory()

if "smart_lab_system" not in st.session_state:
    try:
        st.session_state["smart_lab_system"] = SmartLabSystem()
    except Exception:
        st.session_state["smart_lab_system"] = None

farm_system = FarmManagementSystem()


def is_owner():
    return st.session_state.get("user_role") == "owner"


# ═════════════════════════════════════════════════════════════════════════════
# نهاية الجزء 2/3
# ═════════════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════════════
# القسم 28: CSS المتقدم مع الدعاء المتحرك
# ═════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');
* { font-family: 'Cairo', 'Amiri', sans-serif; color: #1a1a1a !important; }
html, body, [data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600");
    background-size: cover; background-position: center;
    background-attachment: fixed;
}
.stApp { background: transparent; }
.main-box {
    background-color: rgba(255, 255, 255, 0.98);
    padding: 30px; border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
    margin-bottom: 60px; backdrop-filter: blur(5px);
}
h1, h2, h3, h4, h5, p, span, li, div, label { color: #1a1a1a !important; }

@keyframes duaGlow {
    0%, 100% { box-shadow: 0 15px 40px rgba(0,0,0,0.4),
               inset 0 0 30px rgba(212,175,55,0.2); }
    50% { box-shadow: 0 15px 40px rgba(0,0,0,0.5),
          inset 0 0 40px rgba(212,175,55,0.4),
          0 0 80px rgba(212,175,55,0.5); }
}
@keyframes floatIcon {
    0%, 100% { transform: translateY(0) rotate(0); }
    50% { transform: translateY(-12px) rotate(6deg); }
}
@keyframes gradientShift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}
@keyframes shimmerText {
    0% { background-position: -500% 0; }
    100% { background-position: 500% 0; }
}
@keyframes pulseHeart {
    0%, 100% { transform: scale(1); color: #ff6b6b; }
    50% { transform: scale(1.5); color: #ff1744; }
}
@keyframes fixedDuaGlow {
    0%, 100% { text-shadow: 0 0 8px rgba(255,235,59,0.6); }
    50% { text-shadow: 0 0 20px rgba(255,235,59,1),
          0 0 30px rgba(212,175,55,0.8); }
}
@keyframes sigPulse {
    0%, 100% { box-shadow: 0 4px 15px rgba(0,0,0,0.3),
               0 0 20px rgba(212,175,55,0.3); }
    50% { box-shadow: 0 4px 15px rgba(0,0,0,0.3),
          0 0 35px rgba(212,175,55,0.7); }
}

.dua-main-box {
    background: linear-gradient(135deg, #0d3011 0%, #1b5e20 25%,
                #2e7d32 50%, #1b5e20 75%, #0d3011 100%);
    background-size: 200% 200%;
    animation: duaGlow 4s ease-in-out infinite,
               gradientShift 12s ease infinite;
    padding: 32px 28px; border-radius: 22px;
    border: 4px solid #d4af37;
    direction: rtl; text-align: center;
    margin: 25px 0; position: relative; overflow: hidden;
}
.dua-main-box::before {
    content: "🕌"; position: absolute; top: 15px; right: 25px;
    font-size: 3.5rem; opacity: 0.25;
    animation: floatIcon 4s ease-in-out infinite;
}
.dua-main-box::after {
    content: "🕌"; position: absolute; bottom: 15px; left: 25px;
    font-size: 3.5rem; opacity: 0.25;
    animation: floatIcon 5s ease-in-out infinite reverse;
}
.dua-main-box * {
    color: white !important; position: relative; z-index: 2;
}
.dua-main-box h3 {
    color: #d4af37 !important; font-size: 1.9rem;
    margin-bottom: 18px; font-weight: 900; letter-spacing: 1px;
    text-shadow: 0 2px 10px rgba(212,175,55,0.5);
}
.dua-main-box .names {
    display: inline-block;
    background: linear-gradient(90deg, rgba(212,175,55,0.15),
                rgba(212,175,55,0.35), rgba(212,175,55,0.15));
    background-size: 200% 100%;
    animation: shimmerText 4s linear infinite;
    font-size: 1.65rem; font-weight: 900;
    color: #ffeb3b !important;
    margin: 20px 0; padding: 16px 30px;
    border: 2px solid #d4af37; border-radius: 15px;
    text-shadow: 0 0 20px rgba(255,235,59,0.6);
    font-family: 'Amiri', serif !important;
}
.dua-main-box p.quran {
    font-family: 'Amiri', serif !important;
    font-size: 1.2rem; color: #d4af37 !important;
    margin-top: 22px; padding: 18px 25px;
    background: rgba(0,0,0,0.25); border-radius: 12px;
    border-right: 5px solid #d4af37;
    border-left: 5px solid #d4af37;
}

.visitor-dua-banner {
    background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 50%,
                #ffe082 100%);
    padding: 20px 28px; border-radius: 18px;
    border: 3px solid #d4af37;
    margin: 22px 0; direction: rtl; text-align: center;
    box-shadow: 0 6px 25px rgba(0,0,0,0.15);
}
.visitor-dua-banner * { color: #4e342e !important; }
.visitor-dua-banner b {
    color: #c62828 !important; font-size: 1.15rem;
    font-family: 'Amiri', serif !important;
}

.dua-fixed-banner {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32,
                #1b5e20, #0d3011);
    background-size: 200% 100%;
    animation: gradientShift 8s linear infinite;
    color: white !important;
    padding: 11px 20px; z-index: 9998; text-align: center;
    border-top: 3px solid #d4af37;
    font-family: 'Amiri', serif !important;
    font-size: 1.05rem; font-weight: bold;
    box-shadow: 0 -4px 25px rgba(0,0,0,0.4);
    letter-spacing: 0.5px;
}
.dua-fixed-banner * {
    color: #ffeb3b !important;
    font-family: 'Amiri', serif !important;
    animation: fixedDuaGlow 3s ease-in-out infinite;
}

.section-title {
    color: #1b5e20 !important;
    border-right: 6px solid #2e7d32;
    padding: 12px 18px; text-align: right;
    font-size: 1.5rem; font-weight: bold;
    margin-top: 30px; margin-bottom: 20px;
    background: linear-gradient(to left,
                rgba(46,125,50,0.15), transparent);
    border-radius: 10px;
}
.formula-item {
    background: linear-gradient(135deg, #ffffff 0%, #e8f5e9 100%);
    padding: 15px 20px; border-radius: 12px;
    margin-bottom: 10px; font-weight: bold;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    text-align: right;
}
.oil-item {
    background: linear-gradient(135deg, #fff8e1 0%, #ffe0b2 100%);
    padding: 12px 18px; border-radius: 12px;
    margin-bottom: 8px; font-weight: bold;
    color: #bf360c !important;
    border-right: 5px solid #e65100;
    box-shadow: 0 4px 15px rgba(230,81,0,0.15);
    text-align: right;
}
.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px; border-radius: 12px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 20px; direction: rtl; text-align: right;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.oil-info-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 18px; border-radius: 12px;
    border-right: 5px solid #e65100;
    margin-bottom: 18px; direction: rtl; text-align: right;
    box-shadow: 0 4px 15px rgba(230,81,0,0.15);
}
.profile-img-style {
    width: 150px; height: 150px; border-radius: 50%;
    object-fit: cover; border: 4px solid #d4af37;
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    display: block; margin: 0 auto;
}
.metric-card {
    background: white; padding: 22px;
    border-radius: 18px;
    box-shadow: 0 6px 30px rgba(0,0,0,0.08);
    text-align: center;
    transition: all 0.3s ease;
    border: 1px solid rgba(46,125,50,0.1);
}
.metric-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 15px 50px rgba(0,0,0,0.15);
}
.metric-card .number {
    font-size: 2.2rem; font-weight: 900;
    color: #1b5e20; margin: 5px 0;
}
.metric-card .label {
    font-size: 0.95rem; color: #666; font-weight: 600;
}
.measurement-card {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 22px; border-radius: 16px;
    border-right: 5px solid #1565C0;
    box-shadow: 0 4px 25px rgba(0,0,0,0.06);
}
.lab-result-card {
    background: linear-gradient(135deg, #e8f0fe, #d2e3fc);
    padding: 15px; border-radius: 12px;
    border-right: 5px solid #1a73e8;
    margin-bottom: 10px;
}
.alert-critical {
    background: linear-gradient(135deg, #ffebee, #ffcdd2);
    padding: 12px 18px; border-radius: 10px;
    border-right: 5px solid #c62828;
    margin-bottom: 10px; color: #b71c1c !important;
    font-weight: bold;
}
.alert-warning {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 12px 18px; border-radius: 10px;
    border-right: 5px solid #ef6c00;
    margin-bottom: 10px; color: #e65100 !important;
    font-weight: bold;
}
.alert-success {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 12px 18px; border-radius: 10px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 10px; color: #1b5e20 !important;
    font-weight: bold;
}
.dose-card {
    background: linear-gradient(135deg, #f3e5f5, #e1bee7);
    padding: 15px 20px; border-radius: 12px;
    border-right: 5px solid #7b1fa2;
    margin-bottom: 10px; text-align: right;
}
.prayer-card {
    background: linear-gradient(135deg, #e0f2f1, #b2dfdb);
    padding: 20px; border-radius: 14px;
    border-right: 6px solid #00695c;
    text-align: center; margin-bottom: 15px;
    box-shadow: 0 4px 15px rgba(0,105,92,0.15);
}
.prayer-card .time {
    font-size: 1.8rem; font-weight: 900;
    color: #004d40 !important;
}
.book-chapter {
    background: linear-gradient(135deg, #1a237e, #283593);
    color: white !important; padding: 15px 20px;
    border-radius: 10px; font-weight: bold; margin-top: 20px;
}
.book-body {
    padding: 20px 25px; font-size: 1.05rem;
    line-height: 1.8; color: #2c3e50;
    border-left: 4px solid #3498db;
    background: #f8f9fa; border-radius: 0 10px 10px 0;
}
.stButton > button {
    color: #1a1a1a !important;
    background-color: #e8f5e9 !important;
    border: 1px solid #2e7d32 !important;
    font-weight: bold !important;
}
.stButton > button:hover {
    background-color: #c8e6c9 !important;
}
.mini-signature {
    position: fixed; left: 20px; bottom: 65px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important; padding: 9px 22px;
    font-size: 0.88rem; border-radius: 25px;
    z-index: 9997; direction: rtl;
    border: 2px solid #d4af37;
    animation: sigPulse 3s ease-in-out infinite;
    font-weight: bold;
}
.mini-signature * { color: white !important; }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 29: بوابة الدخول
# ═════════════════════════════════════════════════════════════════════════════

def render_dua_bar():
    st.markdown(f"""
    <div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <p style="font-size:1.1rem; color:#a5d6a7 !important;
                  margin-bottom:12px;">
        نبدأ باسم الله، ونسألُه أن يتقبّلَ هذا العملَ صدقةً جاريةً عن:
        </p>
        <div class="names">
        🕊️ رحم الله والدي إسماعيل تاور وأختي ابتسام 🕊️
        </div>
        <p class="quran">{DUA_QURAN}</p>
        <p class="quran" style="margin-top:10px;">{DUA_VERSE}</p>
    </div>
    """, unsafe_allow_html=True)


if not st.session_state["approved"]:
    render_dua_bar()
    st.markdown(
        '<div class="main-box" style="max-width: 780px; '
        'margin: 30px auto; direction: rtl;">',
        unsafe_allow_html=True)

    st.markdown(f"<hr style='border-top: 2px solid #d4af37; margin: 25px 0;'>",
                unsafe_allow_html=True)

    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        if img_base64:
            st.markdown(
                f'<img src="data:image/jpeg;base64,{img_base64}" '
                f'class="profile-img-style">',
                unsafe_allow_html=True)
        else:
            st.markdown(
                f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">',
                unsafe_allow_html=True)
    with col_title:
        st.markdown(f"<h2 style='color:#2E7D32; text-align:right;'>"
                    f"🌾 {APP_NAME}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#1565C0; text-align:right; "
                    f"font-size:1.1rem;'>{APP_TAGLINE}</p>",
                    unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#c62828; text-align:right;'>"
                    f"{SUPERVISOR} — {SUPERVISOR_TITLE}</h4>",
                    unsafe_allow_html=True)

    st.markdown("<hr style='border-top: 2px solid #d4af37; "
                "margin: 25px 0;'>", unsafe_allow_html=True)

    st.markdown("<h3 style='text-align:center; color:#1b5e20; "
                "margin-top:20px;'>🔐 بوابة الدخول</h3>",
                unsafe_allow_html=True)

    # دوال الصوت
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

    st.markdown("<hr style='border-top: 1px dashed #ccc; "
                "margin: 20px 0;'>", unsafe_allow_html=True)

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
        owner_code = st.text_input("🔑 كود المالك:",
                                     type="password", key="owner_code")
        if st.button("👑 دخول المالك", type="primary",
                     use_container_width=True):
            if owner_code.strip() == OWNER_CODE:
                st.session_state.update(
                    {"approved": True, "user_role": "owner"})
                st.rerun()
            else:
                st.error("❌ كود غير صحيح")

    with col_guest:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fff8e1, #ffecb3);
        padding: 20px; border-radius: 12px; border: 2px solid #d4af37;
        text-align: center; margin-bottom: 10px;">
        <h4 style="color: #e65100;">👥 زائر</h4>
        <p style="font-size: 0.9rem; color: #555;">دخول مجاني<br>
        <small style="color: #999;">(بيانات المالك محجوبة)</small></p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True):
            st.session_state.update(
                {"approved": True, "user_role": "guest"})
            st.rerun()

    st.markdown("""
    <div style='text-align:center; margin-top:25px;
                color:#999; font-size:0.85rem; direction:rtl;'>
    <p>🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي
    <b>ابتسام</b> - رحمهما الله وغفر لهما</p>
    <p style='color:#d4af37;'>🌾 <b>منصة علمية صدقة جارية</b> 🌾</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
# القسم 30: الواجهة الرئيسية
# ═════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="main-box">', unsafe_allow_html=True)

c1, c2 = st.columns([0.7, 0.3])
with c2:
    role_label = "المالك 👑" if is_owner() else "زائر 👥"
    st.markdown(f"<div style='text-align:left; padding:10px; "
                f"background:#f5f5f5; border-radius:10px;'>"
                f"الحساب: <b>{role_label}</b></div>",
                unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k != "inventory":
                del st.session_state[k]
        st.session_state["approved"] = False
        voice_guide("تم تسجيل الخروج. السلام عليكم.")
        st.rerun()

c3, c4 = st.columns([0.3, 0.7])
with c3:
    if img_base64:
        st.markdown(
            f'<img src="data:image/jpeg;base64,{img_base64}" '
            f'class="profile-img-style">',
            unsafe_allow_html=True)
    else:
        st.markdown(
            f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">',
            unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <h1 style='color: #0d3011; text-align:right; margin-bottom:0;
               text-shadow: 2px 2px 4px rgba(0,0,0,0.15),
                            0 0 20px rgba(27,94,32,0.4);
               font-weight: 900; font-size: 2.3rem;
               -webkit-text-stroke: 0.5px #1b5e20;'>
    🌾 {APP_NAME}
    </h1>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <p style='color: #1565C0; text-align:right;
              font-size: 1.25rem; font-weight: 600;
              margin-top: 8px;
              text-shadow: 1px 1px 2px rgba(21,101,192,0.2);'>
    {APP_TAGLINE}
    </p>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #fff8e1, #ffe082);
                padding: 12px 20px; border-radius: 12px;
                border-right: 6px solid #c62828;
                border-left: 6px solid #c62828;
                margin-top: 10px;
                box-shadow: 0 4px 15px rgba(198,40,40,0.25);'>
        <h3 style='color: #b71c1c; text-align:right; margin: 0;
                   font-weight: 900; font-size: 1.55rem;
                   text-shadow: 1px 1px 2px rgba(198,40,40,0.3);
                   letter-spacing: 0.5px;'>
        👨‍🔬 {SUPERVISOR}
        </h3>
        <p style='color: #0d47a1; text-align:right;
                  margin: 5px 0 0 0;
                  font-weight: 700; font-size: 1.15rem;'>
        ✨ {SUPERVISOR_TITLE}
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="visitor-dua-banner">{DUA_VISITOR_BANNER}</div>',
            unsafe_allow_html=True)

# ─── لوحة إحصائية سريعة ────────────────────────────────────────────────────
st.markdown("### 📊 لوحة التحكم السريعة")
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
stock_summary = InventoryManager.get_stock_summary()
with col_stat1:
    st.markdown(
        f"<div class='metric-card'>"
        f"<div class='number'>{stock_summary['total_items']}</div>"
        f"<div class='label'>إجمالي المواد</div></div>",
        unsafe_allow_html=True)
with col_stat2:
    st.markdown(
        f"<div class='metric-card'>"
        f"<div class='number'>{stock_summary['total_quantity']:.0f}</div>"
        f"<div class='label'>إجمالي المخزون (طن)</div></div>",
        unsafe_allow_html=True)
with col_stat3:
    low_stock = stock_summary['low_stock']
    color = "#c62828" if low_stock > 5 else ("#e65100" if low_stock > 0 else "#2e7d32")
    st.markdown(
        f"<div class='metric-card'>"
        f"<div class='number' style='color:{color};'>{low_stock}</div>"
        f"<div class='label'>مواد منخفضة</div></div>",
        unsafe_allow_html=True)
with col_stat4:
    st.markdown(
        f"<div class='metric-card'>"
        f"<div class='number'>{len(st.session_state.get('broiler_farms', {}))}</div>"
        f"<div class='label'>مزارع نشطة</div></div>",
        unsafe_allow_html=True)

st.markdown("<hr style='border-top: 3px solid #2e7d32;'>",
            unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 31: دوال التبويبات المساعدة
# ═════════════════════════════════════════════════════════════════════════════

def guide_section(tab_name, guide_text):
    with st.expander(f"📘 دليل استخدام {tab_name}", expanded=False):
        st.markdown(
            f"<div style='background:#f0f8ff; padding:15px; "
            f"border-radius:10px; direction:rtl;'>{guide_text}</div>",
            unsafe_allow_html=True)
        if st.button(f"🔊 تشغيل الدليل صوتياً ({tab_name})",
                     key=f"voice_guide_{tab_name}"):
            voice_guide(guide_text)


def generate_formula_image(formula_data, target_dp, target_se, breed,
                             stage, user_name):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.set_facecolor('#f5f5f5')
        fig.patch.set_facecolor('#ffffff')
        title_text = (
            f"🧬 خلطة علفية معتمدة - {APP_NAME}\n"
            f"المشرف: {user_name}\n"
            f"الفصيل: {breed} | المرحلة: {stage}\n"
            f"DP: {target_dp:.1f}% | SE: {target_se:.1f} وحدة")
        ax.set_title(title_text, fontsize=14, fontweight='bold', pad=25)
        ingredients = list(formula_data.keys())
        kg_per_ton = [p * 10 for p in formula_data.values()]
        y_pos = np.arange(len(ingredients))
        ax.barh(y_pos, kg_per_ton, color='#2e7d32',
                alpha=0.8, edgecolor='#1b5e20', linewidth=1.5)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([ar(i) for i in ingredients], fontsize=11)
        ax.set_xlabel('الكمية (كجم/طن)', fontsize=12, fontweight='bold')
        for i, v in enumerate(kg_per_ton):
            ax.text(v + 3, i, f'{v:.1f} كجم', va='center',
                    fontsize=10, fontweight='bold', color='#1b5e20')
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


def send_image_to_whatsapp(image_buf, caption,
                             phone_number=WHATSAPP_NUMBER):
    try:
        image_base64 = base64.b64encode(image_buf.getvalue()).decode()
        encoded_caption = urllib.parse.quote(caption)
        whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_caption}"
        st.markdown(f"""
        <div style='background:#e8f5e9; padding:20px;
                    border-radius:14px; direction:rtl; text-align:center;'>
            <img src="data:image/png;base64,{image_base64}"
                 style="max-width:100%; border-radius:10px;
                        margin:15px 0; border:3px solid #2e7d32;">
            <br>
            <a href='{whatsapp_url}' target='_blank'>
                <button style='background:#25D366; color:white;
                               padding:14px 40px; border:none;
                               border-radius:35px; font-size:17px;
                               font-weight:bold; cursor:pointer;'>
                    📲 إرسال الصورة عبر واتساب
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        return True
    except Exception as e:
        st.error(f"❌ خطأ: {str(e)}")
        return False


# ═════════════════════════════════════════════════════════════════════════════
# القسم 32: تبويب المختبر المتقدم
# ═════════════════════════════════════════════════════════════════════════════

def render_advanced_lab():
    st.markdown('<div class="section-title">🔬 المختبر المتقدم '
                '- تحليل ومقارنة الخلطات</div>',
                unsafe_allow_html=True)
    st.info("أدخل أوزان المكونات لتحليل خلطتك، أو استخدم العينة "
            "المرسلة من قسم التركيب. اختر النظام العلمي.")

    if st.session_state.get("lab_sample"):
        sample = st.session_state["lab_sample"]
        st.success(f"📥 تم استلام عينة من {sample.get('animal', '؟')} "
                   f"- {sample.get('breed', '؟')} - "
                   f"{sample.get('stage', '؟')}")
        st.write(f"**العمر:** {sample.get('age', 'غير محدد')} شهر | "
                 f"**الحالة:** {sample.get('physiological', 'طبيعي')}")
        st.write(f"**DP:** {sample.get('dp', 0):.2f}% | "
                 f"**SE:** {sample.get('se', 0):.2f}")
        if sample.get('requester'):
            st.write(f"**طالب العلف:** {sample['requester']}")
        if st.button("🗑️ مسح العينة"):
            st.session_state["lab_sample"] = None
            st.rerun()

    col_lab1, col_lab2 = st.columns([0.5, 0.5])
    with col_lab1:
        lab_animal = st.selectbox(
            "الفصيل:",
            ["أبقار", "أغنام", "ماعز", "خيول", "إبل",
             "دواجن لاحم", "دواجن بياض", "سمان", "أسماك"],
            key="lab_animal_adv")
        lab_stages = list(STANDARD_VALUES.get(lab_animal, {}).keys()) or ["عام"]
        lab_stage = st.selectbox("المرحلة:", lab_stages,
                                   key="lab_stage_adv")
        standard = STANDARD_VALUES.get(lab_animal, {}).get(lab_stage, {})
        if standard:
            st.info(f"📊 المعايير: DP={standard.get('DP', '-')}%, "
                    f"SE={standard.get('SE', '-')}, "
                    f"CP={standard.get('CP', '-')}%")
    with col_lab2:
        st.markdown("#### 🧬 خيارات البروتين والطاقة")
        protein_system = st.selectbox(
            "نظام البروتين:",
            ["بروتين مهضوم (DP)", "بروتين خام (CP)",
             "بروتين صافي (NP)"], key="lab_ps_adv")
        energy_system = st.selectbox(
            "نظام الطاقة:",
            ["معادل النشاء (SE)", "طاقة أيضية (ME)",
             "طاقة صافية (NE)"], key="lab_es_adv")

    st.markdown("### ⚖️ أدخل أوزان المكونات (كجم)")
    lab_inputs = {}
    all_ings = list(FLAT_FEED_DB.keys())
    cols = st.columns(3)
    for idx, ing in enumerate(all_ings):
        with cols[idx % 3]:
            lab_inputs[ing] = st.number_input(
                f"{ing}", min_value=0.0, value=0.0, step=5.0,
                key=f"lab_adv_{ing}")

    if st.button("🧪 تشغيل التحليل المخبري", type="primary",
                 use_container_width=True, key="adv_lab_run"):
        total = sum(lab_inputs.values())
        if total <= 0:
            st.warning("⚠️ أدخل أوزاناً أكبر من الصفر.")
        else:
            voice_guide(f"جاري تشغيل التحليل المخبري لـ {lab_animal}.")
            formula_pct = {ing: (w / total) * 100.0
                           for ing, w in lab_inputs.items() if w > 0}
            actual = compute_formula_nutrients(formula_pct)
            oil_pct = compute_total_oil_percentage(formula_pct)

            st.session_state["analysis_results"] = {
                'components': lab_inputs,
                'cp': actual['CP'],
                'dp': actual['DP'],
                'se': actual['SE']}
            st.session_state["analysis_animal"] = lab_animal
            st.session_state["analysis_stage"] = lab_stage

            st.success(f"🔬 تم التحليل! إجمالي: **{total:.1f} كجم**")

            comps = [{"المادة": ing,
                      "الوزن (كجم)": w,
                      "النسبة %": f"{(w/total)*100:.2f}"}
                     for ing, w in lab_inputs.items() if w > 0]
            if comps:
                st.table(pd.DataFrame(comps))

            st.markdown("#### 🔬 النتائج:")
            st.table(pd.DataFrame([
                {"العنصر": "البروتين الخام (CP)",
                 "القيمة": f"{actual['CP']:.2f}%"},
                {"العنصر": "البروتين المهضوم (DP)",
                 "القيمة": f"{actual['DP']:.2f}%"},
                {"العنصر": "معادل النشاء (SE)",
                 "القيمة": f"{actual['SE']:.2f} وحدة"},
                {"العنصر": "ألياف NDF",
                 "القيمة": f"{actual['NDF']:.2f}%"},
                {"العنصر": "دهن EE",
                 "القيمة": f"{actual['EE']:.2f}%"},
                {"العنصر": "مجموع الزيوت",
                 "القيمة": f"{oil_pct:.2f}%" if oil_pct > 0 else "لا يوجد"}
            ]))

            if standard:
                dp_dev = ((actual['DP'] - standard.get('DP', 0)) /
                          standard.get('DP', 1)) * 100 if standard.get('DP', 0) > 0 else 0
                se_dev = ((actual['SE'] - standard.get('SE', 0)) /
                          standard.get('SE', 1)) * 100 if standard.get('SE', 0) > 0 else 0
                cp_dev = ((actual['CP'] - standard.get('CP', 0)) /
                          standard.get('CP', 1)) * 100 if standard.get('CP', 0) > 0 else 0
                dp_grade = "✅ ممتاز" if abs(dp_dev) <= 5 else \
                    ("👍 جيد" if abs(dp_dev) <= 10 else "⚠️ يحتاج تحسين")
                se_grade = "✅ ممتاز" if abs(se_dev) <= 5 else \
                    ("👍 جيد" if abs(se_dev) <= 10 else "⚠️ يحتاج تحسين")
                cp_grade = "✅ ممتاز" if abs(cp_dev) <= 5 else \
                    ("👍 جيد" if abs(cp_dev) <= 10 else "⚠️ يحتاج تحسين")

                st.write("#### 📊 المقارنة مع المعايير:")
                st.table(pd.DataFrame([
                    {"المقياس": "DP",
                     "المحسوب": f"{actual['DP']:.2f}%",
                     "القياسي": f"{standard.get('DP', 0):.2f}%",
                     "الانحراف": f"{dp_dev:+.1f}%",
                     "التقييم": dp_grade},
                    {"المقياس": "SE",
                     "المحسوب": f"{actual['SE']:.2f}",
                     "القياسي": f"{standard.get('SE', 0):.2f}",
                     "الانحراف": f"{se_dev:+.1f}%",
                     "التقييم": se_grade},
                    {"المقياس": "CP",
                     "المحسوب": f"{actual['CP']:.2f}%",
                     "القياسي": f"{standard.get('CP', 0):.2f}%",
                     "الانحراف": f"{cp_dev:+.1f}%",
                     "التقييم": cp_grade}
                ]))

                if PLOTLY_AVAILABLE:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=['DP', 'SE', 'CP'],
                        y=[actual['DP'], actual['SE'], actual['CP']],
                        name='المحسوب', marker_color='#2e7d32'))
                    fig.add_trace(go.Bar(
                        x=['DP', 'SE', 'CP'],
                        y=[standard.get('DP', 0), standard.get('SE', 0),
                           standard.get('CP', 0)],
                        name='القياسي', marker_color='#1565C0'))
                    fig.update_layout(
                        title="مقارنة القيم مع المعايير",
                        barmode='group')
                    st.plotly_chart(fig, use_container_width=True)

                try:
                    pdf_data = pdf_gen.generate_lab_report(
                        st.session_state["analysis_results"],
                        lab_animal, lab_stage,
                        st.session_state.get("user", {}).get(
                            "full_name", "مستخدم"),
                        standard,
                        {'DP': dp_grade, 'SE': se_grade, 'CP': cp_grade})
                    st.download_button(
                        "📥 تحميل تقرير المختبر PDF", pdf_data,
                        file_name=f"Lab_Report_{datetime.now():%Y%m%d_%H%M}.pdf",
                        mime="application/pdf")
                except Exception as e:
                    st.warning(f"⚠️ تعذر إنشاء PDF: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# القسم 33: تبويب المختبر الذكي (OCR)
# ═════════════════════════════════════════════════════════════════════════════

def render_smart_lab_ocr():
    st.markdown('<div class="section-title">🧪 المختبر الذكي '
                '- تحليل الأعلاف من الصور</div>',
                unsafe_allow_html=True)
    if not OCR_AVAILABLE:
        st.warning("""
        ⚠️ **مكتبات OCR غير مثبتة!**
        ```bash
        pip install pytesseract opencv-python-headless
        # أو
        pip install easyocr
        ```
        """)

    st.markdown("### 📸 تحليل صورة تركيبة علفية")
    uploaded_file = st.file_uploader(
        "ارفع صورة للتركيبة (كتب، أوراق، هاتف)",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
        key="smart_lab_upload")

    if uploaded_file is not None:
        image = None
        try:
            image = PILImage_module.open(uploaded_file)
            st.image(image, caption="الصورة المرفوعة",
                     use_container_width=True)
        except Exception:
            pass

        if st.session_state.get("smart_lab_system") and \
                st.button("🔍 تحليل الصورة", type="primary",
                          key="smart_lab_btn"):
            with st.spinner("جاري التحليل..."):
                result, error = st.session_state["smart_lab_system"].analyze_image(image)
                if error:
                    st.error(f"❌ {error}")
                else:
                    st.success("✅ تم التحليل!")
                    st.session_state["lab_sample_name"] = result.get('sample_name', '')
                    st.session_state["lab_cp"] = result.get('cp') or 0.0
                    st.session_state["lab_dc"] = result.get('dc') or 0.0
                    st.session_state["lab_se"] = result.get('se') or 0.0
                    st.session_state["lab_ndf"] = result.get('ndf') or 0.0
                    st.session_state["lab_adf"] = result.get('adf') or 0.0
                    st.session_state["lab_ee"] = result.get('ee') or 0.0
                    st.session_state["lab_ash"] = result.get('ash') or 0.0
                    st.session_state["lab_moisture"] = result.get('moisture') or 0.0
                    st.rerun()

    st.markdown("### ✍️ إدخال/تعديل البيانات")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("اسم العينة:", key="lab_sample_name_input",
                       value=st.session_state.get("lab_sample_name", ""))
        st.number_input("CP %:", min_value=0.0,
                         value=float(st.session_state.get("lab_cp", 0.0)),
                         step=0.1, key="lab_cp_input")
        st.number_input("DC:", min_value=0.0, max_value=1.0,
                         value=float(st.session_state.get("lab_dc", 0.0)),
                         step=0.01, key="lab_dc_input")
        st.number_input("SE:", min_value=0.0,
                         value=float(st.session_state.get("lab_se", 0.0)),
                         step=0.1, key="lab_se_input")
    with col2:
        st.number_input("NDF %:", min_value=0.0,
                         value=float(st.session_state.get("lab_ndf", 0.0)),
                         step=0.1, key="lab_ndf_input")
        st.number_input("ADF %:", min_value=0.0,
                         value=float(st.session_state.get("lab_adf", 0.0)),
                         step=0.1, key="lab_adf_input")
        st.number_input("EE %:", min_value=0.0,
                         value=float(st.session_state.get("lab_ee", 0.0)),
                         step=0.1, key="lab_ee_input")
        st.number_input("ASH %:", min_value=0.0,
                         value=float(st.session_state.get("lab_ash", 0.0)),
                         step=0.1, key="lab_ash_input")
        st.number_input("رطوبة %:", min_value=0.0,
                         value=float(st.session_state.get("lab_moisture", 0.0)),
                         step=0.1, key="lab_moisture_input")

    st.text_area("ملاحظات:", key="lab_notes_input")

    if st.button("💾 حفظ نتيجة التحليل", type="secondary",
                 key="lab_save_btn"):
        if st.session_state.get("smart_lab_system"):
            lab_data = {
                'sample_name': st.session_state.get('lab_sample_name', ''),
                'cp': st.session_state.get('lab_cp', 0.0),
                'dc': st.session_state.get('lab_dc', 0.0),
                'se': st.session_state.get('lab_se', 0.0),
                'ndf': st.session_state.get('lab_ndf', 0.0),
                'adf': st.session_state.get('lab_adf', 0.0),
                'ee': st.session_state.get('lab_ee', 0.0),
                'ash': st.session_state.get('lab_ash', 0.0),
                'moisture': st.session_state.get('lab_moisture', 0.0),
                'analyzed_by': st.session_state.get("user", {}).get(
                    "full_name", "مستخدم"),
                'notes': st.session_state.get('lab_notes', ''),
                'image_path': uploaded_file.name if uploaded_file else ''}
            rid = st.session_state["smart_lab_system"].save_lab_result(lab_data)
            st.success(f"✅ تم الحفظ! ID: {rid[:8]}")

    st.markdown("---")
    st.markdown("### 📋 نتائج التحاليل السابقة")
    if st.session_state.get("smart_lab_system"):
        results = st.session_state["smart_lab_system"].get_lab_results(20)
        if results:
            df_data = [
                {'التاريخ': r[11][:16] if r[11] else '',
                 'العينة': r[1],
                 'CP': r[3], 'DC': r[4], 'SE': r[5],
                 'NDF': r[6], 'ADF': r[7], 'EE': r[8], 'ASH': r[9]}
                for r in results]
            st.dataframe(pd.DataFrame(df_data), use_container_width=True)
        else:
            st.info("📭 لا توجد نتائج سابقة.")


# ═════════════════════════════════════════════════════════════════════════════
# القسم 34: تبويب مواقيت الصلاة
# ═════════════════════════════════════════════════════════════════════════════

def render_prayer_times():
    st.markdown('<div class="section-title">🕌 مواقيت الصلاة</div>',
                unsafe_allow_html=True)
    st.info("🕌 مواقيت تقريبية للاسترشاد — يُفضل التحقق من المسجد المحلي.")

    cities = ["مكة المكرمة", "المدينة المنورة", "الخرطوم", "طرابلس",
              "القاهرة", "دبي", "الرياض", "صنعاء", "عمان", "بيروت",
              "دمشق", "بغداد", "الكويت", "مسقط", "المنامة", "الدوحة",
              "أبوظبي", "القدس", "الرباط", "الجزائر", "تونس", "نواكشوط"]
    city = st.selectbox("📍 اختر المدينة:", cities, key="prayer_city")

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
                    "المغرب": "18:50", "العشاء": "20:20"},
    }
    default_times = {"الفجر": "05:00", "الشروق": "06:30",
                     "الظهر": "12:00", "العصر": "15:30",
                     "المغرب": "18:00", "العشاء": "19:30"}
    times = prayer_times.get(city, default_times)

    st.markdown(f"### 📍 مواقيت الصلاة في {city}")
    cols = st.columns(3)
    for i, (name, t) in enumerate(times.items()):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="prayer-card">
                <div style='font-size:1.2rem; color:#004d40;
                            font-weight:700;'>🕐 {name}</div>
                <div class="time">{t}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
    <div class="dua-main-box" style="padding: 20px;">
        <p class="quran" style="font-size: 1rem;">
        ﴿ إِنَّ الصَّلَاةَ كَانَتْ عَلَى الْمُؤْمِنِينَ كِتَابًا مَّوْقُوتًا ﴾
        </p>
        <p style="color: #d4af37 !important; margin-top: 15px;">
        🤲 اللهم اجعلنا من المحافظين على الصلاة 🤲
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔊 تشغيل التذكير الصوتي بالصلاة"):
        voice_guide("حان وقت الصلاة، حي على الصلاة، حي على الفلاح.")


# ═════════════════════════════════════════════════════════════════════════════
# القسم 35: تبويب منبه الجرعات
# ═════════════════════════════════════════════════════════════════════════════

def render_dose_reminders():
    st.markdown('<div class="section-title">💊 نظام منبه الجرعات</div>',
                unsafe_allow_html=True)
    st.info("سجل اللقاحات والفيتامينات والأدوية، وتابع الجرعات القادمة.")

    if "dose_reminders" not in st.session_state:
        st.session_state["dose_reminders"] = []
    reminders = st.session_state["dose_reminders"]

    with st.expander("➕ إضافة جرعة جديدة", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            animal = st.selectbox(
                "🐾 نوع الحيوان:",
                ["أبقار", "أغنام", "ماعز", "خيول", "إبل",
                 "دواجن", "أسماك"], key="dr_animal")
            dtype = st.selectbox(
                "💉 نوع الجرعة:",
                ["لقاح", "فيتامين", "دواء", "مضاد طفيليات",
                 "هرمون", "مضاد حيوي"], key="dr_type")
            dname = st.text_input("📝 اسم الجرعة:", key="dr_name")
        with c2:
            dose = st.number_input("الجرعة:", 0.0, 1000.0, 1.0, 0.1,
                                     key="dr_dose")
            unit = st.selectbox("الوحدة:",
                                 ["مل", "جم", "مجم", "وحدة دولية", "قطرة"],
                                 key="dr_unit")
            route = st.selectbox(
                "طريقة الإعطاء:",
                ["عضل", "تحت الجلد", "فموي", "مياه الشرب",
                 "رش", "قطرة عين"], key="dr_route")
        with c3:
            freq = st.number_input("التكرار (أيام):", 1, 365, 7, 1,
                                     key="dr_freq")
            start = st.date_input("📅 تاريخ البدء:",
                                    datetime.now(), key="dr_start")
            notes = st.text_area("ملاحظات:", key="dr_notes", height=80)

        if st.button("💾 حفظ الجرعة", use_container_width=True,
                     key="dr_save"):
            if not dname:
                st.error("⚠️ أدخل اسم الجرعة")
            else:
                reminders.append({
                    "id": secrets.token_hex(6),
                    "animal": animal, "type": dtype, "name": dname,
                    "dose": dose, "unit": unit, "route": route,
                    "freq": freq,
                    "start": start.isoformat(),
                    "next": (start + timedelta(days=freq)).isoformat(),
                    "notes": notes, "active": True})
                st.success(f"✅ تم إضافة {dname}")
                voice_guide(f"تم إضافة جرعة {dname} بنجاح.")
                st.rerun()

    if reminders:
        st.markdown("### 📋 الجرعات المسجلة")
        today = datetime.now().date()
        for r in reminders:
            next_date = datetime.fromisoformat(r["next"]).date()
            days_left = (next_date - today).days
            if days_left < 0:
                badge = "🔴 متأخرة"
            elif days_left == 0:
                badge = "🟡 اليوم"
            elif days_left <= 3:
                badge = "🟠 قريباً"
            else:
                badge = "🟢"
            with st.expander(f"{badge} 💊 {r['name']} — {r['animal']}"):
                cc1, cc2, cc3 = st.columns(3)
                cc1.metric("النوع", r["type"])
                cc2.metric("الجرعة", f"{r['dose']} {r['unit']}")
                cc3.metric("التكرار", f"كل {r['freq']} يوم")
                st.write(f"**الطريقة:** {r['route']}")
                st.write(f"**الجرعة القادمة:** {r['next'][:10]} "
                         f"({days_left} يوم)")
                if r.get("notes"):
                    st.caption(f"📝 {r['notes']}")
    else:
        st.info("📭 لا توجد جرعات مسجلة بعد.")


# ═════════════════════════════════════════════════════════════════════════════
# القسم 36: تبويب الإنتاج اليومي
# ═════════════════════════════════════════════════════════════════════════════

def render_daily_production():
    st.markdown('<div class="section-title">📈 الإنتاج اليومي</div>',
                unsafe_allow_html=True)
    st.info("سجل بيانات الإنتاج اليومية (الحليب، البيض، الوزن، النفوق).")

    if "daily_production_log" not in st.session_state:
        st.session_state["daily_production_log"] = []

    with st.form("daily_prod_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            farm = st.text_input("🏠 المزرعة:")
            ddate = st.date_input("📅 التاريخ:", datetime.now())
        with c2:
            milk = st.number_input("🥛 الحليب (لتر):",
                                    0.0, 100000.0, 0.0, 1.0)
            eggs = st.number_input("🥚 البيض (عدد):",
                                    0, 1000000, 0, 1)
        with c3:
            wgain = st.number_input("⚖️ زيادة الوزن (كجم):",
                                     0.0, 10000.0, 0.0, 0.5)
            mort = st.number_input("💀 النافق:", 0, 100000, 0, 1)
        notes = st.text_area("📝 ملاحظات:")

        if st.form_submit_button("💾 حفظ اليوم",
                                   use_container_width=True):
            st.session_state["daily_production_log"].append({
                "farm": farm, "date": ddate.isoformat(),
                "milk": milk, "eggs": eggs,
                "weight_gain": wgain, "mortality": mort,
                "notes": notes})
            st.success("✅ تم الحفظ")
            st.rerun()

    if st.session_state["daily_production_log"]:
        st.markdown("### 📋 السجل اليومي")
        df = pd.DataFrame(st.session_state["daily_production_log"])
        st.dataframe(df, use_container_width=True, hide_index=True)

        if PLOTLY_AVAILABLE and len(df) > 1:
            try:
                fig = px.line(df, x="date", y="milk",
                              title="إنتاج الحليب اليومي",
                              markers=True)
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                pass
    else:
        st.info("📭 لا يوجد سجل بعد.")


# ═════════════════════════════════════════════════════════════════════════════
# القسم 37: تبويب التنبيهات
# ═════════════════════════════════════════════════════════════════════════════

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
            st.markdown(
                f'<div class="{cls}">{icon} <b>{name}:</b> {msg}</div>',
                unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-success">'
                    '✅ لا توجد تنبيهات — المخزون بحالة جيدة'
                    '</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 ملخص المخزون")
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي المواد", len(inv))
    c2.metric("مواد منخفضة", sum(
        1 for d in inv.values()
        if (d["quantity"] if isinstance(d, dict) else d) < 5))
    c3.metric("مواد نافذة", sum(
        1 for d in inv.values()
        if (d["quantity"] if isinstance(d, dict) else d) <= 0))

    st.markdown("---")
    st.markdown("### 🐔 تنبيهات المزارع")
    for cid, farm in st.session_state.get("broiler_farms", {}).items():
        d = farm.get("data", {})
        age = d.get("age", 0)
        if age > 0:
            st.write(f"🏠 **{cid}**: عمر {age} يوم، "
                     f"عدد {d.get('birds', 0)}، "
                     f"وزن {d.get('weight_kg', 0):.3f} كجم")


# ═════════════════════════════════════════════════════════════════════════════
# القسم 38: تبويب إرسال الكود
# ═════════════════════════════════════════════════════════════════════════════

def render_send_code():
    st.markdown('<div class="section-title">📧 إرسال السورس كود</div>',
                unsafe_allow_html=True)
    st.info(f"🔒 خاص بالمالك: {SUPERVISOR}")
    st.warning(f"📮 البريد الوحيد المسموح: **{OWNER_EMAIL}**")

    col1, col2 = st.columns([2, 1])
    with col1:
        email_in = st.text_input("📧 البريد المستلم:",
                                  value=OWNER_EMAIL,
                                  key="send_code_email")
    with col2:
        if st.button("📤 إرسال الكود الآن", type="primary",
                     use_container_width=True, key="send_code_btn"):
            if email_in.strip().lower() != OWNER_EMAIL.lower():
                st.error("❌ الإرسال مسموح فقط لبريد المالك")
            elif not st.session_state.get("email_password"):
                st.warning("⚠️ تحتاج إعداد App Password")
                st.code("""
# .streamlit/secrets.toml
[email]
password = "your_app_password_here"
                """, language="toml")
            else:
                with st.spinner("جاري الإرسال..."):
                    success, msg = send_code_to_email(email_in)
                    if success:
                        st.success(msg)
                        voice_guide("تم إرسال الكود بنجاح.")
                    else:
                        st.error(msg)

    st.markdown("---")
    st.markdown("### 📋 معلومات الكود")
    st.write(f"- **الاسم:** {APP_NAME}")
    st.write(f"- **الإصدار:** 18.0")
    st.write(f"- **التبويبات:** 21")
    st.write(f"- **المشرف:** {SUPERVISOR}")
    st.write(f"- **التاريخ:** {datetime.now():%Y-%m-%d}")


# ═════════════════════════════════════════════════════════════════════════════
# القسم 39: التبويبات الرئيسية
# ═════════════════════════════════════════════════════════════════════════════

if is_owner():
    tabs_titles = [
        "🔬 تركيب الأعلاف",         # 0
        "🌰 مكتبة الزيوت",          # 1
        "🍼 بدائل الحليب",          # 2
        "📷 المختبر الذكي",          # 3
        "🔬 المختبر المتقدم",        # 4
        "🕌 مواقيت الصلاة",          # 5
        "💊 منبه الجرعات",           # 6
        "📈 الإنتاج اليومي",         # 7
        "🔔 التنبيهات",              # 8
        "📊 البورصة",                # 9
        "🏭 المستودعات",            # 10
        "🧾 الفواتير",              # 11
        "🖨️ الديباجة",             # 12
        "📈 التحليلات",             # 13
        "🐔 مزارع الدجاج",          # 14
        "💬 التعليقات",             # 15
        "📚 المراجع",               # 16
        "💡 المساعدة",              # 17
        "📖 الدليل",                # 18
        "📧 إرسال الكود",            # 19
    ]
else:
    tabs_titles = [
        "🔬 تركيب الأعلاف",         # 0
        "🌰 مكتبة الزيوت",          # 1
        "🍼 بدائل الحليب",          # 2
        "📷 المختبر الذكي",          # 3
        "🕌 مواقيت الصلاة",          # 4
        "📚 المراجع",               # 5
        "💡 المساعدة",              # 6
        "📖 الدليل",                # 7
    ]

tabs = st.tabs(tabs_titles)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 40: تبويب 0 — تركيب الأعلاف
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
                                 key="country")
    with cc2:
        state = st.text_input("🗺️ الولاية:", "الخرطوم", key="state")
    with cc3:
        city = st.text_input("🏙️ المدينة:", "الخرطوم", key="city")
    rate = EXCHANGE_RATES.get(country, {"rate": 1.0, "sym": "USD"})
    local_rate, local_sym = rate["rate"], rate["sym"]
    live_prices = get_market_prices(country, city, state)

    st.markdown('<div class="section-title">🧬 أساس حساب البروتين</div>',
                unsafe_allow_html=True)
    protein_basis_choice = st.radio(
        "اختر أساس الحساب:",
        ["البروتين المهضوم (DP) — الأدق علمياً",
         "البروتين الخام (CP) — الأسهل ميدانياً"],
        horizontal=True, key="protein_basis")
    use_dp = "DP" in protein_basis_choice
    if use_dp:
        st.success("🎯 تستخدم الآن **DP** — الأدق علمياً")
    else:
        st.info("📊 تستخدم الآن **CP** — الأسهل ميدانياً")

    st.markdown(
        '<div class="section-title">🐾 اختر الحيوان '
        'والحالة الفسيولوجية</div>',
        unsafe_allow_html=True)
    animal_tabs = st.tabs([
        "🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐪 إبل",
        "🐎 خيول", "🐔 دواجن", "🦆 سمان", "🐟 أسماك"])

    animal_choice = None
    production_type = None
    requirement = None
    img_key = "عام"
    std_key_global = ""

    with animal_tabs[0]:
        st.markdown("### 🐄 احتياجات الأبقار — NRC 2001")
        cattle_type = st.selectbox(
            "الحالة الفسيولوجية:",
            ["حليب_عالي", "حليب_متوسط", "حليب_منخفض",
             "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"],
            format_func=lambda x: {
                "حليب_عالي": "🐄 حلابة عالية الإنتاج",
                "حليب_متوسط": "🐄 حلابة متوسطة",
                "حليب_منخفض": "🐄 حلابة منخفضة",
                "تسمين_مكثف": "💪 تسمين مكثف (ADG >1.3)",
                "تسمين_عادي": "💪 تسمين عادي (ADG ~0.8)",
                "حمل_أخير": "🤰 حمل آخر",
                "صيانة": "🌿 صيانة / جافة"}.get(x, x),
            key="cattle_type")
        c1_, c2_ = st.columns(2)
        cattle_params = {}
        with c1_:
            if "حليب" in cattle_type:
                cattle_params["milk_yield"] = st.number_input(
                    "🥛 إنتاج الحليب (كجم):", 5.0, 60.0, 20.0, 1.0,
                    key="cattle_milk")
            cattle_params["weight_kg"] = st.number_input(
                "⚖️ الوزن (كجم):", 200.0, 900.0, 500.0, 25.0,
                key="cattle_wt")
        with c2_:
            req_pre = get_cattle_requirements(cattle_type, **cattle_params)
            st.metric("🧬 DP", f"{req_pre.DP}%")
            st.metric("🧬 CP", f"{req_pre.CP}%")
            st.metric("🌽 SE", f"{req_pre.SE}")
            st.caption(f"📝 {req_pre.note}")
        if st.checkbox("✅ اعتماد الأبقار", key="use_cattle"):
            animal_choice = "أبقار"
            production_type = cattle_type
            requirement = req_pre
            img_key = "أبقار"
            std_key_global = f"أبقار_{cattle_type}"

    with animal_tabs[1]:
        st.markdown("### 🐏 احتياجات الأغنام — NRC 2007")
        sg = st.radio("الجنس:", ["ذكر (تسمين)", "أنثى (أمهات)"],
                       horizontal=True, key="sheep_gender")
        is_male_s = "ذكر" in sg
        litter = 1
        if is_male_s:
            sheep_type = st.selectbox(
                "الحالة:",
                ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد"],
                format_func=lambda x: {
                    "تسمين_مكثف": "💪 تسمين مكثف (ADG >250 جم)",
                    "تسمين_عادي": "💪 تسمين عادي",
                    "حملان_تيد": "🐑 حملان تيد"}.get(x, x),
                key="sheep_t_m")
        else:
            sheep_type = st.selectbox(
                "الحالة:",
                ["مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
                format_func=lambda x: {
                    "مرضعات": "🍼 نعاج مرضعات",
                    "حامل_أخير": "🤰 حامل (4-5)",
                    "حامل_متوسط": "🤰 حامل (1-3)",
                    "صيانة": "🌿 صيانة"}.get(x, x),
                key="sheep_t_f")
            if sheep_type == "مرضعات":
                litter = st.number_input("👶 عدد المواليد:",
                                           1, 3, 1, 1, key="sheep_litter")
        weight_s = st.number_input("⚖️ الوزن (كجم):",
                                     15.0, 120.0, 50.0, 5.0,
                                     key="sheep_wt")
        req_pre = get_sheep_requirements(sheep_type, is_male=is_male_s,
                                          weight_kg=weight_s,
                                          litter_size=litter)
        p1, p2, p3 = st.columns(3)
        p1.metric("🧬 DP", f"{req_pre.DP}%")
        p2.metric("🧬 CP", f"{req_pre.CP}%")
        p3.metric("🌽 SE", f"{req_pre.SE}")
        st.caption(f"📝 {req_pre.note}")
        if st.checkbox("✅ اعتماد الأغنام", key="use_sheep"):
            animal_choice = "أغنام"
            production_type = sheep_type
            requirement = req_pre
            img_key = "أغنام"
            std_key_global = f"أغنام_{sheep_type}"

    with animal_tabs[2]:
        st.markdown("### 🐐 احتياجات الماعز — NRC 2007")
        gg = st.radio("الجنس:", ["ذكر (تسمين)", "أنثى (حلابة)"],
                       horizontal=True, key="goat_gender")
        is_male_g = "ذكر" in gg
        milk_g = 0
        if is_male_g:
            goat_type = st.selectbox(
                "الحالة:", ["تسمين_جديان", "تيوس"],
                format_func=lambda x: {
                    "تسمين_جديان": "💪 تسمين جديان",
                    "تيوس": "🐐 تيوس"}.get(x, x),
                key="goat_t_m")
        else:
            goat_type = st.selectbox(
                "الحالة:",
                ["حلابة_عالي", "حلابة_متوسط", "حامل_أخير", "صيانة"],
                format_func=lambda x: {
                    "حلابة_عالي": "🍼 حلابة إدرار عالي",
                    "حلابة_متوسط": "🍼 حلابة إدرار متوسط",
                    "حامل_أخير": "🤰 حامل أخير",
                    "صيانة": "🌿 صيانة"}.get(x, x),
                key="goat_t_f")
            if "حلابة" in goat_type:
                milk_g = st.number_input("🥛 إنتاج الحليب (كجم):",
                                           0.5, 8.0, 2.0, 0.25,
                                           key="goat_milk")
        req_pre = get_goat_requirements(goat_type,
                                          is_male=is_male_g,
                                          milk_yield=milk_g)
        p1, p2, p3 = st.columns(3)
        p1.metric("🧬 DP", f"{req_pre.DP}%")
        p2.metric("🧬 CP", f"{req_pre.CP}%")
        p3.metric("🌽 SE", f"{req_pre.SE}")
        st.caption(f"📝 {req_pre.note}")
        if st.checkbox("✅ اعتماد الماعز", key="use_goat"):
            animal_choice = "ماعز"
            production_type = goat_type
            requirement = req_pre
            img_key = "ماعز"
            std_key_global = f"ماعز_{goat_type}"

    with animal_tabs[3]:
        st.markdown("### 🐪 احتياجات الإبل — FAO 2010")
        st.info("🐪 الإبل تحتاج بروتيناً أقل وأليافاً أكثر من الأبقار")
        camel_type = st.selectbox(
            "الحالة:",
            ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
            format_func=lambda x: {
                "نمو": "🐪 نمو (حوار)",
                "تسمين": "💪 تسمين",
                "حليب": "🍼 حلابة",
                "سباق": "🏃 سباق (هجن)",
                "صيانة": "🌿 صيانة"}.get(x, x),
            key="camel_type")
        camel_wt = st.number_input("⚖️ الوزن (كجم):",
                                     100.0, 800.0, 400.0, 25.0,
                                     key="camel_wt")
        camel_milk = 5.0
        if camel_type == "حليب":
            camel_milk = st.number_input("🥛 إنتاج الحليب (لتر):",
                                           2.0, 20.0, 5.0, 0.5,
                                           key="camel_milk")
        req_pre = get_camel_requirements(camel_type,
                                           weight_kg=camel_wt,
                                           milk_yield=camel_milk)
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("🧬 DP", f"{req_pre.DP}%")
        p2.metric("🧬 CP", f"{req_pre.CP}%")
        p3.metric("🌽 SE", f"{req_pre.SE}")
        p4.metric("🌾 NDF", f"{req_pre.NDF}%")
        st.info(f"📝 {req_pre.note}")
        if st.checkbox("✅ اعتماد الإبل", key="use_camel"):
            animal_choice = "إبل"
            production_type = camel_type
            requirement = req_pre
            img_key = "إبل"
            std_key_global = f"إبل_{camel_type}"

    with animal_tabs[4]:
        st.markdown("### 🐎 احتياجات الخيول — NRC 2007")
        horse_type = st.selectbox(
            "الحالة:",
            ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار",
             "مرضعات", "صيانة"],
            format_func=lambda x: {
                "رياضة_مكثف": "🏇 رياضة مكثف",
                "رياضة_عادي": "🏇 رياضة عادي",
                "نمو_أمهار": "🐎 أمهار نمو",
                "مرضعات": "🍼 فرسات مرضعات",
                "صيانة": "🌿 صيانة"}.get(x, x),
            key="horse_type")
        horse_wt = st.number_input("⚖️ الوزن (كجم):",
                                     200.0, 800.0, 450.0, 25.0,
                                     key="horse_wt")
        req_pre = get_horse_requirements(horse_type, weight_kg=horse_wt)
        p1, p2, p3 = st.columns(3)
        p1.metric("🧬 DP", f"{req_pre.DP}%")
        p2.metric("🧬 CP", f"{req_pre.CP}%")
        p3.metric("🌽 SE", f"{req_pre.SE}")
        st.caption(f"📝 {req_pre.note}")
        if st.checkbox("✅ اعتماد الخيول", key="use_horse"):
            animal_choice = "خيول"
            production_type = horse_type
            requirement = req_pre
            img_key = "خيول"
            std_key_global = f"خيول_{horse_type}"

    with animal_tabs[5]:
        st.markdown("### 🐔 احتياجات الدواجن — NRC + Ross 308")
        poultry_strain = st.radio("السلالة:", ["لاحم", "بياض"],
                                    horizontal=True, key="poultry_strain")
        poultry_age = st.number_input("العمر (أسبوع):",
                                        1, 20, 1, 1, key="poultry_age")
        req_pre = get_poultry_requirements(poultry_strain, poultry_age)
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("🧬 DP", f"{req_pre.DP}%")
        p2.metric("🧬 CP", f"{req_pre.CP}%")
        p3.metric("🌽 SE", f"{req_pre.SE}")
        p4.metric("Ca", f"{req_pre.Ca}%")
        st.caption(f"📝 {req_pre.note}")
        if st.checkbox("✅ اعتماد الدواجن", key="use_poultry"):
            animal_choice = "دواجن"
            production_type = poultry_strain
            requirement = req_pre
            img_key = "دواجن"
            if poultry_strain == "لاحم":
                std_key_global = "دواجن_بادي" if poultry_age <= 1 else \
                    ("دواجن_نامي" if poultry_age <= 3 else "دواجن_ناهي")
            else:
                std_key_global = "دواجن_بياض"

    with animal_tabs[6]:
        st.markdown("### 🦆 احتياجات السمان")
        quail_strain = st.radio("النوع:", ["تسمين", "بياض"],
                                  horizontal=True, key="quail_strain")
        quail_age = st.number_input("العمر (أسبوع):",
                                      1, 8, 1, 1, key="quail_age")
        req_pre = get_quail_requirements(quail_strain, quail_age)
        p1, p2, p3 = st.columns(3)
        p1.metric("🧬 DP", f"{req_pre.DP}%")
        p2.metric("🧬 CP", f"{req_pre.CP}%")
        p3.metric("🌽 SE", f"{req_pre.SE}")
        st.caption(f"📝 {req_pre.note}")
        if st.checkbox("✅ اعتماد السمان", key="use_quail"):
            animal_choice = "سمان"
            production_type = quail_strain
            requirement = req_pre
            img_key = "سمان"
            std_key_global = f"سمان_{quail_strain}"

    with animal_tabs[7]:
        st.markdown("### 🐟 احتياجات الأسماك")
        fish_species = st.selectbox(
            "النوع:",
            ["البلطي النيلي", "القرموط الأفريقي", "الكارب"],
            key="fish_sp")
        fish_stage = st.selectbox(
            "المرحلة:", ["بادئ زريعة", "نمو", "تسمين"],
            key="fish_stage")
        req_pre = get_fish_requirements(fish_species, fish_stage)
        p1, p2, p3 = st.columns(3)
        p1.metric("🧬 DP", f"{req_pre.DP}%")
        p2.metric("🧬 CP", f"{req_pre.CP}%")
        p3.metric("🌽 SE", f"{req_pre.SE}")
        st.caption(f"📝 {req_pre.note}")
        if st.checkbox("✅ اعتماد الأسماك", key="use_fish"):
            animal_choice = "أسماك"
            production_type = fish_stage
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

    st.markdown(
        f'<div class="section-title">🎯 المختار: {animal_choice} '
        f'— {requirement.name_ar}</div>',
        unsafe_allow_html=True)
    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
    info_col1.metric("🧬 DP", f"{requirement.DP}%")
    info_col2.metric("🧬 CP", f"{requirement.CP}%")
    info_col3.metric("🌽 SE", f"{requirement.SE}")
    info_col4.metric("🌾 NDF", f"{requirement.NDF}%")
    st.info(f"📝 {requirement.note} | **أساس الحساب: "
            f"{'DP (مهضوم)' if use_dp else 'CP (خام)'}**")

    oil_std_info = get_oil_standard(std_key_global)
    st.markdown('<div class="section-title">🌰 معيار الزيوت '
                'لهذا الحيوان</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="oil-info-card">
    <b>📊 الحدود القياسية للزيوت:</b><br>
    ▪️ الحد الأقصى: <b>{oil_std_info['max']}%</b><br>
    ▪️ النسبة المثالية: <b>{oil_std_info['optimal']}%</b><br>
    ▪️ المرجع: <b>{oil_std_info['source']}</b><br>
    <small>💡 كل 1% زيت ≈ 90 kcal/kg علف</small>
    </div>
    """, unsafe_allow_html=True)

    requester_name = st.text_input(
        "👤 اسم طالب العلفة:",
        placeholder="مثال: مزرعة الأمل — أحمد محمد",
        key="requester")

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
                        "فوسفات ثنائي الكالسيوم (DCP)",
                        "مضاد سموم فطرية"]
                    if animal_choice in ["أغنام", "ماعز", "أبقار", "إبل"]:
                        default_check = default_check or (
                            ing_name == "بيكربونات الصوديوم (الصودا)")
                    if animal_choice in ["دواجن", "سمان"]:
                        default_check = default_check or ("بريمكس" in ing_name)

                    if cat_name == "🌰 الزيوت النباتية والحيوانية":
                        st.markdown(f"**{ing_name}**")
                        st.caption(
                            f"⚡ SE={ing_data.get('SE', 0):.0f} | "
                            f"EE=100% | "
                            f"{ing_data.get('desc', '')[:60]}")
                        checked = st.checkbox(
                            "إضافة", value=False,
                            key=f"ck_{animal_choice}_{ing_name}")
                    else:
                        checked = st.checkbox(
                            ing_name, value=default_check,
                            key=f"ck_{animal_choice}_{ing_name}")

                    price = live_prices.get(ing_name, 300.0)
                    if is_owner():
                        price = st.number_input(
                            "$", min_value=5.0, value=float(price),
                            key=f"p_{animal_choice}_{ing_name}",
                            label_visibility="collapsed")
                    else:
                        st.caption(f"💰 ${price:.0f}/طن")

                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price

    st.markdown("---")

    if st.button("🚀 تشغيل المحرك الذكي — مطابقة شاملة (فرق ≤ 0.3%)",
                 type="primary", use_container_width=True,
                 key="run_smart"):
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
                labels = {
                    "CP": "بروتين خام CP", "DP": "بروتين مهضوم DP",
                    "SE": "معادل النشاء SE", "NDF": "ألياف NDF",
                    "ADF": "ألياف ADF", "EE": "دهن EE",
                    "ASH": "رماد ASH", "Ca": "كالسيوم Ca",
                    "P": "فسفور P"}

                for k, sv in custom_standard.items():
                    cv = actual.get(k, 0.0)
                    diff = cv - sv
                    pct = (diff / sv * 100) if sv else 0
                    ev = evaluate_difference(pct)
                    compare_scores.append({"score": ev["score"]})
                    compare_rows.append({
                        "العنصر": labels.get(k, k),
                        "المعيار": f"{sv:.2f}",
                        "المحسوب": f"{cv:.2f}",
                        "الفرق": f"{diff:+.3f}",
                        "الفرق %": f"{pct:+.2f}%",
                        "التقييم": ev["label"]})

                overall = get_overall_rating(compare_scores)
                perfect = result.get("perfect_match", False)

                if perfect:
                    st.success(f"🎯 **مطابقة كاملة!** — أساس "
                               f"{basis_label}")
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
                             use_container_width=True,
                             hide_index=True)

                st.markdown("### 🌰 تقييم الزيوت")
                if total_oil > 0:
                    if total_oil > oil_std["max"]:
                        st.error(f"⚠️ **تجاوز الحد الأقصى!** "
                                 f"{total_oil:.2f}% > "
                                 f"{oil_std['max']}%")
                    elif total_oil > oil_std["optimal"] * 1.2:
                        st.warning(f"⚡ مرتفع قليلاً ({total_oil:.2f}%) "
                                    f"— المثالي "
                                    f"{oil_std['optimal']}%")
                    else:
                        st.success(f"✅ مطابق — {total_oil:.2f}% "
                                    f"(المثالي {oil_std['optimal']}%)")
                    st.caption(f"📖 المرجع: {oil_std['source']}")

                    oils_used = [(ing, pct)
                                 for ing, pct in formula.items()
                                 if ing in get_oil_ingredients()]
                    for ing, pct in oils_used:
                        kcal = pct * 90
                        st.markdown(
                            f'<div class="oil-item">🌰 <b>{ing}:</b> '
                            f'{pct:.2f}% | طاقة ≈ {kcal:.0f} kcal/kg</div>',
                            unsafe_allow_html=True)
                else:
                    st.info("ℹ️ لم تستخدم أي زيوت في هذه الخلطة")

                st.markdown("#### 🌾 المكونات:")
                for ing, pct in formula.items():
                    st.markdown(
                        f'<div class="formula-item">▪️ <b>{ing}:</b> '
                        f'{pct:.2f}% ({pct*10:.1f} كجم/طن)</div>',
                        unsafe_allow_html=True)

                st.metric("💰 التكلفة الفعلية للطن:",
                          f"${cost:.2f} "
                          f"({cost*local_rate:,.0f} {local_sym})")

                st.session_state["active_formula"] = formula
                st.session_state["computed_ton_cost"] = cost
                st.session_state["active_animal_img"] = ANIMAL_IMAGES.get(
                    img_key, ANIMAL_IMAGES["عام"])
                st.session_state["active_stage_title"] = (
                    f"{animal_choice} — {requirement.name_ar}")

                st.markdown("### 📥 تحميل التقارير")
                dl1, dl2 = st.columns(2)
                with dl1:
                    try:
                        pdf = pdf_gen.generate_report(
                            formula=formula, requirement=requirement,
                            animal_type=animal_choice,
                            breed=requirement.name_ar,
                            cost=cost, city=city,
                            local_cost=cost * local_rate,
                            local_sym=local_sym,
                            requester_name=requester_name,
                            protein_basis=basis_label,
                            standard_key=std_key_global,
                            include_charts=True)
                        fname = (f"TaworNology_{animal_choice}_"
                                 f"{datetime.now():%Y%m%d_%H%M}.pdf")
                        st.download_button("📥 تحميل PDF", pdf,
                                            file_name=fname,
                                            mime="application/pdf",
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
                            st.download_button(
                                "📊 تحميل Excel", xl,
                                file_name=fname,
                                mime="application/vnd.openxmlformats-"
                                     "officedocument.spreadsheetml.sheet",
                                use_container_width=True)
                    except Exception as e:
                        st.error(f"⚠️ خطأ Excel: {e}")

                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    if st.button("🔬 إرسال العينة إلى المختبر",
                                 use_container_width=True,
                                 key="send_to_lab_adv"):
                        st.session_state["lab_sample"] = {
                            'animal': animal_choice,
                            'breed': requirement.name_ar,
                            'stage': requirement.name_ar,
                            'dp': requirement.DP,
                            'se': actual['SE'],
                            'cp': actual['CP'],
                            'requester': requester_name,
                            'formula': formula}
                        st.success("✅ تم إرسال العينة")
                        voice_guide("تم إرسال العينة إلى المختبر.")

                with col_act2:
                    if st.button("📲 مشاركة الخلطة كصورة",
                                 use_container_width=True,
                                 key="share_formula_adv"):
                        img_buf = generate_formula_image(
                            formula, actual['DP'], actual['SE'],
                            requirement.name_ar, requirement.name_ar,
                            st.session_state.get("user", {}).get(
                                "full_name", "مستخدم"))
                        if img_buf:
                            caption = (f"خلطة {animal_choice} | "
                                       f"DP:{actual['DP']:.1f}% | "
                                       f"SE:{actual['SE']:.0f} | "
                                       f"${cost:.2f}/طن")
                            send_image_to_whatsapp(img_buf, caption)

                if PLOTLY_AVAILABLE and len(formula) > 1:
                    try:
                        colors = ['#e53935', '#8e24aa', '#3949ab',
                                  '#1e88e5', '#00897b', '#43a047',
                                  '#7cb342', '#fdd835', '#fb8c00',
                                  '#6d4c41', '#c62828', '#6a1b9a']
                        fig = px.pie(
                            values=list(formula.values()),
                            names=list(formula.keys()),
                            title=f"توزيع المكونات — {animal_choice}",
                            color_discrete_sequence=colors)
                        fig.update_traces(textposition='inside',
                                            textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass
            else:
                st.error(f"❌ {result['message']}")


# ═════════════════════════════════════════════════════════════════════════════
# القسم 41: تبويب 1 — مكتبة الزيوت
# ═════════════════════════════════════════════════════════════════════════════

with tabs[1]:
    st.markdown('<div class="section-title">🌰 مكتبة الزيوت النباتية '
                'والحيوانية</div>', unsafe_allow_html=True)
    st.write("جميع الزيوت المعتمدة في صناعة الأعلاف وفق المعايير "
             "العالمية (NRC، INRA، Ross 308، FAO).")

    st.markdown("### 📊 الحدود القياسية للزيوت حسب الحيوان")
    oil_std_rows = []
    for key, val in MAX_OIL_PERCENTAGE.items():
        oil_std_rows.append({
            "الحيوان/الحالة": key,
            "الحد الأقصى %": f"{val['max']}%",
            "المثالي %": f"{val['optimal']}%",
            "المرجع": val["source"]})
    st.dataframe(pd.DataFrame(oil_std_rows),
                 use_container_width=True, hide_index=True)

    st.markdown("### 🌰 الزيوت المتوفرة")
    oils = get_oil_ingredients()
    for category, oil_list in OIL_CATEGORIES.items():
        st.markdown(f"#### {category}")
        cat_oils = [(name, oils[name]) for name in oil_list if name in oils]
        for ing_name, ing_data in cat_oils:
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
                st.caption(f"📖 المرجع: "
                            f"{ing_data.get('source', 'NRC')}")


# ═════════════════════════════════════════════════════════════════════════════
# القسم 42: تبويب 2 — بدائل الحليب
# ═════════════════════════════════════════════════════════════════════════════

with tabs[2]:
    st.markdown('<div class="section-title">🍼 مختبر بدائل الحليب</div>',
                unsafe_allow_html=True)
    mr1, mr2 = st.columns(2)
    with mr1:
        mr_animal = st.selectbox("نوع الحيوان:",
                                   list(MILK_REPLACER_STANDARDS.keys()),
                                   key="mr_a")
        mr_volume = st.number_input("الكمية (كجم):",
                                      1.0, 10000.0, 100.0, 10.0,
                                      key="mr_v")
        mr_req = st.text_input("اسم طالب التركيب:", key="mr_r")
    with mr2:
        std_mr = MILK_REPLACER_STANDARDS[mr_animal]
        st.markdown(f"""
        <div class="price-card">
        <b>📊 المعيار — {mr_animal}:</b><br>
        ▪️ بروتين: <b>{std_mr['CP']}%</b><br>
        ▪️ دهن: <b>{std_mr['Fat']}%</b><br>
        ▪️ لاكتوز: <b>{std_mr['Lactose']}%</b><br>
        <small>{std_mr['notes']}</small>
        </div>
        """, unsafe_allow_html=True)

    mr_selected = []
    mr_cols = st.columns(3)
    for i, (name, data) in enumerate(MILK_REPLACER_INGREDIENTS.items()):
        with mr_cols[i % 3]:
            default_mr = name in [
                "حليب مجفف منزوع الدسم", "حليب مجفف كامل الدسم",
                "شرش حليب مجفف", "زيت جوز الهند", "زيت النخيل",
                "بريمكس فيتامينات", "كالسيوم كربونات",
                "فوسفات ثنائي الكالسيوم", "ملح طعام"]
            if st.checkbox(f"{name} — ${data['price']}",
                            value=default_mr,
                            key=f"mr_{name}"):
                mr_selected.append(name)

    if st.button("🧪 تشغيل التركيب", type="primary",
                 use_container_width=True, key="mr_run"):
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
                st.info("📌 يُقدَّم دافئاً (38-40°م) على 3-4 وجبات يومياً")
            else:
                st.error(f"❌ {r['message']}")


# ═════════════════════════════════════════════════════════════════════════════
# القسم 43: تبويب 3 — المختبر الذكي (OCR)
# ═════════════════════════════════════════════════════════════════════════════

with tabs[3]:
    guide_section("المختبر الذكي",
                   "ارفع صورة تركيبة علفية لاستخراج البيانات تلقائياً.")
    render_smart_lab_ocr()


# ═════════════════════════════════════════════════════════════════════════════
# القسم 44: تبويب 4 — المختبر المتقدم (للمالك)
# ═════════════════════════════════════════════════════════════════════════════

if is_owner():
    with tabs[4]:
        guide_section("المختبر المتقدم",
                       "حلل خلطاتك وقارنها بالمعايير.")
        render_advanced_lab()


# ═════════════════════════════════════════════════════════════════════════════
# القسم 45: تبويب مواقيت الصلاة (كل المستخدمين)
# ═════════════════════════════════════════════════════════════════════════════

prayer_idx = tabs_titles.index("🕌 مواقيت الصلاة")
with tabs[prayer_idx]:
    guide_section("مواقيت الصلاة",
                   "عرض مواقيت الصلاة حسب المدينة.")
    render_prayer_times()


# ═════════════════════════════════════════════════════════════════════════════
# القسم 46: تبويبات المالك الإضافية
# ═════════════════════════════════════════════════════════════════════════════

if is_owner():
    # ─── منبه الجرعات ─────────────────────────────────────────────────────
    with tabs[tabs_titles.index("💊 منبه الجرعات")]:
        guide_section("منبه الجرعات",
                       "إدارة منبهات اللقاحات والفيتامينات.")
        render_dose_reminders()

    # ─── الإنتاج اليومي ───────────────────────────────────────────────────
    with tabs[tabs_titles.index("📈 الإنتاج اليومي")]:
        guide_section("الإنتاج اليومي",
                       "تسجيل بيانات الإنتاج اليومي.")
        render_daily_production()

    # ─── التنبيهات ────────────────────────────────────────────────────────
    with tabs[tabs_titles.index("🔔 التنبيهات")]:
        guide_section("التنبيهات",
                       "تنبيهات المخزون والإنتاج.")
        render_alerts()

    # ─── البورصة ──────────────────────────────────────────────────────────
    with tabs[tabs_titles.index("📊 البورصة")]:
        st.markdown('<div class="section-title">📊 البورصة</div>',
                    unsafe_allow_html=True)
        t1, t2 = st.tabs(["🐄 الماشية", "🥩 المنتجات"])
        with t1:
            for animal, price in list(
                    st.session_state["livestock_prices"].items()):
                new_p = st.number_input(
                    f"تحديث: {animal}", min_value=0.0,
                    value=float(price), step=0.1, key=f"lv_{animal}")
                st.session_state["livestock_prices"][animal] = new_p
        with t2:
            for product, price in list(
                    st.session_state["products_prices"].items()):
                new_p = st.number_input(
                    f"تحديث: {product}", min_value=0.0,
                    value=float(price), step=0.05, key=f"pr_{product}")
                st.session_state["products_prices"][product] = new_p

    # ─── المستودعات ───────────────────────────────────────────────────────
    with tabs[tabs_titles.index("🏭 المستودعات")]:
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
                new_q = st.number_input(
                    "تحديث:", min_value=0.0, value=float(q),
                    key=f"inv_{name}", label_visibility="collapsed")
                if isinstance(inv[name], dict):
                    inv[name]["quantity"] = new_q

    # ─── الفواتير ─────────────────────────────────────────────────────────
    with tabs[tabs_titles.index("🧾 الفواتير")]:
        st.markdown('<div class="section-title">🧾 الفواتير</div>',
                    unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            client = st.text_input("العميل:", "مزرعة الأمل")
        with fc2:
            tons = st.number_input("الكمية (طن):",
                                     0.1, 1000.0, 2.0, 0.5)
        with fc3:
            profit = st.number_input("هامش الربح ($/طن):",
                                       0.0, 1000.0, 50.0)
        sell = st.session_state["computed_ton_cost"] + profit
        total = sell * tons
        st.markdown(f"""
        <div class="price-card">
        <h4>🧾 فاتورة</h4>
        <p><b>العميل:</b> {client}</p>
        <p><b>الكمية:</b> {tons} طن</p>
        <p><b>سعر الطن:</b> ${sell:.2f}</p>
        <p style="font-size:1.3rem; color:#1b5e20;">
        <b>الإجمالي:</b> ${total:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    # ─── الديباجة ────────────────────────────────────────────────────────
    with tabs[tabs_titles.index("🖨️ الديباجة")]:
        st.markdown('<div class="section-title">🖨️ الديباجة</div>',
                    unsafe_allow_html=True)
        brand = st.text_input("اسم البراند:", APP_NAME)
        st.markdown(f"""
        <div style="border: 3px dashed #1b5e20; padding: 30px;
        border-radius: 15px;
        background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
        direction: rtl; text-align: center;">
        <img src="{st.session_state['active_animal_img']}"
        style="width:100%; max-height:200px; object-fit:cover;
        border-radius:12px; margin-bottom:15px;">
        <h2 style="color: #1b5e20;">🌟 {brand} 🌟</h2>
        <h3 style="color: #c62828;">{SUPERVISOR} — {SUPERVISOR_TITLE}</h3>
        <p style="background:#e8f5e9; padding:12px; border-radius:8px;
        color:#1b5e20; font-weight:bold;">
        🎯 {st.session_state['active_stage_title']}
        </p>
        <small style="color:#666;">📅 {datetime.now():%Y-%m-%d}</small>
        <br><small style="color:#c62828;">🤲 {DUA_SHORT}</small>
        </div>
        """, unsafe_allow_html=True)

    # ─── التحليلات ────────────────────────────────────────────────────────
    with tabs[tabs_titles.index("📈 التحليلات")]:
        st.markdown('<div class="section-title">📈 التحليلات المتقدمة</div>',
                    unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("الخلطات", "1,247")
        m2.metric("متوسط التكلفة", "$285")
        m3.metric("التوفير", "18%")
        m4.metric("رضا العملاء", "96%")

        st.markdown("---")
        st.subheader("🔮 تنبؤات الأسعار (PricePredictor)")
        predictor = PricePredictor()
        pred_ings = ["ذرة صفراء", "كسب فول صويا 44%",
                     "نخالة قمح (ردة)"]
        cols = st.columns(3)
        for idx, ing in enumerate(pred_ings):
            with cols[idx]:
                pred = predictor.predict_price(ing, 7)
                if pred.get('prediction'):
                    trend_icon = ("📈" if pred.get('trend') == 'up'
                                  else ("📉" if pred.get('trend') == 'down'
                                        else "➡️"))
                    st.metric(f"{trend_icon} {ing}",
                              f"${pred['prediction']:.2f}",
                              delta=f"{pred['prediction'] - (pred.get('current_price') or 0):.2f}")

        if PLOTLY_AVAILABLE:
            usage = pd.DataFrame({
                'المادة': ['ذرة', 'صويا', 'نخالة', 'زيوت', 'أملاح', 'أخرى'],
                'نسبة الاستخدام': [42, 23, 14, 8, 8, 5]})
            fig = px.pie(usage, values='نسبة الاستخدام',
                         names='المادة',
                         color_discrete_sequence=px.colors.sequential.Greens)
            st.plotly_chart(fig, use_container_width=True)

    # ─── مزارع الدجاج ─────────────────────────────────────────────────────
    with tabs[tabs_titles.index("🐔 مزارع الدجاج")]:
        st.markdown('<div class="section-title">🐔 مزارع الدجاج</div>',
                    unsafe_allow_html=True)
        with st.expander("➕ إضافة مزرعة"):
            nf_name = st.text_input("اسم المزرعة:", key="nf_name")
            nf_owner = st.text_input("المالك:", key="nf_owner")
            nf_phone = st.text_input("واتساب:", WHATSAPP_NUMBER,
                                       key="nf_phone")
            if st.button("💾 حفظ") and nf_name:
                st.session_state["broiler_farms"][nf_name] = {
                    "owner": nf_owner, "owner_phone": nf_phone,
                    "data": {"age": 1, "birds": 1000,
                             "weight_kg": 0.045, "feed_kg": 0.0,
                             "dead": 0, "temp": 33.0, "hum": 65.0}}
                st.success(f"✅ تمت إضافة {nf_name}")
                st.rerun()

        if st.session_state["broiler_farms"]:
            farms = list(st.session_state["broiler_farms"].keys())
            sel = st.selectbox("اختر مزرعة:", [""] + farms)
            if sel:
                d = st.session_state["broiler_farms"][sel]["data"]
                b1, b2 = st.columns(2)
                with b1:
                    d["age"] = st.number_input(
                        "العمر (يوم):", 1, 60, d["age"], key="bf_age")
                    d["birds"] = st.number_input(
                        "الطيور:", 1, value=d["birds"], key="bf_birds")
                    d["weight_kg"] = st.number_input(
                        "الوزن (كجم):", 0.0, 10.0,
                        float(d["weight_kg"]), 0.01, key="bf_w")
                    d["feed_kg"] = st.number_input(
                        "العلف (كجم):", 0.0,
                        float(d["feed_kg"]), 100.0, key="bf_f")
                with b2:
                    d["dead"] = st.number_input(
                        "النافق:", 0, value=d["dead"], key="bf_d")
                    d["temp"] = st.number_input(
                        "الحرارة:", 10.0, 45.0,
                        float(d["temp"]), key="bf_t")
                    d["hum"] = st.number_input(
                        "الرطوبة:", 20.0, 90.0,
                        float(d["hum"]), key="bf_h")
                alive = d["birds"] - d["dead"]
                gain = alive * (d["weight_kg"] - 0.045)
                adg = ((d["weight_kg"] - 0.045) * 1000 / d["age"]) \
                    if d["age"] > 0 else 0
                fcr = (d["feed_kg"] / gain) if gain > 0 else 0
                liv = 100 - (d["dead"] / d["birds"] * 100)
                epef = ((liv * d["weight_kg"]) / (d["age"] * fcr) * 100
                        if d["age"] > 0 and fcr > 0 else 0)
                k1, k2, k3 = st.columns(3)
                k1.metric("ADG (جم)", f"{adg:.1f}")
                k2.metric("FCR", f"{fcr:.2f}")
                k3.metric("EPEF", f"{epef:.0f}")

    # ─── التعليقات ────────────────────────────────────────────────────────
    with tabs[tabs_titles.index("💬 التعليقات")]:
        st.markdown('<div class="section-title">💬 تعليقات المختصين</div>',
                    unsafe_allow_html=True)
        st.markdown("### 📝 دفتر الملاحظات الفنية المشتركة:")
        st.text_area("الحالية:",
                     value=st.session_state["shared_comments"],
                     height=200, disabled=True)
        nc = st.text_area("📝 إضافة تعليق جديد:",
                          placeholder="اكتب توجيهاً أو ملاحظة...")
        if st.button("➕ نشر التعليق"):
            if nc:
                role = "المالك" if is_owner() else "مختص"
                st.session_state["shared_comments"] += (
                    f"\n• [{role} "
                    f"{datetime.now():%Y-%m-%d %H:%M}]: {nc}")
                st.success("✅ تم نشر التعليق!")
                st.rerun()
        st.metric("عدد التعليقات",
                  len(st.session_state["shared_comments"].split('\n')))

    # ─── إرسال الكود ──────────────────────────────────────────────────────
    with tabs[tabs_titles.index("📧 إرسال الكود")]:
        guide_section("إرسال الكود",
                       "إرسال السورس كود إلى البريد.")
        render_send_code()


# ═════════════════════════════════════════════════════════════════════════════
# القسم 47: المراجع + المساعدة + الدليل
# ═════════════════════════════════════════════════════════════════════════════

with tabs[tabs_titles.index("📚 المراجع")]:
    guide_section("المراجع العلمية",
                   "مصادر معتمدة في تغذية الحيوان.")
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>',
                unsafe_allow_html=True)
    for cat_key, cat_data in ScientificReferenceSystem.REFERENCES.items():
        with st.expander(f"{cat_data['icon']} {cat_data['title']}"):
            for ref in cat_data.get("references", []):
                st.markdown(f"""
                <div style='background:#f8f9fa; padding:12px;
                            border-radius:8px; margin-bottom:8px;
                            border-right:4px solid #2e7d32;'>
                    <b>{ref.get('title', 'عنوان غير محدد')}</b><br>
                    👤 {ref.get('authors', 'مؤلف غير محدد')}<br>
                    📅 {ref.get('year', 'سنة غير محددة')} |
                    📚 {ref.get('publisher', 'ناشر غير محدد')}<br>
                    <small>{ref.get('summary', '')}</small>
                </div>
                """, unsafe_allow_html=True)

    st.subheader("💡 المعرفة السريعة")
    q = st.text_input("اسأل عن مصطلح:")
    if q:
        answer = ScientificReferenceSystem.get_knowledge_answer(q)
        if answer:
            st.success(f"📖 {answer['answer']}")
            st.info(f"🔹 تبسيط: {answer['simplified']}")
        else:
            st.warning("لم أجد إجابة، حاول صياغة السؤال بشكل مختلف.")

with tabs[tabs_titles.index("💡 المساعدة")]:
    guide_section("المساعدة الذكية", "دليل سريع للمنصة.")
    st.markdown('<div class="section-title">💡 المساعدة الذكية</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    ### 🌟 خطوات الاستخدام:
    1. **اختر نوع الحيوان** من تبويب "تركيب الأعلاف"
    2. **حدد الحالة الفسيولوجية** والعمر والوزن
    3. **أدخل اسم طالب العلف** (المربي / المزرعة)
    4. **اختر المكونات العلفية** من المكتبة الموسعة
    5. **اضغط زر التشغيل** للحصول على الخلطة المثالية
    6. **حمّل التقرير PDF** أو **شارك الصورة**
    7. **أرسل العينة للمختبر** للتحليل

    ### 🧪 المختبر الذكي:
    - ارفع صورة تركيبة علفية
    - سيستخرج النظام البيانات تلقائياً

    ### 🌰 مكتبة الزيوت:
    - 15 زيتاً بمعايير NRC/INRA/FAO
    - حد أقصى مخصص لكل حيوان

    ### 🔧 الدعم الفني
    📧 {OWNER_EMAIL}
    📱 {WHATSAPP_NUMBER}
    """)
    if st.button("🔊 استمع للتعليمات"):
        voice_guide("مرحباً، هذا دليل استخدام منصة تاور نولجي العلمية.")

with tabs[tabs_titles.index("📖 الدليل")]:
    guide_section("دليل المستخدم", "شرح مفصل للمنصة.")
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#fff; padding:30px; border-radius:16px;
                box-shadow:0 8px 35px rgba(0,0,0,0.08);">
    <div class="book-chapter">📘 الفصل 1: مقدمة</div>
    <div class="book-body">
    {APP_NAME} منصة متكاملة لتركيب الأعلاف وإدارة الإنتاج الحيواني.
    تعتمد على البرمجة الخطية لحساب أقل تكلفة لخلطة علفية تلبي
    الاحتياجات الغذائية وفق المعايير العالمية NRC، INRA، FAO.
    </div>
    <div class="book-chapter">📗 الفصل 2: تركيب العلف</div>
    <div class="book-body">
    1. اختر الدولة والمكان.<br>
    2. اختر نوع الحيوان (أبقار/أغنام/ماعز/إبل/خيول/دواجن/سمان/أسماك).<br>
    3. حدد الحالة الفسيولوجية.<br>
    4. اختر أساس الحساب (DP أو CP).<br>
    5. اختر المكونات والزيوت.<br>
    6. اضغط تشغيل المحرك الذكي.<br>
    7. حمّل التقرير PDF/Excel.
    </div>
    <div class="book-chapter">🌰 الفصل 3: الزيوت</div>
    <div class="book-body">
    15 نوعاً من الزيوت النباتية والحيوانية بمعايير عالمية.<br>
    كل زيت له حد أقصى مختلف حسب الحيوان.<br>
    الحساب: كل 1% زيت ≈ 90 kcal/kg.
    </div>
    <div class="book-chapter">🍼 الفصل 4: بدائل الحليب</div>
    <div class="book-body">
    تركيب بدائل حليب للعجول والحملان والجديان والأمهار والإبل.
    </div>
    <div class="book-chapter">📷 الفصل 5: المختبر الذكي</div>
    <div class="book-body">
    ارفع صورة تركيبة، سيستخرج النظام القيم تلقائياً عبر OCR.
    </div>
    <div class="book-chapter">🕌 الفصل 6: مواقيت الصلاة</div>
    <div class="book-body">
    عرض مواقيت الصلاة للعديد من المدن العربية.
    </div>
    <div class="book-chapter">💊 الفصل 7: منبه الجرعات</div>
    <div class="book-body">
    سجل اللقاحات والفيتامينات مع تنبيهات الجرعات القادمة.
    </div>
    <div class="book-chapter">📈 الفصل 8: الإنتاج اليومي</div>
    <div class="book-body">
    سجل بيانات الإنتاج اليومية (حليب، بيض، وزن، نفوق).
    </div>
    <div class="book-chapter">🔊 الفصل 9: الشرح الصوتي</div>
    <div class="book-body">
    اضغط زر "الشرح الكامل" في بوابة الدخول.
    </div>
    </div>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# القسم 48: التذييل الثابت
# ═════════════════════════════════════════════════════════════════════════════

st.markdown(
    f'<div class="mini-signature">🌾 {APP_NAME} | {SUPERVISOR} © 2026</div>',
    unsafe_allow_html=True)
st.markdown(
    f'<div class="dua-fixed-banner">🤲 {DUA_SHORT} 🤲</div>',
    unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if st.button("🔊 اختبار الصوت (نهاية الصفحة)"):
    voice_guide("بسم الله الرحمن الرحيم، هذا اختبار للنظام الصوتي.")


# ═════════════════════════════════════════════════════════════════════════════
# نهاية الملف — End of File
# تاور نولجي Tawor Nology v18.0 | © 2026
# إشراف: م. عبدالقادر إسماعيل تاور - اختصاصي تغذية الحيوان
# 🕊️ رحم الله والدي إسماعيل تاور وأختي ابتسام 🕊️
# ═════════════════════════════════════════════════════════════════════════════
