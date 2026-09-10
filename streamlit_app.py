# ============================================================================
# تاور نولجي Tawornology العلمية — الإصدار النهائي 18.0
# ============================================================================
# 🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله
# ============================================================================
# المشرف: اختصاصي تغذية الحيوان م. عبد القادر إسماعيل تاور
# ============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import json, os, base64, smtplib, time, urllib.parse, hashlib, secrets, io
import sqlite3, warnings, re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scipy.optimize import linprog
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List

warnings.filterwarnings('ignore')

# ===== PDF =====
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import (Table, TableStyle, Paragraph, Spacer, Image,
                                 SimpleDocTemplate, PageBreak)
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import arabic_reshaper
from bidi.algorithm import get_display
import qrcode
from PIL import Image as PILImage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ===== الصوت =====
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

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
# الثوابت
# =====================================================================
OWNER_NAME = "اختصاصي تغذية الحيوان م. عبد القادر إسماعيل تاور"
OWNER_CODE = "202687"
OWNER_EMAIL = "abukram128@gmail.com"
SENDER_EMAIL = "abukram128@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
WHATSAPP_NUMBER = "+249123533489"

SIGNATURE_PHRASE = "مع خالص شكري وتقديري"
SIGNATURE_NAME = "اختصاصي تغذية الحيوان م . عبد القادر إسماعيل تاور"

BASMALA = "بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ"

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
    def __init__(self, db_path="tawornology_v18.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        tables = [
            '''CREATE TABLE IF NOT EXISTS formulas (formula_id TEXT PRIMARY KEY, animal TEXT, breed TEXT, stage TEXT, dp REAL, se REAL, cost REAL, ingredients TEXT, requester TEXT, created TEXT)''',
            '''CREATE TABLE IF NOT EXISTS lab_results (result_id TEXT PRIMARY KEY, sample TEXT, cp REAL, dp REAL, se REAL, dc REAL, ndf REAL, adf REAL, ee REAL, ash REAL, date TEXT, user TEXT)''',
            '''CREATE TABLE IF NOT EXISTS milk_replacers (id TEXT PRIMARY KEY, animal TEXT, age INTEGER, formula TEXT, instructions TEXT, date TEXT)''',
            '''CREATE TABLE IF NOT EXISTS dose_reminders (id TEXT PRIMARY KEY, animal TEXT, name TEXT, dose REAL, unit TEXT, route TEXT, freq INTEGER, next_date TEXT)''',
            '''CREATE TABLE IF NOT EXISTS farms (id TEXT PRIMARY KEY, name TEXT, breed TEXT, count INTEGER, age INTEGER, weight REAL, feed REAL, dead INTEGER, date TEXT)''',
        ]
        for t in tables:
            c.execute(t)
        conn.commit()
        conn.close()
    
    def insert(self, table, data):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            cols = ', '.join(data.keys())
            ph = ', '.join(['?' for _ in data])
            c.execute(f"INSERT INTO {table} ({cols}) VALUES ({ph})", list(data.values()))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get(self, table):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            data = c.execute(f"SELECT * FROM {table}").fetchall()
            conn.close()
            return data
        except Exception:
            return []

db = DatabaseManager()

# =====================================================================
# دوال الصوت
# =====================================================================
@st.cache_data(ttl=3600)
def tts_b64(text, lang="ar"):
    if not GTTS_AVAILABLE or not text:
        return None
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()
    except Exception:
        return None

def play_audio(msg):
    if not msg:
        return
    b64 = tts_b64(msg)
    if b64:
        st.components.v1.html(
            f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mpeg"></audio>',
            height=0
        )

def voice_welcome(role):
    msgs = {
        "owner": f"مرحباً بك، {OWNER_NAME}.",
        "public": "مرحباً بك زائراً في تاور نولجي Tawornology العلمية."
    }
    play_audio(msgs.get(role, "مرحباً بك."))

def play_full_guide():
    msgs = [
        "مرحباً بك في منصة تاور نولجي Tawornology العلمية.",
        "المنصة متخصصة في الانتاج الحيواني وتركيب الاعلاف.",
        "يمكنك تركيب الأعلاف، استخدام المختبر الذكي، إدارة المزارع،",
        "تركيب بدائل الحليب، ومعرفة مواقيت الصلاة.",
        "نسأل الله التوفيق والسداد."
    ]
    for m in msgs:
        play_audio(m)
        time.sleep(2.5)

def play_dua():
    msgs = [
        "اللهم اغفر لإسماعيل تاور وابتسام،",
        "وارحمهما وأدخلهما فسيح جناتك."
    ]
    for m in msgs:
        play_audio(m)
        time.sleep(2)

# =====================================================================
# إرسال الكود بالبريد
# =====================================================================
def send_code_email(receiver, password):
    if receiver.strip().lower() != OWNER_EMAIL.lower():
        return False, f"❌ الإرسال مسموح فقط لـ: {OWNER_EMAIL}"
    if not password or len(password.strip().replace(" ", "")) < 8:
        return False, "⚠️ أدخل كلمة مرور التطبيق (App Password 16 حرفاً)"
    
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception:
        code = "# الكود قيد التشغيل مباشرة"
    
    fhash = hashlib.md5(code.encode()).hexdigest()
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver
    msg['Subject'] = "🌾 السورس كود — تاور نولجي Tawornology v18.0"
    
    body = f"""السلام عليكم،
مرفق السورس كود الكامل:
- التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- التوقيع الرقمي: {fhash}
- المشرف: {OWNER_NAME}
- عدد الأسطر: {len(code.splitlines()):,}
- الحجم: {len(code)/1024:.1f} KB"""
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    att = MIMEText(code, 'plain', 'utf-8')
    att.add_header('Content-Disposition', 'attachment', filename="tawornology_v18.py")
    msg.attach(att)
    
    try:
        s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        s.starttls()
        s.login(SENDER_EMAIL, password.strip().replace(" ", ""))
        s.sendmail(SENDER_EMAIL, receiver, msg.as_string())
        s.quit()
        return True, f"✅ تم الإرسال إلى {receiver}"
    except smtplib.SMTPAuthenticationError:
        return False, "❌ فشل تسجيل الدخول — تحقق من App Password"
    except Exception as e:
        return False, f"❌ خطأ: {str(e)}"

# =====================================================================
# تحميل الخط العربي
# =====================================================================
@st.cache_resource
def download_font():
    fp = "Amiri-Regular.ttf"
    if os.path.exists(fp):
        return fp
    try:
        import requests
        url = "https://raw.githubusercontent.com/aliftype/amiri/master/fonts/Amiri-Regular.ttf"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            with open(fp, "wb") as f:
                f.write(r.content)
            return fp
    except Exception:
        pass
    for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "C:/Windows/Fonts/arial.ttf"]:
        if os.path.exists(f):
            return f
    return None

def get_font():
    fp = download_font()
    if fp:
        try:
            pdfmetrics.registerFont(TTFont('ArabicFont', fp))
            return 'ArabicFont'
        except Exception:
            pass
    return 'Helvetica'

# =====================================================================
# مولد PDF الاحترافي — الترويسة + الختم + الشكر
# =====================================================================
class PDFGenerator:
    def __init__(self):
        self.font = get_font()
        self.styles = self._styles()
    
    def _styles(self):
        return {
            'basmala': ParagraphStyle('basmala', fontName=self.font, fontSize=18,
                alignment=TA_CENTER, textColor=HexColor('#1a237e'), spaceAfter=10, leading=24),
            'owner': ParagraphStyle('owner', fontName=self.font, fontSize=20,
                alignment=TA_CENTER, textColor=HexColor('#0d47a1'), spaceAfter=6, leading=26),
            'title': ParagraphStyle('title', fontName=self.font, fontSize=24,
                alignment=TA_CENTER, textColor=HexColor('#1b5e20'), spaceAfter=15, leading=30),
            'subtitle': ParagraphStyle('subtitle', fontName=self.font, fontSize=15,
                alignment=TA_CENTER, textColor=HexColor('#2e7d32'), spaceAfter=12, leading=20),
            'heading': ParagraphStyle('heading', fontName=self.font, fontSize=14,
                alignment=TA_RIGHT, textColor=HexColor('#1b5e20'), spaceAfter=10, leading=18),
            'body': ParagraphStyle('body', fontName=self.font, fontSize=11,
                alignment=TA_RIGHT, textColor=HexColor('#333333'), spaceAfter=6, leading=16),
            'footer': ParagraphStyle('footer', fontName=self.font, fontSize=9,
                alignment=TA_CENTER, textColor=HexColor('#666666'), spaceAfter=0, leading=12),
            'thanks': ParagraphStyle('thanks', fontName=self.font, fontSize=14,
                alignment=TA_CENTER, textColor=HexColor('#1a237e'), spaceAfter=8, leading=20),
            'signature': ParagraphStyle('signature', fontName=self.font, fontSize=13,
                alignment=TA_CENTER, textColor=HexColor('#c62828'), spaceAfter=6, leading=18),
        }
    
    def _p(self, text, style='body'):
        return Paragraph(arabic_processor.fix_arabic_text(str(text)), self.styles.get(style, self.styles['body']))
    
    def _add_header(self, story):
        """الترويسة: البسملة + اسم المشرف"""
        story.append(self._p(BASMALA, 'basmala'))
        story.append(HRFlowable(width="100%", thickness=2,
                                color=HexColor('#d4af37'), spaceBefore=5, spaceAfter=12))
        story.append(self._p(OWNER_NAME, 'owner'))
        story.append(self._p("المشرف العام للمنصة", 'subtitle'))
        story.append(HRFlowable(width="100%", thickness=3,
                                color=HexColor('#1b5e20'), spaceBefore=8, spaceAfter=15))
    
    def _add_footer_signature(self, story):
        """الختم + عبارة الشكر"""
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=2,
                                color=HexColor('#2e7d32'), spaceBefore=15, spaceAfter=20))
        
        # عبارة الشكر
        story.append(self._p(SIGNATURE_PHRASE, 'thanks'))
        story.append(self._p(SIGNATURE_NAME, 'signature'))
        story.append(Spacer(1, 15))
        
        # ختم دائري
        story.append(self._p("═══════════════════════════════", 'footer'))
        story.append(self._p("🔏 ختم المنصة الرسمي 🔏", 'thanks'))
        story.append(self._p("تاور نولجي Tawornology العلمية", 'signature'))
        story.append(self._p(f"📅 {datetime.now().strftime('%Y-%m-%d')} | ⏰ {datetime.now().strftime('%H:%M')}", 'footer'))
        story.append(self._p("═══════════════════════════════", 'footer'))
        story.append(Spacer(1, 12))
        story.append(self._p("🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله", 'footer'))
        story.append(self._p("اللهم اجعل قبرهما روضة من رياض الجنة", 'footer'))
    
    def _compare_chart(self, formula, computed_dp, computed_se, standard):
        """رسم بياني للمقارنة مع المعايير"""
        fig, ax = plt.subplots(figsize=(7, 4))
        metrics, calc_vals, std_vals = [], [], []
        if standard:
            if 'DP' in standard:
                metrics.append('DP'); calc_vals.append(computed_dp); std_vals.append(standard['DP'])
            if 'SE' in standard:
                metrics.append('SE'); calc_vals.append(computed_se); std_vals.append(standard['SE'])
        if not metrics:
            return None
        x = np.arange(len(metrics))
        w = 0.35
        b1 = ax.bar(x - w/2, calc_vals, w, label='المحسوب', color='#2e7d32', edgecolor='#1b5e20', linewidth=1.5)
        b2 = ax.bar(x + w/2, std_vals, w, label='القياسي', color='#1565C0', edgecolor='#0d47a1', linewidth=1.5)
        for bars in [b1, b2]:
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, h, f'{h:.1f}',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax.set_xticks(x); ax.set_xticklabels(metrics)
        ax.set_ylabel('القيمة')
        ax.set_title('مقارنة المحسوب مع القياسي', fontsize=12, fontweight='bold')
        ax.legend(loc='upper right'); ax.grid(axis='y', linestyle='--', alpha=0.5)
        ax.set_facecolor('#f8f9fa')
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close()
        buf.seek(0)
        return buf
    
    def formula_report(self, formula, dp, se, breed, cost, requester="", standard=None):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=45, leftMargin=45,
                                topMargin=45, bottomMargin=45)
        story = []
        
        self._add_header(story)
        story.append(self._p("🌾 تاور نولجي Tawornology العلمية", 'title'))
        story.append(self._p("📄 تقرير تركيب علفي فني", 'subtitle'))
        story.append(Spacer(1, 12))
        
        info = [
            [arabic_processor.fix_arabic_text("🐾 الفصيل"), arabic_processor.fix_arabic_text(breed)],
            [arabic_processor.fix_arabic_text("👤 طالب العلف"), arabic_processor.fix_arabic_text(requester or "غير محدد")],
            [arabic_processor.fix_arabic_text("📅 التاريخ"), arabic_processor.fix_arabic_text(datetime.now().strftime("%Y-%m-%d %H:%M"))],
        ]
        t_info = Table(info, colWidths=[180, 320])
        t_info.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), HexColor('#e8f5e9')),
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,-1), self.font),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#c8e6c9')),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t_info)
        story.append(Spacer(1, 18))
        
        story.append(self._p("📊 النتائج الرئيسية", 'heading'))
        data = [
            [arabic_processor.fix_arabic_text('المعيار'), arabic_processor.fix_arabic_text('القيمة')],
            [arabic_processor.fix_arabic_text('البروتين المهضوم (DP)'), arabic_processor.fix_arabic_text(f'{dp:.2f}%')],
            [arabic_processor.fix_arabic_text('معادل النشاء (SE)'), arabic_processor.fix_arabic_text(f'{se:.2f}')],
            [arabic_processor.fix_arabic_text('التكلفة للطن'), arabic_processor.fix_arabic_text(f'${cost:.2f}')]
        ]
        t = Table(data, colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#2e7d32')),
            ('BACKGROUND', (0,1), (-1,-1), HexColor('#f5f5f5')),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(t)
        
        # الرسم البياني للمقارنة
        if standard:
            story.append(Spacer(1, 15))
            chart_buf = self._compare_chart(formula, dp, se, standard)
            if chart_buf:
                story.append(self._p("📏 المقارنة مع المعايير القياسية", 'heading'))
                story.append(Image(chart_buf, width=440, height=250))
            
            # جدول المقارنة
            comp = [[
                arabic_processor.fix_arabic_text('المقياس'),
                arabic_processor.fix_arabic_text('المحسوب'),
                arabic_processor.fix_arabic_text('القياسي'),
                arabic_processor.fix_arabic_text('الانحراف'),
                arabic_processor.fix_arabic_text('التقييم')
            ]]
            if 'DP' in standard:
                dev = ((dp - standard['DP']) / standard['DP']) * 100 if standard['DP'] > 0 else 0
                g = "✅ ممتاز" if abs(dev) <= 5 else ("⚠️ جيد" if abs(dev) <= 10 else "❌ ضعيف")
                comp.append([
                    arabic_processor.fix_arabic_text('DP'),
                    arabic_processor.fix_arabic_text(f"{dp:.2f}%"),
                    arabic_processor.fix_arabic_text(f"{standard['DP']:.2f}%"),
                    arabic_processor.fix_arabic_text(f"{dev:.1f}%"),
                    arabic_processor.fix_arabic_text(g)
                ])
            if 'SE' in standard:
                dev = ((se - standard['SE']) / standard['SE']) * 100 if standard['SE'] > 0 else 0
                g = "✅ ممتاز" if abs(dev) <= 5 else ("⚠️ جيد" if abs(dev) <= 10 else "❌ ضعيف")
                comp.append([
                    arabic_processor.fix_arabic_text('SE'),
                    arabic_processor.fix_arabic_text(f"{se:.2f}"),
                    arabic_processor.fix_arabic_text(f"{standard['SE']:.2f}"),
                    arabic_processor.fix_arabic_text(f"{dev:.1f}%"),
                    arabic_processor.fix_arabic_text(g)
                ])
            t_c = Table(comp, colWidths=[80, 100, 100, 90, 100])
            t_c.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
                ('TEXTCOLOR', (0,0), (-1,0), white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,-1), self.font),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(Spacer(1, 10))
            story.append(t_c)
        
        # الصفحة الثانية - المكونات
        story.append(PageBreak())
        story.append(self._p("📋 المكونات المعتمدة للطن الواحد", 'heading'))
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
            ('FONTNAME', (0,0), (-1,-1), self.font),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f5f5f5')]),
            ('TOPPADDING', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ]))
        story.append(t2)
        
        # رسم دائري
        if len(formula) > 1:
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
                ax.set_title(arabic_processor.fix_arabic_text('توزيع المكونات'), fontsize=13, fontweight='bold')
                b = io.BytesIO()
                plt.savefig(b, format='png', dpi=130, bbox_inches='tight', facecolor='white')
                plt.close()
                b.seek(0)
                story.append(Spacer(1, 15))
                story.append(Image(b, width=430, height=280))
            except Exception:
                pass
        
        story.append(Spacer(1, 15))
        story.append(self._p("📌 التوصيات:", 'heading'))
        for r in [
            "• إضافة الإنزيمات لتحسين الهضم",
            "• مراقبة جودة المواد الخام دورياً",
            "• التخزين في مكان جاف بعيداً عن الرطوبة"
        ]:
            story.append(self._p(r))
        
        self._add_footer_signature(story)
        doc.build(story)
        buf.seek(0)
        return buf.getvalue()
    
    def lab_report(self, cp, dp, se, dc, animal, stage, standard=None):
        """تقرير المختبر مع الرسم البياني"""
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40, leftMargin=40,
                                topMargin=40, bottomMargin=40)
        story = []
        
        self._add_header(story)
        story.append(self._p("🔬 تقرير التحليل المخبري المتقدم", 'title'))
        story.append(self._p("تاور نولجي Tawornology العلمية", 'subtitle'))
        story.append(Spacer(1, 12))
        
        story.append(self._p(f"🐾 الحيوان: {animal} | المرحلة: {stage}", 'body'))
        story.append(self._p(f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 'body'))
        story.append(Spacer(1, 15))
        
        # جدول النتائج
        story.append(self._p("📊 النتائج المحسوبة", 'heading'))
        data = [
            [arabic_processor.fix_arabic_text('العنصر'), arabic_processor.fix_arabic_text('القيمة')],
            [arabic_processor.fix_arabic_text('البروتين الخام (CP)'),
             arabic_processor.fix_arabic_text(f'{cp:.2f}%')],
            [arabic_processor.fix_arabic_text('معامل الهضم (DC)'),
             arabic_processor.fix_arabic_text(f'{dc:.2f}')],
            [arabic_processor.fix_arabic_text('البروتين المهضوم (DP)'),
             arabic_processor.fix_arabic_text(f'{dp:.2f}%')],
            [arabic_processor.fix_arabic_text('معادل النشاء (SE)'),
             arabic_processor.fix_arabic_text(f'{se:.2f}')],
        ]
        t = Table(data, colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1565C0')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#1565C0')),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        
        # المقارنة مع المعايير
        if standard:
            story.append(self._p("📏 المقارنة مع المعايير القياسية", 'heading'))
            
            # جدول المقارنة
            comp = [[
                arabic_processor.fix_arabic_text('المقياس'),
                arabic_processor.fix_arabic_text('المحسوب'),
                arabic_processor.fix_arabic_text('القياسي'),
                arabic_processor.fix_arabic_text('الانحراف'),
                arabic_processor.fix_arabic_text('التقييم')
            ]]
            
            if 'DP' in standard:
                dev = ((dp - standard['DP']) / standard['DP']) * 100 if standard['DP'] > 0 else 0
                g = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                comp.append([
                    arabic_processor.fix_arabic_text('DP'),
                    arabic_processor.fix_arabic_text(f"{dp:.2f}%"),
                    arabic_processor.fix_arabic_text(f"{standard['DP']:.2f}%"),
                    arabic_processor.fix_arabic_text(f"{dev:.1f}%"),
                    arabic_processor.fix_arabic_text(f"{g}")
                ])
            if 'SE' in standard:
                dev = ((se - standard['SE']) / standard['SE']) * 100 if standard['SE'] > 0 else 0
                g = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                comp.append([
                    arabic_processor.fix_arabic_text('SE'),
                    arabic_processor.fix_arabic_text(f"{se:.2f}"),
                    arabic_processor.fix_arabic_text(f"{standard['SE']:.2f}"),
                    arabic_processor.fix_arabic_text(f"{dev:.1f}%"),
                    arabic_processor.fix_arabic_text(f"{g}")
                ])
            if 'CP' in standard:
                dev = ((cp - standard['CP']) / standard['CP']) * 100 if standard['CP'] > 0 else 0
                g = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                comp.append([
                    arabic_processor.fix_arabic_text('CP'),
                    arabic_processor.fix_arabic_text(f"{cp:.2f}%"),
                    arabic_processor.fix_arabic_text(f"{standard['CP']:.2f}%"),
                    arabic_processor.fix_arabic_text(f"{dev:.1f}%"),
                    arabic_processor.fix_arabic_text(f"{g}")
                ])
            
            t_c = Table(comp, colWidths=[80, 100, 100, 90, 80])
            t_c.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), HexColor('#2e7d32')),
                ('TEXTCOLOR', (0,0), (-1,0), white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,-1), self.font),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd')),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(t_c)
            story.append(Spacer(1, 15))
            
            # الرسم البياني
            fig, ax = plt.subplots(figsize=(7, 4))
            metrics, calc_vals, std_vals = [], [], []
            if 'DP' in standard:
                metrics.append('DP (%)'); calc_vals.append(dp); std_vals.append(standard['DP'])
            if 'SE' in standard:
                metrics.append('SE'); calc_vals.append(se); std_vals.append(standard['SE'])
            if 'CP' in standard:
                metrics.append('CP (%)'); calc_vals.append(cp); std_vals.append(standard['CP'])
            
            x = np.arange(len(metrics))
            w = 0.35
            b1 = ax.bar(x - w/2, calc_vals, w, label='المحسوب',
                       color='#2e7d32', edgecolor='#1b5e20', linewidth=1.5)
            b2 = ax.bar(x + w/2, std_vals, w, label='القياسي',
                       color='#1565C0', edgecolor='#0d47a1', linewidth=1.5)
            for bars in [b1, b2]:
                for bar in bars:
                    h = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2, h, f'{h:.1f}',
                           ha='center', va='bottom', fontsize=10, fontweight='bold')
            ax.set_xticks(x); ax.set_xticklabels(metrics)
            ax.set_title('مقارنة المحسوب مع القياسي', fontsize=12, fontweight='bold')
            ax.legend(loc='upper right'); ax.grid(axis='y', linestyle='--', alpha=0.5)
            ax.set_facecolor('#f8f9fa')
            b = io.BytesIO()
            plt.tight_layout()
            plt.savefig(b, format='png', dpi=130, bbox_inches='tight', facecolor='white')
            plt.close()
            b.seek(0)
            story.append(Image(b, width=460, height=260))
            story.append(Spacer(1, 15))
            
            # التوصيات
            story.append(self._p("📌 التوصيات المخبرية:", 'heading'))
            dp_dev = ((dp - standard.get('DP', 0)) / standard.get('DP', 1)) * 100 if standard.get('DP', 0) > 0 else 0
            se_dev = ((se - standard.get('SE', 0)) / standard.get('SE', 1)) * 100 if standard.get('SE', 0) > 0 else 0
            
            if abs(dp_dev) <= 5 and abs(se_dev) <= 5:
                story.append(self._p("✅ الخلطة مطابقة للمعايير — جودة ممتازة"))
            elif dp_dev < -10:
                story.append(self._p("⚠️ البروتين المهضوم أقل من المعيار — يُنصح بإضافة مصادر بروتين"))
            elif dp_dev > 10:
                story.append(self._p("⚠️ البروتين المهضوم أعلى من المعيار — يمكن تقليل التكلفة"))
            if se_dev < -10:
                story.append(self._p("⚠️ الطاقة (SE) أقل من المعيار — يُنصح بإضافة مصادر طاقة"))
            elif se_dev > 10:
                story.append(self._p("⚠️ الطاقة (SE) أعلى من المعيار — مراجعة التركيبة"))
        
        self._add_footer_signature(story)
        doc.build(story)
        buf.seek(0)
        return buf.getvalue()
    
    def milk_report(self, formula, animal, age, instructions):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=50, leftMargin=50,
                                topMargin=50, bottomMargin=50)
        story = []
        
        self._add_header(story)
        story.append(self._p("🍼 تقرير بديل الحليب", 'title'))
        story.append(self._p("تاور نولجي Tawornology العلمية", 'subtitle'))
        story.append(Spacer(1, 12))
        story.append(self._p(f"🐾 الحيوان: {animal} | العمر: {age} يوم"))
        story.append(Spacer(1, 15))
        
        story.append(self._p("📋 مكونات بديل الحليب", 'heading'))
        data = [[
            arabic_processor.fix_arabic_text('المكون'),
            arabic_processor.fix_arabic_text('النسبة %'),
            arabic_processor.fix_arabic_text('جم/لتر')
        ]]
        for ing, pct in formula.items():
            data.append([
                arabic_processor.fix_arabic_text(ing),
                arabic_processor.fix_arabic_text(f'{pct:.2f}%'),
                arabic_processor.fix_arabic_text(f'{pct*10:.1f}')
            ])
        t = Table(data, colWidths=[220, 130, 130])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), self.font),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('GRID', (0,0), (-1,-1), 1, HexColor('#bdbdbd'))
        ]))
        story.append(t)
        story.append(Spacer(1, 15))
        
        story.append(self._p("📌 تعليمات التقديم", 'heading'))
        for line in instructions.split('\n'):
            if line.strip():
                story.append(self._p(f"• {line.strip()}"))
        
        self._add_footer_signature(story)
        doc.build(story)
        buf.seek(0)
        return buf.getvalue()

pdf_gen = PDFGenerator()

# =====================================================================
# مكتبة الأعلاف
# =====================================================================
FEEDS = {
    "🌾 الحبوب": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5},
        "قمح محلي": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8},
        "جريش أرز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5},
        "دخن": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5},
    },
    "🌱 الأكساب": {
        "أمباز الفول السوداني": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0},
        "كسب عباد الشمس": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5},
        "كسب بذور القطن": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5},
        "كسب السمسم": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5},
        "كسب جلوتين الذرة": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5},
    },
    "🚜 المخلفات": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5},
        "البرسيم الجاف": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8},
        "تبن قمح": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5},
        "سرسة الأرز": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5},
        "مخلفات البسكويت": {"CP": 10.0, "DC": 0.80, "SE": 65.0, "NDF": 8.0, "ADF": 4.0},
    },
    "🧬 البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5},
        "مسحوق أسماك 72%": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5},
        "مركزات دواجن": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5},
        "مركزات مواشي": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5},
    },
    "🧪 أحماض أمينية": {
        "ليسين نقي": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
        "ميثيونين نقي": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
        "ثريونين نقي": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
        "بريمكس مواشي": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
        "إنزيم الفايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
        "إنزيم NSP": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
        "خميرة الخبز": {"CP": 45.0, "DC": 0.85, "SE": 35.0, "NDF": 5.0, "ADF": 2.0},
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
        "فوسفات DCP": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
        "يوريا علفية": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
    },
    "🍼 بدائل الحليب": {
        "مصل الحليب (Whey)": {"CP": 12.0, "DC": 0.95, "SE": 35.0, "NDF": 0.0, "ADF": 0.0},
        "حليب مجفف": {"CP": 34.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0},
        "دهن نباتي": {"CP": 0.0, "DC": 0.0, "SE": 10.0, "NDF": 0.0, "ADF": 0.0},
        "ليسيثين الصويا": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0},
        "بروتين الصويا": {"CP": 65.0, "DC": 0.90, "SE": 30.0, "NDF": 2.0, "ADF": 1.0},
    }
}

FLAT_FEEDS = {}
for cat, items in FEEDS.items():
    for name, nut in items.items():
        FLAT_FEEDS[name] = nut

# =====================================================================
# المعايير القياسية
# =====================================================================
STANDARDS = {
    "أبقار": {
        "تسمين عجول": {"DP": 12.0, "SE": 68.0, "CP": 15.0},
        "حليب/إدرار": {"DP": 14.0, "SE": 70.0, "CP": 17.5},
        "حمل/دفع غذائي": {"DP": 11.0, "SE": 65.0, "CP": 13.8},
        "صيانة": {"DP": 9.0, "SE": 60.0, "CP": 11.3},
    },
    "أغنام": {
        "تسمين حملان": {"DP": 13.0, "SE": 66.0, "CP": 16.3},
        "نعاج مرضعات": {"DP": 14.5, "SE": 68.0, "CP": 18.1},
        "نعاج حامل": {"DP": 11.5, "SE": 62.0, "CP": 14.4},
        "نعاج جافة": {"DP": 8.5, "SE": 58.0, "CP": 10.6},
    },
    "ماعز": {
        "تسمين جديان": {"DP": 12.5, "SE": 64.0, "CP": 15.6},
        "عنزات حلابة": {"DP": 14.0, "SE": 66.0, "CP": 17.5},
        "عنزات حامل": {"DP": 11.0, "SE": 60.0, "CP": 13.8},
        "صيانة": {"DP": 8.0, "SE": 56.0, "CP": 10.0},
    },
    "خيول": {
        "راحة/صيانة": {"DP": 9.0, "SE": 58.0, "CP": 11.3},
        "عمل خفيف": {"DP": 10.0, "SE": 60.0, "CP": 12.5},
        "عمل متوسط": {"DP": 11.0, "SE": 62.0, "CP": 13.8},
        "عمل مكثف": {"DP": 13.0, "SE": 65.0, "CP": 16.3},
        "سباق": {"DP": 14.0, "SE": 68.0, "CP": 17.5},
    },
    "إبل": {
        "راحة/صيانة": {"DP": 8.0, "SE": 55.0, "CP": 10.0},
        "حمل/رضاعة": {"DP": 10.0, "SE": 58.0, "CP": 12.5},
        "إنتاج حليب": {"DP": 12.0, "SE": 60.0, "CP": 15.0},
        "تسمين": {"DP": 11.0, "SE": 62.0, "CP": 13.8},
    },
    "دواجن": {
        "بادي (0-14 يوم)": {"DP": 22.0, "SE": 76.0, "CP": 27.5},
        "نامي (15-28 يوم)": {"DP": 20.0, "SE": 74.0, "CP": 25.0},
        "ناهي (29-42 يوم)": {"DP": 18.0, "SE": 72.0, "CP": 22.5},
    },
    "أسماك": {
        "زريعة/بادئ": {"DP": 32.0, "SE": 70.0, "CP": 40.0},
        "نمو": {"DP": 28.0, "SE": 68.0, "CP": 35.0},
        "تسمين نهائي": {"DP": 26.0, "SE": 66.0, "CP": 32.5},
    },
}

# =====================================================================
# CSS
# =====================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
* { font-family: 'Cairo', 'Tajawal', sans-serif; }
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 50%, #b2dfdb 100%);
    background-attachment: fixed;
}
.stApp { background: transparent; }
.main-box {
    background: rgba(255,255,255,0.97);
    padding: 35px; border-radius: 25px;
    box-shadow: 0 25px 70px rgba(0,0,0,0.15);
    backdrop-filter: blur(15px);
    margin-bottom: 35px;
    border: 2px solid rgba(212,175,55,0.3);
}
h1, h2, h3, h4 { color: #1a237e !important; font-weight: 700 !important; }
.section-title {
    color: #1b5e20 !important;
    border-right: 8px solid #2e7d32;
    padding: 15px 22px;
    text-align: right;
    font-size: 1.7rem;
    font-weight: 900;
    margin: 30px 0 20px 0;
    background: linear-gradient(to left, rgba(46,125,50,0.12), transparent);
    border-radius: 14px;
}
.formula-item {
    background: linear-gradient(135deg, #ffffff, #f1f8e9);
    padding: 15px 22px; border-radius: 14px;
    margin-bottom: 10px; font-weight: 700;
    color: #1b5e20 !important;
    border-right: 6px solid #2e7d32;
    box-shadow: 0 5px 20px rgba(0,0,0,0.06);
    display: flex; justify-content: space-between; align-items: center;
}
.profile-img {
    width: 160px; height: 160px; border-radius: 50%; object-fit: cover;
    border: 5px solid #d4af37;
    box-shadow: 0 15px 40px rgba(212,175,55,0.4);
    background: #fff;
}
.metric-card {
    background: white; padding: 20px;
    border-radius: 18px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    text-align: center;
    border: 2px solid rgba(46,125,50,0.1);
    transition: all 0.3s ease;
}
.metric-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 15px 45px rgba(46,125,50,0.2);
}
.metric-card .number {
    font-size: 2.2rem; font-weight: 900;
    background: linear-gradient(135deg, #1b5e20, #43a047);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.metric-card .label { font-size: 0.9rem; color: #555; font-weight: 700; }
.info-card {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    padding: 20px; border-radius: 15px;
    border-right: 6px solid #2e7d32;
    box-shadow: 0 6px 20px rgba(46,125,50,0.12);
    margin-bottom: 15px;
}
.warning-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 15px; border-radius: 12px;
    border-right: 6px solid #f57c00;
    color: #e65100 !important;
    font-weight: 600;
    margin-bottom: 12px;
}
.stButton > button {
    color: #1a1a1a !important;
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9) !important;
    border: 2px solid #2e7d32 !important;
    font-weight: 700 !important;
    border-radius: 14px !important;
    padding: 10px 22px !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #a5d6a7, #81c784) !important;
    transform: translateY(-3px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1b5e20, #2e7d32, #43a047) !important;
    color: #ffffff !important;
    border: 2px solid #1b5e20 !important;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    border-radius: 12px !important;
    border: 2px solid #c8e6c9 !important;
    padding: 10px 14px !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: rgba(255,255,255,0.7);
    padding: 6px;
    border-radius: 15px;
}
.stTabs [data-baseweb="tab-list"] button {
    border-radius: 12px !important;
    padding: 10px 18px !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9) !important;
    color: #1b5e20 !important;
    font-weight: 800 !important;
}
.manual-book {
    background: #fff; padding: 35px;
    border-radius: 18px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.08);
}
.book-chapter {
    background: linear-gradient(135deg, #1a237e, #283593);
    color: #ffffff !important;
    padding: 15px 22px; border-radius: 12px;
    font-weight: 800; margin-top: 25px;
    font-size: 1.2rem;
    border-right: 6px solid #d4af37;
}
.book-body {
    padding: 20px 25px;
    font-size: 1.05rem; line-height: 1.8;
    color: #2c3e50 !important;
    border-left: 5px solid #3498db;
    margin-bottom: 20px;
    background: linear-gradient(to right, #f8f9fa, #ffffff);
    border-radius: 0 12px 12px 0;
}
.basmala-bar {
    background: linear-gradient(135deg, #0d1b2a, #1a237e, #4a148c, #0d1b2a);
    padding: 20px 15px;
    border-radius: 20px;
    margin-bottom: 20px;
    text-align: center;
    border: 3px solid #ffd700;
    box-shadow: 0 10px 40px rgba(255,215,0,0.4);
}
.basmala-text {
    color: #ffd700; font-size: 1.9rem;
    font-weight: 800;
    text-shadow: 0 0 15px #ffd700, 0 0 30px #ff8c00;
    letter-spacing: 2px;
}
.dua-bar {
    background: linear-gradient(135deg, #0d1b2a, #1a237e);
    padding: 12px;
    border-radius: 15px;
    margin-bottom: 20px;
    text-align: center;
    border: 2px solid #ffd700;
}
.dua-text {
    color: #ffab40;
    font-size: 1.1rem;
    font-weight: 600;
}
.owner-header {
    text-align: center;
    padding: 15px;
    background: linear-gradient(135deg, #ffffff, #f8f9fa);
    border-radius: 15px;
    margin-bottom: 15px;
    border-bottom: 4px solid #d4af37;
}
.owner-name {
    font-size: 1.6rem;
    font-weight: 900;
    color: #0d47a1;
    letter-spacing: 0.5px;
}
.owner-title {
    font-size: 1rem;
    color: #c62828;
    font-weight: 700;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# شريط البسملة
# =====================================================================
def render_basmala():
    st.markdown(f"""
    <div class="basmala-bar">
        <div class="basmala-text">﷽ {BASMALA}</div>
    </div>
    """, unsafe_allow_html=True)

def render_dua():
    st.markdown("""
    <div class="dua-bar">
        <div class="dua-text">
            ❤️ اللهم اغفر لإسماعيل تاور وابتسام وارحمهما وأدخلهما فسيح جناتك ❤️
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_owner_header():
    st.markdown(f"""
    <div class="owner-header">
        <div class="owner-name">🌾 {OWNER_NAME} 🌾</div>
        <div class="owner-title">المشرف العام — منصة تاور نولجي Tawornology العلمية</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# حالة الجلسة
# =====================================================================
defaults = {
    "approved": False, "user_role": None, "login_shown": False,
    "login_attempts": 0, "last_login": None, "active_formula": {},
    "computed_dp": 0.0, "computed_se": 0.0, "computed_cost": 0.0,
    "active_breed": "", "dose_reminders": [], "farms": {},
    "livestock_prices": {
        "عجول تسمين ($)": 1350.0, "أبقار محلية ($)": 900.0,
        "ضأن ($)": 180.0, "ماعز ($)": 130.0, "خيول ($)": 4500.0,
    },
    "products_prices": {
        "كيلو لحم بقري ($)": 7.50, "كيلو لحم ضأن ($)": 9.00,
        "كيلو لحم دجاج ($)": 3.80, "طبق بيض 30 ($)": 4.20,
    }
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =====================================================================
# شاشة الدخول
# =====================================================================
MAX_ATTEMPTS = 5

if not st.session_state["approved"]:
    render_basmala()
    render_dua()
    
    if st.session_state["login_attempts"] >= MAX_ATTEMPTS:
        if st.session_state["last_login"]:
            diff = (datetime.now() - st.session_state["last_login"]).seconds
            if diff < 300:
                st.error(f"🔒 قفل مؤقت — المتبقي: {300 - diff} ثانية")
                st.stop()
            else:
                st.session_state["login_attempts"] = 0
    
    st.markdown('<div class="main-box" style="max-width:600px; margin:60px auto; direction:rtl;">', unsafe_allow_html=True)
    
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" style="width:120px; height:120px; border-radius:50%; border:4px solid #d4af37; display:block; margin:0 auto; box-shadow:0 8px 25px rgba(0,0,0,0.2);">', unsafe_allow_html=True)
    
    st.markdown("<h2 style='color:#1a237e; text-align:center; margin-top:20px;'>🌾 تاور نولجي Tawornology العلمية</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555; font-size:1.1rem;'>للانتاج الحيواني وتركيب الاعلاف</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#c62828; font-size:1rem; font-weight:700;'>{OWNER_NAME}</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888; font-size:0.85rem;'>الإصدار 18.0</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔊 الشرح الكامل", use_container_width=True, key="ag"):
            play_full_guide()
            st.success("✅ يعمل...")
    with col2:
        if st.button("🎵 الترحيب", use_container_width=True, key="aw"):
            voice_welcome("public")
    with col3:
        if st.button("🕊️ الدعاء", use_container_width=True, key="ad"):
            play_dua()
    
    st.markdown("---")
    st.markdown("### 👤 دخول كزائر مجاني")
    st.caption("تركيب الأعلاف • المختبر الذكي • المراجع • المساعدة")
    
    if st.button("🚀 الدخول كزائر", type="secondary", use_container_width=True, key="public_login"):
        st.session_state["approved"] = True
        st.session_state["user_role"] = "public"
        st.session_state["login_shown"] = False
        st.session_state["login_attempts"] = 0
        st.session_state["last_login"] = datetime.now()
        voice_welcome("public")
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔑 دخول المالك")
    st.caption("كل الميزات متاحة")
    
    code = st.text_input("🔐 كود الدخول:", type="password",
                         placeholder="أدخل الكود الخاص بك", key="owner_code")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔓 تسجيل الدخول", type="primary", use_container_width=True, key="owner_login"):
            if code.strip() == OWNER_CODE:
                st.session_state["approved"] = True
                st.session_state["user_role"] = "owner"
                st.session_state["login_shown"] = False
                st.session_state["login_attempts"] = 0
                st.session_state["last_login"] = datetime.now()
                voice_welcome("owner")
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                rem = MAX_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ كود غير صحيح! متبقي {rem} محاولات")
    with c2:
        if st.button("🔄 نسيت الكود", use_container_width=True, key="owner_reset"):
            st.info(f"📧 تواصل: {OWNER_EMAIL}")
    
    st.markdown(f"""
    <div style='text-align:center; margin-top:20px; color:#999; font-size:0.85rem; padding:15px; border-top:1px solid #e0e0e0;'>
    <p>🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b></p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# الواجهة الرئيسية
# =====================================================================
render_basmala()

if not st.session_state["login_shown"]:
    role = st.session_state.get("user_role", "public")
    if role == "owner":
        st.toast(f"👑 مرحباً بك، {OWNER_NAME}", icon="🌾")
    else:
        st.toast("👤 مرحباً بك زائراً", icon="🌾")
    st.session_state["login_shown"] = True

render_dua()
st.markdown('<div class="main-box">', unsafe_allow_html=True)

# الترويسة الرئيسية
c_logout, c_user = st.columns([0.7, 0.3])
with c_user:
    role = st.session_state.get("user_role", "public")
    role_txt = "المالك 👑" if role == "owner" else "زائر 👤"
    st.markdown(f"""
    <div style='text-align:left; background:linear-gradient(135deg,#f5f5f5,#e0e0e0); padding:14px; border-radius:14px;'>
        <div style='font-weight:700;'>{OWNER_NAME if role=='owner' else 'زائر'}</div>
        <div style='font-size:0.85rem; color:#555;'>{role_txt}</div>
        <small style='color:#888;'>آخر دخول: {datetime.now().strftime('%Y-%m-%d %H:%M')}</small>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["livestock_prices", "products_prices", "dose_reminders", "farms"]:
                del st.session_state[key]
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

c_logo, c_title = st.columns([0.2, 0.8])
with c_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img">', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center; font-size:5rem;">🌾</div>', unsafe_allow_html=True)
with c_title:
    st.markdown("<h1 style='color:#1a237e; text-align:right;'>🌾 تاور نولجي Tawornology العلمية</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#1565C0; text-align:right; font-size:1.15rem;'>للانتاج الحيواني وتركيب الاعلاف</p>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:#c62828; text-align:right; font-weight:700;'>{OWNER_NAME}</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top:3px solid #2e7d32;'>", unsafe_allow_html=True)

# إحصائيات
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"<div class='metric-card'><div class='number'>{len(FLAT_FEEDS)}</div><div class='label'>مادة علفية</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='metric-card'><div class='number'>{len(STANDARDS)}</div><div class='label'>قطاع حيواني</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='metric-card'><div class='number'>{len(st.session_state.get('dose_reminders', []))}</div><div class='label'>جرعات مسجلة</div></div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='metric-card'><div class='number'>{len(st.session_state.get('farms', {}))}</div><div class='label'>مزارع</div></div>", unsafe_allow_html=True)

st.markdown("---")

# =====================================================================
# دالة دليل
# =====================================================================
def guide(title, text):
    with st.expander(f"📘 دليل {title}", expanded=False):
        st.markdown(f"<div style='background:#f0f8ff; padding:15px; border-radius:10px; direction:rtl;'>{text}</div>", unsafe_allow_html=True)
        if st.button(f"🔊 تشغيل صوتياً", key=f"g_{title}"):
            play_audio(text)

# =====================================================================
# دالة تركيب العلف
# =====================================================================
def render_formulation(animal_key, display_name, icon, breeds, stages, def_dp, def_se, has_meas=True):
    st.markdown(f'<div class="section-title">{icon} {display_name}</div>', unsafe_allow_html=True)
    
    requester = st.text_input("👤 اسم طالب العلف:",
                              placeholder="اسم المربي أو المزرعة",
                              key=f"{animal_key}_req")
    
    c_m, c_s = st.columns([0.4, 0.6])
    
    with c_m:
        if has_meas:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("#### 📏 القياسات الحيوية")
            ch, cl, ca = st.columns(3)
            with ch:
                hg = st.number_input("محيط الصدر (سم)", min_value=20.0, max_value=300.0,
                                     value=150.0, step=1.0, key=f"{animal_key}_hg")
            with cl:
                bl = st.number_input("طول الجسم (سم)", min_value=20.0, max_value=300.0,
                                     value=130.0, step=1.0, key=f"{animal_key}_bl")
            with ca:
                am = st.number_input("العمر (شهر)", min_value=1, max_value=120,
                                     value=12, step=1, key=f"{animal_key}_am")
            
            wf = {"cattle": 10838, "sheep": 15500, "goat": 15000,
                  "horse": 11877, "camel": 13000}.get(animal_key, 12000)
            ff = {"cattle": 0.025, "sheep": 0.035, "goat": 0.032,
                  "horse": 0.022, "camel": 0.020}.get(animal_key, 0.03)
            
            est_w = (hg ** 2 * bl) / wf
            dm = est_w * ff
            st.success(f"**الوزن التقديري:** {est_w:.1f} كجم")
            st.info(f"**الاحتياج اليومي:** {dm:.2f} كجم")
            
            age_factor = 1 + (am - 12) * 0.01
            adj_dp = def_dp * (1 + (est_w - 500) / 2000) * age_factor if est_w > 0 else def_dp
            adj_se = def_se * (1 + (est_w - 500) / 3000) * age_factor if est_w > 0 else def_se
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            adj_dp, adj_se = def_dp, def_se
            st.info("💡 لا قياسات للطيور والأسماك.")
    
    with c_s:
        st.markdown("#### 🎯 السلالة والمرحلة")
        cb, cs = st.columns(2)
        with cb:
            breed = st.selectbox("السلالة:", breeds, key=f"{animal_key}_br")
        with cs:
            stage = st.selectbox("المرحلة:", stages, key=f"{animal_key}_st")
        
        st.markdown("#### 🧬 العمر والحالة")
        cap = st.columns(2)
        with cap[0]:
            age_in = st.number_input("العمر (شهر)", min_value=1, max_value=240,
                                     value=24, step=1, key=f"{animal_key}_ai")
        with cap[1]:
            phys = st.selectbox("الحالة:",
                ["طبيعي", "حامل", "مرضع", "صائم", "نشاط مكثف", "استشفاء", "نمو سريع"],
                key=f"{animal_key}_ph")
        
        pb = st.radio("أساس البروتين:", ["DP", "CP"], horizontal=True, key=f"{animal_key}_pb")
        
        if pb == "DP":
            tp = st.number_input("DP %:", min_value=5.0, max_value=50.0,
                                value=float(adj_dp), step=0.5, key=f"{animal_key}_dp")
            st.caption(f"💡 CP ≈ {tp/0.80:.1f}%")
            actual_dp = tp
        else:
            tp = st.number_input("CP %:", min_value=5.0, max_value=60.0,
                                value=float(def_dp/0.80), step=0.5, key=f"{animal_key}_cp")
            st.caption(f"💡 DP ≈ {tp*0.80:.1f}%")
            actual_dp = tp * 0.80
        
        ts = st.number_input("SE:", min_value=10.0, max_value=90.0,
                            value=float(adj_se), step=1.0, key=f"{animal_key}_se")
        
        mult = {"طبيعي": 1.0, "حامل": 1.15, "مرضع": 1.30, "صائم": 0.85,
                "نشاط مكثف": 1.25, "استشفاء": 1.20, "نمو سريع": 1.35}.get(phys, 1.0)
        actual_dp *= mult
        ts *= mult
        st.caption(f"📌 معامل الحالة: {mult:.2f}")
    
    st.markdown("#### 🌾 اختر المكونات")
    selected = []
    prices = {}
    
    defaults_list = {
        "cattle": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                   "أمباز الفول السوداني", "مركزات مواشي", "ملح الطعام",
                   "الحجر الجيري", "فوسفات DCP", "بيكربونات الصوديوم"],
        "sheep": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                  "أمباز الفول السوداني", "مركزات مواشي", "ملح الطعام",
                  "الحجر الجيري", "فوسفات DCP", "بيكربونات الصوديوم"],
        "goat": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                 "أمباز الفول السوداني", "مركزات مواشي", "ملح الطعام",
                 "الحجر الجيري", "فوسفات DCP", "بيكربونات الصوديوم"],
        "horse": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                  "مولاس قصب السكر", "مركزات مواشي", "ملح الطعام", "الحجر الجيري"],
        "camel": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                  "أمباز الفول السوداني", "البرسيم الجاف", "مركزات مواشي",
                  "ملح الطعام", "الحجر الجيري", "فوسفات DCP"],
        "poultry": ["ذرة صفراء", "سورجم (فتريتة)", "كسب فول صويا 44%",
                    "كسب جلوتين الذرة", "مركزات دواجن", "بريمكس دواجن",
                    "ملح الطعام", "الحجر الجيري", "فوسفات DCP", "إنزيم الفايتيز"],
        "fish": ["ذرة صفراء", "كسب فول صويا 44%", "مسحوق أسماك 60%",
                 "كسب جلوتين الذرة", "مركزات دواجن", "ملح الطعام",
                 "فوسفات DCP", "إنزيم الفايتيز"]
    }
    
    defs = defaults_list.get(animal_key, [])
    
    for cat, items in FEEDS.items():
        with st.expander(f"📁 {cat}", expanded=False):
            cols = st.columns(3)
            for idx, (name, _) in enumerate(items.items()):
                with cols[idx % 3]:
                    chk = st.checkbox(name, value=name in defs, key=f"{animal_key}_c_{name}")
                    if chk:
                        pr = st.number_input(f"سعر {name}", min_value=5.0,
                                            value=float(250.0 if "نخالة" in name or "ملح" in name else 350.0),
                                            key=f"{animal_key}_p_{name}")
                        selected.append(name)
                        prices[name] = pr
    
    cbtn = st.columns(3)
    with cbtn[0]:
        if st.button(f"🚀 تشغيل المحرك", type="primary", use_container_width=True,
                     key=f"{animal_key}_run"):
            if len(selected) < 3:
                st.warning("⚠️ اختر 3 مكونات على الأقل.")
            else:
                play_audio(f"جاري الحساب لـ {display_name}.")
                st.info("🔄 جاري الحساب...")
                
                c_vec = [prices[i] for i in selected]
                bounds = [(0.0, 100.0) for _ in selected]
                A_eq = [[1.0 for _ in selected]]
                b_eq = [100.0]
                
                dp_row, se_row, ndf_row, adf_row = [], [], [], []
                for i in selected:
                    fd = FLAT_FEEDS.get(i, {})
                    dp_row.append(fd.get("CP", 0) * fd.get("DC", 0))
                    se_row.append(fd.get("SE", 0))
                    ndf_row.append(fd.get("NDF", 0))
                    adf_row.append(fd.get("ADF", 0))
                
                A_eq.append(dp_row)
                b_eq.append(actual_dp * 100.0)
                
                A_ub = [[-x for x in se_row]]
                b_ub = [-ts * 100.0]
                
                if animal_key in ["cattle", "sheep", "goat", "camel"]:
                    A_ub.append(ndf_row); b_ub.append(35.0 * 100.0)
                    A_ub.append(adf_row); b_ub.append(20.0 * 100.0)
                elif animal_key == "horse":
                    A_ub.append(ndf_row); b_ub.append(40.0 * 100.0)
                
                if "نخالة قمح (ردة)" in selected:
                    idx = selected.index("نخالة قمح (ردة)")
                    row = [0.0] * len(selected); row[idx] = 1.0
                    A_ub.append(row)
                    b_ub.append(25.0 if animal_key in ["cattle","sheep","goat","camel"] else 15.0)
                
                # إضافات إلزامية
                if animal_key in ["cattle", "sheep", "goat", "camel"]:
                    if "بيكربونات الصوديوم" not in selected:
                        selected.append("بيكربونات الصوديوم")
                        prices["بيكربونات الصوديوم"] = 340.0
                        c_vec.append(340.0)
                        dp_row.append(0.0); se_row.append(0.0)
                        ndf_row.append(0.0); adf_row.append(0.0)
                        bounds.append((0.75, 0.75))
                
                if animal_key in ["poultry", "fish"]:
                    if "إنزيم الفايتيز" not in selected:
                        selected.append("إنزيم الفايتيز")
                        prices["إنزيم الفايتيز"] = 1200.0
                        c_vec.append(1200.0)
                        dp_row.append(0.0); se_row.append(0.0)
                        ndf_row.append(0.0); adf_row.append(0.0)
                        bounds.append((0.05, 0.05))
                
                A_eq = [[1.0 for _ in selected], dp_row]
                b_eq = [100.0, actual_dp * 100.0]
                
                try:
                    res = linprog(c_vec, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                                 bounds=bounds, method='highs')
                    
                    if res.success:
                        formula = {}
                        calc_se = 0.0
                        calc_dp = 0.0
                        for idx, i in enumerate(selected):
                            if res.x[idx] > 0.0001:
                                formula[i] = res.x[idx]
                                fd = FLAT_FEEDS.get(i, {})
                                calc_se += (res.x[idx] / 100.0) * fd.get("SE", 0.0)
                                calc_dp += (res.x[idx] / 100.0) * fd.get("CP", 0.0) * fd.get("DC", 0.0)
                        
                        cost = res.fun / 100.0
                        std = STANDARDS.get(display_name, {}).get(stage, {})
                        
                        warns = []
                        meets = True
                        if std:
                            if 'DP' in std:
                                r = calc_dp / std['DP'] * 100 if std['DP'] > 0 else 0
                                if r < 75:
                                    meets = False
                                    warns.append(f"DP: {r:.1f}% (< 75%)")
                            if 'SE' in std:
                                r = calc_se / std['SE'] * 100 if std['SE'] > 0 else 0
                                if r < 75:
                                    meets = False
                                    warns.append(f"SE: {r:.1f}% (< 75%)")
                        
                        if not meets:
                            st.error("❌ الخلطة لا تلبي 75% من المعايير.")
                            for w in warns:
                                st.warning(f"⚠️ {w}")
                        else:
                            st.success(f"✅ التكلفة: ${cost:.2f}/طن")
                            play_audio(f"تم التوليد بتكلفة {cost:.2f} دولار")
                            
                            cr1, cr2 = st.columns([0.6, 0.4])
                            with cr1:
                                for k, v in formula.items():
                                    st.markdown(f'<div class="formula-item"><span>{k}</span><span>{v:.2f}% ({v*10:.1f} كجم)</span></div>', unsafe_allow_html=True)
                                st.metric("💰 التكلفة للطن", f"${cost:.2f}")
                                st.metric("🧬 DP المحقق", f"{calc_dp:.2f}%")
                                st.metric("🌽 SE المحقق", f"{calc_se:.2f}")
                                
                                if requester:
                                    st.info(f"👤 طالب العلف: {requester}")
                                
                                if std:
                                    st.markdown("#### 📊 المقارنة:")
                                    comp = []
                                    if 'DP' in std:
                                        dev = ((calc_dp - std['DP']) / std['DP']) * 100
                                        g = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                                        comp.append({"المقياس": "DP", "المحسوب": f"{calc_dp:.2f}%",
                                                    "القياسي": f"{std['DP']:.2f}%",
                                                    "الانحراف": f"{dev:.1f}%", "التقييم": g})
                                    if 'SE' in std:
                                        dev = ((calc_se - std['SE']) / std['SE']) * 100
                                        g = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                                        comp.append({"المقياس": "SE", "المحسوب": f"{calc_se:.2f}",
                                                    "القياسي": f"{std['SE']:.2f}",
                                                    "الانحراف": f"{dev:.1f}%", "التقييم": g})
                                    st.table(pd.DataFrame(comp))
                                
                                try:
                                    pdf = pdf_gen.formula_report(formula, calc_dp, calc_se,
                                                                 f"{breed} - {stage}", cost,
                                                                 requester, std)
                                    st.download_button("📥 تحميل PDF",
                                                       pdf, file_name=f"Formula_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                                       mime="application/pdf", use_container_width=True,
                                                       key=f"{animal_key}_pdf")
                                except Exception as e:
                                    st.warning(f"⚠️ {e}")
                            
                            with cr2:
                                if len(formula) > 1:
                                    fig = px.pie(values=list(formula.values()),
                                                names=list(formula.keys()),
                                                title="توزيع المكونات",
                                                color_discrete_sequence=px.colors.sequential.Greens)
                                    fig.update_layout(height=400)
                                    st.plotly_chart(fig, use_container_width=True)
                            
                            st.session_state["active_formula"] = formula
                            st.session_state["computed_dp"] = calc_dp
                            st.session_state["computed_se"] = calc_se
                            st.session_state["computed_cost"] = cost
                            st.session_state["active_breed"] = f"{breed} - {stage}"
                    else:
                        st.error("❌ تعذر إيجاد حل. أضف مكونات.")
                except Exception as e:
                    st.error(f"❌ {e}")
    
    with cbtn[1]:
        if st.button("📋 المعايير", use_container_width=True, key=f"{animal_key}_std"):
            std = STANDARDS.get(display_name, {}).get(stage, {})
            if std:
                st.info(f"📊 DP={std.get('DP','-')}%, SE={std.get('SE','-')}, CP={std.get('CP','-')}%")
    
    with cbtn[2]:
        if st.button("🔊 استماع", use_container_width=True, key=f"{animal_key}_v"):
            play_audio(f"قسم {display_name}. اختر السلالة والمكونات ثم شغّل المحرك.")

# =====================================================================
# المختبر المتقدم مع الرسم البياني
# =====================================================================
def render_lab():
    st.markdown('<div class="section-title">🔬 المختبر المتقدم</div>', unsafe_allow_html=True)
    st.info("أدخل أوزان المكونات لتحليل الخلطة ومقارنتها مع المعايير القياسية مع رسم بياني.")
    
    c1, c2 = st.columns([0.5, 0.5])
    with c1:
        lab_animal = st.selectbox("الفصيل:",
            ["أبقار", "أغنام", "ماعز", "خيول", "إبل", "دواجن", "أسماك"],
            key="lab_an")
        stages = list(STANDARDS.get(lab_animal, {}).keys())
        lab_stage = st.selectbox("المرحلة:", stages if stages else ["عام"], key="lab_st")
        std = STANDARDS.get(lab_animal, {}).get(lab_stage, {})
        if std:
            st.info(f"📊 المعايير: DP={std.get('DP','-')}% | SE={std.get('SE','-')} | CP={std.get('CP','-')}%")
    
    with c2:
        st.markdown("#### 📝 اسم العينة:")
        sample_name = st.text_input("اسم العينة:", value=f"عينة {lab_animal} - {lab_stage}",
                                    key="lab_name")
    
    st.markdown("### 📥 أدخل أوزان المكونات (كجم):")
    lab_inputs = {}
    cols = st.columns(3)
    all_ings = list(FLAT_FEEDS.keys())
    for idx, i in enumerate(all_ings):
        with cols[idx % 3]:
            lab_inputs[i] = st.number_input(f"{i}", min_value=0.0, value=0.0,
                                            step=5.0, key=f"lab_i_{i}")
    
    if st.button("🧪 تشغيل التحليل المخبري", type="primary",
                 use_container_width=True, key="lab_run"):
        total = sum(lab_inputs.values())
        if total <= 0:
            st.warning("⚠️ أدخل أوزاناً أكبر من الصفر.")
        else:
            play_audio(f"جاري تشغيل التحليل لـ {lab_animal}.")
            st.info("🔄 جاري التحليل...")
            
            cp_t, dp_t, se_t = 0.0, 0.0, 0.0
            dc_t = 0.0
            comps = []
            for i, w in lab_inputs.items():
                if w > 0:
                    pct = w / total
                    fd = FLAT_FEEDS.get(i, {})
                    cp = fd.get("CP", 0)
                    dc = fd.get("DC", 0)
                    se = fd.get("SE", 0)
                    cp_t += pct * cp
                    dp_t += pct * (cp * dc)
                    se_t += pct * se
                    dc_t += pct * dc
                    comps.append({"المادة": i, "الوزن (كجم)": w, "النسبة %": f"{pct*100:.2f}"})
            
            st.success("🔬 تم التحليل بنجاح!")
            play_audio("تم التحليل بنجاح.")
            
            st.markdown(f"### ⚖️ إجمالي الوزن: **{total:.1f} كجم**")
            
            with st.expander("📋 تفاصيل المكونات"):
                st.table(pd.DataFrame(comps))
            
            # النتائج الأساسية
            st.markdown("### 📊 النتائج المحسوبة")
            cr = st.columns(4)
            cr[0].metric("CP", f"{cp_t:.2f}%")
            cr[1].metric("DC", f"{dc_t:.2f}")
            cr[2].metric("DP", f"{dp_t:.2f}%")
            cr[3].metric("SE", f"{se_t:.2f}")
            
            # المقارنة مع المعايير
            if std:
                st.markdown("### 📏 المقارنة مع المعايير القياسية")
                
                dp_dev = ((dp_t - std.get('DP', 0)) / std.get('DP', 1)) * 100 if std.get('DP', 0) > 0 else 0
                se_dev = ((se_t - std.get('SE', 0)) / std.get('SE', 1)) * 100 if std.get('SE', 0) > 0 else 0
                cp_dev = ((cp_t - std.get('CP', 0)) / std.get('CP', 1)) * 100 if std.get('CP', 0) > 0 else 0
                
                g_dp = "✅ ممتاز" if abs(dp_dev) <= 5 else ("⚠️ جيد" if abs(dp_dev) <= 10 else "❌ ضعيف")
                g_se = "✅ ممتاز" if abs(se_dev) <= 5 else ("⚠️ جيد" if abs(se_dev) <= 10 else "❌ ضعيف")
                g_cp = "✅ ممتاز" if abs(cp_dev) <= 5 else ("⚠️ جيد" if abs(cp_dev) <= 10 else "❌ ضعيف")
                
                eval_df = pd.DataFrame([
                    {"المقياس": "DP", "المحسوب": f"{dp_t:.2f}%",
                     "القياسي": f"{std.get('DP', 0):.2f}%",
                     "الانحراف": f"{dp_dev:.1f}%", "التقييم": g_dp},
                    {"المقياس": "SE", "المحسوب": f"{se_t:.2f}",
                     "القياسي": f"{std.get('SE', 0):.2f}",
                     "الانحراف": f"{se_dev:.1f}%", "التقييم": g_se},
                    {"المقياس": "CP", "المحسوب": f"{cp_t:.2f}%",
                     "القياسي": f"{std.get('CP', 0):.2f}%",
                     "الانحراف": f"{cp_dev:.1f}%", "التقييم": g_cp}
                ])
                st.table(eval_df)
                
                # الرسم البياني المقارن
                st.markdown("### 📊 الرسم البياني للمقارنة")
                metrics = ['DP', 'SE', 'CP']
                calc_vals = [dp_t, se_t, cp_t]
                std_vals = [std.get('DP', 0), std.get('SE', 0), std.get('CP', 0)]
                
                fig = go.Figure()
                fig.add_trace(go.Bar(x=metrics, y=calc_vals, name='المحسوب',
                                    marker_color='#2e7d32',
                                    text=[f'{v:.2f}' for v in calc_vals],
                                    textposition='outside'))
                fig.add_trace(go.Bar(x=metrics, y=std_vals, name='القياسي',
                                    marker_color='#1565C0',
                                    text=[f'{v:.2f}' for v in std_vals],
                                    textposition='outside'))
                fig.update_layout(
                    title='مقارنة النتائج المحسوبة مع المعايير القياسية',
                    barmode='group',
                    height=450,
                    showlegend=True,
                    yaxis_title='القيمة',
                    plot_bgcolor='#f8f9fa',
                    paper_bgcolor='#ffffff'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # التوصيات
                st.markdown("### 📌 التوصيات المخبرية")
                if abs(dp_dev) <= 5 and abs(se_dev) <= 5 and abs(cp_dev) <= 5:
                    st.success("✅ الخلطة مطابقة تماماً للمعايير — جودة ممتازة")
                else:
                    if dp_dev < -10:
                        st.warning("⚠️ البروتين المهضوم أقل من المعيار — أضف مصادر بروتين")
                    elif dp_dev > 10:
                        st.info("ℹ️ البروتين المهضوم أعلى من المعيار — يمكن تقليل التكلفة")
                    if se_dev < -10:
                        st.warning("⚠️ الطاقة (SE) أقل من المعيار — أضف مصادر طاقة")
                    elif se_dev > 10:
                        st.info("ℹ️ الطاقة (SE) أعلى من المعيار — مراجعة التركيبة")
            
            # تحميل PDF
            try:
                pdf = pdf_gen.lab_report(cp_t, dp_t, se_t, dc_t, lab_animal, lab_stage, std)
                st.download_button("📥 تحميل تقرير PDF",
                                   pdf,
                                   file_name=f"Lab_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                   mime="application/pdf", use_container_width=True,
                                   key="lab_pdf")
            except Exception as e:
                st.warning(f"⚠️ تعذر إنشاء PDF: {e}")

# =====================================================================
# بدائل الحليب
# =====================================================================
def render_milk():
    st.markdown('<div class="section-title">🍼 تركيب بديل الحليب</div>', unsafe_allow_html=True)
    
    animal_type = st.selectbox("الحيوان:", ["عجل بقري", "حملان", "جديان", "مهرات", "أطفال إبل"],
                               key="mr_an")
    age = st.slider("العمر (يوم)", 1, 120, 30, 1, key="mr_age")
    
    needs = {
        "عجل بقري": {"p": 22, "f": 18, "e": 75, "v": 8},
        "حملان": {"p": 24, "f": 20, "e": 72, "v": 4},
        "جديان": {"p": 23, "f": 19, "e": 70, "v": 3},
        "مهرات": {"p": 20, "f": 15, "e": 68, "v": 5},
        "أطفال إبل": {"p": 21, "f": 17, "e": 66, "v": 6}
    }
    
    af = 1.2 if age < 14 else (1.0 if age < 30 else (0.85 if age < 60 else 0.70))
    tp = needs[animal_type]["p"] * af
    tf = needs[animal_type]["f"] * af
    te = needs[animal_type]["e"] * af
    dv = needs[animal_type]["v"] * af
    
    st.info(f"📊 بروتين {tp:.1f}% | دهون {tf:.1f}% | طاقة {te:.1f} | حجم {dv:.1f} لتر/يوم")
    
    ingredients = {
        "حليب مجفف": {"CP": 34.0, "Fat": 1.0, "SE": 40.0, "Cost": 18.0},
        "مصل الحليب (Whey)": {"CP": 12.0, "Fat": 1.0, "SE": 35.0, "Cost": 12.0},
        "دهن نباتي": {"CP": 0.0, "Fat": 99.0, "SE": 10.0, "Cost": 8.0},
        "ليسيثين الصويا": {"CP": 0.0, "Fat": 95.0, "SE": 0.0, "Cost": 15.0},
        "بروتين الصويا": {"CP": 65.0, "Fat": 1.0, "SE": 30.0, "Cost": 20.0},
    }
    
    selected = []
    prices = {}
    cols = st.columns(3)
    for i, (ing, data) in enumerate(ingredients.items()):
        with cols[i % 3]:
            if st.checkbox(ing, value=(i < 3), key=f"mr_{ing}"):
                selected.append(ing)
                prices[ing] = st.number_input(f"سعر {ing}",
                                              min_value=1.0,
                                              value=float(data["Cost"]),
                                              step=0.5, key=f"mrp_{ing}")
    
    if st.button("🍼 تشغيل المحرك", type="primary", key="mr_run"):
        if len(selected) < 3:
            st.warning("⚠️ اختر 3 مكونات على الأقل")
        else:
            with st.spinner("جاري الحساب..."):
                try:
                    c = [prices[i] for i in selected]
                    bounds = [(0, 100) for _ in selected]
                    A_eq = [[1] * len(selected)]
                    b_eq = [100]
                    fat_row = [ingredients[i]["Fat"] for i in selected]
                    eng_row = [ingredients[i]["SE"] for i in selected]
                    
                    A_ub = [fat_row, [-x for x in eng_row]]
                    b_ub = [tf * 1.1, -te * 0.85]
                    
                    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                                 bounds=bounds, method='highs')
                    
                    if res.success:
                        formula = {selected[i]: res.x[i] for i in range(len(selected))
                                  if res.x[i] > 0.0001}
                        cost = res.fun / 100.0
                        
                        st.success(f"✅ التكلفة: ${cost:.2f}/كجم")
                        for k, v in formula.items():
                            st.markdown(f'<div class="formula-item"><span>{k}</span><span>{v:.1f}% ({v*10:.1f} جم/كجم)</span></div>', unsafe_allow_html=True)
                        
                        instructions = f"""الجرعة اليومية: {dv:.1f} لتر مقسمة على 3-4 وجبات
التركيز: 100-150 جم مسحوق لكل لتر ماء دافئ (40-45 درجة)
درجة الحرارة: 38-40 درجة مئوية
التخزين: مكان بارد وجاف — استخدم خلال 24 ساعة"""
                        
                        try:
                            pdf = pdf_gen.milk_report(formula, animal_type, age, instructions)
                            st.download_button("📥 تحميل PDF", pdf,
                                               file_name=f"Milk_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                               mime="application/pdf", key="mr_pdf")
                        except Exception as e:
                            st.warning(f"⚠️ {e}")
                except Exception as e:
                    st.error(f"❌ {e}")

# =====================================================================
# مواقيت الصلاة
# =====================================================================
def render_prayer():
    st.markdown('<div class="section-title">🕌 مواقيت الصلاة</div>', unsafe_allow_html=True)
    cities = ["مكة المكرمة", "المدينة المنورة", "الخرطوم", "طرابلس", "القاهرة",
              "دبي", "الرياض", "بغداد", "الكويت", "الدوحة"]
    city = st.selectbox("المدينة:", cities, key="pr_city")
    
    times = {"الفجر": "05:00", "الشروق": "06:30", "الظهر": "12:00",
             "العصر": "15:30", "المغرب": "18:00", "العشاء": "19:30"}
    
    cols = st.columns(3)
    for i, (name, t) in enumerate(times.items()):
        with cols[i % 3]:
            st.metric(name, t)
    
    if st.button("🔔 تنبيه صوتي", key="pr_alert"):
        now = datetime.now().strftime("%H:%M")
        nxt = None
        for n, t in times.items():
            if t > now:
                nxt = n
                break
        if nxt:
            play_audio(f"حان وقت صلاة {nxt} في {city}")
            st.success(f"✅ تم التشغيل لصلاة {nxt}")

# =====================================================================
# منبه الجرعات
# =====================================================================
def render_doses():
    st.markdown('<div class="section-title">💊 منبه الجرعات</div>', unsafe_allow_html=True)
    
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
        
        if st.button("💾 حفظ الجرعة", key="dr_save"):
            if dn:
                st.session_state["dose_reminders"].append({
                    'id': secrets.token_hex(8),
                    'animal': at, 'type': dt, 'name': dn,
                    'dose': da, 'unit': du, 'route': ar,
                    'freq': fd, 'start': sd.isoformat(),
                    'next': (sd + timedelta(days=fd)).isoformat()
                })
                st.success(f"✅ تم إضافة {dn}")
                st.rerun()
    
    if st.session_state["dose_reminders"]:
        st.subheader("📋 الجرعات المسجلة")
        for r in st.session_state["dose_reminders"]:
            with st.expander(f"💊 {r['name']} - {r['animal']}"):
                st.write(f"**الجرعة:** {r['dose']} {r['unit']}")
                st.write(f"**الطريقة:** {r['route']}")
                st.write(f"**التكرار:** كل {r['freq']} يوم")
                st.write(f"**البدء:** {r['start'][:10]}")
                st.write(f"**التالية:** {r['next'][:10]}")

# =====================================================================
# بورصة الأسعار
# =====================================================================
def render_prices():
    st.markdown('<div class="section-title">📊 بورصة الأسعار</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🐄 المواشي")
        for name, price in list(st.session_state["livestock_prices"].items()):
            np = st.number_input(name, value=float(price), step=5.0, key=f"pl_{name}")
            st.session_state["livestock_prices"][name] = np
    with c2:
        st.subheader("🥩 المنتجات")
        for name, price in list(st.session_state["products_prices"].items()):
            np = st.number_input(name, value=float(price), step=0.5, key=f"pp_{name}")
            st.session_state["products_prices"][name] = np

# =====================================================================
# إدارة المزارع
# =====================================================================
def render_farms():
    st.markdown('<div class="section-title">🐔 إدارة المزارع</div>', unsafe_allow_html=True)
    
    with st.expander("➕ إضافة مزرعة", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            fn = st.text_input("الاسم:", key="fr_n")
            ib = st.number_input("عدد الكتاكيت:", min_value=1, value=1000, step=100, key="fr_ib")
        with c2:
            br = st.selectbox("السلالة:", ["Ross 308", "Cobb 500", "محلية"], key="fr_br")
        
        if st.button("💾 إنشاء", key="fr_create"):
            if fn:
                cid = secrets.token_hex(8)
                st.session_state["farms"][cid] = {
                    "name": fn, "breed": br, "count": ib,
                    "age": 0, "weight": 0.045, "feed": 0, "dead": 0
                }
                st.success(f"✅ تم إنشاء {fn}")
                st.rerun()
    
    if st.session_state["farms"]:
        for cid, farm in st.session_state["farms"].items():
            with st.expander(f"🏠 {farm['name']} - {farm['breed']}"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("العدد", farm['count'])
                    st.metric("العمر", farm['age'])
                with c2:
                    st.metric("الوزن", f"{farm['weight']:.3f}")
                    st.metric("العلف", f"{farm['feed']:.1f}")
                with c3:
                    m = (farm['dead'] / farm['count']) * 100 if farm['count'] > 0 else 0
                    st.metric("النفوق %", f"{m:.1f}")
                    st.metric("النافق", farm['dead'])
                
                c1, c2 = st.columns(2)
                with c1:
                    nw = st.number_input("الوزن الحالي", min_value=0.01,
                                        value=float(farm['weight']), step=0.01, key=f"w_{cid}")
                    nf = st.number_input("العلف الكلي", min_value=0.0,
                                        value=float(farm['feed']), step=1.0, key=f"f_{cid}")
                with c2:
                    nd = st.number_input("نافق إضافي", min_value=0,
                                        value=0, step=1, key=f"d_{cid}")
                    na = st.number_input("العمر (يوم)", min_value=0,
                                        value=int(farm['age']), step=1, key=f"a_{cid}")
                
                if st.button("📊 تحديث", key=f"up_{cid}"):
                    farm['weight'] = nw
                    farm['feed'] = nf
                    farm['dead'] += nd
                    farm['age'] = na
                    st.success("✅ تم")
                    st.rerun()

# =====================================================================
# المراجع العلمية
# =====================================================================
def render_refs():
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
    
    refs = {
        "🐔 تغذية الدواجن": [
            "NRC (1994) — Nutrient Requirements of Poultry",
            "Leeson & Summers (2009) — Commercial Poultry Nutrition",
        ],
        "🐄 تغذية المجترات": [
            "NRC (2001) — Nutrient Requirements of Dairy Cattle",
            "NRC (2000) — Nutrient Requirements of Beef Cattle",
            "Church (1993) — The Ruminant Animal",
        ],
        "🐏 الأغنام والماعز": [
            "NRC (2007) — Nutrient Requirements of Small Ruminants",
        ],
        "🐴 تغذية الخيول": [
            "NRC (2007) — Nutrient Requirements of Horses",
        ],
        "🐫 تغذية الإبل": [
            "Faye (2018) — Camel Nutrition (FAO)",
        ],
        "🐟 تغذية الأسماك": [
            "Halver & Hardy (2002) — Fish Nutrition",
        ],
        "🧬 البروتين المهضوم": [
            "INRA (2007) — INRA Feeding System for Ruminants",
            "Pesti & Miller (2009) — Least-Cost Feed Formulation",
        ],
        "🍼 بدائل الحليب": [
            "Davis & Drackley (1998) — The Young Calf",
        ],
    }
    
    for cat, items in refs.items():
        with st.expander(cat):
            for r in items:
                st.markdown(f"▪️ {r}")
    
    st.subheader("💡 المعرفة السريعة")
    q = st.text_input("اسأل عن مصطلح:", key="kb")
    if q:
        kb = {
            "البروتين المهضوم": "البروتين المهضوم (DP) = CP × DC — هو الجزء الذي يستفيد منه الحيوان فعلياً.",
            "معادل النشاء": "معادل النشاء (SE) يقيس كمية الطاقة في العلف مقارنة بالنشاء النقي.",
            "تركيب العلف": "باستخدام Linear Programming لحساب أقل تكلفة.",
            "مؤشر EPEF": "EPEF = (الحيوية × الوزن) / (العمر × FCR) × 100.",
            "FCR": "معامل التحويل = العلف / الوزن المكتسب.",
        }
        for k, v in kb.items():
            if k in q:
                st.success(f"📖 {v}")
                break
        else:
            st.info("لم أجد إجابة — راجع المراجع أعلاه.")

# =====================================================================
# المساعدة
# =====================================================================
def render_help():
    st.markdown('<div class="section-title">💡 المساعدة</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#e3f2fd; padding:20px; border-radius:12px; direction:rtl;'>
    <h3>🌟 خطوات الاستخدام:</h3>
    <ol>
    <li>اختر نوع الحيوان من تبويب "تركيب الأعلاف"</li>
    <li>حدد السلالة والمرحلة</li>
    <li>أدخل القياسات (إن وجدت)</li>
    <li>اختر المكونات وحدد أسعارها</li>
    <li>اضغط "تشغيل المحرك"</li>
    <li>حمل التقرير PDF</li>
    </ol>
    <h3>📞 الدعم الفني:</h3>
    <p>abukram128@gmail.com | +249123533489</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔊 استماع للتعليمات", key="help_v"):
        play_audio("مرحباً، هذا دليل استخدام منصة تاور نولجي العلمية.")

# =====================================================================
# دليل المستخدم
# =====================================================================
def render_guide():
    st.markdown('<div class="section-title">📖 دليل المستخدم</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="manual-book">
    <div class="book-chapter">📘 الفصل 1: مقدمة</div>
    <div class="book-body">
    تاور نولجي Tawornology العلمية منصة متكاملة لتركيب الأعلاف وإدارة الإنتاج الحيواني.
    تعتمد على البرمجة الخطية لحساب أقل تكلفة.
    <br><br>
    <b>المشرف:</b> {OWNER_NAME}
    </div>
    
    <div class="book-chapter">📗 الفصل 2: تركيب العلف</div>
    <div class="book-body">
    1. اختر نوع الحيوان<br>
    2. حدد السلالة والمرحلة<br>
    3. أدخل العمر والحالة<br>
    4. اختر المكونات<br>
    5. اضغط "تشغيل المحرك"<br>
    6. حمل PDF
    </div>
    
    <div class="book-chapter">📕 الفصل 3: المختبر المتقدم</div>
    <div class="book-body">
    أدخل أوزان المكونات لتحليل الخلطة، مع رسم بياني يقارن المحسوب بالقياسي.
    </div>
    
    <div class="book-chapter">🍼 الفصل 4: بدائل الحليب</div>
    <div class="book-body">
    تركيب بديل حليب للصغار حسب العمر والنوع.
    </div>
    
    <div class="book-chapter">🕌 الفصل 5: مواقيت الصلاة</div>
    <div class="book-body">
    عرض مواقيت الصلاة حسب المدينة المختارة.
    </div>
    
    <div class="book-chapter">💊 الفصل 6: منبه الجرعات</div>
    <div class="book-body">
    تسجيل ومتابعة جرعات اللقاحات والفيتامينات.
    </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================================
# إرسال الكود (للمالك فقط)
# =====================================================================
def render_send():
    st.markdown('<div class="section-title">📧 إرسال الكود</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#e3f2fd,#bbdefb); padding:18px; border-radius:14px; direction:rtl;'>
    <b>📌 للحصول على App Password من Google:</b><br>
    1. اذهب إلى <b>myaccount.google.com/apppasswords</b><br>
    2. أنشئ كلمة مرور جديدة للتطبيق<br>
    3. انسخها (16 حرفاً) والصقها هنا
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    email = st.text_input("📧 البريد:", value=OWNER_EMAIL, key="send_e")
    pw = st.text_input("🔑 كلمة مرور التطبيق:", type="password",
                       placeholder="16 حرفاً بدون مسافات", key="send_p")
    
    if st.button("📤 إرسال الكود", type="primary", use_container_width=True, key="send_b"):
        if not email or '@' not in email:
            st.error("⚠️ بريد غير صحيح")
        elif not pw:
            st.error("⚠️ أدخل كلمة مرور التطبيق")
        else:
            with st.spinner("جاري الإرسال..."):
                ok, msg = send_code_email(email, pw)
                if ok:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)

# =====================================================================
# التبويبات
# =====================================================================
role = st.session_state.get("user_role", "public")

if role == "owner":
    tabs = st.tabs([
        "🐾 تركيب الأعلاف",
        "🔬 المختبر المتقدم",
        "🍼 بدائل الحليب",
        "🕌 مواقيت الصلاة",
        "💊 منبه الجرعات",
        "📊 بورصة الأسعار",
        "🐔 إدارة المزارع",
        "📚 المراجع العلمية",
        "💡 المساعدة",
        "📖 دليل المستخدم",
        "📧 إرسال الكود",
    ])
else:
    tabs = st.tabs([
        "🐾 تركيب الأعلاف",
        "🔬 المختبر المتقدم",
        "📚 المراجع العلمية",
        "💡 المساعدة",
        "📖 دليل المستخدم",
    ])
    st.info("""
    👋 **مرحباً بك كزائر!**
    
    متاح للزوار: تركيب الأعلاف، المختبر المتقدم، المراجع، المساعدة، الدليل
    
    🔒 **حصرية للمالك:** بدائل الحليب، مواقيت الصلاة، منبه الجرعات،
    بورصة الأسعار، إدارة المزارع، إرسال الكود
    """)

# =====================================================================
# رسم التبويبات
# =====================================================================
with tabs[0]:
    guide("تركيب الأعلاف", "اختر نوع الحيوان، أدخل البيانات، ثم شغّل المحرك.")
    animal_tabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐴 خيول",
                            "🐫 إبل", "🐔 دواجن", "🐟 أسماك"])
    with animal_tabs[0]:
        render_formulation("cattle", "أبقار", "🐄",
            ["كنانة", "بطانة", "هولشتاين/محسن"],
            ["تسمين عجول", "حليب/إدرار", "حمل/دفع غذائي", "صيانة"],
            12.0, 65.0, True)
    with animal_tabs[1]:
        render_formulation("sheep", "أغنام", "🐏",
            ["الضأن الصحراوي", "البربري", "النعيمي"],
            ["تسمين حملان", "نعاج مرضعات", "نعاج حامل", "نعاج جافة"],
            11.5, 62.0, True)
    with animal_tabs[2]:
        render_formulation("goat", "ماعز", "🐐",
            ["النوبي", "الصحراوي", "بور/محسن"],
            ["تسمين جديان", "عنزات حلابة", "عنزات حامل", "صيانة"],
            11.0, 60.0, True)
    with animal_tabs[3]:
        render_formulation("horse", "خيول", "🐴",
            ["خيل عربي أصيل", "ثوروبريد", "محلية"],
            ["راحة/صيانة", "عمل خفيف", "عمل متوسط", "عمل مكثف", "سباق"],
            11.0, 62.0, True)
    with animal_tabs[4]:
        render_formulation("camel", "إبل", "🐫",
            ["عربية (دروميداري)", "باختري", "هجين"],
            ["راحة/صيانة", "حمل/رضاعة", "إنتاج حليب", "تسمين"],
            10.0, 58.0, True)
    with animal_tabs[5]:
        render_formulation("poultry", "دواجن", "🐔",
            ["دواجن لاحم", "دواجن بياض", "طائر السمان"],
            ["بادي (0-14 يوم)", "نامي (15-28 يوم)", "ناهي (29-42 يوم)"],
            18.0, 72.0, False)
    with animal_tabs[6]:
        render_formulation("fish", "أسماك", "🐟",
            ["البلطي النيلي", "القرموط"],
            ["زريعة/بادئ", "نمو", "تسمين نهائي"],
            28.0, 68.0, False)

with tabs[1]:
    guide("المختبر المتقدم", "أدخل أوزان المكونات لتحليل الخلطة مع الرسم البياني والمقارنة.")
    render_lab()

if role == "owner":
    with tabs[2]:
        guide("بدائل الحليب", "تركيب بديل الحليب للصغار.")
        render_milk()
    
    with tabs[3]:
        guide("مواقيت الصلاة", "مواقيت الصلاة حسب المدينة.")
        render_prayer()
    
    with tabs[4]:
        guide("منبه الجرعات", "تسجيل جرعات اللقاحات.")
        render_doses()
    
    with tabs[5]:
        guide("بورصة الأسعار", "أسعار المواشي والمنتجات.")
        render_prices()
    
    with tabs[6]:
        guide("إدارة المزارع", "متابعة دورات الدجاج.")
        render_farms()
    
    with tabs[7]:
        guide("المراجع العلمية", "مصادر معتمدة.")
        render_refs()
    
    with tabs[8]:
        guide("المساعدة", "دليل سريع.")
        render_help()
    
    with tabs[9]:
        guide("دليل المستخدم", "شرح مفصل.")
        render_guide()
    
    with tabs[10]:
        render_send()
else:
    with tabs[2]:
        guide("المراجع العلمية", "مصادر معتمدة.")
        render_refs()
    
    with tabs[3]:
        guide("المساعدة", "دليل سريع.")
        render_help()
    
    with tabs[4]:
        guide("دليل المستخدم", "شرح مفصل.")
        render_guide()

# =====================================================================
# التذييل
# =====================================================================
st.markdown(f"""
<div style='text-align:center; padding:20px; margin-top:30px; border-top:2px solid #e0e0e0; color:#888;'>
🌾 <b>تاور نولجي Tawornology العلمية</b><br>
© 2026 | {OWNER_NAME}<br>
🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b> — رحمهما الله
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

print("=" * 70)
print("🌾 تاور نولجي Tawornology v18.0 — جاهز للتشغيل")
print(f"👤 المشرف: {OWNER_NAME}")
print("=" * 70)
