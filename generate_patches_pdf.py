#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مولّد PDF كامل لباتشات Tawor Nology 11.6.2
════════════════════════════════════════════════════════════════
الاستخدام:
    python generate_patches_pdf.py
    # يولّد: Tawor_Patches_v11.6.2.pdf
════════════════════════════════════════════════════════════════
"""

import os
import io
from datetime import datetime

from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    AR_OK = True
except ImportError:
    AR_OK = False


# ═════════════════════════════════════════════════════════════════════
# 1) الخطوط
# ═════════════════════════════════════════════════════════════════════

FONT = "Helvetica"
FONT_B = "Helvetica-Bold"
FONT_M = "Courier"

def _load_fonts():
    global FONT, FONT_B
    candidates = [
        ("Amiri-Regular.ttf", "Amiri-Bold.ttf"),
        ("/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf",
         "/usr/share/fonts/truetype/amiri/Amiri-Bold.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]
    for reg, bold in candidates:
        if os.path.exists(reg):
            try:
                pdfmetrics.registerFont(TTFont("AR", reg))
                if os.path.exists(bold):
                    pdfmetrics.registerFont(TTFont("AR-Bold", bold))
                    FONT_B = "AR-Bold"
                else:
                    FONT_B = "AR"
                FONT = "AR"
                return
            except Exception:
                pass

_load_fonts()


def ar(text: str) -> str:
    if not AR_OK:
        return str(text)
    try:
        return get_display(arabic_reshaper.reshape(str(text)), base_dir='R')
    except Exception:
        return str(text)


# ═════════════════════════════════════════════════════════════════════
# 2) بيانات الباتشات
# ═════════════════════════════════════════════════════════════════════

PATCHES = [
    {
        "id": "P00", "title": "استيرادات إضافية",
        "type": "إضافة", "location": "أعلى الملف — بعد آخر استيراد",
        "find": "from typing import Optional, Dict, List, Tuple, Any, Union, Set\n\nwarnings.filterwarnings('ignore')",
        "replace": "from typing import Optional, Dict, List, Tuple, Any, Union, Set\n\n# v11.6.2 — للتوليد الصوتي\nimport wave\nimport struct\nimport math\n\nwarnings.filterwarnings('ignore')",
        "verify": "الملف يُستورد بلا أخطاء",
    },
    {
        "id": "P01", "title": "دوال التنبيه الصوتي",
        "type": "إضافة", "location": "قبل def auto_formulate_smart",
        "find": "# ═══════ محرك LP ═══════\n\ndef auto_formulate_smart(",
        "replace": "# ═══════ v11.6.2 — التنبيه الصوتي ═══════\n\ndef generate_alert_wav(pattern='critical') -> bytes:\n    sr = 22050\n    if pattern == 'critical':\n        seq = [(880, .18), (0, .06), (660, .22), (0, .05), (440, .28)]\n        vol = 28000\n    elif pattern == 'warning':\n        seq = [(520, .30), (0, .10), (420, .30)]\n        vol = 22000\n    else:\n        seq = [(660, .10), (0, .04), (880, .12), (0, .04), (1100, .15)]\n        vol = 18000\n    buf = io.BytesIO()\n    with wave.open(buf, 'wb') as w:\n        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)\n        for freq, dur in seq:\n            n = int(dur * sr)\n            for i in range(n):\n                if freq == 0:\n                    val = 0\n                else:\n                    t = i / sr\n                    env = min(t*25, (dur-t)*25, 1.0)\n                    val = int(vol*env*math.sin(2*math.pi*freq*t))\n                w.writeframes(struct.pack('<h', max(-32767, min(32767, val))))\n    buf.seek(0); return buf.getvalue()\n\ndef play_alert(pattern='critical'):\n    try:\n        st.audio(generate_alert_wav(pattern), format='audio/wav', autoplay=True)\n    except Exception:\n        pass\n\n# ═══════ محرك LP ═══════\n\ndef auto_formulate_smart(",
        "verify": "play_alert('success') يعمل بلا استثناء",
    },
    {
        "id": "P02", "title": "قاعدة بيانات المخاطر المركزية",
        "type": "إضافة", "location": "قبل قسم التنبيه الصوتي",
        "find": "# ═══════ v11.6.2 — التنبيه الصوتي ═══════",
        "replace": "# ═══════ HAZARD_DATABASE ═══════\nHAZARD_DATABASE = {\n    'كسافا مجففة': {'hazard': 'HCN', 'limits_by_class': {...}, 'source': 'FAO 2010', 'action': 'تُمنع للدواجن'},\n    'كسب بذور القطن': {'hazard': 'جوسيبول', 'limits_by_class': {...}, 'source': 'NRC 2001', 'action': 'منزوع الجوسيبول'},\n    'يوريا علفية': {'hazard': 'NPN', 'limits_by_class': {...}, 'source': 'FAO 2019', 'action': 'للمجترات فقط'},\n    'فول صويا كامل': {'hazard': 'مثبطات تريبسين', ...},\n    'فوسفات ثنائي الكالسيوم': {'hazard': 'فلورايد', ...},\n    'سيلينيت الصوديوم': {'hazard': 'سيلينيوم', ...},\n    'أمباز الفول السوداني': {'hazard': 'أفلاتوكسين', 'aflatoxin_risk': True, ...},\n    'ذرة صفراء': {'hazard': 'أفلاتوكسين محتمل', 'aflatoxin_risk': True, ...},\n    # + كسب فول صويا، شحم حيواني، أوراق موز، أوراق مانجو\n}\n\n# ═══════ v11.6.2 — التنبيه الصوتي ═══════",
        "verify": "len(HAZARD_DATABASE) >= 10",
    },
    {
        "id": "P03", "title": "دوال مساعدة للأمان",
        "type": "إضافة", "location": "بعد HAZARD_DATABASE مباشرة",
        "find": "}\n\ndef _get_hazard_info(ingredient: str):\n    pass",
        "replace": "_get_hazard_info(ingredient) → Dict أو None\n_hazard_limit_for(ingredient, animal_type, production_type) → float أو None\ncompute_total_selenium_ppm(formula) → ppm Se الكلي\n\nمنطق _hazard_limit_for:\n  - دواجن/سمان → poultry\n  - خيول → horses\n  - أسماك → fish\n  - مجترات → ruminant\n  - صغار (بادي/زريعة/جديان) → young (أشد)",
        "verify": "_hazard_limit_for('يوريا علفية', 'دواجن') == 0.0",
    },
    {
        "id": "P04", "title": "كاشف التحذيرات (11 فحصاً)",
        "type": "إضافة", "location": "قبل قسم التنبيه الصوتي",
        "find": "# ═══════ v11.6.2 — التنبيه الصوتي ═══════\n\ndef generate_alert_wav",
        "replace": "def detect_harmful_mix(formula, animal_type, production_type='', requirement=None, targets=None) → List[Dict]:\n    '''\n    11 فحصاً:\n      1. كل مادة في HAZARD_DATABASE (حدودها حسب الحيوان)\n      2. يوريا للمجترات\n      3. السيلينيوم الكلي\n      4. أفلاتوكسين بلا مضاد سموم\n      5. فول صويا كامل\n      6. كسافا (HCN)\n      7. Ca:P\n      8. ملح\n      9. دهن زائد\n     10. بروتين زائد\n     11. ألياف للدواجن\n    كل تحذير: {level, title, detail, source, action}\n    '''\n\n# ═══════ v11.6.2 — التنبيه الصوتي ═══════\n\ndef generate_alert_wav",
        "verify": "detect_harmful_mix({'يوريا علفية': 2.0}, 'دواجن') يعيد 'critical'",
    },
    {
        "id": "P05", "title": "قيود LP الاستباقية (L1)",
        "type": "إضافة", "location": "قبل قسم التنبيه الصوتي",
        "find": "# ═══════ v11.6.2 — التنبيه الصوتي ═══════",
        "replace": "def _add_safety_constraints(valid, bounds, animal_type, production_type):\n    '''\n    يعدّل bounds لمنع/تقييد المواد الخطرة قبل LP.\n    يعيد (bounds_updated, blocked_ingredients).\n    '''\n    blocked = []\n    for i, ing in enumerate(valid):\n        limit = _hazard_limit_for(ing, animal_type, production_type)\n        if limit is not None:\n            lo, hi = bounds[i]\n            if limit < lo:\n                bounds[i] = (0.0, 0.0)\n                blocked.append(ing)\n            else:\n                bounds[i] = (lo, min(hi, limit))\n    return bounds, blocked\n\n# ═══════ v11.6.2 — التنبيه الصوتي ═══════",
        "verify": "_add_safety_constraints(['يوريا علفية'], [(0,100)], 'دواجن', '') يقفل اليوريا",
    },
    {
        "id": "P06", "title": "محرك التركيب الآمن — استبدال كامل",
        "type": "استبدال", "location": "def auto_formulate_smart",
        "find": "def auto_formulate_smart(...):\n    '''محرك التركيب القديم'''\n    # ... ~120 سطر ...",
        "replace": "def auto_formulate_smart(...):\n    '''\n    v11.6.2 — أمان 3 طبقات:\n      L1: قيود صلبة على المواد الخطرة قبل الحل\n      L2: فلترة الحلول الخطرة + 3 محاولات تلقائية\n      L3: كاشف تحذيرات نهائي\n    نواتج إضافية: harmful_warnings, blocked_ingredients, safety_attempt\n    '''\n    # (الكود الكامل في PATCH-06)",
        "verify": "result['harmful_warnings'] موجود عند النجاح",
    },
    {
        "id": "P07", "title": "توليد التركيبات المتعددة",
        "type": "إضافة", "location": "بعد auto_formulate_smart",
        "find": "def compute_sensitivity(",
        "replace": "def formulate_multiple_options(available, prices, custom_standard, standard_key='', basis='DP', min_quality=70.0, animal_type='', production_type='', requirement=None, n_options=5) -> Dict:\n    '''\n    يولّد حتى 5 تركيبات من نفس المواد:\n      - استبعاد المواد الخطرة أولاً\n      - ثم استبعاد مصادر الطاقة/البروتين\n      - فصل صارم: آمنة vs خطرة\n      - ترتيب: أمان → جودة → تكلفة\n    يعيد: {'success': True, 'options': [...], 'no_safe_option': bool}\n    '''\n\ndef compute_sensitivity(",
        "verify": "formulate_multiple_options(...)['options'] قائمة 1-5",
    },
    {
        "id": "P08", "title": "مخطط الحظائر 2D",
        "type": "إضافة", "location": "قبل create_barn_3d_figure",
        "find": "def create_barn_3d_figure(dims: Dict):",
        "replace": "def create_pen_layout_2d(dims, animal_emoji='🐄', max_per_pen=8, max_pens=6):\n    '''\n    مخطط 2D: كل حظيرة مستطيل بأيقونات.\n    الفائض يظهر '+N إضافي'.\n    الحيوانات الكبيرة 8/حظيرة، الصغيرة 12/حظيرة.\n    '''\n\ndef create_barn_3d_figure(dims: Dict):",
        "verify": "create_pen_layout_2d({'count': 100}, '🐄') يعيد BytesIO",
    },
    {
        "id": "P09", "title": "مجسم 3D محدّث (40 رمزاً)",
        "type": "استبدال", "location": "def create_barn_3d_figure",
        "find": "def create_barn_3d_figure(dims: Dict):\n    '''شكل 3D للحظيرة'''\n    # ... ~80 سطر ...",
        "replace": "def create_barn_3d_figure(dims, max_visible_animals=40):\n    '''\n    مجسم 3D بحد أعلى 40 رمزاً.\n    عند تجاوز العدد: كل رمز = N رأس.\n    يظهر في العنوان: 'كل رمز ≈ N رأس'.\n    '''\n    # (الكود الكامل في PATCH-09)",
        "verify": "التوقيع يحتوي max_visible_animals=40",
    },
    {
        "id": "P10", "title": "زر التشغيل في النمذجة",
        "type": "استبدال", "location": "if run: في تبويب النمذجة",
        "find": "if run:\n    if len(selected) < 2:\n        st.error('اختر مادتين')\n    else:\n        result = auto_formulate_smart(...)\n        if result['success']:\n            ...",
        "replace": "if run:\n    if len(selected) < 2:\n        st.error('اختر مادتين')\n    else:\n        multi = formulate_multiple_options(...)\n        if multi['success']:\n            result = multi['options'][0]\n            # + تشغيل play_alert حسب الحالة\n            # + حفظ multi_options في session\n            # + عرض 'لا يوجد حل آمن' عند الحاجة",
        "verify": "يظهر 'جاري التركيب الآمن' ثم النتيجة",
    },
    {
        "id": "P11", "title": "لوحة الخيارات والتحذيرات",
        "type": "استبدال", "location": "بعد if run: مباشرة",
        "find": "if st.session_state.get('last_formulation_result'):\n    result = st.session_state['last_formulation_result']",
        "replace": "# 1) تنبيه no_safe_alert\n# 2) لوحة تحذيرات (حرج + وقائي)\n# 3) خيارات متعددة (5 بطاقات + زر اختيار)\n# 4) ثم عرض النتيجة (الكود الأصلي)",
        "verify": "عند اختيار خيار يتغير وتُشغّل نغمة",
    },
    {
        "id": "P12", "title": "قسم 3D في تبويب الحظائر",
        "type": "استبدال", "location": "st.markdown('### 🏗️ المجسم 3D')",
        "find": "st.markdown('### 🏗️ المجسم 3D')\nfig3d = create_barn_3d_figure(dims)\nif fig3d:\n    st.plotly_chart(fig3d, use_container_width=True)",
        "replace": "# 1) مخطط 2D أولاً (create_pen_layout_2d)\n# 2) ثم 3D (max_visible_animals=40)\n# 3) تنبيه إذا العدد > 40: 'كل رمز ≈ N رأس'",
        "verify": "رسم 2D ثم 3D بحد 40 رمزاً",
    },
]

CHECKLIST = [
    "تشغيل الملف بلا أخطاء استيراد",
    "دواجن + كسافا → تحذير حرج + صوت",
    "دواجن + يوريا → حظر تلقائي (لا تظهر)",
    "3 مواد فقط → خيار واحد على الأقل",
    "6 مواد متنوعة → 5 خيارات مرتبة",
    "10,000 دجاجة → 12/حظيرة + '+N'",
    "500 بقرة → 8/حظيرة + 3D بـ 40 رمزاً",
    "تركيبة آمنة → صوت نجاح",
    "تركيبة بها تحذير → صوت تحذير",
    "تركيبة بها خطر → صوت خطر",
    "Ca:P منخفض → تحذير مع مصدر",
    "سيلينيوم > 0.5 ppm → تحذير",
    "أفلاتوكسين > 35% بلا مضاد → تحذير",
]

APP_ORDER = [
    ("1", "P00", "استيرادات", "إلزامي أولاً"),
    ("2", "P01", "صوت", "يعتمد على P00"),
    ("3", "P02", "قاعدة بيانات", "مستقل"),
    ("4", "P03", "دوال مساعدة", "يعتمد على P02"),
    ("5", "P04", "كاشف تحذيرات", "يعتمد على P03"),
    ("6", "P05", "قيود LP", "يعتمد على P03"),
    ("7", "P06", "محرك التركيب", "يعتمد على P04+P05"),
    ("8", "P07", "تركيبات متعددة", "يعتمد على P06"),
    ("9", "P08", "مخطط 2D", "مستقل"),
    ("10", "P09", "مجسم 3D", "يعتمد على P08"),
    ("11", "P10", "زر التشغيل", "يعتمد على P06+P07"),
    ("12", "P11", "لوحة العرض", "يعتمد على P10"),
    ("13", "P12", "قسم 3D في UI", "يعتمد على P08+P09"),
]


# ═════════════════════════════════════════════════════════════════════
# 3) مولّد PDF
# ═════════════════════════════════════════════════════════════════════

def _page_decorator(canvas_obj, doc):
    """ديباجة وتذييل كل صفحة."""
    try:
        canvas_obj.saveState()
        w, h = doc.pagesize

        # رأس
        canvas_obj.setFillColor(HexColor("#1b5e20"))
        canvas_obj.rect(0, h - 70, w, 70, fill=1, stroke=0)
        canvas_obj.setFillColor(HexColor("#d4af37"))
        canvas_obj.rect(0, h - 74, w, 4, fill=1, stroke=0)

        canvas_obj.setFillColor(white)
        canvas_obj.setFont(FONT_B, 16)
        canvas_obj.drawCentredString(w/2, h - 40,
                                       ar("تاور نولجي Tawor Nology 11.6.2"))
        canvas_obj.setFont(FONT, 10)
        canvas_obj.setFillColor(HexColor("#c8e6c9"))
        canvas_obj.drawCentredString(w/2, h - 58,
                                       ar("حزمة الباتشات — دليل التطبيق الكامل"))

        # تذييل
        canvas_obj.setFillColor(HexColor("#1b5e20"))
        canvas_obj.rect(0, 0, w, 30, fill=1, stroke=0)
        canvas_obj.setFillColor(white)
        canvas_obj.setFont(FONT, 8)
        canvas_obj.drawCentredString(w/2, 18,
            ar(f"صفحة {canvas_obj.getPageNumber()} | "
               "د. عبدالقادر إسماعيل تاور © 2026"))
        canvas_obj.drawCentredString(w/2, 6,
            ar("رحم الله والدي إسماعيل تاور وأختي ابتسام"))
        canvas_obj.restoreState()
    except Exception:
        pass


def _styles():
    s = getSampleStyleSheet()
    st = {
        "title": ParagraphStyle("t", fontName=FONT_B, fontSize=28,
                                 alignment=TA_CENTER,
                                 textColor=HexColor("#1b5e20"),
                                 spaceAfter=10, leading=36),
        "subtitle": ParagraphStyle("st", fontName=FONT, fontSize=14,
                                     alignment=TA_CENTER,
                                     textColor=HexColor("#1565c0"),
                                     spaceAfter=8, leading=22),
        "h1": ParagraphStyle("h1", fontName=FONT_B, fontSize=20,
                              alignment=TA_RIGHT,
                              textColor=HexColor("#1b5e20"),
                              spaceBefore=15, spaceAfter=10, leading=28),
        "h2": ParagraphStyle("h2", fontName=FONT_B, fontSize=14,
                              alignment=TA_RIGHT,
                              textColor=HexColor("#0d47a1"),
                              spaceBefore=10, spaceAfter=6, leading=20),
        "body": ParagraphStyle("b", fontName=FONT, fontSize=10,
                                alignment=TA_RIGHT,
                                textColor=HexColor("#1a1a1a"),
                                spaceAfter=4, leading=16),
        "caption": ParagraphStyle("c", fontName=FONT, fontSize=8.5,
                                    alignment=TA_RIGHT,
                                    textColor=HexColor("#6b7280"),
                                    spaceAfter=4, leading=13),
        "code": ParagraphStyle("co", fontName=FONT_M, fontSize=7.5,
                                alignment=TA_LEFT,
                                textColor=HexColor("#0d3011"),
                                spaceAfter=2, leading=11),
        "center": ParagraphStyle("ct", fontName=FONT, fontSize=11,
                                   alignment=TA_CENTER,
                                   textColor=HexColor("#1a1a1a"),
                                   leading=18),
    }
    return st


def _code_block(text: str, max_lines: int = 20):
    """يعيد جدول صندوق كود."""
    lines = str(text).split("\n")[:max_lines]
    if len(text.split("\n")) > max_lines:
        lines.append(f"... (+{len(text.split(chr(10)))-max_lines} سطر)")
    content = "<br/>".join(
        line.replace(" ", "&nbsp;").replace("<", "&lt;").replace(">", "&gt;")
        for line in lines
    )
    st = _styles()
    return Paragraph(content, st["code"])


def build_pdf(output_path: str = "Tawor_Patches_v11.6.2.pdf"):
    st = _styles()
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=40, leftMargin=40,
        topMargin=90, bottomMargin=50,
        title="Tawor Nology 11.6.2 — Patches",
        author="Dr. Abdelgader Ismail Tawor",
    )
    story = []

    # ─── الغلاف ──────────────────────────────────────────────
    story.append(Spacer(1, 80))
    story.append(Paragraph(ar("🌾 تاور نولجي"), st["title"]))
    story.append(Paragraph(ar("Tawor Nology 11.6.2"), st["title"]))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="70%", thickness=3,
                             color=HexColor("#d4af37"), hAlign='CENTER'))
    story.append(Spacer(1, 20))
    story.append(Paragraph(ar("حزمة الباتشات الكاملة — دليل التطبيق"),
                             st["subtitle"]))
    story.append(Paragraph(ar("13 باتشاً مرتباً | اختبارات وحدة | قائمة تحقق"),
                             st["subtitle"]))
    story.append(Spacer(1, 60))
    story.append(Paragraph(ar("د. عبدالقادر إسماعيل تاور"), st["h2"]))
    story.append(Paragraph(ar("اختصاصي تغذية الحيوان"), st["caption"]))
    story.append(Spacer(1, 15))
    story.append(Paragraph(ar("📅 " + datetime.now().strftime("%Y-%m-%d")),
                             st["center"]))
    story.append(Spacer(1, 40))
    story.append(Paragraph(
        ar("🕌 رحم الله والدي إسماعيل تاور وأختي ابتسام وأسكنهما فسيح جناته 🕌"),
        st["center"]))
    story.append(PageBreak())

    # ─── فهرس ────────────────────────────────────────────────
    story.append(Paragraph(ar("📑 جدول المحتويات"), st["h1"]))
    story.append(Spacer(1, 10))

    toc_data = [[ar("الباتش"), ar("العنوان"), ar("النوع"), ar("الموقع")]]
    for p in PATCHES:
        toc_data.append([
            p["id"], ar(p["title"]),
            ar(p["type"]), ar(p["location"]),
        ])
    toc = Table(toc_data, colWidths=[50, 190, 70, 200])
    toc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#1b5e20")),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#bdbdbd")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [HexColor("#ffffff"), HexColor("#f1f8e9")]),
    ]))
    story.append(toc)
    story.append(Spacer(1, 20))

    # ─── ترتيب التطبيق ─────────────────────────────────────
    story.append(Paragraph(ar("🎯 ترتيب التطبيق الموصى به"), st["h2"]))
    order_data = [[ar("#"), ar("الباتش"), ar("العنوان"), ar("الاعتماد")]]
    for num, pid, name, dep in APP_ORDER:
        order_data.append([num, pid, ar(name), ar(dep)])
    ot = Table(order_data, colWidths=[30, 55, 180, 240])
    ot.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#1565c0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#bdbdbd")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [HexColor("#ffffff"), HexColor("#e3f2fd")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(ot)
    story.append(PageBreak())

    # ─── الباتشات ────────────────────────────────────────────
    for idx, p in enumerate(PATCHES):
        # رأس الباتش
        badge_color = {"إضافة": "#43a047",
                        "استبدال": "#f57c00",
                        "حذف": "#c62828"}.get(p["type"], "#1565c0")

        header = Table([
            [Paragraph(f"<b>{p['id']}</b>",
                        ParagraphStyle("ph", fontName=FONT_B, fontSize=14,
                                        alignment=TA_CENTER, textColor=white)),
             Paragraph(f"<b>{ar(p['title'])}</b>",
                        ParagraphStyle("pt", fontName=FONT_B, fontSize=14,
                                        alignment=TA_RIGHT, textColor=white)),
             Paragraph(f"<b>{ar(p['type'])}</b>",
                        ParagraphStyle("pp", fontName=FONT_B, fontSize=11,
                                        alignment=TA_CENTER, textColor=white))]
        ], colWidths=[60, 350, 100])
        header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), HexColor("#0d47a1")),
            ('BACKGROUND', (1, 0), (1, 0), HexColor("#1b5e20")),
            ('BACKGROUND', (2, 0), (2, 0), HexColor(badge_color)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(header)
        story.append(Spacer(1, 8))

        # الموقع
        story.append(Paragraph(
            f"<b>📍 الموقع:</b> {ar(p['location'])}", st["body"]))
        story.append(Spacer(1, 6))

        # ابحث عن
        story.append(Paragraph(ar("🔍 ابحث عن:"), st["h2"]))
        story.append(_code_block(p["find"], max_lines=12))
        story.append(Spacer(1, 6))

        # استبدل بـ / أضف
        label = "✅ أضف" if p["type"] == "إضافة" else "✅ استبدل بـ"
        story.append(Paragraph(ar(label), st["h2"]))
        story.append(_code_block(p["replace"], max_lines=18))
        story.append(Spacer(1, 6))

        # التحقق
        verify_tbl = Table([[
            Paragraph(ar("✔️ التحقق:"),
                       ParagraphStyle("vk", fontName=FONT_B, fontSize=10,
                                       alignment=TA_RIGHT, textColor=white)),
            Paragraph(ar(p["verify"]),
                       ParagraphStyle("vv", fontName=FONT, fontSize=10,
                                       alignment=TA_RIGHT,
                                       textColor=HexColor("#1b5e20"))),
        ]], colWidths=[100, 410])
        verify_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), HexColor("#2e7d32")),
            ('BACKGROUND', (1, 0), (1, 0), HexColor("#e8f5e9")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#a5d6a7")),
        ]))
        story.append(verify_tbl)

        # فاصل بين الباتشات
        if idx < len(PATCHES) - 1:
            story.append(PageBreak())

    # ─── قائمة التحقق ───────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph(ar("✔️ قائمة التحقق النهائية"), st["h1"]))
    story.append(Paragraph(
        ar("بعد تطبيق كل الباتشات، تأكد من كل بند:"),
        st["body"]))
    story.append(Spacer(1, 10))

    check_data = [[ar("☐"), ar("#"), ar("الاختبار")]]
    for i, item in enumerate(CHECKLIST, 1):
        check_data.append(["☐", str(i), ar(item)])
    ct = Table(check_data, colWidths=[30, 30, 450])
    ct.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#1b5e20")),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#bdbdbd")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [HexColor("#ffffff"), HexColor("#f1f8e9")]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(ct)
    story.append(Spacer(1, 20))

    story.append(Paragraph(ar("📊 معمارية الأمان"), st["h1"]))
    story.append(Paragraph(
        ar("ثلاث طبقات دفاع:"), st["body"]))
    arch_data = [
        [ar("الطبقة"), ar("الدور"), ar("متى تعمل")],
        [ar("L1 — قيود LP"), ar("تمنع LP من استخدام مواد خطرة"),
         ar("قبل الحل")],
        [ar("L2 — فلترة"), ar("ترفض الحلول الخطرة وتعيد المحاولة"),
         ar("بعد الحل")],
        [ar("L3 — كاشف"), ar("تحذير نهائي مع مصدر علمي وإجراء"),
         ar("بعد العرض")],
    ]
    at = Table(arch_data, colWidths=[130, 260, 120])
    at.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor("#6a1b9a")),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#bdbdbd")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [HexColor("#f3e5f5"), HexColor("#ffffff")]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(at)

    # ─── الخاتمة ────────────────────────────────────────────
    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="80%", thickness=2,
                             color=HexColor("#d4af37"), hAlign='CENTER'))
    story.append(Spacer(1, 15))
    story.append(Paragraph(
        ar("🤲 رحم الله والدي إسماعيل تاور وأختي ابتسام 🤲"),
        st["center"]))
    story.append(Paragraph(
        ar("اللهم اجعل قبرهما روضة من رياض الجنة"), st["caption"]))

    # البناء
    doc.build(story, onFirstPage=_page_decorator,
              onLaterPages=_page_decorator)
    return output_path


# ═════════════════════════════════════════════════════════════════════
# 4) نقطة الدخول
# ═════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 60)
    print("📄 توليد PDF للباتشات — Tawor Nology 11.6.2")
    print("═" * 60)
    print(f"   عدد الباتشات: {len(PATCHES)}")
    print(f"   عدد بنود التحقق: {len(CHECKLIST)}")
    print(f"   دعم العربية: {'✅' if AR_OK else '⚠️ (النص إنجليزي)'}")
    print(f"   الخط: {FONT}")

    try:
        path = build_pdf()
        size_kb = os.path.getsize(path) / 1024
        print(f"\n✅ تم إنشاء: {path} ({size_kb:.1f} KB)")
    except Exception as e:
        print(f"\n❌ فشل: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
