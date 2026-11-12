# ═══════════════════════════════════════════════════════════════════════════
# تاور نولجي TAWOR NOLOGY 11.8 — النسخة الكاملة
# د. عبدالقادر إسماعيل تاور — اختصاصي تغذية الحيوان
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
# ═══════════════════════════════════════════════════════════════════════════
# الجديد في 11.8:
#   ✅ تبويبات هرمية (5 أقسام بدل 18)
#   ✅ NLP مع اختيار الحيوان (NRC-accurate)
#   ✅ المختبر مع مقارنة معيارية
#   ✅ التبويبات الفرعية: LP | NLP | الحليب | الزيوت | المختبر
#   ✅ تحليل مالي متقدم (تدفقات + NPV + سيناريوهات)
#   ✅ كل ميزات 11.7 محفوظة (NLP + دردشة + استديو + أمان)
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
# الاستيرادات الاختيارية
# ═══════════════════════════════════════════════════════════════════════════

try:
    from scipy.optimize import linprog, minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    linprog = None
    minimize = None

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
    from reportlab.lib.pagesizes import A4, letter
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
# 🔐 الأمان
# ═══════════════════════════════════════════════════════════════════════════

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


@lru_cache(maxsize=1)
def _embedded_owner_code() -> Optional[str]:
    try:
        _blob = "Nzg2MjAy"
        decoded = base64.b64decode(_blob).decode()
        return decoded[::-1]
    except Exception:
        return None


def _get_owner_code_hash() -> Optional[str]:
    try:
        if hasattr(st, "secrets"):
            code = str(st.secrets.get("OWNER_CODE", "") or "").strip()
            if code:
                return _sha256(code)
    except Exception:
        pass
    try:
        code = str(os.environ.get("TAWOR_OWNER_CODE", "") or "").strip()
        if code:
            return _sha256(code)
    except Exception:
        pass
    emb = _embedded_owner_code()
    if emb:
        return _sha256(emb)
    return None


def check_owner_code(user_input: str) -> bool:
    if not user_input:
        audit_log("LOGIN_EMPTY", "")
        return False
    expected = _get_owner_code_hash()
    if not expected:
        audit_log("LOGIN_NO_HASH", "")
        return False
    ok = hmac.compare_digest(_sha256(user_input.strip()), expected)
    audit_log("LOGIN_OK" if ok else "LOGIN_FAIL", "")
    return ok


def _session_valid() -> bool:
    approved = st.session_state.get("approved", False)
    role = st.session_state.get("user_role")
    if approved and role not in ("owner", "guest"):
        return False
    if role == "owner" and not _get_owner_code_hash():
        return False
    return True


def audit_log(event: str, details: str = "") -> None:
    try:
        with open("tawor_audit.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] "
                    f"{event} | {details[:200]}\n")
    except Exception:
        pass


def check_rate_limit(key: str, max_calls: int = 30,
                     window: int = 60) -> bool:
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
        st.session_state["csrf_token"] = base64.b64encode(
            os.urandom(32)).decode()
    return st.session_state["csrf_token"]


def validate_csrf_token(token: str) -> bool:
    expected = st.session_state.get("csrf_token", "")
    return hmac.compare_digest(str(token), expected) if expected else False


def _sanitize_message(msg: str, max_len: int = 500) -> str:
    if not msg:
        return ""
    msg = str(msg).strip()[:max_len]
    msg = re.sub(r'<[^>]+>', '', msg)
    msg = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', msg)
    return msg


def _safe_username() -> str:
    if "chat_username" not in st.session_state:
        st.session_state["chat_username"] = (
            f"{'المالك' if st.session_state.get('user_role') == 'owner' else 'زائر'}_"
            f"{random.randint(1000, 9999)}")
    return st.session_state["chat_username"]


# ═══════════════════════════════════════════════════════════════════════════
# 🆕 v11.8 — دالة NLP المطوّرة (مع احتياجات الحيوان)
# ═══════════════════════════════════════════════════════════════════════════

def nlp_optimize_feed_v2(ingredient_names, ingredient_data, prices,
                          requirement, animal_type, standard_key="",
                          protein_basis="DP",
                          price_product=2.5, max_per_ing=0.6):
    """🎯 تحسين غير خطي دقيق حسب احتياجات NRC."""
    n = len(ingredient_names)
    if n < 2:
        return {"success": False, "message": "يلزم مكونان على الأقل"}
    if not SCIPY_AVAILABLE or minimize is None:
        return {"success": False, "message": "SCIPY غير متوفرة"}

    se_vals = np.array([ingredient_data[i].get("SE", 0) for i in ingredient_names])
    me_vals = se_vals * 41.0
    cp_vals = np.array([ingredient_data[i].get("CP", 0) for i in ingredient_names])
    dp_vals = np.array([ingredient_data[i].get("CP", 0) *
                        ingredient_data[i].get("DC", 0.8) for i in ingredient_names])
    ca_vals = np.array([ingredient_data[i].get("Ca", 0) for i in ingredient_names])
    p_vals = np.array([ingredient_data[i].get("P", 0) for i in ingredient_names])
    ndf_vals = np.array([ingredient_data[i].get("NDF", 0) for i in ingredient_names])
    adf_vals = np.array([ingredient_data[i].get("ADF", 0) for i in ingredient_names])
    lys_vals = np.array([ingredient_data[i].get("Lys", 0) for i in ingredient_names])
    met_vals = np.array([ingredient_data[i].get("Met", 0) for i in ingredient_names])
    cost_vals = np.array([prices.get(i, 300.0) / 1000.0 for i in ingredient_names])

    target_me = requirement.SE * 41.0
    target_cp = requirement.DP / 0.75 if protein_basis == "DP" else requirement.CP
    target_ca = requirement.Ca
    target_p = requirement.P
    target_lys = getattr(requirement, 'Lys', 0)
    target_met = getattr(requirement, 'Met', 0)

    is_rum = animal_type in ("أبقار", "أغنام", "ماعز", "إبل")
    is_poultry = animal_type in ("دواجن", "سمان")
    ndf_max = requirement.NDF * (1.20 if is_rum else 1.10)
    adf_max = requirement.ADF * (1.25 if is_rum else 1.10)

    if is_poultry:
        ca_p_min, ca_p_max = 1.5, 2.2
    elif is_rum:
        ca_p_min, ca_p_max = 1.4, 2.5
    else:
        ca_p_min, ca_p_max = 1.4, 2.0

    oil_std = get_oil_standard(standard_key)
    oil_max_pct = oil_std["max"]
    oil_ind = np.array([1.0 if i in get_oil_ingredients() else 0.0
                        for i in ingredient_names])

    bounds = [(0.0, max_per_ing) for _ in range(n)]

    cons = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},
        {'type': 'ineq', 'fun': lambda x: np.dot(me_vals, x) - target_me * 0.98},
        {'type': 'ineq', 'fun': lambda x: np.dot(cp_vals, x) - target_cp * 0.98},
        {'type': 'ineq', 'fun': lambda x: np.dot(ca_vals, x) - target_ca * 0.85},
        {'type': 'ineq', 'fun': lambda x: np.dot(p_vals, x) - target_p * 0.85},
        {'type': 'ineq', 'fun': lambda x: ndf_max - np.dot(ndf_vals, x)},
        {'type': 'ineq', 'fun': lambda x: adf_max - np.dot(adf_vals, x)},
        {'type': 'ineq', 'fun': lambda x: np.dot(ca_vals, x) - ca_p_min * np.dot(p_vals, x)},
        {'type': 'ineq', 'fun': lambda x: ca_p_max * np.dot(p_vals, x) - np.dot(ca_vals, x)},
        {'type': 'ineq', 'fun': lambda x: oil_max_pct/100.0 - np.dot(oil_ind, x)},
    ]
    if target_lys > 0:
        cons.append({'type': 'ineq',
                     'fun': lambda x: np.dot(lys_vals, x) - target_lys * 0.85})
    if target_met > 0:
        cons.append({'type': 'ineq',
                     'fun': lambda x: np.dot(met_vals, x) - target_met * 0.85})

    def objective(x):
        total_cost = np.dot(cost_vals, x)
        me_ratio = np.dot(me_vals, x) / target_me if target_me > 0 else 1.0
        cp_ratio = np.dot(cp_vals, x) / target_cp if target_cp > 0 else 1.0
        quality_value = me_ratio * cp_ratio
        return -(price_product * quality_value - total_cost)

    x0 = np.ones(n) / n

    try:
        res = minimize(objective, x0, method='SLSQP', bounds=bounds,
                       constraints=cons,
                       options={'maxiter': 2000, 'ftol': 1e-9})
    except Exception as e:
        return {"success": False, "message": f"خطأ: {e}"}

    if not res.success:
        soft_cons = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},
            {'type': 'ineq', 'fun': lambda x: np.dot(me_vals, x) - target_me * 0.90},
            {'type': 'ineq', 'fun': lambda x: np.dot(cp_vals, x) - target_cp * 0.90},
        ]
        try:
            res = minimize(objective, x0, method='SLSQP', bounds=bounds,
                           constraints=soft_cons,
                           options={'maxiter': 2000, 'ftol': 1e-9})
        except Exception:
            pass

    if not res.success:
        return {"success": False, "message": f"فشل: {res.message}"}

    x_opt = res.x
    formula = {name: round(float(x_opt[i]) * 100, 2)
               for i, name in enumerate(ingredient_names)
               if x_opt[i] > 0.001}

    p_total = float(np.dot(p_vals, x_opt))
    ca_p = (float(np.dot(ca_vals, x_opt) / p_total) if p_total > 0 else 0.0)

    return {
        "success": True,
        "formula": formula,
        "x_opt": x_opt.tolist(),
        "final_cost": float(np.dot(cost_vals, x_opt)),
        "final_me": float(np.dot(me_vals, x_opt)),
        "final_cp": float(np.dot(cp_vals, x_opt)),
        "final_dp": float(np.dot(dp_vals, x_opt)),
        "final_ca": float(np.dot(ca_vals, x_opt)),
        "final_p": p_total,
        "final_ndf": float(np.dot(ndf_vals, x_opt)),
        "final_adf": float(np.dot(adf_vals, x_opt)),
        "ca_p_ratio": ca_p,
        "oil_total": float(np.dot(oil_ind, x_opt) * 100),
        "oil_max": oil_max_pct,
        "max_profit": float(-res.fun),
        "iterations": int(res.nit),
        "requirement": requirement,
        "animal_type": animal_type,
        "basis": protein_basis,
    }


# ═══════════════════════════════════════════════════════════════════════════
# 🆕 v11.8 — دالة اختيار حيوان موحّدة
# ═══════════════════════════════════════════════════════════════════════════

def get_animal_requirement_ui(key_prefix: str = "req", compact: bool = False):
    """🐾 واجهة موحدة لاختيار الحيوان + الاحتياجات."""
    c1, c2 = st.columns(2)
    with c1:
        a = st.selectbox(
            "🐾 الحيوان:",
            ["أبقار", "أغنام", "ماعز", "إبل", "خيول",
             "دواجن", "سمان", "أسماك", "أرانب"],
            key=f"{key_prefix}_animal")
    with c2:
        prod_map = {
            "أبقار": ["حليب_عالي", "حليب_متوسط", "حليب_منخفض",
                      "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"],
            "أغنام": ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد",
                      "مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
            "ماعز": ["تسمين_جديان", "تيوس", "حلابة_عالي",
                     "حلابة_متوسط", "حامل_أخير", "صيانة"],
            "إبل": ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
            "خيول": ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار",
                     "مرضعات", "صيانة"],
            "دواجن": ["لاحم", "بياض"],
            "سمان": ["تسمين", "بياض"],
            "أسماك": ["بادئ زريعة", "نمو", "تسمين"],
            "أرانب": ["تسمين", "حليب", "صيانة"],
        }
        p = st.selectbox("📋 الحالة:", prod_map[a], key=f"{key_prefix}_prod")

    extra = {}
    if a == "أبقار" and "حليب" in p:
        extra["milk_yield"] = st.number_input(
            "🥛 الحليب (كجم/يوم):", 5.0, 60.0, 20.0, 1.0,
            key=f"{key_prefix}_milk")
    elif a == "ماعز" and "حلابة" in p:
        extra["milk_yield"] = st.number_input(
            "🥛 الحليب (لتر/يوم):", 0.5, 8.0, 2.0, 0.25,
            key=f"{key_prefix}_milk")
    elif a == "إبل" and p == "حليب":
        extra["milk_yield"] = st.number_input(
            "🥛 الحليب (لتر/يوم):", 2.0, 20.0, 5.0, 0.5,
            key=f"{key_prefix}_milk")
    elif a == "أغنام" and p == "مرضعات":
        extra["litter_size"] = st.number_input(
            "👶 عدد المواليد:", 1, 3, 1, 1, key=f"{key_prefix}_lit")
        extra["is_male"] = False
    elif a == "أغنام":
        extra["is_male"] = p not in ("مرضعات", "حامل_أخير",
                                     "حامل_متوسط", "صيانة")
    elif a == "ماعز":
        extra["is_male"] = p in ("تسمين_جديان", "تيوس")

    if a == "دواجن":
        age = st.number_input("العمر (أسبوع):", 1, 20, 1, 1,
                              key=f"{key_prefix}_age")
        req = get_poultry_requirements(p, age)
    elif a == "سمان":
        age = st.number_input("العمر (أسبوع):", 1, 8, 1, 1,
                              key=f"{key_prefix}_age")
        req = get_quail_requirements(p, age)
    elif a == "أسماك":
        req = get_fish_requirements("البلطي", p)
    elif a == "أبقار":
        req = get_cattle_requirements(p, **extra)
    elif a == "أغنام":
        req = get_sheep_requirements(p, **extra)
    elif a == "ماعز":
        req = get_goat_requirements(p, **extra)
    elif a == "إبل":
        req = get_camel_requirements(p, **extra)
    elif a == "خيول":
        req = get_horse_requirements(p)
    elif a == "أرانب":
        req = get_rabbit_requirements(p)
    else:
        return None, None, None, None

    std_key_map = {
        ("دواجن", "لاحم"): "دواجن_بادي",
        ("دواجن", "بياض"): "دواجن_بياض",
        ("سمان", "تسمين"): "سمان_بادي",
        ("سمان", "بياض"): "سمان_بياض",
    }
    std_key = std_key_map.get((a, p), f"{a}_{p}")
    return a, p, req, std_key


# ═══════════════════════════════════════════════════════════════════════════
# 🆕 v11.8 — دوال الدردشة والاستديو (محفوظة من 11.7)
# ═══════════════════════════════════════════════════════════════════════════

CHAT_FILE = "tawor_chat_rooms.json"


def _load_chat_rooms():
    try:
        if os.path.exists(CHAT_FILE):
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
    except Exception:
        pass
    return {"🌾 الغرفة العامة": []}


def _save_chat_rooms(data):
    try:
        tmp = CHAT_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, CHAT_FILE)
    except Exception:
        pass


def add_chat_message(room, user, message):
    msg = _sanitize_message(message)
    user = _sanitize_message(user, 40)
    if not msg or not user:
        return False
    rooms = _load_chat_rooms()
    rooms.setdefault(room, [])
    rooms[room].append({
        "user": user, "msg": msg,
        "ts": datetime.now().strftime("%H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "role": st.session_state.get("user_role", "guest"),
    })
    rooms[room] = rooms[room][-500:]
    _save_chat_rooms(rooms)
    return True


def create_chat_room(room_name):
    rooms = _load_chat_rooms()
    name = _sanitize_message(room_name, 40)
    if name and name not in rooms:
        rooms[name] = []
        _save_chat_rooms(rooms)
        return True
    return False


STUDIO_FILE = "tawor_studio_content.json"


def _load_studio():
    try:
        if os.path.exists(STUDIO_FILE):
            with open(STUDIO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"videos": [], "slides": [], "notes": []}


def _save_studio(data):
    try:
        tmp = STUDIO_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, STUDIO_FILE)
    except Exception:
        pass


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
APP_VERSION = "11.8"
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
# الخطوط العربية
# ═══════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════
# مكتبة الأعلاف (نفس 11.7 — 200+ مكون)
# ═══════════════════════════════════════════════════════════════════════════

def _feed(cp, dc, se, ndf, adf, ee, ash, ca, p, lys, met, price, desc, src):
    return {"CP": cp, "DC": dc, "SE": se, "NDF": ndf, "ADF": adf,
            "EE": ee, "ASH": ash, "Ca": ca, "P": p,
            "Lys": lys, "Met": met,
            "price": price, "desc": desc, "src": src}


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
        "مركزات دواجن": _feed(40, .85, 60, 8.5, 4.5, 3.5, 12.5, 2.5, 1.2, 2.5, .9, 650, "جاهزة", "NRC 2012"),
        "مركزات مواشي": _feed(36, .8, 55, 15.5, 8.5, 3, 15.5, 3, 1.5, 2, .7, 600, "جاهزة", "NRC 2001"),
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
        "ملح الطعام": _feed(0, 0, 0, 0, 0, 0, 99.9, 0, 0, 0, 0, 30, "NaCl", "NRC 2012"),
        "بيكربونات الصوديوم": _feed(0, 0, 0, 0, 0, 0, 99, 0, 0, 0, 0, 340, "مضاد حموضة", "NRC 2001"),
        "أكسيد المغنيسيوم": _feed(0, 0, 0, 0, 0, 0, 99.5, 0, 0, 0, 0, 480, "Mg", "NRC 2007"),
        "كبريتات المغنيسيوم": _feed(0, 0, 0, 0, 0, 0, 98, 0, 0, 0, 0, 380, "MgSO4", "NRC 2007"),
        "يوريا علفية": _feed(287, .95, 0, 0, 0, 0, 1, 0, 0, 0, 0, 480, "NPN — بحذر", "NRC 2001"),
        "مضاد سموم فطرية": _feed(0, 0, 0, 0, 0, 0, 85, 0, 0, 0, 0, 950, "أفلاتوكسين", "NRC 2012"),
        "مضاد أكسدة BHT": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 1200, "تزنخ", "NRC 2012"),
        "كولين كلوريد": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 3200, "B4", "NRC 2012"),
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
        "مضاد كوكسيديا": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 4200, "للدواجن", "NRC 1994"),
        "مضاد فطريات": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 2800, "حفظ العلف", "NRC 2012"),
        "منشط نمو طبيعي": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 8500, "بديل مضادات", "NRC 2012"),
        "محسن نكهة": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 3800, "استساغة", "NRC 2012"),
        "ملون طبيعي": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 6200, "لون الصفار", "NRC 2012"),
        "بيتاين (Betaine)": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 4800, "إجهاد حراري", "NRC 2012"),
        "أحماض عضوية": _feed(0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 3200, "حفظ", "NRC 2012"),
        "بيتا جلوكان": _feed(10, .5, 20, 5, 3, 1, 5, .1, .15, .3, .1, 12000, "مناعة", "NRC 2012"),
        "طحالب كالبتوس": _feed(8, .6, 25, 10, 6, 2, 35, 2.5, .3, .3, .15, 2500, "معادن نادرة", "FAO 2010"),
    },
}


def _get_ingredient_lookup() -> Dict[str, Dict]:
    if not hasattr(_get_ingredient_lookup, "_cache"):
        lookup = {}
        for cat in BIG_FEEDS_LIBRARY.values():
            for name, data in cat.items():
                lookup[name] = data
        _get_ingredient_lookup._cache = lookup
    return _get_ingredient_lookup._cache


def get_oil_ingredients() -> Dict[str, Dict]:
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت النباتية والحيوانية", {})


def get_total_ingredient_count() -> int:
    return len(_get_ingredient_lookup())


# ═══════════════════════════════════════════════════════════════════════════
# معايير الزيوت
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
    return MAX_OIL_PERCENTAGE.get(k, {"max": 5.0, "optimal": 3.0, "source": "عام"})


# ═══════════════════════════════════════════════════════════════════════════
# حدود المكونات
# ═══════════════════════════════════════════════════════════════════════════

INGREDIENT_LIMITS_BY_ANIMAL = {
    "دواجن": {
        "يوريا علفية": (0, 0), "سمن حيواني (Lard)": (0, 0),
        "دهن الدجاج": (0, 3), "نخالة قمح (ردة)": (0, 10),
        "نخالة ذرة": (0, 5), "تبن قمح": (0, 2), "قش أرز": (0, 2),
        "سرسة الأرز": (0, 2), "كسب بذور القطن": (0, 5),
        "كسب السمسم": (0, 8), "كسب الكانولا": (0, 8),
        "ملح الطعام": (.2, .4), "الحجر الجيري": (.8, 2),
        "فوسفات ثنائي الكالسيوم": (.5, 2.5),
        "بيكربونات الصوديوم": (0, .5),
        "مضاد سموم فطرية": (.05, .15),
        "بريمكس تسمين دواجن": (.2, .35), "بريمكس بياض": (.2, .35),
        "ليسين نقي": (0, .5), "ميثيونين نقي": (0, .4),
        "زيت ذرة": (0, 5), "زيت فول الصويا": (0, 6),
    },
    "سمان": {
        "يوريا علفية": (0, 0), "سمن حيواني (Lard)": (0, 0),
        "نخالة قمح (ردة)": (0, 8), "ملح الطعام": (.2, .4),
        "الحجر الجيري": (.8, 2.5),
        "فوسفات ثنائي الكالسيوم": (.5, 2),
        "بريمكس تسمين دواجن": (.2, .35), "بريمكس بياض": (.2, .35),
    },
    "أبقار": {
        "يوريا علفية": (0, 1.5), "نخالة قمح (ردة)": (0, 30),
        "كسب بذور القطن": (0, 20), "كسب السمسم": (0, 15),
        "ملح الطعام": (.3, .5), "بيكربونات الصوديوم": (.5, 1),
        "الحجر الجيري": (0, 3.5),
        "فوسفات ثنائي الكالسيوم": (0, 2),
        "بريمكس أبقار": (.15, .3), "بريمكس مجترات": (.15, .3),
        "مضاد سموم فطرية": (.05, .15),
    },
    "أغنام": {
        "يوريا علفية": (0, 1), "نخالة قمح (ردة)": (0, 25),
        "كسب بذور القطن": (0, 15), "ملح الطعام": (.3, .5),
        "بيكربونات الصوديوم": (.5, 1), "بريمكس مجترات": (.15, .3),
        "الحجر الجيري": (0, 3), "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "ماعز": {
        "يوريا علفية": (0, 1), "نخالة قمح (ردة)": (0, 25),
        "ملح الطعام": (.3, .5), "بيكربونات الصوديوم": (.5, 1),
        "بريمكس مجترات": (.15, .3), "الحجر الجيري": (0, 3),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "إبل": {
        "يوريا علفية": (0, 1), "نخالة قمح (ردة)": (0, 20),
        "ملح الطعام": (.3, .5), "بيكربونات الصوديوم": (.5, 1),
        "بريمكس إبل": (.15, .3), "الحجر الجيري": (0, 3),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "خيول": {
        "يوريا علفية": (0, .5), "نخالة قمح (ردة)": (0, 20),
        "ملح الطعام": (.3, .5), "بريمكس خيول": (.15, .3),
        "الحجر الجيري": (0, 2.5), "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "أسماك": {
        "يوريا علفية": (0, 0), "سمن حيواني (Lard)": (0, 0),
        "نخالة قمح (ردة)": (0, 10), "ملح الطعام": (0, .3),
        "بريمكس أسماك": (.15, .3), "الحجر الجيري": (0, 2),
        "فوسفات ثنائي الكالسيوم": (0, 2),
    },
    "أرانب": {
        "يوريا علفية": (0, .5), "نخالة قمح (ردة)": (0, 20),
        "ملح الطعام": (.3, .5), "بريمكس مجترات": (.15, .3),
        "الحجر الجيري": (0, 2.5), "فوسفات ثنائي الكالسيوم": (0, 2),
    },
}


def get_animal_limits(animal: str) -> Dict[str, Tuple[float, float]]:
    return INGREDIENT_LIMITS_BY_ANIMAL.get(animal, {})


# ═══════════════════════════════════════════════════════════════════════════
# الاحتياجات الغذائية (AnimalRequirement + دوال NRC)
# ═══════════════════════════════════════════════════════════════════════════

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


def get_cattle_requirements(t: str, milk_yield: float = 20.0,
                            weight_kg: float = 500.0) -> AnimalRequirement:
    if t == "حليب_عالي":
        dp = 12.5 + milk_yield * .30
        return AnimalRequirement(round(dp, 2), round(dp / .70, 2),
                                 round(60 + milk_yield * .35, 1), 30, 19, 5.5, 8,
                                 round(.55 + milk_yield * .003, 3),
                                 round(.33 + milk_yield * .0015, 3),
                                 "أبقار حلابة عالية", f"حليب {milk_yield} كجم")
    if t == "حليب_متوسط":
        dp = 11 + milk_yield * .25
        return AnimalRequirement(round(dp, 2), round(dp / .72, 2),
                                 round(55 + milk_yield * .3, 1), 33, 21, 4.5, 8,
                                 round(.5 + milk_yield * .0025, 3),
                                 round(.3 + milk_yield * .0012, 3),
                                 "أبقار حلابة متوسطة", f"حليب {milk_yield} كجم")
    if t == "حليب_منخفض":
        dp = 9.5 + milk_yield * .2
        return AnimalRequirement(round(dp, 2), round(dp / .75, 2),
                                 round(50 + milk_yield * .25, 1), 38, 24, 4, 8.5,
                                 round(.45 + milk_yield * .002, 3),
                                 round(.28 + milk_yield * .001, 3),
                                 "أبقار حلابة منخفضة", f"حليب {milk_yield} كجم")
    if t == "تسمين_مكثف":
        return AnimalRequirement(11.5, 14.5, 72, 32, 20, 4.5, 7.5, .65, .38,
                                 "تسمين عجول مكثف", "ADG >1.3")
    if t == "تسمين_عادي":
        return AnimalRequirement(9.5, 12, 65, 38, 24, 4, 7.5, .55, .32,
                                 "تسمين عجول عادي", "ADG ~0.8")
    if t == "حمل_أخير":
        return AnimalRequirement(11.5, 14.5, 67, 35, 22, 4.2, 8, .7, .42,
                                 "حمل آخر", "شهر 7-9")
    return AnimalRequirement(7.5, 10, 53, 45, 28, 3, 8.5, .42, .26,
                             "أبقار صيانة", "بدون إنتاج")


def get_sheep_requirements(t: str, is_male: bool = True,
                            weight_kg: float = 50.0,
                            litter_size: int = 1) -> AnimalRequirement:
    if is_male:
        if t == "تسمين_مكثف":
            return AnimalRequirement(11.5, 14.5, 64, 28, 17, 4, 8, .65, .36,
                                     "تسمين مكثف", "ADG >250")
        if t == "تسمين_عادي":
            return AnimalRequirement(9.5, 12, 59, 33, 21, 3.6, 8, .55, .32,
                                     "تسمين عادي", "ADG ~180")
        return AnimalRequirement(8.5, 11, 55, 38, 24, 3.2, 8.5, .5, .3,
                                 "حملان تيد", "بداية")
    if t == "مرضعات":
        dp = 10.5 + (litter_size - 1) * 1.5
        return AnimalRequirement(round(dp, 2), round(dp / .72, 2),
                                 round(60 + (litter_size - 1) * 5, 1), 30, 19, 4.5, 8.5,
                                 round(.65 + (litter_size - 1) * .1, 3),
                                 round(.38 + (litter_size - 1) * .05, 3),
                                 f"نعاج مرضعات ({litter_size} مولود)", "")
    if t == "حامل_أخير":
        return AnimalRequirement(10.5, 13.5, 62, 32, 20, 3.8, 8, .6, .35,
                                 "نعاج حامل (4-5)", "")
    if t == "حامل_متوسط":
        return AnimalRequirement(8.5, 11, 55, 38, 24, 3.4, 8, .5, .3,
                                 "نعاج حامل (1-3)", "")
    return AnimalRequirement(7.2, 9.5, 48, 45, 28, 3, 8.5, .42, .26,
                             "نعاج صيانة", "")


def get_goat_requirements(t: str, is_male: bool = True,
                           milk_yield: float = 2.0) -> AnimalRequirement:
    if is_male:
        if t == "تسمين_جديان":
            return AnimalRequirement(11, 14, 62, 30, 19, 3.8, 8, .62, .34,
                                     "تسمين جديان", "")
        return AnimalRequirement(9, 11.5, 57, 36, 22, 3.5, 8, .55, .3,
                                 "تيوس تسمين", "")
    if t == "حلابة_عالي":
        dp = 11.5 + milk_yield * .45
        return AnimalRequirement(round(dp, 2), round(dp / .7, 2),
                                 round(58 + milk_yield * .45, 1), 29, 18, 4.5, 8.5,
                                 round(.6 + milk_yield * .008, 3),
                                 round(.35 + milk_yield * .004, 3),
                                 f"عنزات حلابة ({milk_yield} لتر)", "")
    if t == "حلابة_متوسط":
        dp = 10 + milk_yield * .35
        return AnimalRequirement(round(dp, 2), round(dp / .72, 2),
                                 round(55 + milk_yield * .4, 1), 32, 20, 4, 8.5,
                                 round(.55 + milk_yield * .006, 3),
                                 round(.32 + milk_yield * .003, 3),
                                 f"عنزات حلابة ({milk_yield} لتر)", "")
    if t == "حامل_أخير":
        return AnimalRequirement(10, 13, 60, 33, 21, 3.8, 8, .6, .35,
                                 "عنزات حامل", "")
    return AnimalRequirement(6.8, 9, 46, 46, 28, 3, 8.5, .42, .26,
                             "عنزات صيانة", "")


def get_camel_requirements(t: str, weight_kg: float = 400.0,
                             milk_yield: float = 5.0) -> AnimalRequirement:
    if t == "نمو":
        return AnimalRequirement(10.5, 13.5, 60, 38, 24, 4, 8, .65, .38,
                                 "إبل نمو", f"{weight_kg} كجم")
    if t == "تسمين":
        return AnimalRequirement(9.5, 12, 65, 35, 22, 4.5, 7.5, .6, .35,
                                 "إبل تسمين", f"{weight_kg} كجم")
    if t == "حليب":
        dp = 12 + milk_yield * .25
        return AnimalRequirement(round(dp, 2), round(dp / .7, 2),
                                 round(62 + milk_yield * .4, 1), 32, 20, 5, 8.5,
                                 round(.7 + milk_yield * .006, 3),
                                 round(.4 + milk_yield * .003, 3),
                                 f"إبل حلابة ({milk_yield} لتر)", "")
    if t == "سباق":
        return AnimalRequirement(14, 17, 72, 28, 17, 6, 9, .85, .5,
                                 "إبل سباق", "طاقة عالية")
    return AnimalRequirement(7, 9, 48, 48, 30, 3.5, 9, .42, .26,
                             "إبل صيانة", f"{weight_kg} كجم")


def get_horse_requirements(t: str,
                             weight_kg: float = 450.0) -> AnimalRequirement:
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


def get_poultry_requirements(strain: str,
                               age_weeks: int = 1) -> AnimalRequirement:
    if strain == "لاحم":
        if age_weeks <= 1:
            return AnimalRequirement(20, 23, 76, 8, 4, 5, 6.5, 1, .5,
                                     "بادي لاحم", "Energy 3000")
        if age_weeks <= 3:
            return AnimalRequirement(18.5, 21, 74, 9, 5, 5, 6, .9, .45,
                                     "نامي لاحم", "Energy 3100")
        if age_weeks <= 5:
            return AnimalRequirement(17, 19.5, 75, 10, 5.5, 4.5, 6, .87, .43,
                                     "ناهي لاحم", "Energy 3150")
        return AnimalRequirement(16.5, 19, 75, 10, 5.5, 4.5, 6, .85, .42,
                                 "ناهي لاحم+", "Energy 3200")
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
    if strain == "بياض":
        return AnimalRequirement(15, 18, 68, 11, 5.5, 4.5, 9, 2.5, .45,
                                 "سمان بياض", "")
    if age_weeks <= 2:
        return AnimalRequirement(20.5, 24, 74, 8, 4, 5.5, 6.5, 1, .55,
                                 "سمان بادي", "")
    if age_weeks <= 4:
        return AnimalRequirement(18.5, 22, 72, 9, 4.5, 5, 6, .9, .5,
                                 "سمان نامي", "")
    return AnimalRequirement(17, 20, 70, 10, 5, 4.5, 6, .85, .45,
                             "سمان ناهي", "")


def get_fish_requirements(species: str,
                            stage: str) -> AnimalRequirement:
    if "بادئ" in stage or "زريعة" in stage:
        return AnimalRequirement(32, 40, 72, 8, 4, 10, 11, 1.5, .9,
                                 f"{species} بادئ", "")
    if "نمو" in stage:
        return AnimalRequirement(25, 32, 70, 12, 6, 8, 9, 1, .7,
                                 f"{species} نمو", "")
    return AnimalRequirement(22, 28, 68, 13, 7, 8, 9.5, .9, .65,
                             f"{species} تسمين", "")


def get_rabbit_requirements(t: str,
                              weight_kg: float = 4.0) -> AnimalRequirement:
    if t == "تسمين":
        return AnimalRequirement(15, 17, 65, 25, 15, 3, 8, .7, .35,
                                 "أرانب تسمين", "ADG 40")
    if t == "حليب":
        return AnimalRequirement(18, 20, 68, 25, 15, 4, 8.5, .85, .45,
                                 "أرانب حلابة", "أمهات")
    return AnimalRequirement(12, 14, 60, 30, 20, 2.5, 8.5, .6, .3,
                             "أرانب صيانة", "")


def requirement_to_standard(req: AnimalRequirement) -> Dict[str, float]:
    return {"CP": req.CP, "DP": req.DP, "SE": req.SE,
            "NDF": req.NDF, "ADF": req.ADF, "EE": req.EE,
            "ASH": req.ASH, "Ca": req.Ca, "P": req.P}


# ═══════════════════════════════════════════════════════════════════════════
# الحسابات
# ═══════════════════════════════════════════════════════════════════════════

def compute_formula_nutrients(formula: Dict[str, float]) -> Dict[str, float]:
    totals = {k: 0.0 for k in ["CP", "DP", "SE", "NDF", "ADF", "EE",
                                 "ASH", "Ca", "P", "Lys", "Met"]}
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
    oils = set(get_oil_ingredients().keys())
    return sum(p for i, p in formula.items() if i in oils)


def evaluate_difference(pct_diff: float,
                         standard_value: Optional[float] = None) -> Dict:
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
    name = re.sub(r'\s+', ' ', str(name).strip())
    lookup = _get_ingredient_lookup()
    if name in lookup:
        return name
    for lib in lookup.keys():
        if lib.lower() in name.lower() or name.lower() in lib.lower():
            return lib
    kw = {
        "ذره": "ذرة صفراء", "ذرة": "ذرة صفراء",
        "صويا": "كسب فول صويا 44%", "شعير": "شعير مطحون",
        "قمح": "قمح محلي", "نخاله": "نخالة قمح (ردة)",
        "نخالة": "نخالة قمح (ردة)", "ملح": "ملح الطعام",
        "حجر": "الحجر الجيري", "فوسفات": "فوسفات ثنائي الكالسيوم",
        "يوريا": "يوريا علفية",
    }
    for k, v in kw.items():
        if k in name.lower():
            return v
    return name


# ═══════════════════════════════════════════════════════════════════════════
# محرك LP
# ═══════════════════════════════════════════════════════════════════════════

def auto_formulate_smart(available_ingredients: List[str],
                           prices: Dict[str, float],
                           custom_standard: Dict[str, float],
                           standard_key: str = "",
                           basis: str = "DP",
                           min_quality: float = 70.0,
                           animal_type: str = "",
                           production_type: str = "") -> Dict:
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

    is_rum = animal_type in ("أبقار", "أغنام", "ماعز", "إبل")
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
        elif is_rum:
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
        if is_rum:
            A_ub_base.append([-x for x in rows["NDF"]])
            b_ub_base.append(-target_ndf * 0.85 * 100.0)
            A_ub_base.append(rows["NDF"])
            b_ub_base.append(target_ndf * 1.20 * 100.0)
        else:
            A_ub_base.append(rows["NDF"])
            b_ub_base.append(target_ndf * (1.10 if is_poultry else 1.15) * 100.0)
    if target_adf > 0:
        A_ub_base.append(rows["ADF"])
        mult = 1.30 if is_rum else (1.10 if is_poultry else 1.20)
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

    strategies = [("دقيق", "eq"), ("مرن ±5%", "r05"),
                  ("مرن ±10%", "r10"), ("مرن ±15%", "r15"),
                  ("طوارئ", "none")]

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
                    best = {"success": True, "formula": formula,
                            "cost": res.fun / 100.0,
                            "actual_nutrients": actual,
                            "quality_score": q, "strategy": label,
                            "meets_standard": q >= min_quality,
                            "targets": custom_standard, "basis": basis,
                            "oil_std": oil_std,
                            "total_oil": compute_total_oil_percentage(formula)}
                if q >= 92:
                    break
        except Exception:
            continue

    if best:
        if not best["meets_standard"]:
            best["warning"] = (
                f"⚠️ الجودة {best_q:.1f}% < {min_quality}%")
        return best
    return {"success": False, "message": "تعذر إيجاد حل"}


def compute_sensitivity(formula: Dict[str, float],
                         targets: Dict[str, float],
                         animal_type: str) -> Dict[str, Dict]:
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
        new_q, new_nut = evaluate_quality_weighted(modified, targets, animal_type)
        deviations[nut] = {
            "delta_quality": round(new_q - base_q, 2),
            "delta_value": round(new_nut.get(nut, 0) - base.get(nut, 0), 3),
            "driver_ingredient": best_ing,
        }
    return deviations


# ═══════════════════════════════════════════════════════════════════════════
# بدائل الحليب
# ═══════════════════════════════════════════════════════════════════════════

MILK_REPLACER_STANDARDS = {
    "عجول (Calves)": {"CP": 24, "Fat": 20, "Lactose": 45, "Ca": .85,
                       "P": .7, "Lys": 2.2, "Met": .65,
                       "notes": "NRC 2001 — عمر 1-6 أسابيع",
                       "source": "NRC Dairy Cattle",
                       "Ca_P_optimal": (1.2, 1.5)},
    "حملان (Lambs)": {"CP": 24, "Fat": 24, "Lactose": 40, "Ca": .9,
                       "P": .7, "Lys": 2.4, "Met": .7,
                       "notes": "≥24% دهن ضروري",
                       "source": "NRC Small Ruminants",
                       "Ca_P_optimal": (1.2, 1.6)},
    "جديان (Goat Kids)": {"CP": 24, "Fat": 24, "Lactose": 42, "Ca": .9,
                            "P": .7, "Lys": 2.3, "Met": .7,
                            "notes": "توازن خاص للجديان",
                            "source": "NRC Small Ruminants",
                            "Ca_P_optimal": (1.2, 1.6)},
    "إبل (Camels)": {"CP": 26, "Fat": 28, "Lactose": 38, "Ca": .95,
                       "P": .75, "Lys": 2.5, "Met": .8,
                       "notes": "بروتين ودهن أعلى",
                       "source": "FAO Camel Nutrition",
                       "Ca_P_optimal": (1.2, 1.5)},
    "أمهار (Foals)": {"CP": 22, "Fat": 18, "Lactose": 48, "Ca": 1.0,
                        "P": .8, "Lys": 2.1, "Met": .6,
                        "notes": "توازن خاص للخيل",
                        "source": "NRC Horses",
                        "Ca_P_optimal": (1.2, 1.4)},
    "جراء (Puppies)": {"CP": 28, "Fat": 22, "Lactose": 35, "Ca": 1.1,
                         "P": .9, "Lys": 2.2, "Met": .7,
                         "notes": "AAFCO compliant",
                         "source": "AAFCO 2020",
                         "Ca_P_optimal": (1.2, 1.3)},
}


MILK_REPLACER_INGREDIENTS = {
    "حليب مجفف منزوع الدسم": {"CP": 34, "Fat": 1, "Lactose": 52, "Ca": 1.3, "P": 1, "Lys": 2.7, "Met": .9, "price": 3200, "max": 60, "type": "بروتين"},
    "حليب مجفف كامل الدسم": {"CP": 26, "Fat": 28, "Lactose": 38, "Ca": .95, "P": .75, "Lys": 2.1, "Met": .65, "price": 3800, "max": 70, "type": "بروتين+دهن"},
    "شرش حليب مجفف": {"CP": 12, "Fat": 1.5, "Lactose": 75, "Ca": .9, "P": .75, "Lys": .9, "Met": .2, "price": 1800, "max": 35, "type": "كربوهيدرات"},
    "بروتين شرش WPC 80%": {"CP": 80, "Fat": 5, "Lactose": 8, "Ca": .5, "P": .3, "Lys": 7.5, "Met": 1.6, "price": 8500, "max": 25, "type": "بروتين"},
    "كازين": {"CP": 85, "Fat": 2, "Lactose": 2, "Ca": .1, "P": .5, "Lys": 7, "Met": 2.5, "price": 9000, "max": 20, "type": "بروتين"},
    "مركز بروتين صويا": {"CP": 66, "Fat": 1, "Lactose": 0, "Ca": .2, "P": .8, "Lys": 4.2, "Met": .9, "price": 2800, "max": 15, "type": "نباتي"},
    "دقيق الصويا": {"CP": 38, "Fat": 20, "Lactose": 0, "Ca": .2, "P": .6, "Lys": 2.4, "Met": .55, "price": 1500, "max": 10, "type": "نباتي"},
    "زيت جوز الهند": {"CP": 0, "Fat": 100, "Lactose": 0, "Ca": 0, "P": 0, "Lys": 0, "Met": 0, "price": 2200, "max": 15, "type": "دهن"},
    "زيت النخيل": {"CP": 0, "Fat": 100, "Lactose": 0, "Ca": 0, "P": 0, "Lys": 0, "Met": 0, "price": 1200, "max": 15, "type": "دهن"},
    "دهن حيواني": {"CP": 0, "Fat": 100, "Lactose": 0, "Ca": 0, "P": 0, "Lys": 0, "Met": 0, "price": 1000, "max": 15, "type": "دهن"},
    "مالتودكسترين": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0, "Lys": 0, "Met": 0, "price": 900, "max": 10, "type": "كربوهيدرات"},
    "لاكتوز نقي": {"CP": 0, "Fat": 0, "Lactose": 100, "Ca": 0, "P": 0, "Lys": 0, "Met": 0, "price": 1400, "max": 25, "type": "كربوهيدرات"},
    "ليسين L-Lysine": {"CP": 94, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0, "Lys": 94, "Met": 0, "price": 4200, "max": 1, "type": "أميني"},
    "ميثيونين": {"CP": 58, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0, "Lys": 0, "Met": 58, "price": 5800, "max": .8, "type": "أميني"},
    "بريمكس فيتامينات": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 5, "P": 3, "Lys": 0, "Met": 0, "price": 6500, "max": 1, "type": "بريمكس"},
    "كالسيوم كربونات": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 38, "P": 0, "Lys": 0, "Met": 0, "price": 200, "max": 2.5, "type": "معدن"},
    "فوسفات ثنائي الكالسيوم": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 23, "P": 18, "Lys": 0, "Met": 0, "price": 1100, "max": 2.5, "type": "معدن"},
    "ملح طعام": {"CP": 0, "Fat": 0, "Lactose": 0, "Ca": 0, "P": 0, "Lys": 0, "Met": 0, "price": 150, "max": .5, "type": "معدن"},
}


def formulate_milk_replacer(animal: str, volume: float = 100.0,
                              selected: Optional[List[str]] = None) -> Dict:
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

    base_bounds = [(0, MILK_REPLACER_INGREDIENTS[i].get("max", 100))
                   for i in valid]

    strategies = []
    s1_ub = [(lac, std["Lactose"] * 1.15 * 100),
             ([-x for x in lac], -std["Lactose"] * 0.85 * 100),
             ([-x for x in lys], -std["Lys"] * 0.70 * 100),
             ([-x for x in met], -std["Met"] * 0.70 * 100),
             ([-x for x in ca], -std["Ca"] * 0.85 * 100),
             ([-x for x in p], -std["P"] * 0.85 * 100)]
    strategies.append(("S1: صارم", [[1]*n, cp, fat],
                       [100, std["CP"]*100, std["Fat"]*100],
                       [u for u, _ in s1_ub], [b for _, b in s1_ub]))

    s2_ub = [(lac, std["Lactose"] * 1.30 * 100),
             ([-x for x in lac], -std["Lactose"] * 0.70 * 100),
             ([-x for x in lys], -std["Lys"] * 0.70 * 100),
             ([-x for x in met], -std["Met"] * 0.70 * 100),
             ([-x for x in ca], -std["Ca"] * 0.85 * 100),
             ([-x for x in p], -std["P"] * 0.85 * 100)]
    strategies.append(("S2: مرن", [[1]*n, cp, fat],
                       [100, std["CP"]*100, std["Fat"]*100],
                       [u for u, _ in s2_ub], [b for _, b in s2_ub]))

    s3_ub = s1_ub[:2] + s1_ub[4:]
    strategies.append(("S3: CP+Fat", [[1]*n, cp, fat],
                       [100, std["CP"]*100, std["Fat"]*100],
                       [u for u, _ in s3_ub], [b for _, b in s3_ub]))

    s4_ub = s1_ub[:2]
    strategies.append(("S4: CP+Fat", [[1]*n, cp, fat],
                       [100, std["CP"]*100, std["Fat"]*100],
                       [u for u, _ in s4_ub], [b for _, b in s4_ub]))

    s5_ub = [(cp, std["CP"] * 1.05 * 100),
             ([-x for x in cp], -std["CP"] * 0.95 * 100),
             (fat, std["Fat"] * 1.05 * 100),
             ([-x for x in fat], -std["Fat"] * 0.95 * 100)]
    strategies.append(("S5: CP/Fat ±5%", [[1]*n], [100],
                       [u for u, _ in s5_ub], [b for _, b in s5_ub]))

    s6_ub = [(cp, std["CP"] * 1.15 * 100),
             ([-x for x in cp], -std["CP"] * 0.85 * 100),
             (fat, std["Fat"] * 1.30 * 100),
             ([-x for x in fat], -std["Fat"] * 0.50 * 100)]
    strategies.append(("S6: طوارئ", [[1]*n], [100],
                       [u for u, _ in s6_ub], [b for _, b in s6_ub]))

    best = None
    best_eff = 0.0

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
            util_factor = (1.0 if used_pct >= min_util*100
                           else used_pct / (min_util*100))
            eff = quality * (0.7 + 0.3 * util_factor)
            if eff > best_eff:
                best_eff = eff
                best = {"formula": formula, "cost": res.fun / 100,
                        "cost_per_kg": res.fun / 10000,
                        "used_count": used, "used_pct": used_pct,
                        "actual": actual, "quality_score": quality,
                        "ca_p_ratio": ca_p, "strategy": label}
            if quality >= 90 and used_pct >= min_util * 100:
                break
        except Exception:
            continue

    if not best:
        return {"success": False, "message": "لا يوجد حل"}

    warning = None
    if best["used_pct"] < min_util * 100:
        warning = (f"⚠️ تم استخدام {best['used_count']}/{n}")

    return {"success": True, "formula": best["formula"],
            "cost_per_100kg": best["cost"],
            "cost_per_kg": best["cost_per_kg"],
            "standard": std, "actual": best["actual"],
            "animal": animal, "volume": volume,
            "used_count": best["used_count"],
            "used_pct": best["used_pct"],
            "quality_score": best["quality_score"],
            "ca_p_ratio": best["ca_p_ratio"],
            "strategy": best["strategy"],
            "warning": warning,
            "targets": {k: std.get(k, 0) for k in
                        ["CP", "Fat", "Lactose", "Ca", "P", "Lys", "Met"]}}


# ═══════════════════════════════════════════════════════════════════════════
# OCR (نفس 11.7 — مختصر للتوفير)
# ═══════════════════════════════════════════════════════════════════════════

def _preprocess_image_variants(img):
    variants = []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    variants.append(clahe.apply(gray))
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(otsu)
    variants.append(cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 15, 5))
    variants.append(cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                            cv2.THRESH_BINARY, 15, 5))
    variants.append(cv2.fastNlMeansDenoising(clahe.apply(gray), None, 10, 7, 21))
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    variants.append(cv2.filter2D(gray, -1, kernel))
    variants.append(cv2.bitwise_not(gray))
    variants.append(cv2.morphologyEx(gray, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8)))
    return variants


def _deskew_image(img):
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
    try:
        data = pytesseract.image_to_data(image, lang='ara+eng',
                                           output_type=pytesseract.Output.DICT,
                                           config=r'--oem 3 --psm 6')
        good_lines, current_line, current_y = [], [], None
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
                current_line, current_y = [word], y
            else:
                current_line.append(word)
        if current_line:
            good_lines.append(' '.join(current_line))
        return '\n'.join(good_lines), len(good_lines)
    except Exception:
        return "", 0


def _parse_ingredients_from_text(full_text):
    fixes = {'٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
             '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4', '٪': '%'}
    text = full_text
    for old, new in fixes.items():
        text = text.replace(old, new)
    patterns = [
        r'([\u0600-\u06FFa-zA-Z\s\(\)\-]{3,40}?)[\s:\-=:\.]+\s*(\d{1,3}\.?\d{0,2})\s*%',
        r'(\d{1,3}\.?\d{0,2})\s*%[\s:\-=:\.]+\s*([\u0600-\u06FFa-zA-Z\s\(\)\-]{3,40})',
    ]
    ingredients = {}
    for line in text.split('\n'):
        line = line.strip()
        if len(line) < 4:
            continue
        for pat in patterns:
            for m in re.finditer(pat, line):
                g = m.groups()
                if len(g) < 2:
                    continue
                try:
                    try:
                        val, name = float(g[1]), g[0].strip()
                    except ValueError:
                        val, name = float(g[0]), g[1].strip()
                    if 0.1 <= val <= 100 and len(name) > 2:
                        matched = match_ingredient_name(name)
                        if matched and matched not in ingredients:
                            ingredients[matched] = round(val, 2)
                except Exception:
                    continue
    return ingredients


def match_ingredient_name(text):
    if not text:
        return None
    tl = text.strip().lower()
    for cat in BIG_FEEDS_LIBRARY.values():
        for name in cat.keys():
            if name.lower() in tl or tl in name.lower():
                return name
    kw = {"ذرة": "ذرة صفراء", "صويا": "كسب فول صويا 44%",
          "شعير": "شعير مطحون", "قمح": "قمح محلي",
          "نخالة": "نخالة قمح (ردة)", "ملح": "ملح الطعام",
          "حجر": "الحجر الجيري"}
    for k, v in kw.items():
        if k in tl:
            return v
    return None


def extract_ingredients_from_image(image_bytes):
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
        img = _deskew_image(img)
        variants = _preprocess_image_variants(img)
        all_texts = []
        for variant in variants:
            try:
                txt, score = _extract_with_confidence(variant)
                if txt and len(txt) > 5:
                    all_texts.append(txt)
            except Exception:
                continue
        if not all_texts:
            return {"success": False, "message": "لم يتم استخراج نص"}
        full_text = "\n".join(set(all_texts))
        ingredients = _parse_ingredients_from_text(full_text)
        return {"success": True, "ingredients": ingredients,
                "raw_text": full_text, "count": len(ingredients)}
    except Exception as e:
        return {"success": False, "message": f"خطأ: {e}"}


def render_ocr_correction_ui(ingredients):
    st.markdown("### ✏️ تصحيح يدوي")
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
                new_pct = st.number_input("النسبة %", 0.0, 100.0, float(pct),
                                            0.5, key=f"ocr_fix_pct_{i}")
            with cc:
                keep = st.checkbox("احتفظ", value=True, key=f"ocr_keep_{i}")
            if keep and new_pct > 0:
                corrected[new_name] = new_pct
    return corrected


# ═══════════════════════════════════════════════════════════════════════════
# الرسوم البيانية (12 دالة)
# ═══════════════════════════════════════════════════════════════════════════

def create_colorful_bar_chart(standard, actual, keys=None):
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
                     label='المعيار', color='#1976d2', edgecolor='#0d47a1', linewidth=1.5)
        b2 = ax.bar(x + width/2, [actual.get(n, 0) for n in nuts], width,
                     label='المحسوب', color='#43a047', edgecolor='#1b5e20', linewidth=1.5)
        for bar in b1:
            hh = bar.get_height()
            if hh > 0:
                ax.text(bar.get_x() + bar.get_width()/2, hh, f'{hh:.1f}',
                        ha='center', va='bottom', fontsize=9, color='#0d47a1', fontweight='bold')
        for bar in b2:
            hh = bar.get_height()
            if hh > 0:
                ax.text(bar.get_x() + bar.get_width()/2, hh, f'{hh:.1f}',
                        ha='center', va='bottom', fontsize=9, color='#1b5e20', fontweight='bold')
        ax.set_title('مقارنة العناصر', fontsize=13, fontweight='bold', color='#1b5e20')
        ax.set_xticks(x)
        ax.set_xticklabels(nuts, fontsize=10)
        ax.legend(loc='upper right', fontsize=10)
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
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2:
        return None
    try:
        colors = ['#e53935', '#8e24aa', '#3949ab', '#1e88e5', '#00897b',
                  '#43a047', '#7cb342', '#fdd835', '#fb8c00', '#6d4c41']
        names = list(formula.keys())
        vals = list(formula.values())
        fig, ax = plt.subplots(figsize=(8, 5))
        _, _, autotexts = ax.pie(vals, autopct='%1.1f%%', colors=colors[:len(names)],
                                   startangle=90, pctdistance=0.75,
                                   wedgeprops=dict(edgecolor='white', linewidth=2))
        for t in autotexts:
            t.set_color('white')
            t.set_fontweight('bold')
            t.set_fontsize(9)
        ax.legend(names, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)
        ax.set_title('توزيع المكونات', fontsize=13, fontweight='bold', color='#1b5e20')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_radar_chart(standard, actual, keys=None):
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
        ax.plot(angles, std_norm, 'o-', linewidth=2.5, color='#1976d2', label='المعيار')
        ax.fill(angles, std_norm, alpha=0.15, color='#1976d2')
        ax.plot(angles, act_norm, 'o-', linewidth=2.5, color='#43a047', label='المحسوب')
        ax.fill(angles, act_norm, alpha=0.25, color='#43a047')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(nuts, fontsize=10)
        ax.set_ylim(0, max(max(std_norm), max(act_norm)) * 1.2)
        ax.set_title('المقارنة %', fontsize=12, fontweight='bold', color='#1b5e20', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
        ax.grid(True, alpha=0.3)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_gauge_chart(score):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect='equal'))
        colors = ['#c62828', '#ef6c00', '#f9a825', '#7cb342', '#43a047', '#1b5e20']
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
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_horizontal_bar_chart(formula):
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2:
        return None
    try:
        sorted_pairs = sorted(formula.items(), key=lambda x: x[1], reverse=True)
        names = [p[0] for p in sorted_pairs]
        vals = [p[1] for p in sorted_pairs]
        colors = ['#e53935', '#8e24aa', '#3949ab', '#1e88e5', '#00897b',
                  '#43a047', '#7cb342', '#fdd835', '#fb8c00', '#6d4c41']
        fig, ax = plt.subplots(figsize=(9, max(4, len(names) * 0.4)))
        bars = ax.barh(names, vals, color=colors[:len(names)], edgecolor='#333')
        for bar in bars:
            hh = bar.get_width()
            ax.text(hh + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{hh:.1f}%', ha='left', va='center', fontsize=9, fontweight='bold')
        ax.set_title('توزيع المكونات', fontsize=13, fontweight='bold', color='#1b5e20')
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.invert_yaxis()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_nutrient_breakdown_pie(actual):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        pc = actual.get("CP", 0) * 4
        fc = actual.get("EE", 0) * 9
        fibc = (actual.get("NDF", 0) + actual.get("ADF", 0)) * 2
        oc = max(0, 100 - pc - fc - fibc)
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.pie([pc, fc, fibc, oc], labels=['بروتين', 'دهن', 'ألياف', 'كربوهيدرات'],
                autopct='%1.1f%%', colors=['#1976d2', '#f9a825', '#43a047', '#8e24aa'],
                startangle=90, wedgeprops=dict(edgecolor='white', linewidth=2))
        ax.set_title('مصادر الطاقة', fontsize=13, fontweight='bold', color='#1b5e20')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_oil_comparison_chart(total_oil, oil_std):
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
        ax.set_title(f'الزيوت — {oil_std.get("source", "NRC")}',
                     fontsize=13, fontweight='bold', color='#1b5e20')
        ax.grid(axis='y', alpha=0.3)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_quality_breakdown_chart(rows):
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
        bars = ax.bar(labels, scores, color=colors, edgecolor='#333', linewidth=1.5)
        for bar in bars:
            hh = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, hh, f'{hh:.0f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax.axhline(y=70, color='#c62828', linestyle='--', linewidth=2, label='حد 70%')
        ax.set_ylim(0, 105)
        ax.set_title('تقييم العناصر', fontsize=13, fontweight='bold', color='#1b5e20')
        ax.legend(loc='lower right')
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=30, ha='right')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_ca_p_ratio_chart(ca, p, target_ca=0, target_p=0):
    if not MATPLOTLIB_AVAILABLE or p <= 0:
        return None
    try:
        ratio = ca / p
        fig, ax = plt.subplots(figsize=(8, 3))
        zones = [(0, .8, '#b71c1c'), (.8, 1.2, '#ef6c00'),
                 (1.2, 1.5, '#f9a825'), (1.5, 2.0, '#2e7d32'),
                 (2.0, 3.0, '#f9a825'), (3.0, 5.0, '#ef6c00'),
                 (5.0, 8.0, '#b71c1c')]
        for x0, x1, c in zones:
            ax.axvspan(x0, x1, alpha=0.35, color=c, edgecolor='white', linewidth=0)
        ratio_clipped = min(ratio, 7.9)
        ax.axvline(ratio_clipped, color='#0d47a1', linewidth=4, zorder=10)
        ax.scatter([ratio_clipped], [0.5], s=350, color='#0d47a1', zorder=11,
                    edgecolors='white', linewidth=3)
        ax.text(ratio_clipped, 0.85, f'{ratio:.2f}', ha='center', va='bottom',
                fontsize=18, fontweight='bold', color='#0d47a1',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                          edgecolor='#0d47a1', linewidth=2))
        ax.set_xlim(0, 8)
        ax.set_ylim(0, 1.2)
        ax.set_yticks([])
        ax.set_xticks(range(9))
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
        ax.text(0.02, 0.05, label, transform=ax.transAxes, fontsize=13,
                fontweight='bold', color=color,
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                          edgecolor=color, linewidth=2))
        ax.grid(axis='x', alpha=0.2)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def create_nlp_profit_curve(result, ingredient_names, ingredient_data, prices):
    if not PLOTLY_AVAILABLE:
        return None
    try:
        se_vals = np.array([ingredient_data[i].get("SE", 0) for i in ingredient_names])
        me_vals = se_vals * 41.0
        cp_vals = np.array([ingredient_data[i].get("CP", 0) for i in ingredient_names])
        cost_vals = np.array([prices.get(i, 300.0) / 1000.0 for i in ingredient_names])
        x_opt = np.array(result["x_opt"])
        prices_range = np.linspace(1.0, 5.0, 40)
        profits = []
        for p in prices_range:
            qv = (np.dot(me_vals, x_opt) / 3000.0) * (np.dot(cp_vals, x_opt) / 20.0)
            profits.append(p * qv - np.dot(cost_vals, x_opt))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=prices_range, y=profits,
                                  mode='lines+markers',
                                  line=dict(color='#1b5e20', width=3),
                                  marker=dict(size=5, color='#2e7d32'),
                                  name='صافي العائد'))
        fig.add_hline(y=0, line_dash="dash", line_color="#c62828",
                       annotation_text="التعادل")
        fig.update_layout(title="منحنى الربحية",
                           xaxis_title="سعر المنتج ($/وحدة)",
                           yaxis_title="صافي العائد ($/كجم)",
                           height=420, paper_bgcolor='white',
                           plot_bgcolor='#fafafa')
        return fig
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# PDF Generator (مختصر — النسخة الكاملة من 11.7 محفوظة)
# ═══════════════════════════════════════════════════════════════════════════

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
            return get_display(arabic_reshaper.reshape(str(t)), base_dir='R')
        except Exception:
            return str(t)

    def _draw_stamp(self, canvas_obj, doc):
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
            canvas_obj.setFillColor(HexColor('#c62828'))
            canvas_obj.setFont(self.font_name, 9.5)
            canvas_obj.drawCentredString(sx, sy + 42, self._ar("تاور نولجي"))
            canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(sx, sy + 16, self._ar("د. عبدالقادر"))
            canvas_obj.drawCentredString(sx, sy + 4, self._ar("إسماعيل تاور"))
        except Exception:
            pass

    def _draw_page(self, canvas_obj, doc):
        try:
            canvas_obj.saveState()
            w, h = doc.pagesize
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, h - 90, w, 90, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.rect(0, h - 95, w, 5, fill=1, stroke=0)
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 22)
            canvas_obj.drawCentredString(w/2, h - 38, self._ar("تاور نولجي  Tawor Nology"))
            canvas_obj.setFont(self.font_name, 12)
            canvas_obj.setFillColor(HexColor('#e8f5e9'))
            canvas_obj.drawCentredString(w/2, h - 58, self._ar("للإنتاج الحيواني وتغذية الحيوان"))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.drawCentredString(w/2, h - 76, self._ar(f"إشراف: {SUPERVISOR}"))
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, 42, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#ffeb3b'))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.drawCentredString(w/2, 68, self._ar(f"🤲 {DUA_SHORT} 🤲"))
            canvas_obj.setFillColor(HexColor('#c8e6c9'))
            canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(w/2, 52, self._ar("اللهم اجعل قبرهما روضة من رياض الجنة"))
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(w/2, 27, self._ar("تاور نولجي Tawor Nology © 2026"))
            self._draw_stamp(canvas_obj, doc)
            canvas_obj.restoreState()
        except Exception:
            pass

    def generate_report(self, formula, requirement, animal_type, breed, cost,
                         city, local_cost, local_sym, requester_name="",
                         protein_basis="DP", standard_key="",
                         include_charts=True, quality_score=0.0):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40,
                                topMargin=115, bottomMargin=145)
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

        client = [[self._ar("👤 طالب الخدمة:"), self._ar(requester_name or "—")],
                  [self._ar("📍 الموقع:"), self._ar(city)],
                  [self._ar("🐾 الفصيل:"), self._ar(f"{animal_type} — {breed}")],
                  [self._ar("🧬 الأساس:"), self._ar(protein_basis)],
                  [self._ar("📅 التاريخ:"), datetime.now().strftime('%Y-%m-%d')]]
        ct = Table(client, colWidths=[150, 340])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')),
            ('INNERGRID', (0, 0), (-1, -1), 0.6, HexColor('#c8e6c9')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 8)]))
        story.append(ct)
        story.append(Spacer(1, 15))

        std_vals = requirement_to_standard(requirement)
        calc_vals = compute_formula_nutrients(formula)
        qd = [[self._ar("الجودة"), self._ar("الحالة"), self._ar("70%")],
              [f"{quality_score:.1f}%",
               self._ar("✅ ناجح" if quality_score >= 70 else "⚠️ يحتاج تحسين"),
               self._ar("✅" if quality_score >= 70 else "❌")]]
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
            ('PADDING', (0, 0), (-1, -1), 8)]))
        story.append(qt)
        story.append(Spacer(1, 15))

        # مقارنة
        labels = {"CP": "بروتين CP", "DP": "مهضوم DP", "SE": "SE",
                  "NDF": "NDF", "ADF": "ADF", "EE": "دهن", "ASH": "رماد",
                  "Ca": "Ca", "P": "P"}
        data = [[self._ar(x) for x in ["العنصر", "المعيار", "المحسوب", "الفرق", "%", "التقييم"]]]
        cmds = [('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#9e9e9e'))]
        row = 1
        for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
            if k not in std_vals or std_vals[k] == 0:
                continue
            sv, cv = std_vals[k], calc_vals.get(k, 0)
            diff = cv - sv
            pct = (diff / sv * 100) if sv else 0
            ev = evaluate_difference(pct, standard_value=sv)
            data.append([self._ar(labels[k]), f"{sv:.2f}", f"{cv:.2f}",
                          f"{diff:+.3f}", f"{pct:+.2f}%", self._ar(ev["label"])])
            cmds.append(('BACKGROUND', (0, row), (-1, row), HexColor(ev["bg"])))
            row += 1
        t = Table(data, colWidths=[100, 70, 70, 70, 70, 105])
        t.setStyle(TableStyle(cmds))
        story.append(t)

        # مكونات
        story.append(PageBreak())
        story.append(P("🌾 المكونات للطن", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        ing_data = [[self._ar("المكون"), self._ar("%"), self._ar("كجم/طن")]]
        for ing, pct in formula.items():
            ing_data.append([self._ar(ing), f"{pct:.2f}%", f"{pct * 10:.1f}"])
        ti = Table(ing_data, colWidths=[270, 110, 110])
        ti.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd'))]))
        story.append(ti)

        doc.build(story, onFirstPage=self._draw_page,
                  onLaterPages=self._draw_page)
        buffer.seek(0)
        return buffer.getvalue()


pdf_gen = PDFGenerator()


# ═══════════════════════════════════════════════════════════════════════════
# 🆕 v11.8 — دالة PDF المالية العربية
# ═══════════════════════════════════════════════════════════════════════════

def _generate_financial_pdf_arabic(total_investment, total_operating_costs,
                                     net_annual_profit, roi, payback_period,
                                     total_npv, cf_df):
    """تقرير مالي — بنفس بنية PDF الرئيسي."""
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40, leftMargin=40,
                                topMargin=115, bottomMargin=145)
        story = []

        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(ar(text), ParagraphStyle(
                's', fontName=font_mgr.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))

        story.append(P("تقرير الجدوى المالي الرسمي", size=20,
                       align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
                                color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))
        story.append(P(f"📅 {datetime.now():%Y-%m-%d %H:%M}",
                       size=10, align=TA_CENTER, color='#555'))
        story.append(Spacer(1, 12))

        summary = [[ar("المؤشر المالي"), ar("القيمة")],
                   [ar("الاستثمار الكلي"), f"${total_investment:,.2f}"],
                   [ar("التكاليف التشغيلية السنوية"), f"${total_operating_costs:,.2f}"],
                   [ar("الربح السنوي الصافي"), f"${net_annual_profit:,.2f}"],
                   [ar("عائد الاستثمار (ROI)"), f"{roi:.2f}%"],
                   [ar("فترة الاسترداد"), f"{payback_period:.2f} سنة"],
                   [ar("NPV (5 سنوات)"), f"${total_npv:,.2f}"]]
        ts = Table(summary, colWidths=[220, 240])
        ts.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f9f9f9')]),
            ('PADDING', (0, 0), (-1, -1), 8)]))
        story.append(ts)
        story.append(Spacer(1, 15))

        story.append(P("📊 التدفقات النقدية (5 سنوات)", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        cf_data = [[ar(x) for x in ["السنة", "الإيرادات", "التشغيل",
                                     "CF الصافي", "المخصوم"]]]
        for _, row in cf_df.iterrows():
            cf_data.append([ar(str(row["السنة"])),
                            f"${row['الإيرادات ($)']:,.2f}",
                            f"${row['التشغيل ($)']:,.2f}",
                            f"${row['CF الصافي ($)']:,.2f}",
                            f"${row['القيمة المخصومة ($)']:,.2f}"])
        t_cf = Table(cf_data, colWidths=[70, 105, 105, 95, 95])
        t_cf.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2ca02c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#bdbdbd'))]))
        story.append(t_cf)
        story.append(Spacer(1, 20))

        story.append(P(SUPERVISOR, size=16, align=TA_CENTER, color='#c62828'))
        story.append(P(SUPERVISOR_TITLE, size=11, align=TA_CENTER, color='#1b5e20'))

        doc.build(story, onFirstPage=pdf_gen._draw_page,
                  onLaterPages=pdf_gen._draw_page)
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return None


def generate_milk_replacer_pdf(result):
    """PDF بدائل الحليب — مبسّط."""
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40, leftMargin=40,
                                topMargin=115, bottomMargin=145)
        story = []
        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(ar(text), ParagraphStyle(
                's', fontName=font_mgr.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size * 1.6))
        std = result["standard"]
        story.append(P("تقرير تركيبة بديل الحليب", size=20,
                       align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
                                color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))
        info = [[ar("الحيوان:"), ar(result["animal"])],
                [ar("المرجع:"), ar(std.get("source", ""))],
                [ar("الجودة:"), f"{result['quality_score']:.1f}%"],
                [ar("Ca:P:"), f"{result['ca_p_ratio']:.2f}"]]
        ct = Table(info, colWidths=[160, 330])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e3f2fd')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#1565c0')),
            ('INNERGRID', (0, 0), (-1, -1), 0.6, HexColor('#bbdefb')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 7)]))
        story.append(ct)
        story.append(Spacer(1, 15))

        ing_data = [[ar("المكون"), ar("%"), ar("كجم")]]
        for ing, pct in result["formula"].items():
            kg = pct * result.get("volume", 100) / 100
            ing_data.append([ar(ing), f"{pct:.2f}%", f"{kg:.2f}"])
        ti = Table(ing_data, colWidths=[200, 100, 100])
        ti.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#bdbdbd'))]))
        story.append(ti)

        doc.build(story, onFirstPage=pdf_gen._draw_page,
                  onLaterPages=pdf_gen._draw_page)
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return None


def generate_letterhead_pdf(title_line, sub_line):
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=50, leftMargin=50,
                                topMargin=115, bottomMargin=145)
        story = []
        story.append(Spacer(1, 80))
        story.append(Paragraph(ar(title_line), ParagraphStyle(
            't', fontName=font_mgr.font_name, fontSize=32,
            alignment=TA_CENTER, textColor=HexColor('#1b5e20'), leading=42)))
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
        doc.build(story, onFirstPage=pdf_gen._draw_page,
                  onLaterPages=pdf_gen._draw_page)
        return buf.getvalue()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# التصدير + الثوابت
# ═══════════════════════════════════════════════════════════════════════════

def export_comparison_to_excel(standard, calculated, requester_name="",
                                 animal="", stage="", formula=None, standard_key=""):
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
    labels = {"CP": "بروتين", "DP": "مهضوم", "SE": "SE", "NDF": "NDF",
              "ADF": "ADF", "EE": "دهن", "ASH": "رماد", "Ca": "Ca", "P": "P"}
    row = 5
    for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
        if k not in standard or standard[k] == 0:
            continue
        sv, cv = standard[k], calculated.get(k, 0)
        diff = cv - sv
        pct = (diff / sv * 100) if sv else 0
        ev = evaluate_difference(pct, standard_value=sv)
        vals = [labels[k], round(sv, 2), round(cv, 2), round(diff, 3),
                round(pct, 2), ev["label"]]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.alignment = ct
            cell.border = bd
            cell.fill = PatternFill('solid', fgColor=ev["bg"].replace('#', ''))
        row += 1
    for c in range(1, 7):
        ws.column_dimensions[get_column_letter(c)].width = 22
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


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
    "دواجن_لاحم": {"name_ar": "دواجن لاحم", "area_per_head": 0.10,
                    "feeder_cm_per_head": 5.0, "drinker_cm_per_head": 2.5,
                    "height_m": 2.8, "width_m": 12.0,
                    "ach_summer": 60, "ach_winter": 8, "vent_open_ratio": 0.20,
                    "roof_type": "gable", "slope_pct": 20.0,
                    "feeder_type": "خطية", "drinker_type": "حلمات",
                    "aisle_m": 1.2, "central_aisle": True,
                    "temp_optimal_c": 24, "humidity_optimal": 60},
    "دواجن_بياض": {"name_ar": "دواجن بياض", "area_per_head": 0.15,
                    "feeder_cm_per_head": 10.0, "drinker_cm_per_head": 2.5,
                    "height_m": 3.0, "width_m": 12.0,
                    "ach_summer": 40, "ach_winter": 6, "vent_open_ratio": 0.20,
                    "roof_type": "gable", "slope_pct": 20.0,
                    "feeder_type": "سلسلة", "drinker_type": "حلمات",
                    "aisle_m": 1.2, "central_aisle": True,
                    "temp_optimal_c": 22, "humidity_optimal": 60},
    "سمان": {"name_ar": "سمان", "area_per_head": 0.025,
             "feeder_cm_per_head": 2.0, "drinker_cm_per_head": 1.0,
             "height_m": 2.0, "width_m": 6.0,
             "ach_summer": 50, "ach_winter": 8, "vent_open_ratio": 0.25,
             "roof_type": "mono", "slope_pct": 15.0,
             "feeder_type": "خطية", "drinker_type": "حلمات",
             "aisle_m": 0.8, "central_aisle": False,
             "temp_optimal_c": 26, "humidity_optimal": 65},
    "أغنام": {"name_ar": "أغنام", "area_per_head": 1.5,
              "feeder_cm_per_head": 35.0, "drinker_cm_per_head": 4.0,
              "height_m": 3.5, "width_m": 10.0,
              "ach_summer": 30, "ach_winter": 5, "vent_open_ratio": 0.30,
              "roof_type": "gable", "slope_pct": 25.0,
              "feeder_type": "خرسانية", "drinker_type": "حوض",
              "aisle_m": 2.0, "central_aisle": True,
              "temp_optimal_c": 18, "humidity_optimal": 65},
    "ماعز": {"name_ar": "ماعز", "area_per_head": 1.5,
             "feeder_cm_per_head": 35.0, "drinker_cm_per_head": 4.0,
             "height_m": 3.5, "width_m": 10.0,
             "ach_summer": 30, "ach_winter": 5, "vent_open_ratio": 0.30,
             "roof_type": "gable", "slope_pct": 25.0,
             "feeder_type": "مرتفعة", "drinker_type": "حوض",
             "aisle_m": 2.0, "central_aisle": True,
             "temp_optimal_c": 20, "humidity_optimal": 65},
    "أبقار": {"name_ar": "أبقار", "area_per_head": 5.0,
              "feeder_cm_per_head": 70.0, "drinker_cm_per_head": 6.0,
              "height_m": 4.5, "width_m": 15.0,
              "ach_summer": 25, "ach_winter": 4, "vent_open_ratio": 0.35,
              "roof_type": "gable", "slope_pct": 20.0,
              "feeder_type": "وسطية", "drinker_type": "حوض",
              "aisle_m": 3.5, "central_aisle": True,
              "temp_optimal_c": 15, "humidity_optimal": 65},
    "إبل": {"name_ar": "إبل", "area_per_head": 10.0,
            "feeder_cm_per_head": 100.0, "drinker_cm_per_head": 8.0,
            "height_m": 4.5, "width_m": 15.0,
            "ach_summer": 20, "ach_winter": 4, "vent_open_ratio": 0.40,
            "roof_type": "gable", "slope_pct": 20.0,
            "feeder_type": "مرتفعة", "drinker_type": "حوض كبير",
            "aisle_m": 4.0, "central_aisle": True,
            "temp_optimal_c": 25, "humidity_optimal": 50},
    "خيول": {"name_ar": "خيول", "area_per_head": 16.0,
             "feeder_cm_per_head": 100.0, "drinker_cm_per_head": 10.0,
             "height_m": 4.0, "width_m": 15.0,
             "ach_summer": 25, "ach_winter": 5, "vent_open_ratio": 0.30,
             "roof_type": "gable", "slope_pct": 25.0,
             "feeder_type": "مرتفعة", "drinker_type": "حوض",
             "aisle_m": 3.5, "central_aisle": True,
             "temp_optimal_c": 18, "humidity_optimal": 60},
    "أرانب": {"name_ar": "أرانب", "area_per_head": 0.30,
              "feeder_cm_per_head": 8.0, "drinker_cm_per_head": 2.0,
              "height_m": 2.5, "width_m": 8.0,
              "ach_summer": 40, "ach_winter": 6, "vent_open_ratio": 0.25,
              "roof_type": "gable", "slope_pct": 20.0,
              "feeder_type": "معدنية", "drinker_type": "نبل",
              "aisle_m": 1.2, "central_aisle": True,
              "temp_optimal_c": 20, "humidity_optimal": 65},
    "أسماك_أحواض": {"name_ar": "أسماك", "area_per_head": 1.5,
                     "feeder_cm_per_head": 0.0, "drinker_cm_per_head": 0.0,
                     "height_m": 1.5, "width_m": 20.0,
                     "ach_summer": 0, "ach_winter": 0, "vent_open_ratio": 0.0,
                     "roof_type": "none", "slope_pct": 0.0,
                     "feeder_type": "نثر", "drinker_type": "—",
                     "aisle_m": 2.0, "central_aisle": False,
                     "temp_optimal_c": 28, "humidity_optimal": 0},
}


def calculate_barn_dimensions(key, count):
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
    apr = max(2, int(length / (0.3 if key in ["دواجن_لاحم", "دواجن_بياض", "سمان"]
                             else 1.5)))
    return {"standard": std, "count": count,
            "total_area_m2": round(area, 2),
            "length_m": round(length, 2),
            "width_m": round(width, 2),
            "height_m": std["height_m"],
            "ridge_height_m": round(ridge, 2),
            "roof_type": std["roof_type"],
            "slope_pct": std["slope_pct"],
            "feeders_count": feeders, "drinkers_count": drinkers,
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
            "humidity_optimal": std.get("humidity_optimal", 60)}


def create_barn_3d_figure(dims):
    if not PLOTLY_AVAILABLE:
        return None
    try:
        std = dims["standard"]
        L = max(float(dims["length_m"]), 1.0)
        W = max(float(dims["width_m"]), 1.0)
        H = max(float(dims["height_m"]), 1.0)
        RH = max(float(dims["ridge_height_m"]), 1.0)
        fig = go.Figure()
        fig.add_trace(go.Mesh3d(
            x=[0, L, L, 0], y=[0, 0, W, W], z=[0, 0, 0, 0],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color='#d7ccc8', opacity=0.7, name='الأرضية', hoverinfo='skip'))
        for xp in [0, L]:
            fig.add_trace(go.Mesh3d(
                x=[xp]*4, y=[0, W, W, 0], z=[0, 0, H, H],
                i=[0, 0], j=[1, 2], k=[2, 3],
                color='#a1887f', opacity=0.3, showlegend=False, hoverinfo='skip'))
        for yp in [0, W]:
            fig.add_trace(go.Mesh3d(
                x=[0, L, L, 0], y=[yp]*4, z=[0, 0, H, H],
                i=[0, 0], j=[1, 2], k=[2, 3],
                color='#a1887f', opacity=0.3, showlegend=False, hoverinfo='skip'))
        if dims["roof_type"] == "gable":
            fig.add_trace(go.Mesh3d(
                x=[0, L, L, 0], y=[0, 0, W/2, W/2], z=[H, H, RH, RH],
                i=[0, 0], j=[1, 2], k=[2, 3],
                color='#8d6e63', opacity=0.55, name='السقف', hoverinfo='skip'))
            fig.add_trace(go.Mesh3d(
                x=[0, L, L, 0], y=[W/2, W/2, W, W], z=[RH, RH, H, H],
                i=[0, 0], j=[1, 2], k=[2, 3],
                color='#8d6e63', opacity=0.55, showlegend=False, hoverinfo='skip'))
        fig.update_layout(
            title=dict(text=f"🏗️ {std['name_ar']} — {dims['count']} رأس | {dims['total_area_m2']} م²",
                        font=dict(size=14, color='#1b5e20'), x=0.5),
            scene=dict(xaxis_title='الطول', yaxis_title='العرض', zaxis_title='الارتفاع',
                        backgroundcolor='#f5f5f5'),
            height=600, margin=dict(l=0, r=0, t=90, b=0), paper_bgcolor='white')
        return fig
    except Exception:
        return None


def render_barn_to_pdf_image(dims):
    if not MATPLOTLIB_AVAILABLE:
        return None
    try:
        std = dims["standard"]
        L, W, H, RH = (dims["length_m"], dims["width_m"],
                        dims["height_m"], dims["ridge_height_m"])
        fig = plt.figure(figsize=(11, 7.5))
        ax = fig.add_subplot(111, projection='3d')
        floor = [[(0, 0, 0), (L, 0, 0), (L, W, 0), (0, W, 0)]]
        ax.add_collection3d(Poly3DCollection(floor, facecolors='#d7ccc8',
                                              edgecolors='#5d4037', alpha=0.75))
        ax.set_xlim(0, L)
        ax.set_ylim(0, W)
        ax.set_zlim(0, RH + 0.5)
        ax.set_box_aspect((L, W, RH + 0.5))
        ax.set_title(f"{std['name_ar']} — {dims['count']} رأس",
                     fontsize=13, color='#1b5e20', fontweight='bold')
        ax.view_init(elev=22, azim=-55)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=140, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    except Exception:
        return None


def generate_barn_pdf_report(dims):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40,
                            topMargin=115, bottomMargin=145)
    story = []
    def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
        return Paragraph(ar(text), ParagraphStyle(
            's', fontName=font_mgr.font_name, fontSize=size,
            alignment=align, textColor=HexColor(color),
            spaceAfter=6, leading=size * 1.6))
    std = dims["standard"]
    story.append(P("تقرير حظيرة — تاور نولجي", size=20, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
    story.append(Spacer(1, 12))
    info = [[ar("الحيوان"), ar(std["name_ar"])],
            [ar("العدد"), ar(str(dims["count"]))],
            [ar("المساحة"), ar(f"{dims['total_area_m2']} م²")],
            [ar("الأبعاد"), ar(f"{dims['length_m']}×{dims['width_m']}×{dims['ridge_height_m']} م")]]
    t = Table(info, colWidths=[150, 340])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
        ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 11)]))
    story.append(t)
    img = render_barn_to_pdf_image(dims)
    if img:
        try:
            story.append(RLImage(img, width=480, height=340))
        except Exception:
            pass
    doc.build(story, onFirstPage=pdf_gen._draw_page,
              onLaterPages=pdf_gen._draw_page)
    buffer.seek(0)
    return buffer.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# الجدوى الفنية
# ═══════════════════════════════════════════════════════════════════════════

TECHNICAL_FEASIBILITY_DATA = {
    "دواجن_لاحم": {"feed_per_day_g": 120, "water_per_day_ml": 220,
                    "labor_per_1000": 0.3, "cycle_days": 42,
                    "final_weight_kg": 2.3, "fcr": 1.65, "production_type": "meat"},
    "دواجن_بياض": {"feed_per_day_g": 110, "water_per_day_ml": 250,
                    "labor_per_1000": 0.3, "eggs_per_year": 310,
                    "egg_weight_g": 60, "production_type": "eggs"},
    "سمان": {"feed_per_day_g": 28, "water_per_day_ml": 55,
             "labor_per_1000": 0.5, "cycle_days": 42,
             "final_weight_kg": 0.25, "fcr": 2.5, "production_type": "meat"},
    "أغنام": {"feed_per_day_g": 1800, "water_per_day_ml": 6000,
              "labor_per_1000": 1.5, "milk_per_day_L": 1.5,
              "lactation_days": 200, "production_type": "mixed"},
    "ماعز": {"feed_per_day_g": 1500, "water_per_day_ml": 6000,
             "labor_per_1000": 1.5, "milk_per_day_L": 2.5,
             "lactation_days": 280, "production_type": "milk"},
    "أبقار": {"feed_per_day_g": 20000, "water_per_day_ml": 80000,
              "labor_per_1000": 5.0, "milk_per_day_L": 20,
              "lactation_days": 305, "production_type": "milk"},
    "إبل": {"feed_per_day_g": 8000, "water_per_day_ml": 50000,
            "labor_per_1000": 3.0, "milk_per_day_L": 5,
            "lactation_days": 300, "production_type": "milk"},
    "خيول": {"feed_per_day_g": 10000, "water_per_day_ml": 40000,
             "labor_per_1000": 4.0, "production_type": "service"},
    "أرانب": {"feed_per_day_g": 180, "water_per_day_ml": 350,
              "labor_per_1000": 1.0, "cycle_days": 70,
              "final_weight_kg": 2.5, "fcr": 3.5, "production_type": "meat"},
    "أسماك_أحواض": {"feed_per_day_g": 30, "water_per_day_ml": 0,
                     "labor_per_1000": 0.5, "cycle_days": 240,
                     "final_weight_kg": 0.5, "fcr": 1.8, "production_type": "meat"},
}


def calculate_technical_feasibility(key, count):
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
        production = {"unit": "بيضة/سنة", "annual": eggs_year,
                       "per_day": eggs_year / 365}
    elif ptype == "milk":
        m_day = count * tech.get("milk_per_day_L", 20)
        production = {"unit": "لتر/سنة",
                       "annual": m_day * tech.get("lactation_days", 305),
                       "per_day": m_day}
    elif ptype == "meat":
        cyc = tech.get("cycle_days", 42)
        cyc_y = 365 / cyc
        production = {"unit": "كجم/سنة",
                       "annual": count * tech.get("final_weight_kg", 2) * cyc_y,
                       "cycles_year": cyc_y}
    elif ptype == "mixed":
        m_day = count * tech.get("milk_per_day_L", 1)
        production = {"unit": "لتر/سنة",
                       "annual": m_day * tech.get("lactation_days", 200),
                       "per_day": m_day}
    else:
        production = {"unit": "خدمات", "annual": 0}
    return {"barn_key": key, "std": std, "dims": dims, "count": count,
            "feed": {"per_head_day_kg": tech.get("feed_per_day_g", 100) / 1000,
                      "total_day_kg": feed_day,
                      "total_year_ton": feed_day * 365 / 1000},
            "water": {"per_head_day_L": tech.get("water_per_day_ml", 200) / 1000,
                       "total_day_L": water_day,
                       "total_year_m3": water_day * 365 / 1000},
            "labor": {"workers": workers,
                       "animals_per_worker": count // workers},
            "production": production,
            "ventilation": {"summer_m3h": dims["vent_flow_summer_m3h"],
                              "winter_m3h": dims["vent_flow_winter_m3h"]}}


def generate_feasibility_booklet(key, count, project_name="", requester_name=""):
    feas = calculate_technical_feasibility(key, count)
    if not feas:
        return None
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40,
                            topMargin=115, bottomMargin=145)
    story = []
    def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
        return Paragraph(ar(text), ParagraphStyle(
            's', fontName=font_mgr.font_name, fontSize=size,
            alignment=align, textColor=HexColor(color),
            spaceAfter=6, leading=size * 1.6))
    std = feas["std"]
    dims = feas["dims"]
    story.append(Spacer(1, 30))
    story.append(P("كتيّب دراسة الجدوى", size=30, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=3, color=HexColor('#d4af37')))
    story.append(Spacer(1, 30))
    story.append(P(f"مشروع: {project_name or std['name_ar']}", size=18,
                   align=TA_CENTER, color='#c62828'))
    story.append(Spacer(1, 15))
    story.append(P(f"{count} رأس", size=14, align=TA_CENTER))
    story.append(PageBreak())
    barn_data = [[ar("البيان"), ar("القيمة")],
                  [ar("المساحة"), ar(f"{dims['total_area_m2']} م²")],
                  [ar("الطول"), ar(f"{dims['length_m']} م")],
                  [ar("العرض"), ar(f"{dims['width_m']} م")],
                  [ar("الارتفاع"), ar(f"{dims['height_m']} م")],
                  [ar("الحجم"), ar(f"{dims['volume_m3']} م³")]]
    t = Table(barn_data, colWidths=[220, 230])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10)]))
    story.append(t)
    img = render_barn_to_pdf_image(dims)
    if img:
        try:
            story.append(RLImage(img, width=480, height=340))
        except Exception:
            pass
    doc.build(story, onFirstPage=pdf_gen._draw_page,
              onLaterPages=pdf_gen._draw_page)
    buffer.seek(0)
    return buffer.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# الجلسة + CSS + بوابة الدخول
# ═══════════════════════════════════════════════════════════════════════════

DEFAULTS = {
    "approved": False, "user_role": None,
    "active_formula": {}, "active_stage_title": "إنتاج عام",
    "computed_ton_cost": 280.0, "inventory": {},
    "shared_comments": f"• مرحباً في {APP_NAME}\n• {DUA_SHORT}\n",
    "broiler_farms": {}, "barn_video_gif": None,
    "last_formulation_result": None, "last_formulation_context": None,
    "last_ocr_result": None, "last_ocr_nutrients": None,
    "owner_attempts": 0, "owner_lock_until": 0.0,
    "invoices": [], "formulation_history": [],
    "comments_list": [], "last_activity": _time.time(),
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state["inventory"]:
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing in cat:
            st.session_state["inventory"][ing] = {
                "quantity": 25.0, "min_threshold": 5.0, "unit": "طن"}


class SharedStorage:
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


def is_owner() -> bool:
    return st.session_state.get("user_role") == "owner"


# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');
* { font-family: 'Cairo', 'Amiri', sans-serif; color: #1a1a1a !important; }
html, body, [data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600");
    background-size: cover; background-position: center;
    background-attachment: fixed;
}
.main-box {
    background: rgba(255,255,255,0.92); padding: 32px;
    border-radius: 22px; box-shadow: 0 15px 45px rgba(0,0,0,0.15);
    margin-bottom: 70px; backdrop-filter: blur(12px);
    border: 1px solid rgba(212,175,55,0.2);
}
@keyframes duaGlow {
    0%,100% { box-shadow: 0 15px 45px rgba(0,0,0,0.4), inset 0 0 30px rgba(212,175,55,0.2); }
    50% { box-shadow: 0 15px 45px rgba(0,0,0,0.5), inset 0 0 45px rgba(212,175,55,0.45); }
}
.dua-main-box {
    background: linear-gradient(135deg, #0d3011, #1b5e20, #2e7d32, #1b5e20, #0d3011);
    background-size: 200% 200%;
    animation: duaGlow 4s ease-in-out infinite;
    padding: 34px 28px; border-radius: 22px;
    border: 4px solid #d4af37; direction: rtl; text-align: center;
    margin: 25px 0;
}
.dua-main-box * { color: white !important; }
.dua-main-box h3 { color: #d4af37 !important; font-size: 1.9rem; margin-bottom: 18px; font-weight: 900; }
.dua-main-box .names {
    display: inline-block; background: linear-gradient(90deg, rgba(212,175,55,0.15), rgba(212,175,55,0.35), rgba(212,175,55,0.15));
    font-size: 1.65rem; font-weight: 900; color: #ffeb3b !important;
    margin: 20px 0; padding: 16px 30px; border: 2px solid #d4af37;
    border-radius: 16px; font-family: 'Amiri', serif !important;
}
.dua-main-box p.quran {
    font-family: 'Amiri', serif !important; font-size: 1.2rem;
    color: #d4af37 !important; margin-top: 22px; padding: 18px 25px;
    background: rgba(0,0,0,0.25); border-radius: 12px;
    border-right: 5px solid #d4af37; border-left: 5px solid #d4af37;
}
.dua-fixed-banner {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32, #1b5e20, #0d3011);
    color: white !important; padding: 12px 20px; z-index: 9998; text-align: center;
    border-top: 3px solid #d4af37; font-family: 'Amiri', serif !important;
    font-size: 1.05rem; font-weight: bold;
}
.dua-fixed-banner * { color: #ffeb3b !important; font-family: 'Amiri' !important; }
.section-title {
    color: #1b5e20 !important; border-right: 6px solid #2e7d32;
    padding: 12px 18px; text-align: right; font-size: 1.5rem; font-weight: 900;
    margin-top: 30px; margin-bottom: 20px;
    background: linear-gradient(to left, rgba(46,125,50,0.15), transparent);
    border-radius: 10px;
}
.formula-item {
    background: linear-gradient(135deg, #ffffff, #e8f5e9);
    padding: 15px 20px; border-radius: 10px; margin-bottom: 10px;
    font-weight: 700; color: #1b5e20 !important;
    border-right: 5px solid #2e7d32; text-align: right;
}
.price-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px; border-radius: 16px; border-right: 5px solid #2e7d32;
    margin-bottom: 20px; direction: rtl; text-align: right;
}
.oil-info-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 18px; border-radius: 16px; border-right: 5px solid #e65100;
    margin-bottom: 18px; direction: rtl; text-align: right;
}
.physio-card {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 18px 24px; border-radius: 14px; border-right: 6px solid #1565c0;
    margin-bottom: 20px; direction: rtl; text-align: right;
}
.physio-card h4 { color: #0d47a1 !important; margin: 0 0 8px 0; }
.quality-good-v113 {
    background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
    padding: 24px; border-radius: 22px; border-right: 8px solid #1b5e20;
    margin: 18px 0; direction: rtl; text-align: right;
}
.quality-bad-v113 {
    background: linear-gradient(135deg, #ffcdd2, #ef9a9a);
    padding: 24px; border-radius: 22px; border-right: 8px solid #c62828;
    margin: 18px 0; direction: rtl; text-align: right;
}
.profile-img-style {
    width: 150px; height: 150px; border-radius: 50%; object-fit: cover;
    border: 4px solid #d4af37; display: block; margin: 0 auto;
}
.stButton > button {
    color: #1a1a1a !important;
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9) !important;
    border: 1.5px solid #2e7d32 !important;
    font-weight: 700 !important; border-radius: 10px !important;
}
.mini-signature {
    position: fixed; left: 20px; bottom: 70px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important; padding: 9px 22px; font-size: 0.85rem;
    border-radius: 25px; z-index: 9997; direction: rtl;
    border: 2px solid #d4af37; font-weight: 700;
}
.mini-signature * { color: white !important; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #2e7d32, #1b5e20) !important;
}
.stTabs [aria-selected="true"] * { color: white !important; }
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff, #f1f8e9);
    padding: 14px 18px; border-radius: 16px; border-right: 4px solid #2e7d32;
}
[data-testid="stMetricValue"] {
    color: #1b5e20 !important; font-weight: 900 !important;
}
</style>
""", unsafe_allow_html=True)


# قفل تلقائي
_now_check = _time.time()
_last_check = st.session_state.get("last_activity", _now_check)
if st.session_state.get("approved") and (_now_check - _last_check) > 3600:
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.warning("🔒 جلسة منتهية")
    st.rerun()
st.session_state["last_activity"] = _now_check
generate_csrf_token()

if st.session_state.get("approved", False) and not _session_valid():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.error("⚠️ جلسة غير صالحة")
    st.stop()

if not st.session_state.get("approved", False):
    st.markdown('<div class="main-box" style="max-width: 780px; margin: 30px auto; direction: rtl;">',
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
        if img_base64:
            st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" class="profile-img-style">',
                        unsafe_allow_html=True)
    with col_title:
        st.markdown(f"<h2 style='color:#2E7D32; text-align:right;'>🌾 {APP_NAME}</h2>",
                    unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#c62828; text-align:right;'>{SUPERVISOR}</h4>",
                    unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#1b5e20;'>🔐 بوابة الدخول</h3>",
                unsafe_allow_html=True)
    col_owner, col_guest = st.columns(2)
    with col_owner:
        oc = st.text_input("🔑 كود المالك:", type="password", key="owner_code")
        if st.button("👑 دخول المالك", type="primary", use_container_width=True):
            now = _time.time()
            lock = st.session_state.get("owner_lock_until", 0.0)
            if now < lock:
                st.error(f"🔒 مقفل — {int(lock - now)}ث")
            elif check_owner_code(oc):
                st.session_state.update({"approved": True, "user_role": "owner"})
                st.rerun()
            else:
                n = st.session_state.get("owner_attempts", 0) + 1
                st.session_state["owner_attempts"] = n
                if n >= 3:
                    st.session_state["owner_lock_until"] = now + 300
                    st.error("🔒 3 محاولات — قفل 5 دقائق")
                else:
                    st.error(f"❌ متبقٍ {3 - n}")
    with col_guest:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True):
            st.session_state.update({"approved": True, "user_role": "guest"})
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════
# الواجهة الرئيسية + التبويبات الهرمية
# ═══════════════════════════════════════════════════════════════════════════

st.markdown('<div class="main-box">', unsafe_allow_html=True)

c1, c2 = st.columns([0.7, 0.3])
with c2:
    role_label = "المالك 👑" if is_owner() else "زائر 👥"
    st.markdown(f"<div style='text-align:left; padding:10px; background:#f5f5f5; border-radius:10px;'>الحساب: <b>{role_label}</b></div>",
                unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.cache_data.clear()
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
    st.markdown(f"<h1 style='color: #0d3011; text-align:right; font-weight: 900;'>🌾 {APP_NAME}</h1>",
                unsafe_allow_html=True)
    st.markdown(f"<p style='color: #1565C0; text-align:right; font-size: 1.25rem; font-weight: 600;'>{APP_TAGLINE}</p>",
                unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #fff8e1, #ffe082); padding: 12px 20px;
                border-radius: 12px; border-right: 6px solid #c62828; border-left: 6px solid #c62828;'>
        <h3 style='color: #b71c1c; text-align:right; margin: 0; font-weight: 900;'>
            👨‍🔬 {SUPERVISOR}
        </h3>
        <p style='color: #0d47a1; text-align:right; margin: 5px 0 0 0; font-weight: 700;'>
            ✨ {SUPERVISOR_TITLE}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f'<div class="visitor-dua-banner" style="background:linear-gradient(135deg,#fff8e1,#ffe082);padding:20px;border-radius:16px;border:3px solid #d4af37;text-align:center;margin:22px 0;">{DUA_VISITOR}</div>',
            unsafe_allow_html=True)
st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# 🆕 التبويبات الهرمية (v11.8)
# ═══════════════════════════════════════════════════════════════════════════

TAB_STRUCTURE_OWNER = {
    "🌾 التركيب والتغذية": ["🔬 النمذجة"],
    "🏗️ التصميم والهندسة": ["🏗️ الحظائر 3D", "📊 الجدوى", "🐔 المزارع"],
    "💼 الإدارة": ["🏭 المستودعات", "🧾 الفواتير", "🖨️ الديباجة",
                    "📈 التحليلات", "💬 التعليقات"],
    "💬 التواصل": ["💬 الدردشة", "🎬 الاستديو"],
    "📚 المراجع والدعم": ["📚 المراجع", "💡 المساعدة", "📖 الدليل"],
}

TAB_STRUCTURE_GUEST = {
    "🌾 التركيب والتغذية": ["🔬 النمذجة"],
    "🏗️ التصميم والهندسة": ["🏗️ الحظائر 3D", "📊 الجدوى", "🐔 المزارع"],
    "💬 التواصل": ["💬 الدردشة", "🎬 الاستديو"],
    "📚 المراجع والدعم": ["📚 المراجع", "💡 المساعدة", "📖 الدليل"],
}

TAB_STRUCTURE = TAB_STRUCTURE_OWNER if is_owner() else TAB_STRUCTURE_GUEST
_main_titles = list(TAB_STRUCTURE.keys())
_main_tabs = st.tabs(_main_titles)
tab_map = {}
for _main_title, _main_tab in zip(_main_titles, _main_tabs):
    with _main_tab:
        _sub_titles = TAB_STRUCTURE[_main_title]
        _sub_tabs = st.tabs(_sub_titles)
        for _sub_title, _sub_tab in zip(_sub_titles, _sub_tabs):
            tab_map[_sub_title] = _sub_tab


# ═══════════════════════════════════════════════════════════════════════════
# 🔬 تبويب النمذجة (5 تبويبات فرعية)
# ═══════════════════════════════════════════════════════════════════════════

with tab_map["🔬 النمذجة"]:
    try:
        sub_lp, sub_nlp, sub_milk, sub_oils, sub_lab = st.tabs([
            "🎯 LP (تركيب علفة)",
            "🎯 NLP (غير خطي)",
            "🍼 بدائل الحليب",
            "🌰 الزيوت",
            "🔬 مختبر التحليل",
        ])

        # ══════════════════════════════════════════════════════════
        # 1) LP — تركيب علفة
        # ══════════════════════════════════════════════════════════
        with sub_lp:
            try:
                st.markdown('<div class="section-title">🧬 أساس البروتين</div>',
                            unsafe_allow_html=True)
                pb = st.radio("الأساس:",
                               ["البروتين المهضوم (DP) — الأدق",
                                "البروتين الخام (CP) — الأسهل"],
                               horizontal=True, key="protein_basis")
                basis_code = "DP" if "DP" in pb else "CP"

                st.markdown('<div class="section-title">🐾 اختر الحيوان</div>',
                            unsafe_allow_html=True)
                lp_animal, lp_prod, lp_req, lp_std_key = get_animal_requirement_ui("lp")

                if not lp_req:
                    st.warning("⚠️ اختر حيواناً")
                else:
                    st.markdown(f"""
                    <div class="physio-card">
                        <h4>🧬 الحالة الفسيولوجية</h4>
                        <p style="color: #1a237e; font-size: 1.15rem; font-weight: 700;">
                            {lp_animal} — <span style="color:#c62828;">{lp_req.name_ar}</span>
                        </p>
                        <div style="display:flex; gap:12px; flex-wrap:wrap;">
                            <span style="background:#fff;padding:6px 14px;border-radius:8px;">
                                DP: <b>{lp_req.DP}%</b></span>
                            <span style="background:#fff;padding:6px 14px;border-radius:8px;">
                                CP: <b>{lp_req.CP}%</b></span>
                            <span style="background:#fff;padding:6px 14px;border-radius:8px;">
                                SE: <b>{lp_req.SE}</b></span>
                            <span style="background:#fff;padding:6px 14px;border-radius:8px;">
                                Ca:P: <b>{(lp_req.Ca/lp_req.P) if lp_req.P else 0:.2f}</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    oil_std_info = get_oil_standard(lp_std_key)
                    st.markdown(f"""
                    <div class="oil-info-card">
                    <b>🌰 الزيوت:</b> أقصى {oil_std_info['max']}% | مثالي {oil_std_info['optimal']}%
                    </div>
                    """, unsafe_allow_html=True)

                    requester_name = st.text_input("👤 اسم طالب العلفة:",
                                                      key="req_name_lp")

                    st.markdown('<div class="section-title">🌾 اختيار المكونات</div>',
                                unsafe_allow_html=True)
                    sq = st.text_input("🔍 بحث سريع:", key="ing_search_lp")
                    selected = []
                    default_set = get_default_selections(lp_animal, lp_prod, lp_req)

                    for cat_name, items in BIG_FEEDS_LIBRARY.items():
                        filt = ({k: v for k, v in items.items()
                                 if sq.lower() in k.lower()} if sq else items)
                        if not filt:
                            continue
                        expanded = any(x in cat_name for x in
                                        ["الحبوب", "الأكساب", "الزيوت", "الأملاح"])
                        with st.expander(f"📁 {cat_name} ({len(filt)})", expanded=expanded):
                            sc = st.columns(3)
                            for idx, ing_name in enumerate(filt.keys()):
                                with sc[idx % 3]:
                                    dflt = ing_name in default_set
                                    if st.checkbox(ing_name, value=dflt,
                                                    key=f"pick_{lp_animal}_{ing_name}"):
                                        selected.append(ing_name)

                    st.markdown("### 💰 أسعار المواد")
                    prices_dict = {}
                    if selected:
                        pcols = st.columns(min(3, len(selected)))
                        for idx, ing in enumerate(selected):
                            lookup = _get_ingredient_lookup()
                            with pcols[idx % 3]:
                                prices_dict[ing] = st.number_input(
                                    f"💵 {ing} ($/طن)", min_value=5.0,
                                    value=float(lookup.get(ing, {}).get("price", 350)),
                                    step=10.0, key=f"p_sel_{lp_animal}_{ing}")

                    st.success(f"✅ المختارة: **{len(selected)}** مادة")

                    if st.button("🚀 تشغيل LP", type="primary", use_container_width=True):
                        if len(selected) < 3:
                            st.error("⚠️ اختر 3 مكونات على الأقل")
                        else:
                            custom_std = requirement_to_standard(lp_req)
                            with st.spinner("⏳ جاري التركيب..."):
                                result = auto_formulate_smart(
                                    selected, prices_dict, custom_std,
                                    standard_key=lp_std_key, basis=basis_code,
                                    min_quality=70.0, animal_type=lp_animal,
                                    production_type=lp_prod)
                            if result["success"]:
                                st.session_state["last_formulation_result"] = result
                                st.session_state["last_formulation_context"] = {
                                    "animal_choice": lp_animal,
                                    "requirement_name": lp_req.name_ar,
                                    "basis_label": basis_code,
                                    "requirement": lp_req,
                                    "custom_standard": custom_std,
                                    "std_key_global": lp_std_key,
                                    "requester_name": requester_name,
                                    "local_rate": 1.0, "local_sym": "USD",
                                    "animal_type": lp_animal,
                                    "production_type": lp_prod,
                                }
                            else:
                                st.error(f"❌ {result['message']}")

                    if st.session_state.get("last_formulation_result"):
                        result = st.session_state["last_formulation_result"]
                        ctx = st.session_state["last_formulation_context"]
                        formula = result["formula"]
                        actual = result["actual_nutrients"]
                        quality = result.get("quality_score", 0.0)
                        meets = result.get("meets_standard", False)
                        ca_p = (actual.get("Ca", 0) / actual.get("P", 1)
                                if actual.get("P", 0) > 0 else 0)

                        if meets:
                            st.markdown(f"""
                            <div class="quality-good-v113">
                            <h3 style="color:#1b5e20;">✅ الجودة: {quality:.1f}%</h3>
                            <p>Ca:P = {ca_p:.2f} | التكلفة: ${result['cost']:.2f}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="quality-bad-v113">
                            <h3 style="color:#c62828;">⚠️ الجودة: {quality:.1f}%</h3>
                            </div>
                            """, unsafe_allow_html=True)

                        cmp_rows = []
                        labels = {"CP": "CP", "DP": "DP", "SE": "SE",
                                  "NDF": "NDF", "ADF": "ADF", "EE": "EE",
                                  "ASH": "ASH", "Ca": "Ca", "P": "P"}
                        for k, sv in ctx["custom_standard"].items():
                            if sv == 0:
                                continue
                            cv = actual.get(k, 0.0)
                            diff = cv - sv
                            pct = (diff / sv * 100) if sv else 0
                            ev = evaluate_difference(pct, standard_value=sv)
                            cmp_rows.append({"العنصر": labels.get(k, k),
                                              "المعيار": f"{sv:.2f}",
                                              "المحسوب": f"{cv:.2f}",
                                              "الفرق": f"{diff:+.3f}",
                                              "التقييم": ev["label"],
                                              "score": ev["score"]})

                        st.markdown("### 📊 جدول المقارنة")
                        st.dataframe(pd.DataFrame([{k: v for k, v in r.items()
                                                    if k != "score"} for r in cmp_rows]),
                                      use_container_width=True, hide_index=True)

                        st.markdown("### 🌾 المكونات:")
                        for ing, pct in formula.items():
                            st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.2f}%</div>',
                                        unsafe_allow_html=True)

                        render_scientific_panel = st.expander("📚 التوثيق العلمي")
                        with render_scientific_panel:
                            st.code("LP Model — NRC/INRA/Ross 308", language="text")

                        ch1, ch2 = st.columns(2)
                        with ch1:
                            bf = create_colorful_bar_chart(ctx["custom_standard"], actual)
                            if bf:
                                st.image(bf.getvalue(), use_container_width=True)
                        with ch2:
                            pf = create_colorful_pie_chart(formula)
                            if pf:
                                st.image(pf.getvalue(), use_container_width=True)

                        # تحميل
                        dl1, dl2 = st.columns(2)
                        with dl1:
                            try:
                                pdf_bytes = pdf_gen.generate_report(
                                    formula=formula, requirement=ctx["requirement"],
                                    animal_type=ctx["animal_type"],
                                    breed=ctx["requirement_name"],
                                    cost=result["cost"], city="—",
                                    local_cost=result["cost"], local_sym="USD",
                                    requester_name=ctx["requester_name"],
                                    protein_basis=ctx["basis_label"],
                                    standard_key=ctx["std_key_global"],
                                    include_charts=True, quality_score=quality)
                                st.download_button("📥 تحميل PDF", pdf_bytes,
                                                    file_name=f"Formula_{lp_animal}.pdf",
                                                    mime="application/pdf",
                                                    use_container_width=True)
                            except Exception as e:
                                st.error(f"⚠️ {e}")
            except Exception as e:
                st.error(f"⚠️ {e}")
                with st.expander("التفاصيل"):
                    st.code(traceback.format_exc())

        # ══════════════════════════════════════════════════════════
        # 2) NLP — مع اختيار الحيوان (جديد 11.8)
        # ══════════════════════════════════════════════════════════
        with sub_nlp:
            try:
                st.markdown('<div class="section-title">🎯 NLP — تحسين غير خطي حسب NRC</div>',
                            unsafe_allow_html=True)

                if not SCIPY_AVAILABLE or minimize is None:
                    st.error("⚠️ SCIPY (minimize) غير مثبتة")
                elif not check_rate_limit("nlp", max_calls=15, window=60):
                    st.warning("⏳ تهدئة — انتظر دقيقة")
                else:
                    st.markdown("### 🐾 1. اختيار الحيوان")
                    nlp_animal, nlp_prod, nlp_req, nlp_std_key = \
                        get_animal_requirement_ui("nlp")

                    if nlp_req:
                        st.success(f"📌 {nlp_req.name_ar} | DP={nlp_req.DP}% | "
                                    f"CP={nlp_req.CP}% | SE={nlp_req.SE} | "
                                    f"Ca:P={nlp_req.Ca/nlp_req.P:.2f}")

                    st.markdown("### 🧬 2. أساس البروتين")
                    nlp_basis_radio = st.radio("الأساس:",
                                                 ["البروتين المهضوم (DP)",
                                                  "البروتين الخام (CP)"],
                                                 horizontal=True, key="nlp_basis")
                    nlp_basis = "DP" if "DP" in nlp_basis_radio else "CP"

                    st.markdown("### 🌾 3. اختيار المكونات")
                    all_ings_nlp = list(_get_ingredient_lookup().keys())
                    nlp_sel = st.multiselect("المكونات (2–10):",
                                              options=all_ings_nlp,
                                              default=[], max_selections=10,
                                              key="nlp_sel_v8")

                    if len(nlp_sel) >= 2:
                        lookup = _get_ingredient_lookup()
                        ing_data = {i: lookup[i] for i in nlp_sel}

                        st.markdown("### 💰 4. الأسعار ($/طن)")
                        nlp_prices = {}
                        pcols = st.columns(min(3, len(nlp_sel)))
                        for i, ing in enumerate(nlp_sel):
                            with pcols[i % 3]:
                                nlp_prices[ing] = st.number_input(
                                    f"{ing}:", min_value=10.0,
                                    value=float(lookup[ing].get("price", 300)),
                                    step=10.0, key=f"nlp_p8_{ing}")

                        st.markdown("### ⚙️ 5. سعر المنتج")
                        price_product = st.number_input(
                            "سعر المنتج النهائي ($/وحدة):",
                            0.5, 20.0, 2.5, 0.1, key="nlp_pp8")

                        if st.button("🚀 تشغيل محرك NLP",
                                      type="primary", use_container_width=True,
                                      disabled=(nlp_req is None)):
                            with st.spinner("⏳ جاري التحسين..."):
                                result = nlp_optimize_feed_v2(
                                    nlp_sel, ing_data, nlp_prices,
                                    requirement=nlp_req,
                                    animal_type=nlp_animal,
                                    standard_key=nlp_std_key,
                                    protein_basis=nlp_basis,
                                    price_product=price_product)

                            if result["success"]:
                                audit_log("NLP_RUN",
                                           f"{nlp_animal}|profit={result['max_profit']:.2f}")
                                st.success(f"✅ ربح: ${result['max_profit']:.4f} | "
                                            f"تكلفة: ${result['final_cost']:.4f}/كجم")

                                m1, m2, m3, m4 = st.columns(4)
                                m1.metric("💰 التكلفة", f"${result['final_cost']:.4f}")
                                m2.metric("⚡ ME", f"{result['final_me']:.0f}")
                                m3.metric("🧬 CP", f"{result['final_cp']:.2f}%")
                                m4.metric("⚖️ Ca:P", f"{result['ca_p_ratio']:.2f}")

                                st.markdown("### 🌾 التركيبة المثلى")
                                for ing, pct in result["formula"].items():
                                    st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.2f}%</div>',
                                                unsafe_allow_html=True)

                                fig_curve = create_nlp_profit_curve(
                                    result, nlp_sel, ing_data, nlp_prices)
                                if fig_curve:
                                    st.plotly_chart(fig_curve, use_container_width=True)

                                # مقارنة
                                st.markdown("### 📊 مقارنة مع المعيار")
                                cmp = [{"العنصر": "CP",
                                         "المعيار": f"{nlp_req.CP:.2f}",
                                         "المحسوب": f"{result['final_cp']:.2f}"},
                                        {"العنصر": "DP",
                                         "المعيار": f"{nlp_req.DP:.2f}",
                                         "المحسوب": f"{result['final_dp']:.2f}"},
                                        {"العنصر": "SE",
                                         "المعيار": f"{nlp_req.SE:.1f}",
                                         "المحسوب": f"{result['final_me']/41:.1f}"},
                                        {"العنصر": "Ca",
                                         "المعيار": f"{nlp_req.Ca:.2f}",
                                         "المحسوب": f"{result['final_ca']:.2f}"},
                                        {"العنصر": "P",
                                         "المعيار": f"{nlp_req.P:.2f}",
                                         "المحسوب": f"{result['final_p']:.2f}"},
                                        {"العنصر": "Ca:P",
                                         "المعيار": f"{nlp_req.Ca/nlp_req.P:.2f}",
                                         "المحسوب": f"{result['ca_p_ratio']:.2f}"}]
                                st.dataframe(pd.DataFrame(cmp), use_container_width=True,
                                              hide_index=True)
                            else:
                                st.error(f"❌ {result['message']}")
                    else:
                        st.info("💡 اختر مكونين على الأقل")
            except Exception as e:
                st.error(f"⚠️ {e}")

        # ══════════════════════════════════════════════════════════
        # 3) بدائل الحليب
        # ══════════════════════════════════════════════════════════
        with sub_milk:
            try:
                st.markdown('<div class="section-title">🍼 بدائل الحليب</div>',
                            unsafe_allow_html=True)
                st.caption("⚠️ شرط: 3 مكونات كافية — 4 مفضّلة")

                mr1, mr2 = st.columns(2)
                with mr1:
                    mr_a = st.selectbox("الحيوان:",
                                          list(MILK_REPLACER_STANDARDS.keys()),
                                          key="mr_a")
                    mr_v = st.number_input("الكمية (كجم):", 1.0, 10000.0,
                                            100.0, 10.0, key="mr_v")
                with mr2:
                    std_mr = MILK_REPLACER_STANDARDS[mr_a]
                    st.markdown(f"""
                    <div class="price-card">
                    <b>{mr_a}:</b><br>
                    بروتين: {std_mr['CP']}% | دهن: {std_mr['Fat']}% | لاكتوز: {std_mr['Lactose']}%<br>
                    <small>{std_mr['source']}</small>
                    </div>
                    """, unsafe_allow_html=True)

                mr_sel = []
                cols = st.columns(3)
                for i, (name, data) in enumerate(MILK_REPLACER_INGREDIENTS.items()):
                    with cols[i % 3]:
                        with st.expander(f"{name}"):
                            st.caption(f"${data['price']}/كجم | {data['type']}")
                            if st.checkbox("إضافة", key=f"mr8_{name}"):
                                mr_sel.append(name)

                st.info(f"📊 المختارة: {len(mr_sel)} | الحد: 3")

                if st.button("🧪 تركيب", type="primary", use_container_width=True):
                    if len(mr_sel) < 3:
                        st.warning("⚠️ 3 مكونات على الأقل")
                    else:
                        with st.spinner("⏳ جاري..."):
                            r = formulate_milk_replacer(mr_a, mr_v, mr_sel)
                        if r["success"]:
                            quality = r.get("quality_score", 0)
                            meets70 = quality >= 70
                            bg = "quality-good-v113" if meets70 else "quality-bad-v113"
                            st.markdown(f"""
                            <div class="{bg}">
                            <h3>✅ الجودة: {quality:.1f}%</h3>
                            <p>Ca:P = {r['ca_p_ratio']:.2f} | المكونات: {r['used_count']}</p>
                            </div>
                            """, unsafe_allow_html=True)

                            labels_mr = {"CP": "بروتين", "Fat": "دهن",
                                         "Lactose": "لاكتوز", "Ca": "Ca",
                                         "P": "P", "Lys": "Lys", "Met": "Met"}
                            comp_rows = []
                            for k, lab in labels_mr.items():
                                t = r["targets"].get(k, 0)
                                a = r["actual"].get(k, 0)
                                if t <= 0:
                                    continue
                                diff = a - t
                                pct = (diff / t * 100) if t else 0
                                ev = evaluate_difference(pct, standard_value=t)
                                comp_rows.append({"العنصر": lab,
                                                   "المعيار": f"{t:.2f}",
                                                   "المحسوب": f"{a:.2f}",
                                                   "التقييم": ev["label"]})
                            st.dataframe(pd.DataFrame(comp_rows),
                                          use_container_width=True, hide_index=True)

                            for ing, pct in r["formula"].items():
                                st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct:.2f}%</div>',
                                            unsafe_allow_html=True)

                            pdf_mr = generate_milk_replacer_pdf(r)
                            if pdf_mr:
                                st.download_button("📄 تحميل PDF", pdf_mr,
                                                    file_name=f"Milk_{mr_a}.pdf",
                                                    mime="application/pdf",
                                                    use_container_width=True)
                        else:
                            st.error(f"❌ {r['message']}")
            except Exception as e:
                st.error(f"⚠️ {e}")

        # ══════════════════════════════════════════════════════════
        # 4) الزيوت
        # ══════════════════════════════════════════════════════════
        with sub_oils:
            try:
                st.markdown('<div class="section-title">🌰 مكتبة الزيوت</div>',
                            unsafe_allow_html=True)
                st.write(f"{len(get_oil_ingredients())} زيتاً وفق NRC/INRA/Ross 308")

                st.markdown("### 📊 الحدود القياسية")
                oil_rows = [{"الحيوان": k, "أقصى %": f"{v['max']}%",
                              "مثالي %": f"{v['optimal']}%",
                              "المرجع": v["source"]}
                             for k, v in MAX_OIL_PERCENTAGE.items()]
                st.dataframe(pd.DataFrame(oil_rows),
                              use_container_width=True, hide_index=True)

                oils = get_oil_ingredients()
                st.markdown(f"### 🌰 الزيوت ({len(oils)})")
                for ing_name, ing_data in oils.items():
                    with st.expander(f"🌰 {ing_name}"):
                        c1, c2, c3 = st.columns(3)
                        c1.metric("SE", f"{ing_data.get('SE', 0):.0f}")
                        c2.metric("kcal/kg", f"{ing_data.get('SE', 0) * 41:.0f}")
                        c3.metric("السعر", f"${ing_data.get('price', 0):.0f}")
                        st.info(f"📝 {ing_data.get('desc', '')}")
            except Exception as e:
                st.error(f"⚠️ {e}")

        # ══════════════════════════════════════════════════════════
        # 5) المختبر — مع اختيار الحيوان (جديد 11.8)
        # ══════════════════════════════════════════════════════════
        with sub_lab:
            try:
                st.markdown('<div class="section-title">🔬 مختبر التحليل الذكي</div>',
                            unsafe_allow_html=True)

                st.markdown("### 🐾 1. اختر الحيوان للمقارنة المعيارية")
                lab_animal, lab_prod, lab_req, lab_std_key = \
                    get_animal_requirement_ui("lab")

                lab_std = (requirement_to_standard(lab_req)
                           if lab_req else {})

                if lab_req:
                    st.success(f"📌 المرجع: {lab_req.name_ar} | "
                                f"DP={lab_req.DP}% | CP={lab_req.CP}%")

                st.markdown("### 🌾 2. أدخل أوزان المكونات")
                all_ings = list(_get_ingredient_lookup().keys())
                lab_cat = st.selectbox("📁 التصنيف:",
                                        ["الكل"] + list(BIG_FEEDS_LIBRARY.keys()),
                                        key="lab_cat8")
                lab_search = st.text_input("🔍 بحث:", key="lab_srch8")

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
                    "السعر ($/طن)": [float(lookup_lab.get(m, {}).get("price", 300.0))
                                     for m in pool],
                })

                edited = st.data_editor(default_df, use_container_width=True,
                                          hide_index=True,
                                          column_config={
                                              "المادة": st.column_config.TextColumn(disabled=True),
                                              "الوزن (كجم)": st.column_config.NumberColumn(
                                                  min_value=0.0, step=5.0, format="%.1f"),
                                              "السعر ($/طن)": st.column_config.NumberColumn(
                                                  min_value=5.0, step=10.0, format="$%.0f"),
                                          },
                                          key="lab_editor_v8", num_rows="fixed")

                lab_in = {r["المادة"]: r["الوزن (كجم)"]
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

                    if lab_req:
                        st.markdown("### 📊 المقارنة مع الحيوان المختار")
                        cmp_rows = []
                        for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "Ca", "P"]:
                            sv = lab_std.get(k, 0)
                            if sv == 0:
                                continue
                            cv = nut.get(k, 0)
                            diff = cv - sv
                            pct = (diff / sv * 100) if sv else 0
                            ev = evaluate_difference(pct, standard_value=sv)
                            cmp_rows.append({"العنصر": k,
                                              "المعيار": f"{sv:.2f}",
                                              "المحسوب": f"{cv:.2f}",
                                              "الفرق": f"{diff:+.3f}",
                                              "الفرق %": f"{pct:+.2f}%",
                                              "التقييم": ev["label"],
                                              "score": ev["score"]})
                        st.dataframe(pd.DataFrame([{k: v for k, v in r.items()
                                                     if k != "score"} for r in cmp_rows]),
                                      use_container_width=True, hide_index=True)

                        quality = sum(r["score"] for r in cmp_rows) / len(cmp_rows)
                        st.metric("🏆 الجودة", f"{quality:.1f}%")

                        ch1, ch2 = st.columns(2)
                        with ch1:
                            bf = create_colorful_bar_chart(lab_std, nut)
                            if bf:
                                st.image(bf.getvalue(), caption="📊 المقارنة",
                                          use_container_width=True)
                        with ch2:
                            rf = create_radar_chart(lab_std, nut)
                            if rf:
                                st.image(rf.getvalue(), caption="🕸️ الرادار",
                                          use_container_width=True)

                    st.markdown("### 📋 التركيبة")
                    df_res = pd.DataFrame([{"المادة": k, "الوزن": f"{v:.1f}",
                                             "النسبة %": f"{f_lab[k]:.2f}"}
                                            for k, v in lab_in.items()])
                    st.table(df_res)

                    pie = create_colorful_pie_chart(f_lab)
                    if pie:
                        st.image(pie.getvalue(), use_container_width=True)
                else:
                    st.info("💡 أدخل أوزان المواد")
            except Exception as e:
                st.error(f"⚠️ {e}")
                with st.expander("التفاصيل"):
                    st.code(traceback.format_exc())
    except Exception as e:
        st.error(f"⚠️ {e}")
