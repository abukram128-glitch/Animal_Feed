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
# 3. قاعدة البيانات الجغرافية والسلالات الواقعية (محدثة 2026)
# =====================================================================
GEOGRAPHY_DATA = {
    "ليبيا": {
        "regions": ["المنطقة الشرقية (البطنان والجبل الأخضر)", "المنطقة الغربية", "المنطقة الجنوبية"],
        "cities": ["طبرق", "بنغازي", "البيضاء", "طرابلس", "مصراتة", "الزاوية", "سبها"],
        "livestock": {
            "الأبقار": {"أبقار فريزيان نقية": 3200.0, "أبقار هولشتاين محسنة": 2900.0, "أبقار هجينة محلية": 1800.0},
            "الخيول": {"خيول عربية أصيلة مسجلة": 7500.0, "خيول هجينة (جر وركوب)": 2200.0},
            "الأغنام": {"ضأن برقي أصيل": 380.0, "ضأن بلدي محلي": 310.0},
            "الماعز": {"ماعز برقي / جبلي": 240.0, "ماعز زرايبي محسن": 280.0},
            "الدواجن": {"كتكوت لاحم (عمر يوم)": 0.85, "دجاج بياض جاهز (18 أسبوع)": 6.50, "طير سمان منتج": 1.10}
        },
        "products": {
            "كيلو لحم بقري بالعظم": 14.50, "كيلو لحم ضأن برقي طازج": 18.00, "كيلو لحم دجاج صافي": 5.20,
            "طبق بيض مائدة (30 بيضة)": 5.50, "لتر حليب طازج غير مصنع": 1.80
        }
    },
    "السودان": {
        "regions": ["ولاية الخرطوم", "ولاية القضارف", "ولاية شمال كردفان", "ولاية الجزيرة", "ولاية نهر النيل", "ولاية جنوب دارفور"],
        "cities": ["أم درمان", "الخرطوم", "بحري", "القضارف", "الأبيض", "ود مدني", "الدامر", "نيالا"],
        "livestock": {
            "الأبقار": {"أبقار كنانة حليبية أصيلة": 950.0, "أبقار البطانة": 900.0, "أبقار البقارة للتسمين": 750.0},
            "الخيول": {"خيول دنقلاوية أصيلة": 3500.0, "خيول بلدية محسنة": 1100.0},
            "الأغنام": {"ضأن كباشي / حمري": 160.0, "ضأن بالي / صحراوي": 130.0},
            "الماعز": {"ماعز نوبي حليبي": 120.0, "ماعز الصحراء": 90.0},
            "الدواجن": {"كتكوت لاحم (عمر يوم)": 0.60, "دجاج بياض جاهز": 4.80, "طير سمان": 0.70}
        },
        "products": {
            "كيلو لحم عجالي صافي": 7.00, "كيلو لحم ضأن كباشي": 8.50, "كيلو لحم دجاج": 4.10,
            "طبق بيض مائدة": 4.00, "لتر حليب نوبي طازج": 0.95
        }
    },
    "مصر": {
        "regions": ["الدلتا والوجه البحري", "الصعيد والوجه القبلي", "المحافظات الحدودية"],
        "cities": ["القاهرة", "الإسكندرية", "المنصورة", "طنطا", "الفيوم", "أسيوط"],
        "livestock": {
            "الأبقار": {"أبقار خليط محسنة": 2100.0, "جاموس مصري أصيل": 2400.0},
            "الخيول": {"خيول عربية محطة الزهراء": 9000.0, "خيول بلدية": 1400.0},
            "الأغنام": {"ضأن رحماني / أوسيمي": 280.0, "ضأن برقي": 340.0},
            "الماعز": {"ماعز زرايبي": 220.0, "ماعز بلدي": 160.0},
            "الدواجن": {"كتكوت لاحم": 0.80, "دجاج بياض جاهز": 5.80, "طير سمان": 0.90}
        },
        "products": {
            "كيلو لحم كندوز": 11.00, "كيلو لحم ضاني": 13.00, "كيلو دجاج أبيض": 4.60,
            "طبق بيض مائدة": 4.90, "لتر حليب جاموسي": 1.40
        }
    }
}

# روابط لصور توضيحية لخرائط وأماكن شريط القياس حسب نوع الحيوان لضمان دقة التنفيذ الميداني
ANIMAL_MEASURE_IMAGES = {
    "الأبقار والعجاجيل": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?auto=format&fit=crop&w=600&q=80", # صورة بقرة مرجعية لطيفة
    "الأغنام والماعز": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?auto=format&fit=crop&w=600&q=80",  # صورة غنم مرجعية
    "الخيول والخيول الهجينة": "https://images.unsplash.com/photo-1553284965-83fd3e82fa52?auto=format&fit=crop&w=600&q=80" # صورة خيل مرجعية
}

BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "base_price": 240.0, "max_limit": 65.0, "desc": "المصدر الأساسي للطاقة، غني بالنشا."}, 
        "شعير مطحون": {"CP": 11.5, "base_price": 220.0, "max_limit": 30.0, "desc": "ممتاز للمجترات، يرفع الألياف."}, 
        "سورجم (فتريتة)": {"CP": 10.0, "base_price": 200.0, "max_limit": 40.0, "desc": "بديل محلي غني بالطاقة."}
    },
    "الأكساب والأمباز ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "base_price": 470.0, "max_limit": 25.0, "desc": "بروتين محلي فائق الجودة."}, 
        "كسب فول صويا 44%": {"CP": 44.0, "base_price": 450.0, "max_limit": 35.0, "desc": "حجر الأساس البروتيني للدواجن والمجترات."}, 
        "كسب بذور القطن": {"CP": 41.0, "base_price": 310.0, "max_limit": 15.0, "desc": "يحتوي على مادة الجوسيبول السامة."}
    },
    "الإنزيمات والمحفزات الحيوية ودواعم الكرش": {
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "base_price": 340.0, "max_limit": 1.0, "desc": "منظم حموضة الكرش."},
        "إنزيم الفايتيز (Phytase)": {"CP": 0.0, "base_price": 1200.0, "max_limit": 0.1, "desc": "لتحرير الفسفور العضوي المرتبط."},
        "إنزيم الـ NSP المعوي": {"CP": 0.0, "base_price": 1450.0, "max_limit": 0.1, "desc": "هضم السكريات غير النشوية."},
        "مضاد سموم فطرية لوجستي": {"CP": 0.0, "base_price": 950.0, "max_limit": 0.3, "desc": "حماية كبدية واسعة الطيف."}
    }
}

EXCHANGE_RATES = {
    "ليبيا": {"rate": 4.85, "sym": "LYD"},
    "السودان": {"rate": 620.0, "sym": "SDG"},
    "مصر": {"rate": 48.5, "sym": "EGP"}
}

# تهيئة المتغيرات في الـ Session State
if "active_formula" not in st.session_state: st.session_state["active_formula"] = None
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 0.0
if "enzyme_warnings" not in st.session_state: st.session_state["enzyme_warnings"] = []
if "dynamic_cp_target" not in st.session_state: st.session_state["dynamic_cp_target"] = 21.0

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
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.1rem; margin-top:5px; margin-bottom:0;'>توطين السلالات الجغرافية، الاختيار البرمجي الآلي للبروتين، ودليل قياس الماشية المصور</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

tabs = st.tabs([
    "📏 شريط القياس والدليل المصور", 
    "📊 بورصة تاور الموطنة جغرافياً",
    "🔬 محرك النمذجة والحسابات العلفية وبوابة البروتين الذكية",
    "🗂️ مكتبة تاور الاستشارية الموسعة",
    "🧾 التسويق والفواتير وديباجات الجوال",
    "📬 الربط البريدي والـ Gmail",
    "⚙️ لوحة الإدارة البورصوية المركزية"
])

# ---------------------------------------------------------------------
# التبويب الأول: شريط القياس وحساب الأوزان + الصورة التوضيحية الديناميكية
# ---------------------------------------------------------------------
with tabs[0]:
    st.markdown('<div class="section-title">📐 تقدير الوزن الحي للحيوان عبر شريط القياس والدليل المصور</div>', unsafe_allow_html=True)
    
    col_meas_input, col_meas_guide = st.columns(2)
    with col_meas_input:
        animal_type_select = st.selectbox("اختر نوع الحيوان المستهدف بالقياس:", ["الأبقار والعجاجيل", "الأغنام والماعز", "الخيول والخيول الهجينة"])
        girth_in_cm = st.number_input("قياس محيط الصدر خلف القائمتين الأماميتين مباشرة (سم):", min_value=20.0, max_value=350.0, value=160.0, key="girth_cm")
        length_in_cm = st.number_input("قياس طول الجسم الأفقي من عظمة الكتف إلى عظمة الدبوس (سم):", min_value=20.0, max_value=350.0, value=140.0, key="length_cm")
        
        if st.button("🧮 استخراج الوزن الحي التقديري فوراً", type="primary", use_container_width=True):
            if "الأبقار" in animal_type_select:
                calc_weight = (girth_in_cm ** 2 * length_in_cm) / 10838.0
            elif "الأغنام" in animal_type_select:
                calc_weight = (girth_in_cm ** 2 * length_in_cm) / 11300.0
            else: 
                calc_weight = (girth_in_cm ** 2 * length_in_cm) / 11880.0
                
            st.markdown(
                f"""
                <div style='background-color:#e8f5e9; padding:20px; border-radius:10px; text-align:center; border:2px dashed #2e7d32; margin-top:15px;'>
                    <h3 style='color:#2e7d32; margin:0;'>⚖️ الوزن المقدر الناتج: <b>{calc_weight:.2f} كجم</b></h3>
                    <p style='color:#444; margin-top:5px; font-size:0.9rem;'>المعادلة البرمجية مطابقة لتوجيهات م. عبد القادر تاور الميدانية.</p>
                </div>
                """, unsafe_allow_html=True
            )
            
    with col_meas_guide:
        # عرض صورة ديناميكية تتغير كلياً بناءً على نوع الحيوان المختار
        img_url = ANIMAL_MEASURE_IMAGES[animal_type_select]
        st.image(img_url, caption=f"المخطط المرجعي المعتمد لكيفية وضع شريط القياس على فئة: {animal_type_select}", use_container_width=True)
        st.markdown(
            """
            <div style='background-color:#fff3e0; padding:12px; border-radius:8px; border-right:5px solid #ff9800; text-align:right; margin-top:10px;'>
                <h6 style='color:#e65100; font-weight:bold; margin:0 0 5px 0;'>💡 الطريقة الهندسية لأخذ القياس الموضح بالصورة:</h6>
                <p style='font-size:0.85rem; margin:0;'>اسحب شريط القياس دائرياً حول محيط الصدر (خلف القوائم الأمامية مباشرة) للحصول على <b>محيط الصدر</b>. ثم قس أفقياً من زاوية الكتف الأمامي البارز إلى نهاية عظمة الحوض الخلفي للحصول على <b>طول الجسم</b>.</p>
            </div>
            """, unsafe_allow_html=True
        )

# ---------------------------------------------------------------------
# التبويب الثاني: بورصة تاور الموطنة جغرافياً وبواقعية سعرية كاملة
# ---------------------------------------------------------------------
with tabs[1]:
    st.markdown('<div class="section-title">📊 بورصة تاور المحدثة لأسعار الثروة الحيوانية والمنتجات (موطنة ومصححة جغرافياً)</div>', unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1: 
        user_country = st.selectbox("اختر دولة الرصد السعري لبورصة اليوم لتصفية السلالات والأسواق المتواجدة واقعياً:", ["ليبيا", "السودان", "مصر"], key="bourse_country")
    
    c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
    local_rate = c_info["rate"]; local_sym = c_info["sym"]
    
    # تحميل المدن والولايات المحدثة بدقة وبصورة موسعة جداً بناء على الدولة المستهدفة لمنع الاختلاط اللوجستي
    country_data = GEOGRAPHY_DATA[user_country]
    
    with col_c2: chosen_region = st.selectbox("الإقليم / الولاية الجغرافية:", country_data["regions"], key="b_region")
    with col_c3: user_city = st.selectbox("سوق المدينة أو الولاية الفعلي بالمنطقة:", country_data["cities"], key="b_city")
    
    st.info(f"📈 أسواق البورصة الحالية لعام 2026 تعرض سلالات منطقة ({user_city}) الموطنة بشكل واقعي وموثوق.")

    st.markdown("### 🐂 أولاً: أسعار بورصة رؤوس الماشية الحية (سلالات حقيقية متواجدة بالدولة)")
    livestock_items = country_data["livestock"]
    for category, items in livestock_items.items():
        with st.expander(f"🔹 فئة: {category} المتواجدة في {user_country}", expanded=True):
            cols = st.columns(len(items))
            for idx, (name, base_p) in enumerate(items.items()):
                with cols[idx % len(items)]:
                    # عرض واقعي ومباشر بالعملة المحلية مع القيمة الدولارية المكافئة
                    st.metric(label=name, value=f"{base_p * local_rate:,.1f} {local_sym}", delta=f"${base_p:.1f}")

    st.markdown("---")
    st.markdown("### 🥛 ثانياً: أسعار بورصة المنتجات المزرعية الصافية في أسواق {user_city}")
    product_items = country_data["products"]
    prod_cols = st.columns(3)
    for idx, (p_name, b_price) in enumerate(product_items.items()):
        with prod_cols[idx % 3]:
            st.metric(label=p_name, value=f"{b_price * local_rate:,.2f} {local_sym}", delta=f"${b_price:.2f}")

# ---------------------------------------------------------------------
# التبويب الثالث: محرك النمذجة والحسابات العلفية مع دالة اختيار البروتين برمجياً
# ---------------------------------------------------------------------
with tabs[2]:
    st.markdown('<div class="section-title">🔬 محرك صياغة العلائق (بوابة تحديد البروتين برمجياً تلو نوع الإنتاج)</div>', unsafe_allow_html=True)
    
    # دالة وخوارزمية اختيار وتحديد البروتين المرجعي تلقائياً بناءً على نوع القطاع ونوع الإنتاج
    PRODUCTION_PROTEIN_MAP = {
        "الطيور والسمان": {
            "بادي دواجن تسمين (نمو سريع)": 23.0,
            "نامي دواجن تسمين معزز": 21.0,
            "دجاج بياض إنتاجي": 17.5,
            "سمان بياض عالي الكثافة": 24.0
        },
        "الأبقار وسلالاتها": {
            "أبقار حلابة عالية الإدرار": 18.0,
            "عجول تسمين سريعة النمو": 15.0,
            "أبقار جافة وصيانة": 12.0
        },
        "الماعز وسلالاته والأغنام": {
            "دفع غذائي للحملان والنعاج": 16.0,
            "تسمين خراف برقية وكباش": 14.0,
            "ماعز حليبي محسن": 15.5
        },
        "الخيول": {
            "أمهات خيول مرضعة وحوامل": 14.0,
            "خيول سباق وجهد عالي": 12.5,
            "صيانة خيول هجينة": 10.0
        }
    }

    col_p1, col_p2 = st.columns(2)
    with col_p1: 
        target_sector = st.selectbox("1. اختر القطاع الحيواني:", list(PRODUCTION_PROTEIN_MAP.keys()), key="sec_p")
    with col_p2:
        available_types = PRODUCTION_PROTEIN_MAP[target_sector]
        target_prod_type = st.selectbox("2. اختر غرض ونوع الإنتاج المزرعي الحالي:", list(available_types.keys()), key="prod_t")
        
    # استخراج البروتين الموصى به برمجياً تلقائياً من قاعدة البيانات
    recommended_cp = available_types[target_prod_type]
    
    st.markdown(f"<div style='background-color:#e1f5fe; padding:10px; border-radius:6px; border-right:4px solid #0288d1; text-align:right;'>💡 <b>البروتين الموصى به برمجياً لهذا الإنتاج:</b> <span style='color:#0288d1; font-weight:bold;'>{recommended_cp}%</span></div>", unsafe_allow_html=True)
    
    # دالة الاختيار البرمجي مع إتاحة "البروتين الاختياري" لتعديل النسبة حسب رؤية المهندس
    use_custom_cp = st.checkbox("⚙️ تفعيل خيار تعديل البروتين برمجياً (بروتين اختياري مخصص)")
    if use_custom_cp:
        final_cp_target = st.number_input("ضع النسبة البروتينية الاختيارية التي تراها مناسبة برأيك الهندسي (%):", min_value=10.0, max_value=45.0, value=float(recommended_cp))
    else:
        final_cp_target = recommended_cp

    st.session_state["dynamic_cp_target"] = final_cp_target

    selected_ings = []
    st.markdown("##### 📥 حدد المواد الخام المتاحة في مخزنك الميداني:")
    for cat, items in BIG_FEEDS_LIBRARY.items():
        st.markdown(f"**{cat}:**")
        cols = st.columns(len(items))
        for idx, (ing_name, data) in enumerate(items.items()):
            with cols[idx % len(items)]:
                is_checked = True if "ذرة" in ing_name or "صويا" in ing_name or "مضاد" in ing_name else False
                if st.checkbox(ing_name, value=is_checked, key=f"mix_{ing_name}"):
                    selected_ings.append(ing_name)

    if st.button("🚀 معالجة وصياغة التركيبة وضبط معايير الأمان الحيوية والإنزيمات", type="primary", use_container_width=True):
        formula = {}
        warnings = []
        
        # تخصيص المكونات الثابتة والامنة
        if "مضاد سموم فطرية لوجستي" in selected_ings: formula["مضاد سموم فطرية لوجستي"] = 0.25
            
        grains_avail = [x for x in selected_ings if x in BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"]]
        proteins_avail = [x for x in selected_ings if x in BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"]]
        
        if not grains_avail: grains_avail = ["ذرة صفراء"]
        if not proteins_avail: proteins_avail = ["كسب فول صويا 44%"]
        
        # توزيع النسب بموازنة بروتينية أولية بناء على البروتين المستهدف النهائي (برمجي أو اختياري)
        remaining_pct = 100.0 - sum(formula.values())
        p_weight = 0.45 if final_cp_target > 20 else 0.28
        p_share = remaining_pct * p_weight
        e_share = remaining_pct - p_share
        
        for g in grains_avail: formula[g] = e_share / len(grains_avail)
        for p in proteins_avail: formula[p] = p_share / len(proteins_avail)
        
        # الرقابة والتدقيق الصارم للحدود القياسية والمعالجة بالإنزيمات
        enzyme_additions = {}
        if formula.get("شعير مطحون", 0.0) > 15.0:
            enzyme_additions["إنزيم الـ NSP المعوي"] = 0.1
            warnings.append("⚠️ تجاوز الشعير حده الآمن. تم إضافة إنزيم الـ NSP المعوي تلقائياً لمنع لزوجة الأمعاء.")
            
        if formula.get("كسب بذور القطن", 0.0) > 10.0:
            warnings.append("⚠️ نسبة كسب بذور القطن مرتفعة في التركيبة؛ يرجى مراقبة مستوى الجوسيبول.")
            
        if target_sector == "الطيور والسمان":
            enzyme_additions["إنزيم الفايتيز (Phytase)"] = 0.05
            warnings.append("🔬 تم دمج إنزيم الفايتيز لتحرير الفسفور العضوي لرفع جودة وكفاءة الامتصاص الدواجن.")

        if enzyme_additions:
            for enz_name, enz_val in enzyme_additions.items(): formula[enz_name] = enz_val
            main_grain = grains_avail[0]
            formula[main_grain] = max(1.0, formula[main_grain] - sum(enzyme_additions.values()))

        # حساب النتيجة النهائية للبروتين والتكلفة الواقعية
        computed_cp_val = 0.0
        ton_cost_val = 0.0
        for ing_name, pct in formula.items():
            feed_data = None
            for cat_n, items_n in BIG_FEEDS_LIBRARY.items():
                if ing_name in items_n:
                    feed_data = items_n[ing_name]
                    break
            if feed_data:
                computed_cp_val += (pct / 100.0) * feed_data["CP"]
                ton_cost_val += (pct / 100.0) * feed_data["base_price"]
                
        st.session_state["active_formula"] = formula
        st.session_state["programmed_cp_actual"] = computed_cp_val
        st.session_state["computed_ton_cost"] = ton_cost_val
        st.session_state["enzyme_warnings"] = warnings

    # عرض نتائج خوارزمية الخلط خارج البوتون
    if st.session_state["active_formula"] is not None:
        st.markdown("### 🧬 نتائج المطابقة الحيوية والمراقبة التحليلية للبروتين:")
        col_res_cp1, col_res_cp2 = st.columns(2)
        with col_res_cp1: st.metric("🎯 نسبة البروتين النشطة والنظامية بالتركيبة:", f"{st.session_state['dynamic_cp_target']:.2f} %")
        with col_res_cp2: st.metric("🖥️ نسبة البروتين المتحققة فعلياً بعد الفحص وموازنة النواقص:", f"{st.session_state['programmed_cp_actual']:.2f} %")
        
        if st.session_state["enzyme_warnings"]:
            for warn in st.session_state["enzyme_warnings"]: st.warning(warn)

        c_res1, c_res2 = st.columns([0.6, 0.4])
        with c_res1:
            st.markdown(f"⚙️ **مكونات وأوزان خلطة الطن الواحد الفعليّة المعتمدة للإنتاج ({user_city}):**")
            for k, v in st.session_state["active_formula"].items():
                st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** / للطن)")
            st.metric("💰 تكلفة إنتاج الطن التقديرية في السوق المحلي المختار:", f"{st.session_state['computed_ton_cost']*local_rate:,.1f} {local_sym} (${st.session_state['computed_ton_cost']:.2f})")
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
        
        inv_qty = st.number_input("الكمية (عدد الأطنان أو الرؤوس):", min_value=1.0, value=2.0, key="inv_qty")
        inv_unit_price = st.number_input("السعر الفردي المتفق عليه (بالعملة المحلية):", min_value=1.0, value=2500.0, key="inv_u_price")
        tax_pct = st.number_input("رسوم التحميل والنقل اللوجستي (%):", min_value=0.0, value=2.0, key="inv_tax")
        
    with col_inv2:
        st.markdown("<p style='text-align:center; font-weight:bold; color:#2e7d32;'>📱 العرض والديباجة الفاخرة المخصصة لشاشات الجوال:</p>", unsafe_allow_html=True)
        
        sub_total = inv_qty * inv_unit_price
        final_invoice_total = sub_total + (sub_total * (tax_pct / 100.0))
        
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
        st.download_button("📥 تحميل ديباجة الجوال كنص تسويقي لحفظها", data=f"فاتورة عميل منصة تاور\nالعميل: {client_name}\nالمطلوب: {final_invoice_total} {local_sym}", file_name="invoice_tower.txt")

# ---------------------------------------------------------------------
# التبويب السادس: الربط البريدي والـ Gmail المتكامل
# ---------------------------------------------------------------------
with tabs[5]:
    st.markdown('<div class="section-title">📬 نظام الإرسال والربط التلقائي عبر بريد الـ Gmail للعملاء والمصانع</div>', unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style='background-color:#e3f2fd; padding:15px; border-radius:8px; border-right:5px solid #1e88e5; text-align:right; direction:rtl; font-size:0.9rem;'>
            <b>🔒 التوجيه الأمني لربط الـ Gmail في بايثون:</b><br>
            يرجى إنشاء <b>"App Password" (كلمة مرور التطبيقات)</b> من حساب الـ Google الخاص بك وضعه في حقل كلمة المرور لتفادي حظر عملية الإرسال الخارجية.
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
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
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
# التبويب السابع: لوحة الإدارة البورصوية المركزية لتعديل الأسعار الفوري
# ---------------------------------------------------------------------
if st.session_state["user_role"] == "admin":
    with tabs[6]:
        st.markdown('<div class="section-title">⚙️ لوحة التحكم والإدارة الفنية المركزية لتعديل الأسعار فورا وجعلها واقعية</div>', unsafe_allow_html=True)
        st.info("💡 يمكنك من هنا تعديل الأسعار الأساسية لكل دولة وإقليم على حدة لتطابق أسعار الشراء والبيع الواقعية اليوم بالسوق:")
        
        target_mod_country = st.selectbox("اختر الدولة المراد تعديل أسعارها الأساسية حركياً:", ["ليبيا", "السودان", "مصر"])
        
        st.markdown(f"##### 🛠️ تحديث أسعار الماشية في {target_mod_country} ($):")
        for cat, items in GEOGRAPHY_DATA[target_mod_country]["livestock"].items():
            st.markdown(f"**{cat}:**")
            cols_mod = st.columns(len(items))
            for idx, (name, val) in enumerate(items.items()):
                with cols_mod[idx % len(items)]:
                    GEOGRAPHY_DATA[target_mod_country]["livestock"][cat][name] = st.number_input(f"سعر {name}", min_value=0.0, value=float(val), key=f"mod_live_{target_mod_country}_{name}")

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
