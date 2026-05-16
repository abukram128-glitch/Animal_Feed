import streamlit as st
import numpy as np
from scipy.optimize import linprog
import json
import os

# إعدادات الصفحة
st.set_page_config(page_title="مُركّب الأعلاف الذكي", page_icon="🌾", layout="wide")

# إبراز الهوية والشعار الجميل
st.markdown("<h1 style='text-align: center; color: #2E7D32;'>برنامج تركيب الأعلاف الذكي 🌾</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #1565C0;'>تصميم اختصاصي الإنتاج الحيواني: عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic; color: #555;'>نظام حساب العلائق الأقل تكلفة (Least-Cost Ration) للمجترات والدواجن والخيول</p>", unsafe_allow_html=True)
st.markdown("---")

# التحقق وتحميل البيانات
db_file = "feeds_db.json"
if not os.path.exists(db_file):
    st.error(f"خطأ: ملف قاعدة البيانات `{db_file}` غير موجود.")
    st.stop()

with open(db_file, "r", encoding="utf-8") as f:
    data = json.load(f)

ingredients = data["ingredients"]
requirements = data["requirements"]

# 1. نظام التغذية المستهدف
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

st.info(f"📍 الاحتياجات لـ ({selected_stage}): بروتين خام ≥ {req['min_protein']}% | طاقة ≥ {req['min_energy']} كـ/كجم | كالسيوم ≥ {req['min_calcium']}% | فسفور متاح ≥ {req['min_phosphorus']}%")

# 2. الخامات المتاحة والأسعار
st.header("💰 2. أسعار الخامات العلفية (المكتبة الشاملة المحدثة)")
st.write("أدخل السعر الحالي لكل خامة لتفعيل الحساب الاقتصادي:")

prices = {}
ing_list = list(ingredients.keys())

# توزيع الخامات في 3 أعمدة منسقة
cols = st.columns(3)
for idx, name in enumerate(ing_list):
    with cols[idx % 3]:
        # إعطاء قيمة افتراضية مناسبة للأسعار تسهيلاً للبدء
        default_val = 150.0 if "بريمكس" in name or "ملح" in name or "حجر" in name else 450.0
        prices[name] = st.number_input(f"💵 {name} (للطن)", min_value=0.0, value=default_val, step=10.0, key=f"p_{idx}")

# الحساب والتحسين الرياضي
st.markdown("---")
if st.button("🚀 احسب التركيبة الاقتصادية المثلى", type="primary"):
    
    c = [prices[name] for name in ing_list]
    A_ub = []
    b_ub = []
    
    # قيود الحد الأدنى (تضرب بسالب)
    A_ub.append([-ingredients[name]["protein"] for name in ing_list])
    b_ub.append(-req["min_protein"])
    
    A_ub.append([-ingredients[name]["energy"] for name in ing_list])
    b_ub.append(-req["min_energy"])
    
    A_ub.append([-ingredients[name]["calcium"] for name in ing_list])
    b_ub.append(-req["min_calcium"])
    
    A_ub.append([-ingredients[name]["phosphorus"] for name in ing_list])
    b_ub.append(-req["min_phosphorus"])
    
    # قيد المجموع = 100%
    A_eq = [[1.0 for _ in ing_list]]
    b_eq = [1.0]
    
    bounds = [(0.0, ingredients[name]["max_limit"]) for name in ing_list]
    
    # استدعاء المحرك الرياضي
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    if res.success:
        st.success("🎉 تم الوصول إلى العليقة المثلى بأقل تكلفة ماليّة تلبيةً لكافة الاحتياجات!")
        st.write("### 📋 نسب الخلط الموصى بها في الطن (1000 كجم):")
        
        for idx, name in enumerate(ing_list):
            percentage = res.x[idx] * 100
            if percentage > 0.05:
                st.markdown(f"▪️ **{name}:** `{percentage:.2f} %` (يعادل **{percentage*10:.1f} كجم** لكل طن علف)")
                
        st.markdown("---")
        st.metric(label="💰 التكلفة الإجمالية المحسوبة للطن", value=f"${res.fun:.2f}")
    else:
        st.error("❌ لم يتم العثور على حل رياضي! يرجى مراجعة أسعار الخامات العلفية أو التحقق من نسب المواد المتاحة. في الدواجن، تأكد من توفير خامات غنية بالبروتين والطاقة مثل كسب الصويا والمركزات لتغطية الاحتياجات العالية.")
