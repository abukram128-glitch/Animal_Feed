import streamlit as st
import numpy as np
import json
import os
import base64
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scipy.optimize import linprog

# ==========================================
# 1. إعدادات المنصة المظهر الفخم لعام 2026
# ==========================================
st.set_page_config(page_title="منصة تاور الذكية المتكاملة للأعلاف والإنتاج الحيواني", page_icon="🌾", layout="wide")

USER_ADMIN = "تاور"       
PASS_ADMIN = "202687"     
USER_GUEST = "مربي"       
PASS_GUEST = "2026"       

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"       
SENDER_PASSWORD = "oynz rdli tsdy ekdq"     

def get_image_base64(paths):
    for path in paths:
        if os.path.exists(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    return None

img_base64 = get_image_base64(PHOTO_OPTIONS)

def send_code_to_mail(receiver_email):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 السورس كود المعالج هندسياً - منصة تاور الذكية"
    
    body = "السلام عليكم م. عبد القادر،\n\nمرفق النسخة المحدثة برمجياً وتغذوياً بعد معالجة مشكلة انغلاق مساحة الحل الرياضي وإضافة دالة حساب الأوزان بشريط القياس حَقلياً.\n\nتحياتي الهندسية."
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        current_file = __file__
        with open(current_file, "r", encoding="utf-8") as f:
            code_content = f.read()
        
        attachment = MIMEText(code_content, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', filename="tower_flexible_optimized_v2.py")
        msg.attach(attachment)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ فشل الإرسال بسبب: {e}")
        return False

# التنسيق والمظهر البرمجي
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
    .formula-item {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 6px;
        font-weight: bold;
        color: #1b5e20 !important;
        border-right: 5px solid #2e7d32;
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
    .profile-img-style {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid #d4af37;
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
        z-index: 9999;
        direction: rtl;
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
            st.session_state["approved"] = True; st.session_state["user_role"] = "admin"; st.rerun()
        elif input_user == USER_GUEST and input_pass == PASS_GUEST:
            st.session_state["approved"] = True; st.session_state["user_role"] = "guest"; st.rerun()
        else: st.error("❌ بيانات الاعتماد غير صحيحة.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 3. مكتبة الخامات الموسعة لعام 2026
# ==========================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة الكبرى": {
        "ذرة صفراء": {"CP": 8.5}, "ذرة بيضاء": {"CP": 8.8}, "شعير مطحون": {"CP": 11.5}, 
        "سورجم (فتريتة)": {"CP": 10.0}, "قمح محلي مصنّع": {"CP": 12.0}, "جريش أرز رزاز": {"CP": 7.8}
    },
    "🌱 الأكساب وأمبازات مصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0}, "كسب فول صويا 44%": {"CP": 44.0}, 
        "كسب فول صويا 48%": {"CP": 48.0}, "كسب عباد الشمس 36%": {"CP": 36.0}, 
        "كسب بذور القطن (مقشور)": {"CP": 41.0}
    },
    "🚜 المخلفات الزراعية والصناعية والمواد المالئة": {
        "نخالة قمح (ردة)": {"CP": 15.0}, "البرسيم الجاف (الدريس)": {"CP": 16.5}, 
        "مولاس قصب السكر": {"CP": 4.0}, "تبن قمح ناعم": {"CP": 3.2}
    },
    "🧬 مصادر البروتين الحيواني والمركزات": {
        "مركزات دواجن لاحم 5%": {"CP": 40.0}, "مركزات دواجن بياض 5%": {"CP": 35.0}, 
        "مركزات خيول ومجترات عالية": {"CP": 36.0}
    },
    "🧪 الأحماض الأمينية والبريمكسات والإضافات": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0}, "بريمكس بياض وبشاير": {"CP": 0.0},
        "بريمكس أبقار حلابة ومجترات": {"CP": 0.0}, "بريمكس خيول وفروسية": {"CP": 0.0},
        "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0},
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0}, "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0}, 
        "ملح الطعام النقي": {"CP": 0.0}, "مضاد سموم فطرية بيولوجي": {"CP": 0.0}
    }
}

if "inventory" not in st.session_state: st.session_state["inventory"] = {}
for cat_name, items in BIG_FEEDS_LIBRARY.items():
    for ing in items:
        if ing not in st.session_state["inventory"]: st.session_state["inventory"][ing] = 50.0

# ==========================================
# 4. بناء الواجهة والدوال الحقلية
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    if img_base64: st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور الذكية للإنتاج الحيواني وصناعة الأعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; margin-top: 5px;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

tabs = st.tabs(["🔬 النمذجة والحسابات الخطية الكبرى"])

with tabs[0]:
    st.markdown('<div class="section-title">⚖️ أولاً: اختيار القطاع والإنتاجية والمحددات الفنية</div>', unsafe_allow_html=True)
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec: main_sector = st.selectbox("اختر القطاع الإنتاجي الرئيسي:", ["الأبقار وسلالاتها", "الماعز وسلالاته", "الخيول والفروسية", "الطيور والسمان"])
    
    show_measurements = False
    weight_factor = 10838  # المعامل الافتراضي للأبقار (معادلة Schaeffer)
    feed_factor = 0.025    # 2.5% من وزن الجسم مادة جافة
    default_cp = 14.5
    req_premix = "بريمكس أبقار حلابة ومجترات"

    with col_sub:
        if main_sector == "الخيول والفروسية": 
            sub_type = st.selectbox("السلالة المستهدفة:", ["خيل عربي أصيل", "ثوروبريد"]); show_measurements = True; weight_factor = 11877; feed_factor = 0.022; req_premix = "بريمكس خيول وفروسية"; default_cp = 14.0
        elif main_sector == "الماعز وسلالاته": 
            sub_type = st.selectbox("السلالة المستهدفة:", ["الماعز النوبي السوداني", "الماعز الصحراوي"]); show_measurements = True; weight_factor = 11250; feed_factor = 0.030; default_cp = 15.0
        elif main_sector == "الأبقار وسلالاتها": 
            sub_type = st.selectbox("السلالة المستهدفة:", ["كنانة (سوداني)", "بطانة", "هولشتاين"]); show_measurements = True; weight_factor = 10838; feed_factor = 0.025; default_cp = 14.5
        else: 
            sub_type = st.selectbox("نوع الطيور والداجن:", ["دواجن لاحم (Broiler)", "دواجن بياض (Layer)"]); req_premix = "بريمكس تسمين دواجن (Premix)"; default_cp = 21.0

    with col_prod:
        prod_stage = st.selectbox("مرحلة الإنتاج العلفية:", ["نامي / إنتاج مكثف", "تسمين دوري رئيسي"])

    # 📐 [إضافة دالة شريط القياس الحقلية] 
    if show_measurements:
        st.markdown('<div class="section-title">📐 ثانياً: شريط القياس الجسدي الحَقلي وحساب الاحتياجات اليومية تلقائياً</div>', unsafe_allow_html=True)
        col_girth, col_length = st.columns(2)
        with col_girth: 
            h_girth = st.number_input("📏 محيط الصدر خلف الكوع مباشرة (سم):", min_value=30.0, max_value=300.0, value=160.0)
        with col_length: 
            b_length = st.number_input("📏 طول الجسم من مفصل الكتف إلى مؤخرة الكفل (سم):", min_value=30.0, max_value=250.0, value=140.0)
        
        # دالة حساب الوزن الحيوى التقريبي: (محيط الصدر ^ 2 * طول الجسم) / معامل السلالة
        calc_weight = (h_girth ** 2 * b_length) / weight_factor
        req_feed_kg = calc_weight * feed_factor
        
        st.info(f"📊 **النتائج الحقلية الحسابية:** الوزن الحيوي التقريبي للحيوان: **{calc_weight:.1f} كجم** | الاحتياج اليومي المقدر من العلف: **{req_feed_kg:.2f} كجم مادة جافة**")

    st.markdown('<div class="section-title">📋 ثالثاً: حد البروتين المستهدف والخامات المتاحة</div>', unsafe_allow_html=True)
    final_target_cp = st.slider("حدد نسبة البروتين المستهدفة بدقة في العليقة (%):", 10.0, 30.0, value=default_cp)

    selected_ingredients = []
    ingredient_prices = {}
    
    # عرض الخامات وتفعيلها
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"{cat_name}", expanded=True if "الحبوب" in cat_name or "الأكساب" in cat_name else False):
            sub_cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with sub_cols[idx % 3]:
                    is_def = True if ing_name in ["ذرة صفراء", "سورجم (فتريتة)", "أمباز الفول السوداني (كسب)", "كسب فول صويا 44%", "نخالة قمح (ردة)", "ملح الطعام النقي", "الحجر الجيري (بودرة بلاط)", "فوسفات ثنائي الكالسيوم (DCP)", req_premix] else False
                    checked = st.checkbox(ing_name, value=is_def, key=f"fex_{ing_name}")
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = 300.0 # سعر افتراضي موحد للمحرك المالي

    # المضافات الثابتة لضمان أمان التركيبة
    fixed_additives = {
        "ملح الطعام النقي": 0.5, "مضاد سموم فطرية بيولوجي": 0.2, "الحجر الجيري (بودرة بلاط)": 1.4, 
        "فوسفات ثنائي الكالسيوم (DCP)": 1.0, req_premix: 0.3
    }
    for item, val in fixed_additives.items():
        if item not in selected_ingredients:
            selected_ingredients.append(item)
            ingredient_prices[item] = 400.0

    st.markdown("---")
    if st.button("🚀 تشغيل محرك الاستمثال الخطي للأعلاف (Scipy Optimized)", type="primary", use_container_width=True):
        
        c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
        bounds = []
        for ing in selected_ingredients:
            if ing in fixed_additives: bounds.append((fixed_additives[ing], fixed_additives[ing]))
            else: bounds.append((0.0, 100.0))

        A_eq = [[1.0 for _ in selected_ingredients]]
        b_eq = [100.0]
        
        cp_row = []
        for ing in selected_ingredients:
            cp_val = 0.0
            for cat in BIG_FEEDS_LIBRARY.values():
                if ing in cat: cp_val = cat[ing].get("CP", 0.0)
            cp_row.append(cp_val)
        A_eq.append(cp_row)
        b_eq.append(final_target_cp * 100.0)

        # صياغة قيود الحبوب والألياف كحدود مرنة مرنة (Optimized Relaxed Bounds) لمنع ظهور تعذر الحل الرياضي
        energy_row_min = []
        fiber_row_max = []
        for ing in selected_ingredients:
            is_energy = ing in BIG_FEEDS_LIBRARY["🌾 الحبوب ومصادر الطاقة الكبرى"]
            is_fiber = ing == "نخالة قمح (ردة)"
            energy_row_min.append(-1.0 if is_energy else 0.0)
            fiber_row_max.append(1.0 if is_fiber else 0.0)
            
        # محاولة أولى بحد أدنى للحبوب 55% وفي حال تعذره يتم النزول الذكي لـ 45% لضمان إخراج التركيبة دائماً دون توقف
        A_ub = [energy_row_min, fiber_row_max]
        b_ub = [-55.0, 15.0]

        res = linprog(c_vector, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

        if not res.success:
            # التخفيف الذكي الثاني للمحرك الرياضي لتفادي مشكلة الصورة الثانية تماماً
            b_ub = [-45.0, 20.0]
            res = linprog(c_vector, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

        if res.success:
            st.success("🎯 تم الاستمثال الخطي الرياضي بنجاح تام وتم معالجة مساحة الحل بنجاح!")
            formula_results = {}
            for idx, ing in enumerate(selected_ingredients):
                if res.x[idx] > 0.001: formula_results[ing] = res.x[idx]

            res_col1, res_col2 = st.columns([0.6, 0.4])
            with res_col1:
                st.write("#### 📝 المقادير الدقيقة المعتمدة لتركيب طن واحد (كجم):")
                for k, v in formula_results.items():
                    st.markdown(f'<div class="formula-item">▪️ {k}: {v:.2f} % ➡️ ({v*10:.1f} كجم / طن)</div>', unsafe_allow_html=True)
            with res_col2: 
                st.bar_chart(formula_results)
        else:
            st.error("❌ تعذر إيجاد حل رياضي متزن تماماً ضمن المحددات الحالية. الرجاء تفعيل خامات بروتينية إضافية كأمباز الفول السوداني أو كسب الصويا لتوسيع نطاق الموازنة الحسابية.")

# ====================================================================
# نظام الأرشفة التلقائية وإرسال الكود للبريد الإلكتروني بأسفل التطبيق
# ====================================================================
st.markdown("<br><hr style='border-top: 1px dashed #2e7d32;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #1565C0; text-align:right;'>📨 أرشفت الكود والتقارير الحالية للبريد الإلكتروني</h3>", unsafe_allow_html=True)

col_mail, col_btn = st.columns([0.7, 0.3])
with col_mail:
    target_email = st.text_input("أدخل البريد الإلكتروني المستلم لحفظ نسخة السورس كود الأساسية:", placeholder="example@gmail.com")

with col_btn:
    st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("إرسال نسخة الكود فوراً 🚀", use_container_width=True):
        if target_email:
            with st.spinner("جاري معالجة الملف والاتصال بالخادم..."):
                if send_code_to_mail(target_email):
                    st.success(f"📥 تم إرسال السورس كود كملف مرفق (.py) بنجاح إلى: {target_email}")
        else:
            st.warning("⚠️ الرجاء كتابة البريد الإلكتروني أولاً.")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="mini-left-signature">
        👨‍🔬 م. عبد القادر إسماعيل تاور © 2026 | خبير الحلول الذكية للثروة الحيوانية والبرمجيات المتكاملة
    </div>
    """,
    unsafe_allow_html=True
)
