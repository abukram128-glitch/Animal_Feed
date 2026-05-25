import streamlit as st
import numpy as np
import json
import os
import base64
import smtplib
import time
import urllib.parse  
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scipy.optimize import linprog

# استيراد مكتبات توليد الـ PDF المتقدمة ومعالجة اللغة العربية الصحيحة
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
import io

# ==========================================
# 1. إعدادات المنصة الرسمية والمظهر الفخم
# ==========================================
st.set_page_config(page_title="منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف", page_icon="🌾", layout="wide")

# الأكواد المعتمدة لنظام الصلاحيات الثلاثي
CODES_DB = {
    "202687": "owner",       # المالك تاور - صلاحية واسعة
    "2020": "specialist",    # المختص والزملاء 
    "2026": "breeder"        # المربي - الحدود العملية فقط
}

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

# 🔒 إعدادات خادم البريد الإلكتروني الحصرية للمالك 
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"       
SENDER_PASSWORD = "oynz rdli tsdy ekdq"     
OWNER_EMAIL = "abukram128@gmail.com"  
WHATSAPP_NUMBER = "+249123533489"     
GOOGLE_FORM_URL = "https://forms.google.com/YOUR_FORM_URL"  

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
    msg['Subject'] = "🌾 السورس كود الكامل والمطور - منصة تاور العلمية"
    
    body = "السلام عليكم م. عبد القادر،\n\nمرفق مع هذه الرسالة النسخة البرمجية الكاملة والمستقرة لمنصتكم الذكية (منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف) بعد تحديث الدليل والواجهات بالكامل.\n\nتحياتي الهندسية."
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        try:
            current_file = __file__
            with open(current_file, "r", encoding="utf-8") as f:
                code_content = f.read()
        except NameError:
            code_content = "# كود المنصة مأرشف داخلياً\n"
        
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

# دالة لتشكيل النصوص العربية وإصلاح اتجاهها للـ PDF
def fix_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

# دالة توليد تقارير PDF الفنية الاحترافية للمنظومة العلفية باسم المنصة الجديد
def generate_pdf_report(formula, target_cp, breed, cost, city, local_cost, local_sym):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    
    font_name = "Helvetica"
    if os.path.exists("Amiri-Regular.ttf"):
        try:
            pdfmetrics.registerFont(TTFont('Amiri', 'Amiri-Regular.ttf'))
            font_name = "Amiri"
        except Exception:
            pass
            
    p.setFont(font_name, 16)
    p.drawString(100, 800, fix_arabic_text("تقرير: منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف"))
    p.setFont(font_name, 12)
    p.drawString(100, 760, fix_arabic_text(f"المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور"))
    p.drawString(100, 740, fix_arabic_text(f"الموقع / السوق الجغرافي المستهدف: {city}"))
    p.drawString(100, 720, fix_arabic_text(f"الفصيل / السلالة الحيوانية: {breed}"))
    p.drawString(100, 700, fix_arabic_text(f"نسبة البروتين الخام المستهدفة (CP): {target_cp}%"))
    p.drawString(100, 680, fix_arabic_text(f"التكلفة المحسوبة للطن: ${cost:.2f} ({local_cost:,.2f} {local_sym})"))
    
    p.setFont(font_name, 14)
    p.drawString(100, 640, fix_arabic_text("المقادير الدقيقة المعتمدة لتركيب خلطة الطن الواحدة:"))
    p.setFont(font_name, 12)
    
    y_position = 610
    for k, v in formula.items():
        line_text = f"- {k}: {v:.2f}% -> ({v*10:.1f} كجم / طن)"
        p.drawString(100, y_position, fix_arabic_text(line_text))
        y_position -= 20
        if y_position < 50:
            p.showPage()
            y_position = 800
            
    p.setFont(font_name, 10)
    p.drawString(100, 50, fix_arabic_text("تم التوليد تلقائياً بواسطة منصة تاور العلمية © 2026 تحت إشراف م. عبد القادر إسماعيل تاور"))
    p.save()
    buffer.seek(0)
    return buffer.getvalue()

# --- تحسين الـ CSS لضمان التباين وقابلية القراءة الفخمة الحداثية ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Cairo', sans-serif;
        background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .stApp { background: transparent; }
    .main-box {
        background-color: rgba(255, 255, 255, 0.98);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18);
        margin-bottom: 50px;
    }
    h1, h2, h3, h4, h5, p, span, li { font-family: 'Cairo', sans-serif; }
    
    .formula-item {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 6px;
        font-weight: bold;
        color: #1b5e20 !important;
        border-right: 5px solid #2e7d32;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        text-align: right;
    }
    
    .section-title {
        color: #1b5e20;
        border-right: 6px solid #2e7d32;
        padding-right: 12px;
        text-align: right;
        font-size: 1.4rem;
        font-weight: bold;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    .sack-tag {
        border: 3px dashed #1b5e20;
        padding: 25px;
        border-radius: 12px;
        background-color: #f1f8e9;
        direction: rtl;
        text-align: right;
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
    }
    .animal-banner-img {
        width: 100%;
        max-height: 160px;
        object-fit: cover;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 2px solid #2e7d32;
    }
    .mini-left-signature {
        position: fixed;
        left: 15px;
        bottom: 15px;
        background-color: rgba(27, 94, 32, 0.95);
        color: white;
        padding: 6px 15px;
        font-size: 0.8rem;
        border-radius: 20px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
        z-index: 9999;
        direction: rtl;
    }
    .stock-critical { background-color: #ffebee; padding: 5px; border-radius: 4px; color: #c62828; font-weight: bold; }
    .stock-normal { background-color: #e8f5e9; padding: 5px; border-radius: 4px; color: #2e7d32; }
    .price-card {
        background: #f1f8e9;
        padding: 15px;
        border-radius: 8px;
        border-right: 5px solid #2e7d32;
        margin-bottom: 15px;
        direction: rtl;
        text-align: right;
    }
    .warning-card {
        background: #ffebee;
        padding: 12px;
        border-radius: 8px;
        border-right: 5px solid #c62828;
        margin-bottom: 10px;
        direction: rtl;
        text-align: right;
        color: #b71c1c;
    }
    
    /* تنسيقات الكتاب الكتيب الرقمي المطور */
    .manual-book {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.05);
        direction: rtl;
        text-align: right;
    }
    .book-chapter {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        color: #ffffff;
        padding: 10px 15px;
        border-radius: 6px;
        font-weight: bold;
        margin-top: 20px;
        font-size: 1.15rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .book-body {
        padding: 12px 20px;
        font-size: 1.05rem;
        line-height: 1.7;
        color: #2c3e50;
        border-left: 3px solid #3498db;
        margin-bottom: 15px;
        background-color: #f8f9fa;
        border-radius: 0 6px 6px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. بوابة الدخول وحماية النظام بالأكواد المحسنة
# ==========================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "login_welcome_shown" not in st.session_state: st.session_state["login_welcome_shown"] = False

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</p>", unsafe_allow_html=True)
    
    input_code = st.text_input("🔑 أدخل كود الدخول الخاص بك:", type="password")
    
    if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
        input_code_stripped = input_code.strip()
        if input_code_stripped in CODES_DB:
            st.session_state["approved"] = True
            st.session_state["user_role"] = CODES_DB[input_code_stripped]
            st.session_state["login_welcome_shown"] = False 
            st.rerun()
        else:
            st.error("❌ الكود الذي أدخلته غير صحيح! يرجى المحاولة مرة أخرى.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

if not st.session_state["login_welcome_shown"]:
    if st.session_state["user_role"] == "owner":
        st.toast("👋 مرحباً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور", icon="👑")
    elif st.session_state["user_role"] == "specialist":
        st.toast("🔬 أهلاً بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني.", icon="👨‍🔬")
    elif st.session_state["user_role"] == "breeder":
        st.toast("🚜 أهلاً وسهلاً بإخواننا المربين، شركاء النجاح.", icon="🌾")
    st.session_state["login_welcome_shown"] = True

# =====================================================================
# 3. المكتبة المحدثة والموسعة بالكامل لعام 2026 مع تدقيق نسب البروتين (CP)
# =====================================================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة الكبرى": {
        "ذرة صفراء": {"CP": 8.5}, "ذرة بيضاء": {"CP": 8.8}, "شعير مطحون": {"CP": 11.5}, 
        "سورجم (فتريتة)": {"CP": 10.0}, "قمح محلي مصنّع": {"CP": 12.0}, "جريش أرز رزاز": {"CP": 7.8},
        "دخن محلي غزير": {"CP": 11.0}, "شوفان علفي": {"CP": 11.0}
    },
    "🌱 الأكساب وأمبازات مصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0}, "كسب فول صويا 44%": {"CP": 44.0}, 
        "كسب فول صويا 48%": {"CP": 48.0}, "كسب عباد الشمس 36%": {"CP": 36.0}, 
        "كسب بذور القطن (مقشور)": {"CP": 41.0}, "كسب بذور الكتان": {"CP": 32.0}, 
        "كسب السمسم المحسن": {"CP": 42.0}, "كسب جلوتين الذرة 60%": {"CP": 60.0},
        "كسب نواة النخيل": {"CP": 16.0}
    },
    "🚜 المخلفات الزراعية والصناعية والمواد المالئة": {
        "نخالة قمح (ردة)": {"CP": 15.0}, "البرسيم الجاف (الدريس)": {"CP": 16.5}, 
        "مولاس قصب السكر": {"CP": 4.0}, "تبن قمح ناعم": {"CP": 3.2}, 
        "قشر فول سوداني مطحون": {"CP": 5.0}, "سرسة الأرز المطحونة": {"CP": 2.5},
        "بقايا تفل البنجر المجفف": {"CP": 8.0}, "مخلفات مصانع البسكويت": {"CP": 9.5},
        "سیلاج ذرة كامل متكامل": {"CP": 8.0}
    },
    "🧬 مصادر البروتين الحيواني والمركزات دقيقة الخلط": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0}, "مسحوق أسماك فاخر (72%)": {"CP": 72.0},
        "مسحوق اللحم والعظم": {"CP": 50.0}, "مركزات دواجن وسمان": {"CP": 40.0}, 
        "مركزات خيول ومجترات": {"CP": 36.0}
    },
    "🧪 الأحماض الأمينية البلورية النقية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0}, "ميثيونين نقي (DL-Methionine)": {"CP": 58.0}, 
        "ثريونين نقي (L-Threonine)": {"CP": 72.0}, "تريبتوفان نقي (L-Tryptophan)": {"CP": 85.0},
        "فالين نقي (L-Valine)": {"CP": 90.0}
    },
    "🔬 الإنزيمات والبريمكسات والإضافات التخصصية": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0}, "بريمكس بياض وبشاير": {"CP": 0.0},
        "بريمكس أبقار حلابة ومجترات": {"CP": 0.0}, "بريمكس خيول وفروسية": {"CP": 0.0},
        "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0}, 
        "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0}, 
        "كبريتات الحديدوز (معادل الجوسيبول)": {"CP": 0.0},
        "مستخلص الخمائر والجدر الخلوية (MOS)": {"CP": 12.0}
    },
    "🪨 الأملاح والمعادن ومنظمات الهضم": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0}, "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0}, 
        "ملح الطعام": {"CP": 0.0}, "مضاد سموم فطرية": {"CP": 0.0}, 
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0}, "أكسيد المغنيسيوم العلفي": {"CP": 0.0},
        "يوريا علفية محصنة (المجترات فقط)": {"CP": 287.0}
    }
}

if "inventory" not in st.session_state:
    st.session_state["inventory"] = {}
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        for ing in items:
            st.session_state["inventory"][ing] = 25.0

if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين / محسن ($)": 1350.0, "أبقار كنانة وبطانة محلية ($)": 900.0,
        "ضأن وستيرلنغ / محلي ($)": 180.0, "ماعز نوبي وصحراوي ($)": 130.0,
        "خيول عربية أصيلة وهجين ($)": 4500.0, "كتكوت لاحم عمر يوم ($)": 0.65, "دجاج بياض عمر البشاير ($)": 5.50
    }

if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري صافي ($)": 7.50, "كيلو لحم ضأن طازج ($)": 9.00, "كيلو لحم دجاج لاحم صافي ($)": 3.80,
        "طبق بيض مائدة 30 بيضة ($)": 4.20, "رطل / لتر حليب خام ($)": 0.90, "كيلو جبن أبيض محلي ($)": 5.00,
        "كيلو جبن جاف / شيدر ($)": 8.50
    }

if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = (
        "• [توجيه الاختصاصي م. عبد القادر إسماعيل تاور]: يرجى من جميع الزملاء إضافة تعليقاتهم هنا لتبادل الخبرات التركيبية.\n"
        "• [ملاحظة مختص]: تم مراجعة جودة كسب زهرة الشمس المتاح حالياً بالأسواق ونوصي بضبط ألياف الخيل بناءً عليه.\n"
    )

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"}, "LIBYA": {"rate": 4.80, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"}, "باقي دول العالم / البورصة المفتوحة": {"rate": 1.0, "sym": "USD"}
}

def get_adjusted_market_data(country, state_or_region, city):
    feed_prices = {}
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing in cat:
            feed_prices[ing] = 230.0
    
    feed_prices.update({
        "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0, "سورجم (فتريتة)": 195.0, "قمح محلي مصنّع": 240.0,
        "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا 44%": 440.0, "كسب فول صويا 48%": 480.0, "كسب عباد الشمس 36%": 310.0, "كسب بذور القطن (مقشور)": 290.0,
        "نخالة قمح (ردة)": 150.0, "البرسيم الجاف (الدريس)": 170.0, "مولاس قصب السكر": 120.0,
        "مسحوق أسماك (Fishmeal 60%)": 850.0, "مركزات دواجن وسمان": 650.0, "مركزات خيول ومجترات": 600.0,
        "الحجر الجيري (بودرة بلاط)": 40.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0, "ملح الطعام": 30.0, "مضاد سموم فطرية": 950.0,
        "بيكربونات الصوديوم (الصودا)": 340.0
    })
    
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
        if city == "طبرق": multiplier = 1.06
    elif country == "مصر": multiplier = 1.04

    for k in feed_prices: feed_prices[k] *= multiplier
    return feed_prices

ANIMAL_IMAGES_RESOURCES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600",
    "سمان": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600"
}

if "active_formula" not in st.session_state: st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 16.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_animal_img" not in st.session_state: st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES["عام"]
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0

# ==========================================
# 4. بناء الواجهة الرئيسية للمنصة
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logout_space, col_user_status = st.columns([0.7, 0.3])
with col_user_status:
    role_arabic = {"owner": "الاختصاصي م. عبد القادر إسماعيل تاور 👑", "specialist": "المختص والزملاء 👨‍🔬", "breeder": "المربي 🌾"}[st.session_state["user_role"]]
    st.markdown(f"<div style='text-align: left; font-size:0.9rem; color:#555;'>الحساب: <b>{role_arabic}</b></div>", unsafe_allow_html=True)
    if st.button("تسجيل الخروج 🚪", use_container_width=True):
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    if img_base64: st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else: st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.2rem; margin-top:5px; margin-bottom:0;'>محرك الإنزيمات التلقائي والإلزامي المتكامل وتعديل المحتوى الأيوني والبيكربونات</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

# --- زر المشاركة والدعاية والتسويق الاحترافي ---
st.markdown("### 📢 المشاركة التسويقية والدعوة العلمية")
share_text_payload = """📢 دعوة علمية وتسويقية من منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف

إلى كل مهتم بتطوير الثروة الحيوانية؛ من أطباء بيطريين، اختصاصيي إنتاج حيواني، ومربين طموحين:
يسعدنا دعوتكم لاستخدام وتجربة المنصة المتقدمة لتركيب وتطوير الأعلاف، بإشراف وتصميم:
[ الاختصاصي م. عبد القادر إسماعيل تاور ]

🎯 ما تقدمه المنصة:
• حلول برمجية ذكية لتركيب أعلاف اقتصادية وعالية القيمة الغذائية (Least-Cost Formulation).
• أدوات دقيقة لحساب الاحتياجات الغذائية بما يضمن أعلى معدلات نمو وإنتاجية.
• دعم كامل للعمل الميداني والبحث العلمي والخصم التلقائي للمستودعات في مكان واحد.

🔗 رابط المنصة: [ضع رابط موقعك هنا]"""

st.text_area("النص الدعائي والإعلامي الجاهز للنشر:", value=share_text_payload, height=140, key="top_share_box")
if st.button("📋 نسخ الرابط والنص للدعاية والتسويق", type="secondary"):
    st.success("تم التجهيز بنجاح! يمكنك الآن نسخ النص ومشاركته عبر المجموعات والمنصات.")
st.markdown("---")

# نظام الترحيب الديناميكي المحدث
if st.session_state["user_role"] == "owner":
    st.markdown("<div style='background-color: #eff6ff; padding: 15px; border-radius: 8px; border-right: 5px solid #1d4ed8; text-align: right; direction: rtl; margin-bottom: 20px;'>"
                "<b>👑 أهلاً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور. الواجهات والتحكم الكامل في الخصم والأرصدة متاح بين يديك الآن بالكامل.</b>"
                "</div>", unsafe_allow_html=True)
elif st.session_state["user_role"] == "specialist":
    st.markdown("<div style='background-color: #f0fdf4; padding: 15px; border-radius: 8px; border-right: 5px solid #16a34a; text-align: right; direction: rtl; margin-bottom: 20px;'>"
                "<b>🔬 مرحباً بكم في منصة تركيب وتحليل الأعلاف الذكية. يسعد الاختصاصي م. عبد القادر إسماعيل تاور بالترحيب بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني. معاً نلتقي بالبحث العلمي والتطبيق العقلي لنقود صناعة الأعلاف نحو كفاءة وإنتاجية أعلى.</b>"
                "</div>", unsafe_allow_html=True)
elif st.session_state["user_role"] == "breeder":
    st.markdown("<div style='background-color: #fffbeb; padding: 15px; border-radius: 8px; border-right: 5px solid #d97706; text-align: right; direction: rtl; margin-bottom: 20px;'>"
                "<b>🚜 أهلاً وسهلاً بكم في منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف. نرحب بإخواننا المربين، شركاء النجاح وأعمدة الإنتاج الحقيقيين. نحن هنا لنقدم لكم أفضل الحلول والخلطات العلفية التي تضمن أعلى معدلات التحويل وأفضل العوائد لمشاريعكم.</b>"
                "</div>", unsafe_allow_html=True)

# تفعيل نظام التبويبات بناءً على مستوى الصلاحيات المدخلة
if st.session_state["user_role"] in ["owner", "specialist"]:
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية الكبرى", 
        "📊 بورصة الأسعار المركزية للماشية", 
        "🏭 إدارة المستودعات والخصم التلقائي", 
        "🧾 التسويق وفواتير حركة البيع", 
        "🖨️ مصمم بطاقات الديباجة والدعاية", 
        "💬 خانة تعليقات المختصين والزملاء",
        "📖 دليل المستخدم (الكتيب الرقمي)"
    ]
else: 
    tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى", "📖 دليل المستخدم (الكتيب الرقمي)"]

tabs = st.tabs(tabs_titles)

# -------------------------------------------------------------------------
# التبويب الأول: الحسابات والتركيبات (متاح للجميع) - تم تفرعته إلى نافذتين
# -------------------------------------------------------------------------
with tabs[0]:
    # إنشاء تبويب داخلي للفصل بين "التركيب التلقائي للطن" وبين "مختبر الفحص الحر"
    sub_tab_formulator, sub_tab_analyzer = st.tabs(["🎯 تركيب علفة نموذجية (أقل تكلفة)", "🔬 مختبر تحليل وفحص الأعلاف الجاهزة"])
    
    # --- النافذة الأولى: تركيب العلفة النموذجية (الكود الأساسي الأصلي دون أي تعديل) ---
    with sub_tab_formulator:
        st.markdown('<div class="section-title">🌍 أولاً: تحديد الموقع الجغرافي وبورصة الأسعار بالعملتين المحلية والأجنبية</div>', unsafe_allow_html=True)
        col_country, col_state, col_city = st.columns(3)
        with col_country: user_country = st.selectbox("اختر دولة المربي:", ["السودان", "LIBYA", "مصر", "باقي دول العالم / البورصة المفتوحة"])
            
        c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
        local_rate = c_info["rate"]; local_sym = c_info["sym"]

        chosen_state = "عام"
        with col_state:
            if user_country == "السودان":
                chosen_state = st.selectbox("اختر الولاية السودانية المحدثة:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال كردفان", "ولاية جنوب كردفان", "ولاية غرب كردفان", "إقليم النيل الأزرق", "ولاية البحر الأحمر", "ولاية نهر النيل"])
            elif user_country == "LIBYA": chosen_state = st.selectbox("اختر الإقليم الجغرافي:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
            else: chosen_state = st.selectbox("الإقليم الإداري:", ["المركز الرئيسي العالمي", "الأسواق المفتوحة"])

        with col_city:
            if user_country == "السودان":
                if chosen_state == "ولاية الخرطوم": user_city = st.selectbox("اختر المدينة:", ["الخرطوم", "أم درمان", "بحري"])
                elif chosen_state == "ولاية الجزيرة": user_city = st.selectbox("اختر المدينة:", ["ود مدني", "الحصاحيصا", "المناقل"])
                elif chosen_state == "ولاية القضارف": user_city = st.selectbox("اختر المدينة:", ["القضارف المدينة", "الفاو"])
                elif chosen_state == "ولاية شمال كردفان": user_city = st.selectbox("اختر المدينة:", ["الأبيض", "بارا", "أم روابة"])
                elif chosen_state == "ولاية جنوب كردفان": user_city = st.selectbox("اختر المدينة:", ["كادوقلي", "الدلنج"])
                elif chosen_state == "ولاية غرب كردفان": user_city = st.selectbox("اختر المدينة:", ["الفوله", "النهود", "بابنوسة"])
                elif chosen_state == "إقليم النيل الأزرق": user_city = st.selectbox("اختر المدينة:", ["الدمازين", "الروصيرص"])
                elif chosen_state == "ولاية البحر الأحمر": user_city = st.selectbox("اختر المدينة:", ["بورتسودان", "سواكن"])
                else: user_city = st.selectbox("اختر المدينة:", ["شندي", "عطبرة"])
            elif user_country == "LIBYA":
                if chosen_state == "المنطقة الشرقية": user_city = st.selectbox("اختر المدينة الليبية:", ["طبرق", "بنغازي", "البيضاء", "درنة"])
                elif chosen_state == "المنطقة الغربية": user_city = st.selectbox("اختر المدينة الليبية:", ["طرابلس", "مصراتة", "الزاوية"])
                else: user_city = st.selectbox("اختر المدينة الليبية:", ["سبها", "مرزق", "غات"])
            else: user_city = st.text_input("اكتب اسم المدينة العالمية يدوياً:", "طبرق")

        live_prices = get_adjusted_market_data(user_country, chosen_state, user_city)
        
        col_view1, col_view2 = st.columns(2)
        with col_view1:
            st.markdown(f'<div class="price-card"><b>📈 بورصة الماشية والداجن الحية في ({user_city}) المزدوجة:</b><br>' + 
                        "<br>".join([f"▪️ {k}: <b>${v:.2f}</b> (يعادل: <span style='color:#e65100; font-weight:bold;'>{v*local_rate:,.2f} {local_sym}</span>)" for k, v in st.session_state["global_livestock_prices"].items()]) + "</div>", unsafe_allow_html=True)
        with col_view2:
            st.markdown(f'<div class="price-card"><b>🥩 بورصة المنتجات الحيوانية والألبان والبيض في ({user_city}):</b><br>' + 
                        "<br>".join([f"▪️ {k}: <b>${v:.2f}</b> (يعادل: <span style='color:#1b5e20; font-weight:bold;'>{v*local_rate:,.2f} {local_sym}</span>)" for k, v in st.session_state["global_products_prices"].items()]) + "</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">⚖️ ثانياً: اختيار القطاع والنوع والإنتاجية المستهدفة</div>', unsafe_allow_html=True)
        col_sec, col_sub, col_prod = st.columns(3)
        with col_sec: main_sector = st.selectbox("اختر القطاع الإنتاجي الرئيسي:", ["الخيول والفروسية", "الماعز وسلالاته", "الأبقار وسلالاتها", "الطيور والسمان", "الأسماك والأحياء المائية"])
        
        show_measurements = False; weight_factor = 10000; feed_factor = 0.02; default_cp = 14.0; dynamic_img_key = "عام"; chosen_concentrate = None
        
        with col_sub:
            if main_sector == "الخيول والفروسية": 
                sub_type = st.selectbox("السلالة المستهدفة:", ["خيل عربي أصيل", "ثوروبريد", "خيول محلية هجين"])
                dynamic_img_key = "خيول"; show_measurements = True; weight_factor = 11877; feed_factor = 0.022; chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الماعز وسلالاته": 
                sub_type = st.selectbox("السلالة المستهدفة:", ["الماعز النوبي السوداني", "الماعز الصحراوي", "بور / محسن"])
                dynamic_img_key = "ماعز"; show_measurements = True; weight_factor = 15000; feed_factor = 0.032; chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الأبقار وسلالاتها": 
                sub_type = st.selectbox("السلالة المستهدفة:", ["كنانة (سوداني)", "بطانة (مدر)", "هولشتاين / محسن"])
                dynamic_img_key = "أبقار"; show_measurements = True; weight_factor = 10838; feed_factor = 0.025; chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الطيور والسمان": 
                sub_type = st.selectbox("نوع الطيور:", ["طائر السمان (Quail)", "دواجن لاحم (Broiler)", "دواجن بياض (Layer)"])
                dynamic_img_key = "سمان" if "السمان" in sub_type else "دواجن"; chosen_concentrate = "مركزات دواجن وسمان"
            else: 
                sub_type = st.selectbox("نوع الأسماك:", ["البلطي النيلي (Tilapia)", "القرموط"])
                dynamic_img_key = "أسماك"; chosen_concentrate = "مسحوق أسماك (Fishmeal 60%)"

        with col_prod:
            if main_sector == "الخيول والفروسية": 
                prod_stage = st.selectbox("نوع الإنتاج:", ["خيول رياضة ونشاط مكثف", "أمهار نامية صغيرة", "فرسات مرضعات"])
                default_cp = 16.0 if "أمهار" in prod_stage or "مرضعات" in prod_stage else 12.0
            elif main_sector == "الماعز وسلالاته": 
                prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج اللحوم وتسمين", "إنتاج ألبان وحليب"])
                default_cp = 15.5 if "ألبان" in prod_stage else 13.5
            elif main_sector == "الأبقار وسلالاتها": 
                prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج حليب وغزارة إدرار", "تسمين عجول مكثف"])
                default_cp = 16.0 if "حليب" in prod_stage else 13.0
            elif main_sector == "الطيور والسمان":
                if "السمان" in sub_type: 
                    prod_stage = st.selectbox("نوع الإنتاج:", ["سمان بادي / نامي", "سمان بياض إنتاجي"])
                    default_cp = 24.0 if "بادي" in prod_stage else 20.0
                else: 
                    prod_stage = st.selectbox("نوع الإنتاج:", ["بادي دواجن 23%", "نامي دواجن 21%", "ناهي دواجن 19%", "بياض إنتاجي"])
                    default_cp = 23.0 if "بادي" in prod_stage else (21.0 if "نامي" in prod_stage else (19.0 if "ناهي" in prod_stage else 17.5))
            else: 
                prod_stage = st.selectbox("نوع الإنتاج:", ["بادئ زريعة أسماك عالي", "نمو وتسمين أسماك نيلية"])
                default_cp = 35.0 if "زريعة" in prod_stage else 30

        if show_measurements:
            st.markdown('<div class="section-title">📐 ثالثاً: شريط القياس الجسدي وتقدير الأوزان والاحتياجات حَقلياً</div>', unsafe_allow_html=True)
            col_h, col_l, col_ag = st.columns(3)
            with col_h: h_girth = st.number_input("📏 محيط الصدر خلف الكوع مباشرة (سم):", value=150.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 70.0)
            with col_l: b_length = st.number_input("📏 طول الجسم الجسدي (سم):", value=130.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 60.0)
            with col_ag: a_months = st.number_input("⏳ عمر الحيوان التقديري (أشهر):", value=12)
            calc_weight = (h_girth ** 2 * b_length) / weight_factor; req_feed_kg = calc_weight * feed_factor
            st.success(f"📊 الوزن الحيوي المتوقع للحيوان: **{calc_weight:.1f} كجم** | الاحتياج اليومي المقدر للمادة الجافة: **{req_feed_kg:.2f} كجم**")
        else:
            st.markdown('<div class="section-title">✨ ثالثاً: قطاع الطيور والأسماك</div>', unsafe_allow_html=True)
            st.info(f"💡 نظام المعالجة التلقائي: تم تحييد شريط القياس الجسدي لعدم ملاءمته حَقلياً للطيور والأسماك.")

        st.markdown('<div class="section-title">📋 رابعاً: حد البروتين الصارم للموازنة والخامات المتاحة</div>', unsafe_allow_html=True)
        col_p1, col_p2 = st.columns(2)
        with col_p1: st.metric("🧬 بروتين العليقة المقترح من المنصة:", f"{default_cp} %")
        with col_p2:
            override_cp = st.checkbox("⚙️ تفعيل التعديل الفني الاختياري للبروتين")
            final_target_cp = st.slider("حدّد نسبة البروتين المستهدفة فنيّاً:", 10.0, max_value=45.0, value=default_cp) if override_cp else default_cp

        selected_ingredients = []; ingredient_prices = {}
        
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            with st.expander(f"📁 {cat_name}", expanded=True if "الحبوب" in cat_name or "الأكساب" in cat_name else False):
                sub_cols = st.columns(3)
                for idx, (ing_name, _) in enumerate(items.items()):
                    with sub_cols[idx % 3]:
                        is_def = True if ing_name == chosen_concentrate or ing_name in ["ذرة صفراء", "سورجم (فتريتة)", "أمباز الفول السوداني (كسب)", "كسب فول صويا 44%", "نخالة قمح (ردة)", "ملح الطعام", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)", "بيكربونات الصوديوم (الصودا)", "مضاد سموم فطرية"] else False
                        checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                        current_live_price = live_prices.get(ing_name, 350.0)
                        
                        if st.session_state["user_role"] == "owner": 
                            price_input = st.number_input(f"السعر للطن ({ing_name}) $:", min_value=5.0, value=float(current_live_price), key=f"price_{ing_name}")
                        else:
                            st.markdown(f"💰 السعر الحالي بموقعك: **`${current_live_price:.2f}`** / طن")
                            price_input = current_live_price
                        
                        if checked:
                            selected_ingredients.append(ing_name)
                            ingredient_prices[ing_name] = price_input

        fixed_additives = {"ملح الطعام": 0.5, "مضاد سموم فطرية": 0.2, "الحجر الجيري (بودرة بلاط)": 2.5 if "بياض" in prod_stage else 1.5, "فوسفات ثنائي الكالسيوم (DCP)": 1.0}
        
        auto_added_enzymes = {}
        mandatory_warnings = []
        
        if main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاته"]:
            auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.75
            mandatory_warnings.append("🚨 <b>إضافة إلزامية - بيكربونات الصوديوم:</b> تم فرض بيكربونات الصوديوم أوتوماتيكياً بنسبة 0.75% كمنظم حموضة (Buffer) لحماية الكرش من <b>التحمض Ruminal Acidosis</b>.")
        elif main_sector == "الطيور والسمان":
            auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.20

        if main_sector in ["الطيور والسمان", "الأسماك والأحياء المائية"]:
            auto_added_enzymes["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05
            mandatory_warnings.append("🚨 <b>إضافة إلزامية - إنزيم الفايتيز (Phytase):</b> مضاف تلقائياً بنسبة 0.05% لتحرير <b>الفسفور النباتي المرتبط</b> وتحسين الهضم.")

        if "كسب بذور القطن (مقشور)" in selected_ingredients and main_sector == "الطيور والسمان":
            auto_added_enzymes["كبريتات الحديدوز (معادل الجوسيبول)"] = 0.15
            mandatory_warnings.append("⚠️ <b>معالجة الجوسيبول:</b> تم دمج كبريتات الحديدوز بنسبة 0.15% فورياً لربط <b>الجوسيبول الحر السام Toxic Gossypol</b> وإبطال مفعوله.")

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
        
        if st.button("🚀 تشغيل محرك الاستمثال الخطي للأعلاف (Scipy Optimized)", type="primary", use_container_width=True):
            
            with nz_placeholder.container():
                st.warning(
                    "⚠️ **إشعار هام بشأن الإنزيمات ومضافات الأعلاف:** يرجى التأكد التام والحرص الشديد على موازنة درجات حرارة كبس العلف أثناء التصنيع لضمان عدم تثبيط الإنزيمات والفيتامينات الدقيقة المضافة حيوياً. (سيختفي هذا الإشعار تلقائياً بعد 40 ثانية)"
                )
                
            c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
            bounds = []
            for ing in selected_ingredients:
                if ing in all_fixed_additives:
                    val = all_fixed_additives[ing]
                    bounds.append((val, val))
                else:
                    bounds.append((0.0, 100.0))

            A_eq = [[1.0 for _ in selected_ingredients]]
            b_eq = [100.0]
            
            cp_row = []
            for ing in selected_ingredients:
                cp_val = 0.0
                for cat in BIG_FEEDS_LIBRARY.values():
                    if ing in cat: 
                        cp_val = cat[ing].get("CP", 0.0)
                cp_row.append(cp_val)
            A_eq.append(cp_row)
            b_eq.append(final_target_cp * 100.0)

            A_ub = []
            b_ub = []
            
            grain_indicators = [1.0 if ing in BIG_FEEDS_LIBRARY["🌾 الحبوب ومصادر الطاقة الكبرى"] else 0.0 for ing in selected_ingredients]
            if sum(grain_indicators) > 0:
                A_ub.append([-1.0 * x for x in grain_indicators])
                b_ub.append(-50.0)
                
            if "نخالة قمح (ردة)" in selected_ingredients:
                fiber_indicators = [1.0 if ing == "نخالة قمح (ردة)" else 0.0 for ing in selected_ingredients]
                A_ub.append(fiber_indicators)
                b_ub.append(18.0)

            res = linprog(c_vector, A_ub=A_ub if A_ub else None, b_ub=b_ub if b_ub else None, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

            if not res.success:
                A_ub_flex = []
                b_ub_flex = []
                if sum(grain_indicators) > 0:
                    A_ub_flex.append([-1.0 * x for x in grain_indicators])
                    b_ub_flex.append(-40.0)
                if "نخالة قمح (ردة)" in selected_ingredients:
                    fiber_indicators = [1.0 if ing == "نخالة قمح (ردة)" else 0.0 for ing in selected_ingredients]
                    A_ub_flex.append(fiber_indicators)
                    b_ub_flex.append(25.0)
                    
                res = linprog(c_vector, A_ub=A_ub_flex if A_ub_flex else None, b_ub=b_ub_flex if b_ub_flex else None, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

            if res.success:
                formula_results = {}
                for idx, ing in enumerate(selected_ingredients):
                    if res.x[idx] > 0.0001: 
                        formula_results[ing] = res.x[idx]

                st.session_state["active_formula"] = formula_results
                st.session_state["active_cp_tag"] = final_target_cp
                st.session_state["active_breed_tag"] = sub_type
                st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES.get(dynamic_img_key, ANIMAL_IMAGES_RESOURCES["عام"])
                st.session_state["active_stage_title"] = f"{main_sector} - {prod_stage}"
                
                st.success(f"🎯 تم تشغيل محرك التركيب واستقرار الاستمثال الخطي بنجاح في سوق: {user_city}")
                
                if mandatory_warnings:
                    st.markdown("### 🔬 تقرير فحص العلل والتدخل البرمجي بالإنزيمات والمنظمات الأيونية:")
                    for warn in mandatory_warnings: 
                        st.markdown(f'<div class="warning-card">{warn}</div>', unsafe_allow_html=True)

                res_col1, res_col2 = st.columns([0.6, 0.4])
                with res_col1:
                    st.write("#### 📝 المقادير الدقيقة المعتمدة لتركيب طن واحد (كجم):")
                    for k, v in formula_results.items(): 
                        st.markdown(f'<div class="formula-item">▪️ <b>{k}:</b> {v:.2f} % ➡️ ({v*10:.1f} كجم / طن)</div>', unsafe_allow_html=True)
                    
                    ton_cost = res.fun / 100.0 if hasattr(res, 'fun') else 280.0
                    st.session_state["computed_ton_cost"] = ton_cost
                    st.metric(f"💰 التكلفة الفعلية لإنتاج الطن في {user_city}: ", f"${ton_cost:.2f} (أو {ton_cost*local_rate:,.1f} {local_sym})")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    col_share, col_pdf = st.columns(2)
                    with col_share:
                        share_message = f"منصة تاور العلمية - الخلطة المعتمدة: {sub_type}، بتكلفة إنتاج {ton_cost:.2f}$ للطن. المشرف: الاختصاصي م. عبد القادر إسماعيل تاور."
                        encoded_share_msg = urllib.parse.quote(share_message)
                        st.link_button("📲 مشاركة الفاتورة عبر واتساب", f"https://wa.me/?text={encoded_share_msg}")
                    with col_pdf:
                        try:
                            pdf_data = generate_pdf_report(formula_results, final_target_cp, sub_type, ton_cost, user_city, ton_cost*local_rate, local_sym)
                            st.download_button("📥 تحميل التقرير الفني PDF", pdf_data, file_name=f"Tower_Scientific_Platform_{user_city}.pdf", mime="application/pdf", use_container_width=True)
                        except Exception as pdf_err:
                            st.error(f"⚠️ لم يتم بناء ملف الـ PDF: {pdf_err}")
                    
                with res_col2: 
                    st.bar_chart(formula_results)
            else:
                st.error("❌ تعذر إيجاد حل رياضي متزن تماماً ضمن المحددات الحالية للمركبات الضيقة. يرجى إتاحة وتفعيل خامات إضافية ككسب فول صويا أو أمباز الفول لتوسيع مساحة الحل للمعالج الخطي.")
                
            time.sleep(40)
            nz_placeholder.empty()

    # --- النافذة الثانية: مختبر تحليل وفحص الأعلاف الجاهزة (الإضافة البرمجية المطلوبة) ---
    with sub_tab_analyzer:
        st.markdown('<div class="section-title">🔬 مختبر فحص وتحليل الخلطات الجاهزة يدوياً</div>', unsafe_allow_html=True)
        st.write("اكتب مقادير خلطتك الحالية بالكيلوجرام، وسيقوم المختبر بتحليلها برمجياً لتقدير نسبة البروتين الكلية مقارنة بنوع الإنتاج المستهدف.")
        
        # 1. تحديد فئة المقارنة بناءً على المكتبة الأصلية المتاحة لديك
        st.subheader("🎯 حدد الحيوان والغرض المستهدف لمقارنة النتيجة:")
        col_lab_sec, col_lab_cp = st.columns(2)
        with col_lab_sec:
            target_animal = st.selectbox("اختر فئة الحيوان المستهدف بالفحص:", ["الطيور والسمان", "الأبقار وسلالاتها", "الماعز وسلالاته", "الخيول والفروسية", "الأسماك والأحياء المائية"], key="lab_target_animal")
        with col_lab_cp:
            # استنباط حد البروتين الاسترشادي تلقائياً بناءً على معاييرك الأصلية بالكود
            suggested_cp_target = 14.0
            if target_animal == "الطيور والسمان": suggested_cp_target = 21.0
            elif target_animal == "الأسماك والأحياء المائية": suggested_cp_target = 30.0
            elif target_animal == "الأبقار وسلالاتها": suggested_cp_target = 15.0
            st.markdown(f"🧬 البروتين القياسي المطلوب لهذه الفئة: **{suggested_cp_target}%**")

        st.markdown("---")
        st.subheader("📥 أدخل أوزان المكونات بالكيلوجرام (حرية الإدخال بالكامل):")
        
        # تجميع الخامات المتاحة من مكتبتك الأصلية لتسهيل الإدخال الفردي
        lab_user_inputs = {}
        all_library_ingredients = []
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            for ing_name in items.keys():
                all_library_ingredients.append(ing_name)
        
        # تقسيم واجهة الإدخال على ثلاثة أعمدة منظمة لتفادي طول الصفحة وضمان سهولة القراءة
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
        
        if st.button("🧪 تشغيل التحليل المخبري للخلطة يدوياً", type="primary", use_container_width=True):
            lab_total_weight = sum(lab_user_inputs.values())
            
            if lab_total_weight <= 0:
                st.warning("⚠️ الرجاء إدخال أوزان أكبر من الصفر للمواد لتتمكن المنظومة من تحليلها.")
            else:
                calculated_total_cp = 0.0
                entered_components_summary = []
                
                # حساب المساهمة الحجمية والغذائية بناء على قاعدة بروتين الخامات الأصلية
                for ing_name, weight in lab_user_inputs.items():
                    if weight > 0:
                        pct = weight / lab_total_weight
                        # جلب نسبة بروتين الخامة من مكتبتك الكبرى
                        ing_cp = 0.0
                        for cat, items in BIG_FEEDS_LIBRARY.items():
                            if ing_name in items:
                                ing_cp = items[ing_name].get("CP", 0.0)
                        
                        calculated_total_cp += pct * ing_cp
                        entered_components_summary.append({
                            "المادة العلفية": ing_name,
                            "الوزن المدخل": f"{weight:.1f} كجم",
                            "النسبة المئوية من الإجمالي": f"{pct * 100:.2f}%"
                        })
                
                # عرض تقرير التحليل النهائي
                st.success("🔬 تم فحص عينة العلف وتحليل المحتوى النيتروجيني بنجاح!")
                
                st.markdown(f"### ⚖️ إجمالي وزن الخلطة الجاهزة المختبرة: **{lab_total_weight:.1f} كجم**")
                st.write("#### 📊 نسب توزيع المكونات في العينة المدخلة:")
                st.table(pd.DataFrame(entered_components_summary))
                
                st.markdown("---")
                st.write("#### 🔬 تقرير الفحص المخبري النهائي ومقارنة الجودة:")
                
                status_label = "✅ مطابق وممتاز" if calculated_total_cp >= suggested_cp_target else "⚠️ ناقص البروتين"
                
                lab_report_data = [
                    {
                        "العنصر الغذائي الفني": "البروتين الخام الكلي (Crude Protein CP)",
                        "النسبة المحسوبة برمجياً": f"{calculated_total_cp:.2f}%",
                        "الاحتياج الاسترشادي القياسي": f"{suggested_cp_target:.1f}%",
                        "التقييم المخبري": status_label
                    }
                ]
                st.table(pd.DataFrame(lab_report_data))
                
                # رسم بياني توضيحي للمستخدم لمعاينة توزيع الأوزان
                st.write("📊 التمثيل البياني لتوزيع أوزان المواد المدخلة:")
                graph_data = {k: v for k, v in lab_user_inputs.items() if v > 0}
                st.bar_chart(graph_data)

# ====================================================================
# التبويبات الإدارية المتقدمة (تظهر للمالك والمسؤول والمختص)
# ====================================================================
if st.session_state["user_role"] in ["owner", "specialist"]:
    
    # تبويب البورصة المركزية
    with tabs[1]:
        st.markdown('<div class="section-title">📊 لوحة تحكم بورصة تاور المركزية الشاملة (تحديث الأسعار المباشرة)</div>', unsafe_allow_html=True)
        if st.session_state["user_role"] == "specialist":
            st.warning("⚠️ حساب زميل/مختص: متاح لك استعراض أسعار البورصة فقط، تعديل وحفظ السجلات الأساسية محجوز لإدارة المنصة.")
            
        col_edit1, col_edit2 = st.columns(2)
        with col_edit1:
            st.subheader("🐓 بورصة الماشية والداجن")
            for animal, price in st.session_state["global_livestock_prices"].items():
                if st.session_state["user_role"] == "owner":
                    st.session_state["global_livestock_prices"][animal] = st.number_input(f"تحديث سعر: {animal}", min_value=0.0, value=float(price), step=0.1, key=f"livestock_{animal}")
                else:
                    st.markdown(f"▪️ {animal}: **${price:.2f}**")
        with col_edit2:
            st.subheader("🥛 بورصة الألبان واللحوم والأطباق")
            for product, price in st.session_state["global_products_prices"].items():
                if st.session_state["user_role"] == "owner":
                    st.session_state["global_products_prices"][product] = st.number_input(f"تحديث سعر: {product}", min_value=0.0, value=float(price), step=0.05, key=f"prod_edit_{product}")
                else:
                    st.markdown(f"▪️ {product}: **${price:.2f}**")

    # تبويب إدارة المخازن والمستودعات
    with tabs[2]:
        st.markdown('<div class="section-title">🏭 لوحة التحكم الذكية بالمخازن والمستودعات المركزية</div>', unsafe_allow_html=True)
        if st.session_state["user_role"] == "specialist":
            st.warning("⚠️ حساب زميل/مختص: يمكنك مراجعة ومعاينة الأرصدة المتوفرة بالمخزن دون تعديل يدوي عليها.")
            
        inv_cols = st.columns(3)
        for idx, (ing_name, qty) in enumerate(list(st.session_state["inventory"].items())):
            with inv_cols[idx % 3]:
                status_badge = f'<span class="stock-critical">⚠️ حرج: {qty:.2f} طن</span>' if qty < 5.0 else f'<span class="stock-normal">آمن: {qty:.2f} طن</span>'
                st.markdown(f"**{ing_name}** | {status_badge}", unsafe_allow_html=True)
                if st.session_state["user_role"] == "owner":
                    st.session_state["inventory"][ing_name] = st.number_input(f"تحديث رصيد ({ing_name}) طن:", min_value=0.0, value=float(qty), key=f"inv_input_{ing_name}")

    # تبويب المبيعات والخصم التلقائي
    with tabs[3]:
        st.markdown('<div class="section-title">💰 نظام تسويق المنتجات وإصدار الفواتير مع الخصم التلقائي</div>', unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: client_name = st.text_input("اسم العميل / المزرعة المستلمة:", "مزارع الإنتاج المتكاملة")
        with col_c2: required_tons = st.number_input("الكمية المطلوبة (بالطن):", min_value=0.1, value=2.0, step=0.5)
        with col_c3: added_profit = st.number_input("هامش الربح الصافي المضاف لكل طن ($):", min_value=0.0, value=50.0)
        selling_price = st.session_state["computed_ton_cost"] + added_profit; total_bill = selling_price * required_tons
        st.markdown("### 🧾 فاتورة بيع وتوريد أعلاف رسمية")
        st.markdown(f"### 💰 إجمالي القيمة المستحقة للفاتورة: `${total_bill:.2f}` (أو تعادل `{total_bill*local_rate:,.1f}` {local_sym})")
        
        if st.session_state["user_role"] == "owner":
            if st.button("✅ تأكيد عملية البيع وخصم المكونات من المستودع"):
                can_deduct = True
                for name, pct in st.session_state["active_formula"].items():
                    if st.session_state["inventory"].get(name, 0.0) < ((pct / 100) * required_tons): 
                        can_deduct = False
                        st.error(f"❌ رصيد غير كافي في المخزن للمكون: {name}!")
                        break
                if can_deduct:
                    for name, pct in st.session_state["active_formula"].items(): 
                        st.session_state["inventory"][name] -= ((pct / 100) * required_tons)
                    st.success("🔥 تم الخصم التلقائي وتحديث المخازن بنجاح!"); time.sleep(1); st.rerun()
        else:
            st.info("ℹ️ تأكيد الفواتير وحركات الخصم المالي والترحيل متاحة حصرياً لإدارة المالك المنفرد للمنصة.")

    # تبويب مصمم ديباجات الطباعة 
    with tabs[4]:
        st.markdown('<div class="section-title">👑 مُصمم ديباجات الطباعة الفنية على جوالات الأعلاف</div>', unsafe_allow_html=True)
        trade_brand = st.text_input("اسم البراند التجاري لإصدار الفاتورة:", "منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف")
        st.markdown(f"""
        <div class="sack-tag">
            <img src="{st.session_state['active_animal_img']}" class="animal-banner-img">
            <h2 style="text-align: center; margin-top:0;">🌟 {trade_brand} 🌟</h2>
            <h3 style="text-align: center; color: #c62828; margin-top:0; font-weight: bold;">الاختصاصي م. عبد القادر إسماعيل تاور</h3>
            <p style="text-align: center; font-weight: bold; background-color:#e8f5e9; padding:6px; color:#1b5e20;">🎯 اختصاصي الإنتاج الحيواني | علف مخصص لـ: {st.session_state['active_stage_title']} | نسبة البروتين المحققة: {st.session_state['active_cp_tag']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    # خانة تعليقات المختصين والزملاء
    with tabs[5]:
        st.markdown('<div class="section-title">💬 قناة التواصل والتعليقات الخاصة بالزملاء والمختصين</div>', unsafe_allow_html=True)
        st.markdown("### 📝 دفتر الملاحظات الفنية المشتركة لتركيب العلائق:")
        
        st.text_area("التعليقات الحالية:", value=st.session_state["shared_comments"], height=200, disabled=True)
        
        new_comment = st.text_input("✍️ أكتب تعليقك الفني أو ملاحظتك التركيبية هنا لجهازك:")
        if st.button("📌 حفظ ونشر التعليق للزملاء"):
            if new_comment.strip():
                prefix = "• [توجيه الاختصاصي م. عبد القادر إسماعيل تاور]" if st.session_state["user_role"] == "owner" else "• [ملاحظة مختص]"
                st.session_state["shared_comments"] += f"{prefix}: {new_comment.strip()}\n"
                st.success("تمت إضافة الملاحظة لدفتر التعليقات الفني بنجاح!")
                time.sleep(0.5)
                st.rerun()

# ====================================================================
# 🗂️ التبويب المطور: دليل المستخدم في شكل كتيب رقمي جميل ومنسق (واضح القراءة)
# ====================================================================
support_tab_index = 6 if st.session_state["user_role"] in ["owner", "specialist"] else 1
with tabs[support_tab_index]:
    st.markdown('<div class="section-title">📖 كتيب دليل المستخدم والتقانة الفنية للمنصة</div>', unsafe_allow_html=True)
    
    col_guide, col_actions = st.columns([0.65, 0.35])
    
    with col_guide:
        # تصميم كتيب رقمي تفاعلي باستخدام HTML/CSS متقدم وعالي المرونة والحداثة في التبويب
        st.markdown("""
        <div class="manual-book">
            <div style="text-align: center; border-bottom: 2px double #2c3e50; padding-bottom: 15px; margin-bottom: 20px;">
                <h2 style="color: #2e7d32; margin: 0;">📖 الكتيب الرقمي الذكي لإدارة وتشغيل المنصة</h2>
                <p style="color: #7f8c8d; font-style: italic; margin: 5px 0 0 0;">إصدار هندسي محدث بأحدث تقنيات العرض لعام 2026</p>
                <p style="color: #2c3e50; font-weight: bold; margin: 5px 0 0 0;">المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور</p>
            </div>
            
            <div class="book-chapter">📌 التبويب الأول: الرؤية التقنية والهندسية للمنصة</div>
            <div class="book-body">
                تعتمد <b>منصة تاور العلمية</b> على دمج علوم الإنتاج الحيواني الدقيقة مع تقنيات الذكاء الاصطناعي وبحوث العمليات (Operations Research). 
                يتم تطبيق خوارزميات البرمجة الخطية (Linear Programming) عبر مكتبات متطورة مثل <code>SciPy</code> لضمان الوصول إلى خلطات علفية متزنة تماماً وبأقل تكلفة مادية ممكنة <b>(Least-Cost Formulation)</b> مع مرونة كاملة لتعديل النسب الفردية للخامات.
            </div>
            
            <div class="book-chapter">📌 التبويب الثاني: خارطة الطريق الشاملة للمكونات (Ingredients Matrix)</div>
            <div class="book-body">
                تم تصنيف المواد العلفية داخل المنصة بمرونة تامة لتشمل:<br>
                1. <b>الحبوب ومصادر الطاقة:</b> كالذرة البيضاء (Sorghum) لضبط مستويات التمثيل الغذائي بالطاقة، والذرة الصفراء التقليدية.<br>
                2. <b>الأكساب والبروتينات البديلة:</b> كسب زهرة الشمس (Sunflower Seed Cake) مدمج برمجياً كبديل اقتصادي مستدام للبروتين مع حماية الخوارزمية من تجاوز نسب الألياف الحرج.<br>
                3. <b>الإضافات والأملاح الدقيقة:</b> بريمكسات متخصصة, أحماض أمينية بلورية مصنعة لتأمين الاحتياجات الأيونية والبيولوجية الحيوية.
            </div>
            
            <div class="book-chapter">📌 التبويب الثالث: الوحدات الإنتاجية المتخصصة (Sectors Hub)</div>
            <div class="book-body">
                تم تبويب المنصة إلى واجهات برمجية منفصلة لسهولة الحركة والملاحة الفيلقية:<br>
                • <b>قطاع الدواجن والطيور:</b> يدعم دواجن التسمين، البياض، وطائر السمان حسب فترات النمو (بادي، نامي، ناهي).<br>
                • <b>قطاع المجترات والأبقار والماعز:</b> مخصص لتسمين اللحوم الحمراء أو غزارة إدرار الألبان والتحكم بالكرش.<br>
                • <b>قطاع الخيول والفروسية:</b> مخصص لأعلاف طاقة الجري أو أمهار نامية صغيرة.
            </div>
            
            <div class="book-chapter">📌 التبويب الرابع: خطوات تشغيل المنصة (من المدخلات إلى النتائج)</div>
            <div class="book-body">
                تتبع المنصة تقنية "الخطوات الذكية المرنة" لمنع الأخطاء الحقلية البيدرية:<br>
                <b>الخطوة 1:</b> حدد القطاع والنوع الإنتاجي من لوحة التحكم ليقوم المحرك بشحن الاحتياجات القياسية للبروتين تلقائياً.<br>
                <b>الخطوة 2:</b> اختر الخامات المتوفرة بالمستودع لديك وقم بوضع الأسعار الحالية للسوق المحلي.<br>
                <b>الخطوة 3:</b> اضغط على زر <i>تشغيل محرك الاستمثال الخطي</i> لتقوم المنصة بمعالجة الاحتمالات خلال أجزاء من الثانية والوصول للخلطة الأقل تكلفة.<br>
                <b>الخطوة 4:</b> استعرض تقرير فحص العلل، ثم قم بطباعة ديباجة الجوال أو تصدير التقرير الفني المباشر.
            </div>
            
            <div class="book-chapter">📌 التبويب الخامس: مرونة التقارير والدعم الفني المباشر</div>
            <div class="book-body">
                تمنحك المنصة القدرة على سحب تقارير فنية بصيغة PDF عالية التنسيق، مع إدرار نظام "الذكاء التحذيري" الذي يمنع حدوث طرأت مفاجئة في القطيع (مثل عوارض تحمض الكرش أو البراز الرطب للطيور) عبر الإضافة التلقائية والإلزامية للمنظمات والمحفزات الحيوية.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_actions:
        st.markdown("### 💬 قنوات التفاعل والاستشارات الفنية:")
        st.markdown("يمكنك إرسال استشارتك العلفية أو التعليق على البرنامج والتحسينات المطلوبة عبر القنوات التالية:")
        
        st.link_button("📝 إرسال تعليق أو طلب استشارة (نموذج جوجل)", GOOGLE_FORM_URL, use_container_width=True)
        
        welcome_msg = "السلام عليكم م. عبد القادر، أود الحصول على استشارة فنية بخصوص تركيب الأعلاف وحساب العلائق عبر منصة تاور العلمية..."
        encoded_msg = urllib.parse.quote(welcome_msg)
        whatsapp_link = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_msg}"
        st.link_button("💬 تواصل واستشارة مباشرة عبر الواتساب", whatsapp_link, use_container_width=True)
        
        st.markdown("<br><b>📢 انشر البرنامج وشارك المعرفة مع زملائك المربين والمهندسين:</b>", unsafe_allow_html=True)
        
        share_text_base = "أستخدم الآن منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف لحساب العلائق بأقل تكلفة ودقة علمية عالية، تحت إشراف م. عبد القادر إسماعيل تاور."
        encoded_share_text = urllib.parse.quote(share_text_base)
        
        col_wa, col_fb = st.columns(2)
        with col_wa:
            st.link_button("🟢 مشاركة عبر الواتساب", f"https://wa.me/?text={encoded_share_text}", use_container_width=True)
        with col_fb:
            st.link_button("🔵 مشاركة عبر فيسبوك", f"https://www.facebook.com/sharer/sharer.php?u=https://yourplatform.com&quote={encoded_share_text}", use_container_width=True)

# ====================================================================
# 📨 نظام حفظ وأرشفة السورس كود - مؤمن بالكامل لبريد المالك فقط
# ====================================================================
if st.session_state["user_role"] == "owner":
    st.markdown("<br><hr style='border-top: 1px dashed #2e7d32;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #1565C0; text-align:right;'>📨 أرشفة شفرة المصدر البرمجية للمنصة</h3>", unsafe_allow_html=True)

    col_mail_info, col_btn = st.columns([0.7, 0.3])
    with col_mail_info:
        st.info(f"🔒 حماية الخصوصية نشطة: سيتم إرسال ملف الكود مباشرة إلى البريد الشخصي المثبت للمالك فقط: ({OWNER_EMAIL})")

    with col_btn:
        st.markdown("<div style='padding-top: 5px;'></div>", unsafe_allow_html=True)
        if st.button("إرسال نسخة الكود للمالك 🚀", use_container_width=True, type="secondary"):
            with st.spinner("جاري تأمين الاتصال السحابي بالخادم وإرسال السورس كود..."):
                if send_code_to_mail(OWNER_EMAIL):
                    st.success(f"📥 تم إرسال السورس كود المحدث بأمان كملف (.py) إلى بريدك الهندسي المعتمد.")

st.markdown('</div>', unsafe_allow_html=True)

# التوقيع المصغر الثابت بأسفل الشاشة بالمسمى الجديد
st.markdown(
    """
    <div class="mini-left-signature">
        👨‍🔬 الاختصاصي م. عبد القادر إسماعيل تاور © 2026 | منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف
    </div>
    """,
    unsafe_allow_html=True
)
