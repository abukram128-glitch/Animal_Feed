import streamlit as st
import numpy as np
from scipy.optimize import linprog
import json
import os

# إعدادات الصفحة
st.set_page_config(page_title="مُركّب الأعلاف الذكي", page_icon="🌾", layout="centered")

# إضافة تأثير الخلفية الطبيعية المخصصة وتنسيق الحاويات وتوقيع أسفل الصفحة بالـ CSS
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
        margin-bottom: 60px; /* مساحة إضافية للتوقيع السفلي */
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
    /* تنسيق التوقيع الاحترافي الثابت أسفل الشاشة */
    .footer-signature {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(27, 94, 32, 0.95);
        color: white;
        text-align: center;
        padding: 8px 0;
        font-size: 0.95rem;
        font-weight: bold;
        box-shadow: 0px -4px 10px rgba(0,0,0,0.2);
        z-index: 9999;
        direction: rtl;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# الحاوية البيضاء الرئيسية
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

# ----------------- 2. نظام التغذية المستهدف (بروتين يدوي وضبط تلقائي آمن للطاقة) -----------------
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

# التحكم بالبروتين يدوياً
user_protein = st.slider(
    f"🎯 حدد نسبة البروتين المرغوبة لعليقة ({selected_stage}):",
    min_value=9.0, max_value=26.0,
    value=float(req["min_protein"]),
    step=0.5
)

base_protein = float(req["min_protein"])
base_energy = float(req["min_energy"])

# تصحيح معادلة ربط الطاقة لحماية الدواجن اللاحم من الأرقام المستحيلة رياضياتياً
if current_animal_class == "poultry":
    # في الدواجن: الحفاظ على الاحتياجات القياسية للطاقة لضمان نجاح الخلطة 100% مع الخامات المتاحة
    calculated_energy = base_energy
else:
    # في المجترات والخيول: ربط ديناميكي مرن ومتناسب
    calculated_energy = base_energy + ((user_protein - base_protein) * 20)

st.warning(f"⚙️ النظام التلقائي: تم ضبط الطاقة الممثلة المستهدفة لتكون **{calculated_energy:.0f} كـ/كجم** لتتلاءم تماماً مع احتياجات الطيور والحيوانات.")

# ----------------- 3. المكتبة الشاملة وعرض الخامات والأسعار بجانب بعضها -----------------
st.markdown('<div class="section-title">💰 3. الخامات العلفية المتاحة وأسعار السوق</div>', unsafe_allow_html=True)
st.write("قم بتنشيط الخامات المتوفرة لديك في المخزن وأدخل أسعار الطن الحالية:")

selected_ingredients = []
prices = {}
ing_keys = list(ingredients.keys())
cols = st.columns(2)

for idx, name in enumerate(ing_keys):
    ing_info = ingredients[name]
    
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
            "البرسيم الجاف (الدريس)", "الشوفان", "الشعير المطحون", "مركزات دواجن لاحم (5%)", 
            "مركزات دواجن بياض (10%)", "بريمكس دواجن (لاحم/بياض)", "بريمكس مجترات (تسمين/ألبان)", 
            "بريمكس خيول (مركز)", "مضاد سموم فطرية وبيولوجية", "الحجر الجيري (بودرة بلاط)"
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

# ----------------- 4. النتائج والتحسين الرياضي الاقتصادي -----------------
st.markdown("---")
if st.button("🚀 احسب التركيبة الاقتصادية المثلى", type="primary", use_container_width=True):
    if len(selected_ingredients) < 2:
        st.error("⚠️ يرجى اختيار مادتين علفيتين على الأقل لتشغيل نظام الخلط الحسابي.")
    else:
        c = [prices[name] for name in selected_ingredients]
        A_ub = []
        b_ub = []
        
        A_ub.append([-ingredients[name]["protein"] for name in selected_ingredients])
        b_ub.append(-user_protein)
        
        A_ub.append([-ingredients[name]["energy"] for name in selected_ingredients])
        b_ub.append(-calculated_energy)
        
        A_ub.append([-ingredients[name]["calcium"] for name in selected_ingredients])
        b_ub.append(-req["min_calcium"])
        
        A_ub.append([-ingredients[name]["phosphorus"] for name in selected_ingredients])
        b_ub.append(-req["min_phosphorus"])
        
        A_eq = [[1.0 for _ in selected_ingredients]]
        b_eq = [1.0]
        
        bounds = [(0.0, ingredients[name]["max_limit"]) for name in selected_ingredients]
        
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        
        if res.success:
            st.markdown('<div class="section-title">📊 النتائج والتحليل الاقتصادي المقترح للخلطة</div>', unsafe_allow_html=True)
            st.success("🎉 ممتاز جداً! تم حل مشكلة علائق اللاحم والخيل بالكامل، وتم الوصول للتوليفة المتزنة!")
            
            chart_data = {}
            col_res1, col_res2 = st.columns([0.5, 0.5])
            with col_res1:
                st.write("#### 📝 نسب ومقادير الخلط بالطن (1000 كجم):")
                for idx, name in enumerate(selected_ingredients):
                    percentage = res.x[idx] * 100
                    if percentage > 0.01:
                        chart_data[name] = percentage
                        st.markdown(f"▪️ **{name}:** `{percentage:.2f} %` ➡️ (**{percentage*10:.1f} كجم** / طن)")
                
                st.markdown("---")
                st.metric(label="💰 التكلفة الإجمالية الاقتصادية المحسوبة للطن الواحد:", value=f"${res.fun:.2f}")
                
            with col_res2:
                st.write("#### 📊 التوزيع النسبي لمكونات العلف:")
                st.bar_chart(chart_data)
        else:
            st.error("❌ تعذر الحل الرياضي المباشر بالخامات الحالية! يرجى التأكد من تفعيل كسب الصويا 48% والمركزات لتغطية احتياجات البروتين المرتفعة.")

st.markdown('</div>', unsafe_allow_html=True)

# ----------------- التوقيع الرسمي الثابت أسفل كل صفحة -----------------
st.markdown(
    """
    <div class="footer-signature">
        🌾 برمجة وتطوير اختصاصي الإنتاج الحيواني: عبد القادر إسماعيل تاور © 2026 ⚖️
    </div>
    """,
    unsafe_allow_html=True
)
