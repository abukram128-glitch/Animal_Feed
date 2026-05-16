import streamlit as st
import numpy as np
from scipy.optimize import linprog
import json
import os

st.set_page_config(page_title="مُركّب الأعلاف الذكي", page_icon="🌾", layout="centered")

st.title("برنامج تركيب الأعلاف الذكي 🌾")
st.subheader("تطوير: عبد القادر إسماعيل")
st.write("حساب العليقة الأقل تكلفة (Least-Cost Ration) باستخدام البرمجة الخطية")

# التحقق من وجود ملف قاعدة البيانات
db_file = "feeds_db.json"
if not os.path.exists(db_file):
    st.error(f"خطأ: ملف قاعدة البيانات `{db_file}` غير موجود في المستودع! يرجى إنشاؤه أولاً.")
    st.stop()

# تحميل البيانات
with open(db_file, "r", encoding="utf-8") as f:
    data = json.load(f)

ingredients = data["ingredients"]
requirements = data["requirements"]

# اختيار المرحلة العمرية / نوع العليقة
st.header("1. نظام التغذية المستهدف")
stage = st.selectbox("اختر نوع ومرحلة الطيور:", list(requirements.keys()))
req = requirements[stage]

st.info(f"الاحتياجات المستهدفة لـ ({stage}): بروتين لّا يقل عن {req['min_protein']}% | طاقة لا تقل عن {req['min_energy']} كيلو كالوري")

# إدخال الأسعار الحالية للخامات
st.header("2. أسعار خامات العلف الحالية (للطن)")
prices = {}
cols = st.columns(len(ingredients))

for i, (ing_name, ing_data) in enumerate(ingredients.items()):
    with cols[i % len(cols)]:
        # افتراض سعر مبدئي 400 إذا لم يحدد
        prices[ing_name] = st.number_input(f"{ing_name}", min_value=1.0, value=400.0, step=10.0)

# زر الحساب والتحسين
st.markdown("---")
if st.button("احسب التركيبة المثلى بأقل تكلفة", type="primary"):
    
    # بناء مصفوفة البرمجة الخطية ديناميكياً
    ing_list = list(ingredients.keys())
    
    # 1. مصفوفة التكلفة (c)
    c = [prices[name] for name in ing_list]
    
    # 2. قيود الحد الأدنى (البروتين والطاقة والكالسيوم والفسفور) -> تضرب بسالب في linprog
    A_ub = []
    b_ub = []
    
    # قيد البروتين
    A_ub.append([-ingredients[name]["protein"] for name in ing_list])
    b_ub.append(-req["min_protein"])
    
    # قيد الطاقة
    A_ub.append([-ingredients[name]["energy"] for name in ing_list])
    b_ub.append(-req["min_energy"])
    
    # قيد الكالسيوم
    A_ub.append([-ingredients[name]["calcium"] for name in ing_list])
    b_ub.append(-req["min_calcium"])
    
    # قيد الفسفور
    A_ub.append([-ingredients[name]["phosphorus"] for name in ing_list])
    b_ub.append(-req["min_phosphorus"])
    
    # 3. قيد المجموع (يجب أن تساوي الخامات 100% أي 1 صحيح)
    A_eq = [[1.0 for _ in ing_list]]
    b_eq = [1.0]
    
    # 4. الحدود الدنيا والعليا لكل خامة (Bounds)
    bounds = []
    for name in ing_list:
        min_lim = 0.0
        max_lim = ingredients[name]["max_limit"]
        bounds.append((min_lim, max_lim))
        
    # تشغيل المحرك الرياضي
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    if res.success:
        st.success("🎉 تم الوصول إلى التركيبة العلفية الاقتصادية المثلى!")
        
        st.write("### 📋 نسب الخلط الموصى بها في الطن:")
        for idx, name in enumerate(ing_list):
            percentage = res.x[idx] * 100
            if percentage > 0.01:
                st.write(f"🔹 **{name}:** {percentage:.2f} % (أي {percentage*10:.1f} كجم في الطن)")
                
        st.markdown("---")
        st.metric(label="💰 التكلفة الإجمالية للطن المستهدف", value=f"${res.fun:.2f}")
    else:
        st.error("❌ لم يتم العثور على حل رياضي! يرجى مراجعة أسعار الخامات أو تخفيف قيود الاحتياجات، حيث أن الخامات الحالية بنسبها المتاحة لا يمكنها تغطية هذه الاحتياجات العالية.")
