# streamlit_app.py
import streamlit as st
import config as cfg
import logic as log
import utils as ut

# استدعاء الإعدادات
st.set_page_config(page_title="منصة تاور الذكية 2026", layout="wide")

# منطق الدخول (حماية)
if "approved" not in st.session_state: st.session_state["approved"] = False
# ... باقي منطق الواجهة ...

# عند الحاجة لاستدعاء الإرسال (للمالك فقط):
if st.session_state["user_role"] == "admin":
    if st.button("إرسال نسخة الكود"):
        # قراءة الملف الحالي وإرساله
        with open(__file__, "r", encoding="utf-8") as f:
            content = f.read()
        ut.send_code_to_mail(target_email, content)
