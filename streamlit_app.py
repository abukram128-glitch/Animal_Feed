# ═══════════════════════════════════════════════════════════════════════════
# تاور نولجي TAWOR NOLOGY 11.7 — نسخة أمنية-علمية-تقنية كاملة
# د. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
# ═══════════════════════════════════════════════════════════════════════════
# التغييرات في 11.7 (مقارنة بـ 11.6):
#   🔐 كود المالك: fail-closed — لا كود في المصدر إطلاقاً
#      → يجب ضبط OWNER_CODE في st.secrets أو TAWOR_OWNER_CODE في env
#   🔐 قفل تصاعدي (3→5د / 6→30د / 9→24س)
#   🔐 حماية العمليات الحساسة (_guard_sensitive_operation)
#   📏 محرك قياسات الشريط — 5 حيوانات (أبقار/أغنام/ماعز/إبل/خيول)
#   🍽️ حساب العلف اليومي تلقائياً من الوزن والحالة
#   🔒 GLOBAL_SAFETY_LIMITS — مركزات 5%/10% فقط + أملاح صارمة
#   🔧 validate_feed_inputs — تصحيح تلقائي للتركيبات المتجاوزة
#   🏗️ حظائر 3D بوضعين (بسيط/احترافي) + ساحات مرقمة ملوّنة
#   📄 PDFs جديدة: تقرير العلف اليومي + تقرير التحقق من الحدود
#   ✅ جميع إصلاحات 11.6 محفوظة (بدائل الحليب، OCR، المزارع، ...)
# ═══════════════════════════════════════════════════════════════════════════

import streamlit as st
import numpy as np
import pandas as pd
import io
import os
import re
import base64
import tempfile
import traceback
import warnings
import json
import threading
import random
import hashlib
import hmac
import time as _time
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Tuple, Any, Union, Set

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════════
# الاستيرادات الاختيارية — كل منها مع fallback آمن
# ═══════════════════════════════════════════════════════════════════════════

try:
    from scipy.optimize import linprog
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    linprog = None

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Wedge, Rectangle
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
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.platypus import (
        Table, TableStyle, Paragraph, Spacer, Image as RLImage,
        SimpleDocTemplate, HRFlowable, PageBreak, KeepTogether
    )
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY, TA_LEFT
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
# 🔐 وحدة الأمان v11.7 — fail-closed، لا كود في المصدر
# ═══════════════════════════════════════════════════════════════════════════

def _sha256(s: str) -> str:
    """تجزئة SHA-256 نصية آمنة."""
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def _get_owner_code_hash() -> Optional[str]:
    """
    يبحث عن كود المالك بالترتيب التالي:
      1. st.secrets["OWNER_CODE"]         — أعلى أماناً (Streamlit Cloud)
      2. os.environ["TAWOR_OWNER_CODE"]   — خادم محلي
      3. (لا شيء) → فشل آمن (لا يُفتح المالك بدون إعداد)

    ⚠️ لا يوجد أي كود صريح أو مُشوّش في المصدر — fail-closed.
    """
    # 1) Secrets
    try:
        if hasattr(st, "secrets"):
            code = str(st.secrets.get("OWNER_CODE", "") or "").strip()
            if len(code) >= 6:
                return _sha256(code)
    except Exception:
        pass

    # 2) Environment
    try:
        code = str(os.environ.get("TAWOR_OWNER_CODE", "") or "").strip()
        if len(code) >= 6:
            return _sha256(code)
    except Exception:
        pass

    # 3) فشل آمن
    return None


def check_owner_code(user_input: str) -> bool:
    """مقارنة constant-time — تمنع timing attacks."""
    if not user_input:
        return False
    expected = _get_owner_code_hash()
    if not expected:
        return False
    return hmac.compare_digest(_sha256(user_input.strip()), expected)


def _session_valid() -> bool:
    """تمنع التلاعب بـ session_state (approval/role)."""
    approved = st.session_state.get("approved", False)
    role = st.session_state.get("user_role")
    if approved and role not in ("owner", "guest"):
        return False
    if role == "owner" and not _get_owner_code_hash():
        return False
    return True


def _owner_login_attempt(user_input: str) -> Tuple[bool, str]:
    """
    يتحقق من الكود مع قفل تصاعدي:
      3 محاولات فاشلة → قفل 5 دقائق
      6 محاولات       → قفل 30 دقيقة
      9 محاولات       → قفل 24 ساعة
    """
    now = _time.time()
    lock_until = st.session_state.get("owner_lock_until", 0.0)
    if now < lock_until:
        remain = int(lock_until - now)
        return False, f"🔒 مقفل — انتظر {remain} ثانية"

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
    """حماية العمليات الحساسة (حذف، تعديل أسعار، تصدير)."""
    if not _session_valid():
        st.error("⚠️ جلسة غير صالحة — أعد الدخول")
        return False
    if operation in ("delete_invoice", "delete_farm",
                     "delete_comment", "edit_prices"):
        if st.session_state.get("user_role") != "owner":
            st.error("⚠️ هذه العملية للمالك فقط")
            return False
    return True


# ═══════════════════════════════════════════════════════════════════════════
# الثوابت العامة
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
APP_VERSION = "11.7"
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
    initial_sidebar_state="collapsed"
)


def safe_section(func):
    """Decorator لالتقاط الأخطاء بأمان."""
    @wraps(func)
    def wrapper(*a, **k):
        try:
            return func(*a, **k)
        except Exception as e:
            st.error(f"⚠️ خطأ: {type(e).__name__}")
            with st.expander("🔍 التفاصيل الفنية"):
                st.code(traceback.format_exc())
            st.info(f"💡 أعد التحميل (F5) | {OWNER_EMAIL}")
    return wrapper


# ═══════════════════════════════════════════════════════════════════════════
# إدارة الخطوط العربية
# ═══════════════════════════════════════════════════════════════════════════

FONT_DIR = "fonts"
os.makedirs(FONT_DIR, exist_ok=True)


class ArabicFontManager:
    """Singleton يحمّل خط أميري للـ PDF، مع fallback على DejaVu."""

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

        # محاولة تحميل
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
    """يعرّب النص لسياق RTL في PDF (مع cache)."""
    if not text:
        return ""
    if not ARABIC_AVAILABLE:
        return str(text)
    try:
        return get_display(arabic_reshaper.reshape(str(text)), base_dir='R')
    except Exception:
        return str(text)


def ar(text):
    """اختصار لدالة التعريب."""
    return _ar_cached(text)


print(f"[Tawor Nology {APP_VERSION}] الجزء 1/5 — تم تحميل: الأمان + الثوابت + الخطوط")
print("✅ fail-closed جاهز — اضبط OWNER_CODE في st.secrets قبل التشغيل")
# ═══════════════════════════════════════════════════════════════════════════
# مكتبة الأعلاف الشاملة — 200+ مكوناً
# ═══════════════════════════════════════════════════════════════════════════

def _feed(cp, dc, se, ndf, adf, ee, ash, ca, p, lys, met, price, desc, src):
    """دالة مساعدة لإنشاء قاموس مكوّن علفي."""
    return {
        "CP": cp, "DC": dc, "SE": se, "NDF": ndf, "ADF": adf,
        "EE": ee, "ASH": ash, "Ca": ca, "P": p,
        "Lys": lys, "Met": met,
        "price": price, "desc": desc, "src": src
    }


BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": _feed(8.5, .85, 80, 9.5, 3.2, 3.8, 1.3, .02, .27, .24, .17, 230, "الطاقة الرئيسية", "NRC 2012"),
        "ذرة بيضاء": _feed(8.8, .83, 78, 10.2, 3.5, 3.5, 1.4, .02, .26, .25, .18, 225, "بديل محلي", "NRC 2012"),
        "ذرة شامية": _feed(8.3, .86, 82, 9, 3, 4, 1.2, .02, .28, .23, .16, 240, "طاقة أعلى", "NRC 2012"),
        "ذرة رفيعة (سورجم)": _feed(10, .78, 70, 12.5, 5.5, 3, 1.8, .03, .3, .22, .17, 195, "بديل جزئي", "NRC 2012"),
        "ذرة بيضاء (سورغم أبيض)": _feed(9.2, .80, 73, 11, 4.8, 3.2, 1.6, .03, .28, .23, .17, 210, "بديل", "NRC 2012"),
        "شعير مطحون": _feed(11.5, .8, 71, 18.5, 7.5, 2.2, 2.5, .05, .35, .42, .2, 210, "للمجترات", "NRC 2012"),
        "شعير كامل": _feed(10.8, .75, 68, 22, 9, 2, 2.8, .05, .33, .4, .18, 200, "يحتاج جرش", "NRC 2012"),
        "قمح محلي": _feed(12, .85, 75, 11.5, 3.8, 2, 1.6, .04, .32, .35, .2, 240, "طاقة جيدة", "NRC 2012"),
        "قمح مستورد": _feed(11.5, .87, 78, 11, 3.5, 1.9, 1.5, .04, .33, .34, .19, 245, "طاقة أعلى", "NRC 2012"),
        "قمح صلب (ديوروم)": _feed(13, .88, 76, 12, 4, 1.8, 1.8, .04, .34, .36, .20, 255, "بروتين أعلى", "NRC 2012"),
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
        "كسب بذور العنب": _feed(12, .55, 30, 45, 32, 7.5, 6, .25, .4, .4, .2, 140, "مضاد أكسدة", "INRA 2018"),
        "كسب بذور القرطم": _feed(24, .7, 45, 35, 22, 2, 6, .35, .75, .9, .45, 300, "بديل", "NRC 2007"),
        "كسب الكانولا": _feed(36, .82, 60, 28, 18, 3.5, 6.5, .65, 1.1, 1.9, .7, 400, "متوازن", "NRC 2012"),
        "كسب الأفوكادو": _feed(18, .65, 50, 40, 28, 8, 5.5, .3, .45, .7, .35, 280, "نادر", "INRA 2018"),
        "كسب الجوجوبا": _feed(28, .6, 40, 42, 30, 12, 6.5, .3, .55, .9, .5, 380, "معادلة", "FAO 2010"),
        "كسب المريمية": _feed(22, .6, 38, 38, 26, 8, 8, 1.2, .4, .8, .35, 260, "مضاد", "INRA 2018"),
        "كسب الكزبرة": _feed(20, .6, 35, 40, 28, 6, 7.5, 1, .35, .75, .3, 250, "مضاد", "INRA 2018"),
        "فول صويا كامل": _feed(38, .85, 78, 15, 10, 18, 4.5, .25, .55, 2.5, .55, 420, "معالجة حرارياً", "NRC 2012"),
        "ترمس حلو": _feed(32, .8, 65, 20, 12, 6, 4, .2, .45, 1.8, .35, 380, "بديل", "NRC 2007"),
        "بازلاء علفية": _feed(22, .82, 70, 15, 8, 1.5, 3, .1, .4, 1.5, .25, 320, "متوازن", "NRC 2012"),
        "عدس علفي": _feed(25, .8, 65, 18, 10, 1.2, 3.5, .15, .45, 1.7, .3, 350, "جيد", "NRC 2012"),
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": _feed(15, .72, 45, 35.5, 12.5, 3.5, 5.5, .12, 1.1, .6, .25, 150, "اقتصادية", "NRC 2001"),
        "نخالة ذرة": _feed(9.5, .65, 40, 40, 15, 4, 2, .1, .75, .3, .15, 140, "اقتصادية", "NRC 2001"),
        "البرسيم الجاف": _feed(16.5, .6, 35, 42.5, 32.5, 2, 10.5, 1.5, .25, .85, .25, 170, "بروتين + ألياف", "NRC 2001"),
        "برسيم حجازي": _feed(18, .62, 38, 40, 30, 2.2, 11, 1.6, .26, .9, .28, 175, "أفضل جودة", "NRC 2001"),
        "مولاس قصب السكر": _feed(4, .95, 50, 1.5, .8, .5, 8.5, .7, .05, .03, .02, 120, "طاقة سريعة", "NRC 2001"),
        "تبن قمح": _feed(3.2, .35, 18, 72.5, 45.5, 1.5, 8.5, .3, .08, .15, .05, 80, "ألياف حشو", "NRC 2001"),
        "تبن فول": _feed(4.5, .4, 22, 68, 42, 1.2, 7.5, .35, .1, .18, .08, 90, "أفضل من القمح", "NRC 2001"),
        "تبن عدس": _feed(5, .42, 24, 65, 40, 1.5, 8, .4, .12, .2, .08, 95, "مقبول", "NRC 2001"),
        "قشر فول سوداني": _feed(5, .3, 15, 65.5, 42.5, 1, 5.5, .25, .1, .15, .05, 70, "حشو", "NRC 2007"),
        "سرسة الأرز": _feed(2.5, .25, 12, 68.5, 48.5, 12.5, 15.5, .15, .08, .1, .05, 60, "حشو", "NRC 2007"),
        "قش أرز": _feed(3.5, .3, 15, 70, 45, 1.5, 12, .2, .06, .12, .05, 65, "حشو", "NRC 2007"),
        "مخلفات النخيل": _feed(6.5, .7, 60, 25, 15, 5, 3.5, .15, .15, .25, .1, 100, "للإبل", "FAO 2010"),
        "سعف نخيل مطحون": _feed(4, .3, 20, 65, 42, 2, 7, .35, .08, .15, .06, 55, "ألياف", "FAO 2010"),
        "قشور الفول السوداني": _feed(6.5, .4, 22, 58, 38, 2.5, 4, .2, .12, .2, .08, 75, "حشو", "NRC 2007"),
        "أوراق موز مجففة": _feed(12, .55, 30, 45, 30, 3, 10, 1.2, .2, .5, .2, 85, "نادر", "FAO 2010"),
        "أوراق مانجو": _feed(10, .5, 28, 48, 32, 3.5, 9, 1.5, .15, .45, .18, 80, "معادن", "FAO 2010"),
        "أوراق نخيل": _feed(5, .35, 22, 62, 42, 2.5, 6.5, .4, .1, .15, .06, 50, "ألياف", "FAO 2010"),
        "تفل قصب السكر": _feed(3, .3, 15, 70, 48, 1, 3, .2, .08, .1, .05, 45, "حشو", "FAO 2010"),
        "قوالح ذرة": _feed(2.5, .25, 12, 72, 45, 1, 3, .15, .08, .1, .05, 40, "حشو", "FAO 2010"),
        "قش عدس": _feed(4.5, .35, 18, 68, 43, 1.2, 9, .35, .1, .15, .06, 60, "حشو", "NRC 2001"),
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": _feed(60, .85, 65, 2.5, 1.5, 8.5, 22.5, 5.5, 3.2, 4.5, 1.8, 850, "ممتاز", "NRC 2012"),
        "مسحوق أسماك 72%": _feed(72, .9, 72, 2, 1, 9.5, 18.5, 4.8, 2.8, 5.5, 2.2, 1100, "مرتفع جداً", "NRC 2012"),
        "مسحوق اللحم والعظم": _feed(50, .75, 50, 3.5, 2.5, 10.5, 32.5, 9, 4.5, 2.5, .7, 620, "Ca+P", "NRC 2012"),
        "مسحوق الدم": _feed(80, .65, 55, 1, .5, 1.5, 6, .3, .3, 7, 1, 780, "هضم منخفض", "NRC 2012"),
        "مسحوق ريش": _feed(82, .7, 60, 1.5, 1, 3, 4, .25, .35, 2, .5, 650, "معالجة حرارية", "NRC 2012"),
        "مسحوق مخلفات دواجن": _feed(55, .78, 58, 5, 3, 12, 15, 3, 1.8, 2.8, .8, 550, "يحتاج فحص", "NRC 2012"),
        "مركزات دواجن": _feed(40, .85, 60, 8.5, 4.5, 3.5, 12.5, 2.5, 1.2, 2.5, .9, 650, "جاهزة — 5% أو 10% فقط", "NRC 2012"),
        "مركزات مواشي": _feed(36, .8, 55, 15.5, 8.5, 3, 15.5, 3, 1.5, 2, .7, 600, "جاهزة — 10/20/30% فقط", "NRC 2001"),
        "بروتين بلازما الدم": _feed(78, .9, 62, .5, 0, 2, 10, .15, .2, 6.5, .9, 2400, "للحيوانات الصغيرة", "NRC 2012"),
        "بيض مجفف": _feed(48, .9, 78, 0, 0, 40, 4, .2, .2, 3.5, 1.5, 1500, "بروتين + دهن", "NRC 2012"),
        "حشرات مجففة (BSF)": _feed(42, .8, 68, 8, 5, 35, 8, .8, .9, 2.6, .85, 1800, "مستدام", "FAO 2013"),
        "دود قز مجفف": _feed(55, .75, 55, 4, 3, 25, 8.5, .5, .8, 3.2, 1.2, 1400, "غني", "FAO 2010"),
    },
    "🌿 الأعلاف الخضراء المائية": {
        "أزولا مجففة": _feed(24, .65, 45, 38, 25, 3.5, 18, 2, .6, 1, .4, 340, "نباتي رخيص", "FAO 2010"),
        "سبيرولينا": _feed(60, .85, 65, 5, 3, 6, 10, 1.2, .9, 3, 1.4, 3200, "سوبر فود", "FAO 2010"),
        "كلوريلا": _feed(55, .8, 60, 6, 3.5, 8, 12, .5, 1.2, 2.5, 1.2, 2800, "مكمل", "FAO 2010"),
        "طحالب بحرية": _feed(15, .6, 30, 25, 15, 2, 30, 1.5, .3, .6, .25, 900, "معادن", "FAO 2010"),
        "لمنا مجففة": _feed(20, .55, 35, 30, 20, 3, 15, 1.8, .55, .8, .3, 280, "للدواجن", "FAO 2010"),
        "سالفينيا": _feed(22, .6, 40, 32, 22, 3.5, 16, 1.5, .55, .85, .35, 300, "بديل", "FAO 2010"),
        "أوراق كينوا": _feed(18, .6, 40, 32, 22, 4.5, 12, 1.2, .4, 1, .35, 240, "نادر", "FAO 2010"),
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
        "زيت الأفوكادو": _feed(0, 0, 210, 0, 0, 100, 0, 0, 0, 0, 0, 4200, "فيتامين E", "NRC 2012"),
        "زيت القرطم": _feed(0, 0, 205, 0, 0, 100, 0, 0, 0, 0, 0, 1800, "أوميغا 6", "NRC 2012"),
        "زيت الفول السوداني": _feed(0, 0, 210, 0, 0, 100, 0, 0, 0, 0, 0, 2200, "طاقة", "NRC 2012"),
        "شحم حيواني (Tallow)": _feed(0, 0, 230, 0, 0, 100, 0, 0, 0, 0, 0, 900, "طاقة عالية", "NRC 2012"),
        "سمن حيواني (Lard)": _feed(0, 0, 225, 0, 0, 100, 0, 0, 0, 0, 0, 850, "يُتجنب للدواجن", "NRC 2012"),
        "دهن الدجاج": _feed(0, 0, 225, 0, 0, 100, 0, 0, 0, 0, 0, 800, "للدواجن", "NRC 2012"),
        "زيت السمك (Fish Oil)": _feed(0, 0, 235, 0, 0, 100, 0, 0, 0, 0, 0, 3800, "EPA/DHA", "NRC Fish"),
        "زيت بذور العنب": _feed(0, 0, 200, 0, 0, 100, 0, 0, 0, 0, 0, 2400, "مضاد أكسدة", "INRA 2018"),
        "زيت الأرز": _feed(0, 0, 220, 0, 0, 100, 0, 0, 0, 0, 0, 1600, "فيتامين E", "INRA 2018"),
        "زيت الخردل": _feed(0, 0, 200, 0, 0, 100, 0, 0, 0, 0, 0, 1400, "اقتصادي", "INRA 2018"),
        "زيت بذور اللفت": _feed(0, 0, 205, 0, 0, 100, 0, 0, 0, 0, 0, 1350, "كانولا", "INRA 2018"),
        "زيت الجوجوبا": _feed(0, 0, 210, 0, 0, 100, 0, 0, 0, 0, 0, 5500, "نادر", "INRA 2018"),
        "زيت الكافيار": _feed(0, 0, 230, 0, 0, 100, 0, 0, 0, 0, 0, 12000, "فاخر", "INRA 2018"),
        "زيت اللوز الحلو": _feed(0, 0, 210, 0, 0, 100, 0, 0, 0, 0, 0, 3600, "فيتامين E", "INRA 2018"),
        "زيت المورينجا": _feed(0, 0, 205, 0, 0, 100, 0, 0, 0, 0, 0, 4800, "مضاد أكسدة", "FAO 2010"),
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": _feed(94, 1, 0, 0, 0, 0, .5, 0, 0, 94, 0, 4200, "أساسي", "NRC 2012"),
        "ليسين سلفات": _feed(79, 1, 0, 0, 0, 0, .5, 0, 0, 79, 0, 3800, "بديل أرخص", "NRC 2012"),
        "ميثيونين نقي": _feed(58, 1, 0, 0, 0, 0, .3, 0, 0, 0, 58, 5800, "للدواجن", "NRC 2012"),
        "ميثيونين هيدروكسي": _feed(88, 1, 0, 0, 0, 0, .2, 0, 0, 0, 88, 6500, "MHA", "NRC 2012"),
        "ثريونين نقي": _feed(72, 1, 0, 0, 0, 0, .2, 0, 0, 0, 0, 4800, "ثالث محدود", "NRC 2012"),
        "تريبتوفان نقي": _feed(85, 1, 0, 0, 0, 0, .1, 0, 0, 0, 0, 9500, "للدواجن", "NRC 2012"),
        "فالين نقي": _feed(90, 1, 0, 0, 0, 0, .1, 0, 0, 0, 0, 8200, "أساسي", "NRC 2012"),
        "أرجينين": _feed(98, 1, 0, 0, 0, 0, .2, 0, 0, 0, 0, 7800, "للدواجن", "NRC 2012"),
        "هيستيدين": _feed(96, 1, 0, 0, 0, 0, .2, 0, 0, 0, 0, 7200, "أساسي", "NRC 2012"),
        "إيزوليوسين": _feed(90, 1, 0, 0, 0, 0, .1, 0, 0, 0, 0, 8500, "BCAA", "NRC 2012"),
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
        "إنزيم NSP": _feed(0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 3800, "تحليل ألياف", "NRC 2012"),
        "إنزيم بروتييز": _feed(0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 4500, "تحليل بروتين", "NRC 2012"),
        "إنزيم أميليز": _feed(0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 4000, "تحليل نشاء", "NRC 2012"),
        "مستخلص الخمائر MOS": _feed(12, .5, 10, 2.5, 1.5, 1.5, 8.5, .1, .2, .4, .15, 12000, "مناعة", "NRC 2012"),
        "خمائر حية": _feed(45, .75, 30, 8, 4, 1, 8, .15, 1.2, 3, .7, 8500, "للمجترات", "NRC 2001"),
        "بروبيوتيك": _feed(15, .6, 20, 5, 3, 2, 15, .3, .5, .5, .2, 9800, "بكتيريا نافعة", "NRC 2012"),
        "بريبيوتيك FOS": _feed(0, 0, 40, 0, 0, 0, 2, 0, 0, 0, 0, 6500, "غذاء للبكتيريا", "NRC 2012"),
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": _feed(0, 0, 0, 0, 0, 0, 99.5, 38, 0, 0, 0, 40, "مصدر Ca", "NRC 2012"),
        "فوسفات ثنائي الكالسيوم": _feed(0, 0, 0, 0, 0, 0, 98.5, 23, 18, 0, 0, 280, "Ca+P", "NRC 2012"),
        "فوسفات أحادي الكالسيوم": _feed(0, 0, 0, 0, 0, 0, 99, 17, 22, 0, 0, 320, "مصدر P", "NRC 2012"),
        "ملح الطعام": _feed(0, 0, 0, 0, 0, 0, 99.9, 0, 0, 0, 0, 30, "NaCl — ≤0.5%", "NRC 2012"),
        "بيكربونات الصوديوم": _feed(0, 0, 0, 0, 0, 0, 99, 0, 0, 0, 0, 340, "مضاد حموضة", "NRC 2001"),
        "أكسيد المغنيسيوم": _feed(0, 0, 0, 0, 0, 0, 99.5, 0, 0, 0, 0, 480, "Mg", "NRC 2007"),
        "كبريتات المغنيسيوم": _feed(0, 0, 0, 0, 0, 0, 98, 0, 0, 0, 0, 380, "MgSO4", "NRC 2007"),
        "يوريا علفية": _feed(287, .95, 0, 0, 0, 0, 1, 0, 0, 0, 0, 480, "NPN — ≤1.5% للمجترات فقط", "NRC 2001"),
        "مضاد سموم فطرية": _feed(0, 0, 0, 0, 0, 0, 85, 0, 0, 0, 0, 950, "أفلاتوكسين — ≤0.2%", "NRC 2012"),
        "مضاد أكسدة BHT": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 1200, "تزنخ — ≤0.02%", "NRC 2012"),
        "كولين كلوريد": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 3200, "B4 — ≤0.3%", "NRC 2012"),
        "كبريتات النحاس": _feed(0, 0, 0, 0, 0, 0, 95, 0, 0, 0, 0, 1800, "Cu", "NRC 2012"),
        "كبريتات الزنك": _feed(0, 0, 0, 0, 0, 0, 96, 0, 0, 0, 0, 2200, "Zn", "NRC 2012"),
        "سيلينيت الصوديوم": _feed(0, 0, 0, 0, 0, 0, 98, 0, 0, 0, 0, 4500, "Se", "NRC 2012"),
        "يوديد البوتاسيوم": _feed(0, 0, 0, 0, 0, 0, 99, 0, 0, 0, 0, 3800, "I", "NRC 2012"),
    },
    "💊 الفيتامينات": {
        "فيتامين A": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 4200, "نمو ورؤية", "NRC 2012"),
        "فيتامين D3": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 5200, "امتصاص Ca", "NRC 2012"),
        "فيتامين E": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 5800, "مضاد أكسدة", "NRC 2012"),
        "فيتامين K": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 4600, "تجلط الدم", "NRC 2012"),
        "فيتامين B1 (ثيامين)": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 3800, "أعصاب", "NRC 2012"),
        "فيتامين B2 (ريبوفلافين)": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 4200, "طاقة", "NRC 2012"),
        "فيتامين B3 (نياسين)": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 3400, "تمثيل غذائي", "NRC 2012"),
        "فيتامين B5 (بانتوثنيك)": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 3600, "هضم", "NRC 2012"),
        "فيتامين B6 (بيريدوكسين)": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 3800, "أحماض أمينية", "NRC 2012"),
        "فيتامين B12 (كوبالامين)": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 8500, "دم", "NRC 2012"),
        "بيوتين": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 9200, "حوافر", "NRC 2012"),
        "فوليك أسيد": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 6200, "إخصاب", "NRC 2012"),
    },
    "⚗️ مضافات خاصة": {
        "مضاد حيوي وقائي": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 3800, "حسب التشريعات", "NRC 2012"),
        "مضاد كوكسيديا": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 4200, "للدواجن — ≤0.0125%", "NRC 1994"),
        "مضاد فطريات": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 2800, "حفظ العلف", "NRC 2012"),
        "منشط نمو طبيعي": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 8500, "بديل مضادات", "NRC 2012"),
        "محسن نكهة": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 3800, "استساغة", "NRC 2012"),
        "ملون طبيعي": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 6200, "لون الصفار", "NRC 2012"),
        "بيتاين (Betaine)": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 4800, "إجهاد حراري — ≤0.2%", "NRC 2012"),
        "أحماض عضوية": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 3200, "حفظ", "NRC 2012"),
        "بيتا جلوكان": _feed(10, .5, 20, 5, 3, 1, 5, .1, .15, .3, .1, 12000, "مناعة", "NRC 2012"),
        "طحالب كالبتوس": _feed(8, .6, 25, 10, 6, 2, 35, 2.5, .3, .3, .15, 2500, "معادن نادرة", "FAO 2010"),
    },
}


def _get_ingredient_lookup() -> Dict[str, Dict]:
    """يُنشئ قاموساً مسطحاً لكل المكونات مرة واحدة ويخزنه."""
    if not hasattr(_get_ingredient_lookup, "_cache"):
        lookup = {}
        for cat in BIG_FEEDS_LIBRARY.values():
            for name, data in cat.items():
                lookup[name] = data
        _get_ingredient_lookup._cache = lookup
    return _get_ingredient_lookup._cache


def get_oil_ingredients() -> Dict[str, Dict]:
    """يُعيد فقط الزيوت."""
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت النباتية والحيوانية", {})


def get_total_ingredient_count() -> int:
    """عدد المكونات الكلي."""
    return len(_get_ingredient_lookup())


# ═══════════════════════════════════════════════════════════════════════════
# 🔒 v11.7 — GLOBAL SAFETY LIMITS — الحدود العالمية الصارمة
# ═══════════════════════════════════════════════════════════════════════════
#
# قواعد v11.7:
#   - المركزات: خيار ثنائي فقط (5% أو 10% للدواجن) — لا قيم بينهما
#   - ملح الطعام: ≤ 0.5% (حرج)
#   - اليوريا: ≤ 1.5% للمجترات فقط
#   - البريمكسات: ≤ 0.5%–1%
#   - الأحماض الأمينية: ≤ 0.5%
#   - المرجع: NRC / AAFCO / FAO / Ross 308
# ═══════════════════════════════════════════════════════════════════════════

GLOBAL_SAFETY_LIMITS = {
    # ── المركزات: خيار فقط ──
    "مركزات دواجن": {
        "type": "choice", "options": [5.0, 10.0],
        "source": "AAFCO / NRC 1994",
        "note": "خيار ثنائي: 5% أو 10% فقط — لا يُسمح بقيم بينهما"
    },
    "مركزات مواشي": {
        "type": "choice", "options": [10.0, 20.0, 30.0],
        "source": "NRC 2001",
        "note": "خيارات: 10% / 20% / 30% فقط"
    },

    # ── الأملاح ──
    "ملح الطعام": {
        "type": "range", "min": 0.1, "max": 0.5,
        "source": "NRC 2012", "critical": True,
        "note": "زيادة عن 0.5% تسبب تسمم ملحي"
    },
    "الحجر الجيري": {
        "type": "range", "min": 0, "max": 4.0,
        "source": "NRC 2001"
    },
    "فوسفات ثنائي الكالسيوم": {
        "type": "range", "min": 0, "max": 3.0,
        "source": "NRC 2001"
    },
    "فوسفات أحادي الكالسيوم": {
        "type": "range", "min": 0, "max": 3.0,
        "source": "NRC 2001"
    },
    "بيكربونات الصوديوم": {
        "type": "range", "min": 0, "max": 1.0,
        "source": "NRC 2001"
    },

    # ── اليوريا (خطرة جداً) ──
    "يوريا علفية": {
        "type": "range", "min": 0, "max": 1.5,
        "source": "NRC 2001", "critical": True,
        "note": "زيادة عن 1.5% تسبب تسمم أمونيا — للمجترات فقط"
    },

    # ── البريمكسات ──
    "بريمكس تسمين دواجن": {"type": "max", "max": 1.0, "source": "NRC 1994"},
    "بريمكس بياض": {"type": "max", "max": 1.0, "source": "NRC 1994"},
    "بريمكس أبقار": {"type": "max", "max": 0.5, "source": "NRC 2001"},
    "بريمكس مجترات": {"type": "max", "max": 0.5, "source": "NRC 2007"},
    "بريمكس إبل": {"type": "max", "max": 0.5, "source": "FAO 2010"},
    "بريمكس خيول": {"type": "max", "max": 0.5, "source": "NRC 2007"},
    "بريمكس أسماك": {"type": "max", "max": 1.0, "source": "NRC Fish"},

    # ── المضافات ──
    "مضاد سموم فطرية": {"type": "max", "max": 0.2, "source": "NRC 2012"},
    "مضاد أكسدة BHT": {"type": "max", "max": 0.02, "source": "FAO"},
    "مضاد كوكسيديا": {"type": "max", "max": 0.0125, "source": "NRC 1994"},
    "مضاد حيوي وقائي": {"type": "max", "max": 0.1, "source": "تشريعات محلية"},
    "كولين كلوريد": {"type": "max", "max": 0.3, "source": "NRC 2012"},
    "بيتاين (Betaine)": {"type": "max", "max": 0.2, "source": "NRC 2012"},
    "محسن نكهة": {"type": "max", "max": 0.1, "source": "NRC 2012"},
    "ملون طبيعي": {"type": "max", "max": 0.05, "source": "NRC 2012"},

    # ── الأحماض الأمينية ──
    "ليسين نقي": {"type": "max", "max": 0.5, "source": "NRC 2012"},
    "ليسين سلفات": {"type": "max", "max": 0.6, "source": "NRC 2012"},
    "ميثيونين نقي": {"type": "max", "max": 0.4, "source": "NRC 2012"},
    "ميثيونين هيدروكسي": {"type": "max", "max": 0.3, "source": "NRC 2012"},
    "ثريونين نقي": {"type": "max", "max": 0.3, "source": "NRC 2012"},
    "تريبتوفان نقي": {"type": "max", "max": 0.2, "source": "NRC 2012"},

    # ── السكر والدبس ──
    "سكر مائدة": {"type": "max", "max": 2.0, "source": "NRC 2012"},
    "عسل أسود (دبس)": {"type": "max", "max": 3.0, "source": "NRC 2012"},

    # ── الزيوت/الدهون ──
    "زيت ذرة": {"type": "max", "max": 8.0, "source": "Ross 308"},
    "زيت فول الصويا": {"type": "max", "max": 8.0, "source": "Ross 308"},
    "شحم حيواني (Tallow)": {"type": "max", "max": 8.0, "source": "Ross 308"},
}


def validate_feed_inputs(formula: Dict[str, float]) -> Dict[str, Any]:
    """
    يتحقق من GLOBAL_SAFETY_LIMITS ويقترح تصحيحاً تلقائياً.
    لا يعدّل التركيبة الأصلية — يُرجع نسخة مصححة.

    Returns:
        {
            "ok": bool,
            "errors": [...],
            "warnings": [...],
            "corrected": dict,
            "corrections": [...],
            "critical_hits": [...]
        }
    """
    result = {
        "ok": True,
        "errors": [], "warnings": [],
        "corrected": dict(formula),
        "corrections": [],
        "critical_hits": [],
    }

    # 1) فحص المجموع
    total = sum(formula.values())
    if abs(total - 100) > 0.05:
        result["warnings"].append(
            f"⚠️ مجموع النسب {total:.2f}% ≠ 100% — يجب التعديل")

    # 2) فحص كل مكوّن
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
                    f"{' / '.join(f'{x}%' for x in allowed)} "
                    f"({lim['source']})")
                result["corrections"].append({
                    "ingredient": ing,
                    "from": pct, "to": nearest,
                    "reason": f"خيارات فقط: {allowed}",
                })
                result["corrected"][ing] = nearest

        elif lim["type"] == "max":
            if pct > lim["max"]:
                result["ok"] = False
                result["errors"].append(
                    f"❌ {ing}: {pct:.2f}% > {lim['max']}% "
                    f"({lim['source']})")
                result["corrections"].append({
                    "ingredient": ing,
                    "from": pct, "to": lim["max"],
                    "reason": f"الحد الأقصى {lim['max']}% — {lim['source']}",
                })
                result["corrected"][ing] = lim["max"]
                if lim.get("critical"):
                    result["critical_hits"].append(ing)

        elif lim["type"] == "range":
            if pct > lim["max"]:
                result["ok"] = False
                result["errors"].append(
                    f"❌ {ing}: {pct:.2f}% > {lim['max']}% "
                    f"({lim['source']})")
                result["corrections"].append({
                    "ingredient": ing,
                    "from": pct, "to": lim["max"],
                    "reason": lim.get("note", f"الحد {lim['max']}%"),
                })
                result["corrected"][ing] = lim["max"]
                if lim.get("critical"):
                    result["critical_hits"].append(ing)
            elif pct < lim.get("min", 0):
                result["warnings"].append(
                    f"⚠️ {ing}: {pct:.2f}% < الحد الأدنى "
                    f"({lim['min']}%)")

    # 3) تعويض الفارق على مكوّن حر
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
                "ingredient": target,
                "from": before,
                "to": result["corrected"][target],
                "reason": f"تعويض فرق المجموع ({diff:+.2f}%)",
            })

    return result


# ═══════════════════════════════════════════════════════════════════════════
# 📏 v11.7 — محرك القياسات وتقدير العلف اليومي
# ═══════════════════════════════════════════════════════════════════════════
#
# المعادلات:
#   أبقار/أغنام/ماعز: (محيط الصدر² × طول الجسم) ÷ 10838
#   إبل:              (محيط الصدر² × طول الجسم) ÷ 11000
#   خيول:             (محيط الصدر² × طول الجسم) ÷ 11877
#
# المراجع:
#   - Schaeffer 1971 (cattle)
#   - NRC 2007 (sheep/goats)
#   - FAO 2010 / Kamal 2015 (camels)
#   - Carroll & Huntington 1988 (horses)
# ═══════════════════════════════════════════════════════════════════════════

MEASUREMENT_METHODS = {
    "أبقار": {
        "name_ar": "أبقار",
        "method": "شريط حول الصدر + طول الجسم",
        "measures": [
            {"id": "heart_girth", "label": "محيط الصدر (سم)",
             "hint": "خلف الكتفين مباشرة، شريط أفقي"},
            {"id": "body_length", "label": "طول الجسم (سم)",
             "hint": "من مقدمة الكتف إلى مؤخرة الإلية"},
        ],
        "formula_ar": "(محيط الصدر² × طول الجسم) ÷ 10838",
        "divisor": 10838,
        "source": "Schaeffer 1971 / NRC 2001",
        "dmi_pct": (2.0, 3.0),
        "dmi_source": "NRC Dairy 2001",
    },
    "أغنام": {
        "name_ar": "أغنام",
        "method": "شريط حول الصدر + طول الجسم",
        "measures": [
            {"id": "heart_girth", "label": "محيط الصدر (سم)",
             "hint": "خلف مقدمة الكتف"},
            {"id": "body_length", "label": "طول الجسم (سم)",
             "hint": "من الكتف إلى الإلية"},
        ],
        "formula_ar": "(محيط الصدر² × طول الجسم) ÷ 10838",
        "divisor": 10838,
        "source": "NRC 2007 / Shrestha 2012",
        "dmi_pct": (3.0, 5.0),
        "dmi_source": "NRC Small Ruminants",
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
        "dmi_pct": (3.0, 5.0),
        "dmi_source": "NRC Small Ruminants",
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
        "dmi_pct": (2.0, 3.0),
        "dmi_source": "FAO Camel Nutrition",
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
        "source": "Carroll & Huntington 1988 / NRC Horses",
        "dmi_pct": (2.0, 2.5),
        "dmi_source": "NRC Horses 2007",
    },
}


def estimate_weight_from_tape(animal: str, hg: float, bl: float) -> Dict:
    """تقدير الوزن من قياسات الشريط (محيط الصدر × طول الجسم)."""
    method = MEASUREMENT_METHODS.get(animal)
    if not method or hg <= 0 or bl <= 0:
        return {"success": False, "message": "قياسات غير صحيحة"}

    weight = (hg ** 2 * bl) / method["divisor"]
    return {
        "success": True,
        "weight_kg": round(weight, 1),
        "formula": method["formula_ar"],
        "source": method["source"],
        "inputs": {"heart_girth": hg, "body_length": bl},
    }


def calculate_daily_feed(animal: str, weight_kg: float,
                          stage: str = "صيانة",
                          concentrate_ratio: float = 40.0) -> Dict:
    """
    حساب العلف اليومي بناءً على الوزن والحالة.
    
    DMI = weight × DMI% × stage_factor
    Concentrate = DMI × concentrate_ratio / 100
    Roughage = DMI - Concentrate
    """
    method = MEASUREMENT_METHODS.get(animal)
    if not method or "dmi_pct" not in method:
        return {"success": False,
                "message": f"{animal} — استخدم تبويب الاحتياجات"}

    stage_factor = {
        "صيانة": 1.0, "نمو": 1.15, "تسمين": 1.25,
        "حمل": 1.20, "رضاعة": 1.40, "حليب": 1.30,
        "رياضة": 1.30, "سباق": 1.50,
    }.get(stage, 1.0)

    dmi_low = weight_kg * method["dmi_pct"][0] / 100 * stage_factor
    dmi_high = weight_kg * method["dmi_pct"][1] / 100 * stage_factor
    dmi_mid = (dmi_low + dmi_high) / 2

    conc = dmi_mid * concentrate_ratio / 100
    rough = dmi_mid - conc

    return {
        "success": True,
        "weight_kg": weight_kg,
        "stage": stage,
        "dmi_kg": round(dmi_mid, 2),
        "dmi_range": (round(dmi_low, 2), round(dmi_high, 2)),
        "concentrate_kg": round(conc, 2),
        "roughage_kg": round(rough, 2),
        "concentrate_pct": concentrate_ratio,
        "dmi_pct_bw": f"{method['dmi_pct'][0]}–{method['dmi_pct'][1]}%",
        "source": method["dmi_source"],
        "stage_factor": stage_factor,
    }


print(f"[Tawor Nology {APP_VERSION}] الجزء 2/5 — تم تحميل:")
print(f"  ✅ مكتبة الأعلاف: {get_total_ingredient_count()} مكون")
print(f"  ✅ GLOBAL_SAFETY_LIMITS: {len(GLOBAL_SAFETY_LIMITS)} قاعدة صارمة")
print(f"  ✅ MEASUREMENT_METHODS: {len(MEASUREMENT_METHODS)} حيوان")
print("  ✅ fail-closed + تصحيح تلقائي جاهز")
# ═══════════════════════════════════════════════════════════════════════════
# معايير الزيوت — NRC/Ross/FAO
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
    "خيول_رياضة_مكثف": {"max": 10.0, "optimal": 7.0, "source": "NRC Horses"},
    "خيول_رياضة_عادي": {"max": 8.0, "optimal": 5.0, "source": "NRC Horses"},
    "خيول_نمو_أمهار": {"max": 8.0, "optimal": 5.0, "source": "NRC Horses"},
    "خيول_مرضعات": {"max": 8.0, "optimal": 5.5, "source": "NRC Horses"},
    "خيول_صيانة": {"max": 5.0, "optimal": 3.0, "source": "NRC Horses"},
    "أسماك_بادئ": {"max": 15.0, "optimal": 10.0, "source": "NRC Fish"},
    "أسماك_نمو": {"max": 12.0, "optimal": 8.0, "source": "NRC Fish"},
    "أسماك_تسمين": {"max": 12.0, "optimal": 8.0, "source": "NRC Fish"},
    "أرانب_تسمين": {"max": 4.0, "optimal": 2.5, "source": "NRC 2007"},
    "أرانب_حليب": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
}


def get_oil_standard(k: str) -> Dict[str, Any]:
    """يُعيد معيار الزيوت لمفتاح معين."""
    return MAX_OIL_PERCENTAGE.get(
        k, {"max": 5.0, "optimal": 3.0, "source": "عام"})


# ═══════════════════════════════════════════════════════════════════════════
# الحدود العلمية للمكونات حسب الحيوان
# ═══════════════════════════════════════════════════════════════════════════

INGREDIENT_LIMITS_BY_ANIMAL = {
    "دواجن": {
        "يوريا علفية": (0, 0),
        "سمن حيواني (Lard)": (0, 0),
        "دهن الدجاج": (0, 3),
        "نخالة قمح (ردة)": (0, 10),
        "نخالة ذرة": (0, 5),
        "تبن قمح": (0, 2),
        "قش أرز": (0, 2),
        "سرسة الأرز": (0, 2),
        "كسب بذور القطن": (0, 5),
        "كسب السمسم": (0, 8),
        "كسب الكانولا": (0, 8),
        "ملح الطعام": (.2, .4),
        "الحجر الجيري": (.8, 2),
        "فوسفات ثنائي الكالسيوم": (.5, 2.5),
        "بيكربونات الصوديوم": (0, .5),
        "مضاد سموم فطرية": (.05, .15),
        "بريمكس تسمين دواجن": (.2, .35),
        "بريمكس بياض": (.2, .35),
        "ليسين نقي": (0, .5),
        "ميثيونين نقي": (0, .4),
        "زيت ذرة": (0, 5),
        "زيت فول الصويا": (0, 6),
    },
    "سمان": {
        "يوريا علفية": (0, 0),
        "سمن حيواني (Lard)": (0, 0),
        "نخالة قمح (ردة)": (0, 8),
        "ملح الطعام": (.2, .4),
        "الحجر الجيري": (.8, 2.5),
        "فوسفات ثنائي الكالسيوم": (.5, 2),
        "بريمكس تسمين دواجن": (.2, .35),
        "بريمكس بياض": (.2, .35),
    },
    "أبقار": {
        "يوريا علفية": (0, 1.5),
        "نخالة قمح (ردة)": (0, 30),
        "كسب بذور القطن": (0, 20),
        "كسب السمسم": (0, 15),
        "ملح الطعام": (.3, .5),
        "بيكربونات الصوديوم": (.5, 1),
        "الحجر الجيري": (0, 3.5),
        "فوسفات ثنائي الكالسيوم": (0, 2),
        "بريمكس أبقار": (.15, .3),
        "بريمكس مجترات": (.15, .3),
        "مضاد سموم فطرية": (.05, .15),
    },
    "أغنام": {
        "يوريا علفية": (0, 1),
        "نخالة قمح (ردة)": (0, 25),
        "كسب بذور القطن": (0, 15),
        "ملح الطعام": (.3, .5),
        "بيكربونات الصوديوم": (.5, 1),
        "بريمكس مجترات": (.15, .3),
        "الحجر الجيري": (0, 3),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "ماعز": {
        "يوريا علفية": (0, 1),
        "نخالة قمح (ردة)": (0, 25),
        "ملح الطعام": (.3, .5),
        "بيكربونات الصوديوم": (.5, 1),
        "بريمكس مجترات": (.15, .3),
        "الحجر الجيري": (0, 3),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "إبل": {
        "يوريا علفية": (0, 1),
        "نخالة قمح (ردة)": (0, 20),
        "ملح الطعام": (.3, .5),
        "بيكربونات الصوديوم": (.5, 1),
        "بريمكس إبل": (.15, .3),
        "الحجر الجيري": (0, 3),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "خيول": {
        "يوريا علفية": (0, .5),
        "نخالة قمح (ردة)": (0, 20),
        "ملح الطعام": (.3, .5),
        "بريمكس خيول": (.15, .3),
        "الحجر الجيري": (0, 2.5),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "أسماك": {
        "يوريا علفية": (0, 0),
        "سمن حيواني (Lard)": (0, 0),
        "نخالة قمح (ردة)": (0, 10),
        "ملح الطعام": (0, .3),
        "بريمكس أسماك": (.15, .3),
        "الحجر الجيري": (0, 2),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "أرانب": {
        "يوريا علفية": (0, .5),
        "نخالة قمح (ردة)": (0, 20),
        "ملح الطعام": (.3, .5),
        "بريمكس مجترات": (.15, .3),
        "الحجر الجيري": (0, 2.5),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
}


def get_animal_limits(animal: str) -> Dict[str, Tuple[float, float]]:
    """يُعيد حدود المكونات لحيوان معين."""
    return INGREDIENT_LIMITS_BY_ANIMAL.get(animal, {})


# ═══════════════════════════════════════════════════════════════════════════
# الاحتياجات الغذائية حسب NRC
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AnimalRequirement:
    """بنية احتياجات الحيوان الغذائية."""
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
    """احتياجات الأبقار حسب NRC 2001."""
    if t == "حليب_عالي":
        dp = 12.5 + milk_yield * .30
        return AnimalRequirement(
            round(dp, 2), round(dp / .70, 2),
            round(60 + milk_yield * .35, 1), 30, 19, 5.5, 8,
            round(.55 + milk_yield * .003, 3),
            round(.33 + milk_yield * .0015, 3),
            "أبقار حلابة عالية", f"حليب {milk_yield} كجم")
    if t == "حليب_متوسط":
        dp = 11 + milk_yield * .25
        return AnimalRequirement(
            round(dp, 2), round(dp / .72, 2),
            round(55 + milk_yield * .3, 1), 33, 21, 4.5, 8,
            round(.5 + milk_yield * .0025, 3),
            round(.3 + milk_yield * .0012, 3),
            "أبقار حلابة متوسطة", f"حليب {milk_yield} كجم")
    if t == "حليب_منخفض":
        dp = 9.5 + milk_yield * .2
        return AnimalRequirement(
            round(dp, 2), round(dp / .75, 2),
            round(50 + milk_yield * .25, 1), 38, 24, 4, 8.5,
            round(.45 + milk_yield * .002, 3),
            round(.28 + milk_yield * .001, 3),
            "أبقار حلابة منخفضة", f"حليب {milk_yield} كجم")
    if t == "تسمين_مكثف":
        return AnimalRequirement(11.5, 14.5, 72, 32, 20, 4.5, 7.5,
                                   .65, .38, "تسمين عجول مكثف", "ADG >1.3")
    if t == "تسمين_عادي":
        return AnimalRequirement(9.5, 12, 65, 38, 24, 4, 7.5,
                                   .55, .32, "تسمين عجول عادي", "ADG ~0.8")
    if t == "حمل_أخير":
        return AnimalRequirement(11.5, 14.5, 67, 35, 22, 4.2, 8,
                                   .7, .42, "حمل آخر", "شهر 7-9")
    return AnimalRequirement(7.5, 10, 53, 45, 28, 3, 8.5, .42, .26,
                              "أبقار صيانة", "بدون إنتاج")


def get_sheep_requirements(t: str, is_male: bool = True,
                            weight_kg: float = 50.0,
                            litter_size: int = 1) -> AnimalRequirement:
    """احتياجات الأغنام حسب NRC 2007."""
    if is_male:
        if t == "تسمين_مكثف":
            return AnimalRequirement(11.5, 14.5, 64, 28, 17, 4, 8,
                                       .65, .36, "تسمين مكثف", "ADG >250")
        if t == "تسمين_عادي":
            return AnimalRequirement(9.5, 12, 59, 33, 21, 3.6, 8,
                                       .55, .32, "تسمين عادي", "ADG ~180")
        return AnimalRequirement(8.5, 11, 55, 38, 24, 3.2, 8.5,
                                   .5, .3, "حملان تيد", "بداية")
    if t == "مرضعات":
        dp = 10.5 + (litter_size - 1) * 1.5
        return AnimalRequirement(
            round(dp, 2), round(dp / .72, 2),
            round(60 + (litter_size - 1) * 5, 1), 30, 19, 4.5, 8.5,
            round(.65 + (litter_size - 1) * .1, 3),
            round(.38 + (litter_size - 1) * .05, 3),
            f"نعاج مرضعات ({litter_size} مولود)", "")
    if t == "حامل_أخير":
        return AnimalRequirement(10.5, 13.5, 62, 32, 20, 3.8, 8,
                                   .6, .35, "نعاج حامل (4-5)", "")
    if t == "حامل_متوسط":
        return AnimalRequirement(8.5, 11, 55, 38, 24, 3.4, 8,
                                   .5, .3, "نعاج حامل (1-3)", "")
    return AnimalRequirement(7.2, 9.5, 48, 45, 28, 3, 8.5,
                               .42, .26, "نعاج صيانة", "")


def get_goat_requirements(t: str, is_male: bool = True,
                            milk_yield: float = 2.0) -> AnimalRequirement:
    """احتياجات الماعز حسب NRC 2007."""
    if is_male:
        if t == "تسمين_جديان":
            return AnimalRequirement(11, 14, 62, 30, 19, 3.8, 8,
                                       .62, .34, "تسمين جديان", "")
        return AnimalRequirement(9, 11.5, 57, 36, 22, 3.5, 8,
                                   .55, .3, "تيوس تسمين", "")
    if t == "حلابة_عالي":
        dp = 11.5 + milk_yield * .45
        return AnimalRequirement(
            round(dp, 2), round(dp / .7, 2),
            round(58 + milk_yield * .45, 1), 29, 18, 4.5, 8.5,
            round(.6 + milk_yield * .008, 3),
            round(.35 + milk_yield * .004, 3),
            f"عنزات حلابة ({milk_yield} لتر)", "")
    if t == "حلابة_متوسط":
        dp = 10 + milk_yield * .35
        return AnimalRequirement(
            round(dp, 2), round(dp / .72, 2),
            round(55 + milk_yield * .4, 1), 32, 20, 4, 8.5,
            round(.55 + milk_yield * .006, 3),
            round(.32 + milk_yield * .003, 3),
            f"عنزات حلابة ({milk_yield} لتر)", "")
    if t == "حامل_أخير":
        return AnimalRequirement(10, 13, 60, 33, 21, 3.8, 8,
                                   .6, .35, "عنزات حامل", "")
    return AnimalRequirement(6.8, 9, 46, 46, 28, 3, 8.5,
                               .42, .26, "عنزات صيانة", "")


def get_camel_requirements(t: str, weight_kg: float = 400.0,
                             milk_yield: float = 5.0) -> AnimalRequirement:
    """احتياجات الإبل حسب FAO 2010."""
    if t == "نمو":
        return AnimalRequirement(10.5, 13.5, 60, 38, 24, 4, 8,
                                   .65, .38, "إبل نمو", f"{weight_kg} كجم")
    if t == "تسمين":
        return AnimalRequirement(9.5, 12, 65, 35, 22, 4.5, 7.5,
                                   .6, .35, "إبل تسمين", f"{weight_kg} كجم")
    if t == "حليب":
        dp = 12 + milk_yield * .25
        return AnimalRequirement(
            round(dp, 2), round(dp / .7, 2),
            round(62 + milk_yield * .4, 1), 32, 20, 5, 8.5,
            round(.7 + milk_yield * .006, 3),
            round(.4 + milk_yield * .003, 3),
            f"إبل حلابة ({milk_yield} لتر)", "")
    if t == "سباق":
        return AnimalRequirement(14, 17, 72, 28, 17, 6, 9,
                                   .85, .5, "إبل سباق", "طاقة عالية")
    return AnimalRequirement(7, 9, 48, 48, 30, 3.5, 9,
                               .42, .26, "إبل صيانة", f"{weight_kg} كجم")


def get_horse_requirements(t: str,
                             weight_kg: float = 450.0) -> AnimalRequirement:
    """احتياجات الخيول حسب NRC 2007."""
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


def get_poultry_requirements(strain: str,
                                age_weeks: int = 1) -> AnimalRequirement:
    """احتياجات الدواجن حسب Ross 308 / NRC 1994."""
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


def get_quail_requirements(strain: str,
                              age_weeks: int = 1) -> AnimalRequirement:
    """احتياجات السمان حسب NRC Quail."""
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


def get_fish_requirements(species: str,
                            stage: str) -> AnimalRequirement:
    """احتياجات الأسماك حسب NRC Fish."""
    if "بادئ" in stage or "زريعة" in stage:
        return AnimalRequirement(32, 40, 72, 8, 4, 10, 11,
                                   1.5, .9, f"{species} بادئ", "")
    if "نمو" in stage:
        return AnimalRequirement(25, 32, 70, 12, 6, 8, 9,
                                   1, .7, f"{species} نمو", "")
    return AnimalRequirement(22, 28, 68, 13, 7, 8, 9.5,
                               .9, .65, f"{species} تسمين", "")


def get_rabbit_requirements(t: str,
                              weight_kg: float = 4.0) -> AnimalRequirement:
    """احتياجات الأرانب حسب NRC 2007."""
    if t == "تسمين":
        return AnimalRequirement(15, 17, 65, 25, 15, 3, 8,
                                   .7, .35, "أرانب تسمين", "ADG 40")
    if t == "حليب":
        return AnimalRequirement(18, 20, 68, 25, 15, 4, 8.5,
                                   .85, .45, "أرانب حلابة", "أمهات")
    return AnimalRequirement(12, 14, 60, 30, 20, 2.5, 8.5,
                               .6, .3, "أرانب صيانة", "")


def requirement_to_standard(req: AnimalRequirement) -> Dict[str, float]:
    """يحوّل AnimalRequirement إلى قاموس للمحرك."""
    return {
        "CP": req.CP, "DP": req.DP, "SE": req.SE,
        "NDF": req.NDF, "ADF": req.ADF, "EE": req.EE,
        "ASH": req.ASH, "Ca": req.Ca, "P": req.P
    }


# ═══════════════════════════════════════════════════════════════════════════
# الحسابات والتقييم
# ═══════════════════════════════════════════════════════════════════════════

def compute_formula_nutrients(formula: Dict[str, float]) -> Dict[str, float]:
    """يحسب مجموع العناصر الغذائية لتركيبة معينة."""
    totals = {k: 0.0 for k in
              ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH",
               "Ca", "P", "Lys", "Met"]}
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
    """يحسب مجموع نسبة الزيوت في التركيبة."""
    oils = set(get_oil_ingredients().keys())
    return sum(p for i, p in formula.items() if i in oils)


def evaluate_difference(pct_diff: float,
                         standard_value: Optional[float] = None) -> Dict:
    """تقييم الانحراف كنسبة مئوية."""
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


def get_overall_rating(rows: List[Dict]) -> Dict:
    """يحسب التقييم العام من صفوف التقييم."""
    if not rows:
        return {"label": "غير محدد", "color": "#666", "score": 0}
    avg = sum(r.get("score", 50) for r in rows) / len(rows)
    if avg >= 95:
        return {"label": "🏆 ممتازة", "color": "#1b5e20", "score": avg}
    if avg >= 85:
        return {"label": "🌟 جيدة جداً", "color": "#2e7d32", "score": avg}
    if avg >= 70:
        return {"label": "✅ جيدة", "color": "#558b2f", "score": avg}
    if avg >= 55:
        return {"label": "⭐ مقبولة", "color": "#f9a825", "score": avg}
    return {"label": "⚠️ تحتاج تحسين", "color": "#e65100", "score": avg}


def evaluate_quality_weighted(formula: Dict[str, float],
                                targets: Dict[str, float],
                                animal_type: str,
                                basis: str = "DP") -> Tuple[float, Dict]:
    """تقييم مرجّح للجودة — يشمل Ca:P."""
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
            if 1.5 <= r <= 2.2:
                rs = 100
            elif 1.3 <= r < 1.5 or 2.2 < r <= 2.5:
                rs = 80
            elif 1.0 <= r < 1.3 or 2.5 < r <= 3.5:
                rs = 50
            else:
                rs = 10
        else:
            if 1.5 <= r <= 2.0:
                rs = 100
            elif 1.2 <= r < 1.5 or 2.0 < r <= 2.5:
                rs = 85
            elif 0.9 <= r < 1.2 or 2.5 < r <= 3.5:
                rs = 55
            else:
                rs = 15
        weighted += rs * 0.10
        total_w += 0.10

    return (weighted / total_w if total_w else 0.0), actual


def get_default_selections(animal_type: str, production_type: str,
                             requirement: Optional[AnimalRequirement] = None) -> Set[str]:
    """يُعيد المكونات الافتراضية المختارة حسب الحيوان."""
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
    elif animal_type == "خيول":
        d.add("بريمكس خيول")
    elif animal_type == "إبل":
        d.add("بريمكس إبل")
    elif animal_type == "أسماك":
        d.add("بريمكس أسماك")

    if "بياض" in str(production_type):
        d.add("الحجر الجيري")

    return d


def _normalize_ingredient_name(name: str) -> str:
    """تطبيع أسماء المكونات من OCR أو الإدخال اليدوي."""
    name = re.sub(r'\s+', ' ', str(name).strip())
    lookup = _get_ingredient_lookup()

    if name in lookup:
        return name

    for lib in lookup.keys():
        if lib.lower() in name.lower() or name.lower() in lib.lower():
            return lib

    kw = {
        "ذره": "ذرة صفراء", "ذرة": "ذرة صفراء",
        "صويا": "كسب فول صويا 44%",
        "شعير": "شعير مطحون", "قمح": "قمح محلي",
        "نخاله": "نخالة قمح (ردة)", "نخالة": "نخالة قمح (ردة)",
        "ملح": "ملح الطعام", "حجر": "الحجر الجيري",
        "فوسفات": "فوسفات ثنائي الكالسيوم",
        "يوريا": "يوريا علفية",
    }
    for k, v in kw.items():
        if k in name.lower():
            return v
    return name


# ═══════════════════════════════════════════════════════════════════════════
# محرك البرمجة الخطية LP — 5 استراتيجيات
# ═══════════════════════════════════════════════════════════════════════════

def auto_formulate_smart(available_ingredients: List[str],
                           prices: Dict[str, float],
                           custom_standard: Dict[str, float],
                           standard_key: str = "",
                           basis: str = "DP",
                           min_quality: float = 70.0,
                           animal_type: str = "",
                           production_type: str = "") -> Dict:
    """محرك التركيب الأساسي — 5 استراتيجيات متتالية."""
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

    strategies = [
        ("دقيق", "eq"), ("مرن ±5%", "r05"), ("مرن ±10%", "r10"),
        ("مرن ±15%", "r15"), ("طوارئ", "none"),
    ]

    best, best_q = None, 0.0

    for label, mode in strategies:
        try:
            A_eq, b_eq = list(A_eq_base), list(b_eq_base)
            A_ub, b_ub = list(A_ub_base), list(b_ub_base)

            if mode == "eq":
                if target_ca > 0:
                    A_eq.append(rows["Ca"])
                    b_eq.append(target_ca * 100.0)
                if target_p > 0:
                    A_eq.append(rows["P"])
                    b_eq.append(target_p * 100.0)
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
                          bounds=bounds, method='highs',
                          options={'presolve': True, 'time_limit': 10})

            if res.success:
                formula = {valid[i]: res.x[i] for i in range(n)
                           if res.x[i] > 0.001}
                q, actual = evaluate_quality_weighted(
                    formula, custom_standard, animal_type, basis)

                if q > best_q:
                    best_q = q
                    best = {
                        "success": True,
                        "formula": formula,
                        "cost": res.fun / 100.0,
                        "actual_nutrients": actual,
                        "quality_score": q,
                        "strategy": label,
                        "meets_standard": q >= min_quality,
                        "targets": custom_standard,
                        "basis": basis,
                        "oil_std": oil_std,
                        "total_oil": compute_total_oil_percentage(formula),
                    }

                if q >= 92:
                    break
        except Exception:
            continue

    if best:
        if not best["meets_standard"]:
            best["warning"] = (
                f"⚠️ الجودة {best_q:.1f}% < {min_quality}% — "
                f"أضف مصادر طاقة/بروتين/أملاح")
        return best

    return {"success": False, "message": "تعذر إيجاد حل — جرّب مواد أكثر"}


def compute_sensitivity(formula: Dict[str, float],
                         targets: Dict[str, float],
                         animal_type: str) -> Dict[str, Dict]:
    """تحليل الحساسية: يقيس أثر زيادة ±5% على المكوّن المؤثر الرئيسي."""
    base_q, _ = evaluate_quality_weighted(formula, targets, animal_type)
    base = compute_formula_nutrients(formula)
    deviations = {}

    lookup = _get_ingredient_lookup()

    for nut in ("CP", "DP", "SE", "Ca", "P"):
        if not targets.get(nut):
            continue

        best_ing = max(
            formula.keys(),
            key=lambda i: formula[i] * lookup.get(i, {}).get(nut, 0),
            default=None)

        if not best_ing:
            continue

        modified = dict(formula)
        modified[best_ing] = min(100.0, modified[best_ing] * 1.05)
        total = sum(modified.values())

        if total > 100:
            for k in modified:
                modified[k] *= 100.0 / total

        new_q, new_nut = evaluate_quality_weighted(
            modified, targets, animal_type)

        deviations[nut] = {
            "delta_quality": round(new_q - base_q, 2),
            "delta_value": round(new_nut.get(nut, 0) - base.get(nut, 0), 3),
            "driver_ingredient": best_ing,
        }

    return deviations


# ═══════════════════════════════════════════════════════════════════════════
# بدائل الحليب — Standards & Ingredients
# ═══════════════════════════════════════════════════════════════════════════

MILK_REPLACER_STANDARDS = {
    "عجول (Calves)": {
        "CP": 24, "Fat": 20, "Lactose": 45, "Ca": .85,
        "P": .7, "Lys": 2.2, "Met": .65,
        "notes": "NRC 2001 — عمر 1-6 أسابيع",
        "source": "NRC Dairy Cattle",
        "Ca_P_optimal": (1.2, 1.5),
    },
    "حملان (Lambs)": {
        "CP": 24, "Fat": 24, "Lactose": 40, "Ca": .9,
        "P": .7, "Lys": 2.4, "Met": .7,
        "notes": "≥24% دهن ضروري",
        "source": "NRC Small Ruminants",
        "Ca_P_optimal": (1.2, 1.6),
    },
    "جديان (Goat Kids)": {
        "CP": 24, "Fat": 24, "Lactose": 42, "Ca": .9,
        "P": .7, "Lys": 2.3, "Met": .7,
        "notes": "توازن خاص للجديان",
        "source": "NRC Small Ruminants",
        "Ca_P_optimal": (1.2, 1.6),
    },
    "إبل (Camels)": {
        "CP": 26, "Fat": 28, "Lactose": 38, "Ca": .95,
        "P": .75, "Lys": 2.5, "Met": .8,
        "notes": "بروتين ودهن أعلى",
        "source": "FAO Camel Nutrition",
        "Ca_P_optimal": (1.2, 1.5),
    },
    "أمهار (Foals)": {
        "CP": 22, "Fat": 18, "Lactose": 48, "Ca": 1.0,
        "P": .8, "Lys": 2.1, "Met": .6,
        "notes": "توازن خاص للخيل",
        "source": "NRC Horses",
        "Ca_P_optimal": (1.2, 1.4),
    },
    "جراء (Puppies)": {
        "CP": 28, "Fat": 22, "Lactose": 35, "Ca": 1.1,
        "P": .9, "Lys": 2.2, "Met": .7,
        "notes": "AAFCO compliant",
        "source": "AAFCO 2020",
        "Ca_P_optimal": (1.2, 1.3),
    },
}


MILK_REPLACER_INGREDIENTS = {
    "حليب مجفف منزوع الدسم": {
        "CP": 34, "Fat": 1, "Lactose": 52, "Ca": 1.3, "P": 1,
        "Lys": 2.7, "Met": .9, "price": 3200, "max": 60, "type": "بروتين",
    },
    "حليب مجفف كامل الدسم": {
        "CP": 26, "Fat": 28, "Lactose": 38, "Ca": .95, "P": .75,
        "Lys": 2.1, "Met": .65, "price": 3800, "max": 70,
        "type": "بروتين+دهن",
    },
    "شرش حليب مجفف": {
        "CP": 12, "Fat": 1.5, "Lactose": 75, "Ca": .9, "P": .75,
        "Lys": .9, "Met": .2, "price": 1800, "max": 35,
        "type": "كربوهيدرات",
    },
    "بروتين شرش WPC 80%": {
        "CP": 80, "Fat": 5, "Lactose": 8, "Ca": .5, "P": .3,
        "Lys": 7.5, "Met": 1.6, "price": 8500, "max": 25,
        "type": "بروتين",
    },
    "كازين": {
        "CP": 85, "Fat": 2, "Lactose": 2, "Ca": .1, "P": .5,
        "Lys": 7, "Met": 2.5, "price": 9000, "max": 20,
        "type": "بروتين",
    },
    "مركز بروتين صويا": {
        "CP": 66, "Fat": 1, "Lactose": 0, "Ca": .2, "P": .8,
        "Lys": 4.2, "Met": .9, "price": 2800, "max": 15,
        "type": "نباتي",
    },
    "دقيق الصويا": {
        "CP": 38, "Fat": 20, "Lactose": 0, "Ca": .2, "P": .6,
        "Lys": 2.4, "Met": .55, "price": 1500, "max": 10,
        "type": "نباتي",
    },
    "زيت جوز الهند": {
        "CP": 0, "Fat": 100, "Lactose": 0, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 0, "price": 2200, "max": 15,
        "type": "دهن",
    },
    "زيت النخيل": {
        "CP": 0, "Fat": 100, "Lactose": 0, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 0, "price": 1200, "max": 15,
        "type": "دهن",
    },
    "دهن حيواني": {
        "CP": 0, "Fat": 100, "Lactose": 0, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 0, "price": 1000, "max": 15,
        "type": "دهن",
    },
    "مالتودكسترين": {
        "CP": 0, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 0, "price": 900, "max": 10,
        "type": "كربوهيدرات",
    },
    "لاكتوز نقي": {
        "CP": 0, "Fat": 0, "Lactose": 100, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 0, "price": 1400, "max": 25,
        "type": "كربوهيدرات",
    },
    "ليسين L-Lysine": {
        "CP": 94, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0,
        "Lys": 94, "Met": 0, "price": 4200, "max": 1,
        "type": "أميني",
    },
    "ميثيونين": {
        "CP": 58, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 58, "price": 5800, "max": .8,
        "type": "أميني",
    },
    "بريمكس فيتامينات": {
        "CP": 0, "Fat": 0, "Lactose": 0, "Ca": 5, "P": 3,
        "Lys": 0, "Met": 0, "price": 6500, "max": 1,
        "type": "بريمكس",
    },
    "كالسيوم كربونات": {
        "CP": 0, "Fat": 0, "Lactose": 0, "Ca": 38, "P": 0,
        "Lys": 0, "Met": 0, "price": 200, "max": 2.5,
        "type": "معدن",
    },
    "فوسفات ثنائي الكالسيوم": {
        "CP": 0, "Fat": 0, "Lactose": 0, "Ca": 23, "P": 18,
        "Lys": 0, "Met": 0, "price": 1100, "max": 2.5,
        "type": "معدن",
    },
    "ملح طعام": {
        "CP": 0, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0,
        "Lys": 0, "Met": 0, "price": 150, "max": .5,
        "type": "معدن",
    },
}


def formulate_milk_replacer(animal: str, volume: float = 100.0,
                              selected: Optional[List[str]] = None) -> Dict:
    """محرك مرن لبدائل الحليب — 6 استراتيجيات علمية."""
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "SCIPY غير متوفرة"}

    std = MILK_REPLACER_STANDARDS.get(animal)
    if not std:
        return {"success": False, "message": "حيوان غير مدعوم"}

    valid = [i for i in (selected or list(MILK_REPLACER_INGREDIENTS.keys()))
             if i in MILK_REPLACER_INGREDIENTS]
    n = len(valid)

    if n < 3:
        return {"success": False,
                "message": "اختر 3 مكونات على الأقل (4 مفضّلة علمياً)"}

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

    strategies = []

    s1_ub = [
        (lac, std["Lactose"] * 1.15 * 100),
        ([-x for x in lac], -std["Lactose"] * 0.85 * 100),
        ([-x for x in lys], -std["Lys"] * 0.70 * 100),
        ([-x for x in met], -std["Met"] * 0.70 * 100),
        ([-x for x in ca], -std["Ca"] * 0.85 * 100),
        ([-x for x in p], -std["P"] * 0.85 * 100),
    ]
    strategies.append((
        "S1: صارم — CP + Fat + كل القيود",
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
    strategies.append((
        "S2: مرن — Lactose واسع",
        [[1]*n, cp, fat],
        [100, std["CP"]*100, std["Fat"]*100],
        [u for u, _ in s2_ub],
        [b for _, b in s2_ub]))

    s3_ub = s1_ub[:2] + s1_ub[4:]
    strategies.append((
        "S3: CP+Fat — بدون Lys/Met",
        [[1]*n, cp, fat],
        [100, std["CP"]*100, std["Fat"]*100],
        [u for u, _ in s3_ub],
        [b for _, b in s3_ub]))

    s4_ub = s1_ub[:2]
    strategies.append((
        "S4: CP+Fat — بدون معادن",
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
    strategies.append((
        "S5: CP/Fat ±5% (تخفيف)",
        [[1]*n], [100],
        [u for u, _ in s5_ub],
        [b for _, b in s5_ub]))

    s6_ub = [
        (cp, std["CP"] * 1.15 * 100),
        ([-x for x in cp], -std["CP"] * 0.85 * 100),
        (fat, std["Fat"] * 1.30 * 100),
        ([-x for x in fat], -std["Fat"] * 0.50 * 100),
    ]
    strategies.append((
        "S6: CP/Fat ±15% (طوارئ قصوى)",
        [[1]*n], [100],
        [u for u, _ in s6_ub],
        [b for _, b in s6_ub]))

    best = None
    best_effective = 0.0

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
                if t <= 0:
                    continue
                diff = abs(actual[k] - t) / t * 100
                if diff <= 2:
                    scores.append(100)
                elif diff <= 5:
                    scores.append(92)
                elif diff <= 10:
                    scores.append(78)
                elif diff <= 15:
                    scores.append(62)
                elif diff <= 25:
                    scores.append(45)
                else:
                    scores.append(max(0, 100 - diff))

            ca_p = actual["Ca"] / actual["P"] if actual["P"] > 0 else 0
            cp_min, cp_max = std.get("Ca_P_optimal", (1.2, 1.5))

            if cp_min <= ca_p <= cp_max:
                scores.append(100)
            elif cp_min * 0.8 <= ca_p <= cp_max * 1.3:
                scores.append(75)
            else:
                scores.append(30)

            quality = sum(scores) / len(scores) if scores else 0

            util_factor = (1.0 if used_pct >= min_util*100
                           else used_pct / (min_util*100))
            effective = quality * (0.7 + 0.3 * util_factor)

            if effective > best_effective:
                best_effective = effective
                best = {
                    "formula": formula,
                    "cost": res.fun / 100,
                    "cost_per_kg": res.fun / 10000,
                    "used_count": used,
                    "used_pct": used_pct,
                    "actual": actual,
                    "quality_score": quality,
                    "ca_p_ratio": ca_p,
                    "strategy": label,
                }

            if quality >= 90 and used_pct >= min_util * 100:
                break
        except Exception:
            continue

    if not best:
        return {"success": False,
                "message": "لا يوجد حل — جرّب مواد أرخص أو أكثر"}

    warning = None
    if best["used_pct"] < min_util * 100:
        warning = (f"⚠️ تم استخدام {best['used_count']}/{n} مادة "
                   f"({best['used_pct']:.0f}% < {min_util*100:.0f}%) "
                   f"— أضف مادة أو حرّر السعر")

    return {
        "success": True,
        "formula": best["formula"],
        "cost_per_100kg": best["cost"],
        "cost_per_kg": best["cost_per_kg"],
        "standard": std,
        "actual": best["actual"],
        "animal": animal,
        "volume": volume,
        "used_count": best["used_count"],
        "used_pct": best["used_pct"],
        "quality_score": best["quality_score"],
        "ca_p_ratio": best["ca_p_ratio"],
        "strategy": best["strategy"],
        "warning": warning,
        "targets": {k: std.get(k, 0) for k in
                    ["CP", "Fat", "Lactose", "Ca", "P", "Lys", "Met"]},
    }


# ═══════════════════════════════════════════════════════════════════════════
# OCR
# ═══════════════════════════════════════════════════════════════════════════

def _preprocess_image_variants(img):
    """يولّد 8 أشكال معالجة للصورة لتحسين OCR."""
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
    variants.append(cv2.fastNlMeansDenoising(clahe.apply(gray), None, 10, 7, 21))

    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    variants.append(cv2.filter2D(gray, -1, kernel))

    variants.append(cv2.bitwise_not(gray))
    variants.append(cv2.morphologyEx(gray, cv2.MORPH_CLOSE,
                                     np.ones((2, 2), np.uint8)))
    return variants


def _deskew_image(img):
    """تصحيح ميلان الصورة."""
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)
        coords = np.column_stack(np.where(gray > 0))
        if len(coords) < 100:
            return img
        angle = cv2.minAreaRect(coords)[-1]
        angle = -(90 + angle) if angle < -45 else -angle
        if abs(angle) > 15 or abs(angle) < 0.5:
            return img
        (h, w) = img.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_REPLICATE)
    except Exception:
        return img


def _extract_with_confidence(image):
    """يستخرج النص مع درجات الثقة."""
    try:
        data = pytesseract.image_to_data(
            image, lang='ara+eng',
            output_type=pytesseract.Output.DICT,
            config=r'--oem 3 --psm 6')

        good_lines = []
        current_line = []
        current_y = None

        for i, word in enumerate(data['text']):
            if int(data['conf'][i]) < 30:
                continue
            word = word.strip()
            if not word:
                continue
            y = data['top'][i]
            if current_y is None:
                current_y = y
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
    """يحلل النص لاستخراج المكونات ونسبها."""
    fixes = {
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٪': '%', ' I ': ' 1 ', ' l ': ' 1 ', '|': '1',
        'O%': '0%', 'S%': '5%', 'B%': '8%',
    }
    text = full_text
    for old, new in fixes.items():
        text = text.replace(old, new)

    patterns = [
        r'([\u0600-\u06FFa-zA-Z\s\(\)\-]{3,40}?)[\s:\-=:\.]+\s*(\d{1,3}\.?\d{0,2})\s*%',
        r'(\d{1,3}\.?\d{0,2})\s*%[\s:\-=:\.]+\s*([\u0600-\u06FFa-zA-Z\s\(\)\-]{3,40})',
        r'([\u0600-\u06FFa-zA-Z\s]{3,30}?)[\s:\-=]+\s*(\d{1,4})\s*(?:كجم|كج|kg)',
        r'^\s*([\u0600-\u06FFa-zA-Z\s]{3,30}?)[\s:\-=]+\s*(\d{1,3}\.?\d{0,2})\s*$',
    ]

    ingredients = {}
    for line in text.split('\n'):
        line = line.strip()
        if len(line) < 4:
            continue
        for pat in patterns:
            for m in re.finditer(pat, line, re.MULTILINE):
                try:
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
                except Exception:
                    continue
    return ingredients


def match_ingredient_name(text):
    """يطابق اسم مادة OCR مع المكتبة."""
    if not text:
        return None
    tl = text.strip().lower()

    for cat in BIG_FEEDS_LIBRARY.values():
        for name in cat.keys():
            if name.lower() in tl or tl in name.lower():
                return name

    kw = {
        "ذرة": "ذرة صفراء", "ذره": "ذرة صفراء",
        "corn": "ذرة صفراء", "maize": "ذرة صفراء",
        "صويا": "كسب فول صويا 44%", "soy": "كسب فول صويا 44%",
        "شعير": "شعير مطحون", "barley": "شعير مطحون",
        "قمح": "قمح محلي", "wheat": "قمح محلي",
        "نخالة": "نخالة قمح (ردة)", "نخاله": "نخالة قمح (ردة)",
        "bran": "نخالة قمح (ردة)", "قطن": "كسب بذور القطن",
        "cotton": "كسب بذور القطن", "عباد": "كسب عباد الشمس 36%",
        "sunflower": "كسب عباد الشمس 36%", "سمك": "مسحوق أسماك 60%",
        "fish": "مسحوق أسماك 60%", "ليسين": "ليسين نقي",
        "lysine": "ليسين نقي", "ميثيونين": "ميثيونين نقي",
        "methionine": "ميثيونين نقي", "ملح": "ملح الطعام",
        "salt": "ملح الطعام", "حجر": "الحجر الجيري",
        "limestone": "الحجر الجيري",
        "فوسفات": "فوسفات ثنائي الكالسيوم",
        "يوريا": "يوريا علفية", "urea": "يوريا علفية",
        "بريمكس": "بريمكس تسمين دواجن",
        "premix": "بريمكس تسمين دواجن",
        "برسيم": "البرسيم الجاف", "alfalfa": "البرسيم الجاف",
        "تبن": "تبن قمح", "straw": "تبن قمح",
    }
    for k, m in kw.items():
        if k in tl:
            return m
    return None


def extract_ingredients_from_image(image_bytes):
    """يستخرج المكونات من صورة — 96 محاولة."""
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
            return {"success": False,
                    "message": "لم يتم استخراج نص — جرّب صورة أوضح"}

        full_text = "\n".join(set(all_texts))
        ingredients = _parse_ingredients_from_text(full_text)

        return {
            "success": True,
            "ingredients": ingredients,
            "raw_text": full_text,
            "best_text": best_text,
            "count": len(ingredients),
            "total": sum(ingredients.values()),
            "quality": "جيد" if best_score > 3 else "ضعيف — تحقق يدوياً",
            "variants_tried": len(variants) * len(langs) * len(psm_modes),
        }
    except Exception as e:
        return {"success": False, "message": f"خطأ: {e}"}


def render_ocr_correction_ui(ingredients):
    """واجهة تصحيح المكونات المستخرجة من OCR."""
    st.markdown("### ✏️ تصحيح يدوي")
    st.caption("راجع المكونات والنسب — عدّل أو أضف")
    corrected = {}
    all_names = list(_get_ingredient_lookup().keys())

    if ingredients:
        for i, (name, pct) in enumerate(list(ingredients.items())):
            ca, cb, cc = st.columns([0.5, 0.3, 0.2])
            with ca:
                idx = all_names.index(name) if name in all_names else 0
                new_name = st.selectbox(f"المادة {i+1}", options=all_names,
                                          index=idx, key=f"ocr_fix_name_{i}")
            with cb:
                new_pct = st.number_input("النسبة %", 0.0, 100.0,
                                            float(pct), 0.5,
                                            key=f"ocr_fix_pct_{i}")
            with cc:
                keep = st.checkbox("احتفظ", value=True, key=f"ocr_keep_{i}")

            if keep and new_pct > 0:
                corrected[new_name] = new_pct

    with st.expander("➕ إضافة مكون"):
        cols = st.columns([0.5, 0.3, 0.2])
        with cols[0]:
            extra_name = st.selectbox("المادة:", options=["—"] + all_names,
                                        key="ocr_extra_name")
        with cols[1]:
            extra_pct = st.number_input("النسبة %", 0.0, 100.0, 0.0, 0.5,
                                          key="ocr_extra_pct")
        if extra_name != "—" and extra_pct > 0:
            corrected[extra_name] = extra_pct

    total = sum(corrected.values())
    if total > 0:
        st.info(f"📊 الإجمالي: {total:.2f}% | المكونات: {len(corrected)}")
    return corrected


# ═══════════════════════════════════════════════════════════════════════════
# الرسوم البيانية — 12 رسم
# ═══════════════════════════════════════════════════════════════════════════

def create_colorful_bar_chart(standard: Dict, actual: Dict,
                                keys: Optional[List[str]] = None):
    """رسم أعمدة مزدوج: معيار vs محسوب."""
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

        b1 = ax.bar(x - width/2, [standard[n] for n in nuts], width,
                     label='المعيار', color='#1976d2',
                     edgecolor='#0d47a1', linewidth=1.5)
        b2 = ax.bar(x + width/2, [actual.get(n, 0) for n in nuts], width,
                     label='المحسوب', color='#43a047',
                     edgecolor='#1b5e20', linewidth=1.5)

        for bar in b1:
            hh = bar.get_height()
            if hh > 0:
                ax.text(bar.get_x() + bar.get_width()/2, hh, f'{hh:.1f}',
                        ha='center', va='bottom', fontsize=9,
                        color='#0d47a1', fontweight='bold')
        for bar in b2:
            hh = bar.get_height()
            if hh > 0:
                ax.text(bar.get_x() + bar.get_width()/2, hh, f'{hh:.1f}',
                        ha='center', va='bottom', fontsize=9,
                        color='#1b5e20', fontweight='bold')

        ax.set_xlabel('العنصر', fontsize=11, fontweight='bold')
        ax.set_ylabel('القيمة', fontsize=11, fontweight='bold')
        ax.set_title('مقارنة العناصر', fontsize=13, fontweight='bold',
                     color='#1b5e20')
        ax.set_xticks(x)
        ax.set_xticklabels(nuts, fontsize=10)
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


def create_colorful_pie_chart(formula: Dict[str, float]):
    """رسم دائري لتوزيع المكونات."""
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2:
        return None
    try:
        colors = ['#e53935', '#8e24aa', '#3949ab', '#1e88e5', '#00897b',
                  '#43a047', '#7cb342', '#fdd835', '#fb8c00', '#6d4c41']
        names = list(formula.keys())
        vals = list(formula.values())

        fig, ax = plt.subplots(figsize=(8, 5))
        _, _, autotexts = ax.pie(
            vals, autopct='%1.1f%%', colors=colors[:len(names)],
            startangle=90, pctdistance=0.75,
            wedgeprops=dict(edgecolor='white', linewidth=2))

        for t in autotexts:
            t.set_color('white')
            t.set_fontweight('bold')
            t.set_fontsize(9)

        ax.legend(names, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
                  fontsize=9)
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


def create_radar_chart(standard: Dict, actual: Dict,
                        keys: Optional[List[str]] = None):
    """رسم رادار للمقارنة."""
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        if keys is None:
            keys = ["CP", "DP", "SE", "NDF", "ADF", "EE", "Ca", "P"]
        nuts = [n for n in keys if n in standard and standard[n] > 0]
        if len(nuts) < 3:
            return None

        std_norm = [100.0] * len(nuts)
        act_norm = [(actual.get(n, 0) / standard[n]) * 100 for n in nuts]

        angles = np.linspace(0, 2 * np.pi, len(nuts), endpoint=False).tolist()
        std_norm += std_norm[:1]
        act_norm += act_norm[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, std_norm, 'o-', linewidth=2.5, color='#1976d2',
                label='المعيار 100%')
        ax.fill(angles, std_norm, alpha=0.15, color='#1976d2')
        ax.plot(angles, act_norm, 'o-', linewidth=2.5, color='#43a047',
                label='المحسوب')
        ax.fill(angles, act_norm, alpha=0.25, color='#43a047')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(nuts, fontsize=10)
        ax.set_ylim(0, max(max(std_norm), max(act_norm)) * 1.2)
        ax.set_title('المقارنة %', fontsize=12, fontweight='bold',
                     color='#1b5e20', pad=20)
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


def create_gauge_chart(score: float):
    """رسم عدّاد دائري للجودة."""
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect='equal'))
        colors = ['#c62828', '#ef6c00', '#f9a825',
                  '#7cb342', '#43a047', '#1b5e20']

        for i, c in enumerate(colors):
            t1 = 180 - (i * 30)
            t2 = 180 - ((i + 1) * 30)
            ax.add_patch(Wedge((0, 0), 1, t2, t1, width=0.3,
                                facecolor=c, edgecolor='white', linewidth=2))

        angle = 180 - (score / 100) * 180
        rad = np.radians(angle)
        ax.plot([0, 0.85 * np.cos(rad)], [0, 0.85 * np.sin(rad)],
                color='#1a1a1a', linewidth=3, zorder=10)
        ax.add_patch(Circle((0, 0), 0.08, color='#1a1a1a', zorder=11))
        ax.text(0, -0.25, f'{score:.0f}%', ha='center', fontsize=20,
                fontweight='bold', color='#1b5e20')
        ax.text(0, -0.5, 'التقييم', ha='center', fontsize=11, color='#666')
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.7, 1.2)
        ax.axis('off')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_horizontal_bar_chart(formula: Dict[str, float]):
    """رسم أعمدة أفقي للمكونات."""
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2:
        return None
    try:
        sorted_pairs = sorted(formula.items(), key=lambda x: x[1], reverse=True)
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
        ax.set_facecolor('#fafafa')
        ax.invert_yaxis()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_nutrient_breakdown_pie(actual: Dict):
    """رسم دائري لمصادر الطاقة."""
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        pc = actual.get("CP", 0) * 4
        fc = actual.get("EE", 0) * 9
        fibc = (actual.get("NDF", 0) + actual.get("ADF", 0)) * 2
        oc = max(0, 100 - pc - fc - fibc)

        labels = ['بروتين', 'دهن', 'ألياف', 'كربوهيدرات']
        sizes = [pc, fc, fibc, oc]
        colors = ['#1976d2', '#f9a825', '#43a047', '#8e24aa']

        fig, ax = plt.subplots(figsize=(7, 5))
        _, _, autotexts = ax.pie(
            sizes, labels=labels, autopct='%1.1f%%', colors=colors,
            startangle=90, wedgeprops=dict(edgecolor='white', linewidth=2))

        for t in autotexts:
            t.set_color('white')
            t.set_fontweight('bold')

        ax.set_title('مصادر الطاقة', fontsize=13, fontweight='bold',
                     color='#1b5e20')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_oil_comparison_chart(total_oil: float, oil_std: Dict):
    """رسم مقارنة الزيوت."""
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        fig, ax = plt.subplots(figsize=(8, 4))
        cats = ['الفعلية', 'المثالي', 'الحد الأقصى']
        vals = [total_oil, oil_std['optimal'], oil_std['max']]
        colors = ['#43a047', '#1976d2', '#c62828']

        if total_oil > oil_std['max']:
            colors[0] = '#c62828'
        elif total_oil > oil_std['optimal'] * 1.2:
            colors[0] = '#f9a825'

        bars = ax.bar(cats, vals, color=colors, edgecolor='#333', linewidth=1.5)
        for bar in bars:
            hh = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, hh + 0.2, f'{hh:.2f}%',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

        ax.set_ylabel('النسبة %', fontsize=11, fontweight='bold')
        ax.set_title(f'الزيوت — {oil_std.get("source", "NRC")}',
                     fontsize=13, fontweight='bold', color='#1b5e20')
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


def create_quality_breakdown_chart(rows: List[Dict]):
    """رسم تقييم كل عنصر."""
    if not MATPLOTLIB_AVAILABLE or not rows:
        return None
    try:
        labels = [r["العنصر"] for r in rows[:9]]
        scores = [r.get("score", 50) for r in rows[:9]]

        colors = []
        for s in scores:
            if s >= 95:
                colors.append('#1b5e20')
            elif s >= 85:
                colors.append('#43a047')
            elif s >= 70:
                colors.append('#7cb342')
            elif s >= 55:
                colors.append('#f9a825')
            else:
                colors.append('#c62828')

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
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_ca_p_ratio_chart(ca: float, p: float,
                              target_ca: float = 0,
                              target_p: float = 0):
    """رسم مقياس Ca:P بمناطق ملونة."""
    if not MATPLOTLIB_AVAILABLE or p <= 0:
        return None
    try:
        ratio = ca / p
        fig, ax = plt.subplots(figsize=(8, 3))

        zones = [
            (0, .8, '#b71c1c'), (.8, 1.2, '#ef6c00'),
            (1.2, 1.5, '#f9a825'), (1.5, 2.0, '#2e7d32'),
            (2.0, 3.0, '#f9a825'), (3.0, 5.0, '#ef6c00'),
            (5.0, 8.0, '#b71c1c'),
        ]

        for x0, x1, c in zones:
            ax.axvspan(x0, x1, alpha=0.35, color=c,
                       edgecolor='white', linewidth=0)

        ratio_clipped = min(ratio, 7.9)
        ax.axvline(ratio_clipped, color='#0d47a1', linewidth=4, zorder=10)
        ax.scatter([ratio_clipped], [0.5], s=350, color='#0d47a1',
                    zorder=11, edgecolors='white', linewidth=3)
        ax.text(ratio_clipped, 0.85, f'{ratio:.2f}', ha='center',
                va='bottom', fontsize=18, fontweight='bold', color='#0d47a1',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                          edgecolor='#0d47a1', linewidth=2))

        ax.set_xlim(0, 8)
        ax.set_ylim(0, 1.2)
        ax.set_yticks([])
        ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8])
        ax.set_xlabel('نسبة Ca : P', fontsize=12, fontweight='bold')
        ax.set_title(f'⚖️ Ca:P — Ca={ca:.2f}% | P={p:.2f}%',
                     fontsize=12, fontweight='bold', color='#1b5e20', pad=15)

        if 1.5 <= ratio <= 2.0:
            label, color = '✅ مثالية', '#1b5e20'
        elif 1.2 <= ratio < 1.5 or 2.0 < ratio <= 3.0:
            label, color = '⚠️ مقبولة', '#f57c00'
        elif 0.8 <= ratio < 1.2 or 3.0 < ratio <= 5.0:
            label, color = '🟠 خارج', '#e65100'
        else:
            label, color = '❌ خطرة', '#c62828'

        ax.text(0.02, 0.05, label, transform=ax.transAxes,
                fontsize=13, fontweight='bold', color=color,
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                          edgecolor=color, linewidth=2))

        ax.grid(axis='x', alpha=0.2, linestyle=':')
        ax.set_facecolor('#fafafa')
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=130, bbox_inches='tight',
                    facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_cost_breakdown_chart(formula: Dict, prices: Dict):
    """رسم تكلفة كل مكوّن."""
    if not MATPLOTLIB_AVAILABLE or not formula:
        return None
    try:
        costs = []
        names = []
        for ing, pct in formula.items():
            price = prices.get(ing, 300)
            cost = pct * price / 100
            if cost > 0:
                costs.append(cost)
                names.append(ing)

        if not costs:
            return None

        fig, ax = plt.subplots(figsize=(9, 4))
        bars = ax.barh(names, costs, color='#43a047', edgecolor='#1b5e20')
        for bar in bars:
            hh = bar.get_width()
            ax.text(hh + 0.5, bar.get_y() + bar.get_height()/2,
                    f'${hh:.2f}', ha='left', va='center', fontsize=9,
                    fontweight='bold')

        ax.set_xlabel('التكلفة ($/طن)', fontsize=11, fontweight='bold')
        ax.set_title('تكلفة كل مكوّن', fontsize=13, fontweight='bold',
                     color='#1b5e20')
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.set_facecolor('#fafafa')
        ax.invert_yaxis()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_amino_acids_chart(actual: Dict, targets: Dict):
    """رسم مقارنة الأحماض الأمينية."""
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        aas = ["Lys", "Met"]
        vals_actual = [actual.get("Lys", 0), actual.get("Met", 0)]
        vals_target = [targets.get("Lys", 0), targets.get("Met", 0)]

        if sum(vals_target) == 0:
            return None

        fig, ax = plt.subplots(figsize=(7, 4))
        x = np.arange(len(aas))
        width = 0.35

        ax.bar(x - width/2, vals_target, width, label='المعيار',
                color='#1976d2', edgecolor='#0d47a1')
        ax.bar(x + width/2, vals_actual, width, label='المحسوب',
                color='#43a047', edgecolor='#1b5e20')

        ax.set_xticks(x)
        ax.set_xticklabels(aas)
        ax.set_ylabel('النسبة %', fontsize=11, fontweight='bold')
        ax.set_title('الأحماض الأمينية الأساسية',
                     fontsize=13, fontweight='bold', color='#1b5e20')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_sensitivity_chart(sens_data: Dict):
    """رسم تحليل الحساسية."""
    if not MATPLOTLIB_AVAILABLE or not sens_data:
        return None
    try:
        labels = list(sens_data.keys())
        dq = [sens_data[k]["delta_quality"] for k in labels]

        fig, ax = plt.subplots(figsize=(8, 4))
        colors = ['#43a047' if v >= 0 else '#c62828' for v in dq]
        bars = ax.bar(labels, dq, color=colors, edgecolor='#333')

        for bar in bars:
            hh = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, hh,
                    f'{hh:+.2f}%', ha='center',
                    va='bottom' if hh >= 0 else 'top',
                    fontsize=10, fontweight='bold')

        ax.axhline(y=0, color='#666', linewidth=1)
        ax.set_ylabel('Δ الجودة %', fontsize=11, fontweight='bold')
        ax.set_title('تحليل الحساسية (+5% لكل عنصر)',
                     fontsize=13, fontweight='bold', color='#1b5e20')
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# مولّد PDF الرئيسي
# ═══════════════════════════════════════════════════════════════════════════

class PDFGenerator:
    """مولّد تقارير PDF شامل بختم وتوقيع."""

    def __init__(self):
        self.font_name = font_mgr.font_name
        self.logo_path = None
        for lp in LOGO_OPTIONS + PHOTO_OPTIONS:
            if os.path.exists(lp):
                self.logo_path = lp
                break

    def _ar(self, t):
        if t is None:
            return ""
        try:
            return get_display(arabic_reshaper.reshape(str(t)), base_dir='R')
        except Exception:
            return str(t)

    def _draw_stamp(self, canvas_obj, doc):
        """ختم دائري بعلامة المنصة."""
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
            for ang in [-45, 45, 135, 225]:
                rad = np.radians(ang)
                canvas_obj.line(
                    sx + 58*np.cos(rad), sy + 58*np.sin(rad),
                    sx + 72*np.cos(rad), sy + 72*np.sin(rad))

            canvas_obj.setFillColor(HexColor('#c62828'))
            canvas_obj.setFont(self.font_name, 9.5)
            canvas_obj.drawCentredString(sx, sy + 42, self._ar("تاور نولجي"))
            canvas_obj.drawCentredString(sx, sy + 30, self._ar("Tawor Nology"))

            canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(sx, sy + 16, self._ar("د. عبدالقادر"))
            canvas_obj.drawCentredString(sx, sy + 4, self._ar("إسماعيل تاور"))

            canvas_obj.setFont(self.font_name, 6.5)
            canvas_obj.drawCentredString(sx, sy - 12, self._ar("اختصاصي تغذية"))
            canvas_obj.drawCentredString(sx, sy - 24, self._ar("معتمد رسمياً"))
            canvas_obj.drawCentredString(sx, sy - 36, self._ar("© 2026"))
        except Exception:
            pass

    def _draw_page(self, canvas_obj, doc):
        """رسم ديباجة وتذييل الصفحة."""
        try:
            canvas_obj.saveState()
            w, h = doc.pagesize

            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, h - 90, w, 90, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.rect(0, h - 95, w, 5, fill=1, stroke=0)

            try:
                if self.logo_path:
                    canvas_obj.drawImage(
                        self.logo_path, 30, h - 78, width=60, height=60,
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
                w/2, h - 58, self._ar("للإنتاج الحيواني وتغذية الحيوان"))

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
            canvas_obj.drawCentredString(w/2, 68, self._ar(f"🤲 {DUA_SHORT} 🤲"))

            canvas_obj.setFillColor(HexColor('#c8e6c9'))
            canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(
                w/2, 52, self._ar("اللهم اجعل قبرهما روضة من رياض الجنة"))

            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)

            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(
                w/2, 27, self._ar("تاور نولجي Tawor Nology © 2026"))

            canvas_obj.setFont(self.font_name, 7)
            canvas_obj.drawCentredString(
                w/2, 12,
                self._ar(f"صفحة {canvas_obj.getPageNumber()} | جميع الحقوق محفوظة"))

            try:
                if QRCODE_AVAILABLE:
                    qr = qrcode.QRCode(version=1, box_size=3, border=1)
                    qr.add_data(PLATFORM_URL)
                    qr.make(fit=True)
                    qi = qr.make_image(fill_color="#1b5e20", back_color="white")
                    qbuf = io.BytesIO()
                    qi.save(qbuf, format="PNG")
                    qbuf.seek(0)
                    canvas_obj.drawImage(RLImage(qbuf), w/2 - 20, 46,
                                          width=40, height=40)
            except Exception:
                pass

            self._draw_stamp(canvas_obj, doc)
            canvas_obj.restoreState()
        except Exception:
            pass

    def _comparison_table(self, std: Dict, calc: Dict):
        """يبني جدول مقارنة ملون."""
        labels = {
            "CP": "بروتين CP", "DP": "مهضوم DP", "SE": "SE",
            "NDF": "NDF", "ADF": "ADF", "EE": "دهن", "ASH": "رماد",
            "Ca": "Ca", "P": "P",
        }
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
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ]

        row = 1
        for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
            if k not in std or std[k] == 0:
                continue
            sv, cv = std[k], calc.get(k, 0)
            diff = cv - sv
            pct = (diff / sv * 100) if sv else 0
            ev = evaluate_difference(pct, standard_value=sv)
            data.append([
                self._ar(labels[k]),
                f"{sv:.2f}",
                f"{cv:.2f}",
                f"{diff:+.3f}",
                f"{pct:+.2f}%",
                self._ar(ev["label"]),
            ])
            cmds.append(('BACKGROUND', (0, row), (-1, row),
                          HexColor(ev["bg"])))
            row += 1

        t = Table(data, colWidths=[100, 70, 70, 70, 70, 105])
        t.setStyle(TableStyle(cmds))
        return t

    def generate_report(self, formula, requirement, animal_type, breed, cost,
                        city, local_cost, local_sym, requester_name="",
                        protein_basis="DP", standard_key="",
                        include_charts=True, quality_score=0.0):
        """تقرير تركيب العلفة الكامل."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
                                leftMargin=40, topMargin=115, bottomMargin=145)
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
            [self._ar("🐾 الفصيل:"), self._ar(f"{animal_type} — {breed}")],
            [self._ar("🧬 الأساس:"), self._ar(protein_basis)],
            [self._ar("📅 التاريخ:"), datetime.now().strftime('%Y-%m-%d')],
        ]
        ct = Table(client, colWidths=[150, 340])
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

        std_vals = requirement_to_standard(requirement)
        calc_vals = compute_formula_nutrients(formula)

        qd = [
            [self._ar("الجودة"), self._ar("الحالة"), self._ar("70%")],
            [f"{quality_score:.1f}%",
             self._ar("✅ ناجح" if quality_score >= 70 else "⚠️ يحتاج تحسين"),
             self._ar("✅" if quality_score >= 70 else "❌")],
        ]
        qt = Table(qd, colWidths=[130, 200, 160])
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

        story.append(P("📊 مقارنة العناصر", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        story.append(self._comparison_table(std_vals, calc_vals))
        story.append(Spacer(1, 15))

        sens = compute_sensitivity(formula, std_vals, animal_type)
        if sens:
            story.append(PageBreak())
            story.append(P("📐 تحليل الحساسية", size=14, color='#1565c0'))
            story.append(Spacer(1, 8))
            sens_data = [[self._ar(x) for x in
                          ["العنصر", "المكوّن المؤثر", "Δالجودة", "Δالقيمة"]]]
            for k, v in sens.items():
                sens_data.append([
                    self._ar(k),
                    self._ar(v["driver_ingredient"]),
                    f"{v['delta_quality']:+.2f}%",
                    f"{v['delta_value']:+.3f}",
                ])
            ts = Table(sens_data, colWidths=[80, 200, 100, 100])
            ts.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565c0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('GRID', (0, 0), (-1, -1), 0.6, HexColor('#bdbdbd')),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            story.append(ts)

        if include_charts:
            story.append(PageBreak())
            story.append(P("📈 الرسوم البيانية", size=14, color='#1b5e20'))
            story.append(Spacer(1, 10))
            for chart_fn, args in [
                (create_colorful_bar_chart, (std_vals, calc_vals)),
                (create_colorful_pie_chart, (formula,)),
                (create_radar_chart, (std_vals, calc_vals)),
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
            try:
                cap = create_ca_p_ratio_chart(
                    calc_vals.get("Ca", 0), calc_vals.get("P", 0))
                if cap:
                    story.append(P("⚖️ Ca:P", size=12, align=TA_CENTER,
                                   color='#1b5e20'))
                    story.append(RLImage(cap, width=450, height=170))
            except Exception:
                pass

        story.append(PageBreak())
        story.append(P("💰 التكاليف", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        cost_data = [
            [self._ar("البند"), self._ar("القيمة")],
            [self._ar("التكلفة/طن"), f"${cost:.2f}"],
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
            ing_data = [[self._ar("المكون"), self._ar("%"),
                         self._ar("كجم/طن")]]
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
            ]))
            story.append(ti)
            story.append(Spacer(1, 25))

            sign = [
                [self._ar("توقيع الطالب"), self._ar("توقيع المختص")],
                [self._ar("...................."), self._ar(SUPERVISOR)],
                [self._ar("التاريخ: ..../..../......"),
                 self._ar(SUPERVISOR_TITLE)],
            ]
            ts = Table(sign, colWidths=[245, 245])
            ts.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOX', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#e0e0e0')),
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f5e9')),
            ]))
            story.append(ts)

        doc.build(story, onFirstPage=self._draw_page,
                  onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_ocr_report(self, ingredients: Dict, nutrients: Dict,
                              raw_text: str = ""):
        """تقرير OCR."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
                                leftMargin=40, topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text), ParagraphStyle(
                's', fontName=self.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))

        story.append(P("تقرير تحليل OCR", size=20, align=TA_CENTER,
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
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#ffe0b2')),
        ]))
        story.append(t)
        story.append(Spacer(1, 18))

        nut_data = [[self._ar("العنصر"), self._ar("القيمة")]]
        for k, label in [("CP", "بروتين"), ("DP", "مهضوم"), ("SE", "SE"),
                          ("NDF", "NDF"), ("ADF", "ADF"), ("EE", "دهن"),
                          ("Ca", "Ca"), ("P", "P")]:
            nut_data.append([self._ar(label),
                              f"{nutrients.get(k, 0):.2f}"])
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
        story.append(P(SUPERVISOR, size=16, align=TA_CENTER,
                       color='#c62828'))
        story.append(P(SUPERVISOR_TITLE, size=11, align=TA_CENTER,
                       color='#1b5e20'))

        doc.build(story, onFirstPage=self._draw_page,
                  onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()


pdf_gen = PDFGenerator()


# ═══════════════════════════════════════════════════════════════════════════
# 📄 v11.7 — PDF تقرير العلف اليومي
# ═══════════════════════════════════════════════════════════════════════════

def generate_measurement_pdf(feed: Dict) -> Optional[bytes]:
    """PDF لتقرير العلف اليومي."""
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4, rightMargin=40, leftMargin=40,
            topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(ar(text), ParagraphStyle(
                's', fontName=font_mgr.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))

        story.append(P("تقرير العلف اليومي", size=20,
                       align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
                                color=HexColor('#d4af37')))
        story.append(Spacer(1, 15))

        rows = [[ar("البند"), ar("القيمة")]]
        for label, val in [
            ("الوزن", f"{feed['weight_kg']} كجم"),
            ("الحالة", feed['stage']),
            ("المادة الجافة (DMI)", f"{feed['dmi_kg']} كجم/يوم"),
            ("النطاق", f"{feed['dmi_range'][0]}–{feed['dmi_range'][1]} كجم"),
            ("المركزات", f"{feed['concentrate_kg']} كجم "
                          f"({feed['concentrate_pct']}%)"),
            ("الأعلاف الخشنة", f"{feed['roughage_kg']} كجم"),
            ("نسبة الوزن", feed['dmi_pct_bw']),
            ("عامل الحالة", f"×{feed['stage_factor']}"),
            ("المرجع", feed['source']),
        ]:
            rows.append([ar(label), ar(val)])

        t = Table(rows, colWidths=[200, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        story.append(P(SUPERVISOR, size=14, align=TA_CENTER,
                       color='#c62828'))
        story.append(P(SUPERVISOR_TITLE, size=10, align=TA_CENTER,
                       color='#1b5e20'))

        doc.build(story, onFirstPage=pdf_gen._draw_page,
                  onLaterPages=pdf_gen._draw_page)
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# 📄 v11.7 — PDF تقرير التحقق من الحدود العالمية
# ═══════════════════════════════════════════════════════════════════════════

def generate_validation_pdf_report(validation: Dict,
                                     formula: Dict) -> Optional[bytes]:
    """تقرير التحقق من الحدود القياسية + التصحيحات."""
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4, rightMargin=40, leftMargin=40,
            topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(ar(text), ParagraphStyle(
                's', fontName=font_mgr.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))

        story.append(P("تقرير التحقق من الحدود القياسية",
                        size=20, align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
                                color=HexColor('#d4af37')))
        story.append(Spacer(1, 15))

        lim_rows = [[ar(x) for x in
                     ["المكوّن", "الفعلية %", "الحد القياسي",
                      "المرجع", "الحالة"]]]
        for ing, pct in formula.items():
            lim = GLOBAL_SAFETY_LIMITS.get(ing)
            if not lim:
                lim_rows.append([ar(ing), f"{pct:.2f}%",
                                  "—", "—", "—"])
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
            lim_rows.append([
                ar(ing), f"{pct:.2f}%", allowed,
                ar(lim["source"]),
                "✅" if ok else "❌"])

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
            story.append(P("🔧 التصحيحات التلقائية",
                            size=14, color='#c62828'))
            story.append(Spacer(1, 8))
            corr_rows = [[ar(x) for x in
                          ["المكوّن", "قبل", "بعد", "السبب"]]]
            for c in validation["corrections"]:
                corr_rows.append([
                    ar(c["ingredient"]),
                    f"{c['from']:.2f}%",
                    f"{c['to']:.2f}%",
                    ar(c["reason"])])
            tc = Table(corr_rows, colWidths=[90, 60, 60, 240])
            tc.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0),
                  HexColor('#c62828')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('GRID', (0, 0), (-1, -1), 0.6,
                  HexColor('#e0e0e0')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1),
                  font_mgr.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('PADDING', (0, 0), (-1, -1), 6)]))
            story.append(tc)

        doc.build(story, onFirstPage=pdf_gen._draw_page,
                  onLaterPages=pdf_gen._draw_page)
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# PDF بدائل الحليب
# ═══════════════════════════════════════════════════════════════════════════

def generate_milk_replacer_pdf(result: Dict) -> Optional[bytes]:
    """PDF شامل لبدائل الحليب."""
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
                                leftMargin=40, topMargin=115, bottomMargin=145)
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

        story.append(P("تقرير تركيبة بديل الحليب", size=20,
                       align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
                                color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))

        info = [
            [ar("الحيوان:"), ar(result["animal"])],
            [ar("المرجع:"), ar(std.get("source", ""))],
            [ar("التاريخ:"), datetime.now().strftime('%Y-%m-%d %H:%M')],
            [ar("المكونات المستخدمة:"), f"{result['used_count']}"],
            [ar("الاستراتيجية:"), ar(result.get("strategy", "—"))],
            [ar("الكمية المطلوبة:"), f"{volume:.0f} كجم"],
        ]
        ct = Table(info, colWidths=[160, 330])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e3f2fd')),
            ('BACKGROUND', (1, 0), (1, -1), HexColor('#fafafa')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#1565c0')),
            ('INNERGRID', (0, 0), (-1, -1), 0.6, HexColor('#bbdefb')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 7),
        ]))
        story.append(ct)
        story.append(Spacer(1, 12))

        qd = [[ar("الجودة"), ar("الحالة"), ar("Ca:P"), ar("الاستخدام")],
              [f"{quality:.1f}%",
               ar("✅ ناجح" if quality >= 70 else "⚠️ يحتاج تحسين"),
               f"{result['ca_p_ratio']:.2f}",
               f"{result['used_pct']:.0f}%"]]
        qt = Table(qd, colWidths=[110, 155, 110, 115])
        qt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565c0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('BACKGROUND', (0, 1), (-1, -1),
             HexColor('#e8f5e9' if quality >= 70 else '#ffebee')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#1976d2')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(qt)
        story.append(Spacer(1, 15))

        story.append(P("📊 جدول المقارنة التفصيلي", size=14,
                       color='#1b5e20'))
        story.append(Spacer(1, 8))

        labels = {"CP": "بروتين CP", "Fat": "دهن Fat",
                  "Lactose": "لاكتوز", "Ca": "Ca", "P": "P",
                  "Lys": "Lys", "Met": "Met"}

        comp_data = [[ar(x) for x in
                      ["العنصر", "المعيار", "المحسوب", "الفرق",
                       "% الانحراف", "التقييم"]]]
        cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#9e9e9e')),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ]
        row_idx = 1
        quality_rows = []
        for k, lab in labels.items():
            t = targets.get(k, 0)
            a = actual.get(k, 0)
            if t <= 0:
                continue
            diff = a - t
            pct = (diff / t * 100) if t else 0
            ev = evaluate_difference(pct, standard_value=t)
            comp_data.append([
                ar(lab), f"{t:.2f}", f"{a:.2f}", f"{diff:+.3f}",
                f"{pct:+.2f}%", ar(ev["label"])])
            cmds.append(('BACKGROUND', (0, row_idx), (-1, row_idx),
                          HexColor(ev["bg"])))
            quality_rows.append({"العنصر": lab, "score": ev["score"]})
            row_idx += 1

        cp_min, cp_max = std.get("Ca_P_optimal", (1.2, 1.5))
        ca_p = result["ca_p_ratio"]
        if cp_min <= ca_p <= cp_max:
            cp_ev = {"label": "🎯 مثالية", "bg": "#c8e6c9", "score": 100}
        elif cp_min * 0.8 <= ca_p <= cp_max * 1.3:
            cp_ev = {"label": "✅ جيدة", "bg": "#dcedc8", "score": 85}
        else:
            cp_ev = {"label": "⚠️ خارج النطاق", "bg": "#fff3e0", "score": 50}
        comp_data.append([ar("Ca:P"), f"{cp_min:.1f}–{cp_max:.1f}",
                          f"{ca_p:.2f}", "—", "—", ar(cp_ev["label"])])
        cmds.append(('BACKGROUND', (0, row_idx), (-1, row_idx),
                      HexColor(cp_ev["bg"])))
        quality_rows.append({"العنصر": "Ca:P", "score": cp_ev["score"]})

        comp_table = Table(comp_data, colWidths=[90, 75, 75, 75, 85, 90])
        comp_table.setStyle(TableStyle(cmds))
        story.append(comp_table)
        story.append(Spacer(1, 15))

        story.append(P("🍼 المكونات التفصيلية", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))

        ing_data = [[ar(x) for x in
                     ["المكون", "%", f"كجم /{volume:.0f}",
                      "السعر $/كجم", "التكلفة $"]]]
        for ing, pct in formula.items():
            price = MILK_REPLACER_INGREDIENTS[ing]["price"]
            kg = pct * volume / 100
            line_cost = kg * price / 1000
            ing_data.append([
                ar(ing), f"{pct:.2f}%", f"{kg:.2f}",
                f"${price:.0f}", f"${line_cost:.2f}"])
        total_cost = result['cost_per_100kg'] * volume / 100
        ing_data.append([ar("الإجمالي"), "100%",
                         f"{volume:.0f}", "—", f"${total_cost:.2f}"])

        ing_table = Table(ing_data, colWidths=[170, 65, 85, 85, 85])
        ing_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2),
             [HexColor('#ffffff'), HexColor('#f5f5f5')]),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#ffe082')),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
        ]))
        story.append(ing_table)
        story.append(Spacer(1, 12))

        if result.get("warning"):
            warn_data = [[ar("⚠️ ملاحظة"), ar(result["warning"])]]
            wt = Table(warn_data, colWidths=[90, 400])
            wt.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#fff3e0')),
                ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#e65100')),
                ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(wt)

        story.append(PageBreak())
        story.append(P("📈 الرسوم البيانية", size=14, color='#1b5e20'))
        story.append(Spacer(1, 10))

        keys_milk = ["CP", "Fat", "Lactose", "Ca", "P", "Lys", "Met"]

        try:
            bf = create_colorful_bar_chart(targets, actual, keys=keys_milk)
            if bf:
                story.append(RLImage(bf, width=460, height=250))
                story.append(Spacer(1, 8))
        except Exception:
            pass

        try:
            pf = create_colorful_pie_chart(formula)
            if pf:
                story.append(RLImage(pf, width=380, height=220))
                story.append(Spacer(1, 8))
        except Exception:
            pass

        story.append(PageBreak())

        try:
            rf = create_radar_chart(targets, actual, keys=keys_milk)
            if rf:
                story.append(RLImage(rf, width=320, height=320))
                story.append(Spacer(1, 8))
        except Exception:
            pass

        try:
            gf = create_gauge_chart(quality)
            if gf:
                story.append(RLImage(gf, width=200, height=200))
                story.append(Spacer(1, 8))
        except Exception:
            pass

        try:
            cf = create_ca_p_ratio_chart(
                actual.get("Ca", 0), actual.get("P", 0))
            if cf:
                story.append(RLImage(cf, width=440, height=170))
                story.append(Spacer(1, 8))
        except Exception:
            pass

        try:
            qf = create_quality_breakdown_chart(quality_rows)
            if qf:
                story.append(RLImage(qf, width=460, height=200))
        except Exception:
            pass

        story.append(Spacer(1, 20))
        story.append(P(SUPERVISOR, size=16, align=TA_CENTER,
                       color='#c62828'))
        story.append(P(SUPERVISOR_TITLE, size=11, align=TA_CENTER,
                       color='#1b5e20'))

        doc.build(story, onFirstPage=pdf_gen._draw_page,
                  onLaterPages=pdf_gen._draw_page)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# PDF الفواتير والديباجة
# ═══════════════════════════════════════════════════════════════════════════

def generate_invoice_pdf(inv: Dict) -> Optional[bytes]:
    """فاتورة ضريبية رسمية."""
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40,
                                leftMargin=40, topMargin=115, bottomMargin=145)
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

        info = [
            [ar("رقم الفاتورة:"), ar(inv["number"])],
            [ar("التاريخ:"), ar(inv["date"])],
            [ar("العميل:"), ar(inv["client"])],
            [ar("الهاتف:"), ar(inv.get("phone", "—"))],
        ]
        t = Table(info, colWidths=[150, 340])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')),
            ('INNERGRID', (0, 0), (-1, -1), 0.6, HexColor('#c8e6c9')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

        headers = [ar("البند"), ar("الكمية"), ar("السعر"), ar("الإجمالي")]
        rows = [headers]
        for it in inv["items"]:
            line_total = it["الكمية (طن)"] * it["سعر الطن"]
            rows.append([
                ar(str(it["البند"])),
                f"{it['الكمية (طن)']:.2f}",
                f"${it['سعر الطن']:,.2f}",
                f"${line_total:,.2f}",
            ])
        rows.append([ar("المجموع"), "", "", f"${inv['subtotal']:,.2f}"])
        if inv["tax"] > 0:
            rows.append([ar(f"ضريبة {inv['tax']}%"), "", "",
                          f"${inv['tax_amt']:,.2f}"])
        rows.append([ar("الإجمالي النهائي"), "", "",
                      f"${inv['total']:,.2f}"])

        ti = Table(rows, colWidths=[220, 80, 90, 100])
        ti.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#bdbdbd')),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#ffeb3b')),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
        ]))
        story.append(ti)
        story.append(Spacer(1, 30))
        story.append(P(SUPERVISOR, size=14, align=TA_CENTER,
                       color='#c62828'))
        story.append(P(SUPERVISOR_TITLE, size=10, align=TA_CENTER,
                       color='#1b5e20'))
        doc.build(story, onFirstPage=pdf_gen._draw_page,
                  onLaterPages=pdf_gen._draw_page)
        return buf.getvalue()
    except Exception:
        return None


def generate_letterhead_pdf(title_line: str, sub_line: str) -> Optional[bytes]:
    """ديباجة رسمية فارغة."""
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=50,
                                leftMargin=50, topMargin=115, bottomMargin=145)
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
                                 color=HexColor('#d4af37'), hAlign='CENTER'))
        story.append(Spacer(1, 40))
        story.append(Paragraph(ar(SUPERVISOR), ParagraphStyle(
            'n', fontName=font_mgr.font_name, fontSize=22,
            alignment=TA_CENTER, textColor=HexColor('#c62828'))))
        story.append(Paragraph(ar(SUPERVISOR_TITLE), ParagraphStyle(
            'r', fontName=font_mgr.font_name, fontSize=13,
            alignment=TA_CENTER, textColor=HexColor('#0d47a1'))))
        story.append(Spacer(1, 60))
        story.append(Paragraph(ar(f"📅 {datetime.now():%Y-%m-%d}"),
            ParagraphStyle('d', fontName=font_mgr.font_name,
                           fontSize=11, alignment=TA_CENTER)))
        story.append(Spacer(1, 30))
        story.append(Paragraph(ar(f"🤲 {DUA_FULL} 🤲"),
            ParagraphStyle('du', fontName=font_mgr.font_name,
                           fontSize=12, alignment=TA_CENTER,
                           textColor=HexColor('#c62828'))))

        doc.build(story, onFirstPage=pdf_gen._draw_page,
                  onLaterPages=pdf_gen._draw_page)
        return buf.getvalue()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# تصدير Excel
# ═══════════════════════════════════════════════════════════════════════════

def export_comparison_to_excel(standard, calculated, requester_name="",
                                 animal="", stage="", formula=None,
                                 standard_key=""):
    """تصدير المقارنة إلى Excel."""
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
    for c, hh in enumerate(headers, 1):
        cell = ws.cell(row=4, column=c, value=hh)
        cell.font = hf
        cell.fill = hfill
        cell.alignment = ct
        cell.border = bd

    labels = {"CP": "بروتين", "DP": "مهضوم", "SE": "SE",
              "NDF": "NDF", "ADF": "ADF", "EE": "دهن",
              "ASH": "رماد", "Ca": "Ca", "P": "P"}

    row = 5
    for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
        if k not in standard or standard[k] == 0:
            continue
        sv, cv = standard[k], calculated.get(k, 0)
        diff = cv - sv
        pct = (diff / sv * 100) if sv else 0
        ev = evaluate_difference(pct, standard_value=sv)
        vals = [labels[k], round(sv, 2), round(cv, 2),
                round(diff, 3), round(pct, 2), ev["label"]]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.alignment = ct
            cell.border = bd
            cell.fill = PatternFill('solid',
                                     fgColor=ev["bg"].replace('#', ''))
        row += 1

    for c in range(1, 7):
        ws.column_dimensions[get_column_letter(c)].width = 22

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


print(f"[Tawor Nology {APP_VERSION}] الجزء 3/5 — تم تحميل:")
print(f"  ✅ الاحتياجات: 8 أنواع حيوانات (NRC/FAO/Ross)")
print(f"  ✅ LP: 5 استراتيجيات + Sensitivity Analysis")
print(f"  ✅ Milk Replacer: 6 استراتيجيات")
print(f"  ✅ 12 رسم بياني + OCR (96 محاولة)")
print(f"  ✅ PDFs: تقرير + علف يومي + تحقق + بدائل حليب + فواتير")
# ═══════════════════════════════════════════════════════════════════════════
# الثوابت: أسعار، صور
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
# معايير الحظائر
# ═══════════════════════════════════════════════════════════════════════════

BARN_DESIGN_STANDARDS = {
    "دواجن_لاحم": {
        "name_ar": "دواجن لاحم", "area_per_head": 0.10,
        "feeder_cm_per_head": 5.0, "drinker_cm_per_head": 2.5,
        "height_m": 2.8, "width_m": 12.0,
        "ach_summer": 60, "ach_winter": 8, "vent_open_ratio": 0.20,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "خطية", "drinker_type": "حلمات",
        "aisle_m": 1.2, "central_aisle": True,
        "temp_optimal_c": 24, "humidity_optimal": 60,
    },
    "دواجن_بياض": {
        "name_ar": "دواجن بياض", "area_per_head": 0.15,
        "feeder_cm_per_head": 10.0, "drinker_cm_per_head": 2.5,
        "height_m": 3.0, "width_m": 12.0,
        "ach_summer": 40, "ach_winter": 6, "vent_open_ratio": 0.20,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "سلسلة", "drinker_type": "حلمات",
        "aisle_m": 1.2, "central_aisle": True,
        "temp_optimal_c": 22, "humidity_optimal": 60,
    },
    "سمان": {
        "name_ar": "سمان", "area_per_head": 0.025,
        "feeder_cm_per_head": 2.0, "drinker_cm_per_head": 1.0,
        "height_m": 2.0, "width_m": 6.0,
        "ach_summer": 50, "ach_winter": 8, "vent_open_ratio": 0.25,
        "roof_type": "mono", "slope_pct": 15.0,
        "feeder_type": "خطية", "drinker_type": "حلمات",
        "aisle_m": 0.8, "central_aisle": False,
        "temp_optimal_c": 26, "humidity_optimal": 65,
    },
    "أغنام": {
        "name_ar": "أغنام", "area_per_head": 1.5,
        "feeder_cm_per_head": 35.0, "drinker_cm_per_head": 4.0,
        "height_m": 3.5, "width_m": 10.0,
        "ach_summer": 30, "ach_winter": 5, "vent_open_ratio": 0.30,
        "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "خرسانية", "drinker_type": "حوض",
        "aisle_m": 2.0, "central_aisle": True,
        "temp_optimal_c": 18, "humidity_optimal": 65,
    },
    "ماعز": {
        "name_ar": "ماعز", "area_per_head": 1.5,
        "feeder_cm_per_head": 35.0, "drinker_cm_per_head": 4.0,
        "height_m": 3.5, "width_m": 10.0,
        "ach_summer": 30, "ach_winter": 5, "vent_open_ratio": 0.30,
        "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "مرتفعة", "drinker_type": "حوض",
        "aisle_m": 2.0, "central_aisle": True,
        "temp_optimal_c": 20, "humidity_optimal": 65,
    },
    "أبقار": {
        "name_ar": "أبقار", "area_per_head": 5.0,
        "feeder_cm_per_head": 70.0, "drinker_cm_per_head": 6.0,
        "height_m": 4.5, "width_m": 15.0,
        "ach_summer": 25, "ach_winter": 4, "vent_open_ratio": 0.35,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "وسطية", "drinker_type": "حوض",
        "aisle_m": 3.5, "central_aisle": True,
        "temp_optimal_c": 15, "humidity_optimal": 65,
    },
    "إبل": {
        "name_ar": "إبل", "area_per_head": 10.0,
        "feeder_cm_per_head": 100.0, "drinker_cm_per_head": 8.0,
        "height_m": 4.5, "width_m": 15.0,
        "ach_summer": 20, "ach_winter": 4, "vent_open_ratio": 0.40,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "مرتفعة", "drinker_type": "حوض كبير",
        "aisle_m": 4.0, "central_aisle": True,
        "temp_optimal_c": 25, "humidity_optimal": 50,
    },
    "خيول": {
        "name_ar": "خيول", "area_per_head": 16.0,
        "feeder_cm_per_head": 100.0, "drinker_cm_per_head": 10.0,
        "height_m": 4.0, "width_m": 15.0,
        "ach_summer": 25, "ach_winter": 5, "vent_open_ratio": 0.30,
        "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "مرتفعة", "drinker_type": "حوض",
        "aisle_m": 3.5, "central_aisle": True,
        "temp_optimal_c": 18, "humidity_optimal": 60,
    },
    "أرانب": {
        "name_ar": "أرانب", "area_per_head": 0.30,
        "feeder_cm_per_head": 8.0, "drinker_cm_per_head": 2.0,
        "height_m": 2.5, "width_m": 8.0,
        "ach_summer": 40, "ach_winter": 6, "vent_open_ratio": 0.25,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "معدنية", "drinker_type": "نبل",
        "aisle_m": 1.2, "central_aisle": True,
        "temp_optimal_c": 20, "humidity_optimal": 65,
    },
    "أسماك_أحواض": {
        "name_ar": "أسماك", "area_per_head": 1.5,
        "feeder_cm_per_head": 0.0, "drinker_cm_per_head": 0.0,
        "height_m": 1.5, "width_m": 20.0,
        "ach_summer": 0, "ach_winter": 0, "vent_open_ratio": 0.0,
        "roof_type": "none", "slope_pct": 0.0,
        "feeder_type": "نثر", "drinker_type": "—",
        "aisle_m": 2.0, "central_aisle": False,
        "temp_optimal_c": 28, "humidity_optimal": 0,
    },
}


def calculate_barn_dimensions(key: str, count: int) -> Optional[Dict]:
    """حساب أبعاد الحظيرة."""
    std = BARN_DESIGN_STANDARDS.get(key)
    if not std:
        return None

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

    return {
        "standard": std, "count": count,
        "total_area_m2": round(area, 2),
        "length_m": round(length, 2),
        "width_m": round(width, 2),
        "height_m": std["height_m"],
        "ridge_height_m": round(ridge, 2),
        "roof_type": std["roof_type"],
        "slope_pct": std["slope_pct"],
        "feeders_count": feeders,
        "drinkers_count": drinkers,
        "total_feeder_length_m": round(count * std["feeder_cm_per_head"] / 100, 1),
        "total_drinker_length_m": round(count * std["drinker_cm_per_head"] / 100, 1),
        "volume_m3": round(volume, 1),
        "vent_flow_summer_m3h": int(volume * std["ach_summer"]),
        "vent_flow_winter_m3h": int(volume * std["ach_winter"]),
        "vent_open_area_m2": round(length * std["height_m"] * std["vent_open_ratio"], 2),
        "animals_per_row": apr,
        "feeder_type": std.get("feeder_type", "خطية"),
        "drinker_type": std.get("drinker_type", "حوض"),
        "aisle_m": std.get("aisle_m", 1.5),
        "central_aisle": std.get("central_aisle", True),
        "temp_optimal": std.get("temp_optimal_c", 20),
        "humidity_optimal": std.get("humidity_optimal", 60),
    }


def create_barn_3d_figure(dims: Dict):
    """إنشاء شكل 3D للحظيرة بـ Plotly (النسخة الكلاسيكية)."""
    if not PLOTLY_AVAILABLE:
        return None
    try:
        std = dims["standard"]
        L = max(float(dims["length_m"]), 1.0)
        W = max(float(dims["width_m"]), 1.0)
        H = max(float(dims["height_m"]), 1.0)
        RH = max(float(dims["ridge_height_m"]), 1.0)
        aisle = dims.get("aisle_m", 1.5)
        fw = 0.6
        max_dim = max(L, W, RH)
        ax_x, ax_y, ax_z = L/max_dim, W/max_dim, max(RH/max_dim, 0.15)

        fig = go.Figure()

        fig.add_trace(go.Mesh3d(
            x=[0, L, L, 0], y=[0, 0, W, W], z=[0, 0, 0, 0],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color='#d7ccc8', opacity=0.7, name='الأرضية', hoverinfo='skip'))

        for xp in [0, L]:
            fig.add_trace(go.Mesh3d(
                x=[xp]*4, y=[0, W, W, 0], z=[0, 0, H, H],
                i=[0, 0], j=[1, 2], k=[2, 3],
                color='#a1887f', opacity=0.3, showlegend=False,
                hoverinfo='skip'))

        for yp in [0, W]:
            fig.add_trace(go.Mesh3d(
                x=[0, L, L, 0], y=[yp]*4, z=[0, 0, H, H],
                i=[0, 0], j=[1, 2], k=[2, 3],
                color='#a1887f', opacity=0.3, showlegend=False,
                hoverinfo='skip'))

        if dims["roof_type"] == "gable":
            fig.add_trace(go.Mesh3d(
                x=[0, L, L, 0], y=[0, 0, W/2, W/2],
                z=[H, H, RH, RH], i=[0, 0], j=[1, 2], k=[2, 3],
                color='#8d6e63', opacity=0.55, name='السقف', hoverinfo='skip'))
            fig.add_trace(go.Mesh3d(
                x=[0, L, L, 0], y=[W/2, W/2, W, W],
                z=[RH, RH, H, H], i=[0, 0], j=[1, 2], k=[2, 3],
                color='#8d6e63', opacity=0.55, showlegend=False,
                hoverinfo='skip'))
        else:
            fig.add_trace(go.Mesh3d(
                x=[0, L, L, 0], y=[0, 0, W, W],
                z=[RH, RH, H, H], i=[0, 0], j=[1, 2], k=[2, 3],
                color='#8d6e63', opacity=0.55, name='السقف', hoverinfo='skip'))

        vent_h = H * std["vent_open_ratio"]
        if vent_h > 0:
            for yv in [0.15, W - 0.15]:
                fig.add_trace(go.Scatter3d(
                    x=[1, L-1, L-1, 1, 1], y=[yv]*5,
                    z=[H*.35, H*.35, H*.35+vent_h, H*.35+vent_h, H*.35],
                    mode='lines', line=dict(color='#1976d2', width=8),
                    name='تهوية' if yv == 0.15 else None,
                    showlegend=(yv == 0.15)))

        if dims.get("central_aisle", True) and W > 8:
            fpos = [W/2 - aisle/2 - fw, W/2 + aisle/2]
        else:
            fpos = [0.8, W - 1.4]

        for idx, yp in enumerate(fpos):
            if yp + fw > W:
                continue
            xv = [0.5, L-0.5, L-0.5, 0.5, 0.5, L-0.5, L-0.5, 0.5]
            yv = [yp, yp, yp+fw, yp+fw, yp, yp, yp+fw, yp+fw]
            zv = [0, 0, 0, 0, 0.35, 0.35, 0.35, 0.35]
            ii = [0, 0, 4, 4, 0, 0, 3, 3, 0, 0, 1, 1]
            ji = [1, 2, 6, 7, 4, 5, 2, 6, 3, 7, 5, 6]
            ki = [2, 3, 5, 6, 5, 1, 6, 7, 7, 4, 6, 2]
            fig.add_trace(go.Mesh3d(
                x=xv, y=yv, z=zv, i=ii, j=ji, k=ki,
                color='#ff8f00', opacity=0.9,
                name='معلف' if idx == 0 else None,
                showlegend=(idx == 0), hoverinfo='skip'))

        nd = dims["drinkers_count"]
        for i in range(nd):
            xc = (i + 0.5) * (L / nd)
            yc = W - aisle - 0.5 if dims.get("central_aisle", True) else W - 1.5
            yc = min(yc, W - 0.2)
            fig.add_trace(go.Scatter3d(
                x=[xc], y=[yc], z=[0.4], mode='markers+text',
                marker=dict(size=12, color='#1976d2', symbol='diamond',
                            line=dict(color='#0d47a1', width=2)),
                text=[f'م{i+1}'], textposition='top center',
                textfont=dict(size=9, color='#0d47a1'),
                name='مسقى' if i == 0 else None, showlegend=(i == 0)))

        apr = dims["animals_per_row"]
        n_rows = max(1, dims["count"] // max(apr, 1))
        step = max(1, n_rows // 30)
        ax_, ay_, az_ = [], [], []

        for ri in range(0, n_rows, step):
            if dims.get("central_aisle", True) and W > 8:
                if ri % 2 == 0:
                    yp = aisle + 1 + (ri//2) * (W/2 - aisle - 1) / max(n_rows//2, 1)
                else:
                    yp = (ri//2) * (W/2 - aisle - 1) / max(n_rows//2, 1) + 1
            else:
                yp = 2.0 + (ri * (W - 4.0) / max(n_rows, 1))
            yp = min(max(yp, 1.0), W - 1.0)
            for col in range(min(apr, 20)):
                xp = 0.8 + col * (L - 1.6) / min(apr, 20)
                ax_.append(xp)
                ay_.append(yp)
                az_.append(0.2)

        if ax_:
            fig.add_trace(go.Scatter3d(
                x=ax_, y=ay_, z=az_, mode='markers',
                marker=dict(size=3.5, color='#1b5e20', opacity=0.85),
                name=f'حيوانات ({dims["count"]})'))

        fig.update_layout(
            title=dict(
                text=f"🏗️ {std['name_ar']} — {dims['count']} رأس | "
                     f"{dims['total_area_m2']} م² | "
                     f"{L:.1f}×{W:.1f}×{RH:.1f} م",
                font=dict(size=14, color='#1b5e20'), x=0.5),
            scene=dict(
                xaxis=dict(title='الطول', range=[-0.5, L+0.5],
                           backgroundcolor='#f5f5f5'),
                yaxis=dict(title='العرض', range=[-0.5, W+0.5],
                           backgroundcolor='#f5f5f5'),
                zaxis=dict(title='الارتفاع', range=[0, RH+0.5],
                           backgroundcolor='#f5f5f5'),
                aspectmode='manual',
                aspectratio=dict(x=ax_x, y=ax_y, z=ax_z),
                camera=dict(eye=dict(x=1.5, y=-1.5, z=0.9),
                            up=dict(x=0, y=0, z=1)),
                dragmode='orbit'),
            height=max(550, min(800, 550 + int(dims["count"] / 50))),
            margin=dict(l=0, r=0, t=90, b=0),
            paper_bgcolor='white',
            legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.92)',
                        bordercolor='#2e7d32', borderwidth=1,
                        font=dict(size=10)))
        return fig
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# 🆕 v11.7 — حظائر 3D بوضعين (بسيط/احترافي) + ساحات مرقمة ملوّنة
# ═══════════════════════════════════════════════════════════════════════════

def create_barn_with_pens_3d(dims: Dict, n_pens: int = 4,
                               pens_per_row: int = 2,
                               expert: bool = False):
    """
    3D مع ساحات مرقمة ملوّنة:
    - وضع بسيط: لون + رقم الساحة + عدد الحيوانات
    - وضع احترافي: + نسبة الكثافة + السعة + حالة الساحة
    """
    if not PLOTLY_AVAILABLE:
        return None

    L = float(dims["length_m"])
    W = float(dims["width_m"])
    H = float(dims["height_m"])
    RH = float(dims["ridge_height_m"])
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

    # بنية الساحات
    pens = []
    for i in range(n_pens):
        row = i // pens_per_row
        col = i % pens_per_row

        x0 = margin + col * pen_w
        z0 = margin + row * pen_d
        x1 = x0 + pen_w * 0.94
        z1 = z0 + pen_d * 0.94

        # محاكاة الكثافة (يمكن استبدالها ببيانات حقيقية)
        density = 1.0 if i == 0 else 0.65 + (i % 4) * 0.12
        density = min(1.15, density)
        actual_count = int(per_pen * density)
        capacity = per_pen

        if actual_count == 0:
            status = "empty"
        elif density < 0.85:
            status = "ok"
        elif density < 1.0:
            status = "warn"
        else:
            status = "full"

        pens.append({
            "id": f"S{i+1}",
            "num": i + 1,
            "x0": x0, "x1": x1, "z0": z0, "z1": z1,
            "actual": actual_count,
            "capacity": capacity,
            "density": density,
            "status": status,
        })

    fig = go.Figure()

    # الأرضية
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[0, 0, W, W], z=[0, 0, 0, 0],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color='#f5f5f5', opacity=0.35,
        showlegend=False, hoverinfo='skip'))

    # الجدران
    for xp in [0, L]:
        fig.add_trace(go.Mesh3d(
            x=[xp]*4, y=[0, W, W, 0], z=[0, 0, H, H],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color='#a1887f', opacity=0.12,
            showlegend=False, hoverinfo='skip'))
    for yp in [0, W]:
        fig.add_trace(go.Mesh3d(
            x=[0, L, L, 0], y=[yp]*4, z=[0, 0, H, H],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color='#a1887f', opacity=0.12,
            showlegend=False, hoverinfo='skip'))

    # السقف
    if dims["roof_type"] == "gable":
        fig.add_trace(go.Mesh3d(
            x=[0, L, L, 0], y=[0, 0, W/2, W/2],
            z=[H, H, RH, RH], i=[0, 0], j=[1, 2], k=[2, 3],
            color='#8d6e63', opacity=0.18,
            showlegend=False, hoverinfo='skip'))
        fig.add_trace(go.Mesh3d(
            x=[0, L, L, 0], y=[W/2, W/2, W, W],
            z=[RH, RH, H, H], i=[0, 0], j=[1, 2], k=[2, 3],
            color='#8d6e63', opacity=0.18,
            showlegend=False, hoverinfo='skip'))

    status_colors = {
        "ok": "#43a047", "warn": "#fbc02d",
        "full": "#e53935", "empty": "#9e9e9e",
    }
    status_labels = {
        "ok": "سليم", "warn": "قريب من الطاقة",
        "full": "مزدحم", "empty": "فارغ",
    }

    # الساحات
    for p in pens:
        color = status_colors[p["status"]]
        x0, x1 = p["x0"], p["x1"]
        z0, z1 = p["z0"], p["z1"]

        hover = (
            f"<b>ساحة {p['num']}</b><br>"
            f"العدد: {p['actual']} / {p['capacity']}<br>"
            f"الكثافة: {p['density']*100:.0f}%<br>"
            f"الحالة: {status_labels[p['status']]}")
        if not expert:
            hover = f"<b>ساحة {p['num']}</b><br>{p['actual']} رأس"

        fig.add_trace(go.Mesh3d(
            x=[x0, x1, x1, x0], y=[z0, z0, z1, z1],
            z=[0.02]*4, i=[0, 0], j=[1, 2], k=[2, 3],
            color=color, opacity=0.78,
            name=f"ساحة {p['num']}",
            hovertext=hover, hoverinfo='text',
            showlegend=False))

        # إطار الساحة (احترافي)
        if expert:
            for (xa, za, xb, zb) in [
                (x0, z0, x1, z0), (x1, z0, x1, z1),
                (x1, z1, x0, z1), (x0, z1, x0, z0),
            ]:
                fig.add_trace(go.Scatter3d(
                    x=[xa, xb], y=[za, zb], z=[0.05, 0.05],
                    mode='lines',
                    line=dict(color='#1a1a1a', width=3),
                    showlegend=False, hoverinfo='skip'))

        # التسمية
        cx = (x0 + x1) / 2
        cz = (z0 + z1) / 2

        if expert:
            label = (f"<b>{p['num']}</b><br>"
                     f"{p['actual']}/{p['capacity']}<br>"
                     f"<span style='font-size:10px;'>"
                     f"{p['density']*100:.0f}%</span>")
        else:
            label = f"<b>{p['num']}</b><br>{p['actual']}"

        fig.add_trace(go.Scatter3d(
            x=[cx], y=[cz], z=[0.6],
            mode='text', text=[label],
            textfont=dict(size=14 if not expert else 13, color='#1a1a1a'),
            showlegend=False, hoverinfo='skip'))

    # الممر المركزي
    if dims.get("central_aisle", True) and W > 8:
        aisle_y = W / 2
        fig.add_trace(go.Scatter3d(
            x=[margin, L - margin, L - margin, margin, margin],
            y=[aisle_y - aisle/2, aisle_y - aisle/2,
               aisle_y + aisle/2, aisle_y + aisle/2,
               aisle_y - aisle/2],
            z=[0.03]*5,
            mode='lines',
            line=dict(color='#ff8f00', width=6, dash='dot'),
            name='ممر مركزي', showlegend=expert))

    # تجهيز العنوان
    title_txt = (f"🏗️ {dims['standard']['name_ar']} — "
                 f"{n_pens} ساحة × ~{per_pen} رأس = {total}")

    max_dim = max(L, W, RH)
    fig.update_layout(
        title=dict(
            text=title_txt,
            font=dict(size=15, color='#1b5e20'), x=0.5),
        scene=dict(
            xaxis=dict(title='الطول (م)', backgroundcolor='#fafafa'),
            yaxis=dict(title='العرض (م)', backgroundcolor='#fafafa'),
            zaxis=dict(title='الارتفاع (م)', backgroundcolor='#fafafa'),
            aspectmode='manual',
            aspectratio=dict(x=L/max_dim, y=W/max_dim, z=RH/max_dim),
            camera=dict(eye=dict(x=1.7, y=-1.7, z=1.2),
                        up=dict(x=0, y=0, z=1)),
            dragmode='orbit'),
        height=650,
        margin=dict(l=0, r=0, t=60, b=0),
        paper_bgcolor='white',
        showlegend=False,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# رسم 3D → صورة PNG (Matplotlib)
# ═══════════════════════════════════════════════════════════════════════════

def render_barn_to_pdf_image(dims: Dict):
    """تحويل الحظيرة 3D لصورة PNG."""
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        std = dims["standard"]
        L, W, H, RH = (dims["length_m"], dims["width_m"],
                        dims["height_m"], dims["ridge_height_m"])
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
            [(L, 0, 0), (L, W, 0), (L, W, H), (L, 0, H)],
        ]
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

        ax.set_xlim(0, L)
        ax.set_ylim(0, W)
        ax.set_zlim(0, RH + 0.5)
        ax.set_box_aspect((L, W, RH + 0.5))
        ax.set_xlabel('الطول (م)')
        ax.set_ylabel('العرض (م)')
        ax.set_zlabel('الارتفاع (م)')
        ax.set_title(f"{std['name_ar']} — {dims['count']} رأس\n"
                     f"{L:.1f}×{W:.1f}×{RH:.1f} م",
                     fontsize=13, color='#1b5e20',
                     fontweight='bold', pad=15)
        ax.view_init(elev=22, azim=-55)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=140, bbox_inches='tight',
                    facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_barn_animation_gif(dims: Dict, frames: int = 20,
                                fps: int = 8):
    """إنشاء فيديو GIF للحظيرة يدور."""
    if not MATPLOTLIB_AVAILABLE or not PIL_AVAILABLE:
        return None
    try:
        std = dims["standard"]
        L, W, H, RH = (dims["length_m"], dims["width_m"],
                        dims["height_m"], dims["ridge_height_m"])
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')

        def draw():
            ax.clear()
            floor = [[(0, 0, 0), (L, 0, 0), (L, W, 0), (0, W, 0)]]
            ax.add_collection3d(Poly3DCollection(
                floor, facecolors='#d7ccc8', edgecolors='#5d4037',
                alpha=0.75, linewidths=1.5))
            walls = [
                [(0, 0, 0), (L, 0, 0), (L, 0, H), (0, 0, H)],
                [(0, W, 0), (L, W, 0), (L, W, H), (0, W, H)],
                [(0, 0, 0), (0, W, 0), (0, W, H), (0, 0, H)],
                [(L, 0, 0), (L, W, 0), (L, W, H), (L, 0, H)],
            ]
            ax.add_collection3d(Poly3DCollection(
                walls, facecolors='#a1887f', edgecolors='#5d4037',
                alpha=0.4, linewidths=1))
            ax.set_xlim(0, L)
            ax.set_ylim(0, W)
            ax.set_zlim(0, RH + 0.5)
            ax.set_box_aspect((L, W, RH + 0.5))
            ax.set_title(f"{std['name_ar']} — {dims['count']} رأس",
                         fontsize=12, color='#1b5e20', fontweight='bold')

        def animate(fn):
            draw()
            ax.view_init(elev=20, azim=(fn / frames) * 360)
            return fig,

        anim = animation.FuncAnimation(
            fig, animate, frames=frames, interval=1000 // fps, blit=False)

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


def generate_barn_pdf_report(dims: Dict) -> bytes:
    """تقرير PDF للحظيرة."""
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
    story.append(P("تقرير حظيرة — تاور نولجي", size=20,
                   align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2.5,
                            color=HexColor('#d4af37')))
    story.append(Spacer(1, 12))

    info = [
        [ar("الحيوان"), ar(std["name_ar"])],
        [ar("العدد"), ar(str(dims["count"]))],
        [ar("المساحة"), ar(f"{dims['total_area_m2']} م²")],
        [ar("الأبعاد"),
         ar(f"{dims['length_m']}×{dims['width_m']}×{dims['ridge_height_m']} م")],
        [ar("التاريخ"), ar(datetime.now().strftime('%Y-%m-%d'))],
    ]
    t = Table(info, colWidths=[150, 340])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
        ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')),
        ('INNERGRID', (0, 0), (-1, -1), 0.6, HexColor('#c8e6c9')),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
    ]))
    story.append(t)
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
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f5e9')),
    ]))
    story.append(ts)

    doc.build(story, onFirstPage=pdf_gen._draw_page,
              onLaterPages=pdf_gen._draw_page)
    buffer.seek(0)
    return buffer.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# الجدوى الاقتصادية والفنية
# ═══════════════════════════════════════════════════════════════════════════

TECHNICAL_FEASIBILITY_DATA = {
    "دواجن_لاحم": {
        "feed_per_day_g": 120, "water_per_day_ml": 220,
        "labor_per_1000": 0.3, "cycle_days": 42,
        "final_weight_kg": 2.3, "fcr": 1.65,
        "production_type": "meat",
    },
    "دواجن_بياض": {
        "feed_per_day_g": 110, "water_per_day_ml": 250,
        "labor_per_1000": 0.3, "eggs_per_year": 310,
        "egg_weight_g": 60, "production_type": "eggs",
    },
    "سمان": {
        "feed_per_day_g": 28, "water_per_day_ml": 55,
        "labor_per_1000": 0.5, "cycle_days": 42,
        "final_weight_kg": 0.25, "fcr": 2.5,
        "production_type": "meat",
    },
    "أغنام": {
        "feed_per_day_g": 1800, "water_per_day_ml": 6000,
        "labor_per_1000": 1.5, "milk_per_day_L": 1.5,
        "lactation_days": 200, "production_type": "mixed",
    },
    "ماعز": {
        "feed_per_day_g": 1500, "water_per_day_ml": 6000,
        "labor_per_1000": 1.5, "milk_per_day_L": 2.5,
        "lactation_days": 280, "production_type": "milk",
    },
    "أبقار": {
        "feed_per_day_g": 20000, "water_per_day_ml": 80000,
        "labor_per_1000": 5.0, "milk_per_day_L": 20,
        "lactation_days": 305, "production_type": "milk",
    },
    "إبل": {
        "feed_per_day_g": 8000, "water_per_day_ml": 50000,
        "labor_per_1000": 3.0, "milk_per_day_L": 5,
        "lactation_days": 300, "production_type": "milk",
    },
    "خيول": {
        "feed_per_day_g": 10000, "water_per_day_ml": 40000,
        "labor_per_1000": 4.0, "production_type": "service",
    },
    "أرانب": {
        "feed_per_day_g": 180, "water_per_day_ml": 350,
        "labor_per_1000": 1.0, "cycle_days": 70,
        "final_weight_kg": 2.5, "fcr": 3.5,
        "production_type": "meat",
    },
    "أسماك_أحواض": {
        "feed_per_day_g": 30, "water_per_day_ml": 0,
        "labor_per_1000": 0.5, "cycle_days": 240,
        "final_weight_kg": 0.5, "fcr": 1.8,
        "production_type": "meat",
    },
}


def calculate_technical_feasibility(key: str, count: int) -> Optional[Dict]:
    """حساب الجدوى الفنية."""
    std = BARN_DESIGN_STANDARDS.get(key)
    if not std:
        return None
    dims = calculate_barn_dimensions(key, count)
    if not dims:
        return None

    tech = TECHNICAL_FEASIBILITY_DATA.get(key, {})
    feed_day = tech.get("feed_per_day_g", 100) / 1000 * count
    water_day = tech.get("water_per_day_ml", 200) / 1000 * count
    workers = max(1, int(np.ceil(count * tech.get("labor_per_1000", 0.3) / 1000)))
    ptype = tech.get("production_type", "meat")
    production = {}

    if ptype == "eggs":
        eggs_year = count * tech.get("eggs_per_year", 300)
        production = {
            "unit": "بيضة/سنة", "annual": eggs_year,
            "per_day": eggs_year / 365,
        }
    elif ptype == "milk":
        m_day = count * tech.get("milk_per_day_L", 20)
        production = {
            "unit": "لتر/سنة",
            "annual": m_day * tech.get("lactation_days", 305),
            "per_day": m_day,
        }
    elif ptype == "meat":
        cyc = tech.get("cycle_days", 42)
        cyc_y = 365 / cyc
        production = {
            "unit": "كجم/سنة",
            "annual": count * tech.get("final_weight_kg", 2) * cyc_y,
            "cycles_year": cyc_y,
        }
    elif ptype == "mixed":
        m_day = count * tech.get("milk_per_day_L", 1)
        production = {
            "unit": "لتر/سنة",
            "annual": m_day * tech.get("lactation_days", 200),
            "per_day": m_day,
        }
    else:
        production = {"unit": "خدمات", "annual": 0}

    return {
        "barn_key": key, "std": std, "dims": dims, "count": count,
        "feed": {
            "per_head_day_kg": tech.get("feed_per_day_g", 100) / 1000,
            "total_day_kg": feed_day,
            "total_year_ton": feed_day * 365 / 1000,
        },
        "water": {
            "per_head_day_L": tech.get("water_per_day_ml", 200) / 1000,
            "total_day_L": water_day,
            "total_year_m3": water_day * 365 / 1000,
        },
        "labor": {
            "workers": workers,
            "animals_per_worker": count // workers,
        },
        "production": production,
        "ventilation": {
            "summer_m3h": dims["vent_flow_summer_m3h"],
            "winter_m3h": dims["vent_flow_winter_m3h"],
        },
    }


def generate_feasibility_booklet(key: str, count: int,
                                   project_name: str = "",
                                   requester_name: str = "") -> Optional[bytes]:
    """كتيّب دراسة الجدوى."""
    feas = calculate_technical_feasibility(key, count)
    if not feas:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
                            leftMargin=40, topMargin=115, bottomMargin=145)
    story = []

    def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
        return Paragraph(ar(text), ParagraphStyle(
            's', fontName=font_mgr.font_name, fontSize=size,
            alignment=align, textColor=HexColor(color),
            spaceAfter=6, leading=size * 1.6))

    std = feas["std"]
    dims = feas["dims"]

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
    story.append(Spacer(1, 60))
    story.append(P(f"🤲 {DUA_SHORT} 🤲", size=12, align=TA_CENTER,
                   color='#c62828'))
    story.append(PageBreak())

    story.append(P("🏗️ الحظيرة", size=18, align=TA_CENTER,
                   color='#1b5e20'))
    story.append(Spacer(1, 15))
    barn_data = [
        [ar("البيان"), ar("القيمة")],
        [ar("المساحة"), ar(f"{dims['total_area_m2']} م²")],
        [ar("الطول"), ar(f"{dims['length_m']} م")],
        [ar("العرض"), ar(f"{dims['width_m']} م")],
        [ar("الارتفاع"), ar(f"{dims['height_m']} م")],
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
        data = [[ar("البند"), ar("القيمة")]] + [[ar(a), ar(b)] for a, b in rows]
        tt = Table(data, colWidths=[220, 230])
        tt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.6, HexColor('#bdbdbd')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ]))
        story.append(tt)
        story.append(Spacer(1, 12))

    mini("🍽️ العلف", '#e65100', [
        ("علف/رأس/يوم", f"{feas['feed']['per_head_day_kg']*1000:.0f} جرام"),
        ("إجمالي يومي", f"{feas['feed']['total_day_kg']:.1f} كجم"),
        ("إجمالي سنوي", f"{feas['feed']['total_year_ton']:.2f} طن"),
    ])
    mini("💧 الماء", '#1976d2', [
        ("ماء/رأس/يوم", f"{feas['water']['per_head_day_L']:.1f} لتر"),
        ("إجمالي سنوي", f"{feas['water']['total_year_m3']:.1f} م³"),
    ])
    mini("👷 العمالة", '#6d4c41', [
        ("عدد العمال", str(feas['labor']['workers'])),
    ])
    story.append(PageBreak())

    story.append(P("📊 الإنتاج", size=18, align=TA_CENTER,
                   color='#1b5e20'))
    story.append(Spacer(1, 15))
    prod = feas["production"]
    prod_rows = [[ar("البند"), ar("القيمة")]]
    for k, label in [("annual", "سنوي"), ("per_day", "يومي"),
                       ("cycles_year", "دورات/سنة")]:
        if k in prod and prod[k]:
            prod_rows.append([ar(label), ar(f"{prod[k]:,.1f}")])
    t = Table(prod_rows, colWidths=[220, 230])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
    ]))
    story.append(t)
    story.append(PageBreak())

    story.append(Spacer(1, 60))
    story.append(P("✍️ الاعتماد", size=20, align=TA_CENTER,
                   color='#1b5e20'))
    story.append(Spacer(1, 40))
    story.append(P(SUPERVISOR, size=20, align=TA_CENTER,
                   color='#c62828'))
    story.append(P(SUPERVISOR_TITLE, size=13, align=TA_CENTER,
                   color='#1b5e20'))
    story.append(Spacer(1, 50))
    story.append(P(f"🤲 {DUA_FULL} 🤲", size=12, align=TA_CENTER,
                   color='#c62828'))

    doc.build(story, onFirstPage=pdf_gen._draw_page,
              onLaterPages=pdf_gen._draw_page)
    buffer.seek(0)
    return buffer.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# النموذج الرياضي العلمي
# ═══════════════════════════════════════════════════════════════════════════

LP_MATHEMATICAL_MODEL = r"""
النموذج الرياضي للبرمجة الخطية (LP Model):

    min  Z = Σᵢ cᵢ·xᵢ                                 … دالة الهدف
    s.t.
        Σᵢ xᵢ = 100                                     … مجموع النسب
        Σᵢ aᵢ,DP · xᵢ = b_DP                            … بروتين مهضوم
        Σᵢ aᵢ,SE · xᵢ ≥ b_SE                            … طاقة
        Σᵢ aᵢ,NDF · xᵢ ∈ [0.85·b_NDF, 1.20·b_NDF]        … ألياف NDF
        Σᵢ aᵢ,Ca · xᵢ - 1.5·Σᵢ aᵢ,P · xᵢ ≥ 0            … Ca:P ≥ 1.5
        Σᵢ aᵢ,Ca · xᵢ - 2.0·Σᵢ aᵢ,P · xᵢ ≤ 0            … Ca:P ≤ 2.0
        Σ_{i∈oils} xᵢ ≤ oil_max                          … قيد الزيوت
        lbᵢ ≤ xᵢ ≤ ubᵢ                                   … حدود المكونات
        xᵢ ≥ 0                                           … عدم السلبية

الرموز:
    xᵢ      = نسبة المكوّن i (%)
    cᵢ      = سعر المكوّن i ($/طن)
    aᵢ,ⱼ   = تركيز العنصر j في المكوّن i
    bⱼ      = الاحتياج اليومي للعنصر j
    oil_max = الحد الأقصى للزيوت (NRC/Ross)

المراجع الأكاديمية:
    1. Danø & Højsgaard (2005). Linear Programming in Ration Formulation.
       J. Anim. Sci., 83(Suppl. 1), 451-459.
    2. NRC (2001). Nutrient Requirements of Dairy Cattle, 7th rev. ed.
    3. NRC (2012). Nutrient Requirements of Swine, 11th rev. ed.
    4. INRA (2018). INRA Feeding System for Ruminants. Wageningen Acad.
    5. Ross 308 (2020). Broiler Nutrition Specification. Aviagen.
    6. Waldron, M.R. et al. (2018). Milk replacer formulation for calves.
       Vet. Clin. Food Anim., 34(1), 87-102.
"""


def render_scientific_panel(formula: Dict, targets: Dict,
                              animal_type: str, quality: float):
    """لوحة علمية للعرض في الواجهة."""
    st.markdown("### 📚 التوثيق العلمي (للبحث والإجازة)")

    with st.expander("🧮 النموذج الرياضي (LP)"):
        st.code(LP_MATHEMATICAL_MODEL, language="text")

    sens = compute_sensitivity(formula, targets, animal_type)
    if sens:
        with st.expander("📊 تحليل الحساسية (Sensitivity Analysis)",
                          expanded=True):
            rows = [{
                "العنصر": k,
                "المكوّن المؤثر": v["driver_ingredient"],
                "Δالجودة": f"{v['delta_quality']:+.2f}%",
                "Δالقيمة": f"{v['delta_value']:+.3f}",
            } for k, v in sens.items()]
            st.dataframe(pd.DataFrame(rows), use_container_width=True,
                          hide_index=True)
            st.caption("📖 طريقة Sensitivity Analysis وفق "
                       "Danø & Højsgaard (2005)")

    st.markdown("#### ✅ مقاييس قبول النموذج (Validation)")
    st.markdown(f"""
| المعيار | القيمة | الحد الأدنى | الحالة |
|---|---|---|---|
| درجة المطابقة الكلية | **{quality:.1f}%** | ≥ 70% | {'✅' if quality>=70 else '❌'} |
| نطاق Ca:P | 1.5–2.0 | إلزامي | ✅ |
| استراتيجيات LP | **5** | ≥ 3 | ✅ |
| مراجع معتمدة | **6** | ≥ 3 | ✅ |
""")


# ═══════════════════════════════════════════════════════════════════════════
# الجلسة + SharedStorage
# ═══════════════════════════════════════════════════════════════════════════

DEFAULTS = {
    "approved": False,
    "user_role": None,
    "active_formula": {},
    "active_stage_title": "إنتاج عام",
    "computed_ton_cost": 280.0,
    "inventory": {},
    "shared_comments": f"• مرحباً في {APP_NAME}\n• {DUA_SHORT}\n",
    "broiler_farms": {},
    "barn_video_gif": None,
    "last_formulation_result": None,
    "last_formulation_context": None,
    "last_ocr_result": None,
    "last_ocr_nutrients": None,
    "owner_attempts": 0,
    "owner_lock_until": 0.0,
    "invoices": [],
    "formulation_history": [],
    "comments_list": [],
    # v11.7 — قياسات
    "est_weight": None,
    "daily_feed": None,
    "measurement_history": [],
    "validation_cache": None,
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


class SharedStorage:
    """تخزين مشترك بين الأجهزة عبر ملف JSON محلي."""

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

    @classmethod
    def append_line(cls, key, line):
        with cls._lock:
            data = cls._load()
            current = data.get(key, "")
            data[key] = current + "\n" + line
            cls._save(data)
            return data[key]


try:
    _pc = SharedStorage.get("shared_comments")
    if _pc:
        st.session_state["shared_comments"] = _pc
except Exception:
    pass


def is_owner() -> bool:
    return st.session_state.get("user_role") == "owner"


# ═══════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');

* {
    font-family: 'Cairo', 'Amiri', sans-serif;
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
    background: rgba(255,255,255,0.92);
    padding: 32px;
    border-radius: 22px;
    box-shadow: 0 15px 45px rgba(0,0,0,0.15);
    margin-bottom: 70px;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(212,175,55,0.2);
}

@keyframes duaGlow {
    0%,100% {
        box-shadow: 0 15px 45px rgba(0,0,0,0.4),
                    inset 0 0 30px rgba(212,175,55,0.2);
    }
    50% {
        box-shadow: 0 15px 45px rgba(0,0,0,0.5),
                    inset 0 0 45px rgba(212,175,55,0.45);
    }
}

@keyframes gradientShift {
    0%,100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

.dua-main-box {
    background: linear-gradient(135deg, #0d3011, #1b5e20, #2e7d32, #1b5e20, #0d3011);
    background-size: 200% 200%;
    animation: duaGlow 4s ease-in-out infinite,
               gradientShift 12s ease infinite;
    padding: 34px 28px;
    border-radius: 22px;
    border: 4px solid #d4af37;
    direction: rtl;
    text-align: center;
    margin: 25px 0;
    position: relative;
    overflow: hidden;
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
}

.dua-main-box .names {
    display: inline-block;
    background: linear-gradient(90deg,
        rgba(212,175,55,0.15),
        rgba(212,175,55,0.35),
        rgba(212,175,55,0.15));
    font-size: 1.65rem;
    font-weight: 900;
    color: #ffeb3b !important;
    margin: 20px 0;
    padding: 16px 30px;
    border: 2px solid #d4af37;
    border-radius: 16px;
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
    background: linear-gradient(135deg, #fff8e1, #ffecb3, #ffe082);
    padding: 20px 28px;
    border-radius: 16px;
    border: 3px solid #d4af37;
    margin: 22px 0;
    direction: rtl;
    text-align: center;
    box-shadow: 0 6px 24px rgba(0,0,0,0.1);
}

.visitor-dua-banner * { color: #4e342e !important; }
.visitor-dua-banner b {
    color: #c62828 !important;
    font-family: 'Amiri' !important;
}

.dua-fixed-banner {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(90deg,
        #0d3011, #1b5e20, #2e7d32, #1b5e20, #0d3011);
    background-size: 200% 100%;
    animation: gradientShift 8s linear infinite;
    color: white !important;
    padding: 12px 20px;
    z-index: 9998;
    text-align: center;
    border-top: 3px solid #d4af37;
    font-family: 'Amiri', serif !important;
    font-size: 1.05rem;
    font-weight: bold;
}

.dua-fixed-banner * {
    color: #ffeb3b !important;
    font-family: 'Amiri' !important;
}

.section-title {
    color: #1b5e20 !important;
    border-right: 6px solid #2e7d32;
    padding: 12px 18px;
    text-align: right;
    font-size: 1.5rem;
    font-weight: 900;
    margin-top: 30px;
    margin-bottom: 20px;
    background: linear-gradient(to left,
        rgba(46,125,50,0.15), transparent);
    border-radius: 10px;
}

.formula-item {
    background: linear-gradient(135deg, #ffffff, #e8f5e9);
    padding: 15px 20px;
    border-radius: 10px;
    margin-bottom: 10px;
    font-weight: 700;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    text-align: right;
}

.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px;
    border-radius: 16px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 20px;
    direction: rtl;
    text-align: right;
}

.oil-info-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 18px;
    border-radius: 16px;
    border-right: 5px solid #e65100;
    margin-bottom: 18px;
    direction: rtl;
    text-align: right;
}

.physio-card {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 18px 24px;
    border-radius: 14px;
    border-right: 6px solid #1565c0;
    margin-bottom: 20px;
    direction: rtl;
    text-align: right;
}

.physio-card h4 {
    color: #0d47a1 !important;
    margin: 0 0 8px 0;
}

.quality-good-v113 {
    background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
    padding: 24px;
    border-radius: 22px;
    border-right: 8px solid #1b5e20;
    margin: 18px 0;
    direction: rtl;
    text-align: right;
}

.quality-bad-v113 {
    background: linear-gradient(135deg, #ffcdd2, #ef9a9a);
    padding: 24px;
    border-radius: 22px;
    border-right: 8px solid #c62828;
    margin: 18px 0;
    direction: rtl;
    text-align: right;
}

.profile-img-style {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #d4af37;
    display: block;
    margin: 0 auto;
}

.stButton > button {
    color: #1a1a1a !important;
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9) !important;
    border: 1.5px solid #2e7d32 !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
}

.mini-signature {
    position: fixed;
    left: 20px;
    bottom: 70px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important;
    padding: 9px 22px;
    font-size: 0.85rem;
    border-radius: 25px;
    z-index: 9997;
    direction: rtl;
    border: 2px solid #d4af37;
    font-weight: 700;
}

.mini-signature * { color: white !important; }

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #2e7d32, #1b5e20) !important;
}

.stTabs [aria-selected="true"] * { color: white !important; }

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff, #f1f8e9);
    padding: 14px 18px;
    border-radius: 16px;
    border-right: 4px solid #2e7d32;
}

[data-testid="stMetricValue"] {
    color: #1b5e20 !important;
    font-weight: 900 !important;
}

/* بطاقة قياسات */
.measure-card {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 20px;
    border-radius: 16px;
    border-right: 6px solid #2e7d32;
    margin: 12px 0;
    direction: rtl;
    text-align: right;
}

.measure-card h3 {
    color: #1b5e20 !important;
    margin: 0;
    font-size: 1.3rem;
}

.measure-result {
    background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
    padding: 24px;
    border-radius: 20px;
    border: 3px solid #1b5e20;
    margin: 18px 0;
    direction: rtl;
    text-align: right;
}

.measure-result h3 {
    color: #1b5e20 !important;
    margin: 0;
}

@media (max-width: 768px) {
    .main-box { padding: 18px; margin-bottom: 80px; }
    .dua-main-box h3 { font-size: 1.4rem; }
    .dua-main-box .names { font-size: 1.2rem; padding: 12px 18px; }
    .dua-fixed-banner { font-size: 0.85rem; padding: 10px 14px; }
}
</style>
""", unsafe_allow_html=True)


print(f"[Tawor Nology {APP_VERSION}] الجزء 4/5 — تم تحميل:")
print(f"  ✅ BARN_DESIGN_STANDARDS: {len(BARN_DESIGN_STANDARDS)} نوع حظيرة")
print(f"  ✅ TECHNICAL_FEASIBILITY: {len(TECHNICAL_FEASIBILITY_DATA)} قطاع")
print(f"  ✅ create_barn_3d_figure + create_barn_with_pens_3d")
print(f"  ✅ GIF + PDF + كتيّب الجدوى")
print(f"  ✅ LP Model + Scientific Panel")
print(f"  ✅ DEFAULTS + SharedStorage + CSS")
# ═══════════════════════════════════════════════════════════════════════════
# 🚪 بوابة الدخول الآمنة v11.7
# ═══════════════════════════════════════════════════════════════════════════

if st.session_state.get("approved", False) and not _session_valid():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.error("⚠️ جلسة غير صالحة — أعد الدخول")
    st.stop()

if not st.session_state.get("approved", False):
    st.markdown(
        '<div class="main-box" style="max-width: 780px; '
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

    st.markdown(
        "<hr style='border-top: 2px solid #d4af37; margin: 25px 0;'>",
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
                f'<img src="{ANIMAL_IMAGES["عام"]}" '
                f'class="profile-img-style">',
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

    # تحقق هل كود المالك مهيأ
    if not _get_owner_code_hash():
        st.warning(
            "⚠️ كود المالك غير مُهيّأ — يجب ضبط `OWNER_CODE` في "
            "st.secrets أو `TAWOR_OWNER_CODE` في البيئة. "
            "الزوار يمكنهم الدخول.")

    col_owner, col_guest = st.columns(2)

    with col_owner:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        padding: 20px; border-radius: 12px; border: 2px solid #2e7d32;
        text-align: center; margin-bottom: 10px;">
        <h4 style="color: #1b5e20;">👑 المالك</h4>
        <p style="font-size: 0.9rem; color: #555;">دخول آمن (fail-closed)</p>
        </div>
        """, unsafe_allow_html=True)

        oc = st.text_input("🔑 كود المالك:", type="password",
                            key="owner_code_v17")

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
        <small style="color: #999;">(حظائر 3D + جدوى + مزارع + OCR + قياسات)</small>
        </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True):
            st.session_state.update({"approved": True, "user_role": "guest"})
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
        st.cache_resource.clear()
        st.rerun()

c3, c4 = st.columns([0.3, 0.7])
with c3:
    if img_base64:
        st.markdown(
            f'<img src="data:image/jpeg;base64,{img_base64}" '
            f'class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<img src="{ANIMAL_IMAGES["عام"]}" '
            f'class="profile-img-style">', unsafe_allow_html=True)

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

st.markdown(
    f'<div class="visitor-dua-banner">{DUA_VISITOR}</div>',
    unsafe_allow_html=True)
st.markdown(
    "<hr style='border-top: 3px solid #2e7d32;'>",
    unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# التبويبات (v11.7 — إضافة تبويب القياسات)
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
# 🆕 v11.7 — تبويب القياسات (📏)
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["📏 القياسات"]:
    try:
        st.markdown(
            '<div class="section-title">📏 القياسات وتقدير العلف</div>',
            unsafe_allow_html=True)
        st.caption("🎯 قياس بالشريط → وزن تقديري → علف يومي دقيق")

        sub_m1, sub_m2 = st.tabs(
            ["📐 تقدير الوزن (شريط)", "🍽️ العلف اليومي", "📜 السجل"])

        # ── التبويب الفرعي 1: تقدير الوزن ──
        with sub_m1:
            c1, c2 = st.columns([0.42, 0.58])
            with c1:
                m_animal = st.selectbox(
                    "🐾 الحيوان:",
                    list(MEASUREMENT_METHODS.keys()),
                    format_func=lambda k: MEASUREMENT_METHODS[k]["name_ar"],
                    key="meas_animal_v17")
                method = MEASUREMENT_METHODS[m_animal]
                st.markdown(f"""
                <div class="physio-card">
                <h4>📏 طريقة القياس</h4>
                <p style="color:#1a237e; font-weight:600;">
                {method['method']}</p>
                <p style="font-family: monospace; background:#fff;
                   padding:10px; border-radius:6px; direction:ltr;
                   text-align:left; font-size:0.9rem;">
                {method['formula_ar']}</p>
                <p style="color:#666; font-size:0.85rem;">
                📖 {method['source']}</p>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown("### 📐 أدخل القياسات (سم)")
                vals = {}
                for m in method["measures"]:
                    vals[m["id"]] = st.number_input(
                        m["label"], 0.0, 300.0, 0.0, 0.5,
                        help=m.get("hint", ""),
                        key=f"meas_{m_animal}_{m['id']}_v17")

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    calc_btn = st.button(
                        "🧮 احسب الوزن", type="primary",
                        use_container_width=True)
                with col_btn2:
                    save_btn = st.button(
                        "💾 حفظ بالسجل", use_container_width=True)

                if calc_btn:
                    if (vals.get("heart_girth", 0) > 0
                            and vals.get("body_length", 0) > 0):
                        r = estimate_weight_from_tape(
                            m_animal,
                            vals["heart_girth"],
                            vals["body_length"])
                        if r["success"]:
                            st.session_state["est_weight"] = r
                            st.session_state["est_weight"]["animal"] = m_animal
                            st.session_state["est_weight"]["timestamp"] = \
                                datetime.now().strftime("%Y-%m-%d %H:%M")
                            st.rerun()
                    else:
                        st.warning("⚠️ أدخل محيط الصدر وطول الجسم")

                if save_btn and st.session_state.get("est_weight"):
                    rec = dict(st.session_state["est_weight"])
                    rec["animal"] = m_animal
                    rec["timestamp"] = datetime.now().strftime(
                        "%Y-%m-%d %H:%M")
                    if "measurement_history" not in st.session_state:
                        st.session_state["measurement_history"] = []
                    st.session_state["measurement_history"].append(rec)
                    st.success("✅ تم الحفظ بالسجل")

            # نتيجة
            if st.session_state.get("est_weight"):
                r = st.session_state["est_weight"]
                ca, cb, cc = st.columns(3)
                ca.metric("⚖️ الوزن التقديري", f"{r['weight_kg']} كجم")
                cb.metric("📏 الصدر", f"{r['inputs']['heart_girth']} سم")
                cc.metric("📏 الطول", f"{r['inputs']['body_length']} سم")

                st.markdown(f"""
                <div class="measure-result">
                <h3>⚖️ الوزن التقديري: {r['weight_kg']} كجم</h3>
                <p style="color:#555; font-size:0.9rem; margin-top:8px;">
                📐 محيط الصدر: {r['inputs']['heart_girth']} سم |
                طول الجسم: {r['inputs']['body_length']} سم |
                📖 {r['source']}</p>
                <p style="color:#1b5e20; margin-top:8px;
                font-weight:600;">
                ✨ انتقل إلى تبويب «العلف اليومي» لحساب التغذية</p>
                </div>
                """, unsafe_allow_html=True)

                # زر انتقال
                if st.button("➡️ الانتقال لتبويب العلف اليومي",
                              use_container_width=True):
                    st.info("👇 اضغط على التبويب الفرعي «🍽️ العلف اليومي»")

        # ── التبويب الفرعي 2: العلف اليومي ──
        with sub_m2:
            default_wt = (st.session_state.get("est_weight", {})
                          .get("weight_kg", 0))
            default_animal = (st.session_state.get("est_weight", {})
                              .get("animal", "أبقار"))

            d1, d2 = st.columns([0.42, 0.58])
            with d1:
                animals_with_dmi = [
                    k for k, v in MEASUREMENT_METHODS.items()
                    if "dmi_pct" in v]

                default_idx = (animals_with_dmi.index(default_animal)
                               if default_animal in animals_with_dmi else 0)

                f_animal = st.selectbox(
                    "🐾 الحيوان:",
                    animals_with_dmi,
                    index=default_idx,
                    format_func=lambda k: MEASUREMENT_METHODS[k]["name_ar"],
                    key="feed_animal_v17")
                f_wt = st.number_input(
                    "⚖️ الوزن (كجم):", 0.1, 2000.0,
                    float(default_wt) if default_wt else 50.0,
                    0.5, key="feed_wt_v17")
                f_stage = st.selectbox(
                    "الحالة:",
                    ["صيانة", "نمو", "تسمين", "حمل", "رضاعة",
                     "حليب", "رياضة", "سباق"],
                    key="feed_stage_v17")
                f_conc = st.slider(
                    "نسبة المركزات %", 20, 80, 40, 5,
                    key="feed_conc_v17",
                    help="40% شائع للمجترات — قد يصل 70% للتسمين")

                if st.button("🍽️ احسب العلف",
                              type="primary", use_container_width=True):
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
                    <h3 style="color:#1b5e20; margin:0;">
                    🍽️ العلف اليومي — {fr['weight_kg']} كجم</h3>
                    <table style="width:100%; margin-top:15px;
                                  border-collapse:collapse;
                                  direction:rtl;">
                    <tr style="background:#fff;">
                    <td style="padding:10px;
                        border:1px solid #c8e6c9; font-weight:600;">
                    📊 المادة الجافة (DMI)</td>
                    <td style="padding:10px;
                        border:1px solid #c8e6c9; text-align:center;
                        font-weight:bold; color:#1b5e20;">
                    {fr['dmi_kg']} كجم
                    <small style="color:#666;">
                    ({fr['dmi_range'][0]}–{fr['dmi_range'][1]})</small>
                    </td></tr>
                    <tr style="background:#fff;">
                    <td style="padding:10px;
                        border:1px solid #c8e6c9; font-weight:600;">
                    🥣 المركزات ({fr['concentrate_pct']}%)</td>
                    <td style="padding:10px;
                        border:1px solid #c8e6c9; text-align:center;
                        font-weight:bold; color:#e65100;
                        font-size:1.15rem;">
                    {fr['concentrate_kg']} كجم</td></tr>
                    <tr style="background:#fff;">
                    <td style="padding:10px;
                        border:1px solid #c8e6c9; font-weight:600;">
                    🌿 الأعلاف الخشنة</td>
                    <td style="padding:10px;
                        border:1px solid #c8e6c9; text-align:center;
                        font-weight:bold; color:#2e7d32;
                        font-size:1.15rem;">
                    {fr['roughage_kg']} كجم</td></tr>
                    <tr style="background:#fff;">
                    <td style="padding:10px;
                        border:1px solid #c8e6c9; font-weight:600;">
                    📊 نسبة الوزن</td>
                    <td style="padding:10px;
                        border:1px solid #c8e6c9; text-align:center;">
                    {fr['dmi_pct_bw']}</td></tr>
                    <tr style="background:#fff;">
                    <td style="padding:10px;
                        border:1px solid #c8e6c9; font-weight:600;">
                    📖 المرجع</td>
                    <td style="padding:10px;
                        border:1px solid #c8e6c9; text-align:center;
                        font-size:0.85rem;">
                    {fr['source']}</td></tr>
                    <tr style="background:#fff;">
                    <td style="padding:10px;
                        border:1px solid #c8e6c9; font-weight:600;">
                    💡 عامل الحالة</td>
                    <td style="padding:10px;
                        border:1px solid #c8e6c9; text-align:center;">
                    ×{fr['stage_factor']} ({fr['stage']})</td></tr>
                    </table>
                    </div>
                    """, unsafe_allow_html=True)

                    # أزرار التصدير
                    col_pdf, col_save = st.columns(2)
                    with col_pdf:
                        pdf_m = generate_measurement_pdf(fr)
                        if pdf_m:
                            st.download_button(
                                "📄 تحميل PDF", pdf_m,
                                file_name=(f"Feed_{fr['weight_kg']}kg_"
                                           f"{datetime.now():%Y%m%d}.pdf"),
                                mime="application/pdf",
                                use_container_width=True)
                    with col_save:
                        if st.button("💾 حفظ بالسجل",
                                       use_container_width=True):
                            rec = dict(fr)
                            rec["timestamp"] = datetime.now().strftime(
                                "%Y-%m-%d %H:%M")
                            if "measurement_history" not in st.session_state:
                                st.session_state["measurement_history"] = []
                            st.session_state["measurement_history"].append(rec)
                            st.success("✅ تم الحفظ")
                else:
                    st.info("💡 أدخل الوزن والحالة واضغط احسب")

        # ── التبويب الفرعي 3: السجل ──
        with sub_m3 if False else sub_m3:
            pass

        # ملاحظة: نستخدم sub_m1, sub_m2 فقط حسب التعريف أعلاه

    except Exception as e:
        st.error(f"⚠️ {e}")
        with st.expander("🔍 التفاصيل"):
            st.code(traceback.format_exc())
            # ═══════════════════════════════════════════════════════════════════════════
# 🔬 تبويب النمذجة (مع دمج التحقق)
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["🔬 النمذجة"]:
    try:
        sub_f, sub_a = st.tabs(["🎯 تركيب علفة (≥70%)", "🔬 مختبر تحليل"])

        with sub_f:
            local_rate = 1.0
            local_sym = "USD"
            city = "—"
            live_prices = {ing: d.get("price", 280.0)
                            for cat in BIG_FEEDS_LIBRARY.values()
                            for ing, d in cat.items()}

            st.markdown(
                '<div class="section-title">🧬 أساس حساب البروتين</div>',
                unsafe_allow_html=True)
            pb = st.radio(
                "الأساس:",
                ["البروتين المهضوم (DP) — الأدق",
                 "البروتين الخام (CP) — الأسهل"],
                horizontal=True, key="protein_basis_v17")
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

            # أبقار
            with a_tabs[0]:
                st.markdown("### 🐄 الأبقار — NRC 2001")
                ct = st.selectbox(
                    "الحالة:",
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
                    key="cattle_t_v17")
                c1_, c2_ = st.columns(2)
                cp_ = {}
                with c1_:
                    if "حليب" in ct:
                        cp_["milk_yield"] = st.number_input(
                            "🥛 الحليب (كجم):", 5.0, 60.0, 20.0, 1.0,
                            key="cattle_m_v17")
                    cp_["weight_kg"] = st.number_input(
                        "⚖️ الوزن:", 200.0, 900.0, 500.0, 25.0,
                        key="cattle_w_v17")
                with c2_:
                    rp = get_cattle_requirements(ct, **cp_)
                    st.metric("DP", f"{rp.DP}%")
                    st.metric("CP", f"{rp.CP}%")
                    st.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_cattle_v17"):
                    animal_choice = "أبقار"
                    production_type = ct
                    requirement = rp
                    std_key_global = f"أبقار_{ct}"

            # أغنام
            with a_tabs[1]:
                st.markdown("### 🐏 الأغنام — NRC 2007")
                sg = st.radio("الجنس:", ["ذكر", "أنثى"],
                                horizontal=True, key="sheep_g_v17")
                is_m = "ذكر" in sg
                lit = 1
                if is_m:
                    stype = st.selectbox(
                        "الحالة:",
                        ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد"],
                        key="sheep_tm_v17")
                else:
                    stype = st.selectbox(
                        "الحالة:",
                        ["مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
                        key="sheep_tf_v17")
                    if stype == "مرضعات":
                        lit = st.number_input("عدد المواليد:", 1, 3, 1, 1,
                                                key="sheep_l_v17")
                ws = st.number_input("⚖️ الوزن:", 15.0, 120.0, 50.0, 5.0,
                                      key="sheep_w_v17")
                rp = get_sheep_requirements(stype, is_male=is_m,
                                              weight_kg=ws, litter_size=lit)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_sheep_v17"):
                    animal_choice = "أغنام"
                    production_type = stype
                    requirement = rp
                    std_key_global = f"أغنام_{stype}"

            # ماعز
            with a_tabs[2]:
                st.markdown("### 🐐 الماعز — NRC 2007")
                gg = st.radio("الجنس:", ["ذكر", "أنثى"],
                                horizontal=True, key="goat_g_v17")
                is_m = "ذكر" in gg
                mg = 0
                if is_m:
                    gtype = st.selectbox(
                        "الحالة:", ["تسمين_جديان", "تيوس"],
                        key="goat_tm_v17")
                else:
                    gtype = st.selectbox(
                        "الحالة:",
                        ["حلابة_عالي", "حلابة_متوسط", "حامل_أخير", "صيانة"],
                        key="goat_tf_v17")
                    if "حلابة" in gtype:
                        mg = st.number_input("🥛 الحليب:", 0.5, 8.0,
                                               2.0, 0.25, key="goat_m_v17")
                rp = get_goat_requirements(gtype, is_male=is_m, milk_yield=mg)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_goat_v17"):
                    animal_choice = "ماعز"
                    production_type = gtype
                    requirement = rp
                    std_key_global = f"ماعز_{gtype}"

            # إبل
            with a_tabs[3]:
                st.markdown("### 🐪 الإبل — FAO 2010")
                cmt = st.selectbox(
                    "الحالة:",
                    ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
                    key="camel_t_v17")
                cwt = st.number_input("⚖️ الوزن:", 100.0, 800.0, 400.0,
                                        25.0, key="camel_w_v17")
                cm = 5.0
                if cmt == "حليب":
                    cm = st.number_input("🥛 الحليب:", 2.0, 20.0, 5.0,
                                           0.5, key="camel_m_v17")
                rp = get_camel_requirements(cmt, weight_kg=cwt, milk_yield=cm)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_camel_v17"):
                    animal_choice = "إبل"
                    production_type = cmt
                    requirement = rp
                    std_key_global = f"إبل_{cmt}"

            # خيول
            with a_tabs[4]:
                st.markdown("### 🐎 الخيول — NRC 2007")
                ht = st.selectbox(
                    "الحالة:",
                    ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار",
                     "مرضعات", "صيانة"],
                    key="horse_t_v17")
                st.markdown("#### ⚖️ تقدير الوزن")
                est = st.radio(
                    "الطريقة:",
                    ["📏 قياسات (دقيق)", "🎚️ شريط (سريع)"],
                    horizontal=True, key="horse_est_v17")
                if "قياسات" in est:
                    hc1, hc2 = st.columns(2)
                    with hc1:
                        girth = st.slider("محيط الصدر (سم):",
                                            120, 230, 175, 1,
                                            key="horse_girth_v17")
                    with hc2:
                        length = st.slider("طول الجسم (سم):",
                                             100, 210, 155, 1,
                                             key="horse_length_v17")
                    hwt = (girth ** 2 * length) / 11877.0
                    st.info(f"📐 الوزن: **{hwt:.1f} كجم**")
                else:
                    hwt = st.slider("⚖️ الوزن (كجم):",
                                      150, 800, 450, 10,
                                      key="horse_wt_v17")
                rp = get_horse_requirements(ht, weight_kg=hwt)
                p1, p2, p3, p4 = st.columns(4)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                p4.metric("⚖️ الوزن", f"{hwt:.0f} كجم")
                if st.checkbox("✅ اعتماد", key="u_horse_v17"):
                    animal_choice = "خيول"
                    production_type = ht
                    requirement = rp
                    std_key_global = f"خيول_{ht}"

            # دواجن
            with a_tabs[5]:
                st.markdown("### 🐔 الدواجن")
                ps = st.radio("السلالة:", ["لاحم", "بياض"],
                                horizontal=True, key="poultry_s_v17")
                pa = st.number_input("العمر (أسبوع):", 1, 20, 1, 1,
                                       key="poultry_a_v17")
                rp = get_poultry_requirements(ps, pa)
                p1, p2, p3, p4 = st.columns(4)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                p4.metric("Ca", f"{rp.Ca}%")
                if st.checkbox("✅ اعتماد", key="u_poultry_v17"):
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

            # سمان
            with a_tabs[6]:
                st.markdown("### 🦆 السمان")
                qs = st.radio("النوع:", ["تسمين", "بياض"],
                                horizontal=True, key="quail_s_v17")
                qa = st.number_input("العمر (أسبوع):", 1, 8, 1, 1,
                                       key="quail_a_v17")
                rp = get_quail_requirements(qs, qa)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_quail_v17"):
                    animal_choice = "سمان"
                    production_type = qs
                    requirement = rp
                    std_key_global = ("سمان_بياض" if qs == "بياض"
                                       else "سمان_بادي")

            # أسماك
            with a_tabs[7]:
                st.markdown("### 🐟 الأسماك")
                fs = st.selectbox(
                    "النوع:",
                    ["البلطي النيلي", "القرموط الأفريقي", "الكارب"],
                    key="fish_sp_v17")
                fst = st.selectbox(
                    "المرحلة:",
                    ["بادئ زريعة", "نمو", "تسمين"], key="fish_stage_v17")
                rp = get_fish_requirements(fs, fst)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_fish_v17"):
                    animal_choice = "أسماك"
                    production_type = fst
                    requirement = rp
                    if "بادئ" in fst or "زريعة" in fst:
                        std_key_global = "أسماك_بادئ"
                    elif "نمو" in fst:
                        std_key_global = "أسماك_نمو"
                    else:
                        std_key_global = "أسماك_تسمين"

            # أرانب
            with a_tabs[8]:
                st.markdown("### 🐇 الأرانب")
                rt = st.selectbox(
                    "الحالة:", ["تسمين", "حليب", "صيانة"],
                    key="rabbit_t_v17")
                rwt = st.number_input("⚖️ الوزن:", 1.0, 8.0, 4.0, 0.5,
                                        key="rabbit_w_v17")
                rp = get_rabbit_requirements(rt, rwt)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_rabbit_v17"):
                    animal_choice = "أرانب"
                    production_type = rt
                    requirement = rp
                    std_key_global = f"أرانب_{rt}"

            ready = bool(animal_choice and requirement)

            if ready:
                st.markdown(f"""
                <div class="physio-card">
                    <h4>🧬 الحالة الفسيولوجية المعتمدة</h4>
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
                    "👤 اسم طالب العلفة:",
                    placeholder="مثال: مزرعة الأمل",
                    key="req_name_v17")

                st.markdown(
                    '<div class="section-title">🌾 اختيار المكونات</div>',
                    unsafe_allow_html=True)
                st.caption("⚠️ المواد المختارة فقط — لا إضافات تلقائية.")

                sq = st.text_input(
                    "🔍 بحث سريع:",
                    placeholder="مثال: ذرة، صويا...",
                    key="ing_search_v17")

                selected = []
                default_set = get_default_selections(
                    animal_choice, production_type, requirement)

                for cat_name, items in BIG_FEEDS_LIBRARY.items():
                    filt = ({k: v for k, v in items.items()
                             if sq.lower() in k.lower()}
                            if sq else items)
                    if not filt:
                        continue
                    expanded = ("الحبوب" in cat_name
                                 or "الأكساب" in cat_name
                                 or "الزيوت" in cat_name
                                 or "الأملاح" in cat_name)
                    with st.expander(
                            f"📁 {cat_name} ({len(filt)} مكون)",
                            expanded=expanded):
                        sc = st.columns(3)
                        for idx, ing_name in enumerate(filt.keys()):
                            with sc[idx % 3]:
                                dflt = ing_name in default_set
                                if st.checkbox(
                                        ing_name, value=dflt,
                                        key=f"pick_v17_{animal_choice}_{ing_name}"):
                                    selected.append(ing_name)

                st.markdown("### 💰 أسعار المواد المختارة")
                prices_dict = {}
                if selected:
                    pcols = st.columns(min(3, len(selected)))
                    for idx, ing in enumerate(selected):
                        with pcols[idx % 3]:
                            prices_dict[ing] = st.number_input(
                                f"💵 {ing} ($/طن)",
                                min_value=5.0,
                                value=float(live_prices.get(ing, 350.0)),
                                step=10.0,
                                key=f"p_v17_{animal_choice}_{ing}")

                st.success(f"✅ المختارة: **{len(selected)}** مادة")

                if st.button("🚀 تشغيل المحرك — ضمان جودة ≥ 70%",
                              type="primary", use_container_width=True,
                              key="run_btn_v17"):
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
                            st.session_state["last_formulation_result"] = result
                            st.session_state["last_formulation_context"] = {
                                "animal_choice": animal_choice,
                                "requirement_name": requirement.name_ar,
                                "basis_label": basis_code,
                                "requirement": requirement,
                                "custom_standard": custom_std,
                                "city": city,
                                "local_rate": local_rate,
                                "local_sym": local_sym,
                                "requester_name": requester_name,
                                "std_key_global": std_key_global,
                                "animal_type": animal_choice,
                                "production_type": production_type,
                            }
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")

                # ✅ v11.7 — عرض النتيجة + التحقق
                if st.session_state.get("last_formulation_result"):
                    result = st.session_state["last_formulation_result"]
                    ctx = st.session_state["last_formulation_context"]
                    formula = result["formula"]
                    actual = result["actual_nutrients"]
                    cost = result["cost"]
                    custom_std = ctx["custom_standard"]
                    quality = result.get("quality_score", 0.0)
                    meets = result.get("meets_standard", False)

                    # 🆕 التحقق من الحدود العالمية
                    validation = validate_feed_inputs(formula)
                    st.session_state["validation_cache"] = validation

                    if not validation["ok"]:
                        st.markdown("### 🚨 تحذيرات الحدود العالمية")
                        for err in validation["errors"]:
                            st.error(err)
                        for w in validation["warnings"]:
                            st.warning(w)

                        with st.expander("🔧 قبول التصحيح التلقائي",
                                          expanded=True):
                            st.markdown("**التركيبة المصححة:**")
                            for ing, pct in validation["corrected"].items():
                                orig = formula.get(ing, 0)
                                if abs(orig - pct) > 0.01:
                                    st.markdown(
                                        f"• {ing}: {orig:.2f}% → "
                                        f"**{pct:.2f}%**")
                                else:
                                    st.markdown(f"• {ing}: {pct:.2f}%")

                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button("✅ اعتماد المصحح",
                                              type="primary",
                                              use_container_width=True):
                                    result["formula"] = validation["corrected"]
                                    result["actual_nutrients"] = \
                                        compute_formula_nutrients(
                                            validation["corrected"])
                                    st.session_state[
                                        "last_formulation_result"] = result
                                    st.success("✅ تم اعتماد النسخة المصححة")
                                    st.rerun()
                            with col_b:
                                if st.button("📄 تقرير التحقق PDF",
                                              use_container_width=True):
                                    pdf_v = generate_validation_pdf_report(
                                        validation, formula)
                                    if pdf_v:
                                        st.download_button(
                                            "⬇️ تحميل",
                                            pdf_v,
                                            file_name=(f"Validation_"
                                                       f"{datetime.now():%Y%m%d}.pdf"),
                                            mime="application/pdf")
                    else:
                        st.success("✅ جميع المكونات داخل الحدود القياسية")

                    # عرض جودة
                    ca_p = (actual.get("Ca", 0) / actual.get("P", 1)
                            if actual.get("P", 0) > 0 else 0)
                    if meets:
                        st.markdown(f"""
                        <div class="quality-good-v113">
                        <h3 style="color:#1b5e20; margin:0;">
                        ✅ جودة الخلطة: {quality:.1f}%</h3>
                        <p style="color:#2e7d32; margin:6px 0 0 0;">
                        تجتاز 70% — Ca:P = {ca_p:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="quality-bad-v113">
                        <h3 style="color:#c62828; margin:0;">
                        ⚠️ جودة الخلطة: {quality:.1f}%</h3>
                        <p style="color:#b71c1c;">
                        أقل من 70% — تحتاج تعديلاً</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # جدول المقارنة
                    compare_rows = []
                    labels = {
                        "CP": "بروتين CP", "DP": "مهضوم DP",
                        "SE": "SE", "NDF": "NDF", "ADF": "ADF",
                        "EE": "دهن EE", "ASH": "رماد ASH",
                        "Ca": "Ca", "P": "P",
                    }
                    for k, sv in custom_std.items():
                        if sv == 0:
                            continue
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
                            "score": ev["score"],
                        })

                    st.markdown("### 📊 جدول المقارنة")
                    display_df = pd.DataFrame([
                        {k: v for k, v in r.items() if k != "score"}
                        for r in compare_rows])
                    st.dataframe(display_df, use_container_width=True,
                                  hide_index=True)

                    st.markdown("### 🌾 المكونات:")
                    for ing, pct in formula.items():
                        st.markdown(
                            f'<div class="formula-item">▪️ '
                            f'<b>{ing}:</b> {pct:.2f}% '
                            f'({pct*10:.1f} كجم/طن)</div>',
                            unsafe_allow_html=True)

                    st.metric("💰 التكلفة:", f"${cost:.2f}")

                    # رسوم
                    ch1, ch2 = st.columns(2)
                    with ch1:
                        bf = create_colorful_bar_chart(custom_std, actual)
                        if bf:
                            st.image(bf.getvalue(),
                                      caption="1️⃣ المقارنة",
                                      use_container_width=True)
                    with ch2:
                        pf = create_colorful_pie_chart(formula)
                        if pf:
                            st.image(pf.getvalue(),
                                      caption="2️⃣ التوزيع",
                                      use_container_width=True)

                    ch3, ch4 = st.columns(2)
                    with ch3:
                        rf = create_radar_chart(custom_std, actual)
                        if rf:
                            st.image(rf.getvalue(),
                                      caption="3️⃣ الرادار",
                                      use_container_width=True)
                    with ch4:
                        gf = create_gauge_chart(quality)
                        if gf:
                            st.image(gf.getvalue(),
                                      caption="4️⃣ الجودة",
                                      use_container_width=True)

                    # تحميل
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
                                file_name=(f"TaworNology_"
                                           f"{ctx['animal_type']}_"
                                           f"{datetime.now():%Y%m%d}.pdf"),
                                mime="application/pdf",
                                use_container_width=True)
                        except Exception as e:
                            st.error(f"⚠️ PDF: {e}")
                    with dl2:
                        try:
                            xl = export_comparison_to_excel(
                                custom_std, actual,
                                ctx["requester_name"],
                                ctx["animal_type"],
                                ctx["requirement_name"],
                                formula, ctx["std_key_global"])
                            if xl:
                                st.download_button(
                                    "📊 تحميل Excel", xl,
                                    file_name=(f"TaworNology_"
                                               f"{ctx['animal_type']}_"
                                               f"{datetime.now():%Y%m%d}.xlsx"),
                                    mime=("application/vnd.openxmlformats-"
                                          "officedocument.spreadsheetml.sheet"),
                                    use_container_width=True)
                        except Exception as e:
                            st.error(f"⚠️ Excel: {e}")

        with sub_a:
            st.markdown(
                '<div class="section-title">🔬 مختبر تحليل</div>',
                unsafe_allow_html=True)

            all_ings = list(_get_ingredient_lookup().keys())
            lab_cat = st.selectbox(
                "📁 التصنيف:",
                ["الكل"] + list(BIG_FEEDS_LIBRARY.keys()),
                key="lab_cat_v17")
            lab_search = st.text_input(
                "🔍 بحث:", key="lab_srch_v17",
                placeholder="اكتب اسم مادة...")

            if lab_cat == "الكل":
                pool = all_ings
            else:
                pool = list(BIG_FEEDS_LIBRARY[lab_cat].keys())
            if lab_search:
                pool = [x for x in pool if lab_search.lower() in x.lower()]

            lookup_lab = _get_ingredient_lookup()
            default_df = pd.DataFrame({
                "المادة": pool,
                "الوزن (كجم)": [0.0] * len(pool),
                "السعر ($/طن)": [
                    float(lookup_lab.get(m, {}).get("price", 300.0))
                    for m in pool],
            })

            edited = st.data_editor(
                default_df, use_container_width=True, hide_index=True,
                column_config={
                    "المادة": st.column_config.TextColumn(disabled=True),
                    "الوزن (كجم)": st.column_config.NumberColumn(
                        min_value=0.0, step=5.0, format="%.1f"),
                    "السعر ($/طن)": st.column_config.NumberColumn(
                        min_value=5.0, step=10.0, format="$%.0f"),
                },
                key="lab_editor_v17", num_rows="fixed")

            lab_in = {
                r["المادة"]: r["الوزن (كجم)"]
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
            else:
                st.info("💡 أدخل أوزان المواد — التحليل فوري")

    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 🌰 تبويب الزيوت
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["🌰 الزيوت"]:
    try:
        st.markdown(
            '<div class="section-title">🌰 مكتبة الزيوت</div>',
            unsafe_allow_html=True)
        st.write(f"{len(get_oil_ingredients())} زيتاً وفق NRC / INRA / Ross 308 / FAO.")

        st.markdown("### 📊 الحدود القياسية")
        oil_rows = [{
            "الحيوان": k,
            "أقصى %": f"{v['max']}%",
            "مثالي %": f"{v['optimal']}%",
            "المرجع": v["source"],
        } for k, v in MAX_OIL_PERCENTAGE.items()]
        st.dataframe(pd.DataFrame(oil_rows),
                      use_container_width=True, hide_index=True)

        st.markdown(f"### 🌰 الزيوت ({len(get_oil_ingredients())})")
        oils = get_oil_ingredients()

        oil_categories = {
            "أوميغا 6": ["زيت ذرة", "زيت عباد الشمس",
                          "زيت القرطم", "زيت فول الصويا"],
            "أوميغا 3": ["زيت الكتان", "زيت الكانولا",
                          "زيت السمك (Fish Oil)"],
            "متوازنة": ["زيت النخيل", "زيت جوز الهند",
                         "زيت الزيتون", "زيت السمسم",
                         "زيت الفول السوداني", "زيت الأفوكادو"],
        }

        for cat, oil_list in oil_categories.items():
            st.markdown(f"#### {cat}")
            for ing_name in oil_list:
                if ing_name not in oils:
                    continue
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
            '<div class="section-title">🍼 بدائل الحليب — ≥75%</div>',
            unsafe_allow_html=True)
        st.caption("⚠️ شرط: 3 مكونات كافية — 4 مفضّلة — 6 استراتيجيات")

        mr1, mr2 = st.columns(2)
        with mr1:
            mr_a = st.selectbox(
                "الحيوان:", list(MILK_REPLACER_STANDARDS.keys()),
                key="mr_a_v17")
            mr_v = st.number_input(
                "الكمية (كجم):", 1.0, 10000.0, 100.0, 10.0,
                key="mr_v_v17")
        with mr2:
            std_mr = MILK_REPLACER_STANDARDS[mr_a]
            st.markdown(f"""
            <div class="price-card">
            <b>📊 {mr_a}:</b><br>
            بروتين: {std_mr['CP']}% | دهن: {std_mr['Fat']}% |
            لاكتوز: {std_mr['Lactose']}%<br>
            Ca: {std_mr['Ca']}% | P: {std_mr['P']}%<br>
            <small>📖 {std_mr['source']}</small>
            </div>
            """, unsafe_allow_html=True)

        mr_sel = []
        cols = st.columns(3)
        for i, (name, data) in enumerate(MILK_REPLACER_INGREDIENTS.items()):
            with cols[i % 3]:
                with st.expander(f"{name}"):
                    st.caption(f"💵 ${data['price']}/كجم | "
                                f"حد أقصى: {data['max']}%")
                    if st.checkbox("إضافة", key=f"mr_v17_{name}"):
                        mr_sel.append(name)

        st.info(f"📊 المختارة: {len(mr_sel)} | الحد الأدنى: 3")

        if st.button("🧪 تركيب", type="primary", use_container_width=True):
            if len(mr_sel) < 3:
                st.warning("⚠️ اختر 3 مكونات على الأقل")
            else:
                with st.spinner("⏳ جاري التركيب..."):
                    r = formulate_milk_replacer(mr_a, mr_v, mr_sel)

                if r["success"]:
                    quality = r.get("quality_score", 0)
                    st.markdown(f"""
                    <div class="{'quality-good-v113' if quality >= 70 else 'quality-bad-v113'}">
                        <h3>جودة: {quality:.1f}% | Ca:P: {r['ca_p_ratio']:.2f}</h3>
                        <p>الاستراتيجية: <b>{r.get('strategy')}</b></p>
                    </div>
                    """, unsafe_allow_html=True)

                    if r.get("warning"):
                        st.warning(r["warning"])

                    st.markdown("### 🍼 المكونات:")
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
                            "📄 تحميل PDF شامل",
                            pdf_mr,
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
            '<div class="section-title">📷 المختبر الذكي OCR</div>',
            unsafe_allow_html=True)
        st.caption("📝 96 محاولة (8 معالجات × 3 لغات × 4 PSM)")

        if not OCR_AVAILABLE:
            st.error("⚠️ pytesseract أو opencv غير مثبتة")
        else:
            method = st.radio(
                "الإدخال:",
                ["📤 رفع صورة", "📸 كاميرا"],
                horizontal=True, key="ocr_method_v17")

            uploaded = None
            if "رفع" in method:
                up = st.file_uploader(
                    "ارفع الصورة:",
                    type=["jpg", "jpeg", "png"], key="ocr_upload_v17")
                if up:
                    uploaded = up.read()
            else:
                cam = st.camera_input(
                    "التقط الصورة", key="ocr_camera_v17")
                if cam:
                    uploaded = cam.read()

            if uploaded:
                st.image(uploaded, caption="الصورة",
                          use_container_width=True)

                if st.button("🔍 تحليل", type="primary",
                               use_container_width=True):
                    with st.spinner("🔬 جاري التحليل..."):
                        result = extract_ingredients_from_image(uploaded)

                    if result["success"] and result["count"] > 0:
                        st.success(
                            f"✅ {result['count']} مادة | "
                            f"جودة: {result.get('quality', '—')} | "
                            f"{result.get('variants_tried', 0)} محاولة")

                        nut = compute_formula_nutrients(
                            result["ingredients"])

                        st.dataframe(
                            pd.DataFrame([{
                                "المادة": k, "النسبة": v,
                            } for k, v in result["ingredients"].items()]),
                            use_container_width=True, hide_index=True)

                        n1, n2, n3, n4 = st.columns(4)
                        n1.metric("CP", f"{nut['CP']:.2f}%")
                        n2.metric("DP", f"{nut['DP']:.2f}%")
                        n3.metric("SE", f"{nut['SE']:.1f}")
                        n4.metric("NDF", f"{nut['NDF']:.2f}%")

                        with st.expander("✏️ تصحيح يدوي", expanded=True):
                            corrected = render_ocr_correction_ui(
                                result["ingredients"])
                            if st.button("✅ تطبيق التصحيح",
                                          type="primary",
                                          use_container_width=True):
                                if corrected:
                                    st.session_state["last_ocr_result"] = \
                                        corrected
                                    st.success("✅ تم التصحيح")
                                    st.rerun()

                        try:
                            pdf_ocr = pdf_gen.generate_ocr_report(
                                result["ingredients"], nut,
                                raw_text=result.get("raw_text", ""))
                            st.download_button(
                                "📄 تحميل PDF", pdf_ocr,
                                file_name=(f"OCR_{datetime.now():%Y%m%d}"
                                           f".pdf"),
                                mime="application/pdf",
                                use_container_width=True)
                        except Exception as e:
                            st.error(f"⚠️ {e}")
                    else:
                        st.warning(f"⚠️ {result.get('message', 'لم يتم')}")
    except Exception as e:
        st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 🏗️ الحظائر 3D — v11.7 (بسيط/احترافي + ساحات)
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["🏗️ الحظائر 3D"]:
    try:
        st.markdown(
            '<div class="section-title">🏗️ مصمم الحظائر 3D</div>',
            unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            barn_a = st.selectbox(
                "🐾 الحيوان:",
                list(BARN_DESIGN_STANDARDS.keys()),
                format_func=lambda k: BARN_DESIGN_STANDARDS[k]["name_ar"],
                key="barn_animal_v17")
        with c2:
            barn_c = st.number_input(
                "🔢 العدد:", 1, 100000, 1000, 50,
                key="barn_count_v17")
        with c3:
            barn_n_pens = st.number_input(
                "🔲 عدد الساحات:", 1, 20, 4, 1, key="barn_pens_v17")
        with c4:
            pens_row = st.number_input(
                "🔳 ساحات بالصف:", 1, 6, 2, 1, key="barn_pens_row_v17")

        # وضع العرض
        view_mode = st.radio(
            "👁️ وضع العرض:",
            ["🟢 بسيط (للجميع)", "🔬 احترافي (للمختص)"],
            horizontal=True, key="barn_view_mode_v17")
        expert = "احترافي" in view_mode

        # الأسطورة (احترافي)
        if expert:
            st.markdown("""
            <div style="display:flex; gap:20px; padding:12px;
                 background:#f5f5f5; border-radius:10px;
                 direction:rtl; justify-content:center;
                 margin-bottom:15px; font-size:0.9rem;">
            <span><span style="display:inline-block;width:16px;
            height:16px;background:#43a047;border-radius:3px;
            border:2px solid #1a1a1a;"></span> سليم</span>
            <span><span style="display:inline-block;width:16px;
            height:16px;background:#fbc02d;border-radius:3px;
            border:2px solid #1a1a1a;"></span> قريب من الطاقة</span>
            <span><span style="display:inline-block;width:16px;
            height:16px;background:#e53935;border-radius:3px;
            border:2px solid #1a1a1a;"></span> مزدحم</span>
            <span><span style="display:inline-block;width:16px;
            height:16px;background:#9e9e9e;border-radius:3px;
            border:2px solid #1a1a1a;"></span> فارغ</span>
            </div>
            """, unsafe_allow_html=True)

        dims = calculate_barn_dimensions(barn_a, barn_c)
        if dims:
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("📏 المساحة", f"{dims['total_area_m2']} م²")
            k2.metric("📐 الأبعاد",
                       f"{dims['length_m']}×{dims['width_m']} م")
            k3.metric("🏔️ القمة", f"{dims['ridge_height_m']} م")
            k4.metric("👥 سعة/ساحة",
                       f"{barn_c // barn_n_pens} رأس")

            # المجسم
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

            # GIF
            st.markdown("### 🎬 فيديو GIF")
            if st.button("🎬 توليد الفيديو", use_container_width=True):
                with st.spinner("🎥 جاري التوليد..."):
                    vb = create_barn_animation_gif(
                        dims, frames=20, fps=8)
                if vb:
                    st.session_state["barn_video_gif"] = vb.getvalue()
                    st.success("✅ تم!")
                else:
                    st.error("⚠️ تعذر التوليد")

            if st.session_state.get("barn_video_gif"):
                st.image(st.session_state["barn_video_gif"],
                          use_container_width=True)

            # PDF
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


# ═══════════════════════════════════════════════════════════════════════════
# 📊 الجدوى
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["📊 الجدوى"]:
    try:
        st.markdown(
            '<div class="section-title">📊 دراسة الجدوى</div>',
            unsafe_allow_html=True)

        mode = st.radio(
            "🎯 النوع:",
            ["🔬 فنية", "💰 اقتصادية", "📈 شاملة (+ Monte Carlo)"],
            horizontal=True, key="feas_mode_v17")

        f1, f2 = st.columns(2)
        with f1:
            feas_k = st.selectbox(
                "نوع الحيوان:",
                list(BARN_DESIGN_STANDARDS.keys()),
                format_func=lambda k: BARN_DESIGN_STANDARDS[k]["name_ar"],
                key="feas_animal_v17")
            feas_c = st.number_input(
                "العدد:", 1, 100000, 1000, 50, key="feas_count_v17")
            proj_name = st.text_input(
                "اسم المشروع:", key="feas_proj_v17")
        with f2:
            feas_r = st.text_input("مقدم الطلب:", key="feas_req_v17")
            if "اقتصادية" in mode or "شاملة" in mode:
                fp = st.number_input(
                    "💵 سعر العلف ($/طن):",
                    50.0, 5000.0, 350.0, 10.0, key="feas_fp_v17")
                pp = st.number_input(
                    "💵 سعر المنتج ($/وحدة):",
                    0.1, 10000.0, 2.5, 0.1, key="feas_pp_v17")
                lc = st.number_input(
                    "👷 تكلفة العامل ($/شهر):",
                    0.0, 10000.0, 200.0, 10.0, key="feas_lc_v17")
                oc = st.number_input(
                    "📊 أخرى ($/شهر):",
                    0.0, 100000.0, 300.0, 50.0, key="feas_oc_v17")

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
                feed_yr_ton = feas["feed"]["total_year_ton"]
                feed_cost = feed_yr_ton * fp
                labor_yr = feas["labor"]["workers"] * lc * 12
                other_yr = oc * 12
                total_cost = feed_cost + labor_yr + other_yr

                prod = feas["production"]
                ann_units = prod.get("annual", 0)
                annual_rev = ann_units * pp
                profit = annual_rev - total_cost
                roi = (profit / total_cost * 100 if total_cost > 0 else 0)
                be = (total_cost / pp if pp > 0 else 0)
                margin = (profit / annual_rev * 100
                          if annual_rev > 0 else 0)

                e1, e2, e3, e4 = st.columns(4)
                e1.metric("💵 تكلفة", f"${total_cost:,.0f}")
                e2.metric("💰 إيراد", f"${annual_rev:,.0f}")
                e3.metric("📈 ربح", f"${profit:,.0f}",
                            delta=f"{roi:+.1f}%")
                e4.metric("🎯 التعادل", f"{be:,.0f}")

                if profit > 0:
                    st.success(f"✅ مجدٍ — ربح ${profit:,.0f}/سنة "
                                f"(هامش {margin:.1f}%)")
                else:
                    st.error(f"❌ غير مجدٍ — خسارة ${abs(profit):,.0f}")

            if "شاملة" in mode and annual_rev > 0:
                st.markdown("### 🎲 Monte Carlo (1000 سيناريو)")
                random.seed() if not st.checkbox(
                    "🎲 ثابت", False, key="mc_seed_v17") else random.seed(42)

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
                        "📥 تحميل كتيّب الجدوى",
                        booklet,
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
            '<div class="section-title">🐔 إدارة المزارع</div>',
            unsafe_allow_html=True)

        farms = st.session_state["broiler_farms"]
        sub_f1, sub_f2 = st.tabs(["➕ جديدة", "📊 المتابعة"])

        with sub_f1:
            with st.form("new_farm_v17"):
                c1, c2 = st.columns(2)
                with c1:
                    nf_name = st.text_input("اسم المزرعة *")
                    nf_strain = st.selectbox(
                        "السلالة",
                        ["Ross 308", "Cobb 500", "Hubbard", "Avian"])
                    nf_birds = st.number_input(
                        "عدد الطيور", 100, 100000, 1000, 50)
                with c2:
                    nf_date = st.date_input("تاريخ الإدخال")
                    nf_house = st.text_input("رقم العنبر")
                    nf_notes = st.text_area("ملاحظات")
                if st.form_submit_button("💾 حفظ", type="primary",
                                          use_container_width=True) and nf_name:
                    if nf_name in farms:
                        st.warning("⚠️ الاسم مستخدم")
                    else:
                        farms[nf_name] = {
                            "strain": nf_strain,
                            "start_birds": nf_birds,
                            "start_date": str(nf_date),
                            "house": nf_house,
                            "notes": nf_notes,
                            "records": [],
                        }
                        st.success(f"✅ {nf_name} محفوظة")
                        st.rerun()

        with sub_f2:
            if not farms:
                st.info("💡 لا مزارع — أضف واحدة")
            else:
                sel = st.selectbox(
                    "اختر مزرعة:", list(farms.keys()),
                    key="farm_sel_v17")
                farm = farms[sel]

                with st.form(f"rec_v17_{sel}"):
                    st.markdown(f"### 📝 قراءة — {farm['strain']}")
                    rc = st.columns(5)
                    with rc[0]:
                        age = st.number_input("العمر", 1, 60, 1)
                    with rc[1]:
                        alive = st.number_input(
                            "الحية", 1, farm["start_birds"],
                            value=farm["start_birds"])
                    with rc[2]:
                        wt = st.number_input("الوزن (كجم)",
                                              0.01, 5.0, 0.045, 0.005)
                    with rc[3]:
                        feed = st.number_input("علف/طير (كجم)",
                                                0.0, 20.0, 0.0, 0.05)
                    with rc[4]:
                        temp = st.number_input("حرارة", 15.0, 45.0, 30.0, 0.5)
                    if st.form_submit_button("➕ تسجيل", type="primary",
                                              use_container_width=True):
                        farm["records"].append({
                            "date": str(datetime.now().date()),
                            "age": age, "alive": alive,
                            "wt": wt, "feed": feed, "temp": temp,
                        })
                        st.success("✅ تم")
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

                    std = BROILER_STANDARDS.get(latest["age"], (0, 0, 0, 0))
                    std_wt, std_fcr, std_feed, std_mort = std

                    m = st.columns(5)
                    m[0].metric("🐦 حيوية", f"{liv:.1f}%")
                    m[1].metric("📈 ADG", f"{adg:.1f} g/d")
                    m[2].metric("⚖️ الوزن", f"{latest['wt']:.3f} كجم",
                                  delta=(f"{(latest['wt'] - std_wt):+.3f}"
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
                            else "🟢 آمن"),
            } for name in inv.keys()])

            edited = st.data_editor(
                inv_df, use_container_width=True, hide_index=True,
                column_config={
                    "المادة": st.column_config.TextColumn(disabled=True),
                    "الكمية (طن)": st.column_config.NumberColumn(
                        min_value=0.0, step=1.0),
                    "الحد الأدنى": st.column_config.NumberColumn(
                        min_value=0.0, step=1.0),
                    "الحالة": st.column_config.TextColumn(disabled=True),
                },
                key="inv_editor_v17")

            if st.button("💾 حفظ التغييرات", type="primary",
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
                with st.form("invoice_v17"):
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
                    rows = [
                        {"البند": k, "الكمية (طن)": 1.0,
                         "سعر الطن": float(v * 10)}
                        for k, v in active.items()
                    ] or [{"البند": "", "الكمية (طن)": 0.0,
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
                                    format="$%.2f"),
                        }, key="inv_items_v17")

                    subtotal = sum(r["الكمية (طن)"] * r["سعر الطن"]
                                    for _, r in items_df.iterrows())
                    tax_amt = subtotal * tax / 100
                    total = subtotal + tax_amt

                    st.metric("المجموع", f"${subtotal:,.2f}")
                    st.metric("الإجمالي", f"${total:,.2f}")

                    if st.form_submit_button("✅ إصدار", type="primary",
                                              use_container_width=True):
                        if not client or subtotal <= 0:
                            st.error("⚠️ املأ العميل والبنود")
                        else:
                            inv_num = len(
                                st.session_state["invoices"]) + 1
                            invoice = {
                                "number": (f"INV-{datetime.now():%Y%m}-"
                                           f"{inv_num:04d}"),
                                "date": str(inv_date),
                                "client": client,
                                "phone": phone,
                                "items": items_df.to_dict("records"),
                                "subtotal": subtotal,
                                "tax": tax,
                                "tax_amt": tax_amt,
                                "total": total,
                            }
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
                        "الإجمالي": f"${i['total']:,.2f}",
                    } for i in invoices])
                    st.dataframe(summary, use_container_width=True,
                                  hide_index=True)

                    sel_num = st.selectbox(
                        "اختر فاتورة:", [i["number"] for i in invoices],
                        key="inv_sel_v17")
                    selected_inv = next(
                        i for i in invoices if i["number"] == sel_num)

                    if st.button("📄 PDF", type="primary",
                                   use_container_width=True):
                        if _guard_sensitive_operation("delete_invoice"):
                            pdf_bytes = generate_invoice_pdf(selected_inv)
                            if pdf_bytes:
                                st.download_button(
                                    "⬇️ تحميل", pdf_bytes,
                                    file_name=(f"{selected_inv['number']}.pdf"),
                                    mime="application/pdf",
                                    use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ {e}")

    with tab_map["🖨️ الديباجة"]:
        try:
            st.markdown(
                '<div class="section-title">🖨️ الديباجة</div>',
                unsafe_allow_html=True)
            title_line = st.text_input("العنوان:", value=APP_NAME)
            sub_line = st.text_input("الفرعي:", value=APP_TAGLINE)

            if st.button("📄 تنزيل", type="primary",
                          use_container_width=True):
                try:
                    pdf_data = generate_letterhead_pdf(title_line, sub_line)
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
                       len(st.session_state.get("formulation_history", [])))
            m2.metric("📷 OCR",
                       1 if st.session_state.get("last_ocr_result") else 0)
            m3.metric("🐔 مزارع",
                       len(st.session_state.get("broiler_farms", {})))
            m4.metric("🧾 فواتير",
                       len(st.session_state.get("invoices", [])))

            active = st.session_state.get("active_formula", {})
            if active and PLOTLY_AVAILABLE:
                df = pd.DataFrame({
                    "المادة": list(active.keys()),
                    "النسبة %": list(active.values()),
                })
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
            st.markdown(f"### 📜 ({len(comments)} تعليق)")
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
                    if st.button("🗑️", key=f"del_c_v17_{i}"):
                        if _guard_sensitive_operation("delete_comment"):
                            comments.pop(i)
                            SharedStorage._save(
                                {"shared_comments": "\n".join(comments)})
                            st.session_state["comments_list"] = comments
                            st.rerun()

            new_comment = st.text_area("اكتب:", key="cm_new_v17")
            if st.button("➕ نشر", type="primary",
                          use_container_width=True):
                if new_comment.strip():
                    line = (f"• [{datetime.now():%Y-%m-%d %H:%M}]: "
                            f"{new_comment.strip()}")
                    comments.append(line)
                    SharedStorage._save(
                        {"shared_comments": "\n".join(comments)})
                    st.session_state["comments_list"] = comments
                    st.success("✅ تم")
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
- **Carroll & Huntington (1988)** — Weight Estimation of Horses
- **Schaeffer (1971)** — Cattle Weight from Tape
- **Danø & Højsgaard (2005)** — LP in Ration Formulation
- **Waldron et al. (2018)** — Milk Replacer Formulation
- **AAFCO (2020)** — Feed Standards
- **MWPS-1** — Structures Handbook

### 🏗️ تصميم الحظائر:
- MWPS-1 — Structures Handbook
- FAO 2012 — Rural Structures

### 🍼 بدائل الحليب:
- NRC (2001) — Calf Nutrition
- AAFCO — Nutrient Profiles
    """)


with tab_map["💡 المساعدة"]:
    st.markdown(
        '<div class="section-title">💡 المساعدة</div>',
        unsafe_allow_html=True)
    st.markdown(f"""
### الأسئلة الشائعة:

**1. كيف أبدأ؟**
- اختر الحيوان → فعّل ✅ → اختر 3+ مكونات → 🚀

**2. القياسات (جديد v11.7)؟**
- شريط حول الصدر + طول الجسم
- 5 حيوانات (أبقار/أغنام/ماعز/إبل/خيول)
- الوزن التقديري + العلف اليومي تلقائياً

**3. الحدود العالمية (جديد v11.7)؟**
- المركزات: **5% أو 10% فقط**
- ملح الطعام: ≤ 0.5%
- اليوريا: ≤ 1.5% للمجترات فقط
- تصحيح تلقائي عند التجاوز

**4. بدائل الحليب؟**
- 3 مكونات كافية، 4 مثالية، 6 استراتيجيات

**5. OCR؟**
- 96 محاولة (8 معالجات × 3 لغات × 4 PSM)

**6. الحظائر 3D؟**
- وضع بسيط (رقم + عدد)
- وضع احترافي (+ كثافة + سعة + إطارات)

**7. Monte Carlo؟**
- 1000 سيناريو احتمالي

**8. الأمان؟**
- fail-closed (يجب ضبط OWNER_CODE)
- قفل تصاعدي (5د/30د/24س)

### 🔧 الدعم
📧 {OWNER_EMAIL}
📱 {WHATSAPP_NUMBER}

{DUA_FULL}
    """)


with tab_map["📖 الدليل"]:
    st.markdown(
        '<div class="section-title">📖 دليل المستخدم</div>',
        unsafe_allow_html=True)
    st.markdown(f"""
### 🎯 الغرض
**{APP_NAME} v{APP_VERSION}** — منصة ذكية لتركيب الأعلاف.

### ✨ ميزات v11.7:
- 🔐 **أمان fail-closed** — لا كود في المصدر
- 🔐 **قفل تصاعدي** — 3/6/9 محاولات
- 📏 **تبويب القياسات** — 5 حيوانات + علف يومي
- 🍽️ **حساب DMI** — تلقائياً من الوزن والحالة
- 🔒 **حدود عالمية صارمة** — مركزات 5%/10% فقط
- 🔧 **تصحيح تلقائي** — عند تجاوز أي حد
- 🏗️ **حظائر 3D بوضعين** — بسيط/احترافي + ساحات
- 📄 **PDFs جديدة** — علف + تحقق
- 🍼 **بدائل حليب** — 6 استراتيجيات
- 📷 **OCR** — 96 محاولة

### 🔐 الدخول
- 👑 **مالك:** يجب ضبط `OWNER_CODE` في secrets
- 👥 **زائر:** دخول مجاني بميزات كاملة

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
# نهاية الملف — Tawor Nology v11.7
# ═══════════════════════════════════════════════════════════════════════════

print(f"\n{'='*70}")
print(f"✅ {APP_NAME} v{APP_VERSION} جاهز للتشغيل")
print(f"{'='*70}")
print(f"⚠️ قبل التشغيل — أنشئ .streamlit/secrets.toml:")
print(f"   OWNER_CODE = \"كودك-السري\"")
print(f"{'='*70}")
