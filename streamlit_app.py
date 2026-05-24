# streamlit_app.py
import streamlit as st
import logic
import utils
from datetime import datetime

st.set_page_config(page_title="منصة تاور الذكية", layout="wide")

st.title("🌾 منصة تاور الذكية 2026")

# استدعاء الدوال من الملفات الأخرى
col1, col2 = st.columns(2)
with col1:
    cp = st.slider("البروتين المستهدف (%)", 10.0, 45.0, 16.0)
    me = st.slider("الطاقة المستهدفة", 2000, 3500, 2800)
    if st.button("🚀 تشغيل المحرك"):
        res, names = logic.solve_formula(cp, me)
        if res.success:
            st.success("تم الحساب!")
            # عرض النتائج...

with col2:
    # عرض الديباجة
    tag_html = utils.generate_sack_tag({"animal": "أبقار", "cp": cp, "batch": "2026-001", "date": datetime.now().date()})
    st.markdown(tag_html, unsafe_allow_html=True)
