# ═══════════════════════════════════════════════════════════════════════
# تاور نولجي TAWOR NOLOGY 11.11.0
# د. عبدالقادر إسماعيل تاور
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
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
from typing import Dict, List, Optional
import urllib.parse
import urllib.request
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
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        HRFlowable,
        Image as RLImage,
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
DUA_VERSE = "﴿ وَقُل رَّبِّ ارْحَمْهُمَا كَمَا رَبَّيَانِي صَغِيرًا ﴾"
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
    "أبقار_حليب_عالي": {"primary": "NRC (2001) — Nutrient Requirements of Dairy Cattle, 7th Ed.", "table": "Table 15-1: Lactating dairy cows (high production)", "secondary": ["INRA (2018) — Feeding System for Ruminants", "NRC (2001) — Table 15-2"]},
    "أبقار_حليب_متوسط": {"primary": "NRC (2001) — Dairy Cattle, 7th Ed.", "table": "Table 15-1: Lactating dairy cows (medium)", "secondary": ["INRA (2018)"]},
    "أبقار_حليب_منخفض": {"primary": "NRC (2001) — Dairy Cattle", "table": "Table 15-1: Low production", "secondary": ["INRA (2018)"]},
    "أبقار_تسمين_مكثف": {"primary": "NRC (2001) + NRC (1996)", "table": "Table 15-1: Growing/finishing", "secondary": ["INRA (2018)"]},
    "أبقار_تسمين_عادي": {"primary": "NRC (1996) — Beef Cattle", "table": "Table 10-1: Growth", "secondary": []},
    "أبقار_حمل_أخير": {"primary": "NRC (2001)", "table": "Table 15-3: Gestating", "secondary": []},
    "أبقار_صيانة": {"primary": "NRC (2001)", "table": "Table 15-4: Maintenance", "secondary": []},
    "أغنام_تسمين_مكثف": {"primary": "NRC (2007) — Small Ruminants", "table": "Table 11-1: Growing lambs", "secondary": ["INRA (2018)"]},
    "أغنام_تسمين_عادي": {"primary": "NRC (2007)", "table": "Table 11-1", "secondary": []},
    "أغنام_مرضعات": {"primary": "NRC (2007)", "table": "Table 11-2: Lactating ewes", "secondary": ["INRA (2018)"]},
    "أغنام_حامل_أخير": {"primary": "NRC (2007)", "table": "Table 11-2", "secondary": []},
    "أغنام_حامل_متوسط": {"primary": "NRC (2007)", "table": "Table 11-2", "secondary": []},
    "أغنام_صيانة": {"primary": "NRC (2007)", "table": "Table 11-3", "secondary": []},
    "أغنام_حملان_تيد": {"primary": "NRC (2007)", "table": "Table 11-1", "secondary": []},
    "ماعز_حلابة_عالي": {"primary": "NRC (2007)", "table": "Table 12-1", "secondary": ["INRA (2018)"]},
    "ماعز_حلابة_متوسط": {"primary": "NRC (2007)", "table": "Table 12-1", "secondary": []},
    "ماعز_تسمين_جديان": {"primary": "NRC (2007)", "table": "Table 12-2", "secondary": []},
    "ماعز_تيوس": {"primary": "NRC (2007)", "table": "Table 12-2", "secondary": []},
    "ماعز_صيانة": {"primary": "NRC (2007)", "table": "Table 12-3", "secondary": []},
    "ماعز_حامل_أخير": {"primary": "NRC (2007)", "table": "Table 12-2", "secondary": []},
    "إبل_حليب": {"primary": "FAO (2010) — Camel Nutrition", "table": "Section 4", "secondary": ["Al-Jassim et al. (2002)"]},
    "إبل_تسمين": {"primary": "FAO (2010)", "table": "Section 5", "secondary": []},
    "إبل_نمو": {"primary": "FAO (2010)", "table": "Section 3", "secondary": []},
    "إبل_سباق": {"primary": "FAO (2010)", "table": "Section 6", "secondary": []},
    "إبل_صيانة": {"primary": "FAO (2010)", "table": "Section 2", "secondary": []},
    "خيول_رياضة_مكثف": {"primary": "NRC (2007) — Horses, 6th Ed.", "table": "Table 10-1: Intense work", "secondary": []},
    "خيول_رياضة_عادي": {"primary": "NRC (2007)", "table": "Table 10-1", "secondary": []},
    "خيول_نمو_أمهار": {"primary": "NRC (2007)", "table": "Table 10-2", "secondary": []},
    "خيول_مرضعات": {"primary": "NRC (2007)", "table": "Table 10-3", "secondary": []},
    "خيول_صيانة": {"primary": "NRC (2007)", "table": "Table 10-4", "secondary": []},
    "دواجن_لاحم": {"primary": "Ross 308 (2020)", "table": "Nutrient requirements", "secondary": ["NRC (1994) — Poultry"]},
    "دواجن_بياض": {"primary": "NRC (1994) — Poultry", "table": "Table 4", "secondary": ["Lohmann (2020)"]},
    "سمان_تسمين": {"primary": "NRC (1994)", "table": "Table 12", "secondary": []},
    "سمان_بياض": {"primary": "NRC (1994)", "table": "Table 12", "secondary": []},
    "أسماك_بادئ": {"primary": "NRC (2011) — Fish Nutrition", "table": "Table 6-1", "secondary": ["FAO (2018)"]},
    "أسماك_نمو": {"primary": "NRC (2011)", "table": "Table 6-2", "secondary": []},
    "أسماك_تسمين": {"primary": "NRC (2011)", "table": "Table 6-3", "secondary": []},
    "أرانب_تسمين": {"primary": "NRC (2007)", "table": "Rabbit chapter", "secondary": ["INRA (2018)"]},
    "أرانب_حليب": {"primary": "NRC (2007)", "table": "Lactating does", "secondary": []},
    "أرانب_صيانة": {"primary": "NRC (2007)", "table": "Maintenance", "secondary": []},
    "خيول_مربط": {"primary": "NRC (2007) — Horses + MWPS-1 Structures Handbook", "table": "Stall dimensions & ventilation standards", "secondary": ["ASAE (2005) — Ventilation Standards", "FAO (2012) — Rural Structures"]},
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
    "أبقار_حليب_عالي": {"DP": "DP = 9.0 + (الحليب × 0.175)  [سقف 16%]", "CP": "CP = DP ÷ 0.72", "SE": "SE = 60 + (الحليب × 0.35)", "Ca": "Ca = 0.55 + (الحليب × 0.003)", "P": "P = 0.33 + (الحليب × 0.0015)", "example": "بقرة 20 لتر → DP = 12.5% | CP ≈ 17.4%", "source": "NRC (2001) — Table 15-1"},
    "أبقار_حليب_متوسط": {"DP": "DP = 8.5 + (الحليب × 0.17)  [سقف 14%]", "CP": "CP = DP ÷ 0.72", "SE": "SE = 55 + (الحليب × 0.30)", "source": "NRC (2001)"},
    "أبقار_حليب_منخفض": {"DP": "DP = 8.0 + (الحليب × 0.16)  [سقف 12.5%]", "CP": "CP = DP ÷ 0.75", "source": "NRC (2001)"},
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
    "دواجن_لاحم": {"DP": "20% → 16.5%", "CP": "23% → 19%", "SE": "76 → 75", "example": "بادي: CP=23%, SE=76", "source": "Ross 308 (2020)"},
    "دواجن_بياض": {"DP": "15.5%", "CP": "18%", "source": "NRC (1994)"},
    "سمان_تسمين": {"DP": "18.5% → 17%", "SE": "72 → 70", "source": "NRC (1994)"},
    "سمان_بياض": {"DP": "15%", "SE": "68", "source": "NRC (1994)"},
    "أسماك_بادئ": {"DP": "32%", "CP": "40%", "source": "NRC (2011)"},
    "أسماك_نمو": {"DP": "25%", "CP": "32%", "source": "NRC (2011)"},
    "أسماك_تسمين": {"DP": "22%", "CP": "28%", "source": "NRC (2011)"},
    "أرانب_تسمين": {"DP": "15%", "CP": "17%", "source": "NRC (2007)"},
    "أرانب_حليب": {"DP": "18%", "CP": "20%", "source": "NRC (2007)"},
    "أرانب_صيانة": {"DP": "12%", "CP": "14%", "source": "NRC (2007)"},
    "خيول_مربط": {"المربط": "3.5 م × 3.5 م = 12.25 م² لكل حصان", "الممر": "3.5 م", "التهوية الصيف": "25 تجديد/ساعة", "التهوية الشتاء": "5 تجديد/ساعة", "الماء": "45 لتر/حصان/يوم", "source": "NRC (2007) + MWPS-1"},
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
        "CP": cp, "DC": dc, "SE": se, "NDF": ndf, "ADF": adf,
        "EE": ee, "ASH": ash, "Ca": ca, "P": p, "Lys": lys, "Met": met,
        "price": price, "desc": desc, "src": src,
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


@lru_cache(maxsize=1)
def _get_ingredient_lookup() -> Dict:
    lookup = {}
    for cat in BIG_FEEDS_LIBRARY.values():
        for name, data in cat.items():
            lookup[name] = data
    return lookup


def get_oil_ingredients() -> Dict:
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت النباتية والحيوانية", {})


MAX_OIL_PERCENTAGE = {
    "دواجن_لاحم": {"max": 7.5, "optimal": 4.5, "source": "Ross 308"},
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
    "دواجن": {"يوريا علفية": (0, 0), "نخالة قمح (ردة)": (0, 10), "نخالة ذرة": (0, 5), "تبن قمح": (0, 2), "قش أرز": (0, 2), "كسب بذور القطن": (0, 5), "كسب السمسم": (0, 8), "كسب الكانولا": (0, 8), "ملح الطعام": (0.2, 0.4), "الحجر الجيري": (0.8, 2.5), "فوسفات ثنائي الكالسيوم": (0.5, 2.5), "بريمكس تسمين دواجن": (0.2, 0.35), "بريمكس بياض": (0.2, 0.35), "ليسين نقي": (0, 0.5), "ميثيونين نقي": (0, 0.4)},
    "أبقار": {"يوريا علفية": (0, 1.5), "نخالة قمح (ردة)": (0, 30), "كسب بذور القطن": (0, 20), "كسب السمسم": (0, 15), "ملح الطعام": (0.3, 0.5), "بيكربونات الصوديوم": (0.5, 1.0), "الحجر الجيري": (0, 3.5), "فوسفات ثنائي الكالسيوم": (0, 2.0), "بريمكس أبقار": (0.15, 0.3), "بريمكس مجترات": (0.15, 0.3), "مضاد سموم فطرية": (0.05, 0.15)},
    "أغنام": {"يوريا علفية": (0, 1.0), "نخالة قمح (ردة)": (0, 25), "كسب بذور القطن": (0, 15), "ملح الطعام": (0.3, 0.5), "بيكربونات الصوديوم": (0.5, 1.0), "بريمكس مجترات": (0.15, 0.3), "الحجر الجيري": (0, 3.0), "فوسفات ثنائي الكالسيوم": (0, 2.0)},
    "ماعز": {"يوريا علفية": (0, 1.0), "نخالة قمح (ردة)": (0, 25), "ملح الطعام": (0.3, 0.5), "بيكربونات الصوديوم": (0.5, 1.0), "بريمكس مجترات": (0.15, 0.3), "الحجر الجيري": (0, 3.0), "فوسفات ثنائي الكالسيوم": (0, 2.0)},
    "إبل": {"يوريا علفية": (0, 1.0), "نخالة قمح (ردة)": (0, 20), "ملح الطعام": (0.3, 0.5), "بيكربونات الصوديوم": (0.5, 1.0), "بريمكس إبل": (0.15, 0.3), "الحجر الجيري": (0, 3.0), "فوسفات ثنائي الكالسيوم": (0, 2.0)},
    "خيول": {"يوريا علفية": (0, 0.0), "نخالة قمح (ردة)": (0, 20), "ملح الطعام": (0.3, 0.5), "بريمكس خيول": (0.15, 0.3), "الحجر الجيري": (0, 2.5), "فوسفات ثنائي الكالسيوم": (0, 2.0)},
    "أسماك": {"يوريا علفية": (0, 0.0), "نخالة قمح (ردة)": (0, 10), "ملح الطعام": (0, 0.3), "بريمكس أسماك": (0.15, 0.3), "الحجر الجيري": (0, 2.0), "فوسفات ثنائي الكالسيوم": (0, 2.0)},
    "أرانب": {"يوريا علفية": (0, 0.0), "نخالة قمح (ردة)": (0, 20), "ملح الطعام": (0.3, 0.5), "بريمكس مجترات": (0.15, 0.3), "الحجر الجيري": (0, 2.5), "فوسفات ثنائي الكالسيوم": (0, 2.0)},
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


def get_cattle_requirements(t: str, milk_yield: float = 20.0, weight_kg: float = 500.0) -> AnimalRequirement:
    if t == "حليب_عالي":
        dp = min(9.0 + milk_yield * 0.175, 16.0)
        return AnimalRequirement(round(dp, 2), round(dp / 0.72, 2), round(60 + milk_yield * 0.35, 1), 30, 19, 5.5, 8, round(0.55 + milk_yield * 0.003, 3), round(0.33 + milk_yield * 0.0015, 3), "أبقار حلابة عالية", f"حليب {milk_yield} لتر/يوم")
    if t == "حليب_متوسط":
        dp = min(8.5 + milk_yield * 0.17, 14.0)
        return AnimalRequirement(round(dp, 2), round(dp / 0.72, 2), round(55 + milk_yield * 0.30, 1), 33, 21, 4.5, 8, round(0.5 + milk_yield * 0.0025, 3), round(0.3 + milk_yield * 0.0012, 3), "أبقار حلابة متوسطة", f"حليب {milk_yield} لتر/يوم")
    if t == "حليب_منخفض":
        dp = min(8.0 + milk_yield * 0.16, 12.5)
        return AnimalRequirement(round(dp, 2), round(dp / 0.75, 2), round(50 + milk_yield * 0.25, 1), 38, 24, 4, 8.5, round(0.45 + milk_yield * 0.002, 3), round(0.28 + milk_yield * 0.001, 3), "أبقار حلابة منخفضة", f"حليب {milk_yield} لتر/يوم")
    if t == "تسمين_مكثف":
        return AnimalRequirement(11.5, 14.5, 72, 32, 20, 4.5, 7.5, 0.65, 0.38, "تسمين مكثف", "نمو يومي مرتفع")
    if t == "تسمين_عادي":
        return AnimalRequirement(9.5, 12, 65, 38, 24, 4, 7.5, 0.55, 0.32, "تسمين عادي", "نمو متوسط")
    if t == "حمل_أخير":
        return AnimalRequirement(11.5, 14.5, 67, 35, 22, 4.2, 8, 0.7, 0.42, "حمل آخر", "الثلث الأخير من الحمل")
    return AnimalRequirement(7.5, 10, 53, 45, 28, 3, 8.5, 0.42, 0.26, "أبقار صيانة", "احتياجات الصيانة")


def get_sheep_requirements(t: str, is_male: bool = True, weight_kg: float = 50.0, litter_size: int = 1) -> AnimalRequirement:
    if is_male:
        if t == "تسمين_مكثف":
            return AnimalRequirement(11.5, 14.5, 64, 28, 17, 4, 8, 0.65, 0.36, "تسمين مكثف", "تسمين ذكور مكثف")
        if t == "تسمين_عادي":
            return AnimalRequirement(9.5, 12, 59, 33, 21, 3.6, 8, 0.55, 0.32, "تسمين عادي", "تسمين ذكور عادي")
        return AnimalRequirement(8.5, 11, 55, 38, 24, 3.2, 8.5, 0.5, 0.3, "حملان تيد", "مرحلة تمهيدية")
    if t == "مرضعات":
        dp = 10.5 + (litter_size - 1) * 1.5
        return AnimalRequirement(round(dp, 2), round(dp / 0.72, 2), round(60 + (litter_size - 1) * 5, 1), 30, 19, 4.5, 8.5, round(0.65 + (litter_size - 1) * 0.1, 3), round(0.38 + (litter_size - 1) * 0.05, 3), f"نعاج مرضعات ({litter_size})", "إرضاع")
    if t == "حامل_أخير":
        return AnimalRequirement(10.5, 13.5, 62, 32, 20, 3.8, 8, 0.6, 0.35, "نعاج حامل (شهر 4-5)", "حمل متأخر")
    if t == "حامل_متوسط":
        return AnimalRequirement(8.5, 11, 55, 38, 24, 3.4, 8, 0.5, 0.3, "نعاج حامل (شهر 1-3)", "حمل مبكر/متوسط")
    return AnimalRequirement(7.2, 9.5, 48, 45, 28, 3, 8.5, 0.42, 0.26, "نعاج صيانة", "صيانة")


def get_goat_requirements(t: str, is_male: bool = True, milk_yield: float = 2.0) -> AnimalRequirement:
    if is_male:
        if t == "تسمين_جديان":
            return AnimalRequirement(11, 14, 62, 30, 19, 3.8, 8, 0.62, 0.34, "تسمين جديان", "نمو سريع")
        return AnimalRequirement(9, 11.5, 57, 36, 22, 3.5, 8, 0.55, 0.3, "تيوس تسمين", "تسمين")
    if t == "حلابة_عالي":
        dp = min(9.5 + milk_yield * 0.35, 13.5)
        return AnimalRequirement(round(dp, 2), round(dp / 0.72, 2), round(58 + milk_yield * 0.45, 1), 29, 18, 4.5, 8.5, round(0.6 + milk_yield * 0.008, 3), round(0.35 + milk_yield * 0.004, 3), f"عنزات حلابة ({milk_yield} لتر)", "إنتاج عالٍ")
    if t == "حلابة_متوسط":
        dp = min(8.5 + milk_yield * 0.30, 12.0)
        return AnimalRequirement(round(dp, 2), round(dp / 0.72, 2), round(55 + milk_yield * 0.40, 1), 32, 20, 4, 8.5, round(0.55 + milk_yield * 0.006, 3), round(0.32 + milk_yield * 0.003, 3), f"عنزات حلابة ({milk_yield} لتر)", "إنتاج متوسط")
    if t == "حامل_أخير":
        return AnimalRequirement(10, 13, 60, 33, 21, 3.8, 8, 0.6, 0.35, "عنزات حامل", "حمل متأخر")
    return AnimalRequirement(6.8, 9, 46, 46, 28, 3, 8.5, 0.42, 0.26, "عنزات صيانة", "صيانة")


def get_camel_requirements(t: str, weight_kg: float = 400.0, milk_yield: float = 5.0) -> AnimalRequirement:
    if t == "نمو":
        return AnimalRequirement(10.5, 13.5, 60, 38, 24, 4, 8, 0.65, 0.38, "إبل نمو", f"وزن {weight_kg} كجم")
    if t == "تسمين":
        return AnimalRequirement(9.5, 12, 65, 35, 22, 4.5, 7.5, 0.6, 0.35, "إبل تسمين", f"وزن {weight_kg} كجم")
    if t == "حليب":
        dp = min(10.5 + milk_yield * 0.20, 14.0)
        return AnimalRequirement(round(dp, 2), round(dp / 0.72, 2), round(62 + milk_yield * 0.4, 1), 32, 20, 5, 8.5, round(0.7 + milk_yield * 0.006, 3), round(0.4 + milk_yield * 0.003, 3), f"إبل حلابة ({milk_yield} لتر)", "إدرار الحليب")
    if t == "سباق":
        return AnimalRequirement(14, 17, 72, 28, 17, 6, 9, 0.85, 0.5, "إبل سباق", "مجهود وطاقة عالية")
    return AnimalRequirement(7, 9, 48, 48, 30, 3.5, 9, 0.42, 0.26, "إبل صيانة", f"وزن {weight_kg} كجم")


def get_horse_requirements(t: str, weight_kg: float = 450.0) -> AnimalRequirement:
    if t == "رياضة_مكثف":
        return AnimalRequirement(10.5, 13.5, 70, 30, 18, 7, 7.5, 0.7, 0.4, "خيول رياضة مكثف", "عمل شاق")
    if t == "رياضة_عادي":
        return AnimalRequirement(9, 11.5, 63, 36, 22, 5, 7.5, 0.55, 0.32, "خيول رياضة عادي", "عمل خفيف/متوسط")
    if t == "نمو_أمهار":
        return AnimalRequirement(12, 15, 65, 30, 18, 5, 8, 0.75, 0.42, "أمهار نمو", "نمو هيكلي وعضلي")
    if t == "مرضعات":
        return AnimalRequirement(12.5, 16, 68, 32, 20, 5.5, 8, 0.8, 0.45, "فرسات مرضعات", "إرضاع المهر")
    return AnimalRequirement(7.2, 9.5, 53, 46, 29, 3.5, 8, 0.45, 0.28, "خيول صيانة", "صيانة")


def get_poultry_requirements(strain: str, age_weeks: int = 1) -> AnimalRequirement:
    if strain == "لاحم":
        if age_weeks <= 1:
            return AnimalRequirement(20, 23, 76, 8, 4, 5, 6.5, 1, 0.5, "لاحم — بادي", "الأسبوع الأول")
        if age_weeks <= 3:
            return AnimalRequirement(18.5, 21, 74, 9, 5, 5, 6, 0.9, 0.45, "لاحم — نامي", "الأسبوع 2-3")
        if age_weeks <= 5:
            return AnimalRequirement(17, 19.5, 75, 10, 5.5, 4.5, 6, 0.87, 0.43, "لاحم — ناهي", "الأسبوع 4-5")
        return AnimalRequirement(16.5, 19, 75, 10, 5.5, 4.5, 6, 0.85, 0.42, "لاحم — ناهي+", "ما بعد الأسبوع 5")
    if age_weeks <= 6:
        return AnimalRequirement(17, 20, 72, 10, 5.5, 4, 7, 1, 0.5, "بياض — بادي", "0-6 أسابيع")
    if age_weeks <= 18:
        return AnimalRequirement(14.5, 17, 70, 12, 6.5, 4, 9, 1.5, 0.45, "بياض — نامي", "7-18 أسبوع")
    return AnimalRequirement(15.5, 18, 72, 11, 6, 4.2, 11.5, 3.8, 0.45, "بياض — إنتاج", "فترة وضع البيض")


def get_quail_requirements(strain: str, age_weeks: int = 1) -> AnimalRequirement:
    if strain == "بياض":
        return AnimalRequirement(15, 18, 68, 11, 5.5, 4.5, 9, 2.5, 0.45, "سمان بياض", "إنتاج البيض")
    if age_weeks <= 2:
        return AnimalRequirement(20.5, 24, 74, 8, 4, 5.5, 6.5, 1, 0.55, "سمان بادي", "0-2 أسبوع")
    if age_weeks <= 4:
        return AnimalRequirement(18.5, 22, 72, 9, 4.5, 5, 6, 0.9, 0.5, "سمان نامي", "2-4 أسابيع")
    return AnimalRequirement(17, 20, 70, 10, 5, 4.5, 6, 0.85, 0.45, "سمان ناهي", "4+ أسابيع")


def get_fish_requirements(species: str, stage: str) -> AnimalRequirement:
    if "بادئ" in stage or "زريعة" in stage:
        return AnimalRequirement(32, 40, 72, 8, 4, 10, 11, 1.5, 0.9, f"{species} — بادئ", "زريعة/إصبعيات")
    if "نمو" in stage:
        return AnimalRequirement(25, 32, 70, 12, 6, 8, 9, 1, 0.7, f"{species} — نمو", "مرحلة النمو")
    return AnimalRequirement(22, 28, 68, 13, 7, 8, 9.5, 0.9, 0.65, f"{species} — تسمين", "مرحلة التسمين")


def get_rabbit_requirements(t: str, weight_kg: float = 4.0) -> AnimalRequirement:
    if t == "تسمين":
        return AnimalRequirement(15, 17, 65, 25, 15, 3, 8, 0.7, 0.35, "أرانب تسمين", "نمو يومي")
    if t == "حليب":
        return AnimalRequirement(18, 20, 68, 25, 15, 4, 8.5, 0.85, 0.45, "أرانب أمهات/حليب", "حمل وإرضاع")
    return AnimalRequirement(12, 14, 60, 30, 20, 2.5, 8.5, 0.6, 0.3, "أرانب صيانة", "صيانة")


def requirement_to_standard(req: AnimalRequirement) -> Dict:
    return {"CP": req.CP, "DP": req.DP, "SE": req.SE, "NDF": req.NDF, "ADF": req.ADF, "EE": req.EE, "ASH": req.ASH, "Ca": req.Ca, "P": req.P}


# ═══════════════════════════════════════════════════════════════════════
# الحسابات والتحليل وتشكيل الألوان (مصححة رياضياً)
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
    return {k: round(v, 3) for k, v in totals.items()}


def compute_total_oil_percentage(formula: Dict) -> float:
    oils = set(get_oil_ingredients().keys())
    return round(sum(p for i, p in formula.items() if i in oils), 2)


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
        weights["SE"] = 0.20
    if targets.get("NDF"):
        weights["NDF"] = 0.15 if is_rum else 0.10
    if targets.get("ADF"):
        weights["ADF"] = 0.10
    if targets.get("Ca"):
        weights["Ca"] = 0.08
    if targets.get("P"):
        weights["P"] = 0.07
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
            rs = 100 if 1.5 <= r <= 2.2 else (80 if 1.3 <= r < 1.5 or 2.2 < r <= 2.5 else 30)
        else:
            rs = 100 if 1.4 <= r <= 2.2 else (85 if 1.1 <= r < 1.4 or 2.2 < r <= 2.6 else 35)
        weighted += rs * 0.10
        total_w += 0.10
    return round(weighted / total_w if total_w else 0.0, 1), actual


def build_comparison_rows(standard: Dict, actual: Dict) -> List[Dict]:
    labels = {
        "CP": "البروتين الخام (CP %)",
        "DP": "البروتين المهضوم (DP %)",
        "SE": "معادل النشا / الطاقة (SE)",
        "NDF": "الألياف المتعادلة (NDF %)",
        "ADF": "الألياف الحمضية (ADF %)",
        "EE": "الدهن الخام (EE %)",
        "ASH": "الرماد (ASH %)",
        "Ca": "الكالسيوم (Ca %)",
        "P": "الفسفور (P %)",
    }
    rows = []
    for k, lbl in labels.items():
        sv = standard.get(k, 0.0)
        if sv <= 0:
            continue
        cv = actual.get(k, 0.0)
        diff = cv - sv
        pct_diff = (diff / sv * 100.0) if sv else 0.0
        ev = evaluate_difference(pct_diff, standard_value=sv)
        rows.append({
            "العنصر الغذائي": lbl,
            "القياسي": round(sv, 2),
            "المحسوب": round(cv, 2),
            "الفرق": round(diff, 2),
            "الفرق %": round(pct_diff, 1),
            "التقييم": ev["label"],
            "_bg": ev["bg"],
            "_color": ev["color"],
        })
    return rows


def render_colored_comparison_table(rows: List[Dict]) -> None:
    if not rows:
        return
    html = [
        '<div style="overflow-x:auto; margin:12px 0;">',
        '<table style="width:100%; border-collapse:collapse; background:#fff; border-radius:10px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.06); direction:rtl; text-align:center;">',
        '<thead><tr style="background:#1b5e20; color:#fff;">',
        '<th style="padding:10px;">العنصر الغذائي</th>',
        '<th style="padding:10px;">القياسي</th>',
        '<th style="padding:10px;">المحسوب</th>',
        '<th style="padding:10px;">الفرق</th>',
        '<th style="padding:10px;">الفرق %</th>',
        '<th style="padding:10px;">التقييم</th>',
        '</tr></thead><tbody>',
    ]
    for r in rows:
        sign = "+" if r["الفرق %"] > 0 else ""
        html.append(
            f'<tr style="border-bottom:1px solid #e0e0e0;">'
            f'<td style="padding:9px; font-weight:700; text-align:right;">{r["العنصر الغذائي"]}</td>'
            f'<td style="padding:9px;">{r["القياسي"]}</td>'
            f'<td style="padding:9px; font-weight:700;">{r["المحسوب"]}</td>'
            f'<td style="padding:9px;">{r["الفرق"]:+.2f}</td>'
            f'<td style="padding:9px;">{sign}{r["الفرق %"]:.1f}%</td>'
            f'<td style="padding:9px;"><span style="background:{r["_bg"]}; color:{r["_color"]}; padding:4px 10px; border-radius:999px; font-weight:700; display:inline-block;">{r["التقييم"]}</span></td>'
            f'</tr>'
        )
    html.append("</tbody></table></div>")
    st.markdown("".join(html), unsafe_allow_html=True)


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
        "ذره": "ذرة صفراء", "ذرة": "ذرة صفراء", "صويا": "كسب فول صويا 44%",
        "شعير": "شعير مطحون", "قمح": "قمح محلي", "نخاله": "نخالة قمح (ردة)",
        "نخالة": "نخالة قمح (ردة)", "ملح": "ملح الطعام", "حجر": "الحجر الجيري",
        "فوسفات": "فوسفات ثنائي الكالسيوم", "يوريا": "يوريا علفية",
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
    return _normalize_ingredient_name(text) if _normalize_ingredient_name(text) in lookup else None


def _parse_ingredients_from_text(full_text: str) -> Dict:
    if not full_text:
        return {}
    fixes = {"٥": "5", "٦": "6", "٧": "7", "٨": "8", "٩": "9", "٠": "0", "١": "1", "٢": "2", "٣": "3", "٤": "4"}
    text = full_text
    for old, new in fixes.items():
        text = text.replace(old, new)
    text = text.replace("٪", "%").replace("،", "\n").replace(",", "\n")
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
                num_match = re.search(r"[:\-=:\.\s]*(\d{1,3}\.?\d{0,2})\s*(?:%|كجم|كج|kg|جرام|g)?", remainder)
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
                    name_part = re.sub(r"[:\-=:\.\s]+$", "", line[: kw_match.start()].strip())
                    if len(name_part) > 2:
                        matched = match_ingredient_name(name_part)
                        if matched:
                            ingredients[matched] = round(val, 2)
    return ingredients


def auto_formulate_smart(available_ingredients, prices, custom_standard, standard_key="", basis="DP", min_quality=70.0, animal_type="", production_type="") -> Dict:
    if not SCIPY_AVAILABLE or linprog is None:
        return {"success": False, "message": "مكتبة SciPy غير متوفرة في البيئة"}
    available_ingredients = list(dict.fromkeys(_normalize_ingredient_name(i) for i in available_ingredients))
    lookup = _get_ingredient_lookup()
    ing_data = {i: lookup[i] for i in available_ingredients if i in lookup}
    valid = list(ing_data.keys())
    if len(valid) < 2:
        return {"success": False, "message": "اختر مكونين على الأقل من مكتبة الأعلاف"}

    is_ruminant = animal_type in ("أبقار", "أغنام", "ماعز", "إبل")
    is_poultry = animal_type in ("دواجن", "سمان")
    n = len(valid)
    # x_i يمثل النسبة المئوية (0..100). السعر المدخل لكل 100 كجم -> التكلفة لكل 100 كجم = sum(price_i * x_i / 100)
    c = [prices.get(i, 300.0) / 100.0 for i in valid]

    rows = {nut: [ing_data[i].get(nut, 0.0) for i in valid] for nut in ["CP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P", "Lys", "Met"]}
    rows["DP"] = [ing_data[i].get("CP", 0.0) * ing_data[i].get("DC", 0.0) for i in valid]

    target_key = "DP" if basis == "DP" else "CP"
    target_protein = custom_standard.get(target_key, 15.0)
    target_se = custom_standard.get("SE", 0.0)
    target_ca = custom_standard.get("Ca", 0.0)
    target_p = custom_standard.get("P", 0.0)
    target_ndf = custom_standard.get("NDF", 0.0)
    target_adf = custom_standard.get("ADF", 0.0)

    limits = get_animal_limits(animal_type)
    bounds = []
    for ing in valid:
        lim = limits.get(ing, (0.0, 65.0))
        lb = max(0.0, float(lim[0]))
        ub = min(100.0, float(lim[1]))
        if lb > ub:
            lb = ub
        bounds.append((lb, ub))

    # القيد الأساسي: مجموع النسب = 100%
    A_eq_base = [[1.0] * n]
    b_eq_base = [100.0]

    A_ub_base, b_ub_base = [], []

    # حد أدنى للبروتين المستهدف (لتجنب تعذر الحل عند صرامة المساواة)
    A_ub_base.append([-x for x in rows[target_key]])
    b_ub_base.append(-target_protein * 100.0)

    # حد أدنى للطاقة SE (بنفس وحدة x_i النسبية 0..100)
    if target_se > 0:
        A_ub_base.append([-x for x in rows["SE"]])
        b_ub_base.append(-target_se * 92.0)

    # توازن Ca:P
    if target_ca > 0 and target_p > 0:
        ca_p_min, ca_p_max = (1.5, 2.2) if is_poultry else ((1.4, 2.5) if is_ruminant else (1.5, 2.0))
        A_ub_base.append([-rows["Ca"][i] + ca_p_min * rows["P"][i] for i in range(n)])
        b_ub_base.append(0.0)
        A_ub_base.append([rows["Ca"][i] - ca_p_max * rows["P"][i] for i in range(n)])
        b_ub_base.append(0.0)

    # حدود الألياف NDF و ADF
    if target_ndf > 0 and is_ruminant:
        A_ub_base.append([-x for x in rows["NDF"]])
        b_ub_base.append(-target_ndf * 85.0)
        A_ub_base.append(rows["NDF"])
        b_ub_base.append(target_ndf * 120.0)
    if target_adf > 0:
        A_ub_base.append(rows["ADF"])
        mult_adf = 1.30 if is_ruminant else (1.15 if is_poultry else 1.25)
        b_ub_base.append(target_adf * mult_adf * 100.0)

    # سقف الزيوت
    oil_std = get_oil_standard(standard_key)
    oil_ind = [1.0 if i in get_oil_ingredients() else 0.0 for i in valid]
    if sum(oil_ind) > 0:
        A_ub_base.append(oil_ind)
        b_ub_base.append(oil_std["max"] * 100.0)

    strategies = [
        ("دقيق 100%", 1.00),
        ("مرن 97%", 0.97),
        ("مرن 94%", 0.94),
        ("مرن 90%", 0.90),
        ("مرن 85%", 0.85),
        ("مرن 80%", 0.80),
    ]
    best, best_q = None, -1.0
    for label, mult in strategies:
        A_ub_try = [list(r) for r in A_ub_base]
        b_ub_try = list(b_ub_base)
        # تحديث حد البروتين والطاقة حسب معامل المرونة
        A_ub_try[0] = [-x for x in rows[target_key]]
        b_ub_try[0] = -target_protein * 100.0 * mult
        if target_se > 0:
            se_idx = 1
            b_ub_try[se_idx] = -target_se * 92.0 * mult
        try:
            res = linprog(c, A_ub=A_ub_try, b_ub=b_ub_try, A_eq=A_eq_base, b_eq=b_eq_base, bounds=bounds, method="highs", options={"presolve": True, "time_limit": 15})
            if res.success and res.x is not None:
                formula = {valid[i]: round(float(res.x[i]), 2) for i in range(n) if res.x[i] > 0.05}
                tot_pct = sum(formula.values())
                if tot_pct > 0:
                    formula = {k: round(v / tot_pct * 100.0, 2) for k, v in formula.items()}
                q, actual = evaluate_quality_weighted(formula, custom_standard, animal_type, basis)
                cost_per_ton = sum(formula.get(k, 0.0) / 100.0 * prices.get(k, 300.0) * 10.0 for k in formula)
                if q > best_q:
                    best_q = q
                    best = {
                        "success": True,
                        "formula": formula,
                        "cost": round(cost_per_ton, 2),
                        "actual_nutrients": actual,
                        "quality_score": q,
                        "strategy": label,
                        "meets_standard": q >= min_quality,
                        "targets": custom_standard,
                        "basis": basis,
                        "oil_std": oil_std,
                        "total_oil": compute_total_oil_percentage(formula),
                    }
                if q >= 92.0:
                    break
        except Exception:
            continue

    if best:
        if not best["meets_standard"]:
            best["warning"] = f"⚠️ درجة الجودة ({best_q:.1f}%) أقل من الحد المطلوب ({min_quality:.0f}%) — يُنصح بإضافة مصادر بروتين أو طاقة أنسب."
        return best

    return {"success": False, "message": "تعذر إيجاد خلطة تحقق الحدود والمواصفات المحددة؛ جرب إضافة مكونات متنوعة أو تعديل الحدود."}


def _get_requirement_for_nlp(animal_type: str, production_type: str) -> Dict:
    try:
        if animal_type == "أبقار":
            req = get_cattle_requirements(production_type)
        elif animal_type == "أغنام":
            req = get_sheep_requirements(production_type, is_male=("تسمين" in production_type or "تيد" in production_type))
        elif animal_type == "ماعز":
            req = get_goat_requirements(production_type, is_male=("تسمين" in production_type or "تيوس" in production_type))
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
        # ME تقريبية بالكيلو كالوري/كجم من SE: 1 SE ≈ 4.1 kcal/g * 10 أو معادلة تحويل عملية للخلطة (SE * 41 kcal/kg)
        return {"ME": round(req.SE * 41.0, 1), "CP": req.CP, "DP": req.DP}
    except Exception:
        return {"ME": 2665.0, "CP": 16.0, "DP": 12.0}


def nlp_optimize_feed(ingredient_names, ingredient_data, prices, animal_type="أبقار", production_type="حليب_عالي", target_me=None, target_cp=None, price_product=2.5, max_per_ing=0.6) -> Dict:
    n = len(ingredient_names)
    if n < 2 or not SCIPY_AVAILABLE or minimize is None:
        return {"success": False, "message": "يلزم اختيار مكونين على الأقل وتوفر SciPy"}

    req = _get_requirement_for_nlp(animal_type, production_type)
    target_me = float(req["ME"] if target_me is None else target_me)
    target_cp = float(req["CP"] if target_cp is None else target_cp)

    # x يمثل الكسر الوزني (0..1) بحيث مجموع x = 1.0
    # قيمة ME لكل كجم خلطة = sum(SE_i * 41 * x_i)
    # قيمة CP (%) للخلطة = sum(CP_i * x_i)
    # تكلفة الكجم الواحد ($) = sum((price_per_100kg / 100) * x_i)
    me_vals = np.array([ingredient_data[i].get("SE", 0.0) * 41.0 for i in ingredient_names], dtype=float)
    cp_vals = np.array([ingredient_data[i].get("CP", 0.0) for i in ingredient_names], dtype=float)
    cost_vals = np.array([prices.get(i, 300.0) / 100.0 for i in ingredient_names], dtype=float)

    animal_limits = get_animal_limits(animal_type)
    bounds = []
    for ing in ingredient_names:
        lim = animal_limits.get(ing)
        if lim:
            lb = max(0.0, float(lim[0]) / 100.0)
            ub = min(float(max_per_ing), float(lim[1]) / 100.0)
            if lb > ub:
                lb = ub
        else:
            lb, ub = 0.0, float(max_per_ing)
        bounds.append((lb, ub))

    oils_idx = [i for i, ing in enumerate(ingredient_names) if ing in get_oil_ingredients()]
    oil_max = get_oil_standard(f"{animal_type}_{production_type}")["max"] / 100.0

    def objective(x):
        me = float(np.dot(me_vals, x))
        cp = float(np.dot(cp_vals, x))
        quality_index = (me / max(target_me, 1.0)) * (cp / max(target_cp, 0.1))
        # تعظيم صافي العائد النسبي لكل كجم خلطة
        return -(price_product * quality_index - float(np.dot(cost_vals, x)))

    x0 = np.clip(np.ones(n) / n, [b[0] for b in bounds], [b[1] for b in bounds])
    if x0.sum() > 0:
        x0 = x0 / x0.sum()
    else:
        x0 = np.ones(n) / n

    best = None
    for level_name, mult in [("صارم 100%", 1.0), ("مرن 95%", 0.95), ("مرن 90%", 0.90), ("مرن 85%", 0.85)]:
        tme, tcp = target_me * mult, target_cp * mult
        constraints = [
            {"type": "eq", "fun": lambda x: float(np.sum(x)) - 1.0},
            {"type": "ineq", "fun": lambda x, t=tme: float(np.dot(me_vals, x)) - t},
            {"type": "ineq", "fun": lambda x, t=tcp: float(np.dot(cp_vals, x)) - t},
        ]
        if oils_idx:
            constraints.append({"type": "ineq", "fun": lambda x, idx=oils_idx, om=oil_max: om - float(sum(x[i] for i in idx))})
        try:
            res = minimize(objective, x0, method="SLSQP", bounds=bounds, constraints=constraints, options={"maxiter": 1000, "ftol": 1e-8})
            x_norm = np.clip(res.x, 0.0, None)
            if x_norm.sum() <= 0:
                continue
            x_norm = x_norm / x_norm.sum()
            actual_me = float(np.dot(me_vals, x_norm))
            actual_cp = float(np.dot(cp_vals, x_norm))
            if actual_me >= tme * 0.96 and actual_cp >= tcp * 0.96:
                best = (res, x_norm, level_name, mult, actual_me, actual_cp)
                break
        except Exception:
            continue

    if not best:
        return {"success": False, "message": "تعذر إيجاد حل أمثل يحقق حدود الطاقة والبروتين للمكونات المختارة"}

    _, x_opt, level_name, mult, actual_me, actual_cp = best
    formula = {name: round(float(x_opt[i] * 100.0), 2) for i, name in enumerate(ingredient_names) if x_opt[i] * 100.0 > 0.05}
    tot = sum(formula.values())
    if tot > 0:
        formula = {k: round(v / tot * 100.0, 2) for k, v in formula.items()}
    final_cost = float(np.dot(cost_vals, x_opt))
    quality_index = (actual_me / max(target_me, 1.0)) * (actual_cp / max(target_cp, 0.1))
    max_profit = float(price_product * quality_index - final_cost)
    warning = f"⚠️ تم تخفيف القيود إلى {mult * 100:.0f}% لتوفير حل واقعي" if mult < 1.0 else None
    return {
        "success": True,
        "formula": formula,
        "x_opt": x_opt.tolist(),
        "final_cost": round(final_cost, 4),
        "final_me": round(actual_me, 1),
        "final_cp": round(actual_cp, 2),
        "target_me": round(target_me, 1),
        "target_cp": round(target_cp, 2),
        "max_profit": round(max_profit, 4),
        "strategy": level_name,
        "warning": warning,
    }


def analyze_existing_formula(formula: Dict, animal_type: str, production_type: str) -> Dict:
    if not formula or sum(formula.values()) <= 0:
        return {"success": False, "message": "التركيبة فارغة"}
    total = sum(formula.values())
    normalized = {k: round(v / total * 100.0, 2) for k, v in formula.items()}
    if animal_type == "أبقار":
        req = get_cattle_requirements(production_type)
    elif animal_type == "أغنام":
        req = get_sheep_requirements(production_type, is_male=("تسمين" in production_type or "تيد" in production_type))
    elif animal_type == "ماعز":
        req = get_goat_requirements(production_type, is_male=("تسمين" in production_type or "تيوس" in production_type))
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

    standard = requirement_to_standard(req)
    actual = compute_formula_nutrients(normalized)
    comparison = build_comparison_rows(standard, actual)
    quality, _ = evaluate_quality_weighted(normalized, standard, animal_type)
    ca, p = actual.get("Ca", 0.0), actual.get("P", 0.0)
    ca_p = round(ca / p, 2) if p > 0 else 0.0
    lookup = _get_ingredient_lookup()
    cost = sum(normalized.get(ing, 0.0) / 100.0 * lookup.get(ing, {}).get("price", 300.0) * 10.0 for ing in normalized)
    return {
        "success": True,
        "formula": normalized,
        "standard": standard,
        "actual": actual,
        "comparison": comparison,
        "quality_score": quality,
        "ca_p_ratio": ca_p,
        "cost_per_ton": round(cost, 2),
        "animal_type": animal_type,
        "production_type": production_type,
    }


# ═══════════════════════════════════════════════════════════════════════
# بدائل الحليب وشريط القياس
# ═══════════════════════════════════════════════════════════════════════

MILK_REPLACER_STANDARDS = {
    "عجول (Calves)": {"CP": 24, "Fat": 20, "Lactose": 45, "Ca": 0.85, "P": 0.7, "Lys": 2.2, "Met": 0.65, "source": "NRC Dairy Cattle"},
    "حملان (Lambs)": {"CP": 24, "Fat": 24, "Lactose": 40, "Ca": 0.9, "P": 0.7, "Lys": 2.4, "Met": 0.7, "source": "NRC Small Ruminants"},
    "جديان (Goat Kids)": {"CP": 24, "Fat": 24, "Lactose": 42, "Ca": 0.9, "P": 0.7, "Lys": 2.3, "Met": 0.7, "source": "NRC Small Ruminants"},
    "إبل (Camels)": {"CP": 26, "Fat": 28, "Lactose": 38, "Ca": 0.95, "P": 0.75, "Lys": 2.5, "Met": 0.8, "source": "FAO Camel"},
    "أمهار (Foals)": {"CP": 22, "Fat": 18, "Lactose": 48, "Ca": 1.0, "P": 0.8, "Lys": 2.1, "Met": 0.6, "source": "NRC Horses"},
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
    if not SCIPY_AVAILABLE or linprog is None:
        return {"success": False, "message": "مكتبة SciPy غير متوفرة"}
    std = MILK_REPLACER_STANDARDS.get(animal)
    valid = [i for i in (selected or list(MILK_REPLACER_INGREDIENTS.keys())) if i in MILK_REPLACER_INGREDIENTS]
    n = len(valid)
    if not std or n < 3:
        return {"success": False, "message": "اختر 3 مكونات على الأقل"}
    c = [MILK_REPLACER_INGREDIENTS[i]["price"] for i in valid]
    cp = [MILK_REPLACER_INGREDIENTS[i]["CP"] for i in valid]
    fat = [MILK_REPLACER_INGREDIENTS[i]["Fat"] for i in valid]
    bounds = [(0, MILK_REPLACER_INGREDIENTS[i].get("max", 100)) for i in valid]
    res = linprog(c, A_eq=[[1] * n, cp, fat], b_eq=[100, std["CP"] * 100, std["Fat"] * 100], bounds=bounds, method="highs")
    if not res.success:
        res = linprog(c, A_eq=[[1] * n], b_eq=[100], bounds=bounds, method="highs")
    if not res.success:
        return {"success": False, "message": "لا يوجد حل للمكونات المحددة"}
    formula = {valid[i]: float(res.x[i]) for i in range(n) if res.x[i] > 0.01}
    actual = {k: round(sum(pct / 100 * MILK_REPLACER_INGREDIENTS[ing].get(k, 0) for ing, pct in formula.items()), 2) for k in ["CP", "Fat", "Lactose", "Ca", "P", "Lys", "Met"]}
    scores = [max(0.0, 100.0 - abs(actual[k] - std[k]) / std[k] * 100.0) for k in ["CP", "Fat", "Lactose"] if std.get(k, 0) > 0]
    q = round(sum(scores) / len(scores) if scores else 80.0, 1)
    return {"success": True, "formula": formula, "cost_per_100kg": res.fun / 100, "cost_per_kg": res.fun / 10000, "standard": std, "actual": actual, "animal": animal, "volume": volume, "quality_score": q}


WEIGHT_TAPE_CONFIG = {
    "أبقار": {"hg_min": 100.0, "hg_max": 260.0, "hg_default": 180.0, "bl_min": 100.0, "bl_max": 220.0, "bl_default": 150.0, "hg_label": "محيط الصدر (سم)", "bl_label": "طول الجسم (سم)", "source": "Schaeffer (1978)", "accuracy": "±5%", "calc": lambda hg, bl: (hg**2 * bl) / 10840.0},
    "أغنام": {"hg_min": 40.0, "hg_max": 120.0, "hg_default": 75.0, "bl_min": 40.0, "bl_max": 100.0, "bl_default": 65.0, "hg_label": "محيط الصدر (سم)", "bl_label": "طول الجسم (سم)", "source": "Schaeffer (1978)", "accuracy": "±7%", "calc": lambda hg, bl: (hg**2 * bl) / 10840.0},
    "ماعز": {"hg_min": 35.0, "hg_max": 110.0, "hg_default": 70.0, "bl_min": 35.0, "bl_max": 95.0, "bl_default": 62.0, "hg_label": "محيط الصدر (سم)", "bl_label": "طول الجسم (سم)", "source": "Schaeffer (1978)", "accuracy": "±7%", "calc": lambda hg, bl: (hg**2 * bl) / 10840.0},
    "إبل": {"hg_min": 130.0, "hg_max": 280.0, "hg_default": 210.0, "bl_min": 100.0, "bl_max": 220.0, "bl_default": 155.0, "hg_label": "محيط الصدر (سم)", "bl_label": "طول الجسم (سم)", "source": "FAO Camel (2010)", "accuracy": "±10%", "calc": lambda hg, bl: (hg**2 * bl) / 11880.0},
    "خيول": {"hg_min": 120.0, "hg_max": 240.0, "hg_default": 175.0, "bl_min": 100.0, "bl_max": 210.0, "bl_default": 155.0, "hg_label": "محيط الصدر (سم)", "bl_label": "طول الجسم (سم)", "source": "Carroll & Huntington (1988)", "accuracy": "±5%", "calc": lambda hg, bl: (hg**2 * bl) / 11877.0},
}


def weight_tape_widget(animal_type: str, key_prefix: str, default_weight: Optional[float] = None) -> float:
    cfg = WEIGHT_TAPE_CONFIG.get(animal_type)
    if cfg is None:
        return float(st.number_input("⚖️ الوزن (كجم):", 0.05, 50.0, float(default_weight) if default_weight else 2.0, 0.1, key=f"{key_prefix}_manual"))
    c1, c2 = st.columns(2)
    with c1:
        hg = st.slider(f"① {cfg['hg_label']}", cfg["hg_min"], cfg["hg_max"], cfg["hg_default"], 0.5, key=f"{key_prefix}_hg")
    with c2:
        bl = st.slider(f"② {cfg['bl_label']}", cfg["bl_min"], cfg["bl_max"], cfg["bl_default"], 0.5, key=f"{key_prefix}_bl")
    weight = float(cfg["calc"](hg, bl))
    st.info(f"📏 معادلة {cfg['source']} (دقة {cfg['accuracy']}) → الوزن التقديري = **{weight:.1f} كجم**")
    return weight


# ═══════════════════════════════════════════════════════════════════════
# الدردشة والاستديو وOCR
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
    rooms[room].append({"user": user, "msg": msg, "ts": datetime.now().strftime("%H:%M:%S"), "date": datetime.now().strftime("%Y-%m-%d"), "role": st.session_state.get("user_role", "guest")})
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


def extract_ingredients_from_image(image_bytes: bytes) -> Dict:
    if not OCR_AVAILABLE:
        return {"success": False, "message": "مكتبتا pytesseract و opencv غير مثبتتين في البيئة"}
    try:
        img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return {"success": False, "message": "تعذر قراءة الصورة"}
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        txt = pytesseract.image_to_string(gray, lang="ara+eng", config=r"--oem 3 --psm 6")
        ingredients = _parse_ingredients_from_text(txt)
        return {"success": True, "ingredients": ingredients, "raw_text": txt}
    except Exception as e:
        return {"success": False, "message": f"خطأ أثناء المسح: {e}"}


def render_ocr_correction_ui(ingredients: Dict) -> Dict:
    st.markdown("### ✏️ تصحيح يدوي للمكونات المستخرجة")
    corrected = {}
    all_names = sorted(_get_ingredient_lookup().keys())
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


# ═══════════════════════════════════════════════════════════════════════
# الرسوم البيانية (Bar + Pie + Radar + Profit Curve)
# ═══════════════════════════════════════════════════════════════════════


def create_colorful_bar_chart(standard: Dict, actual: Dict, keys=None) -> Optional[io.BytesIO]:
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        keys = keys or ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH"]
        nuts = [n for n in keys if n in standard and standard[n] > 0]
        if not nuts:
            return None
        fig, ax = plt.subplots(figsize=(9, 4.2))
        x = np.arange(len(nuts))
        width = 0.36
        ax.bar(x - width / 2, [standard[n] for n in nuts], width, label="القياسي (المعيار)", color="#1565c0")
        ax.bar(x + width / 2, [actual.get(n, 0.0) for n in nuts], width, label="المحسوب", color="#2e7d32")
        ax.set_xticks(x)
        ax.set_xticklabels(nuts, fontweight="bold")
        ax.set_title("مقارنة العناصر الغذائية: القياسي مقابل المحسوب", fontweight="bold", color="#1b5e20")
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.legend()
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
        fig, ax = plt.subplots(figsize=(7.5, 4.8))
        ax.pie(list(formula.values()), labels=list(formula.keys()), autopct="%1.1f%%", startangle=90)
        ax.set_title("توزيع نسب مكونات الخلطة العلفية", fontweight="bold", color="#1b5e20")
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
        keys = keys or ["CP", "DP", "SE", "NDF", "ADF", "EE", "Ca", "P"]
        nuts = [n for n in keys if n in standard and standard[n] > 0]
        if len(nuts) < 3:
            return None
        std_norm = [100.0] * len(nuts) + [100.0]
        act_norm = [(actual.get(n, 0.0) / standard[n]) * 100.0 for n in nuts]
        act_norm += act_norm[:1]
        angles = np.linspace(0, 2 * np.pi, len(nuts), endpoint=False).tolist() + [0.0]
        fig, ax = plt.subplots(figsize=(5.5, 5.5), subplot_kw=dict(polar=True))
        ax.plot(angles, std_norm, "o-", linewidth=2, color="#1565c0", label="القياسي (100%)")
        ax.plot(angles, act_norm, "o-", linewidth=2, color="#2e7d32", label="المحسوب %")
        ax.fill(angles, act_norm, alpha=0.15, color="#2e7d32")
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(nuts)
        ax.set_title("مخطط الرادار لتوازن العناصر", fontweight="bold", color="#1b5e20", pad=16)
        ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1))
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="white")
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_nlp_profit_curve(result: Dict, ingredient_names, ingredient_data, prices):
    if not PLOTLY_AVAILABLE:
        return None
    try:
        me_vals = np.array([ingredient_data[i].get("SE", 0.0) * 41.0 for i in ingredient_names])
        cp_vals = np.array([ingredient_data[i].get("CP", 0.0) for i in ingredient_names])
        cost_vals = np.array([prices.get(i, 300.0) / 100.0 for i in ingredient_names])
        x_opt = np.array(result["x_opt"])
        q_idx = (float(np.dot(me_vals, x_opt)) / max(result["target_me"], 1.0)) * (float(np.dot(cp_vals, x_opt)) / max(result["target_cp"], 0.1))
        c_kg = float(np.dot(cost_vals, x_opt))
        prices_range = np.linspace(0.5, 6.0, 45)
        profits = [p * q_idx - c_kg for p in prices_range]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=prices_range, y=profits, mode="lines+markers", line=dict(color="#1b5e20", width=3), name="صافي العائد / كجم"))
        fig.add_hline(y=0, line_dash="dash", line_color="#c62828", annotation_text="نقطة التعادل")
        fig.update_layout(title="منحنى الربحية حسب سعر وحدة المنتج ($)", xaxis_title="سعر وحدة المنتج ($)", yaxis_title="صافي العائد ($/كجم)", height=380, paper_bgcolor="white")
        return fig
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════
# مولد تقارير PDF ونظام الموافقة
# ═══════════════════════════════════════════════════════════════════════


class PDFGenerator:
    def __init__(self):
        self.font_name = font_mgr.font_name

    def _ar(self, t):
        return ar("" if t is None else str(t))

    def _draw_page(self, canvas_obj, doc):
        try:
            canvas_obj.saveState()
            w, h = doc.pagesize
            canvas_obj.setFillColor(HexColor("#1b5e20"))
            canvas_obj.rect(0, h - 85, w, 85, fill=1, stroke=0)
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 20)
            canvas_obj.drawCentredString(w / 2, h - 35, self._ar(APP_NAME))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.drawCentredString(w / 2, h - 58, self._ar(f"إشراف: {SUPERVISOR}"))
            canvas_obj.setFillColor(HexColor("#1b5e20"))
            canvas_obj.rect(0, 0, w, 45, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor("#ffeb3b"))
            canvas_obj.setFont(self.font_name, 9)
            canvas_obj.drawCentredString(w / 2, 24, self._ar(f"🤲 {DUA_SHORT} 🤲"))
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 7)
            canvas_obj.drawCentredString(w / 2, 10, self._ar(f"صفحة {canvas_obj.getPageNumber()}"))
            canvas_obj.restoreState()
        except Exception:
            pass

    def generate_report(self, formula: Dict, requirement: AnimalRequirement, animal_type: str, breed: str, cost: float, city: str, local_cost: float, local_sym: str, requester_name: str = "", protein_basis: str = "DP", standard_key: str = "", include_charts: bool = True, quality_score: float = 0.0) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=105, bottomMargin=65)
        story = []

        def P(text, size=11, align=TA_RIGHT, color="#1a1a1a"):
            return Paragraph(self._ar(text), ParagraphStyle("s", fontName=self.font_name, fontSize=size, alignment=align, textColor=HexColor(color), spaceAfter=6, leading=size * 1.5))

        story.append(P("تقرير فني رسمي — تركيبة علفية", size=18, align=TA_CENTER, color="#1b5e20"))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor("#d4af37")))
        story.append(Spacer(1, 10))
        info = [
            [self._ar("المستخدم:"), self._ar(requester_name or "—")],
            [self._ar("الفصيل / الحالة:"), self._ar(f"{animal_type} — {breed} ({protein_basis})")],
            [self._ar("التكلفة / طن:"), f"${cost:.2f}"],
            [self._ar("الجودة:"), f"{quality_score:.1f}%"],
        ]
        t = Table(info, colWidths=[160, 330])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), HexColor("#e8f5e9")), ("BOX", (0, 0), (-1, -1), 1, HexColor("#2e7d32")), ("ALIGN", (0, 0), (-1, -1), "RIGHT"), ("FONTNAME", (0, 0), (-1, -1), self.font_name), ("PADDING", (0, 0), (-1, -1), 7)]))
        story.append(t)
        story.append(Spacer(1, 14))
        ing_data = [[self._ar("المكون"), self._ar("%"), self._ar("كجم/طن")]]
        for ing, pct in formula.items():
            ing_data.append([self._ar(ing), f"{pct:.2f}%", f"{pct * 10:.1f}"])
        it = Table(ing_data, colWidths=[270, 110, 110])
        it.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HexColor("#2e7d32")), ("TEXTCOLOR", (0, 0), (-1, 0), white), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTNAME", (0, 0), (-1, -1), self.font_name), ("GRID", (0, 0), (-1, -1), 0.8, HexColor("#bdbdbd"))]))
        story.append(it)
        if include_charts:
            actual = compute_formula_nutrients(formula)
            bar_buf = create_colorful_bar_chart(requirement_to_standard(requirement), actual)
            if bar_buf:
                story.append(Spacer(1, 12))
                story.append(RLImage(bar_buf, width=460, height=220))
        doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_ocr_report(self, ingredients: Dict, nutrients: Dict, raw_text: str = "") -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=105, bottomMargin=65)
        story = [Paragraph(self._ar("تقرير تحليل OCR"), ParagraphStyle("t", fontName=self.font_name, fontSize=18, alignment=TA_CENTER, textColor=HexColor("#1b5e20")))]
        data = [[self._ar("المادة"), self._ar("%")]] + [[self._ar(k), f"{v:.2f}%"] for k, v in ingredients.items()]
        t = Table(data, colWidths=[300, 190])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HexColor("#1b5e20")), ("TEXTCOLOR", (0, 0), (-1, 0), white), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTNAME", (0, 0), (-1, -1), self.font_name), ("GRID", (0, 0), (-1, -1), 0.8, HexColor("#bdbdbd"))]))
        story.append(t)
        doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()


pdf_gen = PDFGenerator()


def generate_nlp_math_pdf(result: Dict, animal_type: str, production_type: str) -> Optional[bytes]:
    if not REPORTLAB_AVAILABLE:
        return None
    return pdf_gen.generate_report(result["formula"], AnimalRequirement(result["target_cp"] * 0.75, result["target_cp"], result["target_me"] / 41.0, 20, 10, 4, 7, 0.6, 0.35), animal_type, production_type, result["final_cost"] * 1000, "عام", result["final_cost"] * 1000, "$", quality_score=90.0)


def generate_milk_replacer_pdf(result: Dict) -> Optional[bytes]:
    if not REPORTLAB_AVAILABLE:
        return None
    return pdf_gen.generate_report(result["formula"], AnimalRequirement(20, result["standard"]["CP"], 65, 5, 2, result["standard"]["Fat"], 8, result["standard"]["Ca"], result["standard"]["P"]), result["animal"], "بديل حليب", result["cost_per_100kg"] * 10, "عام", result["cost_per_100kg"] * 10, "$", quality_score=result["quality_score"])


def generate_lab_pdf(result: Dict, ctx: Dict) -> Optional[bytes]:
    if not REPORTLAB_AVAILABLE:
        return None
    return pdf_gen.generate_report(result["formula"], AnimalRequirement(12, 15, 65, 25, 15, 4, 8, 0.6, 0.35), ctx.get("animal", ""), ctx.get("production", ""), result["cost_per_ton"], "عام", result["cost_per_ton"], "$", quality_score=result["quality_score"])


def generate_barn_pdf(dims: Dict) -> Optional[bytes]:
    if not REPORTLAB_AVAILABLE:
        return None
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=105, bottomMargin=65)
    story = [Paragraph(ar(f"مخطط منشأة: {dims['standard'].get('name_ar', '')}"), ParagraphStyle("t", fontName=font_mgr.font_name, fontSize=18, alignment=TA_CENTER, textColor=HexColor("#1b5e20"))), Spacer(1, 12)]
    rows = [[ar("المواصفة"), ar("القيمة")], [ar("المساحة الكلية"), f"{dims['total_area_m2']} م²"], [ar("التهوية الصيفية"), f"{dims['vent_summer_m3h']:,} م³/س"], [ar("التكلفة التقديرية"), f"${dims['cost_total_usd']:,.0f}"]]
    t = Table(rows, colWidths=[220, 270])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HexColor("#1b5e20")), ("TEXTCOLOR", (0, 0), (-1, 0), white), ("ALIGN", (0, 0), (-1, -1), "RIGHT"), ("FONTNAME", (0, 0), (-1, -1), font_mgr.font_name), ("GRID", (0, 0), (-1, -1), 0.8, HexColor("#bdbdbd"))]))
    story.append(t)
    doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
    buffer.seek(0)
    return buffer.getvalue()


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
        data["requests"].append({"id": request_id, "user_name": _sanitize_message(user_name, 50) or "غير محدد", "user_role": user_role, "doc_title": _sanitize_message(doc_title, 100), "doc_context": doc_context or {}, "pdf_path": pdf_path, "status": "pending", "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "reviewed_at": None, "rejection_reason": None})
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
    st.markdown(f"""<div style="background: linear-gradient(135deg, #fff3e0, #ffe0b2); padding: 16px; border-radius: 14px; border: 2px solid #e65100; margin: 12px 0; direction: rtl; text-align: right;"><h4 style="color:#e65100; margin:0 0 8px 0;">🌾 للحصول على تركيبات علفية أكثر دقة وجودة</h4><p style="color:#1a1a1a; margin:0; font-size:1rem;">تواصل مع <b style="color:#c62828;">{SUPERVISOR}</b> — <span style="color:#1565c0;">{SUPERVISOR_TITLE}</span></p></div>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    wa_consult = f"https://wa.me/{WHATSAPP_NUMBER.replace('+', '').replace(' ', '')}?text="
    consult_msg = urllib.parse.quote(f"السلام عليكم دكتور عبدالقادر، أرغب في استشارة حول تركيبة علفية ({APP_NAME}).")
    with col1:
        st.markdown(f"""<a href="{wa_consult}{consult_msg}" target="_blank" style="display:block; padding:11px; background:#25d366; color:white; text-decoration:none; border-radius:10px; text-align:center; font-weight:700;">📱 استشارة واتساب</a>""", unsafe_allow_html=True)
    with col2:
        em_consult = f"mailto:{OWNER_EMAIL}?subject=" + urllib.parse.quote("طلب استشارة - تاور نولجي")
        st.markdown(f"""<a href="{em_consult}" style="display:block; padding:11px; background:#1565c0; color:white; text-decoration:none; border-radius:10px; text-align:center; font-weight:700;">✉️ استشارة بريد</a>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<a href="tel:{WHATSAPP_NUMBER}" style="display:block; padding:11px; background:#c62828; color:white; text-decoration:none; border-radius:10px; text-align:center; font-weight:700;">📞 اتصال مباشر</a>""", unsafe_allow_html=True)


def render_pdf_download_with_approval(pdf_bytes: Optional[bytes], file_name: str, doc_title: str, user_role: str, user_name: str = "", doc_context: Optional[Dict] = None, key_suffix: str = "") -> None:
    if not pdf_bytes:
        st.warning("⚠️ تعذر إنشاء ملف PDF")
        return
    if user_role == "owner":
        st.download_button("📄 تحميل PDF (مالك)", pdf_bytes, file_name=file_name, mime="application/pdf", use_container_width=True, type="primary", key=f"pdf_direct_{key_suffix}")
        return
    if not user_name:
        user_name = st.session_state.get("chat_username", "مستخدم")
    existing = get_user_pending_request(user_name, doc_title)
    if existing:
        if existing["status"] == "approved":
            pdf_data = _read_pdf_bytes(existing["id"])
            if pdf_data:
                st.success("✅ تمت الموافقة بواسطة المالك — يمكنك التحميل الآن")
                st.download_button("📄 تحميل PDF (موافق عليه)", pdf_data, file_name=file_name, mime="application/pdf", use_container_width=True, type="primary", key=f"pdf_approved_{key_suffix}")
        elif existing["status"] == "pending":
            st.warning(f"⏳ طلبك قيد المراجعة من المالك | رقم الطلب: `{existing['id']}`")
        elif existing["status"] == "rejected":
            st.error(f"❌ تم رفض طلبك | السبب: {existing.get('rejection_reason') or 'غير محدد'}")
            if st.button("🔄 إعادة طلب الموافقة", use_container_width=True, key=f"pdf_req_retry_{key_suffix}"):
                create_pdf_request(user_name, user_role, pdf_bytes, doc_title, doc_context)
                st.rerun()
    else:
        st.info("🔒 تحميل PDF يتطلب موافقة المالك")
        if st.button("📤 طلب موافقة على تحميل PDF", type="primary", use_container_width=True, key=f"pdf_req_new_{key_suffix}"):
            rid = create_pdf_request(user_name, user_role, pdf_bytes, doc_title, doc_context)
            if rid.startswith("REQ_"):
                st.success(f"✅ تم إرسال الطلب: {rid}")
                st.rerun()
    st.markdown("---")
    render_consultation_buttons()


def render_pdf_requests_admin() -> None:
    st.markdown('<div class="section-title">📋 إدارة طلبات PDF</div>', unsafe_allow_html=True)
    requests = _load_pdf_requests().get("requests", [])
    pending = [r for r in requests if r["status"] == "pending"]
    approved = [r for r in requests if r["status"] == "approved"]
    rejected = [r for r in requests if r["status"] == "rejected"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 الإجمالي", len(requests))
    c2.metric("⏳ قيد المراجعة", len(pending))
    c3.metric("✅ موافق عليها", len(approved))
    c4.metric("❌ مرفوضة", len(rejected))
    if not pending:
        st.info("💡 لا توجد طلبات معلقة حالياً")
    for req in reversed(pending):
        with st.expander(f"📄 {req['doc_title']} — {req['user_name']} ({req['created_at']})"):
            ac1, ac2 = st.columns(2)
            with ac1:
                if st.button("✅ موافقة", type="primary", use_container_width=True, key=f"approve_{req['id']}"):
                    approve_pdf_request(req["id"])
                    st.rerun()
            with ac2:
                if st.button("❌ رفض", use_container_width=True, key=f"reject_{req['id']}"):
                    reject_pdf_request(req["id"], "غير مستوفٍ")
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════
# الحظائر 3D وشرح المواصفات الهندسية
# ═══════════════════════════════════════════════════════════════════════

HORSE_STALL_SCIENCE = {
    "box_standard": {"width": 3.5, "length": 3.5, "area": 12.25, "name_ar": "مربط صندوقي قياسي"},
    "box_large": {"width": 4.0, "length": 4.0, "area": 16.0, "name_ar": "مربط كبير"},
    "box_foaling": {"width": 4.0, "length": 5.0, "area": 20.0, "name_ar": "مربط ولادة"},
    "box_pony": {"width": 3.0, "length": 3.0, "area": 9.0, "name_ar": "مربط بوني"},
}


def calculate_horse_barn_scientific(num_horses: int, stall_type: str = "box_standard", include_service: bool = True) -> Dict:
    stall = HORSE_STALL_SCIENCE.get(stall_type, HORSE_STALL_SCIENCE["box_standard"])
    rows = 1 if num_horses <= 4 else 2
    stalls_per_row = num_horses if rows == 1 else (num_horses + 1) // 2
    building_length = stalls_per_row * stall["width"] + 2.0
    building_width = rows * stall["length"] + 3.5 + 1.0
    service_area = 73 if include_service else 0
    total_area = building_width * building_length + service_area
    vol = building_width * building_length * 4.0
    vent_summer = int(vol * 25)
    vent_winter = int(vol * 5)
    cost_total = round(building_width * building_length * 125 + num_horses * stall["area"] * 180 + service_area * 40, 0)
    return {
        "is_horse_barn": True,
        "num_horses": num_horses,
        "stall_dimensions": f"{stall['width']}×{stall['length']} م ({stall['area']} م²)",
        "rows_count": rows,
        "stalls_per_row": stalls_per_row,
        "total_area_m2": round(total_area, 2),
        "length_m": round(building_length, 2),
        "width_m": round(building_width, 2),
        "height_m": 4.0,
        "ridge_height_m": 5.5,
        "roof_type": "gable",
        "vent_summer_m3h": vent_summer,
        "vent_winter_m3h": vent_winter,
        "water_l_day": num_horses * 45,
        "cost_total_usd": cost_total,
        "standard": {"name_ar": f"خيول — {stall['name_ar']}"},
        "barn_key": "خيول_مربط",
        "explanation": "يعتمد تصميم الإسطبل على توفير مربط مريح لكل حصان مع ممر خدمة مركزي بعرض 3.5 م لتسهيل الحركة والسلامة، وتهوية طبيعية وميكانيكية تمنع تراكم الأمونيا والرطوبة مع حماية الخيول من التيارات الهوائية المباشرة.",
    }


BARN_DESIGN_STANDARDS = {
    "أبقار": {"name_ar": "حظيرة أبقار", "area_per_head": 5.0, "height_m": 4.5, "width_m": 15.0, "ach_summer": 25, "ach_winter": 6, "water_l": 75, "roof_type": "gable", "slope_pct": 20.0, "desc": "تحتاج الأبقار إلى أسقف مرتفعة ومفتوحة الجوانب جزئياً لتبديد الحرارة الأيضية العالية، مع أرضيات مانعة للانزلاق ومناطق راحة جافة ونظيفة."},
    "أغنام": {"name_ar": "حظيرة أغنام", "area_per_head": 1.5, "height_m": 3.5, "width_m": 10.0, "ach_summer": 30, "ach_winter": 6, "water_l": 10, "roof_type": "gable", "slope_pct": 25.0, "desc": "تُصمم حظائر الأغنام لحماية القطيع من الرطوبة الأرضية والشمس المباشرة وتيارات الهواء الباردة، مع تقسيم مناسب لعزل الحملان والنعاج العشار."},
    "إبل": {"name_ar": "حظيرة إبل", "area_per_head": 10.0, "height_m": 4.5, "width_m": 15.0, "ach_summer": 20, "ach_winter": 5, "water_l": 40, "roof_type": "gable", "slope_pct": 20.0, "desc": "تراعي حظائر الإبل الارتفاع المناسب والاتساع الحركي وتوفير مظلات جيدة ومشارب واسعة مع تصريف جيد للرطوبة."},
    "دواجن_لاحم": {"name_ar": "عنبر دواجن لاحم", "area_per_head": 0.10, "height_m": 2.8, "width_m": 12.0, "ach_summer": 60, "ach_winter": 8, "water_l": 0.35, "roof_type": "gable", "slope_pct": 20.0, "desc": "تعتمد عناصر لاحم على التحكم الدقيق في درجة الحرارة والتهوية النفقية وسرعة الهواء لتقليل الإجهاد الحراري وضمان كفاءة التحويل الغذائي."},
    "سمان": {"name_ar": "عنبر سمان", "area_per_head": 0.025, "height_m": 2.0, "width_m": 6.0, "ach_summer": 50, "ach_winter": 8, "water_l": 0.08, "roof_type": "mono", "slope_pct": 15.0, "desc": "يتطلب السمان بيئة هادئة خالية من الضوضاء والتیارات المباشرة مع تهوية منتظمة تمنع ارتفاع الأمونيا."},
    "أرانب": {"name_ar": "عنبر أرانب", "area_per_head": 0.30, "height_m": 2.5, "width_m": 8.0, "ach_summer": 40, "ach_winter": 6, "water_l": 0.5, "roof_type": "gable", "slope_pct": 20.0, "desc": "تُعد الأرانب حساسة جداً لارتفاع الحرارة والرطوبة؛ لذا يركز التصميم على التهوية الجيدة وعزل السقف الحراري."},
}


def calculate_barn_dimensions(key: str, count: int) -> Optional[Dict]:
    std = BARN_DESIGN_STANDARDS.get(key)
    if not std:
        return None
    area = count * std["area_per_head"]
    width = std["width_m"]
    length = max(area / width, 6.0)
    height = std["height_m"]
    vol = length * width * height
    ridge = height + (width / 2) * (std["slope_pct"] / 100)
    vent_summer = int(vol * std["ach_summer"])
    vent_winter = int(vol * std["ach_winter"])
    return {
        "standard": std,
        "count": count,
        "total_area_m2": round(area, 2),
        "length_m": round(length, 2),
        "width_m": round(width, 2),
        "height_m": round(height, 2),
        "ridge_height_m": round(ridge, 2),
        "roof_type": std["roof_type"],
        "vent_summer_m3h": vent_summer,
        "vent_winter_m3h": vent_winter,
        "water_l_day": round(count * std["water_l"], 1),
        "cost_total_usd": round(length * width * 145, 0),
        "barn_key": key,
        "explanation": std.get("desc", ""),
    }


def create_barn_3d_figure(dims: Dict):
    if not PLOTLY_AVAILABLE:
        return None
    try:
        L = max(float(dims["length_m"]), 1.0)
        W = max(float(dims["width_m"]), 1.0)
        H = max(float(dims["height_m"]), 1.0)
        RH = max(float(dims["ridge_height_m"]), 1.0)
        fig = go.Figure()
        fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[0, 0, 0, 0], i=[0, 0], j=[1, 2], k=[2, 3], color="#d7ccc8", opacity=0.75, name="الأرضية"))
        if dims.get("roof_type") == "gable":
            fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W / 2, W / 2], z=[H, H, RH, RH], i=[0, 0], j=[1, 2], k=[2, 3], color="#8d6e63", opacity=0.6, name="السقف"))
            fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[W / 2, W / 2, W, W], z=[RH, RH, H, H], i=[0, 0], j=[1, 2], k=[2, 3], color="#8d6e63", opacity=0.6, showlegend=False))
        else:
            fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[RH, RH, H, H], i=[0, 0], j=[1, 2], k=[2, 3], color="#8d6e63", opacity=0.6, name="السقف"))
        fig.update_layout(title=f"{dims['standard'].get('name_ar', '')} — {L:.1f}م × {W:.1f}م", scene=dict(xaxis=dict(title="الطول (م)"), yaxis=dict(title="العرض (م)"), zaxis=dict(title="الارتفاع (م)")), height=440, margin=dict(l=0, r=0, t=40, b=0))
        return fig
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════
# تنسيق CSS والهيدر
# ═══════════════════════════════════════════════════════════════════════

st.markdown("""<style>.stApp{background-color:#f4f7f4;color:#1a1a1a}.main-header{background:linear-gradient(135deg,#1b5e20,#2e7d32);padding:24px 30px;border-radius:18px;color:#fff;margin-bottom:16px;border:2px solid #d4af37}.main-header h1{margin:0;font-size:2.3rem;font-weight:900;color:#fff;text-align:center}.main-header .tagline{margin:6px 0 0;font-size:1.1rem;color:#e8f5e9;text-align:center}.dua-banner{background:linear-gradient(135deg,#1b5e20,#0d3b12);padding:14px 20px;border-radius:14px;margin-bottom:16px;text-align:center;color:#fff;border:2px solid #d4af37}.dua-title{font-size:1.25rem;font-weight:800;color:#ffeb3b;margin:4px 0}.dua-sub{font-size:0.95rem;color:#c8e6c9}.section-title{font-size:1.4rem;font-weight:800;color:#1b5e20;margin:18px 0 10px;padding-bottom:6px;border-bottom:3px solid #d4af37}.info-card{background:#fff;padding:16px 20px;border-radius:14px;border-right:5px solid #2e7d32;box-shadow:0 3px 10px rgba(0,0,0,0.06);margin-bottom:12px;color:#1a1a1a}.footer{background:#1b5e20;color:#e8f5e9;padding:16px;border-radius:14px;text-align:center;margin-top:24px;border-top:4px solid #d4af37}</style>""", unsafe_allow_html=True)


def render_main_header() -> None:
    st.markdown(f"""<div class="main-header"><h1>🌾 {APP_NAME}</h1><div class="tagline">{APP_TAGLINE}</div></div><div class="dua-banner"><div class="dua-sub">{DUA_VERSE}</div><div class="dua-title">🤲 {DUA_FULL} 🤲</div><div class="dua-sub">{DUA_QURAN}</div></div>""", unsafe_allow_html=True)


for k, v in [("approved", False), ("user_role", None), ("show_owner_login", False), ("auto_formula", None), ("nlp_result", None), ("milk_replacer_result", None), ("barn_dims", None), ("lab_result", None), ("ocr_result", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

generate_csrf_token()
_safe_username()


def _session_valid() -> bool:
    role = st.session_state.get("user_role")
    if not st.session_state.get("approved", False) or role not in ("owner", "specialist", "guest"):
        return False
    if role == "owner" and not _get_owner_code_hash():
        return False
    return True


if not _session_valid():
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

base_tabs = ["🧮 التركيب (LP)", "🎯 أمثل ربحية (NLP)", "🔬 مختبر التحليل", "📸 مسح OCR", "🍼 بديل الحليب", "🏗️ الحظائر 3D", "🎬 استديو", "💬 الدردشة", "📚 المراجع"]
if role == "owner":
    base_tabs.append("📋 طلبات PDF")

tabs = st.tabs(base_tabs)
tab_idx = 0

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

    ref_lp = get_references(animal_lp, prod_lp)
    eq_lp = get_reference_equations(animal_lp, prod_lp)
    st.markdown(f'<div class="info-card"><b>📖 المرجع العلمي:</b> {ref_lp.get("primary", "")} — <i>{ref_lp.get("table", "")}</i><br><b>📐 المعادلات:</b> {" | ".join(f"{k}: {v}" for k, v in eq_lp.items() if k != "source")}</div>', unsafe_allow_html=True)

    all_ings = list(_get_ingredient_lookup().keys())
    defaults = [i for i in get_default_selections(animal_lp, prod_lp, req_lp) if i in all_ings]
    for s in ["ذرة صفراء", "شعير مطحون", "كسب فول صويا 44%", "أمباز الفول السوداني", "نخالة قمح (ردة)"]:
        if s in all_ings and s not in defaults:
            defaults.append(s)
    selected_lp = st.multiselect("🌾 المواد العلفية المتاحة:", all_ings, default=defaults[:10], key="lp_selected_ings")
    custom_prices = {ing: float(_get_ingredient_lookup()[ing].get("price", 300.0)) for ing in selected_lp}
    if st.button("🚀 حساب التركيبة المثلى", type="primary", use_container_width=True, key="btn_run_lp"):
        res_lp = auto_formulate_smart(selected_lp, custom_prices, requirement_to_standard(req_lp), standard_key=f"{animal_lp}_{prod_lp}", basis=basis_lp, animal_type=animal_lp, production_type=prod_lp)
        st.session_state["auto_formula"] = {"res": res_lp, "req": req_lp, "animal": animal_lp, "prod": prod_lp, "basis": basis_lp}

    lp_pack = st.session_state.get("auto_formula")
    if lp_pack:
        r = lp_pack.get("res", {})
        if r.get("success"):
            if r.get("warning"):
                st.warning(r["warning"])
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("💰 التكلفة / طن", f"${r['cost']:.2f}")
            m2.metric("⭐ الجودة", f"{r['quality_score']:.1f}%")
            m3.metric("⚙️ الاستراتيجية", r["strategy"])
            m4.metric("🌰 نسبة الزيوت", f"{r['total_oil']:.2f}%")

            st.markdown("### 📋 نسب مكونات الخلطة")
            st.dataframe(pd.DataFrame([{"المادة العلفية": k, "النسبة %": round(v, 2), "كجم / طن": round(v * 10, 1)} for k, v in r["formula"].items()]), use_container_width=True, hide_index=True)

            st.markdown("### 📊 مقارنة المحسوب بالقياسي وتشكيل الألوان")
            comp_rows = build_comparison_rows(requirement_to_standard(lp_pack["req"]), r["actual_nutrients"])
            render_colored_comparison_table(comp_rows)

            ch1, ch2, ch3 = st.columns(3)
            with ch1:
                b_img = create_colorful_bar_chart(requirement_to_standard(lp_pack["req"]), r["actual_nutrients"])
                if b_img:
                    st.image(b_img.getvalue(), use_container_width=True)
            with ch2:
                p_img = create_colorful_pie_chart(r["formula"])
                if p_img:
                    st.image(p_img.getvalue(), use_container_width=True)
            with ch3:
                rad_img = create_radar_chart(requirement_to_standard(lp_pack["req"]), r["actual_nutrients"])
                if rad_img:
                    st.image(rad_img.getvalue(), use_container_width=True)

            if REPORTLAB_AVAILABLE:
                pdf_b = pdf_gen.generate_report(r["formula"], lp_pack["req"], lp_pack["animal"], lp_pack["prod"], r["cost"], "عام", r["cost"], "$", requester_name=st.session_state.get("chat_username", ""), protein_basis=lp_pack["basis"], standard_key=f"{lp_pack['animal']}_{lp_pack['prod']}", quality_score=r["quality_score"])
                render_pdf_download_with_approval(pdf_b, f"tawor_lp_{lp_pack['animal']}.pdf", f"تركيبة LP - {lp_pack['animal']} ({lp_pack['prod']})", role, user_name=st.session_state.get("chat_username", ""), key_suffix="lp")
        else:
            st.error(r.get("message", "تعذر إيجاد تركيبة"))

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
        st.session_state["nlp_result"] = nlp_optimize_feed(nlp_sel, _get_ingredient_lookup(), nlp_prices, animal_type=nlp_animal, production_type=nlp_prod, price_product=nlp_price_prod)
    rn = st.session_state.get("nlp_result")
    if rn:
        if rn.get("success"):
            if rn.get("warning"):
                st.warning(rn["warning"])
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("💰 التكلفة / كجم", f"${rn['final_cost']:.4f}")
            c2.metric("⚡ الطاقة ME", f"{rn['final_me']:.0f} (هدف {rn['target_me']:.0f})")
            c3.metric("🧬 البروتين CP", f"{rn['final_cp']:.2f}% (هدف {rn['target_cp']:.1f}%)")
            c4.metric("📈 صافي الربح / كجم", f"${rn['max_profit']:.4f}")
            st.dataframe(pd.DataFrame([{"المكون": k, "النسبة %": v, "كجم/طن": round(v * 10, 1)} for k, v in rn["formula"].items()]), use_container_width=True, hide_index=True)
            fig_p = create_nlp_profit_curve(rn, nlp_sel, _get_ingredient_lookup(), nlp_prices)
            if fig_p:
                st.plotly_chart(fig_p, use_container_width=True)
            pdf_nlp = generate_nlp_math_pdf(rn, nlp_animal, nlp_prod)
            render_pdf_download_with_approval(pdf_nlp, f"tawor_nlp_{nlp_animal}.pdf", f"تقرير NLP - {nlp_animal}", role, user_name=st.session_state.get("chat_username", ""), key_suffix="nlp")
        else:
            st.error(rn.get("message", "تعذر إيجاد حل"))

with tabs[tab_idx]:
    tab_idx += 1
    st.markdown('<div class="section-title">🔬 مختبر تحليل التركيبات وشريط القياس</div>', unsafe_allow_html=True)
    lab_animal = st.selectbox("🐾 الفصيل:", ["أبقار", "أغنام", "ماعز", "إبل", "خيول", "دواجن", "سمان", "أسماك", "أرانب"], key="lab_animal")
    lab_prod = st.text_input("الحالة:", value="حليب_عالي" if lab_animal == "أبقار" else "تسمين_مكثف", key="lab_prod")
    weight_est = weight_tape_widget(lab_animal, "lab_tape")
    st.caption(f"الوزن التقديري المرجعي: {weight_est:.1f} كجم")
    raw_formula_txt = st.text_area("أدخل التركيبة (مثال: ذرة صفراء: 55، كسب فول صويا 44%: 25، نخالة قمح (ردة): 18، ملح الطعام: 2):", height=100, key="lab_raw_txt")
    if st.button("🔬 تحليل التركيبة", type="primary", use_container_width=True, key="btn_run_lab"):
        parsed = _parse_ingredients_from_text(raw_formula_txt)
        if parsed:
            st.session_state["lab_result"] = analyze_existing_formula(parsed, lab_animal, lab_prod)
        else:
            st.warning("⚠️ لم يتم التعرف على مكونات بنسب صالحة")
    lr = st.session_state.get("lab_result")
    if lr and lr.get("success"):
        m1, m2, m3 = st.columns(3)
        m1.metric("⭐ درجة الجودة", f"{lr['quality_score']:.1f}%")
        m2.metric("⚖️ نسبة Ca:P", f"{lr['ca_p_ratio']:.2f}")
        m3.metric("💰 التكلفة / طن", f"${lr['cost_per_ton']:.2f}")
        render_colored_comparison_table(lr["comparison"])
        b_lab = create_colorful_bar_chart(lr["standard"], lr["actual"])
        if b_lab:
            st.image(b_lab.getvalue(), use_container_width=True)
        pdf_lab = generate_lab_pdf(lr, {"animal": lab_animal, "production": lab_prod})
        render_pdf_download_with_approval(pdf_lab, f"tawor_lab_{lab_animal}.pdf", f"تحليل تركيبة - {lab_animal}", role, user_name=st.session_state.get("chat_username", ""), key_suffix="lab")

with tabs[tab_idx]:
    tab_idx += 1
    st.markdown('<div class="section-title">📸 استخراج التركيبات من الصور (OCR)</div>', unsafe_allow_html=True)
    up_ocr = st.file_uploader("ارفع صورة بطاقة أو تركيبة علف:", type=["png", "jpg", "jpeg"], key="ocr_uploader")
    if up_ocr and st.button("🔍 استخراج البيانات", type="primary", key="btn_run_ocr"):
        st.session_state["ocr_result"] = extract_ingredients_from_image(up_ocr.getvalue())
    or_res = st.session_state.get("ocr_result")
    if or_res:
        if or_res.get("success"):
            if or_res.get("raw_text"):
                with st.expander("📝 النص الخام المستخرج"):
                    st.text(or_res["raw_text"])
            corrected = render_ocr_correction_ui(or_res.get("ingredients", {}))
            if corrected:
                nut_c = compute_formula_nutrients(corrected)
                st.dataframe(pd.DataFrame([{"العنصر": k, "المحسوب": v} for k, v in nut_c.items()]), use_container_width=True, hide_index=True)
                pdf_ocr = pdf_gen.generate_ocr_report(corrected, nut_c, or_res.get("raw_text", ""))
                render_pdf_download_with_approval(pdf_ocr, "tawor_ocr.pdf", "تقرير تحليل OCR", role, user_name=st.session_state.get("chat_username", ""), key_suffix="ocr")
        else:
            st.warning(or_res.get("message", "تعذر الاستخراج"))

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

with tabs[tab_idx]:
    tab_idx += 1
    st.markdown('<div class="section-title">🏗️ تصميم الحظائر والإسطبلات ثلاثي الأبعاد (3D) وشرحها</div>', unsafe_allow_html=True)
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
        if bdims.get("explanation"):
            st.markdown(f'<div class="info-card"><b>📐 شرح التصميم والاعتبارات الهندسية والصحية:</b><br>{bdims["explanation"]}</div>', unsafe_allow_html=True)
        fig3d = create_barn_3d_figure(bdims)
        if fig3d:
            st.plotly_chart(fig3d, use_container_width=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📐 المساحة الكلية", f"{bdims['total_area_m2']} م²")
        c2.metric("💨 التهوية الصيفية", f"{bdims['vent_summer_m3h']:,} م³/س")
        c3.metric("💧 الماء اليومي التقريبي", f"{bdims['water_l_day']:,} لتر/يوم")
        c4.metric("💵 التكلفة التقديرية", f"${bdims['cost_total_usd']:,.0f}")
        pdf_barn = generate_barn_pdf(bdims)
        render_pdf_download_with_approval(pdf_barn, "tawor_barn_3d.pdf", f"مخطط حظيرة - {bdims['standard'].get('name_ar', '')}", role, user_name=st.session_state.get("chat_username", ""), key_suffix="barn")

with tabs[tab_idx]:
    tab_idx += 1
    st.markdown('<div class="section-title">🎬 استديو المحتوى والملاحظات</div>', unsafe_allow_html=True)
    studio_data = _load_studio()
    if role == "owner":
        with st.form("studio_note_form", clear_on_submit=True):
            n_title = st.text_input("عنوان الملاحظة / الدرس:")
            n_body = st.text_area("المحتوى:")
            if st.form_submit_button("💾 حفظ في الاستديو") and n_title and n_body:
                studio_data["notes"].append({"title": _sanitize_message(n_title, 100), "body": _sanitize_message(n_body, 1500), "date": datetime.now().strftime("%Y-%m-%d %H:%M")})
                _save_studio(studio_data)
                st.rerun()
    for item in reversed(studio_data.get("notes", [])):
        st.markdown(f'<div class="info-card"><b>{item["title"]}</b> <small>({item["date"]})</small><br>{item["body"]}</div>', unsafe_allow_html=True)

with tabs[tab_idx]:
    tab_idx += 1
    st.markdown('<div class="section-title">💬 غرف النقاش العلمي</div>', unsafe_allow_html=True)
    rooms_dict = _load_chat_rooms()
    active_room = st.selectbox("اختر الغرفة:", list(rooms_dict.keys()), key="chat_active_room")
    if role == "owner":
        new_r = st.text_input("إنشاء غرفة جديدة:", key="chat_new_room")
        if st.button("➕ إضافة غرفة", key="btn_add_room") and new_r and create_chat_room(new_r):
            st.rerun()
    for m in rooms_dict.get(active_room, [])[-40:]:
        st.markdown(f"**{m['user']}** <small>[{m['ts']}]</small>: {m['msg']}", unsafe_allow_html=True)
    with st.form("chat_send_form", clear_on_submit=True):
        msg_txt = st.text_input("اكتب رسالتك:")
        if st.form_submit_button("📤 إرسال") and check_rate_limit("chat", max_calls=20, window=60) and msg_txt:
            add_chat_message(active_room, st.session_state.get("chat_username", "مستخدم"), msg_txt)
            st.rerun()

with tabs[tab_idx]:
    tab_idx += 1
    st.markdown('<div class="section-title">📚 المراجع العلمية المعتمدة</div>', unsafe_allow_html=True)
    for i, ref in enumerate(GENERAL_REFERENCES, 1):
        st.markdown(f"{i}. **{ref}**")

if role == "owner":
    with tabs[tab_idx]:
        render_pdf_requests_admin()

st.markdown(f"""<div class="footer"><div>🤲 <b>{DUA_FULL}</b> 🤲</div><div style="margin-top:6px;">{APP_NAME} v{APP_VERSION} — إشراف: {SUPERVISOR}</div></div>""", unsafe_allow_html=True)
