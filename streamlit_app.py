# ============================================================================
# تاور نولجي TAWOR NOLOGY 10.3 — ملف كامل
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

try: from scipy.optimize import linprog; SCIPY=True
except: SCIPY=False
try: import plotly.express as px, plotly.graph_objects as go; PLOTLY=True
except: PLOTLY=False
try:
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Wedge
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    from matplotlib import animation
    MPL=True
except: MPL=False
try: from PIL import Image as PILImage; PILok=True
except: PILok=False
try: import pytesseract, cv2; OCR=True
except: OCR=False
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    XL=True
except: XL=False
try:
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor, white
    from reportlab.platypus import (Table, TableStyle, Paragraph, Spacer, Image as RLImage,
                                     SimpleDocTemplate, HRFlowable, PageBreak)
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    RL=True
except: RL=False
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    AR=True
except: AR=False
try: import qrcode; QR=True
except: QR=False

DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي ابتسام"
DUA_FULL = "رحم الله والدي إسماعيل تاور وأختي ابتسام وأسكنهما فسيح جناته وجعل قبرهما روضة من رياض الجنة"
DUA_QURAN = "﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾"
DUA_VERSE = "﴿ وَقُل رَّبِّ ارْحَمْهُمَا كَمَا رَبَّيَانِي صَغِيرًا ﴾"
DUA_BANNER = "🕌 إلى زوارنا الكرام: هذه المنصة صدقةٌ جارية عن والدي إسماعيل تاور وأختي ابتسام. نسألكم الدعاء لهما 🤲"

APP_NAME = "تاور نولجي Tawor Nology"
APP_TAGLINE = "للإنتاج الحيواني وتغذية الحيوان"
SUPERVISOR = "م. عبدالقادر إسماعيل تاور"
SUPERVISOR_TITLE = "اختصاصي تغذية الحيوان"
OWNER_CODE = "202687"
PLATFORM_URL = "https://tawor-nology.streamlit.app"
WHATSAPP = "+249123533489"
EMAIL = "abukram128@gmail.com"
PHOTOS = ["14686.jpg", "1000069464.jpg", "14686.JPG"]
LOGOS = ["logo.png", "logo.jpg"]

st.set_page_config(page_title=f"{APP_NAME} | {APP_TAGLINE}", page_icon="🌾",
                   layout="wide", initial_sidebar_state="collapsed")

FONT_DIR = "fonts"; os.makedirs(FONT_DIR, exist_ok=True)

class FontMgr:
    _i = None
    def __new__(cls):
        if cls._i is None:
            cls._i = super().__new__(cls); cls._i._init()
        return cls._i
    def _init(self):
        self.name = 'Helvetica'; self.ready = False
        if not RL: return
        paths = [os.path.join(FONT_DIR, "Amiri-Regular.ttf"), "Amiri-Regular.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        for p in paths:
            if os.path.exists(p) and self._reg(p): return
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
            tgt = os.path.join(FONT_DIR, "Amiri-Regular.ttf")
            if not os.path.exists(tgt): urllib.request.urlretrieve(url, tgt)
            self._reg(tgt)
        except: pass
    def _reg(self, p):
        try:
            pdfmetrics.registerFont(TTFont('TaworAr', p))
            self.name = 'TaworAr'; self.ready = True; return True
        except: return False

fontmgr = FontMgr()

class ArProc:
    @staticmethod
    @lru_cache(maxsize=5000)
    def fix(t):
        if not t: return ""
        t = str(t)
        if not AR: return t
        try: return get_display(arabic_reshaper.reshape(t), base_dir='R')
        except: return t

def ar(t): return ArProc.fix(t)

# ═══════════════ مكتبة الأعلاف ═══════════════
FEEDS = {
    "🌾 الحبوب": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3, "Ca": 0.02, "P": 0.27},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4, "Ca": 0.02, "P": 0.26},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5, "Ca": 0.05, "P": 0.35},
        "سورجم": {"CP": 10, "DC": 0.78, "SE": 70, "NDF": 12.5, "ADF": 5.5, "EE": 3, "ASH": 1.8, "Ca": 0.03, "P": 0.30},
        "قمح محلي": {"CP": 12, "DC": 0.85, "SE": 75, "NDF": 11.5, "ADF": 3.8, "EE": 2, "ASH": 1.6, "Ca": 0.04, "P": 0.32},
        "جريش أرز": {"CP": 7.8, "DC": 0.82, "SE": 82, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2, "Ca": 0.06, "P": 0.30},
    },
    "🌱 الأكساب": {
        "أمباز الفول السوداني": {"CP": 46, "DC": 0.88, "SE": 73, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5, "Ca": 0.20, "P": 0.65},
        "كسب فول صويا 44%": {"CP": 44, "DC": 0.90, "SE": 74, "NDF": 13.5, "ADF": 8, "EE": 1.8, "ASH": 6, "Ca": 0.35, "P": 0.65},
        "كسب فول صويا 48%": {"CP": 48, "DC": 0.91, "SE": 76, "NDF": 12, "ADF": 7, "EE": 1.5, "ASH": 6.2, "Ca": 0.35, "P": 0.65},
        "كسب عباد الشمس 36%": {"CP": 36, "DC": 0.76, "SE": 42, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5, "Ca": 0.40, "P": 1.0},
        "كسب بذور القطن": {"CP": 41, "DC": 0.78, "SE": 55, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5, "Ca": 0.20, "P": 1.10},
        "كسب الكتان": {"CP": 32, "DC": 0.82, "SE": 65, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8, "Ca": 0.35, "P": 0.85},
        "كسب السمسم": {"CP": 42, "DC": 0.84, "SE": 70, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5, "Ca": 2, "P": 1.20},
        "كسب جلوتين 60%": {"CP": 60, "DC": 0.92, "SE": 85, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5, "Ca": 0.15, "P": 0.50},
        "كسب الكانولا": {"CP": 36, "DC": 0.82, "SE": 60, "NDF": 28, "ADF": 18, "EE": 3.5, "ASH": 6.5, "Ca": 0.65, "P": 1.10},
    },
    "🚜 المخلفات": {
        "نخالة قمح": {"CP": 15, "DC": 0.72, "SE": 45, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5, "Ca": 0.12, "P": 1.10},
        "البرسيم الجاف": {"CP": 16.5, "DC": 0.60, "SE": 35, "NDF": 42.5, "ADF": 32.5, "EE": 2, "ASH": 10.5, "Ca": 1.50, "P": 0.25},
        "مولاس": {"CP": 4, "DC": 0.95, "SE": 50, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5, "Ca": 0.70, "P": 0.05},
        "تبن قمح": {"CP": 3.2, "DC": 0.35, "SE": 18, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.30, "P": 0.08},
    },
    "🧬 بروتين حيواني": {
        "مسحوق أسماك 60%": {"CP": 60, "DC": 0.85, "SE": 65, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5, "Ca": 5.5, "P": 3.2},
        "مسحوق لحم وعظم": {"CP": 50, "DC": 0.75, "SE": 50, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5, "Ca": 9, "P": 4.5},
        "مسحوق الدم": {"CP": 80, "DC": 0.65, "SE": 55, "NDF": 1, "ADF": 0.5, "EE": 1.5, "ASH": 6, "Ca": 0.30, "P": 0.30},
        "مركزات دواجن": {"CP": 40, "DC": 0.85, "SE": 60, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5, "Ca": 2.5, "P": 1.20},
        "مركزات مواشي": {"CP": 36, "DC": 0.80, "SE": 55, "NDF": 15.5, "ADF": 8.5, "EE": 3, "ASH": 15.5, "Ca": 3, "P": 1.50},
    },
    "🌰 الزيوت": {
        "زيت ذرة": {"CP": 0, "DC": 0, "SE": 220, "NDF": 0, "ADF": 0, "EE": 100, "ASH": 0, "Ca": 0, "P": 0, "desc": "9000 kcal/kg", "src": "NRC 2012"},
        "زيت فول الصويا": {"CP": 0, "DC": 0, "SE": 215, "NDF": 0, "ADF": 0, "EE": 100, "ASH": 0, "Ca": 0, "P": 0, "desc": "8800 kcal/kg", "src": "Ross 308"},
        "زيت عباد الشمس": {"CP": 0, "DC": 0, "SE": 210, "NDF": 0, "ADF": 0, "EE": 100, "ASH": 0, "Ca": 0, "P": 0, "desc": "أوميغا 6", "src": "NRC 2007"},
        "زيت الكتان": {"CP": 0, "DC": 0, "SE": 205, "NDF": 0, "ADF": 0, "EE": 100, "ASH": 0, "Ca": 0, "P": 0, "desc": "أوميغا 3", "src": "NRC 2007"},
        "زيت جوز الهند": {"CP": 0, "DC": 0, "SE": 230, "NDF": 0, "ADF": 0, "EE": 100, "ASH": 0, "Ca": 0, "P": 0, "desc": "MCT", "src": "NRC 2012"},
        "زيت النخيل": {"CP": 0, "DC": 0, "SE": 215, "NDF": 0, "ADF": 0, "EE": 100, "ASH": 0, "Ca": 0, "P": 0, "desc": "8700 kcal/kg", "src": "NRC 2012"},
        "زيت الكانولا": {"CP": 0, "DC": 0, "SE": 200, "NDF": 0, "ADF": 0, "EE": 100, "ASH": 0, "Ca": 0, "P": 0, "desc": "متوازن", "src": "NRC 2012"},
        "زيت الزيتون": {"CP": 0, "DC": 0, "SE": 210, "NDF": 0, "ADF": 0, "EE": 100, "ASH": 0, "Ca": 0, "P": 0, "desc": "أوميغا 9", "src": "INRA 2018"},
        "شحم حيواني": {"CP": 0, "DC": 0, "SE": 230, "NDF": 0, "ADF": 0, "EE": 100, "ASH": 0, "Ca": 0, "P": 0, "desc": "9500 kcal/kg", "src": "NRC 2012"},
        "زيت السمك": {"CP": 0, "DC": 0, "SE": 235, "NDF": 0, "ADF": 0, "EE": 100, "ASH": 0, "Ca": 0, "P": 0, "desc": "EPA/DHA", "src": "NRC Fish"},
    },
    "🧪 أحماض أمينية": {
        "ليسين نقي": {"CP": 94, "DC": 1, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 0.5, "Ca": 0, "P": 0},
        "ميثيونين نقي": {"CP": 58, "DC": 1, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 0.3, "Ca": 0, "P": 0},
        "ثريونين نقي": {"CP": 72, "DC": 1, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 0.2, "Ca": 0, "P": 0},
    },
    "🔬 بريمكسات": {
        "بريمكس دواجن": {"CP": 0, "DC": 0, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 100, "Ca": 18, "P": 8},
        "بريمكس بياض": {"CP": 0, "DC": 0, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 100, "Ca": 22, "P": 7},
        "بريمكس مجترات": {"CP": 0, "DC": 0, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 100, "Ca": 18, "P": 9},
        "بريمكس خيول": {"CP": 0, "DC": 0, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 100, "Ca": 15, "P": 8},
        "بريمكس إبل": {"CP": 0, "DC": 0, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 100, "Ca": 20, "P": 10},
        "بريمكس أسماك": {"CP": 0, "DC": 0, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 100, "Ca": 15, "P": 7},
        "إنزيم فايتيز": {"CP": 0, "DC": 0, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 5, "Ca": 0, "P": 0},
    },
    "🪨 معادن": {
        "الحجر الجيري": {"CP": 0, "DC": 0, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 99.5, "Ca": 38, "P": 0},
        "فوسفات ثنائي كالسيوم": {"CP": 0, "DC": 0, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 98.5, "Ca": 23, "P": 18},
        "ملح الطعام": {"CP": 0, "DC": 0, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 99.9, "Ca": 0, "P": 0},
        "بيكربونات صوديوم": {"CP": 0, "DC": 0, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 99, "Ca": 0, "P": 0},
        "يوريا": {"CP": 287, "DC": 0.95, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 1, "Ca": 0, "P": 0},
        "مضاد سموم": {"CP": 0, "DC": 0, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 85, "Ca": 0, "P": 0},
    },
}

OIL_STD = {
    "دواجن_بادي": {"max": 8, "optimal": 5, "src": "Ross 308"},
    "دواجن_نامي": {"max": 7, "optimal": 4.5, "src": "Ross 308"},
    "دواجن_ناهي": {"max": 7, "optimal": 4, "src": "Ross 308"},
    "دواجن_بياض": {"max": 5, "optimal": 2.5, "src": "NRC 1994"},
    "سمان_بادي": {"max": 6, "optimal": 4, "src": "NRC Quail"},
    "سمان_بياض": {"max": 5, "optimal": 2.5, "src": "NRC Quail"},
    "أبقار_حليب_عالي": {"max": 6, "optimal": 4, "src": "NRC 2001"},
    "أبقار_حليب_متوسط": {"max": 5, "optimal": 3.5, "src": "NRC 2001"},
    "أبقار_حليب_منخفض": {"max": 5, "optimal": 3, "src": "NRC 2001"},
    "أبقار_تسمين_مكثف": {"max": 6, "optimal": 4.5, "src": "NRC 2001"},
    "أبقار_تسمين_عادي": {"max": 5, "optimal": 3.5, "src": "NRC 2001"},
    "أبقار_حمل_أخير": {"max": 5, "optimal": 3.5, "src": "NRC 2001"},
    "أبقار_صيانة": {"max": 4, "optimal": 2.5, "src": "NRC 2001"},
    "أغنام_تسمين_مكثف": {"max": 5, "optimal": 3.5, "src": "NRC 2007"},
    "أغنام_تسمين_عادي": {"max": 4.5, "optimal": 3, "src": "NRC 2007"},
    "أغنام_حملان_تيد": {"max": 4.5, "optimal": 3, "src": "NRC 2007"},
    "أغنام_مرضعات": {"max": 5, "optimal": 3.5, "src": "NRC 2007"},
    "أغنام_حامل_أخير": {"max": 5, "optimal": 3.5, "src": "NRC 2007"},
    "أغنام_حامل_متوسط": {"max": 4.5, "optimal": 3, "src": "NRC 2007"},
    "أغنام_صيانة": {"max": 3.5, "optimal": 2, "src": "NRC 2007"},
    "ماعز_تسمين_جديان": {"max": 5, "optimal": 3.5, "src": "NRC 2007"},
    "ماعز_تيوس": {"max": 4.5, "optimal": 3, "src": "NRC 2007"},
    "ماعز_حلابة_عالي": {"max": 5, "optimal": 3.5, "src": "NRC 2007"},
    "ماعز_حلابة_متوسط": {"max": 5, "optimal": 3.5, "src": "NRC 2007"},
    "ماعز_حامل_أخير": {"max": 5, "optimal": 3.5, "src": "NRC 2007"},
    "ماعز_صيانة": {"max": 3.5, "optimal": 2, "src": "NRC 2007"},
    "إبل_نمو": {"max": 5, "optimal": 3.5, "src": "FAO 2010"},
    "إبل_تسمين": {"max": 6, "optimal": 4, "src": "FAO 2010"},
    "إبل_حليب": {"max": 5, "optimal": 3.5, "src": "FAO 2010"},
    "إبل_سباق": {"max": 8, "optimal": 6, "src": "FAO 2010"},
    "إبل_صيانة": {"max": 3.5, "optimal": 2, "src": "FAO 2010"},
    "خيول_رياضة_مكثف": {"max": 10, "optimal": 7, "src": "NRC 2007 Horses"},
    "خيول_رياضة_عادي": {"max": 8, "optimal": 5, "src": "NRC 2007 Horses"},
    "خيول_نمو_أمهار": {"max": 8, "optimal": 5, "src": "NRC 2007 Horses"},
    "خيول_مرضعات": {"max": 8, "optimal": 5.5, "src": "NRC 2007 Horses"},
    "خيول_صيانة": {"max": 5, "optimal": 3, "src": "NRC 2007 Horses"},
    "أسماك_بادئ": {"max": 15, "optimal": 10, "src": "NRC Fish"},
    "أسماك_نمو": {"max": 12, "optimal": 8, "src": "NRC Fish"},
    "أسماك_تسمين": {"max": 12, "optimal": 8, "src": "NRC Fish"},
}

def get_oil_std(k): return OIL_STD.get(k, {"max": 5, "optimal": 3, "src": "NRC"})
def get_oils(): return FEEDS.get("🌰 الزيوت", {})

@dataclass
class Req:
    DP: float; CP: float; SE: float; NDF: float; ADF: float
    EE: float; ASH: float; Ca: float; P: float
    name: str = ""; note: str = ""

def req_cattle(t, milk=20, wt=500):
    if t == "حليب_عالي":
        dp = 12.5 + milk*0.30
        return Req(dp, dp/0.70, 60+milk*0.35, 30, 19, 5.5, 8, 0.55+milk*0.003, 0.33+milk*0.0015, "حلابة عالية", f"{milk}كجم")
    if t == "حليب_متوسط":
        dp = 11.0 + milk*0.25
        return Req(dp, dp/0.72, 55+milk*0.30, 33, 21, 4.5, 8, 0.50+milk*0.0025, 0.30+milk*0.0012, "حلابة متوسطة", f"{milk}كجم")
    if t == "حليب_منخفض":
        dp = 9.5 + milk*0.20
        return Req(dp, dp/0.75, 50+milk*0.25, 38, 24, 4, 8.5, 0.45+milk*0.002, 0.28+milk*0.001, "حلابة منخفضة", f"{milk}كجم")
    if t == "تسمين_مكثف": return Req(11.5, 14.5, 72, 32, 20, 4.5, 7.5, 0.65, 0.38, "تسمين مكثف", "ADG>1.3")
    if t == "تسمين_عادي": return Req(9.5, 12, 65, 38, 24, 4, 7.5, 0.55, 0.32, "تسمين عادي", "ADG~0.8")
    if t == "حمل_أخير": return Req(11.5, 14.5, 67, 35, 22, 4.2, 8, 0.70, 0.42, "حمل آخر", "")
    return Req(7.5, 10, 53, 45, 28, 3, 8.5, 0.42, 0.26, "صيانة", "")

def req_sheep(t, male=True, wt=50, litter=1):
    if male:
        if t == "تسمين_مكثف": return Req(11.5, 14.5, 64, 28, 17, 4, 8, 0.65, 0.36, "تسمين مكثف", "ADG>250g")
        if t == "تسمين_عادي": return Req(9.5, 12, 59, 33, 21, 3.6, 8, 0.55, 0.32, "تسمين عادي", "")
        return Req(8.5, 11, 55, 38, 24, 3.2, 8.5, 0.50, 0.30, "حملان تيد", "")
    if t == "مرضعات":
        dp = 10.5 + (litter-1)*1.5
        return Req(dp, dp/0.72, 60+(litter-1)*5, 30, 19, 4.5, 8.5, 0.65+(litter-1)*0.10, 0.38+(litter-1)*0.05, f"مرضعات({litter})", "")
    if t == "حامل_أخير": return Req(10.5, 13.5, 62, 32, 20, 3.8, 8, 0.60, 0.35, "حامل آخر", "")
    if t == "حامل_متوسط": return Req(8.5, 11, 55, 38, 24, 3.4, 8, 0.50, 0.30, "حامل متوسط", "")
    return Req(7.2, 9.5, 48, 45, 28, 3, 8.5, 0.42, 0.26, "صيانة", "")

def req_goat(t, male=True, milk=2):
    if male:
        if t == "تسمين_جديان": return Req(11, 14, 62, 30, 19, 3.8, 8, 0.62, 0.34, "تسمين جديان", "")
        return Req(9, 11.5, 57, 36, 22, 3.5, 8, 0.55, 0.30, "تيوس", "")
    if t == "حلابة_عالي":
        dp = 11.5 + milk*0.45
        return Req(dp, dp/0.70, 58+milk*0.45, 29, 18, 4.5, 8.5, 0.60+milk*0.008, 0.35+milk*0.004, f"حلابة({milk})", "")
    if t == "حلابة_متوسط":
        dp = 10.0 + milk*0.35
        return Req(dp, dp/0.72, 55+milk*0.40, 32, 20, 4, 8.5, 0.55+milk*0.006, 0.32+milk*0.003, f"حلابة({milk})", "")
    if t == "حامل_أخير": return Req(10, 13, 60, 33, 21, 3.8, 8, 0.60, 0.35, "حامل", "")
    return Req(6.8, 9, 46, 46, 28, 3, 8.5, 0.42, 0.26, "صيانة", "")

def req_camel(t, wt=400, milk=5):
    if t == "نمو": return Req(10.5, 13.5, 60, 38, 24, 4, 8, 0.65, 0.38, "نمو", f"{wt}kg")
    if t == "تسمين": return Req(9.5, 12, 65, 35, 22, 4.5, 7.5, 0.60, 0.35, "تسمين", f"{wt}kg")
    if t == "حليب":
        dp = 12.0 + milk*0.25
        return Req(dp, dp/0.70, 62+milk*0.40, 32, 20, 5, 8.5, 0.70+milk*0.006, 0.40+milk*0.003, f"حلابة({milk})", "")
    if t == "سباق": return Req(14, 17, 72, 28, 17, 6, 9, 0.85, 0.50, "سباق", "")
    return Req(7, 9, 48, 48, 30, 3.5, 9, 0.42, 0.26, "صيانة", f"{wt}kg")

def req_horse(t, wt=450):
    if t == "رياضة_مكثف": return Req(10.5, 13.5, 70, 30, 18, 7, 7.5, 0.70, 0.40, "رياضة مكثف", "")
    if t == "رياضة_عادي": return Req(9, 11.5, 63, 36, 22, 5, 7.5, 0.55, 0.32, "رياضة عادي", "")
    if t == "نمو_أمهار": return Req(12, 15, 65, 30, 18, 5, 8, 0.75, 0.42, "أمهار", "")
    if t == "مرضعات": return Req(12.5, 16, 68, 32, 20, 5.5, 8, 0.80, 0.45, "مرضعات", "")
    return Req(7.2, 9.5, 53, 46, 29, 3.5, 8, 0.45, 0.28, "صيانة", "")

def req_poultry(strain, age=1):
    if strain == "لاحم":
        if age <= 1: return Req(20, 23, 76, 8, 4, 5, 6.5, 1, 0.50, "بادي", "3000")
        if age <= 3: return Req(18.5, 21, 74, 9, 5, 5, 6, 0.90, 0.45, "نامي", "3100")
        if age <= 5: return Req(17, 19.5, 75, 10, 5.5, 4.5, 6, 0.87, 0.43, "ناهي", "3150")
        return Req(16.5, 19, 75, 10, 5.5, 4.5, 6, 0.85, 0.42, "ناهي+", "3200")
    if age <= 6: return Req(17, 20, 72, 10, 5.5, 4, 7, 1, 0.50, "بادي بياض", "")
    if age <= 18: return Req(14.5, 17, 70, 12, 6.5, 4, 9, 1.5, 0.45, "نامي بياض", "")
    return Req(15.5, 18, 72, 11, 6, 4.2, 11.5, 3.8, 0.45, "بياض", "")

def req_quail(strain, age=1):
    if strain == "بياض": return Req(15, 18, 68, 11, 5.5, 4.5, 9, 2.5, 0.45, "سمان بياض", "")
    if age <= 2: return Req(20.5, 24, 74, 8, 4, 5.5, 6.5, 1, 0.55, "بادي", "")
    if age <= 4: return Req(18.5, 22, 72, 9, 4.5, 5, 6, 0.90, 0.50, "نامي", "")
    return Req(17, 20, 70, 10, 5, 4.5, 6, 0.85, 0.45, "ناهي", "")

def req_fish(sp, stage):
    if "بادئ" in stage or "زريعة" in stage: return Req(32, 40, 72, 8, 4, 10, 11, 1.5, 0.90, f"{sp} بادئ", "")
    if "نمو" in stage: return Req(25, 32, 70, 12, 6, 8, 9, 1, 0.70, f"{sp} نمو", "")
    return Req(22, 28, 68, 13, 7, 8, 9.5, 0.90, 0.65, f"{sp} تسمين", "")

def req_to_std(r):
    return {"CP": r.CP, "DP": r.DP, "SE": r.SE, "NDF": r.NDF, "ADF": r.ADF,
            "EE": r.EE, "ASH": r.ASH, "Ca": r.Ca, "P": r.P}

def calc_nutrients(formula):
    t = {"CP": 0, "DP": 0, "SE": 0, "NDF": 0, "ADF": 0, "EE": 0, "ASH": 0, "Ca": 0, "P": 0}
    for ing, pct in formula.items():
        for cat in FEEDS.values():
            if ing in cat:
                d = cat[ing]; f = pct/100
                for k in ["CP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
                    t[k] += f * d.get(k, 0)
                t["DP"] += f * d.get("CP", 0) * d.get("DC", 0)
                break
    return t

def oil_pct(formula):
    oils = set(get_oils().keys())
    return sum(p for i, p in formula.items() if i in oils)

def diff_eval(pct, sv=None):
    if sv is not None and sv == 0:
        if abs(pct) < 0.001: return {"label": "🎯 صفر", "color": "#0d5302", "bg": "#c8e6c9", "score": 100}
        return {"label": "⚠️ يجب صفر", "color": "#ef6c00", "bg": "#fff3e0", "score": 40}
    a = abs(pct)
    if a <= 0.5: return {"label": "🎯 مطابق", "color": "#0d5302", "bg": "#c8e6c9", "score": 100}
    if a <= 2: return {"label": "🌟 ممتاز", "color": "#1b5e20", "bg": "#dcedc8", "score": 95}
    if a <= 5: return {"label": "✅ جيد جداً", "color": "#2e7d32", "bg": "#e8f5e9", "score": 85}
    if a <= 10: return {"label": "🟢 جيد", "color": "#558b2f", "bg": "#f1f8e9", "score": 75}
    if a <= 15: return {"label": "⭐ مقبول", "color": "#f9a825", "bg": "#fff8e1", "score": 65}
    if a <= 25: return {"label": "⚠️ تحفظ", "color": "#ef6c00", "bg": "#fff3e0", "score": 50}
    if a <= 40: return {"label": "🟠 ضعيف", "color": "#e65100", "bg": "#ffe0b2", "score": 35}
    return {"label": "❌ غير مطابق", "color": "#c62828", "bg": "#ffebee", "score": 20}

def overall_rating(rows):
    if not rows: return {"label": "—", "color": "#666", "score": 0}
    s = sum(r.get("score", 50) for r in rows)/len(rows)
    if s >= 95: return {"label": "🏆 ممتازة", "color": "#1b5e20", "score": s}
    if s >= 85: return {"label": "🌟 جيدة جداً", "color": "#2e7d32", "score": s}
    if s >= 70: return {"label": "✅ جيدة", "color": "#558b2f", "score": s}
    if s >= 55: return {"label": "⭐ مقبولة", "color": "#f9a825", "score": s}
    return {"label": "⚠️ تحتاج تحسين", "color": "#e65100", "score": s}

def formulate(available, prices, custom_std, standard_key="", tol=0.3, max_it=50, basis="DP"):
    if not SCIPY: return {"success": False, "message": "SCIPY غير متوفرة"}
    ing_data = {}
    for ing in available:
        for cat in FEEDS.values():
            if ing in cat: ing_data[ing] = cat[ing]; break
    valid = [i for i in available if i in ing_data]
    if len(valid) < 3: return {"success": False, "message": "3 مكونات على الأقل"}
    n = len(valid); c = [prices.get(i, 300) for i in valid]
    rows = {}
    for nut in ["CP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
        rows[nut] = [ing_data[i].get(nut, 0) for i in valid]
    rows["DP"] = [ing_data[i].get("CP", 0)*ing_data[i].get("DC", 0) for i in valid]
    tk = "DP" if basis == "DP" else "CP"
    prot_row = rows[tk]
    targets = {k: custom_std.get(k, 0) for k in ["DP", "SE", "NDF", "ADF", "Ca", "P", "CP"]}
    tv = targets[tk]
    oil_std = get_oil_std(standard_key); oil_max = oil_std["max"]
    bounds = []
    for i in valid:
        if i in get_oils(): bounds.append((0, oil_max*0.6))
        elif "يوريا" in i: bounds.append((0, 1))
        elif "مولاس" in i: bounds.append((0, 10))
        elif "ملح الطعام" in i: bounds.append((0.3, 0.7))
        elif "بيكربونات" in i: bounds.append((0, 1.5))
        elif "مضاد سموم" in i: bounds.append((0.05, 0.25))
        elif "بريمكس" in i: bounds.append((0.15, 0.5))
        elif "إنزيم" in i: bounds.append((0.02, 0.10))
        elif "الحجر الجيري" in i: bounds.append((0, 8.5))
        elif "فوسفات" in i: bounds.append((0, 2.5))
        elif "تبن" in i or "قش" in i: bounds.append((0, 25))
        else: bounds.append((0, 100))
    oil_ind = [1.0 if i in get_oils() else 0.0 for i in valid]
    has_oils = sum(oil_ind) > 0
    try:
        A_eq = [[1.0]*n, prot_row]; b_eq = [100.0, tv*100]
        A_ub = [[-1.0*x for x in rows["SE"]], [1.0*x for x in rows["NDF"]], [1.0*x for x in rows["ADF"]]]
        b_ub = [-targets["SE"]*100, targets["NDF"]*1.15*100, targets["ADF"]*1.15*100]
        if has_oils: A_ub.append(oil_ind); b_ub.append(oil_max*100)
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        if not res.success:
            for rlx in [1.05, 1.10, 1.20]:
                b_ub2 = [-targets["SE"]*100*(2-rlx), targets["NDF"]*rlx*100, targets["ADF"]*rlx*100]
                if has_oils: b_ub2.append(oil_max*100)
                res = linprog(c, A_ub=A_ub, b_ub=b_ub2, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
                if res.success: break
    except Exception as e: return {"success": False, "message": f"خطأ: {e}"}
    if not res.success: return {"success": False, "message": "تعذر إيجاد حل"}
    best = None; best_sc = float('inf')
    cur_t = tv; cur_se = targets["SE"]; cur_ndf = targets["NDF"]; cur_adf = targets["ADF"]
    for it in range(max_it):
        try:
            A_eq = [[1.0]*n, prot_row, rows["Ca"], rows["P"]]
            b_eq = [100.0, cur_t*100, targets["Ca"]*100, targets["P"]*100]
            A_ub = [[-1.0*x for x in rows["SE"]], [1.0*x for x in rows["NDF"]], [1.0*x for x in rows["ADF"]]]
            b_ub = [-cur_se*100, cur_ndf*1.10*100, cur_adf*1.10*100]
            if has_oils: A_ub.append(oil_ind); b_ub.append(oil_max*100)
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs',
                          options={'presolve': True, 'time_limit': 15})
        except: res = None
        if res is None or not res.success:
            try:
                A_eq = [[1.0]*n, prot_row, rows["Ca"]]
                b_eq = [100.0, cur_t*100, targets["Ca"]*100]
                A_ub = [[-1.0*x for x in rows["SE"]]]; b_ub = [-cur_se*100]
                if has_oils: A_ub.append(oil_ind); b_ub.append(oil_max*100)
                res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
            except: res = None
        if res is None or not res.success:
            cur_ndf *= 1.05; cur_adf *= 1.05; continue
        formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
        actual = calc_nutrients(formula)
        oil = oil_pct(formula)
        errs = {}
        for k in ["DP", "CP", "SE", "NDF", "ADF", "Ca", "P"]:
            t = targets.get(k, 0)
            if t > 0: errs[k] = abs(actual.get(k, 0)-t)/t
        w = {"DP": 5, "CP": 5, "SE": 3, "NDF": 1.5, "ADF": 1, "Ca": 1, "P": 1}
        sc = sum(errs.get(k, 0)*w.get(k, 0) for k in errs)
        if sc < best_sc:
            best_sc = sc
            best = {"success": True, "formula": formula, "cost": res.fun/100,
                    "actual": actual,
                    "dp_err": abs(actual["DP"]-targets["DP"]),
                    "cp_err": abs(actual["CP"]-targets.get("CP", 0)),
                    "se_err": abs(actual["SE"]-targets["SE"]),
                    "ndf_err": abs(actual["NDF"]-targets["NDF"]),
                    "adf_err": abs(actual["ADF"]-targets["ADF"]),
                    "ca_err": abs(actual.get("Ca", 0)-targets["Ca"]),
                    "p_err": abs(actual.get("P", 0)-targets["P"]),
                    "total_oil": oil, "oil_std": oil_std,
                    "iterations": it+1, "targets": targets, "basis": basis}
        te = errs.get(tk, 1)*100
        if te <= tol and errs.get("SE", 1)*100 <= tol*2 and errs.get("NDF", 1)*100 <= tol*5:
            best["perfect_match"] = True; break
        ap = actual.get(tk, 0)
        cur_t += (tv-ap)*0.25; cur_se += (targets["SE"]-actual["SE"])*0.20
        cur_ndf += (targets["NDF"]-actual["NDF"])*0.15; cur_adf += (targets["ADF"]-actual["ADF"])*0.15
        cur_t = max(5, min(45, cur_t)); cur_se = max(10, min(90, cur_se))
        cur_ndf = max(5, min(70, cur_ndf)); cur_adf = max(3, min(50, cur_adf))
    if best: return best
    return {"success": False, "message": "تعذر حل دقيق"}

def auto_salts(animal, req=None):
    s = {}
    if animal in ["أغنام", "ماعز", "أبقار", "إبل"]: s["بيكربونات صوديوم"] = 0.75
    s["مضاد سموم"] = 0.20
    s["ملح الطعام"] = 0.50
    if animal in ["دواجن", "سمان"]:
        s["الحجر الجيري"] = 8.0 if (req and req.Ca > 2) else 1.5
        s["فوسفات ثنائي كالسيوم"] = 1.5; s["بريمكس دواجن"] = 0.30
    elif animal == "أسماك":
        s["الحجر الجيري"] = 1.0; s["فوسفات ثنائي كالسيوم"] = 1.5; s["بريمكس أسماك"] = 0.30
    elif animal == "خيول":
        s["الحجر الجيري"] = 1.5; s["فوسفات ثنائي كالسيوم"] = 1.5; s["بريمكس خيول"] = 0.30
    elif animal == "إبل":
        s["الحجر الجيري"] = 2.0; s["فوسفات ثنائي كالسيوم"] = 1.5; s["بريمكس إبل"] = 0.30
    else:
        s["الحجر الجيري"] = 2.0; s["فوسفات ثنائي كالسيوم"] = 1.5; s["بريمكس مجترات"] = 0.30
    return s

# ═══════════════ الرسوم البيانية ═══════════════
def chart_bar(std, act):
    if not MPL: return None
    try:
        nuts = [n for n in ["CP","DP","SE","NDF","ADF","EE","ASH"] if n in std]
        if not nuts: return None
        sv = [std[n] for n in nuts]; av = [act.get(n, 0) for n in nuts]
        fig, ax = plt.subplots(figsize=(9, 4.5))
        x = np.arange(len(nuts)); w = 0.35
        b1 = ax.bar(x-w/2, sv, w, label='المعيار', color='#1976d2', edgecolor='#0d47a1')
        b2 = ax.bar(x+w/2, av, w, label='المحسوب', color='#43a047', edgecolor='#1b5e20')
        for b in b1: ax.text(b.get_x()+b.get_width()/2, b.get_height(), f'{b.get_height():.1f}', ha='center', va='bottom', fontsize=9, color='#0d47a1', fontweight='bold')
        for b in b2: ax.text(b.get_x()+b.get_width()/2, b.get_height(), f'{b.get_height():.1f}', ha='center', va='bottom', fontsize=9, color='#1b5e20', fontweight='bold')
        ax.set_title('مقارنة العناصر', fontsize=13, fontweight='bold', color='#1b5e20')
        ax.set_xticks(x); ax.set_xticklabels(nuts); ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3, linestyle='--'); ax.set_facecolor('#fafafa')
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=110, bbox_inches='tight', facecolor='white'); plt.close(); buf.seek(0); return buf
    except: return None

def chart_pie(formula):
    if not MPL or len(formula) < 2: return None
    try:
        colors = ['#e53935','#8e24aa','#3949ab','#1e88e5','#00897b','#43a047','#7cb342','#fdd835','#fb8c00','#6d4c41']
        fig, ax = plt.subplots(figsize=(8, 5))
        _, _, autos = ax.pie(list(formula.values()), autopct='%1.1f%%', colors=colors[:len(formula)], startangle=90, pctdistance=0.75, wedgeprops=dict(edgecolor='white', linewidth=2))
        for t in autos: t.set_color('white'); t.set_fontweight('bold'); t.set_fontsize(9)
        ax.legend(list(formula.keys()), loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)
        ax.set_title('توزيع المكونات', fontsize=13, fontweight='bold', color='#1b5e20')
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=110, bbox_inches='tight', facecolor='white'); plt.close(); buf.seek(0); return buf
    except: return None

def chart_radar(std, act):
    if not MPL: return None
    try:
        nuts = [n for n in ["CP","DP","SE","NDF","ADF","EE","Ca","P"] if n in std and std[n] > 0]
        if len(nuts) < 3: return None
        sn = [100.0 for _ in nuts]; an = [(act.get(n, 0)/std[n])*100 for n in nuts]
        angs = np.linspace(0, 2*np.pi, len(nuts), endpoint=False).tolist()
        sn += sn[:1]; an += an[:1]; angs += angs[:1]
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angs, sn, 'o-', lw=2.5, color='#1976d2', label='المعيار')
        ax.fill(angs, sn, alpha=0.15, color='#1976d2')
        ax.plot(angs, an, 'o-', lw=2.5, color='#43a047', label='المحسوب')
        ax.fill(angs, an, alpha=0.25, color='#43a047')
        ax.set_xticks(angs[:-1]); ax.set_xticklabels(nuts)
        ax.set_title('المقارنة %', fontsize=12, fontweight='bold', color='#1b5e20', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9); ax.grid(True, alpha=0.3)
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=110, bbox_inches='tight', facecolor='white'); plt.close(); buf.seek(0); return buf
    except: return None

def chart_gauge(score):
    if not MPL: return None
    try:
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect='equal'))
        cs = ['#c62828','#ef6c00','#f9a825','#7cb342','#43a047','#1b5e20']
        for i, c in enumerate(cs):
            ax.add_patch(Wedge((0, 0), 1, 180-(i+1)*30, 180-i*30, width=0.3, facecolor=c, edgecolor='white', linewidth=2))
        ang = 180 - (score/100)*180; rad = np.radians(ang)
        ax.plot([0, 0.85*np.cos(rad)], [0, 0.85*np.sin(rad)], color='#1a1a1a', lw=3, zorder=10)
        ax.add_patch(Circle((0, 0), 0.08, color='#1a1a1a', zorder=11))
        ax.text(0, -0.25, f'{score:.0f}%', ha='center', fontsize=20, fontweight='bold', color='#1b5e20')
        ax.text(0, -0.5, 'التقييم', ha='center', fontsize=11, color='#666')
        ax.set_xlim(-1.2, 1.2); ax.set_ylim(-0.7, 1.2); ax.axis('off')
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=110, bbox_inches='tight', facecolor='white'); plt.close(); buf.seek(0); return buf
    except: return None

# ═══════════════ PDF Generator مع الختم والتوقيع ═══════════════
class PDFGen:
    def __init__(self):
        self.fn = fontmgr.name; self.lp = None
        for lp in LOGOS + PHOTOS:
            if os.path.exists(lp): self.lp = lp; break
    def _ar(self, t):
        if t is None: return ""
        try: return get_display(arabic_reshaper.reshape(str(t)), base_dir='R')
        except: return str(t)
    def _stamp(self, c, doc):
        """الختم الرسمي"""
        try:
            w, h = doc.pagesize; sx, sy = w - 105, 145
            c.setStrokeColor(HexColor('#c62828'))
            c.setLineWidth(3.5); c.circle(sx, sy, 72, stroke=1, fill=0)
            c.setLineWidth(2.0); c.circle(sx, sy, 64, stroke=1, fill=0)
            c.setLineWidth(0.8); c.circle(sx, sy, 58, stroke=1, fill=0)
            c.setLineWidth(1.8)
            for ang in [-45, 45, 135, 225]:
                r = np.radians(ang)
                c.line(sx+58*np.cos(r), sy+58*np.sin(r), sx+72*np.cos(r), sy+72*np.sin(r))
            c.setFillColor(HexColor('#c62828')); c.setFont(self.fn, 9.5)
            c.drawCentredString(sx, sy+42, self._ar("تاور نولجي"))
            c.drawCentredString(sx, sy+30, self._ar("Tawor Nology"))
            c.setFont(self.fn, 8)
            c.drawCentredString(sx, sy+16, self._ar("م. عبدالقادر"))
            c.drawCentredString(sx, sy+4, self._ar("إسماعيل تاور"))
            c.setFont(self.fn, 6.5)
            c.drawCentredString(sx, sy-12, self._ar("اختصاصي تغذية"))
            c.drawCentredString(sx, sy-24, self._ar("معتمد رسمياً"))
            c.drawCentredString(sx, sy-36, self._ar("© 2026"))
        except: pass
    def _page(self, c, doc):
        try:
            c.saveState()
            w, h = doc.pagesize
            c.setFillColor(HexColor('#e8f5e9')); c.setFont(self.fn, 60)
            try: c.setFillAlpha(0.07)
            except: pass
            c.saveState(); c.translate(w/2, h/2); c.rotate(45)
            c.drawCentredString(0, 0, self._ar("تاور نولجي")); c.restoreState()
            try: c.setFillAlpha(1)
            except: pass
            c.setFillColor(HexColor('#1b5e20')); c.rect(0, h-90, w, 90, fill=1, stroke=0)
            c.setFillColor(HexColor('#d4af37')); c.rect(0, h-95, w, 5, fill=1, stroke=0)
            try:
                if self.lp: c.drawImage(self.lp, 30, h-78, width=60, height=60, preserveAspectRatio=True, anchor='sw', mask='auto')
            except: pass
            c.setFillColor(white); c.setFont(self.fn, 22)
            c.drawCentredString(w/2, h-38, self._ar("تاور نولجي  Tawor Nology"))
            c.setFont(self.fn, 12); c.setFillColor(HexColor('#e8f5e9'))
            c.drawCentredString(w/2, h-58, self._ar("للإنتاج الحيواني"))
            c.setFont(self.fn, 10); c.setFillColor(HexColor('#d4af37'))
            c.drawCentredString(w/2, h-76, self._ar(f"إشراف: {SUPERVISOR}"))
            c.setFillColor(HexColor('#1b5e20')); c.rect(0, 42, w, 42, fill=1, stroke=0)
            c.setFillColor(HexColor('#d4af37')); c.rect(0, 84, w, 3, fill=1, stroke=0)
            c.setFillColor(HexColor('#ffeb3b')); c.setFont(self.fn, 10)
            c.drawCentredString(w/2, 68, self._ar(f"🤲 {DUA_SHORT} 🤲"))
            c.setFillColor(HexColor('#1b5e20')); c.rect(0, 0, w, 42, fill=1, stroke=0)
            c.setFillColor(white); c.setFont(self.fn, 8)
            c.drawCentredString(w/2, 27, self._ar("تاور نولجي © 2026"))
            c.setFont(self.fn, 7)
            c.drawCentredString(w/2, 12, self._ar(f"صفحة {c.getPageNumber()}"))
            try:
                qr = qrcode.QRCode(version=1, box_size=3, border=1); qr.add_data(PLATFORM_URL); qr.make(fit=True)
                q = qr.make_image(fill_color="#1b5e20", back_color="white")
                qbuf = io.BytesIO(); q.save(qbuf, format="PNG"); qbuf.seek(0)
                c.drawImage(RLImage(qbuf), w/2-20, 46, width=40, height=40)
            except: pass
            self._stamp(c, doc)
            c.restoreState()
        except: pass
    def _cmp_table(self, std, act):
        labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم", "SE": "معادل النشاء",
                  "NDF": "NDF", "ADF": "ADF", "EE": "دهن", "ASH": "رماد", "Ca": "Ca", "P": "P"}
        hdr = [self._ar(x) for x in ["العنصر", "المعيار", "المحسوب", "الفرق", "الفرق %", "التقييم"]]
        data = [hdr]
        cmds = [('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')), ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, -1), self.fn),
                ('FONTSIZE', (0, 0), (-1, -1), 9), ('GRID', (0, 0), (-1, -1), 1, HexColor('#9e9e9e')),
                ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7)]
        r = 1
        for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
            if k not in std: continue
            sv = std[k]; cv = act.get(k, 0); diff = cv-sv
            pct = (diff/sv*100) if sv else 0
            ev = diff_eval(pct, sv)
            data.append([self._ar(labels.get(k, k)), f"{sv:.2f}", f"{cv:.2f}",
                         f"{diff:+.3f}", f"{pct:+.2f}%", self._ar(ev["label"])])
            cmds.append(('BACKGROUND', (0, r), (-1, r), HexColor(ev["bg"])))
            r += 1
        t = Table(data, colWidths=[100, 70, 70, 70, 70, 105])
        t.setStyle(TableStyle(cmds)); return t
    def _oil_table(self, formula, sk):
        oils = get_oils()
        rows = [(i, p) for i, p in formula.items() if i in oils]
        std = get_oil_std(sk); tot = sum(p for _, p in rows)
        if not rows: return (None, 0, std)
        data = [[self._ar("الزيت"), self._ar("النسبة %"), self._ar("kcal/kg")]]
        for i, p in rows: data.append([self._ar(i), f"{p:.2f}%", f"{p*90:.0f}"])
        data.append([self._ar("الإجمالي"), f"{tot:.2f}%", f"{tot*90:.0f}"])
        cmds = [('BACKGROUND', (0, 0), (-1, 0), HexColor('#e65100')), ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, -1), self.fn),
                ('FONTSIZE', (0, 0), (-1, -1), 10), ('GRID', (0, 0), (-1, -1), 1, HexColor('#bf360c')),
                ('BACKGROUND', (0, -1), (-1, -1), HexColor('#ffe0b2'))]
        t = Table(data, colWidths=[250, 100, 135]); t.setStyle(TableStyle(cmds))
        return (t, tot, std)
    def report(self, formula, req, animal, breed, cost, city, lc, ls, rname="", basis="DP", sk=""):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []
        def P(t, s=11, a=TA_RIGHT, c='#1a1a1a'):
            return Paragraph(self._ar(t), ParagraphStyle('s', fontName=self.fn, fontSize=s,
                alignment=a, textColor=HexColor(c), spaceAfter=6, leading=s*1.6))
        story.append(P("تقرير فني رسمي — تركيب علفة", 20, TA_CENTER, '#1b5e20'))
        story.append(Spacer(1, 6)); story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37'))); story.append(Spacer(1, 12))
        info = [[self._ar("👤 طالب:"), self._ar(rname or "—")],
                [self._ar("📍 الموقع:"), self._ar(city)],
                [self._ar("🐾 الفصيل:"), self._ar(f"{animal} — {breed}")],
                [self._ar("🧬 الأساس:"), self._ar(basis)],
                [self._ar("📅 التاريخ:"), datetime.now().strftime('%Y-%m-%d %H:%M')]]
        ct = Table(info, colWidths=[150, 340])
        ct.setStyle(TableStyle([('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')), ('BACKGROUND', (1, 0), (1, -1), HexColor('#fafafa')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')), ('INNERGRID', (0, 0), (-1, -1), 0.6, HexColor('#c8e6c9')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'), ('FONTNAME', (0, 0), (-1, -1), self.fn), ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 9), ('BOTTOMPADDING', (0, 0), (-1, -1), 9)]))
        story.append(ct); story.append(Spacer(1, 15))
        std = req_to_std(req); act = calc_nutrients(formula)
        scores = []
        for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
            if k not in std: continue
            sv = std[k]; cv = act.get(k, 0)
            pct = ((cv-sv)/sv*100) if sv else 0
            scores.append({"score": diff_eval(pct, sv)["score"]})
        story.append(P("📊 مقارنة العناصر", 14, c='#1b5e20')); story.append(Spacer(1, 8))
        story.append(self._cmp_table(std, act)); story.append(Spacer(1, 12))
        ot, tot, ostr = self._oil_table(formula, sk)
        story.append(P("🌰 الزيوت", 14, c='#e65100')); story.append(Spacer(1, 8))
        if ot: story.append(ot); story.append(Spacer(1, 8))
        story.append(P(f"الحد: {ostr['max']}% | المثالي: {ostr['optimal']}% | {ostr['src']}", 10, c='#bf360c'))
        story.append(Spacer(1, 15))
        story.append(P("📈 الرسوم البيانية", 14, c='#1b5e20')); story.append(Spacer(1, 10))
        c1 = chart_bar(std, act)
        if c1:
            try: story.append(RLImage(c1, width=450, height=250)); story.append(Spacer(1, 12))
            except: pass
        c2 = chart_pie(formula); c3 = chart_radar(std, act)
        if c2 and c3:
            try:
                row = [[RLImage(c2, width=210, height=200), RLImage(c3, width=210, height=200)]]
                rt = Table(row, colWidths=[230, 230]); rt.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
                story.append(rt); story.append(Spacer(1, 12))
            except: pass
        g = chart_gauge(overall_rating(scores)["score"])
        if g:
            try: story.append(P("🎯 التقييم", 12, TA_CENTER, '#1b5e20')); story.append(RLImage(g, width=200, height=200)); story.append(Spacer(1, 12))
            except: pass
        story.append(PageBreak())
        story.append(P("💰 التكاليف", 14, c='#1b5e20')); story.append(Spacer(1, 8))
        cd = [[self._ar("البند"), self._ar("القيمة")],
              [self._ar("التكلفة/طن ($)"), f"${cost:.2f}"],
              [self._ar(f"التكلفة ({ls})"), f"{lc:,.2f}"],
              [self._ar("البروتين"), f"{req.DP if basis == 'DP' else req.CP:.2f}%"]]
        tc = Table(cd, colWidths=[280, 210])
        tc.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')), ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#2e7d32')), ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.fn), ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
        story.append(tc); story.append(Spacer(1, 18))
        story.append(P("🌾 المكونات", 14, c='#1b5e20')); story.append(Spacer(1, 8))
        idata = [[self._ar("المكون"), self._ar("النسبة %"), self._ar("كجم/طن")]]
        for i, p in formula.items(): idata.append([self._ar(i), f"{p:.2f}%", f"{p*10:.1f}"])
        ti = Table(idata, colWidths=[270, 110, 110])
        ti.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')), ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, -1), self.fn), ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
        story.append(ti); story.append(Spacer(1, 20))
        sign = [[self._ar("توقيع الطالب"), self._ar("توقيع المختص")],
                [self._ar("........................"), self._ar(SUPERVISOR)],
                [self._ar("التاريخ:"), self._ar(SUPERVISOR_TITLE)]]
        ts = Table(sign, colWidths=[245, 245])
        ts.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, -1), self.fn),
            ('FONTSIZE', (0, 0), (-1, -1), 10), ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')), ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f5e9'))]))
        story.append(ts)
        doc.build(story, onFirstPage=self._page, onLaterPages=self._page)
        buf.seek(0); return buf.getvalue()

pdfgen = PDFGen()

def export_xl(std, act):
    if not XL: return b""
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "مقارنة"; ws.sheet_view.rightToLeft = True
    hf = Font(name='Arial', size=12, bold=True, color='FFFFFF'); hfill = PatternFill('solid', fgColor='1B5E20')
    al = Alignment(horizontal='center', vertical='center', wrap_text=True)
    thin = Side(border_style='thin', color='9E9E9E'); bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    hdr = ["العنصر", "المعيار", "المحسوب", "الفرق", "% الفرق", "التقييم"]
    for c, h in enumerate(hdr, 1):
        cell = ws.cell(row=1, column=c, value=h); cell.font = hf; cell.fill = hfill; cell.alignment = al; cell.border = bd
    labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم", "SE": "معادل النشاء", "NDF": "NDF", "ADF": "ADF",
              "EE": "دهن", "ASH": "رماد", "Ca": "Ca", "P": "P"}
    r = 2
    for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
        if k not in std: continue
        sv = std[k]; cv = act.get(k, 0); diff = cv-sv; pct = (diff/sv*100) if sv else 0
        ev = diff_eval(pct, sv)
        for c, v in enumerate([labels[k], round(sv, 2), round(cv, 2), round(diff, 3), round(pct, 2), ev["label"]], 1):
            cell = ws.cell(row=r, column=c, value=v); cell.alignment = al; cell.border = bd
            cell.fill = PatternFill('solid', fgColor=ev["bg"].replace('#', ''))
        r += 1
    for c in range(1, 7): ws.column_dimensions[get_column_letter(c)].width = 22
    buf = io.BytesIO(); wb.save(buf); buf.seek(0); return buf.getvalue()

RATES = {"السودان": (600, "SDG"), "ليبيا": (4.80, "LYD"), "مصر": (48, "EGP"),
         "السعودية": (3.75, "SAR"), "الإمارات": (3.67, "AED"), "أخرى": (1, "USD")}

def market_prices(country):
    base = {i: 280.0 for cat in FEEDS.values() for i in cat}
    base.update({"ذرة صفراء": 230, "شعير مطحون": 210, "كسب فول صويا 44%": 440,
                 "كسب فول صويا 48%": 480, "أمباز الفول السوداني": 460, "نخالة قمح": 150,
                 "البرسيم الجاف": 170, "مسحوق أسماك 60%": 850, "الحجر الجيري": 40,
                 "فوسفات ثنائي كالسيوم": 280, "ملح الطعام": 30, "بيكربونات صوديوم": 340,
                 "مضاد سموم": 950, "بريمكس دواجن": 4800, "بريمكس مجترات": 4500,
                 "زيت ذرة": 1500, "زيت فول الصويا": 1350, "زيت النخيل": 1100})
    m = {"السودان": 1.15, "ليبيا": 1.10, "مصر": 1.04, "السعودية": 1.08, "الإمارات": 1.12}.get(country, 1.0)
    return {k: v*m for k, v in base.items()}

ANIMAL_IMGS = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "إبل": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600",
    "سمان": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600"}

@st.cache_data(ttl=3600)
def img_b64(paths):
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f: return base64.b64encode(f.read()).decode()
            except: pass
    return None

img_b64 = img_b64(tuple(PHOTOS))

# ═══════════════ معايير الحظائر ═══════════════
BARN_STD = {
    "دواجن_لاحم": {"name": "دواجن لاحم", "area": 0.10, "fed": 5, "drk": 2.5, "h": 2.8, "w": 12,
        "as": 60, "aw": 8, "vr": 0.20, "roof": "gable", "slope": 20, "ft": "خطية معلقة", "dt": "حلمات", "a": 1.2, "ca": True},
    "دواجن_بياض": {"name": "دواجن بياض", "area": 0.15, "fed": 10, "drk": 2.5, "h": 3.0, "w": 12,
        "as": 40, "aw": 6, "vr": 0.20, "roof": "gable", "slope": 20, "ft": "سلسلة", "dt": "حلمات", "a": 1.2, "ca": True},
    "سمان": {"name": "سمان", "area": 0.025, "fed": 2, "drk": 1, "h": 2, "w": 6,
        "as": 50, "aw": 8, "vr": 0.25, "roof": "mono", "slope": 15, "ft": "خطية", "dt": "حلمات", "a": 0.8, "ca": False},
    "أغنام": {"name": "أغنام", "area": 1.5, "fed": 35, "drk": 4, "h": 3.5, "w": 10,
        "as": 30, "aw": 5, "vr": 0.30, "roof": "gable", "slope": 25, "ft": "خرسانية", "dt": "حوض تلقائي", "a": 2, "ca": True},
    "ماعز": {"name": "ماعز", "area": 1.5, "fed": 35, "drk": 4, "h": 3.5, "w": 10,
        "as": 30, "aw": 5, "vr": 0.30, "roof": "gable", "slope": 25, "ft": "مرتفعة", "dt": "حوض تلقائي", "a": 2, "ca": True},
    "أبقار": {"name": "أبقار", "area": 5, "fed": 70, "drk": 6, "h": 4.5, "w": 15,
        "as": 25, "aw": 4, "vr": 0.35, "roof": "gable", "slope": 20, "ft": "وسطية", "dt": "حوض تلقائي", "a": 3.5, "ca": True},
    "إبل": {"name": "إبل", "area": 10, "fed": 100, "drk": 8, "h": 4.5, "w": 15,
        "as": 20, "aw": 4, "vr": 0.40, "roof": "gable", "slope": 20, "ft": "مرتفعة", "dt": "حوض كبير", "a": 4, "ca": True},
    "خيول": {"name": "خيول", "area": 16, "fed": 100, "drk": 10, "h": 4, "w": 15,
        "as": 25, "aw": 5, "vr": 0.30, "roof": "gable", "slope": 25, "ft": "مرتفعة", "dt": "حوض تلقائي", "a": 3.5, "ca": True},
}

def calc_barn(key, count):
    s = BARN_STD.get(key)
    if not s: return None
    ta = count * s["area"]; w = s["w"]; L = max(ta/w, 6)
    fdr = max(1, int(np.ceil(count*s["fed"]/300))); drk = max(1, int(np.ceil(count*s["drk"]/200)))
    vol = L*w*s["h"]; rise = (w/2)*(s["slope"]/100); ridge = s["h"]+rise
    apr = max(2, int(L/0.3)) if key in ["دواجن_لاحم","دواجن_بياض","سمان"] else max(2, int(L/1.5))
    return {"std": s, "count": count, "total_area": round(ta, 2), "length": round(L, 2), "width": round(w, 2),
            "height": s["h"], "ridge": round(ridge, 2), "roof": s["roof"], "slope": s["slope"],
            "feeders": fdr, "drinkers": drk, "fdr_len": round(count*s["fed"]/100, 1),
            "drk_len": round(count*s["drk"]/100, 1), "volume": round(vol, 1),
            "vent_s": int(vol*s["as"]), "vent_w": int(vol*s["aw"]),
            "vent_area": round(L*s["h"]*s["vr"], 2), "apr": apr,
            "ft": s["ft"], "dt": s["dt"], "aisle": s["a"], "ca": s["ca"]}

def fig_3d(d):
    if not PLOTLY: return None
    try:
        s = d["std"]; L = d["length"]; W = d["width"]; H = d["height"]; RH = d["ridge"]
        aisle = d.get("aisle", 1.5); fw = 0.6
        fig = go.Figure()
        fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[0,0,W,W], z=[0,0,0,0], i=[0,0], j=[1,2], k=[2,3], color='#d7ccc8', opacity=0.65, name='الأرضية', hoverinfo='skip'))
        for xp in [0, L]:
            fig.add_trace(go.Mesh3d(x=[xp]*4, y=[0,W,W,0], z=[0,0,H,H], i=[0,0], j=[1,2], k=[2,3], color='#a1887f', opacity=0.35, showlegend=False, hoverinfo='skip'))
        for yp in [0, W]:
            fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[yp]*4, z=[0,0,H,H], i=[0,0], j=[1,2], k=[2,3], color='#a1887f', opacity=0.35, showlegend=False, hoverinfo='skip'))
        if d["roof"] == "gable":
            fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[0,0,W/2,W/2], z=[H,H,RH,RH], i=[0,0], j=[1,2], k=[2,3], color='#8d6e63', opacity=0.5, name='السقف', hoverinfo='skip'))
            fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[W/2,W/2,W,W], z=[RH,RH,H,H], i=[0,0], j=[1,2], k=[2,3], color='#8d6e63', opacity=0.5, showlegend=False, hoverinfo='skip'))
        else:
            fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[0,0,W,W], z=[RH,RH,H,H], i=[0,0], j=[1,2], k=[2,3], color='#8d6e63', opacity=0.5, name='السقف', hoverinfo='skip'))
        vh = H * s["vr"]
        for yv in [0.15, W-0.15]:
            fig.add_trace(go.Scatter3d(x=[1,L-1,L-1,1,1], y=[yv]*5, z=[H*0.35, H*0.35, H*0.35+vh, H*0.35+vh, H*0.35], mode='lines', line=dict(color='#1976d2', width=8), name='فتحة تهوية' if yv == 0.15 else None, showlegend=(yv == 0.15)))
        fpos = [W/2-aisle/2-fw, W/2+aisle/2] if d.get("ca", True) and W > 8 else [0.8, W-1.4]
        for idx, yp in enumerate(fpos):
            xv = [0.5, L-0.5, L-0.5, 0.5, 0.5, L-0.5, L-0.5, 0.5]
            yv = [yp]*2 + [yp+fw]*2 + [yp]*2 + [yp+fw]*2
            zv = [0, 0, 0, 0, 0.35, 0.35, 0.35, 0.35]
            fig.add_trace(go.Mesh3d(x=xv, y=yv, z=zv,
                i=[0,0,4,4,0,0,3,3,0,0,1,1], j=[1,2,6,7,4,5,2,6,3,7,5,6], k=[2,3,5,6,5,1,6,7,7,4,6,2],
                color='#ff8f00', opacity=0.85, name=f'معلف ({d.get("ft","خطي")})' if idx == 0 else None, showlegend=(idx == 0), hoverinfo='skip'))
        nd = d["drinkers"]
        for i in range(nd):
            xc = (i+0.5)*(L/nd); yc = W-aisle-0.5 if d.get("ca", True) else W-1.5
            fig.add_trace(go.Scatter3d(x=[xc], y=[yc], z=[0.4], mode='markers+text',
                marker=dict(size=14, color='#1976d2', symbol='diamond', line=dict(color='#0d47a1', width=2)),
                text=[f'م{i+1}'], textposition='top center',
                name=f'مسقى ({d.get("dt","حوض")})' if i == 0 else None, showlegend=(i == 0)))
        apr = d["apr"]; nr = max(1, d["count"]//max(apr, 1)); stp = max(1, nr//25)
        xs, ys, zs = [], [], []
        for ri in range(0, nr, stp):
            yp = aisle + (ri//2)*(W/2-aisle)/max(nr//2, 1) if d.get("ca", True) and W > 8 and ri%2 == 0 else ((ri//2)*(W/2-aisle)/max(nr//2, 1)+0.5 if d.get("ca", True) and W > 8 else 2+ri*(W-3)/max(nr, 1))
            for col in range(min(apr, 20)):
                xs.append(0.8+col*(L-1.6)/min(apr, 20)); ys.append(yp); zs.append(0.2)
        if xs: fig.add_trace(go.Scatter3d(x=xs, y=ys, z=zs, mode='markers', marker=dict(size=4, color='#1b5e20', opacity=0.8), name=f'الحيوانات ({d["count"]})'))
        fig.add_trace(go.Scatter3d(x=[0, L], y=[-1, -1], z=[0, 0], mode='lines+text', line=dict(color='#c62828', width=4), text=['', f'الطول {L} م'], textposition='middle right', textfont=dict(size=11, color='#c62828'), showlegend=False))
        fig.update_layout(title=dict(text=f"🏗️ {s['name']} — {d['count']} رأس | {d['total_area']} م²", font=dict(size=15, color='#1b5e20')),
            scene=dict(xaxis=dict(title='الطول'), yaxis=dict(title='العرض'), zaxis=dict(title='الارتفاع'), aspectmode='data', camera=dict(eye=dict(x=1.6, y=-1.6, z=1.2))),
            height=700, margin=dict(l=0, r=0, t=90, b=0), paper_bgcolor='white',
            legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.9)', bordercolor='#2e7d32', borderwidth=1))
        return fig
    except: return None

def gif_barn(d, frames=30, fps=8):
    if not MPL or not PILok: return None
    try:
        s = d["std"]; L = d["length"]; W = d["width"]; H = d["height"]; RH = d["ridge"]; aisle = d.get("aisle", 1.5); fw = 0.6
        fig = plt.figure(figsize=(8, 6)); ax = fig.add_subplot(111, projection='3d')
        def draw():
            ax.clear()
            floor = [[(0,0,0),(L,0,0),(L,W,0),(0,W,0)]]
            ax.add_collection3d(Poly3DCollection(floor, facecolors='#d7ccc8', edgecolors='#5d4037', alpha=0.75, linewidths=1.5))
            walls = [[(0,0,0),(L,0,0),(L,0,H),(0,0,H)], [(0,W,0),(L,W,0),(L,W,H),(0,W,H)],
                     [(0,0,0),(0,W,0),(0,W,H),(0,0,H)], [(L,0,0),(L,W,0),(L,W,H),(L,0,H)]]
            ax.add_collection3d(Poly3DCollection(walls, facecolors='#a1887f', edgecolors='#5d4037', alpha=0.4, linewidths=1))
            if d["roof"] == "gable":
                r1 = [[(0,0,H),(L,0,H),(L,W/2,RH),(0,W/2,RH)]]; r2 = [[(0,W/2,RH),(L,W/2,RH),(L,W,H),(0,W,H)]]
                ax.add_collection3d(Poly3DCollection(r1, facecolors='#8d6e63', edgecolors='#4e342e', alpha=0.55, linewidths=1))
                ax.add_collection3d(Poly3DCollection(r2, facecolors='#8d6e63', edgecolors='#4e342e', alpha=0.55, linewidths=1))
            vh = H*s["vr"]
            for yv in [0.15, W-0.15]:
                ax.plot([1, L-1, L-1, 1, 1], [yv]*5, [H*0.35, H*0.35, H*0.35+vh, H*0.35+vh, H*0.35], color='#1976d2', lw=2.5, label='فتحة تهوية' if yv < 1 else None)
            fpos = [W/2-aisle/2-fw, W/2+aisle/2] if d.get("ca", True) and W > 8 else [0.8, W-1.4]
            for yp in fpos:
                fb = [[(0.5, yp, 0.35), (L-0.5, yp, 0.35), (L-0.5, yp+fw, 0.35), (0.5, yp+fw, 0.35)],
                      [(0.5, yp, 0), (0.5, yp+fw, 0), (0.5, yp+fw, 0.35), (0.5, yp, 0.35)],
                      [(L-0.5, yp, 0), (L-0.5, yp+fw, 0), (L-0.5, yp+fw, 0.35), (L-0.5, yp, 0.35)]]
                ax.add_collection3d(Poly3DCollection(fb, facecolors='#ff8f00', edgecolors='#e65100', alpha=0.9, linewidths=1))
            nd = d["drinkers"]
            xd = [(i+0.5)*(L/nd) for i in range(nd)]; yd = [W-aisle-0.5 if d.get("ca", True) else W-1.5]*len(xd)
            ax.scatter(xd, yd, [0.4]*len(xd), s=120, c='#1976d2', marker='D', label='مسقى', depthshade=False, edgecolors='#0d47a1')
            apr = d["apr"]; nr = max(1, d["count"]//max(apr, 1)); ss = max(1, nr//15)
            xa, ya = [], []
            for ri in range(0, nr, ss):
                yp = aisle + (ri//2)*(W/2-aisle)/max(nr//2, 1) if d.get("ca", True) and W > 8 and ri%2 == 0 else ((ri//2)*(W/2-aisle)/max(nr//2, 1)+0.5 if d.get("ca", True) and W > 8 else 2+ri*(W-3)/max(nr, 1))
                for col in range(min(apr, 15)):
                    xa.append(0.8+col*(L-1.6)/min(apr, 15)); ya.append(yp)
            ax.scatter(xa, ya, [0.2]*len(xa), s=25, c='#1b5e20', alpha=0.85, label=f'حيوانات ({d["count"]})', depthshade=False)
            ax.set_xlim(0, L); ax.set_ylim(0, W); ax.set_zlim(0, RH+1)
            ax.set_xlabel('الطول'); ax.set_ylabel('العرض'); ax.set_zlabel('الارتفاع')
            ax.set_title(f"🏗️ {s['name']} — {d['count']} رأس", fontsize=13, color='#1b5e20', fontweight='bold')
            ax.legend(loc='upper left', fontsize=8)
        def animate(fn):
            draw(); ax.view_init(elev=20, azim=(fn/frames)*360); return fig,
        a = animation.FuncAnimation(fig, animate, frames=frames, interval=1000//fps, blit=False)
        tmp = tempfile.NamedTemporaryFile(suffix='.gif', delete=False); tp = tmp.name; tmp.close()
        try:
            a.save(tp, writer='pillow', fps=fps, dpi=80)
            with open(tp, 'rb') as f: data = f.read()
            os.unlink(tp); plt.close(fig); return io.BytesIO(data)
        except:
            try: os.unlink(tp)
            except: pass
            plt.close(fig); return None
    except: return None

def barn_img(d):
    if not MPL: return None
    try:
        s = d["std"]; L = d["length"]; W = d["width"]; H = d["height"]; RH = d["ridge"]; aisle = d.get("aisle", 1.5); fw = 0.6
        fig = plt.figure(figsize=(10, 7)); ax = fig.add_subplot(111, projection='3d')
        floor = [[(0,0,0),(L,0,0),(L,W,0),(0,W,0)]]
        ax.add_collection3d(Poly3DCollection(floor, facecolors='#d7ccc8', edgecolors='#5d4037', alpha=0.75, linewidths=1.5))
        walls = [[(0,0,0),(L,0,0),(L,0,H),(0,0,H)], [(0,W,0),(L,W,0),(L,W,H),(0,W,H)],
                 [(0,0,0),(0,W,0),(0,W,H),(0,0,H)], [(L,0,0),(L,W,0),(L,W,H),(L,0,H)]]
        ax.add_collection3d(Poly3DCollection(walls, facecolors='#a1887f', edgecolors='#5d4037', alpha=0.4, linewidths=1))
        if d["roof"] == "gable":
            r1 = [[(0,0,H),(L,0,H),(L,W/2,RH),(0,W/2,RH)]]; r2 = [[(0,W/2,RH),(L,W/2,RH),(L,W,H),(0,W,H)]]
            ax.add_collection3d(Poly3DCollection(r1, facecolors='#8d6e63', edgecolors='#4e342e', alpha=0.55, linewidths=1))
            ax.add_collection3d(Poly3DCollection(r2, facecolors='#8d6e63', edgecolors='#4e342e', alpha=0.55, linewidths=1))
        vh = H*s["vr"]
        for yv in [0.15, W-0.15]:
            ax.plot([1, L-1, L-1, 1, 1], [yv]*5, [H*0.35, H*0.35, H*0.35+vh, H*0.35+vh, H*0.35], color='#1976d2', lw=2.5)
        fpos = [W/2-aisle/2-fw, W/2+aisle/2] if d.get("ca", True) and W > 8 else [0.8, W-1.4]
        for yp in fpos:
            fb = [[(0.5, yp, 0.35), (L-0.5, yp, 0.35), (L-0.5, yp+fw, 0.35), (0.5, yp+fw, 0.35)],
                  [(0.5, yp, 0), (0.5, yp+fw, 0), (0.5, yp+fw, 0.35), (0.5, yp, 0.35)],
                  [(L-0.5, yp, 0), (L-0.5, yp+fw, 0), (L-0.5, yp+fw, 0.35), (L-0.5, yp, 0.35)]]
            ax.add_collection3d(Poly3DCollection(fb, facecolors='#ff8f00', edgecolors='#e65100', alpha=0.9, linewidths=1))
        nd = d["drinkers"]
        xd = [(i+0.5)*(L/nd) for i in range(nd)]; yd = [W-aisle-0.5 if d.get("ca", True) else W-1.5]*len(xd)
        ax.scatter(xd, yd, [0.4]*len(xd), s=120, c='#1976d2', marker='D', depthshade=False, edgecolors='#0d47a1')
        apr = d["apr"]; nr = max(1, d["count"]//max(apr, 1)); ss = max(1, nr//15)
        xa, ya = [], []
        for ri in range(0, nr, ss):
            yp = aisle + (ri//2)*(W/2-aisle)/max(nr//2, 1) if d.get("ca", True) and W > 8 and ri%2 == 0 else ((ri//2)*(W/2-aisle)/max(nr//2, 1)+0.5 if d.get("ca", True) and W > 8 else 2+ri*(W-3)/max(nr, 1))
            for col in range(min(apr, 15)):
                xa.append(0.8+col*(L-1.6)/min(apr, 15)); ya.append(yp)
        ax.scatter(xa, ya, [0.2]*len(xa), s=25, c='#1b5e20', alpha=0.85, depthshade=False)
        ax.set_xlim(0, L); ax.set_ylim(0, W); ax.set_zlim(0, RH+1)
        ax.set_xlabel('الطول (م)'); ax.set_ylabel('العرض (م)'); ax.set_zlabel('الارتفاع (م)')
        ax.set_title(f"تصميم — {s['name']} | {d['count']} رأس", fontsize=14, color='#1b5e20', fontweight='bold')
        ax.view_init(elev=18, azim=-55)
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white'); plt.close(); buf.seek(0); return buf
    except: return None

# ═══════════════ دراسة الجدوى ═══════════════
TECH = {
    "دواجن_لاحم": {"feed_g": 120, "water_ml": 220, "lab": 0.3, "cycle": 42, "final_kg": 2.3, "ptype": "meat", "note": "42 يوم، 2.3كجم"},
    "دواجن_بياض": {"feed_g": 110, "water_ml": 250, "lab": 0.3, "eggs_y": 310, "egg_g": 60, "ptype": "eggs", "note": "310 بيضة/سنة"},
    "سمان": {"feed_g": 28, "water_ml": 55, "lab": 0.5, "cycle": 42, "final_kg": 0.25, "ptype": "meat", "note": "42 يوم"},
    "أغنام": {"feed_g": 1800, "water_ml": 6000, "lab": 1.5, "milk_L": 1.5, "lact_d": 200, "ptype": "mixed", "note": "1.5L×200يوم"},
    "ماعز": {"feed_g": 1500, "water_ml": 6000, "lab": 1.5, "milk_L": 2.5, "lact_d": 280, "ptype": "milk", "note": "2.5L×280يوم"},
    "أبقار": {"feed_g": 20000, "water_ml": 80000, "lab": 5, "milk_L": 20, "lact_d": 305, "ptype": "milk", "note": "20L×305يوم"},
    "إبل": {"feed_g": 8000, "water_ml": 50000, "lab": 3, "milk_L": 5, "lact_d": 300, "ptype": "milk", "note": "5L×300يوم"},
    "خيول": {"feed_g": 10000, "water_ml": 40000, "lab": 4, "ptype": "service", "note": "خدمات"},
}

def calc_feas(key, count):
    s = BARN_STD.get(key)
    if not s: return None
    d = calc_barn(key, count)
    if not d: return None
    t = TECH.get(key, {})
    fd = t.get("feed_g", 100)/1000*count
    wd = t.get("water_ml", 200)/1000*count
    wk = max(1, int(np.ceil(count*t.get("lab", 0.3)/1000)))
    pt = t.get("ptype", "meat"); prod = {}
    if pt == "eggs":
        ey = count*t.get("eggs_y", 300)
        prod = {"unit": "بيضة/سنة", "annual": ey, "per_day": ey/365, "weight_ton": ey*t.get("egg_g", 60)/1e6, "details": t.get("note", "")}
    elif pt == "milk":
        md = count*t.get("milk_L", 20); my = md*t.get("lact_d", 305)
        prod = {"unit": "لتر/سنة", "annual": my, "per_day": md, "lact_d": t.get("lact_d", 305), "details": t.get("note", "")}
    elif pt == "meat":
        cy = t.get("cycle", 42); cyc = 365/cy; tk = count*t.get("final_kg", 2)*cyc
        prod = {"unit": "كجم لحم/سنة", "annual": tk, "cycles": cyc, "per_cycle": count*t.get("final_kg", 2), "details": t.get("note", "")}
    elif pt == "mixed":
        md = count*t.get("milk_L", 1); my = md*t.get("lact_d", 200)
        prod = {"unit": "لتر/سنة", "annual": my, "per_day": md, "details": t.get("note", "")}
    else: prod = {"unit": "خدمات", "annual": 0, "details": t.get("note", "")}
    return {"key": key, "std": s, "dims": d, "count": count,
            "feed": {"per_head": t.get("feed_g", 100)/1000, "day": fd, "month": fd*30/1000, "year": fd*365/1000},
            "water": {"per_head": t.get("water_ml", 200)/1000, "day": wd, "year": wd*365/1000},
            "labor": {"workers": wk, "per_worker": count//wk},
            "production": prod,
            "vent": {"summer": d["vent_s"], "winter": d["vent_w"]}}

def booklet_feas(key, count, proj="", req_name=""):
    f = calc_feas(key, count)
    if not f: return None
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
    story = []
    def P(t, s=11, a=TA_RIGHT, c='#1a1a1a'):
        return Paragraph(ar(t), ParagraphStyle('s', fontName=fontmgr.name, fontSize=s, alignment=a,
            textColor=HexColor(c), spaceAfter=6, leading=s*1.6))
    s = f["std"]; d = f["dims"]

    # ص1: غلاف
    story.append(Spacer(1, 30))
    story.append(P("كتيّب دراسة الجدوى الفنية", 30, TA_CENTER, '#1b5e20'))
    story.append(Spacer(1, 6))
    story.append(P("Technical Feasibility Study", 13, TA_CENTER, '#666'))
    story.append(Spacer(1, 20)); story.append(HRFlowable(width="100%", thickness=3, color=HexColor('#d4af37')))
    story.append(Spacer(1, 30))
    story.append(P(f"مشروع: {proj or s['name']}", 18, TA_CENTER, '#c62828'))
    story.append(Spacer(1, 15))
    story.append(P(f"{count} رأس من {s['name']}", 14, TA_CENTER, '#1a1a1a'))
    story.append(Spacer(1, 30))
    cover = [[ar("الحيوان"), ar(s["name"])], [ar("العدد"), ar(f"{count} رأس")],
             [ar("المساحة"), ar(f"{d['total_area']} م²")], [ar("مقدم الطلب"), ar(req_name or "—")],
             [ar("التاريخ"), ar(datetime.now().strftime('%Y-%m-%d'))]]
    t = Table(cover, colWidths=[150, 300])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')), ('BACKGROUND', (1, 0), (1, -1), HexColor('#fafafa')),
        ('BOX', (0, 0), (-1, -1), 2, HexColor('#2e7d32')), ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#c8e6c9')),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'), ('FONTNAME', (0, 0), (-1, -1), fontmgr.name), ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10)]))
    story.append(t); story.append(Spacer(1, 60))
    story.append(P(f"🤲 {DUA_SHORT} 🤲", 12, TA_CENTER, '#c62828'))
    story.append(PageBreak())

    # ص2: تصميم الحظيرة
    story.append(P("🏗️ الباب الأول: تصميم الحظيرة", 18, TA_CENTER, '#1b5e20'))
    story.append(Spacer(1, 8)); story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#d4af37')))
    story.append(Spacer(1, 15))
    bd = [[ar("البيان"), ar("القيمة")], [ar("المساحة"), ar(f"{d['total_area']} م²")],
          [ar("الطول"), ar(f"{d['length']} م")], [ar("العرض"), ar(f"{d['width']} م")],
          [ar("ارتفاع الجدار"), ar(f"{d['height']} م")], [ar("القمة"), ar(f"{d['ridge']} م")],
          [ar("الحجم"), ar(f"{d['volume']} م³")], [ar("السقف"), ar("جمالوني" if d["roof"]=="gable" else "أحادي")],
          [ar("الميل"), ar(f"{d['slope']}%")], [ar("المعالف"), ar(f"{d['feeders']} ({d['fdr_len']}م)")],
          [ar("نوع المعالف"), ar(d.get("ft", ""))], [ar("السقايات"), ar(f"{d['drinkers']} ({d['drk_len']}م)")],
          [ar("نوع السقايات"), ar(d.get("dt", ""))], [ar("الممر"), ar(f"{d.get('aisle', 1.5)} م")]]
    t = Table(bd, colWidths=[220, 230])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')), ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')), ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), fontmgr.name), ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
    story.append(t); story.append(Spacer(1, 15))
    im = barn_img(d)
    if im:
        try: story.append(RLImage(im, width=480, height=340))
        except: pass
    story.append(PageBreak())

    # ص3: الجدوى الفنية
    story.append(P("🔧 الباب الثاني: الجدوى الفنية", 18, TA_CENTER, '#1b5e20'))
    story.append(Spacer(1, 8)); story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#d4af37')))
    story.append(Spacer(1, 15))
    def mini(title, color, rows):
        story.append(P(title, 13, c=color)); story.append(Spacer(1, 5))
        dt = [[ar("البند"), ar("القيمة")]] + [[ar(a), ar(b)] for a, b in rows]
        t = Table(dt, colWidths=[220, 230])
        t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), HexColor(color)), ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.6, HexColor('#bdbdbd')), ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), fontmgr.name), ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
        story.append(t); story.append(Spacer(1, 12))
    mini("🍽️ العلف", '#e65100', [("علف/رأس/يوم", f"{f['feed']['per_head']*1000:.0f} جم"),
        ("إجمالي يومي", f"{f['feed']['day']:.1f} كجم"), ("إجمالي شهري", f"{f['feed']['month']:.2f} طن"),
        ("إجمالي سنوي", f"{f['feed']['year']:.2f} طن")])
    mini("💧 الماء", '#1976d2', [("ماء/رأس/يوم", f"{f['water']['per_head']:.1f} لتر"),
        ("إجمالي يومي", f"{f['water']['day']:.0f} لتر"), ("إجمالي سنوي", f"{f['water']['year']:.1f} م³")])
    mini("💨 التهوية", '#558b2f', [("صيفي", f"{f['vent']['summer']:,} م³/س"),
        ("شتوي", f"{f['vent']['winter']:,} م³/س"), ("مساحة الفتحات", f"{d['vent_area']} م²")])
    mini("👷 العمالة", '#6d4c41', [("عدد العمال", str(f['labor']['workers'])),
        ("حيوانات/عامل", str(f['labor']['per_worker']))])
    story.append(PageBreak())

    # ص4: الإنتاج
    story.append(P("📊 الباب الثالث: الإنتاج المتوقع", 18, TA_CENTER, '#1b5e20'))
    story.append(Spacer(1, 8)); story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#d4af37')))
    story.append(Spacer(1, 15))
    pr = f["production"]
    story.append(P(f"نوع الإنتاج: {pr.get('unit', '—')}", 14, c='#c62828')); story.append(Spacer(1, 10))
    prow = [[ar("البند"), ar("القيمة")]]
    for k, lb in [("annual", "سنوي"), ("per_day", "يومي"), ("per_cycle", "دورة"),
                  ("cycles", "عدد الدورات/سنة"), ("lact_d", "أيام الحلابة"), ("weight_ton", "طن")]:
        if k in pr and pr[k]:
            v = pr[k]; prow.append([ar(lb), ar(f"{v:,.1f}" if isinstance(v, (int, float)) else str(v))])
    if pr.get("details"): prow.append([ar("التفاصيل"), ar(pr["details"])])
    t = Table(prow, colWidths=[220, 230])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')), ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')), ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), fontmgr.name), ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
    story.append(t); story.append(Spacer(1, 20))
    story.append(P("📝 ملاحظات", 13, c='#1b5e20')); story.append(Spacer(1, 8))
    for n in ["• دراسة فنية فقط (بدون اقتصاديات).", "• وفق NRC/FAO/MWPS/ASABE.",
              f"• المساحة/رأس: {s['area']} م².", f"• طول المعلف/رأس: {s['fed']} سم.",
              "• يُنصح بإعادة التقييم كل 6 أشهر."]:
        story.append(P(n, 10, c='#444'))
    story.append(PageBreak())

    # ص5: التوقيع
    story.append(Spacer(1, 60))
    story.append(P("✍️ الاعتماد والتوقيع", 20, TA_CENTER, '#1b5e20')); story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37'))); story.append(Spacer(1, 40))
    story.append(P("أُعدّت بمعرفة:", 13, TA_CENTER, '#1a1a1a')); story.append(Spacer(1, 20))
    story.append(P(SUPERVISOR, 20, TA_CENTER, '#c62828'))
    story.append(P(SUPERVISOR_TITLE, 13, TA_CENTER, '#1b5e20')); story.append(Spacer(1, 50))
    sig = [[ar("توقيع المختص"), ar("التاريخ")], [ar("........................"), ar(datetime.now().strftime('%Y-%m-%d'))]]
    st = Table(sig, colWidths=[220, 220])
    st.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, -1), fontmgr.name),
        ('FONTSIZE', (0, 0), (-1, -1), 11), ('TOPPADDING', (0, 0), (-1, -1), 15), ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#1b5e20')), ('INNERGRID', (0, 0), (-1, -1), 0.8, HexColor('#c8e6c9')),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f5e9'))]))
    story.append(st); story.append(Spacer(1, 50))
    story.append(P(f"🤲 {DUA_FULL} 🤲", 12, TA_CENTER, '#c62828'))
    doc.build(story, onFirstPage=pdfgen._page, onLaterPages=pdfgen._page)
    buf.seek(0); return buf.getvalue()

# ═══════════════ Session State ═══════════════
DEF = {
    "approved": False, "user_role": None, "active_formula": {}, "active_stage": "إنتاج عام",
    "active_img": ANIMAL_IMGS["عام"], "computed_cost": 280.0, "inventory": {},
    "shared_comments": f"• مرحباً بكم في {APP_NAME}\n• {DUA_SHORT}\n",
    "broiler_farms": {},
    "livestock_prices": {"عجول ($)": 1350, "أبقار ($)": 900, "ضأن ($)": 180, "ماعز ($)": 130, "إبل ($)": 1200, "كتكوت ($)": 0.65},
    "products_prices": {"لحم بقري ($/كجم)": 7.5, "لحم ضأن ($/كجم)": 9, "لحم إبل ($/كجم)": 8.5,
                         "لحم دجاج ($/كجم)": 3.8, "طبق بيض ($)": 4.2, "حليب بقر ($/لتر)": 0.9},
    "last_result": None, "last_ctx": None, "barn_gif": None,
}
for k, v in DEF.items():
    if k not in st.session_state: st.session_state[k] = v
if not st.session_state["inventory"]:
    for cat in FEEDS.values():
        for ing in cat: st.session_state["inventory"][ing] = {"quantity": 25.0}

def is_owner(): return st.session_state.get("user_role") == "owner"

# ═══════════════ CSS ═══════════════
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri&display=swap');
* { font-family: 'Cairo', 'Amiri', sans-serif; color: #1a1a1a !important; }
html, body, [data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600");
    background-size: cover; background-position: center; background-attachment: fixed; }
.stApp { background: transparent; }
.main-box { background: rgba(255,255,255,0.98); padding: 30px; border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18); margin-bottom: 60px; backdrop-filter: blur(5px); }
.dua-main-box { background: linear-gradient(135deg, #0d3011, #1b5e20, #2e7d32, #1b5e20, #0d3011);
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
.visitor-dua { background: linear-gradient(135deg, #fff8e1, #ffecb3, #ffe082);
    padding: 20px 28px; border-radius: 18px; border: 3px solid #d4af37;
    margin: 22px 0; direction: rtl; text-align: center; }
.visitor-dua * { color: #4e342e !important; }
.visitor-dua b { color: #c62828 !important; font-size: 1.15rem; font-family: 'Amiri', serif !important; }
.dua-footer { position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32, #1b5e20, #0d3011);
    color: white !important; padding: 11px 20px; z-index: 9998; text-align: center;
    border-top: 3px solid #d4af37; font-family: 'Amiri', serif !important;
    font-size: 1.05rem; font-weight: bold; }
.dua-footer * { color: #ffeb3b !important; }
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
.profile-img { width: 150px; height: 150px; border-radius: 50%; object-fit: cover;
    border: 4px solid #d4af37; box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    display: block; margin: 0 auto; }
.stButton > button { color: #1a1a1a !important; background-color: #e8f5e9 !important;
    border: 1px solid #2e7d32 !important; font-weight: bold !important; }
.stButton > button:hover { background-color: #c8e6c9 !important; }
.sig { position: fixed; left: 20px; bottom: 65px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important; padding: 9px 22px; font-size: 0.88rem;
    border-radius: 25px; z-index: 9997; direction: rtl;
    border: 2px solid #d4af37; font-weight: bold; }
.sig * { color: white !important; }
</style>""", unsafe_allow_html=True)

# ═══════════════ بوابة الدخول ═══════════════
if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width:780px; margin:30px auto; direction:rtl;">', unsafe_allow_html=True)
    st.markdown(f"""<div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <p style="font-size:1.1rem; color:#a5d6a7 !important; margin-bottom:12px;">
        نبدأ باسم الله، ونسألُه أن يتقبّلَ هذا العملَ صدقةً جاريةً عن:</p>
        <div class="names">🕊️ رحم الله والدي إسماعيل تاور وأختي ابتسام 🕊️</div>
        <p class="quran">{DUA_QURAN}</p><p class="quran" style="margin-top:10px;">{DUA_VERSE}</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("<hr style='border-top:2px solid #d4af37; margin:25px 0;'>", unsafe_allow_html=True)
    cl, ct = st.columns([0.3, 0.7])
    with cl:
        if img_b64: st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" class="profile-img">', unsafe_allow_html=True)
        else: st.markdown(f'<img src="{ANIMAL_IMGS["عام"]}" class="profile-img">', unsafe_allow_html=True)
    with ct:
        st.markdown(f"<h2 style='color:#2E7D32; text-align:right;'>🌾 {APP_NAME}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.1rem;'>{APP_TAGLINE}</p>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#c62828; text-align:right;'>{SUPERVISOR} — {SUPERVISOR_TITLE}</h4>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#1b5e20; margin-top:20px;'>🔐 بوابة الدخول</h3>", unsafe_allow_html=True)
    co, cg = st.columns(2)
    with co:
        st.markdown("""<div style="background:linear-gradient(135deg,#e8f5e9,#c8e6c9); padding:20px;
        border-radius:12px; border:2px solid #2e7d32; text-align:center; margin-bottom:10px;">
        <h4 style="color:#1b5e20;">👑 المالك</h4><p style="font-size:0.9rem;">كود خاص</p></div>""", unsafe_allow_html=True)
        code = st.text_input("🔑 كود المالك:", type="password", key="owner_code")
        if st.button("👑 دخول المالك", type="primary", use_container_width=True):
            if code.strip() == OWNER_CODE:
                st.session_state.update({"approved": True, "user_role": "owner"}); st.rerun()
            else: st.error("❌ كود غير صحيح")
    with cg:
        st.markdown("""<div style="background:linear-gradient(135deg,#fff8e1,#ffecb3); padding:20px;
        border-radius:12px; border:2px solid #d4af37; text-align:center; margin-bottom:10px;">
        <h4 style="color:#e65100;">👥 زائر</h4>
        <p style="font-size:0.9rem;">مجاني<br><small>حظائر 3D + جدوى + مزارع</small></p></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True):
            st.session_state.update({"approved": True, "user_role": "guest"}); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True); st.stop()

# ═══════════════ الواجهة الرئيسية ═══════════════
st.markdown('<div class="main-box">', unsafe_allow_html=True)
c1, c2 = st.columns([0.7, 0.3])
with c2:
    rl = "المالك 👑" if is_owner() else "زائر 👥"
    st.markdown(f"<div style='text-align:left; padding:10px; background:#f5f5f5; border-radius:10px;'>الحساب: <b>{rl}</b></div>", unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k != "inventory": del st.session_state[k]
        st.session_state["approved"] = False; st.rerun()
c3, c4 = st.columns([0.3, 0.7])
with c3:
    if img_b64: st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" class="profile-img">', unsafe_allow_html=True)
    else: st.markdown(f'<img src="{ANIMAL_IMGS["عام"]}" class="profile-img">', unsafe_allow_html=True)
with c4:
    st.markdown(f"<h1 style='color:#0d3011; text-align:right; font-weight:900; font-size:2.3rem;'>🌾 {APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.25rem; font-weight:600;'>{APP_TAGLINE}</p>", unsafe_allow_html=True)
    st.markdown(f"""<div style='background:linear-gradient(135deg,#fff8e1,#ffe082); padding:12px 20px;
    border-radius:12px; border-right:6px solid #c62828; border-left:6px solid #c62828; margin-top:10px;'>
    <h3 style='color:#b71c1c; text-align:right; margin:0; font-weight:900; font-size:1.55rem;'>
    👨‍🔬 {SUPERVISOR}</h3>
    <p style='color:#0d47a1; text-align:right; margin:5px 0 0 0; font-weight:700; font-size:1.15rem;'>✨ {SUPERVISOR_TITLE}</p></div>""", unsafe_allow_html=True)
st.markdown(f'<div class="visitor-dua">{DUA_BANNER}</div>', unsafe_allow_html=True)
st.markdown("<hr style='border-top:3px solid #2e7d32;'>", unsafe_allow_html=True)

# ═══════════════ التبويبات ═══════════════
if is_owner():
    TITLES = ["🔬 النمذجة", "🌰 الزيوت", "🍼 بدائل الحليب", "📷 OCR",
               "🏗️ الحظائر 3D", "📊 دراسة الجدوى", "🐔 مزارع الدجاج",
               "📊 البورصة", "🏭 المستودعات", "🧾 الفواتير", "🖨️ الديباجة",
               "📈 التحليلات", "💬 التعليقات", "📚 المراجع", "💡 المساعدة", "📖 الدليل"]
else:
    TITLES = ["🔬 النمذجة", "🌰 الزيوت", "🍼 بدائل الحليب", "📷 OCR",
               "🏗️ الحظائر 3D", "📊 دراسة الجدوى", "🐔 مزارع الدجاج",
               "📚 المراجع", "💡 المساعدة", "📖 الدليل"]

tabs = st.tabs(TITLES)
TM = {t: tab for t, tab in zip(TITLES, tabs)}

# ═══════ النمذجة ═══════
with TM["🔬 النمذجة"]:
    try:
        sub1, sub2 = st.tabs(["🎯 تركيب علفة", "🔬 مختبر الأعلاف"])
        with sub1:
            try:
                st.markdown('<div class="section-title">🌍 الموقع</div>', unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                with c1: country = st.selectbox("الدولة:", list(RATES.keys()), key="country")
                with c2: state = st.text_input("الولاية:", "الخرطوم", key="state")
                with c3: city = st.text_input("المدينة:", "الخرطوم", key="city")
                lr, ls = RATES.get(country, (1, "USD"))
                prices_live = market_prices(country)

                st.markdown('<div class="section-title">🧬 أساس الحساب</div>', unsafe_allow_html=True)
                basis = st.radio("اختر:", ["البروتين المهضوم (DP)", "البروتين الخام (CP)"], horizontal=True, key="basis")
                use_dp = "DP" in basis; bc = "DP" if use_dp else "CP"

                st.markdown('<div class="section-title">🐾 الحيوان</div>', unsafe_allow_html=True)
                atabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐪 إبل", "🐎 خيول", "🐔 دواجن", "🦆 سمان", "🐟 أسماك"])
                ac = None; pt = None; req = None; ik = "عام"; sk = ""

                with atabs[0]:
                    ct = st.selectbox("الحالة:", ["حليب_عالي","حليب_متوسط","حليب_منخفض","تسمين_مكثف","تسمين_عادي","حمل_أخير","صيانة"], key="cattle_t")
                    c1_, c2_ = st.columns(2); cpr = {}
                    with c1_:
                        if "حليب" in ct: cpr["milk"] = st.number_input("حليب:", 5.0, 60.0, 20.0, 1.0, key="cm")
                        cpr["wt"] = st.number_input("وزن:", 200.0, 900.0, 500.0, 25.0, key="cw")
                    with c2_:
                        rp = req_cattle(ct, **cpr)
                        st.metric("DP", f"{rp.DP}%"); st.metric("CP", f"{rp.CP}%"); st.metric("SE", f"{rp.SE}")
                    if st.checkbox("✅ اعتماد", key="uc"):
                        ac="أبقار"; pt=ct; req=rp; ik="أبقار"; sk=f"أبقار_{ct}"
                with atabs[1]:
                    sg = st.radio("جنس:", ["ذكر","أنثى"], horizontal=True, key="sg")
                    im = "ذكر" in sg
                    if im: sht = st.selectbox("حالة:", ["تسمين_مكثف","تسمين_عادي","حملان_تيد"], key="shtm")
                    else: sht = st.selectbox("حالة:", ["مرضعات","حامل_أخير","حامل_متوسط","صيانة"], key="shtf")
                    lit = 1
                    if sht == "مرضعات": lit = st.number_input("مواليد:", 1, 3, 1, 1, key="slit")
                    wt = st.number_input("وزن:", 15.0, 120.0, 50.0, 5.0, key="sw")
                    rp = req_sheep(sht, male=im, wt=wt, litter=lit)
                    p1,p2,p3 = st.columns(3); p1.metric("DP", f"{rp.DP}%"); p2.metric("CP", f"{rp.CP}%"); p3.metric("SE", f"{rp.SE}")
                    if st.checkbox("✅ اعتماد", key="us"):
                        ac="أغنام"; pt=sht; req=rp; ik="أغنام"; sk=f"أغنام_{sht}"
                with atabs[2]:
                    gg = st.radio("جنس:", ["ذكر","أنثى"], horizontal=True, key="gg")
                    img_ = "ذكر" in gg; mg = 0
                    if img_: gt = st.selectbox("حالة:", ["تسمين_جديان","تيوس"], key="gtm")
                    else:
                        gt = st.selectbox("حالة:", ["حلابة_عالي","حلابة_متوسط","حامل_أخير","صيانة"], key="gtf")
                        if "حلابة" in gt: mg = st.number_input("حليب:", 0.5, 8.0, 2.0, 0.25, key="gm")
                    rp = req_goat(gt, male=img_, milk=mg)
                    p1,p2,p3 = st.columns(3); p1.metric("DP", f"{rp.DP}%"); p2.metric("CP", f"{rp.CP}%"); p3.metric("SE", f"{rp.SE}")
                    if st.checkbox("✅ اعتماد", key="ug"):
                        ac="ماعز"; pt=gt; req=rp; ik="ماعز"; sk=f"ماعز_{gt}"
                with atabs[3]:
                    c_t = st.selectbox("حالة:", ["نمو","تسمين","حليب","سباق","صيانة"], key="ct")
                    cw = st.number_input("وزن:", 100.0, 800.0, 400.0, 25.0, key="cw2")
                    cm = 5.0
                    if c_t == "حليب": cm = st.number_input("حليب:", 2.0, 20.0, 5.0, 0.5, key="cm2")
                    rp = req_camel(c_t, wt=cw, milk=cm)
                    p1,p2,p3 = st.columns(3); p1.metric("DP", f"{rp.DP}%"); p2.metric("CP", f"{rp.CP}%"); p3.metric("SE", f"{rp.SE}")
                    if st.checkbox("✅ اعتماد", key="ucm"):
                        ac="إبل"; pt=c_t; req=rp; ik="إبل"; sk=f"إبل_{c_t}"
                with atabs[4]:
                    ht = st.selectbox("حالة:", ["رياضة_مكثف","رياضة_عادي","نمو_أمهار","مرضعات","صيانة"], key="ht")
                    hw = st.number_input("وزن:", 200.0, 800.0, 450.0, 25.0, key="hw")
                    rp = req_horse(ht, wt=hw)
                    p1,p2,p3 = st.columns(3); p1.metric("DP", f"{rp.DP}%"); p2.metric("CP", f"{rp.CP}%"); p3.metric("SE", f"{rp.SE}")
                    if st.checkbox("✅ اعتماد", key="uh"):
                        ac="خيول"; pt=ht; req=rp; ik="خيول"; sk=f"خيول_{ht}"
                with atabs[5]:
                    ps = st.radio("سلالة:", ["لاحم","بياض"], horizontal=True, key="ps")
                    pa = st.number_input("عمر (أسبوع):", 1, 20, 1, 1, key="pa")
                    rp = req_poultry(ps, pa)
                    p1,p2,p3,p4 = st.columns(4)
                    p1.metric("DP", f"{rp.DP}%"); p2.metric("CP", f"{rp.CP}%"); p3.metric("SE", f"{rp.SE}"); p4.metric("Ca", f"{rp.Ca}%")
                    if st.checkbox("✅ اعتماد", key="up"):
                        ac="دواجن"; pt=ps; req=rp; ik="دواجن"
                        sk = "دواجن_بادي" if "بادي" in rp.name else "دواجن_نامي" if "نامي" in rp.name else "دواجن_بياض" if "بياض" in rp.name else "دواجن_ناهي"
                with atabs[6]:
                    qs = st.radio("نوع:", ["تسمين","بياض"], horizontal=True, key="qs")
                    qa = st.number_input("عمر:", 1, 8, 1, 1, key="qa")
                    rp = req_quail(qs, qa)
                    p1,p2,p3 = st.columns(3); p1.metric("DP", f"{rp.DP}%"); p2.metric("CP", f"{rp.CP}%"); p3.metric("SE", f"{rp.SE}")
                    if st.checkbox("✅ اعتماد", key="uq"):
                        ac="سمان"; pt=qs; req=rp; ik="سمان"; sk="سمان_بياض" if qs=="بياض" else "سمان_بادي"
                with atabs[7]:
                    fs = st.selectbox("نوع:", ["البلطي","القرموط","الكارب"], key="fs")
                    fst = st.selectbox("مرحلة:", ["بادئ زريعة","نمو","تسمين"], key="fst")
                    rp = req_fish(fs, fst)
                    p1,p2,p3 = st.columns(3); p1.metric("DP", f"{rp.DP}%"); p2.metric("CP", f"{rp.CP}%"); p3.metric("SE", f"{rp.SE}")
                    if st.checkbox("✅ اعتماد", key="uf"):
                        ac="أسماك"; pt=fst; req=rp; ik="أسماك"
                        sk = "أسماك_بادئ" if "بادئ" in fst or "زريعة" in fst else "أسماك_نمو" if "نمو" in fst else "أسماك_تسمين"

                ready = bool(ac and req)
                if not ready:
                    st.warning("⚠️ اختر حيواناً وفعّل ✅ الاعتماد")
                    if st.session_state.get("last_result"):
                        st.markdown("### 📋 آخر نتيجة")
                        prev = st.session_state["last_result"]
                        for ing, pct in prev["formula"].items():
                            st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.2f}%</div>', unsafe_allow_html=True)
                if ready:
                    st.markdown(f'<div class="section-title">🎯 {ac} — {req.name}</div>', unsafe_allow_html=True)
                    ic = st.columns(4)
                    ic[0].metric("DP", f"{req.DP}%"); ic[1].metric("CP", f"{req.CP}%")
                    ic[2].metric("SE", f"{req.SE}"); ic[3].metric("NDF", f"{req.NDF}%")
                    oi = get_oil_std(sk)
                    st.markdown(f'<div class="oil-info-card"><b>🌰 حد الزيوت: {oi["max"]}%</b> | مثالي: {oi["optimal"]}%<br>{oi["src"]}</div>', unsafe_allow_html=True)
                    rname = st.text_input("👤 اسم طالب العلفة:", placeholder="مزرعة الأمل", key="rname")

                    st.markdown('<div class="section-title">🌾 المكونات</div>', unsafe_allow_html=True)
                    selected = []; prices = {}
                    for cname, items in FEEDS.items():
                        with st.expander(f"📁 {cname}", expanded=("الحبوب" in cname or "الأكساب" in cname)):
                            cols = st.columns(3)
                            for idx, (ing, id_) in enumerate(items.items()):
                                with cols[idx % 3]:
                                    dflt = ing in ["ملح الطعام","الحجر الجيري","فوسفات ثنائي كالسيوم","مضاد سموم"]
                                    if ac in ["أغنام","ماعز","أبقار","إبل"]: dflt = dflt or (ing == "بيكربونات صوديوم")
                                    if ac in ["دواجن","سمان"]: dflt = dflt or ("بريمكس" in ing)
                                    ch = st.checkbox(ing, value=dflt, key=f"f_{ac}_{ing}")
                                    cp = prices_live.get(ing, 350)
                                    if is_owner():
                                        pi = st.number_input(f"${ing}:", min_value=5.0, value=float(cp), key=f"p_{ac}_{ing}")
                                    else:
                                        st.markdown(f"💰 `${cp:.2f}`")
                                        pi = cp
                                    if ch: selected.append(ing); prices[ing] = pi

                    cb1, cb2 = st.columns([0.7, 0.3])
                    with cb1:
                        run = st.button("🚀 تشغيل المحرك", type="primary", use_container_width=True, key="run")
                    with cb2:
                        if st.session_state.get("last_result"):
                            if st.button("🗑️ مسح", use_container_width=True, key="clr"):
                                st.session_state["last_result"] = None; st.session_state["last_ctx"] = None; st.rerun()
                    if run:
                        if len(selected) < 3:
                            st.error("⚠️ اختر 3 مكونات على الأقل")
                        else:
                            for sn in auto_salts(ac, req):
                                if sn not in selected: selected.append(sn); prices[sn] = prices_live.get(sn, 300)
                            cstd = req_to_std(req)
                            with st.spinner(f"⏳ التركيب على أساس {bc}..."):
                                result = formulate(selected, prices, cstd, standard_key=sk, tol=0.3, max_it=50, basis=bc)
                            if result["success"]:
                                st.session_state["last_result"] = result
                                st.session_state["last_ctx"] = {
                                    "ac": ac, "rname_ar": req.name, "basis": bc, "req": req,
                                    "cstd": cstd, "city": city, "lr": lr, "ls": ls,
                                    "rname": rname, "sk": sk, "ik": ik, "at": ac}
                                st.session_state["active_formula"] = result["formula"]
                                st.session_state["computed_cost"] = result["cost"]
                            else: st.error(f"❌ {result['message']}")

                    if st.session_state.get("last_result"):
                        result = st.session_state["last_result"]; ctx = st.session_state["last_ctx"]
                        formula = result["formula"]; actual = result["actual"]
                        cost = result["cost"]; oil_t = result.get("total_oil", 0)
                        ostd = result.get("oil_std", get_oil_std(sk))
                        cstd = ctx["cstd"]; bl = ctx["basis"]

                        rows = []; scores = []
                        LBL = {"CP":"بروتين خام","DP":"بروتين مهضوم","SE":"معادل النشاء","NDF":"NDF","ADF":"ADF",
                               "EE":"دهن","ASH":"رماد","Ca":"كالسيوم","P":"فسفور"}
                        for k, sv in cstd.items():
                            cv = actual.get(k, 0); diff = cv - sv
                            pct = (diff/sv*100) if sv else 0
                            ev = diff_eval(pct, sv)
                            scores.append({"score": ev["score"]})
                            rows.append({"العنصر": LBL.get(k, k), "المعيار": f"{sv:.2f}",
                                "المحسوب": f"{cv:.2f}", "الفرق": f"{diff:+.3f}",
                                "الفرق %": f"{pct:+.2f}%", "التقييم": ev["label"]})
                        overall = overall_rating(scores)

                        st.success(f"✅ تم التركيب — {bl} | {overall['label']}")
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                        if oil_t > 0:
                            if oil_t > ostd["max"]: st.error(f"⚠️ تجاوز الزيوت! {oil_t:.2f}% > {ostd['max']}%")
                            else: st.success(f"✅ الزيوت: {oil_t:.2f}% (مثالي {ostd['optimal']}%)")

                        st.markdown('<div class="section-title">📈 الرسوم البيانية</div>', unsafe_allow_html=True)
                        ch1, ch2 = st.columns(2)
                        with ch1:
                            b = chart_bar(cstd, actual)
                            if b: st.image(b.getvalue(), caption="مقارنة العناصر", use_container_width=True)
                        with ch2:
                            p = chart_pie(formula)
                            if p: st.image(p.getvalue(), caption="توزيع المكونات", use_container_width=True)
                        ch3, ch4 = st.columns(2)
                        with ch3:
                            r = chart_radar(cstd, actual)
                            if r: st.image(r.getvalue(), caption="الرادار", use_container_width=True)
                        with ch4:
                            g = chart_gauge(overall["score"])
                            if g: st.image(g.getvalue(), caption="التقييم", use_container_width=True)

                        st.markdown("### 🌾 المكونات")
                        for ing, pct in formula.items():
                            st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.2f}% ({pct*10:.1f} كجم/طن)</div>', unsafe_allow_html=True)
                        st.metric("💰 التكلفة/طن:", f"${cost:.2f} ({cost*ctx['lr']:,.0f} {ctx['ls']})")

                        dl1, dl2 = st.columns(2)
                        with dl1:
                            try:
                                pdf = pdfgen.report(formula, ctx["req"], ctx["at"], ctx["rname_ar"],
                                    cost, ctx["city"], cost*ctx["lr"], ctx["ls"], ctx["rname"], bl, ctx["sk"])
                                st.download_button("📥 تحميل PDF", pdf,
                                    file_name=f"Tawor_{ctx['at']}_{datetime.now():%Y%m%d}.pdf",
                                    mime="application/pdf", use_container_width=True)
                            except Exception as e: st.error(f"⚠️ PDF: {e}")
                        with dl2:
                            try:
                                xl = export_xl(cstd, actual)
                                if xl:
                                    st.download_button("📊 تحميل Excel", xl,
                                        file_name=f"Tawor_{ctx['at']}_{datetime.now():%Y%m%d}.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True)
                            except Exception as e: st.error(f"⚠️ Excel: {e}")
            except Exception as e:
                st.error(f"⚠️ خطأ: {e}")
                with st.expander("تفاصيل"): st.code(traceback.format_exc())

        with sub2:
            try:
                st.markdown('<div class="section-title">🔬 مختبر الأعلاف</div>', unsafe_allow_html=True)
                cl1, cl2 = st.columns(2)
                with cl1: tgt = st.selectbox("فصيل:", ["أبقار","أغنام","ماعز","خيول","إبل","دواجن","سمان","أسماك"], key="ltgt")
                with cl2: stg = st.selectbox("مرحلة:", ["تسمين","حليب","حمل","صيانة"], key="lstg")
                tv = st.number_input("مستهدف %", 5.0, 50.0, 15.0, 0.1, key="ltv")
                st.subheader("📥 الأوزان (كجم):")
                inputs = {}; alli = []
                for cat in FEEDS.values():
                    for i in cat: alli.append(i)
                cols = st.columns(3)
                for idx, i in enumerate(alli):
                    with cols[idx % 3]:
                        inputs[i] = st.number_input(f"{i}:", 0.0, value=0.0, step=5.0, key=f"lb_{i}")
                if st.button("🧪 تحليل", type="primary", use_container_width=True):
                    tw = sum(inputs.values())
                    if tw > 0:
                        ccp = 0.0; cdp = 0.0; cse = 0.0; comps = []
                        for i, w in inputs.items():
                            if w > 0:
                                pct = w/tw; icp = 0.0; idc = 0.0; ise = 0.0
                                for cat in FEEDS.values():
                                    if i in cat: icp = cat[i].get("CP", 0); idc = cat[i].get("DC", 0); ise = cat[i].get("SE", 0)
                                ccp += pct*icp; cdp += pct*(icp*idc); cse += pct*ise
                                comps.append({"المادة": i, "الوزن": f"{w:.1f}", "النسبة": f"{pct*100:.2f}%"})
                        st.success("✅ تم التحليل")
                        st.markdown(f"**إجمالي:** {tw:.1f} كجم")
                        st.table(pd.DataFrame(comps))
                        st.write(f"**CP:** {ccp:.2f}% | **DP:** {cdp:.2f}% | **SE:** {cse:.2f}")
                    else: st.warning("⚠️ أدخل أوزان")
            except Exception as e: st.error(f"⚠️ {e}")
    except Exception as e: st.error(f"⚠️ {e}")

# ═══════ الزيوت ═══════
with TM["🌰 الزيوت"]:
    try:
        st.markdown('<div class="section-title">🌰 مكتبة الزيوت</div>', unsafe_allow_html=True)
        rows = [{"الحالة": k, "الأقصى %": f"{v['max']}%", "المثالي %": f"{v['optimal']}%", "المرجع": v["src"]}
                for k, v in OIL_STD.items()]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        oils = get_oils()
        for ing, d in oils.items():
            with st.expander(f"🌰 {ing}"):
                st.write(f"⚡ SE: {d.get('SE', 0)}")
                st.write(f"📝 {d.get('desc', '')}")
                st.caption(f"📖 {d.get('src', '')}")
    except Exception as e: st.error(f"⚠️ {e}")

# ═══════ بدائل الحليب ═══════
with TM["🍼 بدائل الحليب"]:
    try:
        st.markdown('<div class="section-title">🍼 بدائل الحليب</div>', unsafe_allow_html=True)
        st.info("🚧 قريباً — يمكن تطويرها بطلب من المالك")
        mr_std = {"عجول": {"CP": 24, "Fat": 24}, "حملان": {"CP": 24, "Fat": 24},
                  "جديان": {"CP": 24, "Fat": 24}, "إبل": {"CP": 26, "Fat": 28}, "أمهار": {"CP": 22, "Fat": 20}}
        ma = st.selectbox("نوع:", list(mr_std.keys()), key="ma")
        c = st.columns(2)
        c[0].metric("CP", f"{mr_std[ma]['CP']}%")
        c[1].metric("Fat", f"{mr_std[ma]['Fat']}%")
    except Exception as e: st.error(f"⚠️ {e}")

# ═══════ OCR ═══════
with TM["📷 OCR"]:
    try:
        st.markdown('<div class="section-title">📷 OCR</div>', unsafe_allow_html=True)
        if not OCR: st.error("⚠️ pytesseract غير مثبت")
        else:
            up = st.file_uploader("صورة", type=["jpg","jpeg","png"])
            if up:
                st.image(up, use_container_width=True)
                if st.button("🔍 تحليل", type="primary"):
                    with st.spinner("..."):
                        try:
                            nparr = np.frombuffer(up.read(), np.uint8)
                            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                            txt = pytesseract.image_to_string(gray, lang='ara+eng')
                            st.success("✅ تم")
                            st.text(txt)
                        except Exception as e: st.error(f"❌ {e}")
    except Exception as e: st.error(f"⚠️ {e}")

# ═══════ الحظائر 3D ═══════
with TM["🏗️ الحظائر 3D"]:
    try:
        st.markdown('<div class="section-title">🏗️ تصميم الحظائر 3D</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: bk = st.selectbox("نوع:", list(BARN_STD.keys()),
            format_func=lambda k: BARN_STD[k]["name"], key="bk")
        with c2: bc = st.number_input("عدد:", 1, 100000, 1000, 50, key="bc")
        with c3: bs = st.selectbox("نظام:", ["أرضي","بطاريات"], key="bs")

        mult = 1.0
        if "بطاريات" in bs and bk in ["دواجن_لاحم","دواجن_بياض","سمان"]: mult = 0.55
        dims = calc_barn(bk, bc)
        if dims and mult != 1.0:
            dims["total_area"] = round(dims["total_area"]*mult, 2)
            dims["length"] = round(dims["total_area"]/dims["width"], 2)

        if dims:
            k = st.columns(4)
            k[0].metric("📏 المساحة", f"{dims['total_area']} م²")
            k[1].metric("📐 الأبعاد", f"{dims['length']}×{dims['width']} م")
            k[2].metric("🏔️ القمة", f"{dims['ridge']} م")
            k[3].metric("📦 الحجم", f"{dims['volume']} م³")
            k2 = st.columns(4)
            k2[0].metric("🍽️ معالف", dims["feeders"])
            k2[1].metric("📏 طول المعالف", f"{dims['fdr_len']} م")
            k2[2].metric("💧 سقايات", dims["drinkers"])
            k2[3].metric("💨 تهوية صيف", f"{dims['vent_s']:,}")

            st.markdown("### 🏗️ المجسم 3D")
            fig = fig_3d(dims)
            if fig: st.plotly_chart(fig, use_container_width=True,
                config={"displayModeBar": True, "toImageButtonOptions": {"format": "png", "filename": f"barn_{bk}"}})

            st.markdown('<div class="section-title">🎬 فيديو GIF</div>', unsafe_allow_html=True)
            if st.button("🎬 توليد فيديو GIF", type="primary", use_container_width=True, key="gif_b"):
                with st.spinner("🎥 توليد..."):
                    gb = gif_barn(dims)
                if gb:
                    st.session_state["barn_gif"] = gb.getvalue(); st.success("✅ تم!")
                else: st.error("⚠️ تعذر التوليد")
            if st.session_state.get("barn_gif"):
                st.image(st.session_state["barn_gif"], use_container_width=True)
                st.download_button("⬇️ تحميل GIF", st.session_state["barn_gif"],
                    file_name=f"barn_{bk}_{bc}.gif", mime="image/gif",
                    use_container_width=True, type="primary")
    except Exception as e:
        st.error(f"⚠️ {e}")
        with st.expander("تفاصيل"): st.code(traceback.format_exc())

# ═══════ الجدوى ═══════
with TM["📊 دراسة الجدوى"]:
    try:
        st.markdown('<div class="section-title">📊 دراسة الجدوى الفنية</div>', unsafe_allow_html=True)
        st.markdown("""<div class="feas-card">
        <b>🎯 دراسة فنية شاملة:</b><br>
        ▪️ تصميم الحظيرة + مجسم 3D<br>
        ▪️ العلف والماء والتهوية والعمالة<br>
        ▪️ الإنتاج المتوقع<br>
        ▪️ كتيّب PDF كامل بالتوقيع والختم
        </div>""", unsafe_allow_html=True)

        f1, f2 = st.columns(2)
        with f1:
            fk = st.selectbox("نوع:", list(BARN_STD.keys()),
                format_func=lambda k: BARN_STD[k]["name"], key="fk")
            fc = st.number_input("عدد:", 1, 100000, 1000, 50, key="fc")
        with f2:
            proj = st.text_input("اسم المشروع:", key="proj")
            freqs = st.text_input("مقدم الطلب:", key="freqs")

        with st.spinner("⏳ حساب..."):
            feas = calc_feas(fk, fc)
        if feas:
            d = feas["dims"]
            st.markdown("### 📐 الحظيرة")
            fc1 = st.columns(4)
            fc1[0].metric("📏 المساحة", f"{d['total_area']} م²")
            fc1[1].metric("📐", f"{d['length']}×{d['width']} م")
            fc1[2].metric("🏔️ القمة", f"{d['ridge']} م")
            fc1[3].metric("📦 الحجم", f"{d['volume']} م³")

            st.markdown("### 🍽️ العلف")
            f = st.columns(4)
            f[0].metric("علف/رأس/يوم", f"{feas['feed']['per_head']*1000:.0f} جم")
            f[1].metric("يومي", f"{feas['feed']['day']:.1f} كجم")
            f[2].metric("شهري", f"{feas['feed']['month']:.2f} طن")
            f[3].metric("سنوي", f"{feas['feed']['year']:.2f} طن")

            st.markdown("### 💧 الماء")
            w = st.columns(3)
            w[0].metric("ماء/رأس", f"{feas['water']['per_head']:.1f} لتر")
            w[1].metric("يومي", f"{feas['water']['day']:.0f} لتر")
            w[2].metric("سنوي", f"{feas['water']['year']:.1f} م³")

            st.markdown("### 💨 التهوية والعمالة")
            v = st.columns(4)
            v[0].metric("صيف", f"{feas['vent']['summer']:,} م³/س")
            v[1].metric("شتاء", f"{feas['vent']['winter']:,} م³/س")
            v[2].metric("عمال", feas["labor"]["workers"])
            v[3].metric("حيوانات/عامل", feas["labor"]["per_worker"])

            st.markdown("### 📊 الإنتاج")
            p = feas["production"]
            st.write(f"**نوع:** {p.get('unit', '—')}")
            pc = st.columns(3)
            if "annual" in p: pc[0].metric("سنوي", f"{p['annual']:,.0f}")
            if "per_day" in p: pc[1].metric("يومي", f"{p['per_day']:,.1f}")
            if "per_cycle" in p: pc[2].metric("دورة", f"{p['per_cycle']:,.0f}")
            if p.get("details"): st.info(f"📝 {p['details']}")

            st.markdown("---")
            st.markdown("### 📄 كتيّب الجدوى (PDF)")
            try:
                bk_pdf = booklet_feas(fk, fc, proj, freqs)
                if bk_pdf:
                    st.download_button("📥 تحميل كتيّب الجدوى الكامل", bk_pdf,
                        file_name=f"Feas_{fk}_{fc}_{datetime.now():%Y%m%d}.pdf",
                        mime="application/pdf", use_container_width=True, type="primary")
            except Exception as e: st.error(f"⚠️ {e}")
    except Exception as e:
        st.error(f"⚠️ {e}")
        with st.expander("تفاصيل"): st.code(traceback.format_exc())

# ═══════ مزارع الدجاج ═══════
with TM["🐔 مزارع الدجاج"]:
    try:
        st.markdown('<div class="section-title">🐔 مزارع الدجاج</div>', unsafe_allow_html=True)
        with st.expander("➕ إضافة", expanded=True):
            n = st.text_input("اسم:", key="nfn")
            o = st.text_input("مالك:", key="nfo")
            if st.button("💾 حفظ") and n:
                st.session_state["broiler_farms"][n] = {"owner": o, "data": {"age": 1, "birds": 1000,
                    "weight_kg": 0.045, "feed_kg": 0.0, "dead": 0, "temp": 33.0, "hum": 65.0}}
                st.success(f"✅ {n}"); st.rerun()
        if st.session_state["broiler_farms"]:
            sel = st.selectbox("اختر:", [""] + list(st.session_state["broiler_farms"].keys()), key="fsel")
            if sel:
                d = st.session_state["broiler_farms"][sel]["data"]
                b1, b2 = st.columns(2)
                with b1:
                    d["age"] = st.number_input("عمر (يوم):", 1, 60, d["age"], key="bf_age")
                    d["birds"] = st.number_input("طيور:", 1, value=d["birds"], key="bf_birds")
                    d["weight_kg"] = st.number_input("وزن:", 0.0, 10.0, float(d["weight_kg"]), 0.01, key="bf_w")
                    d["feed_kg"] = st.number_input("علف:", 0.0, float(d["feed_kg"]), 100.0, key="bf_f")
                with b2:
                    d["dead"] = st.number_input("نافق:", 0, value=d["dead"], key="bf_d")
                    d["temp"] = st.number_input("حرارة:", 10.0, 45.0, float(d["temp"]), key="bf_t")
                    d["hum"] = st.number_input("رطوبة:", 20.0, 90.0, float(d["hum"]), key="bf_h")
                alive = d["birds"] - d["dead"]
                gain = alive*(d["weight_kg"]-0.045)
                adg = ((d["weight_kg"]-0.045)*1000/d["age"]) if d["age"] > 0 else 0
                fcr = (d["feed_kg"]/gain) if gain > 0 else 0
                liv = 100-(d["dead"]/d["birds"]*100)
                epef = ((liv*d["weight_kg"])/(d["age"]*fcr)*100) if d["age"] > 0 and fcr > 0 else 0
                k = st.columns(4)
                k[0].metric("ADG (جم)", f"{adg:.1f}"); k[1].metric("FCR", f"{fcr:.2f}")
                k[2].metric("EPEF", f"{epef:.0f}"); k[3].metric("حيوية %", f"{liv:.1f}")
    except Exception as e: st.error(f"⚠️ {e}")

# ═══════ تبويبات المالك ═══════
if is_owner():
    with TM["📊 البورصة"]:
        try:
            st.markdown('<div class="section-title">📊 البورصة</div>', unsafe_allow_html=True)
            t1, t2 = st.tabs(["🐄 ماشية","🥩 منتجات"])
            with t1:
                for a, p in list(st.session_state["livestock_prices"].items()):
                    st.session_state["livestock_prices"][a] = st.number_input(f"{a}", 0.0, value=float(p), step=0.1, key=f"lv_{a}")
            with t2:
                for pr, p in list(st.session_state["products_prices"].items()):
                    st.session_state["products_prices"][pr] = st.number_input(f"{pr}", 0.0, value=float(p), step=0.05, key=f"pr_{pr}")
        except Exception as e: st.error(f"⚠️ {e}")

    with TM["🏭 المستودعات"]:
        try:
            st.markdown('<div class="section-title">🏭 المستودعات</div>', unsafe_allow_html=True)
            inv = st.session_state["inventory"]
            c = st.columns(4)
            c[0].metric("إجمالي", len(inv))
            c[1].metric("منخفضة", sum(1 for v in inv.values() if v.get("quantity", 0) < 5))
            c[2].metric("نفذت", sum(1 for v in inv.values() if v.get("quantity", 0) <= 0))
            c[3].metric("آمنة", sum(1 for v in inv.values() if v.get("quantity", 0) >= 5))
            cols = st.columns(3)
            for i, (n, d) in enumerate(list(inv.items())[:30]):
                with cols[i % 3]:
                    q = d["quantity"] if isinstance(d, dict) else d
                    b = "🔴" if q <= 0 else ("🟡" if q < 5 else "🟢")
                    st.markdown(f"{b} **{n}**: {q:.1f} طن")
                    nq = st.number_input("تحديث:", 0.0, value=float(q), key=f"inv_{n}", label_visibility="collapsed")
                    if isinstance(inv[n], dict): inv[n]["quantity"] = nq
        except Exception as e: st.error(f"⚠️ {e}")

    with TM["🧾 الفواتير"]:
        try:
            st.markdown('<div class="section-title">🧾 الفواتير</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1: cl = st.text_input("عميل:", "مزرعة الأمل")
            with c2: tn = st.number_input("كمية (طن):", 0.1, 1000.0, 2.0, 0.5)
            with c3: pf = st.number_input("هامش ($/طن):", 0.0, 1000.0, 50.0)
            sell = st.session_state["computed_cost"] + pf
            st.markdown(f"""<div class="price-card">
            <h4>🧾 فاتورة</h4>
            <p><b>العميل:</b> {cl}</p>
            <p><b>الكمية:</b> {tn} طن</p>
            <p><b>سعر الطن:</b> ${sell:.2f}</p>
            <p style="font-size:1.3rem; color:#1b5e20;"><b>الإجمالي:</b> ${sell*tn:.2f}</p></div>""",
            unsafe_allow_html=True)
        except Exception as e: st.error(f"⚠️ {e}")

    with TM["🖨️ الديباجة"]:
        try:
            st.markdown('<div class="section-title">🖨️ الديباجة</div>', unsafe_allow_html=True)
            br = st.text_input("براند:", APP_NAME)
            st.markdown(f"""<div style="border:3px dashed #1b5e20; padding:30px; border-radius:15px;
            background:linear-gradient(135deg,#f1f8e9,#e8f5e9); direction:rtl; text-align:center;">
            <h2 style="color:#1b5e20;">🌟 {br} 🌟</h2>
            <h3 style="color:#c62828;">{SUPERVISOR}</h3>
            <p style="color:#1b5e20; font-weight:bold;">🎯 {st.session_state['active_stage']}</p>
            <small style="color:#c62828;">🤲 {DUA_SHORT}</small></div>""", unsafe_allow_html=True)
        except Exception as e: st.error(f"⚠️ {e}")

    with TM["📈 التحليلات"]:
        try:
            st.markdown('<div class="section-title">📈 التحليلات</div>', unsafe_allow_html=True)
            c = st.columns(4)
            c[0].metric("خلطات", "1,247"); c[1].metric("متوسط تكلفة", "$285")
            c[2].metric("توفير", "18%"); c[3].metric("رضا", "96%")
            if PLOTLY:
                df = pd.DataFrame({'مادة': ['ذرة','صويا','نخالة','زيوت','أملاح','أخرى'], 'نسبة': [42, 23, 14, 8, 8, 5]})
                st.plotly_chart(px.pie(df, values='نسبة', names='مادة', color_discrete_sequence=px.colors.sequential.Greens), use_container_width=True)
        except Exception as e: st.error(f"⚠️ {e}")

    with TM["💬 التعليقات"]:
        try:
            st.markdown('<div class="section-title">💬 التعليقات</div>', unsafe_allow_html=True)
            st.text_area("حالية:", value=st.session_state["shared_comments"], height=200, disabled=True)
            nc = st.text_area("جديد:")
            if st.button("➕ نشر") and nc:
                st.session_state["shared_comments"] += f"\n• [{datetime.now():%Y-%m-%d %H:%M}]: {nc}"; st.rerun()
        except Exception as e: st.error(f"⚠️ {e}")

# ═══════ المراجع + المساعدة + الدليل ═══════
with TM["📚 المراجع"]:
    try:
        st.markdown('<div class="section-title">📚 المراجع</div>', unsafe_allow_html=True)
        st.markdown("""### المعتمدة:
        - NRC (2012) Swine | NRC (2007) Ruminants | NRC (2001) Dairy
        - NRC (2007) Horses | NRC (1994) Poultry | INRA (2018)
        - FAO (2010) Camel | Ross 308 (2020) Broiler
        ### 🏗️ الحظائر:
        - MWPS-1 / MWPS-3 / FAO 2012 / ASABE
        """)
    except Exception as e: st.error(f"⚠️ {e}")

with TM["💡 المساعدة"]:
    try:
        st.markdown(f"""<div class="section-title">💡 المساعدة</div>
        ### الأسئلة:
        - **DP أم CP؟** يعملان فعلياً
        - **الرسوم؟** 4 رسوم بعد التركيب
        - **الجدوى؟** تبويب مخصص + كتيّب PDF
        - **الختم؟** على كل صفحة PDF

        ### 📞 الدعم
        📧 {EMAIL} | 📱 {WHATSAPP}

        ### 🤲 {DUA_FULL}
        """, unsafe_allow_html=True)
    except Exception as e: st.error(f"⚠️ {e}")

with TM["📖 الدليل"]:
    try:
        st.markdown(f"""<div class="section-title">📖 الدليل</div>
        ### الميزات:
        - 🐄 8 قطاعات | 🌰 10 زيوت | 🧬 DP/CP يعملان
        - 📈 4 رسوم ملونة | 🏗️ حظائر 3D + GIF
        - 📊 جدوى فنية + كتيّب 5 صفحات
        - ✍️ ختم وتوقيع على كل صفحة PDF

        ### 🆕 في 10.3:
        - ✅ إصلاح auto_formulate_smart
        - ✅ الختم والتوقيع مُستعادان
        - ✅ 4 رسوم ملونة في UI
        - ✅ تبويب الجدوى + كتيّب كامل

        ### 📞 {EMAIL} | {WHATSAPP}
        """, unsafe_allow_html=True)
    except Exception as e: st.error(f"⚠️ {e}")

# ═══════ التذييل ═══════
st.markdown(f'<div class="sig">🌾 {APP_NAME} | {SUPERVISOR} © 2026</div>', unsafe_allow_html=True)
st.markdown(f'<div class="dua-footer">🤲 {DUA_SHORT} 🤲</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
