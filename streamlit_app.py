import base64
import io
import json
import os
import smtplib
import time
import urllib.parse
import sqlite3  
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import arabic_reshaper
import numpy as np
import pandas as pd
import streamlit as st
from bidi.algorithm import get_display
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from scipy.optimize import linprog

# ==========================================
# 0. تأسيس وإدارة قاعدة البيانات (الخطوة 2 المحدثة)
# ==========================================
DB_NAME = "tower_scientific.db"


def init_database():
    """إنشاء الجداول وضخ البيانات الأساسية مع تحديث الأحماض الأمينية ومحددات الهضم قيود الاستخدام"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # جدول المكونات الأساسي (محدث ليدعم الحدود القصوى والدنيا لكل خامة)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        price_per_ton REAL NOT NULL,
        max_limit REAL DEFAULT 100.0,
        min_limit REAL DEFAULT 0.0
    )
    """)

    # جدول العناصر الغذائية ومعاملات الهضم (محدث لعام 2026)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Nutrient_Matrix (
        ingredient_id INTEGER,
        crude_protein REAL DEFAULT 0.0,
        lysine REAL DEFAULT 0.0,
        methionine REAL DEFAULT 0.0,
        digestibility_coeff REAL DEFAULT 1.0,
        starch_equivalent REAL DEFAULT 0.0,
        FOREIGN KEY (ingredient_id) REFERENCES Ingredients(id) ON DELETE CASCADE
    )
    """)
    conn.commit()

    # فحص وضخ المكتبة الموسعة تلقائياً في حال كانت قاعدة البيانات فارغة
    cursor.execute("SELECT COUNT(*) FROM Ingredients")
    if cursor.fetchone()[0] == 0:
        raw_library = {
            "🌾 الحبوب ومصادر الطاقة الكبرى": {
                "ذرة صفراء": {"CP": 8.5, "lys": 0.24, "met": 0.17, "DC": 0.85, "SE": 80.0, "price": 230.0},
                "ذرة بيضاء": {"CP": 8.8, "lys": 0.23, "met": 0.16, "DC": 0.83, "SE": 78.0, "price": 225.0},
                "شعير مطحون": {"CP": 11.5, "lys": 0.36, "met": 0.19, "DC": 0.80, "SE": 71.0, "price": 210.0},
                "سورجم (فتريتة)": {"CP": 10.0, "lys": 0.22, "met": 0.15, "DC": 0.78, "SE": 70.0, "price": 195.0},
                "قمح محلي مصنّع": {"CP": 12.0, "lys": 0.32, "met": 0.21, "DC": 0.85, "SE": 75.0, "price": 240.0},
                "جريش أرز رزاز": {"CP": 7.8, "lys": 0.28, "met": 0.20, "DC": 0.82, "SE": 82.0, "price": 230.0},
                "دخن محلي غزير": {"CP": 11.0, "lys": 0.30, "met": 0.22, "DC": 0.75, "SE": 68.0, "price": 230.0},
                "شوفان علفي": {"CP": 11.0, "lys": 0.40, "met": 0.18, "DC": 0.76, "SE": 62.0, "price": 230.0},
            },
            "🌱 الأكساب وأمبازات مصادر البروتين العالي": {
                "أمباز الفول السوداني (كسب)": {"CP": 46.0, "lys": 1.60, "met": 0.52, "DC": 0.88, "SE": 73.0, "price": 460.0},
                "كسب فول صويا 44%": {"CP": 44.0, "lys": 2.70, "met": 0.62, "DC": 0.90, "SE": 74.0, "price": 440.0},
                "كسب فول صويا 48%": {"CP": 48.0, "lys": 2.90, "met": 0.67, "DC": 0.91, "SE": 76.0, "price": 480.0},
                "كسب عباد الشمس 36%": {"CP": 36.0, "lys": 1.20, "met": 0.75, "DC": 0.76, "SE": 42.0, "price": 310.0},
                "كسب بذور القطن (مقشور)": {"CP": 41.0, "lys": 1.75, "met": 0.64, "DC": 0.78, "SE": 55.0, "price": 290.0},
                "كسب بذور الكتان": {"CP": 32.0, "lys": 1.15, "met": 0.60, "DC": 0.82, "SE": 65.0, "price": 350.0},
                "كسب السمسم المحسن": {"CP": 42.0, "lys": 1.25, "met": 1.10, "DC": 0.84, "SE": 70.0, "price": 350.0},
                "كسب جلوتين الذرة 60%": {"CP": 60.0, "lys": 1.02, "met": 1.45, "DC": 0.92, "SE": 85.0, "price": 350.0},
                "كسب نواة النخيل": {"CP": 16.0, "lys": 0.62, "met": 0.31, "DC": 0.65, "SE": 52.0, "price": 350.0},
            },
            "🚜 المخلفات الزراعية والصناعية والمواد المالئة": {
                "نخالة قمح (ردة)": {"CP": 15.0, "lys": 0.58, "met": 0.23, "DC": 0.72, "SE": 45.0, "price": 150.0},
                "البرسيم الجاف (الدريس)": {"CP": 16.5, "lys": 0.75, "met": 0.28, "DC": 0.60, "SE": 35.0, "price": 170.0},
                "مولاس قصب السكر": {"CP": 4.0, "lys": 0.05, "met": 0.02, "DC": 0.95, "SE": 50.0, "price": 120.0},
                "تبن قمح ناعم": {"CP": 3.2, "lys": 0.08, "met": 0.04, "DC": 0.35, "SE": 18.0, "price": 230.0},
                "قشر فول سوداني مطحون": {"CP": 5.0, "lys": 0.12, "met": 0.05, "DC": 0.30, "SE": 15.0, "price": 230.0},
                "سرسة الأرز المطحونة": {"CP": 2.5, "lys": 0.06, "met": 0.03, "DC": 0.25, "SE": 12.0, "price": 230.0},
                "بقايا تفل البنجر المجفف": {"CP": 8.0, "lys": 0.42, "met": 0.12, "DC": 0.75, "SE": 58.0, "price": 230.0},
                "مخلفات مصانع البسكويت": {"CP": 9.5, "lys": 0.28, "met": 0.15, "DC": 0.88, "SE": 76.0, "price": 230.0},
                "سیلاج ذرة كامل متكامل": {"CP": 8.0, "lys": 0.22, "met": 0.14, "DC": 0.68, "SE": 50.0, "price": 230.0},
            },
            "🧬 مصادر البروتين الحيواني والمركزات دقيقة الخلط": {
                "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "lys": 4.50, "met": 1.65, "DC": 0.85, "SE": 65.0, "price": 850.0},
                "مسحوق أسماك فاخر (72%)": {"CP": 72.0, "lys": 5.40, "met": 2.10, "DC": 0.90, "SE": 72.0, "price": 850.0},
                "مسحوق اللحم والعظم": {"CP": 50.0, "lys": 2.60, "met": 0.70, "DC": 0.75, "SE": 50.0, "price": 850.0},
                "مركزات دواجن وسمان": {"CP": 40.0, "lys": 2.50, "met": 1.20, "DC": 0.85, "SE": 60.0, "price": 650.0},
                "مركزات خيول ومجترات": {"CP": 36.0, "lys": 1.80, "met": 0.65, "DC": 0.80, "SE": 55.0, "price": 600.0},
            },
            "🧪 الأحماض الأمينية البلورية النقية": {
                "ليسين نقي (L-Lysine)": {"CP": 94.0, "lys": 78.0, "met": 0.0, "DC": 1.00, "SE": 0.0, "price": 230.0},
                "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "lys": 0.0, "met": 99.0, "DC": 1.00, "SE": 0.0, "price": 230.0},
                "ثريونين نقي (L-Threonine)": {"CP": 72.0, "lys": 0.0, "met": 0.0, "DC": 1.00, "SE": 0.0, "price": 230.0},
                "تريبتوفان نقي (L-Tryptophan)": {"CP": 85.0, "lys": 0.0, "met": 0.0, "DC": 1.00, "SE": 0.0, "price": 230.0},
                "فالين نقي (L-Valine)": {"CP": 90.0, "lys": 0.0, "met": 0.0, "DC": 1.00, "SE": 0.0, "price": 230.0},
            },
            "🔬 الإنزيمات والبريمكسات والإضافات التخصصية": {
                "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "price": 230.0},
                "بريمكس بياض وبشاير": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "price": 230.0},
                "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "price": 230.0},
                "بريمكس خيول وفروسية": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "price": 230.0},
                "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "price": 230.0},
                "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "price": 230.0},
                "كبريتات الحديدوز (معادل الجوسيبول)": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "price": 230.0},
                "مستخلص الخمائر والجدر الخلوية (MOS)": {"CP": 12.0, "lys": 0.30, "met": 0.10, "DC": 0.50, "SE": 10.0, "price": 230.0},
            },
            "🪨 الأملاح والمعادن ومنظمات الهضم": {
                "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "price": 40.0},
                "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "price": 280.0},
                "ملح الطعام": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "price": 30.0},
                "مضاد سموم فطرية": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "price": 950.0},
                "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "price": 340.0},
                "أكسيد المغنيسيوم العلفي": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "price": 230.0},
                "يوريا علفية محصنة (المجترات فقط)": {"CP": 287.0, "lys": 0.0, "met": 0.0, "DC": 0.95, "SE": 0.0, "price": 230.0},
            }
        }
        for cat, items in raw_library.items():
            for name, nut in items.items():
                cursor.execute(
                    "INSERT OR IGNORE INTO Ingredients (name, category, price_per_ton) VALUES (?, ?, ?)",
                    (name, cat, nut["price"]),
                )
                ing_id = (
                    cursor.lastrowid
                    if cursor.lastrowid
                    else cursor.execute(
                        "SELECT id FROM Ingredients WHERE name=?", (name,)
                    )
                    .fetchone()[0]
                )
                cursor.execute(
                    "INSERT INTO Nutrient_Matrix VALUES (?, ?, ?, ?, ?, ?)",
                    (ing_id, nut["CP"], nut["lys"], nut["met"], nut["DC"], nut["SE"]),
                )
        conn.commit()
    conn.close()


init_database()


def load_feeds_from_db():
    """تحميل البيانات حياً لبناء المصفوفة والقاموس التفاعلي للنظام لتدعم قيود الاستخدام"""
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT i.name, i.category, i.price_per_ton, i.max_limit, i.min_limit,
           n.crude_protein, n.lysine, n.methionine, n.digestibility_coeff, n.starch_equivalent
    FROM Ingredients i JOIN Nutrient_Matrix n ON i.id = n.ingredient_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    structured_library = {}
    for cat in df["category"].unique():
        structured_library[cat] = {}
        sub_df = df[df["category"] == cat]
        for _, row in sub_df.iterrows():
            structured_library[cat][row["name"]] = {
                "CP": row["crude_protein"],
                "lys": row["lysine"],
                "met": row["methionine"],
                "DC": row["digestibility_coeff"],
                "SE": row["starch_equivalent"],
                "price": row["price_per_ton"],
                "max": row["max_limit"],
                "min": row["min_limit"],
            }
    return structured_library


# ==========================================
# 1. إعدادات المنصة الرسمية والمظهر الفخم
# ==========================================
st.set_page_config(
    page_title="منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف",
    page_icon="🌾",
    layout="wide",
)

CODES_DB = {
    "202687": "owner",  # المالك تاور - صلاحية واسعة
    "2020": "specialist",  # المختص والزملاء
    "2026": "breeder",  # المربي - الحدود العملية فقط
}

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"
SENDER_PASSWORD = "oynz rdli tsdy ekdq"
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"
GOOGLE_FORM_URL = "https://forms.google.com/YOUR_FORM_URL"


def get_image_base64(paths):
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode()
            except Exception:
                pass
    return None


img_base64 = get_image_base64(PHOTO_OPTIONS)


def send_code_to_mail(receiver_email):
    if SENDER_EMAIL == "YOUR_EMAIL@gmail.com" or not SENDER_PASSWORD:
        st.error(
            "⚠️ خطأ إعدادات: يرجى تحديث بيانات الـ SMTP داخل السورس كود أولاً."
        )
        return False

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg["Subject"] = "🌾 السورس كود الكامل والمطور - منصة تاور العلمية"

    body = "السلام عليكم م. عبد القادر،\n\nمرفق مع هذه الرسالة النسخة البرمجية الكاملة والمستقرة لمنصتكم الذكية بعد تحديث الدليل والواجهات بالكامل وتضمين معايير البروتين المهضوم ومعادل النشاء والأحماض الأمينية.\n\nتحياتي الهندسية."
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        try:
            current_file = __file__
            with open(current_file, "r", encoding="utf-8") as f:
                code_content = f.read()
        except NameError:
            code_content = "# كود المنصة مأرشف داخلياً\n"

        attachment = MIMEText(code_content, "plain", "utf-8")
        attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename="tower_scientific_platform.py",
        )
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


def fix_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text


def generate_pdf_report(
    formula,
    target_protein,
    breed,
    cost,
    city,
    local_cost,
    local_sym,
    computed_se,
    mode_label,
):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    font_name = "Helvetica"
    if os.path.exists("Amiri-Regular.ttf"):
        try:
            pdfmetrics.registerFont(TTFont("Amiri", "Amiri-Regular.ttf"))
            font_name = "Amiri"
        except Exception:
            pass

    p.setFont(font_name, 16)
    p.drawString(
        100,
        800,
        fix_arabic_text(
            "تقرير: منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف"
        ),
    )
    p.setFont(font_name, 12)
    p.drawString(
        100,
        760,
        fix_arabic_text(f"المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور"),
    )
    p.drawString(
        100, 740, fix_arabic_text(f"الموقع / السوق الجغرافي المستهدف: {city}")
    )
    p.drawString(
        100, 720, fix_arabic_text(f"الفصيل / السلالة الحيوانية: {breed}")
    )
    p.drawString(
        100,
        700,
        fix_arabic_text(f"معيار حساب البروتين المستهدف: {mode_label}"),
    )
    p.drawString(
        100,
        710,
        fix_arabic_text(f"نسبة البروتين المستهدفة المحققة: {target_protein}%"),
    )
    p.drawString(
        100,
        660,
        fix_arabic_text(
            f"إجمالي معادل النشاء المحقق (SE): {computed_se:.2f} وحدة طاقة"
        ),
    )
    p.drawString(
        100,
        640,
        fix_arabic_text(
            f"التكلفة المحسوبة للطن: ${cost:.2f} ({local_cost:,.2f} {local_sym})"
        ),
    )

    p.setFont(font_name, 14)
    p.drawString(
        100,
        600,
        fix_arabic_text("المقادير الدقيقة المعتمدة لتركيب خلطة الطن الواحدة:"),
    )
    p.setFont(font_name, 12)

    y_position = 570
    for k, v in formula.items():
        line_text = f"- {k}: {v:.2f}% -> ({v*10:.1f} كجم / طن)"
        p.drawString(100, y_position, fix_arabic_text(line_text))
        y_position -= 20
        if y_position < 50:
            p.showPage()
            y_position = 800

    p.setFont(font_name, 10)
    p.drawString(
        100,
        50,
        fix_arabic_text(
            "تم التوليد تلقائياً بواسطة منصة تاور العلمية © 2026 تحت إشراف م. عبد القادر إسماعيل تاور"
        ),
    )
    p.save()
    buffer.seek(0)
    return buffer.getvalue()


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;600;700&display=swap');
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
    h1, h2, h3, h4, h5, p, span, li { font-family: 'Cairo', sans-serif; }
    
    .formula-item {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 6px;
        font-weight: bold;
        color: #1b5e20 !important;
        border-right: 5px solid #2e7d32;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        text-align: right;
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
    .price-card {
        background: #f1f8e9;
        padding: 15px;
        border-radius: 8px;
        border-right: 5px solid #2e7d32;
        margin-bottom: 15px;
        direction: rtl;
        text-align: right;
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
    
    .manual-book {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.05);
        direction: rtl;
        text-align: right;
    }
    .book-chapter {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        color: #ffffff;
        padding: 10px 15px;
        border-radius: 6px;
        font-weight: bold;
        margin-top: 20px;
        font-size: 1.15rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .book-body {
        padding: 12px 20px;
        font-size: 1.05rem;
        line-height: 1.7;
        color: #2c3e50;
        border-left: 3px solid #3498db;
        margin-bottom: 15px;
        background-color: #f8f9fa;
        border-radius: 0 6px 6px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 2. بوابة الدخول وحماية النظام بالأكواد المحسنة
# ==========================================
if "approved" not in st.session_state:
    st.session_state["approved"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "login_welcome_shown" not in st.session_state:
    st.session_state["login_welcome_shown"] = False

if not st.session_state["approved"]:
    st.markdown(
        '<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">',
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#555;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</p>",
        unsafe_allow_html=True,
    )

    input_code = st.text_input("🔑 أدخل كود الدخول الخاص بك:", type="password")

    if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
        input_code_stripped = input_code.strip()
        if input_code_stripped in CODES_DB:
            st.session_state["approved"] = True
            st.session_state["user_role"] = CODES_DB[input_code_stripped]
            st.rerun()
        else:
            st.error("❌ الكود غير صحيح! يرجى مراجعة إدارة المنصة.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# سحب مكتبة الخامات حياً من قاعدة البيانات المستقرة بعد تجاوز بوابة الأمان
BIG_FEEDS_LIBRARY = load_feeds_from_db()

# توقيع عائم في أسفل يسار الشاشة تأكيداً للهوية الرسمية
st.markdown(
    '<div class="mini-left-signature">🌾 إشراف م. عبد القادر إسماعيل تاور | 2026</div>',
    unsafe_allow_html=True,
)

# ==========================================
# 3. ترويسة المنصة الرأسية والتعريف بالفريق الدبلوماسي والعلمي
# ==========================================
st.markdown('<div class="main-box" style="direction: rtl;">', unsafe_allow_html=True)

col_h1, col_h2 = st.columns([1, 4])
with col_h1:
    if img_base64:
        st.markdown(
            f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="text-align:center; font-size:4.5rem; padding-top:10px;">🌾</div>',
            unsafe_allow_html=True,
        )

with col_h2:
    st.markdown(
        "<h1 style='color: #1b5e20; margin-bottom: 0; text-align: right;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h4 style='color: #d4af37; margin-top: 5px; font-weight: 600; text-align: right;'>المستشار الفني والأكاديمي العام: مهندس عبد القادر إسماعيل تاور</h4>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color: #455a64; font-size: 1.05rem; line-height: 1.6; text-align: right;'>نظام الخوارزميات المطور للاستمثال الخطي للأعلاف وصياغة العلائق المثالية بأقل تكلفة ممكنة، بالتوافق مع معايير جودة التغذية وأحدث دبلومات الإنتاج الحيواني لعام 2026.</p>",
        unsafe_allow_html=True,
    )

if not st.session_state["login_welcome_shown"]:
    role_ar = (
        "المالك والمدير العام 👑"
        if st.session_state["user_role"] == "owner"
        else (
            "الاختصاصي والزملاء 🔬"
            if st.session_state["user_role"] == "specialist"
            else "المربي والمستفيد 🚜"
        )
    )
    st.toast(
        f"مرحباً بك مهندس عبد القادر. تم تسجيل الدخول بصلاحية: {role_ar}",
        icon="✅",
    )
    st.session_state["login_welcome_shown"] = True

tabs = st.tabs(
    [
        "📊 محرك الاستمثال الخطي وصياغة العلائق",
        "💰 بورصة أسعار الخامات وإدارة قاعدة البيانات",
        "📚 الموسوعة العلمية ودليل الإنتاج الحيواني",
        "📬 مركز الاتصال والدعم البرمجي",
    ]
)

# ==========================================
# التبويب الأول: محرك الاستمثال وصياغة العلائق
# ==========================================
with tabs[0]:
    st.markdown(
        "<div class='section-title'>⚙️ معطيات ومحددات التركيبة العلفية المستهدفة</div>",
        unsafe_allow_html=True,
    )

    col_inp1, col_inp2, col_inp3 = st.columns(3)
    with col_inp1:
        breed_selected = st.selectbox(
            "🐏 اختر فصيل أو سلالة الحيوان:",
            [
                "تسمين عجول (نمو سريع)",
                "أبقار حلابة (إنتاج كلي وعالي)",
                "ضأن وتسمين خراف مقوية",
                "دواجن تسمين (بادئ - نامي - ناهي)",
                "دواجن بياض وبشاير",
                "أرانب وسلالات تخصصية",
                "إبل وهجن سباق",
                "خيول وفروسية طاقة",
            ],
        )
        target_protein = st.slider(
            "🎯 نسبة البروتين المطلوبة في العليقة (%)", 10.0, 75.0, 18.0
        )

    with col_inp2:
        protein_mode = st.radio(
            "🧪 معيار حساب معطيات البروتين المعملي:",
            ["البروتين الخام القياسي (CP)", "البروتين المهضوم الفعلي (DP)"],
            help="يحسب الخوارزمية الحل بناءً على نسب الهضم المسجلة بالدليل لكل مادة علفية",
        )
        city_target = st.text_input(
            "📍 السوق الجغرافي / المدينة المستهدفة:", "الخرطوم / أم درمان"
        )

    with col_inp3:
        local_currency_symbol = st.text_input(
            "💱 رمز العملة المحلية للربط الحسابي:", "SDG"
        )
        exchange_rate = st.number_input(
            "📈 سعر صرف الدولار مقابل العملة المحلية:", min_value=1.0, value=600.0
        )

    # اختيار المكونات المتوفرة في المخازن المحلية حياً
    st.markdown(
        "<div class='section-title'>🌾 حدد الخامات المتوفرة حالياً في مخازن التجميع الحية</div>",
        unsafe_allow_html=True,
    )
    selected_ingredients = []
    live_prices = {}

    col_cat1, col_cat2 = st.columns(2)
    categories_keys = list(BIG_FEEDS_LIBRARY.keys())

    for idx, cat in enumerate(categories_keys):
        target_col = col_cat1 if idx % 2 == 0 else col_cat2
        with target_col:
            st.markdown(
                f"<div style='font-weight:bold; color:#2e7d32; margin-top:10px;'>{cat}</div>",
                unsafe_allow_html=True,
            )
            for item, specs in BIG_FEEDS_LIBRARY[cat].items():
                is_checked = st.checkbox(
                    f"{item} (سعره الحالي الافتراضي: ${specs['price']})",
                    value=True if "ذرة" in item or "كسب" in item or "ملح" in item else False,
                    key=f"check_{item}",
                )
                if is_checked:
                    selected_ingredients.append(item)
                    # تفعيل تعديل الأسعار حياً بناء على البورصة الحالية
                    live_p = st.number_input(
                        f"سعر الطن الحالي لـ [{item}] ($):",
                        min_value=0.0,
                        value=float(specs["price"]),
                        key=f"price_{item}",
                    )
                    live_prices[item] = live_p

    # الإضافات التلقائية المجبورة لحماية الحيوانات وصحتها العامة
    st.markdown(
        "<div class='section-title'>🛠️ محددات الخلطة الذكية والإضافات الجبرية والأمنية</div>",
        unsafe_allow_html=True,
    )
    col_add1, col_add2 = st.columns(2)

    with col_add1:
        st.write("**⚠️ إضافات الأمان والوقاية الحيوية (موصى بها لعام 2026):**")
        add_limestone = st.checkbox(
            "إجبار بودرة البلاط / الحجر الجيري لتوازن الكالسيوم (0.8%)", value=True
        )
        add_salt = st.checkbox("إجبار ملح الطعام لتوازن الصوديوم (0.4%)", value=True)
        add_toxin = st.checkbox(
            "إضافة مضاد السموم الفطرية لحماية الكبد (0.1%)", value=True
        )

    with col_add2:
        st.write("**🔬 إنزيمات حيوية ومحسنات معامل الهضم المستحث:**")
        add_phytase = st.checkbox(
            "تضمين إنزيم الفايتيز (تحرير الفسفور العضوي وتخفيض الفوسفات)",
            value=False,
        )
        add_nsp = st.checkbox(
            "تضمين إنزيم الـ NSP لمعادلة ألياف النخالة والشعير كلياً", value=False
        )

    # تجهيز النسب الإجبارية
    fixed_additives = {}
    if add_limestone:
        fixed_additives["الحجر الجيري (بودرة بلاط)"] = 0.8
    if add_salt:
        fixed_additives["ملح الطعام"] = 0.4
    if add_toxin:
        fixed_additives["مضاد سموم فطرية"] = 0.1

    auto_added_enzymes = {}
    if add_phytase:
        auto_added_enzymes["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05
    if add_nsp:
        auto_added_enzymes["إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)"] = 0.05

    # دمج المكونات الإجبارية التلقائية وتأمين مصفوفة الأسعار ضد KeyError
    all_fixed_additives = {**fixed_additives, **auto_added_enzymes}
    ingredient_prices = {**live_prices}
    for item in all_fixed_additives:
        if item not in selected_ingredients:
            if item in live_prices:  # تأمين الفحص الحرج لمنع توقف المحرك (KeyError)
                selected_ingredients.append(item)
                ingredient_prices[item] = live_prices.get(item, 40.0)

    # حساب وضغط الاستمثال الرياضي بواسطة Scipy Linear Programming
    if st.button("🚀 تشغيل خوارزمية الاستمثال الرياضي وحساب الخلطة الاقتصادية", type="primary", use_container_width=True):
        if len(selected_ingredients) < 2:
            st.warning("⚠️ يرجى اختيار مادتين علفيتين على الأقل لتشغيل مصفوفة الحل الرياضي.")
        else:
            # بناء القاموس المؤقت للمواصفات الحالية المستخدمة في الاستمثال
            current_specs = {}
            for cat in BIG_FEEDS_LIBRARY:
                for item, specs in BIG_FEEDS_LIBRARY[cat].items():
                    if item in selected_ingredients:
                        current_specs[item] = specs

            # مصفوفة التكاليف (الهدف هو التقليل لأدنى حد)
            c = [ingredient_prices.get(item, current_specs[item]["price"]) for item in selected_ingredients]

            # القيود والمحددات المتساوية وغير المتساوية
            A_eq = []
            b_eq = []
            A_ub = []
            b_ub = []

            # 1. القيد الكلي: مجموع النسب يجب أن يساوي 100% تماماً
            A_eq.append([1.0 for _ in selected_ingredients])
            b_eq.append(100.0)

            # 2. قيد البروتين المستهدف (الخام أو المهضوم)
            protein_coeffs = []
            for item in selected_ingredients:
                raw_cp = current_specs[item]["CP"]
                if protein_mode == "البروتين المهضوم الفعلي (DP)":
                    raw_cp = raw_cp * current_specs[item]["DC"]
                protein_coeffs.append(raw_cp)

            # قيد دقيق: يجب أن تلبي العليقة نسبة البروتين المستهدفة بدقة تامة
            A_eq.append(protein_coeffs)
            b_eq.append(target_protein)

            # 3. صياغة قيود الإضافات الإجبارية والمحسنات الحيوية
            for item, fixed_val in all_fixed_additives.items():
                if item in selected_ingredients:
                    idx = selected_ingredients.index(item)
                    row = [0.0 for _ in selected_ingredients]
                    row[idx] = 1.0
                    A_eq.append(row)
                    b_eq.append(fixed_val)

            # 4. قيود الحدود القصوى والدنيا لكل خامة من قاعدة البيانات ديناميكياً
            bounds = []
            for item in selected_ingredients:
                min_limit = current_specs[item].get("min", 0.0)
                max_limit = current_specs[item].get("max", 100.0)
                bounds.append((min_limit, max_limit))

            # تشغيل المحرك الرياضي الفعلي عن طريق طريقة الأجزاء الداخلية المتطورة
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

            if res.success:
                st.balloons()
                st.success("✅ تم حل المصفوفة بنجاح والتوصّل لأرخص تركيب علفي ممتاز تكنولوجياً!")

                # تجميع النتائج وعرضها
                computed_formula = {}
                for idx, item in enumerate(selected_ingredients):
                    val = res.x[idx]
                    if val > 0.001:
                        computed_formula[item] = val

                total_usd_cost = res.fun
                total_local_cost = total_usd_cost * exchange_rate

                # حساب معادل النشاء الكلي المحقق للوجبة
                computed_se_total = 0.0
                for item, pct in computed_formula.items():
                    computed_se_total += (pct / 100.0) * current_specs[item]["SE"]

                # العرض الفني الفخم للنتائج
                col_res1, col_res2 = st.columns([3, 2])

                with col_res1:
                    st.markdown("<div class='sack-tag'>", unsafe_allow_html=True)
                    st.markdown(f"<h3>🏷️ كرت مواصفات الخلطة المعتمد للطن الواحدة ({city_target})</h3>", unsafe_allow_html=True)
                    st.write(f"**🔬 الفصيل / الغرض الإنتاجي:** {breed_selected}")
                    st.write(f"**🎯 نسبة البروتين المحققة:** {target_protein}% ({protein_mode})")
                    st.write(f"**⚡ إجمالي معادل النشاء (الطاقة الإنتاجية SE):** {computed_se_total:.2f} وحدة طاقة")
                    st.write("---")
                    st.write("**⚖️ المقادير الوزنية لكل طن أعلاف (1000 كجم):**")

                    for k, v in computed_formula.items():
                        st.markdown(f"<div class='formula-item'>⚙️ {k} : {v:.2f}% &nbsp;&nbsp; ➔ &nbsp;&nbsp; ({v*10:.1f} كجم / طن)</div>", unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                with col_res2:
                    st.markdown("<div class='sack-tag' style='background-color:#e0f2f1; border-color:#004d40;'>", unsafe_allow_html=True)
                    st.markdown("<h3>💰 التحليل المالي وحساب الجدوى</h3>", unsafe_allow_html=True)
                    st.metric("تكلفة طن العلف الصافية ($):", f"${total_usd_cost:.2f}")
                    st.metric(f"التكلفة بالعملة المحلية ({local_currency_symbol}):", f"{total_local_cost:,.2f} {local_currency_symbol}")
                    st.write("---")
                    st.write("💡 *نصيحة مهندس عبد القادر:* هذه التركيبة تمثل الحل الرياضي الأرخص الذي يضمن تلبية الاحتياجات الكيماوية التامة دون هدر للأحماض الأمينية النقية.")
                    st.markdown("</div>", unsafe_allow_html=True)

                # توليد وتوفير تقرير PDF رسمي للطباعة والتصدير
                pdf_data = generate_pdf_report(
                    computed_formula,
                    target_protein,
                    breed_selected,
                    total_usd_cost,
                    city_target,
                    total_local_cost,
                    local_currency_symbol,
                    computed_se_total,
                    protein_mode,
                )
                st.download_button(
                    label="📥 تحميل تقرير الخلطة الرسمي (PDF) مطبوع الهوية",
                    data=pdf_data,
                    file_name=f"Tower_Scientific_Formula_{city_target}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                st.markdown("<div class='warning-card'>❌ فشل الاستمثال الرياضي: المعطيات والقيود الحالية متعارضة رياضياً ولا يمكن الوصول لحل مستقر بنسبة 100%. يرجى إتاحة مصادر بروتين أعلى (مثل الأكساب والأمبازات) أو خفض النسبة المستهدفة قليلاً لفك التعارض.</div>", unsafe_allow_html=True)

# ==========================================
# التبويب الثاني: بورصة أسعار الخامات وإدارة قاعدة البيانات
# ==========================================
with tabs[1]:
    st.markdown(
        "<div class='section-title'>📊 بورصة تحديث أسعار الخامات الحية وإدارة المدخلات</div>",
        unsafe_allow_html=True,
    )
    st.write(
        "شاشة مخصصة لإدارة الأسعار الافتراضية للخامات والبروتين ومعاملات الهضم التخصصية مباشرة في قاعدة البيانات المستقرة."
    )

    # لوحة الإشراف المتقدمة للمستشار (متاحة لصلاحية المالك فقط)
    if st.session_state["user_role"] == "owner":
        with st.expander("🛠️ لوحة الإشراف المتطور: إضافة وتعديل خامات الأعلاف في قاعدة البيانات (SQLite)"):
            st.write("يمكنك هنا تعديل التحليل الكيماوي لـ **كُسب عباد الشمس** أو أي خامة، أو إضافة خامة جديدة:")
            col_db_add1, col_db_add2, col_db_add3 = st.columns(3)
            with col_db_add1:
                new_ing_name = st.text_input("اسم الخامة العلفية الجديدة/الحالية للضبط:")
                new_ing_cat = st.selectbox("تصنيف الخامة:", list(BIG_FEEDS_LIBRARY.keys()))
            with col_db_add2:
                new_ing_price = st.number_input("السعر الافتراضي للطن ($):", min_value=0.0, value=250.0)
                new_ing_cp = st.number_input("البروتين الخام % (CP):", min_value=0.0, max_value=100.0, value=15.0)
            with col_db_add3:
                new_ing_dc = st.number_input("معامل الهضم (DC 0-1):", min_value=0.0, max_value=1.0, value=0.80)
                new_ing_se = st.number_input("معادل النشاء % (SE):", min_value=0.0, max_value=100.0, value=50.0)
            
            col_db_lim1, col_db_lim2, col_db_btn = st.columns([1,1,1])
            with col_db_lim1:
                new_ing_max = st.number_input("الحد الأقصى للاستخدام %:", min_value=0.0, max_value=100.0, value=100.0)
            with col_db_lim2:
                new_ing_min = st.number_input("الحد الأدنى للاستخدام %:", min_value=0.0, max_value=100.0, value=0.0)
            with col_db_btn:
                st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
                if st.button("💾 حفظ وتحديث المكون في قاعدة البيانات", type="primary", use_container_width=True):
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO Ingredients (name, category, price_per_ton, max_limit, min_limit)
                        VALUES (?, ?, ?, ?, ?)
                    """, (new_ing_name, new_ing_cat, new_ing_price, new_ing_max, new_ing_min))
                    
                    cursor.execute("SELECT id FROM Ingredients WHERE name=?", (new_ing_name,))
                    ing_id = cursor.fetchone()[0]
                    
                    cursor.execute("DELETE FROM Nutrient_Matrix WHERE ingredient_id=?", (ing_id,))
                    cursor.execute("""
                        INSERT INTO Nutrient_Matrix VALUES (?, ?, 0.0, 0.0, ?, ?)
                    """, (ing_id, new_ing_cp, new_ing_dc, new_ing_se))
                    conn.commit()
                    conn.close()
                    st.success(f"تم تحديث [{new_ing_name}] في قاعدة البيانات الحية بنجاح! يرجى إعادة تحميل الصفحة لرؤية التأثير.")
                    time.sleep(1)
                    st.rerun()

    # استعراض جدول الأسعار والمواصفات الحالي للمستخدم
    for cat in BIG_FEEDS_LIBRARY:
        st.markdown(f"#### 📦 {cat}")
        grid_data = []
        for k, v in BIG_FEEDS_LIBRARY[cat].items():
            grid_data.append(
                {
                    "الخامة": k,
                    "السعر الافتراضي ($)": v["price"],
                    "البروتين الخام (CP)": f"{v['CP']}%",
                    "معامل الهضم (DC)": v["DC"],
                    "معادل النشاء (SE)": v["SE"],
                    "الحد الأقصى %": v.get("max", 100.0),
                    "الحد الأدنى %": v.get("min", 0.0)
                }
            )
        st.table(pd.DataFrame(grid_data))

# ==========================================
# التبويب الثالث: الموسوعة العلمية ودليل الإنتاج الحيواني
# ==========================================
with tabs[2]:
    st.markdown(
        "<div class='section-title'>📚 كتاب دبلوم الإنتاج الحيواني وتركيب الأعلاف المتكامل (2026)</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='manual-book'>", unsafe_allow_html=True)

    st.markdown("<div class='book-chapter'>الفصل الأول: الهضم والاستفادة الحيوية من المواد الغذائية</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='book-body'>يرتبط نجاح العليقة ارتباطاً وثيقاً بـ <b>معامل الهضم الفعلي (DC)</b> وليس فقط بنسبة البروتين الخام الكلي. على سبيل المثال، يمتلك كسب فول الصويا معامل هضم يتجاوز 0.90 بينما ينخفض معامل هضم مخلفات المعاصر لبعض الأكساب رديئة التصنيع إلى أقل من 0.70، مما يجعل حساب الكلفة بناءً على وحدة النيتروجين المهضوم الحقيقي هو المعيار الاقتصادي الأدق لعنابر التسمين الحديثة لعام 2026.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='book-chapter'>الفصل الثاني: معادل النشاء (Starch Equivalent) وحسابات الطاقة الإنتاجية</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='book-body'>يُعد معيار <b>معادل النشاء (SE)</b> الركيزة الألمانية الكلاسيكية والمطورة لتقدير كمية الطاقة الصافية المتاحة للإنتاج والنمو. تعتمد الحبوب الكبرى مثل الذرة الصفراء وجريش الأرز على نسب SE مرتفعة تتراوح بين 80-82، في حين تعمل المواد الماصة للمولاس والمواد المالئة على توفير بيئة بيولوجية متزنة للكرش دون التسبب في حالات الحامضية (Acidosis).</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='book-chapter'>الفصل الثالث: دور الإنزيمات المضافة والأحماض الأمينية البلورية</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='book-body'>تساهم إضافة الأحماض الأمينية النقية مثل <i>L-Lysine</i> و <i>DL-Methionine</i> في تخفيض الفائض من النيتروجين المطروح في البيئة، مما يساهم في تقليل الإجهاد الحراري داخل العنابر المغلقة. كما أن دمج الفايتيز وإنزيمات الـ NSP يحسن من الاستفادة الكلية للطاقة المكتنزة في جدران الخلايا النباتية بنسبة تصل إلى 12% إضافية.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# التبويب الرابع: مركز الاتصال والدعم البرمجي
# ==========================================
with tabs[3]:
    st.markdown(
        "<div class='section-title'>📬 إدارة المنصة والتواصل البرمجي المباشر مع م. عبد القادر</div>",
        unsafe_allow_html=True,
    )

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.markdown("### 🛟 الدعم الفني وتحديثات النظام")
        st.write(
            "هذه المنصة مخصصة ومدارة بالكامل تحت إشراف المستشار م. عبد القادر إسماعيل تاور لخدمة مشاريع التسمين وإنتاج الألبان."
        )

        whatsapp_msg = urllib.parse.quote(
            "السلام عليكم م. عبد القادر، أرغب في الاستفسار عن استشارة تخصصية حول تركيبات الأعلاف لعام 2026."
        )
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={whatsapp_msg}"

        st.markdown(
            f'<a href="{wa_url}" target="_blank"><button style="background-color: #25D366; color: white; padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 1.1rem; width: 100%;">💬 تواصل مباشر عبر واتساب المستشار الفني</button></a>',
            unsafe_allow_html=True,
        )

        st.markdown("<div style='padding-top:15px;'></div>", unsafe_allow_html=True)

        st.markdown(
            f'<a href="{GOOGLE_FORM_URL}" target="_blank"><button style="background-color: #4285F4; color: white; padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 1.1rem; width: 100%;">📝 حجز استشارة أو تقديم طلب تحليل معملي</button></a>',
            unsafe_allow_html=True,
        )

    with col_c2:
        st.markdown("### 🔑 السورس كود البرمجي (لصلاحيات الإدارة)")
        st.write(
            "يمكن للمالك أو المهندس المسؤول طلب إرسال النسخة البرمجية الحالية (Python Script) مباشرة إلى البريد الإلكتروني المعتمد كمستند دفعات احتياطية مجدولة."
        )

        target_mail = st.text_input(
            "📬 أدخل البريد الإلكتروني المستلم:", OWNER_EMAIL
        )
        if st.button("📧 إرسال السورس كود المحدث تلقائياً", type="secondary", use_container_width=True):
            with st.spinner("جاري الاتصال بخادم الـ SMTP وتشفير الملف..."):
                success = send_code_to_mail(target_mail)
                if success:
                    st.success(
                        f"🚀 تم إرسال السورس كود الكامل بنجاح إلى البريد: {target_mail}"
                    )

st.markdown("</div>", unsafe_allow_html=True)
