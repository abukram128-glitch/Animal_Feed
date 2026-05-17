import streamlit as st
import numpy as np
from scipy.optimize import linprog
import json
import os

# إعدادات الصفحة
st.set_page_config(page_title="مُركّب الأعلاف الذكي", page_icon="🌾", layout="centered")

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
    /* تصميم مخصص لرسالة تعذر الحل: نص أسود وعلامة خطأ حمراء */
    .custom-error-box {
        background-color: #ffebee;
        border-right: 6px solid #c62828;
        padding: 15px;
        border-radius: 8px;
        color: #000000; /* نص باللون الأسود */
        font-weight: bold;
        text-align: right;
        margin-top: 15px;
        direction: rtl;
    }
    .custom-error-box .error-icon {
        color: #c62828; /* علامة الخطأ باللون الأحمر */
        font-size: 1.3rem;
        margin-left: 8px;
    }
    /* التوقيع المصغر الأنيق في جهة اليسار بأسفل الشاشة */
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

# ----------------- 2. نظام التغذية المستهدف -----------------
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

# ضبط موازنة الطاقة
if current_animal_class == "poultry":
    calculated_energy = base_energy
else:
    calculated_energy = base_energy + ((user_protein - base_protein) * 20)

st.warning(f"⚙️ النظام التلقائي: تم ضبط الطاقة الممثلة المستهدفة لتكون **{calculated_energy:.0f} كـ/كجم** لتتلاءم مع نسبة البروتين المحددة.")

# ----------------- 3. المكتبة الشاملة وعرض الخامات والأسعار بجانب بعضها -----------------
st.markdown('<div class="section-title">💰 3. الخامات العلفية المتاحة وأسعار السوق</div>', unsafe_allow_html=True)
st.write("قم بتنشيط الخامات المتوفرة لديك في المخزن وأدخل أسعار الطن الحالية:")

selected_ingredients = []
prices = {}
ing_keys = list(ingredients.keys())
cols = st.columns(2)

for idx, name in enumerate(ing_keys):
    ing_info = ingredients[name]
    
    # 1. فلترة ومنع تداخل خامات الألياف غير المناسبة نهائياً مع الدواجن
    if current_animal_class == "poultry" and name in ["البرسيم الجاف (الدريس)", "النخالة (الردة)", "الشعير المطحون", "الشوفان", "كسب عباد الشمس 36%"]:
        continue

    # 2. الفصل الصارم بين مركز اللاحم ومركز البياض لمنع الخلط الخاطئ علمياً
    if current_animal_class == "poultry":
        if "لاحم" in selected_stage and "بياض" in name:
            continue
        if "بياض" in selected_stage and "لاحم" in name:
            continue
        
    if ing_info["type"] == "poultry_only" and current_animal_class != "poultry" :
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
        
        adjusted_bounds = []
        for name in selected_ingredients:
            if "الحجر الجيري" in name or "DCP" in name:
                adjusted_bounds.append((0.0, 0.08)) 
            else:
                adjusted_bounds.append((0.0, ingredients[name]["max_limit"]))
        
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=adjusted_bounds, method='highs')
        
        if res.success:
            st.markdown('<div class="section-title">📊 النتائج والتحليل الاقتصادي المقترح للخلطة</div>', unsafe_allow_html=True)
            st.success("🎉 ممتاز جداً! تم احتساب التوليفة المتزنة وحل مشكلة علائق اللاحم بنجاح كامل!")
            
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
            # رسالة تعذر الحل المخصصة بطلبك: نص أسود وعلامة خطأ حمراء تفادياً للتشويه
            st.markdown(
                """
                <div class="custom-error-box">
                    <span class="error-icon">❌</span>
                    تعذر الحل الرياضي المباشر بالخامات الحالية! يرجى التأكد من تفعيل كسب الصويا 48% والمركزات والحجر الجيري لتغطية الاحتياجات العالية.
                </div>
                """, 
                unsafe_allow_html=True
            )

st.markdown('</div>', unsafe_allow_html=True)

# ----------------- التوقيع المصغر والمطور في أقصى اليسار -----------------
st.markdown(
    """
    <div class="mini-left-signature">
        👨‍🔬 م. عبد القادر إسماعيل تاور © 2026
    </div>
    """,
    unsafe_allow_html=True
)
