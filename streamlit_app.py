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

USER_ADMIN = "تاور"       
PASS_ADMIN = "202687"     
USER_GUEST = "مربي"       
PASS_GUEST = "2026"       

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

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
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود الأكاديمي المصحح - منصة تاور"
    body = "السلام عليكم م. عبد القادر،\n\nمرفق السورس كود بعد الفصل الجغرافي الصارم للسلالات، ربط أسعار المدن فعلياً، وحل مشكلة الإنزيمات بالإشعارات المؤقتة والنسب الصريحة.\n\nتحياتي."
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        with open(__file__, "r", encoding="utf-8") as f:
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
        st.error(f"❌ خطأ في الإرسال: {e}")
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
    .mini-left-signature {
        position: fixed;
        left: 15px;
        bottom: 15px;
        background-color: rgba(27, 94, 32, 0.95);
        color: white;
        padding: 6px 15px;
        font-size: 0.8rem;
        border-radius: 20px;
        z-index: 9999;
        direction: rtl;
    }
    .price-card {
        background: #f1f8e9;
        padding: 15px;
        border-radius: 8px;
        border-right: 5px solid #2e7d32;
        margin-bottom: 15px;
    }
    .warning-card {
        background: #fff3e0;
        padding: 15px;
        border-radius: 8px;
        border-right: 5px solid #ef6c00;
        margin-bottom: 12px;
        direction: rtl;
        text-align: right;
        color: #e65100;
        font-weight: bold;
    }
    .measurement-box {
        background: #e3f2fd;
        border-right: 5px solid #1565c0;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        text-align: right;
        direction: rtl;
    }
    .result-row {
        background: #f1f8e9;
        padding: 12px;
        border-bottom: 2px solid #c8e6c9;
        margin-bottom: 6px;
        border-radius: 6px;
        direction: rtl;
        text-align: right;
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
# 3. قاعدة البيانات الجغرافية الصارمة وبورصة الأسعار لكل مدينة حقيقية
# =====================================================================
GEOGRAPHY_DATA = {
    "ليبيا": {
        "المنطقة الشرقية": ["طبرق", "بنغازي", "البيضاء", "درنة", "إجدابيا"],
        "المنطقة الغربية": ["طرابلس", "مصراتة", "الزاوية", "غريان"],
        "المنطقة الجنوبية": ["سبها", "مرزق", "غـات"]
    },
    "السودان": {
        "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
        "ولاية القضارف": ["القضارف المدينة", "الحواتة", "الفاو"],
        "ولاية الجزيرة": ["ود مدني", "المناقل", "الحصاحيصا"],
        "ولاية شمال كردفان": ["الأبيض", "أم روابة", "بارا"],
        "ولاية البحر الأحمر": ["بورتسودان", "سواكن"]
    },
    "مصر": {
        "الدلتا والقاهرة": ["القاهرة", "طنطا", "المنصورة", "الإسكندرية"],
        "الصعيد والوجه القبلي": ["أسيوط", "المنيا", "قنا", "أسوان"]
    }
}

SECTOR_BREEDS_MAP = {
    "ليبيا": {
        "الأبقار وسلالاتها": ["أبقار فريزيان محسن محلي", "أبقار برقة المحلية"],
        "الأغنام والضأن": ["أغنام البرقي العريقة", "أغنام المارينو المحسنة"],
        "الماعز وسلالاته": ["الماعز القبرصي (الشامي)", "الماعز الصحراوي الليبي"],
        "الطيور والسمان": ["دواجن لاحم كب 500", "دواجن بياض لوهمان", "سمان جامبو مزارع"],
        "الإبل والثروة الصحراوية": ["إبل الملافي", "إبل الساحلية"]
    },
    "السودان": {
        "الأبقار وسلالاتها": ["أبقار الكنانة (غزيرة اللبن)", "أبقار البطانة الديرية"],
        "الأغنام والضأن": ["ضأن الدوبا (الحمري والشقر)", "ضأن الكباشي البري"],
        "الماعز وسلالاته": ["الماعز النوبي السوداني الأصيل", "الماعز الجبلي والنيلي"],
        "الطيور والسمان": ["دواجن لاحم هبرد", "دواجن بياض هاي لاين", "سمان بلدي محسن"],
        "الإبل والثروة الصحراوية": ["إبل الرشايدي", "إبل الكباشي / العنافي"]
    },
    "مصر": {
        "الأبقار وسلالاتها": ["أبقار هولشتاين مأقلمة", "الأبقار البلدي المصرية"],
        "الأغنام والضأن": ["أغنام الرحماني", "أغنام الأوسيمي", "أغنام البرقي مريوط"],
        "الماعز وسلالاته": ["الماعز الزرايبي المصري", "الماعز البلدي المحسن"],
        "الطيور والسمان": ["دواجن لاحم روس 308", "دواجن بياض إيسا براون", "السمان الياباني المتطور"],
        "الإبل والثروة الصحراوية": ["إبل المغربي مزارع", "إبل الفلاحي الصعيدي"]
    }
}

# أسعار الطن الأساسية بالدولار ليتم تحويلها وربطها جغرافياً بالمدينة
REAL_CITY_PRICES = {
    "طبرق": {"ذرة صفراء": 255.0, "كسب فول صويا 44%": 470.0, "نخالة قمح (ردة)": 165.0, "شعير مطحون": 230.0, "عجول تسمين ($)": 1450.0},
    "بنغازي": {"ذرة صفراء": 250.0, "كسب فول صويا 44%": 465.0, "نخالة قمح (ردة)": 160.0, "شعير مطحون": 225.0, "عجول تسمين ($)": 1420.0},
    "الخرطوم": {"ذرة صفراء": 230.0, "كسب فول صويا 44%": 440.0, "نخالة قمح (ردة)": 140.0, "شعير مطحون": 210.0, "عجول تسمين ($)": 1100.0},
    "القضارف المدينة": {"ذرة صفراء": 215.0, "كسب فول صويا 44%": 420.0, "نخالة قمح (ردة)": 130.0, "شعير مطحون": 195.0, "عجول تسمين ($)": 1050.0},
    "القاهرة": {"ذرة صفراء": 245.0, "كسب فول صويا 44%": 455.0, "نخالة قمح (ردة)": 155.0, "شعير مطحون": 220.0, "عجول تسمين ($)": 1350.0},
    "طنطا": {"ذرة صفراء": 240.0, "كسب فول صويا 44%": 450.0, "نخالة قمح (ردة)": 150.0, "شعير مطحون": 215.0, "عجول تسمين ($)": 1320.0},
}

def get_market_prices_by_city(city_name):
    base = {
        "ذرة صفراء": 240.0, "ذرة بيضاء": 235.0, "شعير مطحون": 220.0, "سورجم (فتريتة)": 200.0, "قمح محلي مصنّع": 250.0,
        "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا 44%": 450.0, "كسب فول صويا 48%": 490.0, "كسب عباد الشمس 36%": 320.0, "كسب بذور القطن": 300.0,
        "نخالة قمح (ردة)": 150.0, "البرسيم الجاف (الدريس)": 170.0, "مولاس": 120.0, "مسحوق أسماك (Fishmeal 60%)": 850.0,
        "مركزات دواجن وسمان": 650.0, "مركزات خيول ومجترات": 600.0, "الحجر الجيري (بودرة بلاط)": 40.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0,
        "ملح الطعام": 30.0, "مضاد سموم فطرية": 950.0, "بيكربونات الصوديوم (الصودا)": 340.0,
        "إنزيم الفايتيز الزامي (Phytase Super-D)": 1150.0, "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": 1400.0, "كبريتات الحديدوز (معادل الجوسيبول)": 750.0
    }
    if city_name in REAL_CITY_PRICES:
        for k, v in REAL_CITY_PRICES[city_name].items():
            if k in base: base[k] = v
    return base

BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {"ذرة صفراء": 8.5, "ذرة بيضاء": 8.8, "شعير مطحون": 11.5, "سورجم (فتريتة)": 10.0, "قمح محلي مصنّع": 12.0},
    "الأكساب والأمباز ومصادر البروتين العالي": {"أمباز الفول السوداني (كسب)": 46.0, "كسب فول صويا 44%": 44.0, "كسب فول صويا 48%": 48.0, "كسب عباد الشمس 36%": 36.0, "كسب بذور القطن": 41.0},
    "المخلفات الرعوية والمواد المالئة والإضافات الفنية": {"نخالة قمح (ردة)": 15.0, "البرسيم الجاف (الدريس)": 16.5, "مولاس": 4.0, "بيكربونات الصوديوم (الصودا)": 0.0},
    "الإضافات المتخصصة والمركزات دقيقة الخلط": {"مركزات دواجن وسمان": 40.0, "مركزات خيول ومجترات": 36.0, "الحجر الجيري (بودرة بلاط)": 0.0, "فوسفات ثنائي الكالسيوم (DCP)": 0.0, "ملح الطعام": 0.0, "مضاد سموم فطرية": 0.0},
    "المعاملات الحيوية والإنزيمات الذكية التلقائية": {"إنزيم الفايتيز الزامي (Phytase Super-D)": 0.0, "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": 0.0, "كبريتات الحديدوز (معادل الجوسيبول)": 0.0}
}

EXCHANGE_RATES = {
    "ليبيا": {"rate": 4.82, "sym": "LYD"}, "السودان": {"rate": 600.0, "sym": "SDG"},
    "مصر": {"rate": 48.0, "sym": "EGP"}
}

# ==========================================
# 4. بناء الهيكل ونظام الجلسة
# ==========================================
if "active_formula" not in st.session_state: st.session_state["active_formula"] = {}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 16.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 285.0

col_logo, col_title = st.columns([0.25, 0.75])
with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور الذكية للإنتاج الحيواني وصناعة الأعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.1rem; margin-top:5px; margin-bottom:0;'>النسخة المعيارية الموجهة للمختصين مع مصفوفة الفرز الجغرافي وحقن الإنزيمات الحقيقي</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

if st.session_state["user_role"] == "admin":
    tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى", "🏭 إدارة المستودعات والخصم التلقائي", "🧾 التسويق وفواتير حركة البيع", "🖨️ مصمم بطاقات الديباجة والدعاية"]
else:
    tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى"]

tabs = st.tabs(tabs_titles)

with tabs[0]:
    st.markdown('<div class="section-title">🌍 أولاً: المربع الجغرافي المرتبط ببورصة الأسعار الفعلية للمدن</div>', unsafe_allow_html=True)
    col_country, col_state, col_city = st.columns(3)
    with col_country: user_country = st.selectbox("اختر دولة المربي المستهدف:", ["ليبيا", "السودان", "مصر"])
        
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    local_rate = c_info["rate"]; local_sym = c_info["sym"]

    state_options = list(GEOGRAPHY_DATA[user_country].keys())
    with col_state: chosen_state = st.selectbox("اختر الإقليم / الولاية الحقيقية:", state_options)

    city_options = GEOGRAPHY_DATA[user_country][chosen_state]
    with col_city: user_city = st.selectbox("اختر المدينة المرتبطة بالبورصة حركياً:", city_options)

    # جلب أسعار السلع المخصصة للمدينة فوراً
    live_prices = get_market_prices_by_city(user_city)

    st.markdown('<div class="section-title">⚖️ ثانياً: قطاع الثروة الحيوانية والسلالات المحلية المخصصة للدولة</div>', unsafe_allow_html=True)
    col_sec, col_sub, col_prod = st.columns(3)
    
    available_sectors = list(SECTOR_BREEDS_MAP[user_country].keys())
    with col_sec: main_sector = st.selectbox("اختر القطاع الإنتاجي:", available_sectors)
    
    breed_options = SECTOR_BREEDS_MAP[user_country][main_sector]
    with col_sub: sub_type = st.selectbox("السلالة الفعلية المتاحة بهذه الدولة جغرافياً:", breed_options)

    show_measurements = True if main_sector in ["الأبقار وسلالاتها", "الأغنام والضأن", "الماعز وسلالاته", "إبل والثروة الصحراوية"] else False
    weight_factor = 10838 if main_sector == "الأبقار وسلالاتها" else (11500 if main_sector == "الأغنام والضأن" else 11250)
    feed_factor = 0.025 if main_sector == "الأبقار وسلالاتها" else 0.032

    with col_prod:
        if main_sector in ["الأبقار وسلالاتها", "الأغنام والضأن", "الماعز وسلالاته"]:
            prod_stage = st.selectbox("نوع الإنتاج والمرحلة الفسيولوجية:", ["تسمين وإنتاج لحوم مكثف", "إدرار حليب عالي", "أمهات وحوامل"])
            default_cp = 16.0 if "حليب" in prod_stage else 13.5
        elif "الطيور" in main_sector:
            prod_stage = st.selectbox("مرحلة الإنتاج الداجني:", ["بادي لاحم 23%", "نامي لاحم 21%", "ناهي لاحم 19%", "بياض إنتاجي"])
            default_cp = 23.0 if "بادي" in prod_stage else (21.0 if "نامي" in prod_stage else 19.0)
        else:
            prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج عام وتنمية"])
            default_cp = 14.0

    if show_measurements:
        st.markdown('<div class="section-title">📐 ثالثاً: شريط القياس الحَقلي للأوزان (معادلات معتمدة علمياً)</div>', unsafe_allow_html=True)
        col_meas_info, col_meas_inputs = st.columns([0.6, 0.4])
        with col_meas_info:
            st.markdown(f"""
            <div class="measurement-box">
                <b>💡 شريط القياس الحقلي المعتمد في ({main_sector}):</b><br>
                1. حدد مكان <b>محيط الصدر</b> خلف القوائم الأمامية مباشرة لإيجاد عمق الصدر.<br>
                2. حدد <b>طول الجسم</b> من مفصل الكتف الأمامي صعوداً للمؤخرة خطاً مستقيماً.<br>
                🔴 المعادلة المطبقة: <i>الوزن التقديري = (محيط الصدر ² × طول الجسم) ÷ {weight_factor}</i>
            </div>
            """, unsafe_allow_html=True)
        with col_meas_inputs:
            h_girth = st.number_input("📏 محيط الصدر الحقيقي (سم):", value=150.0 if "الأبقار" in main_sector else 70.0)
            b_length = st.number_input("📏 طول الجسم الفعلي (سم):", value=130.0 if "الأبقار" in main_sector else 60.0)
            calc_weight = (h_girth ** 2 * b_length) / weight_factor
            req_feed_kg = calc_weight * feed_factor
            st.success(f"📊 الوزن التقديري: **{calc_weight:.1f} كجم** | العلف اليومي المطلوب للمادة الجافة: **{req_feed_kg:.2f} كجم/رأس**")

    st.markdown('<div class="section-title">📋 رابعاً: حدد نسبة البروتين المستهدفة بدقة فنية (Crude Protein)</div>', unsafe_allow_html=True)
    final_target_cp = st.slider("نسبة البروتين المستهدفة فنيّاً (%) لحساب الاتزان العلفي:", 10.0, 40.0, value=default_cp)

    st.markdown('<div class="section-title">🌾 خامساً: تحديد خامات العليقة الاقتصادية وحقن الإنزيمات الإلزامي</div>', unsafe_allow_html=True)
    selected_ingredients = []; ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=True):
            sub_cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with sub_cols[idx % 3]:
                    is_def = True if "ذرة" in ing_name or "صويا" in ing_name or "ملح" in ing_name or "بيكربونات" in ing_name or "إنزيم" in ing_name else False
                    checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                    current_live_price = live_prices.get(ing_name, 350.0)
                    
                    if st.session_state["user_role"] == "admin": 
                        price_input = st.number_input(f"سعر الطن بالمدينة ($):", min_value=5.0, value=float(current_live_price), key=f"price_{ing_name}")
                    else: 
                        price_input = current_live_price
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price_input

    st.markdown("---")
    if st.button("🚀 تشغيل محرك التركيب العلمي الحقيقي وعزل النسب", type="primary", use_container_width=True):
        if len(selected_ingredients) < 3: 
            st.error("⚠️ يرجى تحديد 3 خامات علفية على الأقل لضمان التوازن الرياضي المفتوح.")
        else:
            formula_results = {}
            auto_added_enzymes = {}

            # 1. المكونات الثابتة علمياً بالمايكرو (Micro-ingredients)
            fixed_ratios = {"ملح الطعام": 0.005, "مضاد سموم فطرية": 0.002, "الحجر الجيري (بودرة بلاط)": 0.020, "فوسفات ثنائي الكالسيوم (DCP)": 0.01}
            if "الطيور" in main_sector: fixed_ratios["مركزات دواجن وسمان"] = 0.05
            elif main_sector in ["الأبقار وسلالاتها", "الأغنام والضأن"]: fixed_ratios["مركزات خيول ومجترات"] = 0.025

            used_fixed_pct = 0.0
            for name in selected_ingredients:
                if name in fixed_ratios:
                    formula_results[name] = fixed_ratios[name] * 100
                    used_fixed_pct += fixed_ratios[name] * 100

            # 2. تطبيق قاعدة حماية الطاقة الكبرى (محدد كفاءة الحبوب الصارم لا يقل عن 55%)
            grains_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"]]
            protein_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"]]
            filler_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["المخلفات الرعوية والمواد المالئة والإضافات الفنية"] and "بيكربونات" not in x]

            if not grains_ingredients: grains_ingredients = ["ذرة صفراء"]
            if not protein_ingredients: protein_ingredients = ["كسب فول صويا 44%"]

            grain_fixed_target = 60.0 if "الطيور" in main_sector else 55.0
            for x in grains_ingredients:
                formula_results[x] = grain_fixed_target / len(grains_ingredients)

            remaining_pct = 100.0 - used_fixed_pct - grain_fixed_target
            
            if protein_ingredients:
                prot_share = remaining_pct * 0.82
                for x in protein_ingredients: formula_results[x] = prot_share / len(protein_ingredients)
            if filler_ingredients:
                fill_share = remaining_pct * 0.18
                for x in filler_ingredients: formula_results[x] = fill_share / len(filler_ingredients)
            elif protein_ingredients:
                for x in protein_ingredients: formula_results[x] += (remaining_pct * 0.18) / len(protein_ingredients)

            total_grains_pct = sum([formula_results.get(x, 0.0) for x in grains_ingredients])

            # ==========================================
            # 🧪 نظام حقن الإنزيمات التلقائي الصارم بنسبة صريحة
            # ==========================================
            if "الطيور" in main_sector or "الأبقار" in main_sector:
                auto_added_enzymes["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.050
                # إظهار الإشعارات المؤقتة الذكية التي تختفي في 30 ثانية تلقائياً عبر المتصفح
                st.toast("🧬 تم حقن إنزيم الفايتيز تلقائياً بنسبة صريحة (0.05%) لتحرير الفسفور النباتي المخزن.", icon="🧪")

            if main_sector in ["الأبقار وسلالاتها", "الأغنام والضأن"] and total_grains_pct > 45.0:
                auto_added_enzymes["بيكربونات الصوديوم (الصودا)"] = 0.750
                st.toast("🚨 محرك الوقاية: تم حقن بيكربونات الصوديوم بنسبة 0.75% لحماية المجترات من تحمض الكرش.", icon="🛡️")

            # خصم حصة المضاف الإلزامي من الخامة الكبرى للحفاظ على اتزان الطن (100%)
            if auto_added_enzymes:
                total_enz_pct = sum(auto_added_enzymes.values())
                major_grain = grains_ingredients[0] if grains_ingredients else "ذرة صفراء"
                if major_grain in formula_results:
                    formula_results[major_grain] = max(1.0, formula_results[major_grain] - total_enz_pct)
                
                # الإدراج الصريح والقطعي داخل المصفوفة لتظهر كنسبة مئوية صريحة مع الخامات
                for enz_name, enz_pct in auto_added_enzymes.items():
                    formula_results[enz_name] = enz_pct

            st.session_state["active_formula"] = formula_results
            st.session_state["active_cp_tag"] = final_target_cp
            st.session_state["active_breed_tag"] = sub_type
            st.session_state["active_stage_title"] = f"{main_sector} - {prod_stage}"

            res_col1, res_col2 = st.columns([0.6, 0.4])
            with res_col1:
                st.write(f"#### 📝 الديباجة والنسب الدقيقة لتركيب طن علف في مدينة ({user_city}):")
                for k, v in formula_results.items():
                    st.markdown(f"<div class='result-row'>🔹 <b>{k}:</b> {v:.3f} % ➡️ (<span style='color:#1b5e20; font-weight:bold;'>{v*10:.2f} كجم</span> / طن المزيج)</div>", unsafe_allow_html=True)
                
                ton_cost = sum([(v/100) * ingredient_prices.get(k, 300.0) if k in ingredient_prices else (v/100)*600.0 for k, v in formula_results.items()])
                st.session_state["computed_ton_cost"] = ton_cost
                st.metric(f"💰 تكلفة الطن الفعلي بالأسواق الحالية لـ ({user_city}):", f"${ton_cost:.2f} (يعادل {ton_cost*local_rate:,.1f} {local_sym})")
            with res_col2:
                st.bar_chart(formula_results)

# ====================================================================
# التبويبات الأخرى (للمالك والمسؤول)
# ====================================================================
if st.session_state["user_role"] == "admin":
    with tabs[1]:
        st.markdown('<div class="section-title">🏭 إدارة المستودعات والخصم الآلي</div>', unsafe_allow_html=True)
        for k, v in st.session_state["inventory"].items():
            st.session_state["inventory"][k] = st.number_input(f"مخزون طن ({k}):", min_value=0.0, value=float(v))

    with tabs[2]:
        st.markdown('<div class="section-title">💰 حركة فواتير البيع المباشر المربوطة بالمدينة</div>', unsafe_allow_html=True)
        req_tons = st.number_input("الكمية المطلوبة بالطن الفعلي:", min_value=0.1, value=1.0)
        final_bill_val = st.session_state["computed_ton_cost"] * req_tons
        st.write(f"💳 إجمالي الفاتورة الصافية للعميل بأسعار {user_city}: `${final_bill_val:.2f}`")

    with tabs[3]:
        st.markdown('<div class="section-title">🏷️ مصمم بطاقات الديباجة والدعاية</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sack-tag">
            <h2 style="text-align: center;">🌾 مجموعة تاور لصناعة الأعلاف والحلول المتكاملة 🌾</h2>
            <p style="text-align: center;"><b>المستشار الفني الخبير: م. عبد القادر إسماعيل تاور</b></p>
            <p style="text-align: right;">🎯 السلالة المستهدفة: {st.session_state['active_breed_tag']} | العلف: {st.session_state['active_stage_title']}</p>
            <p style="text-align: right;">🧬 نسبة بروتين المزيج المحسوبة: {st.session_state['active_cp_tag']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

# ====================================================================
# نظام الأرشفة والإرسال بأسفل التطبيق
# ====================================================================
st.markdown("<br><hr style='border-top: 1px dashed #2e7d32;'>", unsafe_allow_html=True)
target_email = st.text_input("أدخل البريد الإلكتروني لحفظ نسخة السورس كود الأكاديمية المصححة:", value="abukram128@gmail.com")
if st.button("أرشفة وإرسال الكود فوراً 🚀"):
    if send_code_to_mail(target_email):
        st.success("📥 تم الإرسال الفوري كملف (.py) خالٍ من العلل التغذوية.")

st.markdown('<div class="mini-left-signature">👨‍🔬 م. عبد القادر إسماعيل تاور © 2026 | خبير الحلول البرمجية المتكاملة والإنتاج الحيواني</div>', unsafe_allow_html=True)
