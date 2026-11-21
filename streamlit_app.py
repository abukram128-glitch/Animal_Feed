# ═══════════════════════════════════════════════════════════════════════
# تاور نولجي TAWOR NOLOGY 11.11.0
# د. عبدالقادر إسماعيل تاور
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
# ═══════════════════════════════════════════════════════════════════════
# جديد v11.11.0:
#   ✅ نظام موافقة PDF كامل (زائر/مختص يحتاجون موافقة المالك)
#   ✅ 3 أزرار استشارة (واتساب + بريد + اتصال)
#   ✅ فيديو تعريفي عند فتح التطبيق
#   ✅ 3D إسطبلات خيول محسّنة (بأبواب + حصان + معلف + دلو)
#   ✅ شريط القياس بأسهم حمراء/زرقاء على الصورة
#   ✅ تبويب إدارة طلبات PDF للمالك
# ═══════════════════════════════════════════════════════════════════════

import base64
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
import hashlib
import hmac
import io
import json
import os
import random
import re
import time as _time
import traceback
from typing import Dict, Optional
import urllib.parse
import warnings

import numpy as np
import pandas as pd
import streamlit as st

warnings.filterwarnings("ignore")

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

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Wedge

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from PIL import Image as PILImage

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    import pytesseract

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    from reportlab.lib.colors import HexColor, white
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        HRFlowable,
        Image as RLImage,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

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
# الثوابت والإعدادات الأساسية
# ═══════════════════════════════════════════════════════════════════════

DUA_SHORT = "رحم الله والدي إسماعيل تاور وأختي ابتسام"
DUA_FULL = "رحم الله والدي إسماعيل تاور وأختي ابتسام وأسكنهما فسيح جناته"
DUA_QURAN = "﴿ رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ ﴾"
DUA_VISITOR = """🕌 <b>إلى زوارنا الكرام:</b><br>
هذه المنصة صدقةٌ جارية عن <b>والدي إسماعيل تاور</b> و<b>أختي ابتسام</b>.<br>
نسألكم بظهر الغيب أن تشاركوا الدعاء. 🤲"""

APP_NAME = "تاور نولجي Tawor Nology"
APP_TAGLINE = "للإنتاج الحيواني وتغذية الحيوان"
APP_VERSION = "11.11.0"
SUPERVISOR = "د. عبدالقادر إسماعيل تاور"
SUPERVISOR_TITLE = "اختصاصي إنتاج حيواني وتغذية الحيوان"
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


# ═══════════════════════════════════════════════════════════════════════
# 🔐 الأمان
# ═══════════════════════════════════════════════════════════════════════


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _get_owner_code_hash() -> Optional[str]:
    try:
        _blob = "Nzg2MjAy"
        return _sha256(base64.b64decode(_blob).decode()[::-1])
    except Exception:
        return None


def audit_log(event: str, details: str = "") -> None:
    try:
        with open("tawor_audit.log", "a", encoding="utf-8") as f:
            f.write(
                f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {event} | {details[:200]}\n"
            )
    except Exception:
        pass


def check_owner_code(user_input: str) -> bool:
    if not user_input:
        audit_log("LOGIN_EMPTY", "")
        return False
    expected = _get_owner_code_hash()
    if not expected:
        audit_log("LOGIN_NO_HASH", "")
        return False
    ok = hmac.compare_digest(_sha256(user_input.strip()), expected)
    audit_log("LOGIN_OK" if ok else "LOGIN_FAIL", "owner")
    return ok


def check_rate_limit(key: str, max_calls: int = 30, window: int = 60) -> bool:
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


def generate_csrf_token() -> str:
    if "csrf_token" not in st.session_state:
        st.session_state["csrf_token"] = base64.b64encode(os.urandom(32)).decode()
    return st.session_state["csrf_token"]


def _sanitize_message(msg: str, max_len: int = 500) -> str:
    if not msg:
        return ""
    msg = str(msg).strip()[:max_len]
    msg = re.sub(r"<[^>]+>", "", msg)
    msg = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", msg)
    return msg


def _safe_username() -> str:
    if "chat_username" not in st.session_state:
        role = st.session_state.get("user_role", "guest")
        prefix = {"owner": "المالك", "specialist": "مختص", "guest": "زائر"}.get(
            role, "زائر"
        )
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
                urllib.request.urlretrieve(url, target)
            self._register(target)
        except Exception:
            pass

    def _register(self, path: str) -> bool:
        try:
            pdfmetrics.registerFont(TTFont("TaworArabic", path))
            self.font_name = "TaworArabic"
            self.ready = True
            return True
        except Exception:
            return False


font_mgr = ArabicFontManager()


@lru_cache(maxsize=1500)
def _ar_cached(text: str) -> str:
    if not text:
        return ""
    if not ARABIC_AVAILABLE:
        return str(text)
    try:
        return get_display(arabic_reshaper.reshape(str(text)), base_dir="R")
    except Exception:
        return str(text)


def ar(text: str) -> str:
    return _ar_cached(text)


# ═══════════════════════════════════════════════════════════════════════
# 📚 المراجع والمعادلات العلمية
# ═══════════════════════════════════════════════════════════════════════

STANDARD_REFERENCES = {
    "أبقار_حليب_عالي": {
        "primary": "NRC (2001) — Nutrient Requirements of Dairy Cattle, 7th Ed.",
        "table": "Table 15-1: Lactating dairy cows (high production)",
        "secondary": ["INRA (2018) — Feeding System for Ruminants", "NRC (2001) — Table 15-2"],
    },
    "أبقار_حليب_متوسط": {
        "primary": "NRC (2001) — Dairy Cattle, 7th Ed.",
        "table": "Table 15-1: Lactating dairy cows (medium)",
        "secondary": ["INRA (2018)"],
    },
    "أبقار_حليب_منخفض": {
        "primary": "NRC (2001) — Dairy Cattle",
        "table": "Table 15-1: Low production",
        "secondary": ["INRA (2018)"],
    },
    "أبقار_تسمين_مكثف": {
        "primary": "NRC (2001) + NRC (1996)",
        "table": "Table 15-1: Growing/finishing",
        "secondary": ["INRA (2018)"],
    },
    "أبقار_تسمين_عادي": {
        "primary": "NRC (1996) — Beef Cattle",
        "table": "Table 10-1: Growth",
        "secondary": [],
    },
    "أبقار_حمل_أخير": {
        "primary": "NRC (2001)",
        "table": "Table 15-3: Gestating",
        "secondary": [],
    },
    "أبقار_صيانة": {
        "primary": "NRC (2001)",
        "table": "Table 15-4: Maintenance",
        "secondary": [],
    },
    "أغنام_تسمين_مكثف": {
        "primary": "NRC (2007) — Small Ruminants",
        "table": "Table 11-1: Growing lambs",
        "secondary": ["INRA (2018)"],
    },
    "أغنام_تسمين_عادي": {
        "primary": "NRC (2007)",
        "table": "Table 11-1",
        "secondary": [],
    },
    "أغنام_مرضعات": {
        "primary": "NRC (2007)",
        "table": "Table 11-2: Lactating ewes",
        "secondary": ["INRA (2018)"],
    },
    "أغنام_حامل_أخير": {
        "primary": "NRC (2007)",
        "table": "Table 11-2",
        "secondary": [],
    },
    "أغنام_حامل_متوسط": {
        "primary": "NRC (2007)",
        "table": "Table 11-2",
        "secondary": [],
    },
    "أغنام_صيانة": {
        "primary": "NRC (2007)",
        "table": "Table 11-3",
        "secondary": [],
    },
    "أغنام_حملان_تيد": {
        "primary": "NRC (2007)",
        "table": "Table 11-1",
        "secondary": [],
    },
    "ماعز_حلابة_عالي": {
        "primary": "NRC (2007)",
        "table": "Table 12-1",
        "secondary": ["INRA (2018)"],
    },
    "ماعز_حلابة_متوسط": {
        "primary": "NRC (2007)",
        "table": "Table 12-1",
        "secondary": [],
    },
    "ماعز_تسمين_جديان": {
        "primary": "NRC (2007)",
        "table": "Table 12-2",
        "secondary": [],
    },
    "ماعز_تيوس": {
        "primary": "NRC (2007)",
        "table": "Table 12-2",
        "secondary": [],
    },
    "ماعز_صيانة": {
        "primary": "NRC (2007)",
        "table": "Table 12-3",
        "secondary": [],
    },
    "ماعز_حامل_أخير": {
        "primary": "NRC (2007)",
        "table": "Table 12-2",
        "secondary": [],
    },
    "إبل_حليب": {
        "primary": "FAO (2010) — Camel Nutrition",
        "table": "Section 4",
        "secondary": ["Al-Jassim et al. (2002)"],
    },
    "إبل_تسمين": {
        "primary": "FAO (2010)",
        "table": "Section 5",
        "secondary": [],
    },
    "إبل_نمو": {
        "primary": "FAO (2010)",
        "table": "Section 3",
        "secondary": [],
    },
    "إبل_سباق": {
        "primary": "FAO (2010)",
        "table": "Section 6",
        "secondary": [],
    },
    "إبل_صيانة": {
        "primary": "FAO (2010)",
        "table": "Section 2",
        "secondary": [],
    },
    "خيول_رياضة_مكثف": {
        "primary": "NRC (2007) — Horses, 6th Ed.",
        "table": "Table 10-1: Intense work",
        "secondary": [],
    },
    "خيول_رياضة_عادي": {
        "primary": "NRC (2007)",
        "table": "Table 10-1",
        "secondary": [],
    },
    "خيول_نمو_أمهار": {
        "primary": "NRC (2007)",
        "table": "Table 10-2",
        "secondary": [],
    },
    "خيول_مرضعات": {
        "primary": "NRC (2007)",
        "table": "Table 10-3",
        "secondary": [],
    },
    "خيول_صيانة": {
        "primary": "NRC (2007)",
        "table": "Table 10-4",
        "secondary": [],
    },
    "دواجن_لاحم": {
        "primary": "Ross 308 (2020)",
        "table": "Nutrient requirements",
        "secondary": ["NRC (1994) — Poultry"],
    },
    "دواجن_بياض": {
        "primary": "NRC (1994) — Poultry",
        "table": "Table 4",
        "secondary": ["Lohmann (2020)"],
    },
    "سمان_تسمين": {
        "primary": "NRC (1994)",
        "table": "Table 12",
        "secondary": [],
    },
    "سمان_بياض": {
        "primary": "NRC (1994)",
        "table": "Table 12",
        "secondary": [],
    },
    "أسماك_بادئ": {
        "primary": "NRC (2011) — Fish Nutrition",
        "table": "Table 6-1",
        "secondary": ["FAO (2018)"],
    },
    "أسماك_نمو": {
        "primary": "NRC (2011)",
        "table": "Table 6-2",
        "secondary": [],
    },
    "أسماك_تسمين": {
        "primary": "NRC (2011)",
        "table": "Table 6-3",
        "secondary": [],
    },
    "أرانب_تسمين": {
        "primary": "NRC (2007)",
        "table": "Rabbit chapter",
        "secondary": ["INRA (2018)"],
    },
    "أرانب_حليب": {
        "primary": "NRC (2007)",
        "table": "Lactating does",
        "secondary": [],
    },
    "أرانب_صيانة": {
        "primary": "NRC (2007)",
        "table": "Maintenance",
        "secondary": [],
    },
    "خيول_مربط": {
        "primary": "NRC (2007) — Horses + MWPS-1 Structures Handbook",
        "table": "Stall dimensions & ventilation standards",
        "secondary": ["ASAE (2005) — Ventilation Standards", "FAO (2012) — Rural Structures"],
    },
}

GENERAL_REFERENCES = [
    "NRC (2001) — Nutrient Requirements of Dairy Cattle, 7th Ed.",
    "NRC (2007) — Nutrient Requirements of Small Ruminants",
    "NRC (2012) — Nutrient Requirements of Swine, 11th Ed.",
    "NRC (1994) — Nutrient Requirements of Poultry, 9th Ed.",
    "NRC (2007) — Nutrient Requirements of Horses, 6th Ed.",
    "NRC (2011) — Fish and Shrimp Nutrition",
    "INRA (2018) — INRA Feeding System for Ruminants",
    "FAO (2010) — Camel Nutrition",
    "Ross 308 (2020) — Broiler Nutrition Specification",
    "Schaeffer (1978) — Heart Girth Weight Equation",
    "Carroll & Huntington (1988) — Horse Weight Formula",
    "Danø & Højsgaard (2005) — LP in Ration Formulation",
    "Kraft (1988) — SLSQP Algorithm",
    "Nocedal & Wright (2006) — Numerical Optimization",
    "MWPS-1 (2000) — Structures and Environment Handbook",
    "ASAE (2005) — Ventilation Standards",
]


def get_references(animal_type: str, production_type: str) -> Dict:
    key = f"{animal_type}_{production_type}"
    if key in STANDARD_REFERENCES:
        return STANDARD_REFERENCES[key]
    for k, v in STANDARD_REFERENCES.items():
        if k.startswith(f"{animal_type}_"):
            return v
    return {"primary": "NRC (2012) — General", "table": "—", "secondary": ["INRA (2018)", "FAO (2010)"]}


REFERENCE_EQUATIONS = {
    "أبقار_حليب_عالي": {
        "DP": "DP = 9.0 + (الحليب × 0.175)  [سقف 16%]",
        "CP": "CP = DP ÷ 0.72",
        "SE": "SE = 60 + (الحليب × 0.35)",
        "Ca": "Ca = 0.55 + (الحليب × 0.003)",
        "P": "P = 0.33 + (الحليب × 0.0015)",
        "example": "بقرة 20 لتر → DP = 12.5% | CP ≈ 17.4%",
        "source": "NRC (2001) — Table 15-1",
    },
    "أبقار_حليب_متوسط": {
        "DP": "DP = 8.5 + (الحليب × 0.17)  [سقف 14%]",
        "CP": "CP = DP ÷ 0.72",
        "SE": "SE = 55 + (الحليب × 0.30)",
        "source": "NRC (2001)",
    },
    "أبقار_حليب_منخفض": {
        "DP": "DP = 8.0 + (الحليب × 0.16)  [سقف 12.5%]",
        "CP": "CP = DP ÷ 0.75",
        "source": "NRC (2001)",
    },
    "أبقار_تسمين_مكثف": {"DP": "11.5%", "CP": "14.5%", "SE": "72", "source": "NRC (1996)"},
    "أبقار_تسمين_عادي": {"DP": "9.5%", "CP": "12%", "SE": "65", "source": "NRC (1996)"},
    "أبقار_حمل_أخير": {"DP": "11.5%", "CP": "14.5%", "SE": "67", "source": "NRC (2001)"},
    "أبقار_صيانة": {"DP": "7.5%", "CP": "10%", "SE": "53", "source": "NRC (2001)"},
    "أغنام_تسمين_مكثف": {"DP": "11.5%", "CP": "14.5%", "SE": "64", "source": "NRC (2007)"},
    "أغنام_تسمين_عادي": {"DP": "9.5%", "CP": "12%", "SE": "59", "source": "NRC (2007)"},
    "أغنام_مرضعات": {"DP": "10.5 + (المواليد - 1) × 1.5", "CP": "DP ÷ 0.72", "source": "NRC (2007)"},
    "أغنام_حامل_أخير": {"DP": "10.5%", "CP": "13.5%", "SE": "62", "source": "NRC (2007)"},
    "أغنام_حامل_متوسط": {"DP": "8.5%", "CP": "11%", "SE": "55", "source": "NRC (2007)"},
    "أغنام_صيانة": {"DP": "7.2%", "CP": "9.5%", "SE": "48", "source": "NRC (2007)"},
    "أغنام_حملان_تيد": {"DP": "8.5%", "CP": "11%", "SE": "55", "source": "NRC (2007)"},
    "ماعز_حلابة_عالي": {"DP": "9.5 + (الحليب × 0.35)", "CP": "DP ÷ 0.72", "source": "NRC (2007)"},
    "ماعز_حلابة_متوسط": {"DP": "8.5 + (الحليب × 0.30)", "CP": "DP ÷ 0.72", "source": "NRC (2007)"},
    "ماعز_تسمين_جديان": {"DP": "11%", "CP": "14%", "SE": "62", "source": "NRC (2007)"},
    "ماعز_تيوس": {"DP": "9%", "CP": "11.5%", "SE": "57", "source": "NRC (2007)"},
    "ماعز_صيانة": {"DP": "6.8%", "CP": "9%", "SE": "46", "source": "NRC (2007)"},
    "ماعز_حامل_أخير": {"DP": "10%", "CP": "13%", "SE": "60", "source": "NRC (2007)"},
    "إبل_حليب": {"DP": "10.5 + (الحليب × 0.20)", "SE": "62 + (الحليب × 0.4)", "source": "FAO (2010)"},
    "إبل_تسمين": {"DP": "9.5%", "SE": "65", "source": "FAO (2010)"},
    "إبل_نمو": {"DP": "10.5%", "SE": "60", "source": "FAO (2010)"},
    "إبل_سباق": {"DP": "14%", "SE": "72", "source": "FAO (2010)"},
    "إبل_صيانة": {"DP": "7%", "SE": "48", "source": "FAO (2010)"},
    "خيول_رياضة_مكثف": {"DP": "10.5%", "SE": "70", "source": "NRC (2007)"},
    "خيول_رياضة_عادي": {"DP": "9%", "SE": "63", "source": "NRC (2007)"},
    "خيول_نمو_أمهار": {"DP": "12%", "SE": "65", "source": "NRC (2007)"},
    "خيول_مرضعات": {"DP": "12.5%", "SE": "68", "source": "NRC (2007)"},
    "خيول_صيانة": {"DP": "7.2%", "SE": "53", "source": "NRC (2007)"},
    "دواجن_لاحم": {
        "DP": "20% → 16.5%",
        "CP": "23% → 19%",
        "SE": "76 → 75",
        "example": "بادي: CP=23%, SE=76",
        "source": "Ross 308 (2020)",
    },
    "دواجن_بياض": {"DP": "15.5%", "CP": "18%", "source": "NRC (1994)"},
    "سمان_تسمين": {"DP": "18.5% → 17%", "SE": "72 → 70", "source": "NRC (1994)"},
    "سمان_بياض": {"DP": "15%", "SE": "68", "source": "NRC (1994)"},
    "أسماك_بادئ": {"DP": "32%", "CP": "40%", "source": "NRC (2011)"},
    "أسماك_نمو": {"DP": "25%", "CP": "32%", "source": "NRC (2011)"},
    "أسماك_تسمين": {"DP": "22%", "CP": "28%", "source": "NRC (2011)"},
    "أرانب_تسمين": {"DP": "15%", "CP": "17%", "source": "NRC (2007)"},
    "أرانب_حليب": {"DP": "18%", "CP": "20%", "source": "NRC (2007)"},
    "أرانب_صيانة": {"DP": "12%", "CP": "14%", "source": "NRC (2007)"},
    "خيول_مربط": {
        "المربط": "3.5 م × 3.5 م = 12.25 م² لكل حصان",
        "الممر": "3.5 م",
        "التهوية الصيف": "25 تجديد/ساعة",
        "التهوية الشتاء": "5 تجديد/ساعة",
        "الماء": "45 لتر/حصان/يوم",
        "source": "NRC (2007) + MWPS-1",
    },
    "معادلة_التركيب_LP": {
        "الهدف": "min Z = Σ(سعر_i × x_i)",
        "قيد_المجموع": "Σ x_i = 100%",
        "قيد_البروتين": "Σ(CP_i × x_i) = CP",
        "قيد_الطاقة": "Σ(SE_i × 41 × x_i) ≥ 0.90 × ME",
        "قيد_التوازن": "Σ(طاقة) - Σ(بروتين) ≥ 10%",
        "source": "Danø & Højsgaard (2005)",
    },
    "معادلة_التركيب_NLP": {
        "الهدف": "max Z = سعر × (ME/ME_هدف) × (CP/CP_هدف) - Σ(سعر_i × x_i)",
        "الطريقة": "SLSQP",
        "المستويات": "8 مستويات (100% → 70%)",
        "source": "Kraft (1988)",
    },
}


def get_reference_equations(animal_type: str, production_type: str) -> Dict:
    key = f"{animal_type}_{production_type}"
    if key in REFERENCE_EQUATIONS:
        return REFERENCE_EQUATIONS[key]
    for k, v in REFERENCE_EQUATIONS.items():
        if k.startswith(f"{animal_type}_"):
            return v
    return {}


# ═══════════════════════════════════════════════════════════════════════
# مكتبة الأعلاف والحدود والزيوت
# ═══════════════════════════════════════════════════════════════════════


def _feed(cp, dc, se, ndf, adf, ee, ash, ca, p, lys, met, price, desc, src):
    return {
        "CP": cp,
        "DC": dc,
        "SE": se,
        "NDF": ndf,
        "ADF": adf,
        "EE": ee,
        "ASH": ash,
        "Ca": ca,
        "P": p,
        "Lys": lys,
        "Met": met,
        "price": price,
        "desc": desc,
        "src": src,
    }


BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": _feed(8.5, 0.85, 80, 9.5, 3.2, 3.8, 1.3, 0.02, 0.27, 0.24, 0.17, 230, "الطاقة", "NRC 2012"),
        "ذرة بيضاء": _feed(8.8, 0.83, 78, 10.2, 3.5, 3.5, 1.4, 0.02, 0.26, 0.25, 0.18, 225, "بديل", "NRC 2012"),
        "ذرة شامية": _feed(8.3, 0.86, 82, 9.0, 3.0, 4.0, 1.2, 0.02, 0.28, 0.23, 0.16, 240, "طاقة", "NRC 2012"),
        "ذرة رفيعة (سورجم)": _feed(10.0, 0.78, 70, 12.5, 5.5, 3.0, 1.8, 0.03, 0.30, 0.22, 0.17, 195, "بديل", "NRC 2012"),
        "شعير مطحون": _feed(11.5, 0.80, 71, 18.5, 7.5, 2.2, 2.5, 0.05, 0.35, 0.42, 0.20, 210, "مجترات", "NRC 2012"),
        "شعير كامل": _feed(10.8, 0.75, 68, 22.0, 9.0, 2.0, 2.8, 0.05, 0.33, 0.40, 0.18, 200, "جرش", "NRC 2012"),
        "قمح محلي": _feed(12.0, 0.85, 75, 11.5, 3.8, 2.0, 1.6, 0.04, 0.32, 0.35, 0.20, 240, "طاقة", "NRC 2012"),
        "قمح مستورد": _feed(11.5, 0.87, 78, 11.0, 3.5, 1.9, 1.5, 0.04, 0.33, 0.34, 0.19, 245, "طاقة", "NRC 2012"),
        "جريش أرز": _feed(7.8, 0.82, 82, 5.5, 2.5, 8.5, 4.2, 0.06, 0.30, 0.28, 0.18, 240, "عالية", "NRC 2012"),
        "دخن محلي": _feed(11.0, 0.75, 68, 15.5, 6.5, 4.0, 2.2, 0.05, 0.31, 0.28, 0.20, 220, "بديل", "NRC 2012"),
        "شوفان علفي": _feed(11.0, 0.76, 62, 27.5, 13.5, 5.0, 3.0, 0.08, 0.35, 0.40, 0.18, 260, "خيول", "NRC 2007"),
        "كسرة خبز": _feed(10.5, 0.82, 75, 8.0, 3.5, 5.5, 3.5, 0.10, 0.20, 0.28, 0.17, 160, "اقتصادي", "INRA 2018"),
        "مكرونة مكسرة": _feed(11.0, 0.88, 80, 3.5, 1.5, 1.5, 1.0, 0.03, 0.20, 0.28, 0.15, 190, "طاقة", "INRA 2018"),
        "تمر مجفف (دقل)": _feed(5.5, 0.85, 68, 15.0, 8.5, 1.0, 3.5, 0.10, 0.10, 0.10, 0.05, 180, "اقتصادي", "FAO 2010"),
        "تفل بنجر السكر": _feed(8.5, 0.65, 55, 45.0, 28.0, 1.0, 8.5, 0.70, 0.10, 0.30, 0.15, 190, "مجترات", "INRA 2018"),
        "تفل زيتون": _feed(8.0, 0.55, 35, 50.0, 35.0, 12.0, 7.0, 0.50, 0.15, 0.20, 0.10, 130, "زيوت", "INRA 2018"),
    },
    "🌱 الأكساب ومصادر البروتين": {
        "كسب فول صويا 44%": _feed(44.0, 0.90, 74, 13.5, 8.0, 1.8, 6.0, 0.35, 0.65, 2.70, 0.60, 440, "رئيسي", "NRC 2012"),
        "كسب فول صويا 48%": _feed(48.0, 0.91, 76, 12.0, 7.0, 1.5, 6.2, 0.35, 0.65, 3.00, 0.68, 480, "مرتفع", "NRC 2012"),
        "أمباز الفول السوداني": _feed(46.0, 0.88, 73, 15.5, 8.5, 1.5, 5.5, 0.20, 0.65, 1.60, 0.45, 460, "ممتاز", "NRC 2012"),
        "كسب عباد الشمس 36%": _feed(36.0, 0.76, 42, 38.5, 25.5, 2.5, 6.5, 0.40, 1.00, 1.20, 0.70, 310, "اقتصادي", "NRC 2012"),
        "كسب عباد الشمس 32%": _feed(32.0, 0.72, 38, 42.0, 28.0, 2.0, 7.0, 0.42, 0.95, 1.10, 0.65, 290, "اقتصادي", "NRC 2012"),
        "كسب بذور القطن": _feed(41.0, 0.78, 55, 24.5, 15.5, 1.2, 6.5, 0.20, 1.10, 1.80, 0.60, 290, "جوسيبول", "NRC 2012"),
        "كسب بذور الكتان": _feed(32.0, 0.82, 65, 18.5, 10.5, 2.8, 5.8, 0.35, 0.85, 1.20, 0.55, 340, "أوميغا3", "NRC 2007"),
        "كسب السمسم": _feed(42.0, 0.84, 70, 14.5, 9.5, 8.5, 12.5, 2.00, 1.20, 1.30, 1.00, 520, "غني Ca", "NRC 2007"),
        "كسب جلوتين 60%": _feed(60.0, 0.92, 85, 8.5, 5.5, 2.5, 3.5, 0.15, 0.50, 1.10, 1.80, 520, "Met", "NRC 2012"),
        "كسب نواة النخيل": _feed(16.0, 0.65, 52, 55.5, 35.5, 6.5, 4.5, 0.30, 0.55, 0.55, 0.28, 200, "رخيص", "FAO 2010"),
        "كسب الكانولا": _feed(36.0, 0.82, 60, 28.0, 18.0, 3.5, 6.5, 0.65, 1.10, 1.90, 0.70, 400, "متوازن", "NRC 2012"),
        "فول صويا كامل": _feed(38.0, 0.85, 78, 15.0, 10.0, 18.0, 4.5, 0.25, 0.55, 2.50, 0.55, 420, "معالجة", "NRC 2012"),
        "بازلاء علفية": _feed(22.0, 0.82, 70, 15.0, 8.0, 1.5, 3.0, 0.10, 0.40, 1.50, 0.25, 320, "متوازن", "NRC 2012"),
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": _feed(15.0, 0.72, 45, 35.5, 12.5, 3.5, 5.5, 0.12, 1.10, 0.60, 0.25, 150, "اقتصادية", "NRC 2001"),
        "نخالة ذرة": _feed(9.5, 0.65, 40, 40.0, 15.0, 4.0, 2.0, 0.10, 0.75, 0.30, 0.15, 140, "اقتصادية", "NRC 2001"),
        "البرسيم الجاف": _feed(16.5, 0.60, 35, 42.5, 32.5, 2.0, 10.5, 1.50, 0.25, 0.85, 0.25, 170, "بروتين", "NRC 2001"),
        "برسيم حجازي": _feed(18.0, 0.62, 38, 40.0, 30.0, 2.2, 11.0, 1.60, 0.26, 0.90, 0.28, 175, "أفضل", "NRC 2001"),
        "مولاس قصب السكر": _feed(4.0, 0.95, 50, 1.5, 0.8, 0.5, 8.5, 0.70, 0.05, 0.03, 0.02, 120, "طاقة", "NRC 2001"),
        "تبن قمح": _feed(3.2, 0.35, 18, 72.5, 45.5, 1.5, 8.5, 0.30, 0.08, 0.15, 0.05, 80, "حشو", "NRC 2001"),
        "تبن فول": _feed(4.5, 0.40, 22, 68.0, 42.0, 1.2, 7.5, 0.35, 0.10, 0.18, 0.08, 90, "أفضل", "NRC 2001"),
        "قش أرز": _feed(3.5, 0.30, 15, 70.0, 45.0, 1.5, 12.0, 0.20, 0.06, 0.12, 0.05, 65, "حشو", "NRC 2007"),
        "سعف نخيل مطحون": _feed(4.0, 0.30, 20, 65.0, 42.0, 2.0, 7.0, 0.35, 0.08, 0.15, 0.06, 55, "ألياف", "FAO 2010"),
        "مخلفات النخيل": _feed(6.5, 0.70, 60, 25.0, 15.0, 5.0, 3.5, 0.15, 0.15, 0.25, 0.10, 100, "إبل", "FAO 2010"),
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": _feed(60.0, 0.85, 65, 2.5, 1.5, 8.5, 22.5, 5.50, 3.20, 4.50, 1.80, 850, "ممتاز", "NRC 2012"),
        "مسحوق أسماك 72%": _feed(72.0, 0.90, 72, 2.0, 1.0, 9.5, 18.5, 4.80, 2.80, 5.50, 2.20, 1100, "مرتفع", "NRC 2012"),
        "مسحوق اللحم والعظم": _feed(50.0, 0.75, 50, 3.5, 2.5, 10.5, 32.5, 9.00, 4.50, 2.50, 0.70, 620, "Ca+P", "NRC 2012"),
        "مسحوق الدم": _feed(80.0, 0.65, 55, 1.0, 0.5, 1.5, 6.0, 0.30, 0.30, 7.00, 1.00, 780, "هضم منخفض", "NRC 2012"),
        "مسحوق ريش": _feed(82.0, 0.70, 60, 1.5, 1.0, 3.0, 4.0, 0.25, 0.35, 2.00, 0.50, 650, "معالجة", "NRC 2012"),
        "مركزات دواجن": _feed(40.0, 0.85, 60, 8.5, 4.5, 3.5, 12.5, 2.50, 1.20, 2.50, 0.90, 650, "جاهزة", "NRC 2012"),
        "مركزات مواشي": _feed(36.0, 0.80, 55, 15.5, 8.5, 3.0, 15.5, 3.00, 1.50, 2.00, 0.70, 600, "جاهزة", "NRC 2001"),
        "حشرات مجففة (BSF)": _feed(42.0, 0.80, 68, 8.0, 5.0, 35.0, 8.0, 0.80, 0.90, 2.60, 0.85, 1800, "مستدام", "FAO 2013"),
    },
    "🌰 الزيوت النباتية والحيوانية": {
        "زيت ذرة": _feed(0.0, 0.0, 220, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1500, "أوميغا6", "NRC 2012"),
        "زيت فول الصويا": _feed(0.0, 0.0, 215, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1350, "متوازن", "Ross 308"),
        "زيت عباد الشمس": _feed(0.0, 0.0, 210, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1300, "أوميغا6", "NRC 2007"),
        "زيت الكتان": _feed(0.0, 0.0, 205, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1700, "أوميغا3", "NRC 2007"),
        "زيت جوز الهند": _feed(0.0, 0.0, 230, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1900, "MCT", "NRC 2012"),
        "زيت النخيل": _feed(0.0, 0.0, 215, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1100, "مقاوم", "NRC 2012"),
        "زيت الكانولا": _feed(0.0, 0.0, 200, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1450, "متوازن", "NRC 2012"),
        "شحم حيواني (Tallow)": _feed(0.0, 0.0, 230, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 900, "طاقة", "NRC 2012"),
        "زيت السمك (Fish Oil)": _feed(0.0, 0.0, 235, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3800, "EPA", "NRC Fish"),
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": _feed(94.0, 1.0, 0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 94.0, 0.0, 4200, "أساسي", "NRC 2012"),
        "ميثيونين نقي": _feed(58.0, 1.0, 0, 0.0, 0.0, 0.0, 0.3, 0.0, 0.0, 0.0, 58.0, 5800, "دواجن", "NRC 2012"),
        "ثريونين نقي": _feed(72.0, 1.0, 0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 4800, "ثالث", "NRC 2012"),
        "تريبتوفان نقي": _feed(85.0, 1.0, 0, 0.0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 9500, "دواجن", "NRC 2012"),
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 100.0, 18.0, 8.0, 0.0, 0.0, 4800, "فيتامينات", "NRC 1994"),
        "بريمكس بياض": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 100.0, 22.0, 7.0, 0.0, 0.0, 5000, "بياض", "NRC 1994"),
        "بريمكس أبقار": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 100.0, 20.0, 10.0, 0.0, 0.0, 5200, "أبقار", "NRC 2001"),
        "بريمكس مجترات": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 100.0, 18.0, 9.0, 0.0, 0.0, 4500, "مجترات", "NRC 2007"),
        "بريمكس خيول": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 100.0, 15.0, 8.0, 0.0, 0.0, 5500, "خيول", "NRC 2007"),
        "بريمكس إبل": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 100.0, 20.0, 10.0, 0.0, 0.0, 5300, "إبل", "FAO 2010"),
        "بريمكس أسماك": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 100.0, 15.0, 7.0, 0.0, 0.0, 5800, "أسماك", "NRC Fish"),
        "إنزيم فايتيز": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 4200, "تحرير P", "NRC 2012"),
        "خمائر حية": _feed(45.0, 0.75, 30, 8.0, 4.0, 1.0, 8.0, 0.15, 1.20, 3.00, 0.70, 8500, "مجترات", "NRC 2001"),
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 99.5, 38.0, 0.0, 0.0, 0.0, 40, "Ca", "NRC 2012"),
        "فوسفات ثنائي الكالسيوم": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 98.5, 23.0, 18.0, 0.0, 0.0, 280, "Ca+P", "NRC 2012"),
        "فوسفات أحادي الكالسيوم": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 99.0, 17.0, 22.0, 0.0, 0.0, 320, "P", "NRC 2012"),
        "ملح الطعام": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 99.9, 0.0, 0.0, 0.0, 0.0, 30, "NaCl", "NRC 2012"),
        "بيكربونات الصوديوم": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 99.0, 0.0, 0.0, 0.0, 0.0, 340, "مضاد", "NRC 2001"),
        "أكسيد المغنيسيوم": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 99.5, 0.0, 0.0, 0.0, 0.0, 480, "Mg", "NRC 2007"),
        "يوريا علفية": _feed(287.0, 0.95, 0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 480, "NPN", "NRC 2001"),
        "مضاد سموم فطرية": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 85.0, 0.0, 0.0, 0.0, 0.0, 950, "أفلاتوكسين", "NRC 2012"),
    },
    "💊 الفيتامينات": {
        "فيتامين A": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 4200, "نمو", "NRC 2012"),
        "فيتامين D3": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 5200, "Ca", "NRC 2012"),
        "فيتامين E": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 5800, "أكسدة", "NRC 2012"),
        "كولين كلوريد": _feed(0.0, 0.0, 0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0, 3200, "B4", "NRC 2012"),
    },
}


def _get_ingredient_lookup() -> Dict:
    if not hasattr(_get_ingredient_lookup, "_cache"):
        lookup = {}
        for cat in BIG_FEEDS_LIBRARY.values():
            for name, data in cat.items():
                lookup[name] = data
        _get_ingredient_lookup._cache = lookup
    return _get_ingredient_lookup._cache


def get_oil_ingredients() -> Dict:
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت النباتية والحيوانية", {})


MAX_OIL_PERCENTAGE = {
    "دواجن_بادي": {"max": 8.0, "optimal": 5.0, "source": "Ross 308"},
    "دواجن_نامي": {"max": 7.0, "optimal": 4.5, "source": "Ross 308"},
    "دواجن_ناهي": {"max": 7.0, "optimal": 4.0, "source": "Ross 308"},
    "دواجن_بياض": {"max": 5.0, "optimal": 2.5, "source": "NRC 1994"},
    "أبقار_حليب_عالي": {"max": 6.0, "optimal": 4.0, "source": "NRC 2001"},
    "أبقار_حليب_متوسط": {"max": 5.0, "optimal": 3.5, "source": "NRC 2001"},
    "أبقار_حليب_منخفض": {"max": 5.0, "optimal": 3.0, "source": "NRC 2001"},
    "أغنام_تسمين_مكثف": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "ماعز_حلابة_عالي": {"max": 5.0, "optimal": 3.5, "source": "NRC 2007"},
    "إبل_حليب": {"max": 5.0, "optimal": 3.5, "source": "FAO 2010"},
    "خيول_رياضة_مكثف": {"max": 10.0, "optimal": 7.0, "source": "NRC Horses"},
    "أسماك_بادئ": {"max": 15.0, "optimal": 10.0, "source": "NRC Fish"},
}


def get_oil_standard(k: str) -> Dict:
    return MAX_OIL_PERCENTAGE.get(k, {"max": 5.0, "optimal": 3.0, "source": "عام"})


INGREDIENT_LIMITS_BY_ANIMAL = {
    "دواجن": {
        "يوريا علفية": (0, 0),
        "نخالة قمح (ردة)": (0, 10),
        "نخالة ذرة": (0, 5),
        "تبن قمح": (0, 2),
        "قش أرز": (0, 2),
        "كسب بذور القطن": (0, 5),
        "كسب السمسم": (0, 8),
        "كسب الكانولا": (0, 8),
        "ملح الطعام": (0.2, 0.4),
        "الحجر الجيري": (0.8, 2),
        "فوسفات ثنائي الكالسيوم": (0.5, 2.5),
        "بريمكس تسمين دواجن": (0.2, 0.35),
        "بريمكس بياض": (0.2, 0.35),
        "ليسين نقي": (0, 0.5),
        "ميثيونين نقي": (0, 0.4),
    },
    "أبقار": {
        "يوريا علفية": (0, 1.5),
        "نخالة قمح (ردة)": (0, 30),
        "كسب بذور القطن": (0, 20),
        "كسب السمسم": (0, 15),
        "ملح الطعام": (0.3, 0.5),
        "بيكربونات الصوديوم": (0.5, 1),
        "الحجر الجيري": (0, 3.5),
        "فوسفات ثنائي الكالسيوم": (0, 2),
        "بريمكس أبقار": (0.15, 0.3),
        "بريمكس مجترات": (0.15, 0.3),
        "مضاد سموم فطرية": (0.05, 0.15),
    },
    "أغنام": {
        "يوريا علفية": (0, 1),
        "نخالة قمح (ردة)": (0, 25),
        "كسب بذور القطن": (0, 15),
        "ملح الطعام": (0.3, 0.5),
        "بيكربونات الصوديوم": (0.5, 1),
        "بريمكس مجترات": (0.15, 0.3),
        "الحجر الجيري": (0, 3),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "ماعز": {
        "يوريا علفية": (0, 1),
        "نخالة قمح (ردة)": (0, 25),
        "ملح الطعام": (0.3, 0.5),
        "بيكربونات الصوديوم": (0.5, 1),
        "بريمكس مجترات": (0.15, 0.3),
        "الحجر الجيري": (0, 3),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "إبل": {
        "يوريا علفية": (0, 1),
        "نخالة قمح (ردة)": (0, 20),
        "ملح الطعام": (0.3, 0.5),
        "بيكربونات الصوديوم": (0.5, 1),
        "بريمكس إبل": (0.15, 0.3),
        "الحجر الجيري": (0, 3),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "خيول": {
        "يوريا علفية": (0, 0.5),
        "نخالة قمح (ردة)": (0, 20),
        "ملح الطعام": (0.3, 0.5),
        "بريمكس خيول": (0.15, 0.3),
        "الحجر الجيري": (0, 2.5),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "أسماك": {
        "يوريا علفية": (0, 0),
        "نخالة قمح (ردة)": (0, 10),
        "ملح الطعام": (0, 0.3),
        "بريمكس أسماك": (0.15, 0.3),
        "الحجر الجيري": (0, 2),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "أرانب": {
        "يوريا علفية": (0, 0.5),
        "نخالة قمح (ردة)": (0, 20),
        "ملح الطعام": (0.3, 0.5),
        "بريمكس مجترات": (0.15, 0.3),
        "الحجر الجيري": (0, 2.5),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
}


def get_animal_limits(animal: str) -> Dict:
    return INGREDIENT_LIMITS_BY_ANIMAL.get(animal, {})


# ═══════════════════════════════════════════════════════════════════════
# الاحتياجات الغذائية
# ═══════════════════════════════════════════════════════════════════════


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


def get_cattle_requirements(
    t: str, milk_yield: float = 20.0, weight_kg: float = 500.0
) -> AnimalRequirement:
    if t == "حليب_عالي":
        dp = min(9.0 + milk_yield * 0.175, 16.0)
        return AnimalRequirement(
            round(dp, 2),
            round(dp / 0.72, 2),
            round(60 + milk_yield * 0.35, 1),
            30,
            19,
            5.5,
            8,
            round(0.55 + milk_yield * 0.003, 3),
            round(0.33 + milk_yield * 0.0015, 3),
            "أبقار حلابة عالية",
            f"حليب {milk_yield}",
        )
    if t == "حليب_متوسط":
        dp = min(8.5 + milk_yield * 0.17, 14.0)
        return AnimalRequirement(
            round(dp, 2),
            round(dp / 0.72, 2),
            round(55 + milk_yield * 0.30, 1),
            33,
            21,
            4.5,
            8,
            round(0.5 + milk_yield * 0.0025, 3),
            round(0.3 + milk_yield * 0.0012, 3),
            "أبقار حلابة متوسطة",
            f"حليب {milk_yield}",
        )
    if t == "حليب_منخفض":
        dp = min(8.0 + milk_yield * 0.16, 12.5)
        return AnimalRequirement(
            round(dp, 2),
            round(dp / 0.75, 2),
            round(50 + milk_yield * 0.25, 1),
            38,
            24,
            4,
            8.5,
            round(0.45 + milk_yield * 0.002, 3),
            round(0.28 + milk_yield * 0.001, 3),
            "أبقار حلابة منخفضة",
            f"حليب {milk_yield}",
        )
    if t == "تسمين_مكثف":
        return AnimalRequirement(11.5, 14.5, 72, 32, 20, 4.5, 7.5, 0.65, 0.38, "تسمين مكثف", "ADG >1.3")
    if t == "تسمين_عادي":
        return AnimalRequirement(9.5, 12, 65, 38, 24, 4, 7.5, 0.55, 0.32, "تسمين عادي", "ADG ~0.8")
    if t == "حمل_أخير":
        return AnimalRequirement(11.5, 14.5, 67, 35, 22, 4.2, 8, 0.7, 0.42, "حمل آخر", "شهر 7-9")
    return AnimalRequirement(7.5, 10, 53, 45, 28, 3, 8.5, 0.42, 0.26, "أبقار صيانة", "بدون إنتاج")


def get_sheep_requirements(
    t: str, is_male: bool = True, weight_kg: float = 50.0, litter_size: int = 1
) -> AnimalRequirement:
    if is_male:
        if t == "تسمين_مكثف":
            return AnimalRequirement(11.5, 14.5, 64, 28, 17, 4, 8, 0.65, 0.36, "تسمين مكثف", "ADG >250")
        if t == "تسمين_عادي":
            return AnimalRequirement(9.5, 12, 59, 33, 21, 3.6, 8, 0.55, 0.32, "تسمين عادي", "ADG ~180")
        return AnimalRequirement(8.5, 11, 55, 38, 24, 3.2, 8.5, 0.5, 0.3, "حملان تيد", "بداية")
    if t == "مرضعات":
        dp = 10.5 + (litter_size - 1) * 1.5
        return AnimalRequirement(
            round(dp, 2),
            round(dp / 0.72, 2),
            round(60 + (litter_size - 1) * 5, 1),
            30,
            19,
            4.5,
            8.5,
            round(0.65 + (litter_size - 1) * 0.1, 3),
            round(0.38 + (litter_size - 1) * 0.05, 3),
            f"نعاج مرضعات ({litter_size})",
            "",
        )
    if t == "حامل_أخير":
        return AnimalRequirement(10.5, 13.5, 62, 32, 20, 3.8, 8, 0.6, 0.35, "نعاج حامل (4-5)", "")
    if t == "حامل_متوسط":
        return AnimalRequirement(8.5, 11, 55, 38, 24, 3.4, 8, 0.5, 0.3, "نعاج حامل (1-3)", "")
    return AnimalRequirement(7.2, 9.5, 48, 45, 28, 3, 8.5, 0.42, 0.26, "نعاج صيانة", "")


def get_goat_requirements(
    t: str, is_male: bool = True, milk_yield: float = 2.0
) -> AnimalRequirement:
    if is_male:
        if t == "تسمين_جديان":
            return AnimalRequirement(11, 14, 62, 30, 19, 3.8, 8, 0.62, 0.34, "تسمين جديان", "")
        return AnimalRequirement(9, 11.5, 57, 36, 22, 3.5, 8, 0.55, 0.3, "تيوس تسمين", "")
    if t == "حلابة_عالي":
        dp = min(9.5 + milk_yield * 0.35, 13.5)
        return AnimalRequirement(
            round(dp, 2),
            round(dp / 0.72, 2),
            round(58 + milk_yield * 0.45, 1),
            29,
            18,
            4.5,
            8.5,
            round(0.6 + milk_yield * 0.008, 3),
            round(0.35 + milk_yield * 0.004, 3),
            f"عنزات حلابة ({milk_yield})",
            "",
        )
    if t == "حلابة_متوسط":
        dp = min(8.5 + milk_yield * 0.30, 12.0)
        return AnimalRequirement(
            round(dp, 2),
            round(dp / 0.72, 2),
            round(55 + milk_yield * 0.40, 1),
            32,
            20,
            4,
            8.5,
            round(0.55 + milk_yield * 0.006, 3),
            round(0.32 + milk_yield * 0.003, 3),
            f"عنزات حلابة ({milk_yield})",
            "",
        )
    if t == "حامل_أخير":
        return AnimalRequirement(10, 13, 60, 33, 21, 3.8, 8, 0.6, 0.35, "عنزات حامل", "")
    return AnimalRequirement(6.8, 9, 46, 46, 28, 3, 8.5, 0.42, 0.26, "عنزات صيانة", "")


def get_camel_requirements(
    t: str, weight_kg: float = 400.0, milk_yield: float = 5.0
) -> AnimalRequirement:
    if t == "نمو":
        return AnimalRequirement(10.5, 13.5, 60, 38, 24, 4, 8, 0.65, 0.38, "إبل نمو", f"{weight_kg}")
    if t == "تسمين":
        return AnimalRequirement(9.5, 12, 65, 35, 22, 4.5, 7.5, 0.6, 0.35, "إبل تسمين", f"{weight_kg}")
    if t == "حليب":
        dp = min(10.5 + milk_yield * 0.20, 14.0)
        return AnimalRequirement(
            round(dp, 2),
            round(dp / 0.72, 2),
            round(62 + milk_yield * 0.4, 1),
            32,
            20,
            5,
            8.5,
            round(0.7 + milk_yield * 0.006, 3),
            round(0.4 + milk_yield * 0.003, 3),
            f"إبل حلابة ({milk_yield})",
            "",
        )
    if t == "سباق":
        return AnimalRequirement(14, 17, 72, 28, 17, 6, 9, 0.85, 0.5, "إبل سباق", "طاقة عالية")
    return AnimalRequirement(7, 9, 48, 48, 30, 3.5, 9, 0.42, 0.26, "إبل صيانة", f"{weight_kg}")


def get_horse_requirements(t: str, weight_kg: float = 450.0) -> AnimalRequirement:
    if t == "رياضة_مكثف":
        return AnimalRequirement(10.5, 13.5, 70, 30, 18, 7, 7.5, 0.7, 0.4, "خيول رياضة مكثف", "")
    if t == "رياضة_عادي":
        return AnimalRequirement(9, 11.5, 63, 36, 22, 5, 7.5, 0.55, 0.32, "خيول رياضة عادي", "")
    if t == "نمو_أمهار":
        return AnimalRequirement(12, 15, 65, 30, 18, 5, 8, 0.75, 0.42, "أمهار نمو", "")
    if t == "مرضعات":
        return AnimalRequirement(12.5, 16, 68, 32, 20, 5.5, 8, 0.8, 0.45, "فرسات مرضعات", "")
    return AnimalRequirement(7.2, 9.5, 53, 46, 29, 3.5, 8, 0.45, 0.28, "خيول صيانة", "")


def get_poultry_requirements(strain: str, age_weeks: int = 1) -> AnimalRequirement:
    if strain == "لاحم":
        if age_weeks <= 1:
            return AnimalRequirement(20, 23, 76, 8, 4, 5, 6.5, 1, 0.5, "بادي", "")
        if age_weeks <= 3:
            return AnimalRequirement(18.5, 21, 74, 9, 5, 5, 6, 0.9, 0.45, "نامي", "")
        if age_weeks <= 5:
            return AnimalRequirement(17, 19.5, 75, 10, 5.5, 4.5, 6, 0.87, 0.43, "ناهي", "")
        return AnimalRequirement(16.5, 19, 75, 10, 5.5, 4.5, 6, 0.85, 0.42, "ناهي+", "")
    if age_weeks <= 6:
        return AnimalRequirement(17, 20, 72, 10, 5.5, 4, 7, 1, 0.5, "بادي بياض", "")
    if age_weeks <= 18:
        return AnimalRequirement(14.5, 17, 70, 12, 6.5, 4, 9, 1.5, 0.45, "نامي بياض", "")
    return AnimalRequirement(15.5, 18, 72, 11, 6, 4.2, 11.5, 3.8, 0.45, "بياض", "")


def get_quail_requirements(strain: str, age_weeks: int = 1) -> AnimalRequirement:
    if strain == "بياض":
        return AnimalRequirement(15, 18, 68, 11, 5.5, 4.5, 9, 2.5, 0.45, "سمان بياض", "")
    if age_weeks <= 2:
        return AnimalRequirement(20.5, 24, 74, 8, 4, 5.5, 6.5, 1, 0.55, "سمان بادي", "")
    if age_weeks <= 4:
        return AnimalRequirement(18.5, 22, 72, 9, 4.5, 5, 6, 0.9, 0.5, "سمان نامي", "")
    return AnimalRequirement(17, 20, 70, 10, 5, 4.5, 6, 0.85, 0.45, "سمان ناهي", "")


def get_fish_requirements(species: str, stage: str) -> AnimalRequirement:
    if "بادئ" in stage or "زريعة" in stage:
        return AnimalRequirement(32, 40, 72, 8, 4, 10, 11, 1.5, 0.9, f"{species} بادئ", "")
    if "نمو" in stage:
        return AnimalRequirement(25, 32, 70, 12, 6, 8, 9, 1, 0.7, f"{species} نمو", "")
    return AnimalRequirement(22, 28, 68, 13, 7, 8, 9.5, 0.9, 0.65, f"{species} تسمين", "")


def get_rabbit_requirements(t: str, weight_kg: float = 4.0) -> AnimalRequirement:
    if t == "تسمين":
        return AnimalRequirement(15, 17, 65, 25, 15, 3, 8, 0.7, 0.35, "أرانب تسمين", "ADG 40")
    if t == "حليب":
        return AnimalRequirement(18, 20, 68, 25, 15, 4, 8.5, 0.85, 0.45, "أرانب حلابة", "أمهات")
    return AnimalRequirement(12, 14, 60, 30, 20, 2.5, 8.5, 0.6, 0.3, "أرانب صيانة", "")


def requirement_to_standard(req: AnimalRequirement) -> Dict:
    return {
        "CP": req.CP,
        "DP": req.DP,
        "SE": req.SE,
        "NDF": req.NDF,
        "ADF": req.ADF,
        "EE": req.EE,
        "ASH": req.ASH,
        "Ca": req.Ca,
        "P": req.P,
    }


# ═══════════════════════════════════════════════════════════════════════
# الحسابات والتحليل والتقييم
# ═══════════════════════════════════════════════════════════════════════


def compute_formula_nutrients(formula: Dict) -> Dict:
    totals = {k: 0.0 for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P", "Lys", "Met"]}
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


def compute_total_oil_percentage(formula: Dict) -> float:
    oils = set(get_oil_ingredients().keys())
    return sum(p for i, p in formula.items() if i in oils)


def evaluate_difference(pct_diff: float, standard_value: Optional[float] = None) -> Dict:
    if standard_value is not None and standard_value == 0:
        if abs(pct_diff) < 0.001:
            return {"label": "🎯 مطابق", "color": "#0d5302", "bg": "#c8e6c9", "score": 100}
        return {"label": "⚠️ صفر", "color": "#ef6c00", "bg": "#fff3e0", "score": 40}
    a = abs(pct_diff)
    if a <= 0.5:
        return {"label": "🎯 مطابق", "color": "#0d5302", "bg": "#c8e6c9", "score": 100}
    if a <= 2:
        return {"label": "🌟 ممتاز", "color": "#1b5e20", "bg": "#dcedc8", "score": 95}
    if a <= 5:
        return {"label": "✅ جيد جداً", "color": "#2e7d32", "bg": "#e8f5e9", "score": 85}
    if a <= 10:
        return {"label": "🟢 جيد", "color": "#558b2f", "bg": "#f1f8e9", "score": 75}
    if a <= 15:
        return {"label": "⭐ مقبول", "color": "#f9a825", "bg": "#fff8e1", "score": 65}
    if a <= 25:
        return {"label": "⚠️ بتحفظ", "color": "#ef6c00", "bg": "#fff3e0", "score": 50}
    if a <= 40:
        return {"label": "🟠 ضعيف", "color": "#e65100", "bg": "#ffe0b2", "score": 35}
    return {"label": "❌ غير مطابق", "color": "#c62828", "bg": "#ffebee", "score": 20}


def evaluate_quality_weighted(formula: Dict, targets: Dict, animal_type: str, basis: str = "DP"):
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


def get_default_selections(animal_type: str, production_type, requirement=None) -> set:
    d = {"ملح الطعام", "مضاد سموم فطرية"}
    if animal_type != "دواجن":
        d |= {"الحجر الجيري", "فوسفات ثنائي الكالسيوم"}
    if animal_type in ("أبقار", "أغنام", "ماعز", "إبل"):
        d.add("بيكربونات الصوديوم")
    if animal_type in ("دواجن", "سمان"):
        d.add("بريمكس بياض" if "بياض" in str(production_type) else "بريمكس تسمين دواجن")
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


def _normalize_ingredient_name(name: str) -> str:
    name = re.sub(r"\s+", " ", str(name).strip())
    lookup = _get_ingredient_lookup()
    if name in lookup:
        return name
    for lib in lookup.keys():
        if lib.lower() in name.lower() or name.lower() in lib.lower():
            return lib
    kw = {
        "ذره": "ذرة صفراء",
        "ذرة": "ذرة صفراء",
        "صويا": "كسب فول صويا 44%",
        "شعير": "شعير مطحون",
        "قمح": "قمح محلي",
        "نخاله": "نخالة قمح (ردة)",
        "نخالة": "نخالة قمح (ردة)",
        "ملح": "ملح الطعام",
        "حجر": "الحجر الجيري",
        "فوسفات": "فوسفات ثنائي الكالسيوم",
        "يوريا": "يوريا علفية",
    }
    for k, v in kw.items():
        if k in name.lower():
            return v
    return name


def match_ingredient_name(text: str) -> Optional[str]:
    if not text:
        return None
    tl = text.strip().lower()
    lookup = _get_ingredient_lookup()
    for name in lookup.keys():
        if name.lower() == tl:
            return name
    best_match = None
    best_len = 0
    for name in lookup.keys():
        if name.lower() in tl and len(name) > best_len:
            best_match = name
            best_len = len(name)
    if best_match:
        return best_match
    kw = {
        "ذرة": "ذرة صفراء",
        "ذره": "ذرة صفراء",
        "صويا": "كسب فول صويا 44%",
        "شعير": "شعير مطحون",
        "قمح": "قمح محلي",
        "نخالة": "نخالة قمح (ردة)",
        "نخاله": "نخالة قمح (ردة)",
        "ملح": "ملح الطعام",
        "حجر": "الحجر الجيري",
        "فوسفات": "فوسفات ثنائي الكالسيوم",
        "يوريا": "يوريا علفية",
    }
    for k, v in kw.items():
        if k in tl:
            return v
    return None


def _parse_ingredients_from_text(full_text: str) -> Dict:
    if not full_text:
        return {}
    fixes = {"٥": "5", "٦": "6", "٧": "7", "٨": "8", "٩": "9", "٠": "0", "١": "1", "٢": "2", "٣": "3", "٤": "4"}
    text = full_text
    for old, new in fixes.items():
        text = text.replace(old, new)
    text = text.replace("٪", "%")
    lookup = _get_ingredient_lookup()
    all_names = sorted(lookup.keys(), key=len, reverse=True)
    ingredients = {}
    for line in text.split("\n"):
        line = line.strip()
        if len(line) < 3:
            continue
        matched_any = False
        for ing_name in all_names:
            if ing_name in line:
                idx = line.find(ing_name) + len(ing_name)
                remainder = line[idx:].strip()
                num_match = re.search(
                    r"[:\-=:\.\s]*(\d{1,3}\.?\d{0,2})\s*(?:%|كجم|كج|kg|جرام|g)?",
                    remainder,
                )
                if num_match:
                    try:
                        val = float(num_match.group(1))
                        if 0.01 <= val <= 100:
                            ingredients[ing_name] = round(val, 2)
                            matched_any = True
                            break
                    except ValueError:
                        continue
        if not matched_any:
            kw_match = re.search(r"(\d{1,3}\.?\d{0,2})\s*%?", line)
            if kw_match:
                try:
                    val = float(kw_match.group(1))
                except ValueError:
                    continue
                if 0.01 <= val <= 100:
                    name_part = line[: kw_match.start()].strip()
                    name_part = re.sub(r"[:\-=:\.\s]+$", "", name_part)
                    if len(name_part) > 2:
                        matched = match_ingredient_name(name_part)
                        if matched:
                            ingredients[matched] = round(val, 2)
    return ingredients


def auto_formulate_smart(
    available_ingredients,
    prices,
    custom_standard,
    standard_key="",
    basis="DP",
    min_quality=70.0,
    animal_type="",
    production_type="",
) -> Dict:
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "SCIPY غير متوفرة"}
    available_ingredients = [_normalize_ingredient_name(i) for i in available_ingredients]
    available_ingredients = list(dict.fromkeys(available_ingredients))
    lookup = _get_ingredient_lookup()
    ing_data = {i: lookup[i] for i in available_ingredients if i in lookup}
    valid = list(ing_data.keys())
    if len(valid) < 2:
        return {"success": False, "message": "اختر مكونين على الأقل"}
    is_ruminant = animal_type in ("أبقار", "أغنام", "ماعز", "إبل")
    is_poultry = animal_type in ("دواجن", "سمان")
    n = len(valid)
    c = [prices.get(i, 300.0) for i in valid]
    rows = {nut: [ing_data[i].get(nut, 0) for i in valid] for nut in ["CP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P", "Lys", "Met"]}
    rows["DP"] = [ing_data[i].get("CP", 0) * ing_data[i].get("DC", 0) for i in valid]
    target_key = "DP" if basis == "DP" else "CP"
    target_protein = custom_standard.get(target_key, 15.0)
    target_ca = custom_standard.get("Ca", 0)
    target_p = custom_standard.get("P", 0)
    target_se = custom_standard.get("SE", 0)
    target_ndf = custom_standard.get("NDF", 0)
    target_adf = custom_standard.get("ADF", 0)
    MIN_USE = 0.5
    limits = get_animal_limits(animal_type)
    bounds = []
    for ing in valid:
        lim = limits.get(ing, (0.0, 100.0))
        lb = max(MIN_USE, lim[0])
        ub = min(60.0, lim[1])
        if lb > ub:
            lb = ub
        bounds.append((lb, ub))
    energy_sources_idx = [i for i, ing in enumerate(valid) if ing_data[ing].get("SE", 0) > 40 and ing_data[ing].get("CP", 0) < 20]
    protein_sources_idx = [i for i, ing in enumerate(valid) if ing_data[ing].get("CP", 0) >= 20]
    A_eq_base = [[1.0] * n, rows[target_key]]
    b_eq_base = [100.0, target_protein * 100.0]
    A_ub_base, b_ub_base = [], []
    target_me = (target_se * 41) if target_se > 0 else 2500
    if target_me > 0:
        A_ub_base.append([-x * 41 for x in rows["SE"]])
        b_ub_base.append(-target_me * 0.90)
    if energy_sources_idx and protein_sources_idx:
        balance_row = [0.0] * n
        for i in energy_sources_idx:
            balance_row[i] = 1.0
        for i in protein_sources_idx:
            balance_row[i] = -1.0
        A_ub_base.append([-x for x in balance_row])
        b_ub_base.append(-10.0)
    if energy_sources_idx:
        e_row = [1.0 if i in energy_sources_idx else 0.0 for i in range(n)]
        A_ub_base.append([-x for x in e_row])
        b_ub_base.append(-40.0)
    if protein_sources_idx:
        p_row = [1.0 if i in protein_sources_idx else 0.0 for i in range(n)]
        A_ub_base.append(p_row)
        b_ub_base.append(40.0)
    if target_ca > 0 and target_p > 0:
        if is_poultry:
            ca_p_min, ca_p_max = 1.5, 2.2
        elif is_ruminant:
            ca_p_min, ca_p_max = 1.4, 2.5
        else:
            ca_p_min, ca_p_max = 1.5, 2.0
        A_ub_base.append([-rows["Ca"][i] + ca_p_min * rows["P"][i] for i in range(n)])
        b_ub_base.append(0)
        A_ub_base.append([rows["Ca"][i] - ca_p_max * rows["P"][i] for i in range(n)])
        b_ub_base.append(0)
    if target_se > 0:
        A_ub_base.append([-x for x in rows["SE"]])
        b_ub_base.append(-target_se * 0.92 * 100.0)
    if target_ndf > 0 and is_ruminant:
        A_ub_base.append([-x for x in rows["NDF"]])
        b_ub_base.append(-target_ndf * 0.85 * 100.0)
        A_ub_base.append(rows["NDF"])
        b_ub_base.append(target_ndf * 1.20 * 100.0)
    if target_adf > 0:
        A_ub_base.append(rows["ADF"])
        mult = 1.30 if is_ruminant else (1.10 if is_poultry else 1.20)
        b_ub_base.append(target_adf * mult * 100.0)
    oil_std = get_oil_standard(standard_key)
    oil_ind = [1.0 if i in get_oil_ingredients() else 0.0 for i in valid]
    if sum(oil_ind) > 0:
        A_ub_base.append(oil_ind)
        b_ub_base.append(oil_std["max"] * 100.0)
    strategies = [
        ("دقيق 100%", 1.00),
        ("مرن 97%", 0.97),
        ("مرن 95%", 0.95),
        ("مرن 92%", 0.92),
        ("مرن 90%", 0.90),
        ("مرن 85%", 0.85),
        ("مرن 80%", 0.80),
        ("طوارئ قصوى", 0.75),
    ]
    best, best_q = None, 0.0
    attempts = []
    for label, mult in strategies:
        try:
            A_eq = list(A_eq_base)
            b_eq = [100.0, target_protein * 100.0 * mult]
            res = linprog(
                c,
                A_ub=list(A_ub_base),
                b_ub=list(b_ub_base),
                A_eq=A_eq,
                b_eq=b_eq,
                bounds=bounds,
                method="highs",
                options={"presolve": True, "time_limit": 15},
            )
            if res.success:
                formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.01}
                q, actual = evaluate_quality_weighted(formula, custom_standard, animal_type, basis)
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
                attempts.append(f"✅ {label}: {q:.1f}%")
                if q >= 92:
                    break
            else:
                attempts.append(f"❌ {label}")
        except Exception as e:
            attempts.append(f"⚠️ {label}: {e}")
            continue
    if best:
        if not best["meets_standard"]:
            best["warning"] = f"⚠️ جودة {best_q:.1f}% < {min_quality}%"
        return best
    fallback_formula = {}
    remaining = 100.0
    oil_names = [ing for ing in valid if ing in get_oil_ingredients()]
    if oil_names:
        oil_share = min(3.0, 100.0 / (len(valid) + 2))
        for ing in oil_names:
            fallback_formula[ing] = oil_share / len(oil_names)
            remaining -= fallback_formula[ing]
    salt_names = [ing for ing in valid if "ملح" in ing or "حجر" in ing]
    if salt_names:
        salt_share = min(2.0, remaining / (len(valid) + 1))
        for ing in salt_names:
            fallback_formula[ing] = salt_share / len(salt_names)
            remaining -= fallback_formula[ing]
    other = [ing for ing in valid if ing not in fallback_formula]
    if other:
        for ing in other:
            fallback_formula[ing] = remaining / len(other)
    total = sum(fallback_formula.values())
    if total > 0:
        for ing in fallback_formula:
            fallback_formula[ing] *= 100.0 / total
    q, actual = evaluate_quality_weighted(fallback_formula, custom_standard, animal_type, basis)
    return {
        "success": True,
        "formula": fallback_formula,
        "cost": sum(fallback_formula[ing] / 100 * prices.get(ing, 300) for ing in fallback_formula),
        "actual_nutrients": actual,
        "quality_score": q,
        "strategy": "🆘 طوارئ",
        "meets_standard": q >= min_quality,
        "targets": custom_standard,
        "basis": basis,
        "oil_std": oil_std,
        "total_oil": compute_total_oil_percentage(fallback_formula),
        "warning": f"⚠️ حل طوارئ — جودة {q:.1f}%",
        "attempts_log": attempts,
    }


def _get_requirement_for_nlp(animal_type: str, production_type: str) -> Dict:
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
        elif animal_type == "سمان":
            req = get_quail_requirements("بياض" if "بياض" in production_type else "لاحم")
        elif animal_type == "أسماك":
            req = get_fish_requirements("البلطي النيلي", production_type)
        elif animal_type == "أرانب":
            req = get_rabbit_requirements(production_type)
        else:
            req = get_cattle_requirements("حليب_متوسط")
        return {"ME": req.SE * 41, "CP": req.CP, "DP": req.DP}
    except Exception:
        return {"ME": 3000.0, "CP": 18.0, "DP": 14.0}


def _diagnose_nlp_failure(me_vals, cp_vals, bounds, target_me, target_cp) -> Dict:
    hi = np.array([b[1] for b in bounds])
    max_me = float(np.dot(me_vals, hi)) * 100
    max_cp = float(np.dot(cp_vals, hi)) * 100
    issues = []
    if max_me < target_me:
        issues.append(f"⚡ أقصى ME = {max_me:.0f} < {target_me:.0f}")
    if max_cp < target_cp:
        issues.append(f"🧬 أقصى CP = {max_cp:.2f}% < {target_cp:.2f}%")
    return {"issues": issues, "max_me": round(max_me, 1), "max_cp": round(max_cp, 2), "tips": ["➕ أضف طاقة", "➕ أضف بروتين"]}


def nlp_optimize_feed(
    ingredient_names,
    ingredient_data,
    prices,
    animal_type="أبقار",
    production_type="حليب_عالي",
    target_me=None,
    target_cp=None,
    price_product=2.5,
    max_per_ing=0.6,
) -> Dict:
    n = len(ingredient_names)
    if n < 2:
        return {"success": False, "message": "يلزم مكونان"}
    if not SCIPY_AVAILABLE or minimize is None:
        return {"success": False, "message": "SCIPY غير متوفرة"}
    req = _get_requirement_for_nlp(animal_type, production_type)
    if target_me is None:
        target_me = req["ME"]
    if target_cp is None:
        target_cp = req["CP"]
    me_vals = np.array([ingredient_data[i].get("SE", 0) * 41 for i in ingredient_names])
    cp_vals = np.array([ingredient_data[i].get("CP", 0) for i in ingredient_names])
    cost_vals = np.array([prices.get(i, 300.0) / 1000.0 for i in ingredient_names])
    MIN_USE = 0.005
    animal_limits = get_animal_limits(animal_type)
    bounds = []
    for ing in ingredient_names:
        lim = animal_limits.get(ing)
        if lim:
            lb = max(MIN_USE, lim[0] / 100.0)
            ub = min(max_per_ing, lim[1] / 100.0)
        else:
            lb, ub = MIN_USE, max_per_ing
        if lb > ub:
            lb = ub
        bounds.append((lb, ub))
    energy_idx = [i for i, ing in enumerate(ingredient_names) if ingredient_data[ing].get("SE", 0) > 40 and ingredient_data[ing].get("CP", 0) < 20]
    protein_idx = [i for i, ing in enumerate(ingredient_names) if ingredient_data[ing].get("CP", 0) >= 20]
    oils_idx = [i for i, ing in enumerate(ingredient_names) if ing in get_oil_ingredients()]
    oil_max = get_oil_standard(f"{animal_type}_{production_type}")["max"] / 100.0

    def objective(x):
        me = np.dot(me_vals, x)
        cp = np.dot(cp_vals, x)
        quality = (me / target_me) * (cp / target_cp)
        return -(price_product * quality - np.dot(cost_vals, x))

    def objective_penalty(x, lam=500.0):
        base = objective(x)
        pen_me = lam * max(0.0, target_me - np.dot(me_vals, x)) ** 2
        pen_cp = lam * max(0.0, target_cp - np.dot(cp_vals, x)) ** 2
        pen_oil = lam * max(0.0, sum(x[i] for i in oils_idx) - oil_max) ** 2
        pen_sum = 1000.0 * (np.sum(x) - 1.0) ** 2
        pen_balance = 0.0
        if energy_idx and protein_idx:
            e_share = sum(x[i] for i in energy_idx)
            p_share = sum(x[i] for i in protein_idx)
            pen_balance = lam * max(0.0, p_share - e_share + 0.10) ** 2
        return base + pen_me + pen_cp + pen_oil + pen_sum + pen_balance

    lp_warm = None
    if linprog is not None:
        try:
            A_ub = [list(-me_vals * 41), list(-cp_vals)]
            b_ub = [-target_me * 0.90 / 100.0, -target_cp * 0.95 / 100.0]
            if oils_idx:
                A_ub.append([1.0 if i in oils_idx else 0.0 for i in range(n)])
                b_ub.append(oil_max)
            if energy_idx and protein_idx:
                bal_row = [0.0] * n
                for i in energy_idx:
                    bal_row[i] = 1.0
                for i in protein_idx:
                    bal_row[i] = -1.0
                A_ub.append([-x for x in bal_row])
                b_ub.append(-0.10)
            lp_res = linprog(
                np.zeros(n),
                A_ub=A_ub,
                b_ub=b_ub,
                A_eq=[[1.0] * n],
                b_eq=[1.0],
                bounds=bounds,
                method="highs",
                options={"presolve": True, "time_limit": 8},
            )
            if lp_res.success:
                lp_warm = np.clip(lp_res.x, 0, None)
                s = lp_warm.sum()
                if s > 0:
                    lp_warm = lp_warm / s
        except Exception:
            lp_warm = None

    def make_initial_points():
        pts = []
        if lp_warm is not None:
            pts.append(lp_warm.copy())
        pts.append(np.ones(n) / n)
        pts.append(np.eye(n)[int(np.argmin(cost_vals))])
        pts.append(np.eye(n)[int(np.argmax(cp_vals))])
        pts.append(np.eye(n)[int(np.argmax(me_vals))])
        if energy_idx and protein_idx:
            mix1 = np.zeros(n)
            e = energy_idx[0]
            p = protein_idx[0]
            mix1[e] = 0.60
            mix1[p] = 0.30
            others = [i for i in range(n) if i not in (e, p)]
            if others:
                for i in others:
                    mix1[i] = 0.10 / len(others)
            pts.append(mix1)
        rng = np.random.RandomState(42)
        for _ in range(3):
            p_ = rng.rand(n)
            p_ /= p_.sum()
            pts.append(p_)
        return pts

    relaxation_levels = [
        ("صارم 100%", 1.00, True),
        ("خفيف 97%", 0.97, True),
        ("مرن 95%", 0.95, True),
        ("مرن 92%", 0.92, True),
        ("مرن 90%", 0.90, True),
        ("مرن 85%", 0.85, True),
        ("مرن 80%", 0.80, True),
        ("طوارئ 70%", 0.70, False),
    ]
    best = None
    attempts_log = []
    for level_name, mult, enforce_balance in relaxation_levels:
        tme = target_me * mult
        tcp = target_cp * mult
        constraints = [
            {"type": "eq", "fun": lambda x: np.sum(x) - 1.0},
            {"type": "ineq", "fun": lambda x, t=tme: np.dot(me_vals, x) - t / 100.0},
            {"type": "ineq", "fun": lambda x, t=tcp: np.dot(cp_vals, x) - t / 100.0},
        ]
        if oils_idx:
            constraints.append({"type": "ineq", "fun": lambda x: oil_max - sum(x[i] for i in oils_idx)})
        if enforce_balance and energy_idx and protein_idx:
            constraints.append(
                {
                    "type": "ineq",
                    "fun": lambda x: sum(x[i] for i in energy_idx) - sum(x[i] for i in protein_idx) - 0.05,
                }
            )
        for x0 in make_initial_points():
            x0 = np.clip(x0, [b[0] for b in bounds], [b[1] for b in bounds])
            s = x0.sum()
            if s <= 0:
                continue
            x0 = x0 / s
            try:
                res = minimize(
                    objective,
                    x0,
                    method="SLSQP",
                    bounds=bounds,
                    constraints=constraints,
                    options={"maxiter": 1000, "ftol": 1e-8},
                )
                if not res.success:
                    attempts_log.append((level_name, "SLSQP فشل", False))
                    continue
                x_norm = np.clip(res.x, 0, None)
                ss = x_norm.sum()
                if ss <= 0:
                    continue
                x_norm = x_norm / ss
                actual_me = float(np.dot(me_vals, x_norm)) * 100
                actual_cp = float(np.dot(cp_vals, x_norm)) * 100
                if actual_me >= tme * 0.98 and actual_cp >= tcp * 0.98:
                    best = (res, x_norm, level_name, mult, actual_me, actual_cp)
                    attempts_log.append((level_name, "✅ نجح", True))
                    break
                attempts_log.append((level_name, f"قيود (ME={actual_me:.0f})", False))
            except Exception as e:
                attempts_log.append((level_name, f"استثناء: {e}", False))
                continue
        if best:
            break

    if not best:
        for x0 in make_initial_points():
            try:
                x0 = np.clip(x0, [b[0] for b in bounds], [b[1] for b in bounds])
                s = x0.sum()
                if s <= 0:
                    continue
                x0 = x0 / s
                res = minimize(
                    objective_penalty,
                    x0,
                    method="SLSQP",
                    bounds=bounds,
                    options={"maxiter": 3000, "ftol": 1e-5},
                )
                x_norm = np.clip(res.x, 0, None)
                ss = x_norm.sum()
                if ss <= 0:
                    continue
                x_norm = x_norm / ss
                best = (
                    res,
                    x_norm,
                    "عقوبات Penalty",
                    1.0,
                    float(np.dot(me_vals, x_norm)) * 100,
                    float(np.dot(cp_vals, x_norm)) * 100,
                )
                break
            except Exception:
                continue

    if not best:
        diag = _diagnose_nlp_failure(me_vals, cp_vals, bounds, target_me, target_cp)
        return {
            "success": False,
            "message": "لا يوجد حل",
            "diagnosis": diag,
            "attempts_log": attempts_log[-20:],
            "animal_type": animal_type,
            "target_me": target_me,
            "target_cp": target_cp,
        }

    res, x_opt, level_name, mult, actual_me, actual_cp = best
    x_pct = x_opt * 100.0
    formula = {name: round(float(x_pct[i]), 2) for i, name in enumerate(ingredient_names) if x_pct[i] > 0.05}
    final_cost = float(np.dot(cost_vals, x_opt))
    me_ratio = actual_me / target_me
    cp_ratio = actual_cp / target_cp
    max_profit = float(price_product * (me_ratio * cp_ratio) - final_cost)
    warning_parts = []
    if mult < 1.0:
        warning_parts.append(f"⚠️ خُففت القيود إلى {mult * 100:.0f}%")
    if mult < 0.85:
        warning_parts.append("🟠 حل طوارئ")
    e_share = sum(formula.get(ing, 0) for i, ing in enumerate(ingredient_names) if i in energy_idx)
    p_share = sum(formula.get(ing, 0) for i, ing in enumerate(ingredient_names) if i in protein_idx)
    if p_share > e_share:
        warning_parts.append(f"⚠️ بروتين ({p_share:.1f}%) > طاقة ({e_share:.1f}%)")
    final_warning = "\n".join(warning_parts) if warning_parts else None
    return {
        "success": True,
        "formula": formula,
        "x_opt": x_opt.tolist(),
        "final_cost": final_cost,
        "final_me": actual_me,
        "final_cp": actual_cp,
        "target_me": float(target_me),
        "target_cp": float(target_cp),
        "max_profit": max_profit,
        "iterations": int(getattr(res, "nit", 0)),
        "strategy": level_name,
        "relaxation_mult": mult,
        "warning": final_warning,
        "animal_type": animal_type,
        "production_type": production_type,
        "attempts_log": attempts_log,
        "energy_share_pct": round(e_share, 1),
        "protein_share_pct": round(p_share, 1),
    }


def analyze_existing_formula(formula: Dict, animal_type: str, production_type: str) -> Dict:
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
        elif animal_type == "سمان":
            req = get_quail_requirements("بياض" if "بياض" in production_type else "لاحم")
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
    labels = {
        "CP": "بروتين خام",
        "DP": "بروتين مهضوم",
        "SE": "طاقة SE",
        "NDF": "NDF",
        "ADF": "ADF",
        "EE": "دهن",
        "ASH": "رماد",
        "Ca": "Ca",
        "P": "P",
        "Lys": "Lys",
        "Met": "Met",
    }
    comparison = []
    for k, sv in standard.items():
        if sv == 0:
            continue
        cv = actual.get(k, 0)
        diff = cv - sv
        pct = (diff / sv * 100) if sv else 0
        ev = evaluate_difference(pct, standard_value=sv)
        comparison.append(
            {
                "key": k,
                "العنصر": labels.get(k, k),
                "المعيار": sv,
                "المحسوب": cv,
                "الفرق": diff,
                "الفرق %": pct,
                "التقييم": ev["label"],
                "score": ev["score"],
            }
        )
    quality, _ = evaluate_quality_weighted(normalized, standard, animal_type)
    ca = actual.get("Ca", 0)
    p = actual.get("P", 0)
    ca_p = ca / p if p > 0 else 0
    lookup = _get_ingredient_lookup()
    energy_ings = [ing for ing in normalized if lookup.get(ing, {}).get("SE", 0) > 40 and lookup.get(ing, {}).get("CP", 0) < 20]
    protein_ings = [ing for ing in normalized if lookup.get(ing, {}).get("CP", 0) >= 20]
    energy_share = sum(normalized[ing] for ing in energy_ings)
    protein_share = sum(normalized[ing] for ing in protein_ings)
    cost = sum(normalized.get(ing, 0) / 100 * lookup.get(ing, {}).get("price", 300) for ing in normalized)
    refs = get_references(animal_type, production_type)
    return {
        "success": True,
        "formula": normalized,
        "original": dict(formula),
        "standard": standard,
        "actual": actual,
        "comparison": comparison,
        "quality_score": quality,
        "ca_p_ratio": ca_p,
        "energy_share_pct": round(energy_share, 1),
        "protein_share_pct": round(protein_share, 1),
        "cost_per_ton": round(cost, 2),
        "requirement_name": req.name_ar,
        "requirement_note": req.note,
        "animal_type": animal_type,
        "production_type": production_type,
        "references": refs,
        "total_oil": compute_total_oil_percentage(normalized),
    }


MILK_REPLACER_STANDARDS = {
    "عجول (Calves)": {"CP": 24, "Fat": 20, "Lactose": 45, "Ca": 0.85, "P": 0.7, "Lys": 2.2, "Met": 0.65, "source": "NRC Dairy Cattle", "Ca_P_optimal": (1.2, 1.5)},
    "حملان (Lambs)": {"CP": 24, "Fat": 24, "Lactose": 40, "Ca": 0.9, "P": 0.7, "Lys": 2.4, "Met": 0.7, "source": "NRC Small Ruminants", "Ca_P_optimal": (1.2, 1.6)},
    "جديان (Goat Kids)": {"CP": 24, "Fat": 24, "Lactose": 42, "Ca": 0.9, "P": 0.7, "Lys": 2.3, "Met": 0.7, "source": "NRC Small Ruminants", "Ca_P_optimal": (1.2, 1.6)},
    "إبل (Camels)": {"CP": 26, "Fat": 28, "Lactose": 38, "Ca": 0.95, "P": 0.75, "Lys": 2.5, "Met": 0.8, "source": "FAO Camel", "Ca_P_optimal": (1.2, 1.5)},
    "أمهار (Foals)": {"CP": 22, "Fat": 18, "Lactose": 48, "Ca": 1.0, "P": 0.8, "Lys": 2.1, "Met": 0.6, "source": "NRC Horses", "Ca_P_optimal": (1.2, 1.4)},
}

MILK_REPLACER_INGREDIENTS = {
    "حليب مجفف منزوع الدسم": {"CP": 34, "Fat": 1, "Lactose": 52, "Ca": 1.3, "P": 1, "Lys": 2.7, "Met": 0.9, "price": 3200, "max": 60},
    "حليب مجفف كامل الدسم": {"CP": 26, "Fat": 28, "Lactose": 38, "Ca": 0.95, "P": 0.75, "Lys": 2.1, "Met": 0.65, "price": 3800, "max": 70},
    "شرش حليب مجفف": {"CP": 12, "Fat": 1.5, "Lactose": 75, "Ca": 0.9, "P": 0.75, "Lys": 0.9, "Met": 0.2, "price": 1800, "max": 35},
    "بروتين شرش WPC 80%": {"CP": 80, "Fat": 5, "Lactose": 8, "Ca": 0.5, "P": 0.3, "Lys": 7.5, "Met": 1.6, "price": 8500, "max": 25},
    "مركز بروتين صويا": {"CP": 66, "Fat": 1, "Lactose": 0, "Ca": 0.2, "P": 0.8, "Lys": 4.2, "Met": 0.9, "price": 2800, "max": 15},
    "زيت جوز الهند": {"CP": 0, "Fat": 100, "Lactose": 0, "Ca": 0, "P": 0, "Lys": 0, "Met": 0, "price": 2200, "max": 15},
    "زيت النخيل": {"CP": 0, "Fat": 100, "Lactose": 0, "Ca": 0, "P": 0, "Lys": 0, "Met": 0, "price": 1200, "max": 15},
    "لاكتوز نقي": {"CP": 0, "Fat": 0, "Lactose": 100, "Ca": 0, "P": 0, "Lys": 0, "Met": 0, "price": 1400, "max": 25},
    "ليسين L-Lysine": {"CP": 94, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0, "Lys": 94, "Met": 0, "price": 4200, "max": 1},
    "ميثيونين": {"CP": 58, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0, "Lys": 0, "Met": 58, "price": 5800, "max": 0.8},
    "بريمكس فيتامينات": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 5, "P": 3, "Lys": 0, "Met": 0, "price": 6500, "max": 1},
    "كالسيوم كربونات": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 38, "P": 0, "Lys": 0, "Met": 0, "price": 200, "max": 2.5},
    "فوسفات ثنائي الكالسيوم": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 23, "P": 18, "Lys": 0, "Met": 0, "price": 1100, "max": 2.5},
    "ملح طعام": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0, "Lys": 0, "Met": 0, "price": 150, "max": 0.5},
}


def formulate_milk_replacer(animal: str, volume: float = 100.0, selected=None) -> Dict:
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "SCIPY غير متوفرة"}
    std = MILK_REPLACER_STANDARDS.get(animal)
    if not std:
        return {"success": False, "message": "حيوان غير مدعوم"}
    valid = [i for i in (selected or list(MILK_REPLACER_INGREDIENTS.keys())) if i in MILK_REPLACER_INGREDIENTS]
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
    base_bounds = [(0, MILK_REPLACER_INGREDIENTS[i].get("max", 100)) for i in valid]
    s1_ub = [
        (lac, std["Lactose"] * 1.15 * 100),
        ([-x for x in lac], -std["Lactose"] * 0.85 * 100),
        ([-x for x in lys], -std["Lys"] * 0.70 * 100),
        ([-x for x in met], -std["Met"] * 0.70 * 100),
        ([-x for x in ca], -std["Ca"] * 0.85 * 100),
        ([-x for x in p], -std["P"] * 0.85 * 100),
    ]
    s2_ub = s1_ub[:2] + s1_ub[4:]
    s3_ub = [
        (cp, std["CP"] * 1.05 * 100),
        ([-x for x in cp], -std["CP"] * 0.95 * 100),
        (fat, std["Fat"] * 1.05 * 100),
        ([-x for x in fat], -std["Fat"] * 0.95 * 100),
    ]
    s4_ub = [
        (cp, std["CP"] * 1.15 * 100),
        ([-x for x in cp], -std["CP"] * 0.85 * 100),
        (fat, std["Fat"] * 1.30 * 100),
        ([-x for x in fat], -std["Fat"] * 0.50 * 100),
    ]
    strategies = [
        ("S1", [[1] * n, cp, fat], [100, std["CP"] * 100, std["Fat"] * 100], [u for u, _ in s1_ub], [b for _, b in s1_ub]),
        ("S2", [[1] * n, cp, fat], [100, std["CP"] * 100, std["Fat"] * 100], [u for u, _ in s2_ub], [b for _, b in s2_ub]),
        ("S3", [[1] * n], [100], [u for u, _ in s3_ub], [b for _, b in s3_ub]),
        ("S4", [[1] * n], [100], [u for u, _ in s4_ub], [b for _, b in s4_ub]),
    ]
    best = None
    best_effective = 0.0
    for label, A_eq, b_eq, A_ub, b_ub in strategies:
        try:
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=base_bounds, method="highs", options={"presolve": True, "time_limit": 10})
            if not res.success:
                continue
            formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
            used = sum(1 for v in formula.values() if v > 0.5)
            used_pct = used / n * 100
            actual = {k: 0.0 for k in ["CP", "Fat", "Lactose", "Ca", "P", "Lys", "Met"]}
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
            util_factor = 1.0 if used_pct >= min_util * 100 else used_pct / (min_util * 100)
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
        return {"success": False, "message": "لا يوجد حل"}
    warning = f"⚠️ تم استخدام {best['used_count']}/{n}" if best["used_pct"] < min_util * 100 else None
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
        "targets": {k: std.get(k, 0) for k in ["CP", "Fat", "Lactose", "Ca", "P", "Lys", "Met"]},
    }


# ═══════════════════════════════════════════════════════════════════════
# ✅ شريط القياس بأسهم دقيقة على الصورة
# ═══════════════════════════════════════════════════════════════════════

WEIGHT_TAPE_CONFIG = {
    "أبقار": {
        "hg_min": 100.0, "hg_max": 260.0, "hg_default": 180.0,
        "bl_min": 100.0, "bl_max": 220.0, "bl_default": 150.0,
        "hg_label": "محيط الصدر (سم)", "bl_label": "طول الجسم (سم)",
        "hg_tip": "خلف الأرجل الأمامية مباشرة", "bl_tip": "من مقدمة الكتف إلى عظم الحوض",
        "source": "Schaeffer (1978)", "accuracy": "±5%",
        "calc": lambda hg, bl: (hg**2 * bl) / 10840.0,
    },
    "أغنام": {
        "hg_min": 40.0, "hg_max": 120.0, "hg_default": 75.0,
        "bl_min": 40.0, "bl_max": 100.0, "bl_default": 65.0,
        "hg_label": "محيط الصدر (سم)", "bl_label": "طول الجسم (سم)",
        "hg_tip": "خلف الأرجل الأمامية", "bl_tip": "من الكتف للحوض",
        "source": "Schaeffer (1978)", "accuracy": "±7%",
        "calc": lambda hg, bl: (hg**2 * bl) / 10840.0,
    },
    "ماعز": {
        "hg_min": 35.0, "hg_max": 110.0, "hg_default": 70.0,
        "bl_min": 35.0, "bl_max": 95.0, "bl_default": 62.0,
        "hg_label": "محيط الصدر (سم)", "bl_label": "طول الجسم (سم)",
        "hg_tip": "خلف الأرجل الأمامية", "bl_tip": "من الكتف للحوض",
        "source": "Schaeffer (1978)", "accuracy": "±7%",
        "calc": lambda hg, bl: (hg**2 * bl) / 10840.0,
    },
    "إبل": {
        "hg_min": 130.0, "hg_max": 280.0, "hg_default": 210.0,
        "bl_min": 100.0, "bl_max": 220.0, "bl_default": 155.0,
        "hg_label": "محيط الصدر (سم)", "bl_label": "طول الجسم (سم)",
        "hg_tip": "خلف السنام", "bl_tip": "من الصدر للذيل",
        "source": "FAO Camel (2010)", "accuracy": "±10%",
        "calc": lambda hg, bl: (hg**2 * bl) / 11880.0,
    },
    "خيول": {
        "hg_min": 120.0, "hg_max": 240.0, "hg_default": 175.0,
        "bl_min": 100.0, "bl_max": 210.0, "bl_default": 155.0,
        "hg_label": "محيط الصدر (سم)", "bl_label": "طول الجسم (سم)",
        "hg_tip": "خلف الكتف", "bl_tip": "من الكتف للمؤخرة",
        "source": "Carroll & Huntington (1988)", "accuracy": "±5%",
        "calc": lambda hg, bl: (hg**2 * bl) / 11877.0,
    },
}

ANIMAL_PHOTOS = {
    "أبقار": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Cow_female_black_white.jpg/1024px-Cow_female_black_white.jpg",
    "أغنام": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Sheep_in_lesser_himalayas.JPG/1024px-Sheep_in_lesser_himalayas.JPG",
    "ماعز": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Goat_chewing_a_can_%28cropped%29.jpg/1024px-Goat_chewing_a_can_%28cropped%29.jpg",
    "إبل": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Camel_in_Dubai.jpg/1024px-Camel_in_Dubai.jpg",
    "خيول": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Nokota_Horses_cropped.jpg/1024px-Nokota_Horses_cropped.jpg",
}


@st.cache_data(ttl=86400, show_spinner=False)
def _download_image(url: str) -> Optional[bytes]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()
    except Exception:
        return None


def draw_tape_guide(animal_type: str) -> Optional[io.BytesIO]:
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        img_url = ANIMAL_PHOTOS.get(animal_type, ANIMAL_PHOTOS["أبقار"])
        img_bytes = _download_image(img_url)
        fig, ax = plt.subplots(figsize=(12, 7.5))
        img_loaded = False
        if img_bytes and PIL_AVAILABLE:
            try:
                img = PILImage.open(io.BytesIO(img_bytes))
                ax.imshow(img)
                img_loaded = True
            except Exception:
                img_loaded = False
        if not img_loaded:
            ax.text(0.5, 0.5, f"📸 {animal_type}", ha="center", va="center", fontsize=40, transform=ax.transAxes, color="#1b5e20", fontweight="bold")
            ax.axis("off")

        TAPE_POSITIONS = {
            "أبقار": {"girth_x": 0.42, "girth_y_top": 0.55, "girth_y_bot": 0.85, "length_left": 0.25, "length_right": 0.85, "length_y": 0.30},
            "أغنام": {"girth_x": 0.40, "girth_y_top": 0.50, "girth_y_bot": 0.85, "length_left": 0.25, "length_right": 0.80, "length_y": 0.28},
            "ماعز": {"girth_x": 0.42, "girth_y_top": 0.50, "girth_y_bot": 0.85, "length_left": 0.25, "length_right": 0.80, "length_y": 0.28},
            "إبل": {"girth_x": 0.40, "girth_y_top": 0.50, "girth_y_bot": 0.85, "length_left": 0.22, "length_right": 0.82, "length_y": 0.28},
            "خيول": {"girth_x": 0.42, "girth_y_top": 0.55, "girth_y_bot": 0.90, "length_left": 0.22, "length_right": 0.85, "length_y": 0.28},
        }
        pos = TAPE_POSITIONS.get(animal_type, TAPE_POSITIONS["أبقار"])
        ax.plot([pos["girth_x"], pos["girth_x"]], [pos["girth_y_top"], pos["girth_y_bot"]], color="#c62828", linewidth=5, transform=ax.transAxes, zorder=10, solid_capstyle="round")
        ax.annotate("", xy=(pos["girth_x"], pos["girth_y_top"]), xytext=(pos["girth_x"], pos["girth_y_top"] + 0.05), xycoords="axes fraction", textcoords="axes fraction", arrowprops=dict(arrowstyle="->", color="#c62828", lw=4, mutation_scale=25))
        ax.annotate("", xy=(pos["girth_x"], pos["girth_y_bot"]), xytext=(pos["girth_x"], pos["girth_y_bot"] - 0.05), xycoords="axes fraction", textcoords="axes fraction", arrowprops=dict(arrowstyle="->", color="#c62828", lw=4, mutation_scale=25))
        ax.text(pos["girth_x"] + 0.05, pos["girth_y_top"] - 0.03, "① محيط الصدر", color="#c62828", fontweight="bold", fontsize=13, transform=ax.transAxes, bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#c62828", linewidth=2), zorder=11)

        ax.plot([pos["length_left"], pos["length_right"]], [pos["length_y"], pos["length_y"]], color="#1565c0", linewidth=5, transform=ax.transAxes, zorder=10, solid_capstyle="round")
        ax.annotate("", xy=(pos["length_left"], pos["length_y"]), xytext=(pos["length_left"] - 0.03, pos["length_y"]), xycoords="axes fraction", textcoords="axes fraction", arrowprops=dict(arrowstyle="->", color="#1565c0", lw=4, mutation_scale=25))
        ax.annotate("", xy=(pos["length_right"], pos["length_y"]), xytext=(pos["length_right"] + 0.03, pos["length_y"]), xycoords="axes fraction", textcoords="axes fraction", arrowprops=dict(arrowstyle="->", color="#1565c0", lw=4, mutation_scale=25))
        mid_length = (pos["length_left"] + pos["length_right"]) / 2
        ax.text(mid_length, pos["length_y"] - 0.05, "② طول الجسم", color="#1565c0", fontweight="bold", fontsize=13, ha="center", transform=ax.transAxes, bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#1565c0", linewidth=2), zorder=11)

        cfg = WEIGHT_TAPE_CONFIG.get(animal_type, {})
        ax.text(0.5, 0.02, f"🔴 ① {cfg.get('hg_tip', '')}     🔵 ② {cfg.get('bl_tip', '')}", transform=ax.transAxes, ha="center", fontsize=11, color="#1a1a1a", fontweight="bold", bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff8e1", edgecolor="#d4af37", linewidth=2), zorder=12)
        ax.set_title(f"📍 طريقة القياس الصحيحة — {animal_type} | {cfg.get('source', '')} | دقة {cfg.get('accuracy', '')}", fontsize=14, fontweight="bold", color="#1b5e20", pad=15)
        if img_loaded:
            ax.axis("off")
        else:
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=130, bbox_inches="tight", facecolor="white", pad_inches=0.15)
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def weight_tape_widget(animal_type: str, key_prefix: str, default_weight: Optional[float] = None) -> float:
    cfg = WEIGHT_TAPE_CONFIG.get(animal_type)
    if cfg is None:
        return float(st.number_input("⚖️ الوزن (كجم):", 0.05, 50.0, float(default_weight) if default_weight else 2.0, 0.1, key=f"{key_prefix}_manual"))
    tab_tape, tab_manual = st.tabs(["📏 شريط القياس", "⚖️ إدخال يدوي"])
    with tab_tape:
        img = draw_tape_guide(animal_type)
        if img:
            st.image(img.getvalue(), use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            hg = st.slider(f"① {cfg['hg_label']}", cfg["hg_min"], cfg["hg_max"], cfg["hg_default"], 0.5, key=f"{key_prefix}_hg")
        with c2:
            bl = st.slider(f"② {cfg['bl_label']}", cfg["bl_min"], cfg["bl_max"], cfg["bl_default"], 0.5, key=f"{key_prefix}_bl")
        weight = float(cfg["calc"](hg, bl))
        st.success(f"⚖️ الوزن التقديري = **{weight:.1f} كجم**")
        return weight
    with tab_manual:
        lo = cfg["calc"](cfg["hg_min"], cfg["bl_min"])
        hi = cfg["calc"](cfg["hg_max"], cfg["bl_max"])
        return float(st.number_input("⚖️ الوزن (كجم):", float(lo * 0.5), float(hi * 1.5), float(default_weight) if default_weight else float(cfg["calc"](cfg["hg_default"], cfg["bl_default"])), 5.0, key=f"{key_prefix}_manual"))


# ═══════════════════════════════════════════════════════════════════════
# الدردشة والاستديو
# ═══════════════════════════════════════════════════════════════════════

CHAT_FILE = "tawor_chat_rooms.json"
STUDIO_FILE = "tawor_studio_content.json"


def _load_chat_rooms() -> Dict:
    try:
        if os.path.exists(CHAT_FILE):
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
    except Exception:
        pass
    return {"🌾 النقاش العام": [], "🧬 نقاش علمي": [], "💰 نقاش اقتصادي": []}


def _save_chat_rooms(data: Dict) -> None:
    try:
        tmp = CHAT_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, CHAT_FILE)
    except Exception:
        pass


def add_chat_message(room: str, user: str, message: str) -> bool:
    msg = _sanitize_message(message)
    user = _sanitize_message(user, 40)
    if not msg or not user:
        return False
    rooms = _load_chat_rooms()
    rooms.setdefault(room, [])
    rooms[room].append(
        {
            "user": user,
            "msg": msg,
            "ts": datetime.now().strftime("%H:%M:%S"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "role": st.session_state.get("user_role", "guest"),
        }
    )
    rooms[room] = rooms[room][-500:]
    _save_chat_rooms(rooms)
    return True


def create_chat_room(room_name: str) -> bool:
    rooms = _load_chat_rooms()
    name = _sanitize_message(room_name, 40)
    if name and name not in rooms:
        rooms[name] = []
        _save_chat_rooms(rooms)
        return True
    return False


def _load_studio() -> Dict:
    try:
        if os.path.exists(STUDIO_FILE):
            with open(STUDIO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"videos": [], "slides": [], "notes": []}


def _save_studio(data: Dict) -> None:
    try:
        tmp = STUDIO_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, STUDIO_FILE)
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════
# OCR والرسوم البيانية
# ═══════════════════════════════════════════════════════════════════════


def _preprocess_image_variants(img):
    variants = []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    variants.append(clahe.apply(gray))
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(otsu)
    variants.append(cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 5))
    variants.append(cv2.fastNlMeansDenoising(clahe.apply(gray), None, 10, 7, 21))
    variants.append(cv2.bitwise_not(gray))
    return variants


def _extract_with_confidence(image):
    try:
        data = pytesseract.image_to_data(image, lang="ara+eng", output_type=pytesseract.Output.DICT, config=r"--oem 3 --psm 6")
        good_lines = []
        current_line = []
        current_y = None
        for i, word in enumerate(data["text"]):
            if int(data["conf"][i]) < 30:
                continue
            word = word.strip()
            if not word:
                continue
            y = data["top"][i]
            if current_y is None:
                current_y = y
            if abs(y - current_y) > 15:
                if current_line:
                    good_lines.append(" ".join(current_line))
                current_line = [word]
                current_y = y
            else:
                current_line.append(word)
        if current_line:
            good_lines.append(" ".join(current_line))
        return "\n".join(good_lines), len(good_lines)
    except Exception:
        return "", 0


def extract_ingredients_from_image(image_bytes: bytes) -> Dict:
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
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        variants = _preprocess_image_variants(img)
        best_text, best_score, all_texts = "", 0, []
        for variant in variants:
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
        return {
            "success": True,
            "ingredients": ingredients,
            "raw_text": full_text,
            "best_text": best_text,
            "count": len(ingredients),
            "total": sum(ingredients.values()),
            "quality": "جيد" if best_score > 3 else "ضعيف",
        }
    except Exception as e:
        return {"success": False, "message": f"خطأ: {e}"}


def render_ocr_correction_ui(ingredients: Dict) -> Dict:
    st.markdown("### ✏️ تصحيح يدوي")
    corrected = {}
    all_names = sorted(_get_ingredient_lookup().keys())
    if ingredients:
        for i, (name, pct) in enumerate(list(ingredients.items())):
            ca, cb, cc = st.columns([0.5, 0.3, 0.2])
            with ca:
                idx = all_names.index(name) if name in all_names else 0
                new_name = st.selectbox(f"المادة {i + 1}", options=all_names, index=idx, key=f"ocr_fix_name_{i}")
            with cb:
                new_pct = st.number_input("النسبة %", 0.0, 100.0, float(pct), 0.5, key=f"ocr_fix_pct_{i}")
            with cc:
                keep = st.checkbox("احتفظ", value=True, key=f"ocr_keep_{i}")
            if keep and new_pct > 0:
                corrected[new_name] = new_pct
    return corrected


def create_colorful_bar_chart(standard: Dict, actual: Dict, keys=None) -> Optional[io.BytesIO]:
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
        b1 = ax.bar(x - width / 2, [standard[n] for n in nuts], width, label="المعيار", color="#1976d2", edgecolor="#0d47a1", linewidth=1.5)
        b2 = ax.bar(x + width / 2, [actual.get(n, 0) for n in nuts], width, label="المحسوب", color="#43a047", edgecolor="#1b5e20", linewidth=1.5)
        for bar in b1:
            hh = bar.get_height()
            if hh > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, hh, f"{hh:.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
        for bar in b2:
            hh = bar.get_height()
            if hh > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, hh, f"{hh:.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.set_title("مقارنة العناصر", fontsize=13, fontweight="bold", color="#1b5e20")
        ax.set_xticks(x)
        ax.set_xticklabels(nuts)
        ax.legend(loc="upper right")
        ax.grid(axis="y", alpha=0.3)
        ax.set_facecolor("#fafafa")
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="white")
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_colorful_pie_chart(formula: Dict) -> Optional[io.BytesIO]:
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2:
        return None
    try:
        colors = ["#e53935", "#8e24aa", "#3949ab", "#1e88e5", "#00897b", "#43a047", "#7cb342", "#fdd835", "#fb8c00", "#6d4c41"]
        names = list(formula.keys())
        vals = list(formula.values())
        fig, ax = plt.subplots(figsize=(8, 5))
        _, _, autotexts = ax.pie(vals, autopct="%1.1f%%", colors=colors[: len(names)], startangle=90, pctdistance=0.75, wedgeprops=dict(edgecolor="white", linewidth=2))
        for t in autotexts:
            t.set_color("white")
            t.set_fontweight("bold")
            t.set_fontsize(9)
        ax.legend(names, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)
        ax.set_title("توزيع المكونات", fontsize=13, fontweight="bold", color="#1b5e20")
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="white")
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_radar_chart(standard: Dict, actual: Dict, keys=None) -> Optional[io.BytesIO]:
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
        ax.plot(angles, std_norm, "o-", linewidth=2.5, color="#1976d2", label="المعيار")
        ax.fill(angles, std_norm, alpha=0.15, color="#1976d2")
        ax.plot(angles, act_norm, "o-", linewidth=2.5, color="#43a047", label="المحسوب")
        ax.fill(angles, act_norm, alpha=0.25, color="#43a047")
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(nuts)
        ax.set_title("المقارنة %", fontweight="bold", color="#1b5e20", pad=20)
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="white")
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_gauge_chart(score: float) -> Optional[io.BytesIO]:
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect="equal"))
        colors = ["#c62828", "#ef6c00", "#f9a825", "#7cb342", "#43a047", "#1b5e20"]
        for i, c in enumerate(colors):
            t1 = 180 - (i * 30)
            t2 = 180 - ((i + 1) * 30)
            ax.add_patch(Wedge((0, 0), 1, t2, t1, width=0.3, facecolor=c, edgecolor="white", linewidth=2))
        angle = 180 - (score / 100) * 180
        rad = np.radians(angle)
        ax.plot([0, 0.85 * np.cos(rad)], [0, 0.85 * np.sin(rad)], color="#1a1a1a", linewidth=3, zorder=10)
        ax.add_patch(Circle((0, 0), 0.08, color="#1a1a1a", zorder=11))
        ax.text(0, -0.25, f"{score:.0f}%", ha="center", fontsize=20, fontweight="bold", color="#1b5e20")
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.7, 1.2)
        ax.axis("off")
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="white")
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_ca_p_ratio_chart(ca: float, p: float) -> Optional[io.BytesIO]:
    if not MATPLOTLIB_AVAILABLE or p <= 0:
        return None
    try:
        ratio = ca / p
        fig, ax = plt.subplots(figsize=(8, 3))
        zones = [
            (0, 0.8, "#b71c1c"),
            (0.8, 1.2, "#ef6c00"),
            (1.2, 1.5, "#f9a825"),
            (1.5, 2.0, "#2e7d32"),
            (2.0, 3.0, "#f9a825"),
            (3.0, 5.0, "#ef6c00"),
            (5.0, 8.0, "#b71c1c"),
        ]
        for x0, x1, c in zones:
            ax.axvspan(x0, x1, alpha=0.35, color=c)
        ratio_clipped = min(ratio, 7.9)
        ax.axvline(ratio_clipped, color="#0d47a1", linewidth=4, zorder=10)
        ax.text(ratio_clipped, 0.85, f"{ratio:.2f}", ha="center", fontsize=18, fontweight="bold", color="#0d47a1", bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#0d47a1", linewidth=2))
        ax.set_xlim(0, 8)
        ax.set_ylim(0, 1.2)
        ax.set_yticks([])
        ax.set_title(f"⚖️ Ca:P — Ca={ca:.2f}% | P={p:.2f}%", fontweight="bold", color="#1b5e20")
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=130, bbox_inches="tight", facecolor="white")
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_nlp_profit_curve(result: Dict, ingredient_names, ingredient_data, prices):
    if not PLOTLY_AVAILABLE:
        return None
    try:
        import plotly.graph_objects as go

        me_vals = np.array([ingredient_data[i].get("SE", 0) * 41 for i in ingredient_names])
        cp_vals = np.array([ingredient_data[i].get("CP", 0) for i in ingredient_names])
        cost_vals = np.array([prices.get(i, 300.0) / 1000.0 for i in ingredient_names])
        x_opt = np.array(result["x_opt"])
        prices_range = np.linspace(1.0, 5.0, 40)
        profits = []
        for p in prices_range:
            qv = (np.dot(me_vals, x_opt) / result["target_me"]) * (np.dot(cp_vals, x_opt) / result["target_cp"])
            profits.append(p * qv - np.dot(cost_vals, x_opt))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=prices_range, y=profits, mode="lines+markers", line=dict(color="#1b5e20", width=3), name="صافي العائد"))
        fig.add_hline(y=0, line_dash="dash", line_color="#c62828", annotation_text="التعادل")
        fig.update_layout(title="منحنى الربحية", height=420, paper_bgcolor="white")
        return fig
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════
# مولد تقارير PDF
# ═══════════════════════════════════════════════════════════════════════


class PDFGenerator:
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
            return get_display(arabic_reshaper.reshape(str(t)), base_dir="R")
        except Exception:
            return str(t)

    def _draw_page(self, canvas_obj, doc):
        try:
            canvas_obj.saveState()
            w, h = doc.pagesize
            canvas_obj.setFillColor(HexColor("#1b5e20"))
            canvas_obj.rect(0, h - 90, w, 90, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor("#d4af37"))
            canvas_obj.rect(0, h - 95, w, 5, fill=1, stroke=0)
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 22)
            canvas_obj.drawCentredString(w / 2, h - 38, self._ar("تاور نولجي  Tawor Nology"))
            canvas_obj.setFont(self.font_name, 12)
            canvas_obj.setFillColor(HexColor("#e8f5e9"))
            canvas_obj.drawCentredString(w / 2, h - 58, self._ar("للإنتاج الحيواني وتغذية الحيوان"))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.setFillColor(HexColor("#d4af37"))
            canvas_obj.drawCentredString(w / 2, h - 76, self._ar(f"إشراف: {SUPERVISOR}"))
            canvas_obj.setFillColor(HexColor("#1b5e20"))
            canvas_obj.rect(0, 42, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor("#d4af37"))
            canvas_obj.rect(0, 84, w, 3, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor("#ffeb3b"))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.drawCentredString(w / 2, 68, self._ar(f"🤲 {DUA_SHORT} 🤲"))
            canvas_obj.setFillColor(HexColor("#1b5e20"))
            canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(w / 2, 27, self._ar("تاور نولجي © 2026"))
            canvas_obj.setFont(self.font_name, 7)
            canvas_obj.drawCentredString(w / 2, 12, self._ar(f"صفحة {canvas_obj.getPageNumber()}"))
            canvas_obj.restoreState()
        except Exception:
            pass

    def _add_references_page(self, story, animal_type: str, production_type: str):
        try:
            refs = get_references(animal_type, production_type)
            eqs = get_reference_equations(animal_type, production_type)
            story.append(PageBreak())
            story.append(Paragraph(self._ar("📚 المراجع والمعادلات"), ParagraphStyle("rt", fontName=self.font_name, fontSize=16, alignment=TA_CENTER, textColor=HexColor("#1b5e20"), spaceAfter=15)))
            story.append(Paragraph(self._ar(f"📖 المرجع: {refs['primary']}"), ParagraphStyle("rp", fontName=self.font_name, fontSize=11, alignment=TA_RIGHT, textColor=HexColor("#0d47a1"), spaceAfter=8, leading=16)))
            if refs.get("table"):
                story.append(Paragraph(self._ar(f"📑 الجدول: {refs['table']}"), ParagraphStyle("rt2", fontName=self.font_name, fontSize=10, alignment=TA_RIGHT, textColor=HexColor("#1565c0"), spaceAfter=8, leading=14)))
            if eqs:
                story.append(Spacer(1, 10))
                story.append(Paragraph(self._ar("📐 المعادلات المرجعية:"), ParagraphStyle("eqt", fontName=self.font_name, fontSize=12, alignment=TA_RIGHT, textColor=HexColor("#2e7d32"), spaceAfter=8)))
                eq_data = [[self._ar("المؤشر"), self._ar("المعادلة")]]
                for k, v in eqs.items():
                    if k in ("source", "example"):
                        continue
                    eq_data.append([self._ar(k), self._ar(v)])
                if len(eq_data) > 1:
                    et = Table(eq_data, colWidths=[100, 390])
                    et.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HexColor("#2e7d32")), ("TEXTCOLOR", (0, 0), (-1, 0), white), ("BOX", (0, 0), (-1, -1), 1.5, HexColor("#2e7d32")), ("ALIGN", (0, 0), (-1, -1), "RIGHT"), ("FONTNAME", (0, 0), (-1, -1), self.font_name), ("FONTSIZE", (0, 0), (-1, -1), 9), ("PADDING", (0, 0), (-1, -1), 5)]))
                    story.append(et)
                if eqs.get("example"):
                    story.append(Spacer(1, 8))
                    story.append(Paragraph(self._ar(f"💡 مثال: {eqs['example']}"), ParagraphStyle("ex", fontName=self.font_name, fontSize=10, alignment=TA_RIGHT, textColor=HexColor("#c62828"))))
            if refs.get("secondary"):
                story.append(Spacer(1, 12))
                story.append(Paragraph(self._ar("📚 مراجع داعمة:"), ParagraphStyle("rst", fontName=self.font_name, fontSize=11, alignment=TA_RIGHT, textColor=HexColor("#2e7d32"), spaceAfter=6)))
                for sec in refs["secondary"]:
                    story.append(Paragraph(self._ar(f"• {sec}"), ParagraphStyle("rs", fontName=self.font_name, fontSize=10, alignment=TA_RIGHT, spaceAfter=4, leading=14)))
            story.append(Spacer(1, 15))
            story.append(HRFlowable(width="100%", thickness=1.5, color=HexColor("#d4af37")))
            story.append(Spacer(1, 10))
            story.append(Paragraph(self._ar("📖 مراجع عامة:"), ParagraphStyle("rg", fontName=self.font_name, fontSize=11, alignment=TA_RIGHT, textColor=HexColor("#1b5e20"), spaceAfter=8)))
            for i, ref in enumerate(GENERAL_REFERENCES, 1):
                story.append(Paragraph(f"{i}. {ref}", ParagraphStyle("rli", fontName="Helvetica", fontSize=9, alignment=TA_LEFT, spaceAfter=4, leading=12, leftIndent=10)))
        except Exception as e:
            story.append(Paragraph(f"خطأ: {e}", ParagraphStyle("err", fontName=self.font_name, fontSize=9, alignment=TA_RIGHT, textColor=HexColor("#c62828"))))

    def _comparison_table(self, std: Dict, calc: Dict):
        labels = {"CP": "بروتين", "DP": "مهضوم", "SE": "SE", "NDF": "NDF", "ADF": "ADF", "EE": "دهن", "ASH": "رماد", "Ca": "Ca", "P": "P"}
        data = [[self._ar(x) for x in ["العنصر", "المعيار", "المحسوب", "الفرق", "%", "التقييم"]]]
        cmds = [("BACKGROUND", (0, 0), (-1, 0), HexColor("#1b5e20")), ("TEXTCOLOR", (0, 0), (-1, 0), white), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTNAME", (0, 0), (-1, -1), self.font_name), ("FONTSIZE", (0, 0), (-1, -1), 9), ("GRID", (0, 0), (-1, -1), 1, HexColor("#9e9e9e")), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]
        row = 1
        for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
            if k not in std or std[k] == 0:
                continue
            sv, cv = std[k], calc.get(k, 0)
            diff = cv - sv
            pct = (diff / sv * 100) if sv else 0
            ev = evaluate_difference(pct, standard_value=sv)
            data.append([self._ar(labels[k]), f"{sv:.2f}", f"{cv:.2f}", f"{diff:+.3f}", f"{pct:+.2f}%", self._ar(ev["label"])])
            cmds.append(("BACKGROUND", (0, row), (-1, row), HexColor(ev["bg"])))
            row += 1
        t = Table(data, colWidths=[100, 70, 70, 70, 70, 105])
        t.setStyle(TableStyle(cmds))
        return t

    def generate_report(
        self,
        formula: Dict,
        requirement: AnimalRequirement,
        animal_type: str,
        breed: str,
        cost: float,
        city: str,
        local_cost: float,
        local_sym: str,
        requester_name: str = "",
        protein_basis: str = "DP",
        standard_key: str = "",
        include_charts: bool = True,
        quality_score: float = 0.0,
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color="#1a1a1a"):
            return Paragraph(self._ar(text), ParagraphStyle("s", fontName=self.font_name, fontSize=size, alignment=align, textColor=HexColor(color), spaceAfter=6, leading=size * 1.6))

        story.append(P("تقرير فني رسمي", size=20, align=TA_CENTER, color="#1b5e20"))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor("#d4af37")))
        story.append(Spacer(1, 12))
        client = [
            [self._ar("👤 طالب:"), self._ar(requester_name or "—")],
            [self._ar("🐾 الفصيل:"), self._ar(f"{animal_type} — {breed}")],
            [self._ar("🧬 الأساس:"), self._ar(protein_basis)],
            [self._ar("📅 التاريخ:"), datetime.now().strftime("%Y-%m-%d")],
        ]
        ct = Table(client, colWidths=[150, 340])
        ct.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), HexColor("#e8f5e9")), ("BOX", (0, 0), (-1, -1), 1.5, HexColor("#2e7d32")), ("INNERGRID", (0, 0), (-1, -1), 0.6, HexColor("#c8e6c9")), ("ALIGN", (0, 0), (-1, -1), "RIGHT"), ("FONTNAME", (0, 0), (-1, -1), self.font_name), ("FONTSIZE", (0, 0), (-1, -1), 11), ("PADDING", (0, 0), (-1, -1), 9)]))
        story.append(ct)
        story.append(Spacer(1, 15))
        std_vals = requirement_to_standard(requirement)
        calc_vals = compute_formula_nutrients(formula)
        qd = [
            [self._ar("الجودة"), self._ar("الحالة"), self._ar("70%")],
            [f"{quality_score:.1f}%", self._ar("✅ ناجح" if quality_score >= 70 else "⚠️ يحتاج"), self._ar("✅" if quality_score >= 70 else "❌")],
        ]
        qt = Table(qd, colWidths=[130, 200, 160])
        qt.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HexColor("#1565c0")), ("TEXTCOLOR", (0, 0), (-1, 0), white), ("BACKGROUND", (0, 1), (-1, -1), HexColor("#e8f5e9" if quality_score >= 70 else "#ffebee")), ("GRID", (0, 0), (-1, -1), 1, HexColor("#1976d2")), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTNAME", (0, 0), (-1, -1), self.font_name)]))
        story.append(qt)
        story.append(Spacer(1, 15))
        story.append(P("📊 مقارنة العناصر", size=14, color="#1b5e20"))
        story.append(Spacer(1, 8))
        story.append(self._comparison_table(std_vals, calc_vals))
        if include_charts:
            story.append(Spacer(1, 15))
            for chart_fn, args in [(create_colorful_bar_chart, (std_vals, calc_vals)), (create_colorful_pie_chart, (formula,)), (create_radar_chart, (std_vals, calc_vals))]:
                try:
                    c = chart_fn(*args)
                    if c:
                        story.append(RLImage(c, width=450, height=250))
                        story.append(Spacer(1, 10))
                except Exception:
                    pass
        story.append(PageBreak())
        story.append(P("💰 التكاليف", size=14, color="#1b5e20"))
        cost_data = [[self._ar("البند"), self._ar("القيمة")], [self._ar("التكلفة/طن"), f"${cost:.2f}"]]
        tc = Table(cost_data, colWidths=[280, 210])
        tc.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HexColor("#1b5e20")), ("TEXTCOLOR", (0, 0), (-1, 0), white), ("GRID", (0, 0), (-1, -1), 1, HexColor("#2e7d32")), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTNAME", (0, 0), (-1, -1), self.font_name)]))
        story.append(tc)
        story.append(Spacer(1, 18))
        if formula:
            story.append(P("🌾 المكونات للطن", size=14, color="#1b5e20"))
            ing_data = [[self._ar("المكون"), self._ar("%"), self._ar("كجم/طن")]]
            for ing, pct in formula.items():
                ing_data.append([self._ar(ing), f"{pct:.2f}%", f"{pct * 10:.1f}"])
            ti = Table(ing_data, colWidths=[270, 110, 110])
            ti.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HexColor("#2e7d32")), ("TEXTCOLOR", (0, 0), (-1, 0), white), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTNAME", (0, 0), (-1, -1), self.font_name), ("GRID", (0, 0), (-1, -1), 1, HexColor("#bdbdbd")), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f5f5f5")])]))
            story.append(ti)
            story.append(Spacer(1, 25))
        try:
            self._add_references_page(story, animal_type, standard_key or breed)
        except Exception:
            pass
        doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_ocr_report(self, ingredients: Dict, nutrients: Dict, raw_text: str = "") -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color="#1a1a1a"):
            return Paragraph(self._ar(text), ParagraphStyle("s", fontName=self.font_name, fontSize=size, alignment=align, textColor=HexColor(color), spaceAfter=6, leading=size * 1.6))

        story.append(P("تقرير تحليل OCR", size=20, align=TA_CENTER, color="#1b5e20"))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor("#d4af37")))
        data = [[self._ar("المادة"), self._ar("%")]]
        for k, v in ingredients.items():
            data.append([self._ar(k), f"{v:.2f}%"])
        data.append([self._ar("الإجمالي"), f"{sum(ingredients.values()):.2f}%"])
        t = Table(data, colWidths=[300, 200])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HexColor("#1b5e20")), ("TEXTCOLOR", (0, 0), (-1, 0), white), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTNAME", (0, 0), (-1, -1), self.font_name), ("GRID", (0, 0), (-1, -1), 1, HexColor("#bdbdbd")), ("BACKGROUND", (0, -1), (-1, -1), HexColor("#ffe0b2"))]))
        story.append(t)
        doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()


pdf_gen = PDFGenerator()


def generate_nlp_math_pdf(result: Dict, animal_type: str, production_type: str, nlp_sel, ing_data, nlp_prices) -> Optional[bytes]:
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color="#1a1a1a"):
            return Paragraph(ar(text), ParagraphStyle("s", fontName=font_mgr.font_name, fontSize=size, alignment=align, textColor=HexColor(color), spaceAfter=6, leading=size * 1.6))

        story.append(P("تقرير التحسين غير الخطي (NLP)", size=20, align=TA_CENTER, color="#1b5e20"))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor("#d4af37")))
        story.append(Spacer(1, 12))
        info = [
            [ar("الحيوان"), ar(animal_type)],
            [ar("الحالة"), ar(production_type)],
            [ar("الاستراتيجية"), ar(result.get("strategy", "—"))],
            [ar("التكلفة"), f"${result['final_cost']:.4f}/كجم"],
            [ar("الطاقة"), f"{result['final_me']:.0f} kcal/kg"],
            [ar("البروتين"), f"{result['final_cp']:.2f}%"],
            [ar("صافي الربح"), f"${result['max_profit']:.4f}"],
        ]
        t = Table(info, colWidths=[160, 330])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), HexColor("#e8f5e9")), ("BOX", (0, 0), (-1, -1), 1.5, HexColor("#2e7d32")), ("ALIGN", (0, 0), (-1, -1), "RIGHT"), ("FONTNAME", (0, 0), (-1, -1), font_mgr.font_name), ("PADDING", (0, 0), (-1, -1), 6)]))
        story.append(t)
        story.append(Spacer(1, 15))
        story.append(P("📐 المعادلات", size=14, color="#1565c0"))
        story.append(Spacer(1, 8))
        nlp_eq = REFERENCE_EQUATIONS.get("معادلة_التركيب_NLP", {})
        eq_data = [[ar("البند"), ar("القيمة")]]
        for k, v in nlp_eq.items():
            if k == "source":
                continue
            eq_data.append([ar(k), ar(v)])
        et = Table(eq_data, colWidths=[130, 360])
        et.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HexColor("#1565c0")), ("TEXTCOLOR", (0, 0), (-1, 0), white), ("ALIGN", (0, 0), (-1, -1), "RIGHT"), ("FONTNAME", (0, 0), (-1, -1), font_mgr.font_name), ("GRID", (0, 0), (-1, -1), 0.6, HexColor("#bbdefb")), ("FONTSIZE", (0, 0), (-1, -1), 9), ("PADDING", (0, 0), (-1, -1), 6)]))
        story.append(et)
        story.append(PageBreak())
        story.append(P("🌾 التركيبة", size=16, color="#1b5e20"))
        ing_pdf = [[ar("المكوّن"), ar("%"), ar("كجم/طن")]]
        for ing, pct in result["formula"].items():
            ing_pdf.append([ar(ing), f"{pct:.2f}%", f"{pct * 10:.1f}"])
        it = Table(ing_pdf, colWidths=[280, 110, 110])
        it.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HexColor("#2e7d32")), ("TEXTCOLOR", (0, 0), (-1, 0), white), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTNAME", (0, 0), (-1, -1), font_mgr.font_name), ("GRID", (0, 0), (-1, -1), 0.8, HexColor("#bdbdbd"))]))
        story.append(it)
        story.append(PageBreak())
        story.append(P("📈 الرسوم", size=16, color="#1b5e20"))
        story.append(Spacer(1, 10))
        try:
            actual = compute_formula_nutrients(result["formula"])
            nlp_req = _get_requirement_for_nlp(animal_type, production_type)
            std_c = {"ME/100": nlp_req["ME"] / 100, "CP": nlp_req["CP"], "DP": nlp_req["DP"]}
            act_c = {"ME/100": actual.get("SE", 0) * 41 / 100, "CP": actual.get("CP", 0), "DP": actual.get("DP", 0)}
            bf = create_colorful_bar_chart(std_c, act_c)
            if bf:
                story.append(RLImage(bf, width=470, height=250))
                story.append(P("1️⃣ مقارنة ME/CP/DP", size=9, align=TA_CENTER, color="#555"))
                story.append(Spacer(1, 8))
        except Exception:
            pass
        try:
            pf = create_colorful_pie_chart(result["formula"])
            if pf:
                story.append(RLImage(pf, width=380, height=240))
                story.append(P("2️⃣ التوزيع", size=9, align=TA_CENTER, color="#555"))
        except Exception:
            pass
        try:
            pdf_gen._add_references_page(story, animal_type, production_type)
        except Exception:
            pass
        story.append(Spacer(1, 20))
        story.append(P(SUPERVISOR, size=16, align=TA_CENTER, color="#c62828"))
        story.append(P(SUPERVISOR_TITLE, size=11, align=TA_CENTER, color="#1b5e20"))
        doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"⚠️ {e}")
        return None


def generate_milk_replacer_pdf(result: Dict) -> Optional[bytes]:
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color="#1a1a1a"):
            return Paragraph(ar(text), ParagraphStyle("s", fontName=font_mgr.font_name, fontSize=size, alignment=align, textColor=HexColor(color), spaceAfter=6, leading=size * 1.6))

        std = result["standard"]
        quality = result["quality_score"]
        formula = result["formula"]
        volume = result.get("volume", 100.0)
        story.append(P("تقرير بديل الحليب", size=20, align=TA_CENTER, color="#1b5e20"))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor("#d4af37")))
        info = [
            [ar("الحيوان:"), ar(result["animal"])],
            [ar("المرجع:"), ar(std.get("source", ""))],
            [ar("الجودة:"), f"{quality:.1f}%"],
            [ar("الكمية:"), f"{volume:.0f} كجم"],
        ]
        ct = Table(info, colWidths=[160, 330])
        ct.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), HexColor("#e3f2fd")), ("BOX", (0, 0), (-1, -1), 1.5, HexColor("#1565c0")), ("ALIGN", (0, 0), (-1, -1), "RIGHT"), ("FONTNAME", (0, 0), (-1, -1), font_mgr.font_name), ("PADDING", (0, 0), (-1, -1), 7)]))
        story.append(ct)
        story.append(Spacer(1, 15))
        story.append(P("🍼 المكونات", size=14, color="#1b5e20"))
        ing_data = [[ar("المكون"), ar("%"), ar("كجم")]]
        for ing, pct in formula.items():
            kg = pct * volume / 100
            ing_data.append([ar(ing), f"{pct:.2f}%", f"{kg:.2f}"])
        it = Table(ing_data, colWidths=[200, 130, 130])
        it.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HexColor("#2e7d32")), ("TEXTCOLOR", (0, 0), (-1, 0), white), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTNAME", (0, 0), (-1, -1), font_mgr.font_name), ("GRID", (0, 0), (-1, -1), 0.8, HexColor("#bdbdbd"))]))
        story.append(it)
        try:
            pdf_gen._add_references_page(story, "عجول", "حليب")
        except Exception:
            pass
        story.append(P(SUPERVISOR, size=16, align=TA_CENTER, color="#c62828"))
        story.append(P(SUPERVISOR_TITLE, size=11, align=TA_CENTER, color="#1b5e20"))
        doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception:
        return None


def generate_lab_pdf(result: Dict, ctx: Dict) -> Optional[bytes]:
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color="#1a1a1a"):
            return Paragraph(ar(text), ParagraphStyle("s", fontName=font_mgr.font_name, fontSize=size, alignment=align, textColor=HexColor(color), spaceAfter=6, leading=size * 1.6))

        story.append(P("تقرير تحليل تركيبة", size=18, align=TA_CENTER, color="#1b5e20"))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor("#d4af37")))
        info = [
            [ar("الحيوان"), ar(ctx.get("animal", "—"))],
            [ar("الإنتاج"), ar(ctx.get("production", "—"))],
            [ar("الجودة"), ar(f"{result['quality_score']:.1f}%")],
            [ar("Ca:P"), ar(f"{result['ca_p_ratio']:.2f}")],
            [ar("التكلفة"), ar(f"${result['cost_per_ton']:.2f}")],
            [ar("التاريخ"), ar(datetime.now().strftime("%Y-%m-%d %H:%M"))],
        ]
        t = Table(info, colWidths=[160, 330])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), HexColor("#e8f5e9")), ("BOX", (0, 0), (-1, -1), 1.5, HexColor("#2e7d32")), ("ALIGN", (0, 0), (-1, -1), "RIGHT"), ("FONTNAME", (0, 0), (-1, -1), font_mgr.font_name), ("PADDING", (0, 0), (-1, -1), 6)]))
        story.append(t)
        story.append(Spacer(1, 15))
        story.append(P("📊 المقارنة", size=14, color="#1b5e20"))
        data = [[ar(x) for x in ["العنصر", "المعيار", "المحسوب", "الفرق", "%", "التقييم"]]]
        cmds = [("BACKGROUND", (0, 0), (-1, 0), HexColor("#1b5e20")), ("TEXTCOLOR", (0, 0), (-1, 0), white), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTNAME", (0, 0), (-1, -1), font_mgr.font_name), ("GRID", (0, 0), (-1, -1), 0.8, HexColor("#9e9e9e"))]
        for i, c in enumerate(result["comparison"], 1):
            data.append([ar(c["العنصر"]), f"{c['المعيار']:.2f}", f"{c['المحسوب']:.2f}", f"{c['الفرق']:+.3f}", f"{c['الفرق %']:+.2f}%", ar(c["التقييم"])])
            bg = "#e8f5e9" if c["score"] >= 70 else "#ffebee" if c["score"] < 50 else "#fff8e1"
            cmds.append(("BACKGROUND", (0, i), (-1, i), HexColor(bg)))
        ct = Table(data, colWidths=[90, 65, 65, 65, 65, 120])
        ct.setStyle(TableStyle(cmds))
        story.append(ct)
        story.append(PageBreak())
        story.append(P("📐 المعادلات المرجعية", size=14, color="#1565c0"))
        eqs = get_reference_equations(result["animal_type"], result["production_type"])
        if eqs:
            eq_data = [[ar("المؤشر"), ar("المعادلة")]]
            for k, v in eqs.items():
                if k in ("source", "example"):
                    continue
                eq_data.append([ar(k), ar(v)])
            if len(eq_data) > 1:
                et = Table(eq_data, colWidths=[100, 390])
                et.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HexColor("#1565c0")), ("TEXTCOLOR", (0, 0), (-1, 0), white), ("ALIGN", (0, 0), (-1, -1), "RIGHT"), ("FONTNAME", (0, 0), (-1, -1), font_mgr.font_name), ("FONTSIZE", (0, 0), (-1, -1), 9)]))
                story.append(et)
        try:
            pdf_gen._add_references_page(story, result["animal_type"], result["production_type"])
        except Exception:
            pass
        story.append(Spacer(1, 20))
        story.append(P(SUPERVISOR, size=16, align=TA_CENTER, color="#c62828"))
        story.append(P(SUPERVISOR_TITLE, size=11, align=TA_CENTER, color="#1b5e20"))
        doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"⚠️ {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════
# ✅ نظام الموافقة على PDF + أزرار الاستشارة
# ═══════════════════════════════════════════════════════════════════════

PDF_REQUESTS_FILE = "tawor_pdf_requests.json"
PDF_STORAGE_DIR = "pdf_storage"
os.makedirs(PDF_STORAGE_DIR, exist_ok=True)


def _load_pdf_requests() -> Dict:
    try:
        if os.path.exists(PDF_REQUESTS_FILE):
            with open(PDF_REQUESTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
    except Exception:
        pass
    return {"requests": []}


def _save_pdf_requests(data: Dict) -> None:
    try:
        tmp = PDF_REQUESTS_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, PDF_REQUESTS_FILE)
    except Exception:
        pass


def create_pdf_request(user_name: str, user_role: str, pdf_bytes: bytes, doc_title: str, doc_context: Optional[Dict] = None) -> str:
    try:
        request_id = f"REQ_{datetime.now():%Y%m%d%H%M%S}_{random.randint(100, 999)}"
        pdf_path = os.path.join(PDF_STORAGE_DIR, f"{request_id}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        data = _load_pdf_requests()
        data["requests"].append(
            {
                "id": request_id,
                "user_name": _sanitize_message(user_name, 50) or "غير محدد",
                "user_role": user_role,
                "doc_title": _sanitize_message(doc_title, 100),
                "doc_context": doc_context or {},
                "pdf_path": pdf_path,
                "status": "pending",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "reviewed_at": None,
                "rejection_reason": None,
            }
        )
        data["requests"] = data["requests"][-200:]
        _save_pdf_requests(data)
        return request_id
    except Exception as e:
        return f"ERR_{e}"


def get_user_pending_request(user_name: str, doc_title: str) -> Optional[Dict]:
    data = _load_pdf_requests()
    for req in reversed(data["requests"]):
        if req["user_name"] == user_name and req["doc_title"] == doc_title:
            return req
    return None


def approve_pdf_request(request_id: str) -> bool:
    data = _load_pdf_requests()
    for req in data["requests"]:
        if req["id"] == request_id:
            req["status"] = "approved"
            req["reviewed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _save_pdf_requests(data)
            return True
    return False


def reject_pdf_request(request_id: str, reason: str = "") -> bool:
    data = _load_pdf_requests()
    for req in data["requests"]:
        if req["id"] == request_id:
            req["status"] = "rejected"
            req["reviewed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            req["rejection_reason"] = _sanitize_message(reason, 200)
            _save_pdf_requests(data)
            return True
    return False


def _read_pdf_bytes(request_id: str) -> Optional[bytes]:
    try:
        path = os.path.join(PDF_STORAGE_DIR, f"{request_id}.pdf")
        if os.path.exists(path):
            with open(path, "rb") as f:
                return f.read()
    except Exception:
        pass
    return None


def render_consultation_buttons() -> None:
    st.markdown(
        f"""
    <div style="background: linear-gradient(135deg, #fff3e0, #ffe0b2);
                padding: 20px; border-radius: 14px;
                border: 2px solid #e65100; margin: 15px 0;
                direction: rtl; text-align: right;">
        <h4 style="color:#e65100; margin:0 0 12px 0;">
            🌾 للحصول على تركيبات علفية أكثر جودة
        </h4>
        <p style="color:#1a1a1a; margin:0 0 15px 0; font-size:1rem;">
            الرجاء الضغط على الزر أدناه للتواصل مع
            <b style="color:#c62828;">{SUPERVISOR}</b><br>
            <span style="color:#1565c0;">{SUPERVISOR_TITLE}</span>
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    wa_consult = f"https://wa.me/{WHATSAPP_NUMBER.replace('+', '').replace(' ', '')}?text="
    consult_msg = urllib.parse.quote(f"السلام عليكم دكتور عبدالقادر،\nأرغب في استشارة حول تركيبة علفية.\nالمنصة: {APP_NAME}")

    with col1:
        st.markdown(
            f"""<a href="{wa_consult}{consult_msg}" target="_blank"
           style="display:block; padding:14px; background:#25d366;
                  color:white; text-decoration:none; border-radius:10px;
                  text-align:center; font-weight:700; font-size:1rem;
                  border:2px solid #128c7e;">📱 استشارة واتساب</a>""",
            unsafe_allow_html=True,
        )
    with col2:
        em_consult = f"mailto:{OWNER_EMAIL}?subject=" + urllib.parse.quote("طلب استشارة - تاور نولجي") + "&body=" + urllib.parse.quote("السلام عليكم دكتور عبدالقادر،\n\nأرغب في استشارة حول تركيبة علفية.\n\nجزاك الله خيراً")
        st.markdown(
            f"""<a href="{em_consult}"
           style="display:block; padding:14px; background:#1565c0;
                  color:white; text-decoration:none; border-radius:10px;
                  text-align:center; font-weight:700; font-size:1rem;
                  border:2px solid #0d47a1;">✉️ استشارة بريد</a>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<a href="tel:{WHATSAPP_NUMBER}"
           style="display:block; padding:14px; background:#c62828;
                  color:white; text-decoration:none; border-radius:10px;
                  text-align:center; font-weight:700; font-size:1rem;
                  border:2px solid #8e0000;">📞 اتصال مباشر</a>""",
            unsafe_allow_html=True,
        )


def render_pdf_download_with_approval(
    pdf_bytes: Optional[bytes],
    file_name: str,
    doc_title: str,
    user_role: str,
    user_name: str = "",
    doc_context: Optional[Dict] = None,
    key_suffix: str = "",
) -> None:
    if not pdf_bytes:
        st.warning("⚠️ تعذر إنشاء ملف PDF")
        return

    if user_role == "owner":
        st.download_button(
            "📄 تحميل PDF (مالك)",
            pdf_bytes,
            file_name=file_name,
            mime="application/pdf",
            use_container_width=True,
            type="primary",
            key=f"pdf_direct_{key_suffix}",
        )
        return

    if not user_name:
        user_name = st.session_state.get("chat_username", "مستخدم")

    existing = get_user_pending_request(user_name, doc_title)

    if existing:
        status = existing["status"]
        if status == "approved":
            pdf_data = _read_pdf_bytes(existing["id"])
            if pdf_data:
                st.success("✅ تمت الموافقة بواسطة المالك — يمكنك التحميل الآن")
                st.download_button(
                    "📄 تحميل PDF (موافق عليه)",
                    pdf_data,
                    file_name=file_name,
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                    key=f"pdf_approved_{key_suffix}",
                )
            else:
                st.error("⚠️ الملف غير متوفر — أعد طلب الموافقة")
        elif status == "pending":
            st.warning(f"⏳ طلبك قيد المراجعة من المالك\nرقم الطلب: `{existing['id']}`\nتاريخ الطلب: {existing['created_at']}")
            st.info("💡 سيتم إعلامك عند الموافقة. يمكنك أيضاً التواصل مباشرة مع الدكتور")
        elif status == "rejected":
            st.error(f"❌ تم رفض طلبك\nالسبب: {existing.get('rejection_reason') or 'غير محدد'}")
            if st.button("🔄 إعادة طلب الموافقة", use_container_width=True, key=f"pdf_req_retry_{key_suffix}"):
                rid = create_pdf_request(user_name, user_role, pdf_bytes, doc_title, doc_context)
                if rid.startswith("REQ_"):
                    st.success(f"✅ تم إرسال طلب جديد: {rid}")
                    st.rerun()
    else:
        st.info("🔒 تحميل PDF يتطلب موافقة المالك\nاضغط على الزر لطلب الموافقة")
        if st.button("📤 طلب موافقة على تحميل PDF", type="primary", use_container_width=True, key=f"pdf_req_new_{key_suffix}"):
            rid = create_pdf_request(user_name, user_role, pdf_bytes, doc_title, doc_context)
            if rid.startswith("REQ_"):
                st.success(f"✅ تم إرسال الطلب: {rid}\nسيتم المراجعة قريباً")
                st.rerun()
            else:
                st.error(f"❌ فشل الطلب: {rid}")

    st.markdown("---")
    render_consultation_buttons()


def render_pdf_requests_admin() -> None:
    st.markdown('<div class="section-title">📋 إدارة طلبات PDF</div>', unsafe_allow_html=True)
    data = _load_pdf_requests()
    requests = data.get("requests", [])
    pending = [r for r in requests if r["status"] == "pending"]
    approved = [r for r in requests if r["status"] == "approved"]
    rejected = [r for r in requests if r["status"] == "rejected"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 الإجمالي", len(requests))
    c2.metric("⏳ قيد المراجعة", len(pending))
    c3.metric("✅ موافق عليها", len(approved))
    c4.metric("❌ مرفوضة", len(rejected))

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs([f"⏳ قيد المراجعة ({len(pending)})", f"✅ موافق عليها ({len(approved)})", f"❌ مرفوضة ({len(rejected)})"])

    with tab1:
        if not pending:
            st.info("💡 لا توجد طلبات معلقة")
        else:
            for req in reversed(pending):
                with st.expander(f"📄 {req['doc_title']} — {req['user_name']} ({req['user_role']}) — {req['created_at']}"):
                    st.markdown(f"**رقم الطلب:** `{req['id']}`")
                    st.markdown(f"**المستخدم:** {req['user_name']}")
                    st.markdown(f"**الدور:** {req['user_role']}")
                    st.markdown(f"**المستند:** {req['doc_title']}")
                    st.markdown(f"**التاريخ:** {req['created_at']}")
                    if req.get("doc_context"):
                        st.markdown("**تفاصيل:**")
                        for k, v in req["doc_context"].items():
                            st.markdown(f"- {k}: {v}")
                    pdf_preview = _read_pdf_bytes(req["id"])
                    if pdf_preview:
                        st.download_button("👁️ معاينة PDF", pdf_preview, file_name=f"{req['id']}_preview.pdf", mime="application/pdf", use_container_width=True, key=f"preview_{req['id']}")
                    ac1, ac2 = st.columns(2)
                    with ac1:
                        if st.button("✅ موافقة", type="primary", use_container_width=True, key=f"approve_{req['id']}"):
                            if approve_pdf_request(req["id"]):
                                st.success("✅ تمت الموافقة")
                                st.rerun()
                    with ac2:
                        if st.button("❌ رفض", use_container_width=True, key=f"reject_{req['id']}"):
                            st.session_state[f"show_reject_{req['id']}"] = True
                    if st.session_state.get(f"show_reject_{req['id']}"):
                        reason = st.text_input("سبب الرفض:", key=f"reject_reason_{req['id']}")
                        if st.button("تأكيد الرفض", key=f"confirm_reject_{req['id']}"):
                            if reject_pdf_request(req["id"], reason):
                                st.session_state[f"show_reject_{req['id']}"] = False
                                st.success("تم الرفض")
                                st.rerun()

    with tab2:
        if not approved:
            st.info("💡 لا توجد طلبات موافق عليها")
        else:
            for req in reversed(approved[-30:]):
                st.markdown(f"✅ **{req['doc_title']}** — {req['user_name']} ({req['created_at']})")

    with tab3:
        if not rejected:
            st.info("💡 لا توجد طلبات مرفوضة")
        else:
            for req in reversed(rejected[-30:]):
                st.markdown(f"❌ **{req['doc_title']}** — {req['user_name']} ({req['created_at']})")
                if req.get("rejection_reason"):
                    st.caption(f"السبب: {req['rejection_reason']}")


# ═══════════════════════════════════════════════════════════════════════
# ✅ الفيديو التعريفي والصور والحظائر 3D
# ═══════════════════════════════════════════════════════════════════════


def get_intro_video_path() -> Optional[str]:
    for p in ["intro_video.mp4", "intro.mp4", "تعريفي.mp4", "tutorial.mp4", "video/intro.mp4"]:
        if os.path.exists(p):
            return p
    return None


def render_welcome_with_video() -> bool:
    if "video_watched" not in st.session_state:
        st.session_state["video_watched"] = False
    if st.session_state["video_watched"]:
        return False

    video_path = get_intro_video_path()
    st.markdown(
        """
    <div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
                padding: 20px; border-radius: 16px;
                border: 3px solid #2e7d32; margin: 20px 0;
                direction: rtl; text-align: right;">
        <h3 style="color:#1b5e20; margin: 0 0 10px 0;">🎬 مرحباً بك في تاور نولجي</h3>
        <p style="color:#555; margin: 0;">شاهد الفيديو التعريفي لفهم كيفية استخدام المنصة</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    if video_path:
        try:
            st.video(video_path)
        except Exception as e:
            st.warning(f"⚠️ {e}")
    else:
        st.info("📹 ضع ملف `intro_video.mp4` في مجلد التطبيق ليظهر تلقائياً")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ شاهدت الفيديو — متابعة", type="primary", use_container_width=True, key="video_continue"):
            st.session_state["video_watched"] = True
            st.rerun()
    with col2:
        if st.button("⏭️ تخطي", use_container_width=True, key="video_skip"):
            st.session_state["video_watched"] = True
            st.rerun()
    return True


@st.cache_data(ttl=3600)
def get_img_b64(paths) -> Optional[str]:
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                pass
    return None


img_base64 = get_img_b64(tuple(PHOTO_OPTIONS))


def get_owner_photo() -> Optional[str]:
    for p in ["owner.jpg", "owner.png", "14686.jpg"]:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                pass
    return None


owner_b64 = get_owner_photo()

HORSE_STALL_SCIENCE = {
    "box_standard": {"width": 3.5, "length": 3.5, "area": 12.25, "name_ar": "مربط صندوقي قياسي", "usage": "حصان 500-600 كجم"},
    "box_large": {"width": 4.0, "length": 4.0, "area": 16.0, "name_ar": "مربط كبير", "usage": "حصان >600"},
    "box_foaling": {"width": 4.0, "length": 5.0, "area": 20.0, "name_ar": "مربط ولادة", "usage": "فرس حامل"},
    "box_pony": {"width": 3.0, "length": 3.0, "area": 9.0, "name_ar": "مربط بوني", "usage": "بوني"},
}

HORSE_BARN_SCIENCE = {
    "aisle_width_m": 3.5,
    "ceiling_height_m": 4.0,
    "wall_height_m": 3.5,
    "door_width_m": 1.3,
    "door_height_m": 2.4,
    "front_partition_m": 1.5,
    "side_partition_m": 2.0,
    "bedding_cm": 20,
    "ach_winter": 5,
    "ach_summer": 25,
    "fresh_air_m3h_per_horse": 30,
    "window_area_pct": 0.10,
    "service_room_m2": 25,
    "tack_room_m2": 12,
    "wash_bay_m2": 16,
    "hay_storage_m2": 20,
}


def calculate_horse_barn_scientific(num_horses: int, stall_type: str = "box_standard", include_service: bool = True) -> Dict:
    if stall_type not in HORSE_STALL_SCIENCE:
        stall_type = "box_standard"
    stall = HORSE_STALL_SCIENCE[stall_type]
    sci = HORSE_BARN_SCIENCE
    if num_horses <= 4:
        rows = 1
        stalls_per_row = num_horses
    else:
        rows = 2
        stalls_per_row = (num_horses + 1) // 2
    row_length = stalls_per_row * stall["width"]
    aisle_w = sci["aisle_width_m"]
    building_width = (rows * stall["length"]) + aisle_w + 1.0
    building_length = row_length + 2.0
    stall_area_total = num_horses * stall["area"]
    aisle_area = building_length * aisle_w
    service_area = (sci["service_room_m2"] + sci["tack_room_m2"] + sci["wash_bay_m2"] + sci["hay_storage_m2"]) if include_service else 0
    total_area = building_width * building_length + service_area
    building_volume = building_width * building_length * sci["ceiling_height_m"]
    vent_summer = building_volume * sci["ach_summer"]
    vent_winter = building_volume * sci["ach_winter"]
    vent_summer_cfm = vent_summer * 35.3147 / 60
    vent_winter_cfm = vent_winter * 35.3147 / 60
    tunnel_fans = max(1, int(np.ceil(vent_summer_cfm / 20000)))
    side_fans = max(1, int(np.ceil(vent_winter_cfm / 8000)))
    wall_area = 2 * building_length * sci["wall_height_m"] + 2 * building_width * sci["wall_height_m"]
    window_area = wall_area * sci["window_area_pct"]
    light_fixtures = max(1, int(np.ceil(total_area / 80)))
    water_day = num_horses * 45
    cost_structure = building_width * building_length * 90
    cost_roof = building_width * building_length * 35
    cost_stalls = num_horses * stall["area"] * 180
    cost_aisle_floor = aisle_area * 45
    cost_service = service_area * 40
    cost_ventilation = tunnel_fans * 500 + side_fans * 300
    cost_lighting = light_fixtures * 60
    cost_windows = window_area * 120
    cost_total = round(cost_structure + cost_roof + cost_stalls + cost_aisle_floor + cost_service + cost_ventilation + cost_lighting + cost_windows, 0)
    return {
        "is_horse_barn": True,
        "num_horses": num_horses,
        "stall_type": stall_type,
        "stall_type_ar": stall["name_ar"],
        "stall_dimensions": f"{stall['width']}×{stall['length']} م",
        "stall_area_m2": stall["area"],
        "stalls_per_row": stalls_per_row,
        "rows_count": rows,
        "building_width_m": round(building_width, 2),
        "building_length_m": round(building_length, 2),
        "building_height_m": sci["ceiling_height_m"],
        "total_area_m2": round(total_area, 2),
        "volume_m3": round(building_volume, 1),
        "vent_summer_m3h": int(vent_summer),
        "vent_winter_m3h": int(vent_winter),
        "vent_summer_cfm": int(vent_summer_cfm),
        "vent_winter_cfm": int(vent_winter_cfm),
        "tunnel_fans_count": tunnel_fans,
        "side_fans_count": side_fans,
        "door_dimensions": f"{sci['door_width_m']}×{sci['door_height_m']} م",
        "doors_count": num_horses,
        "window_area_m2": round(window_area, 2),
        "bedding_cm": sci["bedding_cm"],
        "bedding_m3": round(stall_area_total * sci["bedding_cm"] / 100, 1),
        "water_per_day_L": water_day,
        "cost_structure_usd": round(cost_structure, 0),
        "cost_roof_usd": round(cost_roof, 0),
        "cost_stalls_usd": round(cost_stalls, 0),
        "cost_aisle_floor_usd": round(cost_aisle_floor, 0),
        "cost_service_usd": round(cost_service, 0),
        "cost_ventilation_usd": round(cost_ventilation, 0),
        "cost_lighting_usd": round(cost_lighting, 0),
        "cost_windows_usd": round(cost_windows, 0),
        "cost_total_usd": cost_total,
        "reference": "NRC (2007) Horses + MWPS-1",
        "standard": {"name_ar": "خيول - مربط علمي"},
        "count": num_horses,
        "length_m": round(building_length, 2),
        "width_m": round(building_width, 2),
        "ridge_height_m": sci["ceiling_height_m"] + 1.5,
        "roof_type": "gable",
        "feeders_count": num_horses * 2,
        "drinkers_count": num_horses,
        "aisle_m": aisle_w,
        "central_aisle": True,
        "barn_key": "خيول_مربط",
    }


BARN_DESIGN_STANDARDS = {
    "دواجن_لاحم": {"name_ar": "دواجن لاحم", "area_per_head": 0.10, "feeder_cm_per_head": 5.0, "drinker_cm_per_head": 2.5, "height_m": 2.8, "width_m": 12.0, "ach_summer": 60, "ach_winter": 8, "vent_open_ratio": 0.20, "roof_type": "gable", "slope_pct": 20.0, "aisle_m": 1.2, "central_aisle": True, "tunnel_fan_cfm": 12000, "side_fan_cfm": 5000, "cooling_pad_enabled": True, "cooling_pad_m2_per_1000cfm": 0.5, "water_per_head_L": 0.25},
    "أبقار": {"name_ar": "أبقار", "area_per_head": 5.0, "feeder_cm_per_head": 70.0, "drinker_cm_per_head": 6.0, "height_m": 4.5, "width_m": 15.0, "ach_summer": 25, "ach_winter": 4, "vent_open_ratio": 0.35, "roof_type": "gable", "slope_pct": 20.0, "aisle_m": 3.5, "central_aisle": True, "tunnel_fan_cfm": 20000, "side_fan_cfm": 8000, "cooling_pad_enabled": False, "cooling_pad_m2_per_1000cfm": 0.4, "water_per_head_L": 80},
    "أغنام": {"name_ar": "أغنام", "area_per_head": 1.5, "feeder_cm_per_head": 35.0, "drinker_cm_per_head": 4.0, "height_m": 3.5, "width_m": 10.0, "ach_summer": 30, "ach_winter": 5, "vent_open_ratio": 0.30, "roof_type": "gable", "slope_pct": 25.0, "aisle_m": 2.0, "central_aisle": True, "tunnel_fan_cfm": 14000, "side_fan_cfm": 6000, "cooling_pad_enabled": False, "cooling_pad_m2_per_1000cfm": 0.3, "water_per_head_L": 6},
    "إبل": {"name_ar": "إبل", "area_per_head": 10.0, "feeder_cm_per_head": 100.0, "drinker_cm_per_head": 8.0, "height_m": 4.5, "width_m": 15.0, "ach_summer": 20, "ach_winter": 4, "vent_open_ratio": 0.40, "roof_type": "gable", "slope_pct": 20.0, "aisle_m": 4.0, "central_aisle": True, "tunnel_fan_cfm": 20000, "side_fan_cfm": 8000, "cooling_pad_enabled": True, "cooling_pad_m2_per_1000cfm": 0.4, "water_per_head_L": 50},
    "سمان": {"name_ar": "سمان", "area_per_head": 0.025, "feeder_cm_per_head": 2.0, "drinker_cm_per_head": 1.0, "height_m": 2.0, "width_m": 6.0, "ach_summer": 50, "ach_winter": 8, "vent_open_ratio": 0.25, "roof_type": "mono", "slope_pct": 15.0, "aisle_m": 0.8, "central_aisle": False, "tunnel_fan_cfm": 10000, "side_fan_cfm": 4000, "cooling_pad_enabled": True, "cooling_pad_m2_per_1000cfm": 0.5, "water_per_head_L": 0.06},
    "أرانب": {"name_ar": "أرانب", "area_per_head": 0.30, "feeder_cm_per_head": 8.0, "drinker_cm_per_head": 2.0, "height_m": 2.5, "width_m": 8.0, "ach_summer": 40, "ach_winter": 6, "vent_open_ratio": 0.25, "roof_type": "gable", "slope_pct": 20.0, "aisle_m": 1.2, "central_aisle": True, "tunnel_fan_cfm": 8000, "side_fan_cfm": 3000, "cooling_pad_enabled": True, "cooling_pad_m2_per_1000cfm": 0.4, "water_per_head_L": 0.35},
}


def calculate_barn_dimensions(key: str, count: int, barn_system: str = "أرضي مفتوح") -> Optional[Dict]:
    std = BARN_DESIGN_STANDARDS.get(key)
    if not std:
        return None
    area = count * std["area_per_head"]
    width = std["width_m"]
    length = max(area / width, 6.0)
    height = std["height_m"]
    volume = length * width * height
    roof_rise = (width / 2) * (std["slope_pct"] / 100)
    ridge = height + roof_rise
    roof_area = length * width * 1.15
    wall_area = 2 * length * height + 2 * width * height
    floor_area = length * width
    feeders = max(1, int(np.ceil(count * std["feeder_cm_per_head"] / 300)))
    drinkers = max(1, int(np.ceil(count * std["drinker_cm_per_head"] / 200)))
    vent_summer = volume * std["ach_summer"]
    vent_winter = volume * std["ach_winter"]
    vent_summer_cfm = vent_summer * 35.3147 / 60
    vent_winter_cfm = vent_winter * 35.3147 / 60
    tunnel_fans = max(1, int(np.ceil(vent_summer_cfm / std["tunnel_fan_cfm"])))
    side_fans = max(1, int(np.ceil(vent_winter_cfm / std["side_fan_cfm"])))
    cooling_pad = round(vent_summer_cfm * std["cooling_pad_m2_per_1000cfm"] / 1000, 2) if std.get("cooling_pad_enabled") else 0.0
    light_fixtures = max(1, int(np.ceil(floor_area / 100)))
    water_day = count * std["water_per_head_L"]
    cost_total = round(floor_area * 105 + roof_area * 25 + wall_area * 15 + tunnel_fans * 450 + side_fans * 250 + cooling_pad * 80 + light_fixtures * 40 + feeders * 180 + drinkers * 90, 0)
    return {
        "standard": std,
        "count": count,
        "total_area_m2": round(area, 2),
        "length_m": round(length, 2),
        "width_m": round(width, 2),
        "height_m": round(height, 2),
        "ridge_height_m": round(ridge, 2),
        "volume_m3": round(volume, 1),
        "roof_type": std["roof_type"],
        "feeders_count": feeders,
        "drinkers_count": drinkers,
        "tunnel_fans_count": tunnel_fans,
        "side_fans_count": side_fans,
        "cooling_pad_area_m2": cooling_pad,
        "cooling_pad_enabled": std.get("cooling_pad_enabled", False),
        "water_per_day_L": round(water_day, 1),
        "cost_total_usd": cost_total,
        "aisle_m": std.get("aisle_m", 1.5),
        "central_aisle": std.get("central_aisle", True),
        "barn_key": key,
    }


def create_barn_3d_figure(dims: Dict):
    if not PLOTLY_AVAILABLE:
        return None
    try:
        import plotly.graph_objects as go

        std = dims["standard"]
        L = max(float(dims["length_m"]), 1.0)
        W = max(float(dims["width_m"]), 1.0)
        H = max(float(dims["height_m"]), 1.0)
        RH = max(float(dims["ridge_height_m"]), 1.0)
        max_dim = max(L, W, RH)
        ax_x, ax_y, ax_z = L / max_dim, W / max_dim, max(RH / max_dim, 0.15)
        fig = go.Figure()
        fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[0, 0, 0, 0], i=[0, 0], j=[1, 2], k=[2, 3], color="#d7ccc8", opacity=0.7, name="الأرضية", hoverinfo="skip"))
        for xp in [0, L]:
            fig.add_trace(go.Mesh3d(x=[xp] * 4, y=[0, W, W, 0], z=[0, 0, H, H], i=[0, 0], j=[1, 2], k=[2, 3], color="#a1887f", opacity=0.3, showlegend=False, hoverinfo="skip"))
        for yp in [0, W]:
            fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[yp] * 4, z=[0, 0, H, H], i=[0, 0], j=[1, 2], k=[2, 3], color="#a1887f", opacity=0.3, showlegend=False, hoverinfo="skip"))
        if dims["roof_type"] == "gable":
            fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W / 2, W / 2], z=[H, H, RH, RH], i=[0, 0], j=[1, 2], k=[2, 3], color="#8d6e63", opacity=0.55, name="السقف", hoverinfo="skip"))
            fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[W / 2, W / 2, W, W], z=[RH, RH, H, H], i=[0, 0], j=[1, 2], k=[2, 3], color="#8d6e63", opacity=0.55, showlegend=False, hoverinfo="skip"))

        fan_count = dims.get("tunnel_fans_count", 0)
        for i in range(min(fan_count, 20)):
            xc = L - 0.05
            yc = (i + 0.5) * (W / max(fan_count, 1))
            fig.add_trace(go.Scatter3d(x=[xc], y=[yc], z=[H * 0.5], mode="markers+text", marker=dict(size=15, color="#1976d2", symbol="circle"), text=[f"م{i+1}"], textposition="middle center", textfont=dict(size=8, color="white"), name="مروحة" if i == 0 else None, showlegend=(i == 0)))

        side_count = dims.get("side_fans_count", 0)
        for i in range(min(side_count, 20)):
            xc = (i + 0.5) * (L / max(side_count, 1))
            fig.add_trace(go.Scatter3d(x=[xc], y=[0.1], z=[H * 0.7], mode="markers", marker=dict(size=10, color="#00897b", symbol="diamond"), name="مروحة جانبية" if i == 0 else None, showlegend=(i == 0)))

        count = dims.get("count", dims.get("num_horses", 100))
        if not dims.get("is_horse_barn"):
            aisle = dims.get("aisle_m", 1.5)
            fw = 0.6
            fpos = [W / 2 - aisle / 2 - fw, W / 2 + aisle / 2] if (dims.get("central_aisle", True) and W > 8) else [0.8, W - 1.4]
            for idx, yp in enumerate(fpos):
                if yp + fw > W:
                    continue
                fig.add_trace(go.Mesh3d(x=[0.5, L - 0.5, L - 0.5, 0.5, 0.5, L - 0.5, L - 0.5, 0.5], y=[yp, yp, yp + fw, yp + fw, yp, yp, yp + fw, yp + fw], z=[0, 0, 0, 0, 0.35, 0.35, 0.35, 0.35], i=[0, 0, 4, 4, 0, 0, 3, 3, 0, 0, 1, 1], j=[1, 2, 6, 7, 4, 5, 2, 6, 3, 7, 5, 6], k=[2, 3, 5, 6, 5, 1, 6, 7, 7, 4, 6, 2], color="#ff8f00", opacity=0.9, name="معلف" if idx == 0 else None, showlegend=(idx == 0), hoverinfo="skip"))
            apr = min(20, max(1, int(np.sqrt(count))))
            ax_, ay_, az_ = [], [], []
            for ri in range(apr):
                for ci in range(apr):
                    if len(ax_) > 200:
                        break
                    ax_.append(0.8 + ci * (L - 1.6) / apr)
                    ay_.append(1.0 + ri * (W - 2.0) / apr)
                    az_.append(0.15)
            if ax_:
                fig.add_trace(go.Scatter3d(x=ax_, y=ay_, z=az_, mode="markers", marker=dict(size=2.5, color="#1b5e20", opacity=0.7), name=f"حيوانات ({count})"))
        else:
            rows = dims.get("rows_count", 2)
            per_row = dims.get("stalls_per_row", 5)
            stall_dim = dims.get("stall_dimensions", "3.5×3.5")
            try:
                stall_w = float(stall_dim.split("×")[0])
                stall_l = float(stall_dim.split("×")[1].replace(" م", "").strip())
            except Exception:
                stall_w, stall_l = 3.5, 3.5
            wall_h = H * 0.75
            for row in range(rows):
                y_offset = 0.5 if row == 0 else W - stall_l - 0.5
                for col in range(per_row):
                    x_offset = 0.5 + col * stall_w
                    stall_num = col + 1 + row * per_row
                    y_front = y_offset if row == 0 else y_offset + stall_l
                    fig.add_trace(go.Mesh3d(x=[x_offset, x_offset + 0.5, x_offset + 0.5, x_offset], y=[y_front] * 4, z=[0, 0, wall_h, wall_h], i=[0, 0], j=[1, 2], k=[2, 3], color="#8d6e63", opacity=0.6, showlegend=False, hoverinfo="skip"))
                    fig.add_trace(go.Mesh3d(x=[x_offset + stall_w - 0.5, x_offset + stall_w, x_offset + stall_w, x_offset + stall_w - 0.5], y=[y_front] * 4, z=[0, 0, wall_h, wall_h], i=[0, 0], j=[1, 2], k=[2, 3], color="#8d6e63", opacity=0.6, showlegend=False, hoverinfo="skip"))
                    fig.add_trace(go.Mesh3d(x=[x_offset, x_offset + stall_w, x_offset + stall_w, x_offset], y=[y_front] * 4, z=[H * 0.6, H * 0.6, wall_h, wall_h], i=[0, 0], j=[1, 2], k=[2, 3], color="#8d6e63", opacity=0.5, showlegend=False, hoverinfo="skip"))
                    x_right = x_offset + stall_w
                    fig.add_trace(go.Mesh3d(x=[x_right] * 4, y=[y_offset, y_offset + stall_l, y_offset + stall_l, y_offset], z=[0, 0, wall_h, wall_h], i=[0, 0], j=[1, 2], k=[2, 3], color="#6d4c41", opacity=0.55, showlegend=False, hoverinfo="skip"))
                    y_back = y_offset + stall_l if row == 0 else y_offset
                    fig.add_trace(go.Mesh3d(x=[x_offset, x_offset + stall_w, x_offset + stall_w, x_offset], y=[y_back] * 4, z=[0, 0, wall_h, wall_h], i=[0, 0], j=[1, 2], k=[2, 3], color="#6d4c41", opacity=0.55, showlegend=False, hoverinfo="skip"))
                    fig.add_trace(go.Mesh3d(x=[x_offset, x_offset + stall_w, x_offset + stall_w, x_offset], y=[y_offset, y_offset, y_offset + stall_l, y_offset + stall_l], z=[0.05] * 4, i=[0, 0], j=[1, 2], k=[2, 3], color="#ffd54f", opacity=0.5, showlegend=False, hoverinfo="skip"))
                    horse_cx = x_offset + stall_w / 2
                    horse_cy = y_offset + stall_l / 2
                    fig.add_trace(go.Scatter3d(x=[horse_cx], y=[horse_cy], z=[0.7], mode="markers", marker=dict(size=22, color="#5d4037", symbol="square", line=dict(color="#3e2723", width=2)), name="حصان" if row == 0 and col == 0 else None, showlegend=(row == 0 and col == 0), hovertemplate=f"حصان {stall_num}<extra></extra>"))
                    fig.add_trace(go.Scatter3d(x=[horse_cx + 0.3], y=[horse_cy], z=[1.0], mode="markers", marker=dict(size=12, color="#4e342e", symbol="circle"), showlegend=False, hoverinfo="skip"))
                    feed_x = x_offset + stall_w * 0.3
                    yb_a = y_back - 0.2 if row == 0 else y_back + 0.2
                    yb_b = y_back - 0.5 if row == 0 else y_back + 0.5
                    fig.add_trace(go.Mesh3d(x=[feed_x, feed_x + 0.6, feed_x + 0.6, feed_x, feed_x, feed_x + 0.6, feed_x + 0.6, feed_x], y=[yb_a, yb_a, yb_b, yb_b, yb_a, yb_a, yb_b, yb_b], z=[0.6, 0.6, 0.6, 0.6, 0.9, 0.9, 0.9, 0.9], i=[0, 0, 4, 4, 0, 0, 3, 3, 0, 0, 1, 1], j=[1, 2, 6, 7, 4, 5, 2, 6, 3, 7, 5, 6], k=[2, 3, 5, 6, 5, 1, 6, 7, 7, 4, 6, 2], color="#ff8f00", opacity=0.95, name="معلف" if row == 0 and col == 0 else None, showlegend=(row == 0 and col == 0), hoverinfo="skip"))
                    bucket_x = x_offset + stall_w * 0.75
                    fig.add_trace(go.Scatter3d(x=[bucket_x], y=[yb_a], z=[0.65], mode="markers", marker=dict(size=10, color="#0288d1", symbol="circle"), name="دلو ماء" if row == 0 and col == 0 else None, showlegend=(row == 0 and col == 0), hoverinfo="skip"))
                    fig.add_trace(go.Scatter3d(x=[horse_cx], y=[horse_cy], z=[wall_h + 0.35], mode="text", text=[f"#{stall_num}"], textfont=dict(size=11, color="#1b5e20", family="Arial"), showlegend=False, hoverinfo="skip"))

        fig.update_layout(
            title=f"مربط {std.get('name_ar', '')} — {L:.1f}م × {W:.1f}م | {dims.get('vent_summer_m3h', 0):,} م³/س",
            scene=dict(xaxis=dict(title="الطول (م)", range=[0, L]), yaxis=dict(title="العرض (م)", range=[0, W]), zaxis=dict(title="الارتفاع (م)", range=[0, max(RH, 2.0)]), aspectmode="manual", aspectratio=dict(x=ax_x, y=ax_y, z=ax_z), camera=dict(eye=dict(x=1.4, y=1.4, z=1.1))),
            height=600,
            margin=dict(l=0, r=0, t=50, b=0),
            paper_bgcolor="white",
        )
        return fig
    except Exception:
        return None


def generate_barn_pdf(dims: Dict) -> Optional[bytes]:
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color="#1a1a1a"):
            return Paragraph(ar(text), ParagraphStyle("s", fontName=font_mgr.font_name, fontSize=size, alignment=align, textColor=HexColor(color), spaceAfter=6, leading=size * 1.6))

        std = dims["standard"]
        story.append(P(f"مخطط حظيرة: {std.get('name_ar', '')}", size=18, align=TA_CENTER, color="#1b5e20"))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor("#d4af37")))
        story.append(Spacer(1, 12))
        if dims.get("is_horse_barn"):
            rows_data = [
                [ar("المواصفة"), ar("القيمة")],
                [ar("عدد الخيول"), f"{dims['num_horses']} حصان"],
                [ar("نوع المربط"), ar(dims["stall_type_ar"])],
                [ar("أبعاد المربط"), ar(dims["stall_dimensions"])],
                [ar("إجمالي المساحة"), f"{dims['total_area_m2']} م²"],
                [ar("أبعاد المبنى"), f"{dims['building_length_m']} م × {dims['building_width_m']} م"],
                [ar("التهوية الصيفية"), f"{dims['vent_summer_m3h']:,} م³/س ({dims['vent_summer_cfm']:,} CFM)"],
                [ar("التهوية الشتوية"), f"{dims['vent_winter_m3h']:,} م³/س ({dims['vent_winter_cfm']:,} CFM)"],
                [ar("مراوح نفقية / جانبية"), f"{dims['tunnel_fans_count']} / {dims['side_fans_count']}"],
                [ar("أبواب المرابط"), f"{dims['doors_count']} باب ({dims['door_dimensions']})"],
                [ar("الفرشة"), f"{dims['bedding_cm']} سم ({dims['bedding_m3']} م³)"],
                [ar("الماء اليومي"), f"{dims['water_per_day_L']:,} لتر/يوم"],
                [ar("التكلفة الإجمالية"), f"${dims['cost_total_usd']:,.0f}"],
            ]
        else:
            rows_data = [
                [ar("المواصفة"), ar("القيمة")],
                [ar("العدد"), f"{dims['count']}"],
                [ar("المساحة"), f"{dims['total_area_m2']} م²"],
                [ar("الأبعاد"), f"{dims['length_m']} م × {dims['width_m']} م"],
                [ar("التهوية الصيفية"), f"{dims['vent_summer_m3h']:,} م³/س ({dims['vent_summer_cfm']:,} CFM)"],
                [ar("التهوية الشتوية"), f"{dims['vent_winter_m3h']:,} م³/س ({dims['vent_winter_cfm']:,} CFM)"],
                [ar("المراوح"), f"{dims['tunnel_fans_count']} نفقية + {dims['side_fans_count']} جانبية"],
                [ar("التكلفة"), f"${dims['cost_total_usd']:,.0f}"],
            ]
        t = Table(rows_data, colWidths=[220, 270])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HexColor("#1b5e20")), ("TEXTCOLOR", (0, 0), (-1, 0), white), ("ALIGN", (0, 0), (-1, -1), "RIGHT"), ("FONTNAME", (0, 0), (-1, -1), font_mgr.font_name), ("GRID", (0, 0), (-1, -1), 0.8, HexColor("#bdbdbd")), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f5f5f5")])]))
        story.append(t)
        try:
            pdf_gen._add_references_page(story, "خيول" if dims.get("is_horse_barn") else dims.get("barn_key", "أبقار"), "مربط" if dims.get("is_horse_barn") else "")
        except Exception:
            pass
        story.append(Spacer(1, 20))
        story.append(P(SUPERVISOR, size=16, align=TA_CENTER, color="#c62828"))
        story.append(P(SUPERVISOR_TITLE, size=11, align=TA_CENTER, color="#1b5e20"))
        doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════
# تنسيق CSS والهيدر
# ═══════════════════════════════════════════════════════════════════════

st.markdown(
    """
<style>
.stApp{background-color:#f4f7f4;color:#1a1a1a}
.main-header{background:linear-gradient(135deg,#1b5e20,#2e7d32);padding:26px 32px;border-radius:18px;color:#fff;margin-bottom:18px;box-shadow:0 8px 24px rgba(27,94,32,0.22);border:2px solid #d4af37;position:relative;overflow:hidden}
.main-header h1{margin:0;font-size:2.4rem;font-weight:900;color:#fff;text-align:center}
.main-header .tagline{margin:6px 0 0;font-size:1.15rem;color:#e8f5e9;text-align:center}
.dua-banner{background:linear-gradient(135deg,#1b5e20,#0d3b12);padding:14px 22px;border-radius:14px;margin-bottom:18px;text-align:center;color:#fff;border:2px solid #d4af37}
.dua-title{font-size:1.3rem;font-weight:800;color:#ffeb3b;margin:4px 0}
.dua-sub{font-size:0.95rem;color:#c8e6c9}
.section-title{font-size:1.45rem;font-weight:800;color:#1b5e20;margin:20px 0 12px;padding-bottom:8px;border-bottom:3px solid #d4af37}
.info-card{background:#fff;padding:18px 22px;border-radius:14px;border-right:5px solid #2e7d32;box-shadow:0 3px 12px rgba(0,0,0,0.06);margin-bottom:14px;color:#1a1a1a}
.footer{background:#1b5e20;color:#e8f5e9;padding:18px;border-radius:14px;text-align:center;margin-top:28px;border-top:4px solid #d4af37}
</style>
""",
    unsafe_allow_html=True,
)


def render_main_header() -> None:
    st.markdown(
        f"""
    <div class="main-header">
        <h1>🌾 {APP_NAME}</h1>
        <div class="tagline">{APP_TAGLINE}</div>
    </div>
    <div class="dua-banner">
        <div class="dua-sub">{DUA_VERSE}</div>
        <div class="dua-title">🤲 {DUA_FULL} 🤲</div>
        <div class="dua-sub">{DUA_QURAN}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════
# التهيئة والتحقق من الجلسة
# ═══════════════════════════════════════════════════════════════════════

for k, v in [
    ("approved", False),
    ("user_role", None),
    ("show_owner_login", False),
    ("auto_formula", None),
    ("nlp_result", None),
    ("milk_replacer_result", None),
    ("barn_dims", None),
    ("lab_result", None),
    ("ocr_result", None),
]:
    if k not in st.session_state:
        st.session_state[k] = v

generate_csrf_token()
_safe_username()


def _session_valid() -> bool:
    role = st.session_state.get("user_role")
    if not st.session_state.get("approved", False):
        return False
    if role not in ("owner", "specialist", "guest"):
        return False
    if role == "owner" and not _get_owner_code_hash():
        return False
    return True


if not _session_valid():
    if render_welcome_with_video():
        st.stop()
    render_main_header()
    st.markdown(f'<div class="info-card">{DUA_VISITOR}</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👑 مالك", type="primary", use_container_width=True, key="btn_role_owner"):
            st.session_state.show_owner_login = True
            st.rerun()
    with c2:
        if st.button("🔬 مختص", use_container_width=True, key="btn_role_spec"):
            st.session_state.approved = True
            st.session_state.user_role = "specialist"
            st.session_state["chat_username"] = f"مختص_{random.randint(1000, 9999)}"
            st.rerun()
    with c3:
        if st.button("🌱 زائر", use_container_width=True, key="btn_role_guest"):
            st.session_state.approved = True
            st.session_state.user_role = "guest"
            st.session_state["chat_username"] = f"زائر_{random.randint(1000, 9999)}"
            st.rerun()
    if st.session_state.get("show_owner_login"):
        st.markdown("---")
        with st.form("owner_login_form", clear_on_submit=True):
            code = st.text_input("🔐 رمز المالك", type="password", key="owner_code_input")
            ok = st.form_submit_button("✅ دخول", use_container_width=True)
        if ok:
            if not check_rate_limit("login", max_calls=10, window=60):
                st.error("⚠️ محاولات كثيرة")
                st.stop()
            if check_owner_code(code):
                st.session_state.approved = True
                st.session_state.user_role = "owner"
                st.session_state["chat_username"] = "د. عبدالقادر (المالك)"
                st.session_state.show_owner_login = False
                st.rerun()
            else:
                st.error("❌ رمز خاطئ")
    st.stop()


render_main_header()
role = st.session_state.get("user_role", "guest")
role_label = {"owner": "👑 مالك", "specialist": "🔬 مختص", "guest": "🌱 زائر"}.get(role, "🌱 زائر")
st.markdown(f"**المستخدم:** `{st.session_state.get('chat_username', '')}` | **الدور:** `{role_label}`")
if st.button("🔄 تبديل الدور / تسجيل الخروج", key="btn_logout"):
    st.session_state.approved = False
    st.session_state.user_role = None
    st.session_state.show_owner_login = False
    st.rerun()


# ═══════════════════════════════════════════════════════════════════════
# التبويبات الرئيسية
# ═══════════════════════════════════════════════════════════════════════

base_tabs = [
    "🧮 التركيب (LP)",
    "🎯 أمثل ربحية (NLP)",
    "🔬 مختبر التحليل",
    "📸 مسح OCR",
    "🍼 بديل الحليب",
    "🏗️ الحظائر 3D",
    "🎬 استديو",
    "💬 الدردشة",
    "📚 المراجع",
]
if role == "owner":
    base_tabs.append("📋 طلبات PDF")

tabs = st.tabs(base_tabs)
tab_idx = 0

# 1. التركيب LP
with tabs[tab_idx]:
    tab_idx += 1
    st.markdown('<div class="section-title">🧮 تركيب العلائق بأقل تكلفة (LP)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        animal_lp = st.selectbox("🐾 الفصيل:", ["أبقار", "أغنام", "ماعز", "إبل", "خيول", "دواجن", "سمان", "أسماك", "أرانب"], key="lp_animal")
        basis_lp = st.radio("🧬 أساس البروتين:", ["DP", "CP"], horizontal=True, key="lp_basis")
    with c2:
        if animal_lp == "أبقار":
            prod_lp = st.selectbox("الحالة:", ["حليب_عالي", "حليب_متوسط", "حليب_منخفض", "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"], key="lp_prod_cattle")
            req_lp = get_cattle_requirements(prod_lp)
        elif animal_lp == "أغنام":
            prod_lp = st.selectbox("الحالة:", ["تسمين_مكثف", "تسمين_عادي", "مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة", "حملان_تيد"], key="lp_prod_sheep")
            req_lp = get_sheep_requirements(prod_lp, is_male=("تسمين" in prod_lp or "تيد" in prod_lp))
        elif animal_lp == "ماعز":
            prod_lp = st.selectbox("الحالة:", ["حلابة_عالي", "حلابة_متوسط", "تسمين_جديان", "تيوس", "حامل_أخير", "صيانة"], key="lp_prod_goat")
            req_lp = get_goat_requirements(prod_lp, is_male=("تسمين" in prod_lp or "تيوس" in prod_lp))
        elif animal_lp == "إبل":
            prod_lp = st.selectbox("الحالة:", ["حليب", "تسمين", "نمو", "سباق", "صيانة"], key="lp_prod_camel")
            req_lp = get_camel_requirements(prod_lp)
        elif animal_lp == "خيول":
            prod_lp = st.selectbox("الحالة:", ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار", "مرضعات", "صيانة"], key="lp_prod_horse")
            req_lp = get_horse_requirements(prod_lp)
        elif animal_lp == "دواجن":
            prod_lp = st.selectbox("الحالة:", ["لاحم", "بياض"], key="lp_prod_poultry")
            req_lp = get_poultry_requirements(prod_lp, 1)
        elif animal_lp == "سمان":
            prod_lp = st.selectbox("الحالة:", ["لاحم", "بياض"], key="lp_prod_quail")
            req_lp = get_quail_requirements(prod_lp, 1)
        elif animal_lp == "أسماك":
            prod_lp = st.selectbox("المرحلة:", ["بادئ", "نمو", "تسمين"], key="lp_prod_fish")
            req_lp = get_fish_requirements("البلطي النيلي", prod_lp)
        else:
            prod_lp = st.selectbox("الحالة:", ["تسمين", "حليب", "صيانة"], key="lp_prod_rabbit")
            req_lp = get_rabbit_requirements(prod_lp)

    all_ings = list(_get_ingredient_lookup().keys())
    defaults = [i for i in get_default_selections(animal_lp, prod_lp, req_lp) if i in all_ings]
    starter_set = ["ذرة صفراء", "شعير مطحون", "كسب فول صويا 44%", "أمباز الفول السوداني", "نخالة قمح (ردة)"]
    for s in starter_set:
        if s in all_ings and s not in defaults:
            defaults.append(s)
    selected_lp = st.multiselect("🌾 المواد العلفية المتاحة:", all_ings, default=defaults[:10], key="lp_selected_ings")
    custom_prices = {}
    if selected_lp:
        with st.expander("💵 أسعار المواد ($/طن)"):
            pcols = st.columns(3)
            for idx, ing in enumerate(selected_lp):
                default_p = float(_get_ingredient_lookup()[ing].get("price", 300.0))
                custom_prices[ing] = pcols[idx % 3].number_input(ing, 10.0, 20000.0, default_p, 10.0, key=f"lp_p_{ing}")

    if st.button("🚀 حساب التركيبة المثلى", type="primary", use_container_width=True, key="btn_run_lp"):
        std_lp = requirement_to_standard(req_lp)
        res_lp = auto_formulate_smart(selected_lp, custom_prices, std_lp, standard_key=f"{animal_lp}_{prod_lp}", basis=basis_lp, animal_type=animal_lp, production_type=prod_lp)
        st.session_state["auto_formula"] = {"res": res_lp, "req": req_lp, "animal": animal_lp, "prod": prod_lp, "basis": basis_lp}

    lp_pack = st.session_state.get("auto_formula")
    if lp_pack and lp_pack.get("res", {}).get("success"):
        r = lp_pack["res"]
        if r.get("warning"):
            st.warning(r["warning"])
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 التكلفة / طن", f"${r['cost']:.2f}")
        m2.metric("⭐ الجودة", f"{r['quality_score']:.1f}%")
        m3.metric("⚙️ الاستراتيجية", r["strategy"])
        df_f = pd.DataFrame([{"المادة العلفية": k, "النسبة %": round(v, 2), "كجم / طن": round(v * 10, 1)} for k, v in r["formula"].items()])
        st.dataframe(df_f, use_container_width=True, hide_index=True)
        if REPORTLAB_AVAILABLE:
            pdf_b = pdf_gen.generate_report(r["formula"], lp_pack["req"], lp_pack["animal"], lp_pack["prod"], r["cost"], "عام", r["cost"], "$", requester_name=st.session_state.get("chat_username", ""), protein_basis=lp_pack["basis"], standard_key=f"{lp_pack['animal']}_{lp_pack['prod']}", quality_score=r["quality_score"])
            render_pdf_download_with_approval(pdf_b, f"tawor_lp_{lp_pack['animal']}.pdf", f"تركيبة LP - {lp_pack['animal']} ({lp_pack['prod']})", role, user_name=st.session_state.get("chat_username", ""), doc_context={"الحيوان": lp_pack["animal"], "التكلفة": f"${r['cost']:.2f}"}, key_suffix="lp")

# 2. أمثل ربحية NLP
with tabs[tab_idx]:
    tab_idx += 1
    st.markdown('<div class="section-title">🎯 التحسين غير الخطي لأقصى ربحية (NLP)</div>', unsafe_allow_html=True)
    nc1, nc2, nc3 = st.columns(3)
    with nc1:
        nlp_animal = st.selectbox("🐾 الفصيل:", ["أبقار", "أغنام", "ماعز", "إبل", "خيول", "دواجن", "سمان", "أسماك", "أرانب"], key="nlp_animal")
    with nc2:
        nlp_prod = st.text_input("الحالة الإنتاجية:", value="حليب_عالي" if nlp_animal == "أبقار" else "تسمين_مكثف", key="nlp_prod")
    with nc3:
        nlp_price_prod = st.number_input("سعر وحدة المنتج ($):", 0.1, 100.0, 2.5, 0.1, key="nlp_prod_price")
    all_ings = list(_get_ingredient_lookup().keys())
    nlp_sel = st.multiselect("🌾 المواد المختارة:", all_ings, default=[x for x in ["ذرة صفراء", "شعير مطحون", "كسب فول صويا 44%", "أمباز الفول السوداني", "نخالة قمح (ردة)", "ملح الطعام", "الحجر الجيري"] if x in all_ings], key="nlp_sel")
    nlp_prices = {i: float(_get_ingredient_lookup()[i].get("price", 300.0)) for i in nlp_sel}
    if st.button("🎯 تشغيل التحسين غير الخطي", type="primary", use_container_width=True, key="btn_run_nlp"):
        res_nlp = nlp_optimize_feed(nlp_sel, _get_ingredient_lookup(), nlp_prices, animal_type=nlp_animal, production_type=nlp_prod, price_product=nlp_price_prod)
        st.session_state["nlp_result"] = res_nlp

    rn = st.session_state.get("nlp_result")
    if rn:
        if rn.get("success"):
            if rn.get("warning"):
                st.warning(rn["warning"])
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("💰 التكلفة / كجم", f"${rn['final_cost']:.4f}")
            c2.metric("⚡ الطاقة ME", f"{rn['final_me']:.0f}")
            c3.metric("🧬 البروتين CP", f"{rn['final_cp']:.2f}%")
            c4.metric("📈 صافي الربح", f"${rn['max_profit']:.4f}")
            st.dataframe(pd.DataFrame([{"المكون": k, "النسبة %": v, "كجم/طن": round(v * 10, 1)} for k, v in rn["formula"].items()]), use_container_width=True, hide_index=True)
            fig_p = create_nlp_profit_curve(rn, nlp_sel, _get_ingredient_lookup(), nlp_prices)
            if fig_p:
                st.plotly_chart(fig_p, use_container_width=True)
            pdf_nlp = generate_nlp_math_pdf(rn, nlp_animal, nlp_prod, nlp_sel, _get_ingredient_lookup(), nlp_prices)
            render_pdf_download_with_approval(pdf_nlp, f"tawor_nlp_{nlp_animal}.pdf", f"تقرير NLP - {nlp_animal}", role, user_name=st.session_state.get("chat_username", ""), key_suffix="nlp")
        else:
            st.error(rn.get("message", "تعذر إيجاد حل"))

# 3. مختبر التحليل
with tabs[tab_idx]:
    tab_idx += 1
    st.markdown('<div class="section-title">🔬 مختبر تحليل التركيبات وشريط القياس</div>', unsafe_allow_html=True)
    lab_animal = st.selectbox("🐾 الفصيل:", ["أبقار", "أغنام", "ماعز", "إبل", "خيول", "دواجن", "سمان", "أسماك", "أرانب"], key="lab_animal")
    lab_prod = st.text_input("الحالة:", value="حليب_عالي" if lab_animal == "أبقار" else "تسمين_مكثف", key="lab_prod")
    weight_est = weight_tape_widget(lab_animal, "lab_tape")
    st.caption(f"الوزن المستخدم في التقدير المرجعي: {weight_est:.1f} كجم")
    raw_formula_txt = st.text_area("أدخل التركيبة (مثال: ذرة صفراء: 55، كسب فول صويا 44%: 25، نخالة قمح (ردة): 18، ملح الطعام: 2):", height=100, key="lab_raw_txt")
    if st.button("🔬 تحليل التركيبة", type="primary", use_container_width=True, key="btn_run_lab"):
        parsed = _parse_ingredients_from_text(raw_formula_txt)
        if parsed:
            st.session_state["lab_result"] = analyze_existing_formula(parsed, lab_animal, lab_prod)
        else:
            st.warning("⚠️ لم يتم التعرف على مكونات بنسب صالحة")
    lr = st.session_state.get("lab_result")
    if lr and lr.get("success"):
        st.metric("⭐ درجة الجودة", f"{lr['quality_score']:.1f}%")
        st.dataframe(pd.DataFrame(lr["comparison"])[["العنصر", "المعيار", "المحسوب", "الفرق %", "التقييم"]], use_container_width=True, hide_index=True)
        pdf_lab = generate_lab_pdf(lr, {"animal": lab_animal, "production": lab_prod})
        render_pdf_download_with_approval(pdf_lab, f"tawor_lab_{lab_animal}.pdf", f"تحليل تركيبة - {lab_animal}", role, user_name=st.session_state.get("chat_username", ""), key_suffix="lab")

# 4. مسح OCR
with tabs[tab_idx]:
    tab_idx += 1
    st.markdown('<div class="section-title">📸 استخراج التركيبات من الصور (OCR)</div>', unsafe_allow_html=True)
    up_ocr = st.file_uploader("ارفع صورة بطاقة أو تركيبة علف:", type=["png", "jpg", "jpeg"], key="ocr_uploader")
    if up_ocr and st.button("🔍 استخراج البيانات", type="primary", key="btn_run_ocr"):
        st.session_state["ocr_result"] = extract_ingredients_from_image(up_ocr.getvalue())
    or_res = st.session_state.get("ocr_result")
    if or_res:
        if or_res.get("success"):
            corrected = render_ocr_correction_ui(or_res.get("ingredients", {}))
            if corrected:
                nut_c = compute_formula_nutrients(corrected)
                st.json(nut_c)
                pdf_ocr = pdf_gen.generate_ocr_report(corrected, nut_c, or_res.get("raw_text", ""))
                render_pdf_download_with_approval(pdf_ocr, "tawor_ocr.pdf", "تقرير تحليل OCR", role, user_name=st.session_state.get("chat_username", ""), key_suffix="ocr")
        else:
            st.warning(or_res.get("message", "تعذر الاستخراج"))

# 5. بديل الحليب
with tabs[tab_idx]:
    tab_idx += 1
    st.markdown('<div class="section-title">🍼 تركيب بدائل الحليب (Milk Replacer)</div>', unsafe_allow_html=True)
    mr_animal = st.selectbox("🐾 الفصيل:", list(MILK_REPLACER_STANDARDS.keys()), key="mr_animal")
    mr_vol = st.number_input("الكمية الإجمالية (كجم):", 10.0, 5000.0, 100.0, 10.0, key="mr_vol")
    mr_sel = st.multiselect("المكونات المتاحة:", list(MILK_REPLACER_INGREDIENTS.keys()), default=list(MILK_REPLACER_INGREDIENTS.keys())[:9], key="mr_sel")
    if st.button("🍼 تركيب بديل الحليب", type="primary", use_container_width=True, key="btn_run_mr"):
        st.session_state["milk_replacer_result"] = formulate_milk_replacer(mr_animal, mr_vol, mr_sel)
    mrr = st.session_state.get("milk_replacer_result")
    if mrr and mrr.get("success"):
        st.success(f"⭐ الجودة: {mrr['quality_score']:.1f}% | 💰 التكلفة/كجم: ${mrr['cost_per_kg']:.2f}")
        st.dataframe(pd.DataFrame([{"المكون": k, "النسبة %": round(v, 2), "الكمية (كجم)": round(v * mrr["volume"] / 100, 2)} for k, v in mrr["formula"].items()]), use_container_width=True, hide_index=True)
        pdf_mr = generate_milk_replacer_pdf(mrr)
        render_pdf_download_with_approval(pdf_mr, "tawor_milk_replacer.pdf", f"بديل حليب - {mr_animal}", role, user_name=st.session_state.get("chat_username", ""), key_suffix="mr")

# 6. الحظائر 3D
with tabs[tab_idx]:
    tab_idx += 1
    st.markdown('<div class="section-title">🏗️ تصميم الحظائر والإسطبلات ثلاثي الأبعاد (3D)</div>', unsafe_allow_html=True)
    b_choice = st.selectbox("نوع المنشأة:", ["خيول_مربط", "أبقار", "أغنام", "إبل", "دواجن_لاحم", "سمان", "أرانب"], key="barn_type_sel")
    if b_choice == "خيول_مربط":
        hc1, hc2 = st.columns(2)
        with hc1:
            n_horses = st.number_input("عدد الخيول:", 1, 50, 8, 1, key="n_horses")
        with hc2:
            stall_t = st.selectbox("نوع المربط:", list(HORSE_STALL_SCIENCE.keys()), format_func=lambda x: HORSE_STALL_SCIENCE[x]["name_ar"], key="stall_t")
        if st.button("🏗️ إنشاء مخطط الإسطبل 3D", type="primary", use_container_width=True, key="btn_horse_3d"):
            st.session_state["barn_dims"] = calculate_horse_barn_scientific(n_horses, stall_t, True)
    else:
        cnt = st.number_input("عدد الحيوانات:", 10, 50000, 200, 10, key="barn_cnt")
        if st.button("🏗️ إنشاء مخطط الحظيرة 3D", type="primary", use_container_width=True, key="btn_barn_3d"):
            st.session_state["barn_dims"] = calculate_barn_dimensions(b_choice, cnt)

    bdims = st.session_state.get("barn_dims")
    if bdims:
        fig3d = create_barn_3d_figure(bdims)
        if fig3d:
            st.plotly_chart(fig3d, use_container_width=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("📐 المساحة الكلية", f"{bdims['total_area_m2']} م²")
        c2.metric("💨 التهوية الصيفية", f"{bdims['vent_summer_m3h']:,} م³/س")
        c3.metric("💵 التكلفة التقديرية", f"${bdims['cost_total_usd']:,.0f}")
        pdf_barn = generate_barn_pdf(bdims)
        render_pdf_download_with_approval(pdf_barn, "tawor_barn_3d.pdf", f"مخطط حظيرة - {bdims['standard'].get('name_ar', '')}", role, user_name=st.session_state.get("chat_username", ""), key_suffix="barn")

# 7. استديو
with tabs[tab_idx]:
    tab_idx += 1
    st.markdown('<div class="section-title">🎬 استديو المحتوى والملاحظات</div>', unsafe_allow_html=True)
    studio_data = _load_studio()
    if role == "owner":
        with st.form("studio_note_form", clear_on_submit=True):
            n_title = st.text_input("عنوان الملاحظة / الدرس:")
            n_body = st.text_area("المحتوى:")
            if st.form_submit_button("💾 حفظ في الاستديو"):
                if n_title and n_body:
                    studio_data["notes"].append({"title": _sanitize_message(n_title, 100), "body": _sanitize_message(n_body, 1500), "date": datetime.now().strftime("%Y-%m-%d %H:%M")})
                    _save_studio(studio_data)
                    st.rerun()
    for item in reversed(studio_data.get("notes", [])):
        st.markdown(f'<div class="info-card"><b>{item["title"]}</b> <small>({item["date"]})</small><br>{item["body"]}</div>', unsafe_allow_html=True)

# 8. الدردشة
with tabs[tab_idx]:
    tab_idx += 1
    st.markdown('<div class="section-title">💬 غرف النقاش العلمي</div>', unsafe_allow_html=True)
    rooms_dict = _load_chat_rooms()
    room_names = list(rooms_dict.keys())
    active_room = st.selectbox("اختر الغرفة:", room_names, key="chat_active_room")
    if role == "owner":
        new_r = st.text_input("إنشاء غرفة جديدة:", key="chat_new_room")
        if st.button("➕ إضافة غرفة", key="btn_add_room") and new_r:
            if create_chat_room(new_r):
                st.rerun()
    for m in rooms_dict.get(active_room, [])[-40:]:
        st.markdown(f"**{m['user']}** <small>[{m['ts']}]</small>: {m['msg']}", unsafe_allow_html=True)
    with st.form("chat_send_form", clear_on_submit=True):
        msg_txt = st.text_input("اكتب رسالتك:")
        if st.form_submit_button("📤 إرسال"):
            if check_rate_limit("chat", max_calls=20, window=60) and msg_txt:
                add_chat_message(active_room, st.session_state.get("chat_username", "مستخدم"), msg_txt)
                st.rerun()

# 9. المراجع
with tabs[tab_idx]:
    tab_idx += 1
    st.markdown('<div class="section-title">📚 المراجع العلمية المعتمدة</div>', unsafe_allow_html=True)
    for i, ref in enumerate(GENERAL_REFERENCES, 1):
        st.markdown(f"{i}. **{ref}**")

# 10. إدارة طلبات PDF للمالك
if role == "owner":
    with tabs[tab_idx]:
        render_pdf_requests_admin()


st.markdown(
    f"""
<div class="footer">
    <div>🤲 <b>{DUA_FULL}</b> 🤲</div>
    <div style="margin-top:6px;">{APP_NAME} v{APP_VERSION} — إشراف: {SUPERVISOR}</div>
</div>
""",
    unsafe_allow_html=True,
)
