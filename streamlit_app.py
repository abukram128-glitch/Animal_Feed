# Digital Signature: 3495cb0eef8355d2f9b0ff82e16e98fb
# Generated: 2026-05-30T22:57:38.541717

import streamlit as st
import numpy as np
import pandas as pd
import json, os, base64, smtplib, time, urllib.parse, hashlib, secrets, io, qrcode
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scipy.optimize import linprog
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import arabic_reshaper
from bidi.algorithm import get_display
import matplotlib.pyplot as plt

st.set_page_config(page_title="منصة تاور العلمية", page_icon="🌾", layout="wide", initial_sidebar_state="collapsed")

# ------------------- التواقيع والحماية -------------------
@st.cache_resource
def init_caching_system():
    return {"cache_hits": 0, "cache_misses": 0, "last_cleanup": datetime.now()}
CACHE_SYSTEM = init_caching_system()

CODES_DB = {
    "202687": {"role": "owner", "name": "الاختصاصي م. عبد القادر إسماعيل تاور", "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}
PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"
SENDER_PASSWORD = "oynz rdli tsdy ekdq"
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"
GOOGLE_FORM_URL = "https://forms.google.com/YOUR_FORM_URL"

@st.cache_data(ttl=3600)
def get_image_base64(paths):
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except:
                pass
    return None
img_base64 = get_image_base64(PHOTO_OPTIONS)

def send_code_to_mail(receiver_email):
    if SENDER_EMAIL == "YOUR_EMAIL@gmail.com" or not SENDER_PASSWORD:
        st.error("⚠️ خطأ إعدادات SMTP")
        return False
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود - منصة تاور العلمية"
    body = "مرفق الكود الكامل للمنصة."
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code_content = f.read()
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
        st.error(f"فشل الإرسال: {e}")
        return False

class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=1000)
    def fix_arabic_text(text: str) -> str:
        return get_display(arabic_reshaper.reshape(text))
arabic_processor = ArabicTextProcessor()

class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = 'Helvetica'
        if os.path.exists("Amiri-Regular.ttf"):
            try:
                pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
                self.font_name = 'Amiri'
            except:
                pass
    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city, local_cost, local_sym, computed_se, include_charts=True):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        def p(text, size=12, align=TA_RIGHT, color=HexColor('#000000')):
            safe = arabic_processor.fix_arabic_text(str(text))
            return Paragraph(safe, ParagraphStyle('style', fontName=self.font_name, fontSize=size, alignment=align, textColor=color, spaceAfter=6, leading=size*1.5))
        story.append(p("تقرير فني شامل - منصة تاور العلمية", size=22, align=TA_CENTER, color=HexColor('#1b5e20')))
        story.append(Spacer(1,12))
        for line in [f"المشرف: م. عبد القادر إسماعيل تاور", f"الموقع: {city}", f"الفصيل: {breed}", f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}"]:
            story.append(p(line, size=11))
        story.append(Spacer(1,15))
        tdata = [[arabic_processor.fix_arabic_text('المعيار'), arabic_processor.fix_arabic_text('القيمة')],
                 [arabic_processor.fix_arabic_text('البروتين المهضوم (DP)'), f'{target_dp:.2f}%'],
                 [arabic_processor.fix_arabic_text('معادل النشاء (SE)'), f'{computed_se:.2f} وحدة'],
                 [arabic_processor.fix_arabic_text('التكلفة للطن'), f'${cost:.2f} ({local_cost:,.2f} {local_sym})']]
        t = Table(tdata, colWidths=[250,250])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#1b5e20')),('TEXTCOLOR',(0,0),(-1,0),white),('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),('FONTSIZE',(0,0),(-1,-1),11),('GRID',(0,0),(-1,-1),1,HexColor('#2e7d32'))]))
        story.append(t); story.append(Spacer(1,20))
        story.append(p("المقادير لتركيب الطن:", size=14, color=HexColor('#2e7d32'))); story.append(Spacer(1,10))
        ing_data = [[arabic_processor.fix_arabic_text('المكون'), arabic_processor.fix_arabic_text('النسبة %'), arabic_processor.fix_arabic_text('كجم/طن')]]
        for ing, pct in formula.items():
            ing_data.append([arabic_processor.fix_arabic_text(ing), f'{pct:.2f}%', f'{pct*10:.1f}'])
        t2 = Table(ing_data, colWidths=[200,150,150])
        t2.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#2e7d32')),('TEXTCOLOR',(0,0),(-1,0),white),('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTNAME',(0,0),(-1,-1),self.font_name),('FONTSIZE',(0,0),(-1,-1),10),('GRID',(0,0),(-1,-1),1,HexColor('#bdbdbd'))]))
        story.append(t2); story.append(Spacer(1,15))
        if include_charts and len(formula)>1:
            try:
                fig,ax=plt.subplots(figsize=(6,3.5))
                names=list(formula.keys()); vals=list(formula.values())
                colors=['#1b5e20','#2e7d32','#388e3c','#43a047','#4caf50','#66bb6a']
                ax.pie(vals, labels=None, autopct='%1.1f%%', colors=colors[:len(names)])
                ax.legend([arabic_processor.fix_arabic_text(n) for n in names], title=arabic_processor.fix_arabic_text("المكونات"), loc='center left', bbox_to_anchor=(1,0,0.5,1), fontsize=8)
                ax.set_title(arabic_processor.fix_arabic_text('توزيع المكونات'), fontsize=12)
                buf=io.BytesIO(); plt.savefig(buf, format='png', dpi=100, bbox_inches='tight'); plt.close(); buf.seek(0)
                story.append(Image(buf, width=400, height=230))
            except:
                pass
        story.append(Spacer(1,25))
        story.append(p("تم التوليد بواسطة منصة تاور العلمية © 2026", size=9, align=TA_CENTER, color=HexColor('#666666')))
        doc.build(story); buffer.seek(0)
        return buffer.getvalue()
pdf_generator = ProfessionalPDFGenerator()

# ------------------- مكتبة الأعلاف -------------------
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
    "🚜 المخلفات الزراعية والصناعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5},
        "بقايا تفل البنجر المجفف": {"CP": 8.0, "DC": 0.75, "SE": 58.0, "NDF": 38.5, "ADF": 22.5, "EE": 1.5, "ASH": 6.5},
        "مخلفات مصانع البسكويت": {"CP": 9.5, "DC": 0.88, "SE": 76.0, "NDF": 8.5, "ADF": 3.5, "EE": 8.5, "ASH": 3.5},
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق أسماك فاخر (72%)": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5}
    },
    "🧪 الأحماض الأمينية": {
        "ليسين نقي": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5},
        "ميثيونين نقي": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3}
    },
    "🔬 الإضافات التخصصية": {
        "بريمكس تسمين دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم الفايتيز": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0}
    }
}

# ------------------- إدارة المخزون -------------------
class InventoryManager:
    @staticmethod
    def initialize_inventory():
        if "inventory" not in st.session_state:
            st.session_state["inventory"] = {}
            for cat in BIG_FEEDS_LIBRARY.values():
                for ing in cat:
                    st.session_state["inventory"][ing] = {"quantity": 25.0, "min_threshold": 5.0, "unit": "طن", "last_updated": datetime.now().isoformat()}
    @staticmethod
    def check_stock_levels():
        warnings = {}
        for item, data in st.session_state["inventory"].items():
            qty = data["quantity"]
            thresh = data["min_threshold"]
            if qty <= 0:
                warnings[item] = "نفذ"
            elif qty < thresh:
                warnings[item] = "منخفض"
        return warnings
InventoryManager.initialize_inventory()

# ------------------- بورصة الأسعار -------------------
if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {"عجول هولشتاين":1350.0, "أبقار كنانة":900.0, "ضأن محلي":180.0, "ماعز نوبي":130.0, "خيول عربية":4500.0, "كتكوت لاحم":0.65}
if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {"لحم بقري":7.50, "لحم ضأن":9.00, "لحم دجاج":3.80, "طبق بيض":4.20, "حليب خام":0.90}
if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = "• توجيه الاختصاصي م. عبد القادر إسماعيل تاور: مرحباً بالزملاء.\n"

EXCHANGE_RATES = {"السودان":{"rate":600.0,"sym":"SDG"},"LIBYA":{"rate":4.80,"sym":"LYD"},"مصر":{"rate":48.0,"sym":"EGP"},"باقي دول العالم":{"rate":1.0,"sym":"USD"}}

class MarketPriceEngine:
    @staticmethod
    @lru_cache(maxsize=128)
    def get_adjusted_market_data(country, state, city):
        feed_prices = {ing: 230.0 for cat in BIG_FEEDS_LIBRARY.values() for ing in cat}
        base = {"ذرة صفراء":230,"ذرة بيضاء":225,"شعير مطحون":210,"سورجم (فتريتة)":195,"قمح محلي مصنّع":240,"أمباز الفول السوداني (كسب)":460,"كسب فول صويا 44%":440,"نخالة قمح (ردة)":150,"مولاس قصب السكر":120,"مسحوق أسماك (Fishmeal 60%)":850,"مركزات دواجن وسمان":650,"مركزات خيول ومجترات":600,"الحجر الجيري":40,"فوسفات ثنائي الكالسيوم":280,"ملح الطعام":30,"بيكربونات الصوديوم":340}
        feed_prices.update(base)
        mult = 1.15 if country=="السودان" else 1.10 if country=="LIBYA" else 1.04 if country=="مصر" else 1.0
        for k in feed_prices:
            feed_prices[k] *= mult
        return feed_prices

ANIMAL_IMAGES_RESOURCES = {"أبقار":"https://images.unsplash.com/photo-1570042225831-d98fa7577f1e","ماعز":"https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c","أغنام":"https://images.unsplash.com/photo-1484557985045-edf25e08da73","خيول":"https://images.unsplash.com/photo-1553284965-83fd3e82fa5a","دواجن":"https://images.unsplash.com/photo-1548550023-2bdb3c5beed7","عام":"https://images.unsplash.com/photo-1500382017468-9049fed747ef"}

# متغيرات الجلسة العامة
if "active_formula" not in st.session_state: st.session_state["active_formula"] = {"ذرة صفراء":60, "كسب فول صويا 44%":35}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"]=12.0
if "active_se_tag" not in st.session_state: st.session_state["active_se_tag"]=65.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"]="سلالة عامة"
if "active_animal_img" not in st.session_state: st.session_state["active_animal_img"]=ANIMAL_IMAGES_RESOURCES["عام"]
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"]="إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"]=280.0
if "live_prices" not in st.session_state: st.session_state["live_prices"] = {}
if "local_rate" not in st.session_state: st.session_state["local_rate"] = 1.0
if "local_sym" not in st.session_state: st.session_state["local_sym"] = "USD"
if "user_city" not in st.session_state: st.session_state["user_city"] = "غير محدد"

# ------------------- إدارة الدجاج اللاحم -------------------
class BroilerFarmManager:
    STANDARD_PERFORMANCE = {7:{"weight_kg":0.180,"fcr":1.05,"mortality_cum":0.8},14:{"weight_kg":0.450,"fcr":1.25,"mortality_cum":1.2},21:{"weight_kg":0.850,"fcr":1.45,"mortality_cum":1.6},28:{"weight_kg":1.350,"fcr":1.65,"mortality_cum":2.0},35:{"weight_kg":1.900,"fcr":1.80,"mortality_cum":2.5},42:{"weight_kg":2.400,"fcr":1.90,"mortality_cum":3.0},49:{"weight_kg":2.800,"fcr":2.00,"mortality_cum":3.5},56:{"weight_kg":3.200,"fcr":2.10,"mortality_cum":4.0}}
    @staticmethod
    def get_standard_at_age(age): return BroilerFarmManager.STANDARD_PERFORMANCE[min(BroilerFarmManager.STANDARD_PERFORMANCE.keys(), key=lambda a: abs(a-age))]
    @staticmethod
    def calculate_adg(current_g, initial_g, age): return (current_g-initial_g)/age if age>0 else 0
    @staticmethod
    def calculate_fcr(feed_kg, gain_kg): return feed_kg/gain_kg if gain_kg>0 else 0
    @staticmethod
    def calculate_mortality(dead, initial): return (dead/initial)*100 if initial>0 else 0
    @staticmethod
    def calculate_livability(initial, dead): return 100 - BroilerFarmManager.calculate_mortality(dead, initial)
    @staticmethod
    def calculate_epef(livability, weight_kg, age, fcr): return (livability*weight_kg)/(age*fcr)*100 if age>0 and fcr>0 else 0
    @staticmethod
    def get_temp_humidity_table(): return pd.DataFrame({"العمر (يوم)":[1,7,14,21,28,35,42],"درجة الحرارة":[33,30,28,26,24,22,21],"الرطوبة":[65,65,65,60,60,55,55]})

BROILER_DATA_FILE = "broiler_farms_data.json"
def load_broiler_farms():
    if os.path.exists(BROILER_DATA_FILE):
        try:
            with open(BROILER_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}
def save_broiler_farms(data):
    with open(BROILER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
if "broiler_farms" not in st.session_state:
    st.session_state["broiler_farms"] = load_broiler_farms()
    if not st.session_state["broiler_farms"]:
        st.session_state["broiler_farms"] = {"farm_1":{"info":{"farm_name":"مزرعة النور","owner_name":"أحمد محمد","location":"الخرطوم","breed":"Ross 308","start_date":datetime.now().strftime("%Y-%m-%d"),"initial_birds":10000,"initial_weight_kg":0.045,"phone":""},"daily_records":[],"health_log":[]}}
        save_broiler_farms(st.session_state["broiler_farms"])
if "broiler_cycles_history" not in st.session_state: st.session_state["broiler_cycles_history"] = []

# ------------------- CSS -------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
* { font-family: 'Cairo', sans-serif; }
html, body, [data-testid="stAppViewContainer"] { background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600"); background-size: cover; background-attachment: fixed; }
.stApp { background: transparent; }
.main-box { background-color: rgba(255,255,255,0.98); padding: 30px; border-radius: 15px; box-shadow: 0px 10px 30px rgba(0,0,0,0.18); margin-bottom: 50px; backdrop-filter: blur(10px); }
.section-title { color: #1b5e20; border-right: 6px solid #2e7d32; padding-right: 15px; text-align: right; font-size: 1.5rem; font-weight: bold; margin-top: 30px; margin-bottom: 20px; background: linear-gradient(to left, rgba(46,125,50,0.1), transparent); padding: 10px 15px; border-radius: 8px; }
.profile-img-style { width: 150px; height: 150px; border-radius: 50%; object-fit: cover; border: 4px solid #d4af37; box-shadow: 0px 6px 20px rgba(0,0,0,0.25); display: block; margin: 0 auto; }
.mini-left-signature { position: fixed; left: 20px; bottom: 20px; background: linear-gradient(135deg, #1b5e20, #2e7d32); color: white; padding: 8px 20px; font-size: 0.85rem; border-radius: 25px; z-index: 9999; direction: rtl; }
.price-card { background: linear-gradient(135deg, #f1f8e9, #e8f5e9); padding: 20px; border-radius: 12px; border-right: 5px solid #2e7d32; margin-bottom: 20px; direction: rtl; }
.warning-card { background: linear-gradient(135deg, #fff3e0, #ffe0b2); padding: 15px; border-radius: 12px; border-right: 5px solid #f57c00; margin-bottom: 15px; }
.metric-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0px 4px 20px rgba(0,0,0,0.1); text-align: center; }
</style>
""", unsafe_allow_html=True)

# ------------------- بوابة الدخول -------------------
if "approved" not in st.session_state: st.session_state["approved"]=False
if "user_role" not in st.session_state: st.session_state["user_role"]=None
if "login_welcome_shown" not in st.session_state: st.session_state["login_welcome_shown"]=False
if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width:500px; margin:100px auto; direction:rtl;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:#2E7D32; text-align:center;'>🔒 بوابة الدخول</h2>")
    input_code = st.text_input("🔑 كود الدخول:", type="password")
    if st.button("تسجيل الدخول", type="primary", use_container_width=True):
        if input_code.strip() in CODES_DB:
            st.session_state["approved"]=True
            st.session_state["user_role"]=CODES_DB[input_code.strip()]["role"]
            st.session_state["login_welcome_shown"]=False
            st.rerun()
        else:
            st.error("كود خاطئ")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()
if not st.session_state["login_welcome_shown"]:
    st.toast(f"مرحباً {st.session_state['user_role']}", icon="👋")
    st.session_state["login_welcome_shown"]=True

# ------------------- الواجهة الرئيسية -------------------
st.markdown('<div class="main-box">', unsafe_allow_html=True)
col_logo, col_title = st.columns([0.3,0.7])
with col_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.image(ANIMAL_IMAGES_RESOURCES["عام"], width=150)
with col_title:
    st.markdown("<h1 style='color:#1b5e20; text-align:right;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#c62828; text-align:right;'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)
st.markdown("---")

# تحديد التبويبات حسب الدور
role = st.session_state["user_role"]
if role == "owner":
    tabs_titles = ["🔬 النمذجة والحسابات", "📊 بورصة الأسعار", "🏭 المخازن", "🧾 التسويق", "🖨️ الديباجة", "📈 التحليلات", "🐔 إدارة الدجاج (متقدم)", "💬 تعليقات", "📖 الدليل"]
elif role == "specialist":
    tabs_titles = ["🔬 النمذجة", "📊 بورصة الأسعار", "🏭 المخازن", "🧾 التسويق", "🖨️ الديباجة", "📈 التحليلات", "💬 تعليقات", "📖 الدليل"]
else:
    tabs_titles = ["🔬 النمذجة", "📖 الدليل"]
tabs = st.tabs(tabs_titles)

# ================== تبويب النمذجة ==================
with tabs[0]:
    st.markdown('<div class="section-title">🌍 تحديد الموقع الجغرافي وبورصة الأسعار</div>', unsafe_allow_html=True)
    col_country, col_state, col_city = st.columns(3)
    with col_country:
        user_country = st.selectbox("اختر دولة المربي:", ["السودان", "LIBYA", "مصر", "باقي دول العالم"])
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    st.session_state["local_rate"] = c_info["rate"]
    st.session_state["local_sym"] = c_info["sym"]
    local_rate = st.session_state["local_rate"]
    local_sym = st.session_state["local_sym"]
    with col_state:
        chosen_state = st.selectbox("الولاية/الإقليم:", ["الخرطوم", "الجزيرة", "القضارف"] if user_country=="السودان" else ["الشرقية", "الغربية"] if user_country=="LIBYA" else ["المركز الرئيسي"])
    with col_city:
        user_city = st.text_input("اسم المدينة:", "الخرطوم")
    st.session_state["user_city"] = user_city
    st.session_state["live_prices"] = MarketPriceEngine.get_adjusted_market_data(user_country, chosen_state, user_city)
    live_prices = st.session_state["live_prices"]
    col_view1, col_view2 = st.columns(2)
    with col_view1:
        st.markdown(f'<div class="price-card"><b>🐄 بورصة الماشية في {user_city}:</b><br>' + "<br>".join([f'▪️ {k}: ${v:.2f}' for k,v in st.session_state["global_livestock_prices"].items()]) + '</div>', unsafe_allow_html=True)
    with col_view2:
        st.markdown(f'<div class="price-card"><b>🥩 بورصة المنتجات في {user_city}:</b><br>' + "<br>".join([f'▪️ {k}: ${v:.2f}' for k,v in st.session_state["global_products_prices"].items()]) + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚖️ اختيار القطاع والنوع</div>', unsafe_allow_html=True)
    main_sector = st.selectbox("القطاع الإنتاجي:", ["أغنام", "ماعز", "أبقار", "خيول", "دواجن", "أسماك"])
    default_dp = 12.0 if main_sector in ["أغنام","ماعز"] else 11.0 if main_sector=="أبقار" else 9.5
    default_se = 64.0 if main_sector in ["أغنام","ماعز"] else 68.0 if main_sector=="أبقار" else 60.0
    col_p1, col_p2 = st.columns(2)
    use_cp = st.checkbox("استخدم البروتين الخام (CP) بدلاً من المهضوم", value=False)
    if use_cp:
        target_protein = st.slider("نسبة CP المطلوبة (%)", 5.0, 60.0, value=default_dp/0.82)
        final_target_dp = target_protein * 0.82
    else:
        final_target_dp = st.slider("نسبة البروتين المهضوم (DP) (%)", 5.0, 40.0, value=float(default_dp))
    final_target_se = st.slider("معادل النشاء (SE) المستهدف", 10.0, 90.0, value=float(default_se))
    st.markdown("---")
    if st.button("🚀 تشغيل محرك الاستمثال", type="primary", use_container_width=True):
        # نموذج مبسط للمحرك (يتم استخدام نفس الهيكل الأصلي)
        selected = ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)", "ملح الطعام"]
        prices = [live_prices.get(x, 300) for x in selected]
        bounds = [(0,100) for _ in selected]
        A_eq = [[1,1,1,1]]
        b_eq = [100]
        cp_row = []
        se_row = []
        for ing in selected:
            for cat in BIG_FEEDS_LIBRARY.values():
                if ing in cat:
                    cp_row.append(cat[ing]["CP"] * (1 if use_cp else cat[ing]["DC"]))
                    se_row.append(cat[ing]["SE"])
                    break
        A_eq.append(cp_row)
        b_eq.append(final_target_dp*100 if not use_cp else target_protein*100)
        A_ub = []
        b_ub = []
        A_ub.append([-x for x in se_row])
        b_ub.append(-final_target_se*100)
        res = linprog(prices, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        if res.success:
            formula = {selected[i]: res.x[i] for i in range(len(selected)) if res.x[i]>0.01}
            st.success("تم حساب الخلطة بنجاح")
            st.write(formula)
            st.session_state["active_formula"] = formula
            ton_cost = res.fun / 100.0
            st.session_state["computed_ton_cost"] = ton_cost
            st.metric("تكلفة الطن", f"${ton_cost:.2f}")
            # زر PDF
            try:
                pdf_data = pdf_generator.generate_comprehensive_report(formula, final_target_dp, main_sector, ton_cost, user_city, ton_cost*local_rate, local_sym, final_target_se)
                st.download_button("تحميل PDF", pdf_data, file_name="report.pdf")
            except Exception as e:
                st.error(f"خطأ في PDF: {e}")
        else:
            st.error("لم يتم إيجاد حل")

# ================== تبويب بورصة الأسعار ==================
with tabs[1]:
    st.markdown('<div class="section-title">📊 بورصة الأسعار المركزية</div>', unsafe_allow_html=True)
    st.subheader("أسعار الماشية")
    for animal, price in st.session_state["global_livestock_prices"].items():
        if role == "owner":
            st.session_state["global_livestock_prices"][animal] = st.number_input(animal, value=price, step=0.1)
        else:
            st.write(f"{animal}: ${price:.2f}")
    st.subheader("أسعار المنتجات")
    for prod, price in st.session_state["global_products_prices"].items():
        if role == "owner":
            st.session_state["global_products_prices"][prod] = st.number_input(prod, value=price, step=0.05)
        else:
            st.write(f"{prod}: ${price:.2f}")

# ================== تبويب المخازن ==================
with tabs[2]:
    st.markdown('<div class="section-title">🏭 إدارة المخازن</div>', unsafe_allow_html=True)
    warnings = InventoryManager.check_stock_levels()
    for w in warnings:
        st.warning(f"{w}: {warnings[w]}")
    for ing, data in st.session_state["inventory"].items():
        qty = data["quantity"]
        if role == "owner":
            new_qty = st.number_input(f"{ing} (طن)", value=float(qty), step=0.5, key=f"inv_{ing}")
            if new_qty != qty:
                st.session_state["inventory"][ing]["quantity"] = new_qty
                st.session_state["inventory"][ing]["last_updated"] = datetime.now().isoformat()
        else:
            st.write(f"{ing}: {qty:.2f} طن")

# ================== تبويب التسويق ==================
with tabs[3]:
    st.markdown('<div class="section-title">💰 نظام التسويق والفواتير</div>', unsafe_allow_html=True)
    client = st.text_input("اسم العميل:", "مزرعة الإنتاج")
    tons = st.number_input("الكمية (طن)", min_value=0.1, value=1.0, step=0.5)
    profit = st.number_input("هامش الربح للطن ($)", value=50.0)
    cost = st.session_state["computed_ton_cost"]
    selling = cost + profit
    total = selling * tons
    st.write(f"تكلفة الطن: ${cost:.2f}")
    st.write(f"سعر البيع: ${selling:.2f}")
    st.write(f"**الإجمالي: ${total:.2f}**")
    if role == "owner":
        if st.button("✅ تأكيد البيع وخصم المخزون", use_container_width=True):
            can_deduct = True
            for ing, pct in st.session_state["active_formula"].items():
                required = (pct/100) * tons
                if st.session_state["inventory"][ing]["quantity"] < required:
                    can_deduct = False
                    st.error(f"رصيد {ing} غير كافٍ")
            if can_deduct:
                for ing, pct in st.session_state["active_formula"].items():
                    st.session_state["inventory"][ing]["quantity"] -= (pct/100) * tons
                st.success("تم خصم المخزون وإتمام البيع")
                st.balloons()

# ================== تبويب الديباجة ==================
with tabs[4]:
    st.markdown('<div class="section-title">👑 مصمم ديباجات الطباعة</div>', unsafe_allow_html=True)
    brand = st.text_input("البراند التجاري:", "منصة تاور العلمية")
    st.markdown(f"""
    <div style='border:2px solid #1b5e20; padding:20px; border-radius:15px; text-align:center; background:white;'>
        <h2 style='color:#1b5e20;'>{brand}</h2>
        <h3 style='color:#c62828;'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>
        <p>علف مركز متوازن حسب معايير البروتين المهضوم (DP) ومعادل النشاء (SE)</p>
        <p>📅 تاريخ الإنتاج: {datetime.now().strftime('%Y-%m-%d')}</p>
        <p>🎯 {st.session_state['active_stage_title']} | DP: {st.session_state['active_cp_tag']:.1f}% | SE: {st.session_state['active_se_tag']:.1f}</p>
    </div>
    """, unsafe_allow_html=True)

# ================== تبويب التحليلات ==================
with tabs[5]:
    st.markdown('<div class="section-title">📈 التحليلات المتقدمة</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("عدد الخلطات", "1,247")
    col2.metric("متوسط التكلفة", "$285")
    col3.metric("نسبة التوفير", "18%")
    col4.metric("رضا العملاء", "96%")
    dates = pd.date_range(start='2024-01-01', periods=12, freq='ME')
    prices = [220,225,230,228,235,240,238,242,245,248,250,252]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines+markers', name='الذرة'))
    fig.update_layout(title="اتجاه أسعار الذرة", xaxis_title="التاريخ", yaxis_title="السعر ($/طن)")
    st.plotly_chart(fig)

# ================== تبويب إدارة الدجاج (للمالك فقط) ==================
if role == "owner":
    with tabs[6]:
        st.markdown('<div class="section-title">🐔 إدارة متكاملة لمزارع الدجاج اللاحم</div>', unsafe_allow_html=True)
        farm_ids = list(st.session_state["broiler_farms"].keys())
        farm_options = {fid: f"{st.session_state['broiler_farms'][fid]['info']['farm_name']} (مالك: {st.session_state['broiler_farms'][fid]['info']['owner_name']})" for fid in farm_ids}
        selected_farm = st.selectbox("اختر المزرعة:", list(farm_options.keys()), format_func=lambda x: farm_options[x])
        farm = st.session_state["broiler_farms"][selected_farm]
        with st.expander("✏️ تعديل معلومات المزرعة"):
            new_name = st.text_input("اسم المزرعة", farm["info"]["farm_name"])
            new_owner = st.text_input("اسم المالك", farm["info"]["owner_name"])
            new_phone = st.text_input("رقم الهاتف", farm["info"].get("phone",""))
            if st.button("حفظ المعلومات"):
                farm["info"]["farm_name"] = new_name
                farm["info"]["owner_name"] = new_owner
                farm["info"]["phone"] = new_phone
                save_broiler_farms(st.session_state["broiler_farms"])
                st.rerun()
        with st.form("daily_farm_form"):
            age = st.number_input("العمر (يوم)", 1, 70, 21)
            weight = st.number_input("متوسط الوزن (كجم)", 0.0, 5.0, 0.950, step=0.05)
            feed = st.number_input("إجمالي العلف المستهلك (كجم)", 0.0, 100000.0, 18500.0, step=500.0)
            dead = st.number_input("النافق الجديد اليوم", 0, 1000, 0)
            culled = st.number_input("المستبعدون الجدد", 0, 1000, 0)
            temp = st.number_input("درجة الحرارة (°C)", 10.0, 45.0, 26.0)
            hum = st.number_input("الرطوبة (%)", 20.0, 90.0, 60.0)
            notes = st.text_area("ملاحظات")
            if st.form_submit_button("💾 حفظ السجل اليومي"):
                prev = farm["daily_records"]
                total_dead = sum(r["new_dead"] for r in prev) + dead if prev else dead
                total_culled = sum(r["new_culled"] for r in prev) + culled if prev else culled
                init_birds = farm["info"]["initial_birds"]
                init_wt = farm["info"]["initial_weight_kg"]
                alive = init_birds - total_dead - total_culled
                gain_kg = alive * (weight - init_wt)
                fcr = BroilerFarmManager.calculate_fcr(feed, gain_kg)
                mort = BroilerFarmManager.calculate_mortality(total_dead, init_birds)
                liv = BroilerFarmManager.calculate_livability(init_birds, total_dead)
                adg = BroilerFarmManager.calculate_adg(weight*1000, init_wt*1000, age)
                epef = BroilerFarmManager.calculate_epef(liv, weight, age, fcr)
                std = BroilerFarmManager.get_standard_at_age(age)
                record = {
                    "date": datetime.now().strftime("%Y-%m-%d"), "age": age, "weight_kg": weight,
                    "feed_kg": feed, "new_dead": dead, "new_culled": culled, "temp_c": temp, "humidity": hum,
                    "notes": notes, "total_dead": total_dead, "total_culled": total_culled, "fcr": fcr,
                    "mortality_rate": mort, "livability": liv, "adg_g": adg, "epef": epef,
                    "std_weight": std["weight_kg"], "std_fcr": std["fcr"], "std_mortality": std["mortality_cum"],
                    "weight_diff": weight - std["weight_kg"], "fcr_diff": fcr - std["fcr"], "mortality_diff": mort - std["mortality_cum"]
                }
                farm["daily_records"].append(record)
                save_broiler_farms(st.session_state["broiler_farms"])
                st.success("تم حفظ السجل")
                st.rerun()
        if farm["daily_records"]:
            df = pd.DataFrame(farm["daily_records"])
            st.dataframe(df[["date","age","weight_kg","fcr","mortality_rate","epef"]], use_container_width=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["age"], y=df["weight_kg"], mode='lines+markers', name='فعلي'))
            ages_std = sorted(BroilerFarmManager.STANDARD_PERFORMANCE.keys())
            weights_std = [BroilerFarmManager.STANDARD_PERFORMANCE[a]["weight_kg"] for a in ages_std]
            fig.add_trace(go.Scatter(x=ages_std, y=weights_std, mode='lines', name='مستهدف'))
            st.plotly_chart(fig)
            last = df.iloc[-1]
            report = f"""🏷️ المزرعة: {farm['info']['farm_name']} (مالك: {farm['info']['owner_name']})
📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')}
🐔 العمر: {last['age']} يوم
⚖️ الوزن: {last['weight_kg']:.3f} كجم (المستهدف: {last['std_weight']:.3f})
🔄 FCR: {last['fcr']:.2f} (المستهدف: {last['std_fcr']:.2f})
💀 النفوق: {last['mortality_rate']:.2f}% (المستهدف: {last['std_mortality']:.1f}%)
🏆 EPEF: {last['epef']:.0f}
🌡️ الحرارة: {last['temp_c']}°C  💧 الرطوبة: {last['humidity']}%
📝 ملاحظات: {last['notes']}"""
            st.text_area("التقرير اليومي", report, height=250)
            if st.button("📲 إرسال التقرير عبر واتساب"):
                msg = urllib.parse.quote(report)
                st.link_button("اضغط للإرسال", f"https://wa.me/{farm['info']['phone'] if farm['info']['phone'] else WHATSAPP_NUMBER}?text={msg}")
        st.subheader("💊 السجل الصحي (الأدوية والتحصينات)")
        with st.form("health_form"):
            med = st.text_input("اسم الدواء/اللقاح")
            date = st.date_input("تاريخ الإعطاء", datetime.now())
            dose = st.text_input("الجرعة")
            next_due = st.date_input("التاريخ القادم", value=None)
            if st.form_submit_button("إضافة"):
                farm["health_log"].append({"med_name": med, "date": date.strftime("%Y-%m-%d"), "dose": dose, "next_due": next_due.strftime("%Y-%m-%d") if next_due else ""})
                save_broiler_farms(st.session_state["broiler_farms"])
                st.rerun()
        if farm["health_log"]:
            st.dataframe(pd.DataFrame(farm["health_log"]))
            today = datetime.now().date()
            for entry in farm["health_log"]:
                if entry.get("next_due"):
                    due = datetime.strptime(entry["next_due"], "%Y-%m-%d").date()
                    if due >= today:
                        days = (due - today).days
                        st.warning(f"{entry['med_name']} مستحق بعد {days} يوم")
                        reminder = f"تذكير: مزرعة {farm['info']['farm_name']} - يجب إعطاء {entry['med_name']} بتاريخ {entry['next_due']}"
                        st.link_button("🔔 تذكير واتساب", f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(reminder)}")
        if st.button("➕ حفظ الدورة الحالية في السجل"):
            st.session_state["broiler_cycles_history"].insert(0, {"info": farm["info"].copy(), "daily_records": farm["daily_records"].copy(), "health_log": farm["health_log"].copy(), "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            if len(st.session_state["broiler_cycles_history"]) > 10:
                st.session_state["broiler_cycles_history"] = st.session_state["broiler_cycles_history"][:10]
            st.success("تم الحفظ")
        if st.session_state["broiler_cycles_history"]:
            st.subheader("📜 التاريخ المحفوظ")
            hist_df = pd.DataFrame([{"التاريخ":c["saved_at"], "المزرعة":c["info"]["farm_name"], "المالك":c["info"]["owner_name"]} for c in st.session_state["broiler_cycles_history"]])
            st.dataframe(hist_df)
            sel_idx = st.selectbox("تحميل دورة سابقة", range(len(st.session_state["broiler_cycles_history"])), format_func=lambda i: st.session_state["broiler_cycles_history"][i]["info"]["farm_name"])
            if st.button("تحميل"):
                st.session_state["broiler_farms"][selected_farm] = st.session_state["broiler_cycles_history"][sel_idx]
                save_broiler_farms(st.session_state["broiler_farms"])
                st.rerun()

# ================== تبويب التعليقات ==================
if role in ["owner","specialist"]:
    comments_idx = 7 if role=="owner" else 6
    with tabs[comments_idx]:
        st.markdown("### 💬 تعليقات المختصين")
        st.text_area("التعليقات الحالية", value=st.session_state["shared_comments"], height=200, disabled=True)
        new_comm = st.text_input("✍️ أضف تعليقاً جديداً")
        if st.button("📌 نشر التعليق"):
            prefix = "• [توجيه الاختصاصي]" if role=="owner" else "• [ملاحظة مختص]"
            st.session_state["shared_comments"] += f"{prefix} ({datetime.now().strftime('%Y-%m-%d %H:%M')}): {new_comm}\n"
            st.rerun()

# ================== تبويب الدليل ==================
guide_idx = 8 if role=="owner" else (7 if role=="specialist" else 1)
with tabs[guide_idx]:
    st.markdown("### 📖 دليل المستخدم")
    st.markdown("""
    **منصة تاور العلمية** – نظام متكامل لإدارة وتطوير الثروة الحيوانية وتركيب الأعلاف.
    - **تركيب الأعلاف:** يعتمد على البروتين المهضوم (DP) ومعادل النشاء (SE) باستخدام الاستمثال الخطي.
    - **إدارة المزارع (للمالك):** تسجيل مزارع متعددة، إدخال بيانات يومية، حساب مؤشرات الأداء (FCR, EPEF, ADG)، مقارنة بالمعايير القياسية، سجل صحي للأدوية والتحصينات مع تنبيهات واتساب.
    - **بورصة الأسعار:** متابعة أسعار الماشية والمنتجات.
    - **المخازن:** إدارة الأرصدة والخصم التلقائي عند البيع.
    - **الديباجة والتحليلات:** تقارير PDF ورسوم بيانية تفاعلية.
    """)

# ================== أرشفة السورس كود للمالك ==================
if role == "owner":
    st.markdown("---")
    if st.button("📧 إرسال نسخة الكود إلى بريد المالك"):
        if send_code_to_mail(OWNER_EMAIL):
            st.success("تم إرسال الكود بنجاح")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown(f'<div class="mini-left-signature">👨‍🔬 الاختصاصي م. عبد القادر إسماعيل تاور © 2026 | منصة تاور العلمية</div>', unsafe_allow_html=True)
