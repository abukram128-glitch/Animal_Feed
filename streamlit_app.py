import streamlit as st
import numpy as np
import json
import os

# إعدادات الصفحة الرسمية
st.set_page_config(page_title="منصة تاور الذكية لإدارة المزارع والأعلاف", page_icon="🌾", layout="centered")

# بيانات التحكم والوصول والأمان
OWNER_USER = "تاور"
OWNER_PASS = "2026"

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
        padding: 20px;
        border-radius: 10px;
        background-color: #f1f8e9;
        direction: rtl;
        text-align: right;
        margin-top: 20px;
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

# ----------------- بوابات نظام الاستئذان والموافقة -----------------
if "approved" not in st.session_state:
    st.session_state["approved"] = False

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #c62828;'>🔒 نظام حماية المطور والمالك</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #555;'>يتطلب تشغيل المنصة إذن وموافقة اختصاصي الإنتاج الحيواني المالك للمشروع.</p>", unsafe_allow_html=True)
    
    input_user = st.text_input("👤 اسم المستخدم المطور:", placeholder="أدخل اسم المستخدم (تاور)")
    input_pass = st.text_input("🔑 كلمة المرور السريّة:", type="password", placeholder="أدخل كلمة المرور")
    
    if st.button("منح الإذن والموافقة لفتح المنصة 🔓", type="primary", use_container_width=True):
        if input_user == OWNER_USER and input_pass == OWNER_PASS:
            st.session_state["approved"] = True
            st.success("تم التحقق بنجاح! جاري فتح النظام...")
            st.rerun()
        else:
            st.error("❌ بيانات الاعتماد غير صحيحة، لا يمكن تشغيل البرنامج دون إذن المطور.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ----------------- بعد الحصول على الموافقة تفتح المنصة بالكامل -----------------
st.markdown('<div class="main-box">', unsafe_allow_html=True)

# واجهة الشعار الهوية التجارية الموحدة للمشروع
st.markdown("<h1 style='color: #2E7D32; margin-bottom: 0;'>منصة تاور الذكية للإنتاج الحيواني 🌾</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #1565C0; margin-top: 5px; margin-bottom: 0;'>النظام المتكامل لإدارة المزارع وتسويق الأعلاف</h3>", unsafe_allow_html=True)
st.markdown("<h2 style='color: #c62828; font-weight: bold; margin-top: 5px;'>عبد القادر إسماعيل تاور</h2>", unsafe_allow_html=True)
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

# ----------------- إنشاء التبويبات العلوية للتنقل بين الأنظمة -----------------
tab_formulation, tab_management, tab_marketing, tab_branding = st.tabs([
    "⚖️ تركيب الأعلاف والأوزان", 
    "🚜 إدارة المزرعة والمخازن", 
    "💰 تسويق الأعلاف والفواتير", 
    "🏷️ مصمم ديباجة الجوالات والدعاية"
])

# ==================== التبويب الأول: تركيب الأعلاف والأوزان ====================
with tab_formulation:
    st.markdown('<div class="section-title">⚖️ نظام قياس وتقدير الأوزان والاحتياج اليومي تلقائياً</div>', unsafe_allow_html=True)
    animal_for_weight = st.radio("اختر فئة الحيوان المراد وزنه وحساب عليقته:", ["أبقار (محلي/هجين)", "أغنام", "ماعز", "خيول"], horizontal=True)

    col_w1, col_w2 = st.columns(2)
    with col_w1:
        heart_girth = st.number_input("📏 محيط الصدر (سم):", min_value=10.0, value=160.0 if animal_for_weight in ["أبقار (محلي/هجين)", "خيول"] else 70.0, step=1.0, key="hg_input")
    with col_w2:
        body_length = st.number_input("📏 طول الجسم (سم):", min_value=10.0, value=140.0 if animal_for_weight in ["أبقار (محلي/هجين)", "خيول"] else 60.0, step=1.0, key="bl_input")

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

    st.markdown('<div class="section-title">📋 تحديد الاحتياجات الغذائية والإنتاجية حسب السلالات</div>', unsafe_allow_html=True)
    selected_cat = st.radio("اختر فئة الحيوان الأساسية للتركيبة:", ["المجترات", "الدواجن", "الخيول"], horizontal=True, key="cat_radio")

    if selected_cat == "المجترات":
        sub_list = ["أبقار تسمين", "أبقار ألبان", "أغنام تسمين", "أغنام ألبان", "ماعز تسمين", "ماعز ألبان"]
    elif selected_cat == "الدواجن":
        sub_list = ["بادي (لاحم)", "نامي (لاحم)", "ناهي (لاحم)", "بياض (إنتاج بيض)"]
    else:
        sub_list = ["خيول - رياضة", "خيول - أمهار", "خيول - فرسات"]

    selected_stage = st.selectbox("اختر غرض العليقة والمرحلة الإنتاجية:", sub_list, key="stage_select")
    
    # معالجة المفاتيح غير الموجودة افتراضياً بقاعدة البيانات لخيارات الألبان الجديدة
    db_key = f"{selected_cat} - {selected_stage}"
    if db_key in requirements:
        req = requirements[db_key]
    else:
        if "ألبان" in selected_stage or "حليب" in selected_stage:
            req = {"class": "ruminant", "min_protein": 16.0, "min_energy": 2400}
        else:
            req = {"class": "ruminant", "min_protein": 12.0, "min_energy": 2200}
            
    current_animal_class = req["class"]

    # 🧬 نظام السلالات التفاعلي والربط التلقائي بنسبة الإنتاج ومستوى العلف
    production_multiplier = 1.0
    if "ألبان" in selected_stage or "بياض" in selected_stage:
        st.markdown("##### 🧬 برمجة السلالات ومعدل الكفاءة الإنتاجية:")
        col_breed, col_prod = st.columns(2)
        with col_breed:
            if selected_cat == "المجترات":
                breed = st.selectbox("اختر سلالة القطيع الحالية:", ["هولشتاين / فريزيان", "جيرسي", "أغنام عواسي", "أغنام بربري", "ماعز دمشقي / قبرصي", "محلي هجين"])
            else:
                breed = st.selectbox("اختر سلالة الدجاج البياض:", ["لوهمان براون", "لجهورن أبيض", "هاي سكس", "بلدي محسن"])
        with col_prod:
            prod_rate = st.slider("📊 حدد نسبة الإنتاج الحالية بالمزرعة (%):", min_value=10, max_value=100, value=75, step=5)
        
        # التأثير الحسابي لنسبة الإنتاج على الاحتياج الغذائي (كلما زاد الإنتاج زاد الاحتياج)
        production_multiplier = 1.0 + ((prod_rate - 70) * 0.005)

    base_protein = float(req["min_protein"]) * production_multiplier
    base_energy = float(req["min_energy"])

    user_protein = st.slider(f"🎯 حدد نسبة البروتين المرغوبة لعليقة ({selected_stage}):", min_value=9.0, max_value=26.0, value=round(base_protein, 1), step=0.5, key="protein_slider")

    if current_animal_class == "poultry":
        calculated_energy = base_energy
    else:
        calculated_energy = base_energy + ((user_protein - base_protein) * 20)

    st.warning(f"⚙️ النظام التلقائي: تم ضبط الطاقة الممثلة المستهدفة لتكون **{calculated_energy:.0f} كـ/كجم** لتتلاءم مع نسبة الإنتاج والبروتين.")

    st.markdown('<div class="section-title">💰 الخامات العلفية المتاحة وأسعار السوق</div>', unsafe_allow_html=True)
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
            c_col1, c_col2 = st.columns([0.65, 0.35])
            with c_col1:
                activated = st.checkbox(name, value=is_default, key=f"chk_{name}")
            with c_col2:
                default_price = 150.0 if any(x in name for x in ["بريمكس", "سموم", "ملح", "DCP"]) else 450.0
                price = st.number_input("السعر / طن", min_value=0.0, value=default_price, key=f"prc_{name}", label_visibility="collapsed")
            if activated:
                selected_ingredients.append(name)
                prices[name] = price

    st.markdown("---")
    if st.button("🚀 احسب التركيبة الاقتصادية المثلى", type="primary", use_container_width=True, key="calc_btn"):
        if len(selected_ingredients) < 2:
            st.error("⚠️ يرجى اختيار مادتين علفيتين على الأقل لتشغيل نظام الخلط الحسابي.")
        else:
            # 🧂 تعيين وتثبيت نسبة ملح الطعام إجبارياً وتلقائياً لكل تشغيلة لحماية الطيور والحيوانات
            salt_ratio = 0.003 if current_animal_class == "poultry" else 0.005
            
            if current_animal_class == "poultry" and "لاحم" in selected_stage:
                st.markdown('<div class="section-title">📊 النتائج والتحليل الاقتصادي المقترح للخلطة</div>', unsafe_allow_html=True)
                st.success("🎉 ممتاز جداً! تم احتساب التوليفة المتزنة لعلائق اللاحم بنجاح كامل ومتضمنة ملح الطعام ومضاد السموم الفطرية!")
                
                if "بادي" in selected_stage:
                    soy_ratio, corn_ratio, conc_ratio, lime_ratio, toxin_ratio = 0.32, (0.599 - salt_ratio), 0.05, 0.03, 0.001
                elif "نامي" in selected_stage:
                    soy_ratio, corn_ratio, conc_ratio, lime_ratio, toxin_ratio = 0.26, (0.659 - salt_ratio), 0.05, 0.03, 0.001
                else:
                    soy_ratio, corn_ratio, conc_ratio, lime_ratio, toxin_ratio = 0.20, (0.719 - salt_ratio), 0.05, 0.03, 0.001
                    
                st.session_state["last_formula"] = {
                    "الذرة الصفراء": corn_ratio * 100,
                    "كسب فول الصويا 48%": soy_ratio * 100,
                    "مركزات دواجن لاحم (5%)": conc_ratio * 100,
                    "الحجر الجيري (بودرة بلاط)": lime_ratio * 100,
                    "ملح الطعام": salt_ratio * 100,
                    "مضاد سموم فطرية وبيولوجية": toxin_ratio * 100
                }
            else:
                # المجترات، والخيول، والدجاج البياض
                success = False
                if "الذرة الصفراء" in selected_ingredients and "كسب فول الصويا 44%" in selected_ingredients:
                    success = True
                    # حجز نسبة الملح وخصمها من الذرة الصفراء للحفاظ على دقة الـ 100%
                    st.session_state["last_formula"] = {
                        "الذرة الصفراء": 65.0 - (salt_ratio * 100), 
                        "كسب فول الصويا 44%": 24.5, 
                        "البرسيم الجاف (الدريس)": 10.0,
                        "ملح الطعام": salt_ratio * 100
                    }
                elif "الشعير المطحون" in selected_ingredients:
                    success = True
                    st.session_state["last_formula"] = {
                        "الشعير المطحون": 70.0 - (salt_ratio * 100), 
                        "البرسيم الجاف (الدريس)": 29.5,
                        "ملح الطعام": salt_ratio * 100
                    }
                    
                if success:
                    st.markdown('<div class="section-title">📊 النتائج والتحليل الاقتصادي المقترح للخلطة</div>', unsafe_allow_html=True)
                    st.success("🎉 ممتاز جداً! تم احتساب التوليفة المتزنة بنجاح كامل ومتضمنة ملح الطعام التلقائي!")
                else:
                    st.markdown('<div class="custom-error-box"><span class="error-icon">❌</span>تعذر الحل الرياضي المباشر بالخامات الحالية! يرجى التأكد من تفعيل كسب الصويا والذرة والحجر الجيري وملح الطعام لتغطية الاحتياجات العالية.</div>', unsafe_allow_html=True)

            if "last_formula" in st.session_state:
                col_res1, col_res2 = st.columns([0.5, 0.5])
                with col_res1:
                    st.write("#### 📝 نسب ومقادير الخلط بالطن (1000 كجم):")
                    for k, v in st.session_state["last_formula"].items():
                        st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** / طن)")
                    st.markdown("---")
                    total_cost = sum([v/100 * prices.get(k, 450.0) for k, v in st.session_state["last_formula"].items()])
                    st.session_state["last_cost"] = total_cost
                    st.metric(label="💰 التكلفة الإجمالية الاقتصادية المحسوبة للطن الواحد:", value=f"${total_cost:.2f}")
                with col_res2:
                    st.write("#### 📊 التوزيع النسبي لمكونات العلف:")
                    st.bar_chart(st.session_state["last_formula"])

# ==================== التبويب الثاني: إدارة المزرعة والمخازن ====================
with tab_management:
    st.markdown('<div class="section-title">🚜 سجل إدارة القطيع ومخازن الأعلاف في المزرعة</div>', unsafe_allow_html=True)
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.write("### 📊 حالة القطيع الحالية")
        st.number_input("🔢 عدد رؤوس الحيوانات الكلي:", min_value=0, value=50, step=1)
        st.number_input("🍼 المواليد الجدد هذا الشهر:", min_value=0, value=4, step=1)
        st.selectbox("💉 حالة التحصين الدورية:", ["ممتازة - تم التحصين بالكامل", "متوسطة - بانتظار جرعة ديدان", "مكتملة"])
    with col_m2:
        st.write("### 📦 كميات خامات العلف بالمخزن (طن)")
        st.slider("🌽 مخزون الذرة الصفراء المتوفر:", 0.0, 50.0, 22.5)
        st.slider("🌱 مخزون كسب صويا 48% متوفر:", 0.0, 50.0, 11.0)
        st.slider("🧪 مخزون المركزات والبريمكس:", 0.0, 10.0, 3.5)
    
    st.info("💡 نصيحة اختصاصي الإنتاج الحيواني: مخزون كسب الصويا الحالي يغطي احتياجات مزرعتك لمدة 24 يوماً قادمة بناءً على معدل السحب اليومي المقدر.")

# ==================== التبويب الثالث: تسويق الأعلاف والفواتير ====================
with tab_marketing:
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
with tab_branding:
    st.markdown('<div class="section-title">🏷️ مُصمم ديباجة الدعاية وبطاقة التحليل على جوالات الأعلاف</div>', unsafe_allow_html=True)
    st.write("يقوم هذا القسم بتوليد بطاقة التحليل الفني والدعاية القانونية الملصقة على أكياس وجوالات الأعلاف الخارجة من مصنعك:")
    
    brand_name = st.text_input("🏢 اسم العمل التجاري (براند الدعاية):", "مجموعة تاور لإنتاج الأعلاف عالية الجودة")
    phone_number = st.text_input("📞 رقم هاتف المبيعات والدعم الفني:", "+218-XX-XXXXXXX")
    notes = st.text_area("📝 إرشادات استخدام وتخزين خاصة للزبائن:", "يُحفظ في مكان بارد وجاف بعيداً عن أشعة الشمس المباشرة. يُقدم للطيور حسب الجدول العمري بانتظام.")
    
    if "last_formula" in st.session_state:
        st.markdown("### 🖨️ معاينة ديباجة الجوال (جاهزة للطباعة واللصق)")
        
        st.markdown(f"""
        <div class="sack-tag">
            <h2 style="color: #1b5e20; text-align: center; margin-top:0;">🌟 {brand_name} 🌟</h2>
            <p style="text-align: center; font-weight: bold; color: #1565C0;">توصية واختيار اختصاصي الإنتاج الحيواني: م. عبد القادر إسماعيل</p>
            <hr style="border-top: 1px solid #1b5e20;">
            <h4>📊 بطاقة التحليل الفني والتركيب (لكل 1 طن):</h4>
            <ul>
                {"".join([f"<li><b>{k}:</b> {v:.2f}%</li>" for k, v in st.session_state["last_formula"].items()])}
            </ul>
            <hr style="border-top: 1px solid #1b5e20;">
            <p><b>⚠️ إرشادات الهيئة الاستشارية للإنتاج:</b> {notes}</p>
            <p style="text-align: center; font-weight: bold; color: #c62828; margin-bottom:0;">📞 لطلبات الدعم والطلب: {phone_number}</p>
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
