# ============================================================================
# تاور نولجي TAWOR NOLOGY 10.3 — النسخة الكاملة (نسخة واحدة)
# إشراف: م. عبدالقادر إسماعيل تاور
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
# ============================================================================
import streamlit as st
import numpy as np
import pandas as pd
import io, os, re, base64, tempfile, traceback, warnings, json
import urllib.parse, urllib.request
from datetime import datetime
from functools import lru_cache
from dataclasses import dataclass

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════
# استيرادات محمية
# ═══════════════════════════════════════════════════════════════════════
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
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY
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


# ═══════════════════════════════════════════════════════════════════════
# النصوص الثابتة
# ═══════════════════════════════════════════════════════════════════════
DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي ابتسام"
DUA_FULL = "رحم الله والدي إسماعيل تاور وأختي ابتسام وأسكنهما فسيح جناته وجعل قبرهما روضة من رياض الجنة"
DUA_QURAN = "﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾"
DUA_VERSE = "﴿ وَقُل رَّبِّ ارْحَمْهُمَا كَمَا رَبَّيَانِي صَغِيرًا ﴾"
DUA_VISITOR = """🕌 <b>إلى زوارنا الكرام:</b><br>
هذه المنصة صدقةٌ جارية عن <b>والدي إسماعيل تاور</b> و<b>أختي ابتسام</b>.<br>
نسألكم بظهر الغيب أن تشاركونا الدعاء لهما. 🤲"""

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

# ═══════════════════════════════════════════════════════════════════════
# إدارة الخطوط العربية
# ═══════════════════════════════════════════════════════════════════════
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
    @lru_cache(maxsize=5000)
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


# ═══════════════════════════════════════════════════════════════════════
# مكتبة الأعلاف الشاملة (18 زيتاً + كل المكونات)
# ═══════════════════════════════════════════════════════════════════════
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
        "زيت ذرة": {"CP": 0.0, "DC": 0.0, "SE": 220.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "طاقة عالية 9000 kcal/kg، غني بأوميغا 6", "source": "NRC 2012", "max_poultry": 6.0, "max_ruminant": 5.0},
        "زيت فول الصويا": {"CP": 0.0, "DC": 0.0, "SE": 215.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "أشهر زيوت الأعلاف، متوازن 8800 kcal/kg", "source": "Ross 308 / NRC 2012", "max_poultry": 8.0, "max_ruminant": 5.0},
        "زيت عباد الشمس": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "غني بأوميغا 6، رخيص نسبياً", "source": "NRC 2007", "max_poultry": 6.0, "max_ruminant": 4.0},
        "زيت بذرة القطن": {"CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "يحتوي جوسيبول (يجب معادلة)", "source": "NRC 2012", "max_poultry": 3.0, "max_ruminant": 5.0},
        "زيت الكتان": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "غني جداً بأوميغا 3، ممتاز للخيول", "source": "NRC 2007 Horses", "max_poultry": 3.0, "max_ruminant": 3.0},
        "زيت جوز الهند": {"CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "دهون متوسطة السلسلة MCT، مضاد بكتيري", "source": "NRC 2012", "max_poultry": 5.0, "max_ruminant": 3.0},
        "زيت النخيل": {"CP": 0.0, "DC": 0.0, "SE": 215.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "طاقة عالية، مقاوم للأكسدة، 8700 kcal/kg", "source": "NRC 2012", "max_poultry": 6.0, "max_ruminant": 5.0},
        "زيت الكانولا": {"CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "متوازن أوميغا 3 و6", "source": "NRC 2012", "max_poultry": 5.0, "max_ruminant": 5.0},
        "زيت السمسم": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "غني بمضادات الأكسدة الطبيعية", "source": "NRC 2007", "max_poultry": 4.0, "max_ruminant": 3.0},
        "زيت الزيتون": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "غني بأوميغا 9، مضاد أكسدة قوي", "source": "INRA 2018", "max_poultry": 4.0, "max_ruminant": 4.0},
        "زيت الأفوكادو": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "غني بفيتامين E", "source": "NRC 2012", "max_poultry": 3.0, "max_ruminant": 3.0},
        "زيت القرطم": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "غني جداً بأوميغا 6 (75%)", "source": "NRC 2012", "max_poultry": 4.0, "max_ruminant": 3.0},
        "زيت الفول السوداني": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "طاقة عالية جداً، 8900 kcal/kg", "source": "NRC 2012", "max_poultry": 5.0, "max_ruminant": 4.0},
        "شحم حيواني (Tallow)": {"CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "طاقة عالية (9500 kcal/kg)", "source": "NRC 2012", "max_poultry": 6.0, "max_ruminant": 5.0},
        "سمن حيواني (Lard)": {"CP": 0.0, "DC": 0.0, "SE": 225.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "شحم الخنزير، يجب تجنبه للحيوانات الحلال", "source": "NRC 2012", "max_poultry": 5.0, "max_ruminant": 0.0},
        "دهن الدجاج": {"CP": 0.0, "DC": 0.0, "SE": 225.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "شحم الدواجن المعاد تدويره، اقتصادي", "source": "NRC 2012", "max_poultry": 6.0, "max_ruminant": 0.0},
        "زيت السمك (Fish Oil)": {"CP": 0.0, "DC": 0.0, "SE": 235.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "غني بأوميغا 3 EPA/DHA، ممتاز للأسماك", "source": "NRC Fish Nutrition", "max_poultry": 2.0, "max_ruminant": 2.0},
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
        "كولين كلوريد": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0},
    },
}

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
    "زيوت نباتية متوازنة": ["زيت النخيل", "زيت جوز الهند", "زيت الزيتون", "زيت السمسم", "زيت الفول السوداني", "زيت الأفوكادو"],
    "دهون حيوانية": ["شحم حيواني (Tallow)", "سمن حيواني (Lard)", "دهن الدجاج"],
}


def get_oil_standard(standard_key: str) -> dict:
    return MAX_OIL_PERCENTAGE.get(standard_key, {"max": 5.0, "optimal": 3.0, "source": "معيار عام"})


def get_oil_ingredients() -> dict:
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت النباتية والحيوانية", {})


# ═══════════════════════════════════════════════════════════════════════
# الاحتياجات الغذائية
# ═══════════════════════════════════════════════════════════════════════
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
            return AnimalRequirement(9.5, 12.0, 59.0, 33.0, 21.0, 3.6, 8.0, 0.55, 0.32, "تسمين حملان عادي", "ADG ~180 جم")
        else:
            return AnimalRequirement(8.5, 11.0, 55.0, 38.0, 24.0, 3.2, 8.5, 0.50, 0.30, "حملان تيد", "تسمين نهائي")
    else:
        if production_type == "مرضعات":
            dp = 10.5 + (litter_size - 1) * 1.5
            cp = dp / 0.72
            return AnimalRequirement(round(dp, 2), round(cp, 2), round(60 + (litter_size - 1) * 5, 1),
                                     30.0, 19.0, 4.5, 8.5, round(0.65 + (litter_size - 1) * 0.10, 3),
                                     round(0.38 + (litter_size - 1) * 0.05, 3), f"نعاج مرضعات ({litter_size})", "إنتاج حليب")
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


def requirement_to_standard(req):
    return {"CP": req.CP, "DP": req.DP, "SE": req.SE, "NDF": req.NDF, "ADF": req.ADF,
            "EE": req.EE, "ASH": req.ASH, "Ca": req.Ca, "P": req.P}


# ═══════════════════════════════════════════════════════════════════════
# الحسابات
# ═══════════════════════════════════════════════════════════════════════
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


def auto_formulate_smart(available_ingredients, prices, custom_standard,
                          standard_key="", tolerance=0.3, max_iterations=50, basis="DP"):
    """⚠️ المفتاح: اسم المعامل standard_key (كان std_key في نسخة سابقة)"""
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "SCIPY غير متوفرة"}

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

    target_key = "DP" if basis == "DP" else "CP"
    protein_row = rows[target_key]
    targets = {k: custom_standard.get(k, 0) for k in ["DP", "SE", "NDF", "ADF", "Ca", "P", "CP"]}
    target_protein_value = targets[target_key]

    oil_std = get_oil_standard(standard_key)
    oil_max = oil_std["max"]

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

    try:
        A_eq = [[1.0] * n, protein_row]
        b_eq = [100.0, target_protein_value * 100.0]
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
    except Exception as e:
        return {"success": False, "message": f"خطأ: {e}"}

    if not res.success:
        return {"success": False, "message": "تعذر إيجاد حل — أضف مكونات متنوعة"}

    best = None
    best_score = float('inf')
    cur_target = target_protein_value
    cur_se = targets["SE"]
    cur_ndf = targets["NDF"]
    cur_adf = targets["ADF"]
    log = []

    for iteration in range(max_iterations):
        try:
            A_eq = [[1.0] * n, protein_row, rows["Ca"], rows["P"]]
            b_eq = [100.0, cur_target * 100.0, targets["Ca"] * 100.0, targets["P"] * 100.0]
            A_ub = [[-1.0 * x for x in rows["SE"]],
                    [1.0 * x for x in rows["NDF"]],
                    [1.0 * x for x in rows["ADF"]]]
            b_ub = [-1.0 * cur_se * 100.0,
                    cur_ndf * 1.10 * 100.0,
                    cur_adf * 1.10 * 100.0]
            if has_oils:
                A_ub.append(oil_indicator)
                b_ub.append(oil_max * 100.0)
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method='highs',
                          options={'presolve': True, 'time_limit': 15})
        except Exception:
            res = None

        if res is None or not res.success:
            try:
                A_eq = [[1.0] * n, protein_row, rows["Ca"]]
                b_eq = [100.0, cur_target * 100.0, targets["Ca"] * 100.0]
                A_ub_s = [[-1.0 * x for x in rows["SE"]]]
                b_ub_s = [-1.0 * cur_se * 100.0]
                if has_oils:
                    A_ub_s.append(oil_indicator)
                    b_ub_s.append(oil_max * 100.0)
                res = linprog(c, A_ub=A_ub_s, b_ub=b_ub_s, A_eq=A_eq, b_eq=b_eq,
                              bounds=bounds, method='highs')
            except Exception:
                res = None

        if res is None or not res.success:
            cur_ndf *= 1.05
            cur_adf *= 1.05
            log.append(f"تكرار {iteration + 1}: تخفيف")
            continue

        formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
        actual = compute_formula_nutrients(formula)
        total_oil_actual = compute_total_oil_percentage(formula)

        errors = {}
        for k in ["DP", "CP", "SE", "NDF", "ADF", "Ca", "P"]:
            tv = targets.get(k, 0)
            if tv > 0:
                errors[k] = abs(actual.get(k, 0) - tv) / tv

        weights = {"DP": 5.0, "CP": 5.0, "SE": 3.0, "NDF": 1.5, "ADF": 1.0, "Ca": 1.0, "P": 1.0}
        score = sum(errors.get(k, 0) * weights.get(k, 0) for k in errors)

        if score < best_score:
            best_score = score
            best = {
                "success": True, "formula": formula, "cost": res.fun / 100.0,
                "actual_nutrients": actual,
                "dp_error": abs(actual["DP"] - targets["DP"]),
                "cp_error": abs(actual["CP"] - targets.get("CP", 0)),
                "se_error": abs(actual["SE"] - targets["SE"]),
                "ndf_error": abs(actual["NDF"] - targets["NDF"]),
                "adf_error": abs(actual["ADF"] - targets["ADF"]),
                "ca_error": abs(actual.get("Ca", 0) - targets["Ca"]),
                "p_error": abs(actual.get("P", 0) - targets["P"]),
                "total_oil": total_oil_actual, "oil_std": oil_std,
                "iterations": iteration + 1, "log": log[-10:],
                "targets": targets, "basis": basis,
                "target_protein_value": target_protein_value
            }

        tgt_err = errors.get(target_key, 1) * 100
        if (tgt_err <= tolerance and
            errors.get("SE", 1) * 100 <= tolerance * 2 and
            errors.get("NDF", 1) * 100 <= tolerance * 5 and
            errors.get("Ca", 1) * 100 <= tolerance * 15):
            best["perfect_match"] = True
            break

        actual_protein = actual.get(target_key, 0)
        cur_target += (target_protein_value - actual_protein) * 0.25
        cur_se += (targets["SE"] - actual["SE"]) * 0.20
        cur_ndf += (targets["NDF"] - actual["NDF"]) * 0.15
        cur_adf += (targets["ADF"] - actual["ADF"]) * 0.15
        cur_target = max(5.0, min(45.0, cur_target))
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
    # ═══════════════════════════════════════════════════════════════════════
# الرسوم البيانية الملونة
# ═══════════════════════════════════════════════════════════════════════
def create_colorful_bar_chart(standard, actual):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        nutrients = [n for n in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH"] if n in standard]
        if not nutrients:
            return None
        std_vals = [standard[n] for n in nutrients]
        act_vals = [actual.get(n, 0) for n in nutrients]
        fig, ax = plt.subplots(figsize=(9, 4.5))
        x = np.arange(len(nutrients))
        width = 0.35
        bars1 = ax.bar(x - width/2, std_vals, width, label='المعيار القياسي',
                        color='#1976d2', edgecolor='#0d47a1', linewidth=1.5)
        bars2 = ax.bar(x + width/2, act_vals, width, label='القيمة المحسوبة',
                        color='#43a047', edgecolor='#1b5e20', linewidth=1.5)
        for bar in bars1:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h, f'{h:.1f}', ha='center',
                    va='bottom', fontsize=9, color='#0d47a1', fontweight='bold')
        for bar in bars2:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h, f'{h:.1f}', ha='center',
                    va='bottom', fontsize=9, color='#1b5e20', fontweight='bold')
        ax.set_xlabel('العنصر الغذائي', fontsize=11, fontweight='bold')
        ax.set_ylabel('القيمة', fontsize=11, fontweight='bold')
        ax.set_title('مقارنة العناصر الغذائية', fontsize=13, fontweight='bold', color='#1b5e20')
        ax.set_xticks(x)
        ax.set_xticklabels(nutrients, fontsize=10)
        ax.legend(loc='upper right', fontsize=10)
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
                  '#43a047', '#7cb342', '#fdd835', '#fb8c00', '#6d4c41',
                  '#c62828', '#6a1b9a']
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
        std_norm = [100.0 for _ in nutrients]
        act_norm = [(actual.get(n, 0) / standard[n]) * 100 for n in nutrients]
        angles = np.linspace(0, 2 * np.pi, len(nutrients), endpoint=False).tolist()
        std_norm += std_norm[:1]
        act_norm += act_norm[:1]
        angles += angles[:1]
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, std_norm, 'o-', linewidth=2.5, color='#1976d2', label='المعيار (100%)')
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
        ax.set_facecolor('white')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════
# PDF Generator — الختم والتوقيع على كل صفحة
# ═══════════════════════════════════════════════════════════════════════
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

    def _draw_page(self, canvas_obj, doc):
        """الهيدر + الفوتر + الختم الرسمي — على كل صفحة"""
        try:
            canvas_obj.saveState()
            w, h = doc.pagesize

            # خلفية مائية
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

            # الهيدر
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

            # الفوتر
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

            # QR
            try:
                qr = qrcode.QRCode(version=1, box_size=3, border=1)
                qr.add_data(PLATFORM_URL)
                qr.make(fit=True)
                qi = qr.make_image(fill_color="#1b5e20", back_color="white")
                qbuf = io.BytesIO()
                qi.save(qbuf, format="PNG")
                qbuf.seek(0)
                canvas_obj.drawImage(RLImage(qbuf), w / 2 - 20, 46, width=40, height=40)
            except Exception:
                pass

            # ═══ 🎯 الختم الرسمي والتوقيع (على كل صفحة) ═══
            try:
                sx, sy = w - 105, 145
                canvas_obj.setStrokeColor(HexColor('#c62828'))
                # 3 دوائر متراكزة
                canvas_obj.setLineWidth(3.5)
                canvas_obj.circle(sx, sy, 72, stroke=1, fill=0)
                canvas_obj.setLineWidth(2.0)
                canvas_obj.circle(sx, sy, 64, stroke=1, fill=0)
                canvas_obj.setLineWidth(0.8)
                canvas_obj.circle(sx, sy, 58, stroke=1, fill=0)
                # 4 خطوط زخرفية
                canvas_obj.setLineWidth(1.8)
                for ang_deg in [-45, 45, 135, 225]:
                    rad = np.radians(ang_deg)
                    x1 = sx + 58 * np.cos(rad)
                    y1 = sy + 58 * np.sin(rad)
                    x2 = sx + 72 * np.cos(rad)
                    y2 = sy + 72 * np.sin(rad)
                    canvas_obj.line(x1, y1, x2, y2)
                # النصوص
                canvas_obj.setFillColor(HexColor('#c62828'))
                canvas_obj.setFont(self.font_name, 9.5)
                canvas_obj.drawCentredString(sx, sy + 42, self._ar("تاور نولجي"))
                canvas_obj.drawCentredString(sx, sy + 30, self._ar("Tawor Nology"))
                canvas_obj.setFont(self.font_name, 8)
                canvas_obj.drawCentredString(sx, sy + 16, self._ar("م. عبدالقادر"))
                canvas_obj.drawCentredString(sx, sy + 4, self._ar("إسماعيل تاور"))
                canvas_obj.setFont(self.font_name, 6.5)
                canvas_obj.drawCentredString(sx, sy - 12, self._ar("اختصاصي تغذية الحيوان"))
                canvas_obj.drawCentredString(sx, sy - 24, self._ar("معتمد رسمياً"))
                canvas_obj.drawCentredString(sx, sy - 36, self._ar("© 2026"))
            except Exception:
                pass

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
            ev = evaluate_difference(pct, standard_value=sv)
            unit = "%" if k in ("CP", "DP", "NDF", "ADF", "EE", "ASH", "Ca", "P") else ""
            data.append([
                self._ar(labels.get(k, k)),
                f"{sv:.2f}{unit}",
                f"{cv:.2f}{unit}",
                f"{diff:+.3f}",
                f"{pct:+.2f}%",
                self._ar(ev["label"])
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
        header = [self._ar("الزيت"), self._ar("النسبة %"), self._ar("kcal/kg تقديري")]
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
            ('TEXTCOLOR', (0, -1), (-1, -1), HexColor('#bf360c')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]
        t = Table(data, colWidths=[250, 100, 135])
        t.setStyle(TableStyle(cmds))
        return (t, total_oil, oil_std)

    def generate_report(self, formula, requirement, animal_type, breed, cost,
                        city, local_cost, local_sym, requester_name="",
                        protein_basis="DP", standard_key="", include_charts=True):
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
            [self._ar("🧬 أساس الحساب:"), self._ar("البروتين المهضوم DP" if protein_basis == "DP" else "البروتين الخام CP")],
            [self._ar("📅 تاريخ الإصدار:"), datetime.now().strftime('%Y-%m-%d | %H:%M')],
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
            scores.append({"score": evaluate_difference(pct, standard_value=sv)["score"]})
        overall = get_overall_rating(scores)

        story.append(P("📊 جدول مقارنة العناصر الغذائية", size=14,
                       align=TA_RIGHT, color='#1b5e20'))
        story.append(Spacer(1, 8))
        story.append(self._comparison_table(standard_vals, calculated_vals))
        story.append(Spacer(1, 12))

        summary_data = [
            [self._ar("التقييم العام"), self._ar("عدد المطابقة"), self._ar("المتوسط")],
            [self._ar(overall["label"]),
             f"{sum(1 for s in scores if s['score'] >= 85)}/{len(scores)}",
             f"{overall['score']:.0f}%"]
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

        # الزيوت
        oil_tbl, total_oil, oil_std = self._oil_table(formula, standard_key)
        story.append(P("🌰 جدول الزيوت النباتية والحيوانية", size=14,
                       align=TA_RIGHT, color='#e65100'))
        story.append(Spacer(1, 8))
        if oil_tbl is None:
            story.append(P("ℹ️ لم تُستخدم أي زيوت في هذه الخلطة.",
                           size=11, align=TA_RIGHT, color='#666'))
        else:
            story.append(oil_tbl)
            story.append(Spacer(1, 8))
        oil_note = (f"الحد الأقصى: {oil_std['max']}% | "
                    f"المثالي: {oil_std['optimal']}% | "
                    f"المرجع: {oil_std['source']}")
        if total_oil > oil_std['max']:
            oil_note = f"⚠️ تجاوز الحد الأقصى! {oil_note}"
        elif total_oil > oil_std['optimal'] * 1.2:
            oil_note = f"⚡ مرتفع قليلاً — {oil_note}"
        else:
            oil_note = f"✅ مطابق — {oil_note}"
        story.append(P(oil_note, size=10, align=TA_RIGHT, color='#bf360c'))
        story.append(Spacer(1, 15))

        # الرسوم البيانية
        if include_charts:
            story.append(P("📈 الرسوم البيانية التحليلية", size=14,
                           align=TA_RIGHT, color='#1b5e20'))
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
                    rt.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
                    story.append(rt)
                    story.append(Spacer(1, 12))
                except Exception:
                    pass
            gauge = create_gauge_chart(overall["score"])
            if gauge:
                try:
                    story.append(P("🎯 مؤشر التقييم", size=12, align=TA_CENTER, color='#1b5e20'))
                    story.append(RLImage(gauge, width=200, height=200))
                    story.append(Spacer(1, 12))
                except Exception:
                    pass

        story.append(PageBreak())

        # التكاليف
        story.append(P("💰 التكاليف", size=14, align=TA_RIGHT, color='#1b5e20'))
        story.append(Spacer(1, 8))
        cost_data = [
            [self._ar("البند"), self._ar("القيمة")],
            [self._ar("التكلفة للطن (دولار)"), f"${cost:.2f}"],
            [self._ar(f"التكلفة ({local_sym})"), f"{local_cost:,.2f}"],
            [self._ar("البروتين المستهدف"),
             f"{requirement.DP if protein_basis == 'DP' else requirement.CP:.2f}%"],
            [self._ar("الدهن EE"), f"{calculated_vals.get('EE', 0):.2f}%"],
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

        # المكونات
        if formula:
            story.append(P("🌾 المكونات للطن", size=14, align=TA_RIGHT, color='#1b5e20'))
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
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(ti)
            story.append(Spacer(1, 25))

            # التوقيع
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
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BOX', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f5e9')),
            ]))
            story.append(ts)

        doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()


pdf_gen = PDFGenerator()


# ═══════════════════════════════════════════════════════════════════════
# Excel Export
# ═══════════════════════════════════════════════════════════════════════
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
    rt = Alignment(horizontal='right', vertical='center', wrap_text=True)
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
    labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم", "SE": "معادل النشاء",
              "NDF": "NDF", "ADF": "ADF", "EE": "دهن", "ASH": "رماد",
              "Ca": "كالسيوم", "P": "فسفور"}
    row = 7
    for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
        if k not in standard:
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


# ═══════════════════════════════════════════════════════════════════════
# الأسعار والصور
# ═══════════════════════════════════════════════════════════════════════
EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "ليبيا": {"rate": 4.80, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"},
    "السعودية": {"rate": 3.75, "sym": "SAR"},
    "الإمارات": {"rate": 3.67, "sym": "AED"},
    "باقي دول العالم": {"rate": 1.0, "sym": "USD"},
}


def get_market_prices(country, city="", state=""):
    base = {ing: 280.0 for cat in BIG_FEEDS_LIBRARY.values() for ing in cat}
    base.update({
        "ذرة صفراء": 230, "ذرة بيضاء": 225, "شعير مطحون": 210,
        "سورجم (فتريتة)": 195, "قمح محلي": 240, "أمباز الفول السوداني": 460,
        "كسب فول صويا 44%": 440, "كسب فول صويا 48%": 480,
        "كسب عباد الشمس 36%": 310, "كسب بذور القطن": 290,
        "نخالة قمح (ردة)": 150, "البرسيم الجاف": 170,
        "مولاس قصب السكر": 120, "مسحوق أسماك 60%": 850,
        "مركزات دواجن": 650, "مركزات مواشي": 600,
        "الحجر الجيري": 40, "فوسفات ثنائي الكالسيوم": 280,
        "ملح الطعام": 30, "بيكربونات الصوديوم": 340,
        "مضاد سموم فطرية": 950, "بريمكس تسمين دواجن": 4800,
        "بريمكس مجترات": 4500, "ليسين نقي": 4200, "ميثيونين نقي": 5800,
        "زيت ذرة": 1500, "زيت فول الصويا": 1350, "زيت عباد الشمس": 1300,
        "زيت بذرة القطن": 1400, "زيت الكتان": 1700, "زيت جوز الهند": 1900,
        "زيت النخيل": 1100, "زيت الكانولا": 1450, "زيت السمسم": 2100,
        "زيت الزيتون": 3500, "زيت الأفوكادو": 4200, "زيت القرطم": 1800,
        "زيت الفول السوداني": 2200, "شحم حيواني (Tallow)": 900,
        "سمن حيواني (Lard)": 850, "دهن الدجاج": 800,
        "زيت السمك (Fish Oil)": 3800,
    })
    m = 1.0
    if country == "السودان":
        m = 1.15
        if "كردفان" in state:
            m = 1.20
    elif country == "ليبيا":
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


# ═══════════════════════════════════════════════════════════════════════
# معايير تصميم الحظائر
# ═══════════════════════════════════════════════════════════════════════
BARN_DESIGN_STANDARDS = {
    "دواجن_لاحم": {
        "name_ar": "دواجن لاحم (Broiler)",
        "area_per_head": 0.10, "feeder_cm_per_head": 5.0,
        "drinker_cm_per_head": 2.5, "height_m": 2.8, "width_m": 12.0,
        "ach_summer": 60, "ach_winter": 8, "vent_open_ratio": 0.20,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "خطية معلقة", "drinker_type": "حلمات",
        "aisle_m": 1.2, "central_aisle": True,
    },
    "دواجن_بياض": {
        "name_ar": "دواجن بياض (Layer)",
        "area_per_head": 0.15, "feeder_cm_per_head": 10.0,
        "drinker_cm_per_head": 2.5, "height_m": 3.0, "width_m": 12.0,
        "ach_summer": 40, "ach_winter": 6, "vent_open_ratio": 0.20,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "سلسلة أو خطية", "drinker_type": "حلمات",
        "aisle_m": 1.2, "central_aisle": True,
    },
    "سمان": {
        "name_ar": "سمان (Quail)",
        "area_per_head": 0.025, "feeder_cm_per_head": 2.0,
        "drinker_cm_per_head": 1.0, "height_m": 2.0, "width_m": 6.0,
        "ach_summer": 50, "ach_winter": 8, "vent_open_ratio": 0.25,
        "roof_type": "mono", "slope_pct": 15.0,
        "feeder_type": "خطية معدنية", "drinker_type": "حلمات",
        "aisle_m": 0.8, "central_aisle": False,
    },
    "أغنام": {
        "name_ar": "أغنام (Sheep)",
        "area_per_head": 1.5, "feeder_cm_per_head": 35.0,
        "drinker_cm_per_head": 4.0, "height_m": 3.5, "width_m": 10.0,
        "ach_summer": 30, "ach_winter": 5, "vent_open_ratio": 0.30,
        "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "خطية خرسانية", "drinker_type": "حوض تلقائي",
        "aisle_m": 2.0, "central_aisle": True,
    },
    "ماعز": {
        "name_ar": "ماعز (Goat)",
        "area_per_head": 1.5, "feeder_cm_per_head": 35.0,
        "drinker_cm_per_head": 4.0, "height_m": 3.5, "width_m": 10.0,
        "ach_summer": 30, "ach_winter": 5, "vent_open_ratio": 0.30,
        "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "خطية مرتفعة", "drinker_type": "حوض تلقائي",
        "aisle_m": 2.0, "central_aisle": True,
    },
    "أبقار": {
        "name_ar": "أبقار (Cattle)",
        "area_per_head": 5.0, "feeder_cm_per_head": 70.0,
        "drinker_cm_per_head": 6.0, "height_m": 4.5, "width_m": 15.0,
        "ach_summer": 25, "ach_winter": 4, "vent_open_ratio": 0.35,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "خطية خرسانية وسطية", "drinker_type": "حوض تلقائي",
        "aisle_m": 3.5, "central_aisle": True,
    },
    "إبل": {
        "name_ar": "إبل (Camel)",
        "area_per_head": 10.0, "feeder_cm_per_head": 100.0,
        "drinker_cm_per_head": 8.0, "height_m": 4.5, "width_m": 15.0,
        "ach_summer": 20, "ach_winter": 4, "vent_open_ratio": 0.40,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "خطية مرتفعة", "drinker_type": "حوض كبير",
        "aisle_m": 4.0, "central_aisle": True,
    },
    "خيول": {
        "name_ar": "خيول (Horse)",
        "area_per_head": 16.0, "feeder_cm_per_head": 100.0,
        "drinker_cm_per_head": 10.0, "height_m": 4.0, "width_m": 15.0,
        "ach_summer": 25, "ach_winter": 5, "vent_open_ratio": 0.30,
        "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "خطية مرتفعة", "drinker_type": "حوض تلقائي",
        "aisle_m": 3.5, "central_aisle": True,
    },
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
    }


# ═══════════════════════════════════════════════════════════════════════
# مجسم 3D تفاعلي
# ═══════════════════════════════════════════════════════════════════════
def create_barn_3d_figure(dims):
    if not PLOTLY_AVAILABLE:
        return None
    try:
        std = dims["standard"]
        L = dims["length_m"]
        W = dims["width_m"]
        H = dims["height_m"]
        RH = dims["ridge_height_m"]
        aisle = dims.get("aisle_m", 1.5)
        feeder_w = 0.6
        fig = go.Figure()

        # الأرضية
        fig.add_trace(go.Mesh3d(
            x=[0, L, L, 0], y=[0, 0, W, W], z=[0, 0, 0, 0],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color='#d7ccc8', opacity=0.65, name='الأرضية', hoverinfo='skip'))

        # الجدران
        for x_pos in [0, L]:
            fig.add_trace(go.Mesh3d(
                x=[x_pos] * 4, y=[0, W, W, 0], z=[0, 0, H, H],
                i=[0, 0], j=[1, 2], k=[2, 3],
                color='#a1887f', opacity=0.35,
                showlegend=False, hoverinfo='skip'))
        for y_pos in [0, W]:
            fig.add_trace(go.Mesh3d(
                x=[0, L, L, 0], y=[y_pos] * 4, z=[0, 0, H, H],
                i=[0, 0], j=[1, 2], k=[2, 3],
                color='#a1887f', opacity=0.35,
                showlegend=False, hoverinfo='skip'))

        # السقف
        if dims["roof_type"] == "gable":
            fig.add_trace(go.Mesh3d(
                x=[0, L, L, 0], y=[0, 0, W/2, W/2], z=[H, H, RH, RH],
                i=[0, 0], j=[1, 2], k=[2, 3],
                color='#8d6e63', opacity=0.5, name='السقف', hoverinfo='skip'))
            fig.add_trace(go.Mesh3d(
                x=[0, L, L, 0], y=[W/2, W/2, W, W], z=[RH, RH, H, H],
                i=[0, 0], j=[1, 2], k=[2, 3],
                color='#8d6e63', opacity=0.5, showlegend=False, hoverinfo='skip'))
        else:
            fig.add_trace(go.Mesh3d(
                x=[0, L, L, 0], y=[0, 0, W, W], z=[RH, RH, H, H],
                i=[0, 0], j=[1, 2], k=[2, 3],
                color='#8d6e63', opacity=0.5, name='السقف', hoverinfo='skip'))

        # فتحات التهوية
        vent_h = H * std["vent_open_ratio"]
        for y_v in [0.15, W - 0.15]:
            fig.add_trace(go.Scatter3d(
                x=[1, L-1, L-1, 1, 1], y=[y_v] * 5,
                z=[H*0.35, H*0.35, H*0.35 + vent_h, H*0.35 + vent_h, H*0.35],
                mode='lines', line=dict(color='#1976d2', width=8),
                name='فتحة تهوية' if y_v == 0.15 else None,
                showlegend=(y_v == 0.15)))

        # المعالف كصناديق 3D
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
            fig.add_trace(go.Mesh3d(
                x=x_vals, y=y_vals, z=z_vals,
                i=i_idx, j=j_idx, k=k_idx,
                color='#ff8f00', opacity=0.85,
                name=f'معلف ({dims.get("feeder_type", "خطي")})' if idx == 0 else None,
                showlegend=(idx == 0), hoverinfo='skip'))

        # السقايات
        n_drinkers = dims["drinkers_count"]
        for i in range(n_drinkers):
            x_center = (i + 0.5) * (L / n_drinkers)
            y_center = W - aisle - 0.5 if dims.get("central_aisle", True) else W - 1.5
            fig.add_trace(go.Scatter3d(
                x=[x_center], y=[y_center], z=[0.4], mode='markers+text',
                marker=dict(size=14, color='#1976d2', symbol='diamond',
                            line=dict(color='#0d47a1', width=2)),
                text=[f'م{i+1}'], textposition='top center',
                textfont=dict(size=9, color='#0d47a1'),
                name=f'مسقى ({dims.get("drinker_type", "حوض")})' if i == 0 else None,
                showlegend=(i == 0)))

        # الحيوانات
        apr = dims["animals_per_row"]
        n_rows = max(1, dims["count"] // max(apr, 1))
        step = max(1, n_rows // 25)
        ax_, ay_, az_ = [], [], []
        for row_idx in range(0, n_rows, step):
            if dims.get("central_aisle", True) and W > 8:
                if row_idx % 2 == 0:
                    y_pos = aisle + (row_idx // 2) * (W/2 - aisle) / max(n_rows//2, 1)
                else:
                    y_pos = (row_idx // 2) * (W/2 - aisle) / max(n_rows//2, 1) + 0.5
            else:
                y_pos = 2.0 + (row_idx * (W - 3.0) / max(n_rows, 1))
            for col in range(min(apr, 20)):
                x_pos = 0.8 + col * (L - 1.6) / min(apr, 20)
                ax_.append(x_pos)
                ay_.append(y_pos)
                az_.append(0.2)
        if ax_:
            fig.add_trace(go.Scatter3d(
                x=ax_, y=ay_, z=az_, mode='markers',
                marker=dict(size=4, color='#1b5e20', opacity=0.8),
                name=f'الحيوانات ({dims["count"]})'))

        # الأبعاد
        fig.add_trace(go.Scatter3d(
            x=[0, L], y=[-1, -1], z=[0, 0], mode='lines+text',
            line=dict(color='#c62828', width=4),
            text=['', f'الطول {L} م'], textposition='middle right',
            textfont=dict(size=11, color='#c62828'), showlegend=False))

        fig.update_layout(
            title=dict(
                text=f"🏗️ {std['name_ar']} — {dims['count']} رأس | مساحة: {dims['total_area_m2']} م²",
                font=dict(size=15, color='#1b5e20')),
            scene=dict(
                xaxis=dict(title='الطول (م)', backgroundcolor='#f5f5f5'),
                yaxis=dict(title='العرض (م)', backgroundcolor='#f5f5f5'),
                zaxis=dict(title='الارتفاع (م)', backgroundcolor='#f5f5f5'),
                aspectmode='data',
                camera=dict(eye=dict(x=1.6, y=-1.6, z=1.2))),
            height=700,
            margin=dict(l=0, r=0, t=90, b=0),
            paper_bgcolor='white',
            legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='#2e7d32', borderwidth=1))
        return fig
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════
# فيديو GIF متحرك
# ═══════════════════════════════════════════════════════════════════════
def create_barn_animation_gif(dims, frames=30, fps=8):
    if not MATPLOTLIB_AVAILABLE or not PIL_AVAILABLE:
        return None
    try:
        std = dims["standard"]
        L = dims["length_m"]
        W = dims["width_m"]
        H = dims["height_m"]
        RH = dims["ridge_height_m"]
        aisle = dims.get("aisle_m", 1.5)
        fw = 0.6

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')

        def draw_barn():
            ax.clear()
            floor = [[(0, 0, 0), (L, 0, 0), (L, W, 0), (0, W, 0)]]
            ax.add_collection3d(Poly3DCollection(
                floor, facecolors='#d7ccc8', edgecolors='#5d4037',
                alpha=0.75, linewidths=1.5))
            walls = [
                [(0, 0, 0), (L, 0, 0), (L, 0, H), (0, 0, H)],
                [(0, W, 0), (L, W, 0), (L, W, H), (0, W, H)],
                [(0, 0, 0), (0, W, 0), (0, W, H), (0, 0, H)],
                [(L, 0, 0), (L, W, 0), (L, W, H), (L, 0, H)]]
            ax.add_collection3d(Poly3DCollection(
                walls, facecolors='#a1887f', edgecolors='#5d4037',
                alpha=0.4, linewidths=1))
            if dims["roof_type"] == "gable":
                r1 = [[(0, 0, H), (L, 0, H), (L, W/2, RH), (0, W/2, RH)]]
                r2 = [[(0, W/2, RH), (L, W/2, RH), (L, W, H), (0, W, H)]]
                ax.add_collection3d(Poly3DCollection(
                    r1, facecolors='#8d6e63', edgecolors='#4e342e',
                    alpha=0.55, linewidths=1))
                ax.add_collection3d(Poly3DCollection(
                    r2, facecolors='#8d6e63', edgecolors='#4e342e',
                    alpha=0.55, linewidths=1))
            vent_h = H * std["vent_open_ratio"]
            for y_v in [0.15, W - 0.15]:
                ax.plot(
                    [1, L-1, L-1, 1, 1], [y_v] * 5,
                    [H*0.35, H*0.35, H*0.35 + vent_h, H*0.35 + vent_h, H*0.35],
                    color='#1976d2', linewidth=2.5,
                    label='فتحة تهوية' if y_v < 1 else None)
            if dims.get("central_aisle", True) and W > 8:
                fpos = [W/2 - aisle/2 - fw, W/2 + aisle/2]
            else:
                fpos = [0.8, W - 1.4]
            for yp in fpos:
                fb = [
                    [(0.5, yp, 0.35), (L-0.5, yp, 0.35),
                     (L-0.5, yp + fw, 0.35), (0.5, yp + fw, 0.35)],
                    [(0.5, yp, 0), (0.5, yp + fw, 0),
                     (0.5, yp + fw, 0.35), (0.5, yp, 0.35)],
                    [(L-0.5, yp, 0), (L-0.5, yp + fw, 0),
                     (L-0.5, yp + fw, 0.35), (L-0.5, yp, 0.35)]]
                ax.add_collection3d(Poly3DCollection(
                    fb, facecolors='#ff8f00', edgecolors='#e65100',
                    alpha=0.9, linewidths=1))
            nd = dims["drinkers_count"]
            xd = [(i + 0.5) * (L / nd) for i in range(nd)]
            yd = [W - aisle - 0.5 if dims.get("central_aisle", True) else W - 1.5] * len(xd)
            ax.scatter(xd, yd, [0.4] * len(xd), s=120, c='#1976d2',
                       marker='D', label='مسقى', depthshade=False,
                       edgecolors='#0d47a1')
            apr = dims["animals_per_row"]
            nr = max(1, dims["count"] // max(apr, 1))
            ss = max(1, nr // 15)
            xa, ya = [], []
            for ri in range(0, nr, ss):
                if dims.get("central_aisle", True) and W > 8:
                    if ri % 2 == 0:
                        yp = aisle + (ri // 2) * (W/2 - aisle) / max(nr//2, 1)
                    else:
                        yp = (ri // 2) * (W/2 - aisle) / max(nr//2, 1) + 0.5
                else:
                    yp = 2.0 + ri * (W - 3.0) / max(nr, 1)
                for col in range(min(apr, 15)):
                    xa.append(0.8 + col * (L - 1.6) / min(apr, 15))
                    ya.append(yp)
            ax.scatter(xa, ya, [0.2] * len(xa), s=25, c='#1b5e20',
                       alpha=0.85, label=f'حيوانات ({dims["count"]})',
                       depthshade=False)
            ax.set_xlim(0, L)
            ax.set_ylim(0, W)
            ax.set_zlim(0, RH + 1)
            ax.set_xlabel('الطول')
            ax.set_ylabel('العرض')
            ax.set_zlabel('الارتفاع')
            ax.set_title(f"🏗️ {std['name_ar']} — {dims['count']} رأس",
                         fontsize=13, color='#1b5e20', fontweight='bold')
            ax.legend(loc='upper left', fontsize=8)

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


# ═══════════════════════════════════════════════════════════════════════
# صورة الحظيرة للـ PDF
# ═══════════════════════════════════════════════════════════════════════
def render_barn_to_pdf_image(dims):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        std = dims["standard"]
        L = dims["length_m"]
        W = dims["width_m"]
        H = dims["height_m"]
        RH = dims["ridge_height_m"]
        aisle = dims.get("aisle_m", 1.5)
        fw = 0.6
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')

        floor = [[(0, 0, 0), (L, 0, 0), (L, W, 0), (0, W, 0)]]
        ax.add_collection3d(Poly3DCollection(
            floor, facecolors='#d7ccc8', edgecolors='#5d4037',
            alpha=0.75, linewidths=1.5))
        walls = [
            [(0, 0, 0), (L, 0, 0), (L, 0, H), (0, 0, H)],
            [(0, W, 0), (L, W, 0), (L, W, H), (0, W, H)],
            [(0, 0, 0), (0, W, 0), (0, W, H), (0, 0, H)],
            [(L, 0, 0), (L, W, 0), (L, W, H), (L, 0, H)]]
        ax.add_collection3d(Poly3DCollection(
            walls, facecolors='#a1887f', edgecolors='#5d4037',
            alpha=0.4, linewidths=1))
        if dims["roof_type"] == "gable":
            r1 = [[(0, 0, H), (L, 0, H), (L, W/2, RH), (0, W/2, RH)]]
            r2 = [[(0, W/2, RH), (L, W/2, RH), (L, W, H), (0, W, H)]]
            ax.add_collection3d(Poly3DCollection(
                r1, facecolors='#8d6e63', edgecolors='#4e342e',
                alpha=0.55, linewidths=1))
            ax.add_collection3d(Poly3DCollection(
                r2, facecolors='#8d6e63', edgecolors='#4e342e',
                alpha=0.55, linewidths=1))
        else:
            roof = [[(0, 0, RH), (L, 0, RH), (L, W, H), (0, W, H)]]
            ax.add_collection3d(Poly3DCollection(
                roof, facecolors='#8d6e63', edgecolors='#4e342e',
                alpha=0.5, linewidths=1))

        vent_h = H * std["vent_open_ratio"]
        for y_v in [0.15, W - 0.15]:
            ax.plot([1, L-1, L-1, 1, 1], [y_v] * 5,
                    [H*0.35, H*0.35, H*0.35 + vent_h, H*0.35 + vent_h, H*0.35],
                    color='#1976d2', linewidth=2.5,
                    label='فتحة تهوية' if y_v < 1 else None)

        if dims.get("central_aisle", True) and W > 8:
            fpos = [W/2 - aisle/2 - fw, W/2 + aisle/2]
        else:
            fpos = [0.8, W - 1.4]
        for yp in fpos:
            fb = [
                [(0.5, yp, 0.35), (L-0.5, yp, 0.35),
                 (L-0.5, yp + fw, 0.35), (0.5, yp + fw, 0.35)],
                [(0.5, yp, 0), (0.5, yp + fw, 0),
                 (0.5, yp + fw, 0.35), (0.5, yp, 0.35)],
                [(L-0.5, yp, 0), (L-0.5, yp + fw, 0),
                 (L-0.5, yp + fw, 0.35), (L-0.5, yp, 0.35)]]
            ax.add_collection3d(Poly3DCollection(
                fb, facecolors='#ff8f00', edgecolors='#e65100',
                alpha=0.9, linewidths=1))

        nd = dims["drinkers_count"]
        xd = [(i + 0.5) * (L / nd) for i in range(nd)]
        yd = [W - aisle - 0.5 if dims.get("central_aisle", True) else W - 1.5] * len(xd)
        ax.scatter(xd, yd, [0.4] * len(xd), s=120, c='#1976d2',
                   marker='D', label='مسقى', depthshade=False,
                   edgecolors='#0d47a1')

        apr = dims["animals_per_row"]
        nr = max(1, dims["count"] // max(apr, 1))
        ss = max(1, nr // 15)
        xa, ya = [], []
        for ri in range(0, nr, ss):
            if dims.get("central_aisle", True) and W > 8:
                if ri % 2 == 0:
                    yp = aisle + (ri // 2) * (W/2 - aisle) / max(nr//2, 1)
                else:
                    yp = (ri // 2) * (W/2 - aisle) / max(nr//2, 1) + 0.5
            else:
                yp = 2.0 + ri * (W - 3.0) / max(nr, 1)
            for col in range(min(apr, 15)):
                xa.append(0.8 + col * (L - 1.6) / min(apr, 15))
                ya.append(yp)
        ax.scatter(xa, ya, [0.2] * len(xa), s=25, c='#1b5e20',
                   alpha=0.85, label=f'حيوانات ({dims["count"]})',
                   depthshade=False)

        ax.set_xlim(0, L)
        ax.set_ylim(0, W)
        ax.set_zlim(0, RH + 1)
        ax.set_xlabel('الطول (م)')
        ax.set_ylabel('العرض (م)')
        ax.set_zlabel('الارتفاع (م)')
        ax.set_title(f"تصميم — {std['name_ar']} | {dims['count']} رأس",
                     fontsize=14, color='#1b5e20', fontweight='bold')
        ax.legend(loc='upper left', fontsize=9)
        ax.view_init(elev=18, azim=-55)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════
# تقرير PDF للحظيرة
# ═══════════════════════════════════════════════════════════════════════
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
        ('BACKGROUND', (1, 0), (1, -1), HexColor('#fafafa')),
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

    story.append(P("📐 الأبعاد الهندسية", size=14, align=TA_RIGHT, color='#1b5e20'))
    story.append(Spacer(1, 8))
    dim_data = [
        [ar("البيان"), ar("القيمة")],
        [ar("المساحة الكلية"), ar(f"{dims['total_area_m2']} م²")],
        [ar("الطول"), ar(f"{dims['length_m']} م")],
        [ar("العرض"), ar(f"{dims['width_m']} م")],
        [ar("ارتفاع الجدار"), ar(f"{dims['height_m']} م")],
        [ar("ارتفاع القمة"), ar(f"{dims['ridge_height_m']} م")],
        [ar("حجم الهواء"), ar(f"{dims['volume_m3']} م³")],
    ]
    t2 = Table(dim_data, colWidths=[250, 240])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 15))

    story.append(P("💨 التهوية والخدمات", size=14, align=TA_RIGHT, color='#1976d2'))
    story.append(Spacer(1, 8))
    serv_data = [
        [ar("البيان"), ar("القيمة")],
        [ar("تهوية صيفية"), ar(f"{dims['vent_flow_summer_m3h']:,} م³/ساعة")],
        [ar("تهوية شتوية"), ar(f"{dims['vent_flow_winter_m3h']:,} م³/ساعة")],
        [ar("فتحات التهوية"), ar(f"{dims['vent_open_area_m2']} م²")],
        [ar("عدد المعالف"), ar(str(dims['feeders_count']))],
        [ar("طول المعالف"), ar(f"{dims['total_feeder_length_m']} م")],
        [ar("عدد السقايات"), ar(str(dims['drinkers_count']))],
        [ar("طول السقايات"), ar(f"{dims['total_drinker_length_m']} م")],
    ]
    t3 = Table(serv_data, colWidths=[250, 240])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1976d2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t3)
    story.append(Spacer(1, 20))

    story.append(P("🏗️ المجسم ثلاثي الأبعاد", size=14,
                   align=TA_RIGHT, color='#1b5e20'))
    story.append(Spacer(1, 10))
    img = render_barn_to_pdf_image(dims)
    if img:
        try:
            story.append(RLImage(img, width=480, height=340))
        except Exception:
            pass
    story.append(Spacer(1, 20))

    # التوقيع
    sign = [[ar("توقيع المختص")], [ar(SUPERVISOR)], [ar(SUPERVISOR_TITLE)]]
    ts = Table(sign, colWidths=[400])
    ts.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f5e9')),
    ]))
    story.append(ts)

    doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
    buffer.seek(0)
    return buffer.getvalue()


# ═══════════════════════════════════════════════════════════════════════
# دراسة الجدوى الفنية
# ═══════════════════════════════════════════════════════════════════════
TECHNICAL_FEASIBILITY_DATA = {
    "دواجن_لاحم": {
        "feed_per_day_g": 120, "water_per_day_ml": 220, "labor_per_1000": 0.3,
        "cycle_days": 42, "final_weight_kg": 2.3, "fcr": 1.65,
        "production_type": "meat", "product_unit": "كجم لحم حي",
        "notes": "دورة 42 يوم، وزن نهائي 2.3 كجم",
    },
    "دواجن_بياض": {
        "feed_per_day_g": 110, "water_per_day_ml": 250, "labor_per_1000": 0.3,
        "eggs_per_year": 310, "egg_weight_g": 60,
        "production_type": "eggs", "product_unit": "بيضة",
        "notes": "310 بيضة/دجاجة/سنة",
    },
    "سمان": {
        "feed_per_day_g": 28, "water_per_day_ml": 55, "labor_per_1000": 0.5,
        "cycle_days": 42, "final_weight_kg": 0.25, "fcr": 2.5,
        "production_type": "meat", "product_unit": "كجم لحم حي",
        "notes": "دورة 42 يوم، وزن 250 جرام",
    },
    "أغنام": {
        "feed_per_day_g": 1800, "water_per_day_ml": 6000, "labor_per_1000": 1.5,
        "milk_per_day_L": 1.5, "lactation_days": 200,
        "production_type": "mixed", "product_unit": "حليب + حملان",
        "notes": "1.5 لتر حليب × 200 يوم",
    },
    "ماعز": {
        "feed_per_day_g": 1500, "water_per_day_ml": 6000, "labor_per_1000": 1.5,
        "milk_per_day_L": 2.5, "lactation_days": 280,
        "production_type": "milk", "product_unit": "لتر حليب",
        "notes": "2.5 لتر × 280 يوم",
    },
    "أبقار": {
        "feed_per_day_g": 20000, "water_per_day_ml": 80000, "labor_per_1000": 5.0,
        "milk_per_day_L": 20, "lactation_days": 305,
        "production_type": "milk", "product_unit": "لتر حليب",
        "notes": "20 لتر × 305 يوم",
    },
    "إبل": {
        "feed_per_day_g": 8000, "water_per_day_ml": 50000, "labor_per_1000": 3.0,
        "milk_per_day_L": 5, "lactation_days": 300,
        "production_type": "milk", "product_unit": "لتر حليب",
        "notes": "5 لتر × 300 يوم",
    },
    "خيول": {
        "feed_per_day_g": 10000, "water_per_day_ml": 40000, "labor_per_1000": 4.0,
        "production_type": "service", "product_unit": "خدمات",
        "notes": "خيول رياضة أو عمل",
    },
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
        production = {
            "unit": "بيضة/سنة", "annual": eggs_year, "per_day": eggs_year / 365,
            "weight_ton": eggs_year * tech.get("egg_weight_g", 60) / 1_000_000,
            "details": tech.get("notes", ""),
        }
    elif ptype == "milk":
        milk_day = count * tech.get("milk_per_day_L", 20)
        milk_year = milk_day * tech.get("lactation_days", 305)
        production = {
            "unit": "لتر/سنة", "annual": milk_year, "per_day": milk_day,
            "lactation_days": tech.get("lactation_days", 305),
            "details": tech.get("notes", ""),
        }
    elif ptype == "meat":
        cycle = tech.get("cycle_days", 42)
        cycles_year = 365 / cycle
        total_kg = count * tech.get("final_weight_kg", 2) * cycles_year
        production = {
            "unit": "كجم/سنة", "annual": total_kg,
            "per_cycle": count * tech.get("final_weight_kg", 2),
            "cycles_year": cycles_year, "details": tech.get("notes", ""),
        }
    elif ptype == "mixed":
        milk_day = count * tech.get("milk_per_day_L", 1)
        milk_year = milk_day * tech.get("lactation_days", 200)
        production = {
            "unit": "لتر/سنة", "annual": milk_year, "per_day": milk_day,
            "details": tech.get("notes", ""),
        }
    else:
        production = {"unit": "خدمات", "annual": 0, "details": tech.get("notes", "")}

    return {
        "barn_key": barn_key, "std": std, "dims": dims, "count": count,
        "feed": {
            "per_head_day_kg": tech.get("feed_per_day_g", 100) / 1000.0,
            "total_day_kg": feed_day,
            "total_month_ton": feed_day * 30 / 1000,
            "total_year_ton": feed_day * 365 / 1000,
        },
        "water": {
            "per_head_day_L": tech.get("water_per_day_ml", 200) / 1000.0,
            "total_day_L": water_day,
            "total_year_m3": water_day * 365 / 1000,
        },
        "labor": {"workers": workers, "animals_per_worker": count // workers},
        "production": production,
        "ventilation": {
            "summer_m3h": dims["vent_flow_summer_m3h"],
            "winter_m3h": dims["vent_flow_winter_m3h"],
        },
    }


# ═══════════════════════════════════════════════════════════════════════
# كتيّب الجدوى PDF (5 صفحات)
# ═══════════════════════════════════════════════════════════════════════
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

    # ═══ صفحة 1: الغلاف ═══
    story.append(Spacer(1, 30))
    story.append(P("كتيّب دراسة الجدوى الفنية", size=30,
                   align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 6))
    story.append(P("Technical Feasibility Study", size=13,
                   align=TA_CENTER, color='#666'))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=3, color=HexColor('#d4af37')))
    story.append(Spacer(1, 30))
    story.append(P(f"مشروع: {project_name or std['name_ar']}", size=18,
                   align=TA_CENTER, color='#c62828'))
    story.append(Spacer(1, 15))
    story.append(P(f"{count} رأس من {std['name_ar']}", size=14,
                   align=TA_CENTER, color='#1a1a1a'))
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
        ('BACKGROUND', (1, 0), (1, -1), HexColor('#fafafa')),
        ('BOX', (0, 0), (-1, -1), 2, HexColor('#2e7d32')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#c8e6c9')),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 60))
    story.append(P(f"🤲 {DUA_SHORT} 🤲", size=12,
                   align=TA_CENTER, color='#c62828'))
    story.append(PageBreak())

    # ═══ صفحة 2: تصميم الحظيرة ═══
    story.append(P("🏗️ الباب الأول: تصميم الحظيرة", size=18,
                   align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#d4af37')))
    story.append(Spacer(1, 15))

    barn_data = [
        [ar("البيان"), ar("القيمة")],
        [ar("المساحة"), ar(f"{dims['total_area_m2']} م²")],
        [ar("الطول"), ar(f"{dims['length_m']} م")],
        [ar("العرض"), ar(f"{dims['width_m']} م")],
        [ar("ارتفاع الجدار"), ar(f"{dims['height_m']} م")],
        [ar("ارتفاع القمة"), ar(f"{dims['ridge_height_m']} م")],
        [ar("الحجم"), ar(f"{dims['volume_m3']} م³")],
        [ar("نوع السقف"), ar("جمالوني" if dims["roof_type"] == "gable" else "منحدر أحادي")],
        [ar("ميل السقف"), ar(f"{dims['slope_pct']}%")],
        [ar("عدد المعالف"), ar(f"{dims['feeders_count']} ({dims['total_feeder_length_m']} م)")],
        [ar("نوع المعالف"), ar(dims.get("feeder_type", ""))],
        [ar("عدد السقايات"), ar(f"{dims['drinkers_count']} ({dims['total_drinker_length_m']} م)")],
        [ar("نوع السقايات"), ar(dims.get("drinker_type", ""))],
        [ar("الممر"), ar(f"{dims.get('aisle_m', 1.5)} م")],
    ]
    t = Table(barn_data, colWidths=[220, 230])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))
    img = render_barn_to_pdf_image(dims)
    if img:
        try:
            story.append(RLImage(img, width=480, height=340))
        except Exception:
            pass
    story.append(PageBreak())

    # ═══ صفحة 3: الجدوى الفنية ═══
    story.append(P("🔧 الباب الثاني: الجدوى الفنية", size=18,
                   align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#d4af37')))
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
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

    mini_table("🍽️ احتياجات العلف", '#e65100', [
        ("علف/رأس/يوم", f"{feas['feed']['per_head_day_kg']*1000:.0f} جرام"),
        ("إجمالي يومي", f"{feas['feed']['total_day_kg']:.1f} كجم"),
        ("إجمالي شهري", f"{feas['feed']['total_month_ton']:.2f} طن"),
        ("إجمالي سنوي", f"{feas['feed']['total_year_ton']:.2f} طن"),
    ])
    mini_table("💧 احتياجات الماء", '#1976d2', [
        ("ماء/رأس/يوم", f"{feas['water']['per_head_day_L']:.1f} لتر"),
        ("إجمالي يومي", f"{feas['water']['total_day_L']:.0f} لتر"),
        ("إجمالي سنوي", f"{feas['water']['total_year_m3']:.1f} م³"),
    ])
    mini_table("💨 التهوية", '#558b2f', [
        ("تهوية صيفية", f"{feas['ventilation']['summer_m3h']:,} م³/ساعة"),
        ("تهوية شتوية", f"{feas['ventilation']['winter_m3h']:,} م³/ساعة"),
        ("مساحة الفتحات", f"{dims['vent_open_area_m2']} م²"),
    ])
    mini_table("👷 العمالة", '#6d4c41', [
        ("عدد العمال", str(feas['labor']['workers'])),
        ("حيوانات/عامل", str(feas['labor']['animals_per_worker'])),
    ])
    story.append(PageBreak())

    # ═══ صفحة 4: الإنتاج ═══
    story.append(P("📊 الباب الثالث: الإنتاج المتوقع", size=18,
                   align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#d4af37')))
    story.append(Spacer(1, 15))

    prod = feas["production"]
    story.append(P(f"نوع الإنتاج: {prod.get('unit', '—')}", size=14, color='#c62828'))
    story.append(Spacer(1, 10))

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
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    story.append(P("📝 ملاحظات فنية", size=13, color='#1b5e20'))
    story.append(Spacer(1, 8))
    for note in [
        "• هذه الدراسة فنية فقط (تغذية، مساحة، تهوية، عمالة) ولا تشمل التكاليف والأسعار.",
        "• الأرقام تقديرية وفق المعايير العالمية: NRC، FAO، MWPS، ASABE.",
        "• يُنصح بإعادة التقييم كل 6 أشهر وفق الظروف الفعلية.",
        f"• المساحة الموصى بها لكل رأس: {std['area_per_head']} م².",
        f"• طول المعلف/رأس: {std['feeder_cm_per_head']} سم.",
    ]:
        story.append(P(note, size=10, color='#444'))
    story.append(PageBreak())

    # ═══ صفحة 5: التوقيع ═══
    story.append(Spacer(1, 60))
    story.append(P("✍️ الاعتماد والتوقيع الرسمي", size=20,
                   align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
    story.append(Spacer(1, 40))
    story.append(P("أُعدّت هذه الدراسة الفنية بمعرفة:", size=13,
                   align=TA_CENTER, color='#1a1a1a'))
    story.append(Spacer(1, 20))
    story.append(P(SUPERVISOR, size=20, align=TA_CENTER, color='#c62828'))
    story.append(P(SUPERVISOR_TITLE, size=13, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 50))

    sig_data = [
        [ar("توقيع المختص"), ar("التاريخ")],
        [ar("........................"), ar(datetime.now().strftime('%Y-%m-%d'))],
    ]
    st_tbl = Table(sig_data, colWidths=[220, 220])
    st_tbl.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#1b5e20')),
        ('INNERGRID', (0, 0), (-1, -1), 0.8, HexColor('#c8e6c9')),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f5e9')),
    ]))
    story.append(st_tbl)
    story.append(Spacer(1, 50))
    story.append(P(f"🤲 {DUA_FULL} 🤲", size=12,
                   align=TA_CENTER, color='#c62828'))

    doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
    buffer.seek(0)
    return buffer.getvalue()


# ═══════════════════════════════════════════════════════════════════════
# Session State
# ═══════════════════════════════════════════════════════════════════════
DEFAULTS = {
    "approved": False, "user_role": None,
    "active_formula": {}, "active_stage_title": "إنتاج عام",
    "active_animal_img": ANIMAL_IMAGES["عام"], "computed_ton_cost": 280.0,
    "inventory": {},
    "shared_comments": f"• مرحباً بكم في {APP_NAME}\n• {DUA_SHORT}\n",
    "broiler_farms": {},
    "livestock_prices": {
        "عجول تسمين هولشتاين ($)": 1350.0, "أبقار كنانة ($)": 900.0,
        "ضأن محلي ($)": 180.0, "ماعز نوبي ($)": 130.0,
        "إبل حاشي ($)": 1200.0, "كتكوت لاحم يوم ($)": 0.65,
        "دجاج بياض ($)": 5.50,
    },
    "products_prices": {
        "كيلو لحم بقري ($)": 7.50, "كيلو لحم ضأن ($)": 9.00,
        "كيلو لحم إبل ($)": 8.50, "كيلو لحم دجاج ($)": 3.80,
        "طبق بيض 30 ($)": 4.20, "لتر حليب بقر ($)": 0.90,
        "لتر حليب إبل ($)": 3.50,
    },
    "barn_last_dims": None,
    "last_formulation_result": None,
    "last_formulation_context": None,
    "barn_video_gif": None,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state["inventory"]:
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing in cat:
            st.session_state["inventory"][ing] = {
                "quantity": 25.0, "min_threshold": 5.0, "unit": "طن"
            }


def is_owner():
    return st.session_state.get("user_role") == "owner"


# ═══════════════════════════════════════════════════════════════════════
# CSS الشامل
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');
* { font-family: 'Cairo', 'Amiri', sans-serif; color: #1a1a1a !important; }
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
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
    margin-bottom: 60px;
    backdrop-filter: blur(5px);
}
h1, h2, h3, h4, h5, p, span, li, div, label { color: #1a1a1a !important; }

@keyframes duaGlow {
    0%, 100% { box-shadow: 0 15px 40px rgba(0,0,0,0.4), inset 0 0 30px rgba(212,175,55,0.2); }
    50% { box-shadow: 0 15px 40px rgba(0,0,0,0.5), inset 0 0 40px rgba(212,175,55,0.4), 0 0 80px rgba(212,175,55,0.5); }
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
    padding: 32px 28px;
    border-radius: 22px;
    border: 4px solid #d4af37;
    direction: rtl;
    text-align: center;
    margin: 25px 0;
    position: relative;
    overflow: hidden;
}
.dua-main-box::before {
    content: "🕌";
    position: absolute;
    top: 15px;
    right: 25px;
    font-size: 3.5rem;
    opacity: 0.25;
    animation: floatIcon 4s ease-in-out infinite;
}
.dua-main-box::after {
    content: "🕌";
    position: absolute;
    bottom: 15px;
    left: 25px;
    font-size: 3.5rem;
    opacity: 0.25;
    animation: floatIcon 5s ease-in-out infinite reverse;
}
.dua-main-box * {
    color: white !important;
    position: relative;
    z-index: 2;
}
.dua-main-box h3 {
    color: #d4af37 !important;
    font-size: 1.9rem;
    margin-bottom: 18px;
    font-weight: 900;
    letter-spacing: 1px;
    text-shadow: 0 2px 10px rgba(212,175,55,0.5);
}
.dua-main-box .names {
    display: inline-block;
    background: linear-gradient(90deg, rgba(212,175,55,0.15), rgba(212,175,55,0.35), rgba(212,175,55,0.15));
    background-size: 200% 100%;
    animation: shimmerText 4s linear infinite;
    font-size: 1.65rem;
    font-weight: 900;
    color: #ffeb3b !important;
    margin: 20px 0;
    padding: 16px 30px;
    border: 2px solid #d4af37;
    border-radius: 15px;
    text-shadow: 0 0 20px rgba(255,235,59,0.6);
    font-family: 'Amiri', serif !important;
}
.dua-main-box p.quran {
    font-family: 'Amiri', serif !important;
    font-size: 1.2rem;
    color: #d4af37 !important;
    margin-top: 22px;
    padding: 18px 25px;
    background: rgba(0,0,0,0.25);
    border-radius: 12px;
    border-right: 5px solid #d4af37;
    border-left: 5px solid #d4af37;
}
.visitor-dua-banner {
    background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 50%, #ffe082 100%);
    padding: 20px 28px;
    border-radius: 18px;
    border: 3px solid #d4af37;
    margin: 22px 0;
    direction: rtl;
    text-align: center;
    box-shadow: 0 6px 25px rgba(0,0,0,0.15);
}
.visitor-dua-banner * { color: #4e342e !important; }
.visitor-dua-banner b {
    color: #c62828 !important;
    font-size: 1.15rem;
    font-family: 'Amiri', serif !important;
}
.dua-fixed-banner {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32, #1b5e20, #0d3011);
    background-size: 200% 100%;
    animation: gradientShift 8s linear infinite;
    color: white !important;
    padding: 11px 20px;
    z-index: 9998;
    text-align: center;
    border-top: 3px solid #d4af37;
    font-family: 'Amiri', serif !important;
    font-size: 1.05rem;
    font-weight: bold;
    box-shadow: 0 -4px 25px rgba(0,0,0,0.4);
    letter-spacing: 0.5px;
}
.dua-fixed-banner * {
    color: #ffeb3b !important;
    font-family: 'Amiri', serif !important;
}
.section-title {
    color: #1b5e20 !important;
    border-right: 6px solid #2e7d32;
    padding: 12px 18px;
    text-align: right;
    font-size: 1.5rem;
    font-weight: bold;
    margin-top: 30px;
    margin-bottom: 20px;
    background: linear-gradient(to left, rgba(46,125,50,0.15), transparent);
    border-radius: 10px;
}
.formula-item {
    background: linear-gradient(135deg, #ffffff 0%, #e8f5e9 100%);
    padding: 15px 20px;
    border-radius: 12px;
    margin-bottom: 10px;
    font-weight: bold;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    text-align: right;
}
.oil-item {
    background: linear-gradient(135deg, #fff8e1 0%, #ffe0b2 100%);
    padding: 12px 18px;
    border-radius: 12px;
    margin-bottom: 8px;
    font-weight: bold;
    color: #bf360c !important;
    border-right: 5px solid #e65100;
    box-shadow: 0 4px 15px rgba(230,81,0,0.15);
    text-align: right;
}
.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px;
    border-radius: 12px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 20px;
    direction: rtl;
    text-align: right;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.oil-info-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 18px;
    border-radius: 12px;
    border-right: 5px solid #e65100;
    margin-bottom: 18px;
    direction: rtl;
    text-align: right;
    box-shadow: 0 4px 15px rgba(230,81,0,0.15);
}
.barn-info-card {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 18px;
    border-radius: 12px;
    border-right: 5px solid #1976d2;
    margin-bottom: 18px;
    direction: rtl;
    text-align: right;
}
.video-card {
    background: linear-gradient(135deg, #fce4ec, #f8bbd0);
    padding: 18px;
    border-radius: 12px;
    border-right: 5px solid #ad1457;
    margin-bottom: 18px;
    direction: rtl;
    text-align: right;
}
.feas-card {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 20px;
    border-radius: 15px;
    border-right: 6px solid #2e7d32;
    margin-bottom: 20px;
    direction: rtl;
    text-align: right;
}
.profile-img-style {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #d4af37;
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    display: block;
    margin: 0 auto;
}
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
    bottom: 65px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important;
    padding: 9px 22px;
    font-size: 0.88rem;
    border-radius: 25px;
    z-index: 9997;
    direction: rtl;
    border: 2px solid #d4af37;
    font-weight: bold;
}
.mini-signature * { color: white !important; }
</style>
""", unsafe_allow_html=True)
# ═══════════════════════════════════════════════════════════════════════
# بوابة الدخول
# ═══════════════════════════════════════════════════════════════════════
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
        <p style="font-size: 0.9rem; color: #555;">دخول مجاني<br>
        <small style="color: #999;">(يشمل الحظائر 3D + الجدوى + المزارع)</small></p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True):
            st.session_state.update({"approved": True, "user_role": "guest"})
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════════════════════
# الواجهة الرئيسية
# ═══════════════════════════════════════════════════════════════════════
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
            if k != "inventory":
                del st.session_state[k]
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
               font-weight: 900; font-size: 2.3rem; -webkit-text-stroke: 0.5px #1b5e20;'>
    🌾 {APP_NAME}
    </h1>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <p style='color: #1565C0; text-align:right; font-size: 1.25rem; font-weight: 600;
              margin-top: 8px; text-shadow: 1px 1px 2px rgba(21,101,192,0.2);'>
    {APP_TAGLINE}
    </p>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #fff8e1, #ffe082);
                padding: 12px 20px; border-radius: 12px;
                border-right: 6px solid #c62828; border-left: 6px solid #c62828;
                margin-top: 10px; box-shadow: 0 4px 15px rgba(198,40,40,0.25);'>
        <h3 style='color: #b71c1c; text-align:right; margin: 0;
                   font-weight: 900; font-size: 1.55rem;
                   text-shadow: 1px 1px 2px rgba(198,40,40,0.3); letter-spacing: 0.5px;'>
        👨‍🔬 {SUPERVISOR}
        </h3>
        <p style='color: #0d47a1; text-align:right; margin: 5px 0 0 0;
                  font-weight: 700; font-size: 1.15rem;'>✨ {SUPERVISOR_TITLE}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="visitor-dua-banner">{DUA_VISITOR}</div>', unsafe_allow_html=True)
st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# التبويبات
# ═══════════════════════════════════════════════════════════════════════
if is_owner():
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية", "🌰 مكتبة الزيوت", "🍼 بدائل الحليب",
        "📷 المختبر الذكي", "🏗️ تصميم الحظائر 3D", "📊 دراسة الجدوى",
        "🐔 مزارع الدجاج", "📊 البورصة", "🏭 المستودعات", "🧾 الفواتير",
        "🖨️ الديباجة", "📈 التحليلات", "💬 التعليقات",
        "📚 المراجع", "💡 المساعدة", "📖 الدليل",
    ]
else:
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية", "🌰 مكتبة الزيوت", "🍼 بدائل الحليب",
        "📷 المختبر الذكي", "🏗️ تصميم الحظائر 3D", "📊 دراسة الجدوى",
        "🐔 مزارع الدجاج", "📚 المراجع", "💡 المساعدة", "📖 الدليل",
    ]

tabs = st.tabs(tabs_titles)
tab_map = {title: tab for title, tab in zip(tabs_titles, tabs)}


# ═══════════════════════════════════════════════════════════════════════
# تبويب النمذجة (المصحح بالكامل)
# ═══════════════════════════════════════════════════════════════════════
with tab_map["🔬 النمذجة والحسابات العلفية"]:
    try:
        sub_tab_formulator, sub_tab_analyzer = st.tabs([
            "🎯 تركيب علفة نموذجية",
            "🔬 مختبر تحليل وفحص الأعلاف الجاهزة"
        ])

        with sub_tab_formulator:
            try:
                # الموقع
                st.markdown('<div class="section-title">🌍 الموقع الجغرافي</div>',
                            unsafe_allow_html=True)
                cc1, cc2, cc3 = st.columns(3)
                with cc1:
                    country = st.selectbox("🌍 الدولة:", list(EXCHANGE_RATES.keys()), key="country")
                with cc2:
                    state = st.text_input("🗺️ الولاية:", "الخرطوم", key="state")
                with cc3:
                    city = st.text_input("🏙️ المدينة:", "الخرطوم", key="city")
                rate = EXCHANGE_RATES.get(country, {"rate": 1.0, "sym": "USD"})
                local_rate = rate["rate"]
                local_sym = rate["sym"]
                live_prices = get_market_prices(country, city, state)

                # أساس الحساب
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
                if use_dp:
                    st.success("🎯 الحساب سيكون على أساس **DP** (البروتين المهضوم)")
                else:
                    st.info("📊 الحساب سيكون على أساس **CP** (البروتين الخام)")

                # اختيار الحيوان
                st.markdown('<div class="section-title">🐾 اختر الحيوان والحالة الفسيولوجية</div>',
                            unsafe_allow_html=True)
                animal_tabs = st.tabs([
                    "🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐪 إبل",
                    "🐎 خيول", "🐔 دواجن", "🦆 سمان", "🐟 أسماك"
                ])

                animal_choice = None
                production_type = None
                requirement = None
                img_key = "عام"
                std_key_global = ""

                # أبقار
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
                            "صيانة": "🌿 صيانة / جافة"
                        }.get(x, x), key="cattle_type"
                    )
                    c1_, c2_ = st.columns(2)
                    cattle_params = {}
                    with c1_:
                        if "حليب" in cattle_type:
                            cattle_params["milk_yield"] = st.number_input(
                                "🥛 إنتاج الحليب (كجم):", 5.0, 60.0, 20.0, 1.0, key="cattle_milk")
                        cattle_params["weight_kg"] = st.number_input(
                            "⚖️ الوزن (كجم):", 200.0, 900.0, 500.0, 25.0, key="cattle_wt")
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

                # أغنام
                with animal_tabs[1]:
                    st.markdown("### 🐏 احتياجات الأغنام — NRC 2007")
                    sg = st.radio("الجنس:", ["ذكر (تسمين)", "أنثى (أمهات)"],
                                  horizontal=True, key="sheep_gender")
                    is_male_s = "ذكر" in sg
                    if is_male_s:
                        sheep_type = st.selectbox(
                            "الحالة:",
                            ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد"],
                            format_func=lambda x: {
                                "تسمين_مكثف": "💪 تسمين مكثف",
                                "تسمين_عادي": "💪 تسمين عادي",
                                "حملان_تيد": "🐑 حملان تيد"
                            }.get(x, x), key="sheep_t_m"
                        )
                    else:
                        sheep_type = st.selectbox(
                            "الحالة:",
                            ["مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
                            format_func=lambda x: {
                                "مرضعات": "🍼 نعاج مرضعات",
                                "حامل_أخير": "🤰 حامل (4-5)",
                                "حامل_متوسط": "🤰 حامل (1-3)",
                                "صيانة": "🌿 صيانة"
                            }.get(x, x), key="sheep_t_f"
                        )
                    litter = 1
                    if sheep_type == "مرضعات":
                        litter = st.number_input("👶 عدد المواليد:", 1, 3, 1, 1, key="sheep_litter")
                    weight_s = st.number_input("⚖️ الوزن (كجم):", 15.0, 120.0, 50.0, 5.0, key="sheep_wt")
                    req_pre = get_sheep_requirements(sheep_type, is_male=is_male_s,
                                                     weight_kg=weight_s, litter_size=litter)
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

                # ماعز
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
                                "تيوس": "🐐 تيوس"
                            }.get(x, x), key="goat_t_m"
                        )
                    else:
                        goat_type = st.selectbox(
                            "الحالة:",
                            ["حلابة_عالي", "حلابة_متوسط", "حامل_أخير", "صيانة"],
                            format_func=lambda x: {
                                "حلابة_عالي": "🍼 حلابة إدرار عالي",
                                "حلابة_متوسط": "🍼 حلابة إدرار متوسط",
                                "حامل_أخير": "🤰 حامل أخير",
                                "صيانة": "🌿 صيانة"
                            }.get(x, x), key="goat_t_f"
                        )
                        if "حلابة" in goat_type:
                            milk_g = st.number_input("🥛 إنتاج الحليب (كجم):", 0.5, 8.0,
                                                     2.0, 0.25, key="goat_milk")
                    req_pre = get_goat_requirements(goat_type, is_male=is_male_g, milk_yield=milk_g)
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

                # إبل
                with animal_tabs[3]:
                    st.markdown("### 🐪 احتياجات الإبل — FAO 2010")
                    st.info("🐪 الإبل تحتاج بروتيناً أقل من الأبقار وأليافاً أكثر")
                    camel_type = st.selectbox(
                        "الحالة:", ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
                        format_func=lambda x: {
                            "نمو": "🐪 نمو (حوار)",
                            "تسمين": "💪 تسمين",
                            "حليب": "🍼 حلابة",
                            "سباق": "🏃 سباق",
                            "صيانة": "🌿 صيانة"
                        }.get(x, x), key="camel_type"
                    )
                    camel_wt = st.number_input("⚖️ الوزن (كجم):", 100.0, 800.0, 400.0, 25.0, key="camel_wt")
                    camel_milk = 5.0
                    if camel_type == "حليب":
                        camel_milk = st.number_input("🥛 إنتاج الحليب (لتر):", 2.0, 20.0, 5.0, 0.5, key="camel_milk")
                    req_pre = get_camel_requirements(camel_type, weight_kg=camel_wt, milk_yield=camel_milk)
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

                # خيول
                with animal_tabs[4]:
                    st.markdown("### 🐎 احتياجات الخيول — NRC 2007")
                    horse_type = st.selectbox(
                        "الحالة:",
                        ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار", "مرضعات", "صيانة"],
                        format_func=lambda x: {
                            "رياضة_مكثف": "🏇 رياضة مكثف",
                            "رياضة_عادي": "🏇 رياضة عادي",
                            "نمو_أمهار": "🐎 أمهار نمو",
                            "مرضعات": "🍼 فرسات مرضعات",
                            "صيانة": "🌿 صيانة"
                        }.get(x, x), key="horse_type"
                    )
                    horse_wt = st.number_input("⚖️ الوزن (كجم):", 200.0, 800.0, 450.0, 25.0, key="horse_wt")
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

                # دواجن
                with animal_tabs[5]:
                    st.markdown("### 🐔 احتياجات الدواجن — NRC + Ross 308")
                    poultry_strain = st.radio("السلالة:", ["لاحم", "بياض"],
                                              horizontal=True, key="poultry_strain")
                    poultry_age = st.number_input("العمر (أسبوع):", 1, 20, 1, 1, key="poultry_age")
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
                        if "بادي" in req_pre.name_ar:
                            std_key_global = "دواجن_بادي"
                        elif "نامي" in req_pre.name_ar:
                            std_key_global = "دواجن_نامي"
                        elif "بياض" in req_pre.name_ar:
                            std_key_global = "دواجن_بياض"
                        else:
                            std_key_global = "دواجن_ناهي"

                # سمان
                with animal_tabs[6]:
                    st.markdown("### 🦆 احتياجات السمان")
                    quail_strain = st.radio("النوع:", ["تسمين", "بياض"],
                                            horizontal=True, key="quail_strain")
                    quail_age = st.number_input("العمر (أسبوع):", 1, 8, 1, 1, key="quail_age")
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
                        std_key_global = "سمان_بياض" if quail_strain == "بياض" else "سمان_بادي"

                # أسماك
                with animal_tabs[7]:
                    st.markdown("### 🐟 احتياجات الأسماك")
                    fish_species = st.selectbox(
                        "النوع:", ["البلطي النيلي", "القرموط الأفريقي", "الكارب"], key="fish_sp")
                    fish_stage = st.selectbox("المرحلة:", ["بادئ زريعة", "نمو", "تسمين"], key="fish_stage")
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
                        if "بادئ" in fish_stage or "زريعة" in fish_stage:
                            std_key_global = "أسماك_بادئ"
                        elif "نمو" in fish_stage:
                            std_key_global = "أسماك_نمو"
                        else:
                            std_key_global = "أسماك_تسمين"

                formulation_ready = bool(animal_choice and requirement)

                if not formulation_ready:
                    st.warning("⚠️ اختر حيواناً وفعّل خيار ✅ الاعتماد للمتابعة")
                    st.info("👉 يمكنك التنقل إلى باقي التبويبات أعلاه دون اختيار حيوان.")
                    if st.session_state.get("last_formulation_result"):
                        st.markdown("---")
                        st.markdown("### 📋 آخر نتيجة تركيب محفوظة")
                        prev = st.session_state["last_formulation_result"]
                        prev_ctx = st.session_state.get("last_formulation_context", {})
                        st.info(f"🐾 الحيوان: {prev_ctx.get('animal_choice','—')} | "
                                f"الحالة: {prev_ctx.get('requirement_name','—')} | "
                                f"أساس الحساب: {prev_ctx.get('basis_label','—')}")
                        st.markdown("#### 🌾 المكونات:")
                        for ing, pct in prev["formula"].items():
                            st.markdown(
                                f'<div class="formula-item">▪️ <b>{ing}:</b> '
                                f'{pct:.2f}% ({pct*10:.1f} كجم/طن)</div>',
                                unsafe_allow_html=True
                            )
                        st.metric("💰 التكلفة للطن:", f"${prev['cost']:.2f}")

                if formulation_ready:
                    st.markdown(
                        f'<div class="section-title">🎯 المختار: {animal_choice} — {requirement.name_ar}</div>',
                        unsafe_allow_html=True
                    )
                    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
                    info_col1.metric("🧬 DP", f"{requirement.DP}%")
                    info_col2.metric("🧬 CP", f"{requirement.CP}%")
                    info_col3.metric("🌽 SE", f"{requirement.SE}")
                    info_col4.metric("🌾 NDF", f"{requirement.NDF}%")
                    st.info(f"📝 {requirement.note} | **أساس الحساب: "
                            f"{'DP (مهضوم)' if use_dp else 'CP (خام)'}**")

                    oil_std_info = get_oil_standard(std_key_global)
                    st.markdown('<div class="section-title">🌰 معيار الزيوت لهذا الحيوان</div>',
                                unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="oil-info-card">
                    <b>📊 الحدود القياسية للزيوت:</b><br>
                    ▪️ الحد الأقصى: <b>{oil_std_info['max']}%</b><br>
                    ▪️ المثالي: <b>{oil_std_info['optimal']}%</b><br>
                    ▪️ المرجع: <b>{oil_std_info['source']}</b><br>
                    <small>💡 كل 1% زيت ≈ 90 kcal/kg علف</small>
                    </div>
                    """, unsafe_allow_html=True)

                    requester_name = st.text_input(
                        "👤 اسم طالب العلفة (سيظهر في التقرير):",
                        placeholder="مثال: مزرعة الأمل — أحمد محمد", key="requester"
                    )

                    st.markdown('<div class="section-title">🌾 اختيار المكونات</div>',
                                unsafe_allow_html=True)
                    selected_ingredients = []
                    ingredient_prices = {}

                    for cat_name, items in BIG_FEEDS_LIBRARY.items():
                        is_expanded = ("الحبوب" in cat_name or "الأكساب" in cat_name or "الزيوت" in cat_name)
                        with st.expander(f"📁 {cat_name}", expanded=is_expanded):
                            sub_cols = st.columns(3)
                            for idx, (ing_name, ing_data) in enumerate(items.items()):
                                with sub_cols[idx % 3]:
                                    default_check = ing_name in [
                                        "ملح الطعام", "الحجر الجيري",
                                        "فوسفات ثنائي الكالسيوم", "مضاد سموم فطرية"
                                    ]
                                    if animal_choice in ["أغنام", "ماعز", "أبقار", "إبل"]:
                                        default_check = default_check or (ing_name == "بيكربونات الصوديوم")
                                    if animal_choice in ["دواجن", "سمان"]:
                                        default_check = default_check or ("بريمكس" in ing_name)

                                    if cat_name == "🌰 الزيوت النباتية والحيوانية":
                                        st.markdown(f"**{ing_name}**")
                                        st.caption(f"⚡ SE={ing_data.get('SE',0):.0f} | "
                                                   f"EE=100% | "
                                                   f"{ing_data.get('desc','')[:60]}")
                                        checked = st.checkbox(
                                            "إضافة", value=False,
                                            key=f"feed_{animal_choice}_{ing_name}")
                                    else:
                                        checked = st.checkbox(
                                            ing_name, value=default_check,
                                            key=f"feed_{animal_choice}_{ing_name}")

                                    current_live_price = live_prices.get(ing_name, 350.0)
                                    if is_owner():
                                        price_input = st.number_input(
                                            f"السعر للطن ({ing_name}) $:",
                                            min_value=5.0, value=float(current_live_price),
                                            key=f"price_{animal_choice}_{ing_name}")
                                    else:
                                        st.markdown(f"💰 السعر الحالي: **`${current_live_price:.2f}`** / طن")
                                        price_input = current_live_price

                                    if checked:
                                        selected_ingredients.append(ing_name)
                                        ingredient_prices[ing_name] = price_input

                    st.markdown("---")

                    col_btn1, col_btn2 = st.columns([0.7, 0.3])
                    with col_btn1:
                        run_clicked = st.button(
                            "🚀 تشغيل المحرك الذكي — مطابقة شاملة (فرق ≤ 0.3%)",
                            type="primary", use_container_width=True, key="run_smart")
                    with col_btn2:
                        if st.session_state.get("last_formulation_result"):
                            if st.button("🗑️ مسح النتائج السابقة",
                                         use_container_width=True, key="clear_results"):
                                st.session_state["last_formulation_result"] = None
                                st.session_state["last_formulation_context"] = None
                                st.rerun()

                    if run_clicked:
                        if len(selected_ingredients) < 3:
                            st.error("⚠️ اختر 3 مكونات على الأقل")
                        else:
                            auto_salts = auto_add_salts_and_minerals(animal_choice, requirement)
                            for sname, spct in auto_salts.items():
                                if sname not in selected_ingredients:
                                    selected_ingredients.append(sname)
                                    ingredient_prices[sname] = live_prices.get(sname, 300.0)

                            custom_standard = requirement_to_standard(requirement)

                            with st.spinner(f"⏳ جاري التركيب على أساس {basis_code}..."):
                                # ✅ استدعاء صحيح باستخدام standard_key (اسم المعامل الرسمي)
                                result = auto_formulate_smart(
                                    selected_ingredients, ingredient_prices, custom_standard,
                                    standard_key=std_key_global,
                                    tolerance=0.3, max_iterations=50, basis=basis_code
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
                                st.session_state["active_animal_img"] = ANIMAL_IMAGES.get(
                                    img_key, ANIMAL_IMAGES["عام"])
                                st.session_state["active_stage_title"] = (
                                    f"{animal_choice} — {requirement.name_ar}")
                            else:
                                st.error(f"❌ {result['message']}")

                    # عرض النتائج المحفوظة
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

                        compare_rows = []
                        compare_scores = []
                        labels = {
                            "CP": "بروتين خام CP", "DP": "بروتين مهضوم DP",
                            "SE": "معادل النشاء SE", "NDF": "ألياف NDF",
                            "ADF": "ألياف ADF", "EE": "دهن EE", "ASH": "رماد ASH",
                            "Ca": "كالسيوم Ca", "P": "فسفور P",
                        }
                        for k, sv in custom_standard.items():
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
                            })

                        overall = get_overall_rating(compare_scores)
                        perfect = result.get("perfect_match", False)

                        if perfect:
                            st.success(f"🎯 **مطابقة كاملة!** جميع العناصر مطابقة — على أساس {basis_label}")
                        else:
                            st.success(f"✅ تم التركيب — على أساس {basis_label}")

                        st.info(f"🔁 التكرارات: {result['iterations']} | "
                                f"التقييم العام: **{overall['label']}** ({overall['score']:.0f}%)")

                        e1, e2, e3, e4 = st.columns(4)
                        if basis_label == "DP":
                            e1.metric("خطأ DP", f"{result['dp_error']:.3f}%")
                        else:
                            e1.metric("خطأ CP", f"{result.get('cp_error', 0):.3f}%")
                        e2.metric("خطأ SE", f"{result['se_error']:.3f}")
                        e3.metric("خطأ NDF", f"{result['ndf_error']:.2f}%")
                        e4.metric("خطأ Ca", f"{result['ca_error']:.3f}%")

                        st.markdown("### 📊 جدول المقارنة الشامل")
                        st.dataframe(pd.DataFrame(compare_rows),
                                     use_container_width=True, hide_index=True)

                        st.markdown("### 🌰 تقييم الزيوت")
                        if total_oil > 0:
                            if total_oil > oil_std["max"]:
                                st.error(f"⚠️ **تجاوز الحد الأقصى!** {total_oil:.2f}% > {oil_std['max']}%")
                            elif total_oil > oil_std["optimal"] * 1.2:
                                st.warning(f"⚡ مرتفع قليلاً ({total_oil:.2f}%) — المثالي {oil_std['optimal']}%")
                            else:
                                st.success(f"✅ مطابق — {total_oil:.2f}% (المثالي {oil_std['optimal']}%)")
                            st.caption(f"📖 المرجع: {oil_std['source']}")
                            oils_used = [(ing, pct) for ing, pct in formula.items()
                                         if ing in get_oil_ingredients()]
                            for ing, pct in oils_used:
                                kcal = pct * 90
                                st.markdown(
                                    f'<div class="oil-item">🌰 <b>{ing}:</b> '
                                    f'{pct:.2f}% | طاقة ≈ {kcal:.0f} kcal/kg</div>',
                                    unsafe_allow_html=True
                                )
                        else:
                            st.info("ℹ️ لم تستخدم أي زيوت")

                        st.markdown("#### 🌾 المكونات:")
                        for ing, pct in formula.items():
                            st.markdown(
                                f'<div class="formula-item">▪️ <b>{ing}:</b> '
                                f'{pct:.2f}% ({pct*10:.1f} كجم/طن)</div>',
                                unsafe_allow_html=True
                            )

                        st.metric("💰 التكلفة الفعلية للطن:",
                                  f"${cost:.2f} ({cost*ctx['local_rate']:,.0f} {ctx['local_sym']})")

                        # ═══ 📈 الرسوم البيانية الملونة ═══
                        st.markdown('<div class="section-title">📈 الرسوم البيانية التحليلية</div>',
                                    unsafe_allow_html=True)

                        chart1, chart2 = st.columns(2)
                        with chart1:
                            bar_buf = create_colorful_bar_chart(custom_standard, actual)
                            if bar_buf:
                                st.image(bar_buf.getvalue(),
                                         caption="مقارنة العناصر: المعيار vs المحسوب",
                                         use_container_width=True)
                        with chart2:
                            pie_buf = create_colorful_pie_chart(formula)
                            if pie_buf:
                                st.image(pie_buf.getvalue(),
                                         caption="توزيع المكونات في الخلطة",
                                         use_container_width=True)

                        chart3, chart4 = st.columns(2)
                        with chart3:
                            radar_buf = create_radar_chart(custom_standard, actual)
                            if radar_buf:
                                st.image(radar_buf.getvalue(),
                                         caption="الرادار: نسب الإنجاز %",
                                         use_container_width=True)
                        with chart4:
                            gauge_buf = create_gauge_chart(overall["score"])
                            if gauge_buf:
                                st.image(gauge_buf.getvalue(),
                                         caption="مؤشر التقييم العام",
                                         use_container_width=True)

                        st.markdown("### 📥 تحميل التقارير")
                        dl1, dl2 = st.columns(2)
                        with dl1:
                            try:
                                pdf = pdf_gen.generate_report(
                                    formula=formula,
                                    requirement=ctx["requirement"],
                                    animal_type=ctx["animal_type"],
                                    breed=ctx["requirement_name"],
                                    cost=cost,
                                    city=ctx["city"],
                                    local_cost=cost * ctx["local_rate"],
                                    local_sym=ctx["local_sym"],
                                    requester_name=ctx["requester_name"],
                                    protein_basis=basis_label,
                                    standard_key=ctx["std_key_global"],
                                    include_charts=True,
                                )
                                fname = (f"TaworNology_{ctx['animal_type']}_"
                                         f"{datetime.now():%Y%m%d_%H%M}.pdf")
                                st.download_button("📥 تحميل PDF", pdf, file_name=fname,
                                                   mime="application/pdf",
                                                   use_container_width=True)
                            except Exception as e:
                                st.error(f"⚠️ خطأ PDF: {e}")

                        with dl2:
                            try:
                                xl = export_comparison_to_excel(
                                    custom_standard, actual,
                                    ctx["requester_name"], ctx["animal_type"],
                                    ctx["requirement_name"], formula,
                                    ctx["std_key_global"])
                                if xl:
                                    fname = (f"TaworNology_{ctx['animal_type']}_"
                                             f"{datetime.now():%Y%m%d_%H%M}.xlsx")
                                    st.download_button("📊 تحميل Excel", xl, file_name=fname,
                                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                                       use_container_width=True)
                            except Exception as e:
                                st.error(f"⚠️ خطأ Excel: {e}")

                        if PLOTLY_AVAILABLE and len(formula) > 1:
                            try:
                                colors = ['#e53935', '#8e24aa', '#3949ab', '#1e88e5',
                                          '#00897b', '#43a047', '#7cb342', '#fdd835',
                                          '#fb8c00', '#6d4c41']
                                fig = px.pie(values=list(formula.values()),
                                             names=list(formula.keys()),
                                             title=f"توزيع المكونات — {ctx['animal_choice']}",
                                             color_discrete_sequence=colors)
                                fig.update_traces(textposition='inside',
                                                  textinfo='percent+label')
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception:
                                pass

            except Exception as e:
                st.error(f"⚠️ خطأ في تبويب التركيب: {e}")
                with st.expander("تفاصيل"):
                    st.code(traceback.format_exc())

        # ═══════ مختبر التحليل ═══════
        with sub_tab_analyzer:
            try:
                st.markdown('<div class="section-title">🔬 مختبر فحص وتحليل الخلطات الجاهزة</div>',
                            unsafe_allow_html=True)
                st.write("أدخل أوزان مكونات خلطتك الحالية بالكيلوجرام، وسيقوم المختبر بتحليلها برمجياً.")

                st.subheader("🎯 حدد الحيوان والغرض المستهدف للمقارنة:")
                col_lab_animal, col_lab_stage = st.columns(2)
                with col_lab_animal:
                    target_animal = st.selectbox(
                        "اختر الفصيل:",
                        ["أبقار", "أغنام", "ماعز", "خيول", "إبل",
                         "دواجن لاحم", "دواجن بياض", "سمان", "أسماك"],
                        key="lab_target_animal")
                with col_lab_stage:
                    if target_animal in ["أبقار", "أغنام", "ماعز", "خيول", "إبل"]:
                        production_type_lab = st.selectbox(
                            "مرحلة الإنتاج:", ["تسمين", "حليب/إدرار", "حمل/دفع غذائي", "صيانة"],
                            key="lab_prod_ruminant")
                    elif target_animal in ["دواجن لاحم", "دواجن بياض", "سمان"]:
                        production_type_lab = st.selectbox(
                            "مرحلة الإنتاج:", ["بادي", "نامي", "ناهي", "بياض"],
                            key="lab_prod_poultry")
                    else:
                        production_type_lab = st.selectbox(
                            "مرحلة الإنتاج:", ["نمو", "تسمين نهائي"], key="lab_prod_fish")

                cp_requirements = {
                    ("أبقار", "تسمين"): 12.0, ("أبقار", "حليب/إدرار"): 14.0,
                    ("أبقار", "حمل/دفع غذائي"): 11.0, ("أبقار", "صيانة"): 9.0,
                    ("أغنام", "تسمين"): 13.0, ("أغنام", "حليب/إدرار"): 14.5,
                    ("أغنام", "حمل/دفع غذائي"): 11.5, ("أغنام", "صيانة"): 8.5,
                    ("ماعز", "تسمين"): 12.5, ("ماعز", "حليب/إدرار"): 14.0,
                    ("ماعز", "حمل/دفع غذائي"): 11.0, ("ماعز", "صيانة"): 8.0,
                    ("خيول", "تسمين"): 11.0, ("خيول", "حليب/إدرار"): 12.5,
                    ("خيول", "حمل/دفع غذائي"): 11.5, ("خيول", "صيانة"): 9.0,
                    ("إبل", "تسمين"): 12.0, ("إبل", "حليب/إدرار"): 13.5,
                    ("إبل", "حمل/دفع غذائي"): 11.0, ("إبل", "صيانة"): 9.0,
                    ("دواجن لاحم", "بادي"): 23.0, ("دواجن لاحم", "نامي"): 21.0,
                    ("دواجن لاحم", "ناهي"): 19.0, ("دواجن لاحم", "بياض"): 18.0,
                    ("دواجن بياض", "بادي"): 20.0, ("دواجن بياض", "نامي"): 18.0,
                    ("دواجن بياض", "ناهي"): 16.5, ("دواجن بياض", "بياض"): 16.0,
                    ("سمان", "بادي"): 24.0, ("سمان", "نامي"): 22.0,
                    ("سمان", "ناهي"): 20.0, ("سمان", "بياض"): 18.0,
                    ("أسماك", "نمو"): 32.0, ("أسماك", "تسمين نهائي"): 28.0,
                }

                suggested_cp = cp_requirements.get((target_animal, production_type_lab), 15.0)
                suggested_dp = suggested_cp * 0.80

                analysis_basis = st.radio(
                    "أساس التحليل:", ["بروتين مهضوم (DP)", "بروتين خام (CP)"],
                    horizontal=True, key="lab_analysis_basis")

                if analysis_basis == "بروتين مهضوم (DP)":
                    target_value = st.number_input(
                        "النسبة المستهدفة (DP %)", min_value=5.0, max_value=50.0,
                        value=float(suggested_dp), step=0.1, key="lab_target_dp")
                    st.caption(f"البروتين الخام المقترح ≈ {suggested_cp:.1f}%")
                else:
                    target_value = st.number_input(
                        "النسبة المستهدفة (CP %)", min_value=5.0, max_value=50.0,
                        value=float(suggested_cp), step=0.1, key="lab_target_cp")

                st.markdown("---")
                st.subheader("📥 أدخل أوزان المكونات بالكيلوجرام:")
                lab_user_inputs = {}
                all_library_ingredients = []
                for cat_name, items in BIG_FEEDS_LIBRARY.items():
                    for ing_name in items.keys():
                        all_library_ingredients.append(ing_name)

                col_input1, col_input2, col_input3 = st.columns(3)
                total_ing_count = len(all_library_ingredients)
                segment = total_ing_count // 3 + 1

                with col_input1:
                    for ing_name in all_library_ingredients[:segment]:
                        lab_user_inputs[ing_name] = st.number_input(
                            f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0,
                            step=5.0, key=f"lab_in_{ing_name}")
                with col_input2:
                    for ing_name in all_library_ingredients[segment:segment * 2]:
                        lab_user_inputs[ing_name] = st.number_input(
                            f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0,
                            step=5.0, key=f"lab_in_{ing_name}")
                with col_input3:
                    for ing_name in all_library_ingredients[segment * 2:]:
                        lab_user_inputs[ing_name] = st.number_input(
                            f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0,
                            step=5.0, key=f"lab_in_{ing_name}")

                st.markdown("---")
                if st.button("🧪 تشغيل التحليل المخبري", type="primary",
                             use_container_width=True, key="lab_run_button"):
                    lab_total_weight = sum(lab_user_inputs.values())
                    if lab_total_weight <= 0:
                        st.warning("⚠️ الرجاء إدخال أوزان أكبر من الصفر.")
                    else:
                        calculated_total_cp = 0.0
                        calculated_total_dp = 0.0
                        calculated_total_se = 0.0
                        entered_components_summary = []
                        for ing_name, weight in lab_user_inputs.items():
                            if weight > 0:
                                pct = weight / lab_total_weight
                                ing_cp = 0.0
                                ing_dc = 0.0
                                ing_se = 0.0
                                for cat, items in BIG_FEEDS_LIBRARY.items():
                                    if ing_name in items:
                                        ing_cp = items[ing_name].get("CP", 0.0)
                                        ing_dc = items[ing_name].get("DC", 0.0)
                                        ing_se = items[ing_name].get("SE", 0.0)
                                calculated_total_cp += pct * ing_cp
                                calculated_total_dp += pct * (ing_cp * ing_dc)
                                calculated_total_se += pct * ing_se
                                entered_components_summary.append({
                                    "المادة العلفية": ing_name,
                                    "الوزن المدخل": f"{weight:.1f} كجم",
                                    "النسبة المئوية": f"{pct * 100:.2f}%"
                                })
                        st.success("🔬 تم فحص العينة وتحليل المحتوى الغذائي بنجاح!")
                        st.markdown(f"### ⚖️ إجمالي وزن الخلطة: **{lab_total_weight:.1f} كجم**")
                        st.write("#### 📊 نسب توزيع المكونات:")
                        st.table(pd.DataFrame(entered_components_summary))

                        st.markdown("---")
                        st.write("#### 🔬 تقرير الفحص المخبري النهائي:")
                        if analysis_basis == "بروتين مهضوم (DP)":
                            comparison_value = calculated_total_dp
                            status_label = "✅ مطابق وممتاز" if comparison_value >= target_value else "⚠️ ناقص"
                        else:
                            comparison_value = calculated_total_cp
                            status_label = "✅ مطابق وممتاز" if comparison_value >= target_value else "⚠️ ناقص"

                        st.write(f"🔬 البروتين الخام (CP): **{calculated_total_cp:.2f}%**")
                        st.write(f"🔬 البروتين المهضوم (DP): **{calculated_total_dp:.2f}%**")

                        lab_report_data = [
                            {"العنصر": "البروتين المهضوم (DP)",
                             "المحسوب": f"{calculated_total_dp:.2f}%",
                             "الاحتياج": f"{target_value:.1f}%" if analysis_basis == "بروتين مهضوم (DP)" else "-",
                             "التقييم": status_label if analysis_basis == "بروتين مهضوم (DP)" else "-"},
                            {"العنصر": "البروتين الخام (CP)",
                             "المحسوب": f"{calculated_total_cp:.2f}%",
                             "الاحتياج": f"{target_value:.1f}%" if analysis_basis == "بروتين خام (CP)" else "-",
                             "التقييم": status_label if analysis_basis == "بروتين خام (CP)" else "-"},
                            {"العنصر": "معادل النشاء (SE)",
                             "المحسوب": f"{calculated_total_se:.2f} وحدة",
                             "الاحتياج": "مرن",
                             "التقييم": "تحليل طاقة كلي"},
                        ]
                        st.table(pd.DataFrame(lab_report_data))

                        st.write("📊 التمثيل البياني:")
                        graph_data = {k: v for k, v in lab_user_inputs.items() if v > 0}
                        if graph_data and PLOTLY_AVAILABLE:
                            fig = px.bar(x=list(graph_data.keys()),
                                         y=list(graph_data.values()),
                                         labels={'x': 'المادة', 'y': 'الوزن (كجم)'},
                                         title="توزيع أوزان المواد المختبرة",
                                         color_discrete_sequence=['#2e7d32'])
                            st.plotly_chart(fig, use_container_width=True)

                        lab_share_text = (f"نتيجة مختبر تاور:\n"
                                          f"الحيوان: {target_animal} - {production_type_lab}\n"
                                          f"البروتين: {comparison_value:.2f}%\n"
                                          f"المعيار: {target_value:.1f}%")
                        encoded_lab = urllib.parse.quote(lab_share_text)
                        st.markdown(
                            f'<a href="https://wa.me/?text={encoded_lab}" target="_blank">'
                            f'<button style="background-color:#25D366; color:white; '
                            f'padding:10px; border-radius:5px;">'
                            f'📲 مشاركة عبر واتساب</button></a>',
                            unsafe_allow_html=True)

            except Exception as e:
                st.error(f"⚠️ خطأ في المختبر: {e}")

    except Exception as e:
        st.error(f"⚠️ خطأ في تبويب النمذجة: {e}")


# ═══════════════════════════════════════════════════════════════════════
# تبويب مكتبة الزيوت
# ═══════════════════════════════════════════════════════════════════════
with tab_map["🌰 مكتبة الزيوت"]:
    try:
        st.markdown('<div class="section-title">🌰 مكتبة الزيوت النباتية والحيوانية</div>',
                    unsafe_allow_html=True)
        st.write("جميع الزيوت المعتمدة وفق NRC، INRA، Ross 308، FAO.")

        st.markdown("### 📊 الحدود القياسية للزيوت حسب الحيوان")
        oil_std_rows = []
        for key, val in MAX_OIL_PERCENTAGE.items():
            oil_std_rows.append({
                "الحيوان/الحالة": key,
                "الحد الأقصى %": f"{val['max']}%",
                "المثالي %": f"{val['optimal']}%",
                "المرجع": val["source"],
            })
        st.dataframe(pd.DataFrame(oil_std_rows), use_container_width=True, hide_index=True)

        st.markdown("### 🌰 الزيوت المتوفرة")
        oils = get_oil_ingredients()
        for category, oil_list in OIL_CATEGORIES.items():
            st.markdown(f"#### {category}")
            cat_oils = [(name, oils[name]) for name in oil_list if name in oils]
            if cat_oils:
                for ing_name, ing_data in cat_oils:
                    with st.expander(f"🌰 {ing_name}"):
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.metric("معادل النشاء", f"{ing_data.get('SE', 0):.0f}")
                            st.metric("الدهن", "100%")
                        with c2:
                            st.metric("طاقة تقديرية", f"{ing_data.get('SE', 0) * 41:.0f} kcal/kg")
                            st.metric("سعر تقريبي",
                                      f"${get_market_prices('السودان', 'الخرطوم').get(ing_name, 0):.0f}/طن")
                        with c3:
                            st.metric("أقصى للدواجن", f"{ing_data.get('max_poultry', 'N/A')}%")
                            st.metric("أقصى للمجترات", f"{ing_data.get('max_ruminant', 'N/A')}%")
                        st.info(f"📝 {ing_data.get('desc', '')}")
                        st.caption(f"📖 المرجع: {ing_data.get('source', 'NRC')}")

    except Exception as e:
        st.error(f"⚠️ خطأ: {e}")


# ═══════════════════════════════════════════════════════════════════════
# تبويب بدائل الحليب
# ═══════════════════════════════════════════════════════════════════════
with tab_map["🍼 بدائل الحليب"]:
    try:
        st.markdown('<div class="section-title">🍼 مختبر بدائل الحليب</div>',
                    unsafe_allow_html=True)

        milk_replacer_standards = {
            "عجول (Calves)": {"CP": 24.0, "Fat": 24.0, "Lactose": 45.0, "notes": "عمر 1-6 أسابيع"},
            "حملان (Lambs)": {"CP": 24.0, "Fat": 24.0, "Lactose": 40.0, "notes": "≥ 24% دهن"},
            "جديان (Goat Kids)": {"CP": 24.0, "Fat": 24.0, "Lactose": 42.0, "notes": "بديل الجديان"},
            "إبل (Camel Calves)": {"CP": 26.0, "Fat": 28.0, "Lactose": 38.0, "notes": "بروتين ودهن أعلى"},
            "أمهار (Foals)": {"CP": 22.0, "Fat": 20.0, "Lactose": 45.0, "notes": "توازن للخيول"},
        }
        milk_replacer_ingredients = {
            "حليب مجفف منزوع الدسم": {"CP": 34.0, "Fat": 1.0, "price": 3200},
            "حليب مجفف كامل الدسم": {"CP": 26.0, "Fat": 28.0, "price": 3800},
            "شرش حليب مجفف": {"CP": 12.0, "Fat": 1.5, "price": 1800},
            "بروتين شرش WPC 80%": {"CP": 80.0, "Fat": 5.0, "price": 8500},
            "كازين": {"CP": 85.0, "Fat": 2.0, "price": 9000},
            "مركز بروتين صويا": {"CP": 66.0, "Fat": 1.0, "price": 2800},
            "زيت جوز الهند": {"CP": 0.0, "Fat": 100.0, "price": 2200},
            "زيت النخيل": {"CP": 0.0, "Fat": 100.0, "price": 1200},
            "مالتودكسترين": {"CP": 0.0, "Fat": 0.0, "price": 900},
            "لاكتوز نقي": {"CP": 0.0, "Fat": 0.0, "price": 1400},
            "بريمكس فيتامينات": {"CP": 0.0, "Fat": 0.0, "price": 6500},
            "كالسيوم كربونات": {"CP": 0.0, "Fat": 0.0, "price": 200},
            "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "Fat": 0.0, "price": 1100},
            "ملح طعام": {"CP": 0.0, "Fat": 0.0, "price": 150},
        }

        mr1, mr2 = st.columns(2)
        with mr1:
            mr_animal = st.selectbox("نوع الحيوان:", list(milk_replacer_standards.keys()), key="mr_a")
            mr_volume = st.number_input("الكمية (كجم):", 1.0, 10000.0, 100.0, 10.0, key="mr_v")
            mr_req = st.text_input("اسم طالب التركيب:", key="mr_r")
        with mr2:
            std_mr = milk_replacer_standards[mr_animal]
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
        for i, (name, data) in enumerate(milk_replacer_ingredients.items()):
            with mr_cols[i % 3]:
                default_mr = name in [
                    "حليب مجفف منزوع الدسم", "حليب مجفف كامل الدسم",
                    "شرش حليب مجفف", "زيت جوز الهند", "زيت النخيل",
                    "بريمكس فيتامينات", "كالسيوم كربونات",
                    "فوسفات ثنائي الكالسيوم", "ملح طعام"
                ]
                if st.checkbox(f"{name} — ${data['price']}",
                               value=default_mr, key=f"mr_{name}"):
                    mr_selected.append(name)

        if st.button("🧪 تشغيل التركيب", type="primary",
                     use_container_width=True, key="mr_run"):
            if len(mr_selected) < 3:
                st.warning("⚠️ اختر 3 مكونات على الأقل")
            elif not SCIPY_AVAILABLE:
                st.error("⚠️ SCIPY غير متوفرة")
            else:
                std = milk_replacer_standards[mr_animal]
                n = len(mr_selected)
                c = [milk_replacer_ingredients[i]["price"] for i in mr_selected]
                A_eq = [
                    [1.0] * n,
                    [milk_replacer_ingredients[i]["CP"] for i in mr_selected],
                    [milk_replacer_ingredients[i]["Fat"] for i in mr_selected]
                ]
                b_eq = [100.0, std["CP"] * 100, std["Fat"] * 100]
                try:
                    res = linprog(c, A_eq=A_eq, b_eq=b_eq,
                                  bounds=[(0, 100)] * n, method='highs')
                    if res.success:
                        st.success(f"✅ تم التركيب لـ ({mr_animal})")
                        for idx, ing in enumerate(mr_selected):
                            pct = res.x[idx]
                            if pct > 0.001:
                                kg = pct * mr_volume / 100.0
                                st.markdown(
                                    f'<div class="formula-item">▪️ <b>{ing}:</b> '
                                    f'{pct:.2f}% ({kg:.2f} كجم)</div>',
                                    unsafe_allow_html=True
                                )
                        st.metric("💰 التكلفة لـ 100 كجم:", f"${res.fun / 100:.2f}")
                        st.metric("💰 التكلفة لكل كجم:", f"${res.fun / 10000:.3f}")
                    else:
                        st.error("❌ تعذر التركيب")
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")

    except Exception as e:
        st.error(f"⚠️ خطأ: {e}")


# ═══════════════════════════════════════════════════════════════════════
# تبويب المختبر الذكي (OCR)
# ═══════════════════════════════════════════════════════════════════════
with tab_map["📷 المختبر الذكي"]:
    try:
        st.markdown('<div class="section-title">📷 المختبر الذكي (OCR)</div>',
                    unsafe_allow_html=True)
        if not OCR_AVAILABLE:
            st.error("⚠️ مكتبة pytesseract غير مثبتة")
            st.code("pip install pytesseract opencv-python-headless", language="bash")
        else:
            uploaded = st.file_uploader("📤 ارفع صورة:", type=["jpg", "jpeg", "png"])
            if uploaded:
                st.image(uploaded, caption="الصورة", use_container_width=True)
                if st.button("🔍 تحليل", type="primary", use_container_width=True):
                    with st.spinner("جاري التحليل..."):
                        try:
                            nparr = np.frombuffer(uploaded.read(), np.uint8)
                            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                            if img is None:
                                st.error("❌ تعذر قراءة الصورة")
                            else:
                                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                                gray = cv2.medianBlur(gray, 3)
                                text = pytesseract.image_to_string(gray, lang='ara+eng',
                                                                   config=r'--oem 3 --psm 6')
                                st.success("✅ تم استخراج النص")
                                st.text(text)

                                ingredients = {}
                                for line in text.split('\n'):
                                    line = line.strip()
                                    if len(line) < 3:
                                        continue
                                    match = re.search(
                                        r'([\u0600-\u06FFa-zA-Z\s]+?)[\s:\-=]+(\d+\.?\d*)\s*%',
                                        line)
                                    if match:
                                        name = match.group(1).strip()
                                        val = float(match.group(2))
                                        if 0.1 < val <= 100 and len(name) > 2:
                                            for cat in BIG_FEEDS_LIBRARY.values():
                                                for ing_name in cat:
                                                    if ing_name in name or name in ing_name:
                                                        ingredients[ing_name] = val
                                                        break

                                if ingredients:
                                    st.markdown("### 📊 المكونات المستخرجة:")
                                    st.dataframe(pd.DataFrame([
                                        {"المادة": k, "النسبة": f"{v:.2f}%"}
                                        for k, v in ingredients.items()
                                    ]), use_container_width=True, hide_index=True)
                                    nutrients = compute_formula_nutrients(ingredients)
                                    n1, n2, n3, n4 = st.columns(4)
                                    n1.metric("CP", f"{nutrients['CP']:.2f}%")
                                    n2.metric("DP", f"{nutrients['DP']:.2f}%")
                                    n3.metric("SE", f"{nutrients['SE']:.2f}")
                                    n4.metric("NDF", f"{nutrients['NDF']:.2f}%")
                        except Exception as e:
                            st.error(f"❌ خطأ: {e}")
    except Exception as e:
        st.error(f"⚠️ خطأ: {e}")


# ═══════════════════════════════════════════════════════════════════════
# تبويب تصميم الحظائر 3D
# ═══════════════════════════════════════════════════════════════════════
with tab_map["🏗️ تصميم الحظائر 3D"]:
    try:
        st.markdown('<div class="section-title">🏗️ مصمم الحظائر العلمي ثلاثي الأبعاد</div>',
                    unsafe_allow_html=True)
        st.info("🌐 هذا التبويب **متاح للجميع** (مالك وزائر) — معايير MWPS-1، FAO 2012، ASABE.")

        c1, c2, c3 = st.columns(3)
        with c1:
            barn_animal = st.selectbox(
                "🐾 نوع الحيوان:", list(BARN_DESIGN_STANDARDS.keys()),
                format_func=lambda k: BARN_DESIGN_STANDARDS[k]["name_ar"],
                key="barn_animal")
        with c2:
            barn_count = st.number_input("🔢 العدد الكلي:", min_value=1, max_value=100000,
                                          value=1000, step=50, key="barn_count")
        with c3:
            barn_system = st.selectbox(
                "🏠 نظام الإيواء:",
                ["أرضي مفتوح (Floor)", "بطاريات (Cages)"], key="barn_system")

        system_multiplier = 1.0
        if "بطاريات" in barn_system and barn_animal in ["دواجن_لاحم", "دواجن_بياض", "سمان"]:
            system_multiplier = 0.55

        dims = calculate_barn_dimensions(barn_animal, barn_count)
        if dims and system_multiplier != 1.0:
            dims["total_area_m2"] = round(dims["total_area_m2"] * system_multiplier, 2)
            dims["length_m"] = round(dims["total_area_m2"] / dims["width_m"], 2)

        if dims:
            st.session_state["barn_last_dims"] = dims

            st.markdown("### 📊 مواصفات الحظيرة المحسوبة")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("📏 المساحة الكلية", f"{dims['total_area_m2']} م²")
            k2.metric("📐 الأبعاد (ط × ع)", f"{dims['length_m']} × {dims['width_m']} م")
            k3.metric("🏔️ ارتفاع القمة", f"{dims['ridge_height_m']} م")
            k4.metric("📦 الحجم الداخلي", f"{dims['volume_m3']} م³")

            k5, k6, k7, k8 = st.columns(4)
            k5.metric("🍽️ عدد المعالف", dims["feeders_count"])
            k6.metric("📏 طول المعالف", f"{dims['total_feeder_length_m']} م")
            k7.metric("💧 عدد السقايات", dims["drinkers_count"])
            k8.metric("💨 تهوية صيفية", f"{dims['vent_flow_summer_m3h']:,} م³/س")

            with st.expander("🔬 تفاصيل علمية إضافية"):
                std = dims["standard"]
                st.markdown(f"""
                - **المساحة لكل رأس:** {std['area_per_head']} م²
                - **طول المعلف لكل رأس:** {std['feeder_cm_per_head']} سم
                - **طول المسقى لكل رأس:** {std['drinker_cm_per_head']} سم
                - **معدل تغيير الهواء — صيف (ACH):** {std['ach_summer']}
                - **معدل تغيير الهواء — شتاء (ACH):** {std['ach_winter']}
                - **نسبة فتحات التهوية:** {std['vent_open_ratio']*100}%
                - **نوع السقف:** {'جمالوني' if std['roof_type']=='gable' else 'أحادي'}
                - **ميل السقف:** {std['slope_pct']}%
                - **نوع المعالف:** {dims.get('feeder_type', 'خطية')}
                - **نوع السقايات:** {dims.get('drinker_type', 'حوض')}
                - **عرض الممر:** {dims.get('aisle_m', 1.5)} م
                - **المرجع:** MWPS-1 / FAO 2012 / ASABE
                """)

            st.markdown("### 🏗️ المجسم ثلاثي الأبعاد التفاعلي")
            st.caption("💡 حرّك المجسم بالفأرة: تدوير، تكبير، وتحريك.")
            fig3d = create_barn_3d_figure(dims)
            if fig3d:
                st.plotly_chart(fig3d, use_container_width=True,
                                config={"displayModeBar": True,
                                        "toImageButtonOptions": {
                                            "format": "png",
                                            "filename": f"barn_{barn_animal}",
                                            "height": 900,
                                            "width": 1400
                                        }})
            else:
                st.warning("⚠️ Plotly غير متوفر لعرض المجسم.")

            st.markdown('<div class="section-title">🎬 فيديو الحظيرة المتحرك (GIF)</div>',
                        unsafe_allow_html=True)
            st.markdown("""
            <div class="video-card">
            <b>🎥 فيديو دوّار 360° للحظيرة:</b><br>
            ▪️ يُظهر الحظيرة من جميع الزوايا<br>
            ▪️ يمكن تنزيله ومشاركته<br>
            ▪️ يعمل على جميع الأجهزة<br>
            <small>⏱️ التوليد قد يستغرق 10-20 ثانية</small>
            </div>
            """, unsafe_allow_html=True)

            col_v1, col_v2 = st.columns([0.6, 0.4])
            with col_v1:
                if st.button("🎬 توليد فيديو GIF للحظيرة",
                             type="primary", use_container_width=True, key="gen_video"):
                    with st.spinner("🎥 جاري توليد الفيديو (30 إطاراً)..."):
                        video_buf = create_barn_animation_gif(dims, frames=30, fps=8)
                    if video_buf:
                        st.session_state["barn_video_gif"] = video_buf.getvalue()
                        st.success("✅ تم توليد الفيديو بنجاح!")
                    else:
                        st.error("⚠️ تعذر التوليد (تأكد من matplotlib و Pillow)")
            with col_v2:
                st.markdown("""
                <div class="barn-info-card">
                <b>💡 نصيحة:</b> استخدم عدد إطارات أعلى (45-60) للحصول على حركة أنعم.
                </div>
                """, unsafe_allow_html=True)

            if st.session_state.get("barn_video_gif"):
                st.markdown("#### 🎥 معاينة الفيديو:")
                st.image(st.session_state["barn_video_gif"], use_container_width=True)
                st.download_button(
                    "⬇️ تحميل الفيديو (GIF)",
                    st.session_state["barn_video_gif"],
                    file_name=f"barn_{barn_animal}_{barn_count}_{datetime.now():%Y%m%d}.gif",
                    mime="image/gif", use_container_width=True, type="primary")

            st.markdown("### 📥 تصدير التقرير")
            try:
                pdf_bytes = generate_barn_pdf_report(dims)
                fname = f"Barn_Design_{barn_animal}_{barn_count}_{datetime.now():%Y%m%d}.pdf"
                st.download_button("📄 تحميل تصميم الحظيرة (PDF)", pdf_bytes,
                                   file_name=fname, mime="application/pdf",
                                   use_container_width=True, type="primary")
            except Exception as e:
                st.error(f"⚠️ خطأ في إنشاء PDF: {e}")

            with st.expander("📊 مقارنة خيارات أحجام مختلفة"):
                alt_rows = []
                for alt_count in [barn_count // 2, barn_count, barn_count * 2]:
                    if alt_count < 1:
                        continue
                    alt_dims = calculate_barn_dimensions(barn_animal, alt_count)
                    if alt_dims:
                        alt_rows.append({
                            "العدد": alt_count,
                            "المساحة (م²)": alt_dims["total_area_m2"],
                            "الطول (م)": alt_dims["length_m"],
                            "العرض (م)": alt_dims["width_m"],
                            "المعالف": alt_dims["feeders_count"],
                            "السقايات": alt_dims["drinkers_count"],
                            "تهوية صيفية (م³/س)": f"{alt_dims['vent_flow_summer_m3h']:,}",
                        })
                st.dataframe(pd.DataFrame(alt_rows), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"⚠️ خطأ في تصميم الحظائر: {e}")
        with st.expander("تفاصيل"):
            st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════════════
# تبويب دراسة الجدوى
# ═══════════════════════════════════════════════════════════════════════
with tab_map["📊 دراسة الجدوى"]:
    try:
        st.markdown('<div class="section-title">📊 دراسة الجدوى الفنية للمشروعات</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        <div class="feas-card">
        <b>🎯 دراسة فنية شاملة (بدون اقتصاديات):</b><br>
        ▪️ تصميم الحظيرة بأبعادها ومساحتها<br>
        ▪️ احتياجات العلف والماء والتهوية<br>
        ▪️ الإنتاج المتوقع (لحم / حليب / بيض)<br>
        ▪️ العمالة المطلوبة<br>
        ▪️ كتيّب PDF كامل بالتوقيع والختم الرسمي
        </div>
        """, unsafe_allow_html=True)

        f1, f2 = st.columns(2)
        with f1:
            feas_key = st.selectbox(
                "نوع الحيوان:", list(BARN_DESIGN_STANDARDS.keys()),
                format_func=lambda k: BARN_DESIGN_STANDARDS[k]["name_ar"],
                key="feas_animal")
            feas_count = st.number_input("العدد الكلي:", 1, 100000, 1000, 50, key="feas_count")
        with f2:
            project_name = st.text_input("اسم المشروع:", placeholder="مشروع دواجن الأمل", key="feas_proj")
            feas_requester = st.text_input("مقدم الطلب:", key="feas_req")

        st.markdown("---")

        with st.spinner("⏳ حساب الجدوى..."):
            feas = calculate_technical_feasibility(feas_key, feas_count)

        if feas:
            st.markdown("### 📐 بيانات الحظيرة")
            d = feas["dims"]
            fc1, fc2, fc3, fc4 = st.columns(4)
            fc1.metric("📏 المساحة", f"{d['total_area_m2']} م²")
            fc2.metric("📐 الأبعاد", f"{d['length_m']}×{d['width_m']} م")
            fc3.metric("🏔️ القمة", f"{d['ridge_height_m']} م")
            fc4.metric("📦 الحجم", f"{d['volume_m3']} م³")

            st.markdown("### 🍽️ احتياجات العلف")
            f1, f2, f3, f4 = st.columns(4)
            f1.metric("علف/رأس/يوم", f"{feas['feed']['per_head_day_kg']*1000:.0f} جم")
            f2.metric("إجمالي يومي", f"{feas['feed']['total_day_kg']:.1f} كجم")
            f3.metric("إجمالي شهري", f"{feas['feed']['total_month_ton']:.2f} طن")
            f4.metric("إجمالي سنوي", f"{feas['feed']['total_year_ton']:.2f} طن")

            st.markdown("### 💧 احتياجات الماء")
            w1, w2, w3 = st.columns(3)
            w1.metric("ماء/رأس/يوم", f"{feas['water']['per_head_day_L']:.1f} لتر")
            w2.metric("إجمالي يومي", f"{feas['water']['total_day_L']:.0f} لتر")
            w3.metric("إجمالي سنوي", f"{feas['water']['total_year_m3']:.1f} م³")

            st.markdown("### 💨 التهوية والعمالة")
            v1, v2, v3, v4 = st.columns(4)
            v1.metric("تهوية صيف", f"{feas['ventilation']['summer_m3h']:,} م³/س")
            v2.metric("تهوية شتاء", f"{feas['ventilation']['winter_m3h']:,} م³/س")
            v3.metric("عدد العمال", feas["labor"]["workers"])
            v4.metric("حيوانات/عامل", feas["labor"]["animals_per_worker"])

            st.markdown("### 📊 الإنتاج المتوقع")
            p = feas["production"]
            st.write(f"**نوع الإنتاج:** {p.get('unit', '—')}")
            prod_cols = st.columns(3)
            if "annual" in p:
                prod_cols[0].metric("سنوي", f"{p['annual']:,.0f}")
            if "per_day" in p:
                prod_cols[1].metric("يومي", f"{p['per_day']:,.1f}")
            if "per_cycle" in p:
                prod_cols[2].metric("دورة", f"{p['per_cycle']:,.0f}")
            if p.get("details"):
                st.info(f"📝 {p['details']}")

            st.markdown("---")
            st.markdown("### 📄 كتيّب الجدوى الفني (PDF)")

            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                try:
                    booklet = generate_feasibility_booklet(
                        feas_key, feas_count,
                        project_name=project_name,
                        requester_name=feas_requester)
                    if booklet:
                        st.download_button(
                            "📥 تحميل كتيّب الجدوى الكامل (PDF)",
                            booklet,
                            file_name=(f"Feasibility_{feas_key}_{feas_count}_"
                                       f"{datetime.now():%Y%m%d}.pdf"),
                            mime="application/pdf",
                            use_container_width=True, type="primary")
                except Exception as e:
                    st.error(f"⚠️ تعذر إنشاء الكتيّب: {e}")

            with col_dl2:
                st.markdown("""
                <div class="feas-card" style="background:linear-gradient(135deg,#fff8e1,#ffe082);">
                <b>📖 الكتيّب يحتوي على:</b><br>
                ▪️ الغلاف + بيانات المشروع<br>
                ▪️ تصميم الحظيرة + مجسم 3D<br>
                ▪️ الجدوى الفنية (علف، ماء، تهوية، عمالة)<br>
                ▪️ الإنتاج المتوقع<br>
                ▪️ صفحة التوقيع الرسمي + الختم
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ خطأ في الجدوى: {e}")
        with st.expander("تفاصيل"):
            st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════════════
# تبويب مزارع الدجاج
# ═══════════════════════════════════════════════════════════════════════
with tab_map["🐔 مزارع الدجاج"]:
    try:
        st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج</div>',
                    unsafe_allow_html=True)
        st.info("🌐 متاح للجميع — يمكن إضافة مزرعة جديدة وتسجيل بياناتك اليومية.")

        with st.expander("➕ إضافة مزرعة جديدة", expanded=True):
            nf_name = st.text_input("اسم المزرعة:", key="nf_name")
            nf_owner = st.text_input("المالك:", key="nf_owner")
            nf_phone = st.text_input("واتساب:", WHATSAPP_NUMBER, key="nf_phone")
            if st.button("💾 حفظ المزرعة", key="nf_save") and nf_name:
                st.session_state["broiler_farms"][nf_name] = {
                    "owner": nf_owner,
                    "owner_phone": nf_phone,
                    "data": {"age": 1, "birds": 1000, "weight_kg": 0.045,
                             "feed_kg": 0.0, "dead": 0, "temp": 33.0, "hum": 65.0},
                }
                st.success(f"✅ تمت إضافة {nf_name}")
                st.rerun()

        if st.session_state["broiler_farms"]:
            farms = list(st.session_state["broiler_farms"].keys())
            sel = st.selectbox("اختر مزرعة:", [""] + farms, key="farm_sel")
            if sel:
                d = st.session_state["broiler_farms"][sel]["data"]
                b1, b2 = st.columns(2)
                with b1:
                    d["age"] = st.number_input("العمر (يوم):", 1, 60, d["age"], key="bf_age")
                    d["birds"] = st.number_input("الطيور:", 1, value=d["birds"], key="bf_birds")
                    d["weight_kg"] = st.number_input("الوزن (كجم):", 0.0, 10.0,
                                                     float(d["weight_kg"]), 0.01, key="bf_w")
                    d["feed_kg"] = st.number_input("العلف (كجم):", 0.0,
                                                    float(d["feed_kg"]), 100.0, key="bf_f")
                with b2:
                    d["dead"] = st.number_input("النافق:", 0, value=d["dead"], key="bf_d")
                    d["temp"] = st.number_input("الحرارة:", 10.0, 45.0,
                                                float(d["temp"]), key="bf_t")
                    d["hum"] = st.number_input("الرطوبة:", 20.0, 90.0,
                                               float(d["hum"]), key="bf_h")

                alive = d["birds"] - d["dead"]
                gain = alive * (d["weight_kg"] - 0.045)
                adg = ((d["weight_kg"] - 0.045) * 1000 / d["age"]) if d["age"] > 0 else 0
                fcr = (d["feed_kg"] / gain) if gain > 0 else 0
                liv = 100 - (d["dead"] / d["birds"] * 100)
                epef = ((liv * d["weight_kg"]) / (d["age"] * fcr) * 100) if d["age"] > 0 and fcr > 0 else 0
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("ADG (جم/يوم)", f"{adg:.1f}")
                k2.metric("FCR", f"{fcr:.2f}")
                k3.metric("EPEF", f"{epef:.0f}")
                k4.metric("الحيوية %", f"{liv:.1f}")

                with st.expander("💡 تفسير المؤشرات"):
                    st.markdown(f"""
                    - **ADG:** متوسط الزيادة اليومية — كلما ارتفع كان أفضل
                    - **FCR:** معامل التحويل الغذائي — كلما انخفض كان أفضل
                    - **EPEF:** مؤشر الكفاءة الأوروبي — أعلى من 350 = ممتاز
                    - **الحيوية:** نسبة الطيور الحية — أعلى من 95% = ممتاز
                    """)

    except Exception as e:
        st.error(f"⚠️ خطأ: {e}")


# ═══════════════════════════════════════════════════════════════════════
# تبويبات المالك فقط
# ═══════════════════════════════════════════════════════════════════════
if is_owner():
    with tab_map["📊 البورصة"]:
        try:
            st.markdown('<div class="section-title">📊 البورصة</div>', unsafe_allow_html=True)
            t1, t2 = st.tabs(["🐄 الماشية", "🥩 المنتجات"])
            with t1:
                for animal, price in list(st.session_state["livestock_prices"].items()):
                    new_p = st.number_input(f"تحديث: {animal}", min_value=0.0,
                                            value=float(price), step=0.1, key=f"lv_{animal}")
                    st.session_state["livestock_prices"][animal] = new_p
            with t2:
                for product, price in list(st.session_state["products_prices"].items()):
                    new_p = st.number_input(f"تحديث: {product}", min_value=0.0,
                                            value=float(price), step=0.05, key=f"pr_{product}")
                    st.session_state["products_prices"][product] = new_p
        except Exception as e:
            st.error(f"⚠️ {e}")

    with tab_map["🏭 المستودعات"]:
        try:
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
                    new_q = st.number_input("تحديث:", min_value=0.0, value=float(q),
                                            key=f"inv_{name}", label_visibility="collapsed")
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
                profit = st.number_input("هامش الربح ($/طن):", 0.0, 1000.0, 50.0)
            sell = st.session_state["computed_ton_cost"] + profit
            total = sell * tons
            st.markdown(f"""
            <div class="price-card">
            <h4>🧾 فاتورة</h4>
            <p><b>العميل:</b> {client}</p>
            <p><b>الكمية:</b> {tons} طن</p>
            <p><b>سعر الطن:</b> ${sell:.2f}</p>
            <p style="font-size:1.3rem; color:#1b5e20;"><b>الإجمالي:</b> ${total:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"⚠️ {e}")

    with tab_map["🖨️ الديباجة"]:
        try:
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
            m4.metric("رضا العملاء", "96%")
            if PLOTLY_AVAILABLE:
                usage = pd.DataFrame({
                    'المادة': ['ذرة', 'صويا', 'نخالة', 'زيوت', 'أملاح', 'أخرى'],
                    'نسبة الاستخدام': [42, 23, 14, 8, 8, 5],
                })
                fig = px.pie(usage, values='نسبة الاستخدام', names='المادة',
                             color_discrete_sequence=px.colors.sequential.Greens)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ {e}")

    with tab_map["💬 التعليقات"]:
        try:
            st.markdown('<div class="section-title">💬 التعليقات</div>',
                        unsafe_allow_html=True)
            st.text_area("الحالية:", value=st.session_state["shared_comments"],
                         height=200, disabled=True)
            nc = st.text_area("جديد:")
            if st.button("➕ نشر") and nc:
                st.session_state["shared_comments"] += (
                    f"\n• [{datetime.now():%Y-%m-%d %H:%M}]: {nc}")
                st.rerun()
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════
# المراجع + المساعدة + الدليل
# ═══════════════════════════════════════════════════════════════════════
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
        - **McDonald et al. (2011)** — Animal Nutrition
        - **Van Soest (1994)** — Nutritional Ecology of the Ruminant

        ### 📖 مراجع الزيوت:
        - NRC 2012 — Chapter: Fat in Animal Nutrition
        - INRA 2018 — Lipids in Ruminant Diets
        - Palmquist (2006) — Milk Fat Depression
        - FAO — Oilseed By-products

        ### 🏗️ مراجع تصميم الحظائر:
        - MWPS-1 — Structures and Environment Handbook
        - MWPS-3 — Swine Housing and Equipment Handbook
        - FAO 2012 — Rural Structures in the Tropics
        - ASABE Standards — Animal Housing Ventilation
        """)
    except Exception as e:
        st.error(f"⚠️ {e}")


with tab_map["💡 المساعدة"]:
    try:
        st.markdown('<div class="section-title">💡 المساعدة</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        ### الأسئلة الشائعة:
        - **كيف أبدأ؟** اختر الحيوان → الحالة → ✅ اعتماد
        - **DP أم CP؟** اختر في الأعلى — كلاهما يعمل في المعادلات
        - **الزيوت؟** راجع "🌰 مكتبة الزيوت"
        - **مختبر التحليل؟** داخل "🔬 النمذجة" ← مختبر الأعلاف الجاهزة
        - **تصميم الحظائر؟** متاح للجميع مع مجسم 3D + فيديو GIF
        - **دراسة الجدوى؟** تبويب كامل مع كتيّب PDF
        - **مزارع الدجاج؟** متاح للجميع — ADG/FCR/EPEF
        - **الختم والتوقيع؟** على كل صفحة PDF

        ### 🔧 الدعم الفني
        📧 {OWNER_EMAIL}
        📱 {WHATSAPP_NUMBER}

        ### 🕌 دعاء
        {DUA_FULL}
        """)
    except Exception as e:
        st.error(f"⚠️ {e}")


with tab_map["📖 الدليل"]:
    try:
        st.markdown('<div class="section-title">📖 دليل المستخدم</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        ### الغرض
        **{APP_NAME}** — منصة ذكية لتركيب الأعلاف بأقل تكلفة وأعلى جودة.

        ### 🎯 الميزات الرئيسية
        - 🐄 **8 قطاعات**: أبقار، أغنام، ماعز، إبل، خيول، دواجن، سمان، أسماك
        - 🌰 **18 زيتاً نباتياً وحيوانياً** بمعايير NRC/INRA/FAO
        - 🧬 **DP/CP يعمل فعلياً** في المعادلات
        - 🔬 **مختبر تحليل + OCR**
        - 🏗️ **تصميم حظائر 3D** (للجميع) + **فيديو GIF دوّار**
        - 📊 **دراسة جدوى فنية** كاملة + **كتيّب PDF 5 صفحات**
        - 🐔 **إدارة مزارع الدجاج** (للجميع) — ADG، FCR، EPEF
        - 📄 **PDF احترافي** بختم وتوقيع ورسوم بيانية
        - 📊 **Excel** قابل للتحرير

        ### 🏗️ معايير تصميم الحظائر
        - **MWPS-1** — Midwest Plan Service
        - **FAO 2012** — Rural Structures in the Tropics
        - **ASABE Standards** — Animal Housing

        ### 🆕 جديد في 10.3:
        - ✅ إصلاح `standard_key` في `auto_formulate_smart`
        - ✅ الختم والتوقيع على كل صفحة PDF
        - ✅ 4 رسوم بيانية ملونة في UI + PDF
        - ✅ تبويب دراسة الجدوى + كتيّب 5 صفحات
        - ✅ معالف خطية + سقايات علمية
        - ✅ كل تبويب محمي بـ try/except مستقل

        ### 🔐 الدخول
        - 👑 **المالك**: كود خاص
        - 👥 **زائر**: مجاني + حظائر 3D + مزارع + مختبرات

        ### 📞 للتواصل
        📧 {OWNER_EMAIL} | 📱 {WHATSAPP_NUMBER}

        ---
        ### 🤲 دعاء
        {DUA_FULL}
        """)
    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════
# التذييل الثابت
# ═══════════════════════════════════════════════════════════════════════
st.markdown(
    f'<div class="mini-signature">🌾 {APP_NAME} | {SUPERVISOR} © 2026</div>',
    unsafe_allow_html=True
)
st.markdown(
    f'<div class="dua-fixed-banner">🤲 {DUA_SHORT} 🤲</div>',
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# نهاية الملف — Tawor Nology 10.3 (كامل)
# ═══════════════════════════════════════════════════════════════════════
