# ============================================================================
# 📦 tawor_modules.py — وحدات التصدير والتخزين الاحترافية
# Tawornology v19.4
# ============================================================================
import io
import json
import sqlite3
import secrets
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

try:
    import xlsxwriter
    XLSX_AVAILABLE = True
except ImportError:
    XLSX_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────
# 1) مُصدِّر Excel احترافي (متعدد الصفحات + RTL + تنسيق)
# ─────────────────────────────────────────────────────────────────────────
class ExcelExporter:
    """
    مُصدِّر Excel احترافي متعدد الصفحات:
      • الصفحة 1: الخلطة النهائية
      • الصفحة 2: الأملاح والألياف
      • الصفحة 3: التوصيات والتحذيرات
      • الصفحة 4: حساسية DP/SE (اختياري)
      • الصفحة 5: توزيع مونت كارلو (اختياري)
      • الصفحة 6: حد باريتو (اختياري)
      • الصفحة 7: الأسعار الظلية (اختياري)
    """

    @staticmethod
    def export_full(result: dict,
                    sensitivity: dict = None,
                    monte_carlo: dict = None,
                    pareto: list = None,
                    shadow: dict = None,
                    extra_meta: dict = None) -> bytes:
        if not XLSX_AVAILABLE:
            raise ImportError("pip install xlsxwriter")

        bio = io.BytesIO()
        wb = xlsxwriter.Workbook(bio, {'in_memory': True})

        # تنسيقات موحدة
        F = {
            'title': wb.add_format({
                'bold': True, 'font_size': 16, 'align': 'center',
                'valign': 'vcenter', 'bg_color': '#1b5e20',
                'font_color': 'white', 'border': 1}),
            'header': wb.add_format({
                'bold': True, 'font_size': 12, 'align': 'center',
                'valign': 'vcenter', 'bg_color': '#2e7d32',
                'font_color': 'white', 'border': 1,
                'text_wrap': True}),
            'cell': wb.add_format({
                'align': 'center', 'valign': 'vcenter',
                'border': 1, 'font_size': 11}),
            'cell_right': wb.add_format({
                'align': 'right', 'valign': 'vcenter',
                'border': 1, 'font_size': 11}),
            'kpi_label': wb.add_format({
                'bold': True, 'bg_color': '#e8f5e9',
                'border': 1, 'align': 'center', 'font_size': 11}),
            'kpi_value': wb.add_format({
                'bold': True, 'font_size': 14, 'align': 'center',
                'bg_color': '#fff9c4', 'border': 1,
                'font_color': '#1b5e20'}),
            'warn': wb.add_format({
                'bg_color': '#fff3e0', 'font_color': '#e65100',
                'border': 1, 'text_wrap': True,
                'align': 'right', 'valign': 'top'}),
            'good': wb.add_format({
                'bg_color': '#e8f5e9', 'font_color': '#1b5e20',
                'border': 1, 'text_wrap': True,
                'align': 'right', 'valign': 'top'}),
            'money': wb.add_format({
                'num_format': '$#,##0.00',
                'align': 'center', 'border': 1, 'bold': True,
                'bg_color': '#fff9c4'}),
            'pct': wb.add_format({
                'num_format': '0.00"%"',
                'align': 'center', 'border': 1}),
        }

        # ═══════════════════════════════════════════
        # الصفحة 1: الخلطة
        # ═══════════════════════════════════════════
        ws1 = wb.add_worksheet("الخلطة")
        ws1.right_to_left()
        ws1.set_column('A:A', 32)
        ws1.set_column('B:D', 18)
        ws1.set_column('E:E', 22)

        ws1.merge_range('A1:E1',
            f"🌾 تاور نولجي Tawornology — خلطة {result['animal_type']} / "
            f"{result['stage']}", F['title'])
        ws1.set_row(0, 32)

        # KPIs
        kpi_row = 2
        kpis = [
            ("💰 التكلفة/طن", f"${result['cost_per_ton']:.2f}"),
            ("📊 DP", f"{result['totals']['DP']:.2f}%"),
            ("⚡ SE", f"{result['totals']['SE']:.2f}"),
            ("🧬 CP", f"{result['totals']['CP']:.2f}%"),
            ("📦 عدد المكونات", str(len(result['formula']))),
        ]
        for i, (lbl, val) in enumerate(kpis):
            col = i
            ws1.write(kpi_row, col, lbl, F['kpi_label'])
            ws1.write(kpi_row + 1, col, val, F['kpi_value'])
        ws1.set_row(kpi_row, 24)
        ws1.set_row(kpi_row + 1, 28)

        # جدول المكونات
        start_row = kpi_row + 3
        headers = ["المادة", "النسبة %", "كجم/طن", "kg/100kg", "الحالة"]
        for j, h in enumerate(headers):
            ws1.write(start_row, j, h, F['header'])
        ws1.set_row(start_row, 26)

        for i, (ing, pct) in enumerate(result['formula'].items(), start=1):
            status = ("🔒 إلزامي"
                      if ing in result.get('fixed_ingredients', {})
                      else "🟢 أساسي" if pct >= 20
                      else "🟡 مهم" if pct >= 5
                      else "⚪ مكمل")
            row = start_row + i
            ws1.write(row, 0, ing, F['cell_right'])
            ws1.write_number(row, 1, round(pct, 4), F['cell'])
            ws1.write_number(row, 2, round(pct * 10, 2), F['cell'])
            ws1.write_number(row, 3, round(pct, 4), F['cell'])
            ws1.write(row, 4, status, F['cell'])

        # الإجمالي
        total_row = start_row + len(result['formula']) + 1
        ws1.write(total_row, 0, "الإجمالي", F['header'])
        ws1.write_number(total_row, 1,
            round(sum(result['formula'].values()), 2), F['header'])
        ws1.write_number(total_row, 2, 1000, F['header'])

        # ═══════════════════════════════════════════
        # الصفحة 2: الأملاح والألياف
        # ═══════════════════════════════════════════
        ws2 = wb.add_worksheet("الأملاح والألياف")
        ws2.right_to_left()
        ws2.set_column('A:A', 22)
        ws2.set_column('B:E', 20)

        ws2.merge_range('A1:E1', "🧂🌾 تحليل الأملاح والألياف",
                         F['title'])
        ws2.set_row(0, 28)

        headers2 = ["العنصر", "المحسوب", "القياسي", "الانحراف %", "التقييم"]
        for j, h in enumerate(headers2):
            ws2.write(2, j, h, F['header'])
        ws2.set_row(2, 26)

        names_map = {"Ca": "كالسيوم (Ca)", "P": "فسفور (P)",
                     "Na": "صوديوم (Na)", "K": "بوتاسيوم (K)",
                     "Mg": "مغنيسيوم (Mg)", "Cl": "كلور (Cl)",
                     "S": "كبريت (S)", "NDF": "NDF", "ADF": "ADF",
                     "CF": "CF", "Ash": "رماد (Ash)"}

        row_i = 3
        for key, name in names_map.items():
            std_val = result.get('mf_standard', {}).get(key)
            calc_val = result.get('minerals', {}).get(key, 0.0)
            ev = result.get('mineral_eval', {}).get(key, {})

            ws2.write(row_i, 0, name, F['cell_right'])
            ws2.write_number(row_i, 1, round(calc_val, 4), F['cell'])
            if std_val is not None:
                ws2.write_number(row_i, 2, round(std_val, 4), F['cell'])
                ws2.write_number(row_i, 3,
                    round(ev.get('deviation', 0), 2), F['cell'])
                ws2.write(row_i, 4, ev.get('grade', '-'), F['cell'])
            else:
                ws2.write(row_i, 2, "—", F['cell'])
                ws2.write(row_i, 3, "—", F['cell'])
                ws2.write(row_i, 4, "—", F['cell'])
            row_i += 1

        # النسب
        row_i += 1
        ws2.write(row_i, 0, "النسبة", F['header'])
        ws2.write(row_i, 1, "القيمة", F['header'])
        ws2.write(row_i, 2, "المثالي", F['header'])
        ws2.write(row_i, 3, "الحالة", F['header'])
        row_i += 1
        ca_p = result.get('ratios', {}).get('Ca_P_ratio', 0)
        k_na = result.get('ratios', {}).get('K_Na_ratio', 0)
        ws2.write(row_i, 0, "Ca : P", F['cell_right'])
        ws2.write_number(row_i, 1, round(ca_p, 3), F['cell'])
        ws2.write(row_i, 2, "≈ 2.0", F['cell'])
        ws2.write(row_i, 3,
            "✅" if abs(ca_p - 2.0) <= 0.6 else "⚠️", F['cell'])
        row_i += 1
        ws2.write(row_i, 0, "K : Na", F['cell_right'])
        ws2.write_number(row_i, 1, round(k_na, 3), F['cell'])
        ws2.write(row_i, 2, "≈ 3.0", F['cell'])
        ws2.write(row_i, 3,
            "✅" if 2.5 <= k_na <= 4.0 else "⚠️", F['cell'])

        # ═══════════════════════════════════════════
        # الصفحة 3: التوصيات والتحذيرات
        # ═══════════════════════════════════════════
        ws3 = wb.add_worksheet("التوصيات")
        ws3.right_to_left()
        ws3.set_column('A:A', 6)
        ws3.set_column('B:B', 100)

        ws3.merge_range('A1:B1', "📌 التوصيات والتحذيرات", F['title'])
        ws3.set_row(0, 28)

        ws3.write(2, 0, "#", F['header'])
        ws3.write(2, 1, "التوصية", F['header'])

        r = 3
        for w in result.get('warnings', []):
            ws3.write(r, 0, r - 2, F['cell'])
            ws3.write(r, 1, w.replace('<b>', '').replace('</b>', ''),
                       F['warn'])
            ws3.set_row(r, 26)
            r += 1
        for rec in result.get('smart_recommendations', []):
            ws3.write(r, 0, r - 2, F['cell'])
            ws3.write(r, 1, rec, F['good'])
            ws3.set_row(r, 26)
            r += 1

        # ═══════════════════════════════════════════
        # الصفحة 4: حساسية (اختياري)
        # ═══════════════════════════════════════════
        if sensitivity and sensitivity.get('dp'):
            ws4 = wb.add_worksheet("الحساسية")
            ws4.right_to_left()
            ws4.set_column('A:C', 18)
            for j, h in enumerate(["DP %", "SE", "التكلفة $/طن"]):
                ws4.write(0, j, h, F['header'])
            for i, (dp, se, cost) in enumerate(zip(
                    sensitivity['dp'], sensitivity['se'],
                    sensitivity['cost']), start=1):
                ws4.write_number(i, 0, round(dp, 2), F['cell'])
                ws4.write_number(i, 1, round(se, 2), F['cell'])
                ws4.write_number(i, 2, round(cost, 2), F['money'])

        # ═══════════════════════════════════════════
        # الصفحة 5: مونت كارلو
        # ═══════════════════════════════════════════
        if monte_carlo:
            ws5 = wb.add_worksheet("مونت كارلو")
            ws5.right_to_left()
            ws5.set_column('A:B', 22)
            stats = [
                ("المتوسط", monte_carlo.get('mean')),
                ("الانحراف المعياري", monte_carlo.get('std')),
                ("P5 (متفائل)", monte_carlo.get('p5')),
                ("P50 (وسيط)", monte_carlo.get('p50')),
                ("P95 (متشائم)", monte_carlo.get('p95')),
                ("الحد الأدنى", monte_carlo.get('min')),
                ("الحد الأقصى", monte_carlo.get('max')),
                ("التكلفة الأساسية", monte_carlo.get('base_cost')),
            ]
            ws5.write(0, 0, "الإحصائية", F['header'])
            ws5.write(0, 1, "القيمة ($/طن)", F['header'])
            for i, (k, v) in enumerate(stats, start=1):
                ws5.write(i, 0, k, F['cell_right'])
                if v is not None:
                    ws5.write_number(i, 1, round(v, 2), F['money'])

        # ═══════════════════════════════════════════
        # الصفحة 6: باريتو
        # ═══════════════════════════════════════════
        if pareto:
            ws6 = wb.add_worksheet("باريتو")
            ws6.right_to_left()
            ws6.set_column('A:C', 18)
            for j, h in enumerate(["DP %", "SE", "التكلفة $/طن"]):
                ws6.write(0, j, h, F['header'])
            for i, pt in enumerate(pareto, start=1):
                ws6.write_number(i, 0, pt['dp'], F['cell'])
                ws6.write_number(i, 1, pt['se'], F['cell'])
                ws6.write_number(i, 2, pt['cost'], F['money'])

        # ═══════════════════════════════════════════
        # الصفحة 7: أسعار ظلية
        # ═══════════════════════════════════════════
        if shadow:
            ws7 = wb.add_worksheet("أسعار ظلية")
            ws7.right_to_left()
            ws7.set_column('A:A', 35)
            ws7.set_column('B:B', 22)
            ws7.write(0, 0, "التجربة", F['header'])
            ws7.write(0, 1, "التغير ($/طن)", F['header'])
            for i, e in enumerate(shadow.get('experiments', []), start=1):
                ws7.write(i, 0, e['name'], F['cell_right'])
                d = e.get('cost_delta')
                if d is None:
                    ws7.write(i, 1, "—", F['cell'])
                else:
                    ws7.write_number(i, 1, round(d, 2), F['money'])

        # ═══════════════════════════════════════════
        # الصفحة 8: معلومات
        # ═══════════════════════════════════════════
        ws8 = wb.add_worksheet("معلومات")
        ws8.right_to_left()
        ws8.set_column('A:A', 30)
        ws8.set_column('B:B', 50)
        ws8.merge_range('A1:B1', "🌾 تاور نولجي Tawornology v19.4",
                         F['title'])
        meta = [
            ("الحيوان", result['animal_type']),
            ("المرحلة", result['stage']),
            ("نظام البروتين", result['totals'].get('basis', 'DP')),
            ("DP القياسي", f"{result['totals']['target_DP']:.2f}%"),
            ("DP المحقق", f"{result['totals']['DP']:.2f}%"),
            ("SE القياسي", f"{result['totals']['target_SE']:.2f}"),
            ("SE المحقق", f"{result['totals']['SE']:.2f}"),
            ("التكلفة/طن", f"${result['cost_per_ton']:.2f}"),
            ("التكلفة/كجم", f"${result['cost_per_kg']:.4f}"),
            ("التاريخ", datetime.now().strftime('%Y-%m-%d %H:%M')),
        ]
        if extra_meta:
            meta.extend(list(extra_meta.items()))
        for i, (k, v) in enumerate(meta, start=2):
            ws8.write(i, 0, k, F['cell_right'])
            ws8.write(i, 1, str(v), F['cell'])

        wb.close()
        bio.seek(0)
        return bio.getvalue()


# ─────────────────────────────────────────────────────────────────────────
# 2) مدير مكتبة الخلطات (Save/Load من قاعدة البيانات)
# ─────────────────────────────────────────────────────────────────────────
class FormulaLibrary:
    """إدارة كاملة لحفظ واسترجاع الخلطات من قاعدة البيانات المعزولة."""

    @staticmethod
    def _db():
        # نستورد من الكود الرئيسي (سيكون متاحاً في السياق)
        try:
            from __main__ import get_db_manager, get_current_user_name
            return get_db_manager(), get_current_user_name()
        except Exception:
            return None, "unknown"

    @staticmethod
    def save_formula(result: dict, formula_name: str,
                     breed: str = "", requester: str = "",
                     notes: str = "") -> str:
        db, user = FormulaLibrary._db()
        if not db:
            return ""
        fid = secrets.token_hex(16)
        db.insert_record('feed_formulas', {
            'formula_id': fid,
            'formula_name': formula_name,
            'animal_type': result['animal_type'],
            'breed': breed or result['animal_type'],
            'stage': result['stage'],
            'target_dp': result['totals']['target_DP'],
            'target_se': result['totals']['target_SE'],
            'ingredients': json.dumps({
                'formula': result['formula'],
                'totals': result['totals'],
                'minerals': result['minerals'],
                'ratios': result['ratios'],
                'mineral_eval': result['mineral_eval'],
                'mf_standard': result.get('mf_standard', {}),
                'warnings': result.get('warnings', []),
                'smart_recommendations':
                    result.get('smart_recommendations', []),
                'fixed_ingredients':
                    result.get('fixed_ingredients', {}),
                'cost_per_kg': result['cost_per_kg'],
                'notes': notes,
            }, ensure_ascii=False),
            'total_cost': result['cost_per_ton'] * 1000,
            'cost_per_ton': result['cost_per_ton'],
            'created_by': user,
            'created_date': datetime.now().isoformat(),
            'is_approved': 0,
            'usage_count': 0,
            'requester_name': requester,
        })
        return fid

    @staticmethod
    def list_formulas(limit: int = 200) -> List[Dict]:
        db, _ = FormulaLibrary._db()
        if not db:
            return []
        rows = db.execute_query(
            "SELECT formula_id, formula_name, animal_type, breed, stage, "
            "cost_per_ton, created_by, created_date, requester_name, "
            "usage_count FROM feed_formulas "
            "ORDER BY created_date DESC LIMIT ?", (limit,))
        return [{
            'formula_id': r[0], 'formula_name': r[1],
            'animal_type': r[2], 'breed': r[3], 'stage': r[4],
            'cost_per_ton': r[5], 'created_by': r[6],
            'created_date': r[7], 'requester_name': r[8],
            'usage_count': r[9] if len(r) > 9 else 0,
        } for r in rows]

    @staticmethod
    def load_formula(formula_id: str) -> Optional[Dict]:
        db, _ = FormulaLibrary._db()
        if not db:
            return None
        rows = db.execute_query(
            "SELECT * FROM feed_formulas WHERE formula_id=?",
            (formula_id,))
        if not rows:
            return None
        r = rows[0]
        try:
            payload = json.loads(r[8])  # ingredients
        except Exception:
            payload = {}
        return {
            'formula_id': r[0], 'formula_name': r[1],
            'animal_type': r[2], 'breed': r[3], 'stage': r[4],
            'target_dp': r[5], 'target_se': r[6],
            'payload': payload, 'cost_per_ton': r[10],
            'created_by': r[11], 'created_date': r[12],
            'requester_name': r[15] if len(r) > 15 else "",
        }

    @staticmethod
    def delete_formula(formula_id: str) -> bool:
        db, _ = FormulaLibrary._db()
        if not db:
            return False
        db.execute_query(
            "DELETE FROM feed_formulas WHERE formula_id=?",
            (formula_id,))
        return True

    @staticmethod
    def increment_usage(formula_id: str) -> None:
        db, _ = FormulaLibrary._db()
        if not db:
            return
        db.execute_query(
            "UPDATE feed_formulas SET usage_count = "
            "COALESCE(usage_count,0) + 1 WHERE formula_id=?",
            (formula_id,))
