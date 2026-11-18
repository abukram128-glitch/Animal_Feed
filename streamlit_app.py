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

import streamlit as st
import numpy as np, pandas as pd, io, os, re, base64, tempfile
import traceback, warnings, json, threading, random, hashlib, hmac
import time as _time
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Tuple, Any, Union, Set
warnings.filterwarnings('ignore')

try:
    from scipy.optimize import linprog, minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False; linprog = None; minimize = None
try:
    import plotly.graph_objects as go, plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
try:
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Wedge, Rectangle, Ellipse
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    from matplotlib import animation
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
try:
    from PIL import Image as PILImage; PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
try:
    import pytesseract, cv2; OCR_AVAILABLE = True
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
    from reportlab.platypus import (Table, TableStyle, Paragraph, Spacer,
        Image as RLImage, SimpleDocTemplate, HRFlowable, PageBreak, KeepTogether)
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
    import qrcode; QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════
# 🔐 الأمان
# ═══════════════════════════════════════════════════════════════════════

def _sha256(s): return hashlib.sha256(s.encode('utf-8')).hexdigest()

def _get_owner_code_hash():
    try:
        _blob = "Nzg2MjAy"
        return _sha256(base64.b64decode(_blob).decode()[::-1])
    except Exception: return None

def check_owner_code(user_input):
    if not user_input:
        audit_log("LOGIN_EMPTY", ""); return False
    expected = _get_owner_code_hash()
    if not expected:
        audit_log("LOGIN_NO_HASH", ""); return False
    ok = hmac.compare_digest(_sha256(user_input.strip()), expected)
    audit_log("LOGIN_OK" if ok else "LOGIN_FAIL", "owner")
    return ok

def _session_valid():
    role = st.session_state.get("user_role")
    if not st.session_state.get("approved", False): return False
    if role not in ("owner", "specialist", "guest"): return False
    if role == "owner" and not _get_owner_code_hash(): return False
    return True

def audit_log(event, details=""):
    try:
        with open("tawor_audit.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {event} | {details[:200]}\n")
    except Exception: pass

def check_rate_limit(key, max_calls=30, window=60):
    now = _time.time(); skey = f"_rl_{key}"
    if skey not in st.session_state: st.session_state[skey] = []
    calls = [t for t in st.session_state[skey] if now - t < window]
    if len(calls) >= max_calls: return False
    calls.append(now); st.session_state[skey] = calls
    return True

def generate_csrf_token():
    if "csrf_token" not in st.session_state:
        st.session_state["csrf_token"] = base64.b64encode(os.urandom(32)).decode()
    return st.session_state["csrf_token"]

def _sanitize_message(msg, max_len=500):
    if not msg: return ""
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
# 📚 المراجع العلمية
# ═══════════════════════════════════════════════════════════════════════

STANDARD_REFERENCES = {
    "أبقار_حليب_عالي": {"primary": "NRC (2001) — Nutrient Requirements of Dairy Cattle, 7th Ed.",
        "table": "Table 15-1: Lactating dairy cows (high production)",
        "secondary": ["INRA (2018) — Feeding System for Ruminants", "NRC (2001) — Table 15-2"]},
    "أبقار_حليب_متوسط": {"primary": "NRC (2001) — Dairy Cattle, 7th Ed.",
        "table": "Table 15-1: Lactating dairy cows (medium)", "secondary": ["INRA (2018)"]},
    "أبقار_حليب_منخفض": {"primary": "NRC (2001) — Dairy Cattle",
        "table": "Table 15-1: Low production", "secondary": ["INRA (2018)"]},
    "أبقار_تسمين_مكثف": {"primary": "NRC (2001) + NRC (1996)",
        "table": "Table 15-1: Growing/finishing", "secondary": ["INRA (2018)"]},
    "أبقار_تسمين_عادي": {"primary": "NRC (1996) — Beef Cattle",
        "table": "Table 10-1: Growth", "secondary": []},
    "أبقار_حمل_أخير": {"primary": "NRC (2001)",
        "table": "Table 15-3: Gestating", "secondary": []},
    "أبقار_صيانة": {"primary": "NRC (2001)",
        "table": "Table 15-4: Maintenance", "secondary": []},
    "أغنام_تسمين_مكثف": {"primary": "NRC (2007) — Small Ruminants",
        "table": "Table 11-1: Growing lambs", "secondary": ["INRA (2018)"]},
    "أغنام_تسمين_عادي": {"primary": "NRC (2007)", "table": "Table 11-1", "secondary": []},
    "أغنام_مرضعات": {"primary": "NRC (2007)", "table": "Table 11-2: Lactating ewes",
        "secondary": ["INRA (2018)"]},
    "أغنام_حامل_أخير": {"primary": "NRC (2007)", "table": "Table 11-2", "secondary": []},
    "أغنام_حامل_متوسط": {"primary": "NRC (2007)", "table": "Table 11-2", "secondary": []},
    "أغنام_صيانة": {"primary": "NRC (2007)", "table": "Table 11-3", "secondary": []},
    "أغنام_حملان_تيد": {"primary": "NRC (2007)", "table": "Table 11-1", "secondary": []},
    "ماعز_حلابة_عالي": {"primary": "NRC (2007)", "table": "Table 12-1",
        "secondary": ["INRA (2018)"]},
    "ماعز_حلابة_متوسط": {"primary": "NRC (2007)", "table": "Table 12-1", "secondary": []},
    "ماعز_تسمين_جديان": {"primary": "NRC (2007)", "table": "Table 12-2", "secondary": []},
    "ماعز_تيوس": {"primary": "NRC (2007)", "table": "Table 12-2", "secondary": []},
    "ماعز_صيانة": {"primary": "NRC (2007)", "table": "Table 12-3", "secondary": []},
    "ماعز_حامل_أخير": {"primary": "NRC (2007)", "table": "Table 12-2", "secondary": []},
    "إبل_حليب": {"primary": "FAO (2010) — Camel Nutrition", "table": "Section 4",
        "secondary": ["Al-Jassim et al. (2002)"]},
    "إبل_تسمين": {"primary": "FAO (2010)", "table": "Section 5", "secondary": []},
    "إبل_نمو": {"primary": "FAO (2010)", "table": "Section 3", "secondary": []},
    "إبل_سباق": {"primary": "FAO (2010)", "table": "Section 6", "secondary": []},
    "إبل_صيانة": {"primary": "FAO (2010)", "table": "Section 2", "secondary": []},
    "خيول_رياضة_مكثف": {"primary": "NRC (2007) — Horses, 6th Ed.",
        "table": "Table 10-1: Intense work", "secondary": []},
    "خيول_رياضة_عادي": {"primary": "NRC (2007)", "table": "Table 10-1", "secondary": []},
    "خيول_نمو_أمهار": {"primary": "NRC (2007)", "table": "Table 10-2", "secondary": []},
    "خيول_مرضعات": {"primary": "NRC (2007)", "table": "Table 10-3", "secondary": []},
    "خيول_صيانة": {"primary": "NRC (2007)", "table": "Table 10-4", "secondary": []},
    "دواجن_لاحم": {"primary": "Ross 308 (2020)", "table": "Nutrient requirements",
        "secondary": ["NRC (1994) — Poultry"]},
    "دواجن_بياض": {"primary": "NRC (1994) — Poultry", "table": "Table 4",
        "secondary": ["Lohmann (2020)"]},
    "سمان_تسمين": {"primary": "NRC (1994)", "table": "Table 12", "secondary": []},
    "سمان_بياض": {"primary": "NRC (1994)", "table": "Table 12", "secondary": []},
    "أسماك_بادئ": {"primary": "NRC (2011) — Fish Nutrition", "table": "Table 6-1",
        "secondary": ["FAO (2018)"]},
    "أسماك_نمو": {"primary": "NRC (2011)", "table": "Table 6-2", "secondary": []},
    "أسماك_تسمين": {"primary": "NRC (2011)", "table": "Table 6-3", "secondary": []},
    "أرانب_تسمين": {"primary": "NRC (2007)", "table": "Rabbit chapter",
        "secondary": ["INRA (2018)"]},
    "أرانب_حليب": {"primary": "NRC (2007)", "table": "Lactating does", "secondary": []},
    "أرانب_صيانة": {"primary": "NRC (2007)", "table": "Maintenance", "secondary": []},
    "خيول_مربط": {"primary": "NRC (2007) — Horses + MWPS-1 Structures Handbook",
        "table": "Stall dimensions & ventilation standards",
        "secondary": ["ASAE (2005) — Ventilation Standards",
                      "FAO (2012) — Rural Structures"]},
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

def get_references(animal_type, production_type):
    key = f"{animal_type}_{production_type}"
    if key in STANDARD_REFERENCES: return STANDARD_REFERENCES[key]
    for k, v in STANDARD_REFERENCES.items():
        if k.startswith(f"{animal_type}_"): return v
    return {"primary": "NRC (2012) — general", "table": "—",
            "secondary": ["INRA (2018)", "FAO (2010)"]}


REFERENCE_EQUATIONS = {
    "أبقار_حليب_عالي": {
        "DP": "DP = 9.0 + (الحليب × 0.175)  [سقف 16%]",
        "CP": "CP = DP ÷ 0.72",
        "SE": "SE = 60 + (الحليب × 0.35)",
        "Ca": "Ca = 0.55 + (الحليب × 0.003)",
        "P": "P = 0.33 + (الحليب × 0.0015)",
        "example": "بقرة 20 لتر → DP = 12.5% | CP ≈ 17.4%",
        "source": "NRC (2001) — Table 15-1"},
    "أبقار_حليب_متوسط": {
        "DP": "DP = 8.5 + (الحليب × 0.17)  [سقف 14%]",
        "CP": "CP = DP ÷ 0.72",
        "SE": "SE = 55 + (الحليب × 0.30)",
        "source": "NRC (2001)"},
    "أبقار_حليب_منخفض": {
        "DP": "DP = 8.0 + (الحليب × 0.16)  [سقف 12.5%]",
        "CP": "CP = DP ÷ 0.75",
        "source": "NRC (2001)"},
    "أبقار_تسمين_مكثف": {"DP": "11.5%", "CP": "14.5%", "SE": "72", "source": "NRC (1996)"},
    "أبقار_تسمين_عادي": {"DP": "9.5%", "CP": "12%", "SE": "65", "source": "NRC (1996)"},
    "أبقار_حمل_أخير": {"DP": "11.5%", "CP": "14.5%", "SE": "67", "source": "NRC (2001)"},
    "أبقار_صيانة": {"DP": "7.5%", "CP": "10%", "SE": "53", "source": "NRC (2001)"},
    "أغنام_تسمين_مكثف": {"DP": "11.5%", "CP": "14.5%", "SE": "64", "source": "NRC (2007)"},
    "أغنام_تسمين_عادي": {"DP": "9.5%", "CP": "12%", "SE": "59", "source": "NRC (2007)"},
    "أغنام_مرضعات": {"DP": "10.5 + (المواليد - 1) × 1.5", "CP": "DP ÷ 0.72",
        "source": "NRC (2007)"},
    "أغنام_حامل_أخير": {"DP": "10.5%", "CP": "13.5%", "SE": "62", "source": "NRC (2007)"},
    "أغنام_حامل_متوسط": {"DP": "8.5%", "CP": "11%", "SE": "55", "source": "NRC (2007)"},
    "أغنام_صيانة": {"DP": "7.2%", "CP": "9.5%", "SE": "48", "source": "NRC (2007)"},
    "أغنام_حملان_تيد": {"DP": "8.5%", "CP": "11%", "SE": "55", "source": "NRC (2007)"},
    "ماعز_حلابة_عالي": {"DP": "9.5 + (الحليب × 0.35)", "CP": "DP ÷ 0.72",
        "source": "NRC (2007)"},
    "ماعز_حلابة_متوسط": {"DP": "8.5 + (الحليب × 0.30)", "source": "NRC (2007)"},
    "ماعز_تسمين_جديان": {"DP": "11%", "CP": "14%", "SE": "62", "source": "NRC (2007)"},
    "ماعز_تيوس": {"DP": "9%", "CP": "11.5%", "SE": "57", "source": "NRC (2007)"},
    "ماعز_صيانة": {"DP": "6.8%", "CP": "9%", "SE": "46", "source": "NRC (2007)"},
    "ماعز_حامل_أخير": {"DP": "10%", "CP": "13%", "SE": "60", "source": "NRC (2007)"},
    "إبل_حليب": {"DP": "10.5 + (الحليب × 0.20)", "SE": "62 + (الحليب × 0.4)",
        "source": "FAO (2010)"},
    "إبل_تسمين": {"DP": "9.5%", "SE": "65", "source": "FAO (2010)"},
    "إبل_نمو": {"DP": "10.5%", "SE": "60", "source": "FAO (2010)"},
    "إبل_سباق": {"DP": "14%", "SE": "72", "source": "FAO (2010)"},
    "إبل_صيانة": {"DP": "7%", "SE": "48", "source": "FAO (2010)"},
    "خيول_رياضة_مكثف": {"DP": "10.5%", "SE": "70", "source": "NRC (2007)"},
    "خيول_رياضة_عادي": {"DP": "9%", "SE": "63", "source": "NRC (2007)"},
    "خيول_نمو_أمهار": {"DP": "12%", "SE": "65", "source": "NRC (2007)"},
    "خيول_مرضعات": {"DP": "12.5%", "SE": "68", "source": "NRC (2007)"},
    "خيول_صيانة": {"DP": "7.2%", "SE": "53", "source": "NRC (2007)"},
    "دواجن_لاحم": {"DP": "20% → 16.5%", "CP": "23% → 19%", "SE": "76 → 75",
        "example": "بادي: CP=23%, SE=76", "source": "Ross 308 (2020)"},
    "دواجن_بياض": {"DP": "15.5%", "CP": "18%", "source": "NRC (1994)"},
    "سمان_تسمين": {"DP": "18.5% → 17%", "SE": "72 → 70", "source": "NRC (1994)"},
    "سمان_بياض": {"DP": "15%", "SE": "68", "source": "NRC (1994)"},
    "أسماك_بادئ": {"DP": "32%", "CP": "40%", "source": "NRC (2011)"},
    "أسماك_نمو": {"DP": "25%", "CP": "32%", "source": "NRC (2011)"},
    "أسماك_تسمين": {"DP": "22%", "CP": "28%", "source": "NRC (2011)"},
    "أرانب_تسمين": {"DP": "15%", "CP": "17%", "source": "NRC (2007)"},
    "أرانب_حليب": {"DP": "18%", "CP": "20%", "source": "NRC (2007)"},
    "أرانب_صيانة": {"DP": "12%", "CP": "14%", "source": "NRC (2007)"},
    "خيول_مربط": {"المربط": "3.5 م × 3.5 م = 12.25 م² لكل حصان",
        "الممر": "3.5 م", "التهوية الصيف": "25 تجديد/ساعة",
        "التهوية الشتاء": "5 تجديد/ساعة", "الماء": "45 لتر/حصان/يوم",
        "source": "NRC (2007) + MWPS-1"},
    "معادلة_التركيب_LP": {"الهدف": "min Z = Σ(سعر_i × x_i)",
        "قيد_المجموع": "Σ x_i = 100%", "قيد_البروتين": "Σ(CP_i × x_i) = CP",
        "قيد_الطاقة": "Σ(SE_i × 41 × x_i) ≥ 0.90 × ME",
        "قيد_التوازن": "Σ(طاقة) - Σ(بروتين) ≥ 10%",
        "source": "Danø & Højsgaard (2005)"},
    "معادلة_التركيب_NLP": {"الهدف": "max Z = سعر × (ME/ME_هدف) × (CP/CP_هدف) - Σ(سعر_i × x_i)",
        "الطريقة": "SLSQP", "المستويات": "8 مستويات (100% → 70%)",
        "source": "Kraft (1988)"},
}

def get_reference_equations(animal_type, production_type):
    key = f"{animal_type}_{production_type}"
    if key in REFERENCE_EQUATIONS: return REFERENCE_EQUATIONS[key]
    for k, v in REFERENCE_EQUATIONS.items():
        if k.startswith(f"{animal_type}_"): return v
    return {}


# ═══════════════════════════════════════════════════════════════════════
# NLP Helper
# ═══════════════════════════════════════════════════════════════════════

def _get_requirement_for_nlp(animal_type, production_type):
    try:
        if animal_type == "أبقار": req = get_cattle_requirements(production_type)
        elif animal_type == "أغنام": req = get_sheep_requirements(production_type, is_male=True)
        elif animal_type == "ماعز": req = get_goat_requirements(production_type, is_male=False)
        elif animal_type == "إبل": req = get_camel_requirements(production_type)
        elif animal_type == "خيول": req = get_horse_requirements(production_type)
        elif animal_type == "دواجن": req = get_poultry_requirements("بياض" if "بياض" in production_type else "لاحم")
        elif animal_type == "سمان": req = get_quail_requirements("بياض" if "بياض" in production_type else "لاحم")
        elif animal_type == "أسماك": req = get_fish_requirements("البلطي النيلي", production_type)
        elif animal_type == "أرانب": req = get_rabbit_requirements(production_type)
        else: req = get_cattle_requirements("حليب_متوسط")
        return {"ME": req.SE * 41, "CP": req.CP, "DP": req.DP}
    except Exception:
        return {"ME": 3000.0, "CP": 18.0, "DP": 14.0}

def _diagnose_nlp_failure(me_vals, cp_vals, bounds, target_me, target_cp):
    lo = np.array([b[0] for b in bounds]); hi = np.array([b[1] for b in bounds])
    max_me = float(np.dot(me_vals, hi)) * 100
    max_cp = float(np.dot(cp_vals, hi)) * 100
    issues = []
    if max_me < target_me: issues.append(f"⚡ أقصى ME = {max_me:.0f} < {target_me:.0f}")
    if max_cp < target_cp: issues.append(f"🧬 أقصى CP = {max_cp:.2f}% < {target_cp:.2f}%")
    return {"issues": issues, "max_me": round(max_me, 1),
            "max_cp": round(max_cp, 2), "tips": ["➕ أضف طاقة", "➕ أضف بروتين"]}


# ═══════════════════════════════════════════════════════════════════════
# NLP محسّن
# ═══════════════════════════════════════════════════════════════════════

def nlp_optimize_feed(ingredient_names, ingredient_data, prices,
                       animal_type="أبقار", production_type="حليب_عالي",
                       target_me=None, target_cp=None, price_product=2.5,
                       max_per_ing=0.6, verbose=False):
    n = len(ingredient_names)
    if n < 2: return {"success": False, "message": "يلزم مكونان"}
    if not SCIPY_AVAILABLE or minimize is None:
        return {"success": False, "message": "SCIPY غير متوفرة"}
    req = _get_requirement_for_nlp(animal_type, production_type)
    if target_me is None: target_me = req["ME"]
    if target_cp is None: target_cp = req["CP"]
    me_vals = np.array([ingredient_data[i].get("SE", 0) * 41 for i in ingredient_names])
    cp_vals = np.array([ingredient_data[i].get("CP", 0) for i in ingredient_names])
    cost_vals = np.array([prices.get(i, 300.0) / 1000.0 for i in ingredient_names])
    MIN_USE = 0.005
    animal_limits = get_animal_limits(animal_type)
    bounds = []
    for ing in ingredient_names:
        lim = animal_limits.get(ing)
        if lim:
            lb = max(MIN_USE, lim[0] / 100.0); ub = min(max_per_ing, lim[1] / 100.0)
        else: lb, ub = MIN_USE, max_per_ing
        if lb > ub: lb = ub
        bounds.append((lb, ub))
    energy_idx = [i for i, ing in enumerate(ingredient_names)
                   if ingredient_data[ing].get("SE", 0) > 40
                   and ingredient_data[ing].get("CP", 0) < 20]
    protein_idx = [i for i, ing in enumerate(ingredient_names)
                    if ingredient_data[ing].get("CP", 0) >= 20]
    oils_idx = [i for i, ing in enumerate(ingredient_names)
                if ing in get_oil_ingredients()]
    oil_max = get_oil_standard(f"{animal_type}_{production_type}")["max"] / 100.0
    def objective(x):
        me = np.dot(me_vals, x); cp = np.dot(cp_vals, x)
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
                oil_row = [1.0 if i in oils_idx else 0.0 for i in range(n)]
                A_ub.append(oil_row); b_ub.append(oil_max)
            if energy_idx and protein_idx:
                bal_row = [0.0] * n
                for i in energy_idx: bal_row[i] = 1.0
                for i in protein_idx: bal_row[i] = -1.0
                A_ub.append([-x for x in bal_row]); b_ub.append(-0.10)
            lp_res = linprog(np.zeros(n), A_ub=A_ub, b_ub=b_ub,
                A_eq=[[1.0] * n], b_eq=[1.0], bounds=bounds, method='highs',
                options={'presolve': True, 'time_limit': 8})
            if lp_res.success:
                lp_warm = np.clip(lp_res.x, 0, None)
                s = lp_warm.sum()
                if s > 0: lp_warm = lp_warm / s
        except Exception: lp_warm = None
    def make_initial_points():
        pts = []
        if lp_warm is not None: pts.append(lp_warm.copy())
        pts.append(np.ones(n) / n)
        pts.append(np.eye(n)[int(np.argmin(cost_vals))])
        pts.append(np.eye(n)[int(np.argmax(cp_vals))])
        pts.append(np.eye(n)[int(np.argmax(me_vals))])
        if energy_idx and protein_idx:
            mix1 = np.zeros(n); e = energy_idx[0]; p = protein_idx[0]
            mix1[e] = 0.60; mix1[p] = 0.30
            others = [i for i in range(n) if i not in (e, p)]
            if others:
                for i in others: mix1[i] = 0.10 / len(others)
            pts.append(mix1)
        rng = np.random.RandomState(42)
        for _ in range(3):
            p_ = rng.rand(n); p_ /= p_.sum(); pts.append(p_)
        return pts
    relaxation_levels = [
        ("صارم 100%", 1.00, True), ("خفيف 97%", 0.97, True),
        ("مرن 95%", 0.95, True), ("مرن 92%", 0.92, True),
        ("مرن 90%", 0.90, True), ("مرن 85%", 0.85, True),
        ("مرن 80%", 0.80, True), ("طوارئ 70%", 0.70, False)]
    best = None; attempts_log = []
    for level_name, mult, enforce_balance in relaxation_levels:
        tme = target_me * mult; tcp = target_cp * mult
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},
            {'type': 'ineq', 'fun': lambda x, t=tme: np.dot(me_vals, x) - t/100.0},
            {'type': 'ineq', 'fun': lambda x, t=tcp: np.dot(cp_vals, x) - t/100.0}]
        if oils_idx:
            constraints.append({'type': 'ineq',
                'fun': lambda x: oil_max - sum(x[i] for i in oils_idx)})
        if enforce_balance and energy_idx and protein_idx:
            constraints.append({'type': 'ineq',
                'fun': lambda x: sum(x[i] for i in energy_idx) -
                                 sum(x[i] for i in protein_idx) - 0.05})
        for x0 in make_initial_points():
            x0 = np.clip(x0, [b[0] for b in bounds], [b[1] for b in bounds])
            s = x0.sum()
            if s <= 0: continue
            x0 = x0 / s
            try:
                res = minimize(objective, x0, method='SLSQP',
                    bounds=bounds, constraints=constraints,
                    options={'maxiter': 1000, 'ftol': 1e-8})
                if not res.success:
                    attempts_log.append((level_name, "SLSQP فشل", False)); continue
                x_norm = np.clip(res.x, 0, None); ss = x_norm.sum()
                if ss <= 0: continue
                x_norm = x_norm / ss
                actual_me = float(np.dot(me_vals, x_norm)) * 100
                actual_cp = float(np.dot(cp_vals, x_norm)) * 100
                if actual_me >= tme*0.98 and actual_cp >= tcp*0.98:
                    best = (res, x_norm, level_name, mult, actual_me, actual_cp)
                    attempts_log.append((level_name, "✅ نجح", True)); break
                else:
                    attempts_log.append((level_name,
                        f"قيود (ME={actual_me:.0f})", False))
            except Exception as e:
                attempts_log.append((level_name, f"استثناء: {e}", False)); continue
        if best: break
    if not best:
        for x0 in make_initial_points():
            try:
                x0 = np.clip(x0, [b[0] for b in bounds], [b[1] for b in bounds])
                s = x0.sum()
                if s <= 0: continue
                x0 = x0 / s
                res = minimize(objective_penalty, x0, method='SLSQP',
                    bounds=bounds, options={'maxiter': 3000, 'ftol': 1e-5})
                x_norm = np.clip(res.x, 0, None); ss = x_norm.sum()
                if ss <= 0: continue
                x_norm = x_norm / ss
                best = (res, x_norm, "عقوبات Penalty", 1.0,
                        float(np.dot(me_vals, x_norm))*100,
                        float(np.dot(cp_vals, x_norm))*100); break
            except Exception: continue
    if not best:
        diag = _diagnose_nlp_failure(me_vals, cp_vals, bounds, target_me, target_cp)
        return {"success": False, "message": "لا يوجد حل",
                "diagnosis": diag, "attempts_log": attempts_log[-20:],
                "animal_type": animal_type, "target_me": target_me,
                "target_cp": target_cp}
    res, x_opt, level_name, mult, actual_me, actual_cp = best
    x_pct = x_opt * 100.0
    formula = {name: round(float(x_pct[i]), 2) for i, name in
               enumerate(ingredient_names) if x_pct[i] > 0.05}
    final_cost = float(np.dot(cost_vals, x_opt))
    me_ratio = actual_me / target_me; cp_ratio = actual_cp / target_cp
    max_profit = float(price_product * (me_ratio * cp_ratio) - final_cost)
    warning = None
    if mult < 1.0:
        warning = (f"⚠️ خُففت القيود إلى {mult*100:.0f}%")
    if mult < 0.85: warning += "\n🟠 حل طوارئ"
    e_share = sum(formula.get(ing, 0) for i, ing in enumerate(ingredient_names)
                  if i in energy_idx)
    p_share = sum(formula.get(ing, 0) for i, ing in enumerate(ingredient_names)
                  if i in protein_idx)
    balance_note = None
    if p_share > e_share:
        balance_note = f"⚠️ بروتين ({p_share:.1f}%) > طاقة ({e_share:.1f}%)"
    final_warning = warning
    if balance_note:
        final_warning = (warning + "\n" + balance_note) if warning else balance_note
    return {"success": True, "formula": formula, "x_opt": x_opt.tolist(),
        "final_cost": final_cost, "final_me": actual_me, "final_cp": actual_cp,
        "target_me": float(target_me), "target_cp": float(target_cp),
        "max_profit": max_profit, "iterations": int(getattr(res, "nit", 0)),
        "strategy": level_name, "relaxation_mult": mult, "warning": final_warning,
        "animal_type": animal_type, "production_type": production_type,
        "attempts_log": attempts_log,
        "energy_share_pct": round(e_share, 1),
        "protein_share_pct": round(p_share, 1)}

def create_nlp_profit_curve(result, ingredient_names, ingredient_data, prices):
    if not PLOTLY_AVAILABLE: return None
    try:
        me_vals = np.array([ingredient_data[i].get("SE", 0) * 41 for i in ingredient_names])
        cp_vals = np.array([ingredient_data[i].get("CP", 0) for i in ingredient_names])
        cost_vals = np.array([prices.get(i, 300.0) / 1000.0 for i in ingredient_names])
        x_opt = np.array(result["x_opt"])
        prices_range = np.linspace(1.0, 5.0, 40); profits = []
        for p in prices_range:
            qv = (np.dot(me_vals, x_opt) / result["target_me"]) * \
                 (np.dot(cp_vals, x_opt) / result["target_cp"])
            profits.append(p * qv - np.dot(cost_vals, x_opt))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=prices_range, y=profits, mode='lines+markers',
            line=dict(color='#1b5e20', width=3), name='صافي العائد'))
        fig.add_hline(y=0, line_dash="dash", line_color="#c62828",
            annotation_text="التعادل")
        fig.update_layout(title="منحنى الربحية", height=420, paper_bgcolor='white')
        return fig
    except Exception: return None


# ═══════════════════════════════════════════════════════════════════════
# ✅ v11.11.0 — شريط القياس بأسهم دقيقة على الصورة
# ═══════════════════════════════════════════════════════════════════════

WEIGHT_TAPE_CONFIG = {
    "أبقار": {"hg_min":100.0,"hg_max":260.0,"hg_default":180.0,
        "bl_min":100.0,"bl_max":220.0,"bl_default":150.0,
        "hg_label":"محيط الصدر (سم)","bl_label":"طول الجسم (سم)",
        "hg_tip":"خلف الأرجل الأمامية مباشرة",
        "bl_tip":"من مقدمة الكتف إلى عظم الحوض",
        "source":"Schaeffer (1978)","accuracy":"±5%",
        "calc":lambda hg,bl: (hg**2*bl)/10840.0},
    "أغنام": {"hg_min":40.0,"hg_max":120.0,"hg_default":75.0,
        "bl_min":40.0,"bl_max":100.0,"bl_default":65.0,
        "hg_label":"محيط الصدر (سم)","bl_label":"طول الجسم (سم)",
        "hg_tip":"خلف الأرجل الأمامية","bl_tip":"من الكتف للحوض",
        "source":"Schaeffer (1978)","accuracy":"±7%",
        "calc":lambda hg,bl: (hg**2*bl)/10840.0},
    "ماعز": {"hg_min":35.0,"hg_max":110.0,"hg_default":70.0,
        "bl_min":35.0,"bl_max":95.0,"bl_default":62.0,
        "hg_label":"محيط الصدر (سم)","bl_label":"طول الجسم (سم)",
        "hg_tip":"خلف الأرجل الأمامية","bl_tip":"من الكتف للحوض",
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

# صور حقيقية للحيوانات
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
    """✅ v11.11.0 — صورة حيوان مع أسهم قياس دقيقة على الموضع الصحيح"""
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        from PIL import Image as _PILImage
        img_url = ANIMAL_PHOTOS.get(animal_type, ANIMAL_PHOTOS["أبقار"])
        img_bytes = _download_image(img_url)

        fig, ax = plt.subplots(figsize=(12, 7.5))
        
        img_loaded = False
        if img_bytes:
            try:
                img = _PILImage.open(io.BytesIO(img_bytes))
                ax.imshow(img)
                img_loaded = True
            except Exception:
                img_loaded = False
        
        if not img_loaded:
            ax.text(0.5, 0.5, f"📸 {animal_type}", ha='center', va='center',
                    fontsize=40, transform=ax.transAxes, color='#1b5e20',
                    fontweight='bold')
            ax.axis('off')

        # إحداثيات موضع الشريط لكل حيوان (نسبة من الصورة)
        TAPE_POSITIONS = {
            "أبقار":  {"girth_x": 0.42, "girth_y_top": 0.55, "girth_y_bot": 0.85,
                       "length_left": 0.25, "length_right": 0.85, "length_y": 0.30},
            "أغنام":  {"girth_x": 0.40, "girth_y_top": 0.50, "girth_y_bot": 0.85,
                       "length_left": 0.25, "length_right": 0.80, "length_y": 0.28},
            "ماعز":   {"girth_x": 0.42, "girth_y_top": 0.50, "girth_y_bot": 0.85,
                       "length_left": 0.25, "length_right": 0.80, "length_y": 0.28},
            "إبل":    {"girth_x": 0.40, "girth_y_top": 0.50, "girth_y_bot": 0.85,
                       "length_left": 0.22, "length_right": 0.82, "length_y": 0.28},
            "خيول":   {"girth_x": 0.42, "girth_y_top": 0.55, "girth_y_bot": 0.90,
                       "length_left": 0.22, "length_right": 0.85, "length_y": 0.28},
        }
        
        pos = TAPE_POSITIONS.get(animal_type, TAPE_POSITIONS["أبقار"])
        
        # شريط محيط الصدر (خط أحمر عمودي)
        ax.plot([pos["girth_x"], pos["girth_x"]],
                [pos["girth_y_top"], pos["girth_y_bot"]],
                color='#c62828', linewidth=5,
                transform=ax.transAxes, zorder=10,
                solid_capstyle='round')
        
        # سهم علوي
        ax.annotate('', xy=(pos["girth_x"], pos["girth_y_top"]),
                    xytext=(pos["girth_x"], pos["girth_y_top"] + 0.05),
                    xycoords='axes fraction', textcoords='axes fraction',
                    arrowprops=dict(arrowstyle='->', color='#c62828',
                                    lw=4, mutation_scale=25))
        
        # سهم سفلي
        ax.annotate('', xy=(pos["girth_x"], pos["girth_y_bot"]),
                    xytext=(pos["girth_x"], pos["girth_y_bot"] - 0.05),
                    xycoords='axes fraction', textcoords='axes fraction',
                    arrowprops=dict(arrowstyle='->', color='#c62828',
                                    lw=4, mutation_scale=25))
        
        # تسمية محيط الصدر
        ax.text(pos["girth_x"] + 0.05, pos["girth_y_top"] - 0.03,
                '① محيط الصدر', color='#c62828', fontweight='bold',
                fontsize=13, transform=ax.transAxes,
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                          edgecolor='#c62828', linewidth=2),
                zorder=11)

        # شريط طول الجسم (خط أزرق أفقي)
        ax.plot([pos["length_left"], pos["length_right"]],
                [pos["length_y"], pos["length_y"]],
                color='#1565c0', linewidth=5,
                transform=ax.transAxes, zorder=10,
                solid_capstyle='round')
        
        # سهم يسار
        ax.annotate('', xy=(pos["length_left"], pos["length_y"]),
                    xytext=(pos["length_left"] - 0.03, pos["length_y"]),
                    xycoords='axes fraction', textcoords='axes fraction',
                    arrowprops=dict(arrowstyle='->', color='#1565c0',
                                    lw=4, mutation_scale=25))
        
        # سهم يمين
        ax.annotate('', xy=(pos["length_right"], pos["length_y"]),
                    xytext=(pos["length_right"] + 0.03, pos["length_y"]),
                    xycoords='axes fraction', textcoords='axes fraction',
                    arrowprops=dict(arrowstyle='->', color='#1565c0',
                                    lw=4, mutation_scale=25))
        
        # تسمية طول الجسم
        mid_length = (pos["length_left"] + pos["length_right"]) / 2
        ax.text(mid_length, pos["length_y"] - 0.05,
                '② طول الجسم', color='#1565c0', fontweight='bold',
                fontsize=13, ha='center', transform=ax.transAxes,
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                          edgecolor='#1565c0', linewidth=2),
                zorder=11)

        # تعليمات أسفل الصورة
        cfg = WEIGHT_TAPE_CONFIG.get(animal_type, {})
        ax.text(0.5, 0.02,
            f"🔴 ① {cfg.get('hg_tip', '')}     🔵 ② {cfg.get('bl_tip', '')}",
            transform=ax.transAxes, ha='center', fontsize=11,
            color='#1a1a1a', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff8e1',
                      edgecolor='#d4af37', linewidth=2),
            zorder=12)

        ax.set_title(
            f"📍 طريقة القياس الصحيحة — {animal_type} | "
            f"{cfg.get('source', '')} | دقة {cfg.get('accuracy', '')}",
            fontsize=14, fontweight='bold', color='#1b5e20', pad=15)
        
        if img_loaded:
            ax.axis('off')
        else:
            ax.set_xlim(0, 1); ax.set_ylim(0, 1)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=130, bbox_inches='tight',
                    facecolor='white', pad_inches=0.15)
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
        if img: st.image(img.getvalue(), use_container_width=True)
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
# الدردشة والاستديو
# ═══════════════════════════════════════════════════════════════════════

CHAT_FILE = "tawor_chat_rooms.json"
STUDIO_FILE = "tawor_studio_content.json"

def _load_chat_rooms():
    try:
        if os.path.exists(CHAT_FILE):
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict): return data
    except Exception: pass
    return {"🌾 النقاش العام": [], "🧬 نقاش علمي": [], "💰 نقاش اقتصادي": []}

def _save_chat_rooms(data):
    try:
        tmp = CHAT_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, CHAT_FILE)
    except Exception: pass

def add_chat_message(room, user, message):
    msg = _sanitize_message(message); user = _sanitize_message(user, 40)
    if not msg or not user: return False
    rooms = _load_chat_rooms()
    rooms.setdefault(room, [])
    rooms[room].append({"user": user, "msg": msg,
        "ts": datetime.now().strftime("%H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "role": st.session_state.get("user_role", "guest")})
    rooms[room] = rooms[room][-500:]
    _save_chat_rooms(rooms); return True

def create_chat_room(room_name):
    rooms = _load_chat_rooms()
    name = _sanitize_message(room_name, 40)
    if name and name not in rooms:
        rooms[name] = []; _save_chat_rooms(rooms); return True
    return False

def _load_studio():
    try:
        if os.path.exists(STUDIO_FILE):
            with open(STUDIO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception: pass
    return {"videos": [], "slides": [], "notes": []}

def _save_studio(data):
    try:
        tmp = STUDIO_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, STUDIO_FILE)
    except Exception: pass


# ═══════════════════════════════════════════════════════════════════════
# الثوابت
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
SUPERVISOR_TITLE = "اختصاصي تغذية الحيوان"
PLATFORM_URL = "https://tawor-nology.streamlit.app"
WHATSAPP_NUMBER = "+249123533489"
OWNER_EMAIL = "abukram128@gmail.com"
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG"]
LOGO_OPTIONS = ["logo.png", "logo.jpg"]

st.set_page_config(page_title=f"{APP_NAME} | {APP_TAGLINE}", page_icon="🌾",
    layout="wide", initial_sidebar_state="collapsed")


# ═══════════════════════════════════════════════════════════════════════
# الخطوط
# ═══════════════════════════════════════════════════════════════════════

FONT_DIR = "fonts"; os.makedirs(FONT_DIR, exist_ok=True)

class ArabicFontManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls); cls._instance._init()
        return cls._instance
    def _init(self):
        self.font_name = 'Helvetica'; self.ready = False
        if not REPORTLAB_AVAILABLE: return
        paths = [os.path.join(FONT_DIR, "Amiri-Regular.ttf"),
                 "Amiri-Regular.ttf",
                 "/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        for p in paths:
            if os.path.exists(p) and self._register(p): return
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
            target = os.path.join(FONT_DIR, "Amiri-Regular.ttf")
            if not os.path.exists(target):
                import urllib.request
                urllib.request.urlretrieve(url, target)
            self._register(target)
        except Exception: pass
    def _register(self, path):
        try:
            pdfmetrics.registerFont(TTFont('TaworArabic', path))
            self.font_name = 'TaworArabic'; self.ready = True; return True
        except Exception: return False

font_mgr = ArabicFontManager()

@lru_cache(maxsize=1500)
def _ar_cached(text):
    if not text: return ""
    if not ARABIC_AVAILABLE: return str(text)
    try: return get_display(arabic_reshaper.reshape(str(text)), base_dir='R')
    except Exception: return str(text)

def ar(text): return _ar_cached(text)


# ═══════════════════════════════════════════════════════════════════════
# مكتبة الأعلاف (مختصرة — نفس v11.10.4)
# ═══════════════════════════════════════════════════════════════════════

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
            for name, data in cat.items(): lookup[name] = data
        _get_ingredient_lookup._cache = lookup
    return _get_ingredient_lookup._cache

def get_oil_ingredients():
    return BIG_FEEDS_LIBRARY.get("🌰 الزيوت النباتية والحيوانية", {})

def get_total_ingredient_count():
    return len(_get_ingredient_lookup())


MAX_OIL_PERCENTAGE = {
    "دواجن_بادي": {"max":8.0,"optimal":5.0,"source":"Ross 308"},
    "دواجن_نامي": {"max":7.0,"optimal":4.5,"source":"Ross 308"},
    "دواجن_ناهي": {"max":7.0,"optimal":4.0,"source":"Ross 308"},
    "دواجن_بياض": {"max":5.0,"optimal":2.5,"source":"NRC 1994"},
    "أبقار_حليب_عالي": {"max":6.0,"optimal":4.0,"source":"NRC 2001"},
    "أبقار_حليب_متوسط": {"max":5.0,"optimal":3.5,"source":"NRC 2001"},
    "أبقار_حليب_منخفض": {"max":5.0,"optimal":3.0,"source":"NRC 2001"},
    "أغنام_تسمين_مكثف": {"max":5.0,"optimal":3.5,"source":"NRC 2007"},
    "ماعز_حلابة_عالي": {"max":5.0,"optimal":3.5,"source":"NRC 2007"},
    "إبل_حليب": {"max":5.0,"optimal":3.5,"source":"FAO 2010"},
    "خيول_رياضة_مكثف": {"max":10.0,"optimal":7.0,"source":"NRC Horses"},
    "أسماك_بادئ": {"max":15.0,"optimal":10.0,"source":"NRC Fish"},
}

def get_oil_standard(k):
    return MAX_OIL_PERCENTAGE.get(k, {"max":5.0,"optimal":3.0,"source":"عام"})

INGREDIENT_LIMITS_BY_ANIMAL = {
"دواجن": {"يوريا علفية":(0,0),"نخالة قمح (ردة)":(0,10),"نخالة ذرة":(0,5),
    "تبن قمح":(0,2),"قش أرز":(0,2),"كسب بذور القطن":(0,5),"كسب السمسم":(0,8),
    "كسب الكانولا":(0,8),"ملح الطعام":(.2,.4),"الحجر الجيري":(.8,2),
    "فوسفات ثنائي الكالسيوم":(.5,2.5),"بريمكس تسمين دواجن":(.2,.35),
    "بريمكس بياض":(.2,.35),"ليسين نقي":(0,.5),"ميثيونين نقي":(0,.4)},
"أبقار": {"يوريا علفية":(0,1.5),"نخالة قمح (ردة)":(0,30),
    "كسب بذور القطن":(0,20),"كسب السمسم":(0,15),"ملح الطعام":(.3,.5),
    "بيكربونات الصوديوم":(.5,1),"الحجر الجيري":(0,3.5),
    "فوسفات ثنائي الكالسيوم":(0,2),"بريمكس أبقار":(.15,.3),
    "بريمكس مجترات":(.15,.3),"مضاد سموم فطرية":(.05,.15)},
"أغنام": {"يوريا علفية":(0,1),"نخالة قمح (ردة)":(0,25),
    "كسب بذور القطن":(0,15),"ملح الطعام":(.3,.5),
    "بيكربونات الصوديوم":(.5,1),"بريمكس مجترات":(.15,.3),
    "الحجر الجيري":(0,3),"فوسفات ثنائي الكالسيوم":(0,2)},
"ماعز": {"يوريا علفية":(0,1),"نخالة قمح (ردة)":(0,25),
    "ملح الطعام":(.3,.5),"بيكربونات الصوديوم":(.5,1),
    "بريمكس مجترات":(.15,.3),"الحجر الجيري":(0,3),
    "فوسفات ثنائي الكالسيوم":(0,2)},
"إبل": {"يوريا علفية":(0,1),"نخالة قمح (ردة)":(0,20),
    "ملح الطعام":(.3,.5),"بيكربونات الصوديوم":(.5,1),
    "بريمكس إبل":(.15,.3),"الحجر الجيري":(0,3),
    "فوسفات ثنائي الكالسيوم":(0,2)},
"خيول": {"يوريا علفية":(0,.5),"نخالة قمح (ردة)":(0,20),
    "ملح الطعام":(.3,.5),"بريمكس خيول":(.15,.3),
    "الحجر الجيري":(0,2.5),"فوسفات ثنائي الكالسيوم":(0,2)},
"أسماك": {"يوريا علفية":(0,0),"نخالة قمح (ردة)":(0,10),
    "ملح الطعام":(0,.3),"بريمكس أسماك":(.15,.3),
    "الحجر الجيري":(0,2),"فوسفات ثنائي الكالسيوم":(0,2)},
"أرانب": {"يوريا علفية":(0,.5),"نخالة قمح (ردة)":(0,20),
    "ملح الطعام":(.3,.5),"بريمكس مجترات":(.15,.3),
    "الحجر الجيري":(0,2.5),"فوسفات ثنائي الكالسيوم":(0,2)},
}

def get_animal_limits(animal):
    return INGREDIENT_LIMITS_BY_ANIMAL.get(animal, {})


# ═══════════════════════════════════════════════════════════════════════
# الاحتياجات الغذائية
# ═══════════════════════════════════════════════════════════════════════

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
            "أبقار حلابة عالية", f"حليب {milk_yield}")
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
            "تسمين مكثف", "ADG >1.3")
    if t == "تسمين_عادي":
        return AnimalRequirement(9.5, 12, 65, 38, 24, 4, 7.5, .55, .32,
            "تسمين عادي", "ADG ~0.8")
    if t == "حمل_أخير":
        return AnimalRequirement(11.5, 14.5, 67, 35, 22, 4.2, 8, .7, .42,
            "حمل آخر", "شهر 7-9")
    return AnimalRequirement(7.5, 10, 53, 45, 28, 3, 8.5, .42, .26,
        "أبقار صيانة", "بدون إنتاج")

def get_sheep_requirements(t, is_male=True, weight_kg=50.0, litter_size=1):
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
        return AnimalRequirement(round(dp,2), round(dp/.72,2),
            round(60 + (litter_size-1)*5, 1), 30, 19, 4.5, 8.5,
            round(.65 + (litter_size-1)*.1, 3),
            round(.38 + (litter_size-1)*.05, 3),
            f"نعاج مرضعات ({litter_size})", "")
    if t == "حامل_أخير":
        return AnimalRequirement(10.5, 13.5, 62, 32, 20, 3.8, 8, .6, .35,
            "نعاج حامل (4-5)", "")
    if t == "حامل_متوسط":
        return AnimalRequirement(8.5, 11, 55, 38, 24, 3.4, 8, .5, .3,
            "نعاج حامل (1-3)", "")
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
            f"عنزات حلابة ({milk_yield})", "")
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
            "إبل نمو", f"{weight_kg}")
    if t == "تسمين":
        return AnimalRequirement(9.5, 12, 65, 35, 22, 4.5, 7.5, .6, .35,
            "إبل تسمين", f"{weight_kg}")
    if t == "حليب":
        dp = min(10.5 + milk_yield * 0.20, 14.0)
        return AnimalRequirement(round(dp,2), round(dp/.72,2),
            round(62 + milk_yield*.4, 1), 32, 20, 5, 8.5,
            round(.7 + milk_yield*.006, 3), round(.4 + milk_yield*.003, 3),
            f"إبل حلابة ({milk_yield})", "")
    if t == "سباق":
        return AnimalRequirement(14, 17, 72, 28, 17, 6, 9, .85, .5,
            "إبل سباق", "طاقة عالية")
    return AnimalRequirement(7, 9, 48, 48, 30, 3.5, 9, .42, .26,
        "إبل صيانة", f"{weight_kg}")

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
            return AnimalRequirement(20, 23, 76, 8, 4, 5, 6.5, 1, .5, "بادي", "")
        if age_weeks <= 3:
            return AnimalRequirement(18.5, 21, 74, 9, 5, 5, 6, .9, .45, "نامي", "")
        if age_weeks <= 5:
            return AnimalRequirement(17, 19.5, 75, 10, 5.5, 4.5, 6, .87, .43, "ناهي", "")
        return AnimalRequirement(16.5, 19, 75, 10, 5.5, 4.5, 6, .85, .42, "ناهي+", "")
    if age_weeks <= 6:
        return AnimalRequirement(17, 20, 72, 10, 5.5, 4, 7, 1, .5, "بادي بياض", "")
    if age_weeks <= 18:
        return AnimalRequirement(14.5, 17, 70, 12, 6.5, 4, 9, 1.5, .45, "نامي بياض", "")
    return AnimalRequirement(15.5, 18, 72, 11, 6, 4.2, 11.5, 3.8, .45, "بياض", "")

def get_quail_requirements(strain, age_weeks=1):
    if strain == "بياض":
        return AnimalRequirement(15, 18, 68, 11, 5.5, 4.5, 9, 2.5, .45, "سمان بياض", "")
    if age_weeks <= 2:
        return AnimalRequirement(20.5, 24, 74, 8, 4, 5.5, 6.5, 1, .55, "سمان بادي", "")
    if age_weeks <= 4:
        return AnimalRequirement(18.5, 22, 72, 9, 4.5, 5, 6, .9, .5, "سمان نامي", "")
    return AnimalRequirement(17, 20, 70, 10, 5, 4.5, 6, .85, .45, "سمان ناهي", "")

def get_fish_requirements(species, stage):
    if "بادئ" in stage or "زريعة" in stage:
        return AnimalRequirement(32, 40, 72, 8, 4, 10, 11, 1.5, .9, f"{species} بادئ", "")
    if "نمو" in stage:
        return AnimalRequirement(25, 32, 70, 12, 6, 8, 9, 1, .7, f"{species} نمو", "")
    return AnimalRequirement(22, 28, 68, 13, 7, 8, 9.5, .9, .65, f"{species} تسمين", "")

def get_rabbit_requirements(t, weight_kg=4.0):
    if t == "تسمين":
        return AnimalRequirement(15, 17, 65, 25, 15, 3, 8, .7, .35, "أرانب تسمين", "ADG 40")
    if t == "حليب":
        return AnimalRequirement(18, 20, 68, 25, 15, 4, 8.5, .85, .45, "أرانب حلابة", "أمهات")
    return AnimalRequirement(12, 14, 60, 30, 20, 2.5, 8.5, .6, .3, "أرانب صيانة", "")

def requirement_to_standard(req):
    return {"CP": req.CP, "DP": req.DP, "SE": req.SE, "NDF": req.NDF,
            "ADF": req.ADF, "EE": req.EE, "ASH": req.ASH,
            "Ca": req.Ca, "P": req.P}


# ═══════════════════════════════════════════════════════════════════════
# الحسابات
# ═══════════════════════════════════════════════════════════════════════

def compute_formula_nutrients(formula):
    totals = {k: 0.0 for k in ["CP","DP","SE","NDF","ADF","EE","ASH",
                                "Ca","P","Lys","Met"]}
    lookup = _get_ingredient_lookup()
    for ing, pct in formula.items():
        if ing not in lookup: continue
        d = lookup[ing]; f = pct / 100.0
        for k in totals:
            if k == "DP": totals[k] += f * d.get("CP", 0) * d.get("DC", 0)
            else: totals[k] += f * d.get(k, 0)
    return totals

def compute_total_oil_percentage(formula):
    oils = set(get_oil_ingredients().keys())
    return sum(p for i, p in formula.items() if i in oils)

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
    if is_poultry and targets.get("Lys"): weights["Lys"] = 0.05
    if is_poultry and targets.get("Met"): weights["Met"] = 0.05
    total_w, weighted = 0.0, 0.0
    for nut, w in weights.items():
        if not targets.get(nut): continue
        diff_pct = abs(actual.get(nut, 0) - targets[nut]) / targets[nut] * 100
        ev = evaluate_difference(diff_pct, standard_value=targets[nut])
        weighted += ev["score"] * w; total_w += w
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
        weighted += rs * 0.10; total_w += 0.10
    return (weighted / total_w if total_w else 0.0), actual

def get_default_selections(animal_type, production_type, requirement=None):
    d = {"ملح الطعام", "مضاد سموم فطرية"}
    if animal_type != "دواجن":
        d |= {"الحجر الجيري", "فوسفات ثنائي الكالسيوم"}
    if animal_type in ("أبقار", "أغنام", "ماعز", "إبل"): d.add("بيكربونات الصوديوم")
    if animal_type in ("دواجن", "سمان"):
        d.add("بريمكس بياض" if "بياض" in str(production_type) else "بريمكس تسمين دواجن")
    elif animal_type == "أبقار": d.add("بريمكس أبقار")
    elif animal_type in ("أغنام", "ماعز", "أرانب"): d.add("بريمكس مجترات")
    elif animal_type == "خيول": d.add("بريمكس خيول")
    elif animal_type == "إبل": d.add("بريمكس إبل")
    elif animal_type == "أسماك": d.add("بريمكس أسماك")
    return d

def _normalize_ingredient_name(name):
    name = re.sub(r'\s+', ' ', str(name).strip())
    lookup = _get_ingredient_lookup()
    if name in lookup: return name
    for lib in lookup.keys():
        if lib.lower() in name.lower() or name.lower() in lib.lower(): return lib
    kw = {"ذره":"ذرة صفراء","ذرة":"ذرة صفراء","صويا":"كسب فول صويا 44%",
          "شعير":"شعير مطحون","قمح":"قمح محلي","نخاله":"نخالة قمح (ردة)",
          "نخالة":"نخالة قمح (ردة)","ملح":"ملح الطعام","حجر":"الحجر الجيري",
          "فوسفات":"فوسفات ثنائي الكالسيوم","يوريا":"يوريا علفية"}
    for k, v in kw.items():
        if k in name.lower(): return v
    return name


def auto_formulate_smart(available_ingredients, prices, custom_standard,
                          standard_key="", basis="DP", min_quality=70.0,
                          animal_type="", production_type=""):
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
    rows = {}
    for nut in ["CP","SE","NDF","ADF","EE","ASH","Ca","P","Lys","Met"]:
        rows[nut] = [ing_data[i].get(nut, 0) for i in valid]
    rows["DP"] = [ing_data[i].get("CP",0) * ing_data[i].get("DC",0) for i in valid]
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
        lb = max(MIN_USE, lim[0]); ub = min(60.0, lim[1])
        if lb > ub: lb = ub
        bounds.append((lb, ub))
    energy_sources_idx = [i for i, ing in enumerate(valid)
                           if ing_data[ing].get("SE", 0) > 40
                           and ing_data[ing].get("CP", 0) < 20]
    protein_sources_idx = [i for i, ing in enumerate(valid)
                            if ing_data[ing].get("CP", 0) >= 20]
    A_eq_base = [[1.0] * n, rows[target_key]]
    b_eq_base = [100.0, target_protein * 100.0]
    A_ub_base, b_ub_base = [], []
    target_me = (target_se * 41) if target_se > 0 else 2500
    if target_me > 0:
        A_ub_base.append([-x * 41 for x in rows["SE"]])
        b_ub_base.append(-target_me * 0.90)
    if energy_sources_idx and protein_sources_idx:
        balance_row = [0.0] * n
        for i in energy_sources_idx: balance_row[i] = 1.0
        for i in protein_sources_idx: balance_row[i] = -1.0
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
        if is_poultry: ca_p_min, ca_p_max = 1.5, 2.2
        elif is_ruminant: ca_p_min, ca_p_max = 1.4, 2.5
        else: ca_p_min, ca_p_max = 1.5, 2.0
        A_ub_base.append([-rows["Ca"][i] + ca_p_min * rows["P"][i] for i in range(n)])
        b_ub_base.append(0)
        A_ub_base.append([rows["Ca"][i] - ca_p_max * rows["P"][i] for i in range(n)])
        b_ub_base.append(0)
    if target_se > 0:
        A_ub_base.append([-x for x in rows["SE"]])
        b_ub_base.append(-target_se * 0.92 * 100.0)
    if target_ndf > 0:
        if is_ruminant:
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
        A_ub_base.append(oil_ind); b_ub_base.append(oil_std["max"] * 100.0)
    strategies = [("دقيق 100%", 1.00), ("مرن 97%", 0.97),
        ("مرن 95%", 0.95), ("مرن 92%", 0.92), ("مرن 90%", 0.90),
        ("مرن 85%", 0.85), ("مرن 80%", 0.80), ("طوارئ قصوى", 0.75)]
    best, best_q = None, 0.0
    attempts = []
    for label, mult in strategies:
        try:
            A_eq = list(A_eq_base); b_eq = [100.0, target_protein * 100.0 * mult]
            A_ub = list(A_ub_base); b_ub = list(b_ub_base)
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                bounds=bounds, method='highs',
                options={'presolve': True, 'time_limit': 15})
            if res.success:
                formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.01}
                q, actual = evaluate_quality_weighted(formula, custom_standard,
                    animal_type, basis)
                if q > best_q:
                    best_q = q
                    best = {"success": True, "formula": formula,
                        "cost": res.fun / 100.0, "actual_nutrients": actual,
                        "quality_score": q, "strategy": label,
                        "meets_standard": q >= min_quality,
                        "targets": custom_standard, "basis": basis,
                        "oil_std": oil_std,
                        "total_oil": compute_total_oil_percentage(formula)}
                attempts.append(f"✅ {label}: {q:.1f}%")
                if q >= 92: break
            else: attempts.append(f"❌ {label}")
        except Exception as e:
            attempts.append(f"⚠️ {label}: {e}"); continue
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
    q, actual = evaluate_quality_weighted(fallback_formula, custom_standard,
                                           animal_type, basis)
    return {"success": True, "formula": fallback_formula,
        "cost": sum(fallback_formula[ing] / 100 *
                    prices.get(ing, 300) for ing in fallback_formula),
        "actual_nutrients": actual, "quality_score": q,
        "strategy": "🆘 طوارئ", "meets_standard": q >= min_quality,
        "targets": custom_standard, "basis": basis, "oil_std": oil_std,
        "total_oil": compute_total_oil_percentage(fallback_formula),
        "warning": f"⚠️ حل طوارئ — جودة {q:.1f}%",
        "attempts_log": attempts}


def _parse_ingredients_from_text(full_text):
    if not full_text: return {}
    fixes = {'٥':'5','٦':'6','٧':'7','٨':'8','٩':'9','٠':'0','١':'1',
             '٢':'2','٣':'3','٤':'4'}
    text = full_text
    for old, new in fixes.items(): text = text.replace(old, new)
    text = text.replace('٪', '%')
    lookup = _get_ingredient_lookup()
    all_names = sorted(lookup.keys(), key=len, reverse=True)
    ingredients = {}
    for line in text.split('\n'):
        line = line.strip()
        if len(line) < 3: continue
        matched_any = False
        for ing_name in all_names:
            if ing_name in line:
                idx = line.find(ing_name) + len(ing_name)
                remainder = line[idx:].strip()
                num_match = re.search(
                    r'[:\-=:\.\s]*(\d{1,3}\.?\d{0,2})\s*(?:%|كجم|كج|kg|جرام|g)?',
                    remainder)
                if num_match:
                    try:
                        val = float(num_match.group(1))
                        if 0.01 <= val <= 100:
                            ingredients[ing_name] = round(val, 2)
                            matched_any = True; break
                    except ValueError: continue
        if not matched_any:
            kw_match = re.search(r'(\d{1,3}\.?\d{0,2})\s*%?', line)
            if kw_match:
                try: val = float(kw_match.group(1))
                except ValueError: continue
                if 0.01 <= val <= 100:
                    name_part = line[:kw_match.start()].strip()
                    name_part = re.sub(r'[:\-=:\.\s]+$', '', name_part)
                    if len(name_part) > 2:
                        matched = match_ingredient_name(name_part)
                        if matched:
                            ingredients[matched] = round(val, 2)
    return ingredients


def match_ingredient_name(text):
    if not text: return None
    tl = text.strip().lower()
    lookup = _get_ingredient_lookup()
    for name in lookup.keys():
        if name.lower() == tl: return name
    best_match = None; best_len = 0
    for name in lookup.keys():
        if name.lower() in tl and len(name) > best_len:
            best_match = name; best_len = len(name)
    if best_match: return best_match
    kw = {"ذرة":"ذرة صفراء","ذره":"ذرة صفراء","صويا":"كسب فول صويا 44%",
          "شعير":"شعير مطحون","قمح":"قمح محلي","نخالة":"نخالة قمح (ردة)",
          "نخاله":"نخالة قمح (ردة)","ملح":"ملح الطعام","حجر":"الحجر الجيري",
          "فوسفات":"فوسفات ثنائي الكالسيوم","يوريا":"يوريا علفية"}
    for k, v in kw.items():
        if k in tl: return v
    return None


def analyze_existing_formula(formula, animal_type, production_type):
    if not formula or sum(formula.values()) <= 0:
        return {"success": False, "message": "التركيبة فارغة"}
    total = sum(formula.values())
    normalized = {k: round(v / total * 100, 2) for k, v in formula.items()}
    try:
        if animal_type == "أبقار": req = get_cattle_requirements(production_type)
        elif animal_type == "أغنام": req = get_sheep_requirements(production_type, is_male=True)
        elif animal_type == "ماعز": req = get_goat_requirements(production_type, is_male=False)
        elif animal_type == "إبل": req = get_camel_requirements(production_type)
        elif animal_type == "خيول": req = get_horse_requirements(production_type)
        elif animal_type == "دواجن": req = get_poultry_requirements("بياض" if "بياض" in production_type else "لاحم")
        elif animal_type == "سمان": req = get_quail_requirements("بياض" if "بياض" in production_type else "لاحم")
        elif animal_type == "أسماك": req = get_fish_requirements("البلطي النيلي", production_type)
        elif animal_type == "أرانب": req = get_rabbit_requirements(production_type)
        else: return {"success": False, "message": "حيوان غير مدعوم"}
    except Exception as e:
        return {"success": False, "message": f"خطأ: {e}"}
    standard = requirement_to_standard(req)
    actual = compute_formula_nutrients(normalized)
    labels = {"CP": "بروتين خام", "DP": "بروتين مهضوم",
              "SE": "طاقة SE", "NDF": "NDF", "ADF": "ADF",
              "EE": "دهن", "ASH": "رماد", "Ca": "Ca", "P": "P",
              "Lys": "Lys", "Met": "Met"}
    comparison = []
    for k, sv in standard.items():
        if sv == 0: continue
        cv = actual.get(k, 0)
        diff = cv - sv
        pct = (diff / sv * 100) if sv else 0
        ev = evaluate_difference(pct, standard_value=sv)
        comparison.append({"key": k, "العنصر": labels.get(k, k),
            "المعيار": sv, "المحسوب": cv, "الفرق": diff,
            "الفرق %": pct, "التقييم": ev["label"], "score": ev["score"]})
    quality, _ = evaluate_quality_weighted(normalized, standard, animal_type)
    ca = actual.get("Ca", 0); p = actual.get("P", 0)
    ca_p = ca / p if p > 0 else 0
    lookup = _get_ingredient_lookup()
    energy_ings = [ing for ing in normalized if
                   lookup.get(ing, {}).get("SE", 0) > 40 and
                   lookup.get(ing, {}).get("CP", 0) < 20]
    protein_ings = [ing for ing in normalized if
                    lookup.get(ing, {}).get("CP", 0) >= 20]
    energy_share = sum(normalized[ing] for ing in energy_ings)
    protein_share = sum(normalized[ing] for ing in protein_ings)
    cost = sum(normalized.get(ing, 0) / 100 *
               lookup.get(ing, {}).get("price", 300) for ing in normalized)
    refs = get_references(animal_type, production_type)
    return {"success": True, "formula": normalized, "original": dict(formula),
        "standard": standard, "actual": actual, "comparison": comparison,
        "quality_score": quality, "ca_p_ratio": ca_p,
        "energy_share_pct": round(energy_share, 1),
        "protein_share_pct": round(protein_share, 1),
        "cost_per_ton": round(cost, 2),
        "requirement_name": req.name_ar, "requirement_note": req.note,
        "animal_type": animal_type, "production_type": production_type,
        "references": refs,
        "total_oil": compute_total_oil_percentage(normalized)}


MILK_REPLACER_STANDARDS = {
    "عجول (Calves)": {"CP":24,"Fat":20,"Lactose":45,"Ca":.85,"P":.7,
        "Lys":2.2,"Met":.65,"source":"NRC Dairy Cattle","Ca_P_optimal":(1.2,1.5)},
    "حملان (Lambs)": {"CP":24,"Fat":24,"Lactose":40,"Ca":.9,"P":.7,
        "Lys":2.4,"Met":.7,"source":"NRC Small Ruminants","Ca_P_optimal":(1.2,1.6)},
    "جديان (Goat Kids)": {"CP":24,"Fat":24,"Lactose":42,"Ca":.9,"P":.7,
        "Lys":2.3,"Met":.7,"source":"NRC Small Ruminants","Ca_P_optimal":(1.2,1.6)},
    "إبل (Camels)": {"CP":26,"Fat":28,"Lactose":38,"Ca":.95,"P":.75,
        "Lys":2.5,"Met":.8,"source":"FAO Camel","Ca_P_optimal":(1.2,1.5)},
    "أمهار (Foals)": {"CP":22,"Fat":18,"Lactose":48,"Ca":1.0,"P":.8,
        "Lys":2.1,"Met":.6,"source":"NRC Horses","Ca_P_optimal":(1.2,1.4)},
}

MILK_REPLACER_INGREDIENTS = {
    "حليب مجفف منزوع الدسم": {"CP":34,"Fat":1,"Lactose":52,"Ca":1.3,"P":1,
        "Lys":2.7,"Met":.9,"price":3200,"max":60,"type":"بروتين"},
    "حليب مجفف كامل الدسم": {"CP":26,"Fat":28,"Lactose":38,"Ca":.95,"P":.75,
        "Lys":2.1,"Met":.65,"price":3800,"max":70,"type":"بروتين+دهن"},
    "شرش حليب مجفف": {"CP":12,"Fat":1.5,"Lactose":75,"Ca":.9,"P":.75,
        "Lys":.9,"Met":.2,"price":1800,"max":35,"type":"كربوهيدرات"},
    "بروتين شرش WPC 80%": {"CP":80,"Fat":5,"Lactose":8,"Ca":.5,"P":.3,
        "Lys":7.5,"Met":1.6,"price":8500,"max":25,"type":"بروتين"},
    "مركز بروتين صويا": {"CP":66,"Fat":1,"Lactose":0,"Ca":.2,"P":.8,
        "Lys":4.2,"Met":.9,"price":2800,"max":15,"type":"نباتي"},
    "زيت جوز الهند": {"CP":0,"Fat":100,"Lactose":0,"Ca":0,"P":0,
        "Lys":0,"Met":0,"price":2200,"max":15,"type":"دهن"},
    "زيت النخيل": {"CP":0,"Fat":100,"Lactose":0,"Ca":0,"P":0,
        "Lys":0,"Met":0,"price":1200,"max":15,"type":"دهن"},
    "لاكتوز نقي": {"CP":0,"Fat":0,"Lactose":100,"Ca":0,"P":0,
        "Lys":0,"Met":0,"price":1400,"max":25,"type":"كربوهيدرات"},
    "ليسين L-Lysine": {"CP":94,"Fat":0,"Lactose":0,"Ca":0,"P":0,
        "Lys":94,"Met":0,"price":4200,"max":1,"type":"أميني"},
    "ميثيونين": {"CP":58,"Fat":0,"Lactose":0,"Ca":0,"P":0,
        "Lys":0,"Met":58,"price":5800,"max":.8,"type":"أميني"},
    "بريمكس فيتامينات": {"CP":0,"Fat":0,"Lactose":0,"Ca":5,"P":3,
        "Lys":0,"Met":0,"price":6500,"max":1,"type":"بريمكس"},
    "كالسيوم كربونات": {"CP":0,"Fat":0,"Lactose":0,"Ca":38,"P":0,
        "Lys":0,"Met":0,"price":200,"max":2.5,"type":"معدن"},
    "فوسفات ثنائي الكالسيوم": {"CP":0,"Fat":0,"Lactose":0,"Ca":23,"P":18,
        "Lys":0,"Met":0,"price":1100,"max":2.5,"type":"معدن"},
    "ملح طعام": {"CP":0,"Fat":0,"Lactose":0,"Ca":0,"P":0,
        "Lys":0,"Met":0,"price":150,"max":.5,"type":"معدن"},
}

def formulate_milk_replacer(animal, volume=100.0, selected=None):
    if not SCIPY_AVAILABLE: return {"success": False, "message": "SCIPY غير متوفرة"}
    std = MILK_REPLACER_STANDARDS.get(animal)
    if not std: return {"success": False, "message": "حيوان غير مدعوم"}
    valid = [i for i in (selected or list(MILK_REPLACER_INGREDIENTS.keys()))
             if i in MILK_REPLACER_INGREDIENTS]
    n = len(valid)
    if n < 3: return {"success": False, "message": "اختر 3 مكونات على الأقل"}
    min_util_by_count = {3:0.40,4:0.50,5:0.60,6:0.65,7:0.70,8:0.75}
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
    strategies = []
    s1_ub = [(lac,std["Lactose"]*1.15*100),([-x for x in lac],-std["Lactose"]*0.85*100),
        ([-x for x in lys],-std["Lys"]*0.70*100),([-x for x in met],-std["Met"]*0.70*100),
        ([-x for x in ca],-std["Ca"]*0.85*100),([-x for x in p],-std["P"]*0.85*100)]
    strategies.append(("S1",[[1]*n,cp,fat],[100,std["CP"]*100,std["Fat"]*100],
        [u for u,_ in s1_ub],[b for _,b in s1_ub]))
    s2_ub = s1_ub[:2] + s1_ub[4:]
    strategies.append(("S2",[[1]*n,cp,fat],[100,std["CP"]*100,std["Fat"]*100],
        [u for u,_ in s2_ub],[b for _,b in s2_ub]))
    s3_ub = [(cp,std["CP"]*1.05*100),([-x for x in cp],-std["CP"]*0.95*100),
             (fat,std["Fat"]*1.05*100),([-x for x in fat],-std["Fat"]*0.95*100)]
    strategies.append(("S3",[[1]*n],[100],[u for u,_ in s3_ub],[b for _,b in s3_ub]))
    s4_ub = [(cp,std["CP"]*1.15*100),([-x for x in cp],-std["CP"]*0.85*100),
             (fat,std["Fat"]*1.30*100),([-x for x in fat],-std["Fat"]*0.50*100)]
    strategies.append(("S4",[[1]*n],[100],[u for u,_ in s4_ub],[b for _,b in s4_ub]))
    best = None; best_effective = 0.0
    for label, A_eq, b_eq, A_ub, b_ub in strategies:
        try:
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                bounds=base_bounds, method='highs',
                options={'presolve':True,'time_limit':10})
            if not res.success: continue
            formula = {valid[i]: res.x[i] for i in range(n) if res.x[i] > 0.001}
            used = sum(1 for v in formula.values() if v > 0.5)
            used_pct = used / n * 100
            actual = {k: 0.0 for k in ["CP","Fat","Lactose","Ca","P","Lys","Met"]}
            for ing, pct in formula.items():
                d = MILK_REPLACER_INGREDIENTS[ing]
                for k in actual: actual[k] += pct / 100 * d.get(k, 0)
            scores = []
            for k in ["CP","Fat","Lactose","Ca","P","Lys","Met"]:
                t = std.get(k, 0)
                if t <= 0: continue
                diff = abs(actual[k] - t) / t * 100
                if diff <= 2: scores.append(100)
                elif diff <= 5: scores.append(92)
                elif diff <= 10: scores.append(78)
                elif diff <= 15: scores.append(62)
                elif diff <= 25: scores.append(45)
                else: scores.append(max(0, 100 - diff))
            ca_p = actual["Ca"] / actual["P"] if actual["P"] > 0 else 0
            cp_min, cp_max = std.get("Ca_P_optimal", (1.2, 1.5))
            if cp_min <= ca_p <= cp_max: scores.append(100)
            elif cp_min*0.8 <= ca_p <= cp_max*1.3: scores.append(75)
            else: scores.append(30)
            quality = sum(scores) / len(scores) if scores else 0
            util_factor = 1.0 if used_pct >= min_util*100 else used_pct / (min_util*100)
            effective = quality * (0.7 + 0.3 * util_factor)
            if effective > best_effective:
                best_effective = effective
                best = {"formula": formula, "cost": res.fun / 100,
                    "cost_per_kg": res.fun / 10000, "used_count": used,
                    "used_pct": used_pct, "actual": actual,
                    "quality_score": quality, "ca_p_ratio": ca_p,
                    "strategy": label}
            if quality >= 90 and used_pct >= min_util * 100: break
        except Exception: continue
    if not best: return {"success": False, "message": "لا يوجد حل"}
    warning = None
    if best["used_pct"] < min_util * 100:
        warning = (f"⚠️ تم استخدام {best['used_count']}/{n}")
    return {"success": True, "formula": best["formula"],
        "cost_per_100kg": best["cost"], "cost_per_kg": best["cost_per_kg"],
        "standard": std, "actual": best["actual"], "animal": animal,
        "volume": volume, "used_count": best["used_count"],
        "used_pct": best["used_pct"], "quality_score": best["quality_score"],
        "ca_p_ratio": best["ca_p_ratio"], "strategy": best["strategy"],
        "warning": warning,
        "targets": {k: std.get(k, 0) for k in
                    ["CP","Fat","Lactose","Ca","P","Lys","Met"]}}

# ═══════════════════════════════════════════════════════════════════════
# نهاية PART 1 — أرسل "تابع" لـ PART 2
# ═══════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════
# [تكملة PART 1] — OCR + الرسوم + PDF + الموافقة + الفيديو + 3D
# ═══════════════════════════════════════════════════════════════════════

# ═══ OCR ═══
def _preprocess_image_variants(img):
    variants = []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    variants.append(clahe.apply(gray))
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(otsu)
    variants.append(cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 15, 5))
    variants.append(cv2.fastNlMeansDenoising(clahe.apply(gray), None, 10, 7, 21))
    variants.append(cv2.bitwise_not(gray))
    return variants

def _extract_with_confidence(image):
    try:
        data = pytesseract.image_to_data(image, lang='ara+eng',
            output_type=pytesseract.Output.DICT, config=r'--oem 3 --psm 6')
        good_lines = []; current_line = []; current_y = None
        for i, word in enumerate(data['text']):
            if int(data['conf'][i]) < 30: continue
            word = word.strip()
            if not word: continue
            y = data['top'][i]
            if current_y is None: current_y = y
            if abs(y - current_y) > 15:
                if current_line: good_lines.append(' '.join(current_line))
                current_line = [word]; current_y = y
            else: current_line.append(word)
        if current_line: good_lines.append(' '.join(current_line))
        return '\n'.join(good_lines), len(good_lines)
    except Exception: return "", 0

def extract_ingredients_from_image(image_bytes):
    if not OCR_AVAILABLE:
        return {"success": False, "message": "pytesseract غير مثبتة"}
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None: return {"success": False, "message": "تعذر قراءة الصورة"}
        h, w = img.shape[:2]
        if max(h, w) < 1500:
            scale = 1800 / max(h, w)
            img = cv2.resize(img, None, fx=scale, fy=scale,
                interpolation=cv2.INTER_CUBIC)
        variants = _preprocess_image_variants(img)
        best_text, best_score, all_texts = "", 0, []
        for variant in variants:
            try:
                txt, score = _extract_with_confidence(variant)
                if score > best_score: best_score, best_text = score, txt
                if txt and len(txt) > 5: all_texts.append(txt)
            except Exception: continue
        if not all_texts:
            return {"success": False, "message": "لم يتم استخراج نص"}
        full_text = "\n".join(set(all_texts))
        ingredients = _parse_ingredients_from_text(full_text)
        return {"success": True, "ingredients": ingredients,
            "raw_text": full_text, "best_text": best_text,
            "count": len(ingredients), "total": sum(ingredients.values()),
            "quality": "جيد" if best_score > 3 else "ضعيف"}
    except Exception as e:
        return {"success": False, "message": f"خطأ: {e}"}

def render_ocr_correction_ui(ingredients):
    st.markdown("### ✏️ تصحيح يدوي")
    corrected = {}
    all_names = sorted(_get_ingredient_lookup().keys())
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
            if keep and new_pct > 0: corrected[new_name] = new_pct
    return corrected


# ═══ الرسوم البيانية ═══
def create_colorful_bar_chart(standard, actual, keys=None):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        if keys is None: keys = ["CP","DP","SE","NDF","ADF","EE","ASH"]
        nuts = [n for n in keys if n in standard and standard[n] > 0]
        if not nuts: return None
        fig, ax = plt.subplots(figsize=(9, 4.5))
        x = np.arange(len(nuts)); width = 0.35
        b1 = ax.bar(x-width/2, [standard[n] for n in nuts], width, label='المعيار',
            color='#1976d2', edgecolor='#0d47a1', linewidth=1.5)
        b2 = ax.bar(x+width/2, [actual.get(n,0) for n in nuts], width,
            label='المحسوب', color='#43a047', edgecolor='#1b5e20', linewidth=1.5)
        for bar in b1:
            hh = bar.get_height()
            if hh > 0: ax.text(bar.get_x()+bar.get_width()/2, hh, f'{hh:.1f}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
        for bar in b2:
            hh = bar.get_height()
            if hh > 0: ax.text(bar.get_x()+bar.get_width()/2, hh, f'{hh:.1f}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
        ax.set_title('مقارنة العناصر', fontsize=13, fontweight='bold', color='#1b5e20')
        ax.set_xticks(x); ax.set_xticklabels(nuts)
        ax.legend(loc='upper right'); ax.grid(axis='y', alpha=0.3)
        ax.set_facecolor('#fafafa')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_colorful_pie_chart(formula):
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2: return None
    try:
        colors = ['#e53935','#8e24aa','#3949ab','#1e88e5','#00897b',
                  '#43a047','#7cb342','#fdd835','#fb8c00','#6d4c41']
        names = list(formula.keys()); vals = list(formula.values())
        fig, ax = plt.subplots(figsize=(8, 5))
        _, _, autotexts = ax.pie(vals, autopct='%1.1f%%', colors=colors[:len(names)],
            startangle=90, pctdistance=0.75, wedgeprops=dict(edgecolor='white', linewidth=2))
        for t in autotexts: t.set_color('white'); t.set_fontweight('bold'); t.set_fontsize(9)
        ax.legend(names, loc='center left', bbox_to_anchor=(1,0,0.5,1), fontsize=9)
        ax.set_title('توزيع المكونات', fontsize=13, fontweight='bold', color='#1b5e20')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_radar_chart(standard, actual, keys=None):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        if keys is None: keys = ["CP","DP","SE","NDF","ADF","EE","Ca","P"]
        nuts = [n for n in keys if n in standard and standard[n] > 0]
        if len(nuts) < 3: return None
        std_norm = [100.0] * len(nuts)
        act_norm = [(actual.get(n, 0) / standard[n]) * 100 for n in nuts]
        angles = np.linspace(0, 2*np.pi, len(nuts), endpoint=False).tolist()
        std_norm += std_norm[:1]; act_norm += act_norm[:1]; angles += angles[:1]
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, std_norm, 'o-', linewidth=2.5, color='#1976d2', label='المعيار')
        ax.fill(angles, std_norm, alpha=0.15, color='#1976d2')
        ax.plot(angles, act_norm, 'o-', linewidth=2.5, color='#43a047', label='المحسوب')
        ax.fill(angles, act_norm, alpha=0.25, color='#43a047')
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(nuts)
        ax.set_title('المقارنة %', fontweight='bold', color='#1b5e20', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3,1.1))
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_gauge_chart(score):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(aspect='equal'))
        colors = ['#c62828','#ef6c00','#f9a825','#7cb342','#43a047','#1b5e20']
        for i, c in enumerate(colors):
            t1 = 180 - (i * 30); t2 = 180 - ((i + 1) * 30)
            ax.add_patch(Wedge((0,0), 1, t2, t1, width=0.3, facecolor=c,
                edgecolor='white', linewidth=2))
        angle = 180 - (score / 100) * 180; rad = np.radians(angle)
        ax.plot([0, 0.85*np.cos(rad)], [0, 0.85*np.sin(rad)],
            color='#1a1a1a', linewidth=3, zorder=10)
        ax.add_patch(Circle((0,0), 0.08, color='#1a1a1a', zorder=11))
        ax.text(0, -0.25, f'{score:.0f}%', ha='center', fontsize=20,
            fontweight='bold', color='#1b5e20')
        ax.set_xlim(-1.2, 1.2); ax.set_ylim(-0.7, 1.2); ax.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_ca_p_ratio_chart(ca, p, target_ca=0, target_p=0):
    if not MATPLOTLIB_AVAILABLE or p <= 0: return None
    try:
        ratio = ca / p
        fig, ax = plt.subplots(figsize=(8, 3))
        zones = [(0,.8,'#b71c1c'),(.8,1.2,'#ef6c00'),(1.2,1.5,'#f9a825'),
                 (1.5,2.0,'#2e7d32'),(2.0,3.0,'#f9a825'),(3.0,5.0,'#ef6c00'),(5.0,8.0,'#b71c1c')]
        for x0, x1, c in zones: ax.axvspan(x0, x1, alpha=0.35, color=c)
        ratio_clipped = min(ratio, 7.9)
        ax.axvline(ratio_clipped, color='#0d47a1', linewidth=4, zorder=10)
        ax.text(ratio_clipped, 0.85, f'{ratio:.2f}', ha='center', fontsize=18,
            fontweight='bold', color='#0d47a1',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                edgecolor='#0d47a1', linewidth=2))
        ax.set_xlim(0, 8); ax.set_ylim(0, 1.2); ax.set_yticks([])
        ax.set_title(f'⚖️ Ca:P — Ca={ca:.2f}% | P={p:.2f}%',
            fontweight='bold', color='#1b5e20')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_quality_breakdown_chart(rows):
    if not MATPLOTLIB_AVAILABLE or not rows: return None
    try:
        labels = [r["العنصر"] for r in rows[:9]]
        scores = [r.get("score", 50) for r in rows[:9]]
        colors = []
        for s in scores:
            if s >= 95: colors.append('#1b5e20')
            elif s >= 85: colors.append('#43a047')
            elif s >= 70: colors.append('#7cb342')
            elif s >= 55: colors.append('#f9a825')
            else: colors.append('#c62828')
        fig, ax = plt.subplots(figsize=(9, 4))
        bars = ax.bar(labels, scores, color=colors, edgecolor='#333')
        for bar in bars:
            hh = bar.get_height()
            ax.text(bar.get_x()+bar.get_width()/2, hh, f'{hh:.0f}',
                ha='center', va='bottom', fontweight='bold')
        ax.axhline(y=70, color='#c62828', linestyle='--', linewidth=2, label='حد 70%')
        ax.set_ylim(0, 105); ax.set_title('تقييم العناصر', fontweight='bold', color='#1b5e20')
        ax.legend(loc='lower right'); ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=30, ha='right')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None


# ═══════════════════════════════════════════════════════════════════════
# PDF Generator
# ═══════════════════════════════════════════════════════════════════════

class PDFGenerator:
    def __init__(self):
        self.font_name = font_mgr.font_name
        self.logo_path = None
        for lp in LOGO_OPTIONS + PHOTO_OPTIONS:
            if os.path.exists(lp): self.logo_path = lp; break

    def _ar(self, t):
        if t is None: return ""
        try: return get_display(arabic_reshaper.reshape(str(t)), base_dir='R')
        except Exception: return str(t)

    def _draw_page(self, canvas_obj, doc):
        try:
            canvas_obj.saveState(); w, h = doc.pagesize
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, h-90, w, 90, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.rect(0, h-95, w, 5, fill=1, stroke=0)
            canvas_obj.setFillColor(white); canvas_obj.setFont(self.font_name, 22)
            canvas_obj.drawCentredString(w/2, h-38, self._ar("تاور نولجي  Tawor Nology"))
            canvas_obj.setFont(self.font_name, 12)
            canvas_obj.setFillColor(HexColor('#e8f5e9'))
            canvas_obj.drawCentredString(w/2, h-58, self._ar("للإنتاج الحيواني وتغذية الحيوان"))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.drawCentredString(w/2, h-76, self._ar(f"إشراف: {SUPERVISOR}"))
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, 42, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.rect(0, 84, w, 3, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#ffeb3b'))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.drawCentredString(w/2, 68, self._ar(f"🤲 {DUA_SHORT} 🤲"))
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(white); canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(w/2, 27, self._ar("تاور نولجي © 2026"))
            canvas_obj.setFont(self.font_name, 7)
            canvas_obj.drawCentredString(w/2, 12,
                self._ar(f"صفحة {canvas_obj.getPageNumber()}"))
            canvas_obj.restoreState()
        except Exception: pass

    def _add_references_page(self, story, animal_type, production_type):
        try:
            refs = get_references(animal_type, production_type)
            eqs = get_reference_equations(animal_type, production_type)
            story.append(PageBreak())
            story.append(Paragraph(self._ar("📚 المراجع والمعادلات"),
                ParagraphStyle('rt', fontName=self.font_name, fontSize=16,
                    alignment=TA_CENTER, textColor=HexColor('#1b5e20'), spaceAfter=15)))
            story.append(Paragraph(self._ar(f"📖 المرجع: {refs['primary']}"),
                ParagraphStyle('rp', fontName=self.font_name, fontSize=11,
                    alignment=TA_RIGHT, textColor=HexColor('#0d47a1'),
                    spaceAfter=8, leading=16)))
            if refs.get("table"):
                story.append(Paragraph(self._ar(f"📑 الجدول: {refs['table']}"),
                    ParagraphStyle('rt2', fontName=self.font_name, fontSize=10,
                        alignment=TA_RIGHT, textColor=HexColor('#1565c0'),
                        spaceAfter=8, leading=14)))
            if eqs:
                story.append(Spacer(1, 10))
                story.append(Paragraph(self._ar("📐 المعادلات المرجعية:"),
                    ParagraphStyle('eqt', fontName=self.font_name, fontSize=12,
                        alignment=TA_RIGHT, textColor=HexColor('#2e7d32'),
                        spaceAfter=8)))
                eq_data = [[self._ar("المؤشر"), self._ar("المعادلة")]]
                for k, v in eqs.items():
                    if k in ("source", "example"): continue
                    eq_data.append([self._ar(k), self._ar(v)])
                if len(eq_data) > 1:
                    et = Table(eq_data, colWidths=[100, 390])
                    et.setStyle(TableStyle([
                        ('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),
                        ('TEXTCOLOR',(0,0),(-1,0),white),
                        ('BOX',(0,0),(-1,-1),1.5,HexColor('#2e7d32')),
                        ('ALIGN',(0,0),(-1,-1),'RIGHT'),
                        ('FONTNAME',(0,0),(-1,-1),self.font_name),
                        ('FONTSIZE',(0,0),(-1,-1),9),
                        ('PADDING',(0,0),(-1,-1),5)]))
                    story.append(et)
                if eqs.get("example"):
                    story.append(Spacer(1, 8))
                    story.append(Paragraph(self._ar(f"💡 مثال: {eqs['example']}"),
                        ParagraphStyle('ex', fontName=self.font_name, fontSize=10,
                            alignment=TA_RIGHT, textColor=HexColor('#c62828'))))
            if refs.get("secondary"):
                story.append(Spacer(1, 12))
                story.append(Paragraph(self._ar("📚 مراجع داعمة:"),
                    ParagraphStyle('rst', fontName=self.font_name, fontSize=11,
                        alignment=TA_RIGHT, textColor=HexColor('#2e7d32'),
                        spaceAfter=6)))
                for sec in refs["secondary"]:
                    story.append(Paragraph(self._ar(f"• {sec}"),
                        ParagraphStyle('rs', fontName=self.font_name, fontSize=10,
                            alignment=TA_RIGHT, spaceAfter=4, leading=14)))
            story.append(Spacer(1, 15))
            story.append(HRFlowable(width="100%", thickness=1.5, color=HexColor('#d4af37')))
            story.append(Spacer(1, 10))
            story.append(Paragraph(self._ar("📖 مراجع عامة:"),
                ParagraphStyle('rg', fontName=self.font_name, fontSize=11,
                    alignment=TA_RIGHT, textColor=HexColor('#1b5e20'), spaceAfter=8)))
            for i, ref in enumerate(GENERAL_REFERENCES, 1):
                story.append(Paragraph(f"{i}. {ref}",
                    ParagraphStyle('rli', fontName='Helvetica', fontSize=9,
                        alignment=TA_LEFT, spaceAfter=4, leading=12, leftIndent=10)))
        except Exception as e:
            story.append(Paragraph(f"خطأ: {e}",
                ParagraphStyle('err', fontName=self.font_name, fontSize=9,
                    alignment=TA_RIGHT, textColor=HexColor('#c62828'))))

    def _comparison_table(self, std, calc):
        labels = {"CP":"بروتين","DP":"مهضوم","SE":"SE","NDF":"NDF",
                  "ADF":"ADF","EE":"دهن","ASH":"رماد","Ca":"Ca","P":"P"}
        data = [[self._ar(x) for x in ["العنصر","المعيار","المحسوب","الفرق","%","التقييم"]]]
        cmds = [('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),
                ('TEXTCOLOR',(0,0),(-1,0),white),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('FONTNAME',(0,0),(-1,-1),self.font_name),
                ('FONTSIZE',(0,0),(-1,-1),9),
                ('GRID',(0,0),(-1,-1),1,HexColor('#9e9e9e')),
                ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]
        row = 1
        for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
            if k not in std or std[k] == 0: continue
            sv, cv = std[k], calc.get(k, 0); diff = cv - sv
            pct = (diff / sv * 100) if sv else 0
            ev = evaluate_difference(pct, standard_value=sv)
            data.append([self._ar(labels[k]), f"{sv:.2f}", f"{cv:.2f}",
                f"{diff:+.3f}", f"{pct:+.2f}%", self._ar(ev["label"])])
            cmds.append(('BACKGROUND',(0,row),(-1,row),HexColor(ev["bg"])))
            row += 1
        t = Table(data, colWidths=[100,70,70,70,70,105])
        t.setStyle(TableStyle(cmds))
        return t

    def generate_report(self, formula, requirement, animal_type, breed, cost,
                         city, local_cost, local_sym, requester_name="",
                         protein_basis="DP", standard_key="",
                         include_charts=True, quality_score=0.0):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
            leftMargin=40, topMargin=115, bottomMargin=145)
        story = []
        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text), ParagraphStyle('s',
                fontName=self.font_name, fontSize=size, alignment=align,
                textColor=HexColor(color), spaceAfter=6, leading=size*1.6))
        story.append(P("تقرير فني رسمي", size=20, align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))
        client = [[self._ar("👤 طالب:"), self._ar(requester_name or "—")],
            [self._ar("🐾 الفصيل:"), self._ar(f"{animal_type} — {breed}")],
            [self._ar("🧬 الأساس:"), self._ar(protein_basis)],
            [self._ar("📅 التاريخ:"), datetime.now().strftime('%Y-%m-%d')]]
        ct = Table(client, colWidths=[150, 340])
        ct.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(0,-1),HexColor('#e8f5e9')),
            ('BOX',(0,0),(-1,-1),1.5,HexColor('#2e7d32')),
            ('INNERGRID',(0,0),(-1,-1),0.6,HexColor('#c8e6c9')),
            ('ALIGN',(0,0),(-1,-1),'RIGHT'),
            ('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),11),
            ('PADDING',(0,0),(-1,-1),9)]))
        story.append(ct); story.append(Spacer(1, 15))
        std_vals = requirement_to_standard(requirement)
        calc_vals = compute_formula_nutrients(formula)
        qd = [[self._ar("الجودة"), self._ar("الحالة"), self._ar("70%")],
              [f"{quality_score:.1f}%",
               self._ar("✅ ناجح" if quality_score >= 70 else "⚠️ يحتاج"),
               self._ar("✅" if quality_score >= 70 else "❌")]]
        qt = Table(qd, colWidths=[130, 200, 160])
        qt.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#1565c0')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('BACKGROUND',(0,1),(-1,-1),
             HexColor('#e8f5e9' if quality_score >= 70 else '#ffebee')),
            ('GRID',(0,0),(-1,-1),1,HexColor('#1976d2')),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),self.font_name)]))
        story.append(qt); story.append(Spacer(1, 15))
        story.append(P("📊 مقارنة العناصر", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        story.append(self._comparison_table(std_vals, calc_vals))
        if include_charts:
            story.append(Spacer(1, 15))
            for chart_fn, args in [(create_colorful_bar_chart,(std_vals, calc_vals)),
                                    (create_colorful_pie_chart,(formula,)),
                                    (create_radar_chart,(std_vals, calc_vals))]:
                try:
                    c = chart_fn(*args)
                    if c:
                        story.append(RLImage(c, width=450, height=250))
                        story.append(Spacer(1, 10))
                except Exception: pass
        story.append(PageBreak())
        story.append(P("💰 التكاليف", size=14, color='#1b5e20'))
        cost_data = [[self._ar("البند"), self._ar("القيمة")],
            [self._ar("التكلفة/طن"), f"${cost:.2f}"]]
        tc = Table(cost_data, colWidths=[280, 210])
        tc.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('GRID',(0,0),(-1,-1),1,HexColor('#2e7d32')),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),self.font_name)]))
        story.append(tc); story.append(Spacer(1, 18))
        if formula:
            story.append(P("🌾 المكونات للطن", size=14, color='#1b5e20'))
            ing_data = [[self._ar("المكون"), self._ar("%"), self._ar("كجم/طن")]]
            for ing, pct in formula.items():
                ing_data.append([self._ar(ing), f"{pct:.2f}%", f"{pct*10:.1f}"])
            ti = Table(ing_data, colWidths=[270, 110, 110])
            ti.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),
                ('TEXTCOLOR',(0,0),(-1,0),white),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('FONTNAME',(0,0),(-1,-1),self.font_name),
                ('GRID',(0,0),(-1,-1),1,HexColor('#bdbdbd')),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),
                 [HexColor('#ffffff'), HexColor('#f5f5f5')])]))
            story.append(ti); story.append(Spacer(1, 25))
        try:
            self._add_references_page(story, animal_type, standard_key or breed)
        except Exception: pass
        doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
        buffer.seek(0); return buffer.getvalue()

    def generate_ocr_report(self, ingredients, nutrients, raw_text=""):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
            leftMargin=40, topMargin=115, bottomMargin=145)
        story = []
        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(self._ar(text), ParagraphStyle('s',
                fontName=self.font_name, fontSize=size, alignment=align,
                textColor=HexColor(color), spaceAfter=6, leading=size*1.6))
        story.append(P("تقرير تحليل OCR", size=20, align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
        data = [[self._ar("المادة"), self._ar("%")]]
        for k, v in ingredients.items(): data.append([self._ar(k), f"{v:.2f}%"])
        data.append([self._ar("الإجمالي"), f"{sum(ingredients.values()):.2f}%"])
        t = Table(data, colWidths=[300, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('GRID',(0,0),(-1,-1),1,HexColor('#bdbdbd')),
            ('BACKGROUND',(0,-1),(-1,-1),HexColor('#ffe0b2'))]))
        story.append(t)
        doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
        buffer.seek(0); return buffer.getvalue()

pdf_gen = PDFGenerator()


def generate_nlp_math_pdf(result, animal_type, production_type,
                            nlp_sel, ing_data, nlp_prices):
    if not REPORTLAB_AVAILABLE: return None
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
            leftMargin=40, topMargin=115, bottomMargin=145)
        story = []
        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(ar(text), ParagraphStyle('s',
                fontName=font_mgr.font_name, fontSize=size,
                alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size*1.6))
        story.append(P("تقرير التحسين غير الخطي (NLP)",
            size=20, align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))
        info = [
            [ar("الحيوان"), ar(animal_type)],
            [ar("الحالة"), ar(production_type)],
            [ar("الاستراتيجية"), ar(result.get("strategy", "—"))],
            [ar("التكلفة"), f"${result['final_cost']:.4f}/كجم"],
            [ar("الطاقة"), f"{result['final_me']:.0f} kcal/kg"],
            [ar("البروتين"), f"{result['final_cp']:.2f}%"],
            [ar("صافي الربح"), f"${result['max_profit']:.4f}"]]
        t = Table(info, colWidths=[160, 330])
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(0,-1),HexColor('#e8f5e9')),
            ('BOX',(0,0),(-1,-1),1.5,HexColor('#2e7d32')),
            ('ALIGN',(0,0),(-1,-1),'RIGHT'),
            ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
            ('PADDING',(0,0),(-1,-1),6)]))
        story.append(t); story.append(Spacer(1, 15))
        story.append(P("📐 المعادلات", size=14, color='#1565c0'))
        story.append(Spacer(1, 8))
        nlp_eq = REFERENCE_EQUATIONS.get("معادلة_التركيب_NLP", {})
        eq_data = [[ar("البند"), ar("القيمة")]]
        for k, v in nlp_eq.items():
            if k == "source": continue
            eq_data.append([ar(k), ar(v)])
        et = Table(eq_data, colWidths=[130, 360])
        et.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#1565c0')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('ALIGN',(0,0),(-1,-1),'RIGHT'),
            ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
            ('GRID',(0,0),(-1,-1),0.6,HexColor('#bbdefb')),
            ('FONTSIZE',(0,0),(-1,-1),9),
            ('PADDING',(0,0),(-1,-1),6)]))
        story.append(et)
        story.append(PageBreak())
        story.append(P("🌾 التركيبة", size=16, color='#1b5e20'))
        ing_pdf = [[ar("المكوّن"), ar("%"), ar("كجم/طن")]]
        for ing, pct in result["formula"].items():
            ing_pdf.append([ar(ing), f"{pct:.2f}%", f"{pct*10:.1f}"])
        it = Table(ing_pdf, colWidths=[280, 110, 110])
        it.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
            ('GRID',(0,0),(-1,-1),0.8,HexColor('#bdbdbd'))]))
        story.append(it)
        story.append(PageBreak())
        story.append(P("📈 الرسوم", size=16, color='#1b5e20'))
        story.append(Spacer(1, 10))
        try:
            actual = compute_formula_nutrients(result["formula"])
            nlp_req = _get_requirement_for_nlp(animal_type, production_type)
            std_c = {"ME/100": nlp_req["ME"]/100, "CP": nlp_req["CP"],
                      "DP": nlp_req["DP"]}
            act_c = {"ME/100": actual.get("SE", 0)*41/100,
                      "CP": actual.get("CP", 0), "DP": actual.get("DP", 0)}
            bf = create_colorful_bar_chart(std_c, act_c)
            if bf:
                story.append(RLImage(bf, width=470, height=250))
                story.append(P("1️⃣ مقارنة ME/CP/DP",
                    size=9, align=TA_CENTER, color='#555'))
                story.append(Spacer(1, 8))
        except Exception: pass
        try:
            pf = create_colorful_pie_chart(result["formula"])
            if pf:
                story.append(RLImage(pf, width=380, height=240))
                story.append(P("2️⃣ التوزيع",
                    size=9, align=TA_CENTER, color='#555'))
        except Exception: pass
        try:
            pdf_gen._add_references_page(story, animal_type, production_type)
        except Exception: pass
        story.append(Spacer(1, 20))
        story.append(P(SUPERVISOR, size=16, align=TA_CENTER, color='#c62828'))
        story.append(P(SUPERVISOR_TITLE, size=11, align=TA_CENTER, color='#1b5e20'))
        doc.build(story, onFirstPage=pdf_gen._draw_page,
            onLaterPages=pdf_gen._draw_page)
        buffer.seek(0); return buffer.getvalue()
    except Exception as e:
        st.error(f"⚠️ {e}"); return None


def generate_milk_replacer_pdf(result):
    if not REPORTLAB_AVAILABLE: return None
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
            leftMargin=40, topMargin=115, bottomMargin=145)
        story = []
        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(ar(text), ParagraphStyle('s', fontName=font_mgr.font_name,
                fontSize=size, alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size*1.6))
        std = result["standard"]; quality = result["quality_score"]
        formula = result["formula"]; volume = result.get("volume", 100.0)
        story.append(P("تقرير بديل الحليب", size=20, align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
        info = [[ar("الحيوان:"), ar(result["animal"])],
            [ar("المرجع:"), ar(std.get("source", ""))],
            [ar("الجودة:"), f"{quality:.1f}%"],
            [ar("الكمية:"), f"{volume:.0f} كجم"]]
        ct = Table(info, colWidths=[160, 330])
        ct.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(0,-1),HexColor('#e3f2fd')),
            ('BOX',(0,0),(-1,-1),1.5,HexColor('#1565c0')),
            ('ALIGN',(0,0),(-1,-1),'RIGHT'),
            ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
            ('PADDING',(0,0),(-1,-1),7)]))
        story.append(ct); story.append(Spacer(1, 15))
        story.append(P("🍼 المكونات", size=14, color='#1b5e20'))
        ing_data = [[ar("المكون"), ar("%"), ar("كجم")]]
        for ing, pct in formula.items():
            kg = pct * volume / 100
            ing_data.append([ar(ing), f"{pct:.2f}%", f"{kg:.2f}"])
        it = Table(ing_data, colWidths=[200, 130, 130])
        it.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
            ('GRID',(0,0),(-1,-1),0.8,HexColor('#bdbdbd'))]))
        story.append(it)
        try:
            pdf_gen._add_references_page(story, "عجول", "حليب")
        except Exception: pass
        story.append(P(SUPERVISOR, size=16, align=TA_CENTER, color='#c62828'))
        story.append(P(SUPERVISOR_TITLE, size=11, align=TA_CENTER, color='#1b5e20'))
        doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
        buffer.seek(0); return buffer.getvalue()
    except Exception: return None


def generate_lab_pdf(result, ctx):
    if not REPORTLAB_AVAILABLE: return None
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
            leftMargin=40, topMargin=115, bottomMargin=145)
        story = []
        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(ar(text), ParagraphStyle('s', fontName=font_mgr.font_name,
                fontSize=size, alignment=align, textColor=HexColor(color),
                spaceAfter=6, leading=size*1.6))
        story.append(P("تقرير تحليل تركيبة", size=18, align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
        info = [[ar("الحيوان"), ar(ctx.get("animal", "—"))],
            [ar("الإنتاج"), ar(ctx.get("production", "—"))],
            [ar("الجودة"), ar(f"{result['quality_score']:.1f}%")],
            [ar("Ca:P"), ar(f"{result['ca_p_ratio']:.2f}")],
            [ar("التكلفة"), ar(f"${result['cost_per_ton']:.2f}")],
            [ar("التاريخ"), ar(datetime.now().strftime("%Y-%m-%d %H:%M"))]]
        t = Table(info, colWidths=[160, 330])
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(0,-1),HexColor('#e8f5e9')),
            ('BOX',(0,0),(-1,-1),1.5,HexColor('#2e7d32')),
            ('ALIGN',(0,0),(-1,-1),'RIGHT'),
            ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
            ('PADDING',(0,0),(-1,-1),6)]))
        story.append(t); story.append(Spacer(1, 15))
        story.append(P("📊 المقارنة", size=14, color='#1b5e20'))
        data = [[ar(x) for x in ["العنصر","المعيار","المحسوب","الفرق","%","التقييم"]]]
        cmds = [('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),
                ('TEXTCOLOR',(0,0),(-1,0),white),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
                ('GRID',(0,0),(-1,-1),0.8,HexColor('#9e9e9e'))]
        for i, c in enumerate(result["comparison"], 1):
            data.append([ar(c["العنصر"]), f"{c['المعيار']:.2f}",
                f"{c['المحسوب']:.2f}", f"{c['الفرق']:+.3f}",
                f"{c['الفرق %']:+.2f}%", ar(c["التقييم"])])
            bg = '#e8f5e9' if c["score"] >= 70 else '#ffebee' if c["score"] < 50 else '#fff8e1'
            cmds.append(('BACKGROUND',(0,i),(-1,i),HexColor(bg)))
        ct = Table(data, colWidths=[90,65,65,65,65,120])
        ct.setStyle(TableStyle(cmds))
        story.append(ct)
        story.append(PageBreak())
        story.append(P("📐 المعادلات المرجعية", size=14, color='#1565c0'))
        eqs = get_reference_equations(result["animal_type"], result["production_type"])
        if eqs:
            eq_data = [[ar("المؤشر"), ar("المعادلة")]]
            for k, v in eqs.items():
                if k in ("source", "example"): continue
                eq_data.append([ar(k), ar(v)])
            if len(eq_data) > 1:
                et = Table(eq_data, colWidths=[100, 390])
                et.setStyle(TableStyle([
                    ('BACKGROUND',(0,0),(-1,0),HexColor('#1565c0')),
                    ('TEXTCOLOR',(0,0),(-1,0),white),
                    ('ALIGN',(0,0),(-1,-1),'RIGHT'),
                    ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
                    ('FONTSIZE',(0,0),(-1,-1),9)]))
                story.append(et)
        try:
            pdf_gen._add_references_page(story, result["animal_type"],
                                           result["production_type"])
        except Exception: pass
        story.append(Spacer(1, 20))
        story.append(P(SUPERVISOR, size=16, align=TA_CENTER, color='#c62828'))
        story.append(P(SUPERVISOR_TITLE, size=11, align=TA_CENTER, color='#1b5e20'))
        doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
        buffer.seek(0); return buffer.getvalue()
    except Exception as e:
        st.error(f"⚠️ {e}"); return None


# ═══════════════════════════════════════════════════════════════════════
# ✅ v11.11.0 — نظام الموافقة على PDF
# ═══════════════════════════════════════════════════════════════════════

PDF_REQUESTS_FILE = "tawor_pdf_requests.json"
PDF_STORAGE_DIR = "pdf_storage"
os.makedirs(PDF_STORAGE_DIR, exist_ok=True)


def _load_pdf_requests() -> Dict:
    try:
        if os.path.exists(PDF_REQUESTS_FILE):
            with open(PDF_REQUESTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict): return data
    except Exception: pass
    return {"requests": []}


def _save_pdf_requests(data: Dict):
    try:
        tmp = PDF_REQUESTS_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, PDF_REQUESTS_FILE)
    except Exception: pass


def create_pdf_request(user_name: str, user_role: str,
                        pdf_bytes: bytes, doc_title: str,
                        doc_context: Dict = None) -> str:
    try:
        request_id = f"REQ_{datetime.now():%Y%m%d%H%M%S}_{random.randint(100, 999)}"
        pdf_path = os.path.join(PDF_STORAGE_DIR, f"{request_id}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        data = _load_pdf_requests()
        data["requests"].append({
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
        })
        data["requests"] = data["requests"][-200:]
        _save_pdf_requests(data)
        return request_id
    except Exception as e:
        return f"ERR_{e}"


def get_user_pending_request(user_name: str, doc_title: str) -> Optional[Dict]:
    data = _load_pdf_requests()
    for req in reversed(data["requests"]):
        if (req["user_name"] == user_name
                and req["doc_title"] == doc_title):
            return req
    return None


def approve_pdf_request(request_id: str):
    data = _load_pdf_requests()
    for req in data["requests"]:
        if req["id"] == request_id:
            req["status"] = "approved"
            req["reviewed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _save_pdf_requests(data)
            return True
    return False


def reject_pdf_request(request_id: str, reason: str = ""):
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
    except Exception: pass
    return None


# ═══ أزرار التواصل والاستشارة ═══

def render_consultation_buttons(key_suffix: str = ""):
    import urllib.parse
    st.markdown(f"""
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
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    wa_consult = f"https://wa.me/{WHATSAPP_NUMBER.replace('+', '').replace(' ', '')}?text="
    consult_msg = urllib.parse.quote(
        f"السلام عليكم دكتور عبدالقادر،\nأرغب في استشارة حول تركيبة علفية.\nالمنصة: {APP_NAME}")
    
    with col1:
        st.markdown(f"""
        <a href="{wa_consult}{consult_msg}" target="_blank"
           style="display:block; padding:14px; background:#25d366;
                  color:white; text-decoration:none; border-radius:10px;
                  text-align:center; font-weight:700; font-size:1rem;
                  border:2px solid #128c7e;">
            📱 استشارة واتساب
        </a>
        """, unsafe_allow_html=True)
    with col2:
        em_consult = (f"mailto:{OWNER_EMAIL}?subject="
                      + urllib.parse.quote("طلب استشارة - تاور نولجي")
                      + "&body=" + urllib.parse.quote(
                          "السلام عليكم دكتور عبدالقادر،\n\nأرغب في استشارة حول تركيبة علفية.\n\nجزاك الله خيراً"))
        st.markdown(f"""
        <a href="{em_consult}"
           style="display:block; padding:14px; background:#1565c0;
                  color:white; text-decoration:none; border-radius:10px;
                  text-align:center; font-weight:700; font-size:1rem;
                  border:2px solid #0d47a1;">
            ✉️ استشارة بريد
        </a>
        """, unsafe_allow_html=True)
    with col3:
        call_link = f"tel:{WHATSAPP_NUMBER}"
        st.markdown(f"""
        <a href="{call_link}"
           style="display:block; padding:14px; background:#c62828;
                  color:white; text-decoration:none; border-radius:10px;
                  text-align:center; font-weight:700; font-size:1rem;
                  border:2px solid #8e0000;">
            📞 اتصال مباشر
        </a>
        """, unsafe_allow_html=True)


def render_pdf_download_with_approval(
        pdf_bytes: bytes, file_name: str, doc_title: str,
        user_role: str, user_name: str = "",
        doc_context: Dict = None, key_suffix: str = ""):
    """عرض زر تحميل PDF مع نظام الموافقة"""
    
    if user_role == "owner":
        st.download_button(
            "📄 تحميل PDF (مالك)", pdf_bytes,
            file_name=file_name, mime="application/pdf",
            use_container_width=True, type="primary",
            key=f"pdf_direct_{key_suffix}")
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
                    "📄 تحميل PDF (موافق عليه)", pdf_data,
                    file_name=file_name, mime="application/pdf",
                    use_container_width=True, type="primary",
                    key=f"pdf_approved_{key_suffix}")
            else:
                st.error("⚠️ الملف غير متوفر — أعد طلب الموافقة")
        elif status == "pending":
            st.warning(
                f"⏳ طلبك قيد المراجعة من المالك\n"
                f"رقم الطلب: `{existing['id']}`\n"
                f"تاريخ الطلب: {existing['created_at']}")
            st.info("💡 سيتم إعلامك عند الموافقة. يمكنك أيضاً التواصل مباشرة مع الدكتور")
        elif status == "rejected":
            st.error(
                f"❌ تم رفض طلبك\n"
                f"السبب: {existing.get('rejection_reason', 'غير محدد')}")
            if st.button("🔄 إعادة طلب الموافقة",
                    use_container_width=True,
                    key=f"pdf_req_retry_{key_suffix}"):
                rid = create_pdf_request(
                    user_name, user_role, pdf_bytes,
                    doc_title, doc_context)
                if rid.startswith("REQ_"):
                    st.success(f"✅ تم إرسال طلب جديد: {rid}")
                    st.rerun()
    else:
        st.info("🔒 تحميل PDF يتطلب موافقة المالك\nاضغط على الزر لطلب الموافقة")
        if st.button("📤 طلب موافقة على تحميل PDF",
                type="primary", use_container_width=True,
                key=f"pdf_req_new_{key_suffix}"):
            rid = create_pdf_request(
                user_name, user_role, pdf_bytes,
                doc_title, doc_context)
            if rid.startswith("REQ_"):
                st.success(f"✅ تم إرسال الطلب: {rid}\nسيتم المراجعة قريباً")
                st.rerun()
            else:
                st.error(f"❌ فشل الطلب: {rid}")
    
    st.markdown("---")
    render_consultation_buttons(key_suffix)


def render_pdf_requests_admin():
    """إدارة طلبات الموافقة — للمالك فقط"""
    st.markdown('<div class="section-title">📋 إدارة طلبات PDF</div>',
        unsafe_allow_html=True)
    
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
    tab1, tab2, tab3 = st.tabs([
        f"⏳ قيد المراجعة ({len(pending)})",
        f"✅ موافق عليها ({len(approved)})",
        f"❌ مرفوضة ({len(rejected)})"])
    
    with tab1:
        if not pending:
            st.info("💡 لا توجد طلبات معلقة")
        else:
            for req in reversed(pending):
                with st.expander(
                        f"📄 {req['doc_title']} — {req['user_name']} "
                        f"({req['user_role']}) — {req['created_at']}"):
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
                        st.download_button(
                            "👁️ معاينة PDF", pdf_preview,
                            file_name=f"{req['id']}_preview.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"preview_{req['id']}")
                    ac1, ac2 = st.columns(2)
                    with ac1:
                        if st.button("✅ موافقة",
                                type="primary",
                                use_container_width=True,
                                key=f"approve_{req['id']}"):
                            if approve_pdf_request(req["id"]):
                                st.success("✅ تمت الموافقة")
                                st.rerun()
                    with ac2:
                        if st.button("❌ رفض",
                                use_container_width=True,
                                key=f"reject_{req['id']}"):
                            st.session_state[
                                f"show_reject_{req['id']}"] = True
                    if st.session_state.get(f"show_reject_{req['id']}"):
                        reason = st.text_input(
                            "سبب الرفض:",
                            key=f"reject_reason_{req['id']}")
                        if st.button("تأكيد الرفض",
                                key=f"confirm_reject_{req['id']}"):
                            if reject_pdf_request(req["id"], reason):
                                st.session_state[
                                    f"show_reject_{req['id']}"] = False
                                st.success("تم الرفض")
                                st.rerun()
    with tab2:
        if not approved: st.info("💡 لا توجد طلبات موافق عليها")
        else:
            for req in reversed(approved[-30:]):
                st.markdown(f"✅ **{req['doc_title']}** — {req['user_name']} ({req['created_at']})")
    with tab3:
        if not rejected: st.info("💡 لا توجد طلبات مرفوضة")
        else:
            for req in reversed(rejected[-30:]):
                st.markdown(f"❌ **{req['doc_title']}** — {req['user_name']} ({req['created_at']})")
                if req.get("rejection_reason"):
                    st.caption(f"السبب: {req['rejection_reason']}")


# ═══════════════════════════════════════════════════════════════════════
# ✅ v11.11.0 — الفيديو التعريفي
# ═══════════════════════════════════════════════════════════════════════

def get_intro_video_path() -> Optional[str]:
    for p in ["intro_video.mp4", "intro.mp4", "تعريفي.mp4",
              "tutorial.mp4", "video/intro.mp4"]:
        if os.path.exists(p): return p
    return None


def render_welcome_with_video():
    if "video_watched" not in st.session_state:
        st.session_state["video_watched"] = False
    
    if st.session_state["video_watched"]: return False
    
    video_path = get_intro_video_path()
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
                padding: 20px; border-radius: 16px;
                border: 3px solid #2e7d32; margin: 20px 0;
                direction: rtl; text-align: right;">
        <h3 style="color:#1b5e20; margin: 0 0 10px 0;">🎬 مرحباً بك في تاور نولجي</h3>
        <p style="color:#555; margin: 0;">شاهد الفيديو التعريفي لفهم كيفية استخدام المنصة</p>
    </div>
    """, unsafe_allow_html=True)
    
    if video_path:
        try: st.video(video_path)
        except Exception as e: st.warning(f"⚠️ {e}")
    else:
        st.info("📹 ضع ملف `intro_video.mp4` في مجلد التطبيق ليظهر تلقائياً")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ شاهدت الفيديو — متابعة", type="primary",
                use_container_width=True, key="video_continue"):
            st.session_state["video_watched"] = True; st.rerun()
    with col2:
        if st.button("⏭️ تخطي", use_container_width=True, key="video_skip"):
            st.session_state["video_watched"] = True; st.rerun()
    
    return True


# ═══ الصور ═══
ANIMAL_IMAGES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600",
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

def get_owner_photo():
    for p in ["owner.jpg", "owner.png", "14686.jpg"]:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f: return base64.b64encode(f.read()).decode()
            except Exception: pass
    return None

owner_b64 = get_owner_photo()


# ═══════════════════════════════════════════════════════════════════════
# مربط الخيول + الحظائر
# ═══════════════════════════════════════════════════════════════════════

HORSE_STALL_SCIENCE = {
    "box_standard": {"width": 3.5, "length": 3.5, "area": 12.25,
        "name_ar": "مربط صندوقي قياسي", "usage": "حصان 500-600 كجم"},
    "box_large": {"width": 4.0, "length": 4.0, "area": 16.0,
        "name_ar": "مربط كبير", "usage": "حصان >600"},
    "box_foaling": {"width": 4.0, "length": 5.0, "area": 20.0,
        "name_ar": "مربط ولادة", "usage": "فرس حامل"},
    "box_pony": {"width": 3.0, "length": 3.0, "area": 9.0,
        "name_ar": "مربط بوني", "usage": "بوني"},
}

HORSE_BARN_SCIENCE = {
    "aisle_width_m": 3.5, "ceiling_height_m": 4.0,
    "wall_height_m": 3.5, "door_width_m": 1.3, "door_height_m": 2.4,
    "front_partition_m": 1.5, "side_partition_m": 2.0,
    "bedding_cm": 20, "ach_winter": 5, "ach_summer": 25,
    "fresh_air_m3h_per_horse": 30, "window_area_pct": 0.10,
    "service_room_m2": 25, "tack_room_m2": 12,
    "wash_bay_m2": 16, "hay_storage_m2": 20,
}

def calculate_horse_barn_scientific(num_horses, stall_type="box_standard",
                                      include_service=True):
    if stall_type not in HORSE_STALL_SCIENCE:
        stall_type = "box_standard"
    stall = HORSE_STALL_SCIENCE[stall_type]
    sci = HORSE_BARN_SCIENCE
    if num_horses <= 4:
        rows = 1; stalls_per_row = num_horses
    else:
        rows = 2; stalls_per_row = (num_horses + 1) // 2
    row_length = stalls_per_row * stall["width"]
    aisle_w = sci["aisle_width_m"]
    building_width = (rows * stall["length"]) + aisle_w + 1.0
    building_length = row_length + 2.0
    stall_area_total = num_horses * stall["area"]
    aisle_area = building_length * aisle_w
    service_area = 0
    if include_service:
        service_area = (sci["service_room_m2"] + sci["tack_room_m2"] +
                        sci["wash_bay_m2"] + sci["hay_storage_m2"])
    total_area = building_width * building_length + service_area
    building_volume = building_width * building_length * sci["ceiling_height_m"]
    vent_summer = building_volume * sci["ach_summer"]
    vent_winter = building_volume * sci["ach_winter"]
    vent_summer_cfm = vent_summer * 35.3147 / 60
    vent_winter_cfm = vent_winter * 35.3147 / 60
    tunnel_fans = max(1, int(np.ceil(vent_summer_cfm / 20000)))
    side_fans = max(1, int(np.ceil(vent_winter_cfm / 8000)))
    wall_area = 2 * building_length * sci["wall_height_m"] + \
                2 * building_width * sci["wall_height_m"]
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
    cost_total = round(cost_structure + cost_roof + cost_stalls +
                       cost_aisle_floor + cost_service + cost_ventilation +
                       cost_lighting + cost_windows, 0)
    return {
        "is_horse_barn": True, "num_horses": num_horses,
        "stall_type": stall_type, "stall_type_ar": stall["name_ar"],
        "stall_dimensions": f"{stall['width']}×{stall['length']} م",
        "stall_area_m2": stall["area"],
        "stalls_per_row": stalls_per_row, "rows_count": rows,
        "building_width_m": round(building_width, 2),
        "building_length_m": round(building_length, 2),
        "building_height_m": sci["ceiling_height_m"],
        "total_area_m2": round(total_area, 2),
        "volume_m3": round(building_volume, 1),
        "vent_summer_m3h": int(vent_summer), "vent_winter_m3h": int(vent_winter),
        "vent_summer_cfm": int(vent_summer_cfm),
        "vent_winter_cfm": int(vent_winter_cfm),
        "tunnel_fans_count": tunnel_fans, "side_fans_count": side_fans,
        "tunnel_fans_hp_total": tunnel_fans * 2.0,
        "side_fans_hp_total": side_fans * 1.0,
        "door_dimensions": f"{sci['door_width_m']}×{sci['door_height_m']} م",
        "doors_count": num_horses,
        "window_area_m2": round(window_area, 2),
        "bedding_cm": sci["bedding_cm"],
        "bedding_m3": round(stall_area_total * sci["bedding_cm"] / 100, 1),
        "water_per_day_L": water_day,
        "light_fixtures": light_fixtures, "lighting_lux": 200,
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
        "count": num_horses, "length_m": round(building_length, 2),
        "width_m": round(building_width, 2),
        "ridge_height_m": sci["ceiling_height_m"] + 1.5,
        "roof_type": "gable", "slope_pct": 25.0,
        "feeders_count": num_horses * 2, "drinkers_count": num_horses,
        "feeder_type": "معلف", "drinker_type": "حوض",
        "total_feeder_length_m": round(num_horses * 1.2, 1),
        "total_drinker_length_m": round(num_horses * 0.6, 1),
        "cooling_pad_enabled": False, "cooling_pad_area_m2": 0,
        "structure_type": "هيكل خشبي/معدني",
        "steel_weight_kg": round(building_width * building_length * 30, 0),
        "roof_material": "صاج + عزل", "wall_material": "خشب + شبك",
        "floor_material": "خرسانة + نشارة",
        "insulation_area_m2": round((building_width * building_length) + wall_area * 0.6, 2),
        "insulation_thickness_mm": 30, "barn_key": "خيول_مربط",
        "vent_flow_summer_m3h": int(vent_summer),
        "vent_flow_winter_m3h": int(vent_winter),
        "vent_flow_summer_cfm": int(vent_summer_cfm),
        "vent_flow_winter_cfm": int(vent_winter_cfm),
        "vent_open_area_m2": round(window_area, 2),
        "ventilation_type": "نفق", "tunnel_fan_spec": "120 سم — 20000 CFM",
        "side_fan_spec": "90 سم — 8000 CFM",
        "roof_area_m2": round(building_width * building_length * 1.15, 2),
        "wall_area_m2": round(wall_area, 2),
        "light_hours": 14, "light_watts_total": light_fixtures * 60,
        "water_per_head_L": 45, "aisle_m": aisle_w, "central_aisle": True,
    }


BARN_DESIGN_STANDARDS = {
    "دواجن_لاحم": {"name_ar": "دواجن لاحم", "area_per_head": 0.10,
        "feeder_cm_per_head": 5.0, "drinker_cm_per_head": 2.5,
        "height_m": 2.8, "width_m": 12.0, "ach_summer": 60, "ach_winter": 8,
        "vent_open_ratio": 0.20, "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "خطية", "drinker_type": "حلمات", "aisle_m": 1.2,
        "central_aisle": True, "structure_type": "هيكل معدني",
        "roof_material": "ساندوتش", "wall_material": "ستائر",
        "floor_material": "خرسانة", "insulation_thickness_cm": 5.0,
        "ventilation_type": "نفق", "tunnel_fan_cfm": 12000,
        "tunnel_fan_hp": 1.5, "tunnel_fan_diameter_cm": 90,
        "side_fan_cfm": 5000, "side_fan_hp": 0.75,
        "cooling_pad_enabled": True, "cooling_pad_m2_per_1000cfm": 0.5,
        "lighting_lux": 30, "light_hours": 18, "water_per_head_L": 0.25},
    "أبقار": {"name_ar": "أبقار", "area_per_head": 5.0,
        "feeder_cm_per_head": 70.0, "drinker_cm_per_head": 6.0,
        "height_m": 4.5, "width_m": 15.0, "ach_summer": 25, "ach_winter": 4,
        "vent_open_ratio": 0.35, "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "وسطية", "drinker_type": "حوض", "aisle_m": 3.5,
        "central_aisle": True, "structure_type": "هيكل معدني ثقيل",
        "roof_material": "صاج", "wall_material": "شبك",
        "floor_material": "خرسانة", "insulation_thickness_cm": 3.0,
        "ventilation_type": "تقطيعي", "tunnel_fan_cfm": 20000,
        "tunnel_fan_hp": 2.0, "tunnel_fan_diameter_cm": 120,
        "side_fan_cfm": 8000, "side_fan_hp": 1.0,
        "cooling_pad_enabled": False, "cooling_pad_m2_per_1000cfm": 0.4,
        "lighting_lux": 200, "light_hours": 16, "water_per_head_L": 80},
    "أغنام": {"name_ar": "أغنام", "area_per_head": 1.5,
        "feeder_cm_per_head": 35.0, "drinker_cm_per_head": 4.0,
        "height_m": 3.5, "width_m": 10.0, "ach_summer": 30, "ach_winter": 5,
        "vent_open_ratio": 0.30, "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "خرسانية", "drinker_type": "حوض", "aisle_m": 2.0,
        "central_aisle": True, "structure_type": "هيكل معدني",
        "roof_material": "صاج", "wall_material": "شبك",
        "floor_material": "خرسانة", "insulation_thickness_cm": 2.5,
        "ventilation_type": "طبيعي", "tunnel_fan_cfm": 14000,
        "tunnel_fan_hp": 1.5, "tunnel_fan_diameter_cm": 90,
        "side_fan_cfm": 6000, "side_fan_hp": 1.0,
        "cooling_pad_enabled": False, "cooling_pad_m2_per_1000cfm": 0.3,
        "lighting_lux": 100, "light_hours": 14, "water_per_head_L": 6},
    "إبل": {"name_ar": "إبل", "area_per_head": 10.0,
        "feeder_cm_per_head": 100.0, "drinker_cm_per_head": 8.0,
        "height_m": 4.5, "width_m": 15.0, "ach_summer": 20, "ach_winter": 4,
        "vent_open_ratio": 0.40, "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "مرتفعة", "drinker_type": "حوض كبير", "aisle_m": 4.0,
        "central_aisle": True, "structure_type": "هيكل ثقيل",
        "roof_material": "صاج", "wall_material": "شبك",
        "floor_material": "رمل", "insulation_thickness_cm": 3.0,
        "ventilation_type": "طبيعي", "tunnel_fan_cfm": 20000,
        "tunnel_fan_hp": 2.0, "tunnel_fan_diameter_cm": 120,
        "side_fan_cfm": 8000, "side_fan_hp": 1.0,
        "cooling_pad_enabled": True, "cooling_pad_m2_per_1000cfm": 0.4,
        "lighting_lux": 100, "light_hours": 12, "water_per_head_L": 50},
    "سمان": {"name_ar": "سمان", "area_per_head": 0.025,
        "feeder_cm_per_head": 2.0, "drinker_cm_per_head": 1.0,
        "height_m": 2.0, "width_m": 6.0, "ach_summer": 50, "ach_winter": 8,
        "vent_open_ratio": 0.25, "roof_type": "mono", "slope_pct": 15.0,
        "feeder_type": "خطية", "drinker_type": "حلمات", "aisle_m": 0.8,
        "central_aisle": False, "structure_type": "خفيف",
        "roof_material": "ساندوبانل", "wall_material": "شبك",
        "floor_material": "بطاريات", "insulation_thickness_cm": 4.0,
        "ventilation_type": "نفق", "tunnel_fan_cfm": 10000,
        "tunnel_fan_hp": 1.0, "tunnel_fan_diameter_cm": 60,
        "side_fan_cfm": 4000, "side_fan_hp": 0.75,
        "cooling_pad_enabled": True, "cooling_pad_m2_per_1000cfm": 0.5,
        "lighting_lux": 20, "light_hours": 16, "water_per_head_L": 0.06},
    "أرانب": {"name_ar": "أرانب", "area_per_head": 0.30,
        "feeder_cm_per_head": 8.0, "drinker_cm_per_head": 2.0,
        "height_m": 2.5, "width_m": 8.0, "ach_summer": 40, "ach_winter": 6,
        "vent_open_ratio": 0.25, "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "معدنية", "drinker_type": "نبل", "aisle_m": 1.2,
        "central_aisle": True, "structure_type": "خفيف",
        "roof_material": "ساندوتش", "wall_material": "شبك",
        "floor_material": "بطاريات", "insulation_thickness_cm": 3.0,
        "ventilation_type": "نفق", "tunnel_fan_cfm": 8000,
        "tunnel_fan_hp": 0.75, "tunnel_fan_diameter_cm": 60,
        "side_fan_cfm": 3000, "side_fan_hp": 0.5,
        "cooling_pad_enabled": True, "cooling_pad_m2_per_1000cfm": 0.4,
        "lighting_lux": 30, "light_hours": 16, "water_per_head_L": 0.35},
}

def calculate_barn_dimensions(key, count, barn_system="أرضي مفتوح"):
    std = BARN_DESIGN_STANDARDS.get(key)
    if not std: return None
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
    cooling_pad = 0.0
    if std.get("cooling_pad_enabled", False):
        cooling_pad = round(vent_summer_cfm * std["cooling_pad_m2_per_1000cfm"] / 1000, 2)
    light_fixtures = max(1, int(np.ceil(floor_area / 100)))
    water_day = count * std["water_per_head_L"]
    cost_structure = floor_area * 60
    cost_roof = roof_area * 25
    cost_walls = wall_area * 15
    cost_floor = floor_area * 30
    cost_fans = tunnel_fans * 450 + side_fans * 250
    cost_cooling = cooling_pad * 80
    cost_lighting = light_fixtures * 40
    cost_feeders = feeders * 180
    cost_drinkers = drinkers * 90
    cost_total = round(cost_structure + cost_roof + cost_walls + cost_floor +
                       cost_fans + cost_cooling + cost_lighting +
                       cost_feeders + cost_drinkers, 0)
    return {
        "standard": std, "count": count,
        "total_area_m2": round(area, 2),
        "length_m": round(length, 2), "width_m": round(width, 2),
        "height_m": round(height, 2), "ridge_height_m": round(ridge, 2),
        "volume_m3": round(volume, 1),
        "roof_type": std["roof_type"], "slope_pct": std["slope_pct"],
        "roof_area_m2": round(roof_area, 2), "wall_area_m2": round(wall_area, 2),
        "feeders_count": feeders, "drinkers_count": drinkers,
        "total_feeder_length_m": round(count * std["feeder_cm_per_head"] / 100, 1),
        "total_drinker_length_m": round(count * std["drinker_cm_per_head"] / 100, 1),
        "feeder_type": std.get("feeder_type", "خطية"),
        "drinker_type": std.get("drinker_type", "حوض"),
        "vent_flow_summer_m3h": int(vent_summer),
        "vent_flow_winter_m3h": int(vent_winter),
        "vent_flow_summer_cfm": int(vent_summer_cfm),
        "vent_flow_winter_cfm": int(vent_winter_cfm),
        "vent_open_area_m2": round(length * height * std["vent_open_ratio"], 2),
        "ventilation_type": std.get("ventilation_type", "نفق"),
        "tunnel_fans_count": tunnel_fans,
        "tunnel_fan_spec": f"{std['tunnel_fan_diameter_cm']}\" — {std['tunnel_fan_cfm']} CFM",
        "tunnel_fans_hp_total": tunnel_fans * std["tunnel_fan_hp"],
        "side_fans_count": side_fans,
        "side_fan_spec": f"{std['side_fan_cfm']} CFM",
        "side_fans_hp_total": side_fans * std["side_fan_hp"],
        "cooling_pad_area_m2": cooling_pad,
        "cooling_pad_enabled": std.get("cooling_pad_enabled", False),
        "structure_type": std.get("structure_type", "هيكل معدني"),
        "steel_weight_kg": round(floor_area * 25.0, 1),
        "roof_material": std.get("roof_material", "ساندوتش"),
        "wall_material": std.get("wall_material", "ستائر"),
        "floor_material": std.get("floor_material", "خرسانة"),
        "roof_material_area_m2": round(roof_area, 2),
        "insulation_area_m2": round(roof_area + wall_area * 0.6, 2),
        "insulation_thickness_mm": std.get("insulation_thickness_cm", 3.0) * 10,
        "lighting_lux": std.get("lighting_lux", 30),
        "light_hours": std.get("light_hours", 16),
        "light_fixtures": light_fixtures,
        "light_watts_total": 15 * light_fixtures,
        "water_per_head_L": std.get("water_per_head_L", 6),
        "water_per_day_L": round(water_day, 1),
        "cost_structure_usd": round(cost_structure, 0),
        "cost_roof_usd": round(cost_roof, 0),
        "cost_walls_usd": round(cost_walls, 0),
        "cost_floor_usd": round(cost_floor, 0),
        "cost_fans_tunnel_usd": tunnel_fans * 450,
        "cost_fans_side_usd": side_fans * 250,
        "cost_cooling_pad_usd": round(cooling_pad * 80, 0),
        "cost_lighting_usd": light_fixtures * 40,
        "cost_feeders_usd": feeders * 180,
        "cost_drinkers_usd": drinkers * 90,
        "cost_total_usd": cost_total,
        "aisle_m": std.get("aisle_m", 1.5),
        "central_aisle": std.get("central_aisle", True),
        "temp_optimal": 20, "barn_key": key,
    }


def create_barn_3d_figure(dims):
    """3D مع إسطبلات خيول محسّنة"""
    if not PLOTLY_AVAILABLE: return None
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
        # المراوح
        fan_count = dims.get("tunnel_fans_count", 0)
        for i in range(min(fan_count, 20)):
            xc = L - 0.05
            yc = (i + 0.5) * (W / max(fan_count, 1))
            fig.add_trace(go.Scatter3d(x=[xc], y=[yc], z=[H * 0.5],
                mode='markers+text',
                marker=dict(size=15, color='#1976d2', symbol='circle'),
                text=[f'م{i+1}'], textposition='middle center',
                textfont=dict(size=8, color='white'),
                name='مروحة' if i == 0 else None, showlegend=(i == 0)))
        side_count = dims.get("side_fans_count", 0)
        for i in range(min(side_count, 20)):
            xc = (i + 0.5) * (L / max(side_count, 1))
            fig.add_trace(go.Scatter3d(x=[xc], y=[0.1], z=[H * 0.7],
                mode='markers',
                marker=dict(size=10, color='#00897b', symbol='diamond'),
                name='مروحة جانبية' if i == 0 else None, showlegend=(i == 0)))
        # المعالف
        aisle = dims.get("aisle_m", 1.5); fw = 0.6
        if dims.get("central_aisle", True) and W > 8:
            fpos = [W/2 - aisle/2 - fw, W/2 + aisle/2]
        else:
            fpos = [0.8, W - 1.4]
        for idx, yp in enumerate(fpos):
            if yp + fw > W: continue
            xv = [0.5, L-0.5, L-0.5, 0.5, 0.5, L-0.5, L-0.5, 0.5]
            yv = [yp, yp, yp+fw, yp+fw, yp, yp, yp+fw, yp+fw]
            zv = [0, 0, 0, 0, 0.35, 0.35, 0.35, 0.35]
            ii = [0,0,4,4,0,0,3,3,0,0,1,1]
            ji = [1,2,6,7,4,5,2,6,3,7,5,6]
            ki = [2,3,5,6,5,1,6,7,7,4,6,2]
            fig.add_trace(go.Mesh3d(x=xv, y=yv, z=zv, i=ii, j=ji, k=ki,
                color='#ff8f00', opacity=0.9,
                name='معلف' if idx == 0 else None, showlegend=(idx == 0),
                hoverinfo='skip'))
        # السقايات
        nd = dims.get("drinkers_count", 0)
        for i in range(min(nd, 20)):
            xc = (i + 0.5) * (L / max(nd, 1))
            yc = W - aisle - 0.5 if dims.get("central_aisle", True) else W - 1.5
            fig.add_trace(go.Scatter3d(x=[xc], y=[min(yc, W - 0.2)], z=[0.4],
                mode='markers+text',
                marker=dict(size=10, color='#1976d2', symbol='diamond'),
                text=[f'م{i+1}'], textposition='top center',
                textfont=dict(size=8, color='#0d47a1'),
                name='سقاية' if i == 0 else None, showlegend=(i == 0)))
        # الحيوانات (عام)
        count = dims.get("count", dims.get("num_horses", 100))
        if not dims.get("is_horse_barn"):
            apr = min(20, max(1, int(np.sqrt(count))))
            ax_, ay_, az_ = [], [], []
            for ri in range(apr):
                for ci in range(apr):
                    if len(ax_) > 200: break
                    xp = 0.8 + ci * (L - 1.6) / apr
                    yp = 1.0 + ri * (W - 2.0) / apr
                    ax_.append(xp); ay_.append(yp); az_.append(0.15)
            if ax_:
                fig.add_trace(go.Scatter3d(x=ax_, y=ay_, z=az_, mode='markers',
                    marker=dict(size=2.5, color='#1b5e20', opacity=0.7),
                    name=f'حيوانات ({count})'))
        
        # ✅ إسطبلات الخيول المحسّنة
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
                    stall_num = col + 1 + row * per_row
                    y_front = y_offset if row == 0 else y_offset + stall_l
                    # يسار الجدار
                    fig.add_trace(go.Mesh3d(
                        x=[x_offset, x_offset+0.5, x_offset+0.5, x_offset],
                        y=[y_front]*4, z=[0, 0, wall_h, wall_h],
                        i=[0,0], j=[1,2], k=[2,3], color='#8d6e63', 
                        opacity=0.6, showlegend=False, hoverinfo='skip'))
                    # يمين الجدار
                    fig.add_trace(go.Mesh3d(
                        x=[x_offset+stall_w-0.5, x_offset+stall_w,
                           x_offset+stall_w, x_offset+stall_w-0.5],
                        y=[y_front]*4, z=[0, 0, wall_h, wall_h],
                        i=[0,0], j=[1,2], k=[2,3], color='#8d6e63', 
                        opacity=0.6, showlegend=False, hoverinfo='skip'))
                    # الجزء العلوي
                    fig.add_trace(go.Mesh3d(
                        x=[x_offset, x_offset+stall_w, x_offset+stall_w, x_offset],
                        y=[y_front]*4, z=[H*0.6, H*0.6, wall_h, wall_h],
                        i=[0,0], j=[1,2], k=[2,3], color='#8d6e63', 
                        opacity=0.5, showlegend=False, hoverinfo='skip'))
                    # الجدار الجانبي
                    x_right = x_offset + stall_w
                    fig.add_trace(go.Mesh3d(
                        x=[x_right]*4, y=[y_offset, y_offset+stall_l,
                                           y_offset+stall_l, y_offset],
                        z=[0, 0, wall_h, wall_h],
                        i=[0,0], j=[1,2], k=[2,3], color='#6d4c41', 
                        opacity=0.55, showlegend=False, hoverinfo='skip'))
                    # الجدار الخلفي
                    y_back = y_offset + stall_l if row == 0 else y_offset
                    fig.add_trace(go.Mesh3d(
                        x=[x_offset, x_offset+stall_w, x_offset+stall_w, x_offset],
                        y=[y_back]*4, z=[0, 0, wall_h, wall_h],
                        i=[0,0], j=[1,2], k=[2,3], color='#6d4c41', 
                        opacity=0.55, showlegend=False, hoverinfo='skip'))
                    # الأرضية (فرشة)
                    fig.add_trace(go.Mesh3d(
                        x=[x_offset, x_offset+stall_w, x_offset+stall_w, x_offset],
                        y=[y_offset, y_offset, y_offset+stall_l, y_offset+stall_l],
                        z=[0.05, 0.05, 0.05, 0.05],
                        i=[0,0], j=[1,2], k=[2,3], color='#ffd54f', 
                        opacity=0.5, showlegend=False, hoverinfo='skip'))
                    # الحصان (جسم)
                    horse_cx = x_offset + stall_w/2
                    horse_cy = y_offset + stall_l/2
                    fig.add_trace(go.Scatter3d(
                        x=[horse_cx], y=[horse_cy], z=[0.7],
                        mode='markers',
                        marker=dict(size=22, color='#5d4037', symbol='square',
                                    line=dict(color='#3e2723', width=2)),
                        name='حصان' if row==0 and col==0 else None,
                        showlegend=(row==0 and col==0),
                        hovertemplate=f'حصان {stall_num}<extra></extra>'))
                    # رأس الحصان
                    fig.add_trace(go.Scatter3d(
                        x=[horse_cx + 0.3], y=[horse_cy], z=[1.0],
                        mode='markers',
                        marker=dict(size=12, color='#4e342e', symbol='circle'),
                        showlegend=False, hoverinfo='skip'))
                    # المعلف (علف أخضر)
                    feed_x = x_offset + stall_w * 0.3
                    fig.add_trace(go.Mesh3d(
                        x=[feed_x, feed_x+0.4, feed_x+0.4, feed_x],
                        y=[y_back-0.2 if row==0 else y_back+0.2,
                           y_back-0.2 if row==0 else y_back+0.2,
                           y_back-0.5 if row==0 else y_back+0.5,
                           y_back-0.5 if row==0 else y_back+0.5],
                        z=[0, 0, 0.5, 0.5],
                        i=[0,0], j=[1,2], k=[2,3], color='#66bb6a',
                        opacity=0.85, showlegend=False, hoverinfo='skip'))
                    # دلو الماء
                    water_x = x_offset + stall_w * 0.7
                    fig.add_trace(go.Scatter3d(
                        x=[water_x], y=[y_back-0.3 if row==0 else y_back+0.3],
                        z=[0.3], mode='markers',
                        marker=dict(size=12, color='#1976d2', symbol='circle',
                                    line=dict(color='#0d47a1', width=1.5)),
                        showlegend=False, hoverinfo='skip'))
                    # رقم الإسطبل
                    fig.add_trace(go.Scatter3d(
                        x=[x_offset+stall_w/2], y=[y_front], z=[wall_h + 0.3],
                        mode='text',
                        text=[f"🐎 {stall_num}"],
                        textfont=dict(size=11, color='#c62828'),
                        showlegend=False))
        
        fig.update_layout(
            title=dict(
                text=f"🏗️ {std['name_ar']} — {count} | "
                     f"{L:.1f}×{W:.1f}×{RH:.1f} م",
                font=dict(size=13, color='#1b5e20'), x=0.5),
            scene=dict(
                xaxis=dict(title='الطول', range=[-0.5, L+0.5]),
                yaxis=dict(title='العرض', range=[-0.5, W+0.5]),
                zaxis=dict(title='الارتفاع', range=[0, RH+0.5]),
                aspectmode='manual',
                aspectratio=dict(x=ax_x, y=ax_y, z=ax_z),
                camera=dict(eye=dict(x=1.5, y=-1.5, z=0.9))),
            height=max(600, min(900, 600 + int(count / 100))),
            paper_bgcolor='white')
        return fig
    except Exception: return None


def generate_barn_pdf_report(dims):
    if not REPORTLAB_AVAILABLE: return b""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
        leftMargin=40, topMargin=115, bottomMargin=145)
    story = []
    def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
        return Paragraph(ar(text), ParagraphStyle('s', fontName=font_mgr.font_name,
            fontSize=size, alignment=align, textColor=HexColor(color),
            spaceAfter=6, leading=size*1.6))
    std = dims["standard"]
    story.append(P("تقرير الحظيرة", size=20, align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor('#d4af37')))
    if dims.get("is_horse_barn"):
        info = [[ar("النوع"), ar("مربط خيول علمي")],
            [ar("عدد الخيول"), ar(str(dims['num_horses']))],
            [ar("نوع المربط"), ar(dims['stall_type_ar'])],
            [ar("أبعاد المربط"), ar(dims['stall_dimensions'])],
            [ar("الصفوف"), ar(f"{dims['rows_count']} صف × {dims['stalls_per_row']}")],
            [ar("المساحة"), ar(f"{dims['total_area_m2']} م²")],
            [ar("المرجع"), ar(dims['reference'])]]
    else:
        info = [[ar("الحيوان"), ar(std["name_ar"])],
            [ar("العدد"), ar(str(dims["count"]))],
            [ar("المساحة"), ar(f"{dims['total_area_m2']} م²")]]
    t = Table(info, colWidths=[160, 330])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1),HexColor('#e8f5e9')),
        ('BOX',(0,0),(-1,-1),1.5,HexColor('#2e7d32')),
        ('INNERGRID',(0,0),(-1,-1),0.6,HexColor('#c8e6c9')),
        ('ALIGN',(0,0),(-1,-1),'RIGHT'),
        ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
        ('PADDING',(0,0),(-1,-1),6)]))
    story.append(t); story.append(Spacer(1, 12))
    try:
        pdf_gen._add_references_page(story, dims.get("barn_key", "أبقار"), "عام")
    except Exception: pass
    doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
    buffer.seek(0); return buffer.getvalue()


# ═══════════════════════════════════════════════════════════════════════
# الجلسة
# ═══════════════════════════════════════════════════════════════════════

DEFAULTS = {
    "approved": False, "user_role": None, "active_formula": {},
    "inventory": {}, "broiler_farms": {},
    "last_formulation_result": None, "last_formulation_context": None,
    "lab_result": None, "lab_context": None,
    "horse_barn_dims": None, "lab_manual_rows": None,
    "lab_full_proportions": {},
    "edited_result": None, "edited_ctx": None,
    "owner_attempts": 0, "owner_lock_until": 0.0,
    "formulation_history": [], "comments_list": [],
    "last_activity": _time.time(), "show_new_room": False,
    "shared_comments": f"• مرحباً في {APP_NAME}\n• {DUA_SHORT}\n",
    "last_ocr_result": None, "last_ocr_nutrients": None,
    "invoices": [], "video_watched": False,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

if not st.session_state["inventory"]:
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing in cat:
            st.session_state["inventory"][ing] = {"quantity": 25.0,
                "min_threshold": 5.0, "unit": "طن"}

def build_whatsapp_link(formula, animal, quality, cost):
    import urllib.parse
    body = "🌾 *تاور نولجي*\n\n"
    body += f"🐾 {animal}\n⭐ {quality:.1f}%\n💰 ${cost:.2f}/كجم\n\n"
    for ing, pct in formula.items(): body += f"• {ing}: {pct:.2f}%\n"
    body += f"\n📱 {SUPERVISOR}"
    num = WHATSAPP_NUMBER.replace('+', '').replace(' ', '')
    return f"https://wa.me/{num}?text={urllib.parse.quote(body)}"

def build_email_link(formula, animal, quality, cost):
    import urllib.parse
    body = f"تركيبة {animal}\nالجودة: {quality:.1f}%\n"
    for ing, pct in formula.items(): body += f"  - {ing}: {pct:.2f}%\n"
    subject = f"تركيبة — {animal}"
    return f"mailto:{OWNER_EMAIL}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"

def render_share_buttons(formula, animal, quality, cost, key_suffix=""):
    st.markdown("### 📤 مشاركة")
    c1, c2 = st.columns(2)
    wa = build_whatsapp_link(formula, animal, quality, cost)
    em = build_email_link(formula, animal, quality, cost)
    with c1:
        st.markdown(f'<a href="{wa}" target="_blank" '
            f'style="display:block; padding:12px; background:#25d366; '
            f'color:white; text-decoration:none; border-radius:10px; '
            f'text-align:center; font-weight:700;">📱 واتساب</a>',
            unsafe_allow_html=True)
    with c2:
        st.markdown(f'<a href="{em}" '
            f'style="display:block; padding:12px; background:#1565c0; '
            f'color:white; text-decoration:none; border-radius:10px; '
            f'text-align:center; font-weight:700;">✉️ بريد</a>',
            unsafe_allow_html=True)


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
# صورة المالك (حق الملكية)
# ═══════════════════════════════════════════════════════════════════════

if owner_b64:
    st.markdown(f"""
    <div style="position: fixed; bottom: 70px; right: 20px; z-index: 9999; text-align: center;">
        <img src="data:image/jpeg;base64,{owner_b64}" 
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
# بوابة الدخول
# ═══════════════════════════════════════════════════════════════════════

_now_check = _time.time()
_last_check = st.session_state.get("last_activity", _now_check)
if st.session_state.get("approved") and (_now_check - _last_check) > 3600:
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.warning("🔒 جلسة منتهية"); st.rerun()
st.session_state["last_activity"] = _now_check
generate_csrf_token()

if not st.session_state.get("approved", False):
    # فيديو الترحيب عند الفتح
    if render_welcome_with_video():
        st.stop()
    
    st.markdown('<div class="main-box" style="max-width:980px; '
        'margin:30px auto; direction:rtl;">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <div class="names">🕊️ رحم الله والدي إسماعيل تاور وأختي ابتسام 🕊️</div>
        <p class="quran">{DUA_QURAN}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 2px solid #d4af37; margin: 25px 0;'>",
        unsafe_allow_html=True)
    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        if owner_b64:
            st.markdown(f'<img src="data:image/jpeg;base64,{owner_b64}" '
                f'class="profile-img-style">', unsafe_allow_html=True)
        elif img_base64:
            st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" '
                f'class="profile-img-style">', unsafe_allow_html=True)
    with col_title:
        st.markdown(f"<h2 style='color:#2E7D32; text-align:right;'>"
            f"🌾 {APP_NAME}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.1rem;'>"
            f"{APP_TAGLINE}</p>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#c62828; text-align:right;'>"
            f"{SUPERVISOR} — {SUPERVISOR_TITLE}</h4>", unsafe_allow_html=True)

    st.markdown("<h3 style='text-align:center; color:#1b5e20; margin-top:20px;'>"
        "🔐 اختر بوابتك</h3>", unsafe_allow_html=True)
    col_owner, col_spec, col_guest = st.columns(3)
    with col_owner:
        st.markdown("""<div style="background:linear-gradient(135deg,#e8f5e9,#c8e6c9);
            padding:16px; border-radius:12px; border:2px solid #2e7d32;
            text-align:center; min-height:140px;">
            <h4 style="color:#1b5e20; margin:0;">👑 المالك</h4>
            <p style="font-size:0.82rem;">إدارة كاملة + موافقة PDF</p></div>""",
            unsafe_allow_html=True)
        oc = st.text_input("كود المالك:", type="password", key="oc_v1111")
        if st.button("👑 دخول", type="primary", use_container_width=True, key="b_owner_v1111"):
            if check_owner_code(oc):
                st.session_state.update({"approved": True, "user_role": "owner"})
                st.rerun()
            else: st.error("❌ كود غير صحيح")
    with col_spec:
        st.markdown("""<div style="background:linear-gradient(135deg,#e3f2fd,#bbdefb);
            padding:16px; border-radius:12px; border:2px solid #1565c0;
            text-align:center; min-height:140px;">
            <h4 style="color:#0d47a1; margin:0;">🔬 مختص</h4>
            <p style="font-size:0.82rem;">دخول مباشر (PDF بموافقة)</p></div>""",
            unsafe_allow_html=True)
        if st.button("🔬 دخول كمختص", type="primary", use_container_width=True,
                key="b_spec_v1111"):
            st.session_state.update({"approved": True, "user_role": "specialist"})
            st.rerun()
    with col_guest:
        st.markdown("""<div style="background:linear-gradient(135deg,#fff8e1,#ffecb3);
            padding:16px; border-radius:12px; border:2px solid #d4af37;
            text-align:center; min-height:140px;">
            <h4 style="color:#e65100; margin:0;">👥 زائر</h4>
            <p style="font-size:0.82rem;">مجاني (PDF بموافقة)</p></div>""",
            unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True, key="b_guest_v1111"):
            st.session_state.update({"approved": True, "user_role": "guest"})
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


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
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

c3, c4 = st.columns([0.3, 0.7])
with c3:
    if owner_b64:
        st.markdown(f'<img src="data:image/jpeg;base64,{owner_b64}" '
            f'class="profile-img-style">', unsafe_allow_html=True)
    elif img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" '
            f'class="profile-img-style">', unsafe_allow_html=True)
with c4:
    st.markdown(f"<h1 style='color:#0d3011; text-align:right; font-weight:900;'>"
        f"🌾 {APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#1565C0; text-align:right; font-size:1.25rem;'>"
        f"{APP_TAGLINE}</p>", unsafe_allow_html=True)

st.markdown(f'<div class="visitor-dua-banner">{DUA_VISITOR}</div>',
    unsafe_allow_html=True)
st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)

role = st.session_state.get("user_role", "guest")

if role == "owner":
    tabs_titles = ["🔬 النمذجة", "🧪 مختبر التركيبات", "🎯 NLP",
                   "🌰 الزيوت", "🍼 بدائل الحليب", "📷 OCR",
                   "🏗️ الحظائر 3D", "📊 الجدوى", "🐔 المزارع",
                   "🏭 المستودعات", "📋 طلبات PDF",
                   "💬 غرفة التواصل", "🎬 الاستديو",
                   "📚 المراجع", "📖 الدليل"]
elif role == "specialist":
    tabs_titles = ["🔬 النمذجة", "🧪 مختبر التركيبات", "🎯 NLP",
                   "🌰 الزيوت", "🍼 بدائل الحليب", "📷 OCR",
                   "🏗️ الحظائر 3D", "📊 الجدوى", "🐔 المزارع",
                   "💬 غرفة التواصل", "📚 المراجع", "📖 الدليل"]
else:
    tabs_titles = ["🧮 حاسبة مبسطة", "🧪 مختبر التركيبات",
                   "💬 غرفة التواصل", "📚 المراجع", "📖 الدليل"]

tabs = st.tabs(tabs_titles)
tab_map = {t: tab for t, tab in zip(tabs_titles, tabs)}

# ═══════════════════════════════════════════════════════════════════════
# نهاية PART 2 — أرسل "تابع" لـ PART 3
# ═══════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════
# [تكملة PART 2] — المختبر + الزائر + النمذجة + NLP
# ═══════════════════════════════════════════════════════════════════════

# ═══ 🧪 مختبر التركيبات ═══

def render_lab_tab(role="guest"):
    st.markdown('<div class="section-title">🧪 مختبر التركيبات</div>',
        unsafe_allow_html=True)
    st.caption("🔬 حلّل أي تركيبة — أدخل النسب فقط من المكتبة الكاملة")

    col1, col2 = st.columns(2)
    with col1:
        lab_animal = st.selectbox("🐾 الحيوان:",
            ["أبقار", "أغنام", "ماعز", "إبل", "خيول",
             "دواجن", "سمان", "أسماك", "أرانب"], key="lab_animal_v1111")
    with col2:
        lab_prod_map = {
            "أبقار": ["حليب_عالي", "حليب_متوسط", "حليب_منخفض",
                      "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"],
            "أغنام": ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد",
                      "مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
            "ماعز": ["تسمين_جديان", "تيوس", "حلابة_عالي",
                     "حلابة_متوسط", "حامل_أخير", "صيانة"],
            "إبل": ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
            "خيول": ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار",
                     "مرضعات", "صيانة"],
            "دواجن": ["لاحم", "بياض"], "سمان": ["تسمين", "بياض"],
            "أسماك": ["بادئ زريعة", "نمو", "تسمين"],
            "أرانب": ["تسمين", "حليب", "صيانة"]}
        lab_prod = st.selectbox("🎯 الإنتاج:",
            lab_prod_map.get(lab_animal, ["عام"]), key="lab_prod_v1111")

    st.markdown("### 📝 المكونات")
    input_method = st.radio("طريقة الإدخال:",
        ["📊 جدول المكتبة الكاملة", "📋 لصق نص", "💾 من آخر تركيبة"],
        horizontal=True, key="lab_method_v1111")

    formula_input = {}

    if input_method == "📊 جدول المكتبة الكاملة":
        st.markdown("#### 📚 المكتبة العلفية الكاملة")
        st.caption("💡 ابحث، ثم اكتب النسبة بجانب المكونات التي تريدها")

        fcol1, fcol2 = st.columns([0.4, 0.6])
        with fcol1:
            cat_filter = st.selectbox("📁 الفئة:",
                ["الكل"] + list(BIG_FEEDS_LIBRARY.keys()),
                key="lab_cat_v1111")
        with fcol2:
            search_q = st.text_input("🔍 بحث:",
                placeholder="اكتب اسم مكون...", key="lab_search_v1111")

        all_ings_rows = []
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            if cat_filter != "الكل" and cat_name != cat_filter:
                continue
            for ing_name, ing_data in items.items():
                if search_q and search_q.lower() not in ing_name.lower():
                    continue
                all_ings_rows.append({
                    "المكوّن": ing_name,
                    "الفئة": cat_name.replace("🌾 ", "").replace("🌱 ", "")
                        .replace("🚜 ", "").replace("🧬 ", "").replace("🌰 ", "")
                        .replace("🧪 ", "").replace("🔬 ", "").replace("🪨 ", "")
                        .replace("💊 ", ""),
                    "CP %": ing_data.get("CP", 0),
                    "SE": ing_data.get("SE", 0),
                    "السعر": ing_data.get("price", 300),
                    "✅ النسبة % (أدخل)": 0.0,
                })

        if not all_ings_rows:
            st.warning("⚠️ لا توجد مكونات مطابقة")
        else:
            st.caption(f"📊 {len(all_ings_rows)} مكوّن متاح")
            df_full = pd.DataFrame(all_ings_rows)

            if "lab_full_proportions" not in st.session_state:
                st.session_state["lab_full_proportions"] = {}

            for idx, row in df_full.iterrows():
                ing_name = row["المكوّن"]
                if ing_name in st.session_state["lab_full_proportions"]:
                    df_full.at[idx, "✅ النسبة % (أدخل)"] = \
                        st.session_state["lab_full_proportions"][ing_name]

            edited = st.data_editor(
                df_full,
                use_container_width=True, hide_index=True, height=550,
                column_config={
                    "المكوّن": st.column_config.TextColumn(
                        disabled=True, width="medium"),
                    "الفئة": st.column_config.TextColumn(
                        disabled=True, width="small"),
                    "CP %": st.column_config.NumberColumn(
                        disabled=True, width="small", format="%.1f"),
                    "SE": st.column_config.NumberColumn(
                        disabled=True, width="small", format="%.0f"),
                    "السعر": st.column_config.NumberColumn(
                        disabled=True, width="small", format="$%.0f"),
                    "✅ النسبة % (أدخل)": st.column_config.NumberColumn(
                        min_value=0.0, max_value=100.0, step=0.5,
                        format="%.2f%%", width="small"),
                },
                key="lab_full_table_v1111")

            new_props = {}
            for _, r in edited.iterrows():
                pct = r["✅ النسبة % (أدخل)"]
                if pct and pct > 0:
                    formula_input[r["المكوّن"]] = float(pct)
                    new_props[r["المكوّن"]] = float(pct)
            st.session_state["lab_full_proportions"] = new_props

            if formula_input:
                total = sum(formula_input.values())
                c_s1, c_s2 = st.columns(2)
                c_s1.metric("📊 عدد المكونات", len(formula_input))
                c_s2.metric("📈 المجموع", f"{total:.1f}%")
                if abs(total - 100) > 0.5:
                    st.warning(f"⚠️ المجموع = {total:.1f}% — سيتم التطبيع")
                else:
                    st.success(f"✅ المجموع = {total:.1f}%")

            if st.button("🗑️ مسح كل النسب", key="lab_clear_all_v1111"):
                st.session_state["lab_full_proportions"] = {}
                st.rerun()

    elif input_method == "📋 لصق نص":
        st.caption("مثال: `ذرة صفراء 45` أو `كسب فول صويا 44% 25`")
        text_input = st.text_area("الصق:", height=200, key="lab_text_v1111",
            placeholder="ذرة صفراء 45\nكسب فول صويا 44% 25\nشعير مطحون 20")
        if text_input:
            parsed = _parse_ingredients_from_text(text_input)
            if parsed:
                formula_input = parsed
                st.success(f"✅ {len(parsed)} مكوّن")
                st.dataframe(pd.DataFrame([
                    {"المكوّن": k, "النسبة %": f"{v:.2f}"}
                    for k, v in parsed.items()]),
                    use_container_width=True, hide_index=True)
            else: st.warning("⚠️ استخدم: `الاسم الرقم`")
    else:
        if st.session_state.get("active_formula"):
            active = st.session_state["active_formula"]
            st.info(f"📋 {len(active)} مكوّن")
            if st.checkbox("استخدمها", value=True, key="lab_use_last_v1111"):
                formula_input = dict(active)

    if formula_input:
        total = sum(formula_input.values())
        if abs(total - 100) > 0.5:
            st.warning(f"⚠️ مجموع = {total:.1f}% — سيتم التطبيع")

    if st.button("🔬 تشغيل المختبر", type="primary",
                 use_container_width=True, key="lab_run_v1111"):
        if not formula_input:
            st.error("⚠️ أدخل التركيبة")
        else:
            with st.spinner("🧪 جاري التحليل..."):
                result = analyze_existing_formula(
                    formula_input, lab_animal, lab_prod)
            if not result["success"]:
                st.error(f"❌ {result['message']}")
            else:
                st.session_state["lab_result"] = result
                st.session_state["lab_context"] = {
                    "animal": lab_animal, "production": lab_prod}

    if not st.session_state.get("lab_result"): return
    result = st.session_state["lab_result"]
    ctx = st.session_state.get("lab_context", {})
    quality = result["quality_score"]
    meets = quality >= 70

    st.markdown("---")
    if meets:
        st.markdown(f"""<div class="quality-good-v113">
            <h3 style="color:#1b5e20; margin:0;">✅ جودة: {quality:.1f}%</h3>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="quality-bad-v113">
            <h3 style="color:#c62828; margin:0;">⚠️ جودة: {quality:.1f}%</h3>
        </div>""", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🎯 الحيوان", ctx.get("animal", "—"))
    m2.metric("🧬 الجودة", f"{quality:.1f}%")
    m3.metric("💰 التكلفة", f"${result['cost_per_ton']:.2f}/طن")
    m4.metric("⚖️ Ca:P", f"{result['ca_p_ratio']:.2f}")

    st.markdown("### ⚡ توازن الطاقة/البروتين")
    bal1, bal2, bal3 = st.columns(3)
    e_share = result.get("energy_share_pct", 0)
    p_share = result.get("protein_share_pct", 0)
    bal1.metric("⚡ الطاقة", f"{e_share:.1f}%")
    bal2.metric("🧬 البروتين", f"{p_share:.1f}%")
    if p_share > e_share:
        bal3.metric("⚠️ الحالة", "بروتين أعلى!")
    else:
        bal3.metric("✅ الحالة", "متوازن")

    st.markdown("### 📋 جدول المقارنة")
    comp_df = pd.DataFrame([{
        "العنصر": c["العنصر"], "المعيار": f"{c['المعيار']:.2f}",
        "المحسوب": f"{c['المحسوب']:.2f}", "الفرق": f"{c['الفرق']:+.3f}",
        "الفرق %": f"{c['الفرق %']:+.2f}%",
        "التقييم": c["التقييم"]} for c in result["comparison"]])
    st.dataframe(comp_df, use_container_width=True, hide_index=True)

    with st.expander("📐 المعادلات المرجعية", expanded=False):
        eqs = get_reference_equations(result["animal_type"],
            result["production_type"])
        if eqs:
            st.markdown(f"**📖 {eqs.get('source', '')}**")
            for k, v in eqs.items():
                if k in ("source", "example"): continue
                st.markdown(f"- **{k}:** `{v}`")
            if eqs.get("example"):
                st.info(f"💡 {eqs['example']}")

    ch1, ch2 = st.columns(2)
    with ch1:
        bf = create_colorful_bar_chart(result["standard"], result["actual"])
        if bf: st.image(bf.getvalue(), caption="المقارنة", use_container_width=True)
    with ch2:
        pf = create_colorful_pie_chart(result["formula"])
        if pf: st.image(pf.getvalue(), caption="التوزيع", use_container_width=True)

    with st.expander("📚 المراجع", expanded=False):
        refs = result["references"]
        st.markdown(f"**📖 {refs['primary']}**")
        if refs.get("table"): st.markdown(f"**📑 {refs['table']}**")

    # ✅ PDF مع نظام الموافقة
    try:
        pdf_bytes = generate_lab_pdf(result, ctx)
        fname = f"Lab_{ctx.get('animal','Analysis')}_{datetime.now():%Y%m%d}.pdf"
        render_pdf_download_with_approval(
            pdf_bytes=pdf_bytes,
            file_name=fname,
            doc_title=f"مختبر — {ctx.get('animal','')} — {ctx.get('production','')}",
            user_role=role,
            user_name=st.session_state.get("chat_username", "مستخدم"),
            doc_context={
                "الحيوان": ctx.get("animal", ""),
                "الإنتاج": ctx.get("production", ""),
                "الجودة": f"{quality:.1f}%"},
            key_suffix="lab_v1111")
    except Exception as e:
        st.error(f"⚠️ PDF: {e}")

    render_share_buttons(result["formula"], ctx.get("animal", ""),
        quality, result["cost_per_ton"], key_suffix="lab_v1111")


if "🧪 مختبر التركيبات" in tab_map:
    with tab_map["🧪 مختبر التركيبات"]:
        try: render_lab_tab(role=role)
        except Exception as e:
            st.error(f"⚠️ {e}")
            with st.expander("التفاصيل"): st.code(traceback.format_exc())


# ═══ 🧮 حاسبة الزائر ═══

GUEST_PRODUCTION = {
    "أبقار": {
        "حليب": {"label": "🐄 حلابة", "dp": 12.5, "cp": 17.5, "se": 65,
                 "name": "أبقار حلابة"},
        "تسمين": {"label": "💪 تسمين", "dp": 11.5, "cp": 14.5, "se": 72,
                  "name": "تسمين عجول"},
        "صيانة": {"label": "🌿 صيانة", "dp": 7.5, "cp": 10.0, "se": 53,
                  "name": "أبقار صيانة"}},
    "أغنام": {
        "تسمين": {"label": "💪 تسمين", "dp": 10.5, "cp": 14.0, "se": 64,
                  "name": "تسمين حملان"},
        "مرضعات": {"label": "🥛 مرضعات", "dp": 10.5, "cp": 14.5, "se": 62,
                    "name": "نعاج مرضعات"},
        "صيانة": {"label": "🌿 صيانة", "dp": 7.2, "cp": 9.5, "se": 48,
                  "name": "نعاج صيانة"}},
    "دواجن": {
        "لاحم_بادي": {"label": "🐔 بادي", "dp": 20.0, "cp": 23.0, "se": 76,
                      "name": "دواجن بادي"},
        "لاحم_ناهي": {"label": "🐔 ناهي", "dp": 17.0, "cp": 19.5, "se": 75,
                      "name": "دواجن ناهي"},
        "بياض": {"label": "🥚 بياض", "dp": 15.5, "cp": 18.0, "se": 72,
                 "name": "دواجن بياض"}},
    "أسماك": {
        "بادئ": {"label": "🐟 بادئ", "dp": 32.0, "cp": 40.0, "se": 72,
                 "name": "أسماك بادئ"},
        "نمو": {"label": "🐟 نمو", "dp": 25.0, "cp": 32.0, "se": 70,
                "name": "أسماك نمو"},
        "تسمين": {"label": "🐟 تسمين", "dp": 22.0, "cp": 28.0, "se": 68,
                  "name": "أسماك تسمين"}},
}

if role == "guest" and "🧮 حاسبة مبسطة" in tab_map:
    with tab_map["🧮 حاسبة مبسطة"]:
        try:
            st.markdown('<div class="section-title">🧮 حاسبة سريعة</div>',
                unsafe_allow_html=True)
            st.caption("💡 تركيبة كاملة + 5 رسوم + مقارنات + مراجع")

            c1, c2 = st.columns(2)
            with c1:
                g_animal = st.selectbox("🐾 الحيوان:",
                    list(GUEST_PRODUCTION.keys()), key="g_animal_v1111")
                prod_opts = GUEST_PRODUCTION[g_animal]
                g_prod = st.selectbox("🎯 الغرض:", list(prod_opts.keys()),
                    format_func=lambda x: prod_opts[x]["label"],
                    key="g_prod_v1111")
                g_weight = st.number_input("⚖️ الوزن (كجم):", 1.0, 900.0,
                    400.0, 5.0, key="g_w_v1111")
            with c2:
                g_count = st.number_input("🔢 العدد:", 1, 100000, 1, 1,
                    key="g_cnt_v1111")
                g_name = st.text_input("👤 اسمك:",
                    placeholder="اتركه فارغاً", key="g_name_v1111")

            if st.button("🧮 احسب", type="primary", use_container_width=True,
                    key="g_calc_v1111"):
                prod_info = prod_opts[g_prod]
                if g_animal in ("أبقار", "أغنام"):
                    rough = {"ذرة صفراء": 40, "شعير مطحون": 20,
                        "كسب فول صويا 44%": 18, "نخالة قمح (ردة)": 15,
                        "الحجر الجيري": 1.5, "ملح الطعام": 0.5,
                        "بريمكس مجترات": 0.25,
                        "فوسفات ثنائي الكالسيوم": 0.75}
                elif g_animal == "دواجن":
                    if "بادي" in g_prod:
                        rough = {"ذرة صفراء": 52, "كسب فول صويا 48%": 36,
                            "زيت فول الصويا": 4, "الحجر الجيري": 1.2,
                            "فوسفات ثنائي الكالسيوم": 1.8,
                            "ملح الطعام": 0.3,
                            "بريمكس تسمين دواجن": 0.3,
                            "ليسين نقي": 0.25, "ميثيونين نقي": 0.15}
                    elif "بياض" in g_prod:
                        rough = {"ذرة صفراء": 58, "كسب فول صويا 44%": 22,
                            "نخالة قمح (ردة)": 6, "الحجر الجيري": 8,
                            "فوسفات ثنائي الكالسيوم": 1.8,
                            "ملح الطعام": 0.3, "بريمكس بياض": 0.3,
                            "ميثيونين نقي": 0.1}
                    else:
                        rough = {"ذرة صفراء": 55, "كسب فول صويا 48%": 32,
                            "زيت فول الصويا": 4, "الحجر الجيري": 1.2,
                            "فوسفات ثنائي الكالسيوم": 1.8,
                            "ملح الطعام": 0.3,
                            "بريمكس تسمين دواجن": 0.3,
                            "ليسين نقي": 0.2, "ميثيونين نقي": 0.15}
                else:
                    if "بادئ" in g_prod:
                        rough = {"كسب فول صويا 44%": 30,
                            "مسحوق أسماك 60%": 40, "قمح محلي": 20,
                            "زيت السمك (Fish Oil)": 6,
                            "بريمكس أسماك": 0.3,
                            "فوسفات ثنائي الكالسيوم": 2}
                    else:
                        rough = {"كسب فول صويا 44%": 40,
                            "مسحوق أسماك 60%": 25, "قمح محلي": 25,
                            "زيت السمك (Fish Oil)": 5,
                            "بريمكس أسماك": 0.3,
                            "فوسفات ثنائي الكالسيوم": 2}

                lookup = _get_ingredient_lookup()
                actual = compute_formula_nutrients(rough)
                std_chart = {"DP": prod_info["dp"], "CP": prod_info["cp"],
                              "SE": prod_info["se"]}
                act_chart = {"DP": actual.get("DP", 0),
                              "CP": actual.get("CP", 0),
                              "SE": actual.get("SE", 0)}
                quality, _ = evaluate_quality_weighted(rough, std_chart, g_animal)
                cost = sum(rough[ing] / 100 *
                    lookup.get(ing, {}).get("price", 300) for ing in rough)

                if quality >= 70:
                    st.markdown(f"""<div class="quality-good-v113">
                        <h3 style="color:#1b5e20; margin:0;">
                        ✅ جودة: {quality:.1f}%</h3>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="quality-bad-v113">
                        <h3 style="color:#c62828; margin:0;">
                        ⚠️ جودة: {quality:.1f}%</h3></div>""",
                        unsafe_allow_html=True)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("🎯", g_animal)
                m2.metric("🧬", f"{quality:.1f}%")
                m3.metric("💰", f"${cost:.2f}/طن")
                m4.metric("⚖️ Ca:P",
                    f"{(actual.get('Ca',0)/actual.get('P',1)):.2f}"
                    if actual.get("P", 0) > 0 else "—")

                st.markdown("### 📊 المقارنة")
                cmp_data = []
                for k, lab, target in [
                        ("DP", "بروتين مهضوم", prod_info["dp"]),
                        ("CP", "بروتين خام", prod_info["cp"]),
                        ("SE", "طاقة SE", prod_info["se"])]:
                    cv = actual.get(k, 0)
                    diff = cv - target
                    pct = (diff / target * 100) if target else 0
                    ev = evaluate_difference(pct, standard_value=target)
                    cmp_data.append({"العنصر": lab,
                        "المعيار": f"{target:.1f}",
                        "المحسوب": f"{cv:.1f}",
                        "الفرق": f"{diff:+.2f}",
                        "الفرق %": f"{pct:+.1f}%",
                        "التقييم": ev["label"]})
                st.dataframe(pd.DataFrame(cmp_data),
                    use_container_width=True, hide_index=True)

                with st.expander("📐 المعادلات المرجعية", expanded=False):
                    eqs = get_reference_equations(g_animal, g_prod)
                    if eqs:
                        st.markdown(f"**📖 {eqs.get('source', '')}**")
                        for k, v in eqs.items():
                            if k in ("source", "example"): continue
                            st.markdown(f"- **{k}:** {v}")
                        if eqs.get("example"):
                            st.info(f"💡 {eqs['example']}")

                st.markdown("### 🌾 المكونات")
                for ing, pct in rough.items():
                    st.markdown(f'<div class="formula-item">▪️ '
                        f'<b>{ing}:</b> {pct:.1f}%</div>',
                        unsafe_allow_html=True)

                st.markdown("### 📈 الرسوم البيانية")
                ch1, ch2 = st.columns(2)
                with ch1:
                    bf = create_colorful_bar_chart(std_chart, act_chart)
                    if bf: st.image(bf.getvalue(), caption="المقارنة",
                        use_container_width=True)
                with ch2:
                    pf = create_colorful_pie_chart(rough)
                    if pf: st.image(pf.getvalue(), caption="التوزيع",
                        use_container_width=True)

                ch3, ch4 = st.columns(2)
                with ch3:
                    rf = create_radar_chart(std_chart, act_chart)
                    if rf: st.image(rf.getvalue(), caption="الرادار",
                        use_container_width=True)
                with ch4:
                    gf = create_gauge_chart(quality)
                    if gf: st.image(gf.getvalue(), caption="الجودة",
                        use_container_width=True)

                if actual.get("P", 0) > 0:
                    cf = create_ca_p_ratio_chart(
                        actual.get("Ca", 0), actual.get("P", 0))
                    if cf:
                        st.image(cf.getvalue(), caption="⚖️ Ca:P",
                            use_container_width=True)

                daily = g_weight * 0.025 * g_count
                st.info(f"📊 العلف اليومي: **{daily:.1f} كجم**")

                try:
                    guest_req = AnimalRequirement(
                        DP=prod_info["dp"], CP=prod_info["cp"],
                        SE=prod_info["se"], NDF=30, ADF=20,
                        EE=4, ASH=8, Ca=0.7, P=0.4,
                        name_ar=prod_info["name"],
                        note="تقرير استرشادي")
                    pdf_bytes = pdf_gen.generate_report(
                        formula=rough, requirement=guest_req,
                        animal_type=g_animal, breed=prod_info["name"],
                        cost=cost, city="—", local_cost=cost,
                        local_sym="USD",
                        requester_name=g_name.strip() or "زائر",
                        protein_basis="CP", standard_key="",
                        include_charts=True, quality_score=quality)
                    # ✅ PDF مع نظام الموافقة
                    render_pdf_download_with_approval(
                        pdf_bytes=pdf_bytes,
                        file_name=f"Guest_{g_animal}_{datetime.now():%Y%m%d}.pdf",
                        doc_title=f"زائر — {g_animal} — {prod_info['name']}",
                        user_role=role,
                        user_name=g_name.strip() or st.session_state.get(
                            "chat_username", "زائر"),
                        doc_context={
                            "الحيوان": g_animal,
                            "الغرض": prod_info["name"],
                            "الجودة": f"{quality:.1f}%"},
                        key_suffix="guest_v1111")
                except Exception as e:
                    st.error(f"⚠️ {e}")

                render_share_buttons(rough, g_animal, quality, cost,
                    key_suffix="guest_v1111")

                st.warning("⚠️ استرشادي — للحساب الدقيق استخدم بوابة المختص")
        except Exception as e:
            st.error(f"⚠️ {e}")
            with st.expander("التفاصيل"): st.code(traceback.format_exc())


# ═══ 🔬 النمذجة ═══

if "🔬 النمذجة" in tab_map:
    with tab_map["🔬 النمذجة"]:
        try:
            st.markdown('<div class="section-title">🧬 أساس البروتين</div>',
                unsafe_allow_html=True)
            pb = st.radio("الأساس:",
                ["البروتين المهضوم (DP) — الأدق",
                 "البروتين الخام (CP) — الأسهل"],
                horizontal=True, key="protein_basis_v1111")
            basis_code = "DP" if "DP" in pb else "CP"

            st.markdown('<div class="section-title">🐾 اختر الحيوان</div>',
                unsafe_allow_html=True)
            a_tabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐪 إبل",
                "🐎 خيول", "🐔 دواجن", "🦆 سمان", "🐟 أسماك", "🐇 أرانب"])

            animal_choice = None; production_type = None
            requirement = None; std_key_global = ""

            with a_tabs[0]:
                st.markdown("### 🐄 الأبقار — NRC 2001")
                ct = st.selectbox("الحالة:",
                    ["حليب_عالي", "حليب_متوسط", "حليب_منخفض",
                     "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"],
                    format_func=lambda x: {
                        "حليب_عالي": "🐄 حلابة عالية",
                        "حليب_متوسط": "🐄 حلابة متوسطة",
                        "حليب_منخفض": "🐄 حلابة منخفضة",
                        "تسمين_مكثف": "💪 تسمين مكثف",
                        "تسمين_عادي": "💪 تسمين عادي",
                        "حمل_أخير": "🤰 حمل آخر",
                        "صيانة": "🌿 صيانة"}.get(x, x),
                    key="cattle_t_v1111")
                cp_ = {}
                if "حليب" in ct:
                    cp_["milk_yield"] = st.number_input("🥛 الحليب:",
                        5.0, 60.0, 20.0, 1.0, key="cattle_m_v1111")
                cp_["weight_kg"] = weight_tape_widget("أبقار",
                    "cattle_w_v1111", 500.0)
                rp = get_cattle_requirements(ct, **cp_)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_cattle_v1111"):
                    animal_choice = "أبقار"; production_type = ct
                    requirement = rp; std_key_global = f"أبقار_{ct}"

            with a_tabs[1]:
                st.markdown("### 🐏 الأغنام — NRC 2007")
                sg = st.radio("الجنس:", ["ذكر", "أنثى"],
                    horizontal=True, key="sheep_g_v1111")
                is_m = "ذكر" in sg
                stype = st.selectbox("الحالة:",
                    ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد"] if is_m
                    else ["مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
                    key="sheep_t_v1111")
                lit = 1
                if stype == "مرضعات":
                    lit = st.number_input("المواليد:", 1, 3, 1, 1,
                        key="sheep_l_v1111")
                ws = weight_tape_widget("أغنام", "sheep_w_v1111", 50.0)
                rp = get_sheep_requirements(stype, is_male=is_m,
                    weight_kg=ws, litter_size=lit)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_sheep_v1111"):
                    animal_choice = "أغنام"; production_type = stype
                    requirement = rp; std_key_global = f"أغنام_{stype}"

            with a_tabs[2]:
                st.markdown("### 🐐 الماعز — NRC 2007")
                gg = st.radio("الجنس:", ["ذكر", "أنثى"],
                    horizontal=True, key="goat_g_v1111")
                is_m = "ذكر" in gg; mg = 0
                gtype = st.selectbox("الحالة:",
                    ["تسمين_جديان", "تيوس"] if is_m
                    else ["حلابة_عالي", "حلابة_متوسط", "حامل_أخير", "صيانة"],
                    key="goat_t_v1111")
                if "حلابة" in gtype:
                    mg = st.number_input("🥛 الحليب:", 0.5, 8.0, 2.0, 0.25,
                        key="goat_m_v1111")
                gwt = weight_tape_widget("ماعز", "goat_w_v1111", 45.0)
                rp = get_goat_requirements(gtype, is_male=is_m, milk_yield=mg)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_goat_v1111"):
                    animal_choice = "ماعز"; production_type = gtype
                    requirement = rp; std_key_global = f"ماعز_{gtype}"

            with a_tabs[3]:
                st.markdown("### 🐪 الإبل — FAO 2010")
                cmt = st.selectbox("الحالة:",
                    ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
                    key="camel_t_v1111")
                cm = 5.0
                if cmt == "حليب":
                    cm = st.number_input("🥛 الحليب:", 2.0, 20.0, 5.0, 0.5,
                        key="camel_m_v1111")
                cwt = weight_tape_widget("إبل", "camel_w_v1111", 400.0)
                rp = get_camel_requirements(cmt, weight_kg=cwt, milk_yield=cm)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_camel_v1111"):
                    animal_choice = "إبل"; production_type = cmt
                    requirement = rp; std_key_global = f"إبل_{cmt}"

            with a_tabs[4]:
                st.markdown("### 🐎 الخيول — NRC 2007")
                ht = st.selectbox("الحالة:",
                    ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار",
                     "مرضعات", "صيانة"], key="horse_t_v1111")
                hwt = weight_tape_widget("خيول", "horse_w_v1111", 450.0)
                rp = get_horse_requirements(ht, weight_kg=hwt)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_horse_v1111"):
                    animal_choice = "خيول"; production_type = ht
                    requirement = rp; std_key_global = f"خيول_{ht}"

            with a_tabs[5]:
                st.markdown("### 🐔 الدواجن")
                ps = st.radio("السلالة:", ["لاحم", "بياض"],
                    horizontal=True, key="poultry_s_v1111")
                pa = st.number_input("العمر (أسبوع):", 1, 20, 1, 1,
                    key="poultry_a_v1111")
                rp = get_poultry_requirements(ps, pa)
                p1, p2, p3, p4 = st.columns(4)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                p4.metric("Ca", f"{rp.Ca}%")
                if st.checkbox("✅ اعتماد", key="u_poultry_v1111"):
                    animal_choice = "دواجن"; production_type = ps
                    requirement = rp
                    if "بادي" in rp.name_ar:
                        std_key_global = "دواجن_بادي"
                    elif "نامي" in rp.name_ar:
                        std_key_global = "دواجن_نامي"
                    elif "بياض" in rp.name_ar:
                        std_key_global = "دواجن_بياض"
                    else:
                        std_key_global = "دواجن_ناهي"

            with a_tabs[6]:
                st.markdown("### 🦆 السمان")
                qs = st.radio("النوع:", ["تسمين", "بياض"],
                    horizontal=True, key="quail_s_v1111")
                qa = st.number_input("العمر:", 1, 8, 1, 1, key="quail_a_v1111")
                rp = get_quail_requirements(qs, qa)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_quail_v1111"):
                    animal_choice = "سمان"; production_type = qs
                    requirement = rp
                    std_key_global = ("سمان_بياض" if qs == "بياض"
                                      else "سمان_بادي")

            with a_tabs[7]:
                st.markdown("### 🐟 الأسماك")
                fs = st.selectbox("النوع:",
                    ["البلطي النيلي", "القرموط الأفريقي", "الكارب"],
                    key="fish_sp_v1111")
                fst = st.selectbox("المرحلة:",
                    ["بادئ زريعة", "نمو", "تسمين"], key="fish_stage_v1111")
                rp = get_fish_requirements(fs, fst)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_fish_v1111"):
                    animal_choice = "أسماك"; production_type = fst
                    requirement = rp
                    if "بادئ" in fst or "زريعة" in fst:
                        std_key_global = "أسماك_بادئ"
                    elif "نمو" in fst:
                        std_key_global = "أسماك_نمو"
                    else:
                        std_key_global = "أسماك_تسمين"

            with a_tabs[8]:
                st.markdown("### 🐇 الأرانب")
                rt = st.selectbox("الحالة:",
                    ["تسمين", "حليب", "صيانة"], key="rabbit_t_v1111")
                rwt = st.number_input("⚖️ الوزن:", 1.0, 8.0, 4.0, 0.5,
                    key="rabbit_w_v1111")
                rp = get_rabbit_requirements(rt, rwt)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_rabbit_v1111"):
                    animal_choice = "أرانب"; production_type = rt
                    requirement = rp; std_key_global = f"أرانب_{rt}"

            ready = bool(animal_choice and requirement)
            if not ready:
                st.warning("⚠️ اختر حيواناً وفعّل ✅ الاعتماد")

            if ready:
                ca_p_val = (requirement.Ca / requirement.P
                    if requirement.P else 0)
                st.markdown(f"""<div class="physio-card">
                    <h4>🧬 الحالة المعتمدة</h4>
                    <p style="color:#1a237e; font-size:1.15rem;
                        font-weight:700; margin:0;">{animal_choice} —
                        <span style="color:#c62828;">
                        {requirement.name_ar}</span></p>
                    <div style="display:flex; gap:12px; margin-top:10px;
                        flex-wrap:wrap;">
                        <span style="background:#fff; padding:6px 14px;
                            border-radius:8px;">🧬 DP: <b>{requirement.DP}%</b></span>
                        <span style="background:#fff; padding:6px 14px;
                            border-radius:8px;">🧬 CP: <b>{requirement.CP}%</b></span>
                        <span style="background:#fff; padding:6px 14px;
                            border-radius:8px;">🌽 SE: <b>{requirement.SE}</b></span>
                        <span style="background:#fff; padding:6px 14px;
                            border-radius:8px;">⚖️ Ca:P: <b>{ca_p_val:.2f}</b></span>
                    </div>
                </div>""", unsafe_allow_html=True)

                with st.expander("📐 المعادلات المرجعية", expanded=False):
                    eqs = get_reference_equations(animal_choice, production_type)
                    if eqs:
                        st.markdown(f"**📖 {eqs.get('source', '—')}**")
                        for k, v in eqs.items():
                            if k in ("source", "example"): continue
                            st.markdown(f"- **{k}:** `{v}`")
                        if eqs.get("example"):
                            st.info(f"💡 {eqs['example']}")

                oil_std_info = get_oil_standard(std_key_global)
                st.info(f"🌰 الزيوت: أقصى {oil_std_info['max']}% | "
                    f"مثالي {oil_std_info['optimal']}%")

                requester_name = st.text_input("👤 اسم الطالب:",
                    key="req_name_v1111")

                st.markdown('<div class="section-title">🌾 المكونات</div>',
                    unsafe_allow_html=True)
                sq = st.text_input("🔍 بحث:", key="ing_search_v1111")
                selected = []
                default_set = get_default_selections(
                    animal_choice, production_type, requirement)

                for cat_name, items in BIG_FEEDS_LIBRARY.items():
                    filt = ({k: v for k, v in items.items()
                             if sq.lower() in k.lower()} if sq else items)
                    if not filt: continue
                    expanded = any(x in cat_name for x in
                        ["الحبوب", "الأكساب", "الزيوت", "الأملاح"])
                    with st.expander(f"📁 {cat_name} ({len(filt)})",
                            expanded=expanded):
                        sc = st.columns(3)
                        for idx, ing_name in enumerate(filt.keys()):
                            with sc[idx % 3]:
                                dflt = ing_name in default_set
                                if st.checkbox(ing_name, value=dflt,
                                    key=f"pick_{animal_choice}_{ing_name}_v1111"):
                                    selected.append(ing_name)

                st.markdown("### 💰 الأسعار")
                prices_dict = {}
                if selected:
                    pcols = st.columns(min(3, len(selected)))
                    for idx, ing in enumerate(selected):
                        with pcols[idx % 3]:
                            default_price = float(
                                _get_ingredient_lookup()[ing].get("price", 350.0))
                            prices_dict[ing] = st.number_input(
                                f"💵 {ing} ($/طن)", min_value=5.0,
                                value=default_price, step=10.0,
                                key=f"p_sel_{animal_choice}_{ing}_v1111")
                st.success(f"✅ المختارة: **{len(selected)}** مادة")

                if st.button("🚀 تشغيل المحرك (لن يفشل)",
                        type="primary", use_container_width=True,
                        key="run_btn_v1111"):
                    if len(selected) < 2:
                        st.error("⚠️ اختر مكونين على الأقل")
                    else:
                        custom_std = requirement_to_standard(requirement)
                        with st.spinner(f"⏳ جاري التركيب ({basis_code})..."):
                            result = auto_formulate_smart(
                                selected, prices_dict, custom_std,
                                standard_key=std_key_global, basis=basis_code,
                                min_quality=70.0, animal_type=animal_choice,
                                production_type=production_type)
                        if result["success"]:
                            st.session_state["last_formulation_result"] = result
                            st.session_state["last_formulation_context"] = {
                                "animal_choice": animal_choice,
                                "requirement_name": requirement.name_ar,
                                "basis_label": basis_code,
                                "requirement": requirement,
                                "custom_standard": custom_std,
                                "requester_name": requester_name,
                                "std_key_global": std_key_global,
                                "animal_type": animal_choice,
                                "production_type": production_type}
                            st.session_state["active_formula"] = result["formula"]
                            st.session_state["edited_result"] = None
                            st.session_state["edited_ctx"] = None
                            st.session_state["formulation_history"].append({
                                "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "الحيوان": animal_choice,
                                "الحالة": requirement.name_ar,
                                "الجودة": f"{result['quality_score']:.1f}%",
                                "التكلفة $": f"{result['cost']:.2f}"})
                        else:
                            st.error(f"❌ {result['message']}")

                if st.session_state.get("last_formulation_result"):
                    result = st.session_state["last_formulation_result"]
                    ctx = st.session_state["last_formulation_context"]
                    formula = result["formula"]
                    actual = result["actual_nutrients"]
                    cost = result["cost"]
                    custom_std = ctx["custom_standard"]
                    quality = result.get("quality_score", 0.0)
                    meets = result.get("meets_standard", False)
                    ca_p = (actual.get("Ca", 0) / actual.get("P", 1)
                        if actual.get("P", 0) > 0 else 0)

                    if result.get("warning"):
                        st.warning(result["warning"])

                    if meets:
                        st.markdown(f"""<div class="quality-good-v113">
                            <h3 style="color:#1b5e20; margin:0;">
                            ✅ جودة: {quality:.1f}%</h3>
                            <p style="color:#2e7d32;">Ca:P = {ca_p:.2f}</p>
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div class="quality-bad-v113">
                            <h3 style="color:#c62828; margin:0;">
                            ⚠️ جودة: {quality:.1f}%</h3>
                        </div>""", unsafe_allow_html=True)

                    compare_rows = []
                    labels = {"CP": "بروتين", "DP": "مهضوم", "SE": "SE",
                        "NDF": "NDF", "ADF": "ADF", "EE": "دهن",
                        "ASH": "رماد", "Ca": "Ca", "P": "P"}
                    for k, sv in custom_std.items():
                        if sv == 0: continue
                        cv = actual.get(k, 0.0); diff = cv - sv
                        pct = (diff / sv * 100) if sv else 0
                        ev = evaluate_difference(pct, standard_value=sv)
                        compare_rows.append({"العنصر": labels.get(k, k),
                            "المعيار": f"{sv:.2f}",
                            "المحسوب": f"{cv:.2f}",
                            "الفرق": f"{diff:+.3f}",
                            "الفرق %": f"{pct:+.2f}%",
                            "التقييم": ev["label"], "score": ev["score"]})
                    st.dataframe(pd.DataFrame([
                        {k: v for k, v in r.items() if k != "score"}
                        for r in compare_rows]), use_container_width=True,
                        hide_index=True)

                    st.markdown("### 🌾 المكونات:")
                    for ing, pct in formula.items():
                        st.markdown(f'<div class="formula-item">▪️ '
                            f'<b>{ing}:</b> {pct:.2f}% '
                            f'({pct*10:.1f} كجم/طن)</div>',
                            unsafe_allow_html=True)

                    st.metric("💰 التكلفة:", f"${cost:.2f}")
                    render_share_buttons(formula, ctx["animal_choice"],
                        quality, cost, key_suffix="model_v1111")

                    ch1, ch2 = st.columns(2)
                    with ch1:
                        bf = create_colorful_bar_chart(custom_std, actual)
                        if bf: st.image(bf.getvalue(),
                            caption="المقارنة", use_container_width=True)
                    with ch2:
                        pf = create_colorful_pie_chart(formula)
                        if pf: st.image(pf.getvalue(),
                            caption="التوزيع", use_container_width=True)
                    ch3, ch4 = st.columns(2)
                    with ch3:
                        rf = create_radar_chart(custom_std, actual)
                        if rf: st.image(rf.getvalue(),
                            caption="الرادار", use_container_width=True)
                    with ch4:
                        gf = create_gauge_chart(quality)
                        if gf: st.image(gf.getvalue(),
                            caption="الجودة", use_container_width=True)
                    if actual.get("P", 0) > 0:
                        cf = create_ca_p_ratio_chart(
                            actual.get("Ca", 0), actual.get("P", 0))
                        if cf: st.image(cf.getvalue(),
                            caption="⚖️ Ca:P", use_container_width=True)

                    # ✅ PDF مع نظام الموافقة
                    try:
                        pdf_bytes = pdf_gen.generate_report(
                            formula=formula,
                            requirement=ctx["requirement"],
                            animal_type=ctx["animal_type"],
                            breed=ctx["requirement_name"],
                            cost=cost, city="—", local_cost=cost,
                            local_sym="USD",
                            requester_name=ctx["requester_name"],
                            protein_basis=ctx["basis_label"],
                            standard_key=ctx["std_key_global"],
                            include_charts=True, quality_score=quality)
                        render_pdf_download_with_approval(
                            pdf_bytes=pdf_bytes,
                            file_name=(f"Tawor_{ctx['animal_type']}_"
                                f"{datetime.now():%Y%m%d_%H%M}.pdf"),
                            doc_title=(f"تركيبة {ctx['animal_type']} — "
                                       f"{ctx['requirement_name']}"),
                            user_role=role,
                            user_name=st.session_state.get(
                                "chat_username", "مستخدم"),
                            doc_context={
                                "الحيوان": ctx["animal_type"],
                                "الحالة": ctx["requirement_name"],
                                "الجودة": f"{quality:.1f}%",
                                "التكلفة": f"${cost:.2f}/طن"},
                            key_suffix="model_v1111")
                    except Exception as e:
                        st.error(f"⚠️ {e}")

                    # ═══ تصحيح التركيبة يدوياً ═══
                    st.markdown("---")
                    st.markdown('<div class="section-title">✏️ تصحيح التركيبة يدوياً</div>',
                        unsafe_allow_html=True)
                    st.caption("💡 عدّل النسب ثم اضغط 'تحقق'")

                    edit_data = [{"المكوّن": ing, "النسبة %": pct}
                                 for ing, pct in formula.items()]

                    edit_key = f"edit_df_{ctx['animal_type']}_{ctx['production_type']}"
                    if edit_key not in st.session_state:
                        st.session_state[edit_key] = pd.DataFrame(edit_data)
                    else:
                        if len(st.session_state[edit_key]) != len(formula):
                            st.session_state[edit_key] = pd.DataFrame(edit_data)

                    edited_formula_df = st.data_editor(
                        st.session_state[edit_key],
                        num_rows="dynamic",
                        use_container_width=True, hide_index=True,
                        column_config={
                            "المكوّن": st.column_config.SelectboxColumn(
                                options=sorted(_get_ingredient_lookup().keys()),
                                required=True, width="medium"),
                            "النسبة %": st.column_config.NumberColumn(
                                min_value=0.0, max_value=100.0, step=0.5,
                                format="%.2f%%", width="small"),
                        },
                        key=f"edit_editor_{ctx['animal_type']}_{ctx['production_type']}_v1111")
                    st.session_state[edit_key] = edited_formula_df

                    edit_total = sum(
                        r["النسبة %"] for _, r in edited_formula_df.iterrows()
                        if r["النسبة %"] and r["النسبة %"] > 0)
                    if edit_total > 0:
                        if abs(edit_total - 100) > 0.5:
                            st.warning(
                                f"⚠️ مجموع = {edit_total:.1f}% — سيتم التطبيع")
                        else:
                            st.success(f"✅ مجموع = {edit_total:.1f}%")

                    v_col1, v_col2 = st.columns(2)
                    with v_col1:
                        verify_btn = st.button(
                            "🔄 تحقق من التصحيح",
                            type="primary", use_container_width=True,
                            key=f"verify_v1111_{ctx['animal_type']}",
                            disabled=(edit_total <= 0))
                    with v_col2:
                        reset_btn = st.button(
                            "↩️ استرجع الأصلية",
                            use_container_width=True,
                            key=f"reset_v1111_{ctx['animal_type']}")

                    if reset_btn:
                        st.session_state[edit_key] = pd.DataFrame(edit_data)
                        st.session_state["edited_result"] = None
                        st.rerun()

                    if verify_btn:
                        edited_f = {}
                        for _, r in edited_formula_df.iterrows():
                            if r["النسبة %"] and r["النسبة %"] > 0:
                                edited_f[r["المكوّن"]] = float(r["النسبة %"])

                        if edited_f:
                            with st.spinner("🧪 جاري التحقق..."):
                                new_res = analyze_existing_formula(
                                    edited_f, ctx["animal_type"],
                                    ctx["production_type"])
                            if new_res["success"]:
                                st.session_state["edited_result"] = new_res
                                st.session_state["edited_ctx"] = {
                                    "animal": ctx["animal_type"],
                                    "production": ctx["production_type"]}
                                st.rerun()
                            else:
                                st.error(f"❌ {new_res['message']}")

                    if st.session_state.get("edited_result"):
                        er = st.session_state["edited_result"]
                        e_quality = er["quality_score"]
                        e_meets = e_quality >= 70

                        st.markdown("---")
                        st.markdown("### 📊 نتيجة التركيبة المعدلة")

                        if e_meets:
                            st.markdown(f"""<div class="quality-good-v113">
                                <h3 style="color:#1b5e20; margin:0;">
                                ✅ جودة المعدلة: {e_quality:.1f}%</h3>
                            </div>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""<div class="quality-bad-v113">
                                <h3 style="color:#c62828; margin:0;">
                                ⚠️ جودة المعدلة: {e_quality:.1f}%</h3>
                            </div>""", unsafe_allow_html=True)

                        em1, em2, em3, em4 = st.columns(4)
                        em1.metric("🧬 الجودة", f"{e_quality:.1f}%")
                        em2.metric("💰 التكلفة", f"${er['cost_per_ton']:.2f}/طن")
                        em3.metric("⚖️ Ca:P", f"{er['ca_p_ratio']:.2f}")
                        em4.metric("📊 المكونات", len(er["formula"]))

                        cmp_df2 = pd.DataFrame([{
                            "العنصر": c["العنصر"],
                            "المعيار": f"{c['المعيار']:.2f}",
                            "المحسوب": f"{c['المحسوب']:.2f}",
                            "الفرق %": f"{c['الفرق %']:+.2f}%",
                            "التقييم": c["التقييم"],
                        } for c in er["comparison"]])
                        st.dataframe(cmp_df2, use_container_width=True,
                            hide_index=True)

                        ech1, ech2 = st.columns(2)
                        with ech1:
                            bf2 = create_colorful_bar_chart(
                                er["standard"], er["actual"])
                            if bf2:
                                st.image(bf2.getvalue(),
                                    caption="المقارنة",
                                    use_container_width=True)
                        with ech2:
                            pf2 = create_colorful_pie_chart(er["formula"])
                            if pf2:
                                st.image(pf2.getvalue(),
                                    caption="التوزيع",
                                    use_container_width=True)

                        # PDF للمعدلة
                        try:
                            edited_pdf = generate_lab_pdf(
                                er, st.session_state["edited_ctx"])
                            render_pdf_download_with_approval(
                                pdf_bytes=edited_pdf,
                                file_name=(f"Edited_{ctx['animal_type']}_"
                                    f"{datetime.now():%Y%m%d}.pdf"),
                                doc_title=(f"تركيبة معدلة — {ctx['animal_type']} — "
                                           f"{ctx['requirement_name']}"),
                                user_role=role,
                                user_name=st.session_state.get(
                                    "chat_username", "مستخدم"),
                                doc_context={
                                    "الحيوان": ctx["animal_type"],
                                    "الحالة": ctx["requirement_name"] + " (معدلة)",
                                    "الجودة": f"{e_quality:.1f}%"},
                                key_suffix="edited_v1111")
                        except Exception as e:
                            st.error(f"⚠️ PDF: {e}")
        except Exception as e:
            st.error(f"⚠️ {e}")
            with st.expander("التفاصيل"): st.code(traceback.format_exc())


# ═══ 🎯 NLP ═══

if "🎯 NLP" in tab_map:
    with tab_map["🎯 NLP"]:
        try:
            st.markdown('<div class="section-title">🎯 التحسين غير الخطي</div>',
                unsafe_allow_html=True)
            if not SCIPY_AVAILABLE or minimize is None:
                st.error("⚠️ SCIPY غير مثبتة")
            else:
                nc1, nc2 = st.columns(2)
                with nc1:
                    nlp_animal = st.selectbox("نوع الحيوان:",
                        ["أبقار", "أغنام", "ماعز", "إبل", "خيول",
                         "دواجن", "سمان", "أسماك", "أرانب"],
                        key="nlp_animal_v1111")
                with nc2:
                    prod_options = {
                        "أبقار": ["حليب_عالي", "حليب_متوسط", "حليب_منخفض",
                            "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"],
                        "أغنام": ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد",
                            "مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
                        "ماعز": ["تسمين_جديان", "تيوس", "حلابة_عالي",
                            "حلابة_متوسط", "حامل_أخير", "صيانة"],
                        "إبل": ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
                        "خيول": ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار",
                            "مرضعات", "صيانة"],
                        "دواجن": ["لاحم", "بياض"], "سمان": ["تسمين", "بياض"],
                        "أسماك": ["بادئ زريعة", "نمو", "تسمين"],
                        "أرانب": ["تسمين", "حليب", "صيانة"]}.get(nlp_animal, ["عام"])
                    nlp_prod = st.selectbox("الحالة:", prod_options,
                        key="nlp_prod_v1111")

                nlp_req = _get_requirement_for_nlp(nlp_animal, nlp_prod)
                m1, m2 = st.columns(2)
                m1.metric("🎯 ME", f"{nlp_req['ME']:.0f} kcal/kg")
                m2.metric("🎯 CP", f"{nlp_req['CP']:.2f}%")

                active = st.session_state.get("active_formula", {})
                all_ings = list(_get_ingredient_lookup().keys())
                nlp_sel = st.multiselect("المكونات:",
                    options=all_ings,
                    default=list(active.keys())[:5] if active else [],
                    max_selections=10, key="nlp_sel_v1111")

                if len(nlp_sel) >= 2:
                    lookup = _get_ingredient_lookup()
                    ing_data = {i: lookup[i] for i in nlp_sel}
                    nlp_prices = {}
                    pcols = st.columns(min(3, len(nlp_sel)))
                    for i, ing in enumerate(nlp_sel):
                        with pcols[i % 3]:
                            nlp_prices[ing] = st.number_input(
                                f"{ing}:", min_value=10.0,
                                value=float(lookup[ing].get("price", 300)),
                                step=10.0, key=f"nlp_p_{ing}_v1111")
                    price_product = st.number_input(
                        "💵 سعر المنتج:", 0.5, 100.0, 2.5, 0.1,
                        key="nlp_pp_v1111")

                    if st.button("🚀 تشغيل NLP", type="primary",
                            use_container_width=True, key="nlp_run_v1111"):
                        with st.spinner("⏳ جاري التحسين..."):
                            result = nlp_optimize_feed(nlp_sel, ing_data,
                                nlp_prices, animal_type=nlp_animal,
                                production_type=nlp_prod,
                                price_product=price_product)
                        if result["success"]:
                            if result.get("warning"):
                                st.warning(result["warning"])
                            st.success(f"✅ ربح: ${result['max_profit']:.4f} | "
                                f"استراتيجية: {result['strategy']}")
                            m1, m2, m3, m4 = st.columns(4)
                            m1.metric("💰 التكلفة", f"${result['final_cost']:.4f}")
                            m2.metric("⚡ ME", f"{result['final_me']:.0f}")
                            m3.metric("🧬 CP", f"{result['final_cp']:.2f}%")
                            m4.metric("📈 الربح", f"${result['max_profit']:.4f}")
                            for ing, pct in result["formula"].items():
                                st.markdown(f'<div class="formula-item">▪️ '
                                    f'<b>{ing}:</b> {pct:.2f}%</div>',
                                    unsafe_allow_html=True)

                            st.markdown("### 📊 تقييم أولي ومقارنة بالقياسي")
                            nlp_actual = compute_formula_nutrients(result["formula"])
                            cmp_nlp = [
                                {"العنصر": "ME (kcal/kg)", 
                                 "المعيار": f"{nlp_req['ME']:.0f}", 
                                 "المحسوب": f"{nlp_actual.get('SE',0)*41:.0f}",
                                 "التقييم": "✅" if nlp_actual.get('SE',0)*41 >= nlp_req['ME']*0.9 else "⚠️"},
                                {"العنصر": "CP (%)", 
                                 "المعيار": f"{nlp_req['CP']:.2f}", 
                                 "المحسوب": f"{nlp_actual.get('CP',0):.2f}",
                                 "التقييم": "✅" if nlp_actual.get('CP',0) >= nlp_req['CP']*0.95 else "⚠️"},
                                {"العنصر": "DP (%)", 
                                 "المعيار": f"{nlp_req['DP']:.2f}", 
                                 "المحسوب": f"{nlp_actual.get('DP',0):.2f}",
                                 "التقييم": "✅" if nlp_actual.get('DP',0) >= nlp_req['DP']*0.95 else "⚠️"},
                            ]
                            st.dataframe(pd.DataFrame(cmp_nlp), use_container_width=True, hide_index=True)
                            
                            r_col1, r_col2 = st.columns(2)
                            with r_col1:
                                chart_std = {"ME/100": nlp_req["ME"]/100, "CP": nlp_req["CP"], "DP": nlp_req["DP"]}
                                chart_act = {"ME/100": nlp_actual.get("SE",0)*41/100, "CP": nlp_actual.get("CP",0), "DP": nlp_actual.get("DP",0)}
                                bf = create_colorful_bar_chart(chart_std, chart_act)
                                if bf:
                                    st.image(bf.getvalue(), caption="مقارنة ME/CP/DP", use_container_width=True)
                            with r_col2:
                                pf = create_colorful_pie_chart(result["formula"])
                                if pf:
                                    st.image(pf.getvalue(), caption="توزيع المكونات", use_container_width=True)

                            fig_curve = create_nlp_profit_curve(
                                result, nlp_sel, ing_data, nlp_prices)
                            if fig_curve:
                                st.plotly_chart(fig_curve, use_container_width=True)

                            # PDF مع الموافقة
                            try:
                                pdf_nlp = generate_nlp_math_pdf(
                                    result, nlp_animal, nlp_prod,
                                    nlp_sel, ing_data, nlp_prices)
                                if pdf_nlp:
                                    render_pdf_download_with_approval(
                                        pdf_bytes=pdf_nlp,
                                        file_name=f"NLP_Full_{nlp_animal}_{datetime.now():%Y%m%d}.pdf",
                                        doc_title=f"NLP — {nlp_animal} — {nlp_prod}",
                                        user_role=role,
                                        user_name=st.session_state.get(
                                            "chat_username", "مستخدم"),
                                        doc_context={
                                            "الحيوان": nlp_animal,
                                            "الحالة": nlp_prod,
                                            "التكلفة": f"${result['final_cost']:.4f}"},
                                        key_suffix="nlp_v1111")
                            except Exception as e:
                                st.warning(f"⚠️ PDF: {e}")
                        else:
                            st.error(f"❌ {result['message']}")
                else:
                    st.info("💡 اختر مكونين على الأقل")
        except Exception as e:
            st.error(f"⚠️ {e}")

# ═══════════════════════════════════════════════════════════════════════
# نهاية PART 3 — أرسل "تابع" لـ PART 4
# ═══════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════
# [تكملة PART 3] — الزيوت + بدائل + OCR + الحظائر + الجدوى + المزارع
# ═══════════════════════════════════════════════════════════════════════

# ═══ 🌰 الزيوت ═══
if "🌰 الزيوت" in tab_map:
    with tab_map["🌰 الزيوت"]:
        try:
            st.markdown('<div class="section-title">🌰 مكتبة الزيوت</div>',
                unsafe_allow_html=True)
            oil_rows = [{"الحيوان": k, "أقصى %": f"{v['max']}%",
                "مثالي %": f"{v['optimal']}%", "المرجع": v["source"]}
                for k, v in MAX_OIL_PERCENTAGE.items()]
            st.dataframe(pd.DataFrame(oil_rows), use_container_width=True,
                hide_index=True)
            oils = get_oil_ingredients()
            for ing_name, ing_data in oils.items():
                with st.expander(f"🌰 {ing_name}"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("SE", f"{ing_data.get('SE', 0):.0f}")
                    c2.metric("kcal/kg", f"{ing_data.get('SE', 0) * 41:.0f}")
                    c3.metric("السعر", f"${ing_data.get('price', 0):.0f}")
                    st.info(f"📝 {ing_data.get('desc', '')}")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 🍼 بدائل الحليب ═══
if "🍼 بدائل الحليب" in tab_map:
    with tab_map["🍼 بدائل الحليب"]:
        try:
            st.markdown('<div class="section-title">🍼 بدائل الحليب</div>',
                unsafe_allow_html=True)
            mr1, mr2 = st.columns(2)
            with mr1:
                mr_a = st.selectbox("الحيوان:",
                    list(MILK_REPLACER_STANDARDS.keys()), key="mr_a_v1111")
                mr_v = st.number_input("الكمية (كجم):", 1.0, 10000.0, 100.0,
                    10.0, key="mr_v_v1111")
            with mr2:
                std_mr = MILK_REPLACER_STANDARDS[mr_a]
                st.markdown(f"""<div style="background:#f1f8e9; padding:20px;
                    border-radius:16px; border-right:5px solid #2e7d32;">
                    <b>📊 {mr_a}:</b><br>
                    بروتين: {std_mr['CP']}% | دهن: {std_mr['Fat']}% |
                    لاكتوز: {std_mr['Lactose']}%<br>
                    Ca: {std_mr['Ca']}% | P: {std_mr['P']}%
                </div>""", unsafe_allow_html=True)

            mr_sel = []
            cols = st.columns(3)
            for i, (name, data) in enumerate(MILK_REPLACER_INGREDIENTS.items()):
                with cols[i % 3]:
                    with st.expander(f"{name}"):
                        st.caption(f"💵 ${data['price']}/كجم | حد: {data['max']}%")
                        if st.checkbox("إضافة", key=f"mr_{name}_v1111"):
                            mr_sel.append(name)

            if st.button("🧪 تركيب", type="primary",
                    use_container_width=True, key="mr_run_v1111"):
                if len(mr_sel) < 3:
                    st.warning("⚠️ اختر 3 مكونات على الأقل")
                else:
                    with st.spinner("⏳ جاري التركيب..."):
                        r = formulate_milk_replacer(mr_a, mr_v, mr_sel)
                    if r["success"]:
                        quality = r.get("quality_score", 0)
                        meets70 = quality >= 70
                        bg = "quality-good-v113" if meets70 else "quality-bad-v113"
                        st.markdown(f"""<div class="{bg}">
                            <h3 style="color:{'#1b5e20' if meets70 else '#c62828'};
                                margin:0;">جودة: {quality:.1f}%</h3>
                            <p>Ca:P = {r['ca_p_ratio']:.2f}</p>
                        </div>""", unsafe_allow_html=True)
                        if r.get("warning"): st.warning(r["warning"])
                        for ing, pct in r["formula"].items():
                            kg = pct * mr_v / 100.0
                            st.markdown(f'<div class="formula-item">▪️ '
                                f'<b>{ing}:</b> {pct:.2f}% ({kg:.2f} كجم)</div>',
                                unsafe_allow_html=True)
                        st.metric("💰 تكلفة 100 كجم",
                            f"${r['cost_per_100kg']:.2f}")
                        
                        # ✅ PDF مع نظام الموافقة
                        pdf_mr = generate_milk_replacer_pdf(r)
                        if pdf_mr:
                            render_pdf_download_with_approval(
                                pdf_bytes=pdf_mr,
                                file_name=(f"Milk_{mr_a.split()[0]}_"
                                    f"{datetime.now():%Y%m%d}.pdf"),
                                doc_title=f"بديل حليب — {mr_a}",
                                user_role=role,
                                user_name=st.session_state.get(
                                    "chat_username", "مستخدم"),
                                doc_context={
                                    "الحيوان": mr_a,
                                    "الجودة": f"{quality:.1f}%",
                                    "الكمية": f"{mr_v:.0f} كجم"},
                                key_suffix="milk_v1111")
                    else:
                        st.error(f"❌ {r['message']}")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 📷 OCR ═══
if "📷 OCR" in tab_map:
    with tab_map["📷 OCR"]:
        try:
            st.markdown('<div class="section-title">📷 OCR</div>',
                unsafe_allow_html=True)
            if not OCR_AVAILABLE:
                st.error("⚠️ pytesseract غير مثبتة")
            else:
                up = st.file_uploader("ارفع الصورة:",
                    type=["jpg", "jpeg", "png"], key="ocr_upload_v1111")
                if up:
                    uploaded = up.read()
                    st.image(uploaded, caption="الصورة", use_container_width=True)
                    if st.button("🔍 تحليل", type="primary",
                            use_container_width=True, key="ocr_run_v1111"):
                        with st.spinner("🔬 جاري التحليل..."):
                            result = extract_ingredients_from_image(uploaded)
                        if result["success"] and result["count"] > 0:
                            st.success(f"✅ {result['count']} مادة")
                            nut = compute_formula_nutrients(result["ingredients"])
                            st.dataframe(pd.DataFrame([
                                {"المادة": k, "النسبة": v}
                                for k, v in result["ingredients"].items()]),
                                use_container_width=True, hide_index=True)
                            n1, n2, n3, n4 = st.columns(4)
                            n1.metric("CP", f"{nut['CP']:.2f}%")
                            n2.metric("DP", f"{nut['DP']:.2f}%")
                            n3.metric("SE", f"{nut['SE']:.1f}")
                            n4.metric("NDF", f"{nut['NDF']:.2f}%")
                            with st.expander("✏️ تصحيح", expanded=True):
                                corrected = render_ocr_correction_ui(
                                    result["ingredients"])
                                if st.button("✅ تطبيق", type="primary",
                                        use_container_width=True):
                                    if corrected:
                                        st.session_state["last_ocr_result"] = corrected
                                        st.session_state["last_ocr_nutrients"] = \
                                            compute_formula_nutrients(corrected)
                                        st.success("✅"); st.rerun()
                            try:
                                pdf_ocr = pdf_gen.generate_ocr_report(
                                    result["ingredients"], nut,
                                    raw_text=result.get("raw_text", ""))
                                render_pdf_download_with_approval(
                                    pdf_bytes=pdf_ocr,
                                    file_name=f"OCR_{datetime.now():%Y%m%d}.pdf",
                                    doc_title="تحليل OCR — صورة",
                                    user_role=role,
                                    user_name=st.session_state.get(
                                        "chat_username", "مستخدم"),
                                    doc_context={
                                        "عدد المواد": str(result["count"])},
                                    key_suffix="ocr_v1111")
                            except Exception as e:
                                st.warning(f"⚠️ PDF: {e}")
                        else:
                            st.warning(f"⚠️ {result.get('message', '')}")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 🏗️ الحظائر 3D ═══
if "🏗️ الحظائر 3D" in tab_map:
    with tab_map["🏗️ الحظائر 3D"]:
        try:
            st.markdown('<div class="section-title">'
                '🏗️ مصمم الحظائر 3D</div>', unsafe_allow_html=True)

            barn_mode = st.radio("نوع الحساب:",
                ["🏠 حظيرة قياسية", "🐎 مربط خيول علمي"],
                horizontal=True, key="barn_mode_v1111")

            if "🐎" in barn_mode:
                st.markdown("### 🐎 مربط خيول علمي (NRC 2007 + MWPS-1)")

                c1, c2, c3 = st.columns(3)
                with c1:
                    horse_count = st.number_input("🔢 عدد الخيول:",
                        1, 100, 10, 1, key="horse_count_v1111")
                with c2:
                    stall_type = st.selectbox("📦 نوع المربط:",
                        list(HORSE_STALL_SCIENCE.keys()),
                        format_func=lambda k:
                            f"{HORSE_STALL_SCIENCE[k]['name_ar']} — "
                            f"{HORSE_STALL_SCIENCE[k]['width']}×"
                            f"{HORSE_STALL_SCIENCE[k]['length']} م",
                        key="stall_type_v1111")
                with c3:
                    include_service = st.checkbox("🚿 خدمات",
                        value=True, key="service_v1111")

                if st.button("🏗️ حساب المربط", type="primary",
                        use_container_width=True, key="horse_calc_v1111"):
                    dims = calculate_horse_barn_scientific(
                        horse_count, stall_type, include_service)
                    st.session_state["horse_barn_dims"] = dims

                if st.session_state.get("horse_barn_dims"):
                    dims = st.session_state["horse_barn_dims"]

                    st.markdown(f"""<div class="physio-card">
                        <h4>🐎 {dims['stall_type_ar']}</h4>
                        <p style="color:#1a237e; font-size:1.1rem;
                            font-weight:700; margin:0;">
                            {dims['stall_dimensions']} |
                            المساحة: {dims['stall_area_m2']} م²
                        </p>
                        <p style="color:#555; margin:8px 0 0 0;">
                            📖 {dims['reference']}
                        </p>
                    </div>""", unsafe_allow_html=True)

                    with st.expander("📐 معادلات المربط", expanded=False):
                        eqs = get_reference_equations("خيول", "مربط")
                        if eqs:
                            st.markdown(f"**📖 {eqs.get('source', '')}**")
                            for k, v in eqs.items():
                                if k in ("source", "example"): continue
                                st.markdown(f"- **{k}:** {v}")

                    st.markdown("### 📐 الأبعاد الكلية")
                    k1, k2, k3, k4 = st.columns(4)
                    k1.metric("📏 المساحة", f"{dims['total_area_m2']} م²")
                    k2.metric("📐 الأبعاد",
                        f"{dims['building_length_m']}×"
                        f"{dims['building_width_m']} م")
                    k3.metric("🏔️ الارتفاع", f"{dims['building_height_m']} م")
                    k4.metric("📦 الحجم", f"{dims['volume_m3']} م³")

                    k5, k6, k7, k8 = st.columns(4)
                    k5.metric("🐎 مربطات",
                        f"{dims['num_horses']} ({dims['rows_count']} صف × "
                        f"{dims['stalls_per_row']})")
                    k6.metric("🚪 الممر", f"{dims['aisle_width_m']} م")
                    k7.metric("🍽️ معالف", f"{dims['feeders_count']}")
                    k8.metric("💧 سقايات", f"{dims['drinkers_count']}")

                    st.markdown("### 🌀 التهوية")
                    v1, v2, v3, v4 = st.columns(4)
                    v1.metric("💨 الصيف",
                        f"{dims['vent_summer_m3h']:,} م³/س")
                    v2.metric("💨 الشتاء",
                        f"{dims['vent_winter_m3h']:,} م³/س")
                    v3.metric("🌀 مراوح نفق",
                        f"{dims['tunnel_fans_count']}")
                    v4.metric("🌀 مراوح جانبية",
                        f"{dims['side_fans_count']}")

                    st.markdown("### 🚪 الأبواب والنوافذ والفرشة")
                    d1, d2, d3, d4 = st.columns(4)
                    d1.metric("🚪 الأبواب",
                        f"{dims['doors_count']} × {dims['door_dimensions']}")
                    d2.metric("🪟 النوافذ", f"{dims['window_area_m2']} م²")
                    d3.metric("🧱 الحاجز",
                        f"{HORSE_BARN_SCIENCE['front_partition_m']} م")
                    d4.metric("🛏️ الفرشة",
                        f"{dims['bedding_cm']} سم ({dims['bedding_m3']} م³)")

                    st.markdown("### 🏗️ المجسم 3D (إسطبلات كاملة)")
                    try:
                        fig3d = create_barn_3d_figure(dims)
                        if fig3d:
                            st.plotly_chart(fig3d, use_container_width=True)
                    except Exception as e:
                        st.warning(f"⚠️ 3D: {e}")

                    st.markdown("### 💰 التكاليف")
                    cost_data = {
                        "الهيكل": dims['cost_structure_usd'],
                        "السقف": dims['cost_roof_usd'],
                        "المربطات": dims['cost_stalls_usd'],
                        "الممر": dims['cost_aisle_floor_usd'],
                        "الخدمات": dims['cost_service_usd'],
                        "التهوية": dims['cost_ventilation_usd'],
                        "الإضاءة": dims['cost_lighting_usd'],
                        "النوافذ": dims['cost_windows_usd']}
                    cost_df = pd.DataFrame([
                        {"البند": k, "التكلفة ($)": f"${v:,.0f}"}
                        for k, v in cost_data.items()])
                    st.dataframe(cost_df, use_container_width=True,
                        hide_index=True)
                    st.metric("💰 إجمالي", f"${dims['cost_total_usd']:,.0f}")

                    # ✅ PDF مع نظام الموافقة
                    try:
                        pdf_b = generate_barn_pdf_report(dims)
                        render_pdf_download_with_approval(
                            pdf_bytes=pdf_b,
                            file_name=(f"Horse_Barn_{horse_count}_"
                                f"{datetime.now():%Y%m%d}.pdf"),
                            doc_title=f"مربط خيول — {horse_count} حصان",
                            user_role=role,
                            user_name=st.session_state.get(
                                "chat_username", "مستخدم"),
                            doc_context={
                                "عدد الخيول": str(horse_count),
                                "نوع المربط": dims['stall_type_ar'],
                                "المساحة": f"{dims['total_area_m2']} م²"},
                            key_suffix="horse_barn_v1111")
                    except Exception as e:
                        st.error(f"⚠️ PDF: {e}")
            else:
                c1, c2, c3 = st.columns(3)
                with c1:
                    barn_a = st.selectbox("🐾 الحيوان:",
                        list(BARN_DESIGN_STANDARDS.keys()),
                        format_func=lambda k:
                            BARN_DESIGN_STANDARDS[k]["name_ar"],
                        key="barn_animal_v1111")
                with c2:
                    barn_c = st.number_input("🔢 العدد:", 1, 100000, 1000, 50,
                        key="barn_count_v1111")
                with c3:
                    barn_s = st.selectbox("🏠 النظام:",
                        ["أرضي مفتوح", "بطاريات"], key="barn_system_v1111")

                dims = calculate_barn_dimensions(barn_a, barn_c, barn_s)
                if dims:
                    k1, k2, k3, k4 = st.columns(4)
                    k1.metric("📏 المساحة", f"{dims['total_area_m2']} م²")
                    k2.metric("📐 الأبعاد",
                        f"{dims['length_m']}×{dims['width_m']} م")
                    k3.metric("🏔️ القمة", f"{dims['ridge_height_m']} م")
                    k4.metric("📦 الحجم", f"{dims['volume_m3']} م³")

                    v1, v2, v3, v4 = st.columns(4)
                    v1.metric("🌀 مراوح نفق",
                        f"{dims['tunnel_fans_count']}")
                    v2.metric("🌀 مراوح جانبية",
                        f"{dims['side_fans_count']}")
                    v3.metric("❄️ ألواح تبريد",
                        f"{dims['cooling_pad_area_m2']} م²"
                        if dims.get("cooling_pad_enabled") else "—")
                    v4.metric("💧 ماء/يوم",
                        f"{dims['water_per_day_L']:,.0f} لتر")

                    fig3d = create_barn_3d_figure(dims)
                    if fig3d:
                        st.plotly_chart(fig3d, use_container_width=True)

                    # ✅ PDF مع نظام الموافقة
                    try:
                        pdf_b = generate_barn_pdf_report(dims)
                        render_pdf_download_with_approval(
                            pdf_bytes=pdf_b,
                            file_name=f"Barn_{barn_a}_{datetime.now():%Y%m%d}.pdf",
                            doc_title=f"حظيرة {barn_a} — {barn_c} رأس",
                            user_role=role,
                            user_name=st.session_state.get(
                                "chat_username", "مستخدم"),
                            doc_context={
                                "الحيوان": barn_a,
                                "العدد": str(barn_c),
                                "المساحة": f"{dims['total_area_m2']} م²"},
                            key_suffix="barn_v1111")
                    except Exception as e:
                        st.error(f"⚠️ PDF: {e}")
        except Exception as e:
            st.error(f"⚠️ {e}")
            with st.expander("التفاصيل"): st.code(traceback.format_exc())


# ═══ 📊 الجدوى ═══
if "📊 الجدوى" in tab_map:
    with tab_map["📊 الجدوى"]:
        try:
            st.markdown('<div class="section-title">📊 دراسة الجدوى</div>',
                unsafe_allow_html=True)
            mode = st.radio("النوع:",
                ["🔬 فنية", "💰 اقتصادية"], horizontal=True,
                key="feas_mode_v1111")
            f1, f2 = st.columns(2)
            with f1:
                feas_k = st.selectbox("الحيوان:",
                    list(BARN_DESIGN_STANDARDS.keys()),
                    format_func=lambda k: BARN_DESIGN_STANDARDS[k]["name_ar"],
                    key="feas_animal_v1111")
                feas_c = st.number_input("العدد:", 1, 100000, 1000, 50,
                    key="feas_count_v1111")
            with f2:
                if "اقتصادية" in mode:
                    fp = st.number_input("💵 سعر العلف:",
                        50.0, 5000.0, 350.0, 10.0, key="feas_fp_v1111")
                    pp = st.number_input("💵 سعر المنتج:",
                        0.1, 10000.0, 2.5, 0.1, key="feas_pp_v1111")

            std = BARN_DESIGN_STANDARDS.get(feas_k)
            if std:
                dims = calculate_barn_dimensions(feas_k, feas_c)
                if dims:
                    fc1, fc2, fc3, fc4 = st.columns(4)
                    fc1.metric("📏 المساحة", f"{dims['total_area_m2']} م²")
                    fc2.metric("📦 الحجم", f"{dims['volume_m3']} م³")
                    fc3.metric("💧 ماء/يوم",
                        f"{dims['water_per_day_L']:.0f} لتر")
                    fc4.metric("💰 تكلفة الحظيرة",
                        f"${dims['cost_total_usd']:,.0f}")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 🐔 المزارع ═══
if "🐔 المزارع" in tab_map:
    with tab_map["🐔 المزارع"]:
        try:
            st.markdown('<div class="section-title">🐔 إدارة المزارع</div>',
                unsafe_allow_html=True)
            farms = st.session_state["broiler_farms"]
            with st.form("new_farm_v1111", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    nf_name = st.text_input("اسم المزرعة *", key="nf_n_v1111")
                    nf_strain = st.selectbox("السلالة",
                        ["Ross 308", "Cobb 500"], key="nf_s_v1111")
                with c2:
                    nf_birds = st.number_input("الطيور:", 100, 100000, 1000,
                        50, key="nf_b_v1111")
                    nf_date = st.date_input("التاريخ", key="nf_d_v1111")
                if st.form_submit_button("💾 حفظ", type="primary",
                        use_container_width=True) and nf_name:
                    if nf_name not in farms:
                        farms[nf_name] = {"strain": nf_strain,
                            "start_birds": nf_birds,
                            "start_date": str(nf_date), "records": []}
                        st.success(f"✅ {nf_name}"); st.rerun()
                    else:
                        st.warning("⚠️ موجودة")

            if farms:
                sel = st.selectbox("اختر مزرعة:", list(farms.keys()),
                    key="farm_sel_v1111")
                farm = farms[sel]
                st.markdown(f"### 📝 {farm['strain']} — قراءة يومية")
                with st.form(f"rec_{sel}_v1111"):
                    rc = st.columns(3)
                    with rc[0]:
                        age = st.number_input("العمر", 1, 60, 1,
                            key="r_age_v1111")
                    with rc[1]:
                        alive = st.number_input("حي", 1, farm["start_birds"],
                            value=farm["start_birds"], key="r_alive_v1111")
                    with rc[2]:
                        wt = st.number_input("وزن (كجم)", 0.01, 5.0, 0.045,
                            0.005, key="r_wt_v1111")
                    if st.form_submit_button("➕ تسجيل", type="primary",
                            use_container_width=True):
                        farm["records"].append({
                            "date": str(datetime.now().date()),
                            "age": age, "alive": alive, "wt": wt})
                        st.success("✅"); st.rerun()
                if farm["records"]:
                    latest = farm["records"][-1]
                    liv = (latest["alive"] / farm["start_birds"] * 100)
                    m = st.columns(3)
                    m[0].metric("🐦 حيوية", f"{liv:.1f}%")
                    m[1].metric("⚖️ الوزن", f"{latest['wt']:.3f} كجم")
                    m[2].metric("📅 العمر", f"{latest['age']} يوم")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ تبويبات المالك ═══
if role == "owner":
    # 🏭 المستودعات
    if "🏭 المستودعات" in tab_map:
        with tab_map["🏭 المستودعات"]:
            try:
                st.markdown('<div class="section-title">🏭 المستودعات</div>',
                    unsafe_allow_html=True)
                inv = st.session_state["inventory"]
                q = [v["quantity"] for v in inv.values()]
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("📦 المواد", len(inv))
                c2.metric("🟢 آمنة", sum(1 for x in q if x >= 5))
                c3.metric("🟡 منخفضة", sum(1 for x in q if 0 < x < 5))
                c4.metric("🔴 نافذة", sum(1 for x in q if x <= 0))
                inv_df = pd.DataFrame([{"المادة": name,
                    "الكمية (طن)": inv[name]["quantity"],
                    "الحد الأدنى": inv[name]["min_threshold"]}
                    for name in inv.keys()])
                edited = st.data_editor(inv_df, use_container_width=True,
                    hide_index=True, column_config={
                        "المادة": st.column_config.TextColumn(disabled=True),
                        "الكمية (طن)": st.column_config.NumberColumn(
                            min_value=0.0, step=1.0),
                        "الحد الأدنى": st.column_config.NumberColumn(
                            min_value=0.0, step=1.0)},
                    key="inv_editor_v1111")
                if st.button("💾 حفظ", type="primary", use_container_width=True):
                    for _, r in edited.iterrows():
                        name = r["المادة"]
                        inv[name]["quantity"] = float(r["الكمية (طن)"])
                        inv[name]["min_threshold"] = float(r["الحد الأدنى"])
                    st.success("✅"); st.rerun()
            except Exception as e:
                st.error(f"⚠️ {e}")

    # 📋 طلبات PDF — التبويب الجديد
    if "📋 طلبات PDF" in tab_map:
        with tab_map["📋 طلبات PDF"]:
            try:
                render_pdf_requests_admin()
            except Exception as e:
                st.error(f"⚠️ {e}")
                with st.expander("التفاصيل"):
                    st.code(traceback.format_exc())

    # 🧾 الفواتير
    if "🧾 الفواتير" in tab_map:
        with tab_map["🧾 الفواتير"]:
            try:
                st.markdown('<div class="section-title">🧾 الفواتير</div>',
                    unsafe_allow_html=True)
                st.info("💡 نظام فواتير كامل")
            except Exception as e:
                st.error(f"⚠️ {e}")

    # 🖨️ الديباجة
    if "🖨️ الديباجة" in tab_map:
        with tab_map["🖨️ الديباجة"]:
            try:
                st.markdown('<div class="section-title">🖨️ الديباجة</div>',
                    unsafe_allow_html=True)
                st.markdown(f"""<div style="border:3px solid #1b5e20;
                    padding:50px 30px; border-radius:15px;
                    background:linear-gradient(135deg,#f1f8e9,#e8f5e9);
                    direction:rtl; text-align:center;">
                    <h1 style="color:#1b5e20;">{APP_NAME}</h1>
                    <h3 style="color:#1565C0;">{APP_TAGLINE}</h3>
                    <h2 style="color:#c62828;">{SUPERVISOR}</h2>
                    <p style="color:#0d47a1;">{SUPERVISOR_TITLE}</p>
                    <p>📅 {datetime.now():%Y-%m-%d}</p>
                    <p style="color:#c62828;">🤲 {DUA_SHORT} 🤲</p>
                </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"⚠️ {e}")

    # 📈 التحليلات
    if "📈 التحليلات" in tab_map:
        with tab_map["📈 التحليلات"]:
            try:
                st.markdown('<div class="section-title">📈 التحليلات</div>',
                    unsafe_allow_html=True)
                n_formulas = len(st.session_state.get(
                    "formulation_history", []))
                m1, m2, m3 = st.columns(3)
                m1.metric("🧬 خلطات", n_formulas)
                m2.metric("🐔 مزارع",
                    len(st.session_state.get("broiler_farms", {})))
                m3.metric("📦 مواد",
                    len(st.session_state.get("inventory", {})))
                history = st.session_state.get("formulation_history", [])
                if history:
                    st.dataframe(pd.DataFrame(history),
                        use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"⚠️ {e}")


# ═══ 💬 غرفة التواصل ═══
if "💬 غرفة التواصل" in tab_map:
    with tab_map["💬 غرفة التواصل"]:
        try:
            st.markdown('<div class="section-title">💬 غرفة التواصل</div>',
                unsafe_allow_html=True)
            st.caption("🔒 نقاش علمي — مشاركة العلفة والنتائج")

            rooms = _load_chat_rooms()
            for dr in ["🌾 النقاش العام", "🧬 نقاش علمي", "💰 نقاش اقتصادي"]:
                if dr not in rooms: rooms[dr] = []
            _save_chat_rooms(rooms)

            c1, c2, c3 = st.columns([0.5, 0.25, 0.25])
            with c1:
                current_room = st.selectbox("🏠 الغرفة:",
                    list(rooms.keys()), key="comm_room_v1111")
            with c2:
                if role in ("owner", "specialist"):
                    if st.button("➕ غرفة جديدة", use_container_width=True,
                            key="comm_new_v1111"):
                        st.session_state["show_new_room"] = True
            with c3:
                if role == "owner" and st.button("🗑️ حذف",
                        use_container_width=True, key="comm_del_v1111"):
                    if current_room in rooms and len(rooms) > 1:
                        del rooms[current_room]
                        _save_chat_rooms(rooms); st.rerun()

            if st.session_state.get("show_new_room"):
                nr = st.text_input("اسم الغرفة:", key="comm_nr_v1111")
                if st.button("إنشاء", key="comm_nr_btn_v1111") and nr:
                    if create_chat_room(nr):
                        st.session_state["show_new_room"] = False; st.rerun()

            username = _safe_username()
            st.caption(f"👤 {username} | 🏠 {current_room} | "
                f"عدد: {len(rooms.get(current_room, []))}")

            msgs = rooms.get(current_room, [])[-80:]
            chat_html = ('<div style="background:#fafafa; padding:15px; '
                'border-radius:14px; height:450px; overflow-y:auto; '
                'border:1px solid #e0e0e0; direction:rtl;">')
            if not msgs:
                chat_html += ('<p style="text-align:center;color:#999;">'
                              'لا رسائل — كن أول من يكتب 👋</p>')
            for m in msgs:
                is_mine = (m["user"] == username)
                role_icon = {"owner": "👑", "specialist": "🔬",
                    "guest": "👥"}.get(m.get("role", "guest"), "")
                bg = "#dcedc8" if is_mine else "#e3f2fd"
                nc = "#1b5e20" if is_mine else "#1565c0"
                chat_html += (f'<div style="background:{bg}; '
                    f'padding:8px 14px; border-radius:10px; '
                    f'margin-bottom:6px; border-right:3px solid {nc};">'
                    f'<b style="color:{nc};">{role_icon} {m["user"]}</b> '
                    f'<small style="color:#888;">{m["ts"]}</small><br>'
                    f'<span style="white-space:pre-wrap;">{m["msg"]}</span></div>')
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)

            with st.form(f"comm_form_{current_room}_v1111",
                    clear_on_submit=True):
                msg_text = st.text_area("✍️ رسالتك:", height=80,
                    key=f"comm_msg_{current_room}_v1111")
                cc1, cc2 = st.columns([0.75, 0.25])
                with cc1:
                    share_formula = st.checkbox("📎 إرفاق التركيبة",
                        value=False, key="comm_attach_v1111")
                with cc2:
                    send = st.form_submit_button("📤 إرسال", type="primary",
                        use_container_width=True)
                if send:
                    if not check_rate_limit("comm", max_calls=30, window=60):
                        st.warning("⏳ تهدئة")
                    else:
                        final_msg = msg_text
                        if share_formula:
                            active = st.session_state.get("active_formula", {})
                            if active:
                                fs = " | ".join(f"{k}: {v:.1f}%"
                                    for k, v in active.items())
                                final_msg += f"\n\n📋 التركيبة:\n{fs}"
                        if add_chat_message(current_room, username, final_msg):
                            st.rerun()

            if st.button("🔄 تحديث", key="comm_refresh_v1111"):
                st.rerun()
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 🎬 الاستديو ═══
if "🎬 الاستديو" in tab_map:
    with tab_map["🎬 الاستديو"]:
        try:
            st.markdown('<div class="section-title">🎬 الاستديو</div>',
                unsafe_allow_html=True)
            studio = _load_studio()
            sub_s1, sub_s2, sub_s3 = st.tabs(
                ["📹 فيديوهات", "📊 شرائح", "📝 ملاحظات"])
            with sub_s1:
                with st.form("sv_v1111"):
                    vt = st.text_input("العنوان:", key="vid_t_v1111")
                    vu = st.text_input("رابط:", key="vid_u_v1111")
                    vd = st.text_area("الوصف:", key="vid_d_v1111")
                    if st.form_submit_button("➕ إضافة", type="primary"):
                        if vt and vu:
                            studio["videos"].append({
                                "title": _sanitize_message(vt, 100),
                                "url": _sanitize_message(vu, 500),
                                "desc": _sanitize_message(vd, 500),
                                "ts": datetime.now().strftime("%Y-%m-%d %H:%M")})
                            _save_studio(studio); st.rerun()
                for i, v in enumerate(studio["videos"]):
                    with st.expander(f"🎬 {v['title']} — {v['ts']}"):
                        st.markdown(f"🔗 [فتح]({v['url']})")
                        if v.get("desc"): st.caption(v["desc"])
                        if st.button("🗑️", key=f"del_vid_{i}_v1111"):
                            studio["videos"].pop(i)
                            _save_studio(studio); st.rerun()
            with sub_s2:
                with st.form("ss_v1111"):
                    s_title = st.text_input("العنوان:", key="sl_t_v1111")
                    s_url = st.text_input("رابط الصورة:", key="sl_u_v1111")
                    if st.form_submit_button("➕ إضافة", type="primary"):
                        if s_title and s_url:
                            studio["slides"].append({
                                "title": _sanitize_message(s_title, 100),
                                "url": _sanitize_message(s_url, 500),
                                "ts": datetime.now().strftime("%Y-%m-%d %H:%M")})
                            _save_studio(studio); st.rerun()
                for i, s in enumerate(studio["slides"]):
                    st.markdown(f"**{s['title']}**")
                    try: st.image(s["url"], use_container_width=True)
                    except Exception: st.caption(f"🔗 {s['url']}")
                    if st.button("🗑️", key=f"del_sl_{i}_v1111"):
                        studio["slides"].pop(i)
                        _save_studio(studio); st.rerun()
            with sub_s3:
                with st.form("sn_v1111"):
                    nt = st.text_area("ملاحظة:", key="note_t_v1111")
                    if st.form_submit_button("➕ حفظ", type="primary"):
                        if nt.strip():
                            studio["notes"].append({
                                "text": _sanitize_message(nt, 1000),
                                "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "author": _safe_username()})
                            _save_studio(studio); st.rerun()
                for i, n in enumerate(reversed(studio["notes"])):
                    ri = len(studio["notes"]) - 1 - i
                    st.markdown(f'<div class="formula-item">'
                        f'<b>{n["author"]}</b> — '
                        f'<small>{n["ts"]}</small><br>{n["text"]}</div>',
                        unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_note_{ri}_v1111"):
                        studio["notes"].pop(ri)
                        _save_studio(studio); st.rerun()
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 📚 المراجع ═══
if "📚 المراجع" in tab_map:
    with tab_map["📚 المراجع"]:
        try:
            st.markdown('<div class="section-title">📚 المراجع</div>',
                unsafe_allow_html=True)
            st.markdown("### 🎯 مراجع حسب الحالة")
            ref_animal = st.selectbox("اختر الحيوان:",
                ["أبقار", "أغنام", "ماعز", "إبل", "خيول",
                 "دواجن", "سمان", "أسماك", "أرانب"], key="ref_animal_v1111")
            ref_prod_map = {
                "أبقار": ["حليب_عالي", "حليب_متوسط", "حليب_منخفض",
                          "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"],
                "أغنام": ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد",
                          "مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
                "ماعز": ["تسمين_جديان", "تيوس", "حلابة_عالي",
                         "حلابة_متوسط", "حامل_أخير", "صيانة"],
                "إبل": ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
                "خيول": ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار",
                         "مرضعات", "صيانة", "مربط"],
                "دواجن": ["لاحم", "بياض"],
                "سمان": ["تسمين", "بياض"],
                "أسماك": ["بادئ زريعة", "نمو", "تسمين"],
                "أرانب": ["تسمين", "حليب", "صيانة"]}
            ref_prod = st.selectbox("نوع الإنتاج:",
                ref_prod_map.get(ref_animal, ["عام"]), key="ref_prod_v1111")

            refs = get_references(ref_animal, ref_prod)
            eqs = get_reference_equations(ref_animal, ref_prod)

            st.markdown(f"""<div class="physio-card">
                <h4>📖 المرجع الأساسي</h4>
                <p style="color:#1a237e; font-size:1.15rem;
                    font-weight:700; margin:0;">{refs['primary']}</p>
                <p style="color:#555; margin:8px 0 0 0;">
                    📑 <b>الجدول:</b> {refs.get('table', '—')}</p>
            </div>""", unsafe_allow_html=True)

            if eqs:
                st.markdown("### 📐 المعادلات المرجعية")
                eq_data = []
                for k, v in eqs.items():
                    if k in ("source", "example"): continue
                    eq_data.append({"المؤشر": k, "المعادلة": v})
                if eq_data:
                    st.table(pd.DataFrame(eq_data))
                if eqs.get("source"):
                    st.caption(f"📖 المصدر: {eqs['source']}")
                if eqs.get("example"):
                    st.info(f"💡 **مثال:** {eqs['example']}")

            if refs.get("secondary"):
                st.markdown("### 📚 مراجع داعمة")
                for s in refs["secondary"]: st.markdown(f"- {s}")

            st.markdown("---")
            st.markdown("### 📖 المراجع العامة")
            for i, ref in enumerate(GENERAL_REFERENCES, 1):
                st.markdown(f"{i}. {ref}")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 💡 المساعدة ═══
if "💡 المساعدة" in tab_map:
    with tab_map["💡 المساعدة"]:
        try:
            st.markdown('<div class="section-title">💡 المساعدة</div>',
                unsafe_allow_html=True)
            st.markdown(f"""
### الأسئلة الشائعة:

**1. كيف أبدأ؟**
- اختر الحيوان → فعّل ✅ → اختر 3+ مكونات → 🚀

**2. ما الجديد في v11.11.0؟**
- ✅ **نظام موافقة PDF** — الزائر/المختص يحتاجون موافقة المالك
- ✅ **فيديو تعريفي عند الفتح**
- ✅ **3D إسطبلات خيول كاملة** (بأبواب + حصان + معلف + دلو)
- ✅ **شريط القياس بأسهم دقيقة على الصورة**
- ✅ **أزرار استشارة** (واتساب + بريد + اتصال) في كل PDF

**3. كيف أحصل على PDF؟**
- 🧑‍💼 **المالك:** تحميل مباشر
- 👥 **الزائر والمختص:** طلب موافقة → انتظار → تحميل

**4. أين تظهر أزرار الاستشارة؟**
- في كل مكان يحتوي على PDF
- 3 أزرار: 📱 واتساب + ✉️ بريد + 📞 اتصال

**5. كيف أضيف الفيديو التعريفي؟**
- احفظ الفيديو باسم `intro_video.mp4` في مجلد التطبيق

### 📞 التواصل المباشر
- 📱 {WHATSAPP_NUMBER}
- 📧 {OWNER_EMAIL}

{DUA_FULL}
""")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 📖 الدليل ═══
if "📖 الدليل" in tab_map:
    with tab_map["📖 الدليل"]:
        try:
            st.markdown('<div class="section-title">📖 دليل المستخدم</div>',
                unsafe_allow_html=True)
            st.markdown(f"""
### 🎯 الغرض
**{APP_NAME} v{APP_VERSION}** — منصة ذكية لتركيب الأعلاف.

### ✨ الميزات الرئيسية
- 🐄 9 قطاعات × متغيرات متعددة
- 🌰 {len(get_oil_ingredients())} زيتاً + معايير
- 🧬 DP/CP
- ✅ ضمان جودة ≥ 70%
- 🎯 محرك NLP (SLSQP)
- 📏 شريط قياس بصور حيوانات مع أسهم
- 🧪 مختبر بالمكتبة الكاملة
- 💬 غرفة تواصل
- 🎬 استديو
- 📷 OCR
- 🏗️ حظائر 3D + **إسطبلات خيول كاملة**
- 📊 جدوى
- 🍼 بدائل حليب
- 📄 PDF بختم رسمي + مراجع NRC + **نظام موافقة**
- 📱 مشاركة واتساب + بريد + **استشارة مباشرة**
- 🎬 فيديو تعريفي عند الفتح

### 🆕 v11.11.0 (هذا التحديث):
- ✅ **نظام موافقة PDF كامل**
- ✅ **3 أزرار استشارة** في كل PDF
- ✅ **فيديو تعريفي** عند فتح التطبيق
- ✅ **3D إسطبلات خيول** بأبواب وحصان ومعلف ودلو
- ✅ **شريط القياس** بأسهم دقيقة على صورة الحيوان
- ✅ **تبويب إدارة طلبات PDF** للمالك

### 🔐 بوابات الدخول
- 👑 **المالك:** كود آمن + تحميل PDF مباشر + إدارة طلبات
- 🔬 **المختص:** دخول مباشر (PDF بموافقة المالك)
- 👥 **الزائر:** مجاني بحاسبة + مختبر + PDF (بموافقة)

### 📞 التواصل
📧 {OWNER_EMAIL}
📱 {WHATSAPP_NUMBER}

---
{DUA_FULL}
""")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════
# التذييل
# ═══════════════════════════════════════════════════════════════════════

st.markdown(f'<div class="mini-signature">🌾 {APP_NAME} '
    f'v{APP_VERSION} | {SUPERVISOR} © 2026</div>',
    unsafe_allow_html=True)
st.markdown(f'<div class="dua-fixed-banner">🤲 {DUA_SHORT} 🤲</div>',
    unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# نهاية الملف — Tawor Nology 11.11.0 ✅
# ═══════════════════════════════════════════════════════════════════════
