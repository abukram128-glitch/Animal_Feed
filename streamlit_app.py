# ═══════════════════════════════════════════════════════════════════════
# تاور نولجي TAWOR NOLOGY 11.11
# د. عبدالقادر إسماعيل تاور
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
# ═══════════════════════════════════════════════════════════════════════
# المميزات:
#   ✅ 12 تركيبة مرجعية معتمدة NRC
#   ✅ محرك LP محصّن + Validator
#   ✅ رفض أي تركيبة فيها بروتين > طاقة
#   ✅ فيديو تعريفي تلقائي
#   ✅ تقييد PDF للمالك فقط
#   ✅ صور قياس على الحيوانات
#   ✅ حظيرة خيل 3D كاملة
# ═══════════════════════════════════════════════════════════════════════

import streamlit as st
import numpy as np, pandas as pd, io, os, re, base64
import traceback, warnings, json, hashlib, base64
import time as _time
from datetime import datetime
from functools import lru_cache
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple, Any

# ─── المكتبات الاختيارية ───
try:
    from scipy.optimize import linprog, minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    linprog = None
    minimize = None

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Wedge, Ellipse
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor, white
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                     Table, TableStyle, Image as RLImage,
                                     PageBreak, HRFlowable)
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_AVAILABLE = True
except ImportError:
    ARABIC_AVAILABLE = False

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════
# الثوابت
# ═══════════════════════════════════════════════════════════════════════

APP_NAME = "تاور نولجي Tawor Nology"
APP_VERSION = "11.11"
SUPERVISOR = "د. عبدالقادر إسماعيل تاور"
SUPERVISOR_TITLE = "اختصاصي تغذية الحيوان"
WHATSAPP_NUMBER = "+249123533489"
OWNER_EMAIL = "abukram128@gmail.com"
PLATFORM_URL = "https://tawor-nology.streamlit.app"

DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي ابتسام"
DUA_FULL = "رحم الله والدي إسماعيل تاور وأختي ابتسام وأسكنهما فسيح جناته"

st.set_page_config(
    page_title=APP_NAME, page_icon="🌾",
    layout="wide", initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════
# الخطوط العربية
# ═══════════════════════════════════════════════════════════════════════

@lru_cache(maxsize=1)
def init_arabic_font():
    if not REPORTLAB_AVAILABLE:
        return 'Helvetica'
    try:
        os.makedirs("fonts", exist_ok=True)
        candidates = ["fonts/Amiri-Regular.ttf", "Amiri-Regular.ttf"]
        for p in candidates:
            if os.path.exists(p):
                pdfmetrics.registerFont(TTFont('TaworArabic', p))
                return 'TaworArabic'
        # محاولة تحميل الخط
        try:
            import urllib.request
            url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
            target = "fonts/Amiri-Regular.ttf"
            urllib.request.urlretrieve(url, target)
            pdfmetrics.registerFont(TTFont('TaworArabic', target))
            return 'TaworArabic'
        except Exception:
            pass
    except Exception:
        pass
    return 'Helvetica'

FONT_NAME = init_arabic_font()

@lru_cache(maxsize=2000)
def ar(text):
    if not text:
        return ""
    if not ARABIC_AVAILABLE:
        return str(text)
    try:
        return get_display(arabic_reshaper.reshape(str(text)), base_dir='R')
    except Exception:
        return str(text)

# ═══════════════════════════════════════════════════════════════════════
# 🔐 الأمان
# ═══════════════════════════════════════════════════════════════════════

def _sha256(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def _get_owner_hash():
    try:
        # base64 لعام 202687
        blob = "Nzg2MjAy"
        code = base64.b64decode(blob).decode()[::-1]
        return _sha256(code)
    except Exception:
        return None

def check_owner_code(user_input):
    if not user_input:
        return False
    expected = _get_owner_hash()
    if not expected:
        return False
    return _sha256(user_input.strip()) == expected

# ═══════════════════════════════════════════════════════════════════════
# 📚 المكتبة العلفية (مع الخميرة وعلف الدجاج الجاهز)
# ═══════════════════════════════════════════════════════════════════════

def _feed(cp, dc, se, ndf, adf, ee, ash, ca, p, lys, met, price, desc, src):
    return {
        "CP": cp, "DC": dc, "SE": se, "NDF": ndf, "ADF": adf,
        "EE": ee, "ASH": ash, "Ca": ca, "P": p,
        "Lys": lys, "Met": met, "price": price,
        "desc": desc, "src": src
    }

FEED_LIBRARY = {
    "🌾 الحبوب (الطاقة)": {
        "ذرة صفراء": _feed(8.5, 0.85, 80, 9.5, 3.2, 3.8, 1.3, 0.02, 0.27, 0.24, 0.17, 230, "الطاقة الرئيسية", "NRC 2012"),
        "ذرة بيضاء": _feed(8.8, 0.83, 78, 10.2, 3.5, 3.5, 1.4, 0.02, 0.26, 0.25, 0.18, 225, "بديل محلي", "NRC 2012"),
        "شعير مطحون": _feed(11.5, 0.80, 71, 18.5, 7.5, 2.2, 2.5, 0.05, 0.35, 0.42, 0.20, 210, "للمجترات", "NRC 2012"),
        "قمح محلي": _feed(12.0, 0.85, 75, 11.5, 3.8, 2.0, 1.6, 0.04, 0.32, 0.35, 0.20, 240, "طاقة جيدة", "NRC 2012"),
        "جريش أرز": _feed(7.8, 0.82, 82, 5.5, 2.5, 8.5, 4.2, 0.06, 0.30, 0.28, 0.18, 240, "طاقة عالية", "NRC 2012"),
        "شوفان علفي": _feed(11.0, 0.76, 62, 27.5, 13.5, 5.0, 3.0, 0.08, 0.35, 0.40, 0.18, 260, "للخيول", "NRC 2007"),
        "دخن محلي": _feed(11.0, 0.75, 68, 15.5, 6.5, 4.0, 2.2, 0.05, 0.31, 0.28, 0.20, 220, "بديل", "NRC 2012"),
    },
    "🌱 البروتين (الأكساب)": {
        "كسب فول صويا 44%": _feed(44.0, 0.90, 74, 13.5, 8.0, 1.8, 6.0, 0.35, 0.65, 2.70, 0.60, 440, "رئيسي", "NRC 2012"),
        "كسب فول صويا 48%": _feed(48.0, 0.91, 76, 12.0, 7.0, 1.5, 6.2, 0.35, 0.65, 3.00, 0.68, 480, "مرتفع", "NRC 2012"),
        "كسب عباد الشمس 36%": _feed(36.0, 0.76, 42, 38.5, 25.5, 2.5, 6.5, 0.40, 1.00, 1.20, 0.70, 310, "اقتصادي", "NRC 2012"),
        "كسب عباد الشمس 32%": _feed(32.0, 0.72, 38, 42.0, 28.0, 2.0, 7.0, 0.42, 0.95, 1.10, 0.65, 290, "اقتصادي", "NRC 2012"),
        "كسب بذور القطن": _feed(41.0, 0.78, 55, 24.5, 15.5, 1.2, 6.5, 0.20, 1.10, 1.80, 0.60, 290, "مع جوسيبول", "NRC 2012"),
        "كسب الكتان": _feed(32.0, 0.82, 65, 18.5, 10.5, 2.8, 5.8, 0.35, 0.85, 1.20, 0.55, 340, "أوميغا 3", "NRC 2007"),
        "كسب السمسم": _feed(42.0, 0.84, 70, 14.5, 9.5, 8.5, 12.5, 2.00, 1.20, 1.30, 1.00, 520, "غني Ca", "NRC 2007"),
        "كسب الكانولا": _feed(36.0, 0.82, 60, 28.0, 18.0, 3.5, 6.5, 0.65, 1.10, 1.90, 0.70, 400, "متوازن", "NRC 2012"),
        "كسب جلوتين 60%": _feed(60.0, 0.92, 85, 8.5, 5.5, 2.5, 3.5, 0.15, 0.50, 1.10, 1.80, 520, "Met عالي", "NRC 2012"),
        "فول صويا كامل": _feed(38.0, 0.85, 78, 15.0, 10.0, 18.0, 4.5, 0.25, 0.55, 2.50, 0.55, 420, "معالجة حرارية", "NRC 2012"),
        "بازلاء علفية": _feed(22.0, 0.82, 70, 15.0, 8.0, 1.5, 3.0, 0.10, 0.40, 1.50, 0.25, 320, "متوازن", "NRC 2012"),
        "خميرة الخبز (مفعلة)": _feed(45.0, 0.80, 60, 12.0, 6.0, 2.0, 8.5, 0.20, 1.20, 3.00, 0.80, 500, "بروتين ميكروبي", "FAO 2010"),
    },
    "🧬 البروتين الحيواني": {
        "مسحوق أسماك 60%": _feed(60.0, 0.85, 65, 2.5, 1.5, 8.5, 22.5, 5.50, 3.20, 4.50, 1.80, 850, "ممتاز", "NRC 2012"),
        "مسحوق أسماك 72%": _feed(72.0, 0.90, 72, 2.0, 1.0, 9.5, 18.5, 4.80, 2.80, 5.50, 2.20, 1100, "مرتفع جداً", "NRC 2012"),
        "مسحوق اللحم والعظم": _feed(50.0, 0.75, 50, 3.5, 2.5, 10.5, 32.5, 9.00, 4.50, 2.50, 0.70, 620, "Ca + P", "NRC 2012"),
        "مسحوق الدم": _feed(80.0, 0.65, 55, 1.0, 0.5, 1.5, 6.0, 0.30, 0.30, 7.00, 1.00, 780, "هضم منخفض", "NRC 2012"),
        "مسحوق ريش": _feed(82.0, 0.70, 60, 1.5, 1.0, 3.0, 4.0, 0.25, 0.35, 2.00, 0.50, 650, "معالجة", "NRC 2012"),
        "حشرات مجففة BSF": _feed(42.0, 0.80, 68, 8.0, 5.0, 35.0, 8.0, 0.80, 0.90, 2.60, 0.85, 1800, "مستدام", "FAO 2013"),
    },
    "🚜 المخلفات والألياف": {
        "نخالة قمح (ردة)": _feed(15.0, 0.72, 45, 35.5, 12.5, 3.5, 5.5, 0.12, 1.10, 0.60, 0.25, 150, "اقتصادية", "NRC 2001"),
        "نخالة ذرة": _feed(9.5, 0.65, 40, 40.0, 15.0, 4.0, 2.0, 0.10, 0.75, 0.30, 0.15, 140, "اقتصادية", "NRC 2001"),
        "البرسيم الجاف": _feed(16.5, 0.60, 35, 42.5, 32.5, 2.0, 10.5, 1.50, 0.25, 0.85, 0.25, 170, "بروتين + ألياف", "NRC 2001"),
        "برسيم حجازي": _feed(18.0, 0.62, 38, 40.0, 30.0, 2.2, 11.0, 1.60, 0.26, 0.90, 0.28, 175, "أفضل برسيم", "NRC 2001"),
        "تبن قمح": _feed(3.2, 0.35, 18, 72.5, 45.5, 1.5, 8.5, 0.30, 0.08, 0.15, 0.05, 80, "حشو فقط", "NRC 2001"),
        "تبن فول": _feed(4.5, 0.40, 22, 68.0, 42.0, 1.2, 7.5, 0.35, 0.10, 0.18, 0.08, 90, "أفضل من تبن القمح", "NRC 2001"),
        "قش أرز": _feed(3.5, 0.30, 15, 70.0, 45.0, 1.5, 12.0, 0.20, 0.06, 0.12, 0.05, 65, "حشو فقط", "NRC 2007"),
        "سعف نخيل مطحون": _feed(4.0, 0.30, 20, 65.0, 42.0, 2.0, 7.0, 0.35, 0.08, 0.15, 0.06, 55, "ألياف", "FAO 2010"),
        "مخلفات النخيل": _feed(6.5, 0.70, 60, 25.0, 15.0, 5.0, 3.5, 0.15, 0.15, 0.25, 0.10, 100, "للإبل", "FAO 2010"),
        "مولاس قصب السكر": _feed(4.0, 0.95, 50, 1.5, 0.8, 0.5, 8.5, 0.70, 0.05, 0.03, 0.02, 120, "طاقة سريعة", "NRC 2001"),
    },
    "🌰 الزيوت": {
        "زيت ذرة": _feed(0, 0, 220, 0, 0, 100, 0, 0, 0, 0, 0, 1500, "أوميغا 6", "NRC 2012"),
        "زيت فول الصويا": _feed(0, 0, 215, 0, 0, 100, 0, 0, 0, 0, 0, 1350, "متوازن", "Ross 308"),
        "زيت عباد الشمس": _feed(0, 0, 210, 0, 0, 100, 0, 0, 0, 0, 0, 1300, "أوميغا 6", "NRC 2007"),
        "زيت الكتان": _feed(0, 0, 205, 0, 0, 100, 0, 0, 0, 0, 0, 1700, "أوميغا 3", "NRC 2007"),
        "زيت جوز الهند": _feed(0, 0, 230, 0, 0, 100, 0, 0, 0, 0, 0, 1900, "MCT", "NRC 2012"),
        "زيت النخيل": _feed(0, 0, 215, 0, 0, 100, 0, 0, 0, 0, 0, 1100, "مقاوم للأكسدة", "NRC 2012"),
        "شحم حيواني Tallow": _feed(0, 0, 230, 0, 0, 100, 0, 0, 0, 0, 0, 900, "طاقة رخيصة", "NRC 2012"),
        "زيت السمك": _feed(0, 0, 235, 0, 0, 100, 0, 0, 0, 0, 0, 3800, "EPA + DHA", "NRC Fish"),
    },
    "🐔 الأعلاف الجاهزة": {
        "علف دجاج جاهز - بادي": _feed(23.0, 0.88, 76, 8.0, 4.0, 5.0, 6.5, 1.00, 0.50, 1.40, 0.55, 400, "جاهز للاستخدام", "Ross 308"),
        "علف دجاج جاهز - نامي": _feed(21.0, 0.87, 74, 9.0, 5.0, 5.0, 6.0, 0.90, 0.45, 1.25, 0.50, 380, "جاهز للاستخدام", "Ross 308"),
        "علف دجاج جاهز - ناهي": _feed(19.5, 0.86, 75, 10.0, 5.5, 4.5, 6.0, 0.87, 0.43, 1.10, 0.48, 370, "جاهز للاستخدام", "Ross 308"),
        "علف دجاج بياض جاهز": _feed(18.0, 0.85, 72, 11.0, 6.0, 4.2, 11.5, 3.80, 0.45, 0.90, 0.42, 390, "جاهز للاستخدام", "NRC 1994"),
        "علف أبقار جاهز": _feed(16.0, 0.82, 68, 32.0, 20.0, 4.0, 8.0, 0.80, 0.40, 0.70, 0.25, 320, "جاهز للاستخدام", "NRC 2001"),
        "علف أغنام جاهز": _feed(14.0, 0.80, 65, 35.0, 22.0, 3.5, 8.0, 0.75, 0.35, 0.65, 0.22, 300, "جاهز للاستخدام", "NRC 2007"),
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": _feed(94.0, 1.0, 0, 0, 0, 0, 0.5, 0, 0, 94.0, 0, 4200, "أساسي", "NRC 2012"),
        "ميثيونين نقي": _feed(58.0, 1.0, 0, 0, 0, 0, 0.3, 0, 0, 0, 58.0, 5800, "للدواجن", "NRC 2012"),
        "ثريونين نقي": _feed(72.0, 1.0, 0, 0, 0, 0, 0.2, 0, 0, 0, 0, 4800, "ثالث محدود", "NRC 2012"),
    },
    "🔬 الإضافات": {
        "بريمكس تسمين دواجن": _feed(0, 0, 0, 0, 0, 0, 100, 18.0, 8.0, 0, 0, 4800, "فيتامينات + معادن", "NRC 1994"),
        "بريمكس بياض": _feed(0, 0, 0, 0, 0, 0, 100, 22.0, 7.0, 0, 0, 5000, "للبياض", "NRC 1994"),
        "بريمكس أبقار": _feed(0, 0, 0, 0, 0, 0, 100, 20.0, 10.0, 0, 0, 5200, "للأبقار", "NRC 2001"),
        "بريمكس مجترات": _feed(0, 0, 0, 0, 0, 0, 100, 18.0, 9.0, 0, 0, 4500, "للأغنام والماعز", "NRC 2007"),
        "بريمكس خيول": _feed(0, 0, 0, 0, 0, 0, 100, 15.0, 8.0, 0, 0, 5500, "للخيول", "NRC 2007"),
        "بريمكس إبل": _feed(0, 0, 0, 0, 0, 0, 100, 20.0, 10.0, 0, 0, 5300, "للإبل", "FAO 2010"),
        "بريمكس أسماك": _feed(0, 0, 0, 0, 0, 0, 100, 15.0, 7.0, 0, 0, 5800, "للأسماك", "NRC Fish"),
        "إنزيم فايتيز": _feed(0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 4200, "تحرير P", "NRC 2012"),
        "خمائر حية": _feed(45.0, 0.75, 30, 8.0, 4.0, 1.0, 8.0, 0.15, 1.20, 3.00, 0.70, 8500, "للمجترات", "NRC 2001"),
    },
    "🪨 الأملاح": {
        "الحجر الجيري": _feed(0, 0, 0, 0, 0, 0, 99.5, 38.0, 0, 0, 0, 40, "مصدر Ca", "NRC 2012"),
        "فوسفات ثنائي الكالسيوم": _feed(0, 0, 0, 0, 0, 0, 98.5, 23.0, 18.0, 0, 0, 280, "Ca + P", "NRC 2012"),
        "فوسفات أحادي الكالسيوم": _feed(0, 0, 0, 0, 0, 0, 99, 17.0, 22.0, 0, 0, 320, "مصدر P", "NRC 2012"),
        "ملح الطعام": _feed(0, 0, 0, 0, 0, 0, 99.9, 0, 0, 0, 0, 30, "NaCl", "NRC 2012"),
        "بيكربونات الصوديوم": _feed(0, 0, 0, 0, 0, 0, 99, 0, 0, 0, 0, 340, "مضاد حموضة", "NRC 2001"),
        "أكسيد المغنيسيوم": _feed(0, 0, 0, 0, 0, 0, 99.5, 0, 0, 0, 0, 480, "Mg", "NRC 2007"),
        "يوريا علفية": _feed(287, 0.95, 0, 0, 0, 0, 1, 0, 0, 0, 0, 480, "NPN للمجترات فقط", "NRC 2001"),
        "مضاد سموم فطرية": _feed(0, 0, 0, 0, 0, 0, 85, 0, 0, 0, 0, 950, "أفلاتوكسين", "NRC 2012"),
    },
}

def get_ingredient_lookup():
    if not hasattr(get_ingredient_lookup, "_cache"):
        lookup = {}
        for cat in FEED_LIBRARY.values():
            for name, data in cat.items():
                lookup[name] = data
        get_ingredient_lookup._cache = lookup
    return get_ingredient_lookup._cache

def get_oil_ingredients():
    return FEED_LIBRARY.get("🌰 الزيوت", {})

# ═══════════════════════════════════════════════════════════════════════
# 🎯 التركيبات المرجعية (12 تركيبة معتمدة NRC)
# ═══════════════════════════════════════════════════════════════════════

REFERENCE_FORMULATIONS = {
    # ═══════ أبقار ═══════
    "أبقار_حليب_عالي": {
        "name": "بقرة حلابة عالية (20 لتر)",
        "animal": "أبقار",
        "targets": {"CP": 17.5, "DP": 12.5, "SE": 65, "Ca": 0.65, "P": 0.36},
        "reference_recipe": {
            "ذرة صفراء": 35.0,
            "شعير مطحون": 15.0,
            "كسب فول صويا 44%": 18.0,
            "نخالة قمح (ردة)": 12.0,
            "البرسيم الجاف": 15.0,
            "الحجر الجيري": 1.5,
            "فوسفات ثنائي الكالسيوم": 1.0,
            "ملح الطعام": 0.5,
            "بيكربونات الصوديوم": 0.7,
            "بريمكس أبقار": 0.3,
        },
        "rationale": "ذرة + شعير كمصدر طاقة أساسي (50%)، صويا + برسيم للبروتين (33%)، أملاح ومضافات (4%)",
        "expected_output": {"CP": 17.3, "DP": 12.4, "SE": 63, "Ca": 0.75, "P": 0.38},
        "source": "NRC 2001 — Table 15-1",
    },
    "أبقار_حليب_متوسط": {
        "name": "بقرة حلابة متوسطة (15 لتر)",
        "animal": "أبقار",
        "targets": {"CP": 15.5, "DP": 11.0, "SE": 60, "Ca": 0.60, "P": 0.32},
        "reference_recipe": {
            "ذرة صفراء": 38.0,
            "شعير مطحون": 18.0,
            "كسب فول صويا 44%": 12.0,
            "نخالة قمح (ردة)": 15.0,
            "البرسيم الجاف": 12.0,
            "الحجر الجيري": 1.5,
            "فوسفات ثنائي الكالسيوم": 0.8,
            "ملح الطعام": 0.5,
            "بريمكس أبقار": 0.2,
        },
        "rationale": "زيادة الطاقة، تقليل البروتين المكلف",
        "expected_output": {"CP": 15.2, "DP": 11.2, "SE": 62, "Ca": 0.68, "P": 0.35},
        "source": "NRC 2001 — Table 15-1",
    },
    "أبقار_تسمين_مكثف": {
        "name": "تسمين عجول مكثف (ADG >1.3)",
        "animal": "أبقار",
        "targets": {"CP": 14.5, "DP": 11.5, "SE": 72, "Ca": 0.65, "P": 0.38},
        "reference_recipe": {
            "ذرة صفراء": 55.0,
            "شعير مطحون": 20.0,
            "كسب فول صويا 44%": 10.0,
            "نخالة قمح (ردة)": 8.0,
            "البرسيم الجاف": 4.0,
            "الحجر الجيري": 1.5,
            "فوسفات ثنائي الكالسيوم": 0.8,
            "ملح الطعام": 0.5,
            "بريمكس أبقار": 0.2,
        },
        "rationale": "طاقة عالية (75%) للوصول إلى ADG > 1.3 كجم",
        "expected_output": {"CP": 14.3, "DP": 11.4, "SE": 71, "Ca": 0.70, "P": 0.40},
        "source": "NRC 1996 — Table 10-1",
    },
    # ═══════ أغنام ═══════
    "أغنام_تسمين_مكثف": {
        "name": "تسمين حملان مكثف (ADG >250 جم)",
        "animal": "أغنام",
        "targets": {"CP": 14.5, "DP": 11.5, "SE": 64, "Ca": 0.65, "P": 0.36},
        "reference_recipe": {
            "ذرة صفراء": 45.0,
            "شعير مطحون": 20.0,
            "كسب فول صويا 44%": 12.0,
            "نخالة قمح (ردة)": 12.0,
            "البرسيم الجاف": 8.0,
            "الحجر الجيري": 1.2,
            "فوسفات ثنائي الكالسيوم": 0.8,
            "ملح الطعام": 0.5,
            "بريمكس مجترات": 0.3,
            "بيكربونات الصوديوم": 0.2,
        },
        "rationale": "65% طاقة، 20% بروتين، 8% ألياف",
        "expected_output": {"CP": 14.3, "DP": 11.4, "SE": 63, "Ca": 0.70, "P": 0.38},
        "source": "NRC 2007 — Table 11-1",
    },
    "أغنام_مرضعات": {
        "name": "نعاج مرضعات (مولود واحد)",
        "animal": "أغنام",
        "targets": {"CP": 14.5, "DP": 10.5, "SE": 62, "Ca": 0.65, "P": 0.38},
        "reference_recipe": {
            "ذرة صفراء": 35.0,
            "شعير مطحون": 18.0,
            "كسب فول صويا 44%": 15.0,
            "نخالة قمح (ردة)": 12.0,
            "البرسيم الجاف": 17.0,
            "الحجر الجيري": 1.5,
            "فوسفات ثنائي الكالسيوم": 0.8,
            "ملح الطعام": 0.4,
            "بريمكس مجترات": 0.3,
        },
        "rationale": "بروتين أعلى للرضاعة + ألياف للهضم",
        "expected_output": {"CP": 14.7, "DP": 10.7, "SE": 60, "Ca": 0.75, "P": 0.40},
        "source": "NRC 2007 — Table 11-2",
    },
    # ═══════ ماعز ═══════
    "ماعز_حلابة_عالي": {
        "name": "عنزات حلابة عالية (2 لتر)",
        "animal": "ماعز",
        "targets": {"CP": 14.2, "DP": 10.2, "SE": 60, "Ca": 0.65, "P": 0.35},
        "reference_recipe": {
            "ذرة صفراء": 30.0,
            "شعير مطحون": 20.0,
            "كسب فول صويا 44%": 14.0,
            "نخالة قمح (ردة)": 13.0,
            "البرسيم الجاف": 20.0,
            "الحجر الجيري": 1.3,
            "فوسفات ثنائي الكالسيوم": 0.8,
            "ملح الطعام": 0.5,
            "بريمكس مجترات": 0.4,
        },
        "rationale": "22% ألياف مهمة للماعز + بروتين متوسط",
        "expected_output": {"CP": 14.0, "DP": 10.1, "SE": 58, "Ca": 0.72, "P": 0.38},
        "source": "NRC 2007 — Table 12-1",
    },
    # ═══════ دواجن ═══════
    "دواجن_لاحم_بادي": {
        "name": "دواجن لاحم - بادي (أسبوع 1)",
        "animal": "دواجن",
        "targets": {"CP": 23.0, "DP": 20.0, "SE": 76, "Ca": 1.0, "P": 0.50},
        "reference_recipe": {
            "ذرة صفراء": 52.0,
            "كسب فول صويا 48%": 36.0,
            "زيت فول الصويا": 3.5,
            "الحجر الجيري": 1.2,
            "فوسفات ثنائي الكالسيوم": 1.8,
            "ملح الطعام": 0.3,
            "بريمكس تسمين دواجن": 0.3,
            "ليسين نقي": 0.25,
            "ميثيونين نقي": 0.15,
        },
        "rationale": "طاقة عالية + بروتين 23% + توازن الأحماض الأمينية",
        "expected_output": {"CP": 22.8, "DP": 20.2, "SE": 75, "Ca": 1.05, "P": 0.52},
        "source": "Ross 308 (2020) — Starter",
    },
    "دواجن_لاحم_ناهي": {
        "name": "دواجن لاحم - ناهي (أسبوع 5+)",
        "animal": "دواجن",
        "targets": {"CP": 19.5, "DP": 17.0, "SE": 75, "Ca": 0.87, "P": 0.43},
        "reference_recipe": {
            "ذرة صفراء": 58.0,
            "كسب فول صويا 48%": 30.0,
            "زيت فول الصويا": 4.0,
            "الحجر الجيري": 1.0,
            "فوسفات ثنائي الكالسيوم": 1.5,
            "ملح الطعام": 0.3,
            "بريمكس تسمين دواجن": 0.3,
            "ليسين نقي": 0.18,
            "ميثيونين نقي": 0.12,
        },
        "rationale": "طاقة أعلى، بروتين أقل تدريجياً",
        "expected_output": {"CP": 19.3, "DP": 17.1, "SE": 76, "Ca": 0.90, "P": 0.44},
        "source": "Ross 308 (2020) — Finisher",
    },
    "دواجن_بياض": {
        "name": "دواجن بياض (إنتاجي)",
        "animal": "دواجن",
        "targets": {"CP": 18.0, "DP": 15.5, "SE": 72, "Ca": 3.8, "P": 0.45},
        "reference_recipe": {
            "ذرة صفراء": 58.0,
            "كسب فول صويا 44%": 22.0,
            "نخالة قمح (ردة)": 6.0,
            "الحجر الجيري": 9.0,
            "فوسفات ثنائي الكالسيوم": 1.8,
            "ملح الطعام": 0.3,
            "بريمكس بياض": 0.3,
            "ميثيونين نقي": 0.12,
        },
        "rationale": "Ca عالٍ جداً لبناء قشر البيض (9% حجر جيري)",
        "expected_output": {"CP": 18.2, "DP": 15.6, "SE": 71, "Ca": 3.85, "P": 0.48},
        "source": "NRC 1994 — Table 4",
    },
    # ═══════ أسماك ═══════
    "أسماك_نمو": {
        "name": "أسماك - نمو (بلطي)",
        "animal": "أسماك",
        "targets": {"CP": 32.0, "DP": 25.0, "SE": 70, "Ca": 1.0, "P": 0.70},
        "reference_recipe": {
            "كسب فول صويا 44%": 42.0,
            "مسحوق أسماك 60%": 22.0,
            "قمح محلي": 25.0,
            "زيت السمك": 5.0,
            "فوسفات ثنائي الكالسيوم": 2.0,
            "بريمكس أسماك": 0.5,
            "ملح الطعام": 0.3,
            "فيتامين C": 0.2,
        },
        "rationale": "بروتين حيواني عالٍ ضروري للأسماك",
        "expected_output": {"CP": 32.5, "DP": 26.2, "SE": 72, "Ca": 1.15, "P": 0.82},
        "source": "NRC 2011 — Table 6-2",
    },
    # ═══════ أرانب ═══════
    "أرانب_تسمين": {
        "name": "أرانب تسمين",
        "animal": "أرانب",
        "targets": {"CP": 17.0, "DP": 15.0, "SE": 65, "Ca": 0.70, "P": 0.35},
        "reference_recipe": {
            "برسيم حجازي": 35.0,
            "شعير مطحون": 28.0,
            "كسب فول صويا 44%": 14.0,
            "نخالة قمح (ردة)": 15.0,
            "ذرة صفراء": 4.0,
            "الحجر الجيري": 1.5,
            "فوسفات ثنائي الكالسيوم": 0.8,
            "ملح الطعام": 0.5,
            "بريمكس مجترات": 0.3,
            "مضاد سموم فطرية": 0.1,
        },
        "rationale": "ألياف عالية (برسيم) ضرورية للأرانب",
        "expected_output": {"CP": 17.2, "DP": 15.1, "SE": 63, "Ca": 0.78, "P": 0.40},
        "source": "NRC 2007 — Rabbit Chapter",
    },
    # ═══════ إبل ═══════
    "إبل_حليب": {
        "name": "إبل حلابة (5 لتر)",
        "animal": "إبل",
        "targets": {"CP": 16.0, "DP": 11.5, "SE": 64, "Ca": 0.70, "P": 0.40},
        "reference_recipe": {
            "ذرة صفراء": 25.0,
            "شعير مطحون": 25.0,
            "كسب فول صويا 44%": 15.0,
            "نخالة قمح (ردة)": 10.0,
            "البرسيم الجاف": 15.0,
            "مخلفات النخيل": 7.0,
            "الحجر الجيري": 1.5,
            "فوسفات ثنائي الكالسيوم": 0.8,
            "ملح الطعام": 0.5,
            "بريمكس إبل": 0.3,
        },
        "rationale": "توازن خاص للإبل مع مخلفات النخيل",
        "expected_output": {"CP": 16.2, "DP": 11.6, "SE": 62, "Ca": 0.78, "P": 0.42},
        "source": "FAO 2010 — Section 4",
    },
    # ═══════ خيول ═══════
    "خيول_رياضة_عادي": {
        "name": "خيول رياضة (عمل متوسط)",
        "animal": "خيول",
        "targets": {"CP": 11.5, "DP": 9.0, "SE": 63, "Ca": 0.55, "P": 0.32},
        "reference_recipe": {
            "شوفان علفي": 30.0,
            "شعير مطحون": 25.0,
            "ذرة صفراء": 10.0,
            "كسب فول صويا 44%": 8.0,
            "البرسيم الجاف": 25.0,
            "الحجر الجيري": 1.2,
            "فوسفات ثنائي الكالسيوم": 0.6,
            "ملح الطعام": 0.5,
            "بريمكس خيول": 0.3,
        },
        "rationale": "الشوفان أساسي للخيول (طاقة + ألياف)",
        "expected_output": {"CP": 11.4, "DP": 8.9, "SE": 62, "Ca": 0.62, "P": 0.35},
        "source": "NRC 2007 — Table 10-1",
    },
}

def get_reference(key):
    return REFERENCE_FORMULATIONS.get(key)

def list_references():
    return [(k, v["name"], v["animal"]) for k, v in REFERENCE_FORMULATIONS.items()]

# ═══════════════════════════════════════════════════════════════════════
# حساب العناصر الغذائية
# ═══════════════════════════════════════════════════════════════════════

def compute_nutrients(formula):
    totals = {k: 0.0 for k in ["CP", "DP", "SE", "NDF", "ADF", "EE",
                                "ASH", "Ca", "P", "Lys", "Met"]}
    lookup = get_ingredient_lookup()
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

def compute_cost(formula, prices):
    total = 0.0
    lookup = get_ingredient_lookup()
    for ing, pct in formula.items():
        price = prices.get(ing, lookup.get(ing, {}).get("price", 300))
        total += pct / 100.0 * price
    return total

# ═══════════════════════════════════════════════════════════════════════
# تقييم الجودة
# ═══════════════════════════════════════════════════════════════════════

def evaluate_diff(pct_diff):
    a = abs(pct_diff)
    if a <= 2: return {"label": "🎯 مطابق", "bg": "#c8e6c9", "score": 100}
    if a <= 5: return {"label": "✅ جيد جداً", "bg": "#dcedc8", "score": 90}
    if a <= 10: return {"label": "🟢 جيد", "bg": "#e8f5e9", "score": 78}
    if a <= 15: return {"label": "⭐ مقبول", "bg": "#fff8e1", "score": 65}
    if a <= 25: return {"label": "⚠️ بتحفظ", "bg": "#fff3e0", "score": 50}
    if a <= 40: return {"label": "🟠 ضعيف", "bg": "#ffe0b2", "score": 35}
    return {"label": "❌ مرفوض", "bg": "#ffebee", "score": 15}

def evaluate_quality(formula, targets):
    actual = compute_nutrients(formula)
    weights = {"CP": 0.30, "SE": 0.20, "Ca": 0.15, "P": 0.15}
    if targets.get("DP"): weights["DP"] = 0.20
    total_w = 0.0
    weighted = 0.0
    for k, w in weights.items():
        if not targets.get(k):
            continue
        diff = abs(actual.get(k, 0) - targets[k]) / targets[k] * 100
        ev = evaluate_diff(diff)
        weighted += ev["score"] * w
        total_w += w
    if total_w == 0:
        return 0, actual
    return weighted / total_w, actual

# ═══════════════════════════════════════════════════════════════════════
# 🚨 Validator — فحص أي تركيبة ضد المرجع
# ═══════════════════════════════════════════════════════════════════════

def validate_against_reference(formula, ref_key):
    """يرفض أي تركيبة تبعد أكثر من 30% عن التركيبة المرجعية"""
    ref = get_reference(ref_key)
    if not ref:
        return {"valid": True, "reason": "لا يوجد مرجع للمقارنة"}
    
    actual = compute_nutrients(formula)
    expected = ref["expected_output"]
    
    issues = []
    for k, expected_val in expected.items():
        if expected_val == 0:
            continue
        actual_val = actual.get(k, 0)
        diff_pct = abs(actual_val - expected_val) / expected_val * 100
        if diff_pct > 30:
            issues.append(
                f"❌ {k}: المحسوب {actual_val:.2f} vs المرجع {expected_val:.2f} "
                f"(انحراف {diff_pct:.0f}%)"
            )
    
    # فحص إضافي: بروتين لا يتجاوز طاقة
    if actual.get("CP", 0) > actual.get("SE", 0):
        issues.append(
            f"🚨 خطأ فادح: البروتين ({actual['CP']:.1f}%) أعلى من الطاقة ({actual['SE']:.1f}%)"
        )
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "actual": actual,
        "expected": expected,
    }

# ═══════════════════════════════════════════════════════════════════════
# 🧮 محرك LP محصّن
# ═══════════════════════════════════════════════════════════════════════

def formulate_lp(selected_ingredients, prices, targets, animal_type=""):
    """
    محرك البرمجة الخطية مع 10 مستويات تراجع + Validator
    يعيد التركيبة أو يرفض إذا فشلت كل المستويات
    """
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "SCIPY غير متوفرة"}
    
    valid = [i for i in selected_ingredients if i in get_ingredient_lookup()]
    if len(valid) < 3:
        return {"success": False, "message": "اختر 3 مكونات على الأقل"}
    
    lookup = get_ingredient_lookup()
    n = len(valid)
    c = [prices.get(i, lookup[i].get("price", 300)) for i in valid]
    
    cp = [lookup[i].get("CP", 0) for i in valid]
    se = [lookup[i].get("SE", 0) for i in valid]
    ca = [lookup[i].get("Ca", 0) for i in valid]
    p = [lookup[i].get("P", 0) for i in valid]
    
    target_cp = targets.get("CP", 16)
    target_se = targets.get("SE", 60)
    target_ca = targets.get("Ca", 0.65)
    target_p = targets.get("P", 0.35)
    
    # تصنيف المصادر
    energy_idx = [i for i in range(n) if se[i] > 40 and cp[i] < 20]
    protein_idx = [i for i in range(n) if cp[i] >= 20]
    
    # الحدود
    bounds = []
    for i, ing in enumerate(valid):
        if "ملح" in ing or "حجر" in ing or "فوسفات" in ing:
            bounds.append((0.2, 3.0))
        elif "بريمكس" in ing or "مضاد" in ing:
            bounds.append((0.05, 1.0))
        elif ing in get_oil_ingredients():
            bounds.append((0, 6))
        else:
            bounds.append((1.0, 60.0))
    
    strategies = [
        ("صارم 100%", 1.00),
        ("خفيف 97%", 0.97),
        ("مرن 95%", 0.95),
        ("مرن 92%", 0.92),
        ("مرن 90%", 0.90),
        ("مرن 85%", 0.85),
        ("مرن 80%", 0.80),
        ("مرن 75%", 0.75),
        ("طوارئ 70%", 0.70),
        ("طوارئ 65%", 0.65),
    ]
    
    best = None
    attempts = []
    
    for label, mult in strategies:
        try:
            A_eq = [[1.0] * n]
            b_eq = [100.0]
            
            A_ub = []
            b_ub = []
            
            # قيد البروتين (≥ target × mult)
            A_ub.append([-x for x in cp])
            b_ub.append(-target_cp * mult)
            
            # قيد الطاقة (≥ target × mult)
            A_ub.append([-x for x in se])
            b_ub.append(-target_se * mult)
            
            # توازن: طاقة ≥ بروتين + 5
            if energy_idx and protein_idx:
                bal = [0.0] * n
                for i in energy_idx: bal[i] = 1.0
                for i in protein_idx: bal[i] = -1.0
                A_ub.append([-x for x in bal])
                b_ub.append(-5.0)
            
            # 40% حد أدنى من الطاقة
            if energy_idx:
                e_row = [1.0 if i in energy_idx else 0.0 for i in range(n)]
                A_ub.append([-x for x in e_row])
                b_ub.append(-40.0)
            
            # 40% حد أقصى من البروتين
            if protein_idx:
                p_row = [1.0 if i in protein_idx else 0.0 for i in range(n)]
                A_ub.append(p_row)
                b_ub.append(40.0)
            
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                bounds=bounds, method='highs',
                options={'presolve': True, 'time_limit': 15})
            
            if res.success:
                formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.1}
                q, actual = evaluate_quality(formula, targets)
                attempts.append(f"✅ {label}: جودة {q:.1f}%")
                
                if best is None or q > best["quality"]:
                    best = {
                        "formula": formula,
                        "quality": q,
                        "actual": actual,
                        "cost": res.fun / 100.0,
                        "strategy": label,
                        "mult": mult,
                    }
                
                if q >= 90:
                    break
            else:
                attempts.append(f"❌ {label}: تعذر الحل")
        except Exception as e:
            attempts.append(f"⚠️ {label}: {str(e)[:50]}")
    
    if best:
        return {
            "success": True,
            "formula": best["formula"],
            "quality": best["quality"],
            "actual": best["actual"],
            "cost": best["cost"],
            "strategy": best["strategy"],
            "attempts": attempts,
        }
    
    return {
        "success": False,
        "message": "لم يُوجد حل يلبي جميع القيود",
        "attempts": attempts,
        "suggestion": "استخدم التركيبة المرجعية أو أضف مكونات متنوعة",
    }

# ═══════════════════════════════════════════════════════════════════════
# قياس الوزن (صور + أسهم)
# ═══════════════════════════════════════════════════════════════════════

WEIGHT_TAPE = {
    "أبقار": {"hg": (100, 260, 180), "bl": (100, 220, 150),
              "formula": lambda h, b: (h**2 * b) / 10840,
              "source": "Schaeffer (1978)"},
    "أغنام": {"hg": (40, 120, 75), "bl": (40, 100, 65),
              "formula": lambda h, b: (h**2 * b) / 10840,
              "source": "Schaeffer (1978)"},
    "ماعز": {"hg": (35, 110, 70), "bl": (35, 95, 62),
             "formula": lambda h, b: (h**2 * b) / 10840,
             "source": "Schaeffer (1978)"},
    "إبل": {"hg": (130, 280, 210), "bl": (100, 220, 155),
            "formula": lambda h, b: (h**2 * b) / 11880,
            "source": "FAO Camel (2010)"},
    "خيول": {"hg": (120, 240, 175), "bl": (100, 210, 155),
             "formula": lambda h, b: (h**2 * b) / 11877,
             "source": "Carroll (1988)"},
}

ANIMAL_IMAGES = {
    "أبقار": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Cow_female_black_white.jpg/1024px-Cow_female_black_white.jpg",
    "أغنام": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Sheep_in_lesser_himalayas.JPG/1024px-Sheep_in_lesser_himalayas.JPG",
    "ماعز": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Goat_chewing_a_can_%28cropped%29.jpg/1024px-Goat_chewing_a_can_%28cropped%29.jpg",
    "إبل": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Camel_in_Dubai.jpg/1024px-Camel_in_Dubai.jpg",
    "خيول": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Nokota_Horses_cropped.jpg/1024px-Nokota_Horses_cropped.jpg",
}

@st.cache_data(ttl=86400)
def load_image(url):
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()
    except Exception:
        return None

def render_weight_guide(animal):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        img_bytes = load_image(ANIMAL_IMAGES.get(animal, ANIMAL_IMAGES["أبقار"]))
        fig, ax = plt.subplots(figsize=(10, 6))
        if img_bytes:
            img = Image.open(io.BytesIO(img_bytes))
            ax.imshow(img)
        else:
            ax.text(0.5, 0.5, f"📸 {animal}", ha='center', va='center',
                    fontsize=30, transform=ax.transAxes, color='#1b5e20')
        ax.axis('off')
        
        # أسهم القياس
        ax.annotate('', xy=(0.35, 0.65), xytext=(0.35, 0.32),
                    xycoords='axes fraction', textcoords='axes fraction',
                    arrowprops=dict(arrowstyle='<->', color='#c62828',
                                     lw=4, mutation_scale=20))
        ax.text(0.37, 0.48, '① محيط الصدر', color='#c62828',
                fontweight='bold', fontsize=13, transform=ax.transAxes,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor='#c62828', alpha=0.9))
        
        ax.annotate('', xy=(0.15, 0.22), xytext=(0.85, 0.22),
                    xycoords='axes fraction', textcoords='axes fraction',
                    arrowprops=dict(arrowstyle='<->', color='#1565c0',
                                     lw=4, mutation_scale=20))
        ax.text(0.5, 0.24, '② طول الجسم', color='#1565c0', ha='center',
                fontweight='bold', fontsize=13, transform=ax.transAxes,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor='#1565c0', alpha=0.9))
        
        cfg = WEIGHT_TAPE.get(animal, {})
        ax.set_title(f"📍 {animal} — {cfg.get('source', '')}",
                     fontsize=14, fontweight='bold', color='#1b5e20', pad=12)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white', pad_inches=0.15)
        plt.close(); buf.seek(0)
        return buf
    except Exception:
        return None

# ═══════════════════════════════════════════════════════════════════════
# 🏗️ حظيرة الخيل 3D (إسطبلات كاملة)
# ═══════════════════════════════════════════════════════════════════════

def build_horse_barn_3d(num_horses=10):
    if not PLOTLY_AVAILABLE:
        return None
    try:
        stall_w = 3.5
        stall_l = 3.5
        aisle_w = 3.5
        rows = 2 if num_horses > 4 else 1
        per_row = (num_horses + 1) // 2 if rows == 2 else num_horses
        
        L = per_row * stall_w + 2
        W = rows * stall_l + aisle_w + 1
        H = 4.0
        wall_h = 3.0
        
        fig = go.Figure()
        
        # الأرضية
        fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[0,0,W,W], z=[0,0,0,0],
            i=[0,0], j=[1,2], k=[2,3],
            color='#d7ccc8', opacity=0.7, name='الأرضية', hoverinfo='skip'))
        
        # الجدران الخارجية
        for xp in [0, L]:
            fig.add_trace(go.Mesh3d(x=[xp]*4, y=[0,W,W,0], z=[0,0,H,H],
                i=[0,0], j=[1,2], k=[2,3],
                color='#a1887f', opacity=0.25, showlegend=False, hoverinfo='skip'))
        for yp in [0, W]:
            fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[yp]*4, z=[0,0,H,H],
                i=[0,0], j=[1,2], k=[2,3],
                color='#a1887f', opacity=0.25, showlegend=False, hoverinfo='skip'))
        
        # السقف
        fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[0,0,W/2,W/2],
            z=[H,H,H+1.5,H+1.5], i=[0,0], j=[1,2], k=[2,3],
            color='#8d6e63', opacity=0.5, name='السقف', hoverinfo='skip'))
        fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[W/2,W/2,W,W],
            z=[H+1.5,H+1.5,H,H], i=[0,0], j=[1,2], k=[2,3],
            color='#8d6e63', opacity=0.5, showlegend=False, hoverinfo='skip'))
        
        # بناء الإسطبلات
        for row in range(rows):
            y_start = 0.5 if row == 0 else W - stall_l - 0.5
            for col in range(per_row):
                x_start = 0.5 + col * stall_w
                
                # جدار أمامي بفتحة باب
                y_front = y_start if row == 0 else y_start + stall_l
                fig.add_trace(go.Mesh3d(
                    x=[x_start, x_start+0.4, x_start+0.4, x_start],
                    y=[y_front]*4, z=[0,0,wall_h,wall_h],
                    i=[0,0], j=[1,2], k=[2,3],
                    color='#8d6e63', opacity=0.5,
                    showlegend=False, hoverinfo='skip'))
                fig.add_trace(go.Mesh3d(
                    x=[x_start+stall_w-0.4, x_start+stall_w,
                       x_start+stall_w, x_start+stall_w-0.4],
                    y=[y_front]*4, z=[0,0,wall_h,wall_h],
                    i=[0,0], j=[1,2], k=[2,3],
                    color='#8d6e63', opacity=0.5,
                    showlegend=False, hoverinfo='skip'))
                # علوي
                fig.add_trace(go.Mesh3d(
                    x=[x_start, x_start+stall_w, x_start+stall_w, x_start],
                    y=[y_front]*4, z=[H*0.5, H*0.5, wall_h, wall_h],
                    i=[0,0], j=[1,2], k=[2,3],
                    color='#8d6e63', opacity=0.5,
                    showlegend=False, hoverinfo='skip'))
                
                # جدار جانبي أيمن
                fig.add_trace(go.Mesh3d(
                    x=[x_start+stall_w]*4,
                    y=[y_start, y_start+stall_l, y_start+stall_l, y_start],
                    z=[0,0,wall_h,wall_h], i=[0,0], j=[1,2], k=[2,3],
                    color='#795548', opacity=0.4,
                    showlegend=False, hoverinfo='skip'))
                
                # حصان
                fig.add_trace(go.Scatter3d(
                    x=[x_start+stall_w/2], y=[y_start+stall_l/2], z=[0.4],
                    mode='markers',
                    marker=dict(size=14, color='#4e342e', symbol='diamond',
                                line=dict(color='#d4af37', width=2)),
                    name='حصان' if row==0 and col==0 else None,
                    showlegend=(row==0 and col==0)))
                
                # رقم الإسطبل
                fig.add_trace(go.Scatter3d(
                    x=[x_start+stall_w/2], y=[y_front], z=[wall_h+0.3],
                    mode='text', text=[f"{col+1+row*per_row}"],
                    textfont=dict(size=11, color='#c62828'),
                    showlegend=False))
        
        # الممر
        aisle_y = stall_l + 0.5 if rows == 2 else W/2 - 0.25
        fig.add_trace(go.Scatter3d(
            x=[0, L, L, 0], y=[aisle_y]*4, z=[0.01]*4,
            mode='lines', line=dict(color='#ffeb3b', width=10),
            name='الممر الرئيسي', hoverinfo='skip'))
        
        fig.update_layout(
            title=dict(
                text=f"🐎 إسطبل خيول 3D — {num_horses} حصان | "
                     f"{L:.1f}×{W:.1f} م",
                font=dict(size=14, color='#1b5e20'), x=0.5),
            scene=dict(
                xaxis=dict(title='الطول', range=[-0.5, L+0.5]),
                yaxis=dict(title='العرض', range=[-0.5, W+0.5]),
                zaxis=dict(title='الارتفاع', range=[0, H+2]),
                aspectmode='manual',
                aspectratio=dict(x=L/12, y=W/12, z=(H+2)/12),
                camera=dict(eye=dict(x=1.5, y=-1.5, z=1.0))),
            height=650, paper_bgcolor='white',
            legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.9)'))
        return fig
    except Exception:
        return None

# ═══════════════════════════════════════════════════════════════════════
# 📄 PDF Generator
# ═══════════════════════════════════════════════════════════════════════

def generate_pdf(formula, targets, animal, reference_key=""):
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
            rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []
        
        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(ar(text), ParagraphStyle(
                'style', fontName=FONT_NAME, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))
        
        def _draw_page(canvas_obj, doc):
            canvas_obj.saveState()
            w, h = doc.pagesize
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, h-90, w, 90, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.rect(0, h-95, w, 5, fill=1, stroke=0)
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(FONT_NAME, 20)
            canvas_obj.drawCentredString(w/2, h-40, ar(APP_NAME))
            canvas_obj.setFont(FONT_NAME, 11)
            canvas_obj.setFillColor(HexColor('#e8f5e9'))
            canvas_obj.drawCentredString(w/2, h-62, ar(SUPERVISOR))
            canvas_obj.setFont(FONT_NAME, 10)
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.drawCentredString(w/2, h-78, ar(SUPERVISOR_TITLE))
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, 42, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#ffeb3b'))
            canvas_obj.setFont(FONT_NAME, 11)
            canvas_obj.drawCentredString(w/2, 62, ar(f"🤲 {DUA_SHORT} 🤲"))
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(FONT_NAME, 8)
            canvas_obj.drawCentredString(w/2, 26,
                ar(f"{APP_NAME} © 2026 — صفحة {canvas_obj.getPageNumber()}"))
            canvas_obj.restoreState()
        
        story.append(P("تقرير تركيبة علفية", size=20, align=TA_CENTER,
                      color='#1b5e20'))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=2.5,
                                color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))
        
        info = [
            [ar("الحيوان:"), ar(animal)],
            [ar("التاريخ:"), datetime.now().strftime('%Y-%m-%d %H:%M')],
        ]
        if reference_key:
            ref = get_reference(reference_key)
            if ref:
                info.append([ar("المرجع:"), ar(ref["name"])])
                info.append([ar("المصدر:"), ar(ref["source"])])
        
        t = Table(info, colWidths=[150, 340])
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(0,-1),HexColor('#e8f5e9')),
            ('BOX',(0,0),(-1,-1),1.5,HexColor('#2e7d32')),
            ('ALIGN',(0,0),(-1,-1),'RIGHT'),
            ('FONTNAME',(0,0),(-1,-1),FONT_NAME),
            ('FONTSIZE',(0,0),(-1,-1),11),
            ('PADDING',(0,0),(-1,-1),8)]))
        story.append(t)
        story.append(Spacer(1, 15))
        
        # المكونات
        story.append(P("🌾 المكونات", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        ing_data = [[ar("المكون"), ar("%"), ar("كجم/طن")]]
        for ing, pct in formula.items():
            ing_data.append([ar(ing), f"{pct:.2f}%", f"{pct*10:.1f}"])
        
        ti = Table(ing_data, colWidths=[270, 110, 110])
        ti.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),FONT_NAME),
            ('FONTSIZE',(0,0),(-1,-1),10),
            ('GRID',(0,0),(-1,-1),0.8,HexColor('#bdbdbd'))]))
        story.append(ti)
        story.append(Spacer(1, 15))
        
        # المقارنة
        actual = compute_nutrients(formula)
        story.append(P("📊 مقارنة مع القياسي", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        
        cmp_data = [[ar("العنصر"), ar("المعيار"), ar("المحسوب"),
                     ar("الفرق %"), ar("التقييم")]]
        cmds = [('BACKGROUND',(0,0),(-1,0),HexColor('#1565c0')),
                ('TEXTCOLOR',(0,0),(-1,0),white),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('FONTNAME',(0,0),(-1,-1),FONT_NAME),
                ('GRID',(0,0),(-1,-1),0.6,HexColor('#bdbdbd'))]
        
        for i, (k, target_val) in enumerate(targets.items(), 1):
            if target_val == 0:
                continue
            actual_val = actual.get(k, 0)
            diff = (actual_val - target_val) / target_val * 100
            ev = evaluate_diff(diff)
            cmp_data.append([ar(k), f"{target_val:.2f}",
                             f"{actual_val:.2f}", f"{diff:+.1f}%",
                             ar(ev["label"])])
            cmds.append(('BACKGROUND',(0,i),(-1,i),HexColor(ev["bg"])))
        
        ct = Table(cmp_data, colWidths=[90,80,80,80,120])
        ct.setStyle(TableStyle(cmds))
        story.append(ct)
        
        doc.build(story, onFirstPage=_draw_page, onLaterPages=_draw_page)
        return buf.getvalue()
    except Exception as e:
        return None

# ═══════════════════════════════════════════════════════════════════════
# 📌 الجلسة
# ═══════════════════════════════════════════════════════════════════════

if "role" not in st.session_state:
    st.session_state["role"] = None
if "pdf_unlocked" not in st.session_state:
    st.session_state["pdf_unlocked"] = False
if "show_video" not in st.session_state:
    st.session_state["show_video"] = True

# نهاية PART 1 — تواصل لـ PART 2
# ═══════════════════════════════════════════════════════════════════════
# [تكملة PART 1] — الواجهة الرئيسية + بوابة الدخول + كل التبويبات
# ═══════════════════════════════════════════════════════════════════════

# ═══ CSS ═══
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');
* { font-family: 'Cairo', 'Amiri', sans-serif !important; }
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
}
.main-box { background: rgba(255,255,255,0.97); padding: 24px;
    border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.12);
    margin-bottom: 70px; }
.dua-box { background: linear-gradient(135deg, #0d3011, #1b5e20, #2e7d32);
    padding: 28px 20px; border-radius: 20px; border: 4px solid #d4af37;
    text-align: center; margin: 20px 0; }
.dua-box * { color: white !important; }
.dua-box h3 { color: #d4af37 !important; font-size: 1.7rem;
    font-weight: 900; margin-bottom: 15px; }
.dua-box .names { background: rgba(212,175,55,0.25);
    font-size: 1.4rem; font-weight: 900; color: #ffeb3b !important;
    padding: 14px 24px; border: 2px solid #d4af37; border-radius: 14px;
    font-family: 'Amiri', serif !important; display: inline-block;
    margin: 15px 0; }
.section-title { color: #1b5e20 !important;
    border-right: 6px solid #2e7d32; padding: 10px 16px;
    text-align: right; font-size: 1.35rem; font-weight: 900;
    margin-top: 20px; margin-bottom: 15px;
    background: linear-gradient(to left, rgba(46,125,50,0.15), transparent);
    border-radius: 10px; }
.formula-item { background: linear-gradient(135deg, #ffffff, #e8f5e9);
    padding: 12px 18px; border-radius: 10px; margin-bottom: 8px;
    font-weight: 700; color: #1b5e20 !important;
    border-right: 5px solid #2e7d32; }
.quality-good { background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
    padding: 20px; border-radius: 20px; border-right: 8px solid #1b5e20;
    margin: 15px 0; }
.quality-bad { background: linear-gradient(135deg, #ffcdd2, #ef9a9a);
    padding: 20px; border-radius: 20px; border-right: 8px solid #c62828;
    margin: 15px 0; }
.ref-card { background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 18px; border-radius: 15px; border-right: 6px solid #1565c0;
    margin: 12px 0; }
.contact-card { background: linear-gradient(135deg, #fff8e1, #ffe082);
    padding: 22px; border-radius: 18px; border: 3px solid #d4af37;
    text-align: center; margin: 20px 0; }
.stButton > button { color: #1a1a1a !important;
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9) !important;
    border: 1.5px solid #2e7d32 !important; font-weight: 700 !important;
    border-radius: 10px !important; }
.mini-sig { position: fixed; left: 20px; bottom: 70px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important; padding: 8px 18px; font-size: 0.82rem;
    border-radius: 25px; z-index: 9997;
    border: 2px solid #d4af37; font-weight: 700; }
.mini-sig * { color: white !important; }
.dua-banner { position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32);
    color: white !important; padding: 10px 20px; z-index: 9998;
    text-align: center; border-top: 3px solid #d4af37;
    font-family: 'Amiri', serif !important; font-size: 1rem;
    font-weight: bold; }
.dua-banner * { color: #ffeb3b !important; }
[data-testid="stMetricValue"] { color: #1b5e20 !important;
    font-weight: 900 !important; }
[data-testid="stMetric"] { background: linear-gradient(135deg,
    #ffffff, #f1f8e9); padding: 12px 16px;
    border-radius: 14px; border-right: 4px solid #2e7d32; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# 🔐 بوابة الدخول
# ═══════════════════════════════════════════════════════════════════════

if not st.session_state["role"]:
    st.markdown('<div class="main-box" style="max-width: 900px; margin: 30px auto;">',
                unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="dua-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <div class="names">🕊️ {DUA_SHORT} 🕊️</div>
        <p style="font-family: 'Amiri', serif; font-size: 1.1rem; margin-top: 15px;">
            ﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-top: 2px solid #d4af37; margin: 25px 0;'>",
                unsafe_allow_html=True)
    
    col_img, col_info = st.columns([0.3, 0.7])
    with col_img:
        if os.path.exists("owner.jpg"):
            st.image("owner.jpg", use_container_width=True)
        else:
            st.info("📸 ضع صورتك باسم owner.jpg")
    
    with col_info:
        st.markdown(f"<h2 style='color:#2E7D32;'>🌾 {APP_NAME}</h2>",
                    unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#c62828;'>{SUPERVISOR}</h4>",
                    unsafe_allow_html=True)
        st.markdown(f"<p style='color:#1565c0;'>{SUPERVISOR_TITLE}</p>",
                    unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align:center; color:#1b5e20; margin-top: 20px;'>"
                "🔐 اختر بوابتك</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""<div style="background:linear-gradient(135deg,#e8f5e9,#c8e6c9);
            padding:16px; border-radius:12px; border:2px solid #2e7d32;
            text-align:center; min-height:140px;">
            <h4 style="color:#1b5e20;">👑 المالك</h4>
            <p style="font-size:0.85rem;">إدارة كاملة + PDF مفتوح</p></div>""",
            unsafe_allow_html=True)
        owner_code = st.text_input("كود المالك:", type="password",
                                    key="owner_code_input")
        if st.button("👑 دخول المالك", type="primary",
                     use_container_width=True, key="btn_owner"):
            if check_owner_code(owner_code):
                st.session_state["role"] = "owner"
                st.session_state["pdf_unlocked"] = True
                st.rerun()
            else:
                st.error("❌ كود غير صحيح")
    
    with col2:
        st.markdown("""<div style="background:linear-gradient(135deg,#e3f2fd,#bbdefb);
            padding:16px; border-radius:12px; border:2px solid #1565c0;
            text-align:center; min-height:140px;">
            <h4 style="color:#0d47a1;">🔬 مختص</h4>
            <p style="font-size:0.85rem;">دخول مباشر</p></div>""",
            unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔬 دخول كمختص", type="primary",
                     use_container_width=True, key="btn_specialist"):
            st.session_state["role"] = "specialist"
            st.rerun()
    
    with col3:
        st.markdown("""<div style="background:linear-gradient(135deg,#fff8e1,#ffecb3);
            padding:16px; border-radius:12px; border:2px solid #d4af37;
            text-align:center; min-height:140px;">
            <h4 style="color:#e65100;">👥 زائر</h4>
            <p style="font-size:0.85rem;">مجاني</p></div>""",
            unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True,
                     key="btn_guest"):
            st.session_state["role"] = "guest"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════════════════════
# 🎥 الفيديو الترحيبي (في الشريط الجانبي)
# ═══════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(f"### 🌾 {APP_NAME}")
    
    if os.path.exists("intro.mp4"):
        st.markdown("#### 🎥 الفيديو التعريفي")
        st.video("intro.mp4", autoplay=True)
        st.caption("💡 شرح كامل للمنصة")
    else:
        st.warning("📹 ضع ملف `intro.mp4` لتفعيل الفيديو الترحيبي")
    
    st.markdown("---")
    
    if os.path.exists("owner.jpg"):
        st.image("owner.jpg", caption=SUPERVISOR, use_container_width=True)
    
    st.markdown(f"""
    **{SUPERVISOR}**
    {SUPERVISOR_TITLE}
    """)
    
    st.markdown("---")
    
    role_label = {"owner": "👑 المالك", "specialist": "🔬 مختص",
                  "guest": "👥 زائر"}.get(st.session_state["role"], "—")
    st.markdown(f"**الحساب:** {role_label}")
    
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📞 التواصل")
    st.markdown(f"📱 واتساب: `{WHATSAPP_NUMBER}`")
    st.markdown(f"📧 `{OWNER_EMAIL}`")


# ═══════════════════════════════════════════════════════════════════════
# الواجهة الرئيسية
# ═══════════════════════════════════════════════════════════════════════

st.markdown('<div class="main-box">', unsafe_allow_html=True)

st.markdown(f"""
<h1 style="color:#0d3011; text-align:center; margin-bottom:5px;">
    🌾 {APP_NAME}
</h1>
<p style="text-align:center; color:#1565c0; font-size:1.1rem;">
    {SUPERVISOR} — {SUPERVISOR_TITLE}
</p>
""", unsafe_allow_html=True)

st.markdown(f'<div class="contact-card">🕌 <b>هذه المنصة صدقة جارية عن والدنا إسماعيل تاور وأختنا ابتسام</b> — نسألكم الدعاء 🤲</div>',
            unsafe_allow_html=True)


# ═══ التبويبات حسب الدور ═══
role = st.session_state["role"]

if role == "owner":
    tab_names = ["🔬 النمذجة", "🧪 المختبر", "📚 التركيبات المرجعية",
                 "📏 شريط القياس", "🏗️ حظيرة الخيل 3D",
                 "📖 المراجع", "💬 تواصل"]
elif role == "specialist":
    tab_names = ["🔬 النمذجة", "🧪 المختبر", "📚 التركيبات المرجعية",
                 "📏 شريط القياس", "🏗️ حظيرة الخيل 3D",
                 "📖 المراجع", "💬 تواصل"]
else:  # guest
    tab_names = ["📚 التركيبات المرجعية", "📏 شريط القياس",
                 "🏗️ حظيرة الخيل 3D", "📖 المراجع", "💬 تواصل"]

tabs = st.tabs(tab_names)
tab_map = dict(zip(tab_names, tabs))


# ═══════════════════════════════════════════════════════════════════════
# 📌 دوال مساعدة للـ UI
# ═══════════════════════════════════════════════════════════════════════

def render_contact_section():
    """قسم التواصل والاستشارة"""
    st.markdown("""
    <div class="contact-card">
        <h3 style="color:#1b5e20; margin:0;">💡 للحصول على تركيبات علفية أكثر جودة</h3>
        <p style="color:#333; font-size:1rem; margin:10px 0;">
            الرجاء الضغط على زر التواصل والاستشارة
        </p>
        <h3 style="color:#c62828; margin:15px 0 5px 0;">👨‍🔬 د. عبدالقادر إسماعيل تاور</h3>
        <p style="color:#0d47a1; font-weight:700;">اختصاصي تغذية الحيوان</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'''
        <a href="https://wa.me/{WHATSAPP_NUMBER.replace("+","").replace(" ","")}?text=أرغب في الحصول على تركيبة علفية أكثر جودة"
           target="_blank"
           style="display:block; padding:14px; background:#25d366; color:white;
                  text-align:center; border-radius:10px; text-decoration:none;
                  font-weight:700; font-size:1rem; border:2px solid #128c7e;">
            📱 تواصل واتساب
        </a>
        ''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''
        <a href="mailto:{OWNER_EMAIL}?subject=طلب استشارة تغذية حيوان&body=السلام عليكم دكتور عبدالقادر،%0D%0Aأرغب في الحصول على استشارة تغذية حيوانية"
           style="display:block; padding:14px; background:#1565c0; color:white;
                  text-align:center; border-radius:10px; text-decoration:none;
                  font-weight:700; font-size:1rem; border:2px solid #0d47a1;">
            ✉️ طلب استشارة بالبريد
        </a>
        ''', unsafe_allow_html=True)


def render_pdf_button(formula, targets, animal, reference_key, key_suffix):
    """عرض زر تحميل PDF مع التقييد"""
    pdf_bytes = generate_pdf(formula, targets, animal, reference_key)
    if not pdf_bytes:
        st.warning("⚠️ تعذر إنشاء PDF")
        return
    
    if role == "owner" or st.session_state.get("pdf_unlocked"):
        st.download_button(
            "📄 تحميل PDF",
            pdf_bytes,
            file_name=f"Tawor_{animal}_{datetime.now():%Y%m%d_%H%M}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
            key=f"pdf_dl_{key_suffix}"
        )
    else:
        st.warning("🔒 تحميل الـ PDF متاح للمالك فقط أو بموافقته")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("📩 طلب موافقة المالك", use_container_width=True,
                         key=f"req_app_{key_suffix}"):
                st.session_state[f"req_sent_{key_suffix}"] = True
                st.info("✅ تم تسجيل طلبك. تواصل مع المالك للاعتماد.")
        
        with col_b:
            st.markdown(f'<a href="https://wa.me/{WHATSAPP_NUMBER.replace("+","").replace(" ","")}?text=أطلب موافقة لتحميل PDF تركيبة علفية ({animal})" target="_blank" style="display:block; padding:10px; background:#25d366; color:white; text-align:center; border-radius:8px; text-decoration:none; font-weight:700;">📱 واتساب المالك</a>',
                        unsafe_allow_html=True)
        
        with col_c:
            st.markdown(f'<a href="mailto:{OWNER_EMAIL}?subject=طلب موافقة PDF" style="display:block; padding:10px; background:#1565c0; color:white; text-align:center; border-radius:8px; text-decoration:none; font-weight:700;">✉️ بريد المالك</a>',
                        unsafe_allow_html=True)
        
        if st.session_state.get(f"req_sent_{key_suffix}"):
            st.caption("🔔 بعد موافقة المالك، سيتم تفعيل التحميل لك.")


def render_charts(formula, targets, actual, quality):
    """عرض الرسوم البيانية"""
    col1, col2 = st.columns(2)
    
    # رسم البار (مقارنة)
    with col1:
        if MATPLOTLIB_AVAILABLE:
            try:
                fig, ax = plt.subplots(figsize=(9, 4.5))
                keys = [k for k in targets.keys() if targets[k] > 0]
                if keys:
                    x = np.arange(len(keys))
                    w = 0.35
                    std_vals = [targets[k] for k in keys]
                    act_vals = [actual.get(k, 0) for k in keys]
                    ax.bar(x - w/2, std_vals, w, label='المعيار',
                           color='#1976d2', edgecolor='#0d47a1')
                    ax.bar(x + w/2, act_vals, w, label='المحسوب',
                           color='#43a047', edgecolor='#1b5e20')
                    ax.set_title('مقارنة العناصر', fontweight='bold',
                                color='#1b5e20')
                    ax.set_xticks(x)
                    ax.set_xticklabels(keys)
                    ax.legend()
                    ax.grid(axis='y', alpha=0.3)
                    st.pyplot(fig)
                    plt.close()
            except Exception:
                pass
    
    # رسم الدائرة
    with col2:
        if MATPLOTLIB_AVAILABLE and len(formula) >= 2:
            try:
                fig, ax = plt.subplots(figsize=(8, 5))
                colors = ['#e53935','#8e24aa','#3949ab','#1e88e5',
                          '#00897b','#43a047','#7cb342','#fdd835',
                          '#fb8c00','#6d4c41']
                names = list(formula.keys())
                vals = list(formula.values())
                ax.pie(vals, labels=names, autopct='%1.1f%%',
                       colors=colors[:len(names)], startangle=90)
                ax.set_title('توزيع المكونات', fontweight='bold',
                            color='#1b5e20')
                st.pyplot(fig)
                plt.close()
            except Exception:
                pass
    
    # مقياس الجودة
    col3, col4 = st.columns(2)
    with col3:
        if MATPLOTLIB_AVAILABLE:
            try:
                fig, ax = plt.subplots(figsize=(4, 4),
                                       subplot_kw=dict(aspect='equal'))
                colors = ['#c62828','#ef6c00','#f9a825',
                          '#7cb342','#43a047','#1b5e20']
                for i, c in enumerate(colors):
                    t1 = 180 - i * 30
                    t2 = 180 - (i + 1) * 30
                    ax.add_patch(Wedge((0,0), 1, t2, t1, width=0.3,
                                       facecolor=c, edgecolor='white',
                                       linewidth=2))
                angle = 180 - (quality / 100) * 180
                rad = np.radians(angle)
                ax.plot([0, 0.85*np.cos(rad)], [0, 0.85*np.sin(rad)],
                        color='#1a1a1a', linewidth=3, zorder=10)
                ax.text(0, -0.25, f'{quality:.0f}%', ha='center',
                        fontsize=22, fontweight='bold', color='#1b5e20')
                ax.set_xlim(-1.2, 1.2)
                ax.set_ylim(-0.7, 1.2)
                ax.axis('off')
                st.pyplot(fig)
                plt.close()
            except Exception:
                pass
    
    with col4:
        if MATPLOTLIB_AVAILABLE:
            try:
                # رادار
                keys = [k for k in targets.keys() if targets[k] > 0][:6]
                if len(keys) >= 3:
                    std_norm = [100.0] * len(keys)
                    act_norm = [(actual.get(k, 0) / targets[k]) * 100
                                for k in keys]
                    angles = np.linspace(0, 2*np.pi, len(keys),
                                          endpoint=False).tolist()
                    std_norm += std_norm[:1]
                    act_norm += act_norm[:1]
                    angles += angles[:1]
                    fig, ax = plt.subplots(figsize=(6, 6),
                                            subplot_kw=dict(polar=True))
                    ax.plot(angles, std_norm, 'o-', linewidth=2.5,
                            color='#1976d2', label='المعيار')
                    ax.fill(angles, std_norm, alpha=0.15, color='#1976d2')
                    ax.plot(angles, act_norm, 'o-', linewidth=2.5,
                            color='#43a047', label='المحسوب')
                    ax.fill(angles, act_norm, alpha=0.25, color='#43a047')
                    ax.set_xticks(angles[:-1])
                    ax.set_xticklabels(keys)
                    ax.set_title('المقارنة %', fontweight='bold',
                                color='#1b5e20', pad=20)
                    ax.legend(loc='upper right',
                              bbox_to_anchor=(1.3, 1.1))
                    st.pyplot(fig)
                    plt.close()
            except Exception:
                pass


def render_comparison_table(actual, targets):
    """جدول مقارنة تفصيلي"""
    rows = []
    labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم",
              "SE": "طاقة SE", "Ca": "كالسيوم Ca", "P": "فسفور P",
              "NDF": "NDF", "ADF": "ADF"}
    
    for k, target in targets.items():
        if target == 0:
            continue
        actual_val = actual.get(k, 0)
        diff = actual_val - target
        pct = (diff / target * 100) if target else 0
        ev = evaluate_diff(pct)
        rows.append({
            "العنصر": labels.get(k, k),
            "المعيار": f"{target:.2f}",
            "المحسوب": f"{actual_val:.2f}",
            "الفرق": f"{diff:+.2f}",
            "الفرق %": f"{pct:+.1f}%",
            "التقييم": ev["label"]
        })
    
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True,
                     hide_index=True)


# ═══════════════════════════════════════════════════════════════════════
# 🔬 تبويب النمذجة
# ═══════════════════════════════════════════════════════════════════════

if "🔬 النمذجة" in tab_map:
    with tab_map["🔬 النمذجة"]:
        st.markdown('<div class="section-title">🔬 محرك النمذجة العلفية</div>',
                    unsafe_allow_html=True)
        
        st.info("💡 اختر حالة الحيوان → اختر المكونات → شغّل المحرك. "
                "النتيجة ستُقارن مع التركيبة المرجعية NRC.")
        
        # اختيار الحالة
        ref_options = list_references()
        
        col1, col2 = st.columns(2)
        with col1:
            ref_labels = [f"{r[1]} ({r[2]})" for r in ref_options]
            selected_ref_label = st.selectbox(
                "اختر حالة الحيوان:",
                ref_labels,
                key="nazej_ref_select")
            selected_ref_key = ref_options[
                ref_labels.index(selected_ref_label)][0]
        
        with col2:
            requester_name = st.text_input("👤 اسم الطالب (اختياري):",
                                            key="nazej_requester")
        
        ref = get_reference(selected_ref_key)
        if ref:
            st.markdown(f"""
            <div class="ref-card">
                <h4 style="color:#0d47a1; margin:0;">📋 {ref['name']}</h4>
                <p style="margin:8px 0;"><b>الأهداف:</b>
                    بروتين {ref['targets']['CP']}% |
                    طاقة {ref['targets']['SE']} |
                    Ca {ref['targets']['Ca']}% |
                    P {ref['targets']['P']}%
                </p>
                <p style="margin:0; color:#555;">
                    📖 {ref['source']}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 🌾 اختر المكونات المتوفرة")
        
        selected_ingredients = []
        for cat_name, items in FEED_LIBRARY.items():
            with st.expander(f"📁 {cat_name} ({len(items)})"):
                cols = st.columns(3)
                for i, ing_name in enumerate(items.keys()):
                    with cols[i % 3]:
                        if st.checkbox(ing_name,
                                       key=f"nazej_pick_{ing_name}"):
                            selected_ingredients.append(ing_name)
        
        if selected_ingredients:
            st.success(f"✅ اخترت {len(selected_ingredients)} مكون")
            
            st.markdown("### 💰 الأسعار")
            prices = {}
            lookup = get_ingredient_lookup()
            cols = st.columns(min(3, len(selected_ingredients)))
            for i, ing in enumerate(selected_ingredients):
                with cols[i % 3]:
                    default_price = lookup.get(ing, {}).get("price", 300)
                    prices[ing] = st.number_input(
                        f"💵 {ing} ($/طن)",
                        min_value=10.0,
                        value=float(default_price),
                        step=10.0,
                        key=f"nazej_price_{ing}")
            
            if st.button("🚀 تشغيل المحرك", type="primary",
                         use_container_width=True, key="nazej_run"):
                if len(selected_ingredients) < 3:
                    st.error("⚠️ اختر 3 مكونات على الأقل")
                else:
                    with st.spinner("⏳ جاري الحساب..."):
                        result = formulate_lp(
                            selected_ingredients,
                            prices,
                            ref["targets"],
                            ref["animal"]
                        )
                    
                    if result["success"]:
                        st.markdown("---")
                        
                        # فحص Validator
                        validation = validate_against_reference(
                            result["formula"], selected_ref_key)
                        
                        quality = result["quality"]
                        meets = quality >= 70
                        
                        if meets:
                            st.markdown(f"""
                            <div class="quality-good">
                                <h3 style="color:#1b5e20; margin:0;">
                                    ✅ جودة التركيبة: {quality:.1f}%
                                </h3>
                                <p style="color:#2e7d32; margin-top:8px;">
                                    الاستراتيجية: {result['strategy']}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="quality-bad">
                                <h3 style="color:#c62828; margin:0;">
                                    ⚠️ جودة التركيبة: {quality:.1f}%
                                </h3>
                                <p style="color:#b71c1c; margin-top:8px;">
                                    الاستراتيجية: {result['strategy']}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # تنبيهات Validator
                        if not validation["valid"]:
                            st.warning("⚠️ تنبيهات الفحص:")
                            for issue in validation.get("issues", []):
                                st.markdown(f"- {issue}")
                        
                        # مقاييس
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("🎯 الجودة", f"{quality:.1f}%")
                        m2.metric("💰 التكلفة", f"${result['cost']:.2f}/طن")
                        m3.metric("🧬 CP", f"{result['actual'].get('CP', 0):.2f}%")
                        m4.metric("⚡ SE", f"{result['actual'].get('SE', 0):.0f}")
                        
                        # المكونات
                        st.markdown("### 🌾 التركيبة")
                        for ing, pct in result["formula"].items():
                            st.markdown(
                                f'<div class="formula-item">▪️ <b>{ing}:</b> '
                                f'{pct:.2f}% ({pct*10:.1f} كجم/طن)</div>',
                                unsafe_allow_html=True)
                        
                        # جدول المقارنة
                        st.markdown("### 📊 جدول المقارنة مع القياسي")
                        render_comparison_table(result["actual"],
                                                 ref["targets"])
                        
                        # الرسوم البيانية
                        st.markdown("### 📈 الرسوم البيانية")
                        render_charts(result["formula"], ref["targets"],
                                       result["actual"], quality)
                        
                        # PDF
                        st.markdown("### 📄 التقرير")
                        render_pdf_button(
                            result["formula"],
                            ref["targets"],
                            ref["animal"],
                            selected_ref_key,
                            "nazej"
                        )
                        
                        # التواصل
                        render_contact_section()
                    else:
                        st.error(f"❌ {result['message']}")
                        st.markdown("### 💡 الحلول المقترحة")
                        st.info(result.get("suggestion", ""))
                        st.markdown("#### سجل المحاولات:")
                        for att in result.get("attempts", []):
                            st.text(att)


# ═══════════════════════════════════════════════════════════════════════
# 🧪 تبويب المختبر
# ═══════════════════════════════════════════════════════════════════════

if "🧪 المختبر" in tab_map:
    with tab_map["🧪 المختبر"]:
        st.markdown('<div class="section-title">🧪 مختبر التركيبات</div>',
                    unsafe_allow_html=True)
        st.info("💡 حلل أي تركيبة جاهزة وقارنها بالمرجع")
        
        col1, col2 = st.columns(2)
        
        with col1:
            lab_animal = st.selectbox(
                "الحيوان:",
                ["أبقار", "أغنام", "ماعز", "دواجن", "أسماك", "أرانب", "إبل", "خيول"],
                key="lab_animal")
        
        with col2:
            lab_ref_key = st.selectbox(
                "المرجع القياسي:",
                list(REFERENCE_FORMULATIONS.keys()),
                format_func=lambda k: REFERENCE_FORMULATIONS[k]["name"],
                key="lab_ref")
        
        st.markdown("### 📝 المكونات والنسب")
        
        lab_input = {}
        with st.form("lab_form"):
            cols = st.columns(3)
            all_ingredients = list(get_ingredient_lookup().keys())
            
            for i in range(8):
                with cols[i % 3]:
                    ing = st.selectbox(
                        f"المكوّن {i+1}",
                        ["— اختر —"] + all_ingredients,
                        key=f"lab_ing_{i}")
                    pct = st.number_input(
                        "النسبة %",
                        min_value=0.0, max_value=100.0, value=0.0,
                        step=0.5, key=f"lab_pct_{i}")
                    if ing != "— اختر —" and pct > 0:
                        lab_input[ing] = pct
            
            if st.form_submit_button("🔬 تحليل", type="primary",
                                     use_container_width=True):
                if not lab_input:
                    st.error("⚠️ أدخل مكونات")
                else:
                    total = sum(lab_input.values())
                    if total > 0:
                        normalized = {k: v/total*100
                                      for k, v in lab_input.items()}
                        actual = compute_nutrients(normalized)
                        ref = get_reference(lab_ref_key)
                        
                        q, _ = evaluate_quality(normalized, ref["targets"])
                        
                        st.markdown("---")
                        if q >= 70:
                            st.markdown(f'<div class="quality-good">'
                                        f'<h3 style="color:#1b5e20;">'
                                        f'✅ الجودة: {q:.1f}%</h3></div>',
                                        unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="quality-bad">'
                                        f'<h3 style="color:#c62828;">'
                                        f'⚠️ الجودة: {q:.1f}%</h3></div>',
                                        unsafe_allow_html=True)
                        
                        st.markdown("### 📊 جدول المقارنة")
                        render_comparison_table(actual, ref["targets"])
                        
                        st.markdown("### 📈 الرسوم")
                        render_charts(normalized, ref["targets"], actual, q)
                        
                        st.markdown("### 📄 التقرير")
                        render_pdf_button(
                            normalized, ref["targets"],
                            ref["animal"], lab_ref_key, "lab")
                        
                        render_contact_section()


# ═══════════════════════════════════════════════════════════════════════
# 📚 تبويب التركيبات المرجعية
# ═══════════════════════════════════════════════════════════════════════

if "📚 التركيبات المرجعية" in tab_map:
    with tab_map["📚 التركيبات المرجعية"]:
        st.markdown('<div class="section-title">📚 12 تركيبة مرجعية معتمدة</div>',
                    unsafe_allow_html=True)
        st.info("💡 هذه التركيبات معتمدة من NRC/FAO/Ross — استخدمها كمرجع ذهبي")
        
        # فلترة
        col1, col2 = st.columns(2)
        with col1:
            filter_animal = st.selectbox(
                "فلتر حسب الحيوان:",
                ["الكل", "أبقار", "أغنام", "ماعز", "دواجن", "أسماك", "أرانب", "إبل", "خيول"],
                key="ref_filter")
        
        with col2:
            st.caption(f"إجمالي: {len(REFERENCE_FORMULATIONS)} تركيبة")
        
        for ref_key, ref in REFERENCE_FORMULATIONS.items():
            if filter_animal != "الكل" and ref["animal"] != filter_animal:
                continue
            
            with st.expander(f"📋 {ref['name']}"):
                st.markdown(f"""
                <div class="ref-card">
                    <p><b>🐾 الحيوان:</b> {ref['animal']}</p>
                    <p><b>📖 المصدر:</b> {ref['source']}</p>
                    <p><b>🎯 الأهداف:</b>
                        بروتين {ref['targets']['CP']}% |
                        طاقة {ref['targets']['SE']} |
                        Ca {ref['targets']['Ca']}% |
                        P {ref['targets']['P']}%
                    </p>
                    <p><b>💡 التبرير العلمي:</b> {ref['rationale']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 🌾 المكونات")
                for ing, pct in ref["reference_recipe"].items():
                    st.markdown(
                        f'<div class="formula-item">▪️ <b>{ing}:</b> '
                        f'{pct:.1f}% ({pct*10:.0f} كجم/طن)</div>',
                        unsafe_allow_html=True)
                
                st.markdown("#### ✅ النتائج المتوقعة")
                expected = ref["expected_output"]
                ecols = st.columns(len(expected))
                for i, (k, v) in enumerate(expected.items()):
                    with ecols[i]:
                        st.metric(k, f"{v:.2f}")
                
                # زر نسخ للتركيبة كـ PDF
                st.markdown("---")
                
                # حساب تركيبة الـ reference
                recipe = ref["reference_recipe"]
                q, actual = evaluate_quality(recipe, ref["targets"])
                
                st.metric("جودة التركيبة المرجعية", f"{q:.1f}%")
                
                render_pdf_button(
                    recipe, ref["targets"],
                    ref["animal"], ref_key, f"ref_{ref_key}")
        
        st.markdown("---")
        render_contact_section()


# ═══════════════════════════════════════════════════════════════════════
# 📏 تبويب شريط القياس
# ═══════════════════════════════════════════════════════════════════════

if "📏 شريط القياس" in tab_map:
    with tab_map["📏 شريط القياس"]:
        st.markdown('<div class="section-title">📏 قياس وزن الحيوان</div>',
                    unsafe_allow_html=True)
        st.info("💡 قس محيط الصدر وطول الجسم لحساب الوزن تقديرياً")
        
        col1, col2 = st.columns(2)
        
        with col1:
            animal = st.selectbox(
                "اختر الحيوان:",
                list(WEIGHT_TAPE.keys()),
                key="tape_animal")
            
            img_buf = render_weight_guide(animal)
            if img_buf:
                st.image(img_buf.getvalue(), use_container_width=True)
        
        with col2:
            cfg = WEIGHT_TAPE[animal]
            hg_min, hg_max, hg_default = cfg["hg"]
            bl_min, bl_max, bl_default = cfg["bl"]
            
            st.markdown("#### 📐 أدخل القياسات")
            
            hg = st.slider(
                "① محيط الصدر (سم):",
                hg_min, hg_max, hg_default,
                key="tape_hg")
            
            bl = st.slider(
                "② طول الجسم (سم):",
                bl_min, bl_max, bl_default,
                key="tape_bl")
            
            weight = cfg["formula"](hg, bl)
            
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#c8e6c9,#a5d6a7);
                        padding:24px; border-radius:18px; text-align:center;
                        border-right:6px solid #1b5e20; margin-top:20px;">
                <div style="font-size:0.9rem; color:#555;">⚖️ الوزن التقديري</div>
                <div style="font-size:3rem; font-weight:900; color:#1b5e20;">
                    {weight:.1f} كجم
                </div>
                <div style="font-size:0.8rem; color:#555; margin-top:8px;">
                    📖 {cfg['source']} | دقة ±5%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("#### 💡 نصائح القياس")
            st.markdown("""
            - 🔴 **محيط الصدر**: ضع الشريط خلف الأرجل الأمامية مباشرة
            - 🔵 **طول الجسم**: من مقدمة الكتف إلى نهاية عظم الحوض
            - ⚖️ اطرح 4% من الناتج إذا كان الحيوان سميناً
            - ⚖️ أضف 4% إذا كان الحيوان نحيفاً
            """)


# ═══════════════════════════════════════════════════════════════════════
# 🏗️ تبويب حظيرة الخيل 3D
# ═══════════════════════════════════════════════════════════════════════

if "🏗️ حظيرة الخيل 3D" in tab_map:
    with tab_map["🏗️ حظيرة الخيل 3D"]:
        st.markdown('<div class="section-title">🏗️ حظيرة خيول 3D</div>',
                    unsafe_allow_html=True)
        st.info("💡 إسطبلات كاملة مع أبواب وأرقام وحيوانات")
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_horses = st.number_input(
                "عدد الخيول:",
                min_value=1, max_value=40, value=10, step=1,
                key="barn_horses")
        
        with col2:
            stall_type = st.selectbox(
                "نوع الإسطبل:",
                ["مربط قياسي (3.5×3.5 م)", "مربط كبير (4×4 م)", "مربط ولادة (4×5 م)"],
                key="barn_stall_type")
        
        # معلومات علمية
        st.markdown("### 📖 المعايير العلمية (NRC 2007 + MWPS-1)")
        info_cols = st.columns(4)
        with info_cols[0]:
            st.metric("المربط", "12.25 م²")
        with info_cols[1]:
            st.metric("الممر", "3.5 م")
        with info_cols[2]:
            st.metric("التهوية/حصان", "30 م³/س")
        with info_cols[3]:
            st.metric("الماء", "45 لتر/يوم")
        
        if st.button("🏗️ بناء النموذج 3D", type="primary",
                     use_container_width=True, key="build_barn"):
            with st.spinner("⏳ جاري بناء النموذج 3D..."):
                fig = build_horse_barn_3d(num_horses)
            
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("### 📊 تفاصيل الحظيرة")
                rows = 2 if num_horses > 4 else 1
                per_row = (num_horses + 1) // 2 if rows == 2 else num_horses
                
                det_cols = st.columns(4)
                with det_cols[0]:
                    st.metric("عدد الصفوف", rows)
                with det_cols[1]:
                    st.metric("مربطات/صف", per_row)
                with det_cols[2]:
                    st.metric("المساحة الكلية",
                              f"{per_row*3.5*2 + 3.5*5:.0f} م²")
                with det_cols[3]:
                    st.metric("إجمالي الإسطبلات", num_horses)
                
                # التكلفة
                st.markdown("### 💰 التكلفة التقديرية")
                cost_rows = [
                    {"البند": "الهيكل المعدني", "التكلفة ($)": f"${num_horses * 3500:,.0f}"},
                    {"البند": "المربطات", "التكلفة ($)": f"${num_horses * 2200:,.0f}"},
                    {"البند": "الخدمات (سرج + غسيل)", "التكلفة ($)": f"$73,000"},
                    {"البند": "التهوية", "التكلفة ($)": f"$8,000"},
                    {"البند": "الإجمالي", "التكلفة ($)": f"${num_horses * 5700 + 81000:,.0f}"},
                ]
                st.dataframe(pd.DataFrame(cost_rows),
                             use_container_width=True, hide_index=True)
            else:
                st.error("⚠️ Plotly غير مثبت أو حدث خطأ")


# ═══════════════════════════════════════════════════════════════════════
# 📖 تبويب المراجع
# ═══════════════════════════════════════════════════════════════════════

if "📖 المراجع" in tab_map:
    with tab_map["📖 المراجع"]:
        st.markdown('<div class="section-title">📖 المراجع العلمية</div>',
                    unsafe_allow_html=True)
        
        st.markdown("""
### 📚 المراجع المعتمدة

#### التغذية
- **NRC (2001)** — Nutrient Requirements of Dairy Cattle, 7th Ed.
- **NRC (2007)** — Nutrient Requirements of Small Ruminants
- **NRC (1994)** — Nutrient Requirements of Poultry, 9th Ed.
- **NRC (2007)** — Nutrient Requirements of Horses, 6th Ed.
- **NRC (2011)** — Fish and Shrimp Nutrition
- **INRA (2018)** — Feeding System for Ruminants
- **FAO (2010)** — Camel Nutrition
- **Ross 308 (2020)** — Broiler Nutrition Specification

#### الحسابات
- **Schaeffer (1978)** — Heart Girth Weight Equation
- **Carroll & Huntington (1988)** — Horse Weight Formula
- **Danø & Højsgaard (2005)** — LP in Ration Formulation
- **Kraft (1988)** — SLSQP Algorithm

#### الحظائر
- **MWPS-1 (2000)** — Structures and Environment Handbook
- **ASAE (2005)** — Ventilation Standards
- **FAO (2012)** — Rural Structures

### 🎯 المعادلات الأساسية

#### محيط الصدر (Schaeffer 1978)
`W = (محيط الصدر² × طول الجسم) ÷ 10840`

#### قياس الخيل (Carroll 1988)
`W = (محيط الصدر² × طول الجسم) ÷ 11877`

#### قياس الإبل (FAO 2010)
`W = (محيط الصدر² × طول الجسم) ÷ 11880`

#### معادلة البرمجة الخطية
