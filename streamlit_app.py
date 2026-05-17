import streamlit as st
import numpy as np
from scipy.optimize import linprog
import json
import os

# إعدادات الصفحة
st.set_page_config(page_title="مُركّب الأعلاف الذكي", page_icon="🌾", layout="centered")

# إضافة تأثير الخلفية الطبيعية المخصصة وتنسيق الحاويات بالـ CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
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
        margin-bottom: 25px;
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
    </style>
    """,
    unsafe_allow_html=True
)

# الحاوية البيضاء الرئيسية
st.markdown('<div class="main-box">', unsafe_allow_html=True)

# واجهة الشعار والعناوين الرسمية مع خط عريض باللون الأحمر لاسمك الكريم
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

# ----------------- 1. دالة تقدير أوزان الخيول والأبقار حstandard -----------------
st.markdown('<div class="section-title">⚖️ 1. نظام قياس وتقدير أوزان الحيوانات ميدانياً</div>', unsafe_allow_html=True)

animal_for_weight = st.radio("اختر فئة الحيوان المراد وزنه:", ["أبقار (محلي/هجين)", "خيول"], horizontal=True)

col_w1, col_w2 = st.columns(2)
with col_w1:
    heart_girth = st.number_input("📏 محيط الصدر (سم - خلف القوائم الأمامية):", min_value=40.0, value=160.0, step=1.0)
with col_w2:
    body_length = st.number_input("📏 طول الجسم (سم - من الكتف إلى دبوس الورك):", min_value=40.0, value=140.0, step=1.0)

if animal_for_weight == "أبقار (محلي/هجين)":
    # معادلة الأبقار: (محيط الصدر² * الطول) / 10838
    estimated_weight = (heart_girth ** 2 * body_length) / 10838
else:
    # معادلة الخيول: (محيط الصدر² * الطول) / 11877
    estimated_weight = (heart_girth ** 2 * body_length) / 11877

st.info(f"💡 الوزن التقديري المحسوب للحيوان حاملاً: **{estimated_weight:.1f} كجم**")

# ----------------- 2. نظام التغذية المستهدف (اختيارات أفقية) -----------------
st.markdown('<div class="section-title">📋 2. نظام التغذية المستهدف</div>', unsafe_allow_html=True)

selected_cat = st.radio("اختر نوع الحيوان الأساسي للتركيبة العلفية:", ["المجترات", "الدواجن", "الخيول"], horizontal=True)

if selected_cat == "المجترات":
    sub_list = [k for k in requirements.keys() if "المجترات" in k]
elif selected_cat == "الدواجن":
    sub_list = [k for k in requirements.keys() if "الدواجن" in k]
else:
    sub_list = [k for k in requirements.keys() if "الخيول" in k]

selected_stage = st.selectbox("اختر المرحلة الإنتاجية / العمرية الدقيقة:", sub_list)
req = requirements[selected_stage]
current_animal_class = req["class"]

st.success(f"📍 الاحتياجات القياسية المعتمدة: بروتين ≥ {req['min_protein']}% | طاقة ممثلة ≥ {req['min_energy']} كـ/كجم")

# ----------------- 3. المكتبة الشاملة وعرض الخامات والأسعار بجانب بعضها -----------------
st.markdown('<div class="section-title">💰 3. الخامات العلفية المتاحة (المكتبة الشاملة المحدثة)</div>', unsafe_allow_html=True)
st.write("قم بتنشيط الخامات وإدخال أسعار السوق الحالية لتشغيل محرك الحساب الخطي الاقتصادي:")

selected_ingredients = []
prices = {}

ing_keys = list(ingredients.keys())
cols = st.columns(2)

for idx, name in enumerate(ing_keys):
    ing_info = ingredients[name]
    
    # فلترة تلقائية وذكية: اختيار البريمكس ومضاد السموم بناءً على نوع الحيوان المختار
    if ing_info["type"] == "poultry_only" and current_animal_class != "poultry":
        continue
    if ing_info["type"] == "ruminant_premix" and current_animal_class != "ruminant":
        continue
    if ing_info["type"] == "poultry_premix" and current_animal_class != "poultry":
        continue
    if ing_info["type"] == "horse_premix" and current_animal_class != "horse":
        continue
        
    with cols[idx % 2]:
        # جعل الخامات والبريمكس المناسب نشطة بشكل افتراضي منعا للأخطاء الرياضية
        is_default = name in ["الذرة البيضاء", "البرسيم الجاف (الدريس)", "مركزات دواجن (لاحم + بياض)", "الذرة الصفراء", "كسب فول الصويا 44%", "بريمكس دواجن", "بريمكس مجترات", "بريمكس خيول", "مضاد سموم فطرية (دواجن)", "الحجر الجيري"]
        
        c_col1, c_col2 = st.columns([0.65, 0.35])
        with c_col1:
            activated = st.checkbox(name, value=is_default, key=f"chk_{name}")
        with c_col2:
            default_price = 150.0 if "بريمكس" in name or "سموم" in name or "ملح" in name else 450.0
            price = st.number_input("السعر / طن", min_value=0.0, value=default_price, key=f"prc_{name}", label_visibility="collapsed")
            
        if activated:
            selected_ingredients.append(name)
            prices[name] = price

# ----------------- 4. النتائج والتحسين الرياضي -----------------
st.markdown("---")
if st.button("🚀 احسب التركيبة الاقتصادية المثلى", type="primary", use_container_width=True):
    if len(selected_ingredients) < 2:
        st.error("⚠️ يرجى اختيار مادتين علفيتين على الأقل لتشغيل معادلة الحل الخطي.")
    else:
        c = [prices[name] for name in selected_ingredients]
        A_ub = []
        b_ub = []
        
        A_ub.append([-ingredients[name]["protein"] for name in selected_ingredients])
        b_ub.append(-req["min_protein"])
        
        A_ub.append([-ingredients[name]["energy"] for name in selected_ingredients])
        b_ub.append(-req["min_energy"])
        
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
            st.success("🎉 ممتاز! تم حساب التوليفة العلفية الأقل تكلفة ومطابقة للاحتياجات الكيميائية بنجاح!")
            
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
                # استخدام أداة بار المخططات المدمجة لضمان التشغيل الفوري والآمن
                st.bar_chart(chart_data)
                
        else:
            st.error("❌ لم يتم الوصول لحل رياضي متوازن! يرجى التأكد من تنشيط مواد علفية كافية غنية بالبروتين والطاقة كـ (مركزات الدواجن وكسب الصويا والذرة) لتلبية الاحتياجات الكيميائية المرتفعة.")

st.markdown('</div>', unsafe_allow_html=True)
