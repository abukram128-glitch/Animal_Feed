import streamlit as st
import numpy as np
import json
import os
import base64
import smtplib
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

# ------------------------------------------
# 🔒 إعدادات خادم البريد الإلكتروني المرجعية المحدثة بالرمز الجديد
# ------------------------------------------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"       # ✅ إيميلك الشخصي
SENDER_PASSWORD = "oynz rdli tsdy ekdq"     # ✅ رمز التطبيق الجديد الصحيح من جوجل

def get_image_base64(paths):
    for path in paths:
        if os.path.exists(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    return None

img_base64 = get_image_base64(PHOTO_OPTIONS)

def send_code_to_mail(receiver_email):
    if SENDER_EMAIL == "YOUR_EMAIL@gmail.com" or SENDER_PASSWORD == "xxxx xxxx xxxx xxxx":
        st.error("⚠️ خطأ إعدادات: يرجى تحديث بيانات الـ SMTP داخل السورس كود أولاً.")
        return False
        
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود الكامل - منصة تاور الذكية المتكاملة للأعلاف"
    
    body = "السلام عليكم م. عبد القادر،\n\nمرفق مع هذه الرسالة النسخة البرمجية الشاملة والمدمجة لمنصة تاور الذكية لعام 2026 بصيغة (.py) كنسخة احتياطية مأرشفة.\n\nتحياتي،\nالنظام التلقائي للمنصة."
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        code_content = ""
        current_file = None
        try:
            current_file = __file__
        except NameError:
            pass
            
        if current_file and os.path.exists(current_file):
            with open(current_file, "r", encoding="utf-8") as f:
                code_content = f.read()
        elif os.path.exists("app.py"): 
            with open("app.py", "r", encoding="utf-8") as f:
                code_content = f.read()
        elif os.path.exists("tower_smart_platform.py"):
            with open("tower_smart_platform.py", "r", encoding="utf-8") as f:
                code_content = f.read()
        else:
            code_content = "# تعذر قراءة الملف برمجياً من السيرفر السحابي الحالي، يرجى مراجعة إدارة المطور عبد القادر تاور."

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
        st.error(f"❌ فشل الإرسال بسبب: {e}")
        return False

# تطبيق الـ CSS المخصص والتنسيقات البصرية المتناسقة والمحاذاة لليمين (RTL)
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
if "approved" not in st.session_state:
    st.session_state["approved"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555;'>فضلاً أدخل بيانات الحساب للولوج للمنظومة العلفية</p>", unsafe_allow_html=True)
    
    input_user = st.text_input("👤 اسم المستخدم:")
    input_pass = st.text_input("🔑 كلمة المرور:", type="password")
    
    if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
        if input_user == USER_ADMIN and input_pass == PASS_ADMIN:
            st.session_state["approved"] = True
            st.session_state["user_role"] = "admin"
            st.rerun()
        elif input_user == USER_GUEST and input_pass == PASS_GUEST:
            st.session_state["approved"] = True
            st.session_state["user_role"] = "guest"
            st.rerun()
        else:
            st.error("❌ بيانات الاعتماد غير صحيحة.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# 3. الهيكل الشامل والمدمج للمخازن والبورصة والمكتبة العلفية الكبرى
# =====================================================================
if "inventory" not in st.session_state:
    st.session_state["inventory"] = {
        "ذرة صفراء": 25.0, "ذرة بيضاء": 10.0, "شعير مطحون": 15.0, "سورجم (فتريتة)": 15.0, "قمح محلي مصنّع": 12.0,
        "أمباز الفول السوداني (كسب)": 20.0, "كسب فول صويا 44%": 14.0, "كسب فول صويا 48%": 18.0, "كسب عباد الشمس 36%": 10.0, "كسب بذور القطن": 8.0,
        "نخالة قمح (ردة)": 20.0, "البرسيم الجاف (الدريس)": 30.0, "مولاس": 5.0,
        "مسحوق أسماك (Fishmeal 60%)": 4.0, "مركزات دواجن وسمان": 3.5, "مركزات خيول ومجترات": 3.5,
        "الحجر الجيري (بودرة بلاط)": 6.0, "فوسفات ثنائي الكالسيوم (DCP)": 3.0, "ملح الطعام": 2.5, "مضاد سموم فطرية": 1.2,
        "بيكربونات الصوديوم (الصودا)": 5.0
    }

if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين / محسن ($)": 1350.0,
        "أبقار كنانة وبطانة محلية ($)": 900.0,
        "ضأن وستيرلنغ / محلي ($)": 180.0,
        "ماعز نوبي وصحراوي ($)": 130.0,
        "خيول عربية أصيلة وهجين ($)": 4500.0,
        "كتكوت لاحم عمر يوم ($)": 0.65,
        "دجاج بياض عمر البشاير ($)": 5.50
    }

if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري صافي ($)": 7.50,
        "كيلو لحم ضأن طازج ($)": 9.00,
        "كيلو لحم دجاج لاحم صافي ($)": 3.80,
        "طبق بيض مائدة 30 بيضة ($)": 4.20,
        "رطل / لتر حليب خام ($)": 0.90,
        "كيلو جبن أبيض محلي ($)": 5.00,
        "كيلو جبن جاف / شيدر ($)": 8.50
    }

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "ليبيا": {"rate": 4.80, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"},
    "باقي دول العالم / البورصة المفتوحة": {"rate": 1.0, "sym": "USD"}
}

def get_adjusted_market_data(country, state_or_region, city):
    feed_prices = {
        "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0, "سورجم (فتريتة)": 195.0, "قمح محلي مصنّع": 240.0,
        "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا 44%": 440.0, "كسب فول صويا 48%": 480.0, "كسب عباد الشمس 36%": 310.0, "كسب بذور القطن": 290.0,
        "نخالة قمح (ردة)": 150.0, "البرسيم الجاف (الدريس)": 170.0, "مولاس": 120.0,
        "مسحوق أسماك (Fishmeal 60%)": 850.0, "مركزات دواجن وسمان": 650.0, "مركزات خيول ومجترات": 600.0,
        "الحجر الجيري (بودرة بلاط)": 40.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0, "ملح الطعام": 30.0, "مضاد سموم فطرية": 950.0,
        "بيكربونات الصوديوم (الصودا)": 340.0
    }
    
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
    elif country == "ليبيا":
        multiplier = 1.10
        if city == "طبرق": multiplier = 1.06
    elif country == "مصر":
        multiplier = 1.04

    for k in feed_prices: feed_prices[k] *= multiplier
    return feed_prices

# المكتبة العلفية الشاملة المدمجة بالكامل
BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "priority": 1.3}, 
        "ذرة بيضاء": {"CP": 8.8, "priority": 0.9}, 
        "شعير مطحون": {"CP": 11.5, "priority": 1.1}, 
        "سورجم (فتريتة)": {"CP": 10.0, "priority": 1.0},
        "قمح محلي مصنّع": {"CP": 12.0, "priority": 1.05}
    },
    "الأكساب والأمباز ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "prio_prot": 1.1}, 
        "كسب فول صويا 44%": {"CP": 44.0, "prio_prot": 1.2}, 
        "كسب فول صويا 48%": {"CP": 48.0, "prio_prot": 1.25}, 
        "كسب عباد الشمس 36%": {"CP": 36.0, "prio_prot": 0.85},
        "كسب بذور القطن": {"CP": 41.0, "prio_prot": 0.8}
    },
    "المخلفات الرعوية والمواد المالئة والإضافات الفنية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "prio_fill": 1.2}, 
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "prio_fill": 0.9}, 
        "مولاس": {"CP": 4.0, "prio_fill": 1.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "prio_fill": 0.5}
    },
    "المركزات دقيقة الخلط ومكملات الأيونات": {
        "مركزات دواجن وسمان": {"CP": 40.0}, 
        "مركزات خيول ومجترات": {"CP": 36.0}, 
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0},
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0}, 
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0}, 
        "ملح الطعام": {"CP": 0.0}, 
        "مضاد سموم فطرية": {"CP": 0.0}
    }
}

ANIMAL_IMAGES_RESOURCES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600&auto=format&fit=crop",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600&auto=format&fit=crop",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600&auto=format&fit=crop",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600&auto=format&fit=crop",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600&auto=format&fit=crop",
    "سمان": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600&auto=format&fit=crop",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop"
}

if "active_formula" not in st.session_state: st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0, "إضافات مخصصة": 5.0}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 16.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_animal_img" not in st.session_state: st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES["عام"]
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0

# ==========================================
# 4. بناء الهيكل والواجهات البصرية للمنصة
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    if img_base64: st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else: st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور الذكية للإنتاج الحيواني وصناعة الأعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.2rem; margin-top:5px; margin-bottom:0;'>دمج كامل وشامل للمكتبة العلفية الكبرى ومحرك حساب نسب الخلط المتقدم</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

if st.session_state["user_role"] == "admin":
    tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى", "📊 بورصة تاور المركزية للمنتجات والماشية", "🏭 إدارة المستودعات والخصم التلقائي", "🧾 التسويق وفواتير حركة البيع", "🖨️ مصمم بطاقات الديباجة والدعاية"]
else:
    tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى"]

tabs = st.tabs(tabs_titles)

with tabs[0]:
    st.markdown('<div class="section-title">🌍 أولاً: تحديد الموقع الجغرافي وبورصة الأسعار بالعملتين المحلية والأجنبية</div>', unsafe_allow_html=True)
    col_country, col_state, col_city = st.columns(3)
    with col_country: user_country = st.selectbox("اختر دولة المربي:", ["السودان", "ليبيا", "مصر", "باقي دول العالم / البورصة المفتوحة"])
        
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    local_rate = c_info["rate"]; local_sym = c_info["sym"]

    chosen_state = "عام"
    with col_state:
        if user_country == "السودان":
            chosen_state = st.selectbox("اختر الولاية السودانية المحدثة:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال كردفان", "ولاية جنوب كردفان", "ولاية غرب كردفان", "إقليم النيل الأزرق", "ولاية البحر الأحمر", "ولاية نهر النيل"])
        elif user_country == "ليبيا": chosen_state = st.selectbox("اختر الإقليم الجغرافي:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
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
        elif user_country == "ليبيا":
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
        if main_sector == "الخيول والفروسية": sub_type = st.selectbox("السلالة المستهدفة:", ["خيل عربي أصيل", "ثوروبريد", "خيول محلية هجين"]); dynamic_img_key = "خيول"; show_measurements = True; weight_factor = 11877; feed_factor = 0.022; chosen_concentrate = "مركزات خيول ومجترات"
        elif main_sector == "الماعز وسلالاته": sub_type = st.selectbox("السلالة المستهدفة:", ["الماعز النوبي السوداني", "الماعز الصحراوي", "بور / محسن"]); dynamic_img_key = "ماعز"; show_measurements = True; weight_factor = 11250; feed_factor = 0.028; chosen_concentrate = "مركزات خيول ومجترات"
        elif main_sector == "الأبقار وسلالاتها": sub_type = st.selectbox("السلالة المستهدفة:", ["كنانة (سوداني)", "بطانة (مدر)", "هولشتاين / محسن"]); dynamic_img_key = "أبقار"; show_measurements = True; weight_factor = 10838; feed_factor = 0.025; chosen_concentrate = "مركزات خيول ومجترات"
        elif main_sector == "الطيور والسمان": sub_type = st.selectbox("نوع الطيور:", ["طائر السمان (Quail)", "دواجن لاحم (Broiler)", "دواجن بياض (Layer)"]); dynamic_img_key = "سمان" if "السمان" in sub_type else "دواجن"; chosen_concentrate = "مركزات دواجن وسمان"
        else: sub_type = st.selectbox("نوع الأسماك:", ["البلطي النيلي (Tilapia)", "القرموط"]); dynamic_img_key = "أسماك"; chosen_concentrate = "مسحوق أسماك (Fishmeal 60%)"

    with col_prod:
        if main_sector == "الخيول والفروسية": prod_stage = st.selectbox("نوع الإنتاج:", ["خيول رياضة ونشاط مكثف", "أمهار نامية صغيرة", "فرسات مرضعات"]); default_cp = 16.0 if "أمهار" in prod_stage or "مرضعات" in prod_stage else 12.0
        elif main_sector == "الماعز وسلالاته": prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج اللحوم وتسمين", "إنتاج ألبان وحليب"]); default_cp = 15.5 if "ألبان" in prod_stage else 13.5
        elif main_sector == "الأبقار وسلالاتها": prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج حليب وغزارة إدرار", "تسمين عجول مكثف"]); default_cp = 16.0 if "حليب" in prod_stage else 13.0
        elif main_sector == "الطيور والسمان":
            if "السمان" in sub_type: prod_stage = st.selectbox("نوع الإنتاج:", ["سمان بادي / نامي", "سمان بياض إنتاجي"]); default_cp = 24.0 if "بادي" in prod_stage else 20.0
            else: prod_stage = st.selectbox("نوع الإنتاج:", ["بادي دواجن 23%", "نامي دواجن 21%", "ناهي دواجن 19%", "بياض إنتاجي"]); default_cp = 23.0 if "بادي" in prod_stage else (21.0 if "نامي" in prod_stage else (19.0 if "ناهي" in prod_stage else 17.5))
        else: prod_stage = st.selectbox("نوع الإنتاج:", ["بادئ زريعة أسماك عالي", "نمو وتسمين أسماك نيلية"]); default_cp = 35.0 if "زريعة" in prod_stage else 30.0

    if show_measurements:
        st.markdown('<div class="section-title">📐 ثالثاً: شريط القياس الجسدي وتقدير الأوزان</div>', unsafe_allow_html=True)
        col_h, col_l, col_ag = st.columns(3)
        with col_h: h_girth = st.number_input("📏 محيط الصدر (سم):", value=150.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 70.0)
        with col_l: b_length = st.number_input("📏 طول الجسم (سم):", value=130.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 60.0)
        with col_ag: a_months = st.number_input("⏳ عمر الحيوان التقديـري (أشهر):", value=12)
        calc_weight = (h_girth ** 2 * b_length) / weight_factor; req_feed_kg = calc_weight * feed_factor
        st.success(f"📊 الوزن الحيوي المتوقع للحيوان: **{calc_weight:.1f} كجم** | الاحتياج اليومي من المادة الجافة: **{req_feed_kg:.2f} كجم**")
    else:
        st.markdown('<div class="section-title">✨ ثالثاً: قطاع الطيور والأسماك</div>', unsafe_allow_html=True)
        st.info(f"💡 نظام المعالجة التلقائي: تم تحييد شريط القياس الجسدي لعدم ملاءمته حَقلياً للطيور والأسماك.")

    st.markdown('<div class="section-title">📋 رابعاً: ضبط نسبة البروتين المستهدفة فنيّاً</div>', unsafe_allow_html=True)
    col_p1, col_p2 = st.columns(2)
    with col_p1: st.metric("🧬 بروتين العليقة المقترح من المنصة:", f"{default_cp} %")
    with col_p2:
        override_cp = st.checkbox("⚙️ تفعيل التعديل الفني الاختياري للبروتين")
        final_target_cp = st.slider("حدّد نسبة البروتين المستهدفة فنيّاً:", 10.0, max_value=45.0, value=default_cp) if override_cp else default_cp

    st.markdown('<div class="section-title">🌾 خامساً: توليد العليقة الاقتصادية المتزنة وطباعة التركيبة</div>', unsafe_allow_html=True)
    selected_ingredients = []; ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=True):
            sub_cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with sub_cols[idx % 3]:
                    is_def = True if ing_name == chosen_concentrate or "ذرة صفراء" in ing_name or "صويا" in ing_name or "ملح" in ing_name or "بيكربونات" in ing_name else False
                    checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                    current_live_price = live_prices.get(ing_name, 350.0)
                    
                    if st.session_state["user_role"] == "admin": price_input = st.number_input(f"السعر للطن ({ing_name}) $:", min_value=10.0, value=float(current_live_price), key=f"price_{ing_name}")
                    else:
                        st.markdown(f"💰 السعر الحالي بموقعك: **`${current_live_price:.2f}`** / طن (أو يعادل **`{(current_live_price * local_rate):,.1f}`** {local_sym})")
                        price_input = current_live_price
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price_input

    st.markdown("---")
    if st.button("🚀 تشغيل محرك التركيب الذكي وحساب نسب الخلط المثلى", type="primary", use_container_width=True):
        if chosen_concentrate and chosen_concentrate not in selected_ingredients:
            selected_ingredients.append(chosen_concentrate)
            ingredient_prices[chosen_concentrate] = live_prices.get(chosen_concentrate, 550.0)

        if len(selected_ingredients) < 3: st.error("⚠️ يرجى تحديد 3 خامات علفية على الأقل لضمان توليفة متزنة.")
        else:
            formula_results = {}
            mandatory_warnings = []
            auto_added_enzymes = {}

            fixed_ratios = {"ملح الطعام": 0.005, "مضاد سموم فطرية": 0.002, "الحجر الجيري (بودرة بلاط)": 0.025 if "بياض" in prod_stage else 0.015, "فوسفات ثنائي الكالسيوم (DCP)": 0.01}
            if "الطيور" in main_sector: fixed_ratios["مركزات دواجن وسمان"] = 0.05  
            elif main_sector in ["الخيول والفروسية", "الماعز وسلالاته", "الأبقار وسلالاتها"]: fixed_ratios["مركزات خيول ومجترات"] = 0.025 
            elif "الأسماك" in main_sector: fixed_ratios["مسحوق أسماك (Fishmeal 60%)"] = 0.08 

            used_fixed_pct = 0.0
            for name in selected_ingredients:
                if name in fixed_ratios:
                    formula_results[name] = fixed_ratios[name] * 100; used_fixed_pct += fixed_ratios[name] * 100
            
            remaining_pct = 100.0 - used_fixed_pct
            grains_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"]]
            filler_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["المخلفات الرعوية والمواد المالئة والإضافات الفنية"] and "بيكربونات" not in x]
            protein_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"]]
            
            if not grains_ingredients: grains_ingredients = ["ذرة صفراء"]
            if not protein_ingredients: protein_ingredients = ["كسب فول صويا 44%"]
            
            p_ratio = 0.55 if final_target_cp > 30 else (0.44 if final_target_cp > 22 else (0.28 if final_target_cp > 15 else 0.16))
            
            protein_share = remaining_pct * p_ratio
            prot_priorities = [BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"].get(x, {}).get("prio_prot", 1.0) for x in protein_ingredients]
            total_prot_prio = sum(prot_priorities) if sum(prot_priorities) > 0 else 1.0
            for idx, x in enumerate(protein_ingredients): 
                share_factor = (prot_priorities[idx] / total_prot_prio) if total_prot_prio > 0 else (1.0 / len(protein_ingredients))
                formula_results[x] = protein_share * share_factor
                
            energy_share = remaining_pct * (1.0 - p_ratio)
            grain_priorities = [BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"].get(x, {}).get("priority", 1.0) for x in grains_ingredients]
            total_grain_prio = sum(grain_priorities) if sum(grain_priorities) > 0 else 1.0
            
            if grains_ingredients and filler_ingredients:
                grain_part = energy_share * 0.75; filler_part = energy_share * 0.25
                for idx, x in enumerate(grains_ingredients): 
                    grain_factor = (grain_priorities[idx] / total_grain_prio) if total_grain_prio > 0 else (1.0 / len(grains_ingredients))
                    formula_results[x] = grain_part * grain_factor
                
                fill_priorities = [BIG_FEEDS_LIBRARY["المخلفات الرعوية والمواد المالئة والإضافات الفنية"].get(x, {}).get("prio_fill", 1.0) for x in filler_ingredients]
                total_fill_prio = sum(fill_priorities) if sum(fill_priorities) > 0 else 1.0
                for idx, x in enumerate(filler_ingredients): 
                    fill_factor = (fill_priorities[idx] / total_fill_prio) if total_fill_prio > 0 else (1.0 / len(filler_ingredients))
                    formula_results[x] = filler_part * fill_factor
            else:
                for idx, x in enumerate(grains_ingredients): 
                    grain_factor = (grain_priorities[idx] / total_grain_prio) if total_grain_prio > 0 else (1.0 / len(grains_ingredients))
                    formula_results[x] = energy_share * grain_factor

            total_grains_pct = sum([formula_results.get(x, 0.0) for x in grains_ingredients])

            # =========================================================================
            # 🧪 محرك الإنزيمات التلقائية والإلزامية وموازنة البيكربونات
            # =========================================================================
            if main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاته"]:
                if total_grains_pct > 45.0 or "بيكربونات الصوديوم (الصودا)" in selected_ingredients:
                    auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.75
                    mandatory_warnings.append("🚨 <b>إضافة إلزامية - بيكربونات الصوديوم:</b> بما أن نسبة الكربوهيدرات السريعة والتخمر (الحبوب) تجاوزت 45% ({:.1f}%)، تم فرض البيكربونات أوتوماتيكياً لحماية الكرش من <b>التحمض Ruminal Acidosis</b> وكساد الهضم.".format(total_grains_pct))
            elif main_sector == "الطيور والسمان" and "بيكربونات الصوديوم (الصودا)" in selected_ingredients:
                auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.20

            if main_sector in ["الطيور والسمان", "الأسماك والأحياء المائية"]:
                auto_added_enzymes["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05
                mandatory_warnings.append("🚨 <b>إضافة إلزامية - إنزيم الفايتيز (Phytase):</b> مضاف تلقائياً، العلة هي تحرير <b>الفسفور المرتبط بحمض الفايتيك Phytic Acid</b> في النباتات الذي لا يهضمه الطير طبيعياً.")

            if "كسب بذور القطن" in formula_results and main_sector == "الطيور والسمان":
                if formula_results["كسب بذور القطن"] > 5.0:
                    auto_added_enzymes["كبريتات الحديدوز (معادل الجوسيبول)"] = 0.15 
                    mandatory_warnings.append("⚠️ <b>علة فنية معالجة برمجياً:</b> احتواء العليقة على كسب القطن للطيور بنسبة ({:.1f}%) يرفع <b>الجوسيبول الحر السام Toxic Gossypol</b>، تم ضخ كبريتات الحديدوز فورياً لإبطال مفعوله.".format(formula_results["كسب بذور القطن"]))
            
            barley_pct = formula_results.get("شعير مطحون", 0.0)
            wheat_pct = formula_results.get("قمح محلي مصنّع", 0.0)
            if main_sector == "الطيور والسمان" and (barley_pct > 10.0 or wheat_pct > 15.0):
                auto_added_enzymes["إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)"] = 0.08
                mandatory_warnings.append("⚠️ <b>علة فنية معالجة برمجياً:</b> استخدام القمح/الشعير يرفع اللزوجة المعوية (NSP)، تم دمج إنزيم مخصص لمنع عارض البراز الرطب.")

            if auto_added_enzymes:
                total_enz_pct = sum(auto_added_enzymes.values())
                major_grain = grains_ingredients[0] if grains_ingredients else "ذرة صفراء"
                if major_grain in formula_results: formula_results[major_grain] = max(1.0, formula_results[major_grain] - total_enz_pct)
                for enz_name, enz_pct in auto_added_enzymes.items(): formula_results[enz_name] = enz_pct

            st.session_state["active_formula"] = formula_results
            st.session_state["active_cp_tag"] = final_target_cp
            st.session_state["active_breed_tag"] = sub_type
            st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES.get(dynamic_img_key, ANIMAL_IMAGES_RESOURCES["عام"])
            st.session_state["active_stage_title"] = f"{main_sector} - {prod_stage}"
            
            st.success(f"🎯 تم تشغيل محرك التركيب وخوارزمية الإنزيمات الذكية بنجاح في سوق: {user_city}")
            
            if mandatory_warnings:
                st.markdown("### 🔬 تقرير فحص العلل والتدخل البرمجي بالإنزيمات:")
                for warn in mandatory_warnings: st.markdown(f'<div class="warning-card">{warn}</div>', unsafe_allow_html=True)

            res_col1, res_col2 = st.columns([0.6, 0.4])
            with res_col1:
                st.write("#### 📝 المقادير الدقيقة المعتمدة لتركيب طن واحد (كجم):")
                for k, v in formula_results.items(): st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** / طن)")
                
                ton_cost = sum([(v/100) * ingredient_prices.get(k, 300.0) if k in ingredient_prices else (v/100)*600.0 for k, v in formula_results.items()])
                st.session_state["computed_ton_cost"] = ton_cost
                st.metric(f"💰 التكلفة الفعلية لإنتاج الطن في {user_city}: ", f"${ton_cost:.2f} (أو {ton_cost*local_rate:,.1f} {local_sym})")
            with res_col2: st.bar_chart(formula_results)

# ====================================================================
# التبويبات المتقدمة للوحة تحكم المالك (Admin Only)
# ====================================================================
if st.session_state["user_role"] == "admin":
    with tabs[1]:
        st.markdown('<div class="section-title">📊 لوحة تحكم بورصة تاور المركزية الشاملة (تحديث الأسعار المباشرة)</div>', unsafe_allow_html=True)
        col_edit1, col_edit2 = st.columns(2)
        with col_edit1:
            st.subheader("🐓 بورصة الماشية والداجن")
            for animal, price in st.session_state["global_livestock_prices"].items():
                st.session_state["global_livestock_prices"][animal] = st.number_input(f"تحديث سعر: {animal}", min_value=0.0, value=float(price), step=0.1, key=f"livestock_{animal}")
        with col_edit2:
            st.subheader("🥛 بورصة الألبان واللحوم والأطباق")
            for product, price in st.session_state["global_products_prices"].items():
                st.session_state["global_products_prices"][product] = st.number_input(f"تحديث سعر: {product}", min_value=0.0, value=float(price), step=0.05, key=f"prod_edit_{product}")

    with tabs[2]:
        st.markdown('<div class="section-title">🏭 لوحة التحكم الذكية بالمخازن والمستودعات المركزية</div>', unsafe_allow_html=True)
        inv_cols = st.columns(3)
        for idx, (ing_name, qty) in enumerate(st.session_state["inventory"].items()):
            with inv_cols[idx % 3]:
                status_badge = f'<span class="stock-critical">⚠️ حرج: {qty:.2f} طن</span>' if qty < 5.0 else f'<span class="stock-normal">آمن: {qty:.2f} طن</span>'
                st.markdown(f"**{ing_name}** | {status_badge}", unsafe_allow_html=True)
                st.session_state["inventory"][ing_name] = st.number_input(f"تحديث رصيد ({ing_name}) طن:", min_value=0.0, value=float(qty), key=f"inv_input_{ing_name}")

    with tabs[3]:
        st.markdown('<div class="section-title">💰 نظام تسويق المنتجات وإصدار الفواتير مع الخصم التلقائي</div>', unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: client_name = st.text_input("اسم العميل / المزرعة المستلمة:", "مزارع الإنتاج المتكاملة")
        with col_c2: required_tons = st.number_input("الكمية المطلوبة (بالطن):", min_value=0.1, value=2.0, step=0.5)
        with col_c3: added_profit = st.number_input("هامش الربح الصافي المضاف لكل طن ($):", min_value=0.0, value=50.0)
        selling_price = st.session_state["computed_ton_cost"] + added_profit; total_bill = selling_price * required_tons
        st.markdown("### 🧾 فاتورة بيع وتوريد أعلاف رسمية")
        st.markdown(f"### 💰 إجمالي القيمة المستحقة للفاتورة: `${total_bill:.2f}` (أو تعادل `{total_bill*local_rate:,.1f}` {local_sym})")
        if st.button("✅ تأكيد عملية البيع وخصم المكونات"):
            can_deduct = True
            for name, pct in st.session_state["active_formula"].items():
                if st.session_state["inventory"].get(name, 0.0) < ((pct / 100) * required_tons): can_deduct = False; st.error(f"❌ رصيد غير كافي لـ {name}!"); break
            if can_deduct:
                for name, pct in st.session_state["active_formula"].items(): st.session_state["inventory"][name] -= ((pct / 100) * required_tons)
                st.success("🔥 تم الخصم التلقائي وتحديث المخازن!"); st.rerun()

    with tabs[4]:
        st.markdown('<div class="section-title">🌟 مُصمم ديباجات الطباعة الفنية على جوالات الأعلاف</div>', unsafe_allow_html=True)
        trade_brand = st.text_input("اسم البراند التجاري:", "مجموعة تاور لإنتاج الأعلاف ومصنعات الإنتاج الحيواني")
        st.markdown(f"""
        <div class="sack-tag">
            <img src="{st.session_state['active_animal_img']}" class="animal-banner-img">
            <h2 style="text-align: center; margin-top:0;">🌟 {trade_brand} 🌟</h2>
            <h3 style="text-align: center; color: #c62828; margin-top:0; font-weight: bold;">م. عبد القادر إسماعيل تاور</h3>
            <p style="text-align: center; font-weight: bold; background-color:#e8f5e9; padding:6px; color:#1b5e20;">🎯 علف مخصص لـ: {st.session_state['active_stage_title']} | نسبة البروتين: {st.session_state['active_cp_tag']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

# ====================================================================
# 📨 نظام الأرشفة التلقائية وإرسال الكود للإيميل بأسفل التطبيق
# ====================================================================
st.markdown("<br><hr style='border-top: 1px dashed #2e7d32;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #1565C0; text-align:right;'>📨 أرشفت الكود والتقارير الحالية للبريد الإلكتروني</h3>", unsafe_allow_html=True)

col_mail, col_btn = st.columns([0.7, 0.3])
with col_mail:
    target_email = st.text_input("أدخل البريد الإلكتروني المستلم لحفظ نسخة السورس كود الأساسية:", placeholder="example@gmail.com")

with col_btn:
    st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("إرسال نسخة الكود فوراً 🚀", use_container_width=True, type="secondary"):
        if target_email:
            with st.spinner("جاري معالجة الملف والاتصال بالخادم..."):
                if send_code_to_mail(target_email):
                    st.success(f"📥 تم إرسال السورس كود كملف مرفق (.py) بنجاح إلى: {target_email}")
        else:
            st.warning("⚠️ الرجاء كتابة البريد الإلكتروني في الحقل المخصص أولاً.")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 5. التوقيع المصغر الدائم للمطور بأسفل الشاشة
# ==========================================
st.markdown(
    """
    <div class="mini-left-signature">
        👨‍🔬 م. عبد القادر إسماعيل تاور © 2026 | خبير الحلول الذكية للثروة الحيوانية والبرمجيات المتكاملة
    </div>
    """,
    unsafe_allow_html=True
)
