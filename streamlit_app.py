# ============================================================================
# تاور نولجي TAWOR NOLOGY — الإصدار 10.3 النهائي المُدمَج
# إشراف: م. عبدالقادر إسماعيل تاور
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
# الميزات: 18 زيتاً + 14 مركز + مختبر + حظائر 3D + قياس الوزن + PDF
# ============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import json, os, base64, time, re, io, sqlite3, hashlib, secrets, warnings
import urllib.parse, urllib.request, smtplib
from datetime import datetime, timedelta, date
from functools import lru_cache
from typing import Optional
from dataclasses import dataclass

warnings.filterwarnings('ignore')

try:
    from scipy.optimize import linprog
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

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
    from matplotlib.patches import Circle, Wedge
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import pytesseract
    import cv2
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

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
                                     HRFlowable, PageBreak)
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
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ═══ القسم 1: الدعاء ═══
DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي ابتسام"
DUA_FULL = "رحم الله والدي إسماعيل تاور وأختي ابتسام، وأسكنهما فسيح جناته، وجعل قبرهما روضة من رياض الجنة"
DUA_QURAN = "﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾"
DUA_VERSE = "﴿ وَقُل رَّبِّ ارْحَمْهُمَا كَمَا رَبَّيَانِي صَغِيرًا ﴾"
DUA_VISITOR_BANNER = """
🕌 <b>إلى زوارنا الكرام:</b><br>
هذه المنصة صدقةٌ جارية عن <b>والدي إسماعيل تاور</b> و<b>أختي ابتسام</b>.<br>
نسألكم بظهر الغيب أن تشاركونا الدعاء لهما. 🤲
"""


# ═══ القسم 2: الإعدادات العامة ═══
APP_NAME = "تاور نولجي Tawor Nology"
APP_TAGLINE = "للإنتاج الحيواني وتغذية الحيوان"
SUPERVISOR = "م. عبدالقادر إسماعيل تاور"
SUPERVISOR_TITLE = "اختصاصي تغذية الحيوان"
OWNER_CODE = "202687"
PLATFORM_URL = "https://tawor-nology.streamlit.app"
WHATSAPP_NUMBER = "+249123533489"
OWNER_EMAIL = "abukram128@gmail.com"
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG"]
LOGO_OPTIONS = ["logo.png", "logo.jpg"]

st.set_page_config(
    page_title=f"{APP_NAME} | {APP_TAGLINE}",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ═══ القسم 3: الخطوط العربية ═══
FONT_DIR = "fonts"
os.makedirs(FONT_DIR, exist_ok=True)

ARABIC_FONT_URLS = [
    ("https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf", "Amiri-Regular.ttf"),
    ("https://github.com/google/fonts/raw/main/ofl/cairo/Cairo%5Bslnt%2Cwght%5D.ttf", "Cairo-Regular.ttf"),
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
        paths = [os.path.join(FONT_DIR, "Amiri-Regular.ttf"),
                 "Amiri-Regular.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        for p in paths:
            if os.path.exists(p):
                if self._register(p): return
        for url, fn in ARABIC_FONT_URLS:
            try:
                target = os.path.join(FONT_DIR, fn)
                if not os.path.exists(target):
                    urllib.request.urlretrieve(url, target)
                if self._register(target): return
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
        if text is None or text == "": return ""
        text = str(text)
        if not ARABIC_AVAILABLE: return text
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped, base_dir='R')
        except Exception:
            return text


arp = ArabicProcessor()
def ar(text): return arp.fix(text)


# ═══ القسم 4: مكتبة الأعلاف الشاملة ═══
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
        "أمباز الفول السوداني": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5, "Ca": 0.20, "P": 0.65},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0, "Ca": 0.35, "P": 0.65},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2, "Ca": 0.35, "P": 0.65},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5, "Ca": 0.40, "P": 1.00},
        "كسب عباد الشمس 32%": {"CP": 32.0, "DC": 0.72, "SE": 38.0, "NDF": 42.0, "ADF": 28.0, "EE": 2.0, "ASH": 7.0, "Ca": 0.42, "P": 0.95},
        "كسب بذور القطن": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5, "Ca": 0.20, "P": 1.10},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8, "Ca": 0.35, "P": 0.85},
        "كسب السمسم": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5, "Ca": 2.00, "P": 1.20},
        "كسب جلوتين 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5, "Ca": 0.15, "P": 0.50},
        "كسب جلوتين 40%": {"CP": 40.0, "DC": 0.88, "SE": 72.0, "NDF": 15.0, "ADF": 8.0, "EE": 3.0, "ASH": 5.0, "Ca": 0.18, "P": 0.55},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5, "Ca": 0.30, "P": 0.55},
        "كسب بذور العنب": {"CP": 12.0, "DC": 0.55, "SE": 30.0, "NDF": 45.0, "ADF": 32.0, "EE": 7.5, "ASH": 6.0, "Ca": 0.25, "P": 0.40},
        "كسب بذور القرطم": {"CP": 24.0, "DC": 0.70, "SE": 45.0, "NDF": 35.0, "ADF": 22.0, "EE": 2.0, "ASH": 6.0, "Ca": 0.35, "P": 0.75},
        "كسب الكانولا": {"CP": 36.0, "DC": 0.82, "SE": 60.0, "NDF": 28.0, "ADF": 18.0, "EE": 3.5, "ASH": 6.5, "Ca": 0.65, "P": 1.10},
        "كسب الأفوكادو": {"CP": 18.0, "DC": 0.65, "SE": 50.0, "NDF": 40.0, "ADF": 28.0, "EE": 8.0, "ASH": 5.5, "Ca": 0.30, "P": 0.45},
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5, "Ca": 0.12, "P": 1.10},
        "نخالة ذرة": {"CP": 9.5, "DC": 0.65, "SE": 40.0, "NDF": 40.0, "ADF": 15.0, "EE": 4.0, "ASH": 2.0, "Ca": 0.10, "P": 0.75},
        "البرسيم الجاف": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5, "Ca": 1.50, "P": 0.25},
        "برسيم حجازي": {"CP": 18.0, "DC": 0.62, "SE": 38.0, "NDF": 40.0, "ADF": 30.0, "EE": 2.2, "ASH": 11.0, "Ca": 1.60, "P": 0.26},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5, "Ca": 0.70, "P": 0.05},
        "تبن قمح": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.30, "P": 0.08},
        "تبن فول": {"CP": 4.5, "DC": 0.40, "SE": 22.0, "NDF": 68.0, "ADF": 42.0, "EE": 1.2, "ASH": 7.5, "Ca": 0.35, "P": 0.10},
        "قشر فول سوداني": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5, "Ca": 0.25, "P": 0.10},
        "سرسة الأرز": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5, "Ca": 0.15, "P": 0.08},
        "قش أرز": {"CP": 3.5, "DC": 0.30, "SE": 15.0, "NDF": 70.0, "ADF": 45.0, "EE": 1.5, "ASH": 12.0, "Ca": 0.20, "P": 0.06},
        "مخلفات النخيل": {"CP": 6.5, "DC": 0.70, "SE": 60.0, "NDF": 25.0, "ADF": 15.0, "EE": 5.0, "ASH": 3.5, "Ca": 0.15, "P": 0.15},
        "قشور الفول السوداني": {"CP": 6.5, "DC": 0.40, "SE": 22.0, "NDF": 58.0, "ADF": 38.0, "EE": 2.5, "ASH": 4.0, "Ca": 0.20, "P": 0.12},
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5, "Ca": 5.50, "P": 3.20},
        "مسحوق أسماك 72%": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5, "Ca": 4.80, "P": 2.80},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5, "Ca": 9.00, "P": 4.50},
        "مسحوق الدم": {"CP": 80.0, "DC": 0.65, "SE": 55.0, "NDF": 1.0, "ADF": 0.5, "EE": 1.5, "ASH": 6.0, "Ca": 0.30, "P": 0.30},
        "مسحوق ريش": {"CP": 82.0, "DC": 0.70, "SE": 60.0, "NDF": 1.5, "ADF": 1.0, "EE": 3.0, "ASH": 4.0, "Ca": 0.25, "P": 0.35},
        "مسحوق مخلفات دواجن": {"CP": 55.0, "DC": 0.78, "SE": 58.0, "NDF": 5.0, "ADF": 3.0, "EE": 12.0, "ASH": 15.0, "Ca": 3.00, "P": 1.80},
        "مركزات دواجن": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5, "Ca": 2.50, "P": 1.20},
        "مركزات مواشي": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5, "Ca": 3.00, "P": 1.50},
        "بروتين بلازما الدم": {"CP": 78.0, "DC": 0.90, "SE": 62.0, "NDF": 0.5, "ADF": 0.0, "EE": 2.0, "ASH": 10.0, "Ca": 0.15, "P": 0.20},
    },
    "🌿 الأعلاف الخضراء المائية": {
        "أزولا مجففة": {"CP": 24.0, "DC": 0.65, "SE": 45.0, "NDF": 38.0, "ADF": 25.0, "EE": 3.5, "ASH": 18.0, "Ca": 2.00, "P": 0.60},
        "سبيرولينا": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 5.0, "ADF": 3.0, "EE": 6.0, "ASH": 10.0, "Ca": 1.20, "P": 0.90},
        "كلوريلا": {"CP": 55.0, "DC": 0.80, "SE": 60.0, "NDF": 6.0, "ADF": 3.5, "EE": 8.0, "ASH": 12.0, "Ca": 0.50, "P": 1.20},
        "طحالب بحرية": {"CP": 15.0, "DC": 0.60, "SE": 30.0, "NDF": 25.0, "ADF": 15.0, "EE": 2.0, "ASH": 30.0, "Ca": 1.50, "P": 0.30},
    },
    "🌰 الزيوت النباتية والحيوانية": {
        "زيت ذرة": {"CP": 0.0, "DC": 0.0, "SE": 220.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                    "desc": "طاقة عالية (9000 kcal/kg)، غني بأوميغا 6", "max_poultry": 6.0, "max_ruminant": 5.0,
                    "max_fish": 10.0, "max_horse": 8.0, "source": "NRC 2012"},
        "زيت فول الصويا": {"CP": 0.0, "DC": 0.0, "SE": 215.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                           "desc": "أشهر زيوت الأعلاف، متوازن، 8800 kcal/kg", "max_poultry": 8.0, "max_ruminant": 5.0,
                           "max_fish": 12.0, "max_horse": 10.0, "source": "Ross 308 / NRC 2012"},
        "زيت عباد الشمس": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                           "desc": "غني بأوميغا 6، رخيص نسبياً", "max_poultry": 6.0, "max_ruminant": 4.0,
                           "max_fish": 8.0, "max_horse": 8.0, "source": "NRC 2007"},
        "زيت بذرة القطن": {"CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                           "desc": "يحتوي جوسيبول (يجب معادلة)", "max_poultry": 3.0, "max_ruminant": 5.0,
                           "max_fish": 6.0, "max_horse": 5.0, "source": "NRC 2012"},
        "زيت الكتان": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                       "desc": "غني جداً بأوميغا 3، ممتاز للخيول", "max_poultry": 3.0, "max_ruminant": 3.0,
                       "max_fish": 6.0, "max_horse": 8.0, "source": "NRC 2007 Horses"},
        "زيت جوز الهند": {"CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                          "desc": "دهون متوسطة السلسلة MCT، مضاد بكتيري", "max_poultry": 5.0, "max_ruminant": 3.0,
                          "max_fish": 8.0, "max_horse": 6.0, "source": "NRC 2012"},
        "زيت النخيل": {"CP": 0.0, "DC": 0.0, "SE": 215.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                       "desc": "طاقة عالية، مقاوم للأكسدة، 8700 kcal/kg", "max_poultry": 6.0, "max_ruminant": 5.0,
                       "max_fish": 8.0, "max_horse": 8.0, "source": "NRC 2012"},
        "زيت الكانولا": {"CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                         "desc": "متوازن أوميغا 3 و6", "max_poultry": 5.0, "max_ruminant": 5.0,
                         "max_fish": 8.0, "max_horse": 6.0, "source": "NRC 2012"},
        "زيت السمسم": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                       "desc": "غني بمضادات الأكسدة الطبيعية", "max_poultry": 4.0, "max_ruminant": 3.0,
                       "max_fish": 6.0, "max_horse": 5.0, "source": "NRC 2007"},
        "زيت الزيتون": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                        "desc": "غني بأوميغا 9، مضاد أكسدة قوي", "max_poultry": 4.0, "max_ruminant": 4.0,
                        "max_fish": 5.0, "max_horse": 5.0, "source": "INRA 2018"},
        "زيت الأفوكادو": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                          "desc": "غني بفيتامين E", "max_poultry": 3.0, "max_ruminant": 3.0,
                          "max_fish": 4.0, "max_horse": 4.0, "source": "NRC 2012"},
        "زيت القرطم": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                       "desc": "غني جداً بأوميغا 6 (75%)", "max_poultry": 4.0, "max_ruminant": 3.0,
                       "max_fish": 5.0, "max_horse": 5.0, "source": "NRC 2012"},
        "زيت الفول السوداني": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                               "desc": "طاقة عالية جداً، 8900 kcal/kg", "max_poultry": 5.0, "max_ruminant": 4.0,
                               "max_fish": 6.0, "max_horse": 6.0, "source": "NRC 2012"},
        "شحم حيواني (Tallow)": {"CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                                "desc": "طاقة عالية (9500 kcal/kg)", "max_poultry": 6.0, "max_ruminant": 5.0,
                                "max_fish": 6.0, "max_horse": 8.0, "source": "NRC 2012"},
        "سمن حيواني (Lard)": {"CP": 0.0, "DC": 0.0, "SE": 225.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                              "desc": "شحم الخنزير، يجب تجنبه للحيوانات الحلال", "max_poultry": 5.0, "max_ruminant": 0.0,
                              "max_fish": 5.0, "max_horse": 6.0, "source": "NRC 2012"},
        "دهن الدجاج": {"CP": 0.0, "DC": 0.0, "SE": 225.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                       "desc": "شحم الدواجن المعاد تدويره، اقتصادي", "max_poultry": 6.0, "max_ruminant": 0.0,
                       "max_fish": 5.0, "max_horse": 6.0, "source": "NRC 2012"},
        "زيت السمك (Fish Oil)": {"CP": 0.0, "DC": 0.0, "SE": 235.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0,
                                 "desc": "غني بأوميغا 3 EPA/DHA، ممتاز للأسماك", "max_poultry": 2.0, "max_ruminant": 2.0,
                                 "max_fish": 8.0, "max_horse": 3.0, "source": "NRC Fish Nutrition"},
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0},
        "ليسين سلفات": {"CP": 79.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0},
        "ميثيونين نقي": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3, "Ca": 0.0, "P": 0.0},
        "ميثيونين هيدروكسي": {"CP": 88.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0},
        "ثريونين نقي": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0},
        "تريبتوفان نقي": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0},
        "فالين نقي": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0},
        "أرجينين": {"CP": 98.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0},
        "هيستيدين": {"CP": 96.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0},
        "إيزوليوسين": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0},
        "ليوسين": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0},
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 8.0},
        "بريمكس بياض": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 22.0, "P": 7.0},
        "بريمكس أبقار": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0},
        "بريمكس مجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 9.0},
        "بريمكس خيول": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 8.0},
        "بريمكس إبل": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0},
        "بريمكس أسماك": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 7.0},
        "إنزيم فايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0, "Ca": 0.0, "P": 0.0},
        "إنزيم NSP": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0, "Ca": 0.0, "P": 0.0},
        "إنزيم بروتييز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 2.0, "Ca": 0.0, "P": 0.0},
        "إنزيم أميليز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0, "Ca": 0.0, "P": 0.0},
        "كبريتات الحديدوز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0, "Ca": 0.0, "P": 0.0},
        "مستخلص الخمائر MOS": {"CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.10, "P": 0.20},
        "خمائر حية": {"CP": 45.0, "DC": 0.75, "SE": 30.0, "NDF": 8.0, "ADF": 4.0, "EE": 1.0, "ASH": 8.0, "Ca": 0.15, "P": 1.20},
        "بروبيوتيك": {"CP": 15.0, "DC": 0.60, "SE": 20.0, "NDF": 5.0, "ADF": 3.0, "EE": 2.0, "ASH": 15.0, "Ca": 0.30, "P": 0.50},
        "بريبيوتيك FOS": {"CP": 0.0, "DC": 0.0, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 2.0, "Ca": 0.0, "P": 0.0},
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 38.0, "P": 0.0},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5, "Ca": 23.0, "P": 18.0},
        "فوسفات أحادي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 17.0, "P": 22.0},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9, "Ca": 0.0, "P": 0.0},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 0.0, "P": 0.0},
        "أكسيد المغنيسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 0.0, "P": 0.0},
        "كبريتات المغنيسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0, "Ca": 0.0, "P": 0.0},
        "يوريا علفية": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0, "Ca": 0.0, "P": 0.0},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Ca": 0.0, "P": 0.0},
        "مضاد أكسدة BHT": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0},
        "مضاد حيوي وقائي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0},
        "كولين كلوريد": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0},
    },
    "🏭 المركزات التجارية": {
        "مركز تسمين 30% بروتين": {
            "CP": 30.0, "DC": 0.82, "SE": 55.0, "NDF": 15.0, "ADF": 8.0,
            "EE": 3.0, "ASH": 12.0, "Ca": 2.50, "P": 1.20,
            "desc": "مركز تجاري لتسمين العجول والحملان", "source": "NRC 2001"},
        "مركز تسمين 35% بروتين": {
            "CP": 35.0, "DC": 0.85, "SE": 58.0, "NDF": 12.0, "ADF": 6.5,
            "EE": 3.5, "ASH": 13.0, "Ca": 2.80, "P": 1.30,
            "desc": "تركيز بروتين متوسط لتسمين مكثف", "source": "NRC 2001"},
        "مركز تسمين 40% بروتين": {
            "CP": 40.0, "DC": 0.87, "SE": 60.0, "NDF": 10.0, "ADF": 5.0,
            "EE": 4.0, "ASH": 14.0, "Ca": 3.00, "P": 1.40,
            "desc": "تركيز عالٍ لتسمين سريع", "source": "NRC 2001"},
        "مركز حلابة 30% بروتين": {
            "CP": 30.0, "DC": 0.82, "SE": 60.0, "NDF": 13.0, "ADF": 7.0,
            "EE": 3.5, "ASH": 15.0, "Ca": 3.50, "P": 1.50,
            "desc": "مركز أبقار حلابة — إنتاج متوسط", "source": "NRC 2001"},
        "مركز حلابة 35% بروتين": {
            "CP": 35.0, "DC": 0.85, "SE": 62.0, "NDF": 11.0, "ADF": 6.0,
            "EE": 4.0, "ASH": 16.0, "Ca": 3.80, "P": 1.60,
            "desc": "مركز أبقار حلابة — إنتاج عالٍ", "source": "NRC 2001"},
        "مركز أغنام 30% بروتين": {
            "CP": 30.0, "DC": 0.80, "SE": 55.0, "NDF": 14.0, "ADF": 8.0,
            "EE": 3.0, "ASH": 14.0, "Ca": 3.00, "P": 1.30,
            "desc": "مركز أغنام متعدد الأغراض", "source": "NRC 2007"},
        "مركز أغنام 35% بروتين": {
            "CP": 35.0, "DC": 0.82, "SE": 58.0, "NDF": 12.0, "ADF": 7.0,
            "EE": 3.5, "ASH": 15.0, "Ca": 3.20, "P": 1.40,
            "desc": "مركز أغنام للمراضع والتسمين", "source": "NRC 2007"},
        "مركز ماعز 30% بروتين": {
            "CP": 30.0, "DC": 0.80, "SE": 55.0, "NDF": 14.0, "ADF": 8.0,
            "EE": 3.0, "ASH": 14.0, "Ca": 3.00, "P": 1.30,
            "desc": "مركز ماعز متعدد الأغراض", "source": "NRC 2007"},
        "مركز دواجن بادئ 40%": {
            "CP": 40.0, "DC": 0.88, "SE": 65.0, "NDF": 8.0, "ADF": 4.0,
            "EE": 4.5, "ASH": 12.0, "Ca": 2.50, "P": 1.20,
            "desc": "مركز بادئ للدواجن اللاحم (1-10 يوم)", "source": "Ross 308"},
        "مركز دواجن نامي 35%": {
            "CP": 35.0, "DC": 0.87, "SE": 62.0, "NDF": 9.0, "ADF": 4.5,
            "EE": 4.0, "ASH": 13.0, "Ca": 2.80, "P": 1.30,
            "desc": "مركز نامي للدواجن اللاحم", "source": "Ross 308"},
        "مركز دواجن ناهي 30%": {
            "CP": 30.0, "DC": 0.86, "SE": 60.0, "NDF": 10.0, "ADF": 5.0,
            "EE": 3.5, "ASH": 14.0, "Ca": 3.00, "P": 1.40,
            "desc": "مركز ناهي للدواجن اللاحم", "source": "Ross 308"},
        "مركز بياض 30% بروتين": {
            "CP": 30.0, "DC": 0.85, "SE": 58.0, "NDF": 10.0, "ADF": 5.5,
            "EE": 3.5, "ASH": 18.0, "Ca": 5.50, "P": 1.50,
            "desc": "مركز دواجن بياض (كالسيوم عالٍ)", "source": "NRC 1994"},
        "مركز إبل 30% بروتين": {
            "CP": 30.0, "DC": 0.78, "SE": 52.0, "NDF": 18.0, "ADF": 10.0,
            "EE": 3.0, "ASH": 15.0, "Ca": 3.20, "P": 1.40,
            "desc": "مركز خاص بالإبل — بروتين متوسط", "source": "FAO 2010"},
        "مركز أسماك 35% بروتين": {
            "CP": 35.0, "DC": 0.88, "SE": 62.0, "NDF": 6.0, "ADF": 3.0,
            "EE": 5.0, "ASH": 13.0, "Ca": 2.50, "P": 1.50,
            "desc": "مركز أسماك مائية", "source": "NRC Fish Nutrition"},
    },
}


# ═══ القسم 5: معايير الزيوت ═══
MAX_OIL_PERCENTAGE = {
    "دواجن_بادي": {"max": 8.0, "optimal": 5.0, "source": "Ross 308 2020"},
    "دواجن_نامي": {"max": 7.0, "optimal": 4.5, "source": "Ross 308 2020"},
    "دواجن_ناهي": {"max": 7.0, "optimal": 4.0, "source": "Ross 308 2020"},
    "دواجن_بياض": {"max": 5.0, "optimal": 2.5, "source": "NRC 1994"},
    "سمان_بادي": {"max": 6.0, "optimal": 4.0, "source": "NRC Quail"},
    "سمان_بياض": {"max": 5.0, "optimal": 2.5, "source": "NRC Quail"},
    "أبقار_حليب_عالي": {"max": 6.0, "optimal": 4.0, "source": "NRC 2001"},
    "أبقار_حليب_متوسط": {"max": 5.0, "optimal": 3.5, "source": "NRC 2001"},
    "أبقار_حليب_منخفض": {"max": 5.0, "optimal": 3.0, "source": "NRC 2001"},
    "أبقار_تسمين_مكثف": {"max": 6.0, "optimal": 4.5, "source": "NRC 2001"},
    "أبقار_تسمين_عادي": {"max": 5.0, "optimal": 3.5, "source": "NRC 2001"},
    "أبقار_حمل_أخير": {"max": 5.0, "optimal": 3.5, "source": "NRC 2001"},
    "أبقار_صيانة": {"max": 4.0, "optimal": 2.5, "source": "NRC 2001"},
    "أغنام_تسمين_مكثف": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "أغنام_تسمين_عادي": {"max": 4.5, "optimal": 3.0, "source": "NRC 2007"},
    "أغنام_حملان_تيد": {"max": 4.5, "optimal": 3.0, "source": "NRC 2007"},
    "أغنام_مرضعات": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "أغنام_حامل_أخير": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "أغنام_حامل_متوسط": {"max": 4.5, "optimal": 3.0, "source": "NRC 2007"},
    "أغنام_صيانة": {"max": 3.5, "optimal": 2.0, "source": "NRC 2007"},
    "ماعز_تسمين_جديان": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "ماعز_تيوس": {"max": 4.5, "optimal": 3.0, "source": "NRC 2007"},
    "ماعز_حلابة_عالي": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "ماعز_حلابة_متوسط": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "ماعز_حامل_أخير": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "ماعز_صيانة": {"max": 3.5, "optimal": 2.0, "source": "NRC 2007"},
    "إبل_نمو": {"max": 5.0, "optimal": 3.5, "source": "FAO 2010"},
    "إبل_تسمين": {"max": 6.0, "optimal": 4.0, "source": "FAO 2010"},
    "إبل_حليب": {"max": 5.0, "optimal": 3.5, "source": "FAO 2010"},
    "إبل_سباق": {"max": 8.0, "optimal": 6.0, "source": "FAO 2010"},
    "إبل_صيانة": {"max": 3.5, "optimal": 2.0, "source": "FAO 2010"},
    "خيول_رياضة_مكثف": {"max": 10.0, "optimal": 7.0, "source": "NRC 2007 Horses"},
    "خيول_رياضة_عادي": {"max": 8.0, "optimal": 5.0, "source": "NRC 2007 Horses"},
    "خيول_نمو_أمهار": {"max": 8.0, "optimal": 5.0, "source": "NRC 2007 Horses"},
    "خيول_مرضعات": {"max": 8.0, "optimal": 5.5, "source": "NRC 2007 Horses"},
    "خيول_صيانة": {"max": 5.0, "optimal": 3.0, "source": "NRC 2007 Horses"},
    "أسماك_بادئ": {"max": 15.0, "optimal": 10.0, "source": "NRC Fish Nutrition"},
    "أسماك_نمو": {"max": 12.0, "optimal": 8.0, "source": "NRC Fish Nutrition"},
    "أسماك_تسمين": {"max": 12.0, "optimal": 8.0, "source": "NRC Fish Nutrition"},
}

OIL_CATEGORIES = {
    "زيوت نباتية غنية بأوميغا 6": ["زيت ذرة", "زيت عباد الشمس", "زيت القرطم", "زيت فول الصويا"],
    "زيوت نباتية غنية بأوميغا 3": ["زيت الكتان", "زيت الكانولا", "زيت السمك (Fish Oil)"],
    "زيوت نباتية متوازنة": ["زيت النخيل", "زيت جوز الهند", "زيت الزيتون",
                            "زيت السمسم", "زيت الفول السوداني", "زيت الأفوكادو"],
    "دهون حيوانية": ["شحم حيواني (Tallow)", "سمن حيواني (Lard)", "دهن الدجاج"],
}


def get_oil_standard(standard_key: str) -> dict:
    return MAX_OIL_PERCENTAGE.get(standard_key,
        {"max": 5.0, "optimal": 3.0, "source": "معيار عام — NRC"})


def get_oil_ingredients() -> dict:
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت النباتية والحيوانية", {})


def get_concentrates() -> dict:
    return BIG_FEEDS_LIBRARY.get("🏭 المركزات التجارية", {})


# ═══ القسم 6: الاحتياجات المتخصصة ═══
@dataclass
class AnimalRequirement:
    DP: float; CP: float; SE: float; NDF: float; ADF: float
    EE: float; ASH: float; Ca: float; P: float
    name_ar: str = ""; note: str = ""


def get_cattle_requirements(production_type, milk_yield=20.0, weight_kg=500.0):
    if production_type == "حليب_عالي":
        dp = 12.5 + (milk_yield * 0.30); cp = dp / 0.70
        return AnimalRequirement(round(dp,2), round(cp,2), round(60+milk_yield*0.35,1),
            30.0, 19.0, 5.5, 8.0, round(0.55+milk_yield*0.003,3),
            round(0.33+milk_yield*0.0015,3), "أبقار حلابة عالية", f"إنتاج {milk_yield} كجم")
    elif production_type == "حليب_متوسط":
        dp = 11.0 + (milk_yield * 0.25); cp = dp / 0.72
        return AnimalRequirement(round(dp,2), round(cp,2), round(55+milk_yield*0.30,1),
            33.0, 21.0, 4.5, 8.0, round(0.50+milk_yield*0.0025,3),
            round(0.30+milk_yield*0.0012,3), "أبقار حلابة متوسطة", f"إنتاج {milk_yield}")
    elif production_type == "حليب_منخفض":
        dp = 9.5 + (milk_yield * 0.20); cp = dp / 0.75
        return AnimalRequirement(round(dp,2), round(cp,2), round(50+milk_yield*0.25,1),
            38.0, 24.0, 4.0, 8.5, round(0.45+milk_yield*0.002,3),
            round(0.28+milk_yield*0.001,3), "أبقار حلابة منخفضة", f"إنتاج {milk_yield}")
    elif production_type == "تسمين_مكثف":
        return AnimalRequirement(11.5, 14.5, 72.0, 32.0, 20.0, 4.5, 7.5, 0.65, 0.38,
            "تسمين عجول مكثف", "ADG >1.3")
    elif production_type == "تسمين_عادي":
        return AnimalRequirement(9.5, 12.0, 65.0, 38.0, 24.0, 4.0, 7.5, 0.55, 0.32,
            "تسمين عجول عادي", "ADG ~0.8")
    elif production_type == "حمل_أخير":
        return AnimalRequirement(11.5, 14.5, 67.0, 35.0, 22.0, 4.2, 8.0, 0.70, 0.42,
            "حمل آخر", "شهر 7-9")
    else:
        return AnimalRequirement(7.5, 10.0, 53.0, 45.0, 28.0, 3.0, 8.5, 0.42, 0.26,
            "أبقار صيانة", "بدون إنتاج")


def get_sheep_requirements(production_type, is_male=True, weight_kg=50.0, litter_size=1):
    if is_male:
        if production_type == "تسمين_مكثف":
            return AnimalRequirement(11.5, 14.5, 64.0, 28.0, 17.0, 4.0, 8.0, 0.65, 0.36,
                "تسمين حملان مكثف", "ADG >250 جم")
        elif production_type == "تسمين_عادي":
            return AnimalRequirement(9.5, 12.0, 59.0, 33.0, 21.0, 3.6, 8.0, 0.55, 0.32,
                "تسمين حملان عادي", "ADG ~180 جم")
        else:
            return AnimalRequirement(8.5, 11.0, 55.0, 38.0, 24.0, 3.2, 8.5, 0.50, 0.30,
                "حملان تيد", "تسمين نهائي")
    else:
        if production_type == "مرضعات":
            dp = 10.5 + (litter_size - 1) * 1.5; cp = dp / 0.72
            return AnimalRequirement(round(dp,2), round(cp,2),
                round(60+(litter_size-1)*5,1), 30.0, 19.0, 4.5, 8.5,
                round(0.65+(litter_size-1)*0.10,3), round(0.38+(litter_size-1)*0.05,3),
                f"نعاج مرضعات ({litter_size})", "إنتاج حليب مرتفع")
        elif production_type == "حامل_أخير":
            return AnimalRequirement(10.5, 13.5, 62.0, 32.0, 20.0, 3.8, 8.0, 0.60, 0.35,
                "نعاج حامل (4-5)", "تغذية جنين")
        elif production_type == "حامل_متوسط":
            return AnimalRequirement(8.5, 11.0, 55.0, 38.0, 24.0, 3.4, 8.0, 0.50, 0.30,
                "نعاج حامل (1-3)", "نمو مبكر")
        else:
            return AnimalRequirement(7.2, 9.5, 48.0, 45.0, 28.0, 3.0, 8.5, 0.42, 0.26,
                "نعاج صيانة", "بدون إنتاج")


def get_goat_requirements(production_type, is_male=True, milk_yield=2.0):
    if is_male:
        if production_type == "تسمين_جديان":
            return AnimalRequirement(11.0, 14.0, 62.0, 30.0, 19.0, 3.8, 8.0, 0.62, 0.34,
                "تسمين جديان", "نمو سريع")
        else:
            return AnimalRequirement(9.0, 11.5, 57.0, 36.0, 22.0, 3.5, 8.0, 0.55, 0.30,
                "تيوس تسمين", "تسمين نهائي")
    else:
        if production_type == "حلابة_عالي":
            dp = 11.5 + (milk_yield * 0.45); cp = dp / 0.70
            return AnimalRequirement(round(dp,2), round(cp,2),
                round(58+milk_yield*0.45,1), 29.0, 18.0, 4.5, 8.5,
                round(0.60+milk_yield*0.008,3), round(0.35+milk_yield*0.004,3),
                f"عنزات حلابة عالي ({milk_yield})", "إدرار عالي")
        elif production_type == "حلابة_متوسط":
            dp = 10.0 + (milk_yield * 0.35); cp = dp / 0.72
            return AnimalRequirement(round(dp,2), round(cp,2),
                round(55+milk_yield*0.40,1), 32.0, 20.0, 4.0, 8.5,
                round(0.55+milk_yield*0.006,3), round(0.32+milk_yield*0.003,3),
                f"عنزات حلابة متوسط ({milk_yield})", "إدرار متوسط")
        elif production_type == "حامل_أخير":
            return AnimalRequirement(10.0, 13.0, 60.0, 33.0, 21.0, 3.8, 8.0, 0.60, 0.35,
                "عنزات حامل", "دفع غذائي")
        else:
            return AnimalRequirement(6.8, 9.0, 46.0, 46.0, 28.0, 3.0, 8.5, 0.42, 0.26,
                "عنزات صيانة", "بدون إنتاج")


def get_camel_requirements(production_type, weight_kg=400.0, milk_yield=5.0):
    if production_type == "نمو":
        return AnimalRequirement(10.5, 13.5, 60.0, 38.0, 24.0, 4.0, 8.0, 0.65, 0.38,
            "إبل نمو (حوار)", f"وزن {weight_kg}")
    elif production_type == "تسمين":
        return AnimalRequirement(9.5, 12.0, 65.0, 35.0, 22.0, 4.5, 7.5, 0.60, 0.35,
            "إبل تسمين", f"وزن {weight_kg}")
    elif production_type == "حليب":
        dp = 12.0 + (milk_yield * 0.25); cp = dp / 0.70
        return AnimalRequirement(round(dp,2), round(cp,2),
            round(62+milk_yield*0.40,1), 32.0, 20.0, 5.0, 8.5,
            round(0.70+milk_yield*0.006,3), round(0.40+milk_yield*0.003,3),
            f"إبل حلابة ({milk_yield})", "دهن الحليب عالي")
    elif production_type == "سباق":
        return AnimalRequirement(14.0, 17.0, 72.0, 28.0, 17.0, 6.0, 9.0, 0.85, 0.50,
            "إبل سباق", "طاقة عالية")
    else:
        return AnimalRequirement(7.0, 9.0, 48.0, 48.0, 30.0, 3.5, 9.0, 0.42, 0.26,
            "إبل صيانة", f"وزن {weight_kg}")


def get_horse_requirements(production_type, weight_kg=450.0):
    if production_type == "رياضة_مكثف":
        return AnimalRequirement(10.5, 13.5, 70.0, 30.0, 18.0, 7.0, 7.5, 0.70, 0.40,
            "خيول رياضة مكثف", "جهد عالي")
    elif production_type == "رياضة_عادي":
        return AnimalRequirement(9.0, 11.5, 63.0, 36.0, 22.0, 5.0, 7.5, 0.55, 0.32,
            "خيول رياضة عادي", "نشاط متوسط")
    elif production_type == "نمو_أمهار":
        return AnimalRequirement(12.0, 15.0, 65.0, 30.0, 18.0, 5.0, 8.0, 0.75, 0.42,
            "أمهار نمو", "نمو هيكلي")
    elif production_type == "مرضعات":
        return AnimalRequirement(12.5, 16.0, 68.0, 32.0, 20.0, 5.5, 8.0, 0.80, 0.45,
            "فرسات مرضعات", "إنتاج حليب")
    else:
        return AnimalRequirement(7.2, 9.5, 53.0, 46.0, 29.0, 3.5, 8.0, 0.45, 0.28,
            "خيول صيانة", "بدون جهد")


def get_poultry_requirements(strain, age_weeks=1):
    if strain == "لاحم":
        if age_weeks <= 1:
            return AnimalRequirement(20.0, 23.0, 76.0, 8.0, 4.0, 5.0, 6.5, 1.00, 0.50,
                "بادي لاحم", "Energy 3000")
        elif age_weeks <= 3:
            return AnimalRequirement(18.5, 21.0, 74.0, 9.0, 5.0, 5.0, 6.0, 0.90, 0.45,
                "نامي لاحم", "Energy 3100")
        elif age_weeks <= 5:
            return AnimalRequirement(17.0, 19.5, 75.0, 10.0, 5.5, 4.5, 6.0, 0.87, 0.43,
                "ناهي لاحم (4-5)", "Energy 3150")
        else:
            return AnimalRequirement(16.5, 19.0, 75.0, 10.0, 5.5, 4.5, 6.0, 0.85, 0.42,
                "ناهي لاحم (6+)", "Energy 3200")
    else:
        if age_weeks <= 6:
            return AnimalRequirement(17.0, 20.0, 72.0, 10.0, 5.5, 4.0, 7.0, 1.00, 0.50,
                "بادي بياض", "تحضير للبيض")
        elif age_weeks <= 18:
            return AnimalRequirement(14.5, 17.0, 70.0, 12.0, 6.5, 4.0, 9.0, 1.50, 0.45,
                "نامي بياض", "نمو هيكلي")
        else:
            return AnimalRequirement(15.5, 18.0, 72.0, 11.0, 6.0, 4.2, 11.5, 3.80, 0.45,
                "بياض إنتاجي", "إنتاج تجاري")


def get_quail_requirements(strain, age_weeks=1):
    if strain == "بياض":
        return AnimalRequirement(15.0, 18.0, 68.0, 11.0, 5.5, 4.5, 9.0, 2.50, 0.45,
            "سمان بياض", "إنتاج بيض")
    else:
        if age_weeks <= 2:
            return AnimalRequirement(20.5, 24.0, 74.0, 8.0, 4.0, 5.5, 6.5, 1.00, 0.55,
                "سمان بادي", "نمو سريع")
        elif age_weeks <= 4:
            return AnimalRequirement(18.5, 22.0, 72.0, 9.0, 4.5, 5.0, 6.0, 0.90, 0.50,
                "سمان نامي", "نمو متوسط")
        else:
            return AnimalRequirement(17.0, 20.0, 70.0, 10.0, 5.0, 4.5, 6.0, 0.85, 0.45,
                "سمان ناهي", "تسمين نهائي")


def get_fish_requirements(species, stage):
    if "زريعة" in stage or "بادئ" in stage:
        return AnimalRequirement(32.0, 40.0, 72.0, 8.0, 4.0, 10.0, 11.0, 1.50, 0.90,
            f"{species} — بادئ", "بروتين عالٍ")
    elif "نمو" in stage:
        return AnimalRequirement(25.0, 32.0, 70.0, 12.0, 6.0, 8.0, 9.0, 1.00, 0.70,
            f"{species} — نمو", "بروتين متوسط")
    else:
        return AnimalRequirement(22.0, 28.0, 68.0, 13.0, 7.0, 8.0, 9.5, 0.90, 0.65,
            f"{species} — تسمين", "تركيز طاقة")


def requirement_to_standard(req):
    return {"CP": req.CP, "DP": req.DP, "SE": req.SE, "NDF": req.NDF,
            "ADF": req.ADF, "EE": req.EE, "ASH": req.ASH, "Ca": req.Ca, "P": req.P}


# ═══ القسم 7: الحسابات والمحرك ═══
def compute_formula_nutrients(formula):
    totals = {"CP": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
              "EE": 0.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0}
    for ing, pct in formula.items():
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat:
                d = cat[ing]; f = pct / 100.0
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


def evaluate_difference(pct_diff):
    a = abs(pct_diff)
    if a <= 0.5: return {"label": "🎯 مطابق تماماً", "color": "#0d5302", "bg": "#c8e6c9", "score": 100}
    elif a <= 2.0: return {"label": "🌟 ممتاز", "color": "#1b5e20", "bg": "#dcedc8", "score": 95}
    elif a <= 5.0: return {"label": "✅ جيد جداً", "color": "#2e7d32", "bg": "#e8f5e9", "score": 85}
    elif a <= 10.0: return {"label": "🟢 جيد", "color": "#558b2f", "bg": "#f1f8e9", "score": 75}
    elif a <= 15.0: return {"label": "⭐ مقبول", "color": "#f9a825", "bg": "#fff8e1", "score": 65}
    elif a <= 25.0: return {"label": "⚠️ مقبول بتحفظ", "color": "#ef6c00", "bg": "#fff3e0", "score": 50}
    elif a <= 40.0: return {"label": "🟠 ضعيف", "color": "#e65100", "bg": "#ffe0b2", "score": 35}
    else: return {"label": "❌ غير مطابق", "color": "#c62828", "bg": "#ffebee", "score": 20}


def get_overall_rating(compare_rows):
    if not compare_rows: return {"label": "غير محدد", "color": "#666", "score": 0}
    scores = [r.get("score", 50) for r in compare_rows]
    avg = sum(scores) / len(scores)
    if avg >= 95: return {"label": "🏆 خلطة ممتازة", "color": "#1b5e20", "score": avg}
    elif avg >= 85: return {"label": "🌟 خلطة جيدة جداً", "color": "#2e7d32", "score": avg}
    elif avg >= 70: return {"label": "✅ خلطة جيدة", "color": "#558b2f", "score": avg}
    elif avg >= 55: return {"label": "⭐ خلطة مقبولة", "color": "#f9a825", "score": avg}
    else: return {"label": "⚠️ تحتاج تحسين", "color": "#e65100", "score": avg}


def auto_formulate_smart(available_ingredients, prices, custom_standard,
                          standard_key, tolerance=0.3, max_iterations=50,
                          required_oils=None):
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "SCIPY غير متوفرة"}
    ing_data = {}
    for ing in available_ingredients:
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat:
                ing_data[ing] = cat[ing]; break
    valid = [i for i in available_ingredients if i in ing_data]
    if len(valid) < 3:
        return {"success": False, "message": "اختر 3 مكونات على الأقل"}

    n = len(valid)
    c = [prices.get(i, 300.0) for i in valid]
    rows = {}
    for nutrient in ["CP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
        rows[nutrient] = [ing_data[i].get(nutrient, 0) for i in valid]
    rows["DP"] = [ing_data[i].get("CP", 0) * ing_data[i].get("DC", 0) for i in valid]

    targets = {k: custom_standard.get(k, 0) for k in ["DP","SE","NDF","ADF","Ca","P"]}
    oil_std = get_oil_standard(standard_key)
    oil_max = oil_std["max"]

    oil_set = set(get_oil_ingredients().keys())
    required_oils = required_oils or []
    valid_required_oils = [i for i in valid if i in oil_set and i in required_oils]
    n_req = len(valid_required_oils)
    per_oil_min = 0.0
    if n_req > 0:
        per_oil_min = min(0.5, (oil_max * 0.9) / n_req)

    bounds = []
    for i in valid:
        if i in oil_set:
            if i in required_oils:
                bounds.append((per_oil_min, oil_max * 0.6))
            else:
                bounds.append((0.0, oil_max * 0.6))
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

    oil_indicator = [1.0 if i in oil_set else 0.0 for i in valid]
    has_oils = sum(oil_indicator) > 0
    oil_upper_cap = max(oil_max, per_oil_min * n_req * 1.2) if n_req > 0 else oil_max

    try:
        A_eq = [[1.0] * n, rows["DP"]]
        b_eq = [100.0, targets["DP"] * 100.0]
        A_ub = [[-1.0 * x for x in rows["SE"]],
                [1.0 * x for x in rows["NDF"]],
                [1.0 * x for x in rows["ADF"]]]
        b_ub = [-1.0 * targets["SE"] * 100.0,
                targets["NDF"] * 1.15 * 100.0,
                targets["ADF"] * 1.15 * 100.0]
        if has_oils:
            A_ub.append(oil_indicator); b_ub.append(oil_upper_cap * 100.0)
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                      bounds=bounds, method='highs')
        if not res.success:
            for relax in [1.05, 1.10, 1.20, 1.30]:
                b_ub_r = [-1.0 * targets["SE"] * 100.0 * (2 - relax),
                          targets["NDF"] * relax * 100.0,
                          targets["ADF"] * relax * 100.0]
                if has_oils: b_ub_r.append(oil_upper_cap * 100.0)
                res = linprog(c, A_ub=A_ub, b_ub=b_ub_r, A_eq=A_eq, b_eq=b_eq,
                              bounds=bounds, method='highs')
                if res.success: break
    except Exception as e:
        return {"success": False, "message": f"خطأ: {e}"}

    if not res.success:
        return {"success": False, "message": "تعذر إيجاد حل — أضف مكونات متنوعة"}

    best = None; best_score = float('inf')
    cur_dp, cur_se = targets["DP"], targets["SE"]
    cur_ndf, cur_adf = targets["NDF"], targets["ADF"]
    log = []

    for iteration in range(max_iterations):
        try:
            A_eq = [[1.0] * n, rows["DP"], rows["Ca"], rows["P"]]
            b_eq = [100.0, cur_dp * 100.0, targets["Ca"] * 100.0, targets["P"] * 100.0]
            A_ub = [[-1.0 * x for x in rows["SE"]],
                    [1.0 * x for x in rows["NDF"]],
                    [1.0 * x for x in rows["ADF"]]]
            b_ub = [-1.0 * cur_se * 100.0,
                    cur_ndf * 1.10 * 100.0, cur_adf * 1.10 * 100.0]
            if has_oils:
                A_ub.append(oil_indicator); b_ub.append(oil_upper_cap * 100.0)
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method='highs',
                          options={'presolve': True, 'time_limit': 15})
        except Exception:
            res = None

        if res is None or not res.success:
            try:
                A_eq = [[1.0] * n, rows["DP"], rows["Ca"]]
                b_eq = [100.0, cur_dp * 100.0, targets["Ca"] * 100.0]
                A_ub_s = [[-1.0 * x for x in rows["SE"]]]
                b_ub_s = [-1.0 * cur_se * 100.0]
                if has_oils:
                    A_ub_s.append(oil_indicator); b_ub_s.append(oil_upper_cap * 100.0)
                res = linprog(c, A_ub=A_ub_s, b_ub=b_ub_s, A_eq=A_eq, b_eq=b_eq,
                              bounds=bounds, method='highs')
            except Exception:
                res = None
        if res is None or not res.success:
            cur_ndf *= 1.05; cur_adf *= 1.05
            log.append(f"تكرار {iteration+1}: تخفيف"); continue

        formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
        actual = compute_formula_nutrients(formula)
        total_oil_actual = compute_total_oil_percentage(formula)

        errors = {}
        for k in ["DP","SE","NDF","ADF","Ca","P"]:
            tv = targets.get(k, 0)
            errors[k] = abs(actual.get(k, 0) - tv) / tv if tv > 0 else 0

        weights = {"DP": 5.0, "SE": 3.0, "NDF": 1.5, "ADF": 1.0, "Ca": 1.0, "P": 1.0}
        score = sum(errors.get(k, 0) * weights[k] for k in errors)

        if score < best_score:
            best_score = score
            best = {"success": True, "formula": formula, "cost": res.fun / 100.0,
                    "actual_nutrients": actual,
                    "dp_error": abs(actual["DP"] - targets["DP"]),
                    "se_error": abs(actual["SE"] - targets["SE"]),
                    "ndf_error": abs(actual["NDF"] - targets["NDF"]),
                    "adf_error": abs(actual["ADF"] - targets["ADF"]),
                    "ca_error": abs(actual.get("Ca", 0) - targets["Ca"]),
                    "p_error": abs(actual.get("P", 0) - targets["P"]),
                    "total_oil": total_oil_actual, "oil_std": oil_std,
                    "iterations": iteration + 1, "log": log[-10:], "targets": targets}

        if (errors.get("DP", 1) * 100 <= tolerance and
            errors.get("SE", 1) * 100 <= tolerance * 2 and
            errors.get("NDF", 1) * 100 <= tolerance * 5 and
            errors.get("Ca", 1) * 100 <= tolerance * 15):
            best["perfect_match"] = True; break

        cur_dp += (targets["DP"] - actual["DP"]) * 0.25
        cur_se += (targets["SE"] - actual["SE"]) * 0.20
        cur_ndf += (targets["NDF"] - actual["NDF"]) * 0.15
        cur_adf += (targets["ADF"] - actual["ADF"]) * 0.15
        cur_dp = max(5.0, min(40.0, cur_dp))
        cur_se = max(10.0, min(90.0, cur_se))
        cur_ndf = max(5.0, min(70.0, cur_ndf))
        cur_adf = max(3.0, min(50.0, cur_adf))

    if best:
        best["log"] = log; return best
    return {"success": False, "message": "تعذر حل دقيق", "log": log}


def auto_add_salts_and_minerals(animal_type, requirement=None):
    salt = {}
    if animal_type in ["أغنام", "ماعز", "أبقار", "إبل"]:
        salt["بيكربونات الصوديوم"] = 0.75
    salt["مضاد سموم فطرية"] = 0.20
    salt["ملح الطعام"] = 0.50
    if animal_type in ["دواجن", "سمان"]:
        if requirement and requirement.Ca > 2.0:
            salt["الحجر الجيري"] = 8.0
        else:
            salt["الحجر الجيري"] = 1.5
        salt["فوسفات ثنائي الكالسيوم"] = 1.5
        salt["بريمكس تسمين دواجن"] = 0.30
    elif animal_type == "أسماك":
        salt["الحجر الجيري"] = 1.0
        salt["فوسفات ثنائي الكالسيوم"] = 1.5
        salt["بريمكس أسماك"] = 0.30
    elif animal_type == "خيول":
        salt["الحجر الجيري"] = 1.5
        salt["فوسفات ثنائي الكالسيوم"] = 1.5
        salt["بريمكس خيول"] = 0.30
    elif animal_type == "إبل":
        salt["الحجر الجيري"] = 2.0
        salt["فوسفات ثنائي الكالسيوم"] = 1.5
        salt["بريمكس إبل"] = 0.30
    else:
        salt["الحجر الجيري"] = 2.0
        salt["فوسفات ثنائي الكالسيوم"] = 1.5
        salt["بريمكس مجترات"] = 0.30
    return salt


# ═════════════════════════════════════════════════════════════════════════
# دالة جديدة: مطابقة احتياجات المختبر بالمعايير القياسية
# ═════════════════════════════════════════════════════════════════════════
def get_lab_requirement(animal_label, stage_label):
    try:
        if animal_label == "أبقار":
            m = {"تسمين": "تسمين_مكثف", "حليب/إدرار": "حليب_عالي",
                 "حمل/دفع غذائي": "حمل_أخير", "صيانة": "صيانة"}
            return get_cattle_requirements(m.get(stage_label, "صيانة"))
        if animal_label == "أغنام":
            m = {"تسمين": "تسمين_مكثف", "حليب/إدرار": "مرضعات",
                 "حمل/دفع غذائي": "حامل_أخير", "صيانة": "صيانة"}
            return get_sheep_requirements(m.get(stage_label, "صيانة"), is_male=True)
        if animal_label == "ماعز":
            m = {"تسمين": "تسمين_جديان", "حليب/إدرار": "حلابة_عالي",
                 "حمل/دفع غذائي": "حامل_أخير", "صيانة": "صيانة"}
            return get_goat_requirements(m.get(stage_label, "صيانة"), is_male=True)
        if animal_label == "خيول":
            m = {"تسمين": "رياضة_مكثف", "حليب/إدرار": "مرضعات",
                 "حمل/دفع غذائي": "نمو_أمهار", "صيانة": "صيانة"}
            return get_horse_requirements(m.get(stage_label, "صيانة"))
        if animal_label == "إبل":
            m = {"تسمين": "تسمين", "حليب/إدرار": "حليب",
                 "حمل/دفع غذائي": "نمو", "صيانة": "صيانة"}
            return get_camel_requirements(m.get(stage_label, "صيانة"))
        if animal_label == "دواجن لاحم":
            age = {"بادي": 1, "نامي": 3, "ناهي": 5, "بياض": 7}.get(stage_label, 1)
            return get_poultry_requirements("لاحم", age)
        if animal_label == "دواجن بياض":
            age = {"بادي": 4, "نامي": 12, "ناهي": 18, "بياض": 25}.get(stage_label, 18)
            return get_poultry_requirements("بياض", age)
        if animal_label == "سمان":
            age = {"بادي": 1, "نامي": 3, "ناهي": 5, "بياض": 7}.get(stage_label, 3)
            return get_quail_requirements("تسمين", age)
        if animal_label == "أسماك":
            stage = {"نمو": "نمو", "تسمين نهائي": "تسمين"}.get(stage_label, "نمو")
            return get_fish_requirements("البلطي النيلي", stage)
    except Exception:
        pass
    return None


# ═════════════════════════════════════════════════════════════════════════
# دالة جديدة: تقدير وزن الحيوان بشريط القياس
# ═════════════════════════════════════════════════════════════════════════
def estimate_animal_weight_by_tape(animal_type, heart_girth_cm,
                                    body_length_cm=0.0, bcs=3.0):
    HG = float(heart_girth_cm or 0)
    BL = float(body_length_cm or 0)
    result = {"weight_kg": 0.0, "formula": "", "reference": "",
              "note": "", "confidence": "متوسطة"}

    if HG <= 0:
        return result

    if animal_type == "أبقار":
        if BL > 0:
            result["weight_kg"] = (HG ** 2) * BL / 10838.0
            result["formula"] = "W = (HG² × BL) / 10838"
            result["reference"] = "Schaeffer's formula (Cattle)"
            result["confidence"] = "عالية (± 5%)"
        else:
            result["weight_kg"] = 0.00261 * (HG ** 2.62)
            result["formula"] = "W = 0.00261 × HG^2.62"
            result["reference"] = "Heinrichs et al. 1992"
            result["confidence"] = "متوسطة (± 8%)"
    elif animal_type in ["أغنام", "ماعز"]:
        if BL > 0:
            result["weight_kg"] = (HG ** 2) * BL / 10838.0
        else:
            result["weight_kg"] = (HG ** 2) * (HG * 1.20) / 10838.0
        result["formula"] = "W = (HG² × BL) / 10838"
        result["reference"] = "Schaeffer (adapted) — Sheep/Goats"
        result["confidence"] = "متوسطة (± 8%)"
    elif animal_type == "خيول":
        if BL <= 0:
            BL = HG * 1.05
        result["weight_kg"] = (HG ** 2) * BL / 11880.0
        result["formula"] = "W = (HG² × BL) / 11880"
        result["reference"] = "NRC 2007 — Horses"
        result["confidence"] = "عالية (± 6%)"
    elif animal_type == "إبل":
        if BL <= 0:
            BL = HG * 1.15
        result["weight_kg"] = (HG ** 2) * BL / 10000.0
        result["formula"] = "W ≈ (HG² × BL) / 10000"
        result["reference"] = "FAO 2010 (approximate)"
        result["confidence"] = "منخفضة (± 12%)"
    elif animal_type == "دواجن":
        result["weight_kg"] = max(0.0, (HG - 8.0) * 0.045)
        result["formula"] = "W ≈ (HG - 8) × 0.045"
        result["reference"] = "تقدير تجريبي للدواجن"
        result["confidence"] = "منخفضة"
    elif animal_type == "سمان":
        result["weight_kg"] = max(0.0, (HG - 4.0) * 0.008)
        result["formula"] = "W ≈ (HG - 4) × 0.008"
        result["reference"] = "تقدير تجريبي للسمان"
        result["confidence"] = "منخفضة"
    else:
        result["note"] = "هذا النوع يحتاج ميزانًا رقميًا"
        return result

    if 1.0 <= bcs <= 5.0:
        adj = 1.0 + (bcs - 3.0) * 0.03
        result["weight_kg"] *= adj
        result["note"] = f"تعديل BCS (درجة {bcs}): × {adj:.3f}"

    result["weight_kg"] = round(result["weight_kg"], 2)
    return result


# ═════════════════════════════════════════════════════════════════════════
# دالة جديدة: رسم بياني لتقييم المركزات
# ═════════════════════════════════════════════════════════════════════════
def create_concentrate_chart(selected_concentrates, standard):
    """رسم بياني لمركز واحد أو أكثر مقابل المعيار"""
    if not PLOTLY_AVAILABLE or not selected_concentrates:
        return None
    nutrients = ["CP", "DP", "SE", "NDF", "ADF", "EE", "Ca", "P"]
    labels_ar = {"CP": "بروتين خام", "DP": "بروتين مهضوم", "SE": "معادل النشاء",
                 "NDF": "NDF", "ADF": "ADF", "EE": "دهن", "Ca": "Ca", "P": "P"}
    fig = go.Figure()
    # المعيار
    if standard:
        std_vals = [standard.get(n, 0) for n in nutrients]
        fig.add_trace(go.Bar(
            name="المعيار القياسي",
            x=[labels_ar[n] for n in nutrients],
            y=std_vals,
            marker_color='#1976d2',
            text=[f"{v:.1f}" for v in std_vals],
            textposition='auto'))
    # كل مركز
    colors = ['#43a047', '#e53935', '#8e24aa', '#fb8c00', '#00897b',
              '#3949ab', '#7cb342', '#c62828']
    for i, (cname, cdata) in enumerate(selected_concentrates.items()):
        vals = [cdata.get(n, 0) for n in nutrients]
        fig.add_trace(go.Bar(
            name=cname,
            x=[labels_ar[n] for n in nutrients],
            y=vals,
            marker_color=colors[i % len(colors)],
            text=[f"{v:.1f}" for v in vals],
            textposition='auto'))
    fig.update_layout(
        title="مقارنة المركزات بالمعيار القياسي",
        barmode='group',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
        xaxis_title="العنصر الغذائي",
        yaxis_title="القيمة")
    return fig


def create_lab_comparison_chart(calculated, standard):
    """رسم بياني لمقارنة نتائج المختبر بالمعيار"""
    if not PLOTLY_AVAILABLE:
        return None
    nutrients = [k for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "Ca", "P"]
                 if standard and k in standard]
    if not nutrients:
        return None
    labels_ar = {"CP": "بروتين خام CP", "DP": "بروتين مهضوم DP",
                 "SE": "معادل النشاء SE", "NDF": "NDF", "ADF": "ADF",
                 "EE": "دهن EE", "Ca": "Ca", "P": "P"}
    fig = go.Figure()
    std_vals = [standard.get(n, 0) for n in nutrients]
    act_vals = [calculated.get(n, 0) for n in nutrients]
    fig.add_trace(go.Bar(
        name="المعيار القياسي",
        x=[labels_ar.get(n, n) for n in nutrients],
        y=std_vals, marker_color='#1976d2',
        text=[f"{v:.2f}" for v in std_vals], textposition='auto'))
    fig.add_trace(go.Bar(
        name="المحسوب من المختبر",
        x=[labels_ar.get(n, n) for n in nutrients],
        y=act_vals, marker_color='#43a047',
        text=[f"{v:.2f}" for v in act_vals], textposition='auto'))
    fig.update_layout(
        title="مقارنة نتائج المختبر بالمعايير القياسية",
        barmode='group', height=480,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
        xaxis_title="العنصر الغذائي", yaxis_title="القيمة")
    return fig


def create_lab_radar_chart(calculated, standard):
    """رسم راداري لمقارنة النسبة %"""
    if not PLOTLY_AVAILABLE or not standard:
        return None
    nutrients = [k for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "Ca", "P"]
                 if standard.get(k, 0) > 0]
    if len(nutrients) < 3:
        return None
    labels_ar = {"CP": "CP", "DP": "DP", "SE": "SE", "NDF": "NDF",
                 "ADF": "ADF", "EE": "EE", "Ca": "Ca", "P": "P"}
    std_pct = [100.0] * len(nutrients)
    act_pct = [(calculated.get(n, 0) / standard.get(n, 1)) * 100
               for n in nutrients]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=std_pct + [std_pct[0]],
        theta=[labels_ar.get(n, n) for n in nutrients] + [labels_ar.get(nutrients[0], nutrients[0])],
        fill='toself', name='المعيار (100%)',
        line=dict(color='#1976d2', width=2)))
    fig.add_trace(go.Scatterpolar(
        r=act_pct + [act_pct[0]],
        theta=[labels_ar.get(n, n) for n in nutrients] + [labels_ar.get(nutrients[0], nutrients[0])],
        fill='toself', name='المحسوب',
        line=dict(color='#43a047', width=2)))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 150])),
        title="المقارنة الشاملة % من المعيار",
        height=500)
    return fig


# ═══ القسم 8: بدائل الحليب ═══
MILK_REPLACER_STANDARDS = {
    "عجول (Calves)": {"CP": 24.0, "Fat": 24.0, "Lactose": 45.0, "Lysine": 2.1,
                      "Ca": 0.75, "P": 0.70, "Fiber_max": 0.15, "Ash_max": 10.0,
                      "notes": "عمر 1-6 أسابيع"},
    "حملان (Lambs)": {"CP": 24.0, "Fat": 24.0, "Lactose": 40.0, "Lysine": 2.1,
                      "Ca": 0.80, "P": 0.70, "Fiber_max": 0.15, "Ash_max": 10.0,
                      "notes": "≥ 24% دهن"},
    "جديان (Goat Kids)": {"CP": 24.0, "Fat": 24.0, "Lactose": 42.0, "Lysine": 2.1,
                          "Ca": 0.80, "P": 0.70, "Fiber_max": 0.15, "Ash_max": 10.0,
                          "notes": "بديل الجديان"},
    "إبل (Camel Calves)": {"CP": 26.0, "Fat": 28.0, "Lactose": 38.0, "Lysine": 2.3,
                           "Ca": 0.85, "P": 0.75, "Fiber_max": 0.10, "Ash_max": 9.0,
                           "notes": "بروتين ودهن أعلى"},
    "أمهار (Foals)": {"CP": 22.0, "Fat": 20.0, "Lactose": 45.0, "Lysine": 1.9,
                      "Ca": 0.90, "P": 0.80, "Fiber_max": 0.15, "Ash_max": 9.0,
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


def formulate_milk_replacer(animal_type, target_volume_kg=100.0, selected_ingredients=None):
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "SCIPY غير متوفرة"}
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
    except Exception as e:
        return {"success": False, "message": f"خطأ: {e}"}
    if not res.success:
        return {"success": False, "message": "تعذر التركيب"}
    formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
    actual = {"CP": 0, "Fat": 0, "Lactose": 0}
    for ing, pct in formula.items():
        d = MILK_REPLACER_INGREDIENTS[ing]
        actual["CP"] += pct / 100.0 * d["CP"]
        actual["Fat"] += pct / 100.0 * d["Fat"]
        actual["Lactose"] += pct / 100.0 * d["Lactose"]
    return {"success": True, "formula": formula, "cost_per_100kg": res.fun / 100.0,
            "cost_per_kg": res.fun / 10000.0, "standard": standard,
            "actual": actual, "animal": animal_type}


# ═══ القسم 9: OCR ═══
def match_ingredient_name(text):
    if not text: return None
    tl = text.strip().lower()
    for cat in BIG_FEEDS_LIBRARY.values():
        for name in cat.keys():
            if name.lower() in tl or tl in name.lower():
                return name
    kw = {"ذرة": "ذرة صفراء", "صويا": "كسب فول صويا 44%",
          "شعير": "شعير مطحون", "قمح": "قمح محلي", "نخالة": "نخالة قمح (ردة)",
          "فول سوداني": "أمباز الفول السوداني", "عباد": "كسب عباد الشمس 36%",
          "سمسم": "كسب السمسم", "جلوتين": "كسب جلوتين 60%",
          "سمك": "مسحوق أسماك 60%", "لحم": "مسحوق اللحم والعظم",
          "دم": "مسحوق الدم", "ليسين": "ليسين نقي", "ميثيونين": "ميثيونين نقي",
          "ملح": "ملح الطعام", "حجر": "الحجر الجيري",
          "فوسفات": "فوسفات ثنائي الكالسيوم", "بيكربونات": "بيكربونات الصوديوم",
          "مولاس": "مولاس قصب السكر", "برسيم": "البرسيم الجاف",
          "يوريا": "يوريا علفية", "زيت": "زيت فول الصويا",
          "مركز": "مركز تسمين 30% بروتين"}
    for k, m in kw.items():
        if k in tl: return m
    return None


def extract_ingredients_from_image(image_bytes):
    if not OCR_AVAILABLE:
        return {"success": False, "message": "pytesseract غير مثبتة"}
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"success": False, "message": "تعذر قراءة الصورة"}
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)
        t1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 11, 2)
        _, t2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        texts = []
        for t in [t1, t2, gray]:
            try:
                txt = pytesseract.image_to_string(t, lang='ara+eng',
                    config=r'--oem 3 --psm 6')
                if txt.strip(): texts.append(txt)
            except Exception:
                continue
        if not texts:
            return {"success": False, "message": "لم يتم استخراج نص"}
        full = "\n".join(texts)
        ingredients = {}
        for line in full.split('\n'):
            line = line.strip()
            if len(line) < 3: continue
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
        return {"success": True, "ingredients": ingredients, "raw_text": full,
                "count": len(ingredients)}
    except Exception as e:
        return {"success": False, "message": f"خطأ: {str(e)}"}


# ═══ القسم 10: الرسوم البيانية الأصلية ═══
def create_colorful_bar_chart(standard, actual):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        nutrients = [n for n in ["CP","DP","SE","NDF","ADF","EE","ASH"] if n in standard]
        if not nutrients: return None
        std_vals = [standard[n] for n in nutrients]
        act_vals = [actual.get(n, 0) for n in nutrients]
        fig, ax = plt.subplots(figsize=(9, 4.5))
        x = np.arange(len(nutrients)); width = 0.35
        bars1 = ax.bar(x - width/2, std_vals, width, label='المعيار',
                       color='#1976d2', edgecolor='#0d47a1', linewidth=1.5)
        bars2 = ax.bar(x + width/2, act_vals, width, label='المحسوب',
                       color='#43a047', edgecolor='#1b5e20', linewidth=1.5)
        for bar in bars1:
            h = bar.get_height()
            ax.text(bar.get_x()+bar.get_width()/2, h, f'{h:.1f}', ha='center',
                    va='bottom', fontsize=9, color='#0d47a1', fontweight='bold')
        for bar in bars2:
            h = bar.get_height()
            ax.text(bar.get_x()+bar.get_width()/2, h, f'{h:.1f}', ha='center',
                    va='bottom', fontsize=9, color='#1b5e20', fontweight='bold')
        ax.set_xlabel('العنصر', fontsize=11, fontweight='bold')
        ax.set_title('مقارنة العناصر الغذائية', fontsize=13, fontweight='bold',
                     color='#1b5e20')
        ax.set_xticks(x); ax.set_xticklabels(nutrients, fontsize=10)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_facecolor('#fafafa')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception:
        return None


def create_colorful_pie_chart(formula):
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2: return None
    try:
        colors = ['#e53935','#8e24aa','#3949ab','#1e88e5','#00897b','#43a047',
                  '#7cb342','#fdd835','#fb8c00','#6d4c41','#c62828','#6a1b9a']
        names = list(formula.keys()); vals = list(formula.values())
        fig, ax = plt.subplots(figsize=(8, 5))
        wedges, texts, autotexts = ax.pie(vals, autopct='%1.1f%%',
            colors=colors[:len(names)], startangle=90, pctdistance=0.75,
            wedgeprops=dict(edgecolor='white', linewidth=2))
        for t in autotexts:
            t.set_color('white'); t.set_fontweight('bold'); t.set_fontsize(9)
        ax.legend(names, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
                  fontsize=9, title="المكونات", title_fontsize=10)
        ax.set_title('توزيع المكونات', fontsize=13, fontweight='bold',
                     color='#1b5e20')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception:
        return None


def create_radar_chart(standard, actual):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        nutrients = [n for n in ["CP","DP","SE","NDF","ADF","EE","Ca","P"]
                     if n in standard and standard[n] > 0]
        if len(nutrients) < 3: return None
        std_norm = [100.0 for _ in nutrients]
        act_norm = [(actual.get(n, 0) / standard[n]) * 100 for n in nutrients]
        angles = np.linspace(0, 2 * np.pi, len(nutrients), endpoint=False).tolist()
        std_norm += std_norm[:1]; act_norm += act_norm[:1]; angles += angles[:1]
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, std_norm, 'o-', linewidth=2.5, color='#1976d2', label='المعيار')
        ax.fill(angles, std_norm, alpha=0.15, color='#1976d2')
        ax.plot(angles, act_norm, 'o-', linewidth=2.5, color='#43a047', label='المحسوب')
        ax.fill(angles, act_norm, alpha=0.25, color='#43a047')
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(nutrients, fontsize=10)
        ax.set_ylim(0, max(max(std_norm), max(act_norm)) * 1.2)
        ax.set_title('المقارنة الشاملة %', fontsize=12, fontweight='bold',
                     color='#1b5e20', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
        ax.grid(True, alpha=0.3); ax.set_facecolor('#fafafa')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception:
        return None


def create_gauge_chart(score):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect='equal'))
        colors_g = ['#c62828','#ef6c00','#f9a825','#7cb342','#43a047','#1b5e20']
        for i, c in enumerate(colors_g):
            theta1 = 180 - (i * 30); theta2 = 180 - ((i + 1) * 30)
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
        ax.set_xlim(-1.2, 1.2); ax.set_ylim(-0.7, 1.2); ax.axis('off')
        ax.set_facecolor('white')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception:
        return None


# ═══ القسم 11: مولد PDF ═══
class PDFGenerator:
    def __init__(self):
        self.font_name = font_mgr.font_name
        self.font_bold = font_mgr.font_bold
        self.logo_path = None
        for lp in LOGO_OPTIONS + PHOTO_OPTIONS:
            if os.path.exists(lp):
                self.logo_path = lp; break

    def _ar(self, text):
        if text is None: return ""
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
        try: canvas_obj.setFillAlpha(0.07)
        except Exception: pass
        canvas_obj.saveState()
        canvas_obj.translate(w/2, h/2); canvas_obj.rotate(45)
        canvas_obj.drawCentredString(0, 0, self._ar("تاور نولجي"))
        canvas_obj.restoreState()
        try: canvas_obj.setFillAlpha(1)
        except Exception: pass
        canvas_obj.setFillColor(HexColor('#1b5e20'))
        canvas_obj.rect(0, h-90, w, 90, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor('#d4af37'))
        canvas_obj.rect(0, h-95, w, 5, fill=1, stroke=0)
        try:
            if self.logo_path:
                canvas_obj.drawImage(self.logo_path, 30, h-78, width=60, height=60,
                                      preserveAspectRatio=True, anchor='sw', mask='auto')
        except Exception: pass
        canvas_obj.setFillColor(white); canvas_obj.setFont(self.font_name, 22)
        canvas_obj.drawCentredString(w/2, h-38, self._ar("تاور نولجي  Tawor Nology"))
        canvas_obj.setFont(self.font_name, 12)
        canvas_obj.setFillColor(HexColor('#e8f5e9'))
        canvas_obj.drawCentredString(w/2, h-58, self._ar("للإنتاج الحيواني وتغذية الحيوان"))
        canvas_obj.setFont(self.font_name, 10)
        canvas_obj.setFillColor(HexColor('#d4af37'))
        canvas_obj.drawCentredString(w/2, h-76,
            self._ar(f"إشراف: {SUPERVISOR}"))
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
        canvas_obj.setFillColor(white); canvas_obj.setFont(self.font_name, 8)
        canvas_obj.drawCentredString(w/2, 27,
            self._ar("تاور نولجي Tawor Nology © 2026"))
        canvas_obj.setFont(self.font_name, 7)
        canvas_obj.drawCentredString(w/2, 12,
            self._ar(f"صفحة {canvas_obj.getPageNumber()}"))
        try:
            qr = qrcode.QRCode(version=1, box_size=3, border=1)
            qr.add_data(PLATFORM_URL); qr.make(fit=True)
            qi = qr.make_image(fill_color="#1b5e20", back_color="white")
            buf = io.BytesIO(); qi.save(buf, format="PNG"); buf.seek(0)
            canvas_obj.drawImage(RLImage(buf), w/2-20, 46, width=40, height=40)
        except Exception: pass
        sx, sy = w - 105, 145
        canvas_obj.setStrokeColor(HexColor('#c62828')); canvas_obj.setLineWidth(3.0)
        canvas_obj.circle(sx, sy, 70, stroke=1, fill=0)
        canvas_obj.setLineWidth(1.5); canvas_obj.circle(sx, sy, 62, stroke=1, fill=0)
        canvas_obj.setFillColor(HexColor('#c62828')); canvas_obj.setFont(self.font_name, 9)
        canvas_obj.drawCentredString(sx, sy+40, self._ar("تاور نولجي"))
        canvas_obj.drawCentredString(sx, sy+28, self._ar("Tawor Nology"))
        canvas_obj.setFont(self.font_name, 7.5)
        canvas_obj.drawCentredString(sx, sy+10, self._ar("م. عبدالقادر"))
        canvas_obj.drawCentredString(sx, sy-1, self._ar("إسماعيل تاور"))
        canvas_obj.setFont(self.font_name, 6)
        canvas_obj.drawCentredString(sx, sy-17, self._ar("اختصاصي تغذية الحيوان"))
        canvas_obj.drawCentredString(sx, sy-30, self._ar("معتمد رسمياً"))
        canvas_obj.drawCentredString(sx, sy-42, self._ar("© 2026"))
        canvas_obj.restoreState()

    def _comparison_table(self, standard, calculated):
        labels = {"CP": "بروتين خام CP", "DP": "بروتين مهضوم DP",
                  "SE": "معادل النشاء SE", "NDF": "ألياف NDF",
                  "ADF": "ألياف ADF", "EE": "دهن EE", "ASH": "رماد ASH",
                  "Ca": "كالسيوم Ca", "P": "فسفور P"}
        header = [self._ar(x) for x in
                  ["العنصر", "المعيار", "المحسوب", "الفرق", "الفرق %", "التقييم"]]
        data = [header]
        cmds = [('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#9e9e9e')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                ('TOPPADDING', (0, 0), (-1, -1), 7)]
        row = 1
        for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
            if k not in standard: continue
            sv = standard[k]; cv = calculated.get(k, 0.0)
            diff = cv - sv; pct = (diff / sv * 100) if sv else 0
            ev = evaluate_difference(pct)
            unit = "%" if k != "SE" else ""
            data.append([self._ar(labels.get(k, k)), f"{sv:.2f}{unit}",
                         f"{cv:.2f}{unit}", f"{diff:+.3f}", f"{pct:+.2f}%",
                         self._ar(ev["label"])])
            cmds.append(('BACKGROUND', (0, row), (-1, row), HexColor(ev["bg"])))
            cmds.append(('TEXTCOLOR', (5, row), (5, row), HexColor(ev["color"])))
            row += 1
        t = Table(data, colWidths=[100, 70, 70, 70, 70, 105])
        t.setStyle(TableStyle(cmds))
        return t

    def _oil_table(self, formula, standard_key):
        oils = get_oil_ingredients()
        oil_rows = [(ing, pct) for ing, pct in formula.items() if ing in oils]
        oil_std = get_oil_standard(standard_key)
        total_oil = sum(p for _, p in oil_rows)

        header = [self._ar("الزيت"), self._ar("النسبة %"),
                  self._ar("كجم/طن"), self._ar("kcal/kg")]
        data = [header]
        if oil_rows:
            for ing, pct in oil_rows:
                data.append([self._ar(ing), f"{pct:.3f}%",
                             f"{pct*10:.2f}", f"{pct * 90.0:.0f}"])
            data.append([self._ar("الإجمالي"), f"{total_oil:.3f}%",
                         f"{total_oil*10:.2f}", f"{total_oil * 90:.0f}"])
            last_bg = HexColor('#ffe0b2')
        else:
            data.append([self._ar("— لا توجد زيوت —"), "0.00%", "0.00", "0"])
            last_bg = HexColor('#f5f5f5')

        cmds = [('BACKGROUND', (0, 0), (-1, 0), HexColor('#e65100')),
                ('TEXTCOLOR',  (0, 0), (-1, 0), white),
                ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME',   (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE',   (0, 0), (-1, -1), 9),
                ('GRID',       (0, 0), (-1, -1), 1, HexColor('#bf360c')),
                ('BACKGROUND', (0, -1), (-1, -1), last_bg),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]
        t = Table(data, colWidths=[170, 80, 80, 110])
        t.setStyle(TableStyle(cmds))
        return (t, total_oil, oil_std)

    def generate_report(self, formula, requirement, animal_type, breed, cost, city,
                        local_cost, local_sym, requester_name="", protein_basis="DP",
                        standard_key="", include_charts=True):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40,
                                topMargin=115, bottomMargin=145)
        story = []
        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text),
                ParagraphStyle('s', fontName=self.font_name, fontSize=size,
                    alignment=align, textColor=HexColor(color), spaceAfter=6,
                    leading=size * 1.6))

        story.append(P("تقرير فني رسمي — تركيب علفة", size=20, align=TA_CENTER,
                       color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
                                color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))

        client_data = [
            [self._ar("👤 طالب الخدمة:"), self._ar(requester_name or "........")],
            [self._ar("📍 الموقع:"), self._ar(city)],
            [self._ar("🐾 الفصيل:"), self._ar(f"{animal_type} — {breed}")],
            [self._ar("🧬 أساس الحساب:"),
             self._ar("DP" if protein_basis == "DP" else "CP")],
            [self._ar("📅 التاريخ:"), datetime.now().strftime('%Y-%m-%d | %H:%M')],
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
            ('BOTTOMPADDING', (0, 0), (-1, -1), 9)]))
        story.append(ct); story.append(Spacer(1, 15))

        standard_vals = requirement_to_standard(requirement)
        calculated_vals = compute_formula_nutrients(formula)
        scores = []
        for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
            if k not in standard_vals: continue
            sv = standard_vals[k]; cv = calculated_vals.get(k, 0.0)
            pct = ((cv - sv) / sv * 100) if sv else 0
            scores.append({"score": evaluate_difference(pct)["score"]})
        overall = get_overall_rating(scores)

        story.append(P("📊 جدول مقارنة العناصر", size=14,
                       align=TA_RIGHT, color='#1b5e20'))
        story.append(Spacer(1, 8))
        story.append(self._comparison_table(standard_vals, calculated_vals))
        story.append(Spacer(1, 12))

        summary_data = [[self._ar("التقييم العام"), self._ar("عدد المطابقة")],
                        [self._ar(overall["label"]),
                         f"{sum(1 for s in scores if s['score'] >= 85)}/{len(scores)}"]]
        st_tbl = Table(summary_data, colWidths=[245, 245])
        st_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565c0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#e3f2fd')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#1976d2')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
        story.append(st_tbl); story.append(Spacer(1, 15))

        oil_tbl, total_oil, oil_std = self._oil_table(formula, standard_key)
        story.append(P("🌰 جدول الزيوت", size=14, align=TA_RIGHT, color='#e65100'))
        story.append(Spacer(1, 8))
        story.append(oil_tbl)
        story.append(Spacer(1, 15))

        if include_charts:
            story.append(P("📈 الرسوم البيانية", size=14, align=TA_RIGHT,
                           color='#1b5e20'))
            story.append(Spacer(1, 10))
            c1 = create_colorful_bar_chart(standard_vals, calculated_vals)
            if c1:
                story.append(RLImage(c1, width=450, height=250))
                story.append(Spacer(1, 12))

        story.append(PageBreak())
        story.append(P("💰 التكاليف", size=14, align=TA_RIGHT, color='#1b5e20'))
        story.append(Spacer(1, 8))
        cost_data = [
            [self._ar("البند"), self._ar("القيمة")],
            [self._ar("التكلفة للطن ($)"), f"${cost:.2f}"],
            [self._ar(f"التكلفة ({local_sym})"), f"{local_cost:,.2f}"],
            [self._ar("الدهن EE"), f"{calculated_vals['EE']:.2f}%"]]
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
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
        story.append(tc); story.append(Spacer(1, 18))

        if formula:
            story.append(P("🌾 المكونات", size=14, align=TA_RIGHT, color='#1b5e20'))
            story.append(Spacer(1, 8))
            ing_data = [[self._ar("المكون"), self._ar("النسبة %"),
                         self._ar("كجم/طن")]]
            for ing, pct in formula.items():
                ing_data.append([self._ar(ing), f"{pct:.2f}%", f"{pct*10:.1f}"])
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
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
            story.append(ti)

        doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()


pdf_gen = PDFGenerator()


# ═════════════════════════════════════════════════════════════════════════
# دالة جديدة: PDF لتقرير المختبر
# ═════════════════════════════════════════════════════════════════════════
def generate_lab_analysis_pdf(animal_label, stage_label, analysis_basis,
                               target_value, entered_components,
                               calculated_nutrients, requirement,
                               requester_name=""):
    if not REPORTLAB_AVAILABLE:
        return b""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40,
                            topMargin=115, bottomMargin=145)
    story = []
    def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
        return Paragraph(pdf_gen._ar(text),
            ParagraphStyle('s', fontName=font_mgr.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color), spaceAfter=6,
                leading=size * 1.6))

    story.append(P("تقرير المختبر — تحليل علف جاهز", size=20,
                   align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2.5,
                            color=HexColor('#d4af37')))
    story.append(Spacer(1, 12))

    info_data = [
        [pdf_gen._ar("👤 طالب التحليل:"),
         pdf_gen._ar(requester_name or "........")],
        [pdf_gen._ar("🐾 الحيوان:"),
         pdf_gen._ar(f"{animal_label} — {stage_label}")],
        [pdf_gen._ar("🧬 أساس التحليل:"), pdf_gen._ar(analysis_basis)],
        [pdf_gen._ar("🎯 القيمة المستهدفة:"),
         pdf_gen._ar(f"{target_value:.2f}%")],
        [pdf_gen._ar("📅 التاريخ:"),
         datetime.now().strftime('%Y-%m-%d | %H:%M')]]
    t_info = Table(info_data, colWidths=[150, 340])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
        ('BACKGROUND', (1, 0), (1, -1), HexColor('#fafafa')),
        ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')),
        ('INNERGRID', (0, 0), (-1, -1), 0.6, HexColor('#c8e6c9')),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
    story.append(t_info); story.append(Spacer(1, 15))

    story.append(P("🌾 المكونات المُدخلة", size=14, align=TA_RIGHT,
                   color='#1b5e20'))
    story.append(Spacer(1, 8))
    comp_data = [[pdf_gen._ar("المادة"), pdf_gen._ar("الوزن (كجم)"),
                  pdf_gen._ar("النسبة %")]]
    total_w = sum(v for v in entered_components.values() if v > 0)
    for name, w in entered_components.items():
        if w > 0:
            comp_data.append([pdf_gen._ar(name), f"{w:.1f}",
                              f"{w / total_w * 100:.2f}%"])
    comp_data.append([pdf_gen._ar("الإجمالي"), f"{total_w:.1f}", "100.00%"])
    t_comp = Table(comp_data, colWidths=[280, 100, 110])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#e8f5e9')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
    story.append(t_comp); story.append(Spacer(1, 15))

    if requirement:
        std = requirement_to_standard(requirement)
        story.append(P("📊 المقارنة بالمعايير القياسية", size=14,
                       align=TA_RIGHT, color='#1565c0'))
        story.append(Spacer(1, 8))
        story.append(pdf_gen._comparison_table(std, calculated_nutrients))
        story.append(Spacer(1, 15))

        # التقييم العام
        scores = []
        for k, sv in std.items():
            if sv > 0:
                pct = ((calculated_nutrients.get(k, 0) - sv) / sv * 100)
                scores.append({"score": evaluate_difference(pct)["score"]})
        overall = get_overall_rating(scores)
        summary = [[pdf_gen._ar("التقييم العام"), pdf_gen._ar("عدد المطابقة")],
                   [pdf_gen._ar(overall["label"]),
                    f"{sum(1 for s in scores if s['score'] >= 85)}/{len(scores)}"]]
        t_sum = Table(summary, colWidths=[245, 245])
        t_sum.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565c0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#e3f2fd')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#1976d2')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
        story.append(t_sum); story.append(Spacer(1, 15))

        # التوصيات
        story.append(P("💡 التوصيات", size=14, align=TA_RIGHT, color='#e65100'))
        story.append(Spacer(1, 8))
        recs = []
        for k, sv in std.items():
            if sv <= 0: continue
            cv = calculated_nutrients.get(k, 0)
            pct = ((cv - sv) / sv * 100)
            if abs(pct) <= 5: continue
            sign = "أعلى" if pct > 0 else "أقل"
            recs.append(f"• {k}: {sign} من المعيار بنسبة {pct:+.1f}% "
                        f"(محسوب {cv:.2f}، معيار {sv:.2f})")
        if recs:
            for r in recs:
                story.append(P(r, size=10, align=TA_RIGHT, color='#bf360c'))
        else:
            story.append(P("✅ الخلطة مطابقة تماماً للمعايير",
                           size=11, align=TA_RIGHT, color='#1b5e20'))
        story.append(Spacer(1, 15))

    # التوقيعات
    sign = [[pdf_gen._ar("توقيع الطالب"), pdf_gen._ar("توقيع المختص")],
            [pdf_gen._ar("........"), pdf_gen._ar(SUPERVISOR)],
            [pdf_gen._ar("التاريخ"), pdf_gen._ar(SUPERVISOR_TITLE)]]
    ts = Table(sign, colWidths=[245, 245])
    ts.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f5e9'))]))
    story.append(ts)

    doc.build(story, onFirstPage=pdf_gen._draw_page,
              onLaterPages=pdf_gen._draw_page)
    buffer.seek(0)
    return buffer.getvalue()


# ═════════════════════════════════════════════════════════════════════════
# دالة جديدة: PDF لتقدير الوزن بالشريط
# ═════════════════════════════════════════════════════════════════════════
def generate_tape_weight_pdf(animal_type, heart_girth, body_length, bcs, result,
                              requester_name=""):
    if not REPORTLAB_AVAILABLE:
        return b""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40,
                            topMargin=115, bottomMargin=145)
    story = []
    def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
        return Paragraph(pdf_gen._ar(text),
            ParagraphStyle('s', fontName=font_mgr.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color), spaceAfter=6,
                leading=size * 1.6))

    story.append(P("تقرير تقدير وزن الحيوان — بشريط القياس", size=18,
                   align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2.5,
                            color=HexColor('#d4af37')))
    story.append(Spacer(1, 12))

    info_data = [
        [pdf_gen._ar("👤 الطالب:"), pdf_gen._ar(requester_name or "........")],
        [pdf_gen._ar("🐾 نوع الحيوان:"), pdf_gen._ar(animal_type)],
        [pdf_gen._ar("📐 محيط الصدر:"), pdf_gen._ar(f"{heart_girth} سم")],
        [pdf_gen._ar("📏 الطول:"), pdf_gen._ar(f"{body_length} سم")],
        [pdf_gen._ar("⚖️ BCS:"), pdf_gen._ar(f"{bcs}")],
        [pdf_gen._ar("📅 التاريخ:"), datetime.now().strftime('%Y-%m-%d %H:%M')]]
    t_info = Table(info_data, colWidths=[150, 340])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
        ('BACKGROUND', (1, 0), (1, -1), HexColor('#fafafa')),
        ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')),
        ('INNERGRID', (0, 0), (-1, -1), 0.6, HexColor('#c8e6c9')),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
    story.append(t_info); story.append(Spacer(1, 15))

    # النتيجة الكبيرة
    result_data = [[pdf_gen._ar("⚖️ الوزن المُقدَّر"),
                    pdf_gen._ar(f"{result['weight_kg']:.1f} كجم")]]
    t_result = Table(result_data, colWidths=[245, 245])
    t_result.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#e8f5e9')),
        ('BOX', (0, 0), (-1, -1), 3, HexColor('#1b5e20')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 16),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15)]))
    story.append(t_result); story.append(Spacer(1, 20))

    story.append(P("🔬 التفاصيل العلمية", size=14, align=TA_RIGHT,
                   color='#1565c0'))
    story.append(Spacer(1, 8))
    details = [
        [pdf_gen._ar("المعادلة:"), pdf_gen._ar(result["formula"])],
        [pdf_gen._ar("المرجع:"), pdf_gen._ar(result["reference"])],
        [pdf_gen._ar("الدقة:"), pdf_gen._ar(result["confidence"])],
        [pdf_gen._ar("ملاحظات:"), pdf_gen._ar(result["note"] or "—")]]
    t_det = Table(details, colWidths=[150, 340])
    t_det.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#e3f2fd')),
        ('BACKGROUND', (1, 0), (1, -1), HexColor('#fafafa')),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#1976d2')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#bbdefb')),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
    story.append(t_det)

    doc.build(story, onFirstPage=pdf_gen._draw_page,
              onLaterPages=pdf_gen._draw_page)
    buffer.seek(0)
    return buffer.getvalue()


# ═══ القسم 12: تصدير Excel ═══
def export_comparison_to_excel(standard, calculated, requester_name="", animal="",
                                stage="", formula=None, standard_key=""):
    if not OPENPYXL_AVAILABLE: return b""
    wb = openpyxl.Workbook()
    ws = wb.active; ws.title = "مقارنة"; ws.sheet_view.rightToLeft = True
    hf = Font(name='Arial', size=12, bold=True, color='FFFFFF')
    hfill = PatternFill('solid', fgColor='1B5E20')
    tf = Font(name='Arial', size=14, bold=True, color='1B5E20')
    ct = Alignment(horizontal='center', vertical='center', wrap_text=True)
    rt = Alignment(horizontal='right', vertical='center', wrap_text=True)
    thin = Side(border_style='thin', color='9E9E9E')
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    ws.merge_cells('A1:F1'); ws['A1'] = f"{APP_NAME}"
    ws['A1'].font = tf; ws['A1'].alignment = ct
    ws.merge_cells('A2:F2'); ws['A2'] = f"🤲 {DUA_SHORT} 🤲"
    ws['A2'].font = Font(name='Arial', size=10, bold=True, color='C62828')
    ws['A2'].alignment = ct
    headers = ["العنصر", "المعيار", "المحسوب", "الفرق", "% الفرق", "التقييم"]
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=6, column=c, value=h)
        cell.font = hf; cell.fill = hfill; cell.alignment = ct; cell.border = bd
    labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم", "SE": "معادل النشاء",
              "NDF": "NDF", "ADF": "ADF", "EE": "دهن", "ASH": "رماد",
              "Ca": "كالسيوم", "P": "فسفور"}
    row = 7
    for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
        if k not in standard: continue
        sv = standard[k]; cv = calculated.get(k, 0.0)
        diff = cv - sv; pct = (diff / sv * 100) if sv else 0
        ev = evaluate_difference(pct)
        vals = [labels[k], round(sv, 2), round(cv, 2), round(diff, 3),
                round(pct, 2), ev["label"]]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.alignment = ct; cell.border = bd
            cell.fill = PatternFill('solid', fgColor=ev["bg"].replace('#', ''))
        row += 1
    for c in range(1, 7):
        ws.column_dimensions[get_column_letter(c)].width = 22
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return buf.getvalue()


# ═══ القسم 13: السوق والأسعار ═══
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
        "ذرة صفراء": 230, "شعير مطحون": 210, "قمح محلي": 240,
        "أمباز الفول السوداني": 460, "كسب فول صويا 44%": 440,
        "كسب عباد الشمس 36%": 310, "نخالة قمح (ردة)": 150,
        "البرسيم الجاف": 170, "مولاس قصب السكر": 120,
        "مسحوق أسماك 60%": 850, "الحجر الجيري": 40,
        "فوسفات ثنائي الكالسيوم": 280, "ملح الطعام": 30,
        "بيكربونات الصوديوم": 340, "مضاد سموم فطرية": 950,
        "بريمكس تسمين دواجن": 4800, "بريمكس مجترات": 4500,
        "ليسين نقي": 4200, "ميثيونين نقي": 5800,
        "زيت ذرة": 1500, "زيت فول الصويا": 1350, "زيت عباد الشمس": 1300,
        "زيت النخيل": 1100, "زيت جوز الهند": 1900,
        "شحم حيواني (Tallow)": 900, "دهن الدجاج": 800,
        "زيت السمك (Fish Oil)": 3800,
        "مركز تسمين 30% بروتين": 2200,
        "مركز تسمين 35% بروتين": 2500,
        "مركز تسمين 40% بروتين": 2800,
        "مركز حلابة 30% بروتين": 2300,
        "مركز حلابة 35% بروتين": 2600,
        "مركز أغنام 30% بروتين": 2100,
        "مركز أغنام 35% بروتين": 2400,
        "مركز ماعز 30% بروتين": 2100,
        "مركز دواجن بادئ 40%": 3200,
        "مركز دواجن نامي 35%": 2800,
        "مركز دواجن ناهي 30%": 2400,
        "مركز بياض 30% بروتين": 2500,
        "مركز إبل 30% بروتين": 2300,
        "مركز أسماك 35% بروتين": 3400})
    m = 1.0
    if country == "السودان":
        m = 1.15
        if "كردفان" in state: m = 1.20
    elif country == "LIBYA": m = 1.10
    elif country == "مصر": m = 1.04
    elif country == "السعودية": m = 1.08
    elif country == "الإمارات": m = 1.12
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


# ═══ القسم 14: حاسبة العليقة اليومية ═══
@dataclass
class DailyFeedPlan:
    animal_type: str
    weight_kg: float
    production_type: str
    dmi_kg: float
    dmi_pct_bw: float
    feed_kg: float
    meals_per_day: int
    feed_per_meal_kg: float
    water_liters: float
    num_animals: int
    total_feed_kg: float
    total_dmi_kg: float
    total_water_liters: float
    energy_note: str = ""
    protein_note: str = ""
    notes: str = ""


DMI_PERCENTAGES = {
    "أبقار": {"صيانة": (2.0, 2.2, "NRC 2001"),
              "حليب_عالي": (3.5, 4.0, "NRC 2001"),
              "حليب_متوسط": (3.0, 3.5, "NRC 2001"),
              "حليب_منخفض": (2.5, 3.0, "NRC 2001"),
              "تسمين_مكثف": (2.8, 3.2, "NRC 2001"),
              "تسمين_عادي": (2.4, 2.8, "NRC 2001"),
              "حمل_أخير": (2.0, 2.3, "NRC 2001"),
              "نمو": (2.5, 3.0, "NRC 2001")},
    "أغنام": {"صيانة": (2.0, 2.5, "NRC 2007"),
              "تسمين_مكثف": (3.5, 4.5, "NRC 2007"),
              "تسمين_عادي": (3.0, 3.8, "NRC 2007"),
              "حملان_تيد": (2.8, 3.5, "NRC 2007"),
              "مرضعات": (4.0, 5.0, "NRC 2007"),
              "حامل_أخير": (2.5, 3.0, "NRC 2007"),
              "حامل_متوسط": (2.2, 2.8, "NRC 2007"),
              "نمو": (3.0, 4.0, "NRC 2007")},
    "ماعز": {"صيانة": (2.0, 2.5, "NRC 2007"),
             "تسمين_جديان": (3.5, 4.5, "NRC 2007"),
             "تيوس": (2.8, 3.5, "NRC 2007"),
             "حلابة_عالي": (4.0, 5.0, "NRC 2007"),
             "حلابة_متوسط": (3.5, 4.2, "NRC 2007"),
             "حامل_أخير": (2.5, 3.0, "NRC 2007"),
             "نمو": (3.0, 4.0, "NRC 2007")},
    "إبل": {"صيانة": (1.5, 2.0, "FAO 2010"),
            "نمو": (2.5, 3.0, "FAO 2010"),
            "تسمين": (2.0, 2.5, "FAO 2010"),
            "حليب": (2.5, 3.0, "FAO 2010"),
            "سباق": (2.5, 3.5, "FAO 2010")},
    "خيول": {"صيانة": (1.8, 2.2, "NRC 2007"),
             "رياضة_مكثف": (3.0, 3.5, "NRC 2007"),
             "رياضة_عادي": (2.3, 2.8, "NRC 2007"),
             "نمو_أمهار": (2.5, 3.0, "NRC 2007"),
             "مرضعات": (3.0, 3.5, "NRC 2007")},
    "دواجن": {"بادي": (0.0, 0.0, "Ross 308"),
              "نامي": (0.0, 0.0, "Ross 308"),
              "ناهي": (0.0, 0.0, "Ross 308"),
              "بياض": (0.0, 0.0, "NRC 1994")},
    "سمان": {"بادي": (0.0, 0.0, "NRC Quail"),
             "نامي": (0.0, 0.0, "NRC Quail"),
             "ناهي": (0.0, 0.0, "NRC Quail"),
             "بياض": (0.0, 0.0, "NRC Quail")},
    "أسماك": {"بادئ زريعة": (5.0, 8.0, "NRC Fish"),
              "نمو": (3.0, 5.0, "NRC Fish"),
              "تسمين": (1.5, 3.0, "NRC Fish")},
}


POULTRY_DAILY_INTAKE_G = {
    "دواجن": {"بادي": {"min": 18, "max": 28, "typical": 23},
              "نامي": {"min": 60, "max": 95, "typical": 78},
              "ناهي": {"min": 140, "max": 200, "typical": 170},
              "بياض": {"min": 105, "max": 125, "typical": 115}},
    "سمان": {"بادي": {"min": 12, "max": 20, "typical": 16},
             "نامي": {"min": 20, "max": 28, "typical": 24},
             "ناهي": {"min": 25, "max": 32, "typical": 28},
             "بياض": {"min": 25, "max": 32, "typical": 28}},
}

MEALS_PER_DAY = {"أبقار": 3, "أغنام": 2, "ماعز": 2, "إبل": 2, "خيول": 3,
                 "دواجن": 4, "سمان": 3, "أسماك": 4}


def calculate_daily_feed_intake(animal_type, weight_kg, production_type="صيانة",
                                  milk_yield=0.0, adg_kg=0.0, age_weeks=0,
                                  num_animals=1, feed_dm_pct=88.0):
    if weight_kg <= 0 or num_animals < 1:
        return None
    std_table = DMI_PERCENTAGES.get(animal_type, {})
    if production_type not in std_table:
        return None
    dmi_min_pct, dmi_max_pct, ref = std_table[production_type]
    dmi_pct = (dmi_min_pct + dmi_max_pct) / 2.0
    if animal_type in ["أبقار", "أغنام", "ماعز", "إبل"]:
        if milk_yield > 0: dmi_pct += milk_yield * 0.003
        if adg_kg > 0: dmi_pct += adg_kg * 0.15
    if animal_type in ["دواجن", "سمان"]:
        pt = POULTRY_DAILY_INTAKE_G.get(animal_type, {})
        if production_type in pt:
            intake_g = pt[production_type]["typical"]
            if animal_type == "دواجن" and production_type == "نامي" and age_weeks >= 2:
                intake_g += (age_weeks - 2) * 3.5
            dmi_kg = intake_g / 1000.0
            dmi_pct = (dmi_kg / max(weight_kg, 0.05)) * 100 if weight_kg > 0.05 else 0
        else:
            return None
    else:
        dmi_kg = weight_kg * (dmi_pct / 100.0)

    if feed_dm_pct <= 0 or feed_dm_pct > 100:
        feed_dm_pct = 88.0
    feed_kg = dmi_kg / (feed_dm_pct / 100.0)
    meals = MEALS_PER_DAY.get(animal_type, 2)
    feed_per_meal = feed_kg / meals

    water_per_dmi = {"أبقار": 4.5, "أغنام": 3.5, "ماعز": 3.5, "إبل": 2.8,
                     "خيول": 3.0, "دواجن": 2.0, "سمان": 2.2, "أسماك": 0.0}
    if animal_type == "أسماك":
        water_liters = 0.0
    else:
        water_liters = dmi_kg * water_per_dmi.get(animal_type, 3.5)
        if milk_yield > 0: water_liters += milk_yield * 0.9

    energy_note = ""; protein_note = ""
    if animal_type == "أبقار":
        if "حليب" in production_type:
            protein_note = f"استهدف DP ≥ {12.5 + milk_yield*0.3:.1f}%"
            energy_note = f"SE ≥ {55 + milk_yield*0.35:.0f} وحدة"
        elif "تسمين" in production_type:
            protein_note = f"استهدف DP ≥ {9.5 + adg_kg*3:.1f}%"
    elif animal_type in ["أغنام", "ماعز"]:
        if production_type == "مرضعات" or "حلابة" in production_type:
            protein_note = f"استهدف DP ≥ {10.5 + milk_yield*0.4:.1f}%"

    return DailyFeedPlan(
        animal_type=animal_type, weight_kg=weight_kg,
        production_type=production_type,
        dmi_kg=round(dmi_kg, 3), dmi_pct_bw=round(dmi_pct, 2),
        feed_kg=round(feed_kg, 3), meals_per_day=meals,
        feed_per_meal_kg=round(feed_per_meal, 3),
        water_liters=round(water_liters, 2),
        num_animals=num_animals,
        total_feed_kg=round(feed_kg * num_animals, 2),
        total_dmi_kg=round(dmi_kg * num_animals, 2),
        total_water_liters=round(water_liters * num_animals, 1),
        energy_note=energy_note, protein_note=protein_note, notes=ref)


PRODUCTION_TYPE_LABELS = {
    "صيانة": "🌿 صيانة", "حليب_عالي": "🥛 حلابة عالية",
    "حليب_متوسط": "🥛 حلابة متوسطة", "حليب_منخفض": "🥛 حلابة منخفضة",
    "تسمين_مكثف": "💪 تسمين مكثف", "تسمين_عادي": "💪 تسمين عادي",
    "حمل_أخير": "🤰 حمل آخر", "نمو": "📈 نمو",
    "تسمين": "💪 تسمين", "حليب": "🥛 حلابة", "سباق": "🏃 سباق",
    "تسمين_جديان": "💪 تسمين جديان", "تيوس": "🐐 تيوس",
    "حلابة_عالي": "🥛 حلابة إدرار عالي",
    "حلابة_متوسط": "🥛 حلابة إدرار متوسط",
    "مرضعات": "🍼 مرضعات", "حامل_أخير": "🤰 حامل",
    "حامل_متوسط": "🤰 حامل مبكر", "حملان_تيد": "🐑 حملان تيد",
    "رياضة_مكثف": "🏇 رياضة مكثف", "رياضة_عادي": "🏇 رياضة عادي",
    "نمو_أمهار": "🐎 أمهار نمو",
    "بادي": "🐣 بادي (1-7 يوم)", "نامي": "🐤 نامي (8-21 يوم)",
    "ناهي": "🐔 ناهي (22-42 يوم)", "بياض": "🥚 بياض إنتاجي",
    "بادئ زريعة": "🐟 بادئ زريعة", "تسمين نهائي": "🐟 تسمين نهائي",
}


def daily_feed_distribution(plan, formula):
    if not formula or not plan: return []
    rows = []
    for ing, pct in formula.items():
        per_animal_g = plan.feed_kg * (pct / 100.0) * 1000
        total_kg = plan.total_feed_kg * (pct / 100.0)
        rows.append({"المكوّن": ing, "النسبة %": f"{pct:.2f}%",
                     "لكل حيوان (جم/يوم)": f"{per_animal_g:.1f}",
                     "للقتيط (كجم/يوم)": f"{total_kg:.3f}"})
    return rows


# ═══ القسم 15: الحالة الأولية ═══
DEFAULTS = {
    "approved": False, "user_role": None,
    "active_formula": {},
    "active_stage_title": "إنتاج عام",
    "active_animal_img": ANIMAL_IMAGES["عام"],
    "computed_ton_cost": 280.0,
    "inventory": {},
    "shared_comments": f"• مرحباً بكم في {APP_NAME}\n• {DUA_SHORT}\n",
    "broiler_farms": {},
    "livestock_prices": {"عجول تسمين ($)": 1350.0, "ضأن محلي ($)": 180.0,
                          "ماعز نوبي ($)": 130.0, "إبل حاشي ($)": 1200.0,
                          "كتكوت لاحم ($)": 0.65, "دجاج بياض ($)": 5.50},
    "products_prices": {"كيلو لحم بقري ($)": 7.50, "كيلو لحم ضأن ($)": 9.00,
                        "كيلو لحم دجاج ($)": 3.80, "طبق بيض 30 ($)": 4.20,
                        "لتر حليب بقر ($)": 0.90},
    "barn_last_dims": None, "barn_gif": None, "barn_html": None,
    "daily_feed_plan": None,
    # ⬇️ مفاتيح الربط التلقائي
    "tape_to_calc_weight": {},   # قاموس: {نوع الحيوان: الوزن}
    "tape_autofill_flag": False, # إشارة لإعادة التعبئة
}

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


# ═══ القسم 16: CSS ═══
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');
* { font-family: 'Cairo', 'Amiri', sans-serif; color: #1a1a1a !important; }
html, body, [data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600");
    background-size: cover; background-position: center; background-attachment: fixed;
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
    0%, 100% { box-shadow: 0 15px 40px rgba(0,0,0,0.4), inset 0 0 30px rgba(212,175,55,0.2); }
    50% { box-shadow: 0 15px 40px rgba(0,0,0,0.5), inset 0 0 40px rgba(212,175,55,0.4); }
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
.dua-main-box {
    background: linear-gradient(135deg, #0d3011 0%, #1b5e20 25%, #2e7d32 50%, #1b5e20 75%, #0d3011 100%);
    background-size: 200% 200%;
    animation: duaGlow 4s ease-in-out infinite, gradientShift 12s ease infinite;
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
.dua-main-box * { color: white !important; position: relative; z-index: 2; }
.dua-main-box h3 { color: #d4af37 !important; font-size: 1.9rem;
    margin-bottom: 18px; font-weight: 900; }
.dua-main-box .names {
    display: inline-block;
    background: linear-gradient(90deg, rgba(212,175,55,0.15), rgba(212,175,55,0.35), rgba(212,175,55,0.15));
    background-size: 200% 100%; animation: shimmerText 4s linear infinite;
    font-size: 1.65rem; font-weight: 900; color: #ffeb3b !important;
    margin: 20px 0; padding: 16px 30px;
    border: 2px solid #d4af37; border-radius: 15px;
    font-family: 'Amiri', serif !important;
}
.dua-main-box p.quran {
    font-family: 'Amiri', serif !important;
    font-size: 1.2rem; color: #d4af37 !important;
    margin-top: 22px; padding: 18px 25px;
    background: rgba(0,0,0,0.25); border-radius: 12px;
    border-right: 5px solid #d4af37; border-left: 5px solid #d4af37;
}
.visitor-dua-banner {
    background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 50%, #ffe082 100%);
    padding: 20px 28px; border-radius: 18px;
    border: 3px solid #d4af37;
    margin: 22px 0; direction: rtl; text-align: center;
    box-shadow: 0 6px 25px rgba(0,0,0,0.15);
}
.visitor-dua-banner * { color: #4e342e !important; }
.visitor-dua-banner b { color: #c62828 !important; font-family: 'Amiri', serif !important; }
@keyframes fixedDuaGlow {
    0%, 100% { text-shadow: 0 0 8px rgba(255,235,59,0.6); }
    50% { text-shadow: 0 0 20px rgba(255,235,59,1), 0 0 30px rgba(212,175,55,0.8); }
}
.dua-fixed-banner {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32, #1b5e20, #0d3011);
    background-size: 200% 100%; animation: gradientShift 8s linear infinite;
    color: white !important; padding: 11px 20px; z-index: 9998;
    text-align: center; border-top: 3px solid #d4af37;
    font-family: 'Amiri', serif !important; font-size: 1.05rem; font-weight: bold;
    box-shadow: 0 -4px 25px rgba(0,0,0,0.4);
}
.dua-fixed-banner * { color: #ffeb3b !important; font-family: 'Amiri', serif !important; }
.section-title {
    color: #1b5e20 !important; border-right: 6px solid #2e7d32;
    padding: 12px 18px; text-align: right;
    font-size: 1.5rem; font-weight: bold;
    margin-top: 30px; margin-bottom: 20px;
    background: linear-gradient(to left, rgba(46,125,50,0.15), transparent);
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
}
.oil-info-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 18px; border-radius: 12px;
    border-right: 5px solid #e65100;
    margin-bottom: 18px; direction: rtl; text-align: right;
}
.profile-img-style {
    width: 150px; height: 150px; border-radius: 50%;
    object-fit: cover; border: 4px solid #d4af37;
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    display: block; margin: 0 auto;
}
.stButton > button {
    color: #1a1a1a !important;
    background-color: #e8f5e9 !important;
    border: 1px solid #2e7d32 !important;
    font-weight: bold !important;
}
.stButton > button:hover { background-color: #c8e6c9 !important; }
.mini-signature {
    position: fixed; left: 20px; bottom: 65px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important; padding: 9px 22px;
    font-size: 0.88rem; border-radius: 25px;
    z-index: 9997; direction: rtl; border: 2px solid #d4af37;
    font-weight: bold;
}
.mini-signature * { color: white !important; }
@media (max-width: 768px) {
    .main-box { padding: 14px; margin-bottom: 70px; }
    h1 { font-size: 1.35rem !important; }
    .dua-main-box { padding: 18px 12px; }
    .dua-main-box h3 { font-size: 1.15rem; }
    .dua-main-box .names { font-size: 1rem; padding: 10px 14px; }
    .dua-main-box p.quran { font-size: 0.9rem; }
    .section-title { font-size: 1.05rem; padding: 8px 12px; }
    .dua-fixed-banner { font-size: 0.8rem; padding: 8px 10px; }
}
</style>
""", unsafe_allow_html=True)


# ═══ القسم 17: بوابة الدخول ═══
if not st.session_state["approved"]:
    st.markdown(
        '<div class="main-box" style="max-width: 780px; margin: 30px auto; direction: rtl;">',
        unsafe_allow_html=True)
    st.markdown(f"""
    <div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <p style="font-size:1.1rem; color:#a5d6a7 !important; margin-bottom:12px;">
        نبدأ باسم الله، ونسألُه أن يتقبّلَ هذا العملَ صدقةً جاريةً عن:
        </p>
        <div class="names">🕊️ رحم الله والدي إسماعيل تاور وأختي ابتسام 🕊️</div>
        <p class="quran">{DUA_QURAN}</p>
        <p class="quran" style="margin-top:10px;">{DUA_VERSE}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 2px solid #d4af37; margin: 25px 0;'>",
                unsafe_allow_html=True)
    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        if img_base64:
            st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">',
                        unsafe_allow_html=True)
    with col_title:
        st.markdown(f"<h2 style='color:#2E7D32; text-align:right;'>🌾 {APP_NAME}</h2>",
                    unsafe_allow_html=True)
        st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.1rem;'>{APP_TAGLINE}</p>",
                    unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#c62828; text-align:right;'>{SUPERVISOR} — {SUPERVISOR_TITLE}</h4>",
                    unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#1b5e20; margin-top:20px;'>🔐 بوابة الدخول</h3>",
                unsafe_allow_html=True)
    col_owner, col_guest = st.columns(2)
    with col_owner:
        st.markdown("""<div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        padding: 20px; border-radius: 12px; border: 2px solid #2e7d32;
        text-align: center; margin-bottom: 10px;">
        <h4 style="color: #1b5e20;">👑 المالك</h4>
        <p style="font-size: 0.9rem; color: #555;">الدخول بكود خاص</p></div>""",
            unsafe_allow_html=True)
        owner_code = st.text_input("🔑 كود المالك:", type="password", key="owner_code")
        if st.button("👑 دخول المالك", type="primary", use_container_width=True):
            if owner_code.strip() == OWNER_CODE:
                st.session_state.update({"approved": True, "user_role": "owner"})
                st.rerun()
            else:
                st.error("❌ كود غير صحيح")
    with col_guest:
        st.markdown("""<div style="background: linear-gradient(135deg, #fff8e1, #ffecb3);
        padding: 20px; border-radius: 12px; border: 2px solid #d4af37;
        text-align: center; margin-bottom: 10px;">
        <h4 style="color: #e65100;">👥 زائر</h4>
        <p style="font-size: 0.9rem; color: #555;">دخول مجاني</p></div>""",
            unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True):
            st.session_state.update({"approved": True, "user_role": "guest"})
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ═══ القسم 18: الواجهة الرئيسية ═══
st.markdown('<div class="main-box">', unsafe_allow_html=True)
c1, c2 = st.columns([0.7, 0.3])
with c2:
    role_label = "المالك 👑" if is_owner() else "زائر 👥"
    st.markdown(f"<div style='text-align:left; padding:10px; background:#f5f5f5;"
                f"border-radius:10px;'>الحساب: <b>{role_label}</b></div>",
                unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k != "inventory":
                del st.session_state[k]
        st.session_state["approved"] = False
        st.rerun()
c3, c4 = st.columns([0.3, 0.7])
with c3:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">',
                    unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <h1 style='color: #0d3011; text-align:right; margin-bottom:0;
               font-weight: 900; font-size: 2.3rem;'>
    🌾 {APP_NAME}
    </h1>
    <p style='color: #1565C0; text-align:right; font-size: 1.25rem;'>
    {APP_TAGLINE}</p>
    <div style='background: linear-gradient(135deg, #fff8e1, #ffe082);
                padding: 12px 20px; border-radius: 12px;
                border-right: 6px solid #c62828; border-left: 6px solid #c62828;'>
        <h3 style='color: #b71c1c; text-align:right; margin: 0;
                   font-weight: 900; font-size: 1.55rem;'>👨‍🔬 {SUPERVISOR}</h3>
        <p style='color: #0d47a1; text-align:right; margin: 5px 0 0 0;'>✨ {SUPERVISOR_TITLE}</p>
    </div>
    """, unsafe_allow_html=True)
st.markdown(f'<div class="visitor-dua-banner">{DUA_VISITOR_BANNER}</div>',
            unsafe_allow_html=True)
st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)


# ═══ القسم 19: التبويبات ═══
if is_owner():
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "⚖️ حاسبة العليقة وقياس الوزن",
        "🌰 مكتبة الزيوت",
        "🏭 مكتبة المركزات",
        "🍼 بدائل الحليب",
        "📷 المختبر الذكي",
        "🏗️ تصميم الحظائر 3D",
        "📊 البورصة",
        "🏭 المستودعات",
        "🧾 الفواتير",
        "🖨️ الديباجة",
        "📈 التحليلات",
        "🐔 مزارع الدجاج",
        "💬 التعليقات",
        "📚 المراجع",
        "💡 المساعدة",
    ]
else:
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "⚖️ حاسبة العليقة وقياس الوزن",
        "🌰 مكتبة الزيوت",
        "🏭 مكتبة المركزات",
        "🍼 بدائل الحليب",
        "📷 المختبر الذكي",
        "📚 المراجع",
        "💡 المساعدة",
    ]

tabs = st.tabs(tabs_titles)
tab_map = {title: tab for title, tab in zip(tabs_titles, tabs)}


# ═══ القسم 20: تبويب النمذجة ═══
with tab_map["🔬 النمذجة والحسابات العلفية"]:
    sub_tab_formulator, sub_tab_analyzer = st.tabs([
        "🎯 تركيب علفة نموذجية",
        "🔬 مختبر تحليل الأعلاف الجاهزة"])

    with sub_tab_formulator:
        st.markdown('<div class="section-title">🌍 الموقع الجغرافي</div>',
                    unsafe_allow_html=True)
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            country = st.selectbox("🌍 الدولة:", list(EXCHANGE_RATES.keys()),
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
            ["البروتين المهضوم (DP)", "البروتين الخام (CP)"],
            horizontal=True, key="protein_basis")
        use_dp = "DP" in protein_basis_choice

        st.markdown('<div class="section-title">🐾 اختر الحيوان</div>',
                    unsafe_allow_html=True)
        animal_tabs = st.tabs([
            "🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐪 إبل",
            "🐎 خيول", "🐔 دواجن", "🦆 سمان", "🐟 أسماك"])

        animal_choice = None; production_type = None
        requirement = None; img_key = "عام"; std_key_global = ""

        with animal_tabs[0]:
            st.markdown("### 🐄 احتياجات الأبقار")
            cattle_type = st.selectbox("الحالة:",
                ["حليب_عالي", "حليب_متوسط", "حليب_منخفض",
                 "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"],
                format_func=lambda x: PRODUCTION_TYPE_LABELS.get(x, x),
                key="cattle_type")
            c1_, c2_ = st.columns(2)
            cattle_params = {}
            with c1_:
                if "حليب" in cattle_type:
                    cattle_params["milk_yield"] = st.number_input(
                        "🥛 إنتاج الحليب (كجم):", 5.0, 60.0, 20.0, 1.0,
                        key="cattle_milk")
                cattle_params["weight_kg"] = st.number_input(
                    "⚖️ الوزن (كجم):", 200.0, 900.0, 500.0, 25.0, key="cattle_wt")
            with c2_:
                req_pre = get_cattle_requirements(cattle_type, **cattle_params)
                st.metric("🧬 DP", f"{req_pre.DP}%")
                st.metric("🧬 CP", f"{req_pre.CP}%")
                st.metric("🌽 SE", f"{req_pre.SE}")
            if st.checkbox("✅ اعتماد", key="use_cattle"):
                animal_choice = "أبقار"; production_type = cattle_type
                requirement = req_pre; img_key = "أبقار"
                std_key_global = f"أبقار_{cattle_type}"

        with animal_tabs[1]:
            st.markdown("### 🐏 احتياجات الأغنام")
            sg = st.radio("الجنس:", ["ذكر", "أنثى"], horizontal=True, key="sheep_g")
            is_male_s = sg == "ذكر"
            if is_male_s:
                sheep_type = st.selectbox("الحالة:",
                    ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد"],
                    format_func=lambda x: PRODUCTION_TYPE_LABELS.get(x, x),
                    key="sheep_t_m")
            else:
                sheep_type = st.selectbox("الحالة:",
                    ["مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
                    format_func=lambda x: PRODUCTION_TYPE_LABELS.get(x, x),
                    key="sheep_t_f")
            litter = 1
            if sheep_type == "مرضعات":
                litter = st.number_input("👶 المواليد:", 1, 3, 1, key="sh_l")
            req_pre = get_sheep_requirements(sheep_type, is_male=is_male_s,
                                              litter_size=litter)
            p1, p2, p3 = st.columns(3)
            p1.metric("DP", f"{req_pre.DP}%"); p2.metric("CP", f"{req_pre.CP}%")
            p3.metric("SE", f"{req_pre.SE}")
            if st.checkbox("✅ اعتماد", key="use_sheep"):
                animal_choice = "أغنام"; production_type = sheep_type
                requirement = req_pre; img_key = "أغنام"
                std_key_global = f"أغنام_{sheep_type}"

        with animal_tabs[2]:
            st.markdown("### 🐐 احتياجات الماعز")
            gg = st.radio("الجنس:", ["ذكر", "أنثى"], horizontal=True, key="goat_g")
            is_male_g = gg == "ذكر"
            milk_g = 0
            if is_male_g:
                goat_type = st.selectbox("الحالة:",
                    ["تسمين_جديان", "تيوس"],
                    format_func=lambda x: PRODUCTION_TYPE_LABELS.get(x, x),
                    key="goat_t_m")
            else:
                goat_type = st.selectbox("الحالة:",
                    ["حلابة_عالي", "حلابة_متوسط", "حامل_أخير", "صيانة"],
                    format_func=lambda x: PRODUCTION_TYPE_LABELS.get(x, x),
                    key="goat_t_f")
                if "حلابة" in goat_type:
                    milk_g = st.number_input("🥛 الحليب (كجم):", 0.5, 8.0, 2.0,
                                              0.25, key="goat_milk")
            req_pre = get_goat_requirements(goat_type, is_male=is_male_g,
                                             milk_yield=milk_g)
            p1, p2, p3 = st.columns(3)
            p1.metric("DP", f"{req_pre.DP}%"); p2.metric("CP", f"{req_pre.CP}%")
            p3.metric("SE", f"{req_pre.SE}")
            if st.checkbox("✅ اعتماد", key="use_goat"):
                animal_choice = "ماعز"; production_type = goat_type
                requirement = req_pre; img_key = "ماعز"
                std_key_global = f"ماعز_{goat_type}"

        with animal_tabs[3]:
            st.markdown("### 🐪 احتياجات الإبل")
            camel_type = st.selectbox("الحالة:",
                ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
                format_func=lambda x: PRODUCTION_TYPE_LABELS.get(x, x),
                key="camel_type")
            camel_wt = st.number_input("الوزن (كجم):", 100.0, 800.0, 400.0,
                                        25.0, key="camel_wt")
            camel_milk = 5.0
            if camel_type == "حليب":
                camel_milk = st.number_input("🥛 الحليب (لتر):", 2.0, 20.0,
                                              5.0, 0.5, key="camel_milk")
            req_pre = get_camel_requirements(camel_type, weight_kg=camel_wt,
                                               milk_yield=camel_milk)
            p1, p2, p3, p4 = st.columns(4)
            p1.metric("DP", f"{req_pre.DP}%"); p2.metric("CP", f"{req_pre.CP}%")
            p3.metric("SE", f"{req_pre.SE}"); p4.metric("NDF", f"{req_pre.NDF}%")
            if st.checkbox("✅ اعتماد", key="use_camel"):
                animal_choice = "إبل"; production_type = camel_type
                requirement = req_pre; img_key = "إبل"
                std_key_global = f"إبل_{camel_type}"

        with animal_tabs[4]:
            st.markdown("### 🐎 احتياجات الخيول")
            horse_type = st.selectbox("الحالة:",
                ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار", "مرضعات", "صيانة"],
                format_func=lambda x: PRODUCTION_TYPE_LABELS.get(x, x),
                key="horse_type")
            req_pre = get_horse_requirements(horse_type)
            p1, p2, p3 = st.columns(3)
            p1.metric("DP", f"{req_pre.DP}%"); p2.metric("CP", f"{req_pre.CP}%")
            p3.metric("SE", f"{req_pre.SE}")
            if st.checkbox("✅ اعتماد", key="use_horse"):
                animal_choice = "خيول"; production_type = horse_type
                requirement = req_pre; img_key = "خيول"
                std_key_global = f"خيول_{horse_type}"

        with animal_tabs[5]:
            st.markdown("### 🐔 احتياجات الدواجن")
            poultry_strain = st.radio("السلالة:", ["لاحم", "بياض"],
                                        horizontal=True, key="poultry_strain")
            poultry_age = st.number_input("العمر (أسبوع):", 1, 20, 1, key="poultry_age")
            req_pre = get_poultry_requirements(poultry_strain, poultry_age)
            p1, p2, p3, p4 = st.columns(4)
            p1.metric("DP", f"{req_pre.DP}%"); p2.metric("CP", f"{req_pre.CP}%")
            p3.metric("SE", f"{req_pre.SE}"); p4.metric("Ca", f"{req_pre.Ca}%")
            if st.checkbox("✅ اعتماد", key="use_poultry"):
                animal_choice = "دواجن"; production_type = poultry_strain
                requirement = req_pre; img_key = "دواجن"
                if "بادي" in req_pre.name_ar: std_key_global = "دواجن_بادي"
                elif "نامي" in req_pre.name_ar: std_key_global = "دواجن_نامي"
                elif "بياض" in req_pre.name_ar: std_key_global = "دواجن_بياض"
                else: std_key_global = "دواجن_ناهي"

        with animal_tabs[6]:
            st.markdown("### 🦆 احتياجات السمان")
            quail_strain = st.radio("النوع:", ["تسمين", "بياض"],
                                      horizontal=True, key="quail_strain")
            quail_age = st.number_input("العمر (أسبوع):", 1, 8, 1, key="quail_age")
            req_pre = get_quail_requirements(quail_strain, quail_age)
            p1, p2, p3 = st.columns(3)
            p1.metric("DP", f"{req_pre.DP}%"); p2.metric("CP", f"{req_pre.CP}%")
            p3.metric("SE", f"{req_pre.SE}")
            if st.checkbox("✅ اعتماد", key="use_quail"):
                animal_choice = "سمان"; production_type = quail_strain
                requirement = req_pre; img_key = "سمان"
                std_key_global = "سمان_بياض" if quail_strain == "بياض" else "سمان_بادي"

        with animal_tabs[7]:
            st.markdown("### 🐟 احتياجات الأسماك")
            fish_species = st.selectbox("النوع:",
                ["البلطي النيلي", "القرموط الأفريقي", "الكارب"], key="fish_sp")
            fish_stage = st.selectbox("المرحلة:",
                ["بادئ زريعة", "نمو", "تسمين"], key="fish_stage")
            req_pre = get_fish_requirements(fish_species, fish_stage)
            p1, p2, p3 = st.columns(3)
            p1.metric("DP", f"{req_pre.DP}%"); p2.metric("CP", f"{req_pre.CP}%")
            p3.metric("SE", f"{req_pre.SE}")
            if st.checkbox("✅ اعتماد", key="use_fish"):
                animal_choice = "أسماك"; production_type = fish_stage
                requirement = req_pre; img_key = "أسماك"
                if "بادئ" in fish_stage: std_key_global = "أسماك_بادئ"
                elif "نمو" in fish_stage: std_key_global = "أسماك_نمو"
                else: std_key_global = "أسماك_تسمين"

        formulation_ready = bool(animal_choice and requirement)

        if not formulation_ready:
            st.warning("⚠️ اختر حيواناً وفعّل ✅ الاعتماد")
        else:
            st.markdown(f'<div class="section-title">🎯 المختار: {animal_choice} — {requirement.name_ar}</div>',
                        unsafe_allow_html=True)
            info_col1, info_col2, info_col3, info_col4 = st.columns(4)
            info_col1.metric("DP", f"{requirement.DP}%")
            info_col2.metric("CP", f"{requirement.CP}%")
            info_col3.metric("SE", f"{requirement.SE}")
            info_col4.metric("NDF", f"{requirement.NDF}%")

            oil_std_info = get_oil_standard(std_key_global)
            st.markdown(f"""
            <div class="oil-info-card">
            <b>📊 حدود الزيوت:</b><br>
            ▪️ الحد الأقصى: <b>{oil_std_info['max']}%</b> |
            المثالي: <b>{oil_std_info['optimal']}%</b><br>
            ▪️ المرجع: <b>{oil_std_info['source']}</b>
            </div>""", unsafe_allow_html=True)

            requester_name = st.text_input("👤 اسم طالب العلفة:",
                key="requester")

            st.markdown('<div class="section-title">🌾 اختيار المكونات</div>',
                        unsafe_allow_html=True)
            selected_ingredients = []
            ingredient_prices = {}

            for cat_name, items in BIG_FEEDS_LIBRARY.items():
                is_expanded = ("الحبوب" in cat_name or "الأكساب" in cat_name
                               or "الزيوت" in cat_name or "المركزات" in cat_name)
                with st.expander(f"📁 {cat_name}", expanded=is_expanded):
                    sub_cols = st.columns(3)
                    for idx, (ing_name, ing_data) in enumerate(items.items()):
                        with sub_cols[idx % 3]:
                            default_check = ing_name in [
                                "ملح الطعام", "الحجر الجيري",
                                "فوسفات ثنائي الكالسيوم", "مضاد سموم فطرية"]
                            if animal_choice in ["أغنام", "ماعز", "أبقار", "إبل"]:
                                default_check = default_check or (
                                    ing_name == "بيكربونات الصوديوم")
                            if animal_choice in ["دواجن", "سمان"]:
                                default_check = default_check or ("بريمكس" in ing_name)

                            if cat_name == "🌰 الزيوت النباتية والحيوانية":
                                st.markdown(f"**{ing_name}**")
                                checked = st.checkbox("إضافة", value=False,
                                    key=f"feed_{animal_choice}_{ing_name}")
                            else:
                                checked = st.checkbox(ing_name,
                                    value=default_check,
                                    key=f"feed_{animal_choice}_{ing_name}")

                            current_live_price = live_prices.get(ing_name, 350.0)
                            if is_owner():
                                price_input = st.number_input(
                                    f"السعر ($/طن):", min_value=5.0,
                                    value=float(current_live_price),
                                    key=f"price_{animal_choice}_{ing_name}")
                            else:
                                st.markdown(f"💰 `${current_live_price:.0f}/طن`")
                                price_input = current_live_price

                            if checked:
                                selected_ingredients.append(ing_name)
                                ingredient_prices[ing_name] = price_input

            st.markdown("---")
            if st.button("🚀 تشغيل المحرك الذكي", type="primary",
                         use_container_width=True, key="run_smart"):
                if len(selected_ingredients) < 3:
                    st.error("⚠️ اختر 3 مكونات على الأقل")
                else:
                    auto_salts = auto_add_salts_and_minerals(animal_choice, requirement)
                    for sname, spct in auto_salts.items():
                        if sname not in selected_ingredients:
                            selected_ingredients.append(sname)
                            ingredient_prices[sname] = live_prices.get(sname, 300.0)

                    custom_standard = requirement_to_standard(requirement)
                    basis_label = "DP" if use_dp else "CP"
                    selected_oils = [ing for ing in selected_ingredients
                                     if ing in get_oil_ingredients()]

                    with st.spinner("⏳ جاري التركيب..."):
                        result = auto_formulate_smart(
                            selected_ingredients, ingredient_prices,
                            custom_standard, standard_key=std_key_global,
                            tolerance=0.3, max_iterations=50,
                            required_oils=selected_oils)

                    if result["success"]:
                        formula = result["formula"]
                        actual = result["actual_nutrients"]
                        cost = result["cost"]
                        total_oil = result.get("total_oil", 0.0)
                        oil_std = result.get("oil_std", oil_std_info)

                        compare_rows = []; compare_scores = []
                        labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم",
                                  "SE": "معادل النشاء", "NDF": "NDF",
                                  "ADF": "ADF", "EE": "دهن", "ASH": "رماد",
                                  "Ca": "Ca", "P": "P"}
                        for k, sv in custom_standard.items():
                            cv = actual.get(k, 0.0); diff = cv - sv
                            pct = (diff / sv * 100) if sv else 0
                            ev = evaluate_difference(pct)
                            compare_scores.append({"score": ev["score"]})
                            compare_rows.append({"العنصر": labels.get(k, k),
                                "المعيار": f"{sv:.2f}", "المحسوب": f"{cv:.2f}",
                                "الفرق": f"{diff:+.3f}",
                                "الفرق %": f"{pct:+.2f}%",
                                "التقييم": ev["label"]})
                        overall = get_overall_rating(compare_scores)
                        st.success(f"✅ تم التركيب — التقييم: {overall['label']}")
                        st.dataframe(pd.DataFrame(compare_rows),
                                     use_container_width=True, hide_index=True)

                        st.markdown("#### 🌾 المكونات:")
                        for ing, pct in formula.items():
                            st.markdown(
                                f'<div class="formula-item">▪️ <b>{ing}:</b> '
                                f'{pct:.2f}% ({pct*10:.1f} كجم/طن)</div>',
                                unsafe_allow_html=True)
                        st.metric("💰 التكلفة للطن:",
                                  f"${cost:.2f} ({cost*local_rate:,.0f} {local_sym})")

                        st.session_state["active_formula"] = formula
                        st.session_state["computed_ton_cost"] = cost
                        st.session_state["active_stage_title"] = (
                            f"{animal_choice} — {requirement.name_ar}")

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
                                standard_key=std_key_global, include_charts=True)
                            st.download_button("📥 تحميل PDF",
                                pdf, file_name=f"Formula_{datetime.now():%Y%m%d}.pdf",
                                mime="application/pdf", use_container_width=True)
                        except Exception as e:
                            st.error(f"PDF: {e}")
                    else:
                        st.error(f"❌ {result['message']}")

    # ═══════════════════════════════════════════════════════════════
    # مختبر تحليل الأعلاف الجاهزة (مع المقارنة + PDF + رسم بياني)
    # ═══════════════════════════════════════════════════════════════
    with sub_tab_analyzer:
        st.markdown('<div class="section-title">🔬 مختبر فحص الأعلاف الجاهزة</div>',
                    unsafe_allow_html=True)
        st.write("أدخل أوزان مكونات خلطتك، وسيتم تحليلها ومقارنتها بالمعايير القياسية.")

        col_lab_a, col_lab_s = st.columns(2)
        with col_lab_a:
            target_animal = st.selectbox("الفصيل:",
                ["أبقار", "أغنام", "ماعز", "خيول", "إبل",
                 "دواجن لاحم", "دواجن بياض", "سمان", "أسماك"],
                key="lab_target_animal")
        with col_lab_s:
            if target_animal in ["أبقار", "أغنام", "ماعز", "خيول", "إبل"]:
                production_type_lab = st.selectbox("مرحلة الإنتاج:",
                    ["تسمين", "حليب/إدرار", "حمل/دفع غذائي", "صيانة"],
                    key="lab_prod_rum")
            elif target_animal in ["دواجن لاحم", "دواجن بياض", "سمان"]:
                production_type_lab = st.selectbox("مرحلة الإنتاج:",
                    ["بادي", "نامي", "ناهي", "بياض"], key="lab_prod_poul")
            else:
                production_type_lab = st.selectbox("مرحلة الإنتاج:",
                    ["نمو", "تسمين نهائي"], key="lab_prod_fish")

        lab_requirement = get_lab_requirement(target_animal, production_type_lab)
        if lab_requirement:
            st.info(f"📊 المعيار للـ **{lab_requirement.name_ar}**: "
                    f"DP = **{lab_requirement.DP}%** | "
                    f"CP = **{lab_requirement.CP}%** | "
                    f"SE = **{lab_requirement.SE}**")

        lab_requester = st.text_input("👤 اسم الطالب:", key="lab_req_name")

        analysis_basis = st.radio("أساس التحليل:",
            ["بروتين مهضوم (DP)", "بروتين خام (CP)"],
            horizontal=True, key="lab_basis")
        suggested = (lab_requirement.DP if lab_requirement else 15.0) \
            if "DP" in analysis_basis else \
            (lab_requirement.CP if lab_requirement else 18.0)
        target_value = st.number_input("القيمة المستهدفة %:",
            min_value=5.0, max_value=50.0, value=float(suggested),
            step=0.1, key="lab_target_val")

        st.markdown("---")
        st.subheader("📥 أدخل أوزان المكونات (كجم):")
        lab_sel_cat = st.selectbox("اختر فئة المكونات:",
            ["الكل"] + list(BIG_FEEDS_LIBRARY.keys()), key="lab_cat")
        lab_user_inputs = {}
        all_lib = []
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            for ing_name in items.keys():
                all_lib.append((cat_name, ing_name))
        filtered = (all_lib if lab_sel_cat == "الكل"
                    else [(c, n) for c, n in all_lib if c == lab_sel_cat])

        cols = st.columns(3)
        for i, (cat, ing_name) in enumerate(filtered):
            with cols[i % 3]:
                lab_user_inputs[ing_name] = st.number_input(
                    f"{ing_name}:", min_value=0.0, value=0.0,
                    step=1.0, key=f"lab_in_{ing_name}")

        st.markdown("---")
        if st.button("🧪 تشغيل التحليل", type="primary",
                     use_container_width=True, key="lab_run"):
            lab_total_weight = sum(lab_user_inputs.values())
            if lab_total_weight <= 0:
                st.warning("⚠️ أدخل أوزاناً أكبر من الصفر")
            else:
                calc = {"CP": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0,
                        "ADF": 0.0, "EE": 0.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0}
                entered = {}
                for ing_name, weight in lab_user_inputs.items():
                    if weight > 0:
                        pct = weight / lab_total_weight
                        entered[ing_name] = weight
                        for cat, items in BIG_FEEDS_LIBRARY.items():
                            if ing_name in items:
                                d = items[ing_name]
                                calc["CP"] += pct * d.get("CP", 0)
                                calc["DP"] += pct * d.get("CP", 0) * d.get("DC", 0)
                                calc["SE"] += pct * d.get("SE", 0)
                                calc["NDF"] += pct * d.get("NDF", 0)
                                calc["ADF"] += pct * d.get("ADF", 0)
                                calc["EE"] += pct * d.get("EE", 0)
                                calc["ASH"] += pct * d.get("ASH", 0)
                                calc["Ca"] += pct * d.get("Ca", 0)
                                calc["P"] += pct * d.get("P", 0)
                                break

                st.success("🔬 تم الفحص بنجاح!")
                st.markdown(f"### ⚖️ الوزن الكلي: {lab_total_weight:.1f} كجم")

                st.write("#### 📊 المكونات:")
                st.dataframe(pd.DataFrame([
                    {"المادة": k, "الوزن (كجم)": f"{v:.1f}",
                     "النسبة %": f"{v / lab_total_weight * 100:.2f}%"}
                    for k, v in entered.items()]),
                    use_container_width=True, hide_index=True)

                if lab_requirement:
                    st.markdown("### 📊 المقارنة بالمعايير القياسية")
                    std = requirement_to_standard(lab_requirement)
                    labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم",
                              "SE": "معادل النشاء", "NDF": "NDF",
                              "ADF": "ADF", "EE": "دهن", "ASH": "رماد",
                              "Ca": "Ca", "P": "P"}
                    comp_rows = []; scores = []
                    for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
                        if k not in std: continue
                        sv = std[k]; cv = calc.get(k, 0.0); diff = cv - sv
                        pct = (diff / sv * 100) if sv else 0
                        ev = evaluate_difference(pct)
                        scores.append({"score": ev["score"]})
                        comp_rows.append({"العنصر": labels.get(k, k),
                            "المعيار": f"{sv:.2f}", "المحسوب": f"{cv:.2f}",
                            "الفرق": f"{diff:+.3f}",
                            "الفرق %": f"{pct:+.2f}%",
                            "التقييم": ev["label"]})
                    st.dataframe(pd.DataFrame(comp_rows),
                                 use_container_width=True, hide_index=True)

                    overall = get_overall_rating(scores)
                    m1, m2 = st.columns(2)
                    m1.metric("🎯 التقييم العام", overall["label"])
                    m2.metric("📈 المتوسط", f"{overall['score']:.0f}%")

                    # رسوم بيانية
                    fig1 = create_lab_comparison_chart(calc, std)
                    if fig1:
                        st.plotly_chart(fig1, use_container_width=True)
                    fig2 = create_lab_radar_chart(calc, std)
                    if fig2:
                        st.plotly_chart(fig2, use_container_width=True)

                # تحميل PDF
                try:
                    pdf_bytes = generate_lab_analysis_pdf(
                        animal_label=target_animal,
                        stage_label=production_type_lab,
                        analysis_basis=analysis_basis,
                        target_value=target_value,
                        entered_components=entered,
                        calculated_nutrients=calc,
                        requirement=lab_requirement,
                        requester_name=lab_requester)
                    if pdf_bytes:
                        st.download_button("📥 تحميل تقرير المختبر (PDF)",
                            pdf_bytes,
                            file_name=f"Lab_{target_animal}_{datetime.now():%Y%m%d}.pdf",
                            mime="application/pdf",
                            use_container_width=True, type="primary")
                except Exception as e:
                    st.error(f"PDF: {e}")


# ═══ القسم 21: حاسبة العليقة + قياس الوزن (مع الربط التلقائي) ═══
with tab_map["⚖️ حاسبة العليقة وقياس الوزن"]:
    st.markdown('<div class="section-title">⚖️ قياس الوزن وحاسبة العليقة</div>',
                unsafe_allow_html=True)

    sub_tape, sub_calc = st.tabs([
        "📏 قياس الوزن بالشريط",
        "🍽️ حاسبة العليقة اليومية"])

    # ═══════════════════════════════════════════════
    # تبويب قياس الوزن بالشريط
    # ═══════════════════════════════════════════════
    with sub_tape:
        st.markdown('<div class="section-title">📏 تقدير وزن الحيوان بشريط القياس</div>',
                    unsafe_allow_html=True)
        st.write("أدخل قياسات الحيوان، وسيتم تقدير وزنه وفق معادلات عالمية "
                 "(Schaeffer / NRC 2007 / FAO 2010).")
        st.info("💡 **قياس محيط الصدر**: خلف الكتفين مباشرة. "
                "**الطول**: من بداية الكتف إلى عظم المؤخرة.")

        tp1, tp2 = st.columns(2)
        with tp1:
            tape_animal = st.selectbox("نوع الحيوان:",
                ["أبقار", "أغنام", "ماعز", "خيول", "إبل", "دواجن", "سمان"],
                key="tape_animal")
            tape_hg = st.number_input("📐 محيط الصدر (سم):",
                min_value=10.0, max_value=400.0,
                value={"أبقار": 180.0, "أغنام": 75.0, "ماعز": 70.0,
                       "خيول": 170.0, "إبل": 195.0,
                       "دواجن": 20.0, "سمان": 8.0}.get(tape_animal, 100.0),
                step=1.0, key="tape_hg")
        with tp2:
            tape_bl = st.number_input("📏 الطول (سم):",
                min_value=0.0, max_value=300.0,
                value={"أبقار": 140.0, "أغنام": 60.0, "ماعز": 55.0,
                       "خيول": 150.0, "إبل": 165.0}.get(tape_animal, 0.0),
                step=1.0, key="tape_bl",
                help="اتركه 0 إذا لم يتوفر")
            tape_bcs = st.slider("BCS (1 نحيف - 5 سمين):",
                min_value=1.0, max_value=5.0, value=3.0, step=0.25,
                key="tape_bcs")

        tape_requester = st.text_input("👤 اسم الطالب:", key="tape_req")

        if st.button("📏 احسب الوزن", type="primary",
                     use_container_width=True, key="tape_calc"):
            result = estimate_animal_weight_by_tape(
                tape_animal, tape_hg, tape_bl, tape_bcs)
            if result["weight_kg"] > 0:
                st.session_state["tape_result"] = result
                st.session_state["tape_animal_saved"] = tape_animal
                st.session_state["tape_hg_saved"] = tape_hg
                st.session_state["tape_bl_saved"] = tape_bl
                st.session_state["tape_bcs_saved"] = tape_bcs
                # ⬇️⬇️⬇️ الربط التلقائي: حفظ الوزن للنقل التلقائي
                st.session_state["tape_to_calc_weight"][tape_animal] = \
                    result["weight_kg"]
                st.session_state["tape_autofill_flag"] = True
            else:
                st.error("⚠️ تعذر الحساب")

        tape_result = st.session_state.get("tape_result")
        if tape_result and tape_result["weight_kg"] > 0:
            st.markdown("---")
            st.markdown(f"## 📊 الوزن المُقدَّر: "
                        f"**{tape_result['weight_kg']:.1f} كجم**")
            c1, c2, c3 = st.columns(3)
            c1.metric("⚖️ الوزن", f"{tape_result['weight_kg']:.1f} كجم")
            c2.metric("📖 المرجع", tape_result["reference"][:25])
            c3.metric("🎯 الدقة", tape_result["confidence"])

            with st.expander("🔬 التفاصيل العلمية", expanded=True):
                st.markdown(f"""
                - **المعادلة:** `{tape_result['formula']}`
                - **المرجع:** {tape_result['reference']}
                - **الدقة:** {tape_result['confidence']}
                - **ملاحظات:** {tape_result['note'] or '—'}
                """)

            st.markdown("#### 📚 معادلات التقدير المعتمدة")
            st.dataframe(pd.DataFrame([
                {"الحيوان": "أبقار", "المعادلة": "W = (HG² × BL) / 10838",
                 "المرجع": "Schaeffer (Cattle)"},
                {"الحيوان": "أغنام/ماعز", "المعادلة": "W = (HG² × BL) / 10838",
                 "المرجع": "Schaeffer (adapted)"},
                {"الحيوان": "خيول", "المعادلة": "W = (HG² × BL) / 11880",
                 "المرجع": "NRC 2007"},
                {"الحيوان": "إبل", "المعادلة": "W ≈ (HG² × BL) / 10000",
                 "المرجع": "FAO 2010"}]),
                use_container_width=True, hide_index=True)

            # ⬇️⬇️⬇️ زر الربط التلقائي
            st.markdown("---")
            st.markdown("### 🔗 الربط التلقائي مع الحاسبة")
            st.success(f"✅ تم حفظ الوزن تلقائياً **{tape_result['weight_kg']:.1f} كجم** "
                       f"لنوع **{tape_animal}**. "
                       "الآن انتقل لتبويب **«🍽️ حاسبة العليقة اليومية»** "
                       "ستجد الوزن مُعبّأً تلقائياً.")

            col_link1, col_link2 = st.columns(2)
            with col_link1:
                st.markdown(f"""
                <div style="background:#e8f5e9; padding:15px;
                border-radius:10px; border-right:4px solid #2e7d32;
                direction:rtl;">
                <b>📋 بيانات محفوظة:</b><br>
                ▪️ الحيوان: <b>{tape_animal}</b><br>
                ▪️ الوزن: <b>{tape_result['weight_kg']:.1f} كجم</b><br>
                ▪️ محيط الصدر: {st.session_state.get('tape_hg_saved', 0)} سم<br>
                ▪️ الطول: {st.session_state.get('tape_bl_saved', 0)} سم<br>
                ▪️ BCS: {st.session_state.get('tape_bcs_saved', 3)}
                </div>""", unsafe_allow_html=True)
            with col_link2:
                st.markdown("**جميع الأوزان المحفوظة:**")
                weights = st.session_state.get("tape_to_calc_weight", {})
                if weights:
                    for a, w in weights.items():
                        st.markdown(f"▪️ {a}: **{w:.1f} كجم**")
                else:
                    st.info("لا توجد أوزان محفوظة بعد")

            # تحميل PDF للوزن
            try:
                pdf_w = generate_tape_weight_pdf(
                    tape_animal, tape_hg, tape_bl, tape_bcs, tape_result,
                    requester_name=tape_requester)
                if pdf_w:
                    st.download_button("📥 تحميل تقرير الوزن (PDF)",
                        pdf_w,
                        file_name=f"Weight_{tape_animal}_{datetime.now():%Y%m%d}.pdf",
                        mime="application/pdf",
                        use_container_width=True, type="primary")
            except Exception as e:
                st.error(f"PDF: {e}")

    # ═══════════════════════════════════════════════
    # تبويب حاسبة العليقة اليومية
    # ═══════════════════════════════════════════════
    with sub_calc:
        st.markdown('<div class="section-title">🍽️ حاسبة العليقة اليومية</div>',
                    unsafe_allow_html=True)

        # ⬇️⬇️⬇️ عرض إشعار الربط التلقائي
        if st.session_state.get("tape_autofill_flag"):
            weights = st.session_state.get("tape_to_calc_weight", {})
            if weights:
                st.info(f"🔗 **الربط التلقائي مُفعَّل**: تم استيراد "
                        f"{len(weights)} وزن من تبويب قياس الشريط. "
                        f"اختر نوع الحيوان المناسب وسيُعبأ الوزن تلقائياً.")

        fp1, fp2, fp3 = st.columns(3)
        with fp1:
            fp_animal = st.selectbox("نوع الحيوان:",
                ["أبقار", "أغنام", "ماعز", "إبل", "خيول", "دواجن", "سمان", "أسماك"],
                key="fp_animal")

        # ⬇️⬇️⬇️ الوزن الافتراضي من القياس التلقائي
        saved_weights = st.session_state.get("tape_to_calc_weight", {})
        default_weight = saved_weights.get(fp_animal, {
            "أبقار": 500.0, "أغنام": 50.0, "ماعز": 45.0,
            "إبل": 450.0, "خيول": 450.0, "دواجن": 2.0,
            "سمان": 0.2, "أسماك": 0.5}.get(fp_animal, 50.0))

        with fp2:
            fp_weight = st.number_input("⚖️ الوزن الحي (كجم):",
                min_value=0.01, max_value=1500.0,
                value=float(default_weight),
                step=0.1 if fp_animal in ["دواجن", "سمان", "أسماك"] else 5.0,
                key=f"fp_weight_{fp_animal}")
            if fp_animal in saved_weights:
                st.caption(f"💡 الوزن مستورد تلقائياً من قياس الشريط "
                           f"({saved_weights[fp_animal]:.1f} كجم)")
        with fp3:
            fp_num = st.number_input("🔢 عدد الحيوانات:",
                min_value=1, max_value=100000, value=1, key="fp_num")

        std_options = list(DMI_PERCENTAGES.get(fp_animal, {}).keys())
        if not std_options:
            st.error("⚠️ لا توجد معايير لهذا الحيوان")
        else:
            fp2_cols = st.columns(3)
            with fp2_cols[0]:
                fp_prod = st.selectbox("الحالة:",
                    std_options,
                    format_func=lambda x: PRODUCTION_TYPE_LABELS.get(x, x),
                    key=f"fp_prod_{fp_animal}")
            with fp2_cols[1]:
                fp_milk = 0.0
                if any(k in fp_prod for k in ["حليب", "حلابة", "مرضعات"]):
                    fp_milk = st.number_input("🥛 الحليب (كجم):",
                        min_value=0.0, max_value=60.0, value=20.0, step=0.5,
                        key="fp_milk")
            with fp2_cols[2]:
                fp_adg = 0.0
                if "تسمين" in fp_prod or "نمو" in fp_prod:
                    fp_adg = st.number_input("📈 ADG (كجم):",
                        min_value=0.0, max_value=3.0,
                        value={"أبقار": 1.2, "أغنام": 0.25, "ماعز": 0.18,
                               "إبل": 0.8, "خيول": 0.5}.get(fp_animal, 0.2),
                        step=0.01, key="fp_adg")

            fp_age_weeks = 0
            if fp_animal in ["دواجن", "سمان"]:
                fp_age_weeks = st.number_input("📅 العمر (أسبوع):",
                    min_value=1, max_value=20, value=1, key="fp_age")

            fp_dm_pct = st.slider("🌾 نسبة المادة الجافة %:",
                min_value=70, max_value=95, value=88, step=1, key="fp_dm")

            if st.button("🧮 احسب العليقة", type="primary",
                         use_container_width=True, key="fp_calc"):
                plan = calculate_daily_feed_intake(
                    animal_type=fp_animal, weight_kg=fp_weight,
                    production_type=fp_prod, milk_yield=fp_milk,
                    adg_kg=fp_adg, age_weeks=fp_age_weeks,
                    num_animals=fp_num, feed_dm_pct=fp_dm_pct)
                if plan:
                    st.session_state["daily_feed_plan"] = plan
                    st.success("✅ تم الحساب!")
                else:
                    st.error("⚠️ تعذّر الحساب")

        plan = st.session_state.get("daily_feed_plan")
        if plan and plan.animal_type == fp_animal:
            st.markdown("---")
            st.markdown(f"### 📊 {plan.animal_type} / "
                        f"{PRODUCTION_TYPE_LABELS.get(plan.production_type, plan.production_type)}")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("🌾 DMI/حيوان", f"{plan.dmi_kg:.3f} كجم",
                      delta=f"{plan.dmi_pct_bw:.2f}% من الوزن")
            r2.metric("🍽️ علف/حيوان", f"{plan.feed_kg:.3f} كجم")
            r3.metric(f"📦 القطيع ({plan.num_animals})",
                      f"{plan.total_feed_kg:.1f} كجم/يوم")
            r4.metric("💧 ماء/حيوان",
                      f"{plan.water_liters:.2f} لتر" if plan.water_liters > 0 else "—")

            st.markdown("#### 🍽️ توزيع الوجبات")
            meal_cols = st.columns(plan.meals_per_day)
            for i, col in enumerate(meal_cols):
                with col:
                    st.metric(f"وجبة {i+1}",
                              f"{plan.feed_per_meal_kg*1000:.0f} جم",
                              delta=f"{plan.feed_per_meal_kg:.3f} كجم")

            with st.expander("🔬 التفاصيل العلمية", expanded=True):
                st.markdown(f"""
                - **المرجع:** {plan.notes}
                - **DMI:** {plan.dmi_kg:.3f} كجم/يوم
                - **العلف الطازج:** {plan.feed_kg:.3f} كجم/يوم
                - **عدد الوجبات:** {plan.meals_per_day}
                - **حجم الوجبة:** {plan.feed_per_meal_kg*1000:.0f} جم
                - **ماء الشرب:** {plan.water_liters:.2f} لتر/يوم
                """)
                if plan.protein_note:
                    st.info(f"🧬 {plan.protein_note}")
                if plan.energy_note:
                    st.info(f"⚡ {plan.energy_note}")

            active_formula = st.session_state.get("active_formula", {})
            if active_formula:
                st.markdown("### 🌾 توزيع المكونات اليومي")
                dist_rows = daily_feed_distribution(plan, active_formula)
                if dist_rows:
                    st.dataframe(pd.DataFrame(dist_rows),
                                 use_container_width=True, hide_index=True)
                    ton_cost = st.session_state.get("computed_ton_cost", 0.0)
                    if ton_cost > 0:
                        c1, c2, c3 = st.columns(3)
                        c1.metric("💰 تكلفة يومية/حيوان",
                                  f"${(plan.feed_kg / 1000.0) * ton_cost:.3f}")
                        c2.metric("💰 تكلفة يومية للقطيع",
                                  f"${(plan.total_feed_kg / 1000.0) * ton_cost:.2f}")
                        c3.metric("📅 تكلفة شهرية",
                                  f"${(plan.total_feed_kg / 1000.0) * ton_cost * 30:.2f}")
            else:
                st.info("💡 ركّب خلطة أولاً من تبويب النمذجة لعرض التوزيع والتكلفة")


# ═══ القسم 22: مكتبة الزيوت ═══
with tab_map["🌰 مكتبة الزيوت"]:
    st.markdown('<div class="section-title">🌰 مكتبة الزيوت</div>',
                unsafe_allow_html=True)
    oil_std_rows = [{"الحالة": k, "الحد الأقصى %": f"{v['max']}%",
                     "المثالي %": f"{v['optimal']}%", "المرجع": v["source"]}
                    for k, v in MAX_OIL_PERCENTAGE.items()]
    st.dataframe(pd.DataFrame(oil_std_rows), use_container_width=True,
                 hide_index=True)
    oils = get_oil_ingredients()
    for category, oil_list in OIL_CATEGORIES.items():
        st.markdown(f"#### {category}")
        for ing_name in oil_list:
            if ing_name in oils:
                with st.expander(f"🌰 {ing_name}"):
                    st.write(oils[ing_name].get("desc", ""))
                    st.caption(f"SE={oils[ing_name].get('SE', 0)} | "
                               f"المرجع: {oils[ing_name].get('source', 'NRC')}")


# ═══ القسم 23: مكتبة المركزات (مع الرسم البياني) ═══
with tab_map["🏭 مكتبة المركزات"]:
    st.markdown('<div class="section-title">🏭 مكتبة المركزات التجارية</div>',
                unsafe_allow_html=True)
    st.write("مقارنة المركزات التجارية بالمعايير القياسية مع رسم بياني تفاعلي.")

    concentrates = get_concentrates()

    # اختيار الحيوان للرسم البياني
    conc_animal = st.selectbox("🎯 اختر الحيوان للمقارنة:",
        ["أبقار — تسمين", "أبقار — حلابة", "أغنام — تسمين",
         "أغنام — مرضعات", "ماعز — حلابة", "دواجن — لاحم",
         "دواجن — بياض", "إبل — حلابة", "أسماك — نمو"],
        key="conc_animal")
    conc_req_map = {
        "أبقار — تسمين": get_cattle_requirements("تسمين_مكثف"),
        "أبقار — حلابة": get_cattle_requirements("حليب_عالي"),
        "أغنام — تسمين": get_sheep_requirements("تسمين_مكثف", is_male=True),
        "أغنام — مرضعات": get_sheep_requirements("مرضعات", is_male=False),
        "ماعز — حلابة": get_goat_requirements("حلابة_عالي", is_male=False),
        "دواجن — لاحم": get_poultry_requirements("لاحم", 3),
        "دواجن — بياض": get_poultry_requirements("بياض", 20),
        "إبل — حلابة": get_camel_requirements("حليب"),
        "أسماك — نمو": get_fish_requirements("البلطي النيلي", "نمو")}
    conc_standard = requirement_to_standard(conc_req_map[conc_animal])

    # اختيار المراكز
    selected_concentrates_names = st.multiselect(
        "اختر المركزات للمقارنة (اختر متعدد):",
        list(concentrates.keys()),
        default=list(concentrates.keys())[:3],
        key="conc_sel")

    if selected_concentrates_names:
        selected_concentrates = {name: concentrates[name]
                                 for name in selected_concentrates_names}

        # الرسم البياني
        chart = create_concentrate_chart(selected_concentrates, conc_standard)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.warning("⚠️ Plotly غير متوفر للرسم البياني")

        # جدول تفصيلي
        st.markdown("### 📊 جدول تفصيلي")
        rows = []
        for name, data in selected_concentrates.items():
            row = {"المركز": name}
            for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "Ca", "P"]:
                if k == "DP":
                    val = data.get("CP", 0) * data.get("DC", 0)
                else:
                    val = data.get(k, 0)
                std_val = conc_standard.get(k, 0)
                if std_val > 0:
                    diff_pct = ((val - std_val) / std_val * 100)
                    ev = evaluate_difference(diff_pct)
                    row[f"{k} ({ev['label'].split()[0]})"] = f"{val:.2f}"
                else:
                    row[k] = f"{val:.2f}"
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # توصية ذكية
        st.markdown("### 💡 التوصية الذكية")
        best_name = None; best_score = -1
        for name, data in selected_concentrates.items():
            scores = []
            for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "Ca", "P"]:
                std_val = conc_standard.get(k, 0)
                if std_val <= 0: continue
                if k == "DP":
                    val = data.get("CP", 0) * data.get("DC", 0)
                else:
                    val = data.get(k, 0)
                diff_pct = ((val - std_val) / std_val * 100)
                scores.append(evaluate_difference(diff_pct)["score"])
            avg = sum(scores) / len(scores) if scores else 0
            if avg > best_score:
                best_score = avg; best_name = name
        if best_name:
            st.success(f"🏆 **الأفضل للـ {conc_animal}**: **{best_name}** "
                       f"(مطابقة {best_score:.0f}%)")
    else:
        st.info("اختر مركزاً واحداً على الأقل لعرض المقارنة")


# ═══ القسم 24: بدائل الحليب ═══
with tab_map["🍼 بدائل الحليب"]:
    st.markdown('<div class="section-title">🍼 مختبر بدائل الحليب</div>',
                unsafe_allow_html=True)
    mr1, mr2 = st.columns(2)
    with mr1:
        mr_animal = st.selectbox("نوع الحيوان:",
            list(MILK_REPLACER_STANDARDS.keys()), key="mr_a")
        mr_volume = st.number_input("الكمية (كجم):", 1.0, 10000.0, 100.0,
                                     10.0, key="mr_v")
    with mr2:
        std_mr = MILK_REPLACER_STANDARDS[mr_animal]
        st.markdown(f"""
        <div class="price-card">
        <b>المعيار — {mr_animal}:</b><br>
        ▪️ بروتين: <b>{std_mr['CP']}%</b> |
        دهن: <b>{std_mr['Fat']}%</b><br>
        ▪️ لاكتوز: <b>{std_mr['Lactose']}%</b>
        </div>""", unsafe_allow_html=True)

    mr_selected = []
    mr_cols = st.columns(3)
    for i, (name, data) in enumerate(MILK_REPLACER_INGREDIENTS.items()):
        with mr_cols[i % 3]:
            default_mr = name in ["حليب مجفف منزوع الدسم",
                "حليب مجفف كامل الدسم", "شرش حليب مجفف",
                "زيت جوز الهند", "زيت النخيل", "بريمكس فيتامينات",
                "كالسيوم كربونات", "فوسفات ثنائي الكالسيوم", "ملح طعام"]
            if st.checkbox(f"{name} — ${data['price']}",
                            value=default_mr, key=f"mr_{name}"):
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
                    st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> '
                                f'{pct:.2f}% ({kg:.2f} كجم)</div>',
                                unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                m1.metric("💰 التكلفة/100 كجم:", f"${r['cost_per_100kg']:.2f}")
                m2.metric("💰 التكلفة/كجم:", f"${r['cost_per_kg']:.3f}")
            else:
                st.error(f"❌ {r['message']}")


# ═══ القسم 25: المختبر الذكي ═══
with tab_map["📷 المختبر الذكي"]:
    st.markdown('<div class="section-title">📷 المختبر الذكي (OCR)</div>',
                unsafe_allow_html=True)
    if not OCR_AVAILABLE:
        st.error("⚠️ pytesseract غير مثبتة")
        st.code("pip install pytesseract opencv-python-headless", language="bash")
    else:
        uploaded = st.file_uploader("📤 ارفع صورة:", type=["jpg", "jpeg", "png"])
        if uploaded:
            st.image(uploaded, caption="الصورة", use_container_width=True)
            if st.button("🔍 تحليل", type="primary", use_container_width=True):
                with st.spinner("جاري التحليل..."):
                    r = extract_ingredients_from_image(uploaded.read())
                if r["success"]:
                    st.success(f"✅ تم استخراج {r['count']} مادة")
                    if r["ingredients"]:
                        st.dataframe(pd.DataFrame([
                            {"المادة": k, "النسبة": f"{v:.2f}%"}
                            for k, v in r["ingredients"].items()
                        ]), use_container_width=True, hide_index=True)
                        nutrients = compute_formula_nutrients(r["ingredients"])
                        n1, n2, n3, n4 = st.columns(4)
                        n1.metric("CP", f"{nutrients['CP']:.2f}%")
                        n2.metric("DP", f"{nutrients['DP']:.2f}%")
                        n3.metric("SE", f"{nutrients['SE']:.2f}")
                        n4.metric("NDF", f"{nutrients['NDF']:.2f}%")
                else:
                    st.error(f"❌ {r['message']}")


# ═══ القسم 26: تبويبات المالك ═══
if is_owner():
    with tab_map["🏗️ تصميم الحظائر 3D"]:
        st.markdown('<div class="section-title">🏗️ تصميم الحظائر 3D</div>',
                    unsafe_allow_html=True)
        st.write("قيد التطوير — يمكن استخدام النسخة السابقة.")

    with tab_map["📊 البورصة"]:
        st.markdown('<div class="section-title">📊 البورصة</div>',
                    unsafe_allow_html=True)
        for animal, price in list(st.session_state["livestock_prices"].items()):
            new_p = st.number_input(f"{animal}", min_value=0.0,
                value=float(price), step=0.1, key=f"lv_{animal}")
            st.session_state["livestock_prices"][animal] = new_p

    with tab_map["🏭 المستودعات"]:
        st.markdown('<div class="section-title">🏭 المستودعات</div>',
                    unsafe_allow_html=True)
        inv = st.session_state["inventory"]
        cols = st.columns(3)
        for i, (name, data) in enumerate(list(inv.items())[:60]):
            with cols[i % 3]:
                q = data["quantity"] if isinstance(data, dict) else data
                badge = "🔴" if q <= 0 else ("🟡" if q < 5 else "🟢")
                st.markdown(f"{badge} **{name}**: {q:.1f} طن")

    with tab_map["🧾 الفواتير"]:
        st.markdown('<div class="section-title">🧾 الفواتير</div>',
                    unsafe_allow_html=True)
        tons = st.number_input("الكمية (طن):", 0.1, 1000.0, 2.0, 0.5)
        profit = st.number_input("هامش الربح ($/طن):", 0.0, 1000.0, 50.0)
        sell = st.session_state["computed_ton_cost"] + profit
        st.markdown(f"""
        <div class="price-card">
        <h4>🧾 فاتورة</h4>
        <p><b>الكمية:</b> {tons} طن</p>
        <p><b>سعر الطن:</b> ${sell:.2f}</p>
        <p style="font-size:1.3rem; color:#1b5e20;">
        <b>الإجمالي:</b> ${sell * tons:.2f}</p>
        </div>""", unsafe_allow_html=True)

    with tab_map["🖨️ الديباجة"]:
        st.markdown('<div class="section-title">🖨️ الديباجة</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div style="border: 3px dashed #1b5e20; padding: 30px;
        border-radius: 15px; background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
        direction: rtl; text-align: center;">
        <h2 style="color: #1b5e20;">🌟 {APP_NAME} 🌟</h2>
        <h3 style="color: #c62828;">{SUPERVISOR}</h3>
        <p style="background:#e8f5e9; padding:12px; color:#1b5e20;">
        🎯 {st.session_state['active_stage_title']}</p>
        <small>📅 {datetime.now():%Y-%m-%d}</small>
        </div>""", unsafe_allow_html=True)

    with tab_map["📈 التحليلات"]:
        st.markdown('<div class="section-title">📈 التحليلات</div>',
                    unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("الخلطات", "1,247"); m2.metric("متوسط", "$285")
        m3.metric("التوفير", "18%"); m4.metric("الرضا", "96%")
        if PLOTLY_AVAILABLE:
            usage = pd.DataFrame({
                'المادة': ['ذرة', 'صويا', 'نخالة', 'زيوت', 'مركزات', 'أخرى'],
                'النسبة': [40, 22, 14, 8, 10, 6]})
            fig = px.pie(usage, values='النسبة', names='المادة',
                         color_discrete_sequence=px.colors.sequential.Greens)
            st.plotly_chart(fig, use_container_width=True)

    with tab_map["🐔 مزارع الدجاج"]:
        st.markdown('<div class="section-title">🐔 مزارع الدجاج</div>',
                    unsafe_allow_html=True)
        with st.expander("➕ إضافة مزرعة"):
            nf = st.text_input("اسم المزرعة:", key="nf")
            if st.button("💾 حفظ") and nf:
                st.session_state["broiler_farms"][nf] = {
                    "data": {"age": 1, "birds": 1000, "weight_kg": 0.045,
                             "feed_kg": 0.0, "dead": 0}}
                st.rerun()
        if st.session_state["broiler_farms"]:
            sel = st.selectbox("اختر:", [""] + list(
                st.session_state["broiler_farms"].keys()))
            if sel:
                d = st.session_state["broiler_farms"][sel]["data"]
                d["age"] = st.number_input("العمر:", 1, 60, d["age"])
                d["birds"] = st.number_input("الطيور:", 1, value=d["birds"])
                d["weight_kg"] = st.number_input("الوزن (كجم):", 0.0, 10.0,
                    float(d["weight_kg"]), 0.01)
                d["feed_kg"] = st.number_input("العلف (كجم):", 0.0,
                    float(d["feed_kg"]), 100.0)

    with tab_map["💬 التعليقات"]:
        st.markdown('<div class="section-title">💬 التعليقات</div>',
                    unsafe_allow_html=True)
        st.text_area("الحالية:", value=st.session_state["shared_comments"],
                     height=200, disabled=True)
        nc = st.text_area("جديد:")
        if st.button("➕ نشر") and nc:
            st.session_state["shared_comments"] += (
                f"\n• [{datetime.now():%Y-%m-%d %H:%M}]: {nc}")
            st.rerun()


# ═══ القسم 27: المراجع والمساعدة ═══
with tab_map["📚 المراجع"]:
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>',
                unsafe_allow_html=True)
    st.markdown("""
    ### المراجع:
    - **NRC (2012, 2007, 2001, 1994)** — Nutrient Requirements
    - **INRA (2018)** — Feeding System for Ruminants
    - **FAO (2010)** — Camel Nutrition
    - **Ross 308 (2020)** — Broiler Handbook
    - **Schaeffer's formula** — Weight estimation
    - **Heinrichs et al. (1992)** — Cattle weight
    - **MWPS-1** — Structures Handbook
    """)

with tab_map["💡 المساعدة"]:
    st.markdown('<div class="section-title">💡 المساعدة</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    ### الأسئلة الشائعة:
    - **🔗 الربط التلقائي للوزن؟**
        1. اذهب لتبويب «⚖️ حاسبة العليقة وقياس الوزن»
        2. اختر «📏 قياس الوزن بالشريط»
        3. أدخل القياسات → اضغط احسب
        4. الوزن يُحفظ تلقائياً لكل نوع حيوان
        5. انتقل لتبويب «🍽️ حاسبة العليقة» → ستجد الوزن معبأً
    - **🏭 المركزات؟** تبويب مخصص مع رسم بياني تفاعلي
    - **📊 المقارنة بالمعايير؟** في مختبر الأعلاف الجاهزة
    - **📥 تحميل PDF؟** في كل تقرير زر PDF

    ### 🔧 الدعم:
    📧 {OWNER_EMAIL} | 📱 {WHATSAPP_NUMBER}

    ### 🕌 دعاء:
    {DUA_FULL}
    """)


# ═══ القسم 28: التذييل ═══
st.markdown(
    f'<div class="mini-signature">🌾 {APP_NAME} | {SUPERVISOR} © 2026</div>',
    unsafe_allow_html=True)
st.markdown(
    f'<div class="dua-fixed-banner">🤲 {DUA_SHORT} 🤲</div>',
    unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# نهاية الملف — Tawor Nology 10.3
# ═══════════════════════════════════════════════════════════════════════════
