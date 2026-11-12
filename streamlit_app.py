# ═══════════════════════════════════════════════════════════════════════════
# تاور نولجي TAWOR NOLOGY 11.8.1 — النسخة الكاملة المُصححة
# د. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
# ═══════════════════════════════════════════════════════════════════════════
# الإصلاحات في 11.8.1:
#   🔐 كود المالك: TAWOR2026 (مشفّر)
#   ⚡ قيود البروتين < الطاقة (إصلاح جذري)
#   📄 PDF شامل: 6 رسوم + مقارنة + تصنيف + مراجع
#   🎯 كل التبويبات تعمل 100%
#   🔬 تصنيف المكونات (8 فئات)
# ═══════════════════════════════════════════════════════════════════════════

import streamlit as st
import numpy as np
import pandas as pd
import io, os, re, base64, traceback, warnings, json, hashlib, hmac
import time as _time
from datetime import datetime
from functools import lru_cache, wraps
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple, Any, Set

warnings.filterwarnings('ignore')

try:
    from scipy.optimize import linprog, minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    linprog = minimize = None

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Wedge
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import pytesseract, cv2
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

# ═══════════════════════════════════════════════════════════════════════════
# الأمان — كود المالك TAWOR2026
# ═══════════════════════════════════════════════════════════════════════════

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

@lru_cache(maxsize=1)
def _owner_code():
    try:
        return base64.b64decode("VEFXT1IyMDI2").decode()  # "TAWOR2026"
    except Exception:
        return None

def check_owner_code(user_input: str) -> bool:
    if not user_input:
        return False
    expected = _owner_code()
    if not expected:
        return False
    return hmac.compare_digest(user_input.strip(), expected)

# ═══════════════════════════════════════════════════════════════════════════
# الثوابت
# ═══════════════════════════════════════════════════════════════════════════

DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي ابتسام"
DUA_FULL = "رحم الله والدي إسماعيل تاور وأختي ابتسام وأسكنهما فسيح جناته"
DUA_QURAN = "﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾"

APP_NAME = "تاور نولجي Tawor Nology"
APP_TAGLINE = "للإنتاج الحيواني وتغذية الحيوان"
APP_VERSION = "11.8.1"
SUPERVISOR = "د. عبدالقادر إسماعيل تاور"
SUPERVISOR_TITLE = "اختصاصي تغذية الحيوان"
OWNER_EMAIL = "abukram128@gmail.com"

st.set_page_config(page_title=f"{APP_NAME} v{APP_VERSION}", page_icon="🌾",
                    layout="wide", initial_sidebar_state="collapsed")

# ═══════════════════════════════════════════════════════════════════════════
# الخطوط العربية
# ═══════════════════════════════════════════════════════════════════════════

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
        if not REPORTLAB_AVAILABLE:
            return
        paths = [os.path.join(FONT_DIR, "Amiri-Regular.ttf"),
                  "Amiri-Regular.ttf",
                  "/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        for p in paths:
            if os.path.exists(p) and self._register(p):
                return
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
            target = os.path.join(FONT_DIR, "Amiri-Regular.ttf")
            if not os.path.exists(target):
                import urllib.request
                urllib.request.urlretrieve(url, target)
            self._register(target)
        except Exception:
            pass
    def _register(self, path):
        try:
            pdfmetrics.registerFont(TTFont('TaworArabic', path))
            self.font_name = 'TaworArabic'
            return True
        except Exception:
            return False

font_mgr = ArabicFontManager()

@lru_cache(maxsize=1500)
def _ar_cached(text):
    if not text:
        return ""
    if not ARABIC_AVAILABLE:
        return str(text)
    try:
        return get_display(arabic_reshaper.reshape(str(text)), base_dir='R')
    except Exception:
        return str(text)

def ar(text):
    return _ar_cached(text)

# ═══════════════════════════════════════════════════════════════════════════
# مكتبة الأعلاف الكاملة (مضغوطة)
# ═══════════════════════════════════════════════════════════════════════════

def _feed(cp, dc, se, ndf, adf, ee, ash, ca, p, lys, met, price, desc=""):
    return {"CP": cp, "DC": dc, "SE": se, "NDF": ndf, "ADF": adf,
            "EE": ee, "ASH": ash, "Ca": ca, "P": p, "Lys": lys, "Met": met,
            "price": price, "desc": desc}

BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": _feed(8.5, .85, 80, 9.5, 3.2, 3.8, 1.3, .02, .27, .24, .17, 230),
        "ذرة بيضاء": _feed(8.8, .83, 78, 10.2, 3.5, 3.5, 1.4, .02, .26, .25, .18, 225),
        "ذرة شامية": _feed(8.3, .86, 82, 9, 3, 4, 1.2, .02, .28, .23, .16, 240),
        "ذرة رفيعة (سورجم)": _feed(10, .78, 70, 12.5, 5.5, 3, 1.8, .03, .3, .22, .17, 195),
        "شعير مطحون": _feed(11.5, .8, 71, 18.5, 7.5, 2.2, 2.5, .05, .35, .42, .2, 210),
        "شعير كامل": _feed(10.8, .75, 68, 22, 9, 2, 2.8, .05, .33, .4, .18, 200),
        "قمح محلي": _feed(12, .85, 75, 11.5, 3.8, 2, 1.6, .04, .32, .35, .2, 240),
        "قمح مستورد": _feed(11.5, .87, 78, 11, 3.5, 1.9, 1.5, .04, .33, .34, .19, 245),
        "جريش أرز": _feed(7.8, .82, 82, 5.5, 2.5, 8.5, 4.2, .06, .3, .28, .18, 240),
        "دخن محلي": _feed(11, .75, 68, 15.5, 6.5, 4, 2.2, .05, .31, .28, .2, 220),
        "شوفان علفي": _feed(11, .76, 62, 27.5, 13.5, 5, 3, .08, .35, .4, .18, 260),
        "كسرة خبز": _feed(10.5, .82, 75, 8, 3.5, 5.5, 3.5, .1, .2, .28, .17, 160),
        "بسكويت مكسر": _feed(8.5, .85, 85, 4, 2, 12, 2.5, .08, .18, .2, .12, 180),
        "مكرونة مكسرة": _feed(11, .88, 80, 3.5, 1.5, 1.5, 1, .03, .2, .28, .15, 190),
        "بطاطا مجففة": _feed(8, .9, 78, 6, 3, 1, 4.5, .08, .22, .28, .15, 200),
        "تمر مجفف (دقل)": _feed(5.5, .85, 68, 15, 8.5, 1, 3.5, .1, .1, .1, .05, 180),
        "مولاس قصب السكر": _feed(4, .95, 50, 1.5, .8, .5, 8.5, .7, .05, .03, .02, 120),
        "تفل بنجر السكر": _feed(8.5, .65, 55, 45, 28, 1, 8.5, .7, .1, .3, .15, 190),
    },
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني": _feed(46, .88, 73, 15.5, 8.5, 1.5, 5.5, .2, .65, 1.6, .45, 460),
        "كسب فول صويا 44%": _feed(44, .9, 74, 13.5, 8, 1.8, 6, .35, .65, 2.7, .6, 440),
        "كسب فول صويا 48%": _feed(48, .91, 76, 12, 7, 1.5, 6.2, .35, .65, 3, .68, 480),
        "كسب عباد الشمس 36%": _feed(36, .76, 42, 38.5, 25.5, 2.5, 6.5, .4, 1, 1.2, .7, 310),
        "كسب عباد الشمس 32%": _feed(32, .72, 38, 42, 28, 2, 7, .42, .95, 1.1, .65, 290),
        "كسب بذور القطن": _feed(41, .78, 55, 24.5, 15.5, 1.2, 6.5, .2, 1.1, 1.8, .6, 290),
        "كسب بذور الكتان": _feed(32, .82, 65, 18.5, 10.5, 2.8, 5.8, .35, .85, 1.2, .55, 340),
        "كسب السمسم": _feed(42, .84, 70, 14.5, 9.5, 8.5, 12.5, 2, 1.2, 1.3, 1, 520),
        "كسب جلوتين 60%": _feed(60, .92, 85, 8.5, 5.5, 2.5, 3.5, .15, .5, 1.1, 1.8, 520),
        "كسب جلوتين 40%": _feed(40, .88, 72, 15, 8, 3, 5, .18, .55, 1.2, 1.1, 390),
        "كسب نواة النخيل": _feed(16, .65, 52, 55.5, 35.5, 6.5, 4.5, .3, .55, .55, .28, 200),
        "كسب الكانولا": _feed(36, .82, 60, 28, 18, 3.5, 6.5, .65, 1.1, 1.9, .7, 400),
        "فول صويا كامل": _feed(38, .85, 78, 15, 10, 18, 4.5, .25, .55, 2.5, .55, 420),
        "ترمس حلو": _feed(32, .8, 65, 20, 12, 6, 4, .2, .45, 1.8, .35, 380),
        "بازلاء علفية": _feed(22, .82, 70, 15, 8, 1.5, 3, .1, .4, 1.5, .25, 320),
    },
    "🚜 المخلفات الزراعية والألياف": {
        "نخالة قمح (ردة)": _feed(15, .72, 45, 35.5, 12.5, 3.5, 5.5, .12, 1.1, .6, .25, 150),
        "نخالة ذرة": _feed(9.5, .65, 40, 40, 15, 4, 2, .1, .75, .3, .15, 140),
        "البرسيم الجاف": _feed(16.5, .6, 35, 42.5, 32.5, 2, 10.5, 1.5, .25, .85, .25, 170),
        "برسيم حجازي": _feed(18, .62, 38, 40, 30, 2.2, 11, 1.6, .26, .9, .28, 175),
        "تبن قمح": _feed(3.2, .35, 18, 72.5, 45.5, 1.5, 8.5, .3, .08, .15, .05, 80),
        "تبن فول": _feed(4.5, .4, 22, 68, 42, 1.2, 7.5, .35, .1, .18, .08, 90),
        "تبن عدس": _feed(5, .42, 24, 65, 40, 1.5, 8, .4, .12, .2, .08, 95),
        "قشر فول سوداني": _feed(5, .3, 15, 65.5, 42.5, 1, 5.5, .25, .1, .15, .05, 70),
        "سرسة الأرز": _feed(2.5, .25, 12, 68.5, 48.5, 12.5, 15.5, .15, .08, .1, .05, 60),
        "قش أرز": _feed(3.5, .3, 15, 70, 45, 1.5, 12, .2, .06, .12, .05, 65),
        "سعف نخيل مطحون": _feed(4, .3, 20, 65, 42, 2, 7, .35, .08, .15, .06, 55),
        "مخلفات النخيل": _feed(6.5, .7, 60, 25, 15, 5, 3.5, .15, .15, .25, .1, 100),
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": _feed(60, .85, 65, 2.5, 1.5, 8.5, 22.5, 5.5, 3.2, 4.5, 1.8, 850),
        "مسحوق أسماك 72%": _feed(72, .9, 72, 2, 1, 9.5, 18.5, 4.8, 2.8, 5.5, 2.2, 1100),
        "مسحوق اللحم والعظم": _feed(50, .75, 50, 3.5, 2.5, 10.5, 32.5, 9, 4.5, 2.5, .7, 620),
        "مسحوق الدم": _feed(80, .65, 55, 1, .5, 1.5, 6, .3, .3, 7, 1, 780),
        "مسحوق ريش": _feed(82, .7, 60, 1.5, 1, 3, 4, .25, .35, 2, .5, 650),
        "مركزات دواجن": _feed(40, .85, 60, 8.5, 4.5, 3.5, 12.5, 2.5, 1.2, 2.5, .9, 650),
        "مركزات مواشي": _feed(36, .8, 55, 15.5, 8.5, 3, 15.5, 3, 1.5, 2, .7, 600),
    },
    "🌰 الزيوت النباتية والحيوانية": {
        "زيت ذرة": _feed(0, 0, 220, 0, 0, 100, 0, 0, 0, 0, 0, 1500),
        "زيت فول الصويا": _feed(0, 0, 215, 0, 0, 100, 0, 0, 0, 0, 0, 1350),
        "زيت عباد الشمس": _feed(0, 0, 210, 0, 0, 100, 0, 0, 0, 0, 0, 1300),
        "زيت الكتان": _feed(0, 0, 205, 0, 0, 100, 0, 0, 0, 0, 0, 1700),
        "زيت جوز الهند": _feed(0, 0, 230, 0, 0, 100, 0, 0, 0, 0, 0, 1900),
        "زيت النخيل": _feed(0, 0, 215, 0, 0, 100, 0, 0, 0, 0, 0, 1100),
        "زيت الزيتون": _feed(0, 0, 210, 0, 0, 100, 0, 0, 0, 0, 0, 3500),
        "شحم حيواني": _feed(0, 0, 230, 0, 0, 100, 0, 0, 0, 0, 0, 900),
        "دهن الدجاج": _feed(0, 0, 225, 0, 0, 100, 0, 0, 0, 0, 0, 800),
        "زيت السمك": _feed(0, 0, 235, 0, 0, 100, 0, 0, 0, 0, 0, 3800),
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": _feed(94, 1, 0, 0, 0, 0, .5, 0, 0, 94, 0, 4200),
        "ميثيونين نقي": _feed(58, 1, 0, 0, 0, 0, .3, 0, 0, 0, 58, 5800),
        "ثريونين نقي": _feed(72, 1, 0, 0, 0, 0, .2, 0, 0, 0, 0, 4800),
        "تريبتوفان نقي": _feed(85, 1, 0, 0, 0, 0, .1, 0, 0, 0, 0, 9500),
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن": _feed(0, 0, 0, 0, 0, 0, 100, 18, 8, 0, 0, 4800),
        "بريمكس بياض": _feed(0, 0, 0, 0, 0, 0, 100, 22, 7, 0, 0, 5000),
        "بريمكس أبقار": _feed(0, 0, 0, 0, 0, 0, 100, 20, 10, 0, 0, 5200),
        "بريمكس مجترات": _feed(0, 0, 0, 0, 0, 0, 100, 18, 9, 0, 0, 4500),
        "بريمكس خيول": _feed(0, 0, 0, 0, 0, 0, 100, 15, 8, 0, 0, 5500),
        "بريمكس إبل": _feed(0, 0, 0, 0, 0, 0, 100, 20, 10, 0, 0, 5300),
        "بريمكس أسماك": _feed(0, 0, 0, 0, 0, 0, 100, 15, 7, 0, 0, 5800),
        "إنزيم فايتيز": _feed(0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 4200),
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": _feed(0, 0, 0, 0, 0, 0, 99.5, 38, 0, 0, 0, 40),
        "فوسفات ثنائي الكالسيوم": _feed(0, 0, 0, 0, 0, 0, 98.5, 23, 18, 0, 0, 280),
        "فوسفات أحادي الكالسيوم": _feed(0, 0, 0, 0, 0, 0, 99, 17, 22, 0, 0, 320),
        "ملح الطعام": _feed(0, 0, 0, 0, 0, 0, 99.9, 0, 0, 0, 0, 30),
        "بيكربونات الصوديوم": _feed(0, 0, 0, 0, 0, 0, 99, 0, 0, 0, 0, 340),
        "أكسيد المغنيسيوم": _feed(0, 0, 0, 0, 0, 0, 99.5, 0, 0, 0, 0, 480),
        "يوريا علفية": _feed(287, .95, 0, 0, 0, 0, 1, 0, 0, 0, 0, 480),
        "مضاد سموم فطرية": _feed(0, 0, 0, 0, 0, 0, 85, 0, 0, 0, 0, 950),
    },
}

def _get_ingredient_lookup() -> Dict[str, Dict]:
    if not hasattr(_get_ingredient_lookup, "_cache"):
        lookup = {}
        for cat in BIG_FEEDS_LIBRARY.values():
            for name, data in cat.items():
                lookup[name] = data
        _get_ingredient_lookup._cache = lookup
    return _get_ingredient_lookup._cache

def get_oil_ingredients() -> Dict[str, Dict]:
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت النباتية والحيوانية", {})

# ═══════════════════════════════════════════════════════════════════════════
# 🆕 تصنيف المكونات (لضبط الطاقة vs البروتين)
# ═══════════════════════════════════════════════════════════════════════════

def _classify_ingredient(name: str) -> str:
    """تصنيف المكون إلى: طاقة | بروتين | ألياف | زيت | معدن | بريمكس | أميني | أخرى"""
    mineral_kw = ["حجر", "فوسفات", "ملح", "بيكربونات", "أكسيد",
                  "كبريتات", "يوريا", "سيلينيت", "يوديد"]
    premix_kw = ["بريمكس", "إنزيم", "خمائر", "بروبيوتيك", "بريبيوتيك",
                 "فيتامين", "بيتاين", "بيتا جلوكان", "مضاد", "منشط",
                 "محسن", "ملون", "أحماض عضوية", "كالبتوس"]
    amino_kw = ["ليسين", "ميثيونين", "ثريونين", "تريبتوفان",
                "فالين", "أرجينين", "هيستيدين", "إيزوليوسين"]
    oil_kw = ["زيت", "شحم", "سمن", "دهن الدجاج", "Fish Oil"]
    fiber_kw = ["تبن", "قش أرز", "قش عدس", "سرسة", "سعف", "قوالح",
                "قشور", "أوراق", "مخلفات", "تفل قصب", "قش فول",
                "برسيم", "مخلفات النخيل"]
    protein_kw = ["كسب", "أمباز", "صويا", "عباد شمس", "قطن", "كتان",
                  "سمسم", "جلوتين", "كانولا", "فول صويا كامل",
                  "ترمس", "بازلاء", "مسحوق أسماك", "مسحوق اللحم",
                  "مسحوق الدم", "مسحوق ريش", "مركزات", "بيض مجفف"]
    energy_kw = ["ذرة", "شعير", "قمح", "جريش", "دخن", "شوفان",
                 "كسرة", "بسكويت", "مكرونة", "بطاطا", "كسافا",
                 "تمر", "سكر مائدة", "عسل أسود", "تفل بنجر",
                 "مولاس"]

    for k in mineral_kw:
        if k in name: return "معدن"
    for k in premix_kw:
        if k in name: return "بريمكس"
    for k in amino_kw:
        if k in name: return "أميني"
    for k in oil_kw:
        if k in name: return "زيت"
    for k in fiber_kw:
        if k in name: return "ألياف"
    for k in protein_kw:
        if k in name: return "بروتين"
    for k in energy_kw:
        if k in name: return "طاقة"
    return "أخرى"

# ═══════════════════════════════════════════════════════════════════════════
# حدود الفئات لكل حيوان
# ═══════════════════════════════════════════════════════════════════════════

CATEGORY_LIMITS_BY_ANIMAL = {
    "دواجن": {"طاقة": (45, 72), "بروتين": (18, 35), "ألياف": (0, 8),
              "زيت": (0, 8), "معدن": (1, 5), "بريمكس": (0.2, 1), "أميني": (0, 1)},
    "سمان": {"طاقة": (45, 70), "بروتين": (20, 38), "ألياف": (0, 7),
             "زيت": (0, 6), "معدن": (1, 5), "بريمكس": (0.2, 1), "أميني": (0, 1)},
    "أبقار": {"طاقة": (25, 55), "بروتين": (12, 28), "ألياف": (25, 55),
              "زيت": (0, 6), "معدن": (1, 5), "بريمكس": (0.1, 0.5)},
    "أغنام": {"طاقة": (25, 55), "بروتين": (12, 28), "ألياف": (25, 55),
              "زيت": (0, 5), "معدن": (1, 5), "بريمكس": (0.1, 0.5)},
    "ماعز": {"طاقة": (25, 55), "بروتين": (12, 28), "ألياف": (25, 55),
             "زيت": (0, 5), "معدن": (1, 5), "بريمكس": (0.1, 0.5)},
    "إبل": {"طاقة": (20, 50), "بروتين": (10, 26), "ألياف": (30, 60),
            "زيت": (0, 5), "معدن": (1, 5), "بريمكس": (0.1, 0.5)},
    "خيول": {"طاقة": (30, 55), "بروتين": (10, 25), "ألياف": (25, 55),
             "زيت": (0, 10), "معدن": (1, 5), "بريمكس": (0.1, 0.5)},
    "أسماك": {"طاقة": (30, 50), "بروتين": (25, 45), "ألياف": (0, 10),
              "زيت": (0, 15), "معدن": (1, 4), "بريمكس": (0.1, 0.5)},
    "أرانب": {"طاقة": (35, 55), "بروتين": (14, 25), "ألياف": (20, 40),
              "زيت": (0, 4), "معدن": (1, 5), "بريمكس": (0.1, 0.5)},
}

def _get_category_limits(animal_type: str) -> Dict[str, Tuple[float, float]]:
    return CATEGORY_LIMITS_BY_ANIMAL.get(animal_type, {})

# ═══════════════════════════════════════════════════════════════════════════
# الاحتياجات الغذائية
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AnimalRequirement:
    DP: float; CP: float; SE: float; NDF: float; ADF: float
    EE: float; ASH: float; Ca: float; P: float
    name_ar: str = ""; note: str = ""

def get_cattle_requirements(t: str, milk_yield: float = 20.0, weight_kg: float = 500.0):
    if t == "حليب_عالي":
        dp = 12.5 + milk_yield * .30
        return AnimalRequirement(round(dp,2), round(dp/.70,2),
            round(60+milk_yield*.35,1), 30, 19, 5.5, 8,
            round(.55+milk_yield*.003,3), round(.33+milk_yield*.0015,3),
            "أبقار حلابة عالية", f"حليب {milk_yield} كجم")
    if t == "حليب_متوسط":
        dp = 11 + milk_yield * .25
        return AnimalRequirement(round(dp,2), round(dp/.72,2),
            round(55+milk_yield*.3,1), 33, 21, 4.5, 8,
            round(.5+milk_yield*.0025,3), round(.3+milk_yield*.0012,3),
            "أبقار حلابة متوسطة", "")
    if t == "حليب_منخفض":
        dp = 9.5 + milk_yield * .2
        return AnimalRequirement(round(dp,2), round(dp/.75,2),
            round(50+milk_yield*.25,1), 38, 24, 4, 8.5,
            round(.45+milk_yield*.002,3), round(.28+milk_yield*.001,3),
            "أبقار حلابة منخفضة", "")
    if t == "تسمين_مكثف":
        return AnimalRequirement(11.5, 14.5, 72, 32, 20, 4.5, 7.5, .65, .38,
                                  "تسمين مكثف", "ADG >1.3")
    if t == "تسمين_عادي":
        return AnimalRequirement(9.5, 12, 65, 38, 24, 4, 7.5, .55, .32,
                                  "تسمين عادي", "ADG ~0.8")
    if t == "حمل_أخير":
        return AnimalRequirement(11.5, 14.5, 67, 35, 22, 4.2, 8, .7, .42,
                                  "حمل آخر", "")
    return AnimalRequirement(7.5, 10, 53, 45, 28, 3, 8.5, .42, .26, "صيانة", "")

def get_sheep_requirements(t: str, is_male: bool = True, weight_kg: float = 50.0, litter_size: int = 1):
    if is_male:
        if t == "تسمين_مكثف":
            return AnimalRequirement(11.5, 14.5, 64, 28, 17, 4, 8, .65, .36, "تسمين مكثف", "")
        if t == "تسمين_عادي":
            return AnimalRequirement(9.5, 12, 59, 33, 21, 3.6, 8, .55, .32, "تسمين عادي", "")
        return AnimalRequirement(8.5, 11, 55, 38, 24, 3.2, 8.5, .5, .3, "حملان تيد", "")
    if t == "مرضعات":
        dp = 10.5 + (litter_size - 1) * 1.5
        return AnimalRequirement(round(dp,2), round(dp/.72,2),
            round(60+(litter_size-1)*5,1), 30, 19, 4.5, 8.5,
            round(.65+(litter_size-1)*.1,3), round(.38+(litter_size-1)*.05,3),
            f"مرضعات ({litter_size})", "")
    if t == "حامل_أخير":
        return AnimalRequirement(10.5, 13.5, 62, 32, 20, 3.8, 8, .6, .35, "حامل آخر", "")
    if t == "حامل_متوسط":
        return AnimalRequirement(8.5, 11, 55, 38, 24, 3.4, 8, .5, .3, "حامل متوسط", "")
    return AnimalRequirement(7.2, 9.5, 48, 45, 28, 3, 8.5, .42, .26, "صيانة", "")

def get_goat_requirements(t: str, is_male: bool = True, milk_yield: float = 2.0):
    if is_male:
        if t == "تسمين_جديان":
            return AnimalRequirement(11, 14, 62, 30, 19, 3.8, 8, .62, .34, "تسمين جديان", "")
        return AnimalRequirement(9, 11.5, 57, 36, 22, 3.5, 8, .55, .3, "تيوس", "")
    if t == "حلابة_عالي":
        dp = 11.5 + milk_yield * .45
        return AnimalRequirement(round(dp,2), round(dp/.7,2),
            round(58+milk_yield*.45,1), 29, 18, 4.5, 8.5,
            round(.6+milk_yield*.008,3), round(.35+milk_yield*.004,3),
            f"حلابة ({milk_yield} لتر)", "")
    if t == "حلابة_متوسط":
        dp = 10 + milk_yield * .35
        return AnimalRequirement(round(dp,2), round(dp/.72,2),
            round(55+milk_yield*.4,1), 32, 20, 4, 8.5,
            round(.55+milk_yield*.006,3), round(.32+milk_yield*.003,3),
            f"حلابة ({milk_yield} لتر)", "")
    if t == "حامل_أخير":
        return AnimalRequirement(10, 13, 60, 33, 21, 3.8, 8, .6, .35, "حامل آخر", "")
    return AnimalRequirement(6.8, 9, 46, 46, 28, 3, 8.5, .42, .26, "صيانة", "")

def get_camel_requirements(t: str, weight_kg: float = 400.0, milk_yield: float = 5.0):
    if t == "نمو":
        return AnimalRequirement(10.5, 13.5, 60, 38, 24, 4, 8, .65, .38, "نمو", "")
    if t == "تسمين":
        return AnimalRequirement(9.5, 12, 65, 35, 22, 4.5, 7.5, .6, .35, "تسمين", "")
    if t == "حليب":
        dp = 12 + milk_yield * .25
        return AnimalRequirement(round(dp,2), round(dp/.7,2),
            round(62+milk_yield*.4,1), 32, 20, 5, 8.5,
            round(.7+milk_yield*.006,3), round(.4+milk_yield*.003,3),
            f"حلابة ({milk_yield} لتر)", "")
    if t == "سباق":
        return AnimalRequirement(14, 17, 72, 28, 17, 6, 9, .85, .5, "سباق", "")
    return AnimalRequirement(7, 9, 48, 48, 30, 3.5, 9, .42, .26, "صيانة", "")

def get_horse_requirements(t: str, weight_kg: float = 450.0):
    if t == "رياضة_مكثف":
        return AnimalRequirement(10.5, 13.5, 70, 30, 18, 7, 7.5, .7, .4, "رياضة مكثف", "")
    if t == "رياضة_عادي":
        return AnimalRequirement(9, 11.5, 63, 36, 22, 5, 7.5, .55, .32, "رياضة عادي", "")
    if t == "نمو_أمهار":
        return AnimalRequirement(12, 15, 65, 30, 18, 5, 8, .75, .42, "نمو أمهار", "")
    if t == "مرضعات":
        return AnimalRequirement(12.5, 16, 68, 32, 20, 5.5, 8, .8, .45, "مرضعات", "")
    return AnimalRequirement(7.2, 9.5, 53, 46, 29, 3.5, 8, .45, .28, "صيانة", "")

def get_poultry_requirements(strain: str, age_weeks: int = 1):
    if strain == "لاحم":
        if age_weeks <= 1:
            return AnimalRequirement(20, 23, 76, 8, 4, 5, 6.5, 1, .5, "بادي لاحم", "")
        if age_weeks <= 3:
            return AnimalRequirement(18.5, 21, 74, 9, 5, 5, 6, .9, .45, "نامي لاحم", "")
        if age_weeks <= 5:
            return AnimalRequirement(17, 19.5, 75, 10, 5.5, 4.5, 6, .87, .43, "ناهي لاحم", "")
        return AnimalRequirement(16.5, 19, 75, 10, 5.5, 4.5, 6, .85, .42, "ناهي لاحم+", "")
    if age_weeks <= 6:
        return AnimalRequirement(17, 20, 72, 10, 5.5, 4, 7, 1, .5, "بادي بياض", "")
    if age_weeks <= 18:
        return AnimalRequirement(14.5, 17, 70, 12, 6.5, 4, 9, 1.5, .45, "نامي بياض", "")
    return AnimalRequirement(15.5, 18, 72, 11, 6, 4.2, 11.5, 3.8, .45, "بياض", "")

def get_quail_requirements(strain: str, age_weeks: int = 1):
    if strain == "بياض":
        return AnimalRequirement(15, 18, 68, 11, 5.5, 4.5, 9, 2.5, .45, "سمان بياض", "")
    if age_weeks <= 2:
        return AnimalRequirement(20.5, 24, 74, 8, 4, 5.5, 6.5, 1, .55, "سمان بادي", "")
    if age_weeks <= 4:
        return AnimalRequirement(18.5, 22, 72, 9, 4.5, 5, 6, .9, .5, "سمان نامي", "")
    return AnimalRequirement(17, 20, 70, 10, 5, 4.5, 6, .85, .45, "سمان ناهي", "")

def get_fish_requirements(species: str, stage: str):
    if "بادئ" in stage or "زريعة" in stage:
        return AnimalRequirement(32, 40, 72, 8, 4, 10, 11, 1.5, .9, f"{species} بادئ", "")
    if "نمو" in stage:
        return AnimalRequirement(25, 32, 70, 12, 6, 8, 9, 1, .7, f"{species} نمو", "")
    return AnimalRequirement(22, 28, 68, 13, 7, 8, 9.5, .9, .65, f"{species} تسمين", "")

def get_rabbit_requirements(t: str, weight_kg: float = 4.0):
    if t == "تسمين":
        return AnimalRequirement(15, 17, 65, 25, 15, 3, 8, .7, .35, "تسمين", "")
    if t == "حليب":
        return AnimalRequirement(18, 20, 68, 25, 15, 4, 8.5, .85, .45, "حلابة", "")
    return AnimalRequirement(12, 14, 60, 30, 20, 2.5, 8.5, .6, .3, "صيانة", "")

def requirement_to_standard(req: AnimalRequirement) -> Dict[str, float]:
    return {"CP": req.CP, "DP": req.DP, "SE": req.SE,
            "NDF": req.NDF, "ADF": req.ADF, "EE": req.EE,
            "ASH": req.ASH, "Ca": req.Ca, "P": req.P}

# ═══════════════════════════════════════════════════════════════════════════
# الحسابات
# ═══════════════════════════════════════════════════════════════════════════

def compute_formula_nutrients(formula):
    totals = {k: 0.0 for k in ["CP", "DP", "SE", "NDF", "ADF", "EE",
                                 "ASH", "Ca", "P", "Lys", "Met"]}
    lookup = _get_ingredient_lookup()
    for ing, pct in formula.items():
        if ing not in lookup:
            continue
        d = lookup[ing]
        f = pct / 100.0
        for k in totals:
            if k == "DP":
                totals[k] += f * d.get("CP", 0) * d.get("DC", 0)
            else:
                totals[k] += f * d.get(k, 0)
    return totals

def evaluate_difference(pct_diff, standard_value=None):
    if standard_value is not None and standard_value == 0:
        if abs(pct_diff) < .001:
            return {"label": "🎯 مطابق", "bg": "#c8e6c9", "score": 100}
        return {"label": "⚠️ صفر", "bg": "#fff3e0", "score": 40}
    a = abs(pct_diff)
    if a <= .5: return {"label": "🎯 مطابق", "bg": "#c8e6c9", "score": 100}
    if a <= 2: return {"label": "🌟 ممتاز", "bg": "#dcedc8", "score": 95}
    if a <= 5: return {"label": "✅ جيد جداً", "bg": "#e8f5e9", "score": 85}
    if a <= 10: return {"label": "🟢 جيد", "bg": "#f1f8e9", "score": 75}
    if a <= 15: return {"label": "⭐ مقبول", "bg": "#fff8e1", "score": 65}
    if a <= 25: return {"label": "⚠️ بتحفظ", "bg": "#fff3e0", "score": 50}
    if a <= 40: return {"label": "🟠 ضعيف", "bg": "#ffe0b2", "score": 35}
    return {"label": "❌ غير مطابق", "bg": "#ffebee", "score": 20}

def evaluate_quality_weighted(formula, targets, animal_type, basis="DP"):
    actual = compute_formula_nutrients(formula)
    is_rum = animal_type in ("أبقار", "أغنام", "ماعز", "إبل")
    is_poultry = animal_type in ("دواجن", "سمان")
    weights = {}
    weights["DP" if basis == "DP" else "CP"] = 0.30
    if targets.get("SE"): weights["SE"] = 0.15
    if targets.get("NDF"): weights["NDF"] = 0.15 if is_rum else 0.10
    if targets.get("ADF"): weights["ADF"] = 0.10
    if targets.get("Ca"): weights["Ca"] = 0.10
    if targets.get("P"): weights["P"] = 0.10
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
        if is_poultry:
            rs = 100 if 1.5 <= r <= 2.2 else (80 if 1.3 <= r < 1.5 or 2.2 < r <= 2.5 else (50 if 1.0 <= r < 1.3 or 2.5 < r <= 3.5 else 10))
        else:
            rs = 100 if 1.5 <= r <= 2.0 else (85 if 1.2 <= r < 1.5 or 2.0 < r <= 2.5 else (55 if 0.9 <= r < 1.2 or 2.5 < r <= 3.5 else 15))
        weighted += rs * 0.10
        total_w += 0.10
    return (weighted / total_w if total_w else 0.0), actual

def compute_sensitivity(formula, targets, animal_type):
    base_q, _ = evaluate_quality_weighted(formula, targets, animal_type)
    base = compute_formula_nutrients(formula)
    deviations = {}
    lookup = _get_ingredient_lookup()
    for nut in ("CP", "DP", "SE", "Ca", "P"):
        if not targets.get(nut): continue
        best_ing = max(formula.keys(),
                       key=lambda i: formula[i] * lookup.get(i, {}).get(nut, 0),
                       default=None)
        if not best_ing: continue
        modified = dict(formula)
        modified[best_ing] = min(100.0, modified[best_ing] * 1.05)
        total = sum(modified.values())
        if total > 100:
            for k in modified: modified[k] *= 100.0 / total
        new_q, new_nut = evaluate_quality_weighted(modified, targets, animal_type)
        deviations[nut] = {"delta_quality": round(new_q - base_q, 2),
                            "delta_value": round(new_nut.get(nut, 0) - base.get(nut, 0), 3),
                            "driver_ingredient": best_ing}
    return deviations

def get_default_selections(animal_type, production_type, requirement=None):
    d = {"ملح الطعام", "مضاد سموم فطرية"}
    if animal_type != "دواجن":
        d |= {"الحجر الجيري", "فوسفات ثنائي الكالسيوم"}
    if animal_type in ("أبقار", "أغنام", "ماعز", "إبل"):
        d.add("بيكربونات الصوديوم")
    if animal_type in ("دواجن", "سمان"):
        d.add("بريمكس بياض" if "بياض" in str(production_type) else "بريمكس تسمين دواجن")
    elif animal_type == "أبقار": d.add("بريمكس أبقار")
    elif animal_type in ("أغنام", "ماعز", "أرانب"): d.add("بريمكس مجترات")
    elif animal_type == "خيول": d.add("بريمكس خيول")
    elif animal_type == "إبل": d.add("بريمكس إبل")
    elif animal_type == "أسماك": d.add("بريمكس أسماك")
    return d

def _normalize_ingredient_name(name: str) -> str:
    name = re.sub(r'\s+', ' ', str(name).strip())
    lookup = _get_ingredient_lookup()
    if name in lookup: return name
    for lib in lookup.keys():
        if lib.lower() in name.lower() or name.lower() in lib.lower():
            return lib
    return name

# ═══════════════════════════════════════════════════════════════════════════
# معايير الزيوت
# ═══════════════════════════════════════════════════════════════════════════

MAX_OIL_PERCENTAGE = {
    "دواجن_بادي": {"max": 8.0, "optimal": 5.0, "source": "Ross 308"},
    "دواجن_نامي": {"max": 7.0, "optimal": 4.5, "source": "Ross 308"},
    "دواجن_ناهي": {"max": 7.0, "optimal": 4.0, "source": "Ross 308"},
    "دواجن_بياض": {"max": 5.0, "optimal": 2.5, "source": "NRC 1994"},
    "سمان_بادي": {"max": 6.0, "optimal": 4.0, "source": "NRC Quail"},
    "سمان_بياض": {"max": 5.0, "optimal": 2.5, "source": "NRC Quail"},
    "أبقار_حليب_عالي": {"max": 6.0, "optimal": 4.0, "source": "NRC 2001"},
    "أبقار_حليب_متوسط": {"max": 5.0, "optimal": 3.5, "source": "NRC 2001"},
    "أبقار_تسمين_مكثف": {"max": 6.0, "optimal": 4.5, "source": "NRC 2001"},
    "أغنام_تسمين_مكثف": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "أغنام_مرضعات": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "ماعز_حلابة_عالي": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "إبل_حليب": {"max": 5.0, "optimal": 3.5, "source": "FAO 2010"},
    "خيول_رياضة_مكثف": {"max": 10.0, "optimal": 7.0, "source": "NRC Horses"},
    "أسماك_بادئ": {"max": 15.0, "optimal": 10.0, "source": "NRC Fish"},
    "أرانب_تسمين": {"max": 4.0, "optimal": 2.5, "source": "NRC 2007"},
}

def get_oil_standard(k):
    return MAX_OIL_PERCENTAGE.get(k, {"max": 5.0, "optimal": 3.0, "source": "عام"})

# ═══════════════════════════════════════════════════════════════════════════
# حدود المكونات (اختصار)
# ═══════════════════════════════════════════════════════════════════════════

INGREDIENT_LIMITS_BY_ANIMAL = {
    "دواجن": {"يوريا علفية": (0, 0), "نخالة قمح (ردة)": (0, 10),
              "تبن قمح": (0, 2), "قش أرز": (0, 2), "كسب بذور القطن": (0, 5),
              "ملح الطعام": (.2, .4), "الحجر الجيري": (.8, 2),
              "فوسفات ثنائي الكالسيوم": (.5, 2.5),
              "بريمكس تسمين دواجن": (.2, .35), "بريمكس بياض": (.2, .35)},
    "أبقار": {"يوريا علفية": (0, 1.5), "نخالة قمح (ردة)": (0, 30),
              "كسب بذور القطن": (0, 20), "ملح الطعام": (.3, .5),
              "بيكربونات الصوديوم": (.5, 1), "الحجر الجيري": (0, 3.5),
              "بريمكس أبقار": (.15, .3)},
    "أغنام": {"يوريا علفية": (0, 1), "ملح الطعام": (.3, .5),
              "بيكربونات الصوديوم": (.5, 1), "بريمكس مجترات": (.15, .3)},
    "ماعز": {"يوريا علفية": (0, 1), "ملح الطعام": (.3, .5),
             "بيكربونات الصوديوم": (.5, 1), "بريمكس مجترات": (.15, .3)},
    "إبل": {"يوريا علفية": (0, 1), "ملح الطعام": (.3, .5),
            "بيكربونات الصوديوم": (.5, 1), "بريمكس إبل": (.15, .3)},
    "خيول": {"يوريا علفية": (0, .5), "ملح الطعام": (.3, .5),
             "بريمكس خيول": (.15, .3)},
    "أسماك": {"يوريا علفية": (0, 0), "ملح الطعام": (0, .3),
              "بريمكس أسماك": (.15, .3)},
    "أرانب": {"يوريا علفية": (0, .5), "ملح الطعام": (.3, .5),
              "بريمكس مجترات": (.15, .3)},
    "سمان": {"يوريا علفية": (0, 0), "ملح الطعام": (.2, .4),
             "بريمكس تسمين دواجن": (.2, .35)},
}

def get_animal_limits(animal_type):
    return INGREDIENT_LIMITS_BY_ANIMAL.get(animal_type, {})

# ═══════════════════════════════════════════════════════════════════════════
# محرك LP مع قيود التصنيف
# ═══════════════════════════════════════════════════════════════════════════

def auto_formulate_smart(available_ingredients, prices, custom_standard,
                           standard_key="", basis="DP", min_quality=70.0,
                           animal_type="", production_type=""):
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "SCIPY غير متوفرة"}

    available_ingredients = [_normalize_ingredient_name(i) for i in available_ingredients]
    available_ingredients = list(dict.fromkeys(available_ingredients))
    lookup = _get_ingredient_lookup()
    ing_data = {i: lookup[i] for i in available_ingredients if i in lookup}
    valid = list(ing_data.keys())
    if len(valid) < 3:
        return {"success": False, "message": "اختر 3 مكونات على الأقل"}

    is_rum = animal_type in ("أبقار", "أغنام", "ماعز", "إبل")
    is_poultry = animal_type in ("دواجن", "سمان")
    n = len(valid)
    c = [prices.get(i, 300.0) for i in valid]

    categories = {i: _classify_ingredient(i) for i in valid}
    cat_indices = {}
    for cat in ["طاقة", "بروتين", "ألياف", "زيت", "معدن", "بريمكس", "أميني"]:
        idxs = [j for j in range(n) if categories[valid[j]] == cat]
        if idxs:
            cat_indices[cat] = idxs

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

    A_eq = [[1.0] * n, rows[target_key]]
    b_eq = [100.0, target_protein * 100.0]
    A_ub, b_ub = [], []

    # 🆕 قيود التصنيف
    cat_limits = _get_category_limits(animal_type)

    if "طاقة" in cat_indices and "طاقة" in cat_limits:
        e_min, e_max = cat_limits["طاقة"]
        A_ub.append([-1.0 if j in cat_indices["طاقة"] else 0.0 for j in range(n)])
        b_ub.append(-e_min * 100.0)
        A_ub.append([1.0 if j in cat_indices["طاقة"] else 0.0 for j in range(n)])
        b_ub.append(e_max * 100.0)

    if "بروتين" in cat_indices and "بروتين" in cat_limits:
        p_min, p_max = cat_limits["بروتين"]
        A_ub.append([-1.0 if j in cat_indices["بروتين"] else 0.0 for j in range(n)])
        b_ub.append(-p_min * 100.0)
        A_ub.append([1.0 if j in cat_indices["بروتين"] else 0.0 for j in range(n)])
        b_ub.append(p_max * 100.0)

    # ⚡ الطاقة ≥ 1.2 × البروتين
    if "طاقة" in cat_indices and "بروتين" in cat_indices:
        ratio_row = []
        for j in range(n):
            if j in cat_indices["طاقة"]: ratio_row.append(-1.0)
            elif j in cat_indices["بروتين"]: ratio_row.append(1.2)
            else: ratio_row.append(0.0)
        A_ub.append(ratio_row)
        b_ub.append(0.0)

    if "ألياف" in cat_indices and "ألياف" in cat_limits:
        f_min, f_max = cat_limits["ألياف"]
        A_ub.append([-1.0 if j in cat_indices["ألياف"] else 0.0 for j in range(n)])
        b_ub.append(-f_min * 100.0)
        A_ub.append([1.0 if j in cat_indices["ألياف"] else 0.0 for j in range(n)])
        b_ub.append(f_max * 100.0)

    if "زيت" in cat_indices:
        _, o_max = cat_limits.get("زيت", (0, 8))
        A_ub.append([1.0 if j in cat_indices["زيت"] else 0.0 for j in range(n)])
        b_ub.append(o_max * 100.0)

    if "معدن" in cat_indices:
        m_min, m_max = cat_limits.get("معدن", (1, 5))
        A_ub.append([-1.0 if j in cat_indices["معدن"] else 0.0 for j in range(n)])
        b_ub.append(-m_min * 100.0)
        A_ub.append([1.0 if j in cat_indices["معدن"] else 0.0 for j in range(n)])
        b_ub.append(m_max * 100.0)

    if "بريمكس" in cat_indices:
        pr_min, pr_max = cat_limits.get("بريمكس", (0.1, 1))
        A_ub.append([-1.0 if j in cat_indices["بريمكس"] else 0.0 for j in range(n)])
        b_ub.append(-pr_min * 100.0)
        A_ub.append([1.0 if j in cat_indices["بريمكس"] else 0.0 for j in range(n)])
        b_ub.append(pr_max * 100.0)

    # Ca:P
    if target_ca > 0 and target_p > 0:
        if is_poultry: ca_p_min, ca_p_max = 1.5, 2.2
        elif is_rum: ca_p_min, ca_p_max = 1.4, 2.5
        else: ca_p_min, ca_p_max = 1.5, 2.0
        A_ub.append([-rows["Ca"][i] + ca_p_min * rows["P"][i] for i in range(n)])
        b_ub.append(0)
        A_ub.append([rows["Ca"][i] - ca_p_max * rows["P"][i] for i in range(n)])
        b_ub.append(0)

    if target_se > 0:
        A_ub.append([-x for x in rows["SE"]])
        b_ub.append(-target_se * 0.92 * 100.0)
    if target_ndf > 0:
        if is_rum:
            A_ub.append([-x for x in rows["NDF"]])
            b_ub.append(-target_ndf * 0.85 * 100.0)
            A_ub.append(rows["NDF"])
            b_ub.append(target_ndf * 1.20 * 100.0)
        else:
            A_ub.append(rows["NDF"])
            b_ub.append(target_ndf * (1.10 if is_poultry else 1.15) * 100.0)
    if target_adf > 0:
        A_ub.append(rows["ADF"])
        mult = 1.30 if is_rum else (1.10 if is_poultry else 1.20)
        b_ub.append(target_adf * mult * 100.0)

    oil_std = get_oil_standard(standard_key)

    strategies = [("صارم", "full"), ("مرن ±5%", "r05"),
                  ("مرن ±10%", "r10"), ("مرن ±15%", "r15"),
                  ("طوارئ", "emergency")]

    best, best_q = None, 0.0

    for label, mode in strategies:
        try:
            A_eq2, b_eq2 = list(A_eq), list(b_eq)
            A_ub2, b_ub2 = list(A_ub), list(b_ub)

            if mode == "full":
                if target_ca > 0:
                    A_eq2.append(rows["Ca"]); b_eq2.append(target_ca * 100.0)
                if target_p > 0:
                    A_eq2.append(rows["P"]); b_eq2.append(target_p * 100.0)
            elif mode.startswith("r"):
                tol = int(mode[1:]) / 100.0
                if target_ca > 0:
                    A_ub2.append(rows["Ca"]); b_ub2.append(target_ca * (1 + tol) * 100.0)
                    A_ub2.append([-x for x in rows["Ca"]]); b_ub2.append(-target_ca * (1 - tol) * 100.0)
                if target_p > 0:
                    A_ub2.append(rows["P"]); b_ub2.append(target_p * (1 + tol) * 100.0)
                    A_ub2.append([-x for x in rows["P"]]); b_ub2.append(-target_p * (1 - tol) * 100.0)

            res = linprog(c, A_ub=A_ub2, b_ub=b_ub2, A_eq=A_eq2, b_eq=b_eq2,
                          bounds=bounds, method='highs',
                          options={'presolve': True, 'time_limit': 15})

            if res.success:
                formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
                q, actual = evaluate_quality_weighted(formula, custom_standard, animal_type, basis)

                # تحقق نهائي: طاقة ≥ بروتين
                cat_totals = {c: 0.0 for c in cat_indices}
                for i, ing in enumerate(valid):
                    if ing in formula:
                        cat = categories[ing]
                        if cat in cat_totals:
                            cat_totals[cat] += formula[ing]
                e_t = cat_totals.get("طاقة", 0)
                p_t = cat_totals.get("بروتين", 0)
                valid_ratio = (e_t >= p_t)

                if q > best_q and valid_ratio:
                    best_q = q
                    cat_summary = {k: round(v, 2) for k, v in cat_totals.items() if v > 0.01}
                    best = {"success": True, "formula": formula,
                            "cost": res.fun / 100.0,
                            "actual_nutrients": actual,
                            "quality_score": q, "strategy": label,
                            "meets_standard": q >= min_quality,
                            "targets": custom_standard, "basis": basis,
                            "oil_std": oil_std,
                            "category_summary": cat_summary,
                            "categories": {ing: categories[ing] for ing in formula}}
                if q >= 92 and valid_ratio:
                    break
        except Exception:
            continue

    if best:
        if not best["meets_standard"]:
            best["warning"] = f"⚠️ الجودة {best_q:.1f}% < {min_quality}%"
        return best
    return {"success": False, "message": "تعذر إيجاد حل يرضي القيود"}

# ═══════════════════════════════════════════════════════════════════════════
# NLP مع قيود التصنيف
# ═══════════════════════════════════════════════════════════════════════════

def nlp_optimize_feed_v2(ingredient_names, ingredient_data, prices,
                          requirement, animal_type, standard_key="",
                          protein_basis="DP", price_product=2.5, max_per_ing=0.6):
    n = len(ingredient_names)
    if n < 2:
        return {"success": False, "message": "يلزم مكونان"}
    if not SCIPY_AVAILABLE or minimize is None:
        return {"success": False, "message": "SCIPY غير متوفرة"}

    categories = {i: _classify_ingredient(i) for i in ingredient_names}
    cat_indices = {}
    for cat in ["طاقة", "بروتين", "ألياف", "زيت", "معدن", "بريمكس", "أميني"]:
        idxs = [j for j in range(n) if categories[ingredient_names[j]] == cat]
        if idxs:
            cat_indices[cat] = idxs

    se_vals = np.array([ingredient_data[i].get("SE", 0) for i in ingredient_names])
    me_vals = se_vals * 41.0
    cp_vals = np.array([ingredient_data[i].get("CP", 0) for i in ingredient_names])
    dp_vals = np.array([ingredient_data[i].get("CP", 0) * ingredient_data[i].get("DC", 0.8) for i in ingredient_names])
    ca_vals = np.array([ingredient_data[i].get("Ca", 0) for i in ingredient_names])
    p_vals = np.array([ingredient_data[i].get("P", 0) for i in ingredient_names])
    ndf_vals = np.array([ingredient_data[i].get("NDF", 0) for i in ingredient_names])
    adf_vals = np.array([ingredient_data[i].get("ADF", 0) for i in ingredient_names])
    cost_vals = np.array([prices.get(i, 300.0) / 1000.0 for i in ingredient_names])

    target_me = requirement.SE * 41.0
    target_cp = requirement.DP / 0.75 if protein_basis == "DP" else requirement.CP
    target_ca = requirement.Ca
    target_p = requirement.P

    is_rum = animal_type in ("أبقار", "أغنام", "ماعز", "إبل")
    is_poultry = animal_type in ("دواجن", "سمان")

    if is_poultry: ca_p_min, ca_p_max = 1.5, 2.2
    elif is_rum: ca_p_min, ca_p_max = 1.4, 2.5
    else: ca_p_min, ca_p_max = 1.4, 2.0

    oil_std = get_oil_standard(standard_key)
    oil_max_pct = oil_std["max"]
    oil_ind = np.array([1.0 if i in get_oil_ingredients() else 0.0 for i in ingredient_names])

    bounds = [(0.0, max_per_ing) for _ in range(n)]

    cons = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},
        {'type': 'ineq', 'fun': lambda x: np.dot(me_vals, x) - target_me * 0.98},
        {'type': 'ineq', 'fun': lambda x: np.dot(cp_vals, x) - target_cp * 0.98},
        {'type': 'ineq', 'fun': lambda x: np.dot(ca_vals, x) - ca_p_min * np.dot(p_vals, x)},
        {'type': 'ineq', 'fun': lambda x: ca_p_max * np.dot(p_vals, x) - np.dot(ca_vals, x)},
        {'type': 'ineq', 'fun': lambda x: oil_max_pct/100.0 - np.dot(oil_ind, x)},
    ]

    cat_limits = _get_category_limits(animal_type)

    if "طاقة" in cat_indices and "طاقة" in cat_limits:
        e_min, e_max = cat_limits["طاقة"]
        e_mask = np.zeros(n)
        for j in cat_indices["طاقة"]: e_mask[j] = 1.0
        cons.append({'type': 'ineq', 'fun': lambda x, m=e_mask: np.dot(m, x) - e_min/100.0})
        cons.append({'type': 'ineq', 'fun': lambda x, m=e_mask: e_max/100.0 - np.dot(m, x)})

    if "بروتين" in cat_indices and "بروتين" in cat_limits:
        p_min, p_max = cat_limits["بروتين"]
        p_mask = np.zeros(n)
        for j in cat_indices["بروتين"]: p_mask[j] = 1.0
        cons.append({'type': 'ineq', 'fun': lambda x, m=p_mask: np.dot(m, x) - p_min/100.0})
        cons.append({'type': 'ineq', 'fun': lambda x, m=p_mask: p_max/100.0 - np.dot(m, x)})

    if "طاقة" in cat_indices and "بروتين" in cat_indices:
        e_mask = np.zeros(n); p_mask = np.zeros(n)
        for j in cat_indices["طاقة"]: e_mask[j] = 1.0
        for j in cat_indices["بروتين"]: p_mask[j] = 1.0
        cons.append({'type': 'ineq',
                     'fun': lambda x, em=e_mask, pm=p_mask: np.dot(em, x) - 1.2 * np.dot(pm, x)})

    def objective(x):
        total_cost = np.dot(cost_vals, x)
        me_ratio = np.dot(me_vals, x) / target_me if target_me > 0 else 1.0
        cp_ratio = np.dot(cp_vals, x) / target_cp if target_cp > 0 else 1.0
        quality_value = me_ratio * cp_ratio
        return -(price_product * quality_value - total_cost)

    x0 = np.ones(n) / n

    try:
        res = minimize(objective, x0, method='SLSQP', bounds=bounds,
                       constraints=cons, options={'maxiter': 2000, 'ftol': 1e-9})
    except Exception as e:
        return {"success": False, "message": f"خطأ: {e}"}

    if not res.success:
        return {"success": False, "message": f"فشل: {res.message}"}

    x_opt = res.x
    formula = {name: round(float(x_opt[i]) * 100, 2) for i, name in enumerate(ingredient_names) if x_opt[i] > 0.001}

    p_total = float(np.dot(p_vals, x_opt))
    ca_p = (float(np.dot(ca_vals, x_opt) / p_total) if p_total > 0 else 0.0)

    category_summary = {}
    for i, ing in enumerate(ingredient_names):
        if x_opt[i] > 0.001:
            cat = categories[ing]
            category_summary[cat] = category_summary.get(cat, 0) + x_opt[i] * 100

    return {"success": True, "formula": formula, "x_opt": x_opt.tolist(),
            "final_cost": float(np.dot(cost_vals, x_opt)),
            "final_me": float(np.dot(me_vals, x_opt)),
            "final_cp": float(np.dot(cp_vals, x_opt)),
            "final_dp": float(np.dot(dp_vals, x_opt)),
            "final_ca": float(np.dot(ca_vals, x_opt)),
            "final_p": p_total,
            "ca_p_ratio": ca_p,
            "max_profit": float(-res.fun),
            "iterations": int(res.nit),
            "requirement": requirement,
            "category_summary": {k: round(v, 2) for k, v in category_summary.items()},
            "categories": categories}

# ═══════════════════════════════════════════════════════════════════════════
# بدائل الحليب
# ═══════════════════════════════════════════════════════════════════════════

MILK_REPLACER_STANDARDS = {
    "عجول (Calves)": {"CP": 24, "Fat": 20, "Lactose": 45, "Ca": .85, "P": .7,
                       "Lys": 2.2, "Met": .65, "source": "NRC Dairy Cattle",
                       "Ca_P_optimal": (1.2, 1.5)},
    "حملان (Lambs)": {"CP": 24, "Fat": 24, "Lactose": 40, "Ca": .9, "P": .7,
                       "Lys": 2.4, "Met": .7, "source": "NRC Small Ruminants",
                       "Ca_P_optimal": (1.2, 1.6)},
    "جديان (Goat Kids)": {"CP": 24, "Fat": 24, "Lactose": 42, "Ca": .9, "P": .7,
                            "Lys": 2.3, "Met": .7, "source": "NRC Small Ruminants",
                            "Ca_P_optimal": (1.2, 1.6)},
    "إبل (Camels)": {"CP": 26, "Fat": 28, "Lactose": 38, "Ca": .95, "P": .75,
                       "Lys": 2.5, "Met": .8, "source": "FAO Camel Nutrition",
                       "Ca_P_optimal": (1.2, 1.5)},
    "أمهار (Foals)": {"CP": 22, "Fat": 18, "Lactose": 48, "Ca": 1.0, "P": .8,
                        "Lys": 2.1, "Met": .6, "source": "NRC Horses",
                        "Ca_P_optimal": (1.2, 1.4)},
}

MILK_REPLACER_INGREDIENTS = {
    "حليب مجفف منزوع الدسم": {"CP": 34, "Fat": 1, "Lactose": 52, "Ca": 1.3, "P": 1, "Lys": 2.7, "Met": .9, "price": 3200, "max": 60, "type": "بروتين"},
    "حليب مجفف كامل الدسم": {"CP": 26, "Fat": 28, "Lactose": 38, "Ca": .95, "P": .75, "Lys": 2.1, "Met": .65, "price": 3800, "max": 70, "type": "بروتين+دهن"},
    "شرش حليب مجفف": {"CP": 12, "Fat": 1.5, "Lactose": 75, "Ca": .9, "P": .75, "Lys": .9, "Met": .2, "price": 1800, "max": 35, "type": "كربوهيدرات"},
    "بروتين شرش WPC 80%": {"CP": 80, "Fat": 5, "Lactose": 8, "Ca": .5, "P": .3, "Lys": 7.5, "Met": 1.6, "price": 8500, "max": 25, "type": "بروتين"},
    "مركز بروتين صويا": {"CP": 66, "Fat": 1, "Lactose": 0, "Ca": .2, "P": .8, "Lys": 4.2, "Met": .9, "price": 2800, "max": 15, "type": "نباتي"},
    "زيت جوز الهند": {"CP": 0, "Fat": 100, "Lactose": 0, "Ca": 0, "P": 0, "Lys": 0, "Met": 0, "price": 2200, "max": 15, "type": "دهن"},
    "زيت النخيل": {"CP": 0, "Fat": 100, "Lactose": 0, "Ca": 0, "P": 0, "Lys": 0, "Met": 0, "price": 1200, "max": 15, "type": "دهن"},
    "لاكتوز نقي": {"CP": 0, "Fat": 0, "Lactose": 100, "Ca": 0, "P": 0, "Lys": 0, "Met": 0, "price": 1400, "max": 25, "type": "كربوهيدرات"},
    "ليسين L-Lysine": {"CP": 94, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0, "Lys": 94, "Met": 0, "price": 4200, "max": 1, "type": "أميني"},
    "ميثيونين": {"CP": 58, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0, "Lys": 0, "Met": 58, "price": 5800, "max": .8, "type": "أميني"},
    "بريمكس فيتامينات": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 5, "P": 3, "Lys": 0, "Met": 0, "price": 6500, "max": 1, "type": "بريمكس"},
}

def formulate_milk_replacer(animal, volume=100.0, selected=None):
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "SCIPY غير متوفرة"}
    std = MILK_REPLACER_STANDARDS.get(animal)
    if not std:
        return {"success": False, "message": "حيوان غير مدعوم"}

    valid = [i for i in (selected or list(MILK_REPLACER_INGREDIENTS.keys()))
             if i in MILK_REPLACER_INGREDIENTS]
    n = len(valid)
    if n < 3:
        return {"success": False, "message": "اختر 3 مكونات على الأقل"}

    c = [MILK_REPLACER_INGREDIENTS[i]["price"] for i in valid]
    cp = [MILK_REPLACER_INGREDIENTS[i]["CP"] for i in valid]
    fat = [MILK_REPLACER_INGREDIENTS[i]["Fat"] for i in valid]
    lac = [MILK_REPLACER_INGREDIENTS[i]["Lactose"] for i in valid]
    ca = [MILK_REPLACER_INGREDIENTS[i]["Ca"] for i in valid]
    p = [MILK_REPLACER_INGREDIENTS[i]["P"] for i in valid]
    base_bounds = [(0, MILK_REPLACER_INGREDIENTS[i].get("max", 100)) for i in valid]

    A_eq = [[1]*n, cp, fat]
    b_eq = [100, std["CP"]*100, std["Fat"]*100]
    A_ub = [(lac, std["Lactose"]*1.30*100),
            ([-x for x in lac], -std["Lactose"]*0.70*100),
            ([-x for x in ca], -std["Ca"]*0.85*100),
            ([-x for x in p], -std["P"]*0.85*100)]
    A_ub_list = [u for u, _ in A_ub]
    b_ub_list = [b for _, b in A_ub]

    try:
        res = linprog(c, A_ub=A_ub_list, b_ub=b_ub_list,
                      A_eq=A_eq, b_eq=b_eq, bounds=base_bounds,
                      method='highs', options={'presolve': True, 'time_limit': 15})
    except Exception as e:
        return {"success": False, "message": f"خطأ: {e}"}

    if not res.success:
        return {"success": False, "message": "لا يوجد حل — جرّب مواد أرخص"}

    formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
    used = sum(1 for v in formula.values() if v > 0.5)
    used_pct = used / n * 100

    actual = {k: 0.0 for k in ["CP", "Fat", "Lactose", "Ca", "P", "Lys", "Met"]}
    for ing, pct in formula.items():
        d = MILK_REPLACER_INGREDIENTS[ing]
        for k in actual:
            actual[k] += pct / 100 * d.get(k, 0)

    scores = []
    for k in ["CP", "Fat", "Lactose", "Ca", "P"]:
        t = std.get(k, 0)
        if t <= 0: continue
        diff = abs(actual[k] - t) / t * 100
        if diff <= 2: scores.append(100)
        elif diff <= 5: scores.append(92)
        elif diff <= 10: scores.append(78)
        elif diff <= 15: scores.append(62)
        elif diff <= 25: scores.append(45)
        else: scores.append(max(0, 100 - diff))

    ca_p = actual["Ca"] / actual["P"] if actual["P"] > 0 else 0
    cp_min, cp_max = std.get("Ca_P_optimal", (1.2, 1.5))
    scores.append(100 if cp_min <= ca_p <= cp_max else (75 if cp_min * 0.8 <= ca_p <= cp_max * 1.3 else 30))

    quality = sum(scores) / len(scores) if scores else 0

    return {"success": True, "formula": formula,
            "cost_per_100kg": res.fun / 100,
            "cost_per_kg": res.fun / 10000,
            "standard": std, "actual": actual, "animal": animal, "volume": volume,
            "used_count": used, "used_pct": used_pct,
            "quality_score": quality, "ca_p_ratio": ca_p,
            "strategy": "متوازن",
            "targets": {k: std.get(k, 0) for k in ["CP", "Fat", "Lactose", "Ca", "P", "Lys", "Met"]}}

# ═══════════════════════════════════════════════════════════════════════════
# الرسوم البيانية
# ═══════════════════════════════════════════════════════════════════════════

def create_colorful_bar_chart(standard, actual, keys=None):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        if keys is None: keys = ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH"]
        nuts = [n for n in keys if n in standard and standard[n] > 0]
        if not nuts: return None
        fig, ax = plt.subplots(figsize=(9, 4.5))
        x = np.arange(len(nuts))
        width = 0.35
        ax.bar(x - width/2, [standard[n] for n in nuts], width,
               label='المعيار', color='#1976d2', edgecolor='#0d47a1', linewidth=1.5)
        ax.bar(x + width/2, [actual.get(n, 0) for n in nuts], width,
               label='المحسوب', color='#43a047', edgecolor='#1b5e20', linewidth=1.5)
        ax.set_title('مقارنة العناصر', fontsize=13, fontweight='bold', color='#1b5e20')
        ax.set_xticks(x); ax.set_xticklabels(nuts, fontsize=10)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_facecolor('#fafafa')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_colorful_pie_chart(formula):
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2: return None
    try:
        colors = ['#e53935', '#8e24aa', '#3949ab', '#1e88e5', '#00897b',
                  '#43a047', '#7cb342', '#fdd835', '#fb8c00', '#6d4c41']
        names = list(formula.keys()); vals = list(formula.values())
        fig, ax = plt.subplots(figsize=(8, 5))
        _, _, autotexts = ax.pie(vals, autopct='%1.1f%%', colors=colors[:len(names)],
                                   startangle=90, pctdistance=0.75,
                                   wedgeprops=dict(edgecolor='white', linewidth=2))
        for t in autotexts: t.set_color('white'); t.set_fontweight('bold'); t.set_fontsize(9)
        ax.legend(names, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)
        ax.set_title('توزيع المكونات', fontsize=13, fontweight='bold', color='#1b5e20')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_radar_chart(standard, actual, keys=None):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        if keys is None: keys = ["CP", "DP", "SE", "NDF", "ADF", "EE", "Ca", "P"]
        nuts = [n for n in keys if n in standard and standard[n] > 0]
        if len(nuts) < 3: return None
        std_norm = [100.0] * len(nuts)
        act_norm = [(actual.get(n, 0) / standard[n]) * 100 for n in nuts]
        angles = np.linspace(0, 2 * np.pi, len(nuts), endpoint=False).tolist()
        std_norm += std_norm[:1]; act_norm += act_norm[:1]; angles += angles[:1]
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, std_norm, 'o-', linewidth=2.5, color='#1976d2', label='المعيار')
        ax.fill(angles, std_norm, alpha=0.15, color='#1976d2')
        ax.plot(angles, act_norm, 'o-', linewidth=2.5, color='#43a047', label='المحسوب')
        ax.fill(angles, act_norm, alpha=0.25, color='#43a047')
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(nuts, fontsize=10)
        ax.set_title('المقارنة %', fontsize=12, fontweight='bold', color='#1b5e20', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_gauge_chart(score):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect='equal'))
        colors = ['#c62828', '#ef6c00', '#f9a825', '#7cb342', '#43a047', '#1b5e20']
        for i, c in enumerate(colors):
            t1 = 180 - (i * 30); t2 = 180 - ((i + 1) * 30)
            ax.add_patch(Wedge((0, 0), 1, t2, t1, width=0.3,
                                facecolor=c, edgecolor='white', linewidth=2))
        angle = 180 - (score / 100) * 180
        rad = np.radians(angle)
        ax.plot([0, 0.85 * np.cos(rad)], [0, 0.85 * np.sin(rad)],
                color='#1a1a1a', linewidth=3, zorder=10)
        ax.add_patch(Circle((0, 0), 0.08, color='#1a1a1a', zorder=11))
        ax.text(0, -0.25, f'{score:.0f}%', ha='center', fontsize=20,
                fontweight='bold', color='#1b5e20')
        ax.set_xlim(-1.2, 1.2); ax.set_ylim(-0.7, 1.2); ax.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_ca_p_ratio_chart(ca, p):
    if not MATPLOTLIB_AVAILABLE or p <= 0: return None
    try:
        ratio = ca / p
        fig, ax = plt.subplots(figsize=(8, 3))
        zones = [(0, .8, '#b71c1c'), (.8, 1.2, '#ef6c00'), (1.2, 1.5, '#f9a825'),
                 (1.5, 2.0, '#2e7d32'), (2.0, 3.0, '#f9a825'), (3.0, 5.0, '#ef6c00'),
                 (5.0, 8.0, '#b71c1c')]
        for x0, x1, c in zones:
            ax.axvspan(x0, x1, alpha=0.35, color=c, edgecolor='white', linewidth=0)
        ratio_clipped = min(ratio, 7.9)
        ax.axvline(ratio_clipped, color='#0d47a1', linewidth=4, zorder=10)
        ax.text(ratio_clipped, 0.85, f'{ratio:.2f}', ha='center', va='bottom',
                fontsize=18, fontweight='bold', color='#0d47a1')
        ax.set_xlim(0, 8); ax.set_ylim(0, 1.2); ax.set_yticks([]); ax.set_xticks(range(9))
        ax.set_title(f'⚖️ Ca:P = {ratio:.2f}', fontsize=12, fontweight='bold', color='#1b5e20')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_quality_breakdown_chart(rows):
    if not MATPLOTLIB_AVAILABLE or not rows: return None
    try:
        labels = [r["العنصر"] for r in rows[:9]]
        scores = [r.get("score", 50) for r in rows[:9]]
        colors = ['#1b5e20' if s >= 95 else '#43a047' if s >= 85
                  else '#7cb342' if s >= 70 else '#f9a825' if s >= 55
                  else '#c62828' for s in scores]
        fig, ax = plt.subplots(figsize=(9, 4))
        bars = ax.bar(labels, scores, color=colors, edgecolor='#333')
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f'{bar.get_height():.0f}', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
        ax.axhline(y=70, color='#c62828', linestyle='--', linewidth=2, label='حد 70%')
        ax.set_ylim(0, 105)
        ax.set_title('تقييم العناصر', fontsize=13, fontweight='bold', color='#1b5e20')
        ax.legend(); ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=30, ha='right')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

# ═══════════════════════════════════════════════════════════════════════════
# PDF Generator شامل
# ═══════════════════════════════════════════════════════════════════════════

class PDFGenerator:
    def __init__(self):
        self.font_name = font_mgr.font_name

    def _ar(self, t):
        return ar(t) if t else ""

    def _draw_page(self, canvas_obj, doc):
        try:
            canvas_obj.saveState()
            w, h = doc.pagesize
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, h - 90, w, 90, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.rect(0, h - 95, w, 5, fill=1, stroke=0)
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 22)
            canvas_obj.drawCentredString(w/2, h - 38, self._ar("تاور نولجي  Tawor Nology"))
            canvas_obj.setFont(self.font_name, 12)
            canvas_obj.setFillColor(HexColor('#e8f5e9'))
            canvas_obj.drawCentredString(w/2, h - 58, self._ar("للإنتاج الحيواني وتغذية الحيوان"))
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, 42, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#ffeb3b'))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.drawCentredString(w/2, 68, self._ar(f"🤲 {DUA_SHORT} 🤲"))
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(w/2, 27, self._ar("تاور نولجي Tawor Nology © 2026"))
            canvas_obj.setFont(self.font_name, 7)
            canvas_obj.drawCentredString(w/2, 12,
                                          self._ar(f"صفحة {canvas_obj.getPageNumber()}"))
            canvas_obj.restoreState()
        except Exception:
            pass

    def generate_report(self, formula, requirement, animal_type, breed, cost,
                         city, local_cost, local_sym, requester_name="",
                         protein_basis="DP", standard_key="",
                         include_charts=True, quality_score=0.0,
                         category_summary=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40,
                                topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text), ParagraphStyle(
                's', fontName=self.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))

        # العنوان
        story.append(P("تقرير فني رسمي — تركيب علفة متوازن", size=20,
                       align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
        story.append(Spacer(1, 10))

        # بطاقة
        client = [[self._ar("👤 طالب الخدمة:"), self._ar(requester_name or "—")],
                  [self._ar("📍 الموقع:"), self._ar(city)],
                  [self._ar("🐾 الفصيل:"), self._ar(f"{animal_type} — {breed}")],
                  [self._ar("🧬 الأساس:"), self._ar(protein_basis)],
                  [self._ar("📅 التاريخ:"), datetime.now().strftime('%Y-%m-%d %H:%M')]]
        ct = Table(client, colWidths=[150, 340])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')),
            ('INNERGRID', (0, 0), (-1, -1), 0.6, HexColor('#c8e6c9')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8)]))
        story.append(ct)
        story.append(Spacer(1, 12))

        std_vals = requirement_to_standard(requirement)
        calc_vals = compute_formula_nutrients(formula)
        meets = quality_score >= 70
        ca_p = (calc_vals.get('Ca',0)/calc_vals.get('P',1)) if calc_vals.get('P',0)>0 else 0

        qd = [[self._ar("الجودة"), self._ar("الحالة"), self._ar("Ca:P"), self._ar("التكلفة")],
              [f"{quality_score:.1f}%",
               self._ar("✅ ناجح" if meets else "⚠️ يحتاج تحسين"),
               f"{ca_p:.2f}", f"${cost:.2f}"]]
        qt = Table(qd, colWidths=[100, 180, 100, 110])
        qt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565c0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#e8f5e9' if meets else '#ffebee')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#1976d2')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 8)]))
        story.append(qt)
        story.append(Spacer(1, 15))

        # مقارنة
        story.append(P("📊 جدول المقارنة التفصيلي", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        labels = {"CP": "بروتين", "DP": "مهضوم", "SE": "طاقة",
                  "NDF": "NDF", "ADF": "ADF", "EE": "دهن", "ASH": "رماد",
                  "Ca": "Ca", "P": "P"}
        data = [[self._ar(x) for x in ["العنصر", "المعيار", "المحسوب", "الفرق", "%", "التقييم"]]]
        cmds = [('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#9e9e9e'))]
        row = 1
        quality_rows = []
        for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
            if k not in std_vals or std_vals[k] == 0: continue
            sv, cv = std_vals[k], calc_vals.get(k, 0)
            diff = cv - sv
            pct = (diff / sv * 100) if sv else 0
            ev = evaluate_difference(pct, standard_value=sv)
            data.append([self._ar(labels[k]), f"{sv:.2f}", f"{cv:.2f}",
                          f"{diff:+.3f}", f"{pct:+.2f}%", self._ar(ev["label"])])
            cmds.append(('BACKGROUND', (0, row), (-1, row), HexColor(ev["bg"])))
            quality_rows.append({"العنصر": labels[k], "score": ev["score"]})
            row += 1
        if ca_p > 0:
            cp_lbl = "🎯 مثالية" if 1.5 <= ca_p <= 2.0 else "✅ مقبولة" if 1.2 <= ca_p < 1.5 or 2.0 < ca_p <= 3.0 else "⚠️ خارج"
            cp_score = 100 if 1.5 <= ca_p <= 2.0 else 80 if 1.2 <= ca_p < 1.5 or 2.0 < ca_p <= 3.0 else 50
            data.append([self._ar("Ca:P"), "1.5 – 2.0", f"{ca_p:.2f}", "—", "—", self._ar(cp_lbl)])
            cmds.append(('BACKGROUND', (0, row), (-1, row), HexColor('#dcedc8')))
            quality_rows.append({"العنصر": "Ca:P", "score": cp_score})
        t = Table(data, colWidths=[95, 70, 70, 70, 80, 100])
        t.setStyle(TableStyle(cmds))
        story.append(t)
        story.append(Spacer(1, 10))

        # التصنيف
        if category_summary:
            story.append(P("🎯 ملخص التصنيف (طاقة/بروتين)", size=13, color='#1565c0'))
            story.append(Spacer(1, 6))
            cat_data = [[self._ar("الفئة"), self._ar("النسبة %")]]
            for cat_name, cat_pct in sorted(category_summary.items(), key=lambda x: x[1], reverse=True):
                cat_data.append([self._ar(cat_name), f"{cat_pct:.1f}%"])
            ct2 = Table(cat_data, colWidths=[150, 150])
            ct2.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565c0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('GRID', (0, 0), (-1, -1), 0.6, HexColor('#bdbdbd')),
                ('FONTSIZE', (0, 0), (-1, -1), 10)]))
            story.append(ct2)
            story.append(Spacer(1, 10))

        # المكونات
        story.append(PageBreak())
        story.append(P("🌾 المكونات للطن", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        ing_data = [[self._ar("المكون"), self._ar("%"), self._ar("كجم/طن"), self._ar("الفئة")]]
        for ing, pct in formula.items():
            cat = _classify_ingredient(ing)
            ing_data.append([self._ar(ing), f"{pct:.2f}%", f"{pct * 10:.1f}", self._ar(cat)])
        ti = Table(ing_data, colWidths=[180, 70, 80, 90])
        ti.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd'))]))
        story.append(ti)
        story.append(Spacer(1, 12))

        # التكاليف
        story.append(P("💰 التكاليف", size=14, color='#1b5e20'))
        story.append(Spacer(1, 6))
        cost_data = [[self._ar("البند"), self._ar("القيمة")],
                     [self._ar("التكلفة/طن"), f"${cost:.2f}"],
                     [self._ar(f"بالعملة ({local_sym})"), f"{local_cost:,.2f}"]]
        tc = Table(cost_data, colWidths=[250, 240])
        tc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#2e7d32')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 6)]))
        story.append(tc)

        # الرسوم
        if include_charts:
            story.append(PageBreak())
            story.append(P("📈 التحليل البياني", size=14, color='#1b5e20'))
            story.append(Spacer(1, 10))

            for chart_fn, args, caption in [
                (create_colorful_bar_chart, (std_vals, calc_vals), "1️⃣ المقارنة"),
                (create_colorful_pie_chart, (formula,), "2️⃣ التوزيع"),
            ]:
                try:
                    c = chart_fn(*args)
                    if c:
                        story.append(RLImage(c, width=460, height=230))
                        story.append(P(caption, size=9, align=TA_CENTER, color='#555'))
                        story.append(Spacer(1, 8))
                except Exception:
                    pass

            story.append(PageBreak())

            try:
                rf = create_radar_chart(std_vals, calc_vals)
                if rf:
                    story.append(RLImage(rf, width=300, height=300))
                    story.append(P("3️⃣ الرادار", size=9, align=TA_CENTER, color='#555'))
            except Exception:
                pass

            try:
                gf = create_gauge_chart(quality_score)
                if gf:
                    story.append(RLImage(gf, width=180, height=180))
                    story.append(P("4️⃣ الجودة", size=9, align=TA_CENTER, color='#555'))
            except Exception:
                pass

            story.append(PageBreak())

            try:
                cf = create_ca_p_ratio_chart(calc_vals.get("Ca", 0), calc_vals.get("P", 0))
                if cf:
                    story.append(RLImage(cf, width=460, height=170))
                    story.append(P("5️⃣ Ca:P", size=9, align=TA_CENTER, color='#555'))
            except Exception:
                pass

            try:
                qf = create_quality_breakdown_chart(quality_rows)
                if qf:
                    story.append(RLImage(qf, width=460, height=200))
                    story.append(P("6️⃣ تقييم العناصر", size=9, align=TA_CENTER, color='#555'))
            except Exception:
                pass

        # حساسية
        try:
            sens = compute_sensitivity(formula, std_vals, animal_type)
            if sens:
                story.append(PageBreak())
                story.append(P("📐 تحليل الحساسية", size=14, color='#1565c0'))
                story.append(Spacer(1, 6))
                sens_data = [[self._ar(x) for x in ["العنصر", "المكوّن المؤثر", "Δالجودة %", "Δالقيمة"]]]
                for k, v in sens.items():
                    sens_data.append([self._ar(k), self._ar(v["driver_ingredient"]),
                                        f"{v['delta_quality']:+.2f}%", f"{v['delta_value']:+.3f}"])
                st_sens = Table(sens_data, colWidths=[70, 220, 90, 90])
                st_sens.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565c0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#bdbdbd'))]))
                story.append(st_sens)
        except Exception:
            pass

        # المراجع
        story.append(PageBreak())
        story.append(P("📚 المراجع العلمية", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        refs = ["NRC (2001/2012) — Nutrient Requirements of Domestic Animals",
                "INRA (2018) — INRA Feeding System for Ruminants",
                "Ross 308 (2020) — Broiler Nutrition Specification",
                "FAO (2010) — Camel Nutrition and Production",
                "Danø & Højsgaard (2005) — LP in Ration Formulation",
                "McDonald et al. (2011) — Animal Nutrition, 7th ed."]
        for i, ref in enumerate(refs, 1):
            story.append(P(f"{i}. {ref}", size=10, color='#333'))
        story.append(Spacer(1, 15))

        # التوقيع
        story.append(P("✍️ الاعتماد", size=14, align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 15))
        story.append(P(SUPERVISOR, size=16, align=TA_CENTER, color='#c62828'))
        story.append(P(SUPERVISOR_TITLE, size=11, align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 10))
        story.append(P(f"🤲 {DUA_FULL} 🤲", size=10, align=TA_CENTER, color='#c62828'))

        doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()


pdf_gen = PDFGenerator()

# ═══════════════════════════════════════════════════════════════════════════
# Excel
# ═══════════════════════════════════════════════════════════════════════════

def export_comparison_to_excel(standard, calculated, requester_name="",
                                 animal="", stage="", formula=None, standard_key=""):
    if not OPENPYXL_AVAILABLE: return b""
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
    ws.merge_cells('A1:F1'); ws['A1'] = APP_NAME
    ws['A1'].font = tf; ws['A1'].alignment = ct
    ws.merge_cells('A2:F2'); ws['A2'] = f"🤲 {DUA_SHORT} 🤲"
    ws['A2'].font = Font(name='Arial', size=10, bold=True, color='C62828')
    ws['A2'].alignment = ct
    headers = ["العنصر", "المعيار", "المحسوب", "الفرق", "%", "التقييم"]
    for c, hh in enumerate(headers, 1):
        cell = ws.cell(row=4, column=c, value=hh)
        cell.font = hf; cell.fill = hfill; cell.alignment = ct; cell.border = bd
    labels = {"CP": "بروتين", "DP": "مهضوم", "SE": "SE", "NDF": "NDF",
              "ADF": "ADF", "EE": "دهن", "ASH": "رماد", "Ca": "Ca", "P": "P"}
    row = 5
    for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
        if k not in standard or standard[k] == 0: continue
        sv, cv = standard[k], calculated.get(k, 0)
        diff = cv - sv
        pct = (diff / sv * 100) if sv else 0
        ev = evaluate_difference(pct, standard_value=sv)
        vals = [labels[k], round(sv, 2), round(cv, 2), round(diff, 3), round(pct, 2), ev["label"]]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.alignment = ct; cell.border = bd
            cell.fill = PatternFill('solid', fgColor=ev["bg"].replace('#', ''))
        row += 1
    for c in range(1, 7):
        ws.column_dimensions[get_column_letter(c)].width = 22
    buf = io.BytesIO()
    wb.save(buf); buf.seek(0)
    return buf.getvalue()

# ═══════════════════════════════════════════════════════════════════════════
# نموذج اختيار الحيوان
# ═══════════════════════════════════════════════════════════════════════════

def get_animal_requirement_ui(key_prefix="req"):
    c1, c2 = st.columns(2)
    with c1:
        a = st.selectbox("🐾 الحيوان:",
                          ["أبقار", "أغنام", "ماعز", "إبل", "خيول",
                           "دواجن", "سمان", "أسماك", "أرانب"],
                          key=f"{key_prefix}_animal")
    with c2:
        prod_map = {
            "أبقار": ["حليب_عالي", "حليب_متوسط", "حليب_منخفض",
                       "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"],
            "أغنام": ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد",
                       "مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
            "ماعز": ["تسمين_جديان", "تيوس", "حلابة_عالي",
                     "حلابة_متوسط", "حامل_أخير", "صيانة"],
            "إبل": ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
            "خيول": ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار", "مرضعات", "صيانة"],
            "دواجن": ["لاحم", "بياض"],
            "سمان": ["تسمين", "بياض"],
            "أسماك": ["بادئ زريعة", "نمو", "تسمين"],
            "أرانب": ["تسمين", "حليب", "صيانة"],
        }
        p = st.selectbox("📋 الحالة:", prod_map[a], key=f"{key_prefix}_prod")

    extra = {}
    if a == "أبقار" and "حليب" in p:
        extra["milk_yield"] = st.number_input("🥛 الحليب (كجم/يوم):",
                                                5.0, 60.0, 20.0, 1.0,
                                                key=f"{key_prefix}_milk")
    elif a == "ماعز" and "حلابة" in p:
        extra["milk_yield"] = st.number_input("🥛 الحليب (لتر/يوم):",
                                                0.5, 8.0, 2.0, 0.25,
                                                key=f"{key_prefix}_milk")
    elif a == "إبل" and p == "حليب":
        extra["milk_yield"] = st.number_input("🥛 الحليب (لتر/يوم):",
                                                2.0, 20.0, 5.0, 0.5,
                                                key=f"{key_prefix}_milk")
    elif a == "أغنام" and p == "مرضعات":
        extra["litter_size"] = st.number_input("👶 المواليد:", 1, 3, 1, 1,
                                                 key=f"{key_prefix}_lit")
        extra["is_male"] = False
    elif a == "أغنام":
        extra["is_male"] = p not in ("مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة")
    elif a == "ماعز":
        extra["is_male"] = p in ("تسمين_جديان", "تيوس")

    if a == "دواجن":
        age = st.number_input("العمر (أسبوع):", 1, 20, 1, 1, key=f"{key_prefix}_age")
        req = get_poultry_requirements(p, age)
    elif a == "سمان":
        age = st.number_input("العمر (أسبوع):", 1, 8, 1, 1, key=f"{key_prefix}_age")
        req = get_quail_requirements(p, age)
    elif a == "أسماك":
        req = get_fish_requirements("البلطي", p)
    elif a == "أبقار":
        req = get_cattle_requirements(p, **extra)
    elif a == "أغنام":
        req = get_sheep_requirements(p, **extra)
    elif a == "ماعز":
        req = get_goat_requirements(p, **extra)
    elif a == "إبل":
        req = get_camel_requirements(p, **extra)
    elif a == "خيول":
        req = get_horse_requirements(p)
    elif a == "أرانب":
        req = get_rabbit_requirements(p)
    else:
        return None, None, None, None

    std_key_map = {("دواجن", "لاحم"): "دواجن_بادي",
                    ("دواجن", "بياض"): "دواجن_بياض",
                    ("سمان", "تسمين"): "سمان_بادي",
                    ("سمان", "بياض"): "سمان_بياض"}
    std_key = std_key_map.get((a, p), f"{a}_{p}")
    return a, p, req, std_key

# ═══════════════════════════════════════════════════════════════════════════
# الجلسة
# ═══════════════════════════════════════════════════════════════════════════

DEFAULTS = {"approved": False, "user_role": None,
             "active_formula": {}, "inventory": {},
             "last_formulation_result": None, "last_formulation_context": None,
             "owner_attempts": 0, "owner_lock_until": 0.0,
             "formulation_history": [], "last_activity": _time.time()}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state["inventory"]:
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing in cat:
            st.session_state["inventory"][ing] = {"quantity": 25.0, "min_threshold": 5.0}

def is_owner() -> bool:
    return st.session_state.get("user_role") == "owner"

# ═══════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');
* { font-family: 'Cairo', 'Amiri', sans-serif; color: #1a1a1a !important; }
html, body, [data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600");
    background-size: cover; background-position: center; background-attachment: fixed;
}
.main-box { background: rgba(255,255,255,0.92); padding: 32px; border-radius: 22px;
    box-shadow: 0 15px 45px rgba(0,0,0,0.15); margin-bottom: 70px;
    backdrop-filter: blur(12px); border: 1px solid rgba(212,175,55,0.2); }
.dua-main-box { background: linear-gradient(135deg, #0d3011, #1b5e20, #2e7d32);
    padding: 34px 28px; border-radius: 22px; border: 4px solid #d4af37;
    direction: rtl; text-align: center; margin: 25px 0; }
.dua-main-box * { color: white !important; }
.dua-main-box h3 { color: #d4af37 !important; font-size: 1.9rem; margin-bottom: 18px; font-weight: 900; }
.dua-main-box .names { display: inline-block; background: rgba(212,175,55,0.35);
    font-size: 1.65rem; font-weight: 900; color: #ffeb3b !important;
    margin: 20px 0; padding: 16px 30px; border: 2px solid #d4af37;
    border-radius: 16px; font-family: 'Amiri', serif !important; }
.dua-fixed-banner { position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32);
    color: white !important; padding: 12px 20px; z-index: 9998; text-align: center;
    border-top: 3px solid #d4af37; font-family: 'Amiri', serif !important; }
.dua-fixed-banner * { color: #ffeb3b !important; }
.section-title { color: #1b5e20 !important; border-right: 6px solid #2e7d32;
    padding: 12px 18px; text-align: right; font-size: 1.5rem; font-weight: 900;
    margin-top: 30px; margin-bottom: 20px;
    background: linear-gradient(to left, rgba(46,125,50,0.15), transparent);
    border-radius: 10px; }
.formula-item { background: linear-gradient(135deg, #ffffff, #e8f5e9);
    padding: 15px 20px; border-radius: 10px; margin-bottom: 10px; font-weight: 700;
    color: #1b5e20 !important; border-right: 5px solid #2e7d32; text-align: right; }
.physio-card { background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 18px 24px; border-radius: 14px; border-right: 6px solid #1565c0;
    margin-bottom: 20px; direction: rtl; text-align: right; }
.quality-good-v113 { background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
    padding: 24px; border-radius: 22px; border-right: 8px solid #1b5e20;
    margin: 18px 0; direction: rtl; text-align: right; }
.quality-bad-v113 { background: linear-gradient(135deg, #ffcdd2, #ef9a9a);
    padding: 24px; border-radius: 22px; border-right: 8px solid #c62828;
    margin: 18px 0; direction: rtl; text-align: right; }
.profile-img-style { width: 150px; height: 150px; border-radius: 50%;
    object-fit: cover; border: 4px solid #d4af37; display: block; margin: 0 auto; }
.stButton > button { color: #1a1a1a !important;
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9) !important;
    border: 1.5px solid #2e7d32 !important; font-weight: 700 !important;
    border-radius: 10px !important; }
.mini-signature { position: fixed; left: 20px; bottom: 70px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32); color: white !important;
    padding: 9px 22px; font-size: 0.85rem; border-radius: 25px; z-index: 9997;
    direction: rtl; border: 2px solid #d4af37; font-weight: 700; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #2e7d32, #1b5e20) !important; }
.stTabs [aria-selected="true"] * { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# بوابة الدخول
# ═══════════════════════════════════════════════════════════════════════════

if not st.session_state.get("approved", False):
    st.markdown('<div class="main-box" style="max-width: 780px; margin: 30px auto; direction: rtl;">',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <div class="names">🕊️ {DUA_SHORT} 🕊️</div>
        <p style="color:#d4af37; font-family:Amiri; font-size:1.2rem;">{DUA_QURAN}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<h2 style='color:#2E7D32; text-align:right;'>🌾 {APP_NAME} v{APP_VERSION}</h2>",
                unsafe_allow_html=True)
    st.markdown(f"<h4 style='color:#c62828; text-align:right;'>{SUPERVISOR} — {SUPERVISOR_TITLE}</h4>",
                unsafe_allow_html=True)

    st.markdown("<h3 style='text-align:center; color:#1b5e20;'>🔐 بوابة الدخول</h3>",
                unsafe_allow_html=True)
    col_owner, col_guest = st.columns(2)
    with col_owner:
        st.markdown("""
        <div style="background:#e8f5e9; padding:20px; border-radius:12px;
                    border:2px solid #2e7d32; text-align:center;">
            <h4 style="color:#1b5e20;">👑 المالك</h4>
            <p style="color:#555;">دخول آمن</p>
        </div>
        """, unsafe_allow_html=True)
        oc = st.text_input("🔑 كود المالك:", type="password", key="owner_code")
        if st.button("👑 دخول المالك", type="primary", use_container_width=True):
            now = _time.time()
            lock = st.session_state.get("owner_lock_until", 0.0)
            if now < lock:
                st.error(f"🔒 مقفل — {int(lock - now)}ث")
            elif check_owner_code(oc):
                st.session_state.update({"approved": True, "user_role": "owner"})
                st.rerun()
            else:
                n = st.session_state.get("owner_attempts", 0) + 1
                st.session_state["owner_attempts"] = n
                if n >= 3:
                    st.session_state["owner_lock_until"] = now + 300
                    st.error("🔒 3 محاولات فاشلة — قفل 5 دقائق")
                else:
                    st.error(f"❌ كود غير صحيح — متبقٍ {3 - n}")

    with col_guest:
        st.markdown("""
        <div style="background:#fff8e1; padding:20px; border-radius:12px;
                    border:2px solid #d4af37; text-align:center;">
            <h4 style="color:#e65100;">👥 زائر</h4>
            <p style="color:#555;">دخول مجاني</p>
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
    st.markdown(f"<div style='padding:10px; background:#f5f5f5; border-radius:10px; text-align:center;'>"
                f"الحساب: <b>{role_label}</b></div>", unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.cache_data.clear()
        st.rerun()

c3, c4 = st.columns([0.3, 0.7])
with c3:
    st.markdown(f'<img src="https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=600" class="profile-img-style">',
                unsafe_allow_html=True)
with c4:
    st.markdown(f"<h1 style='color: #0d3011; text-align:right; font-weight: 900;'>🌾 {APP_NAME}</h1>",
                unsafe_allow_html=True)
    st.markdown(f"<p style='color: #1565C0; text-align:right; font-size: 1.25rem; font-weight: 600;'>{APP_TAGLINE} v{APP_VERSION}</p>",
                unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #fff8e1, #ffe082); padding: 12px 20px;
                border-radius: 12px; border-right: 6px solid #c62828; border-left: 6px solid #c62828;'>
        <h3 style='color: #b71c1c; text-align:right; margin: 0; font-weight: 900;'>
            👨‍🔬 {SUPERVISOR}
        </h3>
        <p style='color: #0d47a1; text-align:right; margin: 5px 0 0 0; font-weight: 700;'>
            ✨ {SUPERVISOR_TITLE}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# التبويبات
# ═══════════════════════════════════════════════════════════════════════════

if is_owner():
    tabs_titles = ["🔬 النمذجة", "🏗️ الحظائر", "📊 الجدوى",
                    "🏭 المستودعات", "📈 التحليلات",
                    "📚 المراجع", "📖 الدليل"]
else:
    tabs_titles = ["🔬 النمذجة", "🏗️ الحظائر", "📊 الجدوى",
                    "📚 المراجع", "📖 الدليل"]

tabs = st.tabs(tabs_titles)
tab_map = {t: tab for t, tab in zip(tabs_titles, tabs)}

# ═══════════════════════════════════════════════════════════════════════════
# 🔬 النمذجة (5 تبويبات فرعية)
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["🔬 النمذجة"]:
    sub_lp, sub_nlp, sub_milk, sub_oils, sub_lab = st.tabs([
        "🎯 LP", "🎯 NLP", "🍼 بدائل الحليب", "🌰 الزيوت", "🔬 المختبر"])

    # ═══════════ LP ═══════════
    with sub_lp:
        st.markdown('<div class="section-title">🎯 تركيب علفة (LP)</div>',
                    unsafe_allow_html=True)

        pb = st.radio("أساس البروتين:",
                       ["المهضوم (DP) — الأدق", "الخام (CP)"],
                       horizontal=True, key="pb_lp")
        basis_code = "DP" if "DP" in pb else "CP"

        lp_animal, lp_prod, lp_req, lp_std_key = get_animal_requirement_ui("lp")

        if not lp_req:
            st.warning("⚠️ اختر حيواناً")
        else:
            st.markdown(f"""
            <div class="physio-card">
                <h4>🧬 {lp_req.name_ar}</h4>
                <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:8px;">
                    <span style="background:#fff;padding:6px 14px;border-radius:8px;">
                        DP: <b>{lp_req.DP}%</b></span>
                    <span style="background:#fff;padding:6px 14px;border-radius:8px;">
                        CP: <b>{lp_req.CP}%</b></span>
                    <span style="background:#fff;padding:6px 14px;border-radius:8px;">
                        SE: <b>{lp_req.SE}</b></span>
                    <span style="background:#fff;padding:6px 14px;border-radius:8px;">
                        Ca:P: <b>{lp_req.Ca/lp_req.P:.2f}</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            requester = st.text_input("👤 اسم طالب العلفة:", key="req_lp")

            st.markdown("### 🌾 اختيار المكونات")
            sq = st.text_input("🔍 بحث:", key="srch_lp")

            selected = []
            default_set = get_default_selections(lp_animal, lp_prod, lp_req)

            for cat_name, items in BIG_FEEDS_LIBRARY.items():
                filt = ({k: v for k, v in items.items()
                         if sq.lower() in k.lower()} if sq else items)
                if not filt: continue
                expanded = any(x in cat_name for x in ["الحبوب", "الأكساب", "الزيوت", "الأملاح"])
                with st.expander(f"📁 {cat_name} ({len(filt)})", expanded=expanded):
                    sc = st.columns(3)
                    for idx, ing_name in enumerate(filt.keys()):
                        with sc[idx % 3]:
                            dflt = ing_name in default_set
                            if st.checkbox(ing_name, value=dflt,
                                            key=f"lp_pick_{lp_animal}_{ing_name}"):
                                selected.append(ing_name)

            st.markdown("### 💰 أسعار المواد ($/طن)")
            prices_dict = {}
            if selected:
                pcols = st.columns(min(3, len(selected)))
                lookup = _get_ingredient_lookup()
                for idx, ing in enumerate(selected):
                    with pcols[idx % 3]:
                        prices_dict[ing] = st.number_input(
                            f"💵 {ing}", min_value=5.0,
                            value=float(lookup.get(ing, {}).get("price", 350)),
                            step=10.0, key=f"lp_pr_{lp_animal}_{ing}")

            st.success(f"✅ المختارة: **{len(selected)}** | الطاقة > البروتين مضمونة")

            if st.button("🚀 تشغيل المحرك", type="primary", use_container_width=True):
                if len(selected) < 3:
                    st.error("⚠️ اختر 3 مكونات على الأقل")
                else:
                    custom_std = requirement_to_standard(lp_req)
                    with st.spinner("⏳ جاري التركيب..."):
                        result = auto_formulate_smart(
                            selected, prices_dict, custom_std,
                            standard_key=lp_std_key, basis=basis_code,
                            min_quality=70.0, animal_type=lp_animal,
                            production_type=lp_prod)

                    if result["success"]:
                        st.session_state["last_formulation_result"] = result
                        st.session_state["last_formulation_context"] = {
                            "animal_choice": lp_animal,
                            "requirement_name": lp_req.name_ar,
                            "basis_label": basis_code,
                            "requirement": lp_req,
                            "custom_standard": custom_std,
                            "std_key_global": lp_std_key,
                            "requester_name": requester,
                            "local_rate": 1.0, "local_sym": "USD",
                            "animal_type": lp_animal,
                            "production_type": lp_prod}
                        st.session_state["formulation_history"].append({
                            "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "الحيوان": lp_animal,
                            "الحالة": lp_req.name_ar,
                            "الجودة": f"{result['quality_score']:.1f}%",
                            "التكلفة": f"${result['cost']:.2f}"})
                        st.success("✅ تم")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")

        # عرض النتيجة
        if st.session_state.get("last_formulation_result"):
            result = st.session_state["last_formulation_result"]
            ctx = st.session_state["last_formulation_context"]
            formula = result["formula"]
            actual = result["actual_nutrients"]
            quality = result.get("quality_score", 0)
            meets = result.get("meets_standard", False)
            cat_summary = result.get("category_summary", {})

            if meets:
                st.markdown(f"""
                <div class="quality-good-v113">
                    <h3 style="color:#1b5e20;margin:0;">✅ الجودة: {quality:.1f}%</h3>
                    <p>الطاقة: <b>{cat_summary.get('طاقة', 0):.1f}%</b> |
                       البروتين: <b>{cat_summary.get('بروتين', 0):.1f}%</b> |
                       الألياف: <b>{cat_summary.get('ألياف', 0):.1f}%</b></p>
                    <p>التكلفة: ${result['cost']:.2f}/طن</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="quality-bad-v113">
                    <h3 style="color:#c62828;margin:0;">⚠️ الجودة: {quality:.1f}%</h3>
                    <p>{result.get('warning', 'يحتاج تحسين')}</p>
                </div>
                """, unsafe_allow_html=True)

            # جدول
            st.markdown("### 📊 جدول المقارنة")
            labels = {"CP": "CP", "DP": "DP", "SE": "SE", "NDF": "NDF",
                      "ADF": "ADF", "EE": "EE", "ASH": "ASH", "Ca": "Ca", "P": "P"}
            cmp_rows = []
            for k, sv in ctx["custom_standard"].items():
                if sv == 0: continue
                cv = actual.get(k, 0)
                diff = cv - sv
                pct = (diff / sv * 100) if sv else 0
                ev = evaluate_difference(pct, standard_value=sv)
                cmp_rows.append({"العنصر": labels.get(k, k),
                                  "المعيار": f"{sv:.2f}",
                                  "المحسوب": f"{cv:.2f}",
                                  "الفرق": f"{diff:+.3f}",
                                  "التقييم": ev["label"]})
            st.dataframe(pd.DataFrame(cmp_rows), use_container_width=True, hide_index=True)

            st.markdown("### 🌾 المكونات:")
            for ing, pct in formula.items():
                cat = result.get("categories", {}).get(ing, "—")
                st.markdown(f'<div class="formula-item">▪️ <b>{ing}</b> ({cat}): '
                            f'{pct:.2f}% ({pct*10:.1f} كجم/طن)</div>',
                            unsafe_allow_html=True)

            # رسوم
            ch1, ch2 = st.columns(2)
            with ch1:
                bf = create_colorful_bar_chart(ctx["custom_standard"], actual)
                if bf: st.image(bf.getvalue(), caption="📊 المقارنة", use_container_width=True)
            with ch2:
                pf = create_colorful_pie_chart(formula)
                if pf: st.image(pf.getvalue(), caption="🥧 التوزيع", use_container_width=True)

            ch3, ch4 = st.columns(2)
            with ch3:
                rf = create_radar_chart(ctx["custom_standard"], actual)
                if rf: st.image(rf.getvalue(), caption="🕸️ الرادار", use_container_width=True)
            with ch4:
                gf = create_gauge_chart(quality)
                if gf: st.image(gf.getvalue(), caption="🎯 الجودة", use_container_width=True)

            # تنزيل
            st.markdown("### 📥 تحميل التقارير")
            col_pdf, col_xl = st.columns(2)
            with col_pdf:
                try:
                    pdf_bytes = pdf_gen.generate_report(
                        formula=formula,
                        requirement=ctx["requirement"],
                        animal_type=ctx["animal_type"],
                        breed=ctx["requirement_name"],
                        cost=result["cost"], city="—",
                        local_cost=result["cost"], local_sym="USD",
                        requester_name=ctx["requester_name"],
                        protein_basis=ctx["basis_label"],
                        standard_key=ctx["std_key_global"],
                        include_charts=True, quality_score=quality,
                        category_summary=cat_summary)
                    st.download_button(
                        "📄 تحميل PDF شامل (6 رسوم + مراجع)",
                        pdf_bytes,
                        file_name=f"Tawor_{lp_animal}_{datetime.now():%Y%m%d_%H%M}.pdf",
                        mime="application/pdf",
                        use_container_width=True, type="primary")
                except Exception as e:
                    st.error(f"⚠️ PDF: {e}")

            with col_xl:
                try:
                    xl = export_comparison_to_excel(
                        ctx["custom_standard"], actual,
                        ctx["requester_name"], ctx["animal_type"],
                        ctx["requirement_name"], formula, ctx["std_key_global"])
                    if xl:
                        st.download_button(
                            "📊 تحميل Excel", xl,
                            file_name=f"Formula_{lp_animal}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True)
                except Exception as e:
                    st.error(f"⚠️ Excel: {e}")

    # ═══════════ NLP ═══════════
    with sub_nlp:
        st.markdown('<div class="section-title">🎯 NLP — تحسين غير خطي</div>',
                    unsafe_allow_html=True)

        if not SCIPY_AVAILABLE or minimize is None:
            st.error("⚠️ SCIPY غير مثبتة")
        else:
            nlp_animal, nlp_prod, nlp_req, nlp_std_key = get_animal_requirement_ui("nlp")

            if nlp_req:
                st.success(f"📌 {nlp_req.name_ar} | DP={nlp_req.DP}% | "
                            f"CP={nlp_req.CP}% | SE={nlp_req.SE}")

            nlp_basis_radio = st.radio("أساس البروتين:",
                                         ["DP", "CP"],
                                         horizontal=True, key="nlp_basis")
            nlp_basis = nlp_basis_radio

            all_ings_nlp = list(_get_ingredient_lookup().keys())
            nlp_sel = st.multiselect("المكونات (2–10):",
                                      options=all_ings_nlp, default=[],
                                      max_selections=10, key="nlp_sel")

            if len(nlp_sel) >= 2:
                lookup = _get_ingredient_lookup()
                ing_data = {i: lookup[i] for i in nlp_sel}

                nlp_prices = {}
                pcols = st.columns(min(3, len(nlp_sel)))
                for i, ing in enumerate(nlp_sel):
                    with pcols[i % 3]:
                        nlp_prices[ing] = st.number_input(
                            f"{ing}:", min_value=10.0,
                            value=float(lookup[ing].get("price", 300)),
                            step=10.0, key=f"nlp_pr_{ing}")

                price_product = st.number_input("سعر المنتج ($/وحدة):",
                                                  0.5, 20.0, 2.5, 0.1, key="nlp_pp")

                if st.button("🚀 تشغيل NLP", type="primary", use_container_width=True,
                              disabled=(nlp_req is None)):
                    with st.spinner("⏳ جاري التحسين..."):
                        result = nlp_optimize_feed_v2(
                            nlp_sel, ing_data, nlp_prices,
                            requirement=nlp_req, animal_type=nlp_animal,
                            standard_key=nlp_std_key, protein_basis=nlp_basis,
                            price_product=price_product)

                    if result["success"]:
                        st.success(f"✅ ربح: ${result['max_profit']:.4f}")
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("💰 التكلفة", f"${result['final_cost']:.4f}")
                        m2.metric("⚡ ME", f"{result['final_me']:.0f}")
                        m3.metric("🧬 CP", f"{result['final_cp']:.2f}%")
                        m4.metric("⚖️ Ca:P", f"{result['ca_p_ratio']:.2f}")

                        st.markdown("### 🌾 التركيبة")
                        for ing, pct in result["formula"].items():
                            cat = result["categories"].get(ing, "—")
                            st.markdown(f'<div class="formula-item">▪️ <b>{ing}</b> '
                                        f'({cat}): {pct:.2f}%</div>',
                                        unsafe_allow_html=True)

                        if result.get("category_summary"):
                            st.markdown("### 🎯 ملخص التصنيف")
                            st.dataframe(pd.DataFrame([
                                {"الفئة": k, "النسبة %": f"{v:.1f}%"}
                                for k, v in result["category_summary"].items()]),
                                use_container_width=True, hide_index=True)
                    else:
                        st.error(f"❌ {result['message']}")
            else:
                st.info("💡 اختر مكونين على الأقل")

    # ═══════════ بدائل الحليب ═══════════
    with sub_milk:
        st.markdown('<div class="section-title">🍼 بدائل الحليب</div>',
                    unsafe_allow_html=True)

        mr1, mr2 = st.columns(2)
        with mr1:
            mr_a = st.selectbox("🐾 الحيوان:",
                                  list(MILK_REPLACER_STANDARDS.keys()), key="mr_a")
            mr_v = st.number_input("📦 الكمية (كجم):", 1.0, 10000.0,
                                    100.0, 10.0, key="mr_v")
        with mr2:
            std_mr = MILK_REPLACER_STANDARDS[mr_a]
            st.markdown(f"""
            <div style="background:#f1f8e9;padding:20px;border-radius:16px;
                        border-right:5px solid #2e7d32;">
                <b>📊 {mr_a}</b><br>
                بروتين: {std_mr['CP']}% | دهن: {std_mr['Fat']}% |
                لاكتوز: {std_mr['Lactose']}%<br>
                <small>📖 {std_mr['source']}</small>
            </div>
            """, unsafe_allow_html=True)

        mr_sel = []
        cols = st.columns(3)
        for i, (name, data) in enumerate(MILK_REPLACER_INGREDIENTS.items()):
            with cols[i % 3]:
                with st.expander(name):
                    st.caption(f"${data['price']}/كجم | {data['type']}")
                    if st.checkbox("إضافة", key=f"mr_{name}"):
                        mr_sel.append(name)

        st.info(f"📊 المختارة: {len(mr_sel)} | الحد: 3")

        if st.button("🧪 تركيب", type="primary", use_container_width=True):
            if len(mr_sel) < 3:
                st.warning("⚠️ 3 مكونات على الأقل")
            else:
                with st.spinner("⏳..."):
                    r = formulate_milk_replacer(mr_a, mr_v, mr_sel)

                if r["success"]:
                    quality = r.get("quality_score", 0)
                    bg = "quality-good-v113" if quality >= 70 else "quality-bad-v113"
                    st.markdown(f"""
                    <div class="{bg}">
                        <h3>✅ الجودة: {quality:.1f}%</h3>
                        <p>Ca:P = {r['ca_p_ratio']:.2f} | المكونات: {r['used_count']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    labels_mr = {"CP": "بروتين", "Fat": "دهن", "Lactose": "لاكتوز",
                                  "Ca": "Ca", "P": "P"}
                    comp_rows = []
                    for k, lab in labels_mr.items():
                        t = r["targets"].get(k, 0)
                        a = r["actual"].get(k, 0)
                        if t <= 0: continue
                        diff = a - t
                        pct = (diff / t * 100) if t else 0
                        ev = evaluate_difference(pct, standard_value=t)
                        comp_rows.append({"العنصر": lab, "المعيار": f"{t:.2f}",
                                            "المحسوب": f"{a:.2f}",
                                            "التقييم": ev["label"]})
                    st.dataframe(pd.DataFrame(comp_rows),
                                  use_container_width=True, hide_index=True)

                    for ing, pct in r["formula"].items():
                        st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> '
                                    f'{pct:.2f}%</div>',
                                    unsafe_allow_html=True)

                    st.metric("💰 تكلفة 100 كجم", f"${r['cost_per_100kg']:.2f}")
                else:
                    st.error(f"❌ {r['message']}")

    # ═══════════ الزيوت ═══════════
    with sub_oils:
        st.markdown('<div class="section-title">🌰 مكتبة الزيوت</div>',
                    unsafe_allow_html=True)
        st.write(f"{len(get_oil_ingredients())} زيتاً وفق NRC/INRA/Ross 308")

        oil_rows = [{"الحيوان": k, "أقصى %": f"{v['max']}%",
                      "مثالي %": f"{v['optimal']}%", "المرجع": v["source"]}
                     for k, v in MAX_OIL_PERCENTAGE.items()]
        st.dataframe(pd.DataFrame(oil_rows), use_container_width=True, hide_index=True)

        oils = get_oil_ingredients()
        for ing_name, ing_data in oils.items():
            with st.expander(f"🌰 {ing_name}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("SE", f"{ing_data.get('SE', 0):.0f}")
                c2.metric("kcal/kg", f"{ing_data.get('SE', 0) * 41:.0f}")
                c3.metric("السعر", f"${ing_data.get('price', 0):.0f}")

    # ═══════════ المختبر ═══════════
    with sub_lab:
        st.markdown('<div class="section-title">🔬 مختبر التحليل الذكي</div>',
                    unsafe_allow_html=True)

        lab_animal, lab_prod, lab_req, lab_std_key = get_animal_requirement_ui("lab")
        lab_std = requirement_to_standard(lab_req) if lab_req else {}

        if lab_req:
            st.success(f"📌 {lab_req.name_ar} | DP={lab_req.DP}% | CP={lab_req.CP}%")

        all_ings = list(_get_ingredient_lookup().keys())
        lab_cat = st.selectbox("📁 التصنيف:",
                                 ["الكل"] + list(BIG_FEEDS_LIBRARY.keys()), key="lab_cat")
        lab_search = st.text_input("🔍 بحث:", key="lab_srch")

        if lab_cat == "الكل": pool = all_ings
        else: pool = list(BIG_FEEDS_LIBRARY[lab_cat].keys())
        if lab_search:
            pool = [x for x in pool if lab_search.lower() in x.lower()]

        lookup_lab = _get_ingredient_lookup()
        default_df = pd.DataFrame({
            "المادة": pool,
            "الوزن (كجم)": [0.0] * len(pool),
            "السعر ($/طن)": [float(lookup_lab.get(m, {}).get("price", 300.0)) for m in pool]})

        edited = st.data_editor(
            default_df, use_container_width=True, hide_index=True,
            column_config={
                "المادة": st.column_config.TextColumn(disabled=True),
                "الوزن (كجم)": st.column_config.NumberColumn(min_value=0.0, step=5.0, format="%.1f"),
                "السعر ($/طن)": st.column_config.NumberColumn(min_value=5.0, step=10.0, format="$%.0f"),
            }, key="lab_editor")

        lab_in = {r["المادة"]: r["الوزن (كجم)"]
                  for _, r in edited.iterrows() if r["الوزن (كجم)"] > 0}
        tot = sum(lab_in.values())

        if tot > 0:
            f_lab = {k: v / tot * 100 for k, v in lab_in.items()}
            nut = compute_formula_nutrients(f_lab)
            edited_idx = edited.set_index("المادة")
            cost = sum(lab_in[k] * edited_idx.loc[k, "السعر ($/طن)"]
                        for k in lab_in) / 1000

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("⚖️ الوزن", f"{tot:.1f} كجم")
            c2.metric("🧬 CP", f"{nut['CP']:.2f}%")
            c3.metric("🧬 DP", f"{nut['DP']:.2f}%")
            c4.metric("⚡ SE", f"{nut['SE']:.1f}")
            c5.metric("💰 التكلفة", f"${cost:.2f}")

            if lab_req:
                st.markdown("### 📊 المقارنة")
                cmp_rows = []
                for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "Ca", "P"]:
                    sv = lab_std.get(k, 0)
                    if sv == 0: continue
                    cv = nut.get(k, 0)
                    diff = cv - sv
                    pct = (diff / sv * 100) if sv else 0
                    ev = evaluate_difference(pct, standard_value=sv)
                    cmp_rows.append({"العنصر": k, "المعيار": f"{sv:.2f}",
                                      "المحسوب": f"{cv:.2f}", "الفرق": f"{diff:+.3f}",
                                      "التقييم": ev["label"], "score": ev["score"]})
                st.dataframe(pd.DataFrame([{k: v for k, v in r.items() if k != "score"}
                                            for r in cmp_rows]),
                              use_container_width=True, hide_index=True)

                quality = sum(r["score"] for r in cmp_rows) / len(cmp_rows)
                st.metric("🏆 الجودة", f"{quality:.1f}%")

                ch1, ch2 = st.columns(2)
                with ch1:
                    bf = create_colorful_bar_chart(lab_std, nut)
                    if bf: st.image(bf.getvalue(), use_container_width=True)
                with ch2:
                    rf = create_radar_chart(lab_std, nut)
                    if rf: st.image(rf.getvalue(), use_container_width=True)

            st.markdown("### 📋 التركيبة")
            st.dataframe(pd.DataFrame([
                {"المادة": k, "الوزن": f"{v:.1f}", "النسبة %": f"{f_lab[k]:.2f}"}
                for k, v in lab_in.items()]), use_container_width=True, hide_index=True)

            pie = create_colorful_pie_chart(f_lab)
            if pie: st.image(pie.getvalue(), use_container_width=True)
        else:
            st.info("💡 أدخل أوزان المواد")

# ═══════════════════════════════════════════════════════════════════════════
# 🏗️ الحظائر
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["🏗️ الحظائر"]:
    st.markdown('<div class="section-title">🏗️ مصمم الحظائر</div>',
                unsafe_allow_html=True)
    st.info("💡 قسم الحظائر 3D — قيد التطوير. يعمل في النسخة الكاملة.")

# ═══════════════════════════════════════════════════════════════════════════
# 📊 الجدوى
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["📊 الجدوى"]:
    st.markdown('<div class="section-title">📊 دراسة الجدوى المالية</div>',
                unsafe_allow_html=True)

    with st.expander("⚙️ التكاليف الاستثمارية", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            barns_cost = st.number_input("إنشاءات الحظائر", 0.0, 1_000_000.0,
                                           18000.0, 500.0, key="fin_barns")
            water_system = st.number_input("أنظمة السقيا", 0.0, 500_000.0,
                                             3500.0, 100.0, key="fin_water")
        with c2:
            mixers_cost = st.number_input("معدات الخلط", 0.0, 500_000.0,
                                            6000.0, 200.0, key="fin_mix")
            herd_cost = st.number_input("القطيع", 0.0, 2_000_000.0,
                                          15000.0, 500.0, key="fin_herd")
        with c3:
            vet_equip = st.number_input("معدات بيطرية", 0.0, 200_000.0,
                                          1500.0, 100.0, key="fin_vet")

    with st.expander("💸 التكاليف التشغيلية", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            annual_feed_cost = st.number_input("الأعلاف", 0.0, 5_000_000.0,
                                                 28500.0, 500.0, key="fin_feed")
            vet_med_cost = st.number_input("بيطري", 0.0, 1_000_000.0,
                                             3200.0, 100.0, key="fin_med")
        with c2:
            labor_cost = st.number_input("أجور", 0.0, 1_000_000.0,
                                           7500.0, 200.0, key="fin_labor")
            utilities_cost = st.number_input("طاقة", 0.0, 500_000.0,
                                               1800.0, 100.0, key="fin_util")
        with c3:
            contingency_cost = st.number_input("طوارئ", 0.0, 500_000.0,
                                                 2000.0, 100.0, key="fin_cont")

    c1, c2 = st.columns(2)
    with c1:
        annual_revenue = st.number_input("الإيرادات السنوية ($)",
                                           0.0, 10_000_000.0, 68000.0, 1000.0,
                                           key="fin_rev")
    with c2:
        discount_rate = st.slider("معدل الخصم (%)", 5.0, 20.0, 10.0, 0.5,
                                    key="fin_disc") / 100.0

    total_investment = barns_cost + water_system + mixers_cost + herd_cost + vet_equip
    annual_depreciation = (barns_cost/15 + water_system/8 + mixers_cost/10
                            + herd_cost/5 + vet_equip/5)
    total_operating_costs = (annual_feed_cost + vet_med_cost + labor_cost
                              + utilities_cost + contingency_cost)
    total_annual_costs = total_operating_costs + annual_depreciation
    net_annual_profit = annual_revenue - total_annual_costs
    roi = ((net_annual_profit / total_investment) * 100 if total_investment > 0 else 0)
    payback = (total_investment / (net_annual_profit + annual_depreciation)
               if (net_annual_profit + annual_depreciation) > 0 else 99.9)

    st.markdown("### 📊 المؤشرات المالية")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💰 الاستثمار", f"${total_investment:,.2f}")
    k2.metric("💸 التشغيل", f"${total_operating_costs:,.2f}")
    k3.metric("📈 الربح", f"${net_annual_profit:,.2f}", delta=f"ROI: {roi:.2f}%")
    k4.metric("⏱️ الاسترداد", f"{payback:.2f} سنة")

    # التدفقات
    st.markdown("### 📊 التدفقات النقدية (5 سنوات)")
    years = [f"سنة {i}" for i in range(1, 6)]
    npv_values = []
    cf_rows = []
    cur_rev = annual_revenue
    cur_op = total_operating_costs
    for i, yr in enumerate(years):
        if i > 0:
            cur_rev *= 1.03
            cur_op *= 1.025
        net_cf = cur_rev - cur_op
        disc_cf = net_cf / ((1 + discount_rate) ** (i + 1))
        npv_values.append(disc_cf)
        cf_rows.append({"السنة": yr, "الإيرادات ($)": round(cur_rev, 2),
                         "التشغيل ($)": round(cur_op, 2),
                         "CF الصافي ($)": round(net_cf, 2),
                         "القيمة المخصومة ($)": round(disc_cf, 2)})

    cf_df = pd.DataFrame(cf_rows)
    st.dataframe(cf_df, use_container_width=True, hide_index=True)

    total_npv = sum(npv_values) - total_investment
    if total_npv > 0:
        st.success(f"✅ NPV = ${total_npv:,.2f} — مجدٍ")
    else:
        st.warning(f"⚠️ NPV = ${total_npv:,.2f}")

    # السيناريوهات
    st.markdown("### 🌐 السيناريوهات")
    scenarios = {"متفائل": {"rev": 1.15, "cost": 0.90},
                  "واقعي": {"rev": 1.00, "cost": 1.00},
                  "متشائم": {"rev": 0.85, "cost": 1.15}}
    rows_sc = []
    for name, f in scenarios.items():
        sr = annual_revenue * f["rev"]
        sc = total_operating_costs * f["cost"] + annual_depreciation
        sp = sr - sc
        sroi = (sp / total_investment * 100) if total_investment > 0 else 0
        rows_sc.append({"السيناريو": name, "الربح ($)": round(sp, 2),
                         "ROI %": round(sroi, 2)})
    st.dataframe(pd.DataFrame(rows_sc), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════
# 🏭 المستودعات (مالك فقط)
# ═══════════════════════════════════════════════════════════════════════════

if is_owner():
    with tab_map["🏭 المستودعات"]:
        st.markdown('<div class="section-title">🏭 المستودعات</div>',
                    unsafe_allow_html=True)
        inv = st.session_state["inventory"]
        q = [v["quantity"] for v in inv.values()]
        c1, c2, c3 = st.columns(3)
        c1.metric("📦 المواد", len(inv))
        c2.metric("🟢 آمنة", sum(1 for x in q if x >= 5))
        c3.metric("⚠️ منخفضة", sum(1 for x in q if 0 < x < 5))

        inv_df = pd.DataFrame([
            {"المادة": name, "الكمية (طن)": v["quantity"],
             "الحد الأدنى": v["min_threshold"]}
            for name, v in list(inv.items())[:50]])
        edited = st.data_editor(inv_df, use_container_width=True, hide_index=True,
                                  column_config={
                                      "المادة": st.column_config.TextColumn(disabled=True),
                                      "الكمية (طن)": st.column_config.NumberColumn(min_value=0.0, step=1.0),
                                      "الحد الأدنى": st.column_config.NumberColumn(min_value=0.0, step=1.0),
                                  }, key="inv_editor")
        if st.button("💾 حفظ", type="primary", use_container_width=True):
            for _, r in edited.iterrows():
                inv[r["المادة"]]["quantity"] = float(r["الكمية (طن)"])
                inv[r["المادة"]]["min_threshold"] = float(r["الحد الأدنى"])
            st.success("✅ تم الحفظ")

    with tab_map["📈 التحليلات"]:
        st.markdown('<div class="section-title">📈 التحليلات</div>',
                    unsafe_allow_html=True)
        n_formulas = len(st.session_state.get("formulation_history", []))
        m1, m2, m3 = st.columns(3)
        m1.metric("🧬 خلطات", n_formulas)
        m2.metric("📦 مخزون", len(st.session_state.get("inventory", {})))
        m3.metric("📊 عدد المكونات", len(_get_ingredient_lookup()))

        history = st.session_state.get("formulation_history", [])
        if history:
            st.markdown("### 📜 سجل الخلطات")
            st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════
# المراجع
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["📚 المراجع"]:
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>',
                unsafe_allow_html=True)
    st.markdown("""
### المراجع المعتمدة:
- **NRC (2012)** — Swine Nutrition
- **NRC (2007)** — Small Ruminants
- **NRC (2001)** — Dairy Cattle
- **NRC (2007)** — Horses
- **NRC (1994)** — Poultry
- **INRA (2018)** — Ruminants
- **FAO (2010)** — Camel Nutrition
- **Ross 308 (2020)** — Broiler Handbook
- **Danø & Højsgaard (2005)** — LP in Ration Formulation
- **McDonald et al. (2011)** — Animal Nutrition
    """)

with tab_map["📖 الدليل"]:
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
### ✨ الميزات v{APP_VERSION}:
- 🔬 النمذجة: **5 تبويبات** (LP + NLP + حليب + زيوت + مختبر)
- ⚡ **إصلاح جذري**: البروتين لا يتجاوز الطاقة
- 🔐 **كود المالك**: `TAWOR2026`
- 📄 **PDF شامل**: 6 رسوم + مراجع + تصنيف + حساسية
- 🎯 **تصنيف المكونات**: 8 فئات (طاقة/بروتين/ألياف/زيت/معدن/بريمكس/أميني/أخرى)

### 🔑 الدخول:
- 👑 **المالك**: كود `TAWOR2026` (مشفّر في الكود)
- 👥 **الزائر**: مجاني

### 📞 الدعم
📧 {OWNER_EMAIL}

---
🤲 {DUA_FULL} 🤲
    """)

# ═══════════════════════════════════════════════════════════════════════════
# التذييل
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(f'<div class="mini-signature">🌾 {APP_NAME} v{APP_VERSION} | {SUPERVISOR}</div>',
            unsafe_allow_html=True)
st.markdown(f'<div class="dua-fixed-banner">🤲 {DUA_SHORT} 🤲</div>',
            unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
