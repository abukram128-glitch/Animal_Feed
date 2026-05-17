import streamlit as st
import numpy as np
from scipy.optimize import linprog
import json
import os

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="مُركّب الأعلاف الذكي", page_icon="🌾", layout="wide")

# إضافة تأثير الخلفية الطبيعية الخضراء التي اخترتها باستخدام CSS مدمج ومحسن للرؤية
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    /* جعل الحاويات والنصوص واضحة فوق الخلفية الطبيعية */
    .block-container {
        background-color: rgba(255, 255, 255, 0.92);
        padding: 30px !important;
        border-radius: 15px;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# واجهة المستخدم الرسمية باسمك وتخصصك المعتمد
st.markdown("<h1 style='text-align: center; color: #2E7D32; font-family: Cairo, sans-serif;'>برنامج تركيب الأعلاف الذكي 🌾</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #1565C0; font-family: Cairo, sans-serif;'>تصميم اختصاصي الإنتاج الحيواني: عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic; color: #444;'>نظام برمجيات الحساب الخطي للأعلاف بأقل تكلفة اقتصادية ممكنة (Least-Cost Ration)</p>", unsafe_allow_html=True)
st.markdown("---")

# التحقق من وجود ملف قاعدة البيانات
db_file = "feeds_db.json"
if not os.path.exists(db_file):
    st.error(f"تنبيه: ملف قاعدة البيانات المحدث `{db_file}` غير موجود في مستودعك الحالي.")
    st.stop()

with open(db_file, "r", encoding="utf-8") as f:
    data = json.load(f)

ingredients = data["ingredients"]
requirements = data["requirements"]

# 1. قائمة التصنيفات الحيوانية المستهدفة
st.header("📋 1. نظام التغذية والتصنيف المستهدف")
category = st.selectbox("اختر فئة الحيوان الرئيسية:", ["المجترات (أبقار، أغنام، ماعز)", "الدواجن", "الخيول"])

if category == "المجترات (أبقار، أغنام، ماعز)":
    sub_list = [k for k in requirements.keys() if "المجترات" in k]
elif category == "الدواجن":
    sub_list = [k for k in requirements.keys() if "الدواجن" in k]
else:
    sub_list = [k for k in requirements.keys() if "الخيول" in k]

selected_stage = st.selectbox("اختر المرحلة الإنتاجية / العمرية الدقيقة:", sub_list)
req = requirements[selected_stage]

st.info(f"📍 الاحتياجات القياسية لـ ({selected_stage}): بروتين خام ≥ {req['min_protein']}% | طاقة ممثلة ≥ {req['min_energy']} كـ/كجم | كالسيوم ≥ {req['min_calcium']}% | فسفور متاح ≥ {req['min_phosphorus']}%")

# 2. المكتبة الشاملة لأسعار الخامات العلفية المتاحة في السوق
st.header("💰 2. أسعار الخامات العلفية المتاحة (المكتبة الشاملة المحدثة)")
st.write("الرجاء إدخال الأسعار الحالية بالسوق لتفعيل الحساب الاقتصادي:")

prices = {}
ing_list = list(ingredients.keys())

# توزيع الخامات في 3 أعمدة منسقة وأنيقة
cols = st.columns(3)
for idx, name in enumerate(ing_list):
    with cols[idx % 3]:
        # وضع قيمة افتراضية تناسب الخامات المركزة والعادية لتسهيل التجربة الافتراضية
        default_val = 150.0 if any(x in name for x in ["بريمكس", "ملح", "حجر"]) else 450.0
        prices[name] = st.number_input(f"🌾 {name} (للطن)", min_value=0.0, value=default_val, step=10.0, key=f"p_{idx}")

# إجراء عمليات التحسين الرياضي وحساب النسب المطلوبة
st.markdown("---")
if st.button("🚀 احسب التركيبة الاقتصادية المثلى", type="primary"):
    
    c = [prices[name] for name in ing_list]
    A_ub = []
    b_ub = []
    
    # تحويل قيود الحد الأدنى لتتوافق مع خوارزمية linprog
    A_ub.append([-ingredients[name]["protein"] for name in ing_list])
    b_ub.append(-req["min_protein"])
    
    A_ub.append([-ingredients[name]["energy"] for name in ing_list])
    b_ub.append(-req["min_energy"])
    
    A_ub.append([-ingredients[name]["calcium"] for name in ing_list])
    b_ub.append(-req["min_calcium"])
    
    A_ub.append([-ingredients[name]["phosphorus"] for name in ing_list])
    b_ub.append(-req["min_phosphorus"])
    
    # قيد مجموع نسب الخامات الإجمالية = 100%
    A_eq = [[1.0 for _ in ing_list]]
    b_eq = [1.0]
    
    # حدود الأمان القصوى لكل خامة بالمكتبة
    bounds = [(0.0, ingredients[name]["max_limit"]) for name in ing_list]
    
    # تشغيل محرك الحل الخطي الاحترافي العالي الكفاءة
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    if res.success:
        st.success("🎉 ممتاز! تم الوصول إلى التركيبة العلفية الاقتصادية الموصى بها ميكانيكياً بنجاح!")
        st.write("### 📋 نسب ومقادير الخلط لكل طن (1000 كجم):")
        
        for idx, name in enumerate(ing_list):
            percentage = res.x[idx] * 100
            if percentage > 0.05:
                st.markdown(f"▪️ **{name}:** `{percentage:.2f} %` (أي ما يعادل **{percentage*10:.1f} كجم** لكل طن علف)")
                
        st.markdown("---")
        st.metric(label="💰 التكلفة الإجمالية المحسوبة للطن المستهدف بالكامل", value=f"${res.fun:.2f}")
    else:
        st.error("❌ تعذر العثور على توليفة رياضية متوازنة! يرجى مراجعة وتعديل قيم أسعار الخامات أو تخفيف قيود المكونات للسماح بتلبية الاحتياجات الغذائية العالية لخلطة الدجاج المطلوبة.")
