import streamlit as st
import time

# قاعدة بيانات مصغرة للإنزيمات والحدود القياسية
ENZYME_DATABASE = {
    "Phytase": {"target_nutrient": "Phytic_Acid", "max_limit": 0.5, "added_dose_per_ton": 150},
    "Xylanase": {"target_nutrient": "Crude_Fiber", "max_limit": 7.0, "added_dose_per_ton": 200}
}

def check_and_apply_enzymes(formulation_results):
    """
    دالة تفحص التركيبة وتضيف الإنزيم برمجياً إذا تم تجاوز الحد القياسي
    """
    applied_enzymes = {}
    
    for enzyme, data in ENZYME_DATABASE.items():
        nutrient = data["target_nutrient"]
        # إذا كان العنصر موجوداً في التركيبة وتجاوز الحد
        if nutrient in formulation_results and formulation_results[nutrient] > data["max_limit"]:
            applied_enzymes[enzyme] = data["added_dose_per_ton"]
            
    return applied_enzymes

# محاكاة لنتيجة حسابات التركيبة العلفية (Solver Output)
# نفترض أن الألياف الخام تجاوزت الحد (7.8 > 7.0)
sample_formulation = {"Crude_Protein": 21.5, "Crude_Fiber": 7.8, "Phytic_Acid": 0.3}

st.title("نظام التدخل البرمجي التلقائي للإنزيمات")

if st.button("تحليل التركيبة العلفية وتحسينها"):
    enzymes_to_add = check_and_apply_enzymes(sample_formulation)
    
    if enzymes_to_add:
        for enzyme, dose in enzymes_to_add.items():
            # إشعار برمجياً يظهر على الشاشة
            notification_box = st.empty()
            
            # عرض التنبيه بتنسيق مميز
            notification_box.error(f"⚠️ تنبيه: تم تجاوز الحد القياسي للألياف! تم إضافة إنزيم **{enzyme}** برمجياً بمعدل **{dose} جرام/طن**.")
            
            # مؤقت تنازلي لمدة 30 ثانية دون تجميد المتصفح بالكامل
            progress_bar = st.sidebar.progress(100)
            for secs in range(30, 0, -1):
                time.sleep(1)
                progress_bar.progress(int((secs/30)*100))
            
            # مسح الإشعار بعد انتهاء الـ 30 ثانية
            notification_box.empty()
            st.sidebar.success("تم إغلاق التنبيه تلقائياً.")
            
        # استكمال عرض النتائج بعد إضافة الإنزيم
        st.success("تم اعتماد التركيبة النهائية بنجاح بعد معالجتها برمجياً.")
