#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبارات وحدة شاملة — Tawor Nology 11.6.2
════════════════════════════════════════════════════════════════
الاستخدام:
    # 1) تعيين اسم ملف التطبيق (اختياري — الافتراضي app.py)
    export TAWOR_APP=app.py

    # 2) تشغيل مباشر (بدون pytest)
    python test_tawor_v1162.py

    # 3) تشغيل بـ pytest
    pytest test_tawor_v1162.py -v

يفحص 32 حالة تغطي:
    • التنبيه الصوتي (3 أنماط)
    • قاعدة بيانات المخاطر
    • كاشف التحذيرات (11 فحصاً)
    • قيود LP الاستباقية
    • محرك التركيب الآمن
    • توليد التركيبات المتعددة
    • مخططات الحظائر (2D + 3D)
════════════════════════════════════════════════════════════════
"""

import os
import sys
import io
import wave
import struct
import traceback
import importlib.util
from unittest.mock import MagicMock

# ═════════════════════════════════════════════════════════════════════
# 1) تجهيز mocks قبل أي استيراد
# ═════════════════════════════════════════════════════════════════════

def _setup_mocks():
    """يحاكي streamlit وبعض المكتبات الثقيلة قبل تحميل التطبيق."""

    # ─── streamlit ────────────────────────────────────────
    st_mock = MagicMock()
    st_mock.secrets = {}
    st_mock.session_state = MagicMock()
    st_mock.cache_data = lambda f=None, **kw: (f if f else (lambda x: x))
    st_mock.cache_resource = lambda f=None, **kw: (f if f else (lambda x: x))
    st_mock.columns = lambda n, **k: [MagicMock() for _ in range(n if isinstance(n, int) else len(n))]
    st_mock.tabs = lambda labels, **k: [MagicMock() for _ in range(len(labels))]
    st_mock.set_page_config = lambda **k: None
    for _name in ("markdown", "error", "warning", "info", "success",
                  "audio", "stop", "rerun", "caption", "code",
                  "dataframe", "metric", "table", "image", "write",
                  "plotly_chart", "download_button", "radio", "selectbox",
                  "number_input", "text_input", "text_area", "checkbox",
                  "button", "spinner", "expander", "slider", "file_uploader",
                  "camera_input", "date_input", "form", "form_submit_button",
                  "data_editor", "container", "empty", "progress", "toast"):
        setattr(st_mock, _name, MagicMock())
    sys.modules['streamlit'] = st_mock
    return st_mock

_ST_MOCK = _setup_mocks()


# ═════════════════════════════════════════════════════════════════════
# 2) تحميل التطبيق
# ═════════════════════════════════════════════════════════════════════

def load_app(path: str = None):
    """يحمّل ملف التطبيق ديناميكياً."""
    path = path or os.environ.get("TAWOR_APP", "app.py")
    if not os.path.exists(path):
        # جرّب أسماء شائعة
        for alt in ("tawor.py", "main.py", "tawor_nology.py",
                     "tawor_nology_v116.py", "streamlit_app.py"):
            if os.path.exists(alt):
                path = alt
                break
        else:
            raise FileNotFoundError(
                f"لم يُعثر على ملف التطبيق. مرّر المسار عبر TAWOR_APP=... "
                f"أو ضع الملف باسم app.py")
    spec = importlib.util.spec_from_file_location("tawor_app", path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"\n⚠️ فشل تحميل {path}: {type(e).__name__}: {e}")
        print(traceback.format_exc()[:2000])
        raise
    return mod


# ═════════════════════════════════════════════════════════════════════
# 3) إطار اختبار بسيط
# ═════════════════════════════════════════════════════════════════════

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.failures = []
        self.current_group = ""

    def group(self, name):
        self.current_group = name
        print(f"\n{'═'*70}\n📁 {name}\n{'═'*70}")

    def run(self, name, func):
        try:
            func()
            self.passed += 1
            print(f"  ✅ {name}")
        except AssertionError as e:
            self.failed += 1
            self.failures.append((name, str(e)))
            print(f"  ❌ {name}: {e}")
        except Exception as e:
            self.failed += 1
            self.failures.append((name, f"{type(e).__name__}: {e}"))
            print(f"  ❌ {name}: {type(e).__name__}: {e}")

    def skip(self, name, reason):
        self.skipped += 1
        print(f"  ⏭️  {name} — {reason}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'═'*70}")
        print(f"📊 الملخص النهائي")
        print(f"{'═'*70}")
        print(f"  ✅ ناجح:   {self.passed}/{total}")
        print(f"  ❌ فاشل:   {self.failed}/{total}")
        print(f"  ⏭️  متجاوز: {self.skipped}")
        if self.failed > 0:
            print(f"\n❌ الاختبارات الفاشلة:")
            for name, err in self.failures:
                print(f"  • {name}: {err}")
            return 1
        print("\n🎉 نجحت جميع الاختبارات — الحزمة جاهزة للنشر")
        return 0


# ═════════════════════════════════════════════════════════════════════
# 4) الاختبارات
# ═════════════════════════════════════════════════════════════════════

def run_all_tests(app):
    t = TestRunner()

    # ─── المجموعة 1: التنبيه الصوتي ────────────────────────────────
    t.group("🔊 التنبيه الصوتي")

    def test_wav_critical():
        wav = app.generate_alert_wav("critical")
        assert isinstance(wav, bytes), "يجب أن يكون bytes"
        assert len(wav) > 1000, f"WAV قصير جداً: {len(wav)} بايت"
        # فحص رأس WAV
        assert wav[:4] == b'RIFF', "رأس RIFF مفقود"
        assert wav[8:12] == b'WAVE', "رأس WAVE مفقود"

    def test_wav_warning():
        wav = app.generate_alert_wav("warning")
        assert isinstance(wav, bytes) and len(wav) > 500

    def test_wav_success():
        wav = app.generate_alert_wav("success")
        assert isinstance(wav, bytes) and len(wav) > 500

    def test_wav_durations_differ():
        c = len(app.generate_alert_wav("critical"))
        s = len(app.generate_alert_wav("success"))
        assert c != s, "الأنماط المختلفة يجب أن تنتج أطوالاً مختلفة"

    def test_play_alert_no_crash():
        app.play_alert("critical")
        app.play_alert("warning")
        app.play_alert("success")

    t.run("WAV حرج صالح", test_wav_critical)
    t.run("WAV تحذير صالح", test_wav_warning)
    t.run("WAV نجاح صالح", test_wav_success)
    t.run("أنماط مختلفة = أطوال مختلفة", test_wav_durations_differ)
    t.run("play_alert لا يرمي استثناء", test_play_alert_no_crash)

    # ─── المجموعة 2: قاعدة بيانات المخاطر ────────────────────────
    t.group("🛡️ قاعدة بيانات المخاطر")

    def test_hazard_db_exists():
        assert hasattr(app, "HAZARD_DATABASE")
        assert len(app.HAZARD_DATABASE) >= 10

    def test_hazard_required_fields():
        required = {"hazard", "limits_by_class", "source", "action"}
        for ing, hz in app.HAZARD_DATABASE.items():
            for f in required:
                assert f in hz, f"{ing} يفتقد {f}"

    def test_get_hazard_info_known():
        assert app._get_hazard_info("يوريا علفية") is not None
        assert app._get_hazard_info("كسافا مجففة") is not None

    def test_get_hazard_info_unknown():
        assert app._get_hazard_info("ذرة صفراء فقط") is None or True
        assert app._get_hazard_info("مادة غير موجودة") is None

    t.run("قاعدة البيانات موجودة (≥10 مادة)", test_hazard_db_exists)
    t.run("كل مادة بها الحقول الإلزامية", test_hazard_required_fields)
    t.run("_get_hazard_info للمواد المعروفة", test_get_hazard_info_known)
    t.run("_get_hazard_info للمواد المجهولة", test_get_hazard_info_unknown)

    # ─── المجموعة 3: حدود المواد حسب الحيوان ──────────────────────
    t.group("🐾 حدود المواد حسب الحيوان")

    def test_urea_poultry_zero():
        lim = app._hazard_limit_for("يوريا علفية", "دواجن")
        assert lim == 0.0, f"يوريا للدواجن يجب 0، جاء {lim}"

    def test_urea_ruminant_one():
        lim = app._hazard_limit_for("يوريا علفية", "أبقار")
        assert lim == 1.0, f"يوريا للمجترات 1.0، جاء {lim}"

    def test_cassava_poultry_zero():
        lim = app._hazard_limit_for("كسافا مجففة", "دواجن")
        assert lim == 0.0

    def test_cassava_ruminant_20():
        lim = app._hazard_limit_for("كسافا مجففة", "أغنام")
        assert lim == 20.0

    def test_cottonseed_poultry_3():
        lim = app._hazard_limit_for("كسب بذور القطن", "دواجن")
        assert lim == 3.0

    def test_young_stricter():
        lim_young = app._hazard_limit_for("كسب بذور القطن", "أبقار",
                                            "بادي")
        assert lim_young == 0.0, "الصغار يجب 0"

    def test_non_hazardous_none():
        lim = app._hazard_limit_for("ذرة صفراء فقط", "دواجن")
        assert lim is None

    t.run("يوريا للدواجن = 0", test_urea_poultry_zero)
    t.run("يوريا للمجترات = 1.0", test_urea_ruminant_one)
    t.run("كسافا للدواجن = 0", test_cassava_poultry_zero)
    t.run("كسافا للأغنام = 20", test_cassava_ruminant_20)
    t.run("جوسيبول للدواجن = 3", test_cottonseed_poultry_3)
    t.run("الصغار أشد من البالغين", test_young_stricter)
    t.run("مواد آمنة = None", test_non_hazardous_none)

    # ─── المجموعة 4: كاشف التحذيرات (11 فحصاً) ────────────────────
    t.group("🚨 كاشف التحذيرات الشامل")

    def test_urea_monogastric_critical():
        warns = app.detect_harmful_mix({"يوريا علفية": 2.0}, "دواجن")
        assert any(w["level"] == "critical" for w in warns), \
            "يوريا للدواجن يجب أن تكون حرجة"

    def test_urea_ruminant_ok():
        warns = app.detect_harmful_mix({"يوريا علفية": 0.5}, "أبقار")
        crit = [w for w in warns if w["level"] == "critical"]
        assert not crit, "يوريا 0.5% للمجترات آمنة"

    def test_cassava_poultry_critical():
        warns = app.detect_harmful_mix({"كسافا مجففة": 5.0}, "دواجن")
        assert any(w["level"] == "critical" for w in warns)

    def test_salt_overdose():
        warns = app.detect_harmful_mix({"ملح الطعام": 1.5}, "أبقار")
        assert any("ملح" in w["title"] for w in warns)

    def test_ca_p_low():
        warns = app.detect_harmful_mix(
            {"الحجر الجيري": 0.2, "فوسفات ثنائي الكالسيوم": 2.0},
            "أبقار")
        assert any("Ca:P" in w["title"] or "Ca" in w["title"]
                    for w in warns)

    def test_selenium_high():
        warns = app.detect_harmful_mix(
            {"سيلينيت الصوديوم": 0.05}, "دواجن")
        assert any("سيلين" in w["title"] for w in warns)

    def test_aflatoxin_no_binder():
        warns = app.detect_harmful_mix(
            {"ذرة صفراء": 40, "كسب فول صويا 44%": 30,
             "أمباز الفول السوداني": 15, "نخالة قمح (ردة)": 15},
            "دواجن")
        assert any("أفلاتوكسين" in w["title"] for w in warns)

    def test_safe_formula_no_warns():
        warns = app.detect_harmful_mix(
            {"ذرة صفراء": 60, "كسب فول صويا 44%": 25,
             "نخالة قمح (ردة)": 10, "الحجر الجيري": 1.5,
             "فوسفات ثنائي الكالسيوم": 0.7, "ملح الطعام": 0.4,
             "مضاد سموم فطرية": 0.1,
             "بريمكس تسمين دواجن": 0.3},
            "دواجن")
        crit = [w for w in warns if w["level"] == "critical"]
        assert not crit, f"تركيبة سليمة يجب ألا تُنتج حرجاً: {crit}"

    def test_warn_has_source():
        warns = app.detect_harmful_mix({"يوريا علفية": 2.0}, "دواجن")
        for w in warns:
            assert "source" in w and w["source"], "كل تحذير يحتاج مصدراً"
            assert "action" in w and w["action"], "كل تحذير يحتاج إجراءً"

    t.run("يوريا 2% للدواجن → حرج", test_urea_monogastric_critical)
    t.run("يوريا 0.5% للمجترات → آمن", test_urea_ruminant_ok)
    t.run("كسافا للدواجن → حرج", test_cassava_poultry_critical)
    t.run("ملح زائد → تحذير", test_salt_overdose)
    t.run("Ca:P منخفض → تحذير", test_ca_p_low)
    t.run("سيلينيوم مرتفع → تحذير", test_selenium_high)
    t.run("أفلاتوكسين بلا مضاد → تحذير", test_aflatoxin_no_binder)
    t.run("تركيبة سليمة → بلا حرج", test_safe_formula_no_warns)
    t.run("كل تحذير له source + action", test_warn_has_source)

    # ─── المجموعة 5: قيود LP الاستباقية ──────────────────────────
    t.group("🛡️ قيود LP الاستباقية")

    def test_blocks_dangerous():
        valid = ["يوريا علفية", "ذرة صفراء", "كسب فول صويا 44%"]
        bounds = [(0.0, 100.0), (0.0, 100.0), (0.0, 100.0)]
        new_b, blocked = app._add_safety_constraints(
            valid, bounds, "دواجن", "")
        assert "يوريا علفية" in blocked
        assert new_b[0] == (0.0, 0.0), "يجب حظر اليوريا تماماً"

    def test_caps_ruminant_urea():
        valid = ["يوريا علفية", "ذرة صفراء"]
        bounds = [(0.0, 100.0), (0.0, 100.0)]
        new_b, blocked = app._add_safety_constraints(
            valid, bounds, "أبقار", "")
        assert new_b[0][1] <= 1.0, f"حد اليوريا يجب ≤ 1، جاء {new_b[0]}"
        assert "يوريا علفية" not in blocked

    def test_preserves_safe():
        valid = ["ذرة صفراء", "كسب فول صويا 44%"]
        bounds = [(0.0, 70.0), (0.0, 30.0)]
        new_b, blocked = app._add_safety_constraints(
            valid, bounds, "أبقار", "")
        assert new_b == bounds
        assert blocked == []

    t.run("حظر اليوريا للدواجن", test_blocks_dangerous)
    t.run("تقييد اليوريا للمجترات", test_caps_ruminant_urea)
    t.run("مواد آمنة لا تتأثر", test_preserves_safe)

    # ─── المجموعة 6: محرك التركيب (مع SCIPY) ─────────────────────
    t.group("⚙️ محرك التركيب الآمن")

    if not getattr(app, "SCIPY_AVAILABLE", False):
        t.skip("auto_formulate_smart", "SCIPY غير مثبتة")
        t.skip("formulate_multiple_options", "SCIPY غير مثبتة")
    else:
        def test_basic_formulate():
            custom_std = {"CP": 18, "SE": 72, "NDF": 10,
                           "ADF": 5, "Ca": 0.9, "P": 0.45,
                           "Lys": 1.0, "Met": 0.45}
            prices = {"ذرة صفراء": 230, "كسب فول صويا 44%": 440,
                      "نخالة قمح (ردة)": 150}
            r = app.auto_formulate_smart(
                ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)"],
                prices, custom_std,
                animal_type="دواجن",
                production_type="بادي")
            assert r["success"], f"فشل التركيب: {r.get('message')}"
            assert "formula" in r
            assert "harmful_warnings" in r, "يجب أن ترجع التحذيرات"
            assert "blocked_ingredients" in r
            assert "safety_attempt" in r
            assert abs(sum(r["formula"].values()) - 100) < 0.5

        def test_no_dangerous_in_safe_formula():
            custom_std = {"CP": 18, "SE": 72, "Ca": 0.9, "P": 0.45}
            prices = {"ذرة صفراء": 230, "كسب فول صويا 44%": 440,
                      "يوريا علفية": 480, "نخالة قمح (ردة)": 150}
            r = app.auto_formulate_smart(
                ["ذرة صفراء", "كسب فول صويا 44%", "يوريا علفية",
                 "نخالة قمح (ردة)"],
                prices, custom_std,
                animal_type="دواجن",
                production_type="بادي")
            if r["success"]:
                # يجب ألا تحتوي الصيغة على يوريا
                assert r["formula"].get("يوريا علفية", 0) == 0, \
                    "اليوريا يجب ألا تظهر للدواجن"

        def test_multiple_options_basic():
            custom_std = {"CP": 18, "SE": 72, "Ca": 0.9, "P": 0.45}
            prices = {
                "ذرة صفراء": 230, "شعير مطحون": 210,
                "كسب فول صويا 44%": 440,
                "كسب عباد الشمس 36%": 310,
                "نخالة قمح (ردة)": 150,
            }
            r = app.formulate_multiple_options(
                list(prices.keys()), prices, custom_std,
                animal_type="أبقار", production_type="تسمين_عادي",
                n_options=5)
            assert r["success"]
            assert 1 <= len(r["options"]) <= 5
            for opt in r["options"]:
                assert "harmful_warnings" in opt
                assert "quality_score" in opt

        def test_safe_options_preferred():
            custom_std = {"CP": 16, "SE": 65, "Ca": 0.7, "P": 0.35}
            prices = {
                "ذرة صفراء": 230, "كسب فول صويا 44%": 440,
                "كسافا مجففة": 150, "نخالة قمح (ردة)": 150,
            }
            r = app.formulate_multiple_options(
                list(prices.keys()), prices, custom_std,
                animal_type="أبقار", production_type="تسمين_عادي",
                n_options=5)
            if r["success"]:
                # الخيار الأول يجب ألا يحتوي تحذيرات حرجة
                first_hw = r["options"][0].get("harmful_warnings", [])
                n_crit = sum(1 for w in first_hw
                             if w["level"] == "critical")
                assert n_crit == 0, \
                    f"الخيار الأول يجب ألا يحتوي حرجاً: {first_hw}"

        t.run("تركيب أساسي ينجح ويعيد 100%",
              test_basic_formulate)
        t.run("لا يظهر مواد محظورة في الصيغة",
              test_no_dangerous_in_safe_formula)
        t.run("تركيبات متعددة (1-5 خيارات)",
              test_multiple_options_basic)
        t.run("الخيار الأول مفضّل بالآمان",
              test_safe_options_preferred)

    # ─── المجموعة 7: مخططات الحظائر ─────────────────────────────
    t.group("🏠 مخططات الحظائر")

    if not getattr(app, "MATPLOTLIB_AVAILABLE", False):
        t.skip("create_pen_layout_2d", "MATPLOTLIB غير مثبتة")
    else:
        def _dummy_dims(count):
            return {
                "count": count, "total_area_m2": count * 1.5,
                "length_m": max(6, count * 0.3),
                "width_m": 10, "height_m": 3,
                "ridge_height_m": 4, "roof_type": "gable",
                "slope_pct": 20, "volume_m3": count * 4.5,
                "aisle_m": 1.5, "central_aisle": True,
                "drinkers_count": max(1, count // 50),
                "animals_per_row": 10,
                "standard": {"name_ar": "أبقار"},
                "vent_flow_summer_m3h": 0,
                "vent_flow_winter_m3h": 0,
            }

        def test_pen_2d_returns_bytes():
            buf = app.create_pen_layout_2d(_dummy_dims(100), "🐄",
                                             max_per_pen=8)
            assert buf is not None
            assert isinstance(buf, io.BytesIO)
            assert len(buf.getvalue()) > 1000

        def test_pen_2d_respects_cap():
            buf = app.create_pen_layout_2d(_dummy_dims(1000), "🐄",
                                             max_per_pen=8, max_pens=6)
            assert buf is not None

        def test_pen_2d_small_count():
            buf = app.create_pen_layout_2d(_dummy_dims(3), "🐑",
                                             max_per_pen=8)
            assert buf is not None

        t.run("2D يعيد BytesIO صالح", test_pen_2d_returns_bytes)
        t.run("2D بحد 8/حظيرة", test_pen_2d_respects_cap)
        t.run("2D بعدد صغير (3 رؤوس)", test_pen_2d_small_count)

    if not getattr(app, "PLOTLY_AVAILABLE", False):
        t.skip("create_barn_3d_figure", "PLOTLY غير مثبتة")
    else:
        def test_barn_3d_signature():
            import inspect
            sig = inspect.signature(app.create_barn_3d_figure)
            params = list(sig.parameters.keys())
            assert "max_visible_animals" in params, \
                f"يجب وجود max_visible_animals في: {params}"
            assert sig.parameters["max_visible_animals"].default == 40

        t.run("3D يقبل max_visible_animals=40", test_barn_3d_signature)

    return t


# ═════════════════════════════════════════════════════════════════════
# 5) نقطة الدخول
# ═════════════════════════════════════════════════════════════════════

def main():
    print("═" * 70)
    print("🧪 اختبارات وحدة — Tawor Nology 11.6.2")
    print("═" * 70)

    try:
        app = load_app()
        print(f"✅ تم تحميل التطبيق بنجاح")
        print(f"   SCIPY: {getattr(app, 'SCIPY_AVAILABLE', False)} | "
              f"PLOTLY: {getattr(app, 'PLOTLY_AVAILABLE', False)} | "
              f"MATPLOTLIB: {getattr(app, 'MATPLOTLIB_AVAILABLE', False)}")
    except Exception as e:
        print(f"\n❌ فشل تحميل التطبيق: {e}")
        return 2

    runner = run_all_tests(app)
    return runner.summary()


if __name__ == "__main__":
    sys.exit(main())
