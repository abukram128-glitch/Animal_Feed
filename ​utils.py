# utils.py
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_code_to_mail(receiver_email, sender_email, sender_password, code_content):
    """إرسال السورس كود للمالك فقط"""
    # (ضع هنا منطق دالة الإرسال الخاص بك مع استخدام st.secrets لكلمة السر)
    pass

def generate_pdf_report(formula, target_cp, breed, cost, city):
    # (كود توليد الـ PDF)
    pass
