# ============================================================================
# ████████████████████████████████████████████████████████████████████████████
# █                                                                          █
# █        تاور نولجي TAWOR NOLOGY — الإصدار المدمج النهائي 20.0            █
# █        للإنتاج الحيواني وتغذية الحيوان وتركيب الأعلاف الذكي             █
# █                                                                          █
# █        إشراف: الاختصاصي م. عبدالقادر إسماعيل تاور                       █
# █        اختصاصي تغذية الحيوان                                             █
# █                                                                          █
# █   🕊️ رحم الله والدي إسماعيل تاور وأختي ابتسام 🕊️                       █
# █                                                                          █
# █   الميزات: 15 زيتاً + محرك ذكي + OCR + إدارة مزارع + PDF + Excel       █
# █                                                                          █
# ████████████████████████████████████████████████████████████████████████████
# ============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import json, os, base64, time, re, io, sqlite3, hashlib, secrets, warnings
import urllib.parse, urllib.request, smtplib
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Optional
from dataclasses import dataclass

warnings.filterwarnings('ignore')

# ─── مكتبات علمية ──────────────────────────────────────────────────────────
try:
    from scipy.optimize import linprog
    SCIPY = True
except ImportError:
    SCIPY = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY = True
except ImportError:
    PLOTLY = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Wedge
    MPL = True
except ImportError:
    MPL = False

try:
    from gtts import gTTS
    GTTS = True
except ImportError:
    GTTS = False

try:
    import pytesseract
    import cv2
    OCR = True
except ImportError:
    OCR = False

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    XLSX = True
except ImportError:
    XLSX = False

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
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    REPORTLAB = True
except ImportError:
    REPORTLAB = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC = True
except ImportError:
    ARABIC = False

try:
    import qrcode
    QRCODE = True
except ImportError:
    QRCODE = False


# ═════════════════════════════════════════════════════════════════════════════
# [1] الثوابت والدعاء
# ═════════════════════════════════════════════════════════════════════════════

APP_NAME = "تاور نولجي Tawor Nology"
APP_TAGLINE = "للإنتاج الحيواني وتغذية الحيوان"
SUPERVISOR = "م. عبدالقادر إسماعيل تاور"
SUPERVISOR_TITLE = "اختصاصي تغذية الحيوان"
OWNER_CODE = "202687"
SPECIALIST_CODE = "2020"
VET_CODE = "2024"
NUTRITIONIST_CODE = "2025"
BREEDER_CODE = "2026"
PLATFORM_URL = "https://tawor-nology.streamlit.app"
WHATSAPP = "+249123533489"
OWNER_EMAIL = "abukram128@gmail.com"
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG"]
LOGO_OPTIONS = ["logo.png", "logo.jpg"]

DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي ابتسام"
DUA_FULL = ("رحم الله والدي إسماعيل تاور وأختي ابتسام، وأسكنهما فسيح جناته، "
            "وجعل قبرهما روضة من رياض الجنة")
DUA_QURAN = "﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾"
DUA_VERSE = "﴿ وَقُل رَّبِّ ارْحَمْهُمَا كَمَا رَبَّيَانِي صَغِيرًا ﴾"

st.set_page_config(page_title=f"{APP_NAME} | {APP_TAGLINE}", page_icon="🌾",
                    layout="wide", initial_sidebar_state="collapsed")


# ═════════════════════════════════════════════════════════════════════════════
# [2] معالج الخط العربي
# ═════════════════════════════════════════════════════════════════════════════

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
        if not REPORTLAB: return
        paths = [os.path.join(FONT_DIR, "Amiri-Regular.ttf"),
                 "Amiri-Regular.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        for p in paths:
            if os.path.exists(p) and self._register(p): return
        try:
            url = ("https://github.com/google/fonts/raw/main/ofl/amiri/"
                   "Amiri-Regular.ttf")
            target = os.path.join(FONT_DIR, "Amiri-Regular.ttf")
            urllib.request.urlretrieve(url, target)
            self._register(target)
        except Exception:
            pass

    def _register(self, path):
        try:
            pdfmetrics.registerFont(TTFont('TaworArabic', path))
            self.font_name = self.font_bold = 'TaworArabic'
            self.ready = True
            return True
        except Exception:
            return False


font_mgr = ArabicFontManager()


@lru_cache(maxsize=5000)
def ar(text):
    """معالجة النص العربي لـ PDF"""
    if not text: return ""
    if not ARABIC: return str(text)
    try:
        return get_display(arabic_reshaper.reshape(str(text)), base_dir='R')
    except Exception:
        return str(text)


# ═════════════════════════════════════════════════════════════════════════════
# [3] مكتبة الأعلاف الشاملة + الزيوت
# ═════════════════════════════════════════════════════════════════════════════

BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP":8.5,"DC":0.85,"SE":80,"NDF":9.5,"ADF":3.2,"EE":3.8,"ASH":1.3,"Ca":0.02,"P":0.27},
        "ذرة بيضاء": {"CP":8.8,"DC":0.83,"SE":78,"NDF":10.2,"ADF":3.5,"EE":3.5,"ASH":1.4,"Ca":0.02,"P":0.26},
        "شعير مطحون": {"CP":11.5,"DC":0.80,"SE":71,"NDF":18.5,"ADF":7.5,"EE":2.2,"ASH":2.5,"Ca":0.05,"P":0.35},
        "سورجم (فتريتة)": {"CP":10,"DC":0.78,"SE":70,"NDF":12.5,"ADF":5.5,"EE":3,"ASH":1.8,"Ca":0.03,"P":0.30},
        "قمح محلي": {"CP":12,"DC":0.85,"SE":75,"NDF":11.5,"ADF":3.8,"EE":2,"ASH":1.6,"Ca":0.04,"P":0.32},
        "جريش أرز": {"CP":7.8,"DC":0.82,"SE":82,"NDF":5.5,"ADF":2.5,"EE":8.5,"ASH":4.2,"Ca":0.06,"P":0.30},
        "دخن محلي": {"CP":11,"DC":0.75,"SE":68,"NDF":15.5,"ADF":6.5,"EE":4,"ASH":2.2,"Ca":0.05,"P":0.31},
        "شوفان علفي": {"CP":11,"DC":0.76,"SE":62,"NDF":27.5,"ADF":13.5,"EE":5,"ASH":3,"Ca":0.08,"P":0.35},
        "كسرة خبز": {"CP":10.5,"DC":0.82,"SE":75,"NDF":8,"ADF":3.5,"EE":5.5,"ASH":3.5,"Ca":0.10,"P":0.20},
        "بسكويت مكسر": {"CP":8.5,"DC":0.85,"SE":85,"NDF":4,"ADF":2,"EE":12,"ASH":2.5,"Ca":0.08,"P":0.18},
    },
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني": {"CP":46,"DC":0.88,"SE":73,"NDF":15.5,"ADF":8.5,"EE":1.5,"ASH":5.5,"Ca":0.20,"P":0.65},
        "كسب فول صويا 44%": {"CP":44,"DC":0.90,"SE":74,"NDF":13.5,"ADF":8,"EE":1.8,"ASH":6,"Ca":0.35,"P":0.65},
        "كسب فول صويا 48%": {"CP":48,"DC":0.91,"SE":76,"NDF":12,"ADF":7,"EE":1.5,"ASH":6.2,"Ca":0.35,"P":0.65},
        "كسب عباد الشمس 36%": {"CP":36,"DC":0.76,"SE":42,"NDF":38.5,"ADF":25.5,"EE":2.5,"ASH":6.5,"Ca":0.40,"P":1.00},
        "كسب بذور القطن": {"CP":41,"DC":0.78,"SE":55,"NDF":24.5,"ADF":15.5,"EE":1.2,"ASH":6.5,"Ca":0.20,"P":1.10},
        "كسب بذور الكتان": {"CP":32,"DC":0.82,"SE":65,"NDF":18.5,"ADF":10.5,"EE":2.8,"ASH":5.8,"Ca":0.35,"P":0.85},
        "كسب السمسم": {"CP":42,"DC":0.84,"SE":70,"NDF":14.5,"ADF":9.5,"EE":8.5,"ASH":12.5,"Ca":2.00,"P":1.20},
        "كسب جلوتين 60%": {"CP":60,"DC":0.92,"SE":85,"NDF":8.5,"ADF":5.5,"EE":2.5,"ASH":3.5,"Ca":0.15,"P":0.50},
        "كسب نواة النخيل": {"CP":16,"DC":0.65,"SE":52,"NDF":55.5,"ADF":35.5,"EE":6.5,"ASH":4.5,"Ca":0.30,"P":0.55},
        "كسب الكانولا": {"CP":36,"DC":0.82,"SE":60,"NDF":28,"ADF":18,"EE":3.5,"ASH":6.5,"Ca":0.65,"P":1.10},
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP":15,"DC":0.72,"SE":45,"NDF":35.5,"ADF":12.5,"EE":3.5,"ASH":5.5,"Ca":0.12,"P":1.10},
        "نخالة ذرة": {"CP":9.5,"DC":0.65,"SE":40,"NDF":40,"ADF":15,"EE":4,"ASH":2,"Ca":0.10,"P":0.75},
        "البرسيم الجاف": {"CP":16.5,"DC":0.60,"SE":35,"NDF":42.5,"ADF":32.5,"EE":2,"ASH":10.5,"Ca":1.50,"P":0.25},
        "برسيم حجازي": {"CP":18,"DC":0.62,"SE":38,"NDF":40,"ADF":30,"EE":2.2,"ASH":11,"Ca":1.60,"P":0.26},
        "مولاس قصب السكر": {"CP":4,"DC":0.95,"SE":50,"NDF":1.5,"ADF":0.8,"EE":0.5,"ASH":8.5,"Ca":0.70,"P":0.05},
        "تبن قمح": {"CP":3.2,"DC":0.35,"SE":18,"NDF":72.5,"ADF":45.5,"EE":1.5,"ASH":8.5,"Ca":0.30,"P":0.08},
        "قشر فول سوداني": {"CP":5,"DC":0.30,"SE":15,"NDF":65.5,"ADF":42.5,"EE":1,"ASH":5.5,"Ca":0.25,"P":0.10},
        "سرسة الأرز": {"CP":2.5,"DC":0.25,"SE":12,"NDF":68.5,"ADF":48.5,"EE":12.5,"ASH":15.5,"Ca":0.15,"P":0.08},
        "قش أرز": {"CP":3.5,"DC":0.30,"SE":15,"NDF":70,"ADF":45,"EE":1.5,"ASH":12,"Ca":0.20,"P":0.06},
        "مخلفات النخيل": {"CP":6.5,"DC":0.70,"SE":60,"NDF":25,"ADF":15,"EE":5,"ASH":3.5,"Ca":0.15,"P":0.15},
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP":60,"DC":0.85,"SE":65,"NDF":2.5,"ADF":1.5,"EE":8.5,"ASH":22.5,"Ca":5.50,"P":3.20},
        "مسحوق أسماك 72%": {"CP":72,"DC":0.90,"SE":72,"NDF":2,"ADF":1,"EE":9.5,"ASH":18.5,"Ca":4.80,"P":2.80},
        "مسحوق اللحم والعظم": {"CP":50,"DC":0.75,"SE":50,"NDF":3.5,"ADF":2.5,"EE":10.5,"ASH":32.5,"Ca":9.00,"P":4.50},
        "مسحوق الدم": {"CP":80,"DC":0.65,"SE":55,"NDF":1,"ADF":0.5,"EE":1.5,"ASH":6,"Ca":0.30,"P":0.30},
        "مسحوق ريش": {"CP":82,"DC":0.70,"SE":60,"NDF":1.5,"ADF":1,"EE":3,"ASH":4,"Ca":0.25,"P":0.35},
        "مركزات دواجن": {"CP":40,"DC":0.85,"SE":60,"NDF":8.5,"ADF":4.5,"EE":3.5,"ASH":12.5,"Ca":2.50,"P":1.20},
        "مركزات مواشي": {"CP":36,"DC":0.80,"SE":55,"NDF":15.5,"ADF":8.5,"EE":3,"ASH":15.5,"Ca":3.00,"P":1.50},
    },
    "🌿 الأعلاف الخضراء المائية": {
        "أزولا مجففة": {"CP":24,"DC":0.65,"SE":45,"NDF":38,"ADF":25,"EE":3.5,"ASH":18,"Ca":2.00,"P":0.60},
        "سبيرولينا": {"CP":60,"DC":0.85,"SE":65,"NDF":5,"ADF":3,"EE":6,"ASH":10,"Ca":1.20,"P":0.90},
        "كلوريلا": {"CP":55,"DC":0.80,"SE":60,"NDF":6,"ADF":3.5,"EE":8,"ASH":12,"Ca":0.50,"P":1.20},
        "طحالب بحرية": {"CP":15,"DC":0.60,"SE":30,"NDF":25,"ADF":15,"EE":2,"ASH":30,"Ca":1.50,"P":0.30},
    },
    # 🌰 15 زيتاً بمعايير NRC / INRA / FAO
    "🌰 الزيوت النباتية والحيوانية": {
        "زيت ذرة": {"CP":0,"DC":0,"SE":220,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,
                    "desc":"طاقة عالية 9000 kcal/kg، غني بأوميغا 6","max_poultry":6,"max_ruminant":5,"source":"NRC 2012"},
        "زيت فول الصويا": {"CP":0,"DC":0,"SE":215,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,
                    "desc":"أشهر زيوت الأعلاف، متوازن، 8800 kcal/kg","max_poultry":8,"max_ruminant":5,"source":"Ross 308"},
        "زيت عباد الشمس": {"CP":0,"DC":0,"SE":210,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,
                    "desc":"غني بأوميغا 6، رخيص نسبياً","max_poultry":6,"max_ruminant":4,"source":"NRC 2007"},
        "زيت بذرة القطن": {"CP":0,"DC":0,"SE":200,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,
                    "desc":"يحتوي جوسيبول (يجب معادلة)","max_poultry":3,"max_ruminant":5,"source":"NRC 2012"},
        "زيت الكتان": {"CP":0,"DC":0,"SE":205,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,
                    "desc":"غني جداً بأوميغا 3، ممتاز للخيول","max_poultry":3,"max_ruminant":3,"source":"NRC 2007"},
        "زيت جوز الهند": {"CP":0,"DC":0,"SE":230,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,
                    "desc":"دهون MCT، سهل الهضم، مضاد بكتيري","max_poultry":5,"max_ruminant":3,"source":"NRC 2012"},
        "زيت النخيل": {"CP":0,"DC":0,"SE":215,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,
                    "desc":"طاقة عالية، مقاوم للأكسدة","max_poultry":6,"max_ruminant":5,"source":"NRC 2012"},
        "زيت الكانولا": {"CP":0,"DC":0,"SE":200,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,
                    "desc":"متوازن أوميغا 3 و6","max_poultry":5,"max_ruminant":5,"source":"NRC 2012"},
        "زيت السمسم": {"CP":0,"DC":0,"SE":205,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,
                    "desc":"غني بمضادات الأكسدة الطبيعية","max_poultry":4,"max_ruminant":3,"source":"NRC 2007"},
        "زيت الزيتون": {"CP":0,"DC":0,"SE":210,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,
                    "desc":"غني بأوميغا 9، مضاد أكسدة قوي","max_poultry":4,"max_ruminant":4,"source":"INRA 2018"},
        "زيت الأفوكادو": {"CP":0,"DC":0,"SE":210,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,
                    "desc":"غني بفيتامين E","max_poultry":3,"max_ruminant":3,"source":"NRC 2012"},
        "زيت القرطم": {"CP":0,"DC":0,"SE":205,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,
                    "desc":"غني جداً بأوميغا 6 (75%)","max_poultry":4,"max_ruminant":3,"source":"NRC 2012"},
        "زيت الفول السوداني": {"CP":0,"DC":0,"SE":210,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,
                    "desc":"طاقة عالية جداً 8900 kcal/kg","max_poultry":5,"max_ruminant":4,"source":"NRC 2012"},
        "شحم حيواني (Tallow)": {"CP":0,"DC":0,"SE":230,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,
                    "desc":"9500 kcal/kg، صلب، مقاوم للأكسدة","max_poultry":6,"max_ruminant":5,"source":"NRC 2012"},
        "زيت السمك (Fish Oil)": {"CP":0,"DC":0,"SE":235,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,
                    "desc":"غني بأوميغا 3 EPA/DHA","max_poultry":2,"max_ruminant":2,"source":"NRC Fish"},
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": {"CP":94,"DC":1.00,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0.5,"Ca":0,"P":0},
        "ميثيونين نقي": {"CP":58,"DC":1.00,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0.3,"Ca":0,"P":0},
        "ثريونين نقي": {"CP":72,"DC":1.00,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0.2,"Ca":0,"P":0},
        "تريبتوفان نقي": {"CP":85,"DC":1.00,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0.1,"Ca":0,"P":0},
        "فالين نقي": {"CP":90,"DC":1.00,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0.1,"Ca":0,"P":0},
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":100,"Ca":18,"P":8},
        "بريمكس بياض": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":100,"Ca":22,"P":7},
        "بريمكس أبقار": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":100,"Ca":20,"P":10},
        "بريمكس مجترات": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":100,"Ca":18,"P":9},
        "بريمكس خيول": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":100,"Ca":15,"P":8},
        "بريمكس إبل": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":100,"Ca":20,"P":10},
        "بريمكس أسماك": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":100,"Ca":15,"P":7},
        "إنزيم فايتيز": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":5,"Ca":0,"P":0},
        "إنزيم NSP": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":3,"Ca":0,"P":0},
        "كبريتات الحديدوز": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":98,"Ca":0,"P":0},
        "خمائر حية": {"CP":45,"DC":0.75,"SE":30,"NDF":8,"ADF":4,"EE":1,"ASH":8,"Ca":0.15,"P":1.20},
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":99.5,"Ca":38,"P":0},
        "فوسفات ثنائي الكالسيوم": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":98.5,"Ca":23,"P":18},
        "ملح الطعام": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":99.9,"Ca":0,"P":0},
        "بيكربونات الصوديوم": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":99,"Ca":0,"P":0},
        "أكسيد المغنيسيوم": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":99.5,"Ca":0,"P":0},
        "يوريا علفية": {"CP":287,"DC":0.95,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":1,"Ca":0,"P":0},
        "مضاد سموم فطرية": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":85,"Ca":0,"P":0},
        "كولين كلوريد": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":100,"Ca":0,"P":0},
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# [4] معايير الزيوت — NRC / INRA / Ross / FAO
# ═════════════════════════════════════════════════════════════════════════════

MAX_OIL_PERCENTAGE = {
    "دواجن_بادي": {"max":8.0,"optimal":5.0,"source":"Ross 308 2020"},
    "دواجن_نامي": {"max":7.0,"optimal":4.5,"source":"Ross 308 2020"},
    "دواجن_ناهي": {"max":7.0,"optimal":4.0,"source":"Ross 308 2020"},
    "دواجن_بياض": {"max":5.0,"optimal":2.5,"source":"NRC 1994"},
    "سمان_بادي":  {"max":6.0,"optimal":4.0,"source":"NRC Quail"},
    "سمان_بياض":  {"max":5.0,"optimal":2.5,"source":"NRC Quail"},
    "أبقار_حليب_عالي":   {"max":6.0,"optimal":4.0,"source":"NRC 2001"},
    "أبقار_حليب_متوسط":  {"max":5.0,"optimal":3.5,"source":"NRC 2001"},
    "أبقار_تسمين_مكثف":  {"max":6.0,"optimal":4.5,"source":"NRC 2001"},
    "أبقار_تسمين_عادي":  {"max":5.0,"optimal":3.5,"source":"NRC 2001"},
    "أغنام_تسمين_مكثف":  {"max":5.0,"optimal":3.5,"source":"NRC 2007"},
    "أغنام_تسمين_عادي":  {"max":4.5,"optimal":3.0,"source":"NRC 2007"},
    "أغنام_مرضعات":      {"max":5.0,"optimal":3.5,"source":"NRC 2007"},
    "ماعز_تسمين":        {"max":5.0,"optimal":3.5,"source":"NRC 2007"},
    "ماعز_حلابة":        {"max":5.0,"optimal":3.5,"source":"NRC 2007"},
    "إبل_نمو":           {"max":5.0,"optimal":3.5,"source":"FAO 2010"},
    "إبل_تسمين":         {"max":6.0,"optimal":4.0,"source":"FAO 2010"},
    "إبل_حليب":          {"max":5.0,"optimal":3.5,"source":"FAO 2010"},
    "إبل_سباق":          {"max":8.0,"optimal":6.0,"source":"FAO 2010"},
    "خيول_رياضة_مكثف":   {"max":10.0,"optimal":7.0,"source":"NRC 2007 Horses"},
    "خيول_رياضة_عادي":   {"max":8.0,"optimal":5.0,"source":"NRC 2007 Horses"},
    "خيول_نمو":          {"max":8.0,"optimal":5.0,"source":"NRC 2007 Horses"},
    "خيول_مرضعات":       {"max":8.0,"optimal":5.5,"source":"NRC 2007 Horses"},
    "أسماك_بادئ":        {"max":15.0,"optimal":10.0,"source":"NRC Fish"},
    "أسماك_نمو":         {"max":12.0,"optimal":8.0,"source":"NRC Fish"},
    "أسماك_تسمين":       {"max":12.0,"optimal":8.0,"source":"NRC Fish"},
}


def get_oil_standard(key):
    return MAX_OIL_PERCENTAGE.get(key, {"max":5.0,"optimal":3.0,"source":"NRC عام"})


def get_oil_ingredients():
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت النباتية والحيوانية", {})


# ═════════════════════════════════════════════════════════════════════════════
# [5] الاحتياجات المتخصصة لكل حيوان — NRC / FAO
# ═════════════════════════════════════════════════════════════════════════════

@dataclass
class AnimalRequirement:
    DP: float; CP: float; SE: float; NDF: float; ADF: float
    EE: float; ASH: float; Ca: float; P: float
    name_ar: str = ""; note: str = ""; oil_key: str = ""


def req_cattle(prod, milk=20.0, weight=500.0):
    if prod == "حليب_عالي":
        dp = 12.5 + milk*0.30
        return AnimalRequirement(round(dp,2), round(dp/0.70,2),
            round(60+milk*0.35,1), 30, 19, 5.5, 8,
            round(0.55+milk*0.003,3), round(0.33+milk*0.0015,3),
            "أبقار حلابة عالية", f"إنتاج {milk} كجم/يوم", "أبقار_حليب_عالي")
    if prod == "حليب_متوسط":
        dp = 11.0 + milk*0.25
        return AnimalRequirement(round(dp,2), round(dp/0.72,2),
            round(55+milk*0.30,1), 33, 21, 4.5, 8,
            round(0.50+milk*0.0025,3), round(0.30+milk*0.0012,3),
            "أبقار حلابة متوسطة", f"إنتاج {milk} كجم/يوم", "أبقار_حليب_متوسط")
    if prod == "حليب_منخفض":
        dp = 9.5 + milk*0.20
        return AnimalRequirement(round(dp,2), round(dp/0.75,2),
            round(50+milk*0.25,1), 38, 24, 4, 8.5,
            round(0.45+milk*0.002,3), round(0.28+milk*0.001,3),
            "أبقار حلابة منخفضة", f"إنتاج {milk} كجم/يوم", "أبقار_حليب_متوسط")
    if prod == "تسمين_مكثف":
        return AnimalRequirement(11.5, 14.5, 72, 32, 20, 4.5, 7.5, 0.65, 0.38,
            "تسمين عجول مكثف", "ADG > 1.3 كجم/يوم", "أبقار_تسمين_مكثف")
    if prod == "تسمين_عادي":
        return AnimalRequirement(9.5, 12, 65, 38, 24, 4, 7.5, 0.55, 0.32,
            "تسمين عجول عادي", "ADG ~0.8 كجم/يوم", "أبقار_تسمين_عادي")
    if prod == "حمل_أخير":
        return AnimalRequirement(11.5, 14.5, 67, 35, 22, 4.2, 8, 0.70, 0.42,
            "حمل آخر (شهر 7-9)", "دفع غذائي جنيني", "أبقار_حليب_متوسط")
    return AnimalRequirement(7.5, 10, 53, 45, 28, 3, 8.5, 0.42, 0.26,
        "أبقار صيانة", "بدون إنتاج", "أبقار_تسمين_عادي")


def req_sheep(prod, is_male=True, litter=1):
    if is_male:
        if prod == "تسمين_مكثف":
            return AnimalRequirement(11.5, 14.5, 64, 28, 17, 4, 8, 0.65, 0.36,
                "تسمين حملان مكثف", "ADG > 250 جم/يوم", "أغنام_تسمين_مكثف")
        if prod == "تسمين_عادي":
            return AnimalRequirement(9.5, 12, 59, 33, 21, 3.6, 8, 0.55, 0.32,
                "تسمين حملان عادي", "ADG ~180 جم/يوم", "أغنام_تسمين_عادي")
        return AnimalRequirement(8.5, 11, 55, 38, 24, 3.2, 8.5, 0.50, 0.30,
            "حملان تيد", "تسمين نهائي", "أغنام_تسمين_عادي")
    if prod == "مرضعات":
        dp = 10.5 + (litter-1)*1.5
        return AnimalRequirement(round(dp,2), round(dp/0.72,2),
            round(60+(litter-1)*5,1), 30, 19, 4.5, 8.5,
            round(0.65+(litter-1)*0.10,3), round(0.38+(litter-1)*0.05,3),
            f"نعاج مرضعات ({litter} مواليد)", "إنتاج حليب مرتفع", "أغنام_مرضعات")
    if prod == "حامل_أخير":
        return AnimalRequirement(10.5, 13.5, 62, 32, 20, 3.8, 8, 0.60, 0.35,
            "نعاج حامل (4-5 شهر)", "تغذية جنين", "أغنام_مرضعات")
    if prod == "حامل_متوسط":
        return AnimalRequirement(8.5, 11, 55, 38, 24, 3.4, 8, 0.50, 0.30,
            "نعاج حامل (1-3 شهر)", "نمو جنيني", "أغنام_مرضعات")
    return AnimalRequirement(7.2, 9.5, 48, 45, 28, 3, 8.5, 0.42, 0.26,
        "نعاج صيانة", "بدون إنتاج", "أغنام_مرضعات")


def req_goat(prod, is_male=True, milk=2.0):
    if is_male:
        if prod == "تسمين_جديان":
            return AnimalRequirement(11, 14, 62, 30, 19, 3.8, 8, 0.62, 0.34,
                "تسمين جديان", "نمو سريع", "ماعز_تسمين")
        return AnimalRequirement(9, 11.5, 57, 36, 22, 3.5, 8, 0.55, 0.30,
            "تيوس تسمين", "تسمين نهائي", "ماعز_تسمين")
    if prod == "حلابة_عالي":
        dp = 11.5 + milk*0.45
        return AnimalRequirement(round(dp,2), round(dp/0.70,2),
            round(58+milk*0.45,1), 29, 18, 4.5, 8.5,
            round(0.60+milk*0.008,3), round(0.35+milk*0.004,3),
            f"عنزات حلابة عالي ({milk} كجم)", "إدرار عالي", "ماعز_حلابة")
    if prod == "حلابة_متوسط":
        dp = 10.0 + milk*0.35
        return AnimalRequirement(round(dp,2), round(dp/0.72,2),
            round(55+milk*0.40,1), 32, 20, 4, 8.5,
            round(0.55+milk*0.006,3), round(0.32+milk*0.003,3),
            f"عنزات حلابة متوسط", "إدرار متوسط", "ماعز_حلابة")
    if prod == "حامل_أخير":
        return AnimalRequirement(10, 13, 60, 33, 21, 3.8, 8, 0.60, 0.35,
            "عنزات حامل", "دفع غذائي", "ماعز_حلابة")
    return AnimalRequirement(6.8, 9, 46, 46, 28, 3, 8.5, 0.42, 0.26,
        "عنزات صيانة", "بدون إنتاج", "ماعز_حلابة")


def req_camel(prod, weight=400.0, milk=5.0):
    if prod == "نمو":
        return AnimalRequirement(10.5, 13.5, 60, 38, 24, 4, 8, 0.65, 0.38,
            "إبل نمو (حوار)", f"وزن {weight} كجم", "إبل_نمو")
    if prod == "تسمين":
        return AnimalRequirement(9.5, 12, 65, 35, 22, 4.5, 7.5, 0.60, 0.35,
            "إبل تسمين", f"وزن {weight} كجم", "إبل_تسمين")
    if prod == "حليب":
        dp = 12 + milk*0.25
        return AnimalRequirement(round(dp,2), round(dp/0.70,2),
            round(62+milk*0.40,1), 32, 20, 5, 8.5,
            round(0.70+milk*0.006,3), round(0.40+milk*0.003,3),
            f"إبل حلابة ({milk} لتر)", "دهن الحليب عالي", "إبل_حليب")
    if prod == "سباق":
        return AnimalRequirement(14, 17, 72, 28, 17, 6, 9, 0.85, 0.50,
            "إبل سباق (هجن)", "طاقة عالية", "إبل_سباق")
    return AnimalRequirement(7, 9, 48, 48, 30, 3.5, 9, 0.42, 0.26,
        "إبل صيانة", f"وزن {weight} كجم", "إبل_حليب")


def req_horse(prod):
    if prod == "رياضة_مكثف":
        return AnimalRequirement(10.5, 13.5, 70, 30, 18, 7, 7.5, 0.70, 0.40,
            "خيول رياضة مكثف", "جهد عالي + دهون عالية", "خيول_رياضة_مكثف")
    if prod == "رياضة_عادي":
        return AnimalRequirement(9, 11.5, 63, 36, 22, 5, 7.5, 0.55, 0.32,
            "خيول رياضة عادي", "نشاط متوسط", "خيول_رياضة_عادي")
    if prod == "نمو_أمهار":
        return AnimalRequirement(12, 15, 65, 30, 18, 5, 8, 0.75, 0.42,
            "أمهار نمو", "نمو هيكلي", "خيول_نمو")
    if prod == "مرضعات":
        return AnimalRequirement(12.5, 16, 68, 32, 20, 5.5, 8, 0.80, 0.45,
            "فرسات مرضعات", "إنتاج حليب مرتفع", "خيول_مرضعات")
    return AnimalRequirement(7.2, 9.5, 53, 46, 29, 3.5, 8, 0.45, 0.28,
        "خيول صيانة", "بدون جهد", "خيول_رياضة_عادي")


def req_poultry(strain, age=1):
    if strain == "لاحم":
        if age <= 1:
            return AnimalRequirement(20, 23, 76, 8, 4, 5, 6.5, 1.00, 0.50,
                "بادي لاحم (0-1 أسبوع)", "3000 kcal/kg", "دواجن_بادي")
        if age <= 3:
            return AnimalRequirement(18.5, 21, 74, 9, 5, 5, 6, 0.90, 0.45,
                "نامي لاحم (2-3 أسابيع)", "3100 kcal/kg", "دواجن_نامي")
        if age <= 5:
            return AnimalRequirement(17, 19.5, 75, 10, 5.5, 4.5, 6, 0.87, 0.43,
                "ناهي لاحم (4-5 أسابيع)", "3150 kcal/kg", "دواجن_ناهي")
        return AnimalRequirement(16.5, 19, 75, 10, 5.5, 4.5, 6, 0.85, 0.42,
            "ناهي لاحم (6+)", "3200 kcal/kg", "دواجن_ناهي")
    else:
        if age <= 6:
            return AnimalRequirement(17, 20, 72, 10, 5.5, 4, 7, 1.00, 0.50,
                "بادي بياض", "تحضير للبيض", "دواجن_بياض")
        if age <= 18:
            return AnimalRequirement(14.5, 17, 70, 12, 6.5, 4, 9, 1.50, 0.45,
                "نامي بياض", "نمو هيكلي", "دواجن_بياض")
        return AnimalRequirement(15.5, 18, 72, 11, 6, 4.2, 11.5, 3.80, 0.45,
            "بياض إنتاجي", "إنتاج بيض تجاري", "دواجن_بياض")


def req_quail(strain, age=1):
    if strain == "بياض":
        return AnimalRequirement(15, 18, 68, 11, 5.5, 4.5, 9, 2.50, 0.45,
            "سمان بياض", "إنتاج بيض", "سمان_بياض")
    if age <= 2:
        return AnimalRequirement(20.5, 24, 74, 8, 4, 5.5, 6.5, 1.00, 0.55,
            "سمان بادي", "نمو سريع", "سمان_بادي")
    if age <= 4:
        return AnimalRequirement(18.5, 22, 72, 9, 4.5, 5, 6, 0.90, 0.50,
            "سمان نامي", "نمو متوسط", "سمان_بادي")
    return AnimalRequirement(17, 20, 70, 10, 5, 4.5, 6, 0.85, 0.45,
        "سمان ناهي", "تسمين نهائي", "سمان_بادي")


def req_fish(species, stage):
    if "زريعة" in stage or "بادئ" in stage:
        return AnimalRequirement(32, 40, 72, 8, 4, 10, 11, 1.50, 0.90,
            f"{species} — بادئ", "بروتين عالٍ جداً", "أسماك_بادئ")
    if "نمو" in stage:
        return AnimalRequirement(25, 32, 70, 12, 6, 8, 9, 1.00, 0.70,
            f"{species} — نمو", "بروتين متوسط", "أسماك_نمو")
    return AnimalRequirement(22, 28, 68, 13, 7, 8, 9.5, 0.90, 0.65,
        f"{species} — تسمين", "تركيز طاقة", "أسماك_تسمين")


def req_to_standard(req):
    return {"CP": req.CP, "DP": req.DP, "SE": req.SE, "NDF": req.NDF,
            "ADF": req.ADF, "EE": req.EE, "ASH": req.ASH, "Ca": req.Ca, "P": req.P}


# ═════════════════════════════════════════════════════════════════════════════
# [6] حسابات غذائية
# ═════════════════════════════════════════════════════════════════════════════

def compute_nutrients(formula):
    totals = {k: 0.0 for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]}
    for ing, pct in formula.items():
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat:
                d, f = cat[ing], pct/100.0
                totals["CP"] += f*d.get("CP",0)
                totals["DP"] += f*d.get("CP",0)*d.get("DC",0)
                totals["SE"] += f*d.get("SE",0)
                totals["NDF"] += f*d.get("NDF",0)
                totals["ADF"] += f*d.get("ADF",0)
                totals["EE"] += f*d.get("EE",0)
                totals["ASH"] += f*d.get("ASH",0)
                totals["Ca"] += f*d.get("Ca",0)
                totals["P"] += f*d.get("P",0)
                break
    return totals


def total_oil(formula):
    oils = set(get_oil_ingredients().keys())
    return sum(p for i, p in formula.items() if i in oils)


def evaluate_diff(pct):
    a = abs(pct)
    if a <= 0.5:  return {"label":"🎯 مطابق تماماً","color":"#0d5302","bg":"#c8e6c9","score":100}
    if a <= 2.0:  return {"label":"🌟 ممتاز","color":"#1b5e20","bg":"#dcedc8","score":95}
    if a <= 5.0:  return {"label":"✅ جيد جداً","color":"#2e7d32","bg":"#e8f5e9","score":85}
    if a <= 10.0: return {"label":"🟢 جيد","color":"#558b2f","bg":"#f1f8e9","score":75}
    if a <= 15.0: return {"label":"⭐ مقبول","color":"#f9a825","bg":"#fff8e1","score":65}
    if a <= 25.0: return {"label":"⚠️ مقبول بتحفظ","color":"#ef6c00","bg":"#fff3e0","score":50}
    if a <= 40.0: return {"label":"🟠 ضعيف","color":"#e65100","bg":"#ffe0b2","score":35}
    return {"label":"❌ غير مطابق","color":"#c62828","bg":"#ffebee","score":20}


def overall_rating(rows):
    if not rows: return {"label":"غير محدد","color":"#666","score":0}
    avg = sum(r.get("score",50) for r in rows)/len(rows)
    if avg >= 95: return {"label":"🏆 خلطة ممتازة","color":"#1b5e20","score":avg}
    if avg >= 85: return {"label":"🌟 جيدة جداً","color":"#2e7d32","score":avg}
    if avg >= 70: return {"label":"✅ جيدة","color":"#558b2f","score":avg}
    if avg >= 55: return {"label":"⭐ مقبولة","color":"#f9a825","score":avg}
    return {"label":"⚠️ تحتاج تحسين","color":"#e65100","score":avg}


# ═════════════════════════════════════════════════════════════════════════════
# [7] محرك التركيب الذكي
# ═════════════════════════════════════════════════════════════════════════════

def auto_formulate_smart(available, prices, standard, oil_key, tolerance=0.3,
                          max_iter=50):
    if not SCIPY:
        return {"success": False, "message": "scipy غير مثبتة"}

    ing_data = {}
    for ing in available:
        for cat in BIG_FEEDS_LIBRARY.values():
            if ing in cat:
                ing_data[ing] = cat[ing]; break
    valid = [i for i in available if i in ing_data]
    if len(valid) < 3:
        return {"success": False, "message": "اختر 3 مكونات على الأقل"}

    n = len(valid)
    c = [prices.get(i, 300.0) for i in valid]

    rows = {k: [ing_data[i].get(k, 0) for i in valid]
            for k in ["CP","SE","NDF","ADF","EE","ASH","Ca","P"]}
    rows["DP"] = [ing_data[i].get("CP",0)*ing_data[i].get("DC",0) for i in valid]

    targets = {k: standard.get(k, 0) for k in ["DP","SE","NDF","ADF","Ca","P"]}
    oil_std = get_oil_standard(oil_key)
    oil_max = oil_std["max"]

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
        elif "سرسة" in i: bounds.append((0.0, 8.0))
        elif "تبن" in i or "قش" in i: bounds.append((0.0, 25.0))
        else: bounds.append((0.0, 100.0))

    oil_ind = [1.0 if i in get_oil_ingredients() else 0.0 for i in valid]
    has_oils = sum(oil_ind) > 0

    best, best_score = None, float('inf')
    cur = {k: targets[k] for k in ["DP","SE","NDF","ADF"]}
    log = []

    for it in range(max_iter):
        A_eq = [[1.0]*n, rows["DP"], rows["Ca"], rows["P"]]
        b_eq = [100.0, cur["DP"]*100, targets["Ca"]*100, targets["P"]*100]
        A_ub = [[-x for x in rows["SE"]], rows["NDF"], rows["ADF"]]
        b_ub = [-cur["SE"]*100, cur["NDF"]*1.10*100, cur["ADF"]*1.10*100]
        if has_oils:
            A_ub.append(oil_ind); b_ub.append(oil_max*100)

        try:
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method='highs',
                          options={'presolve': True, 'time_limit': 15})
        except Exception:
            res = type('obj', (), {'success': False})()

        if not res.success:
            A_eq = [[1.0]*n, rows["DP"], rows["Ca"]]
            b_eq = [100.0, cur["DP"]*100, targets["Ca"]*100]
            try:
                res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                              bounds=bounds, method='highs')
            except Exception:
                res = type('obj', (), {'success': False})()

        if not res.success:
            cur["NDF"] *= 1.05; cur["ADF"] *= 1.05
            log.append(f"تكرار {it+1}: تخفيف"); continue

        formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
        actual = compute_nutrients(formula)
        tot_oil = total_oil(formula)

        errs = {k: abs(actual.get(k,0)-targets.get(k,0))/targets.get(k,1)
                if targets.get(k,0) > 0 else 0
                for k in ["DP","SE","NDF","ADF","Ca","P"]}
        weights = {"DP":5,"SE":3,"NDF":1.5,"ADF":1,"Ca":1,"P":1}
        score = sum(errs[k]*weights[k] for k in errs)

        log.append(f"تكرار {it+1}: DP={actual['DP']:.2f} SE={actual['SE']:.2f} "
                   f"EE={actual['EE']:.2f}")

        if score < best_score:
            best_score = score
            best = {"success": True, "formula": formula, "cost": res.fun/100.0,
                    "actual": actual, "dp_error": abs(actual["DP"]-targets["DP"]),
                    "se_error": abs(actual["SE"]-targets["SE"]),
                    "ndf_error": abs(actual["NDF"]-targets["NDF"]),
                    "adf_error": abs(actual["ADF"]-targets["ADF"]),
                    "ca_error": abs(actual.get("Ca",0)-targets["Ca"]),
                    "p_error": abs(actual.get("P",0)-targets["P"]),
                    "total_oil": tot_oil, "oil_std": oil_std,
                    "iterations": it+1, "log": log[-10:], "targets": targets}

        if (errs.get("DP",1)*100 <= tolerance and
            errs.get("SE",1)*100 <= tolerance*2 and
            errs.get("NDF",1)*100 <= tolerance*5 and
            errs.get("Ca",1)*100 <= tolerance*15):
            log.append(f"✅ مطابقة كاملة في التكرار {it+1}")
            best["perfect_match"] = True; break

        cur["DP"] += (targets["DP"]-actual["DP"])*0.25
        cur["SE"] += (targets["SE"]-actual["SE"])*0.20
        cur["NDF"] += (targets["NDF"]-actual["NDF"])*0.15
        cur["ADF"] += (targets["ADF"]-actual["ADF"])*0.15
        cur["DP"] = max(5, min(40, cur["DP"]))
        cur["SE"] = max(10, min(90, cur["SE"]))
        cur["NDF"] = max(5, min(70, cur["NDF"]))
        cur["ADF"] = max(3, min(50, cur["ADF"]))

    if best:
        best["log"] = log
        return best
    return {"success": False, "message": "تعذر حل دقيق"}


def auto_add_salts(animal, req=None):
    salts = {"مضاد سموم فطرية": 0.20, "ملح الطعام": 0.50}
    if animal in ["أغنام","ماعز","أبقار","إبل"]:
        salts["بيكربونات الصوديوم"] = 0.75
    if animal in ["دواجن","سمان"]:
        salts["الحجر الجيري"] = 8.0 if (req and req.Ca > 2.0) else 1.5
        salts["فوسفات ثنائي الكالسيوم"] = 1.5
        salts["بريمكس تسمين دواجن"] = 0.30
    elif animal == "أسماك":
        salts["الحجر الجيري"] = 1.0
        salts["فوسفات ثنائي الكالسيوم"] = 1.5
        salts["بريمكس أسماك"] = 0.30
    elif animal == "خيول":
        salts["الحجر الجيري"] = 1.5
        salts["فوسفات ثنائي الكالسيوم"] = 1.5
        salts["بريمكس خيول"] = 0.30
    elif animal == "إبل":
        salts["الحجر الجيري"] = 2.0
        salts["فوسفات ثنائي الكالسيوم"] = 1.5
        salts["بريمكس إبل"] = 0.30
    else:
        salts["الحجر الجيري"] = 2.0
        salts["فوسفات ثنائي الكالسيوم"] = 1.5
        salts["بريمكس مجترات"] = 0.30
    return salts


# ═════════════════════════════════════════════════════════════════════════════
# [8] بدائل الحليب
# ═════════════════════════════════════════════════════════════════════════════

MILK_STANDARDS = {
    "عجول (Calves)":      {"CP":24,"Fat":24,"Lactose":45,"Lysine":2.1,"Ca":0.75,"P":0.70,"notes":"عمر 1-6 أسابيع"},
    "حملان (Lambs)":      {"CP":24,"Fat":24,"Lactose":40,"Lysine":2.1,"Ca":0.80,"P":0.70,"notes":"≥24% دهن"},
    "جديان (Goat Kids)":  {"CP":24,"Fat":24,"Lactose":42,"Lysine":2.1,"Ca":0.80,"P":0.70,"notes":"بديل الجديان"},
    "إبل (Camel Calves)": {"CP":26,"Fat":28,"Lactose":38,"Lysine":2.3,"Ca":0.85,"P":0.75,"notes":"بروتين ودهن أعلى"},
    "أمهار (Foals)":      {"CP":22,"Fat":20,"Lactose":45,"Lysine":1.9,"Ca":0.90,"P":0.80,"notes":"توازن للخيول"},
}

MILK_INGREDIENTS = {
    "حليب مجفف منزوع الدسم": {"CP":34,"Fat":1,"Lactose":52,"price":3200},
    "حليب مجفف كامل الدسم": {"CP":26,"Fat":28,"Lactose":38,"price":3800},
    "شرش حليب مجفف": {"CP":12,"Fat":1.5,"Lactose":75,"price":1800},
    "بروتين شرش WPC 80%": {"CP":80,"Fat":5,"Lactose":8,"price":8500},
    "كازين": {"CP":85,"Fat":2,"Lactose":2,"price":9000},
    "مركز بروتين صويا": {"CP":66,"Fat":1,"Lactose":0,"price":2800},
    "زيت جوز الهند": {"CP":0,"Fat":100,"Lactose":0,"price":2200},
    "زيت النخيل": {"CP":0,"Fat":100,"Lactose":0,"price":1200},
    "مالتودكسترين": {"CP":0,"Fat":0,"Lactose":0,"price":900},
    "لاكتوز نقي": {"CP":0,"Fat":0,"Lactose":100,"price":1400},
    "ليسين L-Lysine": {"CP":94,"Fat":0,"Lactose":0,"price":4200},
    "بريمكس فيتامينات": {"CP":0,"Fat":0,"Lactose":0,"price":6500},
    "كالسيوم كربونات": {"CP":0,"Fat":0,"Lactose":0,"price":200},
    "فوسفات ثنائي الكالسيوم": {"CP":0,"Fat":0,"Lactose":0,"price":1100},
    "ملح طعام": {"CP":0,"Fat":0,"Lactose":0,"price":150},
}


def formulate_milk(animal, volume=100.0, selected=None):
    if not SCIPY:
        return {"success": False, "message": "scipy غير مثبتة"}
    std = MILK_STANDARDS.get(animal)
    if not std:
        return {"success": False, "message": "غير مدعوم"}
    valid = [i for i in (selected or list(MILK_INGREDIENTS.keys()))
             if i in MILK_INGREDIENTS]
    if len(valid) < 3:
        return {"success": False, "message": "اختر 3 مكونات"}
    n = len(valid)
    c = [MILK_INGREDIENTS[i]["price"] for i in valid]
    A_eq = [[1.0]*n,
            [MILK_INGREDIENTS[i]["CP"] for i in valid],
            [MILK_INGREDIENTS[i]["Fat"] for i in valid]]
    b_eq = [100.0, std["CP"]*100, std["Fat"]*100]
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=[(0,100)]*n, method='highs')
    if not res.success:
        return {"success": False, "message": "تعذر التركيب"}
    formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
    actual = {"CP":0,"Fat":0,"Lactose":0}
    for ing, pct in formula.items():
        d = MILK_INGREDIENTS[ing]
        for k in actual: actual[k] += pct/100.0*d[k]
    return {"success": True, "formula": formula,
            "cost_per_kg": res.fun/10000.0, "standard": std, "actual": actual}


# ═════════════════════════════════════════════════════════════════════════════
# [9] OCR المختبر الذكي
# ═════════════════════════════════════════════════════════════════════════════

def match_ingredient(text):
    if not text: return None
    tl = text.strip().lower()
    for cat in BIG_FEEDS_LIBRARY.values():
        for name in cat:
            if name.lower() in tl or tl in name.lower(): return name
    kw = {"ذرة":"ذرة صفراء","صويا":"كسب فول صويا 44%","شعير":"شعير مطحون",
          "قمح":"قمح محلي","سورجم":"سورجم (فتريتة)","نخالة":"نخالة قمح (ردة)",
          "فول سوداني":"أمباز الفول السوداني","قطن":"كسب بذور القطن",
          "عباد":"كسب عباد الشمس 36%","سمسم":"كسب السمسم",
          "جلوتين":"كسب جلوتين 60%","سمك":"مسحوق أسماك 60%",
          "لحم":"مسحوق اللحم والعظم","دم":"مسحوق الدم",
          "ليسين":"ليسين نقي","ميثيونين":"ميثيونين نقي",
          "ملح":"ملح الطعام","حجر":"الحجر الجيري",
          "فوسفات":"فوسفات ثنائي الكالسيوم","بيكربونات":"بيكربونات الصوديوم",
          "مولاس":"مولاس قصب السكر","برسيم":"البرسيم الجاف",
          "يوريا":"يوريا علفية","زيت":"زيت فول الصويا"}
    for k, m in kw.items():
        if k in tl: return m
    return None


def ocr_extract(image_bytes):
    if not OCR:
        return {"success": False, "message": "pytesseract غير مثبتة"}
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"success": False, "message": "تعذر قراءة الصورة"}
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)
        t1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 11, 2)
        _, t2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        texts = []
        for t in [t1, t2, gray]:
            try:
                txt = pytesseract.image_to_string(t, lang='ara+eng',
                                                  config='--oem 3 --psm 6')
                if txt.strip(): texts.append(txt)
            except Exception:
                continue
        if not texts:
            return {"success": False, "message": "لم يتم استخراج نص"}
        full = "\n".join(texts)
        ingredients = {}
        for line in full.split('\n'):
            line = line.strip()
            if len(line) < 3: continue
            for pat in [r'([\u0600-\u06FFa-zA-Z\s\(\)%]+?)[\s:\-=]+(\d+\.?\d*)\s*%',
                        r'([\u0600-\u06FFa-zA-Z\s\(\)%]+?)\s+(\d+\.?\d*)\s*%']:
                m = re.search(pat, line)
                if m:
                    name, val = m.group(1).strip(), float(m.group(2))
                    if 0.1 < val <= 100 and len(name) > 2:
                        matched = match_ingredient(name)
                        if matched:
                            ingredients[matched] = val; break
        return {"success": True, "ingredients": ingredients,
                "raw_text": full, "count": len(ingredients)}
    except Exception as e:
        return {"success": False, "message": f"خطأ: {str(e)}"}


# ═════════════════════════════════════════════════════════════════════════════
# [10] رسوم PDF البيانية
# ═════════════════════════════════════════════════════════════════════════════

def chart_bar(standard, actual):
    if not MPL: return None
    try:
        nutrients = [n for n in ["CP","DP","SE","NDF","ADF","EE","ASH"] if n in standard]
        if not nutrients: return None
        sv = [standard[n] for n in nutrients]
        av = [actual.get(n, 0) for n in nutrients]
        fig, ax = plt.subplots(figsize=(9, 4.5))
        x = np.arange(len(nutrients)); w = 0.35
        b1 = ax.bar(x-w/2, sv, w, label='المعيار', color='#1976d2',
                    edgecolor='#0d47a1', linewidth=1.5)
        b2 = ax.bar(x+w/2, av, w, label='المحسوب', color='#43a047',
                    edgecolor='#1b5e20', linewidth=1.5)
        for b in list(b1)+list(b2):
            h = b.get_height()
            ax.text(b.get_x()+b.get_width()/2, h, f'{h:.1f}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        ax.set_xlabel('العنصر الغذائي', fontsize=11, fontweight='bold')
        ax.set_ylabel('القيمة', fontsize=11, fontweight='bold')
        ax.set_title('مقارنة العناصر الغذائية', fontsize=13,
                     fontweight='bold', color='#1b5e20')
        ax.set_xticks(x); ax.set_xticklabels(nutrients, fontsize=10)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception:
        return None


def chart_pie(formula):
    if not MPL or len(formula) < 2: return None
    try:
        colors = ['#e53935','#8e24aa','#3949ab','#1e88e5','#00897b',
                  '#43a047','#7cb342','#fdd835','#fb8c00','#6d4c41',
                  '#c62828','#6a1b9a','#283593','#0277bd','#00695c']
        names, vals = list(formula.keys()), list(formula.values())
        fig, ax = plt.subplots(figsize=(8, 5))
        w, t, at = ax.pie(vals, autopct='%1.1f%%', colors=colors[:len(names)],
                           startangle=90, pctdistance=0.75,
                           wedgeprops=dict(edgecolor='white', linewidth=2))
        for x in at: x.set_color('white'); x.set_fontweight('bold'); x.set_fontsize(9)
        ax.legend(names, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
                  fontsize=9, title="المكونات")
        ax.set_title('توزيع المكونات', fontsize=13, fontweight='bold',
                     color='#1b5e20')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception:
        return None


def chart_radar(standard, actual):
    if not MPL: return None
    try:
        nutrients = [n for n in ["CP","DP","SE","NDF","ADF","EE","Ca","P"]
                     if n in standard and standard[n] > 0]
        if len(nutrients) < 3: return None
        std_norm = [100.0]*len(nutrients)
        act_norm = [(actual.get(n,0)/standard[n])*100 for n in nutrients]
        angles = np.linspace(0, 2*np.pi, len(nutrients), endpoint=False).tolist()
        std_norm += std_norm[:1]; act_norm += act_norm[:1]; angles += angles[:1]
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, std_norm, 'o-', linewidth=2.5, color='#1976d2',
                label='المعيار (100%)')
        ax.fill(angles, std_norm, alpha=0.15, color='#1976d2')
        ax.plot(angles, act_norm, 'o-', linewidth=2.5, color='#43a047',
                label='المحسوب')
        ax.fill(angles, act_norm, alpha=0.25, color='#43a047')
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(nutrients, fontsize=10)
        ax.set_ylim(0, max(max(std_norm), max(act_norm))*1.2)
        ax.set_title('المقارنة الشاملة %', fontsize=12, fontweight='bold',
                     color='#1b5e20', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
        ax.grid(True, alpha=0.3)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception:
        return None


def chart_gauge(score):
    if not MPL: return None
    try:
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect='equal'))
        colors_g = ['#c62828','#ef6c00','#f9a825','#7cb342','#43a047','#1b5e20']
        for i, cc in enumerate(colors_g):
            theta1 = 180 - i*30; theta2 = 180 - (i+1)*30
            ax.add_patch(Wedge((0, 0), 1, theta2, theta1, width=0.3,
                               facecolor=cc, edgecolor='white', linewidth=2))
        angle = 180 - (score/100)*180
        rad = np.radians(angle)
        ax.plot([0, 0.85*np.cos(rad)], [0, 0.85*np.sin(rad)],
                color='#1a1a1a', linewidth=3, zorder=10)
        ax.add_patch(Circle((0, 0), 0.08, color='#1a1a1a', zorder=11))
        ax.text(0, -0.25, f'{score:.0f}%', ha='center', fontsize=20,
                fontweight='bold', color='#1b5e20')
        ax.text(0, -0.5, 'التقييم العام', ha='center', fontsize=11, color='#666')
        ax.set_xlim(-1.2, 1.2); ax.set_ylim(-0.7, 1.2); ax.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception:
        return None


# ═════════════════════════════════════════════════════════════════════════════
# [11] مولّد PDF الرسمي
# ═════════════════════════════════════════════════════════════════════════════

class PDFGenerator:
    def __init__(self):
        self.font_name = font_mgr.font_name
        self.font_bold = font_mgr.font_bold
        self.logo_path = next((p for p in LOGO_OPTIONS + PHOTO_OPTIONS
                                if os.path.exists(p)), None)

    def _draw_page(self, c, doc):
        c.saveState()
        w, h = doc.pagesize
        # علامة مائية
        c.setFillColor(HexColor('#e8f5e9'))
        c.setFont(self.font_name, 60)
        try: c.setFillAlpha(0.07)
        except Exception: pass
        c.saveState(); c.translate(w/2, h/2); c.rotate(45)
        c.drawCentredString(0, 0, ar("تاور نولجي")); c.restoreState()
        try: c.setFillAlpha(1)
        except Exception: pass
        # ترويسة
        c.setFillColor(HexColor('#1b5e20'))
        c.rect(0, h-90, w, 90, fill=1, stroke=0)
        c.setFillColor(HexColor('#d4af37'))
        c.rect(0, h-95, w, 5, fill=1, stroke=0)
        try:
            if self.logo_path:
                c.drawImage(self.logo_path, 30, h-78, width=60, height=60,
                            preserveAspectRatio=True, anchor='sw', mask='auto')
        except Exception: pass
        c.setFillColor(white); c.setFont(self.font_name, 22)
        c.drawCentredString(w/2, h-38, ar("تاور نولجي Tawor Nology"))
        c.setFont(self.font_name, 12); c.setFillColor(HexColor('#e8f5e9'))
        c.drawCentredString(w/2, h-58, ar("للإنتاج الحيواني وتغذية الحيوان"))
        c.setFont(self.font_name, 10); c.setFillColor(HexColor('#d4af37'))
        c.drawCentredString(w/2, h-76, ar(f"إشراف: {SUPERVISOR} — {SUPERVISOR_TITLE}"))
        # دعاء
        c.setFillColor(HexColor('#1b5e20')); c.rect(0, 42, w, 42, fill=1, stroke=0)
        c.setFillColor(HexColor('#d4af37')); c.rect(0, 84, w, 3, fill=1, stroke=0)
        c.setFillColor(HexColor('#ffeb3b')); c.setFont(self.font_name, 10)
        c.drawCentredString(w/2, 68, ar(f"🤲 {DUA_SHORT} 🤲"))
        c.setFillColor(HexColor('#c8e6c9')); c.setFont(self.font_name, 8)
        c.drawCentredString(w/2, 52, ar("اللهم اجعل قبرهما روضة من رياض الجنة"))
        # تذييل
        c.setFillColor(HexColor('#1b5e20')); c.rect(0, 0, w, 42, fill=1, stroke=0)
        c.setFillColor(white); c.setFont(self.font_name, 8)
        c.drawCentredString(w/2, 27, ar("تاور نولجي Tawor Nology © 2026"))
        c.setFont(self.font_name, 7)
        c.drawCentredString(w/2, 12, ar(f"صفحة {c.getPageNumber()} | جميع الحقوق محفوظة"))
        # QR
        try:
            qr = qrcode.QRCode(version=1, box_size=3, border=1)
            qr.add_data(PLATFORM_URL); qr.make(fit=True)
            qi = qr.make_image(fill_color="#1b5e20", back_color="white")
            buf = io.BytesIO(); qi.save(buf, format="PNG"); buf.seek(0)
            c.drawImage(RLImage(buf), w/2-20, 46, width=40, height=40)
        except Exception: pass
        # ختم
        sx, sy = w-105, 145
        c.setStrokeColor(HexColor('#c62828')); c.setLineWidth(3)
        c.circle(sx, sy, 70, stroke=1, fill=0)
        c.setLineWidth(1.5); c.circle(sx, sy, 62, stroke=1, fill=0)
        c.setLineWidth(0.6); c.circle(sx, sy, 56, stroke=1, fill=0)
        c.setFillColor(HexColor('#c62828')); c.setFont(self.font_name, 9)
        c.drawCentredString(sx, sy+40, ar("تاور نولجي"))
        c.drawCentredString(sx, sy+28, ar("Tawor Nology"))
        c.setFont(self.font_name, 7.5)
        c.drawCentredString(sx, sy+10, ar("م. عبدالقادر"))
        c.drawCentredString(sx, sy-1, ar("إسماعيل تاور"))
        c.setFont(self.font_name, 6)
        c.drawCentredString(sx, sy-17, ar("اختصاصي تغذية الحيوان"))
        c.drawCentredString(sx, sy-30, ar("معتمد رسمياً"))
        c.drawCentredString(sx, sy-42, ar("© 2026"))
        c.restoreState()

    def _cmp_table(self, standard, calc):
        labels = {"CP":"بروتين خام CP","DP":"بروتين مهضوم DP",
                  "SE":"معادل النشاء SE","NDF":"ألياف NDF","ADF":"ألياف ADF",
                  "EE":"دهن EE","ASH":"رماد ASH","Ca":"كالسيوم Ca","P":"فسفور P"}
        data = [[ar(x) for x in ["العنصر","المعيار","المحسوب","الفرق","% الفرق","التقييم"]]]
        cmds = [('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),
                ('TEXTCOLOR',(0,0),(-1,0),white),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                ('FONTNAME',(0,0),(-1,-1),self.font_name),
                ('FONTSIZE',(0,0),(-1,-1),9),
                ('GRID',(0,0),(-1,-1),1,HexColor('#9e9e9e')),
                ('BOTTOMPADDING',(0,0),(-1,-1),7),
                ('TOPPADDING',(0,0),(-1,-1),7)]
        r = 1
        for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
            if k not in standard: continue
            sv, cv = standard[k], calc.get(k, 0.0)
            diff = cv - sv
            pct = (diff/sv*100) if sv else 0
            ev = evaluate_diff(pct)
            data.append([ar(labels.get(k,k)), f"{sv:.2f}", f"{cv:.2f}",
                         f"{diff:+.3f}", f"{pct:+.2f}%", ar(ev["label"])])
            cmds.append(('BACKGROUND',(0,r),(-1,r),HexColor(ev["bg"])))
            cmds.append(('TEXTCOLOR',(5,r),(5,r),HexColor(ev["color"])))
            r += 1
        t = Table(data, colWidths=[100,70,70,70,70,105])
        t.setStyle(TableStyle(cmds)); return t

    def _oil_table(self, formula, oil_key):
        oils = get_oil_ingredients()
        oil_rows = [(ing, pct) for ing, pct in formula.items() if ing in oils]
        if not oil_rows: return None
        std = get_oil_standard(oil_key); tot = sum(p for _, p in oil_rows)
        data = [[ar(x) for x in ["الزيت","النسبة %","kcal/kg تقديري"]]]
        for ing, pct in oil_rows:
            data.append([ar(ing), f"{pct:.2f}%", f"{pct*90:.0f}"])
        data.append([ar("الإجمالي"), f"{tot:.2f}%", f"{tot*90:.0f}"])
        cmds = [('BACKGROUND',(0,0),(-1,0),HexColor('#e65100')),
                ('TEXTCOLOR',(0,0),(-1,0),white),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('FONTNAME',(0,0),(-1,-1),self.font_name),
                ('FONTSIZE',(0,0),(-1,-1),10),
                ('GRID',(0,0),(-1,-1),1,HexColor('#bf360c')),
                ('BACKGROUND',(0,-1),(-1,-1),HexColor('#ffe0b2')),
                ('TEXTCOLOR',(0,-1),(-1,-1),HexColor('#bf360c')),
                ('TOPPADDING',(0,0),(-1,-1),6),
                ('BOTTOMPADDING',(0,0),(-1,-1),6)]
        t = Table(data, colWidths=[250,100,135])
        t.setStyle(TableStyle(cmds))
        return t, tot, std

    def generate(self, formula, req, animal, cost, city, local_cost, local_sym,
                  requester="", basis="DP", oil_key="", charts=True):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
            rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []

        def P(txt, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(ar(txt),
                ParagraphStyle('s', fontName=self.font_name, fontSize=size,
                    alignment=align, textColor=HexColor(color),
                    spaceAfter=6, leading=size*1.6))

        story.append(P("تقرير فني رسمي — تركيب علفة", 20, TA_CENTER, '#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
                                color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))

        client = [
            [ar("👤 اسم طالب الخدمة:"), ar(requester or "........................")],
            [ar("📍 الموقع:"), ar(city)],
            [ar("🐾 الفصيل:"), ar(f"{animal} — {req.name_ar}")],
            [ar("🧬 أساس الحساب:"),
             ar("بروتين مهضوم DP" if basis == "DP" else "بروتين خام CP")],
            [ar("📅 التاريخ:"), datetime.now().strftime('%Y-%m-%d | %H:%M')],
        ]
        ct = Table(client, colWidths=[150, 340])
        ct.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(0,-1),HexColor('#e8f5e9')),
            ('BACKGROUND',(1,0),(1,-1),HexColor('#fafafa')),
            ('BOX',(0,0),(-1,-1),1.5,HexColor('#2e7d32')),
            ('INNERGRID',(0,0),(-1,-1),0.6,HexColor('#c8e6c9')),
            ('ALIGN',(0,0),(-1,-1),'RIGHT'),
            ('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),11),
            ('TOPPADDING',(0,0),(-1,-1),9),
            ('BOTTOMPADDING',(0,0),(-1,-1),9)]))
        story.append(ct); story.append(Spacer(1, 15))

        sv = req_to_standard(req); cv = compute_nutrients(formula)
        scores = []
        for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
            if k in sv:
                pct = ((cv.get(k,0)-sv[k])/sv[k]*100) if sv[k] else 0
                scores.append({"score": evaluate_diff(pct)["score"]})
        overall = overall_rating(scores)

        story.append(P("📊 جدول مقارنة العناصر", 14, TA_RIGHT, '#1b5e20'))
        story.append(Spacer(1, 8))
        story.append(self._cmp_table(sv, cv)); story.append(Spacer(1, 12))

        sum_data = [[ar(x) for x in ["التقييم العام","عدد المطابقة","المتوسط"]],
                    [ar(overall["label"]),
                     f"{sum(1 for s in scores if s['score']>=85)}/{len(scores)}",
                     f"{overall['score']:.0f}%"]]
        st_tbl = Table(sum_data, colWidths=[160,165,165])
        st_tbl.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#1565c0')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('BACKGROUND',(0,1),(-1,-1),HexColor('#e3f2fd')),
            ('GRID',(0,0),(-1,-1),1,HexColor('#1976d2')),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),11),
            ('TOPPADDING',(0,0),(-1,-1),8),
            ('BOTTOMPADDING',(0,0),(-1,-1),8)]))
        story.append(st_tbl); story.append(Spacer(1, 15))

        oil_result = self._oil_table(formula, oil_key)
        if oil_result:
            oil_tbl, tot_oil, oil_std = oil_result
            story.append(P("🌰 جدول الزيوت", 14, TA_RIGHT, '#e65100'))
            story.append(Spacer(1, 8)); story.append(oil_tbl)
            story.append(Spacer(1, 8))
            if tot_oil > oil_std['max']:
                note = f"⚠️ تجاوز الحد الأقصى! ({oil_std['max']}%)"
            elif tot_oil > oil_std['optimal']*1.2:
                note = f"⚡ مرتفع قليلاً — المثالي {oil_std['optimal']}%"
            else:
                note = f"✅ مطابق — المثالي {oil_std['optimal']}%"
            story.append(P(f"{note} | المرجع: {oil_std['source']}", 10,
                           TA_RIGHT, '#bf360c'))
            story.append(Spacer(1, 15))

        if charts:
            story.append(P("📈 الرسوم البيانية", 14, TA_RIGHT, '#1b5e20'))
            story.append(Spacer(1, 10))
            c1 = chart_bar(sv, cv)
            if c1:
                story.append(RLImage(c1, width=450, height=250))
                story.append(Spacer(1, 12))
            c2 = chart_pie(formula); c3 = chart_radar(sv, cv)
            if c2 and c3:
                row = [[RLImage(c2, width=210, height=200),
                        RLImage(c3, width=210, height=200)]]
                rt = Table(row, colWidths=[230,230])
                rt.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                                        ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
                story.append(rt); story.append(Spacer(1, 12))
            gauge = chart_gauge(overall["score"])
            if gauge:
                story.append(P("🎯 مؤشر التقييم", 12, TA_CENTER, '#1b5e20'))
                story.append(RLImage(gauge, width=200, height=200))

        story.append(PageBreak())

        story.append(P("💰 التكاليف", 14, TA_RIGHT, '#1b5e20'))
        story.append(Spacer(1, 8))
        cost_data = [[ar("البند"), ar("القيمة")],
                     [ar("التكلفة للطن (دولار)"), f"${cost:.2f}"],
                     [ar(f"التكلفة ({local_sym})"), f"{local_cost:,.2f}"],
                     [ar("البروتين المستهدف"),
                      f"{req.DP if basis == 'DP' else req.CP:.2f}%"],
                     [ar("الدهن EE"), f"{cv['EE']:.2f}%"]]
        tc = Table(cost_data, colWidths=[280,210])
        tc.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('BACKGROUND',(0,1),(-1,-1),HexColor('#f5f5f5')),
            ('GRID',(0,0),(-1,-1),1,HexColor('#2e7d32')),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),11),
            ('TOPPADDING',(0,0),(-1,-1),8),
            ('BOTTOMPADDING',(0,0),(-1,-1),8)]))
        story.append(tc); story.append(Spacer(1, 18))

        if formula:
            story.append(P("🌾 المكونات للطن", 14, TA_RIGHT, '#1b5e20'))
            story.append(Spacer(1, 8))
            ing_data = [[ar("المكون"), ar("النسبة %"), ar("كجم/طن")]]
            for ing, pct in formula.items():
                ing_data.append([ar(ing), f"{pct:.2f}%", f"{pct*10:.1f}"])
            ti = Table(ing_data, colWidths=[270,110,110])
            ti.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),
                ('TEXTCOLOR',(0,0),(-1,0),white),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('FONTNAME',(0,0),(-1,-1),self.font_name),
                ('FONTSIZE',(0,0),(-1,-1),10),
                ('GRID',(0,0),(-1,-1),1,HexColor('#bdbdbd')),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),
                 [HexColor('#ffffff'), HexColor('#f5f5f5')])]))
            story.append(ti); story.append(Spacer(1, 25))

        sign = [[ar("توقيع طالب الخدمة"), ar("توقيع المختص")],
                [ar("........................"), ar(SUPERVISOR)],
                [ar("التاريخ: ..../..../........"), ar(SUPERVISOR_TITLE)]]
        ts = Table(sign, colWidths=[245,245])
        ts.setStyle(TableStyle([
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),10),
            ('TOPPADDING',(0,0),(-1,-1),8),
            ('BOTTOMPADDING',(0,0),(-1,-1),8),
            ('BOX',(0,0),(-1,-1),1,HexColor('#bdbdbd')),
            ('INNERGRID',(0,0),(-1,-1),0.5,HexColor('#e0e0e0')),
            ('BACKGROUND',(0,0),(-1,0),HexColor('#e8f5e9'))]))
        story.append(ts)

        doc.build(story, onFirstPage=self._draw_page,
                  onLaterPages=self._draw_page)
        buffer.seek(0); return buffer.getvalue()


pdf_gen = PDFGenerator()


# ═════════════════════════════════════════════════════════════════════════════
# [12] تصدير Excel
# ═════════════════════════════════════════════════════════════════════════════

def export_excel(standard, calc, requester="", animal="", formula=None, oil_key=""):
    if not XLSX: return b""
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "مقارنة"
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
    ws['A4'] = "طالب:"; ws['A4'].font = Font(bold=True); ws['A4'].alignment = ct
    ws['B4'] = requester; ws['E4'] = "التاريخ:"; ws['E4'].font = Font(bold=True)
    ws['F4'] = datetime.now().strftime('%Y-%m-%d')
    for c, h in enumerate(["العنصر","المعيار","المحسوب","الفرق","% الفرق","التقييم"], 1):
        cell = ws.cell(row=6, column=c, value=h)
        cell.font = hf; cell.fill = hfill; cell.alignment = ct; cell.border = bd
    labels = {"CP":"بروتين خام","DP":"بروتين مهضوم","SE":"معادل النشاء",
              "NDF":"NDF","ADF":"ADF","EE":"دهن","ASH":"رماد",
              "Ca":"كالسيوم","P":"فسفور"}
    r = 7
    for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
        if k not in standard: continue
        sv, cvv = standard[k], calc.get(k, 0)
        diff = cvv - sv; pct = (diff/sv*100) if sv else 0
        ev = evaluate_diff(pct)
        for c, v in enumerate([labels[k], round(sv,2), round(cvv,2),
                                round(diff,3), round(pct,2), ev["label"]], 1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.alignment = ct; cell.border = bd
            cell.fill = PatternFill('solid', fgColor=ev["bg"].replace('#',''))
        r += 1
    if formula:
        oil_rows = [(i, p) for i, p in formula.items() if i in get_oil_ingredients()]
        if oil_rows:
            r += 2
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
            ws.cell(row=r, column=1, value="🌰 الزيوت").font = tf
            ws.cell(row=r, column=1).alignment = ct; r += 1
            for c, h in enumerate(["الزيت","النسبة %","kcal/kg","","",""], 1):
                cell = ws.cell(row=r, column=c, value=h)
                cell.font = hf; cell.fill = PatternFill('solid', fgColor='E65100')
                cell.alignment = ct; cell.border = bd
            r += 1
            for ing, pct in oil_rows:
                ws.cell(row=r, column=1, value=ing).border = bd
                ws.cell(row=r, column=2, value=round(pct,2)).border = bd
                ws.cell(row=r, column=3, value=round(pct*90,0)).border = bd
                r += 1
    for c in range(1, 7):
        ws.column_dimensions[get_column_letter(c)].width = 22
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return buf.getvalue()


# ═════════════════════════════════════════════════════════════════════════════
# [13] الأسعار والحالة
# ═════════════════════════════════════════════════════════════════════════════

EXCHANGE_RATES = {
    "السودان": {"rate":600.0,"sym":"SDG"},
    "LIBYA":   {"rate":4.80,"sym":"LYD"},
    "مصر":     {"rate":48.0,"sym":"EGP"},
    "السعودية":{"rate":3.75,"sym":"SAR"},
    "الإمارات":{"rate":3.67,"sym":"AED"},
    "دولار أمريكي": {"rate":1.0,"sym":"USD"},
}


def market_prices(country, city, state=""):
    base = {ing: 280.0 for cat in BIG_FEEDS_LIBRARY.values() for ing in cat}
    base.update({
        "ذرة صفراء":230,"ذرة بيضاء":225,"شعير مطحون":210,"سورجم (فتريتة)":195,
        "قمح محلي":240,"أمباز الفول السوداني":460,"كسب فول صويا 44%":440,
        "كسب فول صويا 48%":480,"كسب عباد الشمس 36%":310,"كسب بذور القطن":290,
        "نخالة قمح (ردة)":150,"البرسيم الجاف":170,"مولاس قصب السكر":120,
        "مسحوق أسماك 60%":850,"مركزات دواجن":650,"مركزات مواشي":600,
        "الحجر الجيري":40,"فوسفات ثنائي الكالسيوم":280,"ملح الطعام":30,
        "بيكربونات الصوديوم":340,"مضاد سموم فطرية":950,
        "بريمكس تسمين دواجن":4800,"بريمكس مجترات":4500,
        "ليسين نقي":4200,"ميثيونين نقي":5800,
        "زيت ذرة":1500,"زيت فول الصويا":1350,"زيت عباد الشمس":1300,
        "زيت بذرة القطن":1400,"زيت الكتان":1700,"زيت جوز الهند":1900,
        "زيت النخيل":1100,"زيت الكانولا":1450,"زيت السمسم":2100,
        "زيت الزيتون":3500,"زيت الأفوكادو":4200,"زيت القرطم":1800,
        "زيت الفول السوداني":2200,"شحم حيواني (Tallow)":900,
        "زيت السمك (Fish Oil)":3800,
    })
    m = 1.0
    if country == "السودان": m = 1.20 if "كردفان" in state else 1.15
    elif country == "LIBYA": m = 1.10
    elif country == "مصر": m = 1.04
    elif country == "السعودية": m = 1.08
    elif country == "الإمارات": m = 1.12
    return {k: v*m for k, v in base.items()}


ANIMAL_IMAGES = {
    "أبقار":"https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "ماعز":"https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "أغنام":"https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600",
    "خيول":"https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "إبل":"https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "دواجن":"https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
    "أسماك":"https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600",
    "سمان":"https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "عام":"https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600",
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


# الجلسة
DEFAULTS = {
    "approved": False, "user_role": None,
    "active_formula": {},
    "active_animal_img": ANIMAL_IMAGES["عام"],
    "active_stage_title": "إنتاج عام",
    "computed_ton_cost": 280.0,
    "inventory": {},
    "shared_comments": f"• مرحباً بكم في {APP_NAME}\n• {DUA_SHORT}\n",
    "broiler_farms": {},
    "livestock_prices": {
        "عجول تسمين هولشتاين ($)":1350.0,"أبقار كنانة ($)":900.0,
        "ضأن محلي ($)":180.0,"ماعز نوبي ($)":130.0,
        "إبل حاشي ($)":1200.0,"كتكوت لاحم يوم ($)":0.65,
    },
    "products_prices": {
        "كيلو لحم بقري ($)":7.50,"كيلو لحم ضأن ($)":9.00,
        "كيلو لحم إبل ($)":8.50,"كيلو لحم دجاج ($)":3.80,
        "طبق بيض 30 ($)":4.20,"لتر حليب بقر ($)":0.90,
        "لتر حليب إبل ($)":3.50,
    },
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v
if not st.session_state["inventory"]:
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing in cat:
            st.session_state["inventory"][ing] = {
                "quantity": 25.0, "min_threshold": 5.0, "unit": "طن"}


def is_owner(): return st.session_state.get("user_role") == "owner"
def is_logged_in(): return st.session_state.get("user_role") in [
    "owner", "specialist", "veterinarian", "nutritionist", "breeder", "guest"]


# ═════════════════════════════════════════════════════════════════════════════
# [14] CSS الرئيسي
# ═════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');
* { font-family: 'Cairo', 'Amiri', sans-serif; color: #1a1a1a !important; }
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 50%, #f5f7fa 100%);
    background-attachment: fixed;
}
.stApp { background: transparent; }
.main-box {
    background-color: rgba(255, 255, 255, 0.98);
    padding: 30px; border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    margin-bottom: 60px; backdrop-filter: blur(5px);
}
h1,h2,h3,h4,h5,p,span,li,div,label { color: #1a1a1a !important; }

@keyframes duaGlow {
    0%,100% { box-shadow: 0 15px 40px rgba(0,0,0,0.4),
              inset 0 0 30px rgba(212,175,55,0.2); }
    50%     { box-shadow: 0 15px 40px rgba(0,0,0,0.5),
              inset 0 0 40px rgba(212,175,55,0.4),
              0 0 80px rgba(212,175,55,0.5); }
}
@keyframes scrollDuaLR {
    0%   { transform: translateX(-100%); opacity: 0.2; }
    8%   { opacity: 1; }
    50%  { opacity: 1; }
    92%  { opacity: 1; }
    100% { transform: translateX(100%); opacity: 0.2; }
}
@keyframes glowTextDua {
    0%,100% { text-shadow: 0 0 8px #ffd700, 0 0 16px #ffd700; }
    50%     { text-shadow: 0 0 20px #ffd700, 0 0 40px #ff8c00; }
}
@keyframes pulseHeartDua {
    0%,100% { transform: scale(1); color: #ff6b6b; }
    50%     { transform: scale(1.4); color: #ff1744; }
}
@keyframes bgShiftDua {
    0%   { background-position:   0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position:   0% 50%; }
}
@keyframes floatIcon {
    0%,100% { transform: translateY(0) rotate(0); }
    50%     { transform: translateY(-12px) rotate(6deg); }
}

.dua-container {
    background: linear-gradient(90deg, #0d1b2a, #1a237e, #4a148c, #1a237e, #0d1b2a);
    background-size: 300% 300%;
    animation: bgShiftDua 14s ease infinite;
    padding: 24px 0; border-radius: 24px 24px 0 0;
    overflow: hidden; border: 3px solid #ffd700; border-bottom: none;
    box-shadow: 0 8px 40px rgba(255,215,0,0.5);
    direction: ltr; min-height: 90px;
}
.dua-track {
    display: inline-block; white-space: nowrap;
    animation: scrollDuaLR 35s linear infinite,
                glowTextDua 3s ease-in-out infinite;
    font-size: 1.75rem; font-weight: 800; color: #ffd700;
    padding: 0 30px; letter-spacing: 1.5px;
}
.dua-track .emoji-heart { display: inline-block;
    animation: pulseHeartDua 1.2s ease-in-out infinite; margin: 0 10px; }
.dua-track .gold-star  { color: #ffd700; font-size: 1.6rem; margin: 0 14px; }
.dua-track .name-highlight {
    color: #ffab40; font-weight: 900;
    background: rgba(255,215,0,0.18);
    padding: 2px 12px; border-radius: 8px;
    border: 1px solid rgba(255,215,0,0.35);
}
.dua-static {
    background: linear-gradient(90deg, #1b2a4a, #2a1b4a, #1b2a4a);
    background-size: 200% 200%;
    animation: bgShiftDua 10s ease infinite;
    padding: 14px 20px; border-radius: 0 0 20px 20px;
    text-align: center; color: #e1bee7;
    font-size: 1.15rem; font-weight: 700;
    border: 3px solid #ffd700; border-top: 1px solid rgba(255,215,0,0.35);
    direction: rtl; line-height: 1.9; margin-bottom: 20px;
}
.dua-static .name-highlight-static {
    color: #ffd700; font-weight: 900;
    background: rgba(255,215,0,0.12);
    padding: 1px 10px; border-radius: 6px;
}
.dua-static .heart-sm {
    color: #ff6b6b; font-size: 1rem; margin: 0 6px;
    display: inline-block; animation: pulseHeartDua 1.5s ease-in-out infinite;
}

.section-title {
    color: #1b5e20 !important;
    border-right: 6px solid #2e7d32;
    padding: 12px 18px; text-align: right;
    font-size: 1.5rem; font-weight: bold;
    margin-top: 30px; margin-bottom: 20px;
    background: linear-gradient(to left, rgba(46,125,50,0.15), transparent);
    border-radius: 10px;
}
.formula-item {
    background: linear-gradient(135deg, #ffffff 0%, #e8f5e9 100%);
    padding: 15px 20px; border-radius: 12px;
    margin-bottom: 10px; font-weight: bold;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    text-align: right;
}
.oil-item {
    background: linear-gradient(135deg, #fff8e1 0%, #ffe0b2 100%);
    padding: 12px 18px; border-radius: 12px;
    margin-bottom: 8px; font-weight: bold;
    color: #bf360c !important;
    border-right: 5px solid #e65100;
    box-shadow: 0 4px 15px rgba(230,81,0,0.15);
    text-align: right;
}
.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px; border-radius: 12px;
    border-right: 5px solid #2e7d32;
    margin-bottom: 20px; direction: rtl; text-align: right;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.oil-info-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 18px; border-radius: 12px;
    border-right: 5px solid #e65100;
    margin-bottom: 18px; direction: rtl; text-align: right;
    box-shadow: 0 4px 15px rgba(230,81,0,0.15);
}
.profile-img-style {
    width: 150px; height: 150px; border-radius: 50%;
    object-fit: cover; border: 4px solid #d4af37;
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    display: block; margin: 0 auto;
}
.metric-card {
    background: white; padding: 22px; border-radius: 18px;
    box-shadow: 0 6px 30px rgba(0,0,0,0.08);
    text-align: center; transition: all 0.3s ease;
    border: 1px solid rgba(46,125,50,0.1);
}
.metric-card .number { font-size: 2.2rem; font-weight: 900;
    color: #1b5e20; margin: 5px 0; }
.metric-card .label { font-size: 0.95rem; color: #666; font-weight: 600; }

.mini-signature {
    position: fixed; left: 20px; bottom: 65px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important; padding: 9px 22px;
    font-size: 0.88rem; border-radius: 25px;
    z-index: 9997; direction: rtl;
    border: 2px solid #d4af37;
    animation: duaGlow 3s ease-in-out infinite;
    font-weight: bold;
}
.mini-signature * { color: white !important; }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# [15] شريط الدعاء المتحرك
# ═════════════════════════════════════════════════════════════════════════════

def render_dua_bar():
    st.markdown("""
    <div class="dua-container">
        <div class="dua-track">
            <span class="gold-star">✦</span>
            <span class="emoji-heart">❤️</span>
            اللهم اغفر لـ <span class="name-highlight">إسماعيل تاور</span>
            و <span class="name-highlight">ابتسام</span>
            وارحمهما وأدخلهما فسيح جناتك
            <span class="emoji-heart">❤️</span>
            اللهم اجعل قبرهما روضة من رياض الجنة
            <span class="emoji-heart">❤️</span>
            اللهم ارحم موتانا وموتى المسلمين
            <span class="emoji-heart">❤️</span>
            <span class="gold-star">✦</span>
        </div>
    </div>
    <div class="dua-static">
        🕊️ <span class="name-highlight-static">اللهم اغفر لإسماعيل تاور وابتسام</span>
        <span class="heart-sm">❤️</span>
        وارحمهما وأدخلهما فسيح جناتك
        <span class="heart-sm">❤️</span>
        واجمعنا بهما في الفردوس الأعلى 🕊️
    </div>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# [16] بوابة الدخول
# ═════════════════════════════════════════════════════════════════════════════

if not st.session_state["approved"]:
    render_dua_bar()
    st.markdown('<div class="main-box" style="max-width: 780px; '
                'margin: 30px auto; direction: rtl;">', unsafe_allow_html=True)

    c1, c2 = st.columns([0.3, 0.7])
    with c1:
        if img_base64:
            st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" '
                        f'class="profile-img-style">', unsafe_allow_html=True)
        else:
            st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" '
                        f'class="profile-img-style">', unsafe_allow_html=True)
    with c2:
        st.markdown(f"<h2 style='color:#2E7D32; text-align:right;'>🌾 {APP_NAME}</h2>",
                    unsafe_allow_html=True)
        st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.1rem;'>"
                    f"{APP_TAGLINE}</p>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#c62828; text-align:right;'>"
                    f"{SUPERVISOR} — {SUPERVISOR_TITLE}</h4>",
                    unsafe_allow_html=True)

    st.markdown("<hr style='border-top: 2px solid #d4af37; margin: 25px 0;'>",
                unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#1b5e20;'>"
                "🔐 بوابة الدخول</h3>", unsafe_allow_html=True)

    login_tab1, login_tab2 = st.tabs(["🔑 كود الدخول", "👤 زائر"])

    with login_tab1:
        code_input = st.text_input("أدخل كود الدخول:", type="password", key="code_in")
        if st.button("🔓 تسجيل الدخول", type="primary", use_container_width=True):
            codes = {
                OWNER_CODE: "owner",
                SPECIALIST_CODE: "specialist",
                VET_CODE: "veterinarian",
                NUTRITIONIST_CODE: "nutritionist",
                BREEDER_CODE: "breeder",
            }
            if code_input.strip() in codes:
                st.session_state["approved"] = True
                st.session_state["user_role"] = codes[code_input.strip()]
                st.rerun()
            else:
                st.error("❌ كود غير صحيح")
        st.caption("💡 للمالك: 202687")

    with login_tab2:
        st.info("دخول مجاني للاطلاع على المنصة")
        if st.button("👥 دخول كزائر", use_container_width=True):
            st.session_state["approved"] = True
            st.session_state["user_role"] = "guest"
            st.rerun()

    st.markdown(f"<div class='dua-static'>🕊️ {DUA_FULL} 🕊️</div>",
                unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
# [17] الواجهة الرئيسية
# ═════════════════════════════════════════════════════════════════════════════

render_dua_bar()
st.markdown('<div class="main-box">', unsafe_allow_html=True)

c1, c2 = st.columns([0.7, 0.3])
with c2:
    role_label = {"owner":"المالك 👑","specialist":"المختص 👨‍🔬",
                  "veterinarian":"الطبيب البيطري 💊",
                  "nutritionist":"أخصائي التغذية 🧬",
                  "breeder":"المربي 🌾","guest":"زائر 👥"}.get(
                      st.session_state["user_role"], "مستخدم")
    st.markdown(f"<div style='text-align:left; padding:10px; background:#f5f5f5;"
                f"border-radius:10px;'>الحساب: <b>{role_label}</b></div>",
                unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k != "inventory": del st.session_state[k]
        st.session_state["approved"] = False; st.rerun()

c3, c4 = st.columns([0.3, 0.7])
with c3:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" '
                    f'class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" '
                    f'class="profile-img-style">', unsafe_allow_html=True)
with c4:
    st.markdown(f"<h1 style='color:#0d3011; text-align:right; "
                f"font-weight:900; font-size:2.3rem;'>🌾 {APP_NAME}</h1>",
                unsafe_allow_html=True)
    st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.25rem; "
                f"font-weight:600;'>{APP_TAGLINE}</p>", unsafe_allow_html=True)
    st.markdown(f"<div style='background: linear-gradient(135deg, #fff8e1, #ffe082); "
                f"padding: 12px 20px; border-radius: 12px; "
                f"border-right: 6px solid #c62828; border-left: 6px solid #c62828;'>"
                f"<h3 style='color:#b71c1c; text-align:right; margin:0; "
                f"font-weight:900;'>👨‍🔬 {SUPERVISOR}</h3>"
                f"<p style='color:#0d47a1; text-align:right; margin:5px 0 0 0; "
                f"font-weight:700;'>✨ {SUPERVISOR_TITLE}</p></div>",
                unsafe_allow_html=True)

st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# [18] التبويبات الرئيسية
# ═════════════════════════════════════════════════════════════════════════════

if is_owner():
    tabs_titles = [
        "🔬 تركيب الأعلاف", "🌰 مكتبة الزيوت", "🍼 بدائل الحليب",
        "📷 المختبر الذكي", "🐔 إدارة المزارع", "📊 البورصة",
        "🏭 المستودعات", "🧾 الفواتير", "🖨️ الديباجة", "📈 التحليلات",
        "💬 التعليقات", "📚 المراجع", "💡 المساعدة", "📖 الدليل",
    ]
else:
    tabs_titles = [
        "🔬 تركيب الأعلاف", "🌰 مكتبة الزيوت", "🍼 بدائل الحليب",
        "📷 المختبر الذكي", "📚 المراجع", "💡 المساعدة", "📖 الدليل",
    ]

tabs = st.tabs(tabs_titles)


# ═════════════════════════════════════════════════════════════════════════════
# [19] تبويب تركيب الأعلاف
# ═════════════════════════════════════════════════════════════════════════════

with tabs[0]:
    st.markdown('<div class="section-title">🌍 الموقع الجغرافي</div>',
                unsafe_allow_html=True)
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        country = st.selectbox("🌍 الدولة:", list(EXCHANGE_RATES.keys()), key="country")
    with cc2:
        state = st.text_input("🗺️ الولاية:", "الخرطوم", key="state")
    with cc3:
        city = st.text_input("🏙️ المدينة:", "الخرطوم", key="city")
    rate = EXCHANGE_RATES.get(country, {"rate":1.0,"sym":"USD"})
    local_rate, local_sym = rate["rate"], rate["sym"]
    live_prices = market_prices(country, city, state)

    st.markdown('<div class="section-title">🧬 أساس حساب البروتين</div>',
                unsafe_allow_html=True)
    basis_choice = st.radio("اختر أساس الحساب:",
        ["البروتين المهضوم (DP) — الأدق علمياً",
         "البروتين الخام (CP) — الأسهل ميدانياً"],
        horizontal=True, key="basis")
    use_dp = "DP" in basis_choice
    if use_dp:
        st.success("🎯 تستخدم الآن **DP** (البروتين المهضوم) — الأدق علمياً")
    else:
        st.info("📊 تستخدم الآن **CP** (البروتين الخام) — الأسهل ميدانياً")

    st.markdown('<div class="section-title">🐾 اختر الحيوان والحالة</div>',
                unsafe_allow_html=True)
    animal_tabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐪 إبل",
                            "🐎 خيول", "🐔 دواجن", "🦆 سمان", "🐟 أسماك"])

    animal_choice = production = requirement = None
    img_key = "عام"; std_key_global = ""

    with animal_tabs[0]:
        st.markdown("### 🐄 الأبقار — NRC 2001")
        ct = st.selectbox("الحالة:", ["حليب_عالي","حليب_متوسط","حليب_منخفض",
            "تسمين_مكثف","تسمين_عادي","حمل_أخير","صيانة"], key="cattle_t",
            format_func=lambda x: {"حليب_عالي":"🐄 حلابة عالية",
                "حليب_متوسط":"🐄 حلابة متوسطة","حليب_منخفض":"🐄 حلابة منخفضة",
                "تسمين_مكثف":"💪 تسمين مكثف (ADG >1.3)",
                "تسمين_عادي":"💪 تسمين عادي","حمل_أخير":"🤰 حمل أخير",
                "صيانة":"🌿 صيانة"}.get(x,x))
        cc1_, cc2_ = st.columns(2); params = {}
        with cc1_:
            if "حليب" in ct:
                params["milk"] = st.number_input("🥛 إنتاج الحليب (كجم):",
                    5.0, 60.0, 20.0, 1.0, key="c_milk")
        with cc2_:
            params["weight"] = st.number_input("⚖️ الوزن (كجم):",
                200.0, 900.0, 500.0, 25.0, key="c_wt")
        rq = req_cattle(ct, **params)
        a1, a2, a3 = st.columns(3)
        a1.metric("🧬 DP", f"{rq.DP}%"); a2.metric("🧬 CP", f"{rq.CP}%")
        a3.metric("🌽 SE", f"{rq.SE}")
        st.caption(f"📝 {rq.note}")
        if st.checkbox("✅ اعتماد الأبقار", key="u_c"):
            animal_choice="أبقار"; production=ct; requirement=rq
            img_key="أبقار"; std_key_global=rq.oil_key

    with animal_tabs[1]:
        st.markdown("### 🐏 الأغنام — NRC 2007")
        sg = st.radio("الجنس:", ["ذكر (تسمين)","أنثى (أمهات)"],
                       horizontal=True, key="sg")
        is_m = "ذكر" in sg
        if is_m:
            stp = st.selectbox("الحالة:", ["تسمين_مكثف","تسمين_عادي","حملان_تيد"],
                key="sh_t_m", format_func=lambda x:{"تسمين_مكثف":"💪 مكثف",
                "تسمين_عادي":"💪 عادي","حملان_تيد":"🐑 تيد"}.get(x,x))
        else:
            stp = st.selectbox("الحالة:", ["مرضعات","حامل_أخير","حامل_متوسط","صيانة"],
                key="sh_t_f", format_func=lambda x:{"مرضعات":"🍼 مرضعات",
                "حامل_أخير":"🤰 حامل أخير","حامل_متوسط":"🤰 حامل متوسط",
                "صيانة":"🌿 صيانة"}.get(x,x))
        litter = 1
        if stp == "مرضعات":
            litter = st.number_input("👶 عدد المواليد:", 1, 3, 1, key="sh_lit")
        rq = req_sheep(stp, is_male=is_m, litter=litter)
        a1, a2, a3 = st.columns(3)
        a1.metric("🧬 DP", f"{rq.DP}%"); a2.metric("🧬 CP", f"{rq.CP}%")
        a3.metric("🌽 SE", f"{rq.SE}")
        st.caption(f"📝 {rq.note}")
        if st.checkbox("✅ اعتماد الأغنام", key="u_sh"):
            animal_choice="أغنام"; production=stp; requirement=rq
            img_key="أغنام"; std_key_global=rq.oil_key

    with animal_tabs[2]:
        st.markdown("### 🐐 الماعز — NRC 2007")
        gg = st.radio("الجنس:", ["ذكر (تسمين)","أنثى (حلابة)"],
                       horizontal=True, key="gg")
        is_m_g = "ذكر" in gg
        milk_g = 0
        if is_m_g:
            gtp = st.selectbox("الحالة:", ["تسمين_جديان","تيوس"], key="gt_m",
                format_func=lambda x:{"تسمين_جديان":"💪 جديان","تيوس":"🐐 تيوس"}.get(x,x))
        else:
            gtp = st.selectbox("الحالة:",
                ["حلابة_عالي","حلابة_متوسط","حامل_أخير","صيانة"], key="gt_f",
                format_func=lambda x:{"حلابة_عالي":"🍼 عالي",
                "حلابة_متوسط":"🍼 متوسط","حامل_أخير":"🤰 حامل",
                "صيانة":"🌿 صيانة"}.get(x,x))
            if "حلابة" in gtp:
                milk_g = st.number_input("🥛 الحليب (كجم):", 0.5, 8.0, 2.0, 0.25, key="g_milk")
        rq = req_goat(gtp, is_male=is_m_g, milk=milk_g)
        a1, a2, a3 = st.columns(3)
        a1.metric("🧬 DP", f"{rq.DP}%"); a2.metric("🧬 CP", f"{rq.CP}%")
        a3.metric("🌽 SE", f"{rq.SE}")
        st.caption(f"📝 {rq.note}")
        if st.checkbox("✅ اعتماد الماعز", key="u_g"):
            animal_choice="ماعز"; production=gtp; requirement=rq
            img_key="ماعز"; std_key_global=rq.oil_key

    with animal_tabs[3]:
        st.markdown("### 🐪 الإبل — FAO 2010")
        cam_t = st.selectbox("الحالة:",
            ["نمو","تسمين","حليب","سباق","صيانة"], key="cam_t",
            format_func=lambda x:{"نمو":"🐪 نمو","تسمين":"💪 تسمين",
            "حليب":"🍼 حليب","سباق":"🏃 سباق","صيانة":"🌿 صيانة"}.get(x,x))
        cam_wt = st.number_input("⚖️ الوزن (كجم):", 100.0, 800.0, 400.0, 25.0, key="cam_wt")
        cam_milk = 5.0
        if cam_t == "حليب":
            cam_milk = st.number_input("🥛 الحليب (لتر):", 2.0, 20.0, 5.0, 0.5, key="cam_milk")
        rq = req_camel(cam_t, weight=cam_wt, milk=cam_milk)
        a1, a2, a3, a4 = st.columns(4)
        a1.metric("🧬 DP", f"{rq.DP}%"); a2.metric("🧬 CP", f"{rq.CP}%")
        a3.metric("🌽 SE", f"{rq.SE}"); a4.metric("🌾 NDF", f"{rq.NDF}%")
        st.info(f"📝 {rq.note}")
        if st.checkbox("✅ اعتماد الإبل", key="u_cam"):
            animal_choice="إبل"; production=cam_t; requirement=rq
            img_key="إبل"; std_key_global=rq.oil_key

    with animal_tabs[4]:
        st.markdown("### 🐎 الخيول — NRC 2007")
        h_t = st.selectbox("الحالة:",
            ["رياضة_مكثف","رياضة_عادي","نمو_أمهار","مرضعات","صيانة"], key="h_t",
            format_func=lambda x:{"رياضة_مكثف":"🏇 مكثف","رياضة_عادي":"🏇 عادي",
            "نمو_أمهار":"🐎 أمهار","مرضعات":"🍼 مرضعات",
            "صيانة":"🌿 صيانة"}.get(x,x))
        rq = req_horse(h_t)
        a1, a2, a3 = st.columns(3)
        a1.metric("🧬 DP", f"{rq.DP}%"); a2.metric("🧬 CP", f"{rq.CP}%")
        a3.metric("🌽 SE", f"{rq.SE}")
        st.caption(f"📝 {rq.note}")
        if st.checkbox("✅ اعتماد الخيول", key="u_h"):
            animal_choice="خيول"; production=h_t; requirement=rq
            img_key="خيول"; std_key_global=rq.oil_key

    with animal_tabs[5]:
        st.markdown("### 🐔 الدواجن — Ross 308")
        p_strain = st.radio("السلالة:", ["لاحم","بياض"], horizontal=True, key="p_s")
        p_age = st.number_input("العمر (أسبوع):", 1, 20, 1, key="p_age")
        rq = req_poultry(p_strain, p_age)
        a1, a2, a3, a4 = st.columns(4)
        a1.metric("🧬 DP", f"{rq.DP}%"); a2.metric("🧬 CP", f"{rq.CP}%")
        a3.metric("🌽 SE", f"{rq.SE}"); a4.metric("Ca", f"{rq.Ca}%")
        st.caption(f"📝 {rq.note}")
        if st.checkbox("✅ اعتماد الدواجن", key="u_p"):
            animal_choice="دواجن"; production=p_strain; requirement=rq
            img_key="دواجن"; std_key_global=rq.oil_key

    with animal_tabs[6]:
        st.markdown("### 🦆 السمان — NRC")
        q_s = st.radio("النوع:", ["تسمين","بياض"], horizontal=True, key="q_s")
        q_age = st.number_input("العمر (أسبوع):", 1, 8, 1, key="q_age")
        rq = req_quail(q_s, q_age)
        a1, a2, a3 = st.columns(3)
        a1.metric("🧬 DP", f"{rq.DP}%"); a2.metric("🧬 CP", f"{rq.CP}%")
        a3.metric("🌽 SE", f"{rq.SE}")
        st.caption(f"📝 {rq.note}")
        if st.checkbox("✅ اعتماد السمان", key="u_q"):
            animal_choice="سمان"; production=q_s; requirement=rq
            img_key="سمان"; std_key_global=rq.oil_key

    with animal_tabs[7]:
        st.markdown("### 🐟 الأسماك — NRC Fish")
        f_s = st.selectbox("النوع:", ["البلطي النيلي","القرموط الأفريقي","الكارب"], key="f_s")
        f_st = st.selectbox("المرحلة:", ["بادئ زريعة","نمو","تسمين"], key="f_st")
        rq = req_fish(f_s, f_st)
        a1, a2, a3 = st.columns(3)
        a1.metric("🧬 DP", f"{rq.DP}%"); a2.metric("🧬 CP", f"{rq.CP}%")
        a3.metric("🌽 SE", f"{rq.SE}")
        st.caption(f"📝 {rq.note}")
        if st.checkbox("✅ اعتماد الأسماك", key="u_f"):
            animal_choice="أسماك"; production=f_st; requirement=rq
            img_key="أسماك"; std_key_global=rq.oil_key

    if not animal_choice or not requirement:
        st.warning("⚠️ اختر حيواناً، وفعّل خيار ✅ الاعتماد للمتابعة")
        st.stop()

    st.markdown(f'<div class="section-title">🎯 المختار: {animal_choice} — '
                f'{requirement.name_ar}</div>', unsafe_allow_html=True)
    info1, info2, info3, info4 = st.columns(4)
    info1.metric("🧬 DP", f"{requirement.DP}%")
    info2.metric("🧬 CP", f"{requirement.CP}%")
    info3.metric("🌽 SE", f"{requirement.SE}")
    info4.metric("🌾 NDF", f"{requirement.NDF}%")
    st.info(f"📝 {requirement.note} | أساس الحساب: "
            f"{'DP (مهضوم)' if use_dp else 'CP (خام)'}")

    oil_std_info = get_oil_standard(std_key_global)
    st.markdown('<div class="section-title">🌰 معيار الزيوت لهذا الحيوان</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="oil-info-card">
    <b>📊 الحدود القياسية للزيوت:</b><br>
    ▪️ الحد الأقصى المسموح: <b>{oil_std_info['max']}%</b><br>
    ▪️ النسبة المثالية: <b>{oil_std_info['optimal']}%</b><br>
    ▪️ المرجع: <b>{oil_std_info['source']}</b><br>
    <small>💡 كل 1% زيت ≈ 90 kcal/kg علف</small>
    </div>
    """, unsafe_allow_html=True)

    requester = st.text_input("👤 اسم طالب العلفة (سيظهر في التقرير):",
        placeholder="مثال: مزرعة الأمل — أحمد محمد", key="req_name")

    st.markdown('<div class="section-title">🌾 اختيار المكونات</div>',
                unsafe_allow_html=True)
    selected = []; prices = {}

    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        exp = "الحبوب" in cat_name or "الأكساب" in cat_name or "الزيوت" in cat_name
        with st.expander(f"📁 {cat_name}", expanded=exp):
            sub = st.columns(3)
            for i, (ing_name, ing_data) in enumerate(items.items()):
                with sub[i % 3]:
                    default_chk = ing_name in [
                        "ملح الطعام", "الحجر الجيري",
                        "فوسفات ثنائي الكالسيوم", "مضاد سموم فطرية"]
                    if animal_choice in ["أغنام","ماعز","أبقار","إبل"]:
                        default_chk = default_chk or ing_name == "بيكربونات الصوديوم"
                    if animal_choice in ["دواجن","سمان"]:
                        default_chk = default_chk or "بريمكس" in ing_name

                    if cat_name == "🌰 الزيوت النباتية والحيوانية":
                        st.markdown(f"**{ing_name}**")
                        st.caption(f"⚡ SE={ing_data.get('SE',0):.0f} | "
                                   f"{ing_data.get('desc','')[:50]}")
                        chk = st.checkbox("إضافة", value=False,
                                           key=f"ck_{animal_choice}_{ing_name}")
                    else:
                        chk = st.checkbox(ing_name, value=default_chk,
                                           key=f"ck_{animal_choice}_{ing_name}")

                    price = live_prices.get(ing_name, 300.0)
                    if is_owner():
                        price = st.number_input("$", min_value=5.0,
                            value=float(price), key=f"p_{animal_choice}_{ing_name}",
                            label_visibility="collapsed")
                    else:
                        st.caption(f"💰 ${price:.0f}/طن")

                    if chk:
                        selected.append(ing_name); prices[ing_name] = price

    st.markdown("---")

    if st.button("🚀 تشغيل المحرك الذكي — مطابقة شاملة",
                 type="primary", use_container_width=True, key="run"):
        if len(selected) < 3:
            st.error("⚠️ اختر 3 مكونات على الأقل")
        else:
            auto_salts = auto_add_salts(animal_choice, requirement)
            for sname, spct in auto_salts.items():
                if sname not in selected:
                    selected.append(sname)
                    prices[sname] = live_prices.get(sname, 300.0)

            std = req_to_standard(requirement)
            basis_label = "DP" if use_dp else "CP"

            with st.spinner(f"⏳ جاري التركيب على أساس {basis_label}..."):
                result = auto_formulate_smart(selected, prices, std,
                                              oil_key=std_key_global,
                                              tolerance=0.3, max_iter=50)

            if result["success"]:
                formula = result["formula"]
                actual = result["actual"]
                cost = result["cost"]
                tot_oil = result.get("total_oil", 0.0)
                oil_std = result.get("oil_std", oil_std_info)

                cmp_rows = []; cmp_scores = []
                labels = {"CP":"بروتين خام CP","DP":"بروتين مهضوم DP",
                          "SE":"معادل النشاء SE","NDF":"ألياف NDF",
                          "ADF":"ألياف ADF","EE":"دهن EE","ASH":"رماد ASH",
                          "Ca":"كالسيوم Ca","P":"فسفور P"}
                for k, sv in std.items():
                    cvv = actual.get(k, 0.0)
                    diff = cvv - sv
                    pct = (diff/sv*100) if sv else 0
                    ev = evaluate_diff(pct)
                    cmp_scores.append({"score": ev["score"]})
                    cmp_rows.append({"العنصر": labels.get(k,k),
                                     "المعيار": f"{sv:.2f}",
                                     "المحسوب": f"{cvv:.2f}",
                                     "الفرق": f"{diff:+.3f}",
                                     "الفرق %": f"{pct:+.2f}%",
                                     "التقييم": ev["label"]})
                overall = overall_rating(cmp_scores)
                perfect = result.get("perfect_match", False)

                if perfect:
                    st.success(f"🎯 **مطابقة كاملة!** — على أساس {basis_label}")
                else:
                    st.success(f"✅ تم التركيب — على أساس {basis_label}")
                st.info(f"🔁 التكرارات: {result['iterations']} | التقييم: "
                        f"**{overall['label']}** ({overall['score']:.0f}%)")

                e1, e2, e3, e4 = st.columns(4)
                e1.metric("خطأ DP", f"{result['dp_error']:.3f}%")
                e2.metric("خطأ SE", f"{result['se_error']:.3f}")
                e3.metric("خطأ NDF", f"{result['ndf_error']:.2f}%")
                e4.metric("خطأ Ca", f"{result['ca_error']:.3f}%")

                st.markdown("### 📊 جدول المقارنة الشامل")
                st.dataframe(pd.DataFrame(cmp_rows), use_container_width=True,
                             hide_index=True)

                st.markdown("### 🌰 تقييم الزيوت")
                if tot_oil > 0:
                    if tot_oil > oil_std["max"]:
                        st.error(f"⚠️ تجاوز الحد الأقصى! ({tot_oil:.2f}% > "
                                 f"{oil_std['max']}%)")
                    elif tot_oil > oil_std["optimal"]*1.2:
                        st.warning(f"⚡ مرتفع قليلاً ({tot_oil:.2f}%) — "
                                   f"المثالي {oil_std['optimal']}%")
                    else:
                        st.success(f"✅ مطابق — {tot_oil:.2f}% "
                                   f"(المثالي {oil_std['optimal']}%)")
                    st.caption(f"📖 المرجع: {oil_std['source']}")

                    oils_used = [(i, p) for i, p in formula.items()
                                 if i in get_oil_ingredients()]
                    for ing, pct in oils_used:
                        st.markdown(f'<div class="oil-item">🌰 <b>{ing}:</b> '
                                    f'{pct:.2f}% | ≈ {pct*90:.0f} kcal/kg</div>',
                                    unsafe_allow_html=True)
                else:
                    st.info("ℹ️ لم تستخدم أي زيوت في هذه الخلطة")

                st.markdown("#### 🌾 المكونات:")
                for ing, pct in formula.items():
                    st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> '
                                f'{pct:.2f}% ({pct*10:.1f} كجم/طن)</div>',
                                unsafe_allow_html=True)

                st.metric("💰 التكلفة الفعلية للطن:",
                          f"${cost:.2f} ({cost*local_rate:,.0f} {local_sym})")

                st.session_state["active_formula"] = formula
                st.session_state["computed_ton_cost"] = cost
                st.session_state["active_animal_img"] = ANIMAL_IMAGES.get(
                    img_key, ANIMAL_IMAGES["عام"])
                st.session_state["active_stage_title"] = \
                    f"{animal_choice} — {requirement.name_ar}"

                st.markdown("### 📥 تحميل التقارير")
                d1, d2 = st.columns(2)
                with d1:
                    try:
                        pdf = pdf_gen.generate(formula, requirement, animal_choice,
                            cost, city, cost*local_rate, local_sym,
                            requester, basis_label, std_key_global, True)
                        fn = f"TaworNology_{animal_choice}_{datetime.now():%Y%m%d_%H%M}.pdf"
                        st.download_button("📥 تحميل PDF", pdf, file_name=fn,
                            mime="application/pdf", use_container_width=True)
                    except Exception as e:
                        st.error(f"⚠️ خطأ PDF: {e}")
                with d2:
                    try:
                        xl = export_excel(std, actual, requester,
                                            animal_choice, formula, std_key_global)
                        if xl:
                            fn = f"TaworNology_{animal_choice}_{datetime.now():%Y%m%d_%H%M}.xlsx"
                            st.download_button("📊 تحميل Excel", xl, file_name=fn,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True)
                    except Exception as e:
                        st.error(f"⚠️ خطأ Excel: {e}")

                if PLOTLY and len(formula) > 1:
                    try:
                        colors = ['#e53935','#8e24aa','#3949ab','#1e88e5',
                                  '#00897b','#43a047','#7cb342','#fdd835',
                                  '#fb8c00','#6d4c41','#c62828','#6a1b9a']
                        fig = px.pie(values=list(formula.values()),
                                     names=list(formula.keys()),
                                     title=f"توزيع المكونات — {animal_choice}",
                                     color_discrete_sequence=colors)
                        fig.update_traces(textposition='inside',
                                          textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass
            else:
                st.error(f"❌ {result['message']}")


# ═════════════════════════════════════════════════════════════════════════════
# [20] مكتبة الزيوت
# ═════════════════════════════════════════════════════════════════════════════

with tabs[1]:
    st.markdown('<div class="section-title">🌰 مكتبة الزيوت النباتية والحيوانية</div>',
                unsafe_allow_html=True)
    st.write("15 زيتاً معتمداً وفق NRC / INRA / Ross 308 / FAO.")

    st.markdown("### 📊 الحدود القياسية حسب الحيوان")
    st.dataframe(pd.DataFrame([{
        "الحيوان": k, "الحد الأقصى %": f"{v['max']}%",
        "المثالي %": f"{v['optimal']}%", "المرجع": v["source"]}
        for k, v in MAX_OIL_PERCENTAGE.items()]),
        use_container_width=True, hide_index=True)

    st.markdown("### 🌰 الزيوت المتوفرة")
    oils = get_oil_ingredients()
    prices_oil = market_prices("السودان", "الخرطوم")
    for ing_name, ing_data in oils.items():
        with st.expander(f"🌰 {ing_name}"):
            c1, c2, c3 = st.columns(3)
            c1.metric("SE", f"{ing_data.get('SE',0):.0f}")
            c1.metric("EE", "100%")
            c2.metric("kcal/kg ≈", f"{ing_data.get('SE',0)*41:.0f}")
            c2.metric("السعر $/طن", f"{prices_oil.get(ing_name,0):.0f}")
            c3.metric("أقصى دواجن", f"{ing_data.get('max_poultry','N/A')}%")
            c3.metric("أقصى مجترات", f"{ing_data.get('max_ruminant','N/A')}%")
            st.info(f"📝 {ing_data.get('desc','')}")
            st.caption(f"📖 المرجع: {ing_data.get('source','NRC')}")


# ═════════════════════════════════════════════════════════════════════════════
# [21] بدائل الحليب
# ═════════════════════════════════════════════════════════════════════════════

with tabs[2]:
    st.markdown('<div class="section-title">🍼 مختبر بدائل الحليب</div>',
                unsafe_allow_html=True)
    mr1, mr2 = st.columns(2)
    with mr1:
        mr_animal = st.selectbox("نوع الحيوان:", list(MILK_STANDARDS.keys()), key="mr_a")
        mr_vol = st.number_input("الكمية (كجم):", 1.0, 10000.0, 100.0, 10.0, key="mr_v")
    with mr2:
        std_mr = MILK_STANDARDS[mr_animal]
        st.markdown(f"""
        <div class="price-card">
        <b>📊 المعيار — {mr_animal}:</b><br>
        ▪️ بروتين: <b>{std_mr['CP']}%</b> | ▪️ دهن: <b>{std_mr['Fat']}%</b><br>
        ▪️ لاكتوز: <b>{std_mr['Lactose']}%</b><br>
        <small>{std_mr['notes']}</small>
        </div>
        """, unsafe_allow_html=True)

    mr_sel = []
    mr_cols = st.columns(3)
    for i, (name, data) in enumerate(MILK_INGREDIENTS.items()):
        with mr_cols[i % 3]:
            default_mr = name in [
                "حليب مجفف منزوع الدسم","حليب مجفف كامل الدسم",
                "شرش حليب مجفف","زيت جوز الهند","زيت النخيل",
                "بريمكس فيتامينات","كالسيوم كربونات",
                "فوسفات ثنائي الكالسيوم","ملح طعام"]
            if st.checkbox(f"{name} — ${data['price']}",
                            value=default_mr, key=f"mr_{name}"):
                mr_sel.append(name)

    if st.button("🧪 تشغيل التركيب", type="primary",
                 use_container_width=True, key="mr_run"):
        if len(mr_sel) < 3:
            st.warning("⚠️ اختر 3 مكونات")
        else:
            r = formulate_milk(mr_animal, mr_vol, mr_sel)
            if r["success"]:
                st.success(f"✅ تم التركيب لـ ({mr_animal})")
                for ing, pct in r["formula"].items():
                    kg = pct*mr_vol/100.0
                    st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> '
                                f'{pct:.2f}% ({kg:.2f} كجم)</div>',
                                unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                m1.metric("💰 التكلفة لـ 100 كجم:", f"${r['cost_per_kg']*100:.2f}")
                m2.metric("💰 التكلفة/كجم:", f"${r['cost_per_kg']:.3f}")
            else:
                st.error(f"❌ {r['message']}")


# ═════════════════════════════════════════════════════════════════════════════
# [22] المختبر الذكي OCR
# ═════════════════════════════════════════════════════════════════════════════

with tabs[3]:
    st.markdown('<div class="section-title">📷 المختبر الذكي (OCR)</div>',
                unsafe_allow_html=True)
    if not OCR:
        st.error("⚠️ مكتبة pytesseract غير مثبتة")
        st.code("pip install pytesseract opencv-python-headless", language="bash")
    else:
        uploaded = st.file_uploader("📤 ارفع صورة:", type=["jpg","jpeg","png"])
        if uploaded:
            st.image(uploaded, caption="الصورة", use_container_width=True)
            if st.button("🔍 تحليل", type="primary", use_container_width=True):
                with st.spinner("جاري التحليل..."):
                    r = ocr_extract(uploaded.read())
                if r["success"]:
                    st.success(f"✅ تم استخراج {r['count']} مادة")
                    if r["ingredients"]:
                        st.dataframe(pd.DataFrame([
                            {"المادة": k, "النسبة": f"{v:.2f}%"}
                            for k, v in r["ingredients"].items()
                        ]), use_container_width=True, hide_index=True)
                        nutrients = compute_nutrients(r["ingredients"])
                        n1, n2, n3, n4 = st.columns(4)
                        n1.metric("CP", f"{nutrients['CP']:.2f}%")
                        n2.metric("DP", f"{nutrients['DP']:.2f}%")
                        n3.metric("SE", f"{nutrients['SE']:.2f}")
                        n4.metric("NDF", f"{nutrients['NDF']:.2f}%")
                    with st.expander("📝 النص الخام"):
                        st.text(r.get("raw_text", ""))
                else:
                    st.error(f"❌ {r['message']}")


# ═════════════════════════════════════════════════════════════════════════════
# [23] تبويبات المالك
# ═════════════════════════════════════════════════════════════════════════════

if is_owner():
    with tabs[4]:  # إدارة المزارع
        st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج اللاحم</div>',
                    unsafe_allow_html=True)
        with st.expander("➕ إضافة مزرعة"):
            nf_name = st.text_input("اسم المزرعة:", key="nf_name")
            nf_owner = st.text_input("المالك:", key="nf_owner")
            nf_phone = st.text_input("واتساب:", WHATSAPP, key="nf_phone")
            if st.button("💾 حفظ") and nf_name:
                st.session_state["broiler_farms"][nf_name] = {
                    "owner": nf_owner, "phone": nf_phone,
                    "data": {"age":1,"birds":1000,"weight_kg":0.045,
                             "feed_kg":0.0,"dead":0,"temp":33.0,"hum":65.0}}
                st.success(f"✅ تمت إضافة {nf_name}"); st.rerun()

        if st.session_state["broiler_farms"]:
            farms = list(st.session_state["broiler_farms"].keys())
            sel = st.selectbox("اختر مزرعة:", [""] + farms)
            if sel:
                d = st.session_state["broiler_farms"][sel]["data"]
                b1, b2 = st.columns(2)
                with b1:
                    d["age"] = st.number_input("العمر (يوم):", 1, 60, d["age"], key="bf_a")
                    d["birds"] = st.number_input("الطيور:", 1, value=d["birds"], key="bf_b")
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
                adg = ((d["weight_kg"] - 0.045)*1000/d["age"]) if d["age"]>0 else 0
                fcr = (d["feed_kg"]/gain) if gain > 0 else 0
                liv = 100 - (d["dead"]/d["birds"]*100)
                epef = ((liv*d["weight_kg"])/(d["age"]*fcr)*100
                        if d["age"]>0 and fcr>0 else 0)
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("ADG (جم)", f"{adg:.1f}")
                k2.metric("FCR", f"{fcr:.2f}")
                k3.metric("الحيوية %", f"{liv:.1f}")
                k4.metric("EPEF", f"{epef:.0f}")

    with tabs[5]:  # البورصة
        st.markdown('<div class="section-title">📊 البورصة</div>',
                    unsafe_allow_html=True)
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

    with tabs[6]:  # المستودعات
        st.markdown('<div class="section-title">🏭 المستودعات</div>',
                    unsafe_allow_html=True)
        inv = st.session_state["inventory"]
        a, b, c, d = st.columns(4)
        a.metric("إجمالي", len(inv))
        low = sum(1 for v in inv.values() if v.get("quantity",0) < 5)
        b.metric("منخفضة", low)
        crit = sum(1 for v in inv.values() if v.get("quantity",0) <= 0)
        c.metric("نفذت", crit)
        d.metric("آمنة", len(inv) - low - crit)
        cols = st.columns(3)
        for i, (name, data) in enumerate(list(inv.items())[:60]):
            with cols[i % 3]:
                q = data["quantity"] if isinstance(data, dict) else data
                badge = "🔴" if q <= 0 else ("🟡" if q < 5 else "🟢")
                st.markdown(f"{badge} **{name}**: {q:.1f} طن")
                new_q = st.number_input("تحديث:", min_value=0.0,
                    value=float(q), key=f"inv_{name}",
                    label_visibility="collapsed")
                if isinstance(inv[name], dict):
                    inv[name]["quantity"] = new_q

    with tabs[7]:  # الفواتير
        st.markdown('<div class="section-title">🧾 الفواتير</div>',
                    unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        with fc1: client = st.text_input("العميل:", "مزرعة الأمل")
        with fc2: tons = st.number_input("الكمية (طن):", 0.1, 1000.0, 2.0, 0.5)
        with fc3: profit = st.number_input("هامش الربح ($/طن):", 0.0, 1000.0, 50.0)
        sell = st.session_state["computed_ton_cost"] + profit
        total = sell * tons
        st.markdown(f"""
        <div class="price-card">
        <h4>🧾 فاتورة</h4>
        <p><b>العميل:</b> {client}</p>
        <p><b>الكمية:</b> {tons} طن</p>
        <p><b>سعر الطن:</b> ${sell:.2f}</p>
        <p style="font-size:1.3rem; color:#1b5e20;">
        <b>الإجمالي:</b> ${total:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    with tabs[8]:  # الديباجة
        st.markdown('<div class="section-title">🖨️ مصمم الديباجة</div>',
                    unsafe_allow_html=True)
        brand = st.text_input("اسم البراند:", APP_NAME)
        st.markdown(f"""
        <div style="border: 3px dashed #1b5e20; padding: 30px;
        border-radius: 15px; background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
        direction: rtl; text-align: center;">
        <img src="{st.session_state['active_animal_img']}"
        style="width:100%; max-height:200px; object-fit:cover;
        border-radius:12px; margin-bottom:15px;">
        <h2 style="color: #1b5e20;">🌟 {brand} 🌟</h2>
        <h3 style="color: #c62828;">{SUPERVISOR} — {SUPERVISOR_TITLE}</h3>
        <p style="background:#e8f5e9; padding:12px; border-radius:8px;
        color:#1b5e20; font-weight:bold;">
        🎯 {st.session_state['active_stage_title']}</p>
        <small style="color:#666;">📅 {datetime.now():%Y-%m-%d}</small><br>
        <small style="color:#c62828;">🤲 {DUA_SHORT}</small>
        </div>
        """, unsafe_allow_html=True)

    with tabs[9]:  # التحليلات
        st.markdown('<div class="section-title">📈 التحليلات</div>',
                    unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("الخلطات", "1,247"); m2.metric("متوسط التكلفة", "$285")
        m3.metric("التوفير", "18%"); m4.metric("رضا العملاء", "96%")
        if PLOTLY:
            usage = pd.DataFrame({
                'المادة': ['ذرة','صويا','نخالة','زيوت','أملاح','أخرى'],
                'نسبة الاستخدام': [42,23,14,8,8,5]})
            fig = px.pie(usage, values='نسبة الاستخدام', names='المادة',
                         color_discrete_sequence=px.colors.sequential.Greens)
            st.plotly_chart(fig, use_container_width=True)

    with tabs[10]:  # التعليقات
        st.markdown('<div class="section-title">💬 التعليقات</div>',
                    unsafe_allow_html=True)
        st.text_area("الحالية:", value=st.session_state["shared_comments"],
                     height=200, disabled=True)
        nc = st.text_area("جديد:")
        if st.button("➕ نشر") and nc:
            st.session_state["shared_comments"] += \
                f"\n• [{datetime.now():%Y-%m-%d %H:%M}]: {nc}"
            st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# [24] المراجع + المساعدة + الدليل
# ═════════════════════════════════════════════════════════════════════════════

if "📚 المراجع" in tabs_titles:
    with tabs[tabs_titles.index("📚 المراجع")]:
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
        - NRC 2012 — Fat in Animal Nutrition
        - INRA 2018 — Lipids in Ruminant Diets
        - Palmquist (2006) — Milk Fat Depression
        """)

if "💡 المساعدة" in tabs_titles:
    with tabs[tabs_titles.index("💡 المساعدة")]:
        st.markdown('<div class="section-title">💡 المساعدة</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        ### الأسئلة الشائعة:
        - **كيف أبدأ؟** اختر الحيوان → الحالة الفسيولوجية → ✅ الاعتماد
        - **DP أم CP؟** اختر في الأعلى: DP (الأدق)، CP (الأسهل)
        - **الزيوت؟** راجع تبويب "🌰 مكتبة الزيوت" لمعرفة الحدود
        - **تجاوز الزيوت؟** المحرك يقيدها تلقائياً وفق المعيار العالمي

        ### 🔧 الدعم
        📧 {OWNER_EMAIL}
        📱 {WHATSAPP}
        """)

if "📖 الدليل" in tabs_titles:
    with tabs[tabs_titles.index("📖 الدليل")]:
        st.markdown('<div class="section-title">📖 دليل المستخدم</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        ### الغرض
        **{APP_NAME}** — منصة ذكية لتركيب الأعلاف بأقل تكلفة وأعلى جودة.

        ### الميزات الرئيسية
        - 🐄 **8 قطاعات**: أبقار، أغنام، ماعز، إبل، خيول، دواجن، سمان، أسماك
        - 🌰 **15 زيتاً** بمعايير NRC/INRA/FAO مع فرض الحدود تلقائياً
        - 🧬 **احتياجات متخصصة** لكل حيوان حسب NRC
        - 🧠 **محرك ذكي** يطابق DP + SE + NDF + ADF + Ca + P + EE
        - 🔀 **DP أو CP**: اختيار أساس الحساب
        - 📷 **OCR**: تحليل صور المكونات
        - 📄 **PDF احترافي**: ختم + رسوم ملوّنة + جدول الزيوت
        - 🐔 **إدارة مزارع**: ADG / FCR / EPEF / الحيوية
        - 🏭 **مستودعات** + فواتير + بورصة أسعار
        - ⚡ **حساب الطاقة**: كل 1% زيت ≈ 90 kcal/kg

        ### كود المالك
        `{OWNER_CODE}` | كود المختص: `{SPECIALIST_CODE}`
        """)


# ═════════════════════════════════════════════════════════════════════════════
# [25] التذييل الثابت
# ═════════════════════════════════════════════════════════════════════════════

st.markdown(
    f'<div class="mini-signature">🌾 {APP_NAME} | {SUPERVISOR} © 2026</div>',
    unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# نهاية الملف — الإصدار المدمج 20.0
# ============================================================================
