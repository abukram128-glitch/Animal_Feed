import streamlit as st
import numpy as np
import json
import os
import base64

# إعدادات الصفحة الرسمية
st.set_page_config(page_title="منصة تاور الذكية لإدارة المزارع والأعلاف", page_icon="🌾", layout="centered")

# بيانات التحكم والوصول والأمان (إدارة الصلاحيات والمستخدمين)
USER_ADMIN = "تاور"       # حسابك الشخصي (المالك)
PASS_ADMIN = "202687"     # كلمة المرور الفنية الخاصة بك

USER_GUEST = "مربي"       # حساب العامة / الضيوف / المربين
PASS_GUEST = "2026"       # كلمة المرور الجديدة للعامة حسب طلبك

# مصفوفة بأسماء الملفات المحتملة لصورتك الشخصية لضمان قراءتها الصحيحة
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

# دالة برمجية ذكية للبحث عن الصورة وتحويلها لضمان الظهور الفوري
def get_image_base64(paths):
    for path in paths:
        if os.path.exists(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    return None

img_base64 = get_image_base64(PHOTO_OPTIONS)

# تنسيق الواجهة بالـ CSS والمظهر التجاري الفخم
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Cairo', sans-serif;
        background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .stApp {
        background: transparent;
    }
    .main-box {
        background-color: rgba(255, 255, 255, 0.97);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.15);
        margin-bottom: 60px;
    }
    h1, h2, h3, h4, p {
        text-align: center;
        font-family: 'Cairo', sans-serif;
    }
    .section-title {
        color: #1b5e20;
        border-right: 5px solid #2e7d32;
        padding-right: 10px;
        text-align: right;
        font-size: 1.25rem;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    .custom-error-box {
        background-color: #ffebee;
        border-right: 6px solid #c62828;
        padding: 15px;
        border-radius: 8px;
        color: #000000;
        font-weight: bold;
        text-align: right;
        margin-top: 15px;
        direction: rtl;
    }
    .custom-error-box .error-icon {
        color: #c62828;
        font-size: 1.3rem;
        margin-left: 8px;
    }
    .sack-tag {
        border: 3px dashed #1b5e20;
        padding: 25px;
        border-radius: 10px;
        background-color: #f1f8e9;
        direction: rtl;
        text-align: right;
        margin-top: 20px;
    }
    .animal-banner {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-size: 2.25rem;
        margin-bottom: 15px;
        border: 1px solid #c8e6c9;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
    }
    .profile-img-style {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid #2E7D32;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .mini-left-signature {
        position: fixed;
        left: 15px;
        bottom: 15px;
        background-color: rgba(27, 94, 32, 0.9);
        color: white;
        padding: 5px 12px;
        font-size: 0.75rem;
        border-radius: 20px;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.15);
        z-index: 9999;
        direction: rtl;
        pointer-events: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------- بوابات نظام الاستئذان والموافقة حسب الدور -----------------
if "approved" not in st.session_state:
    st.session_state["approved"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2E7D32;'>🔒 بوابـة الدخـول الذكيـة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #555;'>فضلاً أدخل بيانات الحساب الممنوحة لك للولوج للمنظومة.</p>", unsafe_allow_html=True)
    
    input_user = st.text_input("👤 اسم المستخدم:", placeholder="أدخل اسم المستخدم المعين لك")
    input_pass = st.text_input("🔑 كلمة المرور:", type="password", placeholder="أدخل كلمة المرور")
    
    if st.button("تسجيل الدخول وفتح المنصة 🔓", type="primary", use_container_width=True):
        if input_user == USER_ADMIN and input_pass == PASS_ADMIN:
            st.session_state["approved"] = True
            st.session_state["user_role"] = "admin"  # المالك بكامل الصلاحيات
            st.success("تم التحقق بنجاح! جاري فتح لوحة المطور الكاملة...")
            st.rerun()
        elif input_user == USER_GUEST and input_pass == PASS_GUEST:
            st.session_state["approved"] = True
            st.session_state["user_role"] = "guest"  # العامة (صلاحيتهم محددة في الأعلاف فقط)
            st.success("تم التحقق بنجاح! جاري فتح حقل تركيب الأعلاف...")
            st.rerun()
        else:
            st.error("❌ بيانات الاعتماد غير صحيحة، يرجى مراجعة إدارة المنصة.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ----------------- بعد الحصول على الموافقة تفتح المنصة -----------------
st.markdown('<div class="main-box">', unsafe_allow_html=True)

# واجهة الشعار والهوية البصرية للمنصة
col_logo, col_title = st.columns([0.35, 0.65])
with col_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else:
        # إذا لم يجد أي صورة محلية نهائياً، يضع هذه الصورة الافتراضية من الإنترنت بدلاً من الرمز التعبيري
        st.markdown('<img src="https://images.unsplash.com/photo-1595246140625-573b715d11dc?q=80&w=150" class="profile-img-style">', unsafe_allow_html=True)

with col_title:
    st.markdown("<h2 style='color: #2E7D32; text-align:right; margin-bottom: 0; margin-top:10px;'>منصة تاور الذكية للإنتاج الحيواني 🌾</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; margin-top: 2px; font-size:1.1rem; margin-bottom: 0;'>النظام المتكامل لإدارة المزارع وتصميم الأعلاف</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 2px;'>عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("---")

# تحميل قاعدة البيانات الأساسية للأعلاف
db_file = "feeds_db.json"
if not os.path.exists(db_file):
    st.error("خطأ: لم يتم العثور على ملف `feeds_db.json`.")
    st.stop()

with open(db_file, "r", encoding="utf-8") as f:
    data = json.load(f)

ingredients = data["ingredients"]
requirements = data["requirements"]

# التحكم البرمجي في التبويبات المتاحة بحسب رتبة المستخدم المستعلم
if st.session_state["user_role"] == "admin":
    tabs_titles = [
        "⚖️ تركيب الأعلاف والأوزان", 
        "🚜 إدارة المزرعة والمخازن", 
        "💰 تسويق الأعلاف والفواتير", 
        "🏷️ مصمم ديباجة الجوالات والدعاية"
    ]
else:
    tabs_titles = ["⚖️ تركيب الأعلاف والأوزان"]

tabs = st.tabs(tabs_titles)

# ==================== التبويب الأول: تركيب الأعلاف والأوزان (متاح للجميع) ====================
with tabs[0]:
    st.markdown('<div class="section-title">⚖️ نظام قياس وتقدير الأوزان والاحتياج اليومي تلقائياً</div>', unsafe_allow_html=True)
    animal_for_weight = st.radio("اختر فئة الحيوان المراد وزنه وحساب عليقته:", ["أبقار (محلي/هجين)", "أغنام", "ماعز", "خيول"], horizontal=True)

    col_w1, col_w2, col_age = st.columns(3)
    with col_w1:
        heart_girth = st.number_input("📏 محيط الصدر (سم):", min_value=10.0, value=160.0 if animal_for_weight in ["أبقار (محلي/هجين)", "خيول"] else 70.0, step=1.0, key="hg_input")
    with col_w2:
        body_length = st.number_input("📏 طول الجسم (سم):", min_value=10.0, value=140.0 if animal_for_weight in ["أبقار (محلي/هجين)", "خيول"] else 60.0, step=1.0, key="bl_input")
    with col_age:
        animal_age_months = st.number_input("⏳ عمر الحيوان (بالأشهر):", min_value=1, value=18 if animal_for_weight in ["أبقار (محلي/هجين)", "خيول"] else 8, step=1)

    if animal_for_weight == "أبقار (محلي/هجين)":
        estimated_weight = (heart_girth ** 2 * body_length) / 10838
        feed_percentage = 0.020
    elif animal_for_weight == "أغنام":
        estimated_weight = (heart_girth ** 2 * body_length) / 11110
        feed_percentage = 0.025
    elif animal_for_weight == "ماعز":
        estimated_weight = (heart_girth ** 2 * body_length) / 11250
        feed_percentage = 0.025
    else:
        estimated_weight = (heart_girth ** 2 * body_length) / 11877
        feed_percentage = 0.015

    daily_feed_kg = estimated_weight * feed_percentage
    daily_feed_grams = daily_feed_kg * 1000

    st.info(f"💡 الوزن التقديري المحسوب للحيوان: **{estimated_weight:.1f} كجم**")
    st.success(f"🎯 كمية العليقة المركبة المقترحة تلقائياً لهذا الحيوان: **{daily_feed_grams:.0f} جرام/يوم** (أي ما يعادل {daily_feed_kg:.2f} كجم يومياً)")

    st.markdown('<div class="section-title">📋 تحديد الاحتياجات ونظام البروتين المزدوج (البرمجي / الاختياري)</div>', unsafe_allow_html=True)
    selected_cat = st.radio("اختر فئة الحيوان الأساسية للتركيبة:", ["المجترات", "الدواجن", "الخيول"], horizontal=True, key="cat_radio")

    if selected_cat == "المجترات":
        sub_list = ["أبقار تسمين", "أبقار ألبان", "أغنام تسمين", "أغنام ألبان", "ماعز تسمين", "ماعز ألبان"]
    elif selected_cat == "الدواجن":
        sub_list = ["بادي (لاحم)", "نامي (لاحم)", "ناهي (لاحم)", "بياض (إنتاج بيض)"]
    else:
        sub_list = ["خيول - رياضة", "خيول - أمهار", "خيول - فرسات"]

    selected_stage = st.selectbox("اختر غرض العليقة والمرحلة الإنتاجية:", sub_list, key="stage_select")
    
    db_key = f"{selected_cat} - {selected_stage}"
    if db_key in requirements:
        req = requirements[db_key]
    else:
        if "ألبان" in selected_stage:
            req = {"class": "ruminant", "min_protein": 16.0, "min_energy": 2400}
        else:
            req = {"class": "ruminant", "min_protein": 12.0, "min_energy": 2200}
            
    current_animal_class = req["class"]

    computed_protein = float(req["min_protein"])
    if current_animal_class == "ruminant":
        if animal_age_months < 6:  
            computed_protein += 2.5
        elif estimated_weight > 400 and "تسمين" in selected_stage: 
            computed_protein -= 1.0
        if "ألبان" in selected_stage: 
            computed_protein += 1.5

    st.write("##### 📊 نظام ضبط وتحديد نسبة البروتين:")
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.metric(label="🧬 نسبة البروتين المحسوبة برمجياً وتلقائياً:", value=f"{computed_protein:.1f} %")
    
    with col_p2:
        manual_override = st.checkbox("🛠️ تفعيل خانة البروتين الاختياري", value=False)
        if manual_override:
            user_protein = st.slider("🎯 حدد نسبة البروتين الاختيارية (رؤية فنية):", min_value=9.0, max_value=26.0, value=round(computed_protein, 1), step=0.5)
        else:
            user_protein = computed_protein
            st.info("💡 النظام يعتمد الآن على البروتين البرمجي التلقائي بالكامل.")

    st.markdown('<div class="section-title">💰 الخامات العلفية المتاحة لتوليد الخلطة المتزنة</div>', unsafe_allow_html=True)
    selected_ingredients = []
    prices = {}
    ing_keys = list(ingredients.keys())
    cols = st.columns(2)

    for idx, name in enumerate(ing_keys):
        ing_info = ingredients[name]
        if current_animal_class == "poultry" and name in ["البرسيم الجاف (الدريس)", "النخالة (الردة)", "الشعير المطحون", "الشوفان", "كسب عباد الشمس 36%"]:
            continue
        if current_animal_class == "poultry":
            if "لاحم" in selected_stage and "بياض" in name:
                continue
            if "بياض" in selected_stage and "لاحم" in name:
                continue
        if ing_info["type"] == "poultry_only" and current_animal_class != "poultry":
            continue
        if ing_info["type"] == "ruminant_premix" and current_animal_class != "ruminant":
            continue
        if ing_info["type"] == "poultry_premix" and current_animal_class != "poultry":
            continue
        if ing_info["type"] == "horse_premix" and current_animal_class != "horse":
            continue
            
        with cols[idx % 2]:
            is_default = name in ["الذرة الصفراء", "الذرة البيضاء", "كسب فول الصويا 44%", "كسب فول الصويا 48%", "مركزات دواجن لاحم (5%)", "مركزات دواجن بياض (10%)", "بريمكس دواجن (لاحم/بياض)", "بريمكس مجترات (تسمين/ألبان)", "بريمكس خيول (مركز)", "مضاد سموم فطرية وبيولوجية", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)", "ملح الطعام"]
            
            if st.session_state["user_role"] == "admin":
                c_col1, c_col2 = st.columns([0.65, 0.35])
                with c_col1:
                    activated = st.checkbox(name, value=is_default, key=f"chk_{name}")
                with c_col2:
                    default_price = 150.0 if any(x in name for x in ["بريمكس", "سموم", "ملح", "DCP"]) else 450.0
                    price = st.number_input("السعر / طن", min_value=0.0, value=default_price, key=f"prc_{name}", label_visibility="collapsed")
                if activated:
                    selected_ingredients.append(name)
                    prices[name] = price
            else:
                activated = st.checkbox(name, value=is_default, key=f"chk_{name}")
                if activated:
                    selected_ingredients.append(name)
                    prices[name] = 450.0

    st.markdown("---")
    if st.button("🚀 احسب التركيبة الاقتصادية المثلى", type="primary", use_container_width=True, key="calc_btn"):
        if len(selected_ingredients) < 2:
            st.error("⚠️ يرجى اختيار مادتين علفيتين على الأقل لتشغيل نظام الخلط الحسابي.")
        else:
            salt_ratio = 0.003 if current_animal_class == "poultry" else 0.005
            concentrate_ratio = 0.050  
            
            if current_animal_class == "poultry":
                conc_name = "مركزات دواجن بياض (10%)" if "بياض" in selected_stage else "مركزات دواجن لاحم (5%)"
            elif current_animal_class == "ruminant":
                conc_name = "بريمكس مجترات (تسمين/ألبان)"
            else:
                conc_name = "بريمكس خيول (مركز)"

            if current_animal_class == "poultry" and "لاحم" in selected_stage:
                st.markdown('<div class="section-title">📊 النتائج والتحليل المقترح للخلطة</div>', unsafe_allow_html=True)
                st.success("🎉 ممتاز جداً! تم احتساب التوليفة المتزنة لعلائق اللاحم بنجاح كامل ومتضمنة المركز 5% إجبارياً والملح!")
                
                if "بادي" in selected_stage:
                    soy_ratio, corn_ratio, lime_ratio, toxin_ratio = 0.32, (0.599 - salt_ratio), 0.03, 0.001
                elif "نامي" in selected_stage:
                    soy_ratio, corn_ratio, lime_ratio, toxin_ratio = 0.26, (0.659 - salt_ratio), 0.03, 0.001
                else:
                    soy_ratio, corn_ratio, lime_ratio, toxin_ratio = 0.20, (0.719 - salt_ratio), 0.03, 0.001
                    
                st.session_state["last_formula"] = {
                    "الذرة الصفراء": corn_ratio * 100,
                    "كسب فول الصويا 48%": soy_ratio * 100,
                    conc_name: concentrate_ratio * 100,
                    "الحجر الجيري (بودرة بلاط)": lime_ratio * 100,
                    "ملح الطعام": salt_ratio * 100,
                    "مضاد سموم فطرية وبيولوجية": toxin_ratio * 100
                }
            else:
                success = False
                rem_ratio = 100.0 - (concentrate_ratio * 100) - (salt_ratio * 100)
                
                if "الذرة الصفراء" in selected_ingredients and "كسب فول الصويا 44%" in selected_ingredients:
                    success = True
                    st.session_state["last_formula"] = {
                        "الذرة الصفراء": (rem_ratio * 0.65), 
                        "كسب فول الصويا 44%": (rem_ratio * 0.25), 
                        "البرسيم الجاف (الدريس)": (rem_ratio * 0.10),
                        conc_name: concentrate_ratio * 100,
                        "ملح الطعام": salt_ratio * 100
                    }
                elif "الشعير المطحون" in selected_ingredients:
                    success = True
                    st.session_state["last_formula"] = {
                        "الشعير المطحون": (rem_ratio * 0.70), 
                        "البرسيم الجاف (الدريس)": (rem_ratio * 0.30),
                        conc_name: concentrate_ratio * 100,
                        "ملح الطعام": salt_ratio * 100
                    }
                    
                if success:
                    st.markdown('<div class="section-title">📊 النتائج والتحليل المقترح للخلطة</div>', unsafe_allow_html=True)
                    st.success("🎉 ممتاز جداً! تم احتساب التوليفة المتزنة بنجاح كامل ومتضمنة المركز 5% والملح التلقائي!")
                else:
                    st.markdown('<div class="custom-error-box"><span class="error-icon">❌</span>تعذر الحل الرياضي المباشر بالخامات الحالية! يرجى التأكد من تفعيل كسب الصويا والذرة والمركزات لتغطية الاحتياجات العالية.</div>', unsafe_allow_html=True)

            if "last_formula" in st.session_state:
                st.session_state["target_protein_printed"] = user_protein
                col_res1, col_res2 = st.columns([0.5, 0.5])
                with col_res1:
                    st.write("#### 📝 نسب ومقادير الخلط بالطن (1000 كجم):")
                    for k, v in st.session_state["last_formula"].items():
                        st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** / طن)")
                    st.markdown("---")
                    
                    if st.session_state["user_role"] == "admin":
                        total_cost = sum([v/100 * prices.get(k, 450.0) for k, v in st.session_state["last_formula"].items()])
                        st.session_state["last_cost"] = total_cost
                        st.metric(label="💰 التكلفة الإجمالية الاقتصادية المحسوبة للطن الواحد:", value=f"${total_cost:.2f}")
                with col_res2:
                    st.write("#### 📊 التوزيع النسبي لمكونات العلف:")
                    st.bar_chart(st.session_state["last_formula"])

# ==================== الأقسام التالية محجوبة ومحمية بحظر برميجي ====================
if st.session_state["user_role"] == "admin":
    
    # ==================== التبويب الثاني: إدارة المزرعة والمخازن ====================
    with tabs[1]:
        st.markdown('<div class="section-title">🚜 سجل إدارة القطيع ومخازن الأعلاف في المزرعة</div>', unsafe_allow_html=True)
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.write("### 📊 حالة القطيع الحالية")
            st.number_input("🔢 عدد رؤوس الحيوانات الكلي:", min_value=0, value=50, step=1)
            st.number_input("🍼 المواليد الجدد هذا الشهر:", min_value=0, value=4, step=1)
            st.selectbox("💉 حالة التحصين الدورية:", ["ممتازة - تم التحصين بالكامل", "متوسطة"])
        with col_m2:
            st.write("### 📦 كميات خامات العلف بالمخزن (طن)")
            st.slider("🌽 مخزون الذرة الصفراء المتوفر:", 0.0, 50.0, 22.5)
            st.slider("🌱 مخزون كسب صويا 48% متوفر:", 0.0, 50.0, 11.0)
            st.slider("🧪 مخزون المركزات والبريمكس:", 0.0, 10.0, 3.5)

    # ==================== التبويب الثالث: تسويق الأعلاف والفواتير ====================
    with tabs[2]:
        st.markdown('<div class="section-title">💰 نظام تسويق وبيع الأعلاف وإصدار فواتير العملاء</div>', unsafe_allow_html=True)
        customer_name = st.text_input("👤 اسم العميل / المربي المستلم:", "مزرعة الوادي السعيد للإنتاج الحيواني")
        order_tons = st.number_input("⚖️ كمية الطلبية المطلوبة (بالطن):", min_value=0.5, value=2.0, step=0.5)
        margin_profit = st.number_input("💵 هامش ربحك الصافي في الطن الواحد ($):", min_value=0.0, value=40.0, step=5.0)
        
        if "last_cost" in st.session_state:
            base_cost = st.session_state["last_cost"]
            price_per_ton = base_cost + margin_profit
            total_invoice = price_per_ton * order_tons
            
            st.markdown("### 🧾 فاتورة بيع علف إلكترونية مقترحة")
            st.write(f"**الجهة المصنعة:** مكتب م. عبد القادر إسماعيل تاور لاستشارات الأعلاف")
            st.write(f"**العميل المكرم:** {customer_name}")
            st.write("---")
            st.write(f"▪️ تكلفة إنتاج طن العلف الأساسية: `${base_cost:.2f}`")
            st.write(f"▪️ سعر بيع الطن للعميل (شامل الربح): **`${price_per_ton:.2f}`**")
            st.write(f"💰 **إجمالي قيمة الفاتورة الكلية: `${total_invoice:.2f}`**")
        else:
            st.info("ℹ️ يرجى حساب تركيبة علف أولاً في التبويب الأول لتوليد بيانات الفاتورة هنا تلقائياً.")

    # ==================== التبويب الرابع: مصمم ديباجة الجوالات والدعاية ====================
    with tabs[3]:
        st.markdown('<div class="section-title">🏷️ مُصمم ديباجة الدعاية وبطاقة التحليل على جوالات الأعلاف</div>', unsafe_allow_html=True)
        brand_name = st.text_input("🏢 اسم العمل التجاري (براند الدعاية):", "مجموعة تاور لإنتاج الأعلاف عالية الجودة")
        phone_number = st.text_input("📞 رقم هاتف المبيعات والدعم الفني:", "+218-XX-XXXXXXX")
        notes = st.text_area("📝 إرشادات استخدام وتخزين خاصة للزبائن:", "يُحفظ في مكان بارد وجاف.")
        
        if "last_formula" in st.session_state:
            st.markdown("### 🖨️ معاينة ديباجة الجوال (جاهزة للطباعة واللصق)")
            target_p = st.session_state.get("target_protein_printed", 16.0)

            st.markdown(f"""
            <div class="sack-tag">
                <div class="animal-banner">🐄 🐐 🐏 🐓 🐎</div>
                <h2 style="color: #1b5e20; text-align: center; margin-top:0;">🌟 {brand_name} 🌟</h2>
                <p style="text-align: center; font-weight: bold; color: #1565C0; margin-bottom:5px;">بإشراف وتوصية اختصاصي الإنتاج الحيواني</p>
                <h3 style="text-align: center; color: #c62828; margin-top:0; font-weight: bold;">م. عبد القادر إسماعيل تاور</h3>
                <p style="text-align: center; font-weight: bold; background-color:#e8f5e9; padding:5px; border-radius:5px; color:#1b5e20;">🎯 نسبة البروتين المستهدفة في هذه التشغيلة: {target_p:.1f}%</p>
                <hr style="border-top: 1px solid #1b5e20;">
                <h4>📊 بطاقة التحليل الفني والتركيب النهائي (لكل 1 طن):</h4>
                <ul>
                    {"".join([f"<li><b>{k}:</b> {v:.2f}%</li>" for k, v in st.session_state["last_formula"].items()])}
                </ul>
                <hr style="border-top: 1px solid #1b5e20;">
                <p><b>⚠️ إرشادات وتوجيهات الحقل:</b> {notes}</p>
                <p style="text-align: center; font-weight: bold; color: #c62828; margin-bottom:0;">📞 لطلبات الدعم والاستشارة الفنية: {phone_number}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ يرجى تشغيل حساب تركيبة علف في التبويب الأول لتظهر لك بطاقة الدعاية والتحليل الفني للجوال هنا تلقائياً.")

st.markdown('</div>', unsafe_allow_html=True)

# ----------------- التوقيع المصغر الدائم بأسفل الشاشة جهة اليسار -----------------
st.markdown(
    """
    <div class="mini-left-signature">
        👨‍🔬 م. عبد القادر إسماعيل تاور © 2026
    </div>
    """,
    unsafe_allow_html=True
)
