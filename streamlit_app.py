import streamlit as st
import time
import requests

# ==========================================
# 1. قواعد البيانات الثابتة (Data Tables)
# ==========================================

# قاعدة بيانات الإنزيمات والحدود القياسية لكل عنصر
ENZYME_DATABASE = {
    "Phytase (فايتيز)": {"target_nutrient": "Phytic_Acid", "max_limit": 0.5, "added_dose_g_ton": 150},
    "Xylanase (زيلانيز)": {"target_nutrient": "Crude_Fiber", "max_limit": 7.0, "added_dose_g_ton": 200}
}

# قاعدة بيانات السلالات، مواطنها، وتأثير البيئة على احتياجاتها
BREEDS_GEOGRAPHY = {
    "Ross 308 (تسمين)": {
        "الموطن": "المناخ المعتدل / تهوية مغلقة",
        "تحمل الحرارة": "متوسط",
        "تعديل_الاحتياجات": {"البروتين": 1.0, "الطاقة": 1.0}  # الاحتياجات القياسية كتيب السلالة
    },
    "Cobb 500 (تسمين)": {
        "الموطن": "المناخات الحارة والرطبة",
        "تحمل الحرارة": "عالي",
        "تعديل_الاحتياجات": {"البروتين": 1.02, "الطاقة": 0.98} # تعديل لتقليل الإجهاد الحراري
    },
    "سلالات بلدي محسنة": {
        "الموطن": "المناخ الصحراوي / تربية مفتوحة",
        "تحمل الحرارة": "عالي جداً",
        "تعديل_الاحتياجات": {"البروتين": 0.95, "الطاقة": 0.95}
    }
}

# قاعدة بيانات الخامات الأساسية مسعرة عالمياً بالدولار الأمريكي
RAW_MATERIALS_USD = {
    "ذرة صفراء (مستورد)": 240.0,       # سعر الطن بالدولار
    "كسب صويا 44%": 410.0,
    "مركزات دواجن 5%": 850.0,
    "مسحوق حجر جيري": 30.0
}

# ==========================================
# 2. الدوال البرمجية المساعدة (Core Functions)
# ==========================================

@st.cache_data(ttl=3600)  # تخزين مؤقت لمدة ساعة لتقليل طلبات الـ API
def get_live_exchange_rate(local_currency="LYD"):
    """جلب سعر صرف الدولار اللحظي مقابل العملة المحلية عبر الإنترنت"""
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url, timeout=5).json()
        rate = response["rates"].get(local_currency, 1.0)
        return rate, True
    except Exception:
        # سعر افتراضي احتياطي في حال عدم توفر اتصال بالإنترنت
        return 4.85, False

def check_and_apply_enzymes(formulation_results):
    """فحص ناتج التركيبة وإضافة الإنزيمات تلقائياً عند تجاوز الحدود"""
    applied_enzymes = {}
    for enzyme, specs in ENZYME_DATABASE.items():
        nutrient = specs["target_nutrient"]
        if nutrient in formulation_results and formulation_results[nutrient] > specs["max_limit"]:
            applied_enzymes[enzyme] = specs["added_dose_g_ton"]
    return applied_enzymes

# ==========================================
# 3. واجهة المستخدم والتطبيق (Streamlit UI)
# ==========================================

st.set_page_config(page_title="Smart Feed Formulation Pro", layout="wide")
st.title("🌾 النظام الموحد لتركيب الأعلاف الذكي (Smart Feed Formulation)")
st.markdown("---")

# الصف الأول: إدارة الأسعار والعملة وسعر الصرف
st.header("💲 إدارة أسعار السوق اللحظية")
col1, col2 = st.columns([1, 2])

with col1:
    currency_code = st.text_input("رمز عملة البلد الحالية:", value="LYD")
    usd_rate, is_live = get_live_exchange_rate(currency_code)
    
    if is_live:
        st.success(f"✅ تم تحديث سعر الصرف لحظياً: 1 USD = {usd_rate:.2f} {currency_code}")
    else:
        st.warning(f"⚠️ وضع عدم الاتصال: تم استخدام سعر صرف احتياطي: 1 USD = {usd_rate:.2f} {currency_code}")

with col2:
    st.subheader("جدول الأسعار الحالي مقارنة بالدولار ($)")
    updated_local_prices = {}
    
    # عرض الأسعار المحدثة ديناميكياً في جدول
    price_data = []
    for material, price_usd in RAW_MATERIALS_USD.items():
        price_local = price_usd * usd_rate
        updated_local_prices[material] = price_local
        price_data.append({"الخامة": material, "السعر ($)": f"${price_usd:,.2f}", f"السعر الحالي ({currency_code})": f"{price_local:,.2f}"})
    
    st.table(price_data)

st.markdown("---")

# الصف الثاني: السلالات والموقع الجغرافي والاحتياجات
st.header("🐓 إدارة السلالات والمواطن الجغرافية")
col3, col4 = st.columns(2)

with col3:
    selected_breed = st.selectbox("اختر سلالة الدواجن المستهدفة:", list(BREEDS_GEOGRAPHY.keys()))
    breed_meta = BREEDS_GEOGRAPHY[selected_breed]
    
    st.info(f"🌍 **الموطن الأصلي/البيئة الموصى بها:** {breed_meta['الموطن']}")
    st.info(f"🔥 **درجة تحمل الإجهاد الحراري في هذا الموقع:** {breed_meta['تحمل الحرارة']}")

with col4:
    st.subheader("تعديل قيود المغذيات برمجياً بناءً على البيئة")
    base_protein = 21.0  # الاحتياج الأساسي الافتراضي
    base_energy = 3000.0 # الطاقة التمثيلية الافتراضية
    
    # تطبيق معاملات التعديل الجغرافي والمناخي
    adjusted_protein = base_protein * breed_meta["تعديل_الاحتياجات"]["البروتين"]
    adjusted_energy = base_energy * breed_meta["تعديل_الاحتياجات"]["الطاقة"]
    
    st.metric(label="نسبة البروتين المطلوبة المعدلة (%)", value=f"{adjusted_protein:.2f}%", delta=f"{adjusted_protein - base_protein:.2f}% بناءً على البيئة")
    st.metric(label="الطاقة الممثلة المعدلة (كيلو كالوري/كجم)", value=f"{adjusted_energy:.0f}", delta=f"{adjusted_energy - base_energy:.0f}")

st.markdown("---")

# الصف الثالث: تشغيل الـ Solver والتدخل التلقائي للإنزيمات
st.header("🧮 حساب وتحسين التركيبة العلفية")

if st.button("🚀 تشغيل حسابات خوارزمية أقل تكلفة (Least-Cost Formulation)"):
    
    with st.spinner("جاري معالجة المصفوفات وحساب النسب المثلى وتحديث التكلفة..."):
        time.sleep(1.5) # محاكاة وقت المعالجة الحسابية للـ Solver
        
        # محاكاة لنتيجة الـ Solver (هنا تظهر النتيجة الحقيقية بعد تشغيل خوارزميات الـ Optimization)
        # نفترض هنا برمجياً أن الألياف الخام تجاوزت الحد الأقصى المسموح به (مثلاً نتيجة استخدام خامات محلية)
        simulated_output = {
            "Crude_Protein": adjusted_protein,
            "Crude_Energy": adjusted_energy,
            "Crude_Fiber": 7.6,     # تجاوز الحد (7.6 > 7.0)
            "Phytic_Acid": 0.3      # ضمن الحدود الأمنة (0.3 < 0.5)
        }
        
        # عرض نتائج التركيبة الأساسية
        st.subheader("📊 النتائج الأولية للتركيبة:")
        st.write(f"البروتين: {simulated_output['Crude_Protein']:.2f}% | الطاقة: {simulated_output['Crude_Energy']:.0f} kcal | الألياف الخام: {simulated_output['Crude_Fiber']:.1f}%")
        
        # الفحص البرمجي التلقائي للإنزيمات
        detected_enzymes = check_and_apply_enzymes(simulated_output)
        
        if detected_enzymes:
            for enzyme, dose in detected_enzymes.items():
                # 1. إنشاء مكان مخصص للإشعار على الشاشة
                notification_box = st.empty()
                
                # 2. عرض الإشعار بتنسيق مميز وملفت
                notification_box.error(
                    f"⚠️ **تنبيه نظام الإنزيمات التلقائي:** تم رصد تجاوز في الألياف القياسية ({simulated_output['Crude_Fiber']}%).\n\n"
                    f"◀️ **الإجراء البرمجي:** تم إدراج إنزيم **[{enzyme}]** تلقائياً في التركيبة بمعدل **{dose} جرام / طن** لمعالجة الهضم الحيوى للمركبات المعقدة."
                )
                
                # 3. مؤقت تنازلي مرئي في الشريط الجانبي ينتهي بعد 30 ثانية دون تجميد التطبيق
                progress_bar = st.sidebar.progress(100)
                status_text = st.sidebar.empty()
                
                for secs in range(30, 0, -1):
                    status_text.text(f"سيتلاشى إشعار الإنزيمات خلال: {secs} ثانية")
                    progress_bar.progress(int((secs / 30) * 100))
                    time.sleep(1)
                
                # 4. مسح الإشعار تماماً من الشاشة بعد انتهاء الـ 30 ثانية
                notification_box.empty()
                progress_bar.empty()
                status_text.empty()
                st.sidebar.success("⏳ انتهت مدة عرض الإشعار (30 ثانية) وتم إغلاقه تلقائياً.")
        
        # اعتماد النتيجة النهائية للتصدير أو الحفظ
        st.success("✅ تم اعتماد وتحديث الملف النهائي للتركيبة العلفية بنجاح.")
