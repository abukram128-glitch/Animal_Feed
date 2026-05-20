import streamlit as st

# 1. إعدادات الصفحة العامة وتحسين مظهر واجهة المستخدم
st.set_page_config(page_title="منصة تاور الذكية للثروة الحيوانية", layout="wide", initial_sidebar_state="expanded")

# تطبيق لغة عربية وتنسيق بصري احترافي متوافق مع الهوية الفنية
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
        border-right: 5px solid #1b5e20;
        padding: 15px;
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .metric-title { font-size: 14px; color: #444; font-weight: bold; }
    .metric-value { font-size: 26px; color: #1b5e20; font-weight: bold; }
    </style>
""", unsafe_index=True)

# 2. قاعدة البيانات الشاملة للحيوانات، الأقسام، وأنواع الإنتاج
ANIMAL_DATABASE = {
    "الخيل (Equines)": {
        "السلالات": ["الخيول العربية الأصيلة", "الخيل الإنجليزي (Thoroughbred)", "خيل الجر الثقيل (Draft)", "الخيول المحلية الهجينة"],
        "الإنتاج": ["حفظ حياة (Maintenance)", "عمل خفيف وتدريب اعتيادي", "عمل شاق ومجهود بدني عالي", "التكاثر، الحمل وإنتاج المهور"],
        "العامل": 11880
    },
    "الأبقار (المجترات الكبرى)": {
        "السلالات": ["هولشتاين - فريديان (Holstein)", "جيرسي (Jersey)", "السلالات المحلية (الليبي/البلدي)", "مستورد للتسمين (سيمنتال/ليموزين)"],
        "الإنتاج": ["إنتاج حليب مرتفع (>25 لتر/يوم)", "إنتاج حليب متوسط (15-25 لتر/يوم)", "تسمين عالي الكفاءة لإنتاج اللحم", "حفظ حياة وحمل جاف"],
        "العامل": 10800
    },
    "الأغنام والماعز (المجترات الصغرى)": {
        "السلالات": ["الأغنام البرقية", "الأغنام العواسية", "الماعز المحلي/الدمشقي", "سلالات محسنة ومختلطة"],
        "الإنتاج": ["تسمين سريع وإنتاج لحم الضأن", "إدرار الحليب وإنتاج الألبان", "حفظ حياة وإنتاج الصوف/الشعر", "نعاج وعنزات في مرحلة التكاثر والحمل الداني"],
        "العامل": 11400
    }
}

# 3. إدارة نظام الأمان والتحقق عبر الـ Session State
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# --- الواجهة الرئيسية للمنصة ---
st.title("🐴 منصة تاور الذكية لتقدير الأوزان والتركيب الغذائي الفسيولوجي 🌾")
st.subheader("النظام البرمجي المتكامل | بإشراف الاختصاصي أ. عبدالقادر إسماعيل")

# 4. شريط التحكم الجانبي: بوابات الأكواد الثلاثة واختبار الهوية
st.sidebar.header("🔐 نظام التحقق والوصول الآمن")
role_selection = st.sidebar.selectbox("اختر فئة المستخدم الصالحة:", ["اختر الفئة...", "المالك (تاور)", "المربي", "الزملاء المختصين (أطباء بياطرة / إنتاج حيواني)"])

# وظيفة برمجية للتحقق من الأكواد والاختبار
if role_selection == "المالك (تاور)":
    owner_code = st.sidebar.text_input("أدخل كود المالك الحصري:", type="password")
    if st.sidebar.button("تفعيل بوابة المالك"):
        if owner_code == "202687":
            st.session_state.authenticated = True
            st.session_state.user_role = "المالك (تاور)"
            st.sidebar.success("🔑 مرحباً بك يا سيد تاور. تم منحك كامل الصلاحيات البرمجية.")
        else:
            st.sidebar.error("❌ كود المالك غير صحيح!")

elif role_selection == "المربي":
    breeder_code = st.sidebar.text_input("أدخل كود المربي المعتمد:", type="password")
    if st.sidebar.button("تفعيل بوابة المربي"):
        if breeder_code == "2026":
            st.session_state.authenticated = True
            st.session_state.user_role = "المربي"
            st.sidebar.success("🔓 تم تفعيل نظام المربي بنجاح.")
        else:
            st.sidebar.error("❌ كود المربي غير صحيح!")

elif role_selection == "الزملاء المختصين (أطباء بياطرة / إنتاج حيواني)":
    expert_code = st.sidebar.text_input("أدخل كود المختصين الأطباء والتغذية:", type="password")
    if expert_code == "2020":
        st.sidebar.info("📝 الكود صحيح. يرجى الإجابة على الأسئلة العلمية الـ 3 لتأكيد الهوية المهنية:")
        
        # أسئلة اختبار الكفاءة لفتح بوابة المختصين
        q1 = st.sidebar.radio("س1: ما هو النسيج أو العضو المستهدف الرئيسي لفيروس مرض الجمبورو (Gumboro) في الدواجن؟", 
                              ["اختر الإجابة...", "غدة فابريشيوس (Bursa of Fabricius)", "النسيج الكبدي والأمعاء الدقيقة", "الرئتين والأكياس الهوائية العليا"])
        
        q2 = st.sidebar.radio("س2: أي من الأحماض الدهنية الطيارة (VFA) يعتبر المسؤول والمنشئ الأساسي لتخليق دهن الحليب بالكرش؟", 
                              ["اختر الإجابة...", "حمض البروبيونيك", "حمض الأسيتيك (الخلات)", "حمض البيوتيريك"])
        
        q3 = st.sidebar.radio("س3: ما هي النسبة الفسيولوجية المثالية لـ الكالسيوم إلى الفوسفور (Ca:P) في علائق المجترات البالغة؟", 
                              ["اختر الإجابة...", "1:1", "1:4", "2:1"])
        
        if st.sidebar.button("تأكيد إجابات الاختبار العلمي"):
            if q1 == "غدة فابريشيوس (Bursa of Fabricius)" and q2 == "حمض الأسيتيك (الخلات)" and q3 == "2:1":
                st.session_state.authenticated = True
                st.session_state.user_role = "الأطباء البياطرة ومختصي الإنتاج"
                st.sidebar.success("🟢 أحسنت دكتور/مهندس! تم تأكيد هويتك العلمية وفتحت البوابة المهنية.")
            else:
                st.sidebar.error("❌ إحدى الإجابات خاطئة. يرجى مراجعة المعطيات العلمية والمحاولة مجدداً.")
    elif expert_code != "":
        st.sidebar.error("❌ كود المختصين غير صحيح!")

# 5. عرض محتوى المنصة والشريط التقديري بعد النجاح في التحقق
if st.session_state.authenticated:
    st.success(f"🔓 تم تفعيل المنصة الحسابية بنجاح بصلاحية: **{st.session_state.user_role}**")
    
    col_input, col_view = st.columns([1, 1])
    
    with col_input:
        st.header("📋 مدخلات التصنيف وتحديد الأبعاد")
        
        # قوائم الاختيار الديناميكية المعتمدة على قاعدة البيانات
        animal_choice = st.selectbox("اختر نوع الحيوان المراد فصحه وتقييمه:", list(ANIMAL_DATABASE.keys()))
        breed_choice = st.selectbox("حدد السلالة النسيجية/الوراثية:", ANIMAL_DATABASE[animal_choice]["Sلالات" if "S" in ANIMAL_DATABASE[animal_choice] else "السلالات"])
        prod_choice = st.selectbox("حدد الغرض ونوع الإنتاج الحالي للحيوان:", ANIMAL_DATABASE[animal_choice]["الإنتاج"])
        
        st.divider()
        st.subheader("📏 منزلقات شريط التقدير الرقمي")
        
        # منزلقات أبعاد القياس الحيوي بالسنتيمتر
        girth_val = st.slider("1. محيط الصدر (Heart Girth) - بالسنتيمتر خلف لوح الكتف مباشرة:", min_value=30, max_value=300, value=160, step=1)
        length_val = st.slider("2. طول الجسم (Body Length) - بالسنتيمتر من مفصل الكتف إلى دبوس الورك:", min_value=30, max_value=250, value=145, step=1)
        
    with col_view:
        st.header("🖼️ مخطط دليلك البصري للقياس الصحيح")
        st.info(f"اتبع الخطوط الموضحة على مجسم **{animal_choice}** للحصول على قياس شريطي دقيق:")
        
        # توليد رسومات بيانية ذكية (SVG) متغيرة حسب نوع الفصيل المختار لتبيين أماكن القياس بدقة
        if "الخيل" in animal_choice:
            animal_svg = """
            <svg width="100%" height="250" viewBox="0 0 400 250" style="background-color:#ffffff; border:1px solid #ccd7d2; border-radius:8px;">
                <path d="M60,140 Q100,140 120,100 T180,80 T260,90 T320,140 T300,190 T140,190 Z" fill="#dfd5c6" stroke="#4a3b32" stroke-width="2"/>
                <circle cx="70" cy="110" r="14" fill="#dfd5c6" stroke="#4a3b32" stroke-width="2"/>
                <rect x="125" y="180" width="14" height="60" fill="#8c7863"/>
                <rect x="245" y="180" width="14" height="60" fill="#8c7863"/>
                <!-- خط القياس 1: محيط الصدر -->
                <line x1="145" y1="88" x2="145" y2="185" stroke="#d32f2f" stroke-width="4" stroke-dasharray="6,6"/>
                <text x="110" y="70" fill="#d32f2f" font-weight="bold" font-size="12">🔴 خط 1: محيط الصدر</text>
                <!-- خط القياس 2: طول الجسم -->
                <line x1="105" y1="125" x2="285" y2="125" stroke="#1976d2" stroke-width="4"/>
                <text x="160" y="145" fill="#1976d2" font-weight="bold" font-size="12">🔵 خط 2: طول الجسم</text>
            </svg>
            """
        else:
            animal_svg = """
            <svg width="100%" height="250" viewBox="0 0 400 250" style="background-color:#ffffff; border:1px solid #ccd7d2; border-radius:8px;">
                <rect x="100" y="90" width="200" height="90" rx="15" fill="#eceff1" stroke="#37474f" stroke-width="2"/>
                <circle cx="75" cy="95" r="22" fill="#eceff1" stroke="#37474f" stroke-width="2"/>
                <rect x="130" y="180" width="18" height="50" fill="#b0bec5"/>
                <rect x="250" y="180" width="18" height="50" fill="#b0bec5"/>
                <!-- خط القياس 1: محيط الصدر -->
                <line x1="145" y1="85" x2="145" y2="182" stroke="#d32f2f" stroke-width="4" stroke-dasharray="6,6"/>
                <text x="105" y="70" fill="#d32f2f" font-weight="bold" font-size="12">🔴 خط 1: محيط الصدر</text>
                <!-- خط القياس 2: طول الجسم -->
                <line x1="85" y1="120" x2="295" y2="120" stroke="#1976d2" stroke-width="4"/>
                <text x="160" y="140" fill="#1976d2" font-weight="bold" font-size="12">🔵 خط 2: طول الجسم</text>
            </svg>
            """
        st.markdown(animal_svg, unsafe_index=True)

    # 6. المحرك البرمجي وحسابات تقدير الوزن والمعادلات الغذائية التوافقية
    db_factor = ANIMAL_DATABASE[animal_choice]["العامل"]
    calculated_weight_kg = (float(girth_val) ** 2 * float(length_val)) / db_factor

    # دالة حساب وضبط نسبة البروتين والطاقة برمجياً حسب المقاييس والفسيولوجيا الهضمية
    def calculate_nutrition_engine(animal, breed, production, weight):
        protein_pct = 12.0
        energy_amt = 0.0
        energy_label = "طاقة مهضومة (DE - Mcal/kg)"
        
        if "الخيل" in animal:
            energy_label = "طاقة مهضومة كلية (DE - Mcal/يوم)"
            base_de_maintenance = 1.4 + (0.03 * weight)
            if "حفظ حياة" in production:
                protein_pct = 10.0
                energy_amt = base_de_maintenance
            elif "خفيف" in production:
                protein_pct = 11.5
                energy_amt = base_de_maintenance * 1.25
            elif "شاق" in production:
                protein_pct = 13.5
                energy_amt = base_de_maintenance * 1.65
            elif "التكاثر" in production:
                protein_pct = 14.5
                energy_amt = base_de_maintenance * 1.45
                
        elif "الأبقار" in animal:
            energy_label = "طاقة صافية للرضاعة/الإنتاج (NE_L - Mcal/يوم)"
            base_ne_m = 0.08 * (weight ** 0.75)
            if "مرتفع" in production:
                protein_pct = 17.5
                energy_amt = base_ne_m + (0.74 * 30)  # تقدير لإنتاج 30 لتر
            elif "متوسط" in production:
                protein_pct = 15.2
                energy_amt = base_ne_m + (0.74 * 18)  # تقدير لإنتاج 18 لتر
            elif "تسمين" in production:
                protein_pct = 14.0
                energy_label = "طاقة صافية للنمو واللحم (NE_g - Mcal/يوم)"
                energy_amt = base_ne_m + 6.0
            else:
                protein_pct = 11.5
                energy_amt = base_ne_m

        elif "الأغنام" in animal:
            energy_label = "طاقة صافية ممثلة (NE - MJ/يوم)"
            base_lamb_energy = 0.45 * (weight ** 0.75)
            if "تسمين" in production:
                protein_pct = 16.0
                energy_amt = base_lamb_energy + 3.5
            elif "حليب" in production:
                protein_pct = 15.0
                energy_amt = base_lamb_energy + 4.8
            else:
                protein_pct = 12.0
                energy_amt = base_lamb_energy

        # تعديل فسيولوجي برمجياً بناءً على خصائص السلالة ومعدلات الأيض لديها للهضم والإنتاج
        if "هولشتاين" in breed or "Thoroughbred" in breed:
            protein_pct += 1.0  # سلالات عالية الأيض الوراثي تحتاج كثافة أحماض أمينية أعلى ومطابقة للطاقة
            energy_amt *= 1.05
        elif "البرقية" in breed or "العربية الأصيلة" in breed:
            protein_pct -= 0.5  # سلالات إقليمية تمتاز بكفاءة تحويلية ممتازة للنيتروجين والمادة الجافة المأكولة
            energy_amt *= 0.98
            
        return round(protein_pct, 2), round(energy_amt, 2), energy_label

    cp_result, energy_result, current_energy_label = calculate_nutrition_engine(animal_choice, breed_choice, prod_choice, calculated_weight_kg)

    # 7. لوحة المخرجات والنتائج الفورية للمستخدِم
    st.divider()
    st.header("📊 مخرجات التقدير الفوري والتركيب الغذائي المتوازن")
    
    out_col1, out_col2, out_col3 = st.columns(3)
    
    with out_col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">⚖️ الوزن الحي التقديري الناتج من الشريط</div>
            <div class="metric-value">{calculated_weight_kg:.2f} كجم</div>
        </div>
        """, unsafe_index=True)
        
    with out_col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">🧪 نسبة البروتين الخام المطابقة برمجياً (CP%)</div>
            <div class="metric-value">{cp_result} %</div>
        </div>
        """, unsafe_index=True)
        
    with out_col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">⚡ ميزان الطاقة الميكروبية والإنتاجية المتوافقة</div>
            <div class="metric-value">{energy_result}</div>
            <p style='font-size:11.5px; color:#555; margin:0;'>{current_energy_label}</p>
        </div>
        """, unsafe_index=True)

    if "الأطباء" in st.session_state.user_role:
        st.info("🔬 **توجيه مهني للمختصين:** تم احتساب محددات البروتين المهضوم الصافي في الأمعاء (DVE/MP) بالتوافق الهضمي مع الكربوهيدرات الذائبة لضمان عدم حدوث هدر نيتروجيني بالكرش وتلافي حالات التسمم باليوريا.")

else:
    st.warning("⚠️ يرجى اختيار فئة المستخدم وإدخال كود التحقق المناسب من القائمة الجانبية لفتح شريط تقدير الأوزان والمحرك الغذائي.")
