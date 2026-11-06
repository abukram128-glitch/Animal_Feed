# ═══════════════════════════════════════════════════════════════════════════
# تاور نولجي TAWOR NOLOGY v11.8 — نسخة أمنية-علمية-تقنية كاملة
# د. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
# ═══════════════════════════════════════════════════════════════════════════
# ⚠️ قبل التشغيل: أنشئ .streamlit/secrets.toml بهذا المحتوى:
#    OWNER_CODE = "كودك-السري-هنا"
# ═══════════════════════════════════════════════════════════════════════════

import streamlit as st
import numpy as np, pandas as pd, io, os, re, base64, tempfile
import traceback, warnings, json, threading, random, hashlib, hmac
import time as _time
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple, Any, Set

warnings.filterwarnings('ignore')

try:
    from scipy.optimize import linprog
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False; linprog = None

try:
    import plotly.graph_objects as go, plotly.express as px
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
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor, white
    from reportlab.platypus import (Table, TableStyle, Paragraph, Spacer,
        Image as RLImage, SimpleDocTemplate, HRFlowable, PageBreak)
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


# ═══════════════════════════════════════════════════════════════════════════
# 🔐 الأمان — fail-closed
# ═══════════════════════════════════════════════════════════════════════════

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def _get_owner_code_hash() -> Optional[str]:
    """يقرأ كود المالك من secrets/env فقط — لا يوجد كود في المصدر."""
    try:
        if hasattr(st, "secrets"):
            code = str(st.secrets.get("OWNER_CODE", "") or "").strip()
            if len(code) >= 6:
                return _sha256(code)
    except Exception:
        pass
    try:
        code = str(os.environ.get("TAWOR_OWNER_CODE", "") or "").strip()
        if len(code) >= 6:
            return _sha256(code)
    except Exception:
        pass
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


def _owner_login_attempt(user_input: str) -> Tuple[bool, str]:
    now = _time.time()
    lock_until = st.session_state.get("owner_lock_until", 0.0)
    if now < lock_until:
        return False, f"🔒 مقفل — انتظر {int(lock_until - now)} ثانية"

    if not _get_owner_code_hash():
        return False, "⚠️ كود المالك غير مُهيّأ — راجع المسؤول"

    if not check_owner_code(user_input):
        n = st.session_state.get("owner_attempts", 0) + 1
        st.session_state["owner_attempts"] = n
        if n >= 9:
            st.session_state["owner_lock_until"] = now + 86400
            return False, "🔒 9 محاولات — قفل 24 ساعة"
        if n >= 6:
            st.session_state["owner_lock_until"] = now + 1800
            return False, "🔒 6 محاولات — قفل 30 دقيقة"
        if n >= 3:
            st.session_state["owner_lock_until"] = now + 300
            return False, "🔒 3 محاولات — قفل 5 دقائق"
        return False, f"❌ كود غير صحيح — متبقٍ {3 - n}"

    st.session_state.update({
        "approved": True, "user_role": "owner",
        "owner_attempts": 0, "owner_lock_until": 0.0,
    })
    return True, "✅ دخول ناجح"


def _guard_sensitive_operation(operation: str) -> bool:
    if not _session_valid():
        st.error("⚠️ جلسة غير صالحة")
        return False
    if operation in ("delete_invoice", "delete_farm",
                     "delete_comment", "edit_prices"):
        if st.session_state.get("user_role") != "owner":
            st.error("⚠️ للمالك فقط")
            return False
    return True


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
APP_VERSION = "11.8"
SUPERVISOR = "د. عبدالقادر إسماعيل تاور"
SUPERVISOR_TITLE = "اختصاصي تغذية الحيوان"
PLATFORM_URL = "https://tawor-nology.streamlit.app"
WHATSAPP_NUMBER = "+249123533489"
OWNER_EMAIL = "abukram128@gmail.com"
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG"]
LOGO_OPTIONS = ["logo.png", "logo.jpg"]

st.set_page_config(
    page_title=f"{APP_NAME} | {APP_TAGLINE}",
    page_icon="🌾", layout="wide",
    initial_sidebar_state="collapsed")


# ═══════════════════════════════════════════════════════════════════════════
# إدارة الخطوط العربية
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
            pdfmetrics.registerFont(TTFont('TaworArabic', path))
            self.font_name = 'TaworArabic'
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
        return get_display(arabic_reshaper.reshape(str(text)), base_dir='R')
    except Exception:
        return str(text)


def ar(text):
    return _ar_cached(text)


# ═══════════════════════════════════════════════════════════════════════════
# مكتبة الأعلاف — 200+ مكون
# ═══════════════════════════════════════════════════════════════════════════

def _feed(cp, dc, se, ndf, adf, ee, ash, ca, p, lys, met, price, desc, src):
    return {"CP": cp, "DC": dc, "SE": se, "NDF": ndf, "ADF": adf,
            "EE": ee, "ASH": ash, "Ca": ca, "P": p,
            "Lys": lys, "Met": met,
            "price": price, "desc": desc, "src": src}


BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": _feed(8.5, .85, 80, 9.5, 3.2, 3.8, 1.3, .02, .27, .24, .17, 230, "الطاقة الرئيسية", "NRC 2012"),
        "ذرة بيضاء": _feed(8.8, .83, 78, 10.2, 3.5, 3.5, 1.4, .02, .26, .25, .18, 225, "بديل محلي", "NRC 2012"),
        "ذرة شامية": _feed(8.3, .86, 82, 9, 3, 4, 1.2, .02, .28, .23, .16, 240, "طاقة أعلى", "NRC 2012"),
        "ذرة رفيعة (سورجم)": _feed(10, .78, 70, 12.5, 5.5, 3, 1.8, .03, .3, .22, .17, 195, "بديل جزئي", "NRC 2012"),
        "شعير مطحون": _feed(11.5, .8, 71, 18.5, 7.5, 2.2, 2.5, .05, .35, .42, .2, 210, "للمجترات", "NRC 2012"),
        "شعير كامل": _feed(10.8, .75, 68, 22, 9, 2, 2.8, .05, .33, .4, .18, 200, "يحتاج جرش", "NRC 2012"),
        "قمح محلي": _feed(12, .85, 75, 11.5, 3.8, 2, 1.6, .04, .32, .35, .2, 240, "طاقة جيدة", "NRC 2012"),
        "قمح مستورد": _feed(11.5, .87, 78, 11, 3.5, 1.9, 1.5, .04, .33, .34, .19, 245, "طاقة أعلى", "NRC 2012"),
        "جريش أرز": _feed(7.8, .82, 82, 5.5, 2.5, 8.5, 4.2, .06, .3, .28, .18, 240, "طاقة عالية", "NRC 2012"),
        "دخن محلي": _feed(11, .75, 68, 15.5, 6.5, 4, 2.2, .05, .31, .28, .2, 220, "بديل", "NRC 2012"),
        "شوفان علفي": _feed(11, .76, 62, 27.5, 13.5, 5, 3, .08, .35, .4, .18, 260, "للخيول", "NRC 2007"),
        "كسرة خبز": _feed(10.5, .82, 75, 8, 3.5, 5.5, 3.5, .1, .2, .28, .17, 160, "اقتصادي", "INRA 2018"),
        "بسكويت مكسر": _feed(8.5, .85, 85, 4, 2, 12, 2.5, .08, .18, .2, .12, 180, "طاقة عالية", "INRA 2018"),
        "مكرونة مكسرة": _feed(11, .88, 80, 3.5, 1.5, 1.5, 1, .03, .2, .28, .15, 190, "طاقة", "INRA 2018"),
        "بطاطا مجففة": _feed(8, .9, 78, 6, 3, 1, 4.5, .08, .22, .28, .15, 200, "بديلة", "INRA 2018"),
        "كسافا مجففة": _feed(3, .85, 75, 8, 4.5, 1, 3.5, .15, .1, .1, .05, 150, "رخيصة", "FAO 2010"),
        "تمر مجفف (دقل)": _feed(5.5, .85, 68, 15, 8.5, 1, 3.5, .1, .1, .1, .05, 180, "اقتصادي", "FAO 2010"),
        "سكر مائدة": _feed(0, 1, 100, 0, 0, 0, 0, 0, 0, 0, 0, 500, "≤2% فقط", "NRC 2012"),
        "عسل أسود (دبس)": _feed(1, .92, 75, 0, 0, 0, 3.5, .15, .05, .05, .02, 220, "≤3% فقط", "NRC 2012"),
        "تفل بنجر السكر": _feed(8.5, .65, 55, 45, 28, 1, 8.5, .7, .1, .3, .15, 190, "للمجترات", "INRA 2018"),
        "تفل عنب": _feed(12, .55, 40, 45, 32, 7.5, 6, .25, .4, .3, .15, 120, "أكسدة", "INRA 2018"),
        "تفل زيتون": _feed(8, .55, 35, 50, 35, 12, 7, .5, .15, .2, .1, 130, "زيوت", "INRA 2018"),
    },
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني": _feed(46, .88, 73, 15.5, 8.5, 1.5, 5.5, .2, .65, 1.6, .45, 460, "ممتاز", "NRC 2012"),
        "كسب فول صويا 44%": _feed(44, .9, 74, 13.5, 8, 1.8, 6, .35, .65, 2.7, .6, 440, "الرئيسي", "NRC 2012"),
        "كسب فول صويا 48%": _feed(48, .91, 76, 12, 7, 1.5, 6.2, .35, .65, 3, .68, 480, "مرتفع", "NRC 2012"),
        "كسب عباد الشمس 36%": _feed(36, .76, 42, 38.5, 25.5, 2.5, 6.5, .4, 1, 1.2, .7, 310, "أرخص", "NRC 2012"),
        "كسب عباد الشمس 32%": _feed(32, .72, 38, 42, 28, 2, 7, .42, .95, 1.1, .65, 290, "اقتصادي", "NRC 2012"),
        "كسب بذور القطن": _feed(41, .78, 55, 24.5, 15.5, 1.2, 6.5, .2, 1.1, 1.8, .6, 290, "جوسيبول — للمجترات", "NRC 2012"),
        "كسب بذور الكتان": _feed(32, .82, 65, 18.5, 10.5, 2.8, 5.8, .35, .85, 1.2, .55, 340, "أوميغا 3", "NRC 2007"),
        "كسب السمسم": _feed(42, .84, 70, 14.5, 9.5, 8.5, 12.5, 2, 1.2, 1.3, 1, 520, "غني بالكالسيوم", "NRC 2007"),
        "كسب جلوتين 60%": _feed(60, .92, 85, 8.5, 5.5, 2.5, 3.5, .15, .5, 1.1, 1.8, 520, "ميثيونين عالٍ", "NRC 2012"),
        "كسب جلوتين 40%": _feed(40, .88, 72, 15, 8, 3, 5, .18, .55, 1.2, 1.1, 390, "معتدل", "NRC 2012"),
        "كسب نواة النخيل": _feed(16, .65, 52, 55.5, 35.5, 6.5, 4.5, .3, .55, .55, .28, 200, "رخيص", "FAO 2010"),
        "كسب الكانولا": _feed(36, .82, 60, 28, 18, 3.5, 6.5, .65, 1.1, 1.9, .7, 400, "متوازن", "NRC 2012"),
        "فول صويا كامل": _feed(38, .85, 78, 15, 10, 18, 4.5, .25, .55, 2.5, .55, 420, "معالجة حرارياً", "NRC 2012"),
        "ترمس حلو": _feed(32, .8, 65, 20, 12, 6, 4, .2, .45, 1.8, .35, 380, "بديل", "NRC 2007"),
        "بازلاء علفية": _feed(22, .82, 70, 15, 8, 1.5, 3, .1, .4, 1.5, .25, 320, "متوازن", "NRC 2012"),
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": _feed(15, .72, 45, 35.5, 12.5, 3.5, 5.5, .12, 1.1, .6, .25, 150, "اقتصادية", "NRC 2001"),
        "نخالة ذرة": _feed(9.5, .65, 40, 40, 15, 4, 2, .1, .75, .3, .15, 140, "اقتصادية", "NRC 2001"),
        "البرسيم الجاف": _feed(16.5, .6, 35, 42.5, 32.5, 2, 10.5, 1.5, .25, .85, .25, 170, "بروتين + ألياف", "NRC 2001"),
        "برسيم حجازي": _feed(18, .62, 38, 40, 30, 2.2, 11, 1.6, .26, .9, .28, 175, "أفضل جودة", "NRC 2001"),
        "مولاس قصب السكر": _feed(4, .95, 50, 1.5, .8, .5, 8.5, .7, .05, .03, .02, 120, "طاقة سريعة", "NRC 2001"),
        "تبن قمح": _feed(3.2, .35, 18, 72.5, 45.5, 1.5, 8.5, .3, .08, .15, .05, 80, "ألياف حشو", "NRC 2001"),
        "تبن فول": _feed(4.5, .4, 22, 68, 42, 1.2, 7.5, .35, .1, .18, .08, 90, "أفضل من القمح", "NRC 2001"),
        "قشر فول سوداني": _feed(5, .3, 15, 65.5, 42.5, 1, 5.5, .25, .1, .15, .05, 70, "حشو", "NRC 2007"),
        "سرسة الأرز": _feed(2.5, .25, 12, 68.5, 48.5, 12.5, 15.5, .15, .08, .1, .05, 60, "حشو", "NRC 2007"),
        "قش أرز": _feed(3.5, .3, 15, 70, 45, 1.5, 12, .2, .06, .12, .05, 65, "حشو", "NRC 2007"),
        "مخلفات النخيل": _feed(6.5, .7, 60, 25, 15, 5, 3.5, .15, .15, .25, .1, 100, "للإبل", "FAO 2010"),
        "سعف نخيل مطحون": _feed(4, .3, 20, 65, 42, 2, 7, .35, .08, .15, .06, 55, "ألياف", "FAO 2010"),
        "أوراق موز مجففة": _feed(12, .55, 30, 45, 30, 3, 10, 1.2, .2, .5, .2, 85, "نادر", "FAO 2010"),
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": _feed(60, .85, 65, 2.5, 1.5, 8.5, 22.5, 5.5, 3.2, 4.5, 1.8, 850, "ممتاز", "NRC 2012"),
        "مسحوق أسماك 72%": _feed(72, .9, 72, 2, 1, 9.5, 18.5, 4.8, 2.8, 5.5, 2.2, 1100, "مرتفع جداً", "NRC 2012"),
        "مسحوق اللحم والعظم": _feed(50, .75, 50, 3.5, 2.5, 10.5, 32.5, 9, 4.5, 2.5, .7, 620, "Ca+P", "NRC 2012"),
        "مسحوق الدم": _feed(80, .65, 55, 1, .5, 1.5, 6, .3, .3, 7, 1, 780, "هضم منخفض", "NRC 2012"),
        "مسحوق ريش": _feed(82, .7, 60, 1.5, 1, 3, 4, .25, .35, 2, .5, 650, "معالجة حرارية", "NRC 2012"),
        "مركزات دواجن": _feed(40, .85, 60, 8.5, 4.5, 3.5, 12.5, 2.5, 1.2, 2.5, .9, 650, "جاهزة — 5/10% فقط", "NRC 2012"),
        "مركزات مواشي": _feed(36, .8, 55, 15.5, 8.5, 3, 15.5, 3, 1.5, 2, .7, 600, "جاهزة — 10/20/30%", "NRC 2001"),
        "حشرات مجففة (BSF)": _feed(42, .8, 68, 8, 5, 35, 8, .8, .9, 2.6, .85, 1800, "مستدام", "FAO 2013"),
        "دود قز مجفف": _feed(55, .75, 55, 4, 3, 25, 8.5, .5, .8, 3.2, 1.2, 1400, "غني", "FAO 2010"),
    },
    "🌿 الأعلاف الخضراء المائية": {
        "أزولا مجففة": _feed(24, .65, 45, 38, 25, 3.5, 18, 2, .6, 1, .4, 340, "رخيص", "FAO 2010"),
        "سبيرولينا": _feed(60, .85, 65, 5, 3, 6, 10, 1.2, .9, 3, 1.4, 3200, "سوبر فود", "FAO 2010"),
        "كلوريلا": _feed(55, .8, 60, 6, 3.5, 8, 12, .5, 1.2, 2.5, 1.2, 2800, "مكمل", "FAO 2010"),
        "طحالب بحرية": _feed(15, .6, 30, 25, 15, 2, 30, 1.5, .3, .6, .25, 900, "معادن", "FAO 2010"),
        "أوراق مورينجا": _feed(25, .65, 42, 28, 18, 4, 10, 2.5, .35, 1.2, .45, 380, "غنية", "FAO 2010"),
    },
    "🌰 الزيوت النباتية والحيوانية": {
        "زيت ذرة": _feed(0, 0, 220, 0, 0, 100, 0, 0, 0, 0, 0, 1500, "أوميغا 6", "NRC 2012"),
        "زيت فول الصويا": _feed(0, 0, 215, 0, 0, 100, 0, 0, 0, 0, 0, 1350, "متوازن", "Ross 308"),
        "زيت عباد الشمس": _feed(0, 0, 210, 0, 0, 100, 0, 0, 0, 0, 0, 1300, "أوميغا 6", "NRC 2007"),
        "زيت بذرة القطن": _feed(0, 0, 200, 0, 0, 100, 0, 0, 0, 0, 0, 1400, "جوسيبول", "NRC 2012"),
        "زيت الكتان": _feed(0, 0, 205, 0, 0, 100, 0, 0, 0, 0, 0, 1700, "أوميغا 3", "NRC 2007"),
        "زيت جوز الهند": _feed(0, 0, 230, 0, 0, 100, 0, 0, 0, 0, 0, 1900, "MCT", "NRC 2012"),
        "زيت النخيل": _feed(0, 0, 215, 0, 0, 100, 0, 0, 0, 0, 0, 1100, "مقاوم للأكسدة", "NRC 2012"),
        "زيت الكانولا": _feed(0, 0, 200, 0, 0, 100, 0, 0, 0, 0, 0, 1450, "متوازن", "NRC 2012"),
        "زيت السمسم": _feed(0, 0, 205, 0, 0, 100, 0, 0, 0, 0, 0, 2100, "مضاد أكسدة", "NRC 2007"),
        "زيت الزيتون": _feed(0, 0, 210, 0, 0, 100, 0, 0, 0, 0, 0, 3500, "أوميغا 9", "INRA 2018"),
        "زيت الفول السوداني": _feed(0, 0, 210, 0, 0, 100, 0, 0, 0, 0, 0, 2200, "طاقة", "NRC 2012"),
        "شحم حيواني (Tallow)": _feed(0, 0, 230, 0, 0, 100, 0, 0, 0, 0, 0, 900, "طاقة عالية", "NRC 2012"),
        "سمن حيواني (Lard)": _feed(0, 0, 225, 0, 0, 100, 0, 0, 0, 0, 0, 850, "يُتجنب للدواجن", "NRC 2012"),
        "دهن الدجاج": _feed(0, 0, 225, 0, 0, 100, 0, 0, 0, 0, 0, 800, "للدواجن", "NRC 2012"),
        "زيت السمك (Fish Oil)": _feed(0, 0, 235, 0, 0, 100, 0, 0, 0, 0, 0, 3800, "EPA/DHA", "NRC Fish"),
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": _feed(94, 1, 0, 0, 0, 0, .5, 0, 0, 94, 0, 4200, "أساسي", "NRC 2012"),
        "ليسين سلفات": _feed(79, 1, 0, 0, 0, 0, .5, 0, 0, 79, 0, 3800, "بديل أرخص", "NRC 2012"),
        "ميثيونين نقي": _feed(58, 1, 0, 0, 0, 0, .3, 0, 0, 0, 58, 5800, "للدواجن", "NRC 2012"),
        "ميثيونين هيدروكسي": _feed(88, 1, 0, 0, 0, 0, .2, 0, 0, 0, 88, 6500, "MHA", "NRC 2012"),
        "ثريونين نقي": _feed(72, 1, 0, 0, 0, 0, .2, 0, 0, 0, 0, 4800, "ثالث محدود", "NRC 2012"),
        "تريبتوفان نقي": _feed(85, 1, 0, 0, 0, 0, .1, 0, 0, 0, 0, 9500, "للدواجن", "NRC 2012"),
        "أرجينين": _feed(98, 1, 0, 0, 0, 0, .2, 0, 0, 0, 0, 7800, "للدواجن", "NRC 2012"),
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن": _feed(0, 0, 0, 0, 0, 0, 100, 18, 8, 0, 0, 4800, "فيتامينات + معادن", "NRC 1994"),
        "بريمكس بياض": _feed(0, 0, 0, 0, 0, 0, 100, 22, 7, 0, 0, 5000, "للبياض", "NRC 1994"),
        "بريمكس أبقار": _feed(0, 0, 0, 0, 0, 0, 100, 20, 10, 0, 0, 5200, "للأبقار", "NRC 2001"),
        "بريمكس مجترات": _feed(0, 0, 0, 0, 0, 0, 100, 18, 9, 0, 0, 4500, "للمجترات", "NRC 2007"),
        "بريمكس خيول": _feed(0, 0, 0, 0, 0, 0, 100, 15, 8, 0, 0, 5500, "للخيول", "NRC 2007"),
        "بريمكس إبل": _feed(0, 0, 0, 0, 0, 0, 100, 20, 10, 0, 0, 5300, "للإبل", "FAO 2010"),
        "بريمكس أسماك": _feed(0, 0, 0, 0, 0, 0, 100, 15, 7, 0, 0, 5800, "للأسماك", "NRC Fish"),
        "إنزيم فايتيز": _feed(0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 4200, "تحرير P", "NRC 2012"),
        "إنزيم NSP": _feed(0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 3800, "ألياف", "NRC 2012"),
        "مستخلص الخمائر MOS": _feed(12, .5, 10, 2.5, 1.5, 1.5, 8.5, .1, .2, .4, .15, 12000, "مناعة", "NRC 2012"),
        "خمائر حية": _feed(45, .75, 30, 8, 4, 1, 8, .15, 1.2, 3, .7, 8500, "للمجترات", "NRC 2001"),
        "بروبيوتيك": _feed(15, .6, 20, 5, 3, 2, 15, .3, .5, .5, .2, 9800, "بكتيريا نافعة", "NRC 2012"),
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": _feed(0, 0, 0, 0, 0, 0, 99.5, 38, 0, 0, 0, 40, "مصدر Ca", "NRC 2012"),
        "فوسفات ثنائي الكالسيوم": _feed(0, 0, 0, 0, 0, 0, 98.5, 23, 18, 0, 0, 280, "Ca+P", "NRC 2012"),
        "فوسفات أحادي الكالسيوم": _feed(0, 0, 0, 0, 0, 0, 99, 17, 22, 0, 0, 320, "مصدر P", "NRC 2012"),
        "ملح الطعام": _feed(0, 0, 0, 0, 0, 0, 99.9, 0, 0, 0, 0, 30, "NaCl — ≤0.5%", "NRC 2012"),
        "بيكربونات الصوديوم": _feed(0, 0, 0, 0, 0, 0, 99, 0, 0, 0, 0, 340, "مضاد حموضة", "NRC 2001"),
        "أكسيد المغنيسيوم": _feed(0, 0, 0, 0, 0, 0, 99.5, 0, 0, 0, 0, 480, "Mg", "NRC 2007"),
        "يوريا علفية": _feed(287, .95, 0, 0, 0, 0, 1, 0, 0, 0, 0, 480, "NPN — ≤1.5%", "NRC 2001"),
        "مضاد سموم فطرية": _feed(0, 0, 0, 0, 0, 0, 85, 0, 0, 0, 0, 950, "أفلاتوكسين", "NRC 2012"),
        "مضاد أكسدة BHT": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 1200, "تزنخ", "NRC 2012"),
        "كولين كلوريد": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 3200, "B4", "NRC 2012"),
    },
    "💊 الفيتامينات": {
        "فيتامين A": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 4200, "نمو", "NRC 2012"),
        "فيتامين D3": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 5200, "Ca", "NRC 2012"),
        "فيتامين E": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 5800, "أكسدة", "NRC 2012"),
    },
    "⚗️ مضافات خاصة": {
        "مضاد كوكسيديا": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 4200, "للدواجن", "NRC 1994"),
        "مضاد فطريات": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 2800, "حفظ", "NRC 2012"),
        "منشط نمو طبيعي": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 8500, "بديل", "NRC 2012"),
        "بيتاين (Betaine)": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 4800, "إجهاد حراري", "NRC 2012"),
        "طحالب كالبتوس": _feed(8, .6, 25, 10, 6, 2, 35, 2.5, .3, .3, .15, 2500, "معادن", "FAO 2010"),
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


def get_total_ingredient_count() -> int:
    return len(_get_ingredient_lookup())


# ═══════════════════════════════════════════════════════════════════════════
# 🔒 GLOBAL SAFETY LIMITS
# ═══════════════════════════════════════════════════════════════════════════

GLOBAL_SAFETY_LIMITS = {
    "مركزات دواجن": {"type": "choice", "options": [5.0, 10.0],
                     "source": "AAFCO / NRC 1994",
                     "note": "5% أو 10% فقط"},
    "مركزات مواشي": {"type": "choice", "options": [10.0, 20.0, 30.0],
                     "source": "NRC 2001",
                     "note": "10% / 20% / 30% فقط"},
    "ملح الطعام": {"type": "range", "min": 0.1, "max": 0.5,
                   "source": "NRC 2012", "critical": True,
                   "note": "زيادة تسبب تسمم ملحي"},
    "الحجر الجيري": {"type": "range", "min": 0, "max": 4.0,
                     "source": "NRC 2001"},
    "فوسفات ثنائي الكالسيوم": {"type": "range", "min": 0, "max": 3.0,
                                "source": "NRC 2001"},
    "فوسفات أحادي الكالسيوم": {"type": "range", "min": 0, "max": 3.0,
                                "source": "NRC 2001"},
    "بيكربونات الصوديوم": {"type": "range", "min": 0, "max": 1.0,
                            "source": "NRC 2001"},
    "يوريا علفية": {"type": "range", "min": 0, "max": 1.5,
                     "source": "NRC 2001", "critical": True,
                     "note": "تسمم أمونيا — للمجترات فقط"},
    "بريمكس تسمين دواجن": {"type": "max", "max": 1.0, "source": "NRC 1994"},
    "بريمكس بياض": {"type": "max", "max": 1.0, "source": "NRC 1994"},
    "بريمكس أبقار": {"type": "max", "max": 0.5, "source": "NRC 2001"},
    "بريمكس مجترات": {"type": "max", "max": 0.5, "source": "NRC 2007"},
    "بريمكس إبل": {"type": "max", "max": 0.5, "source": "FAO 2010"},
    "بريمكس خيول": {"type": "max", "max": 0.5, "source": "NRC 2007"},
    "بريمكس أسماك": {"type": "max", "max": 1.0, "source": "NRC Fish"},
    "مضاد سموم فطرية": {"type": "max", "max": 0.2, "source": "NRC 2012"},
    "مضاد أكسدة BHT": {"type": "max", "max": 0.02, "source": "FAO"},
    "مضاد كوكسيديا": {"type": "max", "max": 0.0125, "source": "NRC 1994"},
    "كولين كلوريد": {"type": "max", "max": 0.3, "source": "NRC 2012"},
    "بيتاين (Betaine)": {"type": "max", "max": 0.2, "source": "NRC 2012"},
    "ليسين نقي": {"type": "max", "max": 0.5, "source": "NRC 2012"},
    "ليسين سلفات": {"type": "max", "max": 0.6, "source": "NRC 2012"},
    "ميثيونين نقي": {"type": "max", "max": 0.4, "source": "NRC 2012"},
    "ميثيونين هيدروكسي": {"type": "max", "max": 0.3, "source": "NRC 2012"},
    "ثريونين نقي": {"type": "max", "max": 0.3, "source": "NRC 2012"},
    "تريبتوفان نقي": {"type": "max", "max": 0.2, "source": "NRC 2012"},
    "سكر مائدة": {"type": "max", "max": 2.0, "source": "NRC 2012"},
    "عسل أسود (دبس)": {"type": "max", "max": 3.0, "source": "NRC 2012"},
    "زيت ذرة": {"type": "max", "max": 8.0, "source": "Ross 308"},
    "زيت فول الصويا": {"type": "max", "max": 8.0, "source": "Ross 308"},
    "شحم حيواني (Tallow)": {"type": "max", "max": 8.0, "source": "Ross 308"},
}


def validate_feed_inputs(formula: Dict[str, float]) -> Dict[str, Any]:
    result = {"ok": True, "errors": [], "warnings": [],
              "corrected": dict(formula), "corrections": [],
              "critical_hits": []}

    total = sum(formula.values())
    if abs(total - 100) > 0.05:
        result["warnings"].append(
            f"⚠️ مجموع النسب {total:.2f}% ≠ 100%")

    for ing, pct in formula.items():
        lim = GLOBAL_SAFETY_LIMITS.get(ing)
        if not lim:
            continue
        if lim["type"] == "choice":
            allowed = lim["options"]
            nearest = min(allowed, key=lambda x: abs(x - pct))
            if abs(pct - nearest) > 0.01:
                result["ok"] = False
                result["errors"].append(
                    f"❌ {ing}: {pct:.2f}% — المسموح: "
                    f"{' / '.join(f'{x}%' for x in allowed)}")
                result["corrections"].append({
                    "ingredient": ing, "from": pct, "to": nearest,
                    "reason": f"خيارات: {allowed}"})
                result["corrected"][ing] = nearest
        elif lim["type"] == "max":
            if pct > lim["max"]:
                result["ok"] = False
                result["errors"].append(
                    f"❌ {ing}: {pct:.2f}% > {lim['max']}%")
                result["corrections"].append({
                    "ingredient": ing, "from": pct, "to": lim["max"],
                    "reason": f"الحد {lim['max']}%"})
                result["corrected"][ing] = lim["max"]
                if lim.get("critical"):
                    result["critical_hits"].append(ing)
        elif lim["type"] == "range":
            if pct > lim["max"]:
                result["ok"] = False
                result["errors"].append(
                    f"❌ {ing}: {pct:.2f}% > {lim['max']}%")
                result["corrections"].append({
                    "ingredient": ing, "from": pct, "to": lim["max"],
                    "reason": lim.get("note", f"الحد {lim['max']}%")})
                result["corrected"][ing] = lim["max"]
                if lim.get("critical"):
                    result["critical_hits"].append(ing)
            elif pct < lim.get("min", 0):
                result["warnings"].append(
                    f"⚠️ {ing}: {pct:.2f}% < الحد الأدنى")

    new_total = sum(result["corrected"].values())
    if abs(new_total - 100) > 0.05 and result["corrections"]:
        diff = 100 - new_total
        free = [i for i in result["corrected"]
                if i not in GLOBAL_SAFETY_LIMITS
                and result["corrected"][i] > 0]
        if free:
            target = max(free, key=lambda x: result["corrected"][x])
            before = result["corrected"][target]
            result["corrected"][target] = max(0, before + diff)
            result["corrections"].append({
                "ingredient": target, "from": before,
                "to": result["corrected"][target],
                "reason": f"تعويض فرق ({diff:+.2f}%)"})

    return result


# ═══════════════════════════════════════════════════════════════════════════
# 📏 MEASUREMENT METHODS
# ═══════════════════════════════════════════════════════════════════════════

MEASUREMENT_METHODS = {
    "أبقار": {
        "name_ar": "أبقار",
        "method": "شريط حول الصدر + طول الجسم",
        "measures": [
            {"id": "heart_girth", "label": "محيط الصدر (سم)",
             "hint": "خلف الكتفين"},
            {"id": "body_length", "label": "طول الجسم (سم)",
             "hint": "من الكتف إلى الإلية"},
        ],
        "formula_ar": "(محيط الصدر² × طول الجسم) ÷ 10838",
        "divisor": 10838,
        "source": "Schaeffer 1971 / NRC 2001",
        "dmi_pct": (2.0, 3.0), "dmi_source": "NRC Dairy 2001",
    },
    "أغنام": {
        "name_ar": "أغنام",
        "method": "شريط حول الصدر + طول الجسم",
        "measures": [
            {"id": "heart_girth", "label": "محيط الصدر (سم)"},
            {"id": "body_length", "label": "طول الجسم (سم)"},
        ],
        "formula_ar": "(محيط الصدر² × طول الجسم) ÷ 10838",
        "divisor": 10838,
        "source": "NRC 2007 / Shrestha 2012",
        "dmi_pct": (3.0, 5.0), "dmi_source": "NRC Small Ruminants",
    },
    "ماعز": {
        "name_ar": "ماعز",
        "method": "شريط حول الصدر + طول الجسم",
        "measures": [
            {"id": "heart_girth", "label": "محيط الصدر (سم)"},
            {"id": "body_length", "label": "طول الجسم (سم)"},
        ],
        "formula_ar": "(محيط الصدر² × طول الجسم) ÷ 10838",
        "divisor": 10838,
        "source": "NRC 2007",
        "dmi_pct": (3.0, 5.0), "dmi_source": "NRC Small Ruminants",
    },
    "إبل": {
        "name_ar": "إبل",
        "method": "شريط حول الصدر + طول الجسم",
        "measures": [
            {"id": "heart_girth", "label": "محيط الصدر (سم)"},
            {"id": "body_length", "label": "طول الجسم (سم)"},
        ],
        "formula_ar": "(محيط الصدر² × طول الجسم) ÷ 11000",
        "divisor": 11000,
        "source": "FAO 2010 / Kamal 2015",
        "dmi_pct": (2.0, 3.0), "dmi_source": "FAO Camel",
    },
    "خيول": {
        "name_ar": "خيول",
        "method": "محيط الصدر + طول الجسم",
        "measures": [
            {"id": "heart_girth", "label": "محيط الصدر (سم)"},
            {"id": "body_length", "label": "طول الجسم (سم)"},
        ],
        "formula_ar": "(محيط الصدر² × طول الجسم) ÷ 11877",
        "divisor": 11877,
        "source": "Carroll & Huntington 1988",
        "dmi_pct": (2.0, 2.5), "dmi_source": "NRC Horses 2007",
    },
}


def estimate_weight_from_tape(animal: str, hg: float, bl: float) -> Dict:
    method = MEASUREMENT_METHODS.get(animal)
    if not method or hg <= 0 or bl <= 0:
        return {"success": False, "message": "قياسات غير صحيحة"}
    weight = (hg ** 2 * bl) / method["divisor"]
    return {"success": True, "weight_kg": round(weight, 1),
            "formula": method["formula_ar"], "source": method["source"],
            "inputs": {"heart_girth": hg, "body_length": bl}}


def calculate_daily_feed(animal: str, weight_kg: float,
                          stage: str = "صيانة",
                          concentrate_ratio: float = 40.0) -> Dict:
    method = MEASUREMENT_METHODS.get(animal)
    if not method or "dmi_pct" not in method:
        return {"success": False, "message": f"{animal} غير مدعوم"}

    stage_factor = {"صيانة": 1.0, "نمو": 1.15, "تسمين": 1.25,
                    "حمل": 1.20, "رضاعة": 1.40, "حليب": 1.30,
                    "رياضة": 1.30, "سباق": 1.50}.get(stage, 1.0)

    dmi_low = weight_kg * method["dmi_pct"][0] / 100 * stage_factor
    dmi_high = weight_kg * method["dmi_pct"][1] / 100 * stage_factor
    dmi_mid = (dmi_low + dmi_high) / 2
    conc = dmi_mid * concentrate_ratio / 100
    rough = dmi_mid - conc

    return {
        "success": True, "weight_kg": weight_kg, "stage": stage,
        "dmi_kg": round(dmi_mid, 2),
        "dmi_range": (round(dmi_low, 2), round(dmi_high, 2)),
        "concentrate_kg": round(conc, 2),
        "roughage_kg": round(rough, 2),
        "concentrate_pct": concentrate_ratio,
        "dmi_pct_bw": f"{method['dmi_pct'][0]}–{method['dmi_pct'][1]}%",
        "source": method["dmi_source"],
        "stage_factor": stage_factor,
    }


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
    "أبقار_حليب_منخفض": {"max": 5.0, "optimal": 3.0, "source": "NRC 2001"},
    "أبقار_تسمين_مكثف": {"max": 6.0, "optimal": 4.5, "source": "NRC 2001"},
    "أبقار_تسمين_عادي": {"max": 5.0, "optimal": 3.5, "source": "NRC 2001"},
    "أغنام_تسمين_مكثف": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "أغنام_تسمين_عادي": {"max": 4.5, "optimal": 3.0, "source": "NRC 2007"},
    "أغنام_مرضعات": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "ماعز_تسمين_جديان": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "ماعز_حلابة_عالي": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "إبل_نمو": {"max": 5.0, "optimal": 3.5, "source": "FAO 2010"},
    "إبل_تسمين": {"max": 6.0, "optimal": 4.0, "source": "FAO 2010"},
    "إبل_حليب": {"max": 5.0, "optimal": 3.5, "source": "FAO 2010"},
    "خيول_رياضة_مكثف": {"max": 10.0, "optimal": 7.0, "source": "NRC Horses"},
    "خيول_رياضة_عادي": {"max": 8.0, "optimal": 5.0, "source": "NRC Horses"},
    "خيول_نمو_أمهار": {"max": 8.0, "optimal": 5.0, "source": "NRC Horses"},
    "خيول_صيانة": {"max": 5.0, "optimal": 3.0, "source": "NRC Horses"},
    "أسماك_بادئ": {"max": 15.0, "optimal": 10.0, "source": "NRC Fish"},
    "أسماك_نمو": {"max": 12.0, "optimal": 8.0, "source": "NRC Fish"},
    "أسماك_تسمين": {"max": 12.0, "optimal": 8.0, "source": "NRC Fish"},
    "أرانب_تسمين": {"max": 4.0, "optimal": 2.5, "source": "NRC 2007"},
}


def get_oil_standard(k: str) -> Dict[str, Any]:
    return MAX_OIL_PERCENTAGE.get(k, {"max": 5.0, "optimal": 3.0,
                                       "source": "عام"})


# ═══════════════════════════════════════════════════════════════════════════
# حدود المكونات حسب الحيوان
# ═══════════════════════════════════════════════════════════════════════════

INGREDIENT_LIMITS_BY_ANIMAL = {
    "دواجن": {
        "يوريا علفية": (0, 0), "سمن حيواني (Lard)": (0, 0),
        "دهن الدجاج": (0, 3), "نخالة قمح (ردة)": (0, 10),
        "نخالة ذرة": (0, 5), "تبن قمح": (0, 2), "قش أرز": (0, 2),
        "سرسة الأرز": (0, 2), "كسب بذور القطن": (0, 5),
        "كسب السمسم": (0, 8), "كسب الكانولا": (0, 8),
        "ملح الطعام": (.2, .4), "الحجر الجيري": (.8, 2),
        "فوسفات ثنائي الكالسيوم": (.5, 2.5),
        "بيكربونات الصوديوم": (0, .5),
        "مضاد سموم فطرية": (.05, .15),
        "بريمكس تسمين دواجن": (.2, .35),
        "بريمكس بياض": (.2, .35),
        "ليسين نقي": (0, .5), "ميثيونين نقي": (0, .4),
        "زيت ذرة": (0, 5), "زيت فول الصويا": (0, 6),
    },
    "سمان": {
        "يوريا علفية": (0, 0), "سمن حيواني (Lard)": (0, 0),
        "نخالة قمح (ردة)": (0, 8), "ملح الطعام": (.2, .4),
        "الحجر الجيري": (.8, 2.5),
        "فوسفات ثنائي الكالسيوم": (.5, 2),
        "بريمكس تسمين دواجن": (.2, .35),
        "بريمكس بياض": (.2, .35),
    },
    "أبقار": {
        "يوريا علفية": (0, 1.5), "نخالة قمح (ردة)": (0, 30),
        "كسب بذور القطن": (0, 20), "كسب السمسم": (0, 15),
        "ملح الطعام": (.3, .5), "بيكربونات الصوديوم": (.5, 1),
        "الحجر الجيري": (0, 3.5),
        "فوسفات ثنائي الكالسيوم": (0, 2),
        "بريمكس أبقار": (.15, .3),
        "بريمكس مجترات": (.15, .3),
        "مضاد سموم فطرية": (.05, .15),
    },
    "أغنام": {
        "يوريا علفية": (0, 1), "نخالة قمح (ردة)": (0, 25),
        "كسب بذور القطن": (0, 15), "ملح الطعام": (.3, .5),
        "بيكربونات الصوديوم": (.5, 1),
        "بريمكس مجترات": (.15, .3),
        "الحجر الجيري": (0, 3),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "ماعز": {
        "يوريا علفية": (0, 1), "نخالة قمح (ردة)": (0, 25),
        "ملح الطعام": (.3, .5), "بيكربونات الصوديوم": (.5, 1),
        "بريمكس مجترات": (.15, .3),
        "الحجر الجيري": (0, 3),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "إبل": {
        "يوريا علفية": (0, 1), "نخالة قمح (ردة)": (0, 20),
        "ملح الطعام": (.3, .5), "بيكربونات الصوديوم": (.5, 1),
        "بريمكس إبل": (.15, .3),
        "الحجر الجيري": (0, 3),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "خيول": {
        "يوريا علفية": (0, .5), "نخالة قمح (ردة)": (0, 20),
        "ملح الطعام": (.3, .5), "بريمكس خيول": (.15, .3),
        "الحجر الجيري": (0, 2.5),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "أسماك": {
        "يوريا علفية": (0, 0), "سمن حيواني (Lard)": (0, 0),
        "نخالة قمح (ردة)": (0, 10), "ملح الطعام": (0, .3),
        "بريمكس أسماك": (.15, .3),
        "الحجر الجيري": (0, 2),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "أرانب": {
        "يوريا علفية": (0, .5), "نخالة قمح (ردة)": (0, 20),
        "ملح الطعام": (.3, .5), "بريمكس مجترات": (.15, .3),
        "الحجر الجيري": (0, 2.5),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
}


def get_animal_limits(animal: str) -> Dict[str, Tuple[float, float]]:
    return INGREDIENT_LIMITS_BY_ANIMAL.get(animal, {})


# ═══════════════════════════════════════════════════════════════════════════
# الاحتياجات الغذائية
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AnimalRequirement:
    DP: float; CP: float; SE: float; NDF: float; ADF: float
    EE: float; ASH: float; Ca: float; P: float
    name_ar: str = ""; note: str = ""


def get_cattle_requirements(t, milk_yield=20.0, weight_kg=500.0):
    if t == "حليب_عالي":
        dp = 12.5 + milk_yield * .30
        return AnimalRequirement(round(dp, 2), round(dp / .70, 2),
            round(60 + milk_yield * .35, 1), 30, 19, 5.5, 8,
            round(.55 + milk_yield * .003, 3),
            round(.33 + milk_yield * .0015, 3),
            "أبقار حلابة عالية", f"حليب {milk_yield} كجم")
    if t == "حليب_متوسط":
        dp = 11 + milk_yield * .25
        return AnimalRequirement(round(dp, 2), round(dp / .72, 2),
            round(55 + milk_yield * .3, 1), 33, 21, 4.5, 8,
            round(.5 + milk_yield * .0025, 3),
            round(.3 + milk_yield * .0012, 3),
            "أبقار حلابة متوسطة", f"حليب {milk_yield} كجم")
    if t == "حليب_منخفض":
        dp = 9.5 + milk_yield * .2
        return AnimalRequirement(round(dp, 2), round(dp / .75, 2),
            round(50 + milk_yield * .25, 1), 38, 24, 4, 8.5,
            round(.45 + milk_yield * .002, 3),
            round(.28 + milk_yield * .001, 3),
            "أبقار حلابة منخفضة", f"حليب {milk_yield} كجم")
    if t == "تسمين_مكثف":
        return AnimalRequirement(11.5, 14.5, 72, 32, 20, 4.5, 7.5,
                                   .65, .38, "تسمين مكثف", "ADG >1.3")
    if t == "تسمين_عادي":
        return AnimalRequirement(9.5, 12, 65, 38, 24, 4, 7.5,
                                   .55, .32, "تسمين عادي", "ADG ~0.8")
    if t == "حمل_أخير":
        return AnimalRequirement(11.5, 14.5, 67, 35, 22, 4.2, 8,
                                   .7, .42, "حمل آخر", "شهر 7-9")
    return AnimalRequirement(7.5, 10, 53, 45, 28, 3, 8.5, .42, .26,
                              "أبقار صيانة", "بدون إنتاج")


def get_sheep_requirements(t, is_male=True, weight_kg=50.0, litter_size=1):
    if is_male:
        if t == "تسمين_مكثف":
            return AnimalRequirement(11.5, 14.5, 64, 28, 17, 4, 8,
                                       .65, .36, "تسمين مكثف", "")
        if t == "تسمين_عادي":
            return AnimalRequirement(9.5, 12, 59, 33, 21, 3.6, 8,
                                       .55, .32, "تسمين عادي", "")
        return AnimalRequirement(8.5, 11, 55, 38, 24, 3.2, 8.5,
                                   .5, .3, "حملان تيد", "")
    if t == "مرضعات":
        dp = 10.5 + (litter_size - 1) * 1.5
        return AnimalRequirement(round(dp, 2), round(dp / .72, 2),
            round(60 + (litter_size - 1) * 5, 1), 30, 19, 4.5, 8.5,
            round(.65 + (litter_size - 1) * .1, 3),
            round(.38 + (litter_size - 1) * .05, 3),
            f"نعاج مرضعات ({litter_size})", "")
    if t == "حامل_أخير":
        return AnimalRequirement(10.5, 13.5, 62, 32, 20, 3.8, 8,
                                   .6, .35, "نعاج حامل (4-5)", "")
    if t == "حامل_متوسط":
        return AnimalRequirement(8.5, 11, 55, 38, 24, 3.4, 8,
                                   .5, .3, "نعاج حامل (1-3)", "")
    return AnimalRequirement(7.2, 9.5, 48, 45, 28, 3, 8.5,
                               .42, .26, "نعاج صيانة", "")


def get_goat_requirements(t, is_male=True, milk_yield=2.0):
    if is_male:
        if t == "تسمين_جديان":
            return AnimalRequirement(11, 14, 62, 30, 19, 3.8, 8,
                                       .62, .34, "تسمين جديان", "")
        return AnimalRequirement(9, 11.5, 57, 36, 22, 3.5, 8,
                                   .55, .3, "تيوس تسمين", "")
    if t == "حلابة_عالي":
        dp = 11.5 + milk_yield * .45
        return AnimalRequirement(round(dp, 2), round(dp / .7, 2),
            round(58 + milk_yield * .45, 1), 29, 18, 4.5, 8.5,
            round(.6 + milk_yield * .008, 3),
            round(.35 + milk_yield * .004, 3),
            f"عنزات حلابة ({milk_yield})", "")
    if t == "حلابة_متوسط":
        dp = 10 + milk_yield * .35
        return AnimalRequirement(round(dp, 2), round(dp / .72, 2),
            round(55 + milk_yield * .4, 1), 32, 20, 4, 8.5,
            round(.55 + milk_yield * .006, 3),
            round(.32 + milk_yield * .003, 3),
            f"عنزات حلابة ({milk_yield})", "")
    if t == "حامل_أخير":
        return AnimalRequirement(10, 13, 60, 33, 21, 3.8, 8,
                                   .6, .35, "عنزات حامل", "")
    return AnimalRequirement(6.8, 9, 46, 46, 28, 3, 8.5,
                               .42, .26, "عنزات صيانة", "")


def get_camel_requirements(t, weight_kg=400.0, milk_yield=5.0):
    if t == "نمو":
        return AnimalRequirement(10.5, 13.5, 60, 38, 24, 4, 8,
                                   .65, .38, "إبل نمو", f"{weight_kg} كجم")
    if t == "تسمين":
        return AnimalRequirement(9.5, 12, 65, 35, 22, 4.5, 7.5,
                                   .6, .35, "إبل تسمين", f"{weight_kg} كجم")
    if t == "حليب":
        dp = 12 + milk_yield * .25
        return AnimalRequirement(round(dp, 2), round(dp / .7, 2),
            round(62 + milk_yield * .4, 1), 32, 20, 5, 8.5,
            round(.7 + milk_yield * .006, 3),
            round(.4 + milk_yield * .003, 3),
            f"إبل حلابة ({milk_yield})", "")
    if t == "سباق":
        return AnimalRequirement(14, 17, 72, 28, 17, 6, 9,
                                   .85, .5, "إبل سباق", "")
    return AnimalRequirement(7, 9, 48, 48, 30, 3.5, 9,
                               .42, .26, "إبل صيانة", f"{weight_kg} كجم")


def get_horse_requirements(t, weight_kg=450.0):
    if t == "رياضة_مكثف":
        return AnimalRequirement(10.5, 13.5, 70, 30, 18, 7, 7.5,
                                   .7, .4, "خيول رياضة مكثف", "")
    if t == "رياضة_عادي":
        return AnimalRequirement(9, 11.5, 63, 36, 22, 5, 7.5,
                                   .55, .32, "خيول رياضة عادي", "")
    if t == "نمو_أمهار":
        return AnimalRequirement(12, 15, 65, 30, 18, 5, 8,
                                   .75, .42, "أمهار نمو", "")
    if t == "مرضعات":
        return AnimalRequirement(12.5, 16, 68, 32, 20, 5.5, 8,
                                   .8, .45, "فرسات مرضعات", "")
    return AnimalRequirement(7.2, 9.5, 53, 46, 29, 3.5, 8,
                               .45, .28, "خيول صيانة", "")


def get_poultry_requirements(strain, age_weeks=1):
    if strain == "لاحم":
        if age_weeks <= 1:
            return AnimalRequirement(20, 23, 76, 8, 4, 5, 6.5, 1, .5,
                                      "بادي لاحم", "Energy 3000")
        if age_weeks <= 3:
            return AnimalRequirement(18.5, 21, 74, 9, 5, 5, 6, .9, .45,
                                      "نامي لاحم", "Energy 3100")
        if age_weeks <= 5:
            return AnimalRequirement(17, 19.5, 75, 10, 5.5, 4.5, 6,
                                       .87, .43, "ناهي لاحم", "Energy 3150")
        return AnimalRequirement(16.5, 19, 75, 10, 5.5, 4.5, 6,
                                   .85, .42, "ناهي لاحم+", "Energy 3200")
    if age_weeks <= 6:
        return AnimalRequirement(17, 20, 72, 10, 5.5, 4, 7, 1, .5,
                                  "بادي بياض", "")
    if age_weeks <= 18:
        return AnimalRequirement(14.5, 17, 70, 12, 6.5, 4, 9, 1.5, .45,
                                  "نامي بياض", "")
    return AnimalRequirement(15.5, 18, 72, 11, 6, 4.2, 11.5, 3.8, .45,
                              "بياض إنتاجي", "")


def get_quail_requirements(strain, age_weeks=1):
    if strain == "بياض":
        return AnimalRequirement(15, 18, 68, 11, 5.5, 4.5, 9,
                                   2.5, .45, "سمان بياض", "")
    if age_weeks <= 2:
        return AnimalRequirement(20.5, 24, 74, 8, 4, 5.5, 6.5,
                                   1, .55, "سمان بادي", "")
    if age_weeks <= 4:
        return AnimalRequirement(18.5, 22, 72, 9, 4.5, 5, 6,
                                   .9, .5, "سمان نامي", "")
    return AnimalRequirement(17, 20, 70, 10, 5, 4.5, 6,
                               .85, .45, "سمان ناهي", "")


def get_fish_requirements(species, stage):
    if "بادئ" in stage or "زريعة" in stage:
        return AnimalRequirement(32, 40, 72, 8, 4, 10, 11,
                                   1.5, .9, f"{species} بادئ", "")
    if "نمو" in stage:
        return AnimalRequirement(25, 32, 70, 12, 6, 8, 9,
                                   1, .7, f"{species} نمو", "")
    return AnimalRequirement(22, 28, 68, 13, 7, 8, 9.5,
                               .9, .65, f"{species} تسمين", "")


def get_rabbit_requirements(t, weight_kg=4.0):
    if t == "تسمين":
        return AnimalRequirement(15, 17, 65, 25, 15, 3, 8,
                                   .7, .35, "أرانب تسمين", "")
    if t == "حليب":
        return AnimalRequirement(18, 20, 68, 25, 15, 4, 8.5,
                                   .85, .45, "أرانب حلابة", "")
    return AnimalRequirement(12, 14, 60, 30, 20, 2.5, 8.5,
                               .6, .3, "أرانب صيانة", "")


def requirement_to_standard(req: AnimalRequirement) -> Dict[str, float]:
    return {"CP": req.CP, "DP": req.DP, "SE": req.SE,
            "NDF": req.NDF, "ADF": req.ADF, "EE": req.EE,
            "ASH": req.ASH, "Ca": req.Ca, "P": req.P}


# ═══════════════════════════════════════════════════════════════════════════
# الحسابات والتقييم
# ═══════════════════════════════════════════════════════════════════════════

def compute_formula_nutrients(formula: Dict[str, float]) -> Dict[str, float]:
    totals = {k: 0.0 for k in ["CP", "DP", "SE", "NDF", "ADF",
                                 "EE", "ASH", "Ca", "P", "Lys", "Met"]}
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


def compute_total_oil_percentage(formula):
    oils = set(get_oil_ingredients().keys())
    return sum(p for i, p in formula.items() if i in oils)


def evaluate_difference(pct_diff: float,
                         standard_value: Optional[float] = None) -> Dict:
    if standard_value is not None and standard_value == 0:
        if abs(pct_diff) < .001:
            return {"label": "🎯 مطابق", "bg": "#c8e6c9", "score": 100}
        return {"label": "⚠️ صفر", "bg": "#fff3e0", "score": 40}
    a = abs(pct_diff)
    if a <= .5:   return {"label": "🎯 مطابق", "bg": "#c8e6c9", "score": 100}
    if a <= 2:    return {"label": "🌟 ممتاز", "bg": "#dcedc8", "score": 95}
    if a <= 5:    return {"label": "✅ جيد جداً", "bg": "#e8f5e9", "score": 85}
    if a <= 10:   return {"label": "🟢 جيد", "bg": "#f1f8e9", "score": 75}
    if a <= 15:   return {"label": "⭐ مقبول", "bg": "#fff8e1", "score": 65}
    if a <= 25:   return {"label": "⚠️ بتحفظ", "bg": "#fff3e0", "score": 50}
    if a <= 40:   return {"label": "🟠 ضعيف", "bg": "#ffe0b2", "score": 35}
    return {"label": "❌ غير مطابق", "bg": "#ffebee", "score": 20}


def evaluate_quality_weighted(formula, targets, animal_type, basis="DP"):
    actual = compute_formula_nutrients(formula)
    is_rum = animal_type in ("أبقار", "أغنام", "ماعز", "إبل")
    is_poultry = animal_type in ("دواجن", "سمان")

    weights = {"DP" if basis == "DP" else "CP": 0.30}
    if targets.get("SE"):  weights["SE"] = 0.15
    if targets.get("NDF"): weights["NDF"] = 0.15 if is_rum else 0.10
    if targets.get("ADF"): weights["ADF"] = 0.10
    if targets.get("Ca"):  weights["Ca"] = 0.10
    if targets.get("P"):   weights["P"] = 0.10
    if is_poultry and targets.get("Lys"): weights["Lys"] = 0.05
    if is_poultry and targets.get("Met"): weights["Met"] = 0.05

    total_w, weighted = 0.0, 0.0
    for nut, w in weights.items():
        if not targets.get(nut): continue
        diff_pct = abs(actual.get(nut, 0) - targets[nut]) / targets[nut] * 100
        ev = evaluate_difference(diff_pct, standard_value=targets[nut])
        weighted += ev["score"] * w
        total_w += w

    ca, p = actual.get("Ca", 0), actual.get("P", 0)
    if ca > 0 and p > 0 and targets.get("Ca", 0) > 0:
        r = ca / p
        if is_poultry:
            if 1.5 <= r <= 2.2: rs = 100
            elif 1.3 <= r < 1.5 or 2.2 < r <= 2.5: rs = 80
            elif 1.0 <= r < 1.3 or 2.5 < r <= 3.5: rs = 50
            else: rs = 10
        else:
            if 1.5 <= r <= 2.0: rs = 100
            elif 1.2 <= r < 1.5 or 2.0 < r <= 2.5: rs = 85
            elif 0.9 <= r < 1.2 or 2.5 < r <= 3.5: rs = 55
            else: rs = 15
        weighted += rs * 0.10
        total_w += 0.10

    return (weighted / total_w if total_w else 0.0), actual


def get_default_selections(animal_type, production_type, requirement=None):
    d = {"ملح الطعام", "مضاد سموم فطرية"}
    if animal_type != "دواجن":
        d |= {"الحجر الجيري", "فوسفات ثنائي الكالسيوم"}
    if animal_type in ("أبقار", "أغنام", "ماعز", "إبل"):
        d.add("بيكربونات الصوديوم")
    if animal_type in ("دواجن", "سمان"):
        d.add("بريمكس بياض" if "بياض" in str(production_type)
              else "بريمكس تسمين دواجن")
    elif animal_type == "أبقار": d.add("بريمكس أبقار")
    elif animal_type in ("أغنام", "ماعز", "أرانب"): d.add("بريمكس مجترات")
    elif animal_type == "خيول": d.add("بريمكس خيول")
    elif animal_type == "إبل": d.add("بريمكس إبل")
    elif animal_type == "أسماك": d.add("بريمكس أسماك")
    if "بياض" in str(production_type):
        d.add("الحجر الجيري")
    return d


def _normalize_ingredient_name(name: str) -> str:
    name = re.sub(r'\s+', ' ', str(name).strip())
    lookup = _get_ingredient_lookup()
    if name in lookup: return name
    for lib in lookup.keys():
        if lib.lower() in name.lower() or name.lower() in lib.lower():
            return lib
    kw = {"ذره": "ذرة صفراء", "ذرة": "ذرة صفراء",
          "صويا": "كسب فول صويا 44%", "شعير": "شعير مطحون",
          "قمح": "قمح محلي", "نخاله": "نخالة قمح (ردة)",
          "نخالة": "نخالة قمح (ردة)", "ملح": "ملح الطعام",
          "حجر": "الحجر الجيري",
          "فوسفات": "فوسفات ثنائي الكالسيوم",
          "يوريا": "يوريا علفية"}
    for k, v in kw.items():
        if k in name.lower(): return v
    return name


# ═══════════════════════════════════════════════════════════════════════════
# محرك LP — 5 استراتيجيات
# ═══════════════════════════════════════════════════════════════════════════

def auto_formulate_smart(available_ingredients, prices, custom_standard,
                          standard_key="", basis="DP", min_quality=70.0,
                          animal_type="", production_type=""):
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
    tp = custom_standard.get(target_key, 15.0)
    tca = custom_standard.get("Ca", 0); t_p = custom_standard.get("P", 0)
    tse = custom_standard.get("SE", 0)
    tndf = custom_standard.get("NDF", 0); tadf = custom_standard.get("ADF", 0)
    tlys = custom_standard.get("Lys", 0); tmet = custom_standard.get("Met", 0)

    limits = get_animal_limits(animal_type)
    bounds = [limits.get(i, (0.0, 100.0)) for i in valid]

    A_eq_base = [[1.0] * n, rows[target_key]]
    b_eq_base = [100.0, tp * 100.0]
    A_ub_base, b_ub_base = [], []

    if tca > 0 and t_p > 0:
        if is_poultry: ca_p_min, ca_p_max = 1.5, 2.2
        elif is_ruminant: ca_p_min, ca_p_max = 1.4, 2.5
        else: ca_p_min, ca_p_max = 1.5, 2.0
        A_ub_base.append([-rows["Ca"][i] + ca_p_min * rows["P"][i]
                          for i in range(n)])
        b_ub_base.append(0)
        A_ub_base.append([rows["Ca"][i] - ca_p_max * rows["P"][i]
                          for i in range(n)])
        b_ub_base.append(0)

    if tse > 0:
        A_ub_base.append([-x for x in rows["SE"]])
        b_ub_base.append(-tse * 0.92 * 100.0)

    if tndf > 0:
        if is_ruminant:
            A_ub_base.append([-x for x in rows["NDF"]])
            b_ub_base.append(-tndf * 0.85 * 100.0)
            A_ub_base.append(rows["NDF"])
            b_ub_base.append(tndf * 1.20 * 100.0)
        else:
            A_ub_base.append(rows["NDF"])
            b_ub_base.append(tndf * (1.10 if is_poultry else 1.15) * 100.0)

    if tadf > 0:
        A_ub_base.append(rows["ADF"])
        mult = 1.30 if is_ruminant else (1.10 if is_poultry else 1.20)
        b_ub_base.append(tadf * mult * 100.0)

    if tlys > 0:
        A_ub_base.append([-x for x in rows["Lys"]])
        b_ub_base.append(-tlys * 0.85 * 100.0)

    if tmet > 0:
        A_ub_base.append([-x for x in rows["Met"]])
        b_ub_base.append(-tmet * 0.85 * 100.0)

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
                if tca > 0:
                    A_eq.append(rows["Ca"]); b_eq.append(tca * 100.0)
                if t_p > 0:
                    A_eq.append(rows["P"]); b_eq.append(t_p * 100.0)
            elif mode.startswith("r"):
                try: tol = int(mode[1:]) / 100.0
                except ValueError: tol = 0.10
                if tca > 0:
                    A_ub.append(rows["Ca"])
                    b_ub.append(tca * (1 + tol) * 100.0)
                    A_ub.append([-x for x in rows["Ca"]])
                    b_ub.append(-tca * (1 - tol) * 100.0)
                if t_p > 0:
                    A_ub.append(rows["P"])
                    b_ub.append(t_p * (1 + tol) * 100.0)
                    A_ub.append([-x for x in rows["P"]])
                    b_ub.append(-t_p * (1 - tol) * 100.0)

            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method='highs',
                          options={'presolve': True, 'time_limit': 10})
            if res.success:
                formula = {valid[i]: res.x[i] for i in range(n)
                           if res.x[i] > 0.001}
                q, actual = evaluate_quality_weighted(
                    formula, custom_standard, animal_type, basis)
                if q > best_q:
                    best_q = q
                    best = {"success": True, "formula": formula,
                            "cost": res.fun / 100.0,
                            "actual_nutrients": actual,
                            "quality_score": q, "strategy": label,
                            "meets_standard": q >= min_quality,
                            "targets": custom_standard, "basis": basis,
                            "oil_std": oil_std,
                            "total_oil": compute_total_oil_percentage(formula)}
                if q >= 92: break
        except Exception:
            continue

    if best:
        if not best["meets_standard"]:
            best["warning"] = (f"⚠️ الجودة {best_q:.1f}% < {min_quality}%")
        return best
    return {"success": False, "message": "تعذر إيجاد حل"}


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
        new_q, new_nut = evaluate_quality_weighted(
            modified, targets, animal_type)
        deviations[nut] = {
            "delta_quality": round(new_q - base_q, 2),
            "delta_value": round(new_nut.get(nut, 0) - base.get(nut, 0), 3),
            "driver_ingredient": best_ing}
    return deviations


print(f"[Tawor v{APP_VERSION}] الجزء 1/3 — الأمان + المكتبة + المحركات ✅")
print(f"  ✅ {get_total_ingredient_count()} مكون")
print(f"  ✅ {len(GLOBAL_SAFETY_LIMITS)} قاعدة صارمة")
print(f"  ✅ {len(MEASUREMENT_METHODS)} حيوان للقياس")
# ═══════════════════════════════════════════════════════════════════════════
# بدائل الحليب
# ═══════════════════════════════════════════════════════════════════════════

MILK_REPLACER_STANDARDS = {
    "عجول (Calves)": {"CP": 24, "Fat": 20, "Lactose": 45, "Ca": .85,
        "P": .7, "Lys": 2.2, "Met": .65, "notes": "NRC 2001",
        "source": "NRC Dairy Cattle", "Ca_P_optimal": (1.2, 1.5)},
    "حملان (Lambs)": {"CP": 24, "Fat": 24, "Lactose": 40, "Ca": .9,
        "P": .7, "Lys": 2.4, "Met": .7, "notes": "≥24% دهن",
        "source": "NRC Small Ruminants", "Ca_P_optimal": (1.2, 1.6)},
    "جديان (Goat Kids)": {"CP": 24, "Fat": 24, "Lactose": 42, "Ca": .9,
        "P": .7, "Lys": 2.3, "Met": .7, "notes": "توازن خاص",
        "source": "NRC Small Ruminants", "Ca_P_optimal": (1.2, 1.6)},
    "إبل (Camels)": {"CP": 26, "Fat": 28, "Lactose": 38, "Ca": .95,
        "P": .75, "Lys": 2.5, "Met": .8, "notes": "بروتين أعلى",
        "source": "FAO Camel Nutrition", "Ca_P_optimal": (1.2, 1.5)},
    "أمهار (Foals)": {"CP": 22, "Fat": 18, "Lactose": 48, "Ca": 1.0,
        "P": .8, "Lys": 2.1, "Met": .6, "notes": "للخيل",
        "source": "NRC Horses", "Ca_P_optimal": (1.2, 1.4)},
}


MILK_REPLACER_INGREDIENTS = {
    "حليب مجفف منزوع الدسم": {"CP": 34, "Fat": 1, "Lactose": 52,
        "Ca": 1.3, "P": 1, "Lys": 2.7, "Met": .9,
        "price": 3200, "max": 60, "type": "بروتين"},
    "حليب مجفف كامل الدسم": {"CP": 26, "Fat": 28, "Lactose": 38,
        "Ca": .95, "P": .75, "Lys": 2.1, "Met": .65,
        "price": 3800, "max": 70, "type": "بروتين+دهن"},
    "شرش حليب مجفف": {"CP": 12, "Fat": 1.5, "Lactose": 75,
        "Ca": .9, "P": .75, "Lys": .9, "Met": .2,
        "price": 1800, "max": 35, "type": "كربوهيدرات"},
    "بروتين شرش WPC 80%": {"CP": 80, "Fat": 5, "Lactose": 8,
        "Ca": .5, "P": .3, "Lys": 7.5, "Met": 1.6,
        "price": 8500, "max": 25, "type": "بروتين"},
    "كازين": {"CP": 85, "Fat": 2, "Lactose": 2, "Ca": .1, "P": .5,
        "Lys": 7, "Met": 2.5, "price": 9000, "max": 20,
        "type": "بروتين"},
    "مركز بروتين صويا": {"CP": 66, "Fat": 1, "Lactose": 0,
        "Ca": .2, "P": .8, "Lys": 4.2, "Met": .9,
        "price": 2800, "max": 15, "type": "نباتي"},
    "دقيق الصويا": {"CP": 38, "Fat": 20, "Lactose": 0,
        "Ca": .2, "P": .6, "Lys": 2.4, "Met": .55,
        "price": 1500, "max": 10, "type": "نباتي"},
    "زيت جوز الهند": {"CP": 0, "Fat": 100, "Lactose": 0,
        "Ca": 0, "P": 0, "Lys": 0, "Met": 0,
        "price": 2200, "max": 15, "type": "دهن"},
    "زيت النخيل": {"CP": 0, "Fat": 100, "Lactose": 0,
        "Ca": 0, "P": 0, "Lys": 0, "Met": 0,
        "price": 1200, "max": 15, "type": "دهن"},
    "مالتودكسترين": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 0, "price": 900, "max": 10,
        "type": "كربوهيدرات"},
    "لاكتوز نقي": {"CP": 0, "Fat": 0, "Lactose": 100, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 0, "price": 1400, "max": 25,
        "type": "كربوهيدرات"},
    "ليسين L-Lysine": {"CP": 94, "Fat": 0, "Lactose": 0, "Ca": 0,
        "P": 0, "Lys": 94, "Met": 0, "price": 4200, "max": 1,
        "type": "أميني"},
    "ميثيونين": {"CP": 58, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 58, "price": 5800, "max": .8,
        "type": "أميني"},
    "بريمكس فيتامينات": {"CP": 0, "Fat": 0, "Lactose": 0,
        "Ca": 5, "P": 3, "Lys": 0, "Met": 0,
        "price": 6500, "max": 1, "type": "بريمكس"},
    "كالسيوم كربونات": {"CP": 0, "Fat": 0, "Lactose": 0,
        "Ca": 38, "P": 0, "Lys": 0, "Met": 0,
        "price": 200, "max": 2.5, "type": "معدن"},
    "فوسفات ثنائي الكالسيوم": {"CP": 0, "Fat": 0, "Lactose": 0,
        "Ca": 23, "P": 18, "Lys": 0, "Met": 0,
        "price": 1100, "max": 2.5, "type": "معدن"},
    "ملح طعام": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 0, "price": 150, "max": .5,
        "type": "معدن"},
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
        return {"success": False, "message": "3 مكونات على الأقل"}

    min_util_by_count = {3: 0.40, 4: 0.50, 5: 0.60,
                         6: 0.65, 7: 0.70, 8: 0.75}
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

    s1_ub = [
        (lac, std["Lactose"] * 1.15 * 100),
        ([-x for x in lac], -std["Lactose"] * 0.85 * 100),
        ([-x for x in lys], -std["Lys"] * 0.70 * 100),
        ([-x for x in met], -std["Met"] * 0.70 * 100),
        ([-x for x in ca], -std["Ca"] * 0.85 * 100),
        ([-x for x in p], -std["P"] * 0.85 * 100),
    ]
    strategies = [
        ("S1: صارم", [[1]*n, cp, fat],
         [100, std["CP"]*100, std["Fat"]*100],
         [u for u, _ in s1_ub], [b for _, b in s1_ub]),
        ("S2: مرن Lactose",
         [[1]*n, cp, fat],
         [100, std["CP"]*100, std["Fat"]*100],
         [lac, std["Lactose"]*1.30*100, [-x for x in lac],
          -std["Lactose"]*0.70*100, [-x for x in lys],
          -std["Lys"]*0.70*100, [-x for x in met],
          -std["Met"]*0.70*100, [-x for x in ca],
          -std["Ca"]*0.85*100, [-x for x in p],
          -std["P"]*0.85*100],
         [std["Lactose"]*1.30*100, -std["Lactose"]*0.70*100,
          -std["Lys"]*0.70*100, -std["Met"]*0.70*100,
          -std["Ca"]*0.85*100, -std["P"]*0.85*100]),
        ("S3: بدون Lys/Met",
         [[1]*n, cp, fat], [100, std["CP"]*100, std["Fat"]*100],
         [lac, [-x for x in lac], [-x for x in ca], [-x for x in p]],
         [std["Lactose"]*1.15*100, -std["Lactose"]*0.85*100,
          -std["Ca"]*0.85*100, -std["P"]*0.85*100]),
        ("S4: CP+Fat فقط",
         [[1]*n, cp, fat], [100, std["CP"]*100, std["Fat"]*100],
         [], []),
        ("S5: CP/Fat ±5%", [[1]*n], [100],
         [cp, [-x for x in cp], fat, [-x for x in fat]],
         [std["CP"]*1.05*100, -std["CP"]*0.95*100,
          std["Fat"]*1.05*100, -std["Fat"]*0.95*100]),
        ("S6: طوارئ ±15%", [[1]*n], [100],
         [cp, [-x for x in cp], fat, [-x for x in fat]],
         [std["CP"]*1.15*100, -std["CP"]*0.85*100,
          std["Fat"]*1.30*100, -std["Fat"]*0.50*100]),
    ]

    best, best_effective = None, 0.0
    for label, A_eq, b_eq, A_ub, b_ub in strategies:
        try:
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=base_bounds, method='highs',
                          options={'presolve': True, 'time_limit': 10})
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
            if cp_min <= ca_p <= cp_max: scores.append(100)
            elif cp_min*0.8 <= ca_p <= cp_max*1.3: scores.append(75)
            else: scores.append(30)

            quality = sum(scores) / len(scores) if scores else 0
            util_factor = (1.0 if used_pct >= min_util*100
                           else used_pct / (min_util*100))
            effective = quality * (0.7 + 0.3 * util_factor)

            if effective > best_effective:
                best_effective = effective
                best = {"formula": formula, "cost": res.fun / 100,
                        "cost_per_kg": res.fun / 10000,
                        "used_count": used, "used_pct": used_pct,
                        "actual": actual, "quality_score": quality,
                        "ca_p_ratio": ca_p, "strategy": label}
            if quality >= 90 and used_pct >= min_util * 100: break
        except Exception:
            continue

    if not best:
        return {"success": False, "message": "لا يوجد حل"}

    warning = None
    if best["used_pct"] < min_util * 100:
        warning = (f"⚠️ {best['used_count']}/{n} مادة — أضف مادة")

    return {"success": True, "formula": best["formula"],
            "cost_per_100kg": best["cost"],
            "cost_per_kg": best["cost_per_kg"],
            "standard": std, "actual": best["actual"],
            "animal": animal, "volume": volume,
            "used_count": best["used_count"],
            "used_pct": best["used_pct"],
            "quality_score": best["quality_score"],
            "ca_p_ratio": best["ca_p_ratio"],
            "strategy": best["strategy"], "warning": warning,
            "targets": {k: std.get(k, 0) for k in
                        ["CP", "Fat", "Lactose", "Ca", "P", "Lys", "Met"]}}


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
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 15, 5))
    variants.append(cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 15, 5))
    variants.append(cv2.fastNlMeansDenoising(clahe.apply(gray),
                                              None, 10, 7, 21))
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    variants.append(cv2.filter2D(gray, -1, kernel))
    variants.append(cv2.bitwise_not(gray))
    variants.append(cv2.morphologyEx(gray, cv2.MORPH_CLOSE,
                                      np.ones((2, 2), np.uint8)))
    return variants


def _deskew_image(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)
        coords = np.column_stack(np.where(gray > 0))
        if len(coords) < 100: return img
        angle = cv2.minAreaRect(coords)[-1]
        angle = -(90 + angle) if angle < -45 else -angle
        if abs(angle) > 15 or abs(angle) < 0.5: return img
        (h, w) = img.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_REPLICATE)
    except Exception:
        return img


def _extract_with_confidence(image):
    try:
        data = pytesseract.image_to_data(
            image, lang='ara+eng', output_type=pytesseract.Output.DICT,
            config=r'--oem 3 --psm 6')
        good_lines, current_line = [], []
        current_y = None
        for i, word in enumerate(data['text']):
            if int(data['conf'][i]) < 30: continue
            word = word.strip()
            if not word: continue
            y = data['top'][i]
            if current_y is None: current_y = y
            if abs(y - current_y) > 15:
                if current_line:
                    good_lines.append(' '.join(current_line))
                current_line = [word]
                current_y = y
            else:
                current_line.append(word)
        if current_line:
            good_lines.append(' '.join(current_line))
        return '\n'.join(good_lines), len(good_lines)
    except Exception:
        return "", 0


def _parse_ingredients_from_text(full_text):
    fixes = {'٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
             '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
             '٪': '%', ' I ': ' 1 ', ' l ': ' 1 ', '|': '1',
             'O%': '0%', 'S%': '5%', 'B%': '8%'}
    text = full_text
    for old, new in fixes.items():
        text = text.replace(old, new)

    patterns = [
        r'([\u0600-\u06FFa-zA-Z\s\(\)\-]{3,40}?)[\s:\-=:\.]+\s*(\d{1,3}\.?\d{0,2})\s*%',
        r'(\d{1,3}\.?\d{0,2})\s*%[\s:\-=:\.]+\s*([\u0600-\u06FFa-zA-Z\s\(\)\-]{3,40})',
    ]
    ingredients = {}
    for line in text.split('\n'):
        line = line.strip()
        if len(line) < 4: continue
        for pat in patterns:
            for m in re.finditer(pat, line, re.MULTILINE):
                try:
                    g = m.groups()
                    if len(g) < 2: continue
                    try: val, name = float(g[1]), g[0].strip()
                    except ValueError:
                        try: val, name = float(g[0]), g[1].strip()
                        except ValueError: continue
                    if 0.1 <= val <= 100 and len(name) > 2:
                        matched = match_ingredient_name(name)
                        if matched and matched not in ingredients:
                            ingredients[matched] = round(val, 2)
                except Exception:
                    continue
    return ingredients


def match_ingredient_name(text):
    if not text: return None
    tl = text.strip().lower()
    for cat in BIG_FEEDS_LIBRARY.values():
        for name in cat.keys():
            if name.lower() in tl or tl in name.lower():
                return name
    kw = {"ذرة": "ذرة صفراء", "ذره": "ذرة صفراء",
          "corn": "ذرة صفراء", "صويا": "كسب فول صويا 44%",
          "شعير": "شعير مطحون", "قمح": "قمح محلي",
          "نخالة": "نخالة قمح (ردة)", "ملح": "ملح الطعام",
          "حجر": "الحجر الجيري", "فوسفات": "فوسفات ثنائي الكالسيوم",
          "يوريا": "يوريا علفية", "بريمكس": "بريمكس تسمين دواجن",
          "ليسين": "ليسين نقي", "ميثيونين": "ميثيونين نقي"}
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

        h, w = img.shape[:2]
        if max(h, w) < 1500:
            scale = 1800 / max(h, w)
            img = cv2.resize(img, None, fx=scale, fy=scale,
                              interpolation=cv2.INTER_CUBIC)
        elif max(h, w) > 3500:
            scale = 3000 / max(h, w)
            img = cv2.resize(img, None, fx=scale, fy=scale,
                              interpolation=cv2.INTER_AREA)

        img = _deskew_image(img)
        variants = _preprocess_image_variants(img)
        psm_modes = ['--oem 3 --psm 6', '--oem 3 --psm 11',
                     '--oem 3 --psm 12', '--oem 3 --psm 13']
        langs = ['ara+eng', 'eng', 'ara']

        best_text, best_score, all_texts = "", 0, []
        for variant in variants:
            for lang in langs:
                for psm in psm_modes:
                    try:
                        txt, score = _extract_with_confidence(variant)
                        if score > best_score:
                            best_score, best_text = score, txt
                        if txt and len(txt) > 5:
                            all_texts.append(txt)
                    except Exception:
                        continue

        if not all_texts:
            return {"success": False, "message": "لم يتم استخراج نص"}

        full_text = "\n".join(set(all_texts))
        ingredients = _parse_ingredients_from_text(full_text)
        return {"success": True, "ingredients": ingredients,
                "raw_text": full_text, "best_text": best_text,
                "count": len(ingredients),
                "total": sum(ingredients.values()),
                "quality": "جيد" if best_score > 3 else "ضعيف",
                "variants_tried": len(variants) * len(langs) * len(psm_modes)}
    except Exception as e:
        return {"success": False, "message": f"خطأ: {e}"}


def render_ocr_correction_ui(ingredients):
    st.markdown("### ✏️ تصحيح يدوي")
    corrected = {}
    all_names = list(_get_ingredient_lookup().keys())

    if ingredients:
        for i, (name, pct) in enumerate(list(ingredients.items())):
            ca, cb, cc = st.columns([0.5, 0.3, 0.2])
            with ca:
                idx = all_names.index(name) if name in all_names else 0
                new_name = st.selectbox(f"المادة {i+1}", options=all_names,
                                          index=idx, key=f"ocr_fix_{i}")
            with cb:
                new_pct = st.number_input("النسبة %", 0.0, 100.0,
                                            float(pct), 0.5,
                                            key=f"ocr_pct_{i}")
            with cc:
                keep = st.checkbox("احتفظ", value=True, key=f"ocr_keep_{i}")
            if keep and new_pct > 0:
                corrected[new_name] = new_pct

    with st.expander("➕ إضافة"):
        cols = st.columns([0.5, 0.3, 0.2])
        with cols[0]:
            extra_name = st.selectbox("المادة:", options=["—"] + all_names,
                                        key="ocr_extra_n")
        with cols[1]:
            extra_pct = st.number_input("النسبة %", 0.0, 100.0, 0.0, 0.5,
                                          key="ocr_extra_p")
        if extra_name != "—" and extra_pct > 0:
            corrected[extra_name] = extra_pct

    if corrected:
        st.info(f"📊 الإجمالي: {sum(corrected.values()):.2f}% | "
                f"{len(corrected)} مادة")
    return corrected


# ═══════════════════════════════════════════════════════════════════════════
# الرسوم البيانية
# ═══════════════════════════════════════════════════════════════════════════

def create_colorful_bar_chart(standard, actual, keys=None):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        if keys is None:
            keys = ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH"]
        nuts = [n for n in keys if n in standard and standard[n] > 0]
        if not nuts: return None

        fig, ax = plt.subplots(figsize=(9, 4.5))
        x = np.arange(len(nuts)); width = 0.35
        b1 = ax.bar(x - width/2, [standard[n] for n in nuts], width,
                     label='المعيار', color='#1976d2',
                     edgecolor='#0d47a1', linewidth=1.5)
        b2 = ax.bar(x + width/2, [actual.get(n, 0) for n in nuts], width,
                     label='المحسوب', color='#43a047',
                     edgecolor='#1b5e20', linewidth=1.5)
        for bar in list(b1) + list(b2):
            hh = bar.get_height()
            if hh > 0:
                ax.text(bar.get_x() + bar.get_width()/2, hh, f'{hh:.1f}',
                        ha='center', va='bottom', fontsize=9,
                        fontweight='bold')
        ax.set_xlabel('العنصر', fontsize=11, fontweight='bold')
        ax.set_ylabel('القيمة', fontsize=11, fontweight='bold')
        ax.set_title('مقارنة العناصر', fontsize=13, fontweight='bold',
                     color='#1b5e20')
        ax.set_xticks(x); ax.set_xticklabels(nuts, fontsize=10)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_facecolor('#fafafa')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close(); buf.seek(0)
        return buf
    except Exception:
        return None


def create_colorful_pie_chart(formula):
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2: return None
    try:
        colors = ['#e53935', '#8e24aa', '#3949ab', '#1e88e5', '#00897b',
                  '#43a047', '#7cb342', '#fdd835', '#fb8c00', '#6d4c41']
        names = list(formula.keys()); vals = list(formula.values())
        fig, ax = plt.subplots(figsize=(8, 5))
        _, _, autotexts = ax.pie(
            vals, autopct='%1.1f%%', colors=colors[:len(names)],
            startangle=90, pctdistance=0.75,
            wedgeprops=dict(edgecolor='white', linewidth=2))
        for t in autotexts:
            t.set_color('white'); t.set_fontweight('bold'); t.set_fontsize(9)
        ax.legend(names, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
                  fontsize=9)
        ax.set_title('توزيع المكونات', fontsize=13, fontweight='bold',
                     color='#1b5e20')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close(); buf.seek(0)
        return buf
    except Exception:
        return None


def create_radar_chart(standard, actual, keys=None):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        if keys is None:
            keys = ["CP", "DP", "SE", "NDF", "ADF", "EE", "Ca", "P"]
        nuts = [n for n in keys if n in standard and standard[n] > 0]
        if len(nuts) < 3: return None
        std_norm = [100.0] * len(nuts)
        act_norm = [(actual.get(n, 0) / standard[n]) * 100 for n in nuts]
        angles = np.linspace(0, 2 * np.pi, len(nuts),
                             endpoint=False).tolist()
        std_norm += std_norm[:1]; act_norm += act_norm[:1]
        angles += angles[:1]
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, std_norm, 'o-', linewidth=2.5,
                color='#1976d2', label='المعيار')
        ax.fill(angles, std_norm, alpha=0.15, color='#1976d2')
        ax.plot(angles, act_norm, 'o-', linewidth=2.5,
                color='#43a047', label='المحسوب')
        ax.fill(angles, act_norm, alpha=0.25, color='#43a047')
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(nuts, fontsize=10)
        ax.set_ylim(0, max(max(std_norm), max(act_norm)) * 1.2)
        ax.set_title('المقارنة %', fontsize=12, fontweight='bold',
                     color='#1b5e20', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
        ax.grid(True, alpha=0.3); ax.set_facecolor('#fafafa')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close(); buf.seek(0)
        return buf
    except Exception:
        return None


def create_gauge_chart(score):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        fig, ax = plt.subplots(figsize=(4, 4),
                                subplot_kw=dict(aspect='equal'))
        colors = ['#c62828', '#ef6c00', '#f9a825',
                  '#7cb342', '#43a047', '#1b5e20']
        for i, c in enumerate(colors):
            t1 = 180 - (i * 30); t2 = 180 - ((i + 1) * 30)
            ax.add_patch(Wedge((0, 0), 1, t2, t1, width=0.3,
                                facecolor=c, edgecolor='white',
                                linewidth=2))
        angle = 180 - (score / 100) * 180
        rad = np.radians(angle)
        ax.plot([0, 0.85 * np.cos(rad)], [0, 0.85 * np.sin(rad)],
                color='#1a1a1a', linewidth=3, zorder=10)
        ax.add_patch(Circle((0, 0), 0.08, color='#1a1a1a', zorder=11))
        ax.text(0, -0.25, f'{score:.0f}%', ha='center', fontsize=20,
                fontweight='bold', color='#1b5e20')
        ax.text(0, -0.5, 'التقييم', ha='center', fontsize=11, color='#666')
        ax.set_xlim(-1.2, 1.2); ax.set_ylim(-0.7, 1.2); ax.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close(); buf.seek(0)
        return buf
    except Exception:
        return None


def create_horizontal_bar_chart(formula):
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2: return None
    try:
        sorted_pairs = sorted(formula.items(),
                               key=lambda x: x[1], reverse=True)
        names = [p[0] for p in sorted_pairs]
        vals = [p[1] for p in sorted_pairs]
        colors = ['#e53935', '#8e24aa', '#3949ab', '#1e88e5', '#00897b',
                  '#43a047', '#7cb342', '#fdd835', '#fb8c00', '#6d4c41']
        fig, ax = plt.subplots(figsize=(9, max(4, len(names) * 0.4)))
        bars = ax.barh(names, vals, color=colors[:len(names)],
                        edgecolor='#333')
        for bar in bars:
            hh = bar.get_width()
            ax.text(hh + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{hh:.1f}%', ha='left', va='center', fontsize=9,
                    fontweight='bold')
        ax.set_xlabel('النسبة %', fontsize=11, fontweight='bold')
        ax.set_title('توزيع المكونات', fontsize=13, fontweight='bold',
                     color='#1b5e20')
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.set_facecolor('#fafafa'); ax.invert_yaxis()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close(); buf.seek(0)
        return buf
    except Exception:
        return None


def create_ca_p_ratio_chart(ca, p, target_ca=0, target_p=0):
    if not MATPLOTLIB_AVAILABLE or p <= 0: return None
    try:
        ratio = ca / p
        fig, ax = plt.subplots(figsize=(8, 3))
        zones = [(0, .8, '#b71c1c'), (.8, 1.2, '#ef6c00'),
                 (1.2, 1.5, '#f9a825'), (1.5, 2.0, '#2e7d32'),
                 (2.0, 3.0, '#f9a825'), (3.0, 5.0, '#ef6c00'),
                 (5.0, 8.0, '#b71c1c')]
        for x0, x1, c in zones:
            ax.axvspan(x0, x1, alpha=0.35, color=c,
                       edgecolor='white', linewidth=0)
        ratio_clipped = min(ratio, 7.9)
        ax.axvline(ratio_clipped, color='#0d47a1', linewidth=4, zorder=10)
        ax.scatter([ratio_clipped], [0.5], s=350, color='#0d47a1',
                    zorder=11, edgecolors='white', linewidth=3)
        ax.text(ratio_clipped, 0.85, f'{ratio:.2f}', ha='center',
                va='bottom', fontsize=18, fontweight='bold',
                color='#0d47a1',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                          edgecolor='#0d47a1', linewidth=2))
        ax.set_xlim(0, 8); ax.set_ylim(0, 1.2); ax.set_yticks([])
        ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8])
        ax.set_xlabel('Ca : P', fontsize=12, fontweight='bold')
        ax.set_title(f'Ca:P — Ca={ca:.2f}% | P={p:.2f}%',
                     fontsize=12, fontweight='bold', color='#1b5e20', pad=15)
        if 1.5 <= ratio <= 2.0: label, color = '✅ مثالية', '#1b5e20'
        elif 1.2 <= ratio < 1.5 or 2.0 < ratio <= 3.0:
            label, color = '⚠️ مقبولة', '#f57c00'
        elif 0.8 <= ratio < 1.2 or 3.0 < ratio <= 5.0:
            label, color = '🟠 خارج', '#e65100'
        else: label, color = '❌ خطرة', '#c62828'
        ax.text(0.02, 0.05, label, transform=ax.transAxes,
                fontsize=13, fontweight='bold', color=color,
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                          edgecolor=color, linewidth=2))
        ax.grid(axis='x', alpha=0.2, linestyle=':')
        ax.set_facecolor('#fafafa'); plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=130, bbox_inches='tight',
                    facecolor='white')
        plt.close(); buf.seek(0)
        return buf
    except Exception:
        return None


def create_quality_breakdown_chart(rows):
    if not MATPLOTLIB_AVAILABLE or not rows: return None
    try:
        labels = [r["العنصر"] for r in rows[:9]]
        scores = [r.get("score", 50) for r in rows[:9]]
        colors = []
        for s in scores:
            if s >= 95: colors.append('#1b5e20')
            elif s >= 85: colors.append('#43a047')
            elif s >= 70: colors.append('#7cb342')
            elif s >= 55: colors.append('#f9a825')
            else: colors.append('#c62828')
        fig, ax = plt.subplots(figsize=(9, 4))
        bars = ax.bar(labels, scores, color=colors, edgecolor='#333',
                       linewidth=1.5)
        for bar in bars:
            hh = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, hh, f'{hh:.0f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax.axhline(y=70, color='#c62828', linestyle='--', linewidth=2,
                    label='حد 70%')
        ax.set_ylim(0, 105)
        ax.set_ylabel('الدرجة', fontsize=11, fontweight='bold')
        ax.set_title('تقييم العناصر', fontsize=13, fontweight='bold',
                     color='#1b5e20')
        ax.legend(loc='lower right')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_facecolor('#fafafa')
        plt.xticks(rotation=30, ha='right')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close(); buf.seek(0)
        return buf
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# PDFGenerator
# ═══════════════════════════════════════════════════════════════════════════

class PDFGenerator:
    def __init__(self):
        self.font_name = font_mgr.font_name
        self.logo_path = None
        for lp in LOGO_OPTIONS + PHOTO_OPTIONS:
            if os.path.exists(lp):
                self.logo_path = lp; break

    def _ar(self, t):
        if t is None: return ""
        try:
            return get_display(arabic_reshaper.reshape(str(t)),
                                base_dir='R')
        except Exception:
            return str(t)

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
                    canvas_obj.drawImage(self.logo_path, 30, h - 78,
                        width=60, height=60,
                        preserveAspectRatio=True, anchor='sw', mask='auto')
            except Exception:
                pass

            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 22)
            canvas_obj.drawCentredString(
                w/2, h - 38, self._ar("تاور نولجي  Tawor Nology"))
            canvas_obj.setFont(self.font_name, 12)
            canvas_obj.setFillColor(HexColor('#e8f5e9'))
            canvas_obj.drawCentredString(
                w/2, h - 58,
                self._ar("للإنتاج الحيواني وتغذية الحيوان"))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.drawCentredString(
                w/2, h - 76, self._ar(f"إشراف: {SUPERVISOR}"))

            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, 42, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.rect(0, 84, w, 3, fill=1, stroke=0)

            canvas_obj.setFillColor(HexColor('#ffeb3b'))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.drawCentredString(
                w/2, 68, self._ar(f"🤲 {DUA_SHORT} 🤲"))

            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(
                w/2, 27, self._ar(f"{APP_NAME} © 2026"))
            canvas_obj.setFont(self.font_name, 7)
            canvas_obj.drawCentredString(
                w/2, 12,
                self._ar(f"صفحة {canvas_obj.getPageNumber()} | "
                          f"جميع الحقوق محفوظة"))
            canvas_obj.restoreState()
        except Exception:
            pass

    def _comparison_table(self, std, calc):
        labels = {"CP": "بروتين CP", "DP": "مهضوم DP", "SE": "SE",
                  "NDF": "NDF", "ADF": "ADF", "EE": "دهن",
                  "ASH": "رماد", "Ca": "Ca", "P": "P"}
        data = [[self._ar(x) for x in
                 ["العنصر", "المعيار", "المحسوب", "الفرق", "%", "التقييم"]]]
        cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#9e9e9e')),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7)]
        row = 1
        for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
            if k not in std or std[k] == 0: continue
            sv, cv = std[k], calc.get(k, 0)
            diff = cv - sv; pct = (diff / sv * 100) if sv else 0
            ev = evaluate_difference(pct, standard_value=sv)
            data.append([self._ar(labels[k]), f"{sv:.2f}", f"{cv:.2f}",
                          f"{diff:+.3f}", f"{pct:+.2f}%",
                          self._ar(ev["label"])])
            cmds.append(('BACKGROUND', (0, row), (-1, row),
                          HexColor(ev["bg"])))
            row += 1
        t = Table(data, colWidths=[100, 70, 70, 70, 70, 105])
        t.setStyle(TableStyle(cmds))
        return t

    def generate_report(self, formula, requirement, animal_type, breed,
                        cost, city, local_cost, local_sym,
                        requester_name="", protein_basis="DP",
                        standard_key="", include_charts=True,
                        quality_score=0.0):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
                                leftMargin=40, topMargin=115,
                                bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text), ParagraphStyle(
                's', fontName=self.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))

        story.append(P("تقرير فني رسمي — تركيب علفة", size=20,
                       align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
                                color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))

        client = [
            [self._ar("👤 طالب الخدمة:"), self._ar(requester_name or "—")],
            [self._ar("📍 الموقع:"), self._ar(city)],
            [self._ar("🐾 الفصيل:"),
             self._ar(f"{animal_type} — {breed}")],
            [self._ar("🧬 الأساس:"), self._ar(protein_basis)],
            [self._ar("📅 التاريخ:"),
             datetime.now().strftime('%Y-%m-%d')]]
        ct = Table(client, colWidths=[150, 340])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
            ('BACKGROUND', (1, 0), (1, -1), HexColor('#fafafa')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')),
            ('INNERGRID', (0, 0), (-1, -1), 0.6, HexColor('#c8e6c9')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 9)]))
        story.append(ct)
        story.append(Spacer(1, 15))

        std_vals = requirement_to_standard(requirement)
        calc_vals = compute_formula_nutrients(formula)

        qd = [[self._ar("الجودة"), self._ar("الحالة")],
              [f"{quality_score:.1f}%",
               self._ar("✅ ناجح" if quality_score >= 70
                        else "⚠️ يحتاج تحسين")]]
        qt = Table(qd, colWidths=[200, 290])
        qt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565c0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('BACKGROUND', (0, 1), (-1, -1),
             HexColor('#e8f5e9' if quality_score >= 70 else '#ffebee')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#1976d2')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 8)]))
        story.append(qt)
        story.append(Spacer(1, 15))

        story.append(P("📊 مقارنة العناصر", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        story.append(self._comparison_table(std_vals, calc_vals))
        story.append(Spacer(1, 15))

        if include_charts:
            story.append(PageBreak())
            story.append(P("📈 الرسوم", size=14, color='#1b5e20'))
            story.append(Spacer(1, 10))
            for chart_fn, args in [
                (create_colorful_bar_chart, (std_vals, calc_vals)),
                (create_colorful_pie_chart, (formula,))]:
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
        story.append(P("💰 التكاليف", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        cost_data = [[self._ar("البند"), self._ar("القيمة")],
                     [self._ar("التكلفة/طن"), f"${cost:.2f}"],
                     [self._ar(f"({local_sym})"),
                      f"{local_cost:,.2f}"]]
        tc = Table(cost_data, colWidths=[280, 210])
        tc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#2e7d32')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('PADDING', (0, 0), (-1, -1), 8)]))
        story.append(tc)
        story.append(Spacer(1, 18))

        if formula:
            story.append(P("🌾 المكونات للطن", size=14, color='#1b5e20'))
            story.append(Spacer(1, 8))
            ing_data = [[self._ar("المكون"), self._ar("%"),
                         self._ar("كجم/طن")]]
            for ing, pct in formula.items():
                ing_data.append([self._ar(ing), f"{pct:.2f}%",
                                  f"{pct * 10:.1f}"])
            ti = Table(ing_data, colWidths=[270, 110, 110])
            ti.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                 [HexColor('#ffffff'), HexColor('#f5f5f5')])]))
            story.append(ti)

        doc.build(story, onFirstPage=self._draw_page,
                  onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_ocr_report(self, ingredients, nutrients, raw_text=""):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
                                leftMargin=40, topMargin=115,
                                bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text), ParagraphStyle(
                's', fontName=self.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))

        story.append(P("تقرير OCR", size=20, align=TA_CENTER,
                       color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
                                color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))
        story.append(P(f"📅 {datetime.now():%Y-%m-%d %H:%M}", size=11))
        story.append(Spacer(1, 12))

        data = [[self._ar("المادة"), self._ar("%")]]
        for k, v in ingredients.items():
            data.append([self._ar(k), f"{v:.2f}%"])
        data.append([self._ar("الإجمالي"),
                      f"{sum(ingredients.values()):.2f}%"])
        t = Table(data, colWidths=[300, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#ffe0b2'))]))
        story.append(t)

        doc.build(story, onFirstPage=self._draw_page,
                  onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()


pdf_gen = PDFGenerator()


# ═══════════════════════════════════════════════════════════════════════════
# PDFs إضافية
# ═══════════════════════════════════════════════════════════════════════════

def generate_measurement_pdf(feed: Dict) -> Optional[bytes]:
    if not REPORTLAB_AVAILABLE: return None
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40,
                                leftMargin=40, topMargin=115,
                                bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(ar(text), ParagraphStyle(
                's', fontName=font_mgr.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))

        story.append(P("تقرير العلف اليومي", size=20, align=TA_CENTER,
                       color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
                                color=HexColor('#d4af37')))
        story.append(Spacer(1, 15))

        rows = [[ar("البند"), ar("القيمة")]]
        for label, val in [
            ("الوزن", f"{feed['weight_kg']} كجم"),
            ("الحالة", feed['stage']),
            ("DMI", f"{feed['dmi_kg']} كجم/يوم"),
            ("النطاق",
             f"{feed['dmi_range'][0]}–{feed['dmi_range'][1]} كجم"),
            ("المركزات",
             f"{feed['concentrate_kg']} كجم "
             f"({feed['concentrate_pct']}%)"),
            ("الخشنة", f"{feed['roughage_kg']} كجم"),
            ("المرجع", feed['source'])]:
            rows.append([ar(label), ar(val)])

        t = Table(rows, colWidths=[200, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 8)]))
        story.append(t)

        doc.build(story, onFirstPage=pdf_gen._draw_page,
                  onLaterPages=pdf_gen._draw_page)
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return None


def generate_validation_pdf_report(validation, formula):
    if not REPORTLAB_AVAILABLE: return None
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40,
                                leftMargin=40, topMargin=115,
                                bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(ar(text), ParagraphStyle(
                's', fontName=font_mgr.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))

        story.append(P("تقرير التحقق من الحدود", size=20,
                       align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
                                color=HexColor('#d4af37')))
        story.append(Spacer(1, 15))

        lim_rows = [[ar(x) for x in
                     ["المكوّن", "الفعلية %", "الحد", "المرجع", "الحالة"]]]
        for ing, pct in formula.items():
            lim = GLOBAL_SAFETY_LIMITS.get(ing)
            if not lim:
                lim_rows.append([ar(ing), f"{pct:.2f}%", "—", "—", "—"])
                continue
            if lim["type"] == "choice":
                allowed = " / ".join(f"{x}%" for x in lim["options"])
                ok = any(abs(pct - x) < 0.01 for x in lim["options"])
            elif lim["type"] == "max":
                allowed = f"≤ {lim['max']}%"
                ok = pct <= lim["max"]
            else:
                allowed = f"{lim.get('min', 0)}–{lim['max']}%"
                ok = lim.get("min", 0) <= pct <= lim["max"]
            lim_rows.append([ar(ing), f"{pct:.2f}%", allowed,
                              ar(lim["source"]), "✅" if ok else "❌"])

        t = Table(lim_rows, colWidths=[110, 70, 100, 130, 40])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.6, HexColor('#9e9e9e')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6)]))
        story.append(t)
        story.append(Spacer(1, 15))

        if validation["corrections"]:
            story.append(P("🔧 التصحيحات", size=14, color='#c62828'))
            story.append(Spacer(1, 8))
            corr_rows = [[ar(x) for x in
                          ["المكوّن", "قبل", "بعد", "السبب"]]]
            for c in validation["corrections"]:
                corr_rows.append([ar(c["ingredient"]),
                                   f"{c['from']:.2f}%",
                                   f"{c['to']:.2f}%",
                                   ar(c["reason"])])
            tc = Table(corr_rows, colWidths=[90, 60, 60, 240])
            tc.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#c62828')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('GRID', (0, 0), (-1, -1), 0.6, HexColor('#e0e0e0')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('PADDING', (0, 0), (-1, -1), 6)]))
            story.append(tc)

        doc.build(story, onFirstPage=pdf_gen._draw_page,
                  onLaterPages=pdf_gen._draw_page)
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return None


def generate_milk_replacer_pdf(result):
    if not REPORTLAB_AVAILABLE: return None
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
                                leftMargin=40, topMargin=115,
                                bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(ar(text), ParagraphStyle(
                's', fontName=font_mgr.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))

        std = result["standard"]
        targets = result["targets"]
        actual = result["actual"]
        quality = result["quality_score"]
        formula = result["formula"]
        volume = result.get("volume", 100.0)

        story.append(P("تقرير بديل الحليب", size=20, align=TA_CENTER,
                       color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
                                color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))

        info = [[ar("الحيوان:"), ar(result["animal"])],
                [ar("المرجع:"), ar(std.get("source", ""))],
                [ar("الجودة:"), f"{quality:.1f}%"],
                [ar("Ca:P:"), f"{result['ca_p_ratio']:.2f}"]]
        ct = Table(info, colWidths=[160, 330])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e3f2fd')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#1565c0')),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('PADDING', (0, 0), (-1, -1), 7)]))
        story.append(ct)
        story.append(Spacer(1, 15))

        comp_data = [[ar(x) for x in
                      ["العنصر", "المعيار", "المحسوب", "التقييم"]]]
        for k, lab in {"CP": "بروتين", "Fat": "دهن", "Lactose": "لاكتوز",
                       "Ca": "Ca", "P": "P"}.items():
            t_val = targets.get(k, 0); a_val = actual.get(k, 0)
            if t_val <= 0: continue
            diff = (a_val - t_val) / t_val * 100
            ev = evaluate_difference(diff, standard_value=t_val)
            comp_data.append([ar(lab), f"{t_val:.2f}",
                              f"{a_val:.2f}", ar(ev["label"])])

        comp_table = Table(comp_data, colWidths=[100, 100, 100, 150])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('PADDING', (0, 0), (-1, -1), 6)]))
        story.append(comp_table)

        story.append(PageBreak())
        story.append(P("🍼 المكونات", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))

        ing_data = [[ar(x) for x in
                     ["المكون", "%", f"كجم /{volume:.0f}"]]]
        for ing, pct in formula.items():
            kg = pct * volume / 100
            ing_data.append([ar(ing), f"{pct:.2f}%", f"{kg:.2f}"])

        ing_table = Table(ing_data, colWidths=[200, 80, 100])
        ing_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name)]))
        story.append(ing_table)

        doc.build(story, onFirstPage=pdf_gen._draw_page,
                  onLaterPages=pdf_gen._draw_page)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception:
        return None


def generate_invoice_pdf(inv):
    if not REPORTLAB_AVAILABLE: return None
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40,
                                leftMargin=40, topMargin=115,
                                bottomMargin=145)
        story = []

        def P(t, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(ar(t), ParagraphStyle(
                'i', fontName=font_mgr.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))

        story.append(P("فاتورة ضريبية", size=22, align=TA_CENTER,
                       color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2,
                                color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))

        info = [[ar("رقم:"), ar(inv["number"])],
                [ar("التاريخ:"), ar(inv["date"])],
                [ar("العميل:"), ar(inv["client"])]]
        t = Table(info, colWidths=[150, 340])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('PADDING', (0, 0), (-1, -1), 8)]))
        story.append(t)
        story.append(Spacer(1, 15))

        rows = [[ar(x) for x in
                 ["البند", "الكمية", "السعر", "الإجمالي"]]]
        for it in inv["items"]:
            line = it["الكمية (طن)"] * it["سعر الطن"]
            rows.append([ar(str(it["البند"])),
                          f"{it['الكمية (طن)']:.2f}",
                          f"${it['سعر الطن']:,.2f}",
                          f"${line:,.2f}"])
        rows.append([ar("الإجمالي"), "", "",
                      f"${inv['total']:,.2f}"])

        ti = Table(rows, colWidths=[220, 80, 90, 100])
        ti.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#bdbdbd')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#ffeb3b'))]))
        story.append(ti)

        doc.build(story, onFirstPage=pdf_gen._draw_page,
                  onLaterPages=pdf_gen._draw_page)
        return buf.getvalue()
    except Exception:
        return None


def generate_letterhead_pdf(title_line, sub_line):
    if not REPORTLAB_AVAILABLE: return None
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=50,
                                leftMargin=50, topMargin=115,
                                bottomMargin=145)
        story = []
        story.append(Spacer(1, 80))
        story.append(Paragraph(ar(title_line), ParagraphStyle(
            't', fontName=font_mgr.font_name, fontSize=32,
            alignment=TA_CENTER, textColor=HexColor('#1b5e20'),
            leading=42)))
        story.append(Spacer(1, 15))
        story.append(Paragraph(ar(sub_line), ParagraphStyle(
            's', fontName=font_mgr.font_name, fontSize=16,
            alignment=TA_CENTER, textColor=HexColor('#1565C0'))))
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="70%", thickness=2.5,
                                 color=HexColor('#d4af37'),
                                 hAlign='CENTER'))
        story.append(Spacer(1, 40))
        story.append(Paragraph(ar(SUPERVISOR), ParagraphStyle(
            'n', fontName=font_mgr.font_name, fontSize=22,
            alignment=TA_CENTER, textColor=HexColor('#c62828'))))

        doc.build(story, onFirstPage=pdf_gen._draw_page,
                  onLaterPages=pdf_gen._draw_page)
        return buf.getvalue()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# الحظائر — BARN_DESIGN_STANDARDS
# ═══════════════════════════════════════════════════════════════════════════

BARN_DESIGN_STANDARDS = {
    "دواجن_لاحم": {"name_ar": "دواجن لاحم", "area_per_head": 0.10,
        "feeder_cm_per_head": 5.0, "drinker_cm_per_head": 2.5,
        "height_m": 2.8, "width_m": 12.0,
        "ach_summer": 60, "ach_winter": 8, "vent_open_ratio": 0.20,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "خطية", "drinker_type": "حلمات",
        "aisle_m": 1.2, "central_aisle": True,
        "temp_optimal_c": 24, "humidity_optimal": 60},
    "دواجن_بياض": {"name_ar": "دواجن بياض", "area_per_head": 0.15,
        "feeder_cm_per_head": 10.0, "drinker_cm_per_head": 2.5,
        "height_m": 3.0, "width_m": 12.0,
        "ach_summer": 40, "ach_winter": 6, "vent_open_ratio": 0.20,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "سلسلة", "drinker_type": "حلمات",
        "aisle_m": 1.2, "central_aisle": True,
        "temp_optimal_c": 22, "humidity_optimal": 60},
    "سمان": {"name_ar": "سمان", "area_per_head": 0.025,
        "feeder_cm_per_head": 2.0, "drinker_cm_per_head": 1.0,
        "height_m": 2.0, "width_m": 6.0,
        "ach_summer": 50, "ach_winter": 8, "vent_open_ratio": 0.25,
        "roof_type": "mono", "slope_pct": 15.0,
        "feeder_type": "خطية", "drinker_type": "حلمات",
        "aisle_m": 0.8, "central_aisle": False,
        "temp_optimal_c": 26, "humidity_optimal": 65},
    "أغنام": {"name_ar": "أغنام", "area_per_head": 1.5,
        "feeder_cm_per_head": 35.0, "drinker_cm_per_head": 4.0,
        "height_m": 3.5, "width_m": 10.0,
        "ach_summer": 30, "ach_winter": 5, "vent_open_ratio": 0.30,
        "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "خرسانية", "drinker_type": "حوض",
        "aisle_m": 2.0, "central_aisle": True,
        "temp_optimal_c": 18, "humidity_optimal": 65},
    "ماعز": {"name_ar": "ماعز", "area_per_head": 1.5,
        "feeder_cm_per_head": 35.0, "drinker_cm_per_head": 4.0,
        "height_m": 3.5, "width_m": 10.0,
        "ach_summer": 30, "ach_winter": 5, "vent_open_ratio": 0.30,
        "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "مرتفعة", "drinker_type": "حوض",
        "aisle_m": 2.0, "central_aisle": True,
        "temp_optimal_c": 20, "humidity_optimal": 65},
    "أبقار": {"name_ar": "أبقار", "area_per_head": 5.0,
        "feeder_cm_per_head": 70.0, "drinker_cm_per_head": 6.0,
        "height_m": 4.5, "width_m": 15.0,
        "ach_summer": 25, "ach_winter": 4, "vent_open_ratio": 0.35,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "وسطية", "drinker_type": "حوض",
        "aisle_m": 3.5, "central_aisle": True,
        "temp_optimal_c": 15, "humidity_optimal": 65},
    "إبل": {"name_ar": "إبل", "area_per_head": 10.0,
        "feeder_cm_per_head": 100.0, "drinker_cm_per_head": 8.0,
        "height_m": 4.5, "width_m": 15.0,
        "ach_summer": 20, "ach_winter": 4, "vent_open_ratio": 0.40,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "مرتفعة", "drinker_type": "حوض كبير",
        "aisle_m": 4.0, "central_aisle": True,
        "temp_optimal_c": 25, "humidity_optimal": 50},
    "خيول": {"name_ar": "خيول", "area_per_head": 16.0,
        "feeder_cm_per_head": 100.0, "drinker_cm_per_head": 10.0,
        "height_m": 4.0, "width_m": 15.0,
        "ach_summer": 25, "ach_winter": 5, "vent_open_ratio": 0.30,
        "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "مرتفعة", "drinker_type": "حوض",
        "aisle_m": 3.5, "central_aisle": True,
        "temp_optimal_c": 18, "humidity_optimal": 60},
    "أرانب": {"name_ar": "أرانب", "area_per_head": 0.30,
        "feeder_cm_per_head": 8.0, "drinker_cm_per_head": 2.0,
        "height_m": 2.5, "width_m": 8.0,
        "ach_summer": 40, "ach_winter": 6, "vent_open_ratio": 0.25,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "معدنية", "drinker_type": "نبل",
        "aisle_m": 1.2, "central_aisle": True,
        "temp_optimal_c": 20, "humidity_optimal": 65},
    "أسماك_أحواض": {"name_ar": "أسماك", "area_per_head": 1.5,
        "feeder_cm_per_head": 0.0, "drinker_cm_per_head": 0.0,
        "height_m": 1.5, "width_m": 20.0,
        "ach_summer": 0, "ach_winter": 0, "vent_open_ratio": 0.0,
        "roof_type": "none", "slope_pct": 0.0,
        "feeder_type": "نثر", "drinker_type": "—",
        "aisle_m": 2.0, "central_aisle": False,
        "temp_optimal_c": 28, "humidity_optimal": 0},
}


def calculate_barn_dimensions(key, count):
    std = BARN_DESIGN_STANDARDS.get(key)
    if not std: return None
    area = count * std["area_per_head"]
    width = std["width_m"]
    length = max(area / width, 6.0)
    feeders = max(1, int(np.ceil(count * std["feeder_cm_per_head"] / 300)))
    drinkers = max(1, int(np.ceil(count * std["drinker_cm_per_head"] / 200)))
    volume = length * width * std["height_m"]
    roof_rise = (width / 2) * (std["slope_pct"] / 100)
    ridge = std["height_m"] + roof_rise

    if key in ["دواجن_لاحم", "دواجن_بياض", "سمان"]:
        apr = max(2, int(length / 0.3))
    elif key == "أرانب":
        apr = max(2, int(length / 0.5))
    else:
        apr = max(2, int(length / 1.5))

    return {"standard": std, "count": count,
            "total_area_m2": round(area, 2),
            "length_m": round(length, 2),
            "width_m": round(width, 2),
            "height_m": std["height_m"],
            "ridge_height_m": round(ridge, 2),
            "roof_type": std["roof_type"], "slope_pct": std["slope_pct"],
            "feeders_count": feeders, "drinkers_count": drinkers,
            "total_feeder_length_m": round(
                count * std["feeder_cm_per_head"] / 100, 1),
            "total_drinker_length_m": round(
                count * std["drinker_cm_per_head"] / 100, 1),
            "volume_m3": round(volume, 1),
            "vent_flow_summer_m3h": int(volume * std["ach_summer"]),
            "vent_flow_winter_m3h": int(volume * std["ach_winter"]),
            "vent_open_area_m2": round(
                length * std["height_m"] * std["vent_open_ratio"], 2),
            "animals_per_row": apr,
            "feeder_type": std.get("feeder_type", "خطية"),
            "drinker_type": std.get("drinker_type", "حوض"),
            "aisle_m": std.get("aisle_m", 1.5),
            "central_aisle": std.get("central_aisle", True),
            "temp_optimal": std.get("temp_optimal_c", 20),
            "humidity_optimal": std.get("humidity_optimal", 60)}


def create_barn_with_pens_3d(dims, n_pens=4, pens_per_row=2, expert=False):
    """حظيرة 3D بألوان صريحة وفتحات تهوية مرئية."""
    if not PLOTLY_AVAILABLE: return None

    L = float(dims["length_m"]); W = float(dims["width_m"])
    H = float(dims["height_m"]); RH = float(dims["ridge_height_m"])
    total = dims["count"]
    n_pens = max(1, min(n_pens, total))
    pens_per_row = max(1, min(pens_per_row, n_pens))
    per_pen = max(1, total // n_pens)
    n_rows = (n_pens + pens_per_row - 1) // pens_per_row

    aisle = dims.get("aisle_m", 1.5)
    margin = 1.0
    usable_l = max(L - 2 * margin, 2.0)
    usable_w = max(W - 2 * margin, 2.0)
    if dims.get("central_aisle", True) and W > 8:
        usable_w -= aisle

    pen_w = usable_w / pens_per_row
    pen_d = usable_l / n_rows

    fig = go.Figure()

    # أرضية
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[0, 0, W, W], z=[0, 0, 0, 0],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color='#EEEEEE', opacity=0.55,
        name='🏠 الأرضية', showlegend=True, hoverinfo='skip'))

    # جدران شبه شفافة
    for xp in [0, L]:
        fig.add_trace(go.Mesh3d(
            x=[xp]*4, y=[0, W, W, 0], z=[0, 0, H, H],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color='#8D6E63', opacity=0.10,
            showlegend=False, hoverinfo='skip'))
    for yp in [0, W]:
        fig.add_trace(go.Mesh3d(
            x=[0, L, L, 0], y=[yp]*4, z=[0, 0, H, H],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color='#8D6E63', opacity=0.10,
            showlegend=False, hoverinfo='skip'))

    # سقف
    if dims["roof_type"] == "gable":
        fig.add_trace(go.Mesh3d(
            x=[0, L, L, 0], y=[0, 0, W/2, W/2],
            z=[H, H, RH, RH], i=[0, 0], j=[1, 2], k=[2, 3],
            color='#6D4C41', opacity=0.15,
            showlegend=False, hoverinfo='skip'))
        fig.add_trace(go.Mesh3d(
            x=[0, L, L, 0], y=[W/2, W/2, W, W],
            z=[RH, RH, H, H], i=[0, 0], j=[1, 2], k=[2, 3],
            color='#6D4C41', opacity=0.15,
            showlegend=False, hoverinfo='skip'))

    status_colors = {"ok": "#43A047", "warn": "#FBC02D",
                     "full": "#E53935", "empty": "#9E9E9E"}
    status_names = {"ok": "✅ سليم", "warn": "🟡 قريب",
                    "full": "🔴 مزدحم", "empty": "⚪ فارغ"}

    pens = []
    for i in range(n_pens):
        row = i // pens_per_row
        col = i % pens_per_row
        x0 = margin + col * pen_w
        z0 = margin + row * pen_d
        x1 = x0 + pen_w * 0.94
        z1 = z0 + pen_d * 0.94

        density = 1.0 if i == 0 else 0.65 + (i % 4) * 0.12
        density = min(1.15, density)
        actual = int(per_pen * density)

        if actual == 0: status = "empty"
        elif density < 0.85: status = "ok"
        elif density < 1.0: status = "warn"
        else: status = "full"

        pens.append({"num": i + 1, "x0": x0, "x1": x1,
                     "z0": z0, "z1": z1, "actual": actual,
                     "capacity": per_pen, "density": density,
                     "status": status})

    for idx, p in enumerate(pens):
        color = status_colors[p["status"]]
        show_legend = (idx < 4)
        hover = (f"<b>ساحة {p['num']}</b><br>"
                 f"{p['actual']} / {p['capacity']}<br>"
                 f"{p['density']*100:.0f}%")
        fig.add_trace(go.Mesh3d(
            x=[p["x0"], p["x1"], p["x1"], p["x0"]],
            y=[p["z0"], p["z0"], p["z1"], p["z1"]],
            z=[0.02]*4, i=[0, 0], j=[1, 2], k=[2, 3],
            color=color, opacity=0.72,
            name=f"🔲 ساحة {p['num']} — {status_names[p['status']]}",
            hovertext=hover, hoverinfo='text',
            showlegend=show_legend))

        cx = (p["x0"] + p["x1"]) / 2
        cz = (p["z0"] + p["z1"]) / 2
        label = f"<b>{p['num']}</b>"
        if expert:
            label += f"<br>{p['actual']}/{p['capacity']}"
        fig.add_trace(go.Scatter3d(
            x=[cx], y=[cz], z=[0.55],
            mode='text', text=[label],
            textfont=dict(size=15, color='#212121'),
            showlegend=False, hoverinfo='skip'))

    # العلافات — برتقالي فاقع
    if dims.get("central_aisle", True) and W > 8:
        feeder_y = [aisle/2, W - aisle/2]
    else:
        feeder_y = [0.6, W - 0.6]

    for fi, fy in enumerate(feeder_y):
        fw = 0.5; fh = 0.35
        fig.add_trace(go.Mesh3d(
            x=[0.5, L-0.5, L-0.5, 0.5, 0.5, L-0.5, L-0.5, 0.5],
            y=[fy-fw/2]*4 + [fy-fw/2]*4,
            z=[0, 0, 0, 0, fh, fh, fh, fh],
            i=[0, 0, 4, 4, 0, 0, 3, 3, 0, 0, 1, 1],
            j=[1, 2, 6, 7, 4, 5, 2, 6, 3, 7, 5, 6],
            k=[2, 3, 5, 6, 5, 1, 6, 7, 7, 4, 6, 2],
            color='#FF6D00', opacity=0.95,
            name='🍽️ معلف', showlegend=(fi == 0), hoverinfo='skip'))

    # المساقي — أزرق فاقع
    nd = min(dims["drinkers_count"], 6) or 2
    for i in range(nd):
        xc = 1.5 + (i + 0.5) * ((L - 3.0) / nd)
        yc = W/2 if dims.get("central_aisle", True) and W > 8 else W - 1.5
        fig.add_trace(go.Scatter3d(
            x=[xc], y=[yc], z=[0.55],
            mode='markers+text',
            marker=dict(size=16, color='#1976D2', symbol='diamond',
                        line=dict(color='#0D47A1', width=3)),
            text=['💧'], textposition='top center',
            textfont=dict(size=14),
            name='💧 مسقى' if i == 0 else None,
            showlegend=(i == 0),
            hovertext=f"<b>مسقى {i+1}</b>", hoverinfo='text'))

    # حيوانات
    for p in pens:
        n_to_show = min(p["actual"], 20)
        if n_to_show == 0: continue
        xs, ys = [], []
        for j in range(n_to_show):
            col = j % 5; row = j // 5
            n_cols = min(5, n_to_show)
            xj = p["x0"] + (col + 0.5) * (p["x1"] - p["x0"]) / n_cols
            yj = p["z0"] + (row + 0.5) * (p["z1"] - p["z0"]) / max(
                1, (n_to_show + 4) // 5)
            xs.append(xj); ys.append(yj)
        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=[0.15]*len(xs),
            mode='markers',
            marker=dict(size=4.5, color='#2E7D32',
                        line=dict(color='#1B5E20', width=1)),
            name='🐄 حيوانات', showlegend=(p["num"] == 1),
            hovertext=f"ساحة {p['num']}: {p['actual']} رأس",
            hoverinfo='text'))

    # فتحات التهوية — سماوي فاتح
    vent_h = H * dims["standard"]["vent_open_ratio"]
    vent_color = '#00BCD4'
    if vent_h > 0.1:
        n_front = 3
        for i in range(n_front):
            x0_v = (i + 0.3) * L / n_front
            x1_v = (i + 0.7) * L / n_front
            fig.add_trace(go.Mesh3d(
                x=[x0_v, x1_v, x1_v, x0_v], y=[W - 0.02]*4,
                z=[H*0.45, H*0.45, H*0.45 + vent_h, H*0.45 + vent_h],
                i=[0, 0], j=[1, 2], k=[2, 3],
                color=vent_color, opacity=0.9,
                name='💨 فتحة تهوية',
                showlegend=(i == 0),
                hovertext=f"<b>فتحة {i+1}</b>",
                hoverinfo='text'))
            fig.add_trace(go.Mesh3d(
                x=[x0_v, x1_v, x1_v, x0_v], y=[0.02]*4,
                z=[H*0.45, H*0.45, H*0.45 + vent_h, H*0.45 + vent_h],
                i=[0, 0], j=[1, 2], k=[2, 3],
                color=vent_color, opacity=0.9,
                showlegend=False, hoverinfo='skip'))

    # الممر المركزي
    if dims.get("central_aisle", True) and W > 8:
        fig.add_trace(go.Scatter3d(
            x=[margin, L - margin], y=[W/2, W/2],
            z=[0.03, 0.03], mode='lines',
            line=dict(color='#FFC107', width=8, dash='dash'),
            name='🚶 ممر مركزي', showlegend=True, hoverinfo='skip'))

    title = (f"🏗️ {dims['standard']['name_ar']} — "
             f"{n_pens} ساحة × ~{per_pen} رأس = {total}")
    max_dim = max(L, W, RH)
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#1B5E20'), x=0.5),
        scene=dict(
            xaxis=dict(title='الطول (م)', backgroundcolor='#F5F5F5'),
            yaxis=dict(title='العرض (م)', backgroundcolor='#F5F5F5'),
            zaxis=dict(title='الارتفاع (م)', backgroundcolor='#F5F5F5'),
            aspectmode='manual',
            aspectratio=dict(x=L/max_dim, y=W/max_dim,
                             z=max(RH/max_dim, 0.15)),
            camera=dict(eye=dict(x=1.7, y=-1.7, z=1.3),
                        up=dict(x=0, y=0, z=1)),
            dragmode='orbit'),
        height=720, margin=dict(l=0, r=0, t=70, b=0),
        paper_bgcolor='white',
        legend=dict(x=0.01, y=0.99,
                    bgcolor='rgba(255,255,255,0.95)',
                    bordercolor='#2E7D32', borderwidth=2,
                    font=dict(size=11, color='#1A1A1A')),
        showlegend=True)
    return fig


def render_barn_to_pdf_image(dims):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        std = dims["standard"]
        L = dims["length_m"]; W = dims["width_m"]
        H = dims["height_m"]; RH = dims["ridge_height_m"]
        fig = plt.figure(figsize=(11, 7.5))
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

        ax.set_xlim(0, L); ax.set_ylim(0, W); ax.set_zlim(0, RH + 0.5)
        ax.set_box_aspect((L, W, RH + 0.5))
        ax.set_title(f"{std['name_ar']} — {dims['count']} رأس",
                     fontsize=13, color='#1b5e20',
                     fontweight='bold', pad=15)
        ax.view_init(elev=22, azim=-55)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=140, bbox_inches='tight',
                    facecolor='white')
        plt.close(); buf.seek(0)
        return buf
    except Exception:
        return None


def create_barn_animation_gif(dims, frames=20, fps=8):
    if not MATPLOTLIB_AVAILABLE or not PIL_AVAILABLE: return None
    try:
        std = dims["standard"]
        L = dims["length_m"]; W = dims["width_m"]
        H = dims["height_m"]; RH = dims["ridge_height_m"]
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')

        def draw():
            ax.clear()
            floor = [[(0, 0, 0), (L, 0, 0), (L, W, 0), (0, W, 0)]]
            ax.add_collection3d(Poly3DCollection(
                floor, facecolors='#d7ccc8', edgecolors='#5d4037',
                alpha=0.75, linewidths=1.5))
            ax.set_xlim(0, L); ax.set_ylim(0, W); ax.set_zlim(0, RH + 0.5)
            ax.set_box_aspect((L, W, RH + 0.5))
            ax.set_title(f"{std['name_ar']} — {dims['count']}",
                         fontsize=12, color='#1b5e20', fontweight='bold')

        def animate(fn):
            draw()
            ax.view_init(elev=20, azim=(fn / frames) * 360)
            return fig,

        anim = animation.FuncAnimation(fig, animate, frames=frames,
                                        interval=1000 // fps, blit=False)
        tmp = tempfile.NamedTemporaryFile(suffix='.gif', delete=False)
        tmp_path = tmp.name; tmp.close()
        try:
            anim.save(tmp_path, writer='pillow', fps=fps, dpi=80)
            with open(tmp_path, 'rb') as f:
                data = f.read()
            os.unlink(tmp_path); plt.close(fig)
            return io.BytesIO(data)
        except Exception:
            try: os.unlink(tmp_path)
            except Exception: pass
            plt.close(fig)
            return None
    except Exception:
        return None


def generate_barn_pdf_report(dims):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
                            leftMargin=40, topMargin=115, bottomMargin=145)
    story = []

    def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
        return Paragraph(ar(text), ParagraphStyle(
            's', fontName=font_mgr.font_name, fontSize=size,
            alignment=align, textColor=HexColor(color),
            spaceAfter=6, leading=size * 1.6))

    std = dims["standard"]
    story.append(P("تقرير حظيرة", size=20, align=TA_CENTER,
                   color='#1b5e20'))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2.5,
                            color=HexColor('#d4af37')))
    story.append(Spacer(1, 12))

    info = [[ar("الحيوان"), ar(std["name_ar"])],
            [ar("العدد"), ar(str(dims["count"]))],
            [ar("المساحة"), ar(f"{dims['total_area_m2']} م²")],
            [ar("الأبعاد"),
             ar(f"{dims['length_m']}×{dims['width_m']}×"
                f"{dims['ridge_height_m']} م")]]
    t = Table(info, colWidths=[150, 340])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
        ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('PADDING', (0, 0), (-1, -1), 8)]))
    story.append(t)
    story.append(Spacer(1, 15))

    img = render_barn_to_pdf_image(dims)
    if img:
        try:
            story.append(RLImage(img, width=480, height=340))
        except Exception:
            pass

    doc.build(story, onFirstPage=pdf_gen._draw_page,
              onLaterPages=pdf_gen._draw_page)
    buffer.seek(0)
    return buffer.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# الجدوى
# ═══════════════════════════════════════════════════════════════════════════

TECHNICAL_FEASIBILITY_DATA = {
    "دواجن_لاحم": {"feed_per_day_g": 120, "water_per_day_ml": 220,
        "labor_per_1000": 0.3, "cycle_days": 42,
        "final_weight_kg": 2.3, "fcr": 1.65, "production_type": "meat"},
    "دواجن_بياض": {"feed_per_day_g": 110, "water_per_day_ml": 250,
        "labor_per_1000": 0.3, "eggs_per_year": 310,
        "egg_weight_g": 60, "production_type": "eggs"},
    "سمان": {"feed_per_day_g": 28, "water_per_day_ml": 55,
        "labor_per_1000": 0.5, "cycle_days": 42,
        "final_weight_kg": 0.25, "fcr": 2.5, "production_type": "meat"},
    "أغنام": {"feed_per_day_g": 1800, "water_per_day_ml": 6000,
        "labor_per_1000": 1.5, "milk_per_day_L": 1.5,
        "lactation_days": 200, "production_type": "mixed"},
    "ماعز": {"feed_per_day_g": 1500, "water_per_day_ml": 6000,
        "labor_per_1000": 1.5, "milk_per_day_L": 2.5,
        "lactation_days": 280, "production_type": "milk"},
    "أبقار": {"feed_per_day_g": 20000, "water_per_day_ml": 80000,
        "labor_per_1000": 5.0, "milk_per_day_L": 20,
        "lactation_days": 305, "production_type": "milk"},
    "إبل": {"feed_per_day_g": 8000, "water_per_day_ml": 50000,
        "labor_per_1000": 3.0, "milk_per_day_L": 5,
        "lactation_days": 300, "production_type": "milk"},
    "خيول": {"feed_per_day_g": 10000, "water_per_day_ml": 40000,
        "labor_per_1000": 4.0, "production_type": "service"},
    "أرانب": {"feed_per_day_g": 180, "water_per_day_ml": 350,
        "labor_per_1000": 1.0, "cycle_days": 70,
        "final_weight_kg": 2.5, "fcr": 3.5, "production_type": "meat"},
}


def calculate_technical_feasibility(key, count):
    std = BARN_DESIGN_STANDARDS.get(key)
    if not std: return None
    dims = calculate_barn_dimensions(key, count)
    if not dims: return None

    tech = TECHNICAL_FEASIBILITY_DATA.get(key, {})
    feed_day = tech.get("feed_per_day_g", 100) / 1000 * count
    water_day = tech.get("water_per_day_ml", 200) / 1000 * count
    workers = max(1, int(np.ceil(
        count * tech.get("labor_per_1000", 0.3) / 1000)))
    ptype = tech.get("production_type", "meat")
    production = {}

    if ptype == "eggs":
        eggs_year = count * tech.get("eggs_per_year", 300)
        production = {"unit": "بيضة/سنة", "annual": eggs_year,
                      "per_day": eggs_year / 365}
    elif ptype == "milk":
        m_day = count * tech.get("milk_per_day_L", 20)
        production = {"unit": "لتر/سنة",
                      "annual": m_day * tech.get("lactation_days", 305),
                      "per_day": m_day}
    elif ptype == "meat":
        cyc = tech.get("cycle_days", 42)
        cyc_y = 365 / cyc
        production = {"unit": "كجم/سنة",
                      "annual": count * tech.get("final_weight_kg", 2) * cyc_y,
                      "cycles_year": cyc_y}
    else:
        production = {"unit": "خدمات", "annual": 0}

    return {"barn_key": key, "std": std, "dims": dims, "count": count,
            "feed": {"per_head_day_kg": tech.get("feed_per_day_g", 100)/1000,
                     "total_day_kg": feed_day,
                     "total_year_ton": feed_day * 365 / 1000},
            "water": {"per_head_day_L": tech.get("water_per_day_ml", 200)/1000,
                      "total_day_L": water_day,
                      "total_year_m3": water_day * 365 / 1000},
            "labor": {"workers": workers,
                      "animals_per_worker": count // workers},
            "production": production}


def generate_feasibility_booklet(key, count, project_name="",
                                   requester_name=""):
    feas = calculate_technical_feasibility(key, count)
    if not feas: return None
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
                            leftMargin=40, topMargin=115, bottomMargin=145)
    story = []

    def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
        return Paragraph(ar(text), ParagraphStyle(
            's', fontName=font_mgr.font_name, fontSize=size,
            alignment=align, textColor=HexColor(color),
            spaceAfter=6, leading=size * 1.6))

    std = feas["std"]; dims = feas["dims"]
    story.append(Spacer(1, 30))
    story.append(P("كتيّب دراسة الجدوى", size=30, align=TA_CENTER,
                   color='#1b5e20'))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=3,
                            color=HexColor('#d4af37')))
    story.append(Spacer(1, 30))
    story.append(P(f"مشروع: {project_name or std['name_ar']}", size=18,
                   align=TA_CENTER, color='#c62828'))
    story.append(Spacer(1, 15))
    story.append(P(f"{count} رأس", size=14, align=TA_CENTER))
    story.append(PageBreak())

    story.append(P("🏗️ الحظيرة", size=18, align=TA_CENTER,
                   color='#1b5e20'))
    story.append(Spacer(1, 15))
    barn_data = [[ar("البيان"), ar("القيمة")],
                 [ar("المساحة"), ar(f"{dims['total_area_m2']} م²")],
                 [ar("الطول"), ar(f"{dims['length_m']} م")],
                 [ar("العرض"), ar(f"{dims['width_m']} م")],
                 [ar("الحجم"), ar(f"{dims['volume_m3']} م³")]]
    t = Table(barn_data, colWidths=[220, 230])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name)]))
    story.append(t)
    story.append(Spacer(1, 15))

    img = render_barn_to_pdf_image(dims)
    if img:
        try:
            story.append(RLImage(img, width=480, height=340))
        except Exception:
            pass
    story.append(PageBreak())

    story.append(P("🔧 الجدوى الفنية", size=18, align=TA_CENTER,
                   color='#1b5e20'))
    story.append(Spacer(1, 15))

    def mini(title, color, rows):
        story.append(P(title, size=13, color=color))
        story.append(Spacer(1, 5))
        data = [[ar("البند"), ar("القيمة")]] + [[ar(a), ar(b)]
                                                 for a, b in rows]
        tt = Table(data, colWidths=[220, 230])
        tt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.6, HexColor('#bdbdbd')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name)]))
        story.append(tt)
        story.append(Spacer(1, 12))

    mini("🍽️ العلف", '#e65100', [
        ("علف/يوم", f"{feas['feed']['total_day_kg']:.1f} كجم"),
        ("علف/سنة", f"{feas['feed']['total_year_ton']:.2f} طن")])
    mini("💧 الماء", '#1976d2', [
        ("ماء/يوم", f"{feas['water']['total_day_L']:.0f} لتر"),
        ("ماء/سنة", f"{feas['water']['total_year_m3']:.1f} م³")])
    mini("👷 العمالة", '#6d4c41', [
        ("عمال", str(feas['labor']['workers']))])

    doc.build(story, onFirstPage=pdf_gen._draw_page,
              onLaterPages=pdf_gen._draw_page)
    buffer.seek(0)
    return buffer.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# DEFAULTS + SharedStorage
# ═══════════════════════════════════════════════════════════════════════════

DEFAULTS = {
    "approved": False, "user_role": None, "active_formula": {},
    "computed_ton_cost": 280.0, "inventory": {},
    "shared_comments": f"• مرحباً في {APP_NAME}\n• {DUA_SHORT}\n",
    "broiler_farms": {}, "barn_video_gif": None,
    "last_formulation_result": None, "last_formulation_context": None,
    "last_ocr_result": None, "owner_attempts": 0,
    "owner_lock_until": 0.0, "invoices": [],
    "formulation_history": [], "comments_list": [],
    "est_weight": None, "daily_feed": None,
    "measurement_history": [], "validation_cache": None,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state["inventory"]:
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing in cat:
            st.session_state["inventory"][ing] = {
                "quantity": 25.0, "min_threshold": 5.0, "unit": "طن"}


class SharedStorage:
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
            return cls._load().get(key, default)


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
    background-size: cover; background-position: center;
    background-attachment: fixed;
}
.stApp { background: transparent; }
.main-box {
    background: rgba(255,255,255,0.92); padding: 32px;
    border-radius: 22px; box-shadow: 0 15px 45px rgba(0,0,0,0.15);
    margin-bottom: 70px; backdrop-filter: blur(12px);
    border: 1px solid rgba(212,175,55,0.2);
}
@keyframes gradientShift {
    0%,100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}
.dua-main-box {
    background: linear-gradient(135deg, #0d3011, #1b5e20, #2e7d32,
        #1b5e20, #0d3011);
    background-size: 200% 200%;
    animation: gradientShift 12s ease infinite;
    padding: 34px 28px; border-radius: 22px;
    border: 4px solid #d4af37; direction: rtl;
    text-align: center; margin: 25px 0;
}
.dua-main-box * { color: white !important; }
.dua-main-box h3 {
    color: #d4af37 !important; font-size: 1.9rem;
    margin-bottom: 18px; font-weight: 900;
}
.dua-main-box .names {
    display: inline-block;
    background: linear-gradient(90deg,
        rgba(212,175,55,0.15), rgba(212,175,55,0.35),
        rgba(212,175,55,0.15));
    font-size: 1.65rem; font-weight: 900;
    color: #ffeb3b !important; margin: 20px 0;
    padding: 16px 30px; border: 2px solid #d4af37;
    border-radius: 16px; font-family: 'Amiri', serif !important;
}
.dua-main-box p.quran {
    font-family: 'Amiri', serif !important;
    font-size: 1.2rem; color: #d4af37 !important;
    margin-top: 22px; padding: 18px 25px;
    background: rgba(0,0,0,0.25); border-radius: 12px;
    border-right: 5px solid #d4af37; border-left: 5px solid #d4af37;
}
.visitor-dua-banner {
    background: linear-gradient(135deg, #fff8e1, #ffecb3, #ffe082);
    padding: 20px 28px; border-radius: 16px;
    border: 3px solid #d4af37; margin: 22px 0;
    direction: rtl; text-align: center;
    box-shadow: 0 6px 24px rgba(0,0,0,0.1);
}
.visitor-dua-banner * { color: #4e342e !important; }
.visitor-dua-banner b { color: #c62828 !important;
                         font-family: 'Amiri' !important; }
.dua-fixed-banner {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32,
        #1b5e20, #0d3011);
    background-size: 200% 100%;
    animation: gradientShift 8s linear infinite;
    color: white !important; padding: 12px 20px;
    z-index: 9998; text-align: center;
    border-top: 3px solid #d4af37;
    font-family: 'Amiri', serif !important;
    font-size: 1.05rem; font-weight: bold;
}
.dua-fixed-banner * { color: #ffeb3b !important;
                       font-family: 'Amiri' !important; }
.section-title {
    color: #1b5e20 !important;
    border-right: 6px solid #2e7d32; padding: 12px 18px;
    text-align: right; font-size: 1.5rem; font-weight: 900;
    margin-top: 30px; margin-bottom: 20px;
    background: linear-gradient(to left,
        rgba(46,125,50,0.15), transparent);
    border-radius: 10px;
}
.formula-item {
    background: linear-gradient(135deg, #ffffff, #e8f5e9);
    padding: 15px 20px; border-radius: 10px;
    margin-bottom: 10px; font-weight: 700;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32; text-align: right;
}
.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px; border-radius: 16px;
    border-right: 5px solid #2e7d32; margin-bottom: 20px;
    direction: rtl; text-align: right;
}
.oil-info-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 18px; border-radius: 16px;
    border-right: 5px solid #e65100; margin-bottom: 18px;
    direction: rtl; text-align: right;
}
.physio-card {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 18px 24px; border-radius: 14px;
    border-right: 6px solid #1565c0; margin-bottom: 20px;
    direction: rtl; text-align: right;
}
.physio-card h4 { color: #0d47a1 !important; margin: 0 0 8px 0; }
.quality-good-v113 {
    background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
    padding: 24px; border-radius: 22px;
    border-right: 8px solid #1b5e20; margin: 18px 0;
    direction: rtl; text-align: right;
}
.quality-bad-v113 {
    background: linear-gradient(135deg, #ffcdd2, #ef9a9a);
    padding: 24px; border-radius: 22px;
    border-right: 8px solid #c62828; margin: 18px 0;
    direction: rtl; text-align: right;
}
.measure-result {
    background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
    padding: 24px; border-radius: 20px;
    border: 3px solid #1b5e20; margin: 18px 0;
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
[data-testid="stMetricValue"] {
    color: #1b5e20 !important; font-weight: 900 !important;
}
@media (max-width: 768px) {
    .main-box { padding: 18px; margin-bottom: 80px; }
    .dua-main-box h3 { font-size: 1.4rem; }
    .dua-main-box .names { font-size: 1.2rem; padding: 12px 18px; }
    .dua-fixed-banner { font-size: 0.85rem; padding: 10px 14px; }
}
</style>
""", unsafe_allow_html=True)


print(f"[Tawor v{APP_VERSION}] الجزء 2/3 — بدائل الحليب + الرسوم + الحظائر + CSS ✅")
print(f"  ✅ MILK_REPLACER: {len(MILK_REPLACER_STANDARDS)} حيوان × {len(MILK_REPLACER_INGREDIENTS)} مكون")
print(f"  ✅ BARN_DESIGN: {len(BARN_DESIGN_STANDARDS)} نوع")
print(f"  ✅ create_barn_with_pens_3d (بألوان + تهوية)")
print(f"  ✅ TECHNICAL_FEASIBILITY: {len(TECHNICAL_FEASIBILITY_DATA)} قطاع")
print(f"  ✅ PDFs + GIF + CSS")
# ═══════════════════════════════════════════════════════════════════════════
# 🚪 بوابة الدخول
# ═══════════════════════════════════════════════════════════════════════════

if st.session_state.get("approved", False) and not _session_valid():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.error("⚠️ جلسة غير صالحة — أعد الدخول")
    st.stop()

if not st.session_state.get("approved", False):
    st.markdown('<div class="main-box" style="max-width: 780px; '
                'margin: 30px auto; direction: rtl;">',
                unsafe_allow_html=True)

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

    st.markdown("<hr style='border-top: 2px solid #d4af37; "
                "margin: 25px 0;'>", unsafe_allow_html=True)

    # محاولة قراءة صورة شخصية
    @st.cache_data(ttl=3600)
    def _get_img_b64(paths):
        for p in paths:
            if os.path.exists(p):
                try:
                    with open(p, "rb") as f:
                        return base64.b64encode(f.read()).decode()
                except Exception:
                    pass
        return None

    img_base64 = _get_img_b64(tuple(PHOTO_OPTIONS))

    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        if img_base64:
            st.markdown(
                f'<img src="data:image/jpeg;base64,{img_base64}" '
                f'class="profile-img-style">', unsafe_allow_html=True)
        else:
            st.markdown(
                '<img src="https://images.unsplash.com/photo-1500382017468-'
                '9049fed747ef?q=80&w=1600" class="profile-img-style">',
                unsafe_allow_html=True)
    with col_title:
        st.markdown(
            f"<h2 style='color:#2E7D32; text-align:right;'>"
            f"🌾 {APP_NAME}</h2>", unsafe_allow_html=True)
        st.markdown(
            f"<p style='color:#1565C0; text-align:right; "
            f"font-size:1.1rem;'>{APP_TAGLINE}</p>",
            unsafe_allow_html=True)
        st.markdown(
            f"<h4 style='color:#c62828; text-align:right;'>"
            f"{SUPERVISOR} — {SUPERVISOR_TITLE}</h4>",
            unsafe_allow_html=True)

    st.markdown(
        "<h3 style='text-align:center; color:#1b5e20; margin-top:20px;'>"
        "🔐 بوابة الدخول</h3>", unsafe_allow_html=True)

    if not _get_owner_code_hash():
        st.warning(
            "⚠️ كود المالك غير مُهيّأ — يجب ضبط `OWNER_CODE` في "
            "`.streamlit/secrets.toml` أو `TAWOR_OWNER_CODE` في البيئة. "
            "الزوار يمكنهم الدخول.")

    col_owner, col_guest = st.columns(2)

    with col_owner:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        padding: 20px; border-radius: 12px; border: 2px solid #2e7d32;
        text-align: center; margin-bottom: 10px;">
        <h4 style="color: #1b5e20;">👑 المالك</h4>
        <p style="font-size: 0.9rem; color: #555;">
        دخول آمن (fail-closed)</p>
        </div>
        """, unsafe_allow_html=True)

        oc = st.text_input("🔑 كود المالك:", type="password",
                            key="owner_code_v18")

        if st.button("👑 دخول المالك", type="primary",
                       use_container_width=True):
            ok, msg = _owner_login_attempt(oc)
            if ok:
                st.rerun()
            else:
                st.error(msg)

    with col_guest:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fff8e1, #ffecb3);
        padding: 20px; border-radius: 12px; border: 2px solid #d4af37;
        text-align: center; margin-bottom: 10px;">
        <h4 style="color: #e65100;">👥 زائر</h4>
        <p style="font-size: 0.9rem; color: #555;">دخول مجاني<br>
        <small style="color: #999;">(كل الميزات ما عدا المستودعات
        والفواتير والتعليقات)</small></p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True):
            st.session_state.update({"approved": True,
                                       "user_role": "guest"})
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════
# 🏠 الواجهة الرئيسية
# ═══════════════════════════════════════════════════════════════════════════

st.markdown('<div class="main-box">', unsafe_allow_html=True)

c1, c2 = st.columns([0.7, 0.3])
with c2:
    role_label = "المالك 👑" if is_owner() else "زائر 👥"
    st.markdown(
        f"<div style='text-align:left; padding:10px; background:#f5f5f5;"
        f"border-radius:10px;'>الحساب: <b>{role_label}</b></div>",
        unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.cache_data.clear()
        st.rerun()

c3, c4 = st.columns([0.3, 0.7])
with c3:
    if img_base64:
        st.markdown(
            f'<img src="data:image/jpeg;base64,{img_base64}" '
            f'class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown(
            '<img src="https://images.unsplash.com/photo-1500382017468-'
            '9049fed747ef?q=80&w=1600" class="profile-img-style">',
            unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <h1 style='color: #0d3011; text-align:right; margin-bottom:0;
               font-weight: 900; font-size: 2.3rem;'>
    🌾 {APP_NAME}
    </h1>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <p style='color: #1565C0; text-align:right; font-size: 1.25rem;
              font-weight: 600; margin-top: 8px;'>
    {APP_TAGLINE}
    </p>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #fff8e1, #ffe082);
                padding: 12px 20px; border-radius: 12px;
                border-right: 6px solid #c62828;
                border-left: 6px solid #c62828;
                margin-top: 10px;'>
        <h3 style='color: #b71c1c; text-align:right; margin: 0;
                   font-weight: 900; font-size: 1.55rem;'>
        👨‍🔬 {SUPERVISOR}
        </h3>
        <p style='color: #0d47a1; text-align:right; margin: 5px 0 0 0;
                  font-weight: 700; font-size: 1.15rem;'>
        ✨ {SUPERVISOR_TITLE}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="visitor-dua-banner">{DUA_VISITOR}</div>',
            unsafe_allow_html=True)
st.markdown("<hr style='border-top: 3px solid #2e7d32;'>",
            unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# التبويبات
# ═══════════════════════════════════════════════════════════════════════════

if is_owner():
    tabs_titles = [
        "🔬 النمذجة", "🌰 الزيوت", "🍼 بدائل الحليب", "📷 OCR",
        "📏 القياسات", "🏗️ الحظائر 3D", "📊 الجدوى", "🐔 المزارع",
        "🏭 المستودعات", "🧾 الفواتير", "🖨️ الديباجة", "📈 التحليلات",
        "💬 التعليقات", "📚 المراجع", "💡 المساعدة", "📖 الدليل",
    ]
else:
    tabs_titles = [
        "🔬 النمذجة", "🌰 الزيوت", "🍼 بدائل الحليب", "📷 OCR",
        "📏 القياسات", "🏗️ الحظائر 3D", "📊 الجدوى", "🐔 المزارع",
        "📚 المراجع", "💡 المساعدة", "📖 الدليل",
    ]

tabs = st.tabs(tabs_titles)
tab_map = {t: tab for t, tab in zip(tabs_titles, tabs)}


# ═══════════════════════════════════════════════════════════════════════════
# 🔬 تبويب النمذجة
# ═══════════════════════════════════════════════════════════════════════════

def get_standard_by_key(key):
    """يرجع قاموس المعيار حسب المفتاح."""
    if not key or key.startswith("—"):
        return None
    try:
        if key.startswith("دواجن_"):
            if "بادي" in key:
                return requirement_to_standard(
                    get_poultry_requirements("لاحم", 1))
            if "نامي" in key:
                return requirement_to_standard(
                    get_poultry_requirements("لاحم", 3))
            if "بياض" in key:
                return requirement_to_standard(
                    get_poultry_requirements("بياض", 20))
            return requirement_to_standard(
                get_poultry_requirements("لاحم", 5))
        if key.startswith("أبقار_"):
            return requirement_to_standard(
                get_cattle_requirements(key.replace("أبقار_", "")))
        if key.startswith("أغنام_"):
            return requirement_to_standard(
                get_sheep_requirements(key.replace("أغنام_", ""),
                                        is_male=True))
        if key.startswith("ماعز_"):
            return requirement_to_standard(
                get_goat_requirements(key.replace("ماعز_", ""),
                                       is_male=True))
        if key.startswith("إبل_"):
            return requirement_to_standard(
                get_camel_requirements(key.replace("إبل_", "")))
        if key.startswith("خيول_"):
            return requirement_to_standard(
                get_horse_requirements(key.replace("خيول_", "")))
        if key.startswith("سمان_"):
            return requirement_to_standard(
                get_quail_requirements(
                    "بياض" if "بياض" in key else "تسمين", 1))
    except Exception:
        return None
    return None


def render_complete_formula_lab():
    """🧪 مختبر التركيبة الكاملة."""
    st.markdown("### 🧪 مختبر التركيبة الكاملة")
    st.caption("أدخل تركيبة كاملة (عدة مكونات + نسبها) "
               "— تحليل + تحقق + مقارنة + تصدير")

    all_ings = list(_get_ingredient_lookup().keys())

    if "lab_full_df" not in st.session_state:
        st.session_state["lab_full_df"] = pd.DataFrame([
            {"المادة": "ذرة صفراء", "النسبة %": 58.0},
            {"المادة": "كسب فول صويا 44%", "النسبة %": 28.0},
            {"المادة": "نخالة قمح (ردة)", "النسبة %": 8.0},
            {"المادة": "الحجر الجيري", "النسبة %": 1.4},
            {"المادة": "فوسفات ثنائي الكالسيوم", "النسبة %": 1.8},
            {"المادة": "ملح الطعام", "النسبة %": 0.4},
            {"المادة": "بريمكس تسمين دواجن", "النسبة %": 0.3},
            {"المادة": "ليسين نقي", "النسبة %": 0.1},
        ])

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        lab_animal_key = st.selectbox(
            "🐾 للمقارنة مع معيار:",
            ["— بدون معيار —",
             "دواجن_بادي", "دواجن_نامي", "دواجن_ناهي", "دواجن_بياض",
             "أبقار_حليب_عالي", "أبقار_حليب_متوسط", "أبقار_تسمين_مكثف",
             "أغنام_تسمين_مكثف", "أغنام_مرضعات",
             "ماعز_تسمين_جديان", "إبل_نمو", "إبل_حليب",
             "خيول_رياضة_عادي", "سمان_بادي"],
            key="lab_full_animal_v2")
    with col_b:
        use_lib_prices = st.checkbox("💵 أسعار المكتبة", value=True,
                                       key="lab_full_prices_v2")
    with col_c:
        do_validate = st.checkbox("🔒 فحص الحدود العالمية", value=True,
                                    key="lab_full_valid_v2")

    st.markdown("#### 📋 التركيبة (المجموع = 100%)")
    edited = st.data_editor(
        st.session_state["lab_full_df"],
        num_rows="dynamic", use_container_width=True,
        column_config={
            "المادة": st.column_config.SelectboxColumn(
                options=all_ings, required=True, width="large"),
            "النسبة %": st.column_config.NumberColumn(
                min_value=0.0, max_value=100.0, step=0.1,
                format="%.2f"),
        }, key="lab_full_editor_v2")
    st.session_state["lab_full_df"] = edited

    formula = {}
    for _, r in edited.iterrows():
        ing = r["المادة"]
        pct = float(r["النسبة %"])
        if ing and pct > 0:
            formula[ing] = formula.get(ing, 0.0) + pct

    total = sum(formula.values())

    if abs(total - 100) < 0.05:
        st.success(f"✅ المجموع: {total:.2f}% — مطابق")
    elif total > 100:
        st.error(f"❌ المجموع: {total:.2f}% — زائد {total-100:.2f}%")
    else:
        st.warning(f"⚠️ المجموع: {total:.2f}% — ناقص {100-total:.2f}%")

    if not formula or abs(total - 100) > 0.5:
        st.info("💡 عدّل النسب حتى 100% — التحليل يظهر تلقائياً")
        return

    nut = compute_formula_nutrients(formula)

    st.markdown("### 📊 المؤشرات الغذائية")
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("🧬 CP", f"{nut['CP']:.2f}%")
    k2.metric("🧬 DP", f"{nut['DP']:.2f}%")
    k3.metric("⚡ SE", f"{nut['SE']:.1f}")
    k4.metric("🌾 NDF", f"{nut['NDF']:.2f}%")
    k5.metric("🌰 دهن", f"{nut['EE']:.2f}%")
    ca_p = nut['Ca'] / nut['P'] if nut['P'] > 0 else 0
    k6.metric("⚖️ Ca:P", f"{ca_p:.2f}")

    lookup = _get_ingredient_lookup()
    if use_lib_prices:
        prices = {ing: float(lookup.get(ing, {}).get("price", 300.0))
                  for ing in formula}
    else:
        st.markdown("#### 💵 أسعار المواد ($/طن)")
        prices = {}
        pc = st.columns(min(4, len(formula)))
        for i, ing in enumerate(formula.keys()):
            with pc[i % 4]:
                prices[ing] = st.number_input(
                    ing[:25], min_value=1.0,
                    value=float(lookup.get(ing, {}).get("price", 300.0)),
                    step=10.0, key=f"lab_p_v2_{ing}")

    cost = sum(formula[ing] * prices.get(ing, 300.0)
               for ing in formula) / 100
    st.metric("💰 التكلفة ($/طن)", f"${cost:.2f}")

    if do_validate:
        st.markdown("### 🔒 فحص الحدود العالمية")
        validation = validate_feed_inputs(formula)
        if validation["ok"] and not validation["warnings"]:
            st.success("✅ جميع المكونات داخل الحدود القياسية")
        else:
            for err in validation["errors"]:
                st.error(err)
            for w in validation["warnings"]:
                st.warning(w)
            if validation["corrections"]:
                with st.expander("🔧 التصحيحات المقترحة",
                                  expanded=True):
                    corr_df = pd.DataFrame([{
                        "المكون": c["ingredient"],
                        "قبل": f"{c['from']:.2f}%",
                        "بعد": f"{c['to']:.2f}%",
                        "السبب": c["reason"]}
                        for c in validation["corrections"]])
                    st.dataframe(corr_df, use_container_width=True,
                                  hide_index=True)
                    c_a, c_b = st.columns(2)
                    with c_a:
                        if st.button("✅ تطبيق التصحيح",
                                      type="primary",
                                      use_container_width=True):
                            new_df = pd.DataFrame([
                                {"المادة": k, "النسبة %": v}
                                for k, v in
                                validation["corrected"].items()])
                            st.session_state["lab_full_df"] = new_df
                            st.rerun()
                    with c_b:
                        if st.button("📄 تقرير التحقق PDF",
                                      use_container_width=True):
                            pdf_v = generate_validation_pdf_report(
                                validation, formula)
                            if pdf_v:
                                st.download_button(
                                    "⬇️ تحميل", pdf_v,
                                    file_name=(f"Validation_"
                                               f"{datetime.now():%Y%m%d}.pdf"),
                                    mime="application/pdf")

    if lab_animal_key != "— بدون معيار —":
        target = get_standard_by_key(lab_animal_key)
        if target:
            st.markdown(f"### 📐 المقارنة مع `{lab_animal_key}`")
            labels = {"CP": "بروتين CP", "DP": "مهضوم DP",
                      "SE": "طاقة SE", "NDF": "NDF", "ADF": "ADF",
                      "EE": "دهن EE", "ASH": "رماد", "Ca": "Ca",
                      "P": "P"}
            comp_rows = []
            for k, sv in target.items():
                if k not in labels or sv == 0: continue
                cv = nut.get(k, 0.0)
                diff = cv - sv
                pct = (diff / sv * 100) if sv else 0
                ev = evaluate_difference(pct, standard_value=sv)
                comp_rows.append({
                    "العنصر": labels.get(k, k),
                    "المعيار": f"{sv:.2f}",
                    "المحسوب": f"{cv:.2f}",
                    "الفرق": f"{diff:+.3f}",
                    "الفرق %": f"{pct:+.2f}%",
                    "التقييم": ev["label"]})
            st.dataframe(pd.DataFrame(comp_rows),
                          use_container_width=True, hide_index=True)

            animal_short = lab_animal_key.split("_")[0]
            quality, _ = evaluate_quality_weighted(
                formula, target, animal_type=animal_short, basis="DP")

            if quality >= 85:
                st.markdown(f"""
                <div class="quality-good-v113">
                <h3 style="margin:0;">🏆 الجودة: {quality:.1f}%</h3>
                <p style="margin:6px 0 0 0;">ممتازة</p>
                </div>
                """, unsafe_allow_html=True)
            elif quality >= 70:
                st.markdown(f"""
                <div class="quality-good-v113">
                <h3 style="margin:0;">✅ الجودة: {quality:.1f}%</h3>
                <p style="margin:6px 0 0 0;">مقبولة</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="quality-bad-v113">
                <h3 style="margin:0;">⚠️ الجودة: {quality:.1f}%</h3>
                <p style="margin:6px 0 0 0;">تحتاج تحسين</p>
                </div>
                """, unsafe_allow_html=True)

            ch1, ch2 = st.columns(2)
            with ch1:
                bf = create_colorful_bar_chart(target, nut)
                if bf:
                    st.image(bf.getvalue(),
                              caption="📊 مقارنة",
                              use_container_width=True)
            with ch2:
                pf = create_colorful_pie_chart(formula)
                if pf:
                    st.image(pf.getvalue(),
                              caption="🥧 توزيع",
                              use_container_width=True)
            ch3, ch4 = st.columns(2)
            with ch3:
                rf = create_radar_chart(target, nut)
                if rf:
                    st.image(rf.getvalue(),
                              caption="🎯 رادار",
                              use_container_width=True)
            with ch4:
                gf = create_gauge_chart(quality)
                if gf:
                    st.image(gf.getvalue(),
                              caption="🏆 الجودة",
                              use_container_width=True)
            if nut['P'] > 0:
                cf = create_ca_p_ratio_chart(nut['Ca'], nut['P'])
                if cf:
                    st.image(cf.getvalue(), caption="⚖️ Ca:P",
                              use_container_width=True)

    hb = create_horizontal_bar_chart(formula)
    if hb:
        st.image(hb.getvalue(), caption="🌾 المكونات",
                  use_container_width=True)

    st.markdown("### 📥 التصدير")
    e1, e2 = st.columns(2)
    with e1:
        if lab_animal_key != "— بدون معيار —":
            target = get_standard_by_key(lab_animal_key)
            if target:
                try:
                    animal_short = lab_animal_key.split("_")[0]
                    quality_val, _ = evaluate_quality_weighted(
                        formula, target, animal_type=animal_short,
                        basis="DP")
                    req = AnimalRequirement(
                        DP=target.get("DP", 0), CP=target.get("CP", 0),
                        SE=target.get("SE", 0), NDF=target.get("NDF", 0),
                        ADF=target.get("ADF", 0), EE=target.get("EE", 0),
                        ASH=target.get("ASH", 0), Ca=target.get("Ca", 0),
                        P=target.get("P", 0),
                        name_ar=lab_animal_key, note="مختبر كامل")
                    pdf_bytes = pdf_gen.generate_report(
                        formula=formula, requirement=req,
                        animal_type=animal_short, breed=lab_animal_key,
                        cost=cost, city="—", local_cost=cost,
                        local_sym="USD",
                        requester_name="مختبر التركيبة الكاملة",
                        protein_basis="DP", standard_key=lab_animal_key,
                        include_charts=True, quality_score=quality_val)
                    st.download_button(
                        "📄 تحميل PDF", pdf_bytes,
                        file_name=(f"Lab_"
                                   f"{datetime.now():%Y%m%d}.pdf"),
                        mime="application/pdf",
                        use_container_width=True, type="primary")
                except Exception as e:
                    st.error(f"⚠️ {e}")
    with e2:
        st.download_button(
            "💾 حفظ التركيبة (JSON)",
            json.dumps(formula, ensure_ascii=False, indent=2),
            file_name=f"formula_{datetime.now():%Y%m%d}.json",
            mime="application/json", use_container_width=True)


with tab_map["🔬 النمذجة"]:
    try:
        sub_f, sub_a = st.tabs(["🎯 تركيب علفة (≥70%)",
                                 "🧪 مختبر التركيبة الكاملة"])

        with sub_f:
            local_rate, local_sym, city = 1.0, "USD", "—"
            live_prices = {ing: d.get("price", 280.0)
                            for cat in BIG_FEEDS_LIBRARY.values()
                            for ing, d in cat.items()}

            st.markdown(
                '<div class="section-title">🧬 أساس البروتين</div>',
                unsafe_allow_html=True)
            pb = st.radio("الأساس:",
                ["البروتين المهضوم (DP) — الأدق",
                 "البروتين الخام (CP) — الأسهل"],
                horizontal=True, key="protein_basis_v18")
            basis_code = "DP" if "DP" in pb else "CP"

            st.markdown(
                '<div class="section-title">🐾 اختر الحيوان</div>',
                unsafe_allow_html=True)
            a_tabs = st.tabs([
                "🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐪 إبل",
                "🐎 خيول", "🐔 دواجن", "🦆 سمان", "🐟 أسماك",
                "🐇 أرانب"])

            animal_choice = None
            production_type = None
            requirement = None
            std_key_global = ""

            with a_tabs[0]:
                st.markdown("### 🐄 الأبقار — NRC 2001")
                ct = st.selectbox("الحالة:",
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
                    key="cattle_t_v18")
                c1_, c2_ = st.columns(2)
                cp_ = {}
                with c1_:
                    if "حليب" in ct:
                        cp_["milk_yield"] = st.number_input(
                            "🥛 الحليب (كجم):", 5.0, 60.0, 20.0, 1.0,
                            key="cattle_m_v18")
                    cp_["weight_kg"] = st.number_input(
                        "⚖️ الوزن:", 200.0, 900.0, 500.0, 25.0,
                        key="cattle_w_v18")
                with c2_:
                    rp = get_cattle_requirements(ct, **cp_)
                    st.metric("DP", f"{rp.DP}%")
                    st.metric("CP", f"{rp.CP}%")
                    st.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_cattle_v18"):
                    animal_choice = "أبقار"
                    production_type = ct
                    requirement = rp
                    std_key_global = f"أبقار_{ct}"

            with a_tabs[1]:
                st.markdown("### 🐏 الأغنام — NRC 2007")
                sg = st.radio("الجنس:", ["ذكر", "أنثى"],
                                horizontal=True, key="sheep_g_v18")
                is_m = "ذكر" in sg
                lit = 1
                if is_m:
                    stype = st.selectbox("الحالة:",
                        ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد"],
                        key="sheep_tm_v18")
                else:
                    stype = st.selectbox("الحالة:",
                        ["مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
                        key="sheep_tf_v18")
                    if stype == "مرضعات":
                        lit = st.number_input("المواليد:", 1, 3, 1, 1,
                                                key="sheep_l_v18")
                ws = st.number_input("⚖️ الوزن:", 15.0, 120.0, 50.0, 5.0,
                                      key="sheep_w_v18")
                rp = get_sheep_requirements(stype, is_male=is_m,
                                              weight_kg=ws, litter_size=lit)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_sheep_v18"):
                    animal_choice = "أغنام"
                    production_type = stype
                    requirement = rp
                    std_key_global = f"أغنام_{stype}"

            with a_tabs[2]:
                st.markdown("### 🐐 الماعز — NRC 2007")
                gg = st.radio("الجنس:", ["ذكر", "أنثى"],
                                horizontal=True, key="goat_g_v18")
                is_m = "ذكر" in gg
                mg = 0
                if is_m:
                    gtype = st.selectbox("الحالة:",
                        ["تسمين_جديان", "تيوس"], key="goat_tm_v18")
                else:
                    gtype = st.selectbox("الحالة:",
                        ["حلابة_عالي", "حلابة_متوسط",
                         "حامل_أخير", "صيانة"], key="goat_tf_v18")
                    if "حلابة" in gtype:
                        mg = st.number_input("🥛 الحليب:", 0.5, 8.0,
                                               2.0, 0.25,
                                               key="goat_m_v18")
                rp = get_goat_requirements(gtype, is_male=is_m,
                                             milk_yield=mg)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_goat_v18"):
                    animal_choice = "ماعز"
                    production_type = gtype
                    requirement = rp
                    std_key_global = f"ماعز_{gtype}"

            with a_tabs[3]:
                st.markdown("### 🐪 الإبل — FAO 2010")
                cmt = st.selectbox("الحالة:",
                    ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
                    key="camel_t_v18")
                cwt = st.number_input("⚖️ الوزن:", 100.0, 800.0, 400.0,
                                        25.0, key="camel_w_v18")
                cm = 5.0
                if cmt == "حليب":
                    cm = st.number_input("🥛 الحليب:", 2.0, 20.0, 5.0,
                                           0.5, key="camel_m_v18")
                rp = get_camel_requirements(cmt, weight_kg=cwt,
                                              milk_yield=cm)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_camel_v18"):
                    animal_choice = "إبل"
                    production_type = cmt
                    requirement = rp
                    std_key_global = f"إبل_{cmt}"

            with a_tabs[4]:
                st.markdown("### 🐎 الخيول — NRC 2007")
                ht = st.selectbox("الحالة:",
                    ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار",
                     "مرضعات", "صيانة"], key="horse_t_v18")
                est = st.radio("طريقة الوزن:",
                    ["📏 قياسات", "🎚️ شريط"],
                    horizontal=True, key="horse_est_v18")
                if "قياسات" in est:
                    hc1, hc2 = st.columns(2)
                    with hc1:
                        girth = st.slider("محيط الصدر (سم):",
                                            120, 230, 175, 1,
                                            key="horse_girth_v18")
                    with hc2:
                        length = st.slider("طول الجسم (سم):",
                                             100, 210, 155, 1,
                                             key="horse_length_v18")
                    hwt = (girth ** 2 * length) / 11877.0
                    st.info(f"📐 الوزن: **{hwt:.1f} كجم**")
                else:
                    hwt = st.slider("⚖️ الوزن (كجم):",
                                      150, 800, 450, 10,
                                      key="horse_wt_v18")
                rp = get_horse_requirements(ht, weight_kg=hwt)
                p1, p2, p3, p4 = st.columns(4)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                p4.metric("⚖️ الوزن", f"{hwt:.0f} كجم")
                if st.checkbox("✅ اعتماد", key="u_horse_v18"):
                    animal_choice = "خيول"
                    production_type = ht
                    requirement = rp
                    std_key_global = f"خيول_{ht}"

            with a_tabs[5]:
                st.markdown("### 🐔 الدواجن")
                ps = st.radio("السلالة:", ["لاحم", "بياض"],
                                horizontal=True, key="poultry_s_v18")
                pa = st.number_input("العمر (أسبوع):", 1, 20, 1, 1,
                                       key="poultry_a_v18")
                rp = get_poultry_requirements(ps, pa)
                p1, p2, p3, p4 = st.columns(4)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                p4.metric("Ca", f"{rp.Ca}%")
                if st.checkbox("✅ اعتماد", key="u_poultry_v18"):
                    animal_choice = "دواجن"
                    production_type = ps
                    requirement = rp
                    if "بادي" in rp.name_ar:
                        std_key_global = "دواجن_بادي"
                    elif "نامي" in rp.name_ar:
                        std_key_global = "دواجن_نامي"
                    elif "بياض" in rp.name_ar:
                        std_key_global = "دواجن_بياض"
                    else:
                        std_key_global = "دواجن_ناهي"

            with a_tabs[6]:
                st.markdown("### 🦆 السمان")
                qs = st.radio("النوع:", ["تسمين", "بياض"],
                                horizontal=True, key="quail_s_v18")
                qa = st.number_input("العمر (أسبوع):", 1, 8, 1, 1,
                                       key="quail_a_v18")
                rp = get_quail_requirements(qs, qa)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_quail_v18"):
                    animal_choice = "سمان"
                    production_type = qs
                    requirement = rp
                    std_key_global = ("سمان_بياض" if qs == "بياض"
                                       else "سمان_بادي")

            with a_tabs[7]:
                st.markdown("### 🐟 الأسماك")
                fs = st.selectbox("النوع:",
                    ["البلطي النيلي", "القرموط الأفريقي", "الكارب"],
                    key="fish_sp_v18")
                fst = st.selectbox("المرحلة:",
                    ["بادئ زريعة", "نمو", "تسمين"], key="fish_stage_v18")
                rp = get_fish_requirements(fs, fst)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_fish_v18"):
                    animal_choice = "أسماك"
                    production_type = fst
                    requirement = rp
                    if "بادئ" in fst or "زريعة" in fst:
                        std_key_global = "أسماك_بادئ"
                    elif "نمو" in fst:
                        std_key_global = "أسماك_نمو"
                    else:
                        std_key_global = "أسماك_تسمين"

            with a_tabs[8]:
                st.markdown("### 🐇 الأرانب")
                rt = st.selectbox("الحالة:",
                    ["تسمين", "حليب", "صيانة"], key="rabbit_t_v18")
                rwt = st.number_input("⚖️ الوزن:", 1.0, 8.0, 4.0, 0.5,
                                        key="rabbit_w_v18")
                rp = get_rabbit_requirements(rt, rwt)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_rabbit_v18"):
                    animal_choice = "أرانب"
                    production_type = rt
                    requirement = rp
                    std_key_global = f"أرانب_{rt}"

            ready = bool(animal_choice and requirement)

            if ready:
                st.markdown(f"""
                <div class="physio-card">
                    <h4>🧬 الحالة المعتمدة</h4>
                    <p style="color: #1a237e; font-size: 1.15rem;
                              font-weight: 700; margin: 0;">
                        {animal_choice} — <span style="color: #c62828;">
                        {requirement.name_ar}</span>
                    </p>
                    <p style="color: #555; margin: 6px 0 0 0;
                              font-size: 0.92rem;">
                        📌 {requirement.note or "NRC/INRA/FAO"}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                oil_std_info = get_oil_standard(std_key_global)
                st.markdown(f"""
                <div class="oil-info-card">
                <b>🌰 الزيوت:</b> أقصى {oil_std_info['max']}% |
                مثالي {oil_std_info['optimal']}% |
                {oil_std_info['source']}
                </div>
                """, unsafe_allow_html=True)

                requester_name = st.text_input(
                    "👤 اسم الطالب:", placeholder="مزرعة الأمل",
                    key="req_name_v18")

                st.markdown(
                    '<div class="section-title">🌾 المكونات</div>',
                    unsafe_allow_html=True)
                sq = st.text_input("🔍 بحث:", key="ing_search_v18")

                selected = []
                default_set = get_default_selections(
                    animal_choice, production_type, requirement)

                for cat_name, items in BIG_FEEDS_LIBRARY.items():
                    filt = ({k: v for k, v in items.items()
                             if sq.lower() in k.lower()}
                            if sq else items)
                    if not filt: continue
                    expanded = ("الحبوب" in cat_name or
                                 "الأكساب" in cat_name or
                                 "الزيوت" in cat_name or
                                 "الأملاح" in cat_name)
                    with st.expander(
                            f"📁 {cat_name} ({len(filt)})",
                            expanded=expanded):
                        sc = st.columns(3)
                        for idx, ing_name in enumerate(filt.keys()):
                            with sc[idx % 3]:
                                dflt = ing_name in default_set
                                if st.checkbox(
                                        ing_name, value=dflt,
                                        key=f"pick_v18_{animal_choice}_{ing_name}"):
                                    selected.append(ing_name)

                st.markdown("### 💰 الأسعار")
                prices_dict = {}
                if selected:
                    pcols = st.columns(min(3, len(selected)))
                    for idx, ing in enumerate(selected):
                        with pcols[idx % 3]:
                            prices_dict[ing] = st.number_input(
                                f"💵 {ing} ($/طن)", min_value=5.0,
                                value=float(live_prices.get(ing, 350.0)),
                                step=10.0,
                                key=f"p_v18_{animal_choice}_{ing}")

                st.success(f"✅ المختارة: **{len(selected)}** مادة")

                if st.button("🚀 تشغيل المحرك",
                              type="primary",
                              use_container_width=True,
                              key="run_btn_v18"):
                    if len(selected) < 3:
                        st.error("⚠️ اختر 3 مكونات على الأقل")
                    else:
                        custom_std = requirement_to_standard(requirement)
                        with st.spinner("⏳ جاري التركيب..."):
                            result = auto_formulate_smart(
                                selected, prices_dict, custom_std,
                                standard_key=std_key_global,
                                basis=basis_code, min_quality=70.0,
                                animal_type=animal_choice,
                                production_type=production_type)
                        if result["success"]:
                            st.session_state[
                                "last_formulation_result"] = result
                            st.session_state[
                                "last_formulation_context"] = {
                                "animal_choice": animal_choice,
                                "requirement_name": requirement.name_ar,
                                "basis_label": basis_code,
                                "requirement": requirement,
                                "custom_standard": custom_std,
                                "city": city, "local_rate": local_rate,
                                "local_sym": local_sym,
                                "requester_name": requester_name,
                                "std_key_global": std_key_global,
                                "animal_type": animal_choice,
                                "production_type": production_type}
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")

                if st.session_state.get("last_formulation_result"):
                    result = st.session_state["last_formulation_result"]
                    ctx = st.session_state["last_formulation_context"]
                    formula = result["formula"]
                    actual = result["actual_nutrients"]
                    cost = result["cost"]
                    custom_std = ctx["custom_standard"]
                    quality = result.get("quality_score", 0.0)
                    meets = result.get("meets_standard", False)

                    validation = validate_feed_inputs(formula)
                    if not validation["ok"]:
                        st.markdown("### 🚨 تحذيرات الحدود")
                        for err in validation["errors"]:
                            st.error(err)
                        with st.expander("🔧 قبول التصحيح",
                                          expanded=True):
                            for ing, pct in validation["corrected"].items():
                                orig = formula.get(ing, 0)
                                if abs(orig - pct) > 0.01:
                                    st.markdown(
                                        f"• {ing}: {orig:.2f}% → "
                                        f"**{pct:.2f}%**")
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button("✅ اعتماد المصحح",
                                              type="primary",
                                              use_container_width=True):
                                    result["formula"] = \
                                        validation["corrected"]
                                    result["actual_nutrients"] = \
                                        compute_formula_nutrients(
                                            validation["corrected"])
                                    st.session_state[
                                        "last_formulation_result"] = result
                                    st.rerun()
                            with col_b:
                                if st.button("📄 تقرير التحقق",
                                              use_container_width=True):
                                    pdf_v = generate_validation_pdf_report(
                                        validation, formula)
                                    if pdf_v:
                                        st.download_button(
                                            "⬇️ تحميل", pdf_v,
                                            file_name=(f"Validation_"
                                                       f"{datetime.now():%Y%m%d}.pdf"),
                                            mime="application/pdf")
                    else:
                        st.success("✅ داخل الحدود القياسية")

                    ca_p = (actual.get("Ca", 0) / actual.get("P", 1)
                            if actual.get("P", 0) > 0 else 0)

                    if meets:
                        st.markdown(f"""
                        <div class="quality-good-v113">
                        <h3 style="color:#1b5e20; margin:0;">
                        ✅ جودة: {quality:.1f}%</h3>
                        <p style="color:#2e7d32; margin:6px 0 0 0;">
                        تجتاز 70% — Ca:P = {ca_p:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="quality-bad-v113">
                        <h3 style="color:#c62828; margin:0;">
                        ⚠️ جودة: {quality:.1f}%</h3>
                        <p style="color:#b71c1c;">
                        أقل من 70% — تحتاج تعديلاً</p>
                        </div>
                        """, unsafe_allow_html=True)

                    labels = {"CP": "بروتين CP", "DP": "مهضوم DP",
                              "SE": "SE", "NDF": "NDF", "ADF": "ADF",
                              "EE": "دهن EE", "ASH": "رماد ASH",
                              "Ca": "Ca", "P": "P"}
                    compare_rows = []
                    for k, sv in custom_std.items():
                        if sv == 0: continue
                        cv = actual.get(k, 0.0)
                        diff = cv - sv
                        pct = (diff / sv * 100) if sv else 0
                        ev = evaluate_difference(pct, standard_value=sv)
                        compare_rows.append({
                            "العنصر": labels.get(k, k),
                            "المعيار": f"{sv:.2f}",
                            "المحسوب": f"{cv:.2f}",
                            "الفرق": f"{diff:+.3f}",
                            "الفرق %": f"{pct:+.2f}%",
                            "التقييم": ev["label"],
                            "score": ev["score"]})

                    st.markdown("### 📊 جدول المقارنة")
                    display_df = pd.DataFrame([
                        {k: v for k, v in r.items() if k != "score"}
                        for r in compare_rows])
                    st.dataframe(display_df,
                                  use_container_width=True,
                                  hide_index=True)

                    st.markdown("### 🌾 المكونات")
                    for ing, pct in formula.items():
                        st.markdown(
                            f'<div class="formula-item">▪️ '
                            f'<b>{ing}:</b> {pct:.2f}% '
                            f'({pct*10:.1f} كجم/طن)</div>',
                            unsafe_allow_html=True)

                    st.metric("💰 التكلفة ($/طن)", f"${cost:.2f}")

                    ch1, ch2 = st.columns(2)
                    with ch1:
                        bf = create_colorful_bar_chart(custom_std, actual)
                        if bf:
                            st.image(bf.getvalue(), caption="1️⃣ مقارنة",
                                      use_container_width=True)
                    with ch2:
                        pf = create_colorful_pie_chart(formula)
                        if pf:
                            st.image(pf.getvalue(), caption="2️⃣ توزيع",
                                      use_container_width=True)

                    ch3, ch4 = st.columns(2)
                    with ch3:
                        rf = create_radar_chart(custom_std, actual)
                        if rf:
                            st.image(rf.getvalue(), caption="3️⃣ رادار",
                                      use_container_width=True)
                    with ch4:
                        gf = create_gauge_chart(quality)
                        if gf:
                            st.image(gf.getvalue(), caption="4️⃣ جودة",
                                      use_container_width=True)

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
                                protein_basis=ctx["basis_label"],
                                standard_key=ctx["std_key_global"],
                                include_charts=True,
                                quality_score=quality)
                            st.download_button(
                                "📥 تحميل PDF", pdf_bytes,
                                file_name=(f"Tawor_"
                                           f"{ctx['animal_type']}_"
                                           f"{datetime.now():%Y%m%d}.pdf"),
                                mime="application/pdf",
                                use_container_width=True)
                        except Exception as e:
                            st.error(f"⚠️ PDF: {e}")

        with sub_a:
            render_complete_formula_lab()

    except Exception as e:
        st.error(f"⚠️ {e}")
        with st.expander("🔍 التفاصيل"):
            st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════════════════
# 🌰 الزيوت
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["🌰 الزيوت"]:
    try:
        st.markdown(
            '<div class="section-title">🌰 مكتبة الزيوت</div>',
            unsafe_allow_html=True)
        st.write(f"{len(get_oil_ingredients())} زيتاً وفق NRC / INRA / Ross")

        oil_rows = [{"الحيوان": k, "أقصى %": f"{v['max']}%",
                     "مثالي %": f"{v['optimal']}%",
                     "المرجع": v["source"]}
                    for k, v in MAX_OIL_PERCENTAGE.items()]
        st.dataframe(pd.DataFrame(oil_rows),
                      use_container_width=True, hide_index=True)

        oils = get_oil_ingredients()
        oil_cats = {
            "أوميغا 6": ["زيت ذرة", "زيت عباد الشمس", "زيت فول الصويا"],
            "أوميغا 3": ["زيت الكتان", "زيت الكانولا",
                          "زيت السمك (Fish Oil)"],
            "متوازنة": ["زيت النخيل", "زيت جوز الهند", "زيت الزيتون"]}
        for cat, oil_list in oil_cats.items():
            st.markdown(f"#### {cat}")
            for ing_name in oil_list:
                if ing_name not in oils: continue
                ing_data = oils[ing_name]
                with st.expander(f"🌰 {ing_name}"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("SE", f"{ing_data.get('SE', 0):.0f}")
                    c2.metric("kcal/kg",
                               f"{ing_data.get('SE', 0) * 41:.0f}")
                    c3.metric("السعر",
                               f"${ing_data.get('price', 0):.0f}")
                    st.info(f"📝 {ing_data.get('desc', '')}")
    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 🍼 بدائل الحليب
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["🍼 بدائل الحليب"]:
    try:
        st.markdown(
            '<div class="section-title">🍼 بدائل الحليب</div>',
            unsafe_allow_html=True)
        st.caption("3 مكونات كافية — 4 مثالية — 6 استراتيجيات")

        mr1, mr2 = st.columns(2)
        with mr1:
            mr_a = st.selectbox("الحيوان:",
                list(MILK_REPLACER_STANDARDS.keys()), key="mr_a_v18")
            mr_v = st.number_input("الكمية (كجم):",
                1.0, 10000.0, 100.0, 10.0, key="mr_v_v18")
        with mr2:
            std_mr = MILK_REPLACER_STANDARDS[mr_a]
            st.markdown(f"""
            <div class="price-card">
            <b>📊 {mr_a}</b><br>
            بروتين: {std_mr['CP']}% | دهن: {std_mr['Fat']}% |
            لاكتوز: {std_mr['Lactose']}%<br>
            📖 {std_mr['source']}
            </div>
            """, unsafe_allow_html=True)

        mr_sel = []
        cols = st.columns(3)
        for i, (name, data) in enumerate(
                MILK_REPLACER_INGREDIENTS.items()):
            with cols[i % 3]:
                with st.expander(f"{name}"):
                    st.caption(f"💵 ${data['price']}/كجم | "
                                f"أقصى {data['max']}%")
                    if st.checkbox("إضافة", key=f"mr_v18_{name}"):
                        mr_sel.append(name)

        st.info(f"📊 المختارة: {len(mr_sel)}")

        if st.button("🧪 تركيب", type="primary",
                       use_container_width=True):
            if len(mr_sel) < 3:
                st.warning("⚠️ اختر 3 مكونات على الأقل")
            else:
                with st.spinner("⏳ جاري التركيب..."):
                    r = formulate_milk_replacer(mr_a, mr_v, mr_sel)
                if r["success"]:
                    quality = r.get("quality_score", 0)
                    st.markdown(f"""
                    <div class="{'quality-good-v113' if quality >= 70 else 'quality-bad-v113'}">
                        <h3>جودة: {quality:.1f}% |
                        Ca:P: {r['ca_p_ratio']:.2f}</h3>
                        <p>{r.get('strategy', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if r.get("warning"):
                        st.warning(r["warning"])
                    for ing, pct in r["formula"].items():
                        kg = pct * mr_v / 100.0
                        st.markdown(
                            f'<div class="formula-item">▪️ '
                            f'<b>{ing}:</b> {pct:.2f}% '
                            f'({kg:.2f} كجم)</div>',
                            unsafe_allow_html=True)
                    pdf_mr = generate_milk_replacer_pdf(r)
                    if pdf_mr:
                        st.download_button(
                            "📄 تحميل PDF شامل", pdf_mr,
                            file_name=(f"MilkReplacer_"
                                       f"{datetime.now():%Y%m%d}.pdf"),
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary")
                else:
                    st.error(f"❌ {r['message']}")
    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 📷 OCR
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["📷 OCR"]:
    try:
        st.markdown(
            '<div class="section-title">📷 OCR</div>',
            unsafe_allow_html=True)
        st.caption("96 محاولة (8 معالجات × 3 لغات × 4 PSM)")

        if not OCR_AVAILABLE:
            st.error("⚠️ pytesseract أو opencv غير مثبتة")
        else:
            method = st.radio("الإدخال:", ["📤 رفع", "📸 كاميرا"],
                                horizontal=True, key="ocr_method_v18")
            uploaded = None
            if "رفع" in method:
                up = st.file_uploader("ارفع:", type=["jpg", "jpeg", "png"],
                                        key="ocr_upload_v18")
                if up:
                    uploaded = up.read()
            else:
                cam = st.camera_input("التقط:", key="ocr_camera_v18")
                if cam:
                    uploaded = cam.read()

            if uploaded:
                st.image(uploaded, use_container_width=True)
                if st.button("🔍 تحليل", type="primary",
                               use_container_width=True):
                    with st.spinner("🔬 جاري التحليل..."):
                        result = extract_ingredients_from_image(uploaded)
                    if result["success"] and result["count"] > 0:
                        st.success(f"✅ {result['count']} مادة")
                        nut = compute_formula_nutrients(
                            result["ingredients"])
                        st.dataframe(
                            pd.DataFrame([{"المادة": k, "النسبة": v}
                                          for k, v in
                                          result["ingredients"].items()]),
                            use_container_width=True, hide_index=True)
                        n1, n2, n3, n4 = st.columns(4)
                        n1.metric("CP", f"{nut['CP']:.2f}%")
                        n2.metric("DP", f"{nut['DP']:.2f}%")
                        n3.metric("SE", f"{nut['SE']:.1f}")
                        n4.metric("NDF", f"{nut['NDF']:.2f}%")
                        with st.expander("✏️ تصحيح", expanded=True):
                            corrected = render_ocr_correction_ui(
                                result["ingredients"])
                            if st.button("✅ تطبيق",
                                          type="primary",
                                          use_container_width=True):
                                if corrected:
                                    st.session_state[
                                        "last_ocr_result"] = corrected
                                    st.rerun()
                        try:
                            pdf_ocr = pdf_gen.generate_ocr_report(
                                result["ingredients"], nut)
                            st.download_button(
                                "📄 تحميل PDF", pdf_ocr,
                                file_name=(f"OCR_"
                                           f"{datetime.now():%Y%m%d}.pdf"),
                                mime="application/pdf",
                                use_container_width=True)
                        except Exception as e:
                            st.error(f"⚠️ {e}")
                    else:
                        st.warning(f"⚠️ {result.get('message')}")
    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 📏 تبويب القياسات
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["📏 القياسات"]:
    try:
        st.markdown(
            '<div class="section-title">📏 القياسات والعلف اليومي</div>',
            unsafe_allow_html=True)
        st.caption("🎯 شريط → وزن تقديري → علف يومي دقيق")

        sub_m1, sub_m2, sub_m3 = st.tabs(
            ["📐 تقدير الوزن", "🍽️ العلف اليومي", "📜 السجل"])

        with sub_m1:
            c1, c2 = st.columns([0.42, 0.58])
            with c1:
                m_animal = st.selectbox(
                    "🐾 الحيوان:",
                    list(MEASUREMENT_METHODS.keys()),
                    format_func=lambda k:
                        MEASUREMENT_METHODS[k]["name_ar"],
                    key="meas_animal_v18")
                method = MEASUREMENT_METHODS[m_animal]
                st.markdown(f"""
                <div class="physio-card">
                <h4>📏 الطريقة</h4>
                <p>{method['method']}</p>
                <p style="font-family: monospace; background:#fff;
                   padding:10px; border-radius:6px; direction:ltr;
                   text-align:left;">{method['formula_ar']}</p>
                <p style="color:#666; font-size:0.85rem;">
                📖 {method['source']}</p>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown("### 📐 القياسات (سم)")
                vals = {}
                for m in method["measures"]:
                    vals[m["id"]] = st.number_input(
                        m["label"], 0.0, 300.0, 0.0, 0.5,
                        help=m.get("hint", ""),
                        key=f"meas_{m_animal}_{m['id']}_v18")

                if st.button("🧮 احسب الوزن", type="primary",
                              use_container_width=True):
                    if (vals.get("heart_girth", 0) > 0
                            and vals.get("body_length", 0) > 0):
                        r = estimate_weight_from_tape(
                            m_animal, vals["heart_girth"],
                            vals["body_length"])
                        if r["success"]:
                            r["animal"] = m_animal
                            r["timestamp"] = datetime.now().strftime(
                                "%Y-%m-%d %H:%M")
                            st.session_state["est_weight"] = r
                            st.success(f"📐 الوزن: "
                                        f"**{r['weight_kg']} كجم**")
                    else:
                        st.warning("⚠️ أدخل القياسات")

            if st.session_state.get("est_weight"):
                r = st.session_state["est_weight"]
                st.markdown(f"""
                <div class="measure-result">
                <h3>⚖️ الوزن: {r['weight_kg']} كجم</h3>
                <p style="color:#555; margin-top:8px;">
                📐 صدر: {r['inputs']['heart_girth']} سم |
                طول: {r['inputs']['body_length']} سم |
                📖 {r['source']}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("💾 حفظ بالسجل",
                              use_container_width=True):
                    if "measurement_history" not in st.session_state:
                        st.session_state["measurement_history"] = []
                    st.session_state["measurement_history"].append(dict(r))
                    st.success("✅ محفوظ")

        with sub_m2:
            default_wt = st.session_state.get("est_weight", {}).get(
                "weight_kg", 0)
            default_animal = st.session_state.get("est_weight", {}).get(
                "animal", "أبقار")

            d1, d2 = st.columns([0.42, 0.58])
            with d1:
                animals_dmi = [k for k, v in MEASUREMENT_METHODS.items()
                                if "dmi_pct" in v]
                default_idx = (animals_dmi.index(default_animal)
                               if default_animal in animals_dmi else 0)

                f_animal = st.selectbox(
                    "🐾 الحيوان:", animals_dmi, index=default_idx,
                    format_func=lambda k:
                        MEASUREMENT_METHODS[k]["name_ar"],
                    key="feed_animal_v18")
                f_wt = st.number_input(
                    "⚖️ الوزن (كجم):", 0.1, 2000.0,
                    float(default_wt) if default_wt else 50.0,
                    0.5, key="feed_wt_v18")
                f_stage = st.selectbox("الحالة:",
                    ["صيانة", "نمو", "تسمين", "حمل", "رضاعة",
                     "حليب", "رياضة", "سباق"], key="feed_stage_v18")
                f_conc = st.slider("نسبة المركزات %", 20, 80, 40, 5,
                                     key="feed_conc_v18")

                if st.button("🍽️ احسب العلف", type="primary",
                              use_container_width=True):
                    r = calculate_daily_feed(
                        f_animal, f_wt, f_stage, f_conc)
                    if r["success"]:
                        st.session_state["daily_feed"] = r
                        st.rerun()
                    else:
                        st.error(r["message"])

            with d2:
                if st.session_state.get("daily_feed"):
                    fr = st.session_state["daily_feed"]
                    st.markdown(f"""
                    <div class="measure-result">
                    <h3>🍽️ العلف اليومي — {fr['weight_kg']} كجم</h3>
                    <table style="width:100%; margin-top:15px;
                                  border-collapse:collapse; direction:rtl;">
                    <tr style="background:#fff;">
                    <td style="padding:10px; border:1px solid #c8e6c9;
                        font-weight:600;">📊 DMI</td>
                    <td style="padding:10px; border:1px solid #c8e6c9;
                        text-align:center; font-weight:bold;
                        color:#1b5e20;">{fr['dmi_kg']} كجم</td></tr>
                    <tr style="background:#fff;">
                    <td style="padding:10px; border:1px solid #c8e6c9;
                        font-weight:600;">🥣 المركزات
                        ({fr['concentrate_pct']}%)</td>
                    <td style="padding:10px; border:1px solid #c8e6c9;
                        text-align:center; font-weight:bold;
                        color:#e65100;">{fr['concentrate_kg']} كجم</td></tr>
                    <tr style="background:#fff;">
                    <td style="padding:10px; border:1px solid #c8e6c9;
                        font-weight:600;">🌿 الخشنة</td>
                    <td style="padding:10px; border:1px solid #c8e6c9;
                        text-align:center; font-weight:bold;
                        color:#2e7d32;">{fr['roughage_kg']} كجم</td></tr>
                    <tr style="background:#fff;">
                    <td style="padding:10px; border:1px solid #c8e6c9;
                        font-weight:600;">📖 المرجع</td>
                    <td style="padding:10px; border:1px solid #c8e6c9;
                        text-align:center;">{fr['source']}</td></tr>
                    </table>
                    </div>
                    """, unsafe_allow_html=True)

                    pdf_m = generate_measurement_pdf(fr)
                    if pdf_m:
                        st.download_button(
                            "📄 تحميل PDF", pdf_m,
                            file_name=(f"Feed_"
                                       f"{datetime.now():%Y%m%d}.pdf"),
                            mime="application/pdf",
                            use_container_width=True)
                else:
                    st.info("💡 أدخل الوزن واضغط احسب")

        with sub_m3:
            history = st.session_state.get("measurement_history", [])
            if not history:
                st.info("💡 لا سجلات")
            else:
                df = pd.DataFrame(history)
                st.dataframe(df, use_container_width=True,
                              hide_index=True)
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 CSV", csv,
                    file_name=f"Measurements_{datetime.now():%Y%m%d}.csv",
                    mime="text/csv", use_container_width=True)
                if st.button("🗑️ مسح", use_container_width=True):
                    st.session_state["measurement_history"] = []
                    st.rerun()
    except Exception as e:
        st.error(f"⚠️ {e}")
        with st.expander("🔍 التفاصيل"):
            st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════════════════
# 🏗️ تبويب الحظائر 3D
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["🏗️ الحظائر 3D"]:
    try:
        st.markdown(
            '<div class="section-title">🏗️ مصمم الحظائر 3D</div>',
            unsafe_allow_html=True)

        # 🗺️ خارطة الألوان
        st.markdown("""
        <div style="background:linear-gradient(135deg,#E3F2FD,#BBDEFB);
             padding:16px 20px; border-radius:14px;
             border-right:6px solid #1565C0; margin-bottom:16px;
             direction:rtl;">
        <h4 style="color:#0D47A1; margin:0 0 12px 0;">
        🗺️ خارطة الألوان</h4>
        <div style="display:grid;
             grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
             gap:8px;">
            <div style="background:#fff; padding:8px;
                 border-radius:6px; border:1px solid #90CAF9;">
                <b style="color:#43A047;">🟢 ساحة سليمة</b><br>
                <small>كثافة &lt; 85%</small>
            </div>
            <div style="background:#fff; padding:8px;
                 border-radius:6px; border:1px solid #90CAF9;">
                <b style="color:#FBC02D;">🟡 قريب من الطاقة</b><br>
                <small>85–100%</small>
            </div>
            <div style="background:#fff; padding:8px;
                 border-radius:6px; border:1px solid #90CAF9;">
                <b style="color:#E53935;">🔴 مزدحم</b><br>
                <small>&gt; 100%</small>
            </div>
            <div style="background:#fff; padding:8px;
                 border-radius:6px; border:1px solid #90CAF9;">
                <b style="color:#FF6D00;">🍽️ معلف</b><br>
                <small>ممتد على الجانبين</small>
            </div>
            <div style="background:#fff; padding:8px;
                 border-radius:6px; border:1px solid #90CAF9;">
                <b style="color:#1976D2;">💧 مسقى</b><br>
                <small>ماسة زرقاء</small>
            </div>
            <div style="background:#fff; padding:8px;
                 border-radius:6px; border:1px solid #90CAF9;">
                <b style="color:#2E7D32;">🐄 حيوانات</b><br>
                <small>نقاط خضراء</small>
            </div>
            <div style="background:#fff; padding:8px;
                 border-radius:6px; border:1px solid #90CAF9;">
                <b style="color:#00BCD4;">💨 فتحات التهوية</b><br>
                <small>على الجدران</small>
            </div>
            <div style="background:#fff; padding:8px;
                 border-radius:6px; border:1px solid #90CAF9;">
                <b style="color:#FFC107;">🚶 ممر مركزي</b><br>
                <small>أصفر منقّط</small>
            </div>
        </div>
        <p style="color:#555; font-size:0.85rem; margin:12px 0 0 0;">
        💡 اسحب للدوران — عجلة للتكبير — انقر عنصر للتفاصيل</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            barn_a = st.selectbox("🐾 الحيوان:",
                list(BARN_DESIGN_STANDARDS.keys()),
                format_func=lambda k: BARN_DESIGN_STANDARDS[k]["name_ar"],
                key="barn_animal_v18")
        with c2:
            barn_c = st.number_input("🔢 العدد:", 1, 100000, 1000, 50,
                                       key="barn_count_v18")
        with c3:
            barn_n_pens = st.number_input("🔲 ساحات:", 1, 20, 4, 1,
                                            key="barn_pens_v18")
        with c4:
            pens_row = st.number_input("🔳 بالصف:", 1, 6, 2, 1,
                                         key="barn_pens_row_v18")

        view_mode = st.radio("👁️ العرض:",
            ["🟢 بسيط (رقم فقط)",
             "🔬 احترافي (رقم + كثافة + سعة)"],
            horizontal=True, key="barn_view_mode_v18")
        expert = "احترافي" in view_mode

        dims = calculate_barn_dimensions(barn_a, barn_c)
        if dims:
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("📏 المساحة", f"{dims['total_area_m2']} م²")
            k2.metric("📐 الأبعاد",
                       f"{dims['length_m']}×{dims['width_m']} م")
            k3.metric("🏔️ القمة", f"{dims['ridge_height_m']} م")
            k4.metric("👥 سعة/ساحة",
                       f"{barn_c // barn_n_pens} رأس")

            fig3d = create_barn_with_pens_3d(
                dims, n_pens=barn_n_pens,
                pens_per_row=pens_row, expert=expert)
            if fig3d:
                st.plotly_chart(fig3d, use_container_width=True)

            with st.expander("🔧 تفاصيل هندسية"):
                e1, e2, e3, e4 = st.columns(4)
                e1.metric("🍽️ معالف", dims["feeders_count"])
                e2.metric("📏 طول المعالف",
                           f"{dims['total_feeder_length_m']} م")
                e3.metric("💧 سقايات", dims["drinkers_count"])
                e4.metric("💨 تهوية صيف",
                           f"{dims['vent_flow_summer_m3h']:,} م³/س")
                v1, v2 = st.columns(2)
                v1.metric("💨 مساحة الفتحات",
                           f"{dims['vent_open_area_m2']} م²")
                v2.metric("🌡️ حرارة مثالية",
                           f"{dims['temp_optimal']}°C")

            st.markdown("### 🎬 الفيديو والتقرير")
            col_g, col_p = st.columns(2)
            with col_g:
                if st.button("🎬 توليد GIF",
                              use_container_width=True):
                    with st.spinner("🎥 جاري التوليد..."):
                        vb = create_barn_animation_gif(
                            dims, frames=20, fps=8)
                    if vb:
                        st.session_state["barn_video_gif"] = \
                            vb.getvalue()
                        st.success("✅ تم!")
                    else:
                        st.error("⚠️ تعذر التوليد")

            if st.session_state.get("barn_video_gif"):
                st.image(st.session_state["barn_video_gif"],
                          use_container_width=True)

            with col_p:
                try:
                    pdf_b = generate_barn_pdf_report(dims)
                    st.download_button(
                        "📄 تحميل مخطط PDF", pdf_b,
                        file_name=f"Barn_{barn_a}.pdf",
                        mime="application/pdf",
                        use_container_width=True)
                except Exception as e:
                    st.error(f"⚠️ {e}")
    except Exception as e:
        st.error(f"⚠️ {e}")
        with st.expander("🔍 التفاصيل"):
            st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════════════════
# 📊 الجدوى
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["📊 الجدوى"]:
    try:
        st.markdown(
            '<div class="section-title">📊 دراسة الجدوى</div>',
            unsafe_allow_html=True)

        mode = st.radio("🎯 النوع:",
            ["🔬 فنية", "💰 اقتصادية", "📈 شاملة (+ Monte Carlo)"],
            horizontal=True, key="feas_mode_v18")

        f1, f2 = st.columns(2)
        with f1:
            feas_k = st.selectbox("الحيوان:",
                list(BARN_DESIGN_STANDARDS.keys()),
                format_func=lambda k: BARN_DESIGN_STANDARDS[k]["name_ar"],
                key="feas_animal_v18")
            feas_c = st.number_input("العدد:", 1, 100000, 1000, 50,
                                       key="feas_count_v18")
            proj_name = st.text_input("اسم المشروع:",
                                       key="feas_proj_v18")
        with f2:
            feas_r = st.text_input("مقدم الطلب:", key="feas_req_v18")
            if "اقتصادية" in mode or "شاملة" in mode:
                fp = st.number_input("💵 سعر العلف ($/طن):",
                    50.0, 5000.0, 350.0, 10.0, key="feas_fp_v18")
                pp = st.number_input("💵 سعر المنتج ($/وحدة):",
                    0.1, 10000.0, 2.5, 0.1, key="feas_pp_v18")
                lc = st.number_input("👷 تكلفة العامل:",
                    0.0, 10000.0, 200.0, 10.0, key="feas_lc_v18")
                oc = st.number_input("📊 أخرى:",
                    0.0, 100000.0, 300.0, 50.0, key="feas_oc_v18")

        feas = calculate_technical_feasibility(feas_k, feas_c)
        if feas:
            d = feas["dims"]
            st.markdown("### 🔬 الجدوى الفنية")
            fc1, fc2, fc3, fc4 = st.columns(4)
            fc1.metric("📏 المساحة", f"{d['total_area_m2']} م²")
            fc2.metric("📐 الأبعاد",
                        f"{d['length_m']}×{d['width_m']} م")
            fc3.metric("📦 الحجم", f"{d['volume_m3']} م³")
            fc4.metric("👷 عمال", feas["labor"]["workers"])

            f1_, f2_, f3_, f4_ = st.columns(4)
            f1_.metric("علف/يوم",
                        f"{feas['feed']['total_day_kg']:.1f} كجم")
            f2_.metric("علف/سنة",
                        f"{feas['feed']['total_year_ton']:.2f} طن")
            f3_.metric("ماء/يوم",
                        f"{feas['water']['total_day_L']:.0f} لتر")
            f4_.metric("ماء/سنة",
                        f"{feas['water']['total_year_m3']:.1f} م³")

            if "اقتصادية" in mode or "شاملة" in mode:
                st.markdown("### 💰 الجدوى الاقتصادية")
                feed_yr = feas["feed"]["total_year_ton"]
                feed_cost = feed_yr * fp
                labor_yr = feas["labor"]["workers"] * lc * 12
                other_yr = oc * 12
                total_cost = feed_cost + labor_yr + other_yr
                prod = feas["production"]
                ann_units = prod.get("annual", 0)
                annual_rev = ann_units * pp
                profit = annual_rev - total_cost
                roi = (profit / total_cost * 100
                       if total_cost > 0 else 0)

                e1, e2, e3, e4 = st.columns(4)
                e1.metric("💵 تكلفة", f"${total_cost:,.0f}")
                e2.metric("💰 إيراد", f"${annual_rev:,.0f}")
                e3.metric("📈 ربح", f"${profit:,.0f}",
                            delta=f"{roi:+.1f}%")
                e4.metric("🎯 التعادل",
                           f"{total_cost/pp if pp>0 else 0:,.0f}")

                if profit > 0:
                    st.success(f"✅ مجدٍ — ربح ${profit:,.0f}")
                else:
                    st.error(f"❌ غير مجدٍ — خسارة ${abs(profit):,.0f}")

                if "شاملة" in mode and annual_rev > 0:
                    st.markdown("### 🎲 Monte Carlo (1000 سيناريو)")
                    random.seed()
                    sims = []
                    for _ in range(1000):
                        rf = random.gauss(1.0, 0.15)
                        cf = random.gauss(1.0, 0.10)
                        pf = random.gauss(1.0, 0.12)
                        sr = annual_rev * rf * pf
                        sc = total_cost * cf
                        sims.append({"profit": sr - sc})
                    profits = np.array([s["profit"] for s in sims])
                    p5 = np.percentile(profits, 5)
                    p50 = np.percentile(profits, 50)
                    p95 = np.percentile(profits, 95)
                    prob = (profits > 0).mean() * 100

                    mc1, mc2, mc3, mc4 = st.columns(4)
                    mc1.metric("احتمال الربح", f"{prob:.1f}%")
                    mc2.metric("P5", f"${p5:,.0f}")
                    mc3.metric("متوسط", f"${p50:,.0f}")
                    mc4.metric("P95", f"${p95:,.0f}")

            try:
                booklet = generate_feasibility_booklet(
                    feas_k, feas_c, project_name=proj_name,
                    requester_name=feas_r)
                if booklet:
                    st.download_button(
                        "📥 تحميل كتيّب الجدوى", booklet,
                        file_name=(f"Feasibility_{feas_k}_"
                                   f"{datetime.now():%Y%m%d}.pdf"),
                        mime="application/pdf",
                        use_container_width=True, type="primary")
            except Exception as e:
                st.error(f"⚠️ {e}")
    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 🐔 المزارع
# ═══════════════════════════════════════════════════════════════════════════

BROILER_STANDARDS = {
    7: (0.18, 1.05, 0.15, 0.5),
    14: (0.47, 1.20, 0.55, 1.0),
    21: (0.94, 1.35, 1.20, 1.7),
    28: (1.50, 1.50, 2.10, 2.5),
    35: (2.10, 1.62, 3.30, 3.3),
    42: (2.70, 1.72, 4.70, 4.2),
}


with tab_map["🐔 المزارع"]:
    try:
        st.markdown(
            '<div class="section-title">🐔 المزارع</div>',
            unsafe_allow_html=True)
        farms = st.session_state["broiler_farms"]
        sub_f1, sub_f2 = st.tabs(["➕ جديدة", "📊 المتابعة"])

        with sub_f1:
            with st.form("new_farm_v18"):
                c1, c2 = st.columns(2)
                with c1:
                    nf_name = st.text_input("اسم المزرعة *")
                    nf_strain = st.selectbox("السلالة",
                        ["Ross 308", "Cobb 500", "Hubbard", "Avian"])
                    nf_birds = st.number_input("عدد الطيور", 100,
                                                100000, 1000, 50)
                with c2:
                    nf_date = st.date_input("تاريخ الإدخال")
                    nf_house = st.text_input("رقم العنبر")
                    nf_notes = st.text_area("ملاحظات")
                if st.form_submit_button("💾 حفظ",
                                          type="primary",
                                          use_container_width=True) and nf_name:
                    if nf_name in farms:
                        st.warning("⚠️ الاسم مستخدم")
                    else:
                        farms[nf_name] = {
                            "strain": nf_strain,
                            "start_birds": nf_birds,
                            "start_date": str(nf_date),
                            "house": nf_house, "notes": nf_notes,
                            "records": []}
                        st.success(f"✅ {nf_name}")
                        st.rerun()

        with sub_f2:
            if not farms:
                st.info("💡 لا مزارع")
            else:
                sel = st.selectbox("اختر مزرعة:",
                    list(farms.keys()), key="farm_sel_v18")
                farm = farms[sel]

                with st.form(f"rec_v18_{sel}"):
                    st.markdown(f"### 📝 قراءة — {farm['strain']}")
                    rc = st.columns(5)
                    with rc[0]:
                        age = st.number_input("العمر", 1, 60, 1)
                    with rc[1]:
                        alive = st.number_input("الحية", 1,
                            farm["start_birds"],
                            value=farm["start_birds"])
                    with rc[2]:
                        wt = st.number_input("الوزن (كجم)",
                            0.01, 5.0, 0.045, 0.005)
                    with rc[3]:
                        feed = st.number_input("علف/طير (كجم)",
                            0.0, 20.0, 0.0, 0.05)
                    with rc[4]:
                        temp = st.number_input("حرارة", 15.0,
                                                45.0, 30.0, 0.5)
                    if st.form_submit_button("➕ تسجيل",
                                              type="primary",
                                              use_container_width=True):
                        farm["records"].append({
                            "date": str(datetime.now().date()),
                            "age": age, "alive": alive, "wt": wt,
                            "feed": feed, "temp": temp})
                        st.success("✅")
                        st.rerun()

                if farm["records"]:
                    recs = farm["records"]
                    latest = recs[-1]
                    liv = (latest["alive"] / farm["start_birds"] * 100)
                    fcr = (latest["feed"] / (latest["wt"] - 0.045)
                           if latest["wt"] > 0.045 else 0)
                    adg = ((latest["wt"] - 0.045) * 1000 / latest["age"]
                           if latest["age"] > 0 else 0)
                    epef = ((liv * latest["wt"])
                            / (latest["age"] * fcr) * 100
                            if fcr > 0 and latest["age"] > 0 else 0)
                    std = BROILER_STANDARDS.get(latest["age"],
                                                  (0, 0, 0, 0))
                    std_wt = std[0]

                    m = st.columns(5)
                    m[0].metric("🐦 حيوية", f"{liv:.1f}%")
                    m[1].metric("📈 ADG", f"{adg:.1f} g/d")
                    m[2].metric("⚖️ الوزن", f"{latest['wt']:.3f} كجم",
                                  delta=(f"{(latest['wt']-std_wt):+.3f}"
                                         if std_wt > 0 else None))
                    m[3].metric("🍽️ FCR", f"{fcr:.2f}")
                    m[4].metric("🏆 EPEF", f"{epef:.0f}")

                    with st.expander("📋 السجلات"):
                        st.dataframe(pd.DataFrame(recs),
                                      use_container_width=True,
                                      hide_index=True)
    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# التبويبات الخاصة بالمالك
# ═══════════════════════════════════════════════════════════════════════════

if is_owner():
    with tab_map["🏭 المستودعات"]:
        try:
            st.markdown(
                '<div class="section-title">🏭 المستودعات</div>',
                unsafe_allow_html=True)
            inv = st.session_state["inventory"]
            for k, v in list(inv.items()):
                if not isinstance(v, dict):
                    inv[k] = {"quantity": float(v),
                                "min_threshold": 5.0, "unit": "طن"}

            q = [v["quantity"] for v in inv.values()]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📦 المواد", len(inv))
            c2.metric("🟢 آمنة", sum(1 for x in q if x >= 5))
            c3.metric("🟡 منخفضة", sum(1 for x in q if 0 < x < 5))
            c4.metric("🔴 نافذة", sum(1 for x in q if x <= 0))

            inv_df = pd.DataFrame([{
                "المادة": name,
                "الكمية (طن)": inv[name]["quantity"],
                "الحد الأدنى": inv[name]["min_threshold"],
                "الحالة": ("🔴 نافذ" if inv[name]["quantity"] <= 0
                            else "🟡 منخفض"
                            if inv[name]["quantity"]
                            < inv[name]["min_threshold"]
                            else "🟢 آمن")}
                for name in inv.keys()])

            edited = st.data_editor(
                inv_df, use_container_width=True, hide_index=True,
                column_config={
                    "المادة": st.column_config.TextColumn(disabled=True),
                    "الكمية (طن)": st.column_config.NumberColumn(
                        min_value=0.0, step=1.0),
                    "الحد الأدنى": st.column_config.NumberColumn(
                        min_value=0.0, step=1.0),
                    "الحالة": st.column_config.TextColumn(disabled=True)},
                key="inv_editor_v18")

            if st.button("💾 حفظ", type="primary",
                          use_container_width=True):
                for _, r in edited.iterrows():
                    name = r["المادة"]
                    inv[name]["quantity"] = float(r["الكمية (طن)"])
                    inv[name]["min_threshold"] = float(r["الحد الأدنى"])
                st.success("✅ تم")
                st.rerun()
        except Exception as e:
            st.error(f"⚠️ {e}")

    with tab_map["🧾 الفواتير"]:
        try:
            st.markdown(
                '<div class="section-title">🧾 الفواتير</div>',
                unsafe_allow_html=True)
            sub_i1, sub_i2 = st.tabs(["➕ جديدة", "📚 الأرشيف"])

            with sub_i1:
                with st.form("invoice_v18"):
                    c1, c2 = st.columns(2)
                    with c1:
                        client = st.text_input("العميل *")
                        phone = st.text_input("الهاتف")
                    with c2:
                        inv_date = st.date_input("التاريخ")
                        tax = st.number_input("الضريبة %",
                                               0.0, 30.0, 0.0, 0.5)

                    st.markdown("### 📋 البنود")
                    active = st.session_state.get("active_formula", {})
                    rows = [{"البند": k, "الكمية (طن)": 1.0,
                             "سعر الطن": float(v * 10)}
                            for k, v in active.items()] or [
                            {"البند": "", "الكمية (طن)": 0.0,
                             "سعر الطن": 0.0}]

                    items_df = st.data_editor(
                        pd.DataFrame(rows), num_rows="dynamic",
                        use_container_width=True, hide_index=True,
                        column_config={
                            "البند": st.column_config.TextColumn(),
                            "الكمية (طن)":
                                st.column_config.NumberColumn(
                                    min_value=0.0, step=0.1),
                            "سعر الطن":
                                st.column_config.NumberColumn(
                                    min_value=0.0, step=10.0,
                                    format="$%.2f")},
                        key="inv_items_v18")

                    subtotal = sum(r["الكمية (طن)"] * r["سعر الطن"]
                                    for _, r in items_df.iterrows())
                    tax_amt = subtotal * tax / 100
                    total = subtotal + tax_amt
                    st.metric("الإجمالي", f"${total:,.2f}")

                    if st.form_submit_button("✅ إصدار",
                                              type="primary",
                                              use_container_width=True):
                        if not client or subtotal <= 0:
                            st.error("⚠️ املأ البيانات")
                        else:
                            inv_num = len(
                                st.session_state["invoices"]) + 1
                            invoice = {
                                "number": (f"INV-"
                                           f"{datetime.now():%Y%m}-"
                                           f"{inv_num:04d}"),
                                "date": str(inv_date),
                                "client": client, "phone": phone,
                                "items": items_df.to_dict("records"),
                                "subtotal": subtotal, "tax": tax,
                                "tax_amt": tax_amt, "total": total}
                            st.session_state["invoices"].append(invoice)
                            st.success(f"✅ {invoice['number']}")
                            st.rerun()

            with sub_i2:
                invoices = st.session_state["invoices"]
                if not invoices:
                    st.info("💡 لا فواتير")
                else:
                    summary = pd.DataFrame([{
                        "رقم": i["number"],
                        "التاريخ": i["date"],
                        "العميل": i["client"],
                        "الإجمالي": f"${i['total']:,.2f}"}
                        for i in invoices])
                    st.dataframe(summary,
                                  use_container_width=True,
                                  hide_index=True)

                    sel_num = st.selectbox("اختر فاتورة:",
                        [i["number"] for i in invoices],
                        key="inv_sel_v18")
                    selected_inv = next(
                        i for i in invoices if i["number"] == sel_num)

                    if st.button("📄 PDF", type="primary",
                                   use_container_width=True):
                        if _guard_sensitive_operation("delete_invoice"):
                            pdf_bytes = generate_invoice_pdf(
                                selected_inv)
                            if pdf_bytes:
                                st.download_button(
                                    "⬇️ تحميل", pdf_bytes,
                                    file_name=(f"{selected_inv['number']}"
                                               f".pdf"),
                                    mime="application/pdf",
                                    use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ {e}")

    with tab_map["🖨️ الديباجة"]:
        try:
            st.markdown(
                '<div class="section-title">🖨️ الديباجة</div>',
                unsafe_allow_html=True)
            title_line = st.text_input("العنوان:",
                                          value=APP_NAME,
                                          key="lh_title_v18")
            sub_line = st.text_input("الفرعي:",
                                       value=APP_TAGLINE,
                                       key="lh_sub_v18")

            if st.button("📄 تنزيل", type="primary",
                          use_container_width=True):
                try:
                    pdf_data = generate_letterhead_pdf(
                        title_line, sub_line)
                    if pdf_data:
                        st.download_button(
                            "⬇️ تحميل", pdf_data,
                            file_name=(f"Letterhead_"
                                       f"{datetime.now():%Y%m%d}.pdf"),
                            mime="application/pdf",
                            use_container_width=True)
                except Exception as e:
                    st.error(f"⚠️ {e}")
        except Exception as e:
            st.error(f"⚠️ {e}")

    with tab_map["📈 التحليلات"]:
        try:
            st.markdown(
                '<div class="section-title">📈 التحليلات</div>',
                unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🧬 خلطات",
                       len(st.session_state.get(
                           "formulation_history", [])))
            m2.metric("📷 OCR", 1 if st.session_state.get(
                "last_ocr_result") else 0)
            m3.metric("🐔 مزارع",
                       len(st.session_state.get("broiler_farms", {})))
            m4.metric("🧾 فواتير",
                       len(st.session_state.get("invoices", [])))

            active = st.session_state.get("active_formula", {})
            if active and PLOTLY_AVAILABLE:
                df = pd.DataFrame({"المادة": list(active.keys()),
                                    "النسبة %": list(active.values())})
                fig = px.bar(df, x="المادة", y="النسبة %",
                              color="النسبة %",
                              color_continuous_scale="Greens")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ {e}")

    with tab_map["💬 التعليقات"]:
        try:
            st.markdown(
                '<div class="section-title">💬 التعليقات</div>',
                unsafe_allow_html=True)
            if not st.session_state.get("comments_list"):
                raw = (SharedStorage.get("shared_comments")
                       or st.session_state.get("shared_comments", ""))
                st.session_state["comments_list"] = [
                    ln.strip() for ln in raw.split("\n") if ln.strip()]

            comments = st.session_state["comments_list"]
            st.markdown(f"### 📜 ({len(comments)})")
            for i, c in enumerate(comments):
                col1, col2 = st.columns([0.92, 0.08])
                with col1:
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,
                    #f1f8e9,#e8f5e9); padding:12px;
                    border-radius:10px; margin-bottom:8px;
                    border-right:4px solid #2e7d32;
                    direction:rtl;">{c}</div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("🗑️", key=f"del_c_v18_{i}"):
                        if _guard_sensitive_operation("delete_comment"):
                            comments.pop(i)
                            SharedStorage._save(
                                {"shared_comments": "\n".join(comments)})
                            st.session_state["comments_list"] = comments
                            st.rerun()

            new_comment = st.text_area("اكتب:", key="cm_new_v18")
            if st.button("➕ نشر", type="primary",
                          use_container_width=True):
                if new_comment.strip():
                    line = (f"• [{datetime.now():%Y-%m-%d %H:%M}]: "
                            f"{new_comment.strip()}")
                    comments.append(line)
                    SharedStorage._save(
                        {"shared_comments": "\n".join(comments)})
                    st.session_state["comments_list"] = comments
                    st.rerun()
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# المراجع والمساعدة والدليل
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["📚 المراجع"]:
    st.markdown(
        '<div class="section-title">📚 المراجع العلمية</div>',
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
- **Schaeffer (1971)** — Weight from Tape
- **Carroll & Huntington (1988)** — Horse Weight
- **Danø & Højsgaard (2005)** — LP Formulation
- **AAFCO (2020)** — Feed Standards
- **MWPS-1** — Structures Handbook
    """)


with tab_map["💡 المساعدة"]:
    st.markdown(
        '<div class="section-title">💡 المساعدة</div>',
        unsafe_allow_html=True)
    st.markdown(f"""
### الأسئلة الشائعة:

**1. كيف أبدأ؟**
اختر الحيوان → فعّل ✅ → اختر 3+ مكونات → 🚀

**2. مختبر التركيبة الكاملة؟**
في تبويب النمذجة → التبويب الفرعي الثاني
- أدخل عدة مكونات + نسبها
- فحص تلقائي: مجموع = 100%
- تحقق من الحدود العالمية
- مقارنة مع 15 معيار
- تصدير PDF + JSON

**3. القياسات؟**
شريط حول الصدر + طول الجسم → وزن → علف يومي

**4. الحدود العالمية؟**
- المركزات: 5% أو 10% فقط
- ملح الطعام: ≤ 0.5%
- اليوريا: ≤ 1.5% للمجترات
- تصحيح تلقائي

**5. الحظائر 3D؟**
- خارطة ألوان في الأعلى
- وضع بسيط/احترافي
- 8 عناصر ملونة (ساحات، علافات، مساقي، حيوانات، تهوية، ممر)

**6. Monte Carlo؟**
1000 سيناريو احتمالي في تبويب الجدوى

**7. الأمان؟**
- fail-closed (OWNER_CODE في secrets)
- قفل تصاعدي: 5د / 30د / 24س

### 📞 التواصل
📧 {OWNER_EMAIL}
📱 {WHATSAPP_NUMBER}

{DUA_FULL}
    """)


with tab_map["📖 الدليل"]:
    st.markdown(
        '<div class="section-title">📖 الدليل</div>',
        unsafe_allow_html=True)
    st.markdown(f"""
### 🎯 {APP_NAME} v{APP_VERSION}

### ✨ الميزات
- 🔐 أمان fail-closed
- 📏 قياسات (5 حيوانات)
- 🍽️ علف يومي (DMI)
- 🔒 حدود عالمية صارمة
- 🔧 تصحيح تلقائي
- 🧪 مختبر التركيبة الكاملة (جديد!)
- 🏗️ حظائر 3D بخارطة ألوان
- 🍼 بدائل حليب (6 استراتيجيات)
- 📷 OCR (96 محاولة)
- 📊 جدوى + Monte Carlo

### 🔐 الدخول
- 👑 **مالك:** اضبط `OWNER_CODE` في secrets
- 👥 **زائر:** مجاني (بدون مستودعات/فواتير)

### 📞 التواصل
📧 {OWNER_EMAIL}
📱 {WHATSAPP_NUMBER}

---
{DUA_FULL}
    """)


# ═══════════════════════════════════════════════════════════════════════════
# التذييل الثابت
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(
    f'<div class="mini-signature">🌾 {APP_NAME} v{APP_VERSION} | '
    f'{SUPERVISOR} © 2026</div>',
    unsafe_allow_html=True)
st.markdown(
    f'<div class="dua-fixed-banner">🤲 {DUA_SHORT} 🤲</div>',
    unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# نهاية الملف — Tawor Nology v11.8
# ═══════════════════════════════════════════════════════════════════════════

print(f"\n{'='*70}")
print(f"✅ {APP_NAME} v{APP_VERSION} جاهز للتشغيل")
print(f"{'='*70}")
print("⚠️ قبل التشغيل — أنشئ .streamlit/secrets.toml:")
print('   OWNER_CODE = "كودك-السري"')
print(f"{'='*70}\n")
