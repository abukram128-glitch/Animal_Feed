# -*- coding: utf-8 -*-
"""
Tawor Nology 11.11.0 — القسم الثاني (مصحّح):
مكتبة الأعلاف، الاحتياجات الغذائية لجميع الأنواع،
محركات LP و NLP، وبدائل الحليب
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    from scipy.optimize import linprog, minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    linprog = None
    minimize = None


# ═══════════════════════════════════════════════════════════════════════
# 🌾 مكتبة الأعلاف الكبرى (36 مادة علفية) — الأسعار بالطن ($)
# الأعمدة: [DP%, CP%, SE, Ca%, P%, سعر/طن, نوع_المادة]
# ═══════════════════════════════════════════════════════════════════════

BIG_FEEDS_LIBRARY = {
    "ذرة صفراء": [8.5, 10.5, 78.0, 0.03, 0.28, 230.0, "طاقة"],
    "شعير مجروش": [9.5, 11.5, 72.0, 0.06, 0.34, 210.0, "طاقة"],
    "قمح مجروش": [10.5, 13.0, 76.0, 0.05, 0.36, 250.0, "طاقة"],
    "ذرة بيضاء (دخن/ذرة رفيعة)": [8.0, 10.0, 75.0, 0.04, 0.30, 195.0, "طاقة"],
    "نخالة قمح": [12.0, 15.5, 58.0, 0.14, 1.15, 165.0, "طاقة/ألياف"],
    "نخالة أرز": [9.5, 12.5, 62.0, 0.08, 1.40, 150.0, "طاقة/ألياف"],
    "دبس قصب السكر (مولاس)": [2.0, 4.0, 65.0, 0.80, 0.08, 170.0, "طاقة"],
    "لب بنجر مجفف": [7.5, 9.5, 68.0, 0.70, 0.10, 180.0, "طاقة/ألياف"],
    "دهن نباتي / زيت صويا": [0.0, 0.0, 185.0, 0.00, 0.00, 950.0, "طاقة مركزة"],
    "شحم حيواني مكرر": [0.0, 0.0, 175.0, 0.00, 0.00, 780.0, "طاقة مركزة"],

    "كسب فول الصويا (44%)": [39.5, 44.0, 75.0, 0.30, 0.65, 440.0, "بروتين"],
    "كسب فول الصويا (48%)": [43.0, 48.0, 77.0, 0.28, 0.68, 475.0, "بروتين"],
    "كسب عباد الشمس": [26.5, 32.0, 62.0, 0.35, 0.90, 295.0, "بروتين"],
    "كسب الفول السوداني": [37.0, 42.0, 72.0, 0.20, 0.58, 380.0, "بروتين"],
    "كسب السمسم": [34.0, 39.0, 71.0, 1.40, 0.85, 360.0, "بروتين"],
    "كسب القطن مقشور": [33.0, 38.0, 66.0, 0.22, 1.05, 310.0, "بروتين"],
    "كسب الكانولا / اللفت": [31.0, 36.0, 67.0, 0.65, 1.10, 325.0, "بروتين"],
    "مسحوق سمك (65%)": [56.0, 65.0, 78.0, 4.50, 2.80, 1150.0, "بروتين حيواني"],
    "مسحوق لحم وعظم (50%)": [42.0, 50.0, 68.0, 8.50, 4.20, 720.0, "بروتين حيواني"],
    "جلوتين الذرة (60%)": [53.0, 60.0, 82.0, 0.05, 0.45, 780.0, "بروتين"],
    "حبوب التقطير المجففة (DDGS)": [23.0, 27.5, 72.0, 0.06, 0.78, 285.0, "بروتين/طاقة"],

    "دريس برسيم حجازي": [13.5, 17.5, 50.0, 1.35, 0.25, 220.0, "خشنة"],
    "قش شعير / قمح": [1.8, 3.8, 34.0, 0.30, 0.08, 95.0, "خشنة"],
    "تبن فول / عدس": [4.5, 7.5, 42.0, 0.95, 0.16, 120.0, "خشنة"],
    "سيلاج ذرة": [5.5, 8.0, 56.0, 0.25, 0.22, 85.0, "خشنة/سيلاج"],
    "حشيش رودس / بانيكم": [8.0, 11.0, 47.0, 0.45, 0.22, 160.0, "خشنة"],
    "أوراق شجر الزيتون مجففة": [5.0, 8.5, 44.0, 1.10, 0.14, 110.0, "خشنة"],

    "حجر جيري / كربونات كالسيوم": [0.0, 0.0, 0.0, 38.00, 0.00, 65.0, "معدنية"],
    "فوسفات ثنائي الكالسيوم (DCP)": [0.0, 0.0, 0.0, 23.00, 18.00, 680.0, "معدنية"],
    "ملح طعام (كلوريد الصوديوم)": [0.0, 0.0, 0.0, 0.00, 0.00, 80.0, "معدنية"],
    "بيكربونات الصوديوم": [0.0, 0.0, 0.0, 0.00, 0.00, 260.0, "معدنية"],
    "مخلوط فيتامينات ومعادن (بريمكس)": [0.0, 0.0, 0.0, 12.00, 2.00, 1800.0, "إضافات"],
    "DL-ميثيونين (99%)": [0.0, 58.0, 0.0, 0.00, 0.00, 3400.0, "أحماض أمينية"],
    "L-ليسين HCl (78%)": [0.0, 94.0, 0.0, 0.00, 0.00, 2200.0, "أحماض أمينية"],
    "خميرة علفية جافة": [38.0, 44.0, 72.0, 0.15, 1.30, 820.0, "إضافات/بروتين"],
    "يوريا علفية (NPN - للمجترات فقط)": [180.0, 281.0, 0.0, 0.00, 0.00, 450.0, "نيتروجين غير بروتيني"],
}

for _k, _v in BIG_FEEDS_LIBRARY.items():
    if len(_v) == 6:
        _v.append("أخرى")


# ═══════════════════════════════════════════════════════════════════════
# 📋 الاحتياجات الغذائية لجميع الأنواع
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class NutritionalRequirements:
    name: str
    DP: float
    CP: float
    SE: float
    Ca: float
    P: float
    DMI_pct_BW: float = 3.0
    notes: str = ""
    reference: str = ""

    @property
    def ME_kcal(self) -> float:
        return round(self.SE * 41.0, 1)


def get_cattle_requirements(production_type: str, milk_yield: float = 20.0,
                            weight_kg: float = 500.0) -> NutritionalRequirements:
    w = max(100.0, float(weight_kg))
    m = max(0.0, float(milk_yield))
    if production_type == "حليب_عالي":
        dp = min(16.0, 9.0 + m * 0.175)
        cp = round(dp / 0.72, 2)
        se = min(78.0, 60.0 + m * 0.35)
        ca = min(1.05, 0.55 + m * 0.003)
        p = min(0.65, 0.33 + m * 0.0015)
        return NutritionalRequirements(
            f"أبقار حليب إنتاج عالي ({m:.0f} كجم/يوم، وزن {w:.0f} كجم)",
            round(dp, 2), cp, round(se, 1), round(ca, 2), round(p, 2),
            3.8, "أبقار عالية الإدرار؛ تأمين ألياف فعالة (NDF) ومنع الحماض.",
            "NRC (2001) — Table 15-1")
    elif production_type == "حليب_متوسط":
        dp = min(14.0, 8.5 + m * 0.17)
        cp = round(dp / 0.72, 2)
        se = min(74.0, 55.0 + m * 0.30)
        ca = min(0.90, 0.50 + m * 0.0025)
        p = min(0.55, 0.30 + m * 0.0012)
        return NutritionalRequirements(
            f"أبقار حليب إنتاج متوسط ({m:.0f} كجم/يوم، وزن {w:.0f} كجم)",
            round(dp, 2), cp, round(se, 1), round(ca, 2), round(p, 2),
            3.3, "إنتاج متوسط؛ موازنة الطاقة والبروتين وحموضة الكرش.",
            "NRC (2001) — Table 15-1")
    elif production_type == "حليب_منخفض":
        dp = min(12.5, 8.0 + m * 0.16)
        cp = round(dp / 0.75, 2)
        se = min(68.0, 52.0 + m * 0.25)
        return NutritionalRequirements(
            f"أبقار حليب إنتاج منخفض ({m:.0f} كجم/يوم، وزن {w:.0f} كجم)",
            round(dp, 2), cp, round(se, 1), 0.50, 0.30,
            2.8, "إنتاج منخفض أو نهاية موسم الحليب.",
            "NRC (2001) — Table 15-1")
    elif production_type == "تسمين_مكثف":
        return NutritionalRequirements(
            f"أبقار تسمين مكثف (وزن {w:.0f} كجم)",
            11.5, 14.5, 72.0, 0.55, 0.35, 2.9,
            "تسمين سريع؛ رفع كثافة الطاقة تدريجياً وتجنب اضطرابات الكرش.",
            "NRC (1996 / 2001)")
    elif production_type == "تسمين_عادي":
        return NutritionalRequirements(
            f"أبقار تسمين عادي (وزن {w:.0f} كجم)",
            9.5, 12.0, 65.0, 0.45, 0.30, 2.6,
            "تسمين اقتصادي معتدل يعتمد على الحبوب والأعلاف الخشنة الجيدة.",
            "NRC (1996)")
    elif production_type == "حمل_أخير":
        return NutritionalRequirements(
            f"أبقار حامل في الثلث الأخير (وزن {w:.0f} كجم)",
            11.5, 14.5, 67.0, 0.65, 0.38, 2.2,
            "دعم نمو الجنين وتهيئة الضرع قبل الولادة مع ضبط الكالسيوم.",
            "NRC (2001)")
    else:
        return NutritionalRequirements(
            f"أبقار صيانة (وزن {w:.0f} كجم)",
            7.5, 10.0, 53.0, 0.35, 0.25, 2.0,
            "حفظ الوزن والحالة الفسيولوجية.",
            "NRC (2001)")


def get_sheep_requirements(production_type: str, is_male: bool = True,
                           lambs_count: int = 1) -> NutritionalRequirements:
    lc = max(1, int(lambs_count))
    if production_type == "تسمين_مكثف":
        return NutritionalRequirements(
            "أغنام تسمين مكثف", 11.5, 14.5, 64.0, 0.60, 0.35, 3.6,
            "حملان تسمين؛ يُنصح بنسبة Ca:P حوالي 1.7:1 إلى 2:1 للوقاية من حصوات البول.",
            "NRC (2007)")
    elif production_type == "تسمين_عادي":
        return NutritionalRequirements(
            "أغنام تسمين عادي", 9.5, 12.0, 59.0, 0.50, 0.30, 3.2,
            "نمو وتسمين معتدل.", "NRC (2007)")
    elif production_type == "مرضعات":
        dp = min(15.5, 10.5 + (lc - 1) * 1.5)
        cp = round(dp / 0.72, 2)
        se = min(68.0, 60.0 + (lc - 1) * 3.0)
        return NutritionalRequirements(
            f"نعاج مرضعات ({lc} مولود)", round(dp, 2), cp, round(se, 1), 0.65, 0.38, 4.0,
            "ارتفاع احتياجات البروتين والطاقة لإنتاج الحليب.", "NRC (2007)")
    elif production_type == "حامل_أخير":
        return NutritionalRequirements(
            "نعاج حامل في الشهر الأخير", 10.5, 13.5, 62.0, 0.60, 0.35, 2.8,
            "الوقاية من تسمم الحمل بإمداد كافٍ بالطاقة والبروتين.", "NRC (2007)")
    elif production_type == "حامل_متوسط":
        return NutritionalRequirements(
            "نعاج حامل في المرحلة المتوسطة", 8.5, 11.0, 55.0, 0.42, 0.26, 2.4,
            "مرحلة حمل متوسطة.", "NRC (2007)")
    elif production_type == "حملان_تيد":
        return NutritionalRequirements(
            "حملان فطام / نمو مبكر", 11.0, 14.0, 63.0, 0.58, 0.34, 3.8,
            "نمو سريع بعد الفطام.", "NRC (2007)")
    else:
        return NutritionalRequirements(
            "أغنام صيانة", 7.2, 9.5, 48.0, 0.35, 0.22, 2.2,
            "صيانة أساسية.", "NRC (2007)")


def get_goat_requirements(production_type: str, is_male: bool = False,
                          milk_yield: float = 3.0) -> NutritionalRequirements:
    m = max(0.0, float(milk_yield))
    if production_type == "حلابة_عالي":
        dp = min(16.0, 9.5 + m * 0.35)
        cp = round(dp / 0.72, 2)
        se = min(72.0, 58.0 + m * 1.8)
        return NutritionalRequirements(
            f"ماعز حلابة إنتاج عالي ({m:.1f} لتر/يوم)", round(dp, 2), cp, round(se, 1), 0.70, 0.40, 4.2,
            "الماعز الحلوب يتطلب نسبة بروتين وطاقة عالية نسبياً.", "NRC (2007)")
    elif production_type == "حلابة_متوسط":
        dp = min(13.5, 8.5 + m * 0.30)
        cp = round(dp / 0.72, 2)
        se = min(65.0, 54.0 + m * 1.5)
        return NutritionalRequirements(
            f"ماعز حلابة إنتاج متوسط ({m:.1f} لتر/يوم)", round(dp, 2), cp, round(se, 1), 0.58, 0.34, 3.6,
            "إنتاج حليب متوسط.", "NRC (2007)")
    elif production_type == "تسمين_جديان":
        return NutritionalRequirements(
            "جديان تسمين ونمو", 11.0, 14.0, 62.0, 0.60, 0.35, 3.5,
            "نمو وتسمين الجديان.", "NRC (2007)")
    elif production_type == "تيوس":
        return NutritionalRequirements(
            "تيوس التلقيح والإنتاج", 9.0, 11.5, 57.0, 0.48, 0.30, 2.8,
            "دعم النشاط التناسلي والحالة البدنية.", "NRC (2007)")
    elif production_type == "حامل_أخير":
        return NutritionalRequirements(
            "ماعز حامل في الثلث الأخير", 10.0, 13.0, 60.0, 0.58, 0.34, 2.8,
            "فترة الحمل المتأخرة.", "NRC (2007)")
    else:
        return NutritionalRequirements(
            "ماعز صيانة", 6.8, 9.0, 46.0, 0.35, 0.22, 2.3,
            "صيانة الماعز.", "NRC (2007)")


def get_camel_requirements(production_type: str, milk_yield: float = 8.0) -> NutritionalRequirements:
    m = max(0.0, float(milk_yield))
    if production_type == "حليب":
        dp = min(15.0, 10.5 + m * 0.20)
        cp = round(dp / 0.72, 2)
        se = min(70.0, 62.0 + m * 0.40)
        return NutritionalRequirements(
            f"إبل حلوب ({m:.1f} لتر/يوم)", round(dp, 2), cp, round(se, 1), 0.65, 0.40, 2.8,
            "تأمين الطاقة والبروتين لإنتاج الحليب مع مراعاة طبيعة هضم الإبل.", "FAO (2010)")
    elif production_type == "تسمين":
        return NutritionalRequirements(
            "إبل تسمين", 9.5, 12.0, 65.0, 0.50, 0.32, 2.5,
            "تسمين الإبل.", "FAO (2010)")
    elif production_type == "نمو":
        return NutritionalRequirements(
            "حيران / إبل نامية", 10.5, 13.5, 60.0, 0.55, 0.35, 3.0,
            "مرحلة النمو.", "FAO (2010)")
    elif production_type == "سباق":
        return NutritionalRequirements(
            "إبل السباق والهجن", 14.0, 17.5, 72.0, 0.65, 0.42, 2.6,
            "طاقة عالية وأحماض أمينية ومعادن لدعم الأداء البدني.", "FAO (2010)")
    else:
        return NutritionalRequirements(
            "إبل صيانة", 7.0, 9.2, 48.0, 0.35, 0.22, 1.8,
            "صيانة الإبل.", "FAO (2010)")


def get_horse_requirements(production_type: str) -> NutritionalRequirements:
    if production_type == "رياضة_مكثف":
        return NutritionalRequirements(
            "خيول عمل / سباق مكثف", 10.5, 13.5, 70.0, 0.65, 0.40, 2.4,
            "جهد عضلي مرتفع؛ تقسيم العلف على وجبات صغيرة متعددة.", "NRC (2007)")
    elif production_type == "رياضة_عادي":
        return NutritionalRequirements(
            "خيول ركوب / عمل متوسط", 9.0, 11.5, 63.0, 0.50, 0.32, 2.1,
            "جهد معتدل.", "NRC (2007)")
    elif production_type == "نمو_أمهار":
        return NutritionalRequirements(
            "أمهار نامية", 12.0, 15.0, 65.0, 0.75, 0.45, 2.6,
            "نمو العظام والعضلات؛ توازن الكالسيوم والفوسفور والليسين.", "NRC (2007)")
    elif production_type == "مرضعات":
        return NutritionalRequirements(
            "أفراس مرضعات", 12.5, 15.5, 68.0, 0.70, 0.45, 2.7,
            "إدرار الحليب ودعم صحة الفرس.", "NRC (2007)")
    else:
        return NutritionalRequirements(
            "خيول صيانة", 7.2, 9.5, 53.0, 0.35, 0.22, 1.8,
            "صيانة الخيول.", "NRC (2007)")


def get_poultry_requirements(production_type: str, stage: str = "نامي") -> NutritionalRequirements:
    if production_type == "بياض":
        return NutritionalRequirements(
            "دجاج بياض (إنتاج بيض)", 15.5, 18.0, 72.0, 3.80, 0.45, 5.5,
            "ارتفاع الكالسيوم لتكوين قشرة البيضة مع موازنة الفوسفور المتاح.",
            "NRC (1994) / Lohmann (2020)")
    stage_map = {
        "بادي": ("دجاج لاحم — عليقة بادي (0-10 أيام)", 20.0, 23.0, 76.0, 1.00, 0.48, 8.0),
        "نامي": ("دجاج لاحم — عليقة نامي (11-24 يوم)", 18.0, 21.0, 75.5, 0.90, 0.44, 7.0),
        "ناهي": ("دجاج لاحم — عليقة ناهي (25+ يوم)", 16.5, 19.0, 75.0, 0.80, 0.40, 6.0),
    }
    name, dp, cp, se, ca, p, dmi = stage_map.get(stage, stage_map["نامي"])
    return NutritionalRequirements(
        name, dp, cp, se, ca, p, dmi,
        "موازنة الطاقة الممثلة (ME) مع البروتين الخام والأحماض الأمينية الأساسية.",
        "Ross 308 (2020)")


def get_quail_requirements(production_type: str = "تسمين") -> NutritionalRequirements:
    if production_type == "بياض":
        return NutritionalRequirements(
            "سمان بياض", 15.0, 20.0, 70.0, 2.80, 0.55, 8.5,
            "سمان إنتاج البيض.", "NRC (1994)")
    return NutritionalRequirements(
        "سمان تسمين", 18.5, 24.0, 72.0, 0.90, 0.45, 9.0,
        "سمان التسمين؛ يتطلب نسبة بروتين عالية في المراحل الأولى.", "NRC (1994)")


def get_fish_requirements(species: str = "البلطي النيلي", stage: str = "نمو") -> NutritionalRequirements:
    stage_map = {
        "بادئ": (f"أسماك {species} — مرحلة البادئ", 32.0, 40.0, 75.0, 1.20, 0.70, 5.0),
        "نمو": (f"أسماك {species} — مرحلة النمو", 25.0, 32.0, 73.0, 1.00, 0.60, 3.5),
        "تسمين": (f"أسماك {species} — مرحلة التسمين", 22.0, 28.0, 72.0, 0.90, 0.55, 2.5),
    }
    name, dp, cp, se, ca, p, dmi = stage_map.get(stage, stage_map["نمو"])
    return NutritionalRequirements(
        name, dp, cp, se, ca, p, dmi,
        "مراعاة ثبات الكريات في الماء وجودة البروتين والطاقة.", "NRC (2011)")


def get_rabbit_requirements(production_type: str = "تسمين") -> NutritionalRequirements:
    if production_type == "حليب":
        return NutritionalRequirements(
            "أرانب مرضعات / حليب", 18.0, 20.0, 66.0, 1.10, 0.55, 5.0,
            "إنتاج الحليب وتغذية الخلفة.", "NRC (2007)")
    elif production_type == "صيانة":
        return NutritionalRequirements(
            "أرانب صيانة", 12.0, 14.0, 58.0, 0.60, 0.35, 3.5,
            "صيانة أساسية.", "NRC (2007)")
    return NutritionalRequirements(
        "أرانب تسمين", 15.0, 17.0, 63.0, 0.85, 0.45, 4.5,
        "تسمين الأرانب؛ توفير ألياف مناسبة لصحة الجهاز الهضمي.", "NRC (2007)")


# ═══════════════════════════════════════════════════════════════════════
# ⚙️ محرك التركيب الأمثل LP + NLP (مصحّح الوحدات والتكاليف)
# ═══════════════════════════════════════════════════════════════════════

def _build_ingredient_arrays(ingredients: List[str], feed_lib: Dict, custom_prices: Dict):
    n = len(ingredients)
    prices = np.zeros(n, dtype=float)
    dp_vals = np.zeros(n, dtype=float)
    cp_vals = np.zeros(n, dtype=float)
    se_vals = np.zeros(n, dtype=float)
    me_vals = np.zeros(n, dtype=float)
    ca_vals = np.zeros(n, dtype=float)
    p_vals = np.zeros(n, dtype=float)

    for i, ing in enumerate(ingredients):
        row = feed_lib[ing]
        raw_price = custom_prices.get(ing, row[5])
        prices[i] = float(raw_price) / 1000.0  # $/kg لكل 1% في الخلطة (حيث 1% = 0.01 طن/100 كجم)
        dp_vals[i] = float(row[0])
        cp_vals[i] = float(row[1])
        se_vals[i] = float(row[2])
        me_vals[i] = float(row[2]) * 41.0
        ca_vals[i] = float(row[3])
        p_vals[i] = float(row[4])

    return prices, dp_vals, cp_vals, se_vals, me_vals, ca_vals, p_vals


def _default_bounds(ingredients: List[str], feed_lib: Dict):
    bounds = []
    for ing in ingredients:
        stype = feed_lib[ing][6]
        if "يوريا" in ing:
            bounds.append((0.0, 1.5))
        elif "ميثيونين" in ing or "ليسين" in ing:
            bounds.append((0.0, 0.6))
        elif "بريمكس" in ing:
            bounds.append((0.0, 0.5))
        elif "ملح" in ing or "بيكربونات" in ing:
            bounds.append((0.0, 1.0))
        elif "جيري" in ing or "DCP" in ing or "معدنية" in stype:
            bounds.append((0.0, 3.0))
        elif "طاقة مركزة" in stype:
            bounds.append((0.0, 4.0))
        elif "خشنة" in stype:
            bounds.append((0.0, 35.0))
        else:
            bounds.append((0.0, 65.0))
    return bounds


def optimize_ration_lp(ingredients: List[str], target_cp: float, target_se: float,
                       target_dp: float, custom_prices: Dict,
                       feed_lib: Optional[Dict] = None):
    lib = feed_lib if feed_lib is not None else BIG_FEEDS_LIBRARY
    valid = [x for x in ingredients if x in lib]
    if not valid:
        return None

    prices, dp_v, cp_v, se_v, me_v, ca_v, p_v = _build_ingredient_arrays(valid, lib, custom_prices)
    bounds = _default_bounds(valid, lib)
    n = len(valid)

    # نحل بنسب مئوية x_i بحيث مجموعها = 100.0
    if SCIPY_AVAILABLE and linprog is not None:
        A_eq = np.ones((1, n))
        b_eq = np.array([100.0])

        # قيود عدم المساواة (A_ub @ x <= b_ub)
        # 1) CP >= target_cp * 0.95  => -cp_v @ x <= -target_cp * 95.0
        # 2) CP <= target_cp * 1.15  =>  cp_v @ x <=  target_cp * 115.0
        # 3) ME >= target_me * 0.90  => -me_v @ x <= -target_me * 90.0
        target_me = float(target_se) * 41.0
        A_ub = np.vstack([
            -cp_v,
            cp_v,
            -me_v,
        ])
        b_ub = np.array([
            -float(target_cp) * 95.0,
            float(target_cp) * 115.0,
            -target_me * 90.0,
        ])

        res = linprog(prices, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
        if res.success and res.x is not None:
            pcts = np.clip(res.x, 0.0, 100.0)
            s = float(np.sum(pcts))
            if s > 0:
                pcts = pcts * (100.0 / s)
            w = pcts / 100.0
            cost_per_ton = float(np.sum(w * np.array([custom_prices.get(x, lib[x][5]) for x in valid])))
            return {
                "formula": {valid[i]: round(float(pcts[i]), 2) for i in range(n) if pcts[i] > 0.01},
                "cost_per_ton": round(cost_per_ton, 2),
                "CP": round(float(np.sum(w * cp_v)), 2),
                "DP": round(float(np.sum(w * dp_v)), 2),
                "SE": round(float(np.sum(w * se_v)), 2),
                "ME": round(float(np.sum(w * me_v)), 1),
                "Ca": round(float(np.sum(w * ca_v)), 2),
                "P": round(float(np.sum(w * p_v)), 2),
                "solver": "HiGHS LP",
            }

    # احتياطي متوازن إذا لم يتوفر SciPy أو لم يجد حلاً خطياً
    pcts = np.full(n, 100.0 / n)
    w = pcts / 100.0
    cost_per_ton = float(np.sum(w * np.array([custom_prices.get(x, lib[x][5]) for x in valid])))
    return {
        "formula": {valid[i]: round(float(pcts[i]), 2) for i in range(n)},
        "cost_per_ton": round(cost_per_ton, 2),
        "CP": round(float(np.sum(w * cp_v)), 2),
        "DP": round(float(np.sum(w * dp_v)), 2),
        "SE": round(float(np.sum(w * se_v)), 2),
        "ME": round(float(np.sum(w * me_v)), 1),
        "Ca": round(float(np.sum(w * ca_v)), 2),
        "P": round(float(np.sum(w * p_v)), 2),
        "solver": "Balanced Fallback",
    }


def optimize_ration_nlp(ingredients: List[str], target_cp: float, target_me: float,
                        custom_prices: Dict, feed_lib: Optional[Dict] = None):
    lib = feed_lib if feed_lib is not None else BIG_FEEDS_LIBRARY
    valid = [x for x in ingredients if x in lib]
    if not valid:
        return None

    prices, dp_v, cp_v, se_v, me_v, ca_v, p_v = _build_ingredient_arrays(valid, lib, custom_prices)
    bounds = _default_bounds(valid, lib)
    n = len(valid)
    t_me = max(1.0, float(target_me))
    t_cp = max(0.1, float(target_cp))

    def objective(x):
        w = x / 100.0
        cost = float(np.sum(w * np.array([custom_prices.get(valid[i], lib[valid[i]][5]) for i in range(n)])))
        cur_me = max(0.0, float(np.sum(w * me_v)))
        cur_cp = max(0.0, float(np.sum(w * cp_v)))
        penalty_me = ((max(0.0, t_me * 0.92 - cur_me) / t_me) ** 2) * 5000.0
        penalty_cp = ((max(0.0, t_cp * 0.92 - cur_cp) / t_cp) ** 2) * 5000.0
        excess_cp = ((max(0.0, cur_cp - t_cp * 1.25) / t_cp) ** 2) * 800.0
        return cost + penalty_me + penalty_cp + excess_cp

    x0 = np.array([b[1] * 0.3 if b[1] < 100 else 100.0 / n for b in bounds], dtype=float)
    if np.sum(x0) > 0:
        x0 = x0 * (100.0 / np.sum(x0))
    else:
        x0 = np.full(n, 100.0 / n)

    if SCIPY_AVAILABLE and minimize is not None:
        cons = [{"type": "eq", "fun": lambda x: float(np.sum(x)) - 100.0}]
        res = minimize(objective, x0, method="SLSQP", bounds=bounds, constraints=cons,
                       options={"maxiter": 300, "ftol": 1e-7})
        pcts = np.clip(res.x if res.x is not None else x0, 0.0, 100.0)
    else:
        pcts = x0

    s = float(np.sum(pcts))
    pcts = pcts * (100.0 / s) if s > 0 else np.full(n, 100.0 / n)
    w = pcts / 100.0
    cost_per_ton = float(np.sum(w * np.array([custom_prices.get(valid[i], lib[valid[i]][5]) for i in range(n)])))

    return {
        "formula": {valid[i]: round(float(pcts[i]), 2) for i in range(n) if pcts[i] > 0.01},
        "cost_per_ton": round(cost_per_ton, 2),
        "CP": round(float(np.sum(w * cp_v)), 2),
        "DP": round(float(np.sum(w * dp_v)), 2),
        "SE": round(float(np.sum(w * se_v)), 2),
        "ME": round(float(np.sum(w * me_v)), 1),
        "Ca": round(float(np.sum(w * ca_v)), 2),
        "P": round(float(np.sum(w * p_v)), 2),
        "solver": "SLSQP NLP",
    }


def auto_formulate_smart(animal_type: str, production_type: str,
                         available_ingredients: List[str], custom_prices: Dict,
                         feed_lib: Optional[Dict] = None):
    lib = feed_lib if feed_lib is not None else BIG_FEEDS_LIBRARY
    req_info = _get_requirement_for_nlp(animal_type, production_type)
    target_me = float(req_info.get("ME", 2800.0))
    target_cp = float(req_info.get("CP", 16.0))
    target_dp = float(req_info.get("DP", 12.0))
    target_se = target_me / 41.0

    valid = [x for x in available_ingredients if x in lib]
    if not valid:
        valid = ["ذرة صفراء", "كسب فول الصويا (44%)", "نخالة قمح", "حجر جيري / كربونات كالسيوم"]

    lp_res = optimize_ration_lp(valid, target_cp, target_se, target_dp, custom_prices, lib)
    nlp_res = optimize_ration_nlp(valid, target_cp, target_me, custom_prices, lib)

    chosen = nlp_res if nlp_res is not None else lp_res
    if chosen is None:
        fallback = {valid[0]: 100.0}
        # إصلاح قسمة السعر على 1000 ليعطي التكلفة الصحيحة لكل كجم ثم ضربها في 1000 للطن
        price_per_ton = float(custom_prices.get(valid[0], lib[valid[0]][5]))
        cost_per_ton = round(price_per_ton, 2)
        row = lib[valid[0]]
        return {
            "formula": fallback,
            "cost_per_ton": cost_per_ton,
            "CP": row[1],
            "DP": row[0],
            "SE": row[2],
            "ME": round(row[2] * 41.0, 1),
            "Ca": row[3],
            "P": row[4],
            "solver": "Emergency Fallback",
        }

    chosen["target_CP"] = round(target_cp, 2)
    chosen["target_ME"] = round(target_me, 1)
    chosen["lp_comparison"] = lp_res
    chosen["nlp_comparison"] = nlp_res
    return chosen


# ═══════════════════════════════════════════════════════════════════════
# 🍼 بدائل الحليب للرضع (عجول، حملان، جديان، حيران، أمهار)
# ═══════════════════════════════════════════════════════════════════════

MILK_REPLACERS = {
    "عجول_أبقار": {
        "title": "بديل حليب العجول الرضع",
        "CP": 22.0,
        "fat": 17.0,
        "lactose": 44.0,
        "dilution_g_per_L": 125.0,
        "feeding_pct_BW": 12.0,
        "ingredients": {
            "حليب فرز مجفف (SMP)": 45.0,
            "شرش حلو مجفف (WPC/Whey)": 25.0,
            "دهن نباتي / زيت صويا": 17.0,
            "نشا ميسر / دقيق قمح معالج": 10.0,
            "مخلوط فيتامينات ومعادن (بريمكس)": 2.0,
            "L-ليسين HCl (78%)": 0.7,
            "DL-ميثيونين (99%)": 0.3,
        },
        "notes": "تُخلط 125 جم بودرة لكل 1 لتر ماء دافئ (39-40°م) وتُقدم في زجاجات أو دلاء نظيفة.",
    },
    "حملان_أغنام": {
        "title": "بديل حليب الحملان الرضع",
        "CP": 24.0,
        "fat": 22.0,
        "lactose": 40.0,
        "dilution_g_per_L": 160.0,
        "feeding_pct_BW": 15.0,
        "ingredients": {
            "حليب فرز مجفف (SMP)": 40.0,
            "شرش حلو مجفف (WPC/Whey)": 25.0,
            "دهن نباتي / زيت صويا": 22.0,
            "خميرة علفية جافة": 11.5,
            "مخلوط فيتامينات ومعادن (بريمكس)": 1.5,
        },
        "notes": "تغذية متكررة (3-4 وجبات يومياً) في الأسابيع الأولى لضمان نمو سليم وتجنب الإسهالات.",
    },
    "جديان_ماعز": {
        "title": "بديل حليب الجديان الرضع",
        "CP": 24.0,
        "fat": 21.0,
        "lactose": 41.0,
        "dilution_g_per_L": 150.0,
        "feeding_pct_BW": 15.0,
        "ingredients": {
            "حليب فرز مجفف (SMP)": 42.0,
            "شرش حلو مجفف (WPC/Whey)": 24.0,
            "دهن نباتي / زيت صويا": 21.0,
            "خميرة علفية جافة": 11.5,
            "مخلوط فيتامينات ومعادن (بريمكس)": 1.5,
        },
        "notes": "مناسب للجديان في حال نقص حليب الأم أو التوائم.",
    },
    "حيران_إبل": {
        "title": "بديل حليب الحيران الرضع",
        "CP": 23.0,
        "fat": 18.0,
        "lactose": 42.0,
        "dilution_g_per_L": 135.0,
        "feeding_pct_BW": 13.0,
        "ingredients": {
            "حليب فرز مجفف (SMP)": 44.0,
            "شرش حلو مجفف (WPC/Whey)": 25.0,
            "دهن نباتي / زيت صويا": 18.0,
            "نشا ميسر / دقيق قمح معالج": 11.2,
            "مخلوط فيتامينات ومعادن (بريمكس)": 1.8,
        },
        "notes": "تقديم ماء شرب عذب وعلف بادئ ناعم تدريجياً بدءاً من الأسبوع الثاني.",
    },
    "أمهار_خيول": {
        "title": "بديل حليب الأمهار الرضع",
        "CP": 21.0,
        "fat": 14.0,
        "lactose": 48.0,
        "dilution_g_per_L": 110.0,
        "feeding_pct_BW": 14.0,
        "ingredients": {
            "حليب فرز مجفف (SMP)": 40.0,
            "شرش حلو مجفف (WPC/Whey)": 35.0,
            "دهن نباتي / زيت صويا": 14.0,
            "نشا ميسر / دقيق قمح معالج": 9.0,
            "مخلوط فيتامينات ومعادن (بريمكس)": 2.0,
        },
        "notes": "يتميز بارتفاع اللاكتوز وانخفاض الدهن نسبياً مقارنة بحليب المجترات.",
    },
}


def calc_milk_replacer_schedule(species_key: str, birth_weight_kg: float,
                                days: int = 45, price_per_kg: float = 2.5) -> List[Dict]:
    cfg = MILK_REPLACERS.get(species_key, MILK_REPLACERS["عجول_أبقار"])
    bw = max(1.0, float(birth_weight_kg))
    n_days = max(1, min(180, int(days)))
    dil = float(cfg["dilution_g_per_L"])
    pct_bw = float(cfg["feeding_pct_BW"]) / 100.0
    schedule = []
    for d in range(1, n_days + 1):
        # نمو تقديري يومي بسيط
        cur_bw = bw * (1.0 + 0.012 * (d - 1))
        milk_liters = round(cur_bw * pct_bw, 2)
        powder_g = round(milk_liters * dil, 1)
        daily_cost = round((powder_g / 1000.0) * float(price_per_kg), 3)
        schedule.append({
            "day": d,
            "est_weight_kg": round(cur_bw, 2),
            "milk_liters": milk_liters,
            "powder_g": powder_g,
            "daily_cost": daily_cost,
        })
    return schedule

# -*- coding: utf-8 -*-
"""
Tawor Nology 11.11.0 — القسم الثالث (مصحّح):
حسابات المربط والتهوية، الرسم ثلاثي الأبعاد للمربط والخيول،
وتوليد تقارير PDF العربية
"""

import io
import os
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
import streamlit as st

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    go = None

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
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
# 🏠 حسابات المربط والتهوية والاحتياجات البيئية للخيول
# ═══════════════════════════════════════════════════════════════════════

def calculate_barn_requirements(horses_count: int, stall_size_m2: float = 12.25,
                               aisle_width_m: float = 3.5, ceiling_height_m: float = 3.6,
                               season: str = "صيف", bedding_type: str = "نشارة خشب") -> Dict:
    n_horses = max(1, int(horses_count))
    stall_area = max(9.0, float(stall_size_m2))
    side_len = float(np.sqrt(stall_area))
    aisle_w = max(2.5, float(aisle_width_m))
    ceil_h = max(2.8, float(ceiling_height_m))

    # توزيع الصفوف والممرات بشكل عملي
    stalls_area_total = n_horses * stall_area
    row_length = max(side_len, n_horses * side_len)
    aisle_area = row_length * aisle_w
    service_area = max(12.0, 0.15 * (stalls_area_total + aisle_area))
    total_area = round(stalls_area_total + aisle_area + service_area, 2)
    total_volume_m3 = round(total_area * ceil_h, 1)

    # معدلات التهوية (تجديد الهواء في الساعة ACH) حسب الموسم
    if "شتاء" in season:
        ach = 5
        vent_note = "تهوية شتوية مضبوطة (5 تجديدات/ساعة) لتقليل فقد الحرارة ومنع الرطوبة والأمونيا."
    elif "اعتدال" in season or "ربيع" in season or "خريف" in season:
        ach = 12
        vent_note = "تهوية معتدلة (12 تجديد/ساعة) للحفاظ على جودة الهواء دون تيارات هوائية مباشرة."
    else:
        ach = 25
        vent_note = "تهوية صيفية مكثفة (25 تجديد/ساعة) لتصريف الحرارة والرطوبة وتقليل الإجهاد الحراري."

    airflow_m3_per_hr = round(total_volume_m3 * ach, 0)

    # الماء والفرشة والعلف اليومي التقديري للحصان الواحد
    water_per_horse_l = 55.0 if "صيف" in season else 40.0
    total_water_l = round(n_horses * water_per_horse_l, 0)

    bedding_factor = {
        "نشارة خشب": 6.0,
        "قش شعير نظيف": 7.5,
        "حصائر مطاطية + فرشة خفيفة": 3.0,
        "بيت موس / ألياف": 5.5,
    }.get(bedding_type, 6.0)
    daily_bedding_kg = round(n_horses * bedding_factor, 1)

    return {
        "horses_count": n_horses,
        "stall_area_m2": round(stall_area, 2),
        "stall_side_m": round(side_len, 2),
        "aisle_width_m": round(aisle_w, 2),
        "ceiling_height_m": round(ceil_h, 2),
        "total_area_m2": total_area,
        "total_volume_m3": total_volume_m3,
        "season": season,
        "ach": ach,
        "airflow_m3_per_hr": airflow_m3_per_hr,
        "water_per_horse_l": water_per_horse_l,
        "total_water_l": total_water_l,
        "bedding_type": bedding_type,
        "daily_bedding_kg": daily_bedding_kg,
        "vent_note": vent_note,
        "reference": "NRC (2007) + MWPS-1 Structures Handbook",
    }


# ═══════════════════════════════════════════════════════════════════════
# 🎨 رسم ثلاثي الأبعاد للمربط والخيول (Plotly 3D) — مصحّح
# ═══════════════════════════════════════════════════════════════════════

def _box_mesh(x0: float, y0: float, z0: float, dx: float, dy: float, dz: float,
              color: str, name: str = "", opacity: float = 0.85, showlegend: bool = False):
    x1, y1, z1 = x0 + dx, y0 + dy, z0 + dz
    vx = [x0, x1, x1, x0, x0, x1, x1, x0]
    vy = [y0, y0, y1, y1, y0, y0, y1, y1]
    vz = [z0, z0, z0, z0, z1, z1, z1, z1]
    i = [0, 0, 4, 4, 0, 1, 2, 3, 0, 1, 5, 4]
    j = [1, 2, 5, 6, 1, 5, 6, 2, 3, 2, 6, 7]
    k = [2, 3, 6, 7, 5, 6, 7, 3, 7, 6, 7, 4]
    return go.Mesh3d(
        x=vx, y=vy, z=vz,
        i=i, j=j, k=k,
        color=color,
        opacity=opacity,
        name=name if name else None,
        showlegend=showlegend,
        flatshading=True,
    )


def create_barn_3d_figure(horses_count: int = 4, stall_size_m2: float = 12.25,
                          aisle_width_m: float = 3.5, ceiling_height_m: float = 3.6,
                          show_roof: bool = True, show_horses: bool = True):
    if not PLOTLY_AVAILABLE or go is None:
        return None

    n_horses = max(1, min(16, int(horses_count)))
    side = float(np.sqrt(max(9.0, float(stall_size_m2))))
    aisle = max(2.5, float(aisle_width_m))
    ceil_h = max(2.8, float(ceiling_height_m))

    # صفان متقابلان حول ممر مركزي لتقليل الطول وضبط التناسب
    per_row = int(np.ceil(n_horses / 2.0))
    barn_len = max(side * 2.0, per_row * side + 1.0)
    barn_wid = side * 2.0 + aisle + 1.0

    traces = []

    # أرضية المربط
    traces.append(_box_mesh(-0.5, -0.5, -0.05, barn_len + 1.0, barn_wid + 1.0, 0.05,
                             "#d7ccc8", "الأرضية", opacity=0.95, showlegend=True))

    # الممر المركزي
    aisle_y0 = side + 0.25
    traces.append(_box_mesh(0.0, aisle_y0, 0.0, barn_len, aisle, 0.02,
                             "#90a4ae", "الممر المركزي", opacity=0.80, showlegend=True))

    # السقف (اختياري)
    if show_roof:
        traces.append(_box_mesh(-0.5, -0.5, ceil_h, barn_len + 1.0, barn_wid + 1.0, 0.15,
                                 "#5d4037", "السقف", opacity=0.35, showlegend=True))

    placed = 0
    for row_idx in range(2):
        if placed >= n_horses:
            break
        y_start = 0.25 if row_idx == 0 else (side + aisle + 0.25)
        for col_idx in range(per_row):
            if placed >= n_horses:
                break
            x_start = col_idx * side + 0.25
            wall_h = min(1.55, ceil_h * 0.45)
            post_h = min(2.40, ceil_h * 0.70)

            # أرضية الإسطبل / الفرشة
            traces.append(_box_mesh(x_start + 0.05, y_start + 0.05, 0.0,
                                     side - 0.1, side - 0.1, 0.04,
                                     "#ffe082", "فرشة الإسطبل" if placed == 0 else "",
                                     opacity=0.85, showlegend=(placed == 0)))

            # الجدران الجانبية للإسطبل
            traces.append(_box_mesh(x_start, y_start, 0.0, 0.08, side, wall_h,
                                     "#8d6e63", "جدران الإسطبل" if placed == 0 else "",
                                     opacity=0.85, showlegend=(placed == 0)))
            traces.append(_box_mesh(x_start + side - 0.08, y_start, 0.0, 0.08, side, wall_h,
                                     "#8d6e63", opacity=0.85, showlegend=False))

            # أعمدة الزوايا
            for px, py in [(x_start, y_start), (x_start + side - 0.1, y_start),
                           (x_start, y_start + side - 0.1), (x_start + side - 0.1, y_start + side - 0.1)]:
                traces.append(_box_mesh(px, py, 0.0, 0.1, 0.1, post_h,
                                         "#4e342e", opacity=0.9, showlegend=False))

            # معلف ودلو ماء داخل الإسطبل
            fx = x_start + side * 0.5
            fy = y_start + (0.35 if row_idx == 0 else side - 0.35)
            traces.append(go.Scatter3d(
                x=[fx], y=[fy], z=[0.75],
                mode="markers",
                marker=dict(size=6, color="#ff8f00", symbol="square"),
                name="معلف" if placed == 0 else None,
                showlegend=(placed == 0),
            ))
            traces.append(go.Scatter3d(
                x=[fx + 0.5], y=[fy], z=[0.65],
                mode="markers",
                marker=dict(size=5, color="#0288d1", symbol="circle"),
                name="دلو ماء" if placed == 0 else None,
                showlegend=(placed == 0),
            ))

            # مجسم مبسط للحصان داخل الإسطبل
            if show_horses:
                hx = x_start + side * 0.5
                hy = y_start + side * 0.5
                # جسم الحصان
                traces.append(_box_mesh(hx - 0.45, hy - 0.25, 0.85, 0.90, 0.50, 0.55,
                                         "#6d4c41", "حصان" if placed == 0 else "",
                                         opacity=0.95, showlegend=(placed == 0)))
                # رأس ورقبة الحصان
                head_y = hy + 0.35 if row_idx == 0 else hy - 0.55
                traces.append(_box_mesh(hx - 0.14, head_y, 1.15, 0.28, 0.22, 0.55,
                                         "#5d4037", opacity=0.95, showlegend=False))

            placed += 1

    fig = go.Figure(data=traces)
    fig.update_layout(
        title=f"🐴 مخطط المربط ثلاثي الأبعاد ({n_horses} خيول — إسطبل {stall_size_m2:.1f} م²)",
        scene=dict(
            xaxis=dict(title="الطول (م)", range=[-1.0, barn_len + 1.0]),
            yaxis=dict(title="العرض (م)", range=[-1.0, barn_wid + 1.0]),
            zaxis=dict(title="الارتفاع (م)", range=[0.0, ceil_h + 0.8]),
            aspectmode="data",
        ),
        height=560,
        margin=dict(l=10, r=10, t=45, b=10),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════
# 📄 توليد تقارير PDF العربية (ReportLab) — مصحّح
# ═══════════════════════════════════════════════════════════════════════

def _shape_ar(text: str) -> str:
    s = str(text or "")
    if not s:
        return ""
    if ARABIC_AVAILABLE:
        try:
            reshaped = arabic_reshaper.reshape(s)
            return get_display(reshaped)
        except Exception:
            return s
    return s


def _find_arabic_font_path() -> Optional[str]:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def generate_ration_pdf(title: str, metadata: Dict[str, str],
                        formula: Dict[str, float], nutrition: Dict[str, float],
                        notes: str = "") -> Optional[bytes]:
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        width, height = A4

        font_name = "Helvetica"
        font_path = _find_arabic_font_path()
        if font_path:
            try:
                pdfmetrics.registerFont(TTFont("TaworFont", font_path))
                font_name = "TaworFont"
            except Exception:
                font_name = "Helvetica"

        c.setTitle(str(title))
        c.setFont(font_name, 16)
        c.drawRightString(width - 20 * mm, height - 20 * mm, _shape_ar(title))

        c.setFont(font_name, 10)
        c.drawRightString(width - 20 * mm, height - 27 * mm,
                          _shape_ar(f"تاريخ التقرير: {datetime.now():%Y-%m-%d %H:%M} | Tawor Nology 11.11.0"))

        y = height - 38 * mm
        c.setFont(font_name, 11)
        for k, v in (metadata or {}).items():
            if y < 30 * mm:
                c.showPage()
                y = height - 25 * mm
                c.setFont(font_name, 11)
            c.drawRightString(width - 20 * mm, y, _shape_ar(f"{k}: {v}"))
            y -= 6.5 * mm

        y -= 4 * mm
        c.setFont(font_name, 12)
        c.drawRightString(width - 20 * mm, y, _shape_ar("مكونات العليقة (%):"))
        y -= 7 * mm

        c.setFont(font_name, 10.5)
        for ing, pct in (formula or {}).items():
            if y < 30 * mm:
                c.showPage()
                y = height - 25 * mm
                c.setFont(font_name, 10.5)
            c.drawRightString(width - 25 * mm, y, _shape_ar(f"• {ing}: {float(pct):.2f}%"))
            y -= 6 * mm

        y -= 4 * mm
        c.setFont(font_name, 12)
        c.drawRightString(width - 20 * mm, y, _shape_ar("القيم الغذائية والتكلفة:"))
        y -= 7 * mm

        c.setFont(font_name, 10.5)
        for k, v in (nutrition or {}).items():
            if y < 30 * mm:
                c.showPage()
                y = height - 25 * mm
                c.setFont(font_name, 10.5)
            c.drawRightString(width - 25 * mm, y, _shape_ar(f"• {k}: {v}"))
            y -= 6 * mm

        if notes:
            y -= 4 * mm
            c.setFont(font_name, 10)
            c.drawRightString(width - 20 * mm, y, _shape_ar(f"ملاحظات: {notes}"))

        c.save()
        pdf_bytes = buf.getvalue()
        return pdf_bytes if pdf_bytes else None
    except Exception:
        return None


def create_pdf_request(pdf_bytes: Optional[bytes], filename: str) -> Optional[Dict]:
    if not pdf_bytes or not isinstance(pdf_bytes, (bytes, bytearray)) or len(pdf_bytes) < 100:
        return None
    safe_name = str(filename).strip() or "tawor_report.pdf"
    if not safe_name.lower().endswith(".pdf"):
        safe_name += ".pdf"
    return {
        "filename": safe_name,
        "bytes": bytes(pdf_bytes),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "size_kb": round(len(pdf_bytes) / 1024.0, 1),
    }


def render_pdf_download_with_approval(pdf_bytes: Optional[bytes], filename: str,
                                      label: str = "📥 تحميل تقرير PDF"):
    req = create_pdf_request(pdf_bytes, filename)
    if req is None:
        st.warning("⚠️ تعذر توليد ملف PDF صالح حالياً. تأكد من توفر مكتبة reportlab وصحة البيانات.")
        return
    st.download_button(
        label=f"{label} ({req['size_kb']} KB)",
        data=req["bytes"],
        file_name=req["filename"],
        mime="application/pdf",
        key=f"dl_{req['filename']}_{req['size_kb']}",
    )

# -*- coding: utf-8 -*-
"""
Tawor Nology 11.11.0 — القسم الثالث (مصحّح):
حسابات المربط والتهوية، الرسم ثلاثي الأبعاد للمربط والخيول،
وتوليد تقارير PDF العربية
"""

import io
import os
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
import streamlit as st

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    go = None

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
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
# 🏠 حسابات المربط والتهوية والاحتياجات البيئية للخيول
# ═══════════════════════════════════════════════════════════════════════

def calculate_barn_requirements(horses_count: int, stall_size_m2: float = 12.25,
                               aisle_width_m: float = 3.5, ceiling_height_m: float = 3.6,
                               season: str = "صيف", bedding_type: str = "نشارة خشب") -> Dict:
    n_horses = max(1, int(horses_count))
    stall_area = max(9.0, float(stall_size_m2))
    side_len = float(np.sqrt(stall_area))
    aisle_w = max(2.5, float(aisle_width_m))
    ceil_h = max(2.8, float(ceiling_height_m))

    # توزيع الصفوف والممرات بشكل عملي
    stalls_area_total = n_horses * stall_area
    row_length = max(side_len, n_horses * side_len)
    aisle_area = row_length * aisle_w
    service_area = max(12.0, 0.15 * (stalls_area_total + aisle_area))
    total_area = round(stalls_area_total + aisle_area + service_area, 2)
    total_volume_m3 = round(total_area * ceil_h, 1)

    # معدلات التهوية (تجديد الهواء في الساعة ACH) حسب الموسم
    if "شتاء" in season:
        ach = 5
        vent_note = "تهوية شتوية مضبوطة (5 تجديدات/ساعة) لتقليل فقد الحرارة ومنع الرطوبة والأمونيا."
    elif "اعتدال" in season or "ربيع" in season or "خريف" in season:
        ach = 12
        vent_note = "تهوية معتدلة (12 تجديد/ساعة) للحفاظ على جودة الهواء دون تيارات هوائية مباشرة."
    else:
        ach = 25
        vent_note = "تهوية صيفية مكثفة (25 تجديد/ساعة) لتصريف الحرارة والرطوبة وتقليل الإجهاد الحراري."

    airflow_m3_per_hr = round(total_volume_m3 * ach, 0)

    # الماء والفرشة والعلف اليومي التقديري للحصان الواحد
    water_per_horse_l = 55.0 if "صيف" in season else 40.0
    total_water_l = round(n_horses * water_per_horse_l, 0)

    bedding_factor = {
        "نشارة خشب": 6.0,
        "قش شعير نظيف": 7.5,
        "حصائر مطاطية + فرشة خفيفة": 3.0,
        "بيت موس / ألياف": 5.5,
    }.get(bedding_type, 6.0)
    daily_bedding_kg = round(n_horses * bedding_factor, 1)

    return {
        "horses_count": n_horses,
        "stall_area_m2": round(stall_area, 2),
        "stall_side_m": round(side_len, 2),
        "aisle_width_m": round(aisle_w, 2),
        "ceiling_height_m": round(ceil_h, 2),
        "total_area_m2": total_area,
        "total_volume_m3": total_volume_m3,
        "season": season,
        "ach": ach,
        "airflow_m3_per_hr": airflow_m3_per_hr,
        "water_per_horse_l": water_per_horse_l,
        "total_water_l": total_water_l,
        "bedding_type": bedding_type,
        "daily_bedding_kg": daily_bedding_kg,
        "vent_note": vent_note,
        "reference": "NRC (2007) + MWPS-1 Structures Handbook",
    }


# ═══════════════════════════════════════════════════════════════════════
# 🎨 رسم ثلاثي الأبعاد للمربط والخيول (Plotly 3D) — مصحّح
# ═══════════════════════════════════════════════════════════════════════

def _box_mesh(x0: float, y0: float, z0: float, dx: float, dy: float, dz: float,
              color: str, name: str = "", opacity: float = 0.85, showlegend: bool = False):
    x1, y1, z1 = x0 + dx, y0 + dy, z0 + dz
    vx = [x0, x1, x1, x0, x0, x1, x1, x0]
    vy = [y0, y0, y1, y1, y0, y0, y1, y1]
    vz = [z0, z0, z0, z0, z1, z1, z1, z1]
    i = [0, 0, 4, 4, 0, 1, 2, 3, 0, 1, 5, 4]
    j = [1, 2, 5, 6, 1, 5, 6, 2, 3, 2, 6, 7]
    k = [2, 3, 6, 7, 5, 6, 7, 3, 7, 6, 7, 4]
    return go.Mesh3d(
        x=vx, y=vy, z=vz,
        i=i, j=j, k=k,
        color=color,
        opacity=opacity,
        name=name if name else None,
        showlegend=showlegend,
        flatshading=True,
    )


def create_barn_3d_figure(horses_count: int = 4, stall_size_m2: float = 12.25,
                          aisle_width_m: float = 3.5, ceiling_height_m: float = 3.6,
                          show_roof: bool = True, show_horses: bool = True):
    if not PLOTLY_AVAILABLE or go is None:
        return None

    n_horses = max(1, min(16, int(horses_count)))
    side = float(np.sqrt(max(9.0, float(stall_size_m2))))
    aisle = max(2.5, float(aisle_width_m))
    ceil_h = max(2.8, float(ceiling_height_m))

    # صفان متقابلان حول ممر مركزي لتقليل الطول وضبط التناسب
    per_row = int(np.ceil(n_horses / 2.0))
    barn_len = max(side * 2.0, per_row * side + 1.0)
    barn_wid = side * 2.0 + aisle + 1.0

    traces = []

    # أرضية المربط
    traces.append(_box_mesh(-0.5, -0.5, -0.05, barn_len + 1.0, barn_wid + 1.0, 0.05,
                             "#d7ccc8", "الأرضية", opacity=0.95, showlegend=True))

    # الممر المركزي
    aisle_y0 = side + 0.25
    traces.append(_box_mesh(0.0, aisle_y0, 0.0, barn_len, aisle, 0.02,
                             "#90a4ae", "الممر المركزي", opacity=0.80, showlegend=True))

    # السقف (اختياري)
    if show_roof:
        traces.append(_box_mesh(-0.5, -0.5, ceil_h, barn_len + 1.0, barn_wid + 1.0, 0.15,
                                 "#5d4037", "السقف", opacity=0.35, showlegend=True))

    placed = 0
    for row_idx in range(2):
        if placed >= n_horses:
            break
        y_start = 0.25 if row_idx == 0 else (side + aisle + 0.25)
        for col_idx in range(per_row):
            if placed >= n_horses:
                break
            x_start = col_idx * side + 0.25
            wall_h = min(1.55, ceil_h * 0.45)
            post_h = min(2.40, ceil_h * 0.70)

            # أرضية الإسطبل / الفرشة
            traces.append(_box_mesh(x_start + 0.05, y_start + 0.05, 0.0,
                                     side - 0.1, side - 0.1, 0.04,
                                     "#ffe082", "فرشة الإسطبل" if placed == 0 else "",
                                     opacity=0.85, showlegend=(placed == 0)))

            # الجدران الجانبية للإسطبل
            traces.append(_box_mesh(x_start, y_start, 0.0, 0.08, side, wall_h,
                                     "#8d6e63", "جدران الإسطبل" if placed == 0 else "",
                                     opacity=0.85, showlegend=(placed == 0)))
            traces.append(_box_mesh(x_start + side - 0.08, y_start, 0.0, 0.08, side, wall_h,
                                     "#8d6e63", opacity=0.85, showlegend=False))

            # أعمدة الزوايا
            for px, py in [(x_start, y_start), (x_start + side - 0.1, y_start),
                           (x_start, y_start + side - 0.1), (x_start + side - 0.1, y_start + side - 0.1)]:
                traces.append(_box_mesh(px, py, 0.0, 0.1, 0.1, post_h,
                                         "#4e342e", opacity=0.9, showlegend=False))

            # معلف ودلو ماء داخل الإسطبل
            fx = x_start + side * 0.5
            fy = y_start + (0.35 if row_idx == 0 else side - 0.35)
            traces.append(go.Scatter3d(
                x=[fx], y=[fy], z=[0.75],
                mode="markers",
                marker=dict(size=6, color="#ff8f00", symbol="square"),
                name="معلف" if placed == 0 else None,
                showlegend=(placed == 0),
            ))
            traces.append(go.Scatter3d(
                x=[fx + 0.5], y=[fy], z=[0.65],
                mode="markers",
                marker=dict(size=5, color="#0288d1", symbol="circle"),
                name="دلو ماء" if placed == 0 else None,
                showlegend=(placed == 0),
            ))

            # مجسم مبسط للحصان داخل الإسطبل
            if show_horses:
                hx = x_start + side * 0.5
                hy = y_start + side * 0.5
                # جسم الحصان
                traces.append(_box_mesh(hx - 0.45, hy - 0.25, 0.85, 0.90, 0.50, 0.55,
                                         "#6d4c41", "حصان" if placed == 0 else "",
                                         opacity=0.95, showlegend=(placed == 0)))
                # رأس ورقبة الحصان
                head_y = hy + 0.35 if row_idx == 0 else hy - 0.55
                traces.append(_box_mesh(hx - 0.14, head_y, 1.15, 0.28, 0.22, 0.55,
                                         "#5d4037", opacity=0.95, showlegend=False))

            placed += 1

    fig = go.Figure(data=traces)
    fig.update_layout(
        title=f"🐴 مخطط المربط ثلاثي الأبعاد ({n_horses} خيول — إسطبل {stall_size_m2:.1f} م²)",
        scene=dict(
            xaxis=dict(title="الطول (م)", range=[-1.0, barn_len + 1.0]),
            yaxis=dict(title="العرض (م)", range=[-1.0, barn_wid + 1.0]),
            zaxis=dict(title="الارتفاع (م)", range=[0.0, ceil_h + 0.8]),
            aspectmode="data",
        ),
        height=560,
        margin=dict(l=10, r=10, t=45, b=10),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════
# 📄 توليد تقارير PDF العربية (ReportLab) — مصحّح
# ═══════════════════════════════════════════════════════════════════════

def _shape_ar(text: str) -> str:
    s = str(text or "")
    if not s:
        return ""
    if ARABIC_AVAILABLE:
        try:
            reshaped = arabic_reshaper.reshape(s)
            return get_display(reshaped)
        except Exception:
            return s
    return s


def _find_arabic_font_path() -> Optional[str]:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def generate_ration_pdf(title: str, metadata: Dict[str, str],
                        formula: Dict[str, float], nutrition: Dict[str, float],
                        notes: str = "") -> Optional[bytes]:
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        width, height = A4

        font_name = "Helvetica"
        font_path = _find_arabic_font_path()
        if font_path:
            try:
                pdfmetrics.registerFont(TTFont("TaworFont", font_path))
                font_name = "TaworFont"
            except Exception:
                font_name = "Helvetica"

        c.setTitle(str(title))
        c.setFont(font_name, 16)
        c.drawRightString(width - 20 * mm, height - 20 * mm, _shape_ar(title))

        c.setFont(font_name, 10)
        c.drawRightString(width - 20 * mm, height - 27 * mm,
                          _shape_ar(f"تاريخ التقرير: {datetime.now():%Y-%m-%d %H:%M} | Tawor Nology 11.11.0"))

        y = height - 38 * mm
        c.setFont(font_name, 11)
        for k, v in (metadata or {}).items():
            if y < 30 * mm:
                c.showPage()
                y = height - 25 * mm
                c.setFont(font_name, 11)
            c.drawRightString(width - 20 * mm, y, _shape_ar(f"{k}: {v}"))
            y -= 6.5 * mm

        y -= 4 * mm
        c.setFont(font_name, 12)
        c.drawRightString(width - 20 * mm, y, _shape_ar("مكونات العليقة (%):"))
        y -= 7 * mm

        c.setFont(font_name, 10.5)
        for ing, pct in (formula or {}).items():
            if y < 30 * mm:
                c.showPage()
                y = height - 25 * mm
                c.setFont(font_name, 10.5)
            c.drawRightString(width - 25 * mm, y, _shape_ar(f"• {ing}: {float(pct):.2f}%"))
            y -= 6 * mm

        y -= 4 * mm
        c.setFont(font_name, 12)
        c.drawRightString(width - 20 * mm, y, _shape_ar("القيم الغذائية والتكلفة:"))
        y -= 7 * mm

        c.setFont(font_name, 10.5)
        for k, v in (nutrition or {}).items():
            if y < 30 * mm:
                c.showPage()
                y = height - 25 * mm
                c.setFont(font_name, 10.5)
            c.drawRightString(width - 25 * mm, y, _shape_ar(f"• {k}: {v}"))
            y -= 6 * mm

        if notes:
            y -= 4 * mm
            c.setFont(font_name, 10)
            c.drawRightString(width - 20 * mm, y, _shape_ar(f"ملاحظات: {notes}"))

        c.save()
        pdf_bytes = buf.getvalue()
        return pdf_bytes if pdf_bytes else None
    except Exception:
        return None


def create_pdf_request(pdf_bytes: Optional[bytes], filename: str) -> Optional[Dict]:
    if not pdf_bytes or not isinstance(pdf_bytes, (bytes, bytearray)) or len(pdf_bytes) < 100:
        return None
    safe_name = str(filename).strip() or "tawor_report.pdf"
    if not safe_name.lower().endswith(".pdf"):
        safe_name += ".pdf"
    return {
        "filename": safe_name,
        "bytes": bytes(pdf_bytes),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "size_kb": round(len(pdf_bytes) / 1024.0, 1),
    }


def render_pdf_download_with_approval(pdf_bytes: Optional[bytes], filename: str,
                                      label: str = "📥 تحميل تقرير PDF"):
    req = create_pdf_request(pdf_bytes, filename)
    if req is None:
        st.warning("⚠️ تعذر توليد ملف PDF صالح حالياً. تأكد من توفر مكتبة reportlab وصحة البيانات.")
        return
    st.download_button(
        label=f"{label} ({req['size_kb']} KB)",
        data=req["bytes"],
        file_name=req["filename"],
        mime="application/pdf",
        key=f"dl_{req['filename']}_{req['size_kb']}",
    )

# -*- coding: utf-8 -*-
"""
Tawor Nology 11.11.0 — القسم الرابع والأخير (مصحّح):
واجهة Streamlit الرئيسية، التبويبات، الدردشة، وإدارة الجلسة
"""

import io
import os
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    go = None


# ═══════════════════════════════════════════════════════════════════════
# 🎬 الفيديو التعريفي وواجهة الدخول وإدارة الجلسة (مصحّح)
# ═══════════════════════════════════════════════════════════════════════

def _init_session_defaults():
    defaults = {
        "video_watched": False,
        "approved": False,
        "user_role": "guest",
        "custom_prices": {},
        "custom_feeds": {},
        "chat_messages": [],
        "last_formula_result": None,
        "last_barn_result": None,
        "last_milk_schedule": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _logout_cleanly():
    preserve_keys = {"video_watched", "csrf_token", "_rl_login", "_rl_chat"}
    for key in list(st.session_state.keys()):
        if key not in preserve_keys and not key.startswith("_rl_"):
            del st.session_state[key]
    st.session_state["approved"] = False
    st.session_state["user_role"] = "guest"
    st.session_state["custom_prices"] = {}
    st.session_state["custom_feeds"] = {}
    st.session_state["chat_messages"] = []
    audit_log("LOGOUT", _safe_username())


def render_intro_and_auth():
    _init_session_defaults()
    generate_csrf_token()

    if not st.session_state.get("video_watched", False):
        st.markdown("## 🎬 مرحباً بك في منصة **Tawor Nology 11.11.0**")
        st.info("منصة علمية متكاملة لتركيب الأعلاف المثلى (LP & NLP)، بدائل الحليب، حسابات المرابط ثلاثية الأبعاد، وتقارير PDF.")
        video_file = "intro.mp4"
        if os.path.exists(video_file):
            try:
                st.video(video_file)
            except Exception:
                st.caption("تعذر تشغيل ملف الفيديو التمهيدي.")
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("⏭️ تخطي / متابعة إلى المنصة", use_container_width=True):
                st.session_state["video_watched"] = True
                st.rerun()
        st.stop()

    if not _session_valid():
        st.markdown("## 🔐 تسجيل الدخول — **Tawor Nology 11.11.0**")
        mode = st.radio("اختر نوع الدخول:", ["مختص / باحث", "دخول زائر", "دخول المالك"], horizontal=True)

        if mode == "مختص / باحث":
            spec_name = st.text_input("الاسم أو الصفة العلمية:", placeholder="مثال: اختصاصي إنتاج حيواني")
            if st.button("دخول كـ مختص", type="primary"):
                if not check_rate_limit("login", max_calls=20, window=60):
                    st.error("تم تجاوز الحد المسموح لمحاولات الدخول. يرجى الانتظار قليلاً.")
                    st.stop()
                st.session_state["user_role"] = "specialist"
                st.session_state["approved"] = True
                if spec_name and _sanitize_message(spec_name, 50):
                    st.session_state["chat_username"] = _sanitize_message(spec_name, 50)
                audit_log("LOGIN_OK", f"specialist:{st.session_state.get('chat_username', '')}")
                st.rerun()

        elif mode == "دخول زائر":
            if st.button("دخول كـ زائر", type="primary"):
                if not check_rate_limit("login", max_calls=20, window=60):
                    st.error("تم تجاوز الحد المسموح لمحاولات الدخول. يرجى الانتظار قليلاً.")
                    st.stop()
                st.session_state["user_role"] = "guest"
                st.session_state["approved"] = True
                audit_log("LOGIN_OK", "guest")
                st.rerun()

        else:
            code_val = st.text_input("أدخل رمز المالك:", type="password")
            if st.button("تحقق ودخول المالك", type="primary"):
                if not check_rate_limit("login", max_calls=10, window=60):
                    st.error("تم تجاوز الحد المسموح لمحاولات الدخول. يرجى الانتظار قليلاً.")
                    st.stop()
                if check_owner_code(code_val):
                    st.session_state["user_role"] = "owner"
                    st.session_state["approved"] = True
                    st.session_state["chat_username"] = "المالك"
                    st.rerun()
                else:
                    st.error("رمز الدخول غير صحيح.")
        st.stop()


# ═══════════════════════════════════════════════════════════════════════
# 📊 التبويبات الرئيسية للتطبيق
# ═══════════════════════════════════════════════════════════════════════

def _get_merged_library() -> Dict:
    merged = {k: list(v) for k, v in BIG_FEEDS_LIBRARY.items()}
    custom_feeds = st.session_state.get("custom_feeds", {})
    if isinstance(custom_feeds, dict):
        for k, v in custom_feeds.items():
            if isinstance(v, (list, tuple)) and len(v) >= 6:
                row = list(v[:7])
                if len(row) == 6:
                    row.append("مخصص")
                merged[k] = row
    return merged


def render_ration_tab():
    st.subheader("🌾 تركيب العلائق المثلى (LP & NLP)")
    lib = _get_merged_library()
    custom_prices = st.session_state.get("custom_prices", {})

    c1, c2, c3 = st.columns(3)
    with c1:
        animal_type = st.selectbox(
            "نوع الحيوان:",
            ["أبقار", "أغنام", "ماعز", "إبل", "خيول", "دواجن", "سمان", "أسماك", "أرانب"],
            key="rat_animal",
        )
    with c2:
        prod_options = {
            "أبقار": ["حليب_عالي", "حليب_متوسط", "حليب_منخفض", "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"],
            "أغنام": ["تسمين_مكثف", "تسمين_عادي", "مرضعات", "حامل_أخير", "حامل_متوسط", "حملان_تيد", "صيانة"],
            "ماعز": ["حلابة_عالي", "حلابة_متوسط", "تسمين_جديان", "تيوس", "حامل_أخير", "صيانة"],
            "إبل": ["حليب", "تسمين", "نمو", "سباق", "صيانة"],
            "خيول": ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار", "مرضعات", "صيانة"],
            "دواجن": ["لاحم", "بياض"],
            "سمان": ["تسمين", "بياض"],
            "أسماك": ["بادئ", "نمو", "تسمين"],
            "أرانب": ["تسمين", "حليب", "صيانة"],
        }.get(animal_type, ["صيانة"])
        production_type = st.selectbox("المرحلة / الغرض الإنتاجي:", prod_options, key="rat_prod")
    with c3:
        solver_mode = st.selectbox("منهجية التحسين:", ["ذكي (LP + NLP)", "برمجة خطية (LP)", "برمجة غير خطية (NLP)"], key="rat_solver")

    # عرض الاحتياجات المرجعية والمعادلات
    refs = get_references(animal_type, production_type)
    eqs = get_reference_equations(animal_type, production_type)
    with st.expander("📚 المرجع العلمي والمعادلات القياسية", expanded=False):
        st.write(f"**المرجع الأساسي:** {refs.get('primary', '—')} | **الجدول:** {refs.get('table', '—')}")
        if eqs:
            st.json(eqs)

    # شريط القياس للحيوانات الكبيرة والصغيرة
    if animal_type in WEIGHT_TAPE_CONFIG:
        est_w = weight_tape_widget(animal_type, key_prefix="rat_tape")
        st.caption(f"الوزن المستخدم للتقدير المرجعي: {est_w:.1f} كجم")

    default_ings = [
        "ذرة صفراء", "شعير مجروش", "نخالة قمح",
        "كسب فول الصويا (44%)", "كسب عباد الشمس",
        "دريس برسيم حجازي", "حجر جيري / كربونات كالسيوم",
        "فوسفات ثنائي الكالسيوم (DCP)", "ملح طعام (كلوريد الصوديوم)",
        "مخلوط فيتامينات ومعادن (بريمكس)",
    ]
    available_choices = [x for x in default_ings if x in lib] + [x for x in lib.keys() if x not in default_ings]
    selected_ings = st.multiselect(
        "اختر المواد العلفية المتاحة:",
        options=list(lib.keys()),
        default=[x for x in default_ings if x in lib][:7],
        key="rat_ings",
    )

    if st.button("⚙️ حساب العليقة المثلى", type="primary", key="btn_calc_ration"):
        if not selected_ings:
            st.warning("يرجى اختيار مادة علفية واحدة على الأقل.")
            return

        req_info = _get_requirement_for_nlp(animal_type, production_type)
        t_cp = float(req_info.get("CP", 16.0))
        t_me = float(req_info.get("ME", 2800.0))
        t_dp = float(req_info.get("DP", 12.0))
        t_se = t_me / 41.0

        if solver_mode == "برمجة خطية (LP)":
            res = optimize_ration_lp(selected_ings, t_cp, t_se, t_dp, custom_prices, lib)
        elif solver_mode == "برمجة غير خطية (NLP)":
            res = optimize_ration_nlp(selected_ings, t_cp, t_me, custom_prices, lib)
        else:
            res = auto_formulate_smart(animal_type, production_type, selected_ings, custom_prices, lib)

        if not res:
            st.error("تعذر إيجاد تركيبة مناسبة بالمدخلات الحالية.")
            return

        st.session_state["last_formula_result"] = {
            "animal_type": animal_type,
            "production_type": production_type,
            "result": res,
        }

    last_pack = st.session_state.get("last_formula_result")
    if last_pack and isinstance(last_pack, dict):
        res = last_pack["result"]
        st.success(f"✅ تم توليد العليقة باستخدام **{res.get('solver', 'Solver')}** — التكلفة التقديرية: **${res.get('cost_per_ton', 0):.2f} / طن**")

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("البروتين الخام CP%", f"{res.get('CP', 0):.2f}%")
        m2.metric("البروتين المهضوم DP%", f"{res.get('DP', 0):.2f}%")
        m3.metric("الطاقة ME (كيلو كالوري)", f"{res.get('ME', 0):.1f}")
        m4.metric("الكالسيوم Ca%", f"{res.get('Ca', 0):.2f}%")
        m5.metric("الفوسفور P%", f"{res.get('P', 0):.2f}%")

        formula_dict = res.get("formula", {})
        if formula_dict:
            df_f = pd.DataFrame([
                {
                    "المادة العلفية": ing,
                    "النسبة (%)": pct,
                    "كجم / طن": round(pct * 10.0, 2),
                    "سعر الطن ($)": custom_prices.get(ing, lib.get(ing, [0, 0, 0, 0, 0, 0])[5]),
                }
                for ing, pct in formula_dict.items()
            ])
            st.dataframe(df_f, use_container_width=True, hide_index=True)

            if PLOTLY_AVAILABLE and go is not None:
                fig_bar = go.Figure(data=[
                    go.Bar(x=df_f["المادة العلفية"], y=df_f["النسبة (%)"], marker_color="#2e7d32")
                ])
                fig_bar.update_layout(title="توزيع نسب مكونات العليقة (%)", height=320)
                st.plotly_chart(fig_bar, use_container_width=True)

            pdf_bytes = generate_ration_pdf(
                title=f"تقرير عليقة — {last_pack['animal_type']} ({last_pack['production_type']})",
                metadata={
                    "النوع": last_pack["animal_type"],
                    "المرحلة": last_pack["production_type"],
                    "المحرك": str(res.get("solver", "")),
                    "التكلفة للطن": f"${res.get('cost_per_ton', 0):.2f}",
                },
                formula=formula_dict,
                nutrition={
                    "البروتين الخام CP%": f"{res.get('CP', 0):.2f}%",
                    "البروتين المهضوم DP%": f"{res.get('DP', 0):.2f}%",
                    "الطاقة ME": f"{res.get('ME', 0):.1f} kcal/kg",
                    "الكالسيوم Ca%": f"{res.get('Ca', 0):.2f}%",
                    "الفوسفور P%": f"{res.get('P', 0):.2f}%",
                },
                notes=refs.get("primary", ""),
            )
            render_pdf_download_with_approval(pdf_bytes, "tawor_ration_report.pdf")


def render_milk_replacer_tab():
    st.subheader("🍼 بدائل الحليب وجدولة الرضاعة")
    species_labels = {
        "عجول_أبقار": "عجول الأبقار",
        "حملان_أغنام": "حملان الأغنام",
        "جديان_ماعز": "جديان الماعز",
        "حيران_إبل": "حيران الإبل",
        "أمهار_خيول": "أمهار الخيول",
    }
    sp_key = st.selectbox(
        "اختر الفصيلة:",
        options=list(species_labels.keys()),
        format_func=lambda k: species_labels[k],
        key="mr_species",
    )
    cfg = MILK_REPLACERS[sp_key]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        birth_w = st.number_input("وزن الميلاد (كجم):", 2.0, 80.0, 35.0 if "عجول" in sp_key else 4.0, 0.5, key="mr_bw")
    with c2:
        days = st.number_input("مدة البرنامج (يوم):", 7, 120, 45, 1, key="mr_days")
    with c3:
        price_kg = st.number_input("سعر كجم البديل ($):", 0.5, 20.0, 2.5, 0.1, key="mr_price")
    with c4:
        st.metric("نسبة التخفيف", f"{cfg['dilution_g_per_L']:.0f} جم/لتر")

    st.info(f"**{cfg['title']}** — بروتين: {cfg['CP']}% | دهن: {cfg['fat']}% | لاكتوز: {cfg['lactose']}%\n\n{cfg['notes']}")

    df_ing = pd.DataFrame([
        {"المكون": ing, "النسبة (%)": pct}
        for ing, pct in cfg["ingredients"].items()
    ])
    st.dataframe(df_ing, use_container_width=True, hide_index=True)

    if st.button("📅 توليد جدول الرضاعة اليومي", type="primary", key="btn_mr_sched"):
        sched = calc_milk_replacer_schedule(sp_key, birth_w, int(days), float(price_kg))
        st.session_state["last_milk_schedule"] = sched

    sched = st.session_state.get("last_milk_schedule")
    if sched:
        df_s = pd.DataFrame(sched)
        total_cost = round(float(df_s["daily_cost"].sum()), 2)
        total_powder = round(float(df_s["powder_g"].sum()) / 1000.0, 2)
        m1, m2 = st.columns(2)
        m1.metric("إجمالي البودرة خلال الفترة (كجم)", f"{total_powder:.2f} كجم")
        m2.metric("إجمالي التكلفة التقديرية ($)", f"${total_cost:.2f}")
        st.dataframe(df_s.head(30), use_container_width=True, hide_index=True)


def render_barn_3d_tab():
    st.subheader("🏠 حسابات المربط والتهوية والرسم ثلاثي الأبعاد (3D)")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        horses_n = st.number_input("عدد الخيول:", 1, 16, 4, 1, key="barn_n")
    with c2:
        stall_sz = st.number_input("مساحة الإسطبل (م²):", 9.0, 25.0, 12.25, 0.25, key="barn_stall")
    with c3:
        aisle_w = st.number_input("عرض الممر (م):", 2.5, 6.0, 3.5, 0.25, key="barn_aisle")
    with c4:
        ceil_h = st.number_input("ارتفاع السقف (م):", 2.8, 6.0, 3.6, 0.1, key="barn_ceil")

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        season = st.selectbox("الموسم:", ["صيف", "اعتدال", "شتاء"], key="barn_season")
    with c6:
        bedding = st.selectbox("نوع الفرشة:", ["نشارة خشب", "قش شعير نظيف", "حصائر مطاطية + فرشة خفيفة", "بيت موس / ألياف"], key="barn_bed")
    with c7:
        show_roof = st.checkbox("إظهار السقف", value=True, key="barn_roof")
    with c8:
        show_horses = st.checkbox("إظهار الخيول", value=True, key="barn_horses")

    barn_info = calculate_barn_requirements(int(horses_n), float(stall_sz), float(aisle_w), float(ceil_h), season, bedding)
    st.session_state["last_barn_result"] = barn_info

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("المساحة الكلية (م²)", f"{barn_info['total_area_m2']:.2f} م²")
    k2.metric("الحجم الكلي (م³)", f"{barn_info['total_volume_m3']:.1f} م³")
    k3.metric("معدل التهوية", f"{barn_info['ach']} تجديد/ساعة")
    k4.metric("الماء اليومي الكلي", f"{barn_info['total_water_l']:.0f} لتر/يوم")

    st.caption(f"🌬️ {barn_info['vent_note']} | الفرشة اليومية: {barn_info['daily_bedding_kg']} كجم/يوم | المرجع: {barn_info['reference']}")

    fig_3d = create_barn_3d_figure(
        horses_count=int(horses_n),
        stall_size_m2=float(stall_sz),
        aisle_width_m=float(aisle_w),
        ceiling_height_m=float(ceil_h),
        show_roof=show_roof,
        show_horses=show_horses,
    )
    if fig_3d is not None:
        st.plotly_chart(fig_3d, use_container_width=True)
    else:
        st.info("مكتبة Plotly غير متوفرة حالياً لعرض الرسم ثلاثي الأبعاد.")


def render_feeds_prices_tab():
    st.subheader("💰 مكتبة الأعلاف والأسعار المخصصة")
    lib = _get_merged_library()
    custom_prices = st.session_state.get("custom_prices", {})

    rows = []
    for name, vals in lib.items():
        rows.append({
            "المادة العلفية": name,
            "DP%": vals[0],
            "CP%": vals[1],
            "SE": vals[2],
            "Ca%": vals[3],
            "P%": vals[4],
            "النوع": vals[6] if len(vals) > 6 else "أخرى",
            "السعر الأساسي ($/طن)": vals[5],
            "السعر الحالي ($/طن)": custom_prices.get(name, vals[5]),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("### تعديل سعر مادة علفية")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        target_feed = st.selectbox("اختر المادة:", list(lib.keys()), key="pr_feed")
    with c2:
        current_p = float(custom_prices.get(target_feed, lib[target_feed][5]))
        new_p = st.number_input("السعر الجديد ($/طن):", 0.0, 10000.0, current_p, 5.0, key="pr_val")
    with c3:
        st.write("")
        st.write("")
        if st.button("💾 حفظ السعر", key="btn_save_price"):
            st.session_state["custom_prices"][target_feed] = float(new_p)
            st.success(f"تم تحديث سعر {target_feed} إلى ${new_p:.2f}/طن")
            st.rerun()


def render_chat_tab():
    st.subheader("💬 سجل الملاحظات والمناقشات العلمية")
    msgs = st.session_state.get("chat_messages", [])
    for m in msgs[-40:]:
        with st.chat_message("user" if m.get("sender") == _safe_username() else "assistant"):
            st.markdown(f"**{m.get('sender', 'مستخدم')}** · *{m.get('time', '')}*\n\n{m.get('text', '')}")

    prompt = st.chat_input("اكتب ملاحظة أو استفساراً علمياً...")
    if prompt:
        if not check_rate_limit("chat", max_calls=25, window=60):
            st.warning("يرجى التمهل قليلاً قبل إرسال رسالة أخرى.")
            return
        clean_txt = _sanitize_message(prompt, 500)
        if clean_txt:
            st.session_state["chat_messages"].append({
                "sender": _safe_username(),
                "time": datetime.now().strftime("%H:%M"),
                "text": clean_txt,
            })
            audit_log("CHAT_MSG", f"{_safe_username()}: {clean_txt[:80]}")
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════
# 🚀 نقطة الدخول الرئيسية للتطبيق
# ═══════════════════════════════════════════════════════════════════════

def main():
    st.set_page_config(
        page_title="Tawor Nology 11.11.0",
        page_icon="🌾",
        layout="wide",
    )
    render_intro_and_auth()

    top_l, top_r = st.columns([5, 1])
    with top_l:
        st.markdown(f"# 🌾 Tawor Nology `11.11.0` — أهلاً بك يا **عبدالقادر إسماعيل**")
        st.caption(f"المستخدم الحالي: {_safe_username()} | الدور: {st.session_state.get('user_role', 'guest')}")
    with top_r:
        st.write("")
        if st.button("🚪 خروج", key="btn_logout", use_container_width=True):
            _logout_cleanly()
            st.rerun()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧮 تركيب العلائق (LP/NLP)",
        "🍼 بدائل الحليب",
        "🏠 المربط والتهوية (3D)",
        "💰 الأعلاف والأسعار",
        "💬 الملاحظات والدردشة",
    ])

    with tab1:
        render_ration_tab()
    with tab2:
        render_milk_replacer_tab()
    with tab3:
        render_barn_3d_tab()
    with tab4:
        render_feeds_prices_tab()
    with tab5:
        render_chat_tab()


if __name__ == "__main__":
    main()
