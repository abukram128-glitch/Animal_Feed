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
# 3. الهيكل الشامل لمكتبة تاور المحدثة (طاقة، بروتين، أمينو، إنزيمات، مالئة)
# =====================================================================
BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "priority": 1.3, "base_price": 230.0}, 
        "ذرة بيضاء": {"CP": 8.8, "priority": 0.9, "base_price": 225.0}, 
        "شعير مطحون": {"CP": 11.5, "priority": 1.1, "base_price": 210.0}, 
        "سورجم (فتريتة)": {"CP": 10.0, "priority": 1.0, "base_price": 195.0},
        "قمح محلي مصنّع": {"CP": 12.0, "priority": 1.05, "base_price": 240.0}
    },
    "الأكساب والأمباز ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "prio_prot": 1.1, "base_price": 460.0}, 
        "كسب فول صويا 44%": {"CP": 44.0, "prio_prot": 1.2, "base_price": 440.0}, 
        "كسب فول صويا 48%": {"CP": 48.0, "prio_prot": 1.25, "base_price": 480.0}, 
        "كسب عباد الشمس 36%": {"CP": 36.0, "prio_prot": 0.85, "base_price": 310.0},
        "كسب بذور القطن": {"CP": 41.0, "prio_prot": 0.8, "base_price": 290.0}
    },
    "الأحماض الأمينية المصنعة النقية (خامات كاملة)": {
        "لايسين خام مصنع (L-Lysine HCL)": {"CP": 94.0, "prio_prot": 2.0, "base_price": 1650.0},
        "ميثيونين نقّي (DL-Methionine)": {"CP": 58.0, "prio_prot": 2.5, "base_price": 2800.0},
        "تربتوفان مركز (L-Tryptophan)": {"CP": 82.0, "prio_prot": 2.2, "base_price": 4500.0},
        "أرجنين نقي (L-Arginine)": {"CP": 120.0, "prio_prot": 2.1, "base_price": 3200.0},
        "ثريونين علفي (L-Threonine)": {"CP": 72.0, "prio_prot": 1.8, "base_price": 1850.0}
    },
    "الإنزيمات والمحفزات الحيوية ودواعم الكرش": {
        "بيكربونات الصوديوم (الصودا لمنع التحمض)": {"CP": 0.0, "base_price": 340.0},
        "إنزيم الفايتيز (Phytase لتحرير الفسفور)": {"CP": 0.0, "base_price": 1200.0},
        "إنزيم الـ NSP المعوي (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "base_price": 1450.0},
        "كبريتات الحديدوز (معادل سمية الجوسيبول)": {"CP": 0.0, "base_price": 410.0},
        "مضاد سموم فطرية لوجستي متكامل": {"CP": 0.0, "base_price": 950.0}
    },
    "المخلفات الرعوية والمواد المالئة": {
        "نخالة قمح (ردة)": {"CP": 15.0, "prio_fill": 1.2, "base_price": 150.0}, 
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "prio_fill": 0.9, "base_price": 170.0}, 
        "مولاس قصب السكر": {"CP": 4.0, "prio_fill": 1.0, "base_price": 120.0}
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

if "inventory" not in st.session_state:
    st.session_state["inventory"] = {}
    for cat, items in BIG_FEEDS_LIBRARY.items():
        for k in items: st.session_state["inventory"][k] = 15.0

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
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "ليبيا": {"rate": 4.80, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"},
    "باقي دول العالم": {"rate": 1.0, "sym": "USD"}
}

# =====================================================================
# 4. محرك موازنة الأسعار ومطابقة السوق الفعلي بدقة طبقاً للموقع والمدينة
# =====================================================================
def compute_aligned_market_prices(country, state_or_region, city):
    aligned_prices = {}
    
    # تحديد المعامل اللوجستي للشحن والندرة لكل مدينة لمنع التفاوت مع السوق الواقعي
    logistic_multiplier = 1.0
    
    if country == "ليبيا":
        logistic_multiplier = 1.08  # معامل الدولة العام
        if city == "طبرق": 
            logistic_multiplier = 1.14  # ندرة وزيادة تكلفة النقل البري للمناطق الشرقية والحدودية
    elif country == "السودان":
        logistic_multiplier = 1.15
        if "كردفان" in state_or_region or city in ["الفاشر", "الدمازين"]:
            logistic_multiplier = 1.25  # زيادة ملموسة نتيجة الظروف اللوجستية الراهنة وتكلفة الوقود لترحيل خامات العلف
        elif state_or_region in ["ولاية القضارف", "ولاية الجزيرة"]:
            logistic_multiplier = 1.10  # مناطق إنتاج زراعي مباشر (أسعار مخفضة للحبوب والأمباز)
    elif country == "مصر":
        logistic_multiplier = 1.05

    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        for ing_name, data in items.items():
            base = data["base_price"]
            # تعديل أسعار الخامات المنتجة محلياً بشكل مستقل عن المستورد لتطابق الفعلي
            if country == "السودان" and ing_name in ["سورجم (فتريتة)", "أمباز الفول السوداني (كسب)"]:
                if "كردفان" in state_or_region or "القضارف" in state_or_region:
                    base *= 0.80  # سعر المزرعة منخفض في مناطق الإنتاج
            
            aligned_prices[ing_name] = base * logistic_multiplier
            
    return aligned_prices

# تأمين قيم جلسة العمل (Session State) تفادياً لأخطاء الـ KeyError الحاصلة سابقاً
if "active_formula" not in st.session_state: st.session_state["active_formula"] = {"ذرة صفراء": 60.0}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 16.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_animal_img" not in st.session_state: st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES = {"عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop"}["عام"]
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0

# ==========================================
# 5. بناء الواجهة الرسومية والمكتبة المنظمة
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logo, col_title = st.columns([0.25, 0.75])
with col_logo:
    if img_base64: st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else: st.markdown(f'<img src="https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=600" class="profile-img-style">', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور الذكية المتكاملة للأعلاف والإنتاج الحيواني 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.15rem; margin-top:5px; margin-bottom:0;'>المكتبة الرقمية المنظمة للأحماض الأمينية والإنزيمات ومطابقة الأسعار الميدانية الحقيقية</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى", "🗂️ مكتبة تاور المنظمة الشاملة"]
if st.session_state["user_role"] == "admin":
    tabs_titles += ["📊 بورصة التحكم وإدارة الأسعار", "🏭 إدارة المستودعات"]

tabs = st.tabs(tabs_titles)

# ====================================================================
# التبويب الأول: النمذجة ومحرك التركيب ومطابقة الأسعار في المدن
# ====================================================================
with tabs[0]:
    st.markdown('<div class="section-title">🌍 أولاً: تحديد الموقع الجغرافي لضبط تطابق الأسعار مع السوق الفعلي</div>', unsafe_allow_html=True)
    col_country, col_state, col_city = st.columns(3)
    with col_country: user_country = st.selectbox("اختر دولة المربي المستهدف:", ["ليبيا", "السودان", "مصر", "باقي دول العالم"])
        
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    local_rate = c_info["rate"]; local_sym = c_info["sym"]

    chosen_state = "عام"
    with col_state:
        if user_country == "ليبيا": chosen_state = st.selectbox("اختر الإقليم الجغرافي اللوجستي:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
        elif user_country == "السودان": chosen_state = st.selectbox("اختر الولاية السودانية المستهدفة:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال كردفان", "ولاية جنوب كردفان", "ولاية البحر الأحمر"])
        else: chosen_state = st.selectbox("الإقليم الإداري السوقي:", ["الأسواق الحرة المركزية"])

    with col_city:
        if user_country == "ليبيا":
            if chosen_state == "المنطقة الشرقية": user_city = st.selectbox("اختر المدينة المستهدفة:", ["طبرق", "بنغازي", "البيضاء", "درنة"])
            else: user_city = st.selectbox("اختر المدينة المستهدفة:", ["طرابلس", "مصراتة", "سبها"])
        elif user_country == "السودان":
            if chosen_state == "ولاية القضارف": user_city = st.selectbox("اختر المدينة:", ["القضارف المدينة", "الفاو"])
            elif chosen_state == "ولاية شمال كردفان": user_city = st.selectbox("اختر المدينة:", ["الأبيض", "أم روابة"])
            elif chosen_state == "ولاية البحر الأحمر": user_city = st.selectbox("اختر المدينة:", ["بورتسودان", "سواكن"])
            else: user_city = st.selectbox("اختر المدينة الفعليّة:", ["الخرطوم", "ود مدني", "كادوقلي"])
        else: user_city = st.text_input("اكتب اسم المدينة يدوياً لرصد السعر الحقيقي:", "طبرق")

    # حساب وتحديث الأسعار المتطابقة مع سوق المدينة الفعلي مباشرة
    live_prices = compute_aligned_market_prices(user_country, chosen_state, user_city)
    
    st.info(f"💡 <b>نظام مطابقة الأسعار الميدانية:</b> تم حساب أسعار السوق الحقيقية في مدينة (<b>{user_city}</b>) تلقائياً بالاعتماد على الفروقات اللوجستية وتكلفة الشحن البري الفعلي.")

    st.markdown('<div class="section-title">⚖️ ثانياً: قطاع التسمين أو الإنتاج المستهدف</div>', unsafe_allow_html=True)
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec: main_sector = st.selectbox("اختر القطاع الإنتاجي:", ["الطيور والسمان", "الأبقار وسلالاتها", "الماعز وسلالاته", "الخيول والفروسية", "الأسماك والأحياء المائية"])
    
    chosen_concentrate = "مركزات دواجن وسمان 5%"
    default_cp = 21.0
    with col_sub:
        if main_sector == "الطيور والسمان": sub_type = st.selectbox("نوع الطيور:", ["دواجن لاحم (Broiler)", "دواجن بياض (Layer)", "طائر السمان (Quail)"])
        elif main_sector == "الأبقار وسلالاتها": sub_type = st.selectbox("السلالة البقرية:", ["هولشتاين / محسن", "كنانة (سوداني)", "بطانة (مدر)"]); chosen_concentrate = "مركزات خيول ومجترات"; default_cp = 14.0
        else: sub_type = st.selectbox("السلالة أو النوع الفرعي:", ["محلي / محسن عالي الأداء"]); chosen_concentrate = "مركزات خيول ومجترات"; default_cp = 13.0

    with col_prod:
        if main_sector == "الطيور والسمان": prod_stage = st.selectbox("مرحلة التغذية:", ["نامي دواجن 21%", "بادي دواجن 23%", "ناهي دواجن 19%", "بياض إنتاجي"])
        else: prod_stage = st.selectbox("مرحلة الإنتاج الحالية:", ["تسمين مكثف نامي", "إدرار حليب وغزارة عالية"])

    st.markdown('<div class="section-title">🧬 ثالثاً: ضبط بروتين العليقة واختيار خامات التركيب من المكتبة المحدثة</div>', unsafe_allow_html=True)
    final_target_cp = st.slider("حدد نسبة البروتين المستهدفة فنيّاً (%):", 10.0, 45.0, value=default_cp)

    selected_ingredients = []; ingredient_prices = {}
    
    # عرض منظم وفخم للخامات أثناء التركيب
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

    if st.button("🚀 حساب التوليفة العلفية الذكية وتدقيق العلل والإنزيمات الإلزامية", type="primary", use_container_width=True):
        formula_results = {}
        mandatory_warnings = []
        auto_added_enzymes = {}

        # الإضافات الثابتة فنياً في التركيبة لحماية الطيور والحيوانات
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
        
        # توزيع الطاقة
        for x in grains: formula_results[x] = e_share / len(grains)
        # توزيع البروتين الكلي شاملاً أوزان الأحماض الأمينية المدخلة
        total_prot_elements = proteins + aminos
        for x in total_prot_elements:
            if x in aminos:
                formula_results[x] = 0.15  # نسب حيوية دقيقة للأمينو المصنع (1.5 كجم بالطن)
                p_share -= 0.15
        for x in proteins:
            formula_results[x] = p_share / len(proteins)

        total_grains_pct = sum([formula_results.get(x, 0.0) for x in grains])

        # =========================================================================
        # 🔬 نظام الفحص والتشخيص الحيوي التلقائي والإلزامي للمحددات (م. عبد القادر)
        # =========================================================================
        # 1. إلزامية البيكربونات عند زيادة الحبوب والكربوهيدرات للمجترات
        if main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاته"] and total_grains_pct > 45.0:
            auto_added_enzymes["بيكربونات الصوديوم (الصودا لمنع التحمض)"] = 0.75
            mandatory_warnings.append(f"🚨 <span style='color:#b71c1c;'><b>إضافة إلزامية - بيكربونات الصوديوم:</b></span> العلة هي ارتفاع نسبة الحبوب إلى ({total_grains_pct:.1f}%)، مما يهدد بحدوث <b>حموضة الكرش الحادة والتحمض (Acidosis)</b>، تم إدراج الصودا كـ Buffer منظم لحفظ الأس الهيدروجيني للكرش.")

        # 2. إلزامية إنزيم الفايتيز لقطاع الدواجن والأسماك
        if main_sector in ["الطيور والسمان", "الأسماك والأحياء المائية"]:
            auto_added_enzymes["إنزيم الفايتيز (Phytase لتحرير الفسفور)"] = 0.05
            mandatory_warnings.append("🚨 <span style='color:#b71c1c;'><b>إضافة إلزامية - إنزيم الفايتيز (Phytase):</b></span> تم فرض الإنزيم تلقائياً برمجياً والعلة هي كسر وتفكيك <b>حمض الفايتيك (Phytic Acid)</b> النباتي لتحرير الفسفور العضوي غير المتاح أوتوماتيكياً لأمعاء الطيور والأسماك.")

        # 3. علة كسب بذور القطن (الجوسيبول الحر السام)
        if "كسب بذور القطن" in formula_results and main_sector == "الطيور والسمان":
            auto_added_enzymes["كبريتات الحديدوز (معادل سمية الجوسيبول)"] = 0.12
            mandatory_warnings.append("⚠️ <b>علة فنية معالجة:</b> كسب بذور القطن يحتوي على <b>الجوسيبول السام (Free Gossypol)</b> الذي يسبب انسداد الأمعاء وتثبيط جودة البيض، تم إدراج كبريتات الحديدوز فورياً للارتباط به برمجياً وتحييده حيوياً.")

        # 4. علة لزوجة الشعير والقمح (NSP)
        if main_sector == "الطيور والسمان" and (formula_results.get("شعير مطحون", 0.0) > 10.0 or formula_results.get("قمح محلي مصنّع", 0.0) > 15.0):
            auto_added_enzymes["إنزيم الـ NSP المعوي (زيلاناز + بيتا جلوكاناز)"] = 0.08
            mandatory_warnings.append("⚠️ <b>علة القمح والشعير اللزج:</b> تسبب السكريات غير النشوية (NSP) لزوجة عالية في الأمعاء وبراز رطب (Wet Litter)، تم ضخ إنزيم الزيلاناز المخصص لمعادلة المشكلة الهضمية.")

        # تطبيق الإنزيمات وإعادة موازنة الوزن بدقة من خامة الحبوب الكبرى ليبقى مجموع الطن 100%
        if auto_added_enzymes:
            tot_enz = sum(auto_added_enzymes.values())
            m_grain = grains[0] if grains else "ذرة صفراء"
            if m_grain in formula_results: formula_results[m_grain] = max(1.0, formula_results[m_grain] - tot_enz)
            for enz_n, enz_p in auto_added_enzymes.items(): formula_results[enz_n] = enz_p

        st.session_state["active_formula"] = formula_results
        
        # العرض النهائي للمربي
        if mandatory_warnings:
            st.markdown("### 🛠️ لوحة تشخيص العلل العلفية والتدخلات الإلزامية:")
            for warn in mandatory_warnings: st.markdown(f'<div class="warning-card">{warn}</div>', unsafe_allow_html=True)

        res_col1, res_col2 = st.columns([0.6, 0.4])
        with res_col1:
            st.write(f"#### 📝 مقادير خلط الطن المتزنة والمطابقة لسوق ({user_city}):")
            for k, v in formula_results.items(): st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** / الطن)")
            
            ton_cost = sum([(v/100) * ingredient_prices.get(k, 320.0) for k, v in formula_results.items()])
            st.session_state["computed_ton_cost"] = ton_cost
            st.metric("💰 تكلفة إنتاج الطن الفعلية في مدينتك بالمطابقة الحقيقية:", f"${ton_cost:.2f} (أو {ton_cost*local_rate:,.1f} {local_sym})")
        with res_col2: st.bar_chart(formula_results)

# ====================================================================
# التبويب الثاني: استعراض مكتبة تاور المنظمة أحدث ما يكون بالتصنيف المبوب
# ====================================================================
with tabs[1]:
    st.markdown('<div class="section-title">🗂️ مستودع ومكتبة تاور الرقمية الشاملة للمكونات والإضافات الدقيقة</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: right; color: #555;'>استعراض منظم وهندسي لكافة فئات الخامات والأحماض الأمينية والإنزيمات والعلل المرتبطة بكل خامة علفية عالمياً.</p>", unsafe_allow_html=True)
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        st.markdown(f'<div class="lib-category-title">📁 فئة: {cat_name}</div>', unsafe_allow_html=True)
        sub_lib_cols = st.columns(len(items) if len(items) <= 3 else 3)
        
        for idx, (ing_name, data) in enumerate(items.items()):
            col_idx = idx % 3
            if col_idx < len(sub_lib_cols):
                with sub_lib_cols[col_idx]:
                    st.markdown(
                        f"""
                        <div style='background-color:#f9f9f9; padding:15px; border-radius:8px; border:1px solid #e0e0e0; margin-bottom:10px; direction:rtl; text-align:right;'>
                            <h5 style='color:#2e7d32; margin-top:0;'>🌾 {ing_name}</h5>
                            <p style='margin-bottom:4px; font-size:0.9rem;'>🧬 نسبة البروتين الخام: <b>{data.get("CP", 0.0)} %</b></p>
                            <p style='margin-bottom:0; font-size:0.9rem;'>💰 السعر العالمي الأساسي: <b>${data.get("base_price", 0.0)}</b> / طن</p>
                        </div>
                        """, unsafe_allow_html=True
                    )

# التبويبات الإدارية لـ (تاور) فقط لتحديث وضبط قاعدة بيانات الأسعار
if st.session_state["user_role"] == "admin":
    with tabs[2]:
        st.markdown('<div class="section-title">📊 لوحة تحكم وتعديل بورصة الأسعار الأساسية للشبكة العالمية</div>', unsafe_allow_html=True)
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            st.write(f"##### 📁 {cat_name}")
            edit_cols = st.columns(2)
            for idx, (ing_name, data) in enumerate(items.items()):
                with edit_cols[idx % 2]:
                    BIG_FEEDS_LIBRARY[cat_name][ing_name]["base_price"] = st.number_input(f"تعديل السعر الأساسي لـ ({ing_name}) $:", min_value=0.0, value=float(data["base_price"]), key=f"base_ed_{ing_name}")
        st.success("💾 تم حفظ وتحديث أسعار البورصة الأساسية للبرنامج.")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. التوقيع الدائم بأسفل الشاشة لـ م. عبد القادر
# ==========================================
st.markdown(
    """
    <div class="mini-left-signature">
        👨‍🔬 م. عبد القادر إسماعيل تاور © 2026 | خبير الحلول الذكية للثروة الحيوانية والبرمجيات المتكاملة
    </div>
    """,
    unsafe_allow_html=True
)
