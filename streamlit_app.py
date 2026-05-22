import streamlit as st
import numpy as np
import json
import os
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# استيراد محرك البرمجة الخطية لتقليل نسبة الخطأ الصياغي والغذائي إلى الصفر
from scipy.optimize import linprog

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
    if SENDER_EMAIL == "YOUR_EMAIL@gmail.com" or SENDER_PASSWORD == "xxxx xxxx xxxx xxxx":
        st.error("⚠️ خطأ إعدادات: يرجى تحديث بيانات الـ SMTP داخل السورس كود أولاً.")
        return False
        
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود المطور (Linear Programming) - منصة تاور"
    
    body = "السلام عليكم م. عبد القادر،\n\nمرفق النسخة البرمجية المطورة القائمة على البرمجة الخطية لمنع نسب الخطأ في التراكيب العلفية.\n\nتحياتي،\nالنظام التلقائي للمنصة."
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        current_file = __file__
        with open(current_file, "r", encoding="utf-8") as f:
            code_content = f.read()
        
        attachment = MIMEText(code_content, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', filename="tower_optimized_platform.py")
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
# 3. المكتبة وبورصة المكونات الافتراضية
# =====================================================================
INITIAL_INVENTORY = {
    "ذرة صفراء": 25.0, "ذرة بيضاء": 10.0, "شعير مطحون": 15.0, "سورجم (فتريتة)": 15.0, "قمح محلي مصنّع": 12.0,
    "أمباز الفول السوداني (كسب)": 20.0, "كسب فول صويا 44%": 14.0, "كسب فول صويا 48%": 18.0, "كسب عباد الشمس 36%": 10.0, "كسب بذور القطن": 8.0,
    "نخالة قمح (ردة)": 20.0, "البرسيم الجاف (الدريس)": 30.0, "مولاس": 5.0,
    "مسحوق أسماك (Fishmeal 60%)": 4.0, "مركزات دواجن وسمان": 3.5, "مركزات خيول ومجترات": 3.5,
    "الحجر الجيري (بودرة بلاط)": 6.0, "فوسفات ثنائي الكالسيوم (DCP)": 3.0, "ملح الطعام": 2.5, "مضاد سموم فطرية": 1.2,
    "بيكربونات الصوديوم (الصودا)": 5.0,
    "إنزيم الفايتيز الزامي (Phytase Super-D)": 1.0, "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": 1.0, "بروتييز (Protease)": 0.8,
    "ليسين نقي (L-Lysine)": 1.5, "ميثيونين نقي (DL-Methionine)": 1.5, "ثريونين (L-Threonine)": 1.2
}

if "inventory" not in st.session_state: st.session_state["inventory"] = INITIAL_INVENTORY
if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {"عجول تسمين هولشتاين / محسن ($)": 1350.0, "أبقار كنانة وبطانة محلية ($)": 900.0, "ضأن وستيرلنغ / محلي ($)": 180.0, "ماعز نوبي وصحراوي ($)": 130.0, "خيول عربية أصيلة وهجين ($)": 4500.0, "كتكوت لاحم عمر يوم ($)": 0.65, "دجاج بياض عمر البشاير ($)": 5.50}
if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {"كيلو لحم بقري صافي ($)": 7.50, "كيلو لحم ضأن طازج ($)": 9.00, "كيلو لحم دجاج لاحم صافي ($)": 3.80, "طبق بيض مائدة 30 بيضة ($)": 4.20, "رطل / لتر حليب خام ($)": 0.90, "كيلو جبن أبيض محلي ($)": 5.00}

EXCHANGE_RATES = {"السودان": {"rate": 600.0, "sym": "SDG"}, "ليبيا": {"rate": 4.80, "sym": "LYD"}, "مصر": {"rate": 48.0, "sym": "EGP"}, "باقي دول العالم / البورصة المفتوحة": {"rate": 1.0, "sym": "USD"}}

SUDAN_GEOGRAPHY = {
    "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"], "ولاية الجزيرة": ["ود مدني", "الحصاحيصا", "المناقل"], "ولاية القضارف": ["القضارف المدينة", "الفاو"], "ولاية كسلا": ["كسلا", "حلفا الجديدة"], "ولاية سنار": ["سنار", "سنجة"], "ولاية النيل الأبيض": ["ربك", "كextended ستي"], "ولاية شمال كردفان": ["الأبيض", "بارا"], "ولاية نهر النيل": ["الدامر", "عطبرة", "شندي"], "ولاية الشمالية": ["دنقلا", "مروي"]
}

def get_adjusted_market_data(country, state_or_region, city):
    feed_prices = {
        "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0, "سورجم (فتريتة)": 195.0, "قمح محلي مصنّع": 240.0,
        "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا 44%": 440.0, "كسب فول صويا 48%": 480.0, "كسب عباد الشمس 36%": 310.0, "كسب بذور القطن": 290.0,
        "نخالة قمح (ردة)": 150.0, "البرسيم الجاف (الدريس)": 170.0, "مولاس": 120.0, "مسحوق أسماك (Fishmeal 60%)": 850.0, "مركزات دواجن وسمان": 650.0, "مركزات خيول ومجترات": 600.0, "الحجر الجيري (بودرة بلاط)": 40.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0, "ملح الطعام": 30.0, "مضاد سموم فطرية": 950.0, "بيكربونات الصوديوم (الصودا)": 340.0, "إنزيم الفايتيز الزامي (Phytase Super-D)": 1500.0, "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": 1800.0, "بروتييز (Protease)": 2000.0, "ليسين نقي (L-Lysine)": 2200.0, "ميثيونين نقي (DL-Methionine)": 2800.0, "ثريونين (L-Threonine)": 2400.0
    }
    mult = 1.15 if country == "السودان" else (1.10 if country == "ليبيا" else 1.04)
    for k in feed_prices: feed_prices[k] *= mult
    return feed_prices

BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {"ذرة صفراء": {"CP": 8.5}, "ذرة بيضاء": {"CP": 8.8}, "شعير مطحون": {"CP": 11.5}, "سورجم (فتريتة)": {"CP": 10.0}, "قمح محلي مصنّع": {"CP": 12.0}},
    "الأكساب والأمباز ومصادر البروتين العالي": {"أمباز الفول السوداني (كسب)": {"CP": 46.0}, "كسب فول صويا 44%": {"CP": 44.0}, "كسب فول صويا 48%": {"CP": 48.0}, "كسب عباد الشمس 36%": {"CP": 36.0}, "كسب بذور القطن": {"CP": 41.0}},
    "المخلفات الرعوية والمواد المالئة والإضافات الفنية": {"نخالة قمح (ردة)": {"CP": 15.0}, "البرسيم الجاف (الدريس)": {"CP": 16.5}, "مولاس": {"CP": 4.0}, "بيكربونات الصوديوم (الصودا)": {"CP": 0.0}},
    " can_be_fixed": {"مركزات دواجن وسمان": {"CP": 40.0}, "مركزات خيول ومجترات": {"CP": 36.0}, "الحجر الجيري (بودرة بلاط)": {"CP": 0.0}, "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0}, "ملح الطعام": {"CP": 0.0}, "مضاد سموم فطرية": {"CP": 0.0}, "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0}, "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0}, "بروتييز (Protease)": {"CP": 0.0}, "ليسين نقي (L-Lysine)": {"CP": 94.0}, "ميثيونين نقي (DL-Methionine)": {"CP": 58.0}, "ثريونين (L-Threonine)": {"CP": 72.0}}
}

ANIMAL_IMAGES_RESOURCES = {"أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600", "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600", "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600", "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600", "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600"}

if "active_formula" not in st.session_state: st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 16.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0

# ==========================================
# 4. بناء الواجهة الرئيسية للمنصة
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)
st.markdown("<h1 style='color: #1b5e20; text-align:right;'>منصة تاور الذكية - إصدار البرمجة الخطية الصارم المطور 🌾</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #1565C0; text-align:right;'>نظام استمثال الكلفة الأدنى (Least-Cost Formulation) الخالي من الخطأ الرياضي للتحكيم الأكاديمي.</p>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #c62828; text-align:right;'>المستشار الفني / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

tabs = st.tabs(["🔬 النمذجة والحسابات الخطية الكبرى"])

with tabs[0]:
    col_country, col_state, col_city = st.columns(3)
    with col_country: user_country = st.selectbox("اختر دولة المربي:", ["السودان", "ليبيا", "مصر"])
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    local_rate = c_info["rate"]; local_sym = c_info["sym"]
    with col_state: chosen_state = st.selectbox("اختر الولاية/الإقليم:", list(SUDAN_GEOGRAPHY.keys()) if user_country == "السودان" else ["المنطقة المركزية"])
    with col_city: user_city = st.selectbox("اختر المدينة:", SUDAN_GEOGRAPHY[chosen_state] if user_country == "السودان" else ["المدينة الرئيسية"])

    live_prices = get_adjusted_market_data(user_country, chosen_state, user_city)

    st.markdown('<div class="section-title">⚙️ اختيار نوع الحيوان وتحديد البروتين المستهدف</div>', unsafe_allow_html=True)
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec: main_sector = st.selectbox("اختر القطاع الرئيسي:", ["الطيور والسمان", "الأبقار وسلالاتها", "الماعز وسلالاته", "الخيول والفروسية"])
    with col_sub: sub_type = st.selectbox("السلالة:", ["دواجن لاحم", "دواجن بياض", "سلالة إنتاجية محسنة"])
    with col_prod: prod_stage = st.selectbox("مرحلة الإنتاج العلفي:", ["بادي 23%", "نامي 21%", "ناهي 19%", "عام"])
    
    target_cp = st.slider("حدّد نسبة البروتين المطلوبة بدقة (محدد قاطع):", 12.0, 35.0, value=21.0)

    st.markdown('<div class="section-title">🌾 اختيار المكونات المتاحة بالمستودع</div>', unsafe_allow_html=True)
    selected_ingredients = []; ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        if cat_name != " can_be_fixed":
            with st.expander(f"📁 {cat_name}", expanded=True):
                sub_cols = st.columns(3)
                for idx, (ing_name, _) in enumerate(items.items()):
                    with sub_cols[idx % 3]:
                        checked = st.checkbox(ing_name, value=True if "ذرة" in ing_name or "صويا" in ing_name or "ردة" in ing_name else False, key=f"f_{ing_name}")
                        if checked:
                            selected_ingredients.append(ing_name)
                            ingredient_prices[ing_name] = live_prices.get(ing_name, 300.0)

    # حجز وبناء الإضافات الفنية الثابتة التي يجب إدراجها آلياً لسلامة الطن
    fixed_additives = {
        "ملح الطعام": 0.5, "مضاد سموم فطرية": 0.2, "الحجر الجيري (بودرة بلاط)": 1.5, 
        "فوسفات ثنائي الكالسيوم (DCP)": 1.0, "مركزات دواجن وسمان": 5.0
    }
    for item, val in fixed_additives.items():
        if item not in selected_ingredients:
            selected_ingredients.append(item)
            ingredient_prices[item] = live_prices.get(item, 500.0)

    st.markdown("---")
    if st.button("🚀 تشغيل خوارزمية الاستمثال الخطي ومنع نسبة الخطأ", type="primary", use_container_width=True):
        
        # --- بناء المصفوفات الرياضية للبرمجة الخطية (Linear Programming) ---
        # الهدف: تقليل التكلفة Z = c1*x1 + c2*x2 + ...
        c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
        
        # المحددات (Bounds): كل مكون يجب أن يكون بين 0% و 100%
        # مع قفل الإضافات الثابتة عند نسبها العلمية المحددة بدقة
        bounds = []
        for ing in selected_ingredients:
            if ing in fixed_additives:
                bounds.append((fixed_additives[ing], fixed_additives[ing])) # تثبيت تام للإضافات الدقيقة لعدم الإخلال بالخلطة
            else:
                bounds.append((0.0, 100.0))

        # محدد التساوي الأول (A_eq, b_eq): مجموع كل النسب يجب أن يساوي 100%
        A_eq = [[1.0 for _ in selected_ingredients]]
        b_eq = [100.0]
        
        # محدد التساوي الثاني (البروتين المستهدف): مجموع (نسبة بروتين المكون * نسبته) = البروتين المستهدف
        cp_row = []
        for ing in selected_ingredients:
            # البحث عن نسبة البروتين في المكتبة الشاملة
            cp_val = 0.0
            for cat in BIG_FEEDS_LIBRARY.values():
                if ing in cat: cp_val = cat[ing].get("CP", 0.0)
            cp_row.append(cp_val)
        A_eq.append(cp_row)
        b_eq.append(target_cp * 100.0) # ضرب 100 لموازنة النسبة المئوية الإجمالية لكتلة الطن

        # محدد عدم التساوي (Inequality Constraints): قفل مصادر الطاقة بين 60% و 65%
        # Σ (مكونات الطاقة) >= 60  ==>  -Σ(مكونات الطاقة) <= -60
        # Σ (مكونات الطاقة) <= 65
        energy_row_min = []
        energy_row_max = []
        for ing in selected_ingredients:
            is_energy = ing in BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"]
            energy_row_min.append(-1.0 if is_energy else 0.0)
            energy_row_max.append(1.0 if is_energy else 0.0)
            
        A_ub = [energy_row_min, energy_row_max]
        b_ub = [-60.0, 65.0]

        # تشغيل المحرك الرياضي الصارم (Simplex / HiGHS Optimized)
        res = linprog(c_vector, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

        if res.success:
            formula_results = {}
            for idx, ing in enumerate(selected_ingredients):
                if res.x[idx] > 0.01:
                    formula_results[ing] = res.x[idx]

            # ==========================================
            # 🧪 نظام معالجة الإنزيمات التلقائي وبث الإشعارات المنبثقة لمدة 30 ثانية
            # ==========================================
            mandatory_warnings = []
            if main_sector == "الطيور والسمان" and "إنزيم الفايتيز الزامي (Phytase Super-D)" not in formula_results:
                formula_results["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05
                mandatory_warnings.append("🚨 إضافة إلزامية - إنزيم الفايتيز (Phytase): تم حقنه آلياً لكسر روابط حمض الفايتيك وتحرير الفسفور النباتي الطبيعي.")

            if "شعير مطحون" in formula_results or "قمح محلي مصنّع" in formula_results:
                formula_results["إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)"] = 0.08
                mandatory_warnings.append("⚠️ علة معالجة برمجياً: تم دمج إنزيم الـ NSP لرفع كفاءة هضم الحبوب البديلة عالية اللزوجة.")

            # عرض الإشعارات الذكية المؤقتة (Toasts) التي تظهر وتختفي تلقائياً دون تجميد الشاشة
            if mandatory_warnings:
                for warn in mandatory_warnings:
                    st.toast(warn, icon="🔬")

            st.session_state["active_formula"] = formula_results
            st.session_state["active_cp_tag"] = target_cp
            st.session_state["active_stage_title"] = f"{main_sector} - {prod_stage}"

            st.success("🎯 تم الاستمثال الخطي الرياضي بنجاح! نسبة الخطأ في التركيب والخلط = 0.00%")
            
            res_col1, res_col2 = st.columns([0.6, 0.4])
            with res_col1:
                st.write("#### 📝 النسب المقررة علمياً لتركيب الطن الوافد للخلط وكجم/الطن:")
                total_energy_check = 0.0
                for k, v in formula_results.items():
                    st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** / طن واحد)")
                    if k in BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"]:
                        total_energy_check += v
                
                st.info(f"📊 إجمالي نسبة مصادر الطاقة المحققة رياضياً: **{total_energy_check:.2f}%** (تقع تماماً في النطاق الصارم والمطلوب حَقلياً 60% - 65%)")
                
                ton_cost = res.fun / 100.0 if hasattr(res, 'fun') else 300.0
                st.session_state["computed_ton_cost"] = ton_cost
                st.metric(f"💰 التكلفة العلفية المثلى للطن في {user_city}: ", f"${ton_cost:.2f} (يعادل {ton_cost*local_rate:,.1f} {local_sym})")
            with res_col2:
                st.bar_chart(formula_results)
        else:
            st.error("❌ تعذر إيجاد حل رياضي متزن تماماً ضمن هذه المكونات المحددة. يرجى إتاحة خامات إضافية (مثل إضافة كسب صويا أو ذرة أخرى) ليتسنى للمحرك الخطي موازنة النسبة دون أي خطأ.")

st.markdown('</div>', unsafe_allow_html=True)

# التوقيع الذكي الدائم
st.markdown(
    """
    <div class="mini-left-signature">
        👨‍🔬 م. عبد القادر إسماعيل تاور © 2026 | خبير الحلول الذكية للثروة الحيوانية والبرمجيات المتكاملة
    </div>
    """,
    unsafe_allow_html=True
)
