import streamlit as st
import numpy as np
from scipy.optimize import linprog
import json
import os

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="مُركّب الأعلاف الذكي", page_icon="🌾", layout="wide")

# واجهة المستخدم وإبراز الاسم واللقب الاحترافي
st.markdown("<h1 style='text-align: center; color: #2E7D32;'>برنامج تركيب الأعلاف الذكي 🌾</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #1565C0;'>تصميم اختصاصي الإنتاج الحيواني: عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic;'>نظام حساب العلائق الأقل تكلفة (Least-Cost Ration Formulation) بالاعتماد على البرمجة الخطية</p>", unsafe_allow_html=True)
st.markdown("---")

# التحقق من وجود قاعدة البيانات
db_file = "feeds_db.json"
if not os.path.exists(db_file):
    st.error(f"خطأ: ملف قاعدة البيانات `{db_file}` غير موجود في المستودع.")
    st.stop()

with open(db_file, "r", encoding="utf-8") as f:
    data = json.load(f)

ingredients = data["ingredients"]
requirements = data["requirements"]

# تنظيم وتصنيف الحيوانات في واجهة ديناميكية
st.header("📋 1. نظام التغذية والتصنيف المستهدف")

category = st.selectbox("اختر فئة الحيوان الرئيسية:", ["المجترات (أبقار، أغنام، ماعز)", "الدواجن", "الخيول"])

# تصفية القائمة الفرعية بناءً على الفئة المختارة
if category == "المجترات (أبقار، أغنام، ماعز)":
    sub_list = [k for k in requirements.keys() if "المجترات" in k]
elif category == "الدواجن":
    sub_list = [k for k in requirements.keys() if "الدواجن" in k]
else:
    sub_list = [k for k in requirements.keys() if "الخيول" in k]

selected_stage = st.selectbox("اختر المرحلة الإنتاجية / العمرية الدقيقة:", sub_list)
req = requirements[selected_stage]

# عرض الاحتياجات الغذائية للفئة المختارة
st.info(f"📍 الاحتياجات المستهدفة لـ **({selected_stage})**: بروتين خام ≥ {req['min_protein']}% | طاقة ممثلة ≥ {req['min_energy']} (كـ/كجم) | كالسيوم ≥ {req['min_calcium']}% | فسفور متاح ≥ {req['min_phosphorus']}%")

# عرض المكتبة الشاملة للخامات وإدخال الأسعار الحالية
st.header("💰 2. أسعار الخامات العلفية الحالية (للطن في السوق)")
st.write("أدخل الأسعار الحالية لتحديد التوليفة الأقل تكلفة ماليًا:")

prices = {}
ing_list = list(ingredients.keys())

# تقسيم المدخلات في أعمدة منسقة تناسب شاشات الهواتف والمتصفح
cols = st.columns(3)
for idx, name in enumerate(ing_list):
    with cols[idx % 3]:
        prices[name] = st.number_input(f"💵 {name}", min_value=0.0, value=450.0, step=10.0, key=f"price_{idx}")

# زر التحسين والحساب الرياضي
st.markdown("---")
if st.button("🚀 احسب التركيبة المثلى بأقل تكلفة", type="primary"):
    
    # مصفوفة التكلفة
    c = [prices[name] for name in ing_list]
    
    # مصفوفة القيود العليا والدنيا
    A_ub = []
    b_ub = []
    
    # قيد البروتين (الحد الأدنى)
    A_ub.append([-ingredients[name]["protein"] for name in ing_list])
    b_ub.append(-req["min_protein"])
    
    # قيد الطاقة (الحد الأدنى)
    A_ub.append([-ingredients[name]["energy"] for name in ing_list])
    b_ub.append(-req["min_energy"])
    
    # قيد الكالسيوم (الحد الأدنى)
    A_ub.append([-ingredients[name]["calcium"] for name in ing_list])
    b_ub.append(-req["min_calcium"])
    
    # قيد الفسفور (الحد الأدنى)
    A_ub.append([-ingredients[name]["phosphorus"] for name in ing_list])
    b_ub.append(-req["min_phosphorus"])
    
    # قيد مجموع الخامات = 100%
    A_eq = [[1.0 for _ in ing_list]]
    b_eq = [1.0]
    
    # حد الأمان لكل خامة (الحدود الدنيا والعليا)
    bounds = []
    for name in ing_list:
        bounds.append((0.0, ingredients[name]["max_limit"]))
        
    # تشغيل خوارزمية الحل الخطي
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    if res.success:
        st.success("🎉 تم الوصول إلى التركيبة العلفية الاقتصادية بنجاح!")
        
        st.write("### 📋 نسب الخلط الموصى بها في الطن (1000 كجم):")
        
        # عرض الخامات المكونة فقط للتركيبة
        for idx, name in enumerate(ing_list):
            percentage = res.x[idx] * 100
            if percentage > 0.05:
                st.markdown(f"▪️ **{name}:** `{percentage:.2f} %` (أي ما يعادل **{percentage*10:.1f} كجم** لكل طن علف)")
                
        st.markdown("---")
        st.metric(label="💰 التكلفة الإجمالية المحسوبة للطن المستهدف", value=f"${res.fun:.2f}")
    else:
        st.error("❌ لم يتم العثور على حل رياضي! يرجى مراجعة أسعار الخامات أو التحقق من توازن نسب المواد المغذية المتاحة في قاعدة البيانات لتغطية هذه الاحتياجات المرتفعة.")
