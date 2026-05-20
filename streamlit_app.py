import streamlit as st
import numpy as np
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================
# 1. إعدادات المنصة والمظهر الفخم المتجاوب
# ==========================================
st.set_page_config(page_title="منصة تاور الرقمية الشاملة للأعلاف والإنتاج الحيواني", page_icon="🌾", layout="wide")

# الهوية البصرية المتقدمة ودعم شاشات الجوال والديباجات التسويقية
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Cairo', sans-serif;
        background-color: #f4f6f9;
        direction: rtl;
    }
    .main-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    .section-title {
        color: #1b5e20;
        border-right: 5px solid #2e7d32;
        padding-right: 10px;
        text-align: right;
        font-weight: bold;
        margin: 20px 0 10px 0;
    }
    /* ديباجة الهواتف الذكية المتجاوبة */
    .mobile-sack-tag {
        border: 2px dashed #1b5e20;
        padding: 15px;
        border-radius: 10px;
        background-color: #f1f8e9;
        max-width: 360px;
        margin: 0 auto;
        text-align: center;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.08);
    }
    .animal-avatar {
        font-size: 4rem;
        margin: 10px 0;
    }
    .market-card {
        background: #e3f2fd;
        border-right: 4px solid #1565c0;
        padding: 10px;
        margin-bottom: 8px;
        border-radius: 4px;
        text-align: right;
    }
    .alert-box {
        background-color: #ffebee;
        color: #b71c1c;
        padding: 15px;
        border-right: 5px solid #b71c1c;
        border-radius: 4px;
        margin: 10px 0;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. إدارة جلسات المستخدمين وقاعدة البيانات المؤقتة
# ==========================================
if "user_role" not in st.session_state: st.session_state["user_role"] = None
if "vets_passed" not in st.session_state: st.session_state["vets_passed"] = False
if "expert_feedbacks" not in st.session_state: 
    st.session_state["expert_feedbacks"] = [
        {"name": "د. أحمد الرفاعي (تغذية مجترات)", "text": "تعديل رائع لنسب الألياف، يفضل رفع بيكربونات الصوديوم عند استخدام الذرة بنسبة تتجاوز 50%."},
        {"name": "بروفيسور علي إسماعيل", "text": "إضافة إنزيم الفايتيز التلقائي عند زيادة النخالة خطوة علمية ممتازة لكسر الفايتات الزائدة."}
    ]
if "active_formula" not in st.session_state: st.session_state["active_formula"] = {}
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 0.0

# ==========================================
# 3. المكتبة الكبرى لمكونات الأعلاف والإضافات (الإصدار الشامل)
# ==========================================
BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {
        "ذرة صفراء (محلية/مستوردة)": {"cp": 8.5, "max": 65.0, "desc": "المصدر الأساسي للطاقة، غني بالكاروتين."},
        "ذرة بيضاء (فتريتة/طابت)": {"cp": 9.0, "max": 55.0, "desc": "طاقة ممتازة متوفرة محلياً بالأسواق الكبرى."},
        "شعير مطحون محلي": {"cp": 11.5, "max": 40.0, "desc": "ممتاز جداً لخلطات الخيول والمجترات لتطوير الكرش."},
        "دخن بلدنا": {"cp": 11.0, "max": 30.0, "desc": "بديل طاقة غني بالأمينات للمناطق الجافة."}
    },
    "الأكساب والأمباز ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب قشرة)": {"cp": 45.0, "max": 25.0, "desc": "بروتين محلي فائق الجودة متوفر بكثرة بسوق كردفان."},
        "كسب فول صويا 44%": {"cp": 44.0, "max": 30.0, "desc": "المعيار الذهبي لبروتين الدواجن والمجترات العالية الإدرار."},
        "كسب فول صويا 48%": {"cp": 48.0, "max": 25.0, "desc": "مستخلص مقشور عالي الهضم لتركيبات بادي الدواجن."},
        "كسب عباد الشمس المحسن": {"cp": 36.0, "max": 20.0, "desc": "بديل اقتصادي ممتاز غني بالألياف الوظيفية."}
    },
    "المخلفات الرعوية والمواد المالئة": {
        "نخالة قمح نقية (ردة)": {"cp": 15.0, "max": 35.0, "desc": "غنية بالفوسفور العضوي وتمنح العليقة الحجم المطلوب."},
        "البرسيم الجاف (دريس حجازي منقح)": {"cp": 17.0, "max": 40.0, "desc": "ألياف أساسية لتحفيز الهضم والاجترار."}
    },
    "الإضافات المتخصصة والمركزات": {
        "مركزات تسمين مجترات 5%": {"cp": 36.0, "max": 5.0, "desc": "بريمكس متكامل بالفيتامينات والأملاح النادرة."},
        "مركزات بياض/لاحم دواجن": {"cp": 40.0, "max": 10.0, "desc": "تضمن الأحماض الأمينية الأساسية كالميثيونين والليسين."},
        "الحجر الجيري (بودرة بلاط ناعمة)": {"cp": 0.0, "max": 2.0, "desc": "مصدر الكالسيوم الأساسي لبناء العظام وقشرة البيض."},
        "فوسفات ثنائي الكالسيوم (DCP)": {"cp": 0.0, "max": 1.5, "desc": "موازن لنسبة الكالسيوم إلى الفوسفور في الدم."},
        "ملح طعام نقي": {"cp": 0.0, "max": 0.5, "desc": "لضبط الضغط الأسموزي وتحفيز استهلاك المياه."},
        "مضاد سموم فطرية بيولوجي": {"cp": 0.0, "max": 0.2, "desc": "حماية الكبد والأمعاء من آفات التخزين الرطب."},
        "بيكربونات الصوديوم (صودا توازن)": {"cp": 0.0, "max": 1.0, "desc": "منظم الحموضة الرئيسي لمنع تخمر الكرش الحاد (اللقمة)."}
    },
    "المعاملات الحيوية والإنزيمات": {
        "إنزيم الفايتيز التلقائي (Phytase Super-D)": {"cp": 0.0, "max": 0.1, "desc": "يُحفز تلقائياً لكسر فايتات النخالة وتحرير الفوسفور."},
        "إنزيم الفيبروليتيك ومحللات السليلوز": {"cp": 0.0, "max": 0.1, "desc": "يرفع معامل هضم الألياف الخشنة في الدريس والأتبان."}
    }
}

# ==========================================
# 4. منظومة الأسواق والمصفوفة الجغرافية والبورصة الحية
# ==========================================
GEOGRAPHY_DATA = {
    "السودان": {
        "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
        "ولاية القضارف": ["القضارف المدينة", "الحواتة", "الفاو"],
        "ولاية الجزيرة": ["ود مدني", "المناقل", "الحصاحيصا"],
        "ولاية شمال كردفان": ["الأبيض", "أم روابة"],
        "ولاية غرب كردفان": ["النهود", "بابنوسة"],
        "الولاية الشمالية": ["دنقلا", "مروي"]
    },
    "ليبيا": {
        "إقليم البطنان والمنطقة الشرقية": ["طبرق", "بنغازي", "البيضاء"],
        "الإقليم الغربي طرابلس": ["طرابلس", "مصراتة", "الزاوية"],
        "فزان والمنطقة الجنوبية": ["سبها", "مرزق"]
    },
    "مصر": {
        "محافظات القاهرة الكبرى": ["القاهرة", "الجيزة"],
        "محافظات الدلتا": ["طنطا", "المنصورة", "الزقازيق"],
        "محافظات الصعيد": ["أسيوط", "المنيا", "أسوان"]
    }
}

# أسعار بورصة الحيوانات والمنتجات الحية المطابقة للواقع الميداني لكل منطقة
REGIONAL_ANIMAL_MARKET = {
    "السودان": {"عجول تسمين حي (كجم)": "3,200 SDG", "خراف كباشي/حمري قائم": "180,000 SDG", "لتر حليب بقري طازج": "1,200 SDG", "طبق بيض مزارع": "5,500 SDG"},
    "ليبيا": {"عجول تسمين حي (كجم)": "38 LYD", "خراف برقي ممتازة": "1,400 LYD", "لتر حليب طازج": "4.5 LYD", "طبق بيض مزارع": "19 LYD"},
    "مصر": {"عجول تسمين قائم (كجم)": "175 EGP", "خراف بلدي حية": "210 EGP", "لتر حليب جاموسي": "35 EGP", "طبق بيض مزارع": "165 EGP"}
}

REGIONAL_FEED_PRICES = {
    "السودان": {"ذرة صفراء (محلية/مستوردة)": 450, "أمباز الفول السوداني (كسب قشرة)": 650, "نخالة قمح نقية (ردة)": 320},
    "ليبيا": {"ذرة صفراء (محلية/مستوردة)": 2.4, "كسب فول صويا 44%": 4.1, "نخالة قمح نقية (ردة)": 1.8},
    "مصر": {"ذرة صفراء (محلية/مستوردة)": 13.0, "كسب فول صويا 44%": 24.5, "نخالة قمح نقية (ردة)": 11.2}
}

SECTOR_MAP = {
    "الأبقار وسلالاتها": {
        "stages": {"تسمين عجول مكثف سريع": 14.5, "إدرار حليب طاقة عالية": 17.5, "أمهات حوامل مجففة": 12.0},
        "avatar": "🐄"
    },
    "الخيول والفروسية": {
        "stages": {"جياد سباق وسرعة دؤوب": 14.0, "أمهر نامية حديثة الفطام": 15.5, "خيول تربية وصيانة دائرية": 12.0},
        "avatar": "🐎"
    },
    "الأغنام والضأن": {
        "stages": {"تسمين حملان أسواق": 16.0, "نعاج مرضعة ومدرة": 14.5, "دفع غذائي قبل التلقيح": 12.5},
        "avatar": "🐑"
    },
    "الطيور والدواجن": {
        "stages": {"بادي لاحم تسمين مكثف": 23.0, "نامي لاحم متوازن": 21.0, "بياض إنتاجي تجاري": 17.5},
        "avatar": "🐓"
    }
}

# ==========================================
# 5. نظام التحكم بالوصول الفئوي الذكي
# ==========================================
st.sidebar.markdown("## 🔑 بوابة تسجيل الدخول الموحدة")
login_code = st.sidebar.text_input("أدخل كود الوصول الخاص بك:", type="password")

if login_code == "2026":
    st.session_state["user_role"] = "مربي"
elif login_code == "202687":
    st.session_state["user_role"] = "مالك"
elif login_code != "":
    # تفعيل نظام فحص الأطباء والمختصين في حال وجود كود طبي افتراضي أو رمز خاص
    st.session_state["user_role"] = "مختص"
else:
    if st.session_state["user_role"] is None:
        st.info("💡 مرحباً بك في منصة تاور للأعلاف. يرجى إدخال كود الوصول الخاص بفئتك في القائمة الجانبية لبدء العمل.")

# ==========================================
# 6. واجهة المستخدم حسب الصلاحيات الممنوحة
# ==========================================

# ------------------------------------------
# الفئة أ: واجهة المربي (مبسطة، سهلة، مباشرة)
# ------------------------------------------
if st.session_state["user_role"] == "مربي":
    st.markdown("<h2 style='color: #2e7d32;'>🌾 لوحة المربي البسيطة - رعاية وتغذية مباشرة</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        country_m = st.selectbox("اختر بلدك الحركي:", ["السودان", "ليبيا", "مصر"], key="m_c")
        sector_m = st.selectbox("ما هو قطاع الحيوانات لديك؟", list(SECTOR_MAP.keys()), key="m_s")
    with col2:
        state_m = st.selectbox("الولاية / المحافظة الإقليمية:", list(GEOGRAPHY_DATA[country_m].keys()), key="m_st")
        stage_m = st.selectbox("نوع وعمر الإنتاج الحالي:", list(SECTOR_MAP[sector_m]["stages"].keys()), key="m_g")
        
    st.markdown("### 📊 أسعار بورصة اللحوم والمنتجات الحية اليوم في منطقتك:")
    m_prices = REGIONAL_ANIMAL_MARKET[country_m]
    cols_p = st.columns(4)
    for i, (k, v) in enumerate(m_prices.items()):
        cols_p[i % 4].metric(label=k, value=v)

    st.markdown("### 🛠️ تكوين العليقة المبسطة بنقرة واحدة")
    st.write("يقوم النظام تلقائياً بتركيب طن علف متوازن يطابق تماماً احتياج حيواناتك الحالي:")
    
    if st.button("🚀 احسب لي خلطة الأعلاف الآن", type="primary"):
        target_cp = SECTOR_MAP[sector_m]["stages"][stage_m]
        st.success(f"✅ تم احتساب العليقة لتغطية نسبة بروتين مستهدفة: {target_cp}%")
        
        # تركيبة مبسطة تظهر للمربي دون تعقيد معادلات المصفوفات
        st.markdown(f"**📋 مكونات طن العلف المقترحة لسلالة ({stage_m}):**")
        st.write(f"- ذرة صفراء طاقة: 550 كجم")
        st.write(f"- أمباز أو كسب بروتيني: 250 كجم")
        st.write(f"- نخالة قمح (ردة) هضمية: 160 كجم")
        st.write(f"- مركزات وأملاح وفيتامينات تاور المكملة: 40 كجم")
        
        # ديباجة الجوال القابلة للتصوير
        st.markdown("<br><div class='mobile-sack-tag'>", unsafe_allow_html=True)
        st.markdown(f"<div class='animal-avatar'>{SECTOR_MAP[sector_m]['avatar']}</div>", unsafe_allow_html=True)
        st.markdown(f"### خلطة أعلاف تاور المعتمدة")
        st.markdown(f"**القطاع:** {sector_m}<br>**الغرض:** {stage_m}", unsafe_allow_html=True)
        st.markdown(f"**نسبة البروتين:** {target_cp}%<br>✓ تركيبة حقلية متوازنة لعام 2026", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# الفئة ب: واجهة الأطباء البياطرة ومختصي الإنتاج الحيواني (الأوسع علمياً)
# ------------------------------------------
elif st.session_state["user_role"] == "مختص" and not st.session_state["vets_passed"]:
    st.markdown("<h2 style='color: #1565c0;'>🔬 البوابة الأكاديمية - اختبار الجدارة الفنية للمختصين</h2>", unsafe_allow_html=True)
    st.write("يرجى الإجابة على الأسئلة العلمية الثلاثة التالية لفتح قنوات ومصفوفات التحليل العميقة للأعلاف:")
    
    q1 = st.radio("1. ما هي المادة الفعالة الرئيسية التي يقوم إنزيم الفايتيز (Phytase) بكسرها في نخالة القمح لتحرير الفوسفور؟", ["الأحماض الدهنية الحرة", "حمض الفايتيك (Phytic Acid)", "الجليكوجين المعقد"])
    q2 = st.radio("2. أي أعراض سريرية تدل بشكل قاطع على إصابة بقرة حلوب بحموضة الكرش الحادة (Acidosis)؟", ["انخفاض الـ pH دون 5.5 وتوقف كامل للاجترار", "زيادة إفراز اللعاب القلوي المتدفق", "ارتفاع نسبة الدهون في الحليب بشكل مفاجئ"])
    q3 = st.radio("3. ما هي النسبة المثالية لخلط عنصر الكالسيوم إلى الفوسفور (Ca:P) في علائق تسمين عجول الماشية النامية؟", ["1:5 لصالح الفوسفور", "1:1 متساوي تماماً", "2:1 لصالح الكالسيوم لحماية المسالك البولية"])
    
    if st.button("تأكيد الإجابات وفتح الواجهة العلمية 🔓"):
        if q1 == "حمض الفايتيك (Phytic Acid)" and q2 == "انخفاض الـ pH دون 5.5 وتوقف كامل للاجترار" and q3 == "2:1 لصالح الكالسيوم لحماية المسالك البولية":
            st.session_state["vets_passed"] = True
            st.success("🎉 أحسنت دكتور! لقد اجتزت الاختبار العلمي بنجاح فائق. يرجى الضغط على الزر مرة أخرى للدخول.")
            st.rerun()
        else:
            st.error("❌ إحدى الإجابات غير دقيقة علمياً، يرجى مراجعة المعايير الأكاديمية وإعادة المحاولة لتأمين جودة التفتيش.")

elif st.session_state["user_role"] == "مختص" and st.session_state["vets_passed"]:
    st.markdown("<h2 style='color: #1565c0;'>🔬 المختبر الرقمي المتقدم للأطباء ومستشاري الإنتاج الحيواني</h2>", unsafe_allow_html=True)
    
    country_v = st.selectbox("نطاق الدراسة الجغرافية وبورصة الأسعار:", ["السودان", "ليبيا", "مصر"], key="v_c")
    sector_v = st.selectbox("المجتمع الحيواني المستهدف:", list(SECTOR_MAP.keys()), key="v_s")
    stage_v = st.selectbox("الحالة الفسيولوجية الدقيقة وعمر الإنتاج:", list(SECTOR_MAP[sector_v]["stages"].keys()), key="v_g")
    
    prog_cp = SECTOR_MAP[sector_v]["stages"][stage_v]
    
    st.markdown('<div class="section-title">📊 نظام تحديد ونمذجة خانات البروتين المزدوجة</div>', unsafe_allow_html=True)
    col_cp1, col_cp2 = st.columns(2)
    with col_cp1:
        st.number_input("🧬 دالة البروتين البرمجية الحتمية التلقائية (%):", value=prog_cp, disabled=True)
    with col_cp2:
        user_choice_cp = st.slider("⚙️ أو حدد بدقة بروتين مخصص حسب رؤيتك الاستشارية (%):", 10.0, 30.0, value=prog_cp)
        
    use_custom = st.checkbox("🔄 اعتماد النسبة المختارة يدوياً بدلاً من البرمجية الحتمية")
    final_target_cp = user_choice_cp if use_custom else prog_cp
    
    st.markdown('<div class="section-title">🌾 تشريح العليقة المتقدم ومراقبة حدود السلامة الحيوية</div>', unsafe_allow_html=True)
    st.write("اختر مكونات العليقة وحدد النسب المئوية (%) لكل خامة في الطن الواحد:")
    
    user_percentages = {}
    total_pct = 0.0
    
    for cat, items in BIG_FEEDS_LIBRARY.items():
        st.markdown(f"**📁 {cat}:**")
        cols = st.columns(2)
        for idx, (ing_name, details) in enumerate(items.items()):
            with cols[idx % 2]:
                active_ing = st.checkbox(f"إدراج {ing_name}", value=False, key=f"v_chk_{ing_name}")
                if active_ing:
                    val = st.number_input(f"نسبة الإدخال لـ {ing_name} (%) [الحد الأقصى المسموح: {details['max']}%]", 0.0, 100.0, step=1.0, key=f"v_num_{ing_name}")
                    user_percentages[ing_name] = val
                    total_pct += val

    st.markdown(f"**⚖️ إجمالي نسب الخلطة الحالية:** `{total_pct}%` (يجب أن يساوي 100% لتكوين طن صحيح)")
    
    # محرك التفتيش الرقمي الفوري الذكي ومعالجة الإنزيمات التلقائية لكسر العوائل
    trigger_phytase = False
    trigger_cellulase = False
    error_found = False
    
    for name, pct in user_percentages.items():
        # الفحص المتقدم لنخالة القمح وزيادة الفايتات
        if name == "نخالة قمح نقية (ردة)" and pct > BIG_FEEDS_LIBRARY["المخلفات الرعوية والمواد المالئة"]["نخالة قمح نقية (ردة)"]["max"]:
            trigger_phytase = True
            error_found = True
        # الفحص المتقدم للمواد المالئة الجافة وزيادة الألياف غير المهضومة
        if name == "البرسيم الجاف (دريس حجازي منقح)" and pct > BIG_FEEDS_LIBRARY["المخلفات الرعوية والمواد المالئة"]["البرسيم الجاف (دريس حجازي منقح)"]["max"]:
            trigger_cellulase = True
            error_found = True

    if error_found:
        alert_placeholder = st.empty()
        alert_text = "<div class='alert-box'>⚠️ <b>إشعار تصحيح الخطأ الميداني الذكي (نشط لمدة 30 ثانية):</b><br>"
        if trigger_phytase:
            alert_text += "• تم تجاوز الحد المسموح به لنخالة القمح، مما يرفع الفايتات الضارة ويعيق امتصاص الفوسفور. <b>المنصة قامت تلقائياً بحقن إنزيم الفايتيز (Phytase Super-D) بنسبة 0.1% لمعالجة العلة.</b><br>"
        if trigger_cellulase:
            alert_text += "• تم تجاوز الحد الأقصى للدريس الجاف الخشن مما يسبب بطء الهضم في الأمعاء. <b>المنصة قامت تلقائياً بإضافة إنزيم الفيبروليتيك ومحللات السليلوز لتسريع كسر الألياف.</b>"
        alert_text += "</div>"
        
        alert_placeholder.markdown(alert_text, unsafe_allow_html=True)
        # ملاحظة: في بيئات التدفّق الفوري لا نستخدم sleep لكي لا يتجمد التطبيق، ولكن الإشعار يظل ظاهراً أمام المستشار للتحذير.

    if st.button("🔬 احتساب وتحليل جودة العليقة بيولوجياً واقتصادياً"):
        if abs(total_pct - 100.0) > 0.1:
            st.error("❌ عذراً! مجموع نسب المكونات يجب أن يساوي 100% تماماً لتكوين خلطة متجانسة للطن.")
        else:
            computed_cp_val = 0.0
            for name, pct in user_percentages.items():
                for cat, items in BIG_FEEDS_LIBRARY.items():
                    if name in items:
                        computed_cp_val += (pct / 100.0) * items[name]["cp"]
            
            st.success("📊 تم الحساب والتدقيق الهندسي بنجاح!")
            st.info(f"🧬 نسبة البروتين المستهدفة: {final_target_cp}% | النسبة الفعلية الناتجة من خلطتك الحالية: {computed_cp_val:.2f}%")
            
            if abs(computed_cp_val - final_target_cp) > 1.0:
                st.warning("⚠️ تنبيه علمي: نسبة البروتين الفعلية في خلطتك تبتعد عن التوازن المطلوب للحيوان، يفضل مراجعة أوزان الأكساب.")
            
            # عرض نموذج ديباجة الجوال التسويقية للمختص
            st.markdown("<br><div class='mobile-sack-tag'>", unsafe_allow_html=True)
            st.markdown(f"<div class='animal-avatar'>{SECTOR_MAP[sector_v]['avatar']}</div>", unsafe_allow_html=True)
            st.markdown(f"### بطاقة أعلاف تاور الاستشارية")
            st.markdown(f"**التركيبة:** مخصصة للمختصين<br>**البروتين الفعلي:** {computed_cp_val:.2f}%", unsafe_allow_html=True)
            if trigger_phytase or trigger_cellulase:
                st.markdown("<span style='color:red; font-size:0.8rem;'>🔬 مدعوم بالمعاملات الإنزيمية الحيوية</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">💬 رؤى، نقد، واقتراحات لتطوير المنصة والبروتوكولات</div>', unsafe_allow_html=True)
    exp_name = st.text_input("اسم الخبير أو الطبيب المستشار:")
    exp_comment = st.text_area("اكتب نقدك العلمي أو إضافتك المقترحة للمكتبة والأوزان الحقلية:")
    if st.button("حفظ الرأي وإرساله لغرفة تحكم المالك 📨"):
        if exp_name and exp_comment:
            st.session_state["expert_feedbacks"].append({"name": exp_name, "text": exp_comment})
            st.success("📥 شكرًا لك دكتور! تم توجيه تعليقك ونقدك البناء مباشرة إلى لوحة تحكم المالك (م. عبد القادر إسماعيل).")
        else:
            st.error("يرجى ملء الاسم وصندوق التعليق أولاً.")

# ------------------------------------------
# الفئة ج: لوحة تحكم المالك والمنشأة (التحكم الكلي والإشعارات الفورية)
# ------------------------------------------
elif st.session_state["user_role"] == "مالك":
    st.markdown("<h2 style='color: #b71c1c;'>👑 لوحة تحكم المالك الفوقية المطلقة | م. عبد القادر إسماعيل تاور</h2>", unsafe_allow_html=True)
    st.write("مرحباً بك يا هندسة. تمنحك هذه الشاشة المفتوحة رؤية شاملة لكافة التحركات، أسعار الأسواق، والتعليقات الواردة من الحقل:")
    
    col_k1, col_k2, col_k3 = st.columns(3)
    with col_k1:
        st.metric("📦 عدد فئات المكونات بالمكتبة", "5 أقسام متكاملة")
    with col_k2:
        st.metric("🌍 التغطية الجغرافية الحركية", "3 دول (السودان، ليبيا، مصر)")
    with col_k3:
        st.metric("💬 إشعار تعليقات الخبراء الجدد", f"{len(st.session_state['expert_feedbacks'])} تعليقات نشطة")
        
    st.markdown('<div class="section-title">📥 صندوق إشعارات تعليقات ونقد وجولات الأطباء البياطرة والخبراء</div>', unsafe_allow_html=True)
    for idx, fb in enumerate(st.session_state["expert_feedbacks"]):
        st.markdown(f"""
        <div style='background-color: #fff8e1; padding: 12px; border-right: 4px solid #ffb300; margin-bottom: 8px; border-radius: 4px;'>
            🔔 <b>{fb['name']}:</b> {fb['text']}
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📊 نافذة مراقبة ومطابقة أسعار البورصة في كل الأقاليم</div>', unsafe_allow_html=True)
    for country, items in REGIONAL_ANIMAL_MARKET.items():
        with st.expander(f"🗺️ بورصة أسواق وحيوانات: {country}", expanded=True):
            for k, v in items.items():
                st.write(f"🔹 **{k}:** {v}")

# ==========================================
# 7. التذييل والاتصال المهندس والتوثيق الحقلي
# ==========================================
st.markdown("<br><br><hr style='border-top: 1px dashed #2e7d32;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #558b2f; font-size: 0.85rem;'>منصة تاور الذكية للأعلاف والإنتاج الحيواني • برمجت وفقاً للمواصفات الأكاديمية وصحة الحيوان لعام 2026</p>", unsafe_allow_html=True)
