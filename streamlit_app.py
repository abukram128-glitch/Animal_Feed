# ============================================================================
# ██████████████████████████████████████████████████████████████████████████████
# ██                                                                          ██
# ██             تاور نولجي TAWOR NOLOGY — الإصدار 5.0 الكامل               ██
# ██             للإنتاج الحيواني وتغذية الحيوان                             ██
# ██                                                                          ██
# ██  تحت إشراف: م. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان          ██
# ██                                                                          ██
# ██  صدقة جارية عن: الأستاذ إسماعيل تاور، والأخت ابتسام — رحمهما الله       ██
# ██                                                                          ██
# ██████████████████████████████████████████████████████████████████████████████
# ============================================================================

# ═══════════════════════════════════════════════════════════════════════════
# القسم 1: الاستيراد — Imports
# ═══════════════════════════════════════════════════════════════════════════

import streamlit as st
import numpy as np
import pandas as pd
import json
import os
import sys
import base64
import smtplib
import time
import urllib.parse
import re
import io
import sqlite3
import hashlib
import secrets
import warnings
import pickle
import random
import math
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta, date
from functools import lru_cache, wraps
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from collections import OrderedDict, defaultdict
from itertools import combinations, permutations, product

# منع تحذيرات المكتبات
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# ─── مكتبات الحسابات العلمية ───
try:
    from scipy.optimize import linprog, minimize
    from scipy.spatial import ConvexHull
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# ─── مكتبات الرسم البياني ───
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# ─── مكتبات الصوت ───
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# ─── مكتبات OCR ───
try:
    import pytesseract
    import cv2
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ─── مكتبات Excel ───
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, NamedStyle
    from openpyxl.utils import get_column_letter
    from openpyxl.chart import BarChart, PieChart, LineChart, Reference
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

# ─── مكتبات PDF واللغة العربية ───
try:
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.pagesizes import A4, A3, letter, landscape, portrait
    from reportlab.lib.units import inch, mm, cm
    from reportlab.lib.colors import HexColor, black, white, grey, Color
    from reportlab.platypus import (
        Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate,
        Frame, PageTemplate, PageBreak, KeepTogether, HRFlowable,
        ListFlowable, ListItem, CondPageBreak
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
    from reportlab.graphics.shapes import Drawing, Rect, Circle, Line, String
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
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
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
    from qrcode.image.styles.colormasks import SolidFillColorMask
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

try:
    from PIL import Image as PILImage, ImageDraw, ImageFont, ImageFilter
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════════════════
# القسم 2: دعاء الوالدين والأخت — يظهر في كل مكان
# ═══════════════════════════════════════════════════════════════════════════

DUA_SHORT = "اللهم اغفر لإسماعيل تاور وابتسام وارحمهما"

DUA_FULL = """
اللَّهُمَّ اغْفِرْ لَهُمَا وَارْحَمْهُمَا، وَعَافِهِمَا وَاعْفُ عَنْهُمَا،
وَأَكْرِمْ نُزُلَهُمَا، وَوَسِّعْ مُدْخَلَهُمَا،
وَاغْسِلْهُمَا بِالْمَاءِ وَالثَّلْجِ وَالْبَرَدِ،
وَنَقِّهِمَا مِنَ الذُّنُوبِ وَالْخَطَايَا كَمَا يُنَقَّى الثَّوْبُ الأَبْيَضُ مِنَ الدَّنَسِ،
وَأَبْدِلْهُمَا دَارًا خَيْرًا مِنْ دَارِهِمَا، وَأَهْلًا خَيْرًا مِنْ أَهْلِهِمَا،
وَأَدْخِلْهُمَا الجَنَّةَ، وَأَعِذْهُمَا مِنْ عَذَابِ القَبْرِ وَمِنْ عَذَابِ النَّارِ.
اللَّهُمَّ اجْعَلْ قُبُورَهُمَا رَوْضَةً مِنْ رِيَاضِ الجَنَّةِ، وَنَوِّرْ لَهُمَا فِيهَا.
اللَّهُمَّ ارْحَمْهُمَا فَإِنَّهُمَا كَانَا يَرْحَمَانِنَا،
وَاغْفِرْ لَهُمَا فَإِنَّهُمَا كَانَا يُحْسِنَانِ إِلَيْنَا.
اللَّهُمَّ اجْمَعْنَا بِهِمَا فِي مُسْتَقَرِّ رَحْمَتِكَ يَا أَرْحَمَ الرَّاحِمِينَ.
"""

DUA_QURAN = "﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾"

DUA_VISITOR_BANNER = """
🕌 <b>إلى زوارنا الكرام:</b><br>
هذه المنصة صدقةٌ جارية عن <b>الأستاذ إسماعيل تاور</b> و<b>الأخت ابتسام</b> — رحمهما الله.<br>
نسألكم بظهر الغيب أن تشاركونا الدعاء لهما بالمغفرة والرحمة، وأن يجعل الله قبرهما روضةً من رياض الجنة. 🤲
"""

DUA_HEADER = "🤲 اللهم اغفر لإسماعيل تاور وابتسام وارحمهما"

# ═══════════════════════════════════════════════════════════════════════════
# القسم 3: إعدادات Streamlit الأساسية
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="تاور نولجي Tawor Nology | للإنتاج الحيواني وتغذية الحيوان",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'mailto:abukram128@gmail.com',
        'Report a bug': 'mailto:abukram128@gmail.com',
        'About': f"""
        ### تاور نولجي Tawor Nology
        **الإنتاج الحيواني وتغذية الحيوان**
        
        إشراف: م. عبدالقادر إسماعيل تاور
        
        🕌 صدقة جارية عن:
        - الأستاذ إسماعيل تاور
        - الأخت ابتسام
        {DUA_SHORT}
        """
    }
)

# ═══════════════════════════════════════════════════════════════════════════
# القسم 4: الثوابت والإعدادات العامة
# ═══════════════════════════════════════════════════════════════════════════

APP_VERSION = "5.0.0"
APP_BUILD = "2026-STABLE-PRO"
APP_NAME = "تاور نولجي Tawor Nology"
APP_TAGLINE = "للإنتاج الحيواني وتغذية الحيوان"
SUPERVISOR = "م. عبدالقادر إسماعيل تاور"
SUPERVISOR_TITLE = "اختصاصي تغذية الحيوان"

# أكواد الدخول
CODES_DB = {
    "202687": {"role": "owner", "name": SUPERVISOR, "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1},
}

# ملفات
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]
LOGO_OPTIONS = ["logo.png", "logo.jpg", "LOGO.PNG", "tawor_logo.png"]
CITY_PRICES_FILE = "tawor_city_prices.json"
DB_FILE = "tawor_nology.db"

# اتصال
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"
SENDER_PASSWORD = "oynz rdli tsdy ekdq"
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"
PLATFORM_URL = "https://tawor-nology.streamlit.app"

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300
SESSION_TIMEOUT = 3600

# ═══════════════════════════════════════════════════════════════════════════
# القسم 5: معالج النصوص العربية — ArabicTextProcessor
# ═══════════════════════════════════════════════════════════════════════════

class ArabicTextProcessor:
    """معالج النصوص العربية لاستخدامها في PDF و Streamlit"""
    
    def __init__(self):
        self.cache = {}
    
    @staticmethod
    @lru_cache(maxsize=2000)
    def fix(text: str) -> str:
        """إصلاح النص العربي لعرضه بشكل صحيح"""
        if not text:
            return ""
        try:
            reshaped = arabic_reshaper.reshape(str(text))
            return get_display(reshaped)
        except Exception:
            return str(text)
    
    @staticmethod
    def strip_arabic(text: str) -> str:
        """إزالة التشكيل من النص العربي"""
        if not text:
            return ""
        import unicodedata
        return ''.join(
            c for c in unicodedata.normalize('NFD', str(text))
            if unicodedata.category(c) != 'Mn'
        )
    
    @staticmethod
    def normalize(text: str) -> str:
        """تطبيع النص العربي للمقارنة"""
        if not text:
            return ""
        text = str(text).strip()
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ى', 'ي').replace('ة', 'ه')
        return text

arabic_processor = ArabicTextProcessor()

def ar(text: str) -> str:
    """اختصار لاستخدام المعالج"""
    return arabic_processor.fix(text)

# ═══════════════════════════════════════════════════════════════════════════
# القسم 6: مكتبة الأعلاف الشاملة — BIG_FEEDS_LIBRARY
# ═══════════════════════════════════════════════════════════════════════════
# CP = البروتين الخام (%) 
# DC = معامل الهضم (0-1)
# SE = معادل النشاء (وحدة)
# NDF = الألياف المتعادلة (%)
# ADF = الألياف الحمضية (%)
# EE = الدهن الخام (%)
# ASH = الرماد (%)
# Ca = الكالسيوم (%)
# P = الفسفور (%)
# ============================================================================

BIG_FEEDS_LIBRARY = {
    
    # ───────────────────────────────────────────────────────────
    # الحبوب ومصادر الطاقة الرئيسية
    # ───────────────────────────────────────────────────────────
    "🌾 الحبوب ومصادر الطاقة الكبرى": {
        "ذرة صفراء": {
            "CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2,
            "EE": 3.8, "ASH": 1.3, "Ca": 0.02, "P": 0.27,
            "desc": "المصدر الأساسي للطاقة في أعلاف الدواجن والمجترات"
        },
        "ذرة بيضاء": {
            "CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5,
            "EE": 3.5, "ASH": 1.4, "Ca": 0.02, "P": 0.26,
            "desc": "بديل الذرة الصفراء، أقل في الصبغات"
        },
        "ذرة شامية (أمريكا)": {
            "CP": 8.3, "DC": 0.86, "SE": 82.0, "NDF": 9.0, "ADF": 3.0,
            "EE": 4.0, "ASH": 1.2, "Ca": 0.02, "P": 0.28,
            "desc": "نسبة طاقة أعلى من الذرة العادية"
        },
        "شعير مطحون": {
            "CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5,
            "EE": 2.2, "ASH": 2.5, "Ca": 0.05, "P": 0.35,
            "desc": "يحتاج إنزيمات بيتا جلوكاناز"
        },
        "شعير كامل": {
            "CP": 10.8, "DC": 0.75, "SE": 68.0, "NDF": 22.0, "ADF": 9.0,
            "EE": 2.0, "ASH": 2.8, "Ca": 0.05, "P": 0.33,
            "desc": "قشرة أعلى، هضم أقل"
        },
        "سورجم (فتريتة)": {
            "CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5,
            "EE": 3.0, "ASH": 1.8, "Ca": 0.03, "P": 0.30,
            "desc": "بديل اقتصادي للذرة في السودان"
        },
        "قمح محلي مصنّع": {
            "CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8,
            "EE": 2.0, "ASH": 1.6, "Ca": 0.04, "P": 0.32,
            "desc": "يحتاج إنزيمات زيلاناز"
        },
        "قمح مستورد": {
            "CP": 11.5, "DC": 0.87, "SE": 78.0, "NDF": 11.0, "ADF": 3.5,
            "EE": 1.9, "ASH": 1.5, "Ca": 0.04, "P": 0.33,
            "desc": "جودة عالية، طاقة ممتازة"
        },
        "جريش أرز رزاز": {
            "CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5,
            "EE": 8.5, "ASH": 4.2, "Ca": 0.06, "P": 0.30,
            "desc": "طاقة عالية لكن دهن عالي"
        },
        "دخن محلي غزير": {
            "CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5,
            "EE": 4.0, "ASH": 2.2, "Ca": 0.05, "P": 0.31,
            "desc": "محصول محلي، قيمة جيدة"
        },
        "شوفان علفي": {
            "CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5,
            "EE": 5.0, "ASH": 3.0, "Ca": 0.08, "P": 0.35,
            "desc": "مناسب للخيول والمجترات"
        },
        "كسرة خبز مجففة": {
            "CP": 10.5, "DC": 0.82, "SE": 75.0, "NDF": 8.0, "ADF": 3.5,
            "EE": 5.5, "ASH": 3.5, "Ca": 0.10, "P": 0.20,
            "desc": "مخلفات مخابز، اقتصادية"
        },
        "بسكويت مكسر": {
            "CP": 8.5, "DC": 0.85, "SE": 85.0, "NDF": 4.0, "ADF": 2.0,
            "EE": 12.0, "ASH": 2.5, "Ca": 0.08, "P": 0.18,
            "desc": "طاقة عالية جداً، يستخدم بنسب محدودة"
        },
    },
    
    # ───────────────────────────────────────────────────────────
    # الأكساب ومصادر البروتين النباتي
    # ───────────────────────────────────────────────────────────
    "🌱 الأكساب ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {
            "CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5,
            "EE": 1.5, "ASH": 5.5, "Ca": 0.20, "P": 0.65,
            "desc": "ممتاز للدواجن والمجترات، متوفر بالسودان"
        },
        "كسب فول صويا 44%": {
            "CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0,
            "EE": 1.8, "ASH": 6.0, "Ca": 0.35, "P": 0.65,
            "desc": "المرجع العالمي للبروتين النباتي"
        },
        "كسب فول صويا 48%": {
            "CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0,
            "EE": 1.5, "ASH": 6.2, "Ca": 0.35, "P": 0.65,
            "desc": "بروتين أعلى، جودة ممتازة"
        },
        "كسب فول صويا 46%": {
            "CP": 46.0, "DC": 0.905, "SE": 75.0, "NDF": 12.5, "ADF": 7.5,
            "EE": 1.6, "ASH": 6.1, "Ca": 0.35, "P": 0.65,
            "desc": "بروتين متوسط، قياسي"
        },
        "كسب عباد الشمس 36%": {
            "CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5,
            "EE": 2.5, "ASH": 6.5, "Ca": 0.40, "P": 1.00,
            "desc": "بروتين متوسط، ألياف عالية"
        },
        "كسب عباد الشمس 32%": {
            "CP": 32.0, "DC": 0.72, "SE": 38.0, "NDF": 42.0, "ADF": 28.0,
            "EE": 2.0, "ASH": 7.0, "Ca": 0.42, "P": 0.95,
            "desc": "غير مقشور، رخيص"
        },
        "كسب بذور القطن (مقشور)": {
            "CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5,
            "EE": 1.2, "ASH": 6.5, "Ca": 0.20, "P": 1.10,
            "desc": "يحتاج معادل الجوسيبول للدواجن"
        },
        "كسب بذور الكتان": {
            "CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5,
            "EE": 2.8, "ASH": 5.8, "Ca": 0.35, "P": 0.85,
            "desc": "غني بأوميغا 3، جيد للخيول"
        },
        "كسب السمسم المحسن": {
            "CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5,
            "EE": 8.5, "ASH": 12.5, "Ca": 2.00, "P": 1.20,
            "desc": "غني بالكالسيوم والميثيونين"
        },
        "كسب جلوتين الذرة 60%": {
            "CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5,
            "EE": 2.5, "ASH": 3.5, "Ca": 0.15, "P": 0.50,
            "desc": "بروتين عالي، للدواجن خاصة"
        },
        "كسب جلوتين الذرة 40%": {
            "CP": 40.0, "DC": 0.88, "SE": 72.0, "NDF": 15.0, "ADF": 8.0,
            "EE": 3.0, "ASH": 5.0, "Ca": 0.18, "P": 0.55,
            "desc": "بروتين متوسط"
        },
        "كسب نواة النخيل": {
            "CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5,
            "EE": 6.5, "ASH": 4.5, "Ca": 0.30, "P": 0.55,
            "desc": "بروتين منخفض، طاقة جيدة"
        },
        "كسب بذور العنب": {
            "CP": 12.0, "DC": 0.55, "SE": 30.0, "NDF": 45.0, "ADF": 32.0,
            "EE": 7.5, "ASH": 6.0, "Ca": 0.25, "P": 0.40,
            "desc": "يحتاج دراسة الجدوى"
        },
    },
    
    # ───────────────────────────────────────────────────────────
    # المخلفات الزراعية والصناعية
    # ───────────────────────────────────────────────────────────
    "🚜 المخلفات الزراعية والصناعية": {
        "نخالة قمح (ردة)": {
            "CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5,
            "EE": 3.5, "ASH": 5.5, "Ca": 0.12, "P": 1.10,
            "desc": "مخلف الطحن، ممتازة للمجترات"
        },
        "نخالة ذرة": {
            "CP": 9.5, "DC": 0.65, "SE": 40.0, "NDF": 40.0, "ADF": 15.0,
            "EE": 4.0, "ASH": 2.0, "Ca": 0.10, "P": 0.75,
            "desc": "مخلف طحن الذرة"
        },
        "البرسيم الجاف (الدريس)": {
            "CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5,
            "EE": 2.0, "ASH": 10.5, "Ca": 1.50, "P": 0.25,
            "desc": "علف أخضر مجفف، غني بالكالسيوم"
        },
        "برسيم حجازي": {
            "CP": 18.0, "DC": 0.62, "SE": 38.0, "NDF": 40.0, "ADF": 30.0,
            "EE": 2.2, "ASH": 11.0, "Ca": 1.60, "P": 0.26,
            "desc": "جودة عالية"
        },
        "مولاس قصب السكر": {
            "CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8,
            "EE": 0.5, "ASH": 8.5, "Ca": 0.70, "P": 0.05,
            "desc": "مصدر طاقة سريع، يحسن الاستساغة"
        },
        "تبن قمح ناعم": {
            "CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5,
            "EE": 1.5, "ASH": 8.5, "Ca": 0.30, "P": 0.08,
            "desc": "مالئ منخفض القيمة"
        },
        "تبن فول": {
            "CP": 4.5, "DC": 0.40, "SE": 22.0, "NDF": 68.0, "ADF": 42.0,
            "EE": 1.2, "ASH": 7.5, "Ca": 0.35, "P": 0.10,
            "desc": "أفضل من تبن القمح"
        },
        "قشر فول سوداني مطحون": {
            "CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5,
            "EE": 1.0, "ASH": 5.5, "Ca": 0.25, "P": 0.10,
            "desc": "مادة مالئة، نسبة ألياف عالية"
        },
        "سرسة الأرز المطحونة": {
            "CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5,
            "EE": 12.5, "ASH": 15.5, "Ca": 0.15, "P": 0.08,
            "desc": "عالية السيليكا، تستخدم بحذر"
        },
        "قش أرز": {
            "CP": 3.5, "DC": 0.30, "SE": 15.0, "NDF": 70.0, "ADF": 45.0,
            "EE": 1.5, "ASH": 12.0, "Ca": 0.20, "P": 0.06,
            "desc": "مالئ خشبي، هضم منخفض"
        },
        "مخلفات النخيل (تمر مجفف)": {
            "CP": 6.5, "DC": 0.70, "SE": 60.0, "NDF": 25.0, "ADF": 15.0,
            "EE": 5.0, "ASH": 3.5, "Ca": 0.15, "P": 0.15,
            "desc": "مصدر طاقة جيد، مستساغ للإبل"
        },
        "قشور الفول السوداني الكاملة": {
            "CP": 6.5, "DC": 0.40, "SE": 22.0, "NDF": 58.0, "ADF": 38.0,
            "EE": 2.5, "ASH": 4.0, "Ca": 0.20, "P": 0.12,
            "desc": "أفضل من المطحونة"
        },
    },
    
    # ───────────────────────────────────────────────────────────
    # مصادر البروتين الحيواني
    # ───────────────────────────────────────────────────────────
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك (Fishmeal 60%)": {
            "CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5,
            "EE": 8.5, "ASH": 22.5, "Ca": 5.50, "P": 3.20,
            "desc": "الأفضل في الأحماض الأمينية"
        },
        "مسحوق أسماك فاخر (72%)": {
            "CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0,
            "EE": 9.5, "ASH": 18.5, "Ca": 4.80, "P": 2.80,
            "desc": "درجة ممتازة، غالي"
        },
        "مسحوق اللحم والعظم": {
            "CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5,
            "EE": 10.5, "ASH": 32.5, "Ca": 9.00, "P": 4.50,
            "desc": "بروتين حيواني، للدواجن بحذر"
        },
        "مسحوق الدم المجفف": {
            "CP": 80.0, "DC": 0.65, "SE": 55.0, "NDF": 1.0, "ADF": 0.5,
            "EE": 1.5, "ASH": 6.0, "Ca": 0.30, "P": 0.30,
            "desc": "بروتين عالي، لكن غير متوازن"
        },
        "مسحوق ريش هيدروليزي": {
            "CP": 82.0, "DC": 0.70, "SE": 60.0, "NDF": 1.5, "ADF": 1.0,
            "EE": 3.0, "ASH": 4.0, "Ca": 0.25, "P": 0.35,
            "desc": "بروتين عالي، لكن ليسين منخفض"
        },
        "مركزات دواجن وسمان": {
            "CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5,
            "EE": 3.5, "ASH": 12.5, "Ca": 2.50, "P": 1.20,
            "desc": "مخلوط جاهز مع الفيتامينات والمعادن"
        },
        "مركزات خيول ومجترات": {
            "CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5,
            "EE": 3.0, "ASH": 15.5, "Ca": 3.00, "P": 1.50,
            "desc": "مركز للمجترات"
        },
        "حليب مجفف منزوع الدسم": {
            "CP": 34.0, "DC": 0.95, "SE": 78.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 1.0, "ASH": 8.0, "Ca": 1.30, "P": 1.00,
            "desc": "يستخدم لبدائل الحليب"
        },
        "حليب مجفف كامل": {
            "CP": 26.0, "DC": 0.95, "SE": 88.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 28.0, "ASH": 6.0, "Ca": 1.00, "P": 0.80,
            "desc": "يستخدم لبدائل الحليب"
        },
    },
    
    # ───────────────────────────────────────────────────────────
    # الأحماض الأمينية البلورية
    # ───────────────────────────────────────────────────────────
    "🧪 الأحماض الأمينية البلورية": {
        "ليسين نقي (L-Lysine HCl)": {
            "CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0,
            "desc": "حمض أميني أساسي، ضروري للتسمين"
        },
        "ليسين سلفات (L-Lysine SO4)": {
            "CP": 79.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0,
            "desc": "بديل اقتصادي"
        },
        "ميثيونين نقي (DL-Methionine)": {
            "CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 0.3, "Ca": 0.0, "P": 0.0,
            "desc": "أول حمض محدود للدواجن"
        },
        "ميثيونين هيدروكسي (MHA)": {
            "CP": 88.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0,
            "desc": "بديل سائل"
        },
        "ثريونين نقي (L-Threonine)": {
            "CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0,
            "desc": "حمض أساسي ثالث"
        },
        "تريبتوفان نقي (L-Tryptophan)": {
            "CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0,
            "desc": "منظم الشهية والمزاج"
        },
        "فالين نقي (L-Valine)": {
            "CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0,
            "desc": "حمض متشعب السلسلة"
        },
        "أرجينين (L-Arginine)": {
            "CP": 98.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0,
            "desc": "ضروري للدواجن الصغيرة"
        },
    },
    
    # ───────────────────────────────────────────────────────────
    # الإنزيمات والبريمكسات
    # ───────────────────────────────────────────────────────────
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن (Premix Broiler)": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 8.0,
            "desc": "فيتامينات ومعادن كاملة للدواجن"
        },
        "بريمكس بياض وبشاير (Layer Premix)": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 100.0, "Ca": 22.0, "P": 7.0,
            "desc": "لكامل الدجاج البياض"
        },
        "بريمكس أبقار حلابة": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0,
            "desc": "للأبقار عالية الإدرار"
        },
        "بريمكس مجترات عام": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 9.0,
            "desc": "أغنام، ماعز، إبل"
        },
        "بريمكس خيول وأمهار": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 8.0,
            "desc": "متوازن للخيول"
        },
        "إنزيم الفايتيز (Phytase 5000)": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 5.0, "Ca": 0.0, "P": 0.0,
            "desc": "يحرر الفسفور النباتي المرتبط"
        },
        "إنزيم الـ NSP (Xylanase+β-Glucanase)": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 3.0, "Ca": 0.0, "P": 0.0,
            "desc": "لكسر جدران الخلايا النباتية"
        },
        "إنزيم البروتييز (Protease)": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 2.0, "Ca": 0.0, "P": 0.0,
            "desc": "يحسن هضم البروتين"
        },
        "كبريتات الحديدوز": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 98.0, "Ca": 0.0, "P": 0.0,
            "desc": "معادل الجوسيبول في القطن"
        },
        "مستخلص الخمائر (MOS)": {
            "CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5,
            "EE": 1.5, "ASH": 8.5, "Ca": 0.10, "P": 0.20,
            "desc": "يعزز المناعة والهضم"
        },
        "خمائر حية (Yeast Culture)": {
            "CP": 45.0, "DC": 0.75, "SE": 30.0, "NDF": 8.0, "ADF": 4.0,
            "EE": 1.0, "ASH": 8.0, "Ca": 0.15, "P": 1.20,
            "desc": "للمجترات خاصة"
        },
    },
    
    # ───────────────────────────────────────────────────────────
    # الأملاح والمعادن
    # ───────────────────────────────────────────────────────────
    "🪨 الأملاح والمعادن الأساسية": {
        "الحجر الجيري (بودرة بلاط)": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 99.5, "Ca": 38.0, "P": 0.0,
            "desc": "مصدر كالسيوم اقتصادي"
        },
        "فوسفات ثنائي الكالسيوم (DCP)": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 98.5, "Ca": 23.0, "P": 18.0,
            "desc": "مصدر Ca و P متوازن"
        },
        "فوسفات أحادي الكالسيوم (MCP)": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 99.0, "Ca": 17.0, "P": 22.0,
            "desc": "فوسفور أعلى"
        },
        "ملح الطعام": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 99.9, "Ca": 0.0, "P": 0.0,
            "desc": "كلوريد الصوديوم"
        },
        "بيكربونات الصوديوم (الصودا)": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 99.0, "Ca": 0.0, "P": 0.0,
            "desc": "منظم حموضة الكرش"
        },
        "أكسيد المغنيسيوم العلفي": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 99.5, "Ca": 0.0, "P": 0.0,
            "desc": "مصدر مغنيسيوم"
        },
        "كبريتات المغنيسيوم": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 98.0, "Ca": 0.0, "P": 0.0,
            "desc": "ملين ومكمل مغنيسيوم"
        },
        "يوريا علفية محصنة": {
            "CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 1.0, "Ca": 0.0, "P": 0.0,
            "desc": "للمجترات فقط، بحذر شديد"
        },
        "مضاد سموم فطرية": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 85.0, "Ca": 0.0, "P": 0.0,
            "desc": "حماية من الأفلاتوكسين"
        },
        "مضاد أكسدة (BHT)": {
            "CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
            "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0,
            "desc": "يحمي الدهون من التزنخ"
        },
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# القسم 7: المعايير القياسية للعناصر الغذائية
# NUTRIENT_STANDARDS — وفق NRC و INRA و Ross
# ═══════════════════════════════════════════════════════════════════════════

NUTRIENT_STANDARDS = {
    # ─── الأبقار ───
    "أبقار_حليب_عالي":    {"CP": 18.0, "DP": 13.5, "SE": 72.0, "NDF": 32.0, "ADF": 20.0, "EE": 4.5, "ASH": 8.0, "Ca": 0.75, "P": 0.45},
    "أبقار_حليب_متوسط":   {"CP": 16.0, "DP": 12.5, "SE": 68.0, "NDF": 35.0, "ADF": 22.0, "EE": 4.0, "ASH": 8.0, "Ca": 0.65, "P": 0.40},
    "أبقار_حليب_منخفض":   {"CP": 14.5, "DP": 11.0, "SE": 64.0, "NDF": 38.0, "ADF": 24.0, "EE": 3.5, "ASH": 8.5, "Ca": 0.55, "P": 0.35},
    "أبقار_تسمين_مكثف":   {"CP": 14.0, "DP": 10.5, "SE": 70.0, "NDF": 35.0, "ADF": 22.0, "EE": 4.0, "ASH": 7.5, "Ca": 0.60, "P": 0.35},
    "أبقار_تسمين_عادي":   {"CP": 13.0, "DP": 10.0, "SE": 65.0, "NDF": 40.0, "ADF": 25.0, "EE": 3.5, "ASH": 7.5, "Ca": 0.55, "P": 0.32},
    "أبقار_حمل_أخير":     {"CP": 15.0, "DP": 11.5, "SE": 66.0, "NDF": 36.0, "ADF": 23.0, "EE": 3.8, "ASH": 8.0, "Ca": 0.65, "P": 0.40},
    "أبقار_صيانة":        {"CP": 11.0, "DP": 8.0,  "SE": 55.0, "NDF": 45.0, "ADF": 28.0, "EE": 3.0, "ASH": 8.0, "Ca": 0.45, "P": 0.28},
    
    # ─── الأغنام ───
    "أغنام_تسمين_مكثف":   {"CP": 15.0, "DP": 12.0, "SE": 65.0, "NDF": 30.0, "ADF": 18.0, "EE": 3.8, "ASH": 8.0, "Ca": 0.65, "P": 0.35},
    "أغنام_تسمين_عادي":   {"CP": 13.5, "DP": 10.5, "SE": 60.0, "NDF": 35.0, "ADF": 22.0, "EE": 3.5, "ASH": 8.0, "Ca": 0.55, "P": 0.32},
    "أغنام_حليب":         {"CP": 16.0, "DP": 12.8, "SE": 66.0, "NDF": 30.0, "ADF": 19.0, "EE": 4.0, "ASH": 8.5, "Ca": 0.75, "P": 0.42},
    "أغنام_حمل_أخير":     {"CP": 14.0, "DP": 11.0, "SE": 62.0, "NDF": 33.0, "ADF": 20.0, "EE": 3.5, "ASH": 8.0, "Ca": 0.60, "P": 0.35},
    "أغنام_صيانة":        {"CP": 11.0, "DP": 8.0,  "SE": 50.0, "NDF": 45.0, "ADF": 28.0, "EE": 3.0, "ASH": 8.0, "Ca": 0.45, "P": 0.28},
    "حملان_بداية":        {"CP": 18.0, "DP": 14.5, "SE": 70.0, "NDF": 22.0, "ADF": 14.0, "EE": 4.0, "ASH": 7.5, "Ca": 0.70, "P": 0.40},
    
    # ─── الماعز ───
    "ماعز_تسمين":         {"CP": 14.5, "DP": 11.5, "SE": 62.0, "NDF": 33.0, "ADF": 20.0, "EE": 3.5, "ASH": 8.0, "Ca": 0.60, "P": 0.35},
    "ماعز_حليب_عالي":     {"CP": 16.5, "DP": 13.0, "SE": 67.0, "NDF": 30.0, "ADF": 18.0, "EE": 4.0, "ASH": 8.5, "Ca": 0.75, "P": 0.42},
    "ماعز_حليب_متوسط":    {"CP": 15.0, "DP": 11.8, "SE": 62.0, "NDF": 33.0, "ADF": 20.0, "EE": 3.5, "ASH": 8.5, "Ca": 0.65, "P": 0.38},
    "ماعز_حمل_أخير":      {"CP": 13.5, "DP": 10.5, "SE": 60.0, "NDF": 34.0, "ADF": 21.0, "EE": 3.5, "ASH": 8.0, "Ca": 0.60, "P": 0.35},
    "ماعز_صيانة":         {"CP": 10.5, "DP": 7.8,  "SE": 48.0, "NDF": 45.0, "ADF": 28.0, "EE": 3.0, "ASH": 8.0, "Ca": 0.45, "P": 0.28},
    "جديان_بداية":        {"CP": 17.5, "DP": 14.0, "SE": 68.0, "NDF": 22.0, "ADF": 14.0, "EE": 4.0, "ASH": 7.5, "Ca": 0.70, "P": 0.40},
    
    # ─── الإبل ───
    "إبل_نمو":            {"CP": 14.0, "DP": 10.5, "SE": 60.0, "NDF": 38.0, "ADF": 24.0, "EE": 3.5, "ASH": 8.0, "Ca": 0.65, "P": 0.38},
    "إبل_تسمين":          {"CP": 13.0, "DP": 9.5,  "SE": 65.0, "NDF": 35.0, "ADF": 22.0, "EE": 3.8, "ASH": 7.5, "Ca": 0.60, "P": 0.35},
    "إبل_حليب_عالي":      {"CP": 17.0, "DP": 13.0, "SE": 68.0, "NDF": 32.0, "ADF": 20.0, "EE": 4.5, "ASH": 8.5, "Ca": 0.80, "P": 0.45},
    "إبل_حليب_متوسط":     {"CP": 15.5, "DP": 12.0, "SE": 64.0, "NDF": 35.0, "ADF": 22.0, "EE": 4.0, "ASH": 8.5, "Ca": 0.70, "P": 0.40},
    "إبل_سباق":           {"CP": 18.0, "DP": 14.0, "SE": 72.0, "NDF": 30.0, "ADF": 18.0, "EE": 5.0, "ASH": 9.0, "Ca": 0.85, "P": 0.50},
    "إبل_صيانة":          {"CP": 10.0, "DP": 7.5,  "SE": 50.0, "NDF": 45.0, "ADF": 28.0, "EE": 3.0, "ASH": 8.0, "Ca": 0.45, "P": 0.28},
    "حوار_بداية":         {"CP": 18.0, "DP": 14.0, "SE": 70.0, "NDF": 28.0, "ADF": 17.0, "EE": 4.5, "ASH": 8.0, "Ca": 0.75, "P": 0.45},
    
    # ─── الخيول ───
    "خيول_رياضة_مكثف":    {"CP": 13.0, "DP": 10.0, "SE": 70.0, "NDF": 32.0, "ADF": 20.0, "EE": 5.0, "ASH": 7.5, "Ca": 0.60, "P": 0.35},
    "خيول_رياضة_عادي":    {"CP": 12.0, "DP": 9.5,  "SE": 65.0, "NDF": 35.0, "ADF": 22.0, "EE": 4.5, "ASH": 7.5, "Ca": 0.55, "P": 0.32},
    "خيول_نمو":           {"CP": 15.0, "DP": 12.5, "SE": 65.0, "NDF": 30.0, "ADF": 18.0, "EE": 4.0, "ASH": 8.0, "Ca": 0.75, "P": 0.42},
    "أمهار_بداية":        {"CP": 17.0, "DP": 14.0, "SE": 70.0, "NDF": 25.0, "ADF": 15.0, "EE": 4.5, "ASH": 8.0, "Ca": 0.85, "P": 0.50},
    "فرسات_مرضعات":       {"CP": 15.5, "DP": 12.5, "SE": 68.0, "NDF": 32.0, "ADF": 20.0, "EE": 4.5, "ASH": 8.0, "Ca": 0.75, "P": 0.42},
    "خيول_صيانة":         {"CP": 10.0, "DP": 7.5,  "SE": 55.0, "NDF": 45.0, "ADF": 28.0, "EE": 3.5, "ASH": 8.0, "Ca": 0.45, "P": 0.28},
    
    # ─── الدواجن اللاحم ───
    "دواجن_بادي":         {"CP": 23.0, "DP": 20.0, "SE": 76.0, "NDF": 8.0,  "ADF": 4.0,  "EE": 5.0, "ASH": 6.5, "Ca": 1.00, "P": 0.50},
    "دواجن_نامي":         {"CP": 21.0, "DP": 18.5, "SE": 74.0, "NDF": 9.0,  "ADF": 5.0,  "EE": 4.5, "ASH": 6.0, "Ca": 0.90, "P": 0.45},
    "دواجن_ناهي":         {"CP": 19.0, "DP": 16.5, "SE": 75.0, "NDF": 10.0, "ADF": 5.5,  "EE": 4.0, "ASH": 6.0, "Ca": 0.85, "P": 0.42},
    "دواجن_بياض_بادي":    {"CP": 20.0, "DP": 17.5, "SE": 72.0, "NDF": 10.0, "ADF": 5.5,  "EE": 4.0, "ASH": 7.0, "Ca": 1.00, "P": 0.50},
    "دواجن_بياض_نامي":    {"CP": 18.0, "DP": 15.5, "SE": 70.0, "NDF": 11.0, "ADF": 6.0,  "EE": 4.0, "ASH": 8.0, "Ca": 1.20, "P": 0.48},
    "دواجن_بياض_ناهي":    {"CP": 16.5, "DP": 14.5, "SE": 70.0, "NDF": 12.0, "ADF": 6.0,  "EE": 4.0, "ASH": 9.5, "Ca": 2.00, "P": 0.42},
    "دواجن_بياض_إنتاج":   {"CP": 17.5, "DP": 15.5, "SE": 72.0, "NDF": 11.0, "ADF": 6.0,  "EE": 4.2, "ASH": 11.5, "Ca": 3.80, "P": 0.45},
    "دواجن_أمهات":        {"CP": 16.0, "DP": 14.0, "SE": 70.0, "NDF": 11.0, "ADF": 6.0,  "EE": 4.0, "ASH": 10.0, "Ca": 3.00, "P": 0.42},
    
    # ─── السمان ───
    "سمان_بادي":          {"CP": 24.0, "DP": 20.5, "SE": 74.0, "NDF": 8.0,  "ADF": 4.0,  "EE": 5.0, "ASH": 6.5, "Ca": 1.00, "P": 0.55},
    "سمان_نامي":          {"CP": 22.0, "DP": 18.5, "SE": 72.0, "NDF": 9.0,  "ADF": 4.5,  "EE": 4.5, "ASH": 6.0, "Ca": 0.90, "P": 0.50},
    "سمان_ناهي":          {"CP": 20.0, "DP": 17.0, "SE": 70.0, "NDF": 10.0, "ADF": 5.0,  "EE": 4.0, "ASH": 6.0, "Ca": 0.85, "P": 0.45},
    "سمان_بياض":          {"CP": 18.0, "DP": 15.0, "SE": 68.0, "NDF": 11.0, "ADF": 5.5,  "EE": 4.0, "ASH": 9.0, "Ca": 2.50, "P": 0.45},
    
    # ─── الأسماك ───
    "أسماك_بادئ_زريعة":   {"CP": 40.0, "DP": 32.0, "SE": 72.0, "NDF": 8.0,  "ADF": 4.0,  "EE": 8.0, "ASH": 11.0, "Ca": 1.50, "P": 0.90},
    "أسماك_نمو_متوسط":    {"CP": 32.0, "DP": 25.0, "SE": 70.0, "NDF": 12.0, "ADF": 6.0,  "EE": 6.0, "ASH": 9.0, "Ca": 1.00, "P": 0.70},
    "أسماك_تسمين":        {"CP": 28.0, "DP": 22.0, "SE": 68.0, "NDF": 13.0, "ADF": 7.0,  "EE": 6.5, "ASH": 9.5, "Ca": 0.90, "P": 0.65},
    "أسماك_أمهات":        {"CP": 35.0, "DP": 28.0, "SE": 72.0, "NDF": 10.0, "ADF": 5.0,  "EE": 8.0, "ASH": 10.0, "Ca": 1.20, "P": 0.80},
    
    # ─── الأرانب ───
    "أرانب_نمو":          {"CP": 17.0, "DP": 14.0, "SE": 65.0, "NDF": 30.0, "ADF": 18.0, "EE": 3.5, "ASH": 8.0, "Ca": 0.80, "P": 0.55},
    "أرانب_حليب":         {"CP": 18.0, "DP": 15.0, "SE": 68.0, "NDF": 28.0, "ADF": 17.0, "EE": 3.8, "ASH": 8.5, "Ca": 1.00, "P": 0.65},
    "أرانب_صيانة":        {"CP": 14.0, "DP": 11.0, "SE": 58.0, "NDF": 35.0, "ADF": 22.0, "EE": 3.0, "ASH": 8.5, "Ca": 0.60, "P": 0.45},
}

# ═══════════════════════════════════════════════════════════════════════════
# القسم 8: دوال حساب القيم الغذائية
# ═══════════════════════════════════════════════════════════════════════════

def compute_formula_nutrients(formula: dict) -> dict:
    """
    حساب جميع العناصر الغذائية لخلطة معطاة.
    
    Parameters
    ----------
    formula : dict
        قاموس يحتوي على {اسم_المكون: النسبة_المئوية}
    
    Returns
    -------
    dict
        قاموس يحتوي على العناصر: CP, DP, SE, NDF, ADF, EE, ASH, Ca, P
    """
    totals = {
        "CP": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
        "EE": 0.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0
    }
    
    for ing, pct in formula.items():
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat:
                d = cat[ing]
                factor = pct / 100.0
                totals["CP"]  += factor * d.get("CP", 0.0)
                totals["DP"]  += factor * d.get("CP", 0.0) * d.get("DC", 0.0)
                totals["SE"]  += factor * d.get("SE", 0.0)
                totals["NDF"] += factor * d.get("NDF", 0.0)
                totals["ADF"] += factor * d.get("ADF", 0.0)
                totals["EE"]  += factor * d.get("EE", 0.0)
                totals["ASH"] += factor * d.get("ASH", 0.0)
                totals["Ca"]  += factor * d.get("Ca", 0.0)
                totals["P"]   += factor * d.get("P", 0.0)
                break
    
    return totals


def compute_total_digestible_nutrients(formula: dict) -> dict:
    """حساب العناصر المهضومة بنسبة أدق"""
    result = {}
    for ing, pct in formula.items():
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat:
                d = cat[ing]
                result[ing] = {
                    "pct": pct,
                    "CP_kg": pct * d["CP"] / 100.0,
                    "DP_kg": pct * d["CP"] * d["DC"] / 100.0,
                    "SE_units": pct * d["SE"] / 100.0,
                    "NDF_kg": pct * d.get("NDF", 0) / 100.0,
                }
                break
    return result


def compute_nutritive_ratio(se_value: float, dp_value: float) -> float:
    """حساب النسبة الغذائية (Nutritive Ratio) = SE / DP"""
    if dp_value <= 0:
        return 0.0
    return se_value / dp_value


def compute_starch_equivalent_from_ingredients(formula: dict) -> float:
    """حساب معادل النشاء الإجمالي"""
    total = 0.0
    for ing, pct in formula.items():
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat:
                total += (pct / 100.0) * cat[ing].get("SE", 0.0)
                break
    return total


def compute_digestible_protein(formula: dict) -> float:
    """حساب البروتين المهضوم الإجمالي"""
    total = 0.0
    for ing, pct in formula.items():
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat:
                d = cat[ing]
                total += (pct / 100.0) * d.get("CP", 0.0) * d.get("DC", 0.0)
                break
    return total


def compute_crude_protein(formula: dict) -> float:
    """حساب البروتين الخام الإجمالي"""
    total = 0.0
    for ing, pct in formula.items():
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat:
                total += (pct / 100.0) * cat[ing].get("CP", 0.0)
                break
    return total

# ═══════════════════════════════════════════════════════════════════════════
# القسم 9: تحديد المعيار القياسي حسب الحيوان
# ═══════════════════════════════════════════════════════════════════════════

def get_standard_key(animal: str, stage: str, gender: str = "") -> str:
    """
    تحديد مفتاح المعيار القياسي حسب الحيوان والمرحلة.
    
    Parameters
    ----------
    animal : str — اسم الحيوان (أغنام، ماعز، أبقار، إبل، خيول، دواجن، سمان، أسماك)
    stage : str — مرحلة الإنتاج
    gender : str — الجنس (اختياري)
    
    Returns
    -------
    str — مفتاح في NUTRIENT_STANDARDS
    """
    a = str(animal).strip()
    s = str(stage).strip()
    g = str(gender).strip()
    
    # ─── الأبقار ───
    if "أبقار" in a or "بقر" in a:
        if "حليب عالي" in s or "إدرار عالي" in s: return "أبقار_حليب_عالي"
        if "حليب متوسط" in s: return "أبقار_حليب_متوسط"
        if "حليب" in s or "إدرار" in s: return "أبقار_حليب_متوسط"
        if "تسمين مكثف" in s: return "أبقار_تسمين_مكثف"
        if "تسمين" in s: return "أبقار_تسمين_عادي"
        if "حمل" in s or "دفع غذائي" in s: return "أبقار_حمل_أخير"
        if "صيانة" in s: return "أبقار_صيانة"
        return "أبقار_حليب_متوسط"
    
    # ─── الأغنام ───
    if "أغنام" in a or "ضأن" in a:
        if "مكثف" in s: return "أغنام_تسمين_مكثف"
        if "تسمين" in s or "تيد" in s: return "أغنام_تسمين_عادي"
        if "حليب" in s or "إدرار" in s or "مرضع" in s: return "أغنام_حليب"
        if "حامل" in s or "دفع" in s: return "أغنام_حمل_أخير"
        if "صيانة" in s or "جافة" in s: return "أغنام_صيانة"
        if "حملان" in s or "بداية" in s: return "حملان_بداية"
        return "أغنام_تسمين_عادي"
    
    # ─── الماعز ───
    if "ماعز" in a:
        if "حليب عالي" in s or "حلابة" in s: return "ماعز_حليب_عالي"
        if "حليب" in s or "إدرار" in s: return "ماعز_حليب_متوسط"
        if "تسمين" in s: return "ماعز_تسمين"
        if "حامل" in s or "دفع" in s: return "ماعز_حمل_أخير"
        if "صيانة" in s: return "ماعز_صيانة"
        if "جديان" in s or "بداية" in s: return "جديان_بداية"
        return "ماعز_تسمين"
    
    # ─── الإبل ───
    if "إبل" in a or "جمال" in a or "نوق" in a:
        if "حليب عالي" in s or "إدرار عالي" in s: return "إبل_حليب_عالي"
        if "حليب" in s or "إدرار" in s: return "إبل_حليب_متوسط"
        if "سباق" in s or "رياضة" in s or "هجن" in s: return "إبل_سباق"
        if "تسمين" in s: return "إبل_تسمين"
        if "صيانة" in s: return "إبل_صيانة"
        if "حوار" in s or "نمو" in s: return "إبل_نمو"
        return "إبل_نمو"
    
    # ─── الخيول ───
    if "خيول" in a or "خيل" in a or "أحصنة" in a:
        if "مكثف" in s or "سباق" in s: return "خيول_رياضة_مكثف"
        if "رياضة" in s or "نشاط" in s: return "خيول_رياضة_عادي"
        if "نمو" in s or "أمهار" in s: return "خيول_نمو"
        if "بداية" in s: return "أمهار_بداية"
        if "مرضع" in s or "فرس" in s: return "فرسات_مرضعات"
        if "صيانة" in s: return "خيول_صيانة"
        return "خيول_رياضة_عادي"
    
    # ─── الدواجن اللاحم ───
    if "دواجن لاحم" in a or "لاحم" in a or "broiler" in a.lower():
        if "بادي" in s or "بداية" in s: return "دواجن_بادي"
        if "نامي" in s or "نمو" in s: return "دواجن_نامي"
        if "ناهي" in s or "نهائي" in s: return "دواجن_ناهي"
        return "دواجن_ناهي"
    
    # ─── الدواجن البياض ───
    if "دواجن بياض" in a or "بياض" in a or "layer" in a.lower():
        if "بادي" in s: return "دواجن_بياض_بادي"
        if "نامي" in s: return "دواجن_بياض_نامي"
        if "ناهي" in s: return "دواجن_بياض_ناهي"
        if "إنتاج" in s or "بيض" in s: return "دواجن_بياض_إنتاج"
        if "أمهات" in s: return "دواجن_أمهات"
        return "دواجن_بياض_إنتاج"
    
    # ─── الدواجن العامة ───
    if "دواجن" in a or "دجاج" in a:
        if "بادي" in s: return "دواجن_بادي"
        if "نامي" in s: return "دواجن_نامي"
        if "ناهي" in s: return "دواجن_ناهي"
        if "بياض" in s: return "دواجن_بياض_إنتاج"
        return "دواجن_ناهي"
    
    # ─── السمان ───
    if "سمان" in a or "quail" in a.lower():
        if "بادي" in s or "بداية" in s: return "سمان_بادي"
        if "نامي" in s or "نمو" in s: return "سمان_نامي"
        if "ناهي" in s: return "سمان_ناهي"
        if "بياض" in s or "بيض" in s: return "سمان_بياض"
        return "سمان_بياض"
    
    # ─── الأسماك ───
    if "أسماك" in a or "سمك" in a or "fish" in a.lower():
        if "زريعة" in s or "بادئ" in s or "بداية" in s: return "أسماك_بادئ_زريعة"
        if "نمو" in s: return "أسماك_نمو_متوسط"
        if "تسمين" in s or "ناهي" in s: return "أسماك_تسمين"
        if "أمهات" in s: return "أسماك_أمهات"
        return "أسماك_نمو_متوسط"
    
    # ─── الأرانب ───
    if "أرانب" in a or "أرنب" in a:
        if "نمو" in s: return "أرانب_نمو"
        if "حليب" in s or "مرضع" in s: return "أرانب_حليب"
        if "صيانة" in s: return "أرانب_صيانة"
        return "أرانب_نمو"
    
    # ─── افتراضي ───
    return "دواجن_ناهي"


# ═══════════════════════════════════════════════════════════════════════════
# القسم 10: محرك التركيب التلقائي الدقيق
# يضمن الفرق ≤ 0.5% بين المحسوب والقياسي
# ═══════════════════════════════════════════════════════════════════════════

def auto_formulate_precise(
    available_ingredients: list,
    prices: dict,
    target_dp: float,
    target_se: float,
    standard_key: str,
    tolerance: float = 0.5,
    max_iterations: int = 30
) -> dict:
    """
    محرك التركيب التلقائي الدقيق.
    
    يستخدم Linear Programming مع حلقات تصحيح تلقائي
    لضمان أن الفرق بين القيمة المحسوبة والقيمة القياسية ≤ tolerance.
    
    Parameters
    ----------
    available_ingredients : list — قائمة أسماء المكونات المتاحة
    prices : dict — أسعار المكونات
    target_dp : float — البروتين المهضوم المستهدف %
    target_se : float — معادل النشاء المستهدف
    standard_key : str — مفتاح المعيار القياسي
    tolerance : float — الحد الأقصى للفرق المسموح
    max_iterations : int — عدد التكرارات الأقصى
    
    Returns
    -------
    dict — يحتوي على: success, formula, cost, actual_nutrients, dp_error, se_error, iterations
    """
    
    if not available_ingredients:
        return {"success": False, "message": "لا توجد مكونات متاحة"}
    
    standard = NUTRIENT_STANDARDS.get(standard_key, {})
    if not standard:
        return {"success": False, "message": f"لا يوجد معيار لـ ({standard_key})"}
    
    # جمع بيانات المكونات
    ing_data = {}
    for ing in available_ingredients:
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat:
                ing_data[ing] = cat[ing]
                break
    
    valid_ings = [i for i in available_ingredients if i in ing_data]
    if not valid_ings:
        return {"success": False, "message": "المكونات غير معروفة في المكتبة"}
    
    n = len(valid_ings)
    c = [prices.get(i, 300.0) for i in valid_ings]
    
    # ─── الحدود ───
    bounds = []
    for i in valid_ings:
        # قيود خاصة لبعض المكونات
        if "يوريا" in i:
            bounds.append((0.0, 1.5))
        elif "مولاس" in i:
            bounds.append((0.0, 12.0))
        elif "ملح الطعام" in i:
            bounds.append((0.3, 0.8))
        elif "بيكربونات" in i:
            bounds.append((0.0, 2.0))
        elif "مضاد سموم" in i:
            bounds.append((0.05, 0.3))
        elif "بريمكس" in i:
            bounds.append((0.2, 0.5))
        elif "إنزيم" in i:
            bounds.append((0.02, 0.10))
        elif "الحجر الجيري" in i:
            bounds.append((0.5, 3.0))
        elif "فوسفات" in i:
            bounds.append((0.3, 2.0))
        else:
            bounds.append((0.0, 100.0))
    
    # ─── صفوف المكونات ───
    cp_row = [ing_data[i].get("CP", 0) * ing_data[i].get("DC", 0) for i in valid_ings]
    se_row = [ing_data[i].get("SE", 0) for i in valid_ings]
    ndf_row = [ing_data[i].get("NDF", 0) for i in valid_ings]
    adf_row = [ing_data[i].get("ADF", 0) for i in valid_ings]
    ca_row = [ing_data[i].get("Ca", 0) for i in valid_ings]
    p_row = [ing_data[i].get("P", 0) for i in valid_ings]
    
    # ─── قيود المساواة ───
    A_eq = [[1.0] * n]  # مجموع النسب = 100
    b_eq = [100.0]
    
    # ─── قيود عدم المساواة الأولية ───
    A_ub, b_ub = [], []
    
    # SE ≥ target
    A_ub.append([-1.0 * x for x in se_row])
    b_ub.append(-1.0 * target_se * 100.0)
    
    # NDF ≤ standard (اختياري)
    if "NDF" in standard and standard["NDF"] > 0:
        A_ub.append([1.0 * x for x in ndf_row])
        b_ub.append(standard["NDF"] * 1.1 * 100.0)
    
    # ADF ≤ standard (اختياري)
    if "ADF" in standard and standard["ADF"] > 0:
        A_ub.append([1.0 * x for x in adf_row])
        b_ub.append(standard["ADF"] * 1.15 * 100.0)
    
    # ─── محاولات التصحيح ───
    best_result = None
    best_error = float('inf')
    cur_dp = target_dp
    cur_se = target_se
    log = []
    
    for iteration in range(max_iterations):
        # تحديث قيد البروتين المهضوم
        A_eq_cur = [list(row) for row in A_eq]
        b_eq_cur = list(b_eq)
        A_eq_cur.append(cp_row)
        b_eq_cur.append(cur_dp * 100.0)
        
        res = linprog(
            c,
            A_ub=A_ub if A_ub else None,
            b_ub=b_ub if b_ub else None,
            A_eq=A_eq_cur,
            b_eq=b_eq_cur,
            bounds=bounds,
            method='highs',
            options={'presolve': True, 'time_limit': 30}
        )
        
        if not res.success:
            # تخفيف القيود
            b_ub = [b * 0.99 if b < 0 else b * 1.01 for b in b_ub]
            log.append(f"محاولة {iteration+1}: فشل — تخفيف القيود")
            continue
        
        formula = {valid_ings[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
        actual = compute_formula_nutrients(formula)
        
        dp_err = abs(actual["DP"] - target_dp)
        se_err = abs(actual["SE"] - target_se) if target_se > 0 else 0
        ndf_err = abs(actual["NDF"] - standard.get("NDF", actual["NDF"]))
        
        total_err = dp_err * 10 + se_err / 10.0 + ndf_err / 100.0
        
        log.append(f"محاولة {iteration+1}: DP={actual['DP']:.2f} (خطأ {dp_err:.3f}) | "
                   f"SE={actual['SE']:.2f} (خطأ {se_err:.3f})")
        
        if total_err < best_error:
            best_error = total_err
            best_result = {
                "success": True,
                "formula": formula,
                "cost": res.fun / 100.0,
                "actual_nutrients": actual,
                "dp_error": dp_err,
                "se_error": se_err,
                "iterations": iteration + 1,
                "log": log[-5:],
            }
        
        # التحقق من الدقة
        if dp_err <= tolerance and se_err <= tolerance * 5:
            log.append(f"✅ تم تحقيق الدقة المطلوبة في المحاولة {iteration+1}")
            break
        
        # تعديل الأهداف
        cur_dp += (target_dp - actual["DP"]) * 0.2
        cur_se += (target_se - actual["SE"]) * 0.15
        
        # الحدود
        cur_dp = max(5.0, min(40.0, cur_dp))
        cur_se = max(10.0, min(90.0, cur_se))
    
    if best_result:
        best_result["log"] = log
        return best_result
    
    return {"success": False, "message": "تعذر إيجاد حل دقيق — جرّب مكونات إضافية", "log": log}


def auto_formulate_with_constraints(
    available_ingredients: list,
    prices: dict,
    standard_key: str,
    tolerance: float = 0.5,
    custom_constraints: dict = None
) -> dict:
    """
    نسخة موسعة من محرك التركيب تدعم قيوداً مخصصة.
    """
    standard = NUTRIENT_STANDARDS.get(standard_key, {})
    if not standard:
        return {"success": False, "message": "لا يوجد معيار"}
    
    target_dp = standard.get("DP", 12.0)
    target_se = standard.get("SE", 65.0)
    
    result = auto_formulate_precise(
        available_ingredients, prices,
        target_dp, target_se, standard_key,
        tolerance, 30
    )
    return result
    # ═══════════════════════════════════════════════════════════════════════════
# القسم 11: نظام قاعدة البيانات SQLite
# ═══════════════════════════════════════════════════════════════════════════

class DatabaseManager:
    """مدير قاعدة البيانات المحلية"""
    
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            created_date TEXT
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas (
            formula_id TEXT PRIMARY KEY,
            formula_name TEXT,
            animal_type TEXT,
            breed TEXT,
            target_dp REAL,
            target_se REAL,
            ingredients TEXT,
            total_cost REAL,
            actual_nutrients TEXT,
            requester_name TEXT,
            created_by TEXT,
            created_date TEXT
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS milk_replacers (
            id TEXT PRIMARY KEY,
            animal_type TEXT,
            formula TEXT,
            cost_per_kg REAL,
            requester TEXT,
            created_date TEXT
        )''')
        
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
        
        c.execute('''CREATE TABLE IF NOT EXISTS invoices (
            invoice_id TEXT PRIMARY KEY,
            customer_name TEXT,
            formula_id TEXT,
            quantity_ton REAL,
            unit_price REAL,
            total_price REAL,
            status TEXT,
            created_by TEXT,
            created_date TEXT
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS lab_analyses (
            analysis_id TEXT PRIMARY KEY,
            animal_type TEXT,
            stage TEXT,
            ingredients TEXT,
            nutrients TEXT,
            requester TEXT,
            source TEXT,
            created_date TEXT
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS broiler_farms (
            farm_id TEXT PRIMARY KEY,
            farm_name TEXT UNIQUE,
            owner TEXT,
            owner_phone TEXT,
            data TEXT,
            created_date TEXT
        )''')
        
        conn.commit()
        conn.close()
    
    def execute(self, query: str, params: tuple = ()):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        result = c.execute(query, params)
        conn.commit()
        data = result.fetchall()
        conn.close()
        return data
    
    def insert(self, table: str, data: dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        cols = ', '.join(data.keys())
        ph = ', '.join(['?'] * len(data))
        try:
            c.execute(f"INSERT INTO {table} ({cols}) VALUES ({ph})", list(data.values()))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        conn.close()
    
    def update(self, table: str, data: dict, where: str, params: tuple):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        sets = ', '.join(f"{k}=?" for k in data.keys())
        c.execute(f"UPDATE {table} SET {sets} WHERE {where}",
                  list(data.values()) + list(params))
        conn.commit()
        conn.close()
    
    def delete(self, table: str, where: str, params: tuple):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"DELETE FROM {table} WHERE {where}", params)
        conn.commit()
        conn.close()


db = DatabaseManager()

# ═══════════════════════════════════════════════════════════════════════════
# القسم 12: نظام المصادقة
# ═══════════════════════════════════════════════════════════════════════════

class AuthManager:
    def __init__(self):
        self.db = db
        users = self.db.execute("SELECT * FROM users WHERE username='admin'")
        if not users:
            self.create_user(
                'admin', 'admin123', 'owner',
                SUPERVISOR, OWNER_EMAIL, WHATSAPP_NUMBER
            )
    
    def create_user(self, username, password, role, full_name, email, phone):
        uid = secrets.token_hex(16)
        ph = hashlib.sha256(password.encode()).hexdigest()
        self.db.insert('users', {
            'user_id': uid,
            'username': username,
            'password_hash': ph,
            'role': role,
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'created_date': datetime.now().isoformat()
        })
        return uid
    
    def authenticate(self, username, password):
        users = self.db.execute("SELECT * FROM users WHERE username=?", (username,))
        if users:
            u = users[0]
            if u[2] == hashlib.sha256(password.encode()).hexdigest():
                return {
                    'user_id': u[0], 'username': u[1], 'role': u[3],
                    'full_name': u[4], 'email': u[5], 'phone': u[6]
                }
        return None
    
    def get_all_users(self):
        return self.db.execute("SELECT * FROM users")


auth_manager = AuthManager()


# ═══════════════════════════════════════════════════════════════════════════
# القسم 13: النظام المرجعي العلمي
# ═══════════════════════════════════════════════════════════════════════════

class ScientificReferenceSystem:
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان",
            "references": [
                {"id": "REF001", "authors": "McDonald, P., Edwards, R.A., Greenhalgh, J.F.D.",
                 "year": 2011, "title": "Animal Nutrition", "publisher": "Pearson",
                 "edition": "7th Edition", "isbn": "978-1408204238",
                 "summary": "المرجع الأساسي في تغذية الحيوان."},
                {"id": "REF002", "authors": "Cheeke, P.R., Dierenfeld, E.S.",
                 "year": 2010, "title": "Comparative Animal Nutrition",
                 "publisher": "CABI", "isbn": "978-1845936310",
                 "summary": "مقارنة بين آليات التغذية في مختلف الحيوانات."},
            ]
        },
        "protein_amino_acids": {
            "title": "البروتين والأحماض الأمينية",
            "references": [
                {"id": "REF003", "authors": "NRC", "year": 2012,
                 "title": "Nutrient Requirements of Swine",
                 "publisher": "National Academies Press",
                 "summary": "متطلبات العناصر الغذائية للخنازير."},
                {"id": "REF004", "authors": "NRC", "year": 2001,
                 "title": "Nutrient Requirements of Dairy Cattle",
                 "publisher": "National Academies Press",
                 "summary": "تغذية أبقار الحليب."},
            ]
        },
        "camel_nutrition": {
            "title": "تغذية الإبل",
            "references": [
                {"id": "REF100", "authors": "FAO", "year": 2010,
                 "title": "Camel Nutrition and Feeding",
                 "publisher": "FAO Publications",
                 "summary": "الدليل الشامل لتغذية الإبل."},
                {"id": "REF101", "authors": "Kadim et al.", "year": 2014,
                 "title": "Camel Meat and Meat Products",
                 "publisher": "CABI",
                 "summary": "إنتاج لحم الإبل."},
            ]
        },
        "poultry": {
            "title": "تغذية الدواجن",
            "references": [
                {"id": "REF010", "authors": "Leeson, S., Summers, J.D.",
                 "year": 2009, "title": "Commercial Poultry Nutrition",
                 "publisher": "Nottingham University Press",
                 "summary": "تغذية الدواجن التجارية."},
                {"id": "REF020", "authors": "Aviagen", "year": 2020,
                 "title": "Ross 308 Broiler Management",
                 "publisher": "Aviagen",
                 "summary": "دليل روس 308."},
            ]
        },
        "ruminants": {
            "title": "تغذية المجترات",
            "references": [
                {"id": "REF006", "authors": "Van Soest, P.J.", "year": 1994,
                 "title": "Nutritional Ecology of the Ruminant",
                 "publisher": "Cornell University Press",
                 "summary": "المرجع الكلاسيكي للمجترات."},
                {"id": "REF023", "authors": "INRA", "year": 2007,
                 "title": "INRA Feeding System for Ruminants",
                 "publisher": "Wageningen Academic",
                 "summary": "النظام الفرنسي لتغذية المجترات."},
            ]
        },
        "milk_replacers": {
            "title": "بدائل الحليب",
            "references": [
                {"id": "REF200", "authors": "Davis, C.L., Drackley, J.K.",
                 "year": 1998, "title": "The Development, Nutrition, and Management of the Young Calf",
                 "publisher": "Iowa State University Press",
                 "summary": "المرجع الشامل لبدائل حليب العجول."},
                {"id": "REF201", "authors": "NRC", "year": 2007,
                 "title": "Nutrient Requirements of Small Ruminants",
                 "publisher": "National Academies Press",
                 "summary": "لمتطلبات الحملان والجديان."},
            ]
        },
    }
    
    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": {
            "answer": "البروتين المهضوم (Digestible Protein) هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً. يحسب بضرب نسبة البروتين الخام في معامل الهضم.",
            "reference": "REF023",
            "simplified": "الجزء من البروتين الذي يستفيد منه الحيوان فعلياً."
        },
        "ما هو معادل النشاء": {
            "answer": "معادل النشاء (SE) مقياس لكمية الطاقة التي يوفرها العلف مقارنة بالنشاء النقي.",
            "reference": "REF006",
            "simplified": "كلما زاد الرقم، زادت الطاقة."
        },
        "لماذا الإبل مختلفة": {
            "answer": "الإبل لها احتياجات غذائية مختلفة عن الأبقار والأغنام. تحتاج بروتيناً أقل نسبياً وأليافاً أكثر بسبب طبيعة كرشها الفريد الذي يتحمل العطش.",
            "reference": "REF100",
            "simplified": "الإبل تحتاج بروتين أقل وألياف أكثر."
        },
        "ما هو مؤشر EPEF": {
            "answer": "EPEF = (الحيوية × الوزن الحي) / (العمر × معامل التحويل) × 100. كلما ارتفع، كان أداء المزرعة أفضل.",
            "reference": "REF020",
            "simplified": "رقم يعبر عن كفاءة المزرعة."
        },
        "متى أستخدم بديل الحليب": {
            "answer": "بديل الحليب يستخدم عندما: (1) الأم لا تكفي لإرضاع المولود، (2) الأم مريضة أو نافقة، (3) توأم يحتاج رضاعة إضافية، (4) برنامج تربية صناعي مكثف.",
            "reference": "REF200",
            "simplified": "عند نقص حليب الأم أو الحاجة لبرنامج مكثف."
        },
    }
    
    @staticmethod
    def get_reference(ref_id: str) -> Optional[dict]:
        for cat in ScientificReferenceSystem.REFERENCES.values():
            for ref in cat.get("references", []):
                if ref.get("id") == ref_id:
                    return ref
        return None
    
    @staticmethod
    def get_knowledge_answer(question: str) -> Optional[dict]:
        q_norm = arabic_processor.normalize(question)
        for key, value in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            if arabic_processor.normalize(key) in q_norm or any(
                word in q_norm for word in arabic_processor.normalize(key).split()
            ):
                ref = ScientificReferenceSystem.get_reference(value.get("reference", ""))
                return {
                    "answer": value["answer"],
                    "simplified": value.get("simplified", value["answer"]),
                    "reference": ref
                }
        return None


# ═══════════════════════════════════════════════════════════════════════════
# القسم 14: بدائل الحليب — Milk Replacers
# ═══════════════════════════════════════════════════════════════════════════

MILK_REPLACER_STANDARDS = {
    "عجول (Calves)": {
        "CP": 24.0, "Fat": 24.0, "Lactose": 45.0, "Lysine": 2.1,
        "Ca": 0.75, "P": 0.70, "Fiber_max": 0.15, "Ash_max": 10.0,
        "notes": "عمر 1-6 أسابيع، مادة جافة 12-15%، يقدم دافئاً 38-40°C"
    },
    "حملان (Lambs)": {
        "CP": 24.0, "Fat": 24.0, "Lactose": 40.0, "Lysine": 2.1,
        "Ca": 0.80, "P": 0.70, "Fiber_max": 0.15, "Ash_max": 10.0,
        "notes": "≥ 24% دهن، يبدأ من اليوم الثاني"
    },
    "جديان (Goat Kids)": {
        "CP": 24.0, "Fat": 24.0, "Lactose": 42.0, "Lysine": 2.1,
        "Ca": 0.80, "P": 0.70, "Fiber_max": 0.15, "Ash_max": 10.0,
        "notes": "مشابه لحملان مع اختلاف بسيط في اللاكتوز"
    },
    "إبل (Camel Calves)": {
        "CP": 26.0, "Fat": 28.0, "Lactose": 38.0, "Lysine": 2.3,
        "Ca": 0.85, "P": 0.75, "Fiber_max": 0.10, "Ash_max": 9.0,
        "notes": "بروتين ودهن أعلى من البقر — الحوار أضعف من العجل"
    },
    "أمهار (Foals)": {
        "CP": 22.0, "Fat": 20.0, "Lactose": 45.0, "Lysine": 1.9,
        "Ca": 0.90, "P": 0.80, "Fiber_max": 0.15, "Ash_max": 9.0,
        "notes": "توازن خاص للخيول النامية"
    },
    "صغار الأرانب (Kits)": {
        "CP": 30.0, "Fat": 30.0, "Lactose": 25.0, "Lysine": 2.4,
        "Ca": 1.00, "P": 0.80, "Fiber_max": 0.05, "Ash_max": 8.0,
        "notes": "تركيز عالي جداً — حليب الأرانب دهني جداً"
    },
}

MILK_REPLACER_INGREDIENTS = {
    "حليب مجفف منزوع الدسم": {"CP": 34.0, "Fat": 1.0, "Lactose": 52.0, "Ash": 8.0, "price": 3200, "desc": "مصدر بروتين أساسي"},
    "حليب مجفف كامل الدسم": {"CP": 26.0, "Fat": 28.0, "Lactose": 38.0, "Ash": 6.0, "price": 3800, "desc": "بروتين ودهن متوازن"},
    "شرش حليب مجفف": {"CP": 12.0, "Fat": 1.5, "Lactose": 75.0, "Ash": 9.0, "price": 1800, "desc": "مصدر لاكتوز"},
    "بروتين شرش WPC 80%": {"CP": 80.0, "Fat": 5.0, "Lactose": 8.0, "Ash": 4.0, "price": 8500, "desc": "بروتين عالي الجودة"},
    "كازين (Casein)": {"CP": 85.0, "Fat": 2.0, "Lactose": 2.0, "Ash": 3.0, "price": 9000, "desc": "بروتين الحليب النقي"},
    "مركز بروتين صويا SPC 66%": {"CP": 66.0, "Fat": 1.0, "Lactose": 0.0, "Ash": 6.0, "price": 2800, "desc": "بديل اقتصادي للبروتين"},
    "مركز بروتين صويا SPC 55%": {"CP": 55.0, "Fat": 2.0, "Lactose": 0.0, "Ash": 7.0, "price": 2200, "desc": "بروتين نباتي متوسط"},
    "دقيق الصويا كامل الدسم": {"CP": 38.0, "Fat": 20.0, "Lactose": 0.0, "Ash": 6.0, "price": 1500, "desc": "بروتين + دهن"},
    "زيت جوز الهند": {"CP": 0.0, "Fat": 100.0, "Lactose": 0.0, "Ash": 0.0, "price": 2200, "desc": "دهن سهل الهضم"},
    "زيت النخيل": {"CP": 0.0, "Fat": 100.0, "Lactose": 0.0, "Ash": 0.0, "price": 1200, "desc": "دهن اقتصادي"},
    "دهن حيواني (Tallow)": {"CP": 0.0, "Fat": 100.0, "Lactose": 0.0, "Ash": 0.0, "price": 1000, "desc": "مصدر دهن"},
    "زيت الذرة": {"CP": 0.0, "Fat": 100.0, "Lactose": 0.0, "Ash": 0.0, "price": 1800, "desc": "دهن فاخر"},
    "مالتودكسترين": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "Ash": 0.5, "price": 900, "desc": "كربوهيدرات مكملة"},
    "لاكتوز نقي": {"CP": 0.0, "Fat": 0.0, "Lactose": 100.0, "Ash": 0.0, "price": 1400, "desc": "سكر الحليب"},
    "ليسين L-Lysine": {"CP": 94.0, "Fat": 0.0, "Lactose": 0.0, "Ash": 0.5, "price": 4200, "desc": "حمض أميني أساسي"},
    "ميثيونين DL-Methionine": {"CP": 58.0, "Fat": 0.0, "Lactose": 0.0, "Ash": 0.3, "price": 5800, "desc": "حمض كبريتي"},
    "بريمكس فيتامينات حليب": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "Ash": 100.0, "price": 6500, "desc": "فيتامينات ومعادن"},
    "كالسيوم كربونات": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "Ash": 99.5, "price": 200, "desc": "مصدر كالسيوم"},
    "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "Ash": 98.5, "price": 1100, "desc": "Ca + P"},
    "ملح طعام": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "Ash": 99.9, "price": 150, "desc": "كلوريد الصوديوم"},
    "مضاد حيوي وقائي": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "Ash": 100.0, "price": 8500, "desc": "للإسهال"},
    "بروبيوتيك (خمائر)": {"CP": 15.0, "Fat": 0.0, "Lactose": 0.0, "Ash": 20.0, "price": 5000, "desc": "لبكتيريا الأمعاء"},
}


def formulate_milk_replacer(
    animal_type: str,
    target_volume_kg: float = 100.0,
    selected_ingredients: list = None
) -> dict:
    """تركيب بديل حليب متوازن"""
    standard = MILK_REPLACER_STANDARDS.get(animal_type)
    if not standard:
        return {"success": False, "message": "نوع الحيوان غير مدعوم"}
    
    ingredients = selected_ingredients or list(MILK_REPLACER_INGREDIENTS.keys())
    valid = [i for i in ingredients if i in MILK_REPLACER_INGREDIENTS]
    if len(valid) < 3:
        return {"success": False, "message": "اختر 3 مكونات على الأقل"}
    
    n = len(valid)
    c = [MILK_REPLACER_INGREDIENTS[i]["price"] for i in valid]
    bounds = [(0.0, 100.0) for _ in range(n)]
    
    A_eq = [[1.0] * n]
    b_eq = [100.0]
    
    cp_row = [MILK_REPLACER_INGREDIENTS[i]["CP"] for i in valid]
    fat_row = [MILK_REPLACER_INGREDIENTS[i]["Fat"] for i in valid]
    
    A_eq.append(cp_row)
    b_eq.append(standard["CP"] * 100)
    A_eq.append(fat_row)
    b_eq.append(standard["Fat"] * 100)
    
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if not res.success:
        return {"success": False, "message": "تعذر التركيب"}
    
    formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
    
    # حساب القيم الفعلية
    actual = {"CP": 0, "Fat": 0, "Lactose": 0}
    for ing, pct in formula.items():
        d = MILK_REPLACER_INGREDIENTS[ing]
        actual["CP"] += pct / 100.0 * d["CP"]
        actual["Fat"] += pct / 100.0 * d["Fat"]
        actual["Lactose"] += pct / 100.0 * d["Lactose"]
    
    return {
        "success": True,
        "formula": formula,
        "cost_per_100kg": res.fun / 100.0,
        "cost_per_kg": res.fun / 10000.0,
        "standard": standard,
        "actual": actual,
        "animal": animal_type,
        "target_volume_kg": target_volume_kg,
    }


# ═══════════════════════════════════════════════════════════════════════════
# القسم 15: المختبر الذكي — OCR
# ═══════════════════════════════════════════════════════════════════════════

def match_ingredient_name(text: str) -> Optional[str]:
    """مطابقة اسم المادة المستخرج مع المكتبة"""
    if not text:
        return None
    tl = text.strip().lower()
    
    # مطابقة مباشرة
    for cat in BIG_FEEDS_LIBRARY.values():
        for name in cat.keys():
            if name.lower() in tl or tl in name.lower():
                return name
    
    # مطابقة كلمات مفتاحية
    keywords_map = {
        "ذرة": "ذرة صفراء", "corn": "ذرة صفراء",
        "صويا": "كسب فول صويا 44%", "soy": "كسب فول صويا 44%",
        "شعير": "شعير مطحون", "barley": "شعير مطحون",
        "قمح": "قمح محلي مصنّع", "wheat": "قمح محلي مصنّع",
        "سورجم": "سورجم (فتريتة)", "sorghum": "سورجم (فتريتة)",
        "نخالة": "نخالة قمح (ردة)", "bran": "نخالة قمح (ردة)",
        "فول سوداني": "أمباز الفول السوداني (كسب)",
        "قطن": "كسب بذور القطن (مقشور)",
        "عباد": "كسب عباد الشمس 36%",
        "سمسم": "كسب السمسم المحسن",
        "جلوتين": "كسب جلوتين الذرة 60%",
        "سمك": "مسحوق أسماك (Fishmeal 60%)", "fish": "مسحوق أسماك (Fishmeal 60%)",
        "لحم": "مسحوق اللحم والعظم",
        "دم": "مسحوق الدم المجفف",
        "ليسين": "ليسين نقي (L-Lysine HCl)",
        "ميثيونين": "ميثيونين نقي (DL-Methionine)",
        "ملح": "ملح الطعام", "salt": "ملح الطعام",
        "حجر": "الحجر الجيري (بودرة بلاط)",
        "جير": "الحجر الجيري (بودرة بلاط)",
        "فوسفات": "فوسفات ثنائي الكالسيوم (DCP)",
        "بيكربونات": "بيكربونات الصوديوم (الصودا)",
        "صودا": "بيكربونات الصوديوم (الصودا)",
        "مولاس": "مولاس قصب السكر",
        "برسيم": "البرسيم الجاف (الدريس)",
        "دريس": "البرسيم الجاف (الدريس)",
        "تبن": "تبن قمح ناعم",
        "يوريا": "يوريا علفية محصنة",
        "بريمكس": "بريمكس تسمين دواجن (Premix Broiler)",
    }
    for kw, matched in keywords_map.items():
        if kw in tl:
            return matched
    return None


def extract_ingredients_from_image(image_bytes: bytes) -> dict:
    """تحليل صورة تحتوي على نسب المكونات بالـ OCR"""
    if not OCR_AVAILABLE:
        return {"success": False, "message": "مكتبة pytesseract غير مثبتة"}
    
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {"success": False, "message": "تعذر قراءة الصورة"}
        
        # تحسين الصورة
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)
        
        # محاولة أولى: adaptive threshold
        thresh1 = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # محاولة ثانية: otsu
        _, thresh2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        results = []
        for thresh in [thresh1, thresh2, gray]:
            try:
                text = pytesseract.image_to_string(
                    thresh, lang='ara+eng',
                    config=r'--oem 3 --psm 6'
                )
                if text.strip():
                    results.append(text)
            except Exception:
                continue
        
        if not results:
            return {"success": False, "message": "لم يتم استخراج نص"}
        
        full_text = "\n".join(results)
        
        # استخراج أزواج (اسم، نسبة)
        ingredients = {}
        lines = full_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # البحث عن رقم يليه %
            patterns = [
                r'([\u0600-\u06FFa-zA-Z\s\(\)%]+?)[\s:\-=]+(\d+\.?\d*)\s*%',
                r'([\u0600-\u06FFa-zA-Z\s\(\)%]+?)\s+(\d+\.?\d*)\s*%',
                r'([\u0600-\u06FFa-zA-Z\s]+?)\s*[:\-]\s*(\d+\.?\d*)',
            ]
            
            matched = False
            for pattern in patterns:
                m = re.search(pattern, line)
                if m:
                    name = m.group(1).strip()
                    val = float(m.group(2))
                    if 0.1 < val <= 100 and len(name) > 2:
                        matched_name = match_ingredient_name(name)
                        if matched_name:
                            ingredients[matched_name] = val
                            matched = True
                            break
                    elif not matched and 0.1 < val <= 100:
                        # حتى بدون مطابقة تامة، سجل النص
                        pass
            
            # إذا كان السطر مجرد رقم
            if not matched:
                m = re.search(r'^(\d+\.?\d*)\s*%?$', line)
                if m:
                    val = float(m.group(1))
                    if 0.1 < val <= 100:
                        # سجل كقيمة مجهولة
                        pass
        
        return {
            "success": True,
            "ingredients": ingredients,
            "raw_text": full_text,
            "count": len(ingredients),
            "source": "image_ocr"
        }
    
    except Exception as e:
        return {"success": False, "message": f"خطأ: {str(e)}"}


# ═══════════════════════════════════════════════════════════════════════════
# القسم 16: مولد PDF الاحترافي الفائق
# ═══════════════════════════════════════════════════════════════════════════

class ProfessionalPDFGenerator:
    """مولد تقارير PDF احترافي مع ختم وترويسة وتذييل بالدعاء"""
    
    def __init__(self):
        self.font_name = 'Helvetica'
        self.font_bold = 'Helvetica-Bold'
        
        # البحث عن خط عربي
        font_paths = [
            "Amiri-Regular.ttf", "Amiri.ttf",
            "Cairo-Regular.ttf", "Tajawal-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        ]
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    pdfmetrics.registerFont(TTFont('TaworArabic', fp))
                    self.font_name = 'TaworArabic'
                    self.font_bold = 'TaworArabic'
                    break
                except Exception:
                    continue
        
        # شعار
        self.logo_path = None
        for lp in LOGO_OPTIONS + PHOTO_OPTIONS:
            if os.path.exists(lp):
                self.logo_path = lp
                break
    
    def _ar(self, text: str) -> str:
        try:
            return get_display(arabic_reshaper.reshape(str(text)))
        except Exception:
            return str(text)
    
    def _draw_page_decorations(self, canvas_obj, doc):
        """رسم الترويسة والختم والتذييل على كل صفحة"""
        canvas_obj.saveState()
        w, h = doc.pagesize
        
        # ─── علامة مائية ───
        canvas_obj.setFillColor(HexColor('#e8f5e9'))
        canvas_obj.setFont(self.font_name, 60)
        try:
            canvas_obj.setFillAlpha(0.07)
        except Exception:
            pass
        canvas_obj.saveState()
        canvas_obj.translate(w / 2, h / 2)
        canvas_obj.rotate(45)
        canvas_obj.drawCentredString(0, 0, self._ar("تاور نولجي"))
        canvas_obj.restoreState()
        try:
            canvas_obj.setFillAlpha(1)
        except Exception:
            pass
        
        # ─── ترويسة علوية ───
        canvas_obj.setFillColor(HexColor('#1b5e20'))
        canvas_obj.rect(0, h - 90, w, 90, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor('#d4af37'))
        canvas_obj.rect(0, h - 95, w, 5, fill=1, stroke=0)
        
        # شعار
        try:
            if self.logo_path:
                canvas_obj.drawImage(
                    self.logo_path, 30, h - 78, width=60, height=60,
                    preserveAspectRatio=True, anchor='sw', mask='auto'
                )
        except Exception:
            pass
        
        # النصوص
        canvas_obj.setFillColor(white)
        canvas_obj.setFont(self.font_name, 22)
        canvas_obj.drawCentredString(w / 2, h - 38,
                                      self._ar("تاور نولجي  Tawor Nology"))
        
        canvas_obj.setFont(self.font_name, 12)
        canvas_obj.setFillColor(HexColor('#e8f5e9'))
        canvas_obj.drawCentredString(w / 2, h - 58,
                                      self._ar("للإنتاج الحيواني وتغذية الحيوان"))
        
        canvas_obj.setFont(self.font_name, 10)
        canvas_obj.setFillColor(HexColor('#d4af37'))
        canvas_obj.drawCentredString(w / 2, h - 76,
                                      self._ar(f"إشراف: {SUPERVISOR} — {SUPERVISOR_TITLE}"))
        
        # ─── تذييل سفلي بـ 3 صفوف ───
        # صف الدعاء
        canvas_obj.setFillColor(HexColor('#1b5e20'))
        canvas_obj.rect(0, 42, w, 42, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor('#d4af37'))
        canvas_obj.rect(0, 84, w, 3, fill=1, stroke=0)
        
        canvas_obj.setFillColor(HexColor('#ffeb3b'))
        canvas_obj.setFont(self.font_name, 8.5)
        canvas_obj.drawCentredString(w / 2, 68,
                                      self._ar("🤲 اللهم اغفر لإسماعيل تاور وابتسام وارحمهما 🤲"))
        
        canvas_obj.setFillColor(HexColor('#c8e6c9'))
        canvas_obj.setFont(self.font_name, 7.5)
        canvas_obj.drawCentredString(w / 2, 52,
                                      self._ar("اللهم اجعل قبرهما روضة من رياض الجنة"))
        
        # صف الحقوق
        canvas_obj.setFillColor(HexColor('#1b5e20'))
        canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)
        
        canvas_obj.setFillColor(white)
        canvas_obj.setFont(self.font_name, 8)
        canvas_obj.drawCentredString(w / 2, 27,
                                      self._ar("تاور نولجي Tawor Nology © 2026"))
        
        canvas_obj.setFont(self.font_name, 7)
        canvas_obj.drawCentredString(w / 2, 12,
                                      self._ar(f"صفحة {canvas_obj.getPageNumber()} | جميع الحقوق محفوظة"))
        
        # QR Code
        try:
            qr = qrcode.QRCode(version=1, box_size=3, border=1)
            qr.add_data(PLATFORM_URL)
            qr.make(fit=True)
            qi = qr.make_image(fill_color="#1b5e20", back_color="white")
            buf = io.BytesIO()
            qi.save(buf, format="PNG")
            buf.seek(0)
            canvas_obj.drawImage(Image(buf), w / 2 - 20, 46, width=40, height=40)
        except Exception:
            pass
        
        # ─── الختم الرسمي ───
        sx, sy = w - 105, 145
        canvas_obj.setStrokeColor(HexColor('#c62828'))
        
        # 3 دوائر متداخلة
        canvas_obj.setLineWidth(3.0)
        canvas_obj.circle(sx, sy, 70, stroke=1, fill=0)
        canvas_obj.setLineWidth(1.5)
        canvas_obj.circle(sx, sy, 62, stroke=1, fill=0)
        canvas_obj.setLineWidth(0.6)
        canvas_obj.circle(sx, sy, 56, stroke=1, fill=0)
        
        # نصوص الختم
        canvas_obj.setFillColor(HexColor('#c62828'))
        canvas_obj.setFont(self.font_name, 9)
        canvas_obj.drawCentredString(sx, sy + 40, self._ar("تاور نولجي"))
        canvas_obj.drawCentredString(sx, sy + 28, self._ar("Tawor Nology"))
        
        canvas_obj.setFont(self.font_name, 7.5)
        canvas_obj.drawCentredString(sx, sy + 10, self._ar("م. عبدالقادر"))
        canvas_obj.drawCentredString(sx, sy - 1, self._ar("إسماعيل تاور"))
        
        canvas_obj.setFont(self.font_name, 6)
        canvas_obj.drawCentredString(sx, sy - 17, self._ar("اختصاصي تغذية الحيوان"))
        canvas_obj.drawCentredString(sx, sy - 30, self._ar("معتمد رسمياً"))
        canvas_obj.drawCentredString(sx, sy - 42, self._ar("© 2026"))
        
        canvas_obj.restoreState()
    
    def _comparison_table(self, standard: dict, calculated: dict):
        """جدول مقارنة القيم القياسية vs المحسوبة"""
        labels = {
            "CP": "بروتين خام CP", "DP": "بروتين مهضوم DP",
            "SE": "معادل النشاء SE", "NDF": "ألياف NDF",
            "ADF": "ألياف ADF", "EE": "دهن EE", "ASH": "رماد ASH",
            "Ca": "كالسيوم Ca", "P": "فسفور P"
        }
        
        header = [self._ar(x) for x in
                  ["العنصر الغذائي", "المعيار القياسي", "القيمة المحسوبة", "الفرق", "التقييم"]]
        data = [header]
        
        cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR',  (0, 0), (-1, 0), white),
            ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME',   (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE',   (0, 0), (-1, -1), 10),
            ('GRID',       (0, 0), (-1, -1), 1, HexColor('#9e9e9e')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ]
        
        row = 1
        for key in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
            if key not in standard:
                continue
            sv = standard[key]
            cv = calculated.get(key, 0.0)
            diff = cv - sv
            pct = (diff / sv * 100) if sv else 0
            
            if abs(pct) <= 5:
                status, bg = "✅ مطابق", HexColor('#e8f5e9')
            elif abs(pct) <= 15:
                status, bg = "⚠️ مقبول", HexColor('#fff8e1')
            else:
                status, bg = "❌ غير مطابق", HexColor('#ffebee')
            
            unit = "%" if key in ("CP", "DP", "NDF", "ADF", "EE", "ASH", "Ca", "P") else "وحدة"
            
            data.append([
                self._ar(labels.get(key, key)),
                f"{sv:.2f} {unit}",
                f"{cv:.2f} {unit}",
                f"{diff:+.2f} ({pct:+.1f}%)",
                self._ar(status),
            ])
            cmds.append(('BACKGROUND', (0, row), (-1, row), bg))
            row += 1
        
        t = Table(data, colWidths=[110, 100, 100, 100, 90])
        t.setStyle(TableStyle(cmds))
        return t
    
    def generate_comprehensive_report(
        self,
        formula: dict,
        target_dp: float,
        breed: str,
        cost: float,
        city: str,
        local_cost: float,
        local_sym: str,
        computed_se: float,
        requester_name: str = "",
        animal_type: str = "",
        production_stage: str = "",
        include_charts: bool = True,
        report_type: str = "تركيب علفة"
    ) -> bytes:
        """توليد تقرير PDF شامل"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=45, leftMargin=45,
            topMargin=115, bottomMargin=145
        )
        story = []
        
        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(
                self._ar(text),
                ParagraphStyle('s', fontName=self.font_name, fontSize=size,
                               alignment=align, textColor=HexColor(color),
                               spaceAfter=6, leading=size * 1.6)
            )
        
        # ─── العنوان ───
        story.append(P(f"تقرير فني رسمي — {report_type}", size=20,
                       align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))
        
        # ─── بيانات الطالب ───
        client_box_data = [
            [self._ar("👤 اسم طالب الخدمة:"), self._ar(requester_name or "........................")],
            [self._ar("📍 الموقع الجغرافي:"), self._ar(city)],
            [self._ar("🐾 الفصيل المستهدف:"), self._ar(breed)],
            [self._ar("📅 تاريخ الإصدار:"), datetime.now().strftime('%Y-%m-%d  |  %H:%M')],
        ]
        ct = Table(client_box_data, colWidths=[150, 340])
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
        story.append(Spacer(1, 20))
        
        # ─── جدول المقارنة ───
        story.append(P("📊 جدول مقارنة العناصر الغذائية", size=13,
                       align=TA_RIGHT, color='#1b5e20'))
        story.append(Spacer(1, 8))
        
        std_key = get_standard_key(animal_type, production_stage)
        standard_vals = NUTRIENT_STANDARDS.get(std_key, NUTRIENT_STANDARDS["دواجن_ناهي"])
        calculated_vals = compute_formula_nutrients(formula)
        
        story.append(self._comparison_table(standard_vals, calculated_vals))
        story.append(Spacer(1, 20))
        
        # ─── ملخص التكاليف ───
        story.append(P("💰 ملخص التكاليف والمعايير", size=13,
                       align=TA_RIGHT, color='#1b5e20'))
        story.append(Spacer(1, 6))
        
        cost_data = [
            [self._ar("البند"), self._ar("القيمة")],
            [self._ar("التكلفة للطن (دولار)"), f"${cost:.2f}"],
            [self._ar(f"التكلفة للطن ({local_sym})"), f"{local_cost:,.2f}"],
            [self._ar("معادل النشاء المحسوب (SE)"), f"{computed_se:.2f} وحدة"],
            [self._ar("البروتين المستهدف (DP)"), f"{target_dp:.2f}%"],
        ]
        
        tc = Table(cost_data, colWidths=[290, 200])
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
        story.append(Spacer(1, 20))
        
        # ─── جدول المكونات ───
        if formula:
            story.append(P("🌾 المكونات المعتمدة للطن الواحد", size=13,
                           align=TA_RIGHT, color='#1b5e20'))
            story.append(Spacer(1, 6))
            
            ing_data = [[
                self._ar("المكون"),
                self._ar("النسبة %"),
                self._ar("كجم/طن"),
            ]]
            for ing, pct in formula.items():
                ing_data.append([
                    self._ar(ing),
                    f"{pct:.2f}%",
                    f"{pct * 10:.1f}",
                ])
            
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
            story.append(Spacer(1, 20))
        
        # ─── الرسم البياني ───
        if include_charts and len(formula) > 1 and MATPLOTLIB_AVAILABLE:
            try:
                fig, ax = plt.subplots(figsize=(7, 3.8))
                names = list(formula.keys())
                vals = list(formula.values())
                colors = ['#1b5e20', '#2e7d32', '#388e3c', '#43a047',
                          '#4caf50', '#66bb6a', '#81c784', '#a5d6a7',
                          '#c8e6c9', '#e8f5e9']
                ax.pie(vals, autopct='%1.1f%%', colors=colors[:len(names)],
                       textprops={'fontsize': 9})
                ax.legend([self._ar(n) for n in names],
                          title=self._ar("المكونات"),
                          loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
                          fontsize=9)
                ax.set_title(self._ar('توزيع المكونات'), fontsize=12)
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=110, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=420, height=240))
            except Exception:
                pass
        
        story.append(Spacer(1, 25))
        
        # ─── صناديق التوقيع ───
        sign = [
            [self._ar("توقيع طالب الخدمة"), self._ar("توقيع المختص")],
            [self._ar("................................"),
             self._ar(SUPERVISOR)],
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
        
        # ─── بناء PDF ───
        doc.build(story,
                  onFirstPage=self._draw_page_decorations,
                  onLaterPages=self._draw_page_decorations)
        buffer.seek(0)
        return buffer.getvalue()


pdf_generator = ProfessionalPDFGenerator()


# ═══════════════════════════════════════════════════════════════════════════
# القسم 17: تصدير Excel متقدم
# ═══════════════════════════════════════════════════════════════════════════

def export_comparison_to_excel(
    standard: dict,
    calculated: dict,
    requester_name: str = "",
    animal: str = "",
    stage: str = "",
    formula: dict = None
) -> bytes:
    """تصدير جدول المقارنة والمكونات إلى Excel منسّق"""
    if not OPENPYXL_AVAILABLE:
        return b""
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "مقارنة العناصر"
    ws.sheet_view.rightToLeft = True
    
    # تنسيقات
    hf = Font(name='Arial', size=12, bold=True, color='FFFFFF')
    hfill = PatternFill('solid', fgColor='1B5E20')
    tf = Font(name='Arial', size=14, bold=True, color='1B5E20')
    inf = Font(name='Arial', size=10, bold=True)
    ct = Alignment(horizontal='center', vertical='center', wrap_text=True)
    rt = Alignment(horizontal='right', vertical='center', wrap_text=True)
    thin = Side(border_style='thin', color='9E9E9E')
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    
    # العنوان
    ws.merge_cells('A1:F1')
    ws['A1'] = f"{APP_NAME} — تقرير مقارنة العناصر الغذائية"
    ws['A1'].font = tf
    ws['A1'].alignment = ct
    
    ws.merge_cells('A2:F2')
    ws['A2'] = f"🤲 {DUA_SHORT} 🤲"
    ws['A2'].font = Font(name='Arial', size=10, bold=True, color='C62828')
    ws['A2'].alignment = ct
    
    # بيانات
    ws['A4'] = "اسم طالب الخدمة:"
    ws['A4'].font = inf
    ws['A4'].alignment = rt
    ws.merge_cells('B4:D4')
    ws['B4'] = requester_name or "---"
    ws['E4'] = "التاريخ:"
    ws['E4'].font = inf
    ws['E4'].alignment = rt
    ws['F4'] = datetime.now().strftime('%Y-%m-%d')
    
    ws['A5'] = "الفصيل:"
    ws['A5'].font = inf
    ws['A5'].alignment = rt
    ws.merge_cells('B5:D5')
    ws['B5'] = f"{animal} — {stage}"
    ws['E5'] = "المشرف:"
    ws['E5'].font = inf
    ws['E5'].alignment = rt
    ws['F5'] = SUPERVISOR
    
    # رأس الجدول
    headers = ["العنصر الغذائي", "المعيار القياسي", "القيمة المحسوبة",
               "الفرق", "الفرق %", "التقييم"]
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=7, column=c, value=h)
        cell.font = hf
        cell.fill = hfill
        cell.alignment = ct
        cell.border = bd
    
    labels = {
        "CP": "بروتين خام CP", "DP": "بروتين مهضوم DP",
        "SE": "معادل النشاء SE", "NDF": "ألياف NDF",
        "ADF": "ألياف ADF", "EE": "دهن EE",
        "ASH": "رماد ASH", "Ca": "كالسيوم Ca", "P": "فسفور P"
    }
    
    row = 8
    for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
        if k not in standard:
            continue
        sv = standard[k]
        cv = calculated.get(k, 0.0)
        diff = cv - sv
        pct = (diff / sv * 100) if sv else 0
        
        if abs(pct) <= 5:
            status, color = "مطابق", 'C8E6C9'
        elif abs(pct) <= 15:
            status, color = "مقبول", 'FFF8E1'
        else:
            status, color = "غير مطابق", 'FFCDD2'
        
        vals = [labels.get(k, k), round(sv, 2), round(cv, 2),
                round(diff, 2), round(pct, 2), status]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.alignment = ct
            cell.border = bd
            cell.fill = PatternFill('solid', fgColor=color)
        row += 1
    
    # جدول المكونات
    if formula:
        row += 2
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
        cell = ws.cell(row=row, column=1, value="🌾 مكونات الخلطة")
        cell.font = tf
        cell.alignment = ct
        row += 1
        
        for c, h in enumerate(["المكون", "النسبة %", "كجم/طن", "", "", ""], 1):
            cell = ws.cell(row=row, column=c, value=h)
            cell.font = hf
            cell.fill = hfill
            cell.alignment = ct
            cell.border = bd
        row += 1
        
        for ing, pct in formula.items():
            ws.cell(row=row, column=1, value=ing).border = bd
            ws.cell(row=row, column=1).alignment = rt
            ws.cell(row=row, column=2, value=round(pct, 2)).border = bd
            ws.cell(row=row, column=2).alignment = ct
            ws.cell(row=row, column=3, value=round(pct * 10, 1)).border = bd
            ws.cell(row=row, column=3).alignment = ct
            row += 1
    
    # تذييل
    row += 2
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    cell = ws.cell(row=row, column=1, value=f"🤲 {DUA_FULL.strip()[:200]}...")
    cell.font = Font(name='Arial', size=9, italic=True, color='1B5E20')
    cell.alignment = Alignment(horizontal='center', wrap_text=True)
    
    # توسيع الأعمدة
    for c in range(1, 7):
        ws.column_dimensions[get_column_letter(c)].width = 22
    
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# القسم 18: إدارة مزارع الدجاج اللاحم
# ═══════════════════════════════════════════════════════════════════════════

class BroilerFarmManager:
    """مدير حسابات مزارع الدجاج اللاحم"""
    
    @staticmethod
    def calculate_adg(current_weight_g, initial_weight_g, age_days):
        if age_days <= 0:
            return 0.0
        return (current_weight_g - initial_weight_g) / age_days
    
    @staticmethod
    def calculate_fcr(total_feed_kg, total_weight_gain_kg):
        if total_weight_gain_kg <= 0:
            return 0.0
        return total_feed_kg / total_weight_gain_kg
    
    @staticmethod
    def calculate_mortality_rate(dead_count, initial_count):
        if initial_count <= 0:
            return 0.0
        return (dead_count / initial_count) * 100.0
    
    @staticmethod
    def calculate_cull_rate(culled_count, initial_count):
        if initial_count <= 0:
            return 0.0
        return (culled_count / initial_count) * 100.0
    
    @staticmethod
    def calculate_livability(initial_count, dead_count):
        return 100.0 - BroilerFarmManager.calculate_mortality_rate(dead_count, initial_count)
    
    @staticmethod
    def calculate_epef(livability, body_weight_kg, age_days, fcr):
        if age_days <= 0 or fcr <= 0:
            return 0.0
        return (livability * body_weight_kg) / (age_days * fcr) * 100.0
    
    @staticmethod
    def get_temp_humidity_table():
        return pd.DataFrame({
            "العمر (يوم)": [1, 7, 14, 21, 28, 35, 42],
            "درجة الحرارة (مئوي)": [33, 30, 28, 26, 24, 22, 21],
            "الرطوبة النسبية (%)": [65, 65, 65, 60, 60, 55, 55],
        })
    
    @staticmethod
    def get_standard_weights():
        """أوزان قياسية قياسية لسلالة Ross 308"""
        return pd.DataFrame({
            "العمر (يوم)": [1, 7, 14, 21, 28, 35, 42],
            "الوزن (جم)": [42, 185, 470, 940, 1550, 2300, 3050],
            "العلف التراكمي (جم)": [15, 130, 450, 1050, 1900, 2900, 4100],
            "FCR": [0.36, 0.70, 0.96, 1.12, 1.23, 1.26, 1.34],
        })


# ═══════════════════════════════════════════════════════════════════════════
# القسم 19: المحرك السعري
# ═══════════════════════════════════════════════════════════════════════════

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG", "name": "جنيه سوداني"},
    "LIBYA": {"rate": 4.80, "sym": "LYD", "name": "دينار ليبي"},
    "مصر": {"rate": 48.0, "sym": "EGP", "name": "جنيه مصري"},
    "السعودية": {"rate": 3.75, "sym": "SAR", "name": "ريال سعودي"},
    "الإمارات": {"rate": 3.67, "sym": "AED", "name": "درهم إماراتي"},
    "باقي دول العالم": {"rate": 1.0, "sym": "USD", "name": "دولار أمريكي"},
}


def load_city_prices() -> dict:
    """تحميل أسعار المدن من ملف JSON"""
    if os.path.exists(CITY_PRICES_FILE):
        try:
            with open(CITY_PRICES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_city_prices(data: dict):
    """حفظ أسعار المدن"""
    try:
        with open(CITY_PRICES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


CITY_CUSTOM_PRICES = load_city_prices()


def get_market_prices(country: str, city: str, state: str = "") -> dict:
    """الحصول على أسعار السوق حسب الموقع"""
    base = {ing: 280.0 for cat in BIG_FEEDS_LIBRARY.values() for ing in cat}
    
    base.update({
        "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "ذرة شامية (أمريكا)": 245.0,
        "شعير مطحون": 210.0, "شعير كامل": 200.0,
        "سورجم (فتريتة)": 195.0, "قمح محلي مصنّع": 240.0, "قمح مستورد": 260.0,
        "جريش أرز رزاز": 220.0, "دخن محلي غزير": 200.0, "شوفان علفي": 260.0,
        "كسرة خبز مجففة": 180.0, "بسكويت مكسر": 320.0,
        "أمباز الفول السوداني (كسب)": 460.0,
        "كسب فول صويا 44%": 440.0, "كسب فول صويا 48%": 480.0,
        "كسب فول صويا 46%": 460.0,
        "كسب عباد الشمس 36%": 310.0, "كسب عباد الشمس 32%": 280.0,
        "كسب بذور القطن (مقشور)": 290.0, "كسب بذور الكتان": 380.0,
        "كسب السمسم المحسن": 520.0,
        "كسب جلوتين الذرة 60%": 680.0, "كسب جلوتين الذرة 40%": 460.0,
        "كسب نواة النخيل": 240.0,
        "نخالة قمح (ردة)": 150.0, "نخالة ذرة": 180.0,
        "البرسيم الجاف (الدريس)": 170.0, "برسيم حجازي": 190.0,
        "مولاس قصب السكر": 120.0,
        "تبن قمح ناعم": 80.0, "تبن فول": 100.0,
        "قشر فول سوداني مطحون": 60.0, "قشور الفول السوداني الكاملة": 70.0,
        "سرسة الأرز المطحونة": 90.0, "قش أرز": 60.0,
        "مخلفات النخيل (تمر مجفف)": 240.0,
        "مسحوق أسماك (Fishmeal 60%)": 850.0,
        "مسحوق أسماك فاخر (72%)": 1250.0,
        "مسحوق اللحم والعظم": 480.0,
        "مسحوق الدم المجفف": 680.0,
        "مسحوق ريش هيدروليزي": 520.0,
        "مركزات دواجن وسمان": 650.0,
        "مركزات خيول ومجترات": 600.0,
        "حليب مجفف منزوع الدسم": 3200.0,
        "حليب مجفف كامل": 3800.0,
        "ليسين نقي (L-Lysine HCl)": 4200.0,
        "ليسين سلفات (L-Lysine SO4)": 3400.0,
        "ميثيونين نقي (DL-Methionine)": 5800.0,
        "ميثيونين هيدروكسي (MHA)": 4900.0,
        "ثريونين نقي (L-Threonine)": 4600.0,
        "تريبتوفان نقي (L-Tryptophan)": 8500.0,
        "فالين نقي (L-Valine)": 5200.0,
        "أرجينين (L-Arginine)": 4800.0,
        "بريمكس تسمين دواجن (Premix Broiler)": 4800.0,
        "بريمكس بياض وبشاير (Layer Premix)": 5200.0,
        "بريمكس أبقار حلابة": 5500.0,
        "بريمكس مجترات عام": 4500.0,
        "بريمكس خيول وأمهار": 5000.0,
        "إنزيم الفايتيز (Phytase 5000)": 12000.0,
        "إنزيم الـ NSP (Xylanase+β-Glucanase)": 14000.0,
        "إنزيم البروتييز (Protease)": 16000.0,
        "كبريتات الحديدوز": 380.0,
        "مستخلص الخمائر (MOS)": 6800.0,
        "خمائر حية (Yeast Culture)": 5200.0,
        "الحجر الجيري (بودرة بلاط)": 40.0,
        "فوسفات ثنائي الكالسيوم (DCP)": 280.0,
        "فوسفات أحادي الكالسيوم (MCP)": 320.0,
        "ملح الطعام": 30.0,
        "بيكربونات الصوديوم (الصودا)": 340.0,
        "أكسيد المغنيسيوم العلفي": 380.0,
        "كبريتات المغنيسيوم": 240.0,
        "يوريا علفية محصنة": 320.0,
        "مضاد سموم فطرية": 950.0,
        "مضاد أكسدة (BHT)": 720.0,
    })
    
    # مضاعفات حسب الدولة
    m = 1.0
    if country == "السودان":
        m = 1.15
        if "كردفان" in state or "النيل الأزرق" in state:
            m = 1.22
            base["سورجم (فتريتة)"] *= 0.85
            base["أمباز الفول السوداني (كسب)"] *= 0.82
        elif state in ["ولاية القضارف", "ولاية الجزيرة"]:
            base["سورجم (فتريتة)"] *= 0.80
            base["أمباز الفول السوداني (كسب)"] *= 0.88
    elif country == "LIBYA":
        m = 1.10
        if city == "طبرق":
            m = 1.06
    elif country == "مصر":
        m = 1.04
    elif country == "السعودية":
        m = 1.08
    elif country == "الإمارات":
        m = 1.12
    
    return {k: v * m for k, v in base.items()}


# ═══════════════════════════════════════════════════════════════════════════
# القسم 20: صور الحيوانات
# ═══════════════════════════════════════════════════════════════════════════

ANIMAL_IMAGES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "إبل": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600",
    "سمان": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "أرانب": "https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?q=80&w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600",
}


# ═══════════════════════════════════════════════════════════════════════════
# القسم 21: تحميل الصور base64
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def get_image_base64(paths: tuple) -> Optional[str]:
    """تحميل صورة كـ base64"""
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                continue
    return None


img_base64 = get_image_base64(tuple(PHOTO_OPTIONS))
logo_base64 = get_image_base64(tuple(LOGO_OPTIONS))


# ═══════════════════════════════════════════════════════════════════════════
# القسم 22: دوال الصوت
# ═══════════════════════════════════════════════════════════════════════════

def play_welcome_audio():
    """تشغيل صوت ترحيبي مع دعاء للوالدين"""
    audio_file = "welcome.mp3"
    
    if not os.path.exists(audio_file):
        if GTTS_AVAILABLE:
            try:
                welcome_text = (
                    "مرحباً بك في منصة تاور نولجي للإنتاج الحيواني وتغذية الحيوان، "
                    f"تحت إشراف {SUPERVISOR}، {SUPERVISOR_TITLE}. "
                    "نسألكم الدعاء للوالد إسماعيل تاور والأخت ابتسام بالرحمة والمغفرة. "
                    "اللهم اغفر لهما وارحمهما واجعل قبرهما روضة من رياض الجنة. "
                    "اللهم اجمعنا بهما في مستقر رحمتك."
                )
                tts = gTTS(text=welcome_text, lang="ar")
                tts.save(audio_file)
            except Exception:
                return
    
    if os.path.exists(audio_file):
        try:
            with open(audio_file, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode()
            st.components.v1.html(
                f'<audio autoplay><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>',
                height=0
            )
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════════
# القسم 23: الحالة الأولية للجلسة
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_SESSION = {
    "approved": False,
    "user_role": None,
    "login_welcome_shown": False,
    "login_attempts": 0,
    "last_login_time": None,
    "session_token": None,
    "audio_played": False,
    "dua_shown": False,
    "active_formula": {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0},
    "active_cp_tag": 12.0,
    "active_se_tag": 65.0,
    "active_breed_tag": "سلالة عامة",
    "active_animal_img": ANIMAL_IMAGES["عام"],
    "active_stage_title": "إنتاج عام",
    "computed_ton_cost": 280.0,
    "inventory": {},
    "shared_comments": (
        f"• [توجيه {SUPERVISOR}]: يرجى من جميع الزملاء إضافة تعليقاتهم هنا.\n"
        f"• 🤲 {DUA_SHORT}\n"
    ),
    "standard_vacc_schedule": {
        1: {"type": "فيتامين", "name": "فيتامين AD3E", "dose": "1 مل/لتر ماء", "route": "مياه الشرب"},
        7: {"type": "لقاح", "name": "نيوكاسل (Lasota)", "dose": "قطرة عين", "route": "قطرة عين/أنف"},
        14: {"type": "لقاح", "name": "Gumboro (Intermediate)", "dose": "قطرة فم", "route": "مياه الشرب"},
        21: {"type": "دواء", "name": "مضاد كوكسيديا", "dose": "1 جم/لتر", "route": "مياه الشرب"},
        28: {"type": "فيتامين", "name": "فيتامين C + E", "dose": "0.5 جم/لتر", "route": "مياه الشرب"},
        35: {"type": "لقاح", "name": "Gumboro booster", "dose": "قطرة فم", "route": "مياه الشرب"},
    },
    "whatsapp_alerts_sent": {},
    "broiler_farms": {},
    "selected_farm": None,
    "global_livestock_prices": {
        "عجول تسمين هولشتاين ($)": 1350.0,
        "أبقار كنانة محلية ($)": 900.0,
        "ضأن محلي ($)": 180.0,
        "ماعز نوبي ($)": 130.0,
        "إبل حاشي (سوداني) ($)": 1200.0,
        "إبل سباق (خليجي) ($)": 25000.0,
        "خيول عربية أصيلة ($)": 4500.0,
        "كتكوت لاحم يوم ($)": 0.65,
        "دجاج بياض بشاير ($)": 5.50,
    },
    "global_products_prices": {
        "كيلو لحم بقري ($)": 7.50,
        "كيلو لحم ضأن ($)": 9.00,
        "كيلو لحم إبل ($)": 8.50,
        "كيلو لحم دجاج ($)": 3.80,
        "طبق بيض 30 بيضة ($)": 4.20,
        "لتر حليب بقر ($)": 0.90,
        "لتر حليب إبل ($)": 3.50,
        "كيلو جبن أبيض ($)": 5.00,
        "كيلو جبن شيدر ($)": 8.50,
    },
}

for k, v in DEFAULT_SESSION.items():
    if k not in st.session_state:
        st.session_state[k] = v

# تهيئة المستودع
if not st.session_state["inventory"]:
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing in cat:
            st.session_state["inventory"][ing] = {
                "quantity": 25.0,
                "min_threshold": 5.0,
                "unit": "طن",
                "last_updated": datetime.now().isoformat(),
            }


# ═══════════════════════════════════════════════════════════════════════════
# القسم 24: CSS المتقدم
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&family=Tajawal:wght@400;500;700&display=swap');

* {
    font-family: 'Cairo', 'Tajawal', 'Amiri', sans-serif;
    color: #1a1a1a !important;
}

html, body, [data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

.stApp { background: transparent; }

.main-box {
    background-color: rgba(255, 255, 255, 0.98);
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18);
    margin-bottom: 50px;
    backdrop-filter: blur(5px);
}

h1, h2, h3, h4, h5, p, span, li, div, label {
    color: #1a1a1a !important;
    text-shadow: none !important;
}

/* 🕌 صندوق الدعاء الرئيسي */
.dua-main-box {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #388e3c 100%);
    padding: 30px;
    border-radius: 20px;
    border: 4px solid #d4af37;
    box-shadow: 0 15px 40px rgba(0,0,0,0.4), inset 0 0 30px rgba(212,175,55,0.2);
    color: white !important;
    direction: rtl;
    text-align: center;
    margin: 20px 0;
    position: relative;
}
.dua-main-box::before {
    content: "🕌";
    position: absolute;
    top: -20px;
    right: 20px;
    font-size: 3rem;
    opacity: 0.3;
}
.dua-main-box * { color: white !important; }
.dua-main-box h3 {
    color: #d4af37 !important;
    font-size: 1.7rem;
    margin-bottom: 15px;
    font-weight: 900;
}
.dua-main-box .names {
    font-size: 1.5rem;
    font-weight: bold;
    color: #ffeb3b !important;
    margin: 15px 0;
    padding: 12px;
    background: rgba(255,255,255,0.1);
    border-radius: 12px;
}
.dua-main-box p.dua-text {
    font-family: 'Amiri', serif !important;
    font-size: 1.2rem;
    line-height: 2.2;
    margin: 15px 0;
    color: #e8f5e9 !important;
}
.dua-main-box p.quran {
    font-family: 'Amiri', serif !important;
    font-size: 1.15rem;
    color: #d4af37 !important;
    margin-top: 20px;
    padding: 15px;
    background: rgba(0,0,0,0.2);
    border-radius: 10px;
    border-right: 4px solid #d4af37;
    border-left: 4px solid #d4af37;
}

/* 🕌 تنبيه الزوار */
.visitor-dua-banner {
    background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 50%, #ffe082 100%);
    padding: 20px 25px;
    border-radius: 15px;
    border-right: 6px solid #d4af37;
    border-left: 6px solid #d4af37;
    margin: 20px 0;
    direction: rtl;
    text-align: center;
    box-shadow: 0px 6px 25px rgba(0,0,0,0.15);
    position: relative;
}
.visitor-dua-banner::before {
    content: "🤲";
    position: absolute;
    top: 50%;
    right: 15px;
    transform: translateY(-50%);
    font-size: 2rem;
    opacity: 0.4;
}
.visitor-dua-banner::after {
    content: "🤲";
    position: absolute;
    top: 50%;
    left: 15px;
    transform: translateY(-50%);
    font-size: 2rem;
    opacity: 0.4;
}
.visitor-dua-banner * {
    color: #4e342e !important;
    font-family: 'Cairo', sans-serif;
}
.visitor-dua-banner b {
    color: #c62828 !important;
    font-size: 1.05rem;
}

/* شريط الدعاء الثابت */
.dua-fixed-banner {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(90deg, #1b5e20, #2e7d32, #1b5e20);
    color: white !important;
    padding: 10px 15px;
    z-index: 9998;
    text-align: center;
    border-top: 3px solid #d4af37;
    font-family: 'Amiri', serif !important;
    font-size: 1rem;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.3);
}
.dua-fixed-banner * {
    color: #ffeb3b !important;
    font-family: 'Amiri', serif !important;
}

/* عناصر أخرى */
.section-title {
    color: #1b5e20 !important;
    border-right: 6px solid #2e7d32;
    padding: 10px 15px;
    text-align: right;
    font-size: 1.5rem;
    font-weight: bold;
    margin-top: 30px;
    margin-bottom: 20px;
    background: linear-gradient(to left, rgba(46,125,50,0.1), transparent);
    border-radius: 8px;
}

.formula-item {
    background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(232,245,233,0.95));
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
.formula-item:hover { transform: translateX(-5px); }

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
.price-card * { color: #1a1a1a !important; }

.warning-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 15px;
    border-radius: 12px;
    border-right: 5px solid #f57c00;
    margin-bottom: 15px;
    direction: rtl;
    text-align: right;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
}
.warning-card * { color: #e65100 !important; }

.profile-img-style {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #d4af37;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.25);
    display: block;
    margin: 0 auto;
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
    text-align: center;
    transition: transform 0.3s ease;
}
.metric-card:hover { transform: translateY(-5px); }

.stButton > button {
    color: #1a1a1a !important;
    background-color: #e8f5e9 !important;
    border: 1px solid #2e7d32 !important;
    font-weight: bold !important;
}
.stButton > button:hover { background-color: #c8e6c9 !important; }

.mini-signature {
    position: fixed;
    left: 20px;
    bottom: 60px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important;
    padding: 8px 20px;
    font-size: 0.85rem;
    border-radius: 25px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    z-index: 9997;
    direction: rtl;
    border: 2px solid #d4af37;
}
.mini-signature * { color: white !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# القسم 25: بوابة الدخول مع دعاء الوالدين
# ═══════════════════════════════════════════════════════════════════════════

if not st.session_state["approved"]:
    
    # قفل مؤقت
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        if st.session_state["last_login_time"]:
            td = (datetime.now() - st.session_state["last_login_time"]).seconds
            if td < LOCKOUT_TIME:
                st.error(f"🔒 قفل مؤقت. المتبقي {LOCKOUT_TIME - td} ثانية")
                st.stop()
            else:
                st.session_state["login_attempts"] = 0
    
    st.markdown('<div class="main-box" style="max-width: 700px; margin: 30px auto; direction: rtl;">', unsafe_allow_html=True)
    
    # 🕌 الدعاء الافتتاحي
    st.markdown(f"""
    <div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <p style="font-size:1.05rem; color:#a5d6a7 !important; margin-bottom:10px;">
        نبدأ باسم الله، ونسألُه أن يتقبّلَ هذا العملَ صدقةً جاريةً عن:
        </p>
        <div class="names">
        🕊️ الأستاذ / إسماعيل تاور 🕊️<br>
        🕊️ الأخت / ابتسام 🕊️
        </div>
        <p class="dua-text">{DUA_FULL}</p>
        <p class="quran">{DUA_QURAN}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🤲 آمين يا رب العالمين — الدخول إلى المنصة", type="primary", use_container_width=True):
        st.session_state["dua_shown"] = True
    
    st.markdown("<hr style='border-top: 2px solid #d4af37; margin: 25px 0;'>", unsafe_allow_html=True)
    
    # الشعار والعنوان
    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        if img_base64:
            st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">',
                        unsafe_allow_html=True)
    with col_title:
        st.markdown(f"<h2 style='color:#2E7D32; text-align:right; margin-bottom:5px;'>🌾 {APP_NAME}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.1rem; margin:5px 0;'>{APP_TAGLINE}</p>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#c62828; text-align:right; margin-top:5px;'>{SUPERVISOR} — {SUPERVISOR_TITLE}</h4>", unsafe_allow_html=True)
    
    # QR Code
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(PLATFORM_URL)
        qr.make(fit=True)
        qi = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        qi.save(buf, format="PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode()
        st.markdown(f'<div style="text-align:center; margin:20px 0;">'
                    f'<img src="data:image/png;base64,{qr_b64}" width="150"></div>',
                    unsafe_allow_html=True)
    except Exception:
        pass
    
    st.markdown("<h3 style='text-align:center; color:#1b5e20;'>🔐 بوابة الدخول</h3>", unsafe_allow_html=True)
    
    login_option = st.radio("طريقة الدخول:", ["كود الدخول السري", "اسم المستخدم وكلمة المرور"],
                            horizontal=True)
    
    if login_option == "كود الدخول السري":
        code = st.text_input("🔑 كود الدخول:", type="password")
        if st.button("🔓 تسجيل الدخول", type="primary", use_container_width=True):
            code_stripped = code.strip()
            if code_stripped in CODES_DB:
                st.session_state.update({
                    "approved": True,
                    "user_role": CODES_DB[code_stripped]["role"],
                    "login_welcome_shown": False,
                    "login_attempts": 0,
                    "last_login_time": datetime.now(),
                    "session_token": secrets.token_urlsafe(32),
                })
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                st.session_state["last_login_time"] = datetime.now()
                st.error(f"❌ كود غير صحيح! متبقي {MAX_LOGIN_ATTEMPTS - st.session_state['login_attempts']} محاولات")
    else:
        u = st.text_input("👤 اسم المستخدم")
        p = st.text_input("🔑 كلمة المرور", type="password")
        if st.button("🔓 تسجيل الدخول", type="primary", use_container_width=True):
            user = auth_manager.authenticate(u, p)
            if user:
                st.session_state.update({
                    "approved": True,
                    "user_role": user['role'],
                    "login_welcome_shown": False,
                    "login_attempts": 0,
                    "last_login_time": datetime.now(),
                    "session_token": secrets.token_urlsafe(32),
                    "user": user,
                })
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                st.session_state["last_login_time"] = datetime.now()
                st.error(f"❌ بيانات غير صحيحة! متبقي {MAX_LOGIN_ATTEMPTS - st.session_state['login_attempts']} محاولات")
        st.caption("💡 admin / admin123")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════
# القسم 26: بعد تسجيل الدخول
# ═══════════════════════════════════════════════════════════════════════════

if not st.session_state["audio_played"]:
    play_welcome_audio()
    st.session_state["audio_played"] = True

if not st.session_state["login_welcome_shown"]:
    role_msg = {
        "owner": f"👋 مرحباً بك {SUPERVISOR}",
        "specialist": "🔬 أهلاً بالزملاء المختصين",
        "breeder": "🚜 أهلاً بكم أخي المربي",
    }
    st.toast(role_msg.get(st.session_state["user_role"], "مرحباً"), icon="🌾")
    st.session_state["login_welcome_shown"] = True


# ═══════════════════════════════════════════════════════════════════════════
# القسم 27: الواجهة الرئيسية
# ═══════════════════════════════════════════════════════════════════════════

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# الشريط العلوي — تسجيل الخروج
c_logout1, c_logout2 = st.columns([0.7, 0.3])
with c_logout2:
    roles = {
        "owner": f"{SUPERVISOR} 👑",
        "specialist": "المختص 👨‍🔬",
        "breeder": "المربي 🌾",
    }
    st.markdown(
        f"<div style='text-align:left; padding:10px; background:linear-gradient(135deg,#f5f5f5,#e0e0e0); border-radius:10px;'>"
        f"الحساب: <b>{roles.get(st.session_state['user_role'], 'مستخدم')}</b><br>"
        f"<small>آخر دخول: {datetime.now().strftime('%Y-%m-%d %H:%M')}</small></div>",
        unsafe_allow_html=True
    )
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        keys_to_keep = {"inventory"}
        for k in list(st.session_state.keys()):
            if k not in keys_to_keep:
                del st.session_state[k]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

# الشعار والعنوان
col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">',
                    unsafe_allow_html=True)
with col_title:
    st.markdown(f"<h1 style='color:#1b5e20; text-align:right; margin-bottom:0;'>{APP_NAME} 🌾</h1>",
                unsafe_allow_html=True)
    st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.2rem; margin-top:5px;'>{APP_TAGLINE}</p>",
                unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:#c62828; text-align:right; margin-top:5px;'>{SUPERVISOR} — {SUPERVISOR_TITLE}</h3>",
                unsafe_allow_html=True)

# 🕌 تنبيه الزوار بالدعاء
st.markdown(f'<div class="visitor-dua-banner">{DUA_VISITOR_BANNER}</div>',
            unsafe_allow_html=True)

st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# القسم 28: شريط المشاركة التسويقية
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("### 📢 المشاركة التسويقية والدعوة العلمية")

share_text = f"""📢 دعوة علمية وتسويقية من {APP_NAME}

{f"إشراف: {SUPERVISOR} — {SUPERVISOR_TITLE}"}

🕌 صدقة جارية عن: الأستاذ إسماعيل تاور، والأخت ابتسام (رحمهما الله)

🎯 ما تقدمه المنصة:
• حلول ذكية لتركيب الأعلاف بأقل تكلفة
• حسابات دقيقة بناءً على البروتين المهضوم DP ومعادل النشاء SE
• 8 قطاعات: أغنام، ماعز، أبقار، إبل، خيول، دواجن، سمان، أسماك
• بدائل حليب (عجول، حملان، جديان، إبل، أمهار)
• مختبر ذكي لتحليل الصور OCR
• تقارير PDF احترافية + Excel
• إدارة مزارع الدجاج اللاحم مع KPIs

🔗 {PLATFORM_URL}"""

st.text_area("النص الدعائي:", value=share_text, height=200, key="share_box")

c_copy, c_share = st.columns(2)
with c_copy:
    if st.button("📋 تجهيز النص للمشاركة", use_container_width=True):
        st.success("✅ تم تجهيز النص! يمكنك الآن نسخه ومشاركته.")
with c_share:
    enc = urllib.parse.quote(share_text[:500])
    st.link_button("📲 مشاركة عبر واتساب", f"https://wa.me/?text={enc}",
                   use_container_width=True)

st.markdown("---")


# ═══════════════════════════════════════════════════════════════════════════
# القسم 29: التبويبات الرئيسية
# ═══════════════════════════════════════════════════════════════════════════

if st.session_state["user_role"] == "owner":
    tabs_titles = [
        "🔬 تركيب الأعلاف", "🍼 بدائل الحليب", "📷 المختبر الذكي",
        "📊 البورصة", "🏭 المستودعات", "🧾 الفواتير",
        "🖨️ الديباجة", "📈 التحليلات",
        "🐔 مزارع الدجاج", "💬 التعليقات",
        "📚 المراجع", "💡 المساعدة", "📖 الدليل",
    ]
elif st.session_state["user_role"] == "specialist":
    tabs_titles = [
        "🔬 تركيب الأعلاف", "🍼 بدائل الحليب", "📷 المختبر الذكي",
        "📊 البورصة", "🏭 المستودعات", "🧾 الفواتير",
        "🖨️ الديباجة", "📈 التحليلات",
        "💬 التعليقات", "📚 المراجع", "💡 المساعدة", "📖 الدليل",
    ]
else:
    tabs_titles = [
        "🔬 تركيب الأعلاف", "📚 المراجع",
        "💡 المساعدة", "📖 الدليل",
    ]

tabs = st.tabs(tabs_titles)


# ═══════════════════════════════════════════════════════════════════════════
# القسم 30: تبويب تركيب الأعلاف — 8 قطاعات
# ═══════════════════════════════════════════════════════════════════════════

with tabs[0]:
    st.markdown('<div class="section-title">🌍 الموقع الجغرافي والأسعار</div>',
                unsafe_allow_html=True)
    
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        country = st.selectbox("🌍 الدولة:", list(EXCHANGE_RATES.keys()))
    with cc2:
        state = st.text_input("🗺️ الولاية/الإقليم:", "الخرطوم")
    with cc3:
        city = st.text_input("🏙️ المدينة:", "الخرطوم")
    
    rate_info = EXCHANGE_RATES.get(country, {"rate": 1.0, "sym": "USD"})
    local_rate = rate_info["rate"]
    local_sym = rate_info["sym"]
    live_prices = get_market_prices(country, city, state)
    
    # عرض بورصة الماشية والمنتجات
    pc1, pc2 = st.columns(2)
    with pc1:
        livestock_html = f'<div class="price-card"><b>📈 بورصة الماشية والداجن ({city}):</b><br>'
        for k, v in list(st.session_state["global_livestock_prices"].items())[:7]:
            livestock_html += f'▪️ {k}: <b>${v:.2f}</b> <span style="color:#e65100; font-weight:bold;">({v*local_rate:,.0f} {local_sym})</span><br>'
        livestock_html += '</div>'
        st.markdown(livestock_html, unsafe_allow_html=True)
    with pc2:
        products_html = f'<div class="price-card"><b>🥩 بورصة المنتجات ({city}):</b><br>'
        for k, v in list(st.session_state["global_products_prices"].items())[:7]:
            products_html += f'▪️ {k}: <b>${v:.2f}</b> <span style="color:#1b5e20; font-weight:bold;">({v*local_rate:,.0f} {local_sym})</span><br>'
        products_html += '</div>'
        st.markdown(products_html, unsafe_allow_html=True)
    
    # ─── 8 تبويبات للحيوانات ───
    st.markdown('<div class="section-title">🐾 اختر الحيوان للموازنة</div>',
                unsafe_allow_html=True)
    
    animal_tabs = st.tabs([
        "🐏 أغنام", "🐐 ماعز", "🐄 أبقار", "🐪 إبل",
        "🐎 خيول", "🐔 دواجن", "🦆 سمان", "🐟 أسماك",
    ])
    
    animal_choice = None
    stage_choice = None
    gender_choice = ""
    default_dp = 12.0
    default_se = 65.0
    img_key = "عام"
    
    # ── الأغنام ──
    with animal_tabs[0]:
        st.markdown("#### 🐏 تركيب علف الأغنام")
        sg = st.radio("الجنس:", ["ذكور (تسمين)", "إناث (حليب/أمهات)"],
                      horizontal=True, key="sg")
        if "ذكور" in sg:
            ss = st.selectbox("المرحلة:",
                ["تسمين مكثف", "تسمين عادي", "حملان تيد"], key="ss_m")
            default_dp = {"تسمين مكثف": 12.0, "تسمين عادي": 10.5, "حملان تيد": 9.5}[ss]
            default_se = {"تسمين مكثف": 65.0, "تسمين عادي": 60.0, "حملان تيد": 58.0}[ss]
        else:
            ss = st.selectbox("المرحلة:",
                ["نعاج مرضعات", "نعاج حامل", "صيانة"], key="ss_f")
            default_dp = {"نعاج مرضعات": 12.8, "نعاج حامل": 11.0, "صيانة": 8.0}[ss]
            default_se = {"نعاج مرضعات": 66.0, "نعاج حامل": 62.0, "صيانة": 50.0}[ss]
        if st.checkbox("✅ اعتماد اختيار الأغنام للتركيب", key="use_sheep"):
            animal_choice, stage_choice, gender_choice = "أغنام", ss, sg
            img_key = "أغنام"
    
    # ── الماعز ──
    with animal_tabs[1]:
        st.markdown("#### 🐐 تركيب علف الماعز")
        gg = st.radio("الجنس:", ["ذكور (تسمين)", "إناث (حليب/أمهات)"],
                      horizontal=True, key="gg")
        if "ذكور" in gg:
            gs = st.selectbox("المرحلة:", ["تسمين جديان", "تيوس"],
                             key="gs_m")
            default_dp = 11.5 if "جديان" in gs else 9.0
            default_se = 62.0 if "جديان" in gs else 55.0
        else:
            gs = st.selectbox("المرحلة:",
                ["عنزات حلابة عالي", "عنزات حلابة متوسط", "عنزات حامل", "صيانة"],
                key="gs_f")
            default_dp = {"عنزات حلابة عالي": 13.0, "عنزات حلابة متوسط": 11.8,
                         "عنزات حامل": 10.5, "صيانة": 7.8}[gs]
            default_se = {"عنزات حلابة عالي": 67.0, "عنزات حلابة متوسط": 62.0,
                         "عنزات حامل": 60.0, "صيانة": 48.0}[gs]
        if st.checkbox("✅ اعتماد اختيار الماعز للتركيب", key="use_goat"):
            animal_choice, stage_choice, gender_choice = "ماعز", gs, gg
            img_key = "ماعز"
    
    # ── الأبقار ──
    with animal_tabs[2]:
        st.markdown("#### 🐄 تركيب علف الأبقار")
        cs = st.selectbox("نوع الإنتاج:",
            ["حليب عالي الإدرار", "حليب متوسط", "تسمين مكثف", "تسمين عادي", "صيانة"],
            key="cs")
        default_dp = {"حليب عالي الإدرار": 13.5, "حليب متوسط": 12.5,
                     "تسمين مكثف": 10.5, "تسمين عادي": 10.0, "صيانة": 8.0}[cs]
        default_se = {"حليب عالي الإدرار": 72.0, "حليب متوسط": 68.0,
                     "تسمين مكثف": 70.0, "تسمين عادي": 65.0, "صيانة": 55.0}[cs]
        if st.checkbox("✅ اعتماد اختيار الأبقار للتركيب", key="use_cattle"):
            animal_choice, stage_choice, gender_choice = "أبقار", cs, ""
            img_key = "أبقار"
    
    # ── الإبل ──
    with animal_tabs[3]:
        st.markdown("#### 🐪 تركيب علف الإبل — وفق NRC / FAO")
        st.info("🐪 الإبل كائن فريد — كرشها يتحمل العطش وتحتاج بروتيناً أقل وأليافاً أكثر من الأبقار.")
        cams = st.selectbox("نوع الإنتاج:",
            ["نمو", "تسمين", "حليب عالي", "حليب متوسط", "سباق (هجن)", "صيانة"],
            key="cams")
        cwt = st.number_input("الوزن الحي (كجم):", 100.0, 800.0, 400.0, 25.0, key="cwt")
        
        default_dp = {"نمو": 10.5, "تسمين": 9.5, "حليب عالي": 13.0,
                     "حليب متوسط": 12.0, "سباق (هجن)": 14.0, "صيانة": 7.5}[cams]
        default_se = {"نمو": 60.0, "تسمين": 65.0, "حليب عالي": 68.0,
                     "حليب متوسط": 64.0, "سباق (هجن)": 72.0, "صيانة": 50.0}[cams]
        
        dry_matter = cwt * 0.025
        st.info(f"📊 متطلبات الإبل: DP = {default_dp}% | SE = {default_se} | "
                f"المادة الجافة ≈ {dry_matter:.1f} كجم/يوم")
        
        if st.checkbox("✅ اعتماد اختيار الإبل للتركيب", key="use_camel"):
            animal_choice, stage_choice, gender_choice = "إبل", cams, ""
            img_key = "إبل"
    
    # ── الخيول ──
    with animal_tabs[4]:
        st.markdown("#### 🐎 تركيب علف الخيول")
        hs = st.selectbox("نوع الإنتاج:",
            ["رياضة مكثف", "رياضة عادي", "أمهار بداية", "فرسات مرضعات", "صيانة"],
            key="hs")
        default_dp = {"رياضة مكثف": 10.0, "رياضة عادي": 9.5, "أمهار بداية": 14.0,
                     "فرسات مرضعات": 12.5, "صيانة": 7.5}[hs]
        default_se = {"رياضة مكثف": 70.0, "رياضة عادي": 65.0, "أمهار بداية": 70.0,
                     "فرسات مرضعات": 68.0, "صيانة": 55.0}[hs]
        if st.checkbox("✅ اعتماد اختيار الخيول للتركيب", key="use_horse"):
            animal_choice, stage_choice, gender_choice = "خيول", hs, ""
            img_key = "خيول"
    
    # ── الدواجن ──
    with animal_tabs[5]:
        st.markdown("#### 🐔 تركيب علف الدواجن")
        ps = st.selectbox("المرحلة:",
            ["بادي", "نامي", "ناهي", "بياض بادي", "بياض نامي",
             "بياض ناهي", "بياض إنتاج", "أمهات"],
            key="ps")
        default_dp = {"بادي": 20.0, "نامي": 18.5, "ناهي": 16.5,
                     "بياض بادي": 17.5, "بياض نامي": 15.5, "بياض ناهي": 14.5,
                     "بياض إنتاج": 15.5, "أمهات": 14.0}[ps]
        default_se = {"بادي": 76.0, "نامي": 74.0, "ناهي": 75.0,
                     "بياض بادي": 72.0, "بياض نامي": 70.0, "بياض ناهي": 70.0,
                     "بياض إنتاج": 72.0, "أمهات": 70.0}[ps]
        if st.checkbox("✅ اعتماد اختيار الدواجن للتركيب", key="use_poultry"):
            animal_choice, stage_choice, gender_choice = "دواجن لاحم", ps, ""
            img_key = "دواجن"
    
    # ── السمان ──
    with animal_tabs[6]:
        st.markdown("#### 🦆 تركيب علف السمان")
        qs = st.selectbox("المرحلة:",
            ["سمان بادي", "سمان نامي", "سمان ناهي", "سمان بياض"],
            key="qs")
        default_dp = {"سمان بادي": 20.5, "سمان نامي": 18.5,
                     "سمان ناهي": 17.0, "سمان بياض": 15.0}[qs]
        default_se = {"سمان بادي": 74.0, "سمان نامي": 72.0,
                     "سمان ناهي": 70.0, "سمان بياض": 68.0}[qs]
        if st.checkbox("✅ اعتماد اختيار السمان للتركيب", key="use_quail"):
            animal_choice, stage_choice, gender_choice = "سمان", qs, ""
            img_key = "سمان"
    
    # ── الأسماك ──
    with animal_tabs[7]:
        st.markdown("#### 🐟 تركيب علف الأسماك")
        fs = st.selectbox("المرحلة:",
            ["بادئ زريعة", "نمو متوسط", "تسمين", "أمهات"], key="fs")
        default_dp = {"بادئ زريعة": 32.0, "نمو متوسط": 25.0,
                     "تسمين": 22.0, "أمهات": 28.0}[fs]
        default_se = {"بادئ زريعة": 72.0, "نمو متوسط": 70.0,
                     "تسمين": 68.0, "أمهات": 72.0}[fs]
        if st.checkbox("✅ اعتماد اختيار الأسماك للتركيب", key="use_fish"):
            animal_choice, stage_choice, gender_choice = "أسماك", fs, ""
            img_key = "أسماك"
    
    if not animal_choice:
        st.warning("⚠️ اختر حيواناً واحداً من التبويبات أعلاه، وفعّل خيار (✅ اعتماد اختيار) للمتابعة.")
        st.stop()
    
    st.markdown(f"### 🎯 الحيوان المختار: **{animal_choice}** — المرحلة: **{stage_choice}**",
                unsafe_allow_html=True)
    
    # ─── اسم طالب العلفة ───
    st.markdown('<div class="section-title">👤 بيانات طالب الخدمة</div>',
                unsafe_allow_html=True)
    requester_name = st.text_input(
        "اسم طالب العلفة (سيظهر في التقرير الرسمي):",
        placeholder="مثال: مزرعة الأمل — أحمد محمد",
        key="requester_form"
    )
    
    # ─── الموازنة ───
    st.markdown('<div class="section-title">📋 حدود الموازنة الذكية</div>',
                unsafe_allow_html=True)
    p1, p2 = st.columns(2)
    with p1:
        st.metric("🧬 البروتين المهضوم (DP) المقترح:", f"{default_dp}%")
        use_custom_dp = st.checkbox("⚙️ تعديل يدوي للـ DP")
        target_dp = (st.slider("نسبة DP المستهدفة:", 5.0, 40.0, float(default_dp))
                     if use_custom_dp else default_dp)
    with p2:
        st.metric("🌽 معادل النشاء (SE) المقترح:", f"{default_se}")
        use_custom_se = st.checkbox("⚙️ تعديل يدوي للـ SE")
        target_se = (st.slider("معادل SE المستهدف:", 10.0, 90.0, float(default_se))
                     if use_custom_se else default_se)
    
    # ─── اختيار المكونات ───
    st.markdown('<div class="section-title">🌾 اختيار المكونات والأسعار</div>',
                unsafe_allow_html=True)
    
    selected_ingredients = []
    ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}",
                         expanded="الحبوب" in cat_name or "الأكساب" in cat_name):
            sub_cols = st.columns(3)
            for i, (ing_name, ing_data) in enumerate(items.items()):
                with sub_cols[i % 3]:
                    # مكونات إلزامية
                    default_check = False
                    if animal_choice in ["أغنام", "ماعز", "أبقار", "إبل", "خيول"]:
                        if ing_name in ["ملح الطعام", "الحجر الجيري (بودرة بلاط)",
                                       "فوسفات ثنائي الكالسيوم (DCP)",
                                       "بيكربونات الصوديوم (الصودا)"]:
                            default_check = True
                    elif animal_choice in ["دواجن لاحم", "سمان"]:
                        if ing_name in ["ملح الطعام", "الحجر الجيري (بودرة بلاط)",
                                       "فوسفات ثنائي الكالسيوم (DCP)",
                                       "بريمكس تسمين دواجن (Premix Broiler)"]:
                            default_check = True
                    elif animal_choice == "أسماك":
                        if ing_name in ["ملح الطعام", "فوسفات ثنائي الكالسيوم (DCP)"]:
                            default_check = True
                    
                    checked = st.checkbox(
                        ing_name, value=default_check,
                        key=f"ck_{animal_choice}_{ing_name}"
                    )
                    
                    price = live_prices.get(ing_name, 300.0)
                    
                    if st.session_state["user_role"] == "owner":
                        price = st.number_input(
                            f"السعر للطن $:",
                            min_value=5.0, value=float(price),
                            key=f"price_{animal_choice}_{ing_name}",
                            label_visibility="collapsed"
                        )
                    else:
                        st.caption(f"💰 ${price:.0f}/طن")
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price
    
    st.markdown("---")
    
    # ─── زر التشغيل ───
    if st.button("🚀 تشغيل محرك التركيب التلقائي الدقيق (فرق ≤ 0.5%)",
                 type="primary", use_container_width=True):
        
        if len(selected_ingredients) < 3:
            st.error("⚠️ اختر 3 مكونات على الأقل.")
        else:
            with st.spinner("⏳ جاري التشغيل..."):
                std_key = get_standard_key(animal_choice, stage_choice, gender_choice)
                result = auto_formulate_precise(
                    selected_ingredients, ingredient_prices,
                    target_dp, target_se, std_key,
                    tolerance=0.5, max_iterations=30
                )
            
            if result["success"]:
                formula = result["formula"]
                actual = result["actual_nutrients"]
                cost = result["cost"]
                
                # رسالة النجاح
                st.success(
                    f"✅ تم التركيب بنجاح!\n\n"
                    f"📊 الفرق: DP = {result['dp_error']:.3f}% | SE = {result['se_error']:.3f}\n"
                    f"🔁 عدد التكرارات: {result['iterations']}"
                )
                
                # جدول المقارنة
                st.markdown("### 📊 جدول مقارنة العناصر الغذائية")
                std = NUTRIENT_STANDARDS.get(std_key, {})
                
                compare_rows = []
                labels = {"CP": "بروتين خام CP", "DP": "بروتين مهضوم DP",
                         "SE": "معادل النشاء SE", "NDF": "NDF", "ADF": "ADF",
                         "EE": "دهن EE", "ASH": "رماد ASH",
                         "Ca": "Ca", "P": "P"}
                
                for k, sv in std.items():
                    cv = actual.get(k, 0.0)
                    diff = cv - sv
                    pct = (diff / sv * 100) if sv else 0
                    
                    if abs(pct) <= 5:
                        status = "✅ مطابق"
                    elif abs(pct) <= 15:
                        status = "⚠️ مقبول"
                    else:
                        status = "❌ غير مطابق"
                    
                    compare_rows.append({
                        "العنصر": labels.get(k, k),
                        "المعيار القياسي": f"{sv:.2f}",
                        "القيمة المحسوبة": f"{cv:.2f}",
                        "الفرق": f"{diff:+.2f}",
                        "الفرق %": f"{pct:+.1f}%",
                        "التقييم": status,
                    })
                
                st.dataframe(pd.DataFrame(compare_rows),
                             use_container_width=True, hide_index=True)
                
                # عرض المكونات
                st.markdown("#### 🌾 المكونات المعتمدة للطن الواحد:")
                for ing, pct in formula.items():
                    st.markdown(
                        f'<div class="formula-item">▪️ <b>{ing}:</b> '
                        f'{pct:.2f}% ({pct*10:.1f} كجم/طن)</div>',
                        unsafe_allow_html=True
                    )
                
                st.metric("💰 التكلفة الفعلية للطن:",
                          f"${cost:.2f} ({cost*local_rate:,.0f} {local_sym})")
                
                # تحديث الحالة
                st.session_state["active_formula"] = formula
                st.session_state["active_cp_tag"] = target_dp
                st.session_state["active_se_tag"] = actual["SE"]
                st.session_state["computed_ton_cost"] = cost
                st.session_state["active_animal_img"] = ANIMAL_IMAGES.get(img_key, ANIMAL_IMAGES["عام"])
                st.session_state["active_stage_title"] = f"{animal_choice} — {stage_choice}"
                
                # تحميل التقارير
                st.markdown("### 📥 تحميل التقارير")
                dl1, dl2 = st.columns(2)
                
                with dl1:
                    try:
                        pdf_bytes = pdf_generator.generate_comprehensive_report(
                            formula=formula,
                            target_dp=target_dp,
                            breed=f"{animal_choice} — {stage_choice}",
                            cost=cost,
                            city=city,
                            local_cost=cost * local_rate,
                            local_sym=local_sym,
                            computed_se=actual["SE"],
                            requester_name=requester_name,
                            animal_type=animal_choice,
                            production_stage=stage_choice,
                            include_charts=True,
                            report_type=f"تركيب علفة — {animal_choice}"
                        )
                        fname = f"TaworNology_{animal_choice}_{datetime.now():%Y%m%d_%H%M}.pdf"
                        st.download_button(
                            "📥 تحميل تقرير PDF", pdf_bytes,
                            file_name=fname,
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"⚠️ خطأ PDF: {e}")
                
                with dl2:
                    try:
                        xl_bytes = export_comparison_to_excel(
                            standard=std,
                            calculated=actual,
                            requester_name=requester_name,
                            animal=animal_choice,
                            stage=stage_choice,
                            formula=formula
                        )
                        if xl_bytes:
                            fname = f"TaworNology_{animal_choice}_{datetime.now():%Y%m%d_%H%M}.xlsx"
                            st.download_button(
                                "📊 تحميل Excel", xl_bytes,
                                file_name=fname,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"⚠️ خطأ Excel: {e}")
                
                # رسم بياني
                if PLOTLY_AVAILABLE and len(formula) > 1:
                    try:
                        fig = px.pie(
                            values=list(formula.values()),
                            names=list(formula.keys()),
                            title="توزيع المكونات في الخلطة",
                            color_discrete_sequence=px.colors.sequential.Greens
                        )
                        fig.update_layout(height=450)
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass
            else:
                st.error(f"❌ {result['message']}")
                if "log" in result:
                    with st.expander("سجل المحاولات"):
                        for line in result["log"][-10:]:
                            st.text(line)


# ═══════════════════════════════════════════════════════════════════════════
# القسم 31: تبويب بدائل الحليب
# ═══════════════════════════════════════════════════════════════════════════

if "🍼 بدائل الحليب" in tabs_titles:
    with tabs[tabs_titles.index("🍼 بدائل الحليب")]:
        st.markdown('<div class="section-title">🍼 مختبر تركيب بدائل الحليب</div>',
                    unsafe_allow_html=True)
        st.write("تركيب بدائل حليب متوازنة للعجول والحملان والجديان والإبل والأمهار — وفق المعايير العالمية (NRC).")
        
        mr1, mr2 = st.columns(2)
        with mr1:
            mr_animal = st.selectbox("نوع الحيوان:",
                list(MILK_REPLACER_STANDARDS.keys()),
                key="mr_animal")
            mr_volume = st.number_input("الكمية المطلوبة (كجم):",
                1.0, 10000.0, 100.0, 10.0, key="mr_volume")
            mr_requester = st.text_input("اسم طالب التركيب:",
                placeholder="مثال: مزرعة النخيل", key="mr_requester")
        
        with mr2:
            std_mr = MILK_REPLACER_STANDARDS[mr_animal]
            st.markdown(f"""
            <div class="price-card">
            <b>📊 المعيار القياسي — {mr_animal}:</b><br>
            ▪️ البروتين الخام (CP): <b>{std_mr['CP']}%</b><br>
            ▪️ الدهن (Fat): <b>{std_mr['Fat']}%</b><br>
            ▪️ اللاكتوز: <b>{std_mr['Lactose']}%</b><br>
            ▪️ الليسين: <b>{std_mr['Lysine']}%</b><br>
            ▪️ الكالسيوم (Ca): <b>{std_mr['Ca']}%</b><br>
            ▪️ الفسفور (P): <b>{std_mr['P']}%</b><br>
            ▪️ أقصى ألياف: <b>{std_mr['Fiber_max']}%</b><br>
            ▪️ أقصى رماد: <b>{std_mr['Ash_max']}%</b><br>
            <small style="color:#555;">📝 {std_mr['notes']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("#### 🌾 اختر المكونات المتاحة:")
        
        mr_selected = []
        mr_cols = st.columns(3)
        for i, (ing_name, ing_data) in enumerate(MILK_REPLACER_INGREDIENTS.items()):
            with mr_cols[i % 3]:
                # الافتراضي
                default_mr = ing_name in [
                    "حليب مجفف منزوع الدسم", "حليب مجفف كامل الدسم",
                    "شرش حليب مجفف", "زيت جوز الهند", "زيت النخيل",
                    "بريمكس فيتامينات حليب", "كالسيوم كربونات",
                    "فوسفات ثنائي الكالسيوم", "ملح طعام",
                ]
                
                checked = st.checkbox(
                    f"{ing_name}",
                    value=default_mr,
                    key=f"mr_ck_{ing_name}"
                )
                st.caption(f"💰 ${ing_data['price']}/طن — {ing_data['desc']}")
                
                if checked:
                    mr_selected.append(ing_name)
        
        st.markdown("---")
        
        if st.button("🧪 تشغيل تركيب بديل الحليب",
                     type="primary", use_container_width=True, key="mr_run"):
            
            if len(mr_selected) < 3:
                st.warning("⚠️ اختر 3 مكونات على الأقل.")
            else:
                with st.spinner("جاري التركيب..."):
                    result_mr = formulate_milk_replacer(
                        mr_animal, mr_volume, mr_selected
                    )
                
                if result_mr["success"]:
                    st.success(f"✅ تم تركيب بديل الحليب لـ ({mr_animal})")
                    
                    st.markdown(f"#### 📝 التركيبة المعتمدة لكل 100 كجم:")
                    for ing, pct in result_mr["formula"].items():
                        kg_for_order = pct * mr_volume / 100.0
                        st.markdown(
                            f'<div class="formula-item">▪️ <b>{ing}:</b> '
                            f'{pct:.2f}% ({kg_for_order:.2f} كجم للكمية المطلوبة)</div>',
                            unsafe_allow_html=True
                        )
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("💰 التكلفة لـ 100 كجم:", f"${result_mr['cost_per_100kg']:.2f}")
                    m2.metric("💰 التكلفة لكل كجم:", f"${result_mr['cost_per_kg']:.3f}")
                    m3.metric("💰 التكلفة للكمية المطلوبة:",
                              f"${result_mr['cost_per_kg'] * mr_volume:.2f}")
                    
                    # جدول المقارنة
                    st.markdown("#### 📊 جدول المقارنة (قياسي vs محسوب)")
                    compare_mr = []
                    for k in ["CP", "Fat", "Lactose"]:
                        sv = std_mr.get(k, 0)
                        cv = result_mr["actual"].get(k, 0)
                        diff = cv - sv
                        pct_diff = (diff / sv * 100) if sv else 0
                        status = "✅ مطابق" if abs(pct_diff) <= 5 else "⚠️ مقبول"
                        compare_mr.append({
                            "العنصر": k,
                            "المعيار القياسي": f"{sv:.2f}%",
                            "القيمة المحسوبة": f"{cv:.2f}%",
                            "الفرق": f"{diff:+.2f}%",
                            "التقييم": status,
                        })
                    st.dataframe(pd.DataFrame(compare_mr),
                                 use_container_width=True, hide_index=True)
                    
                    # PDF
                    try:
                        pdf_mr = pdf_generator.generate_comprehensive_report(
                            formula=result_mr["formula"],
                            target_dp=std_mr["CP"],
                            breed=mr_animal,
                            cost=result_mr["cost_per_100kg"],
                            city="مختبر بدائل الحليب",
                            local_cost=result_mr["cost_per_100kg"] * local_rate,
                            local_sym=local_sym,
                            computed_se=0.0,
                            requester_name=mr_requester,
                            animal_type=mr_animal,
                            production_stage="بديل حليب",
                            include_charts=True,
                            report_type="تركيب بديل حليب"
                        )
                        st.download_button(
                            "📥 تحميل تقرير PDF", pdf_mr,
                            file_name=f"TaworNology_Milk_{mr_animal}_{datetime.now():%Y%m%d}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"⚠️ خطأ PDF: {e}")
                else:
                    st.error(f"❌ {result_mr['message']}")


# ═══════════════════════════════════════════════════════════════════════════
# القسم 32: تبويب المختبر الذكي
# ═══════════════════════════════════════════════════════════════════════════

if "📷 المختبر الذكي" in tabs_titles:
    with tabs[tabs_titles.index("📷 المختبر الذكي")]:
        st.markdown('<div class="section-title">📷 المختبر الذكي — تحليل الصور</div>',
                    unsafe_allow_html=True)
        st.write("ارفع صورة تحتوي على نسب المكونات (مطبوعة أو مكتوبة)، وسيقوم النظام بتحليلها تلقائياً.")
        
        if not OCR_AVAILABLE:
            st.error("⚠️ مكتبة pytesseract غير مثبتة.\n\n"
                     "ثبّتها بالأمر:\n"
                     "`pip install pytesseract opencv-python-headless`\n\n"
                     "ثم ثبّت Tesseract OCR مع حزمة اللغة العربية `ara`.")
        else:
            uploaded = st.file_uploader(
                "📤 ارفع صورة (JPG / PNG):",
                type=["jpg", "jpeg", "png"],
                key="ocr_upload"
            )
            
            if uploaded:
                st.image(uploaded, caption="الصورة المرفوعة", use_container_width=True)
                
                ocr_requester = st.text_input("👤 اسم طالب التحليل:",
                    placeholder="مثال: مصنع الأعلاف", key="ocr_req")
                
                if st.button("🔍 تحليل الصورة واستخراج النسب",
                             type="primary", use_container_width=True):
                    with st.spinner("جاري التحليل..."):
                        ocr_result = extract_ingredients_from_image(uploaded.read())
                    
                    if ocr_result["success"]:
                        st.success(f"✅ تم استخراج {ocr_result['count']} مادة.")
                        
                        if ocr_result["ingredients"]:
                            df_ocr = pd.DataFrame([
                                {"المادة": k, "النسبة %": f"{v:.2f}%"}
                                for k, v in ocr_result["ingredients"].items()
                            ])
                            st.dataframe(df_ocr, use_container_width=True, hide_index=True)
                            
                            # التحليل الغذائي
                            nutrients_ocr = compute_formula_nutrients(ocr_result["ingredients"])
                            
                            st.markdown("#### 📊 التحليل الغذائي التلقائي:")
                            n1, n2, n3, n4 = st.columns(4)
                            n1.metric("CP", f"{nutrients_ocr['CP']:.2f}%")
                            n2.metric("DP", f"{nutrients_ocr['DP']:.2f}%")
                            n3.metric("SE", f"{nutrients_ocr['SE']:.2f}")
                            n4.metric("NDF", f"{nutrients_ocr['NDF']:.2f}%")
                            
                            # مقارنة
                            st.markdown("#### 📋 جدول المقارنة:")
                            ocr_animal = st.selectbox("اختر الحيوان للمقارنة:",
                                ["أغنام", "ماعز", "أبقار", "إبل", "دواجن لاحم",
                                 "سمان", "أسماك"], key="ocr_animal")
                            ocr_stage = st.text_input("المرحلة:", "تسمين", key="ocr_stage")
                            
                            std_ocr_key = get_standard_key(ocr_animal, ocr_stage)
                            std_ocr = NUTRIENT_STANDARDS.get(std_ocr_key, {})
                            
                            compare_ocr = []
                            for k, sv in std_ocr.items():
                                cv = nutrients_ocr.get(k, 0.0)
                                diff = cv - sv
                                pct_diff = (diff / sv * 100) if sv else 0
                                status = ("✅ مطابق" if abs(pct_diff) <= 5
                                         else ("⚠️ مقبول" if abs(pct_diff) <= 15
                                              else "❌ غير مطابق"))
                                compare_ocr.append({
                                    "العنصر": k,
                                    "القياسي": f"{sv:.2f}",
                                    "المحسوب": f"{cv:.2f}",
                                    "الفرق %": f"{pct_diff:+.1f}%",
                                    "التقييم": status,
                                })
                            st.dataframe(pd.DataFrame(compare_ocr),
                                         use_container_width=True, hide_index=True)
                            
                            # PDF
                            try:
                                pdf_ocr = pdf_generator.generate_comprehensive_report(
                                    formula=ocr_result["ingredients"],
                                    target_dp=nutrients_ocr["DP"],
                                    breed=f"{ocr_animal} — {ocr_stage}",
                                    cost=0.0,
                                    city="المختبر الذكي",
                                    local_cost=0.0,
                                    local_sym=local_sym,
                                    computed_se=nutrients_ocr["SE"],
                                    requester_name=ocr_requester,
                                    animal_type=ocr_animal,
                                    production_stage=ocr_stage,
                                    include_charts=True,
                                    report_type="تحليل صورة OCR"
                                )
                                st.download_button(
                                    "📥 تحميل تقرير التحليل PDF",
                                    pdf_ocr,
                                    file_name=f"TaworNology_OCR_{datetime.now():%Y%m%d_%H%M}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"⚠️ خطأ PDF: {e}")
                        
                        with st.expander("📝 النص الخام المستخرج من الصورة"):
                            st.text(ocr_result.get("raw_text", ""))
                    else:
                        st.error(f"❌ {ocr_result['message']}")


# ═══════════════════════════════════════════════════════════════════════════
# القسم 33: تبويب البورصة
# ═══════════════════════════════════════════════════════════════════════════

if "📊 البورصة" in tabs_titles:
    with tabs[tabs_titles.index("📊 البورصة")]:
        st.markdown('<div class="section-title">📊 بورصة تاور نولجي المركزية</div>',
                    unsafe_allow_html=True)
        
        if st.session_state["user_role"] == "specialist":
            st.warning("⚠️ حساب مختص: استعراض فقط. التعديل متاح للمالك.")
        
        bt1, bt2 = st.tabs(["🐄 الماشية", "🥩 المنتجات"])
        
        with bt1:
            st.markdown("#### أسعار الماشية والداجن")
            for animal, price in st.session_state["global_livestock_prices"].items():
                if st.session_state["user_role"] == "owner":
                    new_price = st.number_input(
                        f"تحديث: {animal}",
                        min_value=0.0, value=float(price), step=0.1,
                        key=f"livestock_{animal}"
                    )
                    st.session_state["global_livestock_prices"][animal] = new_price
                else:
                    st.markdown(f"▪️ {animal}: **${price:.2f}**")
        
        with bt2:
            st.markdown("#### أسعار المنتجات الحيوانية")
            for product, price in st.session_state["global_products_prices"].items():
                if st.session_state["user_role"] == "owner":
                    new_price = st.number_input(
                        f"تحديث: {product}",
                        min_value=0.0, value=float(price), step=0.05,
                        key=f"product_{product}"
                    )
                    st.session_state["global_products_prices"][product] = new_price
                else:
                    st.markdown(f"▪️ {product}: **${price:.2f}**")


# ═══════════════════════════════════════════════════════════════════════════
# القسم 34: تبويب المستودعات
# ═══════════════════════════════════════════════════════════════════════════

if "🏭 المستودعات" in tabs_titles:
    with tabs[tabs_titles.index("🏭 المستودعات")]:
        st.markdown('<div class="section-title">🏭 إدارة المستودعات الذكية</div>',
                    unsafe_allow_html=True)
        
        inventory = st.session_state["inventory"]
        
        # إحصائيات
        total_items = len(inventory)
        low_items = sum(1 for v in inventory.values()
                       if (v["quantity"] if isinstance(v, dict) else v) < 5)
        critical_items = sum(1 for v in inventory.values()
                            if (v["quantity"] if isinstance(v, dict) else v) <= 0)
        safe_items = total_items - low_items - critical_items
        
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("إجمالي المواد", total_items)
        s2.metric("مواد نفذت", critical_items)
        s3.metric("مواد منخفضة", low_items)
        s4.metric("مواد آمنة", safe_items)
        
        st.markdown("---")
        
        # قائمة المواد
        inv_cols = st.columns(3)
        for i, (ing_name, qty_data) in enumerate(list(inventory.items())[:60]):
            with inv_cols[i % 3]:
                qty = qty_data["quantity"] if isinstance(qty_data, dict) else qty_data
                
                if qty <= 0:
                    badge = f'🔴 <b>{qty:.1f} طن</b> — نفذ'
                elif qty < 5:
                    badge = f'🟡 <b>{qty:.1f} طن</b> — منخفض'
                else:
                    badge = f'🟢 <b>{qty:.1f} طن</b>'
                
                st.markdown(f"**{ing_name}** — {badge}", unsafe_allow_html=True)
                
                if st.session_state["user_role"] == "owner":
                    new_qty = st.number_input(
                        f"تحديث {ing_name}",
                        min_value=0.0, value=float(qty), step=1.0,
                        key=f"inv_{ing_name}",
                        label_visibility="collapsed"
                    )
                    if isinstance(inventory[ing_name], dict):
                        inventory[ing_name]["quantity"] = new_qty


# ═══════════════════════════════════════════════════════════════════════════
# القسم 35: تبويب الفواتير
# ═══════════════════════════════════════════════════════════════════════════

if "🧾 الفواتير" in tabs_titles:
    with tabs[tabs_titles.index("🧾 الفواتير")]:
        st.markdown('<div class="section-title">🧾 نظام الفواتير</div>',
                    unsafe_allow_html=True)
        
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            client_name = st.text_input("اسم العميل:", "مزرعة الأمل")
        with fc2:
            tons = st.number_input("الكمية (طن):", 0.1, 1000.0, 2.0, 0.5)
        with fc3:
            profit = st.number_input("هامش الربح ($/طن):", 0.0, 1000.0, 50.0)
        
        selling_price = st.session_state["computed_ton_cost"] + profit
        total_bill = selling_price * tons
        
        st.markdown(f"""
        <div class="price-card">
            <h4>🧾 فاتورة بيع</h4>
            <p><b>العميل:</b> {client_name}</p>
            <p><b>الكمية:</b> {tons} طن</p>
            <p><b>سعر الطن:</b> ${selling_price:.2f}</p>
            <p style="font-size:1.3rem; color:#1b5e20;"><b>الإجمالي:</b> ${total_bill:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state["active_formula"]:
            st.markdown("#### 🌾 مكونات الخلطة المباعة:")
            for ing, pct in st.session_state["active_formula"].items():
                required = (pct / 100) * tons
                st.markdown(f"▪️ {ing}: **{required:.3f}** طن ({pct:.1f}%)")


# ═══════════════════════════════════════════════════════════════════════════
# القسم 36: تبويب الديباجة
# ═══════════════════════════════════════════════════════════════════════════

if "🖨️ الديباجة" in tabs_titles:
    with tabs[tabs_titles.index("🖨️ الديباجة")]:
        st.markdown('<div class="section-title">🖨️ مصمم الديباجة على الشكائر</div>',
                    unsafe_allow_html=True)
        
        brand = st.text_input("اسم البراند:", APP_NAME)
        
        st.markdown(f"""
        <div style="border: 3px dashed #1b5e20; padding: 30px; border-radius: 15px;
        background: linear-gradient(135deg, #f1f8e9, #e8f5e9); direction: rtl; text-align: center;">
        <img src="{st.session_state['active_animal_img']}"
        style="width:100%; max-height:200px; object-fit:cover; border-radius:12px; margin-bottom:15px;">
        <h2 style="color: #1b5e20;">🌟 {brand} 🌟</h2>
        <h3 style="color: #c62828;">{SUPERVISOR} — {SUPERVISOR_TITLE}</h3>
        <p style="background:#e8f5e9; padding:12px; border-radius:8px; color:#1b5e20; font-weight:bold;">
        🎯 {st.session_state['active_stage_title']}<br>
        DP: {st.session_state['active_cp_tag']:.1f}% | SE: {st.session_state['active_se_tag']:.1f}
        </p>
        <small style="color:#666;">📅 {datetime.now():%Y-%m-%d}</small><br>
        <small style="color:#c62828;">🤲 {DUA_SHORT}</small>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# القسم 37: تبويب التحليلات
# ═══════════════════════════════════════════════════════════════════════════

if "📈 التحليلات" in tabs_titles:
    with tabs[tabs_titles.index("📈 التحليلات")]:
        st.markdown('<div class="section-title">📈 التحليلات المتقدمة</div>',
                    unsafe_allow_html=True)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("عدد الخلطات", "1,247")
        m2.metric("متوسط التكلفة", "$285")
        m3.metric("نسبة التوفير", "18%")
        m4.metric("رضا العملاء", "96%")
        
        st.markdown("---")
        
        if PLOTLY_AVAILABLE:
            st.subheader("📊 توزيع استخدام المواد")
            usage_data = pd.DataFrame({
                'المادة': ['ذرة', 'صويا', 'نخالة', 'أملاح', 'أخرى'],
                'نسبة الاستخدام': [45, 25, 15, 10, 5]
            })
            fig = px.pie(usage_data, values='نسبة الاستخدام',
                        names='المادة',
                        color_discrete_sequence=px.colors.sequential.Greens)
            st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# القسم 38: تبويب مزارع الدجاج (owner فقط)
# ═══════════════════════════════════════════════════════════════════════════

if "🐔 مزارع الدجاج" in tabs_titles:
    with tabs[tabs_titles.index("🐔 مزارع الدجاج")]:
        st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج اللاحم</div>',
                    unsafe_allow_html=True)
        st.info("📘 يمكنك تسجيل مزارع متعددة، وتدوين السجل الصحي اليومي، "
                "ومتابعة KPIs (ADG، FCR، EPEF).")
        
        # إضافة مزرعة
        farm_col1, farm_col2 = st.columns([0.4, 0.6])
        
        with farm_col1:
            st.markdown("#### 🏠 المزارع المسجلة")
            farm_names = list(st.session_state["broiler_farms"].keys())
            
            if farm_names:
                selected_farm = st.selectbox("اختر مزرعة:",
                    [""] + farm_names, key="farm_select")
            else:
                selected_farm = None
                st.info("لا توجد مزارع مسجلة بعد.")
            
            with st.expander("➕ إضافة مزرعة جديدة"):
                new_farm_name = st.text_input("اسم المزرعة:", key="new_farm_name")
                new_farm_owner = st.text_input("اسم المالك:", key="new_farm_owner")
                new_farm_phone = st.text_input("رقم واتساب:", WHATSAPP_NUMBER, key="new_farm_phone")
                
                if st.button("💾 حفظ المزرعة", key="save_farm"):
                    if new_farm_name:
                        st.session_state["broiler_farms"][new_farm_name] = {
                            "owner": new_farm_owner,
                            "owner_phone": new_farm_phone,
                            "daily_logs": [],
                            "health_log": [],
                            "current_data": {
                                "flock_age_days": 1,
                                "initial_birds": 1000,
                                "current_weight_kg": 0.045,
                                "initial_weight_kg": 0.045,
                                "total_feed_consumed_kg": 0.0,
                                "dead_birds": 0,
                                "culled_birds": 0,
                                "temperature_c": 33.0,
                                "humidity_percent": 65.0,
                                "notes": "",
                            },
                            "created_at": datetime.now().isoformat(),
                        }
                        st.success(f"✅ تمت إضافة مزرعة {new_farm_name}")
                        st.rerun()
        
        with farm_col2:
            if selected_farm and selected_farm in st.session_state["broiler_farms"]:
                farm = st.session_state["broiler_farms"][selected_farm]
                st.markdown(f"### 🏷️ {selected_farm} — المالك: {farm.get('owner', '-')}")
                
                cur = farm["current_data"]
                
                # بيانات اليوم
                with st.expander("📝 بيانات اليوم", expanded=True):
                    bf1, bf2 = st.columns(2)
                    with bf1:
                        age_d = st.number_input("عمر القطيع (يوم):",
                            min_value=1, max_value=60,
                            value=int(cur["flock_age_days"]), key="bf_age")
                        init_birds = st.number_input("عدد الكتاكيت:",
                            min_value=1, value=int(cur["initial_birds"]), key="bf_init")
                        cur_wt = st.number_input("الوزن الحالي (كجم):",
                            min_value=0.0, value=float(cur["current_weight_kg"]),
                            step=0.05, key="bf_wt")
                        feed_kg = st.number_input("العلف المستهلك (كجم):",
                            min_value=0.0, value=float(cur["total_feed_consumed_kg"]),
                            step=100.0, key="bf_feed")
                    with bf2:
                        dead = st.number_input("النافق:",
                            min_value=0, value=int(cur["dead_birds"]), key="bf_dead")
                        culled = st.number_input("المستبعدين:",
                            min_value=0, value=int(cur["culled_birds"]), key="bf_culled")
                        temp = st.number_input("الحرارة (°C):",
                            min_value=10.0, max_value=45.0,
                            value=float(cur["temperature_c"]), key="bf_temp")
                        hum = st.number_input("الرطوبة (%):",
                            min_value=20.0, max_value=90.0,
                            value=float(cur["humidity_percent"]), key="bf_hum")
                    
                    notes = st.text_area("ملاحظات:", value=cur.get("notes", ""), key="bf_notes")
                    
                    if st.button("💾 حفظ بيانات اليوم"):
                        farm["current_data"].update({
                            "flock_age_days": age_d,
                            "initial_birds": init_birds,
                            "current_weight_kg": cur_wt,
                            "total_feed_consumed_kg": feed_kg,
                            "dead_birds": dead,
                            "culled_birds": culled,
                            "temperature_c": temp,
                            "humidity_percent": hum,
                            "notes": notes,
                        })
                        st.success("✅ تم الحفظ")
                        st.rerun()
                
                # المؤشرات
                total_alive = init_birds - dead - culled
                gain_kg = total_alive * (cur_wt - cur["initial_weight_kg"])
                
                adg = BroilerFarmManager.calculate_adg(
                    cur_wt * 1000, cur["initial_weight_kg"] * 1000, age_d)
                fcr = (BroilerFarmManager.calculate_fcr(feed_kg, gain_kg)
                       if gain_kg > 0 else 0)
                mortality = BroilerFarmManager.calculate_mortality_rate(dead, init_birds)
                livability = BroilerFarmManager.calculate_livability(init_birds, dead)
                epef = BroilerFarmManager.calculate_epef(livability, cur_wt, age_d, fcr)
                
                st.markdown("#### 📊 المؤشرات الحالية:")
                k1, k2, k3 = st.columns(3)
                k1.metric("ADG (جم)", f"{adg:.1f}")
                k2.metric("FCR", f"{fcr:.2f}")
                k3.metric("EPEF", f"{epef:.0f}")
                
                k4, k5, k6 = st.columns(3)
                k4.metric("الحيوية", f"{livability:.1f}%")
                k5.metric("النفوق", f"{mortality:.2f}%")
                k6.metric("الوزن", f"{cur_wt:.3f} كجم")


# ═══════════════════════════════════════════════════════════════════════════
# القسم 39: تبويب التعليقات
# ═══════════════════════════════════════════════════════════════════════════

if "💬 التعليقات" in tabs_titles:
    with tabs[tabs_titles.index("💬 التعليقات")]:
        st.markdown('<div class="section-title">💬 قناة التواصل الفني</div>',
                    unsafe_allow_html=True)
        
        st.text_area("التعليقات الحالية:",
                     value=st.session_state["shared_comments"],
                     height=250, disabled=True)
        
        new_comment = st.text_area("📝 إضافة تعليق جديد:",
            placeholder="اكتب ملاحظتك أو توجيهك...")
        
        if st.button("➕ نشر التعليق"):
            if new_comment.strip():
                who = "المالك" if st.session_state["user_role"] == "owner" else "مختص"
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
                st.session_state["shared_comments"] += (
                    f"\n• [{who} {timestamp}]: {new_comment}"
                )
                st.success("✅ تم النشر!")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# القسم 40: تبويب المراجع العلمية
# ═══════════════════════════════════════════════════════════════════════════

with tabs[tabs_titles.index("📚 المراجع")]:
    st.markdown('<div class="section-title">📚 المراجع العلمية المعتمدة</div>',
                unsafe_allow_html=True)
    
    ref_cats = list(ScientificReferenceSystem.REFERENCES.keys())
    if ref_cats:
        sel_cat = st.selectbox("اختر التخصص:", ref_cats,
            format_func=lambda x: ScientificReferenceSystem.REFERENCES[x]["title"])
        
        cat_data = ScientificReferenceSystem.REFERENCES[sel_cat]
        st.markdown(f"### {cat_data['title']}")
        
        for ref in cat_data["references"]:
            with st.expander(f"📖 {ref['title']} ({ref['year']})"):
                st.markdown(f"**المؤلفون:** {ref['authors']}")
                st.markdown(f"**الناشر:** {ref['publisher']}")
                if 'edition' in ref:
                    st.markdown(f"**الطبعة:** {ref['edition']}")
                if 'isbn' in ref:
                    st.markdown(f"**ISBN:** {ref['isbn']}")
                st.markdown(f"**ملخص:** {ref['summary']}")
                st.markdown(f"**الرقم المرجعي:** `{ref['id']}`")
    
    st.markdown("---")
    st.markdown("### 🧠 بنك المعرفة السريع")
    user_q = st.text_input("اكتب سؤالك:")
    
    if user_q:
        ans = ScientificReferenceSystem.get_knowledge_answer(user_q)
        if ans:
            st.markdown(f"**الإجابة المبسطة:** {ans['simplified']}")
            st.markdown(f"**التفصيل:** {ans['answer']}")
            if ans['reference']:
                ref = ans['reference']
                st.markdown(f"**المصدر:** {ref['authors']} ({ref['year']}) — {ref['title']}")
        else:
            st.warning("لم أجد إجابة مباشرة.")


# ═══════════════════════════════════════════════════════════════════════════
# القسم 41: تبويب المساعدة
# ═══════════════════════════════════════════════════════════════════════════

with tabs[tabs_titles.index("💡 المساعدة")]:
    st.markdown('<div class="section-title">💡 المساعدة الذكية</div>',
                unsafe_allow_html=True)
    
    st.markdown(f"""
    ### 🌟 الأسئلة الشائعة
    
    **1. كيف أبدأ في تركيب علفة؟**
    - اختر الحيوان من التبويبات (8 قطاعات).
    - اعتمد الاختيار بـ ✅.
    - أدخل اسم طالب العلفة.
    - اختر المكونات المتاحة.
    - اضغط "تشغيل محرك التركيب".
    
    **2. ما هو البروتين المهضوم (DP)؟**
    هو الجزء من البروتين الذي يستطيع الحيوان امتصاصه فعلياً. أدق من البروتين الخام (CP).
    
    **3. ما هو معادل النشاء (SE)؟**
    مقياس لكمية الطاقة في العلف مقارنة بالنشاء النقي.
    
    **4. كيف أحلل صورة نسب المكونات؟**
    اذهب لتبويب "📷 المختبر الذكي" وارفع الصورة.
    
    **5. كيف أركّب بديل حليب؟**
    تبويب "🍼 بدائل الحليب" — اختر نوع الحيوان والمكونات.
    
    ---
    
    ### 🔧 الدعم الفني
    📧 **البريد:** abukram128@gmail.com
    📱 **واتساب:** {WHATSAPP_NUMBER}
    
    ---
    
    ### 🕌 دعاء
    {DUA_FULL}
    """)


# ═══════════════════════════════════════════════════════════════════════════
# القسم 42: تبويب الدليل
# ═══════════════════════════════════════════════════════════════════════════

with tabs[tabs_titles.index("📖 الدليل")]:
    st.markdown('<div class="section-title">📖 دليل المستخدم الشامل</div>',
                unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: #ffffff; padding: 30px; border-radius: 15px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08); direction: rtl; text-align: right;">
    
    <h2 style="color: #1b5e20;">🎯 الغرض من المنصة</h2>
    <p>{APP_NAME} — منصة ذكية لتركيب الأعلاف الحيوانية بأقل تكلفة مع الحفاظ
    على المعايير العالمية. تعتمد على محرك <b>Linear Programming</b>
    للوصول إلى تركيبة مثالية.</p>
    
    <h3 style="color: #1b5e20;">🚀 الميزات الرئيسية</h3>
    <ul>
    <li><b>8 قطاعات حيوانية:</b> أغنام، ماعز، أبقار، إبل، خيول، دواجن، سمان، أسماك.</li>
    <li><b>بدائل الحليب:</b> للعجول والحملان والجديان والإبل والأمهار.</li>
    <li><b>المختبر الذكي:</b> تحليل صور نسب المكونات بالـ OCR.</li>
    <li><b>تقارير PDF احترافية:</b> ترويسة + ختم رسمي + QR + تذييل بالدعاء.</li>
    <li><b>تصدير Excel:</b> جداول مقارنة بألوان ذكية.</li>
    <li><b>إدارة مزارع الدجاج:</b> KPIs (ADG، FCR، EPEF).</li>
    <li><b>المستودعات:</b> تتبع أرصدة المواد.</li>
    <li><b>الفواتير:</b> إصدار مع الخصم التلقائي.</li>
    </ul>
    
    <h3 style="color: #1b5e20;">🔑 أكواد الدخول</h3>
    <ul>
    <li><b>المالك:</b> <code>202687</code></li>
    <li><b>المختص:</b> <code>2020</code></li>
    <li><b>المربي:</b> <code>2026</code></li>
    </ul>
    
    <h3 style="color: #1b5e20;">📞 التواصل</h3>
    <p>📧 abukram128@gmail.com<br>📱 {WHATSAPP_NUMBER}</p>
    
    <hr style="border: 1px solid #d4af37; margin: 20px 0;">
    
    <div style="text-align: center; color: #1b5e20;">
    <p style="font-size: 1.2rem; font-weight: bold;">🤲 {DUA_SHORT} 🤲</p>
    <p style="font-style: italic;">{DUA_QURAN}</p>
    </div>
    
    </div>
    """)


# ═══════════════════════════════════════════════════════════════════════════
# القسم 43: التذييل الثابت
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(
    f'<div class="mini-signature">🌾 {APP_NAME} | {SUPERVISOR} © 2026</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="dua-fixed-banner">🤲 {DUA_SHORT} 🤲</div>',
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# نهاية الملف — End of File
# ═══════════════════════════════════════════════════════════════════════════
