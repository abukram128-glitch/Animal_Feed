import streamlit as st
import numpy as np
import time

# ==========================================
# 1. المظهر الكلاسيكي الأول والخلفية الأصلية المفتوحة للبرنامج
# ==========================================
st.set_page_config(page_title="منصة تاور الشاملة للأعلاف والإنتاج الحيواني", page_icon="🌾", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Cairo', sans-serif;
        background-color: #f8fafc; /* الخلفية الهادئة الأولى */
        direction: rtl;
    }
    .main-title-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05);
        border-right: 6px solid #2e7d32;
        margin-bottom: 25px;
        text-align: right;
    }
    .section-title {
        color: #1b5e20;
        font-weight: bold;
        font-size: 1.3rem;
        border-bottom: 2px solid #2e7d32;
        padding-bottom: 5px;
        margin-top: 30px;
        margin-bottom: 15px;
        text-align: right;
    }
    .market-card {
        background: #ffffff;
        border-right: 5px solid #1565c0;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 6px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        text-align: right;
    }
    .alert-countdown {
        background-color: #ffebee;
        color: #b71c1c;
        padding: 15px;
        border-right: 6px solid #b71c1c;
        border-radius: 6px;
        margin: 15px 0;
        text-align: right;
        font-weight: bold;
    }
    .invoice-box {
        background: #ffffff;
        border: 2px solid #455a64;
        padding: 20px;
        border-radius: 10px;
        margin-top: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06);
    }
    /* ديباجة الهواتف الذكية الأنيقة */
    .mobile-sack-tag {
        border: 3px dashed #2e7d32;
        padding: 20px;
        border-radius: 12px;
        background-color: #ffffff;
        max-width: 400px;
        margin: 20px auto;
        box-shadow: 0px 6px 18px rgba(0,0,0,0.08);
        text-align: right;
    }
    .animal-visual-frame {
        border: 1px solid #2e7d32;
        background: #f1f8e9;
        padding: 10px;
        border-radius: 6px;
        text-align: center;
        font-weight: bold;
        color: #1b5e20;
        margin: 10px 0;
    }
    .library-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        background: white;
        border-radius: 6px;
        overflow: hidden;
    }
    .library-table th {
        background-color: #2e7d32;
        color: white;
        padding: 10px;
        text-align: right;
    }
    .library-table td {
        padding: 8px;
        border-bottom: 1px solid #e2e8f0;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. تهيئة المتغيرات والتعليقات النشطة في الخلفية
# ==========================================
if "expert_feedbacks" not in st.session_state: st.session_state["expert_feedbacks"] = []
if "invoice_data" not in st.session_state: st.session_state["invoice_data"] = None
if "computed_formula" not in st.session_state: st.session_state["computed_formula"] = None

# ==========================================
# 3. المصفوفات الجغرافية والبورصة الحية المتطابقة
# ==========================================
GEOGRAPHY_DATABASE = {
    "السودان": {
        "currency": "SDG", "usd_rate": 600.0,
        "states": {
            "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
            "ولاية شمال كردفان": ["الأبيض", "أم روابة"],
            "ولاية القضارف": ["القضارف المدينة", "الفاو"]
        },
        "breeds": {
            "الأبقار وسلالاتها": {"name": "أبقار الكنانة والبطانة المحسنة 🐄", "avatar": "🐄", "graphic": "🐄 [قطاع الأبقار المطور حركياً]"},
            "الأغنام والضأن": {"name": "ضأن الدوبا والكباشي الحركي 🐑", "avatar": "🐑", "graphic": "🐑 [قطاع المجترات الصغيرة للتسمين]"},
            "الخيول والفروسية": {"name": "الجواد الدنقلاوي الأصيل 🐎", "avatar": "🐎", "graphic": "🐎 [قطاع الجياد والفروسية المتكامل]"},
            "الطيور والدواجن": {"name": "دواجن هبرد وسلالات المزارع 🐓", "avatar": "🐓", "graphic": "🐓 [قطاع طيور التسمين والبياض]"}
        },
        "prices": {"عجول تسمين حي (كجم)": 3200, "خراف صادر قائم (رأس)": 180000, "لتر حليب خام": 1200, "طن علف تسمين أساسي": 480000}
    },
    "ليبيا": {
        "currency": "LYD", "usd_rate": 4.82,
        "states": {
            "الإقليم الغربي طرابلس": ["طرابلس", "مصراتة"],
            "إقليم البطنان والشرق": ["طبرق", "بنغازي"],
            "فزان والجنوب": ["سبها", "مرزق"]
        },
        "breeds": {
            "الأبقار وسلالاتها": {"name": "أبقار الفريزيان المؤقلمة محلياً 🐄", "avatar": "🐄", "graphic": "🐄 [أبقار إنتاج الحليب والتسمين بلاد ليبيا]"},
            "الأغنام والضأن": {"name": "أغنام البرقي الليبية العريقة 🐑", "avatar": "🐑", "graphic": "🐑 [أغنام البرقي وصغار الحملان]"},
            "الخيول والفروسية": {"name": "الجواد العربي الليبي الفاخر 🐎", "avatar": "🐎", "graphic": "🐎 [خيول السباق والسرعة الليبية]"},
            "الطيور والدواجن": {"name": "سلالات كب 500 للإنتاج المكثف 🐓", "avatar": "🐓", "graphic": "🐓 [دواجن اللحم والبيض التجاري]"}
        },
        "prices": {"عجول تسمين حي (كجم)": 38, "خراف برقي ممتازة (رأس)": 1400, "لتر حليب طازج": 4.5, "طن علف تسمين أساسي": 1950}
    },
    "مصر": {
        "currency": "EGP", "usd_rate": 48.0,
        "states": {
            "محافظات القاهرة الكبرى": ["القاهرة", "الجيزة"],
            "محافظات الدلتا": ["طنطا", "المنصورة"],
            "محافظات الصعيد": ["أسيوط", "أسوان"]
        },
        "breeds": {
            "الأبقار وسلالاتها": {"name": "الأبقار البلدي والجاموس المصري 🐄", "avatar": "🐄", "graphic": "🐄 [الأبقار الحلابة والتسمين بمصر]"},
            "الأغنام والضأن": {"name": "أغنام الرحماني والأوسيمي الفاخرة 🐑", "avatar": "🐑", "graphic": "🐑 [تسمين الخراف والنعاج المصرية]"},
            "الخيول والفروسية": {"name": "الحصان العربي الفحل المستقيم 🐎", "avatar": "🐎", "graphic": "🐎 [الخيول العربية الأصيلة بمصر]"},
            "الطيور والدواجن": {"name": "كتكوت روس 308 مزارع الدلتا 🐓", "avatar": "🐓", "graphic": "🐓 [قطاع الدواجن والطيور الداجنة بمصر]"}
        },
        "prices": {"عجول تسمين قائم (كجم)": 175, "خراف بلدي حية (رأس)": 11000, "لتر حليب جاموسي": 35, "طن علف تسمين أساسي": 18500}
    }
}

SECTOR_STAGES = {
    "الأبقار وسلالاتها": {"تسمين عجول مكثف سريع": 14.5, "إدرار حليب طاقة عالية": 17.5, "أمهات حوامل مجففة": 12.0},
    "الأغنام والضأن": {"تسمين حملان أسواق": 16.0, "نعاج مرضعة ومدرة": 14.5, "دفع غذائي قبل التلقيح": 12.5},
    "الخيول والفروسية": {"جياد سباق وسرعة دؤوب": 14.0, "أمهر نامية حديثة الفطام": 15.5},
    "الطيور والدواجن": {"بادي لاحم تسمين مكثف": 23.0, "نامي لاحم متوازن": 21.0, "بياض إنتاجي تجاري": 17.5}
}

BIG_LIBRARY = {
    "مصادر الطاقة الحيوية": {"ذرة صفراء": 8.5, "ذرة بيضاء بلدية": 9.0, "شعير مطحون": 11.5},
    "الأكساب والبروتينات": {"أمباز فول سوداني": 45.0, "كسب صويا 44%": 44.0, "كسب صويا 48%": 48.0},
    "المواد الرعوية والمالئة": {"نخالة قمح (ردة)": 15.0, "دريس حجازي منقح": 17.0},
    "الإضافات والمركزات": {"مركزات تسمين 5%": 36.0, "حجر جيري ناعم": 0.0, "بيكربونات الصوديوم": 0.0}
}

# ==========================================
# 4. ترويسة العرض الكلاسيكية الأولى والثابتة
# ==========================================
st.markdown(
    """
    <div class="main-title-box">
        <h1 style="margin:0; color:#1b5e20;">منصة تاور الرقمية الشاملة للأعلاف والإنتاج الحيواني 🌾</h1>
        <h3 style="margin:5px 0 0 0; color:#c62828;">المستشار الفني الخبير: م. عبد القادر إسماعيل تاور</h3>
        <p style="margin:5px 0 0 0; color:#555;">الإصدار الحقلي والأكاديمي المتكامل لعام 2026</p>
    </div>
    """, unsafe_allow_html=True
)

# ==========================================
# أولاً: تفاصيل الموقع الجغرافي العريض
# ==========================================
st.markdown('<div class="section-title">📍 تفاصيل الموقع الجغرافي والتزامن الحركي الكلي</div>', unsafe_allow_html=True)
col_g1, col_g2, col_g3 = st.columns(3)
with col_g1: geo_country = st.selectbox("اختر الدولة المستهدفة:", list(GEOGRAPHY_DATABASE.keys()))
country_data = GEOGRAPHY_DATABASE[geo_country]
with col_g2: geo_state = st.selectbox("الولاية / المحافظة الإقليمية:", list(country_data["states"].keys()))
with col_g3: geo_city = st.selectbox("المدينة المرتبطة بالبورصة الميدانية:", country_data["states"][geo_state])

# ==========================================
# ثانياً: دالة شريط القياس لتقدير الوزن الحي
# ==========================================
st.markdown('<div class="section-title">📏 دالة شريط القياس الميداني لتقدير الوزن الحي الفعلي</div>', unsafe_allow_html=True)
col_w1, col_w2, col_w3 = st.columns(3)
with col_w1: calc_sector = st.selectbox("صنف الحيوان المستهدف بالقياس:", list(SECTOR_STAGES.keys()))
with col_w2: girth_cm = st.number_input("مقاس محيط الصدر خلف المرفق (بالسنتيمتر):", min_value=20.0, value=165.0)
with col_w3: length_cm = st.number_input("مقاس طول الجسم المستقيم للحيوان (بالسنتيمتر):", min_value=20.0, value=145.0)

if calc_sector == "الأبقار وسلالاتها": calculated_weight = (girth_cm ** 2 * length_cm) / 10838
elif calc_sector == "الخيول والفروسية": calculated_weight = (girth_cm ** 2 * length_cm) / 11877
else: calculated_weight = (girth_cm ** 2 * length_cm) / 11312

st.success(f"⚖️ الوزن الحي التقديري الصافي الناتج عن الدالة الحقلية: **{calculated_weight:.2f} كجم قائم**")

# ==========================================
# ثالثاً: بورصة الحيوانات والمنتجات الحية (التطابق الكامل)
# ==========================================
st.markdown(f'<div class="section-title">📊 أسعار بورصة الحيوانات والمنتجات في أسواق ({geo_country}) وعملتها مقابل الدولار</div>', unsafe_allow_html=True)
st.write(f"🧬 سلالة الحيوان المعتمدة جغرافياً في النطاق الحالي: **{country_data['breeds'][calc_sector]['name']}**")

col_b1, col_b2 = st.columns(2)
with col_b1:
    st.markdown(f"##### 💵 الأسعار المتطابقة بالعملة المحلية ({country_data['currency']})")
    for item, price in country_data["prices"].items():
        st.markdown(f"<div class='market-card'>🔹 <b>{item}:</b> {price:,} {country_data['currency']}</div>", unsafe_allow_html=True)
with col_b2:
    st.markdown("##### 🇺🇸 المقابل الفوري بالنقد الأجنبي ($ دولار أمريكي)")
    for item, price in country_data["prices"].items():
        usd_p = price / country_data["usd_rate"]
        st.markdown(f"<div class='market-card' style='border-right-color: #2e7d32;'>🟢 <b>{item}:</b> ${usd_p:,.2f} USD <small>(سعر الصرف لعام 2026: {country_data['usd_rate']})</small></div>", unsafe_allow_html=True)

# ==========================================
# رابعاً: الصبغة العلمية والبروتين المزدوج والإنزيمات الإجبارية
# ==========================================
st.markdown('<div class="section-title">🔬 النمذجة والصبغة العلمية لتكوين علائق الطن</div>', unsafe_allow_html=True)

col_s1, col_s2 = st.columns(2)
with col_s1:
    chosen_stage = st.selectbox("اختر المرحلة الفسيولوجية والغرض الإنتاجي للحيوان:", list(SECTOR_STAGES
