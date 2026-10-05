# -*- coding: utf-8 -*-
# Tawor Nology v10.1 — Compact Full Build
# إشراف: م. عبدالقادر إسماعيل تاور | رحم الله والدي إسماعيل تاور وأختي ابتسام

import streamlit as st
import numpy as np, pandas as pd, json, os, base64, time, re, io, sqlite3
import hashlib, secrets, warnings, urllib.parse, urllib.request, smtplib
from datetime import datetime, timedelta, date
from functools import lru_cache
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
warnings.filterwarnings('ignore')

try:
    from scipy.optimize import linprog, OptimizeResult
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    class OptimizeResult:
        def __init__(self, **kw):
            for k, v in kw.items(): setattr(self, k, v)

try:
    import plotly.express as px, plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError: PLOTLY_AVAILABLE = False

try:
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Wedge
    MATPLOTLIB_AVAILABLE = True
except ImportError: MATPLOTLIB_AVAILABLE = False

try:
    from gtts import gTTS; GTTS_AVAILABLE = True
except ImportError: GTTS_AVAILABLE = False

try:
    import pytesseract, cv2; OCR_AVAILABLE = True
except ImportError: OCR_AVAILABLE = False

try:
    import openpyxl
    from openpyxl.styles import Font as XF, PatternFill, Alignment as XA, Border, Side
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError: OPENPYXL_AVAILABLE = False

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
except ImportError: REPORTLAB_AVAILABLE = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_AVAILABLE = True
except ImportError: ARABIC_AVAILABLE = False

try:
    import qrcode; QRCODE_AVAILABLE = True
except ImportError: QRCODE_AVAILABLE = False

try:
    from PIL import Image as PILImage; PIL_AVAILABLE = True
except ImportError: PIL_AVAILABLE = False

# ═══ الدعاء والإعدادات ═══
DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي ابتسام"
DUA_FULL = "رحم الله والدي إسماعيل تاور وأختي ابتسام، وأسكنهما فسيح جناته، وجعل قبرهما روضة من رياض الجنة"
DUA_QURAN = "﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾"
DUA_VERSE = "﴿ وَقُل رَّبِّ ارْحَمْهُمَا كَمَا رَبَّيَانِي صَغِيرًا ﴾"
DUA_BANNER = "🕌 <b>إلى زوارنا الكرام:</b><br>هذه المنصة صدقةٌ جارية عن <b>والدي إسماعيل تاور</b> و<b>أختي ابتسام</b>.<br>نسألكم بظهر الغيب أن تشاركونا الدعاء لهما. 🤲"

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

st.set_page_config(page_title=f"{APP_NAME} | {APP_TAGLINE}",
                    page_icon="🌾", layout="wide",
                    initial_sidebar_state="collapsed")

# ═══ الخطوط العربية ═══
FONT_DIR = "fonts"; os.makedirs(FONT_DIR, exist_ok=True)
FONT_URLS = [
    ("https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf", "Amiri-Regular.ttf"),
    ("https://github.com/google/fonts/raw/main/ofl/cairo/Cairo%5Bslnt%2Cwght%5D.ttf", "Cairo-Regular.ttf"),
]

class ArabicFontManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    def _init(self):
        self.font_name = 'Helvetica'; self.font_bold = 'Helvetica-Bold'; self.ready = False
        if not REPORTLAB_AVAILABLE: return
        paths = [os.path.join(FONT_DIR, "Amiri-Regular.ttf"), "Amiri-Regular.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        for p in paths:
            if os.path.exists(p) and self._reg(p): return
        for url, fn in FONT_URLS:
            try:
                t = os.path.join(FONT_DIR, fn)
                if not os.path.exists(t): urllib.request.urlretrieve(url, t)
                if self._reg(t): return
            except Exception: continue
    def _reg(self, path):
        try:
            pdfmetrics.registerFont(TTFont('TaworArabic', path))
            self.font_name = 'TaworArabic'; self.font_bold = 'TaworArabic'; self.ready = True
            return True
        except Exception: return False

font_mgr = ArabicFontManager()

class ArabicProcessor:
    @staticmethod
    @lru_cache(maxsize=5000)
    def fix(text):
        if text is None or text == "": return ""
        text = str(text)
        if not ARABIC_AVAILABLE: return text
        try: return get_display(arabic_reshaper.reshape(text), base_dir='R')
        except Exception: return text
arp = ArabicProcessor()
def ar(text): return arp.fix(text)

# ═══ مكتبة الأعلاف ═══
BIG_FEEDS_LIBRARY = {
"🌾 الحبوب ومصادر الطاقة": {
    "ذرة صفراء": {"CP":8.5,"DC":0.85,"SE":80,"NDF":9.5,"ADF":3.2,"EE":3.8,"ASH":1.3,"Ca":0.02,"P":0.27},
    "ذرة بيضاء": {"CP":8.8,"DC":0.83,"SE":78,"NDF":10.2,"ADF":3.5,"EE":3.5,"ASH":1.4,"Ca":0.02,"P":0.26},
    "ذرة شامية": {"CP":8.3,"DC":0.86,"SE":82,"NDF":9,"ADF":3,"EE":4,"ASH":1.2,"Ca":0.02,"P":0.28},
    "شعير مطحون": {"CP":11.5,"DC":0.8,"SE":71,"NDF":18.5,"ADF":7.5,"EE":2.2,"ASH":2.5,"Ca":0.05,"P":0.35},
    "شعير كامل": {"CP":10.8,"DC":0.75,"SE":68,"NDF":22,"ADF":9,"EE":2,"ASH":2.8,"Ca":0.05,"P":0.33},
    "سورجم (فتريتة)": {"CP":10,"DC":0.78,"SE":70,"NDF":12.5,"ADF":5.5,"EE":3,"ASH":1.8,"Ca":0.03,"P":0.3},
    "قمح محلي": {"CP":12,"DC":0.85,"SE":75,"NDF":11.5,"ADF":3.8,"EE":2,"ASH":1.6,"Ca":0.04,"P":0.32},
    "قمح مستورد": {"CP":11.5,"DC":0.87,"SE":78,"NDF":11,"ADF":3.5,"EE":1.9,"ASH":1.5,"Ca":0.04,"P":0.33},
    "جريش أرز": {"CP":7.8,"DC":0.82,"SE":82,"NDF":5.5,"ADF":2.5,"EE":8.5,"ASH":4.2,"Ca":0.06,"P":0.3},
    "دخن محلي": {"CP":11,"DC":0.75,"SE":68,"NDF":15.5,"ADF":6.5,"EE":4,"ASH":2.2,"Ca":0.05,"P":0.31},
    "شوفان علفي": {"CP":11,"DC":0.76,"SE":62,"NDF":27.5,"ADF":13.5,"EE":5,"ASH":3,"Ca":0.08,"P":0.35},
    "كسرة خبز": {"CP":10.5,"DC":0.82,"SE":75,"NDF":8,"ADF":3.5,"EE":5.5,"ASH":3.5,"Ca":0.1,"P":0.2},
    "بسكويت مكسر": {"CP":8.5,"DC":0.85,"SE":85,"NDF":4,"ADF":2,"EE":12,"ASH":2.5,"Ca":0.08,"P":0.18},
},
"🌱 الأكساب ومصادر البروتين": {
    "أمباز الفول السوداني": {"CP":46,"DC":0.88,"SE":73,"NDF":15.5,"ADF":8.5,"EE":1.5,"ASH":5.5,"Ca":0.2,"P":0.65},
    "كسب فول صويا 44%": {"CP":44,"DC":0.9,"SE":74,"NDF":13.5,"ADF":8,"EE":1.8,"ASH":6,"Ca":0.35,"P":0.65},
    "كسب فول صويا 48%": {"CP":48,"DC":0.91,"SE":76,"NDF":12,"ADF":7,"EE":1.5,"ASH":6.2,"Ca":0.35,"P":0.65},
    "كسب فول صويا 46%": {"CP":46,"DC":0.905,"SE":75,"NDF":12.5,"ADF":7.5,"EE":1.6,"ASH":6.1,"Ca":0.35,"P":0.65},
    "كسب عباد الشمس 36%": {"CP":36,"DC":0.76,"SE":42,"NDF":38.5,"ADF":25.5,"EE":2.5,"ASH":6.5,"Ca":0.4,"P":1},
    "كسب عباد الشمس 32%": {"CP":32,"DC":0.72,"SE":38,"NDF":42,"ADF":28,"EE":2,"ASH":7,"Ca":0.42,"P":0.95},
    "كسب بذور القطن": {"CP":41,"DC":0.78,"SE":55,"NDF":24.5,"ADF":15.5,"EE":1.2,"ASH":6.5,"Ca":0.2,"P":1.1},
    "كسب بذور الكتان": {"CP":32,"DC":0.82,"SE":65,"NDF":18.5,"ADF":10.5,"EE":2.8,"ASH":5.8,"Ca":0.35,"P":0.85},
    "كسب السمسم": {"CP":42,"DC":0.84,"SE":70,"NDF":14.5,"ADF":9.5,"EE":8.5,"ASH":12.5,"Ca":2,"P":1.2},
    "كسب جلوتين 60%": {"CP":60,"DC":0.92,"SE":85,"NDF":8.5,"ADF":5.5,"EE":2.5,"ASH":3.5,"Ca":0.15,"P":0.5},
    "كسب جلوتين 40%": {"CP":40,"DC":0.88,"SE":72,"NDF":15,"ADF":8,"EE":3,"ASH":5,"Ca":0.18,"P":0.55},
    "كسب نواة النخيل": {"CP":16,"DC":0.65,"SE":52,"NDF":55.5,"ADF":35.5,"EE":6.5,"ASH":4.5,"Ca":0.3,"P":0.55},
    "كسب بذور العنب": {"CP":12,"DC":0.55,"SE":30,"NDF":45,"ADF":32,"EE":7.5,"ASH":6,"Ca":0.25,"P":0.4},
    "كسب بذور القرطم": {"CP":24,"DC":0.7,"SE":45,"NDF":35,"ADF":22,"EE":2,"ASH":6,"Ca":0.35,"P":0.75},
    "كسب الكانولا": {"CP":36,"DC":0.82,"SE":60,"NDF":28,"ADF":18,"EE":3.5,"ASH":6.5,"Ca":0.65,"P":1.1},
    "كسب الأفوكادو": {"CP":18,"DC":0.65,"SE":50,"NDF":40,"ADF":28,"EE":8,"ASH":5.5,"Ca":0.3,"P":0.45},
},
"🚜 المخلفات الزراعية": {
    "نخالة قمح (ردة)": {"CP":15,"DC":0.72,"SE":45,"NDF":35.5,"ADF":12.5,"EE":3.5,"ASH":5.5,"Ca":0.12,"P":1.1},
    "نخالة ذرة": {"CP":9.5,"DC":0.65,"SE":40,"NDF":40,"ADF":15,"EE":4,"ASH":2,"Ca":0.1,"P":0.75},
    "البرسيم الجاف": {"CP":16.5,"DC":0.6,"SE":35,"NDF":42.5,"ADF":32.5,"EE":2,"ASH":10.5,"Ca":1.5,"P":0.25},
    "برسيم حجازي": {"CP":18,"DC":0.62,"SE":38,"NDF":40,"ADF":30,"EE":2.2,"ASH":11,"Ca":1.6,"P":0.26},
    "مولاس قصب السكر": {"CP":4,"DC":0.95,"SE":50,"NDF":1.5,"ADF":0.8,"EE":0.5,"ASH":8.5,"Ca":0.7,"P":0.05},
    "تبن قمح": {"CP":3.2,"DC":0.35,"SE":18,"NDF":72.5,"ADF":45.5,"EE":1.5,"ASH":8.5,"Ca":0.3,"P":0.08},
    "تبن فول": {"CP":4.5,"DC":0.4,"SE":22,"NDF":68,"ADF":42,"EE":1.2,"ASH":7.5,"Ca":0.35,"P":0.1},
    "قشر فول سوداني": {"CP":5,"DC":0.3,"SE":15,"NDF":65.5,"ADF":42.5,"EE":1,"ASH":5.5,"Ca":0.25,"P":0.1},
    "سرسة الأرز": {"CP":2.5,"DC":0.25,"SE":12,"NDF":68.5,"ADF":48.5,"EE":12.5,"ASH":15.5,"Ca":0.15,"P":0.08},
    "قش أرز": {"CP":3.5,"DC":0.3,"SE":15,"NDF":70,"ADF":45,"EE":1.5,"ASH":12,"Ca":0.2,"P":0.06},
    "مخلفات النخيل": {"CP":6.5,"DC":0.7,"SE":60,"NDF":25,"ADF":15,"EE":5,"ASH":3.5,"Ca":0.15,"P":0.15},
    "قشور الفول السوداني": {"CP":6.5,"DC":0.4,"SE":22,"NDF":58,"ADF":38,"EE":2.5,"ASH":4,"Ca":0.2,"P":0.12},
},
"🧬 مصادر البروتين الحيواني": {
    "مسحوق أسماك 60%": {"CP":60,"DC":0.85,"SE":65,"NDF":2.5,"ADF":1.5,"EE":8.5,"ASH":22.5,"Ca":5.5,"P":3.2},
    "مسحوق أسماك 72%": {"CP":72,"DC":0.9,"SE":72,"NDF":2,"ADF":1,"EE":9.5,"ASH":18.5,"Ca":4.8,"P":2.8},
    "مسحوق اللحم والعظم": {"CP":50,"DC":0.75,"SE":50,"NDF":3.5,"ADF":2.5,"EE":10.5,"ASH":32.5,"Ca":9,"P":4.5},
    "مسحوق الدم": {"CP":80,"DC":0.65,"SE":55,"NDF":1,"ADF":0.5,"EE":1.5,"ASH":6,"Ca":0.3,"P":0.3},
    "مسحوق ريش": {"CP":82,"DC":0.7,"SE":60,"NDF":1.5,"ADF":1,"EE":3,"ASH":4,"Ca":0.25,"P":0.35},
    "مسحوق مخلفات دواجن": {"CP":55,"DC":0.78,"SE":58,"NDF":5,"ADF":3,"EE":12,"ASH":15,"Ca":3,"P":1.8},
    "مركزات دواجن": {"CP":40,"DC":0.85,"SE":60,"NDF":8.5,"ADF":4.5,"EE":3.5,"ASH":12.5,"Ca":2.5,"P":1.2},
    "مركزات مواشي": {"CP":36,"DC":0.8,"SE":55,"NDF":15.5,"ADF":8.5,"EE":3,"ASH":15.5,"Ca":3,"P":1.5},
    "بروتين بلازما الدم": {"CP":78,"DC":0.9,"SE":62,"NDF":0.5,"ADF":0,"EE":2,"ASH":10,"Ca":0.15,"P":0.2},
},
"🌿 الأعلاف الخضراء المائية": {
    "أزولا مجففة": {"CP":24,"DC":0.65,"SE":45,"NDF":38,"ADF":25,"EE":3.5,"ASH":18,"Ca":2,"P":0.6},
    "سبيرولينا": {"CP":60,"DC":0.85,"SE":65,"NDF":5,"ADF":3,"EE":6,"ASH":10,"Ca":1.2,"P":0.9},
    "كلوريلا": {"CP":55,"DC":0.8,"SE":60,"NDF":6,"ADF":3.5,"EE":8,"ASH":12,"Ca":0.5,"P":1.2},
    "طحالب بحرية": {"CP":15,"DC":0.6,"SE":30,"NDF":25,"ADF":15,"EE":2,"ASH":30,"Ca":1.5,"P":0.3},
},
"🌰 الزيوت النباتية والحيوانية": {
    "زيت ذرة": {"CP":0,"DC":0,"SE":220,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"طاقة عالية 9000 kcal/kg، غني بأوميغا 6","max_poultry":6,"max_ruminant":5,"max_fish":10,"max_horse":8,"source":"NRC 2012"},
    "زيت فول الصويا": {"CP":0,"DC":0,"SE":215,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"أشهر زيوت الأعلاف، طاقة 8800 kcal/kg","max_poultry":8,"max_ruminant":5,"max_fish":12,"max_horse":10,"source":"Ross 308"},
    "زيت عباد الشمس": {"CP":0,"DC":0,"SE":210,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"غني بأوميغا 6، طاقة 8500 kcal/kg","max_poultry":6,"max_ruminant":4,"max_fish":8,"max_horse":8,"source":"NRC 2007"},
    "زيت بذرة القطن": {"CP":0,"DC":0,"SE":200,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"يحتوي جوسيبول (يجب معادلة)","max_poultry":3,"max_ruminant":5,"max_fish":6,"max_horse":5,"source":"NRC 2012"},
    "زيت الكتان": {"CP":0,"DC":0,"SE":205,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"غني جداً بأوميغا 3، ممتاز للخيول","max_poultry":3,"max_ruminant":3,"max_fish":6,"max_horse":8,"source":"NRC 2007"},
    "زيت جوز الهند": {"CP":0,"DC":0,"SE":230,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"MCT، سهل الهضم","max_poultry":5,"max_ruminant":3,"max_fish":8,"max_horse":6,"source":"NRC 2012"},
    "زيت النخيل": {"CP":0,"DC":0,"SE":215,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"مقاوم للأكسدة، 8700 kcal/kg","max_poultry":6,"max_ruminant":5,"max_fish":8,"max_horse":8,"source":"NRC 2012"},
    "زيت الكانولا": {"CP":0,"DC":0,"SE":200,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"متوازن أوميغا 3 و6","max_poultry":5,"max_ruminant":5,"max_fish":8,"max_horse":6,"source":"NRC 2012"},
    "زيت السمسم": {"CP":0,"DC":0,"SE":205,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"مضادات أكسدة طبيعية","max_poultry":4,"max_ruminant":3,"max_fish":6,"max_horse":5,"source":"NRC 2007"},
    "زيت الزيتون": {"CP":0,"DC":0,"SE":210,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"أوميغا 9، مضاد أكسدة قوي","max_poultry":4,"max_ruminant":4,"max_fish":5,"max_horse":5,"source":"INRA 2018"},
    "زيت الأفوكادو": {"CP":0,"DC":0,"SE":210,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"فيتامين E عالي","max_poultry":3,"max_ruminant":3,"max_fish":4,"max_horse":4,"source":"NRC 2012"},
    "زيت القرطم": {"CP":0,"DC":0,"SE":205,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"أوميغا 6 بنسبة 75%","max_poultry":4,"max_ruminant":3,"max_fish":5,"max_horse":5,"source":"NRC 2012"},
    "زيت الفول السوداني": {"CP":0,"DC":0,"SE":210,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"طاقة 8900 kcal/kg","max_poultry":5,"max_ruminant":4,"max_fish":6,"max_horse":6,"source":"NRC 2012"},
    "شحم حيواني (Tallow)": {"CP":0,"DC":0,"SE":230,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"9500 kcal/kg، صلب","max_poultry":6,"max_ruminant":5,"max_fish":6,"max_horse":8,"source":"NRC 2012"},
    "سمن حيواني (Lard)": {"CP":0,"DC":0,"SE":225,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"يجب تجنبه للحيوانات الحلال","max_poultry":5,"max_ruminant":0,"max_fish":5,"max_horse":6,"source":"NRC 2012"},
    "دهن الدجاج": {"CP":0,"DC":0,"SE":225,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"شحم دواجن معاد تدويره","max_poultry":6,"max_ruminant":0,"max_fish":5,"max_horse":6,"source":"NRC 2012"},
    "زيت السمك (Fish Oil)": {"CP":0,"DC":0,"SE":235,"NDF":0,"ADF":0,"EE":100,"ASH":0,"Ca":0,"P":0,"desc":"EPA/DHA، ممتاز للأسماك","max_poultry":2,"max_ruminant":2,"max_fish":8,"max_horse":3,"source":"NRC Fish"},
},
"🧪 الأحماض الأمينية": {
    "ليسين نقي": {"CP":94,"DC":1,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0.5,"Ca":0,"P":0},
    "ليسين سلفات": {"CP":79,"DC":1,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0.5,"Ca":0,"P":0},
    "ميثيونين نقي": {"CP":58,"DC":1,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0.3,"Ca":0,"P":0},
    "ميثيونين هيدروكسي": {"CP":88,"DC":1,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0.2,"Ca":0,"P":0},
    "ثريونين نقي": {"CP":72,"DC":1,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0.2,"Ca":0,"P":0},
    "تريبتوفان نقي": {"CP":85,"DC":1,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0.1,"Ca":0,"P":0},
    "فالين نقي": {"CP":90,"DC":1,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0.1,"Ca":0,"P":0},
    "أرجينين": {"CP":98,"DC":1,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0.2,"Ca":0,"P":0},
    "هيستيدين": {"CP":96,"DC":1,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0.2,"Ca":0,"P":0},
    "إيزوليوسين": {"CP":90,"DC":1,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0.1,"Ca":0,"P":0},
    "ليوسين": {"CP":90,"DC":1,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0.1,"Ca":0,"P":0},
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
    "إنزيم بروتييز": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":2,"Ca":0,"P":0},
    "إنزيم أميليز": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":3,"Ca":0,"P":0},
    "كبريتات الحديدوز": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":98,"Ca":0,"P":0},
    "مستخلص الخمائر MOS": {"CP":12,"DC":0.5,"SE":10,"NDF":2.5,"ADF":1.5,"EE":1.5,"ASH":8.5,"Ca":0.1,"P":0.2},
    "خمائر حية": {"CP":45,"DC":0.75,"SE":30,"NDF":8,"ADF":4,"EE":1,"ASH":8,"Ca":0.15,"P":1.2},
    "بروبيوتيك": {"CP":15,"DC":0.6,"SE":20,"NDF":5,"ADF":3,"EE":2,"ASH":15,"Ca":0.3,"P":0.5},
    "بريبيوتيك FOS": {"CP":0,"DC":0,"SE":40,"NDF":0,"ADF":0,"EE":0,"ASH":2,"Ca":0,"P":0},
},
"🪨 الأملاح والمعادن": {
    "الحجر الجيري": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":99.5,"Ca":38,"P":0},
    "فوسفات ثنائي الكالسيوم": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":98.5,"Ca":23,"P":18},
    "فوسفات أحادي الكالسيوم": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":99,"Ca":17,"P":22},
    "ملح الطعام": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":99.9,"Ca":0,"P":0},
    "بيكربونات الصوديوم": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":99,"Ca":0,"P":0},
    "أكسيد المغنيسيوم": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":99.5,"Ca":0,"P":0},
    "كبريتات المغنيسيوم": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":98,"Ca":0,"P":0},
    "يوريا علفية": {"CP":287,"DC":0.95,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":1,"Ca":0,"P":0},
    "مضاد سموم فطرية": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":85,"Ca":0,"P":0},
    "مضاد أكسدة BHT": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":100,"Ca":0,"P":0},
    "مضاد حيوي وقائي": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":100,"Ca":0,"P":0},
    "كولين كلوريد": {"CP":0,"DC":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":100,"Ca":0,"P":0},
},
}

# ═══ معايير الزيوت ═══
MAX_OIL_PERCENTAGE = {
"دواجن_بادي":{"max":8,"optimal":5,"source":"Ross 308 2020"},
"دواجن_نامي":{"max":7,"optimal":4.5,"source":"Ross 308 2020"},
"دواجن_ناهي":{"max":7,"optimal":4,"source":"Ross 308 2020"},
"دواجن_بياض":{"max":5,"optimal":2.5,"source":"NRC 1994"},
"سمان_بادي":{"max":6,"optimal":4,"source":"NRC Quail"},
"سمان_بياض":{"max":5,"optimal":2.5,"source":"NRC Quail"},
"أبقار_حليب_عالي":{"max":6,"optimal":4,"source":"NRC 2001"},
"أبقار_حليب_متوسط":{"max":5,"optimal":3.5,"source":"NRC 2001"},
"أبقار_حليب_منخفض":{"max":5,"optimal":3,"source":"NRC 2001"},
"أبقار_تسمين_مكثف":{"max":6,"optimal":4.5,"source":"NRC 2001"},
"أبقار_تسمين_عادي":{"max":5,"optimal":3.5,"source":"NRC 2001"},
"أغنام_تسمين_مكثف":{"max":5,"optimal":3.5,"source":"NRC 2007"},
"أغنام_تسمين_عادي":{"max":4.5,"optimal":3,"source":"NRC 2007"},
"أغنام_حليب":{"max":5,"optimal":3.5,"source":"NRC 2007"},
"أغنام_صيانة":{"max":3.5,"optimal":2,"source":"NRC 2007"},
"ماعز_تسمين":{"max":5,"optimal":3.5,"source":"NRC 2007"},
"ماعز_حليب":{"max":5,"optimal":3.5,"source":"NRC 2007"},
"ماعز_صيانة":{"max":3.5,"optimal":2,"source":"NRC 2007"},
"إبل_نمو":{"max":5,"optimal":3.5,"source":"FAO 2010"},
"إبل_تسمين":{"max":6,"optimal":4,"source":"FAO 2010"},
"إبل_حليب":{"max":5,"optimal":3.5,"source":"FAO 2010"},
"إبل_سباق":{"max":8,"optimal":6,"source":"FAO 2010"},
"إبل_صيانة":{"max":3.5,"optimal":2,"source":"FAO 2010"},
"خيول_رياضة_مكثف":{"max":10,"optimal":7,"source":"NRC 2007"},
"خيول_رياضة_عادي":{"max":8,"optimal":5,"source":"NRC 2007"},
"خيول_نمو":{"max":8,"optimal":5,"source":"NRC 2007"},
"خيول_مرضعات":{"max":8,"optimal":5.5,"source":"NRC 2007"},
"خيول_صيانة":{"max":5,"optimal":3,"source":"NRC 2007"},
"أسماك_بادئ":{"max":15,"optimal":10,"source":"NRC Fish"},
"أسماك_نمو":{"max":12,"optimal":8,"source":"NRC Fish"},
"أسماك_تسمين":{"max":12,"optimal":8,"source":"NRC Fish"},
"أسماك_أمهات":{"max":15,"optimal":10,"source":"NRC Fish"},
}

OIL_CATEGORIES = {
"زيوت غنية بأوميغا 6": ["زيت ذرة","زيت عباد الشمس","زيت القرطم","زيت فول الصويا"],
"زيوت غنية بأوميغا 3": ["زيت الكتان","زيت الكانولا","زيت السمك (Fish Oil)"],
"زيوت متوازنة": ["زيت النخيل","زيت جوز الهند","زيت الزيتون","زيت السمسم","زيت الفول السوداني","زيت الأفوكادو"],
"دهون حيوانية": ["شحم حيواني (Tallow)","سمن حيواني (Lard)","دهن الدجاج"],
"زيوت تحتاج مراجعة": ["زيت بذرة القطن","سمن حيواني (Lard)"],
}

def get_oil_standard(k):
    if k in MAX_OIL_PERCENTAGE: return MAX_OIL_PERCENTAGE[k]
    for key in MAX_OIL_PERCENTAGE:
        if k and (k in key or key in k): return MAX_OIL_PERCENTAGE[key]
    return {"max":5,"optimal":3,"source":"معيار عام — NRC"}

def get_oil_ingredients():
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت النباتية والحيوانية", {})

def get_ingredient_data(name):
    for cat in BIG_FEEDS_LIBRARY.values():
        if name in cat: return cat[name]
    return None

# ═══ الاحتياجات ═══
@dataclass
class AnimalRequirement:
    DP:float; CP:float; SE:float; NDF:float; ADF:float
    EE:float; ASH:float; Ca:float; P:float
    name_ar:str=""; note:str=""

def get_cattle_requirements(pt, milk_yield=20.0, weight_kg=500.0):
    if pt=="حليب_عالي":
        dp=12.5+milk_yield*0.30; cp=dp/0.70
        return AnimalRequirement(round(dp,2),round(cp,2),round(60+milk_yield*0.35,1),30,19,5.5,8,round(0.55+milk_yield*0.003,3),round(0.33+milk_yield*0.0015,3),"أبقار حلابة عالية",f"إنتاج {milk_yield} كجم/يوم")
    if pt=="حليب_متوسط":
        dp=11+milk_yield*0.25; cp=dp/0.72
        return AnimalRequirement(round(dp,2),round(cp,2),round(55+milk_yield*0.30,1),33,21,4.5,8,round(0.50+milk_yield*0.0025,3),round(0.30+milk_yield*0.0012,3),"أبقار حلابة متوسطة",f"إنتاج {milk_yield} كجم/يوم")
    if pt=="حليب_منخفض":
        dp=9.5+milk_yield*0.20; cp=dp/0.75
        return AnimalRequirement(round(dp,2),round(cp,2),round(50+milk_yield*0.25,1),38,24,4,8.5,round(0.45+milk_yield*0.002,3),round(0.28+milk_yield*0.001,3),"أبقار حلابة منخفضة",f"إنتاج {milk_yield} كجم/يوم")
    if pt=="تسمين_مكثف":
        return AnimalRequirement(11.5,14.5,72,32,20,4.5,7.5,0.65,0.38,"تسمين عجول مكثف","ADG >1.3 كجم/يوم")
    if pt=="تسمين_عادي":
        return AnimalRequirement(9.5,12,65,38,24,4,7.5,0.55,0.32,"تسمين عجول عادي","ADG ~0.8 كجم/يوم")
    if pt=="حمل_أخير":
        return AnimalRequirement(11.5,14.5,67,35,22,4.2,8,0.7,0.42,"حمل آخر (شهر 7-9)","دفع غذائي جنيني")
    return AnimalRequirement(7.5,10,53,45,28,3,8.5,0.42,0.26,"أبقار صيانة","بدون إنتاج")

def get_sheep_requirements(pt, is_male=True, weight_kg=50.0, litter_size=1):
    if is_male:
        if pt=="تسمين_مكثف": return AnimalRequirement(11.5,14.5,64,28,17,4,8,0.65,0.36,"تسمين حملان مكثف","ADG >250 جم/يوم")
        if pt=="تسمين_عادي": return AnimalRequirement(9.5,12,59,33,21,3.6,8,0.55,0.32,"تسمين حملان عادي","ADG ~180 جم/يوم")
        return AnimalRequirement(8.5,11,55,38,24,3.2,8.5,0.5,0.3,"حملان تيد","تسمين نهائي")
    else:
        if pt=="مرضعات":
            dp=10.5+(litter_size-1)*1.5; cp=dp/0.72
            return AnimalRequirement(round(dp,2),round(cp,2),round(60+(litter_size-1)*5,1),30,19,4.5,8.5,round(0.65+(litter_size-1)*0.10,3),round(0.38+(litter_size-1)*0.05,3),f"نعاج مرضعات ({litter_size} مواليد)","إنتاج حليب مرتفع")
        if pt=="حامل_أخير": return AnimalRequirement(10.5,13.5,62,32,20,3.8,8,0.6,0.35,"نعاج حامل (4-5)","تغذية جنين")
        if pt=="حامل_متوسط": return AnimalRequirement(8.5,11,55,38,24,3.4,8,0.5,0.3,"نعاج حامل (1-3)","نمو جنيني مبكر")
        return AnimalRequirement(7.2,9.5,48,45,28,3,8.5,0.42,0.26,"نعاج صيانة","بدون إنتاج")

def get_goat_requirements(pt, is_male=True, milk_yield=2.0):
    if is_male:
        if pt=="تسمين_جديان": return AnimalRequirement(11,14,62,30,19,3.8,8,0.62,0.34,"تسمين جديان","نمو سريع")
        return AnimalRequirement(9,11.5,57,36,22,3.5,8,0.55,0.3,"تيوس تسمين","تسمين نهائي")
    else:
        if pt=="حلابة_عالي":
            dp=11.5+milk_yield*0.45; cp=dp/0.70
            return AnimalRequirement(round(dp,2),round(cp,2),round(58+milk_yield*0.45,1),29,18,4.5,8.5,round(0.60+milk_yield*0.008,3),round(0.35+milk_yield*0.004,3),f"عنزات حلابة عالي","إدرار عالي")
        if pt=="حلابة_متوسط":
            dp=10+milk_yield*0.35; cp=dp/0.72
            return AnimalRequirement(round(dp,2),round(cp,2),round(55+milk_yield*0.40,1),32,20,4,8.5,round(0.55+milk_yield*0.006,3),round(0.32+milk_yield*0.003,3),f"عنزات حلابة متوسط","إدرار متوسط")
        if pt=="حامل_أخير": return AnimalRequirement(10,13,60,33,21,3.8,8,0.6,0.35,"عنزات حامل","دفع غذائي")
        return AnimalRequirement(6.8,9,46,46,28,3,8.5,0.42,0.26,"عنزات صيانة","بدون إنتاج")

def get_camel_requirements(pt, weight_kg=400.0, milk_yield=5.0):
    dm=weight_kg*0.025
    if pt=="نمو": return AnimalRequirement(10.5,13.5,60,38,24,4,8,0.65,0.38,"إبل نمو (حوار)",f"وزن {weight_kg} كجم")
    if pt=="تسمين": return AnimalRequirement(9.5,12,65,35,22,4.5,7.5,0.6,0.35,"إبل تسمين",f"وزن {weight_kg} كجم")
    if pt=="حليب":
        dp=12+milk_yield*0.25; cp=dp/0.70
        return AnimalRequirement(round(dp,2),round(cp,2),round(62+milk_yield*0.40,1),32,20,5,8.5,round(0.70+milk_yield*0.006,3),round(0.40+milk_yield*0.003,3),f"إبل حلابة ({milk_yield} لتر)","دهن الحليب 3-5%")
    if pt=="سباق": return AnimalRequirement(14,17,72,28,17,6,9,0.85,0.5,"إبل سباق","طاقة عالية")
    return AnimalRequirement(7,9,48,48,30,3.5,9,0.42,0.26,"إبل صيانة",f"وزن {weight_kg} كجم")

def get_horse_requirements(pt, weight_kg=450.0):
    if pt=="رياضة_مكثف": return AnimalRequirement(10.5,13.5,70,30,18,7,7.5,0.7,0.4,"خيول رياضة مكثف","جهد عالي")
    if pt=="رياضة_عادي": return AnimalRequirement(9,11.5,63,36,22,5,7.5,0.55,0.32,"خيول رياضة عادي","نشاط متوسط")
    if pt=="نمو_أمهار": return AnimalRequirement(12,15,65,30,18,5,8,0.75,0.42,"أمهار نمو","نمو هيكلي")
    if pt=="مرضعات": return AnimalRequirement(12.5,16,68,32,20,5.5,8,0.8,0.45,"فرسات مرضعات","حليب مرتفع")
    return AnimalRequirement(7.2,9.5,53,46,29,3.5,8,0.45,0.28,"خيول صيانة","بدون جهد")

def get_poultry_requirements(strain, age_weeks=1):
    if strain=="لاحم":
        if age_weeks<=1: return AnimalRequirement(20,23,76,8,4,5,6.5,1,0.5,"بادي لاحم","Energy 3000 kcal/kg")
        if age_weeks<=3: return AnimalRequirement(18.5,21,74,9,5,5,6,0.9,0.45,"نامي لاحم","Energy 3100 kcal/kg")
        if age_weeks<=5: return AnimalRequirement(17,19.5,75,10,5.5,4.5,6,0.87,0.43,"ناهي لاحم (4-5)","Energy 3150")
        return AnimalRequirement(16.5,19,75,10,5.5,4.5,6,0.85,0.42,"ناهي لاحم (6+)","Energy 3200")
    else:
        if age_weeks<=6: return AnimalRequirement(17,20,72,10,5.5,4,7,1,0.5,"بادي بياض","تحضير للبيض")
        if age_weeks<=18: return AnimalRequirement(14.5,17,70,12,6.5,4,9,1.5,0.45,"نامي بياض","نمو هيكلي")
        return AnimalRequirement(15.5,18,72,11,6,4.2,11.5,3.8,0.45,"بياض إنتاجي","إنتاج بيض")

def get_quail_requirements(strain, age_weeks=1):
    if strain=="بياض": return AnimalRequirement(15,18,68,11,5.5,4.5,9,2.5,0.45,"سمان بياض","إنتاج بيض")
    if age_weeks<=2: return AnimalRequirement(20.5,24,74,8,4,5.5,6.5,1,0.55,"سمان بادي","نمو سريع")
    if age_weeks<=4: return AnimalRequirement(18.5,22,72,9,4.5,5,6,0.9,0.5,"سمان نامي","نمو متوسط")
    return AnimalRequirement(17,20,70,10,5,4.5,6,0.85,0.45,"سمان ناهي","تسمين نهائي")

def get_fish_requirements(species, stage):
    if "زريعة" in stage or "بادئ" in stage: return AnimalRequirement(32,40,72,8,4,10,11,1.5,0.9,f"{species} — بادئ","بروتين عالٍ")
    if "نمو" in stage: return AnimalRequirement(25,32,70,12,6,8,9,1,0.7,f"{species} — نمو","بروتين متوسط")
    return AnimalRequirement(22,28,68,13,7,8,9.5,0.9,0.65,f"{species} — تسمين","طاقة عالٍ")

def requirement_to_standard(req):
    return {"CP":req.CP,"DP":req.DP,"SE":req.SE,"NDF":req.NDF,"ADF":req.ADF,"EE":req.EE,"ASH":req.ASH,"Ca":req.Ca,"P":req.P}

# ═══ الحسابات ═══
def compute_formula_nutrients(formula):
    t = {"CP":0,"DP":0,"SE":0,"NDF":0,"ADF":0,"EE":0,"ASH":0,"Ca":0,"P":0}
    for ing, pct in formula.items():
        d = get_ingredient_data(ing)
        if d is None: continue
        f = pct/100.0
        t["CP"] += f*d.get("CP",0)
        t["DP"] += f*d.get("CP",0)*d.get("DC",0)
        t["SE"] += f*d.get("SE",0)
        t["NDF"] += f*d.get("NDF",0)
        t["ADF"] += f*d.get("ADF",0)
        t["EE"] += f*d.get("EE",0)
        t["ASH"] += f*d.get("ASH",0)
        t["Ca"] += f*d.get("Ca",0)
        t["P"] += f*d.get("P",0)
    return t

def compute_energy_kcal(formula):
    t = compute_formula_nutrients(formula)
    ee = t["EE"]/100.0*9000
    cp = t["CP"]/100.0*4000
    carb = max(0,100-(t["EE"]+t["CP"]+t["ASH"]))/100.0*3500
    return round(ee+cp+carb, 0)

def compute_total_oil_percentage(formula):
    oils = set(get_oil_ingredients().keys())
    return sum(pct for ing,pct in formula.items() if ing in oils)

def validate_oil_percentage(formula, standard_key):
    total = compute_total_oil_percentage(formula)
    std = get_oil_standard(standard_key)
    status = "ok"
    if total>std["max"]: status="exceeded"
    elif total>std["optimal"]*1.2: status="high"
    return {"total":total,"max":std["max"],"optimal":std["optimal"],"source":std["source"],"status":status}

# ═══ التقييم (مُصلح #1) ═══
def evaluate_difference(pct_diff, nutrient=None):
    if nutrient in ("Ca","P"):
        if pct_diff==0: return {"label":"🎯 مطابق","color":"#0d5302","bg":"#c8e6c9","score":100}
        a = abs(pct_diff)
        if a<=3: return {"label":"🎯 مطابق","color":"#0d5302","bg":"#c8e6c9","score":100}
        if a<=8: return {"label":"🌟 ممتاز","color":"#1b5e20","bg":"#dcedc8","score":95}
        if a<=15: return {"label":"✅ جيد جداً","color":"#2e7d32","bg":"#e8f5e9","score":85}
        if a<=25: return {"label":"🟢 جيد","color":"#558b2f","bg":"#f1f8e9","score":75}
        if a<=40: return {"label":"⭐ مقبول","color":"#f9a825","bg":"#fff8e1","score":65}
        if a<=60: return {"label":"⚠️ مقبول بتحفظ","color":"#ef6c00","bg":"#fff3e0","score":50}
        return {"label":"❌ غير مطابق","color":"#c62828","bg":"#ffebee","score":20}
    a = abs(pct_diff)
    if a<=0.5: return {"label":"🎯 مطابق تماماً","color":"#0d5302","bg":"#c8e6c9","score":100}
    if a<=2: return {"label":"🌟 ممتاز","color":"#1b5e20","bg":"#dcedc8","score":95}
    if a<=5: return {"label":"✅ جيد جداً","color":"#2e7d32","bg":"#e8f5e9","score":85}
    if a<=10: return {"label":"🟢 جيد","color":"#558b2f","bg":"#f1f8e9","score":75}
    if a<=15: return {"label":"⭐ مقبول","color":"#f9a825","bg":"#fff8e1","score":65}
    if a<=25: return {"label":"⚠️ مقبول بتحفظ","color":"#ef6c00","bg":"#fff3e0","score":50}
    if a<=40: return {"label":"🟠 ضعيف","color":"#e65100","bg":"#ffe0b2","score":35}
    return {"label":"❌ غير مطابق","color":"#c62828","bg":"#ffebee","score":20}

def get_overall_rating(rows):
    if not rows: return {"label":"غير محدد","color":"#666","score":0}
    scores = [r.get("score",50) for r in rows]
    avg = sum(scores)/len(scores)
    if avg>=95: return {"label":"🏆 خلطة ممتازة","color":"#1b5e20","score":avg}
    if avg>=85: return {"label":"🌟 خلطة جيدة جداً","color":"#2e7d32","score":avg}
    if avg>=70: return {"label":"✅ خلطة جيدة","color":"#558b2f","score":avg}
    if avg>=55: return {"label":"⭐ خلطة مقبولة","color":"#f9a825","score":avg}
    return {"label":"⚠️ تحتاج تحسين","color":"#e65100","score":avg}

# ═══ المحرك (مُصلح #4) ═══
def auto_formulate_smart(available, prices, standard, standard_key, tolerance=0.3, max_iter=50):
    if not SCIPY_AVAILABLE: return {"success":False,"message":"scipy غير متوفرة"}
    ing_data = {}
    for ing in available:
        d = get_ingredient_data(ing)
        if d: ing_data[ing]=d
    valid = [i for i in available if i in ing_data]
    if len(valid)<3: return {"success":False,"message":"اختر 3 مكونات على الأقل"}
    n = len(valid)
    c = [float(prices.get(i,300)) for i in valid]
    rows = {}
    for nut in ["CP","SE","NDF","ADF","EE","ASH","Ca","P"]:
        rows[nut]=[ing_data[i].get(nut,0) for i in valid]
    rows["DP"]=[ing_data[i].get("CP",0)*ing_data[i].get("DC",0) for i in valid]
    targets = {k:float(standard.get(k,0)) for k in ["DP","SE","NDF","ADF","Ca","P"]}
    oil_std = get_oil_standard(standard_key); oil_max = oil_std["max"]
    bounds=[]
    for i in valid:
        if i in get_oil_ingredients(): bounds.append((0,min(oil_max*0.6,8)))
        elif "يوريا" in i: bounds.append((0,1))
        elif "مولاس" in i: bounds.append((0,10))
        elif "ملح الطعام" in i: bounds.append((0.3,0.7))
        elif "بيكربونات" in i: bounds.append((0,1.5))
        elif "مضاد سموم" in i: bounds.append((0.05,0.25))
        elif "بريمكس" in i: bounds.append((0.15,0.5))
        elif "إنزيم" in i: bounds.append((0.02,0.10))
        elif "الحجر الجيري" in i: bounds.append((0,8.5))
        elif "فوسفات" in i: bounds.append((0,2.5))
        elif "سرسة" in i or "قش" in i: bounds.append((0,8))
        elif "تبن" in i: bounds.append((0,25))
        else: bounds.append((0,100))
    oil_ind = [1.0 if i in get_oil_ingredients() else 0.0 for i in valid]
    has_oils = sum(oil_ind)>0
    def safe_lp(cv,aub,bub,aeq,beq,bd):
        try: return linprog(cv,A_ub=aub,b_ub=bub,A_eq=aeq,b_eq=beq,bounds=bd,method='highs',options={'presolve':True,'time_limit':15})
        except Exception: return OptimizeResult(success=False,x=None,fun=float('inf'))
    A_eq=[[1.0]*n,rows["DP"]]; b_eq=[100,targets["DP"]*100]
    A_ub=[[-1.0*x for x in rows["SE"]],[1.0*x for x in rows["NDF"]],[1.0*x for x in rows["ADF"]]]
    b_ub=[-1.0*targets["SE"]*100,targets["NDF"]*1.15*100,targets["ADF"]*1.15*100]
    if has_oils: A_ub.append(oil_ind); b_ub.append(oil_max*100)
    res = safe_lp(c,A_ub,b_ub,A_eq,b_eq,bounds)
    if not res.success:
        for relax in [1.05,1.10,1.20,1.30]:
            b_ub_r=[-1.0*targets["SE"]*100*(2-relax),targets["NDF"]*relax*100,targets["ADF"]*relax*100]
            if has_oils: b_ub_r.append(oil_max*100)
            res = safe_lp(c,A_ub,b_ub_r,A_eq,b_eq,bounds)
            if res.success: break
    if not res.success: return {"success":False,"message":"تعذر إيجاد حل — أضف مكونات"}
    best=None; best_score=float('inf')
    cur_dp,cur_se=targets["DP"],targets["SE"]
    cur_ndf,cur_adf=targets["NDF"],targets["ADF"]
    log=[]
    for it in range(max_iter):
        A_eq=[[1.0]*n,rows["DP"],rows["Ca"],rows["P"]]
        b_eq=[100,cur_dp*100,targets["Ca"]*100,targets["P"]*100]
        A_ub=[[-1.0*x for x in rows["SE"]],[1.0*x for x in rows["NDF"]],[1.0*x for x in rows["ADF"]]]
        b_ub=[-1.0*cur_se*100,cur_ndf*1.10*100,cur_adf*1.10*100]
        if has_oils: A_ub.append(oil_ind); b_ub.append(oil_max*100)
        res = safe_lp(c,A_ub,b_ub,A_eq,b_eq,bounds)
        if not res.success:
            A_eq2=[[1.0]*n,rows["DP"],rows["Ca"]]; b_eq2=[100,cur_dp*100,targets["Ca"]*100]
            res = safe_lp(c,A_ub,b_ub,A_eq2,b_eq2,bounds)
        if not res.success:
            cur_ndf*=1.05; cur_adf*=1.05
            log.append(f"تكرار {it+1}: تخفيف"); continue
        formula = {valid[i]:res.x[i] for i in range(n) if res.x[i]>0.001}
        actual = compute_formula_nutrients(formula)
        total_oil_actual = compute_total_oil_percentage(formula)
        errors={}
        for k in ["DP","SE","NDF","ADF","Ca","P"]:
            tv=targets.get(k,0); errors[k]=abs(actual.get(k,0)-tv)/tv if tv>0 else 0
        weights={"DP":5,"SE":3,"NDF":1.5,"ADF":1,"Ca":1,"P":1}
        score=sum(errors.get(k,0)*weights[k] for k in errors)
        log.append(f"تكرار {it+1}: DP={actual['DP']:.2f} SE={actual['SE']:.2f}")
        if score<best_score:
            best_score=score
            best={"success":True,"formula":formula,"cost":res.fun/100.0 if res.fun else 0,
                  "actual_nutrients":actual,
                  "dp_error":abs(actual["DP"]-targets["DP"]),
                  "se_error":abs(actual["SE"]-targets["SE"]),
                  "ndf_error":abs(actual["NDF"]-targets["NDF"]),
                  "adf_error":abs(actual["ADF"]-targets["ADF"]),
                  "ca_error":abs(actual.get("Ca",0)-targets["Ca"]),
                  "p_error":abs(actual.get("P",0)-targets["P"]),
                  "total_oil":total_oil_actual,"oil_std":oil_std,
                  "iterations":it+1,"log":log[-10:],"targets":targets}
        if (errors.get("DP",1)*100<=tolerance and errors.get("SE",1)*100<=tolerance*2 and
            errors.get("NDF",1)*100<=tolerance*5 and errors.get("Ca",1)*100<=tolerance*15):
            log.append(f"✅ مطابقة كاملة في التكرار {it+1}")
            best["perfect_match"]=True; break
        cur_dp += (targets["DP"]-actual["DP"])*0.25
        cur_se += (targets["SE"]-actual["SE"])*0.20
        cur_ndf += (targets["NDF"]-actual["NDF"])*0.15
        cur_adf += (targets["ADF"]-actual["ADF"])*0.15
        cur_dp=max(5,min(40,cur_dp)); cur_se=max(10,min(90,cur_se))
        cur_ndf=max(5,min(70,cur_ndf)); cur_adf=max(3,min(50,cur_adf))
    if best: best["log"]=log; return best
    return {"success":False,"message":"تعذر حل دقيق","log":log}

def auto_add_salts_and_minerals(animal_type, req=None):
    s={}
    if animal_type in ["أغنام","ماعز","أبقار","إبل"]: s["بيكربونات الصوديوم"]=0.75
    s["مضاد سموم فطرية"]=0.20; s["ملح الطعام"]=0.50
    if animal_type in ["دواجن","سمان"]:
        s["الحجر الجيري"]=8.0 if (req and req.Ca>2) else 1.5
        s["فوسفات ثنائي الكالسيوم"]=1.5; s["بريمكس تسمين دواجن"]=0.30
    elif animal_type=="أسماك":
        s["الحجر الجيري"]=1.0; s["فوسفات ثنائي الكالسيوم"]=1.5; s["بريمكس أسماك"]=0.30
    elif animal_type=="خيول":
        s["الحجر الجيري"]=1.5; s["فوسفات ثنائي الكالسيوم"]=1.5; s["بريمكس خيول"]=0.30
    elif animal_type=="إبل":
        s["الحجر الجيري"]=2.0; s["فوسفات ثنائي الكالسيوم"]=1.5; s["بريمكس إبل"]=0.30
    else:
        s["الحجر الجيري"]=2.0; s["فوسفات ثنائي الكالسيوم"]=1.5; s["بريمكس مجترات"]=0.30
    return s

# ═══ بدائل الحليب ═══
MILK_REPLACER_STANDARDS = {
"عجول (Calves)":{"CP":24,"Fat":24,"Lactose":45,"Lysine":2.1,"Ca":0.75,"P":0.70,"notes":"عمر 1-6 أسابيع، مادة جافة 12-15%"},
"حملان (Lambs)":{"CP":24,"Fat":24,"Lactose":40,"Lysine":2.1,"Ca":0.80,"P":0.70,"notes":"> 24% دهن"},
"جديان (Goat Kids)":{"CP":24,"Fat":24,"Lactose":42,"Lysine":2.1,"Ca":0.80,"P":0.70,"notes":"بديل الجديان"},
"إبل (Camel Calves)":{"CP":26,"Fat":28,"Lactose":38,"Lysine":2.3,"Ca":0.85,"P":0.75,"notes":"بروتين ودهن أعلى"},
"أمهار (Foals)":{"CP":22,"Fat":20,"Lactose":45,"Lysine":1.9,"Ca":0.90,"P":0.80,"notes":"توازن للخيول"},
}
MILK_REPLACER_INGREDIENTS = {
"حليب مجفف منزوع الدسم":{"CP":34,"Fat":1,"Lactose":52,"price":3200},
"حليب مجفف كامل الدسم":{"CP":26,"Fat":28,"Lactose":38,"price":3800},
"شرش حليب مجفف":{"CP":12,"Fat":1.5,"Lactose":75,"price":1800},
"بروتين شرش WPC 80%":{"CP":80,"Fat":5,"Lactose":8,"price":8500},
"كازين":{"CP":85,"Fat":2,"Lactose":2,"price":9000},
"مركز بروتين صويا":{"CP":66,"Fat":1,"Lactose":0,"price":2800},
"دقيق الصويا":{"CP":38,"Fat":20,"Lactose":0,"price":1500},
"زيت جوز الهند":{"CP":0,"Fat":100,"Lactose":0,"price":2200},
"زيت النخيل":{"CP":0,"Fat":100,"Lactose":0,"price":1200},
"دهن حيواني":{"CP":0,"Fat":100,"Lactose":0,"price":1000},
"مالتودكسترين":{"CP":0,"Fat":0,"Lactose":0,"price":900},
"لاكتوز نقي":{"CP":0,"Fat":0,"Lactose":100,"price":1400},
"ليسين L-Lysine":{"CP":94,"Fat":0,"Lactose":0,"price":4200},
"ميثيونين":{"CP":58,"Fat":0,"Lactose":0,"price":5800},
"بريمكس فيتامينات":{"CP":0,"Fat":0,"Lactose":0,"price":6500},
"كالسيوم كربونات":{"CP":0,"Fat":0,"Lactose":0,"price":200},
"فوسفات ثنائي الكالسيوم":{"CP":0,"Fat":0,"Lactose":0,"price":1100},
"ملح طعام":{"CP":0,"Fat":0,"Lactose":0,"price":150},
}

def formulate_milk_replacer(animal_type, target_volume_kg=100.0, selected=None):
    std = MILK_REPLACER_STANDARDS.get(animal_type)
    if not std: return {"success":False,"message":"غير مدعوم"}
    valid = [i for i in (selected or list(MILK_REPLACER_INGREDIENTS.keys())) if i in MILK_REPLACER_INGREDIENTS]
    if len(valid)<3: return {"success":False,"message":"اختر 3 مكونات على الأقل"}
    n=len(valid)
    c=[MILK_REPLACER_INGREDIENTS[i]["price"] for i in valid]
    bounds=[(0,100)]*n
    A_eq=[[1.0]*n,[MILK_REPLACER_INGREDIENTS[i]["CP"] for i in valid],[MILK_REPLACER_INGREDIENTS[i]["Fat"] for i in valid]]
    b_eq=[100,std["CP"]*100,std["Fat"]*100]
    try: res = linprog(c,A_eq=A_eq,b_eq=b_eq,bounds=bounds,method='highs')
    except Exception: return {"success":False,"message":"خطأ في المحرك"}
    if not res.success: return {"success":False,"message":"تعذر التركيب"}
    formula = {valid[i]:res.x[i] for i in range(n) if res.x[i]>0.001}
    actual = {"CP":0,"Fat":0,"Lactose":0}
    for ing, pct in formula.items():
        d = MILK_REPLACER_INGREDIENTS[ing]
        actual["CP"]+=pct/100.0*d["CP"]; actual["Fat"]+=pct/100.0*d["Fat"]; actual["Lactose"]+=pct/100.0*d["Lactose"]
    return {"success":True,"formula":formula,"cost_per_100kg":res.fun/100.0,"cost_per_kg":res.fun/10000.0,"standard":std,"actual":actual,"animal":animal_type}

# ═══ OCR ═══
def match_ingredient_name(text):
    if not text: return None
    tl = text.strip().lower()
    for cat in BIG_FEEDS_LIBRARY.values():
        for name in cat.keys():
            if name.lower() in tl or tl in name.lower(): return name
    kw = {"ذرة":"ذرة صفراء","corn":"ذرة صفراء","صويا":"كسب فول صويا 44%","شعير":"شعير مطحون",
          "قمح":"قمح محلي","سورجم":"سورجم (فتريتة)","نخالة":"نخالة قمح (ردة)","فول سوداني":"أمباز الفول السوداني",
          "قطن":"كسب بذور القطن","عباد":"كسب عباد الشمس 36%","سمسم":"كسب السمسم","جلوتين":"كسب جلوتين 60%",
          "سمك":"مسحوق أسماك 60%","لحم":"مسحوق اللحم والعظم","دم":"مسحوق الدم","ليسين":"ليسين نقي",
          "ميثيونين":"ميثيونين نقي","ملح":"ملح الطعام","حجر":"الحجر الجيري","فوسفات":"فوسفات ثنائي الكالسيوم",
          "بيكربونات":"بيكربونات الصوديوم","مولاس":"مولاس قصب السكر","برسيم":"البرسيم الجاف","تبن":"تبن قمح",
          "يوريا":"يوريا علفية","زيت":"زيت فول الصويا"}
    for k,m in kw.items():
        if k in tl: return m
    return None

def extract_ingredients_from_image(image_bytes):
    if not OCR_AVAILABLE: return {"success":False,"message":"pytesseract غير مثبتة"}
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None: return {"success":False,"message":"تعذر قراءة الصورة"}
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)
        t1 = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
        _, t2 = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        texts=[]
        for t in [t1,t2,gray]:
            try:
                txt = pytesseract.image_to_string(t, lang='ara+eng', config=r'--oem 3 --psm 6')
                if txt.strip(): texts.append(txt)
            except Exception: continue
        if not texts: return {"success":False,"message":"لم يتم استخراج نص"}
        full = "\n".join(texts)
        ingredients={}
        for line in full.split('\n'):
            line = line.strip()
            if len(line)<3: continue
            for pat in [r'([\u0600-\u06FFa-zA-Z\s\(\)%]+?)[\s:\-=]+(\d+\.?\d*)\s*%',
                        r'([\u0600-\u06FFa-zA-Z\s\(\)%]+?)\s+(\d+\.?\d*)\s*%']:
                m = re.search(pat, line)
                if m:
                    name, val = m.group(1).strip(), float(m.group(2))
                    if 0.1<val<=100 and len(name)>2:
                        matched = match_ingredient_name(name)
                        if matched: ingredients[matched]=val; break
        return {"success":True,"ingredients":ingredients,"raw_text":full,"count":len(ingredients)}
    except Exception as e: return {"success":False,"message":f"خطأ: {e}"}

# ═══ الرسوم البيانية ═══
def create_colorful_bar_chart(standard, actual):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        nuts = [n for n in ["CP","DP","SE","NDF","ADF","EE","ASH"] if n in standard]
        if not nuts: return None
        sv = [standard[n] for n in nuts]; av = [actual.get(n,0) for n in nuts]
        fig, ax = plt.subplots(figsize=(9,4.5))
        x = np.arange(len(nuts)); w = 0.35
        b1 = ax.bar(x-w/2, sv, w, label='المعيار', color='#1976d2', edgecolor='#0d47a1', linewidth=1.5)
        b2 = ax.bar(x+w/2, av, w, label='المحسوب', color='#43a047', edgecolor='#1b5e20', linewidth=1.5)
        for b in b1: ax.text(b.get_x()+b.get_width()/2, b.get_height(), f'{b.get_height():.1f}', ha='center', va='bottom', fontsize=9, color='#0d47a1', fontweight='bold')
        for b in b2: ax.text(b.get_x()+b.get_width()/2, b.get_height(), f'{b.get_height():.1f}', ha='center', va='bottom', fontsize=9, color='#1b5e20', fontweight='bold')
        ax.set_xlabel('العنصر'); ax.set_ylabel('القيمة'); ax.set_title('مقارنة العناصر', fontweight='bold', color='#1b5e20')
        ax.set_xticks(x); ax.set_xticklabels(nuts); ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3, linestyle='--'); ax.set_facecolor('#fafafa')
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white'); plt.close()
        buf.seek(0); return buf
    except Exception: return None

def create_colorful_pie_chart(formula):
    if not MATPLOTLIB_AVAILABLE or len(formula)<2: return None
    try:
        colors = ['#e53935','#8e24aa','#3949ab','#1e88e5','#00897b','#43a047','#7cb342','#fdd835','#fb8c00','#6d4c41','#c62828','#6a1b9a']
        names = list(formula.keys()); vals = list(formula.values())
        fig, ax = plt.subplots(figsize=(8,5))
        wedges, texts, autotexts = ax.pie(vals, autopct='%1.1f%%', colors=colors[:len(names)], startangle=90, pctdistance=0.75, wedgeprops=dict(edgecolor='white', linewidth=2))
        for t in autotexts: t.set_color('white'); t.set_fontweight('bold'); t.set_fontsize(9)
        ax.legend(names, loc='center left', bbox_to_anchor=(1,0,0.5,1), fontsize=9)
        ax.set_title('توزيع المكونات', fontweight='bold', color='#1b5e20')
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white'); plt.close()
        buf.seek(0); return buf
    except Exception: return None

def create_radar_chart(standard, actual):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        nuts = [n for n in ["CP","DP","SE","NDF","ADF","EE","Ca","P"] if n in standard and standard[n]>0]
        if len(nuts)<3: return None
        std_n = [100.0]*len(nuts); act_n = [(actual.get(n,0)/standard[n])*100 for n in nuts]
        angles = np.linspace(0,2*np.pi,len(nuts),endpoint=False).tolist()
        std_n+=std_n[:1]; act_n+=act_n[:1]; angles+=angles[:1]
        fig, ax = plt.subplots(figsize=(6,6),subplot_kw=dict(polar=True))
        ax.plot(angles,std_n,'o-',linewidth=2.5,color='#1976d2',label='المعيار')
        ax.fill(angles,std_n,alpha=0.15,color='#1976d2')
        ax.plot(angles,act_n,'o-',linewidth=2.5,color='#43a047',label='المحسوب')
        ax.fill(angles,act_n,alpha=0.25,color='#43a047')
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(nuts)
        ax.set_title('المقارنة %', fontweight='bold', color='#1b5e20', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3,1.1))
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white'); plt.close()
        buf.seek(0); return buf
    except Exception: return None

def create_gauge_chart(score):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        fig, ax = plt.subplots(figsize=(4,4),subplot_kw=dict(aspect='equal'))
        for i,c in enumerate(['#c62828','#ef6c00','#f9a825','#7cb342','#43a047','#1b5e20']):
            ax.add_patch(Wedge((0,0),1,180-(i+1)*30,180-i*30,width=0.3,facecolor=c,edgecolor='white',linewidth=2))
        rad = np.radians(180-(score/100)*180)
        ax.plot([0,0.85*np.cos(rad)],[0,0.85*np.sin(rad)],color='#1a1a1a',linewidth=3,zorder=10)
        ax.add_patch(Circle((0,0),0.08,color='#1a1a1a',zorder=11))
        ax.text(0,-0.25,f'{score:.0f}%',ha='center',fontsize=20,fontweight='bold',color='#1b5e20')
        ax.text(0,-0.5,'التقييم العام',ha='center',fontsize=11,color='#666')
        ax.set_xlim(-1.2,1.2); ax.set_ylim(-0.7,1.2); ax.axis('off')
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white'); plt.close()
        buf.seek(0); return buf
    except Exception: return None

print("✅ الجزء A محمّل — أرسل 'تابع B' للحصول على PDF + الواجهة + التبويبات")
# ═══ PDF Generator ═══
class PDFGenerator:
    def __init__(self):
        self.font_name = font_mgr.font_name
        self.logo_path = None
        for lp in LOGO_OPTIONS + PHOTO_OPTIONS:
            if os.path.exists(lp): self.logo_path = lp; break

    def _ar(self, text):
        if text is None: return ""
        try: return get_display(arabic_reshaper.reshape(str(text)), base_dir='R')
        except Exception: return str(text)

    def _draw_page(self, cv, doc):
        cv.saveState(); w, h = doc.pagesize
        try:
            cv.setFillColor(HexColor('#e8f5e9')); cv.setFont(self.font_name, 60); cv.setFillAlpha(0.07)
            cv.saveState(); cv.translate(w/2, h/2); cv.rotate(45)
            cv.drawCentredString(0, 0, self._ar("تاور نولجي")); cv.restoreState(); cv.setFillAlpha(1)
        except Exception: pass
        cv.setFillColor(HexColor('#1b5e20')); cv.rect(0, h-90, w, 90, fill=1, stroke=0)
        cv.setFillColor(HexColor('#d4af37')); cv.rect(0, h-95, w, 5, fill=1, stroke=0)
        try:
            if self.logo_path: cv.drawImage(self.logo_path, 30, h-78, width=60, height=60, preserveAspectRatio=True, anchor='sw', mask='auto')
        except Exception: pass
        cv.setFillColor(white); cv.setFont(self.font_name, 22)
        cv.drawCentredString(w/2, h-38, self._ar("تاور نولجي Tawor Nology"))
        cv.setFont(self.font_name, 12); cv.setFillColor(HexColor('#e8f5e9'))
        cv.drawCentredString(w/2, h-58, self._ar("للإنتاج الحيواني وتغذية الحيوان"))
        cv.setFont(self.font_name, 10); cv.setFillColor(HexColor('#d4af37'))
        cv.drawCentredString(w/2, h-76, self._ar(f"إشراف: {SUPERVISOR}"))
        cv.setFillColor(HexColor('#1b5e20')); cv.rect(0, 42, w, 42, fill=1, stroke=0)
        cv.setFillColor(HexColor('#d4af37')); cv.rect(0, 84, w, 3, fill=1, stroke=0)
        cv.setFillColor(HexColor('#ffeb3b')); cv.setFont(self.font_name, 10)
        cv.drawCentredString(w/2, 68, self._ar(f"🤲 {DUA_SHORT} 🤲"))
        cv.setFillColor(HexColor('#c8e6c9')); cv.setFont(self.font_name, 8)
        cv.drawCentredString(w/2, 52, self._ar("اللهم اجعل قبرهما روضة من رياض الجنة"))
        cv.setFillColor(HexColor('#1b5e20')); cv.rect(0, 0, w, 42, fill=1, stroke=0)
        cv.setFillColor(white); cv.setFont(self.font_name, 8)
        cv.drawCentredString(w/2, 27, self._ar("تاور نولجي © 2026"))
        cv.setFont(self.font_name, 7); cv.drawCentredString(w/2, 12, self._ar(f"صفحة {cv.getPageNumber()}"))
        try:
            qr = qrcode.QRCode(version=1, box_size=3, border=1)
            qr.add_data(PLATFORM_URL); qr.make(fit=True)
            qi = qr.make_image(fill_color="#1b5e20", back_color="white")
            buf = io.BytesIO(); qi.save(buf, format="PNG"); buf.seek(0)
            cv.drawImage(RLImage(buf), w/2-20, 46, width=40, height=40)
        except Exception: pass
        sx, sy = w-105, 145
        cv.setStrokeColor(HexColor('#c62828')); cv.setLineWidth(3.0); cv.circle(sx, sy, 70, stroke=1, fill=0)
        cv.setLineWidth(1.5); cv.circle(sx, sy, 62, stroke=1, fill=0)
        cv.setLineWidth(0.6); cv.circle(sx, sy, 56, stroke=1, fill=0)
        cv.setFillColor(HexColor('#c62828')); cv.setFont(self.font_name, 9)
        cv.drawCentredString(sx, sy+40, self._ar("تاور نولجي"))
        cv.drawCentredString(sx, sy+28, self._ar("Tawor Nology"))
        cv.setFont(self.font_name, 7.5)
        cv.drawCentredString(sx, sy+10, self._ar("م. عبدالقادر"))
        cv.drawCentredString(sx, sy-1, self._ar("إسماعيل تاور"))
        cv.setFont(self.font_name, 6)
        cv.drawCentredString(sx, sy-17, self._ar("اختصاصي تغذية الحيوان"))
        cv.drawCentredString(sx, sy-30, self._ar("معتمد رسمياً"))
        cv.drawCentredString(sx, sy-42, self._ar("© 2026"))
        cv.restoreState()

    def _comparison_table(self, std, calc):
        labels = {"CP":"بروتين خام CP","DP":"بروتين مهضوم DP","SE":"معادل النشاء SE","NDF":"ألياف NDF","ADF":"ألياف ADF","EE":"دهن EE","ASH":"رماد ASH","Ca":"كالسيوم Ca","P":"فسفور P"}
        header = [self._ar(x) for x in ["العنصر","المعيار","المحسوب","الفرق","الفرق %","التقييم"]]
        data = [header]
        cmds = [('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),('TEXTCOLOR',(0,0),(-1,0),white),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                ('FONTNAME',(0,0),(-1,-1),self.font_name),('FONTSIZE',(0,0),(-1,-1),9),
                ('GRID',(0,0),(-1,-1),1,HexColor('#9e9e9e')),
                ('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7)]
        row = 1
        for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
            if k not in std: continue
            sv = std[k]; cv_ = calc.get(k,0); diff = cv_ - sv
            pct = (diff/sv*100) if sv else 0
            ev = evaluate_difference(pct, nutrient=k)
            unit = "%" if k in ("CP","DP","NDF","ADF","EE","ASH","Ca","P") else ""
            data.append([self._ar(labels.get(k,k)), f"{sv:.2f}{unit}", f"{cv_:.2f}{unit}", f"{diff:+.3f}", f"{pct:+.2f}%", self._ar(ev["label"])])
            cmds.append(('BACKGROUND',(0,row),(-1,row),HexColor(ev["bg"])))
            cmds.append(('TEXTCOLOR',(5,row),(5,row),HexColor(ev["color"])))
            row += 1
        t = Table(data, colWidths=[100,70,70,70,70,105]); t.setStyle(TableStyle(cmds)); return t

    def _oil_table(self, formula, std_key):
        oils = get_oil_ingredients()
        rows = [(i,p) for i,p in formula.items() if i in oils]
        if not rows: return None
        oil_std = get_oil_standard(std_key); total = sum(p for _,p in rows)
        data = [[self._ar("الزيت"),self._ar("النسبة %"),self._ar("kcal/kg تقديري")]]
        for ing, pct in rows:
            data.append([self._ar(ing), f"{pct:.2f}%", f"{pct*90:.0f}"])
        data.append([self._ar("الإجمالي"), f"{total:.2f}%", f"{total*90:.0f}"])
        cmds = [('BACKGROUND',(0,0),(-1,0),HexColor('#e65100')),('TEXTCOLOR',(0,0),(-1,0),white),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),
                ('FONTSIZE',(0,0),(-1,-1),10),('GRID',(0,0),(-1,-1),1,HexColor('#bf360c')),
                ('BACKGROUND',(0,-1),(-1,-1),HexColor('#ffe0b2')),
                ('TEXTCOLOR',(0,-1),(-1,-1),HexColor('#bf360c')),
                ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]
        t = Table(data, colWidths=[250,100,135]); t.setStyle(TableStyle(cmds))
        return t, total, oil_std

    def generate_report(self, formula, requirement, animal_type, breed, cost, city,
                        local_cost, local_sym, requester_name="", protein_basis="DP",
                        standard_key="", include_charts=True):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []
        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text), ParagraphStyle('s', fontName=self.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color), spaceAfter=6, leading=size*1.6))
        story.append(P("تقرير فني رسمي — تركيب علفة", size=20, align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1,6)); story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
        story.append(Spacer(1,12))
        cdata = [[self._ar("👤 اسم طالب الخدمة:"), self._ar(requester_name or "...")],
                 [self._ar("📍 الموقع:"), self._ar(city)],
                 [self._ar("🐾 الفصيل:"), self._ar(f"{animal_type} — {breed}")],
                 [self._ar("🧬 أساس الحساب:"), self._ar("DP" if protein_basis=="DP" else "CP")],
                 [self._ar("📅 التاريخ:"), datetime.now().strftime('%Y-%m-%d | %H:%M')]]
        ct = Table(cdata, colWidths=[150,340])
        ct.setStyle(TableStyle([('BACKGROUND',(0,0),(0,-1),HexColor('#e8f5e9')),
            ('BACKGROUND',(1,0),(1,-1),HexColor('#fafafa')),('BOX',(0,0),(-1,-1),1.5,HexColor('#2e7d32')),
            ('INNERGRID',(0,0),(-1,-1),0.6,HexColor('#c8e6c9')),('ALIGN',(0,0),(-1,-1),'RIGHT'),
            ('FONTNAME',(0,0),(-1,-1),self.font_name),('FONTSIZE',(0,0),(-1,-1),11),
            ('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9)]))
        story.append(ct); story.append(Spacer(1,15))
        std_v = requirement_to_standard(requirement); calc_v = compute_formula_nutrients(formula)
        scores = []
        for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
            if k not in std_v: continue
            sv = std_v[k]; cv_ = calc_v.get(k,0); pct = (cv_-sv)/sv*100 if sv else 0
            scores.append({"score": evaluate_difference(pct, nutrient=k)["score"]})
        overall = get_overall_rating(scores)
        story.append(P("📊 جدول مقارنة العناصر", size=14, align=TA_RIGHT, color='#1b5e20'))
        story.append(Spacer(1,8)); story.append(self._comparison_table(std_v, calc_v)); story.append(Spacer(1,12))
        sum_data = [[self._ar("التقييم"), self._ar("المطابقة"), self._ar("المتوسط")],
                    [self._ar(overall["label"]), f"{sum(1 for s in scores if s['score']>=85)}/{len(scores)}", f"{overall['score']:.0f}%"]]
        st_t = Table(sum_data, colWidths=[160,165,165])
        st_t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#1565c0')),('TEXTCOLOR',(0,0),(-1,0),white),
            ('BACKGROUND',(0,1),(-1,-1),HexColor('#e3f2fd')),('GRID',(0,0),(-1,-1),1,HexColor('#1976d2')),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),11),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
        story.append(st_t); story.append(Spacer(1,15))
        oil_res = self._oil_table(formula, standard_key)
        if oil_res:
            oil_t, total_oil, oil_std = oil_res
            story.append(P("🌰 جدول الزيوت", size=14, align=TA_RIGHT, color='#e65100'))
            story.append(Spacer(1,8)); story.append(oil_t); story.append(Spacer(1,8))
            note = f"الأقصى: {oil_std['max']}% | المثالي: {oil_std['optimal']}% | المرجع: {oil_std['source']}"
            if total_oil > oil_std['max']: note = "⚠️ تجاوز الحد! " + note
            elif total_oil > oil_std['optimal']*1.2: note = "⚡ مرتفع. " + note
            else: note = "✅ مطابق. " + note
            story.append(P(note, size=10, align=TA_RIGHT, color='#bf360c')); story.append(Spacer(1,15))
        if include_charts:
            story.append(P("📈 الرسوم", size=14, align=TA_RIGHT, color='#1b5e20')); story.append(Spacer(1,10))
            c1 = create_colorful_bar_chart(std_v, calc_v)
            if c1: story.append(RLImage(c1, width=450, height=250)); story.append(Spacer(1,12))
            c2 = create_colorful_pie_chart(formula); c3 = create_radar_chart(std_v, calc_v)
            if c2 and c3:
                row = [[RLImage(c2,width=210,height=200),RLImage(c3,width=210,height=200)]]
                rt = Table(row, colWidths=[230,230])
                rt.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
                story.append(rt); story.append(Spacer(1,12))
            gauge = create_gauge_chart(overall["score"])
            if gauge:
                story.append(P("🎯 مؤشر التقييم", size=12, align=TA_CENTER, color='#1b5e20'))
                story.append(RLImage(gauge, width=200, height=200)); story.append(Spacer(1,12))
        story.append(PageBreak())
        story.append(P("💰 التكاليف", size=14, align=TA_RIGHT, color='#1b5e20')); story.append(Spacer(1,8))
        cdata2 = [[self._ar("البند"), self._ar("القيمة")],
                  [self._ar("التكلفة للطن ($)"), f"${cost:.2f}"],
                  [self._ar(f"التكلفة ({local_sym})"), f"{local_cost:,.2f}"],
                  [self._ar("البروتين المستهدف"), f"{requirement.DP if protein_basis=='DP' else requirement.CP:.2f}%"],
                  [self._ar("الدهن EE"), f"{calc_v['EE']:.2f}%"]]
        tc = Table(cdata2, colWidths=[280,210])
        tc.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),('TEXTCOLOR',(0,0),(-1,0),white),
            ('BACKGROUND',(0,1),(-1,-1),HexColor('#f5f5f5')),('GRID',(0,0),(-1,-1),1,HexColor('#2e7d32')),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),11),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
        story.append(tc); story.append(Spacer(1,18))
        if formula:
            story.append(P("🌾 المكونات للطن", size=14, align=TA_RIGHT, color='#1b5e20')); story.append(Spacer(1,8))
            ing_d = [[self._ar("المكون"), self._ar("النسبة %"), self._ar("كجم/طن")]]
            for ing, pct in formula.items(): ing_d.append([self._ar(ing), f"{pct:.2f}%", f"{pct*10:.1f}"])
            ti = Table(ing_d, colWidths=[270,110,110])
            ti.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),('TEXTCOLOR',(0,0),(-1,0),white),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),
                ('FONTSIZE',(0,0),(-1,-1),10),('GRID',(0,0),(-1,-1),1,HexColor('#bdbdbd')),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#ffffff'),HexColor('#f5f5f5')]),
                ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
            story.append(ti); story.append(Spacer(1,25))
        sign = [[self._ar("توقيع الطالب"), self._ar("توقيع المختص")],
                [self._ar("......................"), self._ar(SUPERVISOR)],
                [self._ar("التاريخ: ..../..../......"), self._ar(SUPERVISOR_TITLE)]]
        ts = Table(sign, colWidths=[245,245])
        ts.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
            ('BOX',(0,0),(-1,-1),1,HexColor('#bdbdbd')),('INNERGRID',(0,0),(-1,-1),0.5,HexColor('#e0e0e0')),
            ('BACKGROUND',(0,0),(-1,0),HexColor('#e8f5e9'))]))
        story.append(ts)
        doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
        buffer.seek(0); return buffer.getvalue()

pdf_gen = PDFGenerator()

def generate_bag_label_pdf(formula, requirement, animal_type, stage_label, ton_cost,
                           local_cost, local_sym, city="", requester="", report_id=""):
    if not REPORTLAB_AVAILABLE: return b""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=35, leftMargin=35, topMargin=110, bottomMargin=130)
    story = []
    def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
        return Paragraph(ar(text), ParagraphStyle('b', fontName=font_mgr.font_name, fontSize=size,
            alignment=align, textColor=HexColor(color), spaceAfter=4, leading=size*1.5))
    story.append(P("🌾 ديباجة جوال علف — Tawor Nology", size=20, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1,8)); story.append(HRFlowable(width="100%", thickness=3, color=HexColor('#d4af37')))
    story.append(Spacer(1,10))
    rid = report_id or f"TN-{datetime.now():%Y%m%d%H%M%S}"
    info = [[ar("رقم الدفعة:"), rid, ar("التاريخ:"), datetime.now().strftime('%Y-%m-%d')],
            [ar("نوع الحيوان:"), f"{animal_type} — {stage_label}", "", ""],
            [ar("الموقع:"), city or "—", ar("طالب العلفة:"), requester or "—"],
            [ar("أساس الحساب:"), "DP", ar("الوزن الصافي:"), "50 كجم"]]
    it = Table(info, colWidths=[90,160,90,160])
    it.setStyle(TableStyle([('BACKGROUND',(0,0),(0,-1),HexColor('#e8f5e9')),('BACKGROUND',(2,0),(2,-1),HexColor('#e8f5e9')),
        ('BOX',(0,0),(-1,-1),1.5,HexColor('#2e7d32')),('INNERGRID',(0,0),(-1,-1),0.5,HexColor('#a5d6a7')),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),('FONTSIZE',(0,0),(-1,-1),9.5),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(it); story.append(Spacer(1,14))
    story.append(P("📊 التحليل الغذائي المضمون", size=14, align=TA_RIGHT, color='#1b5e20')); story.append(Spacer(1,6))
    act = compute_formula_nutrients(formula); kcal = compute_energy_kcal(formula)
    nd = [[ar("العنصر"), ar("المضمون"), ar("العنصر"), ar("المضمون")],
          [ar("بروتين مهضوم DP"), f"{act.get('DP',0):.2f}%", ar("بروتين خام CP"), f"{act.get('CP',0):.2f}%"],
          [ar("معادل النشاء SE"), f"{act.get('SE',0):.2f}", ar("الدهن EE"), f"{act.get('EE',0):.2f}%"],
          [ar("ألياف NDF"), f"{act.get('NDF',0):.2f}%", ar("ألياف ADF"), f"{act.get('ADF',0):.2f}%"],
          [ar("كالسيوم Ca"), f"{act.get('Ca',0):.3f}%", ar("فسفور P"), f"{act.get('P',0):.3f}%"],
          [ar("طاقة تقديرية kcal/kg"), f"{kcal:.0f}", "", ""]]
    nt = Table(nd, colWidths=[120,110,120,110])
    nt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),('TEXTCOLOR',(0,0),(-1,0),white),
        ('BACKGROUND',(0,1),(0,-1),HexColor('#f1f8e9')),('BACKGROUND',(2,1),(2,-1),HexColor('#f1f8e9')),
        ('SPAN',(1,-1),(-1,-1)),('BOX',(0,0),(-1,-1),2,HexColor('#2e7d32')),
        ('INNERGRID',(0,0),(-1,-1),0.5,HexColor('#a5d6a7')),('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),('FONTSIZE',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(nt); story.append(Spacer(1,14))
    story.append(P("🌾 المكونات (لكل 1000 كجم)", size=14, align=TA_RIGHT, color='#1b5e20')); story.append(Spacer(1,6))
    ig = [[ar("المادة"), ar("النسبة %"), ar("كجم/طن"), ar("الترتيب")]]
    for i,(ing,pct) in enumerate(sorted(formula.items(), key=lambda x:-x[1]), 1):
        ig.append([ar(ing), f"{pct:.2f}%", f"{pct*10:.1f}", f"#{i}"])
    it2 = Table(ig, colWidths=[220,80,80,60])
    it2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),('TEXTCOLOR',(0,0),(-1,0),white),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#ffffff'),HexColor('#f5f5f5')]),
        ('BOX',(0,0),(-1,-1),1.5,HexColor('#2e7d32')),('INNERGRID',(0,0),(-1,-1),0.4,HexColor('#bdbdbd')),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
        ('FONTSIZE',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story.append(it2); story.append(Spacer(1,14))
    story.append(P("📋 تعليمات التخزين", size=12, align=TA_RIGHT, color='#c62828'))
    story.append(P("▪️ يُخزّن في مكان جاف وجيد التهوية.\n▪️ يُقدَّم مع ماء نظيف.\n▪️ الفترة الانتقالية 7-10 أيام.\n▪️ صلاحية الاستخدام: 3 أشهر.", size=9.5, color='#4e342e'))
    story.append(Spacer(1,12))
    cd = [[ar("سعر البيع للطن"), f"${ton_cost:.2f}", ar("السعر المحلي"), f"{local_cost:,.0f} {local_sym}"]]
    ct = Table(cd, colWidths=[120,110,120,110])
    ct.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),HexColor('#fff8e1')),('BOX',(0,0),(-1,-1),2,HexColor('#d4af37')),
        ('INNERGRID',(0,0),(-1,-1),0.5,HexColor('#ffe082')),('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),('FONTSIZE',(0,0),(-1,-1),11),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story.append(ct); story.append(Spacer(1,14))
    story.append(P(f"إشراف: {SUPERVISOR}", size=10, align=TA_CENTER, color='#1b5e20'))
    story.append(P(f"🕌 {DUA_SHORT} 🕌", size=10, align=TA_CENTER, color='#c62828'))
    def _bag_page(cv, doc):
        cv.saveState(); w, h = doc.pagesize
        cv.setFillColor(HexColor('#1b5e20')); cv.rect(0, h-85, w, 85, fill=1, stroke=0)
        cv.setFillColor(HexColor('#d4af37')); cv.rect(0, h-90, w, 5, fill=1, stroke=0)
        try:
            for lp in LOGO_OPTIONS:
                if os.path.exists(lp):
                    cv.drawImage(lp, 25, h-75, width=55, height=55, preserveAspectRatio=True, anchor='sw', mask='auto'); break
        except Exception: pass
        cv.setFillColor(white); cv.setFont(font_mgr.font_name, 20)
        cv.drawCentredString(w/2, h-38, ar("تاور نولجي Tawor Nology"))
        cv.setFont(font_mgr.font_name, 11); cv.setFillColor(HexColor('#e8f5e9'))
        cv.drawCentredString(w/2, h-58, ar("للإنتاج الحيواني وتغذية الحيوان"))
        cv.setFont(font_mgr.font_name, 9); cv.setFillColor(HexColor('#d4af37'))
        cv.drawCentredString(w/2, h-74, ar(f"إشراف: {SUPERVISOR}"))
        cv.setFillColor(HexColor('#1b5e20')); cv.rect(0, 0, w, 65, fill=1, stroke=0)
        cv.setFillColor(HexColor('#d4af37')); cv.rect(0, 65, w, 3, fill=1, stroke=0)
        cv.setFillColor(HexColor('#ffeb3b')); cv.setFont(font_mgr.font_name, 11)
        cv.drawCentredString(w/2, 43, ar(f"🕌 {DUA_SHORT} 🕌"))
        cv.setFillColor(HexColor('#c8e6c9')); cv.setFont(font_mgr.font_name, 8)
        cv.drawCentredString(w/2, 27, ar("اللهم اجعل قبرهما روضة من رياض الجنة"))
        cv.setFillColor(white); cv.setFont(font_mgr.font_name, 7)
        cv.drawCentredString(w/2, 12, ar(f"صفحة {cv.getPageNumber()} | © 2026 Tawor Nology"))
        try:
            qr = qrcode.QRCode(version=1, box_size=3, border=1); qr.add_data(PLATFORM_URL); qr.make(fit=True)
            qi = qr.make_image(fill_color="#1b5e20", back_color="white")
            qb = io.BytesIO(); qi.save(qb, format="PNG"); qb.seek(0)
            cv.drawImage(RLImage(qb), w-75, 78, width=55, height=55)
        except Exception: pass
        sx, sy = 75, 130
        cv.setStrokeColor(HexColor('#c62828')); cv.setLineWidth(3.2); cv.circle(sx, sy, 55, stroke=1, fill=0)
        cv.setLineWidth(1.4); cv.circle(sx, sy, 48, stroke=1, fill=0)
        cv.setLineWidth(0.5); cv.circle(sx, sy, 43, stroke=1, fill=0)
        cv.setFillColor(HexColor('#c62828')); cv.setFont(font_mgr.font_name, 7.5)
        cv.drawCentredString(sx, sy+32, ar("تاور نولجي"))
        cv.drawCentredString(sx, sy+22, ar("Tawor Nology"))
        cv.setFont(font_mgr.font_name, 6.5)
        cv.drawCentredString(sx, sy+6, ar("م. عبدالقادر"))
        cv.drawCentredString(sx, sy-4, ar("إسماعيل تاور"))
        cv.setFont(font_mgr.font_name, 5.5)
        cv.drawCentredString(sx, sy-17, ar("اختصاصي تغذية الحيوان"))
        cv.drawCentredString(sx, sy-27, ar("معتمد © 2026"))
        cv.restoreState()
    doc.build(story, onFirstPage=_bag_page, onLaterPages=_bag_page)
    buffer.seek(0); return buffer.getvalue()

def export_comparison_to_excel(standard, calculated, requester_name="", animal="", stage="", formula=None, standard_key=""):
    if not OPENPYXL_AVAILABLE: return b""
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "مقارنة"; ws.sheet_view.rightToLeft = True
    hf = XF(name='Arial', size=12, bold=True, color='FFFFFF')
    hfill = PatternFill('solid', fgColor='1B5E20')
    tf = XF(name='Arial', size=14, bold=True, color='1B5E20')
    ct = XA(horizontal='center', vertical='center', wrap_text=True)
    rt = XA(horizontal='right', vertical='center', wrap_text=True)
    thin = Side(border_style='thin', color='9E9E9E')
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    ws.merge_cells('A1:F1'); ws['A1'] = APP_NAME; ws['A1'].font = tf; ws['A1'].alignment = ct
    ws.merge_cells('A2:F2'); ws['A2'] = f"🤲 {DUA_SHORT} 🤲"
    ws['A2'].font = XF(name='Arial', size=10, bold=True, color='C62828'); ws['A2'].alignment = ct
    ws['A4'] = "طالب:"; ws['A4'].font = XF(bold=True); ws['A4'].alignment = rt
    ws.merge_cells('B4:D4'); ws['B4'] = requester_name
    ws['E4'] = "التاريخ:"; ws['E4'].font = XF(bold=True); ws['E4'].alignment = rt
    ws['F4'] = datetime.now().strftime('%Y-%m-%d')
    for c, h in enumerate(["العنصر","المعيار","المحسوب","الفرق","% الفرق","التقييم"], 1):
        cell = ws.cell(row=6, column=c, value=h)
        cell.font = hf; cell.fill = hfill; cell.alignment = ct; cell.border = bd
    labels = {"CP":"بروتين خام","DP":"بروتين مهضوم","SE":"معادل النشاء","NDF":"NDF","ADF":"ADF","EE":"دهن","ASH":"رماد","Ca":"كالسيوم","P":"فسفور"}
    row = 7
    for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
        if k not in standard: continue
        sv = standard[k]; cv_ = calculated.get(k,0); diff = cv_-sv
        pct = (diff/sv*100) if sv else 0
        ev = evaluate_difference(pct, nutrient=k)
        for c, v in enumerate([labels[k], round(sv,2), round(cv_,2), round(diff,3), round(pct,2), ev["label"]], 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.alignment = ct; cell.border = bd
            cell.fill = PatternFill('solid', fgColor=ev["bg"].replace('#',''))
        row += 1
    if formula:
        oil_rows = [(i,p) for i,p in formula.items() if i in get_oil_ingredients()]
        if oil_rows:
            row += 2
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
            ws.cell(row=row, column=1, value="🌰 الزيوت المستخدمة").font = tf
            ws.cell(row=row, column=1).alignment = ct; row += 1
            for c, h in enumerate(["الزيت","النسبة %","kcal/kg","","",""], 1):
                cell = ws.cell(row=row, column=c, value=h)
                cell.font = hf; cell.fill = PatternFill('solid', fgColor='E65100')
                cell.alignment = ct; cell.border = bd
            row += 1
            for ing, pct in oil_rows:
                ws.cell(row=row, column=1, value=ing).border = bd; ws.cell(row=row, column=1).alignment = rt
                ws.cell(row=row, column=2, value=round(pct,2)).border = bd; ws.cell(row=row, column=2).alignment = ct
                ws.cell(row=row, column=3, value=round(pct*90,0)).border = bd; ws.cell(row=row, column=3).alignment = ct
                row += 1
    for c in range(1, 7): ws.column_dimensions[get_column_letter(c)].width = 22
    buf = io.BytesIO(); wb.save(buf); buf.seek(0); return buf.getvalue()

# ═══ الأسعار ═══
EXCHANGE_RATES = {
"السودان":{"rate":600.0,"sym":"SDG"}, "LIBYA":{"rate":4.80,"sym":"LYD"},
"مصر":{"rate":48.0,"sym":"EGP"}, "السعودية":{"rate":3.75,"sym":"SAR"},
"الإمارات":{"rate":3.67,"sym":"AED"}, "باقي دول العالم":{"rate":1.0,"sym":"USD"},
}

def get_market_prices(country, city, state=""):
    base = {ing: 280.0 for cat in BIG_FEEDS_LIBRARY.values() for ing in cat}
    base.update({
        "ذرة صفراء":230,"ذرة بيضاء":225,"شعير مطحون":210,"سورجم (فتريتة)":195,"قمح محلي":240,
        "أمباز الفول السوداني":460,"كسب فول صويا 44%":440,"كسب فول صويا 48%":480,
        "كسب عباد الشمس 36%":310,"كسب بذور القطن":290,"نخالة قمح (ردة)":150,
        "البرسيم الجاف":170,"مولاس قصب السكر":120,"مسحوق أسماك 60%":850,
        "مركزات دواجن":650,"مركزات مواشي":600,"الحجر الجيري":40,
        "فوسفات ثنائي الكالسيوم":280,"ملح الطعام":30,"بيكربونات الصوديوم":340,
        "مضاد سموم فطرية":950,"بريمكس تسمين دواجن":4800,"بريمكس مجترات":4500,
        "ليسين نقي":4200,"ميثيونين نقي":5800,
        "زيت ذرة":1500,"زيت فول الصويا":1350,"زيت عباد الشمس":1300,"زيت بذرة القطن":1400,
        "زيت الكتان":1700,"زيت جوز الهند":1900,"زيت النخيل":1100,"زيت الكانولا":1450,
        "زيت السمسم":2100,"زيت الزيتون":3500,"زيت الأفوكادو":4200,"زيت القرطم":1800,
        "زيت الفول السوداني":2200,"شحم حيواني (Tallow)":900,"سمن حيواني (Lard)":850,
        "دهن الدجاج":800,"زيت السمك (Fish Oil)":3800,
    })
    m = 1.0
    if country == "السودان":
        m = 1.15
        if "كردفان" in state: m = 1.20
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
                with open(p, "rb") as f: return base64.b64encode(f.read()).decode()
            except Exception: pass
    return None

img_base64 = get_img_b64(tuple(PHOTO_OPTIONS))

# ═══ حالة الجلسة ═══
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "active_formula" not in st.session_state: st.session_state["active_formula"] = {}
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "active_animal_img" not in st.session_state: st.session_state["active_animal_img"] = ANIMAL_IMAGES["عام"]
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0
if "shared_comments" not in st.session_state: st.session_state["shared_comments"] = f"• مرحباً بكم في {APP_NAME}\n• {DUA_SHORT}\n"
if "broiler_farms" not in st.session_state: st.session_state["broiler_farms"] = {}
if "livestock_prices" not in st.session_state:
    st.session_state["livestock_prices"] = {
        "عجول تسمين هولشتاين ($)":1350.0,"أبقار كنانة ($)":900.0,"ضأن محلي ($)":180.0,
        "ماعز نوبي ($)":130.0,"إبل حاشي ($)":1200.0,"كتكوت لاحم يوم ($)":0.65,"دجاج بياض ($)":5.50}
if "products_prices" not in st.session_state:
    st.session_state["products_prices"] = {
        "كيلو لحم بقري ($)":7.50,"كيلو لحم ضأن ($)":9.00,"كيلو لحم إبل ($)":8.50,
        "كيلو لحم دجاج ($)":3.80,"طبق بيض 30 ($)":4.20,"لتر حليب بقر ($)":0.90,"لتر حليب إبل ($)":3.50}
if "inventory" not in st.session_state:
    st.session_state["inventory"] = {}
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing in cat:
            st.session_state["inventory"][ing] = {"quantity":25.0,"min_threshold":5.0,"unit":"طن"}

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
.main-box { background-color: rgba(255,255,255,0.98); padding: 30px; border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18); margin-bottom: 60px; backdrop-filter: blur(5px); }
h1, h2, h3, h4, h5, p, span, li, div, label { color: #1a1a1a !important; }
@keyframes duaGlow { 0%,100% { box-shadow: 0 15px 40px rgba(0,0,0,0.4), inset 0 0 30px rgba(212,175,55,0.2); }
  50% { box-shadow: 0 15px 40px rgba(0,0,0,0.5), inset 0 0 40px rgba(212,175,55,0.4), 0 0 80px rgba(212,175,55,0.5); } }
@keyframes floatIcon { 0%,100% { transform: translateY(0) rotate(0); } 50% { transform: translateY(-12px) rotate(6deg); } }
@keyframes gradientShift { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
@keyframes shimmerText { 0% { background-position: -500% 0; } 100% { background-position: 500% 0; } }
.dua-main-box { background: linear-gradient(135deg,#0d3011 0%,#1b5e20 25%,#2e7d32 50%,#1b5e20 75%,#0d3011 100%);
  background-size: 200% 200%; animation: duaGlow 4s ease-in-out infinite, gradientShift 12s ease infinite;
  padding: 32px 28px; border-radius: 22px; border: 4px solid #d4af37; direction: rtl; text-align: center;
  margin: 25px 0; position: relative; overflow: hidden; }
.dua-main-box::before { content: "🕌"; position: absolute; top: 15px; right: 25px; font-size: 3.5rem; opacity: 0.25; animation: floatIcon 4s ease-in-out infinite; }
.dua-main-box::after { content: "🕌"; position: absolute; bottom: 15px; left: 25px; font-size: 3.5rem; opacity: 0.25; animation: floatIcon 5s ease-in-out infinite reverse; }
.dua-main-box * { color: white !important; position: relative; z-index: 2; }
.dua-main-box h3 { color: #d4af37 !important; font-size: 1.9rem; margin-bottom: 18px; font-weight: 900; }
.dua-main-box .names { display: inline-block; background: linear-gradient(90deg, rgba(212,175,55,0.15), rgba(212,175,55,0.35), rgba(212,175,55,0.15));
  background-size: 200% 100%; animation: shimmerText 4s linear infinite; font-size: 1.65rem; font-weight: 900; color: #ffeb3b !important;
  margin: 20px 0; padding: 16px 30px; border: 2px solid #d4af37; border-radius: 15px; font-family: 'Amiri', serif !important; }
.dua-main-box p.quran { font-family: 'Amiri', serif !important; font-size: 1.2rem; color: #d4af37 !important;
  margin-top: 22px; padding: 18px 25px; background: rgba(0,0,0,0.25); border-radius: 12px; border-right: 5px solid #d4af37; border-left: 5px solid #d4af37; }
.visitor-dua-banner { background: linear-gradient(135deg,#fff8e1 0%,#ffecb3 50%,#ffe082 100%); padding: 20px 28px;
  border-radius: 18px; border: 3px solid #d4af37; margin: 22px 0; direction: rtl; text-align: center; box-shadow: 0 6px 25px rgba(0,0,0,0.15); }
.visitor-dua-banner * { color: #4e342e !important; }
@keyframes fixedDuaGlow { 0%,100% { text-shadow: 0 0 8px rgba(255,235,59,0.6); } 50% { text-shadow: 0 0 20px rgba(255,235,59,1), 0 0 30px rgba(212,175,55,0.8); } }
.dua-fixed-banner { position: fixed; bottom: 0; left: 0; right: 0;
  background: linear-gradient(90deg,#0d3011,#1b5e20,#2e7d32,#1b5e20,#0d3011); background-size: 200% 100%;
  animation: gradientShift 8s linear infinite; color: white !important; padding: 11px 20px; z-index: 9998;
  text-align: center; border-top: 3px solid #d4af37; font-family: 'Amiri', serif !important; font-size: 1.05rem; font-weight: bold; }
.dua-fixed-banner * { color: #ffeb3b !important; font-family: 'Amiri', serif !important; animation: fixedDuaGlow 3s ease-in-out infinite; }
.section-title { color: #1b5e20 !important; border-right: 6px solid #2e7d32; padding: 12px 18px; text-align: right;
  font-size: 1.5rem; font-weight: bold; margin-top: 30px; margin-bottom: 20px;
  background: linear-gradient(to left, rgba(46,125,50,0.15), transparent); border-radius: 10px; }
.formula-item { background: linear-gradient(135deg,#ffffff 0%,#e8f5e9 100%); padding: 15px 20px; border-radius: 12px;
  margin-bottom: 10px; font-weight: bold; color: #1b5e20 !important; border-right: 5px solid #2e7d32;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: right; }
.oil-item { background: linear-gradient(135deg,#fff8e1 0%,#ffe0b2 100%); padding: 12px 18px; border-radius: 12px;
  margin-bottom: 8px; font-weight: bold; color: #bf360c !important; border-right: 5px solid #e65100; box-shadow: 0 4px 15px rgba(230,81,0,0.15); text-align: right; }
.price-card { background: linear-gradient(135deg,#f1f8e9,#e8f5e9); padding: 20px; border-radius: 12px;
  border-right: 5px solid #2e7d32; margin-bottom: 20px; direction: rtl; text-align: right; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
.oil-info-card { background: linear-gradient(135deg,#fff3e0,#ffe0b2); padding: 18px; border-radius: 12px;
  border-right: 5px solid #e65100; margin-bottom: 18px; direction: rtl; text-align: right; box-shadow: 0 4px 15px rgba(230,81,0,0.15); }
.profile-img-style { width: 150px; height: 150px; border-radius: 50%; object-fit: cover; border: 4px solid #d4af37;
  box-shadow: 0 6px 20px rgba(0,0,0,0.25); display: block; margin: 0 auto; }
.stButton > button { color: #1a1a1a !important; background-color: #e8f5e9 !important;
  border: 1px solid #2e7d32 !important; font-weight: bold !important; }
.stButton > button:hover { background-color: #c8e6c9 !important; }
@keyframes sigPulse { 0%,100% { box-shadow: 0 4px 15px rgba(0,0,0,0.3), 0 0 20px rgba(212,175,55,0.3); }
  50% { box-shadow: 0 4px 15px rgba(0,0,0,0.3), 0 0 35px rgba(212,175,55,0.7); } }
.mini-signature { position: fixed; left: 20px; bottom: 65px;
  background: linear-gradient(135deg,#1b5e20,#2e7d32); color: white !important; padding: 9px 22px;
  font-size: 0.88rem; border-radius: 25px; z-index: 9997; direction: rtl; border: 2px solid #d4af37;
  animation: sigPulse 3s ease-in-out infinite; font-weight: bold; }
.mini-signature * { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ═══ بوابة الدخول ═══
if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 780px; margin: 30px auto; direction: rtl;">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <p style="font-size:1.1rem; color:#a5d6a7 !important;">نبدأ باسم الله، ونسألُه أن يتقبّلَ هذا العملَ صدقةً جاريةً عن:</p>
        <div class="names">🕊️ رحم الله والدي إسماعيل تاور وأختي ابتسام 🕊️</div>
        <p class="quran">{DUA_QURAN}</p>
        <p class="quran" style="margin-top:10px;">{DUA_VERSE}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 2px solid #d4af37; margin: 25px 0;'>", unsafe_allow_html=True)
    cl, ct_ = st.columns([0.3, 0.7])
    with cl:
        if img_base64:
            st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
        else:
            st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)
    with ct_:
        st.markdown(f"<h2 style='color:#2E7D32; text-align:right;'>🌾 {APP_NAME}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.1rem;'>{APP_TAGLINE}</p>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#c62828; text-align:right;'>{SUPERVISOR} — {SUPERVISOR_TITLE}</h4>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#1b5e20; margin-top:20px;'>🔐 بوابة الدخول</h3>", unsafe_allow_html=True)
    co, cg = st.columns(2)
    with co:
        st.markdown("""<div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9); padding: 20px; border-radius: 12px;
        border: 2px solid #2e7d32; text-align: center;"><h4 style="color: #1b5e20;">👑 المالك</h4><p>الدخول بكود خاص</p></div>""", unsafe_allow_html=True)
        oc = st.text_input("🔑 كود المالك:", type="password", key="oc_in")
        if st.button("👑 دخول المالك", type="primary", use_container_width=True, key="btn_own"):
            if oc.strip() == OWNER_CODE:
                st.session_state.update({"approved": True, "user_role": "owner"}); st.rerun()
            else: st.error("❌ كود غير صحيح")
    with cg:
        st.markdown("""<div style="background: linear-gradient(135deg, #fff8e1, #ffecb3); padding: 20px; border-radius: 12px;
        border: 2px solid #d4af37; text-align: center;"><h4 style="color: #e65100;">👥 زائر</h4><p>دخول مجاني<br><small>(بيانات المالك محجوبة)</small></p></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True, key="btn_gst"):
            st.session_state.update({"approved": True, "user_role": "guest"}); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ═══ الواجهة ═══
st.markdown('<div class="main-box">', unsafe_allow_html=True)
c1, c2 = st.columns([0.7, 0.3])
with c2:
    rl = "المالك 👑" if is_owner() else "زائر 👥"
    st.markdown(f"<div style='text-align:left; padding:10px; background:#f5f5f5; border-radius:10px;'>الحساب: <b>{rl}</b></div>", unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True, key="btn_out"):
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
    st.markdown(f"""<h1 style='color: #0d3011; text-align:right; margin-bottom:0; font-weight: 900; font-size: 2.3rem;'>🌾 {APP_NAME}</h1>""", unsafe_allow_html=True)
    st.markdown(f"""<p style='color: #1565C0; text-align:right; font-size: 1.25rem; font-weight: 600;'>{APP_TAGLINE}</p>""", unsafe_allow_html=True)
    st.markdown(f"""<div style='background: linear-gradient(135deg, #fff8e1, #ffe082); padding: 12px 20px; border-radius: 12px;
                border-right: 6px solid #c62828; border-left: 6px solid #c62828; margin-top: 10px;'>
        <h3 style='color: #b71c1c; text-align:right; margin: 0; font-weight: 900;'>👨‍🔬 {SUPERVISOR}</h3>
        <p style='color: #0d47a1; text-align:right; margin: 5px 0 0 0; font-weight: 700;'>✨ {SUPERVISOR_TITLE}</p></div>""", unsafe_allow_html=True)
st.markdown(f'<div class="visitor-dua-banner">{DUA_BANNER}</div>', unsafe_allow_html=True)
st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)

if is_owner():
    tabs_titles = ["🔬 تركيب الأعلاف والمختبر","🌰 مكتبة الزيوت","🍼 بدائل الحليب","📷 المختبر الذكي","📊 البورصة","🏭 المستودعات","🧾 الفواتير","🖨️ الديباجة","📈 التحليلات","🐔 مزارع الدجاج","💬 التعليقات","📚 المراجع","💡 المساعدة","📖 الدليل"]
else:
    tabs_titles = ["🔬 تركيب الأعلاف والمختبر","🌰 مكتبة الزيوت","🍼 بدائل الحليب","📷 المختبر الذكي","📚 المراجع","💡 المساعدة","📖 الدليل"]
tabs = st.tabs(tabs_titles)
tab_map = {t: tab for t, tab in zip(tabs_titles, tabs)}

# ═══ تبويب التركيب + المختبر ═══
with tab_map["🔬 تركيب الأعلاف والمختبر"]:
    sub_form, sub_lab = st.tabs(["🎯 تركيب علفة نموذجية","🔬 مختبر تحليل الأعلاف"])

    with sub_form:
        st.markdown('<div class="section-title">🌍 الموقع الجغرافي</div>', unsafe_allow_html=True)
        cc1, cc2, cc3 = st.columns(3)
        with cc1: country = st.selectbox("🌍 الدولة:", list(EXCHANGE_RATES.keys()), key="co")
        with cc2: state = st.text_input("🗺️ الولاية:", "الخرطوم", key="st")
        with cc3: city = st.text_input("🏙️ المدينة:", "الخرطوم", key="ci")
        rate = EXCHANGE_RATES.get(country, {"rate":1.0,"sym":"USD"})
        local_rate, local_sym = rate["rate"], rate["sym"]
        live_prices = get_market_prices(country, city, state)

        st.markdown('<div class="section-title">🧬 أساس الحساب</div>', unsafe_allow_html=True)
        pb = st.radio("اختر:", ["البروتين المهضوم (DP) — الأدق","البروتين الخام (CP) — الأسهل"], horizontal=True, key="pb")
        use_dp = "DP" in pb
        st.success("🎯 DP" if use_dp else "📊 CP")

        st.markdown('<div class="section-title">🐾 اختر الحيوان</div>', unsafe_allow_html=True)
        at = st.tabs(["🐄 أبقار","🐏 أغنام","🐐 ماعز","🐪 إبل","🐎 خيول","🐔 دواجن","🦆 سمان","🐟 أسماك"])
        animal_choice = None; production_type = None; req = None; img_key = "عام"; std_key = ""

        with at[0]:
            catt = st.selectbox("الحالة:", ["حليب_عالي","حليب_متوسط","حليب_منخفض","تسمين_مكثف","تسمين_عادي","حمل_أخير","صيانة"],
                format_func=lambda x: {"حليب_عالي":"🐄 حلابة عالية","حليب_متوسط":"🐄 حلابة متوسطة","حليب_منخفض":"🐄 حلابة منخفضة","تسمين_مكثف":"💪 تسمين مكثف","تسمين_عادي":"💪 تسمين عادي","حمل_أخير":"🤰 حمل آخر","صيانة":"🌿 صيانة"}.get(x,x), key="ct_")
            c1_, c2_ = st.columns(2); cp_ = {}
            with c1_:
                if "حليب" in catt: cp_["milk_yield"] = st.number_input("🥛 الحليب (كجم):",5.0,60.0,20.0,1.0,key="cm")
                cp_["weight_kg"] = st.number_input("⚖️ الوزن:",200.0,900.0,500.0,25.0,key="cw")
            with c2_:
                rp = get_cattle_requirements(catt, **cp_)
                st.metric("DP", f"{rp.DP}%"); st.metric("CP", f"{rp.CP}%"); st.metric("SE", f"{rp.SE}")
            if st.checkbox("✅ اعتماد", key="uc"):
                animal_choice="أبقار"; production_type=catt; req=rp; img_key="أبقار"; std_key=f"أبقار_{catt}"
        with at[1]:
            sg = st.radio("الجنس:", ["ذكر","أنثى"], horizontal=True, key="sg")
            im = "ذكر" in sg
            if im:
                sht = st.selectbox("الحالة:", ["تسمين_مكثف","تسمين_عادي","حملان_تيد"],
                    format_func=lambda x: {"تسمين_مكثف":"💪 مكثف","تسمين_عادي":"💪 عادي","حملان_تيد":"🐑 تيد"}.get(x,x), key="sht_m")
            else:
                sht = st.selectbox("الحالة:", ["مرضعات","حامل_أخير","حامل_متوسط","صيانة"],
                    format_func=lambda x: {"مرضعات":"🍼 مرضعات","حامل_أخير":"🤰 حامل (4-5)","حامل_متوسط":"🤰 حامل (1-3)","صيانة":"🌿 صيانة"}.get(x,x), key="sht_f")
            lt = 1
            if sht == "مرضعات": lt = st.number_input("👶 المواليد:",1,3,1,1,key="sl")
            wt = st.number_input("⚖️ الوزن:",15.0,120.0,50.0,5.0,key="sw")
            rp = get_sheep_requirements(sht, is_male=im, weight_kg=wt, litter_size=lt)
            p1, p2, p3 = st.columns(3)
            p1.metric("DP", f"{rp.DP}%"); p2.metric("CP", f"{rp.CP}%"); p3.metric("SE", f"{rp.SE}")
            if st.checkbox("✅ اعتماد", key="us"):
                animal_choice="أغنام"; production_type=sht; req=rp; img_key="أغنام"; std_key=f"أغنام_{sht}"
        with at[2]:
            gg = st.radio("الجنس:", ["ذكر","أنثى"], horizontal=True, key="gg")
            img_ = "ذكر" in gg; mg = 0
            if img_:
                gt = st.selectbox("الحالة:", ["تسمين_جديان","تيوس"],
                    format_func=lambda x: {"تسمين_جديان":"💪 جديان","تيوس":"🐐 تيوس"}.get(x,x), key="gt_m")
            else:
                gt = st.selectbox("الحالة:", ["حلابة_عالي","حلابة_متوسط","حامل_أخير","صيانة"],
                    format_func=lambda x: {"حلابة_عالي":"🍼 عالي","حلابة_متوسط":"🍼 متوسط","حامل_أخير":"🤰 حامل","صيانة":"🌿 صيانة"}.get(x,x), key="gt_f")
                if "حلابة" in gt: mg = st.number_input("🥛 الحليب:",0.5,8.0,2.0,0.25,key="gm")
            rp = get_goat_requirements(gt, is_male=img_, milk_yield=mg)
            p1, p2, p3 = st.columns(3)
            p1.metric("DP", f"{rp.DP}%"); p2.metric("CP", f"{rp.CP}%"); p3.metric("SE", f"{rp.SE}")
            if st.checkbox("✅ اعتماد", key="ug"):
                animal_choice="ماعز"; production_type=gt; req=rp; img_key="ماعز"; std_key=f"ماعز_{gt}"
        with at[3]:
            st.info("🐪 الإبل: بروتين أقل، ألياف أكثر")
            cmt = st.selectbox("الحالة:", ["نمو","تسمين","حليب","سباق","صيانة"],
                format_func=lambda x: {"نمو":"🐪 نمو","تسمين":"💪 تسمين","حليب":"🍼 حلابة","سباق":"🏃 سباق","صيانة":"🌿 صيانة"}.get(x,x), key="cmt")
            cw = st.number_input("⚖️ الوزن:",100.0,800.0,400.0,25.0,key="cwt")
            cm_ = 5.0
            if cmt == "حليب": cm_ = st.number_input("🥛 الحليب (لتر):",2.0,20.0,5.0,0.5,key="cmk")
            rp = get_camel_requirements(cmt, weight_kg=cw, milk_yield=cm_)
            p1, p2, p3, p4 = st.columns(4)
            p1.metric("DP", f"{rp.DP}%"); p2.metric("CP", f"{rp.CP}%"); p3.metric("SE", f"{rp.SE}"); p4.metric("NDF", f"{rp.NDF}%")
            if st.checkbox("✅ اعتماد", key="ucam"):
                animal_choice="إبل"; production_type=cmt; req=rp; img_key="إبل"; std_key=f"إبل_{cmt}"
        with at[4]:
            ht = st.selectbox("الحالة:", ["رياضة_مكثف","رياضة_عادي","نمو_أمهار","مرضعات","صيانة"],
                format_func=lambda x: {"رياضة_مكثف":"🏇 مكثف","رياضة_عادي":"🏇 عادي","نمو_أمهار":"🐎 أمهار","مرضعات":"🍼 مرضعات","صيانة":"🌿 صيانة"}.get(x,x), key="ht")
            hw = st.number_input("⚖️ الوزن:",200.0,800.0,450.0,25.0,key="hw")
            rp = get_horse_requirements(ht, weight_kg=hw)
            p1, p2, p3 = st.columns(3)
            p1.metric("DP", f"{rp.DP}%"); p2.metric("CP", f"{rp.CP}%"); p3.metric("SE", f"{rp.SE}")
            if st.checkbox("✅ اعتماد", key="uh"):
                animal_choice="خيول"; production_type=ht; req=rp; img_key="خيول"; std_key=f"خيول_{ht}"
        with at[5]:
            ps = st.radio("السلالة:", ["لاحم","بياض"], horizontal=True, key="ps")
            pa = st.number_input("العمر (أسبوع):",1,20,1,1,key="pa")
            rp = get_poultry_requirements(ps, pa)
            p1, p2, p3, p4 = st.columns(4)
            p1.metric("DP", f"{rp.DP}%"); p2.metric("CP", f"{rp.CP}%"); p3.metric("SE", f"{rp.SE}"); p4.metric("Ca", f"{rp.Ca}%")
            if st.checkbox("✅ اعتماد", key="up"):
                animal_choice="دواجن"; production_type=ps; req=rp; img_key="دواجن"
                if ps == "لاحم":
                    std_key = "دواجن_بادي" if pa<=1 else ("دواجن_نامي" if pa<=3 else "دواجن_ناهي")
                else: std_key = "دواجن_بياض"
        with at[6]:
            qs = st.radio("النوع:", ["تسمين","بياض"], horizontal=True, key="qs")
            qa = st.number_input("العمر:",1,8,1,1,key="qa")
            rp = get_quail_requirements(qs, qa)
            p1, p2, p3 = st.columns(3)
            p1.metric("DP", f"{rp.DP}%"); p2.metric("CP", f"{rp.CP}%"); p3.metric("SE", f"{rp.SE}")
            if st.checkbox("✅ اعتماد", key="uq"):
                animal_choice="سمان"; production_type=qs; req=rp; img_key="سمان"; std_key=f"سمان_{qs}"
        with at[7]:
            fs = st.selectbox("النوع:", ["البلطي النيلي","القرموط الأفريقي","الكارب"], key="fs")
            fst = st.selectbox("المرحلة:", ["بادئ زريعة","نمو","تسمين"], key="fst")
            rp = get_fish_requirements(fs, fst)
            p1, p2, p3 = st.columns(3)
            p1.metric("DP", f"{rp.DP}%"); p2.metric("CP", f"{rp.CP}%"); p3.metric("SE", f"{rp.SE}")
            if st.checkbox("✅ اعتماد", key="uf"):
                animal_choice="أسماك"; production_type=fst; req=rp; img_key="أسماك"
                std_key = "أسماك_بادئ" if "بادئ" in fst else ("أسماك_نمو" if "نمو" in fst else "أسماك_تسمين")

        if not animal_choice or not req:
            st.warning("⚠️ اختر حيواناً وفعّل ✅ الاعتماد للمتابعة.")
        else:
            st.markdown(f'<div class="section-title">🎯 المختار: {animal_choice} — {req.name_ar}</div>', unsafe_allow_html=True)
            i1, i2, i3, i4 = st.columns(4)
            i1.metric("DP", f"{req.DP}%"); i2.metric("CP", f"{req.CP}%"); i3.metric("SE", f"{req.SE}"); i4.metric("NDF", f"{req.NDF}%")
            st.info(f"📝 {req.note} | الأساس: {'DP' if use_dp else 'CP'}")
            oil_std_info = get_oil_standard(std_key)
            st.markdown(f"""<div class="oil-info-card"><b>🌰 معيار الزيوت:</b> الأقصى <b>{oil_std_info['max']}%</b> |
                المثالي <b>{oil_std_info['optimal']}%</b> | المرجع: <b>{oil_std_info['source']}</b><br>
                <small>💡 1% زيت ≈ 90 kcal/kg</small></div>""", unsafe_allow_html=True)
            requester_name = st.text_input("👤 اسم طالب العلفة:", placeholder="مزرعة الأمل", key="rq")
            st.markdown('<div class="section-title">🌾 اختيار المكونات</div>', unsafe_allow_html=True)
            sel_ings = []; ing_prices = {}
            for cat_name, items in BIG_FEEDS_LIBRARY.items():
                expanded = any(k in cat_name for k in ["الحبوب","الأكساب","الزيوت"])
                with st.expander(f"📁 {cat_name}", expanded=expanded):
                    sc = st.columns(3)
                    for idx, (ing_name, ing_data) in enumerate(items.items()):
                        with sc[idx % 3]:
                            dc = ing_name in ["ملح الطعام","الحجر الجيري","فوسفات ثنائي الكالسيوم","مضاد سموم فطرية"]
                            if animal_choice in ["أغنام","ماعز","أبقار","إبل"]: dc = dc or (ing_name == "بيكربونات الصوديوم")
                            if animal_choice in ["دواجن","سمان"]: dc = dc or ("بريمكس" in ing_name)
                            if cat_name == "🌰 الزيوت النباتية والحيوانية":
                                st.markdown(f"**{ing_name}**")
                                st.caption(f"⚡ SE={ing_data.get('SE',0):.0f} | {ing_data.get('desc','')[:55]}")
                                ck = st.checkbox("إضافة", value=False, key=f"ck_{animal_choice}_{ing_name}")
                            else:
                                ck = st.checkbox(ing_name, value=dc, key=f"ck_{animal_choice}_{ing_name}")
                            clp = live_prices.get(ing_name, 300.0)
                            if is_owner():
                                pi = st.number_input("$ (سعر الطن)", min_value=5.0, value=float(clp), key=f"p_{animal_choice}_{ing_name}")
                            else:
                                st.markdown(f"💰 السعر: **`${clp:.2f}`** / طن"); pi = clp
                            if ck: sel_ings.append(ing_name); ing_prices[ing_name] = pi
            st.markdown("---")
            if st.button("🚀 تشغيل المحرك الذكي", type="primary", use_container_width=True, key="run_smart"):
                if len(sel_ings) < 3: st.error("⚠️ اختر 3 مكونات على الأقل")
                else:
                    asalt = auto_add_salts_and_minerals(animal_choice, req)
                    for sn, sp in asalt.items():
                        if sn not in sel_ings: sel_ings.append(sn); ing_prices[sn] = live_prices.get(sn, 300.0)
                    cs = requirement_to_standard(req); bl = "DP" if use_dp else "CP"
                    with st.spinner(f"⏳ جاري التركيب على أساس {bl}..."):
                        res = auto_formulate_smart(sel_ings, ing_prices, cs, standard_key=std_key, tolerance=0.3, max_iterations=50)
                    if res["success"]:
                        formula = res["formula"]; actual = res["actual_nutrients"]; cost = res["cost"]
                        total_oil = res.get("total_oil", 0.0); oil_std = res.get("oil_std", oil_std_info)
                        cmp_rows = []; cmp_scores = []
                        labels = {"CP":"بروتين خام CP","DP":"بروتين مهضوم DP","SE":"معادل النشاء SE","NDF":"ألياف NDF","ADF":"ألياف ADF","EE":"دهن EE","ASH":"رماد ASH","Ca":"كالسيوم Ca","P":"فسفور P"}
                        for k, sv in cs.items():
                            cv_ = actual.get(k, 0); diff = cv_-sv; pct = (diff/sv*100) if sv else 0
                            ev = evaluate_difference(pct, nutrient=k)
                            cmp_scores.append({"score": ev["score"]})
                            cmp_rows.append({"العنصر":labels.get(k,k),"المعيار":f"{sv:.2f}","المحسوب":f"{cv_:.2f}","الفرق":f"{diff:+.3f}","الفرق %":f"{pct:+.2f}%","التقييم":ev["label"]})
                        overall = get_overall_rating(cmp_scores); perfect = res.get("perfect_match", False)
                        st.success(f"🎯 مطابقة كاملة!" if perfect else f"✅ تم التركيب — {bl}")
                        st.info(f"🔁 التكرارات: {res['iterations']} | التقييم: **{overall['label']}** ({overall['score']:.0f}%)")
                        e1, e2, e3, e4 = st.columns(4)
                        e1.metric("خطأ DP", f"{res['dp_error']:.3f}%"); e2.metric("خطأ SE", f"{res['se_error']:.3f}")
                        e3.metric("خطأ NDF", f"{res['ndf_error']:.2f}%"); e4.metric("خطأ Ca", f"{res['ca_error']:.3f}%")
                        st.markdown("### 📊 جدول المقارنة")
                        st.dataframe(pd.DataFrame(cmp_rows), use_container_width=True, hide_index=True)
                        st.markdown("### 🌰 تقييم الزيوت")
                        if total_oil > 0:
                            if total_oil > oil_std["max"]: st.error(f"⚠️ تجاوز! {total_oil:.2f}% > {oil_std['max']}%")
                            elif total_oil > oil_std["optimal"]*1.2: st.warning(f"⚡ مرتفع {total_oil:.2f}%")
                            else: st.success(f"✅ مطابق {total_oil:.2f}%")
                            st.caption(f"📖 {oil_std['source']}")
                            for ing, pct in [(i,p) for i,p in formula.items() if i in get_oil_ingredients()]:
                                st.markdown(f'<div class="oil-item">🌰 <b>{ing}:</b> {pct:.2f}% | ≈ {pct*90:.0f} kcal/kg</div>', unsafe_allow_html=True)
                        else: st.info("ℹ️ لا زيوت")
                        st.markdown("#### 🌾 المكونات:")
                        for ing, pct in formula.items():
                            st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.2f}% ({pct*10:.1f} كجم/طن)</div>', unsafe_allow_html=True)
                        st.metric("💰 التكلفة للطن:", f"${cost:.2f} ({cost*local_rate:,.0f} {local_sym})")
                        st.session_state["active_formula"] = formula
                        st.session_state["computed_ton_cost"] = cost
                        st.session_state["active_animal_img"] = ANIMAL_IMAGES.get(img_key, ANIMAL_IMAGES["عام"])
                        st.session_state["active_stage_title"] = f"{animal_choice} — {req.name_ar}"
                        st.markdown("### 📥 تحميل التقارير")
                        d1, d2 = st.columns(2)
                        with d1:
                            try:
                                pdf = pdf_gen.generate_report(formula, req, animal_choice, req.name_ar, cost, city, cost*local_rate, local_sym, requester_name, bl, std_key, True)
                                st.download_button("📥 PDF", pdf, file_name=f"Tawor_{animal_choice}_{datetime.now():%Y%m%d}.pdf", mime="application/pdf", use_container_width=True)
                            except Exception as e: st.error(f"⚠️ PDF: {e}")
                        with d2:
                            try:
                                xl = export_comparison_to_excel(cs, actual, requester_name, animal_choice, req.name_ar, formula, std_key)
                                if xl: st.download_button("📊 Excel", xl, file_name=f"Tawor_{animal_choice}_{datetime.now():%Y%m%d}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                            except Exception as e: st.error(f"⚠️ Excel: {e}")
                        if PLOTLY_AVAILABLE and len(formula) > 1:
                            try:
                                colors = ['#e53935','#8e24aa','#3949ab','#1e88e5','#00897b','#43a047','#7cb342','#fdd835','#fb8c00','#6d4c41','#c62828','#6a1b9a']
                                fig = px.pie(values=list(formula.values()), names=list(formula.keys()), title=f"توزيع — {animal_choice}", color_discrete_sequence=colors)
                                fig.update_traces(textposition='inside', textinfo='percent+label')
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception: pass
                    else: st.error(f"❌ {res['message']}")

    # ═══ المختبر ═══
    with sub_lab:
        def lab_std_key(animal, stage):
            m = {("أبقار","حليب_عالي"):"أبقار_حليب_عالي",("أبقار","حليب_متوسط"):"أبقار_حليب_متوسط",
                ("أبقار","حليب_منخفض"):"أبقار_حليب_منخفض",("أبقار","تسمين_مكثف"):"أبقار_تسمين_مكثف",
                ("أبقار","تسمين_عادي"):"أبقار_تسمين_عادي",("أغنام","تسمين_مكثف"):"أغنام_تسمين_مكثف",
                ("أغنام","تسمين_عادي"):"أغنام_تسمين_عادي",("أغنام","حملان_تيد"):"أغنام_تسمين_عادي",
                ("أغنام","مرضعات"):"أغنام_حليب",("أغنام","حامل_أخير"):"أغنام_صيانة",
                ("أغنام","حامل_متوسط"):"أغنام_صيانة",("أغنام","صيانة"):"أغنام_صيانة",
                ("ماعز","تسمين_جديان"):"ماعز_تسمين",("ماعز","تيوس"):"ماعز_تسمين",
                ("ماعز","حلابة_عالي"):"ماعز_حليب",("ماعز","حلابة_متوسط"):"ماعز_حليب",
                ("ماعز","حامل_أخير"):"ماعز_صيانة",("ماعز","صيانة"):"ماعز_صيانة",
                ("إبل","نمو"):"إبل_نمو",("إبل","تسمين"):"إبل_تسمين",("إبل","حليب"):"إبل_حليب",
                ("إبل","سباق"):"إبل_سباق",("إبل","صيانة"):"إبل_صيانة",
                ("خيول","رياضة_مكثف"):"خيول_رياضة_مكثف",("خيول","رياضة_عادي"):"خيول_رياضة_عادي",
                ("خيول","نمو_أمهار"):"خيول_نمو",("خيول","مرضعات"):"خيول_مرضعات",("خيول","صيانة"):"خيول_صيانة",
                ("دواجن","بادي"):"دواجن_بادي",("دواجن","نامي"):"دواجن_نامي",("دواجن","ناهي"):"دواجن_ناهي",
                ("دواجن","بياض"):"دواجن_بياض",("سمان","تسمين"):"سمان_بادي",("سمان","بياض"):"سمان_بياض",
                ("أسماك","بادئ"):"أسماك_بادئ",("أسماك","نمو"):"أسماك_نمو",("أسماك","تسمين"):"أسماك_تسمين"}
            return m.get((animal,stage), "دواجن_بادي")
        st.markdown('<div class="section-title">🔬 مختبر فحص وتحليل الخلطات</div>', unsafe_allow_html=True)
        st.write("أدخل أوزان مكونات خلطتك، وسيقارنها المحرك مع معايير **NRC/INRA/FAO** ويولّد **الخلطة المثالية** و**ديباجة الجوال**.")
        lab_a = st.selectbox("🐾 الفصيل:", ["أبقار","أغنام","ماعز","إبل","خيول","دواجن","سمان","أسماك"], key="lba")
        lab_req = None; lab_sc = ""; lab_lbl = ""
        if lab_a == "أبقار":
            lab_sc = st.selectbox("الحالة:", ["حليب_عالي","حليب_متوسط","حليب_منخفض","تسمين_مكثف","تسمين_عادي","حمل_أخير","صيانة"],
                format_func=lambda x: {"حليب_عالي":"🐄 عالية","حليب_متوسط":"🐄 متوسطة","حليب_منخفض":"🐄 منخفضة","تسمين_مكثف":"💪 مكثف","تسمين_عادي":"💪 عادي","حمل_أخير":"🤰 حمل","صيانة":"🌿 صيانة"}.get(x,x), key="lcs")
            c1, c2 = st.columns(2); lp = {}
            with c1:
                if "حليب" in lab_sc: lp["milk_yield"] = st.number_input("🥛 الحليب:",5.0,60.0,20.0,1.0,key="lcm")
            with c2: lp["weight_kg"] = st.number_input("⚖️ الوزن:",200.0,900.0,500.0,25.0,key="lcw")
            lab_req = get_cattle_requirements(lab_sc, **lp); lab_lbl = lab_req.name_ar
        elif lab_a == "أغنام":
            lg = st.radio("الجنس:", ["ذكر","أنثى"], horizontal=True, key="lsg"); lm = "ذكر" in lg
            if lm:
                lab_sc = st.selectbox("الحالة:", ["تسمين_مكثف","تسمين_عادي","حملان_تيد"],
                    format_func=lambda x: {"تسمين_مكثف":"💪 مكثف","تسمين_عادي":"💪 عادي","حملان_تيد":"🐑 تيد"}.get(x,x), key="lst_m")
            else:
                lab_sc = st.selectbox("الحالة:", ["مرضعات","حامل_أخير","حامل_متوسط","صيانة"],
                    format_func=lambda x: {"مرضعات":"🍼 مرضعات","حامل_أخير":"🤰 حامل","حامل_متوسط":"🤰 متوسطة","صيانة":"🌿 صيانة"}.get(x,x), key="lst_f")
            ll = 1
            if lab_sc == "مرضعات": ll = st.number_input("👶 المواليد:",1,3,1,1,key="lsl")
            lw = st.number_input("⚖️ الوزن:",15.0,120.0,50.0,5.0,key="lsw")
            lab_req = get_sheep_requirements(lab_sc, is_male=lm, weight_kg=lw, litter_size=ll); lab_lbl = lab_req.name_ar
        elif lab_a == "ماعز":
            lg = st.radio("الجنس:", ["ذكر","أنثى"], horizontal=True, key="lgg"); lm = "ذكر" in lg; lmg = 0.0
            if lm:
                lab_sc = st.selectbox("الحالة:", ["تسمين_جديان","تيوس"],
                    format_func=lambda x: {"تسمين_جديان":"💪 جديان","تيوس":"🐐 تيوس"}.get(x,x), key="lgt_m")
            else:
                lab_sc = st.selectbox("الحالة:", ["حلابة_عالي","حلابة_متوسط","حامل_أخير","صيانة"],
                    format_func=lambda x: {"حلابة_عالي":"🍼 عالي","حلابة_متوسط":"🍼 متوسط","حامل_أخير":"🤰 حامل","صيانة":"🌿 صيانة"}.get(x,x), key="lgt_f")
                if "حلابة" in lab_sc: lmg = st.number_input("🥛 الحليب:",0.5,8.0,2.0,0.25,key="lgm")
            lab_req = get_goat_requirements(lab_sc, is_male=lm, milk_yield=lmg); lab_lbl = lab_req.name_ar
        elif lab_a == "إبل":
            lab_sc = st.selectbox("الحالة:", ["نمو","تسمين","حليب","سباق","صيانة"],
                format_func=lambda x: {"نمو":"🐪 نمو","تسمين":"💪 تسمين","حليب":"🍼 حلابة","سباق":"🏃 سباق","صيانة":"🌿 صيانة"}.get(x,x), key="lcmt")
            lcw = st.number_input("⚖️ الوزن:",100.0,800.0,400.0,25.0,key="lcwt")
            lcm = 5.0
            if lab_sc == "حليب": lcm = st.number_input("🥛 الحليب:",2.0,20.0,5.0,0.5,key="lcmk")
            lab_req = get_camel_requirements(lab_sc, weight_kg=lcw, milk_yield=lcm); lab_lbl = lab_req.name_ar
        elif lab_a == "خيول":
            lab_sc = st.selectbox("الحالة:", ["رياضة_مكثف","رياضة_عادي","نمو_أمهار","مرضعات","صيانة"],
                format_func=lambda x: {"رياضة_مكثف":"🏇 مكثف","رياضة_عادي":"🏇 عادي","نمو_أمهار":"🐎 أمهار","مرضعات":"🍼 مرضعات","صيانة":"🌿 صيانة"}.get(x,x), key="lht")
            lhw = st.number_input("⚖️ الوزن:",200.0,800.0,450.0,25.0,key="lhwt")
            lab_req = get_horse_requirements(lab_sc, weight_kg=lhw); lab_lbl = lab_req.name_ar
        elif lab_a == "دواجن":
            lps = st.radio("السلالة:", ["لاحم","بياض"], horizontal=True, key="lps")
            lpa = st.number_input("العمر:",1,20,1,1,key="lpa")
            lab_req = get_poultry_requirements(lps, lpa); lab_lbl = lab_req.name_ar
            if lps == "لاحم": lab_sc = "بادي" if lpa<=1 else ("نامي" if lpa<=3 else "ناهي")
            else: lab_sc = "بياض"
        elif lab_a == "سمان":
            lqs = st.radio("النوع:", ["تسمين","بياض"], horizontal=True, key="lqs")
            lqa = st.number_input("العمر:",1,8,1,1,key="lqa")
            lab_req = get_quail_requirements(lqs, lqa); lab_lbl = lab_req.name_ar
            lab_sc = "تسمين" if lqs == "تسمين" else "بياض"
        elif lab_a == "أسماك":
            lfs = st.selectbox("النوع:", ["البلطي النيلي","القرموط الأفريقي","الكارب"], key="lfs")
            lfst = st.selectbox("المرحلة:", ["بادئ زريعة","نمو","تسمين"], key="lfst")
            lab_req = get_fish_requirements(lfs, lfst); lab_lbl = lab_req.name_ar
            lab_sc = "بادئ" if "بادئ" in lfst else ("نمو" if "نمو" in lfst else "تسمين")

        if lab_req:
            tk = st.columns(6)
            tk[0].metric("DP", f"{lab_req.DP}%"); tk[1].metric("CP", f"{lab_req.CP}%"); tk[2].metric("SE", f"{lab_req.SE}")
            tk[3].metric("NDF", f"{lab_req.NDF}%"); tk[4].metric("Ca", f"{lab_req.Ca}%"); tk[5].metric("P", f"{lab_req.P}%")
            st.info(f"📝 {lab_req.note}")
            lsk = lab_std_key(lab_a, lab_sc); los = get_oil_standard(lsk)
            st.markdown(f"""<div class="oil-info-card"><b>🌰 معيار الزيوت:</b> الأقصى <b>{los['max']}%</b> |
                المثالي <b>{los['optimal']}%</b> | {los['source']}</div>""", unsafe_allow_html=True)

            lc = st.selectbox("🌍 الدولة:", list(EXCHANGE_RATES.keys()), key="lco")
            lcity = st.text_input("🏙️ المدينة:", "الخرطوم" if lc=="السودان" else "طرابلس", key="lcity")
            lri = EXCHANGE_RATES.get(lc, {"rate":1.0,"sym":"USD"}); lr = lri["rate"]; lsym = lri["sym"]
            lmp = get_market_prices(lc, lcity, "")
            li = {}; lpr = {}
            for cat_name, items in BIG_FEEDS_LIBRARY.items():
                exp = any(k in cat_name for k in ["الحبوب","الأكساب","الزيوت"])
                with st.expander(f"📁 {cat_name}", expanded=exp):
                    for ing_name in items.keys():
                        cw, cp = st.columns([0.55, 0.45])
                        with cw: li[ing_name] = st.number_input(f"⚖️ {ing_name} (كجم)", min_value=0.0, value=0.0, step=5.0, key=f"lw_{lab_a}_{ing_name}")
                        with cp:
                            dp = lmp.get(ing_name, 300.0)
                            lpr[ing_name] = st.number_input(f"💰 $/طن", min_value=0.0, value=float(dp), step=10.0, key=f"lp_{lab_a}_{ing_name}")
            st.markdown("---")
            if st.button("🧪 تشغيل التحليل + المقارنة مع الأمثل", type="primary", use_container_width=True, key="lrun"):
                ltw = sum(li.values())
                if ltw <= 0: st.warning("⚠️ أدخل أوزاناً أكبر من الصفر")
                else:
                    fl = {i: (w/ltw*100) for i, w in li.items() if w > 0}
                    al = compute_formula_nutrients(fl); tl = requirement_to_standard(lab_req)
                    ac = sum((p/100.0)*lpr.get(i, 300.0) for i, p in fl.items())
                    lbl = {"CP":"بروتين خام CP","DP":"بروتين مهضوم DP","SE":"معادل النشاء SE","NDF":"ألياف NDF","ADF":"ألياف ADF","EE":"دهن EE","ASH":"رماد ASH","Ca":"كالسيوم Ca","P":"فسفور P"}
                    cr = []; scs = []
                    for k, sv in tl.items():
                        cv_ = al.get(k, 0); diff = cv_-sv; pct = (diff/sv*100) if sv else 0
                        ev = evaluate_difference(pct, nutrient=k); scs.append({"score": ev["score"]})
                        cr.append({"العنصر":lbl.get(k,k),"المعيار":f"{sv:.2f}","المحسوب":f"{cv_:.2f}","الفرق":f"{diff:+.3f}","الفرق %":f"{pct:+.2f}%","التقييم":ev["label"]})
                    ov = get_overall_rating(scs)
                    st.success(f"🔬 إجمالي: **{ltw:.1f} كجم**")
                    st.info(f"🏆 التقييم: **{ov['label']}** ({ov['score']:.0f}%)")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("💰 تكلفة الطن", f"${ac:.2f}", f"{ac*lr:,.0f} {lsym}")
                    m2.metric("⚖️ الوزن", f"{ltw:.0f} كجم"); m3.metric("📦 المكونات", len(fl))
                    st.markdown("### 📊 تقرير الفحص")
                    st.dataframe(pd.DataFrame(cr), use_container_width=True, hide_index=True)
                    st.markdown("### 🌾 المكونات")
                    for ing, pct in sorted(fl.items(), key=lambda x: -x[1]):
                        st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.2f}% ({pct*ltw/100:.1f} كجم)</div>', unsafe_allow_html=True)
                    tot_oil = compute_total_oil_percentage(fl)
                    st.markdown("### 🌰 تقييم الزيوت")
                    if tot_oil > 0:
                        if tot_oil > los["max"]: st.error(f"⚠️ تجاوز! {tot_oil:.2f}% > {los['max']}%")
                        elif tot_oil > los["optimal"]*1.2: st.warning(f"⚡ مرتفع: {tot_oil:.2f}%")
                        else: st.success(f"✅ مطابق: {tot_oil:.2f}%")
                    else: st.info("ℹ️ لا زيوت")

                    st.markdown("---")
                    st.markdown("### 🎯 المقارنة مع الخلطة المثالية")
                    if st.checkbox("🚀 تشغيل المقارنة", value=True, key="en_opt"):
                        av = [i for i, w in li.items() if w > 0]
                        if len(av) < 3: st.warning("⚠️ تحتاج 3 مكونات على الأقل")
                        else:
                            asalt = auto_add_salts_and_minerals(lab_a, lab_req)
                            for sn, _ in asalt.items():
                                if sn not in av: av.append(sn)
                            with st.spinner("⏳ توليد الأمثل..."):
                                opt = auto_formulate_smart(av, lpr, tl, standard_key=lsk, tolerance=0.3, max_iterations=50)
                            if opt["success"]:
                                of = opt["formula"]; oa = opt["actual_nutrients"]; oc = opt["cost"]
                                cd = ac - oc; sp = (cd/ac*100) if ac > 0 else 0
                                c1, c2, c3 = st.columns(3)
                                c1.metric("💰 خلطتك", f"${ac:.2f}"); c2.metric("🎯 المثالية", f"${oc:.2f}")
                                if cd > 0: c3.metric("💵 التوفير", f"${cd:.2f}", f"↓ {sp:.1f}%")
                                else: c3.metric("✅ خلطتك أفضل", f"${abs(cd):.2f}")
                                st.markdown("#### 📊 مقارنة المكونات")
                                alli = set(list(fl.keys())+list(of.keys()))
                                cd_data = [{"المكون":i,"خلطتك %":f"{fl.get(i,0):.2f}","المثالية %":f"{of.get(i,0):.2f}","الفرق":f"{of.get(i,0)-fl.get(i,0):+.2f}"} for i in sorted(alli)]
                                st.dataframe(pd.DataFrame(cd_data), use_container_width=True, hide_index=True)
                                st.markdown("#### 🧬 مقارنة القيم")
                                vc = [{"العنصر":lbl.get(k,k),"المعيار":f"{tl[k]:.2f}","خلطتك":f"{al.get(k,0):.2f}","المثالية":f"{oa.get(k,0):.2f}"} for k in tl.keys()]
                                st.dataframe(pd.DataFrame(vc), use_container_width=True, hide_index=True)
                                if PLOTLY_AVAILABLE:
                                    try:
                                        nc = [n for n in ["DP","CP","SE","NDF","Ca","P"] if n in tl]
                                        fg = go.Figure(data=[
                                            go.Bar(name='المعيار', x=nc, y=[tl[n] for n in nc], marker_color='#1976d2'),
                                            go.Bar(name='خلطتك', x=nc, y=[al.get(n,0) for n in nc], marker_color='#43a047'),
                                            go.Bar(name='المثالية', x=nc, y=[oa.get(n,0) for n in nc], marker_color='#e65100')])
                                        fg.update_layout(title="ثلاثية المقارنة", barmode='group', height=420)
                                        st.plotly_chart(fg, use_container_width=True)
                                    except Exception: pass
                            else: st.warning(f"⚠️ {opt['message']}")

                    st.markdown("---")
                    st.markdown("### 📥 تصدير")
                    e1, e2, e3, e4 = st.columns(4)
                    with e1:
                        try:
                            pb_ = pdf_gen.generate_report(fl, lab_req, lab_a, lab_lbl, ac, lcity, ac*lr, lsym, "تقرير مختبر", "DP", lsk, True)
                            st.download_button("📄 PDF", pb_, file_name=f"Lab_{lab_a}_{datetime.now():%Y%m%d}.pdf", mime="application/pdf", use_container_width=True)
                        except Exception as e: st.error(f"⚠️ {e}")
                    with e2:
                        try:
                            xb = export_comparison_to_excel(tl, al, "مختبر", lab_a, lab_lbl, fl, lsk)
                            if xb: st.download_button("📊 Excel", xb, file_name=f"Lab_{lab_a}_{datetime.now():%Y%m%d}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                        except Exception as e: st.error(f"⚠️ {e}")
                    with e3:
                        try:
                            bb = generate_bag_label_pdf(fl, lab_req, lab_a, lab_lbl, ac, ac*lr, lsym, lcity, "مختبر")
                            st.download_button("🏷️ ديباجة", bb, file_name=f"Bag_{lab_a}_{datetime.now():%Y%m%d}.pdf", mime="application/pdf", use_container_width=True)
                        except Exception as e: st.error(f"⚠️ {e}")
                    with e4:
                        sh = f"🔬 مختبر Tawor\n{lab_a} — {lab_lbl}\nDP: {al.get('DP',0):.2f}%\nCP: {al.get('CP',0):.2f}%\nSE: {al.get('SE',0):.2f}\n💰 ${ac:.2f}/طن\n{ov['label']}\n🕌 {DUA_SHORT}"
                        st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(sh)}" target="_blank" style="text-decoration:none;"><button style="background:#25D366; color:white; padding:11px; border-radius:8px; border:none; width:100%; font-weight:bold; cursor:pointer;">📲 واتساب</button></a>', unsafe_allow_html=True)

                    if PLOTLY_AVAILABLE and len(fl) > 1:
                        st.markdown("### 📈 الرسوم")
                        cc1, cc2 = st.columns(2)
                        with cc1:
                            try:
                                colors = ['#e53935','#8e24aa','#3949ab','#1e88e5','#00897b','#43a047','#7cb342','#fdd835','#fb8c00','#6d4c41','#c62828','#6a1b9a']
                                fg = px.pie(values=list(fl.values()), names=list(fl.keys()), title=f"توزيع — {lab_a}", color_discrete_sequence=colors)
                                fg.update_traces(textposition='inside', textinfo='percent+label')
                                st.plotly_chart(fg, use_container_width=True)
                            except Exception: pass
                        with cc2:
                            try:
                                nc2 = [n for n in ["DP","CP","SE","NDF","Ca","P"] if n in tl]
                                fb = go.Figure(data=[go.Bar(name='المعيار', x=nc2, y=[tl[n] for n in nc2], marker_color='#1976d2'),
                                    go.Bar(name='المحسوب', x=nc2, y=[al.get(n,0) for n in nc2], marker_color='#43a047')])
                                fb.update_layout(title="المعيار vs المحسوب", barmode='group', height=400)
                                st.plotly_chart(fb, use_container_width=True)
                            except Exception: pass

                    st.markdown("---")
                    st.markdown("### 💡 نصائح")
                    dpe = abs(al.get("DP",0) - lab_req.DP); see = abs(al.get("SE",0) - lab_req.SE)
                    if dpe < 0.3 and see < 2: st.success("🎯 مطابق تماماً")
                    elif dpe < 1: st.info("✅ جيد — تعديل طفيف")
                    else: st.warning("⚠️ يحتاج مراجعة — أعد توزيع مصادر البروتين")

# ═══ تبويبات أخرى ═══
with tab_map["🌰 مكتبة الزيوت"]:
    st.markdown('<div class="section-title">🌰 مكتبة الزيوت</div>', unsafe_allow_html=True)
    rows = [{"الحيوان": k, "الأقصى": f"{v['max']}%", "المثالي": f"{v['optimal']}%", "المرجع": v["source"]} for k, v in MAX_OIL_PERCENTAGE.items()]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    oils = get_oil_ingredients(); dcp = get_market_prices("السودان", "الخرطوم", "")
    for cat, ol in OIL_CATEGORIES.items():
        st.markdown(f"#### {cat}")
        for on in ol:
            if on in oils:
                oi = oils[on]
                with st.expander(f"🌰 {on}"):
                    c1, c2, c3 = st.columns(3)
                    with c1: st.metric("SE", f"{oi.get('SE',0):.0f}"); st.metric("الدهن", "100%")
                    with c2: st.metric("kcal/kg", f"{oi.get('SE',0)*41:.0f}"); st.metric("السعر", f"${dcp.get(on,0):.0f}/طن")
                    with c3: st.metric("أقصى دواجن", f"{oi.get('max_poultry','N/A')}%"); st.metric("أقصى مجترات", f"{oi.get('max_ruminant','N/A')}%")
                    st.info(f"📝 {oi.get('desc','')}"); st.caption(f"📖 {oi.get('source','NRC')}")

with tab_map["🍼 بدائل الحليب"]:
    st.markdown('<div class="section-title">🍼 بدائل الحليب</div>', unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
        mra = st.selectbox("نوع الحيوان:", list(MILK_REPLACER_STANDARDS.keys()), key="mra")
        mrv = st.number_input("الكمية (كجم):",1.0,10000.0,100.0,10.0,key="mrv")
    with m2:
        sm = MILK_REPLACER_STANDARDS[mra]
        st.markdown(f"""<div class="price-card"><b>📊 {mra}:</b><br>▪️ بروتين: <b>{sm['CP']}%</b><br>
            ▪️ دهن: <b>{sm['Fat']}%</b><br>▪️ لاكتوز: <b>{sm['Lactose']}%</b><br><small>{sm['notes']}</small></div>""", unsafe_allow_html=True)
    ms = []; mc = st.columns(3)
    for i, (name, data) in enumerate(MILK_REPLACER_INGREDIENTS.items()):
        with mc[i % 3]:
            dflt = name in ["حليب مجفف منزوع الدسم","حليب مجفف كامل الدسم","شرش حليب مجفف","زيت جوز الهند","زيت النخيل","بريمكس فيتامينات","كالسيوم كربونات","فوسفات ثنائي الكالسيوم","ملح طعام"]
            if st.checkbox(f"{name} — ${data['price']}", value=dflt, key=f"mr_{name}"): ms.append(name)
    if st.button("🧪 تشغيل التركيب", type="primary", use_container_width=True, key="mrrun"):
        if len(ms) < 3: st.warning("⚠️ اختر 3 مكونات على الأقل")
        else:
            r = formulate_milk_replacer(mra, mrv, ms)
            if r["success"]:
                st.success(f"✅ تم التركيب لـ ({mra})")
                for ing, pct in r["formula"].items():
                    st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.2f}% ({pct*mrv/100:.2f} كجم)</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                c1.metric("💰 لـ 100 كجم:", f"${r['cost_per_100kg']:.2f}"); c2.metric("💰 لكل كجم:", f"${r['cost_per_kg']:.3f}")
            else: st.error(f"❌ {r['message']}")

with tab_map["📷 المختبر الذكي"]:
    st.markdown('<div class="section-title">📷 المختبر الذكي OCR</div>', unsafe_allow_html=True)
    if not OCR_AVAILABLE:
        st.error("⚠️ pytesseract غير مثبتة"); st.code("pip install pytesseract opencv-python-headless", language="bash")
    else:
        up = st.file_uploader("📤 ارفع صورة:", type=["jpg","jpeg","png"])
        if up:
            st.image(up, use_container_width=True)
            if st.button("🔍 تحليل", type="primary", use_container_width=True, key="ocr_run"):
                with st.spinner("جاري التحليل..."):
                    r = extract_ingredients_from_image(up.read())
                if r["success"]:
                    st.success(f"✅ {r['count']} مادة")
                    if r["ingredients"]:
                        st.dataframe(pd.DataFrame([{"المادة":k,"النسبة":f"{v:.2f}%"} for k,v in r["ingredients"].items()]), use_container_width=True, hide_index=True)
                        n = compute_formula_nutrients(r["ingredients"])
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("CP", f"{n['CP']:.2f}%"); c2.metric("DP", f"{n['DP']:.2f}%"); c3.metric("SE", f"{n['SE']:.2f}"); c4.metric("NDF", f"{n['NDF']:.2f}%")
                    with st.expander("📝 النص الخام"): st.text(r.get("raw_text",""))
                else: st.error(f"❌ {r['message']}")

if is_owner():
    with tab_map["📊 البورصة"]:
        st.markdown('<div class="section-title">📊 البورصة</div>', unsafe_allow_html=True)
        t1, t2 = st.tabs(["🐄 الماشية","🥩 المنتجات"])
        with t1:
            for a, p in list(st.session_state["livestock_prices"].items()):
                st.session_state["livestock_prices"][a] = st.number_input(f"{a}", min_value=0.0, value=float(p), step=0.1, key=f"lv_{a}")
        with t2:
            for p, pr in list(st.session_state["products_prices"].items()):
                st.session_state["products_prices"][p] = st.number_input(f"{p}", min_value=0.0, value=float(pr), step=0.05, key=f"pr_{p}")

    with tab_map["🏭 المستودعات"]:
        st.markdown('<div class="section-title">🏭 المستودعات</div>', unsafe_allow_html=True)
        inv = st.session_state["inventory"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("إجمالي", len(inv))
        low = sum(1 for v in inv.values() if v.get("quantity",0) < 5); c2.metric("منخفضة", low)
        crit = sum(1 for v in inv.values() if v.get("quantity",0) <= 0); c3.metric("نفذت", crit)
        c4.metric("آمنة", len(inv)-low-crit)
        cols = st.columns(3)
        for i, (n, d) in enumerate(list(inv.items())[:90]):
            with cols[i % 3]:
                q = d["quantity"] if isinstance(d, dict) else d
                bd = "🔴" if q<=0 else ("🟡" if q<5 else "🟢")
                st.markdown(f"{bd} **{n}**: {q:.1f} طن")
                nq = st.number_input("تحديث:", min_value=0.0, value=float(q), key=f"inv_{n}", label_visibility="collapsed")
                if isinstance(inv[n], dict): inv[n]["quantity"] = nq

    with tab_map["🧾 الفواتير"]:
        st.markdown('<div class="section-title">🧾 الفواتير</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: cl = st.text_input("العميل:", "مزرعة الأمل", key="inv_c")
        with c2: tn = st.number_input("الطن:", 0.1, 1000.0, 2.0, 0.5, key="inv_t")
        with c3: pf = st.number_input("هامش $/طن:", 0.0, 1000.0, 50.0, key="inv_p")
        sl = st.session_state["computed_ton_cost"] + pf; tt = sl * tn
        st.markdown(f"""<div class="price-card"><h4>🧾 فاتورة</h4><p><b>العميل:</b> {cl}</p><p><b>الطن:</b> {tn}</p>
            <p><b>سعر الطن:</b> ${sl:.2f}</p><p style="font-size:1.3rem;color:#1b5e20;"><b>الإجمالي:</b> ${tt:.2f}</p></div>""", unsafe_allow_html=True)

    with tab_map["🖨️ الديباجة"]:
        st.markdown('<div class="section-title">🖨️ الديباجة</div>', unsafe_allow_html=True)
        br = st.text_input("البراند:", APP_NAME, key="bag_b")
        st.markdown(f"""<div style="border:3px dashed #1b5e20; padding:30px; border-radius:15px; background:linear-gradient(135deg,#f1f8e9,#e8f5e9); direction:rtl; text-align:center;">
            <img src="{st.session_state['active_animal_img']}" style="width:100%; max-height:200px; object-fit:cover; border-radius:12px; margin-bottom:15px;">
            <h2 style="color:#1b5e20;">🌟 {br} 🌟</h2>
            <h3 style="color:#c62828;">{SUPERVISOR} — {SUPERVISOR_TITLE}</h3>
            <p style="background:#e8f5e9; padding:12px; border-radius:8px; color:#1b5e20; font-weight:bold;">🎯 {st.session_state['active_stage_title']}</p>
            <small style="color:#666;">📅 {datetime.now():%Y-%m-%d}</small><br>
            <small style="color:#c62828;">🤲 {DUA_SHORT}</small></div>""", unsafe_allow_html=True)
        if st.session_state.get("active_formula"):
            st.markdown("### 🏷️ توليد ديباجة الجوال PDF")
            if st.button("📄 توليد", type="primary", use_container_width=True, key="genbag"):
                try:
                    bb = generate_bag_label_pdf(st.session_state["active_formula"], None, st.session_state["active_stage_title"], st.session_state["active_stage_title"], st.session_state["computed_ton_cost"], st.session_state["computed_ton_cost"]*600, "SDG", "—", "—")
                    st.download_button("📥 تحميل الديباجة", bb, file_name=f"Bag_{datetime.now():%Y%m%d}.pdf", mime="application/pdf", use_container_width=True)
                except Exception as e: st.error(f"⚠️ {e}")

    with tab_map["📈 التحليلات"]:
        st.markdown('<div class="section-title">📈 التحليلات</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("الخلطات", "1,247"); c2.metric("متوسط التكلفة", "$285"); c3.metric("التوفير", "18%"); c4.metric("رضا", "96%")
        if PLOTLY_AVAILABLE:
            usage = pd.DataFrame({'المادة':['ذرة','صويا','نخالة','زيوت','أملاح','أخرى'],'نسبة':[42,23,14,8,8,5]})
            st.plotly_chart(px.pie(usage, values='نسبة', names='المادة', color_discrete_sequence=px.colors.sequential.Greens), use_container_width=True)

    with tab_map["🐔 مزارع الدجاج"]:
        st.markdown('<div class="section-title">🐔 مزارع الدجاج</div>', unsafe_allow_html=True)
        with st.expander("➕ إضافة مزرعة"):
            nfn = st.text_input("الاسم:", key="nfn"); nfo = st.text_input("المالك:", key="nfo")
            nfp = st.text_input("واتساب:", WHATSAPP_NUMBER, key="nfp")
            if st.button("💾 حفظ", key="nfs") and nfn:
                st.session_state["broiler_farms"][nfn] = {"owner":nfo,"owner_phone":nfp,"data":{"age":1,"birds":1000,"weight_kg":0.045,"feed_kg":0.0,"dead":0,"temp":33.0,"hum":65.0}}
                st.success(f"✅ {nfn}"); st.rerun()
        if st.session_state["broiler_farms"]:
            farms = list(st.session_state["broiler_farms"].keys())
            sel = st.selectbox("اختر مزرعة:", [""] + farms, key="bsel")
            if sel:
                d = st.session_state["broiler_farms"][sel]["data"]
                b1, b2 = st.columns(2)
                with b1:
                    d["age"] = st.number_input("العمر:",1,60,d["age"],key="ba")
                    d["birds"] = st.number_input("الطيور:",1,value=d["birds"],key="bb")
                    d["weight_kg"] = st.number_input("الوزن:",0.0,10.0,float(d["weight_kg"]),0.01,key="bw")
                    d["feed_kg"] = st.number_input("العلف:",0.0,float(d["feed_kg"]),100.0,key="bf")
                with b2:
                    d["dead"] = st.number_input("النافق:",0,value=d["dead"],key="bd")
                    d["temp"] = st.number_input("الحرارة:",10.0,45.0,float(d["temp"]),key="bt")
                    d["hum"] = st.number_input("الرطوبة:",20.0,90.0,float(d["hum"]),key="bh")
                al = d["birds"]-d["dead"]; gn = al*(d["weight_kg"]-0.045)
                adg = ((d["weight_kg"]-0.045)*1000/d["age"]) if d["age"]>0 else 0
                fcr = (d["feed_kg"]/gn) if gn>0 else 0
                liv = 100-(d["dead"]/d["birds"]*100)
                ep = ((liv*d["weight_kg"])/(d["age"]*fcr)*100) if d["age"]>0 and fcr>0 else 0
                k1, k2, k3 = st.columns(3)
                k1.metric("ADG (جم)", f"{adg:.1f}"); k2.metric("FCR", f"{fcr:.2f}"); k3.metric("EPEF", f"{ep:.0f}")

    with tab_map["💬 التعليقات"]:
        st.markdown('<div class="section-title">💬 التعليقات</div>', unsafe_allow_html=True)
        st.text_area("الحالية:", value=st.session_state["shared_comments"], height=200, disabled=True, key="cv")
        nc = st.text_area("جديد:", key="cn")
        if st.button("➕ نشر", key="cpost") and nc:
            st.session_state["shared_comments"] += f"\n• [{datetime.now():%Y-%m-%d %H:%M}]: {nc}"; st.rerun()

if "📚 المراجع" in tab_map:
    with tab_map["📚 المراجع"]:
        st.markdown('<div class="section-title">📚 المراجع</div>', unsafe_allow_html=True)
        st.markdown("""### المراجع المعتمدة:
- **NRC (2012)** — Nutrient Requirements of Swine
- **NRC (2007)** — Small Ruminants
- **NRC (2001)** — Dairy Cattle
- **NRC (2007)** — Horses
- **NRC (1994)** — Poultry
- **INRA (2018)** — Feeding System for Ruminants
- **FAO (2010)** — Camel Nutrition
- **Ross 308 (2020)** — Broiler Handbook
- **McDonald et al. (2011)** — Animal Nutrition
- **Van Soest (1994)** — Nutritional Ecology

### 📖 الزيوت:
- NRC 2012 — Fat in Animal Nutrition
- INRA 2018 — Lipids in Ruminant Diets
- Palmquist (2006) — Milk Fat Depression""")

if "💡 المساعدة" in tab_map:
    with tab_map["💡 المساعدة"]:
        st.markdown('<div class="section-title">💡 المساعدة</div>', unsafe_allow_html=True)
        st.markdown(f"""### الأسئلة الشائعة:
- **كيف أبدأ؟** اختر الحيوان ← الحالة ← ✅ الاعتماد
- **DP أم CP؟** DP أدق، CP أسهل
- **الزيوت؟** راجع تبويب "🌰 مكتبة الزيوت"
- **المختبر؟** تبويب "🔬 تركيب الأعلاف والمختبر" ← مختبر
- **ديباجة الجوال؟** من نتائج المختبر، زر "🏷️ ديباجة"

### 🔧 الدعم
📧 {OWNER_EMAIL}
📱 {WHATSAPP_NUMBER}

### 🕌 دعاء
{DUA_FULL}""")

if "📖 الدليل" in tab_map:
    with tab_map["📖 الدليل"]:
        st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
        st.markdown(f"""### الغرض
**{APP_NAME}** — منصة ذكية لتركيب الأعلاف بأقل تكلفة.

### الميزات
- 🐄 **8 قطاعات**: أبقار، أغنام، ماعز، إبل، خيول، دواجن، سمان، أسماك
- 🌰 **16 زيتاً** بمعايير NRC/INRA/FAO
- 🧬 **احتياجات متخصصة** لكل حيوان
- 🧠 **محرك ذكي**: DP + SE + NDF + ADF + Ca + P
- 🔬 **مختبر** + مقارنة مع الخلطة المثالية
- 🏷️ **ديباجة جوال PDF** للطباعة
- 📷 **OCR** لتحليل الصور
- 📄 **PDF احترافي** مع ختم وQR
- ⚡ **حساب kcal/kg**

### التقييمات
🎯 مطابق (0-0.5%) | 🌟 ممتاز (0.5-2%) | ✅ جيد (2-5%) | 🟢 جيد (5-10%)

### كود المالك
`{OWNER_CODE}`""")

st.markdown(f'<div class="mini-signature">🌾 {APP_NAME} | {SUPERVISOR} © 2026</div>', unsafe_allow_html=True)
st.markdown(f'<div class="dua-fixed-banner">🤲 {DUA_SHORT} 🤲</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
