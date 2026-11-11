# ═══════════════════════════════════════════════════════════════════════════
# تاور نولجي TAWOR NOLOGY 12.0 — النسخة النهائية الآمنة الكاملة
# د. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
# ═══════════════════════════════════════════════════════════════════════════
# 🔐 الأمان:
#   • لا يوجد كود مالك صريح في الملف إطلاقاً
#   • يعتمد حصراً على st.secrets["OWNER_CODE"] (أو env var)
#   • مقارنة constant-time + rate-limit (3 محاولات → قفل 5 دقائق)
# ✨ الجديد في 12.0:
#   • محرك التحسين غير الخطي NLP (SLSQP) — تعظيم الربح
#   • 4 رسوم تحليلية: منحنى الربحية، سطح 3D، Tornado، جبهة باريتو
#   • PDF شامل للـ NLP
#   • إصلاح كل أخطاء PDF (ImageReader، الخطوط العربية، Spacer)
#   • إزالة التكرار (الملف كان مُلصقاً مرتين)
# ═══════════════════════════════════════════════════════════════════════════

import os
import re
import io
import base64
import hashlib
import hmac
import json
import time as _time
import random
import traceback
import warnings
import threading
import tempfile
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache, wraps
from typing import Optional, Dict, List, Tuple, Any, Set

import numpy as np
import pandas as pd
import streamlit as st

warnings.filterwarnings("ignore")

# ─── استيرادات اختيارية ───
try:
    from scipy.optimize import linprog, minimize as scipy_minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    linprog = None
    scipy_minimize = None

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Wedge
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

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
    from reportlab.platypus import (
        Table, TableStyle, Paragraph, Spacer, Image as RLImage,
        SimpleDocTemplate, HRFlowable, PageBreak,
    )
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.lib.utils import ImageReader
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    Spacer = RLImage = Table = TableStyle = Paragraph = HRFlowable = None
    ImageReader = None
    SimpleDocTemplate = PageBreak = None
    ParagraphStyle = TA_CENTER = TA_RIGHT = None
    HexColor = white = None

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
    import pytesseract
    import cv2
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════
# الثوابت
# ═══════════════════════════════════════════════════════════════════════════

DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي ابتسام"
DUA_FULL = "رحم الله والدي إسماعيل تاور وأختي ابتسام وأسكنهما فسيح جناته"
DUA_QURAN = "﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾"
DUA_VERSE = "﴿ وَقُل رَّبِّ ارْحَمْهُمَا كَمَا رَبَّيَانِي صَغِيرًا ﴾"
DUA_VISITOR = """🕌 <b>إلى زوارنا الكرام:</b><br>
هذه المنصة صدقةٌ جارية عن <b>والدي إسماعيل تاور</b> و<b>أختي ابتسام</b>.<br>
نسألكم بظهر الغيب أن تشاركوا الدعاء. 🤲"""

APP_NAME = "تاور نولجي Tawor Nology"
APP_TAGLINE = "للإنتاج الحيواني وتغذية الحيوان"
APP_VERSION = "12.0"
SUPERVISOR = "د. عبدالقادر إسماعيل تاور"
SUPERVISOR_TITLE = "اختصاصي تغذية الحيوان"
PLATFORM_URL = "https://tawor-nology.streamlit.app"
WHATSAPP_NUMBER = "+249123533489"
OWNER_EMAIL = "abukram128@gmail.com"
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG"]
LOGO_OPTIONS = ["logo.png", "logo.jpg"]

st.set_page_config(
    page_title=f"{APP_NAME} | {APP_TAGLINE}",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ═══════════════════════════════════════════════════════════════════════════
# 🔐 وحدة الأمان — لا كود صريح
# ═══════════════════════════════════════════════════════════════════════════

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


@lru_cache(maxsize=1)
def _get_owner_code_hash() -> Optional[str]:
    """يقرأ كود المالك من st.secrets أو env — لا fallback مُدمج."""
    try:
        if hasattr(st, "secrets"):
            code = str(st.secrets.get("OWNER_CODE", "") or "").strip()
            if len(code) >= 6:
                return _sha256(code)
    except Exception:
        pass
    code = str(os.environ.get("TAWOR_OWNER_CODE", "") or "").strip()
    if len(code) >= 6:
        return _sha256(code)
    return None


def check_owner_code(user_input: str) -> bool:
    if not user_input:
        return False
    expected = _get_owner_code_hash()
    if not expected:
        return False
    return hmac.compare_digest(_sha256(user_input.strip()), expected)


def _session_valid() -> bool:
    approved = st.session_state.get("approved", False)
    role = st.session_state.get("user_role")
    if approved and role not in ("owner", "guest"):
        return False
    if role == "owner" and not _get_owner_code_hash():
        return False
    return True


def is_owner() -> bool:
    return st.session_state.get("user_role") == "owner"


def _handle_login(user_code: str) -> Dict:
    now = _time.time()
    lock = st.session_state.get("owner_lock_until", 0.0)
    if now < lock:
        return {"ok": False, "msg": f"🔒 مقفل — انتظر {int(lock - now)} ثانية"}

    if check_owner_code(user_code):
        st.session_state.update({
            "approved": True, "user_role": "owner",
            "owner_attempts": 0, "owner_lock_until": 0.0,
        })
        return {"ok": True, "msg": "✅ مرحباً"}

    if not _get_owner_code_hash():
        return {"ok": False, "msg": "⚠️ OWNER_CODE غير مُهيّأ — أضفه في st.secrets"}

    n = st.session_state.get("owner_attempts", 0) + 1
    st.session_state["owner_attempts"] = n
    if n >= 3:
        st.session_state["owner_lock_until"] = now + 300
        return {"ok": False, "msg": "🔒 3 محاولات فاشلة — قفل 5 دقائق"}
    return {"ok": False, "msg": f"❌ كود غير صحيح — متبقٍ {3 - n}"}


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
        self.font_name = "Helvetica"
        self.ready = False
        if not REPORTLAB_AVAILABLE:
            return
        paths = [
            os.path.join(FONT_DIR, "Amiri-Regular.ttf"),
            "Amiri-Regular.ttf",
            "/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
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
            pdfmetrics.registerFont(TTFont("TaworArabic", path))
            self.font_name = "TaworArabic"
            self.ready = True
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
        return get_display(arabic_reshaper.reshape(str(text)), base_dir="R")
    except Exception:
        return str(text)


def ar(text):
    return _ar_cached(text)


# ═══════════════════════════════════════════════════════════════════════════
# مكتبة الأعلاف
# ═══════════════════════════════════════════════════════════════════════════

def _feed(cp, dc, se, ndf, adf, ee, ash, ca, p, lys, met, price, desc, src):
    return {
        "CP": cp, "DC": dc, "SE": se, "NDF": ndf, "ADF": adf,
        "EE": ee, "ASH": ash, "Ca": ca, "P": p,
        "Lys": lys, "Met": met, "price": price, "desc": desc, "src": src,
    }


BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": _feed(8.5, .85, 80, 9.5, 3.2, 3.8, 1.3, .02, .27, .24, .17, 230, "الطاقة الرئيسية", "NRC 2012"),
        "ذرة بيضاء": _feed(8.8, .83, 78, 10.2, 3.5, 3.5, 1.4, .02, .26, .25, .18, 225, "بديل محلي", "NRC 2012"),
        "شعير مطحون": _feed(11.5, .8, 71, 18.5, 7.5, 2.2, 2.5, .05, .35, .42, .2, 210, "للمجترات", "NRC 2012"),
        "قمح محلي": _feed(12, .85, 75, 11.5, 3.8, 2, 1.6, .04, .32, .35, .2, 240, "طاقة جيدة", "NRC 2012"),
        "جريش أرز": _feed(7.8, .82, 82, 5.5, 2.5, 8.5, 4.2, .06, .3, .28, .18, 240, "طاقة عالية", "NRC 2012"),
        "شوفان علفي": _feed(11, .76, 62, 27.5, 13.5, 5, 3, .08, .35, .4, .18, 260, "للخيول", "NRC 2007"),
        "كسرة خبز": _feed(10.5, .82, 75, 8, 3.5, 5.5, 3.5, .1, .2, .28, .17, 160, "اقتصادي", "INRA 2018"),
        "عسل أسود (دبس)": _feed(1, .92, 75, 0, 0, 0, 3.5, .15, .05, .05, .02, 220, "≤3% فقط", "NRC 2012"),
        "تفل بنجر السكر": _feed(8.5, .65, 55, 45, 28, 1, 8.5, .7, .1, .3, .15, 190, "للمجترات", "INRA 2018"),
    },
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني": _feed(46, .88, 73, 15.5, 8.5, 1.5, 5.5, .2, .65, 1.6, .45, 460, "ممتاز", "NRC 2012"),
        "كسب فول صويا 44%": _feed(44, .9, 74, 13.5, 8, 1.8, 6, .35, .65, 2.7, .6, 440, "الرئيسي", "NRC 2012"),
        "كسب فول صويا 48%": _feed(48, .91, 76, 12, 7, 1.5, 6.2, .35, .65, 3, .68, 480, "مرتفع", "NRC 2012"),
        "كسب عباد الشمس 36%": _feed(36, .76, 42, 38.5, 25.5, 2.5, 6.5, .4, 1, 1.2, .7, 310, "أرخص", "NRC 2012"),
        "كسب بذور القطن": _feed(41, .78, 55, 24.5, 15.5, 1.2, 6.5, .2, 1.1, 1.8, .6, 290, "جوسيبول", "NRC 2012"),
        "كسب بذور الكتان": _feed(32, .82, 65, 18.5, 10.5, 2.8, 5.8, .35, .85, 1.2, .55, 340, "أوميغا 3", "NRC 2007"),
        "كسب جلوتين 60%": _feed(60, .92, 85, 8.5, 5.5, 2.5, 3.5, .15, .5, 1.1, 1.8, 520, "ميثيونين عالٍ", "NRC 2012"),
        "كسب الكانولا": _feed(36, .82, 60, 28, 18, 3.5, 6.5, .65, 1.1, 1.9, .7, 400, "متوازن", "NRC 2012"),
        "فول صويا كامل": _feed(38, .85, 78, 15, 10, 18, 4.5, .25, .55, 2.5, .55, 420, "معالجة حرارية", "NRC 2012"),
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": _feed(15, .72, 45, 35.5, 12.5, 3.5, 5.5, .12, 1.1, .6, .25, 150, "اقتصادية", "NRC 2001"),
        "نخالة ذرة": _feed(9.5, .65, 40, 40, 15, 4, 2, .1, .75, .3, .15, 140, "اقتصادية", "NRC 2001"),
        "البرسيم الجاف": _feed(16.5, .6, 35, 42.5, 32.5, 2, 10.5, 1.5, .25, .85, .25, 170, "بروتين + ألياف", "NRC 2001"),
        "مولاس قصب السكر": _feed(4, .95, 50, 1.5, .8, .5, 8.5, .7, .05, .03, .02, 120, "طاقة سريعة", "NRC 2001"),
        "تبن قمح": _feed(3.2, .35, 18, 72.5, 45.5, 1.5, 8.5, .3, .08, .15, .05, 80, "ألياف", "NRC 2001"),
        "قش أرز": _feed(3.5, .3, 15, 70, 45, 1.5, 12, .2, .06, .12, .05, 65, "حشو", "NRC 2007"),
        "سعف نخيل مطحون": _feed(4, .3, 20, 65, 42, 2, 7, .35, .08, .15, .06, 55, "ألياف", "FAO 2010"),
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": _feed(60, .85, 65, 2.5, 1.5, 8.5, 22.5, 5.5, 3.2, 4.5, 1.8, 850, "ممتاز", "NRC 2012"),
        "مسحوق اللحم والعظم": _feed(50, .75, 50, 3.5, 2.5, 10.5, 32.5, 9, 4.5, 2.5, .7, 620, "Ca+P", "NRC 2012"),
        "مسحوق الدم": _feed(80, .65, 55, 1, .5, 1.5, 6, .3, .3, 7, 1, 780, "هضم منخفض", "NRC 2012"),
        "حشرات مجففة (BSF)": _feed(42, .8, 68, 8, 5, 35, 8, .8, .9, 2.6, .85, 1800, "مستدام", "FAO 2013"),
    },
    "🌰 الزيوت النباتية والحيوانية": {
        "زيت ذرة": _feed(0, 0, 220, 0, 0, 100, 0, 0, 0, 0, 0, 1500, "أوميغا 6", "NRC 2012"),
        "زيت فول الصويا": _feed(0, 0, 215, 0, 0, 100, 0, 0, 0, 0, 0, 1350, "متوازن", "Ross 308"),
        "زيت عباد الشمس": _feed(0, 0, 210, 0, 0, 100, 0, 0, 0, 0, 0, 1300, "أوميغا 6", "NRC 2007"),
        "زيت الكتان": _feed(0, 0, 205, 0, 0, 100, 0, 0, 0, 0, 0, 1700, "أوميغا 3", "NRC 2007"),
        "زيت جوز الهند": _feed(0, 0, 230, 0, 0, 100, 0, 0, 0, 0, 0, 1900, "MCT", "NRC 2012"),
        "زيت النخيل": _feed(0, 0, 215, 0, 0, 100, 0, 0, 0, 0, 0, 1100, "مقاوم", "NRC 2012"),
        "زيت الكانولا": _feed(0, 0, 200, 0, 0, 100, 0, 0, 0, 0, 0, 1450, "متوازن", "NRC 2012"),
        "زيت الزيتون": _feed(0, 0, 210, 0, 0, 100, 0, 0, 0, 0, 0, 3500, "أوميغا 9", "INRA 2018"),
        "شحم حيواني (Tallow)": _feed(0, 0, 230, 0, 0, 100, 0, 0, 0, 0, 0, 900, "طاقة عالية", "NRC 2012"),
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": _feed(94, 1, 0, 0, 0, 0, .5, 0, 0, 94, 0, 4200, "أساسي", "NRC 2012"),
        "ميثيونين نقي": _feed(58, 1, 0, 0, 0, 0, .3, 0, 0, 0, 58, 5800, "للدواجن", "NRC 2012"),
        "ثريونين نقي": _feed(72, 1, 0, 0, 0, 0, .2, 0, 0, 0, 0, 4800, "ثالث محدود", "NRC 2012"),
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن": _feed(0, 0, 0, 0, 0, 0, 100, 18, 8, 0, 0, 4800, "فيتامينات", "NRC 1994"),
        "بريمكس بياض": _feed(0, 0, 0, 0, 0, 0, 100, 22, 7, 0, 0, 5000, "للبياض", "NRC 1994"),
        "بريمكس أبقار": _feed(0, 0, 0, 0, 0, 0, 100, 20, 10, 0, 0, 5200, "للأبقار", "NRC 2001"),
        "بريمكس مجترات": _feed(0, 0, 0, 0, 0, 0, 100, 18, 9, 0, 0, 4500, "للمجترات", "NRC 2007"),
        "إنزيم فايتيز": _feed(0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 4200, "تحرير P", "NRC 2012"),
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": _feed(0, 0, 0, 0, 0, 0, 99.5, 38, 0, 0, 0, 40, "مصدر Ca", "NRC 2012"),
        "فوسفات ثنائي الكالسيوم": _feed(0, 0, 0, 0, 0, 0, 98.5, 23, 18, 0, 0, 280, "Ca+P", "NRC 2012"),
        "ملح الطعام": _feed(0, 0, 0, 0, 0, 0, 99.9, 0, 0, 0, 0, 30, "NaCl", "NRC 2012"),
        "بيكربونات الصوديوم": _feed(0, 0, 0, 0, 0, 0, 99, 0, 0, 0, 0, 340, "مضاد حموضة", "NRC 2001"),
        "مضاد سموم فطرية": _feed(0, 0, 0, 0, 0, 0, 85, 0, 0, 0, 0, 950, "أفلاتوكسين", "NRC 2012"),
    },
    "💊 الفيتامينات": {
        "فيتامين A": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 4200, "نمو ورؤية", "NRC 2012"),
        "فيتامين D3": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 5200, "امتصاص Ca", "NRC 2012"),
        "فيتامين E": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 5800, "مضاد أكسدة", "NRC 2012"),
    },
}


def _get_ingredient_lookup() -> Dict[str, Dict]:
    if not hasattr(_get_ingredient_lookup, "_cache"):
        lookup = {}
        for cat in BIG_FEEDS_LIBRARY.values():
            lookup.update(cat)
        _get_ingredient_lookup._cache = lookup
    return _get_ingredient_lookup._cache


def get_oil_ingredients() -> Dict[str, Dict]:
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت النباتية والحيوانية", {})


MAX_OIL_PERCENTAGE = {
    "دواجن_بادي": {"max": 8.0, "optimal": 5.0, "source": "Ross 308"},
    "دواجن_نامي": {"max": 7.0, "optimal": 4.5, "source": "Ross 308"},
    "دواجن_ناهي": {"max": 7.0, "optimal": 4.0, "source": "Ross 308"},
    "دواجن_بياض": {"max": 5.0, "optimal": 2.5, "source": "NRC 1994"},
    "أبقار_حليب_عالي": {"max": 6.0, "optimal": 4.0, "source": "NRC 2001"},
    "أبقار_تسمين_مكثف": {"max": 6.0, "optimal": 4.5, "source": "NRC 2001"},
    "أغنام_تسمين_مكثف": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "ماعز_حلابة_عالي": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "إبل_تسمين": {"max": 6.0, "optimal": 4.0, "source": "FAO 2010"},
    "خيول_رياضة_مكثف": {"max": 10.0, "optimal": 7.0, "source": "NRC Horses"},
    "أسماك_بادئ": {"max": 15.0, "optimal": 10.0, "source": "NRC Fish"},
    "أرانب_تسمين": {"max": 4.0, "optimal": 2.5, "source": "NRC 2007"},
}


def get_oil_standard(k: str) -> Dict[str, Any]:
    return MAX_OIL_PERCENTAGE.get(k, {"max": 5.0, "optimal": 3.0, "source": "عام"})


INGREDIENT_LIMITS_BY_ANIMAL = {
    "دواجن": {
        "يوريا علفية": (0, 0), "سمن حيواني (Lard)": (0, 0),
        "نخالة قمح (ردة)": (0, 10), "تبن قمح": (0, 2),
        "كسب بذور القطن": (0, 5), "ملح الطعام": (.2, .4),
        "الحجر الجيري": (.8, 2), "فوسفات ثنائي الكالسيوم": (.5, 2.5),
        "بريمكس تسمين دواجن": (.2, .35), "بريمكس بياض": (.2, .35),
        "ليسين نقي": (0, .5), "ميثيونين نقي": (0, .4),
    },
    "أبقار": {
        "نخالة قمح (ردة)": (0, 30), "ملح الطعام": (.3, .5),
        "بيكربونات الصوديوم": (.5, 1), "الحجر الجيري": (0, 3.5),
        "فوسفات ثنائي الكالسيوم": (0, 2), "بريمكس أبقار": (.15, .3),
    },
    "أغنام": {
        "نخالة قمح (ردة)": (0, 25), "ملح الطعام": (.3, .5),
        "بيكربونات الصوديوم": (.5, 1), "بريمكس مجترات": (.15, .3),
        "الحجر الجيري": (0, 3),
    },
    "ماعز": {
        "نخالة قمح (ردة)": (0, 25), "ملح الطعام": (.3, .5),
        "بيكربونات الصوديوم": (.5, 1), "بريمكس مجترات": (.15, .3),
    },
    "إبل": {
        "نخالة قمح (ردة)": (0, 20), "ملح الطعام": (.3, .5),
        "بيكربونات الصوديوم": (.5, 1),
    },
    "خيول": {
        "نخالة قمح (ردة)": (0, 20), "ملح الطعام": (.3, .5),
        "الحجر الجيري": (0, 2.5),
    },
    "أسماك": {
        "يوريا علفية": (0, 0), "ملح الطعام": (0, .3),
    },
    "أرانب": {
        "نخالة قمح (ردة)": (0, 20), "ملح الطعام": (.3, .5),
    },
}


def get_animal_limits(animal: str) -> Dict[str, Tuple[float, float]]:
    return INGREDIENT_LIMITS_BY_ANIMAL.get(animal, {})


# ═══════════════════════════════════════════════════════════════════════════
# الاحتياجات الغذائية
# ═══════════════════════════════════════════════════════════════════════════

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


def get_cattle_requirements(t: str, milk_yield: float = 20.0,
                              weight_kg: float = 500.0) -> AnimalRequirement:
    if t == "حليب_عالي":
        dp = 12.5 + milk_yield * .30
        return AnimalRequirement(round(dp, 2), round(dp / .70, 2),
                                  round(60 + milk_yield * .35, 1), 30, 19, 5.5, 8,
                                  round(.55 + milk_yield * .003, 3),
                                  round(.33 + milk_yield * .0015, 3),
                                  "أبقار حلابة عالية", f"حليب {milk_yield} كجم")
    if t == "تسمين_مكثف":
        return AnimalRequirement(11.5, 14.5, 72, 32, 20, 4.5, 7.5, .65, .38,
                                  "تسمين مكثف", "ADG >1.3")
    return AnimalRequirement(7.5, 10, 53, 45, 28, 3, 8.5, .42, .26,
                              "أبقار صيانة", "بدون إنتاج")


def get_sheep_requirements(t: str, is_male: bool = True,
                            weight_kg: float = 50.0,
                            litter_size: int = 1) -> AnimalRequirement:
    if is_male:
        if t == "تسمين_مكثف":
            return AnimalRequirement(11.5, 14.5, 64, 28, 17, 4, 8, .65, .36,
                                      "تسمين مكثف", "ADG >250")
        return AnimalRequirement(9.5, 12, 59, 33, 21, 3.6, 8, .55, .32,
                                  "تسمين عادي", "ADG ~180")
    if t == "مرضعات":
        dp = 10.5 + (litter_size - 1) * 1.5
        return AnimalRequirement(round(dp, 2), round(dp / .72, 2),
                                  round(60 + (litter_size - 1) * 5, 1),
                                  30, 19, 4.5, 8.5,
                                  round(.65 + (litter_size - 1) * .1, 3),
                                  round(.38 + (litter_size - 1) * .05, 3),
                                  f"نعاج مرضعات ({litter_size})", "")
    return AnimalRequirement(7.2, 9.5, 48, 45, 28, 3, 8.5, .42, .26,
                              "نعاج صيانة", "")


def get_goat_requirements(t: str, is_male: bool = True,
                            milk_yield: float = 2.0) -> AnimalRequirement:
    if is_male:
        return AnimalRequirement(9, 11.5, 57, 36, 22, 3.5, 8, .55, .3,
                                  "تيوس تسمين", "")
    if t == "حلابة_عالي":
        dp = 11.5 + milk_yield * .45
        return AnimalRequirement(round(dp, 2), round(dp / .7, 2),
                                  round(58 + milk_yield * .45, 1),
                                  29, 18, 4.5, 8.5,
                                  round(.6 + milk_yield * .008, 3),
                                  round(.35 + milk_yield * .004, 3),
                                  f"عنزات حلابة ({milk_yield} لتر)", "")
    return AnimalRequirement(6.8, 9, 46, 46, 28, 3, 8.5, .42, .26,
                              "عنزات صيانة", "")


def get_camel_requirements(t: str, weight_kg: float = 400.0,
                             milk_yield: float = 5.0) -> AnimalRequirement:
    if t == "تسمين":
        return AnimalRequirement(9.5, 12, 65, 35, 22, 4.5, 7.5, .6, .35,
                                  "إبل تسمين", f"{weight_kg} كجم")
    return AnimalRequirement(7, 9, 48, 48, 30, 3.5, 9, .42, .26,
                              "إبل صيانة", f"{weight_kg} كجم")


def get_horse_requirements(t: str,
                             weight_kg: float = 450.0) -> AnimalRequirement:
    if t == "رياضة_مكثف":
        return AnimalRequirement(10.5, 13.5, 70, 30, 18, 7, 7.5, .7, .4,
                                  "خيول رياضة مكثف", "")
    return AnimalRequirement(7.2, 9.5, 53, 46, 29, 3.5, 8, .45, .28,
                              "خيول صيانة", "")


def get_poultry_requirements(strain: str,
                                age_weeks: int = 1) -> AnimalRequirement:
    if strain == "لاحم":
        if age_weeks <= 1:
            return AnimalRequirement(20, 23, 76, 8, 4, 5, 6.5, 1, .5,
                                      "بادي لاحم", "")
        if age_weeks <= 3:
            return AnimalRequirement(18.5, 21, 74, 9, 5, 5, 6, .9, .45,
                                      "نامي لاحم", "")
        return AnimalRequirement(17, 19.5, 75, 10, 5.5, 4.5, 6, .87, .43,
                                  "ناهي لاحم", "")
    if age_weeks <= 6:
        return AnimalRequirement(17, 20, 72, 10, 5.5, 4, 7, 1, .5,
                                  "بادي بياض", "")
    return AnimalRequirement(15.5, 18, 72, 11, 6, 4.2, 11.5, 3.8, .45,
                              "بياض إنتاجي", "")


def get_fish_requirements(species: str,
                            stage: str) -> AnimalRequirement:
    if "بادئ" in stage or "زريعة" in stage:
        return AnimalRequirement(32, 40, 72, 8, 4, 10, 11, 1.5, .9,
                                  f"{species} بادئ", "")
    return AnimalRequirement(22, 28, 68, 13, 7, 8, 9.5, .9, .65,
                              f"{species} تسمين", "")


def get_rabbit_requirements(t: str,
                              weight_kg: float = 4.0) -> AnimalRequirement:
    if t == "تسمين":
        return AnimalRequirement(15, 17, 65, 25, 15, 3, 8, .7, .35,
                                  "أرانب تسمين", "ADG 40")
    return AnimalRequirement(12, 14, 60, 30, 20, 2.5, 8.5, .6, .3,
                              "أرانب صيانة", "")


def requirement_to_standard(req: AnimalRequirement) -> Dict[str, float]:
    return {
        "CP": req.CP, "DP": req.DP, "SE": req.SE,
        "NDF": req.NDF, "ADF": req.ADF, "EE": req.EE,
        "ASH": req.ASH, "Ca": req.Ca, "P": req.P,
    }


# ═══════════════════════════════════════════════════════════════════════════
# الحسابات والتقييم
# ═══════════════════════════════════════════════════════════════════════════

def compute_formula_nutrients(formula: Dict[str, float]) -> Dict[str, float]:
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


def compute_total_oil_percentage(formula: Dict[str, float]) -> float:
    oils = set(get_oil_ingredients().keys())
    return sum(p for i, p in formula.items() if i in oils)


def evaluate_difference(pct_diff: float,
                         standard_value: Optional[float] = None) -> Dict:
    if standard_value is not None and standard_value == 0:
        if abs(pct_diff) < .001:
            return {"label": "🎯 مطابق", "color": "#0d5302",
                    "bg": "#c8e6c9", "score": 100}
        return {"label": "⚠️ صفر", "color": "#ef6c00",
                "bg": "#fff3e0", "score": 40}
    a = abs(pct_diff)
    if a <= .5:
        return {"label": "🎯 مطابق", "color": "#0d5302",
                "bg": "#c8e6c9", "score": 100}
    if a <= 2:
        return {"label": "🌟 ممتاز", "color": "#1b5e20",
                "bg": "#dcedc8", "score": 95}
    if a <= 5:
        return {"label": "✅ جيد جداً", "color": "#2e7d32",
                "bg": "#e8f5e9", "score": 85}
    if a <= 10:
        return {"label": "🟢 جيد", "color": "#558b2f",
                "bg": "#f1f8e9", "score": 75}
    if a <= 15:
        return {"label": "⭐ مقبول", "color": "#f9a825",
                "bg": "#fff8e1", "score": 65}
    if a <= 25:
        return {"label": "⚠️ بتحفظ", "color": "#ef6c00",
                "bg": "#fff3e0", "score": 50}
    if a <= 40:
        return {"label": "🟠 ضعيف", "color": "#e65100",
                "bg": "#ffe0b2", "score": 35}
    return {"label": "❌ غير مطابق", "color": "#c62828",
            "bg": "#ffebee", "score": 20}


def evaluate_quality_weighted(formula: Dict[str, float],
                                targets: Dict[str, float],
                                animal_type: str,
                                basis: str = "DP") -> Tuple[float, Dict]:
    actual = compute_formula_nutrients(formula)
    is_rum = animal_type in ("أبقار", "أغنام", "ماعز", "إبل")
    is_poultry = animal_type in ("دواجن", "سمان")

    weights = {}
    weights["DP" if basis == "DP" else "CP"] = 0.30
    if targets.get("SE"):
        weights["SE"] = 0.15
    if targets.get("NDF"):
        weights["NDF"] = 0.15 if is_rum else 0.10
    if targets.get("ADF"):
        weights["ADF"] = 0.10
    if targets.get("Ca"):
        weights["Ca"] = 0.10
    if targets.get("P"):
        weights["P"] = 0.10
    if is_poultry and targets.get("Lys"):
        weights["Lys"] = 0.05
    if is_poultry and targets.get("Met"):
        weights["Met"] = 0.05

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
            rs = (100 if 1.5 <= r <= 2.2
                  else 80 if 1.3 <= r < 1.5 or 2.2 < r <= 2.5
                  else 50 if 1.0 <= r < 1.3 or 2.5 < r <= 3.5
                  else 10)
        else:
            rs = (100 if 1.5 <= r <= 2.0
                  else 85 if 1.2 <= r < 1.5 or 2.0 < r <= 2.5
                  else 55 if 0.9 <= r < 1.2 or 2.5 < r <= 3.5
                  else 15)
        weighted += rs * 0.10
        total_w += 0.10

    return (weighted / total_w if total_w else 0.0), actual


def get_default_selections(animal_type: str, production_type: str,
                             requirement: Optional[AnimalRequirement] = None) -> Set[str]:
    d = {"ملح الطعام", "مضاد سموم فطرية"}
    if animal_type != "دواجن":
        d |= {"الحجر الجيري", "فوسفات ثنائي الكالسيوم"}
    if animal_type in ("أبقار", "أغنام", "ماعز", "إبل"):
        d.add("بيكربونات الصوديوم")
    if animal_type in ("دواجن", "سمان"):
        d.add("بريمكس بياض" if "بياض" in str(production_type)
              else "بريمكس تسمين دواجن")
    elif animal_type == "أبقار":
        d.add("بريمكس أبقار")
    elif animal_type in ("أغنام", "ماعز", "أرانب"):
        d.add("بريمكس مجترات")
    return d


def _normalize_ingredient_name(name: str) -> str:
    name = re.sub(r"\s+", " ", str(name).strip())
    lookup = _get_ingredient_lookup()
    if name in lookup:
        return name
    for lib in lookup.keys():
        if lib.lower() in name.lower() or name.lower() in lib.lower():
            return lib
    kw = {
        "ذره": "ذرة صفراء", "ذرة": "ذرة صفراء",
        "صويا": "كسب فول صويا 44%", "شعير": "شعير مطحون",
        "قمح": "قمح محلي", "نخاله": "نخالة قمح (ردة)",
        "نخالة": "نخالة قمح (ردة)", "ملح": "ملح الطعام",
        "حجر": "الحجر الجيري", "فوسفات": "فوسفات ثنائي الكالسيوم",
    }
    for k, v in kw.items():
        if k in name.lower():
            return v
    return name


# ═══════════════════════════════════════════════════════════════════════════
# محرك LP — 5 استراتيجيات
# ═══════════════════════════════════════════════════════════════════════════

def auto_formulate_smart(available_ingredients: List[str],
                           prices: Dict[str, float],
                           custom_standard: Dict[str, float],
                           standard_key: str = "",
                           basis: str = "DP",
                           min_quality: float = 70.0,
                           animal_type: str = "",
                           production_type: str = "") -> Dict:
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "SCIPY غير متوفرة"}

    available_ingredients = [_normalize_ingredient_name(i)
                              for i in available_ingredients]
    available_ingredients = list(dict.fromkeys(available_ingredients))

    lookup = _get_ingredient_lookup()
    ing_data = {i: lookup[i] for i in available_ingredients if i in lookup}
    valid = list(ing_data.keys())
    if len(valid) < 3:
        return {"success": False, "message": "اختر 3 مكونات على الأقل"}

    is_ruminant = animal_type in ("أبقار", "أغنام", "ماعز", "إبل")
    is_poultry = animal_type in ("دواجن", "سمان")
    n = len(valid)

    c = [prices.get(i, 300.0) for i in valid]
    rows = {}
    for nut in ["CP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P", "Lys", "Met"]:
        rows[nut] = [ing_data[i].get(nut, 0) for i in valid]
    rows["DP"] = [ing_data[i].get("CP", 0) * ing_data[i].get("DC", 0)
                   for i in valid]

    target_key = "DP" if basis == "DP" else "CP"
    target_protein = custom_standard.get(target_key, 15.0)
    target_ca = custom_standard.get("Ca", 0)
    target_p = custom_standard.get("P", 0)
    target_se = custom_standard.get("SE", 0)
    target_ndf = custom_standard.get("NDF", 0)
    target_adf = custom_standard.get("ADF", 0)
    target_lys = custom_standard.get("Lys", 0)
    target_met = custom_standard.get("Met", 0)

    limits = get_animal_limits(animal_type)
    bounds = [limits.get(i, (0.0, 100.0)) for i in valid]

    A_eq_base = [[1.0] * n, rows[target_key]]
    b_eq_base = [100.0, target_protein * 100.0]
    A_ub_base, b_ub_base = [], []

    if target_ca > 0 and target_p > 0:
        if is_poultry:
            ca_p_min, ca_p_max = 1.5, 2.2
        elif is_ruminant:
            ca_p_min, ca_p_max = 1.4, 2.5
        else:
            ca_p_min, ca_p_max = 1.5, 2.0
        A_ub_base.append([-rows["Ca"][i] + ca_p_min * rows["P"][i]
                          for i in range(n)])
        b_ub_base.append(0)
        A_ub_base.append([rows["Ca"][i] - ca_p_max * rows["P"][i]
                          for i in range(n)])
        b_ub_base.append(0)

    if target_se > 0:
        A_ub_base.append([-x for x in rows["SE"]])
        b_ub_base.append(-target_se * 0.92 * 100.0)
    if target_ndf > 0:
        if is_ruminant:
            A_ub_base.append([-x for x in rows["NDF"]])
            b_ub_base.append(-target_ndf * 0.85 * 100.0)
            A_ub_base.append(rows["NDF"])
            b_ub_base.append(target_ndf * 1.20 * 100.0)
        else:
            A_ub_base.append(rows["NDF"])
            b_ub_base.append(target_ndf * (1.10 if is_poultry else 1.15) * 100.0)
    if target_adf > 0:
        A_ub_base.append(rows["ADF"])
        mult = 1.30 if is_ruminant else (1.10 if is_poultry else 1.20)
        b_ub_base.append(target_adf * mult * 100.0)
    if target_lys > 0:
        A_ub_base.append([-x for x in rows["Lys"]])
        b_ub_base.append(-target_lys * 0.85 * 100.0)
    if target_met > 0:
        A_ub_base.append([-x for x in rows["Met"]])
        b_ub_base.append(-target_met * 0.85 * 100.0)

    oil_std = get_oil_standard(standard_key)
    oil_ind = [1.0 if i in get_oil_ingredients() else 0.0 for i in valid]
    if sum(oil_ind) > 0:
        A_ub_base.append(oil_ind)
        b_ub_base.append(oil_std["max"] * 100.0)

    strategies = [("دقيق", "eq"), ("مرن ±5%", "r05"),
                   ("مرن ±10%", "r10"), ("مرن ±15%", "r15"),
                   ("طوارئ", "none")]
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
            elif mode.startswith("r"):
                try:
                    tol = int(mode[1:]) / 100.0
                except ValueError:
                    tol = 0.10
                if target_ca > 0:
                    A_ub.append(rows["Ca"])
                    b_ub.append(target_ca * (1 + tol) * 100.0)
                    A_ub.append([-x for x in rows["Ca"]])
                    b_ub.append(-target_ca * (1 - tol) * 100.0)
                if target_p > 0:
                    A_ub.append(rows["P"])
                    b_ub.append(target_p * (1 + tol) * 100.0)
                    A_ub.append([-x for x in rows["P"]])
                    b_ub.append(-target_p * (1 - tol) * 100.0)

            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method="highs",
                          options={"presolve": True, "time_limit": 10})

            if res.success:
                formula = {valid[i]: res.x[i] for i in range(n)
                           if res.x[i] > 0.001}
                q, actual = evaluate_quality_weighted(
                    formula, custom_standard, animal_type, basis)
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
                if q >= 92:
                    break
        except Exception:
            continue

    if best:
        if not best["meets_standard"]:
            best["warning"] = (f"⚠️ الجودة {best_q:.1f}% < {min_quality}%")
        return best
    return {"success": False, "message": "تعذر إيجاد حل — جرّب مواد أكثر"}


# ═══════════════════════════════════════════════════════════════════════════
# 🆕 محرك NLP — التحسين غير الخطي (تعظيم الربح)
# ═══════════════════════════════════════════════════════════════════════════

SE_TO_ME_FACTOR = 42.0


def se_to_me(se_value: float) -> float:
    if not se_value or se_value <= 0:
        return 0.0
    return float(se_value) * SE_TO_ME_FACTOR


def biological_response(me: float, cp: float,
                         k_me: float = 2600.0,
                         k_cp: float = 12.0) -> float:
    r_me = me / (me + k_me) if me > 0 else 0.0
    r_cp = cp / (cp + k_cp) if cp > 0 else 0.0
    return r_me * r_cp


@dataclass
class NLPConstraints:
    cp_min: float = 18.0
    cp_max: float = 24.0
    me_min: float = 2900.0
    me_max: float = 3400.0
    ndf_min: float = 8.0
    ndf_max: float = 20.0
    ca_p_min: float = 1.5
    ca_p_max: float = 2.2


def solve_nlp_formulation(ingredient_names: List[str],
                            prices: Dict[str, float],
                            value_coef: float = 2.0,
                            constraints: Optional[NLPConstraints] = None) -> Dict:
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "scipy غير متوفرة"}
    if constraints is None:
        constraints = NLPConstraints()

    lookup = _get_ingredient_lookup()
    valid = [n for n in ingredient_names if n in lookup]
    if len(valid) < 2:
        return {"success": False, "message": "مطلوب مكونين على الأقل"}

    n = len(valid)
    c = np.array([prices.get(name, lookup[name].get("price", 300.0)) / 1000.0
                  for name in valid])
    me_arr = np.array([se_to_me(lookup[name].get("SE", 0)) for name in valid])
    cp_arr = np.array([lookup[name].get("CP", 0) for name in valid])
    ndf_arr = np.array([lookup[name].get("NDF", 0) for name in valid])
    ca_arr = np.array([lookup[name].get("Ca", 0) for name in valid])
    p_arr = np.array([lookup[name].get("P", 0) for name in valid])

    if me_arr.sum() == 0:
        return {"success": False, "message": "لا توجد بيانات SE"}

    def neg_profit(x):
        cost = float(np.dot(x, c))
        me = float(np.dot(x, me_arr))
        cp = float(np.dot(x, cp_arr))
        return -(value_coef * biological_response(me, cp) - cost)

    cons_list = [
        {"type": "eq", "fun": lambda x: np.sum(x) - 1.0},
        {"type": "ineq", "fun": lambda x: np.dot(x, cp_arr) - constraints.cp_min},
        {"type": "ineq", "fun": lambda x: constraints.cp_max - np.dot(x, cp_arr)},
        {"type": "ineq", "fun": lambda x: np.dot(x, me_arr) - constraints.me_min},
        {"type": "ineq", "fun": lambda x: constraints.me_max - np.dot(x, me_arr)},
        {"type": "ineq", "fun": lambda x: np.dot(x, ndf_arr) - constraints.ndf_min},
        {"type": "ineq", "fun": lambda x: constraints.ndf_max - np.dot(x, ndf_arr)},
        {"type": "ineq", "fun": lambda x: np.dot(x, ca_arr)
                                          - constraints.ca_p_min * np.dot(x, p_arr)},
        {"type": "ineq", "fun": lambda x: constraints.ca_p_max * np.dot(x, p_arr)
                                          - np.dot(x, ca_arr)},
    ]

    x0 = np.ones(n) / n
    try:
        res = scipy_minimize(neg_profit, x0, method="SLSQP",
                              bounds=[(0.0, 1.0)] * n,
                              constraints=cons_list,
                              options={"maxiter": 500, "ftol": 1e-9,
                                        "disp": False})
    except Exception as e:
        return {"success": False, "message": f"خطأ SLSQP: {e}"}

    if not res.success:
        return {"success": False, "message": f"SLSQP: {res.message}"}

    x = np.where(res.x < 1e-5, 0.0, res.x)
    s = x.sum()
    if s <= 0:
        return {"success": False, "message": "تكوين فارغ"}
    x = x / s

    formula = {valid[i]: float(x[i] * 100.0) for i in range(n) if x[i] > 1e-4}
    cost_per_kg = float(np.dot(x, c))
    me = float(np.dot(x, me_arr))
    cp = float(np.dot(x, cp_arr))
    ndf = float(np.dot(x, ndf_arr))
    ca = float(np.dot(x, ca_arr))
    p = float(np.dot(x, p_arr))
    ca_p = ca / p if p > 0 else 0.0

    violations = []
    if cp < constraints.cp_min - 0.01:
        violations.append(f"CP={cp:.2f}%<{constraints.cp_min}%")
    if me < constraints.me_min - 1:
        violations.append(f"ME={me:.0f}<{constraints.me_min}")
    if not (constraints.ndf_min - 0.1 <= ndf <= constraints.ndf_max + 0.1):
        violations.append(f"NDF={ndf:.1f}% خارج النطاق")
    if not (constraints.ca_p_min - 0.02 <= ca_p <= constraints.ca_p_max + 0.02):
        violations.append(f"Ca:P={ca_p:.2f} خارج النطاق")

    return {
        "success": True, "formula": formula,
        "ingredient_names": valid,
        "prices_used": {nm: prices.get(nm, lookup[nm].get("price", 300.0))
                         for nm in valid},
        "cost_per_kg": cost_per_kg, "cost_per_ton": cost_per_kg * 1000.0,
        "me": me, "cp": cp, "ndf": ndf, "ca": ca, "p": p, "ca_p": ca_p,
        "profit_score": -res.fun, "iterations": int(res.nit),
        "violations": violations, "value_coef": value_coef,
        "constraints": constraints, "message": res.message,
    }


# ═══════════════════════════════════════════════════════════════════════════
# 🆕 رسوم NLP الأربعة
# ═══════════════════════════════════════════════════════════════════════════

def build_profit_curve(ingredient_names, prices, value_coef,
                        constraints, me_points: int = 12):
    if not PLOTLY_AVAILABLE or not SCIPY_AVAILABLE:
        return None
    try:
        me_lo = max(constraints.me_min * 0.80, 1500)
        me_hi = min(constraints.me_max * 1.15, 4200)
        me_vals = np.linspace(me_lo, me_hi, me_points)
        profits, actual_me, labels = [], [], []
        for me_t in me_vals:
            c_local = NLPConstraints(
                cp_min=constraints.cp_min, cp_max=constraints.cp_max,
                me_min=float(me_t), me_max=constraints.me_max,
                ndf_min=constraints.ndf_min, ndf_max=constraints.ndf_max,
                ca_p_min=constraints.ca_p_min, ca_p_max=constraints.ca_p_max,
            )
            r = solve_nlp_formulation(ingredient_names, prices, value_coef, c_local)
            profits.append(r["profit_score"] if r["success"] else np.nan)
            actual_me.append(r["me"] if r["success"] else float(me_t))
            labels.append(f"ME={me_t:.0f}")
        if not any(not np.isnan(p) for p in profits):
            return None

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=actual_me, y=profits, mode="lines+markers",
            line=dict(color="#1b5e20", width=3),
            marker=dict(size=9, color="#43a047"),
            text=labels, connectgaps=True,
            hovertemplate="<b>%{text}</b><br>ME: %{x:.0f}<br>"
                          "Profit: %{y:.4f}<extra></extra>",
            name="الربح"))
        pa = np.array(profits, dtype=float)
        if np.any(~np.isnan(pa)):
            bi = int(np.nanargmax(pa))
            fig.add_trace(go.Scatter(
                x=[actual_me[bi]], y=[pa[bi]], mode="markers+text",
                marker=dict(size=20, color="#c62828", symbol="star"),
                text=[f"الأمثل: {pa[bi]:.3f}"], textposition="top center",
                textfont=dict(size=11, color="#c62828"), showlegend=False))
        fig.update_layout(
            title=dict(text="📈 منحنى الربحية — Profit vs ME",
                        font=dict(size=14, color="#1b5e20"), x=0.5),
            xaxis_title="ME (kcal/kg)", yaxis_title="Profit Score",
            height=420, paper_bgcolor="white", plot_bgcolor="#fafafa",
            margin=dict(l=60, r=20, t=60, b=60))
        return fig
    except Exception:
        return None


def build_3d_surface(ingredient_names, prices, value_coef, constraints,
                       me_range=(2500, 3600, 10),
                       cp_range=(15, 25, 10)):
    if not PLOTLY_AVAILABLE or not SCIPY_AVAILABLE:
        return None
    try:
        base = solve_nlp_formulation(ingredient_names, prices,
                                       value_coef, constraints)
        if not base["success"]:
            return None
        me_vals = np.linspace(*me_range)
        cp_vals = np.linspace(*cp_range)
        ME, CP = np.meshgrid(me_vals, cp_vals)
        a_cost = base["cost_per_kg"]
        Z = np.zeros_like(ME)
        for i in range(ME.shape[0]):
            for j in range(ME.shape[1]):
                r = biological_response(ME[i, j], CP[i, j])
                cost = a_cost + 0.00008 * (ME[i, j] - base["me"]) \
                              + 0.005 * (CP[i, j] - base["cp"])
                Z[i, j] = value_coef * r - cost

        fig = go.Figure(data=[go.Surface(
            x=ME, y=CP, z=Z, colorscale="RdYlGn",
            colorbar=dict(title="Profit"),
            hovertemplate="ME: %{x:.0f}<br>CP: %{y:.1f}%<br>"
                          "Profit: %{z:.4f}<extra></extra>")])
        fig.add_trace(go.Scatter3d(
            x=[base["me"]], y=[base["cp"]], z=[base["profit_score"]],
            mode="markers",
            marker=dict(size=8, color="#c62828", symbol="diamond"),
            name="الأمثل"))
        fig.update_layout(
            title=dict(text="🎯 سطح الربحية (ME × CP)",
                        font=dict(size=14, color="#1b5e20"), x=0.5),
            scene=dict(xaxis_title="ME (kcal/kg)",
                       yaxis_title="CP (%)", zaxis_title="Profit",
                       camera=dict(eye=dict(x=1.5, y=-1.5, z=1.2))),
            height=600, paper_bgcolor="white",
            margin=dict(l=0, r=0, t=60, b=0))
        return fig
    except Exception:
        return None


def build_tornado(ingredient_names, prices, value_coef, constraints,
                    perturbation=0.15):
    if not PLOTLY_AVAILABLE or not SCIPY_AVAILABLE:
        return None
    try:
        base = solve_nlp_formulation(ingredient_names, prices,
                                       value_coef, constraints)
        if not base["success"]:
            return None
        base_profit = base["profit_score"]
        impacts = []
        for name in ingredient_names:
            if name not in base["prices_used"]:
                continue
            p0 = base["prices_used"][name]
            p_up = dict(prices); p_up[name] = p0 * (1 + perturbation)
            r_up = solve_nlp_formulation(ingredient_names, p_up,
                                            value_coef, constraints)
            du = (r_up["profit_score"] - base_profit
                  if r_up["success"] else 0.0)
            p_dn = dict(prices); p_dn[name] = p0 * (1 - perturbation)
            r_dn = solve_nlp_formulation(ingredient_names, p_dn,
                                            value_coef, constraints)
            dd = (r_dn["profit_score"] - base_profit
                  if r_dn["success"] else 0.0)
            impacts.append({"name": name, "delta_up": du,
                             "delta_dn": dd,
                             "range": abs(du) + abs(dd)})
        if not impacts:
            return None
        impacts.sort(key=lambda x: x["range"])
        names = [i["name"] for i in impacts]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=names, x=[i["delta_up"] for i in impacts], orientation="h",
            name=f"سعر +{perturbation*100:.0f}%", marker_color="#c62828"))
        fig.add_trace(go.Bar(
            y=names, x=[i["delta_dn"] for i in impacts], orientation="h",
            name=f"سعر -{perturbation*100:.0f}%", marker_color="#2e7d32"))
        fig.add_vline(x=0, line=dict(color="#333", width=1.5))
        fig.update_layout(
            title=dict(text=f"🌪️ تحليل الحساسية ±{perturbation*100:.0f}%",
                        font=dict(size=14, color="#1b5e20"), x=0.5),
            xaxis_title="ΔProfit", barmode="overlay",
            height=max(400, len(names) * 45),
            paper_bgcolor="white", plot_bgcolor="#fafafa",
            margin=dict(l=140, r=20, t=60, b=60))
        return fig
    except Exception:
        return None


def build_pareto(ingredient_names, prices, value_coef, constraints,
                   points=15):
    if not PLOTLY_AVAILABLE or not SCIPY_AVAILABLE:
        return None
    try:
        profits, costs, labels = [], [], []
        for i in range(points):
            me_t = constraints.me_min + (
                constraints.me_max - constraints.me_min) * i / (points - 1)
            c_local = NLPConstraints(
                cp_min=constraints.cp_min, cp_max=constraints.cp_max,
                me_min=float(me_t), me_max=constraints.me_max,
                ndf_min=constraints.ndf_min, ndf_max=constraints.ndf_max,
                ca_p_min=constraints.ca_p_min, ca_p_max=constraints.ca_p_max)
            r = solve_nlp_formulation(ingredient_names, prices,
                                        value_coef, c_local)
            if r["success"]:
                profits.append(r["profit_score"])
                costs.append(r["cost_per_kg"])
                labels.append(f"ME={me_t:.0f}")
        if not profits:
            return None
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=costs, y=profits, mode="lines+markers+text",
            text=labels, textposition="top center",
            line=dict(color="#1976d2", width=3),
            marker=dict(size=10, color="#43a047"),
            name="جبهة باريتو"))
        pa = np.array(profits)
        ca = np.array(costs)
        bi = int(np.argmax(pa))
        fig.add_trace(go.Scatter(
            x=[ca[bi]], y=[pa[bi]], mode="markers+text",
            marker=dict(size=22, color="#c62828", symbol="star"),
            text=["الأمثل"], textposition="bottom center",
            textfont=dict(size=11, color="#c62828"),
            showlegend=False))
        fig.update_layout(
            title=dict(text="⚖️ جبهة باريتو — التكلفة vs الربح",
                        font=dict(size=14, color="#1b5e20"), x=0.5),
            xaxis_title="التكلفة ($/كجم)", yaxis_title="الربح",
            height=450, paper_bgcolor="white", plot_bgcolor="#fafafa",
            margin=dict(l=60, r=20, t=60, b=60))
        return fig
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# بدائل الحليب
# ═══════════════════════════════════════════════════════════════════════════

MILK_REPLACER_STANDARDS = {
    "عجول (Calves)": {
        "CP": 24, "Fat": 20, "Lactose": 45, "Ca": .85, "P": .7,
        "Lys": 2.2, "Met": .65, "notes": "NRC 2001",
        "source": "NRC Dairy Cattle", "Ca_P_optimal": (1.2, 1.5),
    },
    "حملان (Lambs)": {
        "CP": 24, "Fat": 24, "Lactose": 40, "Ca": .9, "P": .7,
        "Lys": 2.4, "Met": .7, "notes": "≥24% دهن",
        "source": "NRC Small Ruminants", "Ca_P_optimal": (1.2, 1.6),
    },
    "جديان (Goat Kids)": {
        "CP": 24, "Fat": 24, "Lactose": 42, "Ca": .9, "P": .7,
        "Lys": 2.3, "Met": .7, "notes": "توازن خاص",
        "source": "NRC Small Ruminants", "Ca_P_optimal": (1.2, 1.6),
    },
    "إبل (Camels)": {
        "CP": 26, "Fat": 28, "Lactose": 38, "Ca": .95, "P": .75,
        "Lys": 2.5, "Met": .8, "notes": "بروتين أعلى",
        "source": "FAO Camel", "Ca_P_optimal": (1.2, 1.5),
    },
    "أمهار (Foals)": {
        "CP": 22, "Fat": 18, "Lactose": 48, "Ca": 1.0, "P": .8,
        "Lys": 2.1, "Met": .6, "notes": "توازن خاص",
        "source": "NRC Horses", "Ca_P_optimal": (1.2, 1.4),
    },
}


MILK_REPLACER_INGREDIENTS = {
    "حليب مجفف منزوع الدسم": {"CP": 34, "Fat": 1, "Lactose": 52, "Ca": 1.3,
        "P": 1, "Lys": 2.7, "Met": .9, "price": 3200, "max": 60, "type": "بروتين"},
    "حليب مجفف كامل الدسم": {"CP": 26, "Fat": 28, "Lactose": 38, "Ca": .95,
        "P": .75, "Lys": 2.1, "Met": .65, "price": 3800, "max": 70,
        "type": "بروتين+دهن"},
    "شرش حليب مجفف": {"CP": 12, "Fat": 1.5, "Lactose": 75, "Ca": .9,
        "P": .75, "Lys": .9, "Met": .2, "price": 1800, "max": 35,
        "type": "كربوهيدرات"},
    "بروتين شرش WPC 80%": {"CP": 80, "Fat": 5, "Lactose": 8, "Ca": .5,
        "P": .3, "Lys": 7.5, "Met": 1.6, "price": 8500, "max": 25, "type": "بروتين"},
    "كازين": {"CP": 85, "Fat": 2, "Lactose": 2, "Ca": .1, "P": .5,
        "Lys": 7, "Met": 2.5, "price": 9000, "max": 20, "type": "بروتين"},
    "مركز بروتين صويا": {"CP": 66, "Fat": 1, "Lactose": 0, "Ca": .2,
        "P": .8, "Lys": 4.2, "Met": .9, "price": 2800, "max": 15, "type": "نباتي"},
    "زيت جوز الهند": {"CP": 0, "Fat": 100, "Lactose": 0, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 0, "price": 2200, "max": 15, "type": "دهن"},
    "زيت النخيل": {"CP": 0, "Fat": 100, "Lactose": 0, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 0, "price": 1200, "max": 15, "type": "دهن"},
    "مالتودكسترين": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 0, "price": 900, "max": 10, "type": "كربوهيدرات"},
    "لاكتوز نقي": {"CP": 0, "Fat": 0, "Lactose": 100, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 0, "price": 1400, "max": 25, "type": "كربوهيدرات"},
    "ليسين L-Lysine": {"CP": 94, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0,
        "Lys": 94, "Met": 0, "price": 4200, "max": 1, "type": "أميني"},
    "ميثيونين": {"CP": 58, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 58, "price": 5800, "max": .8, "type": "أميني"},
    "بريمكس فيتامينات": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 5, "P": 3,
        "Lys": 0, "Met": 0, "price": 6500, "max": 1, "type": "بريمكس"},
    "كالسيوم كربونات": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 38, "P": 0,
        "Lys": 0, "Met": 0, "price": 200, "max": 2.5, "type": "معدن"},
    "فوسفات ثنائي الكالسيوم": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 23,
        "P": 18, "Lys": 0, "Met": 0, "price": 1100, "max": 2.5, "type": "معدن"},
    "ملح طعام": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 0, "price": 150, "max": .5, "type": "معدن"},
}


def formulate_milk_replacer(animal: str, volume: float = 100.0,
                              selected: Optional[List[str]] = None) -> Dict:
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

    min_util_by_count = {3: 0.40, 4: 0.50, 5: 0.60, 6: 0.65, 7: 0.70, 8: 0.75}
    min_util = min_util_by_count.get(n, 0.75)

    c = [MILK_REPLACER_INGREDIENTS[i]["price"] for i in valid]
    cp = [MILK_REPLACER_INGREDIENTS[i]["CP"] for i in valid]
    fat = [MILK_REPLACER_INGREDIENTS[i]["Fat"] for i in valid]
    lac = [MILK_REPLACER_INGREDIENTS[i]["Lactose"] for i in valid]
    ca = [MILK_REPLACER_INGREDIENTS[i]["Ca"] for i in valid]
    p = [MILK_REPLACER_INGREDIENTS[i]["P"] for i in valid]
    lys = [MILK_REPLACER_INGREDIENTS[i]["Lys"] for i in valid]
    met = [MILK_REPLACER_INGREDIENTS[i]["Met"] for i in valid]
    base_bounds = [(0, MILK_REPLACER_INGREDIENTS[i].get("max", 100))
                   for i in valid]

    strategies = []
    s1_ub = [
        (lac, std["Lactose"] * 1.15 * 100),
        ([-x for x in lac], -std["Lactose"] * 0.85 * 100),
        ([-x for x in lys], -std["Lys"] * 0.70 * 100),
        ([-x for x in met], -std["Met"] * 0.70 * 100),
        ([-x for x in ca], -std["Ca"] * 0.85 * 100),
        ([-x for x in p], -std["P"] * 0.85 * 100),
    ]
    strategies.append(("S1: صارم",
                        [[1]*n, cp, fat],
                        [100, std["CP"]*100, std["Fat"]*100],
                        [u for u, _ in s1_ub],
                        [b for _, b in s1_ub]))
    s2_ub = [
        (lac, std["Lactose"] * 1.30 * 100),
        ([-x for x in lac], -std["Lactose"] * 0.70 * 100),
        ([-x for x in lys], -std["Lys"] * 0.70 * 100),
        ([-x for x in met], -std["Met"] * 0.70 * 100),
        ([-x for x in ca], -std["Ca"] * 0.85 * 100),
        ([-x for x in p], -std["P"] * 0.85 * 100),
    ]
    strategies.append(("S2: Lactose واسع",
                        [[1]*n, cp, fat],
                        [100, std["CP"]*100, std["Fat"]*100],
                        [u for u, _ in s2_ub],
                        [b for _, b in s2_ub]))
    s3_ub = s1_ub[:2] + s1_ub[4:]
    strategies.append(("S3: بلا Lys/Met",
                        [[1]*n, cp, fat],
                        [100, std["CP"]*100, std["Fat"]*100],
                        [u for u, _ in s3_ub],
                        [b for _, b in s3_ub]))
    s4_ub = s1_ub[:2]
    strategies.append(("S4: بلا معادن",
                        [[1]*n, cp, fat],
                        [100, std["CP"]*100, std["Fat"]*100],
                        [u for u, _ in s4_ub],
                        [b for _, b in s4_ub]))
    s5_ub = [
        (cp, std["CP"] * 1.05 * 100),
        ([-x for x in cp], -std["CP"] * 0.95 * 100),
        (fat, std["Fat"] * 1.05 * 100),
        ([-x for x in fat], -std["Fat"] * 0.95 * 100),
    ]
    strategies.append(("S5: CP/Fat ±5%",
                        [[1]*n], [100],
                        [u for u, _ in s5_ub],
                        [b for _, b in s5_ub]))
    s6_ub = [
        (cp, std["CP"] * 1.15 * 100),
        ([-x for x in cp], -std["CP"] * 0.85 * 100),
        (fat, std["Fat"] * 1.30 * 100),
        ([-x for x in fat], -std["Fat"] * 0.50 * 100),
    ]
    strategies.append(("S6: طوارئ",
                        [[1]*n], [100],
                        [u for u, _ in s6_ub],
                        [b for _, b in s6_ub]))

    best, best_eff = None, 0.0
    for label, A_eq, b_eq, A_ub, b_ub in strategies:
        try:
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=base_bounds, method="highs",
                          options={"presolve": True, "time_limit": 10})
            if not res.success:
                continue
            formula = {valid[i]: res.x[i] for i in range(n)
                       if res.x[i] > 0.001}
            used = sum(1 for v in formula.values() if v > 0.5)
            used_pct = used / n * 100
            actual = {k: 0.0 for k in
                      ["CP", "Fat", "Lactose", "Ca", "P", "Lys", "Met"]}
            for ing, pct in formula.items():
                d = MILK_REPLACER_INGREDIENTS[ing]
                for k in actual:
                    actual[k] += pct / 100 * d.get(k, 0)
            scores = []
            for k in ["CP", "Fat", "Lactose", "Ca", "P", "Lys", "Met"]:
                t = std.get(k, 0)
                if t <= 0:
                    continue
                diff = abs(actual[k] - t) / t * 100
                scores.append(100 if diff <= 2 else 92 if diff <= 5
                              else 78 if diff <= 10 else 62 if diff <= 15
                              else 45 if diff <= 25 else max(0, 100 - diff))
            ca_p = actual["Ca"] / actual["P"] if actual["P"] > 0 else 0
            cp_min, cp_max = std.get("Ca_P_optimal", (1.2, 1.5))
            scores.append(100 if cp_min <= ca_p <= cp_max
                          else 75 if cp_min * 0.8 <= ca_p <= cp_max * 1.3
                          else 30)
            quality = sum(scores) / len(scores) if scores else 0
            util = (1.0 if used_pct >= min_util * 100
                    else used_pct / (min_util * 100))
            eff = quality * (0.7 + 0.3 * util)
            if eff > best_eff:
                best_eff = eff
                best = {
                    "formula": formula, "cost": res.fun / 100,
                    "cost_per_kg": res.fun / 10000,
                    "used_count": used, "used_pct": used_pct,
                    "actual": actual, "quality_score": quality,
                    "ca_p_ratio": ca_p, "strategy": label,
                }
            if quality >= 90 and used_pct >= min_util * 100:
                break
        except Exception:
            continue
    if not best:
        return {"success": False, "message": "لا يوجد حل"}

    warning = None
    if best["used_pct"] < min_util * 100:
        warning = (f"⚠️ استُخدم {best['used_count']}/{n} مادة "
                   f"({best['used_pct']:.0f}% < {min_util*100:.0f}%)")

    return {
        "success": True, "formula": best["formula"],
        "cost_per_100kg": best["cost"], "cost_per_kg": best["cost_per_kg"],
        "standard": std, "actual": best["actual"],
        "animal": animal, "volume": volume,
        "used_count": best["used_count"], "used_pct": best["used_pct"],
        "quality_score": best["quality_score"],
        "ca_p_ratio": best["ca_p_ratio"],
        "strategy": best["strategy"], "warning": warning,
        "targets": {k: std.get(k, 0) for k in
                    ["CP", "Fat", "Lactose", "Ca", "P", "Lys", "Met"]},
    }


# ═══════════════════════════════════════════════════════════════════════════
# OCR
# ═══════════════════════════════════════════════════════════════════════════

def _preprocess_image_variants(img):
    variants = []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    variants.append(clahe.apply(gray))
    _, otsu = cv2.threshold(gray, 0, 255,
                            cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(otsu)
    variants.append(cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 5))
    variants.append(cv2.fastNlMeansDenoising(clahe.apply(gray), None, 10, 7, 21))
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    variants.append(cv2.filter2D(gray, -1, kernel))
    variants.append(cv2.bitwise_not(gray))
    return variants


def _parse_ingredients_from_text(full_text):
    fixes = {
        "٥": "5", "٦": "6", "٧": "7", "٨": "8", "٩": "9",
        "٠": "0", "١": "1", "٢": "2", "٣": "3", "٤": "4",
        "٪": "%",
    }
    text = full_text
    for old, new in fixes.items():
        text = text.replace(old, new)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\b[Il|]\b", "1", text)

    patterns = [
        r"([\u0600-\u06FFa-zA-Z\s\(\)\-]{3,40}?)[\s:\-=:\.]+\s*(\d{1,3}\.?\d{0,2})\s*%",
        r"(\d{1,3}\.?\d{0,2})\s*%[\s:\-=:\.]+\s*([\u0600-\u06FFa-zA-Z\s\(\)\-]{3,40})",
        r"([\u0600-\u06FFa-zA-Z\s]{3,30}?)[\s:\-=]+\s*(\d{1,4})\s*(?:كجم|كج|kg)",
    ]

    ingredients = {}
    for line in text.split("\n"):
        line = line.strip()
        if len(line) < 4:
            continue
        for pat in patterns:
            for m in re.finditer(pat, line, re.MULTILINE):
                g = m.groups()
                if len(g) < 2:
                    continue
                try:
                    val, name = float(g[1]), g[0].strip()
                except ValueError:
                    try:
                        val, name = float(g[0]), g[1].strip()
                    except ValueError:
                        continue
                if 0.1 <= val <= 100 and len(name) > 2:
                    matched = match_ingredient_name(name)
                    if matched and matched not in ingredients:
                        ingredients[matched] = round(val, 2)
    return ingredients


def match_ingredient_name(text):
    if not text:
        return None
    tl = text.strip().lower()
    for cat in BIG_FEEDS_LIBRARY.values():
        for name in cat.keys():
            if name.lower() in tl or tl in name.lower():
                return name
    kw = {
        "ذرة": "ذرة صفراء", "ذره": "ذرة صفراء",
        "صويا": "كسب فول صويا 44%", "شعير": "شعير مطحون",
        "قمح": "قمح محلي", "نخالة": "نخالة قمح (ردة)",
        "ملح": "ملح الطعام", "حجر": "الحجر الجيري",
        "فوسفات": "فوسفات ثنائي الكالسيوم",
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
        if max(h, w) < 1500:
            scale = 1800 / max(h, w)
            img = cv2.resize(img, None, fx=scale, fy=scale,
                              interpolation=cv2.INTER_CUBIC)
        variants = _preprocess_image_variants(img)
        psm_modes = ["--oem 3 --psm 6", "--oem 3 --psm 11",
                     "--oem 3 --psm 12"]
        all_texts = []
        for variant in variants:
            for psm in psm_modes:
                try:
                    txt = pytesseract.image_to_string(variant,
                                                       lang="ara+eng",
                                                       config=psm)
                    if txt and len(txt) > 5:
                        all_texts.append(txt)
                except Exception:
                    continue
        if not all_texts:
            return {"success": False, "message": "لم يتم استخراج نص"}
        full_text = "\n".join(set(all_texts))
        ingredients = _parse_ingredients_from_text(full_text)
        return {
            "success": True, "ingredients": ingredients,
            "raw_text": full_text, "count": len(ingredients),
            "total": sum(ingredients.values()),
            "variants_tried": len(variants) * len(psm_modes),
        }
    except Exception as e:
        return {"success": False, "message": f"خطأ: {e}"}


# ═══════════════════════════════════════════════════════════════════════════
# الرسوم البيانية (matplotlib)
# ═══════════════════════════════════════════════════════════════════════════

def create_colorful_bar_chart(standard, actual, keys=None):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        if keys is None:
            keys = ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH"]
        nuts = [n for n in keys if n in standard and standard[n] > 0]
        if not nuts:
            return None
        fig, ax = plt.subplots(figsize=(9, 4.5))
        x = np.arange(len(nuts))
        width = 0.35
        ax.bar(x - width/2, [standard[n] for n in nuts], width,
                label="المعيار", color="#1976d2", edgecolor="#0d47a1")
        ax.bar(x + width/2, [actual.get(n, 0) for n in nuts], width,
                label="المحسوب", color="#43a047", edgecolor="#1b5e20")
        ax.set_xticks(x); ax.set_xticklabels(nuts, fontsize=10)
        ax.set_title("مقارنة العناصر", fontsize=13, fontweight="bold",
                     color="#1b5e20")
        ax.legend(); ax.grid(axis="y", alpha=0.3, linestyle="--")
        ax.set_facecolor("#fafafa")
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                    facecolor="white")
        plt.close(); buf.seek(0)
        return buf
    except Exception:
        return None


def create_pie_chart(formula):
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2:
        return None
    try:
        colors = ["#e53935", "#8e24aa", "#3949ab", "#1e88e5", "#00897b",
                  "#43a047", "#7cb342", "#fdd835", "#fb8c00", "#6d4c41"]
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.pie(list(formula.values()), autopct="%1.1f%%",
                colors=colors[:len(formula)], startangle=90,
                pctdistance=0.75,
                wedgeprops=dict(edgecolor="white", linewidth=2))
        ax.legend(list(formula.keys()), loc="center left",
                   bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)
        ax.set_title("توزيع المكونات", fontsize=13, fontweight="bold",
                     color="#1b5e20")
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                    facecolor="white")
        plt.close(); buf.seek(0)
        return buf
    except Exception:
        return None


def create_gauge_chart(score):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect="equal"))
        colors = ["#c62828", "#ef6c00", "#f9a825", "#7cb342", "#43a047", "#1b5e20"]
        for i, c in enumerate(colors):
            t1 = 180 - (i * 30); t2 = 180 - ((i + 1) * 30)
            ax.add_patch(Wedge((0, 0), 1, t2, t1, width=0.3,
                                facecolor=c, edgecolor="white", linewidth=2))
        angle = 180 - (score / 100) * 180
        rad = np.radians(angle)
        ax.plot([0, 0.85 * np.cos(rad)], [0, 0.85 * np.sin(rad)],
                color="#1a1a1a", linewidth=3, zorder=10)
        ax.add_patch(Circle((0, 0), 0.08, color="#1a1a1a", zorder=11))
        ax.text(0, -0.25, f"{score:.0f}%", ha="center", fontsize=20,
                fontweight="bold", color="#1b5e20")
        ax.set_xlim(-1.2, 1.2); ax.set_ylim(-0.7, 1.2); ax.axis("off")
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                    facecolor="white")
        plt.close(); buf.seek(0)
        return buf
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# PDF Generator (الإصلاحات هنا: ImageReader بدل RLImage)
# ═══════════════════════════════════════════════════════════════════════════

class PDFGenerator:
    def __init__(self):
        self.font_name = font_mgr.font_name
        self.logo_path = None
        for lp in LOGO_OPTIONS + PHOTO_OPTIONS:
            if os.path.exists(lp):
                self.logo_path = lp
                break

    def _ar(self, t):
        return ar(t) if t else ""

    def _draw_stamp(self, canvas_obj, doc):
        try:
            w, h = doc.pagesize
            sx, sy = w - 105, 145
            canvas_obj.setStrokeColor(HexColor("#c62828"))
            canvas_obj.setLineWidth(3.5)
            canvas_obj.circle(sx, sy, 72, stroke=1, fill=0)
            canvas_obj.setLineWidth(2.0)
            canvas_obj.circle(sx, sy, 64, stroke=1, fill=0)
            canvas_obj.setFillColor(HexColor("#c62828"))
            canvas_obj.setFont(self.font_name, 9.5)
            canvas_obj.drawCentredString(sx, sy + 42, self._ar("تاور نولجي"))
            canvas_obj.drawCentredString(sx, sy + 30, self._ar("Tawor Nology"))
            canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(sx, sy + 16, self._ar("د. عبدالقادر"))
            canvas_obj.drawCentredString(sx, sy + 4, self._ar("إسماعيل تاور"))
            canvas_obj.setFont(self.font_name, 6.5)
            canvas_obj.drawCentredString(sx, sy - 12, self._ar("اختصاصي تغذية"))
            canvas_obj.drawCentredString(sx, sy - 24, self._ar("معتمد"))
            canvas_obj.drawCentredString(sx, sy - 36, self._ar("© 2026"))
        except Exception:
            pass

    def _draw_page(self, canvas_obj, doc):
        try:
            canvas_obj.saveState()
            w, h = doc.pagesize
            canvas_obj.setFillColor(HexColor("#1b5e20"))
            canvas_obj.rect(0, h - 90, w, 90, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor("#d4af37"))
            canvas_obj.rect(0, h - 95, w, 5, fill=1, stroke=0)
            try:
                if self.logo_path:
                    canvas_obj.drawImage(self.logo_path, 30, h - 78,
                                          width=60, height=60,
                                          preserveAspectRatio=True,
                                          anchor="sw", mask="auto")
            except Exception:
                pass
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 22)
            canvas_obj.drawCentredString(w/2, h - 38,
                                          self._ar("تاور نولجي  Tawor Nology"))
            canvas_obj.setFont(self.font_name, 12)
            canvas_obj.setFillColor(HexColor("#e8f5e9"))
            canvas_obj.drawCentredString(w/2, h - 58,
                                          self._ar("للإنتاج الحيواني"))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.setFillColor(HexColor("#d4af37"))
            canvas_obj.drawCentredString(w/2, h - 76,
                                          self._ar(f"إشراف: {SUPERVISOR}"))
            canvas_obj.setFillColor(HexColor("#1b5e20"))
            canvas_obj.rect(0, 42, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor("#ffeb3b"))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.drawCentredString(w/2, 68,
                                          self._ar(f"🤲 {DUA_SHORT} 🤲"))
            canvas_obj.setFillColor(HexColor("#1b5e20"))
            canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(w/2, 27,
                                          self._ar("Tawor Nology © 2026"))
            canvas_obj.setFont(self.font_name, 7)
            canvas_obj.drawCentredString(w/2, 12,
                                          self._ar(f"صفحة {canvas_obj.getPageNumber()}"))
            try:
                if QRCODE_AVAILABLE:
                    qr = qrcode.QRCode(version=1, box_size=3, border=1)
                    qr.add_data(PLATFORM_URL); qr.make(fit=True)
                    qi = qr.make_image(fill_color="#1b5e20",
                                        back_color="white")
                    qbuf = io.BytesIO()
                    qi.save(qbuf, format="PNG"); qbuf.seek(0)
                    canvas_obj.drawImage(ImageReader(qbuf), w/2 - 20, 46,
                                          width=40, height=40)
            except Exception:
                pass
            self._draw_stamp(canvas_obj, doc)
            canvas_obj.restoreState()
        except Exception:
            pass

    def generate_report(self, formula, requirement, animal_type, breed, cost,
                        city, local_cost, local_sym, requester_name="",
                        protein_basis="DP", standard_key="",
                        include_charts=True, quality_score=0.0):
        if not REPORTLAB_AVAILABLE:
            return None
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
                                leftMargin=40, topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color="#1a1a1a"):
            return Paragraph(ar(text), ParagraphStyle(
                "s", fontName=self.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))

        story.append(P("تقرير فني رسمي — تركيب علفة", 20, TA_CENTER, "#1b5e20"))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
                                color=HexColor("#d4af37")))
        story.append(Spacer(1, 12))

        client = [
            [ar("👤 طالب الخدمة:"), ar(requester_name or "—")],
            [ar("📍 الموقع:"), ar(city)],
            [ar("🐾 الفصيل:"), ar(f"{animal_type} — {breed}")],
            [ar("🧬 الأساس:"), ar(protein_basis)],
            [ar("📅 التاريخ:"), datetime.now().strftime("%Y-%m-%d")],
        ]
        ct = Table(client, colWidths=[150, 340])
        ct.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), HexColor("#e8f5e9")),
            ("BOX", (0, 0), (-1, -1), 1.5, HexColor("#2e7d32")),
            ("INNERGRID", (0, 0), (-1, -1), 0.6, HexColor("#c8e6c9")),
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, -1), self.font_name),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ]))
        story.append(ct)
        story.append(Spacer(1, 15))

        std_vals = requirement_to_standard(requirement)
        calc_vals = compute_formula_nutrients(formula)
        qd = [[ar("الجودة"), ar("الحالة")],
              [f"{quality_score:.1f}%",
               ar("✅ ناجح" if quality_score >= 70 else "⚠️ يحتاج تحسين")]]
        qt = Table(qd, colWidths=[200, 250])
        qt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1565c0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("BACKGROUND", (0, 1), (-1, -1),
             HexColor("#e8f5e9" if quality_score >= 70 else "#ffebee")),
            ("GRID", (0, 0), (-1, -1), 1, HexColor("#1976d2")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), self.font_name),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(qt)
        story.append(Spacer(1, 15))

        labels = {"CP": "بروتين", "DP": "مهضوم", "SE": "SE",
                  "NDF": "NDF", "ADF": "ADF", "EE": "دهن",
                  "ASH": "رماد", "Ca": "Ca", "P": "P"}
        data = [[ar(x) for x in
                 ["العنصر", "المعيار", "المحسوب", "الفرق", "%", "التقييم"]]]
        cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1b5e20")),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), self.font_name),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 1, HexColor("#9e9e9e")),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]
        row = 1
        for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
            if k not in std_vals or std_vals[k] == 0:
                continue
            sv, cv = std_vals[k], calc_vals.get(k, 0)
            diff = cv - sv
            pct = (diff / sv * 100) if sv else 0
            ev = evaluate_difference(pct, standard_value=sv)
            data.append([ar(labels[k]), f"{sv:.2f}", f"{cv:.2f}",
                          f"{diff:+.3f}", f"{pct:+.2f}%", ar(ev["label"])])
            cmds.append(("BACKGROUND", (0, row), (-1, row),
                          HexColor(ev["bg"])))
            row += 1
        t = Table(data, colWidths=[100, 70, 70, 70, 70, 105])
        t.setStyle(TableStyle(cmds))
        story.append(t)
        story.append(Spacer(1, 15))

        if include_charts:
            story.append(PageBreak())
            story.append(P("📈 الرسوم البيانية", 14, "#1b5e20"))
            story.append(Spacer(1, 10))
            for chart_fn, args in [
                (create_colorful_bar_chart, (std_vals, calc_vals)),
                (create_pie_chart, (formula,)),
            ]:
                try:
                    c = chart_fn(*args)
                    if c:
                        story.append(RLImage(c, width=450, height=250))
                        story.append(Spacer(1, 10))
                except Exception:
                    pass
            try:
                g = create_gauge_chart(quality_score)
                if g:
                    story.append(RLImage(g, width=200, height=200))
            except Exception:
                pass

        story.append(PageBreak())
        story.append(P("💰 التكاليف", 14, "#1b5e20"))
        story.append(Spacer(1, 8))
        cost_data = [
            [ar("البند"), ar("القيمة")],
            [ar("التكلفة/طن"), f"${cost:.2f}"],
            [ar(f"التكلفة ({local_sym})"), f"{local_cost:,.2f}"],
        ]
        tc = Table(cost_data, colWidths=[280, 210])
        tc.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1b5e20")),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("GRID", (0, 0), (-1, -1), 1, HexColor("#2e7d32")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), self.font_name),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(tc)
        story.append(Spacer(1, 18))

        if formula:
            story.append(P("🌾 المكونات للطن", 14, "#1b5e20"))
            story.append(Spacer(1, 8))
            ing_data = [[ar("المكون"), ar("%"), ar("كجم/طن")]]
            for ing, pct in formula.items():
                ing_data.append([ar(ing), f"{pct:.2f}%", f"{pct * 10:.1f}"])
            ti = Table(ing_data, colWidths=[270, 110, 110])
            ti.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2e7d32")),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), self.font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 1, HexColor("#bdbdbd")),
            ]))
            story.append(ti)
            story.append(Spacer(1, 25))
            sign = [[ar("توقيع الطالب"), ar("توقيع المختص")],
                    [ar("...................."), ar(SUPERVISOR)],
                    [ar("التاريخ: ..../..../......"), ar(SUPERVISOR_TITLE)]]
            ts = Table(sign, colWidths=[245, 245])
            ts.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), self.font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOX", (0, 0), (-1, -1), 1, HexColor("#bdbdbd")),
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#e8f5e9")),
            ]))
            story.append(ts)

        doc.build(story, onFirstPage=self._draw_page,
                  onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()


pdf_gen = PDFGenerator()


# ═══════════════════════════════════════════════════════════════════════════
# 🆕 PDF الخاص بـ NLP
# ═══════════════════════════════════════════════════════════════════════════

def generate_nlp_pdf_report(result: Dict,
                              charts: Optional[Dict] = None,
                              requester: str = "") -> Optional[bytes]:
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40,
                                leftMargin=40, topMargin=115, bottomMargin=145)
        elements = []

        def P(text, size=11, align=TA_RIGHT, color="#1a1a1a"):
            return Paragraph(ar(text), ParagraphStyle(
                "p", fontName=font_mgr.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))

        elements.append(P("تقرير التركيبة العلفية المثلى", 22, TA_CENTER, "#1b5e20"))
        elements.append(P("التحسين غير الخطي (NLP) — تعظيم الربح",
                          14, TA_CENTER, "#1565c0"))
        elements.append(Spacer(1, 6))
        elements.append(HRFlowable(width="100%", thickness=2.5,
                                    color=HexColor("#d4af37")))
        elements.append(Spacer(1, 14))

        info = [
            [ar("👤 طالب الخدمة:"), ar(requester or "—")],
            [ar("📅 التاريخ:"), datetime.now().strftime("%Y-%m-%d %H:%M")],
            [ar("🔢 التكرارات:"), str(result.get("iterations", 0))],
            [ar("⚠️ انتهاكات:"), ar("لا يوجد" if not result.get("violations")
                                     else " | ".join(result["violations"]))],
        ]
        t_info = Table(info, colWidths=[130, 350])
        t_info.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), HexColor("#e8f5e9")),
            ("BOX", (0, 0), (-1, -1), 1.5, HexColor("#2e7d32")),
            ("INNERGRID", (0, 0), (-1, -1), 0.6, HexColor("#c8e6c9")),
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, -1), font_mgr.font_name),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))
        elements.append(t_info)
        elements.append(Spacer(1, 14))

        elements.append(P("📊 الملخص الاقتصادي والفني", 14, TA_RIGHT, "#1b5e20"))
        elements.append(Spacer(1, 8))
        summary_data = [
            [ar("المؤشر"), ar("القيمة")],
            [ar("التكلفة / كجم"), f"${result['cost_per_kg']:.4f}"],
            [ar("التكلفة / طن"), f"${result['cost_per_ton']:.2f}"],
            [ar("الطاقة الممثلة (ME)"), f"{result['me']:.1f} kcal/kg"],
            [ar("البروتين الخام (CP)"), f"{result['cp']:.2f} %"],
            [ar("الألياف NDF"), f"{result['ndf']:.2f} %"],
            [ar("نسبة Ca:P"), f"{result['ca_p']:.2f}"],
            [ar("صافي العائد"), f"{result['profit_score']:.4f}"],
        ]
        t_sum = Table(summary_data, colWidths=[260, 220])
        t_sum.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1b5e20")),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), font_mgr.font_name),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#bdbdbd")),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))
        elements.append(t_sum)
        elements.append(Spacer(1, 14))

        elements.append(P("🌾 توزيع نسب المواد العلفية", 14, TA_RIGHT, "#1b5e20"))
        elements.append(Spacer(1, 8))
        prices_used = result.get("prices_used", {})
        ing_data = [[ar("المكون"), ar("النسبة %"), ar("كجم / طن"),
                      ar("التكلفة $")]]
        for name, pct in result["formula"].items():
            price = prices_used.get(name, 300.0)
            cost_line = pct * price / 100.0
            ing_data.append([ar(name), f"{pct:.2f}%",
                              f"{pct*10:.1f}", f"${cost_line:.2f}"])
        total_feed_cost = sum(pct * prices_used.get(n, 300.0) / 100.0
                              for n, pct in result["formula"].items())
        ing_data.append([ar("الإجمالي"), "100%", "1000.0",
                          f"${total_feed_cost:.2f}"])
        t_ing = Table(ing_data, colWidths=[180, 90, 90, 90])
        t_ing.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2e7d32")),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), font_mgr.font_name),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#bdbdbd")),
            ("BACKGROUND", (0, -1), (-1, -1), HexColor("#ffe082")),
        ]))
        elements.append(t_ing)
        elements.append(Spacer(1, 14))

        # الرسوم
        if charts:
            for title, fig in charts.items():
                if fig is None:
                    continue
                try:
                    png = fig.to_image(format="png", width=850, height=450,
                                        scale=2)
                    img_buf = io.BytesIO(png); img_buf.seek(0)
                    elements.append(PageBreak())
                    elements.append(P(title, 14, TA_RIGHT, "#1b5e20"))
                    elements.append(Spacer(1, 8))
                    elements.append(RLImage(img_buf, width=470, height=250))
                except Exception:
                    pass  # kaleido غير مثبت

        elements.append(Spacer(1, 20))
        elements.append(P(SUPERVISOR, 16, TA_CENTER, "#c62828"))
        elements.append(P(SUPERVISOR_TITLE, 11, TA_CENTER, "#1b5e20"))

        doc.build(elements, onFirstPage=pdf_gen._draw_page,
                  onLaterPages=pdf_gen._draw_page)
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# الجلسة والصور
# ═══════════════════════════════════════════════════════════════════════════

DEFAULTS = {
    "approved": False, "user_role": None,
    "active_formula": {}, "computed_ton_cost": 280.0,
    "inventory": {}, "broiler_farms": {},
    "last_formulation_result": None, "last_formulation_context": None,
    "last_ocr_result": None, "last_ocr_nutrients": None,
    "owner_attempts": 0, "owner_lock_until": 0.0,
    "invoices": [], "formulation_history": [],
    "nlp_result": None, "nlp_charts": {},
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state["inventory"]:
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing in cat:
            st.session_state["inventory"][ing] = {
                "quantity": 25.0, "min_threshold": 5.0, "unit": "طن",
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
.main-box {
    background: rgba(255,255,255,0.92); padding: 32px; border-radius: 22px;
    box-shadow: 0 15px 45px rgba(0,0,0,0.15); margin-bottom: 70px;
    backdrop-filter: blur(12px);
}
.dua-main-box {
    background: linear-gradient(135deg, #0d3011, #1b5e20, #2e7d32, #1b5e20);
    padding: 34px 28px; border-radius: 22px; border: 4px solid #d4af37;
    direction: rtl; text-align: center; margin: 25px 0;
}
.dua-main-box * { color: white !important; }
.dua-main-box h3 { color: #d4af37 !important; font-size: 1.9rem; }
.dua-main-box .names {
    background: linear-gradient(90deg, rgba(212,175,55,0.15),
                rgba(212,175,55,0.35), rgba(212,175,55,0.15));
    font-size: 1.65rem; font-weight: 900; color: #ffeb3b !important;
    margin: 20px 0; padding: 16px 30px; border: 2px solid #d4af37;
    border-radius: 16px; font-family: 'Amiri', serif !important;
}
.dua-main-box p.quran {
    font-family: 'Amiri', serif !important; font-size: 1.2rem;
    color: #d4af37 !important; margin-top: 22px;
    padding: 18px 25px; background: rgba(0,0,0,0.25);
    border-radius: 12px;
}
.visitor-dua-banner {
    background: linear-gradient(135deg, #fff8e1, #ffecb3, #ffe082);
    padding: 20px 28px; border-radius: 16px; border: 3px solid #d4af37;
    margin: 22px 0; direction: rtl; text-align: center;
}
.visitor-dua-banner b { color: #c62828 !important; font-family: 'Amiri' !important; }
.dua-fixed-banner {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32, #1b5e20);
    color: white !important; padding: 12px 20px; z-index: 9998;
    text-align: center; border-top: 3px solid #d4af37;
    font-family: 'Amiri' !important; font-size: 1.05rem;
    font-weight: bold;
}
.dua-fixed-banner * { color: #ffeb3b !important; font-family: 'Amiri' !important; }
.section-title {
    color: #1b5e20 !important; border-right: 6px solid #2e7d32;
    padding: 12px 18px; text-align: right; font-size: 1.5rem;
    font-weight: 900; margin-top: 30px; margin-bottom: 20px;
    background: linear-gradient(to left, rgba(46,125,50,0.15), transparent);
    border-radius: 10px;
}
.formula-item {
    background: linear-gradient(135deg, #ffffff, #e8f5e9);
    padding: 15px 20px; border-radius: 10px; margin-bottom: 10px;
    font-weight: 700; color: #1b5e20 !important;
    border-right: 5px solid #2e7d32; text-align: right;
}
.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px; border-radius: 16px;
    border-right: 5px solid #2e7d32; margin-bottom: 20px;
    direction: rtl; text-align: right;
}
.physio-card {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 18px 24px; border-radius: 14px;
    border-right: 6px solid #1565c0; margin-bottom: 20px;
    direction: rtl; text-align: right;
}
.quality-good {
    background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
    padding: 24px; border-radius: 22px;
    border-right: 8px solid #1b5e20; margin: 18px 0;
    direction: rtl; text-align: right;
}
.quality-bad {
    background: linear-gradient(135deg, #ffcdd2, #ef9a9a);
    padding: 24px; border-radius: 22px;
    border-right: 8px solid #c62828; margin: 18px 0;
    direction: rtl; text-align: right;
}
.profile-img-style {
    width: 150px; height: 150px; border-radius: 50%;
    object-fit: cover; border: 4px solid #d4af37;
    display: block; margin: 0 auto;
}
.stButton > button {
    color: #1a1a1a !important;
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9) !important;
    border: 1.5px solid #2e7d32 !important;
    font-weight: 700 !important; border-radius: 10px !important;
}
.mini-signature {
    position: fixed; left: 20px; bottom: 70px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important; padding: 9px 22px;
    font-size: 0.85rem; border-radius: 25px; z-index: 9997;
    direction: rtl; border: 2px solid #d4af37; font-weight: 700;
}
.mini-signature * { color: white !important; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #2e7d32, #1b5e20) !important;
}
.stTabs [aria-selected="true"] * { color: white !important; }
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff, #f1f8e9);
    padding: 14px 18px; border-radius: 16px;
    border-right: 4px solid #2e7d32;
}
[data-testid="stMetricValue"] { color: #1b5e20 !important; font-weight: 900 !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# بوابة الدخول
# ═══════════════════════════════════════════════════════════════════════════

if st.session_state.get("approved", False) and not _session_valid():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.error("⚠️ جلسة غير صالحة — أعد الدخول")
    st.stop()

if not st.session_state.get("approved", False):
    st.markdown('<div class="main-box" style="max-width:780px; margin:30px auto; direction:rtl;">',
                unsafe_allow_html=True)

    st.markdown(f"""
    <div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <p style="font-size:1.1rem; color:#a5d6a7 !important;">
        نبدأ باسم الله، ونسألُه أن يتقبّلَ هذا العملَ صدقةً جاريةً عن:
        </p>
        <div class="names">🕊️ {DUA_SHORT} 🕊️</div>
        <p class="quran">{DUA_QURAN}</p>
        <p class="quran">{DUA_VERSE}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-top:2px solid #d4af37; margin:25px 0;'>",
                unsafe_allow_html=True)

    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        if img_base64:
            st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">',
                        unsafe_allow_html=True)
    with col_title:
        st.markdown(f"<h2 style='color:#2E7D32; text-align:right;'>🌾 {APP_NAME}</h2>",
                    unsafe_allow_html=True)
        st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.1rem;'>{APP_TAGLINE}</p>",
                    unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#c62828; text-align:right;'>{SUPERVISOR} — {SUPERVISOR_TITLE}</h4>",
                    unsafe_allow_html=True)

    st.markdown("<h3 style='text-align:center; color:#1b5e20;'>🔐 بوابة الدخول</h3>",
                unsafe_allow_html=True)

    col_owner, col_guest = st.columns(2)
    with col_owner:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#e8f5e9,#c8e6c9);
        padding:20px; border-radius:12px; border:2px solid #2e7d32;
        text-align:center; margin-bottom:10px;">
        <h4 style="color:#1b5e20;">👑 المالك</h4>
        <p style="font-size:0.9rem; color:#555;">دخول آمن</p>
        </div>
        """, unsafe_allow_html=True)
        oc = st.text_input("🔑 كود المالك:", type="password", key="owner_code")
        if st.button("👑 دخول المالك", type="primary", use_container_width=True):
            res = _handle_login(oc)
            if res["ok"]:
                st.rerun()
            else:
                st.error(res["msg"])

    with col_guest:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#fff8e1,#ffecb3);
        padding:20px; border-radius:12px; border:2px solid #d4af37;
        text-align:center; margin-bottom:10px;">
        <h4 style="color:#e65100;">👥 زائر</h4>
        <p style="font-size:0.9rem; color:#555;">دخول مجاني</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True):
            st.session_state.update({"approved": True, "user_role": "guest"})
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════
# الواجهة الرئيسية
# ═══════════════════════════════════════════════════════════════════════════

st.markdown('<div class="main-box">', unsafe_allow_html=True)

c1, c2 = st.columns([0.7, 0.3])
with c2:
    role_label = "المالك 👑" if is_owner() else "زائر 👥"
    st.markdown(f"<div style='text-align:left; padding:10px; background:#f5f5f5;"
                f"border-radius:10px;'>الحساب: <b>{role_label}</b></div>",
                unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

c3, c4 = st.columns([0.3, 0.7])
with c3:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">',
                    unsafe_allow_html=True)
with c4:
    st.markdown(f"<h1 style='color:#0d3011; text-align:right; font-weight:900; font-size:2.3rem;'>"
                f"🌾 {APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.25rem; font-weight:600;'>"
                f"{APP_TAGLINE}</p>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#fff8e1,#ffe082);
                padding:12px 20px; border-radius:12px;
                border-right:6px solid #c62828; border-left:6px solid #c62828;'>
        <h3 style='color:#b71c1c; text-align:right; margin:0; font-weight:900;'>
        👨‍🔬 {SUPERVISOR}</h3>
        <p style='color:#0d47a1; text-align:right; margin:5px 0 0 0; font-weight:700;'>
        ✨ {SUPERVISOR_TITLE}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="visitor-dua-banner">{DUA_VISITOR}</div>',
            unsafe_allow_html=True)
st.markdown("<hr style='border-top:3px solid #2e7d32;'>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# التبويبات
# ═══════════════════════════════════════════════════════════════════════════

tabs_titles = ["🔬 النمذجة", "🌰 الزيوت", "🍼 بدائل الحليب", "📷 OCR",
                "📚 المراجع", "💡 المساعدة"]
if is_owner():
    tabs_titles = ["🔬 النمذجة", "🌰 الزيوت", "🍼 بدائل الحليب", "📷 OCR",
                    "🏭 المستودعات", "📚 المراجع", "💡 المساعدة"]

tabs = st.tabs(tabs_titles)
tab_map = {t: tab for t, tab in zip(tabs_titles, tabs)}


# ─── تبويب النمذجة (3 تبويبات فرعية: LP, مختبر, NLP) ───
with tab_map["🔬 النمذجة"]:
    sub_lp, sub_lab, sub_nlp = st.tabs([
        "🎯 تركيب علفة (LP ≥70%)",
        "🔬 مختبر تحليل",
        "📈 تحسين غير خطي (NLP)",
    ])

    # ═══ LP ═══
    with sub_lp:
        try:
            st.markdown('<div class="section-title">🧬 أساس الحساب</div>',
                        unsafe_allow_html=True)
            pb = st.radio("الأساس:",
                           ["البروتين المهضوم (DP) — الأدق",
                            "البروتين الخام (CP) — الأسهل"],
                           horizontal=True, key="protein_basis")
            basis_code = "DP" if "DP" in pb else "CP"

            st.markdown('<div class="section-title">🐾 اختر الحيوان</div>',
                        unsafe_allow_html=True)

            animal_choice = None
            production_type = None
            requirement = None
            std_key_global = ""

            a_cattle, a_sheep, a_goat, a_camel, a_horse, a_poultry, a_fish, a_rabbit = st.tabs(
                ["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐪 إبل",
                 "🐎 خيول", "🐔 دواجن", "🐟 أسماك", "🐇 أرانب"])

            with a_cattle:
                ct = st.selectbox("الحالة:",
                                    ["حليب_عالي", "تسمين_مكثف", "صيانة"],
                                    key="cattle_t")
                cp_ = {}
                if "حليب" in ct:
                    cp_["milk_yield"] = st.number_input(
                        "🥛 الحليب (كجم):", 5.0, 60.0, 20.0, 1.0, key="cattle_m")
                cp_["weight_kg"] = st.number_input(
                    "⚖️ الوزن:", 200.0, 900.0, 500.0, 25.0, key="cattle_w")
                rp = get_cattle_requirements(ct, **cp_)
                c1, c2, c3 = st.columns(3)
                c1.metric("DP", f"{rp.DP}%")
                c2.metric("CP", f"{rp.CP}%")
                c3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_cattle"):
                    animal_choice = "أبقار"
                    production_type = ct
                    requirement = rp
                    std_key_global = f"أبقار_{ct}"

            with a_sheep:
                sg = st.radio("الجنس:", ["ذكر", "أنثى"], horizontal=True, key="sheep_g")
                is_m = "ذكر" in sg
                stype = st.selectbox("الحالة:",
                                       ["تسمين_مكثف", "تسمين_عادي", "مرضعات", "صيانة"],
                                       key="sheep_t")
                ws = st.number_input("⚖️ الوزن:", 15.0, 120.0, 50.0, 5.0, key="sheep_w")
                rp = get_sheep_requirements(stype, is_male=is_m, weight_kg=ws)
                c1, c2, c3 = st.columns(3)
                c1.metric("DP", f"{rp.DP}%")
                c2.metric("CP", f"{rp.CP}%")
                c3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_sheep"):
                    animal_choice = "أغنام"
                    production_type = stype
                    requirement = rp
                    std_key_global = f"أغنام_{stype}"

            with a_goat:
                gg = st.radio("الجنس:", ["ذكر", "أنثى"], horizontal=True, key="goat_g")
                is_m = "ذكر" in gg
                gtype = st.selectbox("الحالة:",
                                       ["تسمين_جديان", "حلابة_عالي", "صيانة"],
                                       key="goat_t")
                mg = st.number_input("🥛 الحليب (لتر):", 0.5, 8.0, 2.0, 0.25,
                                       key="goat_m") if "حلابة" in gtype else 2.0
                rp = get_goat_requirements(gtype, is_male=is_m, milk_yield=mg)
                c1, c2, c3 = st.columns(3)
                c1.metric("DP", f"{rp.DP}%")
                c2.metric("CP", f"{rp.CP}%")
                c3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_goat"):
                    animal_choice = "ماعز"
                    production_type = gtype
                    requirement = rp
                    std_key_global = f"ماعز_{gtype}"

            with a_camel:
                cmt = st.selectbox("الحالة:", ["نمو", "تسمين", "حليب", "صيانة"],
                                     key="camel_t")
                cwt = st.number_input("⚖️ الوزن:", 100.0, 800.0, 400.0, 25.0,
                                        key="camel_w")
                rp = get_camel_requirements(cmt, weight_kg=cwt)
                c1, c2, c3 = st.columns(3)
                c1.metric("DP", f"{rp.DP}%")
                c2.metric("CP", f"{rp.CP}%")
                c3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_camel"):
                    animal_choice = "إبل"
                    production_type = cmt
                    requirement = rp
                    std_key_global = f"إبل_{cmt}"

            with a_horse:
                ht = st.selectbox("الحالة:", ["رياضة_مكثف", "صيانة"],
                                    key="horse_t")
                hwt = st.slider("⚖️ الوزن:", 150, 800, 450, 10, key="horse_w")
                rp = get_horse_requirements(ht, weight_kg=hwt)
                c1, c2, c3 = st.columns(3)
                c1.metric("DP", f"{rp.DP}%")
                c2.metric("CP", f"{rp.CP}%")
                c3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_horse"):
                    animal_choice = "خيول"
                    production_type = ht
                    requirement = rp
                    std_key_global = f"خيول_{ht}"

            with a_poultry:
                ps = st.radio("السلالة:", ["لاحم", "بياض"],
                                horizontal=True, key="poultry_s")
                pa = st.number_input("العمر (أسبوع):", 1, 20, 1, 1, key="poultry_a")
                rp = get_poultry_requirements(ps, pa)
                c1, c2, c3 = st.columns(3)
                c1.metric("DP", f"{rp.DP}%")
                c2.metric("CP", f"{rp.CP}%")
                c3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_poultry"):
                    animal_choice = "دواجن"
                    production_type = ps
                    requirement = rp
                    if "بادي" in rp.name_ar:
                        std_key_global = "دواجن_بادي"
                    elif "بياض" in rp.name_ar:
                        std_key_global = "دواجن_بياض"
                    else:
                        std_key_global = "دواجن_ناهي"

            with a_fish:
                fs = st.selectbox("النوع:", ["البلطي النيلي", "القرموط الأفريقي"],
                                    key="fish_sp")
                fst = st.selectbox("المرحلة:", ["بادئ", "تسمين"], key="fish_stage")
                rp = get_fish_requirements(fs, fst)
                c1, c2, c3 = st.columns(3)
                c1.metric("DP", f"{rp.DP}%")
                c2.metric("CP", f"{rp.CP}%")
                c3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_fish"):
                    animal_choice = "أسماك"
                    production_type = fst
                    requirement = rp
                    std_key_global = "أسماك_بادئ" if "بادئ" in fst else "أسماك_تسمين"

            with a_rabbit:
                rt = st.selectbox("الحالة:", ["تسمين", "صيانة"], key="rabbit_t")
                rwt = st.number_input("⚖️ الوزن:", 1.0, 8.0, 4.0, 0.5, key="rabbit_w")
                rp = get_rabbit_requirements(rt, rwt)
                c1, c2, c3 = st.columns(3)
                c1.metric("DP", f"{rp.DP}%")
                c2.metric("CP", f"{rp.CP}%")
                c3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_rabbit"):
                    animal_choice = "أرانب"
                    production_type = rt
                    requirement = rp
                    std_key_global = f"أرانب_{rt}"

            if not (animal_choice and requirement):
                st.warning("⚠️ اختر حيواناً وفعّل ✅ الاعتماد")
            else:
                st.markdown(f"""
                <div class="physio-card">
                    <h4>🧬 الحالة المعتمدة</h4>
                    <p style="color:#1a237e; font-size:1.15rem; font-weight:700;">
                        {animal_choice} — <span style="color:#c62828;">{requirement.name_ar}</span>
                    </p>
                    <div style="display:flex; gap:12px; margin-top:10px; flex-wrap:wrap;">
                        <span style="background:#fff; padding:6px 14px; border-radius:8px;">
                            🧬 DP: <b>{requirement.DP}%</b></span>
                        <span style="background:#fff; padding:6px 14px; border-radius:8px;">
                            🧬 CP: <b>{requirement.CP}%</b></span>
                        <span style="background:#fff; padding:6px 14px; border-radius:8px;">
                            🌽 SE: <b>{requirement.SE}</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                requester_name = st.text_input("👤 اسم طالب العلفة:", key="req_name")

                st.markdown('<div class="section-title">🌾 اختيار المكونات</div>',
                            unsafe_allow_html=True)
                sq = st.text_input("🔍 بحث:", key="ing_search")

                selected = []
                default_set = get_default_selections(animal_choice, production_type)
                for cat_name, items in BIG_FEEDS_LIBRARY.items():
                    filt = {k: v for k, v in items.items()
                            if sq.lower() in k.lower()} if sq else items
                    if not filt:
                        continue
                    with st.expander(f"📁 {cat_name} ({len(filt)})",
                                      expanded=("الحبوب" in cat_name or
                                                 "الأكساب" in cat_name)):
                        cols = st.columns(3)
                        for idx, ing_name in enumerate(filt.keys()):
                            with cols[idx % 3]:
                                if st.checkbox(ing_name,
                                                value=(ing_name in default_set),
                                                key=f"pick_{animal_choice}_{ing_name}"):
                                    selected.append(ing_name)

                st.markdown("### 💰 أسعار المواد")
                prices_dict = {}
                if selected:
                    pcols = st.columns(min(3, len(selected)))
                    lookup_p = _get_ingredient_lookup()
                    for idx, ing in enumerate(selected):
                        with pcols[idx % 3]:
                            prices_dict[ing] = st.number_input(
                                f"💵 {ing} ($/طن)", min_value=5.0,
                                value=float(lookup_p.get(ing, {}).get("price", 350.0)),
                                step=10.0, key=f"p_sel_{animal_choice}_{ing}")

                st.success(f"✅ المختارة: **{len(selected)}** مادة")

                if st.button("🚀 تشغيل المحرك", type="primary",
                              use_container_width=True):
                    if len(selected) < 3:
                        st.error("⚠️ اختر 3 مكونات على الأقل")
                    else:
                        custom_std = requirement_to_standard(requirement)
                        with st.spinner(f"⏳ جاري التركيب ({basis_code})..."):
                            result = auto_formulate_smart(
                                selected, prices_dict, custom_std,
                                standard_key=std_key_global, basis=basis_code,
                                min_quality=70.0, animal_type=animal_choice,
                                production_type=production_type)
                        if result["success"]:
                            st.session_state["last_formulation_result"] = result
                            st.session_state["last_formulation_context"] = {
                                "animal_choice": animal_choice,
                                "requirement_name": requirement.name_ar,
                                "basis_label": basis_code,
                                "requirement": requirement,
                                "custom_standard": custom_std,
                                "requester_name": requester_name,
                                "std_key_global": std_key_global,
                                "animal_type": animal_choice,
                            }
                            st.session_state["active_formula"] = result["formula"]
                        else:
                            st.error(f"❌ {result['message']}")

                if st.session_state.get("last_formulation_result"):
                    result = st.session_state["last_formulation_result"]
                    ctx = st.session_state["last_formulation_context"]
                    formula = result["formula"]
                    actual = result["actual_nutrients"]
                    quality = result["quality_score"]
                    meets = result["meets_standard"]

                    cls = "quality-good" if meets else "quality-bad"
                    icon = "✅" if meets else "⚠️"
                    color = "#1b5e20" if meets else "#c62828"
                    st.markdown(f"""
                    <div class="{cls}">
                        <h3 style="color:{color}; margin:0;">
                        {icon} جودة الخلطة: {quality:.1f}%
                        </h3>
                        <p style="color:{color};">التكلفة: ${result['cost']:.2f}/طن</p>
                    </div>
                    """, unsafe_allow_html=True)

                    for ing, pct in formula.items():
                        st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> '
                                    f'{pct:.2f}% ({pct*10:.1f} كجم/طن)</div>',
                                    unsafe_allow_html=True)

                    ch1, ch2 = st.columns(2)
                    with ch1:
                        bf = create_colorful_bar_chart(ctx["custom_standard"], actual)
                        if bf:
                            st.image(bf.getvalue(), caption="📊 المقارنة",
                                      use_container_width=True)
                    with ch2:
                        pf = create_pie_chart(formula)
                        if pf:
                            st.image(pf.getvalue(), caption="🥧 التوزيع",
                                      use_container_width=True)

                    gf = create_gauge_chart(quality)
                    if gf:
                        st.image(gf.getvalue(), caption="🎯 الجودة",
                                  use_container_width=True)

                    try:
                        pdf_bytes = pdf_gen.generate_report(
                            formula=formula, requirement=ctx["requirement"],
                            animal_type=ctx["animal_type"],
                            breed=ctx["requirement_name"],
                            cost=result["cost"], city="—",
                            local_cost=result["cost"], local_sym="USD",
                            requester_name=ctx["requester_name"],
                            protein_basis=ctx["basis_label"],
                            standard_key=ctx["std_key_global"],
                            quality_score=quality)
                        if pdf_bytes:
                            st.download_button(
                                "📥 تحميل PDF", pdf_bytes,
                                file_name=f"Tawor_{datetime.now():%Y%m%d_%H%M}.pdf",
                                mime="application/pdf",
                                use_container_width=True)
                    except Exception as e:
                        st.error(f"⚠️ PDF: {e}")

        except Exception as e:
            st.error(f"⚠️ خطأ: {e}")
            with st.expander("التفاصيل"):
                st.code(traceback.format_exc())

    # ═══ مختبر التحليل ═══
    with sub_lab:
        try:
            st.markdown('<div class="section-title">🔬 مختبر تحليل</div>',
                        unsafe_allow_html=True)
            all_ings = list(_get_ingredient_lookup().keys())
            lab_cat = st.selectbox("📁 التصنيف:",
                                     ["الكل"] + list(BIG_FEEDS_LIBRARY.keys()),
                                     key="lab_cat")
            pool = all_ings if lab_cat == "الكل" else list(BIG_FEEDS_LIBRARY[lab_cat].keys())
            lookup_lab = _get_ingredient_lookup()
            default_df = pd.DataFrame({
                "المادة": pool,
                "الوزن (كجم)": [0.0] * len(pool),
                "السعر ($/طن)": [float(lookup_lab.get(m, {}).get("price", 300.0))
                                  for m in pool],
            })
            edited = st.data_editor(default_df, use_container_width=True,
                                     hide_index=True,
                                     column_config={
                                         "المادة": st.column_config.TextColumn(disabled=True),
                                         "الوزن (كجم)": st.column_config.NumberColumn(
                                             min_value=0.0, step=5.0),
                                     },
                                     key="lab_editor")
            lab_in = {r["المادة"]: r["الوزن (كجم)"]
                       for _, r in edited.iterrows() if r["الوزن (كجم)"] > 0}
            tot = sum(lab_in.values())
            if tot > 0:
                f_lab = {k: v / tot * 100 for k, v in lab_in.items()}
                nut = compute_formula_nutrients(f_lab)
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("⚖️ الوزن", f"{tot:.1f} كجم")
                c2.metric("🧬 CP", f"{nut['CP']:.2f}%")
                c3.metric("🧬 DP", f"{nut['DP']:.2f}%")
                c4.metric("⚡ SE", f"{nut['SE']:.1f}")
        except Exception as e:
            st.error(f"⚠️ {e}")

    # ═══ NLP ═══
    with sub_nlp:
        try:
            st.markdown('<div class="section-title">📈 التحسين غير الخطي</div>',
                        unsafe_allow_html=True)
            st.caption("تعظيم الربح باستخدام SLSQP + استجابة Michaelis-Menten")

            if not SCIPY_AVAILABLE:
                st.error("⚠️ scipy.optimize.minimize غير متوفرة")
            else:
                c1, c2 = st.columns(2)
                with c1:
                    cp_min = st.number_input("CP الأدنى (%)", 5.0, 40.0, 18.0, 0.5,
                                               key="nlp_cp")
                    me_min = st.number_input("ME الأدنى (kcal/kg)", 1500.0, 4000.0,
                                               2900.0, 50.0, key="nlp_me")
                    ndf_min = st.number_input("NDF الأدنى (%)", 0.0, 40.0, 8.0, 0.5,
                                                key="nlp_ndf_lo")
                with c2:
                    ca_p_min = st.number_input("Ca:P الأدنى", 0.5, 3.0, 1.5, 0.1,
                                                 key="nlp_cap_lo")
                    ca_p_max = st.number_input("Ca:P الأقصى", 1.0, 4.0, 2.2, 0.1,
                                                 key="nlp_cap_hi")
                    ndf_max = st.number_input("NDF الأقصى (%)", 5.0, 60.0, 20.0, 0.5,
                                                key="nlp_ndf_hi")

                value_coef = st.number_input("💰 معامل القيمة (V)", 0.1, 100.0,
                                                2.0, 0.1, key="nlp_v")

                all_mats = list(_get_ingredient_lookup().keys())
                nlp_selected = st.multiselect(
                    "المواد المتاحة:", options=all_mats,
                    default=[m for m in ["ذرة صفراء", "كسب فول صويا 44%",
                                          "نخالة قمح (ردة)", "الحجر الجيري",
                                          "فوسفات ثنائي الكالسيوم", "ملح الطعام"]
                              if m in all_mats],
                    key="nlp_mats")

                if st.button("🚀 تشغيل التحسين", type="primary",
                              use_container_width=True):
                    if len(nlp_selected) < 2:
                        st.error("⚠️ اختر مكونين على الأقل")
                    else:
                        lookup_nlp = _get_ingredient_lookup()
                        prices_nlp = {n: lookup_nlp[n].get("price", 300.0)
                                       for n in nlp_selected}
                        cons = NLPConstraints(
                            cp_min=cp_min, cp_max=40.0,
                            me_min=me_min, me_max=4000.0,
                            ndf_min=ndf_min, ndf_max=ndf_max,
                            ca_p_min=ca_p_min, ca_p_max=ca_p_max)
                        with st.spinner("⏳ جاري حل NLP..."):
                            r = solve_nlp_formulation(nlp_selected, prices_nlp,
                                                        value_coef, cons)
                        if r["success"]:
                            st.session_state["nlp_result"] = r
                            st.session_state["nlp_charts"] = {}
                            st.success(f"✅ حل وُجد في {r['iterations']} تكرار")
                        else:
                            st.error(f"❌ {r['message']}")

                if st.session_state.get("nlp_result"):
                    r = st.session_state["nlp_result"]
                    st.markdown(f"""
                    <div class="quality-good">
                        <h3 style="color:#1b5e20; margin:0;">✅ الحل الأمثل</h3>
                        <p>Profit: <b>{r['profit_score']:.4f}</b> |
                           التكلفة: <b>${r['cost_per_kg']:.4f}/كجم</b></p>
                    </div>
                    """, unsafe_allow_html=True)

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("💵 تكلفة/كجم", f"${r['cost_per_kg']:.4f}")
                    m2.metric("⚡ ME", f"{r['me']:.0f}")
                    m3.metric("🧬 CP", f"{r['cp']:.2f}%")
                    m4.metric("⚖️ Ca:P", f"{r['ca_p']:.2f}")

                    if r["violations"]:
                        st.warning("⚠️ " + " | ".join(r["violations"]))

                    st.dataframe(pd.DataFrame([
                        {"المادة": k, "النسبة %": f"{v:.2f}",
                         "كجم/طن": f"{v*10:.1f}"}
                        for k, v in r["formula"].items()
                    ]), use_container_width=True, hide_index=True)

                    st.markdown("### 📊 تحليل متقدم")
                    chart_tabs = st.tabs(["📈 منحنى", "🎯 سطح 3D",
                                           "🌪️ حساسية", "⚖️ باريتو"])

                    with chart_tabs[0]:
                        if st.button("توليد", key="gen_curve",
                                      use_container_width=True):
                            with st.spinner("⏳..."):
                                fig = build_profit_curve(
                                    r["ingredient_names"], r["prices_used"],
                                    r["value_coef"], r["constraints"])
                            st.session_state["nlp_charts"]["منحنى الربحية"] = fig
                        if st.session_state["nlp_charts"].get("منحنى الربحية"):
                            st.plotly_chart(
                                st.session_state["nlp_charts"]["منحنى الربحية"],
                                use_container_width=True)

                    with chart_tabs[1]:
                        if st.button("توليد", key="gen_3d",
                                      use_container_width=True):
                            with st.spinner("⏳..."):
                                fig = build_3d_surface(
                                    r["ingredient_names"], r["prices_used"],
                                    r["value_coef"], r["constraints"])
                            st.session_state["nlp_charts"]["سطح 3D"] = fig
                        if st.session_state["nlp_charts"].get("سطح 3D"):
                            st.plotly_chart(
                                st.session_state["nlp_charts"]["سطح 3D"],
                                use_container_width=True)

                    with chart_tabs[2]:
                        if st.button("توليد", key="gen_tornado",
                                      use_container_width=True):
                            with st.spinner("⏳..."):
                                fig = build_tornado(
                                    r["ingredient_names"], r["prices_used"],
                                    r["value_coef"], r["constraints"])
                            st.session_state["nlp_charts"]["تحليل الحساسية"] = fig
                        if st.session_state["nlp_charts"].get("تحليل الحساسية"):
                            st.plotly_chart(
                                st.session_state["nlp_charts"]["تحليل الحساسية"],
                                use_container_width=True)

                    with chart_tabs[3]:
                        if st.button("توليد", key="gen_pareto",
                                      use_container_width=True):
                            with st.spinner("⏳..."):
                                fig = build_pareto(
                                    r["ingredient_names"], r["prices_used"],
                                    r["value_coef"], r["constraints"])
                            st.session_state["nlp_charts"]["جبهة باريتو"] = fig
                        if st.session_state["nlp_charts"].get("جبهة باريتو"):
                            st.plotly_chart(
                                st.session_state["nlp_charts"]["جبهة باريتو"],
                                use_container_width=True)

                    pdf_nlp = generate_nlp_pdf_report(
                        r, st.session_state.get("nlp_charts"),
                        requester=st.session_state.get("req_name", ""))
                    if pdf_nlp:
                        st.download_button(
                            "📥 تحميل PDF", pdf_nlp,
                            file_name=f"NLP_{datetime.now():%Y%m%d_%H%M}.pdf",
                            mime="application/pdf",
                            use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ {e}")
            with st.expander("التفاصيل"):
                st.code(traceback.format_exc())


# ─── الزيوت ───
with tab_map["🌰 الزيوت"]:
    st.markdown('<div class="section-title">🌰 مكتبة الزيوت</div>',
                unsafe_allow_html=True)
    st.write(f"{len(get_oil_ingredients())} زيتاً وفق NRC/Ross/FAO")
    st.dataframe(pd.DataFrame([
        {"الحيوان": k, "أقصى %": f"{v['max']}%",
         "مثالي %": f"{v['optimal']}%", "المرجع": v["source"]}
        for k, v in MAX_OIL_PERCENTAGE.items()
    ]), use_container_width=True, hide_index=True)


# ─── بدائل الحليب ───
with tab_map["🍼 بدائل الحليب"]:
    st.markdown('<div class="section-title">🍼 بدائل الحليب</div>',
                unsafe_allow_html=True)

    mr1, mr2 = st.columns(2)
    with mr1:
        mr_a = st.selectbox("الحيوان:", list(MILK_REPLACER_STANDARDS.keys()),
                             key="mr_a")
    with mr2:
        std_mr = MILK_REPLACER_STANDARDS[mr_a]
        st.info(f"CP: {std_mr['CP']}% | Fat: {std_mr['Fat']}% | "
                f"Lactose: {std_mr['Lactose']}%")

    mr_sel = []
    cols = st.columns(3)
    for i, (name, data) in enumerate(MILK_REPLACER_INGREDIENTS.items()):
        with cols[i % 3]:
            if st.checkbox(f"{name} (${data['price']})",
                            key=f"mr_{name}"):
                mr_sel.append(name)

    if st.button("🧪 تركيب", type="primary", use_container_width=True):
        if len(mr_sel) < 3:
            st.warning("⚠️ اختر 3 مكونات على الأقل")
        else:
            with st.spinner("⏳..."):
                r = formulate_milk_replacer(mr_a, 100.0, mr_sel)
            if r["success"]:
                st.success(f"✅ جودة: {r['quality_score']:.1f}%")
                for ing, pct in r["formula"].items():
                    st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> '
                                f'{pct:.2f}%</div>', unsafe_allow_html=True)
                st.metric("💰 التكلفة/100كجم", f"${r['cost_per_100kg']:.2f}")
            else:
                st.error(f"❌ {r['message']}")


# ─── OCR ───
with tab_map["📷 OCR"]:
    st.markdown('<div class="section-title">📷 OCR</div>',
                unsafe_allow_html=True)
    if not OCR_AVAILABLE:
        st.error("⚠️ pytesseract/opencv غير مثبتة")
    else:
        up = st.file_uploader("ارفع صورة:", type=["jpg", "jpeg", "png"])
        if up and st.button("🔍 تحليل", type="primary"):
            with st.spinner("⏳..."):
                res = extract_ingredients_from_image(up.read())
            if res["success"] and res["count"] > 0:
                st.success(f"✅ {res['count']} مادة")
                st.dataframe(pd.DataFrame([
                    {"المادة": k, "النسبة": v}
                    for k, v in res["ingredients"].items()
                ]), use_container_width=True, hide_index=True)
            else:
                st.warning(res.get("message", "لم يتم التعرف"))


# ─── المستودعات (مالك فقط) ───
if is_owner():
    with tab_map["🏭 المستودعات"]:
        st.markdown('<div class="section-title">🏭 المستودعات</div>',
                    unsafe_allow_html=True)
        inv = st.session_state["inventory"]
        q = [v["quantity"] for v in inv.values()]
        c1, c2, c3 = st.columns(3)
        c1.metric("📦 المواد", len(inv))
        c2.metric("🟢 آمنة", sum(1 for x in q if x >= 5))
        c3.metric("🔴 نافذة", sum(1 for x in q if x <= 0))

        inv_df = pd.DataFrame([
            {"المادة": name, "الكمية": v["quantity"],
             "الحد": v["min_threshold"]}
            for name, v in inv.items()
        ])
        edited = st.data_editor(inv_df, use_container_width=True,
                                 hide_index=True,
                                 column_config={
                                     "المادة": st.column_config.TextColumn(disabled=True),
                                     "الكمية": st.column_config.NumberColumn(
                                         min_value=0.0, step=1.0),
                                 })
        if st.button("💾 حفظ", type="primary", use_container_width=True):
            for _, row in edited.iterrows():
                inv[row["المادة"]]["quantity"] = float(row["الكمية"])
            st.success("✅ تم الحفظ")
            st.rerun()


# ─── المراجع ───
with tab_map["📚 المراجع"]:
    st.markdown('<div class="section-title">📚 المراجع</div>',
                unsafe_allow_html=True)
    st.markdown("""
- NRC (2012) — Swine Nutrition
- NRC (2007) — Small Ruminants
- NRC (2001) — Dairy Cattle
- NRC (2007) — Horses
- NRC (1994) — Poultry
- INRA (2018) — Ruminants
- FAO (2010) — Camel Nutrition
- Ross 308 (2020) — Broiler Handbook
- Danø & Højsgaard (2005) — LP in Ration Formulation
""")


# ─── المساعدة ───
with tab_map["💡 المساعدة"]:
    st.markdown('<div class="section-title">💡 المساعدة</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
### كيف تبدأ؟
1. اختر الحيوان في تبويب "🔬 النمذجة"
2. فعّل ✅ الاعتماد
3. اختر 3+ مكونات
4. اضغط 🚀 تشغيل المحرك (LP) أو 📈 NLP

### NLP (جديد)
- تعظيم الربح بدلاً من تقليل التكلفة
- 4 رسوم: منحنى، سطح 3D، Tornado، باريتو
- يتطلب `kaleido` لتصدير الرسوم في PDF

### الدعم
📧 {OWNER_EMAIL}
📱 {WHATSAPP_NUMBER}

{DUA_FULL}
    """)


# ═══════════════════════════════════════════════════════════════════════════
# التذييل
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(f'<div class="mini-signature">🌾 {APP_NAME} v{APP_VERSION} | '
            f'{SUPERVISOR} © 2026</div>', unsafe_allow_html=True)
st.markdown(f'<div class="dua-fixed-banner">🤲 {DUA_SHORT} 🤲</div>',
            unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# نهاية الملف — Tawor Nology 12.0
# ═══════════════════════════════════════════════════════════════════════════
