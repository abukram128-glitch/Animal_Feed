import base64
import io
import json
import os
import random
import urllib.parse
from datetime import datetime
from typing import Dict, Optional

import numpy as np
import streamlit as st

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except Exception:
    go = None
    PLOTLY_AVAILABLE = False

try:
    from reportlab.lib.colors import HexColor, white
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
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
except Exception:
    REPORTLAB_AVAILABLE = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_BIDI_AVAILABLE = True
except Exception:
    ARABIC_BIDI_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════
# دوال مساعدة آمنة للتنسيق والأمان
# ═══════════════════════════════════════════════════════════════════════

def _safe_ar(text) -> str:
    if text is None:
        return ""
    s = str(text)
    if not s:
        return ""
    if ARABIC_BIDI_AVAILABLE:
        try:
            return get_display(arabic_reshaper.reshape(s), base_dir="R")
        except Exception:
            return s
    return s


def _safe_sanitize(text, max_len: int = 200) -> str:
    if text is None:
        return ""
    if "_sanitize_message" in globals() and callable(globals()["_sanitize_message"]):
        try:
            return globals()["_sanitize_message"](text, max_len)
        except Exception:
            pass
    cleaned = " ".join(str(text).split())
    return cleaned[:max_len]


def _get_font_name() -> str:
    if "font_mgr" in globals() and getattr(globals()["font_mgr"], "font_name", None):
        return globals()["font_mgr"].font_name
    return "Helvetica"


def _get_global(name: str, default):
    val = globals().get(name, default)
    return default if val is None else val


# ═══════════════════════════════════════════════════════════════════════
# PDF Generator
# ═══════════════════════════════════════════════════════════════════════

class PDFGenerator:
    def __init__(self):
        self.font_name = _get_font_name()
        self.logo_path = None
        logo_candidates = list(_get_global("LOGO_OPTIONS", [])) + list(_get_global("PHOTO_OPTIONS", []))
        for lp in logo_candidates:
            if lp and os.path.exists(lp):
                self.logo_path = lp
                break

    def _ar(self, t) -> str:
        return _safe_ar(t)

    def _para_style(self, name: str, size: int = 11, align=None, color: str = "#1a1a1a",
                    space_after: int = 6, leading_mult: float = 1.6, font_name: Optional[str] = None,
                    left_indent: int = 0):
        if not REPORTLAB_AVAILABLE:
            return None
        if align is None:
            align = TA_RIGHT
        return ParagraphStyle(
            name=name,
            fontName=font_name or self.font_name,
            fontSize=size,
            alignment=align,
            textColor=HexColor(color),
            spaceAfter=space_after,
            leading=max(size * leading_mult, size + 2),
            leftIndent=left_indent,
        )

    def _draw_page(self, canvas_obj, doc):
        if not REPORTLAB_AVAILABLE:
            return
        try:
            canvas_obj.saveState()
            w, h = doc.pagesize
            supervisor = _get_global("SUPERVISOR", "د. عبدالقادر إسماعيل")
            dua_short = _get_global("DUA_SHORT", "اللهم بارك لنا فيما رزقتنا")

            # رأس الصفحة
            canvas_obj.setFillColor(HexColor("#1b5e20"))
            canvas_obj.rect(0, h - 90, w, 90, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor("#d4af37"))
            canvas_obj.rect(0, h - 95, w, 5, fill=1, stroke=0)

            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 20)
            canvas_obj.drawCentredString(w / 2, h - 38, self._ar("تاور نولجي  Tawor Nology"))

            canvas_obj.setFont(self.font_name, 12)
            canvas_obj.setFillColor(HexColor("#e8f5e9"))
            canvas_obj.drawCentredString(w / 2, h - 58, self._ar("للإنتاج الحيواني وتغذية الحيوان"))

            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.setFillColor(HexColor("#d4af37"))
            canvas_obj.drawCentredString(w / 2, h - 76, self._ar(f"إشراف: {supervisor}"))

            # شريط الدعاء أعلى التذييل
            canvas_obj.setFillColor(HexColor("#1b5e20"))
            canvas_obj.rect(0, 42, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor("#d4af37"))
            canvas_obj.rect(0, 84, w, 3, fill=1, stroke=0)
            canvas_obj.setFillColor(HexColor("#ffeb3b"))
            canvas_obj.setFont(self.font_name, 10)
            canvas_obj.drawCentredString(w / 2, 62, self._ar(f"🤲 {dua_short} 🤲"))

            # التذييل السفلي ورقم الصفحة
            canvas_obj.setFillColor(HexColor("#1b5e20"))
            canvas_obj.rect(0, 0, w, 42, fill=1, stroke=0)
            canvas_obj.setFillColor(white)
            canvas_obj.setFont(self.font_name, 8)
            canvas_obj.drawCentredString(w / 2, 25, self._ar("تاور نولجي © 2026"))
            canvas_obj.setFont(self.font_name, 7)
            canvas_obj.drawCentredString(
                w / 2, 11, self._ar(f"صفحة {canvas_obj.getPageNumber()}")
            )
            canvas_obj.restoreState()
        except Exception:
            pass

    def _add_references_page(self, story, animal_type, production_type):
        if not REPORTLAB_AVAILABLE:
            return
        try:
            get_refs_fn = _get_global("get_references", lambda a, p: {})
            get_eqs_fn = _get_global("get_reference_equations", lambda a, p: {})
            gen_refs = _get_global("GENERAL_REFERENCES", [])

            refs = get_refs_fn(animal_type, production_type) or {}
            eqs = get_eqs_fn(animal_type, production_type) or {}

            story.append(PageBreak())
            story.append(
                Paragraph(
                    self._ar("📚 المراجع والمعادلات"),
                    self._para_style("rt", size=16, align=TA_CENTER, color="#1b5e20", space_after=15),
                )
            )
            if refs.get("primary"):
                story.append(
                    Paragraph(
                        self._ar(f"📖 المرجع: {refs['primary']}"),
                        self._para_style("rp", size=11, align=TA_RIGHT, color="#0d47a1", space_after=8),
                    )
                )
            if refs.get("table"):
                story.append(
                    Paragraph(
                        self._ar(f"📑 الجدول: {refs['table']}"),
                        self._para_style("rt2", size=10, align=TA_RIGHT, color="#1565c0", space_after=8),
                    )
                )
            if eqs:
                story.append(Spacer(1, 10))
                story.append(
                    Paragraph(
                        self._ar("📐 المعادلات المرجعية:"),
                        self._para_style("eqt", size=12, align=TA_RIGHT, color="#2e7d32", space_after=8),
                    )
                )
                eq_data = [[self._ar("المؤشر"), self._ar("المعادلة")]]
                for k, v in eqs.items():
                    if k in ("source", "example"):
                        continue
                    eq_data.append([self._ar(k), self._ar(v)])
                if len(eq_data) > 1:
                    et = Table(eq_data, colWidths=[110, 380])
                    et.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2e7d32")),
                                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                                ("BOX", (0, 0), (-1, -1), 1.5, HexColor("#2e7d32")),
                                ("INNERGRID", (0, 0), (-1, -1), 0.5, HexColor("#c8e6c9")),
                                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                                ("FONTNAME", (0, 0), (-1, -1), self.font_name),
                                ("FONTSIZE", (0, 0), (-1, -1), 9),
                                ("PADDING", (0, 0), (-1, -1), 5),
                            ]
                        )
                    )
                    story.append(et)

                if eqs.get("example"):
                    story.append(Spacer(1, 8))
                    story.append(
                        Paragraph(
                            self._ar(f"💡 مثال: {eqs['example']}"),
                            self._para_style("ex", size=10, align=TA_RIGHT, color="#c62828"),
                        )
                    )

            if refs.get("secondary"):
                story.append(Spacer(1, 12))
                story.append(
                    Paragraph(
                        self._ar("📚 مراجع داعمة:"),
                        self._para_style("rst", size=11, align=TA_RIGHT, color="#2e7d32", space_after=6),
                    )
                )
                for sec in refs["secondary"]:
                    story.append(
                        Paragraph(
                            self._ar(f"• {sec}"),
                            self._para_style("rs", size=10, align=TA_RIGHT, space_after=4),
                        )
                    )

            if gen_refs:
                story.append(Spacer(1, 15))
                story.append(HRFlowable(width="100%", thickness=1.5, color=HexColor("#d4af37")))
                story.append(Spacer(1, 10))
                story.append(
                    Paragraph(
                        self._ar("📖 مراجع عامة:"),
                        self._para_style("rg", size=11, align=TA_RIGHT, color="#1b5e20", space_after=8),
                    )
                )
                for i, ref in enumerate(gen_refs, 1):
                    ref_str = str(ref)
                    has_arabic = any("\u0600" <= ch <= "\u06ff" for ch in ref_str)
                    story.append(
                        Paragraph(
                            self._ar(f"{i}. {ref_str}") if has_arabic else f"{i}. {ref_str}",
                            self._para_style(
                                f"rli_{i}",
                                size=9,
                                align=TA_RIGHT if has_arabic else TA_LEFT,
                                space_after=4,
                                leading_mult=1.35,
                                font_name=self.font_name if has_arabic else "Helvetica",
                                left_indent=0 if has_arabic else 10,
                            ),
                        )
                    )
        except Exception as e:
            story.append(
                Paragraph(
                    self._ar(f"تعذر تحميل المراجع: {e}"),
                    self._para_style("err", size=9, align=TA_RIGHT, color="#c62828"),
                )
            )

    def _comparison_table(self, std: Dict, calc: Dict):
        labels = {
            "CP": "بروتين",
            "DP": "مهضوم",
            "SE": "SE",
            "NDF": "NDF",
            "ADF": "ADF",
            "EE": "دهن",
            "ASH": "رماد",
            "Ca": "Ca",
            "P": "P",
        }
        eval_fn = _get_global(
            "evaluate_difference",
            lambda pct, standard_value=0: {"label": "—", "bg": "#ffffff"},
        )
        data = [[self._ar(x) for x in ["العنصر", "المعيار", "المحسوب", "الفرق", "%", "التقييم"]]]
        cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1b5e20")),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), self.font_name),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 1, HexColor("#9e9e9e")),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]
        row = 1
        for k in ["CP", "DP", "SE", "NDF", "ADF", "EE", "ASH", "Ca", "P"]:
            if k not in std or not std[k]:
                continue
            sv = float(std[k])
            cv = float(calc.get(k, 0) or 0)
            diff = cv - sv
            pct = (diff / sv * 100.0) if sv else 0.0
            ev = eval_fn(pct, standard_value=sv) or {}
            bg_hex = ev.get("bg", "#ffffff")
            data.append([
                self._ar(labels[k]),
                f"{sv:.2f}",
                f"{cv:.2f}",
                f"{diff:+.3f}",
                f"{pct:+.2f}%",
                self._ar(ev.get("label", "—")),
            ])
            try:
                cmds.append(("BACKGROUND", (0, row), (-1, row), HexColor(bg_hex)))
            except Exception:
                pass
            row += 1

        if len(data) == 1:
            data.append([self._ar("لا توجد بيانات مقارنة"), "—", "—", "—", "—", "—"])

        t = Table(data, colWidths=[100, 70, 70, 70, 70, 105])
        t.setStyle(TableStyle(cmds))
        return t

    def generate_report(
        self,
        formula: Dict,
        requirement,
        animal_type: str,
        breed: str,
        cost: float,
        city: str = "",
        local_cost: Optional[float] = None,
        local_sym: str = "",
        requester_name: str = "",
        protein_basis: str = "DP",
        standard_key: str = "",
        include_charts: bool = True,
        quality_score: float = 0.0,
    ) -> Optional[bytes]:
        if not REPORTLAB_AVAILABLE:
            return None
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=115,
                bottomMargin=145,
            )
            story = []

            def P(text, size=11, align=TA_RIGHT, color="#1a1a1a"):
                return Paragraph(
                    self._ar(text),
                    self._para_style("rep_p", size=size, align=align, color=color),
                )

            story.append(P("تقرير فني رسمي", size=20, align=TA_CENTER, color="#1b5e20"))
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor("#d4af37")))
            story.append(Spacer(1, 12))

            client = [
                [self._ar("👤 طالب:"), self._ar(requester_name or "—")],
                [self._ar("🐾 الفصيل:"), self._ar(f"{animal_type or '—'} — {breed or '—'}")],
                [self._ar("📍 الموقع:"), self._ar(city or "—")],
                [self._ar("🧬 الأساس:"), self._ar(protein_basis or "—")],
                [self._ar("📅 التاريخ:"), datetime.now().strftime("%Y-%m-%d")],
            ]
            ct = Table(client, colWidths=[150, 340])
            ct.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, -1), HexColor("#e8f5e9")),
                        ("BOX", (0, 0), (-1, -1), 1.5, HexColor("#2e7d32")),
                        ("INNERGRID", (0, 0), (-1, -1), 0.6, HexColor("#c8e6c9")),
                        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                        ("FONTNAME", (0, 0), (-1, -1), self.font_name),
                        ("FONTSIZE", (0, 0), (-1, -1), 11),
                        ("PADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )
            story.append(ct)
            story.append(Spacer(1, 15))

            req_to_std = _get_global("requirement_to_standard", lambda r: {})
            comp_nutrients = _get_global("compute_formula_nutrients", lambda f: {})
            std_vals = req_to_std(requirement) or {}
            calc_vals = comp_nutrients(formula or {}) or {}

            q_score = float(quality_score or 0.0)
            passed = q_score >= 70.0
            qd = [
                [self._ar("الجودة"), self._ar("الحالة"), self._ar("حد القبول 70%")],
                [
                    f"{q_score:.1f}%",
                    self._ar("✅ ناجح" if passed else "⚠️ يحتاج تحسين"),
                    self._ar("✅" if passed else "❌"),
                ],
            ]
            qt = Table(qd, colWidths=[130, 200, 160])
            qt.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1565c0")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), white),
                        ("BACKGROUND", (0, 1), (-1, -1), HexColor("#e8f5e9" if passed else "#ffebee")),
                        ("GRID", (0, 0), (-1, -1), 1, HexColor("#1976d2")),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, -1), self.font_name),
                    ]
                )
            )
            story.append(qt)
            story.append(Spacer(1, 15))

            story.append(P("📊 مقارنة العناصر", size=14, color="#1b5e20"))
            story.append(Spacer(1, 8))
            story.append(self._comparison_table(std_vals, calc_vals))

            if include_charts:
                story.append(Spacer(1, 15))
                chart_specs = [
                    ("create_colorful_bar_chart", (std_vals, calc_vals)),
                    ("create_colorful_pie_chart", (formula or {},)),
                    ("create_radar_chart", (std_vals, calc_vals)),
                ]
                for fn_name, args in chart_specs:
                    fn = _get_global(fn_name, None)
                    if callable(fn):
                        try:
                            c = fn(*args)
                            if c:
                                story.append(RLImage(c, width=450, height=250))
                                story.append(Spacer(1, 10))
                        except Exception:
                            pass

            story.append(PageBreak())
            story.append(P("💰 التكاليف", size=14, color="#1b5e20"))
            cost_val = float(cost or 0.0)
            cost_data = [
                [self._ar("البند"), self._ar("القيمة")],
                [self._ar("التكلفة/طن (دولار)"), f"${cost_val:.2f}"],
            ]
            if local_cost is not None:
                try:
                    lc_num = float(local_cost)
                    sym_clean = _safe_sanitize(local_sym, 15)
                    cost_data.append([
                        self._ar("التكلفة/طن (محلي)"),
                        self._ar(f"{lc_num:.2f} {sym_clean}".strip()),
                    ])
                except Exception:
                    pass

            tc = Table(cost_data, colWidths=[280, 210])
            tc.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1b5e20")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), white),
                        ("GRID", (0, 0), (-1, -1), 1, HexColor("#2e7d32")),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, -1), self.font_name),
                    ]
                )
            )
            story.append(tc)
            story.append(Spacer(1, 18))

            if formula:
                story.append(P("🌾 المكونات للطن", size=14, color="#1b5e20"))
                ing_data = [[self._ar("المكون"), self._ar("%"), self._ar("كجم/طن")]]
                for ing, pct in formula.items():
                    pct_val = float(pct or 0.0)
                    ing_data.append([self._ar(ing), f"{pct_val:.2f}%", f"{pct_val * 10.0:.1f}"])
                ti = Table(ing_data, colWidths=[270, 110, 110])
                ti.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2e7d32")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), white),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, -1), self.font_name),
                            ("GRID", (0, 0), (-1, -1), 1, HexColor("#bdbdbd")),
                            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f5f5f5")]),
                        ]
                    )
                )
                story.append(ti)
                story.append(Spacer(1, 25))

            self._add_references_page(story, animal_type, standard_key or breed)
            doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
            buffer.seek(0)
            return buffer.getvalue()
        except Exception:
            return None

    def generate_ocr_report(self, ingredients: Dict, nutrients: Dict = None, raw_text: str = "") -> Optional[bytes]:
        if not REPORTLAB_AVAILABLE:
            return None
        try:
            ingredients = ingredients or {}
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=115,
                bottomMargin=145,
            )
            story = []

            def P(text, size=11, align=TA_RIGHT, color="#1a1a1a"):
                return Paragraph(
                    self._ar(text),
                    self._para_style("ocr_p", size=size, align=align, color=color),
                )

            story.append(P("تقرير تحليل OCR", size=20, align=TA_CENTER, color="#1b5e20"))
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor("#d4af37")))
            story.append(Spacer(1, 12))

            total_pct = 0.0
            data = [[self._ar("المادة"), self._ar("%")]]
            for k, v in ingredients.items():
                val = float(v or 0.0)
                total_pct += val
                data.append([self._ar(k), f"{val:.2f}%"])
            data.append([self._ar("الإجمالي"), f"{total_pct:.2f}%"])

            t = Table(data, colWidths=[300, 200])
            t.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1b5e20")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, -1), self.font_name),
                        ("GRID", (0, 0), (-1, -1), 1, HexColor("#bdbdbd")),
                        ("BACKGROUND", (0, -1), (-1, -1), HexColor("#ffe0b2")),
                    ]
                )
            )
            story.append(t)

            if nutrients:
                story.append(Spacer(1, 16))
                story.append(P("🧪 العناصر الغذائية المستخرجة", size=14, color="#1b5e20"))
                ndata = [[self._ar("العنصر"), self._ar("القيمة")]]
                for nk, nv in nutrients.items():
                    ndata.append([self._ar(nk), self._ar(nv)])
                nt = Table(ndata, colWidths=[300, 200])
                nt.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1565c0")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), white),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, -1), self.font_name),
                            ("GRID", (0, 0), (-1, -1), 0.8, HexColor("#bdbdbd")),
                        ]
                    )
                )
                story.append(nt)

            if raw_text:
                story.append(Spacer(1, 14))
                story.append(P("📝 النص الخام المستخرج", size=12, color="#1565c0"))
                story.append(P(_safe_sanitize(raw_text, 1000), size=9, color="#333333"))

            doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
            buffer.seek(0)
            return buffer.getvalue()
        except Exception:
            return None


pdf_gen = PDFGenerator()


def generate_nlp_math_pdf(result: Dict, animal_type: str, production_type: str,
                          nlp_sel=None, ing_data=None, nlp_prices=None) -> Optional[bytes]:
    if not REPORTLAB_AVAILABLE or not isinstance(result, dict):
        return None
    try:
        font_name = _get_font_name()
        supervisor = _get_global("SUPERVISOR", "د. عبدالقادر إسماعيل")
        supervisor_title = _get_global("SUPERVISOR_TITLE", "")
        ref_eqs_all = _get_global("REFERENCE_EQUATIONS", {})
        comp_nutrients = _get_global("compute_formula_nutrients", lambda f: {})
        get_nlp_req = _get_global("_get_requirement_for_nlp", lambda a, p: {})

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=115,
            bottomMargin=145,
        )
        story = []

        def P(text, size=11, align=TA_RIGHT, color="#1a1a1a"):
            return Paragraph(
                _safe_ar(text),
                ParagraphStyle(
                    "nlp_p",
                    fontName=font_name,
                    fontSize=size,
                    alignment=align,
                    textColor=HexColor(color),
                    spaceAfter=6,
                    leading=size * 1.6,
                ),
            )

        story.append(P("تقرير التحسين غير الخطي (NLP)", size=20, align=TA_CENTER, color="#1b5e20"))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor("#d4af37")))
        story.append(Spacer(1, 12))

        info = [
            [_safe_ar("الحيوان"), _safe_ar(animal_type or "—")],
            [_safe_ar("الحالة"), _safe_ar(production_type or "—")],
            [_safe_ar("الاستراتيجية"), _safe_ar(result.get("strategy", "—"))],
            [_safe_ar("التكلفة"), f"${float(result.get('final_cost', 0.0)):.4f}/كجم"],
            [_safe_ar("الطاقة"), f"{float(result.get('final_me', 0.0)):.0f} kcal/kg"],
            [_safe_ar("البروتين"), f"{float(result.get('final_cp', 0.0)):.2f}%"],
            [_safe_ar("صافي الربح"), f"${float(result.get('max_profit', 0.0)):.4f}"],
        ]
        t = Table(info, colWidths=[160, 330])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), HexColor("#e8f5e9")),
                    ("BOX", (0, 0), (-1, -1), 1.5, HexColor("#2e7d32")),
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 15))

        nlp_eq = ref_eqs_all.get("معادلة_التركيب_NLP", {})
        if nlp_eq:
            story.append(P("📐 المعادلات", size=14, color="#1565c0"))
            story.append(Spacer(1, 8))
            eq_data = [[_safe_ar("البند"), _safe_ar("القيمة")]]
            for k, v in nlp_eq.items():
                if k == "source":
                    continue
                eq_data.append([_safe_ar(k), _safe_ar(v)])
            et = Table(eq_data, colWidths=[130, 360])
            et.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1565c0")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), white),
                        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                        ("FONTNAME", (0, 0), (-1, -1), font_name),
                        ("GRID", (0, 0), (-1, -1), 0.6, HexColor("#bbdefb")),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("PADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.append(et)

        formula_map = result.get("formula") or {}
        if formula_map:
            story.append(PageBreak())
            story.append(P("🌾 التركيبة", size=16, color="#1b5e20"))
            ing_pdf = [[_safe_ar("المكوّن"), _safe_ar("%"), _safe_ar("كجم/طن")]]
            for ing, pct in formula_map.items():
                pct_val = float(pct or 0.0)
                ing_pdf.append([_safe_ar(ing), f"{pct_val:.2f}%", f"{pct_val * 10.0:.1f}"])
            it = Table(ing_pdf, colWidths=[280, 110, 110])
            it.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2e7d32")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, -1), font_name),
                        ("GRID", (0, 0), (-1, -1), 0.8, HexColor("#bdbdbd")),
                    ]
                )
            )
            story.append(it)

        bar_fn = _get_global("create_colorful_bar_chart", None)
        pie_fn = _get_global("create_colorful_pie_chart", None)
        if callable(bar_fn) or callable(pie_fn):
            story.append(PageBreak())
            story.append(P("📈 الرسوم", size=16, color="#1b5e20"))
            story.append(Spacer(1, 10))
            if callable(bar_fn):
                try:
                    actual = comp_nutrients(formula_map) or {}
                    nlp_req = get_nlp_req(animal_type, production_type) or {}
                    if "ME" in nlp_req and "CP" in nlp_req and "DP" in nlp_req:
                        std_c = {
                            "ME/100": float(nlp_req["ME"]) / 100.0,
                            "CP": float(nlp_req["CP"]),
                            "DP": float(nlp_req["DP"]),
                        }
                        act_c = {
                            "ME/100": float(actual.get("SE", 0.0)) * 41.0 / 100.0,
                            "CP": float(actual.get("CP", 0.0)),
                            "DP": float(actual.get("DP", 0.0)),
                        }
                        bf = bar_fn(std_c, act_c)
                        if bf:
                            story.append(RLImage(bf, width=470, height=250))
                            story.append(P("1️⃣ مقارنة ME/CP/DP", size=9, align=TA_CENTER, color="#555555"))
                            story.append(Spacer(1, 8))
                except Exception:
                    pass
            if callable(pie_fn) and formula_map:
                try:
                    pf = pie_fn(formula_map)
                    if pf:
                        story.append(RLImage(pf, width=380, height=240))
                        story.append(P("2️⃣ التوزيع", size=9, align=TA_CENTER, color="#555555"))
                except Exception:
                    pass

        pdf_gen._add_references_page(story, animal_type, production_type)
        story.append(Spacer(1, 20))
        story.append(P(supervisor, size=16, align=TA_CENTER, color="#c62828"))
        if supervisor_title:
            story.append(P(supervisor_title, size=11, align=TA_CENTER, color="#1b5e20"))

        doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception:
        return None


def generate_milk_replacer_pdf(result: Dict) -> Optional[bytes]:
    if not REPORTLAB_AVAILABLE or not isinstance(result, dict):
        return None
    try:
        font_name = _get_font_name()
        supervisor = _get_global("SUPERVISOR", "د. عبدالقادر إسماعيل")
        supervisor_title = _get_global("SUPERVISOR_TITLE", "")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=115,
            bottomMargin=145,
        )
        story = []

        def P(text, size=11, align=TA_RIGHT, color="#1a1a1a"):
            return Paragraph(
                _safe_ar(text),
                ParagraphStyle(
                    "mr_p",
                    fontName=font_name,
                    fontSize=size,
                    alignment=align,
                    textColor=HexColor(color),
                    spaceAfter=6,
                    leading=size * 1.6,
                ),
            )

        std = result.get("standard") or {}
        quality = float(result.get("quality_score", 0.0) or 0.0)
        formula = result.get("formula") or {}
        volume = float(result.get("volume", 100.0) or 100.0)
        animal_name = result.get("animal", "عجول")
        prod_type = result.get("production_type", "حليب")

        story.append(P("تقرير بديل الحليب", size=20, align=TA_CENTER, color="#1b5e20"))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor("#d4af37")))
        story.append(Spacer(1, 10))

        info = [
            [_safe_ar("الحيوان:"), _safe_ar(animal_name)],
            [_safe_ar("المرجع:"), _safe_ar(std.get("source", "—"))],
            [_safe_ar("الجودة:"), f"{quality:.1f}%"],
            [_safe_ar("الكمية:"), _safe_ar(f"{volume:.0f} كجم")],
        ]
        ct = Table(info, colWidths=[160, 330])
        ct.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), HexColor("#e3f2fd")),
                    ("BOX", (0, 0), (-1, -1), 1.5, HexColor("#1565c0")),
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("PADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )
        story.append(ct)
        story.append(Spacer(1, 15))

        if formula:
            story.append(P("🍼 المكونات", size=14, color="#1b5e20"))
            ing_data = [[_safe_ar("المكون"), _safe_ar("%"), _safe_ar("كجم")]]
            for ing, pct in formula.items():
                pct_val = float(pct or 0.0)
                kg = pct_val * volume / 100.0
                ing_data.append([_safe_ar(ing), f"{pct_val:.2f}%", f"{kg:.2f}"])
            it = Table(ing_data, colWidths=[200, 130, 130])
            it.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2e7d32")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, -1), font_name),
                        ("GRID", (0, 0), (-1, -1), 0.8, HexColor("#bdbdbd")),
                    ]
                )
            )
            story.append(it)

        pdf_gen._add_references_page(story, animal_name, prod_type)
        story.append(Spacer(1, 20))
        story.append(P(supervisor, size=16, align=TA_CENTER, color="#c62828"))
        if supervisor_title:
            story.append(P(supervisor_title, size=11, align=TA_CENTER, color="#1b5e20"))

        doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception:
        return None


def generate_lab_pdf(result: Dict, ctx: Dict = None) -> Optional[bytes]:
    if not REPORTLAB_AVAILABLE or not isinstance(result, dict):
        return None
    try:
        ctx = ctx or {}
        font_name = _get_font_name()
        supervisor = _get_global("SUPERVISOR", "د. عبدالقادر إسماعيل")
        supervisor_title = _get_global("SUPERVISOR_TITLE", "")
        get_eqs_fn = _get_global("get_reference_equations", lambda a, p: {})

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=115,
            bottomMargin=145,
        )
        story = []

        def P(text, size=11, align=TA_RIGHT, color="#1a1a1a"):
            return Paragraph(
                _safe_ar(text),
                ParagraphStyle(
                    "lab_p",
                    fontName=font_name,
                    fontSize=size,
                    alignment=align,
                    textColor=HexColor(color),
                    spaceAfter=6,
                    leading=size * 1.6,
                ),
            )

        story.append(P("تقرير تحليل تركيبة", size=18, align=TA_CENTER, color="#1b5e20"))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor("#d4af37")))
        story.append(Spacer(1, 10))

        info = [
            [_safe_ar("الحيوان"), _safe_ar(ctx.get("animal") or result.get("animal_type") or "—")],
            [_safe_ar("الإنتاج"), _safe_ar(ctx.get("production") or result.get("production_type") or "—")],
            [_safe_ar("الجودة"), f"{float(result.get('quality_score', 0.0) or 0.0):.1f}%"],
            [_safe_ar("Ca:P"), f"{float(result.get('ca_p_ratio', 0.0) or 0.0):.2f}"],
            [_safe_ar("التكلفة"), f"${float(result.get('cost_per_ton', 0.0) or 0.0):.2f}"],
            [_safe_ar("التاريخ"), datetime.now().strftime("%Y-%m-%d %H:%M")],
        ]
        t = Table(info, colWidths=[160, 330])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), HexColor("#e8f5e9")),
                    ("BOX", (0, 0), (-1, -1), 1.5, HexColor("#2e7d32")),
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 15))

        comp_rows = result.get("comparison") or []
        if comp_rows:
            story.append(P("📊 المقارنة", size=14, color="#1b5e20"))
            data = [[_safe_ar(x) for x in ["العنصر", "المعيار", "المحسوب", "الفرق", "%", "التقييم"]]]
            cmds = [
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1b5e20")),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("GRID", (0, 0), (-1, -1), 0.8, HexColor("#9e9e9e")),
            ]
            for i, c in enumerate(comp_rows, 1):
                std_v = float(c.get("المعيار", 0.0) or 0.0)
                calc_v = float(c.get("المحسوب", 0.0) or 0.0)
                diff_v = float(c.get("الفرق", calc_v - std_v) or 0.0)
                pct_v = float(c.get("الفرق %", 0.0) or 0.0)
                score_v = float(c.get("score", 0.0) or 0.0)
                data.append([
                    _safe_ar(c.get("العنصر", "—")),
                    f"{std_v:.2f}",
                    f"{calc_v:.2f}",
                    f"{diff_v:+.3f}",
                    f"{pct_v:+.2f}%",
                    _safe_ar(c.get("التقييم", "—")),
                ])
                bg = "#e8f5e9" if score_v >= 70 else "#ffebee" if score_v < 50 else "#fff8e1"
                cmds.append(("BACKGROUND", (0, i), (-1, i), HexColor(bg)))
            ct = Table(data, colWidths=[90, 65, 65, 65, 65, 120])
            ct.setStyle(TableStyle(cmds))
            story.append(ct)

        animal_t = result.get("animal_type") or ctx.get("animal") or "عام"
        prod_t = result.get("production_type") or ctx.get("production") or "عام"
        eqs = get_eqs_fn(animal_t, prod_t) or {}
        if eqs:
            story.append(PageBreak())
            story.append(P("📐 المعادلات المرجعية", size=14, color="#1565c0"))
            eq_data = [[_safe_ar("المؤشر"), _safe_ar("المعادلة")]]
            for k, v in eqs.items():
                if k in ("source", "example"):
                    continue
                eq_data.append([_safe_ar(k), _safe_ar(v)])
            if len(eq_data) > 1:
                et = Table(eq_data, colWidths=[100, 390])
                et.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1565c0")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), white),
                            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                            ("FONTNAME", (0, 0), (-1, -1), font_name),
                            ("GRID", (0, 0), (-1, -1), 0.6, HexColor("#bbdefb")),
                            ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ]
                    )
                )
                story.append(et)

        pdf_gen._add_references_page(story, animal_t, prod_t)
        story.append(Spacer(1, 20))
        story.append(P(supervisor, size=16, align=TA_CENTER, color="#c62828"))
        if supervisor_title:
            story.append(P(supervisor_title, size=11, align=TA_CENTER, color="#1b5e20"))

        doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception:
        return None


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
                if isinstance(data, dict) and isinstance(data.get("requests"), list):
                    return data
    except Exception:
        pass
    return {"requests": []}


def _save_pdf_requests(data: Dict) -> bool:
    try:
        tmp = PDF_REQUESTS_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, PDF_REQUESTS_FILE)
        return True
    except Exception:
        return False


def create_pdf_request(
    user_name: str,
    user_role: str,
    pdf_bytes: bytes,
    doc_title: str,
    doc_context: Dict = None,
) -> str:
    if not isinstance(pdf_bytes, (bytes, bytearray)) or len(pdf_bytes) == 0:
        return "ERR_EMPTY_PDF"
    try:
        request_id = f"REQ_{datetime.now():%Y%m%d%H%M%S}_{random.randint(100, 999)}"
        pdf_path = os.path.join(PDF_STORAGE_DIR, f"{request_id}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(bytes(pdf_bytes))

        data = _load_pdf_requests()
        data["requests"].append(
            {
                "id": request_id,
                "user_name": _safe_sanitize(user_name, 50) or "غير محدد",
                "user_role": _safe_sanitize(user_role, 30) or "user",
                "doc_title": _safe_sanitize(doc_title, 100) or "تقرير PDF",
                "doc_context": doc_context if isinstance(doc_context, dict) else {},
                "pdf_path": pdf_path,
                "status": "pending",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "reviewed_at": None,
                "rejection_reason": None,
            }
        )
        data["requests"] = data["requests"][-200:]
        if not _save_pdf_requests(data):
            return "ERR_SAVE_FAILED"
        return request_id
    except Exception as e:
        return f"ERR_{e}"


def get_user_pending_request(user_name: str, doc_title: str) -> Optional[Dict]:
    clean_user = _safe_sanitize(user_name, 50)
    clean_title = _safe_sanitize(doc_title, 100)
    data = _load_pdf_requests()
    for req in reversed(data["requests"]):
        if req.get("user_name") == clean_user and req.get("doc_title") == clean_title:
            return req
    return None


def approve_pdf_request(request_id: str) -> bool:
    data = _load_pdf_requests()
    for req in data["requests"]:
        if req.get("id") == request_id:
            req["status"] = "approved"
            req["reviewed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return _save_pdf_requests(data)
    return False


def reject_pdf_request(request_id: str, reason: str = "") -> bool:
    data = _load_pdf_requests()
    for req in data["requests"]:
        if req.get("id") == request_id:
            req["status"] = "rejected"
            req["reviewed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            req["rejection_reason"] = _safe_sanitize(reason, 200)
            return _save_pdf_requests(data)
    return False


def _read_pdf_bytes(request_id: str) -> Optional[bytes]:
    try:
        safe_id = os.path.basename(str(request_id))
        if not safe_id.endswith(".pdf"):
            safe_id = f"{safe_id}.pdf"
        path = os.path.join(PDF_STORAGE_DIR, safe_id)
        if os.path.exists(path):
            with open(path, "rb") as f:
                content = f.read()
                return content if content else None
    except Exception:
        pass
    return None


# ═══ أزرار التواصل والاستشارة ═══

def render_consultation_buttons(key_suffix: str = ""):
    supervisor = _safe_sanitize(_get_global("SUPERVISOR", "د. عبدالقادر إسماعيل"), 80)
    supervisor_title = _safe_sanitize(_get_global("SUPERVISOR_TITLE", ""), 120)
    app_name = _safe_sanitize(_get_global("APP_NAME", "تاور نولجي"), 80)
    wa_raw = str(_get_global("WHATSAPP_NUMBER", "") or "")
    wa_clean = "".join(ch for ch in wa_raw if ch.isdigit())
    owner_email = _safe_sanitize(_get_global("OWNER_EMAIL", ""), 120)

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
            <b style="color:#c62828;">{supervisor}</b><br>
            <span style="color:#1565c0;">{supervisor_title}</span>
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    consult_msg = urllib.parse.quote(
        f"السلام عليكم {supervisor}،\nأرغب في استشارة حول تركيبة علفية.\nالمنصة: {app_name}"
    )

    with col1:
        if wa_clean:
            wa_url = f"https://wa.me/{wa_clean}?text={consult_msg}"
            st.markdown(
                f"""
            <a href="{wa_url}" target="_blank" rel="noopener noreferrer"
               style="display:block; padding:14px; background:#25d366;
                      color:white; text-decoration:none; border-radius:10px;
                      text-align:center; font-weight:700; font-size:1rem;
                      border:2px solid #128c7e;">
                📱 استشارة واتساب
            </a>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.button("📱 واتساب غير متاح", disabled=True, use_container_width=True, key=f"wa_dis_{key_suffix}")

    with col2:
        if owner_email:
            em_consult = (
                f"mailto:{owner_email}?subject="
                + urllib.parse.quote(f"طلب استشارة - {app_name}")
                + "&body="
                + urllib.parse.quote(
                    f"السلام عليكم {supervisor}،\n\nأرغب في استشارة حول تركيبة علفية.\n\nجزاك الله خيراً"
                )
            )
            st.markdown(
                f"""
            <a href="{em_consult}"
               style="display:block; padding:14px; background:#1565c0;
                      color:white; text-decoration:none; border-radius:10px;
                      text-align:center; font-weight:700; font-size:1rem;
                      border:2px solid #0d47a1;">
                ✉️ استشارة بريد
            </a>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.button("✉️ بريد غير متاح", disabled=True, use_container_width=True, key=f"em_dis_{key_suffix}")

    with col3:
        if wa_clean:
            st.markdown(
                f"""
            <a href="tel:+{wa_clean}"
               style="display:block; padding:14px; background:#c62828;
                      color:white; text-decoration:none; border-radius:10px;
                      text-align:center; font-weight:700; font-size:1rem;
                      border:2px solid #8e0000;">
                📞 اتصال مباشر
            </a>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.button("📞 اتصال غير متاح", disabled=True, use_container_width=True, key=f"tel_dis_{key_suffix}")


def render_pdf_download_with_approval(
    pdf_bytes: bytes,
    file_name: str,
    doc_title: str,
    user_role: str,
    user_name: str = "",
    doc_context: Dict = None,
    key_suffix: str = "",
):
    """عرض زر تحميل PDF مع نظام الموافقة"""
    if user_role == "owner":
        if pdf_bytes:
            st.download_button(
                "📄 تحميل PDF (مالك)",
                pdf_bytes,
                file_name=file_name,
                mime="application/pdf",
                use_container_width=True,
                type="primary",
                key=f"pdf_direct_{key_suffix}",
            )
        else:
            st.warning("⚠️ تعذر إنشاء ملف PDF لهذا التقرير")
        return

    resolved_user = _safe_sanitize(
        user_name or st.session_state.get("chat_username", "مستخدم"), 50
    ) or "مستخدم"
    clean_title = _safe_sanitize(doc_title, 100) or "تقرير PDF"

    existing = get_user_pending_request(resolved_user, clean_title)

    if existing:
        status = existing.get("status")
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
                if pdf_bytes and st.button(
                    "📤 إرسال ملف جديد للموافقة",
                    use_container_width=True,
                    key=f"pdf_req_reupload_{key_suffix}",
                ):
                    rid = create_pdf_request(resolved_user, user_role, pdf_bytes, clean_title, doc_context)
                    if rid.startswith("REQ_"):
                        st.success(f"✅ تم إرسال الطلب: {rid}")
                        st.rerun()
        elif status == "pending":
            st.warning(
                f"⏳ طلبك قيد المراجعة من المالك\n"
                f"رقم الطلب: `{existing['id']}`\n"
                f"تاريخ الطلب: {existing['created_at']}"
            )
            st.info("💡 سيتم إعلامك عند الموافقة. يمكنك أيضاً التواصل مباشرة مع المشرف")
        elif status == "rejected":
            reason = existing.get("rejection_reason") or "غير محدد"
            st.error(f"❌ تم رفض طلبك\nالسبب: {reason}")
            if pdf_bytes and st.button(
                "🔄 إعادة طلب الموافقة",
                use_container_width=True,
                key=f"pdf_req_retry_{key_suffix}",
            ):
                rid = create_pdf_request(resolved_user, user_role, pdf_bytes, clean_title, doc_context)
                if rid.startswith("REQ_"):
                    st.success(f"✅ تم إرسال طلب جديد: {rid}")
                    st.rerun()
                else:
                    st.error(f"❌ فشل إرسال الطلب: {rid}")
    else:
        st.info("🔒 تحميل PDF يتطلب موافقة المالك\nاضغط على الزر لطلب الموافقة")
        if pdf_bytes and st.button(
            "📤 طلب موافقة على تحميل PDF",
            type="primary",
            use_container_width=True,
            key=f"pdf_req_new_{key_suffix}",
        ):
            rid = create_pdf_request(resolved_user, user_role, pdf_bytes, clean_title, doc_context)
            if rid.startswith("REQ_"):
                st.success(f"✅ تم إرسال الطلب: {rid}\nسيتم المراجعة قريباً")
                st.rerun()
            else:
                st.error(f"❌ فشل الطلب: {rid}")

    st.markdown("---")
    render_consultation_buttons(key_suffix)


def render_pdf_requests_admin():
    """إدارة طلبات الموافقة — للمالك فقط"""
    st.markdown('<div class="section-title">📋 إدارة طلبات PDF</div>', unsafe_allow_html=True)

    data = _load_pdf_requests()
    requests = data.get("requests", [])

    pending = [r for r in requests if r.get("status") == "pending"]
    approved = [r for r in requests if r.get("status") == "approved"]
    rejected = [r for r in requests if r.get("status") == "rejected"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 الإجمالي", len(requests))
    c2.metric("⏳ قيد المراجعة", len(pending))
    c3.metric("✅ موافق عليها", len(approved))
    c4.metric("❌ مرفوضة", len(rejected))

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(
        [
            f"⏳ قيد المراجعة ({len(pending)})",
            f"✅ موافق عليها ({len(approved)})",
            f"❌ مرفوضة ({len(rejected)})",
        ]
    )

    with tab1:
        if not pending:
            st.info("💡 لا توجد طلبات معلقة")
        else:
            for req in reversed(pending):
                req_id = req["id"]
                with st.expander(
                    f"📄 {req['doc_title']} — {req['user_name']} "
                    f"({req['user_role']}) — {req['created_at']}"
                ):
                    st.markdown(f"**رقم الطلب:** `{req_id}`")
                    st.markdown(f"**المستخدم:** {req['user_name']}")
                    st.markdown(f"**الدور:** {req['user_role']}")
                    st.markdown(f"**المستند:** {req['doc_title']}")
                    st.markdown(f"**التاريخ:** {req['created_at']}")
                    if isinstance(req.get("doc_context"), dict) and req["doc_context"]:
                        st.markdown("**تفاصيل:**")
                        for k, v in req["doc_context"].items():
                            st.markdown(f"- {_safe_sanitize(k, 50)}: {_safe_sanitize(v, 100)}")

                    pdf_preview = _read_pdf_bytes(req_id)
                    if pdf_preview:
                        st.download_button(
                            "👁️ معاينة PDF",
                            pdf_preview,
                            file_name=f"{req_id}_preview.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"preview_{req_id}",
                        )
                    else:
                        st.caption("⚠️ ملف المعاينة غير موجود على القرص")

                    ac1, ac2 = st.columns(2)
                    with ac1:
                        if st.button("✅ موافقة", type="primary", use_container_width=True, key=f"approve_{req_id}"):
                            if approve_pdf_request(req_id):
                                st.success("✅ تمت الموافقة")
                                st.rerun()
                    with ac2:
                        if st.button("❌ رفض", use_container_width=True, key=f"reject_{req_id}"):
                            st.session_state[f"show_reject_{req_id}"] = True

                    if st.session_state.get(f"show_reject_{req_id}"):
                        reason = st.text_input("سبب الرفض:", key=f"reject_reason_{req_id}")
                        if st.button("تأكيد الرفض", key=f"confirm_reject_{req_id}"):
                            if reject_pdf_request(req_id, reason):
                                st.session_state[f"show_reject_{req_id}"] = False
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
# ✅ v11.11.0 — الفيديو التعريفي
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
            st.warning(f"⚠️ تعذر تشغيل الفيديو: {e}")
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


# ═══ الصور ═══
ANIMAL_IMAGES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600",
}


@st.cache_data(ttl=3600)
def _load_first_existing_b64(paths_tuple) -> Optional[str]:
    for p in paths_tuple:
        if p and os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception:
                pass
    return None


def get_img_b64(paths) -> Optional[str]:
    if not paths:
        return None
    return _load_first_existing_b64(tuple(paths))


def get_owner_photo() -> Optional[str]:
    return _load_first_existing_b64(("owner.jpg", "owner.png", "14686.jpg"))


img_base64 = get_img_b64(_get_global("PHOTO_OPTIONS", ()))
owner_b64 = get_owner_photo()


# ═══════════════════════════════════════════════════════════════════════
# مربط الخيول + الحظائر
# ═══════════════════════════════════════════════════════════════════════

HORSE_STALL_SCIENCE = {
    "box_standard": {
        "width": 3.5,
        "length": 3.5,
        "area": 12.25,
        "name_ar": "مربط صندوقي قياسي",
        "usage": "حصان 500-600 كجم",
    },
    "box_large": {
        "width": 4.0,
        "length": 4.0,
        "area": 16.0,
        "name_ar": "مربط كبير",
        "usage": "حصان >600",
    },
    "box_foaling": {
        "width": 4.0,
        "length": 5.0,
        "area": 20.0,
        "name_ar": "مربط ولادة",
        "usage": "فرس حامل",
    },
    "box_pony": {
        "width": 3.0,
        "length": 3.0,
        "area": 9.0,
        "name_ar": "مربط بوني",
        "usage": "بوني",
    },
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


def calculate_horse_barn_scientific(
    num_horses: int, stall_type: str = "box_standard", include_service: bool = True
) -> Dict:
    num_horses = max(1, int(num_horses or 1))
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
    service_area = (
        (sci["service_room_m2"] + sci["tack_room_m2"] + sci["wash_bay_m2"] + sci["hay_storage_m2"])
        if include_service
        else 0.0
    )
    total_area = building_width * building_length + service_area
    building_volume = building_width * building_length * sci["ceiling_height_m"]

    vent_summer = building_volume * sci["ach_summer"]
    vent_winter = building_volume * sci["ach_winter"]
    vent_summer_cfm = vent_summer * 35.3147 / 60.0
    vent_winter_cfm = vent_winter * 35.3147 / 60.0
    tunnel_fans = max(1, int(np.ceil(vent_summer_cfm / 20000.0)))
    side_fans = max(1, int(np.ceil(vent_winter_cfm / 8000.0)))

    wall_area = 2 * building_length * sci["wall_height_m"] + 2 * building_width * sci["wall_height_m"]
    window_area = wall_area * sci["window_area_pct"]
    light_fixtures = max(1, int(np.ceil(total_area / 80.0)))
    water_day = num_horses * 45

    cost_structure = building_width * building_length * 90
    cost_roof = building_width * building_length * 35
    cost_stalls = num_horses * stall["area"] * 180
    cost_aisle_floor = aisle_area * 45
    cost_service = service_area * 40
    cost_ventilation = tunnel_fans * 500 + side_fans * 300
    cost_lighting = light_fixtures * 60
    cost_windows = window_area * 120
    cost_total = round(
        cost_structure
        + cost_roof
        + cost_stalls
        + cost_aisle_floor
        + cost_service
        + cost_ventilation
        + cost_lighting
        + cost_windows,
        0,
    )

    return {
        "is_horse_barn": True,
        "num_horses": num_horses,
        "stall_type": stall_type,
        "stall_type_ar": stall["name_ar"],
        "stall_width_m": stall["width"],
        "stall_length_m": stall["length"],
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
        "tunnel_fans_hp_total": tunnel_fans * 2.0,
        "side_fans_hp_total": side_fans * 1.0,
        "door_dimensions": f"{sci['door_width_m']}×{sci['door_height_m']} م",
        "doors_count": num_horses,
        "window_area_m2": round(window_area, 2),
        "bedding_cm": sci["bedding_cm"],
        "bedding_m3": round(stall_area_total * sci["bedding_cm"] / 100.0, 1),
        "water_per_day_L": water_day,
        "light_fixtures": light_fixtures,
        "lighting_lux": 200,
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
        "slope_pct": 25.0,
        "feeders_count": num_horses * 2,
        "drinkers_count": num_horses,
        "feeder_type": "معلف",
        "drinker_type": "حوض",
        "total_feeder_length_m": round(num_horses * 1.2, 1),
        "total_drinker_length_m": round(num_horses * 0.6, 1),
        "cooling_pad_enabled": False,
        "cooling_pad_area_m2": 0,
        "structure_type": "هيكل خشبي/معدني",
        "steel_weight_kg": round(building_width * building_length * 30.0, 0),
        "roof_material": "صاج + عزل",
        "wall_material": "خشب + شبك",
        "floor_material": "خرسانة + نشارة",
        "insulation_area_m2": round((building_width * building_length) + wall_area * 0.6, 2),
        "insulation_thickness_mm": 30,
        "barn_key": "خيول_مربط",
        "vent_flow_summer_m3h": int(vent_summer),
        "vent_flow_winter_m3h": int(vent_winter),
        "vent_flow_summer_cfm": int(vent_summer_cfm),
        "vent_flow_winter_cfm": int(vent_winter_cfm),
        "vent_open_area_m2": round(window_area, 2),
        "ventilation_type": "نفق",
        "tunnel_fan_spec": "120 سم — 20000 CFM",
        "side_fan_spec": "90 سم — 8000 CFM",
        "roof_area_m2": round(building_width * building_length * 1.15, 2),
        "wall_area_m2": round(wall_area, 2),
        "light_hours": 14,
        "light_watts_total": light_fixtures * 60,
        "water_per_head_L": 45,
        "aisle_m": aisle_w,
        "central_aisle": True,
    }


BARN_DESIGN_STANDARDS = {
    "دواجن_لاحم": {
        "name_ar": "دواجن لاحم",
        "area_per_head": 0.10,
        "feeder_cm_per_head": 5.0,
        "drinker_cm_per_head": 2.5,
        "height_m": 2.8,
        "width_m": 12.0,
        "ach_summer": 60,
        "ach_winter": 8,
        "vent_open_ratio": 0.20,
        "roof_type": "gable",
        "slope_pct": 20.0,
        "feeder_type": "خطية",
        "drinker_type": "حلمات",
        "aisle_m": 1.2,
        "central_aisle": True,
        "structure_type": "هيكل معدني",
        "roof_material": "ساندوتش",
        "wall_material": "ستائر",
        "floor_material": "خرسانة",
        "insulation_thickness_cm": 5.0,
        "ventilation_type": "نفق",
        "tunnel_fan_cfm": 12000,
        "tunnel_fan_hp": 1.5,
        "tunnel_fan_diameter_cm": 90,
        "side_fan_cfm": 5000,
        "side_fan_hp": 0.75,
        "cooling_pad_enabled": True,
        "cooling_pad_m2_per_1000cfm": 0.5,
        "lighting_lux": 30,
        "light_hours": 18,
        "water_per_head_L": 0.25,
    },
    "أبقار": {
        "name_ar": "أبقار",
        "area_per_head": 5.0,
        "feeder_cm_per_head": 70.0,
        "drinker_cm_per_head": 6.0,
        "height_m": 4.5,
        "width_m": 15.0,
        "ach_summer": 25,
        "ach_winter": 4,
        "vent_open_ratio": 0.35,
        "roof_type": "gable",
        "slope_pct": 20.0,
        "feeder_type": "وسطية",
        "drinker_type": "حوض",
        "aisle_m": 3.5,
        "central_aisle": True,
        "structure_type": "هيكل معدني ثقيل",
        "roof_material": "صاج",
        "wall_material": "شبك",
        "floor_material": "خرسانة",
        "insulation_thickness_cm": 3.0,
        "ventilation_type": "تقطيعي",
        "tunnel_fan_cfm": 20000,
        "tunnel_fan_hp": 2.0,
        "tunnel_fan_diameter_cm": 120,
        "side_fan_cfm": 8000,
        "side_fan_hp": 1.0,
        "cooling_pad_enabled": False,
        "cooling_pad_m2_per_1000cfm": 0.4,
        "lighting_lux": 200,
        "light_hours": 16,
        "water_per_head_L": 80,
    },
    "أغنام": {
        "name_ar": "أغنام",
        "area_per_head": 1.5,
        "feeder_cm_per_head": 35.0,
        "drinker_cm_per_head": 4.0,
        "height_m": 3.5,
        "width_m": 10.0,
        "ach_summer": 30,
        "ach_winter": 5,
        "vent_open_ratio": 0.30,
        "roof_type": "gable",
        "slope_pct": 25.0,
        "feeder_type": "خرسانية",
        "drinker_type": "حوض",
        "aisle_m": 2.0,
        "central_aisle": True,
        "structure_type": "هيكل معدني",
        "roof_material": "صاج",
        "wall_material": "شبك",
        "floor_material": "خرسانة",
        "insulation_thickness_cm": 2.5,
        "ventilation_type": "طبيعي",
        "tunnel_fan_cfm": 14000,
        "tunnel_fan_hp": 1.5,
        "tunnel_fan_diameter_cm": 90,
        "side_fan_cfm": 6000,
        "side_fan_hp": 1.0,
        "cooling_pad_enabled": False,
        "cooling_pad_m2_per_1000cfm": 0.3,
        "lighting_lux": 100,
        "light_hours": 14,
        "water_per_head_L": 6,
    },
    "إبل": {
        "name_ar": "إبل",
        "area_per_head": 10.0,
        "feeder_cm_per_head": 100.0,
        "drinker_cm_per_head": 8.0,
        "height_m": 4.5,
        "width_m": 15.0,
        "ach_summer": 20,
        "ach_winter": 4,
        "vent_open_ratio": 0.40,
        "roof_type": "gable",
        "slope_pct": 20.0,
        "feeder_type": "مرتفعة",
        "drinker_type": "حوض كبير",
        "aisle_m": 4.0,
        "central_aisle": True,
        "structure_type": "هيكل ثقيل",
        "roof_material": "صاج",
        "wall_material": "شبك",
        "floor_material": "رمل",
        "insulation_thickness_cm": 3.0,
        "ventilation_type": "طبيعي",
        "tunnel_fan_cfm": 20000,
        "tunnel_fan_hp": 2.0,
        "tunnel_fan_diameter_cm": 120,
        "side_fan_cfm": 8000,
        "side_fan_hp": 1.0,
        "cooling_pad_enabled": True,
        "cooling_pad_m2_per_1000cfm": 0.4,
        "lighting_lux": 100,
        "light_hours": 12,
        "water_per_head_L": 50,
    },
    "سمان": {
        "name_ar": "سمان",
        "area_per_head": 0.025,
        "feeder_cm_per_head": 2.0,
        "drinker_cm_per_head": 1.0,
        "height_m": 2.0,
        "width_m": 6.0,
        "ach_summer": 50,
        "ach_winter": 8,
        "vent_open_ratio": 0.25,
        "roof_type": "mono",
        "slope_pct": 15.0,
        "feeder_type": "خطية",
        "drinker_type": "حلمات",
        "aisle_m": 0.8,
        "central_aisle": False,
        "structure_type": "خفيف",
        "roof_material": "ساندوبانل",
        "wall_material": "شبك",
        "floor_material": "بطاريات",
        "insulation_thickness_cm": 4.0,
        "ventilation_type": "نفق",
        "tunnel_fan_cfm": 10000,
        "tunnel_fan_hp": 1.0,
        "tunnel_fan_diameter_cm": 60,
        "side_fan_cfm": 4000,
        "side_fan_hp": 0.75,
        "cooling_pad_enabled": True,
        "cooling_pad_m2_per_1000cfm": 0.5,
        "lighting_lux": 20,
        "light_hours": 16,
        "water_per_head_L": 0.06,
    },
    "أرانب": {
        "name_ar": "أرانب",
        "area_per_head": 0.30,
        "feeder_cm_per_head": 8.0,
        "drinker_cm_per_head": 2.0,
        "height_m": 2.5,
        "width_m": 8.0,
        "ach_summer": 40,
        "ach_winter": 6,
        "vent_open_ratio": 0.25,
        "roof_type": "gable",
        "slope_pct": 20.0,
        "feeder_type": "معدنية",
        "drinker_type": "نبل",
        "aisle_m": 1.2,
        "central_aisle": True,
        "structure_type": "خفيف",
        "roof_material": "ساندوتش",
        "wall_material": "شبك",
        "floor_material": "بطاريات",
        "insulation_thickness_cm": 3.0,
        "ventilation_type": "نفق",
        "tunnel_fan_cfm": 8000,
        "tunnel_fan_hp": 0.75,
        "tunnel_fan_diameter_cm": 60,
        "side_fan_cfm": 3000,
        "side_fan_hp": 0.5,
        "cooling_pad_enabled": True,
        "cooling_pad_m2_per_1000cfm": 0.4,
        "lighting_lux": 30,
        "light_hours": 16,
        "water_per_head_L": 0.35,
    },
}


def calculate_barn_dimensions(key: str, count: int, barn_system: str = "أرضي مفتوح") -> Optional[Dict]:
    std = BARN_DESIGN_STANDARDS.get(key)
    if not std:
        return None
    count = max(1, int(count or 1))
    area = count * std["area_per_head"]
    width = max(float(std["width_m"]), 1.0)
    length = max(area / width, 6.0)
    height = max(float(std["height_m"]), 1.0)
    volume = length * width * height
    roof_rise = (width / 2.0) * (float(std["slope_pct"]) / 100.0)
    ridge = height + roof_rise
    roof_area = length * width * 1.15
    wall_area = 2 * length * height + 2 * width * height
    floor_area = length * width

    feeders = max(1, int(np.ceil(count * std["feeder_cm_per_head"] / 300.0)))
    drinkers = max(1, int(np.ceil(count * std["drinker_cm_per_head"] / 200.0)))

    vent_summer = volume * std["ach_summer"]
    vent_winter = volume * std["ach_winter"]
    vent_summer_cfm = vent_summer * 35.3147 / 60.0
    vent_winter_cfm = vent_winter * 35.3147 / 60.0
    tunnel_fans = max(1, int(np.ceil(vent_summer_cfm / max(float(std["tunnel_fan_cfm"]), 1.0))))
    side_fans = max(1, int(np.ceil(vent_winter_cfm / max(float(std["side_fan_cfm"]), 1.0))))

    cooling_pad = 0.0
    if std.get("cooling_pad_enabled", False):
        cooling_pad = round(vent_summer_cfm * std["cooling_pad_m2_per_1000cfm"] / 1000.0, 2)

    light_fixtures = max(1, int(np.ceil(floor_area / 100.0)))
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
    cost_total = round(
        cost_structure
        + cost_roof
        + cost_walls
        + cost_floor
        + cost_fans
        + cost_cooling
        + cost_lighting
        + cost_feeders
        + cost_drinkers,
        0,
    )

    return {
        "standard": std,
        "barn_system": barn_system,
        "count": count,
        "total_area_m2": round(area, 2),
        "length_m": round(length, 2),
        "width_m": round(width, 2),
        "height_m": round(height, 2),
        "ridge_height_m": round(ridge, 2),
        "volume_m3": round(volume, 1),
        "roof_type": std["roof_type"],
        "slope_pct": std["slope_pct"],
        "roof_area_m2": round(roof_area, 2),
        "wall_area_m2": round(wall_area, 2),
        "feeders_count": feeders,
        "drinkers_count": drinkers,
        "total_feeder_length_m": round(count * std["feeder_cm_per_head"] / 100.0, 1),
        "total_drinker_length_m": round(count * std["drinker_cm_per_head"] / 100.0, 1),
        "feeder_type": std.get("feeder_type", "خطية"),
        "drinker_type": std.get("drinker_type", "حوض"),
        "vent_flow_summer_m3h": int(vent_summer),
        "vent_flow_winter_m3h": int(vent_winter),
        "vent_flow_summer_cfm": int(vent_summer_cfm),
        "vent_flow_winter_cfm": int(vent_winter_cfm),
        "vent_open_area_m2": round(length * height * std["vent_open_ratio"], 2),
        "ventilation_type": std.get("ventilation_type", "نفق"),
        "tunnel_fans_count": tunnel_fans,
        "tunnel_fan_spec": f"{std['tunnel_fan_diameter_cm']}\"{' — '}{std['tunnel_fan_cfm']} CFM",
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
        "temp_optimal": 20,
        "barn_key": key,
    }


def create_barn_3d_figure(dims: Dict):
    """3D مع إسطبلات خيول محسّنة"""
    if not PLOTLY_AVAILABLE or not isinstance(dims, dict):
        return None
    try:
        std = dims.get("standard") or {"name_ar": "حظيرة"}
        L = max(float(dims.get("length_m", 10.0) or 10.0), 1.0)
        W = max(float(dims.get("width_m", 8.0) or 8.0), 1.0)
        H = max(float(dims.get("height_m", 3.0) or 3.0), 1.0)
        RH = max(float(dims.get("ridge_height_m", H + 1.0) or H + 1.0), H)
        max_dim = max(L, W, RH)
        ax_x, ax_y, ax_z = L / max_dim, W / max_dim, max(RH / max_dim, 0.15)

        fig = go.Figure()

        # الأرضية
        fig.add_trace(
            go.Mesh3d(
                x=[0, L, L, 0],
                y=[0, 0, W, W],
                z=[0, 0, 0, 0],
                i=[0, 0],
                j=[1, 2],
                k=[2, 3],
                color="#d7ccc8",
                opacity=0.7,
                name="الأرضية",
                hoverinfo="skip",
            )
        )

        # الجدران
        for xp in [0, L]:
            fig.add_trace(
                go.Mesh3d(
                    x=[xp] * 4,
                    y=[0, W, W, 0],
                    z=[0, 0, H, H],
                    i=[0, 0],
                    j=[1, 2],
                    k=[2, 3],
                    color="#a1887f",
                    opacity=0.3,
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
        for yp in [0, W]:
            fig.add_trace(
                go.Mesh3d(
                    x=[0, L, L, 0],
                    y=[yp] * 4,
                    z=[0, 0, H, H],
                    i=[0, 0],
                    j=[1, 2],
                    k=[2, 3],
                    color="#a1887f",
                    opacity=0.3,
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

        # السقف
        if dims.get("roof_type") == "gable":
            fig.add_trace(
                go.Mesh3d(
                    x=[0, L, L, 0],
                    y=[0, 0, W / 2, W / 2],
                    z=[H, H, RH, RH],
                    i=[0, 0],
                    j=[1, 2],
                    k=[2, 3],
                    color="#8d6e63",
                    opacity=0.55,
                    name="السقف",
                    hoverinfo="skip",
                )
            )
            fig.add_trace(
                go.Mesh3d(
                    x=[0, L, L, 0],
                    y=[W / 2, W / 2, W, W],
                    z=[RH, RH, H, H],
                    i=[0, 0],
                    j=[1, 2],
                    k=[2, 3],
                    color="#8d6e63",
                    opacity=0.55,
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

        # المراوح
        fan_count = int(dims.get("tunnel_fans_count", 0) or 0)
        for i in range(min(fan_count, 20)):
            xc = L - 0.05
            yc = (i + 0.5) * (W / max(fan_count, 1))
            fig.add_trace(
                go.Scatter3d(
                    x=[xc],
                    y=[yc],
                    z=[H * 0.5],
                    mode="markers+text",
                    marker=dict(size=15, color="#1976d2", symbol="circle"),
                    text=[f"م{i+1}"],
                    textposition="middle center",
                    textfont=dict(size=8, color="white"),
                    name="مروحة" if i == 0 else None,
                    showlegend=(i == 0),
                )
            )

        side_count = int(dims.get("side_fans_count", 0) or 0)
        for i in range(min(side_count, 20)):
            xc = (i + 0.5) * (L / max(side_count, 1))
            fig.add_trace(
                go.Scatter3d(
                    x=[xc],
                    y=[0.1],
                    z=[H * 0.7],
                    mode="markers",
                    marker=dict(size=10, color="#00897b", symbol="diamond"),
                    name="مروحة جانبية" if i == 0 else None,
                    showlegend=(i == 0),
                )
            )

        # المعالف
        aisle = float(dims.get("aisle_m", 1.5) or 1.5)
        fw = 0.6
        if dims.get("central_aisle", True) and W > 8:
            fpos = [W / 2 - aisle / 2 - fw, W / 2 + aisle / 2]
        else:
            fpos = [0.8, W - 1.4]
        for idx, yp in enumerate(fpos):
            if yp < 0 or yp + fw > W or L <= 1.0:
                continue
            xv = [0.5, L - 0.5, L - 0.5, 0.5, 0.5, L - 0.5, L - 0.5, 0.5]
            yv = [yp, yp, yp + fw, yp + fw, yp, yp, yp + fw, yp + fw]
            zv = [0, 0, 0, 0, 0.35, 0.35, 0.35, 0.35]
            ii = [0, 0, 4, 4, 0, 0, 3, 3, 0, 0, 1, 1]
            ji = [1, 2, 6, 7, 4, 5, 2, 6, 3, 7, 5, 6]
            ki = [2, 3, 5, 6, 5, 1, 6, 7, 7, 4, 6, 2]
            fig.add_trace(
                go.Mesh3d(
                    x=xv,
                    y=yv,
                    z=zv,
                    i=ii,
                    j=ji,
                    k=ki,
                    color="#ff8f00",
                    opacity=0.9,
                    name="معلف" if idx == 0 else None,
                    showlegend=(idx == 0),
                    hoverinfo="skip",
                )
            )

        # السقايات
        nd = int(dims.get("drinkers_count", 0) or 0)
        for i in range(min(nd, 20)):
            xc = (i + 0.5) * (L / max(nd, 1))
            yc = W - aisle - 0.5 if dims.get("central_aisle", True) else W - 1.5
            fig.add_trace(
                go.Scatter3d(
                    x=[xc],
                    y=[min(max(yc, 0.2), W - 0.2)],
                    z=[0.4],
                    mode="markers+text",
                    marker=dict(size=10, color="#1976d2", symbol="diamond"),
                    text=[f"م{i+1}"],
                    textposition="top center",
                    textfont=dict(size=8, color="#0d47a1"),
                    name="سقاية" if i == 0 else None,
                    showlegend=(i == 0),
                )
            )

        count = int(dims.get("count", dims.get("num_horses", 100)) or 100)

        # الحيوانات (عام)
        if not dims.get("is_horse_barn"):
            apr = min(20, max(1, int(np.sqrt(count))))
            ax_, ay_, az_ = [], [], []
            for ri in range(apr):
                for ci in range(apr):
                    if len(ax_) > 200:
                        break
                    xp = 0.8 + ci * max(L - 1.6, 0.5) / apr
                    yp = 1.0 + ri * max(W - 2.0, 0.5) / apr
                    ax_.append(xp)
                    ay_.append(yp)
                    az_.append(0.15)
            if ax_:
                fig.add_trace(
                    go.Scatter3d(
                        x=ax_,
                        y=ay_,
                        z=az_,
                        mode="markers",
                        marker=dict(size=2.5, color="#1b5e20", opacity=0.7),
                        name=f"حيوانات ({count})",
                    )
                )

        # ✅ إسطبلات الخيول المحسّنة
        if dims.get("is_horse_barn"):
            rows = max(1, int(dims.get("rows_count", 2) or 2))
            per_row = max(1, int(dims.get("stalls_per_row", 5) or 5))
            stall_w = float(dims.get("stall_width_m", 3.5) or 3.5)
            stall_l = float(dims.get("stall_length_m", 3.5) or 3.5)
            wall_h = H * 0.75

            for row in range(rows):
                y_offset = 0.5 if row == 0 else max(0.5, W - stall_l - 0.5)
                for col in range(per_row):
                    x_offset = 0.5 + col * stall_w
                    stall_num = col + 1 + row * per_row
                    y_front = y_offset if row == 0 else y_offset + stall_l

                    # يسار الجدار الأمامي
                    fig.add_trace(
                        go.Mesh3d(
                            x=[x_offset, x_offset + 0.5, x_offset + 0.5, x_offset],
                            y=[y_front] * 4,
                            z=[0, 0, wall_h, wall_h],
                            i=[0, 0],
                            j=[1, 2],
                            k=[2, 3],
                            color="#8d6e63",
                            opacity=0.6,
                            showlegend=False,
                            hoverinfo="skip",
                        )
                    )
                    # يمين الجدار الأمامي
                    fig.add_trace(
                        go.Mesh3d(
                            x=[
                                x_offset + stall_w - 0.5,
                                x_offset + stall_w,
                                x_offset + stall_w,
                                x_offset + stall_w - 0.5,
                            ],
                            y=[y_front] * 4,
                            z=[0, 0, wall_h, wall_h],
                            i=[0, 0],
                            j=[1, 2],
                            k=[2, 3],
                            color="#8d6e63",
                            opacity=0.6,
                            showlegend=False,
                            hoverinfo="skip",
                        )
                    )
                    # الجزء العلوي
                    fig.add_trace(
                        go.Mesh3d(
                            x=[x_offset, x_offset + stall_w, x_offset + stall_w, x_offset],
                            y=[y_front] * 4,
                            z=[H * 0.6, H * 0.6, wall_h, wall_h],
                            i=[0, 0],
                            j=[1, 2],
                            k=[2, 3],
                            color="#8d6e63",
                            opacity=0.5,
                            showlegend=False,
                            hoverinfo="skip",
                        )
                    )
                    # الجدار الجانبي
                    x_right = x_offset + stall_w
                    fig.add_trace(
                        go.Mesh3d(
                            x=[x_right] * 4,
                            y=[y_offset, y_offset + stall_l, y_offset + stall_l, y_offset],
                            z=[0, 0, wall_h, wall_h],
                            i=[0, 0],
                            j=[1, 2],
                            k=[2, 3],
                            color="#6d4c41",
                            opacity=0.55,
                            showlegend=False,
                            hoverinfo="skip",
                        )
                    )
                    # الجدار الخلفي
                    y_back = y_offset + stall_l if row == 0 else y_offset
                    fig.add_trace(
                        go.Mesh3d(
                            x=[x_offset, x_offset + stall_w, x_offset + stall_w, x_offset],
                            y=[y_back] * 4,
                            z=[0, 0, wall_h, wall_h],
                            i=[0, 0],
                            j=[1, 2],
                            k=[2, 3],
                            color="#6d4c41",
                            opacity=0.55,
                            showlegend=False,
                            hoverinfo="skip",
                        )
                    )
                    # الأرضية (فرشة)
                    fig.add_trace(
                        go.Mesh3d(
                            x=[x_offset, x_offset + stall_w, x_offset + stall_w, x_offset],
                            y=[y_offset, y_offset, y_offset + stall_l, y_offset + stall_l],
                            z=[0.05, 0.05, 0.05, 0.05],
                            i=[0, 0],
                            j=[1, 2],
                            k=[2, 3],
                            color="#ffd54f",
                            opacity=0.5,
                            showlegend=False,
                            hoverinfo="skip",
                        )
                    )
                    # الحصان (جسم)
                    horse_cx = x_offset + stall_w / 2.0
                    horse_cy = y_offset + stall_l / 2.0
                    fig.add_trace(
                        go.Scatter3d(
                            x=[horse_cx],
                            y=[horse_cy],
                            z=[0.7],
                            mode="markers",
                            marker=dict(
                                size=22,
                                color="#5d4037",
                                symbol="square",
                                line=dict(color="#3e2723", width=2),
                            ),
                            name="حصان" if row == 0 and col == 0 else None,
                            showlegend=(row == 0 and col == 0),
                            hovertemplate=f"حصان {stall_num}<extra></extra>",
                        )
                    )
                    # رأس الحصان
                    fig.add_trace(
                        go.Scatter3d(
                            x=[horse_cx + 0.3],
                            y=[horse_cy],
                            z=[1.0],
                            mode="markers",
                            marker=dict(size=12, color="#4e342e", symbol="circle"),
                            showlegend=False,
                            hoverinfo="skip",
                        )
                    )
                    # المعلف (علف أخضر)
                    feed_x = x_offset + stall_w * 0.3
                    y_feed_1 = y_back - 0.2 if row == 0 else y_back + 0.2
                    y_feed_2 = y_back - 0.5 if row == 0 else y_back + 0.5
                    fig.add_trace(
                        go.Mesh3d(
                            x=[feed_x, feed_x + 0.4, feed_x + 0.4, feed_x],
                            y=[y_feed_1, y_feed_1, y_feed_2, y_feed_2],
                            z=[0, 0, 0.5, 0.5],
                            i=[0, 0],
                            j=[1, 2],
                            k=[2, 3],
                            color="#66bb6a",
                            opacity=0.85,
                            showlegend=False,
                            hoverinfo="skip",
                        )
                    )
                    # دلو الماء
                    water_x = x_offset + stall_w * 0.7
                    fig.add_trace(
                        go.Scatter3d(
                            x=[water_x],
                            y=[y_back - 0.3 if row == 0 else y_back + 0.3],
                            z=[0.3],
                            mode="markers",
                            marker=dict(
                                size=12,
                                color="#1976d2",
                                symbol="circle",
                                line=dict(color="#0d47a1", width=1.5),
                            ),
                            showlegend=False,
                            hoverinfo="skip",
                        )
                    )
                    # رقم الإسطبل
                    fig.add_trace(
                        go.Scatter3d(
                            x=[x_offset + stall_w / 2.0],
                            y=[y_front],
                            z=[wall_h + 0.3],
                            mode="text",
                            text=[f"🐎 {stall_num}"],
                            textfont=dict(size=11, color="#c62828"),
                            showlegend=False,
                        )
                    )

        fig.update_layout(
            title=dict(
                text=f"🏗️ {std.get('name_ar', 'حظيرة')} — {count} | {L:.1f}×{W:.1f}×{RH:.1f} م",
                font=dict(size=13, color="#1b5e20"),
                x=0.5,
            ),
            scene=dict(
                xaxis=dict(title="الطول", range=[-0.5, L + 0.5]),
                yaxis=dict(title="العرض", range=[-0.5, W + 0.5]),
                zaxis=dict(title="الارتفاع", range=[0, RH + 0.5]),
                aspectmode="manual",
                aspectratio=dict(x=ax_x, y=ax_y, z=ax_z),
                camera=dict(eye=dict(x=1.5, y=-1.5, z=0.9)),
            ),
            height=max(600, min(900, 600 + int(count / 100))),
            paper_bgcolor="white",
        )
        return fig
    except Exception:
        return None


def generate_barn_pdf_report(dims: Dict) -> Optional[bytes]:
    if not REPORTLAB_AVAILABLE or not isinstance(dims, dict):
        return None
    try:
        font_name = _get_font_name()
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=115,
            bottomMargin=145,
        )
        story = []

        def P(text, size=11, align=TA_RIGHT, color="#1a1a1a"):
            return Paragraph(
                _safe_ar(text),
                ParagraphStyle(
                    "barn_p",
                    fontName=font_name,
                    fontSize=size,
                    alignment=align,
                    textColor=HexColor(color),
                    spaceAfter=6,
                    leading=size * 1.6,
                ),
            )

        std = dims.get("standard") or {"name_ar": "حظيرة"}
        story.append(P("تقرير الحظيرة", size=20, align=TA_CENTER, color="#1b5e20"))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=2.5, color=HexColor("#d4af37")))
        story.append(Spacer(1, 10))

        if dims.get("is_horse_barn"):
            info = [
                [_safe_ar("النوع"), _safe_ar("مربط خيول علمي")],
                [_safe_ar("عدد الخيول"), _safe_ar(str(dims.get("num_horses", "—")))],
                [_safe_ar("نوع المربط"), _safe_ar(dims.get("stall_type_ar", "—"))],
                [_safe_ar("أبعاد المربط"), _safe_ar(dims.get("stall_dimensions", "—"))],
                [_safe_ar("الصفوف"), _safe_ar(f"{dims.get('rows_count', 1)} صف × {dims.get('stalls_per_row', 1)}")],
                [_safe_ar("المساحة"), _safe_ar(f"{dims.get('total_area_m2', 0)} م²")],
                [_safe_ar("التكلفة التقديرية"), f"${float(dims.get('cost_total_usd', 0.0)):,.0f}"],
                [_safe_ar("المرجع"), _safe_ar(dims.get("reference", "—"))],
            ]
        else:
            info = [
                [_safe_ar("الحيوان"), _safe_ar(std.get("name_ar", "—"))],
                [_safe_ar("العدد"), _safe_ar(str(dims.get("count", "—")))],
                [_safe_ar("المساحة"), _safe_ar(f"{dims.get('total_area_m2', 0)} م²")],
                [_safe_ar("التكلفة التقديرية"), f"${float(dims.get('cost_total_usd', 0.0)):,.0f}"],
            ]

        t = Table(info, colWidths=[160, 330])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), HexColor("#e8f5e9")),
                    ("BOX", (0, 0), (-1, -1), 1.5, HexColor("#2e7d32")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.6, HexColor("#c8e6c9")),
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 12))

        pdf_gen._add_references_page(story, dims.get("barn_key", "أبقار"), "عام")
        doc.build(story, onFirstPage=pdf_gen._draw_page, onLaterPages=pdf_gen._draw_page)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception:
        return None

import time as _time
import traceback
import urllib.parse
from datetime import datetime
from typing import Dict, Optional

import pandas as pd
import streamlit as st


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


# ═══════════════════════════════════════════════════════════════════════
# الجلسة
# ═══════════════════════════════════════════════════════════════════════

_APP_NAME = _g("APP_NAME", "تاور نولجي")
_DUA_SHORT = _g("DUA_SHORT", "اللهم بارك لنا فيما رزقتنا")
_DUA_QURAN = _g("DUA_QURAN", "")
_DUA_VISITOR = _g("DUA_VISITOR", "")
_SUPERVISOR = _g("SUPERVISOR", "د. عبدالقادر إسماعيل")
_SUPERVISOR_TITLE = _g("SUPERVISOR_TITLE", "")
_APP_TAGLINE = _g("APP_TAGLINE", "")
_WHATSAPP_NUMBER = _g("WHATSAPP_NUMBER", "")
_OWNER_EMAIL = _g("OWNER_EMAIL", "")

DEFAULTS = {
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
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

big_feeds_lib = _g("BIG_FEEDS_LIBRARY", {})
if not st.session_state["inventory"] and isinstance(big_feeds_lib, dict):
    for cat in big_feeds_lib.values():
        if isinstance(cat, dict):
            for ing in cat:
                st.session_state["inventory"][ing] = {
                    "quantity": 25.0,
                    "min_threshold": 5.0,
                    "unit": "طن",
                }


def build_whatsapp_link(formula: Dict, animal: str, quality: float, cost: float) -> str:
    formula = formula or {}
    body = f"🌾 *{_APP_NAME}*\n\n"
    body += f"🐾 {animal or '—'}\n⭐ {float(quality or 0.0):.1f}%\n💰 ${float(cost or 0.0):.2f}/طن\n\n"
    for ing, pct in formula.items():
        body += f"• {ing}: {float(pct or 0.0):.2f}%\n"
    body += f"\n📱 {_SUPERVISOR}"
    num = "".join(ch for ch in str(_WHATSAPP_NUMBER or "") if ch.isdigit())
    return f"https://wa.me/{num}?text={urllib.parse.quote(body)}"


def build_email_link(formula: Dict, animal: str, quality: float, cost: float) -> str:
    formula = formula or {}
    body = f"تركيبة {animal or '—'}\nالجودة: {float(quality or 0.0):.1f}%\nالتكلفة: ${float(cost or 0.0):.2f}/طن\n\n"
    for ing, pct in formula.items():
        body += f"  - {ing}: {float(pct or 0.0):.2f}%\n"
    subject = f"تركيبة — {animal or '—'}"
    email_addr = str(_OWNER_EMAIL or "").strip()
    return f"mailto:{email_addr}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"


def render_share_buttons(formula: Dict, animal: str, quality: float, cost: float, key_suffix: str = ""):
    st.markdown("### 📤 مشاركة")
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
            f'text-align:center; font-weight:700;">✉️ بريد</a>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Amiri:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Cairo', 'Amiri', sans-serif;
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    color: #1a1a1a;
}
.main-box {
    background: rgba(255,255,255,0.96);
    padding: 32px;
    border-radius: 22px;
    box-shadow: 0 15px 45px rgba(0,0,0,0.12);
    margin-bottom: 70px;
    border: 1px solid rgba(212,175,55,0.25);
}
.dua-main-box {
    background: linear-gradient(135deg, #0d3011, #1b5e20, #2e7d32);
    padding: 34px 28px;
    border-radius: 22px;
    border: 4px solid #d4af37;
    direction: rtl;
    text-align: center;
    margin: 25px 0;
    color: #ffffff;
}
.dua-main-box h3 { color: #d4af37 !important; font-size: 1.9rem; font-weight: 900; }
.dua-main-box .names {
    display: inline-block;
    background: rgba(212,175,55,0.25);
    font-size: 1.65rem;
    font-weight: 900;
    color: #ffeb3b !important;
    margin: 20px 0;
    padding: 16px 30px;
    border: 2px solid #d4af37;
    border-radius: 16px;
    font-family: 'Amiri', serif !important;
}
.dua-main-box p.quran {
    font-family: 'Amiri', serif !important;
    font-size: 1.2rem;
    color: #d4af37 !important;
    margin-top: 22px;
    padding: 18px 25px;
    background: rgba(0,0,0,0.25);
    border-radius: 12px;
}
.visitor-dua-banner {
    background: linear-gradient(135deg, #fff8e1, #ffe082);
    padding: 20px 28px;
    border-radius: 16px;
    border: 3px solid #d4af37;
    margin: 22px 0;
    direction: rtl;
    text-align: center;
    color: #4e342e !important;
}
.dua-fixed-banner {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: linear-gradient(90deg, #0d3011, #1b5e20, #2e7d32);
    color: #ffeb3b !important;
    padding: 12px 20px;
    z-index: 9998;
    text-align: center;
    border-top: 3px solid #d4af37;
    font-family: 'Amiri', serif !important;
    font-size: 1.05rem;
    font-weight: bold;
}
.section-title {
    color: #1b5e20 !important;
    border-right: 6px solid #2e7d32;
    padding: 12px 18px;
    text-align: right;
    font-size: 1.5rem;
    font-weight: 900;
    margin-top: 30px;
    margin-bottom: 20px;
    background: linear-gradient(to left, rgba(46,125,50,0.15), transparent);
    border-radius: 10px;
}
.formula-item {
    background: linear-gradient(135deg, #ffffff, #e8f5e9);
    padding: 15px 20px;
    border-radius: 10px;
    margin-bottom: 10px;
    font-weight: 700;
    color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    text-align: right;
}
.physio-card {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    padding: 18px 24px;
    border-radius: 14px;
    border-right: 6px solid #1565c0;
    margin-bottom: 20px;
    direction: rtl;
    text-align: right;
    color: #0d47a1;
}
.quality-good-v113 {
    background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
    padding: 24px;
    border-radius: 22px;
    border-right: 8px solid #1b5e20;
    margin: 18px 0;
    direction: rtl;
    text-align: right;
}
.quality-bad-v113 {
    background: linear-gradient(135deg, #ffcdd2, #ef9a9a);
    padding: 24px;
    border-radius: 22px;
    border-right: 8px solid #c62828;
    margin: 18px 0;
    direction: rtl;
    text-align: right;
}
.profile-img-style {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #d4af37;
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
    bottom: 70px;
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


# ═══════════════════════════════════════════════════════════════════════
# صورة المالك (حق الملكية)
# ═══════════════════════════════════════════════════════════════════════

_owner_b64 = _g("owner_b64", None)
_img_base64 = _g("img_base64", None)

if _owner_b64:
    st.markdown(
        f"""
    <div style="position: fixed; bottom: 70px; right: 20px; z-index: 9999; text-align: center;">
        <img src="data:image/jpeg;base64,{_owner_b64}"
             style="width: 80px; height: 80px; border-radius: 50%;
                    border: 3px solid #d4af37; object-fit: cover;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
        <div style="background: rgba(255,255,255,0.95); border-radius: 8px;
                    padding: 2px 8px; margin-top: 5px; font-size: 10px;
                    font-weight: bold; color: #1b5e20;
                    border: 1px solid #d4af37; white-space: nowrap;">
            👨‍🔬 {_SUPERVISOR}
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════
# بوابة الدخول
# ═══════════════════════════════════════════════════════════════════════

_now_check = _time.time()
_last_check = st.session_state.get("last_activity", _now_check)
if st.session_state.get("approved") and (_now_check - _last_check) > 3600:
    st.session_state.clear()
    st.warning("🔒 جلسة منتهية")
    st.rerun()
st.session_state["last_activity"] = _now_check
_call_if_exists("generate_csrf_token")

if not st.session_state.get("approved", False):
    if _call_if_exists("render_welcome_with_video", default=False):
        st.stop()

    st.markdown(
        '<div class="main-box" style="max-width:980px; margin:30px auto; direction:rtl;">',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
    <div class="dua-main-box">
        <h3>🕌 دعاءُ افتتاحِ المنصة</h3>
        <div class="names">🕊️ رحم الله والدي إسماعيل تاور وأختي ابتسام 🕊️</div>
        <p class="quran">{_DUA_QURAN}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='border-top: 2px solid #d4af37; margin: 25px 0;'>", unsafe_allow_html=True)

    col_logo, col_title = st.columns([0.3, 0.7])
    with col_logo:
        if _owner_b64:
            st.markdown(
                f'<img src="data:image/jpeg;base64,{_owner_b64}" class="profile-img-style">',
                unsafe_allow_html=True,
            )
        elif _img_base64:
            st.markdown(
                f'<img src="data:image/jpeg;base64,{_img_base64}" class="profile-img-style">',
                unsafe_allow_html=True,
            )
    with col_title:
        st.markdown(f"<h2 style='color:#2E7D32; text-align:right;'>🌾 {_APP_NAME}</h2>", unsafe_allow_html=True)
        st.markdown(
            f"<p style='color:#1565C0; text-align:right; font-size:1.1rem;'>{_APP_TAGLINE}</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<h4 style='color:#c62828; text-align:right;'>{_SUPERVISOR} — {_SUPERVISOR_TITLE}</h4>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<h3 style='text-align:center; color:#1b5e20; margin-top:20px;'>🔐 اختر بوابتك</h3>",
        unsafe_allow_html=True,
    )
    col_owner, col_spec, col_guest = st.columns(3)

    with col_owner:
        st.markdown(
            """<div style="background:linear-gradient(135deg,#e8f5e9,#c8e6c9);
            padding:16px; border-radius:12px; border:2px solid #2e7d32;
            text-align:center; min-height:140px;">
            <h4 style="color:#1b5e20; margin:0;">👑 المالك</h4>
            <p style="font-size:0.82rem;">إدارة كاملة + موافقة PDF</p></div>""",
            unsafe_allow_html=True,
        )
        oc = st.text_input("كود المالك:", type="password", key="oc_v1111")
        if st.button("👑 دخول", type="primary", use_container_width=True, key="b_owner_v1111"):
            if _call_if_exists("check_owner_code", oc, default=False):
                st.session_state.update({"approved": True, "user_role": "owner"})
                st.rerun()
            else:
                st.error("❌ كود غير صحيح")

    with col_spec:
        st.markdown(
            """<div style="background:linear-gradient(135deg,#e3f2fd,#bbdefb);
            padding:16px; border-radius:12px; border:2px solid #1565c0;
            text-align:center; min-height:140px;">
            <h4 style="color:#0d47a1; margin:0;">🔬 مختص</h4>
            <p style="font-size:0.82rem;">دخول مباشر (PDF بموافقة)</p></div>""",
            unsafe_allow_html=True,
        )
        if st.button("🔬 دخول كمختص", type="primary", use_container_width=True, key="b_spec_v1111"):
            st.session_state.update({"approved": True, "user_role": "specialist"})
            st.rerun()

    with col_guest:
        st.markdown(
            """<div style="background:linear-gradient(135deg,#fff8e1,#ffecb3);
            padding:16px; border-radius:12px; border:2px solid #d4af37;
            text-align:center; min-height:140px;">
            <h4 style="color:#e65100; margin:0;">👥 زائر</h4>
            <p style="font-size:0.82rem;">مجاني (PDF بموافقة)</p></div>""",
            unsafe_allow_html=True,
        )
        if st.button("👥 دخول كزائر", use_container_width=True, key="b_guest_v1111"):
            st.session_state.update({"approved": True, "user_role": "guest"})
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════════════════════
# الواجهة الرئيسية
# ═══════════════════════════════════════════════════════════════════════

st.markdown('<div class="main-box">', unsafe_allow_html=True)

c1, c2 = st.columns([0.7, 0.3])
with c2:
    role_label = {
        "owner": "المالك 👑",
        "specialist": "مختص 🔬",
        "guest": "زائر 👥",
    }.get(st.session_state.get("user_role"), "—")
    st.markdown(
        f"<div style='text-align:left; padding:10px; background:#f5f5f5;"
        f"border-radius:10px;'>الحساب: <b>{role_label}</b></div>",
        unsafe_allow_html=True,
    )
    if st.button("🚪 خروج", use_container_width=True, key="logout_btn_v1111"):
        st.session_state.clear()
        st.rerun()

c3, c4 = st.columns([0.3, 0.7])
with c3:
    if _owner_b64:
        st.markdown(
            f'<img src="data:image/jpeg;base64,{_owner_b64}" class="profile-img-style">',
            unsafe_allow_html=True,
        )
    elif _img_base64:
        st.markdown(
            f'<img src="data:image/jpeg;base64,{_img_base64}" class="profile-img-style">',
            unsafe_allow_html=True,
        )
with c4:
    st.markdown(
        f"<h1 style='color:#0d3011; text-align:right; font-weight:900;'>🌾 {_APP_NAME}</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color:#1565C0; text-align:right; font-size:1.25rem;'>{_APP_TAGLINE}</p>",
        unsafe_allow_html=True,
    )

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


# ═══ 🧪 مختبر التركيبات ═══

def render_lab_tab(role: str = "guest"):
    st.markdown('<div class="section-title">🧪 مختبر التركيبات</div>', unsafe_allow_html=True)
    st.caption("🔬 حلّل أي تركيبة — أدخل النسب فقط من المكتبة الكاملة")

    lib = _g("BIG_FEEDS_LIBRARY", {}) or {}
    col1, col2 = st.columns(2)
    with col1:
        lab_animal = st.selectbox(
            "🐾 الحيوان:",
            ["أبقار", "أغنام", "ماعز", "إبل", "خيول", "دواجن", "سمان", "أسماك", "أرانب"],
            key="lab_animal_v1111",
        )
    with col2:
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
            "🎯 الإنتاج:",
            lab_prod_map.get(lab_animal, ["عام"]),
            key="lab_prod_v1111",
        )

    st.markdown("### 📝 المكونات")
    input_method = st.radio(
        "طريقة الإدخال:",
        ["📊 جدول المكتبة الكاملة", "📋 لصق نص", "💾 من آخر تركيبة"],
        horizontal=True,
        key="lab_method_v1111",
    )

    formula_input: Dict[str, float] = {}

    if input_method == "📊 جدول المكتبة الكاملة":
        st.markdown("#### 📚 المكتبة العلفية الكاملة")
        st.caption("💡 ابحث، ثم اكتب النسبة بجانب المكونات التي تريدها")

        fcol1, fcol2 = st.columns([0.4, 0.6])
        with fcol1:
            cat_filter = st.selectbox("📁 الفئة:", ["الكل"] + list(lib.keys()), key="lab_cat_v1111")
        with fcol2:
            search_q = st.text_input("🔍 بحث:", placeholder="اكتب اسم مكون...", key="lab_search_v1111")

        all_ings_rows = []
        for cat_name, items in lib.items():
            if not isinstance(items, dict):
                continue
            if cat_filter != "الكل" and cat_name != cat_filter:
                continue
            for ing_name, ing_data in items.items():
                if search_q and search_q.lower() not in ing_name.lower():
                    continue
                clean_cat = (
                    cat_name.replace("🌾 ", "")
                    .replace("🌱 ", "")
                    .replace("🚜 ", "")
                    .replace("🧬 ", "")
                    .replace("🌰 ", "")
                    .replace("🧪 ", "")
                    .replace("🔬 ", "")
                    .replace("🪨 ", "")
                    .replace("💊 ", "")
                )
                all_ings_rows.append(
                    {
                        "المكوّن": ing_name,
                        "الفئة": clean_cat,
                        "CP %": float(ing_data.get("CP", 0) or 0),
                        "SE": float(ing_data.get("SE", 0) or 0),
                        "السعر": float(ing_data.get("price", 300) or 300),
                        "✅ النسبة % (أدخل)": float(st.session_state["lab_full_proportions"].get(ing_name, 0.0)),
                    }
                )

        if not all_ings_rows:
            st.warning("⚠️ لا توجد مكونات مطابقة")
        else:
            st.caption(f"📊 {len(all_ings_rows)} مكوّن متاح")
            df_full = pd.DataFrame(all_ings_rows)

            edited = st.data_editor(
                df_full,
                use_container_width=True,
                hide_index=True,
                height=550,
                column_config={
                    "المكوّن": st.column_config.TextColumn(disabled=True, width="medium"),
                    "الفئة": st.column_config.TextColumn(disabled=True, width="small"),
                    "CP %": st.column_config.NumberColumn(disabled=True, width="small", format="%.1f"),
                    "SE": st.column_config.NumberColumn(disabled=True, width="small", format="%.0f"),
                    "السعر": st.column_config.NumberColumn(disabled=True, width="small", format="$%.0f"),
                    "✅ النسبة % (أدخل)": st.column_config.NumberColumn(
                        min_value=0.0, max_value=100.0, step=0.5, format="%.2f%%", width="small"
                    ),
                },
                key="lab_full_table_v1111",
            )

            new_props: Dict[str, float] = {}
            for _, r in edited.iterrows():
                pct = float(r["✅ النسبة % (أدخل)"] or 0.0)
                if pct > 0:
                    formula_input[r["المكوّن"]] = pct
                    new_props[r["المكوّن"]] = pct
            st.session_state["lab_full_proportions"] = new_props

            if formula_input:
                total = sum(formula_input.values())
                c_s1, c_s2 = st.columns(2)
                c_s1.metric("📊 عدد المكونات", len(formula_input))
                c_s2.metric("📈 المجموع", f"{total:.1f}%")
                if abs(total - 100.0) > 0.5:
                    st.warning(f"⚠️ المجموع = {total:.1f}% — سيتم التطبيع")
                else:
                    st.success(f"✅ المجموع = {total:.1f}%")

            if st.button("🗑️ مسح كل النسب", key="lab_clear_all_v1111"):
                st.session_state["lab_full_proportions"] = {}
                st.rerun()

    elif input_method == "📋 لصق نص":
        st.caption("مثال: `ذرة صفراء 45` أو `كسب فول صويا 44% 25`")
        text_input = st.text_area(
            "الصق:",
            height=200,
            key="lab_text_v1111",
            placeholder="ذرة صفراء 45\nكسب فول صويا 44% 25\nشعير مطحون 20",
        )
        if text_input:
            parsed = _call_if_exists("_parse_ingredients_from_text", text_input, default={}) or {}
            if parsed:
                formula_input = parsed
                st.success(f"✅ {len(parsed)} مكوّن")
                st.dataframe(
                    pd.DataFrame([{"المكوّن": k, "النسبة %": f"{float(v):.2f}"} for k, v in parsed.items()]),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.warning("⚠️ استخدم: `الاسم الرقم`")
    else:
        if st.session_state.get("active_formula"):
            active = st.session_state["active_formula"]
            st.info(f"📋 {len(active)} مكوّن")
            if st.checkbox("استخدمها", value=True, key="lab_use_last_v1111"):
                formula_input = dict(active)

    if formula_input:
        total = sum(float(v or 0.0) for v in formula_input.values())
        if abs(total - 100.0) > 0.5:
            st.warning(f"⚠️ مجموع = {total:.1f}% — سيتم التطبيع")

    if st.button("🔬 تشغيل المختبر", type="primary", use_container_width=True, key="lab_run_v1111"):
        if not formula_input:
            st.error("⚠️ أدخل التركيبة")
        else:
            with st.spinner("🧪 جاري التحليل..."):
                result = _call_if_exists(
                    "analyze_existing_formula",
                    formula_input,
                    lab_animal,
                    lab_prod,
                    default={"success": False, "message": "دالة التحليل غير متاحة"},
                )
            if not result or not result.get("success"):
                st.error(f"❌ {(result or {}).get('message', 'تعذر التحليل')}")
            else:
                st.session_state["lab_result"] = result
                st.session_state["lab_context"] = {"animal": lab_animal, "production": lab_prod}

    if not st.session_state.get("lab_result"):
        return

    result = st.session_state["lab_result"]
    ctx = st.session_state.get("lab_context", {})
    quality = float(result.get("quality_score", 0.0) or 0.0)
    meets = quality >= 70.0

    st.markdown("---")
    if meets:
        st.markdown(
            f"""<div class="quality-good-v113">
            <h3 style="color:#1b5e20; margin:0;">✅ جودة: {quality:.1f}%</h3>
        </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""<div class="quality-bad-v113">
            <h3 style="color:#c62828; margin:0;">⚠️ جودة: {quality:.1f}%</h3>
        </div>""",
            unsafe_allow_html=True,
        )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🎯 الحيوان", ctx.get("animal", "—"))
    m2.metric("🧬 الجودة", f"{quality:.1f}%")
    m3.metric("💰 التكلفة", f"${float(result.get('cost_per_ton', 0.0)):.2f}/طن")
    m4.metric("⚖️ Ca:P", f"{float(result.get('ca_p_ratio', 0.0)):.2f}")

    st.markdown("### ⚡ توازن الطاقة/البروتين")
    bal1, bal2, bal3 = st.columns(3)
    e_share = float(result.get("energy_share_pct", 0.0) or 0.0)
    p_share = float(result.get("protein_share_pct", 0.0) or 0.0)
    bal1.metric("⚡ الطاقة", f"{e_share:.1f}%")
    bal2.metric("🧬 البروتين", f"{p_share:.1f}%")
    bal3.metric("⚠️ الحالة" if p_share > e_share else "✅ الحالة", "بروتين أعلى!" if p_share > e_share else "متوازن")

    st.markdown("### 📋 جدول المقارنة")
    comp_df = pd.DataFrame(
        [
            {
                "العنصر": c.get("العنصر", "—"),
                "المعيار": f"{float(c.get('المعيار', 0.0)):.2f}",
                "المحسوب": f"{float(c.get('المحسوب', 0.0)):.2f}",
                "الفرق": f"{float(c.get('الفرق', 0.0)):+.3f}",
                "الفرق %": f"{float(c.get('الفرق %', 0.0)):+.2f}%",
                "التقييم": c.get("التقييم", "—"),
            }
            for c in (result.get("comparison") or [])
        ]
    )
    if not comp_df.empty:
        st.dataframe(comp_df, use_container_width=True, hide_index=True)

    with st.expander("📐 المعادلات المرجعية", expanded=False):
        eqs = _call_if_exists(
            "get_reference_equations",
            result.get("animal_type", lab_animal),
            result.get("production_type", lab_prod),
            default={},
        )
        if eqs:
            st.markdown(f"**📖 {eqs.get('source', '')}**")
            for k, v in eqs.items():
                if k in ("source", "example"):
                    continue
                st.markdown(f"- **{k}:** `{v}`")
            if eqs.get("example"):
                st.info(f"💡 {eqs['example']}")

    ch1, ch2 = st.columns(2)
    with ch1:
        _render_chart_image(
            _call_if_exists("create_colorful_bar_chart", result.get("standard"), result.get("actual")),
            caption="المقارنة",
        )
    with ch2:
        _render_chart_image(
            _call_if_exists("create_colorful_pie_chart", result.get("formula")),
            caption="التوزيع",
        )

    refs = result.get("references") or {}
    if refs:
        with st.expander("📚 المراجع", expanded=False):
            if refs.get("primary"):
                st.markdown(f"**📖 {refs['primary']}**")
            if refs.get("table"):
                st.markdown(f"**📑 {refs['table']}**")

    try:
        pdf_bytes = _call_if_exists("generate_lab_pdf", result, ctx)
        fname = f"Lab_{ctx.get('animal','Analysis')}_{datetime.now():%Y%m%d}.pdf"
        _call_if_exists(
            "render_pdf_download_with_approval",
            pdf_bytes=pdf_bytes,
            file_name=fname,
            doc_title=f"مختبر — {ctx.get('animal','')} — {ctx.get('production','')}",
            user_role=role,
            user_name=st.session_state.get("chat_username", "مستخدم"),
            doc_context={
                "الحيوان": ctx.get("animal", ""),
                "الإنتاج": ctx.get("production", ""),
                "الجودة": f"{quality:.1f}%",
            },
            key_suffix="lab_v1111",
        )
    except Exception as e:
        st.error(f"⚠️ PDF: {e}")

    render_share_buttons(
        result.get("formula") or {},
        ctx.get("animal", ""),
        quality,
        float(result.get("cost_per_ton", 0.0) or 0.0),
        key_suffix="lab_v1111",
    )


if "🧪 مختبر التركيبات" in tab_map:
    with tab_map["🧪 مختبر التركيبات"]:
        try:
            render_lab_tab(role=role)
        except Exception as e:
            st.error(f"⚠️ {e}")
            with st.expander("التفاصيل"):
                st.code(traceback.format_exc())


# ═══ 🧮 حاسبة الزائر ═══

GUEST_PRODUCTION = {
    "أبقار": {
        "حليب": {"label": "🐄 حلابة", "dp": 12.5, "cp": 17.5, "se": 65, "name": "أبقار حلابة"},
        "تسمين": {"label": "💪 تسمين", "dp": 11.5, "cp": 14.5, "se": 72, "name": "تسمين عجول"},
        "صيانة": {"label": "🌿 صيانة", "dp": 7.5, "cp": 10.0, "se": 53, "name": "أبقار صيانة"},
    },
    "أغنام": {
        "تسمين": {"label": "💪 تسمين", "dp": 10.5, "cp": 14.0, "se": 64, "name": "تسمين حملان"},
        "مرضعات": {"label": "🥛 مرضعات", "dp": 10.5, "cp": 14.5, "se": 62, "name": "نعاج مرضعات"},
        "صيانة": {"label": "🌿 صيانة", "dp": 7.2, "cp": 9.5, "se": 48, "name": "نعاج صيانة"},
    },
    "دواجن": {
        "لاحم_بادي": {"label": "🐔 بادي", "dp": 20.0, "cp": 23.0, "se": 76, "name": "دواجن بادي"},
        "لاحم_ناهي": {"label": "🐔 ناهي", "dp": 17.0, "cp": 19.5, "se": 75, "name": "دواجن ناهي"},
        "بياض": {"label": "🥚 بياض", "dp": 15.5, "cp": 18.0, "se": 72, "name": "دواجن بياض"},
    },
    "أسماك": {
        "بادئ": {"label": "🐟 بادئ", "dp": 32.0, "cp": 40.0, "se": 72, "name": "أسماك بادئ"},
        "نمو": {"label": "🐟 نمو", "dp": 25.0, "cp": 32.0, "se": 70, "name": "أسماك نمو"},
        "تسمين": {"label": "🐟 تسمين", "dp": 22.0, "cp": 28.0, "se": 68, "name": "أسماك تسمين"},
    },
}

if role == "guest" and "🧮 حاسبة مبسطة" in tab_map:
    with tab_map["🧮 حاسبة مبسطة"]:
        try:
            st.markdown('<div class="section-title">🧮 حاسبة سريعة</div>', unsafe_allow_html=True)
            st.caption("💡 تركيبة كاملة + رسوم + مقارنات")

            c1, c2 = st.columns(2)
            with c1:
                g_animal = st.selectbox("🐾 الحيوان:", list(GUEST_PRODUCTION.keys()), key="g_animal_v1111")
                prod_opts = GUEST_PRODUCTION[g_animal]
                g_prod = st.selectbox(
                    "🎯 الغرض:",
                    list(prod_opts.keys()),
                    format_func=lambda x: prod_opts[x]["label"],
                    key="g_prod_v1111",
                )
                g_weight = st.number_input("⚖️ الوزن (كجم):", 1.0, 900.0, 400.0, 5.0, key="g_w_v1111")
            with c2:
                g_count = st.number_input("🔢 العدد:", 1, 100000, 1, 1, key="g_cnt_v1111")
                g_name = st.text_input("👤 اسمك:", placeholder="اتركه فارغاً", key="g_name_v1111")

            if st.button("🧮 احسب", type="primary", use_container_width=True, key="g_calc_v1111"):
                prod_info = prod_opts[g_prod]
                if g_animal in ("أبقار", "أغنام"):
                    rough = {
                        "ذرة صفراء": 40.0,
                        "شعير مطحون": 20.0,
                        "كسب فول صويا 44%": 18.0,
                        "نخالة قمح (ردة)": 15.0,
                        "الحجر الجيري": 1.5,
                        "ملح الطعام": 0.5,
                        "بريمكس مجترات": 0.25,
                        "فوسفات ثنائي الكالسيوم": 0.75,
                    }
                elif g_animal == "دواجن":
                    if "بادي" in g_prod:
                        rough = {
                            "ذرة صفراء": 52.0,
                            "كسب فول صويا 48%": 36.0,
                            "زيت فول الصويا": 4.0,
                            "الحجر الجيري": 1.2,
                            "فوسفات ثنائي الكالسيوم": 1.8,
                            "ملح الطعام": 0.3,
                            "بريمكس تسمين دواجن": 0.3,
                            "ليسين نقي": 0.25,
                            "ميثيونين نقي": 0.15,
                        }
                    elif "بياض" in g_prod:
                        rough = {
                            "ذرة صفراء": 58.0,
                            "كسب فول صويا 44%": 22.0,
                            "نخالة قمح (ردة)": 6.0,
                            "الحجر الجيري": 8.0,
                            "فوسفات ثنائي الكالسيوم": 1.8,
                            "ملح الطعام": 0.3,
                            "بريمكس بياض": 0.3,
                            "ميثيونين نقي": 0.1,
                        }
                    else:
                        rough = {
                            "ذرة صفراء": 55.0,
                            "كسب فول صويا 48%": 32.0,
                            "زيت فول الصويا": 4.0,
                            "الحجر الجيري": 1.2,
                            "فوسفات ثنائي الكالسيوم": 1.8,
                            "ملح الطعام": 0.3,
                            "بريمكس تسمين دواجن": 0.3,
                            "ليسين نقي": 0.2,
                            "ميثيونين نقي": 0.15,
                        }
                else:
                    if "بادئ" in g_prod:
                        rough = {
                            "كسب فول صويا 44%": 30.0,
                            "مسحوق أسماك 60%": 40.0,
                            "قمح محلي": 20.0,
                            "زيت السمك (Fish Oil)": 6.0,
                            "بريمكس أسماك": 0.3,
                            "فوسفات ثنائي الكالسيوم": 2.0,
                        }
                    else:
                        rough = {
                            "كسب فول صويا 44%": 40.0,
                            "مسحوق أسماك 60%": 25.0,
                            "قمح محلي": 25.0,
                            "زيت السمك (Fish Oil)": 5.0,
                            "بريمكس أسماك": 0.3,
                            "فوسفات ثنائي الكالسيوم": 2.0,
                        }

                lookup = _call_if_exists("_get_ingredient_lookup", default={}) or {}
                actual = _call_if_exists("compute_formula_nutrients", rough, default={}) or {}
                std_chart = {"DP": prod_info["dp"], "CP": prod_info["cp"], "SE": prod_info["se"]}
                act_chart = {
                    "DP": float(actual.get("DP", 0.0) or 0.0),
                    "CP": float(actual.get("CP", 0.0) or 0.0),
                    "SE": float(actual.get("SE", 0.0) or 0.0),
                }
                q_res = _call_if_exists("evaluate_quality_weighted", rough, std_chart, g_animal, default=(0.0, {}))
                quality = float(q_res[0] if isinstance(q_res, (tuple, list)) else (q_res or 0.0))
                cost = sum(
                    (float(pct) / 100.0) * float((lookup.get(ing) or {}).get("price", 300.0) or 300.0)
                    for ing, pct in rough.items()
                )

                if quality >= 70.0:
                    st.markdown(
                        f"""<div class="quality-good-v113">
                        <h3 style="color:#1b5e20; margin:0;">✅ جودة: {quality:.1f}%</h3>
                    </div>""",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""<div class="quality-bad-v113">
                        <h3 style="color:#c62828; margin:0;">⚠️ جودة: {quality:.1f}%</h3>
                    </div>""",
                        unsafe_allow_html=True,
                    )

                p_val = float(actual.get("P", 0.0) or 0.0)
                ca_val = float(actual.get("Ca", 0.0) or 0.0)
                ca_p_str = f"{(ca_val / p_val):.2f}" if p_val > 0 else "—"

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("🎯", g_animal)
                m2.metric("🧬", f"{quality:.1f}%")
                m3.metric("💰", f"${cost:.2f}/طن")
                m4.metric("⚖️ Ca:P", ca_p_str)

                st.markdown("### 📊 المقارنة")
                cmp_data = []
                for k, lab, target in [
                    ("DP", "بروتين مهضوم", prod_info["dp"]),
                    ("CP", "بروتين خام", prod_info["cp"]),
                    ("SE", "طاقة SE", prod_info["se"]),
                ]:
                    cv = float(actual.get(k, 0.0) or 0.0)
                    diff = cv - target
                    pct = (diff / target * 100.0) if target else 0.0
                    ev = _call_if_exists("evaluate_difference", pct, standard_value=target, default={"label": "—"}) or {}
                    cmp_data.append(
                        {
                            "العنصر": lab,
                            "المعيار": f"{target:.1f}",
                            "المحسوب": f"{cv:.1f}",
                            "الفرق": f"{diff:+.2f}",
                            "الفرق %": f"{pct:+.1f}%",
                            "التقييم": ev.get("label", "—"),
                        }
                    )
                st.dataframe(pd.DataFrame(cmp_data), use_container_width=True, hide_index=True)

                eqs = _call_if_exists("get_reference_equations", g_animal, g_prod, default={})
                if eqs:
                    with st.expander("📐 المعادلات المرجعية", expanded=False):
                        if eqs.get("source"):
                            st.markdown(f"**📖 {eqs['source']}**")
                        for k, v in eqs.items():
                            if k in ("source", "example"):
                                continue
                            st.markdown(f"- **{k}:** {v}")
                        if eqs.get("example"):
                            st.info(f"💡 {eqs['example']}")

                st.markdown("### 🌾 المكونات")
                for ing, pct in rough.items():
                    st.markdown(
                        f'<div class="formula-item">▪️ <b>{ing}:</b> {float(pct):.1f}%</div>',
                        unsafe_allow_html=True,
                    )

                st.markdown("### 📈 الرسوم البيانية")
                ch1, ch2 = st.columns(2)
                with ch1:
                    _render_chart_image(
                        _call_if_exists("create_colorful_bar_chart", std_chart, act_chart),
                        caption="المقارنة",
                    )
                with ch2:
                    _render_chart_image(
                        _call_if_exists("create_colorful_pie_chart", rough),
                        caption="التوزيع",
                    )

                ch3, ch4 = st.columns(2)
                with ch3:
                    _render_chart_image(
                        _call_if_exists("create_radar_chart", std_chart, act_chart),
                        caption="الرادار",
                    )
                with ch4:
                    _render_chart_image(
                        _call_if_exists("create_gauge_chart", quality),
                        caption="الجودة",
                    )

                if p_val > 0:
                    _render_chart_image(
                        _call_if_exists("create_ca_p_ratio_chart", ca_val, p_val),
                        caption="⚖️ Ca:P",
                    )

                daily = float(g_weight) * 0.025 * int(g_count)
                st.info(f"📊 العلف اليومي: **{daily:.1f} كجم**")

                try:
                    req_cls = _g("AnimalRequirement", None)
                    pdf_generator_obj = _g("pdf_gen", None)
                    if callable(req_cls) and pdf_generator_obj and hasattr(pdf_generator_obj, "generate_report"):
                        guest_req = req_cls(
                            DP=prod_info["dp"],
                            CP=prod_info["cp"],
                            SE=prod_info["se"],
                            NDF=30,
                            ADF=20,
                            EE=4,
                            ASH=8,
                            Ca=0.7,
                            P=0.4,
                            name_ar=prod_info["name"],
                            note="تقرير استرشادي",
                        )
                        pdf_bytes = pdf_generator_obj.generate_report(
                            formula=rough,
                            requirement=guest_req,
                            animal_type=g_animal,
                            breed=prod_info["name"],
                            cost=cost,
                            city="—",
                            local_cost=cost,
                            local_sym="USD",
                            requester_name=g_name.strip() or "زائر",
                            protein_basis="CP",
                            standard_key="",
                            include_charts=True,
                            quality_score=quality,
                        )
                        _call_if_exists(
                            "render_pdf_download_with_approval",
                            pdf_bytes=pdf_bytes,
                            file_name=f"Guest_{g_animal}_{datetime.now():%Y%m%d}.pdf",
                            doc_title=f"زائر — {g_animal} — {prod_info['name']}",
                            user_role=role,
                            user_name=g_name.strip() or st.session_state.get("chat_username", "زائر"),
                            doc_context={
                                "الحيوان": g_animal,
                                "الغرض": prod_info["name"],
                                "الجودة": f"{quality:.1f}%",
                            },
                            key_suffix="guest_v1111",
                        )
                except Exception as e:
                    st.error(f"⚠️ {e}")

                render_share_buttons(rough, g_animal, quality, cost, key_suffix="guest_v1111")
                st.warning("⚠️ استرشادي — للحساب الدقيق استخدم بوابة المختص")
        except Exception as e:
            st.error(f"⚠️ {e}")
            with st.expander("التفاصيل"):
                st.code(traceback.format_exc())


# ═══ 🔬 النمذجة ═══

if "🔬 النمذجة" in tab_map:
    with tab_map["🔬 النمذجة"]:
        try:
            st.markdown('<div class="section-title">🧬 أساس البروتين</div>', unsafe_allow_html=True)
            pb = st.radio(
                "الأساس:",
                ["البروتين المهضوم (DP) — الأدق", "البروتين الخام (CP) — الأسهل"],
                horizontal=True,
                key="protein_basis_v1111",
            )
            basis_code = "DP" if "DP" in pb else "CP"

            st.markdown('<div class="section-title">🐾 اختر الحيوان</div>', unsafe_allow_html=True)
            a_tabs = st.tabs(
                ["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐪 إبل", "🐎 خيول", "🐔 دواجن", "🦆 سمان", "🐟 أسماك", "🐇 أرانب"]
            )

            animal_choice = None
            production_type = None
            requirement = None
            std_key_global = ""

            with a_tabs[0]:
                st.markdown("### 🐄 الأبقار — NRC 2001")
                ct = st.selectbox(
                    "الحالة:",
                    ["حليب_عالي", "حليب_متوسط", "حليب_منخفض", "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"],
                    format_func=lambda x: {
                        "حليب_عالي": "🐄 حلابة عالية",
                        "حليب_متوسط": "🐄 حلابة متوسطة",
                        "حليب_منخفض": "🐄 حلابة منخفضة",
                        "تسمين_مكثف": "💪 تسمين مكثف",
                        "تسمين_عادي": "💪 تسمين عادي",
                        "حمل_أخير": "🤰 حمل آخر",
                        "صيانة": "🌿 صيانة",
                    }.get(x, x),
                    key="cattle_t_v1111",
                )
                cp_ = {}
                if "حليب" in ct:
                    cp_["milk_yield"] = st.number_input("🥛 الحليب:", 5.0, 60.0, 20.0, 1.0, key="cattle_m_v1111")
                w_tape = _g("weight_tape_widget", None)
                cp_["weight_kg"] = w_tape("أبقار", "cattle_w_v1111", 500.0) if callable(w_tape) else st.number_input("⚖️ الوزن:", 50.0, 1000.0, 500.0, 10.0, key="cattle_w_fb")
                rp = _call_if_exists("get_cattle_requirements", ct, **cp_)
                if rp:
                    p1, p2, p3 = st.columns(3)
                    p1.metric("DP", f"{rp.DP}%")
                    p2.metric("CP", f"{rp.CP}%")
                    p3.metric("SE", f"{rp.SE}")
                    if st.checkbox("✅ اعتماد", key="u_cattle_v1111"):
                        animal_choice = "أبقار"
                        production_type = ct
                        requirement = rp
                        std_key_global = f"أبقار_{ct}"

            with a_tabs[1]:
                st.markdown("### 🐏 الأغنام — NRC 2007")
                sg = st.radio("الجنس:", ["ذكر", "أنثى"], horizontal=True, key="sheep_g_v1111")
                is_m = "ذكر" in sg
                stype = st.selectbox(
                    "الحالة:",
                    ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد"]
                    if is_m
                    else ["مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
                    key="sheep_t_v1111",
                )
                lit = 1
                if stype == "مرضعات":
                    lit = st.number_input("المواليد:", 1, 3, 1, 1, key="sheep_l_v1111")
                w_tape = _g("weight_tape_widget", None)
                ws = w_tape("أغنام", "sheep_w_v1111", 50.0) if callable(w_tape) else st.number_input("⚖️ الوزن:", 10.0, 150.0, 50.0, 2.0, key="sheep_w_fb")
                rp = _call_if_exists("get_sheep_requirements", stype, is_male=is_m, weight_kg=ws, litter_size=lit)
                if rp:
                    p1, p2, p3 = st.columns(3)
                    p1.metric("DP", f"{rp.DP}%")
                    p2.metric("CP", f"{rp.CP}%")
                    p3.metric("SE", f"{rp.SE}")
                    if st.checkbox("✅ اعتماد", key="u_sheep_v1111"):
                        animal_choice = "أغنام"
                        production_type = stype
                        requirement = rp
                        std_key_global = f"أغنام_{stype}"

            with a_tabs[2]:
                st.markdown("### 🐐 الماعز — NRC 2007")
                gg = st.radio("الجنس:", ["ذكر", "أنثى"], horizontal=True, key="goat_g_v1111")
                is_m = "ذكر" in gg
                mg = 0.0
                gtype = st.selectbox(
                    "الحالة:",
                    ["تسمين_جديان", "تيوس"] if is_m else ["حلابة_عالي", "حلابة_متوسط", "حامل_أخير", "صيانة"],
                    key="goat_t_v1111",
                )
                if "حلابة" in gtype:
                    mg = st.number_input("🥛 الحليب:", 0.5, 8.0, 2.0, 0.25, key="goat_m_v1111")
                w_tape = _g("weight_tape_widget", None)
                if callable(w_tape):
                    w_tape("ماعز", "goat_w_v1111", 45.0)
                rp = _call_if_exists("get_goat_requirements", gtype, is_male=is_m, milk_yield=mg)
                if rp:
                    p1, p2, p3 = st.columns(3)
                    p1.metric("DP", f"{rp.DP}%")
                    p2.metric("CP", f"{rp.CP}%")
                    p3.metric("SE", f"{rp.SE}")
                    if st.checkbox("✅ اعتماد", key="u_goat_v1111"):
                        animal_choice = "ماعز"
                        production_type = gtype
                        requirement = rp
                        std_key_global = f"ماعز_{gtype}"

            with a_tabs[3]:
                st.markdown("### 🐪 الإبل — FAO 2010")
                cmt = st.selectbox("الحالة:", ["نمو", "تسمين", "حليب", "سباق", "صيانة"], key="camel_t_v1111")
                cm = 5.0
                if cmt == "حليب":
                    cm = st.number_input("🥛 الحليب:", 2.0, 20.0, 5.0, 0.5, key="camel_m_v1111")
                w_tape = _g("weight_tape_widget", None)
                cwt = w_tape("إبل", "camel_w_v1111", 400.0) if callable(w_tape) else st.number_input("⚖️ الوزن:", 50.0, 900.0, 400.0, 10.0, key="camel_w_fb")
                rp = _call_if_exists("get_camel_requirements", cmt, weight_kg=cwt, milk_yield=cm)
                if rp:
                    p1, p2, p3 = st.columns(3)
                    p1.metric("DP", f"{rp.DP}%")
                    p2.metric("CP", f"{rp.CP}%")
                    p3.metric("SE", f"{rp.SE}")
                    if st.checkbox("✅ اعتماد", key="u_camel_v1111"):
                        animal_choice = "إبل"
                        production_type = cmt
                        requirement = rp
                        std_key_global = f"إبل_{cmt}"

            with a_tabs[4]:
                st.markdown("### 🐎 الخيول — NRC 2007")
                ht = st.selectbox(
                    "الحالة:", ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار", "مرضعات", "صيانة"], key="horse_t_v1111"
                )
                w_tape = _g("weight_tape_widget", None)
                hwt = w_tape("خيول", "horse_w_v1111", 450.0) if callable(w_tape) else st.number_input("⚖️ الوزن:", 50.0, 900.0, 450.0, 10.0, key="horse_w_fb")
                rp = _call_if_exists("get_horse_requirements", ht, weight_kg=hwt)
                if rp:
                    p1, p2, p3 = st.columns(3)
                    p1.metric("DP", f"{rp.DP}%")
                    p2.metric("CP", f"{rp.CP}%")
                    p3.metric("SE", f"{rp.SE}")
                    if st.checkbox("✅ اعتماد", key="u_horse_v1111"):
                        animal_choice = "خيول"
                        production_type = ht
                        requirement = rp
                        std_key_global = f"خيول_{ht}"

            with a_tabs[5]:
                st.markdown("### 🐔 الدواجن")
                ps = st.radio("السلالة:", ["لاحم", "بياض"], horizontal=True, key="poultry_s_v1111")
                pa = st.number_input("العمر (أسبوع):", 1, 20, 1, 1, key="poultry_a_v1111")
                rp = _call_if_exists("get_poultry_requirements", ps, pa)
                if rp:
                    p1, p2, p3, p4 = st.columns(4)
                    p1.metric("DP", f"{rp.DP}%")
                    p2.metric("CP", f"{rp.CP}%")
                    p3.metric("SE", f"{rp.SE}")
                    p4.metric("Ca", f"{rp.Ca}%")
                    if st.checkbox("✅ اعتماد", key="u_poultry_v1111"):
                        animal_choice = "دواجن"
                        production_type = ps
                        requirement = rp
                        name_ar = getattr(rp, "name_ar", "") or ""
                        if "بادي" in name_ar:
                            std_key_global = "دواجن_بادي"
                        elif "نامي" in name_ar:
                            std_key_global = "دواجن_نامي"
                        elif "بياض" in name_ar:
                            std_key_global = "دواجن_بياض"
                        else:
                            std_key_global = "دواجن_ناهي"

            with a_tabs[6]:
                st.markdown("### 🦆 السمان")
                qs = st.radio("النوع:", ["تسمين", "بياض"], horizontal=True, key="quail_s_v1111")
                qa = st.number_input("العمر:", 1, 8, 1, 1, key="quail_a_v1111")
                rp = _call_if_exists("get_quail_requirements", qs, qa)
                if rp:
                    p1, p2, p3 = st.columns(3)
                    p1.metric("DP", f"{rp.DP}%")
                    p2.metric("CP", f"{rp.CP}%")
                    p3.metric("SE", f"{rp.SE}")
                    if st.checkbox("✅ اعتماد", key="u_quail_v1111"):
                        animal_choice = "سمان"
                        production_type = qs
                        requirement = rp
                        std_key_global = "سمان_بياض" if qs == "بياض" else "سمان_بادي"

            with a_tabs[7]:
                st.markdown("### 🐟 الأسماك")
                fs = st.selectbox("النوع:", ["البلطي النيلي", "القرموط الأفريقي", "الكارب"], key="fish_sp_v1111")
                fst = st.selectbox("المرحلة:", ["بادئ زريعة", "نمو", "تسمين"], key="fish_stage_v1111")
                rp = _call_if_exists("get_fish_requirements", fs, fst)
                if rp:
                    p1, p2, p3 = st.columns(3)
                    p1.metric("DP", f"{rp.DP}%")
                    p2.metric("CP", f"{rp.CP}%")
                    p3.metric("SE", f"{rp.SE}")
                    if st.checkbox("✅ اعتماد", key="u_fish_v1111"):
                        animal_choice = "أسماك"
                        production_type = fst
                        requirement = rp
                        if "بادئ" in fst or "زريعة" in fst:
                            std_key_global = "أسماك_بادئ"
                        elif "نمو" in fst:
                            std_key_global = "أسماك_نمو"
                        else:
                            std_key_global = "أسماك_تسمين"

            with a_tabs[8]:
                st.markdown("### 🐇 الأرانب")
                rt = st.selectbox("الحالة:", ["تسمين", "حليب", "صيانة"], key="rabbit_t_v1111")
                rwt = st.number_input("⚖️ الوزن:", 1.0, 8.0, 4.0, 0.5, key="rabbit_w_v1111")
                rp = _call_if_exists("get_rabbit_requirements", rt, rwt)
                if rp:
                    p1, p2, p3 = st.columns(3)
                    p1.metric("DP", f"{rp.DP}%")
                    p2.metric("CP", f"{rp.CP}%")
                    p3.metric("SE", f"{rp.SE}")
                    if st.checkbox("✅ اعتماد", key="u_rabbit_v1111"):
                        animal_choice = "أرانب"
                        production_type = rt
                        requirement = rp
                        std_key_global = f"أرانب_{rt}"

            ready = bool(animal_choice and requirement)
            if not ready:
                st.warning("⚠️ اختر حيواناً وفعّل ✅ الاعتماد")

            if ready:
                p_req = float(getattr(requirement, "P", 0.0) or 0.0)
                ca_req = float(getattr(requirement, "Ca", 0.0) or 0.0)
                ca_p_val = (ca_req / p_req) if p_req > 0 else 0.0
                st.markdown(
                    f"""<div class="physio-card">
                    <h4>🧬 الحالة المعتمدة</h4>
                    <p style="color:#1a237e; font-size:1.15rem; font-weight:700; margin:0;">
                        {animal_choice} — <span style="color:#c62828;">{requirement.name_ar}</span>
                    </p>
                    <div style="display:flex; gap:12px; margin-top:10px; flex-wrap:wrap;">
                        <span style="background:#fff; padding:6px 14px; border-radius:8px;">🧬 DP: <b>{requirement.DP}%</b></span>
                        <span style="background:#fff; padding:6px 14px; border-radius:8px;">🧬 CP: <b>{requirement.CP}%</b></span>
                        <span style="background:#fff; padding:6px 14px; border-radius:8px;">🌽 SE: <b>{requirement.SE}</b></span>
                        <span style="background:#fff; padding:6px 14px; border-radius:8px;">⚖️ Ca:P: <b>{ca_p_val:.2f}</b></span>
                    </div>
                </div>""",
                    unsafe_allow_html=True,
                )

                eqs = _call_if_exists("get_reference_equations", animal_choice, production_type, default={})
                if eqs:
                    with st.expander("📐 المعادلات المرجعية", expanded=False):
                        if eqs.get("source"):
                            st.markdown(f"**📖 {eqs['source']}**")
                        for k, v in eqs.items():
                            if k in ("source", "example"):
                                continue
                            st.markdown(f"- **{k}:** `{v}`")
                        if eqs.get("example"):
                            st.info(f"💡 {eqs['example']}")

                oil_std_info = _call_if_exists("get_oil_standard", std_key_global, default={"max": 5.0, "optimal": 2.5}) or {
                    "max": 5.0,
                    "optimal": 2.5,
                }
                st.info(f"🌰 الزيوت: أقصى {oil_std_info.get('max', 5.0)}% | مثالي {oil_std_info.get('optimal', 2.5)}%")

                requester_name = st.text_input("👤 اسم الطالب:", key="req_name_v1111")

                st.markdown('<div class="section-title">🌾 المكونات</div>', unsafe_allow_html=True)
                sq = st.text_input("🔍 بحث:", key="ing_search_v1111")
                selected = []
                default_set = set(_call_if_exists("get_default_selections", animal_choice, production_type, requirement, default=[]) or [])
                lookup_all = _call_if_exists("_get_ingredient_lookup", default={}) or {}

                for cat_name, items in (big_feeds_lib or {}).items():
                    if not isinstance(items, dict):
                        continue
                    filt = {k: v for k, v in items.items() if sq.lower() in k.lower()} if sq else items
                    if not filt:
                        continue
                    expanded = any(x in cat_name for x in ["الحبوب", "الأكساب", "الزيوت", "الأملاح"])
                    with st.expander(f"📁 {cat_name} ({len(filt)})", expanded=expanded):
                        sc = st.columns(3)
                        for idx, ing_name in enumerate(filt.keys()):
                            with sc[idx % 3]:
                                dflt = ing_name in default_set
                                if st.checkbox(
                                    ing_name,
                                    value=dflt,
                                    key=f"pick_{animal_choice}_{ing_name}_v1111",
                                ):
                                    selected.append(ing_name)

                st.markdown("### 💰 الأسعار")
                prices_dict: Dict[str, float] = {}
                if selected:
                    pcols = st.columns(min(3, len(selected)))
                    for idx, ing in enumerate(selected):
                        with pcols[idx % 3]:
                            default_price = float((lookup_all.get(ing) or {}).get("price", 350.0) or 350.0)
                            prices_dict[ing] = st.number_input(
                                f"💵 {ing} ($/طن)",
                                min_value=5.0,
                                value=default_price,
                                step=10.0,
                                key=f"p_sel_{animal_choice}_{ing}_v1111",
                            )
                st.success(f"✅ المختارة: **{len(selected)}** مادة")

                if st.button("🚀 تشغيل المحرك (لن يفشل)", type="primary", use_container_width=True, key="run_btn_v1111"):
                    if len(selected) < 2:
                        st.error("⚠️ اختر مكونين على الأقل")
                    else:
                        custom_std = _call_if_exists("requirement_to_standard", requirement, default={}) or {}
                        with st.spinner(f"⏳ جاري التركيب ({basis_code})..."):
                            result = _call_if_exists(
                                "auto_formulate_smart",
                                selected,
                                prices_dict,
                                custom_std,
                                standard_key=std_key_global,
                                basis=basis_code,
                                min_quality=70.0,
                                animal_type=animal_choice,
                                production_type=production_type,
                                default={"success": False, "message": "تعذر تشغيل المحرك"},
                            )
                        if result and result.get("success"):
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
                                "production_type": production_type,
                            }
                            st.session_state["active_formula"] = result.get("formula") or {}
                            st.session_state["edited_result"] = None
                            st.session_state["edited_ctx"] = None
                            edit_key = f"edit_df_{animal_choice}_{production_type}"
                            st.session_state[edit_key] = pd.DataFrame(
                                [{"المكوّن": ing, "النسبة %": pct} for ing, pct in (result.get("formula") or {}).items()]
                            )
                            st.session_state["formulation_history"].append(
                                {
                                    "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "الحيوان": animal_choice,
                                    "الحالة": requirement.name_ar,
                                    "الجودة": f"{float(result.get('quality_score', 0.0)):.1f}%",
                                    "التكلفة $": f"{float(result.get('cost', 0.0)):.2f}",
                                }
                            )
                        else:
                            st.error(f"❌ {(result or {}).get('message', 'فشل التركيب')}")

                if st.session_state.get("last_formulation_result"):
                    result = st.session_state["last_formulation_result"]
                    ctx = st.session_state["last_formulation_context"] or {}
                    formula = result.get("formula") or {}
                    actual = result.get("actual_nutrients") or {}
                    cost = float(result.get("cost", 0.0) or 0.0)
                    custom_std = ctx.get("custom_standard") or {}
                    quality = float(result.get("quality_score", 0.0) or 0.0)
                    meets = bool(result.get("meets_standard", False))
                    p_act = float(actual.get("P", 0.0) or 0.0)
                    ca_act = float(actual.get("Ca", 0.0) or 0.0)
                    ca_p = (ca_act / p_act) if p_act > 0 else 0.0

                    if result.get("warning"):
                        st.warning(result["warning"])

                    if meets:
                        st.markdown(
                            f"""<div class="quality-good-v113">
                            <h3 style="color:#1b5e20; margin:0;">✅ جودة: {quality:.1f}%</h3>
                            <p style="color:#2e7d32;">Ca:P = {ca_p:.2f}</p>
                        </div>""",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"""<div class="quality-bad-v113">
                            <h3 style="color:#c62828; margin:0;">⚠️ جودة: {quality:.1f}%</h3>
                        </div>""",
                            unsafe_allow_html=True,
                        )

                    compare_rows = []
                    labels = {
                        "CP": "بروتين",
                        "DP": "مهضوم",
                        "SE": "SE",
                        "NDF": "NDF",
                        "ADF": "ADF",
                        "EE": "دهن",
                        "ASH": "رماد",
                        "Ca": "Ca",
                        "P": "P",
                    }
                    for k, sv in custom_std.items():
                        sv_f = float(sv or 0.0)
                        if sv_f == 0:
                            continue
                        cv = float(actual.get(k, 0.0) or 0.0)
                        diff = cv - sv_f
                        pct = (diff / sv_f * 100.0) if sv_f else 0.0
                        ev = _call_if_exists("evaluate_difference", pct, standard_value=sv_f, default={"label": "—", "score": 0}) or {}
                        compare_rows.append(
                            {
                                "العنصر": labels.get(k, k),
                                "المعيار": f"{sv_f:.2f}",
                                "المحسوب": f"{cv:.2f}",
                                "الفرق": f"{diff:+.3f}",
                                "الفرق %": f"{pct:+.2f}%",
                                "التقييم": ev.get("label", "—"),
                            }
                        )
                    if compare_rows:
                        st.dataframe(pd.DataFrame(compare_rows), use_container_width=True, hide_index=True)

                    st.markdown("### 🌾 المكونات:")
                    for ing, pct in formula.items():
                        pct_f = float(pct or 0.0)
                        st.markdown(
                            f'<div class="formula-item">▪️ <b>{ing}:</b> {pct_f:.2f}% ({pct_f * 10.0:.1f} كجم/طن)</div>',
                            unsafe_allow_html=True,
                        )

                    st.metric("💰 التكلفة:", f"${cost:.2f}")
                    render_share_buttons(formula, ctx.get("animal_choice", ""), quality, cost, key_suffix="model_v1111")

                    ch1, ch2 = st.columns(2)
                    with ch1:
                        _render_chart_image(
                            _call_if_exists("create_colorful_bar_chart", custom_std, actual),
                            caption="المقارنة",
                        )
                    with ch2:
                        _render_chart_image(
                            _call_if_exists("create_colorful_pie_chart", formula),
                            caption="التوزيع",
                        )

                    ch3, ch4 = st.columns(2)
                    with ch3:
                        _render_chart_image(
                            _call_if_exists("create_radar_chart", custom_std, actual),
                            caption="الرادار",
                        )
                    with ch4:
                        _render_chart_image(
                            _call_if_exists("create_gauge_chart", quality),
                            caption="الجودة",
                        )

                    if p_act > 0:
                        _render_chart_image(
                            _call_if_exists("create_ca_p_ratio_chart", ca_act, p_act),
                            caption="⚖️ Ca:P",
                        )

                    try:
                        pdf_generator_obj = _g("pdf_gen", None)
                        if pdf_generator_obj and hasattr(pdf_generator_obj, "generate_report"):
                            pdf_bytes = pdf_generator_obj.generate_report(
                                formula=formula,
                                requirement=ctx.get("requirement"),
                                animal_type=ctx.get("animal_type", ""),
                                breed=ctx.get("requirement_name", ""),
                                cost=cost,
                                city="—",
                                local_cost=cost,
                                local_sym="USD",
                                requester_name=ctx.get("requester_name", ""),
                                protein_basis=ctx.get("basis_label", "DP"),
                                standard_key=ctx.get("std_key_global", ""),
                                include_charts=True,
                                quality_score=quality,
                            )
                            _call_if_exists(
                                "render_pdf_download_with_approval",
                                pdf_bytes=pdf_bytes,
                                file_name=f"Tawor_{ctx.get('animal_type','')}_{datetime.now():%Y%m%d_%H%M}.pdf",
                                doc_title=f"تركيبة {ctx.get('animal_type','')} — {ctx.get('requirement_name','')}",
                                user_role=role,
                                user_name=st.session_state.get("chat_username", "مستخدم"),
                                doc_context={
                                    "الحيوان": ctx.get("animal_type", ""),
                                    "الحالة": ctx.get("requirement_name", ""),
                                    "الجودة": f"{quality:.1f}%",
                                    "التكلفة": f"${cost:.2f}/طن",
                                },
                                key_suffix="model_v1111",
                            )
                    except Exception as e:
                        st.error(f"⚠️ {e}")

                    # ═══ تصحيح التركيبة يدوياً ═══
                    st.markdown("---")
                    st.markdown('<div class="section-title">✏️ تصحيح التركيبة يدوياً</div>', unsafe_allow_html=True)
                    st.caption("💡 عدّل النسب ثم اضغط 'تحقق'")

                    edit_data = [{"المكوّن": ing, "النسبة %": float(pct or 0.0)} for ing, pct in formula.items()]
                    edit_key = f"edit_df_{ctx.get('animal_type','')}_{ctx.get('production_type','')}"
                    if edit_key not in st.session_state:
                        st.session_state[edit_key] = pd.DataFrame(edit_data)

                    edited_formula_df = st.data_editor(
                        st.session_state[edit_key],
                        num_rows="dynamic",
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "المكوّن": st.column_config.SelectboxColumn(
                                options=sorted(lookup_all.keys()), required=True, width="medium"
                            ),
                            "النسبة %": st.column_config.NumberColumn(
                                min_value=0.0, max_value=100.0, step=0.5, format="%.2f%%", width="small"
                            ),
                        },
                        key=f"edit_editor_{ctx.get('animal_type','')}_{ctx.get('production_type','')}_v1111",
                    )
                    st.session_state[edit_key] = edited_formula_df

                    edit_total = sum(
                        float(r["النسبة %"] or 0.0)
                        for _, r in edited_formula_df.iterrows()
                        if float(r["النسبة %"] or 0.0) > 0
                    )
                    if edit_total > 0:
                        if abs(edit_total - 100.0) > 0.5:
                            st.warning(f"⚠️ مجموع = {edit_total:.1f}% — سيتم التطبيع")
                        else:
                            st.success(f"✅ مجموع = {edit_total:.1f}%")

                    v_col1, v_col2 = st.columns(2)
                    with v_col1:
                        verify_btn = st.button(
                            "🔄 تحقق من التصحيح",
                            type="primary",
                            use_container_width=True,
                            key=f"verify_v1111_{ctx.get('animal_type','')}",
                            disabled=(edit_total <= 0),
                        )
                    with v_col2:
                        reset_btn = st.button(
                            "↩️ استرجع الأصلية",
                            use_container_width=True,
                            key=f"reset_v1111_{ctx.get('animal_type','')}",
                        )

                    if reset_btn:
                        st.session_state[edit_key] = pd.DataFrame(edit_data)
                        st.session_state["edited_result"] = None
                        st.rerun()

                    if verify_btn:
                        edited_f: Dict[str, float] = {}
                        for _, r in edited_formula_df.iterrows():
                            pct_val = float(r["النسبة %"] or 0.0)
                            ing_val = r["المكوّن"]
                            if ing_val and pct_val > 0:
                                edited_f[ing_val] = pct_val

                        if edited_f:
                            with st.spinner("🧪 جاري التحقق..."):
                                new_res = _call_if_exists(
                                    "analyze_existing_formula",
                                    edited_f,
                                    ctx.get("animal_type", ""),
                                    ctx.get("production_type", ""),
                                    default={"success": False, "message": "تعذر التحقق"},
                                )
                            if new_res and new_res.get("success"):
                                st.session_state["edited_result"] = new_res
                                st.session_state["edited_ctx"] = {
                                    "animal": ctx.get("animal_type", ""),
                                    "production": ctx.get("production_type", ""),
                                }
                                st.rerun()
                            else:
                                st.error(f"❌ {(new_res or {}).get('message', 'تعذر التحقق')}")

                    if st.session_state.get("edited_result"):
                        er = st.session_state["edited_result"]
                        e_quality = float(er.get("quality_score", 0.0) or 0.0)
                        e_meets = e_quality >= 70.0

                        st.markdown("---")
                        st.markdown("### 📊 نتيجة التركيبة المعدلة")

                        if e_meets:
                            st.markdown(
                                f"""<div class="quality-good-v113">
                                <h3 style="color:#1b5e20; margin:0;">✅ جودة المعدلة: {e_quality:.1f}%</h3>
                            </div>""",
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f"""<div class="quality-bad-v113">
                                <h3 style="color:#c62828; margin:0;">⚠️ جودة المعدلة: {e_quality:.1f}%</h3>
                            </div>""",
                                unsafe_allow_html=True,
                            )

                        em1, em2, em3, em4 = st.columns(4)
                        em1.metric("🧬 الجودة", f"{e_quality:.1f}%")
                        em2.metric("💰 التكلفة", f"${float(er.get('cost_per_ton', 0.0)):.2f}/طن")
                        em3.metric("⚖️ Ca:P", f"{float(er.get('ca_p_ratio', 0.0)):.2f}")
                        em4.metric("📊 المكونات", len(er.get("formula") or {}))

                        cmp_df2 = pd.DataFrame(
                            [
                                {
                                    "العنصر": c.get("العنصر", "—"),
                                    "المعيار": f"{float(c.get('المعيار', 0.0)):.2f}",
                                    "المحسوب": f"{float(c.get('المحسوب', 0.0)):.2f}",
                                    "الفرق %": f"{float(c.get('الفرق %', 0.0)):+.2f}%",
                                    "التقييم": c.get("التقييم", "—"),
                                }
                                for c in (er.get("comparison") or [])
                            ]
                        )
                        if not cmp_df2.empty:
                            st.dataframe(cmp_df2, use_container_width=True, hide_index=True)

                        ech1, ech2 = st.columns(2)
                        with ech1:
                            _render_chart_image(
                                _call_if_exists("create_colorful_bar_chart", er.get("standard"), er.get("actual")),
                                caption="المقارنة",
                            )
                        with ech2:
                            _render_chart_image(
                                _call_if_exists("create_colorful_pie_chart", er.get("formula")),
                                caption="التوزيع",
                            )

                        try:
                            edited_pdf = _call_if_exists("generate_lab_pdf", er, st.session_state.get("edited_ctx"))
                            _call_if_exists(
                                "render_pdf_download_with_approval",
                                pdf_bytes=edited_pdf,
                                file_name=f"Edited_{ctx.get('animal_type','')}_{datetime.now():%Y%m%d}.pdf",
                                doc_title=f"تركيبة معدلة — {ctx.get('animal_type','')} — {ctx.get('requirement_name','')}",
                                user_role=role,
                                user_name=st.session_state.get("chat_username", "مستخدم"),
                                doc_context={
                                    "الحيوان": ctx.get("animal_type", ""),
                                    "الحالة": f"{ctx.get('requirement_name','')} (معدلة)",
                                    "الجودة": f"{e_quality:.1f}%",
                                },
                                key_suffix="edited_v1111",
                            )
                        except Exception as e:
                            st.error(f"⚠️ PDF: {e}")
        except Exception as e:
            st.error(f"⚠️ {e}")
            with st.expander("التفاصيل"):
                st.code(traceback.format_exc())


# ═══ 🎯 NLP ═══

if "🎯 NLP" in tab_map:
    with tab_map["🎯 NLP"]:
        try:
            st.markdown('<div class="section-title">🎯 التحسين غير الخطي</div>', unsafe_allow_html=True)
            scipy_ok = bool(_g("SCIPY_AVAILABLE", False)) and callable(_g("minimize", None))
            if not scipy_ok:
                st.error("⚠️ SCIPY غير مثبتة أو غير متاحة")
            else:
                nc1, nc2 = st.columns(2)
                with nc1:
                    nlp_animal = st.selectbox(
                        "نوع الحيوان:",
                        ["أبقار", "أغنام", "ماعز", "إبل", "خيول", "دواجن", "سمان", "أسماك", "أرانب"],
                        key="nlp_animal_v1111",
                    )
                with nc2:
                    prod_options = {
                        "أبقار": ["حليب_عالي", "حليب_متوسط", "حليب_منخفض", "تسمين_مكثف", "تسمين_عادي", "حمل_أخير", "صيانة"],
                        "أغنام": ["تسمين_مكثف", "تسمين_عادي", "حملان_تيد", "مرضعات", "حامل_أخير", "حامل_متوسط", "صيانة"],
                        "ماعز": ["تسمين_جديان", "تيوس", "حلابة_عالي", "حلابة_متوسط", "حامل_أخير", "صيانة"],
                        "إبل": ["نمو", "تسمين", "حليب", "سباق", "صيانة"],
                        "خيول": ["رياضة_مكثف", "رياضة_عادي", "نمو_أمهار", "مرضعات", "صيانة"],
                        "دواجن": ["لاحم", "بياض"],
                        "سمان": ["تسمين", "بياض"],
                        "أسماك": ["بادئ زريعة", "نمو", "تسمين"],
                        "أرانب": ["تسمين", "حليب", "صيانة"],
                    }.get(nlp_animal, ["عام"])
                    nlp_prod = st.selectbox("الحالة:", prod_options, key="nlp_prod_v1111")

                nlp_req = _call_if_exists(
                    "_get_requirement_for_nlp", nlp_animal, nlp_prod, default={"ME": 2500.0, "CP": 15.0, "DP": 11.0}
                ) or {"ME": 2500.0, "CP": 15.0, "DP": 11.0}

                m1, m2 = st.columns(2)
                m1.metric("🎯 ME", f"{float(nlp_req.get('ME', 0.0)):.0f} kcal/kg")
                m2.metric("🎯 CP", f"{float(nlp_req.get('CP', 0.0)):.2f}%")

                active = st.session_state.get("active_formula") or {}
                lookup = _call_if_exists("_get_ingredient_lookup", default={}) or {}
                all_ings = list(lookup.keys())
                default_nlp = [k for k in list(active.keys())[:5] if k in lookup]

                nlp_sel = st.multiselect(
                    "المكونات:",
                    options=all_ings,
                    default=default_nlp,
                    max_selections=10,
                    key="nlp_sel_v1111",
                )

                if len(nlp_sel) >= 2:
                    ing_data = {i: lookup[i] for i in nlp_sel}
                    nlp_prices: Dict[str, float] = {}
                    pcols = st.columns(min(3, len(nlp_sel)))
                    for i, ing in enumerate(nlp_sel):
                        with pcols[i % 3]:
                            nlp_prices[ing] = st.number_input(
                                f"{ing}:",
                                min_value=10.0,
                                value=float((lookup[ing] or {}).get("price", 300.0) or 300.0),
                                step=10.0,
                                key=f"nlp_p_{ing}_v1111",
                            )
                    price_product = st.number_input("💵 سعر المنتج:", 0.5, 100.0, 2.5, 0.1, key="nlp_pp_v1111")

                    if st.button("🚀 تشغيل NLP", type="primary", use_container_width=True, key="nlp_run_v1111"):
                        with st.spinner("⏳ جاري التحسين..."):
                            result = _call_if_exists(
                                "nlp_optimize_feed",
                                nlp_sel,
                                ing_data,
                                nlp_prices,
                                animal_type=nlp_animal,
                                production_type=nlp_prod,
                                price_product=price_product,
                                default={"success": False, "message": "تعذر تشغيل التحسين"},
                            )
                        if result and result.get("success"):
                            if result.get("warning"):
                                st.warning(result["warning"])
                            st.success(
                                f"✅ ربح: ${float(result.get('max_profit', 0.0)):.4f} | "
                                f"استراتيجية: {result.get('strategy', '—')}"
                            )
                            m1, m2, m3, m4 = st.columns(4)
                            m1.metric("💰 التكلفة", f"${float(result.get('final_cost', 0.0)):.4f}")
                            m2.metric("⚡ ME", f"{float(result.get('final_me', 0.0)):.0f}")
                            m3.metric("🧬 CP", f"{float(result.get('final_cp', 0.0)):.2f}%")
                            m4.metric("📈 الربح", f"${float(result.get('max_profit', 0.0)):.4f}")

                            nlp_formula = result.get("formula") or {}
                            for ing, pct in nlp_formula.items():
                                st.markdown(
                                    f'<div class="formula-item">▪️ <b>{ing}:</b> {float(pct or 0.0):.2f}%</div>',
                                    unsafe_allow_html=True,
                                )

                            st.markdown("### 📊 تقييم أولي ومقارنة بالقياسي")
                            nlp_actual = _call_if_exists("compute_formula_nutrients", nlp_formula, default={}) or {}
                            me_act = float(nlp_actual.get("SE", 0.0) or 0.0) * 41.0
                            cp_act = float(nlp_actual.get("CP", 0.0) or 0.0)
                            dp_act = float(nlp_actual.get("DP", 0.0) or 0.0)
                            me_std = float(nlp_req.get("ME", 0.0) or 0.0)
                            cp_std = float(nlp_req.get("CP", 0.0) or 0.0)
                            dp_std = float(nlp_req.get("DP", 0.0) or 0.0)

                            cmp_nlp = [
                                {
                                    "العنصر": "ME (kcal/kg)",
                                    "المعيار": f"{me_std:.0f}",
                                    "المحسوب": f"{me_act:.0f}",
                                    "التقييم": "✅" if me_act >= me_std * 0.9 else "⚠️",
                                },
                                {
                                    "العنصر": "CP (%)",
                                    "المعيار": f"{cp_std:.2f}",
                                    "المحسوب": f"{cp_act:.2f}",
                                    "التقييم": "✅" if cp_act >= cp_std * 0.95 else "⚠️",
                                },
                                {
                                    "العنصر": "DP (%)",
                                    "المعيار": f"{dp_std:.2f}",
                                    "المحسوب": f"{dp_act:.2f}",
                                    "التقييم": "✅" if dp_act >= dp_std * 0.95 else "⚠️",
                                },
                            ]
                            st.dataframe(pd.DataFrame(cmp_nlp), use_container_width=True, hide_index=True)

                            r_col1, r_col2 = st.columns(2)
                            with r_col1:
                                chart_std = {"ME/100": me_std / 100.0, "CP": cp_std, "DP": dp_std}
                                chart_act = {"ME/100": me_act / 100.0, "CP": cp_act, "DP": dp_act}
                                _render_chart_image(
                                    _call_if_exists("create_colorful_bar_chart", chart_std, chart_act),
                                    caption="مقارنة ME/CP/DP",
                                )
                            with r_col2:
                                _render_chart_image(
                                    _call_if_exists("create_colorful_pie_chart", nlp_formula),
                                    caption="توزيع المكونات",
                                )

                            fig_curve = _call_if_exists(
                                "create_nlp_profit_curve", result, nlp_sel, ing_data, nlp_prices
                            )
                            if fig_curve:
                                st.plotly_chart(fig_curve, use_container_width=True)

                            try:
                                pdf_nlp = _call_if_exists(
                                    "generate_nlp_math_pdf", result, nlp_animal, nlp_prod, nlp_sel, ing_data, nlp_prices
                                )
                                if pdf_nlp:
                                    _call_if_exists(
                                        "render_pdf_download_with_approval",
                                        pdf_bytes=pdf_nlp,
                                        file_name=f"NLP_Full_{nlp_animal}_{datetime.now():%Y%m%d}.pdf",
                                        doc_title=f"NLP — {nlp_animal} — {nlp_prod}",
                                        user_role=role,
                                        user_name=st.session_state.get("chat_username", "مستخدم"),
                                        doc_context={
                                            "الحيوان": nlp_animal,
                                            "الحالة": nlp_prod,
                                            "التكلفة": f"${float(result.get('final_cost', 0.0)):.4f}",
                                        },
                                        key_suffix="nlp_v1111",
                                    )
                            except Exception as e:
                                st.warning(f"⚠️ PDF: {e}")
                        else:
                            st.error(f"❌ {(result or {}).get('message', 'فشل التحسين')}")
                else:
                    st.info("💡 اختر مكونين على الأقل")
        except Exception as e:
            st.error(f"⚠️ {e}")

from datetime import datetime
import traceback
import pandas as pd
import streamlit as st


def _g(name: str, default=None):
    val = globals().get(name, default)
    return default if val is None else val


def _call_if_exists(name: str, *args, default=None, **kwargs):
    fn = globals().get(name)
    if callable(fn):
        return fn(*args, **kwargs)
    return default


def _show_chart_or_img(obj, caption: str = ""):
    if not obj:
        return
    try:
        data = obj.getvalue() if hasattr(obj, "getvalue") else obj
        if data:
            st.image(data, caption=caption, use_container_width=True)
    except Exception:
        pass


# ═══ 🌰 الزيوت ═══
if "🌰 الزيوت" in tab_map:
    with tab_map["🌰 الزيوت"]:
        try:
            st.markdown('<div class="section-title">🌰 مكتبة الزيوت</div>', unsafe_allow_html=True)
            max_oil_pct = _g("MAX_OIL_PERCENTAGE", {}) or {}
            if max_oil_pct:
                oil_rows = [
                    {
                        "الحيوان": k,
                        "أقصى %": f"{float(v.get('max', 0.0)):.1f}%",
                        "مثالي %": f"{float(v.get('optimal', 0.0)):.1f}%",
                        "المرجع": v.get("source", "—"),
                    }
                    for k, v in max_oil_pct.items()
                    if isinstance(v, dict)
                ]
                if oil_rows:
                    st.dataframe(pd.DataFrame(oil_rows), use_container_width=True, hide_index=True)

            oils = _call_if_exists("get_oil_ingredients", default={}) or {}
            for ing_name, ing_data in oils.items():
                if not isinstance(ing_data, dict):
                    continue
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
            mr_stds = _g("MILK_REPLACER_STANDARDS", {}) or {}
            mr_ings = _g("MILK_REPLACER_INGREDIENTS", {}) or {}

            if not mr_stds or not mr_ings:
                st.warning("⚠️ بيانات بدائل الحليب غير متوفرة حالياً")
            else:
                mr1, mr2 = st.columns(2)
                with mr1:
                    mr_a = st.selectbox("الحيوان:", list(mr_stds.keys()), key="mr_a_v1111")
                    mr_v = st.number_input("الكمية (كجم):", 1.0, 10000.0, 100.0, 10.0, key="mr_v_v1111")
                with mr2:
                    std_mr = mr_stds.get(mr_a, {})
                    st.markdown(
                        f"""<div style="background:#f1f8e9; padding:20px;
                        border-radius:16px; border-right:5px solid #2e7d32;">
                        <b>📊 {mr_a}:</b><br>
                        بروتين: {std_mr.get('CP', '—')}% | دهن: {std_mr.get('Fat', '—')}% |
                        لاكتوز: {std_mr.get('Lactose', '—')}%<br>
                        Ca: {std_mr.get('Ca', '—')}% | P: {std_mr.get('P', '—')}%
                    </div>""",
                        unsafe_allow_html=True,
                    )

                mr_sel = []
                cols = st.columns(3)
                for i, (name, data) in enumerate(mr_ings.items()):
                    if not isinstance(data, dict):
                        continue
                    with cols[i % 3]:
                        with st.expander(f"{name}"):
                            st.caption(f"💵 ${float(data.get('price', 0.0)):.2f}/كجم | حد: {float(data.get('max', 0.0)):.1f}%")
                            if st.checkbox("إضافة", key=f"mr_{name}_v1111"):
                                mr_sel.append(name)

                if st.button("🧪 تركيب", type="primary", use_container_width=True, key="mr_run_v1111"):
                    if len(mr_sel) < 3:
                        st.warning("⚠️ اختر 3 مكونات على الأقل")
                    else:
                        with st.spinner("⏳ جاري التركيب..."):
                            r = _call_if_exists(
                                "formulate_milk_replacer",
                                mr_a,
                                mr_v,
                                mr_sel,
                                default={"success": False, "message": "تعذر تركيب بديل الحليب"},
                            )
                        if r and r.get("success"):
                            quality = float(r.get("quality_score", 0.0) or 0.0)
                            meets70 = quality >= 70.0
                            bg = "quality-good-v113" if meets70 else "quality-bad-v113"
                            st.markdown(
                                f"""<div class="{bg}">
                                <h3 style="color:{'#1b5e20' if meets70 else '#c62828'};
                                    margin:0;">جودة: {quality:.1f}%</h3>
                                <p>Ca:P = {float(r.get('ca_p_ratio', 0.0)):.2f}</p>
                            </div>""",
                                unsafe_allow_html=True,
                            )
                            if r.get("warning"):
                                st.warning(r["warning"])
                            for ing, pct in (r.get("formula") or {}).items():
                                pct_f = float(pct or 0.0)
                                kg = pct_f * float(mr_v) / 100.0
                                st.markdown(
                                    f'<div class="formula-item">▪️ <b>{ing}:</b> {pct_f:.2f}% ({kg:.2f} كجم)</div>',
                                    unsafe_allow_html=True,
                                )
                            st.metric("💰 تكلفة 100 كجم", f"${float(r.get('cost_per_100kg', 0.0)):.2f}")

                            pdf_mr = _call_if_exists("generate_milk_replacer_pdf", r)
                            if pdf_mr:
                                _call_if_exists(
                                    "render_pdf_download_with_approval",
                                    pdf_bytes=pdf_mr,
                                    file_name=f"Milk_{str(mr_a).split()[0]}_{datetime.now():%Y%m%d}.pdf",
                                    doc_title=f"بديل حليب — {mr_a}",
                                    user_role=role,
                                    user_name=st.session_state.get("chat_username", "مستخدم"),
                                    doc_context={
                                        "الحيوان": mr_a,
                                        "الجودة": f"{quality:.1f}%",
                                        "الكمية": f"{float(mr_v):.0f} كجم",
                                    },
                                    key_suffix="milk_v1111",
                                )
                        else:
                            st.error(f"❌ {(r or {}).get('message', 'فشل التركيب')}")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 📷 OCR ═══
if "📷 OCR" in tab_map:
    with tab_map["📷 OCR"]:
        try:
            st.markdown('<div class="section-title">📷 OCR</div>', unsafe_allow_html=True)
            if not bool(_g("OCR_AVAILABLE", False)):
                st.error("⚠️ pytesseract غير مثبتة")
            else:
                up = st.file_uploader("ارفع الصورة:", type=["jpg", "jpeg", "png"], key="ocr_upload_v1111")
                if up:
                    uploaded = up.read()
                    _show_chart_or_img(uploaded, caption="الصورة")
                    if st.button("🔍 تحليل", type="primary", use_container_width=True, key="ocr_run_v1111"):
                        with st.spinner("🔬 جاري التحليل..."):
                            result = _call_if_exists(
                                "extract_ingredients_from_image",
                                uploaded,
                                default={"success": False, "count": 0, "message": "تعذر استخراج النص"},
                            )
                        if result and result.get("success") and int(result.get("count", 0)) > 0:
                            ings = result.get("ingredients") or {}
                            st.success(f"✅ {result['count']} مادة")
                            nut = _call_if_exists("compute_formula_nutrients", ings, default={}) or {}
                            st.dataframe(
                                pd.DataFrame([{"المادة": k, "النسبة": v} for k, v in ings.items()]),
                                use_container_width=True,
                                hide_index=True,
                            )
                            n1, n2, n3, n4 = st.columns(4)
                            n1.metric("CP", f"{float(nut.get('CP', 0.0)):.2f}%")
                            n2.metric("DP", f"{float(nut.get('DP', 0.0)):.2f}%")
                            n3.metric("SE", f"{float(nut.get('SE', 0.0)):.1f}")
                            n4.metric("NDF", f"{float(nut.get('NDF', 0.0)):.2f}%")

                            with st.expander("✏️ تصحيح", expanded=True):
                                corrected = _call_if_exists("render_ocr_correction_ui", ings)
                                if st.button("✅ تطبيق", type="primary", use_container_width=True, key="ocr_apply_v1111"):
                                    if corrected:
                                        st.session_state["last_ocr_result"] = corrected
                                        st.session_state["last_ocr_nutrients"] = _call_if_exists(
                                            "compute_formula_nutrients", corrected, default={}
                                        )
                                        st.success("✅")
                                        st.rerun()

                            try:
                                pdf_gen_obj = _g("pdf_gen", None)
                                if pdf_gen_obj and hasattr(pdf_gen_obj, "generate_ocr_report"):
                                    pdf_ocr = pdf_gen_obj.generate_ocr_report(
                                        ings, nut, raw_text=result.get("raw_text", "")
                                    )
                                    _call_if_exists(
                                        "render_pdf_download_with_approval",
                                        pdf_bytes=pdf_ocr,
                                        file_name=f"OCR_{datetime.now():%Y%m%d}.pdf",
                                        doc_title="تحليل OCR — صورة",
                                        user_role=role,
                                        user_name=st.session_state.get("chat_username", "مستخدم"),
                                        doc_context={"عدد المواد": str(result["count"])},
                                        key_suffix="ocr_v1111",
                                    )
                            except Exception as e:
                                st.warning(f"⚠️ PDF: {e}")
                        else:
                            st.warning(f"⚠️ {(result or {}).get('message', 'لم يتم العثور على مكونات')}")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 🏗️ الحظائر 3D ═══
if "🏗️ الحظائر 3D" in tab_map:
    with tab_map["🏗️ الحظائر 3D"]:
        try:
            st.markdown('<div class="section-title">🏗️ مصمم الحظائر 3D</div>', unsafe_allow_html=True)

            barn_mode = st.radio(
                "نوع الحساب:",
                ["🏠 حظيرة قياسية", "🐎 مربط خيول علمي"],
                horizontal=True,
                key="barn_mode_v1111",
            )

            horse_stall_sci = _g("HORSE_STALL_SCIENCE", {}) or {}
            horse_barn_sci = _g("HORSE_BARN_SCIENCE", {}) or {}
            barn_stds = _g("BARN_DESIGN_STANDARDS", {}) or {}

            if "🐎" in barn_mode:
                st.markdown("### 🐎 مربط خيول علمي (NRC 2007 + MWPS-1)")
                if not horse_stall_sci:
                    st.warning("⚠️ معايير مربط الخيول غير متوفرة")
                else:
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        horse_count = st.number_input("🔢 عدد الخيول:", 1, 100, 10, 1, key="horse_count_v1111")
                    with c2:
                        stall_type = st.selectbox(
                            "📦 نوع المربط:",
                            list(horse_stall_sci.keys()),
                            format_func=lambda k: (
                                f"{horse_stall_sci[k].get('name_ar', k)} — "
                                f"{horse_stall_sci[k].get('width', 0)}×{horse_stall_sci[k].get('length', 0)} م"
                            ),
                            key="stall_type_v1111",
                        )
                    with c3:
                        include_service = st.checkbox("🚿 خدمات", value=True, key="service_v1111")

                    if st.button("🏗️ حساب المربط", type="primary", use_container_width=True, key="horse_calc_v1111"):
                        dims = _call_if_exists("calculate_horse_barn_scientific", horse_count, stall_type, include_service)
                        if dims:
                            st.session_state["horse_barn_dims"] = dims

                    if st.session_state.get("horse_barn_dims"):
                        dims = st.session_state["horse_barn_dims"]
                        st.markdown(
                            f"""<div class="physio-card">
                            <h4>🐎 {dims.get('stall_type_ar', '')}</h4>
                            <p style="color:#1a237e; font-size:1.1rem; font-weight:700; margin:0;">
                                {dims.get('stall_dimensions', '')} | المساحة: {dims.get('stall_area_m2', 0)} م²
                            </p>
                            <p style="color:#555; margin:8px 0 0 0;">📖 {dims.get('reference', '')}</p>
                        </div>""",
                            unsafe_allow_html=True,
                        )

                        eqs = _call_if_exists("get_reference_equations", "خيول", "مربط", default={})
                        if eqs:
                            with st.expander("📐 معادلات المربط", expanded=False):
                                if eqs.get("source"):
                                    st.markdown(f"**📖 {eqs['source']}**")
                                for k, v in eqs.items():
                                    if k in ("source", "example"):
                                        continue
                                    st.markdown(f"- **{k}:** {v}")

                        st.markdown("### 📐 الأبعاد الكلية")
                        k1, k2, k3, k4 = st.columns(4)
                        k1.metric("📏 المساحة", f"{dims.get('total_area_m2', 0)} م²")
                        k2.metric("📐 الأبعاد", f"{dims.get('building_length_m', 0)}×{dims.get('building_width_m', 0)} م")
                        k3.metric("🏔️ الارتفاع", f"{dims.get('building_height_m', 0)} م")
                        k4.metric("📦 الحجم", f"{dims.get('volume_m3', 0)} م³")

                        k5, k6, k7, k8 = st.columns(4)
                        k5.metric("🐎 مربطات", f"{dims.get('num_horses', 0)} ({dims.get('rows_count', 0)} صف × {dims.get('stalls_per_row', 0)})")
                        k6.metric("🚪 الممر", f"{dims.get('aisle_width_m', 0)} م")
                        k7.metric("🍽️ معالف", f"{dims.get('feeders_count', 0)}")
                        k8.metric("💧 سقايات", f"{dims.get('drinkers_count', 0)}")

                        st.markdown("### 🌀 التهوية")
                        v1, v2, v3, v4 = st.columns(4)
                        v1.metric("💨 الصيف", f"{float(dims.get('vent_summer_m3h', 0)):,.0f} م³/س")
                        v2.metric("💨 الشتاء", f"{float(dims.get('vent_winter_m3h', 0)):,.0f} م³/س")
                        v3.metric("🌀 مراوح نفق", f"{dims.get('tunnel_fans_count', 0)}")
                        v4.metric("🌀 مراوح جانبية", f"{dims.get('side_fans_count', 0)}")

                        st.markdown("### 🚪 الأبواب والنوافذ والفرشة")
                        d1, d2, d3, d4 = st.columns(4)
                        d1.metric("🚪 الأبواب", f"{dims.get('doors_count', 0)} × {dims.get('door_dimensions', '')}")
                        d2.metric("🪟 النوافذ", f"{dims.get('window_area_m2', 0)} م²")
                        d3.metric("🧱 الحاجز", f"{horse_barn_sci.get('front_partition_m', '—')} م")
                        d4.metric("🛏️ الفرشة", f"{dims.get('bedding_cm', 0)} سم ({dims.get('bedding_m3', 0)} م³)")

                        st.markdown("### 🏗️ المجسم 3D (إسطبلات كاملة)")
                        try:
                            fig3d = _call_if_exists("create_barn_3d_figure", dims)
                            if fig3d:
                                st.plotly_chart(fig3d, use_container_width=True)
                        except Exception as e:
                            st.warning(f"⚠️ 3D: {e}")

                        st.markdown("### 💰 التكاليف")
                        cost_data = {
                            "الهيكل": float(dims.get("cost_structure_usd", 0) or 0),
                            "السقف": float(dims.get("cost_roof_usd", 0) or 0),
                            "المربطات": float(dims.get("cost_stalls_usd", 0) or 0),
                            "الممر": float(dims.get("cost_aisle_floor_usd", 0) or 0),
                            "الخدمات": float(dims.get("cost_service_usd", 0) or 0),
                            "التهوية": float(dims.get("cost_ventilation_usd", 0) or 0),
                            "الإضاءة": float(dims.get("cost_lighting_usd", 0) or 0),
                            "النوافذ": float(dims.get("cost_windows_usd", 0) or 0),
                        }
                        cost_df = pd.DataFrame([{"البند": k, "التكلفة ($)": f"${v:,.0f}"} for k, v in cost_data.items()])
                        st.dataframe(cost_df, use_container_width=True, hide_index=True)
                        st.metric("💰 إجمالي", f"${float(dims.get('cost_total_usd', 0) or 0):,.0f}")

                        try:
                            pdf_b = _call_if_exists("generate_barn_pdf_report", dims)
                            if pdf_b:
                                _call_if_exists(
                                    "render_pdf_download_with_approval",
                                    pdf_bytes=pdf_b,
                                    file_name=f"Horse_Barn_{horse_count}_{datetime.now():%Y%m%d}.pdf",
                                    doc_title=f"مربط خيول — {horse_count} حصان",
                                    user_role=role,
                                    user_name=st.session_state.get("chat_username", "مستخدم"),
                                    doc_context={
                                        "عدد الخيول": str(horse_count),
                                        "نوع المربط": dims.get("stall_type_ar", ""),
                                        "المساحة": f"{dims.get('total_area_m2', 0)} م²",
                                    },
                                    key_suffix="horse_barn_v1111",
                                )
                        except Exception as e:
                            st.error(f"⚠️ PDF: {e}")
            else:
                if not barn_stds:
                    st.warning("⚠️ معايير الحظائر غير متوفرة")
                else:
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        barn_a = st.selectbox(
                            "🐾 الحيوان:",
                            list(barn_stds.keys()),
                            format_func=lambda k: barn_stds[k].get("name_ar", k),
                            key="barn_animal_v1111",
                        )
                    with c2:
                        barn_c = st.number_input("🔢 العدد:", 1, 100000, 1000, 50, key="barn_count_v1111")
                    with c3:
                        barn_s = st.selectbox("🏠 النظام:", ["أرضي مفتوح", "بطاريات"], key="barn_system_v1111")

                    dims = _call_if_exists("calculate_barn_dimensions", barn_a, barn_c, barn_s)
                    if dims:
                        k1, k2, k3, k4 = st.columns(4)
                        k1.metric("📏 المساحة", f"{dims.get('total_area_m2', 0)} م²")
                        k2.metric("📐 الأبعاد", f"{dims.get('length_m', 0)}×{dims.get('width_m', 0)} م")
                        k3.metric("🏔️ القمة", f"{dims.get('ridge_height_m', 0)} م")
                        k4.metric("📦 الحجم", f"{dims.get('volume_m3', 0)} م³")

                        v1, v2, v3, v4 = st.columns(4)
                        v1.metric("🌀 مراوح نفق", f"{dims.get('tunnel_fans_count', 0)}")
                        v2.metric("🌀 مراوح جانبية", f"{dims.get('side_fans_count', 0)}")
                        v3.metric(
                            "❄️ ألواح تبريد",
                            f"{dims.get('cooling_pad_area_m2', 0)} م²" if dims.get("cooling_pad_enabled") else "—",
                        )
                        v4.metric("💧 ماء/يوم", f"{float(dims.get('water_per_day_L', 0) or 0):,.0f} لتر")

                        fig3d = _call_if_exists("create_barn_3d_figure", dims)
                        if fig3d:
                            st.plotly_chart(fig3d, use_container_width=True)

                        try:
                            pdf_b = _call_if_exists("generate_barn_pdf_report", dims)
                            if pdf_b:
                                _call_if_exists(
                                    "render_pdf_download_with_approval",
                                    pdf_bytes=pdf_b,
                                    file_name=f"Barn_{barn_a}_{datetime.now():%Y%m%d}.pdf",
                                    doc_title=f"حظيرة {barn_a} — {barn_c} رأس",
                                    user_role=role,
                                    user_name=st.session_state.get("chat_username", "مستخدم"),
                                    doc_context={
                                        "الحيوان": barn_a,
                                        "العدد": str(barn_c),
                                        "المساحة": f"{dims.get('total_area_m2', 0)} م²",
                                    },
                                    key_suffix="barn_v1111",
                                )
                        except Exception as e:
                            st.error(f"⚠️ PDF: {e}")
        except Exception as e:
            st.error(f"⚠️ {e}")
            with st.expander("التفاصيل"):
                st.code(traceback.format_exc())


# ═══ 📊 الجدوى ═══
if "📊 الجدوى" in tab_map:
    with tab_map["📊 الجدوى"]:
        try:
            st.markdown('<div class="section-title">📊 دراسة الجدوى</div>', unsafe_allow_html=True)
            barn_stds = _g("BARN_DESIGN_STANDARDS", {}) or {}
            if not barn_stds:
                st.warning("⚠️ معايير الجدوى غير متوفرة")
            else:
                mode = st.radio("النوع:", ["🔬 فنية", "💰 اقتصادية"], horizontal=True, key="feas_mode_v1111")
                f1, f2 = st.columns(2)
                fp = 350.0
                pp = 2.5
                with f1:
                    feas_k = st.selectbox(
                        "الحيوان:",
                        list(barn_stds.keys()),
                        format_func=lambda k: barn_stds[k].get("name_ar", k),
                        key="feas_animal_v1111",
                    )
                    feas_c = st.number_input("العدد:", 1, 100000, 1000, 50, key="feas_count_v1111")
                with f2:
                    if "اقتصادية" in mode:
                        fp = st.number_input("💵 سعر العلف ($/طن):", 50.0, 5000.0, 350.0, 10.0, key="feas_fp_v1111")
                        pp = st.number_input("💵 سعر المنتج ($/كجم):", 0.1, 10000.0, 2.5, 0.1, key="feas_pp_v1111")

                dims = _call_if_exists("calculate_barn_dimensions", feas_k, feas_c)
                if dims:
                    fc1, fc2, fc3, fc4 = st.columns(4)
                    fc1.metric("📏 المساحة", f"{dims.get('total_area_m2', 0)} م²")
                    fc2.metric("📦 الحجم", f"{dims.get('volume_m3', 0)} م³")
                    fc3.metric("💧 ماء/يوم", f"{float(dims.get('water_per_day_L', 0) or 0):,.0f} لتر")
                    fc4.metric("💰 تكلفة الحظيرة", f"${float(dims.get('cost_total_usd', 0) or 0):,.0f}")

                    if "اقتصادية" in mode:
                        est_feed_tons = float(feas_c) * 0.08 * 30.0 / 1000.0
                        est_prod_kg = float(feas_c) * 1.8
                        est_feed_cost = est_feed_tons * float(fp)
                        est_rev = est_prod_kg * float(pp)
                        e1, e2, e3 = st.columns(3)
                        e1.metric("🌾 علف تقديري/دورة", f"{est_feed_tons:.1f} طن")
                        e2.metric("💵 تكلفة علف تقديرية", f"${est_feed_cost:,.0f}")
                        e3.metric("📈 إيراد تقديري", f"${est_rev:,.0f}")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 🐔 المزارع ═══
if "🐔 المزارع" in tab_map:
    with tab_map["🐔 المزارع"]:
        try:
            st.markdown('<div class="section-title">🐔 إدارة المزارع</div>', unsafe_allow_html=True)
            farms = st.session_state.setdefault("broiler_farms", {})
            with st.form("new_farm_v1111", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    nf_name = st.text_input("اسم المزرعة *", key="nf_n_v1111")
                    nf_strain = st.selectbox("السلالة", ["Ross 308", "Cobb 500"], key="nf_s_v1111")
                with c2:
                    nf_birds = st.number_input("الطيور:", 100, 100000, 1000, 50, key="nf_b_v1111")
                    nf_date = st.date_input("التاريخ", key="nf_d_v1111")
                if st.form_submit_button("💾 حفظ", type="primary", use_container_width=True) and nf_name.strip():
                    clean_name = nf_name.strip()
                    if clean_name not in farms:
                        farms[clean_name] = {
                            "strain": nf_strain,
                            "start_birds": int(nf_birds),
                            "start_date": str(nf_date),
                            "records": [],
                        }
                        st.success(f"✅ {clean_name}")
                        st.rerun()
                    else:
                        st.warning("⚠️ موجودة")

            if farms:
                sel = st.selectbox("اختر مزرعة:", list(farms.keys()), key="farm_sel_v1111")
                farm = farms[sel]
                st.markdown(f"### 📝 {farm.get('strain', '')} — قراءة يومية")
                with st.form(f"rec_{sel}_v1111"):
                    rc = st.columns(3)
                    with rc[0]:
                        age = st.number_input("العمر", 1, 60, 1, key="r_age_v1111")
                    with rc[1]:
                        alive = st.number_input(
                            "حي", 0, int(farm.get("start_birds", 1000)), value=int(farm.get("start_birds", 1000)), key="r_alive_v1111"
                        )
                    with rc[2]:
                        wt = st.number_input("وزن (كجم)", 0.01, 5.0, 0.045, 0.005, key="r_wt_v1111")
                    if st.form_submit_button("➕ تسجيل", type="primary", use_container_width=True):
                        farm.setdefault("records", []).append(
                            {"date": str(datetime.now().date()), "age": int(age), "alive": int(alive), "wt": float(wt)}
                        )
                        st.success("✅")
                        st.rerun()

                if farm.get("records"):
                    latest = farm["records"][-1]
                    start_b = max(1, int(farm.get("start_birds", 1)))
                    liv = float(latest.get("alive", 0)) / start_b * 100.0
                    m = st.columns(3)
                    m[0].metric("🐦 حيوية", f"{liv:.1f}%")
                    m[1].metric("⚖️ الوزن", f"{float(latest.get('wt', 0.0)):.3f} كجم")
                    m[2].metric("📅 العمر", f"{latest.get('age', 0)} يوم")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ تبويبات المالك ═══
if role == "owner":
    if "🏭 المستودعات" in tab_map:
        with tab_map["🏭 المستودعات"]:
            try:
                st.markdown('<div class="section-title">🏭 المستودعات</div>', unsafe_allow_html=True)
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
                    key="inv_editor_v1111",
                )
                if st.button("💾 حفظ", type="primary", use_container_width=True, key="inv_save_v1111"):
                    for _, r in edited.iterrows():
                        name = r["المادة"]
                        if name in inv:
                            inv[name]["quantity"] = float(r["الكمية (طن)"] or 0.0)
                            inv[name]["min_threshold"] = float(r["الحد الأدنى"] or 0.0)
                    st.success("✅")
                    st.rerun()
            except Exception as e:
                st.error(f"⚠️ {e}")

    if "📋 طلبات PDF" in tab_map:
        with tab_map["📋 طلبات PDF"]:
            try:
                _call_if_exists("render_pdf_requests_admin")
            except Exception as e:
                st.error(f"⚠️ {e}")
                with st.expander("التفاصيل"):
                    st.code(traceback.format_exc())

    if "🧾 الفواتير" in tab_map:
        with tab_map["🧾 الفواتير"]:
            try:
                st.markdown('<div class="section-title">🧾 الفواتير</div>', unsafe_allow_html=True)
                st.info("💡 نظام فواتير كامل")
            except Exception as e:
                st.error(f"⚠️ {e}")

    if "🖨️ الديباجة" in tab_map:
        with tab_map["🖨️ الديباجة"]:
            try:
                st.markdown('<div class="section-title">🖨️ الديباجة</div>', unsafe_allow_html=True)
                st.markdown(
                    f"""<div style="border:3px solid #1b5e20;
                    padding:50px 30px; border-radius:15px;
                    background:linear-gradient(135deg,#f1f8e9,#e8f5e9);
                    direction:rtl; text-align:center;">
                    <h1 style="color:#1b5e20;">{_g("APP_NAME", "تاور نولجي")}</h1>
                    <h3 style="color:#1565C0;">{_g("APP_TAGLINE", "")}</h3>
                    <h2 style="color:#c62828;">{_g("SUPERVISOR", "")}</h2>
                    <p style="color:#0d47a1;">{_g("SUPERVISOR_TITLE", "")}</p>
                    <p>📅 {datetime.now():%Y-%m-%d}</p>
                    <p style="color:#c62828;">🤲 {_g("DUA_SHORT", "")} 🤲</p>
                </div>""",
                    unsafe_allow_html=True,
                )
            except Exception as e:
                st.error(f"⚠️ {e}")

    if "📈 التحليلات" in tab_map:
        with tab_map["📈 التحليلات"]:
            try:
                st.markdown('<div class="section-title">📈 التحليلات</div>', unsafe_allow_html=True)
                history = st.session_state.get("formulation_history", [])
                m1, m2, m3 = st.columns(3)
                m1.metric("🧬 خلطات", len(history))
                m2.metric("🐔 مزارع", len(st.session_state.get("broiler_farms", {})))
                m3.metric("📦 مواد", len(st.session_state.get("inventory", {})))
                if history:
                    st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"⚠️ {e}")


# ═══ 💬 غرفة التواصل ═══
if "💬 غرفة التواصل" in tab_map:
    with tab_map["💬 غرفة التواصل"]:
        try:
            st.markdown('<div class="section-title">💬 غرفة التواصل</div>', unsafe_allow_html=True)
            st.caption("🔒 نقاش علمي — مشاركة العلفة والنتائج")

            rooms = dict(_call_if_exists("_load_chat_rooms", default={}) or {})
            for dr in ["🌾 النقاش العام", "🧬 نقاش علمي", "💰 نقاش اقتصادي"]:
                if dr not in rooms:
                    rooms[dr] = []
            _call_if_exists("_save_chat_rooms", rooms)

            c1, c2, c3 = st.columns([0.5, 0.25, 0.25])
            with c1:
                current_room = st.selectbox("🏠 الغرفة:", list(rooms.keys()), key="comm_room_v1111")
            with c2:
                if role in ("owner", "specialist"):
                    if st.button("➕ غرفة جديدة", use_container_width=True, key="comm_new_v1111"):
                        st.session_state["show_new_room"] = True
            with c3:
                if role == "owner" and st.button("🗑️ حذف", use_container_width=True, key="comm_del_v1111"):
                    if current_room in rooms and len(rooms) > 1:
                        del rooms[current_room]
                        _call_if_exists("_save_chat_rooms", rooms)
                        st.rerun()

            if st.session_state.get("show_new_room"):
                nr = st.text_input("اسم الغرفة:", key="comm_nr_v1111")
                if st.button("إنشاء", key="comm_nr_btn_v1111") and nr.strip():
                    if _call_if_exists("create_chat_room", nr.strip(), default=False):
                        st.session_state["show_new_room"] = False
                        st.rerun()

            username = _call_if_exists("_safe_username", default=st.session_state.get("chat_username", "مستخدم"))
            msgs = (rooms.get(current_room) or [])[-80:]
            st.caption(f"👤 {username} | 🏠 {current_room} | عدد: {len(msgs)}")

            chat_html = (
                '<div style="background:#fafafa; padding:15px; border-radius:14px; '
                'height:450px; overflow-y:auto; border:1px solid #e0e0e0; direction:rtl;">'
            )
            if not msgs:
                chat_html += '<p style="text-align:center;color:#999;">لا رسائل — كن أول من يكتب 👋</p>'
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

            with st.form(f"comm_form_{current_room}_v1111", clear_on_submit=True):
                msg_text = st.text_area("✍️ رسالتك:", height=80, key=f"comm_msg_{current_room}_v1111")
                cc1, cc2 = st.columns([0.75, 0.25])
                with cc1:
                    share_formula = st.checkbox("📎 إرفاق التركيبة", value=False, key="comm_attach_v1111")
                with cc2:
                    send = st.form_submit_button("📤 إرسال", type="primary", use_container_width=True)
                if send:
                    rate_ok = _call_if_exists("check_rate_limit", "comm", max_calls=30, window=60, default=True)
                    if not rate_ok:
                        st.warning("⏳ تهدئة")
                    else:
                        final_msg = msg_text
                        if share_formula:
                            active = st.session_state.get("active_formula") or {}
                            if active:
                                fs = " | ".join(f"{k}: {float(v):.1f}%" for k, v in active.items())
                                final_msg = f"{final_msg}\n\n📋 التركيبة:\n{fs}".strip()
                        if _call_if_exists("add_chat_message", current_room, username, final_msg, default=False):
                            st.rerun()

            if st.button("🔄 تحديث", key="comm_refresh_v1111"):
                st.rerun()
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 🎬 الاستديو ═══
if "🎬 الاستديو" in tab_map:
    with tab_map["🎬 الاستديو"]:
        try:
            st.markdown('<div class="section-title">🎬 الاستديو</div>', unsafe_allow_html=True)
            studio = dict(_call_if_exists("_load_studio", default={}) or {})
            studio.setdefault("videos", [])
            studio.setdefault("slides", [])
            studio.setdefault("notes", [])

            sub_s1, sub_s2, sub_s3 = st.tabs(["📹 فيديوهات", "📊 شرائح", "📝 ملاحظات"])
            with sub_s1:
                with st.form("sv_v1111"):
                    vt = st.text_input("العنوان:", key="vid_t_v1111")
                    vu = st.text_input("رابط:", key="vid_u_v1111")
                    vd = st.text_area("الوصف:", key="vid_d_v1111")
                    if st.form_submit_button("➕ إضافة", type="primary") and vt.strip() and vu.strip():
                        sanitize = lambda x, n: _call_if_exists("_sanitize_message", x, n, default=x)
                        studio["videos"].append(
                            {
                                "title": sanitize(vt.strip(), 100),
                                "url": sanitize(vu.strip(), 500),
                                "desc": sanitize(vd.strip(), 500),
                                "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            }
                        )
                        _call_if_exists("_save_studio", studio)
                        st.rerun()
                for i, v in enumerate(list(studio["videos"])):
                    with st.expander(f"🎬 {v.get('title', '')} — {v.get('ts', '')}"):
                        st.markdown(f"🔗 [فتح]({v.get('url', '')})")
                        if v.get("desc"):
                            st.caption(v["desc"])
                        if st.button("🗑️", key=f"del_vid_{i}_v1111"):
                            studio["videos"].pop(i)
                            _call_if_exists("_save_studio", studio)
                            st.rerun()

            with sub_s2:
                with st.form("ss_v1111"):
                    s_title = st.text_input("العنوان:", key="sl_t_v1111")
                    s_url = st.text_input("رابط الصورة:", key="sl_u_v1111")
                    if st.form_submit_button("➕ إضافة", type="primary") and s_title.strip() and s_url.strip():
                        sanitize = lambda x, n: _call_if_exists("_sanitize_message", x, n, default=x)
                        studio["slides"].append(
                            {
                                "title": sanitize(s_title.strip(), 100),
                                "url": sanitize(s_url.strip(), 500),
                                "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            }
                        )
                        _call_if_exists("_save_studio", studio)
                        st.rerun()
                for i, s in enumerate(list(studio["slides"])):
                    st.markdown(f"**{s.get('title', '')}**")
                    try:
                        st.image(s.get("url", ""), use_container_width=True)
                    except Exception:
                        st.caption(f"🔗 {s.get('url', '')}")
                    if st.button("🗑️", key=f"del_sl_{i}_v1111"):
                        studio["slides"].pop(i)
                        _call_if_exists("_save_studio", studio)
                        st.rerun()

            with sub_s3:
                with st.form("sn_v1111"):
                    nt = st.text_area("ملاحظة:", key="note_t_v1111")
                    if st.form_submit_button("➕ حفظ", type="primary") and nt.strip():
                        sanitize = lambda x, n: _call_if_exists("_sanitize_message", x, n, default=x)
                        author = _call_if_exists("_safe_username", default=st.session_state.get("chat_username", "مستخدم"))
                        studio["notes"].append(
                            {
                                "text": sanitize(nt.strip(), 1000),
                                "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "author": author,
                            }
                        )
                        _call_if_exists("_save_studio", studio)
                        st.rerun()
                total_notes = len(studio["notes"])
                for i, n in enumerate(reversed(list(studio["notes"]))):
                    ri = total_notes - 1 - i
                    st.markdown(
                        f'<div class="formula-item"><b>{n.get("author", "")}</b> — '
                        f'<small>{n.get("ts", "")}</small><br>{n.get("text", "")}</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button("🗑️", key=f"del_note_{ri}_v1111"):
                        studio["notes"].pop(ri)
                        _call_if_exists("_save_studio", studio)
                        st.rerun()
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 📚 المراجع ═══
if "📚 المراجع" in tab_map:
    with tab_map["📚 المراجع"]:
        try:
            st.markdown('<div class="section-title">📚 المراجع</div>', unsafe_allow_html=True)
            st.markdown("### 🎯 مراجع حسب الحالة")
            ref_animal = st.selectbox(
                "اختر الحيوان:",
                ["أبقار", "أغنام", "ماعز", "إبل", "خيول", "دواجن", "سمان", "أسماك", "أرانب"],
                key="ref_animal_v1111",
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
            ref_prod = st.selectbox("نوع الإنتاج:", ref_prod_map.get(ref_animal, ["عام"]), key="ref_prod_v1111")

            refs = _call_if_exists("get_references", ref_animal, ref_prod, default={}) or {}
            eqs = _call_if_exists("get_reference_equations", ref_animal, ref_prod, default={}) or {}

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
                if eqs.get("source"):
                    st.caption(f"📖 المصدر: {eqs['source']}")
                if eqs.get("example"):
                    st.info(f"💡 **مثال:** {eqs['example']}")

            if refs.get("secondary"):
                st.markdown("### 📚 مراجع داعمة")
                for s in refs["secondary"]:
                    st.markdown(f"- {s}")

            gen_refs = _g("GENERAL_REFERENCES", []) or []
            if gen_refs:
                st.markdown("---")
                st.markdown("### 📖 المراجع العامة")
                for i, ref in enumerate(gen_refs, 1):
                    st.markdown(f"{i}. {ref}")
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══ 📖 الدليل ═══
if "📖 الدليل" in tab_map:
    with tab_map["📖 الدليل"]:
        try:
            st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
            app_n = _g("APP_NAME", "تاور نولجي")
            app_v = _g("APP_VERSION", "11.11.0")
            oils_cnt = len(_call_if_exists("get_oil_ingredients", default={}) or {})
            wa_num = _g("WHATSAPP_NUMBER", "")
            own_mail = _g("OWNER_EMAIL", "")
            dua_f = _g("DUA_FULL", "")

            st.markdown(
                f"""
### 🎯 الغرض
**{app_n} v{app_v}** — منصة ذكية لتركيب الأعلاف.

### ✨ الميزات الرئيسية
- 🐄 9 قطاعات × متغيرات متعددة
- 🌰 {oils_cnt} زيتاً + معايير
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

### 🔐 بوابات الدخول
- 👑 **المالك:** كود آمن + تحميل PDF مباشر + إدارة طلبات
- 🔬 **المختص:** دخول مباشر (PDF بموافقة المالك)
- 👥 **الزائر:** مجاني بحاسبة + مختبر + PDF (بموافقة)

### 📞 التواصل
📧 {own_mail}
📱 {wa_num}

---
{dua_f}
"""
            )
        except Exception as e:
            st.error(f"⚠️ {e}")


# ═══════════════════════════════════════════════════════════════════════
# التذييل
# ═══════════════════════════════════════════════════════════════════════

_app_ver = _g("APP_VERSION", "11.11.0")
st.markdown(
    f'<div class="mini-signature">🌾 {_g("APP_NAME", "تاور نولجي")} v{_app_ver} | {_g("SUPERVISOR", "")} © 2026</div>',
    unsafe_allow_html=True,
)
if _g("DUA_SHORT", ""):
    st.markdown(f'<div class="dua-fixed-banner">🤲 {_g("DUA_SHORT", "")} 🤲</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
