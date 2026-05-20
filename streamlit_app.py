import streamlit as st
import numpy as np
import json
import os
import base64
import time
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================
# 1. إعدادات المنصة الرسمية والمظهر الفخم
# ==========================================
st.set_page_config(page_title="منصة تاور الذكية المتكاملة للأعلاف والإنتاج الحيواني", page_icon="🌾", layout="wide")

# بيانات التحكم والوصول والأمان المحدثة
USER_ADMIN = "تاور"       
PASS_ADMIN = "202687"     

USER_GUEST = "مربي"       
PASS_GUEST = "2026"       

USER_EXPERT = "مختص"      
PASS_EXPERT = "2020"      

# إعدادات الربط المباشر بـ Gmail المهندس عبد القادر تاور
GMAIL_USER = "your_email@gmail.com"     # ضع إيميلك هنا
GMAIL_PASS = "xxxx xxxx xxxx xxxx"       # ضع كود App Password السري هنا ليعمل الإرسال
RECEIVER_EMAIL = "your_email@gmail.com"    # البريد المستقبل للإشعارات والملاحظات

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

def get_image_base64(paths):
    for path in paths:
        try:
            if os.path.exists(path):
                with open(path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode()
        except Exception:
            continue
    return None

img_base64 = get_image_base64(PHOTO_OPTIONS)

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
        max-height: 280px;
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
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. محرّك الربط التلقائي وإرسال الإيميلات
# ==========================================
def send_email_notification(subject, body_content):
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body_content, 'plain', 'utf-8'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        return True
    except Exception:
        return False

# بنك الأسئلة لضمان التحقق الأكاديمي من المختصين
VET_QUESTIONS = [
    {"q": "ما هو المسبب لمرض جومبورو (Gumboro) الحاد بالدواجن؟", "ans": "فيروس", "options": ["فيروس", "بكتيريا", "طفيليات"]},
    {"q": "تستخدم بكتيريا Pasteurella multocida كمسبب رئيسي لمرض:", "ans": "التسمم الدموي", "options": ["التسمم الدموي", "البروسيلوز", "السل"]},
    {"q": "التحمض الحاد الكرش (Acidosis) يحدث أساساً نتيجة التغذية المفرطة على:", "ans": "الحبوب والكربوهيدرات", "options": ["الحبوب والكربوهيدرات", "البرسيم الجاف", "اليوريا"]}
]

ANIMAL_PROD_QUESTIONS = [
    {"q": "كم تبلغ نسبة البروتين الخام القياسية بكسب فول الصويا عالي الجودة؟", "ans": "48%", "options": ["44%", "48%", "21%"]},
    {"q": "أي الخامات التالية يعتبر المكون الطاقوي الأبرز لعليقة الدواجن؟", "ans": "الذرة الصفراء", "options": ["الذرة الصفراء", "نخالة القمح", "الملح"]},
    {"q": "لتقليل لزوجة الأمعاء عند التغذية على نسب عالية من الشعير والقمح نستخدم إنزيم:", "ans": "NSP (زيلاناز)", "options": ["NSP (زيلاناز)", "الفايتيز", "الليبيز"]}
]

if "expert_comments_log" not in st.session_state:
    st.session_state["expert_comments_log"] = []

# ==========================================
# 3. بوابة الدخول الثلاثية الذكية
# ==========================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "sub_role" not in st.session_state: st.session_state["sub_role"] = None

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 520px; margin: 80px auto; direction: rtl;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة الثلاثية</h2>", unsafe_allow_html=True)
    
    input_user = st.selectbox("👤 نوع الحساب والاسم:", ["مربي", "طبيب بيطري أو مختص انتاج حيواني", "تاور"])
    input_pass = st.text_input("🔑 كود الدخول السري:", type="password")
    
    if "selected_q_vet" not in st.session_state:
        st.session_state["selected_q_vet"] = random.sample(VET_QUESTIONS, 3)
        st.session_state["selected_q_prod"] = random.sample(ANIMAL_PROD_QUESTIONS, 3)

    if input_user == "طبيب بيطري أو مختص انتاج حيواني" and input_pass == PASS_EXPERT:
        st.markdown("<hr style='border-top: 1px dashed #2e7d32;'>", unsafe_allow_html=True)
        st.warning("🔬 اختبار الأهلية العلمي الإلزامي لتأكيد الصفة التخصصية:")
        chosen_spec = st.radio("حدد تخصصك المهني بدقة:", ["طبيب بيطري", "مختص انتاج حيواني"], horizontal=True)
        
        user_answers = []
        pool = st.session_state["selected_q_vet"] if chosen_spec == "طبيب بيطري" else st.session_state["selected_q_prod"]
        for i, q_item in enumerate(pool):
            ans = st.radio(f"❓ {q_item['q']}", q_item['options'], key=f"login_q_{i}")
            user_answers.append(ans)

    if st.button("ولوج المنظومة العلفية 🔓", type="primary", use_container_width=True):
        if input_user == "تاور" and input_pass == PASS_ADMIN:
            st.session_state["approved"] = True
            st.session_state["user_role"] = "admin"
            st.rerun()
        elif input_user == "مربي" and input_pass == PASS_GUEST:
            st.session_state["approved"] = True
            st.session_state["user_role"] = "guest"
            st.rerun()
        elif input_user == "طبيب بيطري أو مختص انتاج حيواني" and input_pass == PASS_EXPERT:
            is_correct = True
            for i, q_item in enumerate(pool):
                if user_answers[i] != q_item['ans']: is_correct = False
            if is_correct:
                st.session_state["approved"] = True
                st.session_state["user_role"] = "expert"
                st.session_state["sub_role"] = chosen_spec
                st.rerun()
            else:
                st.error("❌ الإجابات العلمية غير مطابقة لتخصصك. تم رفض الدخول لحماية الملكية الفكرية.")
        else:
            st.error("❌ بيانات الاعتماد أو كود الدخول المدخل غير صحيح.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# 4. بنية البيانات الكاملة وبورصة الماشية والمستودعات الثابتة بالبرنامج
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
        "عجول تسمين هولشتاين / محسن ($)": 1350.0, "أبقار كنانة وبطانة محلية ($)": 900.0,
        "ضأن وستيرلنغ / محلي ($)": 180.0, "ماعز نوبي وصحراوي ($)": 130.0,
        "خيول عربية أصيلة وهجين ($)": 4500.0, "كتكوت لاحم عمر يوم ($)": 0.65, "دجاج بياض عمر البشاير ($)": 5.50
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
            feed_prices["سورجم (فتريتة)"] *= 0.85
            feed_prices["أمباز الفول السوداني (كسب)"] *= 0.85
    elif country == "ليبيا" and city == "طبرق": multiplier = 1.06
    for k in feed_prices: feed_prices[k] *= multiplier
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
    "المخلفات الرعوية والمواد المالئة والإضافات الفنية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "prio_fill": 1.2}, "البرسيم الجاف (الدريس)": {"CP": 16.5, "prio_fill": 0.9}, 
        "مولاس": {"CP": 4.0, "prio_fill": 1.0}, "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "prio_fill": 0.5}
    },
    "الإضافات المتخصصة والمركزات دقيقة الخلط": {
        "مركزات دواجن وسمان": {"CP": 40.0}, "مركزات خيول ومجترات": {"CP": 36.0}, "الحجر الجيري (بودرة بلاط)": {"CP": 0.0}, "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0}, "ملح الطعام": {"CP": 0.0}, "مضاد سموم فطرية": {"CP": 0.0}
    }
}

ANIMAL_IMAGES_RESOURCES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600&auto=format&fit=crop",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600&auto=format&fit=crop",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600&auto=format&fit=crop",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600&auto=format&fit=crop",
    "سمان": "https://images.unsplash.com/photo-1600366114216-ad3f5728a2a5?q=80&w=600&auto=format&fit=crop",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop"
}

if "active_formula" not in st.session_state: st.session_state["active_formula"] = {"ذرة صفراء": 63.0, "كسب فول صويا 44%": 31.0, "إضافات مخصصة": 6.0}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 16.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_animal_img" not in st.session_state: st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES["عام"]
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0

# ==========================================
# 5. بناء واجهة الترويسة الرئيسية الفخمة
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logo, col_title = st.columns([0.25, 0.75])
with col_logo:
    if img_base64: st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else: st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور الذكية للإنتاج الحيواني وصناعة الأعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #1565C0; text-align:right; font-size:1.1rem; margin-top:5px; margin-bottom:0;'>الحساب النشط حالياً: <span style='color:#c62828; font-weight:bold;'>{st.session_state['sub_role'] if st.session_state['sub_role'] else st.session_state['user_role']}</span></p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

# =====================================================================
# ⚙️ فرز الواجهات التلقائي والصارم حسب رتبة الصلاحية المدخلة
# =====================================================================

# ---------------------------------------------------------------------
# أ. واجهة حساب المربي (المحتوى البسيط والمحدود جداً حسب الرغبة)
# ---------------------------------------------------------------------
if st.session_state["user_role"] == "guest":
    st.markdown('<div class="section-title">📏 شريط قياس ومحيط الصدر لتقدير الأوزان حيّاً</div>', unsafe_allow_html=True)
    col_h, col_l = st.columns(2)
    with col_h: h_girth = st.number_input("📏 محيط صدر الحيوان (سم):", value=145.0, key="guest_girth")
    with col_l: b_length = st.number_input("📏 طول الجسم (سم):", value=125.0, key="guest_length")
    calc_weight = (h_girth ** 2 * b_length) / 10838
    st.success(f"📊 الوزن المقدر للرأس: **{calc_weight:.1f} كجم** | العليقة اليومية المطلوبة: **{calc_weight*0.025:.2f} كجم**")

    st.markdown('<div class="section-title">📝 مقادير خلط طن العلف (1000 كجم) المتزن</div>', unsafe_allow_html=True)
    animal_choice = st.selectbox("اختر نوع الحيوان المتوفر بمزرعتك:", ["طائر السمان والداجن", "الأبقار والمجترات"])
    
    if "guest_mix" not in st.session_state:
        st.session_state["guest_mix"] = None

    if st.button("🚀 توليد وعرض خلطة الأعلاف فوراً", type="primary", use_container_width=True):
        if "السمان" in animal_choice:
            m_formula = {"ذرة صفراء صفية": 63.5, "كسب فول صويا 44% بروتين": 31.0, "مركزات وإضافات فنية": 5.5}
        else:
            m_formula = {"ذرة صفراء": 45.0, "شعير مطحون محلي": 18.0, "كسب فول صويا 44%": 20.0, "نخالة قمح ردة": 14.5, "أملاح جيرية": 2.5}
        st.session_state["guest_mix"] = m_formula

    if st.session_state["guest_mix"]:
        for k, v in st.session_state["guest_mix"].items():
            st.markdown(f"▪️ **{k}:** اخلط وزن: <span style='color:#1b5e20; font-weight:bold;'>{v*10:.1f} كجم</span> داخل الطن (نسبة {v:.1f}%)", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# ب. واجهة الأطباء البيطريين والمختصين / ج. واجهة المستشار والمالك (تاور)
# ---------------------------------------------------------------------
else:
    # بناء التبويبات الرسمية للبرنامج الأصلي
    if st.session_state["user_role"] == "admin":
        tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى", "📊 بورصة تاور المركزية للمنتجات والماشية", "🏭 إدارة المستودعات والخصم التلقائي", "🧾 التسويق وفواتير حركة البيع", "🖨️ مصمم بطاقات الديباجة والدعاية", "📥 ملاحظات وتقارير الأطباء والمختصين"]
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
                chosen_state = st.selectbox("اختر الولاية السودانية المحدثة:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال كردفان", "إقليم النيل الأزرق"])
            elif user_country == "ليبيا": chosen_state = st.selectbox("اختر الإقليم الجغرافي:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
            else: chosen_state = st.selectbox("الإقليم الإداري:", ["المركز الرئيسي العالمي"])

        with col_city:
            if user_country == "السودان": user_city = st.selectbox("اختر المدينة:", ["الخرطوم", "ود مدني", "القضارف المدينة", "الأبيض", "الدمازين"])
            elif user_country == "ليبيا":
                if chosen_state == "المنطقة الشرقية": user_city = st.selectbox("اختر المدينة الليبية:", ["طبرق", "بنغازي", "البيضاء"])
                else: user_city = st.selectbox("اختر المدينة الليبية:", ["طرابلس", "مصراتة", "سبها"])
            else: user_city = st.text_input("اكتب اسم المدينة العالمية يدوياً:", "طبرق")

        live_prices = get_adjusted_market_data(user_country, chosen_state, user_city)
        
        col_view1, col_view2 = st.columns(2)
        with col_view1:
            st.markdown(f'<div class="price-card"><b>📈 بورصة الماشية والداجن الحية في ({user_city}):</b><br>' + 
                        "<br>".join([f"▪️ {k}: <b>${v:.2f}</b> (تعادل: {v*local_rate:,.2f} {local_sym})" for k, v in st.session_state["global_livestock_prices"].items()]) + "</div>", unsafe_allow_html=True)
        with col_view2:
            st.markdown(f'<div class="price-card"><b>🥩 بورصة المنتجات الحيوانية والألبان والبيض في ({user_city}):</b><br>' + 
                        "<br>".join([f"▪️ {k}: <b>${v:.2f}</b> (تعادل: {v*local_rate:,.2f} {local_sym})" for k, v in st.session_state["global_products_prices"].items()]) + "</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">⚖️ ثانياً: اختيار القطاع والنوع والإنتاجية المستهدفة</div>', unsafe_allow_html=True)
        col_sec, col_sub, col_prod = st.columns(3)
        with col_sec: main_sector = st.selectbox("اختر القطاع الإنتاجي الرئيسي:", ["الطيور والسمان", "الماعز وسلالاته", "الأبقار وسلالاتها", "الخيول والفروسية", "الأسماك والأحياء المائية"])
        
        show_measurements = False; default_cp = 14.0; dynamic_img_key = "عام"; chosen_concentrate = None
        
        with col_sub:
            if main_sector == "الخيول والفروسية": sub_type = st.selectbox("السلالة المستهدفة:", ["خيل عربي أصيل", "خيول محلية هجين"]); dynamic_img_key = "خيول"; show_measurements = True; chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الماعز وسلالاته": sub_type = st.selectbox("السلالة المستهدفة:", ["الماعز النوبي السوداني", "بور / محسن"]); dynamic_img_key = "ماعز"; show_measurements = True; chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الأبقار وسلالاتها": sub_type = st.selectbox("السلالة المستهدفة:", ["كنانة (سوداني)", "هولشتاين / محسن"]); dynamic_img_key = "أبقار"; show_measurements = True; chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الطيور والسمان": sub_type = st.selectbox("نوع الطيور:", ["طائر السمان (Quail)", "دواجن لاحم (Broiler)", "دواجن بياض (Layer)"]); dynamic_img_key = "سمان" if "السمان" in sub_type else "دواجن"; chosen_concentrate = "مركزات دواجن وسمان"
            else: sub_type = st.selectbox("نوع الأسماك:", ["البلطي النيلي (Tilapia)"]); dynamic_img_key = "أسماك"; chosen_concentrate = "مسحوق أسماك (Fishmeal 60%)"

        with col_prod:
            if main_sector == "الخيول والفروسية": prod_stage = st.selectbox("نوع الإنتاج:", ["خيول رياضة ونشاط مكثف", "أمهار نامية صغيرة"]); default_cp = 16.0 if "أمهار" in prod_stage else 12.0
            elif main_sector == "الماعز وسلالاته": prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج اللحوم وتسمين", "إنتاج ألبان وحليب"]); default_cp = 15.5 if "ألبان" in prod_stage else 13.5
            elif main_sector == "الأبقار وسلالاتها": prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج حليب وغزارة إدرار", "تسمين عجول مكثف"]); default_cp = 16.0 if "حليب" in prod_stage else 13.0
            elif main_sector == "الطيور والسمان":
                if "السمان" in sub_type: prod_stage = st.selectbox("نوع الإنتاج:", ["سمان بادي / نامي", "سمان بياض إنتاجي"]); default_cp = 24.0 if "بادي" in prod_stage else 20.0
                else: prod_stage = st.selectbox("نوع الإنتاج:", ["بادي دواجن 23%", "نامي دواجن 21%", "ناهي دواجن 19%"]); default_cp = 23.0 if "بادي" in prod_stage else (21.0 if "نامي" in prod_stage else 19.0)
            else: prod_stage = st.selectbox("نوع الإنتاج:", ["بادئ زريعة أسماك عالي", "نمو وتسمين أسماك نيلية"]); default_cp = 35.0 if "زريعة" in prod_stage else 30.0

        if show_measurements:
            st.markdown('<div class="section-title">📐 ثالثاً: شريط القياس الجسدي وتقدير الأوزان</div>', unsafe_allow_html=True)
            col_h, col_l = st.columns(2)
            with col_h: h_girth = st.number_input("📏 محيط الصدر (سم):", value=150.0, key="expert_girth")
            with col_l: b_length = st.number_input("📏 طول الجسم (سم):", value=130.0, key="expert_length")
            calc_weight = (h_girth ** 2 * b_length) / 10838; req_feed_kg = calc_weight * 0.025
            st.success(f"📊 الوزن الحيوي المتوقع: **{calc_weight:.1f} كجم** | الاحتياج اليومي: **{req_feed_kg:.2f} كجم**")
        else:
            st.markdown('<div class="section-title">✨ ثالثاً: قطاع الطيور والأسماك</div>', unsafe_allow_html=True)
            st.info(f"💡 نظام المعالجة التلقائي: تم تحييد شريط القياس الجسدي لعدم ملاءمته حَقلياً للطيور والأسماك والسمان.")

        st.markdown('<div class="section-title">📋 رابعاً: ضبط نسبة البروتين المستهدفة فنيّاً</div>', unsafe_allow_html=True)
        final_target_cp = st.slider("حدّد نسبة البروتين المستهدفة فنيّاً:", 10.0, 45.0, value=default_cp)

        st.markdown('<div class="section-title">🌾 خامساً: توليد العليقة الاقتصادية المتزنة وطباعة التركيبة</div>', unsafe_allow_html=True)
        selected_ingredients = []; ingredient_prices = {}
        
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            with st.expander(f"📁 {cat_name}", expanded=True):
                sub_cols = st.columns(3)
                for idx, (ing_name, _) in enumerate(items.items()):
                    if ing_name == "كسب فول صويا 48%": is_def = False
                    else: is_def = True if ing_name == chosen_concentrate or "ذرة صفراء" in ing_name or "كسب فول صويا 44%" in ing_name or "ملح" in ing_name or "بيكربونات" in ing_name else False
                    
                    with sub_cols[idx % 3]:
                        checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                        current_live_price = live_prices.get(ing_name, 350.0)
                        price_input = current_live_price
                        if checked:
                            selected_ingredients.append(ing_name)
                            ingredient_prices[ing_name] = price_input

        if st.button("🚀 تشغيل محرك التركيب الذكي وحساب نسب الخلط المثلى", type="primary", use_container_width=True):
            formula_results = {}
            fixed_ratios = {"ملح الطعام": 0.005, "مضاد سموم فطرية": 0.002, "الحجر الجيري (بودرة بلاط)": 0.015, "فوسفات ثنائي الكالسيوم (DCP)": 0.01}
            if "الطيور" in main_sector: fixed_ratios["مركزات دواجن وسمان"] = 0.05
            elif main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاته"]: fixed_ratios["مركزات خيول ومجترات"] = 0.025

            used_fixed_pct = 0.0
            for name in selected_ingredients:
                if name in fixed_ratios:
                    formula_results[name] = fixed_ratios[name] * 100; used_fixed_pct += fixed_ratios[name] * 100

            grains_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"]]
            protein_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"]]
            
            if not grains_ingredients: grains_ingredients = ["ذرة صفراء"]
            if not protein_ingredients: protein_ingredients = ["كسب فول صويا 44%"]

            grain_share = max(62.5, (100.0 - used_fixed_pct) * 0.63)
            leftover_for_others = 100.0 - used_fixed_pct - grain_share

            for x in grains_ingredients: formula_results[x] = grain_share / len(grains_ingredients)
            for x in protein_ingredients: formula_results[x] = leftover_for_others / len(protein_ingredients)

            total_grains_pct = sum([formula_results.get(x, 0.0) for x in grains_ingredients])

            enzyme_alerts = []
            auto_added_enzymes = {}
            if main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاته"] and total_grains_pct > 45.0:
                auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.75
                enzyme_alerts.append("🧬 بيكربونات الصوديوم: تم الفرض التلقائي لمنع حموضة الكرش والاضطرابات الهضمية.")
            
            if main_sector == "الطيور والسمان":
                auto_added_enzymes["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05
                enzyme_alerts.append("🧬 إنزيم الفايتيز: مضاف تلقائياً لتحرير الفسفور النباتي العضوي وتحسين معامل التحويل للسمان والدواجن.")

            if auto_added_enzymes:
                for enz_name, enz_pct in auto_added_enzymes.items(): formula_results[enz_name] = enz_pct

            st.session_state["active_formula"] = formula_results
            st.session_state["active_cp_tag"] = final_target_cp
            st.session_state["active_breed_tag"] = sub_type
            st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES.get(dynamic_img_key, ANIMAL_IMAGES_RESOURCES["عام"])
            st.session_state["active_stage_title"] = f"{main_sector} - {prod_stage}"

            if enzyme_alerts:
                st.toast("🧪 جاري احتساب وهندسة الإنزيمات المضافة تلقائياً... ستختفي هذه النافذة بعد 30 ثانية.", icon="🔬")
                for alert in enzyme_alerts: st.toast(alert, icon="✅")

            st.success(f"🎯 تم تشغيل المحرك الذكي. إجمالي نسبة الحبوب المستقرة بالخلطة: {total_grains_pct:.1f}%")
            
            res_col1, res_col2 = st.columns([0.6, 0.4])
            with res_col1:
                st.write("#### 📝 المقادير الفنية الدقيقة المعتمدة لتركيب طن واحد (كجم):")
                for k, v in formula_results.items(): st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** / طن)")
                ton_cost = sum([(v/100) * ingredient_prices.get(k, 300.0) if k in ingredient_prices else (v/100)*400.0 for k, v in formula_results.items()])
                st.session_state["computed_ton_cost"] = ton_cost
                st.metric(f"💰 التكلفة لإنتاج الطن في {user_city}:", f"${ton_cost:.2f} ({ton_cost*local_rate:,.1f} {local_sym})")
            with res_col2: st.bar_chart(formula_results)

        # صندوق مقترحات المختصين
        if st.session_state["user_role"] == "expert":
            st.markdown('<div class="section-title">✉️ صندوق المساهمة الفنية وتطوير البرمجيات (الربط المباشر بـ Gmail تاور)</div>', unsafe_allow_html=True)
            expert_note = st.text_area("أدخل مقترحك الفني أو تعليقك العلمي لتطوير المنصة:")
            if st.button("🚀 إرسال المقترح والملاحظات فورا للمستشار تاور"):
                if expert_note:
                    st.session_state["expert_comments_log"].append({"sender": st.session_state["sub_role"], "note": expert_note})
                    subject = f"تقرير فني جديد من {st.session_state['sub_role']}"
                    body = f"نوع التخصص: {st.session_state['sub_role']}\nالملاحظة العلمية المدونة لعام 2026:\n{expert_note}"
                    
                    if send_email_notification(subject, body):
                        st.success("✅ تم إرسال الرسالة بنجاح عبر نظام Gmail المباشر ووصلت بريد المستشار تاور فوراً.")
                    else:
                        st.warning("⚠️ تم حفظ المقترح محلياً بالمنظومة، وتعذر التوصيل البريدي المؤقت للإيميل (يرجى التحقق من إعدادات السيرفر بكود التطبيق).")
                else:
                    st.error("❌ يرجى كتابة التعليق أولاً قبل الإرسال.")

    # التبويبات الخاصة بالإدارة والتحكم الكامل (للمستشار تاور فقط)
    if st.session_state["user_role"] == "admin":
        with tabs[1]:
            st.markdown('<div class="section-title">📊 لوحة تحكم بورصة تاور المركزية الشاملة</div>', unsafe_allow_html=True)
            col_edit1, col_edit2 = st.columns(2)
            with col_edit1:
                for animal, price in st.session_state["global_livestock_prices"].items():
                    st.session_state["global_livestock_prices"][animal] = st.number_input(f"سعر: {animal}", min_value=0.0, value=float(price), key=f"live_{animal}")
            with col_edit2:
                for product, price in st.session_state["global_products_prices"].items():
                    st.session_state["global_products_prices"][product] = st.number_input(f"سعر: {product}", min_value=0.0, value=float(price), key=f"prod_{product}")

        with tabs[2]:
            st.markdown('<div class="section-title">🏭 لوحة التحكم الذكية بالمخازن والمستودعات</div>', unsafe_allow_html=True)
            inv_cols = st.columns(3)
            for idx, (ing_name, qty) in enumerate(st.session_state["inventory"].items()):
                with inv_cols[idx % 3]:
                    st.session_state["inventory"][ing_name] = st.number_input(f"رصيد طن ({ing_name}):", min_value=0.0, value=float(qty), key=f"inv_{ing_name}")

        with tabs[3]:
            st.markdown('<div class="section-title">💰 نظام تسويق المنتجات وإصدار الفواتير مع الخصم التلقائي</div>', unsafe_allow_html=True)
            col_c1, col_c2 = st.columns(2)
            with col_c1: required_tons = st.number_input("الكمية المطلوبة للعميل (بالطن):", min_value=0.1, value=1.0)
            with col_c2: added_profit = st.number_input("هامش الربح لكل طن ($):", min_value=0.0, value=40.0)
            total_bill = (st.session_state["computed_ton_cost"] + added_profit) * required_tons
            st.markdown(f"### 🧾 إجمالي الفاتورة المستحقة: `${total_bill:.2f}` (أو `{total_bill*local_rate:,.1f}` {local_sym})")
            
            if st.button("✅ تأكيد البيع وخصم الكميات من المخزن"):
                can_sell = True
                # فحص توفر الكميات لتجنب المخزون السالب
                for name, pct in st.session_state["active_formula"].items():
                    needed = (pct / 100) * required_tons
                    if st.session_state["inventory"].get(name, 0.0) < needed:
                        st.error(f"❌ المخزون غير كافٍ من المادة: {name} (المطلوب: {needed:.2f} طن، المتوفر: {st.session_state['inventory'].get(name, 0.0):.2f} طن)")
                        can_sell = False
                
                if can_sell:
                    for name, pct in st.session_state["active_formula"].items(): 
                        st.session_state["inventory"][name] -= ((pct / 100) * required_tons)
                    st.success("🔥 تم تحديث رصيد المستودعات بنجاح!")
                    time.sleep(1)
                    st.rerun()

        with tabs[4]:
            st.markdown('<div class="section-title">🏷️ مُصمم ديباجات الطباعة الفنية لطائر السمان وبطاقات الجوال</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="sack-tag">
                <img src="{st.session_state['active_animal_img']}" class="animal-banner-img">
                <h2 style="text-align: center; margin-top:0;">🌟 مجموعة تاور لإنتاج الأعلاف المتكاملة 🌟</h2>
                <p style="text-align: center; font-weight: bold; background-color:#e8f5e9; padding:6px; color:#1b5e20;">🎯 علف مخصص لـ: {st.session_state['active_stage_title']} | الصنف والسلالة: {st.session_state['active_breed_tag']} | نسبة البروتين النهائية: {st.session_state['active_cp_tag']:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)

        with tabs[5]:
            st.markdown('<div class="section-title">📥 قائمة إشعارات ومقترحات الأطباء والمختصين الواردة للمنصة</div>', unsafe_allow_html=True)
            if st.session_state["expert_comments_log"]:
                for idx, item in enumerate(st.session_state["expert_comments_log"]):
                    st.markdown(f"""
                    <div style="background-color:#e3f2fd; padding:12px; border-radius:8px; margin-bottom:8px; direction:rtl; text-align:right;">
                        <b>📌 رتبة وتخصص المرسل العلمي: <span style="color:#1565C0;">{item['sender']}</span></b><br>
                        📝 نص المقترح الفني الوارد للمنظومة: {item['note']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📭 الصندوق المحلي خالي من الملاحظات حالياً (علماً بأن المقترحات ترسل لـ Gmail مباشرة).")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. التوقيع المصغر الدائم للمطور بأسفل الشاشة
# ==========================================
st.markdown(
    """
    <div class="mini-left-signature">
        👨‍🔬 م. عبد القادر إسماعيل تاور © 2026 | خبير الحلول الذكية للثروة الحيوانية والبرمجيات المتكاملة
    </div>
    """,
    unsafe_allow_html=True
)
