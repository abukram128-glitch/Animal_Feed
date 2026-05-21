import streamlit as st
import numpy as np
import json
import os
import base64
import smtplib
import time
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

# 🔒 إعدادات خادم البريد الإلكتروني المرجعية المحدثة بالرمز الجديد
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"       
SENDER_PASSWORD = "oynz rdli tsdy ekdq"     

def get_image_base64(paths):
    for path in paths:
        if os.path.exists(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    return None

img_base64 = get_image_base64(PHOTO_OPTIONS)

def send_code_to_mail(receiver_email):
    if SENDER_EMAIL == "YOUR_EMAIL@gmail.com":
        st.error("⚠️ خطأ إعدادات: يرجى تحديث بيانات الـ SMTP داخل السورس كود أولاً.")
        return False
        
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود الكامل والمعدل - منصة تاور الذكية للأعلاف"
    
    body = "السلام عليكم م. عبد القادر،\n\nمرفق مع هذه الرسالة النسخة البرمجية الشاملة والمحدثة بالكامل لمنصة تاور الذكية لعام 2026 بعد معالجة ازدواجية الصويا وتخصيص السلالات جغرافياً وضبط نظام الإنزيمات التلقائي.\n\nتحياتي،\nالنظام التلقائي للمنصة."
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        code_content = ""
        current_file = None
        try: current_file = __file__
        except NameError: pass
            
        if current_file and os.path.exists(current_file):
            with open(current_file, "r", encoding="utf-8") as f: code_content = f.read()
        elif os.path.exists("app.py"): 
            with open("app.py", "r", encoding="utf-8") as f: code_content = f.read()
        else:
            code_content = "# تعذر قراءة الملف برمجياً، يرجى مراجعة المطور عبد القادر تاور."

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

# ==========================================
# 3. الهياكل والبيانات الجغرافية المفلترة
# ==========================================
if "inventory" not in st.session_state:
    st.session_state["inventory"] = {
        "ذرة صفراء": 25.0, "ذرة بيضاء": 10.0, "شعير مطحون": 15.0, "سورجم (فتريتة)": 15.0, "قمح محلي مصنّع": 12.0,
        "أمباز الفول السوداني (كسب)": 20.0, "كسب فول صويا": 25.0, "كسب عباد الشمس 36%": 10.0, "كسب بذور القطن": 8.0,
        "نخالة قمح (ردة)": 20.0, "البرسيم الجاف (الدريس)": 30.0, "مولاس": 5.0,
        "مسحوق أسماك (Fishmeal 60%)": 4.0, "مركزات دواجن وسمان": 3.5, "مركزات خيول ومجترات": 3.5,
        "الحجر الجيري (بودرة بلاط)": 6.0, "فوسفات ثنائي الكالسيوم (DCP)": 3.0, "ملح الطعام": 2.5, "مضاد سموم فطرية": 1.2,
        "بيكربونات الصوديوم (الصودا)": 5.0
    }

# مصفوفة فلترة البورصة الجغرافية حسب الدولة المحددة منعا للخلط الحلقي
GEOGRAPHIC_DATA = {
    "ليبيا": {
        "livestock": {"عجول هجين ومحسن أسواق الشرق ($)": 1400.0, "ضأن برقاوي أصيل ($)": 220.0, "ماعز صحراوي محلي ($)": 140.0, "خيول هجين ورياضية ($)": 4800.0, "كتكوت لاحم ($)": 0.70},
        "products": {"كيلو لحم ضأن طازج ($)": 9.50, "كيلو لحم بقري صافي ($)": 8.00, "لتر حليب طازج ($)": 1.10, "طبق بيض مائدة ($)": 4.50},
        "breeds": {"الخيول والفروسية": ["خيل عربي أصيل", "خيول ليبية هجين"], "الماعز وسلالاته": ["الماعز الصحراوي", "ماعز برقاوي"], "الأبقار وسلالاتها": ["أبقار فريزيان هجين", "أبقار محلي"], "الطيور والسمان": ["دواجن لاحم (بني غازي)", "دواجن بياض", "طائر السمان"], "الأسماك والأحياء المائية": ["البلطي", "القاروص"]}
    },
    "السودان": {
        "livestock": {"عجول تسمين هولشتاين ومحسن ($)": 1250.0, "أبقار كنانة وبطانة محلي ($)": 850.0, "ضأن حمري وشكري ($)": 170.0, "ماعز نوبي سوداني ($)": 120.0, "كتكوت عمر يوم ($)": 0.60},
        "products": {"كيلو لحم عجالي صافي ($)": 7.00, "كيلو لحم ضأن طازج ($)": 8.50, "رطل حليب خام ($)": 0.80, "كيلو جبن أبيض محلي ($)": 4.80},
        "breeds": {"الخيول والفروسية": ["خيل عربي أصيل", "خيول دنقلاوية هجين"], "الماعز وسلالاته": ["الماعز النوبي السوداني", "الماعز الصحراوي السوداني"], "الأبقار وسلالاتها": ["كنانة (سوداني)", "بطانة (مدر)"], "الطيور والسمان": ["دواجن لاحم (مزارع الخرطوم)", "دواجن بياض انتاجي", "طائر السمان المستانس"], "الأسماك والأحياء المائية": ["البلطي النيلي (Tilapia)", "القرموط"]}
    },
    "مصر": {
        "livestock": {"عجول بقري خليط ($)": 1300.0, "أبقار فريزيان ومحسن ($)": 1100.0, "ضأن بلدي وأوسيمي ($)": 190.0, "ماعز زرايبي وبور ($)": 150.0, "كتكوت لاحم عمر يوم ($)": 0.65},
        "products": {"كيلو لحم بقري طازج ($)": 7.80, "كيلو لحم ضأن ($)": 9.20, "كيلو حليب جاموسي خام ($)": 0.95, "طبق بيض مائدة 30 بيضة ($)": 4.10},
        "breeds": {"الخيول والفروسية": ["خيل عربي أصيل محطّات", "خيول بلدي هجين"], "الماعز وسلالاته": ["ماعز زرايبي مصري", "بور محسن"], "الأبقار وسلالاتها": ["أبقار خليط بلدي", "جاموس مصري مدر"], "الطيور والسمان": ["دواجن لاحم", "دواجن بياض أرخص", "طائر السمان الياباني"], "الأسماك والأحياء المائية": ["البلطي النيلي", "البوري"]}
    },
    "باقي دول العالم / البورصة المفتوحة": {
        "livestock": {"عجول تسمين عالمية ($)": 1350.0, "أبقار حلوب هولشتاين ($)": 1200.0, "ضأن وستيرلنغ ($)": 180.0, "ماعز محسن عالمي ($)": 130.0, "كتكوت لاحم قياسي ($)": 0.65},
        "products": {"كيلو لحم صافي قياسي ($)": 7.50, "كيلو لحم ضأن طازج ($)": 9.00, "لتر حليب مصنع ($)": 0.90, "طبق بيض مائدة مبرد ($)": 4.20},
        "breeds": {"الخيول والفروسية": ["خيل عربي أصيل", "ثوروبريد"], "الماعز وسلالاته": ["بور محسن عالمي", "سانين السويسرية"], "الأبقار وسلالاتها": ["هولشتاين بيور", "براون سويس"], "الطيور والسمان": ["دواجن لاحم قياسي", "دواجن بياض تجاري", "طائر السمان الدولي"], "الأسماك والأحياء المائية": ["البلطي العالمي", "السلمون"]}
    }
}

EXCHANGE_RATES = {"السودان": {"rate": 600.0, "sym": "SDG"}, "ليبيا": {"rate": 4.80, "sym": "LYD"}, "مصر": {"rate": 48.0, "sym": "EGP"}, "باقي دول العالم / البورصة المفتوحة": {"rate": 1.0, "sym": "USD"}}

def get_adjusted_market_data(country, state_or_region, city):
    feed_prices = {
        "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0, "سورجم (فتريتة)": 195.0, "قمح محلي مصنّع": 240.0,
        "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا": 450.0, "كسب عباد الشمس 36%": 310.0, "كسب بذور القطن": 290.0,
        "نخالة قمح (ردة)": 150.0, "البرسيم الجاف (الدريس)": 170.0, "مولاس": 120.0,
        "مسحوق أسماك (Fishmeal 60%)": 850.0, "مركزات دواجن وسمان": 650.0, "مركزات خيول ومجترات": 600.0,
        "الحجر الجيري (بودرة بلاط)": 40.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0, "ملح الطعام": 30.0, "مضاد سموم فطرية": 950.0,
        "بيكربونات الصوديوم (الصودا)": 340.0
    }
    multiplier = 1.0
    if country == "السودان":
        multiplier = 1.15
        if "كردفان" in state_or_region or state_or_region == "إقليم النيل الأزرق":
            multiplier = 1.20; feed_prices["سورجم (فتريتة)"] *= 0.85; feed_prices["أمباز الفول السوداني (كسب)"] *= 0.85
    elif country == "ليبيا":
        multiplier = 1.10
        if city == "طبرق": multiplier = 1.06
    elif country == "مصر": multiplier = 1.04

    for k in feed_prices: feed_prices[k] *= multiplier
    return feed_prices

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
        "كسب فول صويا": {"CP": 44.0, "prio_prot": 1.2}, # سيتم تعديل الـ CP ديناميكياً حسب اختيار الـ 44 أو 48
        "كسب عباد الشمس 36%": {"CP": 36.0, "prio_prot": 0.85},
        "كسب بذور القطن": {"CP": 41.0, "prio_prot": 0.8}
    },
    "المخلفات الرعوية والمواد المالئة والإضافات الفنية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "prio_fill": 1.2}, 
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "prio_fill": 0.9}, 
        "مولاس": {"CP": 4.0, "prio_fill": 1.0}
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
    "الأبقار وسلالاتها": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600&auto=format&fit=crop",
    "الماعز وسلالاته": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600&auto=format&fit=crop",
    "الخيول والفروسية": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600&auto=format&fit=crop",
    "الطيور والسمان": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600&auto=format&fit=crop",
    "الأسماك والأحياء المائية": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600&auto=format&fit=crop",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop"
}

if "active_formula" not in st.session_state: st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا": 35.0}
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
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.2rem; margin-top:5px; margin-bottom:0;'>نسخة محدثة بالكامل: الفلترة الجغرافية الدقيقة ومحرك فحص العلل والإنزيمات الذكي</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

if st.session_state["user_role"] == "admin":
    tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى", "📊 بورصة تاور المركزية للمنتجات والماشية", "🏭 إدارة المستودعات والخصم التلقائي", "🧾 التسويق وفواتير حركة البيع", "🖨️ مصمم بطاقات الديباجة والدعاية"]
else:
    tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى"]

tabs = st.tabs(tabs_titles)

with tabs[0]:
    st.markdown('<div class="section-title">🌍 أولاً: تحديد الموقع الجغرافي وبورصة الأسعار المفلترة جغرافيّاً</div>', unsafe_allow_html=True)
    col_country, col_state, col_city = st.columns(3)
    with col_country: user_country = st.selectbox("اختر دولة المربي للتخصيص الجغرافي:", ["ليبيا", "السودان", "مصر", "باقي دول العالم / البورصة المفتوحة"])
        
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    local_rate = c_info["rate"]; local_sym = c_info["sym"]

    chosen_state = "عام"
    with col_state:
        if user_country == "السودان":
            chosen_state = st.selectbox("اختر الولاية السودانية المحدثة:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال كردفان", "ولاية جنوب كردفان", "إقليم النيل الأزرق", "ولاية البحر الأحمر"])
        elif user_country == "ليبيا": chosen_state = st.selectbox("اختر الإقليم الجغرافي اللّيبي:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
        else: chosen_state = st.selectbox("الإقليم الإداري:", ["المركز الرئيسي العالمي", "الأسواق المفتوحة"])

    with col_city:
        if user_country == "السودان":
            if chosen_state == "ولاية الخرطوم": user_city = st.selectbox("اختر المدينة:", ["الخرطوم", "أم درمان", "بحري"])
            elif chosen_state == "ولاية الجزيرة": user_city = st.selectbox("اختر المدينة:", ["ود مدني", "المناقل"])
            elif chosen_state == "ولاية شمال كردفان": user_city = st.selectbox("اختر المدينة:", ["الأبيض", "بارا"])
            else: user_city = st.selectbox("اختر المدينة:", ["بورتسودان", "الدمازين", "القضارف"])
        elif user_country == "ليبيا":
            if chosen_state == "المنطقة الشرقية": user_city = st.selectbox("اختر المدينة الليبية:", ["طبرق", "بنغازي", "البيضاء", "درنة"])
            elif chosen_state == "المنطقة الغربية": user_city = st.selectbox("اختر المدينة الليبية:", ["طرابلس", "مصراتة", "الزاوية"])
            else: user_city = st.selectbox("اختر المدينة الليبية:", ["سبها", "مرزق"])
        else: user_city = st.text_input("اكتب اسم المدينة العالمية يدوياً:", "طبرق")

    # جلب بيانات البورصة المفلترة كلياً بناءً على الدولة لمنع ظهور أبقار كنانة مثلاً في ليبيا
    country_data = GEOGRAPHIC_DATA[user_country]
    live_prices = get_adjusted_market_data(user_country, chosen_state, user_city)
    
    col_view1, col_view2 = st.columns(2)
    with col_view1:
        st.markdown(f'<div class="price-card"><b>📈 بورصة الماشية والداجن الحية المخصصة لسوق ({user_country} - {user_city}):</b><br>' + 
                    "<br>".join([f"▪️ {k}: <b>${v:.2f}</b> (يعادل: <span style='color:#e65100; font-weight:bold;'>{v*local_rate:,.2f} {local_sym}</span>)" for k, v in country_data["livestock"].items()]) + "</div>", unsafe_allow_html=True)
    with col_view2:
        st.markdown(f'<div class="price-card"><b>🥩 بورصة المنتجات الحيوانية والألبان المحلية في ({user_city}):</b><br>' + 
                    "<br>".join([f"▪️ {k}: <b>${v:.2f}</b> (يعادل: <span style='color:#1b5e20; font-weight:bold;'>{v*local_rate:,.2f} {local_sym}</span>)" for k, v in country_data["products"].items()]) + "</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">📐 ثانياً: شريط القياس الجسدي وتقدير الأوزان أولاً</div>', unsafe_allow_html=True)
    col_sec_main = st.selectbox("اختر القطاع الإنتاجي المستهدف أولاً لتحديد نمط الحساب:", ["الأبقار وسلالاتها", "الماعز وسلالاته", "الخيول والفروسية", "الطيور والسمان", "الأسماك والأحياء المائية"])
    
    show_measurements = col_sec_main in ["الأبقار وسلالاتها", "الماعز وسلالاته", "الخيول والفروسية"]
    weight_factor = 10000; feed_factor = 0.025
    if col_sec_main == "الخيول والفروسية": weight_factor = 11877; feed_factor = 0.022
    elif col_sec_main == "الماعز وسلالاته": weight_factor = 11250; feed_factor = 0.028
    elif col_sec_main == "الأبقار وسلالاتها": weight_factor = 10838; feed_factor = 0.025

    if show_measurements:
        col_h, col_l, col_ag = st.columns(3)
        with col_h: h_girth = st.number_input("📏 قياس محيط الصدر للحيوان (سم):", value=150.0 if col_sec_main != "الماعز وسلالاته" else 70.0)
        with col_l: b_length = st.number_input("📏 طول الجسم التقديـري (سم):", value=130.0 if col_sec_main != "الماعز وسلالاته" else 60.0)
        with col_ag: a_months = st.number_input("⏳ عمر الحيوان الحالي (أشهر):", value=12)
        calc_weight = (h_girth ** 2 * b_length) / weight_factor; req_feed_kg = calc_weight * feed_factor
        st.success(f"📊 الوزن التقديري المعتمد: **{calc_weight:.1f} كجم** | الاحتياج الموصى به من المادة الجافة: **{req_feed_kg:.2f} كجم / يومياً**")
    else:
        st.info(f"💡 نظام الأتمتة: تم تحييد شريط القياس الجسدي تلقائياً لأن قطاع (الطيور/الأسماك) يعتمد بروتوكول وزن القطيع الإجمالي.")

    st.markdown('<div class="section-title">📋 ثالثاً: قائمة اختيار السلالة ونوع الإنتاج (مفلترة جغرافيّاً بعد القياس)</div>', unsafe_allow_html=True)
    col_sub, col_prod = st.columns(2)
    
    # فلترة السلالات المتاحة بناء على الدولة المحددة بالأعلى لمنع التداخل حَقلياً
    available_breeds = country_data["breeds"].get(col_sec_main, ["سلالة عامة"])
    with col_sub: sub_type = st.selectbox("اختر السلالة المتوفرة محلياً بموقعك:", available_breeds)
    
    default_cp = 14.0
    chosen_concentrate = "مركزات خيول ومجترات" if col_sec_main in ["الأبقار وسلالاتها", "الماعز وسلالاته", "الخيول والفروسية"] else ("مركزات دواجن وسمان" if col_sec_main == "الطيور والسمان" else "مسحوق أسماك (Fishmeal 60%)")
    
    with col_prod:
        if col_sec_main == "الخيول والفروسية":
            prod_stage = st.selectbox("نوع الإنتاج المستهدف:", ["خيول نشاط مكثف وركض", "أمهار نامية صغيرة", "فرسات مرضعات"]); default_cp = 16.0 if "أمهار" in prod_stage or "مرضعات" in prod_stage else 12.0
        elif col_sec_main == "الماعز وسلالاته":
            prod_stage = st.selectbox("نوع الإنتاج المستهدف:", ["تسمين وتيوس لحم مكثف", "إنتاج حليب وإدرار"]); default_cp = 15.5 if "حليب" in prod_stage else 13.5
        elif col_sec_main == "الأبقار وسلالاتها":
            prod_stage = st.selectbox("نوع الإنتاج المستهدف:", ["إنتاج حليب وغزارة إدرار", "تسمين عجول مكثف"]); default_cp = 16.0 if "حليب" in prod_stage else 13.0
        elif col_sec_main == "الطيور والسمان":
            if "السمان" in sub_type or "سمان" in prod_stage:
                prod_stage = st.selectbox("نوع الإنتاج المستهدف:", ["سمان بادي / نامي", "سمان بياض إنتاجي"]); default_cp = 24.0 if "بادي" in prod_stage else 20.0
            else:
                prod_stage = st.selectbox("نوع الإنتاج المستهدف:", ["بادي دواجن 23%", "نامي دواجن 21%", "ناهي دواجن 19%", "بياض مائدة"]); default_cp = 23.0 if "بادي" in prod_stage else (21.0 if "نامي" in prod_stage else (19.0 if "ناهي" in prod_stage else 17.5))
        else:
            prod_stage = st.selectbox("نوع الإنتاج المستهدف:", ["بادئ زريعة عالي بروتين", "نمو وتسمين أسماك نيلية"]); default_cp = 35.0 if "زريعة" in prod_stage else 30.0

    override_cp = st.checkbox("⚙️ تفعيل التعديل الفني اليدوي لنسبة البروتين المستهدفة")
    final_target_cp = st.slider("حدّد نسبة البروتين المستهدفة فنيّاً:", 10.0, max_value=45.0, value=default_cp) if override_cp else default_cp

    st.markdown('<div class="section-title">🌾 رابعاً: اختيار مكونات العليقة الذكي (حل مشكلة تكرار الصويا)</div>', unsafe_allow_html=True)
    selected_ingredients = []; ingredient_prices = {}
    
    # تفريغ المكونات مع معالجة الصويا كصنف مدمج مرن
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=True):
            sub_cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with sub_cols[idx % 3]:
                    is_def = True if ing_name == chosen_concentrate or "ذرة صفراء" in ing_name or "صويا" in ing_name or "ملح" in ing_name else False
                    checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}_{cat_name}")
                    
                    # معالجة الصويا داخلياً كعنصر واحد بنسب مختلفة تمنع التكرار الجلي بالتحليل
                    if ing_name == "كسب فول صويا" and checked:
                        soya_type = st.radio("حدد تركيز بروتين الصويا المطلوب للخلطة الحالية:", ["44%", "48%"], horizontal=True, key="soya_ratio_select")
                        soya_cp = 44.0 if soya_type == "44%" else 48.0
                        BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"]["كسب فول صويا"]["CP"] = soya_cp
                    
                    current_live_price = live_prices.get(ing_name, 350.0)
                    if st.session_state["user_role"] == "admin": 
                        price_input = st.number_input(f"سعر طن ({ing_name}) $:", min_value=10.0, value=float(current_live_price), key=f"price_{ing_name}_{cat_name}")
                    else:
                        st.markdown(f"💰 السعر الحالي بموقعك: **`${current_live_price:.2f}`** / طن")
                        price_input = current_live_price
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price_input

    st.markdown("---")
    if st.button("🚀 تشغيل محرك التركيب الذكي ونظام فرز العلل الفنية بالإنزيمات", type="primary", use_container_width=True):
        if len(selected_ingredients) < 2: 
            st.error("⚠️ يرجى تحديد خامات علفية كافية لبناء التوليفة الاقتصادية.")
        else:
            formula_results = {}
            mandatory_warnings = []
            
            # نسب ثابتة وقائية للخلطة
            fixed_ratios = {"ملح الطعام": 0.005, "مضاد سموم فطرية": 0.002, "الحجر الجيري (بودرة بلاط)": 0.025 if "بياض" in prod_stage else 0.015, "فوسفات ثنائي الكالسيوم (DCP)": 0.01}
            if col_sec_main == "الطيور والسمان": fixed_ratios["مركزات دواجن وسمان"] = 0.05  
            elif col_sec_main in ["الأبقار وسلالاتها", "الماعز وسلالاته", "الخيول والفروسية"]: fixed_ratios["مركزات خيول ومجترات"] = 0.025 
            elif col_sec_main == "الأسماك والأحياء المائية": fixed_ratios["مسحوق أسماك (Fishmeal 60%)"] = 0.08 

            used_fixed_pct = 0.0
            for name in selected_ingredients:
                if name in fixed_ratios:
                    formula_results[name] = fixed_ratios[name] * 100; used_fixed_pct += fixed_ratios[name] * 100
            
            remaining_pct = 100.0 - used_fixed_pct
            grains_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"]]
            filler_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["المخلفات الرعوية والمواد المالئة والإضافات الفنية"]]
            protein_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"]]
            
            if not grains_ingredients: grains_ingredients = ["ذرة صفراء"]
            if not protein_ingredients: protein_ingredients = ["كسب فول صويا"]
            
            p_ratio = 0.50 if final_target_cp > 25 else (0.35 if final_target_cp > 18 else 0.20)
            
            protein_share = remaining_pct * p_ratio
            for x in protein_ingredients: formula_results[x] = protein_share / len(protein_ingredients)
                
            energy_share = remaining_pct * (1.0 - p_ratio)
            combined_energy_sources = grains_ingredients + filler_ingredients
            for x in combined_energy_sources: formula_results[x] = energy_share / len(combined_energy_sources)

            total_grains_pct = sum([formula_results.get(x, 0.0) for x in grains_ingredients])

            # =========================================================================
            # 🧪 ملف مصفوفة الإنزيمات الأساسية الشامل مع الإشعار المؤقت (30 ثانية)
            # =========================================================================
            enzymes_to_inject = {}

            # علة 1: تحمض الكرش في المجترات لارتفاع الحبوب عن 45%
            if col_sec_main in ["الأبقار وسلالاتها", "الماعز وسلالاته"] and total_grains_pct > 45.0:
                enzymes_to_inject["بيكربونات الصوديوم (معادل حموضة الكرش)"] = 0.80
                msg_body = "🚨 تنبيه فني (حموضة الكرش): تجاوزت نسبة الكربوهيدرات السريعة التخمر 45%، تم فرض صمام أمان البيكربونات لمنع اللقحة والتحمض الحاد بالكرش."
                st.toast(msg_body, icon="⚠️")
                mandatory_warnings.append(msg_body)

            # علة 2: فك ارتباط الفسفور للنباتات في الدواجن والأسماك
            if col_sec_main in ["الطيور والسمان", "الأسماك والأحياء المائية"]:
                enzymes_to_inject["إنزيم الفايتيز (Phytase Alpha)"] = 0.05
                msg_body = "🔬 تنبيه فني (إنزيم الفايتيز): تم دمج الفايتيز إلزامياً لتحرير الفسفور العضوي المرتبط بحمض الفايتيك بالنبات وتحسين الاستفادة الهضمية للطير."
                st.toast(msg_body, icon="🧬")
                mandatory_warnings.append(msg_body)

            # علة 3: سمية الجوسيبول الحر لزيادة كسب القطن للطيور عن 5%
            cotton_pct = formula_results.get("كسب بذور القطن", 0.0)
            if cotton_pct > 5.0 and col_sec_main == "الطيور والسمان":
                enzymes_to_inject["كبريتات الحديدوز (معادل الجوسيبول السام)"] = 0.15
                msg_body = f"⚠️ تنبيه علة الجوسيبول: احتوية العليقة على كسب القطن بنسبة ({cotton_pct:.1f}%) وهو ما يشكل خطراً ساماً على الطيور، تم ضخ كبريتات الحديدوز لإبطال مفعوله كيميائياً."
                st.toast(msg_body, icon="🛑")
                mandatory_warnings.append(msg_body)

            # علة 4: لزوجة الأمعاء (NSP) بسبب الشعير والقمح في خلطات الطيور
            barley_wheat_pct = formula_results.get("شعير مطحون", 0.0) + formula_results.get("قمح محلي مصنّع", 0.0)
            if barley_wheat_pct > 12.0 and col_sec_main == "الطيور والسمان":
                enzymes_to_inject["مجمع إنزيمات NSP (زيلاناز + جلوكاناز)"] = 0.08
                msg_body = "🌾 تنبيه لزوجة الأمعاء: استخدام الشعير/القمح يرفع السكريات غير النشوية المعقدة المسببة للبراز الرطب، تم دمج إنزيمات كسر اللزوجة المعوية فورا."
                st.toast(msg_body, icon="🧬")
                mandatory_warnings.append(msg_body)

            # تطبيق حقن الإنزيمات الفنية بخصمها من الكتلة الكبرى (الذرة أو الحبوب المتوفرة) ليبقى المجموع 100%
            if enzymes_to_inject:
                total_enz_pct = sum(enzymes_to_inject.values())
                major_grain = grains_ingredients[0] if grains_ingredients else "ذرة صفراء"
                if major_grain in formula_results: 
                    formula_results[major_grain] = max(1.0, formula_results[major_grain] - total_enz_pct)
                for enz_name, enz_pct in enzymes_to_inject.items(): 
                    formula_results[enz_name] = enz_pct

            # حفظ التحديثات في الكاش الداخلي للتطبيق
            st.session_state["active_formula"] = formula_results
            st.session_state["active_cp_tag"] = final_target_cp
            st.session_state["active_breed_tag"] = sub_type
            st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES.get(col_sec_main, ANIMAL_IMAGES_RESOURCES["عام"])
            st.session_state["active_stage_title"] = f"{col_sec_main} - {prod_stage}"
            
            st.success(f"🎯 تم الحساب الدقيق واستهداف سوق: {user_city} بنجاح كلي.")
            
            if mandatory_warnings:
                st.markdown("### 🔬 سجل الفحص الفني للعلل والإنزيمات النشطة بتركيبتك الحالية (ستظل الإشعارات نشطة بوضوح):")
                for warn in mandatory_warnings: 
                    st.markdown(f'<div class="warning-card">{warn}</div>', unsafe_allow_html=True)

            res_col1, res_col2 = st.columns([0.6, 0.4])
            with res_col1:
                st.write("#### 📝 قائمة المكونات المعتمدة النهائية شاملة الإنزيمات المعالجة (لكل 1 طن):")
                for k, v in formula_results.items(): 
                    st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** / طن واحد)")
                
                ton_cost = sum([(v/100) * ingredient_prices.get(k, 300.0) if k in ingredient_prices else (v/100)*400.0 for k, v in formula_results.items()])
                st.session_state["computed_ton_cost"] = ton_cost
                st.metric(f"💰 تكلفة إنتاج الطن المتزنة في {user_city}: ", f"${ton_cost:.2f} (يعادل تقريباً {ton_cost*local_rate:,.1f} {local_sym})")
            with res_col2: 
                st.bar_chart(formula_results)

# ====================================================================
# لوحات تحكم المالك الحصرية (Admin Tabs Only)
# ====================================================================
if st.session_state["user_role"] == "admin":
    with tabs[1]:
        st.markdown('<div class="section-title">📊 إدارة تحديث أسعار بورصات الدول والماشية الحية</div>', unsafe_allow_html=True)
        edit_country = st.selectbox("اختر الدولة المراد تحديث بورصتها فورياً:", ["ليبيا", "السودان", "مصر", "باقي دول العالم / البورصة المفتوحة"])
        col_ed1, col_ed2 = st.columns(2)
        with col_ed1:
            st.subheader("🐓 تحديث أسعار الماشية والداجن ($)")
            for animal, price in GEOGRAPHIC_DATA[edit_country]["livestock"].items():
                GEOGRAPHIC_DATA[edit_country]["livestock"][animal] = st.number_input(f"تعديل سعر: {animal}", min_value=0.0, value=float(price), key=f"adm_live_{animal}_{edit_country}")
        with col_ed2:
            st.subheader("🥛 تحديث أسعار اللحوم والألبان ($)")
            for product, price in GEOGRAPHIC_DATA[edit_country]["products"].items():
                GEOGRAPHIC_DATA[edit_country]["products"][product] = st.number_input(f"تعديل سعر: {product}", min_value=0.0, value=float(price), key=f"adm_prod_{product}_{edit_country}")

    with tabs[2]:
        st.markdown('<div class="section-title">🏭 التحكم بأرصدة المخازن والصوامع المركزية</div>', unsafe_allow_html=True)
        inv_cols = st.columns(3)
        for idx, (ing_name, qty) in enumerate(st.session_state["inventory"].items()):
            with inv_cols[idx % 3]:
                status_badge = f'<span style="color:red;font-weight:bold;">⚠️ مخزون حرج: {qty:.2f} طن</span>' if qty < 5.0 else f'<span style="color:green;">آمن: {qty:.2f} طن</span>'
                st.markdown(f"**{ing_name}** | {status_badge}", unsafe_allow_html=True)
                st.session_state["inventory"][ing_name] = st.number_input(f"تعديل كمية ({ing_name}) طن:", min_value=0.0, value=float(qty), key=f"inv_input_mod_{ing_name}")

    with tabs[3]:
        st.markdown('<div class="section-title">💰 حركات البيع وإص
