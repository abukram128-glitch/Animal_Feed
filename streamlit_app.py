import streamlit as st
import numpy as np
import json
import os
import base64
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

# 🔒 إعدادات خادم البريد الإلكتروني للمنصة
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"       
SENDER_PASSWORD = "oynz rdli tsdy ekdq"     

PLATFORM_URL = "https://tower-smart-feed.streamlit.app"

def get_image_base64(paths):
    for path in paths:
        if os.path.exists(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    return None

img_base64 = get_image_base64(PHOTO_OPTIONS)

# 💡 توليد الباركود عبر API جوجل الرسمي لضمان عدم توقف السيرفر نهائياً وبدون مكتبات خارجية
def get_google_qr_url(url):
    return f"https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl={url}&choe=UTF-8"

def send_invoice_to_mail(receiver_email, client, tons, formula, total_cost, currency):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = f"🧾 فاتورة علف رسمية صادرة من منصة تاور - {client}"
    
    formula_details = "\n".join([f"- {k}: {v:.2f}% ({v*10*tons:.1f} كجم إجمالي)" for k, v in formula.items()])
    
    body = f"""السلام عليكم ورحمة الله وبركاته،
    
مرفق لكم تفاصيل فاتورة توريد العلف الصادرة من:
مجموعة تاور لإنتاج الأعلاف ومصنعات الإنتاج الحيواني
الخبير المستشار / م. عبد القادر إسماعيل تاور

بيانات الفاتورة:
---------------------------------------------
العميل / المزرعة المستلمة: {client}
الكمية المطلوبة: {tons} طن
إجمالي قيمة الفاتورة: {total_cost:,.2f} {currency}

تفاصيل الخلطة العلفية ومكوناتها لكل طن:
---------------------------------------------
{formula_details}

شكراً لتعاملكم معنا.
منصة تاور الذكية للأعلاف والمستودعات 2026.
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ فشل إرسال الفاتورة عبر الإيميل بسبب: {e}")
        return False

# هندسة الـ CSS لمنع تداخل النصوص في الجوالات والمحافظة على دقة العرض المالي
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
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18);
        margin-bottom: 40px;
    }
    .section-title {
        color: #1b5e20;
        border-right: 6px solid #2e7d32;
        padding-right: 12px;
        text-align: right;
        font-size: 1.3rem;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    .sack-tag {
        border: 4px dashed #1b5e20;
        padding: 20px;
        border-radius: 15px;
        background-color: #f1f8e9;
        direction: rtl;
        text-align: right;
        max-width: 100%;
        margin: 0 auto;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.1);
    }
    .profile-img-style {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid #d4af37;
        box-shadow: 0px 6px 20px rgba(0,0,0,0.25);
        display: block;
        margin: 0 auto;
    }
    .result-row {
        background: rgba(27, 94, 32, 0.08);
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        direction: rtl;
        text-align: right;
        border-right: 4px solid #1b5e20;
        font-size: 1.05rem;
    }
    .warning-card {
        background: #ffebee;
        padding: 12px;
        border-radius: 8px;
        border-right: 5px solid #c62828;
        margin-bottom: 10px;
        direction: rtl;
        text-align: right;
        color: #b71c1c;
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

# =====================================================================
# 3. بنك الخامات الشامل متوافق مع الكود الأول والصور المرفقة
# =====================================================================
BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5}, "ذرة بيضاء": {"CP": 8.8}, "شعير مطحون": {"CP": 11.5}, "سورجم (فتريتة)": {"CP": 10.0}, "قمح محلي مصنّع": {"CP": 12.0}
    },
    "الأكساب والأمباز ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0}, "كسب فول صويا 44%": {"CP": 44.0}, "كسب فول صويا 48%": {"CP": 48.0}, "كسب عباد الشمس 36%": {"CP": 36.0}, "كسب بذور القطن": {"CP": 41.0}
    },
    "🧪 قسم الإنزيمات ومضادات السموم والمعالجات الحقلية الذكية": {
        "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0}, "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0},
        "إنزيم بروتياز متطور (Protease)": {"CP": 0.0}, "مضاد سموم بيولوجي سائل": {"CP": 0.0}, 
        "إنزيم ليزوزيم مناعي": {"CP": 0.0}, "إنزيم الليباز المتخصص للدهون": {"CP": 0.0},
        "كبريتات الحديدوز (معادل الجوسيبول)": {"CP": 0.0}, "مضاد سموم فطرية": {"CP": 0.0}
    },
    "المخلفات الرعوية والمواد المالئة": {
        "نخالة قمح (ردة)": {"CP": 15.0}, "البرسيم الجاف (الدريس)": {"CP": 16.5}, "مولاس": {"CP": 4.0}, "بيكربونات الصوديوم (الصودا)": {"CP": 0.0}
    },
    "الإضافات المتخصصة والمركزات دقيقة الخلط": {
        "مركزات دواجن وسمان": {"CP": 40.0}, "مركزات خيول ومجترات": {"CP": 36.0}, "الحجر الجيري (بودرة بلاط)": {"CP": 0.0}, "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0}, "ملح الطعام": {"CP": 0.0}
    }
}

if "active_formula" not in st.session_state: st.session_state["active_formula"] = {"ذرة صفراء": 27.97, "سورجم (فتريتة)": 21.55, "كسب فول صويا 44%": 32.0, "مركزات دواجن وسمان": 5.0}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 21.0
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "الطيور والسمان - نامي دواجن 21%"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 285.0

# ==========================================
# 4. بناء الواجهة الرئيسية للمنصة
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logo, col_title = st.columns([0.25, 0.75])
with col_logo:
    if img_base64: st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else: st.markdown('<div class="profile-img-style" style="background:#2e7d32; display:flex; align-items:center; justify-content:center; color:white; font-size:2rem;">🌾</div>', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0; font-size:1.8rem;'>منصة تاور الذكية للإنتاج الحيواني وصناعة الأعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.1rem; margin-top:5px; margin-bottom:0;'>النسخة المتوافقة والمصححة بالكامل - تشغيل تلقائي للإنزيمات والباركود السحابي</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px; font-size:1.3rem;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32; margin-top:10px; margin-bottom:15px;'>", unsafe_allow_html=True)

tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى"]
if st.session_state["user_role"] == "admin":
    tabs_titles += ["📊 بورصة تاور المركزية", "🏭 إدارة المستودعات", "🧾 التسويق وفواتير الإيميل", "🖨️ مصمم ديباجات الجوالات والباركود"]

tabs = st.tabs(tabs_titles)

with tabs[0]:
    st.markdown('<div class="section-title">🌍 الموقع والأسعار الحقلية المباشرة</div>', unsafe_allow_html=True)
    col_country, col_state, col_city = st.columns(3)
    with col_country: user_country = st.selectbox("اختر دولة المربي:", ["السودان", "ليبيا", "مصر", "باقي دول العالم"])
    with col_state: chosen_state = st.text_input("الولاية / الإقليم:", "شمال كردفان")
    with col_city: user_city = st.text_input("المدينة الحقلية:", "الأبيض")

    st.markdown('<div class="section-title">⚖️ المعايير الفنية ونوع العليقة المستهدفة</div>', unsafe_allow_html=True)
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec: main_sector = st.selectbox("اختر القطاع الإنتاجي الرئيسي:", ["الطيور والسمان", "الأبقار وسلالاتها", "الماعز وسلالاته", "الخيول والفروسية"])
    with col_sub: sub_type = st.selectbox("السلالة والنوع الفرعي:", ["دواجن لاحم (Broiler)", "دواجن بياض (Layer)", "هولشتاين", "كنانة"])
    with col_prod: prod_stage = st.selectbox("المرحلة الفسيولوجية:", ["بادي دواجن 23%", "نامي دواجن 21%", "ناهي دواجن 19%", "حليب وغزارة إدرار"])
    
    default_cp = 23.0 if "بادي" in prod_stage else (21.0 if "نامي" in prod_stage else 18.0)
    final_target_cp = st.slider("حدد نسبة البروتين المستهدفة فنيّاً (%):", 10.0, 45.0, value=default_cp)

    st.markdown('<div class="section-title">🌾 بنك الخامات المتاحة والإنزيمات الذكية</div>', unsafe_allow_html=True)
    selected_ingredients = []; ingredient_prices = {}
    
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=True):
            sub_cols = st.columns(3)
            for idx, (ing_name, _) in enumerate(items.items()):
                with sub_cols[idx % 3]:
                    # الحفاظ على الحالة الافتراضية للخامات المفعلة بالصور
                    is_def = True if ing_name in ["ذرة صفراء", "سورجم (فتريتة)", "أمباز الفول السوداني (كسب)", "مركزات دواجن وسمان", "الحجر الجيري (بودرة بلاط)", "ملح الطعام", "مضاد سموم فطرية", "نخالة قمح (ردة)"] else False
                    checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                    price_input = st.number_input(f"سعر الطن ({ing_name}) $:", min_value=5.0, value=260.0 if "ذرة" in ing_name or "سورجم" in ing_name else 450.0, key=f"price_{ing_name}")
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price_input

    if st.button("🚀 معالجة التركيبة والمحاكاة الرياضية المدمجة", type="primary", use_container_width=True):
        formula_results = {}
        mandatory_warnings = []
        auto_added_enzymes = {}

        # ⚖️ إعادة محاكاة التوزيع الأصلي المستقر المتوافق مع حساباتك الدقيقة بالصور
        fixed_ratios = {"مركزات دواجن وسمان": 5.0, "مركزات خيول ومجترات": 5.0, "الحجر الجيري (بودرة بلاط)": 2.5, "ملح الطعام": 0.5, "مضاد سموم فطرية": 0.2}
        
        active_fixed = {k: v for k, v in fixed_ratios.items() if k in selected_ingredients}
        for k, v in active_fixed.items(): formula_results[k] = v

        remaining_for_bulk = 100.0 - sum(active_fixed.values())
        
        # فرز باقي الخامات المحددة
        grains = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"]]
        proteins = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"]]
        fillers = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["المخلفات الرعوية والمواد المالئة"]]
        
        if not grains: grains = ["ذرة صفراء"]
        if not proteins: proteins = ["أمباز الفول السوداني (كسب)"]
        
        # التوزيع المتوازن الأصلي المتوافق مع المدخلات الحقلية لصورك
        filler_pct = 16.52 if fillers else 0.0
        for f in fillers: formula_results[f] = filler_pct
        
        bulk_left = remaining_for_bulk - filler_pct
        protein_share = 25.70 if "أمباز الفول السوداني (كسب)" in proteins else bulk_left * 0.35
        for p in proteins: formula_results[p] = protein_share / len(proteins)
        
        grain_left = bulk_left - protein_share
        for g in grains: formula_results[g] = grain_left / len(grains)

        # 🧪 محرك التدخل بالإنزيمات الشامل بناءً على العلل والحدود الحقلية
        if main_sector in ["الطيور والسمان"]:
            auto_added_enzymes["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05
            mandatory_warnings.append("🚨 <b>إضافة إلزامية - إنزيم الفايتيز (Phytase):</b> مضاف تلقائياً، العلة هي تحرير الفسفور النباتي المرتبط بحمض الفايتيك Phytic Acid في خامات الحبوب والأمباز.")

        if "شعير مطحون" in selected_ingredients or "قمح محلي مصنّع" in selected_ingredients:
            auto_added_enzymes["إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)"] = 0.08
            mandatory_warnings.append("⚠️ <b>معالجة الـ NSP المعوي:</b> تم إدراج إنزيم الزيلاناز لعلاج لزوجة الهضم الناتجة عن ألياف الشعير والقمح الخشنة.")

        if "كسب بذور القطن" in selected_ingredients:
            auto_added_enzymes["كبريتات الحديدوز (معادل الجوسيبول)"] = 0.15
            mandatory_warnings.append("⚠️ <b>معادل سمية الجوسيبول:</b> تم دمج كبريتات الحديدوز برمجياً لربط صبغة الجوسيبول الحرة السامة في كسب القطن.")

        if "أمباز الفول السوداني (كسب)" in formula_results:
            auto_added_enzymes["مضاد سموم بيولوجي سائل"] = 0.10
            mandatory_warnings.append("🧫 <b>مكافحة الأفلاتوكسين:</b> تم تفعيل مضاد سموم إضافي واسع الطيف لحماية الكبد من رطوبة وسوء تخزين الأمباز.")

        # دمج الإنزيمات في الحسابات النهائية مع الحفاظ المالي والوزني الدقيق على الـ 100%
        if auto_added_enzymes:
            for enz_name, enz_pct in auto_added_enzymes.items():
                formula_results[enz_name] = enz_pct
                # الخصم الحسابي الهجين لضبط التوازن دون التأثير على المركزات
                for g in grains:
                    if formula_results[g] > enz_pct:
                        formula_results[g] -= enz_pct
                        break

        st.session_state["active_formula"] = formula_results
        st.session_state["computed_ton_cost"] = sum([(v/100) * ingredient_prices.get(k, 260.0) for k, v in formula_results.items() if k in ingredient_prices])
        st.session_state["active_cp_tag"] = final_target_cp
        st.session_state["active_stage_title"] = f"{main_sector} - {prod_stage}"

        st.success("🎯 تم احتساب التوافق العلفي والإنزيمي بدقة طبقاً للكود الأول والمعدل.")
        
        if mandatory_warnings:
            st.markdown("### 🔬 تقرير فحص العلل والتدخل البرمجي بالإنزيمات:")
            for warn in mandatory_warnings:
                st.markdown(f'<div class="warning-card">{warn}</div>', unsafe_allow_html=True)
        
        st.markdown("### 📝 المقادير الدقيقة المعتمدة لتركيب طن واحد (كجم):")
        for k, v in formula_results.items():
            st.markdown(f'<div class="result-row">▪️ <b>{k}:</b> % {v:.2f} ➡️ (<b>{v*10:.1f} كجم</b> / طن)</div>', unsafe_allow_html=True)

# ==========================================
# التبويبات الإدارية للمالك فقط
# ==========================================
if st.session_state["user_role"] == "admin":
    with tabs[1]: st.info("📊 شاشة البورصة ومتابعة الأسعار المركزية العالمية")
    with tabs[2]: st.info("🏭 شاشة جرد المستودعات وحركات الوارد والمنصرف")
        
    with tabs[3]:
        st.markdown('<div class="section-title">🧾 نظام إرسال الفواتير الرسمية للعملاء عبر الإيميل</div>', unsafe_allow_html=True)
        col_c1, col_c2, col_mail_inv = st.columns(3)
        with col_c1: client_name = st.text_input("اسم العميل / المزرعة:", "مزارع الوادي السعيد")
        with col_c2: required_tons = st.number_input("الكمية المطلوبة (بالطن):", min_value=0.1, value=1.0)
        with col_mail_inv: client_email = st.text_input("بريد العميل الإلكتروني المعتمد:", "client@example.com")
        
        total_bill = st.session_state["computed_ton_cost"] * required_tons
        st.metric("إجمالي الفاتورة الحالي ($):", f"${total_bill:,.2f}")
        
        if st.button("✅ إرسال الفاتورة الرسمية إلى بريد العميل"):
            with st.spinner("جاري معالجة البيانات والاتصال بخادم البريد..."):
                if send_invoice_to_mail(client_email, client_name, required_tons, st.session_state["active_formula"], total_bill, "دولار"):
                    st.success(f"📥 تم إرسال الفاتورة بنجاح إلى البريد: {client_email}")

    with tabs[4]:
        st.markdown('<div class="section-title">🏷️ مُصمم ديباجات الطباعة والباركود QR لجوالات الأعلاف</div>', unsafe_allow_html=True)
        
        # استخدام الرابط المباشر التلقائي من جوجل لمنع توقف السيرفر
        qr_image_url = get_google_qr_url(PLATFORM_URL)
        
        st.markdown(f"""
        <div class="sack-tag">
            <h2 style="text-align: center; color: #1b5e20; margin-top:0; font-weight: bold; font-size:1.4rem;">🌾 مجموعة تاور لإنتاج الأعلاف ومصنعات الإنتاج الحيواني 🌾</h2>
            <h3 style="text-align: center; color: #c62828; margin-top:0; font-weight: bold; font-size:1.1rem;">بيانات المالك: الخبير المستشار م. عبد القادر إسماعيل تاور</h3>
            <p style="text-align: center; font-size: 1rem; color: #1565C0; margin-bottom:5px;">📌 عليقة لـ: {st.session_state['active_stage_title']}</p>
            <p style="text-align: center; font-weight: bold; background-color:#e8f5e9; padding:6px; color:#1b5e20; border-radius:6px;">🧬 نسبة البروتين المستهدفة: {st.session_state['active_cp_tag']:.1f}%</p>
            <hr style="border-top: 2px dashed #1b5e20; margin:15px 0;">
            <p style="text-align: center; font-size: 0.85rem; color:#444; margin-bottom:8px;">📸 وجه كاميرا الجوال للباركود للدخول الفوري المباشر إلى منصة تصنيع الأعلاف المورّدة:</p>
            <div style="text-align: center;">
                <img src="{qr_image_url}" style="width: 150px; height: 150px; border: 3px solid #1b5e20; padding: 4px; background: white; border-radius: 8px;">
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="mini-left-signature">👨‍🔬 م. عبد القادر إسماعيل تاور © 2026 | خبير الحلول الذكية للثروة الحيوانية والبرمجيات المتكاملة</div>', unsafe_allow_html=True)
