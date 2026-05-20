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
SENDER_PASSWORD = "oynz rdli tsdy ekdq"  # تأكد من تفعيل App Password من حساب Google الخاص بك

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
    body = "السلام عليكم م. عبد القادر،\n\nمرفق السورس كود النهائي بعد حل مشكلة الـ KeyError وتوسيع النطاق الجغرافي الشامل للولايات السودانية وإعادة إظهار محددات البروتين.\n\nتحياتي."
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
        st.error(f"❌ خطأ في الاتصال بالخادم الذكي: {e}")
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
    .result-row {
        background: #f1f8e9;
        padding: 12px;
        border-bottom: 2px solid #c8e6c9;
        margin-bottom: 6px;
        border-radius: 6px;
        direction: rtl;
        text-align: right;
    }
    .protein-badge {
        background-color: #e8f5e9;
        border: 2px solid #2e7d32;
        color: #1b5e20;
        padding: 10px;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================================
# 2. حل جذري لـ KeyError: تهيئة كافة متغيرات الجلسة عند الإقلاع الأول
# =====================================================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "active_formula" not in st.session_state: st.session_state["active_formula"] = {}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 16.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 285.0

# تهيئة المخزون بشكل قطعي لمنع انهيار تبويب المستودعات
if "inventory" not in st.session_state:
    st.session_state["inventory"] = {
        "ذرة صفراء": 50.0, "ذرة بيضاء": 30.0, "شعير مطحون": 25.0, "سورجم (فتريتة)": 40.0,
        "كسب فول صويا 44%": 20.0, "كسب فول صويا 48%": 15.0, "أمباز الفول السوداني (كسب)": 35.0,
        "كسب عباد الشمس 36%": 15.0, "نخالة قمح (ردة)": 60.0, "البرسيم الجاف (الدريس)": 40.0
    }

# بوابة الدخول وحماية النظام
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
# 3. توسيع الخريطة الجغرافية الشاملة وبورصة المدن والولايات كاملة
# =====================================================================
GEOGRAPHY_DATA = {
    "السودان": {
        "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
        "ولاية القضارف": ["القضارف المدينة", "الحواتة", "الفاو", "المفازة"],
        "ولاية الجزيرة": ["ود مدني", "المناقل", "الحصاحيصا", "الكاملين"],
        "ولاية شمال كردفان": ["الأبيض", "أم روابة", "بارا", "الرهد"],
        "ولاية غرب كردفان": ["الفولة", "النهود", "بابنوسة", "غبيش"],
        "ولاية النيل الأزرق": ["الدمازين", "الروصيرص", "باو", "قيسان"],
        "ولاية شمال دارفور": ["الفاشر", "كبكابية", "مليط"],
        "ولاية جنوب دارفور": ["نيالا", "عد الفرسان", "تلس"],
        "ولاية البحر الأحمر": ["بورتسودان", "سواكن", "طوكر"]
    },
    "ليبيا": {
        "إقليم البطنان والمنطقة الشرقية": ["طبرق", "امساعد", "البردي", "بنغازي", "البيضاء", "درنة", "إجدابيا"],
        "الإقليم الغربي طرابلس": ["طرابلس", "مصراتة", "الزاوية", "غريان", "زليتن", "خمس"],
        "فزان والمنطقة الجنوبية": ["سبها", "مرزق", "غـات", "براك الشاطئ", "أوباري"]
    },
    "مصر": {
        "الدلتا والقاهرة": ["القاهرة", "طنطا", "المنصورة", "الإسكندرية", "الزقازيق"],
        "الصعيد والوجه القبلي": ["أسيوط", "المنيا", "قنا", "أسوان", "سوهاج"]
    }
}

SECTOR_BREEDS_MAP = {
    "السودان": {
        "الأغنام والضأن": ["ضأن الدوبا (الحمري والشقر)", "ضأن الكباشي البري", "الضأن الصحراوي السوداني"],
        "الأبqar وسلالاتها": ["أبقار الكنانة (غزيرة اللبن)", "أبقار البطانة الديرية", "أبقار البقارة"],
        "الماعز وسلالاته": ["الماعز النوبي السوداني الأصيل", "الماعز الجبلي والنيلي", "الماعز الصحراوي"],
        "الطيور والسمان": ["دواجن لاحم هبرد", "دواجن بياض هاي لاين", "سمان بلدي محسن"],
        "الإبل والثروة الصحراوية": ["إبل الرشايدي", "إبل الكباشي / العنافي"]
    },
    "ليبيا": {
        "الأغنام والضأن": ["أغنام البرقي العريقة", "أغنام المارينو المحسنة", "الضأن المحلي الليبي"],
        "الأبقار وسلالاتها": ["أبقار فريزيان محسن محلي", "أبقار برقة المحلية"],
        "الماعز وسلالاته": ["الماعز القبرصي (الشامي)", "الماعز الصحراوي الليبي"],
        "الطيور والسمان": ["دواجن لاحم كب 500", "دواجن بياض لوهمان", "سمان جامبو مزارع"],
        "الإبل والثروة الصحراوية": ["إبل الملافي", "إبل الساحلية"]
    },
    "مصر": {
        "الأغنام والضأن": ["أغنام الرحماني", "أغنام الأوسيمي", "أغنام البرقي مريوط"],
        "الأبقار وسلالاتها": ["أبقار هولشتاين مأقلمة", "الأبقار البلدي المصرية", "الجاموس المصري العليق"],
        "الماعز وسلالاته": ["الماعز الزرايبي المصري", "الماعز البلدي المحسن"],
        "الطيور والسمان": ["دواجن لاحم روس 308", "دواجن بياض إيسا براون", "السمان الياباني المتطور"],
        "الإبل والثروة الصحراوية": ["إبل المغربي مزارع", "إبل الفلاحي الصعيدي"]
    }
}

# بورصة الأسعار الحركية للمدن والولايات المستحدثة
REAL_CITY_PRICES = {
    "طبرق": {"ذرة صفراء": 255.0, "كسب فول صويا 44%": 470.0, "نخالة قمح (ردة)": 165.0, "شعير مطحون": 230.0},
    "الخرطوم": {"ذرة صفراء": 230.0, "كسب فول صويا 44%": 440.0, "نخالة قمح (ردة)": 140.0, "سورجم (فتريتة)": 190.0},
    "النهود": {"ذرة صفراء": 220.0, "أمباز الفول السوداني (كسب)": 390.0, "نخالة قمح (ردة)": 125.0, "سورجم (فتريتة)": 175.0},
    "الدمازين": {"ذرة صفراء": 210.0, "أمباز الفول السوداني (كسب)": 380.0, "نخالة قمح (ردة)": 120.0, "سورجم (فتريتة)": 170.0},
    "القضارف المدينة": {"ذرة صفراء": 215.0, "كسب فول صويا 44%": 420.0, "سورجم (فتريتة)": 165.0},
    "القاهرة": {"ذرة صفراء": 245.0, "كسب فول صويا 44%": 455.0, "نخالة قمح (ردة)": 155.0}
}

def get_market_prices_by_city(city_name):
    base = {
        "ذرة صفراء": 240.0, "ذرة بيضاء": 235.0, "شعير مطحون": 220.0, "سورجم (فتريتة)": 200.0, "قمح محلي مصنّع": 250.0,
        "أمباز الفول السوداني (كسب)": 440.0, "كسب فول صويا 44%": 450.0, "كسب فول صويا 48%": 490.0, "كسب عباد الشمس 36%": 320.0, "كسب بذور القطن": 300.0,
        "نخالة قمح (ردة)": 150.0, "البرسيم الجاف (الدريس)": 170.0, "مولاس": 120.0, "مسحوق أسماك (Fishmeal 60%)": 850.0,
        "مركزات دواجن وسمان": 650.0, "مركزات خيول ومجترات": 600.0, "الحجر الجيري (بودرة بلاط)": 40.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0,
        "ملح الطعام": 30.0, "مضاد سموم فطرية": 950.0, "بيكربونات الصوديوم (الصودا)": 340.0,
        "إنزيم الفايتيز الزامي (Phytase Super-D)": 1150.0, "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": 1400.0
    }
    if city_name in REAL_CITY_PRICES:
        for k, v in REAL_CITY_PRICES[city_name].items():
            if k in base: base[k] = v
    return base

BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {"ذرة صفراء": 8.5, "ذرة بيضاء": 8.8, "شعير مطحون": 11.5, "سورجم (فتريتة)": 10.0, "قمح محلي مصنّع": 12.0},
    "الأكساب والأمباز ومصادر البروتين العالي": {"أمباز الفول السوداني (كسب)": 46.0, "كسب فول صويا 44%": 44.0, "كسب فول صويا 48%": 48.0, "كسب عباد الشمس 36%": 36.0},
    "المخلفات الرعوية والمواد المالئة": {"نخالة قمح (ردة)": 15.0, "البرسيم الجاف (الدريس)": 16.5, "مولاس": 4.0},
    "الإضافات المتخصصة والمركزات": {"مركزات دواجن وسمان": 40.0, "مركزات خيول ومجترات": 36.0, "الحجر الجيري (بودرة بلاط)": 0.0, "فوسفات ثنائي الكالسيوم (DCP)": 0.0, "ملح الطعام": 0.0, "مضاد سموم فطرية": 0.0, "بيكربونات الصوديوم (الصودا)": 0.0},
    "المعاملات الحيوية والإنزيمات": {"إنزيم الفايتيز الزامي (Phytase Super-D)": 0.0, "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": 0.0}
}

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "ليبيا": {"rate": 4.82, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"}
}

# تفكيك الواجهة الهيكلية للمنصة
col_logo, col_title = st.columns([0.25, 0.75])
with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور الذكية للإنتاج الحيواني وصناعة الأعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

# إدارة الأقسام والتبويبات المتاحة
if st.session_state["user_role"] == "admin":
    tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى", "🏭 إدارة المستودعات والخصم التلقائي", "🧾 التسويق وفواتير حركة البيع", "🏷️ مصمم بطاقات الديباجة والدعاية"]
else:
    tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى"]

tabs = st.tabs(tabs_titles)

with tabs[0]:
    st.markdown('<div class="section-title">🌍 أولاً: المربع الجغرافي وبورصة أسعار الأقاليم الحقيقية</div>', unsafe_allow_html=True)
    col_country, col_state, col_city = st.columns(3)
    with col_country: user_country = st.selectbox("اختر دولة المربي المستهدف:", ["السودان", "ليبيا", "مصر"])
        
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    local_rate = c_info["rate"]; local_sym = c_info["sym"]

    state_options = list(GEOGRAPHY_DATA[user_country].keys())
    with col_state: chosen_state = st.selectbox("اختر الإقليم / الولاية:", state_options)

    city_options = GEOGRAPHY_DATA[user_country][chosen_state]
    with col_city: user_city = st.selectbox("اختر المدينة المرتبطة بالبورصة حركياً:", city_options)

    live_prices = get_market_prices_by_city(user_city)

    st.markdown('<div class="section-title">⚖️ ثانياً: قطاع الثروة الحيوانية والسلالات الجغرافية الدقيقة</div>', unsafe_allow_html=True)
    col_sec, col_sub, col_prod = st.columns(3)
    
    available_sectors = list(SECTOR_BREEDS_MAP[user_country].keys())
    with col_sec: main_sector = st.selectbox("اختر القطاع الإنتاجي:", available_sectors)
    
    breed_options = SECTOR_BREEDS_MAP[user_country][main_sector]
    with col_sub: sub_type = st.selectbox("السلالة الفعلية المتاحة جغرافياً:", breed_options)

    # ضبط محددات الإنتاج والبروتين التلقائي المبدئي
    if "الأغنام" in main_sector or "الأبقار" in main_sector:
        prod_stage = st.selectbox("نوع الإنتاج والمرحلة الفسيولوجية:", ["تسمين وإنتاج لحوم مكثف", "إدرار حليب عالي", "أمهات وحوامل"])
        default_cp = 14.5 if "تسمين" in prod_stage else 16.5
    elif "الطيور" in main_sector:
        prod_stage = st.selectbox("مرحلة الإنتاج الداجني:", ["بادي لاحم 23%", "نامي لاحم 21%", "ناهي لاحم 19%", "بياض إنتاجي"])
        default_cp = 23.0 if "بادي" in prod_stage else 21.0
    else:
        prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج عام وتنمية"])
        default_cp = 14.0

    with col_prod: st.write(f"📊 الصنف الحركي: **{prod_stage}**")

    st.markdown('<div class="section-title">📋 ثالثاً: بروتين العليقة المستهدف (Crude Protein) الحسابي</div>', unsafe_allow_html=True)
    final_target_cp = st.slider("نسبة البروتين الخام (CP %) المستهدفة في الطن:", 10.0, 40.0, value=default_cp)

    st.markdown('<div class="section-title">🌾 رابعاً: تحديد مكونات ومصادر العليقة المتاحة بالمدينة</div>', unsafe_allow_html=True)
    selected_ingredients = []; ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=True):
            sub_cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with sub_cols[idx % 3]:
                    is_def = True if "ذرة" in ing_name or "صويا" in ing_name or "أمباز" in ing_name or "ملح" in ing_name or "إنزيم" in ing_name else False
                    checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                    current_live_price = live_prices.get(ing_name, 350.0)
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = current_live_price

    st.markdown("---")
    if st.button("🚀 تشغيل محرك التركيب العلمي الحقيقي وعزل النسب", type="primary", use_container_width=True):
        if len(selected_ingredients) < 3: 
            st.error("⚠️ يرجى تحديد 3 خامات علفية على الأقل لضمان التوازن الرياضي المفتوح.")
        else:
            formula_results = {}
            auto_added_enzymes = {}

            # الإضافات الصغرى الثابتة
            fixed_ratios = {"ملح الطعام": 0.005, "مضاد سموم فطرية": 0.002, "الحجر الجيري (بودرة بلاط)": 0.020, "فوسفات ثنائي الكالسيوم (DCP)": 0.01}
            used_fixed_pct = 0.0
            for name in selected_ingredients:
                if name in fixed_ratios:
                    formula_results[name] = fixed_ratios[name] * 100
                    used_fixed_pct += fixed_ratios[name] * 100

            # تقسيم المكونات الكبرى وعزل نسب الطاقة والبروتين
            grains_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"]]
            protein_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"]]
            filler_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["المخلفات الرعوية والمواد المالئة"]]

            if not grains_ingredients: grains_ingredients = ["ذرة صفراء"]
            if not protein_ingredients: 
                protein_ingredients = ["أمباز الفول السوداني (كسب)"] if user_country == "السودان" else ["كسب فول صويا 44%"]

            grain_fixed_target = 60.0 if "الطيور" in main_sector else 55.0
            for x in grains_ingredients:
                formula_results[x] = grain_fixed_target / len(grains_ingredients)

            remaining_pct = 100.0 - used_fixed_pct - grain_fixed_target
            
            if protein_ingredients:
                prot_share = remaining_pct * 0.85
                for x in protein_ingredients: formula_results[x] = prot_share / len(protein_ingredients)
            if filler_ingredients:
                fill_share = remaining_pct * 0.15
                for x in filler_ingredients: formula_results[x] = fill_share / len(filler_ingredients)

            # حقن الإنزيم الذكي بالإشعار المؤقت الذي يختفي تلقائياً خلال 30 ثانية
            if "الطيور" in main_sector or "الأبقار" in main_sector or "الأغنام" in main_sector:
                auto_added_enzymes["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.050
                st.toast("🧬 تم حقن إنزيم الفايتيز تلقائياً بنسبة صريحة (0.050%) في جدول المكونات.", icon="🧪")

            if auto_added_enzymes:
                total_enz_pct = sum(auto_added_enzymes.values())
                major_grain = grains_ingredients[0]
                if major_grain in formula_results:
                    formula_results[major_grain] = max(1.0, formula_results[major_grain] - total_enz_pct)
                for enz_name, enz_pct in auto_added_enzymes.items():
                    formula_results[enz_name] = enz_pct

            # حساب حاصل ومعدل البروتين الحقيقي المزيج برمجياً لإعادة إظهاره
            calculated_protein = 0.0
            for ing_name, pct in formula_results.items():
                for cat, items in BIG_FEEDS_LIBRARY.items():
                    if ing_name in items:
                        calculated_protein += (pct / 100.0) * items[ing_name]

            st.session_state["active_formula"] = formula_results
            st.session_state["active_cp_tag"] = calculated_protein if calculated_protein > 0 else final_target_cp
            st.session_state["active_breed_tag"] = sub_type
            st.session_state["active_stage_title"] = f"{main_sector} - {prod_stage}"

            res_col1, res_col2 = st.columns([0.6, 0.4])
            with res_col1:
                st.markdown(f"### 📝 جدول ديباجة الطن المعتمد لمدينة ({user_city}):")
                
                # إظهار نسبة البروتين البرمجية الصريحة المحسوبة للمزيج بدقة وعزل تام
                st.markdown(f"<div class='protein-badge'>🧬 نسبة بروتين المزيج الخام المحسوبة برمجياً (Crude Protein): {st.session_state['active_cp_tag']:.2f} %</div>", unsafe_allow_html=True)
                st.write("")
                
                for k, v in formula_results.items():
                    st.markdown(f"<div class='result-row'>🔹 <b>{k}:</b> {v:.3f} % ➡️ (<span style='color:#1b5e20; font-weight:bold;'>{v*10:.2f} كجم</span> / طن المزيج)</div>", unsafe_allow_html=True)
                
                ton_cost = sum([(v/100) * ingredient_prices.get(k, 300.0) if k in ingredient_prices else (v/100)*600.0 for k, v in formula_results.items()])
                st.session_state["computed_ton_cost"] = ton_cost
                st.metric(f"💰 تكلفة الطن في بورصة أسواق ({user_city}):", f"${ton_cost:.2f} (يعادل {ton_cost*local_rate:,.1f} {local_sym})")
            with res_col2:
                st.bar_chart(formula_results)

# ==========================================
# 5. التبويبات الإدارية المؤمنة ضد الـ KeyError
# ==========================================
if st.session_state["user_role"] == "admin":
    with tabs[1]:
        st.markdown('<div class="section-title">🏭 إدارة المستودعات والخصم الآلي</div>', unsafe_allow_html=True)
        # تعديل المخزون بأمان دون التسبب بانهيار الواجهة
        for k, v in list(st.session_state["inventory"].items()):
            st.session_state["inventory"][k] = st.number_input(f"مخزون طن متوفر من ({k}):", min_value=0.0, value=float(v), key=f"inv_input_{k}")

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
            <p style="text-align: right;">🧬 نسبة بروتين المزيج المحسوبة: {st.session_state['active_cp_tag']:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. نظام الأرشفة والمراسلة الآمنة بأسفل التطبيق
# ==========================================
st.markdown("<br><hr style='border-top: 1px dashed #2e7d32;'>", unsafe_allow_html=True)
st.markdown("### 📨 أرشفة الكود والتقارير الحالية بالبريد الإلكتروني")
target_email = st.text_input("أدخل البريد الإلكتروني المستلم لحفظ نسخة السورس كود الأساسية:", value="abukram128@gmail.com")
if st.button("🚀 إرسال نسخة الكود فوراً"):
    if send_code_to_mail(target_email):
        st.success("📥 تم إرسال ملف السورس كود (.py) بنجاح وأرشفته تغذوياً وبرمجياً.")
    else:
        st.warning("⚠️ تنبيه أمني: يرجى التحقق من توليد App Password من حسابك في Google وتحديث متغير SENDER_PASSWORD في الكود لتخطي جدار الحماية الحركي.")

st.markdown('<div class="mini-left-signature">👨‍🔬 م. عبد القادر إسماعيل تاور © 2026 | خبير الحلول البرمجية المتكاملة والإنتاج الحيواني</div>', unsafe_allow_html=True)
