# ═══════════════════════════════════════════════════════════════════════
# تاور نولجي TAWOR NOLOGY 11.12
# د. عبدالقادر إسماعيل تاور
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
# ═══════════════════════════════════════════════════════════════════════
# جديد v11.12:
#   ✅ فيديو ترحيبي تلقائي (intro.mp4) + شرح صوتي
#   ✅ تقييد تحميل PDF (يتطلب موافقة المالك)
#   ✅ أزرار التواصل والاستشارة مع كل PDF
#   ✅ إضافة خميرة الخبز + علف الدجاج الجاهز للمكتبة
#   ✅ إسطبلات 3D كاملة للخيول
#   ✅ صور حيوانات حقيقية مع أسهم القياس
# ═══════════════════════════════════════════════════════════════════════

import streamlit as st
import numpy as np, pandas as pd, io, os, re, base64, tempfile
import traceback, warnings, json, threading, random, hashlib, hmac
import time as _time
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Tuple, Any, Union, Set

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════
# استيراد المكتبات
# ═══════════════════════════════════════════════════════════════════════

try:
    from scipy.optimize import linprog, minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

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
    from matplotlib.patches import Circle, Wedge, Ellipse
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
    from openpyxl.styles import Font, PatternFill, Alignment
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

# ═══════════════════════════════════════════════════════════════════════
# الثوابت العامة
# ═══════════════════════════════════════════════════════════════════════

DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي ابتسام"
DUA_FULL = "رحم الله والدي إسماعيل تاور وأختي ابتسام وأسكنهما فسيح جناته"
DUA_QURAN = "﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾"
DUA_VERSE = "﴿ وَقُل رَّبِّ ارْحَمْهُمَا كَمَا رَبَّيَانِي صَغِيرًا ﴾"

APP_NAME = "تاور نولجي Tawor Nology"
APP_TAGLINE = "للإنتاج الحيواني وتغذية الحيوان"
APP_VERSION = "11.12"
SUPERVISOR = "د. عبدالقادر إسماعيل تاور"
SUPERVISOR_TITLE = "اختصاصي تغذية الحيوان"
PLATFORM_URL = "https://tawor-nology.streamlit.app"
WHATSAPP_NUMBER = "+249123533489"
OWNER_EMAIL = "abukram128@gmail.com"

st.set_page_config(page_title=f"{APP_NAME} | {APP_TAGLINE}", page_icon="🌾",
    layout="wide", initial_sidebar_state="collapsed")

# ═══════════════════════════════════════════════════════════════════════
# الأمان
# ═══════════════════════════════════════════════════════════════════════

def _sha256(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def _get_owner_code_hash():
    try:
        _blob = "Nzg2MjAy"
        return _sha256(base64.b64decode(_blob).decode()[::-1])
    except Exception:
        return None

def check_owner_code(user_input):
    if not user_input:
        audit_log("LOGIN_EMPTY", "")
        return False
    expected = _get_owner_code_hash()
    if not expected:
        return False
    ok = hmac.compare_digest(_sha256(user_input.strip()), expected)
    audit_log("LOGIN_OK" if ok else "LOGIN_FAIL", "owner")
    return ok

def audit_log(event, details=""):
    try:
        with open("tawor_audit.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {event} | {details[:200]}\n")
    except Exception:
        pass

def check_rate_limit(key, max_calls=30, window=60):
    now = _time.time()
    skey = f"_rl_{key}"
    if skey not in st.session_state:
        st.session_state[skey] = []
    calls = [t for t in st.session_state[skey] if now - t < window]
    if len(calls) >= max_calls:
        return False
    calls.append(now)
    st.session_state[skey] = calls
    return True

def _sanitize_message(msg, max_len=500):
    if not msg:
        return ""
    msg = str(msg).strip()[:max_len]
    msg = re.sub(r'<[^>]+>', '', msg)
    msg = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', msg)
    return msg

def _safe_username():
    if "chat_username" not in st.session_state:
        role = st.session_state.get("user_role", "guest")
        prefix = {"owner": "المالك", "specialist": "مختص",
                  "guest": "زائر"}.get(role, "زائر")
        st.session_state["chat_username"] = f"{prefix}_{random.randint(1000, 9999)}"
    return st.session_state["chat_username"]

# ═══════════════════════════════════════════════════════════════════════
# الخطوط العربية
# ═══════════════════════════════════════════════════════════════════════

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
# ═══════════════════════════════════════════════════════════════════════
# [تكملة PART 1] — المكتبة العلفية + شريط القياس + الفيديو + 3D + PDF
# ═══════════════════════════════════════════════════════════════════════

# ═══ المكتبة العلفية الكاملة (مع الإضافات الجديدة) ═══
def _feed(cp, dc, se, ndf, adf, ee, ash, ca, p, lys, met, price, desc, src):
    return {"CP":cp,"DC":dc,"SE":se,"NDF":ndf,"ADF":adf,"EE":ee,"ASH":ash,
            "Ca":ca,"P":p,"Lys":lys,"Met":met,"price":price,
            "desc":desc,"src":src}

BIG_FEEDS_LIBRARY = {
"🌾 الحبوب ومصادر الطاقة": {
"ذرة صفراء": _feed(8.5,.85,80,9.5,3.2,3.8,1.3,.02,.27,.24,.17,230,"الطاقة","NRC 2012"),
"ذرة بيضاء": _feed(8.8,.83,78,10.2,3.5,3.5,1.4,.02,.26,.25,.18,225,"بديل","NRC 2012"),
"ذرة شامية": _feed(8.3,.86,82,9,3,4,1.2,.02,.28,.23,.16,240,"طاقة","NRC 2012"),
"ذرة رفيعة (سورجم)": _feed(10,.78,70,12.5,5.5,3,1.8,.03,.3,.22,.17,195,"بديل","NRC 2012"),
"شعير مطحون": _feed(11.5,.8,71,18.5,7.5,2.2,2.5,.05,.35,.42,.2,210,"مجترات","NRC 2012"),
"شعير كامل": _feed(10.8,.75,68,22,9,2,2.8,.05,.33,.4,.18,200,"جرش","NRC 2012"),
"قمح محلي": _feed(12,.85,75,11.5,3.8,2,1.6,.04,.32,.35,.2,240,"طاقة","NRC 2012"),
"قمح مستورد": _feed(11.5,.87,78,11,3.5,1.9,1.5,.04,.33,.34,.19,245,"طاقة","NRC 2012"),
"جريش أرز": _feed(7.8,.82,82,5.5,2.5,8.5,4.2,.06,.3,.28,.18,240,"عالية","NRC 2012"),
"دخن محلي": _feed(11,.75,68,15.5,6.5,4,2.2,.05,.31,.28,.2,220,"بديل","NRC 2012"),
"شوفان علفي": _feed(11,.76,62,27.5,13.5,5,3,.08,.35,.4,.18,260,"خيول","NRC 2007"),
"كسرة خبز": _feed(10.5,.82,75,8,3.5,5.5,3.5,.1,.2,.28,.17,160,"اقتصادي","INRA 2018"),
"مكرونة مكسرة": _feed(11,.88,80,3.5,1.5,1.5,1,.03,.2,.28,.15,190,"طاقة","INRA 2018"),
"تمر مجفف (دقل)": _feed(5.5,.85,68,15,8.5,1,3.5,.1,.1,.1,.05,180,"اقتصادي","FAO 2010"),
"تفل بنجر السكر": _feed(8.5,.65,55,45,28,1,8.5,.7,.1,.3,.15,190,"مجترات","INRA 2018"),
"تفل زيتون": _feed(8,.55,35,50,35,12,7,.5,.15,.2,.1,130,"زيوت","INRA 2018"),
},
"🌱 الأكساب ومصادر البروتين": {
"كسب فول صويا 44%": _feed(44,.9,74,13.5,8,1.8,6,.35,.65,2.7,.6,440,"رئيسي","NRC 2012"),
"كسب فول صويا 48%": _feed(48,.91,76,12,7,1.5,6.2,.35,.65,3,.68,480,"مرتفع","NRC 2012"),
"أمباز الفول السوداني": _feed(46,.88,73,15.5,8.5,1.5,5.5,.2,.65,1.6,.45,460,"ممتاز","NRC 2012"),
"كسب عباد الشمس 36%": _feed(36,.76,42,38.5,25.5,2.5,6.5,.4,1,1.2,.7,310,"اقتصادي","NRC 2012"),
"كسب عباد الشمس 32%": _feed(32,.72,38,42,28,2,7,.42,.95,1.1,.65,290,"اقتصادي","NRC 2012"),
"كسب بذور القطن": _feed(41,.78,55,24.5,15.5,1.2,6.5,.2,1.1,1.8,.6,290,"جوسيبول","NRC 2012"),
"كسب بذور الكتان": _feed(32,.82,65,18.5,10.5,2.8,5.8,.35,.85,1.2,.55,340,"أوميغا3","NRC 2007"),
"كسب السمسم": _feed(42,.84,70,14.5,9.5,8.5,12.5,2,1.2,1.3,1,520,"غني Ca","NRC 2007"),
"كسب جلوتين 60%": _feed(60,.92,85,8.5,5.5,2.5,3.5,.15,.5,1.1,1.8,520,"Met","NRC 2012"),
"كسب نواة النخيل": _feed(16,.65,52,55.5,35.5,6.5,4.5,.3,.55,.55,.28,200,"رخيص","FAO 2010"),
"كسب الكانولا": _feed(36,.82,60,28,18,3.5,6.5,.65,1.1,1.9,.7,400,"متوازن","NRC 2012"),
"فول صويا كامل": _feed(38,.85,78,15,10,18,4.5,.25,.55,2.5,.55,420,"معالجة","NRC 2012"),
"بازلاء علفية": _feed(22,.82,70,15,8,1.5,3,.1,.4,1.5,.25,320,"متوازن","NRC 2012"),
"خميرة الخبز (مفعلة)": _feed(45,.88,60,8,4,2,7,.2,.8,3.2,.9,1800,"بروتين عالٍ","NEW v11.12"),
},
"🐔 أعلاف الدواجن الجاهزة": {
"علف دجاج جاهز (بادي)": _feed(23,.86,76,8,4,4.5,6.5,1,.5,1.4,.55,400,"جاهز بادي","ROSS 308"),
"علف دجاج جاهز (نامي)": _feed(21,.85,74,9,5,4.5,6,.9,.45,1.25,.5,390,"جاهز نامي","ROSS 308"),
"علف دجاج جاهز (ناهي)": _feed(19.5,.84,75,10,5.5,4.5,6,.87,.43,1.1,.48,380,"جاهز ناهي","ROSS 308"),
"علف بياض جاهز": _feed(18,.82,72,10,5.5,4,8.5,3.8,.45,1,.45,395,"بياض جاهز","NRC 1994"),
},
"🚜 المخلفات الزراعية": {
"نخالة قمح (ردة)": _feed(15,.72,45,35.5,12.5,3.5,5.5,.12,1.1,.6,.25,150,"اقتصادية","NRC 2001"),
"نخالة ذرة": _feed(9.5,.65,40,40,15,4,2,.1,.75,.3,.15,140,"اقتصادية","NRC 2001"),
"البرسيم الجاف": _feed(16.5,.6,35,42.5,32.5,2,10.5,1.5,.25,.85,.25,170,"بروتين","NRC 2001"),
"برسيم حجازي": _feed(18,.62,38,40,30,2.2,11,1.6,.26,.9,.28,175,"أفضل","NRC 2001"),
"مولاس قصب السكر": _feed(4,.95,50,1.5,.8,.5,8.5,.7,.05,.03,.02,120,"طاقة","NRC 2001"),
"تبن قمح": _feed(3.2,.35,18,72.5,45.5,1.5,8.5,.3,.08,.15,.05,80,"حشو","NRC 2001"),
"تبن فول": _feed(4.5,.4,22,68,42,1.2,7.5,.35,.1,.18,.08,90,"أفضل","NRC 2001"),
"قش أرز": _feed(3.5,.3,15,70,45,1.5,12,.2,.06,.12,.05,65,"حشو","NRC 2007"),
"سعف نخيل مطحون": _feed(4,.3,20,65,42,2,7,.35,.08,.15,.06,55,"ألياف","FAO 2010"),
"مخلفات النخيل": _feed(6.5,.7,60,25,15,5,3.5,.15,.15,.25,.1,100,"إبل","FAO 2010"),
},
"🧬 مصادر البروتين الحيواني": {
"مسحوق أسماك 60%": _feed(60,.85,65,2.5,1.5,8.5,22.5,5.5,3.2,4.5,1.8,850,"ممتاز","NRC 2012"),
"مسحوق أسماك 72%": _feed(72,.9,72,2,1,9.5,18.5,4.8,2.8,5.5,2.2,1100,"مرتفع","NRC 2012"),
"مسحوق اللحم والعظم": _feed(50,.75,50,3.5,2.5,10.5,32.5,9,4.5,2.5,.7,620,"Ca+P","NRC 2012"),
"مسحوق الدم": _feed(80,.65,55,1,.5,1.5,6,.3,.3,7,1,780,"هضم منخفض","NRC 2012"),
"مسحوق ريش": _feed(82,.7,60,1.5,1,3,4,.25,.35,2,.5,650,"معالجة","NRC 2012"),
"مركزات دواجن": _feed(40,.85,60,8.5,4.5,3.5,12.5,2.5,1.2,2.5,.9,650,"جاهزة","NRC 2012"),
"مركزات مواشي": _feed(36,.8,55,15.5,8.5,3,15.5,3,1.5,2,.7,600,"جاهزة","NRC 2001"),
"حشرات مجففة (BSF)": _feed(42,.8,68,8,5,35,8,.8,.9,2.6,.85,1800,"مستدام","FAO 2013"),
},
"🌰 الزيوت النباتية والحيوانية": {
"زيت ذرة": _feed(0,0,220,0,0,100,0,0,0,0,0,1500,"أوميغا6","NRC 2012"),
"زيت فول الصويا": _feed(0,0,215,0,0,100,0,0,0,0,0,1350,"متوازن","Ross 308"),
"زيت عباد الشمس": _feed(0,0,210,0,0,100,0,0,0,0,0,1300,"أوميغا6","NRC 2007"),
"زيت الكتان": _feed(0,0,205,0,0,100,0,0,0,0,0,1700,"أوميغا3","NRC 2007"),
"زيت جوز الهند": _feed(0,0,230,0,0,100,0,0,0,0,0,1900,"MCT","NRC 2012"),
"زيت النخيل": _feed(0,0,215,0,0,100,0,0,0,0,0,1100,"مقاوم","NRC 2012"),
"زيت الكانولا": _feed(0,0,200,0,0,100,0,0,0,0,0,1450,"متوازن","NRC 2012"),
"شحم حيواني (Tallow)": _feed(0,0,230,0,0,100,0,0,0,0,0,900,"طاقة","NRC 2012"),
"زيت السمك (Fish Oil)": _feed(0,0,235,0,0,100,0,0,0,0,0,3800,"EPA","NRC Fish"),
},
"🧪 الأحماض الأمينية": {
"ليسين نقي": _feed(94,1,0,0,0,0,.5,0,0,94,0,4200,"أساسي","NRC 2012"),
"ميثيونين نقي": _feed(58,1,0,0,0,0,.3,0,0,0,58,5800,"دواجن","NRC 2012"),
"ثريونين نقي": _feed(72,1,0,0,0,0,.2,0,0,0,0,4800,"ثالث","NRC 2012"),
"تريبتوفان نقي": _feed(85,1,0,0,0,0,.1,0,0,0,0,9500,"دواجن","NRC 2012"),
},
"🔬 الإنزيمات والبريمكسات": {
"بريمكس تسمين دواجن": _feed(0,0,0,0,0,0,100,18,8,0,0,4800,"فيتامينات","NRC 1994"),
"بريمكس بياض": _feed(0,0,0,0,0,0,100,22,7,0,0,5000,"بياض","NRC 1994"),
"بريمكس أبقار": _feed(0,0,0,0,0,0,100,20,10,0,0,5200,"أبقار","NRC 2001"),
"بريمكس مجترات": _feed(0,0,0,0,0,0,100,18,9,0,0,4500,"مجترات","NRC 2007"),
"بريمكس خيول": _feed(0,0,0,0,0,0,100,15,8,0,0,5500,"خيول","NRC 2007"),
"بريمكس إبل": _feed(0,0,0,0,0,0,100,20,10,0,0,5300,"إبل","FAO 2010"),
"بريمكس أسماك": _feed(0,0,0,0,0,0,100,15,7,0,0,5800,"أسماك","NRC Fish"),
"إنزيم فايتيز": _feed(0,0,0,0,0,0,5,0,0,0,0,4200,"تحرير P","NRC 2012"),
"خمائر حية": _feed(45,.75,30,8,4,1,8,.15,1.2,3,.7,8500,"مجترات","NRC 2001"),
},
"🪨 الأملاح والمعادن": {
"الحجر الجيري": _feed(0,0,0,0,0,0,99.5,38,0,0,0,40,"Ca","NRC 2012"),
"فوسفات ثنائي الكالسيوم": _feed(0,0,0,0,0,0,98.5,23,18,0,0,280,"Ca+P","NRC 2012"),
"فوسفات أحادي الكالسيوم": _feed(0,0,0,0,0,0,99,17,22,0,0,320,"P","NRC 2012"),
"ملح الطعام": _feed(0,0,0,0,0,0,99.9,0,0,0,0,30,"NaCl","NRC 2012"),
"بيكربونات الصوديوم": _feed(0,0,0,0,0,0,99,0,0,0,0,340,"مضاد","NRC 2001"),
"أكسيد المغنيسيوم": _feed(0,0,0,0,0,0,99.5,0,0,0,0,480,"Mg","NRC 2007"),
"يوريا علفية": _feed(287,.95,0,0,0,0,1,0,0,0,0,480,"NPN","NRC 2001"),
"مضاد سموم فطرية": _feed(0,0,0,0,0,0,85,0,0,0,0,950,"أفلاتوكسين","NRC 2012"),
},
"💊 الفيتامينات": {
"فيتامين A": _feed(0,0,0,0,0,0,100,0,0,0,0,4200,"نمو","NRC 2012"),
"فيتامين D3": _feed(0,0,0,0,0,0,100,0,0,0,0,5200,"Ca","NRC 2012"),
"فيتامين E": _feed(0,0,0,0,0,0,100,0,0,0,0,5800,"أكسدة","NRC 2012"),
"كولين كلوريد": _feed(0,0,0,0,0,0,100,0,0,0,0,3200,"B4","NRC 2012"),
},
}

def _get_ingredient_lookup():
    if not hasattr(_get_ingredient_lookup, "_cache"):
        lookup = {}
        for cat in BIG_FEEDS_LIBRARY.values():
            for name, data in cat.items():
                lookup[name] = data
        _get_ingredient_lookup._cache = lookup
    return _get_ingredient_lookup._cache

def get_oil_ingredients():
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت النباتية والحيوانية", {})

# ═══════════════════════════════════════════════════════════════════════
# صور حيوانات حقيقية لشريط القياس
# ═══════════════════════════════════════════════════════════════════════

ANIMAL_PHOTOS = {
    "أبقار": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Cow_female_black_white.jpg/1024px-Cow_female_black_white.jpg",
    "أغنام": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Sheep_in_lesser_himalayas.JPG/1024px-Sheep_in_lesser_himalayas.JPG",
    "ماعز": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Goat_chewing_a_can_%28cropped%29.jpg/1024px-Goat_chewing_a_can_%28cropped%29.jpg",
    "إبل": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Camel_in_Dubai.jpg/1024px-Camel_in_Dubai.jpg",
    "خيول": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Nokota_Horses_cropped.jpg/1024px-Nokota_Horses_cropped.jpg",
    "دواجن": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Hen_in_a_field.jpg/1024px-Hen_in_a_field.jpg",
    "أسماك": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Tilapia_nilotica.jpg/1024px-Tilapia_nilotica.jpg",
    "أرانب": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Oryctolagus_cuniculus_Tasmania_2.jpg/1024px-Oryctolagus_cuniculus_Tasmania_2.jpg",
    "سمان": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Coturnix_coturnix_%28aka%29.jpg/1024px-Coturnix_coturnix_%28aka%29.jpg",
}

WEIGHT_TAPE_CONFIG = {
    "أبقار": {"hg_min":100.0,"hg_max":260.0,"hg_default":180.0,
        "bl_min":100.0,"bl_max":220.0,"bl_default":150.0,
        "hg_label":"محيط الصدر (سم)","bl_label":"طول الجسم (سم)",
        "hg_tip":"خلف الأرجل الأمامية","bl_tip":"من الكتف إلى الحوض",
        "source":"Schaeffer (1978)","accuracy":"±5%",
        "calc":lambda hg,bl: (hg**2*bl)/10840.0},
    "أغنام": {"hg_min":40.0,"hg_max":120.0,"hg_default":75.0,
        "bl_min":40.0,"bl_max":100.0,"bl_default":65.0,
        "hg_label":"محيط الصدر (سم)","bl_label":"طول الجسم (سم)",
        "hg_tip":"خلف الأرجل","bl_tip":"من الكتف للحوض",
        "source":"Schaeffer (1978)","accuracy":"±7%",
        "calc":lambda hg,bl: (hg**2*bl)/10840.0},
    "ماعز": {"hg_min":35.0,"hg_max":110.0,"hg_default":70.0,
        "bl_min":35.0,"bl_max":95.0,"bl_default":62.0,
        "hg_label":"محيط الصدر (سم)","bl_label":"طول الجسم (سم)",
        "hg_tip":"خلف الأرجل","bl_tip":"من الكتف للحوض",
        "source":"Schaeffer (1978)","accuracy":"±7%",
        "calc":lambda hg,bl: (hg**2*bl)/10840.0},
    "إبل": {"hg_min":130.0,"hg_max":280.0,"hg_default":210.0,
        "bl_min":100.0,"bl_max":220.0,"bl_default":155.0,
        "hg_label":"محيط الصدر (سم)","bl_label":"طول الجسم (سم)",
        "hg_tip":"خلف السنام","bl_tip":"من الصدر للذيل",
        "source":"FAO Camel (2010)","accuracy":"±10%",
        "calc":lambda hg,bl: (hg**2*bl)/11880.0},
    "خيول": {"hg_min":120.0,"hg_max":240.0,"hg_default":175.0,
        "bl_min":100.0,"bl_max":210.0,"bl_default":155.0,
        "hg_label":"محيط الصدر (سم)","bl_label":"طول الجسم (سم)",
        "hg_tip":"خلف الكتف","bl_tip":"من الكتف للمؤخرة",
        "source":"Carroll & Huntington (1988)","accuracy":"±5%",
        "calc":lambda hg,bl: (hg**2*bl)/11877.0},
}

@st.cache_data(ttl=86400, show_spinner=False)
def _download_image(url):
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()
    except Exception:
        return None

def draw_tape_guide(animal_type):
    """صورة حيوان حقيقية مع أسهم القياس"""
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        from PIL import Image as _PILImage
        img_url = ANIMAL_PHOTOS.get(animal_type, ANIMAL_PHOTOS["أبقار"])
        img_bytes = _download_image(img_url)

        fig, ax = plt.subplots(figsize=(11, 7))

        if img_bytes:
            img = _PILImage.open(io.BytesIO(img_bytes))
            ax.imshow(img)
        else:
            ax.text(0.5, 0.5, f"📸 {animal_type}", ha='center', va='center',
                    fontsize=40, transform=ax.transAxes, color='#1b5e20')

        ax.axis('off')

        # سهم محيط الصدر (أحمر)
        ax.annotate('', xy=(0.35, 0.65), xytext=(0.35, 0.35),
            xycoords='axes fraction', textcoords='axes fraction',
            arrowprops=dict(arrowstyle='<->', color='#c62828', lw=4, mutation_scale=20))

        ax.text(0.36, 0.65, '① محيط الصدر', color='#c62828', fontweight='bold',
                fontsize=12, transform=ax.transAxes,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor='#c62828', alpha=0.9))

        # سهم طول الجسم (أزرق)
        ax.annotate('', xy=(0.15, 0.25), xytext=(0.85, 0.25),
            xycoords='axes fraction', textcoords='axes fraction',
            arrowprops=dict(arrowstyle='<->', color='#1565c0', lw=4, mutation_scale=20))

        ax.text(0.5, 0.27, '② طول الجسم', color='#1565c0', fontweight='bold',
                fontsize=12, ha='center', transform=ax.transAxes,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor='#1565c0', alpha=0.9))

        cfg = WEIGHT_TAPE_CONFIG.get(animal_type, {})
        ax.text(0.5, -0.05,
            f"🔴 ① {cfg.get('hg_tip', '')}     🔵 ② {cfg.get('bl_tip', '')}",
            transform=ax.transAxes, ha='center', fontsize=10,
            color='#1a1a1a', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff8e1',
                      edgecolor='#d4af37', linewidth=2))

        ax.set_title(f"📍 {animal_type} — {cfg.get('source', '')} | دقة {cfg.get('accuracy', '')}",
            fontsize=13, fontweight='bold', color='#1b5e20', pad=12)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
            facecolor='white', pad_inches=0.2)
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None

def weight_tape_widget(animal_type, key_prefix, default_weight=None):
    cfg = WEIGHT_TAPE_CONFIG.get(animal_type)
    if cfg is None:
        return float(st.number_input("⚖️ الوزن (كجم):", 0.05, 50.0,
            float(default_weight) if default_weight else 2.0, 0.1,
            key=f"{key_prefix}_manual"))
    tab_tape, tab_manual = st.tabs(["📏 شريط القياس", "⚖️ إدخال يدوي"])
    with tab_tape:
        img = draw_tape_guide(animal_type)
        if img:
            st.image(img.getvalue(), use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            hg = st.slider(f"① {cfg['hg_label']}", cfg['hg_min'],
                cfg['hg_max'], cfg['hg_default'], 0.5, key=f"{key_prefix}_hg")
        with c2:
            bl = st.slider(f"② {cfg['bl_label']}", cfg['bl_min'],
                cfg['bl_max'], cfg['bl_default'], 0.5, key=f"{key_prefix}_bl")
        weight = float(cfg["calc"](hg, bl))
        st.success(f"⚖️ الوزن التقديري = **{weight:.1f} كجم**")
        return weight
    with tab_manual:
        lo = cfg['calc'](cfg['hg_min'], cfg['bl_min'])
        hi = cfg['calc'](cfg['hg_max'], cfg['bl_max'])
        return float(st.number_input("⚖️ الوزن (كجم):",
            float(lo*0.5), float(hi*1.5),
            float(default_weight) if default_weight
                else float(cfg['calc'](cfg['hg_default'], cfg['bl_default'])),
            5.0, key=f"{key_prefix}_manual"))

# ═══════════════════════════════════════════════════════════════════════
# الفيديو الترحيبي التلقائي
# ═══════════════════════════════════════════════════════════════════════

def show_intro_video():
    """عرض الفيديو الترحيبي عند فتح التطبيق"""
    video_path = "intro.mp4"
    if os.path.exists(video_path):
        try:
            # عرض الفيديو في أعلى الصفحة الرئيسية
            st.markdown("""
            <div style="background: linear-gradient(135deg, #1b5e20, #2e7d32);
                        padding: 20px; border-radius: 15px; 
                        border: 3px solid #d4af37; margin-bottom: 20px;">
                <h3 style="color: #d4af37; text-align: center; margin: 0;">
                    🎥 مرحباً بكم في منصة تاور نولجي
                </h3>
                <p style="color: white; text-align: center; margin: 8px 0 0 0;">
                    شاهد الفيديو التعريفي لشرح جميع المميزات
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.video(video_path, autoplay=True)
        except Exception as e:
            pass

# ═══════════════════════════════════════════════════════════════════════
# حظائر الخيول 3D (إسطبلات كاملة)
# ═══════════════════════════════════════════════════════════════════════

HORSE_STALL_SCIENCE = {
    "box_standard": {"width": 3.5, "length": 3.5, "area": 12.25,
        "name_ar": "مربط صندوقي قياسي"},
    "box_large": {"width": 4.0, "length": 4.0, "area": 16.0,
        "name_ar": "مربط كبير"},
    "box_foaling": {"width": 4.0, "length": 5.0, "area": 20.0,
        "name_ar": "مربط ولادة"},
    "box_pony": {"width": 3.0, "length": 3.0, "area": 9.0,
        "name_ar": "مربط بوني"},
}

def calculate_horse_barn_scientific(num_horses, stall_type="box_standard", include_service=True):
    stall = HORSE_STALL_SCIENCE.get(stall_type, HORSE_STALL_SCIENCE["box_standard"])
    if num_horses <= 4:
        rows, stalls_per_row = 1, num_horses
    else:
        rows = 2
        stalls_per_row = (num_horses + 1) // 2
    
    aisle_w = 3.5
    building_width = (rows * stall["length"]) + aisle_w + 1.0
    building_length = stalls_per_row * stall["width"] + 2.0
    stall_area_total = num_horses * stall["area"]
    service_area = 73 if include_service else 0
    total_area = building_width * building_length + service_area
    
    return {
        "is_horse_barn": True,
        "num_horses": num_horses,
        "stall_type": stall_type,
        "stall_type_ar": stall["name_ar"],
        "stall_dimensions": f"{stall['width']}×{stall['length']} م",
        "stalls_per_row": stalls_per_row,
        "rows_count": rows,
        "building_width_m": round(building_width, 2),
        "building_length_m": round(building_length, 2),
        "building_height_m": 4.0,
        "total_area_m2": round(total_area, 2),
        "aisle_width_m": aisle_w,
        "service_area_m2": service_area,
        "vent_summer_m3h": int(building_width * building_length * 4 * 25),
        "vent_winter_m3h": int(building_width * building_length * 4 * 5),
        "tunnel_fans_count": max(1, int(np.ceil(num_horses / 3))),
        "side_fans_count": max(1, int(np.ceil(num_horses / 5))),
        "cost_total_usd": int(num_horses * 3500 + 20000),
        "reference": "NRC (2007) Horses + MWPS-1",
        "standard": {"name_ar": "خيول - مربط علمي"},
        "count": num_horses,
        "length_m": round(building_length, 2),
        "width_m": round(building_width, 2),
        "ridge_height_m": 5.5,
        "roof_type": "gable",
        "feeders_count": num_horses * 2,
        "drinkers_count": num_horses,
        "water_per_day_L": num_horses * 45,
        "lighting_lux": 200,
        "light_fixtures": max(1, int(total_area / 80)),
        "doors_count": num_horses,
        "door_dimensions": "1.3 × 2.4 م",
        "window_area_m2": total_area * 0.1,
        "bedding_cm": 20,
        "bedding_m3": num_horses * 12.25 * 0.2,
        "cost_structure_usd": int(building_width * building_length * 90),
        "cost_stalls_usd": int(num_horses * 3500),
    }

def create_barn_3d_figure(dims):
    """3D مع إسطبلات كاملة للخيول"""
    if not PLOTLY_AVAILABLE:
        return None
    try:
        std = dims["standard"]
        L = max(float(dims["length_m"]), 1.0)
        W = max(float(dims["width_m"]), 1.0)
        H = max(float(dims["height_m"]), 1.0)
        RH = max(float(dims["ridge_height_m"]), 1.0)
        max_dim = max(L, W, RH)
        ax_x, ax_y, ax_z = L/max_dim, W/max_dim, max(RH/max_dim, 0.15)
        fig = go.Figure()
        
        # الأرضية
        fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[0,0,W,W], z=[0,0,0,0],
            i=[0,0], j=[1,2], k=[2,3], color='#d7ccc8', opacity=0.7,
            name='الأرضية', hoverinfo='skip'))
        
        # الجدران
        for xp in [0, L]:
            fig.add_trace(go.Mesh3d(x=[xp]*4, y=[0,W,W,0], z=[0,0,H,H],
                i=[0,0], j=[1,2], k=[2,3], color='#a1887f', opacity=0.3,
                showlegend=False, hoverinfo='skip'))
        for yp in [0, W]:
            fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[yp]*4, z=[0,0,H,H],
                i=[0,0], j=[1,2], k=[2,3], color='#a1887f', opacity=0.3,
                showlegend=False, hoverinfo='skip'))
        
        # السقف
        if dims["roof_type"] == "gable":
            fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[0,0,W/2,W/2],
                z=[H,H,RH,RH], i=[0,0], j=[1,2], k=[2,3],
                color='#8d6e63', opacity=0.55, name='السقف', hoverinfo='skip'))
            fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[W/2,W/2,W,W],
                z=[RH,RH,H,H], i=[0,0], j=[1,2], k=[2,3],
                color='#8d6e63', opacity=0.55, showlegend=False, hoverinfo='skip'))
        
        # إسطبلات الخيول
        if dims.get("is_horse_barn"):
            rows = dims.get("rows_count", 2)
            per_row = dims.get("stalls_per_row", 5)
            stall_dim = dims.get("stall_dimensions", "3.5×3.5")
            try:
                stall_w = float(stall_dim.split("×")[0])
                stall_l = float(stall_dim.split("×")[1].replace(" م","").strip())
            except Exception:
                stall_w, stall_l = 3.5, 3.5
            
            wall_h = H * 0.75
            
            for row in range(rows):
                y_offset = 0.5 if row == 0 else W - stall_l - 0.5
                for col in range(per_row):
                    x_offset = 0.5 + col * stall_w
                    
                    # الجدار الأمامي (بفتحة باب)
                    y_front = y_offset if row == 0 else y_offset + stall_l
                    
                    # الجزء الأيسر
                    fig.add_trace(go.Mesh3d(
                        x=[x_offset, x_offset+0.4, x_offset+0.4, x_offset],
                        y=[y_front]*4, z=[0, 0, wall_h, wall_h],
                        i=[0,0], j=[1,2], k=[2,3], color='#8d6e63', 
                        opacity=0.5, showlegend=False, hoverinfo='skip'))
                    
                    # الجزء الأيمن
                    fig.add_trace(go.Mesh3d(
                        x=[x_offset+stall_w-0.4, x_offset+stall_w, x_offset+stall_w, x_offset+stall_w-0.4],
                        y=[y_front]*4, z=[0, 0, wall_h, wall_h],
                        i=[0,0], j=[1,2], k=[2,3], color='#8d6e63', 
                        opacity=0.5, showlegend=False, hoverinfo='skip'))
                    
                    # الجزء العلوي (فوق الباب)
                    fig.add_trace(go.Mesh3d(
                        x=[x_offset, x_offset+stall_w, x_offset+stall_w, x_offset],
                        y=[y_front]*4, z=[H*0.5, H*0.5, wall_h, wall_h],
                        i=[0,0], j=[1,2], k=[2,3], color='#8d6e63', 
                        opacity=0.5, showlegend=False, hoverinfo='skip'))

                    # الجدار الجانبي
                    x_right = x_offset + stall_w
                    fig.add_trace(go.Mesh3d(
                        x=[x_right]*4, y=[y_offset, y_offset+stall_l, y_offset+stall_l, y_offset],
                        z=[0, 0, wall_h, wall_h],
                        i=[0,0], j=[1,2], k=[2,3], color='#795548', 
                        opacity=0.4, showlegend=False, hoverinfo='skip'))
                    
                    # الجدار الخلفي
                    y_back = y_offset + stall_l if row == 0 else y_offset
                    fig.add_trace(go.Mesh3d(
                        x=[x_offset, x_offset+stall_w, x_offset+stall_w, x_offset],
                        y=[y_back]*4, z=[0, 0, wall_h, wall_h],
                        i=[0,0], j=[1,2], k=[2,3], color='#795548', 
                        opacity=0.4, showlegend=False, hoverinfo='skip'))

                    # الحصان
                    fig.add_trace(go.Scatter3d(
                        x=[x_offset+stall_w/2], y=[y_offset+stall_l/2], z=[0.4],
                        mode='markers',
                        marker=dict(size=12, color='#4e342e', symbol='diamond',
                                    line=dict(color='#d4af37', width=1.5)),
                        name='حصان' if row==0 and col==0 else None, 
                        showlegend=(row==0 and col==0)))
                    
                    # رقم الإسطبل
                    fig.add_trace(go.Scatter3d(
                        x=[x_offset+stall_w/2], y=[y_front], z=[wall_h + 0.2],
                        mode='text',
                        text=[f"{col+1 + row*per_row}"],
                        textfont=dict(size=10, color='#c62828'),
                        showlegend=False))
        
        fig.update_layout(
            title=dict(
                text=f"🐎 {std['name_ar']} — {dims['count']} حصان | "
                     f"{L:.1f}×{W:.1f}×{RH:.1f} م",
                font=dict(size=13, color='#1b5e20'), x=0.5),
            scene=dict(
                xaxis=dict(title='الطول', range=[-0.5, L+0.5]),
                yaxis=dict(title='العرض', range=[-0.5, W+0.5]),
                zaxis=dict(title='الارتفاع', range=[0, RH+0.5]),
                aspectmode='manual',
                aspectratio=dict(x=ax_x, y=ax_y, z=ax_z),
                camera=dict(eye=dict(x=1.5, y=-1.5, z=0.9))),
            height=650, paper_bgcolor='white')
        return fig
    except Exception:
        return None

# ═══════════════════════════════════════════════════════════════════════
# نظام تقييد PDF وأزرار التواصل
# ═══════════════════════════════════════════════════════════════════════

def render_pdf_access(pdf_bytes=None, filename="document.pdf", key_suffix=""):
    """
    عرض زر تحميل PDF مع القيود:
    - المالك: تحميل مباشر
    - مختص/زائر: طلب موافقة + أزرار تواصل
    """
    is_owner = st.session_state.get("user_role") == "owner"
    pdf_approved = st.session_state.get("pdf_approved", False)
    
    # === أزرار التواصل والاستشارة (تظهر دائماً) ===
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9); 
                padding: 20px; border-radius: 15px; 
                border-right: 5px solid #1b5e20; 
                text-align: center; margin: 15px 0;">
        <h4 style="color: #1b5e20; margin: 0 0 10px 0; font-size: 1.1rem;">
            💡 للحصول على تركيبات علفية أكثر جودة
        </h4>
        <p style="color: #333; margin: 0 0 15px 0; font-size: 0.95rem;">
            الرجاء الضغط على زر التواصل والاستشارة
        </p>
        <h3 style="color: #c62828; margin: 10px 0; font-size: 1.3rem;">
            👨‍🔬 د. عبدالقادر إسماعيل تاور
        </h3>
        <p style="color: #0d47a1; margin: 0; font-weight: bold; font-size: 1rem;">
            اختصاصي تغذية الحيوان
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        wa_num = WHATSAPP_NUMBER.replace('+', '').replace(' ', '')
        st.markdown(
            f'<a href="https://wa.me/{wa_num}" target="_blank" '
            f'style="display: block; padding: 15px; background: #25d366; '
            f'color: white !important; text-align: center; border-radius: 10px; '
            f'text-decoration: none; font-weight: bold; font-size: 1rem; '
            f'box-shadow: 0 3px 10px rgba(37, 211, 102, 0.3);">'
            f'📱 تواصل واتساب</a>',
            unsafe_allow_html=True)
    with c2:
        st.markdown(
            f'<a href="mailto:{OWNER_EMAIL}?subject=استشارة%20علفية" '
            f'style="display: block; padding: 15px; background: #1565c0; '
            f'color: white !important; text-align: center; border-radius: 10px; '
            f'text-decoration: none; font-weight: bold; font-size: 1rem; '
            f'box-shadow: 0 3px 10px rgba(21, 101, 192, 0.3);">'
            f'✉️ استشارة بالبريد</a>',
            unsafe_allow_html=True)
    
    # === زر تحميل PDF مع القيود ===
    st.markdown("---")
    if pdf_bytes is not None:
        if is_owner or pdf_approved:
            # المالك أو تمت الموافقة: تحميل مباشر
            st.download_button(
                "📄 تحميل PDF",
                pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True,
                type="primary",
                key=f"dl_{key_suffix}")
            if pdf_approved and not is_owner:
                st.caption("✅ تمت الموافقة من المالك (لجلسة واحدة)")
        else:
            # الزائر أو المختص: طلب موافقة
            st.warning("🔒 تحميل الـ PDF يتطلب موافقة المالك")
            
            if st.button("📩 طلب موافقة المالك للتحميل",
                    use_container_width=True, type="primary",
                    key=f"req_{key_suffix}"):
                st.info(
                    "✅ تم إرسال طلب الموافقة! يرجى التواصل مع "
                    "الدكتور عبدالقادر إسماعيل تاور لاعتماده. "
                    "يمكنك التواصل عبر الواتساب أو البريد أدناه.")
                st.session_state["pdf_requested"] = True
            
            if st.session_state.get("pdf_requested"):
                st.caption(
                    f"📞 للاستعجال: واتساب {WHATSAPP_NUMBER} | "
                    f"📧 {OWNER_EMAIL}")

# ═══════════════════════════════════════════════════════════════════════
# PDF Generator (مع تقييد)
# ═══════════════════════════════════════════════════════════════════════

class PDFGenerator:
    def __init__(self):
        self.font_name = font_mgr.font_name
    
    def _ar(self, t):
        if t is None:
            return ""
        try:
            return get_display(arabic_reshaper.reshape(str(t)), base_dir='R')
        except Exception:
            return str(t)
    
    def _draw_page(self, canvas_obj, doc):
        try:
            canvas_obj.saveState()
            w, h = doc.pagesize
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, h-90, w, 90, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.rect(0, h-95, w, 5, fill=1, stroke=0)
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 22)
            canvas_obj.drawCentredString(w/2, h-38,
                self._ar("تاور نولجي Tawor Nology"))
            canvas_obj.setFont(self.font_name, 12)
            canvas_obj.setFillColor(HexColor('#e8f5e9'))
            canvas_obj.drawCentredString(w/2, h-58,
                self._ar("للإنتاج الحيواني وتغذية الحيوان"))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.drawCentredString(w/2, h-76,
                self._ar(f"إشراف: {SUPERVISOR}"))
            
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, 42, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#ffeb3b'))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.drawCentredString(w/2, 68,
                self._ar(f"🤲 {DUA_SHORT} 🤲"))
            
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(w/2, 27,
                self._ar("تاور نولجي © 2026"))
            canvas_obj.setFont(self.font_name, 7)
            canvas_obj.drawCentredString(w/2, 12,
                self._ar(f"صفحة {canvas_obj.getPageNumber()} | "
                         f"{WHATSAPP_NUMBER}"))
            canvas_obj.restoreState()
        except Exception:
            pass
    
    def generate_simple_report(self, title, data_dict, notes=""):
        """تقرير PDF بسيط مع جدول بيانات"""
        if not REPORTLAB_AVAILABLE:
            return b""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
                leftMargin=40, topMargin=115, bottomMargin=145)
            story = []
            
            def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
                return Paragraph(self._ar(text), ParagraphStyle('s',
                    fontName=self.font_name, fontSize=size, alignment=align,
                    textColor=HexColor(color), spaceAfter=6, leading=size*1.6))
            
            story.append(P(title, size=20, align=TA_CENTER, color='#1b5e20'))
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", thickness=2.5,
                color=HexColor('#d4af37')))
            story.append(Spacer(1, 12))
            story.append(P(f"📅 {datetime.now():%Y-%m-%d %H:%M}",
                size=11, align=TA_CENTER, color='#555'))
            story.append(Spacer(1, 15))
            
            # جدول البيانات
            if data_dict:
                data = [[self._ar("البند"), self._ar("القيمة")]]
                for k, v in data_dict.items():
                    data.append([self._ar(str(k)), self._ar(str(v))])
                t = Table(data, colWidths=[200, 250])
                t.setStyle(TableStyle([
                    ('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),
                    ('TEXTCOLOR',(0,0),(-1,0),white),
                    ('ALIGN',(0,0),(-1,-1),'CENTER'),
                    ('FONTNAME',(0,0),(-1,-1),self.font_name),
                    ('FONTSIZE',(0,0),(-1,-1),10),
                    ('GRID',(0,0),(-1,-1),0.6,HexColor('#bdbdbd')),
                    ('ROWBACKGROUNDS',(0,1),(-1,-1),
                     [HexColor('#ffffff'), HexColor('#f5f5f5')]),
                    ('PADDING',(0,0),(-1,-1),8),
                ]))
                story.append(t)
                story.append(Spacer(1, 15))
            
            if notes:
                story.append(P(notes, size=11, color='#333'))
            
            story.append(Spacer(1, 30))
            story.append(P(f"📞 للاستشارة: {WHATSAPP_NUMBER}",
                size=11, align=TA_CENTER, color='#c62828'))
            story.append(P(f"✉️ {OWNER_EMAIL}",
                size=10, align=TA_CENTER, color='#1565c0'))
            story.append(Spacer(1, 15))
            story.append(P(SUPERVISOR, size=14, align=TA_CENTER,
                color='#c62828'))
            story.append(P(SUPERVISOR_TITLE, size=11, align=TA_CENTER,
                color='#1b5e20'))
            
            doc.build(story, onFirstPage=self._draw_page,
                onLaterPages=self._draw_page)
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            st.error(f"⚠️ خطأ PDF: {e}")
            return b""

pdf_gen = PDFGenerator()

# ═══════════════════════════════════════════════════════════════════════
# نهاية PART 2
# ═══════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════
# [تكملة PART 2] — المعادلات + الحسابات + المعايير + NLP
# ═══════════════════════════════════════════════════════════════════════

# ═══ المرجع العلمي ═══
STANDARD_REFERENCES = {
    "أبقار_حليب_عالي": {"primary": "NRC (2001) — Dairy Cattle, 7th Ed.",
        "table": "Table 15-1: Lactating cows (high production)",
        "secondary": ["INRA (2018) — Ruminants"]},
    "أبقار_حليب_متوسط": {"primary": "NRC (2001) — Dairy Cattle",
        "table": "Table 15-1: Lactating cows (medium)",
        "secondary": ["INRA (2018)"]},
    "أبقار_تسمين_مكثف": {"primary": "NRC (1996) — Beef Cattle",
        "table": "Table 10-1: Growing/finishing", "secondary": []},
    "أغنام_تسمين_مكثف": {"primary": "NRC (2007) — Small Ruminants",
        "table": "Table 11-1: Growing lambs", "secondary": ["INRA (2018)"]},
    "أغنام_مرضعات": {"primary": "NRC (2007) — Small Ruminants",
        "table": "Table 11-2: Lactating ewes", "secondary": []},
    "ماعز_حلابة_عالي": {"primary": "NRC (2007) — Small Ruminants",
        "table": "Table 12-1: Lactating goats", "secondary": []},
    "إبل_حليب": {"primary": "FAO (2010) — Camel Nutrition",
        "table": "Section 4", "secondary": []},
    "خيول_رياضة_مكثف": {"primary": "NRC (2007) — Horses, 6th Ed.",
        "table": "Table 10-1: Intense work", "secondary": []},
    "دواجن_لاحم": {"primary": "Ross 308 (2020) — Broiler Nutrition",
        "table": "Nutrient requirements by age",
        "secondary": ["NRC (1994)"]},
    "دواجن_بياض": {"primary": "NRC (1994) — Poultry",
        "table": "Table 4: Laying hens", "secondary": ["Lohmann (2020)"]},
    "أسماك_بادئ": {"primary": "NRC (2011) — Fish Nutrition",
        "table": "Table 6-1", "secondary": []},
    "أرانب_تسمين": {"primary": "NRC (2007)", "table": "Rabbit chapter",
        "secondary": []},
    "خيول_مربط": {"primary": "NRC (2007) Horses + MWPS-1",
        "table": "Stall dimensions & ventilation", "secondary": []},
}

REFERENCE_EQUATIONS = {
    "أبقار_حليب_عالي": {
        "DP": "DP = 9.0 + (الحليب × 0.175)",
        "CP": "CP = DP ÷ 0.72",
        "SE": "SE = 60 + (الحليب × 0.35)",
        "source": "NRC (2001) — Table 15-1"},
    "أبقار_حليب_متوسط": {
        "DP": "DP = 8.5 + (الحليب × 0.17)",
        "SE": "SE = 55 + (الحليب × 0.30)",
        "source": "NRC (2001)"},
    "أبقار_حليب_منخفض": {
        "DP": "DP = 8.0 + (الحليب × 0.16)",
        "source": "NRC (2001)"},
    "أبقار_تسمين_مكثف": {
        "DP": "DP = 11.5%", "CP": "CP = 14.5%", "SE": "SE = 72",
        "source": "NRC (1996)"},
    "أبقار_تسمين_عادي": {
        "DP": "DP = 9.5%", "CP": "CP = 12%", "SE": "SE = 65",
        "source": "NRC (1996)"},
    "أغنام_تسمين_مكثف": {
        "DP": "DP = 11.5%", "CP": "CP = 14.5%", "SE": "SE = 64",
        "source": "NRC (2007)"},
    "أغنام_مرضعات": {
        "DP": "DP = 10.5 + (المواليد - 1) × 1.5",
        "source": "NRC (2007)"},
    "ماعز_حلابة_عالي": {
        "DP": "DP = 9.5 + (الحليب × 0.35)",
        "source": "NRC (2007)"},
    "إبل_حليب": {
        "DP": "DP = 10.5 + (الحليب × 0.20)",
        "source": "FAO (2010)"},
    "خيول_رياضة_مكثف": {
        "DP": "DP = 10.5%", "SE": "SE = 70", "source": "NRC (2007)"},
    "دواجن_لاحم": {
        "DP": "DP = 20% → 16.5%", "CP": "CP = 23% → 19%",
        "SE": "SE = 76 → 75", "source": "Ross 308 (2020)"},
    "دواجن_بياض": {
        "DP": "DP = 15.5%", "CP": "CP = 18%",
        "source": "NRC (1994)"},
    "أسماك_بادئ": {
        "DP": "DP = 32%", "CP": "CP = 40%",
        "source": "NRC (2011)"},
    "أرانب_تسمين": {
        "DP": "DP = 15%", "CP": "CP = 17%",
        "source": "NRC (2007)"},
    "خيول_مربط": {
        "المربط": "3.5 م × 3.5 م = 12.25 م²",
        "الممر": "3.5 م",
        "الماء": "45 لتر/حصان/يوم",
        "source": "NRC (2007) + MWPS-1"},
    "معادلة_التركيب_NLP": {
        "الهدف": "max سعر × (ME/ME_هدف) × (CP/CP_هدف) - Σ(سعر)",
        "الطريقة": "SLSQP — 8 مستويات",
        "source": "Kraft (1988)"},
}

def get_references(animal_type, production_type):
    key = f"{animal_type}_{production_type}"
    if key in STANDARD_REFERENCES:
        return STANDARD_REFERENCES[key]
    return {"primary": "NRC (2012)", "table": "—", "secondary": []}

def get_reference_equations(animal_type, production_type):
    key = f"{animal_type}_{production_type}"
    if key in REFERENCE_EQUATIONS:
        return REFERENCE_EQUATIONS[key]
    for k, v in REFERENCE_EQUATIONS.items():
        if k.startswith(f"{animal_type}_"):
            return v
    return {}

# ═══ الاحتياجات الغذائية ═══
@dataclass
class AnimalRequirement:
    DP: float; CP: float; SE: float; NDF: float; ADF: float
    EE: float; ASH: float; Ca: float; P: float
    name_ar: str = ""; note: str = ""

def get_cattle_requirements(t, milk_yield=20.0, weight_kg=500.0):
    if t == "حليب_عالي":
        dp = min(9.0 + milk_yield * 0.175, 16.0)
        return AnimalRequirement(round(dp,2), round(dp/.72,2),
            round(60 + milk_yield*.35, 1), 30, 19, 5.5, 8,
            round(.55 + milk_yield*.003, 3), round(.33 + milk_yield*.0015, 3),
            "أبقار حلابة عالية", f"حليب {milk_yield} لتر")
    if t == "حليب_متوسط":
        dp = min(8.5 + milk_yield * 0.17, 14.0)
        return AnimalRequirement(round(dp,2), round(dp/.72,2),
            round(55 + milk_yield*.30, 1), 33, 21, 4.5, 8,
            round(.5 + milk_yield*.0025, 3), round(.3 + milk_yield*.0012, 3),
            "أبقار حلابة متوسطة", f"حليب {milk_yield}")
    if t == "حليب_منخفض":
        dp = min(8.0 + milk_yield * 0.16, 12.5)
        return AnimalRequirement(round(dp,2), round(dp/.75,2),
            round(50 + milk_yield*.25, 1), 38, 24, 4, 8.5,
            round(.45 + milk_yield*.002, 3), round(.28 + milk_yield*.001, 3),
            "أبقار حلابة منخفضة", f"حليب {milk_yield}")
    if t == "تسمين_مكثف":
        return AnimalRequirement(11.5, 14.5, 72, 32, 20, 4.5, 7.5, .65, .38,
            "تسمين مكثف", "ADG > 1.3 كجم/يوم")
    if t == "تسمين_عادي":
        return AnimalRequirement(9.5, 12, 65, 38, 24, 4, 7.5, .55, .32,
            "تسمين عادي", "ADG ~ 0.8 كجم/يوم")
    if t == "حمل_أخير":
        return AnimalRequirement(11.5, 14.5, 67, 35, 22, 4.2, 8, .7, .42,
            "حمل آخر", "شهر 7-9")
    return AnimalRequirement(7.5, 10, 53, 45, 28, 3, 8.5, .42, .26,
        "أبقار صيانة", "بدون إنتاج")

def get_sheep_requirements(t, is_male=True, weight_kg=50.0, litter_size=1):
    if is_male:
        if t == "تسمين_مكثف":
            return AnimalRequirement(11.5, 14.5, 64, 28, 17, 4, 8, .65, .36,
                "تسمين مكثف", "ADG > 250 جم")
        if t == "تسمين_عادي":
            return AnimalRequirement(9.5, 12, 59, 33, 21, 3.6, 8, .55, .32,
                "تسمين عادي", "ADG ~ 180 جم")
        return AnimalRequirement(8.5, 11, 55, 38, 24, 3.2, 8.5, .5, .3,
            "حملان تيد", "بداية")
    if t == "مرضعات":
        dp = 10.5 + (litter_size - 1) * 1.5
        return AnimalRequirement(round(dp,2), round(dp/.72,2),
            round(60 + (litter_size-1)*5, 1), 30, 19, 4.5, 8.5,
            round(.65 + (litter_size-1)*.1, 3),
            round(.38 + (litter_size-1)*.05, 3),
            f"نعاج مرضعات ({litter_size} مولود)", "")
    if t == "حامل_أخير":
        return AnimalRequirement(10.5, 13.5, 62, 32, 20, 3.8, 8, .6, .35,
            "نعاج حامل (4-5)", "")
    return AnimalRequirement(7.2, 9.5, 48, 45, 28, 3, 8.5, .42, .26,
        "نعاج صيانة", "")

def get_goat_requirements(t, is_male=True, milk_yield=2.0):
    if is_male:
        if t == "تسمين_جديان":
            return AnimalRequirement(11, 14, 62, 30, 19, 3.8, 8, .62, .34,
                "تسمين جديان", "")
        return AnimalRequirement(9, 11.5, 57, 36, 22, 3.5, 8, .55, .3,
            "تيوس تسمين", "")
    if t == "حلابة_عالي":
        dp = min(9.5 + milk_yield * 0.35, 13.5)
        return AnimalRequirement(round(dp,2), round(dp/.72,2),
            round(58 + milk_yield*.45, 1), 29, 18, 4.5, 8.5,
            round(.6 + milk_yield*.008, 3), round(.35 + milk_yield*.004, 3),
            f"عنزات حلابة ({milk_yield} لتر)", "")
    if t == "حلابة_متوسط":
        dp = min(8.5 + milk_yield * 0.30, 12.0)
        return AnimalRequirement(round(dp,2), round(dp/.72,2),
            round(55 + milk_yield*.40, 1), 32, 20, 4, 8.5,
            round(.55 + milk_yield*.006, 3), round(.32 + milk_yield*.003, 3),
            f"عنزات حلابة ({milk_yield})", "")
    if t == "حامل_أخير":
        return AnimalRequirement(10, 13, 60, 33, 21, 3.8, 8, .6, .35,
            "عنزات حامل", "")
    return AnimalRequirement(6.8, 9, 46, 46, 28, 3, 8.5, .42, .26,
        "عنزات صيانة", "")

def get_camel_requirements(t, weight_kg=400.0, milk_yield=5.0):
    if t == "نمو":
        return AnimalRequirement(10.5, 13.5, 60, 38, 24, 4, 8, .65, .38,
            "إبل نمو", f"{weight_kg} كجم")
    if t == "تسمين":
        return AnimalRequirement(9.5, 12, 65, 35, 22, 4.5, 7.5, .6, .35,
            "إبل تسمين", f"{weight_kg} كجم")
    if t == "حليب":
        dp = min(10.5 + milk_yield * 0.20, 14.0)
        return AnimalRequirement(round(dp,2), round(dp/.72,2),
            round(62 + milk_yield*.4, 1), 32, 20, 5, 8.5,
            round(.7 + milk_yield*.006, 3), round(.4 + milk_yield*.003, 3),
            f"إبل حلابة ({milk_yield} لتر)", "")
    if t == "سباق":
        return AnimalRequirement(14, 17, 72, 28, 17, 6, 9, .85, .5,
            "إبل سباق", "طاقة عالية")
    return AnimalRequirement(7, 9, 48, 48, 30, 3.5, 9, .42, .26,
        "إبل صيانة", f"{weight_kg} كجم")

def get_horse_requirements(t, weight_kg=450.0):
    if t == "رياضة_مكثف":
        return AnimalRequirement(10.5, 13.5, 70, 30, 18, 7, 7.5, .7, .4,
            "خيول رياضة مكثف", "")
    if t == "رياضة_عادي":
        return AnimalRequirement(9, 11.5, 63, 36, 22, 5, 7.5, .55, .32,
            "خيول رياضة عادي", "")
    if t == "نمو_أمهار":
        return AnimalRequirement(12, 15, 65, 30, 18, 5, 8, .75, .42,
            "أمهار نمو", "")
    if t == "مرضعات":
        return AnimalRequirement(12.5, 16, 68, 32, 20, 5.5, 8, .8, .45,
            "فرسات مرضعات", "")
    return AnimalRequirement(7.2, 9.5, 53, 46, 29, 3.5, 8, .45, .28,
        "خيول صيانة", "")

def get_poultry_requirements(strain, age_weeks=1):
    if strain == "لاحم":
        if age_weeks <= 1:
            return AnimalRequirement(20, 23, 76, 8, 4, 5, 6.5, 1, .5,
                "بادي لاحم", "أسبوع 1")
        if age_weeks <= 3:
            return AnimalRequirement(18.5, 21, 74, 9, 5, 5, 6, .9, .45,
                "نامي لاحم", "أسبوع 2-3")
        if age_weeks <= 5:
            return AnimalRequirement(17, 19.5, 75, 10, 5.5, 4.5, 6, .87, .43,
                "ناهي لاحم", "أسبوع 4-5")
        return AnimalRequirement(16.5, 19, 75, 10, 5.5, 4.5, 6, .85, .42,
            "ناهي لاحم+", "أسبوع 6+")
    if age_weeks <= 6:
        return AnimalRequirement(17, 20, 72, 10, 5.5, 4, 7, 1, .5,
            "بادي بياض", "")
    if age_weeks <= 18:
        return AnimalRequirement(14.5, 17, 70, 12, 6.5, 4, 9, 1.5, .45,
            "نامي بياض", "")
    return AnimalRequirement(15.5, 18, 72, 11, 6, 4.2, 11.5, 3.8, .45,
        "بياض إنتاجي", "")

def get_fish_requirements(species, stage):
    if "بادئ" in stage or "زريعة" in stage:
        return AnimalRequirement(32, 40, 72, 8, 4, 10, 11, 1.5, .9,
            f"{species} بادئ", "")
    if "نمو" in stage:
        return AnimalRequirement(25, 32, 70, 12, 6, 8, 9, 1, .7,
            f"{species} نمو", "")
    return AnimalRequirement(22, 28, 68, 13, 7, 8, 9.5, .9, .65,
        f"{species} تسمين", "")

def get_rabbit_requirements(t, weight_kg=4.0):
    if t == "تسمين":
        return AnimalRequirement(15, 17, 65, 25, 15, 3, 8, .7, .35,
            "أرانب تسمين", "ADG 40 جم")
    if t == "حليب":
        return AnimalRequirement(18, 20, 68, 25, 15, 4, 8.5, .85, .45,
            "أرانب حلابة", "أمهات")
    return AnimalRequirement(12, 14, 60, 30, 20, 2.5, 8.5, .6, .3,
        "أرانب صيانة", "")

def requirement_to_standard(req):
    return {"CP": req.CP, "DP": req.DP, "SE": req.SE, "NDF": req.NDF,
            "ADF": req.ADF, "EE": req.EE, "ASH": req.ASH,
            "Ca": req.Ca, "P": req.P}

# ═══ الحسابات ═══
def compute_formula_nutrients(formula):
    totals = {k: 0.0 for k in ["CP","DP","SE","NDF","ADF","EE","ASH",
                                "Ca","P","Lys","Met"]}
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
            return {"label":"🎯 مطابق","color":"#0d5302","bg":"#c8e6c9","score":100}
        return {"label":"⚠️ صفر","color":"#ef6c00","bg":"#fff3e0","score":40}
    a = abs(pct_diff)
    if a <= .5: return {"label":"🎯 مطابق","color":"#0d5302","bg":"#c8e6c9","score":100}
    if a <= 2: return {"label":"🌟 ممتاز","color":"#1b5e20","bg":"#dcedc8","score":95}
    if a <= 5: return {"label":"✅ جيد جداً","color":"#2e7d32","bg":"#e8f5e9","score":85}
    if a <= 10: return {"label":"🟢 جيد","color":"#558b2f","bg":"#f1f8e9","score":75}
    if a <= 15: return {"label":"⭐ مقبول","color":"#f9a825","bg":"#fff8e1","score":65}
    if a <= 25: return {"label":"⚠️ بتحفظ","color":"#ef6c00","bg":"#fff3e0","score":50}
    if a <= 40: return {"label":"🟠 ضعيف","color":"#e65100","bg":"#ffe0b2","score":35}
    return {"label":"❌ غير مطابق","color":"#c62828","bg":"#ffebee","score":20}

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

def _get_requirement_for_nlp(animal_type, production_type):
    try:
        if animal_type == "أبقار":
            req = get_cattle_requirements(production_type)
        elif animal_type == "أغنام":
            req = get_sheep_requirements(production_type, is_male=True)
        elif animal_type == "ماعز":
            req = get_goat_requirements(production_type, is_male=False)
        elif animal_type == "إبل":
            req = get_camel_requirements(production_type)
        elif animal_type == "خيول":
            req = get_horse_requirements(production_type)
        elif animal_type == "دواجن":
            req = get_poultry_requirements("بياض" if "بياض" in production_type else "لاحم")
        elif animal_type == "أسماك":
            req = get_fish_requirements("البلطي النيلي", production_type)
        elif animal_type == "أرانب":
            req = get_rabbit_requirements(production_type)
        else:
            req = get_cattle_requirements("حليب_متوسط")
        return {"ME": req.SE * 41, "CP": req.CP, "DP": req.DP}
    except Exception:
        return {"ME": 3000.0, "CP": 18.0, "DP": 14.0}

def get_oil_standard(k):
    standards = {
        "دواجن_بادي": {"max":8.0,"optimal":5.0},
        "أبقار_حليب_عالي": {"max":6.0,"optimal":4.0},
        "أغنام_تسمين_مكثف": {"max":5.0,"optimal":3.5},
    }
    return standards.get(k, {"max":5.0,"optimal":3.0})

def get_default_selections(animal_type, production_type):
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
    return d

def _normalize_ingredient_name(name):
    name = re.sub(r'\s+', ' ', str(name).strip())
    lookup = _get_ingredient_lookup()
    if name in lookup:
        return name
    for lib in lookup.keys():
        if lib.lower() in name.lower() or name.lower() in lib.lower():
            return lib
    kw = {"ذره":"ذرة صفراء","ذرة":"ذرة صفراء","صويا":"كسب فول صويا 44%",
          "شعير":"شعير مطحون","قمح":"قمح محلي","نخاله":"نخالة قمح (ردة)",
          "نخالة":"نخالة قمح (ردة)","ملح":"ملح الطعام",
          "حجر":"الحجر الجيري","فوسفات":"فوسفات ثنائي الكالسيوم"}
    for k, v in kw.items():
        if k in name.lower():
            return v
    return name

# ═══ محرك NLP ═══
def nlp_optimize_feed(ingredient_names, ingredient_data, prices,
                       animal_type="أبقار", production_type="حليب_عالي",
                       target_me=None, target_cp=None, price_product=2.5,
                       max_per_ing=0.6):
    n = len(ingredient_names)
    if n < 2:
        return {"success": False, "message": "يلزم مكونان"}
    if not SCIPY_AVAILABLE or minimize is None:
        return {"success": False, "message": "SCIPY غير متوفرة"}
    
    req = _get_requirement_for_nlp(animal_type, production_type)
    if target_me is None: target_me = req["ME"]
    if target_cp is None: target_cp = req["CP"]
    
    me_vals = np.array([ingredient_data[i].get("SE", 0) * 41
                        for i in ingredient_names])
    cp_vals = np.array([ingredient_data[i].get("CP", 0)
                        for i in ingredient_names])
    cost_vals = np.array([prices.get(i, 300.0) / 1000.0
                          for i in ingredient_names])
    
    MIN_USE = 0.005
    bounds = [(MIN_USE, max_per_ing) for _ in range(n)]
    
    energy_idx = [i for i, ing in enumerate(ingredient_names)
                  if ingredient_data[ing].get("SE", 0) > 40
                  and ingredient_data[ing].get("CP", 0) < 20]
    protein_idx = [i for i, ing in enumerate(ingredient_names)
                   if ingredient_data[ing].get("CP", 0) >= 20]
    
    def objective(x):
        me = np.dot(me_vals, x)
        cp = np.dot(cp_vals, x)
        quality = (me / target_me) * (cp / target_cp)
        return -(price_product * quality - np.dot(cost_vals, x))
    
    def make_initial_points():
        pts = []
        pts.append(np.ones(n) / n)
        for _ in range(3):
            p = np.random.RandomState(42).rand(n)
            p /= p.sum()
            pts.append(p)
        return pts
    
    best = None
    attempts = []
    levels = [("صارم 100%", 1.00), ("مرن 95%", 0.95),
              ("مرن 90%", 0.90), ("مرن 85%", 0.85),
              ("مرن 80%", 0.80), ("طوارئ 70%", 0.70)]
    
    for level_name, mult in levels:
        tme = target_me * mult
        tcp = target_cp * mult
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},
            {'type': 'ineq', 'fun': lambda x, t=tme: np.dot(me_vals, x) - t/100.0},
            {'type': 'ineq', 'fun': lambda x, t=tcp: np.dot(cp_vals, x) - t/100.0},
        ]
        for x0 in make_initial_points():
            x0 = np.clip(x0, [b[0] for b in bounds], [b[1] for b in bounds])
            try:
                res = minimize(objective, x0, method='SLSQP',
                    bounds=bounds, constraints=constraints,
                    options={'maxiter': 1000, 'ftol': 1e-8})
                if res.success:
                    x_norm = np.clip(res.x, 0, None)
                    x_norm = x_norm / x_norm.sum()
                    actual_me = float(np.dot(me_vals, x_norm)) * 100
                    actual_cp = float(np.dot(cp_vals, x_norm)) * 100
                    if actual_me >= tme*0.98 and actual_cp >= tcp*0.98:
                        best = (res, x_norm, level_name, mult,
                                actual_me, actual_cp)
                        attempts.append(f"✅ {level_name}: نجح")
                        break
            except Exception:
                continue
        if best:
            break
    
    if not best:
        return {"success": False, "message": "لا يوجد حل",
                "attempts": attempts}
    
    res, x_opt, level_name, mult, actual_me, actual_cp = best
    x_pct = x_opt * 100.0
    formula = {name: round(float(x_pct[i]), 2) for i, name in
               enumerate(ingredient_names) if x_pct[i] > 0.05}
    final_cost = float(np.dot(cost_vals, x_opt))
    me_ratio = actual_me / target_me
    cp_ratio = actual_cp / target_cp
    max_profit = float(price_product * (me_ratio * cp_ratio) - final_cost)
    
    warning = None
    if mult < 1.0:
        warning = f"⚠️ خُففت القيود إلى {mult*100:.0f}%"
    
    e_share = sum(formula.get(ing, 0)
                  for i, ing in enumerate(ingredient_names)
                  if i in energy_idx)
    p_share = sum(formula.get(ing, 0)
                  for i, ing in enumerate(ingredient_names)
                  if i in protein_idx)
    
    return {
        "success": True, "formula": formula,
        "final_cost": final_cost, "final_me": actual_me,
        "final_cp": actual_cp, "target_me": float(target_me),
        "target_cp": float(target_cp), "max_profit": max_profit,
        "strategy": level_name, "warning": warning,
        "energy_share_pct": round(e_share, 1),
        "protein_share_pct": round(p_share, 1),
    }

# ═══ محرك LP (Linear Programming) ═══
def auto_formulate_smart(available_ingredients, prices, custom_standard,
                          standard_key="", basis="DP", min_quality=70.0,
                          animal_type="", production_type=""):
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "SCIPY غير متوفرة"}
    
    lookup = _get_ingredient_lookup()
    valid = [i for i in available_ingredients if i in lookup]
    if len(valid) < 2:
        return {"success": False, "message": "اختر مكونين على الأقل"}
    
    is_ruminant = animal_type in ("أبقار", "أغنام", "ماعز", "إبل")
    is_poultry = animal_type in ("دواجن", "سمان")
    n = len(valid)
    c = [prices.get(i, 300.0) for i in valid]
    
    rows = {}
    for nut in ["CP","SE","NDF","ADF","EE","ASH","Ca","P"]:
        rows[nut] = [lookup[i].get(nut, 0) for i in valid]
    rows["DP"] = [lookup[i].get("CP",0) * lookup[i].get("DC",0) for i in valid]
    
    target_key = "DP" if basis == "DP" else "CP"
    target_protein = custom_standard.get(target_key, 15.0)
    target_ca = custom_standard.get("Ca", 0)
    target_p = custom_standard.get("P", 0)
    target_se = custom_standard.get("SE", 0)
    target_ndf = custom_standard.get("NDF", 0)
    
    MIN_USE = 0.5
    bounds = [(MIN_USE, 60.0) for _ in range(n)]
    
    energy_idx = [i for i, ing in enumerate(valid)
                  if lookup[ing].get("SE", 0) > 40
                  and lookup[ing].get("CP", 0) < 20]
    protein_idx = [i for i, ing in enumerate(valid)
                   if lookup[ing].get("CP", 0) >= 20]
    
    A_eq_base = [[1.0] * n, rows[target_key]]
    b_eq_base = [100.0, target_protein * 100.0]
    A_ub_base, b_ub_base = [], []
    
    target_me = (target_se * 41) if target_se > 0 else 2500
    if target_me > 0:
        A_ub_base.append([-x * 41 for x in rows["SE"]])
        b_ub_base.append(-target_me * 0.90)
    if energy_idx and protein_idx:
        balance_row = [0.0] * n
        for i in energy_idx: balance_row[i] = 1.0
        for i in protein_idx: balance_row[i] = -1.0
        A_ub_base.append([-x for x in balance_row])
        b_ub_base.append(-10.0)
    if energy_idx:
        e_row = [1.0 if i in energy_idx else 0.0 for i in range(n)]
        A_ub_base.append([-x for x in e_row])
        b_ub_base.append(-40.0)
    if protein_idx:
        p_row = [1.0 if i in protein_idx else 0.0 for i in range(n)]
        A_ub_base.append(p_row)
        b_ub_base.append(40.0)
    
    strategies = [("دقيق 100%", 1.00), ("مرن 95%", 0.95),
                  ("مرن 90%", 0.90), ("مرن 85%", 0.85),
                  ("مرن 80%", 0.80), ("طوارئ 75%", 0.75)]
    
    best, best_q = None, 0.0
    attempts = []
    
    for label, mult in strategies:
        try:
            A_eq = list(A_eq_base)
            b_eq = [100.0, target_protein * 100.0 * mult]
            A_ub = list(A_ub_base)
            b_ub = list(b_ub_base)
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                bounds=bounds, method='highs',
                options={'presolve': True, 'time_limit': 10})
            if res.success:
                formula = {valid[i]: res.x[i] for i in range(n)
                           if res.x[i] > 0.01}
                q, actual = evaluate_quality_weighted(
                    formula, custom_standard, animal_type, basis)
                if q > best_q:
                    best_q = q
                    best = {"success": True, "formula": formula,
                        "cost": res.fun / 100.0,
                        "actual_nutrients": actual,
                        "quality_score": q, "strategy": label,
                        "meets_standard": q >= min_quality,
                        "targets": custom_standard, "basis": basis}
                attempts.append(f"✅ {label}: {q:.1f}%")
                if q >= 92:
                    break
            else:
                attempts.append(f"❌ {label}")
        except Exception as e:
            attempts.append(f"⚠️ {label}: {e}")
    
    if best:
        if not best["meets_standard"]:
            best["warning"] = f"⚠️ جودة {best_q:.1f}% < {min_quality}%"
        return best
    
    # fallback
    fallback = {valid[i]: 100.0/n for i in range(n)}
    q, actual = evaluate_quality_weighted(
        fallback, custom_standard, animal_type, basis)
    return {"success": True, "formula": fallback,
        "cost": sum(fallback[ing] / 100 * prices.get(ing, 300)
                    for ing in fallback),
        "actual_nutrients": actual, "quality_score": q,
        "strategy": "🆘 طوارئ", "meets_standard": q >= min_quality,
        "targets": custom_standard, "basis": basis,
        "warning": f"⚠️ حل طوارئ — جودة {q:.1f}%",
        "attempts_log": attempts}

# ═══ محلل النص ═══
def _parse_ingredients_from_text(full_text):
    if not full_text:
        return {}
    lookup = _get_ingredient_lookup()
    all_names = sorted(lookup.keys(), key=len, reverse=True)
    ingredients = {}
    for line in full_text.split('\n'):
        line = line.strip()
        if len(line) < 3:
            continue
        for ing_name in all_names:
            if ing_name in line:
                idx = line.find(ing_name) + len(ing_name)
                remainder = line[idx:].strip()
                num_match = re.search(r'[:\-=:\.\s]*(\d{1,3}\.?\d{0,2})',
                                       remainder)
                if num_match:
                    try:
                        val = float(num_match.group(1))
                        if 0.01 <= val <= 100:
                            ingredients[ing_name] = round(val, 2)
                            break
                    except ValueError:
                        continue
    return ingredients

def match_ingredient_name(text):
    if not text:
        return None
    tl = text.strip().lower()
    lookup = _get_ingredient_lookup()
    for name in lookup.keys():
        if name.lower() in tl or tl in name.lower():
            return name
    return None

# ═══ تحليل التركيبة الجاهزة ═══
def analyze_existing_formula(formula, animal_type, production_type):
    if not formula or sum(formula.values()) <= 0:
        return {"success": False, "message": "التركيبة فارغة"}
    total = sum(formula.values())
    normalized = {k: round(v / total * 100, 2) for k, v in formula.items()}
    
    try:
        if animal_type == "أبقار":
            req = get_cattle_requirements(production_type)
        elif animal_type == "أغنام":
            req = get_sheep_requirements(production_type, is_male=True)
        elif animal_type == "ماعز":
            req = get_goat_requirements(production_type, is_male=False)
        elif animal_type == "إبل":
            req = get_camel_requirements(production_type)
        elif animal_type == "خيول":
            req = get_horse_requirements(production_type)
        elif animal_type == "دواجن":
            req = get_poultry_requirements("بياض" if "بياض" in production_type else "لاحم")
        elif animal_type == "أسماك":
            req = get_fish_requirements("البلطي النيلي", production_type)
        elif animal_type == "أرانب":
            req = get_rabbit_requirements(production_type)
        else:
            return {"success": False, "message": "حيوان غير مدعوم"}
    except Exception as e:
        return {"success": False, "message": f"خطأ: {e}"}
    
    standard = requirement_to_standard(req)
    actual = compute_formula_nutrients(normalized)
    labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم",
              "SE": "طاقة SE", "NDF": "NDF", "ADF": "ADF",
              "EE": "دهن", "ASH": "رماد", "Ca": "Ca", "P": "P"}
    
    comparison = []
    for k, sv in standard.items():
        if sv == 0:
            continue
        cv = actual.get(k, 0)
        diff = cv - sv
        pct = (diff / sv * 100) if sv else 0
        ev = evaluate_difference(pct, standard_value=sv)
        comparison.append({
            "key": k, "العنصر": labels.get(k, k),
            "المعيار": sv, "المحسوب": cv, "الفرق": diff,
            "الفرق %": pct, "التقييم": ev["label"],
            "score": ev["score"]})
    
    quality, _ = evaluate_quality_weighted(
        normalized, standard, animal_type)
    ca = actual.get("Ca", 0)
    p = actual.get("P", 0)
    ca_p = ca / p if p > 0 else 0
    
    lookup = _get_ingredient_lookup()
    energy_ings = [ing for ing in normalized
                   if lookup.get(ing, {}).get("SE", 0) > 40
                   and lookup.get(ing, {}).get("CP", 0) < 20]
    protein_ings = [ing for ing in normalized
                    if lookup.get(ing, {}).get("CP", 0) >= 20]
    energy_share = sum(normalized[ing] for ing in energy_ings)
    protein_share = sum(normalized[ing] for ing in protein_ings)
    
    cost = sum(normalized.get(ing, 0) / 100 *
               lookup.get(ing, {}).get("price", 300)
               for ing in normalized)
    
    return {
        "success": True, "formula": normalized,
        "standard": standard, "actual": actual,
        "comparison": comparison,
        "quality_score": quality, "ca_p_ratio": ca_p,
        "energy_share_pct": round(energy_share, 1),
        "protein_share_pct": round(protein_share, 1),
        "cost_per_ton": round(cost, 2),
        "requirement_name": req.name_ar,
        "animal_type": animal_type, "production_type": production_type,
        "references": get_references(animal_type, production_type),
    }

# ═══════════════════════════════════════════════════════════════════════
# نهاية PART 3
# ═══════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════
# [تكملة PART 3] — CSS + الواجهة الرئيسية + كل التبويبات + التذييل
# ═══════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════
# تهيئة الجلسة
# ═══════════════════════════════════════════════════════════════════════
DEFAULTS = {
    "approved": False, "user_role": None,
    "active_formula": {}, "pdf_approved": False,
    "pdf_requested": False, "formulation_history": [],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');
* { font-family: 'Cairo', 'Amiri', sans-serif; color: #1a1a1a !important; }
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
}
.main-box { background: rgba(255,255,255,0.95); padding: 32px;
    border-radius: 22px; box-shadow: 0 15px 45px rgba(0,0,0,0.15);
    margin-bottom: 70px; border: 1px solid rgba(212,175,55,0.2); }
.dua-main-box { background: linear-gradient(135deg, #0d3011, #1b5e20, #2e7d32);
    padding: 34px 28px; border-radius: 22px; border: 4px solid #d4af37;
    direction: rtl; text-align: center; margin: 25px 0; }
.dua-main-box * { color: white !important; }
.dua-main-box h3 { color: #d4af37 !important; font-size: 1.9rem; font-weight: 900; }
.dua-main-box .names { display: inline-block; background: rgba(212,175,55,0.25);
    font-size: 1.65rem; font-weight: 900; color: #ffeb3b !important;
    margin: 20px 0; padding: 16px 30px; border: 2px solid #d4af37;
    border-radius: 16px; font-family: 'Amiri', serif !important; }
.dua-main-box p.quran { font-family: 'Amiri', serif !important;
    font-size: 1.2rem; color: #d4af37 !important; margin-top: 22px;
    padding: 18px 25px; background: rgba(0,0,0,0.25); border-radius: 12px; }
.visitor-dua-banner { background: linear-gradient(135deg, #fff8e1, #ffe082);
    padding: 20px 28px; border-radius: 16px; border: 3px solid #d4af37;
    margin: 22px 0; direction: rtl; text-align: center; }
.visitor-dua-banner * { color: #4e342e !important; }
.dua-fixed-banner { position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32);
    color: white !important; padding: 12px 20px; z-index: 9998;
    text-align: center; border-top: 3px solid #d4af37;
    font-family: 'Amiri', serif !important; font-size: 1.05rem; font-weight: bold; }
.dua-fixed-banner * { color: #ffeb3b !important; }
.section-title { color: #1b5e20 !important; border-right: 6px solid #2e7d32;
    padding: 12px 18px; text-align: right; font-size: 1.5rem; font-weight: 900;
    margin-top: 30px; margin-bottom: 20px;
    background: linear-gradient(to left, rgba(46,125,50,0.15), transparent);
    border-radius: 10px; }
.formula-item { background: linear-gradient(135deg, #ffffff, #e8f5e9);
    padding: 15px 20px; border-radius: 10px; margin-bottom: 10px;
    font-weight: 700; color: #1b5e20 !important;
    border-right: 5px solid #2e7d32; text-align: right; }
.physio-card { background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 18px 24px; border-radius: 14px;
    border-right: 6px solid #1565c0; margin-bottom: 20px;
    direction: rtl; text-align: right; }
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
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important; padding: 9px 22px; font-size: 0.85rem;
    border-radius: 25px; z-index: 9997; direction: rtl;
    border: 2px solid #d4af37; font-weight: 700; }
.mini-signature * { color: white !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #2e7d32, #1b5e20) !important; }
.stTabs [aria-selected="true"] * { color: white !important; }
[data-testid="stMetric"] { background: linear-gradient(135deg, #ffffff, #f1f8e9);
    padding: 14px 18px; border-radius: 16px; border-right: 4px solid #2e7d32; }
[data-testid="stMetricValue"] { color: #1b5e20 !important; font-weight: 900 !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# بوابة الدخول
# ═══════════════════════════════════════════════════════════════════════
if not st.session_state.get("approved", False):
    st.markdown('<div class="main-box" style="max-width:980px; margin:30px auto; direction:rtl;">',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <div class="names">🕊️ {DUA_SHORT} 🕊️</div>
        <p class="quran">{DUA_QURAN}</p>
        <p class="quran" style="margin-top:10px;">{DUA_VERSE}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        if os.path.exists("owner.jpg"):
            with open("owner.jpg", "rb") as f:
                owner_b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<img src="data:image/jpeg;base64,{owner_b64}" class="profile-img-style">',
                        unsafe_allow_html=True)
    with col_title:
        st.markdown(f"<h2 style='color:#2E7D32; text-align:right;'>🌾 {APP_NAME}</h2>",
                    unsafe_allow_html=True)
        st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.1rem;'>{APP_TAGLINE}</p>",
                    unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#c62828; text-align:right;'>{SUPERVISOR} — {SUPERVISOR_TITLE}</h4>",
                    unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align:center; color:#1b5e20; margin-top:20px;'>🔐 اختر بوابتك</h3>",
                unsafe_allow_html=True)
    
    col_owner, col_spec, col_guest = st.columns(3)
    with col_owner:
        st.markdown("""<div style="background:linear-gradient(135deg,#e8f5e9,#c8e6c9);
            padding:16px; border-radius:12px; border:2px solid #2e7d32;
            text-align:center; min-height:140px;">
            <h4 style="color:#1b5e20; margin:0;">👑 المالك</h4>
            <p style="font-size:0.82rem;">إدارة كاملة</p></div>""",
            unsafe_allow_html=True)
        oc = st.text_input("كود المالك:", type="password", key="oc_v1112")
        if st.button("👑 دخول", type="primary", use_container_width=True, key="b_owner_v1112"):
            if check_owner_code(oc):
                st.session_state.update({"approved": True, "user_role": "owner"})
                st.rerun()
            else:
                st.error("❌ كود غير صحيح")
    
    with col_spec:
        st.markdown("""<div style="background:linear-gradient(135deg,#e3f2fd,#bbdefb);
            padding:16px; border-radius:12px; border:2px solid #1565c0;
            text-align:center; min-height:140px;">
            <h4 style="color:#0d47a1; margin:0;">🔬 مختص</h4>
            <p style="font-size:0.82rem;">دخول مباشر</p></div>""",
            unsafe_allow_html=True)
        if st.button("🔬 دخول كمختص", type="primary", use_container_width=True, key="b_spec_v1112"):
            st.session_state.update({"approved": True, "user_role": "specialist"})
            st.rerun()
    
    with col_guest:
        st.markdown("""<div style="background:linear-gradient(135deg,#fff8e1,#ffecb3);
            padding:16px; border-radius:12px; border:2px solid #d4af37;
            text-align:center; min-height:140px;">
            <h4 style="color:#e65100; margin:0;">👥 زائر</h4>
            <p style="font-size:0.82rem;">مجاني</p></div>""",
            unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True, key="b_guest_v1112"):
            st.session_state.update({"approved": True, "user_role": "guest"})
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════════════════
# صورة المالك (ثابتة في الزاوية)
# ═══════════════════════════════════════════════════════════════════════
if os.path.exists("owner.jpg"):
    with open("owner.jpg", "rb") as f:
        _owner_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <div style="position: fixed; bottom: 70px; right: 20px; z-index: 9999; text-align: center;">
        <img src="data:image/jpeg;base64,{_owner_b64}" 
             style="width: 80px; height: 80px; border-radius: 50%; 
                    border: 3px solid #d4af37; object-fit: cover; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
        <div style="background: rgba(255,255,255,0.95); border-radius: 8px; 
                    padding: 2px 8px; margin-top: 5px; font-size: 10px; 
                    font-weight: bold; color: #1b5e20; 
                    border: 1px solid #d4af37; white-space: nowrap;">
            👨‍🔬 {SUPERVISOR}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# الفيديو الترحيبي
# ═══════════════════════════════════════════════════════════════════════
show_intro_video()

# ═══════════════════════════════════════════════════════════════════════
# الواجهة الرئيسية
# ═══════════════════════════════════════════════════════════════════════
st.markdown('<div class="main-box">', unsafe_allow_html=True)

c1, c2 = st.columns([0.7, 0.3])
with c2:
    role_label = {"owner": "المالك 👑", "specialist": "مختص 🔬",
                  "guest": "زائر 👥"}.get(st.session_state.get("user_role"), "—")
    st.markdown(f"<div style='text-align:left; padding:10px; background:#f5f5f5;"
        f"border-radius:10px;'>الحساب: <b>{role_label}</b></div>",
        unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

c3, c4 = st.columns([0.3, 0.7])
with c3:
    if os.path.exists("owner.jpg"):
        with open("owner.jpg", "rb") as f:
            _pb = base64.b64encode(f.read()).decode()
        st.markdown(f'<img src="data:image/jpeg;base64,{_pb}" class="profile-img-style">',
                    unsafe_allow_html=True)
with c4:
    st.markdown(f"<h1 style='color:#0d3011; text-align:right; font-weight:900;'>"
        f"🌾 {APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.25rem;'>"
        f"{APP_TAGLINE}</p>", unsafe_allow_html=True)

st.markdown(f'<div class="visitor-dua-banner">🕌 <b>إلى زوارنا الكرام:</b><br>'
    f'هذه المنصة صدقةٌ جارية عن <b>والدي إسماعيل تاور</b> و<b>أختي ابتسام</b>.'
    f'<br>نسألكم بظهر الغيب أن تشاركوا الدعاء. 🤲</div>',
    unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# التبويبات حسب الدور
# ═══════════════════════════════════════════════════════════════════════
role = st.session_state.get("user_role", "guest")
is_owner = role == "owner"

if is_owner:
    tabs_titles = ["🔬 النمذجة", "🎯 NLP", "🧪 مختبر", "📏 القياس",
                   "🏗️ الحظائر 3D", "📚 المراجع", "📖 الدليل"]
elif role == "specialist":
    tabs_titles = ["🔬 النمذجة", "🎯 NLP", "🧪 مختبر", "📏 القياس",
                   "🏗️ الحظائر 3D", "📚 المراجع", "📖 الدليل"]
else:
    tabs_titles = ["🧮 حاسبة", "🧪 مختبر", "📏 القياس",
                   "🏗️ الحظائر 3D", "📚 المراجع", "📖 الدليل"]

tabs = st.tabs(tabs_titles)
tab_map = {t: tab for t, tab in zip(tabs_titles, tabs)}

# ═══════════════════════════════════════════════════════════════════════
# 1. حاسبة الزائر (بسيطة)
# ═══════════════════════════════════════════════════════════════════════
if role == "guest" and "🧮 حاسبة" in tab_map:
    with tab_map["🧮 حاسبة"]:
        st.markdown('<div class="section-title">🧮 حاسبة سريعة</div>',
            unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            g_animal = st.selectbox("🐾 الحيوان:",
                ["أبقار", "أغنام", "ماعز", "إبل", "دواجن", "أسماك"],
                key="g_animal_v1112")
            g_purpose = st.selectbox("🎯 الغرض:",
                ["حليب", "تسمين", "صيانة"], key="g_purpose_v1112")
        with c2:
            g_weight = st.number_input("⚖️ الوزن (كجم):", 1.0, 900.0,
                400.0, 5.0, key="g_w_v1112")
            g_count = st.number_input("🔢 العدد:", 1, 100000, 1, 1,
                key="g_cnt_v1112")
        
        if st.button("🧮 احسب التركيبة", type="primary",
                use_container_width=True, key="g_calc_v1112"):
            rough = {
                "ذرة صفراء": 40, "شعير مطحون": 20,
                "كسب فول صويا 44%": 18, "نخالة قمح (ردة)": 15,
                "الحجر الجيري": 1.5, "ملح الطعام": 0.5,
                "بريمكس مجترات": 0.25, "فوسفات ثنائي الكالسيوم": 0.75
            } if g_animal in ("أبقار", "أغنام", "ماعز", "إبل") else {
                "ذرة صفراء": 55, "كسب فول صويا 48%": 32,
                "زيت فول الصويا": 4, "الحجر الجيري": 1.2,
                "فوسفات ثنائي الكالسيوم": 1.8, "ملح الطعام": 0.3,
                "بريمكس تسمين دواجن": 0.3, "ليسين نقي": 0.2,
                "ميثيونين نقي": 0.15
            }
            
            lookup = _get_ingredient_lookup()
            actual = compute_formula_nutrients(rough)
            cost = sum(rough[ing] / 100 *
                lookup.get(ing, {}).get("price", 300) for ing in rough)
            
            st.success(f"✅ التكلفة التقريبية: ${cost:.2f}/طن")
            for ing, pct in rough.items():
                st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.1f}%</div>',
                    unsafe_allow_html=True)
            
            st.info(f"📊 العلف اليومي: {g_weight * 0.025 * g_count:.1f} كجم")
            
            # PDF مع التقييد
            pdf_bytes = pdf_gen.generate_simple_report(
                title=f"تركيبة {g_animal} - {g_purpose}",
                data_dict=rough,
                notes=f"عدد الرؤوس: {g_count} | الوزن: {g_weight} كجم")
            
            render_pdf_access(
                pdf_bytes=pdf_bytes,
                filename=f"formula_{g_animal}.pdf",
                key_suffix=f"guest_{g_animal}")
            
            st.warning("⚠️ تركيبة استرشادية — للحساب الدقيق استخدم بوابة المختص")

# ═══════════════════════════════════════════════════════════════════════
# 2. النمذجة (للمختص والمالك)
# ═══════════════════════════════════════════════════════════════════════
if role in ("specialist", "owner") and "🔬 النمذجة" in tab_map:
    with tab_map["🔬 النمذجة"]:
        st.markdown('<div class="section-title">🔬 تركيب علفي متقدم</div>',
            unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            n_animal = st.selectbox("🐾 الحيوان:",
                ["أبقار", "أغنام", "ماعز", "إبل", "خيول",
                 "دواجن", "أسماك", "أرانب"], key="n_animal_v1112")
        with c2:
            prod_map = {
                "أبقار": ["حليب_عالي", "حليب_متوسط", "تسمين_مكثف"],
                "أغنام": ["تسمين_مكثف", "مرضعات", "حامل_أخير"],
                "ماعز": ["حلابة_عالي", "تسمين_جديان"],
                "إبل": ["حليب", "تسمين", "نمو"],
                "خيول": ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار"],
                "دواجن": ["لاحم", "بياض"],
                "أسماك": ["بادئ زريعة", "نمو", "تسمين"],
                "أرانب": ["تسمين", "حليب"]
            }
            n_prod = st.selectbox("🎯 الحالة:",
                prod_map.get(n_animal, ["عام"]), key="n_prod_v1112")
        
        # اختيار المكونات
        st.markdown("### 🌾 اختر المكونات")
        selected = []
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            with st.expander(f"📁 {cat_name}"):
                cols = st.columns(3)
                for idx, ing in enumerate(items.keys()):
                    with cols[idx % 3]:
                        if st.checkbox(ing, key=f"sel_{ing}_v1112"):
                            selected.append(ing)
        
        st.info(f"✅ المختارة: {len(selected)} مادة")
        
        if st.button("🚀 تشغيل التركيب", type="primary",
                use_container_width=True, key="run_v1112"):
            if len(selected) < 2:
                st.error("⚠️ اختر مكونين على الأقل")
            else:
                # تحديد المتطلبات
                if n_animal == "أبقار":
                    req = get_cattle_requirements(n_prod)
                elif n_animal == "أغنام":
                    req = get_sheep_requirements(n_prod, is_male=True)
                elif n_animal == "ماعز":
                    req = get_goat_requirements(n_prod, is_male=False)
                elif n_animal == "إبل":
                    req = get_camel_requirements(n_prod)
                elif n_animal == "خيول":
                    req = get_horse_requirements(n_prod)
                elif n_animal == "دواجن":
                    req = get_poultry_requirements(n_prod)
                elif n_animal == "أسماك":
                    req = get_fish_requirements("البلطي النيلي", n_prod)
                else:
                    req = get_rabbit_requirements(n_prod)
                
                std = requirement_to_standard(req)
                prices = {i: _get_ingredient_lookup()[i].get("price", 300) for i in selected}
                
                with st.spinner("⏳ جاري التركيب..."):
                    result = auto_formulate_smart(
                        selected, prices, std,
                        animal_type=n_animal,
                        production_type=n_prod,
                        min_quality=70.0)
                
                if result["success"]:
                    quality = result["quality_score"]
                    st.success(f"✅ الجودة: {quality:.1f}%")
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("💰 التكلفة", f"${result['cost']:.2f}/طن")
                    m2.metric("🧬 الجودة", f"{quality:.1f}%")
                    m3.metric("⚡ الاستراتيجية", result["strategy"])
                    
                    st.markdown("### 🌾 التركيبة:")
                    for ing, pct in result["formula"].items():
                        st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.2f}%</div>',
                            unsafe_allow_html=True)
                    
                    # جدول المقارنة
                    st.markdown("### 📊 المقارنة")
                    actual = result["actual_nutrients"]
                    cmp_data = []
                    for k, lab in [("CP", "بروتين"), ("DP", "مهضوم"),
                                    ("SE", "طاقة"), ("Ca", "Ca"), ("P", "P")]:
                        if k in std and std[k] > 0:
                            target = std[k]
                            calc = actual.get(k, 0)
                            pct_diff = (calc - target) / target * 100
                            ev = evaluate_difference(pct_diff, standard_value=target)
                            cmp_data.append({
                                "العنصر": lab,
                                "المعيار": f"{target:.2f}",
                                "المحسوب": f"{calc:.2f}",
                                "الفرق %": f"{pct_diff:+.1f}%",
                                "التقييم": ev["label"]
                            })
                    st.dataframe(pd.DataFrame(cmp_data), use_container_width=True)
                    
                    # PDF مع التقييد
                    pdf_bytes = pdf_gen.generate_simple_report(
                        title=f"تركيبة علفية — {n_animal}",
                        data_dict=result["formula"],
                        notes=f"الجودة: {quality:.1f}% | التكلفة: ${result['cost']:.2f}")
                    
                    render_pdf_access(
                        pdf_bytes=pdf_bytes,
                        filename=f"formula_{n_animal}.pdf",
                        key_suffix=f"spec_{n_animal}")
                else:
                    st.error(f"❌ {result['message']}")

# ═══════════════════════════════════════════════════════════════════════
# 3. NLP
# ═══════════════════════════════════════════════════════════════════════
if role in ("specialist", "owner") and "🎯 NLP" in tab_map:
    with tab_map["🎯 NLP"]:
        st.markdown('<div class="section-title">🎯 التحسين غير الخطي (NLP)</div>',
            unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            nlp_animal = st.selectbox("🐾 الحيوان:",
                ["أبقار", "أغنام", "ماعز", "إبل", "خيول", "دواجن"],
                key="nlp_animal_v1112")
        with c2:
            nlp_prod = st.selectbox("🎯 الحالة:",
                ["حليب_عالي", "تسمين_مكثف", "حليب_متوسط"],
                key="nlp_prod_v1112")
        
        nlp_req = _get_requirement_for_nlp(nlp_animal, nlp_prod)
        m1, m2 = st.columns(2)
        m1.metric("🎯 ME", f"{nlp_req['ME']:.0f} kcal/kg")
        m2.metric("🎯 CP", f"{nlp_req['CP']:.2f}%")
        
        all_ings = list(_get_ingredient_lookup().keys())
        nlp_sel = st.multiselect("المكونات:", options=all_ings,
            default=all_ings[:5], max_selections=10, key="nlp_sel_v1112")
        
        if len(nlp_sel) >= 2:
            prices = {i: _get_ingredient_lookup()[i].get("price", 300) for i in nlp_sel}
            data = {i: _get_ingredient_lookup()[i] for i in nlp_sel}
            
            if st.button("🚀 تشغيل NLP", type="primary",
                    use_container_width=True, key="nlp_run_v1112"):
                with st.spinner("⏳ جاري التحسين..."):
                    result = nlp_optimize_feed(nlp_sel, data, prices,
                        animal_type=nlp_animal, production_type=nlp_prod)
                
                if result["success"]:
                    if result.get("warning"):
                        st.warning(result["warning"])
                    
                    st.success(f"✅ ربح: ${result['max_profit']:.4f} | {result['strategy']}")
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("💰 التكلفة", f"${result['final_cost']:.4f}")
                    m2.metric("⚡ ME", f"{result['final_me']:.0f}")
                    m3.metric("🧬 CP", f"{result['final_cp']:.2f}%")
                    m4.metric("📈 الربح", f"${result['max_profit']:.4f}")
                    
                    st.markdown("### 🌾 التركيبة:")
                    for ing, pct in result["formula"].items():
                        st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.2f}%</div>',
                            unsafe_allow_html=True)
                    
                    # مقارنة
                    st.markdown("### 📊 المقارنة مع القياسي")
                    nlp_actual = compute_formula_nutrients(result["formula"])
                    cmp_nlp = [
                        {"العنصر": "ME", "المعيار": f"{nlp_req['ME']:.0f}",
                         "المحسوب": f"{nlp_actual.get('SE',0)*41:.0f}"},
                        {"العنصر": "CP", "المعيار": f"{nlp_req['CP']:.2f}",
                         "المحسوب": f"{nlp_actual.get('CP',0):.2f}"},
                        {"العنصر": "DP", "المعيار": f"{nlp_req['DP']:.2f}",
                         "المحسوب": f"{nlp_actual.get('DP',0):.2f}"}
                    ]
                    st.dataframe(pd.DataFrame(cmp_nlp), use_container_width=True)
                    
                    # PDF مع التقييد
                    pdf_bytes = pdf_gen.generate_simple_report(
                        title=f"NLP — {nlp_animal}",
                        data_dict=result["formula"],
                        notes=f"الربح: ${result['max_profit']:.4f}")
                    
                    render_pdf_access(
                        pdf_bytes=pdf_bytes,
                        filename=f"NLP_{nlp_animal}.pdf",
                        key_suffix=f"nlp_{nlp_animal}")
                else:
                    st.error(f"❌ {result['message']}")

# ═══════════════════════════════════════════════════════════════════════
# 4. المختبر
# ═══════════════════════════════════════════════════════════════════════
if "🧪 مختبر" in tab_map:
    with tab_map["🧪 مختبر"]:
        st.markdown('<div class="section-title">🧪 مختبر التحليل</div>',
            unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            lab_animal = st.selectbox("🐾 الحيوان:",
                ["أبقار", "أغنام", "ماعز", "إبل", "خيول", "دواجن"],
                key="lab_animal_v1112")
        with c2:
            lab_prod = st.selectbox("🎯 الإنتاج:",
                ["حليب_عالي", "تسمين_مكثف", "حليب_متوسط"],
                key="lab_prod_v1112")
        
        st.markdown("### 📝 أدخل النسب يدوياً")
        
        formula_input = {}
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            with st.expander(f"📁 {cat_name}"):
                cols = st.columns(3)
                for idx, ing in enumerate(items.keys()):
                    with cols[idx % 3]:
                        pct = st.number_input(f"{ing} (%)", 0.0, 100.0, 0.0,
                            step=0.5, key=f"lab_{ing}_v1112")
                        if pct > 0:
                            formula_input[ing] = pct
        
        if formula_input:
            total = sum(formula_input.values())
            st.info(f"📊 المجموع: {total:.1f}% | المكونات: {len(formula_input)}")
        
        if st.button("🔬 تحليل", type="primary",
                use_container_width=True, key="lab_run_v1112"):
            if not formula_input:
                st.error("⚠️ أدخل النسب أولاً")
            else:
                with st.spinner("⏳ جاري التحليل..."):
                    result = analyze_existing_formula(
                        formula_input, lab_animal, lab_prod)
                
                if result["success"]:
                    quality = result["quality_score"]
                    if quality >= 70:
                        st.markdown(f"""<div class="quality-good-v113">
                            <h3 style="color:#1b5e20; margin:0;">✅ جودة: {quality:.1f}%</h3>
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div class="quality-bad-v113">
                            <h3 style="color:#c62828; margin:0;">⚠️ جودة: {quality:.1f}%</h3>
                        </div>""", unsafe_allow_html=True)
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("🧬 الجودة", f"{quality:.1f}%")
                    m2.metric("💰 التكلفة", f"${result['cost_per_ton']:.2f}/طن")
                    m3.metric("⚖️ Ca:P", f"{result['ca_p_ratio']:.2f}")
                    
                    # جدول المقارنة
                    st.markdown("### 📊 جدول المقارنة")
                    comp_df = pd.DataFrame([{
                        "العنصر": c["العنصر"],
                        "المعيار": f"{c['المعيار']:.2f}",
                        "المحسوب": f"{c['المحسوب']:.2f}",
                        "الفرق %": f"{c['الفرق %']:+.1f}%",
                        "التقييم": c["التقييم"]
                    } for c in result["comparison"]])
                    st.dataframe(comp_df, use_container_width=True)
                    
                    # PDF مع التقييد
                    pdf_bytes = pdf_gen.generate_simple_report(
                        title=f"تحليل — {lab_animal}",
                        data_dict=result["formula"],
                        notes=f"الجودة: {quality:.1f}%")
                    
                    render_pdf_access(
                        pdf_bytes=pdf_bytes,
                        filename=f"analysis_{lab_animal}.pdf",
                        key_suffix=f"lab_{lab_animal}")
                else:
                    st.error(f"❌ {result['message']}")

# ═══════════════════════════════════════════════════════════════════════
# 5. شريط القياس
# ═══════════════════════════════════════════════════════════════════════
if "📏 القياس" in tab_map:
    with tab_map["📏 القياس"]:
        st.markdown('<div class="section-title">📏 شريط القياس</div>',
            unsafe_allow_html=True)
        
        tape_animal = st.selectbox("🐾 الحيوان:",
            list(WEIGHT_TAPE_CONFIG.keys()), key="tape_animal_v1112")
        
        weight = weight_tape_widget(tape_animal, "tape_v1112")
        
        st.info(f"📖 {WEIGHT_TAPE_CONFIG[tape_animal].get('source', '')}")

# ═══════════════════════════════════════════════════════════════════════
# 6. الحظائر 3D
# ═══════════════════════════════════════════════════════════════════════
if "🏗️ الحظائر 3D" in tab_map:
    with tab_map["🏗️ الحظائر 3D"]:
        st.markdown('<div class="section-title">🏗️ مصمم الحظائر 3D</div>',
            unsafe_allow_html=True)
        
        st.markdown("### 🐎 مربط خيول علمي (NRC 2007 + MWPS-1)")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            horse_count = st.number_input("🔢 عدد الخيول:",
                1, 50, 10, 1, key="horse_count_v1112")
        with c2:
            stall_type = st.selectbox("📦 نوع المربط:",
                list(HORSE_STALL_SCIENCE.keys()),
                format_func=lambda k: HORSE_STALL_SCIENCE[k]["name_ar"],
                key="stall_type_v1112")
        with c3:
            include_service = st.checkbox("🚿 خدمات",
                value=True, key="service_v1112")
        
        if st.button("🏗️ حساب المربط", type="primary",
                use_container_width=True, key="horse_calc_v1112"):
            dims = calculate_horse_barn_scientific(
                horse_count, stall_type, include_service)
            
            st.markdown(f"### 📐 الأبعاد: {dims['total_area_m2']} م²")
            
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("📏 المساحة", f"{dims['total_area_m2']} م²")
            k2.metric("📐 الأبعاد",
                f"{dims['building_length_m']}×{dims['building_width_m']} م")
            k3.metric("🐎 مربطات",
                f"{dims['num_horses']} ({dims['rows_count']} صف × {dims['stalls_per_row']})")
            k4.metric("🚪 الممر", f"{dims['aisle_width_m']} م")
            
            k5, k6, k7, k8 = st.columns(4)
            k5.metric("💧 ماء/يوم", f"{dims['water_per_day_L']:,} لتر")
            k6.metric("🍽️ معالف", f"{dims['feeders_count']}")
            k7.metric("💧 سقايات", f"{dims['drinkers_count']}")
            k8.metric("💰 التكلفة", f"${dims['cost_total_usd']:,.0f}")
            
            st.markdown("### 🏗️ المجسم 3D (إسطبلات كاملة)")
            try:
                fig3d = create_barn_3d_figure(dims)
                if fig3d:
                    st.plotly_chart(fig3d, use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ 3D: {e}")
            
            # PDF مع التقييد
            pdf_bytes = pdf_gen.generate_simple_report(
                title=f"مربط خيول — {horse_count} حصان",
                data_dict={
                    "المساحة": f"{dims['total_area_m2']} م²",
                    "الأبعاد": f"{dims['building_length_m']}×{dims['building_width_m']} م",
                    "عدد المربطات": dims['num_horses'],
                    "الصفوف": f"{dims['rows_count']} صف × {dims['stalls_per_row']}",
                    "الممر": f"{dims['aisle_width_m']} م",
                    "التكلفة": f"${dims['cost_total_usd']:,.0f}",
                },
                notes=dims['reference'])
            
            render_pdf_access(
                pdf_bytes=pdf_bytes,
                filename=f"horse_barn_{horse_count}.pdf",
                key_suffix=f"barn_{horse_count}")

# ═══════════════════════════════════════════════════════════════════════
# 7. المراجع
# ═══════════════════════════════════════════════════════════════════════
if "📚 المراجع" in tab_map:
    with tab_map["📚 المراجع"]:
        st.markdown('<div class="section-title">📚 المراجع العلمية</div>',
            unsafe_allow_html=True)
        
        ref_animal = st.selectbox("اختر الحيوان:",
            list(set(k.split("_")[0] for k in STANDARD_REFERENCES.keys())),
            key="ref_animal_v1112")
        
        st.markdown(f"### 📖 مراجع {ref_animal}")
        for k, v in STANDARD_REFERENCES.items():
            if k.startswith(f"{ref_animal}_"):
                st.markdown(f"**{v['primary']}**")
                if v.get('table'):
                    st.caption(f"📑 {v['table']}")

# ═══════════════════════════════════════════════════════════════════════
# 8. الدليل
# ═══════════════════════════════════════════════════════════════════════
if "📖 الدليل" in tab_map:
    with tab_map["📖 الدليل"]:
        st.markdown('<div class="section-title">📖 دليل المستخدم</div>',
            unsafe_allow_html=True)
        st.markdown(f"""
### 🎯 {APP_NAME} v{APP_VERSION}

**إشراف:** {SUPERVISOR} — {SUPERVISOR_TITLE}

### ✨ الميزات
- 🔬 محرك LP/NLP ذكي
- 🧪 مختبر تحليل التركيبات
- 📏 شريط قياس (صور حقيقية)
- 🏗️ حظائر 3D (إسطبلات خيول كاملة)
- 📄 PDF مع تقييد (يتطلب موافقة المالك)
- 📱 واتساب + بريد للاستشارة

### 🔒 بوابات الدخول
- 👑 **مالك:** كود آمن
- 🔬 **مختص:** دخول مباشر
- 👥 **زائر:** مجاني

### 📞 التواصل
- 📧 {OWNER_EMAIL}
- 📱 {WHATSAPP_NUMBER}

### 🆕 v11.12:
- ✅ فيديو ترحيبي تلقائي
- ✅ تقييد PDF (بموافقة المالك)
- ✅ إضافة خميرة الخبز
- ✅ علف دجاج جاهز
- ✅ إسطبلات 3D كاملة

---
🤲 {DUA_FULL} 🤲
""")

# ═══════════════════════════════════════════════════════════════════════
# التذييل
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f'<div class="mini-signature">🌾 {APP_NAME} v{APP_VERSION} | {SUPERVISOR} © 2026</div>',
    unsafe_allow_html=True)
st.markdown(f'<div class="dua-fixed-banner">🤲 {DUA_SHORT} 🤲</div>',
    unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# نهاية الملف — Tawor Nology 11.12 ✅
# ═══════════════════════════════════════════════════════════════════════
