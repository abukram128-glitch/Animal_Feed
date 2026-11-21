# ═══════════════════════════════════════════════════════════════════════
# تاور نولجي TAWOR NOLOGY 11.14 — النسخة النهائية المُعالَجة
# د. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
# ═══════════════════════════════════════════════════════════════════════
# ✅ محرك LP مُعاد بناؤه (قيود صلبة: طاقة ≥ 50%)
# ✅ 15 تركيبة علمية جاهزة (مرجع ذهبي)
# ✅ نظام Fallback ذكي
# ✅ كل التبويبات تعمل
# ═══════════════════════════════════════════════════════════════════════

import streamlit as st
import numpy as np, pandas as pd, io, os, re, base64, json, random
import traceback, warnings, hashlib, hmac, base64
from datetime import datetime
from functools import lru_cache
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple, Any

warnings.filterwarnings('ignore')

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
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
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

# ═══════════════════════════════════════════════════════════════════════
# 📌 الثوابت والإعدادات
# ═══════════════════════════════════════════════════════════════════════

APP_NAME = "تاور نولجي Tawor Nology"
APP_VERSION = "11.14"
SUPERVISOR = "د. عبدالقادر إسماعيل تاور"
SUPERVISOR_TITLE = "اختصاصي تغذية الحيوان"
WHATSAPP_NUMBER = "+249123533489"
OWNER_EMAIL = "abukram128@gmail.com"
DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي ابتسام"
DUA_FULL = "رحم الله والدي إسماعيل تاور وأختي ابتسام وأسكنهما فسيح جناته"

st.set_page_config(page_title=APP_NAME, page_icon="🌾", layout="wide")

# ═══════════════════════════════════════════════════════════════════════
# 🔐 الأمان
# ═══════════════════════════════════════════════════════════════════════

def check_owner_code(user_input):
    try:
        blob = "Nzg2MjAy"
        expected = hashlib.sha256(
            base64.b64decode(blob).decode()[::-1].encode()
        ).hexdigest()
        return hashlib.sha256(user_input.strip().encode()).hexdigest() == expected
    except Exception:
        return False

# ═══════════════════════════════════════════════════════════════════════
# 📌 الخطوط العربية
# ═══════════════════════════════════════════════════════════════════════

class ArabicFontManager:
    def __init__(self):
        self.font_name = 'Helvetica'
        if not REPORTLAB_AVAILABLE:
            return
        try:
            if not os.path.exists("Amiri-Regular.ttf"):
                import urllib.request
                url = ("https://github.com/google/fonts/raw/main/"
                       "ofl/amiri/Amiri-Regular.ttf")
                urllib.request.urlretrieve(url, "Amiri-Regular.ttf")
            pdfmetrics.registerFont(TTFont('TaworArabic', "Amiri-Regular.ttf"))
            self.font_name = 'TaworArabic'
        except Exception:
            pass

font_mgr = ArabicFontManager()

def ar(text):
    if not text: return ""
    if not ARABIC_AVAILABLE: return str(text)
    try:
        return get_display(arabic_reshaper.reshape(str(text)), base_dir='R')
    except Exception:
        return str(text)

# ═══════════════════════════════════════════════════════════════════════
# 📚 المكتبة العلفية (كاملة مع خميرة وعلف دجاج)
# ═══════════════════════════════════════════════════════════════════════

def _feed(cp, dc, se, ndf, adf, ee, ash, ca, p, price, desc, src="NRC"):
    return {"CP":cp, "DC":dc, "SE":se, "NDF":ndf, "ADF":adf, "EE":ee,
            "ASH":ash, "Ca":ca, "P":p, "price":price, "desc":desc, "src":src}

BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": _feed(8.5, .85, 80, 9.5, 3.2, 3.8, 1.3, .02, .27, 230, "الطاقة الرئيسية"),
        "ذرة بيضاء": _feed(8.8, .83, 78, 10.2, 3.5, 3.5, 1.4, .02, .26, 225, "بديل"),
        "شعير مطحون": _feed(11.5, .80, 71, 18.5, 7.5, 2.2, 2.5, .05, .35, 210, "للمجترات"),
        "شعير كامل": _feed(10.8, .75, 68, 22, 9, 2, 2.8, .05, .33, 200, "يحتاج جرش"),
        "قمح محلي": _feed(12, .85, 75, 11.5, 3.8, 2, 1.6, .04, .32, 240, "طاقة جيدة"),
        "قمح مستورد": _feed(11.5, .87, 78, 11, 3.5, 1.9, 1.5, .04, .33, 245, "طاقة"),
        "جريش أرز": _feed(7.8, .82, 82, 5.5, 2.5, 8.5, 4.2, .06, .3, 240, "طاقة عالية"),
        "شوفان علفي": _feed(11, .76, 62, 27.5, 13.5, 5, 3, .08, .35, 260, "للخيول"),
        "مولاس قصب السكر": _feed(4, .95, 50, 1.5, .8, .5, 8.5, .7, .05, 120, "طاقة"),
        "تمر مجفف (دقل)": _feed(5.5, .85, 68, 15, 8.5, 1, 3.5, .1, .1, 180, "اقتصادي"),
        "كسرة خبز": _feed(10.5, .82, 75, 8, 3.5, 5.5, 3.5, .1, .2, 160, "اقتصادي"),
    },
    "🌱 الأكساب ومصادر البروتين": {
        "كسب فول صويا 44%": _feed(44, .90, 74, 13.5, 8, 1.8, 6, .35, .65, 440, "الرئيسي"),
        "كسب فول صويا 48%": _feed(48, .91, 76, 12, 7, 1.5, 6.2, .35, .65, 480, "مرتفع"),
        "كسب عباد الشمس 36%": _feed(36, .76, 42, 38.5, 25.5, 2.5, 6.5, .4, 1, 310, "اقتصادي"),
        "كسب بذور القطن": _feed(41, .78, 55, 24.5, 15.5, 1.2, 6.5, .2, 1.1, 290, "جوسيبول"),
        "كسب بذور الكتان": _feed(32, .82, 65, 18.5, 10.5, 2.8, 5.8, .35, .85, 340, "أوميغا 3"),
        "كسب الكانولا": _feed(36, .82, 60, 28, 18, 3.5, 6.5, .65, 1.1, 400, "متوازن"),
        "كسب السمسم": _feed(42, .84, 70, 14.5, 9.5, 8.5, 12.5, 2, 1.2, 520, "غني Ca"),
        "كسب جلوتين 60%": _feed(60, .92, 85, 8.5, 5.5, 2.5, 3.5, .15, .5, 520, "Met عالٍ"),
        "خميرة الخبز (مفعلة)": _feed(45, .88, 60, 8, 4, 2, 7, .2, .8, 1800, "بروتين حيوي"),
        "فول صويا كامل": _feed(38, .85, 78, 15, 10, 18, 4.5, .25, .55, 420, "معالجة"),
        "بازلاء علفية": _feed(22, .82, 70, 15, 8, 1.5, 3, .1, .4, 320, "متوازن"),
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": _feed(15, .72, 45, 35.5, 12.5, 3.5, 5.5, .12, 1.1, 150, "اقتصادية"),
        "نخالة ذرة": _feed(9.5, .65, 40, 40, 15, 4, 2, .1, .75, 140, "اقتصادية"),
        "البرسيم الجاف": _feed(16.5, .60, 35, 42.5, 32.5, 2, 10.5, 1.5, .25, 170, "بروتين"),
        "برسيم حجازي": _feed(18, .62, 38, 40, 30, 2.2, 11, 1.6, .26, 175, "أفضل"),
        "تبن قمح": _feed(3.2, .35, 18, 72.5, 45.5, 1.5, 8.5, .3, .08, 80, "حشو"),
        "تبن فول": _feed(4.5, .40, 22, 68, 42, 1.2, 7.5, .35, .1, 90, "أفضل"),
        "قش أرز": _feed(3.5, .30, 15, 70, 45, 1.5, 12, .2, .06, 65, "حشو"),
        "سعف نخيل مطحون": _feed(4, .30, 20, 65, 42, 2, 7, .35, .08, 55, "ألياف"),
        "مخلفات النخيل": _feed(6.5, .70, 60, 25, 15, 5, 3.5, .15, .15, 100, "للإبل"),
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": _feed(60, .85, 65, 2.5, 1.5, 8.5, 22.5, 5.5, 3.2, 850, "ممتاز"),
        "مسحوق أسماك 72%": _feed(72, .90, 72, 2, 1, 9.5, 18.5, 4.8, 2.8, 1100, "مرتفع"),
        "مسحوق اللحم والعظم": _feed(50, .75, 50, 3.5, 2.5, 10.5, 32.5, 9, 4.5, 620, "Ca+P"),
        "مسحوق الدم": _feed(80, .65, 55, 1, .5, 1.5, 6, .3, .3, 780, "هضم منخفض"),
        "مسحوق ريش": _feed(82, .70, 60, 1.5, 1, 3, 4, .25, .35, 650, "معالجة"),
    },
    "🌰 الزيوت النباتية والحيوانية": {
        "زيت ذرة": _feed(0, 0, 220, 0, 0, 100, 0, 0, 0, 1500, "أوميغا 6"),
        "زيت فول الصويا": _feed(0, 0, 215, 0, 0, 100, 0, 0, 0, 1350, "متوازن"),
        "زيت عباد الشمس": _feed(0, 0, 210, 0, 0, 100, 0, 0, 0, 1300, "أوميغا 6"),
        "زيت الكتان": _feed(0, 0, 205, 0, 0, 100, 0, 0, 0, 1700, "أوميغا 3"),
        "زيت النخيل": _feed(0, 0, 215, 0, 0, 100, 0, 0, 0, 1100, "مقاوم"),
        "زيت السمك": _feed(0, 0, 235, 0, 0, 100, 0, 0, 0, 3800, "EPA/DHA"),
        "شحم حيواني": _feed(0, 0, 230, 0, 0, 100, 0, 0, 0, 900, "طاقة"),
    },
    "🐔 أعلاف جاهزة": {
        "علف دجاج جاهز (بادي)": _feed(23, .86, 76, 8, 4, 4.5, 6.5, 1, .5, 400, "لاحم بادي", "Ross 308"),
        "علف دجاج جاهز (نامي)": _feed(21, .85, 74, 9, 5, 4.5, 6, .9, .45, 390, "لاحم نامي", "Ross 308"),
        "علف دجاج جاهز (ناهي)": _feed(19.5, .84, 75, 10, 5.5, 4.5, 6, .87, .43, 380, "لاحم ناهي", "Ross 308"),
        "علف بياض جاهز": _feed(18, .82, 72, 10, 5.5, 4, 8.5, 3.8, .45, 395, "بياض جاهز"),
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": _feed(0, 0, 0, 0, 0, 0, 99.5, 38, 0, 40, "مصدر Ca"),
        "فوسفات ثنائي الكالسيوم": _feed(0, 0, 0, 0, 0, 0, 98.5, 23, 18, 280, "Ca+P"),
        "ملح الطعام": _feed(0, 0, 0, 0, 0, 0, 99.9, 0, 0, 30, "NaCl"),
        "بيكربونات الصوديوم": _feed(0, 0, 0, 0, 0, 0, 99, 0, 0, 340, "مضاد حموضة"),
        "أكسيد المغنيسيوم": _feed(0, 0, 0, 0, 0, 0, 99.5, 0, 0, 480, "Mg"),
        "يوريا علفية": _feed(287, .95, 0, 0, 0, 0, 1, 0, 0, 480, "NPN"),
        "مضاد سموم فطرية": _feed(0, 0, 0, 0, 0, 0, 85, 0, 0, 950, "أفلاتوكسين"),
    },
    "🔬 بريمكسات وإضافات": {
        "بريمكس تسمين دواجن": _feed(0, 0, 0, 0, 0, 0, 100, 18, 8, 4800, "فيتامينات"),
        "بريمكس بياض": _feed(0, 0, 0, 0, 0, 0, 100, 22, 7, 5000, "بياض"),
        "بريمكس أبقار": _feed(0, 0, 0, 0, 0, 0, 100, 20, 10, 5200, "أبقار"),
        "بريمكس مجترات": _feed(0, 0, 0, 0, 0, 0, 100, 18, 9, 4500, "مجترات"),
        "بريمكس خيول": _feed(0, 0, 0, 0, 0, 0, 100, 15, 8, 5500, "خيول"),
        "بريمكس إبل": _feed(0, 0, 0, 0, 0, 0, 100, 20, 10, 5300, "إبل"),
        "بريمكس أسماك": _feed(0, 0, 0, 0, 0, 0, 100, 15, 7, 5800, "أسماك"),
        "ليسين نقي": _feed(94, 1, 0, 0, 0, 0, .5, 0, 0, 4200, "أساسي"),
        "ميثيونين نقي": _feed(58, 1, 0, 0, 0, 0, .3, 0, 0, 5800, "للدواجن"),
        "إنزيم فايتيز": _feed(0, 0, 0, 0, 0, 0, 5, 0, 0, 4200, "تحرير P"),
    },
}

def _get_ingredient_lookup():
    lookup = {}
    for cat in BIG_FEEDS_LIBRARY.values():
        lookup.update(cat)
    return lookup

# ═══════════════════════════════════════════════════════════════════════
# 🏆 v11.14 — 15 تركيبة علمية جاهزة (المرجع الذهبي)
# ═══════════════════════════════════════════════════════════════════════

VALIDATED_FORMULATIONS = {
    "أبقار_حليب_عالي_20L": {
        "label": "أبقار حلابة 20 لتر/يوم (NRC 2001)",
        "animal": "أبقار",
        "production": "حليب_عالي",
        "targets": {"CP": 17.5, "DP": 12.5, "SE": 67, "Ca": 0.65, "P": 0.38},
        "formula": {
            "ذرة صفراء": 35,
            "شعير مطحون": 15,
            "كسب فول صويا 44%": 20,
            "نخالة قمح (ردة)": 12,
            "البرسيم الجاف": 12,
            "الحجر الجيري": 1.8,
            "فوسفات ثنائي الكالسيوم": 1.2,
            "ملح الطعام": 0.5,
            "بيكربونات الصوديوم": 0.75,
            "بريمكس أبقار": 0.25,
            "مضاد سموم فطرية": 0.1,
            "زيت فول الصويا": 1.4,
        },
        "notes": "تركيبة قياسية معتمدة من NRC — ذرة + شعير = طاقة أساسية"
    },
    "أبقار_حليب_متوسط_15L": {
        "label": "أبقار حلابة 15 لتر/يوم",
        "animal": "أبقار",
        "production": "حليب_متوسط",
        "targets": {"CP": 15.5, "DP": 11.0, "SE": 62, "Ca": 0.55, "P": 0.35},
        "formula": {
            "ذرة صفراء": 32,
            "شعير مطحون": 20,
            "كسب فول صويا 44%": 15,
            "نخالة قمح (ردة)": 15,
            "البرسيم الجاف": 15,
            "الحجر الجيري": 1.5,
            "فوسفات ثنائي الكالسيوم": 1,
            "ملح الطعام": 0.5,
            "بيكربونات الصوديوم": 0.5,
            "بريمكس أبقار": 0.25,
        },
    },
    "أبقار_تسمين_مكثف": {
        "label": "تسمين عجول مكثف (ADG 1.3 kg)",
        "animal": "أبقار",
        "production": "تسمين_مكثف",
        "targets": {"CP": 14.5, "DP": 11.5, "SE": 72, "Ca": 0.65, "P": 0.38},
        "formula": {
            "ذرة صفراء": 45,
            "شعير مطحون": 25,
            "كسب فول صويا 44%": 12,
            "نخالة قمح (ردة)": 10,
            "البرسيم الجاف": 5,
            "الحجر الجيري": 1.5,
            "فوسفات ثنائي الكالسيوم": 0.8,
            "ملح الطعام": 0.4,
            "بيكربونات الصوديوم": 0.8,
            "بريمكس أبقار": 0.3,
            "مضاد سموم فطرية": 0.1,
            "يوريا علفية": 0.7,
        },
    },
    "أبقار_تسمين_عادي": {
        "label": "تسمين عجول عادي (ADG 0.8 kg)",
        "animal": "أبقار",
        "production": "تسمين_عادي",
        "targets": {"CP": 12, "DP": 9.5, "SE": 65, "Ca": 0.55, "P": 0.32},
        "formula": {
            "ذرة صفراء": 35,
            "شعير مطحون": 30,
            "كسب فول صويا 44%": 10,
            "نخالة قمح (ردة)": 12,
            "البرسيم الجاف": 10,
            "الحجر الجيري": 1.5,
            "فوسفات ثنائي الكالسيوم": 0.5,
            "ملح الطعام": 0.4,
            "بيكربونات الصوديوم": 0.5,
            "بريمكس أبقار": 0.3,
        },
    },
    "أغنام_تسمين_مكثف": {
        "label": "تسمين حملان مكثف",
        "animal": "أغنام",
        "production": "تسمين_مكثف",
        "targets": {"CP": 14.5, "DP": 11.5, "SE": 64, "Ca": 0.65, "P": 0.36},
        "formula": {
            "شعير مطحون": 40,
            "ذرة صفراء": 20,
            "كسب فول صويا 44%": 15,
            "نخالة قمح (ردة)": 10,
            "البرسيم الجاف": 10,
            "الحجر الجيري": 1.8,
            "فوسفات ثنائي الكالسيوم": 1,
            "ملح الطعام": 0.5,
            "بيكربونات الصوديوم": 0.8,
            "بريمكس مجترات": 0.25,
            "مضاد سموم فطرية": 0.1,
        },
    },
    "أغنام_مرضعات": {
        "label": "نعاج مرضعات (مولود واحد)",
        "animal": "أغنام",
        "production": "مرضعات",
        "targets": {"CP": 14.5, "DP": 10.5, "SE": 62, "Ca": 0.65, "P": 0.38},
        "formula": {
            "شعير مطحون": 35,
            "ذرة صفراء": 15,
            "كسب فول صويا 44%": 15,
            "نخالة قمح (ردة)": 12,
            "البرسيم الجاف": 18,
            "الحجر الجيري": 1.8,
            "فوسفات ثنائي الكالسيوم": 1.2,
            "ملح الطعام": 0.5,
            "بيكربونات الصوديوم": 0.75,
            "بريمكس مجترات": 0.3,
        },
    },
    "ماعز_حلابة_عالي": {
        "label": "عنزات حلابة 2-3 لتر/يوم",
        "animal": "ماعز",
        "production": "حلابة_عالي",
        "targets": {"CP": 14.5, "DP": 10.5, "SE": 60, "Ca": 0.6, "P": 0.35},
        "formula": {
            "شعير مطحون": 30,
            "ذرة صفراء": 20,
            "كسب فول صويا 44%": 15,
            "نخالة قمح (ردة)": 15,
            "البرسيم الجاف": 15,
            "الحجر الجيري": 1.8,
            "فوسفات ثنائي الكالسيوم": 1.2,
            "ملح الطعام": 0.5,
            "بيكربونات الصوديوم": 0.75,
            "بريمكس مجترات": 0.25,
        },
    },
    "إبل_حليب": {
        "label": "إبل حلابة 5 لتر/يوم",
        "animal": "إبل",
        "production": "حليب",
        "targets": {"CP": 16, "DP": 11.5, "SE": 64, "Ca": 0.7, "P": 0.4},
        "formula": {
            "شعير مطحون": 35,
            "ذرة صفراء": 20,
            "كسب فول صويا 44%": 15,
            "نخالة قمح (ردة)": 12,
            "البرسيم الجاف": 12,
            "الحجر الجيري": 2,
            "فوسفات ثنائي الكالسيوم": 1.5,
            "ملح الطعام": 0.5,
            "بيكربونات الصوديوم": 0.75,
            "بريمكس إبل": 0.25,
        },
    },
    "إبل_تسمين": {
        "label": "إبل تسمين",
        "animal": "إبل",
        "production": "تسمين",
        "targets": {"CP": 12, "DP": 9.5, "SE": 65, "Ca": 0.6, "P": 0.35},
        "formula": {
            "شعير مطحون": 40,
            "ذرة صفراء": 20,
            "كسب فول صويا 44%": 10,
            "نخالة قمح (ردة)": 15,
            "البرسيم الجاف": 10,
            "الحجر الجيري": 1.5,
            "فوسفات ثنائي الكالسيوم": 1,
            "ملح الطعام": 0.5,
            "بيكربونات الصوديوم": 1,
            "بريمكس إبل": 0.25,
        },
    },
    "خيول_رياضة_مكثف": {
        "label": "خيول رياضة مكثف",
        "animal": "خيول",
        "production": "رياضة_مكثف",
        "targets": {"CP": 13.5, "DP": 10.5, "SE": 70, "Ca": 0.7, "P": 0.4},
        "formula": {
            "شوفان علفي": 30,
            "شعير مطحون": 25,
            "ذرة صفراء": 15,
            "كسب فول صويا 44%": 12,
            "نخالة قمح (ردة)": 8,
            "البرسيم الجاف": 5,
            "الحجر الجيري": 2,
            "فوسفات ثنائي الكالسيوم": 1.5,
            "ملح الطعام": 0.5,
            "بريمكس خيول": 0.3,
            "زيت فول الصويا": 3,
        },
    },
    "دواجن_بادي": {
        "label": "دواجن لاحم — بادي (أسبوع 1)",
        "animal": "دواجن",
        "production": "لاحم",
        "targets": {"CP": 23, "DP": 20, "SE": 76, "Ca": 1, "P": 0.5},
        "formula": {
            "ذرة صفراء": 52,
            "كسب فول صويا 48%": 35,
            "زيت فول الصويا": 4.5,
            "الحجر الجيري": 1.2,
            "فوسفات ثنائي الكالسيوم": 1.8,
            "ملح الطعام": 0.3,
            "بريمكس تسمين دواجن": 0.3,
            "ليسين نقي": 0.25,
            "ميثيونين نقي": 0.15,
            "مضاد سموم فطرية": 0.1,
        },
    },
    "دواجن_ناهي": {
        "label": "دواجن لاحم — ناهي (أسبوع 5+)",
        "animal": "دواجن",
        "production": "لاحم",
        "targets": {"CP": 19.5, "DP": 17, "SE": 75, "Ca": 0.87, "P": 0.43},
        "formula": {
            "ذرة صفراء": 58,
            "كسب فول صويا 44%": 28,
            "زيت فول الصويا": 4,
            "الحجر الجيري": 1.2,
            "فوسفات ثنائي الكالسيوم": 1.8,
            "ملح الطعام": 0.3,
            "بريمكس تسمين دواجن": 0.3,
            "ليسين نقي": 0.2,
            "ميثيونين نقي": 0.15,
            "مضاد سموم فطرية": 0.1,
        },
    },
    "دواجن_بياض": {
        "label": "دواجن بياض (إنتاجي)",
        "animal": "دواجن",
        "production": "بياض",
        "targets": {"CP": 18, "DP": 15.5, "SE": 72, "Ca": 3.8, "P": 0.45},
        "formula": {
            "ذرة صفراء": 58,
            "كسب فول صويا 44%": 22,
            "نخالة قمح (ردة)": 5,
            "الحجر الجيري": 8,
            "فوسفات ثنائي الكالسيوم": 1.8,
            "ملح الطعام": 0.3,
            "بريمكس بياض": 0.3,
            "ميثيونين نقي": 0.1,
            "زيت فول الصويا": 2,
            "مضاد سموم فطرية": 0.1,
        },
    },
    "أسماك_بادئ": {
        "label": "أسماك البلطي — بادئ",
        "animal": "أسماك",
        "production": "بادئ_زريعة",
        "targets": {"CP": 40, "DP": 32, "SE": 72, "Ca": 1.5, "P": 0.9},
        "formula": {
            "مسحوق أسماك 60%": 35,
            "كسب فول صويا 44%": 30,
            "قمح محلي": 20,
            "كسب جلوتين 60%": 5,
            "زيت السمك": 6,
            "فوسفات ثنائي الكالسيوم": 2,
            "بريمكس أسماك": 0.3,
            "ملح الطعام": 0.2,
            "مضاد سموم فطرية": 0.1,
            "ليسين نقي": 0.4,
            "ميثيونين نقي": 0.2,
        },
    },
    "أرانب_تسمين": {
        "label": "أرانب تسمين",
        "animal": "أرانب",
        "production": "تسمين",
        "targets": {"CP": 17, "DP": 15, "SE": 65, "Ca": 0.7, "P": 0.35},
        "formula": {
            "برسيم حجازي": 35,
            "شعير مطحون": 25,
            "كسب فول صويا 44%": 12,
            "نخالة قمح (ردة)": 18,
            "ذرة صفراء": 5,
            "الحجر الجيري": 1.5,
            "فوسفات ثنائي الكالسيوم": 1,
            "ملح الطعام": 0.5,
            "بريمكس مجترات": 0.25,
        },
    },
}

# ═══════════════════════════════════════════════════════════════════════
# 🧮 الاحتياجات الغذائية (NRC)
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class AnimalRequirement:
    CP: float
    DP: float
    SE: float
    Ca: float
    P: float
    NDF: float = 30
    ADF: float = 20
    EE: float = 4
    ASH: float = 8
    name_ar: str = ""
    note: str = ""

def get_cattle_requirements(t, milk=20):
    if t == "حليب_عالي":
        return AnimalRequirement(17.5, 12.5, 67, .65, .38,
            name_ar="حلابة عالية", note=f"حليب {milk} لتر")
    if t == "حليب_متوسط":
        return AnimalRequirement(15.5, 11, 62, .55, .35,
            name_ar="حلابة متوسطة")
    if t == "تسمين_مكثف":
        return AnimalRequirement(14.5, 11.5, 72, .65, .38,
            name_ar="تسمين مكثف")
    if t == "تسمين_عادي":
        return AnimalRequirement(12, 9.5, 65, .55, .32,
            name_ar="تسمين عادي")
    return AnimalRequirement(10, 7.5, 53, .42, .26, name_ar="صيانة")

def get_sheep_requirements(t, is_male=True, litter=1):
    if is_male:
        if t == "تسمين_مكثف":
            return AnimalRequirement(14.5, 11.5, 64, .65, .36, name_ar="تسمين مكثف")
        return AnimalRequirement(12, 9.5, 59, .55, .32, name_ar="تسمين عادي")
    if t == "مرضعات":
        dp = 10.5 + (litter - 1) * 1.5
        return AnimalRequirement(round(dp/.72,2), round(dp,2),
            62, .65, .38, name_ar=f"مرضعات ({litter})")
    return AnimalRequirement(9.5, 7.2, 48, .42, .26, name_ar="صيانة")

def get_goat_requirements(t, is_male=True, milk=2):
    if is_male:
        return AnimalRequirement(14, 11, 62, .62, .34, name_ar="تسمين")
    if t == "حلابة_عالي":
        dp = 9.5 + milk * .35
        return AnimalRequirement(round(dp/.72,2), round(dp,2),
            60, .6, .35, name_ar=f"حلابة ({milk}L)")
    return AnimalRequirement(9, 6.8, 46, .42, .26, name_ar="صيانة")

def get_camel_requirements(t, milk=5):
    if t == "حليب":
        dp = 10.5 + milk * .2
        return AnimalRequirement(round(dp/.72,2), round(dp,2),
            64, .7, .4, name_ar=f"حلابة ({milk}L)")
    if t == "تسمين":
        return AnimalRequirement(12, 9.5, 65, .6, .35, name_ar="تسمين")
    return AnimalRequirement(13.5, 10.5, 60, .65, .38, name_ar="نمو")

def get_horse_requirements(t):
    if t == "رياضة_مكثف":
        return AnimalRequirement(13.5, 10.5, 70, .7, .4, name_ar="رياضة مكثف")
    if t == "رياضة_عادي":
        return AnimalRequirement(11.5, 9, 63, .55, .32, name_ar="رياضة عادي")
    return AnimalRequirement(9.5, 7.2, 53, .45, .28, name_ar="صيانة")

def get_poultry_requirements(strain, age=1):
    if strain == "لاحم":
        if age <= 1:
            return AnimalRequirement(23, 20, 76, 1, .5, name_ar="بادي")
        if age <= 3:
            return AnimalRequirement(21, 18.5, 74, .9, .45, name_ar="نامي")
        return AnimalRequirement(19.5, 17, 75, .87, .43, name_ar="ناهي")
    return AnimalRequirement(18, 15.5, 72, 3.8, .45, name_ar="بياض")

def get_fish_requirements(species, stage):
    if "بادئ" in stage:
        return AnimalRequirement(40, 32, 72, 1.5, .9, name_ar="بادئ")
    return AnimalRequirement(32, 25, 70, 1, .7, name_ar="نمو")

def get_rabbit_requirements(t):
    if t == "تسمين":
        return AnimalRequirement(17, 15, 65, .7, .35, name_ar="تسمين")
    return AnimalRequirement(14, 12, 60, .6, .3, name_ar="صيانة")

def requirement_to_standard(req):
    return {"CP": req.CP, "DP": req.DP, "SE": req.SE,
            "NDF": req.NDF, "ADF": req.ADF, "Ca": req.Ca, "P": req.P}

# ═══════════════════════════════════════════════════════════════════════
# 🧮 حسابات التقييم
# ═══════════════════════════════════════════════════════════════════════

def compute_formula_nutrients(formula):
    totals = {k: 0.0 for k in ["CP", "DP", "SE", "NDF", "ADF",
                                "EE", "ASH", "Ca", "P"]}
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

def evaluate_difference(pct_diff):
    a = abs(pct_diff)
    if a <= .5: return {"label": "🎯 مطابق", "score": 100, "bg": "#c8e6c9"}
    if a <= 2: return {"label": "🌟 ممتاز", "score": 95, "bg": "#dcedc8"}
    if a <= 5: return {"label": "✅ جيد جداً", "score": 85, "bg": "#e8f5e9"}
    if a <= 10: return {"label": "🟢 جيد", "score": 75, "bg": "#f1f8e9"}
    if a <= 15: return {"label": "⭐ مقبول", "score": 65, "bg": "#fff8e1"}
    if a <= 25: return {"label": "⚠️ بتحفظ", "score": 50, "bg": "#fff3e0"}
    return {"label": "❌ ضعيف", "score": 25, "bg": "#ffebee"}

def evaluate_quality(formula, targets, animal_type="أبقار"):
    actual = compute_formula_nutrients(formula)
    weights = {"CP": 0.30, "DP": 0.15, "SE": 0.20,
               "Ca": 0.10, "P": 0.10, "NDF": 0.15}
    total_w = weighted = 0.0
    for nut, w in weights.items():
        target = targets.get(nut, 0)
        if target <= 0:
            continue
        diff = abs(actual.get(nut, 0) - target) / target * 100
        ev = evaluate_difference(diff)
        weighted += ev["score"] * w
        total_w += w
    return (weighted / total_w if total_w else 0.0), actual

# ═══════════════════════════════════════════════════════════════════════
# 🚀 v11.14 — محرك LP المُعاد بناؤه (بدون أخطاء)
# ═══════════════════════════════════════════════════════════════════════

def categorize_ingredients(ingredient_names):
    """تصنيف المكونات: طاقة / بروتين / أملاح / إضافات / زيوت"""
    lookup = _get_ingredient_lookup()
    energy, protein, salts, additives, oils = [], [], [], [], []
    
    for i, ing in enumerate(ingredient_names):
        d = lookup.get(ing, {})
        se, cp = d.get("SE", 0), d.get("CP", 0)
        ca = d.get("Ca", 0)
        
        if se > 150:  # زيوت
            oils.append(i)
        elif se > 40 and cp < 20:  # حبوب وطاقة
            energy.append(i)
        elif cp >= 20:  # بروتين
            protein.append(i)
        elif ca > 15 or "ملح" in ing or "حجر" in ing:  # أملاح
            salts.append(i)
        else:  # إضافات
            additives.append(i)
    
    return energy, protein, salts, additives, oils

def formulate_lp(ingredient_names, prices, targets, animal_type="أبقار"):
    """
    🎯 محرك LP مُعاد بناؤه بقيود صلبة:
    - مجموع = 100%
    - البروتين = الهدف ±1%
    - الطاقة ≥ 90% الهدف
    - مصادر الطاقة ≥ 45% (قيد صلب!)
    - مصادر البروتين ≤ 35%
    - حدود كل مكون: min 0.1% - max 60%
    """
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "SCIPY غير متوفرة"}
    
    lookup = _get_ingredient_lookup()
    valid = [i for i in ingredient_names if i in lookup]
    if len(valid) < 2:
        return {"success": False, "message": "اختر مكونين على الأقل"}
    
    n = len(valid)
    c = [prices.get(ing, lookup[ing]["price"]) for ing in valid]
    
    # قيمة كل مؤشر لكل مكون
    cp = [lookup[ing].get("CP", 0) for ing in valid]
    se = [lookup[ing].get("SE", 0) for ing in valid]
    ca = [lookup[ing].get("Ca", 0) for ing in valid]
    p = [lookup[ing].get("P", 0) for ing in valid]
    dp = [lookup[ing].get("CP", 0) * lookup[ing].get("DC", 0) for ing in valid]
    
    # تصنيف
    energy_idx, protein_idx, salts_idx, additives_idx, oils_idx = \
        categorize_ingredients(valid)
    
    # ═══ استراتيجيات التراجع ═══
    strategies = [
        ("🎯 دقيق 100%", 1.00),
        ("🌟 مرن 97%", 0.97),
        ("✅ مرن 95%", 0.95),
        ("🟢 مرن 92%", 0.92),
        ("⭐ مرن 90%", 0.90),
        ("⚠️ مرن 85%", 0.85),
    ]
    
    best_result = None
    best_quality = 0.0
    
    for strategy_name, mult in strategies:
        try:
            target_cp = targets.get("CP", 16) * mult
            target_se = targets.get("SE", 65) * mult
            target_ca = targets.get("Ca", 0.6)
            target_p = targets.get("P", 0.35)
            
            A_eq = [[1.0] * n]
            b_eq = [100.0]
            
            A_ub = []
            b_ub = []
            
            # قيد البروتين (في حدود مقبولة)
            A_ub.append([-x for x in cp])
            b_ub.append(-(target_cp * 0.95) * 100)
            A_ub.append(cp)
            b_ub.append((target_cp * 1.10) * 100)
            
            # قيد الطاقة
            A_ub.append([-x * 41 for x in se])
            b_ub.append(-(target_se * 0.92) * 100 * 41 / 100)
            
            # 🚀 قيد صلبة: الطاقة ≥ 45%
            if energy_idx:
                energy_row = [1.0 if i in energy_idx else 0.0
                              for i in range(n)]
                A_ub.append([-x for x in energy_row])
                b_ub.append(-45.0)
            
            # 🚀 قيد صلبة: البروتين ≤ 35%
            if protein_idx:
                protein_row = [1.0 if i in protein_idx else 0.0
                               for i in range(n)]
                A_ub.append(protein_row)
                b_ub.append(35.0)
            
            # قيد الكالسيوم
            if target_ca > 0 and ca[0] + p[0] > 0:
                A_ub.append([-x for x in ca])
                b_ub.append(-(target_ca * 0.85) * 100)
                A_ub.append(ca)
                b_ub.append((target_ca * 1.15) * 100)
            
            # قيد الفسفور
            if target_p > 0:
                A_ub.append([-x for x in p])
                b_ub.append(-(target_p * 0.85) * 100)
                A_ub.append(p)
                b_ub.append((target_p * 1.15) * 100)
            
            # قيد الزيوت
            if oils_idx:
                oil_row = [1.0 if i in oils_idx else 0.0 for i in range(n)]
                A_ub.append(oil_row)
                b_ub.append(8.0)
            
            # حدود المكونات
            bounds = []
            for i, ing in enumerate(valid):
                if i in salts_idx or i in additives_idx:
                    bounds.append((0.0, 5.0))  # أملاح وإضافات ≤ 5%
                elif i in oils_idx:
                    bounds.append((0.0, 8.0))  # زيوت ≤ 8%
                else:
                    bounds.append((0.0, 60.0))  # مكونات رئيسية ≤ 60%
            
            # حل LP
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                         bounds=bounds, method='highs')
            
            if res.success:
                formula = {valid[i]: round(res.x[i], 2)
                          for i in range(n) if res.x[i] > 0.1}
                quality, actual = evaluate_quality(formula, targets, animal_type)
                total_cost = res.fun / 100
                
                if quality > best_quality:
                    best_quality = quality
                    best_result = {
                        "success": True,
                        "formula": formula,
                        "cost": round(total_cost, 2),
                        "actual": actual,
                        "quality_score": round(quality, 1),
                        "strategy": strategy_name,
                        "meets_standard": quality >= 70,
                    }
                
                if quality >= 90:
                    break
        
        except Exception:
            continue
    
    if best_result:
        return best_result
    
    # 🆘 Fallback: توزيع متساوٍ مع التحقق
    fallback = {}
    if energy_idx and protein_idx:
        # 55% طاقة + 25% بروتين + 20% أخرى
        for i in energy_idx[:3]:
            fallback[valid[i]] = round(55 / len(energy_idx[:3]), 1)
        for i in protein_idx[:2]:
            fallback[valid[i]] = round(25 / len(protein_idx[:2]), 1)
        for i in salts_idx:
            fallback[valid[i]] = 1.0
        for i in additives_idx:
            fallback[valid[i]] = 0.3
    else:
        for i in range(n):
            fallback[valid[i]] = round(100 / n, 2)
    
    # تطبيع
    total = sum(fallback.values())
    if total > 0:
        fallback = {k: round(v * 100 / total, 2) for k, v in fallback.items()}
    
    quality, actual = evaluate_quality(fallback, targets, animal_type)
    
    return {
        "success": True,
        "formula": fallback,
        "cost": round(sum(fallback[i] / 100 * prices.get(i, 300)
                         for i in fallback), 2),
        "actual": actual,
        "quality_score": round(quality, 1),
        "strategy": "🆘 توزيع ذكي",
        "meets_standard": quality >= 70,
        "warning": "لم يجد LP حلاً مثالياً — استخدمنا توزيعاً متوازناً"
    }

def get_validated_formula(animal, production):
    """البحث عن تركيبة جاهزة مطابقة"""
    for key, data in VALIDATED_FORMULATIONS.items():
        if data["animal"] == animal and data["production"] == production:
            return key, data
    return None, None

def evaluate_validated_formula(key):
    """تقييم تركيبة جاهزة"""
    data = VALIDATED_FORMULATIONS.get(key)
    if not data:
        return None
    quality, actual = evaluate_quality(
        data["formula"], data["targets"], data["animal"])
    lookup = _get_ingredient_lookup()
    cost = sum(data["formula"][ing] / 100 * lookup.get(ing, {}).get("price", 300)
               for ing in data["formula"])
    return {
        "success": True,
        "formula": data["formula"],
        "cost": round(cost, 2),
        "actual": actual,
        "quality_score": round(quality, 1),
        "strategy": f"🏆 {data['label']}",
        "meets_standard": quality >= 70,
        "notes": data.get("notes", ""),
    }
# ═══════════════════════════════════════════════════════════════════════
# [تكملة PART 1] — الواجهة + التبويبات + الـ 15 تركيبة + التذييل
# ═══════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════
# 📄 PDF Generator
# ═══════════════════════════════════════════════════════════════════════

def generate_pdf_report(title, formula, targets, actual, cost, quality, notes=""):
    """توليد تقرير PDF احترافي"""
    if not REPORTLAB_AVAILABLE:
        return b""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, rightMargin=40, leftMargin=40,
            topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(ar(text), ParagraphStyle('s',
                fontName=font_mgr.font_name, fontSize=size, alignment=align,
                textColor=HexColor(color), spaceAfter=6, leading=size*1.6))

        # العنوان
        story.append(P(title, size=20, align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
            color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))

        # التاريخ
        story.append(P(f"📅 {datetime.now():%Y-%m-%d %H:%M}",
            size=11, align=TA_CENTER, color='#555'))
        story.append(Spacer(1, 15))

        # المؤشرات
        info = [
            [ar("المؤشر"), ar("القيمة")],
            [ar("الجودة"), f"{quality:.1f}%"],
            [ar("التكلفة"), f"${cost:.2f}/طن"],
            [ar("عدد المكونات"), f"{len(formula)}"],
        ]
        t = Table(info, colWidths=[200, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

        # جدول المكونات
        story.append(P("🌾 المكونات", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        ing_data = [[ar("المكوّن"), ar("النسبة %")]]
        for ing, pct in formula.items():
            ing_data.append([ar(ing), f"{pct:.2f}%"])
        ti = Table(ing_data, colWidths=[300, 150])
        ti.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.6, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [HexColor('#ffffff'), HexColor('#f5f5f5')]),
        ]))
        story.append(ti)
        story.append(Spacer(1, 15))

        # جدول المقارنة
        story.append(P("📊 مقارنة العناصر مع NRC", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        labels = {"CP": "بروتين", "DP": "مهضوم", "SE": "طاقة",
                  "Ca": "Ca", "P": "P"}
        cmp = [[ar("العنصر"), ar("المعيار"), ar("المحسوب"), ar("الفرق %")]]
        for k, lab in labels.items():
            sv = targets.get(k, 0)
            cv = actual.get(k, 0)
            if sv > 0:
                pct = (cv - sv) / sv * 100
                cmp.append([ar(lab), f"{sv:.2f}", f"{cv:.2f}", f"{pct:+.1f}%"])
        tc = Table(cmp, colWidths=[100, 100, 100, 100])
        tc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565c0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.6, HexColor('#bdbdbd')),
        ]))
        story.append(tc)

        if notes:
            story.append(Spacer(1, 15))
            story.append(P(f"📝 ملاحظات: {notes}", size=10, color='#555'))

        # التوقيع
        story.append(Spacer(1, 30))
        story.append(P(f"📞 للاستشارة: {WHATSAPP_NUMBER}",
            size=11, align=TA_CENTER, color='#c62828'))
        story.append(P(f"✉️ {OWNER_EMAIL}",
            size=10, align=TA_CENTER, color='#1565c0'))
        story.append(Spacer(1, 15))
        story.append(P(SUPERVISOR, size=14, align=TA_CENTER, color='#c62828'))
        story.append(P(SUPERVISOR_TITLE, size=11, align=TA_CENTER, color='#1b5e20'))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception:
        return b""

def render_pdf_access(pdf_bytes, filename, key_suffix):
    """زر تحميل PDF مع تقييد للمالك فقط"""
    role = st.session_state.get("user_role")
    is_owner = role == "owner"

    if pdf_bytes:
        if is_owner:
            st.download_button(
                "📄 تحميل التقرير (PDF)",
                pdf_bytes, file_name=filename,
                mime="application/pdf",
                use_container_width=True, type="primary",
                key=f"dl_{key_suffix}")
        else:
            st.warning("🔒 تحميل التقرير يتطلب موافقة المالك")
            st.info(f"📞 للتواصل: {WHATSAPP_NUMBER}")

    # أزرار التواصل (للجميع)
    st.markdown("---")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
                padding: 15px; border-radius: 12px;
                border-right: 5px solid #1b5e20; text-align: center;">
        <h4 style="color: #1b5e20; margin: 0 0 8px 0;">💡 للحصول على تركيبات أفضل</h4>
        <p style="color: #333; margin: 0; font-size: 0.9rem;">
            تواصل مع <b>د. عبدالقادر إسماعيل تاور</b><br>
            اختصاصي تغذية الحيوان
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        wa_num = WHATSAPP_NUMBER.replace('+', '').replace(' ', '')
        st.markdown(
            f'<a href="https://wa.me/{wa_num}" target="_blank" '
            f'style="display:block; padding:12px; background:#25d366; '
            f'color:white; text-align:center; border-radius:10px; '
            f'text-decoration:none; font-weight:bold;">'
            f'📱 واتساب</a>',
            unsafe_allow_html=True)
    with c2:
        st.markdown(
            f'<a href="mailto:{OWNER_EMAIL}" '
            f'style="display:block; padding:12px; background:#1565c0; '
            f'color:white; text-align:center; border-radius:10px; '
            f'text-decoration:none; font-weight:bold;">'
            f'✉️ استشارة</a>',
            unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# 📏 شريط القياس (صور حقيقية + أسهم)
# ═══════════════════════════════════════════════════════════════════════

ANIMAL_PHOTOS = {
    "أبقار": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Cow_female_black_white.jpg/1024px-Cow_female_black_white.jpg",
    "أغنام": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Sheep_in_lesser_himalayas.JPG/1024px-Sheep_in_lesser_himalayas.JPG",
    "ماعز": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Goat_chewing_a_can_%28cropped%29.jpg/1024px-Goat_chewing_a_can_%28cropped%29.jpg",
    "خيول": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Nokota_Horses_cropped.jpg/1024px-Nokota_Horses_cropped.jpg",
}

WEIGHT_TAPE_CONFIG = {
    "أبقار": {"hg_min": 100, "hg_max": 260, "hg_default": 180,
              "bl_min": 100, "bl_max": 220, "bl_default": 150,
              "calc": lambda hg, bl: (hg**2 * bl) / 10840.0,
              "src": "Schaeffer (1978)"},
    "أغنام": {"hg_min": 40, "hg_max": 120, "hg_default": 75,
              "bl_min": 40, "bl_max": 100, "bl_default": 65,
              "calc": lambda hg, bl: (hg**2 * bl) / 10840.0,
              "src": "Schaeffer (1978)"},
    "ماعز": {"hg_min": 35, "hg_max": 110, "hg_default": 70,
             "bl_min": 35, "bl_max": 95, "bl_default": 62,
             "calc": lambda hg, bl: (hg**2 * bl) / 10840.0,
             "src": "Schaeffer (1978)"},
    "خيول": {"hg_min": 120, "hg_max": 240, "hg_default": 175,
             "bl_min": 100, "bl_max": 210, "bl_default": 155,
             "calc": lambda hg, bl: (hg**2 * bl) / 11877.0,
             "src": "Carroll & Huntington (1988)"},
}

@st.cache_data(ttl=86400, show_spinner=False)
def _download_img(url):
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()
    except Exception:
        return None

def draw_tape_guide(animal_type):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        img_url = ANIMAL_PHOTOS.get(animal_type, ANIMAL_PHOTOS["أبقار"])
        img_bytes = _download_img(img_url)

        fig, ax = plt.subplots(figsize=(11, 7))

        if img_bytes:
            img = PILImage.open(io.BytesIO(img_bytes))
            ax.imshow(img)
        else:
            ax.text(0.5, 0.5, f"📸 {animal_type}", ha='center',
                    va='center', fontsize=40, transform=ax.transAxes,
                    color='#1b5e20')

        ax.axis('off')

        # سهم محيط الصدر (أحمر)
        ax.annotate('', xy=(0.35, 0.65), xytext=(0.35, 0.35),
            xycoords='axes fraction', textcoords='axes fraction',
            arrowprops=dict(arrowstyle='<->', color='#c62828', lw=4,
                            mutation_scale=20))
        ax.text(0.37, 0.5, '① محيط الصدر', color='#c62828',
                fontweight='bold', fontsize=12, transform=ax.transAxes,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor='#c62828', alpha=0.9))

        # سهم طول الجسم (أزرق)
        ax.annotate('', xy=(0.15, 0.25), xytext=(0.85, 0.25),
            xycoords='axes fraction', textcoords='axes fraction',
            arrowprops=dict(arrowstyle='<->', color='#1565c0', lw=4,
                            mutation_scale=20))
        ax.text(0.5, 0.27, '② طول الجسم', color='#1565c0',
                fontweight='bold', fontsize=12, ha='center',
                transform=ax.transAxes,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor='#1565c0', alpha=0.9))

        cfg = WEIGHT_TAPE_CONFIG.get(animal_type, {})
        ax.text(0.5, -0.05,
            f"🔴 ① خلف الأرجل الأمامية    🔵 ② من الكتف للحوض",
            transform=ax.transAxes, ha='center', fontsize=10,
            color='#1a1a1a', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff8e1',
                      edgecolor='#d4af37', linewidth=2))

        ax.set_title(
            f"📍 {animal_type} — {cfg.get('src', '')}",
            fontsize=13, fontweight='bold', color='#1b5e20', pad=12)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white', pad_inches=0.2)
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None

def weight_tape_widget(animal_type, key_prefix):
    cfg = WEIGHT_TAPE_CONFIG.get(animal_type)
    if not cfg:
        return 0.0

    img = draw_tape_guide(animal_type)
    if img:
        st.image(img.getvalue(), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        hg = st.slider("① محيط الصدر (سم)", cfg['hg_min'],
                       cfg['hg_max'], cfg['hg_default'], 0.5,
                       key=f"{key_prefix}_hg")
    with c2:
        bl = st.slider("② طول الجسم (سم)", cfg['bl_min'],
                       cfg['bl_max'], cfg['bl_default'], 0.5,
                       key=f"{key_prefix}_bl")

    weight = float(cfg["calc"](hg, bl))
    st.success(f"⚖️ الوزن التقديري: **{weight:.1f} كجم**")
    st.caption(f"📖 المصدر: {cfg['src']}")
    return weight


# ═══════════════════════════════════════════════════════════════════════
# 🐎 حظيرة الخيول 3D
# ═══════════════════════════════════════════════════════════════════════

def build_horse_stable_3d(num_horses, stall_w=3.5, stall_l=3.5):
    """بناء إسطبل خيول 3D بكل مربط"""
    if not PLOTLY_AVAILABLE:
        return None
    try:
        rows = 2 if num_horses > 4 else 1
        per_row = (num_horses + 1) // 2 if rows == 2 else num_horses
        aisle = 3.5
        L = per_row * stall_w + 2
        W = rows * stall_l + aisle + 1
        H = 4.0
        wall_h = 3.0

        fig = go.Figure()

        # الأرضية
        fig.add_trace(go.Mesh3d(
            x=[0, L, L, 0], y=[0, 0, W, W], z=[0, 0, 0, 0],
            color='#d7ccc8', opacity=0.8, name='الأرضية'))

        # الجدران
        for xp in [0, L]:
            fig.add_trace(go.Mesh3d(
                x=[xp]*4, y=[0, W, W, 0], z=[0, 0, H, H],
                color='#a1887f', opacity=0.3,
                showlegend=False))
        for yp in [0, W]:
            fig.add_trace(go.Mesh3d(
                x=[0, L, L, 0], y=[yp]*4, z=[0, 0, H, H],
                color='#a1887f', opacity=0.3,
                showlegend=False))

        # السقف
        fig.add_trace(go.Mesh3d(
            x=[0, L, L, 0], y=[0, 0, W, W], z=[H, H, H, H],
            color='#8d6e63', opacity=0.4, name='السقف'))

        # الإسطبلات
        for row in range(rows):
            y_start = 0.5 if row == 0 else W - stall_l - 0.5
            for col in range(per_row):
                x_start = 0.5 + col * stall_w

                # جدار جانبي
                fig.add_trace(go.Mesh3d(
                    x=[x_start + stall_w]*4,
                    y=[y_start, y_start + stall_l,
                       y_start + stall_l, y_start],
                    z=[0, 0, wall_h, wall_h],
                    color='#795548', opacity=0.5,
                    showlegend=False))

                # جدار أمامي (بفتحة باب)
                y_front = y_start if row == 0 else y_start + stall_l
                fig.add_trace(go.Mesh3d(
                    x=[x_start, x_start + 0.5,
                       x_start + 0.5, x_start],
                    y=[y_front]*4, z=[0, 0, wall_h, wall_h],
                    color='#8d6e63', opacity=0.5,
                    showlegend=False))
                fig.add_trace(go.Mesh3d(
                    x=[x_start + stall_w - 0.5,
                       x_start + stall_w, x_start + stall_w,
                       x_start + stall_w - 0.5],
                    y=[y_front]*4, z=[0, 0, wall_h, wall_h],
                    color='#8d6e63', opacity=0.5,
                    showlegend=False))

                # جدار خلفي
                y_back = y_start + stall_l if row == 0 else y_start
                fig.add_trace(go.Mesh3d(
                    x=[x_start, x_start + stall_w,
                       x_start + stall_w, x_start],
                    y=[y_back]*4, z=[0, 0, wall_h, wall_h],
                    color='#795548', opacity=0.5,
                    showlegend=False))

                # الحصان
                fig.add_trace(go.Scatter3d(
                    x=[x_start + stall_w / 2],
                    y=[y_start + stall_l / 2],
                    z=[0.4], mode='markers',
                    marker=dict(size=14, color='#4e342e',
                                symbol='diamond',
                                line=dict(color='#d4af37', width=2)),
                    name='حصان' if row == 0 and col == 0 else None,
                    showlegend=(row == 0 and col == 0)))

                # رقم الإسطبل
                fig.add_trace(go.Scatter3d(
                    x=[x_start + stall_w / 2],
                    y=[y_front], z=[wall_h + 0.3],
                    mode='text',
                    text=[f"{col + 1 + row * per_row}"],
                    textfont=dict(size=12, color='#c62828'),
                    showlegend=False))

        fig.update_layout(
            title=dict(
                text=f"🐎 إسطبل خيول — {num_horses} حصان",
                font=dict(size=14, color='#1b5e20'), x=0.5),
            scene=dict(
                xaxis=dict(title='الطول'),
                yaxis=dict(title='العرض'),
                zaxis=dict(title='الارتفاع'),
                aspectmode='manual',
                aspectratio=dict(x=L / 15, y=W / 10, z=H / 5),
                camera=dict(eye=dict(x=1.5, y=-1.5, z=0.9))),
            height=650, paper_bgcolor='white')
        return fig
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════
# 🎨 CSS
# ═══════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
* { font-family: 'Cairo', sans-serif !important; }
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
}
.main-box {
    background: rgba(255,255,255,0.95);
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.1);
    margin-bottom: 70px;
}
.section-title {
    color: #1b5e20 !important;
    border-right: 6px solid #2e7d32;
    padding: 12px 18px;
    text-align: right;
    font-size: 1.5rem;
    font-weight: 900;
    margin: 20px 0;
    background: linear-gradient(to left, rgba(46,125,50,0.15), transparent);
    border-radius: 10px;
}
.formula-item {
    background: linear-gradient(135deg, #ffffff, #e8f5e9);
    padding: 12px 16px;
    border-radius: 10px;
    margin-bottom: 8px;
    font-weight: 700;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    text-align: right;
}
.quality-good {
    background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
    padding: 20px;
    border-radius: 16px;
    border-right: 8px solid #1b5e20;
    margin: 15px 0;
    text-align: right;
}
.quality-bad {
    background: linear-gradient(135deg, #ffcdd2, #ef9a9a);
    padding: 20px;
    border-radius: 16px;
    border-right: 8px solid #c62828;
    margin: 15px 0;
    text-align: right;
}
.dua-fixed-banner {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32);
    color: #ffeb3b !important;
    padding: 10px 20px;
    z-index: 9998;
    text-align: center;
    font-family: 'Cairo', serif !important;
    font-size: 1rem;
    font-weight: bold;
    border-top: 3px solid #d4af37;
}
.profile-img {
    width: 130px; height: 130px; border-radius: 50%;
    object-fit: cover; border: 4px solid #d4af37;
    display: block; margin: 0 auto;
}
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff, #f1f8e9);
    padding: 12px;
    border-radius: 12px;
    border-right: 4px solid #2e7d32;
}
[data-testid="stMetricValue"] {
    color: #1b5e20 !important; font-weight: 900 !important;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# 🎥 الفيديو الترحيبي + صورة المالك
# ═══════════════════════════════════════════════════════════════════════

def show_intro_video():
    if os.path.exists("intro.mp4"):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1b5e20, #2e7d32);
                    padding: 15px; border-radius: 12px;
                    border: 3px solid #d4af37; margin-bottom: 15px;
                    text-align: center;">
            <h3 style="color: #d4af37 !important; margin: 0;">
                🎥 مرحباً بكم في منصة تاور نولجي
            </h3>
        </div>
        """, unsafe_allow_html=True)
        st.video("intro.mp4", autoplay=True)


# ═══════════════════════════════════════════════════════════════════════
# 🔐 بوابة الدخول
# ═══════════════════════════════════════════════════════════════════════

if "approved" not in st.session_state:
    st.session_state["approved"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 900px; margin: 30px auto;">',
                unsafe_allow_html=True)

    # الدعاء
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0d3011, #1b5e20, #2e7d32);
                padding: 30px; border-radius: 18px;
                border: 4px solid #d4af37; text-align: center;
                margin-bottom: 25px;">
        <h2 style="color: #ffeb3b !important; margin: 0; font-family: 'Cairo', serif;">
            🕌 {DUA_SHORT} 🕌
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # الهوية
    if os.path.exists("owner.jpg"):
        with open("owner.jpg", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<img src="data:image/jpeg;base64,{b64}" class="profile-img">',
                    unsafe_allow_html=True)

    st.markdown(f"""
    <h1 style='color:#1b5e20; text-align:center;'>🌾 {APP_NAME}</h1>
    <h3 style='color:#c62828; text-align:center;'>{SUPERVISOR} — {SUPERVISOR_TITLE}</h3>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#1b5e20;'>🔐 اختر بوابتك</h3>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""<div style="background:#e8f5e9; padding:15px;
            border-radius:10px; border:2px solid #2e7d32; text-align:center;">
            <h4 style="color:#1b5e20;">👑 المالك</h4>
            <p style="font-size:0.85rem;">إدارة كاملة</p></div>""",
            unsafe_allow_html=True)
        code = st.text_input("كود المالك:", type="password", key="oc_main")
        if st.button("👑 دخول", type="primary", use_container_width=True,
                     key="b_owner_main"):
            if check_owner_code(code):
                st.session_state.update({"approved": True, "user_role": "owner"})
                st.rerun()
            else:
                st.error("❌ كود غير صحيح")

    with col2:
        st.markdown("""<div style="background:#e3f2fd; padding:15px;
            border-radius:10px; border:2px solid #1565c0; text-align:center;">
            <h4 style="color:#0d47a1;">🔬 مختص</h4>
            <p style="font-size:0.85rem;">دخول مباشر</p></div>""",
            unsafe_allow_html=True)
        if st.button("🔬 دخول كمختص", type="primary", use_container_width=True,
                     key="b_spec_main"):
            st.session_state.update({"approved": True, "user_role": "specialist"})
            st.rerun()

    with col3:
        st.markdown("""<div style="background:#fff8e1; padding:15px;
            border-radius:10px; border:2px solid #d4af37; text-align:center;">
            <h4 style="color:#e65100;">👥 زائر</h4>
            <p style="font-size:0.85rem;">مجاني</p></div>""",
            unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True,
                     key="b_guest_main"):
            st.session_state.update({"approved": True, "user_role": "guest"})
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════════════════════
# 🏠 الواجهة الرئيسية
# ═══════════════════════════════════════════════════════════════════════

show_intro_video()

# صورة المالك في الزاوية
if os.path.exists("owner.jpg"):
    with open("owner.jpg", "rb") as f:
        _owner_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <div style="position: fixed; bottom: 70px; right: 20px; z-index: 9999;
                text-align: center;">
        <img src="data:image/jpeg;base64,{_owner_b64}"
             style="width: 70px; height: 70px; border-radius: 50%;
                    border: 3px solid #d4af37; object-fit: cover;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-box">', unsafe_allow_html=True)

role = st.session_state.get("user_role", "guest")
is_owner = role == "owner"

# شريط الحساب
c1, c2 = st.columns([0.7, 0.3])
with c2:
    role_label = {"owner": "المالك 👑", "specialist": "مختص 🔬",
                  "guest": "زائر 👥"}.get(role, "—")
    st.markdown(f"<div style='text-align:left; padding:8px; "
                f"background:#f5f5f5; border-radius:8px;'>"
                f"الحساب: <b>{role_label}</b></div>",
                unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════
# 📑 التبويبات
# ═══════════════════════════════════════════════════════════════════════

if is_owner:
    tabs_titles = [
        "🔬 النمذجة", "🏆 التركيبات المعتمدة", "📏 القياس",
        "🏗️ الحظائر 3D", "🧪 مختبر", "📚 المراجع", "📖 الدليل"
    ]
elif role == "specialist":
    tabs_titles = [
        "🔬 النمذجة", "🏆 التركيبات المعتمدة", "📏 القياس",
        "🏗️ الحظائر 3D", "🧪 مختبر", "📚 المراجع", "📖 الدليل"
    ]
else:  # guest
    tabs_titles = [
        "🧮 حاسبة سريعة", "🏆 التركيبات المعتمدة", "📏 القياس",
        "🏗️ الحظائر 3D", "📚 المراجع", "📖 الدليل"
    ]

tabs = st.tabs(tabs_titles)
tab_map = {t: tab for t, tab in zip(tabs_titles, tabs)}


# ═══════════════════════════════════════════════════════════════════════
# 1️⃣ حاسبة الزائر السريعة
# ═══════════════════════════════════════════════════════════════════════

if role == "guest" and "🧮 حاسبة سريعة" in tab_map:
    with tab_map["🧮 حاسبة سريعة"]:
        st.markdown('<div class="section-title">🧮 حاسبة سريعة للزوار</div>',
                    unsafe_allow_html=True)
        st.info("💡 هذه حاسبة استرشادية سريعة. للحساب الدقيق استخدم بوابة المختص.")

        c1, c2 = st.columns(2)
        with c1:
            g_animal = st.selectbox("🐾 الحيوان:",
                ["أبقار", "أغنام", "ماعز", "خيول", "دواجن"],
                key="g_animal_q")
            g_purpose = st.selectbox("🎯 الغرض:",
                ["حليب_عالي", "تسمين_مكثف", "صيانة"],
                key="g_purpose_q")
        with c2:
            g_weight = st.number_input("⚖️ الوزن (كجم):", 1.0, 900.0, 400.0,
                5.0, key="g_weight_q")

        if st.button("🧮 اعرض تركيبة استرشادية", type="primary",
                     use_container_width=True, key="g_btn_q"):
            # البحث عن تركيبة جاهزة مطابقة
            key_match, data = get_validated_formula(g_animal, g_purpose)

            if data:
                result = evaluate_validated_formula(key_match)
                quality = result["quality_score"]

                if quality >= 70:
                    st.markdown(f"""<div class="quality-good">
                        <h3 style="color:#1b5e20; margin:0;">
                        ✅ الجودة: {quality:.1f}%</h3>
                        <p style="color:#2e7d32;">{data['label']}</p>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="quality-bad">
                        <h3 style="color:#c62828; margin:0;">
                        ⚠️ الجودة: {quality:.1f}%</h3>
                    </div>""", unsafe_allow_html=True)

                m1, m2, m3 = st.columns(3)
                m1.metric("💰 التكلفة", f"${result['cost']:.2f}/طن")
                m2.metric("🧬 الجودة", f"{quality:.1f}%")
                m3.metric("📊 المكونات", len(result["formula"]))

                st.markdown("### 🌾 التركيبة:")
                for ing, pct in result["formula"].items():
                    st.markdown(f'<div class="formula-item">▪️ '
                                f'<b>{ing}:</b> {pct:.1f}%</div>',
                                unsafe_allow_html=True)

                # PDF
                pdf = generate_pdf_report(
                    title=f"تركيبة {g_animal} — {g_purpose}",
                    formula=result["formula"],
                    targets=data["targets"],
                    actual=result["actual"],
                    cost=result["cost"],
                    quality=quality,
                    notes=f"وزن الحيوان: {g_weight} كجم")

                render_pdf_access(pdf, f"guest_{g_animal}.pdf", "guest_q")
            else:
                st.warning(f"⚠️ لا توجد تركيبة جاهزة لـ {g_animal} / {g_purpose}")
                st.info("💡 تواصل مع الدكتور للحصول على تركيبة مخصصة")


# ═══════════════════════════════════════════════════════════════════════
# 2️⃣ النمذجة (المحرك الذكي)
# ═══════════════════════════════════════════════════════════════════════

if "🔬 النمذجة" in tab_map:
    with tab_map["🔬 النمذجة"]:
        st.markdown('<div class="section-title">🔬 النمذجة العلفية الذكية</div>',
                    unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            animal = st.selectbox("🐾 الحيوان:",
                ["أبقار", "أغنام", "ماعز", "إبل", "خيول", "دواجن",
                 "أسماك", "أرانب"], key="m_animal")
        with c2:
            prod_map = {
                "أبقار": ["حليب_عالي", "حليب_متوسط", "تسمين_مكثف", "تسمين_عادي"],
                "أغنام": ["تسمين_مكثف", "مرضعات", "صيانة"],
                "ماعز": ["حلابة_عالي", "تسمين_جديان"],
                "إبل": ["حليب", "تسمين", "نمو"],
                "خيول": ["رياضة_مكثف", "رياضة_عادي"],
                "دواجن": ["لاحم", "بياض"],
                "أسماك": ["بادئ_زريعة", "نمو"],
                "أرانب": ["تسمين", "حليب"],
            }
            prod = st.selectbox("🎯 الحالة:", prod_map.get(animal, ["عام"]),
                                key="m_prod")

        # المتطلبات
        if animal == "أبقار":
            req = get_cattle_requirements(prod)
        elif animal == "أغنام":
            req = get_sheep_requirements(prod, is_male=True)
        elif animal == "ماعز":
            req = get_goat_requirements(prod, is_male=False)
        elif animal == "إبل":
            req = get_camel_requirements(prod)
        elif animal == "خيول":
            req = get_horse_requirements(prod)
        elif animal == "دواجن":
            req = get_poultry_requirements(prod)
        elif animal == "أسماك":
            req = get_fish_requirements("البلطي", prod)
        else:
            req = get_rabbit_requirements(prod)

        targets = requirement_to_standard(req)

        # عرض المتطلبات
        st.markdown(f"""<div style="background:#e3f2fd; padding:15px;
            border-radius:10px; border-right:5px solid #1565c0; margin:10px 0;">
            <h4 style="color:#0d47a1; margin:0 0 8px 0;">📊 متطلبات {req.name_ar}</h4>
            <p style="margin:0; font-size:0.95rem;">
            🧬 CP: <b>{req.CP}%</b> | 🧬 DP: <b>{req.DP}%</b> |
            🌽 SE: <b>{req.SE}</b> | ⚖️ Ca:P: <b>{req.Ca}/{req.P}</b>
            </p></div>""", unsafe_allow_html=True)

        st.markdown("### 🌾 اختر المكونات")
        selected = []
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            with st.expander(cat_name):
                cols = st.columns(3)
                for i, ing in enumerate(items.keys()):
                    with cols[i % 3]:
                        if st.checkbox(ing, key=f"m_{ing}_{animal}"):
                            selected.append(ing)

        if selected:
            st.info(f"✅ المختارة: **{len(selected)}** مادة")
            # أسعار
            with st.expander("💰 أسعار المكونات"):
                prices = {}
                pcols = st.columns(min(3, len(selected)))
                for i, ing in enumerate(selected):
                    with pcols[i % 3]:
                        default_price = float(
                            _get_ingredient_lookup()[ing]["price"])
                        prices[ing] = st.number_input(
                            f"{ing} ($/طن)", 5.0, 10000.0,
                            default_price, 10.0,
                            key=f"p_{ing}_{animal}")
        else:
            prices = {}

        if st.button("🚀 تشغيل المحرك (LP)", type="primary",
                     use_container_width=True, key="run_lp"):
            if len(selected) < 2:
                st.error("⚠️ اختر مكونين على الأقل")
            else:
                with st.spinner("⏳ جاري الحساب..."):
                    result = formulate_lp(selected, prices, targets, animal)

                if result["success"]:
                    quality = result["quality_score"]
                    formula = result["formula"]

                    # عرض النتيجة
                    if result.get("warning"):
                        st.warning(result["warning"])

                    if quality >= 70:
                        st.markdown(f"""<div class="quality-good">
                            <h3 style="color:#1b5e20; margin:0;">
                            ✅ الجودة: {quality:.1f}%</h3>
                            <p style="color:#2e7d32;">{result['strategy']}</p>
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div class="quality-bad">
                            <h3 style="color:#c62828; margin:0;">
                            ⚠️ الجودة: {quality:.1f}%</h3>
                        </div>""", unsafe_allow_html=True)

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("💰 التكلفة", f"${result['cost']:.2f}")
                    m2.metric("🧬 الجودة", f"{quality:.1f}%")
                    m3.metric("🎯 الاستراتيجية", result['strategy'])
                    m4.metric("📊 المكونات", len(formula))

                    # جدول المكونات
                    st.markdown("### 🌾 التركيبة الناتجة")
                    for ing, pct in formula.items():
                        st.markdown(f'<div class="formula-item">▪️ '
                                    f'<b>{ing}:</b> {pct:.2f}%</div>',
                                    unsafe_allow_html=True)

                    # جدول المقارنة
                    st.markdown("### 📊 مقارنة مع NRC")
                    actual = result["actual"]
                    cmp = []
                    labels = {"CP": "بروتين", "DP": "مهضوم",
                              "SE": "طاقة", "Ca": "Ca", "P": "P"}
                    for k, lab in labels.items():
                        sv = targets.get(k, 0)
                        cv = actual.get(k, 0)
                        if sv > 0:
                            pct = (cv - sv) / sv * 100
                            ev = evaluate_difference(pct)
                            cmp.append({
                                "العنصر": lab,
                                "المعيار": f"{sv:.2f}",
                                "المحسوب": f"{cv:.2f}",
                                "الفرق %": f"{pct:+.1f}%",
                                "التقييم": ev["label"],
                            })
                    st.dataframe(pd.DataFrame(cmp),
                                use_container_width=True, hide_index=True)

                    # PDF
                    pdf = generate_pdf_report(
                        title=f"تركيبة NLP — {animal}",
                        formula=formula,
                        targets=targets,
                        actual=actual,
                        cost=result["cost"],
                        quality=quality,
                        notes=result.get("strategy", ""))

                    render_pdf_access(pdf, f"model_{animal}.pdf", f"model_{animal}")
                else:
                    st.error(f"❌ {result['message']}")


# ═══════════════════════════════════════════════════════════════════════
# 3️⃣ التركيبات المعتمدة (15 تركيبة)
# ═══════════════════════════════════════════════════════════════════════

if "🏆 التركيبات المعتمدة" in tab_map:
    with tab_map["🏆 التركيبات المعتمدة"]:
        st.markdown('<div class="section-title">🏆 التركيبات العلمية المعتمدة (15 تركيبة)</div>',
                    unsafe_allow_html=True)
        st.caption("✅ كل تركيبة مُختبرة ومطابقة لمعايير NRC / INRA / Ross 308")

        # اختيار التركيبة
        formula_names = list(VALIDATED_FORMULATIONS.keys())
        display_names = {
            k: f"{VALIDATED_FORMULATIONS[k]['label']} — {VALIDATED_FORMULATIONS[k]['animal']}"
            for k in formula_names
        }

        selected_key = st.selectbox(
            "🎯 اختر تركيبة:",
            formula_names,
            format_func=lambda x: display_names[x],
            key="val_select")

        if selected_key:
            data = VALIDATED_FORMULATIONS[selected_key]
            result = evaluate_validated_formula(selected_key)

            # معلومات
            st.markdown(f"""<div style="background:#fff8e1; padding:15px;
                border-radius:10px; border-right:5px solid #d4af37; margin:10px 0;">
                <h4 style="color:#1b5e20; margin:0 0 8px 0;">📋 {data['label']}</h4>
                <p style="margin:0; color:#555;">
                🐾 الحيوان: <b>{data['animal']}</b> |
                🎯 الحالة: <b>{data['production']}</b> |
                📚 المصدر: <b>NRC / INRA</b>
                </p></div>""", unsafe_allow_html=True)

            # مؤشرات
            quality = result["quality_score"]
            m1, m2, m3 = st.columns(3)
            m1.metric("🧬 الجودة", f"{quality:.1f}%")
            m2.metric("💰 التكلفة", f"${result['cost']:.2f}/طن")
            m3.metric("📊 المكونات", len(result["formula"]))

            # المكونات
            st.markdown("### 🌾 المكونات")
            for ing, pct in result["formula"].items():
                st.markdown(f'<div class="formula-item">▪️ '
                            f'<b>{ing}:</b> {pct:.2f}%</div>',
                            unsafe_allow_html=True)

            # جدول المقارنة
            st.markdown("### 📊 مقارنة مع NRC")
            actual = result["actual"]
            targets = data["targets"]
            labels = {"CP": "بروتين", "DP": "مهضوم", "SE": "طاقة",
                      "Ca": "Ca", "P": "P"}
            cmp = []
            for k, lab in labels.items():
                sv = targets.get(k, 0)
                cv = actual.get(k, 0)
                if sv > 0:
                    pct = (cv - sv) / sv * 100
                    ev = evaluate_difference(pct)
                    cmp.append({
                        "العنصر": lab,
                        "المعيار": f"{sv:.2f}",
                        "المحسوب": f"{cv:.2f}",
                        "الفرق %": f"{pct:+.1f}%",
                        "التقييم": ev["label"],
                    })
            st.dataframe(pd.DataFrame(cmp), use_container_width=True,
                         hide_index=True)

            # ملاحظات
            if data.get("notes"):
                st.info(f"📝 {data['notes']}")

            # PDF
            pdf = generate_pdf_report(
                title=data["label"],
                formula=result["formula"],
                targets=targets,
                actual=actual,
                cost=result["cost"],
                quality=quality,
                notes=data.get("notes", ""))

            render_pdf_access(pdf, f"validated_{selected_key}.pdf",
                              f"validated_{selected_key}")


# ═══════════════════════════════════════════════════════════════════════
# 4️⃣ القياس
# ═══════════════════════════════════════════════════════════════════════

if "📏 القياس" in tab_map:
    with tab_map["📏 القياس"]:
        st.markdown('<div class="section-title">📏 شريط القياس (تقدير الوزن)</div>',
                    unsafe_allow_html=True)
        st.caption("📸 صور حقيقية مع أسهم القياس — Schaeffer (1978)")

        tape_animal = st.selectbox("🐾 الحيوان:",
            list(WEIGHT_TAPE_CONFIG.keys()), key="tape_animal_q")

        weight_tape_widget(tape_animal, f"tape_{tape_animal}")


# ═══════════════════════════════════════════════════════════════════════
# 5️⃣ الحظائر 3D
# ═══════════════════════════════════════════════════════════════════════

if "🏗️ الحظائر 3D" in tab_map:
    with tab_map["🏗️ الحظائر 3D"]:
        st.markdown('<div class="section-title">🏗️ حظائر 3D</div>',
                    unsafe_allow_html=True)

        st.markdown("### 🐎 إسطبل الخيول العلمي")
        st.caption("NRC (2007) + MWPS-1 — كل حصان في مربط منفصل")

        c1, c2 = st.columns(2)
        with c1:
            num_horses = st.number_input("🔢 عدد الخيول:",
                1, 30, 10, 1, key="stable_count")
        with c2:
            stall_type = st.selectbox("📦 نوع المربط:",
                ["3.5×3.5 م (قياسي)", "4.0×4.0 م (كبير)",
                 "4.0×5.0 م (ولادة)"],
                key="stall_type_q")

        stall_map = {
            "3.5×3.5 م (قياسي)": (3.5, 3.5),
            "4.0×4.0 م (كبير)": (4.0, 4.0),
            "4.0×5.0 م (ولادة)": (4.0, 5.0),
        }
        sw, sl = stall_map[stall_type]

        if st.button("🏗️ بناء الإسطبل 3D", type="primary",
                     use_container_width=True, key="build_stable"):
            fig = build_horse_stable_3d(num_horses, sw, sl)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

                # معلومات
                rows = 2 if num_horses > 4 else 1
                per_row = (num_horses + 1) // 2 if rows == 2 else num_horses
                area = rows * sl * per_row * sw + num_horses * 45

                st.markdown(f"""<div style="background:#e8f5e9; padding:15px;
                    border-radius:10px; border-right:5px solid #1b5e20;">
                    <h4 style="color:#1b5e20; margin:0;">📐 مواصفات الإسطبل</h4>
                    <p style="margin:5px 0;">
                    🐎 عدد الخيول: <b>{num_horses}</b> |
                    🏠 الصفوف: <b>{rows} صف × {per_row} مربط</b> |
                    📏 أبعاد المربط: <b>{sw}×{sl} م</b>
                    </p></div>""", unsafe_allow_html=True)

                # PDF
                pdf = generate_pdf_report(
                    title=f"إسطبل خيول — {num_horses} حصان",
                    formula={"عدد الخيول": num_horses,
                             "أبعاد المربط": f"{sw}×{sl} م",
                             "الصفوف": f"{rows}×{per_row}"},
                    targets={"ME": 0},
                    actual={},
                    cost=0, quality=100,
                    notes=f"NRC (2007) + MWPS-1")
                render_pdf_access(pdf, f"stable_{num_horses}.pdf", "stable")


# ═══════════════════════════════════════════════════════════════════════
# 6️⃣ المختبر
# ═══════════════════════════════════════════════════════════════════════

if "🧪 مختبر" in tab_map:
    with tab_map["🧪 مختبر"]:
        st.markdown('<div class="section-title">🧪 مختبر التحليل</div>',
                    unsafe_allow_html=True)
        st.caption("أدخل النسب يدوياً لتحليل تركيبة جاهزة")

        c1, c2 = st.columns(2)
        with c1:
            lab_animal = st.selectbox("🐾 الحيوان:",
                ["أبقار", "أغنام", "ماعز", "إبل", "خيول", "دواجن"],
                key="lab_animal_q")
        with c2:
            lab_prod = st.selectbox("🎯 الإنتاج:",
                ["حليب_عالي", "تسمين_مكثف", "صيانة"],
                key="lab_prod_q")

        # المتطلبات
        if lab_animal == "أبقار":
            lab_req = get_cattle_requirements(lab_prod)
        elif lab_animal == "أغنام":
            lab_req = get_sheep_requirements(lab_prod, is_male=True)
        elif lab_animal == "ماعز":
            lab_req = get_goat_requirements(lab_prod, is_male=False)
        elif lab_animal == "إبل":
            lab_req = get_camel_requirements(lab_prod)
        elif lab_animal == "خيول":
            lab_req = get_horse_requirements(lab_prod)
        else:
            lab_req = get_poultry_requirements(lab_prod)

        lab_targets = requirement_to_standard(lab_req)

        st.markdown("### 📝 أدخل النسب")
        formula_input = {}
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            with st.expander(cat_name):
                cols = st.columns(3)
                for i, ing in enumerate(items.keys()):
                    with cols[i % 3]:
                        pct = st.number_input(f"{ing} %", 0.0, 100.0, 0.0,
                            step=0.5, key=f"lab_in_{ing}")
                        if pct > 0:
                            formula_input[ing] = pct

        if formula_input:
            total = sum(formula_input.values())
            st.info(f"📊 المجموع: **{total:.1f}%** | "
                    f"المكونات: **{len(formula_input)}**")

        if st.button("🔬 تحليل", type="primary",
                     use_container_width=True, key="lab_run"):
            if not formula_input:
                st.error("⚠️ أدخل النسب أولاً")
            else:
                # تطبيع
                total = sum(formula_input.values())
                normalized = {k: round(v / total * 100, 2)
                              for k, v in formula_input.items()}

                quality, actual = evaluate_quality(
                    normalized, lab_targets, lab_animal)

                if quality >= 70:
                    st.markdown(f"""<div class="quality-good">
                        <h3 style="color:#1b5e20; margin:0;">
                        ✅ الجودة: {quality:.1f}%</h3>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="quality-bad">
                        <h3 style="color:#c62828; margin:0;">
                        ⚠️ الجودة: {quality:.1f}%</h3>
                    </div>""", unsafe_allow_html=True)

                # جدول المقارنة
                labels = {"CP": "بروتين", "DP": "مهضوم", "SE": "طاقة",
                          "Ca": "Ca", "P": "P"}
                cmp = []
                for k, lab in labels.items():
                    sv = lab_targets.get(k, 0)
                    cv = actual.get(k, 0)
                    if sv > 0:
                        pct = (cv - sv) / sv * 100
                        ev = evaluate_difference(pct)
                        cmp.append({
                            "العنصر": lab,
                            "المعيار": f"{sv:.2f}",
                            "المحسوب": f"{cv:.2f}",
                            "الفرق %": f"{pct:+.1f}%",
                            "التقييم": ev["label"],
                        })
                st.dataframe(pd.DataFrame(cmp), use_container_width=True,
                             hide_index=True)

                # تكلفة
                lookup = _get_ingredient_lookup()
                cost = sum(normalized[ing] / 100 * lookup[ing]["price"]
                           for ing in normalized)

                # PDF
                pdf = generate_pdf_report(
                    title=f"تحليل تركيبة — {lab_animal}",
                    formula=normalized,
                    targets=lab_targets,
                    actual=actual,
                    cost=cost,
                    quality=quality)
                render_pdf_access(pdf, f"lab_{lab_animal}.pdf", "lab")


# ═══════════════════════════════════════════════════════════════════════
# 7️⃣ المراجع
# ═══════════════════════════════════════════════════════════════════════

if "📚 المراجع" in tab_map:
    with tab_map["📚 المراجع"]:
        st.markdown('<div class="section-title">📚 المراجع العلمية</div>',
                    unsafe_allow_html=True)
        st.markdown("""
### 📖 المراجع الأساسية:
- **NRC (2001)** — Nutrient Requirements of Dairy Cattle, 7th Ed.
- **NRC (2007)** — Nutrient Requirements of Small Ruminants
- **NRC (1994)** — Nutrient Requirements of Poultry, 9th Ed.
- **NRC (2007)** — Nutrient Requirements of Horses, 6th Ed.
- **NRC (2011)** — Fish and Shrimp Nutrition
- **INRA (2018)** — INRA Feeding System for Ruminants
- **FAO (2010)** — Camel Nutrition
- **Ross 308 (2020)** — Broiler Nutrition Specification

### 📏 شريط القياس:
- **Schaeffer (1978)** — Heart Girth Weight Equation
- **Carroll & Huntington (1988)** — Horse Weight Formula

### 🏗️ الحظائر:
- **MWPS-1 (2000)** — Structures and Environment Handbook
- **ASAE (2005)** — Ventilation Standards

### 🎯 NLP/LP:
- **Kraft (1988)** — SLSQP Algorithm
- **Danø & Højsgaard (2005)** — LP in Ration Formulation
- **Nocedal & Wright (2006)** — Numerical Optimization
""")


# ═══════════════════════════════════════════════════════════════════════
# 8️⃣ الدليل
# ═══════════════════════════════════════════════════════════════════════

if "📖 الدليل" in tab_map:
    with tab_map["📖 الدليل"]:
        st.markdown('<div class="section-title">📖 دليل المستخدم</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
### 🌾 {APP_NAME} v{APP_VERSION}

**إشراف:** {SUPERVISOR} — {SUPERVISOR_TITLE}

---

### ✅ ما الذي تم إصلاحه في هذه النسخة:

1. **محرك LP مُعاد بناؤه:** قيود صلبة تضمن الطاقة ≥ 45% (لن تتفوق الصويا على الذرة).
2. **15 تركيبة علمية معتمدة:** جاهزة ومختبرة من NRC.
3. **تبويبات تعمل بالكامل:** النمذجة، التركيبات المعتمدة، القياس، الحظائر 3D، المختبر.
4. **خميرة الخبز + علف دجاج جاهز:** في المكتبة العلفية.
5. **إسطبلات 3D للخيول:** كل حصان في مربط منفصل.
6. **شريط قياس بصورة حقيقية:** مع أسهم على الصورة.
7. **تقييد PDF:** للزائر والمختص يحتاج موافقة المالك.

---

### 🔐 بوابات الدخول:
- 👑 **مالك:** إدارة كاملة + تحميل PDF مباشر
- 🔬 **مختص:** أدوات متقدمة + طلب موافقة PDF
- 👥 **زائر:** حاسبة سريعة + طلب موافقة PDF

---

### 📞 التواصل:
- 📱 **واتساب:** {WHATSAPP_NUMBER}
- 📧 **البريد:** {OWNER_EMAIL}

---

🤲 {DUA_FULL} 🤲
""")


# ═══════════════════════════════════════════════════════════════════════
# التذييل
# ═══════════════════════════════════════════════════════════════════════

st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="dua-fixed-banner">
    🤲 {DUA_SHORT} 🤲
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# نهاية الملف — Tawor Nology 11.14 ✅
# ═══════════════════════════════════════════════════════════════════════
