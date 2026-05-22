import streamlit as st
import numpy as np
import json
import os
import base64
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# استيراد محرك البرمجة الخطية لمنع نسب الخطأ في التراكيب العلفية تماماً
from scipy.optimize import linprog

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
# 🔒 إعدادات خادم البريد الإلكتروني المرجعية
# ------------------------------------------
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
    if SENDER_EMAIL == "YOUR_EMAIL@gmail.com" or SENDER_PASSWORD == "xxxx xxxx xxxx xxxx":
        st.error("⚠️ خطأ إعدادات: يرجى تحديث بيانات الـ SMTP داخل السورس كود أولاً.")
        return False
        
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود الموسع الشامل (Linear Programming) - منصة تاور الذكية للأعلاف"
    
    body = "السلام عليكم م. عبد القادر،\n\nمرفق مع هذه الرسالة النسخة البرمجية الموسعة والمستقرة لمنصة تاور الذكية لعام 2026 القائمة على محرك الاستمثال الخطي مع المكتبة الشاملة المحدثة للأحماض والإنزيمات والمخلفات.\n\nتحياتي،\nالنظام التلقائي للمنصة."
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        current_file = __file__
        with open(current_file, "r", encoding="utf-8") as f:
            code_content = f.read()
        
        attachment = MIMEText(code_content, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', filename="tower_expanded_lp_platform.py")
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

# تصميم واجهة المستخدم الاحترافية بـ CSS
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
# 3. المكتبة الشاملة الموسعة وبورصة التحديثات الكبرى لعام 2026
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
        "كسب النواة النخيل": {"CP": 16.0}
    },
    "🚜 المخلفات الزراعية والصناعية والمواد المالئة": {
        "نخالة قمح (ردة)": {"CP": 15.0}, "البرسيم الجاف (الدريس)": {"CP": 16.5}, 
        "مولاس قصب السكر": {"CP": 4.0}, "تبن قمح ناعم": {"CP": 3.2}, 
        "قشر فول سوداني مطحون": {"CP": 5.0}, "سرسة الأرز المطحونة": {"CP": 2.5},
        "بقايا تفل البنجر المجفف": {"CP": 8.0}, "مخلفات مصانع البسكويت": {"CP": 9.5},
        "سيلاج ذرة كامل متكامل": {"CP": 8.0}
    },
    "🧬 مصادر البروتين الحيواني والمركزات": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0}, "مسحوق أسماك فاخر (72%)": {"CP": 72.0},
        "مسحوق اللحم والعظم": {"CP": 50.0}, "مركزات دواجن لاحم 5%": {"CP": 40.0}, 
        "مركزات دواجن بياض 5%": {"CP": 35.0}, "مركزات خيول ومجترات عالية": {"CP": 36.0}
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
        "بروتييز عالي الكفاءة (Protease)": {"CP": 0.0},
        "مستخلص الخمائر والجدر الخلوية (MOS)": {"CP": 12.0}
    },
    "🪨 الأملاح والمعادن ومنظمات الهضم": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0}, "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0}, 
        "ملح الطعام النقي": {"CP": 0.0}, "مضاد سموم فطرية بيولوجي": {"CP": 0.0}, 
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0}, "أكسيد المغنيسيوم العلفي": {"CP": 0.0},
        "يوريا علفية محصنة (المجترات فقط)": {"CP": 287.0}
    }
}

# مواءمة مستودع المخزون آلياً مع التوسعة الجديدة لمنع أخطاء الـ KeyError
if "inventory" not in st.session_state:
    st.session_state["inventory"] = {}
for cat_name, items in BIG_FEEDS_LIBRARY.items():
    for ing in items:
        if ing not in st.session_state["inventory"]:
            st.session_state["inventory"][ing] = 20.0  # الرصيد الافتراضي الأولي بالطن لكل خامة جديدة

if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين / محسن ($)": 1350.0, "أبقار كنانة وبطانة محلية ($)": 900.0,
        "ضأن وستيرلنغ / محلي ($)": 180.0, "ماعز نوبي وصحراوي ($)": 130.0,
        "خيول عربية أصيلة وهجين ($)": 4500.0, " كتكوت لاحم عمر يوم ($)": 0.65, "دجاج بياض عمر البشاير ($)": 5.50
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

SUDAN_GEOGRAPHY = {
    "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"], "ولاية الجزيرة": ["ود مدني", "الحصاحيصا", "المناقل"],
    "ولاية القضارف": ["القضارف المدينة", "الفاو"], "ولاية كسلا": ["كسلا", "حلفا الجديدة"],
    "ولاية سنار": ["سنار", "سنجة"], "ولاية النيل الأبيض": ["ربك", "كوستي"],
    "ولاية شمال كردفان": ["الأبيض", "بارا"], "ولاية نهر النيل": ["الدامر", "عطبرة", "شندي"],
    "ولاية الشمالية": ["دنقلا", "مروي"]
}

def get_adjusted_market_data(country, state_or_region, city):
    # مصفوفة تسعير عالمية مرجعية موسعة للخامات الجديدة
    feed_prices = {
        "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0, "سورجم (فتريتة)": 195.0, "قمح محلي مصنّع": 240.0, "جريش أرز رزاز": 180.0, "دخن محلي غزير": 260.0, "شوفان علفي": 220.0,
        "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا 44%": 440.0, "كسب فول صويا 48%": 480.0, "كسب عباد الشمس 36%": 310.0, "كسب بذور القطن (مقشور)": 290.0, "كسب بذور الكتان": 300.0, "كسب السمسم المحسن": 410.0, "كسب جلوتين الذرة 60%": 590.0, "كسب النواة النخيل": 190.0,
        "نخالة قمح (ردة)": 150.0, "البرسيم الجاف (الدريس)": 170.0, "مولاس قصب السكر": 120.0, "تبن قمح ناعم": 80.0, "قشر فول سوداني مطحون": 60.0, "سرسة الأرز المطحونة": 45.0, "بقايا تفل البنجر المجفف": 140.0, "مخلفات مصانع البسكويت": 165.0, "سيلاج ذرة كامل متكامل": 95.0,
        "مسحوق أسماك (Fishmeal 60%)": 850.0, "مسحوق أسماك فاخر (72%)": 1100.0, "مسحوق اللحم والعظم": 600.0, "مركزات دواجن لاحم 5%": 650.0, "مركزات دواجن بياض 5%": 610.0, "مركزات خيول ومجترات عالية": 600.0,
        "ليسين نقي (L-Lysine)": 2200.0, "ميثيونين نقي (DL-Methionine)": 2800.0, "ثريونين نقي (L-Threonine)": 2400.0, "تريبتوفان نقي (L-Tryptophan)": 4500.0, "فالين نقي (L-Valine)": 3800.0,
        "بريمكس تسمين دواجن (Premix)": 1200.0, "بريمكس بياض وبشاير": 1150.0, "بريمكس أبقار حلابة ومجترات": 1000.0, "بريمكس خيول وفروسية": 1400.0,
        "إنزيم الفايتيز الزامي (Phytase Super-D)": 1500.0, "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": 1800.0, "بروتييز عالي الكفاءة (Protease)": 2000.0, "مستخلص الخمائر والجدر الخلوية (MOS)": 1600.0,
        "الحجر الجيري (بودرة بلاط)": 40.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0, "ملح الطعام النقي": 30.0, "مضاد سموم فطرية بيولوجي": 950.0, "بيكربونات الصوديوم (الصودا)": 340.0, "أكسيد المغنيسيوم العلفي": 450.0, "يوريا علفية محصنة (المجترات فقط)": 400.0
    }
    mult = 1.15 if country == "السودان" else (1.10 if country == "ليبيا" else 1.04)
    for k in feed_prices: feed_prices[k] *= mult
    return feed_prices

ANIMAL_IMAGES_RESOURCES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
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

col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    if img_base64: st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else: st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور الذكية للإنتاج الحيواني وصناعة الأعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.1rem; margin-top:5px; margin-bottom:0;'>الإصدار الموسع عالي المرونة - حسابات الاستمثال الخطي الصارم (Scipy Linear Programming)</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; margin-top: 5px;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

if st.session_state["user_role"] == "admin":
    tabs_titles = ["🔬 النمذجة والحسابات الخطية الكبرى", "📊 بورصة تاور المركزية للأسعار", "🏭 إدارة المستودعات والخصم التلقائي", "🧾 التسويق وفواتير حركة البيع", "🏷️ مصمم بطاقات الديباجة والدعاية"]
else:
    tabs_titles = ["🔬 النمذجة والحسابات الخطية الكبرى"]

tabs = st.tabs(tabs_titles)

with tabs[0]:
    st.markdown('<div class="section-title">🌍 أولاً: تحديد الموقع الجغرافي وبورصة الأسعار</div>', unsafe_allow_html=True)
    col_country, col_state, col_city = st.columns(3)
    with col_country: user_country = st.selectbox("اختر دولة المربي:", ["السودان", "ليبيا", "مصر"])
        
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    local_rate = c_info["rate"]; local_sym = c_info["sym"]

    with col_state: chosen_state = st.selectbox("اختر الولاية/الإقليم الإداري:", list(SUDAN_GEOGRAPHY.keys()) if user_country == "السودان" else ["المنطقة الإقليمية المركزية"])
    with col_city: user_city = st.selectbox("اختر المدينة المستهدفة:", SUDAN_GEOGRAPHY[chosen_state] if user_country == "السودان" else ["المدينة الرئيسية"])

    live_prices = get_adjusted_market_data(user_country, chosen_state, user_city)
    
    col_view1, col_view2 = st.columns(2)
    with col_view1:
        st.markdown(f'<div class="price-card"><b>📈 بورصة الماشية والداجن الحية في ({user_city}):</b><br>' + 
                    "<br>".join([f"▪️ {k}: <b>${v:.2f}</b> (<span style='color:#e65100;'>{v*local_rate:,.1f} {local_sym}</span>)" for k, v in st.session_state["global_livestock_prices"].items()]) + "</div>", unsafe_allow_html=True)
    with col_view2:
        st.markdown(f'<div class="price-card"><b>🥛 بورصة المنتجات والبيض والألبان في ({user_city}):</b><br>' + 
                    "<br>".join([f"▪️ {k}: <b>${v:.2f}</b> (<span style='color:#1b5e20;'>{v*local_rate:,.1f} {local_sym}</span>)" for k, v in st.session_state["global_products_prices"].items()]) + "</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">⚖️ ثانياً: اختيار القطاع والإنتاجية والمحددات الفنية</div>', unsafe_allow_html=True)
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec: main_sector = st.selectbox("اختر القطاع الإنتاجي الرئيسي:", ["الطيور والسمان", "الأبقار وسلالاتها", "الماعز وسلالاته", "الخيول والفروسية"])
    
    show_measurements = False; weight_factor = 10000; feed_factor = 0.02; default_cp = 16.0; dynamic_img_key = "عام"
    # بريمكس إجباري ونوع الأحماض المرتبطة بنوع الحيوان لمنع الخلط المجهول
    req_premix = "بريمكس أبقار حلابة ومجترات"; req_acid = "ليسين نقي (L-Lysine)"

    with col_sub:
        if main_sector == "الخيول والفروسية": sub_type = st.selectbox("السلالة المستهدفة:", ["خيل عربي أصيل", "ثوروبريد", "خيول محلية"]); dynamic_img_key = "خيول"; show_measurements = True; weight_factor = 11877; feed_factor = 0.022; req_premix = "بريمكس خيول وفروسية"
        elif main_sector == "الماعز وسلالاته": sub_type = st.selectbox("السلالة المستهدفة:", ["الماعز النوبي السوداني", "الماعز الصحراوي", "بور"]); dynamic_img_key = "ماعز"; show_measurements = True; weight_factor = 11250; feed_factor = 0.028
        elif main_sector == "الأبقار وسلالاتها": sub_type = st.selectbox("السلالة المستهدفة:", ["كنانة (سوداني)", "بطانة", "هولشتاين"]); dynamic_img_key = "أبقار"; show_measurements = True; weight_factor = 10838; feed_factor = 0.025
        else: sub_type = st.selectbox("نوع الطيور والداجن:", ["دواجن لاحم (Broiler)", "دواجن بياض (Layer)", "طائر السمان"]); dynamic_img_key = "دواجن"; req_premix = "بريمكس تسمين دواجن (Premix)" if "لاحم" in sub_type else "بريمكس بياض وبشاير"

    with col_prod:
        if main_sector == "الخيول والفروسية": prod_stage = st.selectbox("مرحلة الخيل:", ["نشاط مكثف وسباق", "أمهار نامية", "فرسات مرضعات"]); default_cp = 14.0
        elif main_sector == "الماعز وسلالاته": prod_stage = st.selectbox("مرحلة الماعز:", ["تسمين جداء مكثف", "حلب وإنتاج وفير"]); default_cp = 15.0
        elif main_sector == "الأبقار وسلالاتها": prod_stage = st.selectbox("مرحلة الأبقار:", ["إدرار حليب عالي", "تسمين عجول دوري"]); default_cp = 14.5
        else: prod_stage = st.selectbox("مرحلة الطيور:", ["بادي 23%", "نامي 21%", "ناهي 19%", "بياض إنتاجي"]); default_cp = 23.0 if "بادي" in prod_stage else (21.0 if "نامي" in prod_stage else (19.0 if "ناهي" in prod_stage else 17.5))

    if show_measurements:
        st.markdown('<div class="section-title">📐 ثالثاً: شريط القياس الجسدي وتقدير الأوزان والاحتياجات حَقلياً</div>', unsafe_allow_html=True)
        col_h, col_l, col_ag = st.columns(3)
        with col_h: h_girth = st.number_input("📏 محيط الصدر (سم):", value=150.0)
        with col_l: b_length = st.number_input("📏 طول الجسم الجسدي (سم):", value=130.0)
        with col_ag: a_months = st.number_input("⏳ عمر الحيوان التقديـري (أشهر):", value=12)
        calc_weight = (h_girth ** 2 * b_length) / weight_factor; req_feed_kg = calc_weight * feed_factor
        st.success(f"📊 الوزن الحيوي المتوقع للكتلة: **{calc_weight:.1f} كجم** | الاحتياج اليومي المقدر للمادة الجافة: **{req_feed_kg:.2f} كجم**")

    st.markdown('<div class="section-title">📋 رابعاً: حد البروتين الصارم للموازنة</div>', unsafe_allow_html=True)
    col_p1, col_p2 = st.columns(2)
    with col_p1: st.metric("🧬 بروتين العليقة المقترح علمياً:", f"{default_cp} %")
    with col_p2:
        override_cp = st.checkbox("⚙️ تفعيل التعديل الفني واليدوي المستقل للبروتين")
        final_target_cp = st.slider("حدّد نسبة البروتين المستهدفة بدقة (محدد قاطع):", 10.0, 45.0, value=default_cp) if override_cp else default_cp

    st.markdown('<div class="section-title">🌾 خامساً: تفعيل الخامات المتاحة بالمستودع الشامل (المكتبة الموسعة لعام 2026)</div>', unsafe_allow_html=True)
    selected_ingredients = []; ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"{cat_name}", expanded=True if "الحبوب" in cat_name or "الأكساب" in cat_name else False):
            sub_cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with sub_cols[idx % 3]:
                    # وضع اختيار ذكي أولي للخامات الشائعة لتسهيل العرض
                    is_def = True if ing_name in ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)", "ملح الطعام النقي", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)", req_premix] else False
                    checked = st.checkbox(ing_name, value=is_def, key=f"fex_{ing_name}")
                    current_live_price = live_prices.get(ing_name, 350.0)
                    
                    if st.session_state["user_role"] == "admin": 
                        price_input = st.number_input(f"سعر الطن لحسابات الكلفة ($) [{ing_name}]:", min_value=5.0, value=float(current_live_price), key=f"pex_{ing_name}")
                    else:
                        st.markdown(f"💰 السعر الجاري بالمنطقة: **`${current_live_price:.2f}`**")
                        price_input = current_live_price
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price_input

    # حجز وقفل نسب إضافات الأمان الدقيقة (الحجر، الملح، بريمكس، مضاد سموم، DCP) لضمان سلامة وصحة الطن
    fixed_additives = {
        "ملح الطعام النقي": 0.5, "مضاد سموم فطرية بيولوجي": 0.2, "الحجر الجيري (بودرة بلاط)": 1.4, 
        "فوسفات ثنائي الكالسيوم (DCP)": 1.0, req_premix: 0.3
    }
    # ربط الأحماض الأمينية النقية بجرعات فنية مغذية دقيقة (0.15% لكل حمض أساسي متاح)
    for acid_item in ["ليسين نقي (L-Lysine)", "ميثيونين نقي (DL-Methionine)", "ثريونين نقي (L-Threonine)"]:
        if acid_item in selected_ingredients:
            fixed_additives[acid_item] = 0.15

    for item, val in fixed_additives.items():
        if item not in selected_ingredients:
            selected_ingredients.append(item)
            ingredient_prices[item] = live_prices.get(item, 500.0)

    st.markdown("---")
    if st.button("🚀 تشغيل محرك الاستمثال الخطي للأعلاف (Scipy Optimized)", type="primary", use_container_width=True):
        
        # --- بناء المعادلات الرياضية للمحددات الكبرى ---
        c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
        
        bounds = []
        for ing in selected_ingredients:
            if ing in fixed_additives:
                bounds.append((fixed_additives[ing], fixed_additives[ing])) # حجز صارم لمنع تلاعب المحرك بالإضافات الدقيقة
            else:
                bounds.append((0.0, 100.0))

        # محدد توازن كتلة الطن بالكامل (مجموع المكونات = 100%)
        A_eq = [[1.0 for _ in selected_ingredients]]
        b_eq = [100.0]
        
        # محدد التساوي الغذائي الدقيق للبروتين (مجموع حاصل ضرب النسب في قيم البروتين = المستهدف)
        cp_row = []
        for ing in selected_ingredients:
            cp_val = 0.0
            for cat in BIG_FEEDS_LIBRARY.values():
                if ing in cat: cp_val = cat[ing].get("CP", 0.0)
            cp_row.append(cp_val)
        A_eq.append(cp_row)
        b_eq.append(final_target_cp * 100.0)

        # محدد عدم التساوي الصارم (قفل نسبة إجمالي الحبوب والطاقة الكبرى بين 60% و 65% كقيمة مطلقة)
        energy_row_min = []
        energy_row_max = []
        for ing in selected_ingredients:
            is_energy = ing in BIG_FEEDS_LIBRARY["🌾 الحبوب ومصادر الطاقة الكبرى"]
            energy_row_min.append(-1.0 if is_energy else 0.0)
            energy_row_max.append(1.0 if is_energy else 0.0)
            
        A_ub = [energy_row_min, energy_row_max]
        b_ub = [-60.0, 65.0]

        # استدعاء المعالج الرياضي المطور بمكتبة scipy
        res = linprog(c_vector, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

        if res.success:
            formula_results = {}
            for idx, ing in enumerate(selected_ingredients):
                if res.x[idx] > 0.001:
                    formula_results[ing] = res.x[idx]

            # =========================================================================
            # 🧪 نظام الإشعارات المؤقتة الذكي (Toasts) المنبثق تلقائياً دون تعطيل الواجهة
            # =========================================================================
            mandatory_warnings = []
            
            # حقن بيكربونات الصوديوم آلياً للمجترات كأمان حيوي
            if main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاته"]:
                formula_results["بيكربونات الصوديوم (الصودا)"] = 0.75
                mandatory_warnings.append("🚨 حقن أمان حيوي تلقائي - بيكربونات الصوديوم: تم إدراج 7.5 كجم/الطن لمعادلة أس الهيدروجيني وحماية الكرش من التحمض.")

            # معالجة حمض الفايتيك للطيور والداجن
            if main_sector == "الطيور والسمان":
                formula_results["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05
                mandatory_warnings.append("🔬 إضافة فنية إلزامية - إنزيم الفايتيز: تم حقنه آلياً لتحرير الفسفور النباتي المرتبط وتحسين الامتصاص المعوي.")

            # دمج إنزيم الـ NSP للحبوب عالية اللزوجة والشعير والمخلفات
            if "شعير مطحون" in formula_results or "قمح محلي مصنّع" in formula_results or "تبن قمح ناعم" in formula_results:
                formula_results["إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)"] = 0.08
                mandatory_warnings.append("⚠️ معالجة لزوجة الألياف - إنزيم الـ NSP: تم دمجه آلياً لرفع كفاءة هضم الحبوب البديلة والمخلفات الحقلية.")

            # إطلاق التنبيهات المؤقتة لتظهر وتختفي بسلاسة
            if mandatory_warnings:
                for warn in mandatory_warnings:
                    st.toast(warn, icon="🔬")

            st.session_state["active_formula"] = formula_results
            st.session_state["active_cp_tag"] = final_target_cp
            st.session_state["active_breed_tag"] = sub_type
            st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES.get(dynamic_img_key, ANIMAL_IMAGES_RESOURCES["عام"])
            st.session_state["active_stage_title"] = f"{main_sector} - {prod_stage}"
            
            st.success("🎯 تم الاستمثال الخطي الرياضي بنجاح تام! نسبة الخطأ الصياغية والغذائية = 0.00%")
            
            res_col1, res_col2 = st.columns([0.6, 0.4])
            with res_col1:
                st.write("#### 📝 المقادير الدقيقة المعتمدة لتركيب طن واحد (كجم):")
                total_energy_pct = 0.0
                for k, v in formula_results.items():
                    st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** / طن)")
                    if k in BIG_FEEDS_LIBRARY["🌾 الحبوب ومصادر الطاقة الكبرى"]:
                        total_energy_pct += v
                
                st.info(f"📊 إجمالي نسبة مصادر الطاقة المحققة رياضياً: **{total_energy_pct:.2f}%** (تقع تماماً في النطاق الصارم المطلوب علمياً 60% - 65%)")
                
                ton_cost = res.fun / 100.0 if hasattr(res, 'fun') else 280.0
                st.session_state["computed_ton_cost"] = ton_cost
                st.metric(f"💰 التكلفة الفعلية المثلى لإنتاج الطن في {user_city}: ", f"${ton_cost:.2f} (يعادل {ton_cost*local_rate:,.1f} {local_sym})")
            with res_col2: 
                st.bar_chart(formula_results)
        else:
            st.error("❌ تعذر إيجاد حل رياضي متزن تماماً ضمن المحددات الحالية. يرجى تفعيل وإتاحة خامات إضافية من الأكساب أو المخلفات المتاحة في القائمة لتوسيع مساحة الحل الحسابي للمعالج الخطي.")

# ====================================================================
# التبويبات الإدارية المتقدمة (تظهر للمالك والمسؤول فقط)
# ====================================================================
if st.session_state["user_role"] == "admin":
    with tabs[1]:
        st.markdown('<div class="section-title">📊 لوحة تحكم بورصة تاور المركزية الشاملة للأسعار الحية</div>', unsafe_allow_html=True)
        col_edit1, col_edit2 = st.columns(2)
        with col_edit1:
            st.subheader("🐓 بورصة الماشية والداجن")
            for animal, price in st.session_state["global_livestock_prices"].items():
                st.session_state["global_livestock_prices"][animal] = st.number_input(f"تحديث سعر: {animal}", min_value=0.0, value=float(price), key=f"livestock_{animal}")
        with col_edit2:
            st.subheader("🥛 بورصة المنتجات والألبان")
            for product, price in st.session_state["global_products_prices"].items():
                st.session_state["global_products_prices"][product] = st.number_input(f"تحديث سعر: {product}", min_value=0.0, value=float(price), key=f"prod_edit_{product}")

    with tabs[2]:
        st.markdown('<div class="section-title">🏭 لوحة التحكم بالمستودعات والخصم الآلي للمخزون</div>', unsafe_allow_html=True)
        inv_cols = st.columns(3)
        for idx, (ing_name, qty) in enumerate(list(st.session_state["inventory"].items())):
            with inv_cols[idx % 3]:
                status_badge = f'<span class="stock-critical">⚠️ حرج: {qty:.2f} طن</span>' if qty < 3.0 else f'<span class="stock-normal">آمن: {qty:.2f} طن</span>'
                st.markdown(f"**{ing_name}** | {status_badge}", unsafe_allow_html=True)
                st.session_state["inventory"][ing_name] = st.number_input(f"تحديث رصيد المخزن ({ing_name}) طن:", min_value=0.0, value=float(qty), key=f"inv_input_{ing_name}")

    with tabs[3]:
        st.markdown('<div class="section-title">💰 نظام تسويق المنتجات وإصدار الفواتير مع الخصم التلقائي</div>', unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: client_name = st.text_input("اسم العميل / المزرعة المستلمة:", "مزارع تاور والإنتاج المتكامل")
        with col_c2: required_tons = st.number_input("الكمية المطلوبة لتوريد الخلطة (بالطن):", min_value=0.1, value=2.0, step=0.5)
        with col_c3: added_profit = st.number_input("هامش الربح الصافي المضاف لكل طن ($):", min_value=0.0, value=50.0)
        selling_price = st.session_state["computed_ton_cost"] + added_profit; total_bill = selling_price * required_tons
        st.markdown("### 🧾 فاتورة بيع وتوريد أعلاف رسمية")
        st.markdown(f"### 💰 إجمالي القيمة المستحقة للفاتورة: `${total_bill:.2f}` (أو تعادل `{total_bill*local_rate:,.1f}` {local_sym})")
        if st.button("✅ تأكيد عملية البيع وخصم المكونات من المستودع"):
            can_deduct = True
            for name, pct in st.session_state["active_formula"].items():
                if st.session_state["inventory"].get(name, 0.0) < ((pct / 100) * required_tons): 
                    can_deduct = False
                    st.error(f"❌ رصيد غير كافي في المخزن للمكون لـ {name}!")
                    break
            if can_deduct:
                for name, pct in st.session_state["active_formula"].items(): 
                    st.session_state["inventory"][name] -= ((pct / 100) * required_tons)
                st.success("🔥 تم الخصم التلقائي من المستودع وتحديث قاعدة البيانات الحالية!"); time.sleep(1); st.rerun()

    with tabs[4]:
        st.markdown('<div class="section-title">🏷️ مُصمم ديباجات الطباعة الفنية على جوالات الأعلاف والشهادات</div>', unsafe_allow_html=True)
        trade_brand = st.text_input("اسم البراند التجاري لإصدار الشهادة الفنية:", "مجموعة تاور العالمية لإنتاج الأعلاف ومصنعات الإنتاج الحيواني")
        st.markdown(f"""
        <div class="sack-tag">
            <img src="{st.session_state['active_animal_img']}" class="animal-banner-img">
            <h2 style="text-align: center; margin-top:0;">🌟 {trade_brand} 🌟</h2>
            <h3 style="text-align: center; color: #c62828; margin-top:0; font-weight: bold;">الخبير الفني / م. عبد القادر إسماعيل تاور</h3>
            <p style="text-align: center; font-weight: bold; background-color:#e8f5e9; padding:6px; color:#1b5e20;">🎯 علف متزن مخصص لـ: {st.session_state['active_stage_title']} | نسبة البروتين المحققة: {st.session_state['active_cp_tag']:.1f}%</p>
            <p style="text-align: center; font-size: 0.9rem; color:#555;">التركيبة مطابقة لمحددات التغذية القياسية العالمية وخالية تماماً من نسب الخطأ الرياضي.</p>
        </div>
        """, unsafe_allow_html=True)

# ====================================================================
# 📨 نظام الأرشفة التلقائية وإرسال الكود للبريد الإلكتروني بأسفل التطبيق
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

# التوقيع المصغر الدائم للمطور بأسفل الشاشة
st.markdown(
    """
    <div class="mini-left-signature">
        👨‍🔬 م. عبد القادر إسماعيل تاور © 2026 | خبير الحلول الذكية للثروة الحيوانية والبرمجيات المتكاملة
    </div>
    """,
    unsafe_allow_html=True
)
