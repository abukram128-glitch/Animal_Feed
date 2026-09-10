# ============================================================================
# تاور نولجي Tawornology العلمية — الإصدار المتكامل الشامل 17.1
# ============================================================================
# 🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله
# 🕊️ اللهم اجعل قبرهما روضة من رياض الجنة واجمعنا بهما في الفردوس الأعلى
# ============================================================================
# الميزات:
# ✅ محرك الاستمثال الخطي (Least-Cost Formulation)
# ✅ المختبر الذكي OCR (تحليل صور التركيبات)
# ✅ معادلات NRC للألبان والتسمين
# ✅ إدارة المزارع بحفظ دائم SQLite
# ✅ بدائل الحليب + مواقيت الصلاة + منبه الجرعات
# ✅ توليد PDF عربي احترافي (اسم المشرف أعلى + التوقيع أسفل)
# ✅ إرسال الكود للبريد (مع App Password)
# ✅ تقييد التركيبة بـ 75% من المعايير
# ✅ 14 تبويب متكامل — الزوار يحصلون على 5 فقط
# ✅ تصميم تجميلي متقدم
# المشرف: الاختصاصي م. عبد القادر إسماعيل تاور — اختصاصي تغذية الحيوان
# ============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import json, os, base64, smtplib, time, urllib.parse, hashlib, secrets, io
import sqlite3, warnings, re, math, random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scipy.optimize import linprog
from sklearn.linear_model import LinearRegression
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Tuple, Optional

warnings.filterwarnings('ignore')

# ===== PDF واللغة العربية =====
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import arabic_reshaper
from bidi.algorithm import get_display
import qrcode
from PIL import Image as PILImage
import matplotlib.pyplot as plt

# ===== الصوت =====
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# ===== OCR =====
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

# =====================================================================
# إعدادات الصفحة
# =====================================================================
st.set_page_config(
    page_title="تاور نولجي Tawornology العلمية",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================================
# أكواد الدخول (المالك فقط + الزوار)
# =====================================================================
CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور — اختصاصي تغذية الحيوان", "level": 3},
    "2020":   {"role": "owner", "name": "المختص والزملاء", "level": 3},
}

OWNER_EMAIL = "abukram128@gmail.com"
SENDER_EMAIL = "abukram128@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
WHATSAPP_NUMBER = "+249123533489"

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

@st.cache_data(ttl=3600)
def get_image_base64(paths):
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                pass
    return None

img_base64 = get_image_base64(PHOTO_OPTIONS)

# =====================================================================
# معالج النص العربي
# =====================================================================
class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=2000)
    def fix_arabic_text(text):
        if not text:
            return ""
        try:
            reshaped = arabic_reshaper.reshape(str(text))
            return get_display(reshaped)
        except Exception:
            return str(text)

arabic_processor = ArabicTextProcessor()

# =====================================================================
# قاعدة البيانات
# =====================================================================
class DatabaseManager:
    def __init__(self, db_path="tawornology_v17.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        tables = [
            '''CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, role TEXT, full_name TEXT, email TEXT, phone TEXT, specialty TEXT, experience_years INTEGER, created_date TEXT, last_login TEXT, is_active INTEGER DEFAULT 1, is_public INTEGER DEFAULT 0)''',
            '''CREATE TABLE IF NOT EXISTS farms (farm_id TEXT PRIMARY KEY, farm_name TEXT UNIQUE, farm_type TEXT, owner_name TEXT, owner_phone TEXT, location TEXT, area REAL, created_date TEXT, last_updated TEXT)''',
            '''CREATE TABLE IF NOT EXISTS production_cycles (cycle_id TEXT PRIMARY KEY, farm_id TEXT, cycle_type TEXT, start_date TEXT, end_date TEXT, initial_count INTEGER, breed TEXT, target_weight REAL, target_age INTEGER, status TEXT, notes TEXT)''',
            '''CREATE TABLE IF NOT EXISTS daily_records (record_id TEXT PRIMARY KEY, cycle_id TEXT, record_date TEXT, age_days INTEGER, live_birds INTEGER, avg_weight REAL, feed_consumed REAL, dead_count INTEGER, culled_count INTEGER, temperature REAL, humidity REAL, feed_conversion REAL, mortality_rate REAL, notes TEXT)''',
            '''CREATE TABLE IF NOT EXISTS health_records (health_id TEXT PRIMARY KEY, cycle_id TEXT, record_date TEXT, age_days INTEGER, treatment_type TEXT, treatment_name TEXT, dose REAL, dose_unit TEXT, administration_route TEXT, notes TEXT)''',
            '''CREATE TABLE IF NOT EXISTS feed_formulas (formula_id TEXT PRIMARY KEY, formula_name TEXT, animal_type TEXT, breed TEXT, stage TEXT, target_dp REAL, target_se REAL, ingredients TEXT, total_cost REAL, created_by TEXT, created_date TEXT, requester_name TEXT)''',
            '''CREATE TABLE IF NOT EXISTS quality_analysis (analysis_id TEXT PRIMARY KEY, sample_name TEXT, analysis_date TEXT, moisture REAL, protein REAL, fat REAL, fiber REAL, ash REAL, se REAL, dc REAL, ndf REAL, adf REAL, notes TEXT, performed_by TEXT)''',
            '''CREATE TABLE IF NOT EXISTS milk_replacers (replacer_id TEXT PRIMARY KEY, animal_type TEXT, age_days INTEGER, formula_name TEXT, ingredients TEXT, instructions TEXT, created_by TEXT, created_date TEXT)''',
            '''CREATE TABLE IF NOT EXISTS dose_reminders (reminder_id TEXT PRIMARY KEY, animal_type TEXT, dose_type TEXT, dose_name TEXT, dose_amount REAL, dose_unit TEXT, administration_route TEXT, frequency_days INTEGER, start_date TEXT, next_dose_date TEXT, notes TEXT, active BOOLEAN DEFAULT 1)''',
        ]
        for t in tables:
            c.execute(t)
        conn.commit()
        conn.close()
    
    def execute_query(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        result = c.execute(query, params)
        conn.commit()
        data = result.fetchall()
        conn.close()
        return data
    
    def insert_record(self, table, data):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            c.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", list(data.values()))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_records(self, table, conditions=None):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            if conditions:
                where = ' AND '.join([f"{k}=?" for k in conditions.keys()])
                result = c.execute(f"SELECT * FROM {table} WHERE {where}", list(conditions.values()))
            else:
                result = c.execute(f"SELECT * FROM {table}")
            data = result.fetchall()
            conn.close()
            return data
        except Exception:
            return []

# =====================================================================
# نظام الصوت (متسلسل بدون ازدواجية)
# =====================================================================
@st.cache_data(ttl=3600)
def text_to_speech_base64(text, lang="ar"):
    if not GTTS_AVAILABLE or not text:
        return None
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return base64.b64encode(audio_bytes.read()).decode()
    except Exception:
        return None

def play_audio_b64(audio_b64):
    if audio_b64:
        st.components.v1.html(
            f'<audio autoplay><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mpeg"></audio>',
            height=0
        )
        return True
    return False

def voice_guide_sequential(messages, lang="ar", delay_between=2.0):
    if not GTTS_AVAILABLE:
        return
    for i, msg in enumerate(messages):
        if msg:
            audio_b64 = text_to_speech_base64(msg, lang)
            if audio_b64:
                play_audio_b64(audio_b64)
                duration = max(2.0, len(msg.split()) * 0.3 + 1.0)
                time.sleep(duration)
                if i < len(messages) - 1:
                    time.sleep(1.0)

def voice_guide(message, lang="ar"):
    if not GTTS_AVAILABLE or not message:
        return
    audio_b64 = text_to_speech_base64(message, lang)
    if audio_b64:
        play_audio_b64(audio_b64)

def voice_welcome(role):
    messages = {
        "owner": ["مرحباً بك، الاختصاصي م. عبد القادر إسماعيل تاور، اختصاصي تغذية الحيوان."],
        "public": ["مرحباً بك زائراً في تاور نولجي Tawornology العلمية."]
    }
    voice_guide_sequential(messages.get(role, ["مرحباً بك."]))

def play_welcome_audio():
    voice_guide_sequential([
        "السلام عليكم ورحمة الله وبركاته،",
        "مرحباً بكم في تاور نولجي Tawornology العلمية."
    ])

def play_dua_audio():
    voice_guide_sequential([
        "اللهم اغفر لإسماعيل تاور وابتسام،",
        "وارحمهما وأدخلهما فسيح جناتك."
    ])

def play_full_guide_audio():
    voice_guide_sequential([
        "مرحباً بك في منصة تاور نولجي Tawornology العلمية.",
        "هذه المنصة متخصصة في الانتاج الحيواني وتركيب الاعلاف.",
        "الأقسام: تركيب الأعلاف، المختبر الذكي، إدارة المزارع، بدائل الحليب، مواقيت الصلاة، منبه الجرعات، بورصة الأسعار، المستودعات، الإنتاج اليومي، المراجع العلمية.",
        "نسأل الله التوفيق والسداد."
    ], delay_between=2.5)

# =====================================================================
# إرسال الكود للبريد (مُصلح)
# =====================================================================
def send_code_to_email(receiver_email, password):
    if receiver_email.strip().lower() != OWNER_EMAIL.strip().lower():
        return False, f"❌ الإرسال مسموح فقط للبريد: {OWNER_EMAIL}"
    if not password or len(password.strip().replace(" ", "")) < 8:
        return False, "⚠️ يرجى إدخال كلمة مرور التطبيق (App Password) — 16 حرفاً"
    
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception:
        code_content = "# الكود قيد التشغيل مباشرة"
    
    file_hash = hashlib.md5(code_content.encode()).hexdigest()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود — تاور نولجي Tawornology v17.1"
    
    body = f"""السلام عليكم ورحمة الله وبركاته،

مرفق السورس كود الكامل لمنصة تاور نولجي Tawornology العلمية.

📅 التاريخ: {timestamp}
🔑 التوقيع الرقمي: {file_hash}
👨‍💻 المشرف: الاختصاصي م. عبد القادر إسماعيل تاور — اختصاصي تغذية الحيوان
🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام
📊 عدد الأسطر: {len(code_content.splitlines()):,}
📦 حجم الملف: {len(code_content) / 1024:.1f} KB

مع خالص التحية والتقدير،
تاور نولجي Tawornology العلمية © 2026
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    attachment = MIMEText(code_content, 'plain', 'utf-8')
    attachment.add_header('Content-Disposition', 'attachment',
                          filename="tawornology_v17.1.py")
    msg.attach(attachment)
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.starttls()
        server.login(SENDER_EMAIL, password.strip().replace(" ", ""))
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True, f"✅ تم إرسال الكود بنجاح إلى {receiver_email}"
    except smtplib.SMTPAuthenticationError:
        return False, "❌ فشل تسجيل الدخول — تحقق من كلمة مرور التطبيق"
    except Exception as e:
        return False, f"❌ خطأ: {str(e)}"

# =====================================================================
# تحميل الخط العربي
# =====================================================================
@st.cache_resource
def download_arabic_font():
    font_path = "Amiri-Regular.ttf"
    if os.path.exists(font_path):
        return font_path
    try:
        import requests
        url = "https://raw.githubusercontent.com/aliftype/amiri/master/fonts/Amiri-Regular.ttf"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            with open(font_path, "wb") as f:
                f.write(r.content)
            return font_path
    except Exception:
        pass
    for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "C:/Windows/Fonts/arial.ttf"]:
        if os.path.exists(f):
            return f
    return None

def ensure_arabic_font():
    fp = download_arabic_font()
    if fp and os.path.exists(fp):
        try:
            pdfmetrics.registerFont(TTFont('ArabicFont', fp))
            return 'ArabicFont'
        except Exception:
            pass
    return 'Helvetica'

# =====================================================================
# مولد PDF الاحترافي (اسم المشرف أعلى + التوقيع أسفل)
# =====================================================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = ensure_arabic_font()
        self.styles = self._create_styles()
    
    def _create_styles(self):
        return {
            'supervisor': ParagraphStyle('supervisor', fontName=self.font_name, fontSize=22,
                alignment=TA_CENTER, textColor=HexColor('#1a237e'), spaceAfter=8, leading=28),
            'title': ParagraphStyle('title', fontName=self.font_name, fontSize=26,
                alignment=TA_CENTER, textColor=HexColor('#1b5e20'), spaceAfter=20, leading=32),
            'subtitle': ParagraphStyle('subtitle', fontName=self.font_name, fontSize=16,
                alignment=TA_CENTER, textColor=HexColor('#2e7d32'), spaceAfter=15, leading=20),
            'heading': ParagraphStyle('heading', fontName=self.font_name, fontSize=14,
                alignment=TA_RIGHT, textColor=HexColor('#1b5e20'), spaceAfter=10, leading=18),
            'body': ParagraphStyle('body', fontName=self.font_name, fontSize=11,
                alignment=TA_RIGHT, textColor=HexColor('#333333'), spaceAfter=6, leading=16),
            'footer': ParagraphStyle('footer', fontName=self.font_name, fontSize=9,
                alignment=TA_CENTER, textColor=HexColor('#666666'), spaceAfter=0, leading=12),
            'signature': ParagraphStyle('signature', fontName=self.font_name, fontSize=16,
                alignment=TA_CENTER, textColor=HexColor('#1a237e'), spaceAfter=10, leading=22),
        }
    
    def _add_signature_block(self, story, user_name):
        story.append(Spacer(1, 35))
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#2e7d32'),
                                spaceBefore=10, spaceAfter=20))
        story.append(Paragraph(arabic_processor.fix_arabic_text("✍️ التوقيع الرسمي"),
                               self.styles['signature']))
        story.append(Spacer(1, 15))
        sig_data = [
            [arabic_processor.fix_arabic_text("الاسم:"), arabic_processor.fix_arabic_text(user_name)],
            [arabic_processor.fix_arabic_text("الصفة:"), arabic_processor.fix_arabic_text("اختصاصي تغذية الحيوان")],
            [arabic_processor.fix_arabic_text("المؤسسة:"), arabic_processor.fix_arabic_text("تاور نولجي Tawornology العلمية")],
            [arabic_processor.fix_arabic_text("التاريخ:"), arabic_processor.fix_arabic_text(datetime.now().strftime("%Y-%m-%d"))],
        ]
        sig_table = Table(sig_data, colWidths=[150, 350])
        sig_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), HexColor('#e8f5e9')),
            ('BACKGROUND', (1,0), (1,-1), HexColor('#ffffff')),
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#2e7d32')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(sig_table)
        story.append(Spacer(1, 20))
        story.append(Paragraph(arabic_processor.fix_arabic_text("🔏 تم إعداد هذا التقرير وتوقيعه إلكترونياً"),
                               self.styles['footer']))
        story.append(Spacer(1, 8))
        story.append(Paragraph(arabic_processor.fix_arabic_text("🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله"),
                               self.styles['footer']))
    
    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city,
                                      local_cost, local_sym, computed_se, user_name,
                                      requester_name="", standard=None,
                                      include_charts=True, extra_info=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50,
                                topMargin=50, bottomMargin=50)
        story = []
        
        def p(text, style='body'):
            return Paragraph(arabic_processor.fix_arabic_text(str(text)),
                             self.styles.get(style, self.styles['body']))
        
        # === ترويسة باسم المشرف ===
        story.append(p("الاختصاصي م. عبد القادر إسماعيل تاور", 'supervisor'))
        story.append(p("اختصاصي تغذية الحيوان", 'subtitle'))
        story.append(HRFlowable(width="100%", thickness=3, color=HexColor('#1b5e20'),
                                spaceBefore=8, spaceAfter=15))
        story.append(p("🌾 تاور نولجي Tawornology العلمية", 'title'))
        story.append(p("📄 تقرير فني شامل — تقرير التركيب العلفي", 'subtitle'))
        story.append(Spacer(1, 15))
        
        info_data = [
            [arabic_processor.fix_arabic_text("📌 الموقع"), arabic_processor.fix_arabic_text(city)],
            [arabic_processor.fix_arabic_text("🐾 الفصيل"), arabic_processor.fix_arabic_text(breed)],
            [arabic_processor.fix_arabic_text("👤 طالب العلف"), arabic_processor.fix_arabic_text(requester_name or "غير محدد")],
            [arabic_processor.fix_arabic_text("📅 تاريخ الإصدار"), arabic_processor.fix_arabic_text(datetime.now().strftime("%Y-%m-%d %H:%M"))],
        ]
        info_table = Table(info_data, colWidths=[180, 320])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), HexColor('#e8f5e9')),
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#c8e6c9')),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        story.append(p("📊 النتائج الرئيسية:", 'heading'))
        tdata = [
            [arabic_processor.fix_arabic_text('المعيار'), arabic_processor.fix_arabic_text('القيمة')],
            [arabic_processor.fix_arabic_text('البروتين المهضوم (DP)'), arabic_processor.fix_arabic_text(f'{target_dp:.2f}%')],
            [arabic_processor.fix_arabic_text('معادل النشاء (SE)'), arabic_processor.fix_arabic_text(f'{computed_se:.2f}')],
            [arabic_processor.fix_arabic_text('التكلفة للطن'), arabic_processor.fix_arabic_text(f'${cost:.2f} ({local_cost:,.2f} {local_sym})')]
        ]
        t = Table(tdata, colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#2e7d32')),
            ('BACKGROUND', (0,1), (-1,-1), HexColor('#f5f5f5')),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(t)
        
        if standard:
            story.append(Spacer(1, 15))
            story.append(p("📏 المقارنة مع المعايير القياسية:", 'heading'))
            comp_data = [[
                arabic_processor.fix_arabic_text('المقياس'),
                arabic_processor.fix_arabic_text('المحسوب'),
                arabic_processor.fix_arabic_text('القياسي'),
                arabic_processor.fix_arabic_text('الانحراف %'),
                arabic_processor.fix_arabic_text('التقييم')
            ]]
            if 'DP' in standard:
                dev = ((target_dp - standard['DP']) / standard['DP']) * 100 if standard['DP'] > 0 else 0
                grade = "✅ ممتاز" if abs(dev) <= 5 else ("⚠️ جيد" if abs(dev) <= 10 else "❌ ضعيف")
                comp_data.append([arabic_processor.fix_arabic_text('DP'),
                                  arabic_processor.fix_arabic_text(f"{target_dp:.2f}%"),
                                  arabic_processor.fix_arabic_text(f"{standard['DP']:.2f}%"),
                                  arabic_processor.fix_arabic_text(f"{dev:.1f}"),
                                  arabic_processor.fix_arabic_text(grade)])
            if 'SE' in standard:
                dev = ((computed_se - standard['SE']) / standard['SE']) * 100 if standard['SE'] > 0 else 0
                grade = "✅ ممتاز" if abs(dev) <= 5 else ("⚠️ جيد" if abs(dev) <= 10 else "❌ ضعيف")
                comp_data.append([arabic_processor.fix_arabic_text('SE'),
                                  arabic_processor.fix_arabic_text(f"{computed_se:.2f}"),
                                  arabic_processor.fix_arabic_text(f"{standard['SE']:.2f}"),
                                  arabic_processor.fix_arabic_text(f"{dev:.1f}"),
                                  arabic_processor.fix_arabic_text(grade)])
            t_comp = Table(comp_data, colWidths=[80, 100, 100, 100, 120])
            t_comp.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
                ('TEXTCOLOR', (0,0), (-1,0), white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,-1), self.font_name),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
            ]))
            story.append(t_comp)
            
            # رسم بياني للمقارنة
            try:
                fig, ax = plt.subplots(figsize=(7, 3.5))
                metrics, calc_vals, std_vals = [], [], []
                if 'DP' in standard:
                    metrics.append('DP'); calc_vals.append(target_dp); std_vals.append(standard['DP'])
                if 'SE' in standard:
                    metrics.append('SE'); calc_vals.append(computed_se); std_vals.append(standard['SE'])
                x = np.arange(len(metrics))
                width = 0.35
                b1 = ax.bar(x - width/2, calc_vals, width, label='المحسوب', color='#2e7d32')
                b2 = ax.bar(x + width/2, std_vals, width, label='القياسي', color='#1565C0')
                for bars in [b1, b2]:
                    for bar in bars:
                        h = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2, h, f'{h:.1f}',
                               ha='center', va='bottom', fontsize=9, fontweight='bold')
                ax.set_xticks(x)
                ax.set_xticklabels(metrics)
                ax.set_title('المقارنة مع المعايير القياسية')
                ax.legend()
                ax.grid(axis='y', linestyle='--', alpha=0.5)
                buf_chart = io.BytesIO()
                plt.tight_layout()
                plt.savefig(buf_chart, format='png', dpi=120, bbox_inches='tight')
                plt.close()
                buf_chart.seek(0)
                story.append(Spacer(1, 10))
                story.append(Image(buf_chart, width=450, height=225))
            except Exception:
                pass
        
        # الصفحة الثانية: المكونات
        story.append(PageBreak())
        story.append(p("📋 المقادير المعتمدة لتركيب الطن الواحد:", 'heading'))
        story.append(Spacer(1, 10))
        ing_data = [[
            arabic_processor.fix_arabic_text('المكون'),
            arabic_processor.fix_arabic_text('النسبة %'),
            arabic_processor.fix_arabic_text('كجم/طن')
        ]]
        for ing, pct in formula.items():
            ing_data.append([
                arabic_processor.fix_arabic_text(ing),
                arabic_processor.fix_arabic_text(f'{pct:.2f}%'),
                arabic_processor.fix_arabic_text(f'{pct*10:.1f}')
            ])
        t2 = Table(ing_data, colWidths=[250, 120, 120])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')]),
        ]))
        story.append(t2)
        
        if include_charts and len(formula) > 1:
            try:
                fig, ax = plt.subplots(figsize=(6, 4))
                names = list(formula.keys())
                vals = list(formula.values())
                colors = ['#1b5e20','#2e7d32','#388e3c','#43a047','#4caf50','#66bb6a','#81c784']
                wedges, _, _ = ax.pie(vals, labels=None, autopct='%1.1f%%',
                                       colors=colors[:len(names)], startangle=90)
                ax.legend(wedges, [arabic_processor.fix_arabic_text(n) for n in names],
                         title=arabic_processor.fix_arabic_text("المكونات"),
                         loc='center left', bbox_to_anchor=(1,0,0.5,1), fontsize=9)
                ax.set_title(arabic_processor.fix_arabic_text('توزيع المكونات'), fontsize=13)
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=130, bbox_inches='tight')
                plt.close()
                buf.seek(0)
                story.append(Spacer(1, 15))
                story.append(Image(buf, width=440, height=290))
            except Exception:
                pass
        
        story.append(Spacer(1, 15))
        story.append(p("📌 التوصيات الفنية:", 'heading'))
        for rec in [
            "• يوصى بإضافة الإنزيمات لتحسين الهضم.",
            "• يجب مراقبة جودة المواد الخام بشكل دوري.",
            "• يجب تخزين العلف في مكان جاف بعيداً عن الرطوبة."
        ]:
            story.append(p(rec))
        
        if extra_info:
            story.append(Spacer(1, 12))
            story.append(p("معلومات إضافية:", 'heading'))
            for k, v in extra_info.items():
                if v:
                    story.append(p(f"• {k}: {v}"))
        
        # التوقيع في نهاية التقرير
        self._add_signature_block(story, user_name)
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_lab_report(self, analysis_results, animal_type, stage, user_name,
                            standard=None, evaluation=None):
        """تقرير المختبر مع رسوم بيانية للمقارنة"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40,
                                topMargin=40, bottomMargin=40)
        story = []
        
        def p(text, style='body'):
            return Paragraph(arabic_processor.fix_arabic_text(str(text)),
                             self.styles.get(style, self.styles['body']))
        
        story.append(p("الاختصاصي م. عبد القادر إسماعيل تاور", 'supervisor'))
        story.append(p("اختصاصي تغذية الحيوان", 'subtitle'))
        story.append(HRFlowable(width="100%", thickness=3, color=HexColor('#1565C0'),
                                spaceBefore=8, spaceAfter=15))
        story.append(p("🔬 تقرير التحليل المخبري المتقدم", 'title'))
        story.append(p("تاور نولجي Tawornology العلمية", 'subtitle'))
        story.append(Spacer(1, 15))
        story.append(p(f"🐾 الحيوان: {animal_type} | المرحلة: {stage}"))
        story.append(p(f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}"))
        story.append(Spacer(1, 15))
        
        if analysis_results:
            story.append(p("📊 النتائج المحسوبة:", 'heading'))
            res_data = [
                [arabic_processor.fix_arabic_text('العنصر'), arabic_processor.fix_arabic_text('القيمة')],
                [arabic_processor.fix_arabic_text('البروتين الخام (CP)'),
                 arabic_processor.fix_arabic_text(f"{analysis_results.get('cp', 0):.2f}%")],
                [arabic_processor.fix_arabic_text('البروتين المهضوم (DP)'),
                 arabic_processor.fix_arabic_text(f"{analysis_results.get('dp', 0):.2f}%")],
                [arabic_processor.fix_arabic_text('معادل النشاء (SE)'),
                 arabic_processor.fix_arabic_text(f"{analysis_results.get('se', 0):.2f}")]
            ]
            t = Table(res_data, colWidths=[250, 250])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), HexColor('#1565C0')),
                ('TEXTCOLOR', (0,0), (-1,0), white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,-1), self.font_name),
                ('FONTSIZE', (0,0), (-1,-1), 12),
                ('GRID', (0,0), (-1,-1), 1, HexColor('#1565C0')),
            ]))
            story.append(t)
            story.append(Spacer(1, 20))
            
            if standard:
                story.append(p("📏 المقارنة مع المعايير القياسية:", 'heading'))
                dp_val = analysis_results.get('dp', 0)
                se_val = analysis_results.get('se', 0)
                cp_val = analysis_results.get('cp', 0)
                
                comp_data = [[
                    arabic_processor.fix_arabic_text('المقياس'),
                    arabic_processor.fix_arabic_text('المحسوب'),
                    arabic_processor.fix_arabic_text('القياسي'),
                    arabic_processor.fix_arabic_text('الانحراف %'),
                    arabic_processor.fix_arabic_text('التقييم')
                ]]
                if 'DP' in standard:
                    dev = ((dp_val - standard['DP']) / standard['DP']) * 100 if standard['DP'] > 0 else 0
                    grade = "✅ ممتاز" if abs(dev) <= 5 else ("⚠️ جيد" if abs(dev) <= 10 else "❌ ضعيف")
                    comp_data.append([arabic_processor.fix_arabic_text('DP'),
                                      arabic_processor.fix_arabic_text(f"{dp_val:.2f}%"),
                                      arabic_processor.fix_arabic_text(f"{standard['DP']:.2f}%"),
                                      arabic_processor.fix_arabic_text(f"{dev:.1f}"),
                                      arabic_processor.fix_arabic_text(grade)])
                if 'SE' in standard:
                    dev = ((se_val - standard['SE']) / standard['SE']) * 100 if standard['SE'] > 0 else 0
                    grade = "✅ ممتاز" if abs(dev) <= 5 else ("⚠️ جيد" if abs(dev) <= 10 else "❌ ضعيف")
                    comp_data.append([arabic_processor.fix_arabic_text('SE'),
                                      arabic_processor.fix_arabic_text(f"{se_val:.2f}"),
                                      arabic_processor.fix_arabic_text(f"{standard['SE']:.2f}"),
                                      arabic_processor.fix_arabic_text(f"{dev:.1f}"),
                                      arabic_processor.fix_arabic_text(grade)])
                if 'CP' in standard:
                    dev = ((cp_val - standard['CP']) / standard['CP']) * 100 if standard['CP'] > 0 else 0
                    grade = "✅ ممتاز" if abs(dev) <= 5 else ("⚠️ جيد" if abs(dev) <= 10 else "❌ ضعيف")
                    comp_data.append([arabic_processor.fix_arabic_text('CP'),
                                      arabic_processor.fix_arabic_text(f"{cp_val:.2f}%"),
                                      arabic_processor.fix_arabic_text(f"{standard['CP']:.2f}%"),
                                      arabic_processor.fix_arabic_text(f"{dev:.1f}"),
                                      arabic_processor.fix_arabic_text(grade)])
                t_comp = Table(comp_data, colWidths=[80, 100, 100, 100, 120])
                t_comp.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
                    ('TEXTCOLOR', (0,0), (-1,0), white),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,-1), self.font_name),
                    ('FONTSIZE', (0,0), (-1,-1), 10),
                    ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
                ]))
                story.append(t_comp)
                story.append(Spacer(1, 15))
                
                # رسم بياني للمقارنة
                try:
                    fig, ax = plt.subplots(figsize=(7, 4))
                    metrics, calc_vals, std_vals = [], [], []
                    if 'DP' in standard:
                        metrics.append('DP (%)'); calc_vals.append(dp_val); std_vals.append(standard['DP'])
                    if 'SE' in standard:
                        metrics.append('SE'); calc_vals.append(se_val); std_vals.append(standard['SE'])
                    if 'CP' in standard:
                        metrics.append('CP (%)'); calc_vals.append(cp_val); std_vals.append(standard['CP'])
                    
                    x = np.arange(len(metrics))
                    width = 0.35
                    b1 = ax.bar(x - width/2, calc_vals, width, label='المحسوب',
                                color='#2e7d32', edgecolor='#1b5e20', linewidth=1.5)
                    b2 = ax.bar(x + width/2, std_vals, width, label='القياسي',
                                color='#1565C0', edgecolor='#0d47a1', linewidth=1.5)
                    for bars in [b1, b2]:
                        for bar in bars:
                            h = bar.get_height()
                            ax.text(bar.get_x() + bar.get_width()/2, h, f'{h:.1f}',
                                   ha='center', va='bottom', fontsize=9, fontweight='bold')
                    ax.set_xticks(x)
                    ax.set_xticklabels(metrics)
                    ax.set_title('مقارنة النتائج المحسوبة مع المعايير القياسية', fontsize=12)
                    ax.legend()
                    ax.grid(axis='y', linestyle='--', alpha=0.5)
                    ax.set_facecolor('#f8f9fa')
                    buf_chart = io.BytesIO()
                    plt.tight_layout()
                    plt.savefig(buf_chart, format='png', dpi=130, bbox_inches='tight')
                    plt.close()
                    buf_chart.seek(0)
                    story.append(Image(buf_chart, width=480, height=270))
                except Exception:
                    pass
        
        self._add_signature_block(story, user_name)
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_milk_replacer_report(self, formula, animal_type, age_days, instructions, user_name):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50,
                                topMargin=50, bottomMargin=50)
        story = []
        
        def p(text, style='body'):
            return Paragraph(arabic_processor.fix_arabic_text(str(text)),
                             self.styles.get(style, self.styles['body']))
        
        story.append(p("الاختصاصي م. عبد القادر إسماعيل تاور", 'supervisor'))
        story.append(p("اختصاصي تغذية الحيوان", 'subtitle'))
        story.append(HRFlowable(width="100%", thickness=3, color=HexColor('#1b5e20'),
                                spaceBefore=8, spaceAfter=15))
        story.append(p("🍼 تقرير تركيب بديل الحليب", 'title'))
        story.append(p("تاور نولجي Tawornology العلمية", 'subtitle'))
        story.append(Spacer(1, 15))
        story.append(p(f"🐾 الحيوان: {animal_type} | العمر: {age_days} يوم"))
        story.append(p(f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}"))
        story.append(Spacer(1, 15))
        story.append(p("📋 مكونات بديل الحليب:", 'heading'))
        
        ing_data = [[
            arabic_processor.fix_arabic_text('المكون'),
            arabic_processor.fix_arabic_text('النسبة %'),
            arabic_processor.fix_arabic_text('جم/لتر')
        ]]
        for ing, pct in formula.items():
            ing_data.append([
                arabic_processor.fix_arabic_text(ing),
                arabic_processor.fix_arabic_text(f'{pct:.2f}%'),
                arabic_processor.fix_arabic_text(f'{pct*10:.1f}')
            ])
        t = Table(ing_data, colWidths=[220, 130, 130])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font_name),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd'))
        ]))
        story.append(t)
        story.append(Spacer(1, 15))
        story.append(p("📌 تعليمات التقديم:", 'heading'))
        for line in instructions.split('\n'):
            if line.strip():
                story.append(p(f"• {line.strip()}"))
        
        self._add_signature_block(story, user_name)
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

pdf_generator = ProfessionalPDFGenerator()

print("✅ الجزء 1/3 تم التحميل - الإعدادات + قاعدة البيانات + PDF")
# =====================================================================
# مكتبة الأعلاف الشاملة
# =====================================================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6},
        "جريش أرز رزاز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2},
        "دخن محلي غزير": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0},
        "تفل العنب المجفف": {"CP": 12.0, "DC": 0.50, "SE": 45.0, "NDF": 45.0, "ADF": 30.0, "EE": 5.0, "ASH": 8.0},
        "نخالة الأرز الدهنية": {"CP": 12.5, "DC": 0.70, "SE": 55.0, "NDF": 30.0, "ADF": 15.0, "EE": 15.0, "ASH": 8.0},
        "علف الشعير المستنبت": {"CP": 15.0, "DC": 0.75, "SE": 60.0, "NDF": 25.0, "ADF": 12.0, "EE": 3.0, "ASH": 5.0}
    },
    "🌱 الأكساب والبروتين": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5},
        "كسب بذرة القطن غير المقشور": {"CP": 35.0, "DC": 0.70, "SE": 48.0, "NDF": 35.0, "ADF": 22.0, "EE": 2.0, "ASH": 7.0},
        "كسب بذور اللفت (كانولا)": {"CP": 38.0, "DC": 0.82, "SE": 62.0, "NDF": 28.0, "ADF": 18.0, "EE": 3.5, "ASH": 7.5},
        "كسب زهرة الشمس الكامل": {"CP": 30.0, "DC": 0.74, "SE": 40.0, "NDF": 42.0, "ADF": 28.0, "EE": 3.0, "ASH": 6.0}
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5},
        "مخلفات مصانع البسكويت": {"CP": 10.0, "DC": 0.80, "SE": 65.0, "NDF": 8.0, "ADF": 4.0, "EE": 12.0, "ASH": 3.0},
        "قش الأرز المعالج": {"CP": 4.0, "DC": 0.40, "SE": 25.0, "NDF": 65.0, "ADF": 40.0, "EE": 1.5, "ASH": 12.0}
    },
    "🧬 البروتين الحيواني": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق أسماك فاخر (72%)": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5},
        "بروتين مصل الحليب (WPC)": {"CP": 80.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 3.0, "ASH": 3.0},
        "بروتين الدم المجفف": {"CP": 85.0, "DC": 0.92, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.5, "ASH": 5.0}
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3},
        "ثريونين نقي (L-Threonine)": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2},
        "تريبتوفان نقي (L-Tryptophan)": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1},
        "فالين نقي (L-Valine)": {"CP": 90.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1}
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس بياض وبشاير": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
        "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0},
        "كبريتات الحديدوز (معادل الجوسيبول)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.0},
        "مستخلص الخمائر والجدر الخلوية (MOS)": {"CP": 12.0, "DC": 0.50, "SE": 10.0, "NDF": 2.5, "ADF": 1.5, "EE": 1.5, "ASH": 8.5},
        "خميرة الخبز (Yeast)": {"CP": 45.0, "DC": 0.85, "SE": 35.0, "NDF": 5.0, "ADF": 2.0, "EE": 2.5, "ASH": 7.0}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
        "أكسيد المغنيسيوم العلفي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "يوريا علفية محصنة (المجترات فقط)": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0},
        "كلوريد الكولين (Choline Chloride)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 75.0}
    },
    "🍼 مكونات بدائل الحليب": {
        "مصل الحليب المجفف (Whey)": {"CP": 12.0, "DC": 0.95, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.0},
        "حليب مجفف خالي الدسم": {"CP": 34.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.5},
        "دهن نباتي (زيت نباتي)": {"CP": 0.0, "DC": 0.0, "SE": 10.0, "NDF": 0.0, "ADF": 0.0, "EE": 99.0, "ASH": 0.0},
        "ليسيثين الصويا": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 95.0, "ASH": 0.5},
        "فيتامينات ومعادن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بروتين الصويا المركز": {"CP": 65.0, "DC": 0.90, "SE": 30.0, "NDF": 2.0, "ADF": 1.0, "EE": 1.0, "ASH": 5.5}
    }
}

FLAT_FEED_DB = {}
for category, items in BIG_FEEDS_LIBRARY.items():
    for feed_name, nutrition in items.items():
        FLAT_FEED_DB[feed_name] = nutrition

# =====================================================================
# المعايير القياسية
# =====================================================================
STANDARD_VALUES = {
    "أبقار": {
        "تسمين عجول": {"DP": 12.0, "SE": 68.0, "CP": 15.0},
        "حليب/إدرار": {"DP": 14.0, "SE": 70.0, "CP": 17.5},
        "حمل/دفع غذائي": {"DP": 11.0, "SE": 65.0, "CP": 13.8},
        "صيانة": {"DP": 9.0, "SE": 60.0, "CP": 11.3},
        "تسمين مكثف": {"DP": 13.0, "SE": 72.0, "CP": 16.3}
    },
    "أغنام": {
        "تسمين حملان": {"DP": 13.0, "SE": 66.0, "CP": 16.3},
        "نعاج مرضعات": {"DP": 14.5, "SE": 68.0, "CP": 18.1},
        "نعاج حامل": {"DP": 11.5, "SE": 62.0, "CP": 14.4},
        "نعاج جافة": {"DP": 8.5, "SE": 58.0, "CP": 10.6}
    },
    "ماعز": {
        "تسمين جديان": {"DP": 12.5, "SE": 64.0, "CP": 15.6},
        "عنزات حلابة": {"DP": 14.0, "SE": 66.0, "CP": 17.5},
        "عنزات حامل": {"DP": 11.0, "SE": 60.0, "CP": 13.8},
        "صيانة": {"DP": 8.0, "SE": 56.0, "CP": 10.0}
    },
    "خيول": {
        "راحة/صيانة": {"DP": 9.0, "SE": 58.0, "CP": 11.3},
        "عمل خفيف": {"DP": 10.0, "SE": 60.0, "CP": 12.5},
        "عمل متوسط": {"DP": 11.0, "SE": 62.0, "CP": 13.8},
        "عمل مكثف": {"DP": 13.0, "SE": 65.0, "CP": 16.3},
        "سباق": {"DP": 14.0, "SE": 68.0, "CP": 17.5},
        "أمهار نامية": {"DP": 13.0, "SE": 64.0, "CP": 16.3},
        "فرسات مرضعات": {"DP": 14.0, "SE": 66.0, "CP": 17.5}
    },
    "إبل": {
        "راحة/صيانة": {"DP": 8.0, "SE": 55.0, "CP": 10.0},
        "حمل/رضاعة": {"DP": 10.0, "SE": 58.0, "CP": 12.5},
        "إنتاج حليب": {"DP": 12.0, "SE": 60.0, "CP": 15.0},
        "تسمين": {"DP": 11.0, "SE": 62.0, "CP": 13.8},
        "عمل/نقل": {"DP": 10.0, "SE": 58.0, "CP": 12.5}
    },
    "دواجن": {
        "بادي (0-14 يوم)": {"DP": 22.0, "SE": 76.0, "CP": 27.5},
        "نامي (15-28 يوم)": {"DP": 20.0, "SE": 74.0, "CP": 25.0},
        "ناهي (29-42 يوم)": {"DP": 18.0, "SE": 72.0, "CP": 22.5},
        "ناهي متقدم (43+ يوم)": {"DP": 16.0, "SE": 70.0, "CP": 20.0}
    },
    "أسماك": {
        "زريعة/بادئ": {"DP": 32.0, "SE": 70.0, "CP": 40.0},
        "نمو": {"DP": 28.0, "SE": 68.0, "CP": 35.0},
        "تسمين نهائي": {"DP": 26.0, "SE": 66.0, "CP": 32.5},
        "زريعة متقدمة": {"DP": 30.0, "SE": 69.0, "CP": 37.5}
    }
}

# =====================================================================
# معادلات NRC
# =====================================================================
class AdvancedProductionEquations:
    @staticmethod
    def calculate_milk_protein_requirement(milk_yield_kg, milk_protein_pct=3.3):
        return (milk_yield_kg * (milk_protein_pct / 100)) / 0.65
    
    @staticmethod
    def calculate_maintenance_protein(weight_kg):
        return 2.5 * (weight_kg ** 0.75)
    
    @staticmethod
    def calculate_metabolic_protein(weight_kg):
        return 1.2 * (weight_kg ** 0.75)
    
    @staticmethod
    def calculate_total_protein_for_dairy(weight_kg, milk_yield_kg, milk_fat_pct=3.5, milk_protein_pct=3.3):
        maintenance = AdvancedProductionEquations.calculate_maintenance_protein(weight_kg)
        metabolic = AdvancedProductionEquations.calculate_metabolic_protein(weight_kg)
        production = AdvancedProductionEquations.calculate_milk_protein_requirement(milk_yield_kg, milk_protein_pct)
        total = maintenance + metabolic + production
        return {
            'maintenance': maintenance, 'metabolic': metabolic,
            'production': production, 'total': total,
            'dp_requirement': (total / (weight_kg * 10)) * 100
        }
    
    @staticmethod
    def calculate_energy_for_dairy(weight_kg, milk_yield_kg, milk_fat_pct=3.5):
        maintenance = 0.08 * (weight_kg ** 0.75)
        fat_correction = 1 + 0.15 * (milk_fat_pct - 3.5)
        production = 5.3 * milk_yield_kg * fat_correction
        total = maintenance + production
        return {
            'maintenance_energy': maintenance, 'production_energy': production,
            'total_energy': total, 'se_requirement': total * 10
        }
    
    @staticmethod
    def calculate_protein_for_gain(daily_gain_kg, protein_in_gain_pct=18.0):
        return (daily_gain_kg * (protein_in_gain_pct / 100)) / 0.65
    
    @staticmethod
    def calculate_energy_for_gain(daily_gain_kg, gain_energy_pct=5.0):
        return (daily_gain_kg * gain_energy_pct) / 0.70
    
    @staticmethod
    def calculate_total_protein_for_fattening(weight_kg, daily_gain_kg):
        maintenance = 2.0 * (weight_kg ** 0.75)
        metabolic = 1.0 * (weight_kg ** 0.75)
        production = AdvancedProductionEquations.calculate_protein_for_gain(daily_gain_kg)
        total = maintenance + metabolic + production
        return {
            'maintenance': maintenance, 'metabolic': metabolic,
            'production': production, 'total': total,
            'dp_requirement': (total / (weight_kg * 8)) * 100
        }
    
    @staticmethod
    def calculate_total_energy_for_fattening(weight_kg, daily_gain_kg):
        maintenance = 0.07 * (weight_kg ** 0.75)
        production = AdvancedProductionEquations.calculate_energy_for_gain(daily_gain_kg)
        total = maintenance + production
        return {
            'maintenance_energy': maintenance, 'production_energy': production,
            'total_energy': total, 'se_requirement': total * 10
        }
    
    @staticmethod
    def calculate_protein_energy_ratio(protein_requirement, energy_requirement):
        return energy_requirement / protein_requirement if protein_requirement > 0 else 0

# =====================================================================
# المختبر الذكي (OCR)
# =====================================================================
class SmartLabSystem:
    def __init__(self):
        self.db = DatabaseManager()
        self.ocr_available = OCR_AVAILABLE or EASYOCR_AVAILABLE
        self.reader = None
        if EASYOCR_AVAILABLE:
            try:
                self.reader = easyocr.Reader(['ar', 'en'], gpu=False)
            except Exception:
                self.reader = None
    
    def analyze_image(self, image):
        if not self.ocr_available:
            return None, "مكتبات OCR غير مثبتة."
        results = []
        try:
            if EASYOCR_AVAILABLE and self.reader:
                result = self.reader.readtext(np.array(image))
                for (bbox, text, prob) in result:
                    if prob > 0.3:
                        results.append(text)
            elif OCR_AVAILABLE:
                img = PILImage.open(image) if not isinstance(image, PILImage.Image) else image
                text = pytesseract.image_to_string(img, lang='ara+eng')
                results = text.split('\n')
            return self._parse_ocr_results(results), None
        except Exception as e:
            return None, f"خطأ: {str(e)}"
    
    def _parse_ocr_results(self, texts):
        data = {'sample_name': '', 'cp': None, 'dc': None, 'se': None,
                'ndf': None, 'adf': None, 'ee': None, 'ash': None, 'moisture': None}
        patterns = {
            'cp': [r'بروتين\s*خام\s*[:=]?\s*([\d.]+)', r'CP\s*[:=]?\s*([\d.]+)'],
            'dc': [r'معامل\s*الهضم\s*[:=]?\s*([\d.]+)', r'DC\s*[:=]?\s*([\d.]+)'],
            'se': [r'معادل\s*النشاء\s*[:=]?\s*([\d.]+)', r'SE\s*[:=]?\s*([\d.]+)'],
            'ndf': [r'NDF\s*[:=]?\s*([\d.]+)'],
            'adf': [r'ADF\s*[:=]?\s*([\d.]+)'],
            'ee': [r'دهن\s*خام\s*[:=]?\s*([\d.]+)', r'EE\s*[:=]?\s*([\d.]+)'],
            'ash': [r'رماد\s*[:=]?\s*([\d.]+)', r'ASH\s*[:=]?\s*([\d.]+)'],
            'moisture': [r'رطوبة\s*[:=]?\s*([\d.]+)']
        }
        for text in texts:
            t = text.strip()
            if 'اسم' in t and not data['sample_name']:
                parts = t.split(':')
                if len(parts) > 1:
                    data['sample_name'] = parts[1].strip()
            for key, plist in patterns.items():
                if data[key] is None:
                    for pattern in plist:
                        m = re.search(pattern, t, re.IGNORECASE)
                        if m:
                            try:
                                data[key] = float(m.group(1))
                                break
                            except Exception:
                                pass
        return data
    
    def save_lab_result(self, result_data):
        result_id = secrets.token_hex(16)
        data = {
            'analysis_id': result_id,
            'sample_name': result_data.get('sample_name', ''),
            'analysis_date': datetime.now().isoformat(),
            'moisture': result_data.get('moisture', 0.0),
            'protein': result_data.get('cp', 0.0),
            'fat': result_data.get('ee', 0.0),
            'fiber': result_data.get('ndf', 0.0),
            'ash': result_data.get('ash', 0.0),
            'se': result_data.get('se', 0.0),
            'dc': result_data.get('dc', 0.0),
            'ndf': result_data.get('ndf', 0.0),
            'adf': result_data.get('adf', 0.0),
            'notes': result_data.get('notes', ''),
            'performed_by': result_data.get('analyzed_by', '')
        }
        self.db.insert_record('quality_analysis', data)
        return result_id

# =====================================================================
# نظام إدارة المزارع
# =====================================================================
class FarmManagementSystem:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_farm(self, farm_name, farm_type, owner_name, owner_phone, location="", area=0.0):
        farm_id = secrets.token_hex(16)
        self.db.insert_record('farms', {
            'farm_id': farm_id, 'farm_name': farm_name, 'farm_type': farm_type,
            'owner_name': owner_name, 'owner_phone': owner_phone,
            'location': location, 'area': area,
            'created_date': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        })
        return farm_id
    
    def create_production_cycle(self, farm_id, cycle_type, initial_count, breed):
        cycle_id = secrets.token_hex(16)
        self.db.insert_record('production_cycles', {
            'cycle_id': cycle_id, 'farm_id': farm_id, 'cycle_type': cycle_type,
            'start_date': datetime.now().isoformat(), 'end_date': '',
            'initial_count': initial_count, 'breed': breed,
            'target_weight': 0.0, 'target_age': 0,
            'status': 'active', 'notes': ''
        })
        return cycle_id
    
    def add_daily_record(self, cycle_id, record_data):
        record_id = secrets.token_hex(16)
        live_birds = record_data.get('live_birds', 0)
        avg_weight = record_data.get('avg_weight', 0)
        feed_consumed = record_data.get('feed_consumed', 0)
        dead_count = record_data.get('dead_count', 0)
        initial_count = record_data.get('initial_count', live_birds + dead_count)
        total_gain = live_birds * avg_weight
        fcr = feed_consumed / total_gain if total_gain > 0 else 0
        mortality = (dead_count / initial_count) * 100 if initial_count > 0 else 0
        self.db.insert_record('daily_records', {
            'record_id': record_id, 'cycle_id': cycle_id,
            'record_date': datetime.now().isoformat(),
            'age_days': record_data.get('age_days', 0),
            'live_birds': live_birds, 'avg_weight': avg_weight,
            'feed_consumed': feed_consumed, 'dead_count': dead_count,
            'culled_count': 0, 'temperature': record_data.get('temperature', 0),
            'humidity': record_data.get('humidity', 0),
            'feed_conversion': fcr, 'mortality_rate': mortality,
            'notes': record_data.get('notes', '')
        })
        return record_id
    
    def get_active_cycles(self):
        return self.db.get_records('production_cycles', {'status': 'active'})
    
    def close_cycle(self, cycle_id):
        conn = sqlite3.connect(self.db.db_path)
        c = conn.cursor()
        c.execute("UPDATE production_cycles SET status='completed', end_date=? WHERE cycle_id=?",
                  (datetime.now().isoformat(), cycle_id))
        conn.commit()
        conn.close()

farm_system = FarmManagementSystem()

# =====================================================================
# المراجع العلمية
# =====================================================================
class ScientificReferenceSystem:
    REFERENCES = {
        "general_nutrition": {
            "title": "المبادئ الأساسية لتغذية الحيوان", "icon": "📚",
            "references": [
                {"id": "REF001", "authors": "McDonald, P., et al.", "year": 2011,
                 "title": "Animal Nutrition", "publisher": "Pearson",
                 "summary": "المرجع الأساسي في تغذية الحيوان."},
                {"id": "REF002", "authors": "Cheeke, P.R.", "year": 2010,
                 "title": "Comparative Animal Nutrition", "publisher": "CABI",
                 "summary": "مقارنة بين آليات التغذية."}
            ]
        },
        "protein_amino_acids": {
            "title": "البروتين والأحماض الأمينية", "icon": "🧬",
            "references": [
                {"id": "REF004", "authors": "NRC", "year": 2001,
                 "title": "Nutrient Requirements of Dairy Cattle", "publisher": "NAP",
                 "summary": "المرجع الأساسي لتغذية أبقار الحليب."}
            ]
        },
        "poultry": {
            "title": "تغذية الدواجن", "icon": "🐔",
            "references": [
                {"id": "REF010", "authors": "Leeson, S.", "year": 2009,
                 "title": "Commercial Poultry Nutrition", "publisher": "NUP",
                 "summary": "المرجع العملي في تغذية الدواجن."}
            ]
        },
        "ruminants": {
            "title": "تغذية المجترات", "icon": "🐄",
            "references": [
                {"id": "REF012", "authors": "Church, D.C.", "year": 1993,
                 "title": "The Ruminant Animal", "publisher": "Waveland",
                 "summary": "المرجع الشامل للمجترات."}
            ]
        },
        "sheep_goats": {
            "title": "تغذية الأغنام والماعز", "icon": "🐏",
            "references": [
                {"id": "REF014", "authors": "NRC", "year": 2007,
                 "title": "Nutrient Requirements of Small Ruminants", "publisher": "NAP",
                 "summary": "المرجع الرسمي للأغنام والماعز."}
            ]
        },
        "horses": {
            "title": "تغذية الخيول", "icon": "🐴",
            "references": [
                {"id": "REF015", "authors": "NRC", "year": 2007,
                 "title": "Nutrient Requirements of Horses", "publisher": "NAP",
                 "summary": "المرجع الأساسي للخيول."}
            ]
        },
        "camels": {
            "title": "تغذية الإبل", "icon": "🐫",
            "references": [
                {"id": "REF030", "authors": "Faye, B.", "year": 2018,
                 "title": "Camel Nutrition", "publisher": "FAO",
                 "summary": "المرجع الأساسي لتغذية الإبل."}
            ]
        },
        "aquaculture": {
            "title": "تغذية الأسماك", "icon": "🐟",
            "references": [
                {"id": "REF016", "authors": "Halver, J.E.", "year": 2002,
                 "title": "Fish Nutrition", "publisher": "Academic Press",
                 "summary": "المرجع الشامل للأسماك."}
            ]
        },
        "digestible_protein": {
            "title": "البروتين المهضوم", "icon": "🧪",
            "references": [
                {"id": "REF023", "authors": "INRA", "year": 2007,
                 "title": "INRA Feeding System", "publisher": "WAP",
                 "summary": "النظام الفرنسي للمجترات."}
            ]
        },
        "milk_replacers": {
            "title": "بدائل الحليب", "icon": "🍼",
            "references": [
                {"id": "REF040", "authors": "Davis, C.L.", "year": 1998,
                 "title": "The Young Calf", "publisher": "Iowa State",
                 "summary": "تغذية العجول الصغيرة."}
            ]
        }
    }
    
    KNOWLEDGE_BASE = {
        "ما هو البروتين المهضوم": "البروتين المهضوم (DP) هو الجزء من البروتين الذي يستفيد منه الحيوان فعلياً، ويُحسب بضرب CP × DC.",
        "ما هو معادل النشاء": "معادل النشاء (SE) هو مقياس لكمية الطاقة في العلف مقارنة بالنشاء النقي.",
        "كيف يتم تركيب العلف الأمثل": "باستخدام محرك الاستمثال الخطي Linear Programming لحساب أقل تكلفة.",
        "ما هو مؤشر EPEF": "EPEF = (الحيوية × الوزن الحي) / (العمر × FCR) × 100.",
        "ما هو FCR": "معامل التحويل = العلف المستهلك / الوزن المكتسب."
    }
    
    @staticmethod
    def get_knowledge_answer(question):
        for key, value in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            if key in question:
                return {"answer": value, "simplified": value}
        return None

# =====================================================================
# الصور
# =====================================================================
ANIMAL_IMAGES_RESOURCES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "إبل": "https://images.unsplash.com/photo-1502175353174-a7a70e73b362?q=80&w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600"
}

# =====================================================================
# المخزون
# =====================================================================
def init_inventory():
    if "inventory" not in st.session_state:
        st.session_state["inventory"] = {}
        for items in BIG_FEEDS_LIBRARY.values():
            for ing in items:
                st.session_state["inventory"][ing] = {
                    "quantity": 25.0, "min_threshold": 5.0, "unit": "طن"
                }

init_inventory()

# =====================================================================
# حالة الجلسة
# =====================================================================
defaults = {
    "approved": False, "user_role": None, "login_welcome_shown": False,
    "login_attempts": 0, "last_login_time": None, "session_token": None,
    "broiler_farms": {}, "daily_production_log": [],
    "active_formula": {}, "active_cp_tag": 12.0, "active_se_tag": 65.0,
    "active_breed_tag": "سلالة عامة", "computed_ton_cost": 280.0,
    "lab_sample": None, "dose_reminders": [], "ocr_result": {},
    "email_password": None,
    "global_livestock_prices": {
        "عجول تسمين ($)": 1350.0, "أبقار محلية ($)": 900.0,
        "ضأن ($)": 180.0, "ماعز ($)": 130.0,
        "خيول أصيلة ($)": 4500.0, "إبل ($)": 2500.0, "كتكوت لاحم ($)": 0.65
    },
    "global_products_prices": {
        "كيلو لحم بقري ($)": 7.50, "كيلو لحم ضأن ($)": 9.00,
        "كيلو لحم دجاج ($)": 3.80, "طبق بيض 30 ($)": 4.20,
        "لتر حليب بقري ($)": 0.90, "لتر حليب إبل ($)": 1.50
    },
    "shared_comments": "• [توجيه الاختصاصي م. عبد القادر إسماعيل تاور]: يرجى من جميع الزملاء إضافة تعليقاتهم.\n"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if "smart_lab" not in st.session_state:
    try:
        st.session_state["smart_lab"] = SmartLabSystem()
    except Exception:
        st.session_state["smart_lab"] = None

print("✅ الجزء 2/3 تم التحميل - المكتبات والمعايير والمعادلات")
# =====================================================================
# CSS التجميلي
# =====================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
* { font-family: 'Cairo', 'Tajawal', sans-serif; }
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 25%, #b2dfdb 50%, #c8e6c9 75%, #e8f5e9 100%);
    background-size: 400% 400%;
    animation: gradientShift 20s ease infinite;
    background-attachment: fixed;
}
@keyframes gradientShift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}
.stApp { background: transparent; }
.main-box {
    background: rgba(255,255,255,0.97);
    padding: 40px; border-radius: 28px;
    box-shadow: 0 30px 80px rgba(0,0,0,0.18);
    backdrop-filter: blur(20px);
    margin-bottom: 40px;
    border: 2px solid rgba(212,175,55,0.3);
}
h1, h2, h3, h4, h5 { color: #1a237e !important; font-weight: 700 !important; }
.section-title {
    color: #1b5e20 !important;
    border-right: 8px solid #2e7d32;
    padding: 18px 25px;
    text-align: right;
    font-size: 1.8rem;
    font-weight: 900;
    margin: 35px 0 25px 0;
    background: linear-gradient(to left, rgba(46,125,50,0.15), transparent);
    border-radius: 14px;
    box-shadow: 0 4px 15px rgba(46,125,50,0.1);
}
.formula-item {
    background: linear-gradient(135deg, #ffffff 0%, #f1f8e9 100%);
    padding: 18px 25px; border-radius: 16px; margin-bottom: 12px;
    font-weight: 700; color: #1b5e20 !important;
    border-right: 6px solid #2e7d32;
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    transition: all 0.4s ease;
    display: flex; justify-content: space-between; align-items: center;
}
.formula-item:hover {
    transform: translateX(-12px) scale(1.02);
    box-shadow: 0 12px 35px rgba(46,125,50,0.25);
}
.profile-img-style {
    width: 170px; height: 170px; border-radius: 50%; object-fit: cover;
    border: 5px solid #d4af37;
    box-shadow: 0 15px 40px rgba(212,175,55,0.4);
    transition: all 0.6s ease;
    background: #fff;
}
.profile-img-style:hover { transform: scale(1.08) rotate(5deg); }
.metric-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    padding: 25px 20px; border-radius: 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    text-align: center;
    transition: all 0.4s ease;
    border: 2px solid rgba(46,125,50,0.1);
}
.metric-card:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 20px 45px rgba(46,125,50,0.2);
}
.metric-card .number {
    font-size: 2.5rem; font-weight: 900;
    background: linear-gradient(135deg, #1b5e20, #2e7d32, #43a047);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 8px 0;
}
.metric-card .label {
    font-size: 0.95rem; color: #555;
    font-weight: 700;
}
.measurement-card {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    padding: 25px; border-radius: 18px;
    border-right: 6px solid #1565C0;
    box-shadow: 0 8px 30px rgba(21,101,192,0.15);
}
.price-card {
    background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e9 100%);
    padding: 22px; border-radius: 16px;
    border-right: 6px solid #2e7d32;
    margin-bottom: 20px; direction: rtl; text-align: right;
    box-shadow: 0 8px 25px rgba(46,125,50,0.12);
}
.warning-card {
    background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    padding: 18px; border-radius: 14px;
    border-right: 6px solid #f57c00;
    margin-bottom: 15px; direction: rtl; text-align: right;
    color: #e65100 !important;
    box-shadow: 0 6px 20px rgba(245,124,0,0.15);
    font-weight: 600;
}
.stock-critical {
    background: linear-gradient(135deg, #ffebee, #ffcdd2);
    padding: 8px 18px; border-radius: 25px;
    color: #c62828 !important; font-weight: 700;
    display: inline-block;
    border: 2px solid #ef5350;
}
.stock-normal {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    padding: 8px 18px; border-radius: 25px;
    color: #2e7d32 !important; font-weight: 700;
    display: inline-block;
    border: 2px solid #66bb6a;
}
.manual-book {
    background: linear-gradient(135deg, #ffffff 0%, #fafafa 100%);
    padding: 40px; border-radius: 20px;
    box-shadow: 0 15px 50px rgba(0,0,0,0.1);
    direction: rtl; text-align: right;
}
.book-chapter {
    background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
    color: #ffffff !important;
    padding: 18px 25px; border-radius: 14px;
    font-weight: 800; margin-top: 30px;
    font-size: 1.3rem;
    box-shadow: 0 8px 25px rgba(26,35,126,0.3);
    border-right: 6px solid #d4af37;
}
.book-body {
    padding: 25px 30px; font-size: 1.1rem; line-height: 1.9;
    color: #2c3e50 !important;
    border-left: 5px solid #3498db;
    margin-bottom: 25px;
    background: linear-gradient(to right, #f8f9fa, #ffffff);
    border-radius: 0 14px 14px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}
.stButton > button {
    color: #1a1a1a !important;
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%) !important;
    border: 2px solid #2e7d32 !important;
    font-weight: 700 !important;
    border-radius: 14px !important;
    padding: 12px 24px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(46,125,50,0.15) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #a5d6a7 0%, #81c784 100%) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(46,125,50,0.3) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #43a047 100%) !important;
    color: #ffffff !important;
    border: 2px solid #1b5e20 !important;
    box-shadow: 0 6px 25px rgba(27,94,32,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2e7d32 0%, #43a047 50%, #66bb6a 100%) !important;
    box-shadow: 0 10px 35px rgba(46,125,50,0.5) !important;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 12px !important;
    border: 2px solid #c8e6c9 !important;
    padding: 12px 15px !important;
    background: #ffffff !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #2e7d32 !important;
    box-shadow: 0 0 0 4px rgba(46,125,50,0.15) !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255,255,255,0.8);
    padding: 8px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}
.stTabs [data-baseweb="tab-list"] button {
    border-radius: 12px !important;
    padding: 12px 20px !important;
    font-weight: 600 !important;
    color: #555 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%) !important;
    color: #1b5e20 !important;
    font-weight: 800 !important;
    box-shadow: 0 4px 15px rgba(46,125,50,0.2) !important;
}
.stAlert {
    border-radius: 14px !important;
    border-right: 6px solid currentColor !important;
    padding: 16px 20px !important;
    font-weight: 600 !important;
}
.stDataFrame {
    border-radius: 14px !important;
    overflow: hidden !important;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08) !important;
}
.mini-left-signature {
    position: fixed; left: 20px; bottom: 20px;
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    color: white !important;
    padding: 10px 25px; font-size: 0.85rem;
    border-radius: 25px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.35);
    z-index: 9999; direction: rtl;
    border: 2px solid rgba(255,215,0,0.4);
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# شريط الدعاء
# =====================================================================
def render_dua_bar():
    st.markdown("""
    <style>
    @keyframes scrollDua {
        0% { transform: translateX(100%); opacity: 0; }
        5%, 85% { transform: translateX(0%); opacity: 1; }
        95%, 100% { transform: translateX(-100%); opacity: 0; }
    }
    @keyframes glowText {
        0%, 100% { text-shadow: 0 0 5px #ffd700, 0 0 10px #ffd700, 0 0 20px #ff8c00; }
        50% { text-shadow: 0 0 15px #ffd700, 0 0 30px #ff8c00, 0 0 60px #ff4500; }
    }
    .dua-container {
        background: linear-gradient(135deg, #0d1b2a 0%, #1a237e 40%, #4a148c 70%, #0d1b2a 100%);
        padding: 25px 0; border-radius: 24px;
        margin-bottom: 25px; overflow: hidden;
        border: 3px solid #ffd700;
        box-shadow: 0 12px 45px rgba(255,215,0,0.4);
        direction: rtl;
    }
    .dua-text {
        display: inline-block; white-space: nowrap;
        animation: scrollDua 24s ease-in-out infinite, glowText 3.5s ease-in-out infinite;
        font-size: 1.7rem; font-weight: 800;
        color: #ffd700;
        padding: 0 25px; direction: rtl;
    }
    .dua-text .name-highlight {
        color: #ffab40; font-weight: 900;
        background: rgba(255,215,0,0.15);
        padding: 0 10px;
        border-radius: 8px;
        border: 1px solid rgba(255,215,0,0.3);
    }
    </style>
    <div class="dua-container">
        <div class="dua-text">
            ❤️ اللهم اغفر لـ <span class="name-highlight">إسماعيل تاور</span> و <span class="name-highlight">ابتسام</span> وارحمهما وأدخلهما فسيح جناتك ❤️
            اللهم اجعل قبرهما روضة من رياض الجنة واجمعنا بهما في الفردوس الأعلى ❤️
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# شاشة الدخول
# =====================================================================
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300

if not st.session_state["approved"]:
    render_dua_bar()
    
    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        if st.session_state["last_login_time"]:
            time_diff = (datetime.now() - st.session_state["last_login_time"]).seconds
            if time_diff < LOCKOUT_TIME:
                st.error(f"🔒 تم قفل النظام مؤقتاً. المتبقي: {LOCKOUT_TIME - time_diff} ثانية")
                st.stop()
            else:
                st.session_state["login_attempts"] = 0
    
    st.markdown('<div class="main-box" style="max-width:600px; margin:80px auto; direction:rtl;">', unsafe_allow_html=True)
    
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" style="width:120px; height:120px; border-radius:50%; border:4px solid #d4af37; display:block; margin:0 auto; box-shadow:0 8px 25px rgba(0,0,0,0.2);">', unsafe_allow_html=True)
    
    st.markdown("<h2 style='color:#1a237e; text-align:center; margin-top:20px;'>🌾 تاور نولجي Tawornology العلمية</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555; font-size:1.15rem;'>للانتاج الحيواني وتركيب الاعلاف</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#c62828; font-size:1rem; font-weight:700;'>الاختصاصي م. عبد القادر إسماعيل تاور — اختصاصي تغذية الحيوان</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888; font-size:0.85rem;'>الإصدار 17.1</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_audio1, col_audio2, col_audio3 = st.columns(3)
    with col_audio1:
        if st.button("🔊 الشرح الكامل", use_container_width=True, key="audio_guide"):
            play_full_guide_audio()
            st.success("✅ يعمل...")
    with col_audio2:
        if st.button("🎵 الترحيب", use_container_width=True, key="audio_welcome"):
            play_welcome_audio()
    with col_audio3:
        if st.button("🕊️ الدعاء", use_container_width=True, key="audio_dua"):
            play_dua_audio()
    
    st.markdown("---")
    st.markdown("### 👤 دخول كزائر مجاني")
    st.caption("عرض محدود — تركيب الأعلاف، المختبر الذكي، المراجع، المساعدة")
    
    if st.button("🚀 الدخول كزائر", type="secondary", use_container_width=True, key="public_login"):
        st.session_state["approved"] = True
        st.session_state["user_role"] = "public"
        st.session_state["login_welcome_shown"] = False
        st.session_state["login_attempts"] = 0
        st.session_state["last_login_time"] = datetime.now()
        st.session_state["session_token"] = secrets.token_urlsafe(32)
        st.session_state["user"] = {
            'user_id': 'public_visitor',
            'username': 'visitor',
            'role': 'public',
            'full_name': 'زائر',
            'email': '', 'phone': '',
            'specialty': 'عام', 'experience_years': 0
        }
        voice_guide("السلام عليكم، مرحباً بك زائراً في تاور نولجي.")
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔑 دخول المالك (بالكود السري)")
    st.caption("للمالك والاختصاصي فقط — كل الميزات متاحة")
    
    input_code = st.text_input("🔐 كود الدخول:", type="password",
                               placeholder="أدخل الكود الخاص بك",
                               key="owner_code_input")
    
    col_login, col_reset = st.columns(2)
    with col_login:
        if st.button("🔓 تسجيل الدخول", type="primary", use_container_width=True, key="owner_login"):
            if input_code.strip() in CODES_DB:
                info = CODES_DB[input_code.strip()]
                st.session_state["approved"] = True
                st.session_state["user_role"] = info["role"]
                st.session_state["login_welcome_shown"] = False
                st.session_state["login_attempts"] = 0
                st.session_state["last_login_time"] = datetime.now()
                st.session_state["session_token"] = secrets.token_urlsafe(32)
                st.session_state["user"] = {
                    'user_id': secrets.token_hex(16),
                    'username': info["role"],
                    'role': info["role"],
                    'full_name': info["name"],
                    'email': OWNER_EMAIL,
                    'phone': WHATSAPP_NUMBER,
                    'specialty': 'اختصاصي تغذية الحيوان',
                    'experience_years': 15
                }
                voice_guide(f"مرحباً بك، {info['name']}")
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ الكود غير صحيح! متبقي {remaining} محاولات")
    with col_reset:
        if st.button("🔄 نسيت الكود", use_container_width=True, key="owner_reset"):
            st.info("📧 يرجى التواصل: abukram128@gmail.com")
    
    st.markdown("""
    <div style='text-align:center; margin-top:20px; color:#999; font-size:0.85rem; padding:15px; border-top:1px solid #e0e0e0;'>
    <p>🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b></p>
    <p style='color:#b39ddb; font-size:0.8rem;'>اللهم اجعل قبرهما روضة من رياض الجنة</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# الترحيب
# =====================================================================
if not st.session_state["login_welcome_shown"]:
    role = st.session_state.get("user_role", "public")
    msgs = {
        "owner": "👑 مرحباً بك، الاختصاصي م. عبد القادر إسماعيل تاور",
        "public": "👤 مرحباً بك زائراً"
    }
    st.toast(msgs.get(role, "مرحباً"), icon="🌾")
    try:
        voice_welcome(role)
    except Exception:
        pass
    st.session_state["login_welcome_shown"] = True

render_dua_bar()

# =====================================================================
# الواجهة الرئيسية
# =====================================================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logout_space, col_user_status = st.columns([0.7, 0.3])
with col_user_status:
    user_name = st.session_state.get("user", {}).get("full_name", "زائر")
    user_role = st.session_state.get("user_role", "public")
    role_display = "المالك 👑" if user_role == "owner" else "زائر 👤"
    
    st.markdown(f"""
    <div style='text-align:left; background:linear-gradient(135deg,#f5f5f5,#e0e0e0); padding:14px; border-radius:14px;'>
        <div style='font-weight:700; font-size:1rem;'>{user_name}</div>
        <div style='font-size:0.85rem; color:#555;'>{role_display}</div>
        <small style='color:#888;'>آخر دخول: {datetime.now().strftime('%Y-%m-%d %H:%M')}</small>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        protected = ["inventory", "broiler_farms", "dose_reminders",
                     "daily_production_log", "active_formula", "active_cp_tag",
                     "active_se_tag", "active_breed_tag", "computed_ton_cost",
                     "smart_lab", "global_livestock_prices", "global_products_prices",
                     "shared_comments", "lab_sample"]
        for key in list(st.session_state.keys()):
            if key not in protected:
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

col_logo, col_title = st.columns([0.2, 0.8])
with col_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='color:#1a237e; text-align:right; margin-bottom:0; font-size:2.2rem;'>🌾 تاور نولجي Tawornology العلمية</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#1565C0; text-align:right; font-size:1.2rem;'>للانتاج الحيواني وتركيب الاعلاف</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#c62828; text-align:right; font-weight:700;'>الاختصاصي م. عبد القادر إسماعيل تاور — اختصاصي تغذية الحيوان</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top:3px solid #2e7d32;'>", unsafe_allow_html=True)

# إحصائيات
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
with col_stat1:
    st.markdown(f"<div class='metric-card'><div class='number'>{len(st.session_state['inventory'])}</div><div class='label'>إجمالي المواد</div></div>", unsafe_allow_html=True)
with col_stat2:
    total_qty = sum(d['quantity'] if isinstance(d, dict) else d for d in st.session_state['inventory'].values())
    st.markdown(f"<div class='metric-card'><div class='number'>{total_qty:.1f}</div><div class='label'>المخزون (طن)</div></div>", unsafe_allow_html=True)
with col_stat3:
    low = sum(1 for d in st.session_state['inventory'].values() if (d['quantity'] if isinstance(d, dict) else d) < 5)
    st.markdown(f"<div class='metric-card'><div class='number' style='color:#e65100;'>{low}</div><div class='label'>مواد منخفضة</div></div>", unsafe_allow_html=True)
with col_stat4:
    st.markdown(f"<div class='metric-card'><div class='number'>{len(st.session_state['broiler_farms'])}</div><div class='label'>دورات المزارع</div></div>", unsafe_allow_html=True)

st.markdown("---")

# =====================================================================
# دالة دليل التبويب
# =====================================================================
def guide_section(tab_name, guide_text):
    with st.expander(f"📘 دليل استخدام {tab_name}", expanded=False):
        st.markdown(f"<div style='background:#f0f8ff; padding:15px; border-radius:10px; direction:rtl;'>{guide_text}</div>", unsafe_allow_html=True)
        if st.button(f"🔊 تشغيل الدليل صوتياً", key=f"guide_{tab_name}"):
            voice_guide(guide_text)

# =====================================================================
# دالة تركيب العلف
# =====================================================================
def render_feed_formulation(animal_key, display_name, icon, default_breeds, default_stages,
                             default_dp, default_se, has_measurements=True):
    st.markdown(f'<div class="section-title">{icon} {display_name}</div>', unsafe_allow_html=True)
    
    requester_name = st.text_input("👤 اسم طالب العلف (المربي / المزرعة):",
                                   placeholder="أدخل اسم المربي أو المزرعة",
                                   key=f"{animal_key}_requester")
    
    col_measure, col_settings = st.columns([0.4, 0.6])
    
    with col_measure:
        if has_measurements:
            st.markdown('<div class="measurement-card">', unsafe_allow_html=True)
            st.markdown("#### 📏 شريط القياس الحيوي")
            col_h, col_l, col_age = st.columns(3)
            with col_h:
                h_girth = st.number_input("محيط الصدر (سم)", min_value=20.0, max_value=300.0,
                                          value=150.0, step=1.0, key=f"{animal_key}_girth")
            with col_l:
                b_length = st.number_input("طول الجسم (سم)", min_value=20.0, max_value=300.0,
                                           value=130.0, step=1.0, key=f"{animal_key}_length")
            with col_age:
                age_months = st.number_input("العمر (شهر)", min_value=1, max_value=120,
                                             value=12, step=1, key=f"{animal_key}_age")
            
            weight_factors = {"cattle": 10838, "sheep": 15500, "goat": 15000,
                              "horse": 11877, "camel": 13000}
            feed_factors = {"cattle": 0.025, "sheep": 0.035, "goat": 0.032,
                            "horse": 0.022, "camel": 0.020}
            wf = weight_factors.get(animal_key, 12000)
            ff = feed_factors.get(animal_key, 0.03)
            estimated_weight = (h_girth ** 2 * b_length) / wf
            daily_dry_matter = estimated_weight * ff
            
            st.success(f"**الوزن التقديري:** {estimated_weight:.1f} كجم")
            st.info(f"**الاحتياج اليومي:** {daily_dry_matter:.2f} كجم مادة جافة")
            
            if estimated_weight > 0:
                age_factor = 1 + (age_months - 12) * 0.01
                adjusted_dp = default_dp * (1 + (estimated_weight - 500) / 2000) * age_factor
                adjusted_se = default_se * (1 + (estimated_weight - 500) / 3000) * age_factor
            else:
                adjusted_dp = default_dp
                adjusted_se = default_se
            st.caption(f"⚖️ DP المقترح: {adjusted_dp:.1f}% | SE المقترح: {adjusted_se:.1f}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            adjusted_dp = default_dp
            adjusted_se = default_se
            st.info("💡 لا تتوفر قياسات جسدية للطيور والأسماك.")
    
    with col_settings:
        st.markdown("#### 🎯 السلالة والمرحلة")
        col_b, col_s = st.columns(2)
        with col_b:
            breed = st.selectbox("السلالة:", default_breeds, key=f"{animal_key}_breed")
        with col_s:
            stage = st.selectbox("المرحلة:", default_stages, key=f"{animal_key}_stage")
        
        st.markdown("#### 🧬 العمر والحالة")
        col_age_phys = st.columns(2)
        with col_age_phys[0]:
            age_input = st.number_input("العمر (شهر)", min_value=1, max_value=240,
                                        value=24, step=1, key=f"{animal_key}_age_input")
        with col_age_phys[1]:
            physiological_state = st.selectbox(
                "الحالة:",
                ["طبيعي", "حامل", "مرضع", "صائم", "نشاط مكثف", "استشفاء", "نمو سريع"],
                key=f"{animal_key}_physiological"
            )
        
        protein_basis = st.radio("أساس البروتين:", ["DP", "CP"], horizontal=True,
                                 key=f"{animal_key}_basis")
        
        if protein_basis == "DP":
            target_protein = st.number_input("نسبة DP (%)", min_value=5.0, max_value=50.0,
                                             value=float(adjusted_dp), step=0.5, key=f"{animal_key}_dp")
            st.caption(f"💡 CP ≈ {target_protein / 0.80:.1f}%")
        else:
            target_protein = st.number_input("نسبة CP (%)", min_value=5.0, max_value=60.0,
                                             value=float(default_dp/0.80), step=0.5, key=f"{animal_key}_cp")
            st.caption(f"💡 DP ≈ {target_protein * 0.80:.1f}%")
        
        target_se = st.number_input("معادل النشاء (SE)", min_value=10.0, max_value=90.0,
                                    value=float(adjusted_se), step=1.0, key=f"{animal_key}_se")
        
        if protein_basis == "DP":
            actual_dp_target = target_protein
        else:
            actual_dp_target = target_protein * 0.80
        
        multipliers = {"طبيعي": 1.0, "حامل": 1.15, "مرضع": 1.30, "صائم": 0.85,
                       "نشاط مكثف": 1.25, "استشفاء": 1.20, "نمو سريع": 1.35}
        mult = multipliers.get(physiological_state, 1.0)
        actual_dp_target *= mult
        target_se *= mult
        st.caption(f"📌 معامل الحالة: {mult:.2f}")
    
    st.markdown("#### 🌾 اختر المكونات")
    selected_ingredients = []
    ingredient_prices = {}
    
    default_list = {
        "cattle": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                   "أمباز الفول السوداني (كسب)", "مركزات خيول ومجترات", "ملح الطعام",
                   "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)",
                   "بيكربونات الصوديوم (الصودا)"],
        "sheep": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                  "أمباز الفول السوداني (كسب)", "مركزات خيول ومجترات", "ملح الطعام",
                  "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)",
                  "بيكربونات الصوديوم (الصودا)"],
        "goat": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                 "أمباز الفول السوداني (كسب)", "مركزات خيول ومجترات", "ملح الطعام",
                 "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)",
                 "بيكربونات الصوديوم (الصودا)"],
        "horse": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                  "أمباز الفول السوداني (كسب)", "مولاس قصب السكر", "مركزات خيول ومجترات",
                  "ملح الطعام", "الحجر الجيري (بودرة بلاط)",
                  "فوسفات ثنائي الكالسيوم (DCP)"],
        "camel": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                  "أمباز الفول السوداني (كسب)", "البرسيم الجاف (الدريس)",
                  "مركزات خيول ومجترات", "ملح الطعام", "الحجر الجيري (بودرة بلاط)",
                  "فوسفات ثنائي الكالسيوم (DCP)"],
        "poultry": ["ذرة صفراء", "سورجم (فتريتة)", "كسب فول صويا 44%",
                    "كسب جلوتين الذرة 60%", "مركزات دواجن وسمان",
                    "بريمكس تسمين دواجن (Premix)", "ملح الطعام",
                    "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)",
                    "إنزيم الفايتيز الزامي (Phytase Super-D)"],
        "fish": ["ذرة صفراء", "كسب فول صويا 44%", "مسحوق أسماك (Fishmeal 60%)",
                 "كسب جلوتين الذرة 60%", "مركزات دواجن وسمان", "ملح الطعام",
                 "فوسفات ثنائي الكالسيوم (DCP)", "إنزيم الفايتيز الزامي (Phytase Super-D)"]
    }
    
    defaults = default_list.get(animal_key, [])
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=False):
            cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with cols[idx % 3]:
                    checked = st.checkbox(ing_name, value=ing_name in defaults,
                                         key=f"{animal_key}_feed_{ing_name}")
                    if checked:
                        price = st.number_input(
                            f"سعر {ing_name} ($/طن)", min_value=5.0,
                            value=float(250.0 if "نخالة" in ing_name or "ملح" in ing_name else 350.0),
                            key=f"{animal_key}_price_{ing_name}"
                        )
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price
    
    col_btn = st.columns(3)
    with col_btn[0]:
        if st.button(f"🚀 تشغيل المحرك", type="primary",
                     use_container_width=True, key=f"{animal_key}_run"):
            if len(selected_ingredients) < 3:
                st.warning("⚠️ اختر 3 مكونات على الأقل.")
            else:
                voice_guide(f"جاري تشغيل المحرك لـ {display_name}.")
                st.info("🔄 جاري الحساب...")
                
                c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
                bounds = [(0.0, 100.0) for _ in selected_ingredients]
                
                A_eq = [[1.0 for _ in selected_ingredients]]
                b_eq = [100.0]
                
                dp_row = []
                se_row = []
                ndf_row = []
                adf_row = []
                for ing in selected_ingredients:
                    fd = FLAT_FEED_DB.get(ing, {})
                    dp_row.append(fd.get("CP", 0) * fd.get("DC", 0))
                    se_row.append(fd.get("SE", 0))
                    ndf_row.append(fd.get("NDF", 0))
                    adf_row.append(fd.get("ADF", 0))
                
                A_eq.append(dp_row)
                b_eq.append(actual_dp_target * 100.0)
                
                A_ub = []
                b_ub = []
                A_ub.append([-x for x in se_row])
                b_ub.append(-target_se * 100.0)
                
                if animal_key in ["cattle", "sheep", "goat", "camel"]:
                    A_ub.append(ndf_row)
                    b_ub.append(35.0 * 100.0)
                    A_ub.append(adf_row)
                    b_ub.append(20.0 * 100.0)
                elif animal_key == "horse":
                    A_ub.append(ndf_row)
                    b_ub.append(40.0 * 100.0)
                
                if "نخالة قمح (ردة)" in selected_ingredients:
                    idx = selected_ingredients.index("نخالة قمح (ردة)")
                    row = [0.0] * len(selected_ingredients)
                    row[idx] = 1.0
                    A_ub.append(row)
                    b_ub.append(25.0 if animal_key in ["cattle","sheep","goat","camel"] else 15.0)
                
                # إضافات إلزامية
                if animal_key in ["cattle", "sheep", "goat", "camel"]:
                    if "بيكربونات الصوديوم (الصودا)" not in selected_ingredients:
                        selected_ingredients.append("بيكربونات الصوديوم (الصودا)")
                        ingredient_prices["بيكربونات الصوديوم (الصودا)"] = 340.0
                        c_vector.append(340.0)
                        dp_row.append(0.0); se_row.append(0.0)
                        ndf_row.append(0.0); adf_row.append(0.0)
                        bounds.append((0.75, 0.75))
                
                if animal_key in ["poultry", "fish"]:
                    if "إنزيم الفايتيز الزامي (Phytase Super-D)" not in selected_ingredients:
                        selected_ingredients.append("إنزيم الفايتيز الزامي (Phytase Super-D)")
                        ingredient_prices["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 1200.0
                        c_vector.append(1200.0)
                        dp_row.append(0.0); se_row.append(0.0)
                        ndf_row.append(0.0); adf_row.append(0.0)
                        bounds.append((0.05, 0.05))
                
                A_eq = [[1.0 for _ in selected_ingredients], dp_row]
                b_eq = [100.0, actual_dp_target * 100.0]
                
                try:
                    res = linprog(c_vector, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                                 bounds=bounds, method='highs')
                    
                    if res.success:
                        formula_results = {}
                        computed_se_total = 0.0
                        computed_dp_total = 0.0
                        for idx, ing in enumerate(selected_ingredients):
                            if res.x[idx] > 0.0001:
                                formula_results[ing] = res.x[idx]
                                fd = FLAT_FEED_DB.get(ing, {})
                                computed_se_total += (res.x[idx] / 100.0) * fd.get("SE", 0.0)
                                computed_dp_total += (res.x[idx] / 100.0) * fd.get("CP", 0.0) * fd.get("DC", 0.0)
                        
                        ton_cost = res.fun / 100.0
                        standard = STANDARD_VALUES.get(display_name, {}).get(stage, {})
                        warnings_list = []
                        meets = True
                        
                        if standard:
                            if 'DP' in standard:
                                dp_ratio = computed_dp_total / standard['DP'] * 100 if standard['DP'] > 0 else 0
                                if dp_ratio < 75:
                                    meets = False
                                    warnings_list.append(f"DP: {dp_ratio:.1f}% (< 75%)")
                            if 'SE' in standard:
                                se_ratio = computed_se_total / standard['SE'] * 100 if standard['SE'] > 0 else 0
                                if se_ratio < 75:
                                    meets = False
                                    warnings_list.append(f"SE: {se_ratio:.1f}% (< 75%)")
                        
                        if not meets:
                            st.error("❌ الخلطة لا تلبي الحد الأدنى (75%).")
                            for w in warnings_list:
                                st.warning(f"⚠️ {w}")
                        else:
                            st.success(f"✅ التكلفة: ${ton_cost:.2f}/طن")
                            voice_guide(f"تم توليد الخلطة بتكلفة {ton_cost:.2f} دولار")
                            
                            col_res1, col_res2 = st.columns([0.6, 0.4])
                            with col_res1:
                                for k, v in formula_results.items():
                                    st.markdown(f'<div class="formula-item"><span>{k}</span><span>{v:.2f}% ({v*10:.1f} كجم)</span></div>', unsafe_allow_html=True)
                                st.metric("💰 التكلفة", f"${ton_cost:.2f}")
                                st.metric("🧬 DP", f"{computed_dp_total:.2f}%")
                                st.metric("🌽 SE", f"{computed_se_total:.2f}")
                                
                                if requester_name:
                                    st.info(f"👤 {requester_name}")
                                
                                if standard:
                                    comp = []
                                    if 'DP' in standard:
                                        dev = ((computed_dp_total - standard['DP']) / standard['DP']) * 100
                                        g = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                                        comp.append({"المقياس": "DP", "المحسوب": f"{computed_dp_total:.2f}%",
                                                    "القياسي": f"{standard['DP']:.2f}%", "الانحراف": f"{dev:.1f}%", "التقييم": g})
                                    if 'SE' in standard:
                                        dev = ((computed_se_total - standard['SE']) / standard['SE']) * 100
                                        g = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                                        comp.append({"المقياس": "SE", "المحسوب": f"{computed_se_total:.2f}",
                                                    "القياسي": f"{standard['SE']:.2f}", "الانحراف": f"{dev:.1f}%", "التقييم": g})
                                    st.table(pd.DataFrame(comp))
                                
                                try:
                                    pdf_data = pdf_generator.generate_comprehensive_report(
                                        formula_results, computed_dp_total,
                                        f"{breed} - {stage} ({physiological_state})",
                                        ton_cost, "الموقع", ton_cost*600, "SDG", computed_se_total,
                                        user_name=st.session_state.get("user", {}).get("full_name", "مستخدم"),
                                        requester_name=requester_name, standard=standard,
                                        include_charts=True,
                                        extra_info={"السلالة": breed, "المرحلة": stage, "الحالة": physiological_state}
                                    )
                                    st.download_button("📥 تحميل PDF", pdf_data,
                                                     file_name=f"Tawornology_{display_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                                     mime="application/pdf", use_container_width=True,
                                                     key=f"{animal_key}_pdf")
                                except Exception as e:
                                    st.warning(f"⚠️ {e}")
                            
                            with col_res2:
                                if len(formula_results) > 1:
                                    fig = px.pie(values=list(formula_results.values()),
                                                names=list(formula_results.keys()),
                                                title="توزيع المكونات",
                                                color_discrete_sequence=px.colors.sequential.Greens)
                                    fig.update_layout(height=400)
                                    st.plotly_chart(fig, use_container_width=True)
                            
                            st.session_state["active_formula"] = formula_results
                            st.session_state["active_cp_tag"] = computed_dp_total
                            st.session_state["active_se_tag"] = computed_se_total
                            st.session_state["active_breed_tag"] = f"{breed} - {stage}"
                            st.session_state["computed_ton_cost"] = ton_cost
                    else:
                        st.error("❌ تعذر إيجاد حل. حاول إضافة مكونات.")
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")
    
    with col_btn[1]:
        if st.button(f"📋 عرض المعايير", use_container_width=True, key=f"{animal_key}_std"):
            std = STANDARD_VALUES.get(display_name, {}).get(stage, {})
            if std:
                st.info(f"📊 DP={std.get('DP','-')}%, SE={std.get('SE','-')}, CP={std.get('CP','-')}%")
    
    with col_btn[2]:
        if st.button(f"🔊 استماع", use_container_width=True, key=f"{animal_key}_help"):
            voice_guide(f"مرحباً بك في قسم {display_name}.")

# =====================================================================
# معادلات NRC
# =====================================================================
def render_nrc_equations(animal_type="أبقار"):
    st.markdown("### 🧮 معادلات NRC المتقدمة")
    
    c1, c2 = st.columns(2)
    with c1:
        weight = st.number_input("⚖️ الوزن (كجم):", min_value=10.0,
                                 value=450.0 if animal_type == "أبقار" else 60.0,
                                 step=5.0, key=f"nrc_w_{animal_type}")
        prod_type = st.radio("الإنتاج:", ["🥛 حليب", "📈 تسمين"],
                             horizontal=True, key=f"nrc_t_{animal_type}")
    with c2:
        if prod_type == "🥛 حليب":
            milk = st.number_input("🥛 الحليب (لتر):", min_value=0.0,
                                   value=20.0 if animal_type == "أبقار" else 2.0,
                                   step=0.5, key=f"nrc_m_{animal_type}")
            fat = st.slider("دهن (%)", 2.5, 6.0, 3.5, 0.1, key=f"nrc_f_{animal_type}")
        else:
            gain = st.number_input("📈 الزيادة (كجم):", min_value=0.0,
                                   value=1.0 if animal_type == "أبقار" else 0.15,
                                   step=0.05, key=f"nrc_g_{animal_type}")
    
    if st.button("🧮 حساب", type="primary", key=f"nrc_calc_{animal_type}"):
        if prod_type == "🥛 حليب":
            pr = AdvancedProductionEquations.calculate_total_protein_for_dairy(weight, milk, fat)
            er = AdvancedProductionEquations.calculate_energy_for_dairy(weight, milk, fat)
            ratio = AdvancedProductionEquations.calculate_protein_energy_ratio(pr['total'], er['total_energy'])
            st.success("✅ NRC 2001")
            c1, c2, c3 = st.columns(3)
            c1.metric("DP", f"{pr['dp_requirement']:.2f}%")
            c2.metric("SE", f"{er['se_requirement']:.0f}")
            c3.metric("SE/DP", f"{ratio:.2f}")
        else:
            pr = AdvancedProductionEquations.calculate_total_protein_for_fattening(weight, gain)
            er = AdvancedProductionEquations.calculate_total_energy_for_fattening(weight, gain)
            ratio = AdvancedProductionEquations.calculate_protein_energy_ratio(pr['total'], er['total_energy'])
            st.success("✅ NRC 2000")
            c1, c2, c3 = st.columns(3)
            c1.metric("DP", f"{pr['dp_requirement']:.2f}%")
            c2.metric("SE", f"{er['se_requirement']:.0f}")
            c3.metric("SE/DP", f"{ratio:.2f}")

# =====================================================================
# المختبر الذكي
# =====================================================================
def render_smart_ocr_lab():
    st.markdown('<div class="section-title">📸 المختبر الذكي</div>', unsafe_allow_html=True)
    
    if not OCR_AVAILABLE and not EASYOCR_AVAILABLE:
        st.warning("⚠️ مكتبات OCR غير مثبتة. `pip install easyocr pytesseract`")
    
    col_up, col_info = st.columns([2, 1])
    with col_up:
        uploaded = st.file_uploader("ارفع صورة التركيبة", type=['png', 'jpg', 'jpeg', 'bmp'],
                                    key="ocr_upload")
        if uploaded:
            try:
                img = PILImage.open(uploaded)
                st.image(img, caption="الصورة", use_container_width=True)
                if st.button("🔍 تحليل الصورة", type="primary", key="ocr_analyze"):
                    if st.session_state.get("smart_lab"):
                        with st.spinner("جاري التحليل..."):
                            res, err = st.session_state["smart_lab"].analyze_image(img)
                            if err:
                                st.error(f"❌ {err}")
                            else:
                                st.success("✅ تم التحليل!")
                                st.session_state["ocr_result"] = res
                                voice_guide("تم تحليل الصورة")
            except Exception as e:
                st.error(f"خطأ: {e}")
    
    with col_info:
        st.markdown("""
        <div style='background:#e3f2fd; padding:15px; border-radius:10px; direction:rtl;'>
        <h4>💡 نصائح:</h4>
        <ul>
        <li>صورة واضحة ومستقيمة</li>
        <li>إضاءة جيدة</li>
        <li>يدعم العربية والإنجليزية</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    ocr_data = st.session_state.get("ocr_result", {})
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("اسم العينة:", value=ocr_data.get('sample_name', ''), key="ocr_name")
        st.number_input("CP %:", value=float(ocr_data.get('cp') or 0.0), step=0.1, key="ocr_cp")
        st.number_input("DC:", min_value=0.0, max_value=1.0, value=float(ocr_data.get('dc') or 0.0), step=0.01, key="ocr_dc")
        st.number_input("SE:", value=float(ocr_data.get('se') or 0.0), step=0.1, key="ocr_se")
    with c2:
        st.number_input("NDF %:", value=float(ocr_data.get('ndf') or 0.0), step=0.1, key="ocr_ndf")
        st.number_input("ADF %:", value=float(ocr_data.get('adf') or 0.0), step=0.1, key="ocr_adf")
        st.number_input("EE %:", value=float(ocr_data.get('ee') or 0.0), step=0.1, key="ocr_ee")
        st.number_input("ASH %:", value=float(ocr_data.get('ash') or 0.0), step=0.1, key="ocr_ash")
    
    if st.button("💾 حفظ النتيجة", type="secondary", key="ocr_save"):
        if st.session_state.get("smart_lab"):
            data = {
                'sample_name': st.session_state.get('ocr_name', ''),
                'cp': st.session_state.get('ocr_cp', 0.0),
                'dc': st.session_state.get('ocr_dc', 0.0),
                'se': st.session_state.get('ocr_se', 0.0),
                'ndf': st.session_state.get('ocr_ndf', 0.0),
                'adf': st.session_state.get('ocr_adf', 0.0),
                'ee': st.session_state.get('ocr_ee', 0.0),
                'ash': st.session_state.get('ocr_ash', 0.0),
                'analyzed_by': st.session_state.get("user", {}).get("full_name", "مستخدم"),
                'notes': ''
            }
            rid = st.session_state["smart_lab"].save_lab_result(data)
            st.success(f"✅ تم الحفظ! {rid[:8]}")

# =====================================================================
# المختبر المتقدم
# =====================================================================
def render_advanced_lab():
    st.markdown('<div class="section-title">🔬 المختبر المتقدم</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        lab_animal = st.selectbox("الفصيل:", ["أبقار", "أغنام", "ماعز", "خيول", "إبل", "دواجن", "أسماك"],
                                  key="lab_animal")
        stages = list(STANDARD_VALUES.get(lab_animal, {}).keys())
        lab_stage = st.selectbox("المرحلة:", stages if stages else ["عام"], key="lab_stage")
        standard = STANDARD_VALUES.get(lab_animal, {}).get(lab_stage, {})
        if standard:
            st.info(f"📊 DP={standard.get('DP','-')}%, SE={standard.get('SE','-')}, CP={standard.get('CP','-')}%")
    
    lab_inputs = {}
    cols = st.columns(3)
    all_ings = list(FLAT_FEED_DB.keys())
    for idx, ing in enumerate(all_ings):
        with cols[idx % 3]:
            lab_inputs[ing] = st.number_input(f"{ing} (كجم)", min_value=0.0, value=0.0,
                                              step=5.0, key=f"lab_in_{ing}")
    
    if st.button("🧪 تشغيل التحليل", type="primary", use_container_width=True, key="lab_run"):
        total = sum(lab_inputs.values())
        if total <= 0:
            st.warning("⚠️ أدخل أوزاناً.")
        else:
            cp_total, dp_total, se_total = 0.0, 0.0, 0.0
            for ing, weight in lab_inputs.items():
                if weight > 0:
                    pct = weight / total
                    fd = FLAT_FEED_DB.get(ing, {})
                    cp_total += pct * fd.get("CP", 0)
                    dp_total += pct * fd.get("CP", 0) * fd.get("DC", 0)
                    se_total += pct * fd.get("SE", 0)
            
            st.session_state["analysis_results"] = {'cp': cp_total, 'dp': dp_total, 'se': se_total}
            
            st.success("🔬 تم التحليل!")
            col_res = st.columns(3)
            col_res[0].metric("CP", f"{cp_total:.2f}%")
            col_res[1].metric("DP", f"{dp_total:.2f}%")
            col_res[2].metric("SE", f"{se_total:.2f}")
            
            if standard:
                dp_dev = ((dp_total - standard.get('DP', 0)) / standard.get('DP', 1)) * 100 if standard.get('DP', 0) > 0 else 0
                se_dev = ((se_total - standard.get('SE', 0)) / standard.get('SE', 1)) * 100 if standard.get('SE', 0) > 0 else 0
                cp_dev = ((cp_total - standard.get('CP', 0)) / standard.get('CP', 1)) * 100 if standard.get('CP', 0) > 0 else 0
                
                grade_dp = "✅" if abs(dp_dev) <= 5 else ("⚠️" if abs(dp_dev) <= 10 else "❌")
                grade_se = "✅" if abs(se_dev) <= 5 else ("⚠️" if abs(se_dev) <= 10 else "❌")
                grade_cp = "✅" if abs(cp_dev) <= 5 else ("⚠️" if abs(cp_dev) <= 10 else "❌")
                
                eval_df = pd.DataFrame([
                    {"المقياس": "DP", "المحسوب": f"{dp_total:.2f}%", "القياسي": f"{standard.get('DP', 0):.2f}%", "الانحراف": f"{dp_dev:.1f}%", "التقييم": grade_dp},
                    {"المقياس": "SE", "المحسوب": f"{se_total:.2f}", "القياسي": f"{standard.get('SE', 0):.2f}", "الانحراف": f"{se_dev:.1f}%", "التقييم": grade_se},
                    {"المقياس": "CP", "المحسوب": f"{cp_total:.2f}%", "القياسي": f"{standard.get('CP', 0):.2f}%", "الانحراف": f"{cp_dev:.1f}%", "التقييم": grade_cp}
                ])
                st.table(eval_df)
                
                # رسم بياني
                fig = go.Figure()
                fig.add_trace(go.Bar(x=['DP', 'SE', 'CP'], y=[dp_total, se_total, cp_total],
                                     name='المحسوب', marker_color='#2e7d32'))
                fig.add_trace(go.Bar(x=['DP', 'SE', 'CP'],
                                     y=[standard.get('DP',0), standard.get('SE',0), standard.get('CP',0)],
                                     name='القياسي', marker_color='#1565C0'))
                fig.update_layout(title="مقارنة النتائج", barmode='group', height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                try:
                    pdf_data = pdf_generator.generate_lab_report(
                        st.session_state["analysis_results"], lab_animal, lab_stage,
                        st.session_state.get("user", {}).get("full_name", "مستخدم"),
                        standard, {'DP': grade_dp, 'SE': grade_se, 'CP': grade_cp}
                    )
                    st.download_button("📥 تحميل PDF", pdf_data,
                                     file_name=f"Lab_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                     mime="application/pdf", key="lab_pdf")
                except Exception as e:
                    st.warning(f"⚠️ {e}")

# =====================================================================
# بدائل الحليب
# =====================================================================
def render_milk_replacer():
    st.markdown('<div class="section-title">🍼 تركيب بديل الحليب</div>', unsafe_allow_html=True)
    
    animal_type = st.selectbox("الحيوان:", ["عجل بقري", "حملان", "جديان", "مهرات", "أطفال إبل"],
                               key="mr_animal")
    age_days = st.slider("العمر (يوم)", 1, 120, 30, 1, key="mr_age")
    
    needs = {
        "عجل بقري": {"protein": 22, "fat": 18, "energy": 75, "volume": 8},
        "حملان": {"protein": 24, "fat": 20, "energy": 72, "volume": 4},
        "جديان": {"protein": 23, "fat": 19, "energy": 70, "volume": 3},
        "مهرات": {"protein": 20, "fat": 15, "energy": 68, "volume": 5},
        "أطفال إبل": {"protein": 21, "fat": 17, "energy": 66, "volume": 6}
    }
    
    age_factor = 1.2 if age_days < 14 else (1.0 if age_days < 30 else (0.85 if age_days < 60 else 0.70))
    
    target_protein = needs[animal_type]["protein"] * age_factor
    target_fat = needs[animal_type]["fat"] * age_factor
    target_energy = needs[animal_type]["energy"] * age_factor
    daily_volume = needs[animal_type]["volume"] * age_factor
    
    st.info(f"📊 بروتين {target_protein:.1f}% | دهون {target_fat:.1f}% | طاقة {target_energy:.1f} | {daily_volume:.1f} لتر/يوم")
    
    ingredients = {
        "حليب مجفف خالي الدسم": {"CP": 34.0, "Fat": 1.0, "SE": 40.0, "Cost": 18.0},
        "مصل الحليب المجفف (Whey)": {"CP": 12.0, "Fat": 1.0, "SE": 35.0, "Cost": 12.0},
        "دهن نباتي (زيت نباتي)": {"CP": 0.0, "Fat": 99.0, "SE": 10.0, "Cost": 8.0},
        "ليسيثين الصويا": {"CP": 0.0, "Fat": 95.0, "SE": 0.0, "Cost": 15.0},
        "بروتين الصويا المركز": {"CP": 65.0, "Fat": 1.0, "SE": 30.0, "Cost": 20.0},
        "فيتامينات ومعادن (Premix)": {"CP": 0.0, "Fat": 0.0, "SE": 0.0, "Cost": 25.0}
    }
    
    selected = []
    prices = {}
    cols = st.columns(3)
    for i, (ing, data) in enumerate(ingredients.items()):
        with cols[i % 3]:
            if st.checkbox(ing, value=(i < 4), key=f"mr_{ing}"):
                selected.append(ing)
                prices[ing] = st.number_input(f"سعر {ing} ($/كجم)", min_value=1.0,
                                              value=float(data["Cost"]), step=0.5,
                                              key=f"mr_price_{ing}")
    
    if st.button("🍼 تشغيل المحرك", type="primary", key="mr_run"):
        if len(selected) < 3:
            st.warning("⚠️ اختر 3 مكونات على الأقل")
        else:
            with st.spinner("جاري الحساب..."):
                try:
                    c = [prices[ing] for ing in selected]
                    bounds = [(0, 100) for _ in selected]
                    protein_row = [ingredients[ing]["CP"] for ing in selected]
                    fat_row = [ingredients[ing]["Fat"] for ing in selected]
                    energy_row = [ingredients[ing]["SE"] for ing in selected]
                    
                    A_eq = [[1] * len(selected)]
                    b_eq = [100]
                    
                    A_ub = [fat_row, [-x for x in energy_row]]
                    b_ub = [target_fat * 1.1, -target_energy * 0.85]
                    
                    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                                 bounds=bounds, method='highs')
                    
                    if res.success:
                        formula = {selected[i]: res.x[i] for i in range(len(selected)) if res.x[i] > 0.0001}
                        cost_kg = res.fun / 100.0
                        
                        st.success(f"✅ التكلفة: ${cost_kg:.2f}/كجم")
                        for k, v in formula.items():
                            st.markdown(f'<div class="formula-item"><span>{k}</span><span>{v:.1f}% ({v*10:.1f} جم/كجم)</span></div>', unsafe_allow_html=True)
                        
                        instructions = f"""الجرعة اليومية: {daily_volume:.1f} لتر مقسمة على 3-4 وجبات
التركيز: 100-150 جم مسحوق لكل لتر ماء دافئ
درجة الحرارة: 38-40 درجة مئوية"""
                        
                        try:
                            pdf_data = pdf_generator.generate_milk_replacer_report(
                                formula, animal_type, age_days, instructions,
                                st.session_state.get("user", {}).get("full_name", "مستخدم")
                            )
                            st.download_button("📥 تحميل PDF", pdf_data,
                                             file_name=f"Milk_Replacer_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                             mime="application/pdf", key="mr_pdf")
                        except Exception as e:
                            st.warning(f"⚠️ {e}")
                except Exception as e:
                    st.error(f"❌ {e}")

# =====================================================================
# مواقيت الصلاة
# =====================================================================
def prayer_time_reminder():
    st.markdown("### 🕌 مواقيت الصلاة")
    cities = ["مكة المكرمة", "المدينة المنورة", "الخرطوم", "طرابلس", "القاهرة",
              "دبي", "الرياض", "بغداد", "الكويت", "الدوحة"]
    city = st.selectbox("المدينة:", cities, key="pt_city")
    
    times = {"الفجر": "05:00", "الشروق": "06:30", "الظهر": "12:00",
             "العصر": "15:30", "المغرب": "18:00", "العشاء": "19:30"}
    
    cols = st.columns(3)
    for i, (name, t) in enumerate(times.items()):
        with cols[i % 3]:
            st.metric(name, t)

# =====================================================================
# منبه الجرعات
# =====================================================================
def render_dose_reminder():
    st.markdown("### 💊 منبه الجرعات")
    
    if st.session_state.get("dose_reminders"):
        st.subheader("📋 الجرعات المسجلة")
        for r in st.session_state["dose_reminders"]:
            with st.expander(f"💊 {r['dose_name']} - {r['animal_type']}"):
                st.write(f"**الجرعة:** {r['dose_amount']} {r['dose_unit']}")
                st.write(f"**الطريقة:** {r['administration_route']}")
                st.write(f"**التكرار:** كل {r['frequency_days']} يوم")
    
    with st.expander("➕ إضافة جرعة جديدة", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            at = st.selectbox("الحيوان:", ["أبقار", "أغنام", "ماعز", "خيول", "إبل", "دواجن"], key="dr_at")
            dt = st.selectbox("النوع:", ["لقاح", "فيتامين", "دواء"], key="dr_dt")
            dn = st.text_input("الاسم:", key="dr_dn")
        with c2:
            da = st.number_input("الجرعة:", min_value=0.0, value=1.0, key="dr_da")
            du = st.selectbox("الوحدة:", ["مل", "جم", "مجم"], key="dr_du")
            ar = st.selectbox("الطريقة:", ["عضل", "تحت الجلد", "فموي", "مياه الشرب"], key="dr_ar")
        with c3:
            fd = st.number_input("التكرار (أيام):", min_value=1, value=7, key="dr_fd")
            sd = st.date_input("البدء:", datetime.now(), key="dr_sd")
        
        if st.button("💾 حفظ", key="dr_save"):
            if dn:
                st.session_state["dose_reminders"].append({
                    'id': secrets.token_hex(8),
                    'animal_type': at, 'dose_type': dt, 'dose_name': dn,
                    'dose_amount': da, 'dose_unit': du,
                    'administration_route': ar, 'frequency_days': fd,
                    'start_date': sd.isoformat(),
                    'next_dose_date': (sd + timedelta(days=fd)).isoformat()
                })
                st.success(f"✅ تم إضافة {dn}")
                st.rerun()

print("✅ الجزء 3/3 تم التحميل - الواجهة الكاملة")

# =====================================================================
# التبويبات حسب الصلاحية
# =====================================================================
user_role = st.session_state.get("user_role", "public")

if user_role == "owner":
    tabs_titles = [
        "🐾 تركيب الأعلاف",
        "📸 المختبر الذكي",
        "🐔 إدارة المزارع",
        "🍼 بدائل الحليب",
        "🕌 مواقيت الصلاة",
        "💊 منبه الجرعات",
        "📊 بورصة الأسعار",
        "🏭 المستودعات",
        "📈 الإنتاج اليومي",
        "📚 المراجع العلمية",
        "💬 التعليقات",
        "💡 المساعدة",
        "📖 دليل المستخدم",
        "📧 إرسال الكود"
    ]
else:
    tabs_titles = [
        "🐾 تركيب الأعلاف",
        "📸 المختبر الذكي",
        "📚 المراجع العلمية",
        "💡 المساعدة",
        "📖 دليل المستخدم"
    ]
    st.info("""
    👋 **مرحباً بك كزائر!**
    
    **متاح للزوار:** تركيب الأعلاف، المختبر الذكي، المراجع، المساعدة، الدليل
    
    🔒 **حصرية للمالك:** إدارة المزارع، بدائل الحليب، مواقيت الصلاة، منبه الجرعات،
    بورصة الأسعار، المستودعات، الإنتاج اليومي، التعليقات، إرسال الكود
    """)

tabs = st.tabs(tabs_titles)

tab_map = {title: i for i, title in enumerate(tabs_titles)}

# =====================================================================
# تبويب 0: تركيب الأعلاف
# =====================================================================
with tabs[0]:
    guide_section("تركيب الأعلاف", "اختر نوع الحيوان، أدخل البيانات، ثم شغّل المحرك.")
    
    animal_tabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐴 خيول",
                            "🐫 إبل", "🐔 دواجن", "🐟 أسماك", "🔬 المختبر المتقدم"])
    
    with animal_tabs[0]:
        render_feed_formulation("cattle", "أبقار", "🐄",
            ["كنانة (سوداني)", "بطانة (مدر)", "هولشتاين / محسن"],
            ["تسمين عجول", "حليب/إدرار", "حمل/دفع غذائي", "صيانة", "تسمين مكثف"],
            12.0, 65.0, has_measurements=True)
        st.markdown("---")
        render_nrc_equations("أبقار")
    
    with animal_tabs[1]:
        render_feed_formulation("sheep", "أغنام", "🐏",
            ["الضأن الصحراوي", "البربري", "النعيمي"],
            ["تسمين حملان", "نعاج مرضعات", "نعاج حامل", "نعاج جافة"],
            11.5, 62.0, has_measurements=True)
        st.markdown("---")
        render_nrc_equations("أغنام")
    
    with animal_tabs[2]:
        render_feed_formulation("goat", "ماعز", "🐐",
            ["الماعز النوبي", "الماعز الصحراوي", "بور / محسن"],
            ["تسمين جديان", "عنزات حلابة", "عنزات حامل", "صيانة"],
            11.0, 60.0, has_measurements=True)
        st.markdown("---")
        render_nrc_equations("ماعز")
    
    with animal_tabs[3]:
        render_feed_formulation("horse", "خيول", "🐴",
            ["خيل عربي أصيل", "ثوروبريد", "خيول محلية"],
            ["راحة/صيانة", "عمل خفيف", "عمل متوسط", "عمل مكثف", "سباق",
             "أمهار نامية", "فرسات مرضعات"],
            11.0, 62.0, has_measurements=True)
    
    with animal_tabs[4]:
        render_feed_formulation("camel", "إبل", "🐫",
            ["عربية (دروميداري)", "باختري", "هجين"],
            ["راحة/صيانة", "حمل/رضاعة", "إنتاج حليب", "تسمين", "عمل/نقل"],
            10.0, 58.0, has_measurements=True)
    
    with animal_tabs[5]:
        render_feed_formulation("poultry", "دواجن", "🐔",
            ["دواجن لاحم", "دواجن بياض", "طائر السمان"],
            ["بادي (0-14 يوم)", "نامي (15-28 يوم)", "ناهي (29-42 يوم)", "ناهي متقدم"],
            18.0, 72.0, has_measurements=False)
    
    with animal_tabs[6]:
        render_feed_formulation("fish", "أسماك", "🐟",
            ["البلطي النيلي", "القرموط"],
            ["زريعة/بادئ", "نمو", "تسمين نهائي", "زريعة متقدمة"],
            28.0, 68.0, has_measurements=False)
    
    with animal_tabs[7]:
        render_advanced_lab()

# =====================================================================
# تبويب 1: المختبر الذكي
# =====================================================================
with tabs[1]:
    guide_section("المختبر الذكي", "ارفع صورة التركيبة لاستخراج القيم.")
    render_smart_ocr_lab()

# =====================================================================
# التبويبات الأخرى للمالك فقط
# =====================================================================
if user_role == "owner":
    # إدارة المزارع
    with tabs[tab_map["🐔 إدارة المزارع"]]:
        guide_section("إدارة المزارع", "إدارة دورات الدجاج اللاحم.")
        st.markdown('<div class="section-title">🐔 إدارة مزارع الدجاج</div>', unsafe_allow_html=True)
        
        with st.expander("➕ إضافة دورة جديدة", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                fn = st.text_input("اسم المزرعة", key="bf_fn")
                ib = st.number_input("عدد الكتاكيت", min_value=1, value=1000, step=100, key="bf_ib")
            with c2:
                br = st.selectbox("السلالة", ["Ross 308", "Cobb 500", "محلية"], key="bf_br")
            
            if st.button("💾 إنشاء الدورة", key="bf_create"):
                if fn:
                    cid = secrets.token_hex(8)
                    st.session_state["broiler_farms"][cid] = {
                        "farm_name": fn, "initial_birds": ib, "breed": br,
                        "age_days": 0, "current_weight": 0.045,
                        "total_feed": 0, "dead_count": 0
                    }
                    st.success(f"✅ تم إنشاء {fn}")
                    st.rerun()
        
        if st.session_state["broiler_farms"]:
            for cid, farm in st.session_state["broiler_farms"].items():
                with st.expander(f"🏠 {farm['farm_name']} - {farm['breed']}"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("العدد", farm['initial_birds'])
                        st.metric("العمر", farm['age_days'])
                    with c2:
                        st.metric("الوزن", f"{farm['current_weight']:.3f}")
                        st.metric("العلف", f"{farm['total_feed']:.1f}")
                    with c3:
                        mort = (farm['dead_count'] / farm['initial_birds']) * 100 if farm['initial_birds'] > 0 else 0
                        st.metric("النفوق %", f"{mort:.1f}")
                        st.metric("النافق", farm['dead_count'])
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        nw = st.number_input("الوزن الحالي", min_value=0.01,
                                             value=float(farm['current_weight']),
                                             step=0.01, key=f"w_{cid}")
                        nf = st.number_input("العلف", min_value=0.0,
                                             value=float(farm['total_feed']),
                                             step=1.0, key=f"f_{cid}")
                    with c2:
                        nd = st.number_input("النافق الإضافي", min_value=0,
                                             value=0, step=1, key=f"d_{cid}")
                        na = st.number_input("العمر", min_value=0,
                                             value=int(farm['age_days']),
                                             step=1, key=f"a_{cid}")
                    
                    if st.button(f"📊 تحديث", key=f"up_{cid}"):
                        farm['current_weight'] = nw
                        farm['total_feed'] = nf
                        farm['dead_count'] += nd
                        farm['age_days'] = na
                        st.success("✅ تم التحديث")
                        st.rerun()
    
    # بدائل الحليب
    with tabs[tab_map["🍼 بدائل الحليب"]]:
        guide_section("بدائل الحليب", "تركيب بدائل الحليب.")
        render_milk_replacer()
    
    # مواقيت الصلاة
    with tabs[tab_map["🕌 مواقيت الصلاة"]]:
        guide_section("مواقيت الصلاة", "مواقيت الصلاة حسب المدينة.")
        prayer_time_reminder()
    
    # منبه الجرعات
    with tabs[tab_map["💊 منبه الجرعات"]]:
        guide_section("منبه الجرعات", "تسجيل جرعات اللقاحات.")
        render_dose_reminder()
    
    # بورصة الأسعار
    with tabs[tab_map["📊 بورصة الأسعار"]]:
        guide_section("بورصة الأسعار", "أسعار المواشي والمنتجات.")
        st.markdown('<div class="section-title">📊 بورصة الأسعار</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🐄 المواشي")
            for name, price in list(st.session_state["global_livestock_prices"].items()):
                np = st.number_input(name, value=float(price), step=5.0, key=f"pl_{name}")
                st.session_state["global_livestock_prices"][name] = np
        with c2:
            st.subheader("🥩 المنتجات")
            for name, price in list(st.session_state["global_products_prices"].items()):
                np = st.number_input(name, value=float(price), step=0.5, key=f"pp_{name}")
                st.session_state["global_products_prices"][name] = np
    
    # المستودعات
    with tabs[tab_map["🏭 المستودعات"]]:
        guide_section("المستودعات", "إدارة المخزون.")
        st.markdown('<div class="section-title">🏭 المستودعات</div>', unsafe_allow_html=True)
        inv_data = []
        for item, data in st.session_state["inventory"].items():
            qty = data["quantity"] if isinstance(data, dict) else data
            status = "🔴" if qty <= 0 else "🟠" if qty < 5 else "🟢"
            inv_data.append({"المادة": item, "الكمية (طن)": qty, "الحالة": status})
        st.dataframe(pd.DataFrame(inv_data), use_container_width=True)
        
        with st.expander("تحديث المخزون", expanded=False):
            sel = st.selectbox("المادة", list(FLAT_FEED_DB.keys()), key="inv_sel")
            nq = st.number_input("الكمية الجديدة", min_value=0.0, value=25.0, key="inv_qty")
            if st.button("تحديث", key="inv_upd"):
                if isinstance(st.session_state["inventory"][sel], dict):
                    st.session_state["inventory"][sel]["quantity"] = nq
                else:
                    st.session_state["inventory"][sel] = nq
                st.success("✅ تم التحديث")
                st.rerun()
    
    # الإنتاج اليومي
    with tabs[tab_map["📈 الإنتاج اليومي"]]:
        guide_section("الإنتاج اليومي", "تسجيل بيانات الإنتاج.")
        st.markdown('<div class="section-title">📈 الإنتاج اليومي</div>', unsafe_allow_html=True)
        
        with st.form("daily_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                farm = st.text_input("المزرعة", key="dp_farm")
                date = st.date_input("التاريخ", datetime.now(), key="dp_date")
            with c2:
                milk = st.number_input("الحليب (لتر)", min_value=0.0, value=0.0, key="dp_milk")
                eggs = st.number_input("البيض", min_value=0, value=0, key="dp_eggs")
            with c3:
                wg = st.number_input("زيادة الوزن", min_value=0.0, value=0.0, key="dp_wg")
                dead = st.number_input("النافق", min_value=0, value=0, key="dp_dead")
            
            if st.form_submit_button("💾 حفظ"):
                st.session_state["daily_production_log"].append({
                    "farm": farm, "date": date.isoformat(), "milk": milk,
                    "eggs": eggs, "weight_gain": wg, "mortality": dead
                })
                st.success("✅ تم الحفظ")
        
        if st.session_state["daily_production_log"]:
            st.dataframe(pd.DataFrame(st.session_state["daily_production_log"]),
                        use_container_width=True)
    
    # التعليقات
    with tabs[tab_map["💬 التعليقات"]]:
        guide_section("التعليقات", "قناة لتبادل الخبرات.")
        st.markdown('<div class="section-title">💬 تعليقات المختصين</div>', unsafe_allow_html=True)
        st.text_area("التعليقات:", value=st.session_state["shared_comments"],
                     height=200, disabled=True, key="comments_display")
        nc = st.text_area("إضافة تعليق:", key="new_comment")
        if st.button("➕ نشر", key="post_comment"):
            if nc:
                st.session_state["shared_comments"] += f"\n• [المالك {datetime.now().strftime('%Y-%m-%d %H:%M')}]: {nc}"
                st.success("تم النشر!")
                st.rerun()
    
    # إرسال الكود
    with tabs[tab_map["📧 إرسال الكود"]]:
        guide_section("إرسال الكود", "إرسال السورس كود إلى البريد.")
        st.markdown('<div class="section-title">📧 إرسال السورس كود</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background:linear-gradient(135deg,#e3f2fd,#bbdefb); padding:18px; border-radius:14px; direction:rtl; margin-bottom:20px;'>
        <b>📌 للحصول على App Password من Google:</b><br>
        1. اذهب إلى <b>myaccount.google.com/apppasswords</b><br>
        2. أنشئ كلمة مرور جديدة للتطبيق<br>
        3. انسخها (16 حرفاً) والصقها هنا
        </div>
        """, unsafe_allow_html=True)
        
        email_in = st.text_input("📧 البريد:", value=OWNER_EMAIL, key="send_email_final")
        pass_in = st.text_input("🔑 كلمة مرور التطبيق:", type="password",
                                placeholder="16 حرفاً بدون مسافات", key="send_pass_final")
        
        if st.button("📤 إرسال الكود", type="primary", use_container_width=True, key="send_final"):
            if not email_in or '@' not in email_in:
                st.error("⚠️ بريد غير صحيح")
            elif not pass_in:
                st.error("⚠️ أدخل كلمة مرور التطبيق")
            else:
                with st.spinner("⏳ جاري الإرسال..."):
                    success, msg = send_code_to_email(email_in, pass_in)
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)

# =====================================================================
# التبويبات المشتركة (للمالك والزوار)
# =====================================================================
ref_key = "📚 المراجع العلمية"
if ref_key in tab_map:
    with tabs[tab_map[ref_key]]:
        guide_section("المراجع العلمية", "مصادر معتمدة في تغذية الحيوان.")
        st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
        
        for cat_key, cat_data in ScientificReferenceSystem.REFERENCES.items():
            with st.expander(f"{cat_data['icon']} {cat_data['title']}"):
                for ref in cat_data.get("references", []):
                    st.markdown(f"""
                    <div style='background:#f8f9fa; padding:12px; border-radius:8px; margin-bottom:8px; border-right:4px solid #2e7d32;'>
                        <b>{ref.get('title', 'عنوان')}</b><br>
                        👤 {ref.get('authors', 'مؤلف')}<br>
                        📅 {ref.get('year', 'سنة')} | 📚 {ref.get('publisher', 'ناشر')}<br>
                        <small>{ref.get('summary', '')}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.subheader("💡 المعرفة السريعة")
        q = st.text_input("اسأل عن مصطلح:", key="kb_q")
        if q:
            ans = ScientificReferenceSystem.get_knowledge_answer(q)
            if ans:
                st.success(f"📖 {ans['answer']}")

help_key = "💡 المساعدة"
if help_key in tab_map:
    with tabs[tab_map[help_key]]:
        guide_section("المساعدة", "دليل سريع.")
        st.markdown('<div class="section-title">💡 المساعدة</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#e3f2fd; padding:20px; border-radius:12px; direction:rtl;'>
        <h3>🌟 خطوات الاستخدام:</h3>
        <ol>
        <li>اختر نوع الحيوان من التبويب الأول</li>
        <li>حدد السلالة والمرحلة الإنتاجية</li>
        <li>أدخل القياسات الجسدية (إن توفرت)</li>
        <li>اختر المكونات العلفية وحدد أسعارها</li>
        <li>اضغط "تشغيل المحرك"</li>
        <li>احصل على الخلطة + تقرير PDF</li>
        </ol>
        <h3>📞 الدعم الفني:</h3>
        <p>abukram128@gmail.com | +249123533489</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔊 استماع للتعليمات", key="help_voice"):
            voice_guide("مرحباً، هذا دليل استخدام منصة تاور نولجي العلمية.")

guide_key = "📖 دليل المستخدم"
if guide_key in tab_map:
    with tabs[tab_map[guide_key]]:
        guide_section("دليل المستخدم", "شرح مفصل للمنصة.")
        st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="manual-book">
        <div class="book-chapter">📘 الفصل 1: مقدمة</div>
        <div class="book-body">
        تاور نولجي Tawornology العلمية منصة متكاملة لتركيب الأعلاف وإدارة الإنتاج الحيواني.
        تعتمد على البرمجة الخطية لحساب أقل تكلفة لخلطة علفية تلبي الاحتياجات الغذائية.
        </div>
        
        <div class="book-chapter">📗 الفصل 2: تركيب العلف</div>
        <div class="book-body">
        1. اختر نوع الحيوان.<br>
        2. حدد السلالة والمرحلة.<br>
        3. أدخل العمر والحالة.<br>
        4. اختر المكونات وأسعارها.<br>
        5. اضغط "تشغيل المحرك".<br>
        6. حمل PDF.
        </div>
        
        <div class="book-chapter">📕 الفصل 3: المختبر الذكي</div>
        <div class="book-body">
        ارفع صورة تركيبة علفية واستخرج القيم الغذائية تلقائياً.
        </div>
        
        <div class="book-chapter">🧮 الفصل 4: المعادلات الإنتاجية</div>
        <div class="book-body">
        معادلات NRC لحساب الاحتياجات من الوزن والإنتاج.
        </div>
        
        <div class="book-chapter">🍼 الفصل 5: بدائل الحليب</div>
        <div class="book-body">
        تركيب بديل حليب للصغار حسب العمر والنوع.
        </div>
        </div>
        """, unsafe_allow_html=True)

# =====================================================================
# التذييل
# =====================================================================
st.markdown("""
<div style='text-align:center; padding:20px; margin-top:30px; border-top:2px solid #e0e0e0; color:#888;'>
🌾 <b>تاور نولجي Tawornology العلمية</b> — للانتاج الحيواني وتركيب الاعلاف<br>
© 2026 | الاختصاصي م. عبد القادر إسماعيل تاور — اختصاصي تغذية الحيوان<br>
🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b> — رحمهما الله
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="mini-left-signature">🌾 Tawornology © 2026</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# نهاية الكود
# =====================================================================
print("=" * 70)
print("🌾 تاور نولجي Tawornology v17.1 — جاهز للتشغيل")
print("=" * 70)
