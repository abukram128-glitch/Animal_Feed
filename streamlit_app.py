import streamlit as st
import numpy as np
from scipy.optimize import linprog
import json
import os
import plotly.express as px

# إعدادات الصفحة المتقدمة لتطابق جودة الصورة
st.set_page_config(page_title="مركب الأعلاف الذكي", page_icon="🌾", layout="centered")

# دمج الخلفية الطبيعية الحقلية المخصصة وتنسيق الحاويات والنصوص بالـ CSS
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
        background-color: rgba(255, 255, 255, 0.95);
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
        font-size: 1.3rem;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# الحاوية البيضاء الرئيسية الحاضنة للتطبيق
st.markdown('<div class="main-box">', unsafe_allow_html=True)

# الهوية واللوجو المعتمد (القرون والكتكوت والسنبلة)
logo_url = "https://i.ibb.co/3yk7YFv/animal-feed-logo.png" # رابط افتراضي متناسق، يمكنك استبداله
st.image("https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=400&auto=format&fit=crop", width=150, use_container_width=False)

st.markdown("<h1 style='color: #2E7D32; margin-top:0;'>مُركّب الأعلاف الذكي 🌾</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #1565C0; margin-bottom: 5px;'>تصميم اختصاصي الإنتاج الحيواني</h3>", unsafe_allow_html=True)
st.markdown("<h2 style='color: #c62828; font-weight: bold; margin-top: 0;'>عبد القادر إسماعيل تاور</h2>", unsafe_allow_html=True)
st.markdown("---")

# تحميل قاعدة البيانات
db_file = "feeds_db.json"
if not os.path.exists(db_file):
    st.error("خطأ: لم يتم العثور على ملف `feeds_db.json`. يرجى إنشاؤه في مسار المشروع.")
    st.stop()

with open(db_file, "r", encoding="utf-8") as f:
    data = json.load(f)

ingredients = data["ingredients"]
requirements = data["requirements"]

# ----------------- القسم الأول: حساب أوزان الحيوانات ميدانياً -----------------
st.markdown('<div class="section-title">⚖️ دالة قياس وتقدير أوزان الحيوانات ميدانياً</div>', unsafe_allow_html=True)
st.write("أداة حقلية دقيقة لحساب الوزن التقريبي للحيوان بدون ميزان لتحديد الحصص العلفية بدقة:")

animal_type_weight = st.radio("اختر فئة الحيوان المراد وزنه:", ["أبقار (محلي/هجين)", "خيول"], horizontal=True)

col_w1, col_w2 = st.columns(2)
with col_w1:
    heart_girth = st.number_input("📏 محيط الصدر (بالسنتمتر - خلف القوائم الأمامية مباشرة):", min_value=50.0, value=160.0, step=1.0)
with col_w2:
    body_length = st.number_input("📏 طول الجسم (بالسنتمتر - من مفصل الكتف إلى دبوس الورك):", min_value=50.0, value=140.0, step=1.0)

if animal_type_weight == "أبقار (محلي/هجين)":
    # معادلة الأبقار الشهيرة لتقدير الأوزان بالمتر: (محيط الصدر ^ 2 * الطول) / 10838
    calculated_weight = (heart_girth ** 2 * body_length) / 10838
else:
    # معادلة الخيول المعتمدة عالمياً: (محيط الصدر ^ 2 * الطول) / 11877
    calculated_weight = (heart_girth ** 2 * body_length) / 11877

st.info(f"💡 الوزن التقديري المحسوب للحيوان هو تقريباً: **{calculated_weight:.1f} كجم**")

# ----------------- القسم الثاني: نظام التغذية المستهدف (أفقي كالصورة) -----------------
st.markdown('<div class="section-title">📋 نظام التغذية المستهدف</div>', unsafe_allow_html=True)

# عرض فئات الحيوان أفقياً تماماً كالصورة المرفقة
cat_options = ["المجترات", "الدواجن", "الخيول"]
selected_cat = st.radio("اختر نوع الحيوان الأساسي:", cat_options, horizontal=True)

# تصفية المراحل بناءً على الاختيار
if selected_cat == "المجترات":
    sub_list = [k for k in requirements.keys() if "المجترات" in k]
elif selected_cat == "الدواجن":
    sub_list = [k for k in requirements.keys() if "الدواجن" in k]
else:
    sub_list = [k for k in requirements.keys() if "الخيول" in k]

selected_stage = st.selectbox("اختر المرحلة الإنتاجية / العمرية بدقة:", sub_list)
req = requirements[selected_stage]

# تحديد نوع البريمكس وضبط القيود آلياً بناءً على تصنيف الاختيار الفعلي للحيوان
current_animal_class = req["class"]

st.success(f"🎯 الهدف النشط: بروتين ≥ {req['min_protein']}% | طاقة ≥ {req['min_energy']} كجم | كالسيوم ≥ {req['min_calcium']}%")

# ----------------- القسم الثالث: الخامات العلفية المتاحة والأسعار -----------------
st.markdown('<div class="section-title">💰 الخامات العلفية المتاحة (المكتبة الشاملة المحدثة)</div>', unsafe_allow_html=True)
st.write("قم بتحديد الخامات المتوفرة لديك في المخزن أو السوق وأدخل أسعارها الحالية:")

selected_ingredients = []
prices = {}

# عرض المكونات في جدول منظم أفقياً وعامودياً
ing_keys = list(ingredients.keys())
cols = st.columns(2)

for idx, name in enumerate(ing_keys):
    ing_info = ingredients[name]
    
    # فلترة آلية وذكية لاستبعاد المكونات أو البريمكسات غير المتوافقة مع نوع الحيوان المختار
    if ing_info["type"] == "poultry_only" and current_animal_class != "poultry":
        continue
    if ing_info["type"] == "ruminant_premix" and current_animal_class != "ruminant":
        continue
    if ing_info["type"] == "poultry_premix" and current_animal_class != "poultry":
        continue
    if ing_info["type"] == "horse_premix" and current_animal_class != "horse":
        continue
        
    with cols[idx % 2]:
        # جعل المواد الأساسية مختارة تلقائياً لتسهيل العمل وتجنب الأخطاء الرياضية
        is_default = name in ["الذرة الصفراء", "الذرة البيضاء", "كسب فول الصويا 44%", "البرسيم الجاف (الدريس)", "مركزات دواجن (لاحم + bياض)", "بريمكس دواجن", "بريمكس مجترات", "بريمكس خيول", "مضاد سموم فطرية (دواجن)", "الحجر الجيري"]
        
        # صندوق الاختيار ومعه حقل السعر بجانبه تماماً
        c_col1, c_col2 = st.columns([0.6, 0.4])
        with c_col1:
            activated = st.checkbox(name, value=is_default, key=f"chk_{name}")
        with c_col2:
            default_price = 120.0 if "بريمكس" in name or "سموم" in name or "ملح" in name else 480.0
            price = st.number_input("السعر / طن", min_value=0.0, value=default_price, key=f"prc_{name}", label_visibility="collapsed")
            
        if activated:
            selected_ingredients.append(name)
            prices[name] = price

# ----------------- القسم الرابع: التحسين الخطي وحساب النتائج المتقدمة -----------------
st.markdown("---")
if st.button("🚀 احسب التركيبة الاقتصادية المثلى", type="primary", use_container_width=True):
    if len(selected_ingredients) < 2:
        st.error("⚠️ يرجى اختيار مادتين علفيتين على الأقل لتمكين النظام من الخلط والحساب الخطي.")
    else:
        # إعداد مصفوفات الـ Linear Programming
        c = [prices[name] for name in selected_ingredients]
        A_ub = []
        b_ub = []
        
        # قيد البروتين الخام الأدنى
        A_ub.append([-ingredients[name]["protein"] for name in selected_ingredients])
        b_ub.append(-req["min_protein"])
        
        # قيد الطاقة الأدنى
        A_ub.append([-ingredients[name]["energy"] for name in selected_ingredients])
        b_ub.append(-req["min_energy"])
        
        # قيد الكالسيوم الأدنى
        A_ub.append([-ingredients[name]["calcium"] for name in selected_ingredients])
        b_ub.append(-req["min_calcium"])
        
        # قيد الفسفور الأدنى
        A_ub.append([-ingredients[name]["phosphorus"] for name in selected_ingredients])
        b_ub.append(-req["min_phosphorus"])
        
        # قيد المجموع الكلي = 100%
        A_eq = [[1.0 for _ in selected_ingredients]]
        b_eq = [1.0]
        
        # تعيين حدود الأمان القصوى للمواد المدخلة
        bounds = [(0.0, ingredients[name]["max_limit"]) for name in selected_ingredients]
        
        # تشغيل الخوارزمية الرياضية (Highs Solver)
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        
        if res.success:
            st.markdown('<div class="section-title">📊 النتائج والتحليل الكيميائي المقترح بالطن</div>', unsafe_allow_html=True)
            st.success("🎉 تم العثور على خلطة علفية متزنة تلبي الاحتياجات بأقل تكلفة مالية ممكنة في السوق!")
            
            # تجهيز بيانات الرسم البياني
            labels = []
            values = []
            
            col_res1, col_res2 = st.columns([0.5, 0.5])
            
            with col_res1:
                st.write("#### 📝 المقادير المطلوبة لكل 1 طن (1000 كجم):")
                for idx, name in enumerate(selected_ingredients):
                    percentage = res.x[idx] * 100
                    if percentage > 0.01:
                        labels.append(name)
                        values.append(percentage)
                        st.markdown(f"▪️ **{name}:** `{percentage:.2f} %` ➡️ (**{percentage*10:.2f} كجم** / طن)")
                
                st.markdown("---")
                st.metric(label="💰 التكلفة الإجمالية الاقتصادية المحسوبة للطن الواحد:", value=f"${res.fun:.2f}")
                
            with col_res2:
                st.write("#### 🍩 الرسم البياني الدائري للخلطة (مطابق للصورة):")
                fig = px.pie(names=labels, values=values, hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
                
        else:
            st.error("❌ لم يتم العثور على حل رياضي متوازن! يرجى التأكد من تفعيل مواد غنية بالبروتين والطاقة مرتفعة القيمة الغذائية (مثل كسب الصويا والمركزات ومضاد السموم ومكملات الكالسيوم) لتغطية احتياجات الطيور أو المواشي المرتفعة.")

st.markdown('</div>', unsafe_allow_html=True)
