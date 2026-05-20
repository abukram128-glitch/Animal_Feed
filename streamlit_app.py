import streamlit as st
import numpy as np

# إعدادات الصفحة العامة
st.set_page_config(page_title="منصة تاور الذكية لخدمات الثروة الحيوانية", layout="wide", initial_sidebar_state="expanded")

# تطبيق نمط مخصص للغة العربية والتنسيق الجمالي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stSidebar"], .stMarkdown, h1, h2, h3, h4, h5, h6, label, input, button, select {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
    .stAlert p { text-align: right !important; }
    .metric-box {
        background-color: #f8f9fa;
        border-right: 5px solid #2e7d32;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .metric-title { font-size: 14px; color: #555; font-weight: bold; }
    .metric-value { font-size: 24px; color: #2e7d32; font-weight: bold; }
    </style>
""", unsafe_index=True)

# --- قاعدة بيانات الأنواع والسلالات وأنواع الإنتاج ---
ANIMAL_DB = {
    "الخيل": {
        "السلالات": ["الخيول العربية الأصيلة", "الخيل الإنجليزي (Thoroughbred)", "خيل الجر الثقيل (Draft)", "المحلي المختلط"],
        "الإنتاج": ["حفظ حياة (Maintenance)", "عمل خفيف", "عمل شاق ومجهد", "التكاثر وإنتاج المهور"],
        "العامل": 11880
    },
    "الأبقار (المجترات الكبرى)": {
        "السلالات": ["هولشتاين - فريديان (Holstein)", "جيرسي (Jersey)", "السلالات المحلية (الليبي/البلدي)", "مستورد للتسمين (سيمنتال/ليموزين)"],
        "الإنتاج": ["إنتاج حليب مرتفع (>25 لتر)", "إنتاج حليب متوسط (15-25 لتر)", "تسمين وإنتاج لحم سريع", "حفظ حياة وحمل جاف"],
        "العامل": 10800
    },
    "الأغنام والماعز (المجترات الصغرى)": {
        "السلالات": ["الأغنام البرقية", "الأغنام العواسية", "الماعز المحلي/الدمشقي", "سلالات مهجنة"],
        "الإنتاج": ["تسمين وإنتاج لحم نمو سريع", "إدرار حليب", "حفظ حياة وإنتاج صوف/شعر", "حمل وتكاثر (نعاج متقدمة)"],
        "العامل": 11400
    }
}

# --- إدارة الحالة الأمنية عبر الجلسة (Session State) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'quiz_passed' not in st.session_state:
    st.session_state.quiz_passed = False

# --- الواجهة الرئيسية للبرنامج ---
st.title("🐴 منصة تاور الذكية لتقدير الأوزان والتركيب الغذائي 🌾")
st.subheader("النظام البرمجي المتكامل تحت إشراف أ. عبدالقادر إسماعيل")

# القائمة الجانبية: نظام تسجيل الدخول والأكواد
st.sidebar.header("🔐 بوابة التحقق والأكواد الإضافية")
role_selection = st.sidebar.selectbox("اختر فئة المستخدم:", ["اختر الفئة...", "المالك (تاور)", "المربي", "الزملاء المختصين (أطباء بياطرة / إنتاج حيواني)"])

# دالة إعادة ضبط الحالة عند تغيير الفئة
def reset_auth():
    st.session_state.authenticated = False
    st.session_state.quiz_passed = False

if role_selection == "المالك (تاور)":
    code_input = st.sidebar.text_input("أدخل كود المالك الحصري:", type="password")
    if st.sidebar.button("تحقق من الكود"):
        if code_input == "202687":
            st.session_state.authenticated = True
            st.session_state.user_role = "المالك"
            st.sidebar.success("مرحباً بك يا سيد تاور. تم فتح الصلاحيات الكاملة.")
        else:
            st.sidebar.error("كود المالك غير صحيح!")

elif role_selection == "المربي":
    code_input = st.sidebar.text_input("أدخل كود المربي:", type="password")
    if st.sidebar.button("تحقق من الكود"):
        if code_input == "2026":
            st.session_state.authenticated = True
            st.session_state.user_role = "المربي"
            st.sidebar.success("تم تفعيل بوابة المربي بنجاح.")
        else:
            st.sidebar.error("كود المربي غير صحيح!")

elif role_selection == "الزملاء المختصين (أطباء بياطرة / إنتاج حيواني)":
    code_input = st.sidebar.text_input("أدخل كود المختصين الأطباء:", type="password")
    if code_input == "2020":
        st.sidebar.info("💡 الكود صحيح. يرجى الإجابة على الأسئلة العلمية الثلاثة أدناه لتأكيد الهوية:")
        
        # أسئلة اختبار الهوية للمختصين
        q1 = st.sidebar.radio("س1: ما هو العضو المستهدف الرئيسي لفيروس مرض الجمبورو (Gumboro) في الدواجن؟", 
                              ["اختر الإجابة...", "غدة فابريشيوس (Bursa of Fabricius)", "الكبد والأمعاء", "الرئتين والأكياس الهوائية"])
        q2 = st.sidebar.radio("س2: أي من الأحماض الدهنية الطيارة (VFA) يعتبر السلف الأساسي لتخليق دهن الحليب في الكرش؟", 
                              ["اختر الإجابة...", "حمض البروبيونيك", "حمض الأسيتيك (الخلات)", "حمض البيوتيريك"])
        q3 = st.sidebar.radio("س3: ما هي النسبة المثالية لـ الكالسيوم إلى الفوسفور (Ca:P) في علائق المجترات البالغة لمنع حصوات البول؟", 
                              ["اختر الإجابة...", "1:1", "1:4", "2:1"])
        
        if st.sidebar.button("تأكيد إجابات الاختبار"):
            if q1 == "غدة فابريشيوس (Bursa of Fabricius)" and q2 == "حمض الأسيتيك (الخلات)" and q3 == "2:1":
                st.session_state.authenticated = True
                st.session_state.quiz_passed = True
                st.session_state.user_role = "المختصين"
                st.sidebar.success("🟢 أحسنت! تم تأكيد الهوية المهنية بنجاح وفتحت الصلاحيات.")
            else:
                st.sidebar.error("❌ إحدى الإجابات أو أكثر خاطئة. يرجى مراجعة معلوماتك المهنية وإعادة المحاولة.")
    elif code_input != "":
        st.sidebar.error("كود المختصين غير صحيح!")

# --- محتوى المنصة الرئيسي (يفتح فقط بعد تخطي بوابات التحقق بنجاح) ---
if st.session_state.authenticated:
    st.success(f"🔓 تم تسجيل الدخول بنجاح بصلاحية: **{st.session_state.user_role}**")
    
    col_input, col_view = st.columns([1, 1])
    
    with col_input:
        st.header("📋 مدخلات قياس وتصنيف الحيوان")
        
        # اختيار الفصيلة، السلالة، والإنتاج
        animal_type = st.selectbox("اختر نوع الحيوان المطلوب فصحه:", list(ANIMAL_DB.keys()))
        breed_type = st.selectbox("اختر السلالة الفرعية:", ANIMAL_DB[animal_type]["السلالات"])
        production_type = st.selectbox("حدد نوع خط الإنتاج الحالي:", ANIMAL_DB[animal_type]["الإنتاج"])
        
        st.divider()
        st.subheader("📏 شريط التقدير الرقمي للأبعاد حيوياً")
        
        # منزلقات قياس أبعاد الجسم بالسنتيمتر
        heart_girth = st.slider("1. محيط الصدر (Heart Girth) بالسنتيمتر:", min_value=40, max_value=300, value=160, step=1)
        body_length = st.slider("2. طول الجسم (Body Length) بالسنتيمتر:", min_value=40, max_value=250, value=140, step=1)
        
    with col_view:
        st.header("🖼️ مخطط توجيه القياس الفني للحيوان")
        st.info(f"يرجى اتباع الخطوط الموضحة أدناه لقياس **{animal_type}** بدقة:")
        
        # رسم ديناميكي لخطوط القياس باستخدام SVG بناءً على نوع الحيوان المتغير لضمان تفاعلية الشريط
        if "الخيل" in animal_type:
            svg_code = """
            <svg width="100%" height="250" viewBox="0 0 400 250" style="background-color:#ffffff; border:1px solid #ddd; border-radius:8px;">
                <!-- رسم مبسط للخيل -->
                <path d="M60,140 Q100,140 120,100 T180,80 T260,90 T320,140 T300,190 T140,190 Z" fill="#e0e0e0" stroke="#555" stroke-width="2"/>
                <circle cx="70" cy="110" r="15" fill="#e0e0e0" stroke="#555" stroke-width="2"/>
                <!-- قوائم -->
                <rect x="120" y="180" width="15" height="60" fill="#c0c0c0"/>
                <rect x="240" y="180" width="15" height="60" fill="#c0c0c0"/>
                <!-- خط محيط الصدر باللون الأحمر المتقطع -->
                <line x1="145" y1="90" x2="145" y2="185" stroke="#d32f2f" stroke-width="4" stroke-dasharray="5,5"/>
                <text x="110" y="75" fill="#d32f2f" font-weight="bold" font-size="12">محيط الصدر [خط القياس 1]</text>
                <!-- خط طول الجسم باللون الأزرق المتصل -->
                <line x1="110" y1="120" x2="280" y2="120" stroke="#1976d2" stroke-width="4"/>
                <text x="170" y="140" fill="#1976d2" font-weight="bold" font-size="12">طول الجسم [خط القياس 2]</text>
            </svg>
            """
        else:
            svg_code = """
            <svg width="100%" height="250" viewBox="0 0 400 250" style="background-color:#ffffff; border:1px solid #ddd; border-radius:8px;">
                <!-- رسم مبسط للمجترات / الأبقار -->
                <rect x="100" y="90" width="200" height="90" rx="20" fill="#e8f5e9" stroke="#555" stroke-width="2"/>
                <circle cx="80" cy="95" r="20" fill="#e8f5e9" stroke="#555" stroke-width="2"/>
                <rect x="120" y="180" width="20" height="50" fill="#a5d6a7"/>
                <rect x="260" y="180" width="20" height="50" fill="#a5d6a7"/>
                <!-- خط محيط الصدر باللون الأحمر المتقطع -->
                <line x1="140" y1="85" x2="140" y2="182" stroke="#d32f2f" stroke-width="4" stroke-dasharray="5,5"/>
                <text x="100" y="75" fill="#d32f2f" font-weight="bold" font-size="12">محيط الصدر [خط القياس 1]</text>
                <!-- خط طول الجسم باللون الأزرق المتصل -->
                <line x1="90" y1="125" x2="295" y2="125" stroke="#1976d2" stroke-width="4"/>
                <text x="170" y="145" fill="#1976d2" font-weight="bold" font-size="12">طول الجسم [خط القياس 2]</text>
            </svg>
            """
        st.markdown(svg_code, unsafe_index=True)

    # --- الحسابات الرياضية البرمجية المعقدة (محرك الاحتياجات الفسيولوجية) ---
    factor = ANIMAL_DB[animal_type]["العامل"]
    calculated_weight = (float(heart_girth) ** 2 * float(body_length)) / factor

    # دالة محرك التغذية لضبط البروتين والطاقة برمجياً حسب النوع، السلالة، والإنتاج وعلاقتها بالهضم
    def compute_nutrition_requirements(animal, breed, prod, weight):
        # قيم افتراضية قاعدية
        protein_percentage = 12.0
        energy_value = 0.0
        energy_unit = "طاقة مهضومة (DE - Mcal/kg DM)"
        
        if animal == "الخيل":
            energy_unit = "طاقة مهضومة (DE - Mcal/day)"
            # طاقة حفظ الحياة الأساسية للخيول = 1.4 + 0.03 * الوزن
            base_de = 1.4 + (0.03 * weight)
            if "حفظ حياة" in prod:
                protein_percentage = 10.0
                energy_value = base_de
            elif "عمل خفيف" in prod:
                protein_percentage = 11.5
                energy_value = base_de * 1.25
            elif "عمل شاق" in prod:
                protein_percentage = 13.5
                energy_value = base_de * 1.60
            elif "التكاثر" in prod:
                protein_percentage = 14.0
                energy_value = base_de * 1.40
                
        elif animal == "الأبقار (المجترات الكبرى)":
            energy_unit = "طاقة صافية للإنتاج (NE_L - Mcal/day)"
            if "مرتفع" in prod:
                protein_percentage = 17.5
                energy_value = 0.08 * (weight**0.75) + 0.74 * 30 # بافتراض إنتاج 30 لتر حليب
            elif "متوسط" in prod:
                protein_percentage = 15.0
                energy_value = 0.08 * (weight**0.75) + 0.74 * 18
            elif "تسمين" in prod:
                protein_percentage = 14.0
                energy_unit = "طاقة صافية للنمو (NE_g - Mcal/day)"
                energy_value = 0.06 * (weight**0.75) + 5.5 # بافتراض معدل نمو يومي عالي
            else:
                protein_percentage = 12.0
                energy_value = 0.08 * (weight**0.75)

        elif animal == "الأغنام والماعز (المجترات الصغرى)":
            energy_unit = "طاقة صافية (NE - MJ/day)"
            if "تسمين" in prod:
                protein_percentage = 16.0
                energy_value = 0.45 * (weight**0.75) + 3.2
            elif "حليب" in prod:
                protein_percentage = 15.5
                energy_value = 0.45 * (weight**0.75) + 4.5
            else:
                protein_percentage = 12.5
                energy_value = 0.45 * (weight**0.75)
                
        # تخصيص دقيق ومطابقة طبقاً لتأثير السلالة الكروموسومي والفسيولوجي
        if "هولشتاين" in breed or "Thoroughbred" in breed:
            protein_percentage += 1.0 # سلالات ذات معدلات أيضية فائقة الارتفاع تتطلب كثافة أحماض أمينية أعلى
            energy_value *= 1.05
        elif "البرقية" in breed or "العربية الأصيلة" in breed:
            protein_percentage -= 0.5 # تمتاز هذه السلالات الإقليمية بكفاءة استبقاء نيتروجيني أعلى ومقاومة طبيعية للمقنن المنخفض
            
        return round(protein_percentage, 2), round(energy_value, 2), energy_unit

    cp_needed, energy_needed, energy_title = compute_nutrition_requirements(animal_type, breed_type, production_type, calculated_weight)

    # --- مخرجات الحساب ولوحة البيانات الشاملة ---
    st.divider()
    st.header("📊 لوحة المخرجات والنتائج التحليلية الفورية")
    
    out_col1, out_col2, out_col3 = st.columns(3)
    
    with out_col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">الوزن الحي التقديري الناتِج</div>
            <div class="metric-value">{calculated_weight:.2f} كجم</div>
        </div>
        """, unsafe_index=True)
        
    with out_col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">نسبة البروتين الخام المستهدفة (CP%)</div>
            <div class="metric-value">{cp_needed} %</div>
        </div>
        """, unsafe_index=True)
        
    with out_col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">مستوى الاحتياج الغذائي من الطاقة المتوافقة هضماً</div>
            <div class="metric-value">{energy_needed}</div>
            <p style='font-size:11px; color:#666; margin:0;'>{energy_title}</p>
        </div>
        """, unsafe_index=True)

    # معلومات إضافية للمختصين
    if st.session_state.user_role == "المختصين":
        st.info("🔬 **ملاحظة فنية للأطباء ومهندسي الإنتاج:** تم ضبط الاحتياجات الفسيولوجية وهضم البروتين المتدفق للامعاء بناءً على محددات طاقة الكرش المتاحة للميكروبات، لضمان أعلى كفاءة للمادة الجافة المأكولة (DMI).")

else:
    st.warning("⚠️ الوصول للمنصة وشريط القياس محجوب حالياً. يرجى اختيار فئة المستخدم وإدخال كود الأمان الصحيح من القائمة الجانبية لتفعيل النظام البرمجي.")
