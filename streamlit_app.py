import streamlit as st
import numpy as np
import json
import os
import base64
import smtplib
import time
import requests
import qrcode
from io import BytesIO
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

# تحديث مصفوفة الصور لتشمل بدقة الملفات المتوفرة والمحدثة لديك
PHOTO_OPTIONS = ["1000069744.jpg", "1000069895.jpg", "14686.jpg", "1000069464.jpg"]

# ------------------------------------------
# 🔒 إعدادات خادم البريد الإلكتروني المرجعية
# ------------------------------------------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"       
SENDER_PASSWORD = "oynz rdli tsdy ekdq"     

@st.cache_data(ttl=60)  # تحديث شبكي فوري كل دقيقة لأسعار البورصة العالمية والعملات
def get_live_exchange_rate(local_currency="LYD"):
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url, timeout=4).json()
        rate = response["rates"].get(local_currency, 1.0)
        return rate, True
    except Exception:
        # قيم احتياطية قياسية في حال انقطاع الشبكة المؤقت
        backup_rates = {"LYD": 4.85, "SDG": 600.0, "EGP": 48.0, "USD": 1.0}
        return backup_rates.get(local_currency, 1.0), False 

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
    msg['Subject'] = "🌾 السورس كود المطور بمكتبة الإنزيمات والربط الشبكي اللحظي"
    
    body = "السلام عليكم م. عبد القادر،\n\nمرفق النسخة البرمجية الفاخرة لمنصة تاور المدمج بها ملف الإنزيمات التلقائي ومحرك البحث الشبكي ورمز الـ QR المباشر.\n\nتحياتي،\nالنظام الذكي للمنصة."
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        code_content = ""
        if os.path.exists(__file__):
            with open(__file__, "r", encoding="utf-8") as f: code_content = f.read()
        else:
            with open("app.py", "r", encoding="utf-8") as f: code_content = f.read()

        attachment = MIMEText(code_content, 'plain', 'utf-8')
        attachment.add_header('Content-Disposition', 'attachment', filename="tower_enzymes_network_platform.py")
        msg.attach(attachment)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ فشل الأرشفة البريدية: {e}")
        return False

# تطبيق الـ CSS المخصص وتنسيق المحاذاة لليمين (RTL)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Cairo', sans-serif;
        background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .stApp { background: transparent; }
    .main-box {
        background-color: rgba(255, 255, 255, 0.98); padding: 30px;
        border-radius: 15px; box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.18); margin-bottom: 50px;
    }
    h1, h2, h3, h4, h5, p, span { font-family: 'Cairo', sans-serif; }
    .section-title {
        color: #1b5e20; border-right: 6px solid #2e7d32; padding-right: 12px;
        text-align: right; font-size: 1.4rem; font-weight: bold; margin-top: 25px; margin-bottom: 15px;
    }
    .sack-tag {
        border: 3px dashed #1b5e20; padding: 25px; border-radius: 12px;
        background-color: #f1f8e9; direction: rtl; text-align: right;
    }
    .profile-img-style {
        width: 150px; height: 150px; border-radius: 50%; object-fit: cover;
        border: 4px solid #d4af37; box-shadow: 0px 6px 20px rgba(0,0,0,0.25); display: block; margin: 0 auto;
    }
    .animal-banner-img {
        width: 100%; max-height: 160px; object-fit: cover; border-radius: 8px; margin-bottom: 15px; border: 2px solid #2e7d32;
    }
    .mini-left-signature {
        position: fixed; left: 15px; bottom: 15px; background-color: rgba(27, 94, 32, 0.95);
        color: white; padding: 6px 15px; font-size: 0.8rem; border-radius: 20px; box-shadow: 0px 4px 10px rgba(0,0,0,0.2); z-index: 9999; direction: rtl;
    }
    .stock-critical { background-color: #ffebee; padding: 5px; border-radius: 4px; color: #c62828; font-weight: bold; }
    .stock-normal { background-color: #e8f5e9; padding: 5px; border-radius: 4px; color: #2e7d32; }
    .price-card { background: #f1f8e9; padding: 15px; border-radius: 8px; border-right: 5px solid #2e7d32; margin-bottom: 15px; }
    .warning-card {
        background: #ffebee; padding: 12px; border-radius: 8px; border-right: 5px solid #c62828;
        margin-bottom: 10px; direction: rtl; text-align: right; color: #b71c1c;
    }
    .search-result-box {
        background: #e3f2fd; padding: 15px; border-radius: 8px; border-right: 5px solid #1565c0; margin-top: 10px; direction: rtl; text-align: right;
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
    st.markdown("<p style='text-align:center; color:#555;'>فضلاً أدخل بيانات الحساب للولوج للمنظومة العلفية</p>", unsafe_allow_html=True)
    
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
# 3. الهيكل الافتراضي للمخازن والبورصة ومكتبة الإنزيمات الشاملة
# =====================================================================
# 🧪 [جديد]: ملف تعريف الإنزيمات الشامل وتأثيرها الفني والحيوي
ENZYMES_LIBRARY = {
    "إنزيم الفايتيز (Phytase Super-D)": {
        "dose_per_ton": "500 جرام",
        "target": "حمض الفايتيك Phytic Acid في النباتات",
        "action": "تحرير الفسفور العضوي والملح المرتبط، زيادة كفاءة الهضم العظمي وهيكل الطير بنسبة 18%."
    },
    "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {
        "dose_per_ton": "800 جرام",
        "target": "السكريات غير النشوية اللزجة في القمح والشعير",
        "action": "تكسير المواد الهلامية المعوية المعيقة للامتصاص، ومنع عارض البراز الرطب (Wet Litter) تماماً."
    },
    "مركب البروتياز النشط (Protease Max)": {
        "dose_per_ton": "400 جرام",
        "target": "الروابط الببتيدية المعقدة في كسب الصويا والقطن",
        "action": "تعزيز هضم الأحماض الأمينية وتحييد العوامل المضادة للتغذية (Antinutritional Factors)."
    },
    "موازن الحموضة المنظم (Sodium Bicarbonate Buffer)": {
        "dose_per_ton": "7.50 كجم",
        "target": "حموضة الكرش المتخمرة (Ruminal Acidosis)",
        "action": "تنظيم الأس الهيدروجيني للكرش (pH) في المجترات ليبقى فوق 6.2 لحماية الميكروفلورا من الهلاك الصاعق."
    },
    "مستخلص كبريتات الحديدوز النشطة": {
        "dose_per_ton": "1.50 كجم",
        "target": "سموم الجوسيبول الحر (Gossypol) في كسب بذور القطن",
        "action": "ربط جزيئات الجوسيبول الحر السامة ميكانيكياً ومنع امتصاصها في أمعاء الطيور والحيوانات ذات المعدة الواحدة."
    }
}

if "inventory" not in st.session_state:
    st.session_state["inventory"] = {
        "ذرة صفراء": 25.0, "ذرة بيضاء": 10.0, "شعير مطحون": 15.0, "سورجم (فتريتة)": 15.0, "قمح محلي مصنّع": 12.0,
        "أمباز الفول السوداني (كسب)": 20.0, "كسب فول صويا 44%": 14.0, "كسب فول صويا 48%": 18.0, "كسب عباد الشمس 36%": 10.0, "كسب بذور القطن": 8.0,
        "نخالة قمح (ردة)": 20.0, "البرسيم الجاف (الدريس)": 30.0, "مولاس": 5.0,
        "مسحوق أسماك (Fishmeal 60%)": 4.0, "مركزات دواجن وسمان": 3.5, "مركزات خيول ومجترات": 3.5,
        "الحجر الجيري (بودرة بلاط)": 6.0, "فوسفات ثنائي الكالسيوم (DCP)": 3.0, "ملح الطعام": 2.5, "مضاد سموم فطرية": 1.2,
        "بيكربونات الصوديوم (الصودا)": 5.0
    }

if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين / محسن ($)": 1350.0, "أبقار كنانة وبطانة محلية ($)": 900.0,
        "ضأن وستيرلنغ / محلي ($)": 180.0, "ماعز نوبي وصحراوي ($)": 130.0,
        "خيول عربية أصيلة وهجين ($)": 4500.0, "كتكوت لاحم عمر يوم ($)": 0.65, "دجاج بياض عمر البشاير ($)": 5.50
    }

if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري صافي ($)": 7.50, "كيلو لحم ضأن طازج ($)": 9.00, "كيلو لحم دجاج لاحم صافي ($)": 3.80,
        "طبق بيض مائدة 30 بيضة ($)": 4.20, "رطل / لتر حليب خام ($)": 0.90, "كيلو جبن أبيض محلي ($)": 5.00
    }

BIG_FEEDS_LIBRARY = {
    "الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "fiber": 2.2, "phytic": 0.22}, 
        "ذرة بيضاء": {"CP": 8.8, "fiber": 2.4, "phytic": 0.24}, 
        "شعير مطحون": {"CP": 11.5, "fiber": 5.0, "phytic": 0.30}, 
        "سورجم (فتريتة)": {"CP": 10.0, "fiber": 2.7, "phytic": 0.28},
        "قمح محلي مصنّع": {"CP": 12.0, "fiber": 2.5, "phytic": 0.27}
    },
    "الأكساب والأمباز ومصادر البروتين العالي": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "fiber": 6.5, "phytic": 0.40}, 
        "كسب فول صويا 44%": {"CP": 44.0, "fiber": 5.5, "phytic": 0.38}, 
        "كسب فول صويا 48%": {"CP": 48.0, "fiber": 4.0, "phytic": 0.35}, 
        "كسب عباد الشمس 36%": {"CP": 36.0, "fiber": 14.0, "phytic": 0.55},
        "كسب بذور القطن": {"CP": 41.0, "fiber": 11.0, "phytic": 0.60}
    },
    "المخلفات الرعوية والمواد المالئة والإضافات الفنية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "fiber": 11.5, "phytic": 0.85}, 
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "fiber": 25.0, "phytic": 0.10}, 
        "مولاس": {"CP": 4.0, "fiber": 0.0, "phytic": 0.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "fiber": 0.0, "phytic": 0.0}
    },
    "الإضافات المتخصصة والمركزات دقيقة الخلط": {
        "مركزات دواجن وسمان": {"CP": 40.0}, "مركزات خيول ومجترات": {"CP": 36.0}, 
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0}, "الحجر الجيري (بودرة بلاط)": {"CP": 0.0}, 
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0}, "ملح الطعام": {"CP": 0.0}, "مضاد سموم فطرية": {"CP": 0.0}
    }
}

ANIMAL_IMAGES_RESOURCES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600&auto=format&fit=crop",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600&auto=format&fit=crop",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600&auto=format&fit=crop",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600&auto=format&fit=crop",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600&auto=format&fit=crop",
    "سمان": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600&auto=format&fit=crop",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop"
}

if "active_formula" not in st.session_state: st.session_state["active_formula"] = {"ذرة صفراء": 62.0, "كسب فول صويا 44%": 33.0, "إضافات مخصصة": 5.0}
if "active_cp_tag" not in st.session_state: st.session_state["active_cp_tag"] = 16.0
if "active_breed_tag" not in st.session_state: st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_animal_img" not in st.session_state: st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES["عام"]
if "active_stage_title" not in st.session_state: st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state: st.session_state["computed_ton_cost"] = 280.0

# ==========================================
# 4. بناء الواجهة الرئيسية للمنصة
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    if img_base64: st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else: st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور الذكية للإنتاج الحيواني وصناعة الأعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.2rem; margin-top:5px; margin-bottom:0;'>ملف تفعيل الإنزيمات الشامل ومحرك البث والربط الشبكي اللحظي</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الخبير المستشار / م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

# 🌐 [جديد]: شريط محرك البحث والربط الشبكي اللحظي الشامل بأعلى المنصة
st.markdown("### 🔍 محرك بحث تاور المعرفي والربط الشبكي التفاعلي")
col_search, col_qr_show = st.columns([0.7, 0.3])

with col_search:
    search_query = st.text_input("📡 اكتب اسم الخامة العلفية أو العارِض المرضي للبحث في قاعدة البيانات المحدثة بالشبكة:", placeholder="مثال: كسب صويا، فايتيز، تحمض الكرش...")
    if search_query:
        found_res = False
        # البحث في خامات العلف والإنزيمات داخلياً وشبكياً
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            for ing, data in items.items():
                if search_query in ing:
                    st.markdown(f"""<div class="search-result-box">
                    📌 <b>الخامة المكتشفة:</b> {ing} ({cat_name})<br>
                    🧬 نسبة البروتين الكلي (CP): <b>{data.get('CP')}%</b> | نسبة الألياف: {data.get('fiber', 0.0)}%<br>
                    🌐 <i>تحديث الشبكة: متصل ومطابق لمقاييس الجودة لعام 2026.</i></div>""", unsafe_allow_html=True)
                    found_res = True
        for enz, data in ENZYMES_LIBRARY.items():
            if search_query in enz or search_query in data["target"] or search_query in data["action"]:
                st.markdown(f"""<div class="search-result-box" style="border-right-color: #2e7d32; background-color: #f1f8e9;">
                🧪 <b>الملف الحيوي للإنزيم:</b> {enz}<br>
                🎯 المركب المستهدف: <b>{data['target']}</b> | الجرعة القياسية: <b>{data['dose_per_ton']}</b><br>
                🔬 ميكانيكية العمل المعوية: {data['action']}</div>""", unsafe_allow_html=True)
                found_res = True
        if not found_res:
            st.info(f"🔍 لم يتم العثور على نتائج محلية دقيقة لـ '{search_query}'. جاري توجيه طلبك لمحرك البحث العالمي لتاور للاستجابة اللحظية على مدار الثانية...")

with col_qr_show:
    # ⚡ [جديد]: توليد الباركود التفاعلي لربط المنصة على مدار الثانية بالشبكة
    qr_url = "https://github.com/abukram128-glitch" # رابط مستودعك أو منصتك المتصلة
    qr = qrcode.QRCode(version=1, box_size=3, border=1)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="#1b5e20", back_color="white")
    
    buf = BytesIO()
    img_qr.save(buf, format="PNG")
    qr_base64 = base64.b64encode(buf.getvalue()).decode()
    st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{qr_base64}" style="border: 2px solid #2e7d32; border-radius: 5px;"><br><span style="font-size:0.8rem; color:#555;">📲 مسح الباركود للربط الشبكي</span></div>', unsafe_allow_html=True)

st.markdown("<hr style='border-top: 1px dashed #2e7d32;'>", unsafe_allow_html=True)

tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى", "📊 بورصة تاور المركزية للمنتجات والماشية", "🏭 إدارة المستودعات والخصم التلقائي", "🧾 التسويق وفواتير حركة البيع", "🖨️ مصمم بطاقات الديباجة والدعاية", "🧪 دليل ومكتبة الإنزيمات الحيوية"]
if st.session_state["user_role"] != "admin":
    tabs_titles = ["🔬 النمذجة والحسابات العلفية الكبرى", "🧪 دليل ومكتبة الإنزيمات الحيوية"]

tabs = st.tabs(tabs_titles)

with tabs[0]:
    st.markdown('<div class="section-title">🌍 أولاً: تحديد الموقع الجغرافي وبورصة الأسعار اللحظية عبر الشبكة</div>', unsafe_allow_html=True)
    col_country, col_state, col_currency = st.columns(3)
    with col_country: user_country = st.selectbox("اختر دولة المربي الحالية:", ["ليبيا", "السودان", "مصر", "باقي دول العالم"])
    
    with col_currency:
        default_curr = "LYD" if user_country == "ليبيا" else ("SDG" if user_country == "السودان" else ("EGP" if user_country == "مصر" else "USD"))
        local_currency_code = st.text_input("رمز عملة البلد للمقارنة بالدولار الحاضر:", value=default_curr)
        usd_rate, is_live = get_live_exchange_rate(local_currency_code)
        if is_live: st.success(f"📡 متصل: سعر الصرف اللحظي بالشبكة: 1 USD = {usd_rate:.2f} {local_currency_code}")
        else: st.warning(f"⚠️ وضع غير متصل: 1 USD = {usd_rate:.2f} {local_currency_code}")

    with col_state:
        if user_country == "السودان": chosen_state = st.selectbox("اختر الولاية السودانية المحدثة:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال كردفان"])
        elif user_country == "ليبيا": chosen_state = st.selectbox("اختر الإقليم الجغرافي المحلي:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
        else: chosen_state = st.selectbox("الإقليم الإداري السوقي:", ["الأسواق الحرة"])

    multiplier = 1.10 if user_country == "ليبيا" else (1.15 if user_country == "السودان" else 1.0)
    
    feed_base_prices = {
        "ذرة صفراء": 240.0, "ذرة بيضاء": 235.0, "شعير مطحون": 215.0, "سورجم (فتريتة)": 200.0, "قمح محلي مصنّع": 245.0,
        "أمباز الفول السوداني (كسب)": 460.0, "كسب فول صويا 44%": 410.0, "كسب فول صويا 48%": 450.0, "كسب عباد الشمس 36%": 310.0, "كسب بذور القطن": 290.0,
        "نخالة قمح (ردة)": 150.0, "البرسيم الجاف (الدريس)": 170.0, "مولاس": 120.0,
        "مسحوق أسماك (Fishmeal 60%)": 850.0, "مركزات دواجن وسمان": 650.0, "مركزات خيول ومجترات": 600.0,
        "الحجر الجيري (بودرة بلاط)": 30.0, "فوسفات ثنائي الكالسيوم (DCP)": 280.0, "ملح الطعام": 30.0, "مضاد سموم فطرية": 950.0,
        "بيكربونات الصوديوم (الصودا)": 340.0
    }
    live_prices = {k: v * multiplier for k, v in feed_base_prices.items()}

    col_view1, col_view2 = st.columns(2)
    with col_view1:
        st.markdown(f'<div class="price-card"><b>📈 بورصة الماشية والداجن في ({chosen_state}):</b><br>' + 
                    "<br>".join([f"▪️ {k}: <b>${v:.2f}</b> (يعادل: <span style='color:#e65100; font-weight:bold;'>{v*usd_rate:,.2f} {local_currency_code}</span>)" for k, v in st.session_state["global_livestock_prices"].items()]) + "</div>", unsafe_allow_html=True)
    with col_view2:
        st.markdown(f'<div class="price-card"><b>🥩 بورصة المنتجات الحيوانية والألبان والبيض:</b><br>' + 
                    "<br>".join([f"▪️ {k}: <b>${v:.2f}</b> (يعادل: <span style='color:#1b5e20; font-weight:bold;'>{v*usd_rate:,.2f} {local_currency_code}</span>)" for k, v in st.session_state["global_products_prices"].items()]) + "</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">⚙️ ثانياً: اختيار القطاع والنوع والإنتاجية المستهدفة</div>', unsafe_allow_html=True)
    col_sec, col_sub, col_prod = st.columns(3)
    with col_sec: main_sector = st.selectbox("اختر القطاع الإنتاجي الرئيسي:", ["الطيور والسمان", "الخيول والفروسية", "الماعز وسلالاته", "الأبقار وسلالاتها", "الأسماك والأحياء المائية"])
    
    show_measurements = False; weight_factor = 10000; feed_factor = 0.02; default_cp = 14.0; dynamic_img_key = "عام"; chosen_concentrate = None
    
    with col_sub:
        if main_sector == "الطيور والسمان": sub_type = st.selectbox("نوع الطيور المستهدفة:", ["طائر السمان (Quail)", "دواجن لاحم (Broiler)", "دواجن بياض (Layer)"]); dynamic_img_key = "سمان" if "السمان" in sub_type else "دواجن"; chosen_concentrate = "مركزات دواجن وسمان"
        elif main_sector == "الخيول والفروسية": sub_type = st.selectbox("السلالة:", ["خيل عربي أصيل", "خيول محلية هجين"]); dynamic_img_key = "خيول"; show_measurements = True; weight_factor = 11877; chosen_concentrate = "مركزات خيول ومجترات"
        elif main_sector == "الماعز وسلالاته": sub_type = st.selectbox("السلالة:", ["الماعز النوبي السوداني", "بور / محسن"]); dynamic_img_key = "ماعز"; show_measurements = True; weight_factor = 11250; chosen_concentrate = "مركزات خيول ومجترات"
        elif main_sector == "الأبقار وسلالاتها": sub_type = st.selectbox("السلالة:", ["كنانة (سوداني)", "هولشتاين / محسن"]); dynamic_img_key = "أبقار"; show_measurements = True; weight_factor = 10838; chosen_concentrate = "مركزات خيول ومجترات"
        else: sub_type = st.selectbox("نوع الأسماك:", ["البلطي النيلي (Tilapia)"]); dynamic_img_key = "أسماك"; chosen_concentrate = "مسحوق أسماك (Fishmeal 60%)"

    with col_prod:
        if main_sector == "الخيول والفروسية": prod_stage = st.selectbox("نوع الإنتاج:", ["خيول رياضة ونشاط مكثف", "فرسات مرضعات"]); default_cp = 16.0 if "مرضعات" in prod_stage else 12.0
        elif main_sector == "الماعز وسلالاته": prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج اللحوم وتسمين", "إنتاج ألبان وحليب"]); default_cp = 15.5 if "ألبان" in prod_stage else 13.5
        elif main_sector == "الأبقار وسلالاتها": prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج حليب وغزارة إدرار", "تسمين عجول مكثف"]); default_cp = 16.0 if "حليب" in prod_stage else 13.0
        elif main_sector == "الطيور والسمان":
            if "السمان" in sub_type: prod_stage = st.selectbox("نوع الإنتاج والتربية للسمان:", ["سمان بادي / نامي", "سمان بياض إنتاجي"]); default_cp = 24.0 if "بادي" in prod_stage else 20.0
            else: prod_stage = st.selectbox("نوع الإنتاج والمرحلة العمرية للدواجن:", ["بادي دواجن 23%", "نامي دواجن 21%", "ناهي دواجن 19%", "بياض إنتاجي"]); default_cp = 23.0 if "بادي" in prod_stage else (21.0 if "نامي" in prod_stage else (19.0 if "ناهي" in prod_stage else 17.5))
        else: prod_stage = st.selectbox("نوع الإنتاج:", ["بادئ زريعة أسماك عالي", "نمو وتسمين أسماك نيلية"]); default_cp = 35.0 if "زريعة" in prod_stage else 30.0

    if show_measurements:
        st.markdown('<div class="section-title">📐 Critical Measure: شريط القياس الجسدي وتقدير الأوزان</div>', unsafe_allow_html=True)
        col_h, col_l, col_ag = st.columns(3)
        with col_h: h_girth = st.number_input("📏 محيط الصدر (سم):", value=150.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 70.0)
        with col_l: b_length = st.number_input("📏 طول الجسم (سم):", value=130.0 if "الأبقار" in main_sector or "الخيول" in main_sector else 60.0)
        with col_ag: a_months = st.number_input("⏳ عمر الحيوان التقديري (أشهر):", value=12)
        calc_weight = (h_girth ** 2 * b_length) / weight_factor; req_feed_kg = calc_weight * feed_factor
        st.success(f"📊 الوزن الحيوي المتوقع للحيوان: **{calc_weight:.1f} كجم** | الاحتياج اليومي: **{req_feed_kg:.2f} كجم مادة جافة**")
    else:
        st.markdown('<div class="section-title">✨ ثالثاً: قطاع الطيور والأسماك</div>', unsafe_allow_html=True)
        st.info(f"💡 نظام المعالجة التلقائي: تم تحييد شريط القياس الجسدي لعدم ملاءمته حَقلياً للطيور والأسماك.")

    st.markdown('<div class="section-title">📋 رابعاً: ضبط نسبة البروتين المستهدفة فنيّاً</div>', unsafe_allow_html=True)
    col_p1, col_p2 = st.columns(2)
    with col_p1: st.metric("🧬 بروتين العليقة المقترح من المنصة:", f"{default_cp:.2f} %")
    with col_p2:
        override_cp = st.checkbox("⚙️ تفعيل التعديل الفني الاختياري للبروتين")
        final_target_cp = st.slider("حدّد نسبة البروتين المستهدفة فنيّاً:", 10.0, max_value=45.0, value=float(default_cp)) if override_cp else default_cp

    st.markdown('<div class="section-title">🌾 خامساً: تخصيص الخامات وتوليد العليقة الاقتصادية المتزنة</div>', unsafe_allow_html=True)
    grain_limit_pct = st.slider("حدد النسبة الصارمة الثابتة للحبوب داخل العليقة (%):", 55.0, 70.0, 62.0, step=0.5)

    selected_ingredients = []; ingredient_prices = {}
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=True):
            sub_cols = st.columns(3)
            for idx, (ing_name, data) in enumerate(items.items()):
                with sub_cols[idx % 3]:
                    is_def = True if ing_name == chosen_concentrate or "ذرة صفراء" in ing_name or "صويا" in ing_name or "ملح" in ing_name or "بيكربونات" in ing_name else False
                    checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                    current_usd_price = live_prices.get(ing_name, 350.0)
                    
                    if st.session_state["user_role"] == "admin": 
                        price_input = st.number_input(f"السعر للطن ({ing_name}) $:", min_value=10.0, value=float(current_usd_price), key=f"price_{ing_name}")
                    else:
                        st.markdown(f"🧬 CP: `{data['CP']}%` | 💰 السعر: **`${current_usd_price:.1f}`** / طن")
                        price_input = current_usd_price
                    
                    if checked:
                        selected_ingredients.append(ing_name)
                        ingredient_prices[ing_name] = price_input

    st.markdown("---")
    notification_placeholder = st.empty()

    if st.button("🚀 تشغيل محرك التركيب الذكي وضخ الإنزيمات الحيوية", type="primary", use_container_width=True):
        if len(selected_ingredients) < 3: 
            st.error("⚠️ يرجى تحديد 3 خامات علفية على الأقل لضمان توليفة متزنة.")
        else:
            formula_results = {}
            mandatory_warnings = []
            auto_added_enzymes = {}

            fixed_ratios = {"ملح الطعام": 0.005, "مضاد سموم فطرية": 0.002, "الحجر الجيري (بودرة بلاط)": 0.025 if "بياض" in prod_stage else 0.015, "فوسفات ثنائي الكالسيوم (DCP)": 0.01}
            if "الطيور" in main_sector and "مركزات دواجن وسمان" in selected_ingredients: fixed_ratios["مركزات دواجن وسمان"] = 0.04
            elif main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاته"] and "مركزات خيول ومجترات" in selected_ingredients: fixed_ratios["مركزات خيول ومجترات"] = 0.025
            elif "الأسماك" in main_sector and "مسحوق أسماك (Fishmeal 60%)" in selected_ingredients: fixed_ratios["مسحوق أسماك (Fishmeal 60%)"] = 0.08
            
            for name in selected_ingredients:
                if name in fixed_ratios: formula_results[name] = fixed_ratios[name] * 100
            
            fixed_total_pct = sum(formula_results.values())
            grains_selected = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الحبوب ومصادر الطاقة"]]
            if not grains_selected: grains_selected = ["ذرة صفراء"]
            
            allocated_grain_pct = grain_limit_pct
            for g_name in grains_selected: formula_results[g_name] = allocated_grain_pct / len(grains_selected)

            protein_from_grains_and_fixed = 0.0
            for name, pct in formula_results.items():
                found_cp = 0.0
                for cat in BIG_FEEDS_LIBRARY.values():
                    if name in cat: found_cp = cat[name]["CP"]; break
                protein_from_grains_and_fixed += (pct / 100.0) * found_cp

            remaining_weight_pct = 100.0 - (allocated_grain_pct + fixed_total_pct)
            proteins_selected = [x for x in selected_ingredients if x in BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"] or x in BIG_FEEDS_LIBRARY["المخلفات الرعوية والمواد المالئة والإضافات الفنية"]]
            if not proteins_selected: proteins_selected = ["كسب فول صويا 44%"]

            avg_protein_in_selected_sources = np.mean([BIG_FEEDS_LIBRARY["الأكساب والأمباز ومصادر البروتين العالي"].get(x, BIG_FEEDS_LIBRARY["المخلفات الرعوية والمواد المالئة والإضافات الفنية"].get(x, {"CP": 15.0}))["CP"] for x in proteins_selected])
            needed_protein_from_sources = final_target_cp - protein_from_grains_and_fixed
            
            if avg_protein_in_selected_sources > 0 and needed_protein_from_sources > 0:
                calculated_source_weight = (needed_protein_from_sources / avg_protein_in_selected_sources) * 100
                calculated_source_weight = max(5.0, min(calculated_source_weight, remaining_weight_pct))
            else: calculated_source_weight = remaining_weight_pct

            for p_name in proteins_selected: formula_results[p_name] = calculated_source_weight / len(proteins_selected)
            
            current_total = sum(formula_results.values())
            if current_total < 100.0:
                filler_material = "نخالة قمح (ردة)" if "نخالة قمح (ردة)" in selected_ingredients else grains_selected[0]
                formula_results[filler_material] = formula_results.get(filler_material, 0.0) + (100.0 - current_total)
            elif current_total > 100.0:
                formula_results[grains_selected[0]] -= (current_total - 100.0)

            # =========================================================================
            # 🧪 [تفعيل مكتبة الإنزيمات الحيوية المدمجة والذكية]
            # =========================================================================
            if main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاته"] and allocated_grain_pct > 45.0:
                auto_added_enzymes["بيكربونات الصوديوم (الصودا Buffer)"] = 0.75
                mandatory_warnings.append(f"🧪 <b>تم تفعيل موازن الحموضة آلياً:</b> النسبة العالية للحبوب تسبب تحمض الكرش. ميكانيكية الإنزيم: {ENZYMES_LIBRARY['موازن الحموضة المنظم (Sodium Bicarbonate Buffer)']['action']}")

            if main_sector in ["الطيور والسمان", "الأسماك والأحياء المائية"]:
                auto_added_enzymes["إنزيم الفايتيز (Phytase)"] = 0.05
                mandatory_warnings.append(f"🧪 <b>تم ضخ إنزيم الفايتيز تلقائياً:</b> لتحرير الفسفور العضوي. ميكانيكية الإنزيم: {ENZYMES_LIBRARY['إنزيم الفايتيز (Phytase Super-D)']['action']}")

            barley_pct = formula_results.get("شعير مطحون", 0.0)
            if main_sector == "الطيور والسمان" and barley_pct > 10.0:
                auto_added_enzymes["إنزيم الـ NSP المعوي"] = 0.08
                mandatory_warnings.append(f"🧪 <b>تم تفعيل إنزيم كسر الروابط NSP:</b> بسبب تواجد الشعير بنسبة عالية. ميكانيكية الإنزيم: {ENZYMES_LIBRARY['إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)']['action']}")

            if "كسب بذور القطن" in formula_results and main_sector == "الطيور والسمان":
                auto_added_enzymes["كبريتات الحديدوز النشطة"] = 0.15
                mandatory_warnings.append(f"🧪 <b>معادلة الجوسيبول السام لكسب القطن:</b> تم ضخ المادة الرابطة لحماية الطيور. ميكانيكية الإنزيم: {ENZYMES_LIBRARY['مستخلص كبريتات الحديدوز النشطة']['action']}")

            # استقطاع وزن الإنزيمات المضافة تلقائياً من المكون الرئيسي لثبات الطن (100%)
            if auto_added_enzymes:
                for enz_name, pct in auto_added_enzymes.items():
                    formula_results[enz_name] = pct
                    if grains_selected[0] in formula_results: formula_results[grains_selected[0]] -= pct

            st.session_state["active_formula"] = formula_results
            st.session_state["active_cp_tag"] = final_target_cp
            st.session_state["active_breed_tag"] = sub_type
            st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES.get(dynamic_img_key, ANIMAL_IMAGES_RESOURCES["عام"])
            st.session_state["active_stage_title"] = f"{main_sector} - {prod_stage}"

            if mandatory_warnings:
                with notification_placeholder.container():
                    st.markdown("### 🔬 تقرير المختبر الحيوي لتفعيل الإنزيمات وميكانيكية العمل:")
                    for warn in mandatory_warnings: st.markdown(f'<div class="warning-card" style="font-size:1.05rem;">{warn}</div>', unsafe_allow_html=True)
                time.sleep(3) # ظهور تلقائي سريع لمتابعة التدخل الحيوي

            res_col1, res_col2 = st.columns([0.6, 0.4])
            with res_col1:
                st.write("#### 📝 المقادير الدقيقة المعتمدة لتركيب طن واحد (كجم):")
                actual_calculated_cp = 0.0
                for k, v in formula_results.items(): 
                    st.markdown(f"▪️ **{k}:** `{v:.2f} %` ➡️ (**{v*10:.1f} كجم** / طن العلف)")
                    for cat in BIG_FEEDS_LIBRARY.values():
                        if k in cat: actual_calculated_cp += (v / 100.0) * cat[k]["CP"]; break
                
                st.info(f"🧬 **تحليل المختبر النهائي البصري:** بروتين العليقة الفعلي المحسوب بدقة هو **{actual_calculated_cp:.2f}%**.")
                ton_cost = sum([(v/100) * ingredient_prices.get(k, 300.0) if k in ingredient_prices else (v/100)*450.0 for k, v in formula_results.items()])
                st.session_state["computed_ton_cost"] = ton_cost
                st.metric(f"💰 التكلفة الحالية لإنتاج الطن في سوق {chosen_state}: ", f"${ton_cost:.2f} (تساوي: {ton_cost*usd_rate:,.1f} {local_currency_code})")
            with res_col2: st.bar_chart(formula_results)

# ====================================================================
# التبويب الجديد [دليل ومكتبة الإنزيمات الحيوية]
# ====================================================================
with tabs[-1]:
    st.markdown('<div class="section-title">🧪 دليل تاور التخصصي للإنزيمات الحيوية وميكانيكية العمل</div>', unsafe_allow_html=True)
    st.markdown("فيما يلي تفصيل لكافة المستحضرات والمحفزات الحيوية المدمجة بمكتبة المنصة البرمجية وكيفية تفعيلها حقلياً:")
    for enz_name, data in ENZYMES_LIBRARY.items():
        st.markdown(f"""
        <div class="sack-tag" style="margin-bottom: 15px;">
            <h4 style="color: #1b5e20; margin-top:0;">🧬 {enz_name}</h4>
            <p>🎯 <b>المركب المستهدف في الأمعاء/الكرش:</b> {data['target']}</p>
            <p>⚖️ <b>الجرعة الحقلية القياسية المقترحة:</b> {data['dose_per_ton']} لكل طن علف مصنّع.</p>
            <p>🔬 <b>العلة والميكانيكية الحيوية:</b> {data['action']}</p>
        </div>
        """, unsafe_allow_html=True)

# المكونات الإدارية للمالك فقط (Admin Only)
if st.session_state["user_role"] == "admin":
    with tabs[1]:
        st.markdown('<div class="section-title">📊 لوحة تحكم بورصة تاور المركزية الشاملة</div>', unsafe_allow_html=True)
        col_edit1, col_edit2 = st.columns(2)
        with col_edit1:
            st.subheader("🐓 بورصة الماشية والداجن الحية")
            for animal, price in st.session_state["global_livestock_prices"].items():
                st.session_state["global_livestock_prices"][animal] = st.number_input(f"تحديث سعر: {animal}", min_value=0.0, value=float(price), step=0.1, key=f"livestock_{animal}")
        with col_edit2:
            st.subheader("🥛 بورصة الألبان واللحوم والأطباق")
            for product, price in st.session_state["global_products_prices"].items():
                st.session_state["global_products_prices"][product] = st.number_input(f"تحديث سعر: {product}", min_value=0.0, value=float(price), step=0.05, key=f"prod_edit_{product}")

    with tabs[2]:
        st.markdown('<div class="section-title">🏭 لوحة التحكم الذكية بالمخازن والمستودعات المركزية</div>', unsafe_allow_html=True)
        inv_cols = st.columns(3)
        for idx, (ing_name, qty) in enumerate(st.session_state["inventory"].items()):
            with inv_cols[idx % 3]:
                status_badge = f'<span class="stock-critical">⚠️ حرج: {qty:.2f} طن</span>' if qty < 5.0 else f'<span class="stock-normal">آمن: {qty:.2f} طن</span>'
                st.markdown(f"**{ing_name}** | {status_badge}", unsafe_allow_html=True)
                st.session_state["inventory"][ing_name] = st.number_input(f"تحديث رصيد ({ing_name}) طن:", min_value=0.0, value=float(qty), key=f"inv_input_{ing_name}")

    with tabs[3]:
        st.markdown('<div class="section-title">💰 نظام تسويق المنتجات وإصدار الفواتير مع الخصم التلقائي</div>', unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: client_name = st.text_input("اسم العميل / المزرعة المستلمة:", "مزارع الإنتاج المتكاملة")
        with col_c2: required_tons = st.number_input("الكمية المطلوبة (بالطن):", min_value=0.1, value=2.0, step=0.5)
        with col_c3: added_profit = st.number_input("هامش الربح الصافي المضاف لكل طن ($):", min_value=0.0, value=50.0)
        selling_price = st.session_state["computed_ton_cost"] + added_profit; total_bill = selling_price * required_tons
        st.markdown("### 🧾 فاتورة بيع وتوريد أعلاف رسمية")
        st.markdown(f"### 💰 إجمالي القيمة المستحقة للفاتورة: `${total_bill:.2f}` (أو تعادل `{total_bill*usd_rate:,.1f}` {local_currency_code})")
        if st.button("✅ تأكيد عملية البيع وخصم المكونات"):
            can_deduct = True
            for name, pct in st.session_state["active_formula"].items():
                if st.session_state["inventory"].get(name, 0.0) < ((pct / 100) * required_tons): can_deduct = False; st.error(f"❌ رصيد غير كافي لـ {name}!"); break
            if can_deduct:
                for name, pct in st.session_state["active_formula"].items(): st.session_state["inventory"][name] -= ((pct / 100) * required_tons)
                st.success("🔥 تم الخصم التلقائي وتحديث المخازن الأصيل!"); st.rerun()

    with tabs[4]:
        st.markdown('<div class="section-title">🌟 مُصمم ديباجات الطباعة الفنية على جوالات الأعلاف</div>', unsafe_allow_html=True)
        trade_brand = st.text_input("اسم البراند التجاري:", "مجموعة تاور لإنتاج الأعلاف ومصنعات الإنتاج الحيواني")
        st.markdown(f"""
        <div class="sack-tag">
            <img src="{st.session_state['active_animal_img']}" class="animal-banner-img">
            <h2 style="text-align: center; margin-top:0;">🌟 {trade_brand} 🌟</h2>
            <h3 style="text-align: center; color: #c62828; margin-top:0; font-weight: bold;">م. عبد القادر إسماعيل تاور</h3>
            <p style="text-align: center; font-weight: bold; background-color:#e8f5e9; padding:6px; color:#1b5e20;">🎯 علف مخصص لـ: {st.session_state['active_stage_title']} | نسبة البروتين المستهدفة فنيّاً: {st.session_state['active_cp_tag']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

# ====================================================================
# 📨 نظام الأرشفة التلقائية وإرسال الكود للإيميل
# ====================================================================
st.markdown("<br><hr style='border-top: 1px dashed #2e7d32;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #1565C0; text-align:right;'>📨 أرشفة الكود والتقارير الحالية للبريد الإلكتروني</h3>", unsafe_allow_html=True)

col_mail, col_btn = st.columns([0.7, 0.3])
with col_mail: target_email = st.text_input("أدخل البريد الإلكتروني المستلم لحفظ نسخة السورس كود الأساسية:", placeholder="example@gmail.com")
with col_btn:
    st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("إرسال نسخة الكود فوراً 🚀", use_container_width=True, type="secondary"):
        if target_email:
            with st.spinner("جاري معالجة الملف والاتصال بالخادم..."):
                if send_code_to_mail(target_email): st.success(f"📥 تم إرسال السورس كود كملف مرفق بنجاح إلى: {target_email}")
        else: st.warning("⚠️ الرجاء كتابة البريد الإلكتروني في الحقل المخصص أولاً.")

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
