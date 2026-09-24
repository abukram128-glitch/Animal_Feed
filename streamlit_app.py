# ============================================================================
# ██████████████████████████████████████████████████████████████████████████
# █                                                                        █
# █            تاور نولجي TAWOR NOLOGY — الإصدار 7.0                       █
# █            للإنتاج الحيواني وتغذية الحيوان                             █
# █            إشراف: م. عبدالقادر إسماعيل تاور                             █
# █            اختصاصي تغذية الحيوان                                        █
# █                                                                        █
# █  🕌 رحم الله والدي إسماعيل تاور وأختي 🕌                              █
# █                                                                        █
# ██████████████████████████████████████████████████████████████████████████
# ============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import json, os, sys, base64, time, re, io, sqlite3, hashlib, secrets, warnings
import urllib.parse, smtplib
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

warnings.filterwarnings('ignore')

# ─── مكتبات علمية ───
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
    import matplotlib.patches as mpatches
    from matplotlib.patches import Circle, Wedge
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

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
    from reportlab.platypus import (
        Table, TableStyle, Paragraph, Spacer, Image,
        SimpleDocTemplate, HRFlowable, PageBreak
    )
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

try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════
# الدعاء المبسط — رحم الله والدي إسماعيل تاور وأختي
# ═══════════════════════════════════════════════════════════════════════════

DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي"
DUA_FULL = "رحم الله والدي إسماعيل تاور وأختي، وأسكنهما فسيح جناته، وجعل قبرهما روضة من رياض الجنة"
DUA_QURAN = "﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾"
DUA_VISITOR_BANNER = """
🕌 <b>إلى زوارنا الكرام:</b><br>
هذه المنصة صدقةٌ جارية عن <b>والدي إسماعيل تاور وأختي</b>.<br>
نسألكم بظهر الغيب أن تشاركونا الدعاء لهما. 🤲
"""
DUA_HEADER = "🤲 رحم الله والدي إسماعيل تاور وأختي"


# ═══════════════════════════════════════════════════════════════════════════
# الإعدادات الأساسية
# ═══════════════════════════════════════════════════════════════════════════

APP_VERSION = "7.0.0"
APP_NAME = "تاور نولجي Tawor Nology"
APP_TAGLINE = "للإنتاج الحيواني وتغذية الحيوان"
SUPERVISOR = "م. عبدالقادر إسماعيل تاور"
SUPERVISOR_TITLE = "اختصاصي تغذية الحيوان"
OWNER_CODE = "202687"  # كود المالك الوحيد
PLATFORM_URL = "https://tawor-nology.streamlit.app"
WHATSAPP_NUMBER = "+249123533489"
OWNER_EMAIL = "abukram128@gmail.com"
DB_FILE = "tawor_nology.db"
CITY_PRICES_FILE = "tawor_city_prices.json"
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]
LOGO_OPTIONS = ["logo.png", "logo.jpg", "LOGO.PNG"]

st.set_page_config(
    page_title=f"{APP_NAME} | {APP_TAGLINE}",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ═══════════════════════════════════════════════════════════════════════════
# معالج النصوص العربية
# ═══════════════════════════════════════════════════════════════════════════

class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=2000)
    def fix(text: str) -> str:
        if not text:
            return ""
        try:
            return get_display(arabic_reshaper.reshape(str(text)))
        except Exception:
            return str(text)
    
    @staticmethod
    def normalize(text: str) -> str:
        if not text:
            return ""
        text = str(text).strip()
        for a, b in [('أ', 'ا'), ('إ', 'ا'), ('آ', 'ا'), ('ى', 'ي'), ('ة', 'ه')]:
            text = text.replace(a, b)
        return text


arp = ArabicTextProcessor()
def ar(text): return arp.fix(text)


# ═══════════════════════════════════════════════════════════════════════════
# مكتبة الأعلاف الشاملة
# ═══════════════════════════════════════════════════════════════════════════

BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3, "Ca": 0.02, "P": 0.27},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4, "Ca": 0.02, "P": 0.26},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5, "Ca": 0.05, "P": 0.35},
        "شعير كامل": {"CP": 10.8, "DC": 0.75, "SE": 68.0, "NDF": 22.0, "ADF": 9.0, "EE": 2.0, "ASH": 2.8, "Ca": 0.05, "P": 0.33},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8, "Ca": 0.03, "P": 0.30},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6, "Ca": 0.04, "P": 0.32},
        "جريش أرز رزاز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2, "Ca": 0.06, "P": 0.30},
        "دخن محلي غزير": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2, "Ca": 0.05, "P": 0.31},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0, "Ca": 0.08, "P": 0.35},
        "كسرة خبز مجففة": {"CP": 10.5, "DC": 0.82, "SE": 75.0, "NDF": 8.0, "ADF": 3.5, "EE": 5.5, "ASH": 3.5, "Ca": 0.10, "P": 0.20},
        "بسكويت مكسر": {"CP": 8.5, "DC": 0.85, "SE": 85.0, "NDF": 4.0, "ADF": 2.0, "EE": 12.0, "ASH": 2.5, "Ca": 0.08, "P": 0.18},
    },
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5, "Ca": 0.20, "P": 0.65},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0, "Ca": 0.35, "P": 0.65},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2, "Ca": 0.35, "P": 0.65},
        "كسب فول صويا 46%": {"CP": 46.0, "DC": 0.905, "SE": 75.0, "NDF": 12.5, "ADF": 7.5, "EE": 1.6, "ASH": 6.1, "Ca": 0.35, "P": 0.65},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5, "Ca": 0.40, "P": 1.00},
        "كسب عباد الشمس 32%": {"CP": 32.0, "DC": 0.72, "SE": 38.0, "NDF": 42.0, "ADF": 28.0, "EE": 2.0, "ASH": 7.0, "Ca": 0.42, "P": 0.95},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5, "Ca": 0.20, "P": 1.10},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8, "Ca": 0.35, "P": 0.85},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5, "Ca": 2.00, "P": 1.20},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5, "Ca": 0.15, "P": 0.50},
        "كسب جلوتين الذرة 40%": {"CP": 40.0, "DC": 0.88, "SE": 72.0, "NDF": 15.0, "ADF": 8.0, "EE": 3.0, "ASH": 5.0, "Ca": 0.18, "P": 0.55},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5, "Ca": 0.30, "P": 0.55},
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5, "Ca": 0.12, "P": 1.10},
        "نخالة ذرة": {"CP": 9.5, "DC": 0.65, "SE": 40.0, "NDF": 40.0, "ADF": 15.0, "EE": 4.0, "ASH": 2.0, "Ca": 0.10, "P": 0.75},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5, "Ca": 1.50, "P": 0.25},
        "برسيم حجازي": {"CP": 18.0, "DC": 0.62, "SE": 38.0, "NDF": 40.0, "ADF": 30.0, "EE": 2.2, "ASH": 11.0, "Ca": 1.60, "P": 0.26},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5, "Ca": 0.70, "P": 0.05},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.30, "P": 0.08},
        "تبن فول": {"CP": 4.5, "DC": 0.40, "SE": 22.0, "NDF": 68.0, "ADF": 42.0, "EE": 1.2, "ASH": 7.5, "Ca": 0.35, "P": 0.10},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5, "Ca": 0.25, "P": 0.10},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5, "Ca": 0.15, "P": 0.08},
        "قش أرز": {"CP": 3.5, "DC": 0.30, "SE": 15.0, "NDF": 70.0, "ADF": 45.0, "EE": 1.5, "ASH": 12.0, "Ca": 0.20, "P": 0.06},
        "مخلفات النخيل (تمر مجفف)": {"CP": 6.5, "DC": 0.70, "SE": 60.0, "NDF": 25.0, "ADF": 15.0, "EE": 5.0, "ASH": 3.5, "Ca": 0.15, "P": 0.15},
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5, "Ca": 5.50, "P": 3.20},
        "مسحوق أسماك فاخر (72%)": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5, "Ca": 4.80, "P": 2.80},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5, "Ca": 9.00, "P": 4.50},
        "مسحوق الدم المجفف": {"CP": 80.0, "DC": 0.65, "SE": 55.0, "NDF": 1.0, "ADF": 0.5, "EE": 1.5, "ASH": 6.0, "Ca": 0.30, "P": 0.30},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5, "Ca": 2.50, "P": 1.20},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5, "Ca": 3.00, "P": 1.50},
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي (L-Lysine HCl)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3, "Ca": 0.0, "P": 0.0},
        "ثريونين نقي (L-Threonine)": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0},
        "تريبتوفان نقي (L-Tryptophan)": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0},
        "فالين نقي (L-Valine)": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0},
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن (Premix Broiler)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 8.0},
        "بريمكس بياض وبشاير (Layer Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 22.0, "P": 7.0},
        "بريمكس أبقار حلابة": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0},
        "بريمكس مجترات عام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 9.0},
        "بريمكس خيول وأمهار": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 8.0},
        "إنزيم الفايتيز (Phytase 5000)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0, "Ca": 0.0, "P": 0.0},
        "إنزيم الـ NSP (Xylanase+β-Glucanase)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0, "Ca": 0.0, "P": 0.0},
        "كبريتات الحديدوز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0, "Ca": 0.0, "P": 0.0},
        "مستخلص الخمائر (MOS)": {"CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.10, "P": 0.20},
        "خمائر حية (Yeast Culture)": {"CP": 45.0, "DC": 0.75, "SE": 30.0, "NDF": 8.0, "ADF": 4.0, "EE": 1.0, "ASH": 8.0, "Ca": 0.15, "P": 1.20},
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 38.0, "P": 0.0},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5, "Ca": 23.0, "P": 18.0},
        "فوسفات أحادي الكالسيوم (MCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 17.0, "P": 22.0},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9, "Ca": 0.0, "P": 0.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 0.0, "P": 0.0},
        "أكسيد المغنيسيوم العلفي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 0.0, "P": 0.0},
        "يوريا علفية محصنة": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0, "Ca": 0.0, "P": 0.0},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Ca": 0.0, "P": 0.0},
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# المعايير القياسية — NRC / INRA / FAO / Ross
# ═══════════════════════════════════════════════════════════════════════════

NUTRIENT_STANDARDS = {
    # أبقار
    "أبقار_حليب_عالي": {"CP": 18.0, "DP": 13.5, "SE": 72.0, "NDF": 32.0, "ADF": 20.0, "EE": 4.5, "ASH": 8.0, "Ca": 0.75, "P": 0.45},
    "أبقار_حليب_متوسط": {"CP": 16.0, "DP": 12.5, "SE": 68.0, "NDF": 35.0, "ADF": 22.0, "EE": 4.0, "ASH": 8.0, "Ca": 0.65, "P": 0.40},
    "أبقار_تسمين_مكثف": {"CP": 14.0, "DP": 10.5, "SE": 70.0, "NDF": 35.0, "ADF": 22.0, "EE": 4.0, "ASH": 7.5, "Ca": 0.60, "P": 0.35},
    "أبقار_تسمين_عادي": {"CP": 13.0, "DP": 10.0, "SE": 65.0, "NDF": 40.0, "ADF": 25.0, "EE": 3.5, "ASH": 7.5, "Ca": 0.55, "P": 0.32},
    "أبقار_صيانة": {"CP": 11.0, "DP": 8.0, "SE": 55.0, "NDF": 45.0, "ADF": 28.0, "EE": 3.0, "ASH": 8.0, "Ca": 0.45, "P": 0.28},
    # أغنام
    "أغنام_تسمين_مكثف": {"CP": 15.0, "DP": 12.0, "SE": 65.0, "NDF": 30.0, "ADF": 18.0, "EE": 3.8, "ASH": 8.0, "Ca": 0.65, "P": 0.35},
    "أغنام_تسمين_عادي": {"CP": 13.5, "DP": 10.5, "SE": 60.0, "NDF": 35.0, "ADF": 22.0, "EE": 3.5, "ASH": 8.0, "Ca": 0.55, "P": 0.32},
    "أغنام_حليب": {"CP": 16.0, "DP": 12.8, "SE": 66.0, "NDF": 30.0, "ADF": 19.0, "EE": 4.0, "ASH": 8.5, "Ca": 0.75, "P": 0.42},
    "أغنام_صيانة": {"CP": 11.0, "DP": 8.0, "SE": 50.0, "NDF": 45.0, "ADF": 28.0, "EE": 3.0, "ASH": 8.0, "Ca": 0.45, "P": 0.28},
    # ماعز
    "ماعز_تسمين": {"CP": 14.5, "DP": 11.5, "SE": 62.0, "NDF": 33.0, "ADF": 20.0, "EE": 3.5, "ASH": 8.0, "Ca": 0.60, "P": 0.35},
    "ماعز_حليب": {"CP": 16.5, "DP": 13.0, "SE": 67.0, "NDF": 30.0, "ADF": 18.0, "EE": 4.0, "ASH": 8.5, "Ca": 0.75, "P": 0.42},
    "ماعز_صيانة": {"CP": 10.5, "DP": 7.8, "SE": 48.0, "NDF": 45.0, "ADF": 28.0, "EE": 3.0, "ASH": 8.0, "Ca": 0.45, "P": 0.28},
    # إبل
    "إبل_نمو": {"CP": 14.0, "DP": 10.5, "SE": 60.0, "NDF": 38.0, "ADF": 24.0, "EE": 3.5, "ASH": 8.0, "Ca": 0.65, "P": 0.38},
    "إبل_تسمين": {"CP": 13.0, "DP": 9.5, "SE": 65.0, "NDF": 35.0, "ADF": 22.0, "EE": 3.8, "ASH": 7.5, "Ca": 0.60, "P": 0.35},
    "إبل_حليب": {"CP": 17.0, "DP": 13.0, "SE": 68.0, "NDF": 32.0, "ADF": 20.0, "EE": 4.5, "ASH": 8.5, "Ca": 0.80, "P": 0.45},
    "إبل_سباق": {"CP": 18.0, "DP": 14.0, "SE": 72.0, "NDF": 30.0, "ADF": 18.0, "EE": 5.0, "ASH": 9.0, "Ca": 0.85, "P": 0.50},
    "إبل_صيانة": {"CP": 10.0, "DP": 7.5, "SE": 50.0, "NDF": 45.0, "ADF": 28.0, "EE": 3.0, "ASH": 8.0, "Ca": 0.45, "P": 0.28},
    # خيول
    "خيول_رياضة": {"CP": 12.0, "DP": 9.5, "SE": 65.0, "NDF": 35.0, "ADF": 22.0, "EE": 4.5, "ASH": 7.5, "Ca": 0.55, "P": 0.32},
    "خيول_نمو": {"CP": 15.0, "DP": 12.5, "SE": 65.0, "NDF": 30.0, "ADF": 18.0, "EE": 4.0, "ASH": 8.0, "Ca": 0.75, "P": 0.42},
    "خيول_صيانة": {"CP": 10.0, "DP": 7.5, "SE": 55.0, "NDF": 45.0, "ADF": 28.0, "EE": 3.5, "ASH": 8.0, "Ca": 0.45, "P": 0.28},
    # دواجن لاحم
    "دواجن_بادي": {"CP": 23.0, "DP": 20.0, "SE": 76.0, "NDF": 8.0, "ADF": 4.0, "EE": 5.0, "ASH": 6.5, "Ca": 1.00, "P": 0.50},
    "دواجن_نامي": {"CP": 21.0, "DP": 18.5, "SE": 74.0, "NDF": 9.0, "ADF": 5.0, "EE": 4.5, "ASH": 6.0, "Ca": 0.90, "P": 0.45},
    "دواجن_ناهي": {"CP": 19.0, "DP": 16.5, "SE": 75.0, "NDF": 10.0, "ADF": 5.5, "EE": 4.0, "ASH": 6.0, "Ca": 0.85, "P": 0.42},
    "دواجن_بياض": {"CP": 17.5, "DP": 15.5, "SE": 72.0, "NDF": 11.0, "ADF": 6.0, "EE": 4.2, "ASH": 11.5, "Ca": 3.80, "P": 0.45},
    # سمان
    "سمان_بادي": {"CP": 24.0, "DP": 20.5, "SE": 74.0, "NDF": 8.0, "ADF": 4.0, "EE": 5.0, "ASH": 6.5, "Ca": 1.00, "P": 0.55},
    "سمان_بياض": {"CP": 18.0, "DP": 15.0, "SE": 68.0, "NDF": 11.0, "ADF": 5.5, "EE": 4.0, "ASH": 9.0, "Ca": 2.50, "P": 0.45},
    # أسماك
    "أسماك_بادئ": {"CP": 40.0, "DP": 32.0, "SE": 72.0, "NDF": 8.0, "ADF": 4.0, "EE": 8.0, "ASH": 11.0, "Ca": 1.50, "P": 0.90},
    "أسماك_نمو": {"CP": 32.0, "DP": 25.0, "SE": 70.0, "NDF": 12.0, "ADF": 6.0, "EE": 6.0, "ASH": 9.0, "Ca": 1.00, "P": 0.70},
    "أسماك_تسمين": {"CP": 28.0, "DP": 22.0, "SE": 68.0, "NDF": 13.0, "ADF": 7.0, "EE": 6.5, "ASH": 9.5, "Ca": 0.90, "P": 0.65},
}


# ═══════════════════════════════════════════════════════════════════════════
# دوال الحساب الغذائي
# ═══════════════════════════════════════════════════════════════════════════

def compute_formula_nutrients(formula: dict) -> dict:
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


def get_standard_key(animal: str, stage: str) -> str:
    a, s = str(animal).strip(), str(stage).strip()
    if "أبقار" in a:
        if "حليب عالي" in s: return "أبقار_حليب_عالي"
        if "حليب" in s: return "أبقار_حليب_متوسط"
        if "مكثف" in s: return "أبقار_تسمين_مكثف"
        if "تسمين" in s: return "أبقار_تسمين_عادي"
        return "أبقار_صيانة"
    if "أغنام" in a:
        if "مكثف" in s: return "أغنام_تسمين_مكثف"
        if "حليب" in s or "مرضع" in s: return "أغنام_حليب"
        if "تسمين" in s: return "أغنام_تسمين_عادي"
        return "أغنام_صيانة"
    if "ماعز" in a:
        if "حليب" in s or "حلاب" in s: return "ماعز_حليب"
        if "تسمين" in s: return "ماعز_تسمين"
        return "ماعز_صيانة"
    if "إبل" in a or "جمال" in a:
        if "حليب" in s: return "إبل_حليب"
        if "سباق" in s: return "إبل_سباق"
        if "تسمين" in s: return "إبل_تسمين"
        if "نمو" in s: return "إبل_نمو"
        return "إبل_صيانة"
    if "خيول" in a or "خيل" in a:
        if "رياضة" in s: return "خيول_رياضة"
        if "نمو" in s or "أمهار" in s: return "خيول_نمو"
        return "خيول_صيانة"
    if "دواجن" in a or "دجاج" in a:
        if "بياض" in a or "بياض" in s: return "دواجن_بياض"
        if "بادي" in s: return "دواجن_بادي"
        if "نامي" in s: return "دواجن_نامي"
        return "دواجن_ناهي"
    if "سمان" in a:
        if "بياض" in s: return "سمان_بياض"
        return "سمان_بادي"
    if "أسماك" in a:
        if "بادئ" in s or "زريعة" in s: return "أسماك_بادئ"
        if "تسمين" in s: return "أسماك_تسمين"
        return "أسماك_نمو"
    return "دواجن_ناهي"


# ═══════════════════════════════════════════════════════════════════════════
# نظام التقييم المحسّن
# ═══════════════════════════════════════════════════════════════════════════

def evaluate_difference(pct_diff: float) -> dict:
    """نظام تقييم محسّن"""
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


def get_overall_rating(compare_rows: list) -> dict:
    """تقييم عام للخلطة"""
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


# ═══════════════════════════════════════════════════════════════════════════
# محرك التركيب الذكي — يطابق كل العناصر تلقائياً
# ═══════════════════════════════════════════════════════════════════════════

def auto_formulate_smart(available_ingredients, prices, standard_key,
                          tolerance=0.3, max_iterations=50):
    """محرك التركيب الذكي — 3 مراحل"""
    standard = NUTRIENT_STANDARDS.get(standard_key, {})
    if not standard:
        return {"success": False, "message": "معيار غير موجود"}
    
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
    
    targets = {k: standard.get(k, 0) for k in ["DP", "SE", "NDF", "ADF", "Ca", "P"]}
    
    bounds = []
    for i in valid:
        if "يوريا" in i: bounds.append((0.0, 1.0))
        elif "مولاس" in i: bounds.append((0.0, 10.0))
        elif "ملح الطعام" in i: bounds.append((0.3, 0.7))
        elif "بيكربونات" in i: bounds.append((0.0, 1.5))
        elif "مضاد سموم" in i: bounds.append((0.05, 0.25))
        elif "بريمكس" in i: bounds.append((0.15, 0.5))
        elif "إنزيم" in i: bounds.append((0.02, 0.10))
        elif "الحجر الجيري" in i: bounds.append((0.0, 3.5))
        elif "فوسفات" in i: bounds.append((0.0, 2.5))
        elif "سرسة" in i: bounds.append((0.0, 8.0))
        elif "تبن" in i or "قش" in i: bounds.append((0.0, 25.0))
        else: bounds.append((0.0, 100.0))
    
    # المرحلة 1: حل أولي
    A_eq = [[1.0] * n, rows["DP"]]
    b_eq = [100.0, targets["DP"] * 100.0]
    A_ub = [
        [-1.0 * x for x in rows["SE"]],
        [1.0 * x for x in rows["NDF"]],
        [1.0 * x for x in rows["ADF"]],
    ]
    b_ub = [
        -1.0 * targets["SE"] * 100.0,
        targets["NDF"] * 1.15 * 100.0,
        targets["ADF"] * 1.15 * 100.0,
    ]
    
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method='highs')
    if not res.success:
        # تخفيف
        for relax in [1.05, 1.10, 1.20, 1.30]:
            b_ub_relaxed = [
                -1.0 * targets["SE"] * 100.0 * (2 - relax),
                targets["NDF"] * relax * 100.0,
                targets["ADF"] * relax * 100.0,
            ]
            res = linprog(c, A_ub=A_ub, b_ub=b_ub_relaxed, A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method='highs')
            if res.success: break
    
    if not res.success:
        return {"success": False, "message": "تعذر إيجاد حل — أضف مكونات متنوعة"}
    
    # المرحلة 2: التصحيح التلقائي
    best = None
    best_score = float('inf')
    cur_dp = targets["DP"]; cur_se = targets["SE"]
    cur_ndf = targets["NDF"]; cur_adf = targets["ADF"]
    log = []
    
    for iteration in range(max_iterations):
        A_eq = [[1.0] * n, rows["DP"], rows["Ca"], rows["P"]]
        b_eq = [100.0, cur_dp * 100.0,
                targets["Ca"] * 100.0, targets["P"] * 100.0]
        A_ub = [
            [-1.0 * x for x in rows["SE"]],
            [1.0 * x for x in rows["NDF"]],
            [1.0 * x for x in rows["ADF"]],
        ]
        b_ub = [
            -1.0 * cur_se * 100.0,
            cur_ndf * 1.10 * 100.0,
            cur_adf * 1.10 * 100.0,
        ]
        
        try:
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method='highs',
                          options={'presolve': True, 'time_limit': 15})
        except Exception:
            res = type('obj', (), {'success': False})()
        
        if not res.success:
            # نسقط قيود Ca و P
            A_eq = [[1.0] * n, rows["DP"], rows["Ca"]]
            b_eq = [100.0, cur_dp * 100.0, targets["Ca"] * 100.0]
            try:
                res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                              bounds=bounds, method='highs')
            except Exception:
                res = type('obj', (), {'success': False})()
        
        if not res.success:
            cur_ndf *= 1.05; cur_adf *= 1.05
            log.append(f"تكرار {iteration+1}: تخفيف")
            continue
        
        formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
        actual = compute_formula_nutrients(formula)
        
        errors = {}
        for k in ["DP", "SE", "NDF", "ADF", "Ca", "P"]:
            tv = targets.get(k, 0)
            if tv > 0:
                errors[k] = abs(actual.get(k, 0) - tv) / tv
            else:
                errors[k] = 0
        
        weights = {"DP": 5.0, "SE": 3.0, "NDF": 1.5, "ADF": 1.0, "Ca": 1.0, "P": 1.0}
        score = sum(errors.get(k, 0) * weights[k] for k in errors)
        
        log.append(f"تكرار {iteration+1}: DP={actual['DP']:.2f} SE={actual['SE']:.2f} "
                   f"NDF={actual['NDF']:.1f} Ca={actual.get('Ca',0):.2f}")
        
        if score < best_score:
            best_score = score
            best = {
                "success": True, "formula": formula, "cost": res.fun / 100.0,
                "actual_nutrients": actual,
                "dp_error": abs(actual["DP"] - targets["DP"]),
                "se_error": abs(actual["SE"] - targets["SE"]),
                "ndf_error": abs(actual["NDF"] - targets["NDF"]),
                "adf_error": abs(actual["ADF"] - targets["ADF"]),
                "ca_error": abs(actual.get("Ca", 0) - targets["Ca"]),
                "p_error": abs(actual.get("P", 0) - targets["P"]),
                "iterations": iteration + 1, "log": log[-10:], "targets": targets,
            }
        
        # التحقق
        if (errors.get("DP", 1) * 100 <= tolerance and
            errors.get("SE", 1) * 100 <= tolerance * 2 and
            errors.get("NDF", 1) * 100 <= tolerance * 5 and
            errors.get("Ca", 1) * 100 <= tolerance * 15):
            log.append(f"✅ مطابقة كاملة في التكرار {iteration+1}")
            best["perfect_match"] = True
            break
        
        cur_dp += (targets["DP"] - actual["DP"]) * 0.25
        cur_se += (targets["SE"] - actual["SE"]) * 0.20
        cur_ndf += (targets["NDF"] - actual["NDF"]) * 0.15
        cur_adf += (targets["ADF"] - actual["ADF"]) * 0.15
        cur_dp = max(5.0, min(40.0, cur_dp))
        cur_se = max(10.0, min(90.0, cur_se))
        cur_ndf = max(5.0, min(70.0, cur_ndf))
        cur_adf = max(3.0, min(50.0, cur_adf))
    
    if best:
        best["log"] = log
        return best
    return {"success": False, "message": "تعذر حل دقيق", "log": log}


def auto_formulate_precise(available_ingredients, prices, target_dp, target_se,
                            standard_key, tolerance=0.3, max_iterations=50):
    """غلاف التوافق"""
    return auto_formulate_smart(available_ingredients, prices, standard_key,
                                 tolerance=tolerance, max_iterations=max_iterations)


def auto_add_salts_and_minerals(animal_type, formula):
    """إضافة الأملاح والفيتامينات تلقائياً"""
    salt = {}
    if any(x in animal_type for x in ["أغنام", "ماعز", "أبقار", "إبل"]):
        salt["بيكربونات الصوديوم (الصودا)"] = 0.75
    salt["مضاد سموم فطرية"] = 0.20
    salt["ملح الطعام"] = 0.50
    if "دواجن" in animal_type or "سمان" in animal_type:
        if "بياض" in animal_type:
            salt["الحجر الجيري (بودرة بلاط)"] = 8.0
        else:
            salt["الحجر الجيري (بودرة بلاط)"] = 1.5
        salt["فوسفات ثنائي الكالسيوم (DCP)"] = 1.5
        salt["بريمكس تسمين دواجن (Premix Broiler)"] = 0.30
    else:
        salt["الحجر الجيري (بودرة بلاط)"] = 2.0
        salt["فوسفات ثنائي الكالسيوم (DCP)"] = 1.5
        salt["بريمكس مجترات عام"] = 0.30
    return salt


# ═══════════════════════════════════════════════════════════════════════════
# بدائل الحليب
# ═══════════════════════════════════════════════════════════════════════════

MILK_REPLACER_STANDARDS = {
    "عجول (Calves)": {"CP": 24.0, "Fat": 24.0, "Lactose": 45.0, "Lysine": 2.1, "Ca": 0.75, "P": 0.70, "Fiber_max": 0.15, "Ash_max": 10.0, "notes": "عمر 1-6 أسابيع، مادة جافة 12-15%"},
    "حملان (Lambs)": {"CP": 24.0, "Fat": 24.0, "Lactose": 40.0, "Lysine": 2.1, "Ca": 0.80, "P": 0.70, "Fiber_max": 0.15, "Ash_max": 10.0, "notes": "≥ 24% دهن"},
    "جديان (Goat Kids)": {"CP": 24.0, "Fat": 24.0, "Lactose": 42.0, "Lysine": 2.1, "Ca": 0.80, "P": 0.70, "Fiber_max": 0.15, "Ash_max": 10.0, "notes": "بديل الجديان"},
    "إبل (Camel Calves)": {"CP": 26.0, "Fat": 28.0, "Lactose": 38.0, "Lysine": 2.3, "Ca": 0.85, "P": 0.75, "Fiber_max": 0.10, "Ash_max": 9.0, "notes": "بروتين ودهن أعلى"},
    "أمهار (Foals)": {"CP": 22.0, "Fat": 20.0, "Lactose": 45.0, "Lysine": 1.9, "Ca": 0.90, "P": 0.80, "Fiber_max": 0.15, "Ash_max": 9.0, "notes": "توازن خاص للخيول"},
}

MILK_REPLACER_INGREDIENTS = {
    "حليب مجفف منزوع الدسم": {"CP": 34.0, "Fat": 1.0, "Lactose": 52.0, "Ash": 8.0, "price": 3200},
    "حليب مجفف كامل الدسم": {"CP": 26.0, "Fat": 28.0, "Lactose": 38.0, "Ash": 6.0, "price": 3800},
    "شرش حليب مجفف": {"CP": 12.0, "Fat": 1.5, "Lactose": 75.0, "Ash": 9.0, "price": 1800},
    "بروتين شرش WPC 80%": {"CP": 80.0, "Fat": 5.0, "Lactose": 8.0, "Ash": 4.0, "price": 8500},
    "كازين (Casein)": {"CP": 85.0, "Fat": 2.0, "Lactose": 2.0, "Ash": 3.0, "price": 9000},
    "مركز بروتين صويا SPC 66%": {"CP": 66.0, "Fat": 1.0, "Lactose": 0.0, "Ash": 6.0, "price": 2800},
    "دقيق الصويا كامل الدسم": {"CP": 38.0, "Fat": 20.0, "Lactose": 0.0, "Ash": 6.0, "price": 1500},
    "زيت جوز الهند": {"CP": 0.0, "Fat": 100.0, "Lactose": 0.0, "Ash": 0.0, "price": 2200},
    "زيت النخيل": {"CP": 0.0, "Fat": 100.0, "Lactose": 0.0, "Ash": 0.0, "price": 1200},
    "دهن حيواني (Tallow)": {"CP": 0.0, "Fat": 100.0, "Lactose": 0.0, "Ash": 0.0, "price": 1000},
    "مالتودكسترين": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "Ash": 0.5, "price": 900},
    "لاكتوز نقي": {"CP": 0.0, "Fat": 0.0, "Lactose": 100.0, "Ash": 0.0, "price": 1400},
    "ليسين L-Lysine": {"CP": 94.0, "Fat": 0.0, "Lactose": 0.0, "Ash": 0.5, "price": 4200},
    "ميثيونين DL-Methionine": {"CP": 58.0, "Fat": 0.0, "Lactose": 0.0, "Ash": 0.3, "price": 5800},
    "بريمكس فيتامينات حليب": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "Ash": 100.0, "price": 6500},
    "كالسيوم كربونات": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "Ash": 99.5, "price": 200},
    "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "Ash": 98.5, "price": 1100},
    "ملح طعام": {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "Ash": 99.9, "price": 150},
}

def formulate_milk_replacer(animal_type, target_volume_kg=100.0, selected_ingredients=None):
    standard = MILK_REPLACER_STANDARDS.get(animal_type)
    if not standard:
        return {"success": False, "message": "نوع الحيوان غير مدعوم"}
    ingredients = selected_ingredients or list(MILK_REPLACER_INGREDIENTS.keys())
    valid = [i for i in ingredients if i in MILK_REPLACER_INGREDIENTS]
    if len(valid) < 3:
        return {"success": False, "message": "اختر 3 مكونات على الأقل"}
    n = len(valid)
    c = [MILK_REPLACER_INGREDIENTS[i]["price"] for i in valid]
    bounds = [(0.0, 100.0) for _ in range(n)]
    A_eq = [[1.0] * n, [MILK_REPLACER_INGREDIENTS[i]["CP"] for i in valid],
            [MILK_REPLACER_INGREDIENTS[i]["Fat"] for i in valid]]
    b_eq = [100.0, standard["CP"] * 100, standard["Fat"] * 100]
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if not res.success:
        return {"success": False, "message": "تعذر التركيب"}
    formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
    actual = {"CP": 0, "Fat": 0, "Lactose": 0}
    for ing, pct in formula.items():
        d = MILK_REPLACER_INGREDIENTS[ing]
        actual["CP"] += pct / 100.0 * d["CP"]
        actual["Fat"] += pct / 100.0 * d["Fat"]
        actual["Lactose"] += pct / 100.0 * d["Lactose"]
    return {"success": True, "formula": formula,
            "cost_per_100kg": res.fun / 100.0, "cost_per_kg": res.fun / 10000.0,
            "standard": standard, "actual": actual, "animal": animal_type}


# ═══════════════════════════════════════════════════════════════════════════
# المختبر الذكي (OCR)
# ═══════════════════════════════════════════════════════════════════════════

def match_ingredient_name(text):
    if not text: return None
    tl = text.strip().lower()
    for cat in BIG_FEEDS_LIBRARY.values():
        for name in cat.keys():
            if name.lower() in tl or tl in name.lower():
                return name
    kw_map = {
        "ذرة": "ذرة صفراء", "corn": "ذرة صفراء", "صويا": "كسب فول صويا 44%",
        "شعير": "شعير مطحون", "barley": "شعير مطحون", "قمح": "قمح محلي مصنّع",
        "سورجم": "سورجم (فتريتة)", "نخالة": "نخالة قمح (ردة)",
        "فول سوداني": "أمباز الفول السوداني (كسب)", "قطن": "كسب بذور القطن (مقشور)",
        "عباد": "كسب عباد الشمس 36%", "سمسم": "كسب السمسم المحسن",
        "جلوتين": "كسب جلوتين الذرة 60%", "سمك": "مسحوق أسماك (Fishmeal 60%)",
        "لحم": "مسحوق اللحم والعظم", "دم": "مسحوق الدم المجفف",
        "ليسين": "ليسين نقي (L-Lysine HCl)", "ميثيونين": "ميثيونين نقي (DL-Methionine)",
        "ملح": "ملح الطعام", "حجر": "الحجر الجيري (بودرة بلاط)",
        "فوسفات": "فوسفات ثنائي الكالسيوم (DCP)",
        "بيكربونات": "بيكربونات الصوديوم (الصودا)",
        "مولاس": "مولاس قصب السكر", "برسيم": "البرسيم الجاف (الدريس)",
        "تبن": "تبن قمح ناعم", "يوريا": "يوريا علفية محصنة",
    }
    for kw, m in kw_map.items():
        if kw in tl: return m
    return None


def extract_ingredients_from_image(image_bytes):
    if not OCR_AVAILABLE:
        return {"success": False, "message": "pytesseract غير مثبتة"}
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"success": False, "message": "تعذر قراءة الصورة"}
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)
        thresh1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY, 11, 2)
        _, thresh2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        results = []
        for thresh in [thresh1, thresh2, gray]:
            try:
                text = pytesseract.image_to_string(thresh, lang='ara+eng',
                    config=r'--oem 3 --psm 6')
                if text.strip(): results.append(text)
            except Exception:
                continue
        if not results:
            return {"success": False, "message": "لم يتم استخراج نص"}
        full_text = "\n".join(results)
        ingredients = {}
        for line in full_text.split('\n'):
            line = line.strip()
            if len(line) < 3: continue
            for pattern in [r'([\u0600-\u06FFa-zA-Z\s\(\)%]+?)[\s:\-=]+(\d+\.?\d*)\s*%',
                            r'([\u0600-\u06FFa-zA-Z\s\(\)%]+?)\s+(\d+\.?\d*)\s*%']:
                m = re.search(pattern, line)
                if m:
                    name, val = m.group(1).strip(), float(m.group(2))
                    if 0.1 < val <= 100 and len(name) > 2:
                        matched = match_ingredient_name(name)
                        if matched:
                            ingredients[matched] = val
                            break
        return {"success": True, "ingredients": ingredients,
                "raw_text": full_text, "count": len(ingredients)}
    except Exception as e:
        return {"success": False, "message": f"خطأ: {str(e)}"}


# ═══════════════════════════════════════════════════════════════════════════
# مولد PDF الاحترافي مع رسوم بيانية ملوّنة
# ═══════════════════════════════════════════════════════════════════════════

def create_colorful_nutrient_chart(standard, actual):
    """إنشاء رسم بياني ملوّن بأعمدة للمقارنة"""
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        nutrients = ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH"]
        nutrients = [n for n in nutrients if n in standard]
        std_vals = [standard[n] for n in nutrients]
        act_vals = [actual.get(n, 0) for n in nutrients]
        
        fig, ax = plt.subplots(figsize=(8, 4))
        x = np.arange(len(nutrients))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, std_vals, width, label='المعيار القياسي',
                       color='#1976d2', edgecolor='#0d47a1', linewidth=1.5)
        bars2 = ax.bar(x + width/2, act_vals, width, label='القيمة المحسوبة',
                       color='#43a047', edgecolor='#1b5e20', linewidth=1.5)
        
        for bar in bars1:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h, f'{h:.1f}',
                    ha='center', va='bottom', fontsize=8, color='#0d47a1', fontweight='bold')
        for bar in bars2:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h, f'{h:.1f}',
                    ha='center', va='bottom', fontsize=8, color='#1b5e20', fontweight='bold')
        
        ax.set_xlabel('العنصر الغذائي', fontsize=11, fontweight='bold')
        ax.set_ylabel('القيمة', fontsize=11, fontweight='bold')
        ax.set_title('مقارنة العناصر الغذائية', fontsize=13, fontweight='bold', color='#1b5e20')
        ax.set_xticks(x)
        ax.set_xticklabels([arp.fix(n) for n in nutrients], fontsize=10)
        ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
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
    """رسم بياني دائري ملوّن للمكونات"""
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2:
        return None
    try:
        colors = ['#e53935', '#8e24aa', '#3949ab', '#1e88e5', '#00897b',
                  '#43a047', '#7cb342', '#fdd835', '#fb8c00', '#6d4c41',
                  '#c62828', '#6a1b9a', '#283593', '#0277bd', '#00695c']
        names = list(formula.keys())
        vals = list(formula.values())
        
        fig, ax = plt.subplots(figsize=(7, 5))
        wedges, texts, autotexts = ax.pie(
            vals, autopct='%1.1f%%', colors=colors[:len(names)],
            startangle=90, pctdistance=0.75,
            wedgeprops=dict(edgecolor='white', linewidth=2)
        )
        for t in autotexts:
            t.set_color('white')
            t.set_fontweight('bold')
            t.set_fontsize(9)
        
        ax.legend([arp.fix(n) for n in names], loc='center left',
                  bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9,
                  title=arp.fix("المكونات"), title_fontsize=10)
        ax.set_title(arp.fix('توزيع المكونات'), fontsize=13,
                     fontweight='bold', color='#1b5e20')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_radar_chart(standard, actual):
    """رسم رادار للمقارنة الشاملة"""
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        nutrients = ["CP", "DP", "SE", "NDF", "ADF", "EE", "Ca", "P"]
        nutrients = [n for n in nutrients if n in standard and standard[n] > 0]
        if len(nutrients) < 3:
            return None
        
        std_norm = []
        act_norm = []
        for n in nutrients:
            sv = standard[n]
            av = actual.get(n, 0)
            # تطبيع بحيث القيمة القياسية = 100%
            std_norm.append(100.0)
            act_norm.append((av / sv) * 100 if sv > 0 else 0)
        
        angles = np.linspace(0, 2 * np.pi, len(nutrients), endpoint=False).tolist()
        std_norm += std_norm[:1]
        act_norm += act_norm[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        
        ax.plot(angles, std_norm, 'o-', linewidth=2.5, color='#1976d2',
                label='المعيار القياسي (100%)')
        ax.fill(angles, std_norm, alpha=0.15, color='#1976d2')
        
        ax.plot(angles, act_norm, 'o-', linewidth=2.5, color='#43a047',
                label='القيمة المحسوبة')
        ax.fill(angles, act_norm, alpha=0.25, color='#43a047')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([arp.fix(n) for n in nutrients], fontsize=9)
        ax.set_ylim(0, max(max(std_norm), max(act_norm)) * 1.2)
        ax.set_title(arp.fix('المقارنة الشاملة %'), fontsize=12,
                     fontweight='bold', color='#1b5e20', pad=20)
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
    """مؤشر دائري للتقييم"""
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect='equal'))
        
        colors_gauge = ['#c62828', '#ef6c00', '#f9a825', '#7cb342', '#43a047', '#1b5e20']
        for i, c in enumerate(colors_gauge):
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
        ax.text(0, -0.5, arp.fix('التقييم العام'), ha='center',
                fontsize=11, color='#666')
        
        ax.set_xlim(-1.2, 1.2); ax.set_ylim(-0.7, 1.2)
        ax.axis('off')
        ax.set_facecolor('white')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        for fp in ["Amiri-Regular.ttf", "Amiri.ttf", "Cairo-Regular.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
            if os.path.exists(fp):
                try:
                    pdfmetrics.registerFont(TTFont('TaworArabic', fp))
                    self.font_name = 'TaworArabic'
                    break
                except Exception:
                    continue
        self.logo_path = None
        for lp in LOGO_OPTIONS + PHOTO_OPTIONS:
            if os.path.exists(lp):
                self.logo_path = lp
                break
    
    def _ar(self, text):
        try:
            return get_display(arabic_reshaper.reshape(str(text)))
        except Exception:
            return str(text)
    
    def _draw_page_decorations(self, canvas_obj, doc):
        canvas_obj.saveState()
        w, h = doc.pagesize
        
        # علامة مائية
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
        
        # ترويسة
        canvas_obj.setFillColor(HexColor('#1b5e20'))
        canvas_obj.rect(0, h - 90, w, 90, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor('#d4af37'))
        canvas_obj.rect(0, h - 95, w, 5, fill=1, stroke=0)
        
        try:
            if self.logo_path:
                canvas_obj.drawImage(self.logo_path, 30, h - 78, width=60, height=60,
                                     preserveAspectRatio=True, anchor='sw', mask='auto')
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
        
        # تذييل — صف الدعاء
        canvas_obj.setFillColor(HexColor('#1b5e20'))
        canvas_obj.rect(0, 42, w, 42, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor('#d4af37'))
        canvas_obj.rect(0, 84, w, 3, fill=1, stroke=0)
        
        canvas_obj.setFillColor(HexColor('#ffeb3b'))
        canvas_obj.setFont(self.font_name, 9)
        canvas_obj.drawCentredString(w / 2, 68, self._ar(f"🤲 {DUA_SHORT} 🤲"))
        
        canvas_obj.setFillColor(HexColor('#c8e6c9'))
        canvas_obj.setFont(self.font_name, 7.5)
        canvas_obj.drawCentredString(w / 2, 52,
            self._ar("اللهم اجعل قبرهما روضة من رياض الجنة"))
        
        # تذييل سفلي
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
            buf = io.BytesIO()
            qi.save(buf, format="PNG")
            buf.seek(0)
            canvas_obj.drawImage(Image(buf), w / 2 - 20, 46, width=40, height=40)
        except Exception:
            pass
        
        # ختم
        sx, sy = w - 105, 145
        canvas_obj.setStrokeColor(HexColor('#c62828'))
        canvas_obj.setLineWidth(3.0)
        canvas_obj.circle(sx, sy, 70, stroke=1, fill=0)
        canvas_obj.setLineWidth(1.5)
        canvas_obj.circle(sx, sy, 62, stroke=1, fill=0)
        canvas_obj.setLineWidth(0.6)
        canvas_obj.circle(sx, sy, 56, stroke=1, fill=0)
        
        canvas_obj.setFillColor(HexColor('#c62828'))
        canvas_obj.setFont(self.font_name, 9)
        canvas_obj.drawCentredString(sx, sy + 40, self._ar("تاور نولجي"))
        canvas_obj.drawCentredString(sx, sy + 28, self._ar("Tawor Nology"))
        canvas_obj.setFont(self.font_name, 7.5)
        canvas_obj.drawCentredString(sx, sy + 10, self._ar("م. عبدالقادر"))
        canvas_obj.drawCentredString(sx, sy - 1, self._ar("إسماعيل تاور"))
        canvas_obj.setFont(self.font_name, 6)
        canvas_obj.drawCentredString(sx, sy - 17, self._ar("اختصاصي تغذية الحيوان"))
        canvas_obj.drawCentredString(sx, sy - 30, self._ar("معتمد رسمياً"))
        canvas_obj.drawCentredString(sx, sy - 42, self._ar("© 2026"))
        
        canvas_obj.restoreState()
    
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
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
        ]
        
        row = 1
        for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
            if k not in standard: continue
            sv = standard[k]
            cv = calculated.get(k, 0.0)
            diff = cv - sv
            pct = (diff / sv * 100) if sv else 0
            ev = evaluate_difference(pct)
            
            unit = "%" if k in ("CP", "DP", "NDF", "ADF", "EE", "ASH", "Ca", "P") else ""
            data.append([
                self._ar(labels.get(k, k)),
                f"{sv:.2f}{unit}",
                f"{cv:.2f}{unit}",
                f"{diff:+.3f}",
                f"{pct:+.2f}%",
                self._ar(ev["label"]),
            ])
            cmds.append(('BACKGROUND', (0, row), (-1, row), HexColor(ev["bg"])))
            cmds.append(('TEXTCOLOR', (5, row), (5, row), HexColor(ev["color"])))
            row += 1
        
        t = Table(data, colWidths=[100, 75, 75, 75, 75, 100])
        t.setStyle(TableStyle(cmds))
        return t
    
    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city,
                                       local_cost, local_sym, computed_se,
                                       requester_name="", animal_type="",
                                       production_stage="", include_charts=True,
                                       report_type="تركيب علفة"):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
            rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []
        
        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text),
                ParagraphStyle('s', fontName=self.font_name, fontSize=size,
                    alignment=align, textColor=HexColor(color),
                    spaceAfter=6, leading=size * 1.6))
        
        # العنوان
        story.append(P(f"تقرير فني رسمي — {report_type}", size=20,
                       align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))
        
        # بيانات الطالب
        client_data = [
            [self._ar("👤 اسم طالب الخدمة:"), self._ar(requester_name or "........................")],
            [self._ar("📍 الموقع:"), self._ar(city)],
            [self._ar("🐾 الفصيل:"), self._ar(breed)],
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
        
        # حساب القيم
        std_key = get_standard_key(animal_type, production_stage)
        standard_vals = NUTRIENT_STANDARDS.get(std_key, {})
        calculated_vals = compute_formula_nutrients(formula)
        
        # التقييم العام
        compare_scores = []
        for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
            if k not in standard_vals: continue
            sv = standard_vals[k]
            cv = calculated_vals.get(k, 0.0)
            pct = ((cv - sv) / sv * 100) if sv else 0
            ev = evaluate_difference(pct)
            compare_scores.append({"score": ev["score"], "label": ev["label"]})
        
        overall = get_overall_rating(compare_scores)
        
        # جدول المقارنة
        story.append(P("📊 جدول مقارنة العناصر الغذائية", size=14,
                       align=TA_RIGHT, color='#1b5e20'))
        story.append(Spacer(1, 8))
        story.append(self._comparison_table(standard_vals, calculated_vals))
        story.append(Spacer(1, 12))
        
        # ملخص التقييم
        summary_data = [
            [self._ar("التقييم العام"), self._ar("عدد العناصر المطابقة"),
             self._ar("المتوسط")],
            [self._ar(overall["label"]),
             f"{sum(1 for s in compare_scores if s['score'] >= 85)}/{len(compare_scores)}",
             f"{overall['score']:.0f}%"],
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
        
        # 📊 الرسوم البيانية الملوّنة
        if include_charts:
            story.append(P("📈 الرسوم البيانية التحليلية", size=14,
                           align=TA_RIGHT, color='#1b5e20'))
            story.append(Spacer(1, 10))
            
            # 1. مقارنة أعمدة
            chart1 = create_colorful_nutrient_chart(standard_vals, calculated_vals)
            if chart1:
                story.append(Image(chart1, width=450, height=250))
                story.append(Spacer(1, 12))
            
            # 2. دائري + رادار في صف
            chart2 = create_colorful_pie_chart(formula)
            chart3 = create_radar_chart(standard_vals, calculated_vals)
            
            if chart2 and chart3:
                row_data = [[Image(chart2, width=210, height=200),
                            Image(chart3, width=210, height=200)]]
                r_tbl = Table(row_data, colWidths=[230, 230])
                r_tbl.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(r_tbl)
                story.append(Spacer(1, 12))
            elif chart2:
                story.append(Image(chart2, width=350, height=280))
                story.append(Spacer(1, 12))
            
            # 3. مؤشر التقييم
            gauge = create_gauge_chart(overall["score"])
            if gauge:
                story.append(P("🎯 مؤشر التقييم العام", size=12,
                               align=TA_CENTER, color='#1b5e20'))
                story.append(Image(gauge, width=200, height=200))
                story.append(Spacer(1, 12))
        
        story.append(PageBreak())
        
        # التكاليف
        story.append(P("💰 ملخص التكاليف", size=14, align=TA_RIGHT, color='#1b5e20'))
        story.append(Spacer(1, 8))
        cost_data = [
            [self._ar("البند"), self._ar("القيمة")],
            [self._ar("التكلفة للطن (دولار)"), f"${cost:.2f}"],
            [self._ar(f"التكلفة ({local_sym})"), f"{local_cost:,.2f}"],
            [self._ar("معادل النشاء المحسوب"), f"{computed_se:.2f}"],
            [self._ar("البروتين المستهدف"), f"{target_dp:.2f}%"],
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
            story.append(P("🌾 المكونات المعتمدة للطن", size=14, align=TA_RIGHT, color='#1b5e20'))
            story.append(Spacer(1, 8))
            ing_data = [[self._ar("المكون"), self._ar("النسبة %"), self._ar("كجم/طن")]]
            for ing, pct in formula.items():
                ing_data.append([self._ar(ing), f"{pct:.2f}%", f"{pct*10:.1f}"])
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
        
        # التوقيعات
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
        
        doc.build(story, onFirstPage=self._draw_page_decorations,
                  onLaterPages=self._draw_page_decorations)
        buffer.seek(0)
        return buffer.getvalue()


pdf_generator = ProfessionalPDFGenerator()


# ═══════════════════════════════════════════════════════════════════════════
# تصدير Excel
# ═══════════════════════════════════════════════════════════════════════════

def export_comparison_to_excel(standard, calculated, requester_name="",
                                animal="", stage="", formula=None):
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
    ws['A1'] = f"{APP_NAME} — تقرير"
    ws['A1'].font = tf
    ws['A1'].alignment = ct
    
    ws['A3'] = "طالب:"; ws['A3'].font = Font(bold=True); ws['A3'].alignment = rt
    ws.merge_cells('B3:D3'); ws['B3'] = requester_name
    ws['E3'] = "التاريخ:"; ws['E3'].font = Font(bold=True); ws['E3'].alignment = rt
    ws['F3'] = datetime.now().strftime('%Y-%m-%d')
    
    headers = ["العنصر", "المعيار", "المحسوب", "الفرق", "% الفرق", "التقييم"]
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=5, column=c, value=h)
        cell.font = hf; cell.fill = hfill; cell.alignment = ct; cell.border = bd
    
    labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم", "SE": "معادل النشاء",
              "NDF": "NDF", "ADF": "ADF", "EE": "دهن", "ASH": "رماد",
              "Ca": "كالسيوم", "P": "فسفور"}
    
    row = 6
    for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
        if k not in standard: continue
        sv = standard[k]; cv = calculated.get(k, 0.0)
        diff = cv - sv
        pct = (diff / sv * 100) if sv else 0
        ev = evaluate_difference(pct)
        
        vals = [labels[k], round(sv, 2), round(cv, 2), round(diff, 3),
                round(pct, 2), ev["label"]]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.alignment = ct; cell.border = bd
            cell.fill = PatternFill('solid', fgColor=ev["bg"].replace('#', ''))
        row += 1
    
    for c in range(1, 7):
        ws.column_dimensions[get_column_letter(c)].width = 22
    
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# السوق والأسعار
# ═══════════════════════════════════════════════════════════════════════════

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "LIBYA": {"rate": 4.80, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"},
    "السعودية": {"rate": 3.75, "sym": "SAR"},
    "الإمارات": {"rate": 3.67, "sym": "AED"},
    "باقي دول العالم": {"rate": 1.0, "sym": "USD"},
}

def get_market_prices(country, city, state=""):
    base = {ing: 280.0 for cat in BIG_FEEDS_LIBRARY.values() for ing in cat}
    base.update({
        "ذرة صفراء": 230, "ذرة بيضاء": 225, "شعير مطحون": 210,
        "سورجم (فتريتة)": 195, "قمح محلي مصنّع": 240,
        "أمباز الفول السوداني (كسب)": 460, "كسب فول صويا 44%": 440,
        "كسب فول صويا 48%": 480, "كسب عباد الشمس 36%": 310,
        "كسب بذور القطن (مقشور)": 290, "نخالة قمح (ردة)": 150,
        "البرسيم الجاف (الدريس)": 170, "مولاس قصب السكر": 120,
        "مسحوق أسماك (Fishmeal 60%)": 850, "مركزات دواجن وسمان": 650,
        "مركزات خيول ومجترات": 600, "الحجر الجيري (بودرة بلاط)": 40,
        "فوسفات ثنائي الكالسيوم (DCP)": 280, "ملح الطعام": 30,
        "بيكربونات الصوديوم (الصودا)": 340, "مضاد سموم فطرية": 950,
        "بريمكس تسمين دواجن (Premix Broiler)": 4800,
        "بريمكس مجترات عام": 4500,
        "ليسين نقي (L-Lysine HCl)": 4200,
        "ميثيونين نقي (DL-Methionine)": 5800,
        "إنزيم الفايتيز (Phytase 5000)": 12000,
    })
    m = 1.0
    if country == "السودان":
        m = 1.15
        if "كردفان" in state: m = 1.20
    elif country == "LIBYA": m = 1.10
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
                with open(p, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                pass
    return None

img_base64 = get_img_b64(tuple(PHOTO_OPTIONS))


# ═══════════════════════════════════════════════════════════════════════════
# الحالة الأولية
# ═══════════════════════════════════════════════════════════════════════════

DEFAULTS = {
    "approved": False,
    "user_role": None,
    "audio_played": False,
    "dua_shown": False,
    "active_formula": {},
    "active_stage_title": "إنتاج عام",
    "active_animal_img": ANIMAL_IMAGES["عام"],
    "computed_ton_cost": 280.0,
    "inventory": {},
    "shared_comments": f"• مرحباً بكم في {APP_NAME}\n• {DUA_SHORT}\n",
    "broiler_farms": {},
    "livestock_prices": {
        "عجول تسمين هولشتاين ($)": 1350.0,
        "أبقار كنانة محلية ($)": 900.0,
        "ضأن محلي ($)": 180.0,
        "ماعز نوبي ($)": 130.0,
        "إبل حاشي ($)": 1200.0,
        "كتكوت لاحم يوم ($)": 0.65,
        "دجاج بياض ($)": 5.50,
    },
    "products_prices": {
        "كيلو لحم بقري ($)": 7.50,
        "كيلو لحم ضأن ($)": 9.00,
        "كيلو لحم إبل ($)": 8.50,
        "كيلو لحم دجاج ($)": 3.80,
        "طبق بيض 30 ($)": 4.20,
        "لتر حليب بقر ($)": 0.90,
        "لتر حليب إبل ($)": 3.50,
    },
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


# ═══════════════════════════════════════════════════════════════════════════
# دوال الصلاحيات
# ═══════════════════════════════════════════════════════════════════════════

def is_owner():
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
.stApp { background: transparent; }

.main-box {
    background-color: rgba(255, 255, 255, 0.98);
    padding: 30px; border-radius: 15px;
    box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18);
    margin-bottom: 60px; backdrop-filter: blur(5px);
}

h1, h2, h3, h4, h5, p, span, li, div, label { color: #1a1a1a !important; }

.dua-main-box {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #388e3c 100%);
    padding: 30px; border-radius: 20px;
    border: 4px solid #d4af37;
    box-shadow: 0 15px 40px rgba(0,0,0,0.4);
    color: white !important; direction: rtl; text-align: center;
    margin: 20px 0;
}
.dua-main-box * { color: white !important; }
.dua-main-box h3 {
    color: #d4af37 !important; font-size: 1.7rem; margin-bottom: 15px;
}
.dua-main-box .names {
    font-size: 1.5rem; font-weight: bold; color: #ffeb3b !important;
    margin: 15px 0; padding: 12px;
    background: rgba(255,255,255,0.1); border-radius: 12px;
}
.dua-main-box p.quran {
    font-family: 'Amiri', serif !important;
    font-size: 1.15rem; color: #d4af37 !important;
    margin-top: 20px; padding: 15px;
    background: rgba(0,0,0,0.2); border-radius: 10px;
    border-right: 4px solid #d4af37; border-left: 4px solid #d4af37;
}

.visitor-dua-banner {
    background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 50%, #ffe082 100%);
    padding: 20px 25px; border-radius: 15px;
    border-right: 6px solid #d4af37; border-left: 6px solid #d4af37;
    margin: 20px 0; direction: rtl; text-align: center;
    box-shadow: 0px 6px 25px rgba(0,0,0,0.15);
}
.visitor-dua-banner * { color: #4e342e !important; }
.visitor-dua-banner b { color: #c62828 !important; font-size: 1.05rem; }

.dua-fixed-banner {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #1b5e20, #2e7d32, #1b5e20);
    color: white !important; padding: 10px 15px;
    z-index: 9998; text-align: center;
    border-top: 3px solid #d4af37;
    font-family: 'Amiri', serif !important;
    font-size: 1rem;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.3);
}
.dua-fixed-banner * {
    color: #ffeb3b !important;
    font-family: 'Amiri', serif !important;
}

.section-title {
    color: #1b5e20 !important; border-right: 6px solid #2e7d32;
    padding: 10px 15px; text-align: right; font-size: 1.5rem;
    font-weight: bold; margin-top: 30px; margin-bottom: 20px;
    background: linear-gradient(to left, rgba(46,125,50,0.1), transparent);
    border-radius: 8px;
}

.formula-item {
    background: linear-gradient(135deg, #ffffff 0%, #e8f5e9 100%);
    padding: 15px 20px; border-radius: 12px;
    margin-bottom: 10px; font-weight: bold; color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    text-align: right;
}
.formula-item:hover { transform: translateX(-5px); }

.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px; border-radius: 12px;
    border-right: 5px solid #2e7d32; margin-bottom: 20px;
    direction: rtl; text-align: right;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
}

.warning-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 15px; border-radius: 12px;
    border-right: 5px solid #f57c00; margin-bottom: 15px;
    direction: rtl; text-align: right;
}

.profile-img-style {
    width: 150px; height: 150px; border-radius: 50%;
    object-fit: cover; border: 4px solid #d4af37;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.25);
    display: block; margin: 0 auto;
}

.stButton > button {
    color: #1a1a1a !important; background-color: #e8f5e9 !important;
    border: 1px solid #2e7d32 !important; font-weight: bold !important;
}
.stButton > button:hover { background-color: #c8e6c9 !important; }

.mini-signature {
    position: fixed; left: 20px; bottom: 60px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important; padding: 8px 20px;
    font-size: 0.85rem; border-radius: 25px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    z-index: 9997; direction: rtl;
    border: 2px solid #d4af37;
}
.mini-signature * { color: white !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# بوابة الدخول — المالك بكود فقط + دخول كزائر
# ═══════════════════════════════════════════════════════════════════════════

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 750px; margin: 30px auto; direction: rtl;">',
                unsafe_allow_html=True)
    
    # الدعاء الافتتاحي
    st.markdown(f"""
    <div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <p style="font-size:1.05rem; color:#a5d6a7 !important; margin-bottom:10px;">
        نبدأ باسم الله، ونسألُه أن يتقبّلَ هذا العملَ صدقةً جاريةً عن:
        </p>
        <div class="names">
        🕊️ رحم الله والدي إسماعيل تاور وأختي 🕊️
        </div>
        <p style="font-size:1.05rem; color:#e8f5e9 !important; margin-top:15px;">
        اللهم اجعل قبرهما روضة من رياض الجنة، واجمعنا بهما في مستقر رحمتك.
        </p>
        <p class="quran">{DUA_QURAN}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-top: 2px solid #d4af37; margin: 25px 0;'>",
                unsafe_allow_html=True)
    
    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        if img_base64:
            st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">',
                        unsafe_allow_html=True)
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
        <h4 style="color: #1b5e20; margin-bottom: 10px;">👑 المالك</h4>
        <p style="font-size: 0.9rem; color: #555;">الدخول بكود خاص</p>
        </div>
        """, unsafe_allow_html=True)
        
        owner_code = st.text_input("🔑 كود المالك:", type="password", key="owner_code")
        if st.button("👑 دخول المالك", type="primary", use_container_width=True):
            if owner_code.strip() == OWNER_CODE:
                st.session_state.update({
                    "approved": True,
                    "user_role": "owner",
                })
                st.rerun()
            else:
                st.error("❌ كود غير صحيح")
    
    with col_guest:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fff8e1, #ffecb3);
        padding: 20px; border-radius: 12px; border: 2px solid #d4af37;
        text-align: center; margin-bottom: 10px;">
        <h4 style="color: #e65100; margin-bottom: 10px;">👥 زائر</h4>
        <p style="font-size: 0.9rem; color: #555;">دخول مجاني بدون كود<br>
        <small style="color: #999;">(بيانات المالك محجوبة)</small></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True):
            st.session_state.update({
                "approved": True,
                "user_role": "guest",
            })
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
    st.markdown(f"<div style='text-align:left; padding:10px; background:#f5f5f5; border-radius:10px;'>"
                f"الحساب: <b>{role_label}</b></div>", unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k != "inventory": del st.session_state[k]
        st.session_state["approved"] = False
        st.rerun()

c3, c4 = st.columns([0.3, 0.7])
with c3:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">',
                    unsafe_allow_html=True)
with c4:
    st.markdown(f"<h1 style='color:#1b5e20; text-align:right; margin-bottom:0;'>{APP_NAME} 🌾</h1>",
                unsafe_allow_html=True)
    st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.2rem;'>{APP_TAGLINE}</p>",
                unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:#c62828; text-align:right;'>{SUPERVISOR} — {SUPERVISOR_TITLE}</h3>",
                unsafe_allow_html=True)

st.markdown(f'<div class="visitor-dua-banner">{DUA_VISITOR_BANNER}</div>',
            unsafe_allow_html=True)

st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# التبويبات
# ═══════════════════════════════════════════════════════════════════════════

if is_owner():
    tabs_titles = [
        "🔬 تركيب الأعلاف", "🍼 بدائل الحليب", "📷 المختبر الذكي",
        "📊 البورصة", "🏭 المستودعات", "🧾 الفواتير",
        "🖨️ الديباجة", "📈 التحليلات",
        "🐔 مزارع الدجاج", "💬 التعليقات",
        "📚 المراجع", "💡 المساعدة", "📖 الدليل",
    ]
else:
    tabs_titles = [
        "🔬 تركيب الأعلاف", "🍼 بدائل الحليب", "📷 المختبر الذكي",
        "📚 المراجع", "💡 المساعدة", "📖 الدليل",
    ]

tabs = st.tabs(tabs_titles)


# ═══════════════════════════════════════════════════════════════════════════
# تبويب تركيب الأعلاف
# ═══════════════════════════════════════════════════════════════════════════

with tabs[0]:
    st.markdown('<div class="section-title">🌍 الموقع الجغرافي والأسعار</div>',
                unsafe_allow_html=True)
    
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        country = st.selectbox("🌍 الدولة:", list(EXCHANGE_RATES.keys()))
    with cc2:
        state = st.text_input("🗺️ الولاية:", "الخرطوم")
    with cc3:
        city = st.text_input("🏙️ المدينة:", "الخرطوم")
    
    rate = EXCHANGE_RATES.get(country, {"rate": 1.0, "sym": "USD"})
    local_rate, local_sym = rate["rate"], rate["sym"]
    live_prices = get_market_prices(country, city, state)
    
    # عرض أسعار
    pc1, pc2 = st.columns(2)
    with pc1:
        html1 = '<div class="price-card"><b>📈 بورصة الماشية:</b><br>'
        for k, v in list(st.session_state["livestock_prices"].items())[:5]:
            html1 += f'▪️ {k}: <b>${v:.2f}</b><br>'
        html1 += '</div>'
        st.markdown(html1, unsafe_allow_html=True)
    with pc2:
        html2 = '<div class="price-card"><b>🥩 بورصة المنتجات:</b><br>'
        for k, v in list(st.session_state["products_prices"].items())[:5]:
            html2 += f'▪️ {k}: <b>${v:.2f}</b><br>'
        html2 += '</div>'
        st.markdown(html2, unsafe_allow_html=True)
    
    # 8 تبويبات حيوانات
    st.markdown('<div class="section-title">🐾 اختر الحيوان</div>',
                unsafe_allow_html=True)
    
    animal_tabs = st.tabs([
        "🐏 أغنام", "🐐 ماعز", "🐄 أبقار", "🐪 إبل",
        "🐎 خيول", "🐔 دواجن", "🦆 سمان", "🐟 أسماك",
    ])
    
    animal_choice = None
    stage_choice = None
    img_key = "عام"
    
    with animal_tabs[0]:
        st.markdown("#### 🐏 الأغنام")
        sg = st.radio("الجنس:", ["ذكور (تسمين)", "إناث (حليب)"], horizontal=True, key="sg")
        if "ذكور" in sg:
            ss = st.selectbox("المرحلة:", ["تسمين مكثف", "تسمين عادي"], key="ss_m")
        else:
            ss = st.selectbox("المرحلة:", ["نعاج مرضعات", "صيانة"], key="ss_f")
        if st.checkbox("✅ اعتماد الأغنام", key="use_sheep"):
            animal_choice, stage_choice, img_key = "أغنام", ss, "أغنام"
    
    with animal_tabs[1]:
        st.markdown("#### 🐐 الماعز")
        gg = st.radio("الجنس:", ["ذكور (تسمين)", "إناث (حليب)"], horizontal=True, key="gg")
        if "ذكور" in gg:
            gs = st.selectbox("المرحلة:", ["تسمين جديان"], key="gs_m")
        else:
            gs = st.selectbox("المرحلة:", ["عنزات حلابة", "صيانة"], key="gs_f")
        if st.checkbox("✅ اعتماد الماعز", key="use_goat"):
            animal_choice, stage_choice, img_key = "ماعز", gs, "ماعز"
    
    with animal_tabs[2]:
        st.markdown("#### 🐄 الأبقار")
        cs = st.selectbox("نوع الإنتاج:",
            ["حليب عالي الإدرار", "حليب متوسط", "تسمين مكثف", "تسمين عادي", "صيانة"],
            key="cs")
        if st.checkbox("✅ اعتماد الأبقار", key="use_cattle"):
            animal_choice, stage_choice, img_key = "أبقار", cs, "أبقار"
    
    with animal_tabs[3]:
        st.markdown("#### 🐪 الإبل")
        cams = st.selectbox("نوع الإنتاج:",
            ["نمو", "تسمين", "حليب", "سباق", "صيانة"], key="cams")
        cwt = st.number_input("الوزن (كجم):", 100.0, 800.0, 400.0, 25.0, key="cwt")
        st.info(f"المادة الجافة ≈ {cwt*0.025:.1f} كجم/يوم")
        if st.checkbox("✅ اعتماد الإبل", key="use_camel"):
            animal_choice, stage_choice, img_key = "إبل", cams, "إبل"
    
    with animal_tabs[4]:
        st.markdown("#### 🐎 الخيول")
        hs = st.selectbox("نوع الإنتاج:", ["رياضة", "نمو", "صيانة"], key="hs")
        if st.checkbox("✅ اعتماد الخيول", key="use_horse"):
            animal_choice, stage_choice, img_key = "خيول", hs, "خيول"
    
    with animal_tabs[5]:
        st.markdown("#### 🐔 الدواجن")
        ps = st.selectbox("المرحلة:", ["بادي", "نامي", "ناهي", "بياض"], key="ps")
        if st.checkbox("✅ اعتماد الدواجن", key="use_poultry"):
            animal_choice, stage_choice, img_key = "دواجن لاحم", ps, "دواجن"
    
    with animal_tabs[6]:
        st.markdown("#### 🦆 السمان")
        qs = st.selectbox("المرحلة:", ["سمان بادي", "سمان بياض"], key="qs")
        if st.checkbox("✅ اعتماد السمان", key="use_quail"):
            animal_choice, stage_choice, img_key = "سمان", qs, "سمان"
    
    with animal_tabs[7]:
        st.markdown("#### 🐟 الأسماك")
        fs = st.selectbox("المرحلة:", ["بادئ زريعة", "نمو", "تسمين"], key="fs")
        if st.checkbox("✅ اعتماد الأسماك", key="use_fish"):
            animal_choice, stage_choice, img_key = "أسماك", fs, "أسماك"
    
    if not animal_choice:
        st.warning("⚠️ اختر حيواناً واحداً وفعّل ✅ الاعتماد")
        st.stop()
    
    st.markdown(f"### 🎯 المختار: **{animal_choice}** — {stage_choice}")
    
    requester_name = st.text_input("👤 اسم طالب العلفة:",
        placeholder="مثال: مزرعة الأمل", key="requester")
    
    # اختيار المكونات
    st.markdown('<div class="section-title">🌾 المكونات</div>',
                unsafe_allow_html=True)
    
    selected_ingredients = []
    ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}",
                         expanded="الحبوب" in cat_name or "الأكساب" in cat_name):
            sub = st.columns(3)
            for i, (ing_name, ing_data) in enumerate(items.items()):
                with sub[i % 3]:
                    default_check = False
                    if ing_name in ["ملح الطعام", "الحجر الجيري (بودرة بلاط)",
                                    "فوسفات ثنائي الكالسيوم (DCP)",
                                    "مضاد سموم فطرية",
                                    "بيكربونات الصوديوم (الصودا)"]:
                        default_check = True
                    
                    checked = st.checkbox(ing_name, value=default_check,
                                            key=f"ck_{animal_choice}_{ing_name}")
                    price = live_prices.get(ing_name, 300.0)
                    
                    if is_owner():
                        price = st.number_input(f"$", min_value=5.0,
                            value=float(price),
                            key=f"p_{animal_choice}_{ing_name}",
                            label_visibility="collapsed")
                    else:
                        st.caption(f"💰 ${price:.0f}")
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price
    
    st.markdown("---")
    
    if st.button("🚀 تشغيل المحرك الذكي (فرق ≤ 0.3%)",
                 type="primary", use_container_width=True):
        if len(selected_ingredients) < 3:
            st.error("⚠️ اختر 3 مكونات على الأقل")
        else:
            # إضافة الأملاح تلقائياً
            auto_salts = auto_add_salts_and_minerals(animal_choice, {})
            for sname, spct in auto_salts.items():
                if sname not in selected_ingredients:
                    selected_ingredients.append(sname)
                    ingredient_prices[sname] = live_prices.get(sname, 300.0)
            
            with st.spinner("⏳ جاري التركيب..."):
                std_key = get_standard_key(animal_choice, stage_choice)
                result = auto_formulate_smart(
                    selected_ingredients, ingredient_prices, std_key,
                    tolerance=0.3, max_iterations=50
                )
            
            if result["success"]:
                formula = result["formula"]
                actual = result["actual_nutrients"]
                cost = result["cost"]
                std = NUTRIENT_STANDARDS.get(std_key, {})
                
                # التقييم العام
                compare_rows = []
                compare_scores = []
                labels = {"CP": "بروتين خام CP", "DP": "بروتين مهضوم DP",
                          "SE": "معادل النشاء SE", "NDF": "ألياف NDF",
                          "ADF": "ألياف ADF", "EE": "دهن EE",
                          "ASH": "رماد ASH", "Ca": "كالسيوم Ca", "P": "فسفور P"}
                
                for k, sv in std.items():
                    cv = actual.get(k, 0.0)
                    diff = cv - sv
                    pct = (diff / sv * 100) if sv else 0
                    ev = evaluate_difference(pct)
                    compare_scores.append({"score": ev["score"]})
                    compare_rows.append({
                        "العنصر": labels.get(k, k),
                        "المعيار القياسي": f"{sv:.2f}",
                        "القيمة المحسوبة": f"{cv:.2f}",
                        "الفرق": f"{diff:+.3f}",
                        "الفرق %": f"{pct:+.2f}%",
                        "التقييم": ev["label"],
                    })
                
                overall = get_overall_rating(compare_scores)
                
                perfect = result.get("perfect_match", False)
                if perfect:
                    st.success(f"🎯 **مطابقة كاملة!** جميع العناصر مطابقة (فرق ≤ 0.3%)")
                else:
                    st.success(f"✅ تم التركيب — الفرق مقبول")
                
                st.info(f"🔁 التكرارات: {result['iterations']} | "
                        f"التقييم العام: **{overall['label']}** ({overall['score']:.0f}%)")
                
                # مؤشرات الخطأ
                col_e1, col_e2, col_e3, col_e4 = st.columns(4)
                col_e1.metric("خطأ DP", f"{result['dp_error']:.3f}%")
                col_e2.metric("خطأ SE", f"{result['se_error']:.3f}")
                col_e3.metric("خطأ NDF", f"{result['ndf_error']:.2f}%")
                col_e4.metric("خطأ Ca", f"{result['ca_error']:.3f}%")
                
                # جدول المقارنة
                st.markdown("### 📊 جدول المقارنة الشامل")
                st.dataframe(pd.DataFrame(compare_rows),
                             use_container_width=True, hide_index=True)
                
                # المكونات
                st.markdown("#### 🌾 المكونات:")
                for ing, pct in formula.items():
                    st.markdown(
                        f'<div class="formula-item">▪️ <b>{ing}:</b> '
                        f'{pct:.2f}% ({pct*10:.1f} كجم/طن)</div>',
                        unsafe_allow_html=True
                    )
                
                st.metric("💰 التكلفة للطن:",
                          f"${cost:.2f} ({cost*local_rate:,.0f} {local_sym})")
                
                st.session_state["active_formula"] = formula
                st.session_state["computed_ton_cost"] = cost
                st.session_state["active_animal_img"] = ANIMAL_IMAGES.get(img_key, ANIMAL_IMAGES["عام"])
                st.session_state["active_stage_title"] = f"{animal_choice} — {stage_choice}"
                
                # تحميل
                st.markdown("### 📥 التحميل")
                dl1, dl2 = st.columns(2)
                with dl1:
                    try:
                        pdf = pdf_generator.generate_comprehensive_report(
                            formula=formula, target_dp=std.get("DP", 12),
                            breed=f"{animal_choice} — {stage_choice}",
                            cost=cost, city=city,
                            local_cost=cost * local_rate, local_sym=local_sym,
                            computed_se=actual["SE"],
                            requester_name=requester_name,
                            animal_type=animal_choice, production_stage=stage_choice,
                            include_charts=True,
                            report_type=f"تركيب — {animal_choice}"
                        )
                        st.download_button("📥 PDF",
                            pdf,
                            file_name=f"TaworNology_{animal_choice}_{datetime.now():%Y%m%d}.pdf",
                            mime="application/pdf",
                            use_container_width=True)
                    except Exception as e:
                        st.error(f"PDF: {e}")
                with dl2:
                    try:
                        xl = export_comparison_to_excel(std, actual, requester_name,
                                                        animal_choice, stage_choice, formula)
                        if xl:
                            st.download_button("📊 Excel", xl,
                                file_name=f"TaworNology_{animal_choice}_{datetime.now():%Y%m%d}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True)
                    except Exception as e:
                        st.error(f"Excel: {e}")
                
                # رسم بياني
                if PLOTLY_AVAILABLE and len(formula) > 1:
                    try:
                        colors = ['#e53935', '#8e24aa', '#3949ab', '#1e88e5',
                                  '#00897b', '#43a047', '#7cb342', '#fdd835',
                                  '#fb8c00', '#6d4c41']
                        fig = px.pie(values=list(formula.values()),
                                     names=list(formula.keys()),
                                     title="توزيع المكونات",
                                     color_discrete_sequence=colors)
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass
            else:
                st.error(f"❌ {result['message']}")
                if "log" in result:
                    with st.expander("سجل المحاولات"):
                        for line in result["log"][-10:]:
                            st.text(line)


# ═══════════════════════════════════════════════════════════════════════════
# تبويب بدائل الحليب
# ═══════════════════════════════════════════════════════════════════════════

if "🍼 بدائل الحليب" in tabs_titles:
    with tabs[tabs_titles.index("🍼 بدائل الحليب")]:
        st.markdown('<div class="section-title">🍼 مختبر بدائل الحليب</div>',
                    unsafe_allow_html=True)
        
        mr1, mr2 = st.columns(2)
        with mr1:
            mr_animal = st.selectbox("نوع الحيوان:",
                list(MILK_REPLACER_STANDARDS.keys()), key="mr_a")
            mr_volume = st.number_input("الكمية (كجم):", 1.0, 10000.0, 100.0, 10.0, key="mr_v")
            mr_requester = st.text_input("اسم طالب التركيب:", key="mr_r")
        with mr2:
            std_mr = MILK_REPLACER_STANDARDS[mr_animal]
            st.markdown(f"""
            <div class="price-card">
            <b>📊 المعيار — {mr_animal}:</b><br>
            ▪️ بروتين: <b>{std_mr['CP']}%</b><br>
            ▪️ دهن: <b>{std_mr['Fat']}%</b><br>
            ▪️ لاكتوز: <b>{std_mr['Lactose']}%</b><br>
            ▪️ ليسين: <b>{std_mr['Lysine']}%</b><br>
            ▪️ كالسيوم: <b>{std_mr['Ca']}%</b> | فوسفور: <b>{std_mr['P']}%</b><br>
            <small>{std_mr['notes']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        mr_selected = []
        mr_cols = st.columns(3)
        for i, (name, data) in enumerate(MILK_REPLACER_INGREDIENTS.items()):
            with mr_cols[i % 3]:
                default_mr = name in [
                    "حليب مجفف منزوع الدسم", "حليب مجفف كامل الدسم",
                    "شرش حليب مجفف", "زيت جوز الهند", "زيت النخيل",
                    "بريمكس فيتامينات حليب", "كالسيوم كربونات",
                    "فوسفات ثنائي الكالسيوم", "ملح طعام"
                ]
                if st.checkbox(f"{name} — ${data['price']}",
                                value=default_mr, key=f"mr_{name}"):
                    mr_selected.append(name)
        
        if st.button("🧪 تشغيل التركيب", type="primary",
                     use_container_width=True, key="mr_run"):
            if len(mr_selected) < 3:
                st.warning("⚠️ اختر 3 مكونات على الأقل")
            else:
                r = formulate_milk_replacer(mr_animal, mr_volume, mr_selected)
                if r["success"]:
                    st.success(f"✅ تم التركيب لـ ({mr_animal})")
                    
                    st.markdown("#### 📝 التركيبة لكل 100 كجم:")
                    for ing, pct in r["formula"].items():
                        kg = pct * mr_volume / 100.0
                        st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> '
                                    f'{pct:.2f}% ({kg:.2f} كجم)</div>',
                                    unsafe_allow_html=True)
                    
                    st.metric("💰 التكلفة لـ 100 كجم:", f"${r['cost_per_100kg']:.2f}")
                    st.metric("💰 التكلفة لكل كجم:", f"${r['cost_per_kg']:.3f}")
                    
                    # مقارنة
                    st.markdown("#### 📊 المقارنة:")
                    compare_mr = []
                    for k in ["CP", "Fat", "Lactose"]:
                        sv = std_mr.get(k, 0)
                        cv = r["actual"].get(k, 0)
                        diff = cv - sv
                        pct = (diff / sv * 100) if sv else 0
                        ev = evaluate_difference(pct)
                        compare_mr.append({
                            "العنصر": k,
                            "القياسي": f"{sv:.2f}%",
                            "المحسوب": f"{cv:.2f}%",
                            "الفرق": f"{pct:+.2f}%",
                            "التقييم": ev["label"],
                        })
                    st.dataframe(pd.DataFrame(compare_mr),
                                 use_container_width=True, hide_index=True)
                    
                    try:
                        pdf_mr = pdf_generator.generate_comprehensive_report(
                            formula=r["formula"], target_dp=std_mr["CP"],
                            breed=mr_animal, cost=r["cost_per_100kg"],
                            city="مختبر بدائل الحليب",
                            local_cost=r["cost_per_100kg"] * local_rate,
                            local_sym=local_sym, computed_se=0.0,
                            requester_name=mr_requester,
                            animal_type=mr_animal, production_stage="بديل حليب",
                            include_charts=True, report_type="بديل حليب"
                        )
                        st.download_button("📥 PDF", pdf_mr,
                            file_name=f"TaworNology_Milk_{mr_animal}.pdf",
                            mime="application/pdf",
                            use_container_width=True)
                    except Exception as e:
                        st.error(f"PDF: {e}")
                else:
                    st.error(f"❌ {r['message']}")


# ═══════════════════════════════════════════════════════════════════════════
# تبويب المختبر الذكي
# ═══════════════════════════════════════════════════════════════════════════

if "📷 المختبر الذكي" in tabs_titles:
    with tabs[tabs_titles.index("📷 المختبر الذكي")]:
        st.markdown('<div class="section-title">📷 المختبر الذكي (OCR)</div>',
                    unsafe_allow_html=True)
        
        if not OCR_AVAILABLE:
            st.error("⚠️ مكتبة pytesseract غير مثبتة")
            st.code("pip install pytesseract opencv-python-headless", language="bash")
        else:
            uploaded = st.file_uploader("📤 ارفع صورة:", type=["jpg", "jpeg", "png"])
            if uploaded:
                st.image(uploaded, caption="الصورة", use_container_width=True)
                ocr_req = st.text_input("👤 اسم طالب التحليل:", key="ocr_req")
                
                if st.button("🔍 تحليل", type="primary", use_container_width=True):
                    with st.spinner("جاري التحليل..."):
                        r = extract_ingredients_from_image(uploaded.read())
                    
                    if r["success"]:
                        st.success(f"✅ تم استخراج {r['count']} مادة")
                        if r["ingredients"]:
                            st.dataframe(pd.DataFrame([
                                {"المادة": k, "النسبة": f"{v:.2f}%"}
                                for k, v in r["ingredients"].items()
                            ]), use_container_width=True, hide_index=True)
                            
                            nutrients = compute_formula_nutrients(r["ingredients"])
                            n1, n2, n3, n4 = st.columns(4)
                            n1.metric("CP", f"{nutrients['CP']:.2f}%")
                            n2.metric("DP", f"{nutrients['DP']:.2f}%")
                            n3.metric("SE", f"{nutrients['SE']:.2f}")
                            n4.metric("NDF", f"{nutrients['NDF']:.2f}%")
                            
                            ocr_animal = st.selectbox("للمقارنة مع:",
                                ["أغنام", "ماعز", "أبقار", "إبل", "دواجن لاحم", "سمان", "أسماك"],
                                key="ocr_animal")
                            ocr_stage = st.text_input("المرحلة:", "تسمين", key="ocr_stage")
                            std_ocr_key = get_standard_key(ocr_animal, ocr_stage)
                            std_ocr = NUTRIENT_STANDARDS.get(std_ocr_key, {})
                            
                            compare_ocr = []
                            scores = []
                            for k, sv in std_ocr.items():
                                cv = nutrients.get(k, 0)
                                pct = ((cv - sv) / sv * 100) if sv else 0
                                ev = evaluate_difference(pct)
                                scores.append({"score": ev["score"]})
                                compare_ocr.append({
                                    "العنصر": k, "القياسي": f"{sv:.2f}",
                                    "المحسوب": f"{cv:.2f}",
                                    "الفرق %": f"{pct:+.2f}%",
                                    "التقييم": ev["label"],
                                })
                            st.dataframe(pd.DataFrame(compare_ocr),
                                         use_container_width=True, hide_index=True)
                            
                            overall = get_overall_rating(scores)
                            st.info(f"🏆 التقييم العام: **{overall['label']}** ({overall['score']:.0f}%)")
                        
                        with st.expander("النص الخام"):
                            st.text(r.get("raw_text", ""))
                    else:
                        st.error(f"❌ {r['message']}")


# ═══════════════════════════════════════════════════════════════════════════
# تبويبات المالك
# ═══════════════════════════════════════════════════════════════════════════

if is_owner():
    # البورصة
    if "📊 البورصة" in tabs_titles:
        with tabs[tabs_titles.index("📊 البورصة")]:
            st.markdown('<div class="section-title">📊 البورصة</div>', unsafe_allow_html=True)
            t1, t2 = st.tabs(["🐄 الماشية", "🥩 المنتجات"])
            with t1:
                for animal, price in st.session_state["livestock_prices"].items():
                    new_p = st.number_input(f"تحديث: {animal}", min_value=0.0,
                        value=float(price), step=0.1, key=f"lv_{animal}")
                    st.session_state["livestock_prices"][animal] = new_p
            with t2:
                for product, price in st.session_state["products_prices"].items():
                    new_p = st.number_input(f"تحديث: {product}", min_value=0.0,
                        value=float(price), step=0.05, key=f"pr_{product}")
                    st.session_state["products_prices"][product] = new_p
    
    # المستودعات
    if "🏭 المستودعات" in tabs_titles:
        with tabs[tabs_titles.index("🏭 المستودعات")]:
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
                    new_q = st.number_input(f"تحديث:", min_value=0.0,
                        value=float(q), key=f"inv_{name}",
                        label_visibility="collapsed")
                    if isinstance(inv[name], dict):
                        inv[name]["quantity"] = new_q
    
    # الفواتير
    if "🧾 الفواتير" in tabs_titles:
        with tabs[tabs_titles.index("🧾 الفواتير")]:
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
    
    # الديباجة
    if "🖨️ الديباجة" in tabs_titles:
        with tabs[tabs_titles.index("🖨️ الديباجة")]:
            st.markdown('<div class="section-title">🖨️ الديباجة</div>',
                        unsafe_allow_html=True)
            brand = st.text_input("اسم البراند:", APP_NAME)
            st.markdown(f"""
            <div style="border: 3px dashed #1b5e20; padding: 30px; border-radius: 15px;
            background: linear-gradient(135deg, #f1f8e9, #e8f5e9); direction: rtl; text-align: center;">
            <img src="{st.session_state['active_animal_img']}"
            style="width:100%; max-height:200px; object-fit:cover; border-radius:12px; margin-bottom:15px;">
            <h2 style="color: #1b5e20;">🌟 {brand} 🌟</h2>
            <h3 style="color: #c62828;">{SUPERVISOR} — {SUPERVISOR_TITLE}</h3>
            <p style="background:#e8f5e9; padding:12px; border-radius:8px; color:#1b5e20; font-weight:bold;">
            🎯 {st.session_state['active_stage_title']}
            </p>
            <small style="color:#666;">📅 {datetime.now():%Y-%m-%d}</small><br>
            <small style="color:#c62828;">🤲 {DUA_SHORT}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # التحليلات
    if "📈 التحليلات" in tabs_titles:
        with tabs[tabs_titles.index("📈 التحليلات")]:
            st.markdown('<div class="section-title">📈 التحليلات</div>',
                        unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("الخلطات", "1,247")
            m2.metric("متوسط التكلفة", "$285")
            m3.metric("التوفير", "18%")
            m4.metric("رضا العملاء", "96%")
    
    # مزارع الدجاج
    if "🐔 مزارع الدجاج" in tabs_titles:
        with tabs[tabs_titles.index("🐔 مزارع الدجاج")]:
            st.markdown('<div class="section-title">🐔 مزارع الدجاج اللاحم</div>',
                        unsafe_allow_html=True)
            st.info("📘 سجل المزارع و KPIs")
            
            with st.expander("➕ إضافة مزرعة"):
                nf_name = st.text_input("اسم المزرعة:", key="nf_name")
                nf_owner = st.text_input("المالك:", key="nf_owner")
                nf_phone = st.text_input("واتساب:", WHATSAPP_NUMBER, key="nf_phone")
                if st.button("💾 حفظ") and nf_name:
                    st.session_state["broiler_farms"][nf_name] = {
                        "owner": nf_owner, "owner_phone": nf_phone,
                        "data": {"age": 1, "birds": 1000, "weight_kg": 0.045,
                                 "feed_kg": 0.0, "dead": 0, "temp": 33.0, "hum": 65.0}
                    }
                    st.success(f"✅ تمت إضافة {nf_name}")
                    st.rerun()
            
            if st.session_state["broiler_farms"]:
                farms = list(st.session_state["broiler_farms"].keys())
                sel = st.selectbox("اختر مزرعة:", [""] + farms)
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
                    epef = (liv * d["weight_kg"]) / (d["age"] * fcr) * 100 if d["age"] > 0 and fcr > 0 else 0
                    
                    k1, k2, k3 = st.columns(3)
                    k1.metric("ADG (جم)", f"{adg:.1f}")
                    k2.metric("FCR", f"{fcr:.2f}")
                    k3.metric("EPEF", f"{epef:.0f}")
    
    # التعليقات
    if "💬 التعليقات" in tabs_titles:
        with tabs[tabs_titles.index("💬 التعليقات")]:
            st.markdown('<div class="section-title">💬 التعليقات</div>',
                        unsafe_allow_html=True)
            st.text_area("الحالية:", value=st.session_state["shared_comments"],
                         height=200, disabled=True)
            nc = st.text_area("جديد:")
            if st.button("➕ نشر") and nc:
                st.session_state["shared_comments"] += (
                    f"\n• [{datetime.now():%Y-%m-%d %H:%M}]: {nc}")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# المراجع والمساعدة والدليل
# ═══════════════════════════════════════════════════════════════════════════

with tabs[tabs_titles.index("📚 المراجع")]:
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>',
                unsafe_allow_html=True)
    st.markdown("""
    ### المراجع المعتمدة:
    - **NRC (2012)** — Nutrient Requirements of Swine
    - **NRC (2007)** — Nutrient Requirements of Small Ruminants
    - **NRC (2001)** — Nutrient Requirements of Dairy Cattle
    - **INRA (2007)** — Feeding System for Ruminants
    - **FAO (2010)** — Camel Nutrition and Feeding
    - **Ross 308 (2020)** — Broiler Management Handbook
    - **McDonald et al. (2011)** — Animal Nutrition
    - **Van Soest (1994)** — Nutritional Ecology of the Ruminant
    """)

with tabs[tabs_titles.index("💡 المساعدة")]:
    st.markdown('<div class="section-title">💡 المساعدة</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    ### الأسئلة الشائعة:
    - **كيف أبدأ؟** اختر الحيوان من التبويبات وأكد الاختيار.
    - **المحرك الذكي؟** يطابق تلقائياً البروتين والطاقة والألياف والمعادن.
    - **ما الفرق؟** بين CP و DP: DP أدق (يأخذ معامل الهضم).
    - **تقييماتي؟** ممتاز / جيد جداً / جيد / مقبول / ضعيف.

    ### 🔧 الدعم الفني
    📧 {OWNER_EMAIL}
    📱 {WHATSAPP_NUMBER}
    
    ### 🕌 دعاء
    {DUA_FULL}
    """)

with tabs[tabs_titles.index("📖 الدليل")]:
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    ### الغرض
    **{APP_NAME}** — منصة ذكية لتركيب الأعلاف بأقل تكلفة وأعلى جودة.
    
    ### الميزات
    - 🔬 **8 قطاعات**: أغنام، ماعز، أبقار، إبل، خيول، دواجن، سمان، أسماك
    - 🧠 **محرك ذكي**: يطابق DP، SE، NDF، ADF، Ca، P تلقائياً
    - 🍼 **بدائل الحليب**: 5 أنواع حيوانات
    - 📷 **مختبر OCR**: تحليل صور المكونات
    - 📄 **PDF احترافي**: ختم، ترويسة، رسوم بيانية ملوّنة
    - 📊 **Excel**: تقارير ملونة
    
    ### التقييمات
    - 🎯 **مطابق تماماً**: 0-0.5%
    - 🌟 **ممتاز**: 0.5-2%
    - ✅ **جيد جداً**: 2-5%
    - 🟢 **جيد**: 5-10%
    - ⭐ **مقبول**: 10-15%
    - ⚠️ **مقبول بتحفظ**: 15-25%
    - 🟠 **ضعيف**: 25-40%
    - ❌ **غير مطابق**: >40%
    
    ### كود المالك
    `{OWNER_CODE}`
    """)


# ═══════════════════════════════════════════════════════════════════════════
# التذييل
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(
    f'<div class="mini-signature">🌾 {APP_NAME} | {SUPERVISOR} © 2026</div>',
    unsafe_allow_html=True
)
st.markdown(
    f'<div class="dua-fixed-banner">🤲 {DUA_SHORT} 🤲</div>',
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# نهاية الملف
# ═══════════════════════════════════════════════════════════════════════════
