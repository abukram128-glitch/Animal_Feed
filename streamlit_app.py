# streamlit_app.py
import streamlit as st
import config as cfg
import logic as log
import utils as ut

# إعدادات الصفحة (شكل المنصة الأساسي)
st.set_page_config(page_title="منصة تاور الذكية 2026", layout="wide")

# محتوى المنصة (الواجهة)
# يمكنك هنا وضع الـ st.title و st.sidebar و st.button كما كنت تفعل سابقاً
# وعندما تحتاج للحسابات، استخدم: log.run_optimization(...)
# وعندما تحتاج للإرسال، استخدم: ut.send_code_to_mail(...)
