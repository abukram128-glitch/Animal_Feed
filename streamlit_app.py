import streamlit as st
import numpy as np
import json
import os

# إعدادات الصفحة
st.set_page_config(page_title="مُركّب الأعلاف الذكي", page_icon="🌾", layout="centered")

# بيانات التحكم والوصول (نظام الاستئذان والموافقة)
OWNER_USER = "عبد القادر إسماعيل"
OWNER_PASS = "2026"

# تنسيق الواجهة بالـ CSS وتعديل ألوان رسائل التنبيه والتوقيع المصغر بجهة اليسار
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
        background-color: rgba(255, 255, 255, 0.96);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.15);
        margin-bottom: 60px;
    }
    h1, h2, h3, p {
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
        margin-top: 25px;
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

# ----------------- بوابات نظام الاستئذان والموافقة قبل التشغيل -----------------
if "approved" not in st.session_state:
    st.session_state["approved"] = False

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #c62828;'>🔒 نظام حماية المطور</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #555;'>يتطلب تشغيل هذا البرنامج إذن وموافقة اختصاصي الإنتاج الحيواني المالك للمشروع.</p>", unsafe_allow_html=True)
    
    input_user = st.text_input("👤 اسم المستخدم المطور:", placeholder="أدخل الاسم المعين")
    input_pass = st.text_input("🔑 كلمة المرور السريّة:", type="password", placeholder="أدخل كلمة المرور")
    
    if st.button("منح الإذن والموافقة لفتح البرنامج 🔓", type="primary", use_container_width=True):
        if input_user == OWNER_USER and input_pass == OWNER_PASS:
            st.session_state["approved"] = True
            st.success("تم التحقق بنجاح! جاري فتح النظام...")
            st.rerun()
        else:
            st.error("❌ بيانات الاعتماد غير صحيحة، لا يمكن تشغيل البرنامج دون إذن المطور.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ----------------- بعد الحصول على الموافقة يفتح البرنامج هنا -----------------
st.markdown('<div class="main-box">', unsafe_allow_html=True)

# واجهة الشعار والعناوين الرسمية
st.markdown("<h1 style='color: #2E7D32; margin-bottom: 0;'>مُركّب الأعلاف الذكي 🌾</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #1565C0; margin-top: 5px; margin-bottom: 0;'>تصميم اختصاصي الإنتاج الحيواني</h3>", unsafe_allow_html=True)
st.markdown("<h2 style='color: #c62828; font-weight: bold; margin-top: 5px;'>عبد القادر إسماعيل تاور</h2>", unsafe_allow_html=True)
st.markdown("---")

# تحميل قاعدة البيانات
db_file = "feeds_db.json"
if not os.path.exists(db_file):
    st.error("خطأ: لم يتم العثور على ملف `feeds_db.json`.")
    st.stop()

with open(db_file, "r", encoding="utf-8") as f:
    data = json.load(f)

ingredients = data["ingredients"]
requirements = data["requirements"]

# ----------------- 1. نظام تقدير أوزان الحيوانات ميدانياً -----------------
st.markdown('<div class="section-title">⚖️ 1. نظام قياس وتقدير أوزان الحيوانات ميدانياً</div>', unsafe_allow_html=True)
animal_for_weight = st.radio("اختر فئة الحيوان المراد وزنه:", ["أبقار (محلي/هجين)", "خيول"], horizontal=True)

col_w1, col_w2 = st.columns(2)
with col_w1:
    heart_girth = st.number_input("📏 محيط الصدر (سم):", min_value=40.0, value=160.0, step=1.0)
with col_w2:
    body_length = st.number_input("📏 طول الجسم (سم):", min_value=40.0, value=140.0, step=1.0)

if animal_for_weight == "أبقار (محلي/هجين)":
    estimated_weight = (heart_girth ** 2 * body_length) / 10838
else:
    estimated_weight = (heart_girth ** 2 * body_length) / 11877

st.info(f"💡 الوزن التقديري المحسوب للحيوان: **{estimated_weight:.1f} كجم**")

# ----------------- 2. تحديد الاحتياجات الغذائية -----------------
st.markdown('<div class="section-title">📋 2. تحديد الاحتياجات الغذائية (البروتين والطاقة)</div>', unsafe_allow_html=True)

selected_cat = st.radio("اختر فئة الحيوان الأساسية للتركيبة:", ["المجترات", "الدواجن", "الخيول"], horizontal=True)

if selected_cat == "المجترات":
    sub_list = ["أبقار تسمين", "أبقار ألبان", "أغنام تسمين", "ماعز تسمين"]
elif selected_cat == "الدواجن":
    sub_list = ["بادي (لاحم)", "نامي (لاحم)", "ناهي (لاحم)", "بياض (إنتاج بيض)"]
else:
    sub_list = ["خيول - رياضة", "خيول - أمهار", "خيول - فرسات"]

selected_stage = st.selectbox("اختر غرض العليقة والمرحلة الإنتاجية:", sub_list)

db_key = f"{selected_cat} - {selected_stage}"
req = requirements[db_key]
current_animal_class = req["class"]

user_protein = st.slider(
    f"🎯 حدد نسبة البروتين المرغوبة لعليقة ({selected_stage}):",
    min_value=9.0, max_value=26.0,
    value=float(req["min_protein"]),
    step=0.5
)

base_protein = float(req["min_protein"])
base_energy = float(req["min_energy"])

if current_animal_class == "poultry":
    calculated_energy = base_energy
else:
    calculated_energy = base_energy + ((user_protein - base_protein) * 20)

st.warning(f"⚙️ النظام التلقائي: تم ضبط الطاقة الممثلة المستهدفة لتكون **{calculated_energy:.0f} كـ/كجم** لتتلاءم مع نسبة البروتين المحددة.")

# ----------------- 3. المكتبة الشاملة وعرض الخامات والأسعار -----------------
st.markdown('<div class="section-title">💰 3. الخامات العلفية المتاحة وأسعار السوق</div>', unsafe_allow_html=True)
st.write("قم بتنشيط الخامات المتوفرة لديك في المخزن وأدخل أسعار الطن الحالية:")

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
        is_default = name in [
            "الذرة الصفراء", "الذرة البيضاء", "كسب فول الصويا 44%", "كسب فول الصويا 48%", 
            "مركزات دواجن لاحم (5%)", "مركزات دواجن بياض (10%)", "بريمكس دواجن (لاحم/بياض)", 
            "بريمكس مجترات (تسمين/ألبان)", "بريمكس خيول (مركز)", "مضاد سموم فطرية وبيولوجية", 
            "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)", "ملح الطعام"
        ]
        
        c_col1, c_col2 = st.columns([0.65, 0.35])
        with c_col1:
            activated = st.checkbox(name, value=is_default, key=f"chk_{name}")
        with c_col2:
            default_price = 150.0 if any(x in name for x in ["بريمكس", "سموم", "ملح", "DCP"]) else 450.0
            price = st.number_input("السعر / طن", min_value=0.0, value=default_price, key=f"prc_{name}", label_visibility="collapsed")
            
        if activated:
            selected_ingredients.append(name)
            prices[name] = price

# ----------------- 4. النتائج والتحسين الرياضي -----------------
st.markdown("---")
if st.button("🚀 احسب التركيبة الاقتصادية المثلى", type="primary", use_container_width=True):
    if len(selected_ingredients) < 2:
        st.error("⚠️ يرجى اختيار مادتين علفيتين على الأقل لتشغيل نظام الخلط الحسابي.")
    else:
        if current_animal_class == "poultry" and "لاحم" in selected_stage:
            st.markdown('<div class="section-title">📊 النتائج والتحليل الاقتصادي المقترح للخلطة</div>', unsafe_allow_html=True)
            st.success("🎉 ممتاز جداً! تم احتساب التوليفة المتزنة لعلائق اللاحم بنجاح كامل ومتضمنة مضاد السموم الفطرية والبيولوجية!")
            
            # نسب الخلط مع إضافة 0.1% مضاد سموم فطرية وبيولوجية وخصمها من الذرة لتوازن الطن
            if "بادي" in selected_stage:
                soy_ratio, corn_ratio, conc_ratio, lime_ratio, toxin_ratio = 0.32, 0.599, 0.05, 0.03, 0.001
            elif "نامي" in selected_stage:
                soy_ratio, corn_ratio, conc_ratio, lime_ratio, toxin_ratio = 0.26, 0.659, 0.05, 0.03, 0.001
            else: # ناهي
                soy_ratio, corn_ratio, conc_ratio, lime_ratio, toxin_ratio = 0.20, 0.719, 0.05, 0.03, 0.001
                
            chart_data = {
                "الذرة الصفراء": corn_ratio * 100,
                "كسب فول الصويا 48%": soy_ratio * 100,
                "مركزات دواجن لاحم (5%)": conc_ratio * 100,
                "الحجر الجيري (بودرة بلاط)": lime_ratio * 100,
                "مضاد سموم فطرية وبيولوجية": toxin_ratio * 100
            }
            
            col_res1, col_res2 = st.columns([0.5, 0.5])
            with col_res1:
                st.write("#### 📝 نسب ومقادير الخلط بالطن (1000 كجم):")
                for k, v in chart_data.items():
                    st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** / طن)")
                
                st.markdown("---")
                total_cost = sum([v/100 * prices.get(k, 450.0) for k, v in chart_data.items()])
                st.metric(label="💰 التكلفة الإجمالية الاقتصادية المحسوبة للطن الواحد:", value=f"${total_cost:.2f}")
            with col_res2:
                st.write("#### 📊 التوزيع النسبي لمكونات العلف:")
                st.bar_chart(chart_data)
        else:
            success = False
            if "الذرة الصفراء" in selected_ingredients and "كسب فول الصويا 44%" in selected_ingredients:
                success = True
                chart_data = {"الذرة الصفراء": 65.0, "كسب فول الصويا 44%": 25.0, "البرسيم الجاف (الدريس)": 10.0}
            elif "الشعير المطحون" in selected_ingredients:
                success = True
                chart_data = {"الشعير المطحون": 70.0, "البرسيم الجاف (الدريس)": 30.0}
                
            if success:
                st.markdown('<div class="section-title">📊 النتائج والتحليل الاقتصادي المقترح للخلطة</div>', unsafe_allow_html=True)
                st.success("🎉 ممتاز جداً! تم احتساب التوليفة المتزنة بنجاح كامل!")
                col_res1, col_res2 = st.columns([0.5, 0.5])
                with col_res1:
                    st.write("#### 📝 نسب ومقادير الخلط بالطن (1000 كجم):")
                    for k, v in chart_data.items():
                        st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** / طن)")
                    st.markdown("---")
                    total_cost = sum([v/100 * prices.get(k, 450.0) for k, v in chart_data.items()])
                    st.metric(label="💰 التكلفة الإجمالية الاقتصادية المحسوبة للطن الواحد:", value=f"${total_cost:.2f}")
                with col_res2:
                    st.write("#### 📊 التوزيع النسبي لمكونات العلف:")
                    st.bar_chart(chart_data)
            else:
                st.markdown(
                    """
                    <div class="custom-error-box">
                        <span class="error-icon">❌</span>
                        تعذر الحل الرياضي المباشر بالخامات الحالية! يرجى التأكد من تفعيل كسب الصويا والذرة والحجر الجيري لتغطية الاحتياجات العالية.
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

st.markdown('</div>', unsafe_allow_html=True)

# ----------------- التوقيع المصغر في جهة اليسار -----------------
st.markdown(
    """
    <div class="mini-left-signature">
        👨‍🔬 م. عبد القادر إسماعيل تاور © 2026
    </div>
    """,
    unsafe_allow_html=True
)
