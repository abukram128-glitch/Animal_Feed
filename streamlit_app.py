import streamlit as st
import numpy as np
import json
import os
import base64
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scipy.optimize import linprog

# ==========================================
# 1. إعدادات المنصة الرسمية والمظهر الفخم لعام 2026
# ==========================================
st.set_page_config(page_title="منصة تاور الذكية المتكاملة للأعلاف والإنتاج الحيواني", page_icon="🌾", layout="wide")

# بيانات التحكم والوصول والأمان
USER_ADMIN = "تاور"       
PASS_ADMIN = "202687"     
USER_GUEST = "مربي"       
PASS_GUEST = "2026"       

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"       
SENDER_PASSWORD = "oynz rdli tsdy ekdq"     

def get_image_base64(paths):
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode()
            except Exception:
                pass
    return None

img_base64 = get_image_base64(PHOTO_OPTIONS)

def send_code_to_mail(receiver_email):
    if SENDER_EMAIL == "YOUR_EMAIL@gmail.com" or not SENDER_PASSWORD:
        st.error("⚠️ خطأ إعدادات: يرجى تحديث بيانات الـ SMTP داخل السورس كود أولاً.")
        return False
        
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود الكامل والمطور - منصة تاور الذكية المتكاملة"
    
    body = "السلام عليكم م. عبد القادر،\n\nمرفق مع هذه الرسالة النسخة البرمجية الكاملة والمعدلة.\n\nتحياتي الهندسية."
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        try:
            current_file = __file__
            with open(current_file, "r", encoding="utf-8") as f:
                code_content = f.read()
        except NameError:
            code_content = "# كود المنصة مأرشف داخلياً\n"
        
        attachment = MIMEText(code_content, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', filename="tower_smart_integrated_platform.py")
        msg.attach(attachment)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ فشل الإرسال بسبب: {e}")
        return False

# --- تحسين الـ CSS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { font-family: 'Cairo', sans-serif; }
    .main-box { background-color: rgba(255, 255, 255, 0.98); padding: 30px; border-radius: 15px; box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18); margin-bottom: 50px; }
    .formula-item { background-color: rgba(255, 255, 255, 0.9); padding: 10px 15px; border-radius: 8px; margin-bottom: 6px; font-weight: bold; color: #1b5e20 !important; border-right: 5px solid #2e7d32; }
    .section-title { color: #1b5e20; border-right: 6px solid #2e7d32; padding-right: 12px; font-size: 1.4rem; font-weight: bold; margin-top: 25px; margin-bottom: 15px; }
    .warning-card { background: #ffebee; padding: 12px; border-radius: 8px; border-right: 5px solid #c62828; margin-bottom: 10px; color: #b71c1c; }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. بوابة الدخول
# ==========================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
    input_user = st.text_input("👤 اسم المستخدم:")
    input_pass = st.text_input("🔑 كلمة المرور:", type="password")
    if st.button("تسجيل الدخول 🔓", type="primary"):
        if input_user == USER_ADMIN and input_pass == PASS_ADMIN:
            st.session_state["approved"] = True; st.session_state["user_role"] = "admin"; st.rerun()
        elif input_user == USER_GUEST and input_pass == PASS_GUEST:
            st.session_state["approved"] = True; st.session_state["user_role"] = "guest"; st.rerun()
    st.stop()

# [ملاحظة: تم حذف المكتبات الضخمة هنا للاختصار، استخدمها كما في كودك الأصلي]
# (افترض أن BIG_FEEDS_LIBRARY و البيانات موجودة هنا كما هي في ملفك الأصلي)

# ... [تكملة الكود في التبويب 0] ...

with tabs[0]:
    # ... (باقي كود اختيار الدولة والولاية) ...
    
    if st.button("🚀 تشغيل محرك الاستمثال الخطي للأعلاف (Scipy Optimized)", type="primary", use_container_width=True):
        # ... (منطق الاستمثال الخطي) ...
        
        if res.success:
            formula_results = {}
            for idx, ing in enumerate(selected_ingredients):
                if res.x[idx] > 0.0001: formula_results[ing] = res.x[idx]

            st.session_state["active_formula"] = formula_results
            st.success(f"🎯 تم تشغيل محرك التركيب واستقرار الاستمثال الخطي بنجاح.")

            if mandatory_warnings:
                st.markdown("### 🔬 تقرير فحص العلل:")
                for warn in mandatory_warnings: st.markdown(f'<div class="warning-card">{warn}</div>', unsafe_allow_html=True)

            res_col1, res_col2 = st.columns([0.6, 0.4])
            with res_col1:
                for k, v in formula_results.items(): st.markdown(f'<div class="formula-item">▪️ {k}: {v:.2f} %</div>', unsafe_allow_html=True)
            with res_col2: st.bar_chart(formula_results)
            
        else:
            st.error("❌ تعذر إيجاد حل رياضي متزن.")

# ... (باقي التبويبات كما هي) ...
