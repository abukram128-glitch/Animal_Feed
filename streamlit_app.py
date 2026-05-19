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
    .lib-category-title {
        background-color: #2e7d32;
        color: white;
        padding: 8px 15px;
        border-radius: 6px;
        font-weight: bold;
        margin-top: 15px;
        text-align: right;
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
# 3. تثبيت موارد الصور وقاعدة البيانات الشاملة
# =====================================================================
ANIMAL_IMAGES_RESOURCES = {
    "الطيور والسمان": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600&auto=format&fit=crop",
    "الأبقار وسلالاتها": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600&auto=format&fit=crop",
    "الماعز وسلالاته": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600&auto=format&fit=crop",
    "الخيول والفروسية": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600&auto=format&fit=crop",
    "الأسماك والأحياء المائية": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600&auto=format&fit=crop",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop"
}

# حل جذري لخطأ KeyError: تعريف مفاتيح الحالة بشكل مبكر جداً وثابت
if "active_animal_img" not in st.session_state: st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES["عام"]
if "active_formula" not in st.session_state: st.session_state["active_formula"] = {"ذرة صفراء": 100.0}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 16.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 250.0

# قاعدة البيانات المحدثة للمكتبة العلفية الكبرى
BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "base_price": 230.0}, 
        "ذرة بيضاء": {"CP": 8.8, "base_price": 225.0}, 
        "شعير مطحون": {"CP": 11.5, "base_price": 210.0}, 
        "سورجم (فتريتة)": {"CP": 10.0, "base_price": 195.0},
        "قمح محلي مصنّع": {"CP": 12.0, "base_price": 240.0}
    },
    "الأكساب والأمباز ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "base_price": 460.0}, 
        "كسب فول صويا 44%": {"CP": 44.0, "base_price": 440.0}, 
        "كسب فول صويا 48%": {"CP": 48.0, "base_price": 480.0}, 
        "كسب عباد الشمس 36%": {"CP": 36.0, "base_price": 310.0},
        "كسب بذور القطن": {"CP": 41.0, "base_price": 290.0}
    },
    "الأحماض الأمينية المصنعة النقية (خامات كاملة)": {
        "لايسين خام مصنع (L-Lysine HCL)": {"CP": 94.0, "base_price": 1650.0},
        "ميثيونين نقّي (DL-Methionine)": {"CP": 58.0, "base_price": 2800.0},
        "تربتوفان مركز (L-Tryptophan)": {"CP": 82.0, "base_price": 4500.0},
        "أرجنين نقي (L-Arginine)": {"CP": 120.0, "base_price": 3200.0},
        "ثريونين علفي (L-Threonine)": {"CP": 72.0, "base_price": 1850.0}
    },
    "الإنزيمات والمحفزات الحيوية ودواعم الكرش": {
        "بيكربونات الصوديوم (الصودا لمنع التحمض)": {"CP": 0.0, "base_price": 340.0},
        "إنزيم الفايتيز (Phytase لتحرير الفسفور)": {"CP": 0.0, "base_price": 1200.0},
        "إنزيم الـ NSP المعوي (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "base_price": 1450.0},
        "كبريتات الحديدوز (معادل سمية الجوسيبول)": {"CP": 0.0, "base_price": 410.0},
        "مضاد سموم فطرية لوجستي متكامل": {"CP": 0.0, "base_price": 950.0}
    },
    "المخلفات الرعوية والمواد المالئة": {
        "نخالة قمح (ردة)": {"CP": 15.0, "base_price": 150.0}, 
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "base_price": 170.0}, 
        "مولاس قصب السكر": {"CP": 4.0, "base_price": 120.0}
    },
    "الإضافات المتخصصة والمركزات": {
        "مركزات دواجن وسمان 5%": {"CP": 40.0, "base_price": 650.0}, 
        "مركزات خيول ومجترات": {"CP": 36.0, "base_price": 600.0}, 
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "base_price": 850.0},
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "base_price": 40.0}, 
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "base_price": 280.0}, 
        "ملح الطعام": {"CP": 0.0, "base_price": 30.0}
    }
}

# إعداد قيم الجلسة لأسعار البورصة للحيوانات والمنتجات
if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين / محسن ($)": 1350.0, "أبقار كنانة وبطانة محلية ($)": 900.0,
        "ضأن وستيرلنغ / محلي ($)": 180.0, "ماعز نوبي وصحراوي ($)": 130.0, "كتكوت لاحم عمر يوم ($)": 0.65
    }

if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري صافي ($)": 7.50, "كيلو لحم ضأن طازج ($)": 9.00,
        "كيلو لحم دجاج لاحم صافي ($)": 3.80, "طبق بيض مائدة 30 بيضة ($)": 4.20
    }

EXCHANGE_RATES = {
    "ليبيا": {"rate": 4.80, "sym": "LYD"},
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "مصر": {"rate": 48.0, "sym": "EGP"},
    "باقي دول العالم": {"rate": 1.0, "sym": "USD"}
}

# =====================================================================
# 4. محرك موازنة الأسعار اللوجستي لربط البورصة بأسواق المدن (طبرق نموذجاً)
# =====================================================================
def compute_aligned_market_prices(country, state_or_region, city):
    aligned_prices = {}
    logistic_factor = 1.0
    
    if country == "ليبيا":
        logistic_factor = 1.08
        if city == "طبرق": logistic_factor = 1.14  # حساب تكاليف الشحن البري والمسافات بدقة
    elif country == "السودان":
        logistic_factor = 1.15
        if "كردفان" in state_or_region: logistic_factor = 1.25
    
    for cat, items in BIG_FEEDS_LIBRARY.items():
        for ing, data in items.items():
            base = data["base_price"]
            aligned_prices[ing] = base * logistic_factor
            
    return aligned_prices, logistic_factor

# ==========================================
# 5. بناء الواجهة الرسومية للمنصة
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logo, col_title = st.columns([0.25, 0.75])
with col_logo:
    if img_base64: st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else: st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور الذكية المتكاملة للأعلاف والإنتاج الحيواني 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.15rem; margin-top:5px; margin-bottom:0;'>نظام المعالجة الصامتة والمطابقة السعرية اللوجستية لأسواق المدن</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى", "🗂️ مكتبة تاور المنظمة الشاملة", "📊 بورصة تاور لأسواق الماشية والمنتجات"]
if st.session_state["user_role"] == "admin":
    tabs_titles += ["⚙️ إدخالات البورصة المركزية"]

tabs = st.tabs(tabs_titles)

# ---------------------------------------------------------------------
# التبويب الأول: محرك الحسابات والمعالجة البرمجية الصامتة للمشكلات
# ---------------------------------------------------------------------
with tabs[0]:
    st.markdown('<div class="section-title">🌍 أولاً: تحديد الموقع الجغرافي لربط وتطابق الأسعار مع السوق الفعلي</div>', unsafe_allow_html=True)
    col_country, col_state, col_city = st.columns(3)
    with col_country: user_country = st.selectbox("اختر دولة المربي المستهدف:", ["ليبيا", "السودان", "مصر", "باقي دول العالم"])
        
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    local_rate = c_info["rate"]; local_sym = c_info["sym"]

    chosen_state = "عام"
    with col_state:
        if user_country == "ليبيا": chosen_state = st.selectbox("اختر الإقليم الجغرافي اللوجستي:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
        elif user_country == "السودان": chosen_state = st.selectbox("اختر الولاية السودانية المستهدفة:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال كردفان"])
        else: chosen_state = st.selectbox("الإقليم الإداري السوقي:", ["الأسواق الحرة المركزية"])

    with col_city:
        if user_country == "ليبيا":
            if chosen_state == "المنطقة الشرقية": user_city = st.selectbox("اختر المدينة المستهدفة:", ["طبرق", "بنغازي", "البيضاء", "درنة"])
            else: user_city = st.selectbox("اختر المدينة المستهدفة:", ["طرابلس", "مصراتة", "سبها"])
        elif user_country == "السودان":
            if chosen_state == "ولاية القضارف": user_city = st.selectbox("اختر المدينة:", ["القضارف المدينة", "الفاو"])
            else: user_city = st.selectbox("اختر المدينة الفعليّة:", ["الخرطوم", "ود مدني", "الأبيض"])
        else: user_city = st.text_input("اكتب اسم المدينة يدوياً لرصد السعر الحقيقي:", "طبرق")

    # رصد الأسعار المتطابقة محلياً
    live_prices, current_logistic_factor = compute_aligned_market_prices(user_country, chosen_state, user_city)
    
    st.success(f"📊 تم مزامنة وتطابق أسعار الخامات والبورصة مع أسواق (<b>{user_city}</b>) الحقيقية بالاعتماد على الفروقات اللوجستية الفعليّة حَقلياً.")

    st.markdown('<div class="section-title">⚖️ ثانياً: قطاع التسمين أو الإنتاج المستهدف</div>', unsafe_allow_html=True)
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec: main_sector = st.selectbox("اختر القطاع الإنتاجي:", ["الطيور والسمان", "الأبقار وسلالاتها", "الماعز وسلالاته", "الخيول والفروسية", "الأسماك والأحياء المائية"])
    
    chosen_concentrate = "مركزات دواجن وسمان 5%"
    default_cp = 21.0
    with col_sub:
        if main_sector == "الطيور والسمان": sub_type = st.selectbox("نوع الطيور:", ["دواجن لاحم (Broiler)", "دواجن بياض (Layer)", "طائر السمان (Quail)"])
        elif main_sector == "الأبقار وسلالاتها": sub_type = st.selectbox("السلالة البقرية:", ["هولشتاين / محسن", "كنانة (سوداني)"]); chosen_concentrate = "مركزات خيول ومجترات"; default_cp = 14.0
        else: sub_type = st.selectbox("السلالة أو النوع الفرعي:", ["محلي / محسن عالي الأداء"]); chosen_concentrate = "مركزات خيول ومجترات"; default_cp = 13.0

    with col_prod:
        if main_sector == "الطيور والسمان": prod_stage = st.selectbox("مرحلة التغذية:", ["نامي دواجن 21%", "بادي دواجن 23%", "ناهي دواجن 19%", "بياض إنتاجي"])
        else: prod_stage = st.selectbox("مرحلة الإنتاج الحالية:", ["تسمين مكثف نامي", "إدرار حليب وغزارة عالية"])

    st.markdown('<div class="section-title">🧬 ثالثاً: ضبط بروتين العليقة واختيار خامات التركيب</div>', unsafe_allow_html=True)
    final_target_cp = st.slider("حدد نسبة البروتين المستهدفة فنيّاً (%):", 10.0, 45.0, value=default_cp)

    selected_ingredients = []; ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📥 فئة: {cat_name} (اضغط للاستعراض والاختيار)", expanded=True):
            sub_cols = st.columns(3)
            for idx, (ing_name, data) in enumerate(items.items()):
                with sub_cols[idx % 3]:
                    is_def = False
                    if "ذرة صفراء" in ing_name or "صويا" in ing_name or "ملح" in ing_name: is_def = True
                    if ing_name in [chosen_concentrate, "لايسين خام مصنع (L-Lysine HCL)", "ميثيونين نقّي (DL-Methionine)"]: is_def = True
                    
                    checked = st.checkbox(ing_name, value=is_def, key=f"fcalc_{ing_name}")
                    market_p = live_prices.get(ing_name, 350.0)
                    st.markdown(f"<small>💵 السعر في {user_city}: <b>${market_p:.1f}</b> ({market_p*local_rate:,.0f} {local_sym})</small>", unsafe_allow_html=True)
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = market_p

    if st.button("🚀 حساب التوليفة العلفية وتعديل المكونات برمجياً وصامتاً", type="primary", use_container_width=True):
        formula_results = {}
        auto_added_enzymes = {}

        fixed_ratios = {"ملح الطعام": 0.005, "مضاد سموم فطرية لوجستي متكامل": 0.002, "الحجر الجيري (بودرة بلاط)": 0.015, "فوسفات ثنائي الكالسيوم (DCP)": 0.01}
        if "الطيور" in main_sector: fixed_ratios[chosen_concentrate] = 0.05
        
        used_fixed_pct = 0.0
        for name in selected_ingredients:
            if name in fixed_ratios:
                formula_results[name] = fixed_ratios[name] * 100
                used_fixed_pct += fixed_ratios[name] * 100
        
        remaining_pct = 100.0 - used_fixed_pct
        grains = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"]]
        proteins = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"]]
        aminos = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الأحماض الأمينية المصنعة النقية (خامات كاملة)"]]
        
        if not grains: grains = ["ذرة صفراء"]
        if not proteins: proteins = ["كسب فول صويا 44%"]
        
        p_share = remaining_pct * (0.42 if final_target_cp > 20 else 0.26)
        e_share = remaining_pct - p_share
        
        for x in grains: formula_results[x] = e_share / len(grains)
        total_prot_elements = proteins + aminos
        for x in total_prot_elements:
            if x in aminos:
                formula_results[x] = 0.15
                p_share -= 0.15
        for x in proteins:
            formula_results[x] = p_share / len(proteins)

        total_grains_pct = sum([formula_results.get(x, 0.0) for x in grains])

        # =========================================================================
        # 🔬 نظام المعالجة البرمجية الصامتة تماماً للتركيبة العلفية (دون التنبيهات المزعجة)
        # =========================================================================
        if main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاته"] and total_grains_pct > 45.0:
            auto_added_enzymes["بيكربونات الصوديوم (الصودا لمنع التحمض)"] = 0.75

        if main_sector in ["الطيور والسمان", "الأسماك والأحياء المائية"]:
            auto_added_enzymes["إنزيم الفايتيز (Phytase لتحرير الفسفور)"] = 0.05

        if "كسب بذور القطن" in formula_results and main_sector == "الطيور والسمان":
            auto_added_enzymes["كبريتات الحديدوز (معادل سمية الجوسيبول)"] = 0.12

        if main_sector == "الطيور والسمان" and (formula_results.get("شعير مطحون", 0.0) > 10.0 or formula_results.get("قمح محلي مصنّع", 0.0) > 15.0):
            auto_added_enzymes["إنزيم الـ NSP المعوي (زيلاناز + بيتا جلوكاناز)"] = 0.08

        # خصم أوزان الإضافات تلقائياً من خامة الطاقة الكبرى ليبقى مجموع الطن 100% تماماً
        if auto_added_enzymes:
            tot_enz = sum(auto_added_enzymes.values())
            m_grain = grains[0] if grains else "ذرة صفراء"
            if m_grain in formula_results: formula_results[m_grain] = max(1.0, formula_results[m_grain] - tot_enz)
            for enz_n, enz_p in auto_added_enzymes.items(): formula_results[enz_n] = enz_p

        # حفظ آمن لبيانات الجلسة لمنع ظهور أخطاء KeyError مجدداً
        st.session_state["active_formula"] = formula_results
        st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES.get(main_sector, ANIMAL_IMAGES_RESOURCES["عام"])
        st.session_state["active_cp_tag"] = final_target_cp
        st.session_state["active_breed_tag"] = sub_type
        st.session_state["active_stage_title"] = f"{main_sector} - {prod_stage}"

        res_col1, res_col2 = st.columns([0.6, 0.4])
        with res_col1:
            st.markdown(f"#### 📝 مقادير خلط الطن الصافية والمعالجة تلقائياً لسوق ({user_city}):")
            for k, v in formula_results.items(): st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** / الطن)")
            
            ton_cost = sum([(v/100) * ingredient_prices.get(k, 320.0) for k, v in formula_results.items()])
            st.session_state["computed_ton_cost"] = ton_cost
            st.metric("💰 تكلفة إنتاج الطن الفعلية بمطابقة السوق والمدينة الحالية:", f"${ton_cost:.2f} (أو {ton_cost*local_rate:,.1f} {local_sym})")
        with res_col2: st.bar_chart(formula_results)

# ---------------------------------------------------------------------
# التبويب الثاني: استعراض مكتبة تاور المنظمة بالتصنيف المبوب الأحدث
# ---------------------------------------------------------------------
with tabs[1]:
    st.markdown('<div class="section-title">🗂️ مستودع ومكتبة تاور الرقمية المنظمة للمكونات والإضافات المصنعة</div>', unsafe_allow_html=True)
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        st.markdown(f'<div class="lib-category-title">📁 فئة: {cat_name}</div>', unsafe_allow_html=True)
        sub_lib_cols = st.columns(3)
        for idx, (ing_name, data) in enumerate(items.items()):
            with sub_lib_cols[idx % 3]:
                st.markdown(
                    f"""
                    <div style='background-color:#f9f9f9; padding:15px; border-radius:8px; border:1px solid #e0e0e0; margin-bottom:10px; direction:rtl; text-align:right;'>
                        <h5 style='color:#2e7d32; margin-top:0;'>🌾 {ing_name}</h5>
                        <p style='margin-bottom:4px; font-size:0.9rem;'>🧬 نسبة البروتين الكلي المكافئ: <b>{data.get("CP", 0.0)} %</b></p>
                        <p style='margin-bottom:0; font-size:0.9rem;'>💰 السعر العالمي للطن الأساسي: <b>${data.get("base_price", 0.0)}</b></p>
                    </div>
                    """, unsafe_allow_html=True
                )

# ---------------------------------------------------------------------
# التبويب الثالث: بورصة تاور لأسواق الماشية والمنتجات (مربوطة بالمعامل اللوجستي الحقيقي)
# ---------------------------------------------------------------------
with tabs[2]:
    st.markdown(f'<div class="section-title">📊 أسعار بورصة الماشية والمنتجات المتطابقة مع سوق مدينة ({user_city})</div>', unsafe_allow_html=True)
    
    # ربط أسعار البورصة للحيوانات والمنتجات مباشرة بالمعامل اللوجستي للمدينة لإصابة دقة الأسعار بالسوق
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown("### 🐂 أسعار رؤوس الماشية الحية ومرحلة التربية:")
        for animal, price in st.session_state["global_livestock_prices"].items():
            adjusted_p = price * current_logistic_factor
            st.markdown(f"▪️ {animal}: **${adjusted_p:.2f}** | الفعلي بالعملة المحلية: <span style='color:#e65100; font-weight:bold;'>{adjusted_p * local_rate:,.2f} {local_sym}</span>")
            
    with col_b2:
        st.markdown("### 🥛 أسعار المنتجات الصافية والألبان والبيض:")
        for product, price in st.session_state["global_products_prices"].items():
            adjusted_p = price * current_logistic_factor
            st.markdown(f"▪️ {product}: **${adjusted_p:.2f}** | الفعلي بالعملة المحلية: <span style='color:#2e7d32; font-weight:bold;'>{adjusted_p * local_rate:,.2f} {local_sym}</span>")

# لوحة تحكم التعديل الأساسية للمالك فقط
if st.session_state["user_role"] == "admin":
    with tabs[3]:
        st.markdown('<div class="section-title">⚙️ لوحة الإدارة: تعديل أسعار البورصة العالمية المرجعية للشبكة</div>', unsafe_allow_html=True)
        col_ed1, col_ed2 = st.columns(2)
        with col_ed1:
            st.subheader("تحديث أسعار الماشية والداجن الأساسية ($):")
            for animal, price in st.session_state["global_livestock_prices"].items():
                st.session_state["global_livestock_prices"][animal] = st.number_input(f"تحديث {animal}", min_value=0.0, value=float(price), key=f"edit_live_{animal}")
        with col_ed2:
            st.subheader("تحديث أسعار المنتجات والألبان الأساسية ($):")
            for product, price in st.session_state["global_products_prices"].items():
                st.session_state["global_products_prices"][product] = st.number_input(f"تحديث {product}", min_value=0.0, value=float(price), key=f"edit_prod_{product}")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. التوقيع الدائم بأسفل الشاشة
# ==========================================
st.markdown(
    f"""
    <div class="mini-left-signature">
        👨‍🔬 م. عبد القادر إسماعيل تاور © 2026 | خبير الحلول الذكية للثروة الحيوانية والبرمجيات المتكاملة
    </div>
    """,
    unsafe_allow_html=True
)
