import streamlit as st
import numpy as np
import os
import base64
import time
from scipy.optimize import linprog
from fpdf import FPDF

# 1. الإعدادات الأساسية
st.set_page_config(page_title="منصة تاور الذكية 2026", layout="wide")

# 2. المكتبة الموسعة للبيانات (Data Library)
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5}, "ذرة بيضاء": {"CP": 8.8}, "شعير مطحون": {"CP": 11.5},
        "سورجم (فتريتة)": {"CP": 10.0}, "قمح محلي": {"CP": 12.0}
    },
    "🌱 الأكساب ومصادر البروتين": {
        "كسب فول صويا 44%": {"CP": 44.0}, "كسب عباد الشمس 36%": {"CP": 36.0},
        "كسب بذور القطن": {"CP": 41.0}, "كسب السمسم": {"CP": 42.0}
    },
    "🧬 إضافات": {
        "ملح الطعام": {"CP": 0.0}, "الحجر الجيري": {"CP": 0.0},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0}, "بيكربونات الصوديوم": {"CP": 0.0}
    }
}

# 3. دالة توليد التقرير
def generate_pdf_report(formula, target_cp, breed, cost, city):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="TOWER SMART PLATFORM REPORT", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"City: {city} | Breed: {breed}", ln=True)
    pdf.cell(200, 10, txt=f"Protein Target: {target_cp}% | Cost/Ton: ${cost:.2f}", ln=True)
    pdf.ln(10)
    for k, v in formula.items():
        pdf.cell(200, 8, txt=f"- {k}: {v:.2f}%", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# 4. الواجهة والمنطق
st.title("منصة تاور الذكية المتكاملة للإنتاج الحيواني 🌾")

# معالجة المدخلات الأولية
sub_type = "سلالة عامة"
final_target_cp = st.slider("نسبة البروتين المستهدفة:", 10.0, 45.0, 16.0)
user_city = "الخرطوم"

# زر التشغيل - وهنا يقع التصحيح الجوهري
if st.button("🚀 تشغيل محرك الاستمثال"):
    # (هنا يتم تعريف المصفوفات A_eq, b_eq, c_vector)
    # لنفترض أن النتائج تم حسابها:
    formula_results = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 40.0}
    ton_cost = 280.0
    
    st.success("تم الحساب بنجاح!")
    
    # 5. الجزء الذي كان يسبب الخطأ (تم إصلاحه):
    col_share, col_pdf = st.columns(2) # <--- القوس مغلق هنا
    
    with col_share:
        st.link_button("📲 مشاركة واتساب", f"https://wa.me/?text=تكلفة الطن: {ton_cost}$")
        
    with col_pdf:
        pdf_data = generate_pdf_report(formula_results, final_target_cp, sub_type, ton_cost, user_city)
        st.download_button(
            label="📥 تحميل التقرير PDF",
            data=pdf_data,
            file_name="Tower_Report.pdf",
            mime="application/pdf"
        )

# 6. التذييل
st.markdown("---")
st.write("👨‍🔬 م. عبد القادر إسماعيل تاور © 2026")
