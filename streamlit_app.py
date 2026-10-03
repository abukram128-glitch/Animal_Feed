# ═════════════════════════════════════════════════════════════════════════════
# 🌾 تاور نولجي Tawor Nology 11.0 — نسخة موحدة شاملة
# للإنتاج الحيواني وتركيب الأعلاف بمعايير NRC / INRA / FAO / Ross 308
# إشراف: م. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
# ═════════════════════════════════════════════════════════════════════════════

import streamlit as st
import numpy as np
import pandas as pd
import json, os, base64, time, re, io, sqlite3, hashlib, hmac, secrets
import urllib.parse, warnings
from datetime import datetime
from functools import lru_cache
from typing import Optional, Dict, Tuple
from dataclasses import dataclass, asdict

warnings.filterwarnings('ignore')

# ─── مكتبات علمية ─────────────────────────────────────────────────────────
from scipy.optimize import linprog

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Wedge
    MPL_OK = True
except ImportError:
    MPL_OK = False

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    XLSX_OK = True
except ImportError:
    XLSX_OK = False

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
    PDF_OK = True
except ImportError:
    PDF_OK = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    AR_OK = True
except ImportError:
    AR_OK = False

try:
    import qrcode
    QR_OK = True
except ImportError:
    QR_OK = False

try:
    from PIL import Image as PILImage
    PIL_OK = True
except ImportError:
    PIL_OK = False

try:
    import pytesseract
    import cv2
    OCR_OK = True
except ImportError:
    OCR_OK = False


# ═════════════════════════════════════════════════════════════════════════════
# 1. الدعاء والثوابت
# ═════════════════════════════════════════════════════════════════════════════

DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي ابتسام"
DUA_FULL = "رحم الله والدي إسماعيل تاور وأختي ابتسام وأسكنهما فسيح جناته"
DUA_QURAN = "﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾"
DUA_VERSE = "﴿ وَقُل رَّبِّ ارْحَمْهُمَا كَمَا رَبَّيَانِي صَغِيرًا ﴾"

APP_NAME = "تاور نولجي Tawor Nology 11.0"
APP_TAGLINE = "للإنتاج الحيواني وتغذية الحيوان"
SUPERVISOR = "م. عبدالقادر إسماعيل تاور"
SUPERVISOR_TITLE = "اختصاصي تغذية الحيوان"
PLATFORM_URL = "https://tawor-nology.streamlit.app"
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "logo.png"]
LOGO_OPTIONS = ["logo.png", "logo.jpg"]

st.set_page_config(
    page_title=f"{APP_NAME} | {APP_TAGLINE}",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ═════════════════════════════════════════════════════════════════════════════
# 2. الوحدة الأمنية الموحدة (Security Core)
# ═════════════════════════════════════════════════════════════════════════════

def _secret(key: str, default: str = "") -> str:
    """قراءة آمنة من Streamlit Secrets مع fallback للمتغيرات البيئية"""
    try:
        return st.secrets.get(key, default)
    except Exception:
        return os.environ.get(key, default)


# هاشات الأكواد — تُقرأ من secrets.toml
# في حال عدم التهيئة، تُستخدم هاشات احتياطية مع تحذير
_FALLBACK = {
    "owner": hashlib.sha256(b"202687").hexdigest(),
    "specialist": hashlib.sha256(b"2020").hexdigest(),
    "breeder": hashlib.sha256(b"2026").hexdigest(),
}

OWNER_CODE_HASH = _secret("OWNER_CODE_HASH", _FALLBACK["owner"])
SPECIALIST_CODE_HASH = _secret("SPECIALIST_CODE_HASH", _FALLBACK["specialist"])
BREEDER_CODE_HASH = _secret("BREEDER_CODE_HASH", _FALLBACK["breeder"])

OWNER_EMAIL = _secret("OWNER_EMAIL", "abukram128@gmail.com")
WHATSAPP_NUMBER = _secret("WHATSAPP_NUMBER", "+249123533489")

ALLOWED_HOSTS = set(
    h.strip() for h in _secret("ALLOWED_HOSTS", "localhost").split(",") if h.strip()
)

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 300
SESSION_TIMEOUT = 8 * 3600


def hash_code(code: str) -> str:
    return hashlib.sha256(code.strip().encode("utf-8")).hexdigest()


def verify_code(entered: str, target_hash: str) -> bool:
    """مقارنة ثابتة الزمن — Timing Attack Safe"""
    if not entered or not target_hash:
        return False
    return hmac.compare_digest(hash_code(entered), target_hash)


def get_role_from_code(code: str) -> Optional[str]:
    if verify_code(code, OWNER_CODE_HASH):
        return "owner"
    if verify_code(code, SPECIALIST_CODE_HASH):
        return "specialist"
    if verify_code(code, BREEDER_CODE_HASH):
        return "breeder"
    return None


def check_rate_limit() -> Tuple[bool, int]:
    st.session_state.setdefault("login_attempts", 0)
    st.session_state.setdefault("lockout_until", 0.0)
    now = time.time()
    if now < st.session_state["lockout_until"]:
        return False, int(st.session_state["lockout_until"] - now)
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        st.session_state["lockout_until"] = now + LOCKOUT_SECONDS
        st.session_state["login_attempts"] = 0
        return False, LOCKOUT_SECONDS
    return True, 0


def register_failed_attempt():
    st.session_state["login_attempts"] = st.session_state.get("login_attempts", 0) + 1


def reset_attempts():
    st.session_state["login_attempts"] = 0
    st.session_state["lockout_until"] = 0.0


def issue_session_token(role: str) -> str:
    """رمز جلسة موقّع بـ HMAC"""
    payload = f"{role}|{secrets.token_hex(16)}|{int(time.time())}"
    sig = hmac.new(
        (OWNER_CODE_HASH + SPECIALIST_CODE_HASH).encode(),
        payload.encode(), hashlib.sha256
    ).hexdigest()
    return f"{payload}|{sig}"


def verify_session_token(token: str) -> bool:
    if not token or token.count("|") != 3:
        return False
    try:
        role, nonce, ts, sig = token.split("|")
        payload = f"{role}|{nonce}|{ts}"
        expected = hmac.new(
            (OWNER_CODE_HASH + SPECIALIST_CODE_HASH).encode(),
            payload.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return False
        return (time.time() - int(ts)) <= SESSION_TIMEOUT
    except Exception:
        return False


# ═════════════════════════════════════════════════════════════════════════════
# 3. مدير الخطوط العربية (PDF)
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
        self.ready = False
        if not PDF_OK:
            return
        for p in [
            os.path.join(FONT_DIR, "Amiri-Regular.ttf"),
            "Amiri-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]:
            if os.path.exists(p) and self._register(p):
                return

    def _register(self, path):
        try:
            pdfmetrics.registerFont(TTFont('TaworAr', path))
            self.font_name = 'TaworAr'
            self.ready = True
            return True
        except Exception:
            return False


font_mgr = ArabicFontManager()


class ArabicProcessor:
    @staticmethod
    @lru_cache(maxsize=5000)
    def fix(text):
        if not text:
            return ""
        text = str(text)
        if not AR_OK:
            return text
        try:
            return get_display(arabic_reshaper.reshape(text), base_dir='R')
        except Exception:
            return text


arp = ArabicProcessor()
def ar(t): return arp.fix(t)


# ═════════════════════════════════════════════════════════════════════════════
# 4. مكتبة الأعلاف الشاملة — NRC / INRA / FAO
# ═════════════════════════════════════════════════════════════════════════════

FEEDS = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء":          {"CP": 8.5,  "DC": 0.85, "SE": 80.0, "NDF": 9.5,  "ADF": 3.2,  "EE": 3.8,  "ASH": 1.3,  "Ca": 0.02, "P": 0.27},
        "ذرة بيضاء":          {"CP": 8.8,  "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5,  "EE": 3.5,  "ASH": 1.4,  "Ca": 0.02, "P": 0.26},
        "ذرة شامية":          {"CP": 8.3,  "DC": 0.86, "SE": 82.0, "NDF": 9.0,  "ADF": 3.0,  "EE": 4.0,  "ASH": 1.2,  "Ca": 0.02, "P": 0.28},
        "شعير مطحون":         {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5,  "EE": 2.2,  "ASH": 2.5,  "Ca": 0.05, "P": 0.35},
        "سورجم (فتريتة)":      {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5,  "EE": 3.0,  "ASH": 1.8,  "Ca": 0.03, "P": 0.30},
        "قمح محلي":           {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8,  "EE": 2.0,  "ASH": 1.6,  "Ca": 0.04, "P": 0.32},
        "جريش أرز":           {"CP": 7.8,  "DC": 0.82, "SE": 82.0, "NDF": 5.5,  "ADF": 2.5,  "EE": 8.5,  "ASH": 4.2,  "Ca": 0.06, "P": 0.30},
        "شوفان علفي":         {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0,  "ASH": 3.0,  "Ca": 0.08, "P": 0.35},
        "دخن محلي":           {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5,  "EE": 4.0,  "ASH": 2.2,  "Ca": 0.05, "P": 0.31},
        "كسرة خبز":           {"CP": 10.5, "DC": 0.82, "SE": 75.0, "NDF": 8.0,  "ADF": 3.5,  "EE": 5.5,  "ASH": 3.5,  "Ca": 0.10, "P": 0.20},
    },
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني":  {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5,  "EE": 1.5,  "ASH": 5.5,  "Ca": 0.20, "P": 0.65},
        "كسب فول صويا 44%":     {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0,  "EE": 1.8,  "ASH": 6.0,  "Ca": 0.35, "P": 0.65},
        "كسب فول صويا 46%":     {"CP": 46.0, "DC": 0.905,"SE": 75.0, "NDF": 12.5, "ADF": 7.5,  "EE": 1.6,  "ASH": 6.1,  "Ca": 0.35, "P": 0.65},
        "كسب فول صويا 48%":     {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0,  "EE": 1.5,  "ASH": 6.2,  "Ca": 0.35, "P": 0.65},
        "كسب عباد الشمس 36%":   {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5,  "ASH": 6.5,  "Ca": 0.40, "P": 1.00},
        "كسب عباد الشمس 32%":   {"CP": 32.0, "DC": 0.72, "SE": 38.0, "NDF": 42.0, "ADF": 28.0, "EE": 2.0,  "ASH": 7.0,  "Ca": 0.42, "P": 0.95},
        "كسب بذور القطن":      {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2,  "ASH": 6.5,  "Ca": 0.20, "P": 1.10},
        "كسب بذور الكتان":     {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8,  "ASH": 5.8,  "Ca": 0.35, "P": 0.85},
        "كسب السمسم":          {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5,  "EE": 8.5,  "ASH": 12.5, "Ca": 2.00, "P": 1.20},
        "كسب جلوتين 60%":      {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5,  "ADF": 5.5,  "EE": 2.5,  "ASH": 3.5,  "Ca": 0.15, "P": 0.50},
        "كسب جلوتين 40%":      {"CP": 40.0, "DC": 0.88, "SE": 72.0, "NDF": 15.0, "ADF": 8.0,  "EE": 3.0,  "ASH": 5.0,  "Ca": 0.18, "P": 0.55},
        "كسب نواة النخيل":     {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5,  "ASH": 4.5,  "Ca": 0.30, "P": 0.55},
        "كسب الكانولا":        {"CP": 36.0, "DC": 0.82, "SE": 60.0, "NDF": 28.0, "ADF": 18.0, "EE": 3.5,  "ASH": 6.5,  "Ca": 0.65, "P": 1.10},
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)":     {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5,  "ASH": 5.5,  "Ca": 0.12, "P": 1.10},
        "البرسيم الجاف":      {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0,  "ASH": 10.5, "Ca": 1.50, "P": 0.25},
        "مولاس قصب السكر":    {"CP": 4.0,  "DC": 0.95, "SE": 50.0, "NDF": 1.5,  "ADF": 0.8,  "EE": 0.5,  "ASH": 8.5,  "Ca": 0.70, "P": 0.05},
        "تبن قمح":            {"CP": 3.2,  "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5,  "ASH": 8.5,  "Ca": 0.30, "P": 0.08},
        "قشر فول سوداني":      {"CP": 5.0,  "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0,  "ASH": 5.5,  "Ca": 0.25, "P": 0.10},
        "سرسة الأرز":          {"CP": 2.5,  "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5, "Ca": 0.15, "P": 0.08},
    },
    "🧬 البروتين الحيواني": {
        "مسحوق أسماك 60%":     {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5,  "ASH": 22.5, "Ca": 5.50, "P": 3.20},
        "مسحوق أسماك 72%":     {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5,  "ASH": 18.5, "Ca": 4.80, "P": 2.80},
        "مسحوق اللحم والعظم":   {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5, "Ca": 9.00, "P": 4.50},
        "مسحوق الدم":          {"CP": 80.0, "DC": 0.65, "SE": 55.0, "NDF": 1.0, "ADF": 0.5, "EE": 1.5,  "ASH": 6.0,  "Ca": 0.30, "P": 0.30},
        "مركزات دواجن":        {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5,  "ASH": 12.5, "Ca": 2.50, "P": 1.20},
        "مركزات مواشي":        {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5,"ADF": 8.5, "EE": 3.0,  "ASH": 15.5, "Ca": 3.00, "P": 1.50},
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي":          {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0},
        "ليسين سلفات":        {"CP": 79.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0},
        "ميثيونين نقي":       {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3, "Ca": 0.0, "P": 0.0},
        "ميثيونين هيدروكسي":  {"CP": 88.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0},
        "ثريونين":            {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2, "Ca": 0.0, "P": 0.0},
        "تريبتوفان":          {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1, "Ca": 0.0, "P": 0.0},
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن":  {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 8.0},
        "بريمكس بياض":        {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 22.0, "P": 7.0},
        "بريمكس أبقار":       {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0},
        "بريمكس مجترات":      {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 18.0, "P": 9.0},
        "بريمكس خيول":        {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 8.0},
        "بريمكس إبل":         {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 20.0, "P": 10.0},
        "بريمكس أسماك":       {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 15.0, "P": 7.0},
        "إنزيم فايتيز":        {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0, "Ca": 0.0, "P": 0.0},
        "إنزيم NSP":          {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0, "Ca": 0.0, "P": 0.0},
        "خمائر حية":          {"CP": 45.0, "DC": 0.75, "SE": 30.0, "NDF": 8.0, "ADF": 4.0, "EE": 1.0, "ASH": 8.0, "Ca": 0.15, "P": 1.20},
        "MOS مستخلص خمائر":   {"CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5, "EE": 1.5, "ASH": 8.5, "Ca": 0.10, "P": 0.20},
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري":         {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 38.0, "P": 0.0},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5, "Ca": 23.0, "P": 18.0},
        "فوسفات أحادي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 17.0, "P": 22.0},
        "ملح الطعام":           {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9, "Ca": 0.0, "P": 0.0},
        "بيكربونات الصوديوم":   {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 0.0, "P": 0.0},
        "أكسيد المغنيسيوم":     {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5, "Ca": 0.0, "P": 0.0},
        "يوريا علفية":          {"CP": 287.0,"DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0, "Ca": 0.0, "P": 0.0},
        "مضاد سموم فطرية":     {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Ca": 0.0, "P": 0.0},
        "كولين كلوريد":        {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0, "Ca": 0.0, "P": 0.0},
    },
    "🌰 الزيوت النباتية والحيوانية": {
        "زيت ذرة":          {"CP": 0.0, "DC": 0.0, "SE": 220.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "max_poultry": 6.0, "max_ruminant": 5.0, "source": "NRC 2012"},
        "زيت فول الصويا":    {"CP": 0.0, "DC": 0.0, "SE": 215.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "max_poultry": 8.0, "max_ruminant": 5.0, "source": "Ross 308 / NRC"},
        "زيت عباد الشمس":    {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "max_poultry": 6.0, "max_ruminant": 4.0, "source": "NRC 2007"},
        "زيت بذرة القطن":    {"CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "max_poultry": 3.0, "max_ruminant": 5.0, "source": "NRC 2012"},
        "زيت الكتان":        {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "max_poultry": 3.0, "max_ruminant": 3.0, "source": "NRC 2007 Horse"},
        "زيت جوز الهند":     {"CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "max_poultry": 5.0, "max_ruminant": 3.0, "source": "NRC 2012"},
        "زيت النخيل":        {"CP": 0.0, "DC": 0.0, "SE": 215.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "max_poultry": 6.0, "max_ruminant": 5.0, "source": "NRC 2012"},
        "زيت الكانولا":      {"CP": 0.0, "DC": 0.0, "SE": 200.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "max_poultry": 5.0, "max_ruminant": 5.0, "source": "NRC 2012"},
        "زيت السمسم":        {"CP": 0.0, "DC": 0.0, "SE": 205.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "max_poultry": 4.0, "max_ruminant": 3.0, "source": "NRC 2007"},
        "زيت الزيتون":       {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "max_poultry": 4.0, "max_ruminant": 4.0, "source": "INRA 2018"},
        "زيت الفول السوداني": {"CP": 0.0, "DC": 0.0, "SE": 210.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "max_poultry": 5.0, "max_ruminant": 4.0, "source": "NRC 2012"},
        "زيت السمك":         {"CP": 0.0, "DC": 0.0, "SE": 235.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "max_poultry": 2.0, "max_ruminant": 2.0, "source": "NRC Fish Nutrition"},
        "شحم حيواني Tallow": {"CP": 0.0, "DC": 0.0, "SE": 230.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "max_poultry": 6.0, "max_ruminant": 5.0, "source": "NRC 2012"},
        "دهن الدجاج":        {"CP": 0.0, "DC": 0.0, "SE": 225.0, "NDF": 0.0, "ADF": 0.0, "EE": 100.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "max_poultry": 6.0, "max_ruminant": 0.0, "source": "NRC 2012"},
    },
}


# فهرس سريع
INGREDIENT_INDEX = {}
for _cat, _items in FEEDS.items():
    for _name, _data in _items.items():
        INGREDIENT_INDEX[_name] = _data

OIL_NAMES = set(FEEDS["🌰 الزيوت النباتية والحيوانية"].keys())


# ═════════════════════════════════════════════════════════════════════════════
# 5. معايير الزيوت العالمية
# ═════════════════════════════════════════════════════════════════════════════

MAX_OIL_STD = {
    "دواجن_بادي":       {"max": 8.0, "opt": 5.0, "src": "Ross 308 2020"},
    "دواجن_نامي":       {"max": 7.0, "opt": 4.5, "src": "Ross 308 2020"},
    "دواجن_ناهي":       {"max": 7.0, "opt": 4.0, "src": "Ross 308 2020"},
    "دواجن_بياض":       {"max": 5.0, "opt": 2.5, "src": "NRC 1994"},
    "سمان_بادي":        {"max": 6.0, "opt": 4.0, "src": "NRC Quail"},
    "سمان_بياض":        {"max": 5.0, "opt": 2.5, "src": "NRC Quail"},
    "أبقار_حليب":       {"max": 6.0, "opt": 4.0, "src": "NRC 2001 Dairy"},
    "أبقار_تسمين":      {"max": 6.0, "opt": 4.5, "src": "NRC 2001"},
    "أغنام_تسمين":      {"max": 5.0, "opt": 3.5, "src": "NRC 2007"},
    "أغنام_حليب":       {"max": 5.0, "opt": 3.5, "src": "NRC 2007"},
    "ماعز_تسمين":       {"max": 5.0, "opt": 3.5, "src": "NRC 2007"},
    "ماعز_حليب":        {"max": 5.0, "opt": 3.5, "src": "NRC 2007"},
    "إبل_تسمين":        {"max": 6.0, "opt": 4.0, "src": "FAO 2010"},
    "إبل_حليب":         {"max": 5.0, "opt": 3.5, "src": "FAO 2010"},
    "إبل_سباق":         {"max": 8.0, "opt": 6.0, "src": "FAO 2010"},
    "خيول_رياضة":       {"max": 10.0,"opt": 7.0, "src": "NRC 2007 Horses"},
    "خيول_نمو":         {"max": 8.0, "opt": 5.0, "src": "NRC 2007 Horses"},
    "خيول_مرضعات":      {"max": 8.0, "opt": 5.5, "src": "NRC 2007 Horses"},
    "أسماك_بادئ":       {"max": 15.0,"opt": 10.0,"src": "NRC Fish"},
    "أسماك_نمو":        {"max": 12.0,"opt": 8.0, "src": "NRC Fish"},
}

def get_oil_std(key: str) -> dict:
    return MAX_OIL_STD.get(key, {"max": 5.0, "opt": 3.0, "src": "NRC General"})


# ═════════════════════════════════════════════════════════════════════════════
# 6. الاحتياجات الغذائية لكل حيوان — NRC / FAO
# ═════════════════════════════════════════════════════════════════════════════

@dataclass
class Requirement:
    DP: float; CP: float; SE: float; NDF: float; ADF: float
    EE: float; ASH: float; Ca: float; P: float
    name_ar: str = ""; note: str = ""; oil_key: str = ""


def get_cattle_req(ptype: str, milk: float = 20.0, wt: float = 500.0) -> Requirement:
    if ptype == "حليب_عالي":
        dp = 12.5 + milk * 0.30
        return Requirement(dp, dp/0.70, 60+milk*0.35, 30, 19, 5.5, 8.0,
                          0.55+milk*0.003, 0.33+milk*0.0015,
                          "أبقار حلابة عالية", f"إنتاج {milk} كجم/يوم", "أبقار_حليب")
    if ptype == "حليب_متوسط":
        dp = 11.0 + milk * 0.25
        return Requirement(dp, dp/0.72, 55+milk*0.30, 33, 21, 4.5, 8.0,
                          0.50+milk*0.0025, 0.30+milk*0.0012,
                          "أبقار حلابة متوسطة", f"إنتاج {milk} كجم/يوم", "أبقار_حليب")
    if ptype == "تسمين_مكثف":
        return Requirement(11.5, 14.5, 72, 32, 20, 4.5, 7.5, 0.65, 0.38,
                          "تسمين مكثف", "ADG >1.3 كجم", "أبقار_تسمين")
    if ptype == "تسمين_عادي":
        return Requirement(9.5, 12.0, 65, 38, 24, 4.0, 7.5, 0.55, 0.32,
                          "تسمين عادي", "ADG ~0.8 كجم", "أبقار_تسمين")
    if ptype == "حمل_أخير":
        return Requirement(11.5, 14.5, 67, 35, 22, 4.2, 8.0, 0.70, 0.42,
                          "حمل آخر", "شهر 7-9", "أبقار_حليب")
    return Requirement(7.5, 10.0, 53, 45, 28, 3.0, 8.5, 0.42, 0.26,
                      "صيانة", "بدون إنتاج", "أبقار_تسمين")


def get_sheep_req(ptype: str, male: bool = True, litter: int = 1) -> Requirement:
    if male:
        if ptype == "تسمين_مكثف":
            return Requirement(11.5, 14.5, 64, 28, 17, 4.0, 8.0, 0.65, 0.36,
                              "تسمين حملان مكثف", "ADG >250 جم", "أغنام_تسمين")
        if ptype == "تسمين_عادي":
            return Requirement(9.5, 12.0, 59, 33, 21, 3.6, 8.0, 0.55, 0.32,
                              "تسمين عادي", "ADG ~180 جم", "أغنام_تسمين")
        return Requirement(8.5, 11.0, 55, 38, 24, 3.2, 8.5, 0.50, 0.30,
                          "حملان تيد", "تسمين نهائي", "أغنام_تسمين")
    if ptype == "مرضعات":
        dp = 10.5 + (litter-1)*1.5
        return Requirement(dp, dp/0.72, 60+(litter-1)*5, 30, 19, 4.5, 8.5,
                          0.65+(litter-1)*0.10, 0.38+(litter-1)*0.05,
                          f"نعاج مرضعات ({litter})", "إدرار عالي", "أغنام_حليب")
    if ptype == "حامل_أخير":
        return Requirement(10.5, 13.5, 62, 32, 20, 3.8, 8.0, 0.60, 0.35,
                          "حامل (4-5)", "دفع غذائي", "أغنام_حليب")
    if ptype == "حامل_متوسط":
        return Requirement(8.5, 11.0, 55, 38, 24, 3.4, 8.0, 0.50, 0.30,
                          "حامل (1-3)", "نمو مبكر", "أغنام_حليب")
    return Requirement(7.2, 9.5, 48, 45, 28, 3.0, 8.5, 0.42, 0.26,
                      "صيانة", "بدون إنتاج", "أغنام_حليب")


def get_goat_req(ptype: str, male: bool = True, milk: float = 2.0) -> Requirement:
    if male:
        if ptype == "تسمين_جديان":
            return Requirement(11.0, 14.0, 62, 30, 19, 3.8, 8.0, 0.62, 0.34,
                              "تسمين جديان", "نمو سريع", "ماعز_تسمين")
        return Requirement(9.0, 11.5, 57, 36, 22, 3.5, 8.0, 0.55, 0.30,
                          "تيوس تسمين", "تسمين نهائي", "ماعز_تسمين")
    if ptype == "حلابة_عالي":
        dp = 11.5 + milk * 0.45
        return Requirement(dp, dp/0.70, 58+milk*0.45, 29, 18, 4.5, 8.5,
                          0.60+milk*0.008, 0.35+milk*0.004,
                          f"عنزات حلابة ({milk} كجم)", "إدرار عالي", "ماعز_حليب")
    if ptype == "حلابة_متوسط":
        dp = 10.0 + milk * 0.35
        return Requirement(dp, dp/0.72, 55+milk*0.40, 32, 20, 4.0, 8.5,
                          0.55+milk*0.006, 0.32+milk*0.003,
                          f"عنزات حلابة ({milk} كجم)", "إدرار متوسط", "ماعز_حليب")
    if ptype == "حامل_أخير":
        return Requirement(10.0, 13.0, 60, 33, 21, 3.8, 8.0, 0.60, 0.35,
                          "عنزات حامل", "دفع غذائي", "ماعز_حليب")
    return Requirement(6.8, 9.0, 46, 46, 28, 3.0, 8.5, 0.42, 0.26,
                      "عنزات صيانة", "بدون إنتاج", "ماعز_حليب")


def get_camel_req(ptype: str, wt: float = 400.0, milk: float = 5.0) -> Requirement:
    dm = wt * 0.025
    if ptype == "نمو":
        return Requirement(10.5, 13.5, 60, 38, 24, 4.0, 8.0, 0.65, 0.38,
                          "إبل نمو", f"وزن {wt} | DM {dm:.1f}", "إبل_تسمين")
    if ptype == "تسمين":
        return Requirement(9.5, 12.0, 65, 35, 22, 4.5, 7.5, 0.60, 0.35,
                          "إبل تسمين", f"وزن {wt}", "إبل_تسمين")
    if ptype == "حليب":
        dp = 12.0 + milk * 0.25
        return Requirement(dp, dp/0.70, 62+milk*0.40, 32, 20, 5.0, 8.5,
                          0.70+milk*0.006, 0.40+milk*0.003,
                          f"إبل حلابة ({milk} لتر)", "دهن حليب 3-5%", "إبل_حليب")
    if ptype == "سباق":
        return Requirement(14.0, 17.0, 72, 28, 17, 6.0, 9.0, 0.85, 0.50,
                          "إبل سباق", "طاقة عالية", "إبل_سباق")
    return Requirement(7.0, 9.0, 48, 48, 30, 3.5, 9.0, 0.42, 0.26,
                      "إبل صيانة", f"وزن {wt}", "إبل_حليب")


def get_horse_req(ptype: str) -> Requirement:
    if ptype == "رياضة_مكثف":
        return Requirement(10.5, 13.5, 70, 30, 18, 7.0, 7.5, 0.70, 0.40,
                          "خيول رياضة مكثف", "جهد عالي", "خيول_رياضة")
    if ptype == "رياضة_عادي":
        return Requirement(9.0, 11.5, 63, 36, 22, 5.0, 7.5, 0.55, 0.32,
                          "خيول رياضة عادي", "نشاط متوسط", "خيول_رياضة")
    if ptype == "نمو_أمهار":
        return Requirement(12.0, 15.0, 65, 30, 18, 5.0, 8.0, 0.75, 0.42,
                          "أمهار نمو", "نمو هيكلي", "خيول_نمو")
    if ptype == "مرضعات":
        return Requirement(12.5, 16.0, 68, 32, 20, 5.5, 8.0, 0.80, 0.45,
                          "فرسات مرضعات", "إدرار مرتفع", "خيول_مرضعات")
    return Requirement(7.2, 9.5, 53, 46, 29, 3.5, 8.0, 0.45, 0.28,
                      "خيول صيانة", "بدون جهد", "خيول_نمو")


def get_poultry_req(strain: str, age: int) -> Requirement:
    if strain == "لاحم":
        if age <= 1:
            return Requirement(20.0, 23.0, 76, 8, 4, 5.0, 6.5, 1.00, 0.50,
                              "بادي لاحم", "Energy 3000", "دواجن_بادي")
        if age <= 3:
            return Requirement(18.5, 21.0, 74, 9, 5, 5.0, 6.0, 0.90, 0.45,
                              "نامي لاحم", "Energy 3100", "دواجن_نامي")
        if age <= 5:
            return Requirement(17.0, 19.5, 75, 10, 5.5, 4.5, 6.0, 0.87, 0.43,
                              "ناهي لاحم", "Energy 3150", "دواجن_ناهي")
        return Requirement(16.5, 19.0, 75, 10, 5.5, 4.5, 6.0, 0.85, 0.42,
                          "ناهي لاحم (6+)", "Energy 3200", "دواجن_ناهي")
    if age <= 6:
        return Requirement(17.0, 20.0, 72, 10, 5.5, 4.0, 7.0, 1.00, 0.50,
                          "بادي بياض", "تحضير للبيض", "دواجن_بياض")
    if age <= 18:
        return Requirement(14.5, 17.0, 70, 12, 6.5, 4.0, 9.0, 1.50, 0.45,
                          "نامي بياض", "نمو هيكلي", "دواجن_بياض")
    return Requirement(15.5, 18.0, 72, 11, 6.0, 4.2, 11.5, 3.80, 0.45,
                      "بياض إنتاجي", "إنتاج بيض", "دواجن_بياض")


def get_quail_req(strain: str, age: int) -> Requirement:
    if strain == "بياض":
        return Requirement(15.0, 18.0, 68, 11, 5.5, 4.5, 9.0, 2.50, 0.45,
                          "سمان بياض", "إنتاج بيض", "سمان_بياض")
    if age <= 2:
        return Requirement(20.5, 24.0, 74, 8, 4, 5.5, 6.5, 1.00, 0.55,
                          "سمان بادي", "نمو سريع", "سمان_بادي")
    if age <= 4:
        return Requirement(18.5, 22.0, 72, 9, 4.5, 5.0, 6.0, 0.90, 0.50,
                          "سمان نامي", "نمو متوسط", "سمان_بادي")
    return Requirement(17.0, 20.0, 70, 10, 5, 4.5, 6.0, 0.85, 0.45,
                      "سمان ناهي", "تسمين نهائي", "سمان_بادي")


def get_fish_req(species: str, stage: str) -> Requirement:
    if "بادئ" in stage or "زريعة" in stage:
        return Requirement(32.0, 40.0, 72, 8, 4, 10.0, 11.0, 1.50, 0.90,
                          f"{species} بادئ", "بروتين عالٍ", "أسماك_بادئ")
    if "نمو" in stage:
        return Requirement(25.0, 32.0, 70, 12, 6, 8.0, 9.0, 1.00, 0.70,
                          f"{species} نمو", "متوسط", "أسماك_نمو")
    return Requirement(22.0, 28.0, 68, 13, 7, 8.0, 9.5, 0.90, 0.65,
                      f"{species} تسمين", "طاقة عالية", "أسماك_نمو")


def req_to_dict(r: Requirement) -> dict:
    return {"CP": r.CP, "DP": r.DP, "SE": r.SE, "NDF": r.NDF,
            "ADF": r.ADF, "EE": r.EE, "ASH": r.ASH, "Ca": r.Ca, "P": r.P}


# ═════════════════════════════════════════════════════════════════════════════
# 7. محرك الحسابات والتركيب — Linear Programming + Precision Metrics
# ═════════════════════════════════════════════════════════════════════════════

def compute_nutrients(formula: Dict[str, float]) -> Dict[str, float]:
    """حساب العناصر الغذائية الكلية للخلطة"""
    t = {"CP":0.0,"DP":0.0,"SE":0.0,"NDF":0.0,"ADF":0.0,"EE":0.0,"ASH":0.0,"Ca":0.0,"P":0.0}
    for ing, pct in formula.items():
        d = INGREDIENT_INDEX.get(ing)
        if not d: continue
        f = pct / 100.0
        t["CP"]  += f * d.get("CP", 0)
        t["DP"]  += f * d.get("CP", 0) * d.get("DC", 0)
        t["SE"]  += f * d.get("SE", 0)
        t["NDF"] += f * d.get("NDF", 0)
        t["ADF"] += f * d.get("ADF", 0)
        t["EE"]  += f * d.get("EE", 0)
        t["ASH"] += f * d.get("ASH", 0)
        t["Ca"]  += f * d.get("Ca", 0)
        t["P"]   += f * d.get("P", 0)
    return t


def total_oil_pct(formula: Dict[str, float]) -> float:
    return sum(p for i, p in formula.items() if i in OIL_NAMES)


def evaluate_diff(pct: float) -> dict:
    a = abs(pct)
    if a <= 0.5:   return {"label":"🎯 مطابق تماماً","color":"#0d5302","bg":"#c8e6c9","score":100}
    if a <= 2.0:   return {"label":"🌟 ممتاز","color":"#1b5e20","bg":"#dcedc8","score":95}
    if a <= 5.0:   return {"label":"✅ جيد جداً","color":"#2e7d32","bg":"#e8f5e9","score":85}
    if a <= 10.0:  return {"label":"🟢 جيد","color":"#558b2f","bg":"#f1f8e9","score":75}
    if a <= 15.0:  return {"label":"⭐ مقبول","color":"#f9a825","bg":"#fff8e1","score":65}
    if a <= 25.0:  return {"label":"⚠️ بتحفظ","color":"#ef6c00","bg":"#fff3e0","score":50}
    if a <= 40.0:  return {"label":"🟠 ضعيف","color":"#e65100","bg":"#ffe0b2","score":35}
    return {"label":"❌ غير مطابق","color":"#c62828","bg":"#ffebee","score":20}


def overall_rating(rows: list) -> dict:
    if not rows: return {"label":"غير محدد","score":0,"color":"#666"}
    scores = [r["score"] for r in rows]
    avg = sum(scores)/len(scores)
    if avg >= 95: return {"label":"🏆 ممتازة","score":avg,"color":"#1b5e20"}
    if avg >= 85: return {"label":"🌟 جيدة جداً","score":avg,"color":"#2e7d32"}
    if avg >= 70: return {"label":"✅ جيدة","score":avg,"color":"#558b2f"}
    if avg >= 55: return {"label":"⭐ مقبولة","score":avg,"color":"#f9a825"}
    return {"label":"⚠️ تحتاج تحسين","score":avg,"color":"#e65100"}


def rmse(actual: dict, target: dict, keys: list) -> float:
    """جذر متوسط مربع الخطأ — مؤشر الدقة العلمية"""
    errs = []
    for k in keys:
        tv = target.get(k, 0)
        if tv <= 0: continue
        errs.append(((actual.get(k, 0) - tv) / tv) ** 2)
    return float(np.sqrt(np.mean(errs)) * 100) if errs else 0.0


def auto_formulate(available: list, prices: dict, req: Requirement,
                   oil_key: str, tol: float = 0.3, max_iter: int = 50) -> dict:
    """محرك التركيب الخطي الذكي مع مطابقة دقيقة لكل العناصر"""
    valid = [i for i in available if i in INGREDIENT_INDEX]
    if len(valid) < 3:
        return {"success": False, "message": "اختر 3 مكونات على الأقل"}

    n = len(valid)
    c = [prices.get(i, 300.0) for i in valid]

    # مصفوفات المكونات
    CP_r = [INGREDIENT_INDEX[i]["CP"] for i in valid]
    DC_r = [INGREDIENT_INDEX[i]["DC"] for i in valid]
    DP_r = [CP_r[i] * DC_r[i] for i in range(n)]
    SE_r = [INGREDIENT_INDEX[i]["SE"] for i in valid]
    NDF_r = [INGREDIENT_INDEX[i]["NDF"] for i in valid]
    ADF_r = [INGREDIENT_INDEX[i]["ADF"] for i in valid]
    Ca_r = [INGREDIENT_INDEX[i]["Ca"] for i in valid]
    P_r  = [INGREDIENT_INDEX[i]["P"] for i in valid]

    # قيود individual bounds
    bounds = []
    for i in valid:
        d = INGREDIENT_INDEX[i]
        if i in OIL_NAMES:
            oil_std = get_oil_std(oil_key)
            bounds.append((0.0, oil_std["max"] * 0.5))
        elif "يوريا" in i: bounds.append((0.0, 1.0))
        elif "مولاس" in i: bounds.append((0.0, 10.0))
        elif "ملح الطعام" in i: bounds.append((0.3, 0.7))
        elif "بيكربونات" in i: bounds.append((0.0, 1.5))
        elif "مضاد سموم" in i: bounds.append((0.05, 0.25))
        elif "بريمكس" in i: bounds.append((0.15, 0.5))
        elif "إنزيم" in i: bounds.append((0.02, 0.10))
        elif "الحجر الجيري" in i: bounds.append((0.0, 10.0))
        elif "فوسفات" in i: bounds.append((0.0, 2.5))
        elif "تبن" in i or "قش" in i or "سرسة" in i: bounds.append((0.0, 20.0))
        else: bounds.append((0.0, 100.0))

    oil_ind = [1.0 if i in OIL_NAMES else 0.0 for i in valid]
    has_oils = sum(oil_ind) > 0
    oil_max = get_oil_std(oil_key)["max"]

    targets = req_to_dict(req)
    best, best_score = None, float("inf")
    cur = dict(targets)

    for it in range(max_iter):
        # قيود المساواة: المجموع = 100 | DP | Ca | P
        A_eq = [[1.0]*n, DP_r, Ca_r, P_r]
        b_eq = [100.0, cur["DP"]*100, targets["Ca"]*100, targets["P"]*100]

        # قيود عدم المساواة
        A_ub, b_ub = [], []
        A_ub.append([-x for x in SE_r]);  b_ub.append(-cur["SE"]*100)
        A_ub.append(NDF_r);               b_ub.append(cur["NDF"]*1.10*100)
        A_ub.append(ADF_r);               b_ub.append(cur["ADF"]*1.10*100)
        if has_oils:
            A_ub.append(oil_ind);         b_ub.append(oil_max*100)

        try:
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method='highs',
                          options={"time_limit": 15, "presolve": True})
        except Exception:
            res = type('X', (), {'success': False})()

        # تبسيط إذا فشل
        if not res.success:
            A_eq_s = [[1.0]*n, DP_r]
            b_eq_s = [100.0, cur["DP"]*100]
            try:
                res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq_s, b_eq=b_eq_s,
                              bounds=bounds, method='highs')
            except Exception:
                res = type('X', (), {'success': False})()

        if not res.success:
            cur["NDF"] *= 1.05; cur["ADF"] *= 1.05
            continue

        formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
        actual = compute_nutrients(formula)

        # مؤشرات الدقة
        errs = {}
        for k in ["DP", "SE", "NDF", "ADF", "Ca", "P"]:
            tv = targets.get(k, 0)
            if tv > 0:
                errs[k] = abs(actual.get(k, 0) - tv) / tv

        weights = {"DP": 5.0, "SE": 3.0, "NDF": 1.5, "ADF": 1.0, "Ca": 1.0, "P": 1.0}
        score = sum(errs.get(k, 0) * weights[k] for k in errs)

        if score < best_score:
            best_score = score
            best = {
                "success": True, "formula": formula, "cost": res.fun / 100.0,
                "actual": actual, "targets": targets,
                "iterations": it + 1,
                "rmse_dp": abs(actual["DP"] - targets["DP"]),
                "rmse_se": abs(actual["SE"] - targets["SE"]),
                "rmse_ndf": abs(actual["NDF"] - targets["NDF"]),
                "rmse_ca": abs(actual["Ca"] - targets["Ca"]),
                "total_oil": total_oil_pct(formula),
                "oil_std": get_oil_std(oil_key),
                "overall_rmse": rmse(actual, targets,
                                     ["DP", "SE", "NDF", "ADF", "Ca", "P"]),
            }

        # توقف مبكر
        if errs.get("DP", 1)*100 <= tol and errs.get("SE", 1)*200 <= tol*2:
            best["perfect_match"] = True
            break

        # تحديث تقاربي
        cur["DP"]  += (targets["DP"]  - actual["DP"])  * 0.25
        cur["SE"]  += (targets["SE"]  - actual["SE"])  * 0.20
        cur["NDF"] += (targets["NDF"] - actual["NDF"]) * 0.15
        cur["ADF"] += (targets["ADF"] - actual["ADF"]) * 0.15
        cur["DP"]  = max(5.0,  min(40.0, cur["DP"]))
        cur["SE"]  = max(10.0, min(90.0, cur["SE"]))
        cur["NDF"] = max(5.0,  min(70.0, cur["NDF"]))
        cur["ADF"] = max(3.0,  min(50.0, cur["ADF"]))

    return best or {"success": False, "message": "تعذر إيجاد حل مناسب"}


def auto_salts(animal: str, req: Optional[Requirement] = None) -> dict:
    s = {}
    if animal in ["أغنام", "ماعز", "أبقار", "إبل"]:
        s["بيكربونات الصوديوم"] = 0.75
    s["مضاد سموم فطرية"] = 0.20
    s["ملح الطعام"] = 0.50
    if animal in ["دواجن", "سمان"]:
        s["الحجر الجيري"] = 8.0 if (req and req.Ca > 2.0) else 1.5
        s["فوسفات ثنائي الكالسيوم"] = 1.5
        s["بريمكس تسمين دواجن"] = 0.30
    elif animal == "أسماك":
        s["الحجر الجيري"] = 1.0
        s["فوسفات ثنائي الكالسيوم"] = 1.5
        s["بريمكس أسماك"] = 0.30
    elif animal == "خيول":
        s["الحجر الجيري"] = 1.5
        s["فوسفات ثنائي الكالسيوم"] = 1.5
        s["بريمكس خيول"] = 0.30
    elif animal == "إبل":
        s["الحجر الجيري"] = 2.0
        s["فوسفات ثنائي الكالسيوم"] = 1.5
        s["بريمكس إبل"] = 0.30
    else:
        s["الحجر الجيري"] = 2.0
        s["فوسفات ثنائي الكالسيوم"] = 1.5
        s["بريمكس مجترات"] = 0.30
    return s


# ═════════════════════════════════════════════════════════════════════════════
# 8. بدائل الحليب
# ═════════════════════════════════════════════════════════════════════════════

MILK_REPLACER_STD = {
    "عجول (Calves)":     {"CP":24.0,"Fat":24.0,"Lactose":45.0,"Lysine":2.1,"Ca":0.75,"P":0.70,"notes":"عمر 1-6 أسابيع"},
    "حملان (Lambs)":     {"CP":24.0,"Fat":24.0,"Lactose":40.0,"Lysine":2.1,"Ca":0.80,"P":0.70,"notes":"≥24% دهن"},
    "جديان (Kids)":      {"CP":24.0,"Fat":24.0,"Lactose":42.0,"Lysine":2.1,"Ca":0.80,"P":0.70,"notes":"بديل جديان"},
    "إبل (Camel Calves)":{"CP":26.0,"Fat":28.0,"Lactose":38.0,"Lysine":2.3,"Ca":0.85,"P":0.75,"notes":"بروتين ودهن أعلى"},
    "أمهار (Foals)":     {"CP":22.0,"Fat":20.0,"Lactose":45.0,"Lysine":1.9,"Ca":0.90,"P":0.80,"notes":"توازن خيول"},
}

MILK_REPLACER_ING = {
    "حليب مجفف منزوع الدسم": {"CP":34.0,"Fat":1.0,"Lactose":52.0,"price":3200},
    "حليب مجفف كامل الدسم":  {"CP":26.0,"Fat":28.0,"Lactose":38.0,"price":3800},
    "شرش حليب مجفف":        {"CP":12.0,"Fat":1.5,"Lactose":75.0,"price":1800},
    "بروتين شرش WPC 80%":   {"CP":80.0,"Fat":5.0,"Lactose":8.0,"price":8500},
    "كازين":                {"CP":85.0,"Fat":2.0,"Lactose":2.0,"price":9000},
    "مركز بروتين صويا":     {"CP":66.0,"Fat":1.0,"Lactose":0.0,"price":2800},
    "زيت جوز الهند":        {"CP":0.0,"Fat":100.0,"Lactose":0.0,"price":2200},
    "زيت النخيل":           {"CP":0.0,"Fat":100.0,"Lactose":0.0,"price":1200},
    "لاكتوز نقي":           {"CP":0.0,"Fat":0.0,"Lactose":100.0,"price":1400},
    "بريمكس فيتامينات":      {"CP":0.0,"Fat":0.0,"Lactose":0.0,"price":6500},
    "كالسيوم كربونات":       {"CP":0.0,"Fat":0.0,"Lactose":0.0,"price":200},
    "فوسفات ثنائي الكالسيوم": {"CP":0.0,"Fat":0.0,"Lactose":0.0,"price":1100},
}


def formulate_milk_replacer(animal: str, volume: float, selected: list) -> dict:
    std = MILK_REPLACER_STD.get(animal)
    if not std:
        return {"success": False, "message": "نوع غير مدعوم"}
    valid = [i for i in selected if i in MILK_REPLACER_ING]
    if len(valid) < 3:
        return {"success": False, "message": "اختر 3 مكونات على الأقل"}
    n = len(valid)
    c = [MILK_REPLACER_ING[i]["price"] for i in valid]
    bounds = [(0, 100)] * n
    A_eq = [
        [1.0]*n,
        [MILK_REPLACER_ING[i]["CP"]  for i in valid],
        [MILK_REPLACER_ING[i]["Fat"] for i in valid],
    ]
    b_eq = [100.0, std["CP"]*100, std["Fat"]*100]
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if not res.success:
        return {"success": False, "message": "تعذر التركيب"}
    formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
    actual = {"CP": 0.0, "Fat": 0.0, "Lactose": 0.0}
    for ing, pct in formula.items():
        d = MILK_REPLACER_ING[ing]
        actual["CP"] += pct/100 * d["CP"]
        actual["Fat"] += pct/100 * d["Fat"]
        actual["Lactose"] += pct/100 * d["Lactose"]
    return {"success": True, "formula": formula,
            "cost_kg": res.fun / 10000.0, "std": std, "actual": actual}


# ═════════════════════════════════════════════════════════════════════════════
# 9. المختبر الذكي OCR
# ═════════════════════════════════════════════════════════════════════════════

def match_ingredient(text: str) -> Optional[str]:
    if not text: return None
    tl = text.strip().lower()
    for name in INGREDIENT_INDEX:
        if name.lower() in tl or tl in name.lower():
            return name
    kw = {"ذرة":"ذرة صفراء","corn":"ذرة صفراء","صويا":"كسب فول صويا 44%",
          "شعير":"شعير مطحون","قمح":"قمح محلي","سورجم":"سورجم (فتريتة)",
          "نخالة":"نخالة قمح (ردة)","فول سوداني":"أمباز الفول السوداني",
          "قطن":"كسب بذور القطن","عباد":"كسب عباد الشمس 36%",
          "سمسم":"كسب السمسم","جلوتين":"كسب جلوتين 60%",
          "سمك":"مسحوق أسماك 60%","لحم":"مسحوق اللحم والعظم",
          "ليسين":"ليسين نقي","ميثيونين":"ميثيونين نقي",
          "ملح":"ملح الطعام","حجر":"الحجر الجيري",
          "فوسفات":"فوسفات ثنائي الكالسيوم","مولاس":"مولاس قصب السكر"}
    for k, v in kw.items():
        if k in tl: return v
    return None


def extract_ingredients(image_bytes: bytes) -> dict:
    if not OCR_OK:
        return {"success": False, "message": "pytesseract غير مثبتة"}
    try:
        arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return {"success": False, "message": "صورة غير صالحة"}
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)
        t1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 11, 2)
        texts = []
        for t in [t1, gray]:
            try:
                txt = pytesseract.image_to_string(t, lang='ara+eng',
                        config=r'--oem 3 --psm 6')
                if txt.strip(): texts.append(txt)
            except Exception:
                continue
        full = "\n".join(texts)
        found = {}
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
                            found[matched] = val
                            break
        return {"success": True, "ingredients": found,
                "raw_text": full, "count": len(found)}
    except Exception as e:
        return {"success": False, "message": f"خطأ: {e}"}


# ═════════════════════════════════════════════════════════════════════════════
# 10. مدير مزارع الدجاج اللاحم
# ═════════════════════════════════════════════════════════════════════════════

VACC_SCHEDULE_DEFAULT = {
    1:  {"type":"فيتامين","name":"فيتامين AD3E","dose":"1 مل/لتر","route":"مياه الشرب"},
    7:  {"type":"لقاح","name":"نيوكاسل Lasota","dose":"قطرة عين","route":"قطرة عين"},
    14: {"type":"لقاح","name":"Gumboro","dose":"قطرة فم","route":"مياه"},
    21: {"type":"دواء","name":"مضاد كوكسيديا","dose":"1 جم/لتر 3 أيام","route":"مياه"},
    28: {"type":"فيتامين","name":"فيتامين C + E","dose":"0.5 جم/لتر","route":"مياه"},
    35: {"type":"لقاح","name":"Gumboro booster","dose":"قطرة فم","route":"مياه"},
}


def calc_adg(cur_g: float, init_g: float, age: int) -> float:
    return (cur_g - init_g) / age if age > 0 else 0.0

def calc_fcr(feed_kg: float, gain_kg: float) -> float:
    return feed_kg / gain_kg if gain_kg > 0 else 0.0

def calc_mortality(dead: int, init: int) -> float:
    return (dead / init) * 100 if init > 0 else 0.0

def calc_livability(init: int, dead: int) -> float:
    return 100.0 - calc_mortality(dead, init)

def calc_epef(liv: float, wt_kg: float, age: int, fcr: float) -> float:
    if age <= 0 or fcr <= 0: return 0.0
    return (liv * wt_kg) / (age * fcr) * 100.0

def temp_humidity_table() -> pd.DataFrame:
    return pd.DataFrame({
        "العمر (يوم)": [1, 7, 14, 21, 28, 35, 42],
        "الحرارة (°م)": [33, 30, 28, 26, 24, 22, 21],
        "الرطوبة (%)": [65, 65, 65, 60, 60, 55, 55],
    })


# ═════════════════════════════════════════════════════════════════════════════
# 11. مولد PDF الاحترافي
# ═════════════════════════════════════════════════════════════════════════════

def _ar(text) -> str:
    return ar(text)


def make_pdf_report(formula, req: Requirement, animal: str, breed: str,
                    cost: float, city: str, local_cost: float, local_sym: str,
                    requester: str = "", protein_basis: str = "DP",
                    oil_key: str = "", include_charts: bool = True) -> bytes:
    if not PDF_OK:
        return b""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        rightMargin=40, leftMargin=40, topMargin=80, bottomMargin=60)
    story = []

    def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
        return Paragraph(_ar(text),
            ParagraphStyle('s', fontName=font_mgr.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))

    story.append(P("تقرير فني رسمي — تركيب علفة", size=20,
                   align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#d4af37')))
    story.append(Spacer(1, 12))

    # بيانات
    client_data = [
        [_ar("👤 طالب الخدمة:"), _ar(requester or "................")],
        [_ar("📍 الموقع:"), _ar(city)],
        [_ar("🐾 الفصيل:"), _ar(f"{animal} — {breed}")],
        [_ar("🧬 أساس الحساب:"), _ar(protein_basis)],
        [_ar("📅 التاريخ:"), datetime.now().strftime('%Y-%m-%d %H:%M')],
    ]
    ct = Table(client_data, colWidths=[150, 340])
    ct.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), HexColor('#e8f5e9')),
        ('BACKGROUND', (1,0), (1,-1), HexColor('#fafafa')),
        ('BOX', (0,0), (-1,-1), 1.5, HexColor('#2e7d32')),
        ('INNERGRID', (0,0), (-1,-1), 0.6, HexColor('#c8e6c9')),
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,-1), font_mgr.font_name),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(ct)
    story.append(Spacer(1, 15))

    # جدول المقارنة
    std = req_to_dict(req)
    actual = compute_nutrients(formula)
    labels = {"CP":"بروتين خام","DP":"بروتين مهضوم","SE":"معادل النشاء",
              "NDF":"ألياف NDF","ADF":"ألياف ADF","EE":"دهن",
              "ASH":"رماد","Ca":"كالسيوم","P":"فسفور"}
    header = [_ar(x) for x in ["العنصر","المعيار","المحسوب","الفرق","% الفرق","التقييم"]]
    data = [header]
    cmds = [
        ('BACKGROUND', (0,0), (-1,0), HexColor('#1b5e20')),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), font_mgr.font_name),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 1, HexColor('#9e9e9e')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]
    row = 1
    for k, lbl in labels.items():
        sv = std.get(k, 0); cv = actual.get(k, 0)
        diff = cv - sv
        pct = (diff / sv * 100) if sv else 0
        ev = evaluate_diff(pct)
        data.append([_ar(lbl), f"{sv:.2f}", f"{cv:.2f}",
                     f"{diff:+.3f}", f"{pct:+.2f}%", _ar(ev["label"])])
        cmds.append(('BACKGROUND', (0,row), (-1,row), HexColor(ev["bg"])))
        row += 1
    t = Table(data, colWidths=[95, 70, 70, 70, 70, 110])
    t.setStyle(TableStyle(cmds))
    story.append(t)
    story.append(Spacer(1, 12))

    # دقة
    rms = rmse(actual, std, ["DP","SE","NDF","ADF","Ca","P"])
    story.append(P(f"مؤشر الدقة RMSE: {rms:.3f}% | التكلفة/طن: ${cost:.2f} ({local_cost:,.0f} {local_sym})",
                   size=11, color='#0d47a1'))
    story.append(Spacer(1, 15))

    # جدول الزيوت
    oil_used = [(i, p) for i, p in formula.items() if i in OIL_NAMES]
    if oil_used:
        story.append(P("🌰 الزيوت المستخدمة", size=13, color='#e65100'))
        story.append(Spacer(1, 6))
        oil_data = [[_ar(x) for x in ["الزيت","النسبة %","kcal/kg"]]]
        for ing, pct in oil_used:
            oil_data.append([_ar(ing), f"{pct:.2f}%", f"{pct*90:.0f}"])
        total_oil = sum(p for _, p in oil_used)
        oil_data.append([_ar("الإجمالي"), f"{total_oil:.2f}%", f"{total_oil*90:.0f}"])
        ot = Table(oil_data, colWidths=[250, 100, 100])
        ot.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#e65100')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), font_mgr.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#bf360c')),
            ('BACKGROUND', (0,-1), (-1,-1), HexColor('#ffe0b2')),
        ]))
        story.append(ot)
        story.append(Spacer(1, 15))

    # المكونات
    if formula:
        story.append(P("🌾 المكونات للطن", size=13, color='#1b5e20'))
        story.append(Spacer(1, 6))
        ing_data = [[_ar(x) for x in ["المكون","النسبة %","كجم/طن"]]]
        for ing, pct in formula.items():
            ing_data.append([_ar(ing), f"{pct:.2f}%", f"{pct*10:.1f}"])
        ti = Table(ing_data, colWidths=[270, 110, 110])
        ti.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), font_mgr.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1),
             [HexColor('#ffffff'), HexColor('#f5f5f5')]),
        ]))
        story.append(ti)
        story.append(Spacer(1, 20))

    # توقيع
    sign = [
        [_ar("طالب الخدمة"), _ar("المختص")],
        [_ar(".................."), _ar(SUPERVISOR)],
        [_ar("التاريخ"), _ar(SUPERVISOR_TITLE)],
    ]
    ts = Table(sign, colWidths=[245, 245])
    ts.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), font_mgr.font_name),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, HexColor('#e0e0e0')),
        ('BACKGROUND', (0,0), (-1,0), HexColor('#e8f5e9')),
    ]))
    story.append(ts)

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


def make_excel(standard: dict, actual: dict, formula: dict = None) -> bytes:
    if not XLSX_OK: return b""
    wb = Workbook()
    ws = wb.active
    ws.title = "مقارنة"
    ws.sheet_view.rightToLeft = True
    hf = Font(name='Arial', size=12, bold=True, color='FFFFFF')
    hfill = PatternFill('solid', fgColor='1B5E20')
    ct = Alignment(horizontal='center', vertical='center')
    rt = Alignment(horizontal='right', vertical='center')
    thin = Side(border_style='thin', color='9E9E9E')
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    ws.merge_cells('A1:F1')
    ws['A1'] = APP_NAME
    ws['A1'].font = Font(name='Arial', size=14, bold=True, color='1B5E20')
    ws['A1'].alignment = ct
    ws.merge_cells('A2:F2')
    ws['A2'] = DUA_SHORT
    ws['A2'].font = Font(name='Arial', size=10, bold=True, color='C62828')
    ws['A2'].alignment = ct

    headers = ["العنصر", "المعيار", "المحسوب", "الفرق", "% الفرق", "التقييم"]
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=4, column=c, value=h)
        cell.font = hf; cell.fill = hfill
        cell.alignment = ct; cell.border = bd

    labels = {"CP":"بروتين خام","DP":"بروتين مهضوم","SE":"معادل النشاء",
              "NDF":"NDF","ADF":"ADF","EE":"دهن","ASH":"رماد","Ca":"Ca","P":"P"}
    row = 5
    for k, lbl in labels.items():
        sv = standard.get(k, 0); cv = actual.get(k, 0)
        diff = cv - sv
        pct = (diff / sv * 100) if sv else 0
        ev = evaluate_diff(pct)
        vals = [lbl, round(sv, 2), round(cv, 2), round(diff, 3),
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


# ═════════════════════════════════════════════════════════════════════════════
# 12. الرسوم البيانية
# ═════════════════════════════════════════════════════════════════════════════

def chart_bar(standard: dict, actual: dict):
    if not MPL_OK: return None
    try:
        keys = ["CP","DP","SE","NDF","ADF","EE","ASH"]
        keys = [k for k in keys if k in standard]
        if not keys: return None
        fig, ax = plt.subplots(figsize=(9, 4.5))
        x = np.arange(len(keys)); w = 0.35
        s = [standard[k] for k in keys]
        a = [actual.get(k, 0) for k in keys]
        ax.bar(x-w/2, s, w, label='المعيار', color='#1976d2',
               edgecolor='#0d47a1', linewidth=1.5)
        ax.bar(x+w/2, a, w, label='المحسوب', color='#43a047',
               edgecolor='#1b5e20', linewidth=1.5)
        for i, (sv, av) in enumerate(zip(s, a)):
            ax.text(i-w/2, sv, f'{sv:.1f}', ha='center', va='bottom',
                    fontsize=9, color='#0d47a1', fontweight='bold')
            ax.text(i+w/2, av, f'{av:.1f}', ha='center', va='bottom',
                    fontsize=9, color='#1b5e20', fontweight='bold')
        ax.set_xticks(x); ax.set_xticklabels(keys)
        ax.set_title('مقارنة العناصر', color='#1b5e20', fontweight='bold')
        ax.legend(); ax.grid(axis='y', alpha=0.3, linestyle='--')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception:
        return None


def chart_gauge(score: float):
    if not MPL_OK: return None
    try:
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect='equal'))
        colors = ['#c62828','#ef6c00','#f9a825','#7cb342','#43a047','#1b5e20']
        for i, c in enumerate(colors):
            t1 = 180 - (i * 30); t2 = 180 - ((i + 1) * 30)
            ax.add_patch(Wedge((0,0), 1, t2, t1, width=0.3,
                               facecolor=c, edgecolor='white', linewidth=2))
        ang = np.radians(180 - (score/100)*180)
        ax.plot([0, 0.85*np.cos(ang)], [0, 0.85*np.sin(ang)],
                color='#1a1a1a', linewidth=3, zorder=10)
        ax.add_patch(Circle((0,0), 0.08, color='#1a1a1a', zorder=11))
        ax.text(0, -0.25, f'{score:.0f}%', ha='center', fontsize=20,
                fontweight='bold', color='#1b5e20')
        ax.text(0, -0.5, 'التقييم', ha='center', fontsize=11, color='#666')
        ax.set_xlim(-1.2, 1.2); ax.set_ylim(-0.7, 1.2)
        ax.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception:
        return None


# ═════════════════════════════════════════════════════════════════════════════
# 13. أسعار السوق
# ═════════════════════════════════════════════════════════════════════════════

EXCHANGE_RATES = {
    "السودان":   {"rate": 600.0, "sym": "SDG"},
    "ليبيا":     {"rate": 4.80,  "sym": "LYD"},
    "مصر":       {"rate": 48.0,  "sym": "EGP"},
    "السعودية":  {"rate": 3.75,  "sym": "SAR"},
    "الإمارات":  {"rate": 3.67,  "sym": "AED"},
    "دولار عالمي": {"rate": 1.0, "sym": "USD"},
}


def market_prices(country: str) -> dict:
    base = {ing: 280.0 for ing in INGREDIENT_INDEX}
    base.update({
        "ذرة صفراء": 230, "شعير مطحون": 210, "سورجم (فتريتة)": 195,
        "قمح محلي": 240, "أمباز الفول السوداني": 460,
        "كسب فول صويا 44%": 440, "كسب فول صويا 48%": 480,
        "كسب عباد الشمس 36%": 310, "نخالة قمح (ردة)": 150,
        "البرسيم الجاف": 170, "مولاس قصب السكر": 120,
        "مسحوق أسماك 60%": 850, "مركزات دواجن": 650,
        "مركزات مواشي": 600, "الحجر الجيري": 40,
        "فوسفات ثنائي الكالسيوم": 280, "ملح الطعام": 30,
        "بيكربونات الصوديوم": 340, "مضاد سموم فطرية": 950,
        "بريمكس تسمين دواجن": 4800, "بريمكس مجترات": 4500,
        "ليسين نقي": 4200, "ميثيونين نقي": 5800,
        "زيت ذرة": 1500, "زيت فول الصويا": 1350,
        "زيت النخيل": 1100, "زيت عباد الشمس": 1300,
        "شحم حيواني Tallow": 900, "زيت السمك": 3800,
    })
    m = {"السودان": 1.15, "ليبيا": 1.10, "مصر": 1.04,
         "السعودية": 1.08, "الإمارات": 1.12}.get(country, 1.0)
    return {k: v * m for k, v in base.items()}


ANIMAL_IMAGES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "ماعز":  "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600",
    "خيول":  "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "إبل":   "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600",
    "سمان":  "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "عام":   "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600",
}


@st.cache_data(ttl=3600)
def load_b64_photo(paths):
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                pass
    return None


# ═════════════════════════════════════════════════════════════════════════════
# 14. الحالة الأولية
# ═════════════════════════════════════════════════════════════════════════════

DEFAULTS = {
    "approved": False,
    "user_role": None,
    "login_attempts": 0,
    "lockout_until": 0.0,
    "session_token": "",
    "login_time": 0.0,
    "active_formula": {},
    "active_stage_title": "إنتاج عام",
    "active_animal_img": ANIMAL_IMAGES["عام"],
    "computed_ton_cost": 280.0,
    "inventory": {},
    "shared_comments": f"• مرحباً بكم في {APP_NAME}\n• {DUA_SHORT}\n",
    "broiler_farms": {},
    "vacc_schedule": dict(VACC_SCHEDULE_DEFAULT),
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state["inventory"]:
    for ing in INGREDIENT_INDEX:
        st.session_state["inventory"][ing] = {"quantity": 25.0, "min": 5.0}


def is_owner() -> bool:
    return st.session_state.get("user_role") == "owner"

def is_staff() -> bool:
    return st.session_state.get("user_role") in ("owner", "specialist")


# ═════════════════════════════════════════════════════════════════════════════
# 15. CSS
# ═════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');
* { font-family:'Cairo','Amiri',sans-serif; color:#1a1a1a !important; }
html,body,[data-testid="stAppViewContainer"] {
    background-image:url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600");
    background-size:cover; background-position:center; background-attachment:fixed;
}
.stApp { background:transparent; }
.main-box {
    background-color:rgba(255,255,255,0.98); padding:30px; border-radius:15px;
    box-shadow:0 10px 30px rgba(0,0,0,0.18); margin-bottom:60px;
    backdrop-filter:blur(5px);
}
h1,h2,h3,h4,h5,p,span,li,div,label { color:#1a1a1a !important; }

@keyframes duaGlow {
    0%,100% { box-shadow:0 15px 40px rgba(0,0,0,.4), inset 0 0 30px rgba(212,175,55,.2); }
    50% { box-shadow:0 15px 40px rgba(0,0,0,.5), inset 0 0 40px rgba(212,175,55,.4),
          0 0 80px rgba(212,175,55,.5); }
}
.dua-main-box {
    background:linear-gradient(135deg,#0d3011 0%,#1b5e20 50%,#0d3011 100%);
    animation:duaGlow 4s ease-in-out infinite;
    padding:32px 28px; border-radius:22px; border:4px solid #d4af37;
    direction:rtl; text-align:center; margin:25px 0;
}
.dua-main-box * { color:white !important; }
.dua-main-box h3 { color:#d4af37 !important; font-size:1.9rem; font-weight:900; }
.dua-main-box .names {
    display:inline-block; background:rgba(212,175,55,.25);
    font-size:1.5rem; font-weight:900; color:#ffeb3b !important;
    margin:20px 0; padding:16px 30px; border:2px solid #d4af37;
    border-radius:15px; font-family:'Amiri',serif !important;
}
.dua-main-box p.quran {
    font-family:'Amiri',serif !important; font-size:1.15rem;
    color:#d4af37 !important; margin-top:18px; padding:16px 20px;
    background:rgba(0,0,0,.25); border-radius:12px;
    border-right:5px solid #d4af37; border-left:5px solid #d4af37;
}

.section-title {
    color:#1b5e20 !important; border-right:6px solid #2e7d32;
    padding:12px 18px; text-align:right; font-size:1.5rem; font-weight:bold;
    margin-top:30px; margin-bottom:20px;
    background:linear-gradient(to left, rgba(46,125,50,0.15), transparent);
    border-radius:10px;
}
.formula-item {
    background:linear-gradient(135deg,#fff 0%,#e8f5e9 100%);
    padding:14px 20px; border-radius:12px; margin-bottom:8px;
    font-weight:bold; color:#1b5e20 !important;
    border-right:5px solid #2e7d32; text-align:right;
    box-shadow:0 4px 15px rgba(0,0,0,.08);
}
.oil-item {
    background:linear-gradient(135deg,#fff8e1,#ffe0b2);
    padding:12px 18px; border-radius:12px; margin-bottom:8px;
    font-weight:bold; color:#bf360c !important;
    border-right:5px solid #e65100; text-align:right;
}
.price-card {
    background:linear-gradient(135deg,#f1f8e9,#e8f5e9);
    padding:20px; border-radius:12px; border-right:5px solid #2e7d32;
    margin-bottom:20px; direction:rtl; text-align:right;
    box-shadow:0 4px 15px rgba(0,0,0,.1);
}
.oil-info-card {
    background:linear-gradient(135deg,#fff3e0,#ffe0b2);
    padding:18px; border-radius:12px; border-right:5px solid #e65100;
    margin-bottom:18px; direction:rtl; text-align:right;
}
.visitor-dua-banner {
    background:linear-gradient(135deg,#fff8e1,#ffecb3);
    padding:18px 25px; border-radius:16px; border:3px solid #d4af37;
    margin:20px 0; direction:rtl; text-align:center;
    box-shadow:0 6px 25px rgba(0,0,0,.15);
}
.visitor-dua-banner b { color:#c62828 !important; font-family:'Amiri',serif; }

.dua-fixed-banner {
    position:fixed; bottom:0; left:0; right:0;
    background:linear-gradient(90deg,#0d3011,#1b5e20,#2e7d32,#1b5e20,#0d3011);
    background-size:200% 100%;
    padding:11px 20px; z-index:9998; text-align:center;
    border-top:3px solid #d4af37; font-family:'Amiri',serif;
    font-weight:bold; font-size:1.05rem;
    box-shadow:0 -4px 25px rgba(0,0,0,.4);
}
.dua-fixed-banner * { color:#ffeb3b !important; font-family:'Amiri',serif; }

.mini-signature {
    position:fixed; left:20px; bottom:65px;
    background:linear-gradient(135deg,#1b5e20,#2e7d32);
    color:white !important; padding:9px 22px; font-size:0.88rem;
    border-radius:25px; z-index:9997; direction:rtl;
    border:2px solid #d4af37; font-weight:bold;
}
.mini-signature * { color:white !important; }

.metric-card {
    background:linear-gradient(135deg,#e8f5e9,#c8e6c9);
    padding:18px; border-radius:12px; border-right:4px solid #1b5e20;
    text-align:center; margin-bottom:12px;
}
.stButton > button {
    color:#1a1a1a !important; background-color:#e8f5e9 !important;
    border:1px solid #2e7d32 !important; font-weight:bold !important;
}
.stButton > button:hover { background-color:#c8e6c9 !important; }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# 16. بوابة الدخول الآمنة
# ═════════════════════════════════════════════════════════════════════════════

if not st.session_state["approved"]:
    allowed, remaining = check_rate_limit()
    if not allowed:
        st.error(f"🔒 تم القفل — أعد المحاولة بعد {remaining} ثانية")
        st.stop()

    st.markdown('<div class="main-box" style="max-width:820px;margin:30px auto;direction:rtl;">',
                unsafe_allow_html=True)

    st.markdown(f"""
    <div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <div class="names">🕊️ {DUA_SHORT} 🕊️</div>
        <p class="quran">{DUA_QURAN}</p>
        <p class="quran" style="margin-top:10px;">{DUA_VERSE}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-top:2px solid #d4af37;margin:25px 0;'>",
                unsafe_allow_html=True)

    photo_b64 = load_b64_photo(tuple(PHOTO_OPTIONS))
    c1, c2 = st.columns([0.25, 0.75])
    with c1:
        src = (f"data:image/jpeg;base64,{photo_b64}" if photo_b64
               else ANIMAL_IMAGES["عام"])
        st.markdown(f'<img src="{src}" style="width:150px;height:150px;'
                    f'border-radius:50%;object-fit:cover;border:4px solid #d4af37;">',
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f"<h2 style='color:#2e7d32;text-align:right;'>🌾 {APP_NAME}</h2>",
                    unsafe_allow_html=True)
        st.markdown(f"<p style='color:#1565c0;text-align:right;font-size:1.1rem;'>"
                    f"{APP_TAGLINE}</p>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#c62828;text-align:right;'>"
                    f"{SUPERVISOR} — {SUPERVISOR_TITLE}</h4>",
                    unsafe_allow_html=True)

    st.markdown("<h3 style='text-align:center;color:#1b5e20;'>🔐 بوابة الدخول</h3>",
                unsafe_allow_html=True)

    code_in = st.text_input("🔑 كود الدخول:", type="password",
                            key=f"login_{st.session_state['login_attempts']}")
    if st.button("🔓 تسجيل الدخول", type="primary", use_container_width=True):
        role = get_role_from_code(code_in)
        if role:
            reset_attempts()
            st.session_state.update({
                "approved": True,
                "user_role": role,
                "session_token": issue_session_token(role),
                "login_time": time.time(),
            })
            st.rerun()
        else:
            register_failed_attempt()
            left = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
            st.error(f"❌ كود غير صحيح — متبقي {left} محاولات")

    st.caption("💡 الأكواد: مالك / مختص / مربي — تواصل مع الإدارة للحصول على كودك")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# التحقق من رمز الجلسة
if not verify_session_token(st.session_state.get("session_token", "")):
    st.warning("⚠️ انتهت الجلسة — أعد الدخول")
    st.session_state["approved"] = False
    st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# 17. الواجهة الرئيسية
# ═════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# شريط الحالة
top_c1, top_c2 = st.columns([0.75, 0.25])
with top_c2:
    role_txt = {"owner":"المالك 👑","specialist":"المختص 👨‍🔬","breeder":"المربي 🌾"}
    st.markdown(f"<div style='text-align:left;padding:10px;background:#f5f5f5;"
                f"border-radius:10px;'>الحساب: <b>{role_txt.get(st.session_state['user_role'],'')}</b></div>",
                unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k not in ("inventory",):
                del st.session_state[k]
        st.rerun()

photo_b64 = load_b64_photo(tuple(PHOTO_OPTIONS))
c3, c4 = st.columns([0.25, 0.75])
with c3:
    src = (f"data:image/jpeg;base64,{photo_b64}" if photo_b64
           else ANIMAL_IMAGES["عام"])
    st.markdown(f'<img src="{src}" style="width:150px;height:150px;'
                f'border-radius:50%;object-fit:cover;border:4px solid #d4af37;'
                f'display:block;margin:0 auto;">', unsafe_allow_html=True)
with c4:
    st.markdown(f"<h1 style='color:#0d3011;text-align:right;font-size:2.2rem;"
                f"font-weight:900;'>🌾 {APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#1565c0;text-align:right;font-size:1.2rem;"
                f"font-weight:600;'>{APP_TAGLINE} — NRC / INRA / FAO / Ross 308</p>",
                unsafe_allow_html=True)
    st.markdown(f"<div style='background:linear-gradient(135deg,#fff8e1,#ffe082);"
                f"padding:12px 20px;border-radius:12px;"
                f"border-left:6px solid #c62828;border-right:6px solid #c62828;'>"
                f"<h3 style='color:#b71c1c;margin:0;font-weight:900;'>"
                f"👨‍🔬 {SUPERVISOR}</h3>"
                f"<p style='color:#0d47a1;margin:5px 0 0 0;font-weight:700;'>"
                f"✨ {SUPERVISOR_TITLE}</p></div>", unsafe_allow_html=True)

st.markdown(f'<div class="visitor-dua-banner">🕌 <b>إلى زوارنا الكرام:</b> '
            f'هذه المنصة صدقة جارية عن <b>والدي إسماعيل تاور</b> و<b>أختي ابتسام</b>. '
            f'نسألكم الدعاء لهما 🤲</div>', unsafe_allow_html=True)

st.markdown("<hr style='border-top:3px solid #2e7d32;'>", unsafe_allow_html=True)


# ─── التبويبات ──────────────────────────────────────────────────────────
if is_owner():
    tabs_titles = [
        "🔬 تركيب الأعلاف", "🌰 مكتبة الزيوت", "🍼 بدائل الحليب",
        "📷 المختبر الذكي", "📊 بورصة الأسعار", "🏭 المستودعات",
        "🧾 الفواتير", "🐔 مزارع الدجاج", "💬 التعليقات",
        "📚 المراجع", "💡 المساعدة", "📖 الدليل",
    ]
elif st.session_state["user_role"] == "specialist":
    tabs_titles = [
        "🔬 تركيب الأعلاف", "🌰 مكتبة الزيوت", "🍼 بدائل الحليب",
        "📷 المختبر الذكي", "📊 بورصة الأسعار", "🏭 المستودعات",
        "🧾 الفواتير", "💬 التعليقات", "📚 المراجع", "💡 المساعدة", "📖 الدليل",
    ]
else:
    tabs_titles = [
        "🔬 تركيب الأعلاف", "🌰 مكتبة الزيوت", "🍼 بدائل الحليب",
        "📷 المختبر الذكي", "📚 المراجع", "💡 المساعدة", "📖 الدليل",
    ]

tabs = st.tabs(tabs_titles)


# ═════════════════════════════════════════════════════════════════════════════
# تبويب 0: تركيب الأعلاف
# ═════════════════════════════════════════════════════════════════════════════

with tabs[0]:
    st.markdown('<div class="section-title">🌍 الموقع الجغرافي والعملة</div>',
                unsafe_allow_html=True)
    cc1, cc2 = st.columns(2)
    with cc1:
        country = st.selectbox("الدولة:", list(EXCHANGE_RATES.keys()))
    with cc2:
        city = st.text_input("المدينة:", "الخرطوم")
    rate = EXCHANGE_RATES[country]
    local_rate, local_sym = rate["rate"], rate["sym"]
    prices = market_prices(country)

    st.markdown('<div class="section-title">🐾 اختر الحيوان والحالة الفسيولوجية</div>',
                unsafe_allow_html=True)

    # بطاقات الحيوانات
    a_tabs = st.tabs(["🐄 أبقار","🐏 أغنام","🐐 ماعز","🐪 إبل","🐎 خيول","🐔 دواجن","🦆 سمان","🐟 أسماك"])

    animal_choice = None
    requirement: Optional[Requirement] = None
    img_key = "عام"

    with a_tabs[0]:
        st.markdown("### 🐄 أبقار — NRC 2001")
        ctype = st.selectbox("الحالة:", ["حليب_عالي","حليب_متوسط","تسمين_مكثف","تسمين_عادي","حمل_أخير","صيانة"],
            format_func=lambda x: {"حليب_عالي":"حلابة عالية","حليب_متوسط":"حلابة متوسطة",
                "تسمين_مكثف":"تسمين مكثف","تسمين_عادي":"تسمين عادي",
                "حمل_أخير":"حمل آخر","صيانة":"صيانة"}[x])
        milk = 20.0
        if "حليب" in ctype:
            milk = st.number_input("إنتاج الحليب (كجم):", 5.0, 60.0, 20.0, 1.0)
        req = get_cattle_req(ctype, milk)
        p1,p2,p3,p4 = st.columns(4)
        p1.metric("DP", f"{req.DP}%"); p2.metric("CP", f"{req.CP}%")
        p3.metric("SE", f"{req.SE}"); p4.metric("NDF", f"{req.NDF}%")
        st.caption(f"📝 {req.note}")
        if st.checkbox("✅ اعتماد أبقار", key="u_cattle"):
            animal_choice = "أبقار"; requirement = req; img_key = "أبقار"

    with a_tabs[1]:
        st.markdown("### 🐏 أغنام — NRC 2007")
        g = st.radio("الجنس:", ["ذكر","أنثى"], horizontal=True, key="sh_g")
        if g == "ذكر":
            stype = st.selectbox("الحالة:", ["تسمين_مكثف","تسمين_عادي","حملان_تيد"])
        else:
            stype = st.selectbox("الحالة:", ["مرضعات","حامل_أخير","حامل_متوسط","صيانة"])
        litter = 1
        if stype == "مرضعات":
            litter = st.number_input("عدد المواليد:", 1, 3, 1)
        req = get_sheep_req(stype, g=="ذكر", litter)
        p1,p2,p3 = st.columns(3)
        p1.metric("DP", f"{req.DP}%"); p2.metric("CP", f"{req.CP}%"); p3.metric("SE", f"{req.SE}")
        st.caption(f"📝 {req.note}")
        if st.checkbox("✅ اعتماد أغنام", key="u_sheep"):
            animal_choice = "أغنام"; requirement = req; img_key = "أغنام"

    with a_tabs[2]:
        st.markdown("### 🐐 ماعز — NRC 2007")
        g = st.radio("الجنس:", ["ذكر","أنثى"], horizontal=True, key="gt_g")
        if g == "ذكر":
            gtype = st.selectbox("الحالة:", ["تسمين_جديان","تيوس"])
        else:
            gtype = st.selectbox("الحالة:", ["حلابة_عالي","حلابة_متوسط","حامل_أخير","صيانة"])
        milk_g = 2.0
        if "حلابة" in gtype:
            milk_g = st.number_input("حليب (كجم):", 0.5, 8.0, 2.0, 0.25)
        req = get_goat_req(gtype, g=="ذكر", milk_g)
        p1,p2,p3 = st.columns(3)
        p1.metric("DP", f"{req.DP}%"); p2.metric("CP", f"{req.CP}%"); p3.metric("SE", f"{req.SE}")
        st.caption(f"📝 {req.note}")
        if st.checkbox("✅ اعتماد ماعز", key="u_goat"):
            animal_choice = "ماعز"; requirement = req; img_key = "ماعز"

    with a_tabs[3]:
        st.markdown("### 🐪 إبل — FAO 2010")
        ctype = st.selectbox("الحالة:", ["نمو","تسمين","حليب","سباق","صيانة"])
        wt = st.number_input("الوزن (كجم):", 100.0, 800.0, 400.0, 25.0)
        milk_c = 5.0
        if ctype == "حليب":
            milk_c = st.number_input("حليب (لتر):", 2.0, 20.0, 5.0, 0.5)
        req = get_camel_req(ctype, wt, milk_c)
        p1,p2,p3 = st.columns(3)
        p1.metric("DP", f"{req.DP}%"); p2.metric("CP", f"{req.CP}%"); p3.metric("SE", f"{req.SE}")
        st.caption(f"📝 {req.note}")
        if st.checkbox("✅ اعتماد إبل", key="u_camel"):
            animal_choice = "إبل"; requirement = req; img_key = "إبل"

    with a_tabs[4]:
        st.markdown("### 🐎 خيول — NRC 2007")
        htype = st.selectbox("الحالة:", ["رياضة_مكثف","رياضة_عادي","نمو_أمهار","مرضعات","صيانة"])
        req = get_horse_req(htype)
        p1,p2,p3 = st.columns(3)
        p1.metric("DP", f"{req.DP}%"); p2.metric("CP", f"{req.CP}%"); p3.metric("SE", f"{req.SE}")
        st.caption(f"📝 {req.note}")
        if st.checkbox("✅ اعتماد خيول", key="u_horse"):
            animal_choice = "خيول"; requirement = req; img_key = "خيول"

    with a_tabs[5]:
        st.markdown("### 🐔 دواجن — NRC + Ross 308")
        strain = st.radio("السلالة:", ["لاحم","بياض"], horizontal=True)
        age = st.number_input("العمر (أسبوع):", 1, 20, 1)
        req = get_poultry_req(strain, age)
        p1,p2,p3,p4 = st.columns(4)
        p1.metric("DP", f"{req.DP}%"); p2.metric("CP", f"{req.CP}%")
        p3.metric("SE", f"{req.SE}"); p4.metric("Ca", f"{req.Ca}%")
        st.caption(f"📝 {req.note}")
        if st.checkbox("✅ اعتماد دواجن", key="u_poultry"):
            animal_choice = "دواجن"; requirement = req; img_key = "دواجن"

    with a_tabs[6]:
        st.markdown("### 🦆 سمان")
        strain = st.radio("النوع:", ["تسمين","بياض"], horizontal=True)
        age = st.number_input("العمر (أسبوع):", 1, 8, 1)
        req = get_quail_req(strain, age)
        p1,p2,p3 = st.columns(3)
        p1.metric("DP", f"{req.DP}%"); p2.metric("CP", f"{req.CP}%"); p3.metric("SE", f"{req.SE}")
        st.caption(f"📝 {req.note}")
        if st.checkbox("✅ اعتماد سمان", key="u_quail"):
            animal_choice = "سمان"; requirement = req; img_key = "سمان"

    with a_tabs[7]:
        st.markdown("### 🐟 أسماك")
        sp = st.selectbox("النوع:", ["البلطي النيلي","القرموط الأفريقي","الكارب"])
        stage = st.selectbox("المرحلة:", ["بادئ زريعة","نمو","تسمين"])
        req = get_fish_req(sp, stage)
        p1,p2,p3 = st.columns(3)
        p1.metric("DP", f"{req.DP}%"); p2.metric("CP", f"{req.CP}%"); p3.metric("SE", f"{req.SE}")
        st.caption(f"📝 {req.note}")
        if st.checkbox("✅ اعتماد أسماك", key="u_fish"):
            animal_choice = "أسماك"; requirement = req; img_key = "أسماك"

    if not animal_choice or not requirement:
        st.warning("⚠️ اختر حيواناً وفعّل خيار ✅ الاعتماد للمتابعة")
        st.stop()

    st.markdown(f'<div class="section-title">🎯 المختار: {animal_choice} — {requirement.name_ar}</div>',
                unsafe_allow_html=True)

    # أساس الحساب
    basis_choice = st.radio("أساس الحساب:", ["DP (البروتين المهضوم) — الأدق",
                                              "CP (البروتين الخام) — الأسهل"], horizontal=True)
    use_dp = "DP" in basis_choice

    # معيار الزيوت
    oil_info = get_oil_std(requirement.oil_key)
    st.markdown(f"""
    <div class="oil-info-card">
    <b>🌰 معيار الزيوت لهذا الحيوان:</b><br>
    ▪️ الحد الأقصى: <b>{oil_info['max']}%</b> | المثالي: <b>{oil_info['opt']}%</b><br>
    ▪️ المرجع: <b>{oil_info['src']}</b><br>
    <small>💡 كل 1% زيت ≈ 90 kcal/kg علف</small>
    </div>
    """, unsafe_allow_html=True)

    requester = st.text_input("👤 اسم طالب العلفة (للتقرير):", "",
                              placeholder="مثال: مزرعة الأمل — أحمد محمد")

    # اختيار المكونات
    st.markdown('<div class="section-title">🌾 اختيار المكونات والأسعار</div>',
                unsafe_allow_html=True)
    selected = []
    selected_prices = {}

    for cat_name, items in FEEDS.items():
        expanded = any(x in cat_name for x in ["الحبوب", "الأكساب", "الزيوت"])
        with st.expander(f"📁 {cat_name}", expanded=expanded):
            cols = st.columns(3)
            for i, (ing, data) in enumerate(items.items()):
                with cols[i % 3]:
                    default_ck = ing in ["ملح الطعام","الحجر الجيري",
                                          "فوسفات ثنائي الكالسيوم","مضاد سموم فطرية"]
                    if ing in OIL_NAMES:
                        st.markdown(f"**{ing}**")
                        st.caption(f"SE={data['SE']:.0f} | {data.get('source','NRC')}")
                    ck = st.checkbox(ing, value=default_ck, key=f"ck_{animal_choice}_{ing}")
                    price = prices.get(ing, 300.0)
                    if is_owner():
                        price = st.number_input("$", min_value=5.0, value=float(price),
                                                key=f"p_{ing}", label_visibility="collapsed")
                    else:
                        st.caption(f"💰 ${price:.0f}/طن")
                    if ck:
                        selected.append(ing)
                        selected_prices[ing] = price

    if st.button("🚀 تشغيل المحرك الذكي — مطابقة دقيقة", type="primary",
                 use_container_width=True):
        if len(selected) < 3:
            st.error("⚠️ اختر 3 مكونات على الأقل")
        else:
            # إضافة الأملاح تلقائياً
            for s, p in auto_salts(animal_choice, requirement).items():
                if s not in selected:
                    selected.append(s)
                    selected_prices[s] = prices.get(s, 300.0)

            with st.spinner(f"⏳ جاري التركيب على أساس {'DP' if use_dp else 'CP'}..."):
                result = auto_formulate(selected, selected_prices, requirement,
                                        requirement.oil_key, tol=0.3, max_iter=50)

            if not result["success"]:
                st.error(f"❌ {result['message']}")
                st.stop()

            formula = result["formula"]
            actual = result["actual"]
            targets = result["targets"]

            # جدول المقارنة
            labels = {"CP":"بروتين خام","DP":"بروتين مهضوم","SE":"معادل النشاء",
                      "NDF":"NDF","ADF":"ADF","EE":"دهن","ASH":"رماد",
                      "Ca":"كالسيوم","P":"فسفور"}
            rows = []
            for k, lbl in labels.items():
                sv = targets.get(k, 0); cv = actual.get(k, 0)
                diff = cv - sv
                pct = (diff / sv * 100) if sv else 0
                ev = evaluate_diff(pct)
                rows.append({"العنصر": lbl, "المعيار": f"{sv:.2f}",
                             "المحسوب": f"{cv:.2f}", "الفرق": f"{diff:+.3f}",
                             "% الفرق": f"{pct:+.2f}%", "التقييم": ev["label"],
                             "score": ev["score"]})

            overall = overall_rating(rows)

            st.success(f"✅ تم التركيب — {result['iterations']} تكرار | "
                       f"RMSE: {result['overall_rmse']:.3f}%")
            st.info(f"🏆 التقييم العام: **{overall['label']}** ({overall['score']:.0f}%)")

            # مؤشرات الدقة
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("خطأ DP", f"{result['rmse_dp']:.3f}%")
            m2.metric("خطأ SE", f"{result['rmse_se']:.3f}")
            m3.metric("خطأ NDF", f"{result['rmse_ndf']:.3f}%")
            m4.metric("خطأ Ca", f"{result['rmse_ca']:.3f}%")

            st.markdown("### 📊 جدول المقارنة الشامل")
            df_show = pd.DataFrame([{k: v for k, v in r.items() if k != "score"}
                                     for r in rows])
            st.dataframe(df_show, use_container_width=True, hide_index=True)

            # الزيوت
            if result["total_oil"] > 0:
                oil_std = result["oil_std"]
                total_oil = result["total_oil"]
                if total_oil > oil_std["max"]:
                    st.error(f"⚠️ الزيوت {total_oil:.2f}% > الحد {oil_std['max']}%")
                elif total_oil > oil_std["opt"] * 1.2:
                    st.warning(f"⚡ الزيوت {total_oil:.2f}% — المثالي {oil_std['opt']}%")
                else:
                    st.success(f"✅ الزيوت {total_oil:.2f}% — مطابق")

                for ing, pct in formula.items():
                    if ing in OIL_NAMES:
                        st.markdown(f'<div class="oil-item">🌰 <b>{ing}:</b> '
                                    f'{pct:.2f}% | ≈ {pct*90:.0f} kcal/kg</div>',
                                    unsafe_allow_html=True)

            # المكونات
            st.markdown("#### 🌾 المكونات:")
            for ing, pct in formula.items():
                st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> '
                            f'{pct:.2f}% ({pct*10:.1f} كجم/طن)</div>',
                            unsafe_allow_html=True)

            ton_cost = result["cost"]
            st.session_state["computed_ton_cost"] = ton_cost
            st.session_state["active_formula"] = formula
            st.session_state["active_stage_title"] = f"{animal_choice} — {requirement.name_ar}"

            st.metric("💰 التكلفة للطن:",
                      f"${ton_cost:.2f} ({ton_cost*local_rate:,.0f} {local_sym})")

            # التحميل
            dl1, dl2 = st.columns(2)
            with dl1:
                try:
                    pdf = make_pdf_report(
                        formula, requirement, animal_choice, requirement.name_ar,
                        ton_cost, city, ton_cost*local_rate, local_sym,
                        requester, "DP" if use_dp else "CP",
                        requirement.oil_key, True)
                    st.download_button("📥 تحميل PDF", pdf,
                        file_name=f"Tawor_{animal_choice}_{datetime.now():%Y%m%d_%H%M}.pdf",
                        mime="application/pdf", use_container_width=True)
                except Exception as e:
                    st.error(f"⚠️ PDF: {e}")
            with dl2:
                try:
                    xl = make_excel(targets, actual, formula)
                    if xl:
                        st.download_button("📊 تحميل Excel", xl,
                            file_name=f"Tawor_{animal_choice}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True)
                except Exception as e:
                    st.error(f"⚠️ Excel: {e}")

            # الرسوم
            if PLOTLY_OK and len(formula) > 1:
                fig = px.pie(values=list(formula.values()),
                             names=list(formula.keys()),
                             title=f"توزيع المكونات — {animal_choice}",
                             color_discrete_sequence=px.colors.sequential.Greens)
                st.plotly_chart(fig, use_container_width=True)

            bar = chart_bar(targets, actual)
            if bar:
                st.image(bar, caption="مقارنة العناصر الغذائية")
            gauge = chart_gauge(overall["score"])
            if gauge:
                st.image(gauge, width=250)


# ═════════════════════════════════════════════════════════════════════════════
# تبويب 1: مكتبة الزيوت
# ═════════════════════════════════════════════════════════════════════════════

with tabs[1]:
    st.markdown('<div class="section-title">🌰 مكتبة الزيوت النباتية والحيوانية</div>',
                unsafe_allow_html=True)
    st.markdown("جميع الزيوت بمعايير NRC 2012, NRC 2007, INRA 2018, Ross 308, FAO 2010")

    rows = []
    for k, v in MAX_OIL_STD.items():
        rows.append({"الحيوان": k, "الحد الأقصى %": v["max"],
                     "المثالي %": v["opt"], "المرجع": v["src"]})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("### 🌰 الزيوت المتوفرة")
    oils = FEEDS["🌰 الزيوت النباتية والحيوانية"]
    for ing, d in oils.items():
        with st.expander(f"🌰 {ing}"):
            c1, c2, c3 = st.columns(3)
            c1.metric("SE", f"{d['SE']:.0f}")
            c2.metric("طاقة تقديرية", f"{d['SE']*41:.0f} kcal/kg")
            c3.metric("مرجع", d.get("source", "NRC"))
            st.caption(f"🐔 أقصى للدواجن: {d.get('max_poultry','-')}% | "
                       f"🐄 أقصى للمجترات: {d.get('max_ruminant','-')}%")


# ═════════════════════════════════════════════════════════════════════════════
# تبويب 2: بدائل الحليب
# ═════════════════════════════════════════════════════════════════════════════

with tabs[2]:
    st.markdown('<div class="section-title">🍼 مختبر بدائل الحليب</div>',
                unsafe_allow_html=True)
    mr1, mr2 = st.columns(2)
    with mr1:
        mr_animal = st.selectbox("الحيوان:", list(MILK_REPLACER_STD.keys()))
        mr_vol = st.number_input("الكمية (كجم):", 1.0, 10000.0, 100.0, 10.0)
    with mr2:
        std = MILK_REPLACER_STD[mr_animal]
        st.markdown(f"""
        <div class="price-card">
        <b>📊 المعيار:</b><br>
        ▪️ بروتين: <b>{std['CP']}%</b> | دهن: <b>{std['Fat']}%</b><br>
        ▪️ لاكتوز: <b>{std['Lactose']}%</b><br>
        <small>{std['notes']}</small>
        </div>
        """, unsafe_allow_html=True)

    mr_sel = []
    cols = st.columns(3)
    for i, (name, d) in enumerate(MILK_REPLACER_ING.items()):
        with cols[i % 3]:
            default = name in ["حليب مجفف منزوع الدسم","حليب مجفف كامل الدسم",
                                "شرش حليب مجفف","زيت جوز الهند","زيت النخيل",
                                "بريمكس فيتامينات","كالسيوم كربونات","فوسفات ثنائي الكالسيوم"]
            if st.checkbox(f"{name} (${d['price']})", value=default, key=f"mr_{name}"):
                mr_sel.append(name)

    if st.button("🧪 تشغيل التركيب", type="primary", use_container_width=True):
        if len(mr_sel) < 3:
            st.warning("اختر 3 مكونات على الأقل")
        else:
            r = formulate_milk_replacer(mr_animal, mr_vol, mr_sel)
            if r["success"]:
                st.success(f"✅ تم التركيب — التكلفة ${r['cost_kg']:.3f}/كجم")
                for ing, pct in r["formula"].items():
                    kg = pct * mr_vol / 100
                    st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> '
                                f'{pct:.2f}% ({kg:.2f} كجم)</div>',
                                unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                c1.metric("CP الفعلي", f"{r['actual']['CP']:.2f}%")
                c2.metric("Fat الفعلي", f"{r['actual']['Fat']:.2f}%")
                c3.metric("Lactose", f"{r['actual']['Lactose']:.2f}%")
            else:
                st.error(r["message"])


# ═════════════════════════════════════════════════════════════════════════════
# تبويب 3: المختبر الذكي OCR
# ═════════════════════════════════════════════════════════════════════════════

with tabs[3]:
    st.markdown('<div class="section-title">📷 المختبر الذكي (OCR)</div>',
                unsafe_allow_html=True)
    if not OCR_OK:
        st.error("⚠️ pytesseract غير مثبتة")
        st.code("pip install pytesseract opencv-python-headless", language="bash")
    else:
        uploaded = st.file_uploader("📤 ارفع صورة:", type=["jpg","jpeg","png"])
        if uploaded and st.button("🔍 تحليل", type="primary"):
            with st.spinner("جاري التحليل..."):
                r = extract_ingredients(uploaded.read())
            if r["success"]:
                st.success(f"✅ تم استخراج {r['count']} مادة")
                if r["ingredients"]:
                    st.dataframe(pd.DataFrame([
                        {"المادة": k, "النسبة": f"{v:.2f}%"}
                        for k, v in r["ingredients"].items()
                    ]), use_container_width=True, hide_index=True)
                    nutrients = compute_nutrients(r["ingredients"])
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("CP", f"{nutrients['CP']:.2f}%")
                    c2.metric("DP", f"{nutrients['DP']:.2f}%")
                    c3.metric("SE", f"{nutrients['SE']:.2f}")
                    c4.metric("NDF", f"{nutrients['NDF']:.2f}%")
                with st.expander("📝 النص الخام"):
                    st.text(r.get("raw_text", ""))
            else:
                st.error(r["message"])


# ═════════════════════════════════════════════════════════════════════════════
# تبويبات إضافية (للمالك / المختص فقط)
# ═════════════════════════════════════════════════════════════════════════════

if is_staff():
    with tabs[4]:
        st.markdown('<div class="section-title">📊 بورصة الأسعار</div>',
                    unsafe_allow_html=True)
        country_m = st.selectbox("الدولة:", list(EXCHANGE_RATES.keys()), key="brs_c")
        prices_m = market_prices(country_m)
        df_p = pd.DataFrame([
            {"المادة": k, "السعر $/طن": f"${v:.0f}"}
            for k, v in sorted(prices_m.items())
        ])
        st.dataframe(df_p, use_container_width=True, hide_index=True)

    with tabs[5]:
        st.markdown('<div class="section-title">🏭 المستودعات</div>',
                    unsafe_allow_html=True)
        inv = st.session_state["inventory"]
        low = sum(1 for v in inv.values() if v["quantity"] < v["min"])
        out = sum(1 for v in inv.values() if v["quantity"] <= 0)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("إجمالي", len(inv))
        c2.metric("منخفضة", low)
        c3.metric("نفذت", out)
        c4.metric("آمنة", len(inv) - low - out)
        cols = st.columns(3)
        for i, (name, data) in enumerate(list(inv.items())[:60]):
            with cols[i % 3]:
                q = data["quantity"]
                badge = "🔴" if q <= 0 else ("🟡" if q < data["min"] else "🟢")
                st.markdown(f"{badge} **{name}**: {q:.1f} طن")
                if is_owner():
                    new_q = st.number_input("تحديث:", 0.0, 1000.0,
                        value=float(q), key=f"inv_{name}",
                        label_visibility="collapsed")
                    inv[name]["quantity"] = new_q

    with tabs[6]:
        st.markdown('<div class="section-title">🧾 الفواتير</div>',
                    unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        with f1: client = st.text_input("العميل:", "مزرعة الأمل")
        with f2: tons = st.number_input("الكمية (طن):", 0.1, 1000.0, 2.0, 0.5)
        with f3: profit = st.number_input("هامش الربح $/طن:", 0.0, 1000.0, 50.0)
        sell = st.session_state["computed_ton_cost"] + profit
        total = sell * tons
        st.markdown(f"""
        <div class="price-card">
        <h4>🧾 فاتورة</h4>
        <p><b>العميل:</b> {client}</p>
        <p><b>الكمية:</b> {tons} طن</p>
        <p><b>سعر الطن:</b> ${sell:.2f}</p>
        <p style="font-size:1.3rem;color:#1b5e20;"><b>الإجمالي:</b> ${total:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

if is_owner():
    with tabs[7]:
        st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج اللاحم</div>',
                    unsafe_allow_html=True)
        st.markdown("### ➕ إضافة مزرعة جديدة")
        nf1, nf2, nf3 = st.columns(3)
        with nf1: farm_name = st.text_input("اسم المزرعة:", key="nf_name")
        with nf2: farm_owner = st.text_input("المالك:", key="nf_owner")
        with nf3: farm_phone = st.text_input("واتساب:", WHATSAPP_NUMBER, key="nf_phone")
        if st.button("💾 إضافة مزرعة") and farm_name:
            st.session_state["broiler_farms"][farm_name] = {
                "owner": farm_owner, "phone": farm_phone,
                "data": {"age": 1, "birds": 1000, "weight": 0.045,
                         "feed": 0.0, "dead": 0, "temp": 33.0, "hum": 65.0},
            }
            st.success(f"✅ تمت إضافة {farm_name}")
            st.rerun()

        farms = list(st.session_state["broiler_farms"].keys())
        if farms:
            sel_farm = st.selectbox("اختر مزرعة:", farms)
            if sel_farm:
                d = st.session_state["broiler_farms"][sel_farm]["data"]
                b1, b2 = st.columns(2)
                with b1:
                    d["age"] = st.number_input("العمر (يوم):", 1, 60, d["age"])
                    d["birds"] = st.number_input("الطيور:", 1, value=d["birds"])
                    d["weight"] = st.number_input("الوزن (كجم):", 0.0, 10.0,
                        float(d["weight"]), 0.01)
                    d["feed"] = st.number_input("العلف (كجم):", 0.0,
                        float(d["feed"]), 100.0)
                with b2:
                    d["dead"] = st.number_input("النافق:", 0, value=d["dead"])
                    d["temp"] = st.number_input("الحرارة:", 10.0, 45.0, float(d["temp"]))
                    d["hum"] = st.number_input("الرطوبة:", 20.0, 90.0, float(d["hum"]))

                alive = d["birds"] - d["dead"]
                gain = alive * (d["weight"] - 0.045)
                adg = calc_adg(d["weight"]*1000, 45, d["age"])
                fcr = calc_fcr(d["feed"], gain) if gain > 0 else 0
                liv = calc_livability(d["birds"], d["dead"])
                epef = calc_epef(liv, d["weight"], d["age"], fcr)

                k1, k2, k3, k4 = st.columns(4)
                k1.metric("ADG (جم)", f"{adg:.1f}")
                k2.metric("FCR", f"{fcr:.2f}")
                k3.metric("الحيوية %", f"{liv:.1f}%")
                k4.metric("EPEF", f"{epef:.0f}")

                st.dataframe(temp_humidity_table(), use_container_width=True, hide_index=True)

        with st.expander("💊 بروتوكول التحصينات القياسي"):
            st.json(st.session_state["vacc_schedule"])

    with tabs[8]:
        st.markdown('<div class="section-title">💬 التعليقات الفنية</div>',
                    unsafe_allow_html=True)
        st.text_area("الحالية:", value=st.session_state["shared_comments"],
                     height=200, disabled=True)
        nc = st.text_area("جديد:")
        if st.button("➕ نشر") and nc:
            st.session_state["shared_comments"] += (
                f"\n• [{datetime.now():%Y-%m-%d %H:%M}]: {nc}")
            st.rerun()

# المراجع + المساعدة + الدليل
ref_idx = tabs_titles.index("📚 المراجع") if "📚 المراجع" in tabs_titles else -1
if ref_idx >= 0:
    with tabs[ref_idx]:
        st.markdown('<div class="section-title">📚 المراجع العلمية المعتمدة</div>',
                    unsafe_allow_html=True)
        refs = {
            "NRC 2012 — Nutrient Requirements of Swine": "المرجع الرسمي للخنازير والأحماض الأمينية",
            "NRC 2007 — Small Ruminants": "الأغنام والماعز والمجترات الصغيرة",
            "NRC 2001 — Dairy Cattle": "أبقار الحليب والمعادن والفيتامينات",
            "NRC 2007 — Horses": "خيول وتربية",
            "NRC 1994 — Poultry": "دواجن (طبعة كلاسيكية)",
            "NRC Fish Nutrition": "تغذية الأسماك",
            "INRA 2018": "النظام الفرنسي — البروتين المهضوم",
            "Ross 308 (2020)": "دليل إدارة الدجاج اللاحم",
            "FAO 2010 — Camel Nutrition": "تغذية الإبل والجمال",
            "McDonald et al. (2011)": "Animal Nutrition — 7th Edition",
            "Van Soest (1994)": "تحليل الألياف والكربوهيدرات",
            "Palmquist (2006)": "دهون الحليب — Milk Fat Depression",
        }
        for k, v in refs.items():
            st.markdown(f"**📖 {k}** — {v}")

help_idx = tabs_titles.index("💡 المساعدة") if "💡 المساعدة" in tabs_titles else -1
if help_idx >= 0:
    with tabs[help_idx]:
        st.markdown('<div class="section-title">💡 المساعدة الذكية</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        ### الأسئلة الشائعة
        - **كيف أبدأ؟** اختر الحيوان ← فعّل الاعتماد ← اختر المكونات ← شغّل المحرك
        - **DP أم CP؟** اختر أساس الحساب: DP (الأدق)، CP (الأسهل)
        - **الزيوت؟** راجع تبويب "مكتبة الزيوت" — كل حيوان له حد أقصى مختلف
        - **الدقة؟** مؤشر RMSE يقيس نسبة الانحراف عن المعيار. أقل من 0.5% = مطابق

        ### 📧 الدعم
        - Email: {OWNER_EMAIL}
        - WhatsApp: {WHATSAPP_NUMBER}

        ### 🕌 دعاء
        {DUA_FULL}
        """)

guide_idx = tabs_titles.index("📖 الدليل") if "📖 الدليل" in tabs_titles else -1
if guide_idx >= 0:
    with tabs[guide_idx]:
        st.markdown('<div class="section-title">📖 دليل المستخدم</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        ### 🌾 {APP_NAME}
        **الغرض:** تركيب أعلاف بأقل تكلفة وأعلى دقة بمعايير NRC/INRA/FAO/Ross 308.

        ### ✨ الميزات
        - 🐄 **8 قطاعات:** أبقار، أغنام، ماعز، إبل، خيول، دواجن، سمان، أسماك
        - 🌰 **14 زيتاً:** نباتية وحيوانية بمعايير دولية
        - 🧠 **محرك LP:** يطابق DP + SE + NDF + ADF + Ca + P + EE
        - 📊 **مؤشرات دقة:** RMSE + Conformity Score + التقييم
        - 📷 **OCR:** تحليل صور الخلطات
        - 📄 **تقارير PDF/Excel** احترافية
        - 🐔 **إدارة مزارع Broiler** (للمالك)

        ### 📊 مؤشرات الدقة
        - 🎯 **مطابق تماماً:** فرق ≤ 0.5%
        - 🌟 **ممتاز:** 0.5-2%
        - ✅ **جيد جداً:** 2-5%
        - 🟢 **جيد:** 5-10%

        ### 🔐 الأمان
        - كود المالك مُشفَّر SHA-256 — غير قابل للعكس
        - Rate limiting (5 محاولات) + قفل 5 دقائق
        - رموز جلسة موقّعة HMAC
        - قفل الدومين (Domain Lock)
        """)


# ═════════════════════════════════════════════════════════════════════════════
# التذييل الثابت
# ═════════════════════════════════════════════════════════════════════════════

st.markdown(
    f'<div class="mini-signature">🌾 {APP_NAME} | {SUPERVISOR} © 2026</div>',
    unsafe_allow_html=True)
st.markdown(
    f'<div class="dua-fixed-banner">🤲 {DUA_SHORT} 🤲</div>',
    unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# نهاية الملف
# ═════════════════════════════════════════════════════════════════════════════
