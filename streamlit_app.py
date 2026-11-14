# ═══════════════════════════════════════════════════════════════════════
# تاور نولجي TAWOR NOLOGY 11.10
# د. عبدالقادر إسماعيل تاور
# 🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام 🕌
# ═══════════════════════════════════════════════════════════════════════
# جديد v11.10:
#   ✅ مختبر تحليل التركيبات الجاهزة (يعمل في كل البوابات)
#   ✅ صفحة مراجع في كل تقارير PDF
#   ✅ PDF الزائر محسّن + مراجع
#   ✅ 3 طرق إدخال للمختبر (جدول / نص / آخر تركيبة)
#   ✅ تحقق توازن الطاقة/البروتين في المختبر
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
# 📚 v11.10 — قاموس المراجع العلمية
# ═══════════════════════════════════════════════════════════════════════

STANDARD_REFERENCES = {
    "أبقار_حليب_عالي": {
        "primary": "NRC (2001) — Nutrient Requirements of Dairy Cattle, 7th Ed.",
        "table": "Table 15-1: Lactating dairy cows (high production)",
        "secondary": ["INRA (2018) — Feeding System for Ruminants",
                      "NRC (2001) — Table 15-2: Dry matter intake"]},
    "أبقار_حليب_متوسط": {
        "primary": "NRC (2001) — Dairy Cattle, 7th Ed.",
        "table": "Table 15-1: Lactating dairy cows (medium)",
        "secondary": ["INRA (2018) — Ruminant Feeding"]},
    "أبقار_حليب_منخفض": {
        "primary": "NRC (2001) — Dairy Cattle",
        "table": "Table 15-1: Low production cows",
        "secondary": ["INRA (2018)"]},
    "أبقار_تسمين_مكثف": {
        "primary": "NRC (2001) + NRC (1996) — Beef Cattle",
        "table": "Table 15-1: Growing/finishing cattle",
        "secondary": ["INRA (2018) — Fattening systems"]},
    "أبقار_تسمين_عادي": {
        "primary": "NRC (1996) — Beef Cattle, 7th Ed.",
        "table": "Table 10-1: Beef cattle growth",
        "secondary": ["INRA (2018)"]},
    "أبقار_حمل_أخير": {
        "primary": "NRC (2001) — Dairy Cattle",
        "table": "Table 15-3: Gestating cows",
        "secondary": ["INRA (2018)"]},
    "أبقار_صيانة": {
        "primary": "NRC (2001) — Dairy Cattle",
        "table": "Table 15-4: Maintenance",
        "secondary": []},
    "أغنام_تسمين_مكثف": {
        "primary": "NRC (2007) — Small Ruminants",
        "table": "Table 11-1: Growing lambs (high ADG)",
        "secondary": ["INRA (2018) — Sheep nutrition"]},
    "أغنام_تسمين_عادي": {
        "primary": "NRC (2007) — Small Ruminants",
        "table": "Table 11-1: Growing lambs",
        "secondary": ["INRA (2018)"]},
    "أغنام_مرضعات": {
        "primary": "NRC (2007) — Small Ruminants",
        "table": "Table 11-2: Lactating ewes",
        "secondary": ["INRA (2018) — Lactation"]},
    "أغنام_حامل_أخير": {
        "primary": "NRC (2007) — Small Ruminants",
        "table": "Table 11-2: Late gestation",
        "secondary": []},
    "أغنام_حامل_متوسط": {
        "primary": "NRC (2007)",
        "table": "Table 11-2: Mid gestation",
        "secondary": []},
    "أغنام_صيانة": {
        "primary": "NRC (2007)",
        "table": "Table 11-3: Maintenance",
        "secondary": []},
    "أغنام_حملان_تيد": {
        "primary": "NRC (2007)",
        "table": "Table 11-1: Early weaned lambs",
        "secondary": []},
    "ماعز_حلابة_عالي": {
        "primary": "NRC (2007) — Small Ruminants",
        "table": "Table 12-1: Lactating dairy goats",
        "secondary": ["INRA (2018) — Goat nutrition"]},
    "ماعز_حلابة_متوسط": {
        "primary": "NRC (2007)",
        "table": "Table 12-1: Medium production goats",
        "secondary": ["INRA (2018)"]},
    "ماعز_تسمين_جديان": {
        "primary": "NRC (2007)",
        "table": "Table 12-2: Growing goat kids",
        "secondary": []},
    "ماعز_تيوس": {
        "primary": "NRC (2007)",
        "table": "Table 12-2: Finishing bucks",
        "secondary": []},
    "ماعز_صيانة": {
        "primary": "NRC (2007)",
        "table": "Table 12-3: Maintenance",
        "secondary": []},
    "ماعز_حامل_أخير": {
        "primary": "NRC (2007)",
        "table": "Table 12-2: Late gestation",
        "secondary": []},
    "إبل_حليب": {
        "primary": "FAO (2010) — Camel Nutrition",
        "table": "Section 4: Lactating camels",
        "secondary": ["Al-Jassim et al. (2002) — Camel milk"]},
    "إبل_تسمين": {
        "primary": "FAO (2010)",
        "table": "Section 5: Fattening",
        "secondary": []},
    "إبل_نمو": {
        "primary": "FAO (2010)",
        "table": "Section 3: Growth",
        "secondary": []},
    "إبل_سباق": {
        "primary": "FAO (2010)",
        "table": "Section 6: Racing performance",
        "secondary": []},
    "إبل_صيانة": {
        "primary": "FAO (2010)",
        "table": "Section 2: Maintenance",
        "secondary": []},
    "خيول_رياضة_مكثف": {
        "primary": "NRC (2007) — Nutrient Requirements of Horses, 6th Ed.",
        "table": "Table 10-1: Intense work",
        "secondary": []},
    "خيول_رياضة_عادي": {
        "primary": "NRC (2007) — Horses",
        "table": "Table 10-1: Moderate work",
        "secondary": []},
    "خيول_نمو_أمهار": {
        "primary": "NRC (2007) — Horses",
        "table": "Table 10-2: Growing horses",
        "secondary": []},
    "خيول_مرضعات": {
        "primary": "NRC (2007) — Horses",
        "table": "Table 10-3: Lactating mares",
        "secondary": []},
    "خيول_صيانة": {
        "primary": "NRC (2007) — Horses",
        "table": "Table 10-4: Maintenance",
        "secondary": []},
    "دواجن_لاحم": {
        "primary": "Ross 308 (2020) — Broiler Nutrition Specification",
        "table": "Nutrient requirements by age",
        "secondary": ["NRC (1994) — Poultry, 9th Ed.",
                      "Aviagen (2022) — Ross 308 Handbook"]},
    "دواجن_بياض": {
        "primary": "NRC (1994) — Poultry, 9th Ed.",
        "table": "Table 4: Laying hens",
        "secondary": ["Lohmann (2020) — Layer Management Guide"]},
    "سمان_تسمين": {
        "primary": "NRC (1994) — Poultry",
        "table": "Table 12: Japanese quail",
        "secondary": ["Minvielle (2004) — Quail nutrition"]},
    "سمان_بياض": {
        "primary": "NRC (1994) — Poultry",
        "table": "Table 12: Laying quail",
        "secondary": []},
    "أسماك_بادئ": {
        "primary": "NRC (2011) — Fish and Shrimp Nutrition",
        "table": "Table 6-1: Tilapia starter",
        "secondary": ["FAO (2018) — Aquaculture Nutrition"]},
    "أسماك_نمو": {
        "primary": "NRC (2011)",
        "table": "Table 6-2: Tilapia growth",
        "secondary": []},
    "أسماك_تسمين": {
        "primary": "NRC (2011)",
        "table": "Table 6-3: Finishing tilapia",
        "secondary": []},
    "أرانب_تسمين": {
        "primary": "NRC (2007) — Small Ruminants & Rabbits",
        "table": "Rabbit chapter",
        "secondary": ["INRA (2018) — Rabbit feeding"]},
    "أرانب_حليب": {
        "primary": "NRC (2007)",
        "table": "Lactating does",
        "secondary": []},
    "أرانب_صيانة": {
        "primary": "NRC (2007)",
        "table": "Maintenance rabbits",
        "secondary": []},
}

GENERAL_REFERENCES = [
    "NRC (2001) — Nutrient Requirements of Dairy Cattle, 7th Ed., NAS Press",
    "NRC (2007) — Nutrient Requirements of Small Ruminants, NAS Press",
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
    if key in STANDARD_REFERENCES:
        return STANDARD_REFERENCES[key]
    for k, v in STANDARD_REFERENCES.items():
        if k.startswith(f"{animal_type}_"):
            return v
    return {"primary": "NRC (2012) — general",
            "table": "—",
            "secondary": ["INRA (2018)", "FAO (2010)"]}


# ═══════════════════════════════════════════════════════════════════════
# 🎯 NLP Helper
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
    tips = ["➕ أضف مكوناً عالي الطاقة (ذرة، زيت)",
            "➕ أضف مكوناً عالي البروتين (صويا، سمك)",
            "🔓 ارفع الحد الأقصى",
            "⬇️ خفّض ME/CP يدوياً"]
    return {"issues": issues, "max_me": round(max_me, 1),
            "max_cp": round(max_cp, 2), "tips": tips}


# ═══════════════════════════════════════════════════════════════════════
# NLP محسّن — 8 مستويات + penalty
# ═══════════════════════════════════════════════════════════════════════

def nlp_optimize_feed(ingredient_names, ingredient_data, prices,
                       animal_type="أبقار", production_type="حليب_عالي",
                       target_me=None, target_cp=None, price_product=2.5,
                       max_per_ing=0.6, verbose=False):
    n = len(ingredient_names)
    if n < 2:
        return {"success": False, "message": "يلزم مكونان على الأقل"}
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
            lb = max(MIN_USE, lim[0] / 100.0)
            ub = min(max_per_ing, lim[1] / 100.0)
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
                A_ub.append([-x for x in bal_row])
                b_ub.append(-0.10)
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
                    attempts_log.append((level_name, "SLSQP فشل", False))
                    continue
                x_norm = np.clip(res.x, 0, None); ss = x_norm.sum()
                if ss <= 0: continue
                x_norm = x_norm / ss
                actual_me = float(np.dot(me_vals, x_norm)) * 100
                actual_cp = float(np.dot(cp_vals, x_norm)) * 100
                if actual_me >= tme*0.98 and actual_cp >= tcp*0.98:
                    best = (res, x_norm, level_name, mult, actual_me, actual_cp)
                    attempts_log.append((level_name, "✅ نجح", True))
                    break
                else:
                    attempts_log.append((level_name,
                        f"قيود (ME={actual_me:.0f}, CP={actual_cp:.1f})", False))
            except Exception as e:
                attempts_log.append((level_name, f"استثناء: {e}", False))
                continue
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
                        float(np.dot(cp_vals, x_norm))*100)
                break
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
        warning = (f"⚠️ خُففت القيود إلى {mult*100:.0f}% "
                   f"(ME={actual_me:.0f}/{target_me:.0f}، "
                   f"CP={actual_cp:.2f}/{target_cp:.2f})")
    if mult < 0.85: warning += "\n🟠 حل طوارئ"
    e_share = sum(formula.get(ing, 0) for i, ing in enumerate(ingredient_names)
                  if i in energy_idx)
    p_share = sum(formula.get(ing, 0) for i, ing in enumerate(ingredient_names)
                  if i in protein_idx)
    balance_note = None
    if p_share > e_share:
        balance_note = (f"⚠️ البروتين ({p_share:.1f}%) أعلى من "
                        f"الطاقة ({e_share:.1f}%)")
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
            line=dict(color='#1b5e20', width=3),
            marker=dict(size=5, color='#2e7d32'), name='صافي العائد'))
        fig.add_hline(y=0, line_dash="dash", line_color="#c62828",
            annotation_text="التعادل")
        fig.update_layout(title="منحنى الربحية",
            xaxis_title="سعر المنتج", yaxis_title="صافي العائد",
            height=420, paper_bgcolor='white')
        return fig
    except Exception: return None


# ═══════════════════════════════════════════════════════════════════════
# شريط القياس
# ═══════════════════════════════════════════════════════════════════════

WEIGHT_TAPE_CONFIG = {
    "أبقار": {"hg_min":100.0,"hg_max":260.0,"hg_default":180.0,
        "bl_min":100.0,"bl_max":220.0,"bl_default":150.0,
        "hg_label":"محيط الصدر (سم)","bl_label":"طول الجسم (سم)",
        "hg_tip":"خلف الأرجل الأمامية مباشرة",
        "bl_tip":"من الكتف إلى عظم الحوض",
        "source":"Schaeffer (1978)","accuracy":"±5%",
        "formula_display":"W = (محيط² × طول) ÷ 10840",
        "calc":lambda hg,bl: (hg**2*bl)/10840.0},
    "أغنام": {"hg_min":40.0,"hg_max":120.0,"hg_default":75.0,
        "bl_min":40.0,"bl_max":100.0,"bl_default":65.0,
        "hg_label":"محيط الصدر (سم)","bl_label":"طول الجسم (سم)",
        "hg_tip":"خلف الأرجل الأمامية","bl_tip":"من الكتف إلى الحوض",
        "source":"Schaeffer (1978)","accuracy":"±7%",
        "formula_display":"W = (محيط² × طول) ÷ 10840",
        "calc":lambda hg,bl: (hg**2*bl)/10840.0},
    "ماعز": {"hg_min":35.0,"hg_max":110.0,"hg_default":70.0,
        "bl_min":35.0,"bl_max":95.0,"bl_default":62.0,
        "hg_label":"محيط الصدر (سم)","bl_label":"طول الجسم (سم)",
        "hg_tip":"خلف الأرجل الأمامية","bl_tip":"من الكتف إلى الحوض",
        "source":"Schaeffer (1978)","accuracy":"±7%",
        "formula_display":"W = (محيط² × طول) ÷ 10840",
        "calc":lambda hg,bl: (hg**2*bl)/10840.0},
    "إبل": {"hg_min":130.0,"hg_max":280.0,"hg_default":210.0,
        "bl_min":100.0,"bl_max":220.0,"bl_default":155.0,
        "hg_label":"محيط الصدر (سم)","bl_label":"طول الجسم (سم)",
        "hg_tip":"خلف السنام","bl_tip":"من الصدر إلى الذيل",
        "source":"FAO Camel (2010)","accuracy":"±10%",
        "formula_display":"W = (محيط² × طول) ÷ 11880",
        "calc":lambda hg,bl: (hg**2*bl)/11880.0},
    "خيول": {"hg_min":120.0,"hg_max":240.0,"hg_default":175.0,
        "bl_min":100.0,"bl_max":210.0,"bl_default":155.0,
        "hg_label":"محيط الصدر (سم)","bl_label":"طول الجسم (سم)",
        "hg_tip":"خلف الكتف","bl_tip":"من الكتف إلى المؤخرة",
        "source":"Carroll & Huntington (1988)","accuracy":"±5%",
        "formula_display":"W = (محيط² × طول) ÷ 11877",
        "calc":lambda hg,bl: (hg**2*bl)/11877.0},
}

def draw_tape_guide(animal_type):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        fig, ax = plt.subplots(figsize=(10, 5.5))
        ax.set_xlim(0, 10); ax.set_ylim(0, 5.5)
        ax.set_aspect('equal'); ax.axis('off')
        body_c = '#d7ccc8'; edge_c = '#5d4037'
        if animal_type in ("أبقار", "خيول"):
            ax.add_patch(Ellipse((5.2, 2.4), 5.0, 1.9, facecolor=body_c,
                edgecolor=edge_c, lw=2.5))
            ax.add_patch(Ellipse((2.0, 3.0), 1.2, 0.9, facecolor=body_c,
                edgecolor=edge_c, lw=2.5))
            for x in [3.3, 4.2, 6.2, 7.1]:
                ax.plot([x, x], [1.5, 0.4], color=edge_c, lw=7,
                    solid_capstyle='round')
            girth_x = 3.4; girth_y_top, girth_y_bot = 3.5, 1.3
            length_x_start, length_x_end = 2.9, 7.6; length_y = 4.6
        elif animal_type == "إبل":
            ax.add_patch(Ellipse((5.2, 2.4), 5.0, 1.9, facecolor='#bcaaa4',
                edgecolor=edge_c, lw=2.5))
            ax.add_patch(Ellipse((5.2, 3.7), 1.4, 0.9, facecolor='#bcaaa4',
                edgecolor=edge_c, lw=2.5))
            for x in [3.3, 4.2, 6.2, 7.1]:
                ax.plot([x, x], [1.5, 0.4], color=edge_c, lw=7,
                    solid_capstyle='round')
            girth_x = 3.4; girth_y_top, girth_y_bot = 3.4, 1.3
            length_x_start, length_x_end = 2.8, 7.6; length_y = 4.8
        else:
            ax.add_patch(Ellipse((5.2, 2.4), 3.6, 1.5, facecolor='#efebe9',
                edgecolor=edge_c, lw=2.5))
            ax.add_patch(Ellipse((2.5, 2.9), 0.9, 0.7, facecolor='#efebe9',
                edgecolor=edge_c, lw=2.5))
            for x in [3.8, 4.7, 5.7, 6.6]:
                ax.plot([x, x], [1.7, 0.5], color=edge_c, lw=6,
                    solid_capstyle='round')
            girth_x = 3.9; girth_y_top, girth_y_bot = 3.3, 1.5
            length_x_start, length_x_end = 3.3, 7.0; length_y = 4.4
        ax.annotate('', xy=(girth_x, girth_y_bot), xytext=(girth_x, girth_y_top),
            arrowprops=dict(arrowstyle='<->', color='#c62828', lw=3.5,
                mutation_scale=18))
        ax.text(girth_x+0.15, girth_y_top+0.1, '① محيط الصدر',
            color='#c62828', fontweight='bold', fontsize=11,
            bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                edgecolor='#c62828'))
        ax.annotate('', xy=(length_x_start, length_y),
            xytext=(length_x_end, length_y),
            arrowprops=dict(arrowstyle='<->', color='#1565c0', lw=3.5,
                mutation_scale=18))
        ax.text((length_x_start+length_x_end)/2, length_y+0.15,
            '② طول الجسم', color='#1565c0', ha='center',
            fontweight='bold', fontsize=11,
            bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                edgecolor='#1565c0'))
        cfg = WEIGHT_TAPE_CONFIG.get(animal_type, {})
        ax.set_title(f"📍 شريط القياس — {animal_type} | {cfg.get('formula_display','')}",
            fontsize=12, fontweight='bold', color='#1b5e20', pad=18)
        ax.text(0.5, 0.03, '🔴 ① محيط الصدر  |  🔵 ② طول الجسم',
            transform=ax.transAxes, ha='center', fontsize=10, color='#333',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff8e1',
                edgecolor='#d4af37'))
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=130, bbox_inches='tight',
            facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def weight_tape_widget(animal_type, key_prefix, default_weight=None):
    cfg = WEIGHT_TAPE_CONFIG.get(animal_type)
    if cfg is None:
        st.caption("💡 يُقاس بالعمر/المعيار")
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
            st.caption(f"💡 {cfg['hg_tip']}")
        with c2:
            bl = st.slider(f"② {cfg['bl_label']}", cfg['bl_min'],
                cfg['bl_max'], cfg['bl_default'], 0.5, key=f"{key_prefix}_bl")
            st.caption(f"💡 {cfg['bl_tip']}")
        weight = float(cfg["calc"](hg, bl))
        st.success(f"⚖️ الوزن التقديري = **{weight:.1f} كجم**  \n"
                   f"📖 {cfg['source']} — دقة {cfg['accuracy']}")
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
APP_VERSION = "11.10"
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
# الخطوط العربية
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
# مكتبة الأعلاف
# ═══════════════════════════════════════════════════════════════════════

def _feed(cp, dc, se, ndf, adf, ee, ash, ca, p, lys, met, price, desc, src):
    return {"CP":cp,"DC":dc,"SE":se,"NDF":ndf,"ADF":adf,"EE":ee,"ASH":ash,
            "Ca":ca,"P":p,"Lys":lys,"Met":met,"price":price,
            "desc":desc,"src":src}

BIG_FEEDS_LIBRARY = {
"🌾 الحبوب ومصادر الطاقة": {
"ذرة صفراء": _feed(8.5,.85,80,9.5,3.2,3.8,1.3,.02,.27,.24,.17,230,"الطاقة الرئيسية","NRC 2012"),
"ذرة بيضاء": _feed(8.8,.83,78,10.2,3.5,3.5,1.4,.02,.26,.25,.18,225,"بديل","NRC 2012"),
"ذرة شامية": _feed(8.3,.86,82,9,3,4,1.2,.02,.28,.23,.16,240,"طاقة أعلى","NRC 2012"),
"ذرة رفيعة (سورجم)": _feed(10,.78,70,12.5,5.5,3,1.8,.03,.3,.22,.17,195,"بديل","NRC 2012"),
"شعير مطحون": _feed(11.5,.8,71,18.5,7.5,2.2,2.5,.05,.35,.42,.2,210,"للمجترات","NRC 2012"),
"شعير كامل": _feed(10.8,.75,68,22,9,2,2.8,.05,.33,.4,.18,200,"يحتاج جرش","NRC 2012"),
"قمح محلي": _feed(12,.85,75,11.5,3.8,2,1.6,.04,.32,.35,.2,240,"طاقة","NRC 2012"),
"قمح مستورد": _feed(11.5,.87,78,11,3.5,1.9,1.5,.04,.33,.34,.19,245,"طاقة أعلى","NRC 2012"),
"جريش أرز": _feed(7.8,.82,82,5.5,2.5,8.5,4.2,.06,.3,.28,.18,240,"طاقة عالية","NRC 2012"),
"دخن محلي": _feed(11,.75,68,15.5,6.5,4,2.2,.05,.31,.28,.2,220,"بديل","NRC 2012"),
"شوفان علفي": _feed(11,.76,62,27.5,13.5,5,3,.08,.35,.4,.18,260,"للخيول","NRC 2007"),
"كسرة خبز": _feed(10.5,.82,75,8,3.5,5.5,3.5,.1,.2,.28,.17,160,"اقتصادي","INRA 2018"),
"مكرونة مكسرة": _feed(11,.88,80,3.5,1.5,1.5,1,.03,.2,.28,.15,190,"طاقة","INRA 2018"),
"تمر مجفف (دقل)": _feed(5.5,.85,68,15,8.5,1,3.5,.1,.1,.1,.05,180,"اقتصادي","FAO 2010"),
"تفل بنجر السكر": _feed(8.5,.65,55,45,28,1,8.5,.7,.1,.3,.15,190,"للمجترات","INRA 2018"),
"تفل زيتون": _feed(8,.55,35,50,35,12,7,.5,.15,.2,.1,130,"زيوت","INRA 2018"),
},
"🌱 الأكساب ومصادر البروتين": {
"كسب فول صويا 44%": _feed(44,.9,74,13.5,8,1.8,6,.35,.65,2.7,.6,440,"الرئيسي","NRC 2012"),
"كسب فول صويا 48%": _feed(48,.91,76,12,7,1.5,6.2,.35,.65,3,.68,480,"مرتفع","NRC 2012"),
"أمباز الفول السوداني": _feed(46,.88,73,15.5,8.5,1.5,5.5,.2,.65,1.6,.45,460,"ممتاز","NRC 2012"),
"كسب عباد الشمس 36%": _feed(36,.76,42,38.5,25.5,2.5,6.5,.4,1,1.2,.7,310,"أرخص","NRC 2012"),
"كسب عباد الشمس 32%": _feed(32,.72,38,42,28,2,7,.42,.95,1.1,.65,290,"اقتصادي","NRC 2012"),
"كسب بذور القطن": _feed(41,.78,55,24.5,15.5,1.2,6.5,.2,1.1,1.8,.6,290,"جوسيبول","NRC 2012"),
"كسب بذور الكتان": _feed(32,.82,65,18.5,10.5,2.8,5.8,.35,.85,1.2,.55,340,"أوميغا 3","NRC 2007"),
"كسب السمسم": _feed(42,.84,70,14.5,9.5,8.5,12.5,2,1.2,1.3,1,520,"غني Ca","NRC 2007"),
"كسب جلوتين 60%": _feed(60,.92,85,8.5,5.5,2.5,3.5,.15,.5,1.1,1.8,520,"Met عالٍ","NRC 2012"),
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
"مخلفات النخيل": _feed(6.5,.7,60,25,15,5,3.5,.15,.15,.25,.1,100,"للإبل","FAO 2010"),
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
"زيت ذرة": _feed(0,0,220,0,0,100,0,0,0,0,0,1500,"أوميغا 6","NRC 2012"),
"زيت فول الصويا": _feed(0,0,215,0,0,100,0,0,0,0,0,1350,"متوازن","Ross 308"),
"زيت عباد الشمس": _feed(0,0,210,0,0,100,0,0,0,0,0,1300,"أوميغا 6","NRC 2007"),
"زيت الكتان": _feed(0,0,205,0,0,100,0,0,0,0,0,1700,"أوميغا 3","NRC 2007"),
"زيت جوز الهند": _feed(0,0,230,0,0,100,0,0,0,0,0,1900,"MCT","NRC 2012"),
"زيت النخيل": _feed(0,0,215,0,0,100,0,0,0,0,0,1100,"مقاوم","NRC 2012"),
"زيت الكانولا": _feed(0,0,200,0,0,100,0,0,0,0,0,1450,"متوازن","NRC 2012"),
"شحم حيواني (Tallow)": _feed(0,0,230,0,0,100,0,0,0,0,0,900,"طاقة","NRC 2012"),
"زيت السمك (Fish Oil)": _feed(0,0,235,0,0,100,0,0,0,0,0,3800,"EPA/DHA","NRC Fish"),
},
"🧪 الأحماض الأمينية": {
"ليسين نقي": _feed(94,1,0,0,0,0,.5,0,0,94,0,4200,"أساسي","NRC 2012"),
"ميثيونين نقي": _feed(58,1,0,0,0,0,.3,0,0,0,58,5800,"للدواجن","NRC 2012"),
"ثريونين نقي": _feed(72,1,0,0,0,0,.2,0,0,0,0,4800,"ثالث","NRC 2012"),
"تريبتوفان نقي": _feed(85,1,0,0,0,0,.1,0,0,0,0,9500,"للدواجن","NRC 2012"),
},
"🔬 الإنزيمات والبريمكسات": {
"بريمكس تسمين دواجن": _feed(0,0,0,0,0,0,100,18,8,0,0,4800,"فيتامينات","NRC 1994"),
"بريمكس بياض": _feed(0,0,0,0,0,0,100,22,7,0,0,5000,"للبياض","NRC 1994"),
"بريمكس أبقار": _feed(0,0,0,0,0,0,100,20,10,0,0,5200,"للأبقار","NRC 2001"),
"بريمكس مجترات": _feed(0,0,0,0,0,0,100,18,9,0,0,4500,"للمجترات","NRC 2007"),
"بريمكس خيول": _feed(0,0,0,0,0,0,100,15,8,0,0,5500,"للخيول","NRC 2007"),
"بريمكس إبل": _feed(0,0,0,0,0,0,100,20,10,0,0,5300,"للإبل","FAO 2010"),
"بريمكس أسماك": _feed(0,0,0,0,0,0,100,15,7,0,0,5800,"للأسماك","NRC Fish"),
"إنزيم فايتيز": _feed(0,0,0,0,0,0,5,0,0,0,0,4200,"تحرير P","NRC 2012"),
"خمائر حية": _feed(45,.75,30,8,4,1,8,.15,1.2,3,.7,8500,"للمجترات","NRC 2001"),
},
"🪨 الأملاح والمعادن": {
"الحجر الجيري": _feed(0,0,0,0,0,0,99.5,38,0,0,0,40,"مصدر Ca","NRC 2012"),
"فوسفات ثنائي الكالسيوم": _feed(0,0,0,0,0,0,98.5,23,18,0,0,280,"Ca+P","NRC 2012"),
"فوسفات أحادي الكالسيوم": _feed(0,0,0,0,0,0,99,17,22,0,0,320,"P","NRC 2012"),
"ملح الطعام": _feed(0,0,0,0,0,0,99.9,0,0,0,0,30,"NaCl","NRC 2012"),
"بيكربونات الصوديوم": _feed(0,0,0,0,0,0,99,0,0,0,0,340,"مضاد حموضة","NRC 2001"),
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


# ═══════════════════════════════════════════════════════════════════════
# معايير الزيوت
# ═══════════════════════════════════════════════════════════════════════

MAX_OIL_PERCENTAGE = {
    "دواجن_بادي": {"max":8.0,"optimal":5.0,"source":"Ross 308"},
    "دواجن_نامي": {"max":7.0,"optimal":4.5,"source":"Ross 308"},
    "دواجن_ناهي": {"max":7.0,"optimal":4.0,"source":"Ross 308"},
    "دواجن_بياض": {"max":5.0,"optimal":2.5,"source":"NRC 1994"},
    "أبقار_حليب_عالي": {"max":6.0,"optimal":4.0,"source":"NRC 2001"},
    "أبقار_حليب_متوسط": {"max":5.0,"optimal":3.5,"source":"NRC 2001"},
    "أبقار_حليب_منخفض": {"max":5.0,"optimal":3.0,"source":"NRC 2001"},
    "أبقار_تسمين_مكثف": {"max":6.0,"optimal":4.5,"source":"NRC 2001"},
    "أبقار_تسمين_عادي": {"max":5.0,"optimal":3.5,"source":"NRC 2001"},
    "أغنام_تسمين_مكثف": {"max":5.0,"optimal":3.5,"source":"NRC 2007"},
    "أغنام_تسمين_عادي": {"max":4.5,"optimal":3.0,"source":"NRC 2007"},
    "ماعز_حلابة_عالي": {"max":5.0,"optimal":3.5,"source":"NRC 2007"},
    "إبل_حليب": {"max":5.0,"optimal":3.5,"source":"FAO 2010"},
    "خيول_رياضة_مكثف": {"max":10.0,"optimal":7.0,"source":"NRC Horses"},
    "أسماك_بادئ": {"max":15.0,"optimal":10.0,"source":"NRC Fish"},
    "أرانب_تسمين": {"max":4.0,"optimal":2.5,"source":"NRC 2007"},
}

def get_oil_standard(k):
    return MAX_OIL_PERCENTAGE.get(k, {"max":5.0,"optimal":3.0,"source":"عام"})


# ═══════════════════════════════════════════════════════════════════════
# الحدود العلمية
# ═══════════════════════════════════════════════════════════════════════

INGREDIENT_LIMITS_BY_ANIMAL = {
"دواجن": {"يوريا علفية":(0,0),"سمن حيواني (Lard)":(0,0),
    "نخالة قمح (ردة)":(0,10),"نخالة ذرة":(0,5),"تبن قمح":(0,2),
    "قش أرز":(0,2),"كسب بذور القطن":(0,5),"كسب السمسم":(0,8),
    "كسب الكانولا":(0,8),"ملح الطعام":(.2,.4),"الحجر الجيري":(.8,2),
    "فوسفات ثنائي الكالسيوم":(.5,2.5),"مضاد سموم فطرية":(.05,.15),
    "بريمكس تسمين دواجن":(.2,.35),"بريمكس بياض":(.2,.35),
    "ليسين نقي":(0,.5),"ميثيونين نقي":(0,.4)},
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
"أسماك": {"يوريا علفية":(0,0),"سمن حيواني (Lard)":(0,0),
    "نخالة قمح (ردة)":(0,10),"ملح الطعام":(0,.3),
    "بريمكس أسماك":(.15,.3),"الحجر الجيري":(0,2),
    "فوسفات ثنائي الكالسيوم":(0,2)},
"أرانب": {"يوريا علفية":(0,.5),"نخالة قمح (ردة)":(0,20),
    "ملح الطعام":(.3,.5),"بريمكس مجترات":(.15,.3),
    "الحجر الجيري":(0,2.5),"فوسفات ثنائي الكالسيوم":(0,2)},
}

def get_animal_limits(animal):
    return INGREDIENT_LIMITS_BY_ANIMAL.get(animal, {})


# ═══════════════════════════════════════════════════════════════════════
# الاحتياجات الغذائية — NRC مُصحَّحة
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
            round(.55 + milk_yield*.003, 3),
            round(.33 + milk_yield*.0015, 3),
            "أبقار حلابة عالية", f"حليب {milk_yield} كجم")
    if t == "حليب_متوسط":
        dp = min(8.5 + milk_yield * 0.17, 14.0)
        return AnimalRequirement(round(dp,2), round(dp/.72,2),
            round(55 + milk_yield*.30, 1), 33, 21, 4.5, 8,
            round(.5 + milk_yield*.0025, 3),
            round(.3 + milk_yield*.0012, 3),
            "أبقار حلابة متوسطة", f"حليب {milk_yield} كجم")
    if t == "حليب_منخفض":
        dp = min(8.0 + milk_yield * 0.16, 12.5)
        return AnimalRequirement(round(dp,2), round(dp/.75,2),
            round(50 + milk_yield*.25, 1), 38, 24, 4, 8.5,
            round(.45 + milk_yield*.002, 3),
            round(.28 + milk_yield*.001, 3),
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
            f"نعاج مرضعات ({litter_size} مولود)", "")
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
            round(.6 + milk_yield*.008, 3),
            round(.35 + milk_yield*.004, 3),
            f"عنزات حلابة ({milk_yield} لتر)", "")
    if t == "حلابة_متوسط":
        dp = min(8.5 + milk_yield * 0.30, 12.0)
        return AnimalRequirement(round(dp,2), round(dp/.72,2),
            round(55 + milk_yield*.40, 1), 32, 20, 4, 8.5,
            round(.55 + milk_yield*.006, 3),
            round(.32 + milk_yield*.003, 3),
            f"عنزات حلابة ({milk_yield} لتر)", "")
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
            round(.7 + milk_yield*.006, 3),
            round(.4 + milk_yield*.003, 3),
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
                "بادي لاحم", "")
        if age_weeks <= 3:
            return AnimalRequirement(18.5, 21, 74, 9, 5, 5, 6, .9, .45,
                "نامي لاحم", "")
        if age_weeks <= 5:
            return AnimalRequirement(17, 19.5, 75, 10, 5.5, 4.5, 6, .87, .43,
                "ناهي لاحم", "")
        return AnimalRequirement(16.5, 19, 75, 10, 5.5, 4.5, 6, .85, .42,
            "ناهي لاحم+", "")
    if age_weeks <= 6:
        return AnimalRequirement(17, 20, 72, 10, 5.5, 4, 7, 1, .5,
            "بادي بياض", "")
    if age_weeks <= 18:
        return AnimalRequirement(14.5, 17, 70, 12, 6.5, 4, 9, 1.5, .45,
            "نامي بياض", "")
    return AnimalRequirement(15.5, 18, 72, 11, 6, 4.2, 11.5, 3.8, .45,
        "بياض إنتاجي", "")

def get_quail_requirements(strain, age_weeks=1):
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
            "أرانب تسمين", "ADG 40")
    if t == "حليب":
        return AnimalRequirement(18, 20, 68, 25, 15, 4, 8.5, .85, .45,
            "أرانب حلابة", "أمهات")
    return AnimalRequirement(12, 14, 60, 30, 20, 2.5, 8.5, .6, .3,
        "أرانب صيانة", "")

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
            return {"label":"🎯 مطابق","color":"#0d5302",
                "bg":"#c8e6c9","score":100}
        return {"label":"⚠️ صفر","color":"#ef6c00",
            "bg":"#fff3e0","score":40}
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
    if "بياض" in str(production_type): d.add("الحجر الجيري")
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


# ═══════════════════════════════════════════════════════════════════════
# LP محسّن — 10 مستويات
# ═══════════════════════════════════════════════════════════════════════

def auto_formulate_smart(available_ingredients, prices, custom_standard,
                          standard_key="", basis="DP", min_quality=70.0,
                          animal_type="", production_type=""):
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "SCIPY غير متوفرة"}
    available_ingredients = [_normalize_ingredient_name(i)
                              for i in available_ingredients]
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
    rows["DP"] = [ing_data[i].get("CP",0) * ing_data[i].get("DC",0)
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
        if is_ruminant:
            A_ub_base.append([-x for x in rows["NDF"]])
            b_ub_base.append(-target_ndf * 0.85 * 100.0)
            A_ub_base.append(rows["NDF"])
            b_ub_base.append(target_ndf * 1.20 * 100.0)
        else:
            A_ub_base.append(rows["NDF"])
            b_ub_base.append(target_ndf * (1.10 if is_poultry else 1.15) * 100.0)
    if target_adf > 0:
        A_ub_base.append(rows["ADF"])
        mult = 1.30 if is_ruminant else (1.10 if is_poultry else 1.20)
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
    strategies = [
        ("دقيق 100%", 1.00), ("مرن 97%", 0.97), ("مرن 95%", 0.95),
        ("مرن 92%", 0.92), ("مرن 90%", 0.90), ("مرن 85%", 0.85),
        ("مرن 80%", 0.80), ("بدون Ca/P", 1.00),
        ("بدون Ca/P + مرن 85%", 0.85), ("طوارئ قصوى", 0.75)]
    best, best_q = None, 0.0
    attempts = []
    for label, mult in strategies:
        try:
            A_eq = list(A_eq_base)
            b_eq = [100.0, target_protein * 100.0 * mult]
            A_ub = list(A_ub_base); b_ub = list(b_ub_base)
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                bounds=bounds, method='highs',
                options={'presolve': True, 'time_limit': 15})
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
                        "targets": custom_standard, "basis": basis,
                        "oil_std": oil_std,
                        "total_oil": compute_total_oil_percentage(formula)}
                attempts.append(f"✅ {label}: جودة {q:.1f}%")
                if q >= 92: break
            else:
                attempts.append(f"❌ {label}: تعذر")
        except Exception as e:
            attempts.append(f"⚠️ {label}: {e}")
            continue
    if best:
        if not best["meets_standard"]:
            best["warning"] = (f"⚠️ جودة {best_q:.1f}% < {min_quality}%")
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
        "strategy": "🆘 طوارئ",
        "meets_standard": q >= min_quality,
        "targets": custom_standard, "basis": basis,
        "oil_std": oil_std,
        "total_oil": compute_total_oil_percentage(fallback_formula),
        "warning": f"⚠️ حل طوارئ — جودة {q:.1f}%",
        "attempts_log": attempts}


# ═══════════════════════════════════════════════════════════════════════
# 🧪 v11.10 — مختبر تحليل التركيبات الجاهزة
# ═══════════════════════════════════════════════════════════════════════

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
    labels = {"CP": "بروتين خام CP", "DP": "بروتين مهضوم DP",
              "SE": "طاقة SE", "NDF": "NDF", "ADF": "ADF",
              "EE": "دهن EE", "ASH": "رماد ASH",
              "Ca": "كالسيوم Ca", "P": "فسفور P",
              "Lys": "ليسين Lys", "Met": "ميثيونين Met"}
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
               lookup.get(ing, {}).get("price", 300)
               for ing in normalized)
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


# ═══════════════════════════════════════════════════════════════════════
# بدائل الحليب
# ═══════════════════════════════════════════════════════════════════════

MILK_REPLACER_STANDARDS = {
    "عجول (Calves)": {"CP":24,"Fat":20,"Lactose":45,"Ca":.85,"P":.7,
        "Lys":2.2,"Met":.65,"notes":"NRC 2001",
        "source":"NRC Dairy Cattle","Ca_P_optimal":(1.2,1.5)},
    "حملان (Lambs)": {"CP":24,"Fat":24,"Lactose":40,"Ca":.9,"P":.7,
        "Lys":2.4,"Met":.7,"notes":"≥24% دهن",
        "source":"NRC Small Ruminants","Ca_P_optimal":(1.2,1.6)},
    "جديان (Goat Kids)": {"CP":24,"Fat":24,"Lactose":42,"Ca":.9,"P":.7,
        "Lys":2.3,"Met":.7,"notes":"توازن خاص",
        "source":"NRC Small Ruminants","Ca_P_optimal":(1.2,1.6)},
    "إبل (Camels)": {"CP":26,"Fat":28,"Lactose":38,"Ca":.95,"P":.75,
        "Lys":2.5,"Met":.8,"notes":"أعلى بروتين",
        "source":"FAO Camel Nutrition","Ca_P_optimal":(1.2,1.5)},
    "أمهار (Foals)": {"CP":22,"Fat":18,"Lactose":48,"Ca":1.0,"P":.8,
        "Lys":2.1,"Met":.6,"notes":"توازن خاص",
        "source":"NRC Horses","Ca_P_optimal":(1.2,1.4)},
}

MILK_REPLACER_INGREDIENTS = {
    "حليب مجفف منزوع الدسم": {"CP":34,"Fat":1,"Lactose":52,"Ca":1.3,
        "P":1,"Lys":2.7,"Met":.9,"price":3200,"max":60,"type":"بروتين"},
    "حليب مجفف كامل الدسم": {"CP":26,"Fat":28,"Lactose":38,"Ca":.95,
        "P":.75,"Lys":2.1,"Met":.65,"price":3800,"max":70,"type":"بروتين+دهن"},
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
    if not SCIPY_AVAILABLE:
        return {"success": False, "message": "SCIPY غير متوفرة"}
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
    base_bounds = [(0, MILK_REPLACER_INGREDIENTS[i].get("max", 100))
                   for i in valid]
    strategies = []
    s1_ub = [(lac,std["Lactose"]*1.15*100),
        ([-x for x in lac],-std["Lactose"]*0.85*100),
        ([-x for x in lys],-std["Lys"]*0.70*100),
        ([-x for x in met],-std["Met"]*0.70*100),
        ([-x for x in ca],-std["Ca"]*0.85*100),
        ([-x for x in p],-std["P"]*0.85*100)]
    strategies.append(("S1",[[1]*n,cp,fat],
        [100,std["CP"]*100,std["Fat"]*100],
        [u for u,_ in s1_ub],[b for _,b in s1_ub]))
    s2_ub = [(lac,std["Lactose"]*1.30*100),
        ([-x for x in lac],-std["Lactose"]*0.70*100),
        ([-x for x in lys],-std["Lys"]*0.70*100),
        ([-x for x in met],-std["Met"]*0.70*100),
        ([-x for x in ca],-std["Ca"]*0.85*100),
        ([-x for x in p],-std["P"]*0.85*100)]
    strategies.append(("S2",[[1]*n,cp,fat],
        [100,std["CP"]*100,std["Fat"]*100],
        [u for u,_ in s2_ub],[b for _,b in s2_ub]))
    s3_ub = s1_ub[:2] + s1_ub[4:]
    strategies.append(("S3",[[1]*n,cp,fat],
        [100,std["CP"]*100,std["Fat"]*100],
        [u for u,_ in s3_ub],[b for _,b in s3_ub]))
    s4_ub = s1_ub[:2]
    strategies.append(("S4",[[1]*n,cp,fat],
        [100,std["CP"]*100,std["Fat"]*100],
        [u for u,_ in s4_ub],[b for _,b in s4_ub]))
    s5_ub = [(cp,std["CP"]*1.05*100),
        ([-x for x in cp],-std["CP"]*0.95*100),
        (fat,std["Fat"]*1.05*100),
        ([-x for x in fat],-std["Fat"]*0.95*100)]
    strategies.append(("S5",[[1]*n],[100],
        [u for u,_ in s5_ub],[b for _,b in s5_ub]))
    s6_ub = [(cp,std["CP"]*1.15*100),
        ([-x for x in cp],-std["CP"]*0.85*100),
        (fat,std["Fat"]*1.30*100),
        ([-x for x in fat],-std["Fat"]*0.50*100)]
    strategies.append(("S6",[[1]*n],[100],
        [u for u,_ in s6_ub],[b for _,b in s6_ub]))
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
        warning = (f"⚠️ تم استخدام {best['used_count']}/{n} مادة "
                   f"({best['used_pct']:.0f}% < {min_util*100:.0f}%)")
    return {"success": True, "formula": best["formula"],
        "cost_per_100kg": best["cost"], "cost_per_kg": best["cost_per_kg"],
        "standard": std, "actual": best["actual"], "animal": animal,
        "volume": volume, "used_count": best["used_count"],
        "used_pct": best["used_pct"],
        "quality_score": best["quality_score"],
        "ca_p_ratio": best["ca_p_ratio"],
        "strategy": best["strategy"], "warning": warning,
        "targets": {k: std.get(k, 0) for k in
                    ["CP","Fat","Lactose","Ca","P","Lys","Met"]}}

# ═══════════════════════════════════════════════════════════════════════
# نهاية PART 1 — تابع
# ═══════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════
# [تكملة PART 1] — OCR + الرسوم + PDF + Excel + حظائر + جلسة + UI + مختبر
# ═══════════════════════════════════════════════════════════════════════

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

def _parse_ingredients_from_text(full_text):
    fixes = {'٥':'5','٦':'6','٧':'7','٨':'8','٩':'9','٠':'0','١':'1',
             '٢':'2','٣':'3','٤':'4','٪':'%'}
    text = full_text
    for old, new in fixes.items(): text = text.replace(old, new)
    patterns = [
        r'([\u0600-\u06FFa-zA-Z\s\(\)\-]{3,40}?)[\s:\-=:\.]+\s*(\d{1,3}\.?\d{0,2})\s*%',
        r'(\d{1,3}\.?\d{0,2})\s*%[\s:\-=:\.]+\s*([\u0600-\u06FFa-zA-Z\s\(\)\-]{3,40})']
    ingredients = {}
    for line in text.split('\n'):
        line = line.strip()
        if len(line) < 4: continue
        for pat in patterns:
            for m in re.finditer(pat, line, re.MULTILINE):
                try:
                    g = m.groups()
                    if len(g) < 2: continue
                    try: val, name = float(g[1]), g[0].strip()
                    except ValueError:
                        try: val, name = float(g[0]), g[1].strip()
                        except ValueError: continue
                    if 0.1 <= val <= 100 and len(name) > 2:
                        matched = match_ingredient_name(name)
                        if matched and matched not in ingredients:
                            ingredients[matched] = round(val, 2)
                except Exception: continue
    return ingredients

def match_ingredient_name(text):
    if not text: return None
    tl = text.strip().lower()
    for cat in BIG_FEEDS_LIBRARY.values():
        for name in cat.keys():
            if name.lower() in tl or tl in name.lower(): return name
    kw = {"ذرة":"ذرة صفراء","ذره":"ذرة صفراء","صويا":"كسب فول صويا 44%",
          "شعير":"شعير مطحون","قمح":"قمح محلي","نخالة":"نخالة قمح (ردة)",
          "ملح":"ملح الطعام","حجر":"الحجر الجيري",
          "فوسفات":"فوسفات ثنائي الكالسيوم","يوريا":"يوريا علفية"}
    for k, m in kw.items():
        if k in tl: return m
    return None

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
            if keep and new_pct > 0: corrected[new_name] = new_pct
    return corrected


# ═══════════════════════════════════════════════════════════════════════
# الرسوم البيانية
# ═══════════════════════════════════════════════════════════════════════

def create_colorful_bar_chart(standard, actual, keys=None):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        if keys is None: keys = ["CP","DP","SE","NDF","ADF","EE","ASH"]
        nuts = [n for n in keys if n in standard and standard[n] > 0]
        if not nuts: return None
        fig, ax = plt.subplots(figsize=(9, 4.5))
        x = np.arange(len(nuts)); width = 0.35
        ax.bar(x-width/2, [standard[n] for n in nuts], width, label='المعيار',
            color='#1976d2', edgecolor='#0d47a1', linewidth=1.5)
        ax.bar(x+width/2, [actual.get(n,0) for n in nuts], width,
            label='المحسوب', color='#43a047', edgecolor='#1b5e20',
            linewidth=1.5)
        ax.set_xlabel('العنصر', fontweight='bold')
        ax.set_ylabel('القيمة', fontweight='bold')
        ax.set_title('مقارنة العناصر', fontsize=13, fontweight='bold',
            color='#1b5e20')
        ax.set_xticks(x); ax.set_xticklabels(nuts)
        ax.legend(loc='upper right'); ax.grid(axis='y', alpha=0.3)
        ax.set_facecolor('#fafafa')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
            facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_colorful_pie_chart(formula):
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2: return None
    try:
        colors = ['#e53935','#8e24aa','#3949ab','#1e88e5','#00897b',
                  '#43a047','#7cb342','#fdd835','#fb8c00','#6d4c41']
        names = list(formula.keys()); vals = list(formula.values())
        fig, ax = plt.subplots(figsize=(8, 5))
        _, _, autotexts = ax.pie(vals, autopct='%1.1f%%',
            colors=colors[:len(names)], startangle=90, pctdistance=0.75,
            wedgeprops=dict(edgecolor='white', linewidth=2))
        for t in autotexts: t.set_color('white'); t.set_fontweight('bold')
        ax.legend(names, loc='center left', bbox_to_anchor=(1,0,0.5,1),
            fontsize=9)
        ax.set_title('توزيع المكونات', fontsize=13, fontweight='bold',
            color='#1b5e20')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
            facecolor='white')
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
        std_norm += std_norm[:1]; act_norm += act_norm[:1]
        angles += angles[:1]
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, std_norm, 'o-', linewidth=2.5, color='#1976d2',
            label='المعيار')
        ax.fill(angles, std_norm, alpha=0.15, color='#1976d2')
        ax.plot(angles, act_norm, 'o-', linewidth=2.5, color='#43a047',
            label='المحسوب')
        ax.fill(angles, act_norm, alpha=0.25, color='#43a047')
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(nuts)
        ax.set_title('المقارنة %', fontweight='bold', color='#1b5e20', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3,1.1))
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
            facecolor='white')
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
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
            facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_ca_p_ratio_chart(ca, p, target_ca=0, target_p=0):
    if not MATPLOTLIB_AVAILABLE or p <= 0: return None
    try:
        ratio = ca / p
        fig, ax = plt.subplots(figsize=(8, 3))
        zones = [(0,.8,'#b71c1c'),(.8,1.2,'#ef6c00'),(1.2,1.5,'#f9a825'),
                 (1.5,2.0,'#2e7d32'),(2.0,3.0,'#f9a825'),
                 (3.0,5.0,'#ef6c00'),(5.0,8.0,'#b71c1c')]
        for x0, x1, c in zones: ax.axvspan(x0, x1, alpha=0.35, color=c)
        ratio_clipped = min(ratio, 7.9)
        ax.axvline(ratio_clipped, color='#0d47a1', linewidth=4, zorder=10)
        ax.text(ratio_clipped, 0.85, f'{ratio:.2f}', ha='center', fontsize=18,
            fontweight='bold', color='#0d47a1',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                edgecolor='#0d47a1', linewidth=2))
        ax.set_xlim(0, 8); ax.set_ylim(0, 1.2); ax.set_yticks([])
        ax.set_xlabel('نسبة Ca : P', fontweight='bold')
        ax.set_title(f'⚖️ Ca:P — Ca={ca:.2f}% | P={p:.2f}%',
            fontweight='bold', color='#1b5e20')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=130, bbox_inches='tight',
            facecolor='white')
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
        ax.axhline(y=70, color='#c62828', linestyle='--', linewidth=2,
            label='حد 70%')
        ax.set_ylim(0, 105); ax.set_title('تقييم العناصر',
            fontweight='bold', color='#1b5e20')
        ax.legend(loc='lower right'); ax.grid(axis='y', alpha=0.3)
        ax.set_facecolor('#fafafa'); plt.xticks(rotation=30, ha='right')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
            facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_horizontal_bar_chart(formula):
    if not MATPLOTLIB_AVAILABLE or len(formula) < 2: return None
    try:
        sorted_pairs = sorted(formula.items(), key=lambda x: x[1], reverse=True)
        names = [p[0] for p in sorted_pairs]; vals = [p[1] for p in sorted_pairs]
        colors = ['#e53935','#8e24aa','#3949ab','#1e88e5','#00897b',
                  '#43a047','#7cb342','#fdd835','#fb8c00','#6d4c41']
        fig, ax = plt.subplots(figsize=(9, max(4, len(names)*0.4)))
        bars = ax.barh(names, vals, color=colors[:len(names)], edgecolor='#333')
        for bar in bars:
            hh = bar.get_width()
            ax.text(hh+0.5, bar.get_y()+bar.get_height()/2, f'{hh:.1f}%',
                ha='left', va='center', fontsize=9, fontweight='bold')
        ax.set_xlabel('النسبة %', fontweight='bold')
        ax.set_title('توزيع المكونات', fontweight='bold', color='#1b5e20')
        ax.invert_yaxis(); ax.grid(axis='x', alpha=0.3)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
            facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None

def create_oil_comparison_chart(total_oil, oil_std):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        fig, ax = plt.subplots(figsize=(8, 4))
        cats = ['الفعلية', 'المثالي', 'الحد الأقصى']
        vals = [total_oil, oil_std['optimal'], oil_std['max']]
        colors = ['#43a047', '#1976d2', '#c62828']
        if total_oil > oil_std['max']: colors[0] = '#c62828'
        elif total_oil > oil_std['optimal'] * 1.2: colors[0] = '#f9a825'
        bars = ax.bar(cats, vals, color=colors, edgecolor='#333', linewidth=1.5)
        for bar in bars:
            hh = bar.get_height()
            ax.text(bar.get_x()+bar.get_width()/2, hh+0.2, f'{hh:.2f}%',
                ha='center', fontweight='bold')
        ax.set_ylabel('النسبة %', fontweight='bold')
        ax.set_title(f'الزيوت — {oil_std.get("source", "")}',
            fontweight='bold', color='#1b5e20')
        ax.grid(axis='y', alpha=0.3); ax.set_facecolor('#fafafa')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight',
            facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None


# ═══════════════════════════════════════════════════════════════════════
# PDF Generator (مع صفحة المراجع v11.10)
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
            canvas_obj.drawCentredString(w/2, h-38,
                self._ar("تاور نولجي  Tawor Nology"))
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
            canvas_obj.setFillColor(HexColor('#d4af37'))
            canvas_obj.rect(0, 84, w, 3, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor('#ffeb3b'))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.drawCentredString(w/2, 68,
                self._ar(f"🤲 {DUA_SHORT} 🤲"))
            canvas_obj.setFillColor(HexColor('#1b5e20'))
            canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(white); canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(w/2, 27,
                self._ar("تاور نولجي Tawor Nology © 2026"))
            canvas_obj.setFont(self.font_name, 7)
            canvas_obj.drawCentredString(w/2, 12,
                self._ar(f"صفحة {canvas_obj.getPageNumber()} | جميع الحقوق محفوظة"))
            canvas_obj.restoreState()
        except Exception: pass

    def _add_references_page(self, story, animal_type, production_type):
        """✅ v11.10 — صفحة المراجع العلمية"""
        try:
            refs = get_references(animal_type, production_type)
            story.append(PageBreak())
            story.append(Paragraph(self._ar("📚 المراجع العلمية"),
                ParagraphStyle('ref_title', fontName=self.font_name,
                    fontSize=16, alignment=TA_CENTER,
                    textColor=HexColor('#1b5e20'), spaceAfter=15)))
            story.append(Paragraph(
                self._ar(f"📖 المرجع الأساسي: {refs['primary']}"),
                ParagraphStyle('ref_p', fontName=self.font_name,
                    fontSize=11, alignment=TA_RIGHT,
                    textColor=HexColor('#0d47a1'), spaceAfter=8,
                    leading=16)))
            if refs.get("table"):
                story.append(Paragraph(
                    self._ar(f"📑 الجدول: {refs['table']}"),
                    ParagraphStyle('ref_t', fontName=self.font_name,
                        fontSize=10, alignment=TA_RIGHT,
                        textColor=HexColor('#1565c0'), spaceAfter=8,
                        leading=14)))
            if refs.get("secondary"):
                story.append(Spacer(1, 6))
                story.append(Paragraph(
                    self._ar("📚 مراجع داعمة:"),
                    ParagraphStyle('ref_st', fontName=self.font_name,
                        fontSize=11, alignment=TA_RIGHT,
                        textColor=HexColor('#2e7d32'), spaceAfter=6)))
                for sec in refs["secondary"]:
                    story.append(Paragraph(
                        self._ar(f"• {sec}"),
                        ParagraphStyle('ref_s', fontName=self.font_name,
                            fontSize=10, alignment=TA_RIGHT,
                            spaceAfter=4, leading=14)))
            story.append(Spacer(1, 20))
            story.append(HRFlowable(width="100%", thickness=1.5,
                color=HexColor('#d4af37')))
            story.append(Spacer(1, 10))
            story.append(Paragraph(
                self._ar("📖 مراجع عامة معتمدة في المنصة:"),
                ParagraphStyle('ref_gen', fontName=self.font_name,
                    fontSize=11, alignment=TA_RIGHT,
                    textColor=HexColor('#1b5e20'), spaceAfter=8)))
            for i, ref in enumerate(GENERAL_REFERENCES, 1):
                story.append(Paragraph(
                    f"{i}. {ref}",
                    ParagraphStyle('ref_li', fontName='Helvetica',
                        fontSize=9, alignment=TA_LEFT,
                        spaceAfter=4, leading=12, leftIndent=10)))
        except Exception as e:
            story.append(Paragraph(f"خطأ: {e}",
                ParagraphStyle('err', fontName=self.font_name,
                    fontSize=9, alignment=TA_RIGHT,
                    textColor=HexColor('#c62828'))))

    def _comparison_table(self, std, calc):
        labels = {"CP":"بروتين CP","DP":"مهضوم DP","SE":"SE","NDF":"NDF",
                  "ADF":"ADF","EE":"دهن","ASH":"رماد","Ca":"Ca","P":"P"}
        data = [[self._ar(x) for x in
                 ["العنصر","المعيار","المحسوب","الفرق","%","التقييم"]]]
        cmds = [('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),
                ('TEXTCOLOR',(0,0),(-1,0),white),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('FONTNAME',(0,0),(-1,-1),self.font_name),
                ('FONTSIZE',(0,0),(-1,-1),9),
                ('GRID',(0,0),(-1,-1),1,HexColor('#9e9e9e')),
                ('TOPPADDING',(0,0),(-1,-1),7),
                ('BOTTOMPADDING',(0,0),(-1,-1),7)]
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
        story.append(P("تقرير فني رسمي — تركيب علفة", size=20,
            align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
            color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))
        client = [[self._ar("👤 طالب الخدمة:"),
                   self._ar(requester_name or "—")],
            [self._ar("📍 الموقع:"), self._ar(city)],
            [self._ar("🐾 الفصيل:"), self._ar(f"{animal_type} — {breed}")],
            [self._ar("🧬 الأساس:"), self._ar(protein_basis)],
            [self._ar("📅 التاريخ:"), datetime.now().strftime('%Y-%m-%d')]]
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
            ('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),11)]))
        story.append(qt); story.append(Spacer(1, 15))
        story.append(P("📊 مقارنة العناصر", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        story.append(self._comparison_table(std_vals, calc_vals))
        story.append(Spacer(1, 15))
        if include_charts:
            for chart_fn, args in [
                (create_colorful_bar_chart,(std_vals, calc_vals)),
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
            [self._ar("التكلفة/طن"), f"${cost:.2f}"],
            [self._ar(f"التكلفة ({local_sym})"), f"{local_cost:,.2f}"]]
        tc = Table(cost_data, colWidths=[280, 210])
        tc.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('GRID',(0,0),(-1,-1),1,HexColor('#2e7d32')),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),11)]))
        story.append(tc); story.append(Spacer(1, 18))
        if formula:
            story.append(P("🌾 المكونات للطن", size=14, color='#1b5e20'))
            ing_data = [[self._ar("المكون"), self._ar("%"),
                         self._ar("كجم/طن")]]
            for ing, pct in formula.items():
                ing_data.append([self._ar(ing), f"{pct:.2f}%",
                    f"{pct*10:.1f}"])
            ti = Table(ing_data, colWidths=[270, 110, 110])
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
        # ✅ v11.10: صفحة المراجع
        try:
            self._add_references_page(story, animal_type,
                                       standard_key or breed)
        except Exception: pass
        doc.build(story, onFirstPage=self._draw_page,
            onLaterPages=self._draw_page)
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
        story.append(P("تقرير تحليل OCR", size=20, align=TA_CENTER,
            color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
            color=HexColor('#d4af37')))
        data = [[self._ar("المادة"), self._ar("%")]]
        for k, v in ingredients.items():
            data.append([self._ar(k), f"{v:.2f}%"])
        data.append([self._ar("الإجمالي"),
                     f"{sum(ingredients.values()):.2f}%"])
        t = Table(data, colWidths=[300, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),self.font_name),
            ('FONTSIZE',(0,0),(-1,-1),11),
            ('GRID',(0,0),(-1,-1),1,HexColor('#bdbdbd')),
            ('BACKGROUND',(0,-1),(-1,-1),HexColor('#ffe0b2'))]))
        story.append(t)
        doc.build(story, onFirstPage=self._draw_page,
            onLaterPages=self._draw_page)
        buffer.seek(0); return buffer.getvalue()

pdf_gen = PDFGenerator()


def generate_milk_replacer_pdf(result):
    if not REPORTLAB_AVAILABLE: return None
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
            leftMargin=40, topMargin=115, bottomMargin=145)
        story = []
        def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
            return Paragraph(ar(text), ParagraphStyle('s',
                fontName=font_mgr.font_name, fontSize=size, alignment=align,
                textColor=HexColor(color), spaceAfter=6, leading=size*1.6))
        std = result["standard"]; actual = result["actual"]
        quality = result["quality_score"]; formula = result["formula"]
        volume = result.get("volume", 100.0)
        story.append(P("تقرير تركيبة بديل الحليب", size=20,
            align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
            color=HexColor('#d4af37')))
        info = [[ar("الحيوان:"), ar(result["animal"])],
            [ar("المرجع:"), ar(std.get("source", ""))],
            [ar("التاريخ:"), datetime.now().strftime('%Y-%m-%d %H:%M')],
            [ar("المكونات:"), f"{result['used_count']}"],
            [ar("الكمية:"), f"{volume:.0f} كجم"]]
        ct = Table(info, colWidths=[160, 330])
        ct.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(0,-1),HexColor('#e3f2fd')),
            ('BACKGROUND',(1,0),(1,-1),HexColor('#fafafa')),
            ('BOX',(0,0),(-1,-1),1.5,HexColor('#1565c0')),
            ('INNERGRID',(0,0),(-1,-1),0.6,HexColor('#bbdefb')),
            ('ALIGN',(0,0),(-1,-1),'RIGHT'),
            ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
            ('FONTSIZE',(0,0),(-1,-1),10),('PADDING',(0,0),(-1,-1),7)]))
        story.append(ct); story.append(Spacer(1, 12))
        qd = [[ar("الجودة"), ar("الحالة"), ar("Ca:P"), ar("الاستخدام")],
              [f"{quality:.1f}%", ar("✅" if quality >= 70 else "⚠️"),
               f"{result['ca_p_ratio']:.2f}",
               f"{result['used_pct']:.0f}%"]]
        qt = Table(qd, colWidths=[110, 155, 110, 115])
        qt.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#1565c0')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('BACKGROUND',(0,1),(-1,-1),HexColor('#e8f5e9')),
            ('GRID',(0,0),(-1,-1),1,HexColor('#1976d2')),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
            ('FONTSIZE',(0,0),(-1,-1),11),('PADDING',(0,0),(-1,-1),8)]))
        story.append(qt); story.append(Spacer(1, 15))
        story.append(P("🍼 المكونات", size=14, color='#1b5e20'))
        ing_data = [[ar(x) for x in
                     ["المكون","%",f"كجم /{volume:.0f}",
                      "السعر","التكلفة $"]]]
        for ing, pct in formula.items():
            price = MILK_REPLACER_INGREDIENTS[ing]["price"]
            kg = pct * volume / 100; line_cost = kg * price / 1000
            ing_data.append([ar(ing), f"{pct:.2f}%", f"{kg:.2f}",
                f"${price:.0f}", f"${line_cost:.2f}"])
        total_cost = result['cost_per_100kg'] * volume / 100
        ing_data.append([ar("الإجمالي"), "100%", f"{volume:.0f}", "—",
            f"${total_cost:.2f}"])
        it = Table(ing_data, colWidths=[170, 65, 85, 85, 85])
        it.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),
            ('TEXTCOLOR',(0,0),(-1,0),white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
            ('FONTSIZE',(0,0),(-1,-1),9),
            ('GRID',(0,0),(-1,-1),0.8,HexColor('#bdbdbd')),
            ('BACKGROUND',(0,-1),(-1,-1),HexColor('#ffe082'))]))
        story.append(it); story.append(Spacer(1, 20))
        # ✅ v11.10: صفحة المراجع
        try:
            pdf_gen._add_references_page(story, "عجول", "حليب")
        except Exception: pass
        story.append(P(SUPERVISOR, size=16, align=TA_CENTER,
            color='#c62828'))
        story.append(P(SUPERVISOR_TITLE, size=11, align=TA_CENTER,
            color='#1b5e20'))
        doc.build(story, onFirstPage=pdf_gen._draw_page,
            onLaterPages=pdf_gen._draw_page)
        buffer.seek(0); return buffer.getvalue()
    except Exception: return None


# ═══════════════════════════════════════════════════════════════════════
# 🧪 v11.10 — PDF المختبر
# ═══════════════════════════════════════════════════════════════════════

def generate_lab_pdf(result, ctx):
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
                spaceAfter=6, leading=size * 1.6))
        story.append(P("تقرير تحليل تركيبة علفية — مختبر تاور نولجي",
            size=18, align=TA_CENTER, color='#1b5e20'))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5,
            color=HexColor('#d4af37')))
        story.append(Spacer(1, 12))
        info = [
            [ar("الحيوان"), ar(ctx.get("animal", "—"))],
            [ar("نوع الإنتاج"), ar(ctx.get("production", "—"))],
            [ar("المعيار"), ar(result.get("requirement_name", "—"))],
            [ar("الجودة"), ar(f"{result['quality_score']:.1f}%")],
            [ar("Ca:P"), ar(f"{result['ca_p_ratio']:.2f}")],
            [ar("الطاقة"), ar(f"{result['energy_share_pct']:.1f}%")],
            [ar("البروتين"), ar(f"{result['protein_share_pct']:.1f}%")],
            [ar("التكلفة/طن"), ar(f"${result['cost_per_ton']:.2f}")],
            [ar("التاريخ"), ar(datetime.now().strftime("%Y-%m-%d %H:%M"))]]
        t = Table(info, colWidths=[160, 330])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
            ('BOX', (0, 0), (-1, -1), 1.5, HexColor('#2e7d32')),
            ('INNERGRID', (0, 0), (-1, -1), 0.6, HexColor('#c8e6c9')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 6)]))
        story.append(t); story.append(Spacer(1, 15))
        story.append(P("📊 جدول المقارنة التفصيلي", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        data = [[ar(x) for x in
            ["العنصر", "المعيار", "المحسوب", "الفرق", "%", "التقييم"]]]
        cmds = [('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#9e9e9e')),
            ('PADDING', (0, 0), (-1, -1), 6)]
        for i, c in enumerate(result["comparison"], 1):
            data.append([ar(c["العنصر"]), f"{c['المعيار']:.2f}",
                f"{c['المحسوب']:.2f}", f"{c['الفرق']:+.3f}",
                f"{c['الفرق %']:+.2f}%", ar(c["التقييم"])])
            bg = ('#e8f5e9' if c["score"] >= 70
                  else '#ffebee' if c["score"] < 50 else '#fff8e1')
            cmds.append(('BACKGROUND', (0, i), (-1, i), HexColor(bg)))
        ct = Table(data, colWidths=[90, 65, 65, 65, 65, 120])
        ct.setStyle(TableStyle(cmds))
        story.append(ct); story.append(Spacer(1, 15))
        story.append(P("🌾 مكونات التركيبة", size=14, color='#1b5e20'))
        story.append(Spacer(1, 8))
        ing_data = [[ar("المكوّن"), ar("%"), ar("كجم/طن")]]
        for ing, pct in result["formula"].items():
            ing_data.append([ar(ing), f"{pct:.2f}%", f"{pct * 10:.1f}"])
        it = Table(ing_data, colWidths=[280, 110, 110])
        it.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_mgr.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.8, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [HexColor('#ffffff'), HexColor('#f5f5f5')])]))
        story.append(it)
        story.append(PageBreak())
        story.append(P("📈 الرسوم البيانية", size=14, color='#1b5e20'))
        story.append(Spacer(1, 10))
        try:
            bf = create_colorful_bar_chart(result["standard"],
                                            result["actual"])
            if bf:
                story.append(RLImage(bf, width=460, height=250))
                story.append(Spacer(1, 10))
        except Exception: pass
        try:
            pf = create_colorful_pie_chart(result["formula"])
            if pf:
                story.append(RLImage(pf, width=380, height=240))
        except Exception: pass
        try:
            pdf_gen._add_references_page(story, result["animal_type"],
                                           result["production_type"])
        except Exception: pass
        story.append(Spacer(1, 30))
        story.append(P(SUPERVISOR, size=16, align=TA_CENTER,
                        color='#c62828'))
        story.append(P(SUPERVISOR_TITLE, size=11, align=TA_CENTER,
                        color='#1b5e20'))
        doc.build(story, onFirstPage=pdf_gen._draw_page,
                  onLaterPages=pdf_gen._draw_page)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"⚠️ generate_lab_pdf: {e}")
        return None


def export_comparison_to_excel(standard, calculated, requester_name="",
                                 animal="", stage="", formula=None,
                                 standard_key=""):
    if not OPENPYXL_AVAILABLE: return b""
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "مقارنة"
    ws.sheet_view.rightToLeft = True
    hf = Font(name='Arial', size=12, bold=True, color='FFFFFF')
    hfill = PatternFill('solid', fgColor='1B5E20')
    ct = Alignment(horizontal='center', vertical='center', wrap_text=True)
    thin = Side(border_style='thin', color='9E9E9E')
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    ws.merge_cells('A1:F1'); ws['A1'] = APP_NAME
    ws['A1'].font = Font(name='Arial', size=14, bold=True, color='1B5E20')
    ws['A1'].alignment = ct
    headers = ["العنصر","المعيار","المحسوب","الفرق","% الفرق","التقييم"]
    for c, hh in enumerate(headers, 1):
        cell = ws.cell(row=4, column=c, value=hh)
        cell.font = hf; cell.fill = hfill; cell.alignment = ct
        cell.border = bd
    labels = {"CP":"بروتين","DP":"مهضوم","SE":"SE","NDF":"NDF","ADF":"ADF",
              "EE":"دهن","ASH":"رماد","Ca":"Ca","P":"P"}
    row = 5
    for k in ["CP","DP","SE","NDF","ADF","EE","ASH","Ca","P"]:
        if k not in standard or standard[k] == 0: continue
        sv, cv = standard[k], calculated.get(k, 0); diff = cv - sv
        pct = (diff / sv * 100) if sv else 0
        ev = evaluate_difference(pct, standard_value=sv)
        vals = [labels[k], round(sv, 2), round(cv, 2), round(diff, 3),
                round(pct, 2), ev["label"]]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.alignment = ct; cell.border = bd
            cell.fill = PatternFill('solid',
                fgColor=ev["bg"].replace('#', ''))
        row += 1
    for c in range(1, 7):
        ws.column_dimensions[get_column_letter(c)].width = 22
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════
# الصور
# ═══════════════════════════════════════════════════════════════════════

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
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600",
}

@st.cache_data(ttl=3600)
def get_img_b64(paths):
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception: pass
    return None

img_base64 = get_img_b64(tuple(PHOTO_OPTIONS))


# ═══════════════════════════════════════════════════════════════════════
# الحظائر v11.9 — مراوح + هياكل + عزل
# ═══════════════════════════════════════════════════════════════════════

BARN_DESIGN_STANDARDS = {
    "دواجن_لاحم": {
        "name_ar": "دواجن لاحم", "area_per_head": 0.10,
        "feeder_cm_per_head": 5.0, "drinker_cm_per_head": 2.5,
        "height_m": 2.8, "width_m": 12.0,
        "ach_summer": 60, "ach_winter": 8, "vent_open_ratio": 0.20,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "خطية", "drinker_type": "حلمات",
        "aisle_m": 1.2, "central_aisle": True,
        "temp_optimal_c": 24, "humidity_optimal": 60,
        "structure_type": "هيكل معدني (Steel Frame)",
        "roof_material": "ساندوتش بانل + عزل بولي يوريثان",
        "wall_material": "ستائر جانبية قابلة للسحب",
        "floor_material": "خرسانة مسلحة + فرشة نشارة",
        "insulation_thickness_cm": 5.0,
        "ventilation_type": "نفق + جانبي",
        "tunnel_fan_cfm": 12000, "tunnel_fan_hp": 1.5,
        "tunnel_fan_diameter_cm": 90,
        "side_fan_cfm": 5000, "side_fan_hp": 0.75,
        "cooling_pad_enabled": True,
        "cooling_pad_m2_per_1000cfm": 0.5,
        "lighting_lux": 30, "light_hours": 18,
        "water_per_head_L": 0.25, "waterer_flow_L_min": 0.5},
    "دواجن_بياض": {
        "name_ar": "دواجن بياض", "area_per_head": 0.15,
        "feeder_cm_per_head": 10.0, "drinker_cm_per_head": 2.5,
        "height_m": 3.0, "width_m": 12.0,
        "ach_summer": 40, "ach_winter": 6, "vent_open_ratio": 0.20,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "سلسلة", "drinker_type": "حلمات",
        "aisle_m": 1.2, "central_aisle": True,
        "temp_optimal_c": 22, "humidity_optimal": 60,
        "structure_type": "هيكل معدني (Steel Frame)",
        "roof_material": "ساندوتش بانل + عزل",
        "wall_material": "ستائر + شبك",
        "floor_material": "خرسانة مسلحة",
        "insulation_thickness_cm": 5.0,
        "ventilation_type": "نفق + جانبي",
        "tunnel_fan_cfm": 12000, "tunnel_fan_hp": 1.5,
        "tunnel_fan_diameter_cm": 90,
        "side_fan_cfm": 5000, "side_fan_hp": 0.75,
        "cooling_pad_enabled": True,
        "cooling_pad_m2_per_1000cfm": 0.5,
        "lighting_lux": 20, "light_hours": 16,
        "water_per_head_L": 0.3, "waterer_flow_L_min": 0.5},
    "أبقار": {
        "name_ar": "أبقار", "area_per_head": 5.0,
        "feeder_cm_per_head": 70.0, "drinker_cm_per_head": 6.0,
        "height_m": 4.5, "width_m": 15.0,
        "ach_summer": 25, "ach_winter": 4, "vent_open_ratio": 0.35,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "وسطية", "drinker_type": "حوض",
        "aisle_m": 3.5, "central_aisle": True,
        "temp_optimal_c": 15, "humidity_optimal": 65,
        "structure_type": "هيكل معدني ثقيل (Heavy Steel)",
        "roof_material": "صاج مجلفن + عزل فايبرجلاس",
        "wall_material": "شبك + ستائر جانبية",
        "floor_material": "خرسانة مسلحة + مفارش مطاطية",
        "insulation_thickness_cm": 3.0,
        "ventilation_type": "تقطيعي + جانبي",
        "tunnel_fan_cfm": 20000, "tunnel_fan_hp": 2.0,
        "tunnel_fan_diameter_cm": 120,
        "side_fan_cfm": 8000, "side_fan_hp": 1.0,
        "cooling_pad_enabled": False,
        "cooling_pad_m2_per_1000cfm": 0.4,
        "lighting_lux": 200, "light_hours": 16,
        "water_per_head_L": 80, "waterer_flow_L_min": 10},
    "أغنام": {
        "name_ar": "أغنام", "area_per_head": 1.5,
        "feeder_cm_per_head": 35.0, "drinker_cm_per_head": 4.0,
        "height_m": 3.5, "width_m": 10.0,
        "ach_summer": 30, "ach_winter": 5, "vent_open_ratio": 0.30,
        "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "خرسانية", "drinker_type": "حوض",
        "aisle_m": 2.0, "central_aisle": True,
        "temp_optimal_c": 18, "humidity_optimal": 65,
        "structure_type": "هيكل معدني متوسط",
        "roof_material": "صاج مجلفن",
        "wall_material": "شبك + ستائر",
        "floor_material": "خرسانة + فرشة قش",
        "insulation_thickness_cm": 2.5,
        "ventilation_type": "طبيعي + جانبي",
        "tunnel_fan_cfm": 14000, "tunnel_fan_hp": 1.5,
        "tunnel_fan_diameter_cm": 90,
        "side_fan_cfm": 6000, "side_fan_hp": 1.0,
        "cooling_pad_enabled": False,
        "cooling_pad_m2_per_1000cfm": 0.3,
        "lighting_lux": 100, "light_hours": 14,
        "water_per_head_L": 6, "waterer_flow_L_min": 5},
    "ماعز": {
        "name_ar": "ماعز", "area_per_head": 1.5,
        "feeder_cm_per_head": 35.0, "drinker_cm_per_head": 4.0,
        "height_m": 3.5, "width_m": 10.0,
        "ach_summer": 30, "ach_winter": 5, "vent_open_ratio": 0.30,
        "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "مرتفعة", "drinker_type": "حوض",
        "aisle_m": 2.0, "central_aisle": True,
        "temp_optimal_c": 20, "humidity_optimal": 65,
        "structure_type": "هيكل معدني متوسط",
        "roof_material": "صاج مجلفن",
        "wall_material": "شبك + ستائر",
        "floor_material": "خرسانة + فرشة",
        "insulation_thickness_cm": 2.5,
        "ventilation_type": "طبيعي + جانبي",
        "tunnel_fan_cfm": 14000, "tunnel_fan_hp": 1.5,
        "tunnel_fan_diameter_cm": 90,
        "side_fan_cfm": 6000, "side_fan_hp": 1.0,
        "cooling_pad_enabled": False,
        "cooling_pad_m2_per_1000cfm": 0.3,
        "lighting_lux": 100, "light_hours": 14,
        "water_per_head_L": 6, "waterer_flow_L_min": 5},
    "إبل": {
        "name_ar": "إبل", "area_per_head": 10.0,
        "feeder_cm_per_head": 100.0, "drinker_cm_per_head": 8.0,
        "height_m": 4.5, "width_m": 15.0,
        "ach_summer": 20, "ach_winter": 4, "vent_open_ratio": 0.40,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "مرتفعة", "drinker_type": "حوض كبير",
        "aisle_m": 4.0, "central_aisle": True,
        "temp_optimal_c": 25, "humidity_optimal": 50,
        "structure_type": "هيكل معدني ثقيل",
        "roof_material": "صاج مجلفن + عزل",
        "wall_material": "شبك فقط",
        "floor_material": "رمل + خرسانة جزئية",
        "insulation_thickness_cm": 3.0,
        "ventilation_type": "طبيعي مفتوح",
        "tunnel_fan_cfm": 20000, "tunnel_fan_hp": 2.0,
        "tunnel_fan_diameter_cm": 120,
        "side_fan_cfm": 8000, "side_fan_hp": 1.0,
        "cooling_pad_enabled": True,
        "cooling_pad_m2_per_1000cfm": 0.4,
        "lighting_lux": 100, "light_hours": 12,
        "water_per_head_L": 50, "waterer_flow_L_min": 8},
    "خيول": {
        "name_ar": "خيول", "area_per_head": 16.0,
        "feeder_cm_per_head": 100.0, "drinker_cm_per_head": 10.0,
        "height_m": 4.0, "width_m": 15.0,
        "ach_summer": 25, "ach_winter": 5, "vent_open_ratio": 0.30,
        "roof_type": "gable", "slope_pct": 25.0,
        "feeder_type": "مرتفعة", "drinker_type": "حوض",
        "aisle_m": 3.5, "central_aisle": True,
        "temp_optimal_c": 18, "humidity_optimal": 60,
        "structure_type": "هيكل معدني أو خشبي",
        "roof_material": "صاج + عزل",
        "wall_material": "خشب + شبك",
        "floor_material": "خرسانة + فرشة نشارة",
        "insulation_thickness_cm": 3.0,
        "ventilation_type": "طبيعي",
        "tunnel_fan_cfm": 16000, "tunnel_fan_hp": 1.5,
        "tunnel_fan_diameter_cm": 90,
        "side_fan_cfm": 6000, "side_fan_hp": 1.0,
        "cooling_pad_enabled": False,
        "cooling_pad_m2_per_1000cfm": 0.3,
        "lighting_lux": 200, "light_hours": 12,
        "water_per_head_L": 40, "waterer_flow_L_min": 10},
    "أرانب": {
        "name_ar": "أرانب", "area_per_head": 0.30,
        "feeder_cm_per_head": 8.0, "drinker_cm_per_head": 2.0,
        "height_m": 2.5, "width_m": 8.0,
        "ach_summer": 40, "ach_winter": 6, "vent_open_ratio": 0.25,
        "roof_type": "gable", "slope_pct": 20.0,
        "feeder_type": "معدنية", "drinker_type": "نبل",
        "aisle_m": 1.2, "central_aisle": True,
        "temp_optimal_c": 20, "humidity_optimal": 65,
        "structure_type": "هيكل معدني خفيف",
        "roof_material": "ساندوتش بانل",
        "wall_material": "شبك + ستائر",
        "floor_material": "بطاريات معدنية",
        "insulation_thickness_cm": 3.0,
        "ventilation_type": "نفق صغير",
        "tunnel_fan_cfm": 8000, "tunnel_fan_hp": 0.75,
        "tunnel_fan_diameter_cm": 60,
        "side_fan_cfm": 3000, "side_fan_hp": 0.5,
        "cooling_pad_enabled": True,
        "cooling_pad_m2_per_1000cfm": 0.4,
        "lighting_lux": 30, "light_hours": 16,
        "water_per_head_L": 0.35, "waterer_flow_L_min": 0.3},
    "سمان": {
        "name_ar": "سمان", "area_per_head": 0.025,
        "feeder_cm_per_head": 2.0, "drinker_cm_per_head": 1.0,
        "height_m": 2.0, "width_m": 6.0,
        "ach_summer": 50, "ach_winter": 8, "vent_open_ratio": 0.25,
        "roof_type": "mono", "slope_pct": 15.0,
        "feeder_type": "خطية", "drinker_type": "حلمات",
        "aisle_m": 0.8, "central_aisle": False,
        "temp_optimal_c": 26, "humidity_optimal": 65,
        "structure_type": "هيكل معدني خفيف",
        "roof_material": "ساندوبانل",
        "wall_material": "شبك + ستائر",
        "floor_material": "بطاريات",
        "insulation_thickness_cm": 4.0,
        "ventilation_type": "نفق",
        "tunnel_fan_cfm": 10000, "tunnel_fan_hp": 1.0,
        "tunnel_fan_diameter_cm": 60,
        "side_fan_cfm": 4000, "side_fan_hp": 0.75,
        "cooling_pad_enabled": True,
        "cooling_pad_m2_per_1000cfm": 0.5,
        "lighting_lux": 20, "light_hours": 16,
        "water_per_head_L": 0.06, "waterer_flow_L_min": 0.1},
}


def calculate_barn_dimensions(key, count, barn_system="أرضي مفتوح"):
    std = BARN_DESIGN_STANDARDS.get(key)
    if not std: return None
    area = count * std["area_per_head"]
    width = std["width_m"]
    length = max(area / width, 6.0)
    height = std["height_m"]
    if "بطاريات" in barn_system and key in ("دواجن_لاحم", "دواجن_بياض",
                                              "سمان", "أرانب"):
        area *= 0.55
        length = max(area / width, 6.0)
    volume = length * width * height
    roof_rise = (width / 2) * (std["slope_pct"] / 100)
    ridge = height + roof_rise
    roof_slope_len = np.sqrt((width/2)**2 + roof_rise**2)
    roof_area = (2 * length * roof_slope_len
                 if std["roof_type"] == "gable" else length * width)
    wall_area = 2 * length * height + 2 * width * height
    floor_area = length * width
    feeders = max(1, int(np.ceil(count * std["feeder_cm_per_head"] / 300)))
    drinkers = max(1, int(np.ceil(count * std["drinker_cm_per_head"] / 200)))
    vent_flow_summer_m3h = volume * std["ach_summer"]
    vent_flow_winter_m3h = volume * std["ach_winter"]
    vent_flow_summer_cfm = vent_flow_summer_m3h * 35.3147 / 60
    vent_flow_winter_cfm = vent_flow_winter_m3h * 35.3147 / 60
    tunnel_fan_cfm = std["tunnel_fan_cfm"]
    tunnel_fans_count = max(1, int(np.ceil(vent_flow_summer_cfm / tunnel_fan_cfm)))
    tunnel_fans_hp_total = tunnel_fans_count * std["tunnel_fan_hp"]
    side_fan_cfm = std["side_fan_cfm"]
    side_fans_count = max(1, int(np.ceil(vent_flow_winter_cfm / side_fan_cfm)))
    side_fans_hp_total = side_fans_count * std["side_fan_hp"]
    cooling_pad_area_m2 = 0.0
    if std.get("cooling_pad_enabled", False):
        cooling_pad_area_m2 = round(
            vent_flow_summer_cfm * std["cooling_pad_m2_per_1000cfm"] / 1000, 2)
    vent_open_area_m2 = round(length * height * std["vent_open_ratio"], 2)
    light_fixtures = max(1, int(np.ceil(floor_area / 100)))
    steel_weight_kg = round(floor_area * 25.0, 1)
    insulation_area_m2 = round(roof_area + wall_area * 0.6, 2)
    insulation_thickness_mm = std.get("insulation_thickness_cm", 3.0) * 10
    water_per_day_L = count * std.get("water_per_head_L", 6)
    cost_structure = floor_area * 60
    cost_roof = roof_area * 25
    cost_walls = wall_area * 15
    cost_floor = floor_area * 30
    cost_fans_tunnel = tunnel_fans_count * 450
    cost_fans_side = side_fans_count * 250
    cost_cooling_pad = cooling_pad_area_m2 * 80
    cost_lighting = light_fixtures * 40
    cost_feeders = feeders * 180
    cost_drinkers = drinkers * 90
    total_cost_estimate = round(cost_structure + cost_roof + cost_walls +
        cost_floor + cost_fans_tunnel + cost_fans_side + cost_cooling_pad +
        cost_lighting + cost_feeders + cost_drinkers, 0)
    return {
        "standard": std, "count": count,
        "total_area_m2": round(area, 2),
        "length_m": round(length, 2), "width_m": round(width, 2),
        "height_m": round(height, 2), "ridge_height_m": round(ridge, 2),
        "volume_m3": round(volume, 1),
        "roof_type": std["roof_type"], "slope_pct": std["slope_pct"],
        "roof_area_m2": round(roof_area, 2),
        "wall_area_m2": round(wall_area, 2),
        "feeders_count": feeders, "drinkers_count": drinkers,
        "total_feeder_length_m": round(count * std["feeder_cm_per_head"] / 100, 1),
        "total_drinker_length_m": round(count * std["drinker_cm_per_head"] / 100, 1),
        "feeder_type": std.get("feeder_type", "خطية"),
        "drinker_type": std.get("drinker_type", "حوض"),
        "vent_flow_summer_m3h": int(vent_flow_summer_m3h),
        "vent_flow_winter_m3h": int(vent_flow_winter_m3h),
        "vent_flow_summer_cfm": int(vent_flow_summer_cfm),
        "vent_flow_winter_cfm": int(vent_flow_winter_cfm),
        "vent_open_area_m2": vent_open_area_m2,
        "ventilation_type": std.get("ventilation_type", "نفق + جانبي"),
        "tunnel_fans_count": tunnel_fans_count,
        "tunnel_fan_spec": (f"{std['tunnel_fan_diameter_cm']}\" — "
            f"{tunnel_fan_cfm} CFM — {std['tunnel_fan_hp']} HP"),
        "tunnel_fans_hp_total": tunnel_fans_hp_total,
        "side_fans_count": side_fans_count,
        "side_fan_spec": f"{side_fan_cfm} CFM — {std['side_fan_hp']} HP",
        "side_fans_hp_total": side_fans_hp_total,
        "cooling_pad_area_m2": cooling_pad_area_m2,
        "cooling_pad_enabled": std.get("cooling_pad_enabled", False),
        "structure_type": std.get("structure_type", "هيكل معدني"),
        "steel_weight_kg": steel_weight_kg,
        "roof_material": std.get("roof_material", "ساندوتش بانل"),
        "wall_material": std.get("wall_material", "ستائر"),
        "floor_material": std.get("floor_material", "خرسانة"),
        "roof_material_area_m2": round(roof_area, 2),
        "insulation_type": std.get("roof_material", ""),
        "insulation_area_m2": insulation_area_m2,
        "insulation_thickness_mm": insulation_thickness_mm,
        "lighting_lux": std.get("lighting_lux", 30),
        "light_hours": std.get("light_hours", 16),
        "light_fixtures": light_fixtures,
        "light_watts_total": 15 * light_fixtures,
        "water_per_head_L": std.get("water_per_head_L", 6),
        "water_per_day_L": round(water_per_day_L, 1),
        "waterer_flow_L_min": std.get("waterer_flow_L_min", 5),
        "cost_structure_usd": round(cost_structure, 0),
        "cost_roof_usd": round(cost_roof, 0),
        "cost_walls_usd": round(cost_walls, 0),
        "cost_floor_usd": round(cost_floor, 0),
        "cost_fans_tunnel_usd": round(cost_fans_tunnel, 0),
        "cost_fans_side_usd": round(cost_fans_side, 0),
        "cost_cooling_pad_usd": round(cost_cooling_pad, 0),
        "cost_lighting_usd": round(cost_lighting, 0),
        "cost_feeders_usd": round(cost_feeders, 0),
        "cost_drinkers_usd": round(cost_drinkers, 0),
        "cost_total_usd": total_cost_estimate,
        "aisle_m": std.get("aisle_m", 1.5),
        "central_aisle": std.get("central_aisle", True),
        "temp_optimal": std.get("temp_optimal_c", 20),
        "humidity_optimal": std.get("humidity_optimal", 60),
        "barn_key": key,
    }


def create_barn_3d_figure(dims):
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
        fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[0,0,W,W], z=[0,0,0,0],
            i=[0,0], j=[1,2], k=[2,3], color='#d7ccc8', opacity=0.7,
            name='الأرضية', hoverinfo='skip'))
        for xp in [0, L]:
            fig.add_trace(go.Mesh3d(x=[xp]*4, y=[0,W,W,0], z=[0,0,H,H],
                i=[0,0], j=[1,2], k=[2,3], color='#a1887f', opacity=0.3,
                showlegend=False, hoverinfo='skip'))
        for yp in [0, W]:
            fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[yp]*4, z=[0,0,H,H],
                i=[0,0], j=[1,2], k=[2,3], color='#a1887f', opacity=0.3,
                showlegend=False, hoverinfo='skip'))
        if dims["roof_type"] == "gable":
            fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[0,0,W/2,W/2],
                z=[H,H,RH,RH], i=[0,0], j=[1,2], k=[2,3],
                color='#8d6e63', opacity=0.55, name='السقف',
                hoverinfo='skip'))
            fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[W/2,W/2,W,W],
                z=[RH,RH,H,H], i=[0,0], j=[1,2], k=[2,3],
                color='#8d6e63', opacity=0.55, showlegend=False,
                hoverinfo='skip'))
        fan_count = dims["tunnel_fans_count"]
        for i in range(min(fan_count, 20)):
            xc = L - 0.05
            yc = (i + 0.5) * (W / max(fan_count, 1))
            fig.add_trace(go.Scatter3d(
                x=[xc], y=[yc], z=[H * 0.5], mode='markers+text',
                marker=dict(size=15, color='#1976d2', symbol='circle',
                            line=dict(color='#0d47a1', width=2)),
                text=[f'م{i+1}'], textposition='middle center',
                textfont=dict(size=8, color='white'),
                name='مروحة شفط' if i == 0 else None,
                showlegend=(i == 0)))
        side_count = dims["side_fans_count"]
        for i in range(min(side_count, 20)):
            xc = (i + 0.5) * (L / max(side_count, 1))
            fig.add_trace(go.Scatter3d(
                x=[xc], y=[0.1], z=[H * 0.7], mode='markers',
                marker=dict(size=10, color='#00897b', symbol='diamond',
                            line=dict(color='#004d40', width=1.5)),
                name='مروحة جانبية' if i == 0 else None,
                showlegend=(i == 0)))
        if dims.get("cooling_pad_enabled", False):
            pad_h = min(H * 0.6, 1.5)
            fig.add_trace(go.Mesh3d(
                x=[0, 0, 0, 0], y=[W*0.1, W*0.9, W*0.9, W*0.1],
                z=[H*0.2, H*0.2, H*0.2 + pad_h, H*0.2 + pad_h],
                i=[0,0], j=[1,2], k=[2,3], color='#4fc3f7', opacity=0.6,
                name='لوح تبريد', hoverinfo='skip'))
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
                name='معلف' if idx == 0 else None,
                showlegend=(idx == 0), hoverinfo='skip'))
        nd = dims["drinkers_count"]
        for i in range(min(nd, 20)):
            xc = (i + 0.5) * (L / nd)
            yc = W - aisle - 0.5 if dims.get("central_aisle", True) else W - 1.5
            fig.add_trace(go.Scatter3d(
                x=[xc], y=[min(yc, W - 0.2)], z=[0.4],
                mode='markers+text',
                marker=dict(size=10, color='#1976d2', symbol='diamond',
                            line=dict(color='#0d47a1', width=2)),
                text=[f'م{i+1}'], textposition='top center',
                textfont=dict(size=8, color='#0d47a1'),
                name='سقاية' if i == 0 else None,
                showlegend=(i == 0)))
        apr = min(20, max(1, int(np.sqrt(dims["count"]))))
        ax_, ay_, az_ = [], [], []
        for ri in range(apr):
            for ci in range(apr):
                if len(ax_) > 200: break
                ax_.append(0.8 + ci * (L - 1.6) / apr)
                ay_.append(1.0 + ri * (W - 2.0) / apr)
                az_.append(0.15)
        if ax_:
            fig.add_trace(go.Scatter3d(x=ax_, y=ay_, z=az_, mode='markers',
                marker=dict(size=2.5, color='#1b5e20', opacity=0.7),
                name=f'حيوانات ({dims["count"]})'))
        fig.update_layout(
            title=dict(text=f"🏗️ {std['name_ar']} — {dims['count']} رأس | "
                f"{dims['total_area_m2']} م² | {L:.1f}×{W:.1f}×{RH:.1f} م | "
                f"🌀 {fan_count} مروحة",
                font=dict(size=13, color='#1b5e20'), x=0.5),
            scene=dict(xaxis=dict(title='الطول', range=[-0.5, L+0.5]),
                yaxis=dict(title='العرض', range=[-0.5, W+0.5]),
                zaxis=dict(title='الارتفاع', range=[0, RH+0.5]),
                aspectmode='manual',
                aspectratio=dict(x=ax_x, y=ax_y, z=ax_z),
                camera=dict(eye=dict(x=1.5, y=-1.5, z=0.9))),
            height=max(600, min(850, 600 + int(dims["count"] / 100))),
            margin=dict(l=0, r=0, t=100, b=0), paper_bgcolor='white',
            legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.92)',
                        bordercolor='#2e7d32', borderwidth=1,
                        font=dict(size=10)))
        return fig
    except Exception: return None


def render_barn_to_pdf_image(dims):
    if not MATPLOTLIB_AVAILABLE: return None
    try:
        std = dims["standard"]
        L, W, H, RH = (dims["length_m"], dims["width_m"],
                        dims["height_m"], dims["ridge_height_m"])
        fig = plt.figure(figsize=(11, 7.5))
        ax = fig.add_subplot(111, projection='3d')
        floor = [[(0,0,0), (L,0,0), (L,W,0), (0,W,0)]]
        ax.add_collection3d(Poly3DCollection(floor, facecolors='#d7ccc8',
            edgecolors='#5d4037', alpha=0.75, linewidths=1.5))
        walls = [[(0,0,0),(L,0,0),(L,0,H),(0,0,H)],
            [(0,W,0),(L,W,0),(L,W,H),(0,W,H)],
            [(0,0,0),(0,W,0),(0,W,H),(0,0,H)],
            [(L,0,0),(L,W,0),(L,W,H),(L,0,H)]]
        ax.add_collection3d(Poly3DCollection(walls, facecolors='#a1887f',
            edgecolors='#5d4037', alpha=0.4, linewidths=1))
        if dims["roof_type"] == "gable":
            r1 = [[(0,0,H),(L,0,H),(L,W/2,RH),(0,W/2,RH)]]
            r2 = [[(0,W/2,RH),(L,W/2,RH),(L,W,H),(0,W,H)]]
            ax.add_collection3d(Poly3DCollection(r1, facecolors='#8d6e63',
                edgecolors='#4e342e', alpha=0.55, linewidths=1))
            ax.add_collection3d(Poly3DCollection(r2, facecolors='#8d6e63',
                edgecolors='#4e342e', alpha=0.55, linewidths=1))
        fans = dims.get("tunnel_fans_count", 0)
        for i in range(min(fans, 15)):
            yc = (i + 0.5) * (W / fans)
            ax.scatter([L], [yc], [H*0.5], c='#1976d2', s=150, marker='o',
                edgecolors='#0d47a1', linewidths=2, zorder=10)
        ax.set_xlim(0, L); ax.set_ylim(0, W); ax.set_zlim(0, RH + 0.5)
        ax.set_box_aspect((L, W, RH + 0.5))
        ax.set_xlabel('الطول (م)'); ax.set_ylabel('العرض (م)')
        ax.set_zlabel('الارتفاع (م)')
        ax.set_title(f"{std['name_ar']} — {dims['count']} رأس\n"
            f"{L:.1f}×{W:.1f}×{RH:.1f} م | {fans} مروحة",
            fontsize=13, color='#1b5e20', fontweight='bold', pad=15)
        ax.view_init(elev=22, azim=-55)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=140, bbox_inches='tight',
            facecolor='white')
        plt.close(); buf.seek(0); return buf
    except Exception: return None


def create_barn_animation_gif(dims, frames=20, fps=8):
    if not MATPLOTLIB_AVAILABLE or not PIL_AVAILABLE: return None
    try:
        std = dims["standard"]
        L, W, H, RH = (dims["length_m"], dims["width_m"],
                        dims["height_m"], dims["ridge_height_m"])
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        def draw():
            ax.clear()
            floor = [[(0,0,0), (L,0,0), (L,W,0), (0,W,0)]]
            ax.add_collection3d(Poly3DCollection(floor,
                facecolors='#d7ccc8', edgecolors='#5d4037',
                alpha=0.75, linewidths=1.5))
            walls = [[(0,0,0),(L,0,0),(L,0,H),(0,0,H)],
                [(0,W,0),(L,W,0),(L,W,H),(0,W,H)],
                [(0,0,0),(0,W,0),(0,W,H),(0,0,H)],
                [(L,0,0),(L,W,0),(L,W,H),(L,0,H)]]
            ax.add_collection3d(Poly3DCollection(walls,
                facecolors='#a1887f', edgecolors='#5d4037',
                alpha=0.4, linewidths=1))
            ax.set_xlim(0, L); ax.set_ylim(0, W); ax.set_zlim(0, RH + 0.5)
            ax.set_box_aspect((L, W, RH + 0.5))
            ax.set_title(f"{std['name_ar']} — {dims['count']} رأس",
                fontsize=12, color='#1b5e20', fontweight='bold')
        def animate(fn):
            draw()
            ax.view_init(elev=20, azim=(fn / frames) * 360)
            return fig,
        anim = animation.FuncAnimation(fig, animate, frames=frames,
            interval=1000 // fps, blit=False)
        tmp = tempfile.NamedTemporaryFile(suffix='.gif', delete=False)
        tmp_path = tmp.name; tmp.close()
        try:
            anim.save(tmp_path, writer='pillow', fps=fps, dpi=80)
            with open(tmp_path, 'rb') as f: data = f.read()
            os.unlink(tmp_path); plt.close(fig)
            return io.BytesIO(data)
        except Exception:
            try: os.unlink(tmp_path)
            except Exception: pass
            plt.close(fig); return None
    except Exception: return None


def generate_barn_pdf_report(dims):
    if not REPORTLAB_AVAILABLE: return b""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
        leftMargin=40, topMargin=115, bottomMargin=145)
    story = []
    def P(text, size=11, align=TA_RIGHT, color='#1a1a1a'):
        return Paragraph(ar(text), ParagraphStyle('s',
            fontName=font_mgr.font_name, fontSize=size, alignment=align,
            textColor=HexColor(color), spaceAfter=6, leading=size*1.6))
    std = dims["standard"]
    story.append(P("تقرير الحظيرة الشامل — تاور نولجي", size=20,
        align=TA_CENTER, color='#1b5e20'))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2.5,
        color=HexColor('#d4af37')))
    story.append(Spacer(1, 12))
    story.append(P("📐 الأبعاد والمساحة", size=14, color='#1b5e20'))
    info = [[ar("الحيوان"), ar(std["name_ar"])],
        [ar("العدد"), ar(str(dims["count"]))],
        [ar("المساحة"), ar(f"{dims['total_area_m2']} م²")],
        [ar("الطول × العرض"),
         ar(f"{dims['length_m']} × {dims['width_m']} م")],
        [ar("الارتفاع/القمة"),
         ar(f"{dims['height_m']} / {dims['ridge_height_m']} م")],
        [ar("الحجم"), ar(f"{dims['volume_m3']} م³")],
        [ar("مساحة السقف"), ar(f"{dims['roof_area_m2']} م²")],
        [ar("مساحة الجدران"), ar(f"{dims['wall_area_m2']} م²")]]
    t = Table(info, colWidths=[160, 330])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1),HexColor('#e8f5e9')),
        ('BOX',(0,0),(-1,-1),1.5,HexColor('#2e7d32')),
        ('INNERGRID',(0,0),(-1,-1),0.6,HexColor('#c8e6c9')),
        ('ALIGN',(0,0),(-1,-1),'RIGHT'),
        ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
        ('FONTSIZE',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),6),
        ('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(t); story.append(Spacer(1, 12))
    story.append(P("🌀 التهوية والمراوح", size=14, color='#1565c0'))
    vent = [
        [ar("نوع التهوية"), ar(dims.get("ventilation_type", "—"))],
        [ar("تدفق الصيف"),
         ar(f"{dims['vent_flow_summer_m3h']:,} م³/س "
            f"({dims['vent_flow_summer_cfm']:,} CFM)")],
        [ar("تدفق الشتاء"),
         ar(f"{dims['vent_flow_winter_m3h']:,} م³/س")],
        [ar("مراوح النفق"),
         ar(f"{dims['tunnel_fans_count']} × {dims['tunnel_fan_spec']}")],
        [ar("إجمالي HP النفق"),
         ar(f"{dims['tunnel_fans_hp_total']} HP")],
        [ar("مراوح جانبية"),
         ar(f"{dims['side_fans_count']} × {dims['side_fan_spec']}")],
        [ar("ألواح التبريد"),
         ar(f"{dims['cooling_pad_area_m2']} م²"
            if dims.get("cooling_pad_enabled") else "—")],
        [ar("فتحات التهوية"),
         ar(f"{dims['vent_open_area_m2']} م²")]]
    tv = Table(vent, colWidths=[160, 330])
    tv.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1),HexColor('#e3f2fd')),
        ('BOX',(0,0),(-1,-1),1.5,HexColor('#1565c0')),
        ('INNERGRID',(0,0),(-1,-1),0.6,HexColor('#bbdefb')),
        ('ALIGN',(0,0),(-1,-1),'RIGHT'),
        ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
        ('FONTSIZE',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),6),
        ('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(tv); story.append(Spacer(1, 12))
    story.append(P("🏗️ الهيكل والعزل", size=14, color='#6d4c41'))
    struct = [
        [ar("نوع الهيكل"), ar(dims.get("structure_type", "—"))],
        [ar("وزن الحديد"), ar(f"{dims['steel_weight_kg']:,} كجم")],
        [ar("السقف"), ar(dims.get("roof_material", "—"))],
        [ar("الجدران"), ar(dims.get("wall_material", "—"))],
        [ar("الأرضية"), ar(dims.get("floor_material", "—"))],
        [ar("العزل"),
         ar(f"{dims['insulation_area_m2']} م² × "
            f"{dims['insulation_thickness_mm']} مم")]]
    ts = Table(struct, colWidths=[160, 330])
    ts.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1),HexColor('#efebe9')),
        ('BOX',(0,0),(-1,-1),1.5,HexColor('#6d4c41')),
        ('INNERGRID',(0,0),(-1,-1),0.6,HexColor('#d7ccc8')),
        ('ALIGN',(0,0),(-1,-1),'RIGHT'),
        ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
        ('FONTSIZE',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),6),
        ('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(ts); story.append(Spacer(1, 12))
    story.append(P("💡 الإضاءة والمياه", size=14, color='#e65100'))
    eq = [
        [ar("إضاءة"), ar(f"{dims['lighting_lux']} لوكس × "
                         f"{dims['light_hours']} ساعة")],
        [ar("وحدات الإضاءة"), ar(f"{dims['light_fixtures']}")],
        [ar("ماء/يوم"), ar(f"{dims['water_per_day_L']:,.0f} لتر")],
        [ar("المعالف"),
         ar(f"{dims['feeders_count']} × {dims['feeder_type']}")],
        [ar("السقايات"),
         ar(f"{dims['drinkers_count']} × {dims['drinker_type']}")]]
    te = Table(eq, colWidths=[160, 330])
    te.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1),HexColor('#fff3e0')),
        ('BOX',(0,0),(-1,-1),1.5,HexColor('#e65100')),
        ('INNERGRID',(0,0),(-1,-1),0.6,HexColor('#ffe0b2')),
        ('ALIGN',(0,0),(-1,-1),'RIGHT'),
        ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
        ('FONTSIZE',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),6),
        ('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(te); story.append(Spacer(1, 12))
    img = render_barn_to_pdf_image(dims)
    if img:
        try:
            story.append(RLImage(img, width=480, height=340))
            story.append(Spacer(1, 12))
        except Exception: pass
    story.append(PageBreak())
    story.append(P("💰 التكاليف التقديرية ($)", size=14, color='#c62828'))
    costs = [[ar("البند"), ar("التكلفة $")],
        [ar("الهيكل المعدني"), f"${dims['cost_structure_usd']:,.0f}"],
        [ar("السقف"), f"${dims['cost_roof_usd']:,.0f}"],
        [ar("الجدران"), f"${dims['cost_walls_usd']:,.0f}"],
        [ar("الأرضية"), f"${dims['cost_floor_usd']:,.0f}"],
        [ar("مراوح النفق"), f"${dims['cost_fans_tunnel_usd']:,.0f}"],
        [ar("مراوح جانبية"), f"${dims['cost_fans_side_usd']:,.0f}"],
        [ar("ألواح التبريد"), f"${dims['cost_cooling_pad_usd']:,.0f}"],
        [ar("الإضاءة"), f"${dims['cost_lighting_usd']:,.0f}"],
        [ar("المعالف"), f"${dims['cost_feeders_usd']:,.0f}"],
        [ar("السقايات"), f"${dims['cost_drinkers_usd']:,.0f}"],
        [ar("الإجمالي"), f"${dims['cost_total_usd']:,.0f}"]]
    tc = Table(costs, colWidths=[280, 210])
    tc.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),
        ('TEXTCOLOR',(0,0),(-1,0),white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
        ('FONTSIZE',(0,0),(-1,-1),10),
        ('GRID',(0,0),(-1,-1),0.6,HexColor('#bdbdbd')),
        ('ROWBACKGROUNDS',(0,1),(-1,-2),
         [HexColor('#ffffff'), HexColor('#f5f5f5')]),
        ('BACKGROUND',(0,-1),(-1,-1),HexColor('#ffe082')),
        ('FONTSIZE',(0,-1),(-1,-1),12)]))
    story.append(tc); story.append(Spacer(1, 20))
    # ✅ v11.10: صفحة المراجع
    try:
        pdf_gen._add_references_page(story, dims.get("barn_key", "أبقار"),
                                       "عام")
    except Exception: pass
    sign = [[ar("توقيع المختص")], [ar(SUPERVISOR)],
            [ar(SUPERVISOR_TITLE)]]
    ts2 = Table(sign, colWidths=[400])
    ts2.setStyle(TableStyle([
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME',(0,0),(-1,-1),font_mgr.font_name),
        ('BOX',(0,0),(-1,-1),1,HexColor('#bdbdbd')),
        ('BACKGROUND',(0,0),(-1,0),HexColor('#e8f5e9'))]))
    story.append(ts2)
    doc.build(story, onFirstPage=pdf_gen._draw_page,
        onLaterPages=pdf_gen._draw_page)
    buffer.seek(0); return buffer.getvalue()


# ═══════════════════════════════════════════════════════════════════════
# الجدوى
# ═══════════════════════════════════════════════════════════════════════

TECHNICAL_FEASIBILITY_DATA = {
    "دواجن_لاحم": {"feed_per_day_g":120,"water_per_day_ml":220,
        "labor_per_1000":0.3,"cycle_days":42,"final_weight_kg":2.3,
        "production_type":"meat"},
    "دواجن_بياض": {"feed_per_day_g":110,"water_per_day_ml":250,
        "labor_per_1000":0.3,"eggs_per_year":310,"production_type":"eggs"},
    "أبقار": {"feed_per_day_g":20000,"water_per_day_ml":80000,
        "labor_per_1000":5.0,"milk_per_day_L":20,"lactation_days":305,
        "production_type":"milk"},
    "أغنام": {"feed_per_day_g":1800,"water_per_day_ml":6000,
        "labor_per_1000":1.5,"milk_per_day_L":1.5,"lactation_days":200,
        "production_type":"mixed"},
    "ماعز": {"feed_per_day_g":1500,"water_per_day_ml":6000,
        "labor_per_1000":1.5,"milk_per_day_L":2.5,"lactation_days":280,
        "production_type":"milk"},
    "إبل": {"feed_per_day_g":8000,"water_per_day_ml":50000,
        "labor_per_1000":3.0,"milk_per_day_L":5,"lactation_days":300,
        "production_type":"milk"},
    "خيول": {"feed_per_day_g":10000,"water_per_day_ml":40000,
        "labor_per_1000":4.0,"production_type":"service"},
    "أرانب": {"feed_per_day_g":180,"water_per_day_ml":350,
        "labor_per_1000":1.0,"cycle_days":70,"final_weight_kg":2.5,
        "production_type":"meat"},
    "سمان": {"feed_per_day_g":28,"water_per_day_ml":55,
        "labor_per_1000":0.5,"cycle_days":42,"final_weight_kg":0.25,
        "production_type":"meat"},
}

def calculate_technical_feasibility(key, count):
    std = BARN_DESIGN_STANDARDS.get(key)
    if not std: return None
    dims = calculate_barn_dimensions(key, count)
    if not dims: return None
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
        cyc = tech.get("cycle_days", 42); cyc_y = 365 / cyc
        production = {"unit": "كجم/سنة",
            "annual": count * tech.get("final_weight_kg", 2) * cyc_y,
            "cycles_year": cyc_y}
    elif ptype == "mixed":
        m_day = count * tech.get("milk_per_day_L", 1)
        production = {"unit": "لتر/سنة",
            "annual": m_day * tech.get("lactation_days", 200),
            "per_day": m_day}
    return {"barn_key": key, "std": std, "dims": dims, "count": count,
        "feed": {"per_head_day_kg": tech.get("feed_per_day_g", 100) / 1000,
            "total_day_kg": feed_day,
            "total_year_ton": feed_day * 365 / 1000},
        "water": {"per_head_day_L": tech.get("water_per_day_ml", 200) / 1000,
            "total_day_L": water_day,
            "total_year_m3": water_day * 365 / 1000},
        "labor": {"workers": workers, "animals_per_worker": count // workers},
        "production": production}


# ═══════════════════════════════════════════════════════════════════════
# الجلسة
# ═══════════════════════════════════════════════════════════════════════

DEFAULTS = {
    "approved": False, "user_role": None, "active_formula": {},
    "computed_ton_cost": 280.0, "inventory": {},
    "shared_comments": f"• مرحباً في {APP_NAME}\n• {DUA_SHORT}\n",
    "broiler_farms": {}, "barn_video_gif": None,
    "last_formulation_result": None, "last_formulation_context": None,
    "last_ocr_result": None, "last_ocr_nutrients": None,
    "lab_result": None, "lab_context": None,
    "owner_attempts": 0, "owner_lock_until": 0.0,
    "invoices": [], "formulation_history": [], "comments_list": [],
    "last_activity": _time.time(), "show_new_room": False}

for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

if not st.session_state["inventory"]:
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing in cat:
            st.session_state["inventory"][ing] = {"quantity": 25.0,
                "min_threshold": 5.0, "unit": "طن"}

class SharedStorage:
    _lock = threading.Lock(); FILE = "tawor_shared_state.json"
    @classmethod
    def _load(cls):
        try:
            if os.path.exists(cls.FILE):
                with open(cls.FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception: pass
        return {}
    @classmethod
    def _save(cls, data):
        try:
            with cls._lock:
                tmp = cls.FILE + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                os.replace(tmp, cls.FILE)
        except Exception: pass
    @classmethod
    def get(cls, key, default=None):
        with cls._lock: return cls._load().get(key, default)

def is_owner(): return st.session_state.get("user_role") == "owner"
def is_specialist(): return st.session_state.get("user_role") == "specialist"
def is_guest(): return st.session_state.get("user_role") == "guest"


def build_whatsapp_link(formula, animal, quality, cost):
    import urllib.parse
    body = "🌾 *تاور نولجي — تركيبة علفية*\n\n"
    body += f"🐾 الحيوان: {animal}\n⭐ الجودة: {quality:.1f}%\n"
    body += f"💰 التكلفة: ${cost:.2f}/كجم\n\n*المكونات:*\n"
    for ing, pct in formula.items(): body += f"• {ing}: {pct:.2f}%\n"
    body += f"\n📱 {SUPERVISOR}\n{PLATFORM_URL}"
    num = WHATSAPP_NUMBER.replace('+', '').replace(' ', '')
    return f"https://wa.me/{num}?text={urllib.parse.quote(body)}"

def build_email_link(formula, animal, quality, cost):
    import urllib.parse
    body = f"تاور نولجي — تركيبة\n\nالحيوان: {animal}\n"
    body += f"الجودة: {quality:.1f}%\nالتكلفة: ${cost:.2f}/كجم\n\n"
    for ing, pct in formula.items(): body += f"  - {ing}: {pct:.2f}%\n"
    body += f"\n{SUPERVISOR}\n{PLATFORM_URL}"
    subject = f"تركيبة علفية — {animal} — {datetime.now():%Y-%m-%d}"
    return (f"mailto:{OWNER_EMAIL}?subject={urllib.parse.quote(subject)}"
            f"&body={urllib.parse.quote(body)}")

def render_share_buttons(formula, animal, quality, cost, key_suffix=""):
    st.markdown("### 📤 مشاركة التركيبة")
    c1, c2, c3 = st.columns(3)
    wa = build_whatsapp_link(formula, animal, quality, cost)
    em = build_email_link(formula, animal, quality, cost)
    with c1:
        st.markdown(f'<a href="{wa}" target="_blank" '
            f'style="display:block; padding:12px; background:#25d366; '
            f'color:white; text-decoration:none; border-radius:10px; '
            f'text-align:center; font-weight:700; border:2px solid #128c7e;">'
            f'📱 إرسال واتساب</a>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<a href="{em}" '
            f'style="display:block; padding:12px; background:#1565c0; '
            f'color:white; text-decoration:none; border-radius:10px; '
            f'text-align:center; font-weight:700; border:2px solid #0d47a1;">'
            f'✉️ إرسال بريد</a>', unsafe_allow_html=True)
    with c3:
        if st.button("📋 عرض النص", key=f"copy_{key_suffix}",
                use_container_width=True):
            txt = (f"تركيبة {animal} — جودة {quality:.1f}% — "
                   f"${cost:.2f}/كجم\n")
            for ing, pct in formula.items():
                txt += f"  - {ing}: {pct:.2f}%\n"
            st.code(txt, language="text")


# ═══════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');
* { font-family: 'Cairo', 'Amiri', sans-serif; color: #1a1a1a !important; }
html, body, [data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600");
    background-size: cover; background-position: center;
    background-attachment: fixed;
}
.stApp { background: transparent; }
.main-box { background: rgba(255,255,255,0.92); padding: 32px;
    border-radius: 22px; box-shadow: 0 15px 45px rgba(0,0,0,0.15);
    margin-bottom: 70px; backdrop-filter: blur(12px);
    border: 1px solid rgba(212,175,55,0.2); }
@keyframes duaGlow {
    0%,100% { box-shadow: 0 15px 45px rgba(0,0,0,0.4),
              inset 0 0 30px rgba(212,175,55,0.2); }
    50% { box-shadow: 0 15px 45px rgba(0,0,0,0.5),
          inset 0 0 45px rgba(212,175,55,0.45); }
}
.dua-main-box { background: linear-gradient(135deg, #0d3011, #1b5e20,
    #2e7d32, #1b5e20, #0d3011); background-size: 200% 200%;
    animation: duaGlow 4s ease-in-out infinite; padding: 34px 28px;
    border-radius: 22px; border: 4px solid #d4af37; direction: rtl;
    text-align: center; margin: 25px 0; }
.dua-main-box * { color: white !important; }
.dua-main-box h3 { color: #d4af37 !important; font-size: 1.9rem;
    margin-bottom: 18px; font-weight: 900; }
.dua-main-box .names { display: inline-block;
    background: rgba(212,175,55,0.25); font-size: 1.65rem;
    font-weight: 900; color: #ffeb3b !important; margin: 20px 0;
    padding: 16px 30px; border: 2px solid #d4af37; border-radius: 16px;
    font-family: 'Amiri', serif !important; }
.dua-main-box p.quran { font-family: 'Amiri', serif !important;
    font-size: 1.2rem; color: #d4af37 !important; margin-top: 22px;
    padding: 18px 25px; background: rgba(0,0,0,0.25);
    border-radius: 12px; border-right: 5px solid #d4af37;
    border-left: 5px solid #d4af37; }
.visitor-dua-banner { background: linear-gradient(135deg, #fff8e1,
    #ffecb3, #ffe082); padding: 20px 28px; border-radius: 16px;
    border: 3px solid #d4af37; margin: 22px 0; direction: rtl;
    text-align: center; }
.visitor-dua-banner * { color: #4e342e !important; }
.visitor-dua-banner b { color: #c62828 !important;
    font-family: 'Amiri' !important; }
.dua-fixed-banner { position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32,
    #1b5e20, #0d3011); color: white !important; padding: 12px 20px;
    z-index: 9998; text-align: center; border-top: 3px solid #d4af37;
    font-family: 'Amiri', serif !important; font-size: 1.05rem;
    font-weight: bold; }
.dua-fixed-banner * { color: #ffeb3b !important;
    font-family: 'Amiri' !important; }
.section-title { color: #1b5e20 !important;
    border-right: 6px solid #2e7d32; padding: 12px 18px;
    text-align: right; font-size: 1.5rem; font-weight: 900;
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
    padding: 24px; border-radius: 22px;
    border-right: 8px solid #1b5e20; margin: 18px 0;
    direction: rtl; text-align: right; }
.quality-bad-v113 { background: linear-gradient(135deg, #ffcdd2, #ef9a9a);
    padding: 24px; border-radius: 22px;
    border-right: 8px solid #c62828; margin: 18px 0;
    direction: rtl; text-align: right; }
.profile-img-style { width: 150px; height: 150px;
    border-radius: 50%; object-fit: cover; border: 4px solid #d4af37;
    display: block; margin: 0 auto; }
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
.stTabs [aria-selected="true"] { background: linear-gradient(135deg,
    #2e7d32, #1b5e20) !important; }
.stTabs [aria-selected="true"] * { color: white !important; }
[data-testid="stMetric"] { background: linear-gradient(135deg,
    #ffffff, #f1f8e9); padding: 14px 18px; border-radius: 16px;
    border-right: 4px solid #2e7d32; }
[data-testid="stMetricValue"] { color: #1b5e20 !important;
    font-weight: 900 !important; }
</style>
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

if st.session_state.get("approved", False) and not _session_valid():
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.error("⚠️ جلسة غير صالحة"); st.stop()

if not st.session_state.get("approved", False):
    st.markdown('<div class="main-box" style="max-width:980px; '
        'margin:30px auto; direction:rtl;">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <p style="font-size:1.1rem; color:#a5d6a7 !important;
            margin-bottom:12px;">
        نبدأ باسم الله، ونسألُه أن يتقبّلَ هذا العملَ صدقةً جاريةً عن:
        </p>
        <div class="names">🕊️ رحم الله والدي إسماعيل تاور
            وأختي ابتسام 🕊️</div>
        <p class="quran">{DUA_QURAN}</p>
        <p class="quran" style="margin-top:10px;">{DUA_VERSE}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 2px solid #d4af37; "
        "margin: 25px 0;'>", unsafe_allow_html=True)
    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        if img_base64:
            st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" '
                f'class="profile-img-style">', unsafe_allow_html=True)
        else:
            st.markdown(f'<img src="{ANIMAL_IMAGES["عام"]}" '
                f'class="profile-img-style">', unsafe_allow_html=True)
    with col_title:
        st.markdown(f"<h2 style='color:#2E7D32; text-align:right;'>"
            f"🌾 {APP_NAME}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#1565C0; text-align:right; "
            f"font-size:1.1rem;'>{APP_TAGLINE}</p>",
            unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#c62828; text-align:right;'>"
            f"{SUPERVISOR} — {SUPERVISOR_TITLE}</h4>",
            unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#1b5e20; "
        "margin-top:20px;'>🔐 اختر بوابتك</h3>", unsafe_allow_html=True)
    col_owner, col_spec, col_guest = st.columns(3)

    with col_owner:
        st.markdown("""<div style="background:linear-gradient(135deg,
            #e8f5e9,#c8e6c9); padding:16px; border-radius:12px;
            border:2px solid #2e7d32; text-align:center;
            min-height:150px;">
            <h4 style="color:#1b5e20; margin:0;">👑 المالك</h4>
            <p style="font-size:0.82rem; color:#444; margin-top:8px;">
            إدارة كاملة + مستودعات + فواتير</p></div>""",
            unsafe_allow_html=True)
        oc = st.text_input("كود المالك:", type="password", key="oc_v110")
        if st.button("👑 دخول", type="primary",
                use_container_width=True, key="b_owner_v110"):
            now = _time.time()
            lock = st.session_state.get("owner_lock_until", 0.0)
            if now < lock:
                st.error(f"🔒 انتظر {int(lock-now)}ث")
            elif check_owner_code(oc):
                st.session_state.update({"approved": True,
                    "user_role": "owner", "owner_attempts": 0,
                    "owner_lock_until": 0.0})
                st.rerun()
            else:
                n = st.session_state.get("owner_attempts", 0) + 1
                st.session_state["owner_attempts"] = n
                if n >= 3:
                    st.session_state["owner_lock_until"] = now + 300
                    st.error("🔒 3 محاولات فاشلة — قفل 5 دقائق")
                else:
                    st.error(f"❌ متبقٍ {3-n}")

    with col_spec:
        st.markdown("""<div style="background:linear-gradient(135deg,
            #e3f2fd,#bbdefb); padding:16px; border-radius:12px;
            border:2px solid #1565c0; text-align:center;
            min-height:150px;">
            <h4 style="color:#0d47a1; margin:0;">🔬 مختص</h4>
            <p style="font-size:0.82rem; color:#444; margin-top:8px;">
            NLP + OCR + مختبر + تقارير PDF</p></div>""",
            unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""<div style="text-align:center;
            font-size:0.85rem; color:#1565c0; padding:6px;">
            ✅ دخول مباشر — بدون كود</div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔬 دخول كمختص", type="primary",
                use_container_width=True, key="b_spec_v110"):
            st.session_state.update({"approved": True,
                "user_role": "specialist"})
            audit_log("SPEC_DIRECT_ACCESS", "no_code_v110")
            st.rerun()

    with col_guest:
        st.markdown("""<div style="background:linear-gradient(135deg,
            #fff8e1,#ffecb3); padding:16px; border-radius:12px;
            border:2px solid #d4af37; text-align:center;
            min-height:150px;">
            <h4 style="color:#e65100; margin:0;">👥 زائر</h4>
            <p style="font-size:0.82rem; color:#444; margin-top:8px;">
            حاسبة + مختبر + PDF + غرفة النقاش</p></div>""",
            unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👥 دخول كزائر", use_container_width=True,
                key="b_guest_v110"):
            st.session_state.update({"approved": True,
                "user_role": "guest"})
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
                  "guest": "زائر 👥"}.get(
                  st.session_state.get("user_role"), "—")
    st.markdown(f"<div style='text-align:left; padding:10px; "
        f"background:#f5f5f5; border-radius:10px;'>"
        f"الحساب: <b>{role_label}</b></div>", unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.cache_data.clear(); st.cache_resource.clear(); st.rerun()

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
        f"margin-bottom:0; font-weight:900; font-size:2.3rem;'>"
        f"🌾 {APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#1565C0; text-align:right; "
        f"font-size:1.25rem; font-weight:600; margin-top:8px;'>"
        f"{APP_TAGLINE}</p>", unsafe_allow_html=True)
    st.markdown(f"""<div style='background: linear-gradient(135deg,
        #fff8e1, #ffe082); padding: 12px 20px; border-radius: 12px;
        border-right: 6px solid #c62828; border-left: 6px solid #c62828;
        margin-top: 10px;'>
        <h3 style='color: #b71c1c; text-align:right; margin: 0;
            font-weight: 900; font-size: 1.55rem;'>👨‍🔬 {SUPERVISOR}</h3>
        <p style='color: #0d47a1; text-align:right; margin: 5px 0 0 0;
            font-weight: 700; font-size: 1.15rem;'>
            ✨ {SUPERVISOR_TITLE}</p>
    </div>""", unsafe_allow_html=True)

st.markdown(f'<div class="visitor-dua-banner">{DUA_VISITOR}</div>',
    unsafe_allow_html=True)
st.markdown("<hr style='border-top: 3px solid #2e7d32;'>",
    unsafe_allow_html=True)

role = st.session_state.get("user_role", "guest")

if role == "owner":
    tabs_titles = ["🔬 النمذجة", "🧪 مختبر التركيبات", "🎯 NLP",
                   "🌰 الزيوت", "🍼 بدائل الحليب",
                   "📷 OCR", "🏗️ الحظائر 3D", "📊 الجدوى",
                   "🐔 المزارع", "🏭 المستودعات", "🧾 الفواتير",
                   "🖨️ الديباجة", "💬 غرفة التواصل", "🎬 الاستديو",
                   "📈 التحليلات", "💬 التعليقات",
                   "📚 المراجع", "💡 المساعدة", "📖 الدليل"]
elif role == "specialist":
    tabs_titles = ["🔬 النمذجة", "🧪 مختبر التركيبات", "🎯 NLP",
                   "🌰 الزيوت", "🍼 بدائل الحليب",
                   "📷 OCR", "🏗️ الحظائر 3D", "📊 الجدوى",
                   "🐔 المزارع", "💬 غرفة التواصل",
                   "📚 المراجع", "💡 المساعدة", "📖 الدليل"]
else:
    tabs_titles = ["🧮 حاسبة مبسطة", "🧪 مختبر التركيبات",
                   "💬 غرفة التواصل", "📚 المراجع", "📖 الدليل"]

tabs = st.tabs(tabs_titles)
tab_map = {t: tab for t, tab in zip(tabs_titles, tabs)}


# ═══════════════════════════════════════════════════════════════════════
# 🧪 v11.10 — render_lab_tab (يعمل في كل البوابات)
# ═══════════════════════════════════════════════════════════════════════

def render_lab_tab(role="guest"):
    st.markdown('<div class="section-title">'
        '🧪 مختبر التركيبات الجاهزة</div>', unsafe_allow_html=True)
    st.caption("🔬 حلّل أي تركيبة علفية (من مصنع/مزرعة/جدول) "
               "وقارنها بالمعيار القياسي (NRC) مع تقرير PDF كامل")

    col1, col2 = st.columns(2)
    with col1:
        lab_animal = st.selectbox("🐾 نوع الحيوان:",
            ["أبقار", "أغنام", "ماعز", "إبل", "خيول",
             "دواجن", "سمان", "أسماك", "أرانب"], key="lab_animal_v110")
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
            "دواجن": ["لاحم", "بياض"],
            "سمان": ["تسمين", "بياض"],
            "أسماك": ["بادئ زريعة", "نمو", "تسمين"],
            "أرانب": ["تسمين", "حليب", "صيانة"],
        }
        lab_prod = st.selectbox("🎯 نوع الإنتاج:",
            lab_prod_map.get(lab_animal, ["عام"]), key="lab_prod_v110")

    st.markdown("### 📝 أدخل مكونات التركيبة")
    input_method = st.radio("طريقة الإدخال:",
        ["📊 جدول يدوي", "📋 لصق نص", "💾 من آخر تركيبة محفوظة"],
        horizontal=True, key="lab_method_v110")

    formula_input = {}

    if input_method == "📊 جدول يدوي":
        all_ings = list(_get_ingredient_lookup().keys())
        default_rows = pd.DataFrame({
            "المكوّن": [all_ings[0]] * 10, "النسبة %": [0.0] * 10})
        edited = st.data_editor(default_rows,
            use_container_width=True, hide_index=True, num_rows="dynamic",
            column_config={
                "المكوّن": st.column_config.SelectboxColumn(
                    options=all_ings, required=False, width="medium"),
                "النسبة %": st.column_config.NumberColumn(
                    min_value=0.0, max_value=100.0, step=0.5,
                    format="%.2f%%", width="small")},
            key="lab_editor_v110")
        for _, r in edited.iterrows():
            ing = r["المكوّن"]; pct = r["النسبة %"]
            if ing and pct and pct > 0:
                formula_input[ing] = formula_input.get(ing, 0) + float(pct)

    elif input_method == "📋 لصق نص":
        st.caption("مثال: `ذرة صفراء 45` — أو `ذرة صفراء 45%`")
        text_input = st.text_area("الصق التركيبة (سطر لكل مكوّن):",
            height=200, key="lab_text_v110",
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
            else:
                st.warning("⚠️ استخدم صيغة: `الاسم الرقم`")

    else:
        if st.session_state.get("active_formula"):
            active = st.session_state["active_formula"]
            st.info(f"📋 آخر تركيبة — {len(active)} مكوّن")
            st.dataframe(pd.DataFrame([
                {"المكوّن": k, "النسبة %": f"{v:.2f}"}
                for k, v in active.items()]),
                use_container_width=True, hide_index=True)
            if st.checkbox("استخدم هذه التركيبة", value=True,
                          key="lab_use_last_v110"):
                formula_input = dict(active)
        else:
            st.info("💡 لا توجد تركيبة — استخدم إدخال يدوي")

    if formula_input:
        total = sum(formula_input.values())
        if abs(total - 100) > 0.5:
            st.warning(f"⚠️ مجموع النسب = {total:.1f}% — سيتم التطبيع")
        else:
            st.success(f"✅ مجموع النسب = {total:.1f}%")

    if st.button("🔬 تشغيل المختبر", type="primary",
                 use_container_width=True, key="lab_run_v110"):
        if not formula_input:
            st.error("⚠️ أدخل التركيبة أولاً")
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

    if not st.session_state.get("lab_result"):
        return

    result = st.session_state["lab_result"]
    ctx = st.session_state.get("lab_context", {})
    quality = result["quality_score"]
    meets = quality >= 70

    st.markdown("---")
    st.markdown("### 📊 نتيجة التحليل")

    if meets:
        st.markdown(f"""<div class="quality-good-v113">
            <h3 style="color:#1b5e20; margin:0;">
            ✅ جودة التركيبة: {quality:.1f}%</h3>
            <p style="color:#2e7d32;">
            مطابقة للمعيار القياسي</p></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="quality-bad-v113">
            <h3 style="color:#c62828; margin:0;">
            ⚠️ جودة التركيبة: {quality:.1f}%</h3>
            <p style="color:#b71c1c;">تحتاج تحسين</p>
        </div>""", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🎯 الحيوان", ctx.get("animal", "—"))
    m2.metric("🧬 الجودة", f"{quality:.1f}%")
    m3.metric("💰 التكلفة", f"${result['cost_per_ton']:.2f}/طن")
    m4.metric("⚖️ Ca:P", f"{result['ca_p_ratio']:.2f}")

    st.markdown("### ⚡ توازن الطاقة والبروتين")
    bal1, bal2, bal3 = st.columns(3)
    e_share = result.get("energy_share_pct", 0)
    p_share = result.get("protein_share_pct", 0)
    bal1.metric("⚡ الطاقة", f"{e_share:.1f}%")
    bal2.metric("🧬 البروتين", f"{p_share:.1f}%")
    if p_share > e_share:
        bal3.metric("⚠️ الحالة", "بروتين أعلى!")
        st.warning(
            f"⚠️ البروتين ({p_share:.1f}%) أعلى من "
            f"الطاقة ({e_share:.1f}%)")
    else:
        bal3.metric("✅ الحالة", "متوازن")

    st.markdown("### 📋 جدول المقارنة التفصيلي")
    comp_df = pd.DataFrame([{
        "العنصر": c["العنصر"], "المعيار": f"{c['المعيار']:.2f}",
        "المحسوب": f"{c['المحسوب']:.2f}", "الفرق": f"{c['الفرق']:+.3f}",
        "الفرق %": f"{c['الفرق %']:+.2f}%",
        "التقييم": c["التقييم"]} for c in result["comparison"]])
    st.dataframe(comp_df, use_container_width=True, hide_index=True)

    st.markdown("### 📈 الرسوم البيانية")
    ch1, ch2 = st.columns(2)
    with ch1:
        bf = create_colorful_bar_chart(result["standard"],
                                        result["actual"])
        if bf:
            st.image(bf.getvalue(), caption="المقارنة",
                     use_container_width=True)
    with ch2:
        pf = create_colorful_pie_chart(result["formula"])
        if pf:
            st.image(pf.getvalue(), caption="التوزيع",
                     use_container_width=True)
    if result["actual"].get("P", 0) > 0:
        cf = create_ca_p_ratio_chart(
            result["actual"].get("Ca", 0),
            result["actual"].get("P", 0),
            result["standard"].get("Ca", 0),
            result["standard"].get("P", 0))
        if cf:
            st.image(cf.getvalue(), caption="⚖️ Ca:P",
                     use_container_width=True)

    with st.expander("📚 المراجع العلمية للتحليل", expanded=False):
        refs = result["references"]
        st.markdown(f"**📖 المرجع الأساسي:** {refs['primary']}")
        if refs.get("table"):
            st.markdown(f"**📑 الجدول:** {refs['table']}")
        if refs.get("secondary"):
            st.markdown("**📚 مراجع داعمة:**")
            for s in refs["secondary"]:
                st.markdown(f"- {s}")

    try:
        pdf_bytes = generate_lab_pdf(result, ctx)
        fname = (f"Lab_{ctx.get('animal', 'Analysis')}_"
                 f"{datetime.now():%Y%m%d_%H%M}.pdf")
        st.download_button("📄 تحميل تقرير PDF",
            pdf_bytes, file_name=fname, mime="application/pdf",
            use_container_width=True, type="primary",
            key="lab_pdf_dl_v110")
    except Exception as e:
        st.error(f"⚠️ PDF: {e}")

    render_share_buttons(result["formula"],
        ctx.get("animal", ""), quality,
        result["cost_per_ton"], key_suffix="lab_v110")


# ═══════════════════════════════════════════════════════════════════════
# حاسبة الزائر المبسطة
# ═══════════════════════════════════════════════════════════════════════

GUEST_PRODUCTION = {
    "أبقار": {
        "حليب": {"label": "🐄 حلابة (حليب)", "dp": 12.5, "cp": 17.5,
                 "se": 65, "name": "أبقار حلابة (استرشادي)"},
        "تسمين": {"label": "💪 تسمين", "dp": 11.5, "cp": 14.5,
                  "se": 72, "name": "تسمين عجول (استرشادي)"},
        "صيانة": {"label": "🌿 صيانة", "dp": 7.5, "cp": 10.0,
                  "se": 53, "name": "أبقار صيانة (استرشادي)"}},
    "أغنام": {
        "تسمين": {"label": "💪 تسمين حملان", "dp": 10.5, "cp": 14.0,
                  "se": 64, "name": "تسمين حملان (استرشادي)"},
        "مرضعات": {"label": "🥛 مرضعات", "dp": 10.5, "cp": 14.5,
                    "se": 62, "name": "نعاج مرضعات (استرشادي)"},
        "صيانة": {"label": "🌿 صيانة", "dp": 7.2, "cp": 9.5,
                  "se": 48, "name": "نعاج صيانة (استرشادي)"}},
    "ماعز": {
        "حليب": {"label": "🥛 حلابة", "dp": 10.2, "cp": 14.2,
                 "se": 60, "name": "عنزات حلابة (استرشادي)"},
        "تسمين": {"label": "💪 تسمين", "dp": 10.0, "cp": 13.5,
                  "se": 62, "name": "تسمين جديان (استرشادي)"},
        "صيانة": {"label": "🌿 صيانة", "dp": 6.8, "cp": 9.0,
                  "se": 46, "name": "عنزات صيانة (استرشادي)"}},
    "إبل": {
        "حليب": {"label": "🥛 حلابة", "dp": 11.5, "cp": 16.0,
                 "se": 64, "name": "إبل حلابة (استرشادي)"},
        "تسمين": {"label": "💪 تسمين", "dp": 9.5, "cp": 12.0,
                  "se": 65, "name": "إبل تسمين (استرشادي)"},
        "نمو": {"label": "🌱 نمو", "dp": 10.5, "cp": 13.5,
                "se": 60, "name": "إبل نمو (استرشادي)"}},
    "دواجن": {
        "لاحم_بادي": {"label": "🐔 لاحم بادي", "dp": 20.0, "cp": 23.0,
                      "se": 76, "name": "دواجن لاحم بادي (استرشادي)"},
        "لاحم_ناهي": {"label": "🐔 لاحم ناهي", "dp": 17.0, "cp": 19.5,
                      "se": 75, "name": "دواجن لاحم ناهي (استرشادي)"},
        "بياض": {"label": "🥚 بياض", "dp": 15.5, "cp": 18.0,
                 "se": 72, "name": "دواجن بياض (استرشادي)"}},
    "أسماك": {
        "بادئ": {"label": "🐟 بادئ", "dp": 32.0, "cp": 40.0,
                 "se": 72, "name": "أسماك بادئ (استرشادي)"},
        "نمو": {"label": "🐟 نمو", "dp": 25.0, "cp": 32.0,
                "se": 70, "name": "أسماك نمو (استرشادي)"},
        "تسمين": {"label": "🐟 تسمين", "dp": 22.0, "cp": 28.0,
                  "se": 68, "name": "أسماك تسمين (استرشادي)"}},
    "أرانب": {
        "تسمين": {"label": "🐇 تسمين", "dp": 15.0, "cp": 17.0,
                  "se": 65, "name": "أرانب تسمين (استرشادي)"},
        "أمهات": {"label": "🥛 أمهات", "dp": 18.0, "cp": 20.0,
                  "se": 68, "name": "أرانب أمهات (استرشادي)"}},
}

if role == "guest" and "🧮 حاسبة مبسطة" in tab_map:
    with tab_map["🧮 حاسبة مبسطة"]:
        try:
            st.markdown('<div class="section-title">'
                '🧮 حاسبة سريعة للزوار</div>', unsafe_allow_html=True)
            st.caption("💡 اختر الحيوان + الغرض → تركيبة استرشادية + PDF")

            c1, c2 = st.columns(2)
            with c1:
                g_animal = st.selectbox("🐾 نوع الحيوان:",
                    list(GUEST_PRODUCTION.keys()), key="g_animal_v110")
                prod_opts = GUEST_PRODUCTION[g_animal]
                prod_keys = list(prod_opts.keys())
                g_prod = st.selectbox("🎯 الغرض/الحالة:", prod_keys,
                    format_func=lambda x: prod_opts[x]["label"],
                    key="g_prod_v110")
                g_weight = st.number_input("⚖️ الوزن (كجم):", 1.0, 900.0,
                    400.0, 5.0, key="g_w_v110")
            with c2:
                g_count = st.number_input("🔢 عدد الرؤوس:", 1, 100000, 1, 1,
                    key="g_cnt_v110")
                g_name = st.text_input("👤 اسمك (اختياري):",
                    placeholder="اتركه فارغاً للزائر", key="g_name_v110")
                prod_info = prod_opts[g_prod]
                st.markdown(f"""<div style="background:linear-gradient(
                    135deg, #e8f5e9,#c8e6c9); padding:14px;
                    border-radius:12px; border-right:4px solid #2e7d32;
                    direction:rtl; text-align:right; margin-top:10px;">
                    <b>📊 المتطلبات الاسترشادية:</b><br>
                    🧬 DP ≈ <b>{prod_info['dp']:.1f}%</b> |
                    🧬 CP ≈ <b>{prod_info['cp']:.1f}%</b> |
                    ⚡ SE ≈ <b>{prod_info['se']:.0f}</b>
                </div>""", unsafe_allow_html=True)

            if st.button("🧮 احسب التركيبة", type="primary",
                    use_container_width=True, key="g_calc_v110"):
                prod_info = prod_opts[g_prod]
                if g_animal in ("أبقار", "أغنام", "ماعز", "إبل"):
                    rough = {"ذرة صفراء": 40, "شعير مطحون": 20,
                        "كسب فول صويا 44%": 18, "نخالة قمح (ردة)": 15,
                        "الحجر الجيري": 1.5, "ملح الطعام": 0.5,
                        "بريمكس مجترات": 0.25,
                        "فوسفات ثنائي الكالسيوم": 0.75}
                elif g_animal == "دواجن":
                    if "بادي" in g_prod:
                        rough = {"ذرة صفراء": 52,
                            "كسب فول صويا 48%": 36,
                            "زيت فول الصويا": 4,
                            "الحجر الجيري": 1.2,
                            "فوسفات ثنائي الكالسيوم": 1.8,
                            "ملح الطعام": 0.3,
                            "بريمكس تسمين دواجن": 0.3,
                            "ليسين نقي": 0.25, "ميثيونين نقي": 0.15}
                    elif "بياض" in g_prod:
                        rough = {"ذرة صفراء": 58,
                            "كسب فول صويا 44%": 22,
                            "نخالة قمح (ردة)": 6,
                            "الحجر الجيري": 8,
                            "فوسفات ثنائي الكالسيوم": 1.8,
                            "ملح الطعام": 0.3, "بريمكس بياض": 0.3,
                            "ميثيونين نقي": 0.1}
                    else:
                        rough = {"ذرة صفراء": 55,
                            "كسب فول صويا 48%": 32,
                            "زيت فول الصويا": 4,
                            "الحجر الجيري": 1.2,
                            "فوسفات ثنائي الكالسيوم": 1.8,
                            "ملح الطعام": 0.3,
                            "بريمكس تسمين دواجن": 0.3,
                            "ليسين نقي": 0.2, "ميثيونين نقي": 0.15}
                elif g_animal == "أسماك":
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
                else:
                    rough = {"برسيم حجازي": 35, "شعير مطحون": 30,
                        "كسب فول صويا 44%": 15,
                        "نخالة قمح (ردة)": 15,
                        "الحجر الجيري": 1.5, "ملح الطعام": 0.5,
                        "بريمكس مجترات": 0.25,
                        "فوسفات ثنائي الكالسيوم": 0.75}

                lookup = _get_ingredient_lookup()
                actual = compute_formula_nutrients(rough)
                score = 0; count_eval = 0
                for key, target in [("DP", prod_info["dp"]),
                                     ("CP", prod_info["cp"]),
                                     ("SE", prod_info["se"])]:
                    if target > 0:
                        diff = (abs(actual.get(key, 0) - target) /
                                target * 100)
                        ev = evaluate_difference(diff,
                            standard_value=target)
                        score += ev["score"]; count_eval += 1
                quality = score / count_eval if count_eval else 0
                cost = sum(rough[ing] / 100 *
                    lookup.get(ing, {}).get("price", 300) for ing in rough)

                st.success(f"✅ جودة: **{quality:.1f}%** | "
                    f"💰 التكلفة: **${cost:.2f}/طن**")
                st.markdown("### 📋 التركيبة الاسترشادية")
                for ing, pct in rough.items():
                    st.markdown(f'<div class="formula-item">▪️ '
                        f'<b>{ing}:</b> {pct:.1f}% '
                        f'({pct*10:.0f} كجم/طن)</div>',
                        unsafe_allow_html=True)
                daily = g_weight * 0.025 * g_count
                st.info(f"📊 العلف اليومي: **{daily:.1f} كجم**")

                st.markdown("### 📊 مقارنة العناصر")
                compare = []
                for k, lab in [("DP", "بروتين مهضوم DP"),
                                ("CP", "بروتين خام CP"),
                                ("SE", "طاقة SE")]:
                    t = prod_info[k.lower()]; a = actual.get(k, 0)
                    diff = a - t
                    pct = (diff / t * 100) if t else 0
                    ev = evaluate_difference(pct, standard_value=t)
                    compare.append({"العنصر": lab,
                        "المستهدف": f"{t:.1f}",
                        "المحسوب": f"{a:.1f}",
                        "التقييم": ev["label"]})
                st.dataframe(pd.DataFrame(compare),
                    use_container_width=True, hide_index=True)

                st.markdown("### 📥 تحميل التقرير")
                try:
                    guest_req = AnimalRequirement(
                        DP=prod_info["dp"], CP=prod_info["cp"],
                        SE=prod_info["se"], NDF=30, ADF=20,
                        EE=4, ASH=8, Ca=0.7, P=0.4,
                        name_ar=prod_info["name"],
                        note="تقرير استرشادي — للدقة استخدم بوابة المختص")
                    requester = (g_name.strip() if g_name.strip()
                                  else "زائر")
                    pdf_bytes = pdf_gen.generate_report(
                        formula=rough, requirement=guest_req,
                        animal_type=g_animal, breed=prod_info["name"],
                        cost=cost, city="—", local_cost=cost,
                        local_sym="USD", requester_name=requester,
                        protein_basis="CP", standard_key="",
                        include_charts=True, quality_score=quality)
                    st.download_button("📄 تحميل PDF (تقرير الزائر)",
                        pdf_bytes,
                        file_name=(f"Guest_Formula_{g_animal}_"
                            f"{datetime.now():%Y%m%d_%H%M}.pdf"),
                        mime="application/pdf",
                        use_container_width=True, type="primary")
                except Exception as e:
                    st.error(f"⚠️ خطأ في PDF: {e}")

                render_share_buttons(rough, g_animal, quality, cost,
                    key_suffix="guest_v110")
                st.warning("⚠️ تركيبة استرشادية فقط.")
        except Exception as e:
            st.error(f"⚠️ {e}")
            with st.expander("التفاصيل"):
                st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════════════
# 🧪 تبويب المختبر — لكل البوابات
# ═══════════════════════════════════════════════════════════════════════
if "🧪 مختبر التركيبات" in tab_map:
    with tab_map["🧪 مختبر التركيبات"]:
        try:
            render_lab_tab(role=role)
        except Exception as e:
            st.error(f"⚠️ {e}")
            with st.expander("التفاصيل"):
                st.code(traceback.format_exc())

# ═══════════════════════════════════════════════════════════════════════
# نهاية PART 2 — تابع
# ═══════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════
# [تكملة PART 2] — تبويب النمذجة + NLP + الزيوت + بدائل + OCR + حظائر + جدوى + مزارع + مالك
# ═══════════════════════════════════════════════════════════════════════

# 🔬 تبويب النمذجة
if "🔬 النمذجة" in tab_map:
    with tab_map["🔬 النمذجة"]:
        try:
            st.markdown('<div class="section-title">🧬 أساس البروتين</div>',
                unsafe_allow_html=True)
            pb = st.radio("الأساس:",
                ["البروتين المهضوم (DP) — الأدق",
                 "البروتين الخام (CP) — الأسهل"],
                horizontal=True, key="protein_basis_v110")
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
                    key="cattle_t_v110")
                cp_ = {}
                if "حليب" in ct:
                    cp_["milk_yield"] = st.number_input("🥛 الحليب (كجم):",
                        5.0, 60.0, 20.0, 1.0, key="cattle_m_v110")
                cp_["weight_kg"] = weight_tape_widget("أبقار",
                    "cattle_w_v110", default_weight=500.0)
                rp = get_cattle_requirements(ct, **cp_)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_cattle_v110"):
                    animal_choice = "أبقار"; production_type = ct
                    requirement = rp; std_key_global = f"أبقار_{ct}"

            with a_tabs[1]:
                st.markdown("### 🐏 الأغنام — NRC 2007")
                sg = st.radio("الجنس:", ["ذكر", "أنثى"],
                    horizontal=True, key="sheep_g_v110")
                is_m = "ذكر" in sg
                if is_m:
                    stype = st.selectbox("الحالة:",
                        ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد"],
                        key="sheep_tm_v110")
                else:
                    stype = st.selectbox("الحالة:",
                        ["مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
                        key="sheep_tf_v110")
                lit = 1
                if stype == "مرضعات":
                    lit = st.number_input("عدد المواليد:", 1, 3, 1, 1,
                        key="sheep_l_v110")
                ws = weight_tape_widget("أغنام", "sheep_w_v110", 50.0)
                rp = get_sheep_requirements(stype, is_male=is_m,
                    weight_kg=ws, litter_size=lit)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_sheep_v110"):
                    animal_choice = "أغنام"; production_type = stype
                    requirement = rp; std_key_global = f"أغنام_{stype}"

            with a_tabs[2]:
                st.markdown("### 🐐 الماعز — NRC 2007")
                gg = st.radio("الجنس:", ["ذكر", "أنثى"],
                    horizontal=True, key="goat_g_v110")
                is_m = "ذكر" in gg; mg = 0
                if is_m:
                    gtype = st.selectbox("الحالة:",
                        ["تسمين_جديان", "تيوس"], key="goat_tm_v110")
                else:
                    gtype = st.selectbox("الحالة:",
                        ["حلابة_عالي", "حلابة_متوسط", "حامل_أخير", "صيانة"],
                        key="goat_tf_v110")
                    if "حلابة" in gtype:
                        mg = st.number_input("🥛 الحليب:", 0.5, 8.0,
                            2.0, 0.25, key="goat_m_v110")
                gwt = weight_tape_widget("ماعز", "goat_w_v110", 45.0)
                rp = get_goat_requirements(gtype, is_male=is_m, milk_yield=mg)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_goat_v110"):
                    animal_choice = "ماعز"; production_type = gtype
                    requirement = rp; std_key_global = f"ماعز_{gtype}"

            with a_tabs[3]:
                st.markdown("### 🐪 الإبل — FAO 2010")
                cmt = st.selectbox("الحالة:",
                    ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
                    key="camel_t_v110")
                cm = 5.0
                if cmt == "حليب":
                    cm = st.number_input("🥛 الحليب:", 2.0, 20.0, 5.0, 0.5,
                        key="camel_m_v110")
                cwt = weight_tape_widget("إبل", "camel_w_v110", 400.0)
                rp = get_camel_requirements(cmt, weight_kg=cwt, milk_yield=cm)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_camel_v110"):
                    animal_choice = "إبل"; production_type = cmt
                    requirement = rp; std_key_global = f"إبل_{cmt}"

            with a_tabs[4]:
                st.markdown("### 🐎 الخيول — NRC 2007")
                ht = st.selectbox("الحالة:",
                    ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار",
                     "مرضعات", "صيانة"], key="horse_t_v110")
                hwt = weight_tape_widget("خيول", "horse_w_v110", 450.0)
                rp = get_horse_requirements(ht, weight_kg=hwt)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_horse_v110"):
                    animal_choice = "خيول"; production_type = ht
                    requirement = rp; std_key_global = f"خيول_{ht}"

            with a_tabs[5]:
                st.markdown("### 🐔 الدواجن")
                ps = st.radio("السلالة:", ["لاحم", "بياض"],
                    horizontal=True, key="poultry_s_v110")
                pa = st.number_input("العمر (أسبوع):", 1, 20, 1, 1,
                    key="poultry_a_v110")
                rp = get_poultry_requirements(ps, pa)
                p1, p2, p3, p4 = st.columns(4)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                p4.metric("Ca", f"{rp.Ca}%")
                if st.checkbox("✅ اعتماد", key="u_poultry_v110"):
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
                    horizontal=True, key="quail_s_v110")
                qa = st.number_input("العمر (أسبوع):", 1, 8, 1, 1,
                    key="quail_a_v110")
                rp = get_quail_requirements(qs, qa)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_quail_v110"):
                    animal_choice = "سمان"; production_type = qs
                    requirement = rp
                    std_key_global = ("سمان_بياض" if qs == "بياض"
                                      else "سمان_بادي")

            with a_tabs[7]:
                st.markdown("### 🐟 الأسماك")
                fs = st.selectbox("النوع:",
                    ["البلطي النيلي", "القرموط الأفريقي", "الكارب"],
                    key="fish_sp_v110")
                fst = st.selectbox("المرحلة:",
                    ["بادئ زريعة", "نمو", "تسمين"], key="fish_stage_v110")
                rp = get_fish_requirements(fs, fst)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_fish_v110"):
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
                    ["تسمين", "حليب", "صيانة"], key="rabbit_t_v110")
                rwt = st.number_input("⚖️ الوزن:", 1.0, 8.0, 4.0, 0.5,
                    key="rabbit_w_v110")
                rp = get_rabbit_requirements(rt, rwt)
                p1, p2, p3 = st.columns(3)
                p1.metric("DP", f"{rp.DP}%")
                p2.metric("CP", f"{rp.CP}%")
                p3.metric("SE", f"{rp.SE}")
                if st.checkbox("✅ اعتماد", key="u_rabbit_v110"):
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
                            border-radius:8px; border:1px solid #90caf9;">
                            🧬 DP: <b>{requirement.DP}%</b></span>
                        <span style="background:#fff; padding:6px 14px;
                            border-radius:8px; border:1px solid #90caf9;">
                            🧬 CP: <b>{requirement.CP}%</b></span>
                        <span style="background:#fff; padding:6px 14px;
                            border-radius:8px; border:1px solid #90caf9;">
                            🌽 SE: <b>{requirement.SE}</b></span>
                        <span style="background:#fff; padding:6px 14px;
                            border-radius:8px; border:1px solid #90caf9;">
                            ⚖️ Ca:P: <b>{ca_p_val:.2f}</b></span>
                    </div>
                </div>""", unsafe_allow_html=True)

                oil_std_info = get_oil_standard(std_key_global)
                st.info(f"🌰 الزيوت: أقصى {oil_std_info['max']}% | "
                    f"مثالي {oil_std_info['optimal']}% | "
                    f"{oil_std_info['source']}")

                requester_name = st.text_input("👤 اسم طالب العلفة:",
                    key="req_name_v110")

                st.markdown('<div class="section-title">'
                    '🌾 اختيار المكونات</div>', unsafe_allow_html=True)
                st.caption("⚠️ اختر أكبر عدد من المكونات — المحرك يستخدمها كلها")

                sq = st.text_input("🔍 بحث:", key="ing_search_v110")
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
                                    key=f"pick_{animal_choice}_{ing_name}_v110"):
                                    selected.append(ing_name)

                st.markdown("### 💰 أسعار المواد المختارة")
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
                                key=f"p_sel_{animal_choice}_{ing}_v110")
                st.success(f"✅ المختارة: **{len(selected)}** مادة")

                if st.button("🚀 تشغيل المحرك (لن يفشل)",
                        type="primary", use_container_width=True,
                        key="run_btn_v110"):
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
                                "city": "—", "local_rate": 1.0,
                                "local_sym": "USD",
                                "requester_name": requester_name,
                                "std_key_global": std_key_global,
                                "animal_type": animal_choice,
                                "production_type": production_type}
                            st.session_state["active_formula"] = result["formula"]
                            st.session_state["computed_ton_cost"] = result["cost"]
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
                            ✅ جودة الخلطة: {quality:.1f}%</h3>
                            <p style="color:#2e7d32;">
                            تجتاز 70% | Ca:P = {ca_p:.2f}</p></div>""",
                            unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div class="quality-bad-v113">
                            <h3 style="color:#c62828; margin:0;">
                            ⚠️ جودة الخلطة: {quality:.1f}%</h3></div>""",
                            unsafe_allow_html=True)

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
                        quality, cost, key_suffix="model_v110")

                    st.markdown("### 📈 الرسوم")
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
                            actual.get("Ca", 0), actual.get("P", 0),
                            custom_std.get("Ca", 0), custom_std.get("P", 0))
                        if cf: st.image(cf.getvalue(),
                            caption="⚖️ Ca:P", use_container_width=True)

                    st.markdown("### 📥 تحميل")
                    dl1, dl2 = st.columns(2)
                    with dl1:
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
                                include_charts=True,
                                quality_score=quality)
                            st.download_button("📥 PDF", pdf_bytes,
                                file_name=(f"TaworNology_"
                                    f"{ctx['animal_type']}_"
                                    f"{datetime.now():%Y%m%d_%H%M}.pdf"),
                                mime="application/pdf",
                                use_container_width=True)
                        except Exception as e:
                            st.error(f"⚠️ {e}")
                    with dl2:
                        try:
                            xl = export_comparison_to_excel(
                                custom_std, actual, ctx["requester_name"],
                                ctx["animal_type"],
                                ctx["requirement_name"],
                                formula, ctx["std_key_global"])
                            if xl:
                                st.download_button("📊 Excel", xl,
                                    file_name=(f"TaworNology_"
                                        f"{datetime.now():%Y%m%d}.xlsx"),
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True)
                        except Exception as e:
                            st.error(f"⚠️ {e}")
        except Exception as e:
            st.error(f"⚠️ {e}")
            with st.expander("التفاصيل"):
                st.code(traceback.format_exc())


# 🎯 تبويب NLP
if "🎯 NLP" in tab_map:
    with tab_map["🎯 NLP"]:
        try:
            st.markdown('<div class="section-title">'
                '🎯 التحسين غير الخطي (NLP)</div>',
                unsafe_allow_html=True)
            st.caption("🚀 محرك SLSQP — 8 مستويات + penalty")

            if not SCIPY_AVAILABLE or minimize is None:
                st.error("⚠️ SCIPY غير مثبتة")
            else:
                nc1, nc2 = st.columns(2)
                with nc1:
                    nlp_animal = st.selectbox("نوع الحيوان:",
                        ["أبقار", "أغنام", "ماعز", "إبل", "خيول",
                         "دواجن", "سمان", "أسماك", "أرانب"],
                        key="nlp_animal_v110")
                with nc2:
                    prod_options = {
                        "أبقار": ["حليب_عالي", "حليب_متوسط",
                            "حليب_منخفض", "تسمين_مكثف", "تسمين_عادي",
                            "حمل_أخير", "صيانة"],
                        "أغنام": ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد",
                            "مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
                        "ماعز": ["تسمين_جديان", "تيوس", "حلابة_عالي",
                            "حلابة_متوسط", "حامل_أخير", "صيانة"],
                        "إبل": ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
                        "خيول": ["رياضة_مكثف", "رياضة_عادي",
                            "نمو_أمهار", "مرضعات", "صيانة"],
                        "دواجن": ["لاحم", "بياض"],
                        "سمان": ["تسمين", "بياض"],
                        "أسماك": ["بادئ زريعة", "نمو", "تسمين"],
                        "أرانب": ["تسمين", "حليب", "صيانة"]}.get(
                            nlp_animal, ["عام"])
                    nlp_prod = st.selectbox("الحالة:", prod_options,
                        key="nlp_prod_v110")

                nlp_req = _get_requirement_for_nlp(nlp_animal, nlp_prod)
                m1, m2 = st.columns(2)
                m1.metric("🎯 ME", f"{nlp_req['ME']:.0f} kcal/kg")
                m2.metric("🎯 CP", f"{nlp_req['CP']:.2f}%")

                active = st.session_state.get("active_formula", {})
                all_ings = list(_get_ingredient_lookup().keys())
                nlp_sel = st.multiselect("المكونات (2–10):",
                    options=all_ings,
                    default=list(active.keys())[:5] if active else [],
                    max_selections=10, key="nlp_sel_v110")

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
                                step=10.0, key=f"nlp_p_{ing}_v110")
                    price_product = st.number_input(
                        "💵 سعر بيع المنتج ($/وحدة):",
                        0.5, 100.0, 2.5, 0.1, key="nlp_pp_v110")

                    if st.button("🚀 تشغيل NLP", type="primary",
                            use_container_width=True, key="nlp_run_v110"):
                        with st.spinner("⏳ جاري التحسين..."):
                            result = nlp_optimize_feed(nlp_sel, ing_data,
                                nlp_prices, animal_type=nlp_animal,
                                production_type=nlp_prod,
                                price_product=price_product)
                        if result["success"]:
                            if result.get("warning"):
                                st.warning(result["warning"])
                            st.success(
                                f"✅ ربح: ${result['max_profit']:.4f} | "
                                f"استراتيجية: {result['strategy']}")
                            m1, m2, m3, m4 = st.columns(4)
                            m1.metric("💰 التكلفة",
                                f"${result['final_cost']:.4f}")
                            m2.metric("⚡ ME",
                                f"{result['final_me']:.0f}")
                            m3.metric("🧬 CP",
                                f"{result['final_cp']:.2f}%")
                            m4.metric("📈 الربح",
                                f"${result['max_profit']:.4f}")
                            for ing, pct in result["formula"].items():
                                st.markdown(f'<div class="formula-item">'
                                    f'▪️ <b>{ing}:</b> {pct:.2f}%</div>',
                                    unsafe_allow_html=True)
                            fig_curve = create_nlp_profit_curve(
                                result, nlp_sel, ing_data, nlp_prices)
                            if fig_curve:
                                st.plotly_chart(fig_curve,
                                    use_container_width=True)
                        else:
                            st.error(f"❌ {result['message']}")
                            diag = result.get("diagnosis", {})
                            if diag:
                                for issue in diag.get("issues", []):
                                    st.markdown(f"- {issue}")
                                st.info("💡 " + " | ".join(
                                    diag.get("tips", [])))
                else:
                    st.info("💡 اختر مكونين على الأقل")
        except Exception as e:
            st.error(f"⚠️ {e}")


# 🌰 الزيوت
if "🌰 الزيوت" in tab_map:
    with tab_map["🌰 الزيوت"]:
        try:
            st.markdown('<div class="section-title">'
                '🌰 مكتبة الزيوت</div>', unsafe_allow_html=True)
            oil_rows = [{"الحيوان": k, "أقصى %": f"{v['max']}%",
                "مثالي %": f"{v['optimal']}%", "المرجع": v["source"]}
                for k, v in MAX_OIL_PERCENTAGE.items()]
            st.dataframe(pd.DataFrame(oil_rows),
                use_container_width=True, hide_index=True)
            oils = get_oil_ingredients()
            for ing_name, ing_data in oils.items():
                with st.expander(f"🌰 {ing_name}"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("SE", f"{ing_data.get('SE', 0):.0f}")
                    c2.metric("kcal/kg",
                        f"{ing_data.get('SE', 0) * 41:.0f}")
                    c3.metric("السعر",
                        f"${ing_data.get('price', 0):.0f}")
                    st.info(f"📝 {ing_data.get('desc', '')}")
        except Exception as e:
            st.error(f"⚠️ {e}")


# 🍼 بدائل الحليب
if "🍼 بدائل الحليب" in tab_map:
    with tab_map["🍼 بدائل الحليب"]:
        try:
            st.markdown('<div class="section-title">'
                '🍼 بدائل الحليب</div>', unsafe_allow_html=True)
            mr1, mr2 = st.columns(2)
            with mr1:
                mr_a = st.selectbox("الحيوان:",
                    list(MILK_REPLACER_STANDARDS.keys()),
                    key="mr_a_v110")
                mr_v = st.number_input("الكمية (كجم):",
                    1.0, 10000.0, 100.0, 10.0, key="mr_v_v110")
            with mr2:
                std_mr = MILK_REPLACER_STANDARDS[mr_a]
                st.markdown(f"""<div style="background:linear-gradient(
                    135deg,#f1f8e9,#e8f5e9); padding:20px;
                    border-radius:16px; border-right:5px solid #2e7d32;">
                    <b>📊 {mr_a}:</b><br>
                    بروتين: {std_mr['CP']}% | دهن: {std_mr['Fat']}% |
                    لاكتوز: {std_mr['Lactose']}%<br>
                    Ca: {std_mr['Ca']}% | P: {std_mr['P']}%
                </div>""", unsafe_allow_html=True)

            mr_sel = []
            cols = st.columns(3)
            for i, (name, data) in enumerate(
                    MILK_REPLACER_INGREDIENTS.items()):
                with cols[i % 3]:
                    with st.expander(f"{name}"):
                        st.caption(
                            f"💵 ${data['price']}/كجم | حد: {data['max']}%")
                        if st.checkbox("إضافة",
                                key=f"mr_{name}_v110"):
                            mr_sel.append(name)

            if st.button("🧪 تركيب", type="primary",
                    use_container_width=True, key="mr_run_v110"):
                if len(mr_sel) < 3:
                    st.warning("⚠️ اختر 3 مكونات على الأقل")
                else:
                    with st.spinner("⏳ جاري التركيب..."):
                        r = formulate_milk_replacer(mr_a, mr_v, mr_sel)
                    if r["success"]:
                        quality = r.get("quality_score", 0)
                        meets70 = quality >= 70
                        bg = ("quality-good-v113" if meets70
                              else "quality-bad-v113")
                        st.markdown(f"""<div class="{bg}">
                            <h3 style="color:{'#1b5e20' if meets70 else '#c62828'};
                                margin:0;">جودة: {quality:.1f}%</h3>
                            <p>استراتيجية: {r.get('strategy', '—')} |
                            استخدام: {r.get('used_pct', 0):.0f}% |
                            Ca:P = {r['ca_p_ratio']:.2f}</p>
                        </div>""", unsafe_allow_html=True)
                        if r.get("warning"):
                            st.warning(r["warning"])
                        for ing, pct in r["formula"].items():
                            kg = pct * mr_v / 100.0
                            st.markdown(f'<div class="formula-item">'
                                f'▪️ <b>{ing}:</b> {pct:.2f}% '
                                f'({kg:.2f} كجم)</div>',
                                unsafe_allow_html=True)
                        st.metric("💰 تكلفة 100 كجم",
                            f"${r['cost_per_100kg']:.2f}")
                        pdf_mr = generate_milk_replacer_pdf(r)
                        if pdf_mr:
                            st.download_button("📄 PDF", pdf_mr,
                                file_name=(f"Milk_{mr_a.split()[0]}_"
                                    f"{datetime.now():%Y%m%d}.pdf"),
                                mime="application/pdf",
                                use_container_width=True, type="primary")
                    else:
                        st.error(f"❌ {r['message']}")
        except Exception as e:
            st.error(f"⚠️ {e}")


# 📷 OCR
if "📷 OCR" in tab_map:
    with tab_map["📷 OCR"]:
        try:
            st.markdown('<div class="section-title">'
                '📷 المختبر الذكي OCR</div>', unsafe_allow_html=True)
            if not OCR_AVAILABLE:
                st.error("⚠️ pytesseract غير مثبتة")
            else:
                up = st.file_uploader("ارفع الصورة:",
                    type=["jpg", "jpeg", "png"], key="ocr_upload_v110")
                if up:
                    uploaded = up.read()
                    st.image(uploaded, caption="الصورة",
                        use_container_width=True)
                    if st.button("🔍 تحليل", type="primary",
                            use_container_width=True,
                            key="ocr_run_v110"):
                        with st.spinner("🔬 جاري التحليل..."):
                            result = extract_ingredients_from_image(
                                uploaded)
                        if result["success"] and result["count"] > 0:
                            st.success(f"✅ {result['count']} مادة")
                            nut = compute_formula_nutrients(
                                result["ingredients"])
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
                                        st.session_state[
                                            "last_ocr_result"] = corrected
                                        st.session_state[
                                            "last_ocr_nutrients"] = \
                                            compute_formula_nutrients(corrected)
                                        st.success("✅"); st.rerun()
                        else:
                            st.warning(
                                f"⚠️ {result.get('message', '')}")
        except Exception as e:
            st.error(f"⚠️ {e}")


# 🏗️ الحظائر 3D
if "🏗️ الحظائر 3D" in tab_map:
    with tab_map["🏗️ الحظائر 3D"]:
        try:
            st.markdown('<div class="section-title">'
                '🏗️ مصمم الحظائر 3D — v11.9</div>',
                unsafe_allow_html=True)
            st.caption("🌀 مراوح + ❄️ ألواح تبريد + 🏗️ هياكل + 💰 تكاليف")

            c1, c2, c3 = st.columns(3)
            with c1:
                barn_a = st.selectbox("🐾 الحيوان:",
                    list(BARN_DESIGN_STANDARDS.keys()),
                    format_func=lambda k:
                        BARN_DESIGN_STANDARDS[k]["name_ar"],
                    key="barn_animal_v110")
            with c2:
                barn_c = st.number_input("🔢 العدد:", 1, 100000, 1000, 50,
                    key="barn_count_v110")
            with c3:
                barn_s = st.selectbox("🏠 النظام:",
                    ["أرضي مفتوح", "بطاريات"], key="barn_system_v110")

            dims = calculate_barn_dimensions(barn_a, barn_c, barn_s)

            if dims:
                st.markdown("### 📐 الأبعاد والمساحة")
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("📏 المساحة", f"{dims['total_area_m2']} م²")
                k2.metric("📐 الأبعاد",
                    f"{dims['length_m']}×{dims['width_m']} م")
                k3.metric("🏔️ القمة", f"{dims['ridge_height_m']} م")
                k4.metric("📦 الحجم", f"{dims['volume_m3']} م³")

                st.markdown("### 🌀 التهوية والمراوح")
                v1, v2, v3, v4 = st.columns(4)
                v1.metric("💨 تدفق الصيف",
                    f"{dims['vent_flow_summer_m3h']:,} م³/س")
                v2.metric("🌀 مراوح النفق",
                    f"{dims['tunnel_fans_count']} مروحة")
                v3.metric("🌀 مراوح جانبية",
                    f"{dims['side_fans_count']} مروحة")
                v4.metric("❄️ ألواح تبريد",
                    f"{dims['cooling_pad_area_m2']} م²"
                    if dims.get("cooling_pad_enabled") else "—")

                v5, v6, v7, v8 = st.columns(4)
                total_hp = (dims['tunnel_fans_hp_total'] +
                            dims['side_fans_hp_total'])
                v5.metric("⚡ إجمالي HP", f"{total_hp} HP")
                v6.metric("📏 مراوح نفق", dims['tunnel_fan_spec'])
                v7.metric("📏 مراوح جانبية", dims['side_fan_spec'])
                v8.metric("🪟 فتحات",
                    f"{dims['vent_open_area_m2']} م²")

                st.markdown("### 🏗️ الهيكل والإنشاء")
                s1, s2, s3, s4 = st.columns(4)
                s1.metric("🏗️ الهيكل",
                    dims['structure_type'].split('(')[0])
                s2.metric("⚖️ وزن الحديد",
                    f"{dims['steel_weight_kg']:,} كجم")
                s3.metric("🧊 العزل",
                    f"{dims['insulation_area_m2']} م²")
                s4.metric("📏 سماكة",
                    f"{dims['insulation_thickness_mm']} مم")

                st.markdown("### 💡 الإضاءة والمياه")
                l1, l2, l3, l4 = st.columns(4)
                l1.metric("💡 لوكس", dims['lighting_lux'])
                l2.metric("⏰ ساعات", dims['light_hours'])
                l3.metric("💧 ماء/يوم",
                    f"{dims['water_per_day_L']:,.0f} لتر")
                l4.metric("🔧 وحدات إضاءة", dims['light_fixtures'])

                st.markdown("### 🍽️ المعالف والسقايات")
                f1, f2, f3, f4 = st.columns(4)
                f1.metric("🍽️ معالف",
                    f"{dims['feeders_count']} × {dims['feeder_type']}")
                f2.metric("📏 طول المعالف",
                    f"{dims['total_feeder_length_m']} م")
                f3.metric("💧 سقايات",
                    f"{dims['drinkers_count']} × {dims['drinker_type']}")
                f4.metric("📏 طول السقايات",
                    f"{dims['total_drinker_length_m']} م")

                st.markdown("### 🏗️ المجسم 3D")
                fig3d = create_barn_3d_figure(dims)
                if fig3d:
                    st.plotly_chart(fig3d, use_container_width=True)

                st.markdown("### 🎬 فيديو GIF")
                if st.button("🎬 توليد الفيديو", type="primary",
                        use_container_width=True, key="barn_gif_v110"):
                    with st.spinner("🎥 جاري التوليد..."):
                        vb = create_barn_animation_gif(dims, frames=20,
                            fps=8)
                    if vb:
                        st.session_state["barn_video_gif"] = vb.getvalue()
                        st.success("✅ تم!")
                    else:
                        st.error("⚠️ تعذر التوليد")

                if st.session_state.get("barn_video_gif"):
                    st.image(st.session_state["barn_video_gif"],
                        use_container_width=True)
                    st.download_button("⬇️ تحميل GIF",
                        st.session_state["barn_video_gif"],
                        file_name=f"barn_{barn_a}.gif",
                        mime="image/gif", use_container_width=True)

                st.markdown("### 💰 التكاليف التقديرية")
                cost_data = {
                    "الهيكل المعدني": dims['cost_structure_usd'],
                    "السقف": dims['cost_roof_usd'],
                    "الجدران": dims['cost_walls_usd'],
                    "الأرضية": dims['cost_floor_usd'],
                    "مراوح النفق": dims['cost_fans_tunnel_usd'],
                    "مراوح جانبية": dims['cost_fans_side_usd'],
                    "ألواح التبريد": dims['cost_cooling_pad_usd'],
                    "الإضاءة": dims['cost_lighting_usd'],
                    "المعالف": dims['cost_feeders_usd'],
                    "السقايات": dims['cost_drinkers_usd']}
                cost_df = pd.DataFrame([
                    {"البند": k, "التكلفة ($)": f"${v:,.0f}"}
                    for k, v in cost_data.items()])
                st.dataframe(cost_df, use_container_width=True,
                    hide_index=True)
                st.metric("💰 إجمالي التكلفة",
                    f"${dims['cost_total_usd']:,.0f}")

                try:
                    pdf_b = generate_barn_pdf_report(dims)
                    st.download_button("📄 تحميل PDF شامل", pdf_b,
                        file_name=(f"Barn_{barn_a}_"
                            f"{datetime.now():%Y%m%d}.pdf"),
                        mime="application/pdf",
                        use_container_width=True, type="primary")
                except Exception as e:
                    st.error(f"⚠️ PDF: {e}")
        except Exception as e:
            st.error(f"⚠️ {e}")
            with st.expander("التفاصيل"):
                st.code(traceback.format_exc())


# 📊 الجدوى
if "📊 الجدوى" in tab_map:
    with tab_map["📊 الجدوى"]:
        try:
            st.markdown('<div class="section-title">'
                '📊 دراسة الجدوى</div>', unsafe_allow_html=True)
            mode = st.radio("🎯 النوع:",
                ["🔬 فنية", "💰 اقتصادية", "📈 شاملة (+ Monte Carlo)"],
                horizontal=True, key="feas_mode_v110")
            f1, f2 = st.columns(2)
            with f1:
                feas_k = st.selectbox("نوع الحيوان:",
                    list(BARN_DESIGN_STANDARDS.keys()),
                    format_func=lambda k:
                        BARN_DESIGN_STANDARDS[k]["name_ar"],
                    key="feas_animal_v110")
                feas_c = st.number_input("العدد:", 1, 100000, 1000, 50,
                    key="feas_count_v110")
            with f2:
                if "اقتصادية" in mode or "شاملة" in mode:
                    fp = st.number_input("💵 سعر العلف ($/طن):",
                        50.0, 5000.0, 350.0, 10.0, key="feas_fp_v110")
                    pp = st.number_input("💵 سعر المنتج ($/وحدة):",
                        0.1, 10000.0, 2.5, 0.1, key="feas_pp_v110")
                    lc = st.number_input("👷 تكلفة العامل ($/شهر):",
                        0.0, 10000.0, 200.0, 10.0, key="feas_lc_v110")

            feas = calculate_technical_feasibility(feas_k, feas_c)
            if feas:
                d = feas["dims"]
                st.markdown("### 🔬 الجدوى الفنية")
                fc1, fc2, fc3, fc4 = st.columns(4)
                fc1.metric("📏 المساحة", f"{d['total_area_m2']} م²")
                fc2.metric("📐 الأبعاد",
                    f"{d['length_m']}×{d['width_m']} م")
                fc3.metric("📦 الحجم", f"{d['volume_m3']} م³")
                fc4.metric("👷 عمال", feas["labor"]["workers"])
                f1_, f2_, f3_, f4_ = st.columns(4)
                f1_.metric("علف/يوم",
                    f"{feas['feed']['total_day_kg']:.1f} كجم")
                f2_.metric("علف/سنة",
                    f"{feas['feed']['total_year_ton']:.2f} طن")
                f3_.metric("ماء/يوم",
                    f"{feas['water']['total_day_L']:.0f} لتر")
                f4_.metric("ماء/سنة",
                    f"{feas['water']['total_year_m3']:.1f} م³")

                if "اقتصادية" in mode or "شاملة" in mode:
                    st.markdown("### 💰 الجدوى الاقتصادية")
                    feed_yr_ton = feas["feed"]["total_year_ton"]
                    feed_cost = feed_yr_ton * fp
                    labor_yr = feas["labor"]["workers"] * lc * 12
                    total_cost = feed_cost + labor_yr
                    prod = feas["production"]
                    ann_units = prod.get("annual", 0)
                    annual_rev = ann_units * pp
                    profit = annual_rev - total_cost
                    roi = ((profit / total_cost * 100)
                           if total_cost > 0 else 0)
                    e1, e2, e3, e4 = st.columns(4)
                    e1.metric("💵 تكلفة سنوية", f"${total_cost:,.0f}")
                    e2.metric("💰 إيراد سنوي", f"${annual_rev:,.0f}")
                    e3.metric("📈 ربح سنوي", f"${profit:,.0f}",
                        delta=f"{roi:+.1f}% ROI")
                    e4.metric("🎯 التعادل",
                        f"{(total_cost / pp if pp > 0 else 0):,.0f} وحدة")
                    if profit > 0:
                        st.success(
                            f"✅ مجدٍ — ربح ${profit:,.0f}/سنة "
                            f"(ROI {roi:.1f}%)")
                    else:
                        st.error(
                            f"❌ غير مجدٍ — يحتاج ${abs(profit):,.0f}")

                if "شاملة" in mode and annual_rev > 0:
                    st.markdown("### 🎲 Monte Carlo (1000 سيناريو)")
                    random.seed(42)
                    sims = []
                    for _ in range(1000):
                        rf = random.gauss(1.0, 0.15)
                        cf = random.gauss(1.0, 0.10)
                        pf = random.gauss(1.0, 0.12)
                        sr = annual_rev * rf * pf
                        sc = total_cost * cf
                        sims.append({"rev": sr, "cost": sc,
                                     "profit": sr - sc})
                    profits = np.array([s["profit"] for s in sims])
                    p5 = np.percentile(profits, 5)
                    p50 = np.percentile(profits, 50)
                    p95 = np.percentile(profits, 95)
                    prob = (profits > 0).mean() * 100
                    mc1, mc2, mc3, mc4 = st.columns(4)
                    mc1.metric("احتمال الربح", f"{prob:.1f}%")
                    mc2.metric("P5 (سيئ)", f"${p5:,.0f}")
                    mc3.metric("متوسط", f"${p50:,.0f}")
                    mc4.metric("P95 (ممتاز)", f"${p95:,.0f}")
                    if MATPLOTLIB_AVAILABLE:
                        fig, ax = plt.subplots(figsize=(10, 4))
                        ax.hist(profits, bins=50, color='#43a047',
                            edgecolor='#1b5e20', alpha=0.7)
                        ax.axvline(0, color='#c62828', linestyle='--',
                            linewidth=2, label='التعادل')
                        ax.axvline(p50, color='#1976d2', linewidth=2,
                            label=f'الوسيط ${p50:,.0f}')
                        ax.set_xlabel('الربح ($)', fontweight='bold')
                        ax.set_ylabel('التكرار', fontweight='bold')
                        ax.set_title('توزيع الأرباح', fontsize=13,
                            fontweight='bold', color='#1b5e20')
                        ax.legend(); ax.grid(axis='y', alpha=0.3)
                        buf = io.BytesIO()
                        plt.savefig(buf, format='png', dpi=120,
                            bbox_inches='tight', facecolor='white')
                        plt.close(); buf.seek(0)
                        st.image(buf.getvalue(),
                            use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ {e}")


# 🐔 المزارع
BROILER_STANDARDS = {7: (0.18, 1.05), 14: (0.47, 1.20),
    21: (0.94, 1.35), 28: (1.50, 1.50), 35: (2.10, 1.62),
    42: (2.70, 1.72)}

if "🐔 المزارع" in tab_map:
    with tab_map["🐔 المزارع"]:
        try:
            st.markdown('<div class="section-title">'
                '🐔 إدارة المزارع</div>', unsafe_allow_html=True)
            farms = st.session_state["broiler_farms"]
            with st.form("new_farm_v110", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    nf_name = st.text_input("اسم المزرعة *",
                        key="nf_n_v110")
                    nf_strain = st.selectbox("السلالة",
                        ["Ross 308", "Cobb 500", "Hubbard", "Avian"],
                        key="nf_s_v110")
                with c2:
                    nf_birds = st.number_input("عدد الطيور",
                        100, 100000, 1000, 50, key="nf_b_v110")
                    nf_date = st.date_input("تاريخ الإدخال",
                        key="nf_d_v110")
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
                sel = st.selectbox("اختر مزرعة:",
                    list(farms.keys()), key="farm_sel_v110")
                farm = farms[sel]
                with st.form(f"rec_{sel}_v110"):
                    st.markdown(f"### 📝 {farm['strain']} — قراءة يومية")
                    rc = st.columns(4)
                    with rc[0]:
                        age = st.number_input("العمر", 1, 60, 1,
                            key="r_age_v110")
                    with rc[1]:
                        alive = st.number_input("حي", 1,
                            farm["start_birds"],
                            value=farm["start_birds"],
                            key="r_alive_v110")
                    with rc[2]:
                        wt = st.number_input("وزن (كجم)",
                            0.01, 5.0, 0.045, 0.005, key="r_wt_v110")
                    with rc[3]:
                        feed = st.number_input("علف (كجم)",
                            0.0, 20.0, 0.0, 0.05, key="r_feed_v110")
                    if st.form_submit_button("➕ تسجيل",
                            type="primary", use_container_width=True):
                        farm["records"].append({
                            "date": str(datetime.now().date()),
                            "age": age, "alive": alive,
                            "wt": wt, "feed": feed})
                        st.success("✅"); st.rerun()
                if farm["records"]:
                    latest = farm["records"][-1]
                    liv = (latest["alive"] / farm["start_birds"] * 100)
                    fcr = (latest["feed"] / (latest["wt"] - 0.045)
                        if latest["wt"] > 0.045 else 0)
                    adg = ((latest["wt"] - 0.045) * 1000 / latest["age"]
                        if latest["age"] > 0 else 0)
                    epef = ((liv * latest["wt"])
                        / (latest["age"] * fcr) * 100
                        if fcr > 0 and latest["age"] > 0 else 0)
                    m = st.columns(5)
                    m[0].metric("🐦 حيوية", f"{liv:.1f}%")
                    m[1].metric("📈 ADG", f"{adg:.1f} g/d")
                    m[2].metric("⚖️ الوزن", f"{latest['wt']:.3f} كجم")
                    m[3].metric("🍽️ FCR", f"{fcr:.2f}")
                    m[4].metric("🏆 EPEF", f"{epef:.0f}")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ تبويبات المالك ═══
if role == "owner":
    if "🏭 المستودعات" in tab_map:
        with tab_map["🏭 المستودعات"]:
            try:
                st.markdown('<div class="section-title">'
                    '🏭 المستودعات</div>', unsafe_allow_html=True)
                inv = st.session_state["inventory"]
                for k, v in list(inv.items()):
                    if not isinstance(v, dict):
                        inv[k] = {"quantity": float(v),
                            "min_threshold": 5.0, "unit": "طن"}
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
                edited = st.data_editor(inv_df,
                    use_container_width=True, hide_index=True,
                    column_config={
                        "المادة": st.column_config.TextColumn(
                            disabled=True),
                        "الكمية (طن)": st.column_config.NumberColumn(
                            min_value=0.0, step=1.0),
                        "الحد الأدنى": st.column_config.NumberColumn(
                            min_value=0.0, step=1.0)},
                    key="inv_editor_v110")
                if st.button("💾 حفظ", type="primary",
                        use_container_width=True):
                    for _, r in edited.iterrows():
                        name = r["المادة"]
                        inv[name]["quantity"] = float(r["الكمية (طن)"])
                        inv[name]["min_threshold"] = float(
                            r["الحد الأدنى"])
                    st.success("✅"); st.rerun()
            except Exception as e:
                st.error(f"⚠️ {e}")

    if "🧾 الفواتير" in tab_map:
        with tab_map["🧾 الفواتير"]:
            try:
                st.markdown('<div class="section-title">'
                    '🧾 الفواتير</div>', unsafe_allow_html=True)
                st.info("💡 نظام فواتير كامل متوفر في النسخة الموسعة.")
            except Exception as e:
                st.error(f"⚠️ {e}")

    if "🖨️ الديباجة" in tab_map:
        with tab_map["🖨️ الديباجة"]:
            try:
                st.markdown('<div class="section-title">'
                    '🖨️ الديباجة</div>', unsafe_allow_html=True)
                st.markdown(f"""<div style="border:3px solid #1b5e20;
                    padding:50px 30px; border-radius:15px;
                    background:linear-gradient(135deg,#f1f8e9,#e8f5e9);
                    direction:rtl; text-align:center;">
                    <h1 style="color:#1b5e20; margin:0;">{APP_NAME}</h1>
                    <h3 style="color:#1565C0;">{APP_TAGLINE}</h3>
                    <h2 style="color:#c62828;">{SUPERVISOR}</h2>
                    <p style="color:#0d47a1;">{SUPERVISOR_TITLE}</p>
                    <p>📅 {datetime.now():%Y-%m-%d}</p>
                    <p style="color:#c62828;">🤲 {DUA_SHORT} 🤲</p>
                </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"⚠️ {e}")

    if "📈 التحليلات" in tab_map:
        with tab_map["📈 التحليلات"]:
            try:
                st.markdown('<div class="section-title">'
                    '📈 التحليلات</div>', unsafe_allow_html=True)
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

    if "💬 التعليقات" in tab_map:
        with tab_map["💬 التعليقات"]:
            try:
                st.markdown('<div class="section-title">'
                    '💬 التعليقات</div>', unsafe_allow_html=True)
                if not st.session_state.get("comments_list"):
                    raw = (SharedStorage.get("shared_comments")
                        or st.session_state.get(
                            "shared_comments", ""))
                    st.session_state["comments_list"] = [
                        ln.strip() for ln in raw.split("\n")
                        if ln.strip()]
                comments = st.session_state["comments_list"]
                for c in comments:
                    st.markdown(f'<div style="background:#f1f8e9; '
                        f'padding:12px; border-radius:10px; '
                        f'margin-bottom:8px; '
                        f'border-right:4px solid #2e7d32;">{c}</div>',
                        unsafe_allow_html=True)
                nc = st.text_area("➕ تعليق جديد:",
                    key="cm_new_v110")
                if st.button("📤 نشر", type="primary",
                        use_container_width=True):
                    if nc.strip():
                        comments.append(
                            f"• [{datetime.now():%Y-%m-%d %H:%M}]: "
                            f"{nc.strip()}")
                        SharedStorage._save(
                            {"shared_comments": "\n".join(comments)})
                        st.session_state["comments_list"] = comments
                        st.success("✅"); st.rerun()
            except Exception as e:
                st.error(f"⚠️ {e}")

# ═══════════════════════════════════════════════════════════════════════
# نهاية PART 3 — تابع
# ═══════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════
# [تكملة PART 3] — غرفة التواصل + الاستديو + المراجع + المساعدة + الدليل
# ═══════════════════════════════════════════════════════════════════════

# 💬 غرفة التواصل
if "💬 غرفة التواصل" in tab_map:
    with tab_map["💬 غرفة التواصل"]:
        try:
            st.markdown('<div class="section-title">'
                '💬 غرفة التواصل والنقاش</div>',
                unsafe_allow_html=True)
            st.caption("🔒 نقاش علمي — مع إمكانية مشاركة العلفة والنتائج")

            rooms = _load_chat_rooms()
            for dr in ["🌾 النقاش العام", "🧬 نقاش علمي",
                        "💰 نقاش اقتصادي"]:
                if dr not in rooms: rooms[dr] = []
            _save_chat_rooms(rooms)

            c1, c2, c3 = st.columns([0.5, 0.25, 0.25])
            with c1:
                current_room = st.selectbox("🏠 الغرفة:",
                    list(rooms.keys()), key="comm_room_v110")
            with c2:
                if role in ("owner", "specialist"):
                    if st.button("➕ غرفة جديدة",
                            use_container_width=True, key="comm_new_v110"):
                        st.session_state["show_new_room"] = True
            with c3:
                if role == "owner" and st.button("🗑️ حذف",
                        use_container_width=True, key="comm_del_v110"):
                    if current_room in rooms and len(rooms) > 1:
                        del rooms[current_room]
                        _save_chat_rooms(rooms); st.rerun()

            if st.session_state.get("show_new_room"):
                nr = st.text_input("اسم الغرفة:",
                    key="comm_nr_name_v110")
                if st.button("إنشاء", key="comm_nr_btn_v110") and nr:
                    if create_chat_room(nr):
                        st.session_state["show_new_room"] = False
                        st.rerun()

            username = _safe_username()
            st.caption(f"👤 {username} | 🏠 {current_room} | "
                f"عدد: {len(rooms.get(current_room, []))}")

            msgs = rooms.get(current_room, [])[-80:]
            chat_html = ('<div style="background:#fafafa; padding:15px; '
                'border-radius:14px; height:450px; overflow-y:auto; '
                'border:1px solid #e0e0e0; direction:rtl;">')
            if not msgs:
                chat_html += ('<p style="text-align:center;color:#999;">'
                              'لا رسائل 👋</p>')
            for m in msgs:
                is_mine = (m["user"] == username)
                role_icon = {"owner": "👑", "specialist": "🔬",
                    "guest": "👥"}.get(m.get("role", "guest"), "")
                bg = "#dcedc8" if is_mine else "#e3f2fd"
                nc = "#1b5e20" if is_mine else "#1565c0"
                chat_html += (f'<div style="background:{bg}; '
                    f'padding:8px 14px; border-radius:10px; '
                    f'margin-bottom:6px; '
                    f'border-right:3px solid {nc};">'
                    f'<b style="color:{nc};">{role_icon} {m["user"]}</b> '
                    f'<small style="color:#888;">{m["ts"]}</small><br>'
                    f'<span style="white-space:pre-wrap;">{m["msg"]}'
                    f'</span></div>')
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)

            with st.form(f"comm_form_{current_room}_v110",
                    clear_on_submit=True):
                msg_text = st.text_area("✍️ رسالتك:", height=80,
                    key=f"comm_msg_{current_room}_v110")
                cc1, cc2 = st.columns([0.75, 0.25])
                with cc1:
                    share_formula = st.checkbox("📎 إرفاق التركيبة",
                        value=False, key="comm_attach_v110")
                with cc2:
                    send = st.form_submit_button("📤 إرسال",
                        type="primary", use_container_width=True)
                if send:
                    if not check_rate_limit("comm", max_calls=30,
                            window=60):
                        st.warning("⏳ تهدئة")
                    else:
                        final_msg = msg_text
                        if share_formula:
                            active = st.session_state.get(
                                "active_formula", {})
                            if active:
                                fs = " | ".join(f"{k}: {v:.1f}%"
                                    for k, v in active.items())
                                final_msg += f"\n\n📋 التركيبة:\n{fs}"
                        if add_chat_message(current_room, username,
                                final_msg):
                            st.rerun()

            if st.button("🔄 تحديث", key="comm_refresh_v110"):
                st.rerun()
        except Exception as e:
            st.error(f"⚠️ {e}")


# 🎬 الاستديو
if "🎬 الاستديو" in tab_map:
    with tab_map["🎬 الاستديو"]:
        try:
            st.markdown('<div class="section-title">'
                '🎬 الاستديو التعليمي</div>', unsafe_allow_html=True)
            studio = _load_studio()
            sub_s1, sub_s2, sub_s3 = st.tabs(
                ["📹 فيديوهات", "📊 شرائح", "📝 ملاحظات"])
            with sub_s1:
                with st.form("sv_v110"):
                    vt = st.text_input("العنوان:", key="vid_t_v110")
                    vu = st.text_input("رابط:", key="vid_u_v110")
                    vd = st.text_area("الوصف:", key="vid_d_v110")
                    if st.form_submit_button("➕ إضافة",
                            type="primary"):
                        if vt and vu:
                            studio["videos"].append({
                                "title": _sanitize_message(vt, 100),
                                "url": _sanitize_message(vu, 500),
                                "desc": _sanitize_message(vd, 500),
                                "ts": datetime.now().strftime(
                                    "%Y-%m-%d %H:%M")})
                            _save_studio(studio); st.rerun()
                for i, v in enumerate(studio["videos"]):
                    with st.expander(f"🎬 {v['title']} — {v['ts']}"):
                        st.markdown(f"🔗 [فتح]({v['url']})")
                        if v.get("desc"): st.caption(v["desc"])
                        if st.button("🗑️", key=f"del_vid_{i}_v110"):
                            studio["videos"].pop(i)
                            _save_studio(studio); st.rerun()
            with sub_s2:
                with st.form("ss_v110"):
                    st_title = st.text_input("العنوان:",
                        key="sl_t_v110")
                    s_url = st.text_input("رابط الصورة:",
                        key="sl_u_v110")
                    if st.form_submit_button("➕ إضافة",
                            type="primary"):
                        if st_title and s_url:
                            studio["slides"].append({
                                "title": _sanitize_message(st_title, 100),
                                "url": _sanitize_message(s_url, 500),
                                "ts": datetime.now().strftime(
                                    "%Y-%m-%d %H:%M")})
                            _save_studio(studio); st.rerun()
                for i, s in enumerate(studio["slides"]):
                    st.markdown(f"**{s['title']}**")
                    try: st.image(s["url"], use_container_width=True)
                    except Exception: st.caption(f"🔗 {s['url']}")
                    if st.button("🗑️", key=f"del_sl_{i}_v110"):
                        studio["slides"].pop(i)
                        _save_studio(studio); st.rerun()
            with sub_s3:
                with st.form("sn_v110"):
                    nt = st.text_area("ملاحظة:", key="note_t_v110")
                    if st.form_submit_button("➕ حفظ",
                            type="primary"):
                        if nt.strip():
                            studio["notes"].append({
                                "text": _sanitize_message(nt, 1000),
                                "ts": datetime.now().strftime(
                                    "%Y-%m-%d %H:%M"),
                                "author": _safe_username()})
                            _save_studio(studio); st.rerun()
                for i, n in enumerate(reversed(studio["notes"])):
                    ri = len(studio["notes"]) - 1 - i
                    st.markdown(f'<div class="formula-item">'
                        f'<b>{n["author"]}</b> — '
                        f'<small>{n["ts"]}</small><br>'
                        f'{n["text"]}</div>', unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_note_{ri}_v110"):
                        studio["notes"].pop(ri)
                        _save_studio(studio); st.rerun()
        except Exception as e:
            st.error(f"⚠️ {e}")


# 📚 المراجع
if "📚 المراجع" in tab_map:
    with tab_map["📚 المراجع"]:
        try:
            st.markdown('<div class="section-title">'
                '📚 المراجع العلمية</div>', unsafe_allow_html=True)

            st.markdown("### 🎯 مراجع حسب الحالة")
            ref_animal = st.selectbox("اختر الحيوان:",
                ["أبقار", "أغنام", "ماعز", "إبل", "خيول",
                 "دواجن", "سمان", "أسماك", "أرانب"],
                key="ref_animal_v110")
            ref_prod_map = {
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
                "أرانب": ["تسمين", "حليب", "صيانة"]}
            ref_prod = st.selectbox("نوع الإنتاج:",
                ref_prod_map.get(ref_animal, ["عام"]),
                key="ref_prod_v110")

            refs = get_references(ref_animal, ref_prod)

            st.markdown(f"""<div class="physio-card">
                <h4>📖 المرجع الأساسي</h4>
                <p style="color:#1a237e; font-size:1.15rem;
                    font-weight:700; margin:0;">{refs['primary']}</p>
                <p style="color:#555; margin:8px 0 0 0;">
                    📑 <b>الجدول:</b> {refs.get('table', '—')}</p>
            </div>""", unsafe_allow_html=True)

            if refs.get("secondary"):
                st.markdown("### 📚 مراجع داعمة")
                for s in refs["secondary"]:
                    st.markdown(f"- {s}")

            st.markdown("---")
            st.markdown("### 📖 المراجع العامة")
            for i, ref in enumerate(GENERAL_REFERENCES, 1):
                st.markdown(f"{i}. {ref}")

        except Exception as e:
            st.error(f"⚠️ {e}")


# 💡 المساعدة
if "💡 المساعدة" in tab_map:
    with tab_map["💡 المساعدة"]:
        try:
            st.markdown('<div class="section-title">'
                '💡 المساعدة</div>', unsafe_allow_html=True)
            st.markdown(f"""
### الأسئلة الشائعة:

**1. كيف أبدأ؟**
- اختر الحيوان → فعّل ✅ → اختر 3+ مكونات → 🚀

**2. ما الجديد في v11.10؟**
- ✅ **مختبر التركيبات الجاهزة** — حلّل أي تركيبة (من مصنع/مزرعة) وقارنها بـ NRC
- ✅ **3 طرق إدخال** للمختبر: جدول / نص / آخر تركيبة
- ✅ **صفحة مراجع** في كل تقارير PDF (النمذجة + بدائل + حظائر + مختبر + زائر)
- ✅ **مراجع حسب الحالة** — عرض فوري لمرجع NRC الدقيق
- ✅ **المختبر يعمل في كل البوابات** (زائر / مختص / مالك)

**3. بوابات الدخول:**
- 👑 **مالك** — كود آمن (محفوظ لدى المالك فقط)
- 🔬 **مختص** — دخول مباشر بدون كود
- 👥 **زائر** — مجاني بحاسبة + مختبر + PDF

**4. كيف أستخدم المختبر؟**
- تبويب **🧪 مختبر التركيبات**
- اختر الحيوان ونوع الإنتاج
- اختر طريقة إدخال: جدول يدوي / لصق نص / من آخر تركيبة
- اضغط **🔬 تشغيل المختبر**
- شاهد: الجودة + المقارنة + المراجع + PDF

**5. المراجع في PDF؟**
- كل تقرير PDF يحتوي على صفحة مراجع كاملة:
  - المرجع الأساسي (NRC)
  - الجدول المحدد
  - مراجع داعمة
  - قائمة المراجع العامة

### 📞 التواصل
📧 {OWNER_EMAIL}
📱 {WHATSAPP_NUMBER}

{DUA_FULL}
""")
        except Exception as e:
            st.error(f"⚠️ {e}")


# 📖 الدليل
if "📖 الدليل" in tab_map:
    with tab_map["📖 الدليل"]:
        try:
            st.markdown('<div class="section-title">'
                '📖 دليل المستخدم</div>', unsafe_allow_html=True)
            st.markdown(f"""
### 🎯 الغرض
**{APP_NAME} v{APP_VERSION}** — منصة ذكية لتركيب الأعلاف.

### ✨ الميزات الرئيسية
- 🐄 9 قطاعات × متغيرات متعددة
- 🌰 {len(get_oil_ingredients())} زيتاً + معايير
- 🧬 DP/CP
- ✅ ضمان جودة ≥ 70%
- 🎯 محرك NLP (SLSQP) محصّن
- 📏 شريط قياس لكل الحيوانات
- 🧪 **مختبر التركيبات الجاهزة** (جديد v11.10)
- 💬 غرفة تواصل متعددة الغرف
- 🎬 استديو تعليمي
- 📷 OCR
- 🏗️ حظائر 3D (مراوح + هياكل + تكاليف)
- 📊 جدوى + Monte Carlo
- 🍼 بدائل حليب + PDF
- 📄 PDF بختم رسمي + **مراجع NRC**
- 📱 مشاركة واتساب + بريد

### 🆕 v11.10 (هذا التحديث):
- ✅ **مختبر التحليل** — يعمل في كل البوابات
- ✅ **3 طرق إدخال** (جدول/نص/آخر تركيبة)
- ✅ **مقارنة NRC دقيقة** حسب الحيوان ونوع الإنتاج
- ✅ **تحقق توازن الطاقة/البروتين** في المختبر
- ✅ **مراجع في كل تقرير PDF**
- ✅ **قاموس مراجع شامل** (40+ حالة)
- ✅ **عرض المراجع حسب الحالة**

### 🧩 الملفات المُنشأة:
- `tawor_chat_rooms.json` — رسائل الدردشة
- `tawor_studio_content.json` — محتوى الاستديو
- `tawor_audit.log` — سجل أمني
- `tawor_shared_state.json` — حالة مشتركة

### 🔐 بوابات الدخول
- 👑 **المالك:** كود آمن (محفوظ لدى المالك فقط)
- 🔬 **المختص:** دخول مباشر — بدون كود
- 👥 **الزائر:** دخول مجاني بحاسبة مبسطة + مختبر + PDF

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
# نهاية الملف — Tawor Nology 11.10 ✅
# ═══════════════════════════════════════════════════════════════════════
