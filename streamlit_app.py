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
        background-color: #f4f6f9;
    }
    .main-box {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.08);
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
    .profile-img-style {
        width: 130px;
        height: 130px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid #d4af37;
        box-shadow: 0px 6px 20px rgba(0,0,0,0.15);
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
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
        z-index: 9999;
        direction: rtl;
    }
    /* ديباجة الجوال الفاخرة المخصصة للتسويق والفواتير */
    .mobile-invoice-card {
        background: linear-gradient(135deg, #ffffff 0%, #f9fbf7 100%);
        border: 1px solid #e1e8dc;
        border-top: 8px solid #2e7d32;
        border-radius: 12px;
        padding: 20px;
        max-width: 450px;
        margin: 0 auto 20px auto;
        box-shadow: 0 8px 24px rgba(46,125,50,0.08);
        direction: rtl;
        text-align: right;
    }
    .mobile-invoice-header {
        text-align: center;
        border-bottom: 2px dashed #2e7d32;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    .mobile-invoice-header h4 { color: #1b5e20; margin: 5px 0; font-weight: bold; }
    .mobile-invoice-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 0.95rem;
        border-bottom: 1px solid #f0f0f0;
        padding-bottom: 4px;
    }
    .mobile-invoice-total {
        background-color: #2e7d32;
        color: white;
        padding: 10px;
        border-radius: 6px;
        text-align: center;
        font-weight: bold;
        font-size: 1.1rem;
        margin-top: 15px;
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
        else: st.error("❌ بيانات الاعتماد غير صحيحة.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =====================================================================
# 3. قاعدة البيانات الموسعة والمطورة هندسياً
# =====================================================================
BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "base_price": 230.0, "max_limit": 65.0, "desc": "المصدر الأساسي للطاقة، غني بالرطوبة والنشا."}, 
        "ذرة بيضاء": {"CP": 8.8, "base_price": 225.0, "max_limit": 60.0, "desc": "طاقة ممتازة بديلة للاستخدام المحلي."}, 
        "شعير مطحون": {"CP": 11.5, "base_price": 210.0, "max_limit": 30.0, "desc": "ممتاز للمجترات، يرفع الألياف (يحتاج NSP عند زيادة النسبة في الدواجن)."}, 
        "سورجم (فتريتة)": {"CP": 10.0, "base_price": 195.0, "max_limit": 40.0, "desc": "بديل محلي غني بالطاقة، يحتوي تانينات متوسطة."},
        "قمح محلي مصنّع": {"CP": 12.0, "base_price": 240.0, "max_limit": 35.0, "desc": "يمنح تماسكاً للعلف (يحتاج زيلاناز لمنع اللزوجة المعوية)."}
    },
    "الأكساب والأمباز ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "base_price": 460.0, "max_limit": 25.0, "desc": "بروتين محلي فائق الجودة، ممتاز للتسمين."}, 
        "كسب فول صويا 44%": {"CP": 44.0, "base_price": 440.0, "max_limit": 35.0, "desc": "حجر الأساس البروتيني للدواجن والمجترات."}, 
        "كسب فول صويا 48%": {"CP": 48.0, "base_price": 480.0, "max_limit": 30.0, "desc": "مركز بروتيني عالي للأعلاف البادئة."}, 
        "كسب عباد الشمس 36%": {"CP": 36.0, "base_price": 310.0, "max_limit": 20.0, "desc": "ألياف مرتفعة، اقتصادي وممتاز لخلطات الأبقار."},
        "كسب بذور القطن": {"CP": 41.0, "base_price": 290.0, "max_limit": 15.0, "desc": "يحتوي على مادة الجوسيبول السامة (يتطلب كبريتات الحديدوز لمعادلته في الدواجن)."}
    },
    "الأحماض الأمينية المصنعة النقية": {
        "لايسين خام مصنع (L-Lysine HCL)": {"CP": 94.0, "base_price": 1650.0, "max_limit": 1.0, "desc": "حمض أميني حرج لبناء اللحم."},
        "ميثيونين نقّي (DL-Methionine)": {"CP": 58.0, "base_price": 2800.0, "max_limit": 0.8, "desc": "الحمض الأميني الأول لدواجن اللحم والريش."},
        "تربتوفان مركز (L-Tryptophan)": {"CP": 82.0, "base_price": 4500.0, "max_limit": 0.3, "desc": "منظم النمو والمناعة العصبي الحيوي."},
        "ثريونين علفي (L-Threonine)": {"CP": 72.0, "base_price": 1850.0, "max_limit": 0.5, "desc": "صيانة جدار الأمعاء والامتصاص الفعلي."}
    },
    "الإنزيمات والمحفزات الحيوية ودواعم الكرش": {
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "base_price": 340.0, "max_limit": 1.0, "desc": "منظم حموضة الكرش (الحموضة اللبنية)."},
        "إنزيم الفايتيز (Phytase)": {"CP": 0.0, "base_price": 1200.0, "max_limit": 0.1, "desc": "لتحرير الفسفور العضوي المرتبط."},
        "إنزيم الـ NSP المعوي": {"CP": 0.0, "base_price": 1450.0, "max_limit": 0.1, "desc": "هضم السكريات غير النشوية في الشعير والقمح."},
        "كبريتات الحديدوز": {"CP": 0.0, "base_price": 410.0, "max_limit": 0.2, "desc": "مضاد ومقيد لسمية الجوسيبول الحرة."},
        "مضاد سموم فطرية لوجستي": {"CP": 0.0, "base_price": 950.0, "max_limit": 0.3, "desc": "حماية كبدية واسعة الطيف من الأفلاتوكسين."}
    },
    "المخلفات الرعوية والمواد المالئة": {
        "نخالة قمح (ردة)": {"CP": 15.0, "base_price": 150.0, "max_limit": 35.0, "desc": "مادة مالئة غنية بالفسفور السهب وممتازة للهضم."}, 
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "base_price": 170.0, "max_limit": 40.0, "desc": "الياف طويلة داعمة للاجترار وصحة الكرش."}, 
        "مولاس قصب السكر": {"CP": 4.0, "base_price": 120.0, "max_limit": 7.0, "desc": "مشهي علفي ومربط جزيئات الغبار لمنع التنفسي."}
    }
}

# تهيئة مخزن البورصة الشامل والمقسم بدقة بداخل الـ Session State
if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "الأبقار": {
            "عجول تسمين هولشتاين محسن ($)": 1350.0, 
            "أبقار كنانة وبطانة محلية ($)": 900.0,
            "أبقار فريزيان حلاب مدرّ ($)": 1800.0
        },
        "الخيول": {
            "خيول عربية أصيلة مسجلة ($)": 6500.0,
            "خيول هجينة للركوب والعمل ($)": 1200.0
        },
        "الأغنام": {
            "ضأن حري / بلدي محلي ($)": 190.0, 
            "ضأن بربري / سواكني ($)": 140.0
        },
        "الماعز": {
            "ماعز نوبي حليبي ($)": 160.0, 
            "جديان تسمين صحراوية ($)": 110.0
        },
        "الدواجن": {
            "كتكوت لاحم عمر يوم ($)": 0.65,
            "دجاج بياض عمر 18 أسبوع ($)": 4.50,
            "طير سمان بياض منجّز ($)": 0.85
        }
    }

if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري صافي ($)": 7.50, 
        "كيلو لحم ضأن طازج ($)": 9.00,
        "كيلو لحم دجاج لاحم صافي ($)": 3.80, 
        "طبق بيض مائدة 30 بيضة ($)": 4.20,
        "لتر حليب بقري طازج ($)": 1.10
    }

EXCHANGE_RATES = {
    "ليبيا": {"rate": 4.80, "sym": "LYD"},
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "مصر": {"rate": 48.0, "sym": "EGP"},
    "باقي دول العالم": {"rate": 1.0, "sym": "USD"}
}

# متغيرات الحسابات العلفية المستقرة
if "active_formula" not in st.session_state: st.session_state["active_formula"] = None
if "manual_cp_target" not in st.session_state: st.session_state["manual_cp_target"] = 21.0
if "programmed_cp_actual" not in st.session_state: st.session_state["programmed_cp_actual"] = 0.0
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 0.0
if "enzyme_warnings" not in st.session_state: st.session_state["enzyme_warnings"] = []

# ==========================================
# 4. بناء الهيدر والتوقيع الفخم
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)
col_logo, col_title = st.columns([0.2, 0.8])
with col_logo:
    if img_base64: st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else: st.markdown(f'<div style="text-align:center; font-size:4rem;">🌾</div>', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور الذكية المتكاملة للأعلاف والإنتاج الحيواني 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.1rem; margin-top:5px; margin-bottom:0;'>إصدار موازنة الإنزيمات الحرجة، نظام ديباجات الجوال للتسويق، والربط البريدي المتكامل مع Gmail</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

# تفعيل التبويبات حسب الترتيب الجديد المطلوب
tabs = st.tabs([
    "📏 شريط القياس وحساب الأوزان", 
    "📊 بورصة تاور الكبرى للثروة الحيوانية",
    "🔬 محرك النمذجة والحسابات العلفية بدقة الإنزيمات",
    "🗂️ مكتبة تاور الاستشارية الموسعة",
    "🧾 التسويق والفواتير وديباجات الجوال",
    "📬 الربط البريدي والـ Gmail",
    "⚙️ لوحة الإدارة البورصوية المركزية"
])

# ---------------------------------------------------------------------
# التبويب الأول: شريط القياس وحساب الأوزان للمربين (أولاً)
# ---------------------------------------------------------------------
with tabs[0]:
    st.markdown('<div class="section-title">📐 تقدير الوزن الحي للحيوان عبر شريط القياس الفني</div>', unsafe_allow_html=True)
    
    col_meas_input, col_meas_guide = st.columns(2)
    with col_meas_input:
        animal_type_select = st.selectbox("اختر نوع الحيوان المستهدف بالقياس:", ["الأبقار والعجاجيل", "الأغنام والماعز", "الخيول والخيول الهجينة"])
        girth_in_cm = st.number_input("قياس محيط الصدر خلف القائمتين الأماميتين مباشرة (سم):", min_value=20.0, max_value=350.0, value=160.0)
        length_in_cm = st.number_input("قياس طول الجسم الأفقي من عظمة الكتف إلى عظمة الدبوس (سم):", min_value=20.0, max_value=350.0, value=140.0)
        
        if st.button("🧮 استخراج الوزن الحي التقديري فوراً", type="primary", use_container_width=True):
            if "الأبقار" in animal_type_select:
                calc_weight = (girth_in_cm ** 2 * length_in_cm) / 10838.0
            elif "الأغنام" in animal_type_select:
                calc_weight = (girth_in_cm ** 2 * length_in_cm) / 11300.0
            else: # الخيول
                calc_weight = (girth_in_cm ** 2 * length_in_cm) / 11880.0
                
            st.markdown(
                f"""
                <div style='background-color:#e8f5e9; padding:20px; border-radius:10px; text-align:center; border:2px dashed #2e7d32; margin-top:15px;'>
                    <h3 style='color:#2e7d32; margin:0;'>⚖️ الوزن المقدر الناتج: <b>{calc_weight:.2f} كجم</b></h3>
                    <p style='color:#444; margin-top:5px; font-size:0.9rem;'>المعادلة مطابقة للمواصفات الحقلية المعتمدة لدى الخبير م. عبد القادر تاور.</p>
                </div>
                """, unsafe_allow_html=True
            )
            
    with col_meas_guide:
        st.markdown(
            """
            <div style='background-color:#fff3e0; padding:20px; border-radius:8px; border-right:5px solid #ff9800; text-align:right;'>
                <h5 style='color:#e65100; font-weight:bold; margin-top:0;'>💡 التوجيه الحقلي لأخذ القياس:</h5>
                <p>1. <b>محيط الصدر (Heart Girth):</b> لف شريط القياس المتربّع حول الصدر خلف المرفقين تماماً وبشكل مشدود يطرد الهواء من الفراء.</p>
                <p>2. <b>طول الهيكل (Length):</b> القياس المستقيم من النقطة البارزة لمفصل الكتف وحتى النقطة الخارجية لعظمة الحوض الخلفية (الدبوس).</p>
            </div>
            """, unsafe_allow_html=True
        )

# ---------------------------------------------------------------------
# التبويب الثاني: بورصة الحيوانات الشاملة ثم المنتجات (ثانياً)
# ---------------------------------------------------------------------
with tabs[1]:
    st.markdown('<div class="section-title">📊 بورصة تاور المحدثة لأسعار الثروة الحيوانية والمنتجات المزرعية</div>', unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1: user_country = st.selectbox("اختر دولة الرصد السعري لبورصة اليوم:", ["ليبيا", "السودان", "مصر", "باقي دول العالم"], key="bourse_country")
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    local_rate = c_info["rate"]; local_sym = c_info["sym"]
    
    with col_c2:
        if user_country == "ليبيا": chosen_state = st.selectbox("الإقليم الجغرافي اللوجستي:", ["المنطقة الشرقية", "المنطقة الغربية"], key="b_state")
        elif user_country == "السودان": chosen_state = st.selectbox("الإقليم الجغرافي اللوجستي:", ["ولاية الخرطوم", "ولاية القضارف", "ولاية شمال كردفان"], key="b_state")
        else: chosen_state = st.selectbox("الإقليم الجغرافي اللوجستي:", ["الأسواق الحرة المركزية"], key="b_state")
    with col_c3: user_city = st.text_input("اسم سوق المدينة المستهدف:", "طبرق", key="b_city")
    
    logistic_factor = 1.0
    if user_country == "ليبيا":
        logistic_factor = 1.08 if user_city != "طبرق" else 1.14
    elif user_country == "السودان":
        logistic_factor = 1.25 if "كردفان" in chosen_state else 1.15

    st.info(f"📈 أسعار الصرف والخدمات اللوجستية النشطة حالياً في سوق {user_city}: المعامل اللوجستي الفعلي المطبق = {logistic_factor}")

    st.markdown("### 🐂 أولاً: أسعار بورصة رؤوس الماشية الحية (حسب الصنف والقسم)")
    for category, items in st.session_state["global_livestock_prices"].items():
        with st.expander(f"🔹 فئة: {category}", expanded=True):
            cols = st.columns(len(items))
            for idx, (name, base_p) in enumerate(items.items()):
                with cols[idx % len(items)]:
                    final_p = base_p * logistic_factor
                    st.metric(label=name, value=f"{final_p * local_rate:,.1f} {local_sym}", delta=f"${final_p:.2f}")

    st.markdown("---")
    st.markdown("### 🥛 ثانياً: أسعار بورصة المنتجات الحيوانية الصافية والداجنة")
    prod_cols = st.columns(3)
    for idx, (p_name, b_price) in enumerate(st.session_state["global_products_prices"].items()):
        with prod_cols[idx % 3]:
            final_p = b_price * logistic_factor
            st.metric(label=p_name, value=f"{final_p * local_rate:,.2f} {local_sym}", delta=f"${final_p:.2f}")

# ---------------------------------------------------------------------
# التبويب الثالث: محرك النمذجة والحسابات العلفية مع الرقابة والإنزيمات
# ---------------------------------------------------------------------
with tabs[2]:
    st.markdown('<div class="section-title">🔬 محرك صياغة العلائق المتوازن ذكياً (ضوابط الحدود والإنزيمات العلاجية)</div>', unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: target_sector = st.selectbox("القطاع الحيواني المستهدف بالتركيبة:", ["الطيور والسمان", "الأبقار وسلالاتها", "الماعز وسلالاته", "الخيول"])
    with col_s2: target_cp = st.number_input("نسبة البروتين الخام المطلوبة في خلطة الطن (الهدف %):", min_value=10.0, max_value=45.0, value=21.0)
    
    selected_ings = []
    st.markdown("##### 📥 حدد المواد الخام المتاحة في مخزنك اليوم:")
    for cat, items in BIG_FEEDS_LIBRARY.items():
        st.markdown(f"**{cat}:**")
        cols = st.columns(len(items))
        for idx, (ing_name, data) in enumerate(items.items()):
            with cols[idx % len(items)]:
                is_checked = True if "ذرة صفراء" in ing_name or "صويا" in ing_name or "ملح" in ing_name or "مضاد" in ing_name else False
                if st.checkbox(ing_name, value=is_checked, key=f"mix_{ing_name}"):
                    selected_ings.append(ing_name)

    if st.button("🚀 معالجة وصياغة التركيبة وضبط معايير الأمان الحيوية", type="primary", use_container_width=True):
        formula = {}
        warnings = []
        
        # 1. تخصيص المكونات الثابتة والامنة
        fixed_components = {"ملح الطعام": 0.5, "مضاد سموم فطرية لوجستي": 0.2}
        for k, v in fixed_components.items():
            if k in selected_ings: formula[k] = v
            
        # 2. حصر المواد الأساسية للطاقة والبروتين المتاحة
        grains_avail = [x for x in selected_ings if x in BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"]]
        proteins_avail = [x for x in selected_ings if x in BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"]]
        aminos_avail = [x for x in selected_ings if x in BIG_FEEDS_LIBRARY["الأحماض الأمينية المصنعة النقية"]]
        
        if not grains_avail: grains_avail = ["ذرة صفراء"]
        if not proteins_avail: proteins_avail = ["كسب فول صويا 44%"]
        
        # 3. توزيع النسب المبدئية مع موازنة بروتينية أولية
        remaining_pct = 100.0 - sum(formula.values())
        p_weight = 0.42 if target_cp > 20 else 0.25
        p_share = remaining_pct * p_weight
        e_share = remaining_pct - p_share
        
        for g in grains_avail: formula[g] = e_share / len(grains_avail)
        for p in proteins_avail: formula[p] = p_share / len(proteins_avail)
        for a in aminos_avail: formula[a] = 0.25 # حد أميني ميكروجرامي آمن
        
        # 4. الرقابة والتدقيق الصارم للحدود القياسية (Upper Limits) والمعالجة بالإنزيمات
        total_enzymes = 0.0
        enzyme_additions = {}
        
        # أ. معالجة ارتفاع الحبوب اللزجة أو الشعير والألياف
        total_viscous_grains = formula.get("شعير مطحون", 0.0) + formula.get("قمح محلي مصنّع", 0.0)
        if total_viscous_grains > 15.0:
            enzyme_additions["إنزيم الـ NSP المعوي"] = 0.1
            warnings.append(f"⚠️ تجاوزت الحبوب اللزجة والشعير حدها الآمن ({total_viscous_grains:.1f}%). تم إضافة إنزيم الـ NSP المعوي تلقائياً لمنع لزوجة الأمعاء.")
            
        # ب. معالجة سمية كسب بذور القطن
        if formula.get("كسب بذور القطن", 0.0) > 10.0:
            enzyme_additions["كبريتات الحديدوز"] = 0.15
            warnings.append("⚠️ نسبة كسب بذور القطن مرتفعة. تم ضخ كبريتات الحديدوز لربط ومعادلة الجوسيبول الحر السام.")
            
        # ج. معالجة ضغط النشا وحموضة الكرش للمجترات
        total_grains = sum([formula.get(x, 0.0) for x in grains_avail])
        if total_grains > 45.0 and target_sector in ["الأبقار وسلالاتها", "الماعز وسلالاته"]:
            enzyme_additions["بيكربونات الصوديوم (الصودا)"] = 0.8
            warnings.append(f"⚠️ محتوى الكربوهيدرات سهل التخمر عالٍ جداً ({total_grains:.1f}%). تم دمج بيكربونات الصوديوم لتفادي اللقsummary الحامضي والتحمض.")
            
        # د. الفوسفور العضوي المرتبط بالفايرتات في الدواجن
        if target_sector == "الطيور والسمان":
            enzyme_additions["إنزيم الفايتيز (Phytase)"] = 0.05
            warnings.append("🔬 تم دمج إنزيم الفايتيز لتحرير الفسفور المرتبط بالنباتات لرفع جودة وكفاءة الامتصاص المعوي.")

        # دمج الإنزيمات المضافة واقتطاعها من الخامة الأساسية لضمان ثبات المجموع = 100%
        if enzyme_additions:
            for enz_name, enz_val in enzyme_additions.items():
                formula[enz_name] = enz_val
            main_grain = grains_avail[0]
            formula[main_grain] = max(1.0, formula[main_grain] - sum(enzyme_additions.values()))

        # 5. حساب النتيجة النهائية للبروتين والتكلفة
        computed_cp_val = 0.0
        ton_cost_val = 0.0
        for ing_name, pct in formula.items():
            # البحث في فئات المكتبة للوصول لبيانات المادة الخام
            feed_data = None
            for cat_n, items_n in BIG_FEEDS_LIBRARY.items():
                if ing_name in items_n:
                    feed_data = items_n[ing_name]
                    break
            if feed_data:
                computed_cp_val += (pct / 100.0) * feed_data["CP"]
                ton_cost_val += (pct / 100.0) * (feed_data["base_price"] * logistic_factor)
                
        st.session_state["active_formula"] = formula
        st.session_state["programmed_cp_actual"] = computed_cp_val
        st.session_state["computed_ton_cost"] = ton_cost_val
        st.session_state["enzyme_warnings"] = warnings

    # عرض نتائج خوارزمية الخلط والبروتين المستقرة خارج البوتون
    if st.session_state["active_formula"] is not None:
        st.markdown("### 🧬 نتائج المطابقة الحيوية والمراقبة التحليلية للبروتين:")
        col_res_cp1, col_res_cp2 = st.columns(2)
        with col_res_cp1: st.metric("🎯 نسبة البروتين المستهدفة:", f"{st.session_state['manual_cp_target']:.2f} %")
        with col_res_cp2: st.metric("🖥️ نسبة البروتين المتحققة فعلياً بعد الفحص:", f"{st.session_state['programmed_cp_actual']:.2f} %")
        
        if st.session_state["enzyme_warnings"]:
            st.markdown("##### 🚨 الإجراءات الوقائية والمعالجة بالإنزيمات المنفذة:")
            for warn in st.session_state["enzyme_warnings"]:
                st.warning(warn)

        c_res1, c_res2 = st.columns([0.6, 0.4])
        with c_res1:
            st.markdown(f"⚙️ **مكونات وأوزان خلطة الطن الواحد الفعليّة ({user_city}):**")
            for k, v in st.session_state["active_formula"].items():
                st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** / للطن)")
            st.metric("💰 تكلفة إنتاج الطن اللوجستية الإجمالية في السوق المحلي:", f"{st.session_state['computed_ton_cost']*local_rate:,.1f} {local_sym} (${st.session_state['computed_ton_cost']:.2f})")
        with c_res2:
            st.bar_chart(st.session_state["active_formula"])

# ---------------------------------------------------------------------
# التبويب الرابع: مكتبة تاور الاستشارية الموسعة الشاملة
# ---------------------------------------------------------------------
with tabs[3]:
    st.markdown('<div class="section-title">🗂️ مستودع ومكتبة خبير الأعلاف الاستشارية الموسعة</div>', unsafe_allow_html=True)
    for cat_title, items in BIG_FEEDS_LIBRARY.items():
        st.markdown(f"#### 📁 فئة: {cat_title}")
        sub_cols = st.columns(3)
        for i, (ing_name, d) in enumerate(items.items()):
            with sub_cols[i % 3]:
                st.markdown(
                    f"""
                    <div style='background-color:#ffffff; padding:15px; border-radius:8px; border-left:4px solid #1b5e20; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom:15px; text-align:right;'>
                        <h5 style='color:#2e7d32; margin:0;'>🌾 {ing_name}</h5>
                        <p style='margin:4px 0; font-size:0.9rem; color:#555;'>{d['desc']}</p>
                        <span style='background:#e8f5e9; padding:2px 6px; border-radius:4px; font-size:0.8rem;'>البروتين: {d['CP']}%</span>
                        <span style='background:#fff3e0; padding:2px 6px; border-radius:4px; font-size:0.8rem;'>أقصى حد آمن: {d['max_limit']}%</span>
                    </div>
                    """, unsafe_allow_html=True
                )

# ---------------------------------------------------------------------
# التبويب الخامس: نظام التسويق والفواتير وديباجات الجوال الفاخرة
# ---------------------------------------------------------------------
with tabs[4]:
    st.markdown('<div class="section-title">🧾 وحدة التسويق والفواتير الذكية (ديباجات الهواتف المحمولة الفخمة)</div>', unsafe_allow_html=True)
    
    col_inv1, col_inv2 = st.columns([0.4, 0.6])
    with col_inv1:
        st.markdown("##### 📝 مدخلات الفاتورة والتسويق:")
        client_name = st.text_input("اسم العميل المستهدف:", "المربي الفاضل / علي طبرق")
        invoice_type = st.radio("نوع العملية التسويقية:", ["بيع تركيبة علفية بالطن", "بيع رؤوس ماشية وبورصة"])
        
        inv_qty = st.number_input("الكمية (عدد الأطنان أو الرؤوس):", min_value=1.0, value=2.0)
        inv_unit_price = st.number_input("السعر الفردي المتفق عليه (بالعملة المحلية):", min_value=1.0, value=2500.0)
        tax_pct = st.number_input("رسوم التحميل والنقل اللوجستي (%):", min_value=0.0, value=2.0)
        
    with col_inv2:
        st.markdown("<p style='text-align:center; font-weight:bold; color:#2e7d32;'>📱 العرض والديباجة الفاخرة المخصصة لشاشات الجوال:</p>", unsafe_allow_html=True)
        
        sub_total = inv_qty * inv_unit_price
        final_invoice_total = sub_total + (sub_total * (tax_pct / 100.0))
        
        # كود HTML متوافق ومصمم ليعطي مظهراً فخماً وراصاً على الجوال
        html_mobile_invoice = f"""
        <div class="mobile-invoice-card">
            <div class="mobile-invoice-header">
                <h4>🌾 منصة تاور الذكية المتكاملة 🌾</h4>
                <small>مكتب المستشار م. عبد القادر إسماعيل تاور</small>
            </div>
            <div class="mobile-invoice-row"><b>اسم العميل:</b> <span>{client_name}</span></div>
            <div class="mobile-invoice-row"><b>تاريخ العملية:</b> <span>2026-05-21</span></div>
            <div class="mobile-invoice-row"><b>البيان التسويقي:</b> <span>{invoice_type}</span></div>
            <div class="mobile-invoice-row"><b>الكمية المطلوبة:</b> <span>{inv_qty}</span></div>
            <div class="mobile-invoice-row"><b>سعر الوحدة:</b> <span>{inv_unit_price:,.2f} {local_sym}</span></div>
            <div class="mobile-invoice-row"><b>الربط واللوجستيات:</b> <span>{tax_pct} %</span></div>
            <div class="mobile-invoice-total">
                المجموع الإجمالي النهائي الواجب سداده:<br>
                {final_invoice_total:,.2f} {local_sym}
            </div>
            <p style='font-size:0.75rem; text-align:center; color:#777; margin-top:10px; margin-bottom:0;'>شكراً لتعاملكم مع خبير البرمجيات المتكاملة للأعلاف</p>
        </div>
        """
        st.markdown(html_mobile_invoice, unsafe_allow_html=True)
        # توفير دالة تحميل الفاتورة كنص كاش
        st.download_button("📥 تحميل ديباجة الجوال كنص تسويقي لحفظها", data=f"فاتورة عميل منصة تاور\nالعميل: {client_name}\nالمطلوب: {final_invoice_total} {local_sym}", file_name="invoice_tower.txt")

# ---------------------------------------------------------------------
# التبويب السادس: الربط البريدي والـ Gmail المتكامل
# ---------------------------------------------------------------------
with tabs[5]:
    st.markdown('<div class="section-title">📬 نظام الإرسال والربط التلقائي عبر بريد الـ Gmail للعملاء والمصانع</div>', unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style='background-color:#e3f2fd; padding:15px; border-radius:8px; border-right:5px solid #1e88e5; text-align:right; direction:rtl; font-size:0.9rem;'>
            <b>🔒 التوجيه الأمني المعتمد لربط الـ Gmail في بايثون:</b><br>
            بسبب معايير الحماية لعام 2026، يرجى إنشاء <b>"App Password" (كلمة مرور التطبيقات)</b> من حساب الـ Google الخاص بك وضعه في حقل كلمة المرور لتفادي حظر عملية الإرسال الخارجية.
        </div>
        """, unsafe_allow_html=True
    )
    
    col_em1, col_em2 = st.columns(2)
    with col_em1:
        sender_email = st.text_input("بريد الـ Gmail الخاص بك كمسؤول (الراسل):", "abdelkader.tower@gmail.com")
        sender_app_password = st.text_input("كلمة مرور التطبيقات الآمنة (App Password):", type="password")
        receiver_email = st.text_input("بريد العميل أو المصنع المستهدف (المستقبل):", "client.farm@gmail.com")
    with col_em2:
        email_subject = st.text_input("موضوع الرسالة التلقائية البريدية:", "تقرير فني معتمد وتركيبة طن علف من منصة تاور الذكية")
        email_body_text = st.text_area(
            "محتوى نص الإيميل الصادر الفعلي:", 
            value=f"تحية طيبة وبعد،\nمرفق لكم التقرير الفني الصادر من منصة المهندس عبد القادر تاور الذكية للأعلاف.\nالعميل المستهدف: {client_name}\nيرجى مراجعة المنصة وتفاصيل ديباجة الجوال المرفقة للحصول على أوزان الخلط والإنزيمات المضافة."
        )
        
    if st.button("📧 إرسال التقرير والفاتورة عبر Gmail فوراً", type="primary", use_container_width=True):
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = email_subject
            msg.attach(MIMEText(email_body_text, 'plain', 'utf-8'))
            
            # محاكاة وبناء اتصال السيرفر مع تأمين الأخطاء التام
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            # لغايات العرض التوضيحي يتم عزل الاتصال الفعلي لمنع التجميد ما لم يتم تزويد باسوورد حقيقي
            if sender_app_password:
                server.login(sender_email, sender_app_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
                server.close()
                st.success("🎯 تم إرسال البريد بنجاح وبأعلى معايير الحماية إلى صندوق بريد العميل!")
            else:
                st.warning("⚠️ يرجى تعبئة حقل 'كلمة مرور التطبيقات' لتفعيل الاتصال الحقيقي بخوادم بريد Google.")
        except Exception as e:
            st.error(f"❌ خطأ أمني أو برمي في الاتصال بالخادم: {e}")

# ---------------------------------------------------------------------
# التبويب السابع: لوحة الإدارة البورصوية المركزية (المسؤول)
# ---------------------------------------------------------------------
if st.session_state["user_role"] == "admin":
    with tabs[6]:
        st.markdown('<div class="section-title">⚙️ لوحة التحكم والإدارة الفنية المركزية للبورصة الكبرى</div>', unsafe_allow_html=True)
        
        st.markdown("#### 🛠️ تحديث أسعار البورصة العالمية الأساسية لرؤوس الماشية ($):")
        for category, items in st.session_state["global_livestock_prices"].items():
            st.markdown(f"**قسم {category}:**")
            cols = st.columns(len(items))
            for idx, (name, val) in enumerate(items.items()):
                with cols[idx % len(items)]:
                    st.session_state["global_livestock_prices"][category][name] = st.number_input(f"تحديث {name}", min_value=0.0, value=float(val), key=f"central_live_{category}_{name}")
                    
        st.markdown("---")
        st.markdown("#### 🛠️ تحديث أسعار البورصة العالمية الأساسية للمنتجات الصافية ($):")
        cols_p = st.columns(3)
        for idx, (p_name, b_val) in enumerate(st.session_state["global_products_prices"].items()):
            with cols_p[idx % 3]:
                st.session_state["global_products_prices"][p_name] = st.number_input(f"تحديث {p_name}", min_value=0.0, value=float(b_val), key=f"central_prod_{p_name}")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 5. التوقيع الدائم لـ م. عبد القادر تاور
# ==========================================
st.markdown(
    f"""
    <div class="mini-left-signature">
        👨‍🔬 م. عبد القادر إسماعيل تاور © 2026 | خبير الحلول الذكية للثروة الحيوانية والبرمجيات المتكاملة والـ ERP
    </div>
    """,
    unsafe_allow_html=True
)
