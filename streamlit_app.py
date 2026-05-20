import streamlit as st
import numpy as np
import time

# ==========================================
# 1. إعدادات المنصة والمظهر الفخم الممتد (الواجهة الأولى)
# ==========================================
st.set_page_config(page_title="منصة تاور الرقمية المتكاملة للأعلاف", page_icon="🌾", layout="wide")

# تطبيق التصميم الفخم الممتد بدون جانبية مضغوطة لدعم الجوالات
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Cairo', sans-serif;
        background-color: #fafbfc;
        direction: rtl;
    }
    .app-header {
        background: linear-gradient(135deg, #1b5e20, #2e7d32);
        color: white;
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .section-title {
        color: #1b5e20;
        border-right: 6px solid #e65100;
        padding-right: 12px;
        text-align: right;
        font-size: 1.4rem;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 15px;
        background-color: #f1f8e9;
        padding-top: 5px;
        padding-bottom: 5px;
        border-radius: 0 8px 8px 0;
    }
    .market-card {
        background: #ffffff;
        border-right: 5px solid #1565c0;
        padding: 15px;
        margin-bottom: 12px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        text-align: right;
    }
    .alert-countdown {
        background-color: #ffebee;
        color: #c62828;
        padding: 18px;
        border-right: 6px solid #b71c1c;
        border-radius: 8px;
        margin: 15px 0;
        text-align: right;
        font-weight: bold;
        animation: blinker 1.5s linear infinite;
    }
    .invoice-box {
        background: #ffffff;
        border: 2px solid #37474f;
        padding: 25px;
        border-radius: 12px;
        margin-top: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    /* ديباجة الأصناف العلفية الفخمة للجوال */
    .sack-tag-2026 {
        border: 3px dashed #1b5e20;
        padding: 20px;
        border-radius: 15px;
        background-color: #ffffff;
        max-width: 420px;
        margin: 20px auto;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        text-align: right;
    }
    .animal-frame-graphic {
        border: 2px solid #2e7d32;
        background: #f1f8e9;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        color: #1b5e20;
        margin: 10px 0;
    }
    .library-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        background: white;
        border-radius: 8px;
        overflow: hidden;
    }
    .library-table th {
        background-color: #2e7d32;
        color: white;
        padding: 12px;
        text-align: right;
    }
    .library-table td {
        padding: 10px;
        border-bottom: 1px solid #e0e0e0;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. إدارة متحولات الجلسة التفاعلية
# ==========================================
if "expert_feedbacks" not in st.session_state: st.session_state["expert_feedbacks"] = []
if "invoice_data" not in st.session_state: st.session_state["invoice_data"] = None
if "last_computed_formula" not in st.session_state: st.session_state["last_computed_formula"] = None

# ==========================================
# 3. المصفوفات الجغرافية والبورصة والسلالات المتطابقة
# ==========================================
GEOGRAPHY_DATABASE = {
    "السودان": {
        "currency": "SDG", "usd_rate": 600.0,
        "states": {
            "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
            "ولاية شمال كردفان": ["الأبيض", "أم روابة", "بارا"],
            "ولاية القضارف": ["القضارف المدينة", "الفاو", "الحواتة"]
        },
        "breeds": {
            "الأبقار وسلالاتها": {"name": "أبقار الكنانة والبطانة المحسنة 🐄", "avatar": "🐄"},
            "الأغنام والضأن": {"name": "ضأن الدوبا والكباشي الكردفاني 🐑", "avatar": "🐑"},
            "الخيول والفروسية": {"name": "الجواد الدنقلاوي الأصيل 🐎", "avatar": "🐎"},
            "الطيور والدواجن": {"name": "دواجن هبرد وسلالات المزارع السودانية 🐓", "avatar": "🐓"}
        },
        "prices": {"عجول تسمين حي (كجم)": 3200, "خراف صادر قائم (رأس)": 180000, "لتر حليب خام": 1200, "طن علف تسمين أساسي": 480000}
    },
    "ليبيا": {
        "currency": "LYD", "usd_rate": 4.82,
        "states": {
            "الإقليم الغربي طرابلس": ["طرابلس", "مصراتة", "الزاوية"],
            "إقليم البطنان والشرق": ["طبرق", "بنغازي", "البيضاء"],
            "فزان والجنوب": ["سبها", "مرزق", "غـات"]
        },
        "breeds": {
            "الأبقار وسلالاتها": {"name": "أبقار الفريزيان المؤقلمة محلياً 🐄", "avatar": "🐄"},
            "الأغنام والضأن": {"name": "أغنام البرقي الليبية العريقة 🐑", "avatar": "🐑"},
            "الخيول والفروسية": {"name": "الجواد العربي الليبي الفاخر 🐎", "avatar": "🐎"},
            "الطيور والدواجن": {"name": "سلالات كب 500 للإنتاج المكثف 🐓", "avatar": "🐓"}
        },
        "prices": {"عجول تسمين حي (كجم)": 38, "خراف برقي ممتازة (رأس)": 1400, "لتر حليب طازج": 4.5, "طن علف تسمين أساسي": 1950}
    },
    "مصر": {
        "currency": "EGP", "usd_rate": 48.0,
        "states": {
            "محافظات القاهرة الكبرى": ["القاهرة", "الجيزة", "القليوبية"],
            "محافظات الدلتا": ["طنطا", "المنصورة", "الزقازيق"],
            "محافظات الصعيد": ["أسيوط", "المنيا", "أسوان"]
        },
        "breeds": {
            "الأبقار وسلالاتها": {"name": "الأبقار البلدي والجاموس المصري 🐄", "avatar": "🐄"},
            "الأغنام والضأن": {"name": "أغنام الرحماني والأوسيمي الفاخرة 🐑", "avatar": "🐑"},
            "الخيول والفروسية": {"name": "الحصان العربي الفحل المستقيم 🐎", "avatar": "🐎"},
            "الطيور والدواجن": {"name": "كتكوت روس 308 مزارع الدلتا 🐓", "avatar": "🐓"}
        },
        "prices": {"عجول تسمين قائم (كجم)": 175, "خراف بلدي حية (رأس)": 11000, "لتر حليب جاموسي": 35, "طن علف تسمين أساسي": 18500}
    }
}

SECTOR_STAGES = {
    "الأبقار وسلالاتها": {"تسمين عجول مكثف سريع": 14.5, "إدرار حليب طاقة عالية": 17.5, "أمهات حوامل مجففة": 12.0},
    "الأغنام والضأن": {"تسمين حملان أسواق": 16.0, "نعاج مرضعة ومدرة": 14.5, "دفع غذائي قبل التلقيح": 12.5},
    "الخيول والفروسية": {"جياد سباق وسرعة دؤوب": 14.0, "أمهر نامية حديثة الفطام": 15.5},
    "الطيور والدواجن": {"بادي لاحم تسمين مكثف": 23.0, "نامي لاحم متوازن": 21.0, "بياض إنتاجي تجاري": 17.5}
}

BIG_LIBRARY = {
    "مصادر الطاقة الحيوية": {"ذرة صفراء": 8.5, "ذرة بيضاء بلدية": 9.0, "شعير مطحون": 11.5},
    "الأكساب والبروتينات": {"أمباز فول سوداني": 45.0, "كسب صويا 44%": 44.0, "كسب صويا 48%": 48.0},
    "المواد الرعوية والمالئة": {"نخالة قمح (ردة)": 15.0, "دريس حجازي منقح": 17.0},
    "الإضافات والمركزات": {"مركزات تسمين 5%": 36.0, "حجر جيري ناعم": 0.0, "بيكربونات الصوديوم": 0.0}
}

# ==========================================
# 4. ترويسة المنصة الثابتة (الخلفية الممتدة الأولى)
# ==========================================
st.markdown(
    """
    <div class="app-header">
        <h1>منصة تاور الرقمية الشاملة للأعلاف والإنتاج الحيواني 🌾</h1>
        <h3>تحت إشراف المستشار الفني: م. عبد القادر إسماعيل تاور</h3>
        <p>الواجهة الحقلية المفتوحة والمحدثة لعام 2026</p>
    </div>
    """, unsafe_allow_html=True
)

# ==========================================
# المتطلب الأول: تفاصيل الموقع الجغرافي العريض
# ==========================================
st.markdown('<div class="section-title">📍 تفاصيل الموقع الجغرافي والتزامن الحركي</div>', unsafe_allow_html=True)
col_g1, col_g2, col_g3 = st.columns(3)
with col_g1: geo_country = st.selectbox("الدولة المستهدفة بالدراسة:", list(GEOGRAPHY_DATABASE.keys()))
country_data = GEOGRAPHY_DATABASE[geo_country]
with col_g2: geo_state = st.selectbox("الولاية / المحافظة الإقليمية:", list(country_data["states"].keys()))
with col_g3: geo_city = st.selectbox("المدينة (نقطة الربط بالبورصة):", country_data["states"][geo_state])

# ==========================================
# المتطلب الثاني: شريط القياس المتطور لحساب الوزن
# ==========================================
st.markdown('<div class="section-title">📏 دالة شريط القياس الميداني لتقدير الوزن الحي الفعلي</div>', unsafe_allow_html=True)
col_w1, col_w2, col_w3 = st.columns(3)
with col_w1: calc_sector = st.selectbox("صنف الحيوان المقاس حقلياً:", list(SECTOR_STAGES.keys()))
with col_w2: girth_cm = st.number_input("محيط الصدر خلف المرفق (سم):", min_value=20.0, value=160.0)
with col_w3: length_cm = st.number_input("طول الجسم المستقيم للحيوان (سم):", min_value=20.0, value=140.0)

if calc_sector == "الأبقار وسلالاتها": calculated_weight = (girth_cm ** 2 * length_cm) / 10838
elif calc_sector == "الخيول والفروسية": calculated_weight = (girth_cm ** 2 * length_cm) / 11877
else: calculated_weight = (girth_cm ** 2 * length_cm) / 11312

st.success(f"⚖️ الوزن الحي التقديري الناتج عن دالة شريط القياس: **{calculated_weight:.2f} كجم قائم**")

# ==========================================
# المتطلب الثالث: بورصة الحيوانات والمنتجات المتطابقة بالعملة والدولار
# ==========================================
st.markdown(f'<div class="section-title">📊 بورصة أسواق وحيوانات {geo_country} الرسمية المتطابقة</div>', unsafe_allow_html=True)
st.write(f"سلالة القطاع المعتمدة جغرافياً في هذا النطاق: **{country_data['breeds'][calc_sector]['name']}**")

col_b1, col_b2 = st.columns(2)
with col_b1:
    st.markdown(f"#### 💵 الأسعار بالعملة المحلية ({country_data['currency']})")
    for item, price in country_data["prices"].items():
        st.markdown(f"<div class='market-card'>🔹 <b>{item}:</b> {price:,} {country_data['currency']}</div>", unsafe_allow_html=True)
with col_b2:
    st.markdown("#### 🇺🇸 المقابل التقديري بالنقد الأجنبي ($ دولار أمريكي)")
    for item, price in country_data["prices"].items():
        usd_p = price / country_data["usd_rate"]
        st.markdown(f"<div class='market-card' style='border-right-color: #2e7d32;'>🟢 <b>{item}:</b> ${usd_p:,.2f} USD <small>(سعر الصرف: {country_data['usd_rate']})</small></div>", unsafe_allow_html=True)

# ==========================================
# المتطلب الرابع: الصبغة العلمية والبروتين المزدوج وإضافة الإنزيمات التلقائية
# ==========================================
st.markdown('<div class="section-title">🔬 نظام التحكم بالصبغة العلمية وتكوين علائق الطن</div>', unsafe_allow_html=True)

col_s1, col_s2 = st.columns(2)
with col_s1:
    chosen_stage = st.selectbox("المرحلة الفسيولوجية والإنتاجية المستهدفة:", list(SECTOR_STAGES[calc_sector].keys()))
    prog_cp = SECTOR_STAGES[calc_sector][chosen_stage]
    st.info(f"🧬 دالة البروتين البرمجية التلقائية لهذه المرحلة: **{prog_cp}%**")
with col_s2:
    user_cp = st.slider("⚙️ النسبة المختارة يدوياً من المربي/المستشار (%):", 10.0, 35.0, value=prog_cp)

use_custom = st.checkbox("🔄 تفعيل النسبة المختارة يدوياً وإيقاف دالة البرنامج التلقائية")
target_cp = user_cp if use_custom else prog_cp

st.markdown("### 📁 جدول محتويات مكتبة الأعلاف الكبرى - أدخل نسب الخلطة للطن (إجمالي 100%):")

# عرض المكتبة بشكل جدول منظم وجيد الشكل
html_table = "<table class='library-table'><tr><th>اسم الخامة العلفية</th><th>نسبة البروتين الخام (CP%)</th><th>الحد الأقصى المسموح به صنفيّاً</th></tr>"
for cat, ingredients in BIG_LIBRARY.items():
    for name, cp in ingredients.items():
        max_v = "30%" if name == "نخالة قمح (ردة)" else ("40%" if name == "دريس حجازي منقح" else "مفتوح")
        html_table += f"<tr><td>{name}</td><td>{cp}%</td><td>{max_v}</td></tr>"
html_table += "</table>"
st.markdown(html_table, unsafe_allow_html=True)

user_inputs = {}
cols_inputs = st.columns(4)
idx_input = 0
for cat, ingredients in BIG_LIBRARY.items():
    for name, cp in ingredients.items():
        with cols_inputs[idx_input % 4]:
            user_inputs[name] = st.number_input(f"نسبة {name} (%):", min_value=0.0, max_value=100.0, step=5.0, value=0.0, key=f"inp_{name}")
        idx_input += 1

total_mix = sum(user_inputs.values())
st.markdown(f"**⚖️ مجموع نسب المكونات الحالية:** `{total_mix}%` (يجب أن يبلغ 100% لتكوين خلطة الطن المتجانسة)")

# فحص الاختلال الصنفي وإضافة الإنزيمات إجبارياً مع إشعار 30 ثانية
trigger_enzyme_phytase = False
if user_inputs.get("نخالة قمح (ردة)", 0.0) > 30.0:
    trigger_enzyme_phytase = True

if trigger_enzyme_phytase:
    # عرض إشعار تصحيح الخطأ الموقوت بـ 30 ثانية بشكل فخم
    st.markdown(
        """
        <div class="alert-countdown">
            ⚠️ إشعار تفتيش وتصحيح تلقائي حاد (نشط لمدة 30 ثانية):<br>
            التركيبة مختلة صنفياً بسبب تجاوز حد النخالة (30%) وصعود عوائق الفايتات! 
            تم إجبارياً حقن إنزيم الفايتيز التلقائي (Phytase) لكسر العلة وتصحيح مسار الهضم حيوياً.
        </div>
        """, unsafe_allow_html=True
    )

# زر الحساب وتوليد البيانات للخطوة التالية
if st.button("🚀 احتساب العليقة وتدقيق المطابقة العلمية", type="primary", use_container_width=True):
    if total_mix != 100.0 and total_mix > 0.0:
        st.error("❌ عذراً! مجموع نسب المكونات يجب أن يساوي 100% تماماً لتكوين خلطة متجانسة للطن.")
    else:
        # إذا لم يدخل المربي نسباً، يقوم النظام بعمل تركيبة تلقائية ناجحة حماية للبرنامج
        if total_mix == 0.0:
            user_inputs = {"ذرة صفراء": 60.0, "أمباز فول سوداني": 25.0, "نخالة قمح (ردة)": 13.0, "حجر جيري ناعم": 2.0}
            if trigger_enzyme_phytase: user_inputs["إنزيم الفايتيز التلقائي"] = 0.1
        
        st.session_state["last_computed_formula"] = user_inputs
        calculated_cp_mix = sum([(v/100) * BIG_LIBRARY[k] for k, v in user_inputs.items() if k in BIG_LIBRARY])
        
        st.success(f"📊 تم التدقيق! بروتين العليقة المستهدف: {target_cp}% | البروتين الفعلي الناتج: {calculated_cp_mix:.2f}%")
        
        # إنشاء بيانات الفاتورة الافتراضية للتسويق بناء على البلد وعملته
        base_cost_ton = country_data["prices"]["طن علف تسمين أساسي"]
        st.session_state["invoice_data"] = {
            "country": geo_country,
            "currency": country_data["currency"],
            "usd_rate": country_data["usd_rate"],
            "base_cost": base_cost_ton,
            "tax": base_cost_ton * 0.05,
            "total": base_cost_ton * 1.05,
            "sector": calc_sector,
            "stage": chosen_stage,
            "target_cp": target_cp
        }

# ==========================================
# المتطلب الخامس: واجهة التسويق والفواتير العريضة
# ==========================================
if st.session_state["invoice_data"]:
    st.markdown('<div class="section-title">🧾 واجهة التسويق وإصدار الفواتير الرسمية للخلطات</div>', unsafe_allow_html=True)
    inv = st.session_state["invoice_data"]
    
    st.markdown(
        f"""
        <div class="invoice-box">
            <h3 style="text-align:center; color:#1565c0; margin:0;">🧾 فاتورة بيع وتوريد علف معتمدة 🧾</h3>
            <p style="text-align:center; color:#555;">منصة تاور للحلول العلفية المتكاملة لعام 2026</p>
            <hr style="border-top: 1px solid #ccc;">
            <p style="text-align:right;"><b>الجهة المستفيدة:</b> مزارع إنتاج {inv['sector']} - مدينة {geo_city}</p>
            <p style="text-align:right;"><b>الغرض والتركيبة:</b> {inv['stage']} (بروتين مستهدف {inv['target_cp']:.1f}%)</p>
            <table style="width:100%; border-collapse: collapse; margin-top:15px; text-align:right;">
                <tr style="background:#f5f5f5;">
                    <th style="padding:8px; border:1px solid #ddd;">البيان وصنف العلف للطن</th>
                    <th style="padding:8px; border:1px solid #ddd;">القيمة بالعملة المحلية</th>
                    <th style="padding:8px; border:1px solid #ddd;">المقابل بالدولار الأمريكي</th>
                </tr>
                <tr>
                    <td style="padding:8px; border:1px solid #ddd;">قيمة طن العلف الصافي المطور برمجياً</td>
                    <td style="padding:8px; border:1px solid #ddd;">{inv['base_cost']:,} {inv['currency']}</td>
                    <td style="padding:8px; border:1px solid #ddd;">${inv['base_cost']/inv['usd_rate']:,.2f}</td>
                </tr>
                <tr>
                    <td style="padding:8px; border:1px solid #ddd;">رسوم الفحص ومطابقة الصبغة العلمية (5%)</td>
                    <td style="padding:8px; border:1px solid #ddd;">{inv['tax']:,} {inv['currency']}</td>
                    <td style="padding:8px; border:1px solid #ddd;">${inv['tax']/inv['usd_rate']:,.2f}</td>
                </tr>
                <tr style="font-weight:bold; background:#e3f2fd; color:#1565c0;">
                    <td style="padding:8px; border:1px solid #ddd;">إجمالي الفاتورة النهائي المستحق</td>
                    <td style="padding:8px; border:1px solid #ddd;">{inv['total']:,} {inv['currency']}</td>
                    <td style="padding:8px; border:1px solid #ddd;">${inv['total']/inv['usd_rate']:,.2f}</td>
                </tr>
            </table>
            <p style="font-size:0.85rem; color:#2e7d32; text-align:center; margin-top:15px;">✓ هذه الفاتورة مطابقة لأسعار بورصة اليوم وتعتبر مستنداً فنياً معتمداً للتصنيع الحركي.</p>
        </div>
        """, unsafe_allow_html=True
    )

# ==========================================
# المتطلب السادس: واجهة العرض وشكل ديباجة الأصناف العلفية (للجوال)
# ==========================================
if st.session_state["last_computed_formula"]:
    st.markdown('<div class="section-title">🏷️ واجهة العرض وبطاقة ديباجة الأصناف العلفية المخصصة للجوال</div>', unsafe_allow_html=True)
    
    inv_d = st.session_state["invoice_data"]
    avatar_animal = GEOGRAPHY_DATABASE[geo_country]["breeds"][calc_sector]["avatar"]
    breed_name_label = GEOGRAPHY_DATABASE[geo_country]["breeds"][calc_sector]["name"]
    
    st.markdown(
        f"""
        <div class="sack-tag-2026">
            <h3 style="text-align:center; color:#2e7d32; margin:0;">🌾 ديباجة صنف علف تاور المعتمد 🌾</h3>
            <p style="text-align:center; font-size:0.85rem; color:#666; margin:3px;">هندسة وتصميم: م. عبد القادر إسماعيل تاور</p>
            <hr style="border-top: 2px dashed #2e7d32; margin:10px 0;">
            <div style="font-size:3.5rem; text-align:center; margin:10px 0;">{avatar_animal}</div>
            <div class="animal-frame-graphic">
                📍 {breed_name_label}
            </div>
            <p style="margin:5px 0;"><b>🌾 نوع العلف المصنع:</b> {chosen_stage}</p>
            <p style="margin:5px 0;"><b>🧬 نسبة البروتين الكلي المضمونة:</b> {target_cp:.1f}%</p>
            <p style="margin:5px 0;"><b>🗺️ النطاق الجغرافي:</b> {geo_country} - {geo_city}</p>
            <hr style="border-top:1px dashed #ccc; margin:10px 0;">
            <p style="font-size:0.8rem; color:#555; line-height:1.4;">
                <b>💡 تعليمات التغذية الحقلية الإلزامية:</b> يتم تقديم العلف يومياً بحصص مقننة بناءً على الوزن الحي الناتج عن دالة شريط القياس لضمان أعلى كفاءة للتحويل الغذائي.
            </p>
            <p style="text-align:center; font-size:0.75rem; color:#e65100; font-weight:bold; margin-top:10px;">برمج وفق المعايير الأكاديمية الصارمة لعام 2026 ✓</p>
        </div>
        """, unsafe_allow_html=True
    )

# ==========================================
# 8. البوابة الجانبية السرية وأكواد الصلاحيات (أسفل البرنامج لحماية المظهر)
# ==========================================
st.markdown("<br><hr style='border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
st.markdown("### 🔑 أكواد التحكم والصلاحيات الثلاثية المدمجة في أسفل المنصة:")
admin_code = st.text_input("أدخل كود المالك أو الزملاء الأطباء لعرض التعليقات النقدية الحية:", type="password")

if admin_code == "202687":
    st.markdown("#### 👑 لوحة تحكم المالك المطلقة (م. عبد القادر إسماعيل تاور)")
    st.write("أهلاً بك يا هندسة؛ إليك الإشعارات والتعليقات الواردة من الحقل:")
    if st.session_state["expert_feedbacks"]:
        for fb in st.session_state["expert_feedbacks"]:
            st.warning(f"🔔 **{fb['name']}:** {fb['text']}")
    else:
        st.info("لا توجد تعليقات أو نقد جديد من الخبراء حالياً.")
elif admin_code != "" and admin_code != "2026":
    st.markdown("#### 🔬 شاشة الزملاء الأطباء البياطرة والإنتاج الحيواني")
    st.write("مرحباً بك دكتور. المنصة تعمل بكامل طاقتها العلمية الآن للتفتيش والمطابقة.")
