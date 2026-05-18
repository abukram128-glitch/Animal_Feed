import streamlit as st
import numpy as np
import json
import os
import base64

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

def get_image_base64(paths):
    for path in paths:
        if os.path.exists(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
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
    .owner-card {
        background: #fff3e0;
        padding: 15px;
        border-radius: 8px;
        border-right: 5px solid #e65100;
        margin-bottom: 15px;
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
# 3. الهيكل الافتراضي للمخازن وبورصة تاور العالمية الشاملة
# =====================================================================
if "inventory" not in st.session_state:
    st.session_state["inventory"] = {
        "ذرة صفراء": 25.0, "ذرة بيضاء": 10.0, "شعير مطحون": 15.0, "سورجم (فتريتة)": 15.0,
        "أمباز الفول السوداني (كسب)": 20.0, "كسب فول صويا 44%": 14.0, "كسب فول صويا 48%": 18.0, "كسب عباد الشمس 36%": 10.0, 
        "نخالة قمح (ردة)": 20.0, "البرسيم الجاف (الدريس)": 30.0, "مولاس": 5.0,
        "مسحوق أسماك (Fishmeal 60%)": 4.0, "مركزات دواجن وسمان": 3.5, "مركزات خيول ومجترات": 3.5,
        "الحجر الجيري (بودرة بلاط)": 6.0, "فوسفات ثنائي الكالسيوم (DCP)": 3.0, "ملح الطعام": 2.5, "مضاد سموم فطرية": 1.2
    }

# تهيئة البورصة الشاملة في الجلسة حتى يتمكن "تاور" من تعديلها وتحديثها ديناميكياً
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
        "طبق بيض مائدة 30 بيضة ($)": 4.20,
        "رطل / لتر حليب خام ($)": 0.90,
        "كيلو جبن أبيض محلي ($)": 5.00,
        "كيلو جبن جاف / شيدر ($)": 8.50
    }

def get_adjusted_market_data(country, state_or_region, city):
    """
    تعديل الأسعار استرشادياً بناءً على الموقع الجغرافي المختار مع ربطها بالبورصة المركزية للمنصة.
    """
    # أسعار خامات الأعلاف الأساسية
    feed_prices = {
        "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0, "سورجم (فتريتة)": 195.0,
        "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا 44%": 440.0, "كسب فول صويا 48%": 480.0, "كسب عباد الشمس 36%": 310.0, 
        "نخالة قمح (ردة)": 150.0, "البرسيم الجاف (الدريس)": 170.0, "مولاس": 120.0,
        "مسحوق أسماك (Fishmeal 60%)": 850.0, "مركزات دواجن وسمان": 650.0, "مركزات خيول ومجترات": 600.0,
        "الحجر الجيري (بودرة بلاط)": 40.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0, "ملح الطعام": 30.0, "مضاد سموم فطرية": 950.0
    }
    
    multiplier = 1.0
    if country == "السودان":
        multiplier = 1.15
        if state_or_region in ["ولاية القضارف", "ولاية الجزيرة"]:
            feed_prices["سورجم (فتريتة)"] *= 0.82
            feed_prices["أمباز الفول السوداني (كسب)"] *= 0.88
    elif country == "ليبيا":
        multiplier = 1.10
        if city == "طبرق": multiplier = 1.06
    elif country == "مصر":
        multiplier = 1.04

    for k in feed_prices:
        feed_prices[k] *= multiplier

    return feed_prices

BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5}, "ذرة بيضاء": {"CP": 8.8}, "شعير مطحون": {"CP": 11.5}, "سورجم (فتريتة)": {"CP": 10.0}
    },
    "الأكساب والأمباز ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0}, "كسب فول صويا 44%": {"CP": 44.0}, "كسب فول صويا 48%": {"CP": 48.0}, "كسب عباد الشمس 36%": {"CP": 36.0}, "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0}
    },
    "المخلفات الرعوية والمواد المالئة": {
        "نخالة قمح (ردة)": {"CP": 15.0}, "البرسيم الجاف (الدريس)": {"CP": 16.5}, "مولاس": {"CP": 4.0}
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
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600&auto=format&fit=crop",
    "سمان": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600&auto=format&fit=crop",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=600&auto=format&fit=crop"
}

# تهيئة أوتوماتيكية للحالة العامة للمنصة لضمان عدم حدوث تعارض
if "active_formula" not in st.session_state:
    st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "أمباز الفول السوداني (كسب)": 35.0, "إضافات مخصصة": 5.0}
if "active_cp_tag" not in st.session_state:
    st.session_state["active_cp_tag"] = 16.0
if "active_breed_tag" not in st.session_state:
    st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_animal_img" not in st.session_state:
    st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES["عام"]
if "active_stage_title" not in st.session_state:
    st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state:
    st.session_state["computed_ton_cost"] = 280.0

# ==========================================
# 4. بناء الواجهة الرئيسية للمنصة
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown('<img src="https://images.unsplash.com/photo-1595246140625-573b715d11dc?q=80&w=150" class="profile-img-style">', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور الذكية للإنتاج الحيواني وصناعة الأعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.2rem; margin-top:5px; margin-bottom:0;'>البورصة العالمية والمحلية الشاملة للماشية والطيور والمنتجات الحيوانية</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

# فرز التبويبات حسب رتبة الدخول
if st.session_state["user_role"] == "admin":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية الكبرى", 
        "📊 بورصة تاور المركزية للمنتجات والماشية",
        "🏭 إدارة المستودعات والخصم التلقائي", 
        "🧾 التسويق وفواتير حركة البيع", 
        "🖨️ مصمم بطاقات الديباجة والدعاية"
    ]
else:
    tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى"]

tabs = st.tabs(tabs_titles)

# ====================================================================
# التبويب الأول: النمذجة والحسابات العلفية الكبرى واختيار المواقع
# ====================================================================
with tabs[0]:
    st.markdown('<div class="section-title">🌍 أولاً: تحديد الموقع الجغرافي وبورصة الأسعار الإقليمية والعالمية</div>', unsafe_allow_html=True)
    
    col_country, col_state, col_city = st.columns(3)
    with col_country:
        user_country = st.selectbox("اختر دولة المربي:", ["السودان", "ليبيا", "مصر", "باقي دول العالم / البورصة المفتوحة"])
        
    chosen_state = "عام"
    with col_state:
        if user_country == "السودان":
            chosen_state = st.selectbox("اختر الولاية السودانية:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال دارفور", "ولاية جنوب دارفور", "ولاية البحر الأحمر", "ولاية نهر النيل"])
        elif user_country == "ليبيا":
            chosen_state = st.selectbox("اختر الإقليم الجغرافي:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
        else:
            chosen_state = st.selectbox("الإقليم الإداري:", ["المركز الرئيسي العالمي", "الأسواق المفتوحة"])

    with col_city:
        if user_country == "السودان":
            if chosen_state == "ولاية الخرطوم": user_city = st.selectbox("اختر المدينة:", ["الخرطوم", "أم درمان", "بحري"])
            elif chosen_state == "ولاية الجزيرة": user_city = st.selectbox("اختر المدينة:", ["ود مدني", "الحصاحيصا", "المناقل"])
            elif chosen_state == "ولاية القضارف": user_city = st.selectbox("اختر المدينة:", ["القضارف المدينة", "الفاو"])
            elif chosen_state == "ولاية شمال دارفور": user_city = st.selectbox("اختر المدينة:", ["الفاشر", "كتم"])
            elif chosen_state == "ولاية جنوب دارفور": user_city = st.selectbox("اختر المدينة:", ["نيالا", "عد الفرسان"])
            elif chosen_state == "ولاية البحر الأحمر": user_city = st.selectbox("اختر المدينة:", ["بورتسودان", "سواكن"])
            else: user_city = st.selectbox("اختر المدينة:", ["شندي", "عطبرة"])
        elif user_country == "ليبيا":
            if chosen_state == "المنطقة الشرقية": user_city = st.selectbox("اختر المدينة الليبية:", ["طبرق", "بنغازي", "البيضاء", "درنة"])
            elif chosen_state == "المنطقة الغربية": user_city = st.selectbox("اختر المدينة الليبية:", ["طرابلس", "مصراتة", "الزاوية"])
            else: user_city = st.selectbox("اختر المدينة الليبية:", ["سبها", "مرزق", "غات"])
        else:
            user_city = st.text_input("اكتب اسم المدينة العالمية يدوياً:", "شيكاغو / لندن / دبي")

    live_prices = get_adjusted_market_data(user_country, chosen_state, user_city)
    
    # عرض أسعار البورصة الشاملة للحيوانات والمنتجات للمربي مباشرة في الواجهة
    col_view1, col_view2 = st.columns(2)
    with col_view1:
        st.markdown(f'<div class="price-card"><b>📈 بورصة الماشية والطيور الحية في ({user_city}):</b><br>' + 
                    "<br>".join([f"▪️ {k}: <b>${v:.2f}</b>" for k, v in st.session_state["global_livestock_prices"].items()]) + "</div>", unsafe_allow_html=True)
    with col_view2:
        st.markdown(f'<div class="price-card"><b>🥩 بورصة المنتجات الحيوانية والألبان في ({user_city}):</b><br>' + 
                    "<br>".join([f"▪️ {k}: <b>${v:.2f}</b>" for k, v in st.session_state["global_products_prices"].items()]) + "</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">⚖️ ثانياً: اختيار القطاع والنوع والإنتاجية المستهدفة</div>', unsafe_allow_html=True)
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec:
        main_sector = st.selectbox("اختر القطاع الإنتاجي الرئيسي:", ["الخيول والفروسية", "الماعز وسلالاته", "الأبقار وسلالاتها", "الطيور والسمان", "الأسماك والأحياء المائية"])
    
    show_measurements = False
    weight_factor = 10000; feed_factor = 0.02; default_cp = 14.0; dynamic_img_key = "عام"; chosen_concentrate = None
    
    with col_sub:
        if main_sector == "الخيول والفروسية":
            sub_type = st.selectbox("السلالة المستهدفة:", ["خيل عربي أصيل", "ثوروبريد", "خيول محلية هجين"]); dynamic_img_key = "خيول"; show_measurements = True
            weight_factor = 11877; feed_factor = 0.022; chosen_concentrate = "مركزات خيول ومجترات"
        elif main_sector == "الماعز وسلالاته":
            sub_type = st.selectbox("السلالة المستهدفة:", ["الماعز النوبي السوداني", "الماعز الصحراوي", "بور / محسن"]); dynamic_img_key = "ماعز"; show_measurements = True
            weight_factor = 11250; feed_factor = 0.028; chosen_concentrate = "مركزات خيول ومجترات"
        elif main_sector == "الأبقار وسلالاتها":
            sub_type = st.selectbox("السلالة المستهدفة:", ["كنانة (سوداني)", "بطانة (مدر)", "هولشتاين / محسن"]); dynamic_img_key = "أبقار"; show_measurements = True
            weight_factor = 10838; feed_factor = 0.025; chosen_concentrate = "مركزات خيول ومجترات"
        elif main_sector == "الطيور والسمان":
            sub_type = st.selectbox("نوع الطيور:", ["طائر السمان (Quail)", "دواجن لاحم (Broiler)", "دواجن بياض (Layer)"]); dynamic_img_key = "سمان" if "السمان" in sub_type else "دواجن"
            chosen_concentrate = "مركزات دواجن وسمان"
        else:
            sub_type = st.selectbox("نوع الأسماك:", ["البلطي النيلي (Tilapia)", "القرموط"]); dynamic_img_key = "أسماك"
            chosen_concentrate = "مسحوق أسماك (Fishmeal 60%)"

    with col_prod:
        if main_sector == "الخيول والفروسية":
            prod_stage = st.selectbox("نوع الإنتاج:", ["خيول رياضة ونشاط مكثف", "أمهار نامية صغيرة", "فرسات مرضعات"]); default_cp = 16.0 if "أمهار" in prod_stage or "مرضعات" in prod_stage else 12.0
        elif main_sector == "الماعز وسلالاته":
            prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج اللحوم وتسمين", "إنتاج ألبان وحليب"]); default_cp = 15.5 if "ألبان" in prod_stage else 13.5
        elif main_sector == "الأبقار وسلالاتها":
            prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج حليب وغزارة إدرار", "تسمين عجول مكثف"]); default_cp = 16.0 if "حليب" in prod_stage else 13.0
        elif main_sector == "الطيور والسمان":
            if "السمان" in sub_type:
                prod_stage = st.selectbox("نوع الإنتاج:", ["سمان بادي / نامي", "سمان بياض إنتاجي"]); default_cp = 24.0 if "بادي" in prod_stage else 20.0
            else:
                prod_stage = st.selectbox("نوع الإنتاج:", ["بادي دواجن 23%", "نامي دواجن 21%", "ناهي دواجن 19%", "بياض إنتاجي"]); default_cp = 23.0 if "بادي" in prod_stage else (21.0 if "نامي" in prod_stage else (19.0 if "ناهي" in prod_stage else 17.5))
        else:
            prod_stage = st.selectbox("نوع الإنتاج:", ["بادئ زريعة أسماك عالي", "نمو وتسمين أسماك نيلية"]); default_cp = 35.0 if "زريعة" in prod_stage else 30.0

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
                    is_def = True if ing_name == chosen_concentrate or "ذرة" in ing_name or "أمباز" in ing_name or "ملح" in ing_name else False
                    checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                    current_live_price = live_prices.get(ing_name, 350.0)
                    
                    if st.session_state["user_role"] == "admin":
                        price_input = st.number_input(f"السعر للطن ({ing_name}) $:", min_value=10.0, value=float(current_live_price), key=f"price_{ing_name}")
                    else:
                        st.markdown(f"💰 السعر الحالي بموقعك: **`${current_live_price:.2f}`** / طن")
                        price_input = current_live_price
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price_input

    st.markdown("---")
    if st.button("🚀 تشغيل محرك التركيب الذكي وحساب نسب الخلط المثلى", type="primary", use_container_width=True):
        if chosen_concentrate and chosen_concentrate not in selected_ingredients:
            selected_ingredients.append(chosen_concentrate)
            ingredient_prices[chosen_concentrate] = live_prices.get(chosen_concentrate, 550.0)

        if len(selected_ingredients) < 3:
            st.error("⚠️ يرجى تحديد 3 خامات علفية على الأقل لضمان توليفة متزنة.")
        else:
            formula_results = {}
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
            filler_ingredients = [x for x in selected_ingredients if x == "نخالة قمح (ردة)" or x in BIG_FEEDS_LIBRARY["المخلفات الرعوية والمواد المالئة"]]
            protein_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"] and x != "مسحوق أسماك (Fishmeal 60%)"]
            
            if not grains_ingredients: grains_ingredients = [selected_ingredients[0]]
            if not protein_ingredients: protein_ingredients = [selected_ingredients[-1]]
            
            p_ratio = 0.55 if final_target_cp > 30 else (0.42 if final_target_cp > 22 else (0.25 if final_target_cp > 15 else 0.14))
            protein_share = remaining_pct * p_ratio
            for x in protein_ingredients: formula_results[x] = protein_share / len(protein_ingredients)
                
            energy_share = remaining_pct * (1.0 - p_ratio)
            if grains_ingredients and filler_ingredients:
                grain_part = energy_share * 0.70; filler_part = energy_share * 0.30
                for x in grains_ingredients: formula_results[x] = grain_part / len(grains_ingredients)
                for x in filler_ingredients: formula_results[x] = filler_part / len(filler_ingredients)
            else:
                for x in grains_ingredients: formula_results[x] = energy_share / len(grains_ingredients)

            st.session_state["active_formula"] = formula_results
            st.session_state["active_cp_tag"] = final_target_cp
            st.session_state["active_breed_tag"] = sub_type
            st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES.get(dynamic_img_key, ANIMAL_IMAGES_RESOURCES["عام"])
            st.session_state["active_stage_title"] = f"{main_sector} - {prod_stage}"
            
            st.success(f"🎯 تم حساب نسب الخلط والجدوى لأسواق: {user_city} بنجاح!")
            res_col1, res_col2 = st.columns([0.6, 0.4])
            with res_col1:
                st.write("#### 📝 المقادير لتركيب طن واحد (كجم):")
                for k, v in formula_results.items(): st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** / طن)")
                ton_cost = sum([(v/100) * ingredient_prices.get(k, 300.0) for k, v in formula_results.items()])
                st.session_state["computed_ton_cost"] = ton_cost
                st.metric(f"💰 التكلفة الفعلية لإنتاج الطن في {user_city}: ", f"${ton_cost:.2f}")
            with res_col2:
                st.bar_chart(formula_results)

# ====================================================================
# التبويب الثاني الجديد: بورصة تاور المركزية للمنتجات والماشية (للمالك فقط)
# ====================================================================
if st.session_state["user_role"] == "admin":
    with tabs[1]:
        st.markdown('<div class="section-title">📊 لوحة تحكم بورصة تاور المركزية الشاملة (تحديث الأسعار المباشرة)</div>', unsafe_allow_html=True)
        st.markdown('<div class="owner-card">👑 <b>مرحباً م. عبد القادر إسماعيل تاور:</b> هذه اللوحة مخصصة لك بالكامل لربط وتحديث الأسواق اليومية للماشية والمنتجات لتحديث الشبكة تلقائياً.</div>', unsafe_allow_html=True)
        
        col_edit1, col_edit2 = st.columns(2)
        with col_edit1:
            st.subheader("🐓 بورصة الماشية والداجن (عمر يوم والبشاير)")
            for animal, price in st.session_state["global_livestock_prices"].items():
                st.session_state["global_livestock_prices"][animal] = st.number_input(f"تحديث سعر: {animal}", min_value=0.0, value=float(price), step=0.1)
                
        with col_edit2:
            st.subheader("🥛 بورصة الألبان واللحوم والأجبان المصنعة")
            for product, price in st.session_state["global_products_prices"].items():
                st.session_state["global_products_prices"][product] = st.number_input(f"تحديث سعر: {product}", min_value=0.0, value=float(price), step=0.1)
        st.success("💾 يتم حفظ وتحديث أسعار البورصة للشبكة محلياً وعالمياً بشكل تلقائي وفوري بمجرد إدخالها.")

    # التبويبات الأخرى الإدارية
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
        st.markdown(f"### 💰 إجمالي القيمة المستحقة للفاتورة: `${total_bill:.2f}`")
        if st.button("✅ تأكيد عملية البيع وخصم المكونات"):
            can_deduct = True
            for name, pct in st.session_state["active_formula"].items():
                if st.session_state["inventory"].get(name, 0.0) < ((pct / 100) * required_tons): can_deduct = False; st.error(f"❌ رصيد غير كافي لـ {name}!"); break
            if can_deduct:
                for name, pct in st.session_state["active_formula"].items(): st.session_state["inventory"][name] -= ((pct / 100) * required_tons)
                st.success("🔥 تم الخصم التلقائي وتحديث المخازن!"); st.rerun()

    with tabs[4]:
        st.markdown('<div class="section-title">🏷️ مُصمم ديباجات الطباعة الفنية على جوالات الأعلاف</div>', unsafe_allow_html=True)
        trade_brand = st.text_input("اسم البراند التجاري:", "مجموعة تاور لإنتاج الأعلاف ومصنعات الإنتاج الحيواني")
        st.markdown(f"""
        <div class="sack-tag">
            <img src="{st.session_state['active_animal_img']}" class="animal-banner-img">
            <h2 style="text-align: center; margin-top:0;">🌟 {trade_brand} 🌟</h2>
            <h3 style="text-align: center; color: #c62828; margin-top:0; font-weight: bold;">م. عبد القادر إسماعيل تاور</h3>
            <p style="text-align: center; font-weight: bold; background-color:#e8f5e9; padding:6px; color:#1b5e20;">🎯 علف مخصص لـ: {st.session_state['active_stage_title']} | نسبة البروتين: {st.session_state['active_cp_tag']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

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
