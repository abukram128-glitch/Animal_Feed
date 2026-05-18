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
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. بوابة الدخول وحماية النظام
# ==========================================
if "approved" not in st.session_state:
    st.session_state["approved"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555;'>فضلاً أدخل بيانات الحساب للولوج للمنظومة العلفية</p>", unsafe_allow_html=True)
    
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

# ==========================================
# 3. الهيكل الافتراضي للمخازن والمكتبة العلفية الموسعة
# ==========================================
if "inventory" not in st.session_state:
    st.session_state["inventory"] = {
        "ذرة صفراء": 25.0, "ذرة بيضاء": 10.0, "شعير مطحون": 15.0, "سورجم (فتريتة)": 15.0,
        "أمباز الفول السوداني (كسب)": 20.0, "كسب فول صويا 44%": 14.0, "كسب فول صويا 48%": 18.0, "كسب عباد الشمس 36%": 10.0, 
        "نخالة قمح (ردة)": 20.0, "البرسيم الجاف (الدريس)": 30.0, "مولاس": 5.0,
        "مسحوق أسماك (Fishmeal 60%)": 4.0, "مركزات دواجن وسمان": 3.5,
        "الحجر الجيري (بودرة بلاط)": 6.0, "فوسفات ثنائي الكالسيوم (DCP)": 3.0, "ملح الطعام": 2.5, "مضاد سموم فطرية": 1.2
    }

BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "ME_Poultry": 3350, "ME_Fish": 2800, "CF": 2.2},
        "ذرة بيضاء": {"CP": 8.8, "ME_Poultry": 3300, "ME_Fish": 2750, "CF": 2.3},
        "شعير مطحون": {"CP": 11.5, "ME_Poultry": 2640, "ME_Fish": 2400, "CF": 5.0},
        "سورجم (فتريتة)": {"CP": 10.0, "ME_Poultry": 3150, "ME_Fish": 2600, "CF": 2.7}
    },
    "الأكساب والأمباز ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "ME_Poultry": 2500, "ME_Fish": 2700, "CF": 6.0},
        "كسب فول صويا 44%": {"CP": 44.0, "ME_Poultry": 2230, "ME_Fish": 2500, "CF": 7.0},
        "كسب فول صويا 48%": {"CP": 48.0, "ME_Poultry": 2440, "ME_Fish": 2600, "CF": 3.5},
        "كسب عباد الشمس 36%": {"CP": 36.0, "ME_Poultry": 1700, "ME_Fish": 1900, "CF": 14.0},
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "ME_Poultry": 2900, "ME_Fish": 3200, "CF": 1.0}
    },
    "المخلفات الرعوية والمواد المالئة": {
        "نخالة قمح (ردة)": {"CP": 15.0, "ME_Poultry": 1300, "ME_Fish": 1800, "CF": 11.0},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "ME_Poultry": 800, "ME_Fish": 1200, "CF": 25.0},
        "مولاس": {"CP": 4.0, "ME_Poultry": 1800, "ME_Fish": 2100, "CF": 0.0}
    },
    "الإضافات المتخصصة والمركزات دقيقة الخلط": {
        "مركزات دواجن وسمان": {"CP": 40.0, "ME_Poultry": 2100, "ME_Fish": 1800, "CF": 2.0},
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "ME_Poultry": 0, "ME_Fish": 0, "CF": 0.0},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "ME_Poultry": 0, "ME_Fish": 0, "CF": 0.0},
        "ملح الطعام": {"CP": 0.0, "ME_Poultry": 0, "ME_Fish": 0, "CF": 0.0},
        "مضاد سموم فطرية": {"CP": 0.0, "ME_Poultry": 0, "ME_Fish": 0, "CF": 0.0}
    }
}

ANIMAL_IMAGES_RESOURCES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600&auto=format&fit=crop",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600&auto=format&fit=crop",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600&auto=format&fit=crop",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600&auto=format&fit=crop",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600&auto=format&fit=crop",
    "سمان": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600&auto=format&fit=crop",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=600&auto=format&fit=crop"
}

# ==========================================
# 4. بناء الواجهة الرئيسية وهوية م. عبد القادر
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown('<img src="https://images.unsplash.com/photo-1595246140625-573b715d11dc?q=80&w=150" class="profile-img-style">', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور الذكية للإنتاج الحيواني وصناعة الأعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.2rem; margin-top:5px; margin-bottom:0;'>لوحة التحكم والمطور الشامل - نظام معالجة الأخطاء الآمن</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

if st.session_state["user_role"] == "admin":
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية الكبرى", 
        "🏭 إدارة المستودعات والخصم التلقائي", 
        "🧾 التسويق وفواتير حركة البيع", 
        "🖨️ مصمم بطاقات الديباجة والدعاية"
    ]
else:
    tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى"]

tabs = st.tabs(tabs_titles)

# ====================================================================
# التبويب الأول: النمذجة والحسابات العلفية الكبرى
# ====================================================================
with tabs[0]:
    st.markdown('<div class="section-title">⚖️ أولاً: التقييم التلقائي للأوزان والاحتياجات بناءً على السلالات السودانية والعالمية</div>', unsafe_allow_html=True)
    
    col_an, col_breed, col_h, col_l, col_ag = st.columns(5)
    with col_an:
        animal_type = st.selectbox("نوع الحيوان / القطاع الحقلّي:", ["أبقار تسمين وإنتاج", "ماعز محلي ومحسن", "أغنام ومجترات أخرى", "الدواجن والطيور", "الأسماك والأحياء المائية"])
    
    with col_breed:
        if "أبقار" in animal_type:
            breed_type = st.selectbox("السلالة المستهدفة:", ["كنانة (سوداني رائد)", "بطانة (سوداني مدر)", "البقارة / جهينة", "هولشتاين هجين"])
            dynamic_img_key = "أبقار"
            weight_factor = 10838
        elif "ماعز" in animal_type:
            breed_type = st.selectbox("السلالة المستهدفة:", ["الماعز النوبي السوداني", "الماعز الصحراوي", "الماعز النيلي قزم", "هجين محسن (بور)"])
            dynamic_img_key = "ماعز"
            weight_factor = 11250
        elif "أغنام" in animal_type:
            breed_type = st.selectbox("السلالة المستهدفة:", ["الحمري / الصحراوي السوداني", "البلدي / الكباشي", "البربري"])
            dynamic_img_key = "أغنام"
            weight_factor = 11110
        elif "الدواجن" in animal_type:
            breed_type = st.selectbox("نوع الطيور:", ["طائر السمان (بادي/نامي)", "طائر السمان (بياض)", "دواجن لاحم سريع", "دواجن بياض"])
            dynamic_img_key = "سمان" if "السمان" in breed_type else "دواجن"
            weight_factor = 1
        else:
            breed_type = st.selectbox("نوع الأسماك:", ["البلطي النيلي (Tilapia)", "القرموط / الكلاريا", "أسماك مياه عذبة عامة"])
            dynamic_img_key = "أسماك"
            weight_factor = 1

    with col_h:
        h_girth = st.number_input("📏 محيط الصدر / أو الحجم (سم):", value=150.0 if "أبقار" in animal_type else 65.0)
    with col_l:
        b_length = st.number_input("📏 طول الجسم (سم):", value=130.0 if "أبقار" in animal_type else 55.0)
    with col_ag:
        a_months = st.number_input("⏳ العمر التقديـري (أشهر/أيام):", value=12, min_value=1)

    # حساب الوزن تلقائياً للمجترات
    if "أبقار" in animal_type or "ماعز" in animal_type or "أغنام" in animal_type:
        calc_weight = (h_girth ** 2 * b_length) / weight_factor
        feed_factor = 0.026 if "كنانة" in breed_type or "النوبي" in breed_type else 0.024
        req_feed_kg = calc_weight * feed_factor
        st.success(f"📊 [السلالة السودانية: {breed_type}] | الوزن الحيوي المتوقع: **{calc_weight:.1f} كجم** | كمية المادة الجافة المقترحة يومياً: **{req_feed_kg:.2f} كجم**")
    else:
        st.info(f"📈 [قطاع: {animal_type} - {breed_type}] سيتم احتساب الاحتياجات مباشرة طبقاً لمرحلة النمو.")

    st.markdown('<div class="section-title">📋 ثانياً: ضبط الاحتياجات الفنية والبروتين المستهدف للتركيبة الحالية</div>', unsafe_allow_html=True)
    
    # تحديد البروتين التلقائي حسب اختيار السلالة والقطاع الجديد
    if "الأسماك" in animal_type:
        default_cp = 32.0 if "البلطي" in breed_type else 35.0
    elif "طائر السمان" in breed_type:
        default_cp = 24.0 if "بادي" in breed_type else 20.0
    elif "أبقار" in animal_type:
        default_cp = 16.0 if "كنانة" in breed_type or "بطانة" in breed_type else 14.0
    elif "ماعز" in animal_type:
        default_cp = 15.0 if "النوبي" in breed_type else 13.5
    else:
        default_cp = 18.0

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.metric("🧬 بروتين العليقة المقترح تلقائياً بناءً على نوع القطاع والسلالة المحددة:", f"{default_cp} %")
    with col_p2:
        override_cp = st.checkbox("⚙️ تفعيل التعديل الفني الاختياري للبروتين")
        final_target_cp = st.slider("حدّد نسبة البروتين المستهدفة فنيّاً:", 10.0, max_value=45.0, value=default_cp) if override_cp else default_cp

    st.markdown('<div class="section-title">🌾 ثالثاً: توليد العليقة الاقتصادية المتزنة</div>', unsafe_allow_html=True)
    selected_ingredients = []
    ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=True):
            sub_cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with sub_cols[idx % 3]:
                    # اختيار ذكي تلقائي لبعض الخامات حسب نوع القطاع لتسهيل العمل
                    is_def = False
                    if "الأسماك" in animal_type and ing_name in ["مسحوق أسماك (Fishmeal 60%)", "كسب فول صويا 48%", "ذرة صفراء", "ملح الطعام"]:
                        is_def = True
                    elif "سمان" in dynamic_img_key and ing_name in ["ذرة صفراء", "كسب فول صويا 48%", "مركزات دواجن وسمان", "ملح الطعام"]:
                        is_def = True
                    elif "ذرة" in ing_name or "أمباز" in ing_name or "ملح" in ing_name:
                        is_def = True

                    checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                    if st.session_state["user_role"] == "admin":
                        price_input = st.number_input(f"السعر للطن ({ing_name}) $:", min_value=10.0, value=550.0 if "مسحوق" in ing_name else (480.0 if "أمباز" in ing_name else 120.0), key=f"price_{ing_name}")
                    else:
                        price_input = 400.0 
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price_input

    st.markdown("---")
    if st.button("🚀 تشغيل محرك التركيب الذكي وحساب نسب الخلط المثلى", type="primary", use_container_width=True):
        if len(selected_ingredients) < 3:
            st.error("⚠️ يرجى تحديد 3 خامات علفية على الأقل لضمان توليفة متزنة.")
        else:
            formula_results = {}
            fixed_ratios = {
                "ملح الطعام": 0.005, "مضاد سموم فطرية": 0.002, 
                "الحجر الجيري (بودرة بلاط)": 0.025 if "بياض" in breed_type else 0.015,
                "فوسفات ثنائي الكالسيوم (DCP)": 0.01,
                "مركزات دواجن وسمان": 0.05 if ("الدواجن" in animal_type or "السمان" in breed_type) else 0.0,
            }
            
            used_fixed_pct = 0.0
            for name in selected_ingredients:
                if name in fixed_ratios:
                    formula_results[name] = fixed_ratios[name] * 100
                    used_fixed_pct += fixed_ratios[name] * 100
            
            remaining_pct = 100.0 - used_fixed_pct
            base_energy_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"] or x in BIG_FEEDS_LIBRARY["المخلفات الرعوية والمواد المالئة"]]
            base_protein_ingredients = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"]]
            
            if not base_energy_ingredients: base_energy_ingredients = [selected_ingredients[0]]
            if not base_protein_ingredients: base_protein_ingredients = [selected_ingredients[-1]]
            
            # محاكاة خطية للنسب حسب البروتين المستهدف
            if final_target_cp > 30: p_ratio = 0.55  # أعلاف أسماك مكثفة
            elif final_target_cp > 22: p_ratio = 0.42 # بادئات سمان ودواجن
            elif final_target_cp > 15: p_ratio = 0.25 # حلاب وتسمين كنانة وبطانة
            else: p_ratio = 0.15

            for x in base_protein_ingredients:
                formula_results[x] = (remaining_pct * p_ratio) / len(base_protein_ingredients)
            for x in base_energy_ingredients:
                formula_results[x] = (remaining_pct * (1.0 - p_ratio)) / len(base_energy_ingredients)

            # تخزين البيانات في الجلسة بأمان تام لمنع ظهور أخطاء الـ KeyError
            st.session_state["active_formula"] = formula_results
            st.session_state["active_cp_tag"] = final_target_cp
            st.session_state["active_breed_tag"] = breed_type
            st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES.get(dynamic_img_key, ANIMAL_IMAGES_RESOURCES["عام"])
            st.session_state["active_stage_title"] = animal_type
            
            st.success("🎯 تم توليد التركيبة العلفية المتزنة وحساب مدخلات السلالة والمرحلة بنجاح!")
            
            res_col1, res_col2 = st.columns([0.6, 0.4])
            with res_col1:
                st.write("#### 📝 المقادير المستهدفة لتركيب طن واحد (كجم):")
                for k, v in formula_results.items():
                    st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** لكل طن علف)")
                
                if st.session_state["user_role"] == "admin":
                    ton_cost = sum([(v/100) * ingredient_prices.get(k, 300.0) for k, v in formula_results.items()])
                    st.session_state["computed_ton_cost"] = ton_cost
                    st.metric("💰 تكلفة إنتاج المواد الخام للطن الواحد:", f"${ton_cost:.2f}")
            with res_col2:
                st.write("#### 📊 التوزيع المئوي لمكونات العلف:")
                st.bar_chart(formula_results)

# ====================================================================
# التبويب الثاني والثالث: المستودعات والتسويق (تظهر للآدمين)
# ====================================================================
if st.session_state["user_role"] == "admin":
    with tabs[1]:
        st.markdown('<div class="section-title">🏭 لوحة التحكم الذكية بالمخازن والمستودعات المركزية</div>', unsafe_allow_html=True)
        inv_cols = st.columns(3)
        for idx, (ing_name, qty) in enumerate(st.session_state["inventory"].items()):
            with inv_cols[idx % 3]:
                if qty < 5.0: status_badge = f'<span class="stock-critical">⚠️ حرج: {qty:.2f} طن</span>'
                else: status_badge = f'<span class="stock-normal">آمن: {qty:.2f} طن</span>'
                st.markdown(f"**{ing_name}** | {status_badge}", unsafe_allow_html=True)
                new_qty = st.number_input(f"تحديث رصيد ({ing_name}) طن:", min_value=0.0, value=float(qty), key=f"inv_input_{ing_name}")
                st.session_state["inventory"][ing_name] = new_qty

    with tabs[2]:
        st.markdown('<div class="section-title">💰 نظام تسويق المنتجات وإصدار الفواتير مع الخصم التلقائي</div>', unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: client_name = st.text_input("اسم العميل / المزرعة المستلمة:", "شركة نماء للإنتاج الحيواني والداجني")
        with col_c2: required_tons = st.number_input("الكمية المطلوبة أمر البيع (بالطن):", min_value=0.1, value=2.0, step=0.5)
        with col_c3: added_profit = st.number_input("هامش الربح الصافي المضاف لكل طن ($):", min_value=0.0, value=50.0)

        if "active_formula" in st.session_state:
            raw_cost = st.session_state["computed_ton_cost"]
            selling_price = raw_cost + added_profit
            total_bill = selling_price * required_tons
            
            st.markdown("### 🧾 فاتورة بيع وتوريد أعلاف رسمية")
            st.write(f"**المستشار المصنع:** مكتب م. عبد القادر إسماعيل تاور للاستشارات والحلول الذكية")
            st.write(f"**المستفيد المكرم:** {client_name}")
            st.write("---")
            st.write(f"▪️ سعر البيع النهائي المعتمد للزبون: **`${selling_price:.2f}`** لكل طن.")
            st.markdown(f"### 💰 إجمالي القيمة المستحقة للفاتورة: `${total_bill:.2f}`")
            
            if st.button("✅ تأكيد عملية البيع وخصم المكونات تلقائياً من المخازن"):
                can_deduct = True
                for name, pct in st.session_state["active_formula"].items():
                    needed_ton = (pct / 100) * required_tons
                    if st.session_state["inventory"].get(name, 0.0) < needed_ton:
                        can_deduct = False
                        st.error(f"❌ رصيد غير كافي في المخزن للمكون: {name}! تحتاج لـ {needed_ton:.2f} طن.")
                        break
                if can_deduct:
                    for name, pct in st.session_state["active_formula"].items():
                        needed_ton = (pct / 100) * required_tons
                        st.session_state["inventory"][name] -= needed_ton
                    st.success("🔥 تم تأكيد الفاتورة وخصم كامل المقادير من المستودعات تلقائياً بنجاح واحتساب الأرباح!")
                    st.rerun()

# ====================================================================
# التبويب الرابع: مصمم بطاقات الديباجة والدعاية (محمي تماماً ضد KeyError)
# ====================================================================
    with tabs[3]:
        st.markdown('<div class="section-title">🏷️ مُصمم ديباجات الطباعة الفنية على جوالات الأعلاف</div>', unsafe_allow_html=True)
        
        col_tag1, col_tag2, col_tag3 = st.columns(3)
        with col_tag1: trade_brand = st.text_input("اسم البراند التجاري للدعاية:", "مجموعة تاور لإنتاج الأعلاف ومصنعات الإنتاج الحيواني")
        with col_tag2: contact_phone = st.text_input("هاتف قسم المبيعات والاستشارات الحقلية:", "+249-XX-XXXXXXX")
        with col_tag3: sack_size = st.radio("سعة وحجم الجوال (شكارة العلف):", ["50 كجم", "25 كجم"])

        # استخدام آلية الأمان والحماية المتقدمة للتحقق من الجلسة
        if "active_formula" in st.session_state:
            formula_data = st.session_state["active_formula"]
            target_cp_printed = st.session_state["active_cp_tag"]
            br_tag = st.session_state["active_breed_tag"]
            animal_url = st.session_state["active_animal_img"]
            stage_title_tag = st.session_state["active_stage_title"]
        else:
            # قيم افتراضية احتياطية تمنع ظهور أي خطأ أحمر قبل الضغط على زر الحساب
            formula_data = {"ذرة صفراء": 65.0, "أمباز الفول السوداني (كسب)": 30.0, "إضافات مخصصة": 5.0}
            target_cp_printed = 16.0
            br_tag = "سلالة كنانة / بطانة"
            animal_url = ANIMAL_IMAGES_RESOURCES["عام"]
            stage_title_tag = "إنتاج عام احتياطي"

        weight_divider = 20 if "50" in sack_size else 40
        
        st.markdown("### 🖨️ معاينة ديباجة بطاقة التحليل الفني للجوال (جاهزة للطباعة والتسويق)")
        
        st.markdown(f"""
        <div class="sack-tag">
            <img src="{animal_url}" class="animal-banner-img">
            
            <h2 style="color: #1b5e20; text-align: center; margin-top:0;">🌟 {trade_brand} 🌟</h2>
            <p style="text-align: center; font-weight: bold; color: #1565C0; margin-bottom:5px;">بإشراف وتوصية اختصاصي الإنتاج الحيواني وصناعة الأعلاف</p>
            <h3 style="text-align: center; color: #c62828; margin-top:0; font-weight: bold;">م. عبد القادر إسماعيل تاور</h3>
            
            <p style="text-align: center; font-weight: bold; background-color:#e8f5e9; padding:6px; border-radius:5px; color:#1b5e20; font-size:1.1rem;">
                🎯 علف مخصص لـ: {stage_title_tag} ({br_tag}) | نسبة البروتين المستهدفة: {target_cp_printed:.1f}%
            </p>
            
            <hr style="border-top: 2px dashed #1b5e20;">
            <h4>📊 بطاقة المكونات والوزن الفعلي لكل جوال واحد ({sack_size}):</h4>
            <ul>
                {"".join([f"<li><b>{k}:</b> {v:.2f}% (أي ما يعادل دقيقاً <b>{(v*10)/weight_divider:.2f} كجم</b> في الجوال الواحد)</li>" for k, v in formula_data.items()])}
            </ul>
            <hr style="border-top: 1px solid #1b5e20;">
            <p><b>⚠️ إرشادات الحقل المعتمدة:</b> يُخزن في مكان جاف وبارد بعيدًا عن الرطوبة والأمطار.</p>
            <p style="text-align: center; font-weight: bold; color: #c62828; margin-bottom:0; font-size:1.1rem;">📞 لطلبات التوريد والاستشارات الفنية لتركيب الأعلاف بالسودان: {contact_phone}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 5. التوقيع المصغر الدائم للمطور بأسفل الشاشة
# ==========================================
st.markdown(
    """
    <div class="mini-left-signature">
        👨‍🔬 م. عبد القادر إسماعيل تاور © 2026 | خبير الحلول الذكية للثروة الحيوانية والبرمجيات المتكاملة
    </div>
    """,
    unsafe_allow_html=True
)
