import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_code_via_email(user_email):
    # إعدادات خادم البريد (كمثال: Gmail)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "YOUR_PLATFORM_EMAIL@gmail.com"
    sender_password = "YOUR_APP_PASSWORD" # كلمة مرور التطبيقات من جوجل
    
    # بناء الرسالة
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = "🌾 نسخة كود منصة تاور الذكية المتكاملة 2026"
    
    body = "مرفق لك في هذه الرسالة السورس كود الكامل لمنصة تاور الذكية للأعلاف."
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # قراءة الملف الحالي وإرفاقه
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code_content = f.read()
        
        attachment = MIMEText(code_content, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', filename="tower_platform.py")
        msg.attach(attachment)
        
        # الاتصال بالخادم والإرسال
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, user_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"خطأ أثناء الإرسال: {e}")
        return False

# زر واجهة المستخدم في سيل الجلسة أو التبويب الأخير
st.markdown("---")
st.subheader("📨 أرشفت الكود أو التقارير للبريد الإلكتروني")
target_mail = st.text_input("أدخل بريدك الإلكتروني لاستلام نسخة:")
if st.button("إرسال السورس كود فوراً 🚀"):
    if target_mail:
        with st.spinner("جاري إرسال الكود إلى بريدك..."):
            if send_code_via_email(target_mail):
                st.success(f"📥 تم إرسال نسخة من الملف بنجاح إلى: {target_mail}")
    else:
        st.warning("الرجاء كتابة البريد الإلكتروني أولاً.")
