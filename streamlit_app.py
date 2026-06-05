# Digital Signature: 017694d30a07573d0935e198aa9a950f
# Generated: 2026-06-05T22:57:11.826327

# Digital Signature: 3495cb0eef8355d2f9b0ff82e16e98fb
# Generated: 2026-05-30T22:57:38.541717

# Digital Signature: (سيتم توليده تلقائياً)
# Generated: 2026-05-31T12:00:00

import streamlit as st
import numpy as np
import pandas as pd  
import json
import os
import base64
import smtplib
import time
import urllib.parse  
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scipy.optimize import linprog
from scipy.spatial import ConvexHull
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
from datetime import datetime, timedelta
import hashlib
import secrets
from functools import lru_cache
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# استيراد مكتبات توليد الـ PDF المتقدمة ومعالجة اللغة العربية الصحيحة
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus.flowables import HRFlowable
import arabic_reshaper
from bidi.algorithm import get_display
import io
import qrcode
from PIL import Image as PILImage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.font_manager as fm

# ==========================================
# 1. إعدادات المنصة الرسمية والمظهر الفخم
# ==========================================
st.set_page_config(
    page_title="منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# نظام التخزين المؤقت المتقدم
@st.cache_resource
def init_caching_system():
    return {
        "cache_hits": 0,
        "cache_misses": 0,
        "last_cleanup": datetime.now()
    }
CACHE_SYSTEM = init_caching_system()

# الأكواد المعتمدة
def generate_secure_hash(code: str, salt: str = None) -> str:
    if salt is None:
        salt = secrets.token_hex(16)
    return hashlib.pbkdf2_hmac('sha256', code.encode(), salt.encode(), 100000).hex()

CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}
SECURE_CODES = {generate_secure_hash(code)[:32]: info for code, info in CODES_DB.items()}

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"
SENDER_PASSWORD = "oynz rdli tsdy ekdq"
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"
GOOGLE_FORM_URL = "https://forms.google.com/YOUR_FORM_URL"

@st.cache_data(ttl=3600)
def get_image_base64(paths: List[str]) -> Optional[str]:
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode()
            except Exception:
                pass
    return None
img_base64 = get_image_base64(PHOTO_OPTIONS)

def send_code_to_mail(receiver_email: str, attachment_type: str = "full") -> bool:
    if SENDER_EMAIL == "YOUR_EMAIL@gmail.com" or not SENDER_PASSWORD:
        st.error("⚠️ خطأ إعدادات: يرجى تحديث بيانات الـ SMTP داخل السورس كود أولاً.")
        return False
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود الكامل والمطور - منصة تاور العلمية"
    body = """السلام عليكم م. عبد القادر،

مرفق مع هذه الرسالة النسخة البرمجية الكاملة والمستقرة لمنصتكم الذكية (منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف) 
بعد تحديث الدليل والواجهات بالكامل وتضمين معايير البروتين المهضوم ومعادل النشاء ونظام إدارة مزارع الدجاج اللاحم.

التحسينات الجديدة:
- نظام تحليلات متقدم مع رسوم بيانية تفاعلية
- لوحة تحكم ذكية للمخازن
- نظام تنبؤات الأسعار
- محسن PDF متعدد الصفحات
- إدارة مزارع الدجاج اللاحم (خاص بالمالك) مع حساب KPIs و EPEF

تحياتي الهندسية."""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        try:
            current_file = __file__
            with open(current_file, "r", encoding="utf-8") as f:
                code_content = f.read()
        except NameError:
            code_content = "# كود المنصة مأرشيف داخلياً\n"
        file_hash = hashlib.md5(code_content.encode()).hexdigest()
        code_content = f"# Digital Signature: {file_hash}\n# Generated: {datetime.now().isoformat()}\n\n{code_content}"
        attachment = MIMEText(code_content, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', filename="tower_scientific_platform.py")
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

class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=1000)
    def fix_arabic_text(text: str) -> str:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text

arabic_processor = ArabicTextProcessor()

# ==========================================
# كلاس مولد PDF (آمن تماماً)
# ==========================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        if os.path.exists("Amiri-Regular.ttf"):
            try:
                pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
                self.font_name = 'Amiri'
            except:
                pass

    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, include_charts=True) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []

        def p(text, size=12, align=TA_RIGHT, color=HexColor('#000000')):
            safe_text = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe_text, ParagraphStyle('style', fontName=self.font_name, fontSize=size, alignment=align, textColor=color, spaceAfter=6, leading=size*1.5))

        story.append(p("تقرير فني شامل - منصة تاور العلمية", size=22, align=TA_CENTER, color=HexColor('#1b5e20')))
        story.append(Spacer(1, 12))
        for line in [f"المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور", f"الموقع الجغرافي: {city}", f"الفصيل المستهدف: {breed}", f"تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d %H:%M')}"]:
            story.append(p(line, size=11))
        story.append(Spacer(1, 15))

        tdata = [
            [arabic_processor.fix_arabic_text('المعيار'), arabic_processor.fix_arabic_text('القيمة')],
            [arabic_processor.fix_arabic_text('البروتين المهضوم (DP)'), f'{target_dp:.2f}%'],
            [arabic_processor.fix_arabic_text('معادل النشاء (SE)'), f'{computed_se:.2f} وحدة'],
            [arabic_processor.fix_arabic_text('التكلفة للطن'), f'${cost:.2f} ({local_cost:,.2f} {local_sym})']
        ]
        t = Table(tdata, colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('BACKGROUND', (0,1), (-1,-1), HexColor('#f5f5f5')),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#2e7d32')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        story.append(p("المقادير المعتمدة لتركيب الطن الواحد:", size=14, color=HexColor('#2e7d32')))
        story.append(Spacer(1, 10))
        ing_data = [[arabic_processor.fix_arabic_text('المكون'), arabic_processor.fix_arabic_text('النسبة %'), arabic_processor.fix_arabic_text('كجم/طن')]]
        for ing, pct in formula.items():
            ing_data.append([arabic_processor.fix_arabic_text(ing), f'{pct:.2f}%', f'{pct*10:.1f}'])
        t2 = Table(ing_data, colWidths=[200, 150, 150])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')]),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t2)
        story.append(Spacer(1, 15))

        if include_charts and len(formula) > 1:
            try:
                fig, ax = plt.subplots(figsize=(6, 3.5))
                names = list(formula.keys())
                vals = list(formula.values())
                colors = ['#1b5e20','#2e7d32','#388e3c','#43a047','#4caf50','#66bb6a']
                ax.pie(vals, labels=None, autopct='%1.1f%%', colors=colors[:len(names)])
                ax.legend([arabic_processor.fix_arabic_text(n) for n in names], title=arabic_processor.fix_arabic_text("المكونات"),
                         loc='center left', bbox_to_anchor=(1,0,0.5,1), fontsize=8)
                ax.set_title(arabic_processor.fix_arabic_text('توزيع المكونات'), fontsize=12)
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Image(buf, width=400, height=230))
            except:
                pass

        story.append(Spacer(1, 25))
        story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026 | تحت إشراف م. عبد القادر إسماعيل تاور", size=9, align=TA_CENTER, color=HexColor('#666666')))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

# ==========================================
# كلاس إدارة مزارع الدجاج اللاحم (جديد - خاص بالمالك)
# ==========================================
class BroilerFarmManager:
    @staticmethod
    def calculate_adg(current_weight_g: float, initial_weight_g: float, age_days: int) -> float:
        """معدل النمو اليومي (ADG) بالجرام"""
        if age_days <= 0:
            return 0.0
        return (current_weight_g - initial_weight_g) / age_days

    @staticmethod
    def calculate_fcr(total_feed_kg: float, total_weight_gain_kg: float) -> float:
        """معامل التحويل الغذائي (FCR)"""
        if total_weight_gain_kg <= 0:
            return 0.0
        return total_feed_kg / total_weight_gain_kg

    @staticmethod
    def calculate_mortality_rate(dead_count: int, initial_count: int) -> float:
        """نسبة النفوق المئوية"""
        if initial_count <= 0:
            return 0.0
        return (dead_count / initial_count) * 100.0

    @staticmethod
    def calculate_cull_rate(culled_count: int, initial_count: int) -> float:
        """نسبة الاستبعاد المئوية"""
        if initial_count <= 0:
            return 0.0
        return (culled_count / initial_count) * 100.0

    @staticmethod
    def calculate_livability(initial_count: int, dead_count: int) -> float:
        """الحيوية (Livability) = 100 - نسبة النفوق"""
        return 100.0 - BroilerFarmManager.calculate_mortality_rate(dead_count, initial_count)

    @staticmethod
    def calculate_epef(livability: float, body_weight_kg: float, age_days: int, fcr: float) -> float:
        """مؤشر الأداء الأوروبي EPEF"""
        if age_days <= 0 or fcr <= 0:
            return 0.0
        return (livability * body_weight_kg) / (age_days * fcr) * 100.0

    @staticmethod
    def get_temp_humidity_table():
        """جدول الحرارة والرطوبة الموصى بها حسب عمر الطيور (أيام)"""
        data = {
            "العمر (يوم)": [1, 7, 14, 21, 28, 35, 42],
            "درجة الحرارة (مئوي)": [33, 30, 28, 26, 24, 22, 21],
            "الرطوبة النسبية (%)": [65, 65, 65, 60, 60, 55, 55]
        }
        return pd.DataFrame(data)

# ==========================================
# تهيئة حالة جلسة إدارة الدجاج اللاحم (خاص بالمالك)
# ==========================================
if "broiler_farm_data" not in st.session_state:
    st.session_state["broiler_farm_data"] = {
        "farm_name": "مزرعة الدجاج اللاحم",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "flock_age_days": 21,
        "initial_birds": 10000,
        "current_weight_kg": 0.950,
        "initial_weight_kg": 0.045,
        "total_feed_consumed_kg": 18500.0,
        "total_water_consumed_l": 0.0,
        "dead_birds": 120,
        "culled_birds": 15,
        "temperature_c": 26.0,
        "humidity_percent": 60.0,
        "ventilation_status": "جيدة",
        "litter_quality": "جيدة",
        "notes": ""
    }
if "broiler_cycles_history" not in st.session_state:
    st.session_state["broiler_cycles_history"] = []  # قائمة لتخزين الدورات السابقة

# --- CSS (بدون تغيير) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Tajawal:wght@400;500;700&display=swap');
    
    * {
        font-family: 'Cairo', 'Tajawal', sans-serif;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .stApp { 
        background: transparent; 
    }
    
    .main-box {
        background-color: rgba(255, 255, 255, 0.98);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18);
        margin-bottom: 50px;
        backdrop-filter: blur(10px);
    }
    
    h1, h2, h3, h4, h5, p, span, li { 
        font-family: 'Cairo', sans-serif; 
    }
    
    .formula-item {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(232,245,233,0.9) 100%);
        padding: 15px 20px;
        border-radius: 12px;
        margin-bottom: 10px;
        font-weight: bold;
        color: #1b5e20 !important;
        border-right: 5px solid #2e7d32;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        text-align: right;
        transition: transform 0.3s ease;
    }
    
    .formula-item:hover {
        transform: translateX(-5px);
        box-shadow: 0px 6px 20px rgba(0,0,0,0.15);
    }
    
    .section-title {
        color: #1b5e20;
        border-right: 6px solid #2e7d32;
        padding-right: 15px;
        text-align: right;
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 20px;
        background: linear-gradient(to left, rgba(46,125,50,0.1), transparent);
        padding: 10px 15px;
        border-radius: 8px;
    }
    
    .sack-tag {
        border: 3px dashed #1b5e20;
        padding: 30px;
        border-radius: 15px;
        background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e9 100%);
        direction: rtl;
        text-align: right;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.1);
    }
    
    .profile-img-style {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid #d4af37;
        box-shadow: 0px 6px 20px rgba(0,0,0,0.25);
        display: block;
        margin: 0 auto;
        transition: transform 0.3s ease;
    }
    
    .profile-img-style:hover {
        transform: scale(1.05);
    }
    
    .animal-banner-img {
        width: 100%;
        max-height: 200px;
        object-fit: cover;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 3px solid #2e7d32;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
    }
    
    .mini-left-signature {
        position: fixed;
        left: 20px;
        bottom: 20px;
        background: linear-gradient(135deg, #1b5e20, #2e7d32);
        color: white;
        padding: 8px 20px;
        font-size: 0.85rem;
        border-radius: 25px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
        z-index: 9999;
        direction: rtl;
        backdrop-filter: blur(5px);
    }
    
    .stock-critical { 
        background: linear-gradient(135deg, #ffebee, #ffcdd2); 
        padding: 8px 12px; 
        border-radius: 8px; 
        color: #c62828; 
        font-weight: bold;
        border: 1px solid #ef5350;
    }
    
    .stock-normal { 
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9); 
        padding: 8px 12px; 
        border-radius: 8px; 
        color: #2e7d32;
        border: 1px solid #66bb6a;
    }
    
    .price-card {
        background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
        padding: 20px;
        border-radius: 12px;
        border-right: 5px solid #2e7d32;
        margin-bottom: 20px;
        direction: rtl;
        text-align: right;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        padding: 15px;
        border-radius: 12px;
        border-right: 5px solid #f57c00;
        margin-bottom: 15px;
        direction: rtl;
        text-align: right;
        color: #e65100;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    
    .manual-book {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        padding: 35px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0px 8px 30px rgba(0,0,0,0.08);
        direction: rtl;
        text-align: right;
    }
    
    .book-chapter {
        background: linear-gradient(135deg, #1a237e, #283593);
        color: #ffffff;
        padding: 15px 20px;
        border-radius: 10px;
        font-weight: bold;
        margin-top: 25px;
        font-size: 1.2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        letter-spacing: 0.5px;
    }
    
    .book-body {
        padding: 20px 25px;
        font-size: 1.1rem;
        line-height: 1.8;
        color: #2c3e50;
        border-left: 4px solid #3498db;
        margin-bottom: 20px;
        background: linear-gradient(to right, #f8f9fa, #ffffff);
        border-radius: 0 10px 10px 0;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
    }
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 8px 30px rgba(0,0,0,0.15);
    }
    
    .analytics-container {
        background: linear-gradient(135deg, #f5f5f5, #ffffff);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.08);
        margin: 20px 0;
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #1b5e20, #4caf50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    .card-hover {
        transition: all 0.3s ease;
    }
    
    .card-hover:hover {
        transform: translateY(-3px);
        box-shadow: 0px 8px 25px rgba(0,0,0,0.15);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. بوابة الدخول
# ==========================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "login_welcome_shown" not in st.session_state: st.session_state["login_welcome_shown"] = False
if "login_attempts" not in st.session_state: st.session_state["login_attempts"] = 0
if "last_login_time" not in st.session_state: st.session_state["last_login_time"] = None
if "session_token" not in st.session_state: st.session_state["session_token"] = None

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300

if not st.session_state["approved"]:
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        if st.session_state["last_login_time"]:
            time_diff = (datetime.now() - st.session_state["last_login_time"]).seconds
            if time_diff < LOCKOUT_TIME:
                st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
                st.error(f"🔒 تم قفل النظام مؤقتاً. يرجى المحاولة بعد {LOCKOUT_TIME - time_diff} ثانية")
                st.markdown('</div>', unsafe_allow_html=True)
                st.stop()
            else:
                st.session_state["login_attempts"] = 0

    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</p>", unsafe_allow_html=True)

    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("https://tower-scientific-platform.streamlit.app")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        st.markdown(f'<div style="text-align:center; margin:20px 0;"><img src="data:image/png;base64,{qr_base64}" width="150"></div>', unsafe_allow_html=True)
    except:
        pass

    input_code = st.text_input("🔑 أدخل كود الدخول الخاص بك:", type="password")
    col_login, col_reset = st.columns(2)
    with col_login:
        if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
            input_code_stripped = input_code.strip()
            if input_code_stripped in CODES_DB:
                st.session_state["approved"] = True
                st.session_state["user_role"] = CODES_DB[input_code_stripped]["role"]
                st.session_state["login_welcome_shown"] = False
                st.session_state["login_attempts"] = 0
                st.session_state["last_login_time"] = datetime.now()
                st.session_state["session_token"] = secrets.token_urlsafe(32)
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                st.session_state["last_login_time"] = datetime.now()
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ الكود غير صحيح! متبقي {remaining} محاولات")
    with col_reset:
        if st.button("🔄 نسيت الكود", use_container_width=True):
            st.info("يرجى التواصل مع مدير النظام: abukram128@gmail.com")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

if not st.session_state["login_welcome_shown"]:
    role_messages = {
        "owner": "👋 مرحباً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور",
        "specialist": "🔬 أهلاً بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني.",
        "breeder": "🚜 أهلاً وسهلاً بإخواننا المربين، شركاء النجاح."
    }
    role_icons = {"owner": "👑", "specialist": "👨‍🔬", "breeder": "🌾"}
    st.toast(role_messages.get(st.session_state["user_role"], "مرحباً"), icon=role_icons.get(st.session_state["user_role"], "🌾"))
    st.session_state["login_welcome_shown"] = True

# =========================================================================================
# 3. المكتبة والمتغيرات (نفس السابق)
# =========================================================================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة الكبرى": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6},
        "جريش أرز رزاز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2},
        "دخن محلي غزير": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0}
    },
    "🌱 الأكساب وأمبازات مصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5}
    },
    "🚜 المخلفات الزراعية والصناعية والمواد المالئة": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5},
        "بقايا تفل البنجر المجفف": {"CP": 8.0, "DC": 0.75, "SE": 58.0, "NDF": 38.5, "ADF": 22.5, "EE": 1.5, "ASH": 6.5},
        "مخلفات مصانع البسكويت": {"CP": 9.5, "DC": 0.88, "SE": 76.0, "NDF": 8.5, "ADF": 3.5, "EE": 8.5, "ASH": 3.5},
        "سیلاج ذرة كامل متكامل": {"CP": 8.0, "DC": 0.68, "SE": 50.0, "NDF": 45.5, "ADF": 25.5, "EE": 2.5, "ASH": 4.5}
    },
    "🧬 مصادر البروتين الحيواني والمركزات دقيقة الخلط": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق أسماك فاخر (72%)": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5}
    },
    "🧪 الأحماض الأمينية البلورية النقية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3},
        "ثريونين نقي (L-Threonine)": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2},
        "تريبتوفان نقي (L-Tryptophan)": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1},
        "فالين نقي (L-Valine)": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1}
    },
    "🔬 الإنزيمات والبريمكسات والإضافات التخصصية": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس بياض وبشاير": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس خيول وفروسية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
        "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0},
        "كبريتات الحديدوز (معادل الجوسيبول)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0},
        "مستخلص الخمائر والجدر الخلوية (MOS)": {"CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5, "EE": 1.5, "ASH": 8.5}
    },
    "🪨 الأملاح والمعادن ومنظمات الهضم": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
        "أكسيد المغنيسيوم العلفي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "يوريا علفية محصنة (المجترات فقط)": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0}
    }
}

# نظام أسعار المدن المخصصة
CITY_PRICES_FILE = "city_prices.json"
def load_city_prices():
    if os.path.exists(CITY_PRICES_FILE):
        try:
            with open(CITY_PRICES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_city_prices(data):
    with open(CITY_PRICES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

CITY_CUSTOM_PRICES = load_city_prices()

class InventoryManager:
    @staticmethod
    def initialize_inventory():
        if "inventory" not in st.session_state:
            st.session_state["inventory"] = {}
            for cat_name, items in BIG_FEEDS_LIBRARY.items():
                for ing in items:
                    st.session_state["inventory"][ing] = {
                        "quantity": 25.0,
                        "min_threshold": 5.0,
                        "unit": "طن",
                        "last_updated": datetime.now().isoformat(),
                        "price_history": [],
                        "supplier": "غير محدد"
                    }

    @staticmethod
    def check_stock_levels() -> Dict[str, str]:
        warnings = {}
        for item, data in st.session_state["inventory"].items():
            qty = data if isinstance(data, (int, float)) else data["quantity"]
            threshold = 5.0 if isinstance(data, (int, float)) else data["min_threshold"]
            if qty <= 0:
                warnings[item] = "نفذ المخزون"
            elif qty < threshold:
                warnings[item] = "منخفض"
        return warnings

InventoryManager.initialize_inventory()

if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين / محسن ($)": 1350.0, "أبقار كنانة وبطانة محلية ($)": 900.0,
        "ضأن وستيرلنغ / محلي ($)": 180.0, "ماعز نوبي وصحراوي ($)": 130.0,
        "خيول عربية أصيلة وهجين ($)": 4500.0, "كتكوت لاحم عمر يوم ($)": 0.65, "دجاج بياض عمر البشاير ($)": 5.50
    }
if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري صافي ($)": 7.50, "كيلو لحم ضأن طازج ($)": 9.00,
        "كيلو لحم دجاج لاحم صافي ($)": 3.80, "طبق بيض مائدة 30 بيضة ($)": 4.20,
        "رطل / لتر حليب خام ($)": 0.90, "كيلو جبن أبيض محلي ($)": 5.00,
        "كيلو جبن جاف / شيدر ($)": 8.50
    }
if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = (
        "• [توجيه الاختصاصي م. عبد القادر إسماعيل تاور]: يرجى من جميع الزملاء إضافة تعليقاتهم هنا لتبادل الخبرات التركيبية.\n"
        "• [ملاحظة مختص]: تم مراجعة جودة كسب زهرة الشمس المتاح حالياً بالأسواق ونوصي بضبط ألياف الخيل بناءً عليه.\n"
    )

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG", "currency_name": "جنيه سوداني"},
    "LIBYA": {"rate": 4.80, "sym": "LYD", "currency_name": "دينار ليبي"},
    "مصر": {"rate": 48.0, "sym": "EGP", "currency_name": "جنيه مصري"},
    "باقي دول العالم / البورصة المفتوحة": {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"}
}

class MarketPriceEngine:
    @staticmethod
    @lru_cache(maxsize=128)
    def get_adjusted_market_data(country: str, state_or_region: str, city: str) -> Dict[str, float]:
        feed_prices = {}
        for cat in BIG_FEEDS_LIBRARY.values():
            for ing in cat:
                feed_prices[ing] = 230.0
        base_prices = {
            "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0,
            "سورجم (فتريتة)": 195.0, "قمح محلي مصنّع": 240.0,
            "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا 44%": 440.0,
            "كسب فول صويا 48%": 480.0, "كسب عباد الشمس 36%": 310.0,
            "كسب بذور القطن (مقشور)": 290.0, "نخالة قمح (ردة)": 150.0,
            "البرسيم الجاف (الدريس)": 170.0, "مولاس قصب السكر": 120.0,
            "مسحوق أسماك (Fishmeal 60%)": 850.0, "مركزات دواجن وسمان": 650.0,
            "مركزات خيول ومجترات": 600.0,
            "الحجر الجيري (بودرة بلاط)": 40.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0,
            "ملح الطعام": 30.0, "مضاد سموم فطرية": 950.0,
            "بيكربونات الصوديوم (الصودا)": 340.0
        }
        feed_prices.update(base_prices)
        multiplier = 1.0
        if country == "السودان":
            multiplier = 1.15
            if "كردفان" in state_or_region or state_or_region == "إقليم النيل الأزرق":
                multiplier = 1.20
                feed_prices["سورجم (فتريتة)"] *= 0.85
                feed_prices["أمباز الفول السوداني (كسب)"] *= 0.85
            elif state_or_region in ["ولاية القضارف", "ولاية الجزيرة"]:
                feed_prices["سورجم (فتريتة)"] *= 0.82
                feed_prices["أمباز الفول السوداني (كسب)"] *= 0.88
        elif country == "LIBYA":
            multiplier = 1.10
            if city == "طبرق":
                multiplier = 1.06
        elif country == "مصر":
            multiplier = 1.04
        for k in feed_prices:
            feed_prices[k] *= multiplier
        return feed_prices

ANIMAL_IMAGES_RESOURCES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600",
    "سمان": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600"
}

if "active_formula" not in st.session_state: st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 12.0
if "active_se_tag" not in st.session_state: st.session_state["active_se_tag"] = 65.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_animal_img" not in st.session_state: st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES["عام"]
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0

# ==========================================
# 4. الواجهة الرئيسية
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logout_space, col_user_status = st.columns([0.7, 0.3])
with col_user_status:
    role_info = {"owner": "الاختصاصي م. عبد القادر إسماعيل تاور 👑", "specialist": "المختص والزملاء 👨‍🔬", "breeder": "المربي 🌾"}
    st.markdown(f"""<div style='text-align: left; font-size:0.9rem; color:#555; background: linear-gradient(135deg, #f5f5f5, #e0e0e0); padding: 10px; border-radius: 10px;'>الحساب: <b>{role_info.get(st.session_state["user_role"], "مستخدم")}</b><br><small>آخر دخول: {datetime.now().strftime('%Y-%m-%d %H:%M')}</small></div>""", unsafe_allow_html=True)
    if st.button("تسجيل الخروج 🚪", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key != "inventory":
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style pulse-animation">', unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.2rem; margin-top:5px; margin-bottom:0;'>محرك الاستمثال الخطي المتقدم القائم على البروتين المهضوم (DP) ومعادل النشاء (SE)</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 3px solid #2e7d32;'>", unsafe_allow_html=True)

st.markdown("### 📢 المشاركة التسويقية والدعوة العلمية")
share_text_payload = """📢 دعوة علمية وتسويقية من منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف

إلى كل مهتم بتطوير الثروة الحيوانية؛ من أطباء بيطريين، اختصاصيي إنتاج حيواني، ومربين طموحين:
يسعدنا دعوتكم لاستخدام وتجربة المنصة المتقدمة لتركيب وتطوير الأعلاف، بإشراف وتصميم:
[ الاختصاصي م. عبد القادر إسماعيل تاور ]

🎯 ما تقدمه المنصة:
• حلول برمجية ذكية لتركيب أعلاف اقتصادية على أساس البروتين المهضوم ومعادل النشاء (Least-Cost Formulation).
• أدوات دقيقة لحساب الاحتياجات الغذائية بما يضمن أعلى معدلات نمو وإنتاجية.
• دعم كامل للعمل الميداني والبحث العلمي والخصم التلقائي للمستودعات في مكان واحد.
• نظام تحليلات متقدم وتقارير PDF احترافية
• إدارة مزارع الدجاج اللاحم مع حساب KPIs و EPEF (خاص بالمالك)

🔗 رابط المنصة: [ضع رابط موقعك هنا]"""
st.text_area("النص الدعائي والإعلامي الجاهز للنشر:", value=share_text_payload, height=140, key="top_share_box")
col_copy, col_share = st.columns(2)
with col_copy:
    if st.button("📋 نسخ الرابط والنص للدعاية والتسويق", type="secondary", use_container_width=True):
        st.success("تم التجهيز بنجاح! يمكنك الآن نسخ النص ومشاركته عبر المجموعات والمنصات.")
with col_share:
    encoded_share = urllib.parse.quote(share_text_payload[:200])
    st.link_button("📲 مشاركة مباشرة عبر واتساب", f"https://wa.me/?text={encoded_share}", use_container_width=True)

st.markdown("---")

welcome_messages = {
    "owner": {"bg": "#eff6ff", "border": "#1d4ed8", "text": "👑 أهلاً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور. نظام التوازن الدقيق بالبروتين المهضوم ومعادل النشاء قيد التشغيل الآن بكفاءة متناهية. كما تم تفعيل إدارة مزارع الدجاج اللاحم."},
    "specialist": {"bg": "#f0fdf4", "border": "#16a34a", "text": "🔬 مرحباً بكم في منصة تركيب وتحليل الأعلاف الذكية. يسعد الاختصاصي م. عبد القادر إسماعيل تاور بالترحيب بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني."},
    "breeder": {"bg": "#fffbeb", "border": "#d97706", "text": "🚜 أهلاً وسهلاً بكم في منصة تاور العلمية. نرحب بإخواننا المربين. نوفر لكم خلطات مبنية على القيمة الغذائية الحقيقية الممتصة لضمان التوفير المالي العالي."}
}
current_welcome = welcome_messages.get(st.session_state["user_role"], welcome_messages["breeder"])
st.markdown(f"""<div style='background-color: {current_welcome["bg"]}; padding: 15px; border-radius: 8px; border-right: 5px solid {current_welcome["border"]}; text-align: right; direction: rtl; margin-bottom: 20px;'><b>{current_welcome["text"]}</b></div>""", unsafe_allow_html=True)

# تحديد التبويبات (مع إضافة تبويب إدارة الدجاج اللاحم للمالك فقط)
if st.session_state["user_role"] == "owner":
    tabs_titles = ["🔬 النمذجة والحسابات العلفية", "📊 بورصة الأسعار المركزية", "🏭 إدارة المستودعات الذكية", "🧾 التسويق وفواتير البيع", "🖨️ مصمم الديباجة والدعاية", "📈 التحليلات المتقدمة", "🐔 إدارة مزارع الدجاج اللاحم (Broiler) – خاص بالمالك", "💬 تعليقات المختصين", "📖 دليل المستخدم"]
elif st.session_state["user_role"] == "specialist":
    tabs_titles = ["🔬 النمذجة والحسابات العلفية", "📊 بورصة الأسعار المركزية", "🏭 إدارة المستودعات الذكية", "🧾 التسويق وفواتير البيع", "🖨️ مصمم الديباجة والدعاية", "📈 التحليلات المتقدمة", "💬 تعليقات المختصين", "📖 دليل المستخدم"]
else:  # breeder
    tabs_titles = ["🔬 النمذجة والحسابات العلفية", "📖 دليل المستخدم"]

tabs = st.tabs(tabs_titles)

# -------------------------------------------------------------------------
# التبويب الأول: الحسابات والتركيبات (نفس السابق)
# -------------------------------------------------------------------------
with tabs[0]:
    sub_tab_formulator, sub_tab_analyzer = st.tabs(["🎯 تركيب علفة نموذجية (أقل تكلفة بالبروتين المهضوم)", "🔬 مختبر تحليل وفحص الأعلاف الجاهزة"])

    with sub_tab_formulator:
        st.markdown('<div class="section-title">🌍 أولاً: تحديد الموقع الجغرافي وبورصة الأسعار</div>', unsafe_allow_html=True)
        col_country, col_state, col_city = st.columns(3)
        with col_country:
            user_country = st.selectbox("اختر دولة المربي:", ["السودان", "LIBYA", "مصر", "باقي دول العالم / البورصة المفتوحة"])
        c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD", "currency_name": "دولار أمريكي"})
        local_rate = c_info["rate"]
        local_sym = c_info["sym"]

        chosen_state = "عام"
        with col_state:
            if user_country == "السودان":
                chosen_state = st.selectbox("اختر الولاية السودانية:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال كردفان", "ولاية جنوب كردفان", "ولاية غرب كردفان", "إقليم النيل الأزرق", "ولاية البحر الأحمر", "ولاية نهر النيل"])
            elif user_country == "LIBYA":
                chosen_state = st.selectbox("اختر الإقليم الجغرافي:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
            else:
                chosen_state = st.selectbox("الإقليم الإداري:", ["المركز الرئيسي العالمي", "الأسواق المفتوحة"])

        with col_city:
            if user_country == "السودان":
                cities_map = {
                    "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
                    "ولاية الجزيرة": ["ود مدني", "الحصاحيصا", "المناقل"],
                    "ولاية القضارف": ["القضارف المدينة", "الفاو"],
                    "ولاية شمال كردفان": ["الأبيض", "بارا", "أم روابة"],
                    "ولاية جنوب كردفان": ["كادوقلي", "الدلنج"],
                    "ولاية غرب كردفان": ["الفوله", "النهود", "بابنوسة"],
                    "إقليم النيل الأزرق": ["الدمازين", "الروصيرص"],
                    "ولاية البحر الأحمر": ["بورتسودان", "سواكن"],
                    "ولاية نهر النيل": ["شندي", "عطبرة", "الدامر"]
                }
                user_city = st.selectbox("اختر المدينة:", cities_map.get(chosen_state, ["عام"]))
            elif user_country == "LIBYA":
                cities_map = {
                    "المنطقة الشرقية": ["طبرق", "بنغازي", "البيضاء", "درنة"],
                    "المنطقة الغربية": ["طرابلس", "مصراتة", "الزاوية"],
                    "المنطقة الجنوبية": ["سبها", "مرزق", "غات"]
                }
                user_city = st.selectbox("اختر المدينة:", cities_map.get(chosen_state, ["عام"]))
            else:
                user_city = st.text_input("اكتب اسم المدينة:", "طبرق")

        city_key = f"{user_country}|||{chosen_state}|||{user_city}"
        custom_prices = CITY_CUSTOM_PRICES.get(city_key, {})
        live_prices = MarketPriceEngine.get_adjusted_market_data(user_country, chosen_state, user_city)

        col_view1, col_view2 = st.columns(2)
        with col_view1:
            st.markdown(f'<div class="price-card"><b>📈 بورصة الماشية والداجن في ({user_city}):</b><br>' + "<br>".join([f'▪️ {k}: <b>${v:.2f}</b> (<span style="color:#e65100; font-weight:bold;">{v*local_rate:,.2f} {local_sym}</span>)' for k, v in st.session_state["global_livestock_prices"].items()]) + "</div>", unsafe_allow_html=True)
        with col_view2:
            st.markdown(f'<div class="price-card"><b>🥩 بورصة المنتجات الحيوانية في ({user_city}):</b><br>' + "<br>".join([f'▪️ {k}: <b>${v:.2f}</b> (<span style="color:#1b5e20; font-weight:bold;">{v*local_rate:,.2f} {local_sym}</span>)' for k, v in st.session_state["global_products_prices"].items()]) + "</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">⚖️ ثانياً: اختيار القطاع والنوع والإنتاجية المستهدفة</div>', unsafe_allow_html=True)
        col_sec, col_sub, col_prod = st.columns(3)
        with col_sec:
            main_sector = st.selectbox("اختر القطاع الإنتاجي الرئيسي:", ["الأغنام وسلالاتها 🐏", "الماعز وسلالاتها", "الأبقار وسلالاتها", "الخيول والفروسية", "الطيور والسمان", "الأسماك والأحياء المائية"])
        show_measurements = False
        weight_factor = 10000; feed_factor = 0.02
        default_dp = 11.0; default_se = 60.0
        dynamic_img_key = "عام"; chosen_concentrate = None
        gender_option = "إناث"
        if main_sector in ["الأغنام وسلالاتها 🐏", "الماعز وسلالاتها"]:
            with col_sec:
                gender_option = st.radio("حدد الجنس:", ["ذكور (تسمين)", "إناث (حليب / أمهات)"], horizontal=True)

        with col_sub:
            if main_sector == "الأغنام وسلالاتها 🐏":
                sub_type = st.selectbox("السلالة المستهدفة:", ["الضأن الصحراوي السوداني", "البربري", "النعيمي", "سلالات محلية / هجين"])
                dynamic_img_key = "أغنام"; show_measurements = True; weight_factor = 15500; feed_factor = 0.035; chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الماعز وسلالاتها":
                sub_type = st.selectbox("السلالة المستهدفة:", ["الماعز النوبي السوداني", "الماعز الصحراوي", "بور / محسن"])
                dynamic_img_key = "ماعز"; show_measurements = True; weight_factor = 15000; feed_factor = 0.032; chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الأبقار وسلالاتها":
                sub_type = st.selectbox("السلالة المستهدفة:", ["كنانة (سوداني)", "بطانة (مدر)", "هولشتاين / محسن"])
                dynamic_img_key = "أبقار"; show_measurements = True; weight_factor = 10838; feed_factor = 0.025; chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الخيول والفروسية":
                sub_type = st.selectbox("السلالة المستهدفة:", ["خيل عربي أصيل", "ثوروبريد", "خيول محلية هجين"])
                dynamic_img_key = "خيول"; show_measurements = True; weight_factor = 11877; feed_factor = 0.022; chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الطيور والسمان":
                sub_type = st.selectbox("نوع الطيور:", ["طائر السمان (Quail)", "دواجن لاحم (Broiler)", "دواجن بياض (Layer)"])
                dynamic_img_key = "سمان" if "السمان" in sub_type else "دواجن"; chosen_concentrate = "مركزات دواجن وسمان"
            else:
                sub_type = st.selectbox("نوع الأسماك:", ["البلطي النيلي (Tilapia)", "القرموط"])
                dynamic_img_key = "أسماك"; chosen_concentrate = "مسحوق أسماك (Fishmeal 60%)"

        with col_prod:
            if main_sector == "الأغنام وسلالاتها 🐏":
                if gender_option == "ذكور (تسمين)":
                    prod_stage = st.selectbox("خط إنتاج الذكور:", ["تسمين حملان مكثف (نمو سريع)", "حملان تيد / كباش جاهزة للأسواق"])
                    default_dp = 12.0 if "مكثف" in prod_stage else 9.5; default_se = 64.0 if "مكثف" in prod_stage else 58.0
                else:
                    prod_stage = st.selectbox("خط إنتاج الإناث:", ["نعاج مرضعات (إدرار عالي)", "نعاج حامل (الفترة الأخيرة)", "نعاج جافة / صيانة"])
                    default_dp = 12.8 if "مرضعات" in prod_stage else (10.5 if "حامل" in prod_stage else 8.0)
                    default_se = 66.0 if "مرضعات" in prod_stage else (60.0 if "حامل" in prod_stage else 50.0)
            elif main_sector == "الماعز وسلالاتها":
                if gender_option == "ذكور (تسمين)":
                    prod_stage = st.selectbox("خط إنتاج الذكور:", ["تسمين جديان نمو سريع", "تيوس علفية جاهزة للتسويق"])
                    default_dp = 11.5 if "جديان" in prod_stage else 9.0; default_se = 62.0 if "جديان" in prod_stage else 55.0
                else:
                    prod_stage = st.selectbox("خط إنتاج الإناث:", ["عنزات حلابة وغزارة لبن", "عنزات حامل (دفع غذائي)", "صيانة دورية للأمهات"])
                    default_dp = 12.8 if "حلابة" in prod_stage else (10.0 if "حامل" in prod_stage else 7.8)
                    default_se = 65.0 if "حلابة" in prod_stage else (58.0 if "حامل" in prod_stage else 48.0)
            elif main_sector == "الأبقار وسلالاتها":
                prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج حليب وغزارة إدرار", "تسمين عجول مكثف"])
                default_dp = 12.5 if "حليب" in prod_stage else 10.0; default_se = 68.0 if "حليب" in prod_stage else 65.0
            elif main_sector == "الخيول والفروسية":
                prod_stage = st.selectbox("نوع الإنتاج:", ["خيول رياضة ونشاط مكثف", "أمهار نامية صغيرة", "فرسات مرضعات"])
                default_dp = 12.5 if "أمهار" in prod_stage or "مرضعات" in prod_stage else 9.5; default_se = 65.0 if "رياضة" in prod_stage else 60.0
            elif main_sector == "الطيور والسمان":
                if "السمان" in sub_type:
                    prod_stage = st.selectbox("نوع الإنتاج:", ["سمان بادي / نامي", "سمان بياض إنتاجي"])
                    default_dp = 20.0 if "بادي" in prod_stage else 16.5; default_se = 72.0 if "بادي" in prod_stage else 68.0
                else:
                    prod_stage = st.selectbox("نوع الإنتاج:", ["بادي دواجن 23%", "نامي دواجن 21%", "ناهي دواجن 19%", "بياض إنتاجي"])
                    default_dp = 20.0 if "بادي" in prod_stage else (18.5 if "نامي" in prod_stage else (16.5 if "ناهي" in prod_stage else 15.0))
                    default_se = 76.0 if "بادي" in prod_stage else (74.0 if "نامي" in prod_stage else (75.0 if "ناهي" in prod_stage else 70.0))
            else:
                prod_stage = st.selectbox("نوع الإنتاج:", ["بادئ زريعة أسماك عالي", "نمو وتسمين أسماك نيلية"])
                default_dp = 29.5 if "زريعة" in prod_stage else 25.0; default_se = 70.0

        if show_measurements:
            st.markdown('<div class="section-title">📐 القياسات الجسدية وتقدير الأوزان</div>', unsafe_allow_html=True)
            col_h, col_l, col_ag = st.columns(3)
            with col_h: h_girth = st.number_input("📏 محيط الصدر (سم):", value=150.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 75.0)
            with col_l: b_length = st.number_input("📏 طول الجسم (سم):", value=130.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 65.0)
            with col_ag: a_months = st.number_input("⏳ العمر التقديري (أشهر):", value=12)
            calc_weight = (h_girth ** 2 * b_length) / weight_factor; req_feed_kg = calc_weight * feed_factor
            st.success(f"📊 الوزن الحيوي المتوقع: **{calc_weight:.1f} كجم** | الاحتياج اليومي للمادة الجافة: **{req_feed_kg:.2f} كجم**")
        else:
            st.markdown('<div class="section-title">✨ قطاع الطيور والأسماك</div>', unsafe_allow_html=True)
            st.info("💡 تم تحييد شريط القياس الجسدي لعدم ملاءمته للطيور والأسماك.")

        st.markdown('<div class="section-title">📋 رابعاً: حدود الموازنة الذكية (DP & SE)</div>', unsafe_allow_html=True)
        col_p1, col_p2 = st.columns(2)
        use_cp_basis = st.checkbox("⚡ استخدم البروتين الخام (CP) بدلاً من المهضوم (DP)", value=False)
        if use_cp_basis:
            default_cp = default_dp / 0.82
            with col_p1:
                st.metric("🧬 بروتين خام (CP) مقترح:", f"{default_cp:.1f} %")
                override_cp = st.checkbox("⚙️ تعديل البروتين الخام")
                final_target_cp = st.slider("حدّد نسبة CP:", 5.0, 60.0, value=float(default_cp)) if override_cp else default_cp
            final_target_dp = None
        else:
            with col_p1:
                st.metric("🧬 بروتين مهضوم (DP) مقترح:", f"{default_dp} %")
                override_dp = st.checkbox("⚙️ تعديل فني اختياري للبروتين المهضوم")
                final_target_dp = st.slider("حدّد نسبة DP:", 5.0, 40.0, value=default_dp) if override_dp else default_dp
        with col_p2:
            st.metric("🌽 معادل النشاء (SE) مقترح:", f"{default_se} وحدة")
            override_se = st.checkbox("⚙️ تعديل فني اختياري لمعادل النشاء")
            final_target_se = st.slider("حدّد حد الـ SE المستهدف:", 10.0, 90.0, value=default_se) if override_se else default_se

        selected_ingredients = []
        ingredient_prices = {}
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            with st.expander(f"📁 {cat_name}", expanded=True if "الحبوب" in cat_name or "الأكساب" in cat_name else False):
                sub_cols = st.columns(3)
                for idx, (ing_name, _) in enumerate(items.items()):
                    with sub_cols[idx % 3]:
                        is_def = ing_name == chosen_concentrate or ing_name in ["ذرة صفراء", "سورجم (فتريتة)", "أمباز الفول السوداني (كسب)", "كسب فول صويا 44%", "نخالة قمح (ردة)", "ملح الطعام", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)", "بيكربونات الصوديوم (الصودا)", "مضاد سموم فطرية"]
                        checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                        current_live_price = live_prices.get(ing_name, 350.0)
                        if ing_name in custom_prices:
                            current_live_price = custom_prices[ing_name]
                        if st.session_state["user_role"] == "owner":
                            price_input = st.number_input(f"السعر للطن ({ing_name}) $:", min_value=5.0, value=float(current_live_price), key=f"price_{ing_name}")
                        else:
                            st.markdown(f"💰 السعر الحالي: **`${current_live_price:.2f}`** / طن")
                            price_input = current_live_price
                        if checked:
                            selected_ingredients.append(ing_name)
                            ingredient_prices[ing_name] = price_input

        fixed_additives = {"ملح الطعام": 0.5, "مضاد سموم فطرية": 0.2, "الحجر الجيري (بودرة بلاط)": 2.5 if "بياض" in prod_stage else 1.5, "فوسفات ثنائي الكالسيوم (DCP)": 1.0}
        auto_added_enzymes = {}
        mandatory_warnings = []

        if main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاتها", "الأغنام وسلالاتها 🐏"]:
            auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.75
            mandatory_warnings.append("🚨 <b>إضافة إلزامية - بيكربونات الصوديوم:</b> تم فرضها أوتوماتيكياً بنسبة 0.75% كمنظم حموضة (Buffer) لحماية الكرش من <b>التحمض Ruminal Acidosis</b>.")
        elif main_sector == "الطيور والسمان":
            auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.20

        if main_sector in ["الطيور والسمان", "الأسماك والأحياء المائية"]:
            auto_added_enzymes["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05
            mandatory_warnings.append("🚨 <b>إضافة إلزامية - إنزيم الفايتيز:</b> مضاف تلقائياً بنسبة 0.05% لتحرير <b>الفسفور النباتي المرتبط</b> وتحسين الهضم.")
        if "كسب بذور القطن (مقشور)" in selected_ingredients and main_sector == "الطيور والسمان":
            auto_added_enzymes["كبريتات الحديدوز (معادل الجوسيبول)"] = 0.15
            mandatory_warnings.append("⚠️ <b>معالجة الجوسيبول:</b> تم دمج كبريتات الحديدوز بنسبة 0.15% لربط <b>الجوسيبول الحر السام Toxic Gossypol</b> وإبطال مفعوله.")
        if main_sector == "الطيور والسمان" and (("شعير مطحون" in selected_ingredients) or ("قمح محلي مصنّع" in selected_ingredients)):
            auto_added_enzymes["إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)"] = 0.08
            mandatory_warnings.append("⚠️ <b>إضافة إنزيمات الـ NSP:</b> تم دمج إنزيمات كسر الروابط المتعددة لمنع عارض البراز الرطب (Wet Litter).")

        all_fixed_additives = {**fixed_additives, **auto_added_enzymes}
        for item in all_fixed_additives:
            if item not in selected_ingredients:
                selected_ingredients.append(item)
                ingredient_prices[item] = live_prices.get(item, 40.0)

        st.markdown("---")
        nz_placeholder = st.empty()

        if st.button("🚀 تشغيل محرك الاستمثال الخطي (بالبروتين المهضوم ومعادل النشاء)", type="primary", use_container_width=True):
            with nz_placeholder.container():
                st.warning("⚠️ **إشعار هام بشأن الإنزيمات ومضافات الأعلاف:** يرجى التأكد من موازنة درجات حرارة كبس العلف لضمان عدم تثبيط الإنزيمات والفيتامينات الدقيقة. (سيختفي هذا الإشعار تلقائياً بعد 40 ثانية)")

            c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
            bounds = [(all_fixed_additives[ing], all_fixed_additives[ing]) if ing in all_fixed_additives else (0.0, 100.0) for ing in selected_ingredients]

            A_eq = [[1.0 for _ in selected_ingredients]]
            b_eq = [100.0]

            cp_row = []
            se_row = []
            for ing in selected_ingredients:
                cp_val = 0.0; dc_val = 0.0; se_val = 0.0
                for cat in BIG_FEEDS_LIBRARY.values():
                    if ing in cat:
                        cp_val = cat[ing].get("CP", 0.0)
                        dc_val = cat[ing].get("DC", 0.0)
                        se_val = cat[ing].get("SE", 0.0)
                if use_cp_basis:
                    cp_row.append(cp_val)
                else:
                    cp_row.append(cp_val * dc_val)
                se_row.append(se_val)
            A_eq.append(cp_row)
            if use_cp_basis:
                b_eq.append(final_target_cp * 100.0)
            else:
                b_eq.append(final_target_dp * 100.0)

            A_ub = []
            b_ub = []
            A_ub.append([-1.0 * x for x in se_row])
            b_ub.append(-1.0 * final_target_se * 100.0)

            grain_indicators = [1.0 if ing in BIG_FEEDS_LIBRARY["🌾 الحبوب ومصادر الطاقة الكبرى"] else 0.0 for ing in selected_ingredients]
            if sum(grain_indicators) > 0:
                A_ub.append([-1.0 * x for x in grain_indicators])
                b_ub.append(-50.0)
            if "نخالة قمح (ردة)" in selected_ingredients:
                fiber_indicators = [1.0 if ing == "نخالة قمح (ردة)" else 0.0 for ing in selected_ingredients]
                A_ub.append(fiber_indicators)
                b_ub.append(18.0)

            # الحدود الديناميكية
            dynamic_limits = {
                "مولاس قصب السكر": {"default": 12.0, "دواجن": 5.0, "خيول": 8.0, "أسماك": 5.0},
                "يوريا علفية محصنة (المجترات فقط)": {"default": 1.0, "دواجن": 0.0, "خيول": 0.0, "أسماك": 0.0},
                "مخلفات مصانع البسكويت": {"default": 15.0, "دواجن": 10.0},
                "سرسة الأرز المطحونة": {"default": 10.0},
                "ملح الطعام": {"default": 1.0}
            }
            sector_key = main_sector.replace(" وسلالاتها","").replace(" والأحياء المائية","")
            for material, limits_dict in dynamic_limits.items():
                if material in selected_ingredients:
                    limit = limits_dict.get(sector_key, limits_dict.get("default", 15.0))
                    idx = selected_ingredients.index(material)
                    constraint_row = [0.0] * len(selected_ingredients)
                    constraint_row[idx] = 1.0
                    A_ub.append(constraint_row)
                    b_ub.append(limit)
                    mandatory_warnings.append(f"ℹ️ <b>حد أقصى:</b> {material} ≤ {limit}% (تلقائي للقطاع)")

            res = linprog(c_vector, A_ub=A_ub if A_ub else None, b_ub=b_ub if b_ub else None, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
            if not res.success:
                A_ub_flex = []
                b_ub_flex = []
                A_ub_flex.append([-1.0 * x for x in se_row])
                b_ub_flex.append(-1.0 * (final_target_se - 3.0) * 100.0)
                if sum(grain_indicators) > 0:
                    A_ub_flex.append([-1.0 * x for x in grain_indicators])
                    b_ub_flex.append(-40.0)
                if "نخالة قمح (ردة)" in selected_ingredients:
                    fiber_indicators = [1.0 if ing == "نخالة قمح (ردة)" else 0.0 for ing in selected_ingredients]
                    A_ub_flex.append(fiber_indicators)
                    b_ub_flex.append(25.0)
                for material, limits_dict in dynamic_limits.items():
                    if material in selected_ingredients:
                        limit = limits_dict.get(sector_key, limits_dict.get("default", 15.0)) + 3
                        idx = selected_ingredients.index(material)
                        constraint_row = [0.0] * len(selected_ingredients)
                        constraint_row[idx] = 1.0
                        A_ub_flex.append(constraint_row)
                        b_ub_flex.append(limit)
                res = linprog(c_vector, A_ub=A_ub_flex, b_ub=b_ub_flex, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

            if res.success:
                formula_results = {}
                computed_se_total = 0.0
                for idx, ing in enumerate(selected_ingredients):
                    if res.x[idx] > 0.0001:
                        formula_results[ing] = res.x[idx]
                        for cat in BIG_FEEDS_LIBRARY.values():
                            if ing in cat:
                                computed_se_total += (res.x[idx] / 100.0) * cat[ing].get("SE", 0.0)

                st.session_state["active_formula"] = formula_results
                st.session_state["active_cp_tag"] = final_target_dp if not use_cp_basis else (final_target_cp * 0.82)
                st.session_state["active_se_tag"] = computed_se_total
                st.session_state["active_breed_tag"] = sub_type
                st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES.get(dynamic_img_key, ANIMAL_IMAGES_RESOURCES["عام"])
                st.session_state["active_stage_title"] = f"{main_sector} ({gender_option}) - {prod_stage}"
                st.success(f"🎯 تم تشغيل محرك الاستمثال الخطي بنجاح في سوق: {user_city}")

                if not use_cp_basis and final_target_dp > 0:
                    nutritive_ratio = computed_se_total / final_target_dp
                    st.info(f"📊 النسبة الغذائية للخلطة (Nutritive Ratio = SE / DP): **{nutritive_ratio:.2f}**")

                if mandatory_warnings:
                    st.markdown("### 🔬 تقرير فحص العلل والتدخل البرمجي:")
                    for warn in mandatory_warnings:
                        st.markdown(f'<div class="warning-card">{warn}</div>', unsafe_allow_html=True)

                res_col1, res_col2 = st.columns([0.6, 0.4])
                with res_col1:
                    st.write("#### 📝 المقادير المعتمدة لتركيب طن واحد (كجم):")
                    for k, v in formula_results.items():
                        st.markdown(f'<div class="formula-item">▪️ <b>{k}:</b> {v:.2f} % ➡️ ({v*10:.1f} كجم / طن)</div>', unsafe_allow_html=True)

                    ton_cost = res.fun / 100.0 if hasattr(res, 'fun') else 280.0
                    st.session_state["computed_ton_cost"] = ton_cost
                    st.metric(f"💰 التكلفة الفعلية لإنتاج الطن في {user_city}: ", f"${ton_cost:.2f} (أو {ton_cost*local_rate:,.1f} {local_sym})")

                    col_share, col_pdf = st.columns(2)
                    with col_share:
                        share_message = f"منصة تاور العلمية - الخلطة المعتمدة: {sub_type} ({gender_option})، بتكلفة إنتاج {ton_cost:.2f}$ للطن. المشرف: الاختصاصي م. عبد القادر إسماعيل تاور."
                        encoded_share_msg = urllib.parse.quote(share_message)
                        st.link_button("📲 مشاركة الفاتورة عبر واتساب", f"https://wa.me/?text={encoded_share_msg}")
                    with col_pdf:
                        try:
                            pdf_data = pdf_generator.generate_comprehensive_report(formula_results, st.session_state["active_cp_tag"], f"{sub_type} ({gender_option})", ton_cost, user_city, ton_cost*local_rate, local_sym, computed_se_total, include_charts=True)
                            st.download_button("📥 تحميل التقرير الفني PDF", pdf_data, file_name=f"Tower_Scientific_Platform_{user_city}.pdf", mime="application/pdf", use_container_width=True)
                            # مشاركة PDF عبر واتساب (نص مع رابط تحميل افتراضي)
                            share_text = f"تقرير خلطة منصة تاور العلمية:\nالفصيل: {sub_type}\nالتكلفة: ${ton_cost:.2f}/طن\nالبروتين: {st.session_state['active_cp_tag']:.1f}%\nالمشرف: م. عبد القادر إسماعيل تاور"
                            encoded_share = urllib.parse.quote(share_text)
                            st.markdown(f'<a href="https://wa.me/?text={encoded_share}" target="_blank"><button style="background-color:#25D366; color:white; padding:10px; border-radius:5px;">📲 مشاركة التقرير عبر واتساب</button></a>', unsafe_allow_html=True)
                        except Exception as pdf_err:
                            st.error(f"⚠️ لم يتم بناء ملف الـ PDF: {pdf_err}")

                with res_col2:
                    fig = px.pie(values=list(formula_results.values()), names=list(formula_results.keys()), title="توزيع مكونات الخلطة", color_discrete_sequence=px.colors.sequential.Greens)
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    chart_data = pd.DataFrame({'المكون': list(formula_results.keys()), 'النسبة المئوية': list(formula_results.values()), 'الوزن (كجم/طن)': [v*10 for v in formula_results.values()]})
                    st.bar_chart(chart_data.set_index('المكون')['الوزن (كجم/طن)'])
            else:
                st.error("❌ تعذر إيجاد حل رياضي متزن. يرجى إتاحة خامات إضافية ككسب فول صويا أو أمباز الفول لتوسيع مساحة الحل.")
            time.sleep(40)
            nz_placeholder.empty()

    # --- مختبر التحليل ---
    with sub_tab_analyzer:
        st.markdown('<div class="section-title">🔬 مختبر فحص وتحليل الخلطات الجاهزة</div>', unsafe_allow_html=True)
        st.write("اكتب مقادير خلطتك الحالية بالكيلوجرام، وسيقوم المختبر بتحليلها برمجياً لتقدير نسبة البروتين المهضوم ومعادل النشاء الإجمالي.")

        st.subheader("🎯 حدد الحيوان والغرض المستهدف للمقارنة:")
        col_lab_animal, col_lab_stage = st.columns(2)
        with col_lab_animal:
            target_animal = st.selectbox("اختر الفصيل:", ["أبقار", "أغنام", "ماعز", "خيول", "دواجن لاحم", "دواجن بياض", "سمان", "أسماك"])
        with col_lab_stage:
            if target_animal in ["أبقار", "أغنام", "ماعز"]:
                production_type = st.selectbox("مرحلة الإنتاج:", ["تسمين", "حليب/إدرار", "حمل/دفع غذائي", "صيانة"])
            elif target_animal in ["دواجن لاحم", "دواجن بياض", "سمان"]:
                production_type = st.selectbox("مرحلة الإنتاج:", ["بادي", "نامي", "ناهي", "بياض"])
            else:
                production_type = st.selectbox("مرحلة الإنتاج:", ["نمو", "تسمين نهائي"])

        cp_requirements = {
            ("أبقار", "تسمين"): 12.0, ("أبقار", "حليب/إدرار"): 14.0, ("أبقار", "حمل/دفع غذائي"): 11.0, ("أبقار", "صيانة"): 9.0,
            ("أغنام", "تسمين"): 13.0, ("أغنام", "حليب/إدرار"): 14.5, ("أغنام", "حمل/دفع غذائي"): 11.5, ("أغنام", "صيانة"): 8.5,
            ("ماعز", "تسمين"): 12.5, ("ماعز", "حليب/إدرار"): 14.0, ("ماعز", "حمل/دفع غذائي"): 11.0, ("ماعز", "صيانة"): 8.0,
            ("خيول", "نمو"): 13.0, ("خيول", "تسمين نهائي"): 11.0,
            ("دواجن لاحم", "بادي"): 23.0, ("دواجن لاحم", "نامي"): 21.0, ("دواجن لاحم", "ناهي"): 19.0,
            ("دواجن بياض", "بادي"): 20.0, ("دواجن بياض", "نامي"): 18.0, ("دواجن بياض", "ناهي"): 16.5, ("دواجن بياض", "بياض"): 16.0,
            ("سمان", "بادي"): 24.0, ("سمان", "نامي"): 22.0, ("سمان", "ناهي"): 20.0, ("سمان", "بياض"): 18.0,
            ("أسماك", "نمو"): 32.0, ("أسماك", "تسمين نهائي"): 28.0
        }
        suggested_cp = cp_requirements.get((target_animal, production_type), 15.0)
        suggested_dp = suggested_cp * 0.80

        analysis_basis = st.radio("أساس التحليل:", ["بروتين مهضوم (DP)", "بروتين خام (CP)"], horizontal=True)
        if analysis_basis == "بروتين مهضوم (DP)":
            target_value = st.number_input("النسبة المستهدفة (DP %)", min_value=5.0, max_value=50.0, value=float(suggested_dp), step=0.1)
            st.caption(f"البروتين الخام المقترح ≈ {suggested_cp:.1f}%")
        else:
            target_value = st.number_input("النسبة المستهدفة (CP %)", min_value=5.0, max_value=50.0, value=float(suggested_cp), step=0.1)

        st.markdown("---")
        st.subheader("📥 أدخل أوزان المكونات بالكيلوجرام:")
        lab_user_inputs = {}
        all_library_ingredients = []
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            for ing_name in items.keys():
                all_library_ingredients.append(ing_name)

        col_input1, col_input2, col_input3 = st.columns(3)
        total_ing_count = len(all_library_ingredients)
        segment = total_ing_count // 3 + 1
        with col_input1:
            for ing_name in all_library_ingredients[:segment]:
                lab_user_inputs[ing_name] = st.number_input(f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0, step=5.0, key=f"lab_in_{ing_name}")
        with col_input2:
            for ing_name in all_library_ingredients[segment:segment*2]:
                lab_user_inputs[ing_name] = st.number_input(f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0, step=5.0, key=f"lab_in_{ing_name}")
        with col_input3:
            for ing_name in all_library_ingredients[segment*2:]:
                lab_user_inputs[ing_name] = st.number_input(f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0, step=5.0, key=f"lab_in_{ing_name}")

        st.markdown("---")
        if st.button("🧪 تشغيل التحليل المخبري", type="primary", use_container_width=True):
            lab_total_weight = sum(lab_user_inputs.values())
            if lab_total_weight <= 0:
                st.warning("⚠️ الرجاء إدخال أوزان أكبر من الصفر.")
            else:
                calculated_total_cp = 0.0
                calculated_total_dp = 0.0
                calculated_total_se = 0.0
                entered_components_summary = []
                for ing_name, weight in lab_user_inputs.items():
                    if weight > 0:
                        pct = weight / lab_total_weight
                        ing_cp = 0.0; ing_dc = 0.0; ing_se = 0.0
                        for cat, items in BIG_FEEDS_LIBRARY.items():
                            if ing_name in items:
                                ing_cp = items[ing_name].get("CP", 0.0)
                                ing_dc = items[ing_name].get("DC", 0.0)
                                ing_se = items[ing_name].get("SE", 0.0)
                        calculated_total_cp += pct * ing_cp
                        calculated_total_dp += pct * (ing_cp * ing_dc)
                        calculated_total_se += pct * ing_se
                        entered_components_summary.append({"المادة العلفية": ing_name, "الوزن المدخل": f"{weight:.1f} كجم", "النسبة المئوية": f"{pct * 100:.2f}%"})

                st.success("🔬 تم فحص العينة وتحليل المحتوى الغذائي بنجاح!")
                st.markdown(f"### ⚖️ إجمالي وزن الخلطة: **{lab_total_weight:.1f} كجم**")
                st.write("#### 📊 نسب توزيع المكونات:")
                st.table(pd.DataFrame(entered_components_summary))

                st.markdown("---")
                st.write("#### 🔬 تقرير الفحص المخبري النهائي:")
                if analysis_basis == "بروتين مهضوم (DP)":
                    comparison_value = calculated_total_dp
                    status_label = "✅ مطابق وممتاز" if comparison_value >= target_value else "⚠️ ناقص البروتين المهضوم"
                    st.write(f"🔬 البروتين الخام (CP) المحسوب: **{calculated_total_cp:.2f}%**")
                    st.write(f"🔬 البروتين المهضوم (DP) المحسوب: **{calculated_total_dp:.2f}%**")
                else:
                    comparison_value = calculated_total_cp
                    status_label = "✅ مطابق وممتاز" if comparison_value >= target_value else "⚠️ ناقص البروتين الخام"
                    st.write(f"🔬 البروتين الخام (CP) المحسوب: **{calculated_total_cp:.2f}%**")
                    st.write(f"🔬 البروتين المهضوم (DP) المحسوب: **{calculated_total_dp:.2f}%**")

                lab_report_data = [
                    {"العنصر الغذائي": "البروتين المهضوم (DP)", "القيمة المحسوبة": f"{calculated_total_dp:.2f}%", "الاحتياج القياسي": f"{target_value:.1f}%" if analysis_basis == "بروتين مهضوم (DP)" else "-", "التقييم": status_label},
                    {"العنصر الغذائي": "البروتين الخام (CP)", "القيمة المحسوبة": f"{calculated_total_cp:.2f}%", "الاحتياج القياسي": f"{target_value:.1f}%" if analysis_basis == "بروتين خام (CP)" else "-", "التقييم": "-"},
                    {"العنصر الغذائي": "معادل النشاء (SE)", "القيمة المحسوبة": f"{calculated_total_se:.2f} وحدة", "الاحتياج القياسي": "مرن حسب الفصيل", "التقييم": "تحليل طاقة كلي"}
                ]
                st.table(pd.DataFrame(lab_report_data))

                st.write("📊 التمثيل البياني لتوزيع المواد المدخلة:")
                graph_data = {k: v for k, v in lab_user_inputs.items() if v > 0}
                if graph_data:
                    fig = px.bar(x=list(graph_data.keys()), y=list(graph_data.values()), labels={'x': 'المادة العلفية', 'y': 'الوزن (كجم)'}, title="توزيع أوزان المواد في الخلطة المختبرة")
                    st.plotly_chart(fig, use_container_width=True)

                # مشاركة نتيجة المختبر عبر واتساب
                lab_share_text = f"نتيجة مختبر منصة تاور:\nالحيوان: {target_animal} - {production_type}\nالبروتين المحسوب: {comparison_value:.2f}%\nالمعيار: {target_value:.1f}%"
                encoded_lab = urllib.parse.quote(lab_share_text)
                st.markdown(f'<a href="https://wa.me/?text={encoded_lab}" target="_blank"><button style="background-color:#25D366; color:white; padding:10px; border-radius:5px;">📲 مشاركة النتيجة عبر واتساب</button></a>', unsafe_allow_html=True)

# ====================================================================
# التبويبات الأخرى (بورصة، مخازن، مبيعات، ديباجة، تحليلات، تعليقات، دليل)
# ====================================================================
if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[1]:
        st.markdown('<div class="section-title">📊 لوحة تحكم بورصة تاور المركزية الشاملة</div>', unsafe_allow_html=True)
        if st.session_state["user_role"] == "specialist":
            st.warning("⚠️ حساب مختص: متاح لك استعراض الأسعار فقط، التعديل محجوز لإدارة المنصة.")

        tab_livestock, tab_products = st.tabs(["🐄 بورصة الماشية", "🥛 بورصة المنتجات"])
        with tab_livestock:
            col_edit1, col_edit2 = st.columns(2)
            with col_edit1:
                st.subheader("أسعار الماشية والداجن")
                for animal, price in st.session_state["global_livestock_prices"].items():
                    if st.session_state["user_role"] == "owner":
                        st.session_state["global_livestock_prices"][animal] = st.number_input(f"تحديث: {animal}", min_value=0.0, value=float(price), step=0.1, key=f"livestock_{animal}")
                    else:
                        st.markdown(f"▪️ {animal}: **${price:.2f}**")
            with col_edit2:
                if st.session_state["user_role"] == "owner":
                    st.subheader("إضافة حيوان جديد")
                    new_animal = st.text_input("اسم الحيوان/السلالة:")
                    new_price = st.number_input("السعر بالدولار:", min_value=0.0, value=0.0)
                    if st.button("إضافة إلى البورصة") and new_animal:
                        st.session_state["global_livestock_prices"][f"{new_animal} ($)"] = new_price
                        st.success("تمت الإضافة بنجاح!")
                        st.rerun()
        with tab_products:
            col_prod1, col_prod2 = st.columns(2)
            with col_prod1:
                st.subheader("أسعار المنتجات الحيوانية")
                for product, price in st.session_state["global_products_prices"].items():
                    if st.session_state["user_role"] == "owner":
                        st.session_state["global_products_prices"][product] = st.number_input(f"تحديث: {product}", min_value=0.0, value=float(price), step=0.05, key=f"prod_edit_{product}")
                    else:
                        st.markdown(f"▪️ {product}: **${price:.2f}**")

        # واجهة تحرير أسعار المدن للمالك
        if st.session_state["user_role"] == "owner":
            with st.expander("⚙️ تحرير أسعار المواد للمدن"):
                city_keys = list(CITY_CUSTOM_PRICES.keys())
                if city_keys:
                    edit_city = st.selectbox("اختر المدينة:", city_keys, format_func=lambda x: x.replace("|||", " - "))
                    if edit_city:
                        prices_to_edit = CITY_CUSTOM_PRICES[edit_city]
                        for material in sorted(live_prices.keys()):
                            new_price = st.number_input(material, value=prices_to_edit.get(material, live_prices[material]), step=1.0, key=f"city_price_{material}")
                            prices_to_edit[material] = new_price
                        if st.button("💾 حفظ أسعار هذه المدينة"):
                            CITY_CUSTOM_PRICES[edit_city] = prices_to_edit
                            save_city_prices(CITY_CUSTOM_PRICES)
                            st.success("تم حفظ الأسعار!")
                            st.rerun()
                else:
                    st.info("لا توجد أسعار مخصصة بعد. عند استخدام البرنامج، سيتم حفظ الأسعار تلقائياً.")

    with tabs[2]:
        st.markdown('<div class="section-title">🏭 لوحة التحكم الذكية بالمخازن والمستودعات المركزية</div>', unsafe_allow_html=True)
        if st.session_state["user_role"] == "specialist":
            st.warning("⚠️ حساب مختص: يمكنك مراجعة الأرصدة فقط دون تعديل.")
        stock_warnings = InventoryManager.check_stock_levels()
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        with col_stats1: st.metric("إجمالي المواد", len(st.session_state["inventory"]))
        with col_stats2:
            critical_items = sum(1 for v in stock_warnings.values() if v == "نفذ المخزون")
            st.metric("مواد نفذت", critical_items, delta=f"-{critical_items}" if critical_items > 0 else "0")
        with col_stats3:
            low_items = sum(1 for v in stock_warnings.values() if v == "منخفض")
            st.metric("مواد منخفضة", low_items, delta=f"-{low_items}" if low_items > 0 else "0")
        with col_stats4:
            healthy_items = len(st.session_state["inventory"]) - critical_items - low_items
            st.metric("مواد آمنة", healthy_items)
        st.markdown("---")
        inv_cols = st.columns(3)
        for idx, (ing_name, qty_data) in enumerate(list(st.session_state["inventory"].items())):
            with inv_cols[idx % 3]:
                qty = qty_data if isinstance(qty_data, (int, float)) else qty_data["quantity"]
                threshold = 5.0 if isinstance(qty_data, (int, float)) else qty_data.get("min_threshold", 5.0)
                if qty <= 0:
                    status_badge = f'<span class="stock-critical">⚠️ نفذ: {qty:.2f} طن</span>'
                elif qty < threshold:
                    status_badge = f'<span class="stock-critical">⚠️ حرج: {qty:.2f} طن</span>'
                else:
                    status_badge = f'<span class="stock-normal">آمن: {qty:.2f} طن</span>'
                st.markdown(f"**{ing_name}** | {status_badge}", unsafe_allow_html=True)
                if st.session_state["user_role"] == "owner":
                    new_qty = st.number_input(f"تحديث ({ing_name}) طن:", min_value=0.0, value=float(qty), key=f"inv_input_{ing_name}")
                    if isinstance(st.session_state["inventory"][ing_name], dict):
                        st.session_state["inventory"][ing_name]["quantity"] = new_qty
                        st.session_state["inventory"][ing_name]["last_updated"] = datetime.now().isoformat()
                    else:
                        st.session_state["inventory"][ing_name] = new_qty

    with tabs[3]:
        st.markdown('<div class="section-title">💰 نظام تسويق المنتجات وإصدار الفواتير مع الخصم التلقائي</div>', unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: client_name = st.text_input("اسم العميل / المزرعة:", "مزارع الإنتاج المتكاملة")
        with col_c2: required_tons = st.number_input("الكمية المطلوبة (طن):", min_value=0.1, value=2.0, step=0.5)
        with col_c3: added_profit = st.number_input("هامش الربح للطن ($):", min_value=0.0, value=50.0)
        selling_price = st.session_state["computed_ton_cost"] + added_profit
        total_bill = selling_price * required_tons
        st.markdown("### 🧾 فاتورة بيع وتوريد أعلاف رسمية")
        col_fact1, col_fact2 = st.columns(2)
        with col_fact1:
            st.markdown(f"""<div class="price-card"><h4>تفاصيل الفاتورة:</h4><p>العميل: <b>{client_name}</b></p><p>الكمية: <b>{required_tons} طن</b></p><p>سعر الطن: <b>${selling_price:.2f}</b></p><p style="font-size: 1.2rem; color: #1b5e20;">الإجمالي: <b>${total_bill:.2f}</b></p><p style="color: #666;">ما يعادل: <b>{total_bill*local_rate:,.1f} {local_sym}</b></p></div>""", unsafe_allow_html=True)
        with col_fact2:
            st.markdown("#### 📊 مكونات الخلطة المباعة:")
            if st.session_state["active_formula"]:
                for ingredient, pct in st.session_state["active_formula"].items():
                    required_amount = (pct / 100) * required_tons
                    st.markdown(f"▪️ {ingredient}: **{required_amount:.2f}** طن ({pct:.1f}% من الخلطة)")
        if st.session_state["user_role"] == "owner":
            if st.button("✅ تأكيد عملية البيع وخصم المكونات من المستودع", type="primary", use_container_width=True):
                can_deduct = True
                for name, pct in st.session_state["active_formula"].items():
                    current_stock = st.session_state["inventory"].get(name, 0.0)
                    if isinstance(current_stock, dict):
                        current_stock = current_stock["quantity"]
                    required_amount = (pct / 100) * required_tons
                    if current_stock < required_amount:
                        can_deduct = False
                        st.error(f"❌ رصيد غير كافي: {name}!")
                        break
                if can_deduct:
                    for name, pct in st.session_state["active_formula"].items():
                        required_amount = (pct / 100) * required_tons
                        if isinstance(st.session_state["inventory"][name], dict):
                            st.session_state["inventory"][name]["quantity"] -= required_amount
                            st.session_state["inventory"][name]["last_updated"] = datetime.now().isoformat()
                        else:
                            st.session_state["inventory"][name] -= required_amount
                    st.success("🔥 تم الخصم التلقائي وتحديث المخازن بنجاح!")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
        else:
            st.info("ℹ️ تأكيد الفواتير وحركات الخصم متاحة حصرياً لإدارة المالك.")

    with tabs[4]:
        st.markdown('<div class="section-title">👑 مصمم ديباجات الطباعة الفنية على جوالات الأعلاف</div>', unsafe_allow_html=True)
        trade_brand = st.text_input("اسم البراند التجاري:", "منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف")
        col_preview, col_options = st.columns([0.7, 0.3])
        with col_preview:
            st.markdown(f"""<div class="sack-tag"><img src="{st.session_state['active_animal_img']}" class="animal-banner-img"><h2 style="text-align: center; margin-top:0; color: #1b5e20;">🌟 {trade_brand} 🌟</h2><h3 style="text-align: center; color: #c62828; margin-top:0; font-weight: bold;">الاختصاصي م. عبد القادر إسماعيل تاور</h3><p style="text-align: center; font-weight: bold; background-color:#e8f5e9; padding:10px; color:#1b5e20; border-radius: 8px;">🎯 {st.session_state['active_stage_title']} | DP: {st.session_state['active_cp_tag']:.1f}% | SE: {st.session_state['active_se_tag']:.1f} وحدة</p><div style="text-align: center; margin-top: 15px;"><small style="color: #666;">تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d')}</small></div></div>""", unsafe_allow_html=True)
        with col_options:
            st.markdown("#### خيارات التخصيص:")
            show_qr = st.checkbox("إضافة QR Code", value=True)
            show_date = st.checkbox("إظهار تاريخ الإنتاج", value=True)
            font_size = st.slider("حجم الخط", 12, 24, 16)
            if st.button("📥 تصدير الديباجة كـ PDF", use_container_width=True):
                st.success("تم تجهيز الديباجة للطباعة!")

    with tabs[5]:
        st.markdown('<div class="section-title">📈 التحليلات المتقدمة ولوحة المؤشرات</div>', unsafe_allow_html=True)
        col_met1, col_met2, col_met3, col_met4 = st.columns(4)
        with col_met1: st.markdown("""<div class="metric-card"><h3 style="color: #1b5e20;">عدد الخلطات</h3><h2 style="color: #2e7d32;">1,247</h2><p>خلطة تم توليدها</p></div>""", unsafe_allow_html=True)
        with col_met2: st.markdown("""<div class="metric-card"><h3 style="color: #1565C0;">متوسط التكلفة</h3><h2 style="color: #1976D2;">$285</h2><p>لطن العلف</p></div>""", unsafe_allow_html=True)
        with col_met3: st.markdown("""<div class="metric-card"><h3 style="color: #E65100;">نسبة التوفير</h3><h2 style="color: #F57C00;">18%</h2><p>مقارنة بالتقليدي</p></div>""", unsafe_allow_html=True)
        with col_met4: st.markdown("""<div class="metric-card"><h3 style="color: #2E7D32;">رضا العملاء</h3><h2 style="color: #388E3C;">96%</h2><p>تقييم إيجابي</p></div>""", unsafe_allow_html=True)
        st.markdown("---")
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("📊 توزيع استخدام المواد العلفية")
            usage_data = pd.DataFrame({'المادة': ['ذرة', 'صويا', 'نخالة', 'أملاح', 'أخرى'], 'نسبة الاستخدام': [45, 25, 15, 10, 5]})
            fig = px.pie(usage_data, values='نسبة الاستخدام', names='المادة', title='المواد الأكثر استخداماً', color_discrete_sequence=px.colors.sequential.Greens)
            st.plotly_chart(fig, use_container_width=True)
        with col_chart2:
            st.subheader("📈 اتجاه أسعار المواد الخام")
            dates = pd.date_range(start='2024-01-01', periods=12, freq='ME')
            price_trend = pd.DataFrame({'التاريخ': dates, 'الذرة': [220, 225, 230, 228, 235, 240, 238, 242, 245, 248, 250, 252], 'الصويا': [440, 445, 442, 448, 450, 455, 452, 458, 460, 462, 465, 468]})
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=price_trend['التاريخ'], y=price_trend['الذرة'], mode='lines+markers', name='الذرة', line=dict(color='#2e7d32', width=2)))
            fig.add_trace(go.Scatter(x=price_trend['التاريخ'], y=price_trend['الصويا'], mode='lines+markers', name='الصويا', line=dict(color='#1565C0', width=2)))
            fig.update_layout(title='اتجاه أسعار المواد الخام خلال العام', xaxis_title='التاريخ', yaxis_title='السعر ($/طن)', hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
        st.subheader("🌡️ خريطة حرارية لتكاليف الخلطات حسب القطاع")
        heatmap_data = pd.DataFrame({'القطاع': ['أبقار', 'أغنام', 'دواجن', 'أسماك', 'خيول'], 'البروتين': [12.5, 11.0, 20.0, 28.0, 12.0], 'التكلفة': [285, 265, 420, 580, 350], 'الكفاءة': [85, 82, 92, 88, 80]})
        fig = px.scatter(heatmap_data, x='البروتين', y='التكلفة', size='الكفاءة', color='القطاع', hover_name='القطاع', title='علاقة البروتين بالتكلفة حسب القطاع', size_max=30)
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------
# تبويب إدارة مزارع الدجاج اللاحم (خاص بالمالك فقط)
# -----------------------------------------------------------------
if st.session_state["user_role"] == "owner":
    # التبويب رقم 6 للمالك (حسب ترتيب tabs_titles أعلاه)
    with tabs[6]:
        st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج اللاحم (Broiler Management) – خاص بالمالك</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background-color: #f0fdf4; padding: 15px; border-radius: 12px; border-right: 5px solid #16a34a; margin-bottom: 20px;'>
        <b>📘 دليل سريع:</b> استخدم هذا التبويب لتسجيل ومتابعة مؤشرات الأداء الرئيسية (KPIs) لدورة التسمين. أدخل البيانات الحالية لقطيعك وسيقوم النظام بحساب ADG، FCR، EPEF، ونسب النفوق والاستبعاد تلقائياً. هذا القسم متاح فقط لمالك المنصة.
        </div>
        """, unsafe_allow_html=True)

        # عمودان رئيسيان: المدخلات (يمين) والمخرجات (يسار)
        col_inputs, col_outputs = st.columns([0.5, 0.5])

        with col_inputs:
            st.markdown("#### 📝 بيانات القطيع الحالية")
            farm_name = st.text_input("اسم المزرعة / الدورة", value=st.session_state["broiler_farm_data"]["farm_name"], key="bf_farm_name")
            flock_age = st.number_input("عمر القطيع (يوم)", min_value=1, max_value=60, value=st.session_state["broiler_farm_data"]["flock_age_days"], step=1, key="bf_age")
            initial_birds = st.number_input("عدد الكتاكيت المستلمة (طير)", min_value=1, value=st.session_state["broiler_farm_data"]["initial_birds"], step=100, key="bf_initial")
            dead_birds = st.number_input("عدد الطيور النافقة حتى الآن", min_value=0, value=st.session_state["broiler_farm_data"]["dead_birds"], step=1, key="bf_dead")
            culled_birds = st.number_input("الطيور المستبعدة (مريضة / ضعيفة)", min_value=0, value=st.session_state["broiler_farm_data"]["culled_birds"], step=1, key="bf_culled")

            st.markdown("#### ⚖️ الأوزان والاستهلاك")
            avg_weight_kg = st.number_input("متوسط الوزن الحي الحالي (كجم)", min_value=0.0, value=st.session_state["broiler_farm_data"]["current_weight_kg"], step=0.05, format="%.3f", key="bf_weight")
            initial_weight_kg = st.number_input("متوسط وزن الكتكوت عند الاستلام (كجم)", min_value=0.030, value=st.session_state["broiler_farm_data"]["initial_weight_kg"], step=0.005, format="%.3f", key="bf_init_wt")
            total_feed_kg = st.number_input("إجمالي العلف المستهلك حتى الآن (كجم)", min_value=0.0, value=st.session_state["broiler_farm_data"]["total_feed_consumed_kg"], step=100.0, key="bf_feed")
            water_consumption_l = st.number_input("استهلاك المياه التراكمي (لتر) - اختياري", min_value=0.0, value=st.session_state["broiler_farm_data"]["total_water_consumed_l"], step=100.0, key="bf_water")

            st.markdown("#### 🌡️ الظروف البيئية")
            temp_c = st.number_input("درجة الحرارة داخل العنبر (مئوي)", min_value=10.0, max_value=45.0, value=st.session_state["broiler_farm_data"]["temperature_c"], step=0.5, key="bf_temp")
            humidity = st.number_input("الرطوبة النسبية (%)", min_value=20.0, max_value=90.0, value=st.session_state["broiler_farm_data"]["humidity_percent"], step=1.0, key="bf_hum")
            ventilation = st.selectbox("حالة التهوية", ["سيئة", "مقبولة", "جيدة", "ممتازة"], index=["سيئة", "مقبولة", "جيدة", "ممتازة"].index(st.session_state["broiler_farm_data"]["ventilation_status"]), key="bf_vent")
            litter = st.selectbox("جودة الفرشة", ["سيئة", "مقبولة", "جيدة", "ممتازة"], index=["سيئة", "مقبولة", "جيدة", "ممتازة"].index(st.session_state["broiler_farm_data"]["litter_quality"]), key="bf_litter")

            notes = st.text_area("ملاحظات إضافية (الأمراض، الأدوية، إلخ)", value=st.session_state["broiler_farm_data"]["notes"], key="bf_notes")

            # حفظ التغييرات في الجلسة
            if st.button("💾 حفظ بيانات القطيع", use_container_width=True, type="primary", key="bf_save"):
                st.session_state["broiler_farm_data"].update({
                    "farm_name": farm_name,
                    "flock_age_days": flock_age,
                    "initial_birds": initial_birds,
                    "dead_birds": dead_birds,
                    "culled_birds": culled_birds,
                    "current_weight_kg": avg_weight_kg,
                    "initial_weight_kg": initial_weight_kg,
                    "total_feed_consumed_kg": total_feed_kg,
                    "total_water_consumed_l": water_consumption_l,
                    "temperature_c": temp_c,
                    "humidity_percent": humidity,
                    "ventilation_status": ventilation,
                    "litter_quality": litter,
                    "notes": notes,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("تم حفظ بيانات الدورة الحالية بنجاح!")
                st.rerun()

        with col_outputs:
            # استخراج البيانات المحفوظة
            data = st.session_state["broiler_farm_data"]
            age = data["flock_age_days"]
            initial = data["initial_birds"]
            dead = data["dead_birds"]
            culled = data["culled_birds"]
            current_wt = data["current_weight_kg"]
            init_wt = data["initial_weight_kg"]
            total_feed = data["total_feed_consumed_kg"]
            water = data["total_water_consumed_l"]

            # حساب المؤشرات
            total_birds_alive = initial - dead - culled
            total_weight_gain_kg = total_birds_alive * (current_wt - init_wt) if total_birds_alive > 0 else 0
            adg_g = BroilerFarmManager.calculate_adg(current_wt * 1000, init_wt * 1000, age) if age > 0 else 0.0
            fcr = BroilerFarmManager.calculate_fcr(total_feed, total_weight_gain_kg) if total_weight_gain_kg > 0 else 0.0
            mortality_rate = BroilerFarmManager.calculate_mortality_rate(dead, initial)
            cull_rate = BroilerFarmManager.calculate_cull_rate(culled, initial)
            livability = BroilerFarmManager.calculate_livability(initial, dead)
            epef = BroilerFarmManager.calculate_epef(livability, current_wt, age, fcr)

            # عرض بطاقات KPIs
            st.markdown("#### 📊 مؤشرات الأداء الرئيسية (KPIs)")
            kpi_cols = st.columns(3)
            kpi_cols[0].metric("📈 الوزن الحي الحالي (كجم)", f"{current_wt:.3f}", delta=f"{((current_wt - init_wt)/init_wt*100):.1f}% منذ الاستلام")
            kpi_cols[1].metric("📅 معدل النمو اليومي ADG (جم)", f"{adg_g:.1f}", delta=None)
            kpi_cols[2].metric("🔄 معامل التحويل FCR", f"{fcr:.2f}", delta=None if fcr == 0 else ("ممتاز" if fcr < 1.6 else "جيد" if fcr < 1.8 else "مرتفع"))
            
            kpi_cols2 = st.columns(3)
            kpi_cols2[0].metric("💀 نسبة النفوق (%)", f"{mortality_rate:.2f}%", delta=f"-{mortality_rate:.1f}%")
            kpi_cols2[1].metric("🚫 نسبة الاستبعاد (%)", f"{cull_rate:.2f}%", delta=None)
            kpi_cols2[2].metric("❤️ الحيوية (Livability)", f"{livability:.1f}%", delta=None)
            
            kpi_cols3 = st.columns(2)
            kpi_cols3[0].metric("🏆 مؤشر الأداء الأوروبي EPEF", f"{epef:.0f}", delta="مرجع: >300 ممتاز" if epef > 300 else "تحتاج تحسين")
            if water > 0:
                water_to_feed = water / total_feed if total_feed > 0 else 0
                kpi_cols3[1].metric("💧 نسبة الماء إلى العلف", f"{water_to_feed:.2f}", delta="مثالي 1.6-2.0" if 1.6 <= water_to_feed <= 2.0 else "مرتفع/منخفض")
            else:
                kpi_cols3[1].metric("💧 استهلاك الماء", "لم يدخل", delta=None)

            # جدول الحرارة والرطوبة المرجعي
            st.markdown("#### 🌡️ جدول الحرارة والرطوبة المرجعي حسب العمر")
            temp_hum_df = BroilerFarmManager.get_temp_humidity_table()
            st.dataframe(temp_hum_df, use_container_width=True, hide_index=True)
            
            # تقييم الظروف الحالية مقابل الجدول
            closest_age = temp_hum_df.iloc[(temp_hum_df['العمر (يوم)'] - age).abs().argsort()[:1]].iloc[0]
            rec_temp = closest_age['درجة الحرارة (مئوي)']
            rec_hum = closest_age['الرطوبة النسبية (%)']
            temp_ok = abs(temp_c - rec_temp) <= 2
            hum_ok = abs(humidity - rec_hum) <= 10
            if not temp_ok or not hum_ok:
                st.warning(f"⚠️ درجة الحرارة الحالية ({temp_c}°C) أو الرطوبة ({humidity}%) خارج النطاق الموصى به لعمر {age} يوم (موصى: {rec_temp}°C, {rec_hum}% رطوبة).")

            # تقرير يومي للمزرعة
            st.markdown("#### 📋 تقرير يومي للمزرعة (Daily Farm Report)")
            report_lines = [
                f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                f"🏷️ اسم المزرعة: {data['farm_name']}",
                f"📊 عمر القطيع: {age} يوم",
                f"🐔 عدد الطيور الحية: {total_birds_alive:,} من أصل {initial:,}",
                f"⚖️ متوسط الوزن: {current_wt:.3f} كجم",
                f"📈 معدل النمو اليومي: {adg_g:.1f} جم/يوم",
                f"🔄 معامل التحويل: {fcr:.2f}",
                f"💀 النفوق التراكمي: {dead} طير ({mortality_rate:.2f}%)",
                f"🚫 الاستبعاد: {culled} طير ({cull_rate:.2f}%)",
                f"❤️ الحيوية: {livability:.1f}%",
                f"🏆 مؤشر EPEF: {epef:.0f}",
                f"🌡️ درجة الحرارة: {temp_c}°C (الموصى: {rec_temp}°C)",
                f"💧 الرطوبة: {humidity}% (الموصى: {rec_hum}%)",
                f"💨 التهوية: {ventilation}",
                f"🌾 جودة الفرشة: {litter}",
                f"📝 ملاحظات: {notes if notes else 'لا توجد'}"
            ]
            report_text = "\n".join(report_lines)
            st.text_area("نص التقرير", value=report_text, height=300, disabled=True)
            
            col_report_share, col_report_save = st.columns(2)
            with col_report_share:
                encoded_report = urllib.parse.quote(report_text[:1500])  # واتساب حد أقصى
                st.link_button("📲 مشاركة التقرير عبر واتساب", f"https://wa.me/?text={encoded_report}", use_container_width=True)
            with col_report_save:
                if st.button("➕ حفظ الدورة الحالية في السجل", use_container_width=True):
                    # إضافة نسخة من البيانات الحالية مع timestamp
                    cycle_copy = data.copy()
                    cycle_copy["saved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cycle_copy["kpis"] = {
                        "ADG_g": adg_g,
                        "FCR": fcr,
                        "Mortality_%": mortality_rate,
                        "Cull_%": cull_rate,
                        "Livability_%": livability,
                        "EPEF": epef
                    }
                    st.session_state["broiler_cycles_history"].insert(0, cycle_copy)  # الأحدث أولاً
                    if len(st.session_state["broiler_cycles_history"]) > 10:
                        st.session_state["broiler_cycles_history"] = st.session_state["broiler_cycles_history"][:10]
                    st.success("تم حفظ الدورة في سجل التاريخ!")
                    st.rerun()
            
            # عرض تاريخ الدورات السابقة
            if st.session_state["broiler_cycles_history"]:
                st.markdown("#### 📜 تاريخ الدورات السابقة (آخر 10)")
                history_df = pd.DataFrame([{
                    "التاريخ": c["saved_at"],
                    "المزرعة": c["farm_name"],
                    "العمر": c["flock_age_days"],
                    "الوزن كجم": c["current_weight_kg"],
                    "FCR": c["kpis"]["FCR"],
                    "EPEF": c["kpis"]["EPEF"],
                    "نسبة النفوق%": c["kpis"]["Mortality_%"]
                } for c in st.session_state["broiler_cycles_history"]])
                st.dataframe(history_df, use_container_width=True, hide_index=True)
                
                # زر لتحميل دورة سابقة
                selected_cycle = st.selectbox("تحميل دورة سابقة للاطلاع", range(len(st.session_state["broiler_cycles_history"])), format_func=lambda i: f"{st.session_state['broiler_cycles_history'][i]['farm_name']} - {st.session_state['broiler_cycles_history'][i]['saved_at']}")
                if st.button("تحميل الدورة المحددة"):
                    st.session_state["broiler_farm_data"] = st.session_state["broiler_cycles_history"][selected_cycle].copy()
                    # إزالة المفاتيح الإضافية التي لا نحتاجها في المدخلات
                    for k in ["saved_at", "kpis"]:
                        if k in st.session_state["broiler_farm_data"]:
                            del st.session_state["broiler_farm_data"][k]
                    st.success("تم تحميل الدورة، قم بمراجعة البيانات واستخدم زر الحفظ إذا أردت التعديل.")
                    st.rerun()

# -----------------------------------------------------------------
# تبويب تعليقات المختصين (للمالك والمختص)
# -----------------------------------------------------------------
if st.session_state["user_role"] in ["owner", "specialist"]:
    # تبويب تعليقات المختصين يختلف رقمه حسب وجود تبويب الدجاج من عدمه
    if st.session_state["user_role"] == "owner":
        comments_tab_index = 7
    else:
        comments_tab_index = 6
    with tabs[comments_tab_index]:
        st.markdown('<div class="section-title">💬 قناة التواصل والتعليقات الفنية</div>', unsafe_allow_html=True)
        st.markdown("### 📝 دفتر الملاحظات الفنية المشتركة:")
        st.text_area("التعليقات الحالية:", value=st.session_state["shared_comments"], height=200, disabled=True)
        col_comment1, col_comment2 = st.columns([0.7, 0.3])
        with col_comment1: new_comment = st.text_input("✍️ أكتب تعليقك الفني هنا:")
        with col_comment2:
            if st.button("📌 حفظ ونشر التعليق", use_container_width=True):
                if new_comment.strip():
                    prefix = "• [توجيه الاختصاصي م. عبد القادر إسماعيل تاور]" if st.session_state["user_role"] == "owner" else "• [ملاحظة مختص]"
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.session_state["shared_comments"] += f"{prefix} ({timestamp}): {new_comment.strip()}\n"
                    st.success("تمت إضافة الملاحظة بنجاح!")
                    time.sleep(0.5)
                    st.rerun()

# -----------------------------------------------------------------
# تبويب دليل المستخدم (آخر تبويب)
# -----------------------------------------------------------------
if st.session_state["user_role"] == "owner":
    guide_tab_index = 8
elif st.session_state["user_role"] == "specialist":
    guide_tab_index = 7
else:
    guide_tab_index = 2

with tabs[guide_tab_index]:
    st.markdown('<div class="section-title">📖 كتيب دليل المستخدم والتقانة الفنية</div>', unsafe_allow_html=True)
    col_guide, col_actions = st.columns([0.65, 0.35])
    with col_guide:
        st.markdown("""<div class="manual-book"><div style="text-align: center; border-bottom: 2px double #2c3e50; padding-bottom: 15px; margin-bottom: 20px;"><h2 style="color: #2e7d32; margin: 0;">📖 الكتيب الرقمي الذكي لإدارة وتشغيل المنصة</h2><p style="color: #7f8c8d; font-style: italic; margin: 5px 0 0 0;">إصدار هندسي محدث بأحدث تقنيات العرض لعام 2026</p><p style="color: #2c3e50; font-weight: bold; margin: 5px 0 0 0;">المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور</p></div>
        <div class="book-chapter">📌 الرؤية التقنية والهندسية للمنصة</div><div class="book-body">تعتمد <b>منصة تاور العلمية</b> على معايير التغذية الدقيقة المعتمدة عالمياً. يتم صياغة قيود الاستمثال الخطي عبر مكتبة <code>SciPy</code> بالاعتماد على <b>البروتين المهضوم الحقيقي (Digestible Protein)</b> كحاصل ضرب نسبة البروتين الخام في معامل الهضم العضوي لكل خامة، بالتكامل مع قيود <b>معادل النشاء (Starch Equivalent)</b> لتقييم كفاءة طاقة العلف.</div>
        <div class="book-chapter">📌 خارطة المكونات (Ingredients Matrix)</div><div class="book-body">تم تصنيف المواد العلفية داخل المنصة بمرونة تامة لتشمل:<br>1. <b>الحبوب ومصادر الطاقة:</b> الذرة البيضاء وسورجم الفتريتة.<br>2. <b>الأكساب والبروتينات:</b> كسب زهرة الشمس، كسب فول الصويا.<br>3. <b>الإضافات والأملاح:</b> بريمكسات، أحماض أمينية نقية.</div>
        <div class="book-chapter">📌 القطاعات الإنتاجية المتخصصة</div><div class="book-body">• <b>قطاع الأغنام والماعز:</b> فصل برمجي ذكي بين الذكور والإناث.<br>• <b>قطاع الدواجن:</b> دواجن التسمين، البياض، والسمان.<br>• <b>قطاع المجترات:</b> تسمين لحوم أو غزارة إدرار الألبان.<br>• <b>قطاع الخيول:</b> طاقة الجري أو أمهار نامية.</div>
        <div class="book-chapter">📌 إدارة مزارع الدجاج اللاحم (خاص بالمالك)</div><div class="book-body">• تسجيل بيانات الدورة اليومية (العمر، العدد، الأوزان، الاستهلاك، النافق، المستبعدين، الظروف البيئية).<br>• حساب تلقائي لمؤشرات ADG، FCR، EPEF، ونسب النفوق والاستبعاد.<br>• جدول الحرارة والرطوبة المرجعي حسب العمر.<br>• تقرير يومي شامل يمكن مشاركته عبر واتساب.<br>• حفظ تاريخ الدورات السابقة (حتى 10 دورات).</div>
        <div class="book-chapter">📌 خطوات تشغيل المنصة</div><div class="book-body"><b>الخطوة 1:</b> حدد القطاع والنوع الإنتاجي.<br><b>الخطوة 2:</b> اختر الخامات المتوفرة وأسعار السوق.<br><b>الخطوة 3:</b> اضغط على زر التشغيل للحصول على الخلطة المثلى.<br><b>الخطوة 4:</b> استعرض التقرير وقم بطباعة الديباجة أو تصدير PDF.<br><b>الخطوة 5 (للمالك):</b> استخدم تبويب إدارة الدجاج اللاحم لتسجيل ومتابعة أداء دورات التسمين.</div></div>""", unsafe_allow_html=True)
    with col_actions:
        st.markdown("### 💬 قنوات التفاعل والاستشارات:")
        st.link_button("📝 إرسال تعليق أو استشارة (نموذج جوجل)", GOOGLE_FORM_URL, use_container_width=True)
        welcome_msg = "السلام عليكم م. عبد القادر، أود الحصول على استشارة فنية بخصوص تركيب الأعلاف وحساب العلائق..."
        encoded_msg = urllib.parse.quote(welcome_msg)
        whatsapp_link = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_msg}"
        st.link_button("💬 تواصل واستشارة عبر الواتساب", whatsapp_link, use_container_width=True)
        st.markdown("<br><b>📢 انشر البرنامج وشارك المعرفة:</b>", unsafe_allow_html=True)
        share_text_base = "أستخدم الآن منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف لحساب العلائق بأقل تكلفة ودقة علمية عالية، تحت إشراف م. عبد القادر إسماعيل تاور. كما تتضمن إدارة متقدمة لمزارع الدجاج اللاحم."
        encoded_share_text = urllib.parse.quote(share_text_base)
        col_wa, col_fb = st.columns(2)
        with col_wa: st.link_button("🟢 واتساب", f"https://wa.me/?text={encoded_share_text}", use_container_width=True)
        with col_fb: st.link_button("🔵 فيسبوك", f"https://www.facebook.com/sharer/sharer.php?u=https://yourplatform.com&quote={encoded_share_text}", use_container_width=True)

# أرشفة السورس كود للمالك فقط
if st.session_state["user_role"] == "owner":
    st.markdown("<br><hr style='border-top: 1px dashed #2e7d32;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #1565C0; text-align:right;'>📨 أرشفة شفرة المصدر البرمجية</h3>", unsafe_allow_html=True)
    col_mail_info, col_btn = st.columns([0.7, 0.3])
    with col_mail_info:
        st.info(f"🔒 حماية الخصوصية نشطة: سيتم إرسال ملف الكود مباشرة إلى البريد الشخصي للمالك: ({OWNER_EMAIL})")
    with col_btn:
        if st.button("إرسال نسخة الكود للمالك 🚀", use_container_width=True, type="secondary"):
            with st.spinner("جاري تأمين الاتصال السحابي وإرسال السورس كود..."):
                if send_code_to_mail(OWNER_EMAIL):
                    st.success(f"📥 تم إرسال السورس كود المحدث بأمان كملف (.py) إلى بريدك الهندسي.")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("""<div class="mini-left-signature">👨‍🔬 الاختصاصي م. عبد القادر إسماعيل تاور © 2026 | منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</div>""", unsafe_allow_html=True)
