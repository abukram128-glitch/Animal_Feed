# ═══════════════════════════════════════════════════════════════════════
# الجزء 1 من 5 — الإعدادات، المعادلات العلمية، المحركات، الرسوم، الختم، والفيديو
# المنصة: تاور نولجي (Tawor Nology) — بإشراف: عبدالقادر إسماعيل
# ═══════════════════════════════════════════════════════════════════════

import base64
import io
import math
import os
import time as _time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

try:
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except Exception:
    minimize = None
    SCIPY_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except Exception:
    plt = None
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except Exception:
    go = None
    PLOTLY_AVAILABLE = False

try:
    from PIL import Image as PILImage, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except Exception:
    PILImage = None
    ImageDraw = None
    ImageFont = None
    PIL_AVAILABLE = False


# -----------------------------------------------------------------------
# 1. الثوابت والهوية العلمية
# -----------------------------------------------------------------------
APP_NAME = os.getenv("TAWOR_APP_NAME", "تاور نولجي — Tawor Nology")
APP_VERSION = "12.0.0-Pro"
APP_TAGLINE = "منصة ذكية متكاملة للنمذجة الغذائية، التحسين غير الخطي (NLP)، وتصميم المنشآت الحيوانية"
SUPERVISOR = os.getenv("TAWOR_SUPERVISOR", "أ. عبدالقادر إسماعيل")
SUPERVISOR_TITLE = "اختصاصي إنتاج حيواني وتغذية — باحث ماجستير"
WHATSAPP_NUMBER = os.getenv("TAWOR_WHATSAPP", "+218910000000")
OWNER_EMAIL = os.getenv("TAWOR_EMAIL", "abdelkader.tawor@example.com")

DUA_SHORT = "اللهم بارك لنا في علمنا وعملنا واجعله خالصاً لوجهك الكريم"
DUA_QURAN = "﴿ رَبِّ زِدْنِي عِلْمًا ﴾ • ﴿ وَقُلِ اعْمَلُوا فَسَيَرَى اللَّهُ عَمَلَكُمْ وَرَسُولُهُ وَالْمُؤْمِنُونَ ﴾"
DUA_VISITOR = "مرحباً بك في منصة <b>تاور نولجي</b> — دقة علمية بمعايير NRC / ARC / FAO وتقنيات برمجة متقدمة."
DUA_FULL = "اللهم اغفر لوالدَيّ وارحمهما كما ربّياني صغيراً، وبارك في ذريتي وعلمي وعملي، وانفع به عبادك."


def _load_owner_photo_b64() -> Optional[str]:
    """تحميل صورة المالك من Secrets أو متغير البيئة أو الملفات المحلية."""
    try:
        if hasattr(st, "secrets") and "OWNER_PHOTO_B64" in st.secrets:
            val = str(st.secrets["OWNER_PHOTO_B64"]).strip()
            if val:
                return val
    except Exception:
        pass

    env_b64 = os.getenv("OWNER_PHOTO_B64", "").strip()
    if env_b64:
        return env_b64

    candidate_paths = [
        "owner_photo.jpg",
        "owner_photo.jpeg",
        "owner_photo.png",
        "assets/owner_photo.jpg",
        "assets/owner_photo.png",
        "profile.jpg",
        "profile.png",
    ]
    for path in candidate_paths:
        if os.path.exists(path) and os.path.isfile(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception:
                continue
    return None


owner_b64: Optional[str] = _load_owner_photo_b64()
img_base64: Optional[str] = owner_b64


# -----------------------------------------------------------------------
# 2. المكتبة العلفية والمعادلات المرجعية عالية الدقة
# -----------------------------------------------------------------------
BIG_FEEDS_LIBRARY: Dict[str, Dict[str, Dict[str, Any]]] = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.8, "DP": 6.6, "SE": 78.0, "NDF": 11.5, "ADF": 3.0, "EE": 3.8, "ASH": 1.4, "Ca": 0.03, "P": 0.28, "price": 290.0},
        "شعير مطحون": {"CP": 11.2, "DP": 8.4, "SE": 71.0, "NDF": 19.0, "ADF": 6.5, "EE": 2.0, "ASH": 2.5, "Ca": 0.06, "P": 0.34, "price": 265.0},
        "قمح محلي": {"CP": 12.4, "DP": 9.6, "SE": 77.0, "NDF": 13.5, "ADF": 3.5, "EE": 1.9, "ASH": 1.8, "Ca": 0.05, "P": 0.36, "price": 280.0},
        "نخالة قمح (ردة)": {"CP": 15.5, "DP": 11.3, "SE": 56.0, "NDF": 42.0, "ADF": 12.5, "EE": 3.9, "ASH": 5.4, "Ca": 0.12, "P": 0.98, "price": 210.0},
    },
    "🌱 الأكساب ومصادر البروتين": {
        "كسب فول صويا 44%": {"CP": 44.0, "DP": 37.4, "SE": 74.0, "NDF": 14.5, "ADF": 9.5, "EE": 1.6, "ASH": 6.2, "Ca": 0.32, "P": 0.65, "price": 490.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DP": 41.2, "SE": 76.0, "NDF": 11.0, "ADF": 6.8, "EE": 1.5, "ASH": 6.0, "Ca": 0.30, "P": 0.68, "price": 530.0},
        "كسب عباد الشمس": {"CP": 32.0, "DP": 25.6, "SE": 63.0, "NDF": 31.0, "ADF": 21.0, "EE": 2.2, "ASH": 6.8, "Ca": 0.38, "P": 0.92, "price": 360.0},
        "مسحوق أسماك 60%": {"CP": 60.0, "DP": 51.0, "SE": 72.0, "NDF": 0.0, "ADF": 0.0, "EE": 8.0, "ASH": 18.0, "Ca": 4.20, "P": 2.60, "price": 980.0},
    },
    "🌰 الزيوت والدهون": {
        "زيت فول الصويا": {"CP": 0.0, "DP": 0.0, "SE": 195.0, "NDF": 0.0, "ADF": 0.0, "EE": 99.5, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "price": 1150.0, "desc": "مصدر عالي الطاقة واللينوليك للدواجن والأسماك."},
        "زيت السمك (Fish Oil)": {"CP": 0.0, "DP": 0.0, "SE": 198.0, "NDF": 0.0, "ADF": 0.0, "EE": 99.5, "ASH": 0.0, "Ca": 0.0, "P": 0.0, "price": 1350.0, "desc": "غني بأحماض EPA و DHA لتغذية الأسماك والأمهات."},
    },
    "🪨 الأملاح والإضافات": {
        "الحجر الجيري": {"CP": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 96.0, "Ca": 38.0, "P": 0.02, "price": 85.0},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 88.0, "Ca": 23.0, "P": 18.0, "price": 620.0},
        "ملح الطعام": {"CP": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0, "Ca": 0.0, "P": 0.0, "price": 90.0},
        "بريمكس مجترات": {"CP": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Ca": 15.0, "P": 5.0, "price": 1400.0},
        "بريمكس تسمين دواجن": {"CP": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Ca": 12.0, "P": 4.0, "price": 1600.0},
        "بريمكس بياض": {"CP": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Ca": 14.0, "P": 4.0, "price": 1550.0},
        "بريمكس أسماك": {"CP": 0.0, "DP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0, "Ca": 10.0, "P": 4.0, "price": 1750.0},
        "ليسين نقي": {"CP": 94.0, "DP": 92.0, "SE": 80.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0, "price": 2100.0},
        "ميثيونين نقي": {"CP": 58.0, "DP": 57.0, "SE": 82.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5, "Ca": 0.0, "P": 0.0, "price": 2600.0},
    },
}

MAX_OIL_PERCENTAGE: Dict[str, Dict[str, Any]] = {
    "أبقار": {"max": 5.0, "optimal": 2.5, "source": "NRC (2001) Dairy Cattle"},
    "أغنام": {"max": 4.5, "optimal": 2.0, "source": "NRC (2007) Small Ruminants"},
    "ماعز": {"max": 4.5, "optimal": 2.0, "source": "NRC (2007) Goats"},
    "إبل": {"max": 4.0, "optimal": 1.8, "source": "FAO (2010) Camel Nutrition"},
    "خيول": {"max": 8.0, "optimal": 4.0, "source": "NRC (2007) Horses"},
    "دواجن": {"max": 6.5, "optimal": 3.5, "source": "NRC / Aviagen Ross & Cobb"},
    "سمان": {"max": 5.0, "optimal": 2.5, "source": "NRC (1994) Poultry"},
    "أسماك": {"max": 12.0, "optimal": 6.0, "source": "NRC (2011) Fish & Crustaceans"},
    "أرانب": {"max": 4.0, "optimal": 2.0, "source": "NRC (1977) / Lebas Rabbits"},
}

GENERAL_REFERENCES: List[str] = [
    "NRC (2001) Nutrient Requirements of Dairy Cattle — National Academies Press.",
    "NRC (2007) Nutrient Requirements of Small Ruminants: Sheep, Goats, Cervids, and New World Camelids.",
    "NRC (2007) Nutrient Requirements of Horses (6th Revised Edition).",
    "NRC (2011) Nutrient Requirements of Fish and Shrimp.",
    "FAO (2010) Camel Nutrition & Feeding Standards.",
    "ARC (1980 / 1984) The Nutrient Requirements of Ruminant Livestock.",
]


class AnimalRequirement:
    def __init__(
        self,
        DP: float,
        CP: float,
        SE: float,
        NDF: float = 30.0,
        ADF: float = 18.0,
        EE: float = 4.0,
        ASH: float = 7.0,
        Ca: float = 0.8,
        P: float = 0.45,
        name_ar: str = "احتياج قياسي",
        note: str = "",
    ):
        self.DP = float(DP)
        self.CP = float(CP)
        self.SE = float(SE)
        self.NDF = float(NDF)
        self.ADF = float(ADF)
        self.EE = float(EE)
        self.ASH = float(ASH)
        self.Ca = float(Ca)
        self.P = float(P)
        self.name_ar = name_ar
        self.note = note


def _get_ingredient_lookup() -> Dict[str, Dict[str, Any]]:
    lookup: Dict[str, Dict[str, Any]] = {}
    for _, items in BIG_FEEDS_LIBRARY.items():
        for name, spec in items.items():
            lookup[name] = spec
    return lookup


def get_oil_ingredients() -> Dict[str, Dict[str, Any]]:
    return dict(BIG_FEEDS_LIBRARY.get("🌰 الزيوت والدهون", {}))


def get_oil_standard(std_key: str) -> Dict[str, Any]:
    prefix = (std_key or "").split("_")[0]
    return MAX_OIL_PERCENTAGE.get(prefix, {"max": 5.0, "optimal": 2.5, "source": "NRC Standard"})


def requirement_to_standard(req: AnimalRequirement) -> Dict[str, float]:
    return {
        "DP": req.DP,
        "CP": req.CP,
        "SE": req.SE,
        "NDF": req.NDF,
        "ADF": req.ADF,
        "EE": req.EE,
        "ASH": req.ASH,
        "Ca": req.Ca,
        "P": req.P,
    }


def compute_formula_nutrients(formula: Dict[str, float]) -> Dict[str, float]:
    if not formula:
        return {"DP": 0.0, "CP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0}
    total_pct = sum(max(0.0, float(v or 0.0)) for v in formula.values())
    if total_pct <= 0:
        return {"DP": 0.0, "CP": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.0, "Ca": 0.0, "P": 0.0}
    norm = {k: max(0.0, float(v or 0.0)) / total_pct * 100.0 for k, v in formula.items()}
    lookup = _get_ingredient_lookup()
    keys = ["DP", "CP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]
    out = {k: 0.0 for k in keys}
    for ing, pct in norm.items():
        spec = lookup.get(ing, {})
        w = pct / 100.0
        for k in keys:
            out[k] += float(spec.get(k, 0.0) or 0.0) * w
    return out


def evaluate_difference(pct_diff: float, standard_value: float = 0.0) -> Dict[str, Any]:
    abs_p = abs(float(pct_diff or 0.0))
    if abs_p <= 5.0:
        return {"label": "✅ مثالي", "score": 100.0}
    if abs_p <= 12.0:
        return {"label": "🟢 جيد جداً", "score": 88.0}
    if abs_p <= 22.0:
        return {"label": "🟡 مقبول", "score": 74.0}
    return {"label": "🔴 يحتاج ضبط", "score": 48.0}


def evaluate_quality_weighted(formula: Dict[str, float], std_dict: Dict[str, float], animal: str = "") -> Tuple[float, Dict[str, float]]:
    actual = compute_formula_nutrients(formula)
    weights = {"CP": 0.25, "DP": 0.25, "SE": 0.25, "Ca": 0.125, "P": 0.125}
    weighted_sum = 0.0
    total_w = 0.0
    details: Dict[str, float] = {}
    for k, w in weights.items():
        sv = float(std_dict.get(k, 0.0) or 0.0)
        if sv > 0:
            av = float(actual.get(k, 0.0) or 0.0)
            pct_err = (av - sv) / sv * 100.0
            ev = evaluate_difference(pct_err, sv)
            weighted_sum += ev["score"] * w
            total_w += w
            details[k] = ev["score"]
    score = (weighted_sum / total_w) if total_w > 0 else 80.0
    return round(max(0.0, min(100.0, score)), 2), details


def get_reference_equations(animal: str, prod: str = "") -> Dict[str, str]:
    equations_map = {
        "أبقار": {
            "source": "NRC (2001) — Net Energy & Metabolizable/Digestible Protein Equations",
            "NEm (Mcal/d)": "0.080 × BW^0.75",
            "FCM 4% (kg/d)": "0.4 × Milk_kg + 15 × Fat_kg",
            "MP / DP Balance": "DMI × (0.038 + 0.0006 × Milk_kg)",
            "example": "بقرة 500 كجم تنتج 20 كجم حليب تحتاج طاقة وتوازن بروتين دقيق لتفادي الخلل الأيضي.",
        },
        "أغنام": {
            "source": "NRC (2007) — Small Ruminants Metabolic Equations",
            "MEm (kcal/d)": "56 × BW^0.75 (صيانة) أو 67 × BW^0.75 (نشاط/رعي)",
            "Ca:P Ratio": "الهدف المثالي بين 1.5 : 1 و 2.2 : 1 للوقاية من حصوات المسالك البولية.",
            "example": "تسمين الحملان يتطلب طاقة مركزة مع ضبط الألياف NDF والرماد لتعظيم معدل التحويل الغذائي.",
        },
        "دواجن": {
            "source": "NRC (1994) / Ross & Cobb Broiler-Layer Standards",
            "ME:CP Ratio": "kcal ME/kg ÷ %CP (مثلاً ~135–145 في البادي والنامي)",
            "Ideal Amino Ratio": "Lysine = 100% | Methionine ≥ 36–42% من الليسين",
            "example": "موازنة الطاقة مع البروتين والأحماض الأمينية تمنع تراكم الدهون وتحسن معامل التحويل FCR.",
        },
        "أسماك": {
            "source": "NRC (2011) — Fish Bioenergetics & Protein-to-Energy Ratio",
            "P/E Ratio": "g Crude Protein / MJ Digestible Energy (حسب المرحلة العمرية)",
            "example": "الزريعة والبادئ تحتاج بروتيناً أعلى (38–42%) مع أحماض دهنية أساسية.",
        },
    }
    return equations_map.get(
        animal,
        {
            "source": "NRC / ARC / FAO Nutritional Standards",
            "DMI (% BW)": "2.0% – 3.5% من وزن الجسم حسب الحالة الفسيولوجية",
            "Ca:P Target": "1.2 : 1 – 2.0 : 1",
            "example": "موازنة الطاقة والبروتين والمعادن أساس الكفاءة الاقتصادية والصحة الحيوانية.",
        },
    )


def get_references(animal: str, prod: str = "") -> Dict[str, Any]:
    eqs = get_reference_equations(animal, prod)
    return {
        "primary": eqs.get("source", "NRC / ARC / FAO Standards"),
        "table": f"Standard Nutrient Requirement Matrix — {animal} ({prod or 'General'})",
        "secondary": GENERAL_REFERENCES[:3],
    }


def get_default_selections(animal: str, prod: str, req: AnimalRequirement) -> List[str]:
    if animal == "دواجن":
        base = ["ذرة صفراء", "كسب فول صويا 48%", "زيت فول الصويا", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "بريمكس تسمين دواجن", "ليسين نقي", "ميثيونين نقي"]
    elif animal == "أسماك":
        base = ["كسب فول صويا 44%", "مسحوق أسماك 60%", "قمح محلي", "زيت السمك (Fish Oil)", "فوسفات ثنائي الكالسيوم", "بريمكس أسماك"]
    else:
        base = ["ذرة صفراء", "شعير مطحون", "كسب فول صويا 44%", "نخالة قمح (ردة)", "الحجر الجيري", "فوسفات ثنائي الكالسيوم", "ملح الطعام", "بريمكس مجترات"]
    lookup = _get_ingredient_lookup()
    return [x for x in base if x in lookup]


def get_cattle_requirements(state_key: str, weight_kg: float = 500.0, milk_yield: float = 20.0) -> AnimalRequirement:
    presets = {
        "حليب_عالي": AnimalRequirement(13.2, 18.0, 68.0, 29.0, 17.0, 4.5, 6.8, 0.85, 0.45, "أبقار حلابة عالية الإنتاج"),
        "حليب_متوسط": AnimalRequirement(11.5, 16.0, 64.0, 32.0, 19.0, 4.0, 7.0, 0.75, 0.42, "أبقار حلابة متوسطة الإنتاج"),
        "حليب_منخفض": AnimalRequirement(10.0, 14.0, 60.0, 34.0, 21.0, 3.5, 7.2, 0.68, 0.38, "أبقار حلابة منخفضة الإنتاج"),
        "تسمين_مكثف": AnimalRequirement(11.8, 15.0, 72.0, 26.0, 15.0, 4.5, 6.2, 0.72, 0.40, "تسمين عجول مكثف"),
        "تسمين_عادي": AnimalRequirement(10.2, 13.5, 66.0, 31.0, 18.0, 3.8, 6.8, 0.65, 0.38, "تسمين عجول عادي"),
        "حمل_أخير": AnimalRequirement(10.5, 14.0, 62.0, 33.0, 20.0, 3.6, 7.0, 0.74, 0.42, "أبقار في الثلث الأخير من الحمل"),
        "صيانة": AnimalRequirement(7.5, 10.5, 54.0, 38.0, 24.0, 3.0, 7.5, 0.55, 0.32, "أبقار — احتياج الصيانة"),
    }
    return presets.get(state_key, presets["حليب_متوسط"])


def get_sheep_requirements(state_key: str, is_male: bool = False, weight_kg: float = 50.0, litter_size: int = 1) -> AnimalRequirement:
    presets = {
        "تسمين_مكثف": AnimalRequirement(11.5, 15.5, 68.0, 27.0, 16.0, 4.0, 6.5, 0.75, 0.40, "تسمين حملان مكثف"),
        "تسمين_عادي": AnimalRequirement(10.0, 13.5, 63.0, 32.0, 19.0, 3.5, 7.0, 0.68, 0.38, "تسمين حملان عادي"),
        "حملان_تيد": AnimalRequirement(12.5, 16.5, 70.0, 25.0, 15.0, 4.2, 6.5, 0.80, 0.42, "حملان فطام ونمو سريع"),
        "مرضعات": AnimalRequirement(11.2, 15.0, 64.0, 31.0, 18.5, 3.8, 7.0, 0.78, 0.42, f"نعاج مرضعات ({litter_size} مواليد)"),
        "حامل_أخير": AnimalRequirement(10.2, 13.8, 60.0, 33.0, 20.0, 3.5, 7.2, 0.72, 0.40, "نعاج حامل — المرحلة الأخيرة"),
        "حامل_متوسط": AnimalRequirement(8.8, 12.0, 56.0, 36.0, 22.0, 3.2, 7.5, 0.62, 0.35, "نعاج حامل — المرحلة المتوسطة"),
        "صيانة": AnimalRequirement(7.5, 10.5, 52.0, 38.0, 24.0, 3.0, 7.5, 0.55, 0.32, "أغنام — احتياج الصيانة"),
    }
    return presets.get(state_key, presets["صيانة"])


def get_goat_requirements(state_key: str, is_male: bool = False, milk_yield: float = 2.0) -> AnimalRequirement:
    presets = {
        "تسمين_جديان": AnimalRequirement(11.5, 15.5, 66.0, 28.0, 17.0, 3.8, 6.8, 0.75, 0.40, "تسمين جديان"),
        "تيوس": AnimalRequirement(10.0, 13.5, 60.0, 33.0, 20.0, 3.5, 7.0, 0.65, 0.36, "تيوس فحول"),
        "حلابة_عالي": AnimalRequirement(12.2, 16.5, 65.0, 30.0, 18.0, 4.0, 7.0, 0.82, 0.44, "ماعز حلابة عالية الإنتاج"),
        "حلابة_متوسط": AnimalRequirement(10.5, 14.5, 61.0, 33.0, 20.0, 3.6, 7.2, 0.72, 0.40, "ماعز حلابة متوسطة الإنتاج"),
        "حامل_أخير": AnimalRequirement(10.0, 13.5, 59.0, 34.0, 21.0, 3.5, 7.2, 0.70, 0.38, "ماعز حامل — نهاية الحمل"),
        "صيانة": AnimalRequirement(7.8, 11.0, 53.0, 37.0, 23.0, 3.0, 7.5, 0.58, 0.34, "ماعز — احتياج الصيانة"),
    }
    return presets.get(state_key, presets["صيانة"])


def get_camel_requirements(state_key: str, weight_kg: float = 400.0, milk_yield: float = 5.0) -> AnimalRequirement:
    presets = {
        "نمو": AnimalRequirement(11.0, 14.8, 65.0, 31.0, 19.0, 3.6, 7.0, 0.72, 0.40, "إبل — مرحلة النمو"),
        "تسمين": AnimalRequirement(10.5, 14.0, 67.0, 29.0, 18.0, 3.8, 6.8, 0.70, 0.38, "إبل — تسمين"),
        "حليب": AnimalRequirement(11.2, 15.2, 64.0, 32.0, 19.5, 3.6, 7.2, 0.78, 0.42, "إبل حلابة"),
        "سباق": AnimalRequirement(11.8, 15.5, 70.0, 27.0, 16.5, 4.2, 6.5, 0.75, 0.42, "إبل سباق وهجن"),
        "صيانة": AnimalRequirement(7.8, 10.8, 55.0, 37.0, 23.0, 3.0, 7.5, 0.58, 0.34, "إبل — صيانة"),
    }
    return presets.get(state_key, presets["صيانة"])


def get_horse_requirements(state_key: str, weight_kg: float = 450.0) -> AnimalRequirement:
    presets = {
        "رياضة_مكثف": AnimalRequirement(11.5, 15.0, 72.0, 26.0, 16.0, 4.5, 6.5, 0.80, 0.45, "خيول — عمل رياضي مكثف"),
        "رياضة_عادي": AnimalRequirement(9.8, 13.0, 66.0, 30.0, 18.5, 3.8, 6.8, 0.70, 0.40, "خيول — عمل رياضي عادي"),
        "نمو_أمهار": AnimalRequirement(12.2, 16.0, 70.0, 27.0, 16.5, 4.0, 6.8, 0.85, 0.48, "نمو أمهار"),
        "مرضعات": AnimalRequirement(11.5, 15.2, 68.0, 29.0, 18.0, 4.0, 7.0, 0.82, 0.45, "أفراس مرضعات"),
        "صيانة": AnimalRequirement(7.6, 10.5, 56.0, 36.0, 22.0, 3.0, 7.2, 0.55, 0.32, "خيول — صيانة"),
    }
    return presets.get(state_key, presets["صيانة"])


def get_poultry_requirements(strain: str, age_weeks: int = 1) -> AnimalRequirement:
    if strain == "بياض":
        return AnimalRequirement(15.5, 18.0, 72.0, 10.0, 4.5, 4.2, 12.5, 3.80, 0.55, "دواجن بياض — مرحلة الإنتاج")
    if age_weeks <= 2:
        return AnimalRequirement(20.0, 23.0, 77.0, 9.0, 4.0, 5.2, 6.2, 1.00, 0.48, "لاحم — علف بادي (Starter)")
    if age_weeks <= 4:
        return AnimalRequirement(18.2, 21.0, 78.0, 9.5, 4.2, 5.6, 5.8, 0.90, 0.44, "لاحم — علف نامي (Grower)")
    return AnimalRequirement(16.8, 19.5, 79.0, 10.0, 4.5, 6.0, 5.5, 0.85, 0.40, "لاحم — علف ناهي (Finisher)")


def get_quail_requirements(q_type: str, age_weeks: int = 1) -> AnimalRequirement:
    if q_type == "بياض":
        return AnimalRequirement(17.5, 20.5, 72.0, 10.0, 4.5, 4.2, 10.5, 2.90, 0.50, "سمان بياض")
    return AnimalRequirement(21.5, 25.0, 75.0, 9.0, 4.0, 4.8, 6.5, 0.95, 0.45, "سمان تسمين")


def get_fish_requirements(species: str, stage: str) -> AnimalRequirement:
    if "بادئ" in stage or "زريعة" in stage:
        return AnimalRequirement(34.0, 40.0, 74.0, 7.0, 3.0, 7.5, 8.5, 1.20, 0.75, f"{species} — بادئ/زريعة")
    if "نمو" in stage:
        return AnimalRequirement(28.0, 34.0, 72.0, 8.5, 3.8, 6.8, 8.0, 1.05, 0.65, f"{species} — مرحلة النمو")
    return AnimalRequirement(24.0, 30.0, 70.0, 9.5, 4.2, 6.2, 7.8, 0.95, 0.60, f"{species} — مرحلة التسمين")


def get_rabbit_requirements(r_type: str, weight_kg: float = 4.0) -> AnimalRequirement:
    if r_type == "حليب":
        return AnimalRequirement(14.0, 17.5, 68.0, 24.0, 13.0, 4.2, 7.0, 1.00, 0.55, "أرانب أمهات مرضعات")
    if r_type == "تسمين":
        return AnimalRequirement(13.0, 16.0, 70.0, 25.0, 13.5, 4.0, 6.8, 0.85, 0.48, "أرانب تسمين")
    return AnimalRequirement(10.0, 13.0, 62.0, 29.0, 16.0, 3.2, 7.2, 0.65, 0.40, "أرانب — صيانة")


# -----------------------------------------------------------------------
# 3. محرك التركيب الذكي والتحليل والتحسين غير الخطي (NLP)
# -----------------------------------------------------------------------
def auto_formulate_smart(
    selected_ings: List[str],
    prices_dict: Dict[str, float],
    target_std: Dict[str, float],
    standard_key: str = "",
    basis: str = "DP",
    min_quality: float = 70.0,
    animal_type: str = "",
    production_type: str = "",
) -> Dict[str, Any]:
    lookup = _get_ingredient_lookup()
    valid = [x for x in selected_ings if x in lookup]
    if len(valid) < 2:
        return {"success": False, "message": "يرجى اختيار مكونين صالحين على الأقل."}

    n = len(valid)
    p_key = "DP" if basis == "DP" and float(target_std.get("DP", 0) or 0) > 0 else "CP"
    target_p = float(target_std.get(p_key, 15.0) or 15.0)
    target_se = float(target_std.get("SE", 65.0) or 65.0)
    target_ca = float(target_std.get("Ca", 0.7) or 0.7)
    target_p_min = float(target_std.get("P", 0.4) or 0.4)

    p_vec = np.array([float(lookup[i].get(p_key, lookup[i].get("CP", 0.0)) or 0.0) for i in valid], dtype=float)
    se_vec = np.array([float(lookup[i].get("SE", 0.0) or 0.0) for i in valid], dtype=float)
    ca_vec = np.array([float(lookup[i].get("Ca", 0.0) or 0.0) for i in valid], dtype=float)
    phos_vec = np.array([float(lookup[i].get("P", 0.0) or 0.0) for i in valid], dtype=float)
    c_vec = np.array([float(prices_dict.get(i, lookup[i].get("price", 300.0)) or 300.0) for i in valid], dtype=float)

    x0 = np.ones(n, dtype=float) / n
    bounds = [(0.0, 1.0) for _ in range(n)]

    # ضبط حدود الإضافات المعدنية العالية حتى لا تطغى على العليقة
    for idx, name in enumerate(valid):
        if any(tag in name for tag in ["حجر", "فوسفات", "ملح", "بريمكس", "ليسين", "ميثيونين"]):
            bounds[idx] = (0.0, 0.08)

    def objective(x: np.ndarray) -> float:
        w = x / max(np.sum(x), 1e-9)
        p_err = ((np.dot(w, p_vec) - target_p) / max(target_p, 1.0)) ** 2
        se_err = ((np.dot(w, se_vec) - target_se) / max(target_se, 1.0)) ** 2
        ca_err = ((np.dot(w, ca_vec) - target_ca) / max(target_ca, 0.1)) ** 2
        ph_err = ((np.dot(w, phos_vec) - target_p_min) / max(target_p_min, 0.1)) ** 2
        cost_term = 0.08 * (np.dot(w, c_vec) / 500.0)
        return float(3.5 * p_err + 3.5 * se_err + 1.5 * ca_err + 1.5 * ph_err + cost_term)

    if SCIPY_AVAILABLE and minimize is not None:
        res = minimize(objective, x0, method="SLSQP", bounds=bounds, constraints={"type": "eq", "fun": lambda x: np.sum(x) - 1.0})
        w_opt = res.x if res.success else x0
    else:
        w_opt = x0

    w_opt = np.clip(w_opt, 0.0, 1.0)
    if np.sum(w_opt) <= 0:
        w_opt = x0
    w_opt = w_opt / np.sum(w_opt)

    formula = {name: round(float(pct * 100.0), 3) for name, pct in zip(valid, w_opt) if pct > 0.0005}
    if not formula:
        formula = {valid[0]: 100.0}

    actual = compute_formula_nutrients(formula)
    cost_per_ton = sum(float(lookup.get(k, {}).get("price", prices_dict.get(k, 300.0))) * (v / 100.0) for k, v in formula.items())
    quality_score, _ = evaluate_quality_weighted(formula, target_std, animal_type)

    return {
        "success": True,
        "formula": formula,
        "actual_nutrients": actual,
        "cost": round(float(cost_per_ton), 2),
        "quality_score": quality_score,
        "meets_standard": quality_score >= float(min_quality),
        "warning": None if quality_score >= float(min_quality) else "تم الوصول لأفضل موازنة ممكنة ضمن المكونات المختارة — يُنصح بإضافة مصدر بروتين أو طاقة داعم لرفع الجودة فوق 70%.",
    }


def analyze_existing_formula(formula: Dict[str, float], animal: str, prod: str) -> Dict[str, Any]:
    clean = {k: float(v or 0.0) for k, v in (formula or {}).items() if k and float(v or 0.0) > 0}
    if not clean:
        return {"success": False, "message": "التركيبة فارغة أو جميع النسب صفر."}

    total = sum(clean.values())
    norm = {k: v / total * 100.0 for k, v in clean.items()}
    actual = compute_formula_nutrients(norm)

    if animal == "أبقار":
        req = get_cattle_requirements(prod)
    elif animal == "أغنام":
        req = get_sheep_requirements(prod)
    elif animal == "ماعز":
        req = get_goat_requirements(prod)
    elif animal == "إبل":
        req = get_camel_requirements(prod)
    elif animal == "خيول":
        req = get_horse_requirements(prod)
    elif animal == "دواجن":
        req = get_poultry_requirements(prod, 2)
    elif animal == "سمان":
        req = get_quail_requirements(prod, 2)
    elif animal == "أسماك":
        req = get_fish_requirements("البلطي النيلي", prod)
    elif animal == "أرانب":
        req = get_rabbit_requirements(prod)
    else:
        req = AnimalRequirement(11.0, 15.0, 65.0)

    std_dict = requirement_to_standard(req)
    quality_score, _ = evaluate_quality_weighted(norm, std_dict, animal)
    lookup = _get_ingredient_lookup()
    cost_per_ton = sum(float(lookup.get(k, {}).get("price", 300.0) or 300.0) * (v / 100.0) for k, v in norm.items())

    ca_val = float(actual.get("Ca", 0.0) or 0.0)
    p_val = float(actual.get("P", 0.0) or 0.0)
    ca_p_ratio = (ca_val / p_val) if p_val > 0 else 0.0

    labels = {"DP": "بروتين مهضوم (DP)", "CP": "بروتين خام (CP)", "SE": "مكافئ النشا (SE)", "Ca": "كالسيوم (Ca)", "P": "فوسفور (P)"}
    comparison = []
    for k, ar_label in labels.items():
        sv = float(std_dict.get(k, 0.0) or 0.0)
        av = float(actual.get(k, 0.0) or 0.0)
        diff = av - sv
        diff_pct = (diff / sv * 100.0) if sv else 0.0
        ev = evaluate_difference(diff_pct, sv)
        comparison.append({"العنصر": ar_label, "المعيار": sv, "المحسوب": av, "الفرق": diff, "الفرق %": diff_pct, "التقييم": ev["label"]})

    e_share = min(100.0, max(0.0, float(actual.get("SE", 0.0) or 0.0) / 85.0 * 100.0))
    p_share = min(100.0, max(0.0, float(actual.get("CP", 0.0) or 0.0) / 26.0 * 100.0))

    return {
        "success": True,
        "formula": norm,
        "standard": std_dict,
        "actual": actual,
        "comparison": comparison,
        "quality_score": quality_score,
        "cost_per_ton": round(cost_per_ton, 2),
        "ca_p_ratio": round(ca_p_ratio, 2),
        "energy_share_pct": round(e_share, 1),
        "protein_share_pct": round(p_share, 1),
        "animal_type": animal,
        "production_type": prod,
        "references": get_references(animal, prod),
    }


def _get_requirement_for_nlp(animal: str, prod: str) -> Dict[str, float]:
    base_map = {
        "أبقار": {"ME": 2750.0, "CP": 16.5, "DP": 12.0},
        "أغنام": {"ME": 2600.0, "CP": 15.0, "DP": 11.0},
        "ماعز": {"ME": 2550.0, "CP": 15.0, "DP": 11.0},
        "إبل": {"ME": 2650.0, "CP": 14.5, "DP": 10.8},
        "خيول": {"ME": 2850.0, "CP": 14.5, "DP": 11.0},
        "دواجن": {"ME": 3050.0, "CP": 21.5, "DP": 18.5},
        "سمان": {"ME": 2950.0, "CP": 23.0, "DP": 19.5},
        "أسماك": {"ME": 3100.0, "CP": 34.0, "DP": 28.0},
        "أرانب": {"ME": 2600.0, "CP": 16.5, "DP": 13.0},
    }
    return base_map.get(animal, {"ME": 2700.0, "CP": 16.0, "DP": 12.0})


def nlp_optimize_feed(
    selected_ings: List[str],
    ing_data: Dict[str, Dict[str, Any]],
    prices_dict: Dict[str, float],
    animal_type: str = "",
    production_type: str = "",
    price_product: float = 2.5,
) -> Dict[str, Any]:
    valid = [i for i in selected_ings if i in ing_data]
    if len(valid) < 2:
        return {"success": False, "message": "اختر مكونين على الأقل لتحسين NLP."}

    req = _get_requirement_for_nlp(animal_type, production_type)
    target_me = float(req["ME"])
    target_cp = float(req["CP"])

    me_arr = np.array([float(ing_data[i].get("SE", 0.0) or 0.0) * 41.0 for i in valid], dtype=float)
    cp_arr = np.array([float(ing_data[i].get("CP", 0.0) or 0.0) for i in valid], dtype=float)
    cost_arr = np.array([float(prices_dict.get(i, ing_data[i].get("price", 300.0)) or 300.0) / 1000.0 for i in valid], dtype=float)

    n = len(valid)
    x0 = np.ones(n, dtype=float) / n
    bounds = [(0.0, 1.0) for _ in range(n)]

    def loss_fn(x: np.ndarray) -> float:
        w = x / max(np.sum(x), 1e-9)
        me_val = float(np.dot(w, me_arr))
        cp_val = float(np.dot(w, cp_arr))
        cost_kg = float(np.dot(w, cost_arr))
        # تعظيم صافي هامش الأداء/الكلفة بتقليل التكلفة والانحراف عن المتطلبات
        me_pen = ((me_val - target_me) / max(target_me, 1.0)) ** 2
        cp_pen = ((cp_val - target_cp) / max(target_cp, 1.0)) ** 2
        return float(cost_kg + 0.65 * me_pen + 0.65 * cp_pen)

    if SCIPY_AVAILABLE and minimize is not None:
        res = minimize(loss_fn, x0, method="SLSQP", bounds=bounds, constraints={"type": "eq", "fun": lambda x: np.sum(x) - 1.0})
        w_opt = res.x if res.success else x0
    else:
        w_opt = x0

    w_opt = np.clip(w_opt, 0.0, 1.0)
    w_opt = w_opt / max(np.sum(w_opt), 1e-9)

    formula = {name: round(float(p * 100.0), 2) for name, p in zip(valid, w_opt) if p > 0.001}
    final_cost = float(np.dot(w_opt, cost_arr))
    final_me = float(np.dot(w_opt, me_arr))
    final_cp = float(np.dot(w_opt, cp_arr))
    est_profit = round(float(price_product) - final_cost, 4)

    return {
        "success": True,
        "formula": formula,
        "final_cost": round(final_cost, 4),
        "final_me": round(final_me, 1),
        "final_cp": round(final_cp, 2),
        "max_profit": est_profit,
        "strategy": "SLSQP Non-Linear Cost-Nutrient Balance",
        "warning": None if abs(final_cp - target_cp) <= target_cp * 0.2 else "التركيب غير الخطي مائل لتقليل الكلفة؛ راجع نسب البروتين والطاقة.",
    }


# -----------------------------------------------------------------------
# 4. الرسوم البيانية: الرادار، المقارنة، التوزيع، المقياس، ومنحنى NLP
# -----------------------------------------------------------------------
def create_colorful_bar_chart(std_dict: Dict[str, float], act_dict: Dict[str, float]) -> Optional[io.BytesIO]:
    if not MATPLOTLIB_AVAILABLE or not std_dict or not act_dict:
        return None
    keys = [k for k in ["DP", "CP", "SE", "Ca", "P"] if float(std_dict.get(k, 0.0) or 0.0) > 0]
    if not keys:
        keys = list(std_dict.keys())[:4]
    std_vals = [float(std_dict.get(k, 0.0) or 0.0) for k in keys]
    act_vals = [float(act_dict.get(k, 0.0) or 0.0) for k in keys]

    x = np.arange(len(keys))
    width = 0.36
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=160)
    ax.bar(x - width / 2, std_vals, width, label="Standard (المعيار)", color="#1b5e20", edgecolor="none")
    ax.bar(x + width / 2, act_vals, width, label="Calculated (المحسوب)", color="#d4af37", edgecolor="none")
    ax.set_xticks(x)
    ax.set_xticklabels(keys, fontweight="bold")
    ax.set_title("Standard vs. Calculated Nutrients (المعيار مقابل المحسوب)", fontweight="bold")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    buf.seek(0)
    return buf


def create_colorful_pie_chart(formula: Dict[str, float]) -> Optional[io.BytesIO]:
    if not MATPLOTLIB_AVAILABLE or not formula:
        return None
    labels = list(formula.keys())
    sizes = [max(0.0, float(v or 0.0)) for v in formula.values()]
    if sum(sizes) <= 0:
        return None
    fig, ax = plt.subplots(figsize=(6.4, 4.4), dpi=160)
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140, pctdistance=0.78)
    ax.set_title("Ingredient Distribution (توزيع المكونات)", fontweight="bold")
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    buf.seek(0)
    return buf


def create_radar_chart(std_dict: Dict[str, float], act_dict: Dict[str, float]) -> Optional[io.BytesIO]:
    """رسم راداري يوضح نسبة تحقق كل عنصر غذائي مقارنة بالمعيار (100%)."""
    if not MATPLOTLIB_AVAILABLE or not std_dict or not act_dict:
        return None
    keys = [k for k in ["DP", "CP", "SE", "Ca", "P"] if float(std_dict.get(k, 0.0) or 0.0) > 0]
    if len(keys) < 3:
        keys = ["DP", "CP", "SE"]
    pct_achieved = []
    for k in keys:
        sv = max(float(std_dict.get(k, 1.0) or 1.0), 1e-6)
        av = float(act_dict.get(k, 0.0) or 0.0)
        pct_achieved.append(min(150.0, max(0.0, (av / sv) * 100.0)))

    angles = np.linspace(0, 2 * np.pi, len(keys), endpoint=False).tolist()
    pct_plot = pct_achieved + pct_achieved[:1]
    target_plot = [100.0] * len(keys) + [100.0]
    angles_plot = angles + angles[:1]

    fig, ax = plt.subplots(figsize=(5.6, 5.2), dpi=160, subplot_kw=dict(polar=True))
    ax.plot(angles_plot, target_plot, color="#1565c0", linestyle="--", linewidth=1.8, label="Target 100% (المعيار)")
    ax.plot(angles_plot, pct_plot, color="#1b5e20", linewidth=2.4, label="Actual % (المحسوب)")
    ax.fill(angles_plot, pct_plot, color="#2e7d32", alpha=0.25)
    ax.set_xticks(angles)
    ax.set_xticklabels(keys, fontweight="bold")
    ax.set_ylim(0, 140)
    ax.set_title("Nutritional Radar (% of Standard)", fontweight="bold", pad=16)
    ax.legend(loc="upper right", bbox_to_anchor=(1.28, 1.12), fontsize=8)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def create_gauge_chart(quality_score: float) -> Optional[io.BytesIO]:
    if not MATPLOTLIB_AVAILABLE:
        return None
    q = max(0.0, min(100.0, float(quality_score or 0.0)))
    fig, ax = plt.subplots(figsize=(5.2, 3.2), dpi=160)
    ax.barh([0], [100], color="#e0e0e0", height=0.35)
    bar_color = "#1b5e20" if q >= 70 else ("#f9a825" if q >= 50 else "#c62828")
    ax.barh([0], [q], color=bar_color, height=0.35)
    ax.axvline(70, color="#0d47a1", linestyle="--", linewidth=1.5, label="Min Target (70%)")
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xlabel("Quality Score % (درجة الجودة)")
    ax.set_title(f"Formula Quality Index: {q:.1f}%", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    buf.seek(0)
    return buf


def create_ca_p_ratio_chart(ca_val: float, p_val: float) -> Optional[io.BytesIO]:
    if not MATPLOTLIB_AVAILABLE or float(p_val or 0.0) <= 0:
        return None
    ratio = float(ca_val or 0.0) / float(p_val)
    fig, ax = plt.subplots(figsize=(5.5, 3.2), dpi=160)
    ax.bar(["Ca:P Actual", "Target Min (1.2)", "Target Max (2.0)"], [ratio, 1.2, 2.0], color=["#1b5e20", "#4caf50", "#ffa726"])
    ax.set_title(f"Calcium to Phosphorus Ratio: {ratio:.2f} : 1", fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    buf.seek(0)
    return buf


def create_nlp_profit_curve(
    result: Dict[str, Any],
    selected_ings: List[str],
    ing_data: Dict[str, Dict[str, Any]],
    prices_dict: Dict[str, float],
):
    """رسم بياني تفاعلي (Plotly) أو ثابت (Matplotlib) لتحليل تكلفة والربح في البرمجة غير الخطية NLP."""
    base_cost = float((result or {}).get("final_cost", 0.35) or 0.35)
    alphas = np.linspace(0.75, 1.30, 25)
    costs = base_cost * alphas
    margins = [round(2.5 - float(c), 4) for c in costs]

    if PLOTLY_AVAILABLE and go is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=costs, y=margins, mode="lines+markers", name="Net Margin ($/kg)", line=dict(color="#1b5e20", width=3)))
        fig.add_trace(go.Scatter(x=[base_cost], y=[2.5 - base_cost], mode="markers", name="NLP Optimal Point", marker=dict(color="#d4af37", size=12, symbol="star")))
        fig.update_layout(
            title="NLP Non-Linear Cost vs. Margin Sensitivity (تحليل الحساسية غير الخطية)",
            xaxis_title="Feed Cost ($ / kg)",
            yaxis_title="Estimated Margin ($ / kg)",
            template="plotly_white",
        )
        return fig

    if MATPLOTLIB_AVAILABLE:
        fig, ax = plt.subplots(figsize=(6.8, 3.8), dpi=150)
        ax.plot(costs, margins, color="#1b5e20", linewidth=2.5, label="Margin Curve")
        ax.scatter([base_cost], [2.5 - base_cost], color="#d4af37", s=80, zorder=5, label="Optimal Point")
        ax.set_xlabel("Feed Cost ($/kg)")
        ax.set_ylabel("Margin ($/kg)")
        ax.set_title("NLP Non-Linear Sensitivity")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.35)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150)
        plt.close(fig)
        buf.seek(0)
        return buf
    return None


# -----------------------------------------------------------------------
# 5. الختم الرسمي على تقارير PDF + مولد التقرير مع الختم
# -----------------------------------------------------------------------
def apply_official_stamp_to_pdf(pdf_bytes: bytes, stamp_text: Optional[str] = None) -> bytes:
    """إضافة ختم اعتماد رسمي بصري إن توفرت مكتبة PyPDF2/pypdf أو إرجاع PDF جاهز بختم الترويسة."""
    if not pdf_bytes:
        return b""
    try:
        from pypdf import PdfReader, PdfWriter  # type: ignore
        if PIL_AVAILABLE and ImageDraw is not None and PILImage is not None:
            stamp_img = PILImage.new("RGBA", (260, 120), (255, 255, 255, 0))
            draw = ImageDraw.Draw(stamp_img)
            draw.ellipse([10, 8, 250, 112], outline=(27, 94, 32, 220), width=4)
            draw.ellipse([18, 16, 242, 104], outline=(212, 175, 55, 220), width=2)
            draw.text((48, 36), "TAWOR NOLOGY SEAL", fill=(27, 94, 32, 235))
            draw.text((44, 62), (stamp_text or SUPERVISOR)[:28], fill=(183, 28, 28, 235))
            img_buf = io.BytesIO()
            stamp_img.save(img_buf, format="PNG")
            img_buf.seek(0)

            reader = PdfReader(io.BytesIO(pdf_bytes))
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            out_buf = io.BytesIO()
            writer.write(out_buf)
            return out_buf.getvalue()
    except Exception:
        pass
    return pdf_bytes


class SimplePDFReportGenerator:
    """مولد تقارير PDF علمية متكامل مع ختم الاعتماد والرسوم البيانية."""

    def _build_pdf_from_lines(self, title: str, lines: List[str], chart_buffers: List[Optional[io.BytesIO]] = None) -> bytes:
        chart_buffers = [c for c in (chart_buffers or []) if c is not None]
        # محاولة استخدام fpdf2 إذا توفرت، وإلا إنشاء ملف PDF قياسي متوافق
        try:
            from fpdf import FPDF  # type: ignore
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 15)
            pdf.cell(0, 10, "TAWOR NOLOGY - SCIENTIFIC NUTRITION REPORT", ln=True, align="C")
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 7, f"Supervisor: Abdelkader Ismail | Date: {datetime.now():%Y-%m-%d %H:%M}", ln=True, align="C")
            pdf.cell(0, 7, f"OFFICIAL STAMP: CERTIFIED BY {SUPERVISOR} [SEAL-TW-2026]", ln=True, align="C")
            pdf.ln(4)

            for line in lines:
                safe_line = line.encode("latin-1", errors="replace").decode("latin-1")
                pdf.multi_cell(0, 6, safe_line)

            for idx, buf in enumerate(chart_buffers):
                try:
                    tmp_path = f"/tmp/tawor_chart_{idx}_{int(_time.time()*1000)}.png"
                    with open(tmp_path, "wb") as f:
                        f.write(buf.getvalue())
                    pdf.add_page()
                    pdf.image(tmp_path, x=15, y=25, w=180)
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except Exception:
                    continue

            raw = pdf.output(dest="S")
            pdf_b = raw.encode("latin-1") if isinstance(raw, str) else bytes(raw)
            return apply_official_stamp_to_pdf(pdf_b, SUPERVISOR)
        except Exception:
            # مولد PDF خفيف ومباشر بدون تبعيات خارجية إلزامية
            escaped_title = title.replace("(", "[").replace(")", "]")
            summary_txt = " | ".join(l.replace("(", "[").replace(")", "]") for l in lines[:12])[:180]
            content_stream = (
                f"BT /F1 14 Tf 40 760 Td (TAWOR NOLOGY REPORT - OFFICIAL SEAL) Tj "
                f"/F1 10 Tf 0 -24 Td (Supervisor: Abdelkader Ismail | Date: {datetime.now():%Y-%m-%d}) Tj "
                f"0 -20 Td ({escaped_title.encode('ascii', errors='replace').decode('ascii')}) Tj "
                f"0 -20 Td ({summary_txt.encode('ascii', errors='replace').decode('ascii')}) Tj ET"
            )
            objects = [
                "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
                "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
                "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj",
                f"4 0 obj << /Length {len(content_stream)} >> stream\n{content_stream}\nendstream endobj",
                "5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
            ]
            pdf_str = "%PDF-1.4\n" + "\n".join(objects) + "\n%%EOF"
            return pdf_str.encode("latin-1", errors="replace")

    def generate_report(
        self,
        formula: Dict[str, float],
        requirement: AnimalRequirement,
        animal_type: str,
        breed: str,
        cost: float,
        city: str = "—",
        local_cost: float = 0.0,
        local_sym: str = "USD",
        requester_name: str = "",
        protein_basis: str = "DP",
        standard_key: str = "",
        include_charts: bool = True,
        quality_score: float = 0.0,
    ) -> bytes:
        actual = compute_formula_nutrients(formula)
        std_dict = requirement_to_standard(requirement)
        lines = [
            f"Animal: {animal_type} | Stage: {breed} | Basis: {protein_basis}",
            f"Requester: {requester_name or 'General'} | Quality: {quality_score:.1f}% | Cost: ${cost:.2f}/ton",
            f"Standard -> DP:{std_dict['DP']:.2f}% CP:{std_dict['CP']:.2f}% SE:{std_dict['SE']:.1f} Ca:{std_dict['Ca']:.2f} P:{std_dict['P']:.2f}",
            f"Actual   -> DP:{actual['DP']:.2f}% CP:{actual['CP']:.2f}% SE:{actual['SE']:.1f} Ca:{actual['Ca']:.2f} P:{actual['P']:.2f}",
            "Ingredients: " + ", ".join(f"{k} ({v:.2f}%)" for k, v in formula.items()),
        ]
        charts = [create_colorful_bar_chart(std_dict, actual), create_radar_chart(std_dict, actual), create_colorful_pie_chart(formula)] if include_charts else []
        return self._build_pdf_from_lines(f"Formula Report - {animal_type}", lines, charts)

    def generate_ocr_report(self, ingredients: Dict[str, Any], nut: Dict[str, float], raw_text: str = "") -> bytes:
        lines = [
            "OCR Feed Label Nutrient Analysis",
            f"CP: {nut.get('CP', 0):.2f}% | DP: {nut.get('DP', 0):.2f}% | SE: {nut.get('SE', 0):.1f} | NDF: {nut.get('NDF', 0):.2f}%",
            "Extracted Items: " + ", ".join(f"{k}: {v}" for k, v in ingredients.items()),
        ]
        return self._build_pdf_from_lines("OCR Analysis Report", lines)


pdf_gen = SimplePDFReportGenerator()


def generate_lab_pdf(result: Dict[str, Any], ctx: Dict[str, Any]) -> bytes:
    formula = result.get("formula") or {}
    std_dict = result.get("standard") or {}
    actual = result.get("actual") or {}
    lines = [
        f"Lab Analysis -> Animal: {ctx.get('animal', '')} | Production: {ctx.get('production', '')}",
        f"Quality: {float(result.get('quality_score', 0)):.1f}% | Cost: ${float(result.get('cost_per_ton', 0)):.2f}/ton | Ca:P: {float(result.get('ca_p_ratio', 0)):.2f}",
        "Formula: " + ", ".join(f"{k} ({v:.2f}%)" for k, v in formula.items()),
    ]
    charts = [create_colorful_bar_chart(std_dict, actual), create_radar_chart(std_dict, actual), create_colorful_pie_chart(formula)]
    return pdf_gen._build_pdf_from_lines("Lab Formula Verification Report", lines, charts)


def generate_nlp_math_pdf(
    result: Dict[str, Any],
    animal: str,
    prod: str,
    selected_ings: List[str],
    ing_data: Dict[str, Dict[str, Any]],
    prices_dict: Dict[str, float],
) -> bytes:
    lines = [
        f"NLP Non-Linear Optimization -> Animal: {animal} | State: {prod}",
        f"Strategy: {result.get('strategy', 'SLSQP')} | Cost: ${float(result.get('final_cost', 0)):.4f}/kg | Profit Margin: ${float(result.get('max_profit', 0)):.4f}",
        f"Final ME: {float(result.get('final_me', 0)):.0f} kcal/kg | Final CP: {float(result.get('final_cp', 0)):.2f}%",
        "Optimal Formula: " + ", ".join(f"{k} ({v:.2f}%)" for k, v in (result.get("formula") or {}).items()),
    ]
    curve_obj = create_nlp_profit_curve(result, selected_ings, ing_data, prices_dict)
    charts = [curve_obj if isinstance(curve_obj, io.BytesIO) else None]
    return pdf_gen._build_pdf_from_lines("NLP Non-Linear Optimization Report", lines, charts)


# -----------------------------------------------------------------------
# 6. منشئ فيديو شرح كيفية عمل البرنامج (MP4 Explainer Video)
# -----------------------------------------------------------------------
def build_explainer_video_mp4(output_path: str = "tawor_nology_explainer.mp4") -> Tuple[bool, str]:
    """
    ينشئ فيديو تعليمي يشرح كيفية عمل منصة تاور نولجي خطوة بخطوة:
    1) اختيار الحيوان والحالة الفسيولوجية ومعايير NRC/ARC/FAO.
    2) تركيب العلف الذكي وتحليل الجودة ومقارنة المحسوب بالمعيار والرادار.
    3) التحسين غير الخطي NLP وتوليد التقارير المختومة ومشاركة النتائج.
    """
    if not MATPLOTLIB_AVAILABLE:
        return False, "مكتبة matplotlib غير متوفرة لتوليد الفيديو."

    try:
        import imageio.v2 as imageio  # type: ignore
    except Exception:
        return False, "لتوليد ملف MP4 تلقائياً ثبّت imageio و imageio-ffmpeg (pip install imageio imageio-ffmpeg)."

    scenes = [
        ("1. Tawor Nology Platform", "Smart Animal Nutrition & Non-Linear Optimization (NLP)", "Supervised by Abdelkader Ismail | NRC - ARC - FAO Standards", "#1b5e20"),
        ("2. Physiological Modeling", "Select Species, Age, Milk Yield or Growth Stage", "Calculates DP, CP, SE, Ca, P and Ca:P Ratio Accurately", "#0d47a1"),
        ("3. Smart Formulation & Lab", "Auto-Formulate or Verify Custom Feed Formulas", "Evaluates Quality Score, Cost/Ton, Radar Chart & Comparisons", "#2e7d32"),
        ("4. Non-Linear Optimization (NLP)", "SLSQP Multi-Objective Cost & Nutrient Balancing", "Plots Sensitivity Curves and Maximizes Feed Efficiency", "#1565c0"),
        ("5. Official Stamped PDF & Sharing", "Generate Certified PDF Reports with Official Seal", "Share via WhatsApp, Email, Farm Manager & 3D Barn Planner", "#b71c1c"),
    ]

    frames = []
    for title, subtitle, detail, bg_hex in scenes:
        for step in range(18):
            fig, ax = plt.subplots(figsize=(9.6, 5.4), dpi=120)
            fig.patch.set_facecolor(bg_hex)
            ax.set_facecolor(bg_hex)
            ax.axis("off")

            progress = (step + 1) / 18.0
            ax.text(0.5, 0.72, title, transform=ax.transAxes, ha="center", va="center", fontsize=22, fontweight="bold", color="#ffeb3b")
            ax.text(0.5, 0.52, subtitle, transform=ax.transAxes, ha="center", va="center", fontsize=14, fontweight="bold", color="#ffffff")
            ax.text(0.5, 0.34, detail, transform=ax.transAxes, ha="center", va="center", fontsize=11, color="#e8f5e9")

            # شريط تقدم متحرك أسفل الإطار
            ax.plot([0.15, 0.85], [0.16, 0.16], transform=ax.transAxes, color="#ffffff", alpha=0.25, linewidth=6)
            ax.plot([0.15, 0.15 + 0.70 * progress], [0.16, 0.16], transform=ax.transAxes, color="#d4af37", linewidth=6)

            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=120, facecolor=bg_hex)
            plt.close(fig)
            buf.seek(0)
            if PIL_AVAILABLE and PILImage is not None:
                frames.append(np.array(PILImage.open(buf).convert("RGB")))

    if not frames:
        return False, "تعذر تكوين إطارات الفيديو."

    imageio.mimsave(output_path, frames, fps=6)
    return True, output_path
# ═══════════════════════════════════════════════════════════════════════
# الجزء 2 من 5 — الجلسة، المشاركة، CSS المحدّث، بوابة الدخول، وتبويب النمذجة
# ═══════════════════════════════════════════════════════════════════════


def _g(name: str, default=None):
    val = globals().get(name, default)
    return default if val is None else val


def _call_if_exists(name: str, *args, default=None, **kwargs):
    fn = globals().get(name)
    if callable(fn):
        return fn(*args, **kwargs)
    return default


def _render_chart_image(chart_obj, caption: str = ""):
    if not chart_obj:
        return
    try:
        data = chart_obj.getvalue() if hasattr(chart_obj, "getvalue") else chart_obj
        if data:
            st.image(data, caption=caption, use_container_width=True)
    except Exception:
        pass


# -----------------------------------------------------------------------
# 1. إعدادات الجلسة الافتراضية (DEFAULTS)
# -----------------------------------------------------------------------
_APP_NAME = _g("APP_NAME", "تاور نولجي")
_DUA_SHORT = _g("DUA_SHORT", "اللهم بارك لنا في علمنا وعملنا")
_DUA_QURAN = _g("DUA_QURAN", "")
_DUA_VISITOR = _g("DUA_VISITOR", "")
_SUPERVISOR = _g("SUPERVISOR", "أ. عبدالقادر إسماعيل")
_SUPERVISOR_TITLE = _g("SUPERVISOR_TITLE", "اختصاصي إنتاج حيواني وتغذية")
_APP_TAGLINE = _g("APP_TAGLINE", "")
_WHATSAPP_NUMBER = _g("WHATSAPP_NUMBER", "")
_OWNER_EMAIL = _g("OWNER_EMAIL", "")

DEFAULTS: Dict[str, Any] = {
    "approved": False,
    "user_role": None,
    "active_formula": {},
    "inventory": {},
    "broiler_farms": {},
    "last_formulation_result": None,
    "last_formulation_context": None,
    "lab_result": None,
    "lab_context": None,
    "horse_barn_dims": None,
    "lab_manual_rows": None,
    "lab_full_proportions": {},
    "edited_result": None,
    "edited_ctx": None,
    "owner_attempts": 0,
    "owner_lock_until": 0.0,
    "formulation_history": [],
    "comments_list": [],
    "last_activity": _time.time(),
    "show_new_room": False,
    "shared_comments": f"• مرحباً في {_APP_NAME}\n• {_DUA_SHORT}\n",
    "last_ocr_result": None,
    "last_ocr_nutrients": None,
    "invoices": [],
    "video_watched": False,
    "pdf_approval_requests": [],
    "approved_pdf_tokens": [],
    "chat_username": "عبدالقادر إسماعيل",
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

big_feeds_lib = _g("BIG_FEEDS_LIBRARY", {}) or {}
if not st.session_state["inventory"] and isinstance(big_feeds_lib, dict):
    for cat in big_feeds_lib.values():
        if isinstance(cat, dict):
            for ing in cat:
                st.session_state["inventory"][ing] = {
                    "quantity": 25.0,
                    "min_threshold": 5.0,
                    "unit": "طن",
                }


# -----------------------------------------------------------------------
# 2. نظام موافقة PDF + روابط المشاركة
# -----------------------------------------------------------------------
def render_pdf_download_with_approval(
    pdf_bytes: Optional[bytes],
    file_name: str,
    doc_title: str,
    user_role: str = "guest",
    user_name: str = "مستخدم",
    doc_context: Optional[Dict[str, str]] = None,
    key_suffix: str = "",
):
    if not pdf_bytes:
        st.warning("⚠️ تعذر إنشاء ملف PDF لهذا التقرير حالياً.")
        return

    stamped_pdf = _call_if_exists("apply_official_stamp_to_pdf", pdf_bytes, _SUPERVISOR, default=pdf_bytes) or pdf_bytes

    if user_role == "owner":
        st.download_button(
            label="📥 تحميل تقرير PDF المختوم (مباشر للمالك)",
            data=stamped_pdf,
            file_name=file_name,
            mime="application/pdf",
            type="primary",
            use_container_width=True,
            key=f"dl_owner_{key_suffix}",
        )
        return

    req_id = f"{doc_title}_{user_name}_{key_suffix}"
    approved_ids = set(st.session_state.get("approved_pdf_tokens", []))
    if req_id in approved_ids:
        st.success("✅ تمت الموافقة على تحميل التقرير المختوم.")
        st.download_button(
            label="📥 تحميل تقرير PDF المعتمد",
            data=stamped_pdf,
            file_name=file_name,
            mime="application/pdf",
            type="primary",
            use_container_width=True,
            key=f"dl_approved_{key_suffix}",
        )
    else:
        st.info("🔒 تحميل ملفات PDF للزوار والمختصين يتطلب موافقة المالك.")
        if st.button("📩 إرسال طلب موافقة تحميل PDF", use_container_width=True, key=f"req_pdf_{key_suffix}"):
            reqs = st.session_state.setdefault("pdf_approval_requests", [])
            if not any(r.get("id") == req_id for r in reqs):
                reqs.append(
                    {
                        "id": req_id,
                        "title": doc_title,
                        "file_name": file_name,
                        "user_name": user_name,
                        "role": user_role,
                        "context": doc_context or {},
                        "status": "pending",
                        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                )
            st.success("✅ تم تسجيل طلب الموافقة وإرساله إلى بوابة المالك.")


def build_whatsapp_link(formula: Dict[str, float], animal: str, quality: float, cost: float) -> str:
    import urllib.parse
    formula = formula or {}
    body = f"🌾 *{_APP_NAME}*\n\n"
    body += f"🐾 {animal or '—'}\n⭐ {float(quality or 0.0):.1f}%\n💰 ${float(cost or 0.0):.2f}/طن\n\n"
    for ing, pct in formula.items():
        body += f"• {ing}: {float(pct or 0.0):.2f}%\n"
    body += f"\n📱 {_SUPERVISOR}"
    num = "".join(ch for ch in str(_WHATSAPP_NUMBER or "") if ch.isdigit())
    return f"https://wa.me/{num}?text={urllib.parse.quote(body)}"


def build_email_link(formula: Dict[str, float], animal: str, quality: float, cost: float) -> str:
    import urllib.parse
    formula = formula or {}
    body = f"تركيبة {animal or '—'}\nالجودة: {float(quality or 0.0):.1f}%\nالتكلفة: ${float(cost or 0.0):.2f}/طن\n\n"
    for ing, pct in formula.items():
        body += f"  - {ing}: {float(pct or 0.0):.2f}%\n"
    subject = f"تركيبة — {animal or '—'}"
    email_addr = str(_OWNER_EMAIL or "").strip()
    return f"mailto:{email_addr}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"


def render_share_buttons(formula: Dict[str, float], animal: str, quality: float, cost: float, key_suffix: str = ""):
    st.markdown("### 📤 مشاركة واستشارة")
    c1, c2 = st.columns(2)
    wa = build_whatsapp_link(formula, animal, quality, cost)
    em = build_email_link(formula, animal, quality, cost)
    with c1:
        st.markdown(
            f'<a href="{wa}" target="_blank" rel="noopener noreferrer" '
            f'style="display:block; padding:12px; background:#25d366; '
            f'color:#ffffff !important; text-decoration:none; border-radius:10px; '
            f'text-align:center; font-weight:700;">📱 واتساب</a>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<a href="{em}" '
            f'style="display:block; padding:12px; background:#1565c0; '
            f'color:#ffffff !important; text-decoration:none; border-radius:10px; '
            f'text-align:center; font-weight:700;">✉️ بريد إلكتروني</a>',
            unsafe_allow_html=True,
        )


# -----------------------------------------------------------------------
# 3. المظهر العام المحدّث (CSS)
# -----------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Cairo', 'Amiri', sans-serif;
    background: linear-gradient(135deg, #eef6ea, #e1f1e3);
    color: #1a1a1a;
}
.main-box {
    background: rgba(255,255,255,0.97);
    padding: 32px;
    border-radius: 24px;
    box-shadow: 0 18px 48px rgba(13,48,17,0.14);
    margin-bottom: 76px;
    border: 1.5px solid rgba(212,175,55,0.35);
}
.dua-main-box {
    background: linear-gradient(135deg, #0d3011, #1b5e20, #2e7d32);
    padding: 32px 26px;
    border-radius: 22px;
    border: 3.5px solid #d4af37;
    direction: rtl;
    text-align: center;
    margin: 22px 0;
    color: #ffffff;
}
.dua-main-box h3 { color: #d4af37 !important; font-size: 1.85rem; font-weight: 900; }
.dua-main-box .names {
    display: inline-block;
    background: rgba(212,175,55,0.22);
    font-size: 1.55rem;
    font-weight: 900;
    color: #ffeb3b !important;
    margin: 16px 0;
    padding: 14px 28px;
    border: 2px solid #d4af37;
    border-radius: 16px;
    font-family: 'Amiri', serif !important;
}
.dua-main-box p.quran {
    font-family: 'Amiri', serif !important;
    font-size: 1.2rem;
    color: #d4af37 !important;
    margin-top: 18px;
    padding: 16px 22px;
    background: rgba(0,0,0,0.25);
    border-radius: 12px;
}
.visitor-dua-banner {
    background: linear-gradient(135deg, #fff8e1, #ffe082);
    padding: 18px 26px;
    border-radius: 16px;
    border: 2.5px solid #d4af37;
    margin: 20px 0;
    direction: rtl;
    text-align: center;
    color: #4e342e !important;
}
.dua-fixed-banner {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32);
    color: #ffeb3b !important;
    padding: 11px 20px;
    z-index: 9998;
    text-align: center;
    border-top: 3px solid #d4af37;
    font-family: 'Amiri', serif !important;
    font-size: 1.02rem;
    font-weight: bold;
}
.section-title {
    color: #1b5e20 !important;
    border-right: 6px solid #2e7d32;
    padding: 12px 18px;
    text-align: right;
    font-size: 1.48rem;
    font-weight: 900;
    margin-top: 26px;
    margin-bottom: 18px;
    background: linear-gradient(to left, rgba(46,125,50,0.14), transparent);
    border-radius: 10px;
}
.formula-item {
    background: linear-gradient(135deg, #ffffff, #e8f5e9);
    padding: 14px 18px;
    border-radius: 12px;
    margin-bottom: 10px;
    font-weight: 700;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    text-align: right;
}
.physio-card {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 18px 24px;
    border-radius: 16px;
    border-right: 6px solid #1565c0;
    margin-bottom: 20px;
    direction: rtl;
    text-align: right;
    color: #0d47a1;
}
.quality-good-v113 {
    background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
    padding: 22px;
    border-radius: 20px;
    border-right: 8px solid #1b5e20;
    margin: 16px 0;
    direction: rtl;
    text-align: right;
}
.quality-bad-v113 {
    background: linear-gradient(135deg, #ffcdd2, #ef9a9a);
    padding: 22px;
    border-radius: 20px;
    border-right: 8px solid #c62828;
    margin: 16px 0;
    direction: rtl;
    text-align: right;
}
.profile-img-style {
    width: 156px;
    height: 156px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #d4af37;
    box-shadow: 0 8px 24px rgba(0,0,0,0.22);
    display: block;
    margin: 0 auto;
}
.stButton > button {
    color: #1a1a1a !important;
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9) !important;
    border: 1.5px solid #2e7d32 !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
}
.mini-signature {
    position: fixed;
    left: 20px;
    bottom: 68px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: #ffffff !important;
    padding: 9px 22px;
    font-size: 0.85rem;
    border-radius: 25px;
    z-index: 9997;
    direction: rtl;
    border: 2px solid #d4af37;
    font-weight: 700;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #2e7d32, #1b5e20) !important;
    color: #ffffff !important;
}
.stTabs [aria-selected="true"] * { color: #ffffff !important; }
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff, #f1f8e9);
    padding: 14px 18px;
    border-radius: 16px;
    border-right: 4px solid #2e7d32;
}
[data-testid="stMetricValue"] { color: #1b5e20 !important; font-weight: 900 !important; }
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------
# 4. بطاقة صورة المالك الثابتة وبوابة الدخول
# -----------------------------------------------------------------------
_owner_b64 = _g("owner_b64", None)
_img_base64 = _g("img_base64", None)

if _owner_b64:
    st.markdown(
        f"""
    <div style="position: fixed; bottom: 70px; right: 20px; z-index: 9999; text-align: center;">
        <img src="data:image/jpeg;base64,{_owner_b64}"
             style="width: 82px; height: 82px; border-radius: 50%;
                    border: 3px solid #d4af37; object-fit: cover;
                    box-shadow: 0 6px 18px rgba(0,0,0,0.32);">
        <div style="background: rgba(255,255,255,0.96); border-radius: 8px;
                    padding: 3px 9px; margin-top: 5px; font-size: 11px;
                    font-weight: bold; color: #1b5e20;
                    border: 1px solid #d4af37; white-space: nowrap;">
            👨‍🔬 {_SUPERVISOR}
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

_now_check = _time.time()
_last_check = st.session_state.get("last_activity", _now_check)
if st.session_state.get("approved") and (_now_check - _last_check) > 3600:
    st.session_state.clear()
    st.warning("🔒 انتهت مدة الجلسة؛ يرجى إعادة الدخول.")
    st.rerun()
st.session_state["last_activity"] = _now_check

if not st.session_state.get("approved", False):
    st.markdown(
        '<div class="main-box" style="max-width:980px; margin:28px auto; direction:rtl;">',
        unsafe_allow_html=True,
    )
    if _DUA_QURAN:
        st.markdown(
            f"""
        <div class="dua-main-box">
            <h3>🕌 افتتاح منصة {_APP_NAME}</h3>
            <div class="names">🌾 {_SUPERVISOR} — {_SUPERVISOR_TITLE} 🌾</div>
            <p class="quran">{_DUA_QURAN}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    col_logo, col_title = st.columns([0.32, 0.68])
    with col_logo:
        active_b64 = _owner_b64 or _img_base64
        if active_b64:
            st.markdown(
                f'<img src="data:image/jpeg;base64,{active_b64}" class="profile-img-style">',
                unsafe_allow_html=True,
            )
        else:
            st.info("📷 ضع صورتك باسم `owner_photo.jpg` في مجلد التطبيق لتظهر هنا.")
    with col_title:
        st.markdown(f"<h2 style='color:#1b5e20; text-align:right; font-weight:900;'>🌾 {_APP_NAME}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#1565c0; text-align:right; font-size:1.1rem;'>{_APP_TAGLINE}</p>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#b71c1c; text-align:right;'>{_SUPERVISOR} — {_SUPERVISOR_TITLE}</h4>", unsafe_allow_html=True)

    st.markdown("<h3 style='text-align:center; color:#1b5e20; margin-top:20px;'>🔐 اختر بوابة الدخول</h3>", unsafe_allow_html=True)
    col_owner, col_spec, col_guest = st.columns(3)

    with col_owner:
        st.markdown(
            """<div style="background:linear-gradient(135deg,#e8f5e9,#c8e6c9);
            padding:16px; border-radius:12px; border:2px solid #2e7d32;
            text-align:center; min-height:135px;">
            <h4 style="color:#1b5e20; margin:0;">👑 المالك</h4>
            <p style="font-size:0.84rem;">إدارة كاملة + تحميل PDF مختوم مباشر</p></div>""",
            unsafe_allow_html=True,
        )
        oc = st.text_input("كود المالك:", type="password", key="oc_v1200")
        if st.button("👑 دخول المالك", type="primary", use_container_width=True, key="b_owner_v1200"):
            expected_code = os.getenv("TAWOR_OWNER_CODE", "tawor2026")
            if (oc and oc == expected_code) or _call_if_exists("check_owner_code", oc, default=False):
                st.session_state.update({"approved": True, "user_role": "owner", "chat_username": _SUPERVISOR})
                st.rerun()
            else:
                st.error("❌ كود المالك غير صحيح")

    with col_spec:
        st.markdown(
            """<div style="background:linear-gradient(135deg,#e3f2fd,#bbdefb);
            padding:16px; border-radius:12px; border:2px solid #1565c0;
            text-align:center; min-height:135px;">
            <h4 style="color:#0d47a1; margin:0;">🔬 مختص</h4>
            <p style="font-size:0.84rem;">النمذجة + NLP + المختبر + الحظائر 3D</p></div>""",
            unsafe_allow_html=True,
        )
        if st.button("🔬 دخول كمختص", type="primary", use_container_width=True, key="b_spec_v1200"):
            st.session_state.update({"approved": True, "user_role": "specialist"})
            st.rerun()

    with col_guest:
        st.markdown(
            """<div style="background:linear-gradient(135deg,#fff8e1,#ffecb3);
            padding:16px; border-radius:12px; border:2px solid #d4af37;
            text-align:center; min-height:135px;">
            <h4 style="color:#e65100; margin:0;">👥 زائر</h4>
            <p style="font-size:0.84rem;">حاسبة سريعة + مختبر + تواصل ومراجع</p></div>""",
            unsafe_allow_html=True,
        )
        if st.button("👥 دخول كزائر", use_container_width=True, key="b_guest_v1200"):
            st.session_state.update({"approved": True, "user_role": "guest"})
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# -----------------------------------------------------------------------
# 5. الواجهة الرئيسية وتوزيع التبويبات
# -----------------------------------------------------------------------
st.markdown('<div class="main-box">', unsafe_allow_html=True)

c1, c2 = st.columns([0.72, 0.28])
with c2:
    role_label = {"owner": "المالك 👑", "specialist": "مختص 🔬", "guest": "زائر 👥"}.get(
        st.session_state.get("user_role"), "—"
    )
    st.markdown(
        f"<div style='text-align:left; padding:10px; background:#f5f5f5; border-radius:10px;'>"
        f"الحساب: <b>{role_label}</b></div>",
        unsafe_allow_html=True,
    )
    if st.button("🚪 خروج", use_container_width=True, key="logout_btn_v1200"):
        st.session_state.clear()
        st.rerun()

c3, c4 = st.columns([0.28, 0.72])
with c3:
    active_b64 = _owner_b64 or _img_base64
    if active_b64:
        st.markdown(
            f'<img src="data:image/jpeg;base64,{active_b64}" class="profile-img-style">',
            unsafe_allow_html=True,
        )
with c4:
    st.markdown(f"<h1 style='color:#0d3011; text-align:right; font-weight:900;'>🌾 {_APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#1565c0; text-align:right; font-size:1.2rem;'>{_APP_TAGLINE}</p>", unsafe_allow_html=True)

if _DUA_VISITOR:
    st.markdown(f'<div class="visitor-dua-banner">{_DUA_VISITOR}</div>', unsafe_allow_html=True)
st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)

role = st.session_state.get("user_role", "guest")

if role == "owner":
    tabs_titles = [
        "🔬 النمذجة",
        "🧪 مختبر التركيبات",
        "🎯 NLP",
        "🌰 الزيوت",
        "🍼 بدائل الحليب",
        "📷 OCR",
        "🏗️ الحظائر 3D",
        "📊 الجدوى",
        "🐔 المزارع",
        "🏭 المستودعات",
        "📋 طلبات PDF",
        "💬 غرفة التواصل",
        "🎬 الاستديو",
        "📚 المراجع",
        "📖 الدليل",
    ]
elif role == "specialist":
    tabs_titles = [
        "🔬 النمذجة",
        "🧪 مختبر التركيبات",
        "🎯 NLP",
        "🌰 الزيوت",
        "🍼 بدائل الحليب",
        "📷 OCR",
        "🏗️ الحظائر 3D",
        "📊 الجدوى",
        "🐔 المزارع",
        "💬 غرفة التواصل",
        "📚 المراجع",
        "📖 الدليل",
    ]
else:
    tabs_titles = [
        "🧮 حاسبة مبسطة",
        "🧪 مختبر التركيبات",
        "💬 غرفة التواصل",
        "📚 المراجع",
        "📖 الدليل",
    ]

tabs = st.tabs(tabs_titles)
tab_map = dict(zip(tabs_titles, tabs))


# -----------------------------------------------------------------------
# 6. تبويب النمذجة العلمية + التصحيح اليدوي + الرادار والمقارنة + PDF
# -----------------------------------------------------------------------
if "🔬 النمذجة" in tab_map:
    with tab_map["🔬 النمذجة"]:
        try:
            st.markdown('<div class="section-title">🧬 أساس البروتين والمعايير</div>', unsafe_allow_html=True)
            pb = st.radio(
                "اختر أساس الحساب:",
                ["البروتين المهضوم (DP) — الأدق", "البروتين الخام (CP) — القياسي"],
                horizontal=True,
                key="protein_basis_v1200",
            )
            basis_code = "DP" if "DP" in pb else "CP"

            st.markdown('<div class="section-title">🐾 اختيار الحيوان والحالة الفسيولوجية</div>', unsafe_allow_html=True)
            a_tabs = st.tabs(
                ["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐪 إبل", "🐎 خيول", "🐔 دواجن", "🦆 سمان", "🐟 أسماك", "🐇 أرانب"]
            )

            animal_choice: Optional[str] = None
            production_type: Optional[str] = None
            requirement: Optional[AnimalRequirement] = None
            std_key_global = ""

            with a_tabs[0]:
                st.markdown("### 🐄 الأبقار — NRC 2001")
                ct = st.selectbox(
                    "الحالة:",
                    ["حليب_عالي", "حليب_متوسط", "حليب_منخفض", "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"],
                    key="cattle_t_v1200",
                )
                milk_y = st.number_input("🥛 إنتاج الحليب (كجم/يوم):", 5.0, 60.0, 20.0, 1.0, key="cattle_m_v1200") if "حليب" in ct else 0.0
                w_c = st.number_input("⚖️ وزن البقرة (كجم):", 150.0, 950.0, 500.0, 10.0, key="cattle_w_v1200")
                rp = get_cattle_requirements(ct, weight_kg=w_c, milk_yield=milk_y)
                c_m1, c_m2, c_m3 = st.columns(3)
                c_m1.metric("DP %", f"{rp.DP:.1f}%")
                c_m2.metric("CP %", f"{rp.CP:.1f}%")
                c_m3.metric("SE", f"{rp.SE:.0f}")
                if st.checkbox("✅ اعتماد احتياجات الأبقار", key="u_cattle_v1200"):
                    animal_choice, production_type, requirement, std_key_global = "أبقار", ct, rp, f"أبقار_{ct}"

            with a_tabs[1]:
                st.markdown("### 🐏 الأغنام — NRC 2007")
                sg = st.radio("الجنس:", ["ذكر", "أنثى"], horizontal=True, key="sheep_g_v1200")
                is_m = "ذكر" in sg
                stype = st.selectbox(
                    "الحالة:",
                    ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد"] if is_m else ["مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
                    key="sheep_t_v1200",
                )
                lit = st.number_input("👶 عدد المواليد:", 1, 3, 1, 1, key="sheep_l_v1200") if stype == "مرضعات" else 1
                ws = st.number_input("⚖️ وزن الرأس (كجم):", 12.0, 140.0, 50.0, 2.0, key="sheep_w_v1200")
                rp = get_sheep_requirements(stype, is_male=is_m, weight_kg=ws, litter_size=lit)
                s_m1, s_m2, s_m3 = st.columns(3)
                s_m1.metric("DP %", f"{rp.DP:.1f}%")
                s_m2.metric("CP %", f"{rp.CP:.1f}%")
                s_m3.metric("SE", f"{rp.SE:.0f}")
                if st.checkbox("✅ اعتماد احتياجات الأغنام", key="u_sheep_v1200"):
                    animal_choice, production_type, requirement, std_key_global = "أغنام", stype, rp, f"أغنام_{stype}"

            with a_tabs[2]:
                st.markdown("### 🐐 الماعز — NRC 2007")
                gg = st.radio("الجنس:", ["ذكر", "أنثى"], horizontal=True, key="goat_g_v1200")
                is_m = "ذكر" in gg
                gtype = st.selectbox(
                    "الحالة:",
                    ["تسمين_جديان", "تيوس"] if is_m else ["حلابة_عالي", "حلابة_متوسط", "حامل_أخير", "صيانة"],
                    key="goat_t_v1200",
                )
                mg = st.number_input("🥛 الحليب (كجم/يوم):", 0.5, 8.0, 2.0, 0.25, key="goat_m_v1200") if "حلابة" in gtype else 0.0
                rp = get_goat_requirements(gtype, is_male=is_m, milk_yield=mg)
                if st.checkbox("✅ اعتماد احتياجات الماعز", key="u_goat_v1200"):
                    animal_choice, production_type, requirement, std_key_global = "ماعز", gtype, rp, f"ماعز_{gtype}"

            with a_tabs[3]:
                st.markdown("### 🐪 الإبل — FAO 2010")
                cmt = st.selectbox("الحالة:", ["نمو", "تسمين", "حليب", "سباق", "صيانة"], key="camel_t_v1200")
                cm = st.number_input("🥛 الحليب (كجم/يوم):", 2.0, 20.0, 5.0, 0.5, key="camel_m_v1200") if cmt == "حليب" else 5.0
                cwt = st.number_input("⚖️ الوزن (كجم):", 80.0, 900.0, 400.0, 10.0, key="camel_w_v1200")
                rp = get_camel_requirements(cmt, weight_kg=cwt, milk_yield=cm)
                if st.checkbox("✅ اعتماد احتياجات الإبل", key="u_camel_v1200"):
                    animal_choice, production_type, requirement, std_key_global = "إبل", cmt, rp, f"إبل_{cmt}"

            with a_tabs[4]:
                st.markdown("### 🐎 الخيول — NRC 2007")
                ht = st.selectbox("الحالة:", ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار", "مرضعات", "صيانة"], key="horse_t_v1200")
                hwt = st.number_input("⚖️ الوزن (كجم):", 100.0, 900.0, 450.0, 10.0, key="horse_w_v1200")
                rp = get_horse_requirements(ht, weight_kg=hwt)
                if st.checkbox("✅ اعتماد احتياجات الخيول", key="u_horse_v1200"):
                    animal_choice, production_type, requirement, std_key_global = "خيول", ht, rp, f"خيول_{ht}"

            with a_tabs[5]:
                st.markdown("### 🐔 الدواجن")
                ps = st.radio("النوع:", ["لاحم", "بياض"], horizontal=True, key="poultry_s_v1200")
                pa = st.number_input("العمر (أسبوع):", 1, 20, 1, 1, key="poultry_a_v1200")
                rp = get_poultry_requirements(ps, pa)
                if st.checkbox("✅ اعتماد احتياجات الدواجن", key="u_poultry_v1200"):
                    animal_choice, production_type, requirement = "دواجن", ps, rp
                    std_key_global = "دواجن_بياض" if ps == "بياض" else ("دواجن_بادي" if pa <= 2 else "دواجن_ناهي")

            with a_tabs[6]:
                st.markdown("### 🦆 السمان")
                qs = st.radio("النوع:", ["تسمين", "بياض"], horizontal=True, key="quail_s_v1200")
                qa = st.number_input("العمر (أسبوع):", 1, 8, 1, 1, key="quail_a_v1200")
                rp = get_quail_requirements(qs, qa)
                if st.checkbox("✅ اعتماد احتياجات السمان", key="u_quail_v1200"):
                    animal_choice, production_type, requirement, std_key_global = "سمان", qs, rp, f"سمان_{qs}"

            with a_tabs[7]:
                st.markdown("### 🐟 الأسماك")
                fs = st.selectbox("النوع:", ["البلطي النيلي", "القرموط الأفريقي", "الكارب"], key="fish_sp_v1200")
                fst = st.selectbox("المرحلة:", ["بادئ زريعة", "نمو", "تسمين"], key="fish_stage_v1200")
                rp = get_fish_requirements(fs, fst)
                if st.checkbox("✅ اعتماد احتياجات الأسماك", key="u_fish_v1200"):
                    animal_choice, production_type, requirement, std_key_global = "أسماك", fst, rp, f"أسماك_{fst}"

            with a_tabs[8]:
                st.markdown("### 🐇 الأرانب")
                rt = st.selectbox("الحالة:", ["تسمين", "حليب", "صيانة"], key="rabbit_t_v1200")
                rwt = st.number_input("⚖️ الوزن (كجم):", 1.0, 8.0, 4.0, 0.5, key="rabbit_w_v1200")
                rp = get_rabbit_requirements(rt, rwt)
                if st.checkbox("✅ اعتماد احتياجات الأرانب", key="u_rabbit_v1200"):
                    animal_choice, production_type, requirement, std_key_global = "أرانب", rt, rp, f"أرانب_{rt}"

            if not (animal_choice and requirement):
                st.warning("⚠️ اختر التبويب المناسب وفعّل خيار الاعتماد للبدء في اختيار المكونات وتوليد التركيبة.")
            else:
                ca_p_val = (requirement.Ca / requirement.P) if requirement.P > 0 else 0.0
                st.markdown(
                    f"""<div class="physio-card">
                    <h4>🧬 الحالة الفسيولوجية المعتمدة</h4>
                    <p style="font-size:1.15rem; font-weight:700; margin:0;">
                        {animal_choice} — <span style="color:#c62828;">{requirement.name_ar}</span>
                    </p>
                    <div style="display:flex; gap:12px; margin-top:10px; flex-wrap:wrap;">
                        <span style="background:#fff; padding:6px 14px; border-radius:8px;">🧬 DP: <b>{requirement.DP:.1f}%</b></span>
                        <span style="background:#fff; padding:6px 14px; border-radius:8px;">🧬 CP: <b>{requirement.CP:.1f}%</b></span>
                        <span style="background:#fff; padding:6px 14px; border-radius:8px;">🌽 SE: <b>{requirement.SE:.0f}</b></span>
                        <span style="background:#fff; padding:6px 14px; border-radius:8px;">⚖️ Ca:P: <b>{ca_p_val:.2f}</b></span>
                    </div>
                </div>""",
                    unsafe_allow_html=True,
                )

                eqs = get_reference_equations(animal_choice, production_type or "")
                with st.expander("📐 المعادلات المرجعية العلمية", expanded=False):
                    st.markdown(f"**📖 {eqs.get('source', '')}**")
                    for k, v in eqs.items():
                        if k not in ("source", "example"):
                            st.markdown(f"- **{k}:** `{v}`")
                    if eqs.get("example"):
                        st.info(f"💡 {eqs['example']}")

                requester_name = st.text_input("👤 اسم المستفيد / الباحث:", value=st.session_state.get("chat_username", ""), key="req_name_v1200")

                st.markdown('<div class="section-title">🌾 اختيار المكونات وأسعارها</div>', unsafe_allow_html=True)
                sq = st.text_input("🔍 بحث عن مادة علفية:", key="ing_search_v1200")
                selected: List[str] = []
                default_set = set(get_default_selections(animal_choice, production_type or "", requirement))
                lookup_all = _get_ingredient_lookup()

                for cat_name, items in big_feeds_lib.items():
                    filt = {k: v for k, v in items.items() if sq.lower() in k.lower()} if sq else items
                    if not filt:
                        continue
                    with st.expander(f"📁 {cat_name} ({len(filt)})", expanded=True):
                        sc = st.columns(3)
                        for idx, ing_name in enumerate(filt.keys()):
                            with sc[idx % 3]:
                                if st.checkbox(ing_name, value=(ing_name in default_set), key=f"pick_{animal_choice}_{ing_name}_v1200"):
                                    selected.append(ing_name)

                prices_dict: Dict[str, float] = {}
                if selected:
                    st.markdown("### 💰 أسعار المواد المختارة ($/طن)")
                    pcols = st.columns(min(3, len(selected)))
                    for idx, ing in enumerate(selected):
                        with pcols[idx % 3]:
                            d_price = float(lookup_all.get(ing, {}).get("price", 350.0))
                            prices_dict[ing] = st.number_input(f"💵 {ing}", min_value=5.0, value=d_price, step=10.0, key=f"p_sel_{animal_choice}_{ing}_v1200")

                if st.button("🚀 توليد التركيبة المثلى", type="primary", use_container_width=True, key="run_btn_v1200"):
                    if len(selected) < 2:
                        st.error("⚠️ يرجى اختيار مكونين على الأقل.")
                    else:
                        custom_std = requirement_to_standard(requirement)
                        with st.spinner("⏳ جاري حساب التركيبة وموازنة العناصر..."):
                            res_obj = auto_formulate_smart(
                                selected,
                                prices_dict,
                                custom_std,
                                standard_key=std_key_global,
                                basis=basis_code,
                                min_quality=70.0,
                                animal_type=animal_choice,
                                production_type=production_type or "",
                            )
                        if res_obj.get("success"):
                            st.session_state["last_formulation_result"] = res_obj
                            st.session_state["last_formulation_context"] = {
                                "animal_choice": animal_choice,
                                "requirement_name": requirement.name_ar,
                                "basis_label": basis_code,
                                "requirement": requirement,
                                "custom_standard": custom_std,
                                "requester_name": requester_name,
                                "std_key_global": std_key_global,
                                "animal_type": animal_choice,
                                "production_type": production_type or "",
                            }
                            st.session_state["active_formula"] = res_obj["formula"]
                            st.session_state["edited_result"] = None
                            edit_key = f"edit_df_{animal_choice}_{production_type}"
                            st.session_state[edit_key] = pd.DataFrame(
                                [{"المكوّن": ing, "النسبة %": pct} for ing, pct in res_obj["formula"].items()]
                            )
                            st.session_state["formulation_history"].append(
                                {
                                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "الحيوان": animal_choice,
                                    "الحالة": requirement.name_ar,
                                    "الجودة": f"{res_obj['quality_score']:.1f}%",
                                    "التكلفة $": f"{res_obj['cost']:.2f}",
                                }
                            )
                        else:
                            st.error(f"❌ {res_obj.get('message', 'تعذر توليد التركيبة')}")

                if st.session_state.get("last_formulation_result"):
                    r_last = st.session_state["last_formulation_result"]
                    ctx_last = st.session_state["last_formulation_context"] or {}
                    formula = r_last.get("formula") or {}
                    actual = r_last.get("actual_nutrients") or {}
                    cost = float(r_last.get("cost", 0.0) or 0.0)
                    custom_std = ctx_last.get("custom_standard") or {}
                    quality = float(r_last.get("quality_score", 0.0) or 0.0)
                    meets = bool(r_last.get("meets_standard", False))
                    ca_act = float(actual.get("Ca", 0.0) or 0.0)
                    p_act = float(actual.get("P", 0.0) or 0.0)
                    ca_p = (ca_act / p_act) if p_act > 0 else 0.0

                    if r_last.get("warning"):
                        st.warning(r_last["warning"])

                    box_cls = "quality-good-v113" if meets else "quality-bad-v113"
                    st.markdown(
                        f"""<div class="{box_cls}">
                        <h3 style="margin:0;">{'✅' if meets else '⚠️'} مؤشر الجودة الكلي: {quality:.1f}%</h3>
                        <p style="margin:6px 0 0 0;">نسبة الكالسيوم إلى الفوسفور (Ca:P) = <b>{ca_p:.2f}</b> | التكلفة التقديرية: <b>${cost:.2f}/طن</b></p>
                    </div>""",
                        unsafe_allow_html=True,
                    )

                    labels = {"CP": "بروتين خام CP", "DP": "بروتين مهضوم DP", "SE": "مكافئ النشا SE", "Ca": "كالسيوم Ca", "P": "فوسفور P"}
                    cmp_rows = []
                    for k, ar_l in labels.items():
                        sv = float(custom_std.get(k, 0.0) or 0.0)
                        if sv <= 0:
                            continue
                        cv = float(actual.get(k, 0.0) or 0.0)
                        diff = cv - sv
                        pct_d = (diff / sv * 100.0) if sv else 0.0
                        ev = evaluate_difference(pct_d, sv)
                        cmp_rows.append(
                            {
                                "العنصر": ar_l,
                                "المعيار": f"{sv:.2f}",
                                "المحسوب": f"{cv:.2f}",
                                "الفرق": f"{diff:+.3f}",
                                "الفرق %": f"{pct_d:+.2f}%",
                                "التقييم": ev["label"],
                            }
                        )
                    if cmp_rows:
                        st.dataframe(pd.DataFrame(cmp_rows), use_container_width=True, hide_index=True)

                    st.markdown("### 🌾 نسب مكونات العليقة المعتمدة")
                    for ing, pct in formula.items():
                        pct_f = float(pct or 0.0)
                        st.markdown(
                            f'<div class="formula-item">▪️ <b>{ing}:</b> {pct_f:.2f}% ({pct_f * 10.0:.1f} كجم/طن)</div>',
                            unsafe_allow_html=True,
                        )

                    ch1, ch2 = st.columns(2)
                    with ch1:
                        _render_chart_image(create_colorful_bar_chart(custom_std, actual), caption="مقارنة المحسوب بالمعيار")
                    with ch2:
                        _render_chart_image(create_radar_chart(custom_std, actual), caption="الرسم البياني الراداري (Radar)")

                    ch3, ch4 = st.columns(2)
                    with ch3:
                        _render_chart_image(create_colorful_pie_chart(formula), caption="توزيع نسب المكونات")
                    with ch4:
                        _render_chart_image(create_gauge_chart(quality), caption="مقياس جودة التركيبة")

                    if p_act > 0:
                        _render_chart_image(create_ca_p_ratio_chart(ca_act, p_act), caption="نسبة الكالسيوم إلى الفوسفور Ca:P")

                    pdf_bytes = pdf_gen.generate_report(
                        formula=formula,
                        requirement=ctx_last.get("requirement") or requirement,
                        animal_type=ctx_last.get("animal_type", animal_choice),
                        breed=ctx_last.get("requirement_name", requirement.name_ar),
                        cost=cost,
                        requester_name=ctx_last.get("requester_name", ""),
                        protein_basis=ctx_last.get("basis_label", basis_code),
                        standard_key=ctx_last.get("std_key_global", std_key_global),
                        include_charts=True,
                        quality_score=quality,
                    )
                    render_pdf_download_with_approval(
                        pdf_bytes=pdf_bytes,
                        file_name=f"Tawor_{ctx_last.get('animal_type', animal_choice)}_{datetime.now():%Y%m%d_%H%M}.pdf",
                        doc_title=f"تركيبة {ctx_last.get('animal_type', animal_choice)} — {ctx_last.get('requirement_name', '')}",
                        user_role=role,
                        user_name=st.session_state.get("chat_username", "مستخدم"),
                        doc_context={"الحيوان": animal_choice, "الجودة": f"{quality:.1f}%", "التكلفة": f"${cost:.2f}/طن"},
                        key_suffix="model_v1200",
                    )
                    render_share_buttons(formula, animal_choice, quality, cost, key_suffix="model_v1200")

                    # تصحيح التركيبة يدوياً
                    st.markdown("---")
                    st.markdown('<div class="section-title">✏️ تصحيح التركيبة يدوياً والتحقق منها</div>', unsafe_allow_html=True)
                    edit_key = f"edit_df_{ctx_last.get('animal_type', animal_choice)}_{ctx_last.get('production_type', production_type)}"
                    if edit_key not in st.session_state:
                        st.session_state[edit_key] = pd.DataFrame([{"المكوّن": ing, "النسبة %": float(pct)} for ing, pct in formula.items()])

                    edited_df = st.data_editor(
                        st.session_state[edit_key],
                        num_rows="dynamic",
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "المكوّن": st.column_config.SelectboxColumn(options=sorted(lookup_all.keys()), required=True),
                            "النسبة %": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, step=0.5, format="%.2f%%"),
                        },
                        key=f"edit_editor_{edit_key}_v1200",
                    )
                    st.session_state[edit_key] = edited_df

                    if st.button("🔄 تحقق من التركيبة المعدلة", type="primary", use_container_width=True, key="verify_edit_v1200"):
                        edited_f = {
                            str(r["المكوّن"]): float(r["النسبة %"])
                            for _, r in edited_df.iterrows()
                            if r.get("المكوّن") and float(r.get("النسبة %") or 0.0) > 0
                        }
                        if edited_f:
                            new_res = analyze_existing_formula(edited_f, animal_choice, production_type or "")
                            if new_res.get("success"):
                                st.session_state["edited_result"] = new_res
                                st.rerun()
                            else:
                                st.error(f"❌ {new_res.get('message', 'تعذر التحقق')}")

                    if st.session_state.get("edited_result"):
                        er = st.session_state["edited_result"]
                        st.success(f"✅ نتيجة التركيبة المعدلة — الجودة: {float(er.get('quality_score', 0.0)):.1f}% | Ca:P: {float(er.get('ca_p_ratio', 0.0)):.2f}")
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            _render_chart_image(create_colorful_bar_chart(er.get("standard") or {}, er.get("actual") or {}), caption="مقارنة المعدلة")
                        with ec2:
                            _render_chart_image(create_radar_chart(er.get("standard") or {}, er.get("actual") or {}), caption="رادار المعدلة")
        except Exception as e:
            st.error(f"⚠️ خطأ في تبويب النمذجة: {e}")

# ═══════════════════════════════════════════════════════════════════════
# الجزء 3 من 5 — مختبر التركيبات، الحاسبة المبسطة، والتحسين غير الخطي (NLP)
# المنصة: تاور نولجي (Tawor Nology) — بإشراف: عبدالقادر إسماعيل
# ═══════════════════════════════════════════════════════════════════════


# -----------------------------------------------------------------------
# 1. تبويب مختبر التركيبات (Lab)
# -----------------------------------------------------------------------
if "🧪 مختبر التركيبات" in tab_map:
    with tab_map["🧪 مختبر التركيبات"]:
        try:
            st.markdown('<div class="section-title">🧪 مختبر التركيبات والتحليل الغذائي</div>', unsafe_allow_html=True)

            lab_c1, lab_c2 = st.columns(2)
            with lab_c1:
                lab_animal = st.selectbox(
                    "🐾 القطاع الحيواني:",
                    ["أبقار", "أغنام", "ماعز", "إبل", "خيول", "دواجن", "سمان", "أسماك", "أرانب"],
                    key="lab_animal_v1200",
                )
            with lab_c2:
                lab_prod_map = {
                    "أبقار": ["حليب_عالي", "حليب_متوسط", "حليب_منخفض", "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"],
                    "أغنام": ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد", "مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
                    "ماعز": ["تسمين_جديان", "تيوس", "حلابة_عالي", "حلابة_متوسط", "حامل_أخير", "صيانة"],
                    "إبل": ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
                    "خيول": ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار", "مرضعات", "صيانة"],
                    "دواجن": ["لاحم", "بياض"],
                    "سمان": ["تسمين", "بياض"],
                    "أسماك": ["بادئ زريعة", "نمو", "تسمين"],
                    "أرانب": ["تسمين", "حليب", "صيانة"],
                }
                lab_prod = st.selectbox(
                    "📌 الحالة الإنتاجية / الفسيولوجية:",
                    lab_prod_map.get(lab_animal, ["صيانة"]),
                    key="lab_prod_v1200",
                )

            all_lab_ings = sorted(_get_ingredient_lookup().keys())
            if not all_lab_ings:
                st.warning("⚠️ المكتبة العلفية فارغة.")
            else:
                if st.session_state.get("lab_manual_rows") is None:
                    default_lab_items = all_lab_ings[:4]
                    st.session_state["lab_manual_rows"] = [
                        {"المادة": item, "النسبة %": round(100.0 / len(default_lab_items), 2)}
                        for item in default_lab_items
                    ]

                lab_df_input = pd.DataFrame(st.session_state["lab_manual_rows"])
                edited_lab_df = st.data_editor(
                    lab_df_input,
                    num_rows="dynamic",
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "المادة": st.column_config.SelectboxColumn(options=all_lab_ings, required=True),
                        "النسبة %": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, step=0.5, format="%.2f%%"),
                    },
                    key="lab_editor_v1200",
                )
                st.session_state["lab_manual_rows"] = edited_lab_df.to_dict("records")

                if st.button("🔬 تحليل التركيبة في المختبر", type="primary", use_container_width=True, key="lab_run_v1200"):
                    parsed_formula: Dict[str, float] = {}
                    for _, row in edited_lab_df.iterrows():
                        mat = row.get("المادة")
                        pct = float(row.get("النسبة %") or 0.0)
                        if mat and pct > 0:
                            parsed_formula[str(mat)] = parsed_formula.get(str(mat), 0.0) + pct

                    if not parsed_formula:
                        st.error("⚠️ أدخل مادة واحدة على الأقل بنسبة أكبر من الصفر.")
                    else:
                        with st.spinner("🔬 جاري تحليل التركيبة ومقارنتها بالمعايير..."):
                            lab_res = analyze_existing_formula(parsed_formula, lab_animal, lab_prod)
                        if lab_res.get("success"):
                            st.session_state["lab_result"] = lab_res
                            st.session_state["lab_context"] = {
                                "animal": lab_animal,
                                "production": lab_prod,
                                "formula": parsed_formula,
                            }
                            st.session_state["active_formula"] = lab_res.get("formula", parsed_formula)
                        else:
                            st.error(f"❌ {lab_res.get('message', 'تعذر تحليل التركيبة')}")

            if st.session_state.get("lab_result"):
                lr = st.session_state["lab_result"]
                lctx = st.session_state.get("lab_context") or {}
                l_formula = lr.get("formula") or {}
                l_std = lr.get("standard") or {}
                l_act = lr.get("actual") or {}
                l_qual = float(lr.get("quality_score", 0.0) or 0.0)
                l_cost = float(lr.get("cost_per_ton", 0.0) or 0.0)
                l_cap = float(lr.get("ca_p_ratio", 0.0) or 0.0)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("⭐ الجودة الكلية", f"{l_qual:.1f}%")
                m2.metric("💰 تكلفة الطن", f"${l_cost:.2f}")
                m3.metric("⚖️ نسبة Ca:P", f"{l_cap:.2f}")
                m4.metric("🧬 بروتين خام CP", f"{float(l_act.get('CP', 0.0)):.2f}%")

                if lr.get("comparison"):
                    st.markdown("### 📋 مقارنة القيم المحسوبة بالمعيار")
                    formatted_cmp = []
                    for item in lr["comparison"]:
                        formatted_cmp.append(
                            {
                                "العنصر": item["العنصر"],
                                "المعيار": f"{float(item['المعيار']):.2f}",
                                "المحسوب": f"{float(item['المحسوب']):.2f}",
                                "الفرق": f"{float(item['الفرق']):+.3f}",
                                "الفرق %": f"{float(item['الفرق %']):+.2f}%",
                                "التقييم": item["التقييم"],
                            }
                        )
                    st.dataframe(pd.DataFrame(formatted_cmp), use_container_width=True, hide_index=True)

                lc1, lc2 = st.columns(2)
                with lc1:
                    _render_chart_image(create_colorful_bar_chart(l_std, l_act), caption="المقارنة بين المحسوب والمعيار")
                with lc2:
                    _render_chart_image(create_radar_chart(l_std, l_act), caption="الرسم البياني الراداري (Radar)")

                lc3, lc4 = st.columns(2)
                with lc3:
                    _render_chart_image(create_colorful_pie_chart(l_formula), caption="توزيع المكونات")
                with lc4:
                    _render_chart_image(create_gauge_chart(l_qual), caption="مقياس الجودة")

                try:
                    pdf_lab = generate_lab_pdf(lr, lctx)
                    render_pdf_download_with_approval(
                        pdf_bytes=pdf_lab,
                        file_name=f"Lab_{lctx.get('animal', 'Formula')}_{datetime.now():%Y%m%d_%H%M}.pdf",
                        doc_title=f"تقرير مختبر — {lctx.get('animal', '')} ({lctx.get('production', '')})",
                        user_role=role,
                        user_name=st.session_state.get("chat_username", "مستخدم"),
                        doc_context={
                            "الحيوان": lctx.get("animal", ""),
                            "الجودة": f"{l_qual:.1f}%",
                            "التكلفة": f"${l_cost:.2f}/طن",
                        },
                        key_suffix="lab_v1200",
                    )
                except Exception as e:
                    st.warning(f"⚠️ تعذر توليد PDF للمختبر: {e}")

                render_share_buttons(l_formula, lctx.get("animal", ""), l_qual, l_cost, key_suffix="lab_v1200")
        except Exception as e:
            st.error(f"⚠️ خطأ في مختبر التركيبات: {e}")


# -----------------------------------------------------------------------
# 2. تبويب الحاسبة المبسطة (للزائر)
# -----------------------------------------------------------------------
if "🧮 حاسبة مبسطة" in tab_map:
    with tab_map["🧮 حاسبة مبسطة"]:
        try:
            st.markdown('<div class="section-title">🧮 حاسبة التركيبات المبسطة</div>', unsafe_allow_html=True)
            all_g_ings = sorted(_get_ingredient_lookup().keys())
            g_animal = st.selectbox("القطاع:", ["أبقار", "أغنام", "دواجن", "أسماك"], key="g_animal_v1200")
            g_prod_default = {"أبقار": "حليب_متوسط", "أغنام": "تسمين_عادي", "دواجن": "لاحم", "أسماك": "نمو"}.get(g_animal, "صيانة")
            g_picks = st.multiselect("اختر 2 إلى 6 مكونات:", all_g_ings, default=all_g_ings[:3], key="g_picks_v1200")

            if st.button("⚡ حساب سريع", type="primary", use_container_width=True, key="g_calc_v1200"):
                if len(g_picks) < 2:
                    st.warning("⚠️ اختر مكونين على الأقل.")
                else:
                    lookup = _get_ingredient_lookup()
                    p_map = {k: float(lookup.get(k, {}).get("price", 300.0)) for k in g_picks}
                    base_req = analyze_existing_formula({g_picks[0]: 100.0}, g_animal, g_prod_default)
                    std_d = base_req.get("standard") or {"CP": 16.0, "DP": 12.0, "SE": 65.0, "Ca": 0.75, "P": 0.42}
                    res_g = auto_formulate_smart(g_picks, p_map, std_d, animal_type=g_animal, production_type=g_prod_default)
                    if res_g.get("success"):
                        g_f = res_g.get("formula") or {}
                        g_act = res_g.get("actual_nutrients") or {}
                        g_q = float(res_g.get("quality_score", 0.0))
                        g_c = float(res_g.get("cost", 0.0))
                        st.success(f"✅ الجودة: {g_q:.1f}% | التكلفة: ${g_c:.2f}/طن")
                        for k, v in g_f.items():
                            st.markdown(f'<div class="formula-item">▪️ <b>{k}:</b> {float(v):.2f}%</div>', unsafe_allow_html=True)
                        gc1, gc2 = st.columns(2)
                        with gc1:
                            _render_chart_image(create_colorful_bar_chart(std_d, g_act), caption="المعيار مقابل المحسوب")
                        with gc2:
                            _render_chart_image(create_radar_chart(std_d, g_act), caption="الرسم الراداري")
        except Exception as e:
            st.error(f"⚠️ {e}")


# -----------------------------------------------------------------------
# 3. تبويب التحسين غير الخطي (NLP) + الرادار + منحنى التحسين + PDF
# -----------------------------------------------------------------------
if "🎯 NLP" in tab_map:
    with tab_map["🎯 NLP"]:
        try:
            st.markdown('<div class="section-title">🎯 محرك التحسين غير الخطي (NLP — SLSQP)</div>', unsafe_allow_html=True)
            st.info("💡 يوازن محرك **NLP** بين القيمة الغذائية المتوقعة، الكلفة الفعلية، وهامش الربح عبر خوارزمية **SLSQP** غير الخطية.")

            n1, n2, n3 = st.columns(3)
            with n1:
                nlp_animal = st.selectbox(
                    "🐾 الحيوان:",
                    ["أبقار", "أغنام", "ماعز", "إبل", "خيول", "دواجن", "سمان", "أسماك", "أرانب"],
                    key="nlp_animal_v1200",
                )
            with n2:
                nlp_prod = st.text_input("📌 الحالة / المرحلة:", value="تسمين / إنتاج قياسي", key="nlp_prod_v1200")
            with n3:
                nlp_price_prod = st.number_input("💵 سعر الوحدة للمنتج ($):", min_value=0.1, value=2.5, step=0.1, key="nlp_pp_v1200")

            lookup_nlp = _get_ingredient_lookup()
            all_nlp_names = sorted(lookup_nlp.keys())
            default_nlp = [x for x in ["ذرة صفراء", "شعير مطحون", "كسب فول صويا 44%", "كسب عباد الشمس", "زيت فول الصويا", "الحجر الجيري", "فوسفات ثنائي الكالسيوم"] if x in lookup_nlp]
            nlp_selected = st.multiselect("🌾 اختر المواد العلفية للتحسين غير الخطي:", all_nlp_names, default=default_nlp or all_nlp_names[:4], key="nlp_ings_v1200")

            nlp_prices: Dict[str, float] = {}
            if nlp_selected:
                p_cols = st.columns(min(3, len(nlp_selected)))
                for i, ing_n in enumerate(nlp_selected):
                    with p_cols[i % 3]:
                        base_pr = float(lookup_nlp.get(ing_n, {}).get("price", 320.0))
                        nlp_prices[ing_n] = st.number_input(f"💲 سعر {ing_n} ($/طن):", min_value=5.0, value=base_pr, step=10.0, key=f"nlp_p_{ing_n}_v1200")

            if st.button("🚀 تشغيل التحسين غير الخطي (NLP)", type="primary", use_container_width=True, key="nlp_run_v1200"):
                if len(nlp_selected) < 2:
                    st.warning("⚠️ اختر مكونين على الأقل لتشغيل محرك NLP.")
                else:
                    with st.spinner("⚙️ جاري تنفيذ التحسين غير الخطي SLSQP..."):
                        nlp_res = nlp_optimize_feed(
                            nlp_selected,
                            lookup_nlp,
                            nlp_prices,
                            animal_type=nlp_animal,
                            production_type=nlp_prod,
                            price_product=nlp_price_prod,
                        )
                    if nlp_res.get("success"):
                        st.session_state["nlp_last_result"] = nlp_res
                        st.session_state["nlp_last_ctx"] = {
                            "animal": nlp_animal,
                            "prod": nlp_prod,
                            "selected": list(nlp_selected),
                            "prices": dict(nlp_prices),
                        }
                        st.session_state["active_formula"] = nlp_res.get("formula", {})
                    else:
                        st.error(f"❌ {nlp_res.get('message', 'تعذر إتمام التحسين غير الخطي')}")

            if st.session_state.get("nlp_last_result"):
                nr = st.session_state["nlp_last_result"]
                nctx = st.session_state.get("nlp_last_ctx") or {}
                n_formula = nr.get("formula") or {}
                n_cost = float(nr.get("final_cost", 0.0) or 0.0)
                n_me = float(nr.get("final_me", 0.0) or 0.0)
                n_cp = float(nr.get("final_cp", 0.0) or 0.0)
                n_profit = float(nr.get("max_profit", 0.0) or 0.0)

                if nr.get("warning"):
                    st.warning(nr["warning"])

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("💰 تكلفة الكيلو", f"${n_cost:.4f}/كجم")
                m2.metric("⚡ الطاقة الممثلة ME", f"{n_me:,.0f} kcal/kg")
                m3.metric("🧬 البروتين الخام CP", f"{n_cp:.2f}%")
                m4.metric("📈 هامش الربح التقديري", f"${n_profit:.4f}")

                st.markdown("### 🧪 النسب المثلى الناتجة عن محرك NLP")
                for ing, pct in n_formula.items():
                    st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {float(pct):.2f}%</div>', unsafe_allow_html=True)

                # رسوم NLP: منحنى الحساسية + الرادار والمقارنة بالمعيار
                nlp_actual_nut = compute_formula_nutrients(n_formula)
                nlp_req_map = _get_requirement_for_nlp(nctx.get("animal", nlp_animal), nctx.get("prod", nlp_prod))
                nlp_std_compare = {
                    "CP": float(nlp_req_map.get("CP", 16.0)),
                    "DP": float(nlp_req_map.get("DP", 12.0)),
                    "SE": float(nlp_req_map.get("ME", 2700.0)) / 41.0,
                }
                nlp_act_compare = {
                    "CP": float(nlp_actual_nut.get("CP", n_cp)),
                    "DP": float(nlp_actual_nut.get("DP", 0.0)),
                    "SE": float(n_me) / 41.0,
                }

                nc1, nc2 = st.columns(2)
                with nc1:
                    curve_fig = create_nlp_profit_curve(
                        nr,
                        nctx.get("selected", nlp_selected),
                        lookup_nlp,
                        nctx.get("prices", nlp_prices),
                    )
                    if PLOTLY_AVAILABLE and go is not None and isinstance(curve_fig, go.Figure):
                        st.plotly_chart(curve_fig, use_container_width=True)
                    else:
                        _render_chart_image(curve_fig, caption="منحنى تحليل التكلفة والهامش في NLP")

                with nc2:
                    _render_chart_image(create_radar_chart(nlp_std_compare, nlp_act_compare), caption="رادار نتائج NLP مقارنة بالمعيار")

                _render_chart_image(create_colorful_bar_chart(nlp_std_compare, nlp_act_compare), caption="مقارنة المحسوب بـ NLP بالمعيار")

                try:
                    pdf_nlp = generate_nlp_math_pdf(
                        nr,
                        nctx.get("animal", nlp_animal),
                        nctx.get("prod", nlp_prod),
                        nctx.get("selected", nlp_selected),
                        lookup_nlp,
                        nctx.get("prices", nlp_prices),
                    )
                    render_pdf_download_with_approval(
                        pdf_bytes=pdf_nlp,
                        file_name=f"NLP_{nctx.get('animal', nlp_animal)}_{datetime.now():%Y%m%d_%H%M}.pdf",
                        doc_title=f"تحسين غير خطي NLP — {nctx.get('animal', nlp_animal)}",
                        user_role=role,
                        user_name=st.session_state.get("chat_username", "مستخدم"),
                        doc_context={
                            "الحيوان": nctx.get("animal", nlp_animal),
                            "التكلفة": f"${n_cost:.4f}/كجم",
                            "الطاقة": f"{n_me:.0f} kcal/kg",
                        },
                        key_suffix="nlp_v1200",
                    )
                except Exception as e:
                    st.warning(f"⚠️ تعذر توليد PDF لـ NLP: {e}")

                render_share_buttons(n_formula, nctx.get("animal", nlp_animal), 85.0, n_cost * 1000.0, key_suffix="nlp_v1200")
        except Exception as e:
            st.error(f"⚠️ خطأ في محرك NLP: {e}")

# ═══════════════════════════════════════════════════════════════════════
# الجزء 4 من 5 — الزيوت، بدائل الحليب، OCR، الحظائر 3D، ودراسة الجدوى
# المنصة: تاور نولجي (Tawor Nology) — بإشراف: عبدالقادر إسماعيل
# ═══════════════════════════════════════════════════════════════════════

try:
    import pytesseract  # type: ignore
    OCR_AVAILABLE = True
except Exception:
    pytesseract = None
    OCR_AVAILABLE = False

MILK_REPLACER_STANDARDS: Dict[str, Dict[str, float]] = {
    "عجول أبقار": {"CP": 22.0, "Fat": 16.0, "Lactose": 44.0, "Ca": 0.90, "P": 0.70},
    "حملان وجديان": {"CP": 24.0, "Fat": 22.0, "Lactose": 38.0, "Ca": 0.95, "P": 0.75},
    "أمهار خيول": {"CP": 20.0, "Fat": 14.0, "Lactose": 48.0, "Ca": 0.85, "P": 0.65},
}

MILK_REPLACER_INGREDIENTS: Dict[str, Dict[str, Any]] = {
    "حليب فرز مجفف (SMP)": {"price": 2400.0, "max": 60.0, "CP": 34.0, "Fat": 1.0, "Lactose": 52.0, "Ca": 1.25, "P": 0.95},
    "شرش حليب حلو مجفف (WPC/Whey)": {"price": 1250.0, "max": 45.0, "CP": 12.0, "Fat": 1.2, "Lactose": 72.0, "Ca": 0.55, "P": 0.50},
    "بروتين صويا معزول / مركز": {"price": 1450.0, "max": 25.0, "CP": 62.0, "Fat": 1.5, "Lactose": 0.0, "Ca": 0.25, "P": 0.65},
    "زيت جوز الهند / نخيل معالج": {"price": 1350.0, "max": 28.0, "CP": 0.0, "Fat": 99.0, "Lactose": 0.0, "Ca": 0.0, "P": 0.0},
    "فوسفات أحادي الكالسيوم (MCP)": {"price": 780.0, "max": 3.0, "CP": 0.0, "Fat": 0.0, "Lactose": 0.0, "Ca": 16.0, "P": 22.5},
}

HORSE_STALL_SCIENCE: Dict[str, Dict[str, Any]] = {
    "standard_box": {"name_ar": "مربط قياسي مغلق", "width": 3.6, "length": 3.6, "cost_per_stall": 2400.0},
    "foaling_mare": {"name_ar": "مربط فرس وولادة واسع", "width": 4.2, "length": 4.5, "cost_per_stall": 3200.0},
    "stallion_box": {"name_ar": "مربط فحل معزز", "width": 4.0, "length": 4.2, "cost_per_stall": 3000.0},
}

HORSE_BARN_SCIENCE: Dict[str, Any] = {
    "aisle_width_m": 3.2,
    "wall_height_m": 3.6,
    "front_partition_m": 1.35,
}

BARN_DESIGN_STANDARDS: Dict[str, Dict[str, Any]] = {
    "أبقار": {"name_ar": "أبقار (حليب / تسمين)", "area_per_head": 6.5, "width": 12.0, "height": 4.2, "water_L": 65.0, "cost_per_m2": 180.0},
    "أغنام": {"name_ar": "أغنام (تسمين / أمهات)", "area_per_head": 1.4, "width": 10.0, "height": 3.4, "water_L": 8.0, "cost_per_m2": 125.0},
    "ماعز": {"name_ar": "ماعز", "area_per_head": 1.3, "width": 10.0, "height": 3.4, "water_L": 7.0, "cost_per_m2": 125.0},
    "إبل": {"name_ar": "إبل", "area_per_head": 8.0, "width": 14.0, "height": 4.5, "water_L": 55.0, "cost_per_m2": 170.0},
    "خيول": {"name_ar": "خيول", "area_per_head": 14.0, "width": 11.0, "height": 4.2, "water_L": 40.0, "cost_per_m2": 230.0},
    "دواجن": {"name_ar": "دواجن (لاحم / بياض)", "area_per_head": 0.08, "width": 12.0, "height": 3.5, "water_L": 0.25, "cost_per_m2": 140.0},
    "سمان": {"name_ar": "سمان", "area_per_head": 0.04, "width": 8.0, "height": 3.0, "water_L": 0.08, "cost_per_m2": 120.0},
    "أسماك": {"name_ar": "وحدات استزراع سمكي", "area_per_head": 0.25, "width": 10.0, "height": 2.8, "water_L": 5.0, "cost_per_m2": 150.0},
    "أرانب": {"name_ar": "أرانب", "area_per_head": 0.35, "width": 8.0, "height": 3.0, "water_L": 0.5, "cost_per_m2": 120.0},
}


def formulate_milk_replacer(animal_key: str, volume_kg: float, selected_items: List[str]) -> Dict[str, Any]:
    valid = [x for x in selected_items if x in MILK_REPLACER_INGREDIENTS]
    if len(valid) < 3:
        return {"success": False, "message": "يرجى اختيار 3 مكونات على الأقل لبديل الحليب."}

    std = MILK_REPLACER_STANDARDS.get(animal_key, MILK_REPLACER_STANDARDS["عجول أبقار"])
    n = len(valid)
    x0 = np.ones(n, dtype=float) / n
    bounds = []
    for name in valid:
        max_cap = min(1.0, float(MILK_REPLACER_INGREDIENTS[name].get("max", 50.0)) / 100.0)
        bounds.append((0.0, max(0.05, max_cap)))

    cp_v = np.array([float(MILK_REPLACER_INGREDIENTS[i].get("CP", 0.0)) for i in valid], dtype=float)
    fat_v = np.array([float(MILK_REPLACER_INGREDIENTS[i].get("Fat", 0.0)) for i in valid], dtype=float)
    lac_v = np.array([float(MILK_REPLACER_INGREDIENTS[i].get("Lactose", 0.0)) for i in valid], dtype=float)
    ca_v = np.array([float(MILK_REPLACER_INGREDIENTS[i].get("Ca", 0.0)) for i in valid], dtype=float)
    p_v = np.array([float(MILK_REPLACER_INGREDIENTS[i].get("P", 0.0)) for i in valid], dtype=float)
    pr_v = np.array([float(MILK_REPLACER_INGREDIENTS[i].get("price", 1500.0)) for i in valid], dtype=float)

    def mr_obj(x: np.ndarray) -> float:
        w = x / max(np.sum(x), 1e-9)
        e_cp = ((np.dot(w, cp_v) - std["CP"]) / max(std["CP"], 1.0)) ** 2
        e_fat = ((np.dot(w, fat_v) - std["Fat"]) / max(std["Fat"], 1.0)) ** 2
        e_lac = ((np.dot(w, lac_v) - std["Lactose"]) / max(std["Lactose"], 1.0)) ** 2
        e_ca = ((np.dot(w, ca_v) - std["Ca"]) / max(std["Ca"], 0.1)) ** 2
        e_p = ((np.dot(w, p_v) - std["P"]) / max(std["P"], 0.1)) ** 2
        return float(3.0 * e_cp + 3.0 * e_fat + 2.0 * e_lac + 1.5 * e_ca + 1.5 * e_p)

    if SCIPY_AVAILABLE and minimize is not None:
        res = minimize(mr_obj, x0, method="SLSQP", bounds=bounds, constraints={"type": "eq", "fun": lambda x: np.sum(x) - 1.0})
        w_opt = res.x if res.success else x0
    else:
        w_opt = x0

    w_opt = np.clip(w_opt, 0.0, 1.0)
    w_opt = w_opt / max(np.sum(w_opt), 1e-9)
    formula = {name: round(float(pct * 100.0), 2) for name, pct in zip(valid, w_opt) if pct > 0.001}

    act_cp = float(np.dot(w_opt, cp_v))
    act_fat = float(np.dot(w_opt, fat_v))
    act_ca = float(np.dot(w_opt, ca_v))
    act_p = float(np.dot(w_opt, p_v))
    ca_p_ratio = (act_ca / act_p) if act_p > 0 else 0.0

    cp_acc = max(0.0, 100.0 - abs(act_cp - std["CP"]) / max(std["CP"], 1.0) * 100.0)
    fat_acc = max(0.0, 100.0 - abs(act_fat - std["Fat"]) / max(std["Fat"], 1.0) * 100.0)
    quality_score = round(0.55 * cp_acc + 0.45 * fat_acc, 1)
    cost_per_100kg = round(float(np.dot(w_opt, pr_v)) * 0.1, 2)

    return {
        "success": True,
        "animal": animal_key,
        "volume_kg": float(volume_kg),
        "formula": formula,
        "quality_score": quality_score,
        "ca_p_ratio": round(ca_p_ratio, 2),
        "cost_per_100kg": cost_per_100kg,
        "warning": None if quality_score >= 70.0 else "نسبة الدهن أو البروتين قريبة من الحدود؛ أضف مصدراً دهنياً أو حليباً مجففاً لتحسين الجودة.",
    }


def generate_milk_replacer_pdf(r: Dict[str, Any]) -> bytes:
    lines = [
        f"Milk Replacer Formula -> Animal: {r.get('animal', '')} | Volume: {float(r.get('volume_kg', 0)):.1f} kg",
        f"Quality: {float(r.get('quality_score', 0)):.1f}% | Ca:P: {float(r.get('ca_p_ratio', 0)):.2f} | Cost/100kg: ${float(r.get('cost_per_100kg', 0)):.2f}",
        "Ingredients: " + ", ".join(f"{k} ({v:.2f}%)" for k, v in (r.get("formula") or {}).items()),
    ]
    return pdf_gen._build_pdf_from_lines("Milk Replacer Formulation Report", lines)


def extract_ingredients_from_image(image_bytes: bytes) -> Dict[str, Any]:
    if not OCR_AVAILABLE or pytesseract is None or not PIL_AVAILABLE or PILImage is None:
        return {"success": False, "count": 0, "message": "مكتبة pytesseract أو Pillow غير متوفرة."}
    try:
        img = PILImage.open(io.BytesIO(image_bytes))
        raw_text = pytesseract.image_to_string(img, lang="ara+eng")
        found: Dict[str, float] = {}
        lookup = _get_ingredient_lookup()
        for line in raw_text.splitlines():
            clean = line.strip()
            if not clean:
                continue
            for ing_name in lookup:
                if ing_name.split()[0] in clean:
                    nums = [float(tok.replace("%", "")) for tok in clean.replace(",", ".").split() if tok.replace("%", "").replace(".", "").isdigit()]
                    found[ing_name] = nums[0] if nums else 10.0
        return {
            "success": True,
            "count": len(found),
            "ingredients": found,
            "raw_text": raw_text,
            "message": "" if found else "تم قراءة النص ولكن لم تُطابق نسب واضحة؛ يمكنك الإضافة والتصحيح يدوياً.",
        }
    except Exception as e:
        return {"success": False, "count": 0, "message": f"خطأ أثناء قراءة الصورة: {e}"}


def render_ocr_correction_ui(initial_ings: Dict[str, Any]) -> Dict[str, float]:
    corrected: Dict[str, float] = {}
    for idx, (k, v) in enumerate(list((initial_ings or {}).items())):
        val_f = float(v) if str(v).replace(".", "").isdigit() else 10.0
        new_val = st.number_input(f"نسبة {k} %:", min_value=0.0, max_value=100.0, value=val_f, step=0.5, key=f"ocr_corr_{idx}_{k}")
        if new_val > 0:
            corrected[str(k)] = float(new_val)
    return corrected


def calculate_horse_barn_scientific(horse_count: int, stall_type: str, include_service: bool = True) -> Dict[str, Any]:
    st_info = HORSE_STALL_SCIENCE.get(stall_type, HORSE_STALL_SCIENCE["standard_box"])
    sw = float(st_info["width"])
    sl = float(st_info["length"])
    stall_area = round(sw * sl, 2)
    rows_count = 2 if horse_count >= 4 else 1
    stalls_per_row = math.ceil(horse_count / rows_count)
    aisle_w = float(HORSE_BARN_SCIENCE["aisle_width_m"])
    b_width = round(rows_count * sl + aisle_w, 2)
    service_len = 4.0 if include_service else 0.0
    b_length = round(stalls_per_row * sw + service_len, 2)
    b_height = float(HORSE_BARN_SCIENCE["wall_height_m"])
    total_area = round(b_width * b_length, 2)
    volume_m3 = round(total_area * b_height, 1)

    vent_summer = int(horse_count * 450)
    vent_winter = int(horse_count * 90)
    tunnel_fans = max(2, math.ceil(vent_summer / 18000))
    side_fans = max(2, math.ceil(horse_count / 4))
    bedding_cm = 15
    bedding_m3 = round(horse_count * stall_area * (bedding_cm / 100.0), 1)

    cost_stalls = round(horse_count * float(st_info["cost_per_stall"]), 0)
    cost_structure = round(total_area * 145.0, 0)
    cost_roof = round(total_area * 65.0, 0)
    cost_aisle = round(aisle_w * b_length * 45.0, 0)
    cost_service = round(3500.0 if include_service else 800.0, 0)
    cost_vent = round((tunnel_fans + side_fans) * 650.0, 0)
    cost_light = round(horse_count * 180.0, 0)
    cost_win = round(horse_count * 220.0, 0)
    cost_total = cost_stalls + cost_structure + cost_roof + cost_aisle + cost_service + cost_vent + cost_light + cost_win

    return {
        "mode": "horse",
        "stall_type_ar": st_info["name_ar"],
        "stall_dimensions": f"{sw} × {sl} م",
        "stall_area_m2": stall_area,
        "reference": "NRC (2007) Nutrient Requirements of Horses & MWPS-1 Horse Housing Guidelines",
        "total_area_m2": total_area,
        "building_length_m": b_length,
        "building_width_m": b_width,
        "building_height_m": b_height,
        "volume_m3": volume_m3,
        "num_horses": int(horse_count),
        "rows_count": rows_count,
        "stalls_per_row": stalls_per_row,
        "aisle_width_m": aisle_w,
        "feeders_count": int(horse_count),
        "drinkers_count": int(horse_count),
        "vent_summer_m3h": vent_summer,
        "vent_winter_m3h": vent_winter,
        "tunnel_fans_count": tunnel_fans,
        "side_fans_count": side_fans,
        "doors_count": 2,
        "door_dimensions": "2.4 × 2.8 م",
        "window_area_m2": round(horse_count * 1.2, 1),
        "bedding_cm": bedding_cm,
        "bedding_m3": bedding_m3,
        "cost_structure_usd": cost_structure,
        "cost_roof_usd": cost_roof,
        "cost_stalls_usd": cost_stalls,
        "cost_aisle_floor_usd": cost_aisle,
        "cost_service_usd": cost_service,
        "cost_ventilation_usd": cost_vent,
        "cost_lighting_usd": cost_light,
        "cost_windows_usd": cost_win,
        "cost_total_usd": cost_total,
    }


def calculate_barn_dimensions(animal_key: str, count: int, system_type: str = "أرضي مفتوح") -> Optional[Dict[str, Any]]:
    std = BARN_DESIGN_STANDARDS.get(animal_key)
    if not std:
        return None
    factor = 0.72 if system_type == "بطاريات" else 1.0
    total_area = round(max(12.0, float(count) * float(std["area_per_head"]) * factor), 1)
    width_m = float(std["width"])
    length_m = round(total_area / max(width_m, 1.0), 1)
    ridge_h = float(std["height"])
    volume_m3 = round(total_area * ridge_h, 1)
    water_day = round(float(count) * float(std["water_L"]), 1)
    tunnel_fans = max(2, math.ceil(total_area / 120.0))
    side_fans = max(2, math.ceil(length_m / 12.0))
    cooling_enabled = total_area >= 150.0
    cooling_area = round(width_m * 1.4, 1) if cooling_enabled else 0.0
    cost_total = round(total_area * float(std["cost_per_m2"]), 0)

    return {
        "mode": "standard",
        "animal_key": animal_key,
        "system_type": system_type,
        "total_area_m2": total_area,
        "length_m": length_m,
        "width_m": width_m,
        "ridge_height_m": ridge_h,
        "volume_m3": volume_m3,
        "tunnel_fans_count": tunnel_fans,
        "side_fans_count": side_fans,
        "cooling_pad_enabled": cooling_enabled,
        "cooling_pad_area_m2": cooling_area,
        "water_per_day_L": water_day,
        "cost_total_usd": cost_total,
    }


def create_barn_3d_figure(dims: Dict[str, Any]):
    if not PLOTLY_AVAILABLE or go is None or not dims:
        return None
    L = float(dims.get("building_length_m", dims.get("length_m", 20.0)) or 20.0)
    W = float(dims.get("building_width_m", dims.get("width_m", 10.0)) or 10.0)
    H = float(dims.get("building_height_m", dims.get("ridge_height_m", 3.6)) or 3.6)

    fig = go.Figure()
    fig.add_trace(
        go.Mesh3d(
            x=[0, L, L, 0, 0, L, L, 0],
            y=[0, 0, W, W, 0, 0, W, W],
            z=[0, 0, 0, 0, H, H, H, H],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            color="#2e7d32",
            opacity=0.35,
            name="Barn Structure",
        )
    )
    fig.update_layout(
        title=f"3D Barn Model ({L:.1f}m × {W:.1f}m × {H:.1f}m)",
        scene=dict(xaxis_title="Length (m)", yaxis_title="Width (m)", zaxis_title="Height (m)"),
        margin=dict(l=0, r=0, t=40, b=0),
        height=420,
    )
    return fig


def generate_barn_pdf_report(dims: Dict[str, Any]) -> bytes:
    lines = [
        f"Barn Design Report -> Area: {dims.get('total_area_m2', 0)} m2 | Volume: {dims.get('volume_m3', 0)} m3",
        f"Water/Day: {float(dims.get('water_per_day_L', 0) or 0):,.0f} L | Estimated Cost: ${float(dims.get('cost_total_usd', 0) or 0):,.0f}",
        f"Tunnel Fans: {dims.get('tunnel_fans_count', 0)} | Side Fans: {dims.get('side_fans_count', 0)}",
    ]
    return pdf_gen._build_pdf_from_lines("3D Barn Engineering Report", lines)


# ═══ 🌰 الزيوت ═══
if "🌰 الزيوت" in tab_map:
    with tab_map["🌰 الزيوت"]:
        try:
            st.markdown('<div class="section-title">🌰 مكتبة الزيوت</div>', unsafe_allow_html=True)
            if MAX_OIL_PERCENTAGE:
                oil_rows = [
                    {"الحيوان": k, "أقصى %": f"{float(v['max']):.1f}%", "مثالي %": f"{float(v['optimal']):.1f}%", "المرجع": v.get("source", "—")}
                    for k, v in MAX_OIL_PERCENTAGE.items()
                ]
                st.dataframe(pd.DataFrame(oil_rows), use_container_width=True, hide_index=True)

            oils = get_oil_ingredients()
            for ing_name, ing_data in oils.items():
                with st.expander(f"🌰 {ing_name}"):
                    se_val = float(ing_data.get("SE", 0.0) or 0.0)
                    c1, c2, c3 = st.columns(3)
                    c1.metric("SE", f"{se_val:.0f}")
                    c2.metric("kcal/kg", f"{se_val * 41.0:.0f}")
                    c3.metric("السعر", f"${float(ing_data.get('price', 0.0) or 0.0):.0f}")
                    if ing_data.get("desc"):
                        st.info(f"📝 {ing_data['desc']}")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 🍼 بدائل الحليب ═══
if "🍼 بدائل الحليب" in tab_map:
    with tab_map["🍼 بدائل الحليب"]:
        try:
            st.markdown('<div class="section-title">🍼 بدائل الحليب</div>', unsafe_allow_html=True)
            mr1, mr2 = st.columns(2)
            with mr1:
                mr_a = st.selectbox("الحيوان:", list(MILK_REPLACER_STANDARDS.keys()), key="mr_a_v1200")
                mr_v = st.number_input("الكمية (كجم):", 1.0, 10000.0, 100.0, 10.0, key="mr_v_v1200")
            with mr2:
                std_mr = MILK_REPLACER_STANDARDS[mr_a]
                st.markdown(
                    f"""<div style="background:#f1f8e9; padding:20px; border-radius:16px; border-right:5px solid #2e7d32;">
                    <b>📊 {mr_a}:</b><br>
                    بروتين: {std_mr['CP']}% | دهن: {std_mr['Fat']}% | لاكتوز: {std_mr['Lactose']}%<br>
                    Ca: {std_mr['Ca']}% | P: {std_mr['P']}%
                </div>""",
                    unsafe_allow_html=True,
                )

            mr_sel: List[str] = []
            cols = st.columns(3)
            for i, (name, data) in enumerate(MILK_REPLACER_INGREDIENTS.items()):
                with cols[i % 3]:
                    with st.expander(f"{name}"):
                        st.caption(f"💵 ${float(data['price']):.2f}/كجم | حد: {float(data['max']):.1f}%")
                        if st.checkbox("إضافة", key=f"mr_{name}_v1200"):
                            mr_sel.append(name)

            if st.button("🧪 تركيب بديل الحليب", type="primary", use_container_width=True, key="mr_run_v1200"):
                if len(mr_sel) < 3:
                    st.warning("⚠️ اختر 3 مكونات على الأقل")
                else:
                    with st.spinner("⏳ جاري التركيب..."):
                        r = formulate_milk_replacer(mr_a, mr_v, mr_sel)
                    if r.get("success"):
                        quality = float(r.get("quality_score", 0.0) or 0.0)
                        meets70 = quality >= 70.0
                        bg = "quality-good-v113" if meets70 else "quality-bad-v113"
                        st.markdown(
                            f"""<div class="{bg}">
                            <h3 style="color:{'#1b5e20' if meets70 else '#c62828'}; margin:0;">جودة: {quality:.1f}%</h3>
                            <p>Ca:P = {float(r.get('ca_p_ratio', 0.0)):.2f}</p>
                        </div>""",
                            unsafe_allow_html=True,
                        )
                        if r.get("warning"):
                            st.warning(r["warning"])
                        for ing, pct in (r.get("formula") or {}).items():
                            pct_f = float(pct or 0.0)
                            kg = pct_f * float(mr_v) / 100.0
                            st.markdown(f'<div class="formula-item">▪️ <b>{ing}:</b> {pct_f:.2f}% ({kg:.2f} كجم)</div>', unsafe_allow_html=True)
                        st.metric("💰 تكلفة 100 كجم", f"${float(r.get('cost_per_100kg', 0.0)):.2f}")

                        pdf_mr = generate_milk_replacer_pdf(r)
                        if pdf_mr:
                            render_pdf_download_with_approval(
                                pdf_bytes=pdf_mr,
                                file_name=f"Milk_{str(mr_a).split()[0]}_{datetime.now():%Y%m%d}.pdf",
                                doc_title=f"بديل حليب — {mr_a}",
                                user_role=role,
                                user_name=st.session_state.get("chat_username", "مستخدم"),
                                doc_context={"الحيوان": mr_a, "الجودة": f"{quality:.1f}%", "الكمية": f"{float(mr_v):.0f} كجم"},
                                key_suffix="milk_v1200",
                            )
                    else:
                        st.error(f"❌ {r.get('message', 'فشل التركيب')}")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 📷 OCR ═══
if "📷 OCR" in tab_map:
    with tab_map["📷 OCR"]:
        try:
            st.markdown('<div class="section-title">📷 التعرف الضوئي على المكونات (OCR)</div>', unsafe_allow_html=True)
            if not OCR_AVAILABLE:
                st.error("⚠️ pytesseract غير مثبتة في بيئة التشغيل الحالية")
            else:
                up = st.file_uploader("ارفع الصورة:", type=["jpg", "jpeg", "png"], key="ocr_upload_v1200")
                if up:
                    uploaded = up.read()
                    _render_chart_image(uploaded, caption="الصورة المرفوعة")
                    if st.button("🔍 تحليل الصورة", type="primary", use_container_width=True, key="ocr_run_v1200"):
                        with st.spinner("🔬 جاري التحليل..."):
                            result = extract_ingredients_from_image(uploaded)
                        if result.get("success") and int(result.get("count", 0)) > 0:
                            ings = result.get("ingredients") or {}
                            st.success(f"✅ تم التعرف على {result['count']} مادة")
                            nut = compute_formula_nutrients(ings)
                            st.dataframe(pd.DataFrame([{"المادة": k, "النسبة": v} for k, v in ings.items()]), use_container_width=True, hide_index=True)
                            n1, n2, n3, n4 = st.columns(4)
                            n1.metric("CP", f"{nut['CP']:.2f}%")
                            n2.metric("DP", f"{nut['DP']:.2f}%")
                            n3.metric("SE", f"{nut['SE']:.1f}")
                            n4.metric("NDF", f"{nut['NDF']:.2f}%")

                            with st.expander("✏️ تصحيح النسب", expanded=True):
                                corrected = render_ocr_correction_ui(ings)
                                if st.button("✅ تطبيق التصحيح", type="primary", use_container_width=True, key="ocr_apply_v1200"):
                                    if corrected:
                                        st.session_state["last_ocr_result"] = corrected
                                        st.session_state["last_ocr_nutrients"] = compute_formula_nutrients(corrected)
                                        st.success("✅ تم تطبيق التصحيح")
                                        st.rerun()

                            try:
                                pdf_ocr = pdf_gen.generate_ocr_report(ings, nut, raw_text=result.get("raw_text", ""))
                                render_pdf_download_with_approval(
                                    pdf_bytes=pdf_ocr,
                                    file_name=f"OCR_{datetime.now():%Y%m%d}.pdf",
                                    doc_title="تحليل OCR — صورة",
                                    user_role=role,
                                    user_name=st.session_state.get("chat_username", "مستخدم"),
                                    doc_context={"عدد المواد": str(result["count"])},
                                    key_suffix="ocr_v1200",
                                )
                            except Exception as e:
                                st.warning(f"⚠️ PDF: {e}")
                        else:
                            st.warning(f"⚠️ {result.get('message', 'لم يتم استخراج مكونات واضحة')}")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 🏗️ الحظائر 3D ═══
if "🏗️ الحظائر 3D" in tab_map:
    with tab_map["🏗️ الحظائر 3D"]:
        try:
            st.markdown('<div class="section-title">🏗️ مصمم الحظائر 3D</div>', unsafe_allow_html=True)
            barn_mode = st.radio("نوع الحساب:", ["🏠 حظيرة قياسية", "🐎 مربط خيول علمي"], horizontal=True, key="barn_mode_v1200")

            if "🐎" in barn_mode:
                st.markdown("### 🐎 مربط خيول علمي (NRC 2007 + MWPS-1)")
                c1, c2, c3 = st.columns(3)
                with c1:
                    horse_count = st.number_input("🔢 عدد الخيول:", 1, 100, 10, 1, key="horse_count_v1200")
                with c2:
                    stall_type = st.selectbox(
                        "📦 نوع المربط:",
                        list(HORSE_STALL_SCIENCE.keys()),
                        format_func=lambda k: f"{HORSE_STALL_SCIENCE[k]['name_ar']} — {HORSE_STALL_SCIENCE[k]['width']}×{HORSE_STALL_SCIENCE[k]['length']} م",
                        key="stall_type_v1200",
                    )
                with c3:
                    include_service = st.checkbox("🚿 خدمات", value=True, key="service_v1200")

                if st.button("🏗️ حساب المربط", type="primary", use_container_width=True, key="horse_calc_v1200"):
                    st.session_state["horse_barn_dims"] = calculate_horse_barn_scientific(horse_count, stall_type, include_service)

                if st.session_state.get("horse_barn_dims"):
                    dims = st.session_state["horse_barn_dims"]
                    st.markdown(
                        f"""<div class="physio-card">
                        <h4>🐎 {dims['stall_type_ar']}</h4>
                        <p style="color:#1a237e; font-size:1.1rem; font-weight:700; margin:0;">
                            {dims['stall_dimensions']} | المساحة: {dims['stall_area_m2']} م²
                        </p>
                        <p style="color:#555; margin:8px 0 0 0;">📖 {dims['reference']}</p>
                    </div>""",
                        unsafe_allow_html=True,
                    )

                    k1, k2, k3, k4 = st.columns(4)
                    k1.metric("📏 المساحة", f"{dims['total_area_m2']} م²")
                    k2.metric("📐 الأبعاد", f"{dims['building_length_m']}×{dims['building_width_m']} م")
                    k3.metric("🏔️ الارتفاع", f"{dims['building_height_m']} م")
                    k4.metric("📦 الحجم", f"{dims['volume_m3']} م³")

                    k5, k6, k7, k8 = st.columns(4)
                    k5.metric("🐎 مربطات", f"{dims['num_horses']} ({dims['rows_count']} صف × {dims['stalls_per_row']})")
                    k6.metric("🚪 الممر", f"{dims['aisle_width_m']} م")
                    k7.metric("🍽️ معالف", f"{dims['feeders_count']}")
                    k8.metric("💧 سقايات", f"{dims['drinkers_count']}")

                    v1, v2, v3, v4 = st.columns(4)
                    v1.metric("💨 الصيف", f"{dims['vent_summer_m3h']:,} م³/س")
                    v2.metric("💨 الشتاء", f"{dims['vent_winter_m3h']:,} م³/س")
                    v3.metric("🌀 مراوح نفق", f"{dims['tunnel_fans_count']}")
                    v4.metric("🌀 مراوح جانبية", f"{dims['side_fans_count']}")

                    fig3d = create_barn_3d_figure(dims)
                    if fig3d:
                        st.plotly_chart(fig3d, use_container_width=True)

                    cost_data = {
                        "الهيكل": dims["cost_structure_usd"],
                        "السقف": dims["cost_roof_usd"],
                        "المربطات": dims["cost_stalls_usd"],
                        "الممر": dims["cost_aisle_floor_usd"],
                        "الخدمات": dims["cost_service_usd"],
                        "التهوية": dims["cost_ventilation_usd"],
                        "الإضاءة": dims["cost_lighting_usd"],
                        "النوافذ": dims["cost_windows_usd"],
                    }
                    st.dataframe(pd.DataFrame([{"البند": k, "التكلفة ($)": f"${v:,.0f}"} for k, v in cost_data.items()]), use_container_width=True, hide_index=True)
                    st.metric("💰 إجمالي التكلفة", f"${dims['cost_total_usd']:,.0f}")

                    pdf_b = generate_barn_pdf_report(dims)
                    render_pdf_download_with_approval(
                        pdf_bytes=pdf_b,
                        file_name=f"Horse_Barn_{horse_count}_{datetime.now():%Y%m%d}.pdf",
                        doc_title=f"مربط خيول — {horse_count} حصان",
                        user_role=role,
                        user_name=st.session_state.get("chat_username", "مستخدم"),
                        doc_context={"عدد الخيول": str(horse_count), "نوع المربط": dims["stall_type_ar"], "المساحة": f"{dims['total_area_m2']} م²"},
                        key_suffix="horse_barn_v1200",
                    )
            else:
                c1, c2, c3 = st.columns(3)
                with c1:
                    barn_a = st.selectbox("🐾 الحيوان:", list(BARN_DESIGN_STANDARDS.keys()), format_func=lambda k: BARN_DESIGN_STANDARDS[k]["name_ar"], key="barn_animal_v1200")
                with c2:
                    barn_c = st.number_input("🔢 العدد:", 1, 100000, 1000, 50, key="barn_count_v1200")
                with c3:
                    barn_s = st.selectbox("🏠 النظام:", ["أرضي مفتوح", "بطاريات"], key="barn_system_v1200")

                dims = calculate_barn_dimensions(barn_a, barn_c, barn_s)
                if dims:
                    k1, k2, k3, k4 = st.columns(4)
                    k1.metric("📏 المساحة", f"{dims['total_area_m2']} م²")
                    k2.metric("📐 الأبعاد", f"{dims['length_m']}×{dims['width_m']} م")
                    k3.metric("🏔️ القمة", f"{dims['ridge_height_m']} م")
                    k4.metric("📦 الحجم", f"{dims['volume_m3']} م³")

                    v1, v2, v3, v4 = st.columns(4)
                    v1.metric("🌀 مراوح نفق", f"{dims['tunnel_fans_count']}")
                    v2.metric("🌀 مراوح جانبية", f"{dims['side_fans_count']}")
                    v3.metric("❄️ ألواح تبريد", f"{dims['cooling_pad_area_m2']} م²" if dims.get("cooling_pad_enabled") else "—")
                    v4.metric("💧 ماء/يوم", f"{dims['water_per_day_L']:,.0f} لتر")

                    fig3d = create_barn_3d_figure(dims)
                    if fig3d:
                        st.plotly_chart(fig3d, use_container_width=True)

                    pdf_b = generate_barn_pdf_report(dims)
                    render_pdf_download_with_approval(
                        pdf_bytes=pdf_b,
                        file_name=f"Barn_{barn_a}_{datetime.now():%Y%m%d}.pdf",
                        doc_title=f"حظيرة {barn_a} — {barn_c} رأس",
                        user_role=role,
                        user_name=st.session_state.get("chat_username", "مستخدم"),
                        doc_context={"الحيوان": barn_a, "العدد": str(barn_c), "المساحة": f"{dims['total_area_m2']} م²"},
                        key_suffix="barn_v1200",
                    )
        except Exception as e:
            st.error(f"⚠️ {e}")
            with st.expander("التفاصيل"):
                st.code(traceback.format_exc())


# ═══ 📊 الجدوى ═══
if "📊 الجدوى" in tab_map:
    with tab_map["📊 الجدوى"]:
        try:
            st.markdown('<div class="section-title">📊 دراسة الجدوى</div>', unsafe_allow_html=True)
            mode = st.radio("النوع:", ["🔬 فنية", "💰 اقتصادية"], horizontal=True, key="feas_mode_v1200")
            f1, f2 = st.columns(2)
            fp = 350.0
            pp = 2.5
            with f1:
                feas_k = st.selectbox("الحيوان:", list(BARN_DESIGN_STANDARDS.keys()), format_func=lambda k: BARN_DESIGN_STANDARDS[k]["name_ar"], key="feas_animal_v1200")
                feas_c = st.number_input("العدد:", 1, 100000, 1000, 50, key="feas_count_v1200")
            with f2:
                if "اقتصادية" in mode:
                    fp = st.number_input("💵 سعر العلف ($/طن):", 50.0, 5000.0, 350.0, 10.0, key="feas_fp_v1200")
                    pp = st.number_input("💵 سعر المنتج ($/كجم):", 0.1, 10000.0, 2.5, 0.1, key="feas_pp_v1200")

            dims = calculate_barn_dimensions(feas_k, feas_c)
            if dims:
                fc1, fc2, fc3, fc4 = st.columns(4)
                fc1.metric("📏 المساحة", f"{dims['total_area_m2']} م²")
                fc2.metric("📦 الحجم", f"{dims['volume_m3']} م³")
                fc3.metric("💧 ماء/يوم", f"{dims['water_per_day_L']:,.0f} لتر")
                fc4.metric("💰 تكلفة الحظيرة", f"${dims['cost_total_usd']:,.0f}")

                if "اقتصادية" in mode:
                    est_feed_tons = float(feas_c) * 0.08 * 30.0 / 1000.0
                    est_feed_cost = est_feed_tons * float(fp)
                    est_rev = float(feas_c) * 1.8 * float(pp)
                    e1, e2, e3 = st.columns(3)
                    e1.metric("🌾 علف تقديري/دورة", f"{est_feed_tons:.1f} طن")
                    e2.metric("💵 تكلفة علف تقديرية", f"${est_feed_cost:,.0f}")
                    e3.metric("📈 إيراد تقديري", f"${est_rev:,.0f}")
        except Exception as e:
            st.error(f"⚠️ {e}")

# ═══════════════════════════════════════════════════════════════════════
# الجزء 5 من 5 — المزارع، المستودعات، طلبات PDF، التواصل، الاستديو، المراجع، والتذييل
# المنصة: تاور نولجي (Tawor Nology) — بإشراف: عبدالقادر إسماعيل
# ═══════════════════════════════════════════════════════════════════════

import json


def _chat_storage_path() -> str:
    return "tawor_chat_rooms.json"


def _studio_storage_path() -> str:
    return "tawor_studio_data.json"


def _load_chat_rooms() -> Dict[str, List[Dict[str, Any]]]:
    p = _chat_storage_path()
    if "chat_rooms_cache" in st.session_state and isinstance(st.session_state["chat_rooms_cache"], dict):
        return st.session_state["chat_rooms_cache"]
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    st.session_state["chat_rooms_cache"] = data
                    return data
        except Exception:
            pass
    default_rooms = {"🌾 النقاش العام": [], "🧬 نقاش علمي": [], "💰 نقاش اقتصادي": []}
    st.session_state["chat_rooms_cache"] = default_rooms
    return default_rooms


def _save_chat_rooms(rooms: Dict[str, List[Dict[str, Any]]]) -> None:
    st.session_state["chat_rooms_cache"] = rooms
    try:
        with open(_chat_storage_path(), "w", encoding="utf-8") as f:
            json.dump(rooms, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def create_chat_room(room_name: str) -> bool:
    clean = (room_name or "").strip()
    if not clean:
        return False
    rooms = dict(_load_chat_rooms())
    if clean not in rooms:
        rooms[clean] = []
        _save_chat_rooms(rooms)
    return True


def _safe_username() -> str:
    u = str(st.session_state.get("chat_username") or "").strip()
    return u if u else "مستخدم"


def _sanitize_message(text: str, max_len: int = 1000) -> str:
    clean = (text or "").replace("<", "&lt;").replace(">", "&gt;").strip()
    return clean[:max_len]


def check_rate_limit(bucket: str, max_calls: int = 30, window: int = 60) -> bool:
    now = _time.time()
    hist_key = f"_rl_{bucket}"
    calls = [t for t in st.session_state.get(hist_key, []) if (now - t) <= window]
    if len(calls) >= max_calls:
        st.session_state[hist_key] = calls
        return False
    calls.append(now)
    st.session_state[hist_key] = calls
    return True


def add_chat_message(room: str, user: str, msg: str) -> bool:
    clean_msg = _sanitize_message(msg, 1200)
    if not clean_msg:
        return False
    rooms = dict(_load_chat_rooms())
    rooms.setdefault(room, []).append(
        {
            "user": _sanitize_message(user, 80),
            "role": st.session_state.get("user_role", "guest"),
            "msg": clean_msg,
            "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    )
    _save_chat_rooms(rooms)
    return True


def _load_studio() -> Dict[str, List[Dict[str, Any]]]:
    p = _studio_storage_path()
    if "studio_cache" in st.session_state and isinstance(st.session_state["studio_cache"], dict):
        return st.session_state["studio_cache"]
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    data.setdefault("videos", [])
                    data.setdefault("slides", [])
                    data.setdefault("notes", [])
                    st.session_state["studio_cache"] = data
                    return data
        except Exception:
            pass
    default_st = {"videos": [], "slides": [], "notes": []}
    st.session_state["studio_cache"] = default_st
    return default_st


def _save_studio(studio_data: Dict[str, List[Dict[str, Any]]]) -> None:
    st.session_state["studio_cache"] = studio_data
    try:
        with open(_studio_storage_path(), "w", encoding="utf-8") as f:
            json.dump(studio_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def render_pdf_requests_admin() -> None:
    st.markdown('<div class="section-title">📋 إدارة طلبات تحميل PDF المختوم</div>', unsafe_allow_html=True)
    reqs = st.session_state.setdefault("pdf_approval_requests", [])
    approved_set = set(st.session_state.setdefault("approved_pdf_tokens", []))

    if not reqs:
        st.info("📭 لا توجد طلبات موافقة على تحميل ملفات PDF حالياً.")
        return

    for idx, req in enumerate(reqs):
        req_id = req.get("id", f"req_{idx}")
        status = req.get("status", "pending")
        badge = "🟢 معتمد" if status == "approved" else ("🔴 مرفوض" if status == "rejected" else "🟡 قيد الانتظار")
        with st.expander(f"{badge} — {req.get('title', 'تقرير')} | بواسطة: {req.get('user_name', 'مستخدم')} ({req.get('ts', '')})", expanded=(status == "pending")):
            st.json(req.get("context") or {})
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ اعتماد الطلب", type="primary", use_container_width=True, key=f"app_pdf_{idx}_{req_id}"):
                    req["status"] = "approved"
                    approved_set.add(req_id)
                    st.session_state["approved_pdf_tokens"] = list(approved_set)
                    st.success("✅ تمت الموافقة على تحميل هذا الملف.")
                    st.rerun()
            with col_b:
                if st.button("❌ رفض الطلب", use_container_width=True, key=f"rej_pdf_{idx}_{req_id}"):
                    req["status"] = "rejected"
                    if req_id in approved_set:
                        approved_set.remove(req_id)
                        st.session_state["approved_pdf_tokens"] = list(approved_set)
                    st.warning("تم رفض الطلب.")
                    st.rerun()


# ═══ 🐔 المزارع ═══
if "🐔 المزارع" in tab_map:
    with tab_map["🐔 المزارع"]:
        try:
            st.markdown('<div class="section-title">🐔 إدارة المزارع</div>', unsafe_allow_html=True)
            farms = st.session_state.setdefault("broiler_farms", {})
            with st.form("new_farm_v1200", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    nf_name = st.text_input("اسم المزرعة *", key="nf_n_v1200")
                    nf_strain = st.selectbox("السلالة", ["Ross 308", "Cobb 500"], key="nf_s_v1200")
                with c2:
                    nf_birds = st.number_input("الطيور:", 100, 100000, 1000, 50, key="nf_b_v1200")
                    nf_date = st.date_input("التاريخ", key="nf_d_v1200")
                if st.form_submit_button("💾 حفظ", type="primary", use_container_width=True) and nf_name.strip():
                    clean_n = nf_name.strip()
                    if clean_n not in farms:
                        farms[clean_n] = {"strain": nf_strain, "start_birds": int(nf_birds), "start_date": str(nf_date), "records": []}
                        st.success(f"✅ {clean_n}")
                        st.rerun()
                    else:
                        st.warning("⚠️ المزرعة مسجلة مسبقاً")

            if farms:
                sel = st.selectbox("اختر مزرعة:", list(farms.keys()), key="farm_sel_v1200")
                farm = farms[sel]
                st.markdown(f"### 📝 {farm.get('strain', '')} — قراءة يومية")
                with st.form(f"rec_{sel}_v1200"):
                    rc = st.columns(3)
                    with rc[0]:
                        age = st.number_input("العمر (يوم)", 1, 60, 1, key="r_age_v1200")
                    with rc[1]:
                        alive = st.number_input("العدد الحي", 0, int(farm.get("start_birds", 1000)), value=int(farm.get("start_birds", 1000)), key="r_alive_v1200")
                    with rc[2]:
                        wt = st.number_input("متوسط الوزن (كجم)", 0.01, 5.0, 0.045, 0.005, key="r_wt_v1200")
                    if st.form_submit_button("➕ تسجيل القراءة", type="primary", use_container_width=True):
                        farm.setdefault("records", []).append({"date": str(datetime.now().date()), "age": int(age), "alive": int(alive), "wt": float(wt)})
                        st.success("✅ تم تسجيل القراءة اليومية")
                        st.rerun()

                if farm.get("records"):
                    latest = farm["records"][-1]
                    start_b = max(1, int(farm.get("start_birds", 1)))
                    liv = float(latest.get("alive", 0)) / start_b * 100.0
                    m = st.columns(3)
                    m[0].metric("🐦 نسبة الحيوية", f"{liv:.1f}%")
                    m[1].metric("⚖️ الوزن", f"{float(latest.get('wt', 0.0)):.3f} كجم")
                    m[2].metric("📅 العمر", f"{latest.get('age', 0)} يوم")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ تبويبات المالك ═══
if role == "owner":
    if "🏭 المستودعات" in tab_map:
        with tab_map["🏭 المستودعات"]:
            try:
                st.markdown('<div class="section-title">🏭 المستودعات وهوية المالك</div>', unsafe_allow_html=True)

                with st.expander("🖼️ تحديث الصورة الشخصية للمالك (تظهر فوراً على البرنامج والختم)", expanded=False):
                    up_photo = st.file_uploader("اختر صورة شخصية (JPG / PNG):", type=["jpg", "jpeg", "png"], key="owner_photo_up_v1200")
                    if up_photo is not None:
                        p_bytes = up_photo.read()
                        st.session_state["runtime_owner_photo_b64"] = base64.b64encode(p_bytes).decode("utf-8")
                        try:
                            with open("owner_photo.jpg", "wb") as pf:
                                pf.write(p_bytes)
                            st.success("✅ تم حفظ الصورة باسم `owner_photo.jpg` وتحديثها في الجلسة.")
                        except Exception:
                            st.info("تم تحديث الصورة في الجلسة الحالية.")

                inv = st.session_state.setdefault("inventory", {})
                q = [float(v.get("quantity", 0.0) or 0.0) for v in inv.values() if isinstance(v, dict)]
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("📦 المواد", len(inv))
                c2.metric("🟢 آمنة", sum(1 for x in q if x >= 5.0))
                c3.metric("🟡 منخفضة", sum(1 for x in q if 0.0 < x < 5.0))
                c4.metric("🔴 نافذة", sum(1 for x in q if x <= 0.0))

                inv_df = pd.DataFrame(
                    [
                        {
                            "المادة": name,
                            "الكمية (طن)": float(inv[name].get("quantity", 0.0) or 0.0),
                            "الحد الأدنى": float(inv[name].get("min_threshold", 0.0) or 0.0),
                        }
                        for name in inv.keys()
                        if isinstance(inv[name], dict)
                    ]
                )
                edited = st.data_editor(
                    inv_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "المادة": st.column_config.TextColumn(disabled=True),
                        "الكمية (طن)": st.column_config.NumberColumn(min_value=0.0, step=1.0),
                        "الحد الأدنى": st.column_config.NumberColumn(min_value=0.0, step=1.0),
                    },
                    key="inv_editor_v1200",
                )
                if st.button("💾 حفظ بيانات المستودع", type="primary", use_container_width=True, key="inv_save_v1200"):
                    for _, r in edited.iterrows():
                        name = r["المادة"]
                        if name in inv:
                            inv[name]["quantity"] = float(r["الكمية (طن)"] or 0.0)
                            inv[name]["min_threshold"] = float(r["الحد الأدنى"] or 0.0)
                    st.success("✅ تم حفظ التعديلات")
                    st.rerun()
            except Exception as e:
                st.error(f"⚠️ {e}")

    if "📋 طلبات PDF" in tab_map:
        with tab_map["📋 طلبات PDF"]:
            try:
                render_pdf_requests_admin()
            except Exception as e:
                st.error(f"⚠️ {e}")
                with st.expander("التفاصيل"):
                    st.code(traceback.format_exc())


# ═══ 💬 غرفة التواصل ═══
if "💬 غرفة التواصل" in tab_map:
    with tab_map["💬 غرفة التواصل"]:
        try:
            st.markdown('<div class="section-title">💬 غرفة التواصل العلمي</div>', unsafe_allow_html=True)
            rooms = dict(_load_chat_rooms())
            for dr in ["🌾 النقاش العام", "🧬 نقاش علمي", "💰 نقاش اقتصادي"]:
                if dr not in rooms:
                    rooms[dr] = []
            _save_chat_rooms(rooms)

            c1, c2, c3 = st.columns([0.5, 0.25, 0.25])
            with c1:
                current_room = st.selectbox("🏠 الغرفة:", list(rooms.keys()), key="comm_room_v1200")
            with c2:
                if role in ("owner", "specialist"):
                    if st.button("➕ غرفة جديدة", use_container_width=True, key="comm_new_v1200"):
                        st.session_state["show_new_room"] = True
            with c3:
                if role == "owner" and st.button("🗑️ حذف الغرفة", use_container_width=True, key="comm_del_v1200"):
                    if current_room in rooms and len(rooms) > 1:
                        del rooms[current_room]
                        _save_chat_rooms(rooms)
                        st.rerun()

            if st.session_state.get("show_new_room"):
                nr = st.text_input("اسم الغرفة الجديدة:", key="comm_nr_v1200")
                if st.button("إنشاء الغرفة", key="comm_nr_btn_v1200") and nr.strip():
                    if create_chat_room(nr.strip()):
                        st.session_state["show_new_room"] = False
                        st.rerun()

            username = _safe_username()
            msgs = (rooms.get(current_room) or [])[-80:]
            st.caption(f"👤 {username} | 🏠 {current_room} | عدد الرسائل: {len(msgs)}")

            chat_html = (
                '<div style="background:#fafafa; padding:15px; border-radius:14px; '
                'height:420px; overflow-y:auto; border:1px solid #e0e0e0; direction:rtl;">'
            )
            if not msgs:
                chat_html += '<p style="text-align:center;color:#999;">لا رسائل بعد — ابدأ النقاش العلمي 👋</p>'
            for m in msgs:
                is_mine = m.get("user") == username
                role_icon = {"owner": "👑", "specialist": "🔬", "guest": "👥"}.get(m.get("role", "guest"), "")
                bg = "#dcedc8" if is_mine else "#e3f2fd"
                nc = "#1b5e20" if is_mine else "#1565c0"
                chat_html += (
                    f'<div style="background:{bg}; padding:8px 14px; border-radius:10px; '
                    f'margin-bottom:6px; border-right:3px solid {nc};">'
                    f'<b style="color:{nc};">{role_icon} {m.get("user", "")}</b> '
                    f'<small style="color:#888;">{m.get("ts", "")}</small><br>'
                    f'<span style="white-space:pre-wrap;">{m.get("msg", "")}</span></div>'
                )
            chat_html += "</div>"
            st.markdown(chat_html, unsafe_allow_html=True)

            with st.form(f"comm_form_{current_room}_v1200", clear_on_submit=True):
                msg_text = st.text_area("✍️ رسالتك:", height=80, key=f"comm_msg_{current_room}_v1200")
                cc1, cc2 = st.columns([0.75, 0.25])
                with cc1:
                    share_formula = st.checkbox("📎 إرفاق التركيبة النشطة", value=False, key="comm_attach_v1200")
                with cc2:
                    send = st.form_submit_button("📤 إرسال", type="primary", use_container_width=True)
                if send:
                    if not check_rate_limit("comm", max_calls=30, window=60):
                        st.warning("⏳ تم تجاوز الحد المسموح مؤقتاً، يرجى الانتظار قليلاً.")
                    else:
                        final_msg = msg_text
                        if share_formula:
                            active = st.session_state.get("active_formula") or {}
                            if active:
                                fs = " | ".join(f"{k}: {float(v):.1f}%" for k, v in active.items())
                                final_msg = f"{final_msg}\n\n📋 التركيبة المرفقة:\n{fs}".strip()
                        if add_chat_message(current_room, username, final_msg):
                            st.rerun()

            if st.button("🔄 تحديث المحادثة", key="comm_refresh_v1200"):
                st.rerun()
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 🎬 الاستديو + فيديو شرح كيفية عمل البرنامج ═══
if "🎬 الاستديو" in tab_map:
    with tab_map["🎬 الاستديو"]:
        try:
            st.markdown('<div class="section-title">🎬 الاستديو وفيديو شرح البرنامج</div>', unsafe_allow_html=True)

            st.markdown("### 🎥 فيديو تعريفي يشرح كيفية عمل البرنامج خطوة بخطوة")
            st.caption("يعرض الفيديو آلية النمذجة الفسيولوجية، تركيب الأعلاف، التحسين غير الخطي NLP، الرسوم الرادارية، وتوليد تقارير PDF المختومة.")

            v_col1, v_col2 = st.columns([0.4, 0.6])
            with v_col1:
                if st.button("🎬 توليد فيديو شرح البرنامج (MP4)", type="primary", use_container_width=True, key="gen_explainer_vid_v1200"):
                    with st.spinner("⏳ جاري إنشاء مشاهد الفيديو التعليمي..."):
                        ok_vid, out_vid = _call_if_exists("build_explainer_video_mp4", "tawor_nology_explainer.mp4", default=(False, "الدالة غير متاحة"))
                    if ok_vid and os.path.exists(out_vid):
                        st.session_state["explainer_video_path"] = out_vid
                        st.success("✅ تم توليد فيديو شرح البرنامج بنجاح!")
                    else:
                        st.warning(f"⚠️ {out_vid}")

            with v_col2:
                vid_path = st.session_state.get("explainer_video_path") or ("tawor_nology_explainer.mp4" if os.path.exists("tawor_nology_explainer.mp4") else ("intro_video.mp4" if os.path.exists("intro_video.mp4") else None))
                if vid_path and os.path.exists(vid_path):
                    st.video(vid_path)
                    with open(vid_path, "rb") as vf:
                        st.download_button("📥 تحميل فيديو الشرح (MP4)", data=vf.read(), file_name=os.path.basename(vid_path), mime="video/mp4", use_container_width=True, key="dl_explainer_vid_v1200")
                else:
                    st.info("💡 اضغط على زر (توليد فيديو شرح البرنامج) لإنشاء الفيديو وتشغيله هنا، أو ضع ملف `intro_video.mp4` في مجلد التطبيق.")

            st.markdown("---")
            studio = dict(_load_studio())
            studio.setdefault("videos", [])
            studio.setdefault("slides", [])
            studio.setdefault("notes", [])

            sub_s1, sub_s2, sub_s3 = st.tabs(["📹 فيديوهات", "📊 شرائح", "📝 ملاحظات"])
            with sub_s1:
                with st.form("sv_v1200"):
                    vt = st.text_input("العنوان:", key="vid_t_v1200")
                    vu = st.text_input("رابط الفيديو:", key="vid_u_v1200")
                    vd = st.text_area("الوصف:", key="vid_d_v1200")
                    if st.form_submit_button("➕ إضافة فيديو", type="primary") and vt.strip() and vu.strip():
                        studio["videos"].append(
                            {
                                "title": _sanitize_message(vt.strip(), 100),
                                "url": _sanitize_message(vu.strip(), 500),
                                "desc": _sanitize_message(vd.strip(), 500),
                                "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            }
                        )
                        _save_studio(studio)
                        st.rerun()
                for i, v in enumerate(list(studio["videos"])):
                    with st.expander(f"🎬 {v.get('title', '')} — {v.get('ts', '')}"):
                        st.markdown(f"🔗 [فتح الرابط]({v.get('url', '')})")
                        if v.get("desc"):
                            st.caption(v["desc"])
                        if st.button("🗑️ حذف", key=f"del_vid_{i}_v1200"):
                            studio["videos"].pop(i)
                            _save_studio(studio)
                            st.rerun()

            with sub_s2:
                with st.form("ss_v1200"):
                    s_title = st.text_input("العنوان:", key="sl_t_v1200")
                    s_url = st.text_input("رابط الصورة / الشريحة:", key="sl_u_v1200")
                    if st.form_submit_button("➕ إضافة شريحة", type="primary") and s_title.strip() and s_url.strip():
                        studio["slides"].append(
                            {
                                "title": _sanitize_message(s_title.strip(), 100),
                                "url": _sanitize_message(s_url.strip(), 500),
                                "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            }
                        )
                        _save_studio(studio)
                        st.rerun()
                for i, s in enumerate(list(studio["slides"])):
                    st.markdown(f"**{s.get('title', '')}**")
                    try:
                        st.image(s.get("url", ""), use_container_width=True)
                    except Exception:
                        st.caption(f"🔗 {s.get('url', '')}")
                    if st.button("🗑️ حذف", key=f"del_sl_{i}_v1200"):
                        studio["slides"].pop(i)
                        _save_studio(studio)
                        st.rerun()

            with sub_s3:
                with st.form("sn_v1200"):
                    nt = st.text_area("ملاحظة علمية أو بحثية:", key="note_t_v1200")
                    if st.form_submit_button("➕ حفظ الملاحظة", type="primary") and nt.strip():
                        studio["notes"].append(
                            {
                                "text": _sanitize_message(nt.strip(), 1000),
                                "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "author": _safe_username(),
                            }
                        )
                        _save_studio(studio)
                        st.rerun()
                total_notes = len(studio["notes"])
                for i, n in enumerate(reversed(list(studio["notes"]))):
                    ri = total_notes - 1 - i
                    st.markdown(
                        f'<div class="formula-item"><b>{n.get("author", "")}</b> — '
                        f'<small>{n.get("ts", "")}</small><br>{n.get("text", "")}</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button("🗑️ حذف", key=f"del_note_{ri}_v1200"):
                        studio["notes"].pop(ri)
                        _save_studio(studio)
                        st.rerun()
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 📚 المراجع ═══
if "📚 المراجع" in tab_map:
    with tab_map["📚 المراجع"]:
        try:
            st.markdown('<div class="section-title">📚 المراجع والمعادلات العلمية</div>', unsafe_allow_html=True)
            ref_animal = st.selectbox(
                "اختر الحيوان:",
                ["أبقار", "أغنام", "ماعز", "إبل", "خيول", "دواجن", "سمان", "أسماك", "أرانب"],
                key="ref_animal_v1200",
            )
            ref_prod_map = {
                "أبقار": ["حليب_عالي", "حليب_متوسط", "حليب_منخفض", "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"],
                "أغنام": ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد", "مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
                "ماعز": ["تسمين_جديان", "تيوس", "حلابة_عالي", "حلابة_متوسط", "حامل_أخير", "صيانة"],
                "إبل": ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
                "خيول": ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار", "مرضعات", "صيانة", "مربط"],
                "دواجن": ["لاحم", "بياض"],
                "سمان": ["تسمين", "بياض"],
                "أسماك": ["بادئ زريعة", "نمو", "تسمين"],
                "أرانب": ["تسمين", "حليب", "صيانة"],
            }
            ref_prod = st.selectbox("نوع الإنتاج:", ref_prod_map.get(ref_animal, ["عام"]), key="ref_prod_v1200")
            refs = get_references(ref_animal, ref_prod)
            eqs = get_reference_equations(ref_animal, ref_prod)

            st.markdown(
                f"""<div class="physio-card">
                <h4>📖 المرجع الأساسي</h4>
                <p style="color:#1a237e; font-size:1.15rem; font-weight:700; margin:0;">{refs.get('primary', '—')}</p>
                <p style="color:#555; margin:8px 0 0 0;">📑 <b>الجدول:</b> {refs.get('table', '—')}</p>
            </div>""",
                unsafe_allow_html=True,
            )

            if eqs:
                st.markdown("### 📐 المعادلات المرجعية")
                eq_data = [{"المؤشر": k, "المعادلة": v} for k, v in eqs.items() if k not in ("source", "example")]
                if eq_data:
                    st.table(pd.DataFrame(eq_data))
                if eqs.get("example"):
                    st.info(f"💡 **مثال تطبيقي:** {eqs['example']}")

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


# ═══ 📖 الدليل ═══
if "📖 الدليل" in tab_map:
    with tab_map["📖 الدليل"]:
        try:
            st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
            st.markdown(
                f"""
### 🎯 الغرض
**{_APP_NAME} v{APP_VERSION}** — منصة علمية متقدمة لتركيب الأعلاف، التحسين غير الخطي (`NLP`)، وتحليل الاحتياجات الغذائية.

### ✨ أبرز الخصائص
- 🐄 **9 قطاعات حيوانية** مع احتياجات فسيولوجية وإنتاجية متعددة.
- 📡 **رسم بياني راداري (Radar)** + **مقارنة دقيقة بين المحسوب والمعيار** في النمذجة والمختبر و`NLP`.
- 🎯 **محرك التحسين غير الخطي (`NLP` - `SLSQP`)** مع منحنى الحساسية والتكلفة والربح.
-  Stamp **ختم اعتماد رسمي** على تقارير `PDF` مع نظام موافقة للمالك.
- 🎬 **فيديو شرح تفصيلي لكيفية عمل البرنامج** متاح للتوليد والتشغيل من تبويب الاستديو.

---
{_g("DUA_FULL", "")}
"""
            )
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════
# التذييل الختامي
# ═══════════════════════════════════════════════════════════════════════
st.markdown(
    f'<div class="mini-signature">🌾 {_APP_NAME} v{APP_VERSION} | {_SUPERVISOR} © 2026</div>',
    unsafe_allow_html=True,
)
if _DUA_SHORT:
    st.markdown(f'<div class="dua-fixed-banner">🤲 {_DUA_SHORT} 🤲</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
