# ============================================================================
# تاور نولجي TAWOR NOLOGY — الإصدار 10.3 النهائي (ملف واحد)
# إشراف: م. عبدالقادر إسماعيل تاور
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
# ============================================================================

import streamlit as st
import numpy as np, pandas as pd, io, os, re, base64, tempfile, traceback, warnings
import urllib.parse, urllib.request
from datetime import datetime
from functools import lru_cache
from dataclasses import dataclass

warnings.filterwarnings('ignore')

try:
    from scipy.optimize import linprog
    SCIPY_AVAILABLE = True
except: SCIPY_AVAILABLE = False

try:
    import plotly.express as px, plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except: PLOTLY_AVAILABLE = False

try:
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Wedge
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    from matplotlib import animation
    MATPLOTLIB_AVAILABLE = True
except: MATPLOTLIB_AVAILABLE = False

try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except: PIL_AVAILABLE = False

try:
    import pytesseract, cv2
    OCR_AVAILABLE = True
except: OCR_AVAILABLE = False

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except: OPENPYXL_AVAILABLE = False

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
except: REPORTLAB_AVAILABLE = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_AVAILABLE = True
except: ARABIC_AVAILABLE = False

try:
    import qrcode
    QRCODE_AVAILABLE = True
except: QRCODE_AVAILABLE = False


# ═══ الدعاء ═══
DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي ابتسام"
DUA_FULL = "رحم الله والدي إسماعيل تاور وأختي ابتسام، وأسكنهما فسيح جناته، وجعل قبرهما روضة من رياض الجنة"
DUA_QURAN = "﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾"
DUA_VERSE = "﴿ وَقُل رَّبِّ ارْحَمْهُمَا كَمَا رَبَّيَانِي صَغِيرًا ﴾"
DUA_VISITOR_BANNER = """
🕌 <b>إلى زوارنا الكرام:</b><br>
هذه المنصة صدقةٌ جارية عن <b>والدي إسماعيل تاور</b> و<b>أختي ابتسام</b>.<br>
نسألكم بظهر الغيب أن تشاركونا الدعاء لهما. 🤲
"""

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

st.set_page_config(page_title=f"{APP_NAME} | {APP_TAGLINE}", page_icon="🌾",
                   layout="wide", initial_sidebar_state="collapsed")

# ═══ الخطوط ═══
FONT_DIR = "fonts"; os.makedirs(FONT_DIR, exist_ok=True)
ARABIC_FONT_URLS = [("https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf", "Amiri-Regular.ttf")]

class ArabicFontManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls); cls._instance._init()
        return cls._instance
    def _init(self):
        self.font_name = 'Helvetica'; self.font_bold = 'Helvetica-Bold'; self.ready = False
        if not REPORTLAB_AVAILABLE: return
        for p in [os.path.join(FONT_DIR, "Amiri-Regular.ttf"), "Amiri-Regular.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
            if os.path.exists(p) and self._register(p): return
        for url, fn in ARABIC_FONT_URLS:
            try:
                target = os.path.join(FONT_DIR, fn)
                if not os.path.exists(target): urllib.request.urlretrieve(url, target)
                if self._register(target): return
            except: continue
    def _register(self, path):
        try:
            pdfmetrics.registerFont(TTFont('TaworArabic', path))
            self.font_name = 'TaworArabic'; self.font_bold = 'TaworArabic'; self.ready = True
            return True
        except: return False

font_mgr = ArabicFontManager()

class ArabicProcessor:
    @staticmethod
    @lru_cache(maxsize=5000)
    def fix(text):
        if text is None or text == "": return ""
        text = str(text)
        if not ARABIC_AVAILABLE: return text
        try: return get_display(arabic_reshaper.reshape(text), base_dir='R')
        except: return text

arp = ArabicProcessor()
def ar(text): return arp.fix(text)


# ═══ مكتبة الأعلاف ═══
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3, "Ca": 0.02, "P": 0.27},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4, "Ca": 0.02, "P": 0.26},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5, "Ca": 0.05, "P": 0.35},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8, "Ca": 0.03, "P": 0.30},
        "قمح محلي": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6, "Ca": 0.04, "P": 0.32},
        "جريش أرز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2, "Ca": 0.06, "P": 0.30},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0, "Ca": 0.08, "P": 0.35},
    },
    "🌱 الأكساب": {
        "أمباز الفول السوداني": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5, "Ca": 0.20, "P": 0.65},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0, "Ca": 0.35, "P": 0.65},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2, "Ca": 0.35, "P": 0.65},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5, "Ca": 0.40, "P": 1.00},
        "كسب بذور القطن": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5, "Ca": 0.20, "P": 1.10},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8, "Ca": 0.35, "P": 0.85},
        "كسب السمسم": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5, "Ca": 2.00, "P": 1.20},
        "كسب جلوتين 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5, "Ca": 0.15, "P": 0.50},
        "كسب الكانولا": {"CP": 36.0, "DC": 0.82, "SE": 60.0, "NDF": 28.0, "ADF": 18.0, "EE": 3.5, "ASH": 6.5, "Ca": 0.65, "P": 1.10},
    },
    "🚜 المخلفات": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5, "Ca": 0.12, "P": 1.10},
        "البرسيم الجاف": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5, "Ca": 1.50, "P": 0.25},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5, "Ca": 0.70, "P": 0.05},
        "تبن قمح": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.30, "P": 0.08},
        "سرسة الأرز": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5, "Ca": 0.15, "P": 0.08},
    },
    "🧬 البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5, "Ca": 5.50, "P": 3.20},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5, "Ca": 9.00, "P": 4.50},
        "مسحوق الدم": {"CP": 80.0, "DC": 0.65, "SE": 55.0, "NDF": 1.0, "ADF": 0.5, "EE": 1.5, "ASH": 6.0, "Ca": 0.30, "P": 0.30},
        "مركزات دواجن": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5, "Ca": 2.50, "P": 1.20},
        "مركزات مواشي": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5, "Ca": 3.00, "P": 1.50},
    },
    "🌰 الزيوت": {
        "زيت ذرة": {"CP": 0.0, "DC": 0.0, "SE": 220.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "9000 kcal/kg", "source": "NRC 2012"},
        "زيت فول الصويا": {"CP": 0.0, "DC": 0.0, "SE": 215.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "8800 kcal/kg", "source": "Ross 308"},
        "زيت عباد الشمس": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "أوميغا 6", "source": "NRC 2007"},
        "زيت الكتان": {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "أوميغا 3", "source": "NRC 2007 Horses"},
        "زيت جوز الهند": {"CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "MCT", "source": "NRC 2012"},
        "زيت النخيل": {"CP": 0.0, "DC": 0.0, "SE": 215.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "8700 kcal/kg", "source": "NRC 2012"},
        "زيت الكانولا": {"CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "متوازن", "source": "NRC 2012"},
        "زيت الزيتون": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "أوميغا 9", "source": "INRA 2018"},
        "شحم حيواني (Tallow)": {"CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "9500 kcal/kg", "source": "NRC 2012"},
        "زيت السمك (Fish Oil)": {"CP": 0.0, "DC": 0.0, "SE": 235.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "desc": "EPA/DHA", "source": "NRC Fish"},
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0},
        "ميثيونين نقي": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3, "Ca": 0.0, "P": 0.0},
        "ثريونين نقي": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0},
    },
    "🔬 البريمكسات": {
        "بريمكس تسمين دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 8.0},
        "بريمكس بياض": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 22.0, "P": 7.0},
        "بريمكس مجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 9.0},
        "بريمكس خيول": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 8.0},
        "بريمكس إبل": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0},
        "بريمكس أسماك": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 7.0},
        "إنزيم فايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0, "Ca": 0.0, "P": 0.0},
    },
    "🪨 المعادن": {
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 38.0, "P": 0.0},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5, "Ca": 23.0, "P": 18.0},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9, "Ca": 0.0, "P": 0.0},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 0.0, "P": 0.0},
        "يوريا علفية": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0, "Ca": 0.0, "P": 0.0},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Ca": 0.0, "P": 0.0},
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
    "أسماك_بادئ": {"max": 15.0, "optimal": 10.0, "source": "NRC Fish"},
    "أسماك_نمو": {"max": 12.0, "optimal": 8.0, "source": "NRC Fish"},
    "أسماك_تسمين": {"max": 12.0, "optimal": 8.0, "source": "NRC Fish"},
}

OIL_CATEGORIES = {
    "زيوت أوميغا 6": ["زيت ذرة", "زيت عباد الشمس", "زيت فول الصويا"],
    "زيوت أوميغا 3": ["زيت الكتان", "زيت الكانولا", "زيت السمك (Fish Oil)"],
    "زيوت متوازنة": ["زيت النخيل", "زيت جوز الهند", "زيت الزيتون"],
    "دهون حيوانية": ["شحم حيواني (Tallow)"],
}

def get_oil_standard(key):
    return MAX_OIL_PERCENTAGE.get(key, {"max": 5.0, "optimal": 3.0, "source": "NRC"})

def get_oil_ingredients():
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت", {})


@dataclass
class AnimalRequirement:
    DP: float; CP: float; SE: float; NDF: float; ADF: float
    EE: float; ASH: float; Ca: float; P: float
    name_ar: str = ""; note: str = ""

def get_cattle_requirements(t, milk=20, wt=500):
    if t == "حليب_عالي":
        dp = 12.5 + milk*0.30
        return AnimalRequirement(dp, dp/0.70, 60+milk*0.35, 30, 19, 5.5, 8.0, 0.55+milk*0.003, 0.33+milk*0.0015, "حلابة عالية", f"{milk} كجم")
    if t == "حليب_متوسط":
        dp = 11.0 + milk*0.25
        return AnimalRequirement(dp, dp/0.72, 55+milk*0.30, 33, 21, 4.5, 8.0, 0.50+milk*0.0025, 0.30+milk*0.0012, "حلابة متوسطة", f"{milk}")
    if t == "حليب_منخفض":
        dp = 9.5 + milk*0.20
        return AnimalRequirement(dp, dp/0.75, 50+milk*0.25, 38, 24, 4.0, 8.5, 0.45+milk*0.002, 0.28+milk*0.001, "حلابة منخفضة", f"{milk}")
    if t == "تسمين_مكثف": return AnimalRequirement(11.5, 14.5, 72, 32, 20, 4.5, 7.5, 0.65, 0.38, "تسمين مكثف", "ADG >1.3")
    if t == "تسمين_عادي": return AnimalRequirement(9.5, 12.0, 65, 38, 24, 4.0, 7.5, 0.55, 0.32, "تسمين عادي", "ADG 0.8")
    if t == "حمل_أخير": return AnimalRequirement(11.5, 14.5, 67, 35, 22, 4.2, 8.0, 0.70, 0.42, "حمل آخر", "")
    return AnimalRequirement(7.5, 10.0, 53, 45, 28, 3.0, 8.5, 0.42, 0.26, "صيانة", "")

def get_sheep_requirements(t, is_male=True, wt=50, litter=1):
    if is_male:
        if t == "تسمين_مكثف": return AnimalRequirement(11.5, 14.5, 64, 28, 17, 4.0, 8.0, 0.65, 0.36, "تسمين مكثف", "ADG 250")
        if t == "تسمين_عادي": return AnimalRequirement(9.5, 12.0, 59, 33, 21, 3.6, 8.0, 0.55, 0.32, "تسمين عادي", "")
        return AnimalRequirement(8.5, 11.0, 55, 38, 24, 3.2, 8.5, 0.50, 0.30, "حملان تيد", "")
    if t == "مرضعات":
        dp = 10.5 + (litter-1)*1.5
        return AnimalRequirement(dp, dp/0.72, 60+(litter-1)*5, 30, 19, 4.5, 8.5, 0.65+(litter-1)*0.10, 0.38+(litter-1)*0.05, f"مرضعات ({litter})", "")
    if t == "حامل_أخير": return AnimalRequirement(10.5, 13.5, 62, 32, 20, 3.8, 8.0, 0.60, 0.35, "حامل آخر", "")
    if t == "حامل_متوسط": return AnimalRequirement(8.5, 11.0, 55, 38, 24, 3.4, 8.0, 0.50, 0.30, "حامل متوسط", "")
    return AnimalRequirement(7.2, 9.5, 48, 45, 28, 3.0, 8.5, 0.42, 0.26, "صيانة", "")

def get_goat_requirements(t, is_male=True, milk=2):
    if is_male:
        if t == "تسمين_جديان": return AnimalRequirement(11.0, 14.0, 62, 30, 19, 3.8, 8.0, 0.62, 0.34, "تسمين جديان", "")
        return AnimalRequirement(9.0, 11.5, 57, 36, 22, 3.5, 8.0, 0.55, 0.30, "تيوس", "")
    if t == "حلابة_عالي":
        dp = 11.5 + milk*0.45
        return AnimalRequirement(dp, dp/0.70, 58+milk*0.45, 29, 18, 4.5, 8.5, 0.60+milk*0.008, 0.35+milk*0.004, f"حلابة ({milk})", "")
    if t == "حلابة_متوسط":
        dp = 10.0 + milk*0.35
        return AnimalRequirement(dp, dp/0.72, 55+milk*0.40, 32, 20, 4.0, 8.5, 0.55+milk*0.006, 0.32+milk*0.003, f"حلابة ({milk})", "")
    if t == "حامل_أخير": return AnimalRequirement(10.0, 13.0, 60, 33, 21, 3.8, 8.0, 0.60, 0.35, "حامل", "")
    return AnimalRequirement(6.8, 9.0, 46, 46, 28, 3.0, 8.5, 0.42, 0.26, "صيانة", "")

def get_camel_requirements(t, wt=400, milk=5):
    if t == "نمو": return AnimalRequirement(10.5, 13.5, 60, 38, 24, 4.0, 8.0, 0.65, 0.38, "نمو", f"{wt}")
    if t == "تسمين": return AnimalRequirement(9.5, 12.0, 65, 35, 22, 4.5, 7.5, 0.60, 0.35, "تسمين", f"{wt}")
    if t == "حليب":
        dp = 12.0 + milk*0.25
        return AnimalRequirement(dp, dp/0.70, 62+milk*0.40, 32, 20, 5.0, 8.5, 0.70+milk*0.006, 0.40+milk*0.003, f"حلابة ({milk})", "")
    if t == "سباق": return AnimalRequirement(14.0, 17.0, 72, 28, 17, 6.0, 9.0, 0.85, 0.50, "سباق", "")
    return AnimalRequirement(7.0, 9.0, 48, 48, 30, 3.5, 9.0, 0.42, 0.26, "صيانة", f"{wt}")

def get_horse_requirements(t, wt=450):
    if t == "رياضة_مكثف": return AnimalRequirement(10.5, 13.5, 70, 30, 18, 7.0, 7.5, 0.70, 0.40, "رياضة مكثف", "")
    if t == "رياضة_عادي": return AnimalRequirement(9.0, 11.5, 63, 36, 22, 5.0, 7.5, 0.55, 0.32, "رياضة عادي", "")
    if t == "نمو_أمهار": return AnimalRequirement(12.0, 15.0, 65, 30, 18, 5.0, 8.0, 0.75, 0.42, "أمهار", "")
    if t == "مرضعات": return AnimalRequirement(12.5, 16.0, 68, 32, 20, 5.5, 8.0, 0.80, 0.45, "مرضعات", "")
    return AnimalRequirement(7.2, 9.5, 53, 46, 29, 3.5, 8.0, 0.45, 0.28, "صيانة", "")

def get_poultry_requirements(strain, age=1):
    if strain == "لاحم":
        if age <= 1: return AnimalRequirement(20.0, 23.0, 76, 8, 4, 5.0, 6.5, 1.00, 0.50, "بادي لاحم", "3000")
        if age <= 3: return AnimalRequirement(18.5, 21.0, 74, 9, 5, 5.0, 6.0, 0.90, 0.45, "نامي لاحم", "3100")
        if age <= 5: return AnimalRequirement(17.0, 19.5, 75, 10, 5.5, 4.5, 6.0, 0.87, 0.43, "ناهي", "3150")
        return AnimalRequirement(16.5, 19.0, 75, 10, 5.5, 4.5, 6.0, 0.85, 0.42, "ناهي+", "3200")
    if age <= 6: return AnimalRequirement(17.0, 20.0, 72, 10, 5.5, 4.0, 7.0, 1.00, 0.50, "بادي بياض", "")
    if age <= 18: return AnimalRequirement(14.5, 17.0, 70, 12, 6.5, 4.0, 9.0, 1.50, 0.45, "نامي بياض", "")
    return AnimalRequirement(15.5, 18.0, 72, 11, 6.0, 4.2, 11.5, 3.80, 0.45, "بياض", "")

def get_quail_requirements(strain, age=1):
    if strain == "بياض": return AnimalRequirement(15.0, 18.0, 68, 11, 5.5, 4.5, 9.0, 2.50, 0.45, "سمان بياض", "")
    if age <= 2: return AnimalRequirement(20.5, 24.0, 74, 8, 4, 5.5, 6.5, 1.00, 0.55, "سمان بادي", "")
    if age <= 4: return AnimalRequirement(18.5, 22.0, 72, 9, 4.5, 5.0, 6.0, 0.90, 0.50, "سمان نامي", "")
    return AnimalRequirement(17.0, 20.0, 70, 10, 5.0, 4.5, 6.0, 0.85, 0.45, "سمان ناهي", "")

def get_fish_requirements(sp, stg):
    if "زريعة" in stg or "بادئ" in stg: return AnimalRequirement(32.0, 40.0, 72, 8, 4, 10.0, 11.0, 1.50, 0.90, f"{sp} بادئ", "")
    if "نمو" in stg: return AnimalRequirement(25.0, 32.0, 70, 12, 6, 8.0, 9.0, 1.00, 0.70, f"{sp} نمو", "")
    return AnimalRequirement(22.0, 28.0, 68, 13, 7, 8.0, 9.5, 0.90, 0.65, f"{sp} تسمين", "")

def requirement_to_standard(req):
    return {"CP": req.CP, "DP": req.DP, "SE": req.SE, "NDF": req.NDF, "ADF": req.ADF,
            "EE": req.EE, "ASH": req.ASH, "Ca": req.Ca, "P": req.P}


def compute_formula_nutrients(formula):
    t = {"CP": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0}
    for ing, pct in formula.items():
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat:
                d = cat[ing]; f = pct/100.0
                for k in ["CP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
                    t[k] += f * d.get(k, 0)
                t["DP"] += f * d.get("CP", 0) * d.get("DC", 0)
                break
    return t

def compute_total_oil_percentage(formula):
    oils = set(get_oil_ingredients().keys())
    return sum(pct for ing, pct in formula.items() if ing in oils)

def evaluate_difference(pct_diff, standard_value=None):
    if standard_value is not None and standard_value == 0:
        if abs(pct_diff) < 0.001:
            return {"label": "🎯 مطابق (صفر)", "color": "#0d5302", "bg": "#c8e6c9", "score": 100}
        return {"label": "⚠️ يجب أن يكون صفراً", "color": "#ef6c00", "bg": "#fff3e0", "score": 40}
    a = abs(pct_diff)
    if a <= 0.5: return {"label": "🎯 مطابق", "color": "#0d5302", "bg": "#c8e6c9", "score": 100}
    if a <= 2.0: return {"label": "🌟 ممتاز", "color": "#1b5e20", "bg": "#dcedc8", "score": 95}
    if a <= 5.0: return {"label": "✅ جيد جداً", "color": "#2e7d32", "bg": "#e8f5e9", "score": 85}
    if a <= 10.0: return {"label": "🟢 جيد", "color": "#558b2f", "bg": "#f1f8e9", "score": 75}
    if a <= 15.0: return {"label": "⭐ مقبول", "color": "#f9a825", "bg": "#fff8e1", "score": 65}
    if a <= 25.0: return {"label": "⚠️ تحفظ", "color": "#ef6c00", "bg": "#fff3e0", "score": 50}
    if a <= 40.0: return {"label": "🟠 ضعيف", "color": "#e65100", "bg": "#ffe0b2", "score": 35}
    return {"label": "❌ غير مطابق", "color": "#c62828", "bg": "#ffebee", "score": 20}

def get_overall_rating(rows):
    if not rows: return {"label": "—", "color": "#666", "score": 0}
    scores = [r.get("score", 50) for r in rows]
    avg = sum(scores)/len(scores)
    if avg >= 95: return {"label": "🏆 ممتازة", "color": "#1b5e20", "score": avg}
    if avg >= 85: return {"label": "🌟 جيدة جداً", "color": "#2e7d32", "score": avg}
    if avg >= 70: return {"label": "✅ جيدة", "color": "#558b2f", "score": avg}
    if avg >= 55: return {"label": "⭐ مقبولة", "color": "#f9a825", "score": avg}
    return {"label": "⚠️ تحتاج تحسين", "color": "#e65100", "score": avg}


def auto_formulate_smart(available, prices, custom_std, std_key, tolerance=0.3, max_iter=50, basis="DP"):
    if not SCIPY_AVAILABLE: return {"success": False, "message": "SCIPY غير متوفرة"}
    ing_data = {}
    for ing in available:
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat: ing_data[ing] = cat[ing]; break
    valid = [i for i in available if i in ing_data]
    if len(valid) < 3: return {"success": False, "message": "3 مكونات على الأقل"}
    n = len(valid); c = [prices.get(i, 300.0) for i in valid]
    rows = {}
    for nut in ["CP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
        rows[nut] = [ing_data[i].get(nut, 0) for i in valid]
    rows["DP"] = [ing_data[i].get("CP", 0) * ing_data[i].get("DC", 0) for i in valid]
    target_key = "DP" if basis == "DP" else "CP"
    protein_row = rows[target_key]
    targets = {k: custom_std.get(k, 0) for k in ["DP","SE","NDF","ADF","Ca","P","CP"]}
    target_val = targets[target_key]
    oil_std = get_oil_standard(std_key); oil_max = oil_std["max"]
    bounds = []
    for i in valid:
        if i in get_oil_ingredients(): bounds.append((0.0, oil_max*0.6))
        elif "يوريا" in i: bounds.append((0.0, 1.0))
        elif "مولاس" in i: bounds.append((0.0, 10.0))
        elif "ملح الطعام" in i: bounds.append((0.3, 0.7))
        elif "بيكربونات" in i: bounds.append((0.0, 1.5))
        elif "مضاد سموم" in i: bounds.append((0.05, 0.25))
        elif "بريمكس" in i: bounds.append((0.15, 0.5))
        elif "إنزيم" in i: bounds.append((0.02, 0.10))
        elif "الحجر الجيري" in i: bounds.append((0.0, 8.5))
        elif "فوسفات" in i: bounds.append((0.0, 2.5))
        elif "تبن" in i or "قش" in i: bounds.append((0.0, 25.0))
        else: bounds.append((0.0, 100.0))
    oil_ind = [1.0 if i in get_oil_ingredients() else 0.0 for i in valid]
    has_oils = sum(oil_ind) > 0
    try:
        A_eq = [[1.0]*n, protein_row]; b_eq = [100.0, target_val*100.0]
        A_ub = [[-1.0*x for x in rows["SE"]], [1.0*x for x in rows["NDF"]], [1.0*x for x in rows["ADF"]]]
        b_ub = [-1.0*targets["SE"]*100.0, targets["NDF"]*1.15*100.0, targets["ADF"]*1.15*100.0]
        if has_oils: A_ub.append(oil_ind); b_ub.append(oil_max*100.0)
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        if not res.success:
            for relax in [1.05, 1.10, 1.20]:
                b_ub_r = [-1.0*targets["SE"]*100.0*(2-relax), targets["NDF"]*relax*100.0, targets["ADF"]*relax*100.0]
                if has_oils: b_ub_r.append(oil_max*100.0)
                res = linprog(c, A_ub=A_ub, b_ub=b_ub_r, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
                if res.success: break
    except Exception as e: return {"success": False, "message": f"خطأ: {e}"}
    if not res.success: return {"success": False, "message": "تعذر إيجاد حل — أضف مكونات"}
    best = None; best_score = float('inf')
    cur_t = target_val; cur_se = targets["SE"]; cur_ndf = targets["NDF"]; cur_adf = targets["ADF"]
    for it in range(max_iter):
        try:
            A_eq = [[1.0]*n, protein_row, rows["Ca"], rows["P"]]
            b_eq = [100.0, cur_t*100.0, targets["Ca"]*100.0, targets["P"]*100.0]
            A_ub = [[-1.0*x for x in rows["SE"]], [1.0*x for x in rows["NDF"]], [1.0*x for x in rows["ADF"]]]
            b_ub = [-1.0*cur_se*100.0, cur_ndf*1.10*100.0, cur_adf*1.10*100.0]
            if has_oils: A_ub.append(oil_ind); b_ub.append(oil_max*100.0)
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs',
                          options={'presolve': True, 'time_limit': 15})
        except: res = None
        if res is None or not res.success:
            try:
                A_eq = [[1.0]*n, protein_row, rows["Ca"]]
                b_eq = [100.0, cur_t*100.0, targets["Ca"]*100.0]
                A_ub_s = [[-1.0*x for x in rows["SE"]]]
                b_ub_s = [-1.0*cur_se*100.0]
                if has_oils: A_ub_s.append(oil_ind); b_ub_s.append(oil_max*100.0)
                res = linprog(c, A_ub=A_ub_s, b_ub=b_ub_s, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
            except: res = None
        if res is None or not res.success:
            cur_ndf *= 1.05; cur_adf *= 1.05; continue
        formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
        actual = compute_formula_nutrients(formula)
        total_oil = compute_total_oil_percentage(formula)
        errors = {}
        for k in ["DP", "CP", "SE", "NDF", "ADF", "Ca", "P"]:
            tv = targets.get(k, 0)
            if tv > 0: errors[k] = abs(actual.get(k, 0) - tv) / tv
        weights = {"DP": 5.0, "CP": 5.0, "SE": 3.0, "NDF": 1.5, "ADF": 1.0, "Ca": 1.0, "P": 1.0}
        score = sum(errors.get(k, 0) * weights.get(k, 0) for k in errors)
        if score < best_score:
            best_score = score
            best = {"success": True, "formula": formula, "cost": res.fun/100.0,
                    "actual_nutrients": actual,
                    "dp_error": abs(actual["DP"] - targets["DP"]),
                    "cp_error": abs(actual["CP"] - targets.get("CP", 0)),
                    "se_error": abs(actual["SE"] - targets["SE"]),
                    "ndf_error": abs(actual["NDF"] - targets["NDF"]),
                    "adf_error": abs(actual["ADF"] - targets["ADF"]),
                    "ca_error": abs(actual.get("Ca", 0) - targets["Ca"]),
                    "p_error": abs(actual.get("P", 0) - targets["P"]),
                    "total_oil": total_oil, "oil_std": oil_std,
                    "iterations": it+1, "targets": targets, "basis": basis}
        tgt_err = errors.get(target_key, 1) * 100
        if (tgt_err <= tolerance and errors.get("SE", 1)*100 <= tolerance*2 and
            errors.get("NDF", 1)*100 <= tolerance*5 and errors.get("Ca", 1)*100 <= tolerance*15):
            best["perfect_match"] = True; break
        actual_prot = actual.get(target_key, 0)
        cur_t += (target_val - actual_prot) * 0.25
        cur_se += (targets["SE"] - actual["SE"]) * 0.20
        cur_ndf += (targets["NDF"] - actual["NDF"]) * 0.15
        cur_adf += (targets["ADF"] - actual["ADF"]) * 0.15
        cur_t = max(5.0, min(45.0, cur_t)); cur_se = max(10.0, min(90.0, cur_se))
        cur_ndf = max(5.0, min(70.0, cur_ndf)); cur_adf = max(3.0, min(50.0, cur_adf))
    if best: return best
    return {"success": False, "message": "تعذر حل دقيق"}

def auto_add_salts(animal_type, requirement=None):
    salt = {}
    if animal_type in ["أغنام", "ماعز", "أبقار", "إبل"]: salt["بيكربونات الصوديوم"] = 0.75
    salt["مضاد سموم فطرية"] = 0.20
    salt["ملح الطعام"] = 0.50
    if animal_type in ["دواجن", "سمان"]:
        salt["الحجر الجيري"] = 8.0 if (requirement and requirement.Ca > 2.0) else 1.5
        salt["فوسفات ثنائي الكالسيوم"] = 1.5
        salt["بريمكس تسمين دواجن"] = 0.30
    elif animal_type == "أسماك":
        salt["الحجر الجيري"] = 1.0; salt["فوسفات ثنائي الكالسيوم"] = 1.5; salt["بريمكس أسماك"] = 0.30
    elif animal_type == "خيول":
        salt["الحجر الجيري"] = 1.5; salt["فوسفات ثنائي الكالسيوم"] = 1.5; salt["بريمكس خيول"] = 0.30
    elif animal_type == "إبل":
        salt["الحجر الجيري"] = 2.0; salt["فوسفات ثنائي الكالسيوم"] = 1.5; salt["بريمكس إبل"] = 0.30
    else:
        salt["الحجر الجيري"] = 2.0; salt["فوسفات ثنائي الكالسيوم"] = 1.5; salt["بريمكس مجترات"] = 0.30
    return salt


# ═══ بدائل الحليب ═══
MILK_REPLACER_STANDARDS = {
    "عجول (Calves)": {"CP": 24.0, "Fat": 24.0, "Lactose": 45.0, "notes": "عمر 1-6 أسابيع"},
    "حملان (Lambs)": {"CP": 24.0, "Fat": 24.0, "Lactose": 40.0, "notes": "≥ 24% دهن"},
    "جديان (Goat Kids)": {"CP": 24.0, "Fat": 24.0, "Lactose": 42.0, "notes": "بديل الجديان"},
    "إبل (Camel Calves)": {"CP": 26.0, "Fat": 28.0, "Lactose": 38.0, "notes": "بروتين ودهن أعلى"},
    "أمهار (Foals)": {"CP": 22.0, "Fat": 20.0, "Lactose": 45.0, "notes": "توازن للخيول"},
}

MILK_REPLACER_INGREDIENTS = {
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

def formulate_milk_replacer(animal_type, selected=None):
    if not SCIPY_AVAILABLE: return {"success": False, "message": "SCIPY غير متوفرة"}
    standard = MILK_REPLACER_STANDARDS.get(animal_type)
    if not standard: return {"success": False, "message": "غير مدعوم"}
    valid = [i for i in (selected or list(MILK_REPLACER_INGREDIENTS.keys())) if i in MILK_REPLACER_INGREDIENTS]
    if len(valid) < 3: return {"success": False, "message": "3 مكونات على الأقل"}
    n = len(valid); c = [MILK_REPLACER_INGREDIENTS[i]["price"] for i in valid]
    A_eq = [[1.0]*n, [MILK_REPLACER_INGREDIENTS[i]["CP"] for i in valid],
            [MILK_REPLACER_INGREDIENTS[i]["Fat"] for i in valid]]
    b_eq = [100.0, standard["CP"]*100, standard["Fat"]*100]
    try:
        res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=[(0, 100)]*n, method='highs')
    except Exception as e: return {"success": False, "message": f"خطأ: {e}"}
    if not res.success: return {"success": False, "message": "تعذر التركيب"}
    formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
    return {"success": True, "formula": formula, "cost_per_100kg": res.fun/100.0,
            "cost_per_kg": res.fun/10000.0}


# ═══ OCR ═══
def extract_ingredients_from_image(image_bytes):
    if not OCR_AVAILABLE: return {"success": False, "message": "pytesseract غير مثبتة"}
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None: return {"success": False, "message": "تعذر قراءة الصورة"}
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY); gray = cv2.medianBlur(gray, 3)
        texts = []
        for t in [gray, cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)]:
            try:
                txt = pytesseract.image_to_string(t, lang='ara+eng', config=r'--oem 3 --psm 6')
                if txt.strip(): texts.append(txt)
            except: continue
        if not texts: return {"success": False, "message": "لا نص"}
        full = "\n".join(texts)
        ingredients = {}
        for line in full.split('\n'):
            if len(line.strip()) < 3: continue
            m = re.search(r'([\u0600-\u06FFa-zA-Z\s]+?)[\s:\-=]+(\d+\.?\d*)\s*%', line)
            if m:
                name, val = m.group(1).strip(), float(m.group(2))
                if 0.1 < val <= 100 and len(name) > 2:
                    for cat in BIG_FEEDS_LIBRARY.values():
                        for ing_name in cat:
                            if ing_name in name or name in ing_name:
                                ingredients[ing_name] = val; break
        return {"success": True, "ingredients": ingredients, "raw_text": full, "count": len(ingredients)}
    except Exception as e: return {"success": False, "message": f"خطأ: {str(e)}"}


# ═══ الرسوم البيانية الملونة ═══
def create_colorful_bar_chart(standard, actual):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        nutrients = [n for n in ["CP","DP","SE","NDF","ADF","EE","ASH"] if n in standard]
        if not nutrients: return None
        std_vals = [standard[n] for n in nutrients]
        act_vals = [actual.get(n, 0) for n in nutrients]
        fig, ax = plt.subplots(figsize=(9, 4.5))
        x = np.arange(len(nutrients)); width = 0.35
        bars1 = ax.bar(x - width/2, std_vals, width, label='المعيار', color='#1976d2', edgecolor='#0d47a1', linewidth=1.5)
        bars2 = ax.bar(x + width/2, act_vals, width, label='المحسوب', color='#43a047', edgecolor='#1b5e20', linewidth=1.5)
        for bar in bars1:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height(), f'{bar.get_height():.1f}',
                    ha='center', va='bottom', fontsize=9, color='#0d47a1', fontweight='bold')
        for bar in bars2:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height(), f'{bar.get_height():.1f}',
                    ha='center', va='bottom', fontsize=9, color='#1b5e20', fontweight='bold')
        ax.set_xlabel('العنصر', fontsize=11, fontweight='bold')
        ax.set_ylabel('القيمة', fontsize=11, fontweight='bold')
        ax.set_title('مقارنة العناصر الغذائية', fontsize=13, fontweight='bold', color='#1b5e20')
        ax.set_xticks(x); ax.set_xticklabels(nutrients); ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3, linestyle='--'); ax.set_facecolor('#fafafa')
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=110, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except: return None

def create_colorful_pie_chart(formula):
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2: return None
    try:
        colors = ['#e53935','#8e24aa','#3949ab','#1e88e5','#00897b','#43a047','#7cb342','#fdd835','#fb8c00','#6d4c41']
        names = list(formula.keys()); vals = list(formula.values())
        fig, ax = plt.subplots(figsize=(8, 5))
        wedges, texts, autotexts = ax.pie(vals, autopct='%1.1f%%', colors=colors[:len(names)],
            startangle=90, pctdistance=0.75, wedgeprops=dict(edgecolor='white', linewidth=2))
        for t in autotexts: t.set_color('white'); t.set_fontweight('bold'); t.set_fontsize(9)
        ax.legend(names, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9, title="المكونات")
        ax.set_title('توزيع المكونات', fontsize=13, fontweight='bold', color='#1b5e20')
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=110, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except: return None

def create_radar_chart(standard, actual):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        nutrients = [n for n in ["CP","DP","SE","NDF","ADF","EE","Ca","P"] if n in standard and standard[n] > 0]
        if len(nutrients) < 3: return None
        std_norm = [100.0 for _ in nutrients]
        act_norm = [(actual.get(n, 0)/standard[n])*100 for n in nutrients]
        angles = np.linspace(0, 2*np.pi, len(nutrients), endpoint=False).tolist()
        std_norm += std_norm[:1]; act_norm += act_norm[:1]; angles += angles[:1]
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, std_norm, 'o-', linewidth=2.5, color='#1976d2', label='المعيار')
        ax.fill(angles, std_norm, alpha=0.15, color='#1976d2')
        ax.plot(angles, act_norm, 'o-', linewidth=2.5, color='#43a047', label='المحسوب')
        ax.fill(angles, act_norm, alpha=0.25, color='#43a047')
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(nutrients, fontsize=10)
        ax.set_ylim(0, max(max(std_norm), max(act_norm))*1.2)
        ax.set_title('المقارنة %', fontsize=12, fontweight='bold', color='#1b5e20', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
        ax.grid(True, alpha=0.3); ax.set_facecolor('#fafafa')
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=110, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except: return None

def create_gauge_chart(score):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect='equal'))
        colors_g = ['#c62828','#ef6c00','#f9a825','#7cb342','#43a047','#1b5e20']
        for i, c in enumerate(colors_g):
            theta1 = 180 - i*30; theta2 = 180 - (i+1)*30
            ax.add_patch(Wedge((0, 0), 1, theta2, theta1, width=0.3, facecolor=c, edgecolor='white', linewidth=2))
        angle = 180 - (score/100)*180
        rad = np.radians(angle)
        ax.plot([0, 0.85*np.cos(rad)], [0, 0.85*np.sin(rad)], color='#1a1a1a', linewidth=3, zorder=10)
        ax.add_patch(Circle((0, 0), 0.08, color='#1a1a1a', zorder=11))
        ax.text(0, -0.25, f'{score:.0f}%', ha='center', fontsize=20, fontweight='bold', color='#1b5e20')
        ax.text(0, -0.5, 'التقييم', ha='center', fontsize=11, color='#666')
        ax.set_xlim(-1.2, 1.2); ax.set_ylim(-0.7, 1.2); ax.axis('off'); ax.set_facecolor('white')
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=110, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except: return None


# ═══ PDFGenerator مع الختم والتوقيع ═══
class PDFGenerator:
    def __init__(self):
        self.font_name = font_mgr.font_name
        self.font_bold = font_mgr.font_bold
        self.logo_path = None
        for lp in LOGO_OPTIONS + PHOTO_OPTIONS:
            if os.path.exists(lp): self.logo_path = lp; break

    def _ar(self, text):
        if text is None: return ""
        try: return get_display(arabic_reshaper.reshape(str(text)), base_dir='R')
        except: return str(text)

    def _draw_page(self, canvas_obj, doc):
        try:
            canvas_obj.saveState()
            w, h = doc.pagesize
            # خلفية مائية
            canvas_obj.setFillColor(HexColor('#e8f5e9')); canvas_obj.setFont(self.font_name, 60)
            try: canvas_obj.setFillAlpha(0.07)
            except: pass
            canvas_obj.saveState(); canvas_obj.translate(w/2, h/2); canvas_obj.rotate(45)
            canvas_obj.drawCentredString(0, 0, self._ar("تاور نولجي")); canvas_obj.restoreState()
            try: canvas_obj.setFillAlpha(1)
            except: pass
            # الهيدر
            canvas_obj.setFillColor(HexColor('#1b5e20')); canvas_obj.rect(0, h-90, w, 90, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#d4af37')); canvas_obj.rect(0, h-95, w, 5, fill=1, stroke=0)
            try:
                if self.logo_path:
                    canvas_obj.drawImage(self.logo_path, 30, h-78, width=60, height=60, preserveAspectRatio=True, anchor='sw', mask='auto')
            except: pass
            canvas_obj.setFillColor(white); canvas_obj.setFont(self.font_name, 22)
            canvas_obj.drawCentredString(w/2, h-38, self._ar("تاور نولجي  Tawor Nology"))
            canvas_obj.setFont(self.font_name, 12); canvas_obj.setFillColor(HexColor('#e8f5e9'))
            canvas_obj.drawCentredString(w/2, h-58, self._ar("للإنتاج الحيواني وتغذية الحيوان"))
            canvas_obj.setFont(self.font_name, 10); canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.drawCentredString(w/2, h-76, self._ar(f"إشراف: {SUPERVISOR} — {SUPERVISOR_TITLE}"))
            # الفوتر
            canvas_obj.setFillColor(HexColor('#1b5e20')); canvas_obj.rect(0, 42, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#d4af37')); canvas_obj.rect(0, 84, w, 3, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#ffeb3b')); canvas_obj.setFont(self.font_name, 10)
            canvas_obj.drawCentredString(w/2, 68, self._ar(f"🤲 {DUA_SHORT} 🤲"))
            canvas_obj.setFillColor(HexColor('#c8e6c9')); canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(w/2, 52, self._ar("اللهم اجعل قبرهما روضة من رياض الجنة"))
            canvas_obj.setFillColor(HexColor('#1b5e20')); canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(white); canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(w/2, 27, self._ar("تاور نولجي Tawor Nology © 2026"))
            canvas_obj.setFont(self.font_name, 7)
            canvas_obj.drawCentredString(w/2, 12, self._ar(f"صفحة {canvas_obj.getPageNumber()} | جميع الحقوق محفوظة"))
            # QR
            try:
                qr = qrcode.QRCode(version=1, box_size=3, border=1); qr.add_data(PLATFORM_URL); qr.make(fit=True)
                qi = qr.make_image(fill_color="#1b5e20", back_color="white")
                buf = io.BytesIO(); qi.save(buf, format="PNG"); buf.seek(0)
                canvas_obj.drawImage(RLImage(buf), w/2-20, 46, width=40, height=40)
            except: pass

            # ═══ 🎯 الختم الرسمي (استعادة كاملة) ═══
            try:
                sx, sy = w - 105, 145
                canvas_obj.setStrokeColor(HexColor('#c62828'))
                canvas_obj.setLineWidth(3.5); canvas_obj.circle(sx, sy, 72, stroke=1, fill=0)
                canvas_obj.setLineWidth(2.0); canvas_obj.circle(sx, sy, 64, stroke=1, fill=0)
                canvas_obj.setLineWidth(0.8); canvas_obj.circle(sx, sy, 58, stroke=1, fill=0)
                canvas_obj.setLineWidth(1.8)
                for ang in [-45, 45, 135, 225]:
                    rad = np.radians(ang)
                    canvas_obj.line(sx + 58*np.cos(rad), sy + 58*np.sin(rad),
                                    sx + 72*np.cos(rad), sy + 72*np.sin(rad))
                canvas_obj.setFillColor(HexColor('#c62828'))
                canvas_obj.setFont(self.font_name, 9.5)
                canvas_obj.drawCentredString(sx, sy+42, self._ar("تاور نولجي"))
                canvas_obj.drawCentredString(sx, sy+30, self._ar("Tawor Nology"))
                canvas_obj.setFont(self.font_name, 8)
                canvas_obj.drawCentredString(sx, sy+16, self._ar("م. عبدالقادر"))
                canvas_obj.drawCentredString(sx, sy+4, self._ar("إسماعيل تاور"))
                canvas_obj.setFont(self.font_name, 6.5)
                canvas_obj.drawCentredString(sx, sy-12, self._ar("اختصاصي تغذية الحيوان"))
                canvas_obj.drawCentredString(sx, sy-24, self._ar("معتمد رسمياً"))
                canvas_obj.drawCentredString(sx, sy-36, self._ar("© 2026"))
            except: pass
            canvas_obj.restoreState()
        except: pass

    def _comparison_table(self, standard, calculated):
        labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم", "SE": "معادل النشاء",
                  "NDF": "NDF", "ADF": "ADF", "EE": "دهن", "ASH": "رماد", "Ca": "Ca", "P": "P"}
        header = [self._ar(x) for x in ["العنصر", "المعيار", "المحسوب", "الفرق", "الفرق %", "التقييم"]]
        data = [header]
        cmds = [('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')), ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 9), ('GRID', (0, 0), (-1, -1), 1, HexColor('#9e9e9e')),
                ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7)]
        row = 1
        for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
            if k not in standard: continue
            sv = standard[k]; cv = calculated.get(k, 0.0)
            diff = cv - sv; pct = (diff/sv*100) if sv else 0
            ev = evaluate_difference(pct, standard_value=sv)
            data.append([self._ar(labels.get(k, k)), f"{sv:.2f}", f"{cv:.2f}",
                         f"{diff:+.3f}", f"{pct:+.2f}%", self._ar(ev["label"])])
            cmds.append(('BACKGROUND', (0, row), (-1, row), HexColor(ev["bg"])))
            row += 1
        t = Table(data, colWidths=[100, 70, 70, 70, 70, 105])
        t.setStyle(TableStyle(cmds)); return t

    def _oil_table(self, formula, std_key):
        oils = get_oil_ingredients()
        rows = [(ing, pct) for ing, pct in formula.items() if ing in oils]
        std = get_oil_standard(std_key); total = sum(p for _, p in rows)
        if not rows: return (None, 0.0, std)
        data = [[self._ar("الزيت"), self._ar("النسبة %"), self._ar("kcal/kg")]]
        for ing, pct in rows: data.append([self._ar(ing), f"{pct:.2f}%", f"{pct*90:.0f}"])
        data.append([self._ar("الإجمالي"), f"{total:.2f}%", f"{total*90:.0f}"])
        cmds = [('BACKGROUND', (0, 0), (-1, 0), HexColor('#e65100')), ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10), ('GRID', (0, 0), (-1, -1), 1, HexColor('#bf360c')),
                ('BACKGROUND', (0, -1), (-1, -1), HexColor('#ffe0b2'))]
        t = Table(data, colWidths=[250, 100, 135]); t.setStyle(TableStyle(cmds))
        return (t, total, std)

    def generate_report(self, formula, requirement, animal_type, breed, cost, city, local_cost,
                        local_sym, requester_name="", protein_basis="DP", standard_key=""):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []
        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text), ParagraphStyle('s', fontName=self.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color), spaceAfter=6, leading=size*1.6))
        story.append(P("تقرير فني رسمي — تركيب علفة", size=20, align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))
        info = [[self._ar("👤 طالب الخدمة:"), self._ar(requester_name or "—")],
                [self._ar("📍 الموقع:"), self._ar(city)],
                [self._ar("🐾 الفصيل:"), self._ar(f"{animal_type} — {breed}")],
                [self._ar("🧬 أساس الحساب:"), self._ar(protein_basis)],
                [self._ar("📅 التاريخ:"), datetime.now().strftime('%Y-%m-%d | %H:%M')]]
        ct = Table(info, colWidths=[150, 340])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
            ('BACKGROUND', (1, 0), (1, -1), HexColor('#fafafa')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')),
            ('INNERGRID', (0, 0), (-1, -1), 0.6, HexColor('#c8e6c9')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 9), ('BOTTOMPADDING', (0, 0), (-1, -1), 9)]))
        story.append(ct); story.append(Spacer(1, 15))
        standard_vals = requirement_to_standard(requirement)
        calculated_vals = compute_formula_nutrients(formula)
        scores = []
        for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
            if k not in standard_vals: continue
            sv = standard_vals[k]; cv = calculated_vals.get(k, 0.0)
            pct = ((cv-sv)/sv*100) if sv else 0
            scores.append({"score": evaluate_difference(pct, standard_value=sv)["score"]})
        overall = get_overall_rating(scores)
        story.append(P("📊 مقارنة العناصر", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        story.append(self._comparison_table(standard_vals, calculated_vals))
        story.append(Spacer(1, 12))
        oil_tbl, total_oil, oil_std = self._oil_table(formula, standard_key)
        story.append(P("🌰 الزيوت", size=14, color='#e65100'))
        story.append(Spacer(1, 8))
        if oil_tbl is None: story.append(P("ℹ️ لا زيوت.", size=11, color='#666'))
        else: story.append(oil_tbl); story.append(Spacer(1, 8))
        story.append(P(f"الحد: {oil_std['max']}% | المثالي: {oil_std['optimal']}% | {oil_std['source']}",
                       size=10, color='#bf360c'))
        story.append(Spacer(1, 15))
        # ═══ الرسوم البيانية ═══
        story.append(P("📈 الرسوم البيانية", size=14, color='#1b5e20'))
        story.append(Spacer(1, 10))
        c1 = create_colorful_bar_chart(standard_vals, calculated_vals)
        if c1:
            try: story.append(RLImage(c1, width=450, height=250)); story.append(Spacer(1, 12))
            except: pass
        c2 = create_colorful_pie_chart(formula); c3 = create_radar_chart(standard_vals, calculated_vals)
        if c2 and c3:
            try:
                row = [[RLImage(c2, width=210, height=200), RLImage(c3, width=210, height=200)]]
                rt = Table(row, colWidths=[230, 230]); rt.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
                story.append(rt); story.append(Spacer(1, 12))
            except: pass
        gauge = create_gauge_chart(overall["score"])
        if gauge:
            try:
                story.append(P("🎯 التقييم", size=12, align=TA_CENTER, color='#1b5e20'))
                story.append(RLImage(gauge, width=200, height=200)); story.append(Spacer(1, 12))
            except: pass
        story.append(PageBreak())
        story.append(P("💰 التكاليف", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        cost_data = [[self._ar("البند"), self._ar("القيمة")],
                     [self._ar("التكلفة للطن ($)"), f"${cost:.2f}"],
                     [self._ar(f"التكلفة ({local_sym})"), f"{local_cost:,.2f}"],
                     [self._ar("البروتين"), f"{requirement.DP if protein_basis == 'DP' else requirement.CP:.2f}%"]]
        tc = Table(cost_data, colWidths=[280, 210])
        tc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')), ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#2e7d32')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
        story.append(tc); story.append(Spacer(1, 18))
        if formula:
            story.append(P("🌾 المكونات للطن", size=14, color='#1b5e20'))
            story.append(Spacer(1, 8))
            ing_data = [[self._ar("المكون"), self._ar("النسبة %"), self._ar("كجم/طن")]]
            for ing, pct in formula.items():
                ing_data.append([self._ar(ing), f"{pct:.2f}%", f"{pct*10:.1f}"])
            ti = Table(ing_data, colWidths=[270, 110, 110])
            ti.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')), ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10), ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
                ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
            story.append(ti); story.append(Spacer(1, 20))
            # التوقيع
            sign = [[self._ar("توقيع طالب الخدمة"), self._ar("توقيع المختص")],
                    [self._ar("........................"), self._ar(SUPERVISOR)],
                    [self._ar("التاريخ: ..../..../........"), self._ar(SUPERVISOR_TITLE)]]
            ts = Table(sign, colWidths=[245, 245])
            ts.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BOX', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f5e9'))]))
            story.append(ts)
        doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
        buffer.seek(0); return buffer.getvalue()

pdf_gen = PDFGenerator()


# ═══ Excel ═══
def export_to_excel(standard, calculated, requester="", animal=""):
    if not OPENPYXL_AVAILABLE: return b""
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "مقارنة"; ws.sheet_view.rightToLeft = True
    hf = Font(name='Arial', size=12, bold=True, color='FFFFFF')
    hfill = PatternFill('solid', fgColor='1B5E20')
    ct = Alignment(horizontal='center', vertical='center', wrap_text=True)
    thin = Side(border_style='thin', color='9E9E9E')
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    headers = ["العنصر", "المعيار", "المحسوب", "الفرق", "% الفرق", "التقييم"]
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=c, value=h); cell.font = hf; cell.fill = hfill; cell.alignment = ct; cell.border = bd
    labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم", "SE": "معادل النشاء",
              "NDF": "NDF", "ADF": "ADF", "EE": "دهن", "ASH": "رماد", "Ca": "Ca", "P": "P"}
    row = 2
    for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
        if k not in standard: continue
        sv = standard[k]; cv = calculated.get(k, 0.0)
        diff = cv - sv; pct = (diff/sv*100) if sv else 0
        ev = evaluate_difference(pct, standard_value=sv)
        for c, v in enumerate([labels[k], round(sv, 2), round(cv, 2), round(diff, 3), round(pct, 2), ev["label"]], 1):
            cell = ws.cell(row=row, column=c, value=v); cell.alignment = ct; cell.border = bd
            cell.fill = PatternFill('solid', fgColor=ev["bg"].replace('#', ''))
        row += 1
    for c in range(1, 7): ws.column_dimensions[get_column_letter(c)].width = 22
    buf = io.BytesIO(); wb.save(buf); buf.seek(0); return buf.getvalue()


# ═══ الأسعار والصور ═══
EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"}, "ليبيا": {"rate": 4.80, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"}, "السعودية": {"rate": 3.75, "sym": "SAR"},
    "الإمارات": {"rate": 3.67, "sym": "AED"}, "باقي دول العالم": {"rate": 1.0, "sym": "USD"},
}

def get_market_prices(country, city="", state=""):
    base = {ing: 280.0 for cat in BIG_FEEDS_LIBRARY.values() for ing in cat}
    base.update({"ذرة صفراء": 230, "شعير مطحون": 210, "كسب فول صويا 44%": 440,
                 "كسب فول صويا 48%": 480, "أمباز الفول السوداني": 460,
                 "نخالة قمح (ردة)": 150, "البرسيم الجاف": 170, "مسحوق أسماك 60%": 850,
                 "الحجر الجيري": 40, "فوسفات ثنائي الكالسيوم": 280, "ملح الطعام": 30,
                 "بيكربونات الصوديوم": 340, "مضاد سموم فطرية": 950,
                 "بريمكس تسمين دواجن": 4800, "بريمكس مجترات": 4500,
                 "زيت ذرة": 1500, "زيت فول الصويا": 1350, "زيت النخيل": 1100})
    m = 1.0
    if country == "السودان": m = 1.15
    elif country == "ليبيا": m = 1.10
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
                with open(p, "rb") as f: return base64.b64encode(f.read()).decode()
            except: pass
    return None

img_base64 = get_img_b64(tuple(PHOTO_OPTIONS))


# ═══ معايير الحظائر ═══
BARN_DESIGN_STANDARDS = {
    "دواجن_لاحم": {"name_ar": "دواجن لاحم", "area_per_head": 0.10, "feeder_cm_per_head": 5.0,
        "drinker_cm_per_head": 2.5, "height_m": 2.8, "width_m": 12.0, "ach_summer": 60,
        "ach_winter": 8, "vent_open_ratio": 0.20, "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "خطية معلقة", "drinker_type": "حلمات", "aisle_m": 1.2, "central_aisle": True},
    "دواجن_بياض": {"name_ar": "دواجن بياض", "area_per_head": 0.15, "feeder_cm_per_head": 10.0,
        "drinker_cm_per_head": 2.5, "height_m": 3.0, "width_m": 12.0, "ach_summer": 40,
        "ach_winter": 6, "vent_open_ratio": 0.20, "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "سلسلة", "drinker_type": "حلمات", "aisle_m": 1.2, "central_aisle": True},
    "سمان": {"name_ar": "سمان", "area_per_head": 0.025, "feeder_cm_per_head": 2.0,
        "drinker_cm_per_head": 1.0, "height_m": 2.0, "width_m": 6.0, "ach_summer": 50,
        "ach_winter": 8, "vent_open_ratio": 0.25, "roof_type": "mono", "slope_pct": 15.0,
        "feeder_type": "خطية معدنية", "drinker_type": "حلمات", "aisle_m": 0.8, "central_aisle": False},
    "أغنام": {"name_ar": "أغنام", "area_per_head": 1.5, "feeder_cm_per_head": 35.0,
        "drinker_cm_per_head": 4.0, "height_m": 3.5, "width_m": 10.0, "ach_summer": 30,
        "ach_winter": 5, "vent_open_ratio": 0.30, "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "خطية خرسانية", "drinker_type": "حوض تلقائي", "aisle_m": 2.0, "central_aisle": True},
    "ماعز": {"name_ar": "ماعز", "area_per_head": 1.5, "feeder_cm_per_head": 35.0,
        "drinker_cm_per_head": 4.0, "height_m": 3.5, "width_m": 10.0, "ach_summer": 30,
        "ach_winter": 5, "vent_open_ratio": 0.30, "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "خطية مرتفعة", "drinker_type": "حوض تلقائي", "aisle_m": 2.0, "central_aisle": True},
    "أبقار": {"name_ar": "أبقار", "area_per_head": 5.0, "feeder_cm_per_head": 70.0,
        "drinker_cm_per_head": 6.0, "height_m": 4.5, "width_m": 15.0, "ach_summer": 25,
        "ach_winter": 4, "vent_open_ratio": 0.35, "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "خطية وسطية", "drinker_type": "حوض تلقائي", "aisle_m": 3.5, "central_aisle": True},
    "إبل": {"name_ar": "إبل", "area_per_head": 10.0, "feeder_cm_per_head": 100.0,
        "drinker_cm_per_head": 8.0, "height_m": 4.5, "width_m": 15.0, "ach_summer": 20,
        "ach_winter": 4, "vent_open_ratio": 0.40, "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "خطية مرتفعة", "drinker_type": "حوض كبير", "aisle_m": 4.0, "central_aisle": True},
    "خيول": {"name_ar": "خيول", "area_per_head": 16.0, "feeder_cm_per_head": 100.0,
        "drinker_cm_per_head": 10.0, "height_m": 4.0, "width_m": 15.0, "ach_summer": 25,
        "ach_winter": 5, "vent_open_ratio": 0.30, "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "خطية مرتفعة", "drinker_type": "حوض تلقائي", "aisle_m": 3.5, "central_aisle": True},
}

def calculate_barn_dimensions(key, count):
    std = BARN_DESIGN_STANDARDS.get(key)
    if not std: return None
    total_area = count * std["area_per_head"]
    width = std["width_m"]; length = max(total_area/width, 6.0)
    feeders = max(1, int(np.ceil(count * std["feeder_cm_per_head"] / 300)))
    drinkers = max(1, int(np.ceil(count * std["drinker_cm_per_head"] / 200)))
    volume = length * width * std["height_m"]
    roof_rise = (width/2) * (std["slope_pct"]/100.0)
    ridge = std["height_m"] + roof_rise
    apr = max(2, int(length/0.3)) if key in ["دواجن_لاحم","دواجن_بياض","سمان"] else max(2, int(length/1.5))
    return {"standard": std, "count": count, "total_area_m2": round(total_area, 2),
            "length_m": round(length, 2), "width_m": round(width, 2),
            "height_m": std["height_m"], "ridge_height_m": round(ridge, 2),
            "roof_type": std["roof_type"], "slope_pct": std["slope_pct"],
            "feeders_count": feeders, "drinkers_count": drinkers,
            "total_feeder_length_m": round(count*std["feeder_cm_per_head"]/100, 1),
            "total_drinker_length_m": round(count*std["drinker_cm_per_head"]/100, 1),
            "volume_m3": round(volume, 1),
            "vent_flow_summer_m3h": int(volume*std["ach_summer"]),
            "vent_flow_winter_m3h": int(volume*std["ach_winter"]),
            "vent_open_area_m2": round(length*std["height_m"]*std["vent_open_ratio"], 2),
            "animals_per_row": apr,
            "feeder_type": std.get("feeder_type", "خطية"),
            "drinker_type": std.get("drinker_type", "حوض"),
            "aisle_m": std.get("aisle_m", 1.5),
            "central_aisle": std.get("central_aisle", True)}


# ═══ المجسم 3D ═══
def create_barn_3d_figure(dims):
    if not PLOTLY_AVAILABLE: return None
    try:
        std = dims["standard"]; L = dims["length_m"]; W = dims["width_m"]
        H = dims["height_m"]; RH = dims["ridge_height_m"]
        aisle = dims.get("aisle_m", 1.5); feeder_w = 0.6
        fig = go.Figure()
        fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[0, 0, 0, 0],
            i=[0, 0], j=[1, 2], k=[2, 3], color='#d7ccc8', opacity=0.65, name='الأرضية', hoverinfo='skip'))
        for xp in [0, L]:
            fig.add_trace(go.Mesh3d(x=[xp]*4, y=[0, W, W, 0], z=[0, 0, H, H],
                i=[0, 0], j=[1, 2], k=[2, 3], color='#a1887f', opacity=0.35, showlegend=False, hoverinfo='skip'))
        for yp in [0, W]:
            fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[yp]*4, z=[0, 0, H, H],
                i=[0, 0], j=[1, 2], k=[2, 3], color='#a1887f', opacity=0.35, showlegend=False, hoverinfo='skip'))
        if dims["roof_type"] == "gable":
            fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W/2, W/2], z=[H, H, RH, RH],
                i=[0, 0], j=[1, 2], k=[2, 3], color='#8d6e63', opacity=0.5, name='السقف', hoverinfo='skip'))
            fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[W/2, W/2, W, W], z=[RH, RH, H, H],
                i=[0, 0], j=[1, 2], k=[2, 3], color='#8d6e63', opacity=0.5, showlegend=False, hoverinfo='skip'))
        else:
            fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[RH, RH, H, H],
                i=[0, 0], j=[1, 2], k=[2, 3], color='#8d6e63', opacity=0.5, name='السقف', hoverinfo='skip'))
        vent_h = H * std["vent_open_ratio"]
        for yv in [0.15, W-0.15]:
            fig.add_trace(go.Scatter3d(x=[1, L-1, L-1, 1, 1], y=[yv]*5,
                z=[H*0.35, H*0.35, H*0.35+vent_h, H*0.35+vent_h, H*0.35],
                mode='lines', line=dict(color='#1976d2', width=8),
                name='فتحة تهوية' if yv == 0.15 else None, showlegend=(yv == 0.15)))
        # المعالف كصناديق 3D
        if dims.get("central_aisle", True) and W > 8:
            feeder_pos = [W/2 - aisle/2 - feeder_w, W/2 + aisle/2]
        else:
            feeder_pos = [0.8, W - 1.4]
        for idx, yp in enumerate(feeder_pos):
            x_v = [0.5, L-0.5, L-0.5, 0.5, 0.5, L-0.5, L-0.5, 0.5]
            y_v = [yp, yp, yp+feeder_w, yp+feeder_w, yp, yp, yp+feeder_w, yp+feeder_w]
            z_v = [0, 0, 0, 0, 0.35, 0.35, 0.35, 0.35]
            fig.add_trace(go.Mesh3d(x=x_v, y=y_v, z=z_v,
                i=[0,0,4,4,0,0,3,3,0,0,1,1], j=[1,2,6,7,4,5,2,6,3,7,5,6],
                k=[2,3,5,6,5,1,6,7,7,4,6,2], color='#ff8f00', opacity=0.85,
                name=f'معلف ({dims.get("feeder_type","خطي")})' if idx == 0 else None,
                showlegend=(idx == 0), hoverinfo='skip'))
        # السقايات
        nd = dims["drinkers_count"]
        for i in range(nd):
            xc = (i+0.5) * (L/nd)
            yc = W - aisle - 0.5 if dims.get("central_aisle", True) else W - 1.5
            fig.add_trace(go.Scatter3d(x=[xc], y=[yc], z=[0.4], mode='markers+text',
                marker=dict(size=14, color='#1976d2', symbol='diamond', line=dict(color='#0d47a1', width=2)),
                text=[f'م{i+1}'], textposition='top center', textfont=dict(size=9, color='#0d47a1'),
                name=f'مسقى ({dims.get("drinker_type","حوض")})' if i == 0 else None, showlegend=(i == 0)))
        # الحيوانات
        apr = dims["animals_per_row"]; nrows = max(1, dims["count"]//max(apr, 1))
        step = max(1, nrows//25); xs, ys, zs = [], [], []
        for ri in range(0, nrows, step):
            if dims.get("central_aisle", True) and W > 8:
                yp = aisle + (ri//2)*(W/2 - aisle)/max(nrows//2, 1) if ri % 2 == 0 else (ri//2)*(W/2 - aisle)/max(nrows//2, 1) + 0.5
            else:
                yp = 2.0 + ri*(W-3.0)/max(nrows, 1)
            for col in range(min(apr, 20)):
                xs.append(0.8 + col*(L-1.6)/min(apr, 20)); ys.append(yp); zs.append(0.2)
        if xs:
            fig.add_trace(go.Scatter3d(x=xs, y=ys, z=zs, mode='markers',
                marker=dict(size=4, color='#1b5e20', opacity=0.8), name=f'الحيوانات ({dims["count"]})'))
        fig.add_trace(go.Scatter3d(x=[0, L], y=[-1, -1], z=[0, 0], mode='lines+text',
            line=dict(color='#c62828', width=4), text=['', f'الطول {L} م'],
            textposition='middle right', textfont=dict(size=11, color='#c62828'), showlegend=False))
        fig.update_layout(
            title=dict(text=f"🏗️ {std['name_ar']} — {dims['count']} رأس | {dims['total_area_m2']} م²",
                       font=dict(size=15, color='#1b5e20')),
            scene=dict(xaxis=dict(title='الطول'), yaxis=dict(title='العرض'), zaxis=dict(title='الارتفاع'),
                       aspectmode='data', camera=dict(eye=dict(x=1.6, y=-1.6, z=1.2))),
            height=700, margin=dict(l=0, r=0, t=90, b=0), paper_bgcolor='white',
            legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.9)', bordercolor='#2e7d32', borderwidth=1))
        return fig
    except: return None


def create_barn_animation_gif(dims, frames=30, fps=8):
    if not MATPLOTLIB_AVAILABLE or not PIL_AVAILABLE: return None
    try:
        std = dims["standard"]; L = dims["length_m"]; W = dims["width_m"]
        H = dims["height_m"]; RH = dims["ridge_height_m"]
        aisle = dims.get("aisle_m", 1.5); fw = 0.6
        fig = plt.figure(figsize=(8, 6)); ax = fig.add_subplot(111, projection='3d')
        def draw():
            ax.clear()
            floor = [[(0,0,0),(L,0,0),(L,W,0),(0,W,0)]]
            ax.add_collection3d(Poly3DCollection(floor, facecolors='#d7ccc8', edgecolors='#5d4037', alpha=0.75, linewidths=1.5))
            walls = [[(0,0,0),(L,0,0),(L,0,H),(0,0,H)], [(0,W,0),(L,W,0),(L,W,H),(0,W,H)],
                     [(0,0,0),(0,W,0),(0,W,H),(0,0,H)], [(L,0,0),(L,W,0),(L,W,H),(L,0,H)]]
            ax.add_collection3d(Poly3DCollection(walls, facecolors='#a1887f', edgecolors='#5d4037', alpha=0.4, linewidths=1))
            if dims["roof_type"] == "gable":
                r1 = [[(0,0,H),(L,0,H),(L,W/2,RH),(0,W/2,RH)]]
                r2 = [[(0,W/2,RH),(L,W/2,RH),(L,W,H),(0,W,H)]]
                ax.add_collection3d(Poly3DCollection(r1, facecolors='#8d6e63', edgecolors='#4e342e', alpha=0.55, linewidths=1))
                ax.add_collection3d(Poly3DCollection(r2, facecolors='#8d6e63', edgecolors='#4e342e', alpha=0.55, linewidths=1))
            vh = H * std["vent_open_ratio"]
            for yv in [0.15, W-0.15]:
                ax.plot([1, L-1, L-1, 1, 1], [yv]*5,
                        [H*0.35, H*0.35, H*0.35+vh, H*0.35+vh, H*0.35],
                        color='#1976d2', linewidth=2.5, label='فتحة تهوية' if yv < 1 else None)
            if dims.get("central_aisle", True) and W > 8:
                fpos = [W/2 - aisle/2 - fw, W/2 + aisle/2]
            else:
                fpos = [0.8, W-1.4]
            for yp in fpos:
                fb = [[(0.5, yp, 0.35), (L-0.5, yp, 0.35), (L-0.5, yp+fw, 0.35), (0.5, yp+fw, 0.35)],
                      [(0.5, yp, 0), (0.5, yp+fw, 0), (0.5, yp+fw, 0.35), (0.5, yp, 0.35)],
                      [(L-0.5, yp, 0), (L-0.5, yp+fw, 0), (L-0.5, yp+fw, 0.35), (L-0.5, yp, 0.35)]]
                ax.add_collection3d(Poly3DCollection(fb, facecolors='#ff8f00', edgecolors='#e65100', alpha=0.9, linewidths=1))
            nd = dims["drinkers_count"]
            xd = [(i+0.5)*(L/nd) for i in range(nd)]
            yd = [W - aisle - 0.5 if dims.get("central_aisle", True) else W - 1.5]*len(xd)
            ax.scatter(xd, yd, [0.4]*len(xd), s=120, c='#1976d2', marker='D', label='مسقى', depthshade=False, edgecolors='#0d47a1')
            apr = dims["animals_per_row"]; nr = max(1, dims["count"]//max(apr, 1))
            ss = max(1, nr//15); xa, ya = [], []
            for ri in range(0, nr, ss):
                if dims.get("central_aisle", True) and W > 8:
                    yp = aisle + (ri//2)*(W/2 - aisle)/max(nr//2, 1) if ri % 2 == 0 else (ri//2)*(W/2 - aisle)/max(nr//2, 1) + 0.5
                else:
                    yp = 2.0 + ri*(W-3.0)/max(nr, 1)
                for col in range(min(apr, 15)):
                    xa.append(0.8 + col*(L-1.6)/min(apr, 15)); ya.append(yp)
            ax.scatter(xa, ya, [0.2]*len(xa), s=25, c='#1b5e20', alpha=0.85, label=f'حيوانات ({dims["count"]})', depthshade=False)
            ax.set_xlim(0, L); ax.set_ylim(0, W); ax.set_zlim(0, RH + 1)
            ax.set_xlabel('الطول'); ax.set_ylabel('العرض'); ax.set_zlabel('الارتفاع')
            ax.set_title(f"🏗️ {std['name_ar']} — {dims['count']} رأس", fontsize=13, color='#1b5e20', fontweight='bold')
            ax.legend(loc='upper left', fontsize=8)
        def anim(fn):
            draw(); ax.view_init(elev=20, azim=(fn/frames)*360); return fig,
        a = animation.FuncAnimation(fig, anim, frames=frames, interval=1000//fps, blit=False)
        tmp = tempfile.NamedTemporaryFile(suffix='.gif', delete=False); tmp_path = tmp.name; tmp.close()
        try:
            a.save(tmp_path, writer='pillow', fps=fps, dpi=80)
            with open(tmp_path, 'rb') as f: data = f.read()
            os.unlink(tmp_path); plt.close(fig)
            return io.BytesIO(data)
        except:
            try: os.unlink(tmp_path)
            except: pass
            plt.close(fig); return None
    except: return None


def render_barn_to_pdf_image(dims):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        std = dims["standard"]; L = dims["length_m"]; W = dims["width_m"]
        H = dims["height_m"]; RH = dims["ridge_height_m"]
        aisle = dims.get("aisle_m", 1.5); fw = 0.6
        fig = plt.figure(figsize=(10, 7)); ax = fig.add_subplot(111, projection='3d')
        floor = [[(0,0,0),(L,0,0),(L,W,0),(0,W,0)]]
        ax.add_collection3d(Poly3DCollection(floor, facecolors='#d7ccc8', edgecolors='#5d4037', alpha=0.75, linewidths=1.5))
        walls = [[(0,0,0),(L,0,0),(L,0,H),(0,0,H)], [(0,W,0),(L,W,0),(L,W,H),(0,W,H)],
                 [(0,0,0),(0,W,0),(0,W,H),(0,0,H)], [(L,0,0),(L,W,0),(L,W,H),(L,0,H)]]
        ax.add_collection3d(Poly3DCollection(walls, facecolors='#a1887f', edgecolors='#5d4037', alpha=0.4, linewidths=1))
        if dims["roof_type"] == "gable":
            r1 = [[(0,0,H),(L,0,H),(L,W/2,RH),(0,W/2,RH)]]; r2 = [[(0,W/2,RH),(L,W/2,RH),(L,W,H),(0,W,H)]]
            ax.add_collection3d(Poly3DCollection(r1, facecolors='#8d6e63', edgecolors='#4e342e', alpha=0.55, linewidths=1))
            ax.add_collection3d(Poly3DCollection(r2, facecolors='#8d6e63', edgecolors='#4e342e', alpha=0.55, linewidths=1))
        vh = H * std["vent_open_ratio"]
        for yv in [0.15, W-0.15]:
            ax.plot([1, L-1, L-1, 1, 1], [yv]*5,
                    [H*0.35, H*0.35, H*0.35+vh, H*0.35+vh, H*0.35], color='#1976d2', linewidth=2.5,
                    label='فتحة تهوية' if yv < 1 else None)
        if dims.get("central_aisle", True) and W > 8: fpos = [W/2 - aisle/2 - fw, W/2 + aisle/2]
        else: fpos = [0.8, W-1.4]
        for yp in fpos:
            fb = [[(0.5, yp, 0.35), (L-0.5, yp, 0.35), (L-0.5, yp+fw, 0.35), (0.5, yp+fw, 0.35)],
                  [(0.5, yp, 0), (0.5, yp+fw, 0), (0.5, yp+fw, 0.35), (0.5, yp, 0.35)],
                  [(L-0.5, yp, 0), (L-0.5, yp+fw, 0), (L-0.5, yp+fw, 0.35), (L-0.5, yp, 0.35)]]
            ax.add_collection3d(Poly3DCollection(fb, facecolors='#ff8f00', edgecolors='#e65100', alpha=0.9, linewidths=1))
        nd = dims["drinkers_count"]
        xd = [(i+0.5)*(L/nd) for i in range(nd)]
        yd = [W - aisle - 0.5 if dims.get("central_aisle", True) else W - 1.5]*len(xd)
        ax.scatter(xd, yd, [0.4]*len(xd), s=120, c='#1976d2', marker='D', label='مسقى', depthshade=False, edgecolors='#0d47a1')
        apr = dims["animals_per_row"]; nr = max(1, dims["count"]//max(apr, 1))
        ss = max(1, nr//15); xa, ya = [], []
        for ri in range(0, nr, ss):
            if dims.get("central_aisle", True) and W > 8:
                yp = aisle + (ri//2)*(W/2 - aisle)/max(nr//2, 1) if ri % 2 == 0 else (ri//2)*(W/2 - aisle)/max(nr//2, 1) + 0.5
            else:
                yp = 2.0 + ri*(W-3.0)/max(nr, 1)
            for col in range(min(apr, 15)):
                xa.append(0.8 + col*(L-1.6)/min(apr, 15)); ya.append(yp)
        ax.scatter(xa, ya, [0.2]*len(xa), s=25, c='#1b5e20', alpha=0.85, label=f'حيوانات ({dims["count"]})', depthshade=False)
        ax.set_xlim(0, L); ax.set_ylim(0, W); ax.set_zlim(0, RH + 1)
        ax.set_xlabel('الطول (م)'); ax.set_ylabel('العرض (م)'); ax.set_zlabel('الارتفاع (م)')
        ax.set_title(f"تصميم الحظيرة — {std['name_ar']} | {dims['count']} رأس", fontsize=14, color='#1b5e20', fontweight='bold')
        ax.legend(loc='upper left', fontsize=9); ax.view_init(elev=18, azim=-55)
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except: return None


def generate_barn_pdf_report(dims):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
    story = []
    def P(t, size=11, align=TA_RIGHT, color='#1a1a1a'):
        return Paragraph(ar(t), ParagraphStyle('s', fontName=font_mgr.font_name, fontSize=size,
            alignment=align, textColor=HexColor(color), spaceAfter=6, leading=size*1.6))
    std = dims["standard"]
    story.append(P("تقرير تصميم حظيرة", size=20, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
    story.append(Spacer(1, 12))
    info = [[ar("نوع الحيوان:"), ar(std["name_ar"])], [ar("العدد:"), ar(str(dims["count"]))],
            [ar("نوع المعالف:"), ar(dims.get("feeder_type", ""))], [ar("نوع السقايات:"), ar(dims.get("drinker_type", ""))],
            [ar("التاريخ:"), datetime.now().strftime('%Y-%m-%d %H:%M')]]
    t = Table(info, colWidths=[150, 340])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')), ('BACKGROUND', (1, 0), (1, -1), HexColor('#fafafa')),
        ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')), ('INNERGRID', (0, 0), (-1, -1), 0.6, HexColor('#c8e6c9')),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'), ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
    story.append(t); story.append(Spacer(1, 15))
    dim_data = [[ar("البيان"), ar("القيمة")],
                [ar("المساحة"), ar(f"{dims['total_area_m2']} م²")],
                [ar("الأبعاد"), ar(f"{dims['length_m']} × {dims['width_m']} × {dims['height_m']} م")],
                [ar("القمة"), ar(f"{dims['ridge_height_m']} م")],
                [ar("الحجم"), ar(f"{dims['volume_m3']} م³")],
                [ar("المعالف"), ar(f"{dims['feeders_count']} ({dims['total_feeder_length_m']} م)")],
                [ar("السقايات"), ar(f"{dims['drinkers_count']} ({dims['total_drinker_length_m']} م)")],
                [ar("تهوية صيفية"), ar(f"{dims['vent_flow_summer_m3h']:,} م³/س")],
                [ar("تهوية شتوية"), ar(f"{dims['vent_flow_winter_m3h']:,} م³/س")]]
    t2 = Table(dim_data, colWidths=[220, 270])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')), ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10), ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
        ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
    story.append(t2); story.append(Spacer(1, 15))
    img = render_barn_to_pdf_image(dims)
    if img:
        try: story.append(RLImage(img, width=480, height=340))
        except: pass
    story.append(Spacer(1, 20))
    # التوقيع
    sign = [[ar("توقيع المختص")], [ar(SUPERVISOR)], [ar(SUPERVISOR_TITLE)]]
    ts = Table(sign, colWidths=[400])
    ts.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f5e9'))]))
    story.append(ts)
    doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
    buffer.seek(0); return buffer.getvalue()


# ═══ 🆕 دراسة الجدوى الفنية ═══
TECH_DATA = {
    "دواجن_لاحم": {"feed_day_g": 120, "water_day_ml": 220, "labor_per_1000": 0.3,
        "cycle_days": 42, "final_kg": 2.3, "fcr": 1.65, "prod_type": "meat",
        "notes": "دورة 42 يوم، وزن نهائي 2.3 كجم"},
    "دواجن_بياض": {"feed_day_g": 110, "water_day_ml": 250, "labor_per_1000": 0.3,
        "eggs_year": 310, "egg_g": 60, "prod_type": "eggs", "notes": "310 بيضة/دجاجة/سنة"},
    "سمان": {"feed_day_g": 28, "water_day_ml": 55, "labor_per_1000": 0.5,
        "cycle_days": 42, "final_kg": 0.25, "fcr": 2.5, "prod_type": "meat", "notes": "دورة 42 يوم"},
    "أغنام": {"feed_day_g": 1800, "water_day_ml": 6000, "labor_per_1000": 1.5,
        "milk_day_L": 1.5, "lactation_days": 200, "prod_type": "mixed", "notes": "1.5 لتر × 200 يوم"},
    "ماعز": {"feed_day_g": 1500, "water_day_ml": 6000, "labor_per_1000": 1.5,
        "milk_day_L": 2.5, "lactation_days": 280, "prod_type": "milk", "notes": "2.5 لتر × 280 يوم"},
    "أبقار": {"feed_day_g": 20000, "water_day_ml": 80000, "labor_per_1000": 5.0,
        "milk_day_L": 20, "lactation_days": 305, "prod_type": "milk", "notes": "20 لتر × 305 يوم"},
    "إبل": {"feed_day_g": 8000, "water_day_ml": 50000, "labor_per_1000": 3.0,
        "milk_day_L": 5, "lactation_days": 300, "prod_type": "milk", "notes": "5 لتر × 300 يوم"},
    "خيول": {"feed_day_g": 10000, "water_day_ml": 40000, "labor_per_1000": 4.0,
        "prod_type": "service", "notes": "خيول رياضة/عمل"},
}

def calculate_technical_feasibility(key, count):
    std = BARN_DESIGN_STANDARDS.get(key)
    if not std: return None
    dims = calculate_barn_dimensions(key, count)
    if not dims: return None
    tech = TECH_DATA.get(key, {})
    feed_day = tech.get("feed_day_g", 100) / 1000.0 * count
    water_day = tech.get("water_day_ml", 200) / 1000.0 * count
    workers = max(1, int(np.ceil(count * tech.get("labor_per_1000", 0.3) / 1000)))
    ptype = tech.get("prod_type", "meat")
    prod = {}
    if ptype == "eggs":
        eggs_year = count * tech.get("eggs_year", 300)
        prod = {"unit": "بيضة/سنة", "annual": eggs_year, "per_day": eggs_year/365,
                "weight_ton": eggs_year * tech.get("egg_g", 60) / 1_000_000,
                "details": tech.get("notes", "")}
    elif ptype == "milk":
        milk_day = count * tech.get("milk_day_L", 20)
        milk_year = milk_day * tech.get("lactation_days", 305)
        prod = {"unit": "لتر/سنة", "annual": milk_year, "per_day": milk_day,
                "lactation_days": tech.get("lactation_days", 305), "details": tech.get("notes", "")}
    elif ptype == "meat":
        cycle = tech.get("cycle_days", 42)
        cycles_year = 365/cycle
        total_kg = count * tech.get("final_kg", 2) * cycles_year
        prod = {"unit": "كجم لحم/سنة", "annual": total_kg, "cycles_year": cycles_year,
                "per_cycle": count * tech.get("final_kg", 2), "details": tech.get("notes", "")}
    elif ptype == "mixed":
        milk_day = count * tech.get("milk_day_L", 1)
        milk_year = milk_day * tech.get("lactation_days", 200)
        prod = {"unit": "لتر/سنة", "annual": milk_year, "per_day": milk_day,
                "details": tech.get("notes", "")}
    else:
        prod = {"unit": "خدمات", "annual": 0, "details": tech.get("notes", "")}
    return {"key": key, "std": std, "dims": dims, "count": count,
            "feed": {"per_head_kg": tech.get("feed_day_g", 100) / 1000.0,
                     "day_kg": feed_day, "month_ton": feed_day * 30 / 1000,
                     "year_ton": feed_day * 365 / 1000},
            "water": {"per_head_L": tech.get("water_day_ml", 200) / 1000.0,
                      "day_L": water_day, "year_m3": water_day * 365 / 1000},
            "labor": {"workers": workers, "per_worker": count // workers},
            "production": prod,
            "ventilation": {"summer": dims["vent_flow_summer_m3h"], "winter": dims["vent_flow_winter_m3h"]}}


def generate_feasibility_booklet(key, count, project_name="", requester=""):
    feas = calculate_technical_feasibility(key, count)
    if not feas: return None
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
    story = []
    def P(t, size=11, align=TA_RIGHT, color='#1a1a1a'):
        return Paragraph(ar(t), ParagraphStyle('s', fontName=font_mgr.font_name, fontSize=size,
            alignment=align, textColor=HexColor(color), spaceAfter=6, leading=size*1.6))
    std = feas["std"]; dims = feas["dims"]

    # ═══ صفحة 1: الغلاف ═══
    story.append(Spacer(1, 30))
    story.append(P("كتيّب دراسة الجدوى الفنية", size=30, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 6))
    story.append(P("Technical Feasibility Study Booklet", size=13, align=TA_CENTER, color='#666'))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=3, color=HexColor('#d4af37')))
    story.append(Spacer(1, 30))
    story.append(P(f"مشروع: {project_name or std['name_ar']}", size=18, align=TA_CENTER, color='#c62828'))
    story.append(Spacer(1, 15))
    story.append(P(f"{count} رأس من {std['name_ar']}", size=14, align=TA_CENTER, color='#1a1a1a'))
    story.append(Spacer(1, 30))
    cover = [[ar("نوع الحيوان"), ar(std["name_ar"])],
             [ar("العدد"), ar(f"{count} رأس")],
             [ar("المساحة"), ar(f"{dims['total_area_m2']} م²")],
             [ar("مقدم الطلب"), ar(requester or "—")],
             [ar("التاريخ"), ar(datetime.now().strftime('%Y-%m-%d'))]]
    t = Table(cover, colWidths=[150, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
        ('BACKGROUND', (1, 0), (1, -1), HexColor('#fafafa')),
        ('BOX', (0, 0), (-1, -1), 2, HexColor('#2e7d32')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#c8e6c9')),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10)]))
    story.append(t)
    story.append(Spacer(1, 60))
    story.append(P(f"🤲 {DUA_SHORT} 🤲", size=12, align=TA_CENTER, color='#c62828'))
    story.append(PageBreak())

    # ═══ صفحة 2: تصميم الحظيرة ═══
    story.append(P("🏗️ الباب الأول: تصميم الحظيرة", size=18, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#d4af37')))
    story.append(Spacer(1, 15))
    bd = [[ar("البيان"), ar("القيمة")],
          [ar("المساحة"), ar(f"{dims['total_area_m2']} م²")],
          [ar("الطول"), ar(f"{dims['length_m']} م")],
          [ar("العرض"), ar(f"{dims['width_m']} م")],
          [ar("ارتفاع الجدار"), ar(f"{dims['height_m']} م")],
          [ar("ارتفاع القمة"), ar(f"{dims['ridge_height_m']} م")],
          [ar("الحجم"), ar(f"{dims['volume_m3']} م³")],
          [ar("السقف"), ar("جمالوني" if dims["roof_type"] == "gable" else "أحادي")],
          [ar("الميل"), ar(f"{dims['slope_pct']}%")],
          [ar("المعالف"), ar(f"{dims['feeders_count']} ({dims['total_feeder_length_m']} م)")],
          [ar("نوع المعالف"), ar(dims.get("feeder_type", ""))],
          [ar("السقايات"), ar(f"{dims['drinkers_count']} ({dims['total_drinker_length_m']} م)")],
          [ar("نوع السقايات"), ar(dims.get("drinker_type", ""))],
          [ar("الممر"), ar(f"{dims.get('aisle_m', 1.5)} م")]]
    t = Table(bd, colWidths=[220, 230])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')), ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
    story.append(t); story.append(Spacer(1, 15))
    img = render_barn_to_pdf_image(dims)
    if img:
        try: story.append(RLImage(img, width=480, height=340))
        except: pass
    story.append(PageBreak())

    # ═══ صفحة 3: الجدوى الفنية ═══
    story.append(P("🔧 الباب الثاني: الجدوى الفنية", size=18, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#d4af37')))
    story.append(Spacer(1, 15))

    def mini(title, color, rows):
        story.append(P(title, size=13, color=color))
        story.append(Spacer(1, 5))
        data = [[ar("البند"), ar("القيمة")]] + [[ar(a), ar(b)] for a, b in rows]
        t = Table(data, colWidths=[220, 230])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(color)), ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.6, HexColor('#bdbdbd')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
        story.append(t); story.append(Spacer(1, 12))

    mini("🍽️ احتياجات العلف", '#e65100', [
        ("علف/رأس/يوم", f"{feas['feed']['per_head_kg']*1000:.0f} جرام"),
        ("إجمالي يومي", f"{feas['feed']['day_kg']:.1f} كجم"),
        ("إجمالي شهري", f"{feas['feed']['month_ton']:.2f} طن"),
        ("إجمالي سنوي", f"{feas['feed']['year_ton']:.2f} طن")])
    mini("💧 احتياجات الماء", '#1976d2', [
        ("ماء/رأس/يوم", f"{feas['water']['per_head_L']:.1f} لتر"),
        ("إجمالي يومي", f"{feas['water']['day_L']:.0f} لتر"),
        ("إجمالي سنوي", f"{feas['water']['year_m3']:.1f} م³")])
    mini("💨 التهوية", '#558b2f', [
        ("تهوية صيفية", f"{feas['ventilation']['summer']:,} م³/ساعة"),
        ("تهوية شتوية", f"{feas['ventilation']['winter']:,} م³/ساعة"),
        ("مساحة الفتحات", f"{dims['vent_open_area_m2']} م²")])
    mini("👷 العمالة", '#6d4c41', [
        ("عدد العمال", str(feas['labor']['workers'])),
        ("حيوانات/عامل", str(feas['labor']['per_worker']))])
    story.append(PageBreak())

    # ═══ صفحة 4: الإنتاج ═══
    story.append(P("📊 الباب الثالث: الإنتاج المتوقع", size=18, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#d4af37')))
    story.append(Spacer(1, 15))
    prod = feas["production"]
    story.append(P(f"نوع الإنتاج: {prod.get('unit', '—')}", size=14, color='#c62828'))
    story.append(Spacer(1, 10))
    prow = [[ar("البند"), ar("القيمة")]]
    for k, lb in [("annual", "الإنتاج السنوي"), ("per_day", "الإنتاج اليومي"),
                  ("per_cycle", "الإنتاج/دورة"), ("cycles_year", "عدد الدورات/سنة"),
                  ("lactation_days", "أيام الحلابة"), ("weight_ton", "الوزن بالطن")]:
        if k in prod and prod[k]:
            v = prod[k]
            prow.append([ar(lb), ar(f"{v:,.1f}" if isinstance(v, (int, float)) else str(v))])
    if prod.get("details"):
        prow.append([ar("التفاصيل"), ar(prod["details"])])
    t = Table(prow, colWidths=[220, 230])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')), ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
    story.append(t); story.append(Spacer(1, 20))
    story.append(P("📝 ملاحظات فنية", size=13, color='#1b5e20'))
    story.append(Spacer(1, 8))
    for n in ["• هذه الدراسة فنية فقط ولا تشمل التكاليف والأسعار.",
              "• الأرقام تقديرية وفق المعايير العالمية NRC/FAO/MWPS/ASABE.",
              f"• المساحة الموصى بها/رأس: {std['area_per_head']} م².",
              f"• طول المعلف/رأس: {std['feeder_cm_per_head']} سم.",
              "• يُنصح بإعادة التقييم كل 6 أشهر."]:
        story.append(P(n, size=10, color='#444'))
    story.append(PageBreak())

    # ═══ صفحة 5: التوقيع ═══
    story.append(Spacer(1, 60))
    story.append(P("✍️ الاعتماد والتوقيع الرسمي", size=20, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
    story.append(Spacer(1, 40))
    story.append(P("أُعدّت هذه الدراسة الفنية بمعرفة:", size=13, align=TA_CENTER, color='#1a1a1a'))
    story.append(Spacer(1, 20))
    story.append(P(SUPERVISOR, size=20, align=TA_CENTER, color='#c62828'))
    story.append(P(SUPERVISOR_TITLE, size=13, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 50))
    sig_data = [[ar("توقيع المختص"), ar("التاريخ")],
                [ar("........................"), ar(datetime.now().strftime('%Y-%m-%d'))]]
    st = Table(sig_data, colWidths=[220, 220])
    st.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 15), ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#1b5e20')),
        ('INNERGRID', (0, 0), (-1, -1), 0.8, HexColor('#c8e6c9')),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f5e9'))]))
    story.append(st); story.append(Spacer(1, 50))
    story.append(P(f"🤲 {DUA_FULL} 🤲", size=12, align=TA_CENTER, color='#c62828'))
    doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
    buffer.seek(0); return buffer.getvalue()


# ═══ Session State ═══
DEFAULTS = {
    "approved": False, "user_role": None,
    "active_formula": {}, "active_stage_title": "إنتاج عام",
    "active_animal_img": ANIMAL_IMAGES["عام"], "computed_ton_cost": 280.0,
    "inventory": {},
    "shared_comments": f"• مرحباً بكم في {APP_NAME}\n• {DUA_SHORT}\n",
    "broiler_farms": {},
    "livestock_prices": {"عجول ($)": 1350.0, "أبقار ($)": 900.0, "ضأن ($)": 180.0,
                          "ماعز ($)": 130.0, "إبل ($)": 1200.0, "كتكوت ($)": 0.65},
    "products_prices": {"لحم بقري ($/كجم)": 7.50, "لحم ضأن ($/كجم)": 9.00,
                         "لحم إبل ($/كجم)": 8.50, "لحم دجاج ($/كجم)": 3.80,
                         "طبق بيض ($)": 4.20, "حليب بقر ($/لتر)": 0.90},
    "last_formulation_result": None, "last_formulation_context": None,
    "barn_video_gif": None,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

if not st.session_state["inventory"]:
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing in cat: st.session_state["inventory"][ing] = {"quantity": 25.0}

def is_owner(): return st.session_state.get("user_role") == "owner"


# ═══ CSS ═══
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');
* { font-family: 'Cairo', 'Amiri', sans-serif; color: #1a1a1a !important; }
html, body, [data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600");
    background-size: cover; background-position: center; background-attachment: fixed;
}
.stApp { background: transparent; }
.main-box { background: rgba(255,255,255,0.98); padding: 30px; border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18); margin-bottom: 60px; backdrop-filter: blur(5px); }
.dua-main-box {
    background: linear-gradient(135deg, #0d3011 0%, #1b5e20 25%, #2e7d32 50%, #1b5e20 75%, #0d3011 100%);
    padding: 32px 28px; border-radius: 22px; border: 4px solid #d4af37; direction: rtl;
    text-align: center; margin: 25px 0; }
.dua-main-box * { color: white !important; }
.dua-main-box h3 { color: #d4af37 !important; font-size: 1.9rem; margin-bottom: 18px; font-weight: 900; }
.dua-main-box .names { display: inline-block; font-size: 1.65rem; font-weight: 900;
    color: #ffeb3b !important; margin: 20px 0; padding: 16px 30px;
    border: 2px solid #d4af37; border-radius: 15px; font-family: 'Amiri', serif !important; }
.dua-main-box p.quran { font-family: 'Amiri', serif !important; font-size: 1.2rem;
    color: #d4af37 !important; margin-top: 22px; padding: 18px 25px;
    background: rgba(0,0,0,0.25); border-radius: 12px;
    border-right: 5px solid #d4af37; border-left: 5px solid #d4af37; }
.visitor-dua-banner { background: linear-gradient(135deg, #fff8e1, #ffecb3, #ffe082);
    padding: 20px 28px; border-radius: 18px; border: 3px solid #d4af37;
    margin: 22px 0; direction: rtl; text-align: center; }
.visitor-dua-banner * { color: #4e342e !important; }
.visitor-dua-banner b { color: #c62828 !important; font-size: 1.15rem; font-family: 'Amiri', serif !important; }
.dua-fixed-banner { position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32, #1b5e20, #0d3011);
    color: white !important; padding: 11px 20px; z-index: 9998; text-align: center;
    border-top: 3px solid #d4af37; font-family: 'Amiri', serif !important;
    font-size: 1.05rem; font-weight: bold; }
.dua-fixed-banner * { color: #ffeb3b !important; }
.section-title { color: #1b5e20 !important; border-right: 6px solid #2e7d32;
    padding: 12px 18px; text-align: right; font-size: 1.5rem; font-weight: bold;
    margin-top: 30px; margin-bottom: 20px;
    background: linear-gradient(to left, rgba(46,125,50,0.15), transparent); border-radius: 10px; }
.formula-item { background: linear-gradient(135deg, #fff, #e8f5e9);
    padding: 15px 20px; border-radius: 12px; margin-bottom: 10px; font-weight: bold;
    color: #1b5e20 !important; border-right: 5px solid #2e7d32; text-align: right; }
.price-card { background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px; border-radius: 12px; border-right: 5px solid #2e7d32;
    margin-bottom: 20px; direction: rtl; text-align: right; }
.oil-info-card { background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 18px; border-radius: 12px; border-right: 5px solid #e65100;
    margin-bottom: 18px; direction: rtl; text-align: right; }
.video-card { background: linear-gradient(135deg, #fce4ec, #f8bbd0);
    padding: 18px; border-radius: 12px; border-right: 5px solid #ad1457;
    margin-bottom: 18px; direction: rtl; text-align: right; }
.feas-card { background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 20px; border-radius: 15px; border-right: 6px solid #2e7d32;
    margin-bottom: 20px; direction: rtl; text-align: right; }
.profile-img-style { width: 150px; height: 150px; border-radius: 50%; object-fit: cover;
    border: 4px solid #d4af37; box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    display: block; margin: 0 auto; }
.stButton > button { color: #1a1a1a !important; background-color: #e8f5e9 !important;
    border: 1px solid #2e7d32 !important; font-weight: bold !important; }
.stButton > button:hover { background-color: #c8e6c9 !important; }
.mini-signature { position: fixed; left: 20px; bottom: 65px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important; padding: 9px 22px; font-size: 0.88rem;
    border-radius: 25px; z-index: 9997; direction: rtl;
    border: 2px solid #d4af37; font-weight: bold; }
.mini-signature * { color: white !important; }
</style>
""", unsafe_allow_html=True)


# ═══ بوابة الدخول ═══
if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width:780px; margin:30px auto; direction:rtl;">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <p style="font-size:1.1rem; color:#a5d6a7 !important; margin-bottom:12px;">
        نبدأ باسم الله، ونسألُه أن يتقبّلَ هذا العملَ صدقةً جاريةً عن:</p>
        <div class="names">🕊️ رحم الله والدي إسماعيل تاور وأختي ابتسام 🕊️</div>
        <p class="quran">{DUA_QURAN}</p>
        <p class="quran" style="margin-top:10px;">{DUA_VERSE}</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("<hr style='border-top:2px solid #d4af37; margin:25px 0;'>", unsafe_allow_html=True)
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
    st.markdown("<h3 style='text-align:center; color:#1b5e20; margin-top:20px;'>🔐 بوابة الدخول</h3>", unsafe_allow_html=True)
    col_owner, col_guest = st.columns(2)
    with col_owner:
        st.markdown("""<div style="background:linear-gradient(135deg,#e8f5e9,#c8e6c9); padding:20px;
        border-radius:12px; border:2px solid #2e7d32; text-align:center; margin-bottom:10px;">
        <h4 style="color:#1b5e20;">👑 المالك</h4><p style="font-size:0.9rem;">كود خاص</p></div>""", unsafe_allow_html=True)
        owner_code = st.text_input("🔑 كود المالك:", type="password", key="owner_code")
        if st.button("👑 دخول المالك", type="primary", use_container_width=True):
            if owner_code.strip() == OWNER_CODE:
                st.session_state.update({"approved": True, "user_role": "owner"}); st.rerun()
            else: st.error("❌ كود غير صحيح")
    with col_guest:
        st.markdown("""<div style="background:linear-gradient(135deg,#fff8e1,#ffecb3); padding:20px;
        border-radius:12px; border:2px solid #d4af37; text-align:center; margin-bottom:10px;">
        <h4 style="color:#e65100;">👥 زائر</h4>
        <p style="font-size:0.9rem;">مجاني<br><small>حظائر 3D + جدوى + مزارع</small></p></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True):
            st.session_state.update({"approved": True, "user_role": "guest"}); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ═══ الواجهة الرئيسية ═══
st.markdown('<div class="main-box">', unsafe_allow_html=True)
c1, c2 = st.columns([0.7, 0.3])
with c2:
    role_label = "المالك 👑" if is_owner() else "زائر 👥"
    st.markdown(f"<div style='text-align:left; padding:10px; background:#f5f5f5;"
                f"border-radius:10px;'>الحساب: <b>{role_label}</b></div>", unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k != "inventory": del st.session_state[k]
        st.session_state["approved"] = False; st.rerun()
c3, c4 = st.columns([0.3, 0.7])
with c3:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)
with c4:
    st.markdown(f"<h1 style='color:#0d3011; text-align:right; font-weight:900; font-size:2.3rem;'>🌾 {APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.25rem; font-weight:600;'>{APP_TAGLINE}</p>", unsafe_allow_html=True)
    st.markdown(f"""<div style='background:linear-gradient(135deg,#fff8e1,#ffe082); padding:12px 20px;
    border-radius:12px; border-right:6px solid #c62828; border-left:6px solid #c62828; margin-top:10px;'>
    <h3 style='color:#b71c1c; text-align:right; margin:0; font-weight:900; font-size:1.55rem;'>
    👨‍🔬 {SUPERVISOR}</h3>
    <p style='color:#0d47a1; text-align:right; margin:5px 0 0 0; font-weight:700; font-size:1.15rem;'>✨ {SUPERVISOR_TITLE}</p></div>""",
    unsafe_allow_html=True)
st.markdown(f'<div class="visitor-dua-banner">{DUA_VISITOR_BANNER}</div>', unsafe_allow_html=True)
st.markdown("<hr style='border-top:3px solid #2e7d32;'>", unsafe_allow_html=True)


# ═══ التبويبات ═══
if is_owner():
    tabs_titles = ["🔬 النمذجة", "🌰 الزيوت", "🍼 بدائل الحليب", "📷 OCR",
                    "🏗️ الحظائر 3D", "📊 دراسة الجدوى", "🐔 مزارع الدجاج",
                    "📊 البورصة", "🏭 المستودعات", "🧾 الفواتير", "🖨️ الديباجة",
                    "📈 التحليلات", "💬 التعليقات", "📚 المراجع", "💡 المساعدة", "📖 الدليل"]
else:
    tabs_titles = ["🔬 النمذجة", "🌰 الزيوت", "🍼 بدائل الحليب", "📷 OCR",
                    "🏗️ الحظائر 3D", "📊 دراسة الجدوى", "🐔 مزارع الدجاج",
                    "📚 المراجع", "💡 المساعدة", "📖 الدليل"]

tabs = st.tabs(tabs_titles)
tab_map = {title: tab for title, tab in zip(tabs_titles, tabs)}


# ═══ تبويب النمذجة (مع الرسوم البيانية الملونة في UI) ═══
with tab_map["🔬 النمذجة"]:
    try:
        sub1, sub2 = st.tabs(["🎯 تركيب علفة", "🔬 مختبر الأعلاف"])
        with sub1:
            try:
                st.markdown('<div class="section-title">🌍 الموقع</div>', unsafe_allow_html=True)
                cc1, cc2, cc3 = st.columns(3)
                with cc1: country = st.selectbox("الدولة:", list(EXCHANGE_RATES.keys()), key="country")
                with cc2: state = st.text_input("الولاية:", "الخرطوم", key="state")
                with cc3: city = st.text_input("المدينة:", "الخرطوم", key="city")
                rate = EXCHANGE_RATES.get(country, {"rate": 1.0, "sym": "USD"})
                local_rate, local_sym = rate["rate"], rate["sym"]
                live_prices = get_market_prices(country, city, state)

                st.markdown('<div class="section-title">🧬 أساس الحساب</div>', unsafe_allow_html=True)
                basis_choice = st.radio("اختر:", ["البروتين المهضوم (DP) — الأدق", "البروتين الخام (CP)"],
                    horizontal=True, key="protein_basis")
                use_dp = "DP" in basis_choice; basis_code = "DP" if use_dp else "CP"

                st.markdown('<div class="section-title">🐾 الحيوان</div>', unsafe_allow_html=True)
                a_tabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐪 إبل", "🐎 خيول", "🐔 دواجن", "🦆 سمان", "🐟 أسماك"])
                animal_choice = None; production_type = None; requirement = None
                img_key = "عام"; std_key_global = ""

                with a_tabs[0]:
                    ct = st.selectbox("الحالة:", ["حليب_عالي","حليب_متوسط","حليب_منخفض","تسمين_مكثف","تسمين_عادي","حمل_أخير","صيانة"], key="cattle_type")
                    c1_, c2_ = st.columns(2); cp = {}
                    with c1_:
                        if "حليب" in ct: cp["milk"] = st.number_input("إنتاج الحليب:", 5.0, 60.0, 20.0, 1.0, key="cattle_milk")
                        cp["wt"] = st.number_input("الوزن:", 200.0, 900.0, 500.0, 25.0, key="cattle_wt")
                    with c2_:
                        req_pre = get_cattle_requirements(ct, **cp)
                        st.metric("DP", f"{req_pre.DP}%"); st.metric("CP", f"{req_pre.CP}%"); st.metric("SE", f"{req_pre.SE}")
                    if st.checkbox("✅ اعتماد", key="use_cattle"):
                        animal_choice="أبقار"; production_type=ct; requirement=req_pre
                        img_key="أبقار"; std_key_global=f"أبقار_{ct}"
                with a_tabs[1]:
                    sg = st.radio("الجنس:", ["ذكر","أنثى"], horizontal=True, key="sheep_g")
                    is_m = "ذكر" in sg
                    if is_m: sh_t = st.selectbox("الحالة:", ["تسمين_مكثف","تسمين_عادي","حملان_تيد"], key="sheep_t_m")
                    else: sh_t = st.selectbox("الحالة:", ["مرضعات","حامل_أخير","حامل_متوسط","صيانة"], key="sheep_t_f")
                    litter = 1
                    if sh_t == "مرضعات": litter = st.number_input("المواليد:", 1, 3, 1, 1, key="sheep_lit")
                    wt = st.number_input("الوزن:", 15.0, 120.0, 50.0, 5.0, key="sheep_wt")
                    req_pre = get_sheep_requirements(sh_t, is_male=is_m, wt=wt, litter=litter)
                    p1,p2,p3 = st.columns(3); p1.metric("DP", f"{req_pre.DP}%"); p2.metric("CP", f"{req_pre.CP}%"); p3.metric("SE", f"{req_pre.SE}")
                    if st.checkbox("✅ اعتماد", key="use_sheep"):
                        animal_choice="أغنام"; production_type=sh_t; requirement=req_pre
                        img_key="أغنام"; std_key_global=f"أغنام_{sh_t}"
                with a_tabs[2]:
                    gg = st.radio("الجنس:", ["ذكر","أنثى"], horizontal=True, key="goat_g")
                    is_m = "ذكر" in gg; milk_g = 0
                    if is_m: gt = st.selectbox("الحالة:", ["تسمين_جديان","تيوس"], key="goat_t_m")
                    else:
                        gt = st.selectbox("الحالة:", ["حلابة_عالي","حلابة_متوسط","حامل_أخير","صيانة"], key="goat_t_f")
                        if "حلابة" in gt: milk_g = st.number_input("الحليب:", 0.5, 8.0, 2.0, 0.25, key="goat_milk")
                    req_pre = get_goat_requirements(gt, is_male=is_m, milk=milk_g)
                    p1,p2,p3 = st.columns(3); p1.metric("DP", f"{req_pre.DP}%"); p2.metric("CP", f"{req_pre.CP}%"); p3.metric("SE", f"{req_pre.SE}")
                    if st.checkbox("✅ اعتماد", key="use_goat"):
                        animal_choice="ماعز"; production_type=gt; requirement=req_pre
                        img_key="ماعز"; std_key_global=f"ماعز_{gt}"
                with a_tabs[3]:
                    cam_t = st.selectbox("الحالة:", ["نمو","تسمين","حليب","سباق","صيانة"], key="cam_t")
                    cam_wt = st.number_input("الوزن:", 100.0, 800.0, 400.0, 25.0, key="cam_wt")
                    cam_milk = 5.0
                    if cam_t == "حليب": cam_milk = st.number_input("الحليب:", 2.0, 20.0, 5.0, 0.5, key="cam_milk")
                    req_pre = get_camel_requirements(cam_t, wt=cam_wt, milk=cam_milk)
                    p1,p2,p3 = st.columns(3); p1.metric("DP", f"{req_pre.DP}%"); p2.metric("CP", f"{req_pre.CP}%"); p3.metric("SE", f"{req_pre.SE}")
                    if st.checkbox("✅ اعتماد", key="use_camel"):
                        animal_choice="إبل"; production_type=cam_t; requirement=req_pre
                        img_key="إبل"; std_key_global=f"إبل_{cam_t}"
                with a_tabs[4]:
                    ht = st.selectbox("الحالة:", ["رياضة_مكثف","رياضة_عادي","نمو_أمهار","مرضعات","صيانة"], key="horse_t")
                    hwt = st.number_input("الوزن:", 200.0, 800.0, 450.0, 25.0, key="horse_wt")
                    req_pre = get_horse_requirements(ht, wt=hwt)
                    p1,p2,p3 = st.columns(3); p1.metric("DP", f"{req_pre.DP}%"); p2.metric("CP", f"{req_pre.CP}%"); p3.metric("SE", f"{req_pre.SE}")
                    if st.checkbox("✅ اعتماد", key="use_horse"):
                        animal_choice="خيول"; production_type=ht; requirement=req_pre
                        img_key="خيول"; std_key_global=f"خيول_{ht}"
                with a_tabs[5]:
                    ps = st.radio("السلالة:", ["لاحم","بياض"], horizontal=True, key="poultry_s")
                    pa = st.number_input("العمر (أسبوع):", 1, 20, 1, 1, key="poultry_a")
                    req_pre = get_poultry_requirements(ps, pa)
                    p1,p2,p3,p4 = st.columns(4)
                    p1.metric("DP", f"{req_pre.DP}%"); p2.metric("CP", f"{req_pre.CP}%")
                    p3.metric("SE", f"{req_pre.SE}"); p4.metric("Ca", f"{req_pre.Ca}%")
                    if st.checkbox("✅ اعتماد", key="use_poultry"):
                        animal_choice="دواجن"; production_type=ps; requirement=req_pre
                        img_key="دواجن"
                        if "بادي" in req_pre.name_ar: std_key_global="دواجن_بادي"
                        elif "نامي" in req_pre.name_ar: std_key_global="دواجن_نامي"
                        elif "بياض" in req_pre.name_ar: std_key_global="دواجن_بياض"
                        else: std_key_global="دواجن_ناهي"
                with a_tabs[6]:
                    qs = st.radio("النوع:", ["تسمين","بياض"], horizontal=True, key="quail_s")
                    qa = st.number_input("العمر:", 1, 8, 1, 1, key="quail_a")
                    req_pre = get_quail_requirements(qs, qa)
                    p1,p2,p3 = st.columns(3); p1.metric("DP", f"{req_pre.DP}%"); p2.metric("CP", f"{req_pre.CP}%"); p3.metric("SE", f"{req_pre.SE}")
                    if st.checkbox("✅ اعتماد", key="use_quail"):
                        animal_choice="سمان"; production_type=qs; requirement=req_pre
                        img_key="سمان"; std_key_global="سمان_بياض" if qs=="بياض" else "سمان_بادي"
                with a_tabs[7]:
                    fs = st.selectbox("النوع:", ["البلطي","القرموط","الكارب"], key="fish_s")
                    fstg = st.selectbox("المرحلة:", ["بادئ زريعة","نمو","تسمين"], key="fish_stg")
                    req_pre = get_fish_requirements(fs, fstg)
                    p1,p2,p3 = st.columns(3); p1.metric("DP", f"{req_pre.DP}%"); p2.metric("CP", f"{req_pre.CP}%"); p3.metric("SE", f"{req_pre.SE}")
                    if st.checkbox("✅ اعتماد", key="use_fish"):
                        animal_choice="أسماك"; production_type=fstg; requirement=req_pre
                        img_key="أسماك"
                        if "بادئ" in fstg or "زريعة" in fstg: std_key_global="أسماك_بادئ"
                        elif "نمو" in fstg: std_key_global="أسماك_نمو"
                        else: std_key_global="أسماك_تسمين"

                ready = bool(animal_choice and requirement)
                if not ready:
                    st.warning("⚠️ اختر حيواناً وفعّل ✅ الاعتماد")
                    if st.session_state.get("last_formulation_result"):
                        st.markdown("### 📋 آخر نتيجة محفوظة")
                        prev = st.session_state["last_formulation_result"]
                        for ing, pct in prev["formula"].items():
                            st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.2f}%</div>', unsafe_allow_html=True)

                if ready:
                    st.markdown(f'<div class="section-title">🎯 {animal_choice} — {requirement.name_ar}</div>', unsafe_allow_html=True)
                    ic = st.columns(4)
                    ic[0].metric("DP", f"{requirement.DP}%"); ic[1].metric("CP", f"{requirement.CP}%")
                    ic[2].metric("SE", f"{requirement.SE}"); ic[3].metric("NDF", f"{requirement.NDF}%")

                    oil_info = get_oil_standard(std_key_global)
                    st.markdown(f"""<div class="oil-info-card">
                    <b>🌰 الحد الأقصى للزيوت: {oil_info['max']}%</b> | المثالي: {oil_info['optimal']}%<br>
                    المرجع: {oil_info['source']}</div>""", unsafe_allow_html=True)

                    requester_name = st.text_input("👤 اسم طالب العلفة:", placeholder="مزرعة الأمل", key="requester")

                    st.markdown('<div class="section-title">🌾 المكونات</div>', unsafe_allow_html=True)
                    selected = []; prices = {}
                    for cat_name, items in BIG_FEEDS_LIBRARY.items():
                        with st.expander(f"📁 {cat_name}", expanded=("الحبوب" in cat_name or "الأكساب" in cat_name)):
                            sub_cols = st.columns(3)
                            for idx, (ing_name, ing_data) in enumerate(items.items()):
                                with sub_cols[idx % 3]:
                                    default = ing_name in ["ملح الطعام","الحجر الجيري","فوسفات ثنائي الكالسيوم","مضاد سموم فطرية"]
                                    if animal_choice in ["أغنام","ماعز","أبقار","إبل"]:
                                        default = default or (ing_name == "بيكربونات الصوديوم")
                                    if animal_choice in ["دواجن","سمان"]:
                                        default = default or ("بريمكس" in ing_name)
                                    checked = st.checkbox(ing_name, value=default, key=f"feed_{animal_choice}_{ing_name}")
                                    current_price = live_prices.get(ing_name, 350.0)
                                    if is_owner():
                                        price_input = st.number_input(f"${ing_name}:", min_value=5.0,
                                            value=float(current_price), key=f"price_{animal_choice}_{ing_name}")
                                    else:
                                        st.markdown(f"💰 `${current_price:.2f}` / طن")
                                        price_input = current_price
                                    if checked: selected.append(ing_name); prices[ing_name] = price_input

                    c_btn1, c_btn2 = st.columns([0.7, 0.3])
                    with c_btn1:
                        run_clicked = st.button("🚀 تشغيل المحرك", type="primary", use_container_width=True, key="run_smart")
                    with c_btn2:
                        if st.session_state.get("last_formulation_result"):
                            if st.button("🗑️ مسح", use_container_width=True, key="clear"):
                                st.session_state["last_formulation_result"] = None
                                st.session_state["last_formulation_context"] = None; st.rerun()

                    if run_clicked and len(selected) >= 3:
                        auto_salts = auto_add_salts(animal_choice, requirement)
                        for sname, _ in auto_salts.items():
                            if sname not in selected:
                                selected.append(sname); prices[sname] = live_prices.get(sname, 300.0)
                        custom_std = requirement_to_standard(requirement)
                        with st.spinner(f"⏳ التركيب على أساس {basis_code}..."):
                            result = auto_formulate_smart(selected, prices, custom_std,
                                standard_key=std_key_global, tolerance=0.3, max_iter=50, basis=basis_code)
                        if result["success"]:
                            st.session_state["last_formulation_result"] = result
                            st.session_state["last_formulation_context"] = {
                                "animal_choice": animal_choice, "requirement_name": requirement.name_ar,
                                "basis_label": basis_code, "requirement": requirement,
                                "custom_standard": custom_std, "city": city,
                                "local_rate": local_rate, "local_sym": local_sym,
                                "requester_name": requester_name, "std_key_global": std_key_global,
                                "img_key": img_key, "animal_type": animal_choice}
                            st.session_state["active_formula"] = result["formula"]
                            st.session_state["computed_ton_cost"] = result["cost"]
                        else: st.error(f"❌ {result['message']}")
                    elif run_clicked:
                        st.error("⚠️ اختر 3 مكونات على الأقل")

                    if st.session_state.get("last_formulation_result"):
                        result = st.session_state["last_formulation_result"]
                        ctx = st.session_state["last_formulation_context"]
                        formula = result["formula"]; actual = result["actual_nutrients"]
                        cost = result["cost"]; total_oil = result.get("total_oil", 0.0)
                        oil_std = result.get("oil_std", get_oil_standard(std_key_global))
                        custom_std = ctx["custom_standard"]; basis_label = ctx["basis_label"]

                        rows = []; scores = []
                        labels = {"CP":"بروتين خام","DP":"بروتين مهضوم","SE":"معادل النشاء",
                                  "NDF":"NDF","ADF":"ADF","EE":"دهن","ASH":"رماد","Ca":"كالسيوم","P":"فسفور"}
                        for k, sv in custom_std.items():
                            cv = actual.get(k, 0.0); diff = cv - sv
                            pct = (diff/sv*100) if sv else 0
                            ev = evaluate_difference(pct, standard_value=sv)
                            scores.append({"score": ev["score"]})
                            rows.append({"العنصر": labels.get(k, k), "المعيار": f"{sv:.2f}",
                                "المحسوب": f"{cv:.2f}", "الفرق": f"{diff:+.3f}",
                                "الفرق %": f"{pct:+.2f}%", "التقييم": ev["label"]})
                        overall = get_overall_rating(scores)

                        st.success(f"✅ تم التركيب — {basis_label} | {overall['label']}")
                        st.markdown("### 📊 جدول المقارنة")
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                        if total_oil > 0:
                            if total_oil > oil_std["max"]:
                                st.error(f"⚠️ تجاوز الزيوت! {total_oil:.2f}% > {oil_std['max']}%")
                            else:
                                st.success(f"✅ الزيوت: {total_oil:.2f}% (المثالي {oil_std['optimal']}%)")

                        # ═══ 📈 الرسوم البيانية الملونة في UI ═══
                        st.markdown('<div class="section-title">📈 الرسوم البيانية التحليلية</div>', unsafe_allow_html=True)
                        chart1, chart2 = st.columns(2)
                        with chart1:
                            bar_buf = create_colorful_bar_chart(custom_std, actual)
                            if bar_buf:
                                st.image(bar_buf.getvalue(), caption="مقارنة العناصر: المعيار vs المحسوب",
                                          use_container_width=True)
                        with chart2:
                            pie_buf = create_colorful_pie_chart(formula)
                            if pie_buf:
                                st.image(pie_buf.getvalue(), caption="توزيع المكونات في الخلطة",
                                          use_container_width=True)
                        chart3, chart4 = st.columns(2)
                        with chart3:
                            radar_buf = create_radar_chart(custom_std, actual)
                            if radar_buf:
                                st.image(radar_buf.getvalue(), caption="الرادار: نسب الإنجاز %",
                                          use_container_width=True)
                        with chart4:
                            gauge_buf = create_gauge_chart(overall["score"])
                            if gauge_buf:
                                st.image(gauge_buf.getvalue(), caption="مؤشر التقييم العام",
                                          use_container_width=True)

                        st.markdown("### 🌾 المكونات")
                        for ing, pct in formula.items():
                            st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.2f}% ({pct*10:.1f} كجم/طن)</div>', unsafe_allow_html=True)
                        st.metric("💰 التكلفة للطن:", f"${cost:.2f} ({cost*ctx['local_rate']:,.0f} {ctx['local_sym']})")

                        dl1, dl2 = st.columns(2)
                        with dl1:
                            try:
                                pdf = pdf_gen.generate_report(formula=formula, requirement=ctx["requirement"],
                                    animal_type=ctx["animal_type"], breed=ctx["requirement_name"],
                                    cost=cost, city=ctx["city"], local_cost=cost*ctx["local_rate"],
                                    local_sym=ctx["local_sym"], requester_name=ctx["requester_name"],
                                    protein_basis=basis_label, standard_key=ctx["std_key_global"])
                                st.download_button("📥 تحميل PDF", pdf,
                                    file_name=f"Tawor_{ctx['animal_type']}_{datetime.now():%Y%m%d}.pdf",
                                    mime="application/pdf", use_container_width=True)
                            except Exception as e: st.error(f"⚠️ PDF: {e}")
                        with dl2:
                            try:
                                xl = export_to_excel(custom_std, actual, ctx["requester_name"], ctx["animal_type"])
                                if xl:
                                    st.download_button("📊 تحميل Excel", xl,
                                        file_name=f"Tawor_{ctx['animal_type']}_{datetime.now():%Y%m%d}.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True)
                            except Exception as e: st.error(f"⚠️ Excel: {e}")
            except Exception as e:
                st.error(f"⚠️ خطأ: {e}")
                with st.expander("تفاصيل"): st.code(traceback.format_exc())

        with sub2:
            try:
                st.markdown('<div class="section-title">🔬 مختبر الأعلاف</div>', unsafe_allow_html=True)
                c_lab1, c_lab2 = st.columns(2)
                with c_lab1:
                    target = st.selectbox("الفصيل:", ["أبقار","أغنام","ماعز","خيول","إبل",
                        "دواجن لاحم","دواجن بياض","سمان","أسماك"], key="lab_target")
                with c_lab2:
                    stage = st.selectbox("المرحلة:", ["تسمين","حليب","حمل","صيانة"], key="lab_stage")
                target_val = st.number_input("المستهدف %", 5.0, 50.0, 15.0, 0.1, key="lab_target_v")

                st.subheader("📥 أوزان المكونات (كجم):")
                lab_inputs = {}; all_ings = []
                for cat in BIG_FEEDS_LIBRARY.values():
                    for ing in cat: all_ings.append(ing)
                cols3 = st.columns(3); seg = len(all_ings)//3 + 1
                for idx, ing_name in enumerate(all_ings):
                    with cols3[idx % 3]:
                        lab_inputs[ing_name] = st.number_input(f"{ing_name}:", 0.0, value=0.0, step=5.0, key=f"lab_{ing_name}")

                if st.button("🧪 تحليل", type="primary", use_container_width=True):
                    tw = sum(lab_inputs.values())
                    if tw > 0:
                        calc_cp = 0.0; calc_dp = 0.0; calc_se = 0.0; comps = []
                        for ing, wt in lab_inputs.items():
                            if wt > 0:
                                pct = wt/tw; icp = 0.0; idc = 0.0; ise = 0.0
                                for cat in BIG_FEEDS_LIBRARY.values():
                                    if ing in cat:
                                        icp = cat[ing].get("CP", 0); idc = cat[ing].get("DC", 0); ise = cat[ing].get("SE", 0)
                                calc_cp += pct*icp; calc_dp += pct*(icp*idc); calc_se += pct*ise
                                comps.append({"المادة": ing, "الوزن": f"{wt:.1f}", "النسبة": f"{pct*100:.2f}%"})
                        st.success("✅ تم التحليل")
                        st.markdown(f"**إجمالي:** {tw:.1f} كجم")
                        st.table(pd.DataFrame(comps))
                        st.write(f"**CP:** {calc_cp:.2f}% | **DP:** {calc_dp:.2f}% | **SE:** {calc_se:.2f}")
                    else: st.warning("⚠️ أدخل أوزاناً")
            except Exception as e: st.error(f"⚠️ {e}")
    except Exception as e:
        st.error(f"⚠️ خطأ رئيسي: {e}")


# ═══ مكتبة الزيوت ═══
with tab_map["🌰 الزيوت"]:
    try:
        st.markdown('<div class="section-title">🌰 مكتبة الزيوت</div>', unsafe_allow_html=True)
        rows = [{"الحالة": k, "الأقصى %": f"{v['max']}%", "المثالي %": f"{v['optimal']}%", "المرجع": v["source"]}
                for k, v in MAX_OIL_PERCENTAGE.items()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        oils = get_oil_ingredients()
        for cat, lst in OIL_CATEGORIES.items():
            st.markdown(f"#### {cat}")
            for ing in lst:
                if ing in oils:
                    d = oils[ing]
                    with st.expander(f"🌰 {ing}"):
                        st.write(f"⚡ SE: {d.get('SE', 0)}")
                        st.write(f"📝 {d.get('desc', '')}")
                        st.caption(f"📖 {d.get('source', '')}")
    except Exception as e: st.error(f"⚠️ {e}")


# ═══ بدائل الحليب ═══
with tab_map["🍼 بدائل الحليب"]:
    try:
        st.markdown('<div class="section-title">🍼 بدائل الحليب</div>', unsafe_allow_html=True)
        mr1, mr2 = st.columns(2)
        with mr1: ma = st.selectbox("النوع:", list(MILK_REPLACER_STANDARDS.keys()), key="mr_a")
        with mr2:
            std = MILK_REPLACER_STANDARDS[ma]
            st.markdown(f"""<div class="price-card"><b>CP: {std['CP']}% | Fat: {std['Fat']}%</b>
            <br><small>{std['notes']}</small></div>""", unsafe_allow_html=True)
        sel = []
        cols = st.columns(3)
        for i, (name, data) in enumerate(MILK_REPLACER_INGREDIENTS.items()):
            with cols[i % 3]:
                if st.checkbox(f"{name} ${data['price']}", value=(name in ["حليب مجفف منزوع الدسم","حليب مجفف كامل الدسم"]), key=f"mr_{name}"):
                    sel.append(name)
        if st.button("🧪 تركيب", type="primary", use_container_width=True):
            if len(sel) < 3: st.warning("⚠️ اختر 3 مكونات")
            else:
                r = formulate_milk_replacer(ma, sel)
                if r["success"]:
                    st.success("✅ تم")
                    for ing, pct in r["formula"].items():
                        st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.2f}%</div>', unsafe_allow_html=True)
                    st.metric("التكلفة/100كجم", f"${r['cost_per_100kg']:.2f}")
                else: st.error(f"❌ {r['message']}")
    except Exception as e: st.error(f"⚠️ {e}")


# ═══ OCR ═══
with tab_map["📷 OCR"]:
    try:
        st.markdown('<div class="section-title">📷 OCR</div>', unsafe_allow_html=True)
        if not OCR_AVAILABLE: st.error("⚠️ pytesseract غير مثبت")
        else:
            up = st.file_uploader("ارفع صورة", type=["jpg","jpeg","png"])
            if up:
                st.image(up, use_container_width=True)
                if st.button("🔍 تحليل", type="primary"):
                    with st.spinner("..."):
                        r = extract_ingredients_from_image(up.read())
                    if r["success"]:
                        st.success(f"✅ {r['count']} مادة")
                        if r["ingredients"]:
                            st.dataframe(pd.DataFrame([{"المادة": k, "النسبة": f"{v:.2f}%"} for k, v in r["ingredients"].items()]),
                                          use_container_width=True, hide_index=True)
                    else: st.error(f"❌ {r['message']}")
    except Exception as e: st.error(f"⚠️ {e}")


# ═══ الحظائر 3D ═══
with tab_map["🏗️ الحظائر 3D"]:
    try:
        st.markdown('<div class="section-title">🏗️ تصميم الحظائر 3D</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: bk = st.selectbox("النوع:", list(BARN_DESIGN_STANDARDS.keys()),
            format_func=lambda k: BARN_DESIGN_STANDARDS[k]["name_ar"], key="barn_animal")
        with c2: bc = st.number_input("العدد:", 1, 100000, 1000, 50, key="barn_count")
        with c3: bs = st.selectbox("النظام:", ["أرضي","بطاريات"], key="barn_system")

        mult = 1.0
        if "بطاريات" in bs and bk in ["دواجن_لاحم","دواجن_بياض","سمان"]: mult = 0.55
        dims = calculate_barn_dimensions(bk, bc)
        if dims and mult != 1.0:
            dims["total_area_m2"] = round(dims["total_area_m2"]*mult, 2)
            dims["length_m"] = round(dims["total_area_m2"]/dims["width_m"], 2)

        if dims:
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("📏 المساحة", f"{dims['total_area_m2']} م²")
            k2.metric("📐 الأبعاد", f"{dims['length_m']}×{dims['width_m']} م")
            k3.metric("🏔️ القمة", f"{dims['ridge_height_m']} م")
            k4.metric("📦 الحجم", f"{dims['volume_m3']} م³")
            k5, k6, k7, k8 = st.columns(4)
            k5.metric("🍽️ معالف", dims["feeders_count"])
            k6.metric("📏 طول المعالف", f"{dims['total_feeder_length_m']} م")
            k7.metric("💧 سقايات", dims["drinkers_count"])
            k8.metric("💨 تهوية صيف", f"{dims['vent_flow_summer_m3h']:,}")

            st.markdown("### 🏗️ المجسم 3D")
            fig = create_barn_3d_figure(dims)
            if fig:
                st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": True,
                            "toImageButtonOptions": {"format": "png", "filename": f"barn_{bk}"}})

            st.markdown('<div class="section-title">🎬 فيديو GIF</div>', unsafe_allow_html=True)
            if st.button("🎬 توليد فيديو GIF", type="primary", use_container_width=True, key="gen_video"):
                with st.spinner("🎥 جاري التوليد..."):
                    vb = create_barn_animation_gif(dims, frames=30, fps=8)
                if vb:
                    st.session_state["barn_video_gif"] = vb.getvalue()
                    st.success("✅ تم!")
                else: st.error("⚠️ تعذر التوليد")
            if st.session_state.get("barn_video_gif"):
                st.image(st.session_state["barn_video_gif"], use_container_width=True)
                st.download_button("⬇️ تحميل GIF", st.session_state["barn_video_gif"],
                    file_name=f"barn_{bk}_{bc}.gif", mime="image/gif",
                    use_container_width=True, type="primary")

            try:
                pdf_bytes = generate_barn_pdf_report(dims)
                st.download_button("📄 تحميل PDF الحظيرة", pdf_bytes,
                    file_name=f"Barn_{bk}_{bc}.pdf", mime="application/pdf",
                    use_container_width=True, type="primary")
            except Exception as e: st.error(f"⚠️ PDF: {e}")
    except Exception as e:
        st.error(f"⚠️ خطأ: {e}")
        with st.expander("تفاصيل"): st.code(traceback.format_exc())


# ═══ 🆕 دراسة الجدوى الفنية ═══
with tab_map["📊 دراسة الجدوى"]:
    try:
        st.markdown('<div class="section-title">📊 دراسة الجدوى الفنية</div>', unsafe_allow_html=True)
        st.markdown("""<div class="feas-card">
        <b>🎯 دراسة فنية شاملة (بدون اقتصاديات):</b><br>
        ▪️ تصميم الحظيرة بأبعادها ومساحتها<br>
        ▪️ احتياجات العلف والماء والتهوية<br>
        ▪️ الإنتاج المتوقع (لحم/حليب/بيض)<br>
        ▪️ العمالة المطلوبة<br>
        ▪️ كتيّب PDF كامل بالتوقيع الرسمي<br>
        </div>""", unsafe_allow_html=True)

        f1, f2 = st.columns(2)
        with f1:
            feas_key = st.selectbox("نوع الحيوان:", list(BARN_DESIGN_STANDARDS.keys()),
                format_func=lambda k: BARN_DESIGN_STANDARDS[k]["name_ar"], key="feas_animal")
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
            f1.metric("علف/رأس/يوم", f"{feas['feed']['per_head_kg']*1000:.0f} جم")
            f2.metric("إجمالي يومي", f"{feas['feed']['day_kg']:.1f} كجم")
            f3.metric("إجمالي شهري", f"{feas['feed']['month_ton']:.2f} طن")
            f4.metric("إجمالي سنوي", f"{feas['feed']['year_ton']:.2f} طن")

            st.markdown("### 💧 احتياجات الماء")
            w1, w2, w3 = st.columns(3)
            w1.metric("ماء/رأس/يوم", f"{feas['water']['per_head_L']:.1f} لتر")
            w2.metric("إجمالي يومي", f"{feas['water']['day_L']:.0f} لتر")
            w3.metric("إجمالي سنوي", f"{feas['water']['year_m3']:.1f} م³")

            st.markdown("### 💨 التهوية والعمالة")
            v1, v2, v3, v4 = st.columns(4)
            v1.metric("تهوية صيف", f"{feas['ventilation']['summer']:,} م³/س")
            v2.metric("تهوية شتاء", f"{feas['ventilation']['winter']:,} م³/س")
            v3.metric("عدد العمال", feas["labor"]["workers"])
            v4.metric("حيوانات/عامل", feas["labor"]["per_worker"])

            st.markdown("### 📊 الإنتاج المتوقع")
            p = feas["production"]
            st.write(f"**نوع الإنتاج:** {p.get('unit', '—')}")
            prod_cols = st.columns(3)
            if "annual" in p: prod_cols[0].metric("سنوي", f"{p['annual']:,.0f}")
            if "per_day" in p: prod_cols[1].metric("يومي", f"{p['per_day']:,.1f}")
            if "per_cycle" in p: prod_cols[2].metric("دورة", f"{p['per_cycle']:,.0f}")
            if p.get("details"): st.info(f"📝 {p['details']}")

            st.markdown("---")
            st.markdown("### 📄 كتيّب الجدوى الفني (PDF)")

            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                try:
                    booklet = generate_feasibility_booklet(feas_key, feas_count,
                        project_name=project_name, requester=feas_requester)
                    if booklet:
                        st.download_button("📥 تحميل كتيّب الجدوى الكامل (PDF)", booklet,
                            file_name=f"Feasibility_{feas_key}_{feas_count}_{datetime.now():%Y%m%d}.pdf",
                            mime="application/pdf", use_container_width=True, type="primary")
                except Exception as e:
                    st.error(f"⚠️ تعذر إنشاء الكتيّب: {e}")
            with col_dl2:
                st.markdown("""<div class="feas-card" style="background:linear-gradient(135deg,#fff8e1,#ffe082);">
                <b>📖 الكتيّب يحتوي على:</b><br>
                ▪️ الغلاف + بيانات المشروع<br>
                ▪️ تصميم الحظيرة + مجسم 3D<br>
                ▪️ الجدوى الفنية (علف، ماء، تهوية، عمالة)<br>
                ▪️ الإنتاج المتوقع<br>
                ▪️ صفحة التوقيع الرسمي + الختم<br>
                </div>""", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"⚠️ خطأ في الجدوى: {e}")
        with st.expander("تفاصيل"): st.code(traceback.format_exc())


# ═══ مزارع الدجاج ═══
with tab_map["🐔 مزارع الدجاج"]:
    try:
        st.markdown('<div class="section-title">🐔 مزارع الدجاج</div>', unsafe_allow_html=True)
        with st.expander("➕ إضافة مزرعة", expanded=True):
            n = st.text_input("اسم المزرعة:", key="nf_name")
            o = st.text_input("المالك:", key="nf_owner")
            if st.button("💾 حفظ") and n:
                st.session_state["broiler_farms"][n] = {
                    "owner": o, "data": {"age": 1, "birds": 1000, "weight_kg": 0.045,
                                          "feed_kg": 0.0, "dead": 0, "temp": 33.0, "hum": 65.0}}
                st.success(f"✅ {n}"); st.rerun()
        if st.session_state["broiler_farms"]:
            sel = st.selectbox("اختر:", [""] + list(st.session_state["broiler_farms"].keys()), key="farm_sel")
            if sel:
                d = st.session_state["broiler_farms"][sel]["data"]
                b1, b2 = st.columns(2)
                with b1:
                    d["age"] = st.number_input("العمر (يوم):", 1, 60, d["age"], key="bf_age")
                    d["birds"] = st.number_input("الطيور:", 1, value=d["birds"], key="bf_birds")
                    d["weight_kg"] = st.number_input("الوزن:", 0.0, 10.0, float(d["weight_kg"]), 0.01, key="bf_w")
                    d["feed_kg"] = st.number_input("العلف:", 0.0, float(d["feed_kg"]), 100.0, key="bf_f")
                with b2:
                    d["dead"] = st.number_input("النافق:", 0, value=d["dead"], key="bf_d")
                    d["temp"] = st.number_input("الحرارة:", 10.0, 45.0, float(d["temp"]), key="bf_t")
                    d["hum"] = st.number_input("الرطوبة:", 20.0, 90.0, float(d["hum"]), key="bf_h")
                alive = d["birds"] - d["dead"]
                gain = alive * (d["weight_kg"] - 0.045)
                adg = ((d["weight_kg"] - 0.045) * 1000 / d["age"]) if d["age"] > 0 else 0
                fcr = (d["feed_kg"] / gain) if gain > 0 else 0
                liv = 100 - (d["dead"] / d["birds"] * 100)
                epef = ((liv * d["weight_kg"]) / (d["age"] * fcr) * 100) if d["age"] > 0 and fcr > 0 else 0
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("ADG (جم)", f"{adg:.1f}"); k2.metric("FCR", f"{fcr:.2f}")
                k3.metric("EPEF", f"{epef:.0f}"); k4.metric("الحيوية %", f"{liv:.1f}")
    except Exception as e: st.error(f"⚠️ {e}")


# ═══ تبويبات المالك ═══
if is_owner():
    with tab_map["📊 البورصة"]:
        try:
            st.markdown('<div class="section-title">📊 البورصة</div>', unsafe_allow_html=True)
            t1, t2 = st.tabs(["🐄 الماشية","🥩 المنتجات"])
            with t1:
                for a, p in list(st.session_state["livestock_prices"].items()):
                    new = st.number_input(f"{a}", 0.0, value=float(p), step=0.1, key=f"lv_{a}")
                    st.session_state["livestock_prices"][a] = new
            with t2:
                for pr, p in list(st.session_state["products_prices"].items()):
                    new = st.number_input(f"{pr}", 0.0, value=float(p), step=0.05, key=f"pr_{pr}")
                    st.session_state["products_prices"][pr] = new
        except Exception as e: st.error(f"⚠️ {e}")

    with tab_map["🏭 المستودعات"]:
        try:
            st.markdown('<div class="section-title">🏭 المستودعات</div>', unsafe_allow_html=True)
            inv = st.session_state["inventory"]
            c = st.columns(4)
            c[0].metric("إجمالي", len(inv))
            c[1].metric("منخفضة", sum(1 for v in inv.values() if v.get("quantity", 0) < 5))
            c[2].metric("نفذت", sum(1 for v in inv.values() if v.get("quantity", 0) <= 0))
            c[3].metric("آمنة", sum(1 for v in inv.values() if v.get("quantity", 0) >= 5))
            cols = st.columns(3)
            for i, (name, data) in enumerate(list(inv.items())[:30]):
                with cols[i % 3]:
                    q = data["quantity"] if isinstance(data, dict) else data
                    badge = "🔴" if q <= 0 else ("🟡" if q < 5 else "🟢")
                    st.markdown(f"{badge} **{name}**: {q:.1f} طن")
                    nq = st.number_input("تحديث:", 0.0, value=float(q), key=f"inv_{name}", label_visibility="collapsed")
                    if isinstance(inv[name], dict): inv[name]["quantity"] = nq
        except Exception as e: st.error(f"⚠️ {e}")

    with tab_map["🧾 الفواتير"]:
        try:
            st.markdown('<div class="section-title">🧾 الفواتير</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1: client = st.text_input("العميل:", "مزرعة الأمل")
            with c2: tons = st.number_input("الكمية (طن):", 0.1, 1000.0, 2.0, 0.5)
            with c3: profit = st.number_input("هامش ($/طن):", 0.0, 1000.0, 50.0)
            sell = st.session_state["computed_ton_cost"] + profit
            st.markdown(f"""<div class="price-card">
            <h4>🧾 فاتورة</h4>
            <p><b>العميل:</b> {client}</p>
            <p><b>الكمية:</b> {tons} طن</p>
            <p><b>سعر الطن:</b> ${sell:.2f}</p>
            <p style="font-size:1.3rem; color:#1b5e20;"><b>الإجمالي:</b> ${sell*tons:.2f}</p></div>""",
            unsafe_allow_html=True)
        except Exception as e: st.error(f"⚠️ {e}")

    with tab_map["🖨️ الديباجة"]:
        try:
            st.markdown('<div class="section-title">🖨️ الديباجة</div>', unsafe_allow_html=True)
            brand = st.text_input("اسم البراند:", APP_NAME)
            st.markdown(f"""<div style="border:3px dashed #1b5e20; padding:30px; border-radius:15px;
            background:linear-gradient(135deg,#f1f8e9,#e8f5e9); direction:rtl; text-align:center;">
            <h2 style="color:#1b5e20;">🌟 {brand} 🌟</h2>
            <h3 style="color:#c62828;">{SUPERVISOR}</h3>
            <p style="color:#1b5e20; font-weight:bold;">🎯 {st.session_state['active_stage_title']}</p>
            <small style="color:#c62828;">🤲 {DUA_SHORT}</small></div>""", unsafe_allow_html=True)
        except Exception as e: st.error(f"⚠️ {e}")

    with tab_map["📈 التحليلات"]:
        try:
            st.markdown('<div class="section-title">📈 التحليلات</div>', unsafe_allow_html=True)
            c = st.columns(4)
            c[0].metric("الخلطات", "1,247"); c[1].metric("متوسط التكلفة", "$285")
            c[2].metric("التوفير", "18%"); c[3].metric("رضا", "96%")
            if PLOTLY_AVAILABLE:
                df = pd.DataFrame({'المادة': ['ذرة','صويا','نخالة','زيوت','أملاح','أخرى'],
                                    'نسبة': [42, 23, 14, 8, 8, 5]})
                st.plotly_chart(px.pie(df, values='نسبة', names='المادة', color_discrete_sequence=px.colors.sequential.Greens), use_container_width=True)
        except Exception as e: st.error(f"⚠️ {e}")

    with tab_map["💬 التعليقات"]:
        try:
            st.markdown('<div class="section-title">💬 التعليقات</div>', unsafe_allow_html=True)
            st.text_area("الحالية:", value=st.session_state["shared_comments"], height=200, disabled=True)
            nc = st.text_area("جديد:")
            if st.button("➕ نشر") and nc:
                st.session_state["shared_comments"] += f"\n• [{datetime.now():%Y-%m-%d %H:%M}]: {nc}"; st.rerun()
        except Exception as e: st.error(f"⚠️ {e}")


# ═══ المراجع + المساعدة + الدليل ═══
with tab_map["📚 المراجع"]:
    try:
        st.markdown('<div class="section-title">📚 المراجع</div>', unsafe_allow_html=True)
        st.markdown("""
        ### المراجع المعتمدة:
        - **NRC (2012)** — Swine | **NRC (2007)** — Small Ruminants
        - **NRC (2001)** — Dairy Cattle | **NRC (2007)** — Horses
        - **NRC (1994)** — Poultry | **INRA (2018)** — Ruminants
        - **FAO (2010)** — Camel Nutrition | **Ross 308 (2020)** — Broiler

        ### 🏗️ الحظائر:
        - MWPS-1 / MWPS-3 / FAO 2012 / ASABE Standards
        """)
    except Exception as e: st.error(f"⚠️ {e}")

with tab_map["💡 المساعدة"]:
    try:
        st.markdown('<div class="section-title">💡 المساعدة</div>', unsafe_allow_html=True)
        st.markdown(f"""
        ### الأسئلة الشائعة:
        - **DP أم CP؟** يعملان فعلياً الآن
        - **الرسوم البيانية؟** تظهر تلقائياً بعد التركيب (4 رسوم)
        - **دراسة الجدوى؟** تبويب مخصص مع كتيّب PDF كامل
        - **الختم والتوقيع؟** يظهران على كل صفحة PDF

        ### 🔧 الدعم
        📧 {OWNER_EMAIL} | 📱 {WHATSAPP_NUMBER}

        ### 🕌 دعاء
        {DUA_FULL}
        """)
    except Exception as e: st.error(f"⚠️ {e}")

with tab_map["📖 الدليل"]:
    try:
        st.markdown('<div class="section-title">📖 الدليل</div>', unsafe_allow_html=True)
        st.markdown(f"""
        ### الميزات:
        - 🐄 **8 قطاعات** حيوانية
        - 🌰 **10 زيوت** بمعايير NRC
        - 🧬 **DP/CP** يعملان فعلياً
        - 📈 **4 رسوم بيانية ملونة** في UI + PDF
        - 🏗️ **حظائر 3D + فيديو GIF**
        - 📊 **دراسة جدوى فنية** + كتيّب PDF كامل
        - ✍️ **ختم رسمي وتوقيع** على كل صفحة

        ### 🆕 جديد في 10.3:
        - ✅ استعادة **الختم والتوقيع** في كل صفحة PDF
        - ✅ **4 رسوم بيانية ملونة** في واجهة النتائج
        - ✅ **تبويب دراسة جدوى فنية** كامل
        - ✅ **كتيّب PDF (5 صفحات)** بالتوقيع
        - ✅ كل تبويب محمي بـ try/except

        ### 📞 التواصل:
        📧 {OWNER_EMAIL} | 📱 {WHATSAPP_NUMBER}
        """)
    except Exception as e: st.error(f"⚠️ {e}")


# ═══ التذييل ═══
st.markdown(f'<div class="mini-signature">🌾 {APP_NAME} | {SUPERVISOR} © 2026</div>', unsafe_allow_html=True)
st.markdown(f'<div class="dua-fixed-banner">🤲 {DUA_SHORT} 🤲</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# نهاية الملف — Tawor Nology 10.3
# ═══════════════════════════════════════════════════════════════════════════
