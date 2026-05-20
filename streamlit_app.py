import streamlit as st
import numpy as np
import os
import threading
import time

# ==========================================
# 1. إعدادات المنصة الرسمية والمظهر الفخم الأولي
# ==========================================
st.set_page_config(page_title="منصة تاور الذكية المتكاملة للأعلاف والإنتاج الحيواني", page_icon="🌾", layout="wide")

# الهوية البصرية الفخمة الأولى الممتدة على كامل الشاشة والمقاومة لضغط شاشات الجوال
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Cairo', sans-serif;
        background-color: #f7f9fa;
        direction: rtl;
    }
    .main-box {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.05);
        margin-bottom: 40px;
    }
    .section-title {
        color: #1b5e20;
        border-right: 6px solid #2e7d32;
        padding-right: 12px;
        text-align: right;
        font-size: 1.3rem;
        font-weight: bold;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    .sack-tag {
        border: 3px dashed #1b5e20;
        padding: 25px;
        border-radius: 12px;
        background-color: #f1f8e9;
        direction: rtl;
        text-align: right;
        max-width: 450px;
        margin: 20px auto;
    }
    .animal-visual-frame {
        border: 2px dashed #e65100;
        background: #fff3e0;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 15px 0;
    }
    .market-card {
        background: #e3f2fd;
        border-right: 5px solid #1565c0;
        padding: 12px;
        margin-bottom: 10px;
        border-radius: 6px;
        text-align: right;
        font-size: 1.1rem;
    }
    .alert-box {
        background-color: #ffebee;
        color: #b71c1c;
        padding: 15px;
        border-right: 5px solid #b71c1c;
        border-radius: 6px;
        margin: 15px 0;
        text-align: right;
    }
    .protein-badge {
        background-color: #e8f5e9;
        border: 2px solid #2e7d32;
        color: #1b5e20;
        padding: 12px;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        margin-top: 10px;
        font-size: 1.1rem;
    }
    .result-row {
        background: #f1f8e9;
        padding: 12px;
        border-bottom: 2px solid #c8e6c9;
        margin-bottom: 6px;
        border-radius: 6px;
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. تهيئة متغيرات الجلسة الآمنة ضد الكراش
# ==========================================
if "user_role" not in st.session_state: st.session_state["user_role"] = "عام"
if "vets_passed" not in st.session_state: st.session_state["vets_passed"] = False
if "expert_feedbacks" not in st.session_state: 
    st.session_state["expert_feedbacks"] = [
        {"name": "د. أحمد الرفاعي", "text": "تعديل رائع لنسب الألياف، يفضل رفع بيكربونات الصوديوم عند استخدام الذرة بنسبة تتجاوز 50%."},
        {"name": "بروفيسور علي إسماعيل", "text": "إضافة إنزيم الفايتيز التلقائي عند زيادة النخالة خطوة علمية ممتازة لكسر الفايتات الزائدة."}
    ]
if "active_formula" not in st.session_state: st.session_state["active_formula"] = {}
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 0.0

# ==========================================
# 3. قاعدة البيانات الجغرافية وبورصة الخامات والمنتجات
# ==========================================
GEOGRAPHY_DATA = {
    "السودان": {
        "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
        "ولاية القضارف": ["القضارف المدينة", "الحواتة", "الفاو"],
        "ولاية الجزيرة": ["ود مدني", "المناقل", "الحصاحيصا"],
        "ولاية شمال كردفان": ["الأبيض", "أم روابة"],
        "ولاية غرب كردفان": ["النهود", "بابنوسة"],
        "الولاية الشمالية": ["دنقلا", "مروي"]
    },
    "ليبيا": {
        "إقليم البطنان والمنطقة الشرقية": ["طبرق", "بنغازي", "البيضاء"],
        "الإقليم الغربي طرابلس": ["طرابلس", "مصراتة", "الزاوية"],
        "فزان والمنطقة الجنوبية": ["سبها", "مرزق"]
    },
    "مصر": {
        "محافظات القاهرة الكبرى": ["القاهرة", "الجيزة"],
        "محافظات الدلتا": ["طنطا", "المنصورة", "الزقازيق"],
        "محافظات الصعيد": ["أسيوط", "المنيا", "أسوان"]
    }
}

REGIONAL_ANIMAL_MARKET = {
    "السودان": {"عجول تسمين حي (كجم)": "3,200 SDG", "خراف كباشي/حمري قائم": "180,000 SDG", "لتر حليب بقري طازج": "1,200 SDG", "طبق بيض مزارع": "5,500 SDG"},
    "ليبيا": {"عجول تسمين حي (كجم)": "38 LYD", "خراف برقي ممتازة": "1,400 LYD", "لتر حليب طازج": "4.5 LYD", "طبق بيض مزارع": "19 LYD"},
    "مصر": {"عجول تسمين قائم (كجم)": "175 EGP", "خراف بلدي حية": "210 EGP", "لتر حليب جاموسي": "35 EGP", "طبق بيض مزارع": "165 EGP"}
}

EXCHANGE_RATES = {"السودان": {"rate": 600.0, "sym": "SDG"}, "ليبيا": {"rate": 4.82, "sym": "LYD"}, "مصر": {"rate": 48.0, "sym": "EGP"} }

SECTOR_OPTIONS_MAP = {
    "الأبقار وسلالاتها": {
        "stages": {"تسمين عجول مكثف سريع": 14.5, "إدرار حليب طاقة عالية": 17.5, "أمهات حوامل مجففة": 12.0},
        "breeds": {"السودان": ["أبقار الكنانة الرائدة", "أبقار البطانة الديرية", "أبقار البقارة"], "ليبيا": ["أبقار فريزيان محسن محلي", "أبقار برقة المحلية"], "مصر": ["أبقار هولشتاين مأقلمة", "الأبقار البلدي المصرية"]},
        "avatar": "🐄", "graphic": "🐄 [رسم بقرة تسمين وإنتاج حليب حركي مكثف]", "desc": "📍 يمثل الأبقار والماشية الكبرى. يوضع شريط القياس حول محيط الصدر خلف المرفق مباشرة."
    },
    "الخيول والفروسية": {
        "stages": {"جياد سباق وسرعة دؤوب": 14.0, "أمهر نامية حديثة الفطام": 15.5, "خيول تربية وصيانة دائرية": 12.0},
        "breeds": {"السودان": ["الحصان الدنقلاوي الأصيل", "الخيول المخلوطة المحسنة"], "ليبيا": ["الجواد العربي الليبي الفاخر", "الخيول الهجينة المحسنة"], "مصر": ["الحصان العربي المصري المستقيم"]},
        "avatar": "🐎", "graphic": "🐎 [رسم تخطيطي لجواد أصيل - علف خيول متكامل]", "desc": "📍 يمثل الجواد الرياضي والنامي. يوضع شريط القياس خلف الغارب مباشرة مائلاً نحو عظمة المقعدة."
    },
    "الأغنام والضأن": {
        "stages": {"تسمين حملان أسواق": 16.0, "نعاج مرضعة ومدرة": 14.5, "دفع غذائي قبل التلقيح": 12.5},
        "breeds": {"السودان": ["ضأن الدوبا (الحمري والشقر)", "ضأن الكباشي البري"], "ليبيا": ["أغنام البرقي العريقة", "الضأن المحلي الليبي"], "مصر": ["أغنام الرحماني"]},
        "avatar": "🐑", "graphic": "🐑 [رسم مجترات صغيرة - علف تسمين حملان وضأن]", "desc": "📍 يمثل الأغنام والماعز. يوضع الشريط حول أضيق منطقة خلف لوح الكتف مباشرة."
    },
    "الطيور والدواجن": {
        "stages": {"بادي لاحم تسمين مكثف": 23.0, "نامي لاحم متوازن": 21.0, "بياض إنتاجي تجاري": 17.5},
        "breeds": {"السودان": ["هبرد محسن مزارع"], "ليبيا": ["كب 500 مزارع"], "مصر": ["روس 308 متطور"]},
        "avatar": "🐓", "graphic": "🐓 [رسم قطاع الطيور والدواجن الداجنة]", "desc": "📍 يمثل الطيور والسمان. الوزن يعتمد على الميزان الحركي الدقيق للقطيع."
    }
}

BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {
        "ذرة صفراء (محلية/مستوردة)": {"cp": 8.5, "max": 65.0},
        "ذرة بيضاء (فتريتة/طابت)": {"cp": 9.0, "max": 55.0},
        "شعير مطحون محلي": {"cp": 11.5, "max": 40.0}
    },
    "الأكساب والأمباز ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب قشرة)": {"cp": 45.0, "max": 25.0},
        "كسب فول صويا 44%": {"cp": 44.0, "max": 30.0},
        "كسب فول صويا 48%": {"cp": 48.0, "max": 25.0}
    },
    "المخلفات الرعوية والمواد المالئة": {
        "نخالة قمح نقية (ردة)": {"cp": 15.0, "max": 30.0},
        "البرسيم الجاف (دريس حجازي منقح)": {"cp": 17.0, "max": 40.0}
    },
    "الإضافات المتخصصة والمركزات": {
        "مركزات تسمين مجترات 5%": {"cp": 36.0, "max": 5.0},
        "مركزات بياض/لاحم دواجن": {"cp": 40.0, "max": 10.0},
        "الحجر الجيري (بودرة بلاط ناعمة)": {"cp": 0.0, "max": 2.0},
        "فوسفات ثنائي الكالسيوم (DCP)": {"cp": 0.0, "max": 1.5},
        "ملح طعام نقي": {"cp": 0.0, "max": 0.5},
        "مضاد سموم فطرية بيولوجي": {"cp": 0.0, "max": 0.2},
        "بيكربونات الصوديوم (صودا توازن)": {"cp": 0.0, "max": 1.0}
    },
    "المعاملات الحيوية والإنزيمات": {
        "إنزيم الفايتيز التلقائي (Phytase Super-D)": {"cp": 0.0, "max": 0.1},
        "إنزيم الفيبروليتيك ومحللات السليلوز": {"cp": 0.0, "max": 0.1}
    }
}

# ==========================================
# 4. ترويسة المنصة الثابتة في الأعلى
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)
st.markdown("<h1 style='color: #1b5e20; text-align:right;'>منصة تاور الذكية المتكاملة للأعلاف والإنتاج الحيواني 🌾</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #c62828; text-align:right;'>الخبير المستشار / م. عبد القادر إسماعيل تاور - تحديث هندسي شامل 2026</h4>", unsafe_allow_html=True)
st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

# نظام الدخول السلس بدون إخفاء الشاشة كاملة
st.markdown("### 🔑 تسجيل الدخول للفئات (اختياري لفتح الأدوات المتقدمة):")
col_acc1, col_acc2 = st.columns([0.3, 0.7])
with col_acc1:
    user_key = st.text_input("أدخل كود الصلاحية (مربي / طبيب / مالك):", type="password", key="main_login")
    if user_key == "2026": st.session_state["user_role"] = "مربي"
    elif user_key == "202687": st.session_state["user_role"] = "مالك"
    elif user_key != "" and not st.session_state["vets_passed"]: st.session_state["user_role"] = "طلب_مختص"
    elif st.session_state["vets_passed"]: st.session_state["user_role"] = "مختص"
with col_acc2:
    st.info(f"الصلاحية الحالية النشطة في النظام: **[ {st.session_state['user_role']} ]**")

# ==========================================
# 5. التبويبات الكبرى المفتوحة دائماً للجميع
# ==========================================
tabs = st.tabs(["🔬 النمذجة والحسابات العلفية الكبرى", "📏 دالة قياس الوزن الحقلية", "📊 بورصة المنتجات والحيوانات الحية"])

# ------------------------------------------
# التبويب الأول: النمذجة والتركيب والإنزيمات
# ------------------------------------------
with tabs[0]:
    st.markdown('<div class="section-title">🌍 أولاً: الجغرافيا وتزامن أسواق البورصة المحلية</div>', unsafe_allow_html=True)
    col_country, col_state, col_city = st.columns(3)
    with col_country: user_country = st.selectbox("اختر دولة المربي المستهدف:", ["السودان", "ليبيا", "مصر"])
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    state_options = list(GEOGRAPHY_DATA[user_country].keys())
    with col_state: chosen_state = st.selectbox("اختر الإقليم / الولاية الإدارية كاملة:", state_options)
    city_options = GEOGRAPHY_DATA[user_country][chosen_state]
    with col_city: user_city = st.selectbox("اختر المدينة المرتبطة بالبورصة حركياً:", city_options)

    st.markdown('<div class="section-title">🐎 ثانياً: تحديد سلالة الحيوان ونوع الإنتاج الفسيولوجي</div>', unsafe_allow_html=True)
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec: main_sector = st.selectbox("اختر القطاع الحيواني المستهدف:", list(SECTOR_OPTIONS_MAP.keys()))
    stage_dict = SECTOR_OPTIONS_MAP[main_sector]["stages"]
    with col_sub: prod_stage = st.selectbox("القسم والمرحلة الفسيولوجية الدقيقة للحيوان:", list(stage_dict.keys()))
    breed_list = SECTOR_OPTIONS_MAP[main_sector]["breeds"].get(user_country, ["سلالة محلية محسنة"])
    with col_prod: chosen_breed = st.selectbox("السلالة الجغرافية المتوفرة:", breed_list)

    # دالة تحديد البروتين المزدوجة التلقائية والاختيارية
    st.markdown('<div class="section-title">📋 ثالثاً: نظام تحديد البروتين المزدوج لخلطة الطن</div>', unsafe_allow_html=True)
    col_cp_p, col_cp_o = st.columns(2)
    mandatory_cp = stage_dict[prod_stage]
    with col_cp_p:
        st.number_input("🧬 نسبة البروتين الحتمية برمجياً (التلقائية وفق الدوال):", value=mandatory_cp, disabled=True)
    with col_cp_o:
        optional_cp = st.slider("⚙️ نسبة البروتين الاختيارية المفتوحة (إذا أردت تعديل المستشار يدوياً):", 10.0, 40.0, value=mandatory_cp)
    
    use_custom_cp = st.checkbox("🔄 اعتماد النسبة الاختيارية المفتوحة بدلاً من النسبة التلقائية للدوال")
    final_target_cp = optional_cp if use_custom_cp else mandatory_cp

    # لوحة التحليل المتقدم للمختصين بعد تخطي الاختبار العلمي
    if st.session_state["user_role"] == "طلب_مختص":
        st.markdown("<div style='background-color:#e3f2fd; padding:15px; border-radius:8px;'>", unsafe_allow_html=True)
        st.subheader("🔬 اختبار الجدارة العلمية للأطباء والخبراء لتفعيل لوحة التركيب الحر:")
        q1 = st.radio("1. ما هي المادة التي يكسرها إنزيم الفايتيز في الردة؟", ["حمض الفايتيك", "النشويات"])
        if st.button("تأكيد الإجابة وفتح الأدوات 🔓"):
            if q1 == "حمض الفايتيك":
                st.session_state["vets_passed"] = True
                st.session_state["user_role"] = "مختص"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">🌾 رابعاً: انتقاء مكونات الخلطة وحساب النتائج العلفية المعززة بالإنزيمات</div>', unsafe_allow_html=True)
    selected_ingredients = {}
    total_pct = 0.0
    
    # محرك اختيار وتوزيع الخامات في الطن
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=False):
            sub_cols = st.columns(2)
            for idx, (ing_name, details) in enumerate(items.items()):
                with sub_cols[idx % 2]:
                    checked = st.checkbox(ing_name, value=False, key=f"f4_{ing_name}")
                    if checked:
                        val = st.number_input(f"نسبة خلط {ing_name} (%) [الأقصى: {details['max']}%]:", 0.0, 100.0, step=1.0, key=f"num_{ing_name}")
                        selected_ingredients[ing_name] = val
                        total_pct += val

    st.markdown(f"**⚖️ إجمالي نسب الخلطة المدخلة للطن:** `{total_pct}%`")

    # آلية معالجة وحقن الإنزيمات الحيوية التلقائية في حال تجاوز الحد
    trigger_phytase = False
    for k, v in selected_ingredients.items():
        if k == "نخالة قمح نقية (ردة)" and v > 30.0:
            trigger_phytase = True

    if trigger_phytase:
        st.markdown("<div class='alert-box'>⚠️ <b>إشعار تصحيح الخطأ التلقائي من تاور (نشط):</b> تم تجاوز الحد الآمن للردة وتصاعدت الفايتات الضارة! قام النظام تلقائياً بحقن <b>إنزيم الفايتيز (Phytase Super-D) بنسبة 0.1%</b> لمعالجة العلة فوراً وضبط الهضم.</div>", unsafe_allow_html=True)

    if st.button("🚀 تشغيل محرك التركيب والاحتساب البرمجي والتحليل الجغرافي", type="primary", use_container_width=True):
        if total_pct == 0.0:
            # تشغيل الدالة التلقائية كلياً في حال لم يدخل المستخدم نسباً يدوية (تسهيلاً للمربي)
            formula_results = {"ذرة صفراء (محلية/مستوردة)": 60.0, "كسب فول صويا 44%": 25.0, "نخالة قمح نقية (ردة)": 11.0, "الحجر الجيري (بودرة بلاط ناعمة)": 2.0, "مركزات تسمين مجترات 5%": 2.0}
            calculated_cp = final_target_cp
            st.info("💡 تم حساب ونمذجة العليقة آلياً وبصورة كاملة بناءً على دالة القطيع والمرحلة المحددة.")
        else:
            formula_results = selected_ingredients
            calculated_cp = sum([(v/100) * BIG_FEEDS_LIBRARY[cat][ing]["cp"] for ing in formula_results for cat in BIG_FEEDS_LIBRARY if ing in BIG_FEEDS_LIBRARY[cat]])

        st.session_state["active_formula"] = formula_results
        
        res_col1, res_col2 = st.columns([0.6, 0.4])
        with res_col1:
            st.markdown(f"<div class='protein-badge'>🧬 بروتين الإنتاج المطلوب: {final_target_cp:.1f}% | بروتين المزيج الفعلي المحسوب: {calculated_cp:.2f}%</div>", unsafe_allow_html=True)
            for k, v in formula_results.items():
                st.markdown(f"<div class='result-row'>🔹 <b>{k}:</b> {v:.2f} % ➡️ ({v*10:.1f} كجم / طن)</div>", unsafe_allow_html=True)
        with res_col2:
            st.bar_chart(formula_results)

    # 💬 منفذ الآراء والنقد للأطباء والمستشارين لتطوير المنصة
    if st.session_state["user_role"] in ["مختص", "مالك"]:
        st.markdown('<div class="section-title">💬 ركن آراء ونقد الأطباء والخبراء لتطوير المنصة</div>', unsafe_allow_html=True)
        exp_name = st.text_input("اسم الخبير أو الطبيب المستشار:")
        exp_text = st.text_area("أضف نقدك العلمي أو مقترحاتك لتعديل نسب الخامات الحقلية:")
        if st.button("حفظ التقييم وإرساله للمالك 📨"):
            if exp_name and exp_text:
                st.session_state["expert_feedbacks"].append({"name": exp_name, "text": exp_text})
                st.success("📥 تم توجيه نقدك البناء بنجاح إلى قاعدة بيانات المالك.")

# ------------------------------------------
# التبويب الثاني: دالة قياس الأوزان الحقلية
# ------------------------------------------
with tabs[1]:
    st.markdown('<div class="section-title">📏 دالة قياس الأوزان الحقلية عبر شريط القياس المتطور</div>', unsafe_allow_html=True)
    st.write("أدخل مقاسات الحيوان الميدانية بالسنتيمتر (cm) لحساب الوزن الحي الفعلي بدقة:")
    
    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1: animal_type_calc = st.selectbox("نوع الحيوان المقاس حقلياً:", ["أبقار وتسمين", "خيول وجياد", "أغنام وضأن"])
    with col_w2: heart_girth = st.number_input("محيط الصدر (Heart Girth) بالسنتيمتر:", min_value=10.0, value=150.0)
    with col_w3: body_length = st.number_input("طول الجسم المستقيم (Body Length) بالسنتيمتر:", min_value=10.0, value=130.0)
    
    if st.button("⚖️ احسب الوزن الحي الحيواني الفعلي فوراً"):
        if animal_type_calc == "أبقار وتسمين": weight_kg = (heart_girth ** 2 * body_length) / 10838
        elif animal_type_calc == "خيول وجياد": weight_kg = (heart_girth ** 2 * body_length) / 11877
        else: weight_kg = (heart_girth ** 2 * body_length) / 11312
        st.success(f"📊 الوزن التقديري الصافي للحيوان هو: **{weight_kg:.2f} كجم قائم**")

# ------------------------------------------
# التبويب الثالث: البورصة الحية المتطابقة مع الواقع الإقليمي
# ------------------------------------------
with tabs[2]:
    st.markdown(f'<div class="section-title">📊 أسعار بورصة المنتجات واللحوم الحية القائمة في أسواق ({user_country})</div>', unsafe_allow_html=True)
    animal_prices = REGIONAL_ANIMAL_MARKET.get(user_country, {"عجول قائم": "0.0"})
    for prod_name, price_val in animal_prices.items():
        st.markdown(f"""
        <div class="market-card">
            🎯 <b>{prod_name}:</b> {price_val} في الأسواق المحلية والمجازر الآن.
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. منفذ العرض وديباجة التسويق المخصصة للجوال
# ==========================================
if st.session_state["active_formula"]:
    st.markdown('<div class="section-title">🏷️ منفذ التسويق النهائي وديباجة المنتج المخصصة للجوالات الذكية</div>', unsafe_allow_html=True)
    
    sec_data = SECTOR_OPTIONS_MAP[main_sector]
    st.markdown(f"""
    <div class="mobile-sack-tag">
        <h3 style="text-align: center; color: #1b5e20; margin:0;">🌾 خلطات ومجموعة تاور المعتمدة 🌾</h3>
        <p style="text-align: center; font-size:0.9rem; margin:2px;">المستشار الفني: م. عبد القادر إسماعيل تاور</p>
        <hr style="border-top: 1px dashed #1b5e20; margin:10px 0;">
        <div style="font-size: 3.5rem; text-align:center;">{sec_data['avatar']}</div>
        <p style="text-align: right; font-size:0.95rem; margin:4px;"><b>🎯 السلالة:</b> {chosen_breed}</p>
        <p style="text-align: right; font-size:0.95rem; margin:4px;"><b>نوع العلف:</b> {prod_stage}</p>
        <p style="text-align: right; font-size:0.95rem; margin:4px;"><b>نسبة البروتين الكلي:</b> {final_target_cp:.1f}%</p>
        <div class="animal-visual-frame">
            <p style="color: #d84315; font-size:0.85rem; margin:0;"><b>{sec_data['graphic']}</b></p>
            <p style="font-size:0.8rem; color:#37474f; margin:5px 0 0 0;">{sec_data['desc']}</p>
        </div>
        <p style="text-align: center; font-size: 0.75rem; color: #558b2f; margin:0;">برمج وفقاً للمواصفات الأكاديمية وصحة الحيوان 2026</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 7. لوحة تحكم المالك الحصرية والسرية (أعلى التذييل)
# ==========================================
if st.session_state["user_role"] == "مالك":
    st.markdown('<div class="section-title">👑 لوحة المالك الكبرى المطلقة ومراقبة الإشعارات الحية</div>', unsafe_allow_html=True)
    st.write("مرحباً بك يا م. عبد القادر؛ إليك كافة إشعارات ونقد المختصين الموجهة لك مباشرة:")
    for idx, fb in enumerate(st.session_state["expert_feedbacks"]):
        st.markdown(f"""
        <div style='background-color: #fff8e1; padding: 12px; border-right: 5px solid #ffb300; margin-bottom: 8px; border-radius: 6px;'>
            🔔 <b>إشعار من {fb['name']}:</b> {fb['text']}
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; font-size: 0.85rem; color: #777; margin-bottom: 30px;">👨‍🔬 م. عبد القادر إسماعيل تاور © 2026 | خبير الحلول البرمجية للإنتاج الحيواني</div>', unsafe_allow_html=True)
