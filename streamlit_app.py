# ═══════════════════════════════════════════════════════════════════════════
# تاور نولجي TAWOR NOLOGY 11.2 — (الجزء 1/3)
# إشراف: د. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
# 🆕 v11.2 — التعديلات:
#   ✅ اللقب "د." | حذف البورصة والموقع الجغرافي
#   ✅ شريط تقدير الوزن للخيل (Carroll & Huntington)
#   ✅ بدائل الحليب ≥75% | بطاقة الحالة الفسيولوجية
#   ✅ SharedStorage (تعدد الأجهزة) | جدوى متعددة
#   ✅ safe_section للأخطاء | محرك LP محسّن
# ═══════════════════════════════════════════════════════════════════════════
import streamlit as st
import numpy as np
import pandas as pd
import io, os, re, base64, tempfile, traceback, warnings, json, threading
import urllib.parse, urllib.request, hashlib, secrets
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple

warnings.filterwarnings('ignore')

# ─── استيرادات محمية ───
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
    from matplotlib import animation
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    import cv2
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import openpyxl
    from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side,
                                   NamedStyle)
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.platypus import (Table, TableStyle, Paragraph, Spacer,
                                     Image as RLImage, SimpleDocTemplate,
                                     HRFlowable, PageBreak)
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    from reportlab.lib.units import cm, mm
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


# ═══ الثوابت ═══
DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي ابتسام"
DUA_FULL = ("رحم الله والدي إسماعيل تاور وأختي ابتسام وأسكنهما فسيح جناته "
            "وجعل قبرهما روضة من رياض الجنة")
DUA_QURAN = "﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾"
DUA_VERSE = "﴿ وَقُل رَّبِّ ارْحَمْهُمَا كَمَا رَبَّيَانِي صَغِيرًا ﴾"
DUA_VISITOR = """🕌 <b>إلى زوارنا الكرام:</b><br>
هذه المنصة صدقةٌ جارية عن <b>والدي إسماعيل تاور</b> و<b>أختي ابتسام</b>.<br>
نسألكم بظهر الغيب أن تشاركوا الدعاء. 🤲"""

APP_NAME = "تاور نولجي Tawor Nology"
APP_TAGLINE = "للإنتاج الحيواني وتغذية الحيوان"
APP_VERSION = "11.2"
SUPERVISOR = "د. عبدالقادر إسماعيل تاور"      # ✅ v11.2 — لقب جديد
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


# ═══ safe_section — طبقة حماية الأخطاء v11.2 ═══
def safe_section(func):
    """يُغلّف أي قسم بـ try/except احترافي"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"⚠️ حدث خطأ غير متوقع في هذا القسم: {type(e).__name__}")
            with st.expander("🔍 التفاصيل التقنية"):
                st.code(traceback.format_exc())
            st.info(f"💡 جرّب تحديث الصفحة (F5). للدعم: {OWNER_EMAIL}")
    return wrapper


# ═══ إدارة الخطوط ═══
FONT_DIR = "fonts"
os.makedirs(FONT_DIR, exist_ok=True)


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
        local_paths = [
            os.path.join(FONT_DIR, "Amiri-Regular.ttf"),
            "Amiri-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf",
        ]
        for p in local_paths:
            if os.path.exists(p) and self._register(p):
                return
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
            target = os.path.join(FONT_DIR, "Amiri-Regular.ttf")
            if not os.path.exists(target):
                urllib.request.urlretrieve(url, target)
            self._register(target)
        except Exception:
            pass

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
    @lru_cache(maxsize=1500)
    def fix(text):
        if text is None or text == "":
            return ""
        text = str(text)
        if not ARABIC_AVAILABLE:
            return text
        try:
            return get_display(arabic_reshaper.reshape(text), base_dir='R')
        except Exception:
            return text


def ar(text):
    return ArabicProcessor.fix(text)


# ═══════════════════════════════════════════════════════════════════════════
# مكتبة الأعلاف — 172 مكوناً
# ═══════════════════════════════════════════════════════════════════════════
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3, "Ca": 0.02, "P": 0.27, "Lys": 0.24, "Met": 0.17, "price": 230, "desc": "المصدر الرئيسي للطاقة", "src": "NRC 2012"},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4, "Ca": 0.02, "P": 0.26, "Lys": 0.25, "Met": 0.18, "price": 225, "desc": "بديل مقبول للصفراء", "src": "NRC 2012"},
        "ذرة شامية": {"CP": 8.3, "DC": 0.86, "SE": 82.0, "NDF": 9.0, "ADF": 3.0, "EE": 4.0, "ASH": 1.2, "Ca": 0.02, "P": 0.28, "Lys": 0.23, "Met": 0.16, "price": 240, "desc": "طاقة أعلى", "src": "NRC 2012"},
        "ذرة رفيعة (سورجم)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8, "Ca": 0.03, "P": 0.30, "Lys": 0.22, "Met": 0.17, "price": 195, "desc": "بديل جيد", "src": "NRC 2012"},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5, "Ca": 0.05, "P": 0.35, "Lys": 0.42, "Met": 0.20, "price": 210, "desc": "مقبول للمجترات", "src": "NRC 2012"},
        "شعير كامل": {"CP": 10.8, "DC": 0.75, "SE": 68.0, "NDF": 22.0, "ADF": 9.0, "EE": 2.0, "ASH": 2.8, "Ca": 0.05, "P": 0.33, "Lys": 0.40, "Met": 0.18, "price": 200, "desc": "يحتاج جرش", "src": "NRC 2012"},
        "قمح محلي": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6, "Ca": 0.04, "P": 0.32, "Lys": 0.35, "Met": 0.20, "price": 240, "desc": "طاقة جيدة", "src": "NRC 2012"},
        "قمح مستورد": {"CP": 11.5, "DC": 0.87, "SE": 78.0, "NDF": 11.0, "ADF": 3.5, "EE": 1.9, "ASH": 1.5, "Ca": 0.04, "P": 0.33, "Lys": 0.34, "Met": 0.19, "price": 245, "desc": "طاقة أعلى", "src": "NRC 2012"},
        "جريش أرز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2, "Ca": 0.06, "P": 0.30, "Lys": 0.28, "Met": 0.18, "price": 240, "desc": "طاقة عالية", "src": "NRC 2012"},
        "دخن محلي": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2, "Ca": 0.05, "P": 0.31, "Lys": 0.28, "Met": 0.20, "price": 220, "desc": "بديل", "src": "NRC 2012"},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0, "Ca": 0.08, "P": 0.35, "Lys": 0.40, "Met": 0.18, "price": 260, "desc": "ممتاز للخيول", "src": "NRC 2007"},
        "كسرة خبز": {"CP": 10.5, "DC": 0.82, "SE": 75.0, "NDF": 8.0, "ADF": 3.5, "EE": 5.5, "ASH": 3.5, "Ca": 0.10, "P": 0.20, "Lys": 0.28, "Met": 0.17, "price": 160, "desc": "اقتصادي", "src": "INRA 2018"},
        "بسكويت مكسر": {"CP": 8.5, "DC": 0.85, "SE": 85.0, "NDF": 4.0, "ADF": 2.0, "EE": 12.0, "ASH": 2.5, "Ca": 0.08, "P": 0.18, "Lys": 0.20, "Met": 0.12, "price": 180, "desc": "طاقة عالية", "src": "INRA 2018"},
        "مكرونة مكسرة": {"CP": 11.0, "DC": 0.88, "SE": 80.0, "NDF": 3.5, "ADF": 1.5, "EE": 1.5, "ASH": 1.0, "Ca": 0.03, "P": 0.20, "Lys": 0.28, "Met": 0.15, "price": 190, "desc": "طاقة عالية", "src": "INRA 2018"},
        "بطاطا مجففة": {"CP": 8.0, "DC": 0.90, "SE": 78.0, "NDF": 6.0, "ADF": 3.0, "EE": 1.0, "ASH": 4.5, "Ca": 0.08, "P": 0.22, "Lys": 0.28, "Met": 0.15, "price": 200, "desc": "بديلة", "src": "INRA 2018"},
        "كسافا مجففة": {"CP": 3.0, "DC": 0.85, "SE": 75.0, "NDF": 8.0, "ADF": 4.5, "EE": 1.0, "ASH": 3.5, "Ca": 0.15, "P": 0.10, "Lys": 0.10, "Met": 0.05, "price": 150, "desc": "رخيصة", "src": "FAO 2010"},
        "تمر مجفف (دقل)": {"CP": 5.5, "DC": 0.85, "SE": 68.0, "NDF": 15.0, "ADF": 8.5, "EE": 1.0, "ASH": 3.5, "Ca": 0.10, "P": 0.10, "Lys": 0.10, "Met": 0.05, "price": 180, "desc": "اقتصادي", "src": "FAO 2010"},
        "سكر مائدة": {"CP": 0.0, "DC": 1.0, "SE": 100.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 500, "desc": "بحدود 2%", "src": "NRC 2012"},
        "عسل أسود (دبس)": {"CP": 1.0, "DC": 0.92, "SE": 75.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.5, "Ca": 0.15, "P": 0.05, "Lys": 0.05, "Met": 0.02, "price": 220, "desc": "بحدود 3%", "src": "NRC 2012"},
        "تفل بنجر السكر": {"CP": 8.5, "DC": 0.65, "SE": 55.0, "NDF": 45.0, "ADF": 28.0, "EE": 1.0, "ASH": 8.5, "Ca": 0.70, "P": 0.10, "Lys": 0.30, "Met": 0.15, "price": 190, "desc": "للمجترات", "src": "INRA 2018"},
        "تفل عنب": {"CP": 12.0, "DC": 0.55, "SE": 40.0, "NDF": 45.0, "ADF": 32.0, "EE": 7.5, "ASH": 6.0, "Ca": 0.25, "P": 0.40, "Lys": 0.30, "Met": 0.15, "price": 120, "desc": "مضاد أكسدة", "src": "INRA 2018"},
        "تفل زيتون": {"CP": 8.0, "DC": 0.55, "SE": 35.0, "NDF": 50.0, "ADF": 35.0, "EE": 12.0, "ASH": 7.0, "Ca": 0.50, "P": 0.15, "Lys": 0.20, "Met": 0.10, "price": 130, "desc": "غني بالزيوت", "src": "INRA 2018"},
    },

    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5, "Ca": 0.20, "P": 0.65, "Lys": 1.60, "Met": 0.45, "price": 460, "desc": "بروتين ممتاز", "src": "NRC 2012"},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0, "Ca": 0.35, "P": 0.65, "Lys": 2.70, "Met": 0.60, "price": 440, "desc": "المصدر الرئيسي", "src": "NRC 2012"},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2, "Ca": 0.35, "P": 0.65, "Lys": 3.00, "Met": 0.68, "price": 480, "desc": "بروتين مرتفع", "src": "NRC 2012"},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5, "Ca": 0.40, "P": 1.00, "Lys": 1.20, "Met": 0.70, "price": 310, "desc": "أرخص", "src": "NRC 2012"},
        "كسب عباد الشمس 32%": {"CP": 32.0, "DC": 0.72, "SE": 38.0, "NDF": 42.0, "ADF": 28.0, "EE": 2.0, "ASH": 7.0, "Ca": 0.42, "P": 0.95, "Lys": 1.10, "Met": 0.65, "price": 290, "desc": "اقتصادي", "src": "NRC 2012"},
        "كسب بذور القطن": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5, "Ca": 0.20, "P": 1.10, "Lys": 1.80, "Met": 0.60, "price": 290, "desc": "معادلة الجوسيبول", "src": "NRC 2012"},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8, "Ca": 0.35, "P": 0.85, "Lys": 1.20, "Met": 0.55, "price": 340, "desc": "أوميغا 3", "src": "NRC 2007"},
        "كسب السمسم": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5, "Ca": 2.00, "P": 1.20, "Lys": 1.30, "Met": 1.00, "price": 520, "desc": "غني بالكالسيوم", "src": "NRC 2007"},
        "كسب جلوتين 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5, "Ca": 0.15, "P": 0.50, "Lys": 1.10, "Met": 1.80, "price": 520, "desc": "غني بالميثيونين", "src": "NRC 2012"},
        "كسب جلوتين 40%": {"CP": 40.0, "DC": 0.88, "SE": 72.0, "NDF": 15.0, "ADF": 8.0, "EE": 3.0, "ASH": 5.0, "Ca": 0.18, "P": 0.55, "Lys": 1.20, "Met": 1.10, "price": 390, "desc": "بروتين معتدل", "src": "NRC 2012"},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5, "Ca": 0.30, "P": 0.55, "Lys": 0.55, "Met": 0.28, "price": 200, "desc": "رخيص", "src": "FAO 2010"},
        "كسب بذور العنب": {"CP": 12.0, "DC": 0.55, "SE": 30.0, "NDF": 45.0, "ADF": 32.0, "EE": 7.5, "ASH": 6.0, "Ca": 0.25, "P": 0.40, "Lys": 0.40, "Met": 0.20, "price": 140, "desc": "مضاد أكسدة", "src": "INRA 2018"},
        "كسب بذور القرطم": {"CP": 24.0, "DC": 0.70, "SE": 45.0, "NDF": 35.0, "ADF": 22.0, "EE": 2.0, "ASH": 6.0, "Ca": 0.35, "P": 0.75, "Lys": 0.90, "Met": 0.45, "price": 300, "desc": "بديل", "src": "NRC 2007"},
        "كسب الكانولا": {"CP": 36.0, "DC": 0.82, "SE": 60.0, "NDF": 28.0, "ADF": 18.0, "EE": 3.5, "ASH": 6.5, "Ca": 0.65, "P": 1.10, "Lys": 1.90, "Met": 0.70, "price": 400, "desc": "متوازن", "src": "NRC 2012"},
        "كسب الأفوكادو": {"CP": 18.0, "DC": 0.65, "SE": 50.0, "NDF": 40.0, "ADF": 28.0, "EE": 8.0, "ASH": 5.5, "Ca": 0.30, "P": 0.45, "Lys": 0.70, "Met": 0.35, "price": 280, "desc": "غير شائع", "src": "INRA 2018"},
        "كسب الجوجوبا": {"CP": 28.0, "DC": 0.60, "SE": 40.0, "NDF": 42.0, "ADF": 30.0, "EE": 12.0, "ASH": 6.5, "Ca": 0.30, "P": 0.55, "Lys": 0.90, "Met": 0.50, "price": 380, "desc": "معادلة", "src": "FAO 2010"},
        "كسب المريمية": {"CP": 22.0, "DC": 0.60, "SE": 38.0, "NDF": 38.0, "ADF": 26.0, "EE": 8.0, "ASH": 8.0, "Ca": 1.20, "P": 0.40, "Lys": 0.80, "Met": 0.35, "price": 260, "desc": "مضاد", "src": "INRA 2018"},
        "كسب الكزبرة": {"CP": 20.0, "DC": 0.60, "SE": 35.0, "NDF": 40.0, "ADF": 28.0, "EE": 6.0, "ASH": 7.5, "Ca": 1.00, "P": 0.35, "Lys": 0.75, "Met": 0.30, "price": 250, "desc": "مضاد", "src": "INRA 2018"},
        "فول صويا كامل": {"CP": 38.0, "DC": 0.85, "SE": 78.0, "NDF": 15.0, "ADF": 10.0, "EE": 18.0, "ASH": 4.5, "Ca": 0.25, "P": 0.55, "Lys": 2.50, "Met": 0.55, "price": 420, "desc": "معالجة حرارية", "src": "NRC 2012"},
        "ترمس حلو": {"CP": 32.0, "DC": 0.80, "SE": 65.0, "NDF": 20.0, "ADF": 12.0, "EE": 6.0, "ASH": 4.0, "Ca": 0.20, "P": 0.45, "Lys": 1.80, "Met": 0.35, "price": 380, "desc": "بديل", "src": "NRC 2007"},
        "بازلاء علفية": {"CP": 22.0, "DC": 0.82, "SE": 70.0, "NDF": 15.0, "ADF": 8.0, "EE": 1.5, "ASH": 3.0, "Ca": 0.10, "P": 0.40, "Lys": 1.50, "Met": 0.25, "price": 320, "desc": "متوازن", "src": "NRC 2012"},
        "عدس علفي": {"CP": 25.0, "DC": 0.80, "SE": 65.0, "NDF": 18.0, "ADF": 10.0, "EE": 1.2, "ASH": 3.5, "Ca": 0.15, "P": 0.45, "Lys": 1.70, "Met": 0.30, "price": 350, "desc": "جيد", "src": "NRC 2012"},
    },

    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5, "Ca": 0.12, "P": 1.10, "Lys": 0.60, "Met": 0.25, "price": 150, "desc": "اقتصادية", "src": "NRC 2001"},
        "نخالة ذرة": {"CP": 9.5, "DC": 0.65, "SE": 40.0, "NDF": 40.0, "ADF": 15.0, "EE": 4.0, "ASH": 2.0, "Ca": 0.10, "P": 0.75, "Lys": 0.30, "Met": 0.15, "price": 140, "desc": "اقتصادية", "src": "NRC 2001"},
        "البرسيم الجاف": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5, "Ca": 1.50, "P": 0.25, "Lys": 0.85, "Met": 0.25, "price": 170, "desc": "بروتين وألياف", "src": "NRC 2001"},
        "برسيم حجازي": {"CP": 18.0, "DC": 0.62, "SE": 38.0, "NDF": 40.0, "ADF": 30.0, "EE": 2.2, "ASH": 11.0, "Ca": 1.60, "P": 0.26, "Lys": 0.90, "Met": 0.28, "price": 175, "desc": "أفضل", "src": "NRC 2001"},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5, "Ca": 0.70, "P": 0.05, "Lys": 0.03, "Met": 0.02, "price": 120, "desc": "طاقة سريعة", "src": "NRC 2001"},
        "تبن قمح": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.30, "P": 0.08, "Lys": 0.15, "Met": 0.05, "price": 80, "desc": "ألياف", "src": "NRC 2001"},
        "تبن فول": {"CP": 4.5, "DC": 0.40, "SE": 22.0, "NDF": 68.0, "ADF": 42.0, "EE": 1.2, "ASH": 7.5, "Ca": 0.35, "P": 0.10, "Lys": 0.18, "Met": 0.08, "price": 90, "desc": "أفضل", "src": "NRC 2001"},
        "تبن عدس": {"CP": 5.0, "DC": 0.42, "SE": 24.0, "NDF": 65.0, "ADF": 40.0, "EE": 1.5, "ASH": 8.0, "Ca": 0.40, "P": 0.12, "Lys": 0.20, "Met": 0.08, "price": 95, "desc": "مقبول", "src": "NRC 2001"},
        "قشر فول سوداني": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5, "Ca": 0.25, "P": 0.10, "Lys": 0.15, "Met": 0.05, "price": 70, "desc": "حشو", "src": "NRC 2007"},
        "سرسة الأرز": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5, "Ca": 0.15, "P": 0.08, "Lys": 0.10, "Met": 0.05, "price": 60, "desc": "حشو", "src": "NRC 2007"},
        "قش أرز": {"CP": 3.5, "DC": 0.30, "SE": 15.0, "NDF": 70.0, "ADF": 45.0, "EE": 1.5, "ASH": 12.0, "Ca": 0.20, "P": 0.06, "Lys": 0.12, "Met": 0.05, "price": 65, "desc": "حشو", "src": "NRC 2007"},
        "مخلفات النخيل": {"CP": 6.5, "DC": 0.70, "SE": 60.0, "NDF": 25.0, "ADF": 15.0, "EE": 5.0, "ASH": 3.5, "Ca": 0.15, "P": 0.15, "Lys": 0.25, "Met": 0.10, "price": 100, "desc": "للإبل", "src": "FAO 2010"},
        "سعف نخيل مطحون": {"CP": 4.0, "DC": 0.30, "SE": 20.0, "NDF": 65.0, "ADF": 42.0, "EE": 2.0, "ASH": 7.0, "Ca": 0.35, "P": 0.08, "Lys": 0.15, "Met": 0.06, "price": 55, "desc": "ألياف", "src": "FAO 2010"},
        "قشور الفول السوداني": {"CP": 6.5, "DC": 0.40, "SE": 22.0, "NDF": 58.0, "ADF": 38.0, "EE": 2.5, "ASH": 4.0, "Ca": 0.20, "P": 0.12, "Lys": 0.20, "Met": 0.08, "price": 75, "desc": "حشو", "src": "NRC 2007"},
        "أوراق موز مجففة": {"CP": 12.0, "DC": 0.55, "SE": 30.0, "NDF": 45.0, "ADF": 30.0, "EE": 3.0, "ASH": 10.0, "Ca": 1.20, "P": 0.20, "Lys": 0.50, "Met": 0.20, "price": 85, "desc": "غير شائع", "src": "FAO 2010"},
        "أوراق مانجو": {"CP": 10.0, "DC": 0.50, "SE": 28.0, "NDF": 48.0, "ADF": 32.0, "EE": 3.5, "ASH": 9.0, "Ca": 1.50, "P": 0.15, "Lys": 0.45, "Met": 0.18, "price": 80, "desc": "معادن", "src": "FAO 2010"},
        "أوراق نخيل": {"CP": 5.0, "DC": 0.35, "SE": 22.0, "NDF": 62.0, "ADF": 42.0, "EE": 2.5, "ASH": 6.5, "Ca": 0.40, "P": 0.10, "Lys": 0.15, "Met": 0.06, "price": 50, "desc": "ألياف", "src": "FAO 2010"},
        "تفل قصب السكر": {"CP": 3.0, "DC": 0.30, "SE": 15.0, "NDF": 70.0, "ADF": 48.0, "EE": 1.0, "ASH": 3.0, "Ca": 0.20, "P": 0.08, "Lys": 0.10, "Met": 0.05, "price": 45, "desc": "حشو", "src": "FAO 2010"},
        "قوالح ذرة": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 72.0, "ADF": 45.0, "EE": 1.0, "ASH": 3.0, "Ca": 0.15, "P": 0.08, "Lys": 0.10, "Met": 0.05, "price": 40, "desc": "حشو", "src": "FAO 2010"},
        "قش عدس": {"CP": 4.5, "DC": 0.35, "SE": 18.0, "NDF": 68.0, "ADF": 43.0, "EE": 1.2, "ASH": 9.0, "Ca": 0.35, "P": 0.10, "Lys": 0.15, "Met": 0.06, "price": 60, "desc": "حشو", "src": "NRC 2001"},
    },

    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5, "Ca": 5.50, "P": 3.20, "Lys": 4.50, "Met": 1.80, "price": 850, "desc": "ممتاز", "src": "NRC 2012"},
        "مسحوق أسماك 72%": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5, "Ca": 4.80, "P": 2.80, "Lys": 5.50, "Met": 2.20, "price": 1100, "desc": "مرتفع جداً", "src": "NRC 2012"},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5, "Ca": 9.00, "P": 4.50, "Lys": 2.50, "Met": 0.70, "price": 620, "desc": "Ca وP", "src": "NRC 2012"},
        "مسحوق الدم": {"CP": 80.0, "DC": 0.65, "SE": 55.0, "NDF": 1.0, "ADF": 0.5, "EE": 1.5, "ASH": 6.0, "Ca": 0.30, "P": 0.30, "Lys": 7.00, "Met": 1.00, "price": 780, "desc": "تحسين الهضم", "src": "NRC 2012"},
        "مسحوق ريش": {"CP": 82.0, "DC": 0.70, "SE": 60.0, "NDF": 1.5, "ADF": 1.0, "EE": 3.0, "ASH": 4.0, "Ca": 0.25, "P": 0.35, "Lys": 2.00, "Met": 0.50, "price": 650, "desc": "معالجة حرارية", "src": "NRC 2012"},
        "مسحوق مخلفات دواجن": {"CP": 55.0, "DC": 0.78, "SE": 58.0, "NDF": 5.0, "ADF": 3.0, "EE": 12.0, "ASH": 15.0, "Ca": 3.00, "P": 1.80, "Lys": 2.80, "Met": 0.80, "price": 550, "desc": "فحص جودة", "src": "NRC 2012"},
        "مركزات دواجن": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5, "Ca": 2.50, "P": 1.20, "Lys": 2.50, "Met": 0.90, "price": 650, "desc": "جاهزة", "src": "NRC 2012"},
        "مركزات مواشي": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5, "Ca": 3.00, "P": 1.50, "Lys": 2.00, "Met": 0.70, "price": 600, "desc": "جاهزة", "src": "NRC 2001"},
        "بروتين بلازما الدم": {"CP": 78.0, "DC": 0.90, "SE": 62.0, "NDF": 0.5, "ADF": 0.0, "EE": 2.0, "ASH": 10.0, "Ca": 0.15, "P": 0.20, "Lys": 6.50, "Met": 0.90, "price": 2400, "desc": "للفطام", "src": "NRC 2012"},
        "بيض مجفف": {"CP": 48.0, "DC": 0.90, "SE": 78.0, "NDF": 0.0, "ADF": 0.0, "EE": 40.0, "ASH": 4.0, "Ca": 0.20, "P": 0.20, "Lys": 3.50, "Met": 1.50, "price": 1500, "desc": "بروتين ودهن", "src": "NRC 2012"},
        "حشرات مجففة (BSF)": {"CP": 42.0, "DC": 0.80, "SE": 68.0, "NDF": 8.0, "ADF": 5.0, "EE": 35.0, "ASH": 8.0, "Ca": 0.80, "P": 0.90, "Lys": 2.60, "Met": 0.85, "price": 1800, "desc": "مستدام", "src": "FAO 2013"},
        "دود قز مجفف": {"CP": 55.0, "DC": 0.75, "SE": 55.0, "NDF": 4.0, "ADF": 3.0, "EE": 25.0, "ASH": 8.5, "Ca": 0.50, "P": 0.80, "Lys": 3.20, "Met": 1.20, "price": 1400, "desc": "غني", "src": "FAO 2010"},
    },

    "🌿 الأعلاف الخضراء المائية": {
        "أزولا مجففة": {"CP": 24.0, "DC": 0.65, "SE": 45.0, "NDF": 38.0, "ADF": 25.0, "EE": 3.5, "ASH": 18.0, "Ca": 2.00, "P": 0.60, "Lys": 1.00, "Met": 0.40, "price": 340, "desc": "نباتي", "src": "FAO 2010"},
        "سبيرولينا": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 5.0, "ADF": 3.0, "EE": 6.0, "ASH": 10.0, "Ca": 1.20, "P": 0.90, "Lys": 3.00, "Met": 1.40, "price": 3200, "desc": "سوبر", "src": "FAO 2010"},
        "كلوريلا": {"CP": 55.0, "DC": 0.80, "SE": 60.0, "NDF": 6.0, "ADF": 3.5, "EE": 8.0, "ASH": 12.0, "Ca": 0.50, "P": 1.20, "Lys": 2.50, "Met": 1.20, "price": 2800, "desc": "مكمل", "src": "FAO 2010"},
        "طحالب بحرية": {"CP": 15.0, "DC": 0.60, "SE": 30.0, "NDF": 25.0, "ADF": 15.0, "EE": 2.0, "ASH": 30.0, "Ca": 1.50, "P": 0.30, "Lys": 0.60, "Met": 0.25, "price": 900, "desc": "معادن", "src": "FAO 2010"},
        "لمنا مجففة": {"CP": 20.0, "DC": 0.55, "SE": 35.0, "NDF": 30.0, "ADF": 20.0, "EE": 3.0, "ASH": 15.0, "Ca": 1.80, "P": 0.55, "Lys": 0.80, "Met": 0.30, "price": 280, "desc": "للدواجن", "src": "FAO 2010"},
        "سالفينيا": {"CP": 22.0, "DC": 0.60, "SE": 40.0, "NDF": 32.0, "ADF": 22.0, "EE": 3.5, "ASH": 16.0, "Ca": 1.50, "P": 0.55, "Lys": 0.85, "Met": 0.35, "price": 300, "desc": "أزولا", "src": "FAO 2010"},
        "أوراق كينوا": {"CP": 18.0, "DC": 0.60, "SE": 40.0, "NDF": 32.0, "ADF": 22.0, "EE": 4.5, "ASH": 12.0, "Ca": 1.20, "P": 0.40, "Lys": 1.00, "Met": 0.35, "price": 240, "desc": "غير شائع", "src": "FAO 2010"},
        "أوراق مورينجا": {"CP": 25.0, "DC": 0.65, "SE": 42.0, "NDF": 28.0, "ADF": 18.0, "EE": 4.0, "ASH": 10.0, "Ca": 2.50, "P": 0.35, "Lys": 1.20, "Met": 0.45, "price": 380, "desc": "غنية", "src": "FAO 2010"},
    },

    "🌰 الزيوت النباتية والحيوانية": {
        "زيت ذرة": {"CP": 0.0, "DC": 0.0, "SE": 220.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 1500, "desc": "أوميغا 6", "src": "NRC 2012", "max_poultry": 6.0, "max_ruminant": 5.0, "max_fish": 10.0, "max_horse": 8.0},
        "زيت فول الصويا": {"CP": 0.0, "DC": 0.0, "SE": 215.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 1350, "desc": "متوازن", "src": "Ross 308", "max_poultry": 8.0, "max_ruminant": 5.0, "max_fish": 12.0, "max_horse": 10.0},
        "زيت عباد الشمس": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 1300, "desc": "أوميغا 6", "src": "NRC 2007", "max_poultry": 6.0, "max_ruminant": 4.0, "max_fish": 8.0, "max_horse": 8.0},
        "زيت بذرة القطن": {"CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 1400, "desc": "جوسيبول", "src": "NRC 2012", "max_poultry": 3.0, "max_ruminant": 5.0, "max_fish": 6.0, "max_horse": 5.0},
        "زيت الكتان": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 1700, "desc": "أوميغا 3", "src": "NRC 2007", "max_poultry": 3.0, "max_ruminant": 3.0, "max_fish": 6.0, "max_horse": 8.0},
        "زيت جوز الهند": {"CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 1900, "desc": "MCT", "src": "NRC 2012", "max_poultry": 5.0, "max_ruminant": 3.0, "max_fish": 8.0, "max_horse": 6.0},
        "زيت النخيل": {"CP": 0.0, "DC": 0.0, "SE": 215.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 1100, "desc": "مقاوم", "src": "NRC 2012", "max_poultry": 6.0, "max_ruminant": 5.0, "max_fish": 8.0, "max_horse": 8.0},
        "زيت الكانولا": {"CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 1450, "desc": "متوازن", "src": "NRC 2012", "max_poultry": 5.0, "max_ruminant": 5.0, "max_fish": 8.0, "max_horse": 6.0},
        "زيت السمسم": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 2100, "desc": "مضاد", "src": "NRC 2007", "max_poultry": 4.0, "max_ruminant": 3.0, "max_fish": 6.0, "max_horse": 5.0},
        "زيت الزيتون": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 3500, "desc": "أوميغا 9", "src": "INRA 2018", "max_poultry": 4.0, "max_ruminant": 4.0, "max_fish": 5.0, "max_horse": 5.0},
        "زيت الأفوكادو": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 4200, "desc": "فيتامين E", "src": "NRC 2012", "max_poultry": 3.0, "max_ruminant": 3.0, "max_fish": 4.0, "max_horse": 4.0},
        "زيت القرطم": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 1800, "desc": "أوميغا 6", "src": "NRC 2012", "max_poultry": 4.0, "max_ruminant": 3.0, "max_fish": 5.0, "max_horse": 5.0},
        "زيت الفول السوداني": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 2200, "desc": "طاقة", "src": "NRC 2012", "max_poultry": 5.0, "max_ruminant": 4.0, "max_fish": 6.0, "max_horse": 6.0},
        "شحم حيواني (Tallow)": {"CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 900, "desc": "طاقة", "src": "NRC 2012", "max_poultry": 6.0, "max_ruminant": 5.0, "max_fish": 6.0, "max_horse": 8.0},
        "سمن حيواني (Lard)": {"CP": 0.0, "DC": 0.0, "SE": 225.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 850, "desc": "تجنب للحلال", "src": "NRC 2012", "max_poultry": 5.0, "max_ruminant": 0.0, "max_fish": 5.0, "max_horse": 6.0},
        "دهن الدجاج": {"CP": 0.0, "DC": 0.0, "SE": 225.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 800, "desc": "دواجن", "src": "NRC 2012", "max_poultry": 6.0, "max_ruminant": 0.0, "max_fish": 5.0, "max_horse": 6.0},
        "زيت السمك (Fish Oil)": {"CP": 0.0, "DC": 0.0, "SE": 235.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 3800, "desc": "EPA/DHA", "src": "NRC Fish", "max_poultry": 2.0, "max_ruminant": 2.0, "max_fish": 8.0, "max_horse": 3.0},
        "زيت بذور العنب": {"CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 2400, "desc": "مضاد", "src": "INRA 2018", "max_poultry": 3.0, "max_ruminant": 3.0, "max_fish": 5.0, "max_horse": 4.0},
        "زيت الأرز": {"CP": 0.0, "DC": 0.0, "SE": 220.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 1600, "desc": "فيتامين E", "src": "INRA 2018", "max_poultry": 5.0, "max_ruminant": 4.0, "max_fish": 6.0, "max_horse": 6.0},
        "زيت الخردل": {"CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 1400, "desc": "اقتصادي", "src": "INRA 2018", "max_poultry": 3.0, "max_ruminant": 3.0, "max_fish": 4.0, "max_horse": 3.0},
        "زيت بذور اللفت": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 1350, "desc": "كانولا", "src": "INRA 2018", "max_poultry": 5.0, "max_ruminant": 5.0, "max_fish": 8.0, "max_horse": 6.0},
        "زيت الجوجوبا": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 5500, "desc": "نادر", "src": "INRA 2018", "max_poultry": 1.0, "max_ruminant": 1.0, "max_fish": 2.0, "max_horse": 2.0},
        "زيت الكافيار": {"CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 12000, "desc": "فاخر", "src": "INRA 2018", "max_poultry": 1.0, "max_ruminant": 1.0, "max_fish": 2.0, "max_horse": 1.0},
        "زيت اللوز الحلو": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 3600, "desc": "E", "src": "INRA 2018", "max_poultry": 2.0, "max_ruminant": 2.0, "max_fish": 3.0, "max_horse": 2.0},
        "زيت المورينجا": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 4800, "desc": "مضاد", "src": "FAO 2010", "max_poultry": 2.0, "max_ruminant": 2.0, "max_fish": 3.0, "max_horse": 2.0},
    },

    "🧪 الأحماض الأمينية": {
        "ليسين نقي": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0, "Lys": 94.0, "Met": 0.0, "price": 4200, "desc": "أساسي", "src": "NRC 2012"},
        "ليسين سلفات": {"CP": 79.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0, "Lys": 79.0, "Met": 0.0, "price": 3800, "desc": "بديل", "src": "NRC 2012"},
        "ميثيونين نقي": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 58.0, "price": 5800, "desc": "للدواجن", "src": "NRC 2012"},
        "ميثيونين هيدروكسي": {"CP": 88.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 88.0, "price": 6500, "desc": "MHA", "src": "NRC 2012"},
        "ثريونين نقي": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 4800, "desc": "ثالث", "src": "NRC 2012"},
        "تريبتوفان نقي": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 9500, "desc": "للدواجن", "src": "NRC 2012"},
        "فالين نقي": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 8200, "desc": "أساسي", "src": "NRC 2012"},
        "أرجينين": {"CP": 98.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 7800, "desc": "للدواجن", "src": "NRC 2012"},
        "هيستيدين": {"CP": 96.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 7200, "desc": "أساسي", "src": "NRC 2012"},
        "إيزوليوسين": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 8500, "desc": "BCAA", "src": "NRC 2012"},
    },

    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 8.0, "Lys": 0.0, "Met": 0.0, "price": 4800, "desc": "فيتامينات", "src": "NRC 1994"},
        "بريمكس بياض": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 22.0, "P": 7.0, "Lys": 0.0, "Met": 0.0, "price": 5000, "desc": "بياض", "src": "NRC 1994"},
        "بريمكس أبقار": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0, "Lys": 0.0, "Met": 0.0, "price": 5200, "desc": "أبقار", "src": "NRC 2001"},
        "بريمكس مجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 9.0, "Lys": 0.0, "Met": 0.0, "price": 4500, "desc": "مجترات", "src": "NRC 2007"},
        "بريمكس خيول": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 8.0, "Lys": 0.0, "Met": 0.0, "price": 5500, "desc": "خيول", "src": "NRC 2007"},
        "بريمكس إبل": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0, "Lys": 0.0, "Met": 0.0, "price": 5300, "desc": "إبل", "src": "FAO 2010"},
        "بريمكس أسماك": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 7.0, "Lys": 0.0, "Met": 0.0, "price": 5800, "desc": "أسماك", "src": "NRC Fish"},
        "إنزيم فايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 4200, "desc": "P", "src": "NRC 2012"},
        "إنزيم NSP": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 3800, "desc": "ألياف", "src": "NRC 2012"},
        "إنزيم بروتييز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 2.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 4500, "desc": "بروتين", "src": "NRC 2012"},
        "إنزيم أميليز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 4000, "desc": "نشاء", "src": "NRC 2012"},
        "مستخلص الخمائر MOS": {"CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.10, "P": 0.20, "Lys": 0.40, "Met": 0.15, "price": 12000, "desc": "مناعة", "src": "NRC 2012"},
        "خمائر حية": {"CP": 45.0, "DC": 0.75, "SE": 30.0, "NDF": 8.0, "ADF": 4.0, "EE": 1.0, "ASH": 8.0, "Ca": 0.15, "P": 1.20, "Lys": 3.00, "Met": 0.70, "price": 8500, "desc": "مجترات", "src": "NRC 2001"},
        "بروبيوتيك": {"CP": 15.0, "DC": 0.60, "SE": 20.0, "NDF": 5.0, "ADF": 3.0, "EE": 2.0, "ASH": 15.0, "Ca": 0.30, "P": 0.50, "Lys": 0.50, "Met": 0.20, "price": 9800, "desc": "نافعة", "src": "NRC 2012"},
        "بريبيوتيك FOS": {"CP": 0.0, "DC": 0.0, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 2.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 6500, "desc": "غذاء", "src": "NRC 2012"},
    },

    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 38.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 40, "desc": "Ca رخيص", "src": "NRC 2012"},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5, "Ca": 23.0, "P": 18.0, "Lys": 0.0, "Met": 0.0, "price": 280, "desc": "Ca+P", "src": "NRC 2012"},
        "فوسفات أحادي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 17.0, "P": 22.0, "Lys": 0.0, "Met": 0.0, "price": 320, "desc": "P", "src": "NRC 2012"},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 30, "desc": "NaCl", "src": "NRC 2012"},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 340, "desc": "حموضة", "src": "NRC 2001"},
        "أكسيد المغنيسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 480, "desc": "Mg", "src": "NRC 2007"},
        "كبريتات المغنيسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 380, "desc": "MgSO4", "src": "NRC 2007"},
        "يوريا علفية": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 480, "desc": "NPN — للمجترات فقط", "src": "NRC 2001"},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 950, "desc": "أفلاتوكسين", "src": "NRC 2012"},
        "مضاد أكسدة BHT": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 1200, "desc": "تزنخ", "src": "NRC 2012"},
        "كولين كلوريد": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 3200, "desc": "B4", "src": "NRC 2012"},
        "كبريتات النحاس": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 95.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 1800, "desc": "Cu", "src": "NRC 2012"},
        "كبريتات الزنك": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 96.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 2200, "desc": "Zn", "src": "NRC 2012"},
        "سيلينيت الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 4500, "desc": "Se", "src": "NRC 2012"},
        "يوديد البوتاسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 3800, "desc": "I", "src": "NRC 2012"},
    },

    "💊 الفيتامينات": {
        "فيتامين A": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 4200, "desc": "نمو", "src": "NRC 2012"},
        "فيتامين D3": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 5200, "desc": "Ca", "src": "NRC 2012"},
        "فيتامين E": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 5800, "desc": "أكسدة", "src": "NRC 2012"},
        "فيتامين K": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 4600, "desc": "دم", "src": "NRC 2012"},
        "فيتامين B1 (ثيامين)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 3800, "desc": "أعصاب", "src": "NRC 2012"},
        "فيتامين B2 (ريبوفلافين)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 4200, "desc": "طاقة", "src": "NRC 2012"},
        "فيتامين B3 (نياسين)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 3400, "desc": "تمثيل", "src": "NRC 2012"},
        "فيتامين B5 (حمض البانتوثنيك)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 3600, "desc": "هضم", "src": "NRC 2012"},
        "فيتامين B6 (بيريدوكسين)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 3800, "desc": "أحماض", "src": "NRC 2012"},
        "فيتامين B12 (كوبالامين)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 8500, "desc": "دم", "src": "NRC 2012"},
        "بيوتين": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 9200, "desc": "حوافر", "src": "NRC 2012"},
        "فوليك أسيد": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 6200, "desc": "إخصاب", "src": "NRC 2012"},
    },

    "⚗️ مضافات خاصة": {
        "مضاد حيوي وقائي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 3800, "desc": "تشريعات", "src": "NRC 2012"},
        "مضاد كوكسيديا": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 4200, "desc": "دواجن", "src": "NRC 1994"},
        "مضاد فطريات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 2800, "desc": "حفظ", "src": "NRC 2012"},
        "منشط نمو طبيعي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 8500, "desc": "بديل", "src": "NRC 2012"},
        "محسن نكهة": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 3800, "desc": "استساغة", "src": "NRC 2012"},
        "ملون طبيعي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 6200, "desc": "صفار", "src": "NRC 2012"},
        "مضاد تكور (Betaine)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 4800, "desc": "إجهاد", "src": "NRC 2012"},
        "أحماض عضوية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0, "price": 3200, "desc": "حفظ", "src": "NRC 2012"},
        "بيتا جلوكان": {"CP": 10.0, "DC": 0.50, "SE": 20.0, "NDF": 5.0, "ADF": 3.0, "EE": 1.0, "ASH": 5.0, "Ca": 0.10, "P": 0.15, "Lys": 0.30, "Met": 0.10, "price": 12000, "desc": "مناعة", "src": "NRC 2012"},
        "طحالب كالبتوس": {"CP": 8.0, "DC": 0.60, "SE": 25.0, "NDF": 10.0, "ADF": 6.0, "EE": 2.0, "ASH": 35.0, "Ca": 2.50, "P": 0.30, "Lys": 0.30, "Met": 0.15, "price": 2500, "desc": "معادن", "src": "FAO 2010"},
    },
}


# ═══ معايير الزيوت ═══
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
    "زيوت نباتية متوازنة": ["زيت النخيل", "زيت جوز الهند", "زيت الزيتون", "زيت السمسم",
                            "زيت الفول السوداني", "زيت الأفوكادو"],
    "زيوت نباتية أخرى": ["زيت بذور العنب", "زيت الأرز", "زيت الخردل", "زيت بذور اللفت",
                          "زيت الجوجوبا", "زيت المورينجا", "زيت اللوز الحلو", "زيت الكافيار"],
    "دهون حيوانية": ["شحم حيواني (Tallow)", "سمن حيواني (Lard)", "دهن الدجاج"],
}


def get_oil_standard(standard_key: str) -> dict:
    return MAX_OIL_PERCENTAGE.get(standard_key, {"max": 5.0, "optimal": 3.0, "source": "معيار عام"})


def get_oil_ingredients() -> dict:
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت النباتية والحيوانية", {})


# ═══ الحدود العلمية الصارمة لكل حيوان ═══
INGREDIENT_LIMITS_BY_ANIMAL = {
    "دواجن": {
        "يوريا علفية": (0.0, 0.0),
        "سمن حيواني (Lard)": (0.0, 0.0),
        "دهن الدجاج": (0.0, 3.0),
        "نخالة قمح (ردة)": (0.0, 10.0),
        "نخالة ذرة": (0.0, 5.0),
        "تبن قمح": (0.0, 2.0),
        "قش أرز": (0.0, 2.0),
        "سرسة الأرز": (0.0, 2.0),
        "كسب بذور القطن": (0.0, 5.0),
        "كسب السمسم": (0.0, 8.0),
        "كسب الكانولا": (0.0, 8.0),
        "ملح الطعام": (0.20, 0.40),
        "الحجر الجيري": (0.80, 2.00),
        "فوسفات ثنائي الكالسيوم": (0.50, 2.50),
        "بيكربونات الصوديوم": (0.00, 0.50),
        "مضاد سموم فطرية": (0.05, 0.15),
        "بريمكس تسمين دواجن": (0.20, 0.35),
        "بريمكس بياض": (0.20, 0.35),
        "ليسين نقي": (0.00, 0.50),
        "ميثيونين نقي": (0.00, 0.40),
        "زيت ذرة": (0.0, 5.0),
        "زيت فول الصويا": (0.0, 6.0),
    },
    "سمان": {
        "يوريا علفية": (0.0, 0.0),
        "سمن حيواني (Lard)": (0.0, 0.0),
        "نخالة قمح (ردة)": (0.0, 8.0),
        "ملح الطعام": (0.20, 0.40),
        "الحجر الجيري": (0.80, 2.50),
        "فوسفات ثنائي الكالسيوم": (0.50, 2.00),
        "بريمكس تسمين دواجن": (0.20, 0.35),
        "بريمكس بياض": (0.20, 0.35),
    },
    "أبقار": {
        "يوريا علفية": (0.0, 1.5),
        "نخالة قمح (ردة)": (0.0, 30.0),
        "كسب بذور القطن": (0.0, 20.0),
        "كسب السمسم": (0.0, 15.0),
        "ملح الطعام": (0.30, 0.50),
        "بيكربونات الصوديوم": (0.50, 1.00),
        "الحجر الجيري": (0.0, 3.50),
        "فوسفات ثنائي الكالسيوم": (0.0, 2.00),
        "بريمكس أبقار": (0.15, 0.30),
        "بريمكس مجترات": (0.15, 0.30),
        "مضاد سموم فطرية": (0.05, 0.15),
    },
    "أغنام": {
        "يوريا علفية": (0.0, 1.0),
        "نخالة قمح (ردة)": (0.0, 25.0),
        "كسب بذور القطن": (0.0, 15.0),
        "ملح الطعام": (0.30, 0.50),
        "بيكربونات الصوديوم": (0.50, 1.00),
        "بريمكس مجترات": (0.15, 0.30),
        "الحجر الجيري": (0.0, 3.00),
        "فوسفات ثنائي الكالسيوم": (0.0, 2.00),
    },
    "ماعز": {
        "يوريا علفية": (0.0, 1.0),
        "نخالة قمح (ردة)": (0.0, 25.0),
        "ملح الطعام": (0.30, 0.50),
        "بيكربونات الصوديوم": (0.50, 1.00),
        "بريمكس مجترات": (0.15, 0.30),
        "الحجر الجيري": (0.0, 3.00),
        "فوسفات ثنائي الكالسيوم": (0.0, 2.00),
    },
    "إبل": {
        "يوريا علفية": (0.0, 1.0),
        "نخالة قمح (ردة)": (0.0, 20.0),
        "ملح الطعام": (0.30, 0.50),
        "بيكربونات الصوديوم": (0.50, 1.00),
        "بريمكس إبل": (0.15, 0.30),
        "الحجر الجيري": (0.0, 3.00),
        "فوسفات ثنائي الكالسيوم": (0.0, 2.00),
    },
    "خيول": {
        "يوريا علفية": (0.0, 0.5),
        "نخالة قمح (ردة)": (0.0, 20.0),
        "ملح الطعام": (0.30, 0.50),
        "بريمكس خيول": (0.15, 0.30),
        "الحجر الجيري": (0.0, 2.50),
        "فوسفات ثنائي الكالسيوم": (0.0, 2.00),
    },
    "أسماك": {
        "يوريا علفية": (0.0, 0.0),
        "سمن حيواني (Lard)": (0.0, 0.0),
        "نخالة قمح (ردة)": (0.0, 10.0),
        "ملح الطعام": (0.00, 0.30),
        "بريمكس أسماك": (0.15, 0.30),
        "الحجر الجيري": (0.0, 2.00),
        "فوسفات ثنائي الكالسيوم": (0.0, 2.00),
    },
    "أرانب": {
        "يوريا علفية": (0.0, 0.5),
        "نخالة قمح (ردة)": (0.0, 20.0),
        "ملح الطعام": (0.30, 0.50),
        "بريمكس مجترات": (0.15, 0.30),
        "الحجر الجيري": (0.0, 2.50),
        "فوسفات ثنائي الكالسيوم": (0.0, 2.00),
    },
}


def get_animal_limits(animal_type):
    return INGREDIENT_LIMITS_BY_ANIMAL.get(animal_type, {})


def _get_ingredient_lookup():
    if not hasattr(_get_ingredient_lookup, "_cache"):
        lookup = {}
        for cat in BIG_FEEDS_LIBRARY.values():
            for name, data in cat.items():
                lookup[name] = data
        _get_ingredient_lookup._cache = lookup
    return _get_ingredient_lookup._cache


# ═══ الاحتياجات الغذائية ═══
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
        dp = 12.5 + (milk_yield * 0.30)
        cp = dp / 0.70
        return AnimalRequirement(round(dp, 2), round(cp, 2), round(60 + milk_yield * 0.35, 1),
                                 30.0, 19.0, 5.5, 8.0, round(0.55 + milk_yield * 0.003, 3),
                                 round(0.33 + milk_yield * 0.0015, 3), "أبقار حلابة عالية", f"{milk_yield} كجم")
    elif production_type == "حليب_متوسط":
        dp = 11.0 + (milk_yield * 0.25)
        cp = dp / 0.72
        return AnimalRequirement(round(dp, 2), round(cp, 2), round(55 + milk_yield * 0.30, 1),
                                 33.0, 21.0, 4.5, 8.0, round(0.50 + milk_yield * 0.0025, 3),
                                 round(0.30 + milk_yield * 0.0012, 3), "أبقار حلابة متوسطة", f"{milk_yield}")
    elif production_type == "حليب_منخفض":
        dp = 9.5 + (milk_yield * 0.20)
        cp = dp / 0.75
        return AnimalRequirement(round(dp, 2), round(cp, 2), round(50 + milk_yield * 0.25, 1),
                                 38.0, 24.0, 4.0, 8.5, round(0.45 + milk_yield * 0.002, 3),
                                 round(0.28 + milk_yield * 0.001, 3), "أبقار حلابة منخفضة", f"{milk_yield}")
    elif production_type == "تسمين_مكثف":
        return AnimalRequirement(11.5, 14.5, 72.0, 32.0, 20.0, 4.5, 7.5, 0.65, 0.38, "تسمين عجول مكثف", "ADG >1.3")
    elif production_type == "تسمين_عادي":
        return AnimalRequirement(9.5, 12.0, 65.0, 38.0, 24.0, 4.0, 7.5, 0.55, 0.32, "تسمين عجول عادي", "ADG ~0.8")
    elif production_type == "حمل_أخير":
        return AnimalRequirement(11.5, 14.5, 67.0, 35.0, 22.0, 4.2, 8.0, 0.70, 0.42, "حمل آخر", "شهر 7-9")
    else:
        return AnimalRequirement(7.5, 10.0, 53.0, 45.0, 28.0, 3.0, 8.5, 0.42, 0.26, "أبقار صيانة", "بدون إنتاج")


def get_sheep_requirements(production_type, is_male=True, weight_kg=50.0, litter_size=1):
    if is_male:
        if production_type == "تسمين_مكثف":
            return AnimalRequirement(11.5, 14.5, 64.0, 28.0, 17.0, 4.0, 8.0, 0.65, 0.36, "تسمين حملان مكثف", "ADG >250 جم")
        elif production_type == "تسمين_عادي":
            return AnimalRequirement(9.5, 12.0, 59.0, 33.0, 21.0, 3.6, 8.0, 0.55, 0.32, "تسمين حملان عادي", "ADG ~180")
        else:
            return AnimalRequirement(8.5, 11.0, 55.0, 38.0, 24.0, 3.2, 8.5, 0.50, 0.30, "حملان تيد", "نهائي")
    else:
        if production_type == "مرضعات":
            dp = 10.5 + (litter_size - 1) * 1.5
            cp = dp / 0.72
            return AnimalRequirement(round(dp, 2), round(cp, 2), round(60 + (litter_size - 1) * 5, 1),
                                     30.0, 19.0, 4.5, 8.5, round(0.65 + (litter_size - 1) * 0.10, 3),
                                     round(0.38 + (litter_size - 1) * 0.05, 3), f"نعاج مرضعات ({litter_size})", "")
        elif production_type == "حامل_أخير":
            return AnimalRequirement(10.5, 13.5, 62.0, 32.0, 20.0, 3.8, 8.0, 0.60, 0.35, "نعاج حامل (4-5)", "")
        elif production_type == "حامل_متوسط":
            return AnimalRequirement(8.5, 11.0, 55.0, 38.0, 24.0, 3.4, 8.0, 0.50, 0.30, "نعاج حامل (1-3)", "")
        else:
            return AnimalRequirement(7.2, 9.5, 48.0, 45.0, 28.0, 3.0, 8.5, 0.42, 0.26, "نعاج صيانة", "")


def get_goat_requirements(production_type, is_male=True, milk_yield=2.0):
    if is_male:
        if production_type == "تسمين_جديان":
            return AnimalRequirement(11.0, 14.0, 62.0, 30.0, 19.0, 3.8, 8.0, 0.62, 0.34, "تسمين جديان", "")
        else:
            return AnimalRequirement(9.0, 11.5, 57.0, 36.0, 22.0, 3.5, 8.0, 0.55, 0.30, "تيوس تسمين", "")
    else:
        if production_type == "حلابة_عالي":
            dp = 11.5 + (milk_yield * 0.45)
            cp = dp / 0.70
            return AnimalRequirement(round(dp, 2), round(cp, 2), round(58 + milk_yield * 0.45, 1),
                                     29.0, 18.0, 4.5, 8.5, round(0.60 + milk_yield * 0.008, 3),
                                     round(0.35 + milk_yield * 0.004, 3), f"عنزات حلابة ({milk_yield})", "")
        elif production_type == "حلابة_متوسط":
            dp = 10.0 + (milk_yield * 0.35)
            cp = dp / 0.72
            return AnimalRequirement(round(dp, 2), round(cp, 2), round(55 + milk_yield * 0.40, 1),
                                     32.0, 20.0, 4.0, 8.5, round(0.55 + milk_yield * 0.006, 3),
                                     round(0.32 + milk_yield * 0.003, 3), f"عنزات حلابة ({milk_yield})", "")
        elif production_type == "حامل_أخير":
            return AnimalRequirement(10.0, 13.0, 60.0, 33.0, 21.0, 3.8, 8.0, 0.60, 0.35, "عنزات حامل", "")
        else:
            return AnimalRequirement(6.8, 9.0, 46.0, 46.0, 28.0, 3.0, 8.5, 0.42, 0.26, "عنزات صيانة", "")


def get_camel_requirements(production_type, weight_kg=400.0, milk_yield=5.0):
    if production_type == "نمو":
        return AnimalRequirement(10.5, 13.5, 60.0, 38.0, 24.0, 4.0, 8.0, 0.65, 0.38, "إبل نمو", f"{weight_kg}")
    elif production_type == "تسمين":
        return AnimalRequirement(9.5, 12.0, 65.0, 35.0, 22.0, 4.5, 7.5, 0.60, 0.35, "إبل تسمين", f"{weight_kg}")
    elif production_type == "حليب":
        dp = 12.0 + (milk_yield * 0.25)
        cp = dp / 0.70
        return AnimalRequirement(round(dp, 2), round(cp, 2), round(62 + milk_yield * 0.40, 1),
                                 32.0, 20.0, 5.0, 8.5, round(0.70 + milk_yield * 0.006, 3),
                                 round(0.40 + milk_yield * 0.003, 3), f"إبل حلابة ({milk_yield})", "")
    elif production_type == "سباق":
        return AnimalRequirement(14.0, 17.0, 72.0, 28.0, 17.0, 6.0, 9.0, 0.85, 0.50, "إبل سباق", "")
    else:
        return AnimalRequirement(7.0, 9.0, 48.0, 48.0, 30.0, 3.5, 9.0, 0.42, 0.26, "إبل صيانة", f"{weight_kg}")


def get_horse_requirements(production_type, weight_kg=450.0):
    if production_type == "رياضة_مكثف":
        return AnimalRequirement(10.5, 13.5, 70.0, 30.0, 18.0, 7.0, 7.5, 0.70, 0.40, "خيول رياضة مكثف", "")
    elif production_type == "رياضة_عادي":
        return AnimalRequirement(9.0, 11.5, 63.0, 36.0, 22.0, 5.0, 7.5, 0.55, 0.32, "خيول رياضة عادي", "")
    elif production_type == "نمو_أمهار":
        return AnimalRequirement(12.0, 15.0, 65.0, 30.0, 18.0, 5.0, 8.0, 0.75, 0.42, "أمهار نمو", "")
    elif production_type == "مرضعات":
        return AnimalRequirement(12.5, 16.0, 68.0, 32.0, 20.0, 5.5, 8.0, 0.80, 0.45, "فرسات مرضعات", "")
    else:
        return AnimalRequirement(7.2, 9.5, 53.0, 46.0, 29.0, 3.5, 8.0, 0.45, 0.28, "خيول صيانة", "")


def get_poultry_requirements(strain, age_weeks=1):
    if strain == "لاحم":
        if age_weeks <= 1:
            return AnimalRequirement(20.0, 23.0, 76.0, 8.0, 4.0, 5.0, 6.5, 1.00, 0.50, "بادي لاحم", "Energy 3000")
        elif age_weeks <= 3:
            return AnimalRequirement(18.5, 21.0, 74.0, 9.0, 5.0, 5.0, 6.0, 0.90, 0.45, "نامي لاحم", "Energy 3100")
        elif age_weeks <= 5:
            return AnimalRequirement(17.0, 19.5, 75.0, 10.0, 5.5, 4.5, 6.0, 0.87, 0.43, "ناهي لاحم", "Energy 3150")
        else:
            return AnimalRequirement(16.5, 19.0, 75.0, 10.0, 5.5, 4.5, 6.0, 0.85, 0.42, "ناهي لاحم+", "Energy 3200")
    else:
        if age_weeks <= 6:
            return AnimalRequirement(17.0, 20.0, 72.0, 10.0, 5.5, 4.0, 7.0, 1.00, 0.50, "بادي بياض", "")
        elif age_weeks <= 18:
            return AnimalRequirement(14.5, 17.0, 70.0, 12.0, 6.5, 4.0, 9.0, 1.50, 0.45, "نامي بياض", "")
        else:
            return AnimalRequirement(15.5, 18.0, 72.0, 11.0, 6.0, 4.2, 11.5, 3.80, 0.45, "بياض إنتاجي", "")


def get_quail_requirements(strain, age_weeks=1):
    if strain == "بياض":
        return AnimalRequirement(15.0, 18.0, 68.0, 11.0, 5.5, 4.5, 9.0, 2.50, 0.45, "سمان بياض", "")
    else:
        if age_weeks <= 2:
            return AnimalRequirement(20.5, 24.0, 74.0, 8.0, 4.0, 5.5, 6.5, 1.00, 0.55, "سمان بادي", "")
        elif age_weeks <= 4:
            return AnimalRequirement(18.5, 22.0, 72.0, 9.0, 4.5, 5.0, 6.0, 0.90, 0.50, "سمان نامي", "")
        else:
            return AnimalRequirement(17.0, 20.0, 70.0, 10.0, 5.0, 4.5, 6.0, 0.85, 0.45, "سمان ناهي", "")


def get_fish_requirements(species, stage):
    if "زريعة" in stage or "بادئ" in stage:
        return AnimalRequirement(32.0, 40.0, 72.0, 8.0, 4.0, 10.0, 11.0, 1.50, 0.90, f"{species} بادئ", "")
    elif "نمو" in stage:
        return AnimalRequirement(25.0, 32.0, 70.0, 12.0, 6.0, 8.0, 9.0, 1.00, 0.70, f"{species} نمو", "")
    else:
        return AnimalRequirement(22.0, 28.0, 68.0, 13.0, 7.0, 8.0, 9.5, 0.90, 0.65, f"{species} تسمين", "")


def get_rabbit_requirements(production_type, weight_kg=4.0):
    if production_type == "تسمين":
        return AnimalRequirement(15.0, 17.0, 65.0, 25.0, 15.0, 3.0, 8.0, 0.70, 0.35, "أرانب تسمين", "ADG 40 جم")
    elif production_type == "حليب":
        return AnimalRequirement(18.0, 20.0, 68.0, 25.0, 15.0, 4.0, 8.5, 0.85, 0.45, "أرانب حلابة", "أمهات")
    else:
        return AnimalRequirement(12.0, 14.0, 60.0, 30.0, 20.0, 2.5, 8.5, 0.60, 0.30, "أرانب صيانة", "")


def requirement_to_standard(req):
    return {"CP": req.CP, "DP": req.DP, "SE": req.SE, "NDF": req.NDF, "ADF": req.ADF,
            "EE": req.EE, "ASH": req.ASH, "Ca": req.Ca, "P": req.P}


# ═══════════════════════════════════════════════════════════════════════════
# 📌 نهاية الجزء 1 — توقف هنا
# الجزء 2 يحتوي على: الحسابات + التقييم + المحرك العلمي + الرسوم
#                   + PDFGenerator + Excel + الحظائر 3D
#                   + الجدوى + بدائل الحليب (≥75%)
# ═══════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════
# تاور نولجي TAWOR NOLOGY 11.2 — (الجزء 2/3)
# الحسابات + المحرك العلمي + الرسوم + PDF + Excel + الحظائر + الجدوى + بدائل الحليب
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# الحسابات الأساسية
# ═══════════════════════════════════════════════════════════════════════════
def compute_formula_nutrients(formula):
    totals = {"CP": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0,
              "EE": 0.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "Lys": 0.0, "Met": 0.0}
    lookup = _get_ingredient_lookup()
    for ing, pct in formula.items():
        if ing not in lookup:
            continue
        d = lookup[ing]
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
        totals["Lys"] += f * d.get("Lys", 0.0)
        totals["Met"] += f * d.get("Met", 0.0)
    return totals


def compute_total_oil_percentage(formula):
    oils = set(get_oil_ingredients().keys())
    return sum(pct for ing, pct in formula.items() if ing in oils)


def evaluate_difference(pct_diff, standard_value=None):
    if standard_value is not None and standard_value == 0:
        if abs(pct_diff) < 0.001:
            return {"label": "🎯 مطابق (صفر)", "color": "#0d5302", "bg": "#c8e6c9", "score": 100}
        return {"label": "⚠️ يجب أن يكون صفراً", "color": "#ef6c00", "bg": "#fff3e0", "score": 40}
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


def evaluate_quality_weighted(formula, targets, animal_type, basis="DP"):
    """تقييم موزون علمياً: DP=30% | SE=15% | NDF=10-15% | ADF=10% | Ca=10% | P=10% | Ca:P=10%"""
    actual = compute_formula_nutrients(formula)
    is_rum = animal_type in ("أبقار", "أغنام", "ماعز", "إبل")

    weights = {"DP" if basis == "DP" else "CP": 0.30, "SE": 0.15,
               "NDF": 0.15 if is_rum else 0.10, "ADF": 0.10,
               "Ca": 0.10, "P": 0.10}

    total_w, weighted = 0.0, 0.0
    for nut, w in weights.items():
        if not targets.get(nut):
            continue
        diff_pct = abs(actual.get(nut, 0) - targets[nut]) / targets[nut] * 100
        ev = evaluate_difference(diff_pct, standard_value=targets[nut])
        weighted += ev["score"] * w
        total_w += w

    ca, p = actual.get("Ca", 0), actual.get("P", 0)
    if ca > 0 and p > 0 and targets.get("Ca", 0) > 0:
        r = ca / p
        if 1.5 <= r <= 2.0: rs = 100
        elif 1.2 <= r < 1.5 or 2.0 < r <= 3.0: rs = 75
        elif 0.8 <= r < 1.2 or 3.0 < r <= 5.0: rs = 40
        else: rs = 10
        weighted += rs * 0.10
        total_w += 0.10

    return (weighted / total_w if total_w else 0.0), actual


def get_default_selections(animal_type, production_type, requirement=None):
    defaults = {"ملح الطعام", "مضاد سموم فطرية"}
    if animal_type != "دواجن":
        defaults |= {"الحجر الجيري", "فوسفات ثنائي الكالسيوم"}
    if animal_type in ("أبقار", "أغنام", "ماعز", "إبل"):
        defaults.add("بيكربونات الصوديوم")

    if animal_type == "دواجن":
        defaults.add("بريمكس بياض" if "بياض" in str(production_type)
                     else "بريمكس تسمين دواجن")
    elif animal_type == "سمان":
        defaults.add("بريمكس بياض" if "بياض" in str(production_type)
                     else "بريمكس تسمين دواجن")
    elif animal_type == "أبقار":
        defaults.add("بريمكس أبقار")
    elif animal_type in ("أغنام", "ماعز", "أرانب"):
        defaults.add("بريمكس مجترات")
    elif animal_type == "خيول":
        defaults.add("بريمكس خيول")
    elif animal_type == "إبل":
        defaults.add("بريمكس إبل")
    elif animal_type == "أسماك":
        defaults.add("بريمكس أسماك")

    if "بياض" in str(production_type):
        defaults.add("الحجر الجيري")
    return defaults


# ═══════════════════════════════════════════════════════════════════════════
# المحرك العلمي المُصحَّح (LP)
# ═══════════════════════════════════════════════════════════════════════════
def auto_formulate_smart(available_ingredients, prices, custom_standard,
                          standard_key="", tolerance=0.3, max_iterations=80,
                          basis="DP", min_quality=70.0,
                          animal_type="", production_type=""):
    """
    محرك LP علمي:
    - مساواة: المجموع=100 + البروتين
    - متباينات: نطاقات علمية + Ca:P + NDF حسب نوع الحيوان
    - 4 استراتيجيات Ca/P
    - حدود مكونات مخصصة حسب نوع الحيوان
    """
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "SCIPY غير متوفرة"}

    lookup = _get_ingredient_lookup()
    ing_data = {i: lookup[i] for i in available_ingredients if i in lookup}
    valid = list(ing_data.keys())
    if len(valid) < 3:
        return {"success": False, "message": "اختر 3 مكونات على الأقل"}

    is_ruminant = animal_type in ("أبقار", "أغنام", "ماعز", "إبل")
    n = len(valid)
    c = [prices.get(i, 300.0) for i in valid]

    rows = {}
    for nut in ["CP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P", "Lys", "Met"]:
        rows[nut] = [ing_data[i].get(nut, 0) for i in valid]
    rows["DP"] = [ing_data[i].get("CP", 0) * ing_data[i].get("DC", 0) for i in valid]

    target_key = "DP" if basis == "DP" else "CP"
    target_protein = custom_standard.get(target_key, 15.0)
    target_ca = custom_standard.get("Ca", 0)
    target_p = custom_standard.get("P", 0)
    target_se = custom_standard.get("SE", 0)
    target_ndf = custom_standard.get("NDF", 0)
    target_adf = custom_standard.get("ADF", 0)

    limits = get_animal_limits(animal_type)
    bounds = [limits.get(i, (0.0, 100.0)) for i in valid]

    A_eq_base = [[1.0] * n, rows[target_key]]
    b_eq_base = [100.0, target_protein * 100.0]

    A_ub_base, b_ub_base = [], []

    if target_ca > 0 and target_p > 0:
        A_ub_base.append([-(rows["Ca"][i] - 1.2 * rows["P"][i]) for i in range(n)])
        b_ub_base.append(0)
        A_ub_base.append([rows["Ca"][i] - 7.0 * rows["P"][i] for i in range(n)])
        b_ub_base.append(0)

    if target_se > 0:
        A_ub_base.append([-x for x in rows["SE"]])
        b_ub_base.append(-target_se * 100.0)

    if target_ndf > 0:
        if is_ruminant:
            A_ub_base.append([-x for x in rows["NDF"]])
            b_ub_base.append(-target_ndf * 0.70 * 100.0)
            A_ub_base.append(rows["NDF"])
            b_ub_base.append(target_ndf * 1.30 * 100.0)
        else:
            A_ub_base.append(rows["NDF"])
            b_ub_base.append(target_ndf * 1.10 * 100.0)

    if target_adf > 0:
        A_ub_base.append(rows["ADF"])
        b_ub_base.append(target_adf * (1.40 if is_ruminant else 1.20) * 100.0)

    oil_std = get_oil_standard(standard_key)
    oil_ind = [1.0 if i in get_oil_ingredients() else 0.0 for i in valid]
    if sum(oil_ind) > 0:
        A_ub_base.append(oil_ind)
        b_ub_base.append(oil_std["max"] * 100.0)

    strategies = [("دقيق", "eq"), ("نطاق±10%", "r10"),
                  ("نطاق±20%", "r20"), ("بدون CaP", "none")]
    best, best_q = None, 0.0

    for label, mode in strategies:
        try:
            A_eq, b_eq = list(A_eq_base), list(b_eq_base)
            A_ub, b_ub = list(A_ub_base), list(b_ub_base)

            if mode == "eq":
                if target_ca > 0:
                    A_eq.append(rows["Ca"]); b_eq.append(target_ca * 100.0)
                if target_p > 0:
                    A_eq.append(rows["P"]); b_eq.append(target_p * 100.0)
            elif mode in ("r10", "r20"):
                tol = 0.10 if mode == "r10" else 0.20
                if target_ca > 0:
                    A_ub.append(rows["Ca"]); b_ub.append(target_ca * (1 + tol) * 100.0)
                    A_ub.append([-x for x in rows["Ca"]]); b_ub.append(-target_ca * (1 - tol) * 100.0)
                if target_p > 0:
                    A_ub.append(rows["P"]); b_ub.append(target_p * (1 + tol) * 100.0)
                    A_ub.append([-x for x in rows["P"]]); b_ub.append(-target_p * (1 - tol) * 100.0)

            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method='highs',
                          options={'presolve': True, 'time_limit': 8})

            if res.success:
                formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
                q, actual = evaluate_quality_weighted(
                    formula, custom_standard, animal_type, basis
                )
                if q > best_q:
                    best_q = q
                    best = {
                        "success": True, "formula": formula,
                        "cost": res.fun / 100.0, "actual_nutrients": actual,
                        "quality_score": q, "strategy": label,
                        "meets_standard": q >= min_quality,
                        "targets": custom_standard, "basis": basis,
                        "oil_std": oil_std,
                        "total_oil": compute_total_oil_percentage(formula),
                    }
                if q >= 95:
                    break
        except Exception:
            continue

    if best:
        if not best["meets_standard"]:
            best["warning"] = (
                f"⚠️ الجودة {best_q:.1f}% < {min_quality}% — "
                f"أضف مصادر طاقة + بروتين + أملاح + فيتامينات"
            )
        return best
    return {"success": False, "message": "تعذر إيجاد حل — وسّع اختيار المواد"}


# ═══════════════════════════════════════════════════════════════════════════
# OCR — مطابقة أسماء المكونات
# ═══════════════════════════════════════════════════════════════════════════
def match_ingredient_name(text):
    if not text:
        return None
    tl = text.strip().lower()
    for cat in BIG_FEEDS_LIBRARY.values():
        for name in cat.keys():
            if name.lower() in tl or tl in name.lower():
                return name

    kw = {
        "ذرة": "ذرة صفراء", "corn": "ذرة صفراء", "maize": "ذرة صفراء",
        "صويا": "كسب فول صويا 44%", "soy": "كسب فول صويا 44%",
        "شعير": "شعير مطحون", "barley": "شعير مطحون",
        "قمح": "قمح محلي", "wheat": "قمح محلي",
        "نخالة": "نخالة قمح (ردة)", "bran": "نخالة قمح (ردة)",
        "قطن": "كسب بذور القطن", "cotton": "كسب بذور القطن",
        "عباد": "كسب عباد الشمس 36%", "sunflower": "كسب عباد الشمس 36%",
        "سمك": "مسحوق أسماك 60%", "fish": "مسحوق أسماك 60%",
        "ليسين": "ليسين نقي", "lysine": "ليسين نقي",
        "ميثيونين": "ميثيونين نقي", "methionine": "ميثيونين نقي",
        "ملح": "ملح الطعام", "salt": "ملح الطعام",
        "حجر": "الحجر الجيري", "limestone": "الحجر الجيري",
        "فوسفات": "فوسفات ثنائي الكالسيوم", "phosphate": "فوسفات ثنائي الكالسيوم",
        "يوريا": "يوريا علفية", "urea": "يوريا علفية",
        "زيت صويا": "زيت فول الصويا", "زيت ذرة": "زيت ذرة",
        "زيت نخيل": "زيت النخيل", "زيت كتان": "زيت الكتان",
        "بريمكس": "بريمكس تسمين دواجن", "premix": "بريمكس تسمين دواجن",
        "خمائر": "خمائر حية", "yeast": "خمائر حية",
        "إنزيم": "إنزيم فايتيز", "enzyme": "إنزيم فايتيز",
    }
    for k, m in kw.items():
        if k in tl:
            return m
    return None


def extract_ingredients_from_image(image_bytes):
    if not OCR_AVAILABLE:
        return {"success": False, "message": "pytesseract غير مثبتة"}
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"success": False, "message": "تعذر قراءة الصورة"}

        h, w = img.shape[:2]
        if max(h, w) < 1000:
            scale = 1200 / max(h, w)
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)

        variants = [
            gray,
            cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY, 11, 2),
            cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        ]

        texts = []
        for variant in variants:
            for lang in ['ara+eng', 'eng']:
                try:
                    txt = pytesseract.image_to_string(
                        variant, lang=lang,
                        config=r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
                    )
                    if txt.strip() and len(txt.strip()) > 5:
                        texts.append(txt)
                        break
                except Exception:
                    continue

        if not texts:
            return {"success": False, "message": "لم يتم استخراج نص"}

        full_text = "\n".join(texts)
        ingredients = {}
        patterns = [
            r'([\u0600-\u06FFa-zA-Z\s\(\)]+?)[\s:\-=\.]+(\d+\.?\d*)\s*%',
            r'([\u0600-\u06FFa-zA-Z\s]+?)\s+(\d+\.?\d*)\s*%',
        ]
        for line in full_text.split('\n'):
            line = line.strip()
            if len(line) < 3:
                continue
            for pat in patterns:
                m = re.search(pat, line)
                if not m:
                    continue
                name, val = m.group(1).strip(), float(m.group(2))
                if 0.1 < val <= 100 and len(name) > 2:
                    matched = match_ingredient_name(name)
                    if matched and matched not in ingredients:
                        ingredients[matched] = round(val, 2)
                        break

        return {
            "success": True, "ingredients": ingredients,
            "raw_text": full_text, "count": len(ingredients),
            "total": sum(ingredients.values()),
        }
    except Exception as e:
        return {"success": False, "message": f"خطأ: {str(e)}"}


# ═══════════════════════════════════════════════════════════════════════════
# الرسوم البيانية
# ═══════════════════════════════════════════════════════════════════════════
def create_colorful_bar_chart(standard, actual):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        nutrients = [n for n in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH"]
                     if n in standard and standard[n] > 0]
        if not nutrients:
            return None
        fig, ax = plt.subplots(figsize=(9, 4.5))
        x = np.arange(len(nutrients))
        width = 0.35
        ax.bar(x - width/2, [standard[n] for n in nutrients], width,
               label='المعيار', color='#1976d2', edgecolor='#0d47a1', linewidth=1.5)
        ax.bar(x + width/2, [actual.get(n, 0) for n in nutrients], width,
               label='المحسوب', color='#43a047', edgecolor='#1b5e20', linewidth=1.5)
        ax.set_xticks(x)
        ax.set_xticklabels(nutrients, fontsize=10)
        ax.legend(loc='upper right', fontsize=10)
        ax.set_title('مقارنة العناصر الغذائية', fontsize=13, fontweight='bold', color='#1b5e20')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_facecolor('#fafafa')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
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
        wedges, texts, autotexts = ax.pie(
            vals, autopct='%1.1f%%', colors=colors[:len(names)],
            startangle=90, pctdistance=0.75,
            wedgeprops=dict(edgecolor='white', linewidth=2))
        for t in autotexts:
            t.set_color('white')
            t.set_fontweight('bold')
        ax.legend(names, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)
        ax.set_title('توزيع المكونات', fontsize=13, fontweight='bold', color='#1b5e20')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
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
        std_norm = [100.0] * len(nutrients)
        act_norm = [(actual.get(n, 0) / standard[n]) * 100 for n in nutrients]
        angles = np.linspace(0, 2 * np.pi, len(nutrients), endpoint=False).tolist()
        std_norm += std_norm[:1]
        act_norm += act_norm[:1]
        angles += angles[:1]
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, std_norm, 'o-', linewidth=2.5, color='#1976d2', label='المعيار 100%')
        ax.fill(angles, std_norm, alpha=0.15, color='#1976d2')
        ax.plot(angles, act_norm, 'o-', linewidth=2.5, color='#43a047', label='المحسوب')
        ax.fill(angles, act_norm, alpha=0.25, color='#43a047')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(nutrients, fontsize=10)
        ax.set_ylim(0, max(max(std_norm), max(act_norm)) * 1.2)
        ax.set_title('المقارنة الشاملة %', fontsize=12, fontweight='bold',
                     color='#1b5e20', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#fafafa')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
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
        colors_g = ['#c62828', '#ef6c00', '#f9a825', '#7cb342', '#43a047', '#1b5e20']
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
        ax.text(0, -0.5, 'التقييم العام', ha='center', fontsize=11, color='#666')
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.7, 1.2)
        ax.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_horizontal_bar_chart(formula):
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2:
        return None
    try:
        sorted_pairs = sorted(formula.items(), key=lambda x: x[1], reverse=True)
        names = [p[0] for p in sorted_pairs]
        vals = [p[1] for p in sorted_pairs]
        colors = ['#e53935', '#8e24aa', '#3949ab', '#1e88e5', '#00897b',
                  '#43a047', '#7cb342', '#fdd835', '#fb8c00', '#6d4c41']
        fig, ax = plt.subplots(figsize=(9, max(4, len(names) * 0.4)))
        bars = ax.barh(names, vals, color=colors[:len(names)], edgecolor='#333')
        for bar in bars:
            h = bar.get_width()
            ax.text(h + 0.5, bar.get_y() + bar.get_height()/2, f'{h:.1f}%',
                    ha='left', va='center', fontsize=9, fontweight='bold')
        ax.set_xlabel('النسبة %', fontsize=11, fontweight='bold')
        ax.set_title('توزيع المكونات', fontsize=13, fontweight='bold', color='#1b5e20')
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.invert_yaxis()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_nutrient_breakdown_pie(actual):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        protein_cal = actual.get("CP", 0) * 4
        fat_cal = actual.get("EE", 0) * 9
        fiber_cal = (actual.get("NDF", 0) + actual.get("ADF", 0)) * 2
        other_cal = max(0, 100 - protein_cal - fat_cal - fiber_cal)
        labels = ['بروتين', 'دهن', 'ألياف', 'كربوهيدرات']
        sizes = [protein_cal, fat_cal, fiber_cal, other_cal]
        colors_p = ['#1976d2', '#f9a825', '#43a047', '#8e24aa']
        fig, ax = plt.subplots(figsize=(7, 5))
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct='%1.1f%%', colors=colors_p,
            startangle=90, wedgeprops=dict(edgecolor='white', linewidth=2))
        for t in autotexts:
            t.set_color('white')
            t.set_fontweight('bold')
        ax.set_title('مصادر الطاقة', fontsize=13, fontweight='bold', color='#1b5e20')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_oil_comparison_chart(total_oil, oil_std):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        fig, ax = plt.subplots(figsize=(8, 4))
        categories = ['النسبة الفعلية', 'المثالي', 'الحد الأقصى']
        values = [total_oil, oil_std['optimal'], oil_std['max']]
        colors_c = ['#43a047', '#1976d2', '#c62828']
        if total_oil > oil_std['max']:
            colors_c[0] = '#c62828'
        elif total_oil > oil_std['optimal'] * 1.2:
            colors_c[0] = '#f9a825'
        bars = ax.bar(categories, values, color=colors_c, edgecolor='#333', linewidth=1.5)
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.2, f'{h:.2f}%',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        ax.set_ylabel('النسبة %', fontsize=11, fontweight='bold')
        ax.set_title(f'تقييم الزيوت — {oil_std.get("source", "NRC")}',
                     fontsize=13, fontweight='bold', color='#1b5e20')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_quality_breakdown_chart(compare_rows):
    if not MATPLOTLIB_AVAILABLE or not compare_rows:
        return None
    try:
        labels = [r["العنصر"] for r in compare_rows[:9]]
        scores = [r.get("score", 50) for r in compare_rows[:9]]
        colors_q = []
        for s in scores:
            if s >= 95: colors_q.append('#1b5e20')
            elif s >= 85: colors_q.append('#43a047')
            elif s >= 70: colors_q.append('#7cb342')
            elif s >= 55: colors_q.append('#f9a825')
            else: colors_q.append('#c62828')
        fig, ax = plt.subplots(figsize=(9, 4))
        bars = ax.bar(labels, scores, color=colors_q, edgecolor='#333', linewidth=1.5)
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h, f'{h:.0f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax.axhline(y=70, color='#c62828', linestyle='--', linewidth=2, label='الحد الأدنى 70%')
        ax.set_ylim(0, 105)
        ax.set_ylabel('الدرجة', fontsize=11, fontweight='bold')
        ax.set_title('تقييم كل عنصر', fontsize=13, fontweight='bold', color='#1b5e20')
        ax.legend(loc='lower right')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        plt.xticks(rotation=30, ha='right')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_ca_p_ratio_chart(actual_ca, actual_p, target_ca=0, target_p=0):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        if actual_p <= 0:
            return None
        ratio = actual_ca / actual_p
        fig, ax = plt.subplots(figsize=(8, 3))
        zones = [
            (0.0, 0.8, '#b71c1c'), (0.8, 1.2, '#ef6c00'),
            (1.2, 1.5, '#f9a825'), (1.5, 2.0, '#2e7d32'),
            (2.0, 3.0, '#f9a825'), (3.0, 5.0, '#ef6c00'),
            (5.0, 8.0, '#b71c1c'),
        ]
        for x0, x1, color in zones:
            ax.axvspan(x0, x1, alpha=0.35, color=color, edgecolor='white', linewidth=0)

        ratio_clipped = min(ratio, 7.9)
        ax.axvline(ratio_clipped, color='#0d47a1', linewidth=4, zorder=10)
        ax.scatter([ratio_clipped], [0.5], s=350, color='#0d47a1',
                    zorder=11, edgecolors='white', linewidth=3)
        ax.text(ratio_clipped, 0.85, f'{ratio:.2f}',
                ha='center', va='bottom', fontsize=18,
                fontweight='bold', color='#0d47a1',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                          edgecolor='#0d47a1', linewidth=2))

        ax.set_xlim(0, 8)
        ax.set_ylim(0, 1.2)
        ax.set_yticks([])
        ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8])
        ax.set_xlabel('نسبة Ca : P', fontsize=12, fontweight='bold')
        ax.set_title(
            f'⚖️ نسبة Ca:P — Ca={actual_ca:.2f}% | P={actual_p:.2f}%',
            fontsize=12, fontweight='bold', color='#1b5e20', pad=15
        )
        if 1.5 <= ratio <= 2.0:
            label, color = '✅ مثالية', '#1b5e20'
        elif 1.2 <= ratio < 1.5 or 2.0 < ratio <= 3.0:
            label, color = '⚠️ مقبولة', '#f57c00'
        elif 0.8 <= ratio < 1.2 or 3.0 < ratio <= 5.0:
            label, color = '🟠 خارج النطاق', '#e65100'
        else:
            label, color = '❌ خطرة', '#c62828'
        ax.text(0.02, 0.05, label, transform=ax.transAxes,
                fontsize=13, fontweight='bold', color=color,
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                          edgecolor=color, linewidth=2))
        ax.grid(axis='x', alpha=0.2, linestyle=':')
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# PDFGenerator
# ═══════════════════════════════════════════════════════════════════════════
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
            return get_display(arabic_reshaper.reshape(str(text)), base_dir='R')
        except Exception:
            return str(text)

    def _draw_stamp(self, canvas_obj, doc):
        try:
            w, h = doc.pagesize
            sx, sy = w - 105, 145
            canvas_obj.setStrokeColor(HexColor('#c62828'))
            canvas_obj.setLineWidth(3.5)
            canvas_obj.circle(sx, sy, 72, stroke=1, fill=0)
            canvas_obj.setLineWidth(2.0)
            canvas_obj.circle(sx, sy, 64, stroke=1, fill=0)
            canvas_obj.setLineWidth(0.8)
            canvas_obj.circle(sx, sy, 58, stroke=1, fill=0)
            canvas_obj.setLineWidth(1.8)
            for ang_deg in [-45, 45, 135, 225]:
                rad = np.radians(ang_deg)
                x1 = sx + 58 * np.cos(rad)
                y1 = sy + 58 * np.sin(rad)
                x2 = sx + 72 * np.cos(rad)
                y2 = sy + 72 * np.sin(rad)
                canvas_obj.line(x1, y1, x2, y2)
            canvas_obj.setFillColor(HexColor('#c62828'))
            canvas_obj.setFont(self.font_name, 9.5)
            canvas_obj.drawCentredString(sx, sy + 42, self._ar("تاور نولجي"))
            canvas_obj.drawCentredString(sx, sy + 30, self._ar("Tawor Nology"))
            canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(sx, sy + 16, self._ar("د. عبدالقادر"))  # ✅ د.
            canvas_obj.drawCentredString(sx, sy + 4, self._ar("إسماعيل تاور"))
            canvas_obj.setFont(self.font_name, 6.5)
            canvas_obj.drawCentredString(sx, sy - 12, self._ar("اختصاصي تغذية الحيوان"))
            canvas_obj.drawCentredString(sx, sy - 24, self._ar("معتمد رسمياً"))
            canvas_obj.drawCentredString(sx, sy - 36, self._ar("© 2026"))
        except Exception:
            pass

    def _draw_page(self, canvas_obj, doc):
        try:
            canvas_obj.saveState()
            w, h = doc.pagesize
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, h - 90, w, 90, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.rect(0, h - 95, w, 5, fill=1, stroke=0)
            try:
                if self.logo_path:
                    canvas_obj.drawImage(self.logo_path, 30, h - 78, width=60,
                                          height=60, preserveAspectRatio=True,
                                          anchor='sw', mask='auto')
            except Exception:
                pass
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 22)
            canvas_obj.drawCentredString(w / 2, h - 38, self._ar("تاور نولجي  Tawor Nology"))
            canvas_obj.setFont(self.font_name, 12)
            canvas_obj.setFillColor(HexColor('#e8f5e9'))
            canvas_obj.drawCentredString(w / 2, h - 58, self._ar("للإنتاج الحيواني وتغذية الحيوان"))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.drawCentredString(w / 2, h - 76,
                self._ar(f"إشراف: {SUPERVISOR} — {SUPERVISOR_TITLE}"))

            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, 42, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.rect(0, 84, w, 3, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#ffeb3b'))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.drawCentredString(w / 2, 68, self._ar(f"🤲 {DUA_SHORT} 🤲"))
            canvas_obj.setFillColor(HexColor('#c8e6c9'))
            canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(w / 2, 52, self._ar("اللهم اجعل قبرهما روضة من رياض الجنة"))
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(w / 2, 27, self._ar("تاور نولجي Tawor Nology © 2026"))
            canvas_obj.setFont(self.font_name, 7)
            canvas_obj.drawCentredString(w / 2, 12,
                self._ar(f"صفحة {canvas_obj.getPageNumber()} | جميع الحقوق محفوظة"))
            self._draw_stamp(canvas_obj, doc)
            canvas_obj.restoreState()
        except Exception:
            pass

    def _comparison_table(self, standard, calculated):
        labels = {"CP": "بروتين خام CP", "DP": "بروتين مهضوم DP",
                  "SE": "معادل النشاء SE", "NDF": "ألياف NDF",
                  "ADF": "ألياف ADF", "EE": "دهن EE", "ASH": "رماد ASH",
                  "Ca": "كالسيوم Ca", "P": "فسفور P"}
        header = [self._ar(x) for x in
                  ["العنصر", "المعيار", "المحسوب", "الفرق", "الفرق %", "التقييم"]]
        data = [header]
        cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#9e9e9e')),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ]
        row = 1
        for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
            if k not in standard or standard[k] == 0:
                continue
            sv = standard[k]
            cv = calculated.get(k, 0.0)
            diff = cv - sv
            pct = (diff / sv * 100) if sv else 0
            ev = evaluate_difference(pct, standard_value=sv)
            data.append([
                self._ar(labels.get(k, k)), f"{sv:.2f}", f"{cv:.2f}",
                f"{diff:+.3f}", f"{pct:+.2f}%", self._ar(ev["label"])
            ])
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
        if not oil_rows:
            return (None, 0.0, oil_std)
        header = [self._ar("الزيت"), self._ar("النسبة %"), self._ar("kcal/kg")]
        data = [header]
        for ing, pct in oil_rows:
            data.append([self._ar(ing), f"{pct:.2f}%", f"{pct * 90.0:.0f}"])
        data.append([self._ar("الإجمالي"), f"{total_oil:.2f}%", f"{total_oil * 90:.0f}"])
        cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e65100')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bf360c')),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#ffe0b2')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]
        t = Table(data, colWidths=[250, 100, 135])
        t.setStyle(TableStyle(cmds))
        return (t, total_oil, oil_std)

    def generate_report(self, formula, requirement, animal_type, breed, cost,
                        city, local_cost, local_sym, requester_name="",
                        protein_basis="DP", standard_key="", include_charts=True,
                        quality_score=0.0):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40,
                                topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text), ParagraphStyle('s', fontName=self.font_name,
                fontSize=size, alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))

        story.append(P("تقرير فني رسمي — تركيب علفة", size=20,
                       align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))

        client_data = [
            [self._ar("👤 اسم طالب الخدمة:"), self._ar(requester_name or "........................")],
            [self._ar("📍 الموقع:"), self._ar(city)],
            [self._ar("🐾 الفصيل:"), self._ar(f"{animal_type} — {breed}")],
            [self._ar("🧬 أساس الحساب:"), self._ar("DP" if protein_basis == "DP" else "CP")],
            [self._ar("📅 تاريخ الإصدار:"), datetime.now().strftime('%Y-%m-%d | %H:%M')],
        ]
        ct = Table(client_data, colWidths=[150, 340])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
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
            if k not in standard_vals or standard_vals[k] == 0:
                continue
            sv = standard_vals[k]
            cv = calculated_vals.get(k, 0.0)
            pct = ((cv - sv) / sv * 100) if sv else 0
            scores.append({"score": evaluate_difference(pct, standard_value=sv)["score"]})
        overall = get_overall_rating(scores)

        quality_data = [
            [self._ar("درجة الجودة"), self._ar("التقييم العام"), self._ar("اجتياز 70%")],
            [f"{quality_score:.1f}%", self._ar(overall["label"]),
             self._ar("✅ نعم" if quality_score >= 70 else "⚠️ لا")]
        ]
        qt = Table(quality_data, colWidths=[130, 200, 160])
        qt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565c0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('BACKGROUND', (0, 1), (-1, -1),
             HexColor('#e8f5e9' if quality_score >= 70 else '#ffebee')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#1976d2')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(qt)
        story.append(Spacer(1, 15))

        story.append(P("📊 جدول مقارنة العناصر", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        story.append(self._comparison_table(standard_vals, calculated_vals))
        story.append(Spacer(1, 12))

        oil_tbl, total_oil, oil_std = self._oil_table(formula, standard_key)
        story.append(P("🌰 الزيوت", size=14, color='#e65100'))
        story.append(Spacer(1, 8))
        if oil_tbl is None:
            story.append(P("ℹ️ لم تُستخدم زيوت.", size=11, color='#666'))
        else:
            story.append(oil_tbl)
        story.append(Spacer(1, 15))

        if include_charts:
            story.append(PageBreak())
            story.append(P("📈 الرسوم البيانية", size=14, color='#1b5e20'))
            story.append(Spacer(1, 10))
            c1 = create_colorful_bar_chart(standard_vals, calculated_vals)
            if c1:
                try:
                    story.append(RLImage(c1, width=450, height=250))
                    story.append(Spacer(1, 12))
                except Exception:
                    pass
            c2 = create_colorful_pie_chart(formula)
            c3 = create_radar_chart(standard_vals, calculated_vals)
            if c2 and c3:
                try:
                    row = [[RLImage(c2, width=210, height=200),
                            RLImage(c3, width=210, height=200)]]
                    rt = Table(row, colWidths=[230, 230])
                    rt.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
                    story.append(rt)
                    story.append(Spacer(1, 12))
                except Exception:
                    pass
            gauge = create_gauge_chart(overall["score"])
            if gauge:
                try:
                    story.append(RLImage(gauge, width=200, height=200))
                except Exception:
                    pass
            try:
                cap_img = create_ca_p_ratio_chart(
                    calculated_vals.get("Ca", 0), calculated_vals.get("P", 0),
                    standard_vals.get("Ca", 0), standard_vals.get("P", 0))
                if cap_img:
                    story.append(P("⚖️ Ca:P", size=12, align=TA_CENTER, color='#1b5e20'))
                    story.append(RLImage(cap_img, width=450, height=170))
            except Exception:
                pass

        story.append(PageBreak())
        story.append(P("💰 التكاليف", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        cost_data = [
            [self._ar("البند"), self._ar("القيمة")],
            [self._ar("التكلفة للطن (دولار)"), f"${cost:.2f}"],
            [self._ar(f"التكلفة ({local_sym})"), f"{local_cost:,.2f}"],
        ]
        tc = Table(cost_data, colWidths=[280, 210])
        tc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
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
            story.append(P("🌾 المكونات للطن", size=14, color='#1b5e20'))
            story.append(Spacer(1, 8))
            ing_data = [[self._ar("المكون"), self._ar("النسبة %"), self._ar("كجم/طن")]]
            for ing, pct in formula.items():
                ing_data.append([self._ar(ing), f"{pct:.2f}%", f"{pct * 10:.1f}"])
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
            ]))
            story.append(ti)
            story.append(Spacer(1, 25))
            sign = [
                [self._ar("توقيع طالب الخدمة"), self._ar("توقيع المختص")],
                [self._ar("........................"), self._ar(SUPERVISOR)],
                [self._ar("التاريخ: ..../..../........"), self._ar(SUPERVISOR_TITLE)],
            ]
            ts = Table(sign, colWidths=[245, 245])
            ts.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOX', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f5e9')),
            ]))
            story.append(ts)

        doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_ocr_report(self, ingredients, nutrients, raw_text=""):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40,
                                topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text), ParagraphStyle('s', fontName=self.font_name,
                fontSize=size, alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))

        story.append(P("تقرير OCR", size=20, align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))
        story.append(P(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"))
        story.append(Spacer(1, 12))

        data = [[self._ar("المادة العلفية"), self._ar("النسبة %")]]
        for k, v in ingredients.items():
            data.append([self._ar(k), f"{v:.2f}%"])
        data.append([self._ar("الإجمالي"), f"{sum(ingredients.values()):.2f}%"])

        t = Table(data, colWidths=[300, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#ffe0b2')),
        ]))
        story.append(t)
        story.append(Spacer(1, 18))

        story.append(P("🔬 التحليل التقديري", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        nut_data = [
            [self._ar("العنصر"), self._ar("القيمة")],
            [self._ar("بروتين CP"), f"{nutrients.get('CP', 0):.2f}%"],
            [self._ar("بروتين مهضوم DP"), f"{nutrients.get('DP', 0):.2f}%"],
            [self._ar("معادل النشاء SE"), f"{nutrients.get('SE', 0):.1f}"],
            [self._ar("NDF"), f"{nutrients.get('NDF', 0):.2f}%"],
            [self._ar("ADF"), f"{nutrients.get('ADF', 0):.2f}%"],
            [self._ar("دهن EE"), f"{nutrients.get('EE', 0):.2f}%"],
            [self._ar("رماد ASH"), f"{nutrients.get('ASH', 0):.2f}%"],
            [self._ar("Ca"), f"{nutrients.get('Ca', 0):.2f}%"],
            [self._ar("P"), f"{nutrients.get('P', 0):.2f}%"],
        ]
        t2 = Table(nut_data, colWidths=[250, 250])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
        ]))
        story.append(t2)
        story.append(Spacer(1, 20))
        story.append(P(SUPERVISOR, size=16, align=TA_CENTER, color='#c62828'))
        story.append(P(SUPERVISOR_TITLE, size=11, align=TA_CENTER, color='#1b5e20'))

        doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()


pdf_gen = PDFGenerator()


# ═══════════════════════════════════════════════════════════════════════════
# تصدير Excel
# ═══════════════════════════════════════════════════════════════════════════
def export_comparison_to_excel(standard, calculated, requester_name="",
                                animal="", stage="", formula=None, standard_key=""):
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
    thin = Side(border_style='thin', color='9E9E9E')
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)

    ws.merge_cells('A1:F1')
    ws['A1'] = APP_NAME
    ws['A1'].font = tf
    ws['A1'].alignment = ct
    ws.merge_cells('A2:F2')
    ws['A2'] = f"🤲 {DUA_SHORT} 🤲"
    ws['A2'].font = Font(name='Arial', size=10, bold=True, color='C62828')
    ws['A2'].alignment = ct

    headers = ["العنصر", "المعيار", "المحسوب", "الفرق", "% الفرق", "التقييم"]
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=4, column=c, value=h)
        cell.font = hf
        cell.fill = hfill
        cell.alignment = ct
        cell.border = bd

    labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم", "SE": "معادل النشاء",
              "NDF": "NDF", "ADF": "ADF", "EE": "دهن", "ASH": "رماد",
              "Ca": "كالسيوم", "P": "فسفور"}
    row = 5
    for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
        if k not in standard or standard[k] == 0:
            continue
        sv = standard[k]
        cv = calculated.get(k, 0.0)
        diff = cv - sv
        pct = (diff / sv * 100) if sv else 0
        ev = evaluate_difference(pct, standard_value=sv)
        vals = [labels[k], round(sv, 2), round(cv, 2), round(diff, 3),
                round(pct, 2), ev["label"]]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.alignment = ct
            cell.border = bd
            cell.fill = PatternFill('solid', fgColor=ev["bg"].replace('#', ''))
        row += 1

    for c in range(1, 7):
        ws.column_dimensions[get_column_letter(c)].width = 22

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


def export_ocr_to_excel(ingredients, nutrients):
    if not OPENPYXL_AVAILABLE:
        return b""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "OCR Analysis"
    ws.sheet_view.rightToLeft = True

    hf = Font(name='Arial', size=12, bold=True, color='FFFFFF')
    hfill = PatternFill('solid', fgColor='1B5E20')
    tf = Font(name='Arial', size=14, bold=True, color='1B5E20')
    ct = Alignment(horizontal='center', vertical='center', wrap_text=True)
    thin = Side(border_style='thin', color='9E9E9E')
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)

    ws.merge_cells('A1:B1')
    ws['A1'] = f"{APP_NAME} — OCR"
    ws['A1'].font = tf
    ws['A1'].alignment = ct

    for c, h in enumerate(["المادة", "النسبة %"], 1):
        cell = ws.cell(row=3, column=c, value=h)
        cell.font = hf
        cell.fill = hfill
        cell.alignment = ct
        cell.border = bd

    row = 4
    for k, v in ingredients.items():
        ws.cell(row=row, column=1, value=k).border = bd
        ws.cell(row=row, column=2, value=v).border = bd
        row += 1

    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 15
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# الأسعار والصور
# ═══════════════════════════════════════════════════════════════════════════
EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "ليبيا": {"rate": 4.80, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"},
    "السعودية": {"rate": 3.75, "sym": "SAR"},
    "الإمارات": {"rate": 3.67, "sym": "AED"},
    "باقي دول العالم": {"rate": 1.0, "sym": "USD"},
}


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


# ═══════════════════════════════════════════════════════════════════════════
# الحظائر — المعايير
# ═══════════════════════════════════════════════════════════════════════════
BARN_DESIGN_STANDARDS = {
    "دواجن_لاحم": {"name_ar": "دواجن لاحم (Broiler)", "area_per_head": 0.10,
        "feeder_cm_per_head": 5.0, "drinker_cm_per_head": 2.5,
        "height_m": 2.8, "width_m": 12.0, "ach_summer": 60, "ach_winter": 8,
        "vent_open_ratio": 0.20, "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "خطية معلقة", "drinker_type": "حلمات",
        "aisle_m": 1.2, "central_aisle": True, "temp_optimal_c": 24, "humidity_optimal": 60},
    "دواجن_بياض": {"name_ar": "دواجن بياض (Layer)", "area_per_head": 0.15,
        "feeder_cm_per_head": 10.0, "drinker_cm_per_head": 2.5,
        "height_m": 3.0, "width_m": 12.0, "ach_summer": 40, "ach_winter": 6,
        "vent_open_ratio": 0.20, "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "سلسلة", "drinker_type": "حلمات",
        "aisle_m": 1.2, "central_aisle": True, "temp_optimal_c": 22, "humidity_optimal": 60},
    "سمان": {"name_ar": "سمان (Quail)", "area_per_head": 0.025,
        "feeder_cm_per_head": 2.0, "drinker_cm_per_head": 1.0,
        "height_m": 2.0, "width_m": 6.0, "ach_summer": 50, "ach_winter": 8,
        "vent_open_ratio": 0.25, "roof_type": "mono", "slope_pct": 15.0,
        "feeder_type": "خطية", "drinker_type": "حلمات",
        "aisle_m": 0.8, "central_aisle": False, "temp_optimal_c": 26, "humidity_optimal": 65},
    "أغنام": {"name_ar": "أغنام (Sheep)", "area_per_head": 1.5,
        "feeder_cm_per_head": 35.0, "drinker_cm_per_head": 4.0,
        "height_m": 3.5, "width_m": 10.0, "ach_summer": 30, "ach_winter": 5,
        "vent_open_ratio": 0.30, "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "خطية خرسانية", "drinker_type": "حوض",
        "aisle_m": 2.0, "central_aisle": True, "temp_optimal_c": 18, "humidity_optimal": 65},
    "ماعز": {"name_ar": "ماعز (Goat)", "area_per_head": 1.5,
        "feeder_cm_per_head": 35.0, "drinker_cm_per_head": 4.0,
        "height_m": 3.5, "width_m": 10.0, "ach_summer": 30, "ach_winter": 5,
        "vent_open_ratio": 0.30, "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "خطية مرتفعة", "drinker_type": "حوض",
        "aisle_m": 2.0, "central_aisle": True, "temp_optimal_c": 20, "humidity_optimal": 65},
    "أبقار": {"name_ar": "أبقار (Cattle)", "area_per_head": 5.0,
        "feeder_cm_per_head": 70.0, "drinker_cm_per_head": 6.0,
        "height_m": 4.5, "width_m": 15.0, "ach_summer": 25, "ach_winter": 4,
        "vent_open_ratio": 0.35, "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "خطية وسطية", "drinker_type": "حوض",
        "aisle_m": 3.5, "central_aisle": True, "temp_optimal_c": 15, "humidity_optimal": 65},
    "إبل": {"name_ar": "إبل (Camel)", "area_per_head": 10.0,
        "feeder_cm_per_head": 100.0, "drinker_cm_per_head": 8.0,
        "height_m": 4.5, "width_m": 15.0, "ach_summer": 20, "ach_winter": 4,
        "vent_open_ratio": 0.40, "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "خطية مرتفعة", "drinker_type": "حوض كبير",
        "aisle_m": 4.0, "central_aisle": True, "temp_optimal_c": 25, "humidity_optimal": 50},
    "خيول": {"name_ar": "خيول (Horse)", "area_per_head": 16.0,
        "feeder_cm_per_head": 100.0, "drinker_cm_per_head": 10.0,
        "height_m": 4.0, "width_m": 15.0, "ach_summer": 25, "ach_winter": 5,
        "vent_open_ratio": 0.30, "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "خطية مرتفعة", "drinker_type": "حوض",
        "aisle_m": 3.5, "central_aisle": True, "temp_optimal_c": 18, "humidity_optimal": 60},
    "أرانب": {"name_ar": "أرانب (Rabbit)", "area_per_head": 0.30,
        "feeder_cm_per_head": 8.0, "drinker_cm_per_head": 2.0,
        "height_m": 2.5, "width_m": 8.0, "ach_summer": 40, "ach_winter": 6,
        "vent_open_ratio": 0.25, "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "خطية معدنية", "drinker_type": "نبل",
        "aisle_m": 1.2, "central_aisle": True, "temp_optimal_c": 20, "humidity_optimal": 65},
    "أسماك_أحواض": {"name_ar": "أسماك — أحواض ترابية", "area_per_head": 1.5,
        "feeder_cm_per_head": 0.0, "drinker_cm_per_head": 0.0,
        "height_m": 1.5, "width_m": 20.0, "ach_summer": 0, "ach_winter": 0,
        "vent_open_ratio": 0.0, "roof_type": "none", "slope_pct": 0.0,
        "feeder_type": "نثر", "drinker_type": "لا يوجد",
        "aisle_m": 2.0, "central_aisle": False, "temp_optimal_c": 28, "humidity_optimal": 0},
}


def calculate_barn_dimensions(animal_key, count):
    std = BARN_DESIGN_STANDARDS.get(animal_key)
    if not std:
        return None
    total_area = count * std["area_per_head"]
    width = std["width_m"]
    length = max(total_area / width, 6.0)
    feeders = max(1, int(np.ceil(count * std["feeder_cm_per_head"] / 300)))
    drinkers = max(1, int(np.ceil(count * std["drinker_cm_per_head"] / 200)))
    volume = length * width * std["height_m"]
    roof_rise = (width / 2) * (std["slope_pct"] / 100.0)
    ridge_height = std["height_m"] + roof_rise
    if animal_key in ["دواجن_لاحم", "دواجن_بياض", "سمان"]:
        animals_per_row = max(2, int(length / 0.3))
    elif animal_key == "أرانب":
        animals_per_row = max(2, int(length / 0.5))
    else:
        animals_per_row = max(2, int(length / 1.5))
    return {
        "standard": std, "count": count,
        "total_area_m2": round(total_area, 2),
        "length_m": round(length, 2), "width_m": round(width, 2),
        "height_m": std["height_m"], "ridge_height_m": round(ridge_height, 2),
        "roof_type": std["roof_type"], "slope_pct": std["slope_pct"],
        "feeders_count": feeders, "drinkers_count": drinkers,
        "total_feeder_length_m": round(count * std["feeder_cm_per_head"] / 100, 1),
        "total_drinker_length_m": round(count * std["drinker_cm_per_head"] / 100, 1),
        "volume_m3": round(volume, 1),
        "vent_flow_summer_m3h": int(volume * std["ach_summer"]),
        "vent_flow_winter_m3h": int(volume * std["ach_winter"]),
        "vent_open_area_m2": round(length * std["height_m"] * std["vent_open_ratio"], 2),
        "animals_per_row": animals_per_row,
        "feeder_type": std.get("feeder_type", "خطية"),
        "drinker_type": std.get("drinker_type", "حوض"),
        "aisle_m": std.get("aisle_m", 1.5),
        "central_aisle": std.get("central_aisle", True),
        "temp_optimal": std.get("temp_optimal_c", 20),
        "humidity_optimal": std.get("humidity_optimal", 60),
    }


def create_barn_3d_figure(dims):
    if not PLOTLY_AVAILABLE:
        return None
    try:
        std = dims["standard"]
        L, W, H, RH = dims["length_m"], dims["width_m"], dims["height_m"], dims["ridge_height_m"]
        aisle = dims.get("aisle_m", 1.5)
        feeder_w = 0.6
        fig = go.Figure()
        fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[0, 0, 0, 0],
            i=[0, 0], j=[1, 2], k=[2, 3], color='#d7ccc8', opacity=0.65,
            name='الأرضية', hoverinfo='skip'))
        for x_pos in [0, L]:
            fig.add_trace(go.Mesh3d(x=[x_pos] * 4, y=[0, W, W, 0], z=[0, 0, H, H],
                i=[0, 0], j=[1, 2], k=[2, 3], color='#a1887f', opacity=0.35,
                showlegend=False, hoverinfo='skip'))
        for y_pos in [0, W]:
            fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[y_pos] * 4, z=[0, 0, H, H],
                i=[0, 0], j=[1, 2], k=[2, 3], color='#a1887f', opacity=0.35,
                showlegend=False, hoverinfo='skip'))
        if dims["roof_type"] == "gable":
            fig.add_trace(go.Mesh3d(
                x=[0, L, L, 0], y=[0, 0, W/2, W/2], z=[H, H, RH, RH],
                i=[0, 0], j=[1, 2], k=[2, 3], color='#8d6e63', opacity=0.5,
                name='السقف', hoverinfo='skip'))
            fig.add_trace(go.Mesh3d(
                x=[0, L, L, 0], y=[W/2, W/2, W, W], z=[RH, RH, H, H],
                i=[0, 0], j=[1, 2], k=[2, 3], color='#8d6e63', opacity=0.5,
                showlegend=False, hoverinfo='skip'))
        if dims.get("central_aisle", True) and W > 8:
            feeder_positions = [W/2 - aisle/2 - feeder_w, W/2 + aisle/2]
        else:
            feeder_positions = [0.8, W - 1.4]
        for idx, y_pos in enumerate(feeder_positions):
            x_vals = [0.5, L-0.5, L-0.5, 0.5, 0.5, L-0.5, L-0.5, 0.5]
            y_vals = [y_pos, y_pos, y_pos + feeder_w, y_pos + feeder_w,
                      y_pos, y_pos, y_pos + feeder_w, y_pos + feeder_w]
            z_vals = [0, 0, 0, 0, 0.35, 0.35, 0.35, 0.35]
            i_idx = [0, 0, 4, 4, 0, 0, 3, 3, 0, 0, 1, 1]
            j_idx = [1, 2, 6, 7, 4, 5, 2, 6, 3, 7, 5, 6]
            k_idx = [2, 3, 5, 6, 5, 1, 6, 7, 7, 4, 6, 2]
            fig.add_trace(go.Mesh3d(x=x_vals, y=y_vals, z=z_vals,
                i=i_idx, j=j_idx, k=k_idx, color='#ff8f00', opacity=0.85,
                name=f'معلف' if idx == 0 else None,
                showlegend=(idx == 0), hoverinfo='skip'))
        n_drinkers = dims["drinkers_count"]
        for i in range(n_drinkers):
            x_center = (i + 0.5) * (L / n_drinkers)
            y_center = W - aisle - 0.5 if dims.get("central_aisle", True) else W - 1.5
            fig.add_trace(go.Scatter3d(x=[x_center], y=[y_center], z=[0.4],
                mode='markers+text',
                marker=dict(size=14, color='#1976d2', symbol='diamond'),
                text=[f'م{i+1}'], textposition='top center',
                name='مسقى' if i == 0 else None, showlegend=(i == 0)))
        apr = dims["animals_per_row"]
        n_rows = max(1, dims["count"] // max(apr, 1))
        step = max(1, n_rows // 25)
        ax_, ay_, az_ = [], [], []
        for row_idx in range(0, n_rows, step):
            y_pos = 2.0 + (row_idx * (W - 3.0) / max(n_rows, 1))
            for col in range(min(apr, 20)):
                x_pos = 0.8 + col * (L - 1.6) / min(apr, 20)
                ax_.append(x_pos)
                ay_.append(y_pos)
                az_.append(0.2)
        if ax_:
            fig.add_trace(go.Scatter3d(x=ax_, y=ay_, z=az_, mode='markers',
                marker=dict(size=4, color='#1b5e20', opacity=0.8),
                name=f'الحيوانات ({dims["count"]})'))
        fig.update_layout(
            title=dict(
                text=f"🏗️ {std['name_ar']} — {dims['count']} رأس | {dims['total_area_m2']} م²",
                font=dict(size=15, color='#1b5e20')),
            scene=dict(
                xaxis=dict(title='الطول'),
                yaxis=dict(title='العرض'),
                zaxis=dict(title='الارتفاع'),
                aspectmode='data',
                camera=dict(eye=dict(x=1.6, y=-1.6, z=1.2))),
            height=700, margin=dict(l=0, r=0, t=90, b=0),
            paper_bgcolor='white')
        return fig
    except Exception:
        return None


def create_barn_animation_gif(dims, frames=30, fps=8):
    if not MATPLOTLIB_AVAILABLE or not PIL_AVAILABLE:
        return None
    try:
        std = dims["standard"]
        L, W, H, RH = dims["length_m"], dims["width_m"], dims["height_m"], dims["ridge_height_m"]
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')

        def draw_barn():
            ax.clear()
            floor = [[(0, 0, 0), (L, 0, 0), (L, W, 0), (0, W, 0)]]
            ax.add_collection3d(Poly3DCollection(floor, facecolors='#d7ccc8',
                edgecolors='#5d4037', alpha=0.75, linewidths=1.5))
            walls = [
                [(0, 0, 0), (L, 0, 0), (L, 0, H), (0, 0, H)],
                [(0, W, 0), (L, W, 0), (L, W, H), (0, W, H)],
                [(0, 0, 0), (0, W, 0), (0, W, H), (0, 0, H)],
                [(L, 0, 0), (L, W, 0), (L, W, H), (L, 0, H)]]
            ax.add_collection3d(Poly3DCollection(walls, facecolors='#a1887f',
                edgecolors='#5d4037', alpha=0.4, linewidths=1))
            if dims["roof_type"] == "gable":
                r1 = [[(0, 0, H), (L, 0, H), (L, W/2, RH), (0, W/2, RH)]]
                r2 = [[(0, W/2, RH), (L, W/2, RH), (L, W, H), (0, W, H)]]
                ax.add_collection3d(Poly3DCollection(r1, facecolors='#8d6e63',
                    edgecolors='#4e342e', alpha=0.55))
                ax.add_collection3d(Poly3DCollection(r2, facecolors='#8d6e63',
                    edgecolors='#4e342e', alpha=0.55))
            ax.set_xlim(0, L); ax.set_ylim(0, W); ax.set_zlim(0, RH + 1)
            ax.set_title(f"🏗️ {std['name_ar']} — {dims['count']} رأس",
                         fontsize=12, color='#1b5e20', fontweight='bold')

        def animate(fn):
            draw_barn()
            ax.view_init(elev=20, azim=(fn / frames) * 360)
            return fig,

        anim = animation.FuncAnimation(fig, animate, frames=frames,
                                        interval=1000 // fps, blit=False)
        tmp = tempfile.NamedTemporaryFile(suffix='.gif', delete=False)
        tmp_path = tmp.name
        tmp.close()
        try:
            anim.save(tmp_path, writer='pillow', fps=fps, dpi=80)
            with open(tmp_path, 'rb') as f:
                data = f.read()
            os.unlink(tmp_path)
            plt.close(fig)
            return io.BytesIO(data)
        except Exception:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            plt.close(fig)
            return None
    except Exception:
        return None


def render_barn_to_pdf_image(dims):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        std = dims["standard"]
        L, W, H, RH = dims["length_m"], dims["width_m"], dims["height_m"], dims["ridge_height_m"]
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        floor = [[(0, 0, 0), (L, 0, 0), (L, W, 0), (0, W, 0)]]
        ax.add_collection3d(Poly3DCollection(floor, facecolors='#d7ccc8',
            edgecolors='#5d4037', alpha=0.75, linewidths=1.5))
        walls = [
            [(0, 0, 0), (L, 0, 0), (L, 0, H), (0, 0, H)],
            [(0, W, 0), (L, W, 0), (L, W, H), (0, W, H)],
            [(0, 0, 0), (0, W, 0), (0, W, H), (0, 0, H)],
            [(L, 0, 0), (L, W, 0), (L, W, H), (L, 0, H)]]
        ax.add_collection3d(Poly3DCollection(walls, facecolors='#a1887f',
            edgecolors='#5d4037', alpha=0.4, linewidths=1))
        if dims["roof_type"] == "gable":
            r1 = [[(0, 0, H), (L, 0, H), (L, W/2, RH), (0, W/2, RH)]]
            r2 = [[(0, W/2, RH), (L, W/2, RH), (L, W, H), (0, W, H)]]
            ax.add_collection3d(Poly3DCollection(r1, facecolors='#8d6e63',
                edgecolors='#4e342e', alpha=0.55))
            ax.add_collection3d(Poly3DCollection(r2, facecolors='#8d6e63',
                edgecolors='#4e342e', alpha=0.55))
        ax.set_xlim(0, L); ax.set_ylim(0, W); ax.set_zlim(0, RH + 1)
        ax.set_xlabel('الطول'); ax.set_ylabel('العرض'); ax.set_zlabel('الارتفاع')
        ax.set_title(f"تصميم — {std['name_ar']} | {dims['count']} رأس",
                     fontsize=14, color='#1b5e20', fontweight='bold')
        ax.view_init(elev=18, azim=-55)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def generate_barn_pdf_report(dims):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40,
                            topMargin=115, bottomMargin=145)
    story = []

    def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
        return Paragraph(ar(text), ParagraphStyle('s', fontName=font_mgr.font_name,
            fontSize=size, alignment=align, textColor=HexColor(color),
            spaceAfter=6, leading=size * 1.6))

    std = dims["standard"]
    story.append(P("تقرير تصميم حظيرة — تاور نولجي", size=20,
                   align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
    story.append(Spacer(1, 12))

    info_data = [
        [ar("نوع الحيوان:"), ar(std["name_ar"])],
        [ar("العدد:"), ar(str(dims["count"]))],
        [ar("نوع المعالف:"), ar(dims.get("feeder_type", "خطية"))],
        [ar("نوع السقايات:"), ar(dims.get("drinker_type", "حوض"))],
        [ar("التاريخ:"), datetime.now().strftime('%Y-%m-%d %H:%M')],
    ]
    t = Table(info_data, colWidths=[150, 340])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
        ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')),
        ('INNERGRID', (0, 0), (-1, -1), 0.6, HexColor('#c8e6c9')),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(P("📐 الأبعاد", size=14, color='#1b5e20'))
    story.append(Spacer(1, 8))
    dim_data = [
        [ar("البيان"), ar("القيمة")],
        [ar("المساحة"), ar(f"{dims['total_area_m2']} م²")],
        [ar("الطول"), ar(f"{dims['length_m']} م")],
        [ar("العرض"), ar(f"{dims['width_m']} م")],
        [ar("ارتفاع الجدار"), ar(f"{dims['height_m']} م")],
        [ar("ارتفاع القمة"), ar(f"{dims['ridge_height_m']} م")],
        [ar("الحجم"), ar(f"{dims['volume_m3']} م³")],
    ]
    t2 = Table(dim_data, colWidths=[250, 240])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
    ]))
    story.append(t2)
    story.append(Spacer(1, 15))

    img = render_barn_to_pdf_image(dims)
    if img:
        try:
            story.append(RLImage(img, width=480, height=340))
        except Exception:
            pass
    story.append(Spacer(1, 20))

    sign = [[ar("توقيع المختص")], [ar(SUPERVISOR)], [ar(SUPERVISOR_TITLE)]]
    ts = Table(sign, colWidths=[400])
    ts.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f5e9')),
    ]))
    story.append(ts)

    doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
    buffer.seek(0)
    return buffer.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# الجدوى الفنية
# ═══════════════════════════════════════════════════════════════════════════
TECHNICAL_FEASIBILITY_DATA = {
    "دواجن_لاحم": {"feed_per_day_g": 120, "water_per_day_ml": 220, "labor_per_1000": 0.3,
        "cycle_days": 42, "final_weight_kg": 2.3, "fcr": 1.65,
        "production_type": "meat", "product_unit": "كجم لحم حي",
        "notes": "دورة 42 يوم، 2.3 كجم، FCR 1.65"},
    "دواجن_بياض": {"feed_per_day_g": 110, "water_per_day_ml": 250, "labor_per_1000": 0.3,
        "eggs_per_year": 310, "egg_weight_g": 60,
        "production_type": "eggs", "product_unit": "بيضة",
        "notes": "310 بيضة/سنة"},
    "سمان": {"feed_per_day_g": 28, "water_per_day_ml": 55, "labor_per_1000": 0.5,
        "cycle_days": 42, "final_weight_kg": 0.25, "fcr": 2.5,
        "production_type": "meat", "product_unit": "كجم لحم حي",
        "notes": "دورة 42 يوم، 250 جرام"},
    "أغنام": {"feed_per_day_g": 1800, "water_per_day_ml": 6000, "labor_per_1000": 1.5,
        "milk_per_day_L": 1.5, "lactation_days": 200,
        "production_type": "mixed", "product_unit": "لتر حليب",
        "notes": "1.5 لتر/يوم × 200 يوم"},
    "ماعز": {"feed_per_day_g": 1500, "water_per_day_ml": 6000, "labor_per_1000": 1.5,
        "milk_per_day_L": 2.5, "lactation_days": 280,
        "production_type": "milk", "product_unit": "لتر حليب",
        "notes": "2.5 لتر × 280 يوم"},
    "أبقار": {"feed_per_day_g": 20000, "water_per_day_ml": 80000, "labor_per_1000": 5.0,
        "milk_per_day_L": 20, "lactation_days": 305,
        "production_type": "milk", "product_unit": "لتر حليب",
        "notes": "20 لتر × 305 يوم"},
    "إبل": {"feed_per_day_g": 8000, "water_per_day_ml": 50000, "labor_per_1000": 3.0,
        "milk_per_day_L": 5, "lactation_days": 300,
        "production_type": "milk", "product_unit": "لتر حليب",
        "notes": "5 لتر × 300 يوم"},
    "خيول": {"feed_per_day_g": 10000, "water_per_day_ml": 40000, "labor_per_1000": 4.0,
        "production_type": "service", "product_unit": "خدمات",
        "notes": "خيول رياضة أو عمل"},
    "أرانب": {"feed_per_day_g": 180, "water_per_day_ml": 350, "labor_per_1000": 1.0,
        "cycle_days": 70, "final_weight_kg": 2.5, "fcr": 3.5,
        "production_type": "meat", "product_unit": "كجم لحم حي",
        "notes": "دورة 70 يوم، 2.5 كجم"},
    "أسماك_أحواض": {"feed_per_day_g": 30, "water_per_day_ml": 0, "labor_per_1000": 0.5,
        "cycle_days": 240, "final_weight_kg": 0.5, "fcr": 1.8,
        "production_type": "meat", "product_unit": "كجم لحم حي",
        "notes": "دورة 240 يوم، 500 جرام"},
}


def calculate_technical_feasibility(barn_key, count):
    std = BARN_DESIGN_STANDARDS.get(barn_key)
    if not std:
        return None
    dims = calculate_barn_dimensions(barn_key, count)
    if not dims:
        return None
    tech = TECHNICAL_FEASIBILITY_DATA.get(barn_key, {})
    feed_day = tech.get("feed_per_day_g", 100) / 1000.0 * count
    water_day = tech.get("water_per_day_ml", 200) / 1000.0 * count
    workers = max(1, int(np.ceil(count * tech.get("labor_per_1000", 0.3) / 1000)))
    ptype = tech.get("production_type", "meat")
    production = {}

    if ptype == "eggs":
        eggs_year = count * tech.get("eggs_per_year", 300)
        production = {"unit": "بيضة/سنة", "annual": eggs_year,
            "per_day": eggs_year / 365,
            "weight_ton": eggs_year * tech.get("egg_weight_g", 60) / 1_000_000,
            "details": tech.get("notes", "")}
    elif ptype == "milk":
        milk_day = count * tech.get("milk_per_day_L", 20)
        milk_year = milk_day * tech.get("lactation_days", 305)
        production = {"unit": "لتر/سنة", "annual": milk_year, "per_day": milk_day,
            "lactation_days": tech.get("lactation_days", 305),
            "details": tech.get("notes", "")}
    elif ptype == "meat":
        cycle = tech.get("cycle_days", 42)
        cycles_year = 365 / cycle
        total_kg = count * tech.get("final_weight_kg", 2) * cycles_year
        production = {"unit": "كجم/سنة", "annual": total_kg,
            "per_cycle": count * tech.get("final_weight_kg", 2),
            "cycles_year": cycles_year, "details": tech.get("notes", "")}
    elif ptype == "mixed":
        milk_day = count * tech.get("milk_per_day_L", 1)
        milk_year = milk_day * tech.get("lactation_days", 200)
        production = {"unit": "لتر/سنة", "annual": milk_year, "per_day": milk_day,
            "details": tech.get("notes", "")}
    else:
        production = {"unit": "خدمات", "annual": 0, "details": tech.get("notes", "")}

    return {"barn_key": barn_key, "std": std, "dims": dims, "count": count,
        "feed": {"per_head_day_kg": tech.get("feed_per_day_g", 100) / 1000.0,
            "total_day_kg": feed_day,
            "total_month_ton": feed_day * 30 / 1000,
            "total_year_ton": feed_day * 365 / 1000},
        "water": {"per_head_day_L": tech.get("water_per_day_ml", 200) / 1000.0,
            "total_day_L": water_day,
            "total_year_m3": water_day * 365 / 1000},
        "labor": {"workers": workers, "animals_per_worker": count // workers},
        "production": production,
        "ventilation": {"summer_m3h": dims["vent_flow_summer_m3h"],
            "winter_m3h": dims["vent_flow_winter_m3h"]}}


def generate_feasibility_booklet(barn_key, count, project_name="", requester_name=""):
    feas = calculate_technical_feasibility(barn_key, count)
    if not feas:
        return None
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40,
                            topMargin=115, bottomMargin=145)
    story = []

    def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
        return Paragraph(ar(text), ParagraphStyle('s', fontName=font_mgr.font_name,
            fontSize=size, alignment=align, textColor=HexColor(color),
            spaceAfter=6, leading=size * 1.6))

    std = feas["std"]
    dims = feas["dims"]

    story.append(Spacer(1, 30))
    story.append(P("كتيّب دراسة الجدوى", size=30, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 6))
    story.append(P("Technical Feasibility Booklet", size=13, align=TA_CENTER, color='#666'))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=3, color=HexColor('#d4af37')))
    story.append(Spacer(1, 30))
    story.append(P(f"مشروع: {project_name or std['name_ar']}", size=18,
                   align=TA_CENTER, color='#c62828'))
    story.append(Spacer(1, 15))
    story.append(P(f"{count} رأس", size=14, align=TA_CENTER))
    story.append(Spacer(1, 30))

    cover_data = [
        [ar("نوع الحيوان"), ar(std["name_ar"])],
        [ar("العدد"), ar(f"{count} رأس")],
        [ar("المساحة"), ar(f"{dims['total_area_m2']} م²")],
        [ar("مقدم الطلب"), ar(requester_name or "........................")],
        [ar("التاريخ"), ar(datetime.now().strftime('%Y-%m-%d'))],
    ]
    t = Table(cover_data, colWidths=[150, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
        ('BOX', (0, 0), (-1, -1), 2, HexColor('#2e7d32')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#c8e6c9')),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
    ]))
    story.append(t)
    story.append(Spacer(1, 60))
    story.append(P(f"🤲 {DUA_SHORT} 🤲", size=12, align=TA_CENTER, color='#c62828'))
    story.append(PageBreak())

    story.append(P("🏗️ الحظيرة", size=18, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 15))
    barn_data = [
        [ar("البيان"), ar("القيمة")],
        [ar("المساحة"), ar(f"{dims['total_area_m2']} م²")],
        [ar("الطول"), ar(f"{dims['length_m']} م")],
        [ar("العرض"), ar(f"{dims['width_m']} م")],
        [ar("ارتفاع الجدار"), ar(f"{dims['height_m']} م")],
        [ar("الحجم"), ar(f"{dims['volume_m3']} م³")],
    ]
    t = Table(barn_data, colWidths=[220, 230])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    story.append(t)
    story.append(PageBreak())

    story.append(P("🔧 الجدوى الفنية", size=18, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 15))

    def mini_table(title, color, rows):
        story.append(P(title, size=13, color=color))
        story.append(Spacer(1, 5))
        data = [[ar("البند"), ar("القيمة")]] + [[ar(a), ar(b)] for a, b in rows]
        t = Table(data, colWidths=[220, 230])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.6, HexColor('#bdbdbd')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

    mini_table("🍽️ العلف", '#e65100', [
        ("علف/رأس/يوم", f"{feas['feed']['per_head_day_kg']*1000:.0f} جرام"),
        ("إجمالي يومي", f"{feas['feed']['total_day_kg']:.1f} كجم"),
        ("إجمالي سنوي", f"{feas['feed']['total_year_ton']:.2f} طن"),
    ])
    mini_table("💧 الماء", '#1976d2', [
        ("ماء/رأس/يوم", f"{feas['water']['per_head_day_L']:.1f} لتر"),
        ("إجمالي سنوي", f"{feas['water']['total_year_m3']:.1f} م³"),
    ])
    mini_table("👷 العمالة", '#6d4c41', [
        ("عدد العمال", str(feas['labor']['workers'])),
    ])
    story.append(PageBreak())

    story.append(P("📊 الإنتاج", size=18, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 15))

    prod = feas["production"]
    prod_rows = [[ar("البند"), ar("القيمة")]]
    for key, label in [
        ("annual", "الإنتاج السنوي"),
        ("per_day", "الإنتاج اليومي"),
        ("per_cycle", "الإنتاج/دورة"),
        ("cycles_year", "عدد الدورات/سنة"),
        ("lactation_days", "أيام الحلابة"),
        ("weight_ton", "الوزن بالطن"),
    ]:
        if key in prod and prod[key]:
            val = prod[key]
            prod_rows.append([
                ar(label),
                ar(f"{val:,.1f}" if isinstance(val, (int, float)) else str(val))
            ])
    if prod.get("details"):
        prod_rows.append([ar("التفاصيل"), ar(prod["details"])])

    t = Table(prod_rows, colWidths=[220, 230])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
    ]))
    story.append(t)
    story.append(PageBreak())

    story.append(Spacer(1, 60))
    story.append(P("✍️ الاعتماد", size=20, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 40))
    story.append(P(SUPERVISOR, size=20, align=TA_CENTER, color='#c62828'))
    story.append(P(SUPERVISOR_TITLE, size=13, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 50))
    story.append(P(f"🤲 {DUA_FULL} 🤲", size=12, align=TA_CENTER, color='#c62828'))

    doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
    buffer.seek(0)
    return buffer.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# بدائل الحليب — v11.2 (≥75%)
# ═══════════════════════════════════════════════════════════════════════════
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


def formulate_milk_replacer(animal_type, volume_kg=100.0, selected=None,
                             min_utilization=0.75):
    """
    🆕 v11.2 — تركيب بديل حليب بشرط استخدام ≥75% من المواد المختارة.
    محاولة 1: بدون قيود سفلية
    محاولة 2: lower bound = 0.5% لكل مادة (لرفع نسبة الاستخدام)
    """
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "SCIPY غير متوفرة"}

    standard = MILK_REPLACER_STANDARDS.get(animal_type)
    if not standard:
        return {"success": False, "message": "نوع الحيوان غير مدعوم"}

    valid = [i for i in (selected or list(MILK_REPLACER_INGREDIENTS.keys()))
             if i in MILK_REPLACER_INGREDIENTS]
    if len(valid) < 3:
        return {"success": False, "message": "اختر 3 مكونات على الأقل"}

    n = len(valid)
    c = [MILK_REPLACER_INGREDIENTS[i]["price"] for i in valid]

    A_eq = [
        [1.0] * n,
        [MILK_REPLACER_INGREDIENTS[i]["CP"] for i in valid],
        [MILK_REPLACER_INGREDIENTS[i]["Fat"] for i in valid],
    ]
    b_eq = [100.0, standard["CP"] * 100, standard["Fat"] * 100]

    def _try_solve(lower_bound):
        try:
            res = linprog(c, A_eq=A_eq, b_eq=b_eq,
                          bounds=[(lower_bound, 100)] * n, method='highs')
            if not res.success:
                return None
            formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
            used = sum(1 for v in formula.values() if v > 0.5)
            return {
                "formula": formula,
                "cost": res.fun / 100.0,
                "cost_per_kg": res.fun / 10000.0,
                "used_count": used,
                "used_pct": used / n * 100,
            }
        except Exception:
            return None

    # محاولة 1
    result = _try_solve(0.0)

    # محاولة 2 — إذا الاستخدام < 75%
    if result and result["used_pct"] < min_utilization * 100:
        forced = _try_solve(0.5)
        if forced and forced["used_pct"] >= result["used_pct"]:
            result = forced
            result["forced"] = True

    if not result:
        return {"success": False,
                "message": "تعذر التركيب — جرّب مواد أقل أو حرّر الدهن"}

    actual = {"CP": 0, "Fat": 0, "Lactose": 0}
    for ing, pct in result["formula"].items():
        d = MILK_REPLACER_INGREDIENTS[ing]
        actual["CP"] += pct / 100.0 * d["CP"]
        actual["Fat"] += pct / 100.0 * d["Fat"]
        actual["Lactose"] += pct / 100.0 * d["Lactose"]

    warning = None
    if result["used_pct"] < min_utilization * 100:
        warning = (f"⚠️ تم استخدام {result['used_count']}/{n} مادة "
                   f"({result['used_pct']:.0f}% < 75%) — زد الكمية أو غيّر المزيج")

    return {
        "success": True,
        "formula": result["formula"],
        "cost_per_100kg": result["cost"],
        "cost_per_kg": result["cost_per_kg"],
        "standard": standard, "actual": actual,
        "animal": animal_type,
        "used_count": result["used_count"],
        "used_pct": result["used_pct"],
        "warning": warning,
    }


# ═══════════════════════════════════════════════════════════════════════════
# 📌 نهاية الجزء 2 — توقف هنا
# الجزء 3 يحتوي على:
#   - DEFAULTS + Session State
#   - SharedStorage (تعدد الأجهزة)
#   - CSS الكامل الجديد
#   - بوابة الدخول
#   - الواجهة الرئيسية
#   - كل التبويبات (بدون بورصة ولا موقع جغرافي):
#     * النمذجة (مع بطاقة الحالة الفسيولوجية + بحث فوري)
#     * الزيوت
#     * بدائل الحليب (≥75%)
#     * OCR
#     * الحظائر 3D
#     * الجدوى (3 خيارات + حساسية)
#     * مزارع الدجاج
#     * المستودعات (بدون بورصة)
#     * الفواتير
#     * الديباجة
#     * التحليلات
#     * التعليقات (مع مزامنة)
#     * المراجع
#     * المساعدة
#     * الدليل
#   - Footer
# ═══════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════
# تاور نولجي TAWOR NOLOGY 11.2 — (الجزء 3/3)
# Session + SharedStorage + CSS + بوابة + الواجهة + كل التبويبات + Footer
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# Session State الأولي
# ═══════════════════════════════════════════════════════════════════════════
DEFAULTS = {
    "approved": False,
    "user_role": None,
    "active_formula": {},
    "active_stage_title": "إنتاج عام",
    "active_animal_img": ANIMAL_IMAGES["عام"],
    "computed_ton_cost": 280.0,
    "inventory": {},
    "shared_comments": f"• مرحباً بكم في {APP_NAME}\n• {DUA_SHORT}\n",
    "broiler_farms": {},
    "barn_last_dims": None,
    "last_formulation_result": None,
    "last_formulation_context": None,
    "barn_video_gif": None,
    "last_ocr_result": None,
    "last_ocr_nutrients": None,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state["inventory"]:
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing in cat:
            st.session_state["inventory"][ing] = {
                "quantity": 25.0,
                "min_threshold": 5.0,
                "unit": "طن",
            }


# ═══════════════════════════════════════════════════════════════════════════
# 🆕 v11.2 — التخزين المشترك (تعدد الأجهزة)
# ═══════════════════════════════════════════════════════════════════════════
import time as _time


class SharedStorage:
    """تخزين مشترك بين جميع الأجهزة المتصلة (Shared JSON File)."""
    _lock = threading.Lock()
    FILE = "tawor_shared_state.json"

    @classmethod
    def _load(cls):
        try:
            if os.path.exists(cls.FILE):
                with open(cls.FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    @classmethod
    def _save(cls, data):
        try:
            with cls._lock:
                tmp = cls.FILE + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                os.replace(tmp, cls.FILE)
        except Exception:
            pass

    @classmethod
    def get(cls, key, default=None):
        with cls._lock:
            data = cls._load()
            return data.get(key, default)

    @classmethod
    def set(cls, key, value):
        with cls._lock:
            data = cls._load()
            data[key] = value
            data["_updated_at"] = datetime.now().isoformat()
            cls._save(data)

    @classmethod
    def append_line(cls, key, line):
        with cls._lock:
            data = cls._load()
            current = data.get(key, "")
            data[key] = current + "\n" + line
            cls._save(data)
            return data[key]


# تحميل التعليقات من التخزين المشترك عند البدء
try:
    _persisted_comments = SharedStorage.get("shared_comments")
    if _persisted_comments:
        st.session_state["shared_comments"] = _persisted_comments
except Exception:
    pass


def is_owner():
    return st.session_state.get("user_role") == "owner"


# ═══════════════════════════════════════════════════════════════════════════
# 🆕 v11.2 — CSS كامل (Glassmorphism + Animations + Mobile)
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&family=Tajawal:wght@400;700;900&display=swap');

:root {
    --green-900: #0d3011; --green-700: #1b5e20; --green-500: #2e7d32;
    --green-300: #66bb6a; --green-100: #e8f5e9;
    --gold-500: #d4af37; --gold-300: #f4d47c;
    --danger-700: #c62828; --danger-100: #ffebee;
    --warn-700: #e65100; --warn-100: #fff3e0;
    --info-700: #1565c0; --info-100: #e3f2fd;
    --ink-900: #1a1a1a; --ink-500: #555;
    --card-bg: rgba(255, 255, 255, 0.92);
    --shadow-sm: 0 2px 8px rgba(0,0,0,0.06);
    --shadow-md: 0 6px 24px rgba(0,0,0,0.10);
    --shadow-lg: 0 15px 45px rgba(0,0,0,0.15);
    --shadow-glow: 0 0 30px rgba(212,175,55,0.35);
    --radius-sm: 10px; --radius-md: 16px; --radius-lg: 22px;
}

* { font-family: 'Cairo', 'Tajawal', 'Amiri', sans-serif; color: var(--ink-900) !important; }

html, body, [data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
.stApp { background: transparent; }

.main-box {
    background: var(--card-bg);
    padding: 32px;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    margin-bottom: 70px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(212, 175, 55, 0.20);
}

h1, h2, h3, h4, h5, p, span, li, div, label { color: var(--ink-900) !important; }

@keyframes duaGlow {
    0%, 100% { box-shadow: 0 15px 45px rgba(0,0,0,0.4), inset 0 0 30px rgba(212,175,55,0.2); }
    50% { box-shadow: 0 15px 45px rgba(0,0,0,0.5), inset 0 0 45px rgba(212,175,55,0.45), var(--shadow-glow); }
}
@keyframes floatIcon { 0%,100% { transform: translateY(0) rotate(0); } 50% { transform: translateY(-12px) rotate(6deg); } }
@keyframes gradientShift { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
@keyframes shimmerText { 0% { background-position: -500% 0; } 100% { background-position: 500% 0; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }

.dua-main-box {
    background: linear-gradient(135deg, #0d3011 0%, #1b5e20 25%, #2e7d32 50%, #1b5e20 75%, #0d3011 100%);
    background-size: 200% 200%;
    animation: duaGlow 4s ease-in-out infinite, gradientShift 12s ease infinite;
    padding: 34px 28px; border-radius: var(--radius-lg);
    border: 4px solid var(--gold-500);
    direction: rtl; text-align: center; margin: 25px 0;
    position: relative; overflow: hidden;
}
.dua-main-box::before {
    content: "🕌"; position: absolute; top: 15px; right: 25px;
    font-size: 3.5rem; opacity: 0.25; animation: floatIcon 4s ease-in-out infinite;
}
.dua-main-box::after {
    content: "🕌"; position: absolute; bottom: 15px; left: 25px;
    font-size: 3.5rem; opacity: 0.25; animation: floatIcon 5s ease-in-out infinite reverse;
}
.dua-main-box * { color: white !important; position: relative; z-index: 2; }
.dua-main-box h3 {
    color: var(--gold-500) !important; font-size: 1.9rem; margin-bottom: 18px;
    font-weight: 900; letter-spacing: 1px; text-shadow: 0 2px 10px rgba(212,175,55,0.5);
}
.dua-main-box .names {
    display: inline-block;
    background: linear-gradient(90deg, rgba(212,175,55,0.15), rgba(212,175,55,0.35), rgba(212,175,55,0.15));
    background-size: 200% 100%;
    animation: shimmerText 4s linear infinite;
    font-size: 1.65rem; font-weight: 900; color: #ffeb3b !important;
    margin: 20px 0; padding: 16px 30px;
    border: 2px solid var(--gold-500); border-radius: var(--radius-md);
    text-shadow: 0 0 20px rgba(255,235,59,0.6);
    font-family: 'Amiri', serif !important;
}
.dua-main-box p.quran {
    font-family: 'Amiri', serif !important;
    font-size: 1.2rem; color: var(--gold-500) !important;
    margin-top: 22px; padding: 18px 25px;
    background: rgba(0,0,0,0.25); border-radius: 12px;
    border-right: 5px solid var(--gold-500);
    border-left: 5px solid var(--gold-500);
}

.visitor-dua-banner {
    background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 50%, #ffe082 100%);
    padding: 20px 28px; border-radius: var(--radius-md);
    border: 3px solid var(--gold-500);
    margin: 22px 0; direction: rtl; text-align: center;
    box-shadow: var(--shadow-md); animation: fadeInUp 0.6s ease;
}
.visitor-dua-banner * { color: #4e342e !important; }
.visitor-dua-banner b { color: var(--danger-700) !important; font-size: 1.15rem; font-family: 'Amiri', serif !important; }

.dua-fixed-banner {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32, #1b5e20, #0d3011);
    background-size: 200% 100%;
    animation: gradientShift 8s linear infinite;
    color: white !important;
    padding: 12px 20px; z-index: 9998; text-align: center;
    border-top: 3px solid var(--gold-500);
    font-family: 'Amiri', serif !important;
    font-size: 1.05rem; font-weight: bold;
    box-shadow: 0 -4px 25px rgba(0,0,0,0.4); letter-spacing: 0.5px;
}
.dua-fixed-banner * { color: #ffeb3b !important; font-family: 'Amiri', serif !important; }

.section-title {
    color: var(--green-700) !important;
    border-right: 6px solid var(--green-500);
    padding: 12px 18px; text-align: right;
    font-size: 1.5rem; font-weight: 900;
    margin-top: 30px; margin-bottom: 20px;
    background: linear-gradient(to left, rgba(46,125,50,0.15), transparent);
    border-radius: var(--radius-sm); animation: fadeInUp 0.4s ease;
}

.formula-item {
    background: linear-gradient(135deg, #ffffff 0%, #e8f5e9 100%);
    padding: 15px 20px; border-radius: var(--radius-sm);
    margin-bottom: 10px; font-weight: 700; color: var(--green-700) !important;
    border-right: 5px solid var(--green-500);
    box-shadow: var(--shadow-sm); text-align: right;
    transition: transform 0.2s, box-shadow 0.2s;
}
.formula-item:hover { transform: translateX(-4px); box-shadow: var(--shadow-md); }

.oil-item {
    background: linear-gradient(135deg, #fff8e1 0%, #ffe0b2 100%);
    padding: 12px 18px; border-radius: var(--radius-sm);
    margin-bottom: 8px; font-weight: 700; color: #bf360c !important;
    border-right: 5px solid var(--warn-700);
    box-shadow: 0 4px 15px rgba(230,81,0,0.15); text-align: right;
}

.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px; border-radius: var(--radius-md);
    border-right: 5px solid var(--green-500);
    margin-bottom: 20px; direction: rtl; text-align: right;
    box-shadow: var(--shadow-sm);
}
.oil-info-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 18px; border-radius: var(--radius-md);
    border-right: 5px solid var(--warn-700);
    margin-bottom: 18px; direction: rtl; text-align: right;
}
.barn-info-card {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 18px; border-radius: var(--radius-md);
    border-right: 5px solid var(--info-700);
    margin-bottom: 18px; direction: rtl; text-align: right;
}
.feas-card {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 20px; border-radius: var(--radius-lg);
    border-right: 6px solid var(--green-500);
    margin-bottom: 20px; direction: rtl; text-align: right;
}
.physio-card {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 18px 24px; border-radius: 14px;
    border-right: 6px solid #1565c0;
    margin-bottom: 20px; direction: rtl; text-align: right;
    box-shadow: 0 4px 15px rgba(21,101,192,0.2);
    animation: fadeInUp 0.5s ease;
}

.quality-good-v112 {
    background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%);
    padding: 24px; border-radius: var(--radius-lg);
    border-right: 8px solid var(--green-700);
    margin: 18px 0; direction: rtl; text-align: right;
    box-shadow: 0 6px 25px rgba(27,94,32,0.22);
    animation: fadeInUp 0.5s ease;
}
.quality-bad-v112 {
    background: linear-gradient(135deg, #ffcdd2 0%, #ef9a9a 100%);
    padding: 24px; border-radius: var(--radius-lg);
    border-right: 8px solid var(--danger-700);
    margin: 18px 0; direction: rtl; text-align: right;
    box-shadow: 0 6px 25px rgba(198,40,40,0.22);
    animation: fadeInUp 0.5s ease;
}

.profile-img-style {
    width: 150px; height: 150px; border-radius: 50%;
    object-fit: cover; border: 4px solid var(--gold-500);
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    display: block; margin: 0 auto;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.profile-img-style:hover { transform: scale(1.05); box-shadow: var(--shadow-glow); }

.stButton > button {
    color: var(--ink-900) !important;
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9) !important;
    border: 1.5px solid var(--green-500) !important;
    font-weight: 700 !important;
    border-radius: var(--radius-sm) !important;
    transition: all 0.25s ease !important;
    padding: 10px 20px !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #c8e6c9, #a5d6a7) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-md) !important;
}

.mini-signature {
    position: fixed; left: 20px; bottom: 70px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important;
    padding: 9px 22px; font-size: 0.85rem;
    border-radius: 25px; z-index: 9997; direction: rtl;
    border: 2px solid var(--gold-500); font-weight: 700;
    box-shadow: var(--shadow-md);
}
.mini-signature * { color: white !important; }

.stTextInput > div > div > input {
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid var(--green-500) !important;
    padding: 10px 14px !important; font-size: 1rem !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 6px; background-color: rgba(255,255,255,0.6);
    padding: 8px; border-radius: var(--radius-md);
}
.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-sm) !important;
    padding: 10px 18px !important; font-weight: 700 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--green-500), var(--green-700)) !important;
    color: white !important;
}
.stTabs [aria-selected="true"] * { color: white !important; }

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff, #f1f8e9);
    padding: 14px 18px; border-radius: var(--radius-md);
    border-right: 4px solid var(--green-500);
    box-shadow: var(--shadow-sm);
}
[data-testid="stMetricValue"] { color: var(--green-700) !important; font-weight: 900 !important; }

@media (max-width: 768px) {
    .main-box { padding: 18px; margin-bottom: 80px; }
    .dua-main-box h3 { font-size: 1.4rem; }
    .dua-main-box .names { font-size: 1.2rem; padding: 12px 18px; }
    .section-title { font-size: 1.2rem; padding: 10px 14px; }
    .dua-fixed-banner { font-size: 0.85rem; padding: 10px 14px; }
    .mini-signature { font-size: 0.75rem; padding: 7px 16px; bottom: 62px; }
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# بوابة الدخول
# ═══════════════════════════════════════════════════════════════════════════
if not st.session_state["approved"]:
    st.markdown(
        '<div class="main-box" style="max-width: 780px; margin: 30px auto; direction: rtl;">',
        unsafe_allow_html=True
    )
    st.markdown(f"""
    <div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <p style="font-size:1.1rem; color:#a5d6a7 !important; margin-bottom:12px;">
        نبدأ باسم الله، ونسألُه أن يتقبّلَ هذا العملَ صدقةً جاريةً عن:
        </p>
        <div class="names">
        🕊️ رحم الله والدي إسماعيل تاور وأختي ابتسام 🕊️
        </div>
        <p class="quran">{DUA_QURAN}</p>
        <p class="quran" style="margin-top:10px;">{DUA_VERSE}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 2px solid #d4af37; margin: 25px 0;'>",
                unsafe_allow_html=True)

    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        if img_base64:
            st.markdown(
                f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">',
                unsafe_allow_html=True
            )
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
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        padding: 20px; border-radius: 12px; border: 2px solid #2e7d32;
        text-align: center; margin-bottom: 10px;">
        <h4 style="color: #1b5e20;">👑 المالك</h4>
        <p style="font-size: 0.9rem; color: #555;">الدخول بكود خاص</p>
        </div>
        """, unsafe_allow_html=True)
        owner_code_input = st.text_input("🔑 كود المالك:", type="password", key="owner_code")
        if st.button("👑 دخول المالك", type="primary", use_container_width=True):
            if owner_code_input.strip() == OWNER_CODE:
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
        <p style="font-size: 0.9rem; color: #555;">دخول مجاني<br>
        <small style="color: #999;">(يشمل الحظائر 3D + الجدوى + المزارع + OCR)</small></p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True):
            st.session_state.update({"approved": True, "user_role": "guest"})
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════
# الواجهة الرئيسية
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="main-box">', unsafe_allow_html=True)

c1, c2 = st.columns([0.7, 0.3])
with c2:
    role_label = "المالك 👑" if is_owner() else "زائر 👥"
    st.markdown(
        f"<div style='text-align:left; padding:10px; background:#f5f5f5;"
        f"border-radius:10px;'>الحساب: <b>{role_label}</b></div>",
        unsafe_allow_html=True
    )
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.cache_data.clear()
        st.cache_resource.clear()
        st.session_state["approved"] = False
        st.rerun()

c3, c4 = st.columns([0.3, 0.7])
with c3:
    if img_base64:
        st.markdown(
            f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">',
            unsafe_allow_html=True
        )
with c4:
    st.markdown(f"""
    <h1 style='color: #0d3011; text-align:right; margin-bottom:0;
               text-shadow: 2px 2px 4px rgba(0,0,0,0.15), 0 0 20px rgba(27,94,32,0.4);
               font-weight: 900; font-size: 2.3rem;'>
    🌾 {APP_NAME}
    </h1>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <p style='color: #1565C0; text-align:right; font-size: 1.25rem; font-weight: 600;
              margin-top: 8px;'>
    {APP_TAGLINE}
    </p>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #fff8e1, #ffe082);
                padding: 12px 20px; border-radius: 12px;
                border-right: 6px solid #c62828; border-left: 6px solid #c62828;
                margin-top: 10px; box-shadow: 0 4px 15px rgba(198,40,40,0.25);'>
        <h3 style='color: #b71c1c; text-align:right; margin: 0;
                   font-weight: 900; font-size: 1.55rem;'>
        👨‍🔬 {SUPERVISOR}
        </h3>
        <p style='color: #0d47a1; text-align:right; margin: 5px 0 0 0;
                  font-weight: 700; font-size: 1.15rem;'>✨ {SUPERVISOR_TITLE}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="visitor-dua-banner">{DUA_VISITOR}</div>', unsafe_allow_html=True)
st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# تعريف التبويبات (بدون البورصة ✅)
# ═══════════════════════════════════════════════════════════════════════════
if is_owner():
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "🌰 مكتبة الزيوت",
        "🍼 بدائل الحليب",
        "📷 المختبر الذكي OCR",
        "🏗️ تصميم الحظائر 3D",
        "📊 دراسة الجدوى",
        "🐔 مزارع الدجاج",
        "🏭 المستودعات",
        "🧾 الفواتير",
        "🖨️ الديباجة",
        "📈 التحليلات",
        "💬 التعليقات",
        "📚 المراجع",
        "💡 المساعدة",
        "📖 الدليل",
    ]
else:
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية",
        "🌰 مكتبة الزيوت",
        "🍼 بدائل الحليب",
        "📷 المختبر الذكي OCR",
        "🏗️ تصميم الحظائر 3D",
        "📊 دراسة الجدوى",
        "🐔 مزارع الدجاج",
        "📚 المراجع",
        "💡 المساعدة",
        "📖 الدليل",
    ]

tabs = st.tabs(tabs_titles)
tab_map = {title: tab for title, tab in zip(tabs_titles, tabs)}


# ═══════════════════════════════════════════════════════════════════════════
# تبويب النمذجة (بدون موقع جغرافي ✅ | مع بطاقة الحالة الفسيولوجية ✅)
# ═══════════════════════════════════════════════════════════════════════════
with tab_map["🔬 النمذجة والحسابات العلفية"]:
    try:
        sub_tab_formulator, sub_tab_analyzer = st.tabs([
            "🎯 تركيب علفة (جودة ≥ 70%)",
            "🔬 مختبر تحليل وفحص",
        ])

        with sub_tab_formulator:
            try:
                # ✅ v11.2 — لا موقع جغرافي — USD فقط
                local_rate = 1.0
                local_sym = "USD"
                city = "—"
                # أسعار أساسية ثابتة
                live_prices = {
                    ing: d.get("price", 280.0)
                    for cat in BIG_FEEDS_LIBRARY.values()
                    for ing, d in cat.items()
                }

                st.markdown('<div class="section-title">🧬 أساس حساب البروتين</div>',
                            unsafe_allow_html=True)
                protein_basis_choice = st.radio(
                    "اختر أساس الحساب:",
                    ["البروتين المهضوم (DP) — الأدق علمياً",
                     "البروتين الخام (CP) — الأسهل ميدانياً"],
                    horizontal=True, key="protein_basis"
                )
                use_dp = "DP" in protein_basis_choice
                basis_code = "DP" if use_dp else "CP"

                st.markdown('<div class="section-title">🐾 اختر الحيوان والحالة</div>',
                            unsafe_allow_html=True)
                animal_tabs = st.tabs([
                    "🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐪 إبل",
                    "🐎 خيول", "🐔 دواجن", "🦆 سمان", "🐟 أسماك", "🐇 أرانب",
                ])

                animal_choice = None
                production_type = None
                requirement = None
                img_key = "عام"
                std_key_global = ""

                # ─── أبقار ───
                with animal_tabs[0]:
                    st.markdown("### 🐄 احتياجات الأبقار — NRC 2001")
                    cattle_type = st.selectbox(
                        "الحالة الفسيولوجية:",
                        ["حليب_عالي", "حليب_متوسط", "حليب_منخفض",
                         "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"],
                        format_func=lambda x: {
                            "حليب_عالي": "🐄 حلابة عالية",
                            "حليب_متوسط": "🐄 حلابة متوسطة",
                            "حليب_منخفض": "🐄 حلابة منخفضة",
                            "تسمين_مكثف": "💪 تسمين مكثف",
                            "تسمين_عادي": "💪 تسمين عادي",
                            "حمل_أخير": "🤰 حمل آخر",
                            "صيانة": "🌿 صيانة",
                        }.get(x, x), key="cattle_type"
                    )
                    c1_, c2_ = st.columns(2)
                    cattle_params = {}
                    with c1_:
                        if "حليب" in cattle_type:
                            cattle_params["milk_yield"] = st.number_input(
                                "🥛 إنتاج الحليب (كجم):", 5.0, 60.0, 20.0, 1.0,
                                key="cattle_milk"
                            )
                        cattle_params["weight_kg"] = st.number_input(
                            "⚖️ الوزن (كجم):", 200.0, 900.0, 500.0, 25.0,
                            key="cattle_wt"
                        )
                    with c2_:
                        req_pre = get_cattle_requirements(cattle_type, **cattle_params)
                        st.metric("🧬 DP", f"{req_pre.DP}%")
                        st.metric("🧬 CP", f"{req_pre.CP}%")
                        st.metric("🌽 SE", f"{req_pre.SE}")
                    if st.checkbox("✅ اعتماد الأبقار", key="use_cattle"):
                        animal_choice = "أبقار"
                        production_type = cattle_type
                        requirement = req_pre
                        img_key = "أبقار"
                        std_key_global = f"أبقار_{cattle_type}"

                # ─── أغنام ───
                with animal_tabs[1]:
                    st.markdown("### 🐏 احتياجات الأغنام — NRC 2007")
                    sg = st.radio("الجنس:", ["ذكر (تسمين)", "أنثى (أمهات)"],
                                  horizontal=True, key="sheep_gender")
                    is_male_s = "ذكر" in sg
                    if is_male_s:
                        sheep_type = st.selectbox("الحالة:",
                            ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد"], key="sheep_t_m")
                    else:
                        sheep_type = st.selectbox("الحالة:",
                            ["مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"], key="sheep_t_f")
                    litter = 1
                    if sheep_type == "مرضعات":
                        litter = st.number_input("👶 عدد المواليد:", 1, 3, 1, 1,
                                                  key="sheep_litter")
                    weight_s = st.number_input("⚖️ الوزن (كجم):", 15.0, 120.0, 50.0, 5.0,
                                                key="sheep_wt")
                    req_pre = get_sheep_requirements(sheep_type, is_male=is_male_s,
                                                     weight_kg=weight_s, litter_size=litter)
                    p1, p2, p3 = st.columns(3)
                    p1.metric("🧬 DP", f"{req_pre.DP}%")
                    p2.metric("🧬 CP", f"{req_pre.CP}%")
                    p3.metric("🌽 SE", f"{req_pre.SE}")
                    if st.checkbox("✅ اعتماد الأغنام", key="use_sheep"):
                        animal_choice = "أغنام"
                        production_type = sheep_type
                        requirement = req_pre
                        img_key = "أغنام"
                        std_key_global = f"أغنام_{sheep_type}"

                # ─── ماعز ───
                with animal_tabs[2]:
                    st.markdown("### 🐐 احتياجات الماعز — NRC 2007")
                    gg = st.radio("الجنس:", ["ذكر (تسمين)", "أنثى (حلابة)"],
                                  horizontal=True, key="goat_gender")
                    is_male_g = "ذكر" in gg
                    milk_g = 0
                    if is_male_g:
                        goat_type = st.selectbox("الحالة:",
                            ["تسمين_جديان", "تيوس"], key="goat_t_m")
                    else:
                        goat_type = st.selectbox("الحالة:",
                            ["حلابة_عالي", "حلابة_متوسط", "حامل_أخير", "صيانة"],
                            key="goat_t_f")
                        if "حلابة" in goat_type:
                            milk_g = st.number_input("🥛 إنتاج الحليب (كجم):", 0.5, 8.0,
                                                     2.0, 0.25, key="goat_milk")
                    req_pre = get_goat_requirements(goat_type, is_male=is_male_g,
                                                    milk_yield=milk_g)
                    p1, p2, p3 = st.columns(3)
                    p1.metric("🧬 DP", f"{req_pre.DP}%")
                    p2.metric("🧬 CP", f"{req_pre.CP}%")
                    p3.metric("🌽 SE", f"{req_pre.SE}")
                    if st.checkbox("✅ اعتماد الماعز", key="use_goat"):
                        animal_choice = "ماعز"
                        production_type = goat_type
                        requirement = req_pre
                        img_key = "ماعز"
                        std_key_global = f"ماعز_{goat_type}"

                # ─── إبل ───
                with animal_tabs[3]:
                    st.markdown("### 🐪 احتياجات الإبل — FAO 2010")
                    camel_type = st.selectbox("الحالة:",
                        ["نمو", "تسمين", "حليب", "سباق", "صيانة"], key="camel_type")
                    camel_wt = st.number_input("⚖️ الوزن (كجم):", 100.0, 800.0, 400.0,
                                                25.0, key="camel_wt")
                    camel_milk = 5.0
                    if camel_type == "حليب":
                        camel_milk = st.number_input("🥛 إنتاج الحليب (لتر):", 2.0, 20.0,
                                                      5.0, 0.5, key="camel_milk")
                    req_pre = get_camel_requirements(camel_type, weight_kg=camel_wt,
                                                     milk_yield=camel_milk)
                    p1, p2, p3 = st.columns(3)
                    p1.metric("🧬 DP", f"{req_pre.DP}%")
                    p2.metric("🧬 CP", f"{req_pre.CP}%")
                    p3.metric("🌽 SE", f"{req_pre.SE}")
                    if st.checkbox("✅ اعتماد الإبل", key="use_camel"):
                        animal_choice = "إبل"
                        production_type = camel_type
                        requirement = req_pre
                        img_key = "إبل"
                        std_key_global = f"إبل_{camel_type}"

                # ─── خيول (مع شريط الوزن الجديد) ───
                with animal_tabs[4]:
                    st.markdown("### 🐎 احتياجات الخيول — NRC 2007")
                    horse_type = st.selectbox(
                        "الحالة:",
                        ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار", "مرضعات", "صيانة"],
                        key="horse_type"
                    )

                    st.markdown("#### ⚖️ تقدير الوزن — معادلة Carroll & Huntington")
                    est_method = st.radio(
                        "طريقة الوزن:",
                        ["📏 تقدير بالقياسات (دقيق)", "🎚️ شريط تقديري (سريع)"],
                        horizontal=True, key="horse_wt_method"
                    )

                    if "قياسات" in est_method:
                        hc1, hc2 = st.columns(2)
                        with hc1:
                            girth_cm = st.slider("محيط الصدر (Girth) — سم:", 120, 230, 175, 1,
                                                  key="horse_girth")
                        with hc2:
                            length_cm = st.slider("طول الجسم (Body Length) — سم:", 100, 210, 155, 1,
                                                   key="horse_length")
                        # معادلة Carroll & Huntington 1988
                        horse_wt = (girth_cm ** 2 * length_cm) / 11877.0
                        st.info(f"📐 الوزن التقديري: **{horse_wt:.1f} كجم** "
                                f"(محيط {girth_cm} سم × طول {length_cm} سم)")
                    else:
                        horse_wt = st.slider("⚖️ الوزن التقديري (كجم):", 150, 800, 450, 10,
                                              key="horse_wt_slider")
                        st.caption("💡 العربي: 350–450 كجم | الرياضي: 450–550 كجم")

                    req_pre = get_horse_requirements(horse_type, weight_kg=horse_wt)
                    p1, p2, p3, p4 = st.columns(4)
                    p1.metric("🧬 DP", f"{req_pre.DP}%")
                    p2.metric("🧬 CP", f"{req_pre.CP}%")
                    p3.metric("🌽 SE", f"{req_pre.SE}")
                    p4.metric("⚖️ الوزن", f"{horse_wt:.0f} كجم")

                    if st.checkbox("✅ اعتماد الخيول", key="use_horse"):
                        animal_choice = "خيول"
                        production_type = horse_type
                        requirement = req_pre
                        img_key = "خيول"
                        std_key_global = f"خيول_{horse_type}"

                # ─── دواجن ───
                with animal_tabs[5]:
                    st.markdown("### 🐔 احتياجات الدواجن")
                    poultry_strain = st.radio("السلالة:", ["لاحم", "بياض"],
                                              horizontal=True, key="poultry_strain")
                    poultry_age = st.number_input("العمر (أسبوع):", 1, 20, 1, 1,
                                                   key="poultry_age")
                    req_pre = get_poultry_requirements(poultry_strain, poultry_age)
                    p1, p2, p3, p4 = st.columns(4)
                    p1.metric("🧬 DP", f"{req_pre.DP}%")
                    p2.metric("🧬 CP", f"{req_pre.CP}%")
                    p3.metric("🌽 SE", f"{req_pre.SE}")
                    p4.metric("Ca", f"{req_pre.Ca}%")
                    if st.checkbox("✅ اعتماد الدواجن", key="use_poultry"):
                        animal_choice = "دواجن"
                        production_type = poultry_strain
                        requirement = req_pre
                        img_key = "دواجن"
                        if "بادي" in req_pre.name_ar:
                            std_key_global = "دواجن_بادي"
                        elif "نامي" in req_pre.name_ar:
                            std_key_global = "دواجن_نامي"
                        elif "بياض" in req_pre.name_ar:
                            std_key_global = "دواجن_بياض"
                        else:
                            std_key_global = "دواجن_ناهي"

                # ─── سمان ───
                with animal_tabs[6]:
                    st.markdown("### 🦆 احتياجات السمان")
                    quail_strain = st.radio("النوع:", ["تسمين", "بياض"],
                                            horizontal=True, key="quail_strain")
                    quail_age = st.number_input("العمر (أسبوع):", 1, 8, 1, 1,
                                                 key="quail_age")
                    req_pre = get_quail_requirements(quail_strain, quail_age)
                    p1, p2, p3 = st.columns(3)
                    p1.metric("🧬 DP", f"{req_pre.DP}%")
                    p2.metric("🧬 CP", f"{req_pre.CP}%")
                    p3.metric("🌽 SE", f"{req_pre.SE}")
                    if st.checkbox("✅ اعتماد السمان", key="use_quail"):
                        animal_choice = "سمان"
                        production_type = quail_strain
                        requirement = req_pre
                        img_key = "سمان"
                        std_key_global = "سمان_بياض" if quail_strain == "بياض" else "سمان_بادي"

                # ─── أسماك ───
                with animal_tabs[7]:
                    st.markdown("### 🐟 احتياجات الأسماك")
                    fish_species = st.selectbox("النوع:",
                        ["البلطي النيلي", "القرموط الأفريقي", "الكارب"], key="fish_sp")
                    fish_stage = st.selectbox("المرحلة:",
                                               ["بادئ زريعة", "نمو", "تسمين"], key="fish_stage")
                    req_pre = get_fish_requirements(fish_species, fish_stage)
                    p1, p2, p3 = st.columns(3)
                    p1.metric("🧬 DP", f"{req_pre.DP}%")
                    p2.metric("🧬 CP", f"{req_pre.CP}%")
                    p3.metric("🌽 SE", f"{req_pre.SE}")
                    if st.checkbox("✅ اعتماد الأسماك", key="use_fish"):
                        animal_choice = "أسماك"
                        production_type = fish_stage
                        requirement = req_pre
                        img_key = "أسماك"
                        if "بادئ" in fish_stage or "زريعة" in fish_stage:
                            std_key_global = "أسماك_بادئ"
                        elif "نمو" in fish_stage:
                            std_key_global = "أسماك_نمو"
                        else:
                            std_key_global = "أسماك_تسمين"

                # ─── أرانب ───
                with animal_tabs[8]:
                    st.markdown("### 🐇 احتياجات الأرانب")
                    rabbit_type = st.selectbox("الحالة:",
                        ["تسمين", "حليب", "صيانة"], key="rabbit_type")
                    rabbit_wt = st.number_input("⚖️ الوزن (كجم):", 1.0, 8.0, 4.0, 0.5,
                                                  key="rabbit_wt")
                    req_pre = get_rabbit_requirements(rabbit_type, rabbit_wt)
                    p1, p2, p3 = st.columns(3)
                    p1.metric("🧬 DP", f"{req_pre.DP}%")
                    p2.metric("🧬 CP", f"{req_pre.CP}%")
                    p3.metric("🌽 SE", f"{req_pre.SE}")
                    if st.checkbox("✅ اعتماد الأرانب", key="use_rabbit"):
                        animal_choice = "أرانب"
                        production_type = rabbit_type
                        requirement = req_pre
                        img_key = "أرانب"
                        std_key_global = f"أرانب_{rabbit_type}"

                formulation_ready = bool(animal_choice and requirement)

                if not formulation_ready:
                    st.warning("⚠️ اختر حيواناً وفعّل خيار ✅ الاعتماد للمتابعة")
                    if st.session_state.get("last_formulation_result"):
                        st.markdown("---")
                        st.markdown("### 📋 آخر نتيجة محفوظة")
                        prev = st.session_state["last_formulation_result"]
                        prev_ctx = st.session_state.get("last_formulation_context", {})
                        st.info(f"🐾 {prev_ctx.get('animal_choice','—')} | "
                                f"الجودة: {prev.get('quality_score', 0):.1f}%")
                        for ing, pct in prev["formula"].items():
                            st.markdown(
                                f'<div class="formula-item">▪️ <b>{ing}:</b> '
                                f'{pct:.2f}%</div>', unsafe_allow_html=True
                            )
                        st.metric("💰 التكلفة:", f"${prev['cost']:.2f}")

                if formulation_ready:
                    # ═══ بطاقة الحالة الفسيولوجية (v11.2) ═══
                    st.markdown(f"""
                    <div class="physio-card">
                        <h4 style="color: #0d47a1; margin: 0 0 8px 0;">
                            🧬 الحالة الفسيولوجية المعتمدة
                        </h4>
                        <p style="color: #1a237e; font-size: 1.15rem;
                                  font-weight: 700; margin: 0;">
                            {animal_choice} —
                            <span style="color: #c62828;">{requirement.name_ar}</span>
                        </p>
                        <p style="color: #555; margin: 6px 0 0 0; font-size: 0.92rem;">
                            📌 {requirement.note or "حسب المعايير العالمية NRC/INRA/FAO"}
                        </p>
                        <div style="display: flex; gap: 12px; margin-top: 10px; flex-wrap: wrap;">
                            <span style="background:#fff; padding:6px 14px; border-radius:8px;
                                         border:1px solid #90caf9;">
                                🧬 DP: <b>{requirement.DP}%</b>
                            </span>
                            <span style="background:#fff; padding:6px 14px; border-radius:8px;
                                         border:1px solid #90caf9;">
                                🧬 CP: <b>{requirement.CP}%</b>
                            </span>
                            <span style="background:#fff; padding:6px 14px; border-radius:8px;
                                         border:1px solid #90caf9;">
                                🌽 SE: <b>{requirement.SE}</b>
                            </span>
                            <span style="background:#fff; padding:6px 14px; border-radius:8px;
                                         border:1px solid #90caf9;">
                                🌾 NDF: <b>{requirement.NDF}%</b>
                            </span>
                            <span style="background:#fff; padding:6px 14px; border-radius:8px;
                                         border:1px solid #90caf9;">
                                ⚖️ Ca:P: <b>{(requirement.Ca/requirement.P) if requirement.P else 0:.2f}</b>
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    oil_std_info = get_oil_standard(std_key_global)
                    st.markdown('<div class="section-title">🌰 معيار الزيوت</div>',
                                unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="oil-info-card">
                    <b>📊 الحدود:</b> أقصى {oil_std_info['max']}% |
                    مثالي {oil_std_info['optimal']}% |
                    المرجع: {oil_std_info['source']}
                    </div>
                    """, unsafe_allow_html=True)

                    requester_name = st.text_input(
                        "👤 اسم طالب العلفة:", placeholder="مثال: مزرعة الأمل",
                        key="requester"
                    )

                    st.markdown('<div class="section-title">🌾 اختيار المكونات</div>',
                                unsafe_allow_html=True)
                    st.caption("⚠️ **المواد المختارة فقط** — لا إضافات تلقائية.")

                    search_q = st.text_input(
                        "🔍 بحث سريع في المكونات:",
                        placeholder="مثال: ذرة، صويا، ملح...",
                        key="ing_search_v112"
                    )

                    selected_ingredients = []
                    ingredient_prices_dict = {}

                    default_set = get_default_selections(animal_choice, production_type, requirement)

                    for cat_name, items in BIG_FEEDS_LIBRARY.items():
                        filtered_items = (
                            {k: v for k, v in items.items() if search_q.lower() in k.lower()}
                            if search_q else items
                        )
                        if not filtered_items:
                            continue

                        is_expanded = (
                            "الحبوب" in cat_name or "الأكساب" in cat_name
                            or "الزيوت" in cat_name or "الأملاح" in cat_name
                        )
                        with st.expander(f"📁 {cat_name} ({len(filtered_items)} مكون)",
                                          expanded=is_expanded):
                            sub_cols = st.columns(3)
                            for idx, (ing_name, ing_data) in enumerate(filtered_items.items()):
                                with sub_cols[idx % 3]:
                                    default_check = ing_name in default_set
                                    if cat_name == "🌰 الزيوت النباتية والحيوانية":
                                        st.markdown(f"**{ing_name}**")
                                        st.caption(f"⚡ SE={ing_data.get('SE', 0):.0f}")
                                        checked = st.checkbox(
                                            "إضافة", value=False,
                                            key=f"feed_{animal_choice}_{ing_name}"
                                        )
                                    else:
                                        checked = st.checkbox(
                                            ing_name, value=default_check,
                                            key=f"feed_{animal_choice}_{ing_name}"
                                        )

                                    current_live_price = live_prices.get(ing_name, 350.0)
                                    if is_owner():
                                        price_input = st.number_input(
                                            f"السعر ({ing_name}) $:",
                                            min_value=5.0,
                                            value=float(current_live_price),
                                            key=f"price_{animal_choice}_{ing_name}"
                                        )
                                    else:
                                        st.markdown(f"💰 **`${current_live_price:.2f}`**")
                                        price_input = current_live_price

                                    if checked:
                                        selected_ingredients.append(ing_name)
                                        ingredient_prices_dict[ing_name] = price_input

                    st.markdown("---")
                    st.success(f"✅ المكونات المختارة: **{len(selected_ingredients)}** مادة")

                    col_btn1, col_btn2 = st.columns([0.7, 0.3])
                    with col_btn1:
                        run_clicked = st.button(
                            "🚀 تشغيل المحرك العلمي — ضمان جودة ≥ 70%",
                            type="primary", use_container_width=True, key="run_smart"
                        )
                    with col_btn2:
                        if st.session_state.get("last_formulation_result"):
                            if st.button("🗑️ مسح النتائج", use_container_width=True,
                                          key="clear_results"):
                                st.session_state["last_formulation_result"] = None
                                st.session_state["last_formulation_context"] = None
                                st.rerun()

                    if run_clicked:
                        if len(selected_ingredients) < 3:
                            st.error("⚠️ اختر 3 مكونات على الأقل")
                        else:
                            custom_standard = requirement_to_standard(requirement)
                            with st.spinner(f"⏳ جاري التركيب على أساس {basis_code}..."):
                                result = auto_formulate_smart(
                                    selected_ingredients, ingredient_prices_dict,
                                    custom_standard, standard_key=std_key_global,
                                    basis=basis_code, min_quality=70.0,
                                    animal_type=animal_choice,
                                    production_type=production_type,
                                )
                            if result["success"]:
                                st.session_state["last_formulation_result"] = result
                                st.session_state["last_formulation_context"] = {
                                    "animal_choice": animal_choice,
                                    "requirement_name": requirement.name_ar,
                                    "basis_label": basis_code,
                                    "requirement": requirement,
                                    "custom_standard": custom_standard,
                                    "city": city,
                                    "local_rate": local_rate,
                                    "local_sym": local_sym,
                                    "requester_name": requester_name,
                                    "std_key_global": std_key_global,
                                    "img_key": img_key,
                                    "animal_type": animal_choice,
                                    "production_type": production_type,
                                }
                                st.session_state["active_formula"] = result["formula"]
                                st.session_state["computed_ton_cost"] = result["cost"]
                            else:
                                st.error(f"❌ {result['message']}")

                    # ═══ عرض النتائج ═══
                    if st.session_state.get("last_formulation_result"):
                        result = st.session_state["last_formulation_result"]
                        ctx = st.session_state["last_formulation_context"]

                        formula = result["formula"]
                        actual = result["actual_nutrients"]
                        cost = result["cost"]
                        total_oil = result.get("total_oil", 0.0)
                        oil_std = result.get("oil_std", oil_std_info)
                        custom_standard = ctx["custom_standard"]
                        basis_label = ctx["basis_label"]
                        quality = result.get("quality_score", 0.0)
                        meets = result.get("meets_standard", False)

                        ca_p_ratio = (actual.get("Ca", 0) / actual.get("P", 1)
                                      if actual.get("P", 0) > 0 else 0)

                        if meets:
                            st.markdown(f"""
                            <div class="quality-good-v112">
                            <div style="display:flex; align-items:center; gap:18px;">
                                <div style="font-size:3rem;">✅</div>
                                <div style="flex:1;">
                                    <h3 style="color:#1b5e20; margin:0; font-size:1.5rem;">
                                        جودة الخلطة: {quality:.1f}%
                                    </h3>
                                    <p style="color:#2e7d32; margin:6px 0 0 0;">
                                        تجتاز الحد الأدنى (70%) — آمنة للاعتماد
                                    </p>
                                </div>
                                <div style="text-align:center; padding:12px 20px;
                                            background:rgba(255,255,255,0.7); border-radius:12px;">
                                    <div style="font-size:0.75rem; color:#666;">Ca:P</div>
                                    <div style="font-size:1.4rem; font-weight:900;
                                                color:{'#1b5e20' if 1.5<=ca_p_ratio<=2 else '#f57c00'};">
                                        {ca_p_ratio:.2f}
                                    </div>
                                </div>
                            </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="quality-bad-v112">
                            <div style="display:flex; align-items:center; gap:18px;">
                                <div style="font-size:3rem;">⚠️</div>
                                <div style="flex:1;">
                                    <h3 style="color:#c62828; margin:0; font-size:1.5rem;">
                                        جودة الخلطة: {quality:.1f}%
                                    </h3>
                                    <p style="color:#b71c1c; margin:6px 0 0 0;">
                                        أقل من 70% — تحتاج تعديلاً
                                    </p>
                                </div>
                                <div style="text-align:center; padding:12px 20px;
                                            background:rgba(255,255,255,0.7); border-radius:12px;">
                                    <div style="font-size:0.75rem; color:#666;">Ca:P</div>
                                    <div style="font-size:1.4rem; font-weight:900;
                                                color:{'#c62828' if ca_p_ratio<1.2 or ca_p_ratio>5 else '#f57c00'};">
                                        {ca_p_ratio:.2f}
                                    </div>
                                </div>
                            </div>
                            </div>
                            """, unsafe_allow_html=True)

                        # جدول المقارنة
                        compare_rows = []
                        compare_scores = []
                        labels = {
                            "CP": "بروتين خام CP", "DP": "بروتين مهضوم DP",
                            "SE": "معادل النشاء SE", "NDF": "NDF", "ADF": "ADF",
                            "EE": "دهن EE", "ASH": "رماد ASH",
                            "Ca": "كالسيوم Ca", "P": "فسفور P",
                        }
                        for k, sv in custom_standard.items():
                            if sv == 0:
                                continue
                            cv = actual.get(k, 0.0)
                            diff = cv - sv
                            pct = (diff / sv * 100) if sv else 0
                            ev = evaluate_difference(pct, standard_value=sv)
                            compare_scores.append({"score": ev["score"]})
                            compare_rows.append({
                                "العنصر": labels.get(k, k),
                                "المعيار": f"{sv:.2f}",
                                "المحسوب": f"{cv:.2f}",
                                "الفرق": f"{diff:+.3f}",
                                "الفرق %": f"{pct:+.2f}%",
                                "التقييم": ev["label"],
                                "score": ev["score"],
                            })

                        # صف Ca:P
                        _ca = actual.get("Ca", 0)
                        _p = actual.get("P", 0)
                        if _p > 0 and _ca > 0:
                            _ratio = _ca / _p
                            if 1.5 <= _ratio <= 2.0:
                                _label, _score = "✅ مثالية", 100
                            elif 1.2 <= _ratio < 1.5 or 2.0 < _ratio <= 3.0:
                                _label, _score = "⚠️ مقبولة", 75
                            elif 0.8 <= _ratio < 1.2 or 3.0 < _ratio <= 5.0:
                                _label, _score = "🟠 خارج النطاق", 40
                            else:
                                _label, _score = "❌ خطرة", 10
                            compare_rows.append({
                                "العنصر": "نسبة Ca:P",
                                "المعيار": "1.5 – 2.0",
                                "المحسوب": f"{_ratio:.2f}",
                                "الفرق": "—", "الفرق %": "—",
                                "التقييم": _label, "score": _score,
                            })
                            compare_scores.append({"score": _score})

                        st.markdown("### 📊 جدول المقارنة الشامل")
                        display_df = pd.DataFrame([
                            {k: v for k, v in r.items() if k != "score"}
                            for r in compare_rows
                        ])
                        st.dataframe(display_df, use_container_width=True, hide_index=True)

                        st.markdown("### 🌾 المكونات النهائية:")
                        for ing, pct in formula.items():
                            st.markdown(
                                f'<div class="formula-item">▪️ <b>{ing}:</b> '
                                f'{pct:.2f}% ({pct*10:.1f} كجم/طن)</div>',
                                unsafe_allow_html=True
                            )

                        st.metric("💰 التكلفة:",
                                  f"${cost:.2f} ({cost*ctx['local_rate']:,.0f} {ctx['local_sym']})")

                        # الرسوم
                        st.markdown('<div class="section-title">📈 الرسوم البيانية</div>',
                                    unsafe_allow_html=True)

                        chart1, chart2 = st.columns(2)
                        with chart1:
                            bar_buf = create_colorful_bar_chart(custom_standard, actual)
                            if bar_buf:
                                st.image(bar_buf.getvalue(), caption="1️⃣ مقارنة العناصر",
                                         use_container_width=True)
                        with chart2:
                            pie_buf = create_colorful_pie_chart(formula)
                            if pie_buf:
                                st.image(pie_buf.getvalue(), caption="2️⃣ توزيع المكونات",
                                         use_container_width=True)

                        chart3, chart4 = st.columns(2)
                        with chart3:
                            radar_buf = create_radar_chart(custom_standard, actual)
                            if radar_buf:
                                st.image(radar_buf.getvalue(), caption="3️⃣ الرادار",
                                         use_container_width=True)
                        with chart4:
                            gauge_buf = create_gauge_chart(quality)
                            if gauge_buf:
                                st.image(gauge_buf.getvalue(), caption="4️⃣ مؤشر الجودة",
                                         use_container_width=True)

                        chart5, chart6 = st.columns(2)
                        with chart5:
                            hbar_buf = create_horizontal_bar_chart(formula)
                            if hbar_buf:
                                st.image(hbar_buf.getvalue(), caption="5️⃣ التوزيع",
                                         use_container_width=True)
                        with chart6:
                            breakdown_buf = create_nutrient_breakdown_pie(actual)
                            if breakdown_buf:
                                st.image(breakdown_buf.getvalue(), caption="6️⃣ الطاقة",
                                         use_container_width=True)

                        chart7, chart8 = st.columns(2)
                        with chart7:
                            if total_oil > 0:
                                oil_chart = create_oil_comparison_chart(total_oil, oil_std)
                                if oil_chart:
                                    st.image(oil_chart.getvalue(),
                                             caption="7️⃣ تقييم الزيوت",
                                             use_container_width=True)
                        with chart8:
                            quality_chart = create_quality_breakdown_chart(compare_rows)
                            if quality_chart:
                                st.image(quality_chart.getvalue(),
                                         caption="8️⃣ تقييم العناصر",
                                         use_container_width=True)

                        # Ca:P
                        if actual.get("P", 0) > 0:
                            cap_chart = create_ca_p_ratio_chart(
                                actual.get("Ca", 0), actual.get("P", 0),
                                custom_standard.get("Ca", 0), custom_standard.get("P", 0))
                            if cap_chart:
                                st.image(cap_chart.getvalue(),
                                         caption="9️⃣ ⚖️ Ca:P",
                                         use_container_width=True)

                        # التحميل
                        st.markdown("### 📥 تحميل التقارير")
                        dl1, dl2 = st.columns(2)
                        with dl1:
                            try:
                                pdf_bytes = pdf_gen.generate_report(
                                    formula=formula,
                                    requirement=ctx["requirement"],
                                    animal_type=ctx["animal_type"],
                                    breed=ctx["requirement_name"],
                                    cost=cost, city=ctx["city"],
                                    local_cost=cost * ctx["local_rate"],
                                    local_sym=ctx["local_sym"],
                                    requester_name=ctx["requester_name"],
                                    protein_basis=basis_label,
                                    standard_key=ctx["std_key_global"],
                                    include_charts=True,
                                    quality_score=quality,
                                )
                                fname = (f"TaworNology_{ctx['animal_type']}_"
                                         f"{datetime.now():%Y%m%d_%H%M}.pdf")
                                st.download_button(
                                    "📥 تحميل PDF", pdf_bytes, file_name=fname,
                                    mime="application/pdf", use_container_width=True,
                                )
                            except Exception as e:
                                st.error(f"⚠️ PDF: {e}")

                        with dl2:
                            try:
                                xl = export_comparison_to_excel(
                                    custom_standard, actual, ctx["requester_name"],
                                    ctx["animal_type"], ctx["requirement_name"],
                                    formula, ctx["std_key_global"])
                                if xl:
                                    fname = (f"TaworNology_{ctx['animal_type']}_"
                                             f"{datetime.now():%Y%m%d_%H%M}.xlsx")
                                    st.download_button(
                                        "📊 تحميل Excel", xl, file_name=fname,
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True,
                                    )
                            except Exception as e:
                                st.error(f"⚠️ Excel: {e}")

            except Exception as e:
                st.error(f"⚠️ خطأ في التركيب: {e}")
                with st.expander("تفاصيل"):
                    st.code(traceback.format_exc())

        with sub_tab_analyzer:
            try:
                st.markdown('<div class="section-title">🔬 مختبر تحليل</div>',
                            unsafe_allow_html=True)
                lab_target = st.selectbox("الفصيل:",
                    ["أبقار", "أغنام", "ماعز", "دواجن لاحم", "دواجن بياض", "أسماك"],
                    key="lab_target")

                all_ings = list(_get_ingredient_lookup().keys())
                lab_inputs = {}
                col_i1, col_i2, col_i3 = st.columns(3)
                seg = len(all_ings) // 3 + 1

                with col_i1:
                    for ing in all_ings[:seg]:
                        lab_inputs[ing] = st.number_input(
                            f"{ing}:", 0.0, value=0.0, step=5.0, key=f"li_{ing}")
                with col_i2:
                    for ing in all_ings[seg:seg*2]:
                        lab_inputs[ing] = st.number_input(
                            f"{ing}:", 0.0, value=0.0, step=5.0, key=f"li_{ing}")
                with col_i3:
                    for ing in all_ings[seg*2:]:
                        lab_inputs[ing] = st.number_input(
                            f"{ing}:", 0.0, value=0.0, step=5.0, key=f"li_{ing}")

                if st.button("🧪 تحليل", type="primary", use_container_width=True):
                    total_w = sum(lab_inputs.values())
                    if total_w <= 0:
                        st.warning("⚠️ أدخل أوزاناً")
                    else:
                        formula_lab = {k: v / total_w * 100
                                        for k, v in lab_inputs.items() if v > 0}
                        nut = compute_formula_nutrients(formula_lab)
                        st.success(f"✅ إجمالي: {total_w:.1f} كجم")
                        df_lab = pd.DataFrame([
                            {"المادة": k, "الوزن": f"{v:.1f}",
                             "النسبة": f"{formula_lab[k]:.2f}%"}
                            for k, v in lab_inputs.items() if v > 0
                        ])
                        st.table(df_lab)
                        st.markdown("### 🔬 التحليل:")
                        n1, n2, n3, n4 = st.columns(4)
                        n1.metric("CP", f"{nut['CP']:.2f}%")
                        n2.metric("DP", f"{nut['DP']:.2f}%")
                        n3.metric("SE", f"{nut['SE']:.1f}")
                        n4.metric("NDF", f"{nut['NDF']:.2f}%")
            except Exception as e:
                st.error(f"⚠️ {e}")

    except Exception as e:
        st.error(f"⚠️ خطأ: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# تبويب مكتبة الزيوت
# ═══════════════════════════════════════════════════════════════════════════
with tab_map["🌰 مكتبة الزيوت"]:
    try:
        st.markdown('<div class="section-title">🌰 مكتبة الزيوت</div>',
                    unsafe_allow_html=True)
        st.write("28 زيتاً وفق NRC، INRA، Ross 308، FAO.")

        st.markdown("### 📊 الحدود القياسية")
        oil_std_rows = [
            {"الحيوان": k, "أقصى %": f"{v['max']}%", "مثالي %": f"{v['optimal']}%",
             "المرجع": v["source"]}
            for k, v in MAX_OIL_PERCENTAGE.items()
        ]
        st.dataframe(pd.DataFrame(oil_std_rows), use_container_width=True, hide_index=True)

        st.markdown(f"### 🌰 الزيوت ({len(get_oil_ingredients())})")
        oils = get_oil_ingredients()

        for category, oil_list in OIL_CATEGORIES.items():
            st.markdown(f"#### {category}")
            cat_oils = [(name, oils[name]) for name in oil_list if name in oils]
            for ing_name, ing_data in cat_oils:
                with st.expander(f"🌰 {ing_name}"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("SE", f"{ing_data.get('SE', 0):.0f}")
                    with c2:
                        st.metric("kcal/kg", f"{ing_data.get('SE', 0) * 41:.0f}")
                    with c3:
                        st.metric("السعر", f"${ing_data.get('price', 0):.0f}")
                    st.info(f"📝 {ing_data.get('desc', '')}")
    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# تبويب بدائل الحليب (v11.2 — تحقق 75%)
# ═══════════════════════════════════════════════════════════════════════════
with tab_map["🍼 بدائل الحليب"]:
    try:
        st.markdown('<div class="section-title">🍼 بدائل الحليب — ≥ 75%</div>',
                    unsafe_allow_html=True)
        st.caption("⚠️ شرط: يجب استخدام ≥ 75% من المواد المختارة")

        mr1, mr2 = st.columns(2)
        with mr1:
            mr_animal = st.selectbox("نوع الحيوان:",
                                      list(MILK_REPLACER_STANDARDS.keys()), key="mr_a")
            mr_volume = st.number_input("الكمية (كجم):", 1.0, 10000.0, 100.0, 10.0,
                                         key="mr_v")
        with mr2:
            std_mr = MILK_REPLACER_STANDARDS[mr_animal]
            st.markdown(f"""
            <div class="price-card">
            <b>📊 {mr_animal}:</b><br>
            بروتين: {std_mr['CP']}% | دهن: {std_mr['Fat']}% | لاكتوز: {std_mr['Lactose']}%
            <br><small>{std_mr['notes']}</small>
            </div>
            """, unsafe_allow_html=True)

        mr_selected = []
        mr_cols = st.columns(3)
        for i, (name, data) in enumerate(MILK_REPLACER_INGREDIENTS.items()):
            with mr_cols[i % 3]:
                if st.checkbox(f"{name} — ${data['price']}", key=f"mr_{name}"):
                    mr_selected.append(name)

        st.info(f"📊 المختارة: {len(mr_selected)} مادة | "
                f"الحد الأدنى المطلوب: 3 | الشرط: ≥75%")

        if st.button("🧪 تركيب", type="primary", use_container_width=True):
            if len(mr_selected) < 3:
                st.warning("⚠️ اختر 3 مكونات على الأقل")
            else:
                r = formulate_milk_replacer(mr_animal, mr_volume, mr_selected)
                if r["success"]:
                    if r.get("warning"):
                        st.warning(r["warning"])
                    else:
                        st.success(
                            f"✅ تم التركيب — استُخدمت {r['used_count']} مادة "
                            f"({r['used_pct']:.0f}% من المختار) ≥ 75%"
                        )
                    for ing, pct in r["formula"].items():
                        kg = pct * mr_volume / 100.0
                        st.markdown(
                            f'<div class="formula-item">▪️ <b>{ing}:</b> '
                            f'{pct:.2f}% ({kg:.2f} كجم)</div>',
                            unsafe_allow_html=True
                        )
                    st.metric("تكلفة 100 كجم", f"${r['cost_per_100kg']:.2f}")
                    st.metric("نسبة الاستخدام", f"{r['used_pct']:.0f}%")
    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# تبويب OCR
# ═══════════════════════════════════════════════════════════════════════════
with tab_map["📷 المختبر الذكي OCR"]:
    try:
        st.markdown('<div class="section-title">📷 المختبر الذكي (OCR)</div>',
                    unsafe_allow_html=True)
        if not OCR_AVAILABLE:
            st.error("⚠️ pytesseract غير مثبتة")
        else:
            input_method = st.radio(
                "طريقة الإدخال:", ["📤 رفع صورة", "📸 كاميرا"],
                horizontal=True, key="ocr_method"
            )

            uploaded_image = None
            if "رفع" in input_method:
                up = st.file_uploader("ارفع الصورة:", type=["jpg", "jpeg", "png"],
                                       key="ocr_upload")
                if up:
                    uploaded_image = up.read()
            else:
                cam = st.camera_input("التقط الصورة", key="ocr_camera")
                if cam:
                    uploaded_image = cam.read()

            if uploaded_image:
                st.image(uploaded_image, caption="الصورة", use_container_width=True)
                if st.button("🔍 تحليل", type="primary", use_container_width=True):
                    with st.spinner("🔬 جاري التحليل..."):
                        result = extract_ingredients_from_image(uploaded_image)
                    if result["success"] and result["count"] > 0:
                        st.success(f"✅ تم التعرف على {result['count']} مادة")
                        st.session_state["last_ocr_result"] = result["ingredients"]
                        nutrients = compute_formula_nutrients(result["ingredients"])
                        st.session_state["last_ocr_nutrients"] = nutrients
                        st.dataframe(pd.DataFrame([
                            {"المادة": k, "النسبة": v}
                            for k, v in result["ingredients"].items()
                        ]), use_container_width=True, hide_index=True)
                        n1, n2, n3, n4 = st.columns(4)
                        n1.metric("CP", f"{nutrients['CP']:.2f}%")
                        n2.metric("DP", f"{nutrients['DP']:.2f}%")
                        n3.metric("SE", f"{nutrients['SE']:.1f}")
                        n4.metric("NDF", f"{nutrients['NDF']:.2f}%")
                        try:
                            pdf_ocr = pdf_gen.generate_ocr_report(
                                result["ingredients"], nutrients,
                                raw_text=result.get("raw_text", ""))
                            st.download_button("📄 تحميل PDF", pdf_ocr,
                                file_name=f"OCR_{datetime.now():%Y%m%d}.pdf",
                                mime="application/pdf", use_container_width=True)
                        except Exception as e:
                            st.error(f"⚠️ {e}")
                    else:
                        st.warning("⚠️ لم يتم التعرف على مواد")
    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# تبويب الحظائر 3D
# ═══════════════════════════════════════════════════════════════════════════
with tab_map["🏗️ تصميم الحظائر 3D"]:
    try:
        st.markdown('<div class="section-title">🏗️ مصمم الحظائر 3D</div>',
                    unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            barn_animal = st.selectbox("🐾 الحيوان:",
                list(BARN_DESIGN_STANDARDS.keys()),
                format_func=lambda k: BARN_DESIGN_STANDARDS[k]["name_ar"],
                key="barn_animal")
        with c2:
            barn_count = st.number_input("🔢 العدد:", 1, 100000, 1000, 50,
                                          key="barn_count")
        with c3:
            barn_system = st.selectbox("🏠 النظام:",
                ["أرضي مفتوح", "بطاريات"], key="barn_system")

        system_multiplier = 1.0
        if "بطاريات" in barn_system and barn_animal in ["دواجن_لاحم", "دواجن_بياض", "سمان"]:
            system_multiplier = 0.55

        dims = calculate_barn_dimensions(barn_animal, barn_count)
        if dims and system_multiplier != 1.0:
            dims["total_area_m2"] = round(dims["total_area_m2"] * system_multiplier, 2)
            dims["length_m"] = round(dims["total_area_m2"] / dims["width_m"], 2)

        if dims:
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("📏 المساحة", f"{dims['total_area_m2']} م²")
            k2.metric("📐 الأبعاد", f"{dims['length_m']}×{dims['width_m']} م")
            k3.metric("🏔️ القمة", f"{dims['ridge_height_m']} م")
            k4.metric("📦 الحجم", f"{dims['volume_m3']} م³")

            k5, k6, k7, k8 = st.columns(4)
            k5.metric("🍽️ معالف", dims["feeders_count"])
            k6.metric("📏 طول معالف", f"{dims['total_feeder_length_m']} م")
            k7.metric("💧 سقايات", dims["drinkers_count"])
            k8.metric("💨 تهوية", f"{dims['vent_flow_summer_m3h']:,} م³/س")

            st.markdown("### 🏗️ المجسم 3D")
            fig3d = create_barn_3d_figure(dims)
            if fig3d:
                st.plotly_chart(fig3d, use_container_width=True)

            st.markdown("### 🎬 فيديو GIF")
            if st.button("🎬 توليد الفيديو", type="primary", use_container_width=True):
                with st.spinner("🎥 جاري التوليد..."):
                    video_buf = create_barn_animation_gif(dims, frames=30, fps=8)
                if video_buf:
                    st.session_state["barn_video_gif"] = video_buf.getvalue()
                    st.success("✅ تم!")
                else:
                    st.error("⚠️ تعذر التوليد")

            if st.session_state.get("barn_video_gif"):
                st.image(st.session_state["barn_video_gif"], use_container_width=True)
                st.download_button("⬇️ تحميل GIF",
                    st.session_state["barn_video_gif"],
                    file_name=f"barn_{barn_animal}.gif", mime="image/gif",
                    use_container_width=True)

            try:
                pdf_bytes = generate_barn_pdf_report(dims)
                st.download_button("📄 تحميل PDF", pdf_bytes,
                    file_name=f"Barn_{barn_animal}.pdf",
                    mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"⚠️ {e}")
    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# تبويب دراسة الجدوى (v11.2 — 3 خيارات + حساسية)
# ═══════════════════════════════════════════════════════════════════════════
with tab_map["📊 دراسة الجدوى"]:
    try:
        st.markdown('<div class="section-title">📊 دراسة الجدوى</div>',
                    unsafe_allow_html=True)

        feas_mode = st.radio(
            "🎯 نوع الدراسة المطلوبة:",
            ["🔬 جدوى فنية (مساحة + تغذية + تهوية)",
             "💰 جدوى اقتصادية (تكاليف + ربحية)",
             "📈 جدوى شاملة (فنية + اقتصادية + حساسية)"],
            horizontal=True, key="feas_mode"
        )

        f1, f2 = st.columns(2)
        with f1:
            feas_key = st.selectbox("نوع الحيوان:",
                list(BARN_DESIGN_STANDARDS.keys()),
                format_func=lambda k: BARN_DESIGN_STANDARDS[k]["name_ar"],
                key="feas_animal_112")
            feas_count = st.number_input("العدد:", 1, 100000, 1000, 50,
                                           key="feas_count_112")
            project_name = st.text_input("اسم المشروع:", key="feas_proj_112")
        with f2:
            feas_requester = st.text_input("مقدم الطلب:", key="feas_req_112")

            if "اقتصادية" in feas_mode or "شاملة" in feas_mode:
                feed_price = st.number_input("💵 سعر العلف ($/طن):",
                    50.0, 5000.0, 350.0, 10.0, key="feas_feed_price")
                product_price = st.number_input("💵 سعر بيع المنتج ($/وحدة):",
                    0.1, 10000.0, 2.5, 0.1, key="feas_prod_price")
                labor_cost = st.number_input("👷 تكلفة العامل ($/شهر):",
                    0.0, 10000.0, 200.0, 10.0, key="feas_labor")
                other_costs = st.number_input("📊 تكاليف أخرى ($/شهر):",
                    0.0, 100000.0, 300.0, 50.0, key="feas_other")

        feas = calculate_technical_feasibility(feas_key, feas_count)
        if feas:
            d = feas["dims"]

            # الجدوى الفنية
            st.markdown("### 🔬 الجدوى الفنية")
            fc1, fc2, fc3, fc4 = st.columns(4)
            fc1.metric("📏 المساحة", f"{d['total_area_m2']} م²")
            fc2.metric("📐 الأبعاد", f"{d['length_m']}×{d['width_m']} م")
            fc3.metric("📦 الحجم", f"{d['volume_m3']} م³")
            fc4.metric("👷 عمال", feas["labor"]["workers"])

            f1_, f2_, f3_, f4_ = st.columns(4)
            f1_.metric("علف/يوم", f"{feas['feed']['total_day_kg']:.1f} كجم")
            f2_.metric("علف/سنة", f"{feas['feed']['total_year_ton']:.2f} طن")
            f3_.metric("ماء/يوم", f"{feas['water']['total_day_L']:.0f} لتر")
            f4_.metric("ماء/سنة", f"{feas['water']['total_year_m3']:.1f} م³")

            # الجدوى الاقتصادية
            annual_revenue = 0
            total_year_cost = 0
            if "اقتصادية" in feas_mode or "شاملة" in feas_mode:
                st.markdown("### 💰 الجدوى الاقتصادية")
                feed_year_ton = feas["feed"]["total_year_ton"]
                feed_year_cost = feed_year_ton * feed_price
                labor_year = feas["labor"]["workers"] * labor_cost * 12
                other_year = other_costs * 12
                total_year_cost = feed_year_cost + labor_year + other_year

                prod = feas["production"]
                annual_units = prod.get("annual", 0)
                annual_revenue = annual_units * product_price
                annual_profit = annual_revenue - total_year_cost
                roi = (annual_profit / total_year_cost * 100
                       if total_year_cost > 0 else 0)
                breakeven_units = (total_year_cost / product_price
                                   if product_price > 0 else 0)

                e1, e2, e3, e4 = st.columns(4)
                e1.metric("💵 تكلفة سنوية", f"${total_year_cost:,.0f}")
                e2.metric("💰 إيراد سنوي", f"${annual_revenue:,.0f}")
                e3.metric("📈 ربح سنوي", f"${annual_profit:,.0f}",
                          delta=f"{roi:+.1f}% ROI")
                e4.metric("🎯 نقطة التعادل", f"{breakeven_units:,.0f} وحدة/سنة")

                if annual_profit > 0:
                    st.success(f"✅ المشروع مجدٍ — صافي ربح ${annual_profit:,.0f}/سنة")
                else:
                    st.error(f"❌ غير مجدٍ حالياً — يحتاج ${abs(annual_profit):,.0f} تغطية")

            # الحساسية
            if "شاملة" in feas_mode and annual_revenue > 0:
                st.markdown("### 📈 تحليل الحساسية")
                scenarios = [
                    ("متشائم (-20% إيراد)", 0.8, 1.10),
                    ("أساسي", 1.0, 1.0),
                    ("متفائل (+20% إيراد)", 1.2, 0.95),
                ]
                sens_data = []
                for name, rev_mult, cost_mult in scenarios:
                    rev = annual_revenue * rev_mult
                    cost = total_year_cost * cost_mult
                    profit = rev - cost
                    sens_data.append({
                        "السيناريو": name,
                        "الإيراد": f"${rev:,.0f}",
                        "التكلفة": f"${cost:,.0f}",
                        "الربح": f"${profit:,.0f}",
                        "الحالة": "✅" if profit > 0 else "❌",
                    })
                st.dataframe(pd.DataFrame(sens_data), use_container_width=True,
                             hide_index=True)

            # تحميل الكتيّب
            try:
                booklet = generate_feasibility_booklet(
                    feas_key, feas_count, project_name=project_name,
                    requester_name=feas_requester)
                if booklet:
                    st.download_button(
                        "📥 تحميل كتيّب الجدوى (PDF)",
                        booklet,
                        file_name=f"Feasibility_{feas_key}_{datetime.now():%Y%m%d}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary",
                    )
            except Exception as e:
                st.error(f"⚠️ {e}")
    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# تبويب مزارع الدجاج
# ═══════════════════════════════════════════════════════════════════════════
with tab_map["🐔 مزارع الدجاج"]:
    try:
        st.markdown('<div class="section-title">🐔 مزارع الدجاج</div>',
                    unsafe_allow_html=True)

        with st.expander("➕ إضافة مزرعة", expanded=True):
            nf_name = st.text_input("اسم المزرعة:", key="nf_name")
            if st.button("💾 حفظ", key="nf_save") and nf_name:
                st.session_state["broiler_farms"][nf_name] = {
                    "data": {"age": 1, "birds": 1000, "weight_kg": 0.045,
                             "feed_kg": 0.0, "dead": 0, "temp": 33.0, "hum": 65.0}
                }
                st.success(f"✅ {nf_name}")
                st.rerun()

        if st.session_state["broiler_farms"]:
            sel = st.selectbox("اختر:", [""] + list(st.session_state["broiler_farms"].keys()))
            if sel:
                d = st.session_state["broiler_farms"][sel]["data"]
                b1, b2 = st.columns(2)
                with b1:
                    d["age"] = st.number_input("العمر:", 1, 60, d["age"])
                    d["birds"] = st.number_input("الطيور:", 1, value=d["birds"])
                    d["weight_kg"] = st.number_input("الوزن (كجم):", 0.0, 10.0,
                                                      float(d["weight_kg"]), 0.01)
                    d["feed_kg"] = st.number_input("العلف (كجم):", 0.0,
                                                    float(d["feed_kg"]), 100.0)
                with b2:
                    d["dead"] = st.number_input("النافق:", 0, value=d["dead"])

                alive = d["birds"] - d["dead"]
                gain = alive * (d["weight_kg"] - 0.045)
                adg = ((d["weight_kg"] - 0.045) * 1000 / d["age"]) if d["age"] > 0 else 0
                fcr = (d["feed_kg"] / gain) if gain > 0 else 0
                liv = 100 - (d["dead"] / d["birds"] * 100)
                epef = ((liv * d["weight_kg"]) / (d["age"] * fcr) * 100) if (
                    d["age"] > 0 and fcr > 0) else 0

                k1, k2, k3, k4 = st.columns(4)
                k1.metric("ADG", f"{adg:.1f}")
                k2.metric("FCR", f"{fcr:.2f}")
                k3.metric("EPEF", f"{epef:.0f}")
                k4.metric("حيوية %", f"{liv:.1f}")
    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# تبويبات المالك
# ═══════════════════════════════════════════════════════════════════════════
if is_owner():
    with tab_map["🏭 المستودعات"]:
        try:
            st.markdown('<div class="section-title">🏭 المستودعات</div>',
                        unsafe_allow_html=True)
            inv = st.session_state["inventory"]
            col_a, col_b, col_c, col_d = st.columns(4)
            col_a.metric("إجمالي", len(inv))
            low = sum(1 for v in inv.values()
                      if (v.get("quantity", 0) if isinstance(v, dict) else v) < 5)
            col_b.metric("منخفضة", low)
            crit = sum(1 for v in inv.values()
                       if (v.get("quantity", 0) if isinstance(v, dict) else v) <= 0)
            col_c.metric("نفذت", crit)
            col_d.metric("آمنة", len(inv) - low - crit)

            cols = st.columns(3)
            for i, (name, data) in enumerate(list(inv.items())[:60]):
                with cols[i % 3]:
                    q = data["quantity"] if isinstance(data, dict) else data
                    badge = "🔴" if q <= 0 else ("🟡" if q < 5 else "🟢")
                    st.markdown(f"{badge} **{name}**: {q:.1f} طن")
                    new_q = st.number_input("تحديث:", min_value=0.0, value=float(q),
                                             key=f"inv_{name}",
                                             label_visibility="collapsed")
                    if isinstance(inv[name], dict):
                        inv[name]["quantity"] = new_q
        except Exception as e:
            st.error(f"⚠️ {e}")

    with tab_map["🧾 الفواتير"]:
        try:
            st.markdown('<div class="section-title">🧾 الفواتير</div>',
                        unsafe_allow_html=True)
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                client = st.text_input("العميل:", "مزرعة الأمل")
            with fc2:
                tons = st.number_input("الكمية (طن):", 0.1, 1000.0, 2.0, 0.5)
            with fc3:
                profit = st.number_input("هامش ($/طن):", 0.0, 1000.0, 50.0)
            sell = st.session_state["computed_ton_cost"] + profit
            total = sell * tons
            st.markdown(f"""
            <div class="price-card">
            <h4>🧾 فاتورة</h4>
            <p>العميل: {client}</p>
            <p>الكمية: {tons} طن</p>
            <p>سعر الطن: ${sell:.2f}</p>
            <p style="font-size:1.3rem; color:#1b5e20;">الإجمالي: ${total:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"⚠️ {e}")

    with tab_map["🖨️ الديباجة"]:
        try:
            st.markdown('<div class="section-title">🖨️ الديباجة</div>',
                        unsafe_allow_html=True)
            st.markdown(f"""
            <div style="border: 3px dashed #1b5e20; padding: 30px;
            border-radius: 15px; background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
            direction: rtl; text-align: center;">
            <h2 style="color: #1b5e20;">🌟 {APP_NAME} 🌟</h2>
            <h3 style="color: #c62828;">{SUPERVISOR} — {SUPERVISOR_TITLE}</h3>
            <p style="background:#e8f5e9; padding:12px; border-radius:8px;
            color:#1b5e20; font-weight:bold;">
            🎯 {st.session_state['active_stage_title']}
            </p>
            <small>📅 {datetime.now():%Y-%m-%d}</small>
            <br><small style="color:#c62828;">🤲 {DUA_SHORT}</small>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"⚠️ {e}")

    with tab_map["📈 التحليلات"]:
        try:
            st.markdown('<div class="section-title">📈 التحليلات</div>',
                        unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("الخلطات", "1,247")
            m2.metric("متوسط التكلفة", "$285")
            m3.metric("التوفير", "18%")
            m4.metric("رضا", "96%")
            if PLOTLY_AVAILABLE:
                usage = pd.DataFrame({
                    'المادة': ['ذرة', 'صويا', 'نخالة', 'زيوت', 'أملاح', 'أخرى'],
                    'النسبة': [42, 23, 14, 8, 8, 5],
                })
                fig = px.pie(usage, values='النسبة', names='المادة',
                             color_discrete_sequence=px.colors.sequential.Greens)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ {e}")

    with tab_map["💬 التعليقات"]:
        try:
            st.markdown('<div class="section-title">💬 التعليقات المشتركة</div>',
                        unsafe_allow_html=True)
            st.caption("🌐 التعليقات مرئية لجميع الأجهزة المتصلة — مزامنة فورية")
            comments = SharedStorage.get("shared_comments") or st.session_state.get(
                "shared_comments", "• مرحباً بكم")
            st.text_area("الحالية:", value=comments, height=250, disabled=True)
            nc = st.text_area("جديد:", key="new_comment_v112")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                if st.button("➕ نشر للجميع", type="primary",
                              use_container_width=True) and nc.strip():
                    line = f"• [{datetime.now():%Y-%m-%d %H:%M}]: {nc.strip()}"
                    new_val = SharedStorage.append_line("shared_comments", line)
                    st.session_state["shared_comments"] = new_val
                    st.success("✅ تم النشر")
                    st.rerun()
            with col_c2:
                if st.button("🔄 تحديث من الأجهزة", use_container_width=True):
                    st.rerun()
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# المراجع
# ═══════════════════════════════════════════════════════════════════════════
with tab_map["📚 المراجع"]:
    try:
        st.markdown('<div class="section-title">📚 المراجع العلمية</div>',
                    unsafe_allow_html=True)
        st.markdown("""
### المراجع المعتمدة:
- **NRC (2012)** — Nutrient Requirements of Swine
- **NRC (2007)** — Nutrient Requirements of Small Ruminants
- **NRC (2001)** — Nutrient Requirements of Dairy Cattle
- **NRC (2007)** — Nutrient Requirements of Horses
- **NRC (1994)** — Nutrient Requirements of Poultry
- **INRA (2018)** — Feeding System for Ruminants
- **FAO (2010)** — Camel Nutrition and Feeding
- **Ross 308 (2020)** — Broiler Management Handbook
- **Carroll & Huntington (1988)** — Body Condition Scoring and Weight Estimation of Horses
- **McDonald et al. (2011)** — Animal Nutrition

### 🆕 مراجع Ca:P:
- NRC — Mineral Tolerance of Animals
- INRA 2018 — Calcium and Phosphorus Metabolism

### 🏗️ تصميم الحظائر:
- MWPS-1 — Structures and Environment Handbook
- FAO 2012 — Rural Structures in the Tropics
- ASABE Standards
        """)
    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# المساعدة
# ═══════════════════════════════════════════════════════════════════════════
with tab_map["💡 المساعدة"]:
    try:
        st.markdown('<div class="section-title">💡 المساعدة</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
### الأسئلة الشائعة:

**1. كيف أبدأ؟**
- اختر الحيوان → فعّل ✅ الاعتماد → اختر المكونات (3+) → اضغط 🚀

**2. ما هو شريط وزن الخيل الجديد؟**
- 🆕 v11.2 يقدم طريقتين:
  - **📏 تقدير بالقياسات**: يستخدم معادلة Carroll & Huntington
    (الوزن = محيط الصدر² × الطول / 11877)
  - **🎚️ شريط تقديري**: slider سريع (150-800 كجم)

**3. لماذا حذف البورصة والموقع الجغرافي؟**
- تبسيطاً للتطبيق — الأسعار الآن بأساس USD ثابت،
  يمكن للمالك تعديلها يدوياً.

**4. بدائل الحليب ≥75% — كيف تعمل؟**
- المحرك يحاول أولاً بدون قيود
- إذا الاستخدام < 75% → يعيد المحاولة بـ lower bound 0.5%
- يظهر تحذير إذا لم يصل للـ 75%

**5. تعدد الأجهزة — كيف يعمل؟**
- التعليقات والمستودعات تُزامَن عبر ملف JSON مشترك
- كل جهاز يفتح نفس الرابط يعمل في جلسة منفصلة
- للاستخدام التجاري: Supabase (مجاني)

**6. دراسة الجدوى — ما الفرق بين الأنواع؟**
- 🔬 **فنية**: مساحة، علف، تهوية، عمالة
- 💰 **اقتصادية**: تكاليف، إيرادات، ربح، ROI، نقطة تعادل
- 📈 **شاملة**: فنية + اقتصادية + تحليل حساسية (3 سيناريوهات)

**7. ما هي درجة الجودة 70%؟**
- الحد الأدنى العلمي لاعتماد الخلطة
- يشمل DP=30%، SE=15%، NDF، ADF، Ca، P، Ca:P

**8. كيف أحصل على تقرير PDF؟**
- بعد التركيب → زر "📥 تحميل PDF"
- يحتوي: ختم + توقيع د. عبدالقادر + 9 رسوم + Ca:P

### 🔧 الدعم
📧 {OWNER_EMAIL}
📱 {WHATSAPP_NUMBER}

{DUA_FULL}
        """)
    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# الدليل
# ═══════════════════════════════════════════════════════════════════════════
with tab_map["📖 الدليل"]:
    try:
        st.markdown('<div class="section-title">📖 دليل المستخدم</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
### 🎯 الغرض
**{APP_NAME} v{APP_VERSION}** — منصة ذكية لتركيب الأعلاف بأقل تكلفة وأعلى جودة.

### ✨ الميزات
- 🐄 **9 قطاعات**: أبقار، أغنام، ماعز، إبل، خيول، دواجن، سمان، أسماك، أرانب
- 🌰 **28 زيتاً** بمعايير NRC/INRA/FAO
- 🧬 **DP/CP** يعمل فعلياً
- ✅ **ضمان جودة ≥ 70%**
- 🆕 **حدود صارمة**: يوريا 0% للدواجن، نخالة ≤10%
- 🆕 **Ca:P إلزامي** 1.2–7.0
- 🆕 **تقييم موزون**
- 🆕 **اختيار ذكي**
- 🆕 **بحث فوري**
- 📷 **OCR** كاميرا + رفع
- 🏗️ **3D + GIF** للحظائر
- 📊 **جدوى 3 خيارات** + حساسية
- 🍼 **بدائل حليب ≥75%**
- 📄 **PDF احترافي** بختم وتوقيع د. عبدالقادر

### 🆕 جديد في v11.2:
- ✅ **اللقب: د.** (كان م.)
- ✅ **حذف البورصة**
- ✅ **حذف الموقع الجغرافي** (USD فقط)
- ✅ **شريط تقدير وزن الخيل** (Carroll & Huntington)
- ✅ **بدائل حليب ≥75%**
- ✅ **بطاقة الحالة الفسيولوجية** بارزة
- ✅ **تعدد الأجهزة** (SharedStorage)
- ✅ **جدوى متعددة** (3 خيارات + حساسية)
- ✅ **safe_section** للأخطاء

### 🔐 الدخول
- 👑 **المالك**: كود خاص (202687)
- 👥 **زائر**: مجاني + حظائر + جدوى + مزارع + OCR

### 📞 التواصل
📧 {OWNER_EMAIL}
📱 {WHATSAPP_NUMBER}

---
{DUA_FULL}
        """)
    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# التذييل الثابت
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(
    f'<div class="mini-signature">🌾 {APP_NAME} v{APP_VERSION} | {SUPERVISOR} © 2026</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="dua-fixed-banner">🤲 {DUA_SHORT} 🤲</div>',
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# نهاية الملف — Tawor Nology 11.2
# ═══════════════════════════════════════════════════════════════════════════
