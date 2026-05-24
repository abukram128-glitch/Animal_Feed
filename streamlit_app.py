# streamlit_app.py
import streamlit as st
import config as cfg
import logic as log
import utils as ut

# 1. إعدادات الواجهة
st.set_page_config(page_title="منصة تاور الذكية 2026", layout="wide")

# 2. حماية الدخول
if "approved" not in st.session_state: st.session_state["approved"] = False
# ... (كود الدخول)

# 3. عرض المحتوى باستدعاء المكتبات (cfg, log, ut)
# مثال:
# if st.button("🚀 تشغيل المحرك"):
#     res = log.run_optimization(...)

# 4. صلاحية المالك فقط للإرسال
if st.session_state["user_role"] == "admin":
    target_email = st.text_input("بريد المالك لإرسال الكود:")
    if st.button("إرسال نسخة الكود"):
        # إرسال الكود
        pass
