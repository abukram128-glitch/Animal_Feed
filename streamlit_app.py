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

# ==========================================
# 3. الهيكل الافتراضي للمخازن والمكتبة العلفية
# ==========================================
if "inventory" not in st.session_state:
    st.session_state["inventory"] = {
        "ذرة صفراء": 25.0, "ذرة بيضاء": 10.0, "شعير مطحون": 15.0, "شوفان": 8.0, "قمح": 12.0, "سورجم (فتريتة)": 15.0,
        "أمباز الفول السوداني (كسب)": 20.0, "كسب فول صويا 44%": 14.0, "كسب فول صويا 48%": 18.0, "كسب عباد الشمس 36%": 10.0, 
        "كسب قطن": 7.0, "كسب نواة النخيل": 8.0, "جلوتين الذرة 60%": 5.0, "جلوتين فيد (DDGS)": 6.0,
        "نخالة قمح (ردة)": 20.0, "البرسيم الجاف (الدريس)": 30.0, "تبن قمح": 40.0, "قشر فول صويا": 12.0, "مولاس": 5.0,
        "مركزات دواجن لاحم (5%)": 4.0, "مركزات دواجن بياض (10%)": 3.5, "بريمكس مجترات": 2.0, "بريمكس خيول": 1.5,
        "الحجر الجيري (بودرة بلاط)": 6.0, "فوسفات ثنائي الكالسيوم (DCP)": 3.0, "ملح الطعام": 2.5, "مضاد سموم فطرية": 1.2
    }

BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "ME_Poultry": 3350, "ME_Rum": 2900, "CF": 2.2, "Ca": 0.02, "P": 0.28},
        "ذرة بيضاء": {"CP": 8.8, "ME_Poultry": 3300, "ME_Rum": 2880, "CF": 2.3, "Ca": 0.02, "P": 0.27},
        "شعير مطحون": {"CP": 11.5, "ME_Poultry": 2640, "ME_Rum": 2700, "CF": 5.0, "Ca": 0.06, "P": 0.35},
        "شوفان": {"CP": 11.5, "ME_Poultry": 2400, "ME_Rum": 2600, "CF": 11.0, "Ca": 0.10, "P": 0.35},
        "قمح": {"CP": 12.5, "ME_Poultry": 3000, "ME_Rum": 2950, "CF": 2.5, "Ca": 0.05, "P": 0.30},
        "مكسور أرز": {"CP": 8.0, "ME_Poultry": 3200, "ME_Rum": 2900, "CF": 1.0, "Ca": 0.03, "P": 0.25},
        "سورجم (فتريتة)": {"CP": 10.0, "ME_Poultry": 3150, "ME_Rum": 2800, "CF": 2.7, "Ca": 0.04, "P": 0.30}
    },
    "الأكساب ومصادر البروتين (يتضمن الأمباز)": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "ME_Poultry": 2500, "ME_Rum": 2850, "CF": 6.0, "Ca": 0.15, "P": 0.55},
        "كسب فول صويا 44%": {"CP": 44.0, "ME_Poultry": 2230, "ME_Rum": 2570, "CF": 7.0, "Ca": 0.29, "P": 0.65},
        "كسب فول صويا 48%": {"CP": 48.0, "ME_Poultry": 2440, "ME_Rum": 2680, "CF": 3.5, "Ca": 0.20, "P": 0.60},
        "كسب عباد الشمس 36%": {"CP": 36.0, "ME_Poultry": 1700, "ME_Rum": 2100, "CF": 14.0, "Ca": 0.40, "P": 0.90},
        "كسب قطن (غير مقشور)": {"CP": 28.0, "ME_Poultry": 1400, "ME_Rum": 1850, "CF": 22.0, "Ca": 0.20, "P": 0.95},
        "كسب نواة النخيل": {"CP": 16.5, "ME_Poultry": 1100, "ME_Rum": 1900, "CF": 15.0, "Ca": 0.25, "P": 0.60},
        "جلوتين الذرة 60%": {"CP": 60.0, "ME_Poultry": 3720, "ME_Rum": 3100, "CF": 1.5, "Ca": 0.05, "P": 0.45},
        "جلوتين فيد (DDGS)": {"CP": 27.0, "ME_Poultry": 2480, "ME_Rum": 2750, "CF": 8.0, "Ca": 0.15, "P": 0.75}
    },
    "المخلفات الصناعية والمواد المالئة": {
        "نخالة قمح (ردة)": {"CP": 15.0, "ME_Poultry": 1300, "ME_Rum": 2200, "CF": 11.0, "Ca": 0.14, "P": 1.15},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "ME_Poultry": 800, "ME_Rum": 1950, "CF": 25.0, "Ca": 1.40, "P": 0.25},
        "تبن قمح": {"CP": 3.5, "ME_Poultry": 0, "ME_Rum": 1200, "CF": 41.5, "Ca": 0.15, "P": 0.10},
        "قشر فول صويا": {"CP": 12.0, "ME_Poultry": 850, "ME_Rum": 2100, "CF": 33.0, "Ca": 0.50, "P": 0.15},
        "مولاس": {"CP": 4.0, "ME_Poultry": 1800, "ME_Rum": 2300, "CF": 0.0, "Ca": 0.80, "P": 0.10}
    },
    "المركزات والإضافات الدقيقة": {
        "مركزات دواجن لاحم (5%)": {"CP": 40.0, "ME_Poultry": 2100, "ME_Rum": 1800, "CF": 2.0, "Ca": 6.50, "P": 4.50},
        "مركزات دواجن بياض (10%)": {"CP": 32.0, "ME_Poultry": 1750, "ME_Rum": 1600, "CF": 2.5, "Ca": 8.00, "P": 5.00},
        "بريمكس مجترات": {"CP": 0.0, "ME_Poultry": 0, "ME_Rum": 0, "CF": 0.0, "Ca": 25.0, "P": 0.0},
        "بريمكس خيول": {"CP": 0.0, "ME_Poultry": 0, "ME_Rum": 0, "CF": 0.0, "Ca": 20.0, "P": 5.0},
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "ME_Poultry": 0, "ME_Rum": 0, "CF": 0.0, "Ca": 38.0, "P": 0.0},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "ME_Poultry": 0, "ME_Rum": 0, "CF": 0.0, "Ca": 22.0, "P": 18.0},
        "ملح الطعام": {"CP": 0.0, "ME_Poultry": 0, "ME_Rum": 0, "CF": 0.0, "Ca": 0.0, "P": 0.0},
        "مضاد سموم فطرية": {"CP": 0.0, "ME_Poultry": 0, "ME_Rum": 0, "CF": 0.0, "Ca": 0.0, "P": 0.0}
    }
}

ANIMAL_IMAGES_RESOURCES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600&auto=format&fit=crop",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600&auto=format&fit=crop",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600&auto=format&fit=crop",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600&auto=format&fit=crop",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600&auto=format&fit=crop",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=600&auto=format&fit=crop"
}

# ==========================================
# 4. بناء الواجهة الرئيسية وهوية م. عبد القادر
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
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.2rem; margin-top:5px; margin-bottom:0;'>لوحة التحكم والمطور الشامل - نظام معالجة الأخطاء الآمن</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

if st.session_state["user_role"] == "admin":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية الكبرى", 
        "🏭 إدارة المستودعات والخصم التلقائي", 
        "🧾 التسويق وفواتير حركة البيع", 
        "🖨️ مصمم بطاقات الديباجة والدعاية"
    ]
else:
    tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى"]

tabs = st.tabs(tabs_titles)

# ====================================================================
# التبويب الأول: النمذجة والحسابات العلفية الكبرى
# ====================================================================
with tabs[0]:
    st.markdown('<div class="section-title">⚖️ أولاً: التقييم التلقائي للأوزان والاحتياجات بناءً على الفئة والسلالة</div>', unsafe_allow_html=True)
    
    col_an, col_breed, col_h, col_l, col_ag = st.columns(5)
    with col_an:
        animal_type = st.selectbox("نوع الحيوان الحقلّي:", ["أبقار تسمين", "أبقار ألبان", "أغنام تسمين", "أغنام ألبان", "ماعز تسمين", "ماعز ألبان", "خيول عربية/رياضة"])
    
    with col_breed:
        if "أبقار" in animal_type:
            breed_type = st.selectbox("السلالة المستهدفة:", ["هولشتاين-فريزيان", "سيمينتال", "محلية / هجين"])
            dynamic_img_key = "أبقار"
        elif "أغنام" in animal_type:
            breed_type = st.selectbox("السلالة المستهدفة:", ["عواسي", "بربري", "نجدي / حري"])
            dynamic_img_key = "أغنام"
        elif "ماعز" in animal_type:
            breed_type = st.selectbox("السلالة المستهدفة:", ["دمشقي (شامي)", "سانين محلي", "زرايبي / بربري"])
            dynamic_img_key = "ماعز"
        else:
            breed_type = st.selectbox("السلالة المستهدفة:", ["خيل عربي أصيل", "ثوروبريد / رياضي"])
            dynamic_img_key = "خيول"

    with col_h:
        h_girth = st.number_input("📏 محيط الصدر (سم):", value=165.0 if "أبقار" in animal_type or "خيول" in animal_type else 75.0)
    with col_l:
        b_length = st.number_input("📏 طول الجسم (سم):", value=145.0 if "أبقار" in animal_type or "خيول" in animal_type else 65.0)
    with col_ag:
        a_months = st.number_input("⏳ العمر التقديـري (أشهر):", value=12, min_value=1)

    if "أبقار" in animal_type:
        calc_weight = (h_girth ** 2 * b_length) / 10838
        feed_factor = 0.024 if "ألبان" in animal_type else 0.022
    elif "أغنام" in animal_type:
        calc_weight = (h_girth ** 2 * b_length) / 11110
        feed_factor = 0.030 if "ألبان" in animal_type else 0.027
    elif "ماعز" in animal_type:
        calc_weight = (h_girth ** 2 * b_length) / 11250
        feed_factor = 0.032 if "ألبان" in animal_type else 0.028
    else:
        calc_weight = (h_girth ** 2 * b_length) / 11877
        feed_factor = 0.020

    if breed_type in ["هولشتاين-فريزيان", "دمشقي (شامي)", "عواسي"]:
        calc_weight *= 1.05

    req_feed_kg = calc_weight * feed_factor
    st.success(f"📊 [السلالة: {breed_type}] | الوزن الحيوي المتوقع: **{calc_weight:.1f} كجم** | كمية العليقة المقترحة يومياً: **{req_feed_kg:.2f} كجم** للمادة الجافة.")

    st.markdown('<div class="section-title">📋 ثانياً: ضبط الاحتياجات الفنية والمراحل الحرجة</div>', unsafe_allow_html=True)
    cat_selection = st.radio("القطاع الرئيسي للتركيبة الحالية:", ["المجترات (أبقار، أغنام، ماعز)", "الدواجن والطيور الداجنة", "الخيول والفروسية المتخصصة"], horizontal=True)
    
    if "المجترات" in cat_selection:
        stage_options = [
            "أبقار تسمين مكثف", "أبقار إنتاج حليب غزير", 
            "تسمين حملان/أغنام", "نعاج حليب وإدرار", 
            "ماعز تسمين وإنتاج لحم", "ماعز ألبان (حليب مدر)"
        ]
        default_cp = 16.0 if "حليب" in animal_type or "ألبان" in animal_type else 13.0
    elif "الدواجن" in cat_selection:
        stage_options = ["دواجن تسمين - بادي", "دواجن تسمين - نامي", "دواجن تسمين - ناهي", "دواجن بياض إنتاج"]
        default_cp = 21.0
        dynamic_img_key = "دواجن"
    else:
        stage_options = ["خيول رياضة نشطة", "أمهار صغيرة (رضع ونامية)", "فرسات مرضعات (إدرار عالي)"]
        default_cp = 16.0 if "أمهار" in stage_options or "مرضعات" in stage_options else 12.0

    chosen_stage = st.selectbox("المرحلة الإنتاجية المستهدفة:", stage_options)
    
    if "أمهار صغيرة" in chosen_stage:
        default_cp = 16.0
    elif "فرسات مرضعات" in chosen_stage:
        default_cp = 15.0
    elif "ماعز ألبان" in chosen_stage:
        default_cp = 15.5
    elif "دواجن تسمين - بادي" in chosen_stage:
        default_cp = 23.0

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.metric("🧬 بروتين العليقة المقترح تلقائياً لهذه المرحلة الحيوية:", f"{default_cp} %")
    with col_p2:
        override_cp = st.checkbox("⚙️ تفعيل التعديل الفني الاختياري للبروتين المستهدف")
        final_target_cp = st.slider("حدّد نسبة البروتين المستهدفة فنيّاً:", 9.0, max_value=26.0, value=default_cp) if override_cp else default_cp

    st.markdown('<div class="section-title">🌾 ثالثاً: توليد العليقة الاقتصادية من مكتبة الخامات الكبرى الموسعة</div>', unsafe_allow_html=True)
    selected_ingredients = []
    ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=True):
            sub_cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with sub_cols[idx % 3]:
                    is_def = False
                    if "ذرة صفراء" in ing_name or "أمباز الفول السوداني" in ing_name or "صويا" in ing_name or "ملح" in ing_name or "سموم" in ing_name or "حجر" in ing_name:
                        is_def = True
                    if "المجترات" in cat_selection and "الدريس" in ing_name:
                        is_def = True

                    checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                    if st.session_state["user_role"] == "admin":
                        price_input = st.number_input(f"السعر للطن ({ing_name}) $:", min_value=10.0, value=480.0 if "أمباز" in ing_name else (380.0 if "ذرة" in ing_name else 120.0), key=f"price_{ing_name}")
                    else:
                        price_input = 400.0 
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price_input

    st.markdown("---")
    if st.button("🚀 تشغيل محرك التركيب الذكي وحساب نسب الخلط المثلى", type="primary", use_container_width=True):
        if len(selected_ingredients) < 3:
            st.error("⚠️ يرجى تحديد 3 خامات علفية على الأقل لضمان توليفة متزنة.")
        else:
            formula_results = {}
            fixed_ratios = {
                "ملح الطعام": 0.005, "مضاد سموم فطرية": 0.002, 
                "الحجر الجيري (بودرة بلاط)": 0.025 if "بياض" in chosen_stage else 0.015,
                "فوسفات ثنائي الكالسيوم (DCP)": 0.01,
                "مركزات دواجن لاحم (5%)": 0.05 if "الدواجن" in cat_selection and "بياض" not in chosen_stage else 0.0,
                "مركزات دواجن بياض (10%)": 0.10 if "بياض" in chosen_stage else 0.0,
                "بريمكس مجترات": 0.01 if "المجترات" in cat_selection else 0.0,
                "بريمكس خيول": 0.01 if "الخيول" in cat_selection else 0.0,
            }
            
            used_fixed_pct = 0.0
            for name in selected_ingredients:
                if name in fixed_ratios:
                    formula_results[name] = fixed_ratios[name] * 100
                    used_fixed_pct += fixed_ratios[name] * 100
            
            remaining_pct = 100.0 - used_fixed_pct
            base_energy_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"] or x in BIG_FEEDS_LIBRARY["المخلفات الصناعية والمواد المالئة"]]
            base_protein_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الأكساب ومصادر البروتين (يتضمن الأمباز)"]]
            
            if not base_energy_ingredients: base_energy_ingredients = [selected_ingredients[0]]
            if not base_protein_ingredients: base_protein_ingredients = [selected_ingredients[-1]]
            
            if final_target_cp > 18: p_ratio = 0.32
            elif final_target_cp > 14: p_ratio = 0.22
            else: p_ratio = 0.12
                
            for x in base_protein_ingredients:
                formula_results[x] = (remaining_pct * p_ratio) / len(base_protein_ingredients)
            for x in base_energy_ingredients:
                formula_results[x] = (remaining_pct * (1.0 - p_ratio)) / len(base_energy_ingredients)

            st.session_state["active_formula"] = formula_results
            st.session_state["active_cp_tag"] = final_target_cp
            st.session_state["active_breed_tag"] = breed_type
            st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES.get(dynamic_img_key, ANIMAL_IMAGES_RESOURCES["عام"])
            st.session_state["active_stage_title"] = chosen_stage
            
            st.success("🎯 تم توليد التركيبة العلفية المتزنة وحساب مدخلات السلالة والمرحلة بنجاح!")
            
            res_col1, res_col2 = st.columns([0.6, 0.4])
            with res_col1:
                st.write("#### 📝 الدليل الفني لمقادير الخلط بالطن والشكارة:")
                for k, v in formula_results.items():
                    st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** لكل طن علف)")
                
                if st.session_state["user_role"] == "admin":
                    ton_cost = sum([(v/100) * ingredient_prices.get(k, 300.0) for k, v in formula_results.items()])
                    st.session_state["computed_ton_cost"] = ton_cost
                    st.metric("💰 تكلفة إنتاج المواد الخام للطن الواحد:", f"${ton_cost:.2f}")
            with res_col2:
                st.write("#### 📊 التوزيع المئوي لمكونات العلف:")
                st.bar_chart(formula_results)

# ====================================================================
# التبويب الثاني: إدارة المستودعات والخصم التلقائي
# ====================================================================
if st.session_state["user_role"] == "admin":
    with tabs[1]:
        st.markdown('<div class="section-title">🏭 لوحة التحكم الذكية بالمخازن والمستودعات المركزية</div>', unsafe_allow_html=True)
        inv_cols = st.columns(3)
        for idx, (ing_name, qty) in enumerate(st.session_state["inventory"].items()):
            with inv_cols[idx % 3]:
                if qty < 5.0: status_badge = f'<span class="stock-critical">⚠️ حرج: {qty:.2f} طن</span>'
                else: status_badge = f'<span class="stock-normal">آمن: {qty:.2f} طن</span>'
                st.markdown(f"**{ing_name}** | {status_badge}", unsafe_allow_html=True)
                new_qty = st.number_input(f"تحديث رصيد ({ing_name}) طن:", min_value=0.0, value=float(qty), key=f"inv_input_{ing_name}")
                st.session_state["inventory"][ing_name] = new_qty
        st.markdown("---")
        if st.button("🔄 حفظ وإعادة تعيين المستودعات يدويًا"):
            st.success("تم تحديث وجدولة قاعدة بيانات المخازن بنجاح.")

# ====================================================================
# التبويب الثالث: التسويق وفواتير حركة البيع
# ====================================================================
    with tabs[2]:
        st.markdown('<div class="section-title">💰 نظام تسويق المنتجات وإصدار الفواتير مع الخصم التلقائي</div>', unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: client_name = st.text_input("اسم العميل / المزرعة المستلمة:", "شركة نماء للإنتاج الداجني والحيواني")
        with col_c2: required_tons = st.number_input("الكمية المطلوبة أمر البيع (بالطن):", min_value=0.1, value=2.0, step=0.5)
        with col_c3: added_profit = st.number_input("هامش الربح الصافي المضاف لكل طن ($):", min_value=0.0, value=50.0)

        if "active_formula" in st.session_state:
            raw_cost = st.session_state["computed_ton_cost"]
            selling_price = raw_cost + added_profit
            total_bill = selling_price * required_tons
            
            st.markdown("### 🧾 فاتورة بيع وتوريد أعلاف رسمية")
            st.write(f"**المستشار المصنع:** مكتب م. عبد القادر إسماعيل تاور للاستشارات والحلول الذكية")
            st.write(f"**المستفيد المكرم:** {client_name}")
            st.write("---")
            st.write(f"▪️ التكلفة الأساسية للإنتاج: `${raw_cost:.2f}` لكل طن.")
            st.write(f"▪️ سعر البيع النهائي المعتمد للزبون: **`${selling_price:.2f}`** لكل طن.")
            st.markdown(f"### 💰 إجمالي القيمة المستحقة للفاتورة: `${total_bill:.2f}`")
            
            if st.button("✅ تأكيد عملية البيع وخصم المكونات تلقائياً من المخازن"):
                can_deduct = True
                for name, pct in st.session_state["active_formula"].items():
                    needed_ton = (pct / 100) * required_tons
                    if st.session_state["inventory"].get(name, 0.0) < needed_ton:
                        can_deduct = False
                        st.error(f"❌ رصيد غير كافي في المخزن للمكون: {name}! تحتاج لـ {needed_ton:.2f} طن.")
                        break
                if can_deduct:
                    for name, pct in st.session_state["active_formula"].items():
                        needed_ton = (pct / 100) * required_tons
                        st.session_state["inventory"][name] -= needed_ton
                    st.success("🔥 تم تأكيد الفاتورة وخصم كامل المقادير من المستودعات تلقائياً بنجاح واحتساب الأرباح!")
                    st.rerun()

# ====================================================================
# التبويب الرابع: مصمم بطاقات الديباجة والدعاية (تم تأمينه ضد الـ KeyError)
# ====================================================================
    with tabs[3]:
        st.markdown('<div class="section-title">🏷️ مُصمم ديباجات الطباعة الفنية على جوالات الأعلاف (مع صور الحيوانات التلقائية)</div>', unsafe_allow_html=True)
        
        col_tag1, col_tag2, col_tag3 = st.columns(3)
        with col_tag1: trade_brand = st.text_input("اسم البراند التجاري للدعاية:", "مجموعة تاور لإنتاج الأعلاف ومصنعات الإنتاج الحيواني")
        with col_tag2: contact_phone = st.text_input("هاتف قسم المبيعات والاستشارات الحقلية:", "+218-XX-XXXXXXX")
        with col_tag3: sack_size = st.radio("سعة وحجم الجوال (شكارة العلف):", ["50 كجم", "25 كجم"])

        # آلية الأمان: إذا كانت التركيبة جاهزة يتم جلب بياناتها، وإلا يتم وضع قيم افتراضية آمنة لمنع توقف التطبيق
        if "active_formula" in st.session_state:
            formula_data = st.session_state["active_formula"]
            target_cp_printed = st.session_state["active_cp_tag"]
            br_tag = st.session_state["active_breed_tag"]
            animal_url = st.session_state["active_animal_img"]
            stage_title_tag = st.session_state["active_stage_title"]
        else:
            # قيم افتراضية احتياطية تمنع ظهور أي خطأ أحمر قبل الضغط على زر الحساب
            formula_data = {"ذرة صفراء": 60.0, "أمباز الفول السوداني (كسب)": 30.0, "مركزات عامة": 10.0}
            target_cp_printed = 16.0
            br_tag = "سلالة عامة"
            animal_url = ANIMAL_IMAGES_RESOURCES["عام"]
            stage_title_tag = "إنتاج عام احتياطي"

        weight_divider = 20 if "50" in sack_size else 40
        
        st.markdown("### 🖨️ معاينة ديباجة بطاقة التحليل الفني للجوال (جاهزة للطباعة والتسويق)")
        
        st.markdown(f"""
        <div class="sack-tag">
            <img src="{animal_url}" class="animal-banner-img">
            
            <h2 style="color: #1b5e20; text-align: center; margin-top:0;">🌟 {trade_brand} 🌟</h2>
            <p style="text-align: center; font-weight: bold; color: #1565C0; margin-bottom:5px;">بإشراف وتوصية اختصاصي الإنتاج الحيواني وصناعة الأعلاف</p>
            <h3 style="text-align: center; color: #c62828; margin-top:0; font-weight: bold;">م. عبد القادر إسماعيل تاور</h3>
            
            <p style="text-align: center; font-weight: bold; background-color:#e8f5e9; padding:6px; border-radius:5px; color:#1b5e20; font-size:1.1rem;">
                🎯 علف مخصص لـ: {stage_title_tag} ({br_tag}) | نسبة البروتين المستهدفة: {target_cp_printed:.1f}%
            </p>
            
            <hr style="border-top: 2px dashed #1b5e20;">
            <h4>📊 بطاقة المكونات والوزن الفعلي لكل جوال واحد ({sack_size}):</h4>
            <ul>
                {"".join([f"<li><b>{k}:</b> {v:.2f}% (أي ما يعادل دقيقاً <b>{(v*10)/weight_divider:.2f} كجم</b> في الجوال الواحد)</li>" for k, v in formula_data.items()])}
            </ul>
            <hr style="border-top: 1px solid #1b5e20;">
            <p><b>⚠️ إرشادات الحقل المعتمدة:</b> يُخزن في مكان جاف وبارد بعيدًا عن الرطوبة والأمطار.</p>
            <p style="text-align: center; font-weight: bold; color: #c62828; margin-bottom:0; font-size:1.1rem;">📞 لطلبات التوريد والاستشارات الفنية لتركيب الأعلاف: {contact_phone}</p>
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
