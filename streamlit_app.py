import streamlit as st
import numpy as np
import json
import os
import base64
import smtplib
import time
import qrcode
from io import BytesIO
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================
# 1. إعدادات المنصة الرسمية والمظهر الفخم
# ==========================================
st.set_page_config(page_title="منصة تاور الذكية المتكاملة للأعلاف والإنتاج الحيواني", page_icon="🌾", layout="wide")

# بيانات التحكم والوصول والأمان
USER_ADMIN = "تاور"       
PASS_ADMIN = "202687"     

USER_GUEST = "مربي"       
PASS_GUEST = "2026"       

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

# 🔒 إعدادات خادم البريد الإلكتروني المرجعية (تأكد من تفعيل كلمة مرور التطبيق من جوجل)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"       
SENDER_PASSWORD = "oynz rdli tsdy ekdq"     

# رابط المنصة الافتراضي لتوليد الباركود (يمكنك تعديله للرابط الفعلي لاحقاً)
PLATFORM_URL = "https://tower-smart-feed.streamlit.app"

def get_image_base64(paths):
    for path in paths:
        if os.path.exists(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    return None

img_base64 = get_image_base64(PHOTO_OPTIONS)

# وظيفة توليد الباركود QR Code ديناميكياً
def generate_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1b5e20", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# وظيفة إرسال السورس كود عبر الإيميل
def send_code_to_mail(receiver_email):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود الكامل - منصة تاور الذكية المتكاملة للأعلاف"
    
    body = "السلام عليكم م. عبد القادر،\n\nمرفق مع هذه الرسالة النسخة البرمجية المحدثة والمستقرة لمنصة تاور الذكية لعام 2026 بصيغة (.py).\n\nتحياتي،\nالنظام التلقائي للمنصة."
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        current_file = __file__
        with open(current_file, "r", encoding="utf-8") as f:
            code_content = f.read()
        attachment = MIMEText(code_content, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', filename="tower_smart_platform.py")
        msg.attach(attachment)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ فشل إرسال الكود بسبب: {e}")
        return False

# وظيفة إرسال الفواتير عبر الإيميل
def send_invoice_to_mail(receiver_email, client, tons, formula, total_cost, currency):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = f"🧾 فاتورة علف رسمية صادرة من منصة تاور - {client}"
    
    formula_details = "\n".join([f"- {k}: {v:.2f}% ({v*10*tons:.1f} كجم إجمالي)" for k, v in formula.items()])
    
    body = f"""السلام عليكم ورحمة الله وبركاته،
    
مرفق لكم تفاصيل فاتورة توريد العلف الصادرة من:
مجموعة تاور لإنتاج الأعلاف ومصنعات الإنتاج الحيواني
الخبير المستشار / م. عبد القادر إسماعيل تاور

بيانات الفاتورة:
---------------------------------------------
العميل / المزرعة المستلمة: {client}
الكمية المطلوبة: {tons} طن
إجمالي قيمة الفاتورة: {total_cost:,.2f} {currency}

تفاصيل الخلطة العلفية ومكوناتها لكل طن:
---------------------------------------------
{formula_details}

شكراً لتعاملكم معنا.
منصة تاور الذكية للأعلاف والمستودعات 2026.
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ فشل إرسال الفاتورة عبر الإيميل بسبب: {e}")
        return False

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;700&display=swap');
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
    h1, h2, h3, h4, h5, p, span { font-family: 'Cairo', sans-serif; }
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
        border: 4px dashed #1b5e20;
        padding: 30px;
        border-radius: 15px;
        background-color: #f1f8e9;
        direction: rtl;
        text-align: right;
        max-width: 650px;
        margin: 0 auto;
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
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. بوابة الدخول وحماية النظام
# ==========================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة</h2>", unsafe_allow_html=True)
    
    input_user = st.text_input("👤 اسم المستخدم:")
    input_pass = st.text_input("🔑 كلمة المرور:", type="password")
    
    if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
        if input_user == USER_ADMIN and input_pass == PASS_ADMIN:
            st.session_state["approved"] = True; st.session_state["user_role"] = "admin"; st.rerun()
        elif input_user == USER_GUEST and input_pass == PASS_GUEST:
            st.session_state["approved"] = True; st.session_state["user_role"] = "guest"; st.rerun()
        else: st.error("❌ بيانات الاعتماد غير صحيحة.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# 3. الهيكل الافتراضي للمخازن وبورصة تاور العالمية الشاملة ($)
# =====================================================================
if "inventory" not in st.session_state:
    st.session_state["inventory"] = {
        "ذرة صفراء": 25.0, "ذرة بيضاء": 10.0, "شعير مطحون": 15.0, "سورجم (فتريتة)": 15.0, "قمح محلي مصنّع": 12.0,
        "أمباز الفول السوداني (كسب)": 20.0, "كسب فول صويا 44%": 14.0, "كسب فول صويا 48%": 18.0, "كسب عباد الشمس 36%": 10.0, "كسب بذور القطن": 8.0,
        "نخالة قمح (ردة)": 20.0, "البرسيم الجاف (الدريس)": 30.0, "مولاس": 5.0,
        "مسحوق أسماك (Fishmeal 60%)": 4.0, "مركزات دواجن وسمان": 3.5, "مركزات خيول ومجترات": 3.5,
        "الحجر الجيري (بودرة بلاط)": 6.0, "فوسفات ثنائي الكالسيوم (DCP)": 3.0, "ملح الطعام": 2.5, "مضاد سموم فطرية": 1.2,
        "بيكربونات الصوديوم (الصودا)": 5.0, "إنزيم الفايتيز الزامي (Phytase Super-D)": 2.0, "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": 2.0,
        "إنزيم بروتياز متطور (Protease)": 2.0, "مضاد سموم بيولوجي سائل": 1.5, "إنزيم ليزوزيم مناعي": 1.0, "إنزيم الليباز المتخصص للدهون": 1.0,
        "كبريتات الحديدوز (معادل الجوسيبول)": 2.0
    }

if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين / محسن ($)": 1350.0, "أبقار كنانة وبطانة محلية ($)": 900.0,
        "ضأن وستيرلنغ / محلي ($)": 180.0, "ماعز نوبي وصحراوي ($)": 130.0, "خيول عربية أصيلة وهجين ($)": 4500.0,
        "كتكوت لاحم عمر يوم ($)": 0.65, "دجاج بياض عمر البشاير ($)": 5.50
    }

if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري صافي ($)": 7.50, "كيلو لحم ضأن طازج ($)": 9.00, "كيلو لحم دجاج لاحم صافي ($)": 3.80,
        "طبق بيض مائدة 30 بيضة ($)": 4.20, "رطل / لتر حليب خام ($)": 0.90, "كيلو جبن أبيض محلي ($)": 5.00
    }

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"}, "ليبيا": {"rate": 4.80, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"}, "باقي دول العالم / البورصة المفتوحة": {"rate": 1.0, "sym": "USD"}
}

def get_adjusted_market_data(country, state_or_region, city):
    feed_prices = {k: 250.0 for k in st.session_state["inventory"].keys()}
    # أسعار افتراضية تخصصية للإنزيمات والمضافات الدقيقة
    feed_prices.update({
        "إنزيم الفايتيز الزامي (Phytase Super-D)": 1200.0, "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": 1400.0,
        "إنزيم بروتياز متطور (Protease)": 1500.0, "مضاد سموم بيولوجي سائل": 1800.0, "إنزيم ليزوزيم مناعي": 2500.0,
        "إنزيم الليباز المتخصص للدهون": 1600.0, "كبريتات الحديدوز (معادل الجوسيبول)": 450.0, "مضاد سموم فطرية": 950.0
    })
    return feed_prices

BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "priority": 1.3}, "ذرة بيضاء": {"CP": 8.8, "priority": 0.9}, 
        "شعير مطحون": {"CP": 11.5, "priority": 1.1}, "سورجم (فتريتة)": {"CP": 10.0, "priority": 1.0},
        "قمح محلي مصنّع": {"CP": 12.0, "priority": 1.05}
    },
    "الأكساب والأمباز ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "prio_prot": 1.1}, "كسب فول صويا 44%": {"CP": 44.0, "prio_prot": 1.2}, 
        "كسب فول صويا 48%": {"CP": 48.0, "prio_prot": 1.25}, "كسب عباد الشمس 36%": {"CP": 36.0, "prio_prot": 0.85},
        "كسب بذور القطن": {"CP": 41.0, "prio_prot": 0.8}
    },
    "🧪 قسم الإنزيمات ومضادات السموم والمعالجات الحقلية الذكية": {
        "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0}, "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0},
        "إنزيم بروتياز متطور (Protease)": {"CP": 0.0}, "مضاد سموم بيولوجي سائل": {"CP": 0.0}, 
        "إنزيم ليزوزيم مناعي": {"CP": 0.0}, "إنزيم الليباز المتخصص للدهون": {"CP": 0.0},
        "كبريتات الحديدوز (معادل الجوسيبول)": {"CP": 0.0}, "مضاد سموم فطرية": {"CP": 0.0}
    },
    "المخلفات الرعوية والمواد المالئة والإضافات الفنية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "prio_fill": 1.2}, "البرسيم الجاف (الدريس)": {"CP": 16.5, "prio_fill": 0.9}, 
        "مولاس": {"CP": 4.0, "prio_fill": 1.0}, "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "prio_fill": 0.5}
    },
    "الإضافات المتخصصة والمركزات دقيقة الخلط": {
        "مركزات دواجن وسمان": {"CP": 40.0}, "مركزات خيول ومجترات": {"CP": 36.0}, "الحجر الجيري (بودرة بلاط)": {"CP": 0.0}, "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0}, "ملح الطعام": {"CP": 0.0}
    }
}

ANIMAL_IMAGES_RESOURCES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600&auto=format&fit=crop",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600&auto=format&fit=crop",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600&auto=format&fit=crop",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600&auto=format&fit=crop",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop"
}

if "active_formula" not in st.session_state: st.session_state["active_formula"] = {"ذرة صفراء": 62.0, "كسب فول صويا 44%": 33.0, "إضافات مخصصة": 5.0}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 16.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_animal_img" not in st.session_state: st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES["عام"]
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0

# ==========================================
# 4. بناء الواجهة الرئيسية للمنصة
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    if img_base64: st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else: st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور الذكية للإنتاج الحيواني وصناعة الأعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.2rem; margin-top:5px; margin-bottom:0;'>توليد الباركود ونظام المضافات التلقائية وإرسال الفواتير البريدية الشاملة</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

toast_container = st.empty()

tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى"]
if st.session_state["user_role"] == "admin":
    tabs_titles += ["📊 بورصة تاور المركزية", "🏭 إدارة المستودعات والخصم", "🧾 التسويق وفواتير الإيميل", "🖨️ مصمم ديباجات الجوالات والباركود"]

tabs = st.tabs(tabs_titles)

with tabs[0]:
    st.markdown('<div class="section-title">🌍 تحديد الموقع الجغرافي وبورصة الأسعار</div>', unsafe_allow_html=True)
    col_country, col_state, col_city = st.columns(3)
    with col_country: user_country = st.selectbox("اختر دولة المربي:", ["السودان", "ليبيا", "مصر", "باقي دول العالم"])
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    local_rate = c_info["rate"]; local_sym = c_info["sym"]
    with col_state: chosen_state = st.text_input("الولاية / الإقليم:", "شمال كردفان")
    with col_city: user_city = st.text_input("المدينة الحقلية:", "الأبيض")

    live_prices = get_adjusted_market_data(user_country, chosen_state, user_city)

    st.markdown('<div class="section-title">⚖️ اختيار القطاع والنوع والإنتاجية المستهدفة</div>', unsafe_allow_html=True)
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec: main_sector = st.selectbox("اختر القطاع الإنتاجي الرئيسي:", ["الطيور والسمان", "الأبقار وسلالاتها", "الماعز وسلالاته", "الخيول والفروسية"])
    with col_sub: sub_type = st.selectbox("السلالة والنوع الفرعي:", ["دواجن لاحم (Broiler)", "دواجن بياض (Layer)", "هولشتاين", "كنانة"])
    with col_prod: prod_stage = st.selectbox("المرحلة الفسيولوجية:", ["بادي دواجن 23%", "نامي دواجن 21%", "ناهي دواجن 19%", "حليب وغزارة إدرار"])
    
    default_cp = 23.0 if "بادي" in prod_stage else (21.0 if "نامي" in prod_stage else 18.0)
    final_target_cp = st.slider("حدد نسبة البروتين المستهدفة فنيّاً (%):", 10.0, 45.0, value=default_cp)

    st.markdown('<div class="section-title">🌾 اختيار الخامات المتاحة (سيتم تفعيل الإنزيمات تلقائياً عند تجاوز الحدود)</div>', unsafe_allow_html=True)
    selected_ingredients = []; ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=True):
            sub_cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with sub_cols[idx % 3]:
                    # جعل الإنزيمات غير محددة افتراضياً ليقوم المحرك بتنشيطها تلقائياً عند الحاجة
                    is_def = True if "ذرة صفراء" in ing_name or "صويا" in ing_name or "ملح" in ing_name else False
                    checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                    current_live_price = live_prices.get(ing_name, 350.0)
                    price_input = st.number_input(f"سعر الطن ({ing_name}) $:", min_value=10.0, value=float(current_live_price), key=f"price_{ing_name}")
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price_input

    if st.button("🚀 تشغيل محرك التركيب وتطبيق قيود الإنزيمات والطاقة الحبوبية", type="primary", use_container_width=True):
        formula_results = {}
        mandatory_warnings = []
        auto_added_enzymes = {}

        # تطبيق قيود الطاقة الحبوبية الصارمة (60% - 65%)
        grain_share = 63.0 if final_target_cp < 22 else 60.0
        grains_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"]]
        if not grains_ingredients: grains_ingredients = ["ذرة صفراء"]
        
        for x in grains_ingredients:
            formula_results[x] = grain_share / len(grains_ingredients)

        # حساب الإضافات والبروتينات
        fixed_ratios = {"ملح الطعام": 0.5, "الحجر الجيري (بودرة بلاط)": 1.5}
        for k, v in fixed_ratios.items(): formula_results[k] = v
        
        leftover_pct = 100.0 - grain_share - sum(fixed_ratios.values())
        protein_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"]]
        if not protein_ingredients: protein_ingredients = ["كسب فول صويا 44%"]
        
        for x in protein_ingredients:
            formula_results[x] = leftover_pct / len(protein_ingredients)

        # 🧪 تفعيل الإنزيمات والمضافات الدقيقة تلقائياً حسب المكونات والحدود الحقلية المسموحة
        total_grains_pct = grain_share
        if main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاته"] and total_grains_pct > 45.0:
            auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.75
            mandatory_warnings.append("🚨 <b>بيكربونات الصوديوم إلزامية:</b> نسبة الحبوب تجاوزت حد الأمان الفني وبلغت ({:.1f}%) لمنع حموضة الكرش.".format(total_grains_pct))
        
        if main_sector in ["الطيور والسمان", "الأسماك والأحياء المائية"]:
            auto_added_enzymes["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05
            mandatory_warnings.append("🚨 <b>إنزيم الفايتيز إلزامي:</b> تم ضخه تلقائياً لتحرير الفسفور النباتي.")

        if "شعير مطحون" in selected_ingredients or "قمح محلي مصنّع" in selected_ingredients:
            auto_added_enzymes["إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)"] = 0.08
            mandatory_warnings.append("⚠️ <b>معالجة NSP المعوي:</b> تم إدراج زيلاناز وبيتا جلوكاناز لعلاج لزوجة هضم حبوب القمح/الشعير.")

        if "كسب بذور القطن" in formula_results:
            auto_added_enzymes["كبريتات الحديدوز (معادل الجوسيبول)"] = 0.15
            mandatory_warnings.append("⚠️ <b>معادل الجوسيبول نشط:</b> تم دمج كبريتات الحديدوز لربط السمية الحرة لكسب بذور القطن.")

        if "كسب عباد الشمس 36%" in formula_results:
            auto_added_enzymes["إنزيم بروتياز متطور (Protease)"] = 0.05
            mandatory_warnings.append("🌾 <b>إنزيم بروتياز متطور:</b> مدمج لكسر روابط الألياف الخشنة لكسب عباد الشمس.")

        if "أمباز الفول السوداني (كسب)" in formula_results:
            auto_added_enzymes["مضاد سموم بيولوجي سائل"] = 0.10
            mandatory_warnings.append("🧫 <b>مكافحة الأفلاتوكسين:</b> تم تفعيل مضاد سموم بيولوجي واسع الطيف لحماية الكبد من سموم الأمباز.")

        # حسم نسب الإنزيمات من خامة الذرة لضبط توازن الـ 100%
        if auto_added_enzymes:
            for enz_name, enz_pct in auto_added_enzymes.items():
                formula_results[enz_name] = enz_pct
                if "ذرة صفراء" in formula_results: formula_results["ذرة صفراء"] -= enz_pct

        st.session_state["active_formula"] = formula_results
        st.session_state["computed_ton_cost"] = sum([(v/100) * ingredient_prices.get(k, 300.0) for k, v in formula_results.items() if k in ingredient_prices])
        st.session_state["active_cp_tag"] = final_target_cp
        st.session_state["active_stage_title"] = f"{main_sector} - {prod_stage}"

        st.success("🎯 تم احتساب التركيبة وتطبيق محرك الإنزيمات بدقة.")
        
        # تفعيل الإشعار المؤقت لمدة 30 ثانية
        with toast_container.container():
            if mandatory_warnings:
                st.markdown("### 🔬 تقرير التدخل البرمجي ومحرك الإنزيمات المتقدم:")
                for warn in mandatory_warnings:
                    st.markdown(f'<div class="warning-card">{warn}</div>', unsafe_allow_html=True)
                st.toast("🔬 تم ضخ التوليفة الإنزيمية التلقائية لحماية العليقة!", icon="🧪")
        
        for k, v in formula_results.items():
            st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** / طن)")
        
        time.sleep(30)
        toast_container.empty()

# ==========================================
# التبويبات الإدارية للمالك فقط
# ==========================================
if st.session_state["user_role"] == "admin":
    with tabs[1]:
        st.write("📊 لوحة تحكم البورصة المركزية لتاور")
    with tabs[2]:
        st.write("🏭 إدارة حركة المستودعات")
        
    with tabs[3]:
        st.markdown('<div class="section-title">🧾 نظام تسويق المنتجات وإرسال الفواتير عبر الإيميل</div>', unsafe_allow_html=True)
        col_c1, col_c2, col_mail_inv = st.columns(3)
        with col_c1: client_name = st.text_input("اسم العميل / المزرعة المستلمة:", "مزارع الوادي السعيد")
        with col_c2: required_tons = st.number_input("الكمية المطلوبة (بالطن):", min_value=0.1, value=2.0)
        with col_mail_inv: client_email = st.text_input("بريد العميل الإلكتروني لإرسال الفاتورة:", "client@example.com")
        
        total_bill = st.session_state["computed_ton_cost"] * required_tons
        st.metric("إجمالي الفاتورة الحالي ($):", f"${total_bill:,.2f}")
        
        if st.button("✅ إصدار الفاتورة وإرسالها للإيميل فوراً"):
            with st.spinner("جاري الاتصال بخادم البريد التلقائي..."):
                if send_invoice_to_mail(client_email, client_name, required_tons, st.session_state["active_formula"], total_bill, "دولار"):
                    st.success(f"📥 تم إرسال الفاتورة التفصيلية بنجاح إلى البريد: {client_email}")

    with tabs[4]:
        st.markdown('<div class="section-title">🏷️ مُصمم ديباجات الطباعة الفنية والباركود QR على جوالات الأعلاف</div>', unsafe_allow_html=True)
        
        qr_bytes = generate_qr_code(PLATFORM_URL)
        qr_b64 = base64.b64encode(qr_bytes).decode()
        
        st.markdown(f"""
        <div class="sack-tag">
            <h2 style="text-align: center; color: #1b5e20; margin-top:0; font-weight: bold;">🌾 مجموعة تاور لإنتاج الأعلاف ومصنعات الإنتاج الحيواني 🌾</h2>
            <h3 style="text-align: center; color: #c62828; margin-top:0; font-weight: bold;">بيانات المالك: الخبير المستشار م. عبد القادر إسماعيل تاور</h3>
            <p style="text-align: center; font-size:1.1rem; color: #1565C0;">📌 تركيبة مخصصة لـ: {st.session_state['active_stage_title']}</p>
            <p style="text-align: center; font-weight: bold; background-color:#e8f5e9; padding:6px; color:#1b5e20;">🧬 نسبة البروتين الفعلية: {st.session_state['active_cp_tag']:.1f}%</p>
            <hr style="border-top: 2px dashed #1b5e20;">
            <p style="text-align: center; font-size: 0.9rem; color:#555; margin-bottom:5px;">📷 قم بتصوير الباركود أدناه بكاميرا الجوال للدخول المباشر إلى المنصة الذكية لتركيب العلف:</p>
            <div style="text-align: center;">
                <img src="data:image/png;base64,{qr_b64}" style="width: 160px; height: 160px; border: 3px solid #1b5e20; padding: 5px; background: white; border-radius: 8px;">
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="mini-left-signature">👨‍🔬 م. عبد القادر إسماعيل تاور © 2026 | خبير الحلول الذكية للثروة الحيوانية والبرمجيات المتكاملة</div>', unsafe_allow_html=True)
