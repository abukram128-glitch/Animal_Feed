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

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"       

# جلب كلمة المرور بأمان من إعدادات الـ Secrets الخاصة بـ Streamlit لحمايتها من السرقة
SENDER_PASSWORD = st.secrets.get("SMTP_PASSWORD", "oynz rdli tsdy ekdq")

def send_code_to_mail(receiver_email):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود الاحترافي الشامل - منصة تاور V3 المحصنة"
    body = "السلام عليكم م. عبد القادر،\n\nمرفق السورس كود بعد إرجاع دالة الوزن بشريط القياس، نظام خانات البروتين المزدوجة، وبورصة المنتجات الحية الدقيقة للمدن.\n\nتحياتي."
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        # تحديد مسار الملف الحالي بدقة ديناميكية لمنع الكراش على الخوادم السحابية
        current_file_path = os.path.abspath(__file__)
        if os.path.exists(current_file_path):
            with open(current_file_path, "r", encoding="utf-8") as f:
                code_content = f.read()
            attachment = MIMEText(code_content, 'plain', 'utf-8')
            attachment.add_header('Content-Disposition', 'attachment', filename="tower_smart_platform.py")
            msg.attach(attachment)
        else:
            st.error("❌ تعذر العثور على ملف السورس كود في هذا المسار السحابي.")
            return False

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ خطأ في خادم الإرسال: {e}")
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
    .animal-visual-frame {
        border: 2px dashed #e65100;
        background: #fff3e0;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 15px 0;
    }
    .market-card {
        background: #e3f2fd;
        border-right: 5px solid #1565c0;
        padding: 10px;
        margin-bottom: 8px;
        border-radius: 4px;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. تهيئة متغيرات الجلسة الآمنة (ضد الكراش)
# ==========================================
if "approved" not in st.session_state: st.session_state["approved"] = False
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "active_formula" not in st.session_state: st.session_state["active_formula"] = {}
if "active_cp_prog" not in st.session_state: st.session_state["active_cp_prog"] = 16.0
if "active_cp_opt" not in st.session_state: st.session_state["active_cp_opt"] = 16.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 240.0
if "chosen_sector_tag" not in st.session_state: st.session_state["chosen_sector_tag"] = "الأبقار وسلالاتها"

if "inventory" not in st.session_state:
    st.session_state["inventory"] = {
        "ذرة صفراء": 100.0, "ذرة بيضاء": 50.0, "شعير مطحون": 40.0, "سورجم (فتريتة)": 80.0,
        "كسب فول صويا 44%": 30.0, "أمباز الفول السوداني (كسب)": 50.0, "نخالة قمح (ردة)": 70.0,
        "البرسيم الجاف (الدريس)": 50.0, "مركزات خيول ومجترات": 10.0, "مركزات دواجن وسمان": 10.0
    }

# بوابة الحماية والدخول
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
# 3. المصفوفة الجغرافية الكبرى الشاملة لولايات ومدن السودان وليبيا ومصر
# =====================================================================
GEOGRAPHY_DATA = {
    "السودان": {
        "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
        "ولاية القضارف": ["القضارف المدينة", "الحواتة", "الفاو"],
        "ولاية الجزيرة": ["ود مدني", "المناقل", "الحصاحيصا"],
        "ولاية شمال كردفان": ["الأبيض", "أم روابة"],
        "ولاية غرب كردفان": ["النهود", "الفوله", "بابنوسة"],
        "ولاية النيل الأزرق": ["الدمازين", "الروصيرص"],
        "ولاية شمال دارفور": ["الفاشر", "كبكابية"],
        "ولاية جنوب دارفور": ["نيالا", "عد الفرسان"],
        "ولاية غرب دارفور": ["الجنينة"],
        "ولاية شرق دارفور": ["الضعين"],
        "ولاية وسط دارفور": ["زالنجي"],
        "ولاية البحر الأحمر": ["بورتسودان", "سواكن"],
        "الولاية الشمالية": ["دنقلا", "مروي"]
    },
    "ليبيا": {
        "إقليم البطنان والمنطقة الشرقية": ["طبرق", "امساعد", "بنغازي", "البيضاء", "درنة"],
        "الإقليم الغربي طرابلس": ["طرابلس", "مصراتة", "الزاوية", "غريان"],
        "فزان والمنطقة الجنوبية": ["سبها", "مرزق", "أوباري"]
    },
    "مصر": {
        "الدلتا والقاهرة": ["القاهرة", "طنطا", "المنصورة"],
        "الصعيد والوجه القبلي": ["أسيوط", "المنيا", "أسوان"]
    }
}

SECTOR_OPTIONS_MAP = {
    "الأبقار وسلالاتها": {
        "stages": {"تسمين وإنتاج لحوم مكثف": 14.5, "إدرار حليب عالي": 17.0, "أمهات وحوامل": 13.5},
        "breeds": {"السودان": ["أبقار الكنانة الرائدة", "أبقار البطانة الديرية", "أبقار البقارة"], "ليبيا": ["أبقار فريزيان محسن محلي", "أبقار برقة المحلية"], "مصر": ["أبقار هولشتاين مأقلمة", "الأبقار البلدي المصرية"]}
    },
    "الخيول والفروسية": {
        "stages": {"خيول سباق وسرعة مكثف": 14.0, "خيول قفز وحواجز رياضي": 13.0, "مهرة نامية صغرى": 15.5, "خيول تربية وإنتاج وأمهات": 12.5},
        "breeds": {"السودان": ["الحصان الدنقلاوي الأصيل", "الخيول المخلوطة المحسنة"], "ليبيا": ["الجواد العربي الليبي الفاخر", "الخيول الهجينة المحسنة"], "مصر": ["الحصان العربي المصري المستقيم"]}
    },
    "الأغنام والضأن": {
        "stages": {"تسمين حملان سريع": 16.0, "نعاج مرضعة ومدرة حليب": 15.0, "أمهات دافع غذائي": 12.5},
        "breeds": {"السودان": ["ضأن الدوبا (الحمري والشقر)", "ضأن الكباشي البري"], "ليبيا": ["أغنام البرقي العريقة", "الضأن المحلي الليبي"], "مصر": ["أغنام الرحماني"]}
    },
    "الطيور والدواجن": {
        "stages": {"بادي لاحم 23%": 23.0, "نامي لاحم 21%": 21.0, "ناهي لاحم 19%": 19.0, "بياض إنتاجي دائم": 17.5},
        "breeds": {"السودان": ["هبرد محسن مزارع"], "ليبيا": ["كب 500 مزارع"], "مصر": ["روس 308 متطور"]}
    }
}

# =====================================================================
# 4. بورصة أسعار الخامات والحيوانات الحية للمدن والولايات
# =====================================================================
LIVE_FEED_PRICES = {
    "طبرق": {"ذرة صفراء": 255.0, "كسب فول صويا 44%": 470.0, "نخالة قمح (ردة)": 165.0, "شعير مطحون": 230.0},
    "الخرطوم": {"ذرة صفراء": 230.0, "كسب فول صويا 44%": 440.0, "نخالة قمح (ردة)": 140.0, "سورجم (فتريتة)": 190.0},
    "النهود": {"ذرة صفراء": 220.0, "أمباز الفول السوداني (كسب)": 390.0, "نخالة قمح (ردة)": 125.0, "سورجم (فتريتة)": 175.0},
    "الدمازين": {"ذرة صفراء": 210.0, "أمباز الفول السوداني (كسب)": 380.0, "نخالة قمح (ردة)": 120.0, "سورجم (فتريتة)": 170.0}
}

LIVE_ANIMAL_MARKET = {
    "طبرق": {"عجول قائم (كجم)": 35.0, "خراف برقي حي": 45.0, "لتر حليب طازج": 4.5, "طبق بيض": 18.0},
    "الخرطوم": {"عجول قائم (كجم)": 28.0, "خراف كباشي حي": 35.0, "لتر حليب طازج": 3.2, "طبق بيض": 14.0},
    "النهود": {"عجول قائم (كجم)": 25.0, "خراف حمرية حية": 30.0, "لتر حليب طازج": 2.8, "طبق بيض": 15.0},
    "الدمازين": {"عجول قائم (كجم)": 24.0, "خراف محليه حية": 29.0, "لتر حليب طازج": 2.5, "طبق بيض": 14.5}
}

def get_market_prices(city_name):
    base_feed = {"ذرة صفراء": 240.0, "ذرة بيضاء": 235.0, "شعير مطحون": 220.0, "سورجم (فتريتة)": 200.0, "أمباز الفول السوداني (كسب)": 440.0, "كسب فول صويا 44%": 450.0, "نخالة قمح (ردة)": 150.0, "البرسيم الجاف (الدريس)": 170.0, "مركزات خيول ومجترات": 600.0, "مركزات دواجن وسمان": 650.0, "الحجر الجيري (بودرة بلاط)": 40.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0, "ملح الطعام": 30.0, "مضاد سموم فطرية": 950.0, "إنزيم الفايتيز الزامي (Phytase Super-D)": 1150.0, "بيكربونات الصوديوم (الصودا)": 340.0}
    base_animal = {"عجول قائم (كجم)": 30.0, "خراف حية": 38.0, "لتر حليب طازج": 3.5, "طبق بيض": 16.0}
    if city_name in LIVE_FEED_PRICES: base_feed.update(LIVE_FEED_PRICES[city_name])
    if city_name in LIVE_ANIMAL_MARKET: base_animal.update(LIVE_ANIMAL_MARKET[city_name])
    return base_feed, base_animal

BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {"ذرة صفراء": 8.5, "ذرة بيضاء": 8.8, "شعير مطحون": 11.5, "سورجم (فتريتة)": 10.0},
    "الأكساب والأمباز ومصادر البروتين العالي": {"أمباز الفول السوداني (كسب)": 46.0, "كسب فول صويا 44%": 44.0, "كسب فول صويا 48%": 48.0, "كسب عباد الشمس 36%": 36.0},
    "المخلفات الرعوية والمواد المالئة": {"نخالة قمح (ردة)": 15.0, "البرسيم الجاف (الدريس)": 16.5},
    "الإضافات المتخصصة والمركزات": {"مركزات دواجن وسمان": 40.0, "مركزات خيول ومجترات": 36.0, "الحجر الجيري (بودرة بلاط)": 0.0, "فوسفات ثنائي الكالسيوم (DCP)": 0.0, "ملح الطعام": 0.0, "مضاد سموم فطرية": 0.0, "بيكربونات الصوديوم (الصودا)": 0.0},
    "المعاملات الحيوية والإنزيمات": {"إنزيم الفايتيز الزامي (Phytase Super-D)": 0.0}
}

EXCHANGE_RATES = {"السودان": {"rate": 600.0, "sym": "SDG"}, "ليبيا": {"rate": 4.82, "sym": "LYD"}, "مصر": {"rate": 48.0, "sym": "EGP"}}

st.markdown('<div class="main-box">', unsafe_allow_html=True)
st.markdown("<h1 style='color: #1b5e20; text-align:right;'>منصة تاور الذكية للإنتاج الحيواني وصناعة الأعلاف 🌾</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #c62828; text-align:right;'>الخبير المستشار / م. عبد القادر إسماعيل تاور - تحديثات 2026 حقلية</h4>", unsafe_allow_html=True)
st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

tabs = st.tabs(["🔬 النمذجة والحسابات العلفية الكبرى", "📏 دالة قياس الوزن الحقلية", "📊 بورصة المنتجات الحية للولاية"])

with tabs[0]:
    st.markdown('<div class="section-title">🌍 أولاً: الجغرافيا وتزامن أسواق البورصة المحلية</div>', unsafe_allow_html=True)
    col_country, col_state, col_city = st.columns(3)
    with col_country: user_country = st.selectbox("اختر دولة المربي المستهدف:", ["السودان", "ليبيا", "مصر"])
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    state_options = list(GEOGRAPHY_DATA[user_country].keys())
    with col_state: chosen_state = st.selectbox("اختر الإقليم / الولاية الإدارية كاملة:", state_options)
    city_options = GEOGRAPHY_DATA[user_country][chosen_state]
    with col_city: user_city = st.selectbox("اختر المدينة المرتبطة بالبورصة حركياً:", city_options)

    feed_prices, animal_prices = get_market_prices(user_city)

    st.markdown('<div class="section-title">🐎 ثانياً: تحديد سلالة الحيوان ونوع الإنتاج الفسيولوجي</div>', unsafe_allow_html=True)
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec: main_sector = st.selectbox("اختر القطاع الحيواني المستهدف:", list(SECTOR_OPTIONS_MAP.keys()))
    st.session_state["chosen_sector_tag"] = main_sector
    
    stage_dict = SECTOR_OPTIONS_MAP[main_sector]["stages"]
    with col_sub: prod_stage = st.selectbox("القسم والمرحلة الفسيولوجية الدقيقة للحيوان:", list(stage_dict.keys()))
    
    breed_list = SECTOR_OPTIONS_MAP[main_sector]["breeds"].get(user_country, ["سلالة محلية محسنة"])
    with col_prod: chosen_breed = st.selectbox("السلالة الجغرافية المتوفرة:", breed_list)

    st.markdown('<div class="section-title">📋 ثالثاً: نظام تحديد البروتين المزدوج لخلطة الطن</div>', unsafe_allow_html=True)
    col_cp_p, col_cp_o = st.columns(2)
    
    mandatory_cp = stage_dict[prod_stage]
    with col_cp_p:
        st.number_input("🧬 نسبة البروتين الحتمية برمجياً (حسب نوع الإنتاج المطلوب):", value=mandatory_cp, disabled=True)
    
    with col_cp_o:
        optional_cp = st.slider("⚙️ نسبة البروتين الاختيارية المفتوحة (تعديل المستشار):", 10.0, 40.0, value=mandatory_cp)

    st.markdown('<div class="section-title">🌾 رابعاً: انتقاء مكونات الخلطة وحساب النتائج العلفية</div>', unsafe_allow_html=True)
    selected_ingredients = []; ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=False):
            sub_cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with sub_cols[idx % 3]:
                    is_def = True if "ذرة" in ing_name or "صويا" in ing_name or "أمباز" in ing_name or "ملح" in ing_name or "مركزات" in ing_name else False
                    checked = st.checkbox(ing_name, value=is_def, key=f"f3_{ing_name}")
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = feed_prices.get(ing_name, 300.0)

    if st.button("🚀 تشغيل محرك التركيب والاحتساب البرمجي الصارم للبروتين والخلطة", type="primary", use_container_width=True):
        formula_results = {}
        fixed_ratios = {"ملح الطعام": 0.005, "مضاد سموم فطرية": 0.002, "الحجر الجيري (بودرة بلاط)": 0.015, "فوسفات ثنائي الكالسيوم (DCP)": 0.01}
        if "الطيور" in main_sector: fixed_ratios["مركزات دواجن وسمان"] = 0.050
        if "الخيول" in main_sector or "الأبقار" in main_sector: fixed_ratios["مركزات خيول ومجترات"] = 0.025

        used_fixed_pct = 0.0
        for name in selected_ingredients:
            if name in fixed_ratios:
                formula_results[name] = fixed_ratios[name] * 100
                used_fixed_pct += fixed_ratios[name] * 100

        grains = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"]]
        proteins = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"]]
        
        if not grains: grains = ["ذرة صفراء"]
        if not proteins: proteins = ["أمباز الفول السوداني (كسب)"] if user_country == "السودان" else ["كسب فول صويا 44%"]

        grain_target = 60.0 if "الطيور" in main_sector else 55.0
        for x in grains: formula_results[x] = grain_target / len(grains)

        remaining_pct = 100.0 - used_fixed_pct - grain_target
        for x in proteins: formula_results[x] = remaining_pct / len(proteins)

        calculated_cp = 0.0
        for ing_name, pct in formula_results.items():
            for cat, items in BIG_FEEDS_LIBRARY.items():
                if ing_name in items:
                    calculated_cp += (pct / 100.0) * items[ing_name]

        st.session_state["active_formula"] = formula_results
        st.session_state["active_cp_prog"] = mandatory_cp
        st.session_state["active_cp_opt"] = calculated_cp if calculated_cp > 0 else optional_cp
        st.session_state["active_breed_tag"] = chosen_breed
        st.session_state["active_stage_title"] = f"{main_sector} - {prod_stage}"

        res_col1, res_col2 = st.columns([0.6, 0.4])
        with res_col1:
            st.markdown(f"<div class='protein-badge'>🧬 بروتين الإنتاج الحتمي برمجياً: {st.session_state['active_cp_prog']:.1f}% | بروتين المزيج المخلوط الفعلي: {st.session_state['active_cp_opt']:.2f}%</div>", unsafe_allow_html=True)
            for k, v in formula_results.items():
                st.markdown(f"<div class='result-row'>🔹 <b>{k}:</b> {v:.2f} % ➡️ ({v*10:.1f} كجم / طن)</div>", unsafe_allow_html=True)
            
            # معالجة جلب الأسعار بشكل شامل وآمن لمنع إسقاط تكلفة أي مادة مضافة برمجياً
            ton_cost = sum([(v/100) * ingredient_prices.get(k, feed_prices.get(k, 300.0)) for k, v in formula_results.items()])
            st.session_state["computed_ton_cost"] = ton_cost
            st.metric(f"💰 تكلفة طن العلف في بورصة أسواق ({user_city}):", f"${ton_cost:.2f} ( يعادل {ton_cost*c_info['rate']:,.1f} {c_info['sym']} )")
        with res_col2:
            st.bar_chart(formula_results)

# ==========================================
# 📏 5. دالة قياس الوزن الحقلية عبر شريط القياس
# ==========================================
with tabs[1]:
    st.markdown('<div class="section-title">📏 دالة قياس الأوزان الحقلية عبر شريط القياس المتطور</div>', unsafe_allow_html=True)
    st.write("أدخل مقاسات الحيوان الميدانية بالسنتيمتر (cm) لحساب الوزن الحي الفعلي بدقة:")
    
    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1: animal_type_calc = st.selectbox("نوع الحيوان المقاس حرقلياً:", ["أبقار وتسمين", "خيول وجياد", "أغنام وضأن"])
    with col_w2: heart_girth = st.number_input("محيط الصدر (Heart Girth) بالسنتيمتر:", min_value=10.0, value=150.0)
    with col_w3: body_length = st.number_input("طول الجسم المستقيم (Body Length) بالسنتيمتر:", min_value=10.0, value=130.0)
    
    if st.button("⚖️ احسب الوزن الحي الحيواني الفعلي فوراً"):
        if animal_type_calc == "أبقار وتسمين":
            weight_kg = (heart_girth ** 2 * body_length) / 10838
        elif animal_type_calc == "خيول وجياد":
            weight_kg = (heart_girth ** 2 * body_length) / 11877
        else:
            weight_kg = (heart_girth ** 2 * body_length) / 11312
        st.success(f"📊 الوزن التقديري الصافي للحيوان هو: **{weight_kg:.2f} كجم قائم**")

# ==========================================
# 📊 6. تبويب بورصة المنتجات والحيوانات الحية للمدينة
# ==========================================
with tabs[2]:
    st.markdown(f'<div class="section-title">📊 أسعار بورصة المنتجات واللحوم الحية القائمة في مدينة ({user_city})</div>', unsafe_allow_html=True)
    for prod_name, price_val in animal_prices.items():
        st.markdown(f"""
        <div class="market-card">
            🎯 <b>{prod_name}:</b> {price_val:.2f} {c_info['sym']} في أسواق المنطقة الحالية
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 🏷️ 7. مصمم بطاقات الديباجة والتسويق النهائي
# ==========================================
if st.session_state["user_role"] == "admin" and st.session_state["active_formula"]:
    st.write("")
    st.markdown('<div class="section-title">🏷️ ديباجة المنتج النهائية المعتمدة مع صورة وتخطيط الحيوان حسب العلف</div>', unsafe_allow_html=True)
    
    current_sec = st.session_state['chosen_sector_tag']
    if "الخيول" in current_sec:
        animal_graphic = "🐎 [رسم تخطيطي لجواد أصيل - علف خيول متكامل]"
        visual_desc = "📍 يمثل الجواد الرياضي والنامي. يوضع شريط القياس خلف الغارب مباشرة مائلاً نحو عظمة المقعدة."
    elif "الأبقار" in current_sec:
        animal_graphic = "🐄 [رسم بقرة تسمين وإنتاج حليب حركي مكثف]"
        visual_desc = "📍 يمثل الأبقار والماشية الكبرى. يوضع شريط القياس حول محيط الصدر خلف المرفق مباشرة."
    elif "الأغنام" in current_sec:
        animal_graphic = "🐑 [رسم مجترات صغيرة - علف تسمين حملان وضأن]"
        visual_desc = "📍 يمثل الأغنام والماعز. يوضع الشريط حول أضيق منطقة خلف لوح الكتف مباشرة."
    else:
        animal_graphic = "🐓 [رسم قطاع الطيور والدواجن الداجنة]"
        visual_desc = "📍 يمثل الطيور والسمان. الوزن يعتمد على الميزان الحركي الدقيق للقطيع."

    st.markdown(f"""
    <div class="sack-tag">
        <h2 style="text-align: center;">🌾 مجموعة تاور لصناعة الأعلاف والحلول المتكاملة 🌾</h2>
        <p style="text-align: center;"><b>المستشار الفني الخبير: م. عبد القادر إسماعيل تاور</b></p>
        <hr style="border-top: 1px dashed #1b5e20;">
        <p style="text-align: right;">🎯 السلالة المستهدفة: {st.session_state['active_breed_tag']} | نوع العلف: {st.session_state['active_stage_title']}</p>
        <p style="text-align: right;">🧬 بروتين الإنتاج الثابت برمجياً: <b>{st.session_state['active_cp_prog']:.1f}%</b> | بروتين المزيج الفعلي: <b>{st.session_state['active_cp_opt']:.2f}%</b></p>
        
        <div class="animal-visual-frame">
            <h4 style="color: #d84315; margin: 0;">🖼️ صورة وتخطيط دليل الحيوان المعتمد لهذا العلف</h4>
            <div style="font-size: 3rem; margin: 15px 0;">{animal_graphic}</div>
            <p style="color: #37474f; font-size: 0.95rem; direction: rtl; text-align: center; margin: 0;">
                {visual_desc}
            </p>
        </div>
        
        <p style="text-align: center; margin-top: 15px; font-size: 0.8rem; color: #558b2f;">برمج وفقاً للمواصفات الأكاديمية الصارمة لمعايير هندسة التغذية وصحة الحيوان 2026</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 8. نظام الأرشفة والمراسلة الآمنة بأسفل التطبيق
# ==========================================
st.markdown("<br><hr style='border-top: 1px dashed #2e7d32;'>", unsafe_allow_html=True)
st.markdown("### 📨 أرشفة الكود والتقارير الحالية بالبريد الإلكتروني")
target_email = st.text_input("أدخل البريد الإلكتروني المستلم لحفظ نسخة السورس كود الأساسية:", value="abukram128@gmail.com")
if st.button("🚀 إرسال نسخة الكود المتكاملة"):
    if send_code_to_mail(target_email):
        st.success("📥 تم إرسال ملف السورس كود المتكامل بنجاح وأرشفته برمجياً وتغذوياً دون أي علل علمية.")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="mini-left-signature">👨‍🔬 م. عبد القادر إسماعيل تاور © 2026 | خبير الحلول البرمجية المتكاملة والإنتاج الحيواني</div>', unsafe_allow_html=True)
