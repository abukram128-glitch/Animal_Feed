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
# 0. تأسيس وإدارة قاعدة البيانات
# ==========================================
DB_NAME = "tower_scientific.db"

def init_database():
    """إنشاء الجداول وضخ البيانات الأساسية إذا لم تكن موجودة مسبقاً"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        price_per_ton REAL NOT NULL,
        max_limit REAL DEFAULT 100.0,
        min_limit REAL DEFAULT 0.0
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Nutrient_Matrix (
        ingredient_id INTEGER,
        crude_protein REAL DEFAULT 0.0,
        lysine REAL DEFAULT 0.0,
        methionine REAL DEFAULT 0.0,
        digestibility_coeff REAL DEFAULT 1.0,
        starch_equivalent REAL DEFAULT 0.0,
        calcium REAL DEFAULT 0.0,
        phosphorus REAL DEFAULT 0.0,
        FOREIGN KEY (ingredient_id) REFERENCES Ingredients(id) ON DELETE CASCADE
    )
    ''')
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM Ingredients")
    if cursor.fetchone()[0] == 0:
        raw_library = {
            "🌾 الحبوب ومصادر الطاقة الكبرى": {
                "ذرة صفراء": {"CP": 8.5, "lys": 0.24, "met": 0.17, "DC": 0.85, "SE": 80.0, "Ca": 0.02, "P": 0.28, "price": 230.0},
                "ذرة بيضاء": {"CP": 8.8, "lys": 0.23, "met": 0.16, "DC": 0.83, "SE": 78.0, "Ca": 0.02, "P": 0.27, "price": 225.0},
                "شعير مطحون": {"CP": 11.5, "lys": 0.36, "met": 0.19, "DC": 0.80, "SE": 71.0, "Ca": 0.06, "P": 0.35, "price": 210.0},
                "سورجم (فتريتة)": {"CP": 10.0, "lys": 0.22, "met": 0.15, "DC": 0.78, "SE": 70.0, "Ca": 0.04, "P": 0.30, "price": 195.0},
                "قمح محلي مصنّع": {"CP": 12.0, "lys": 0.32, "met": 0.21, "DC": 0.85, "SE": 75.0, "Ca": 0.05, "P": 0.36, "price": 240.0},
                "جريش أرز رزاز": {"CP": 7.8, "lys": 0.28, "met": 0.20, "DC": 0.82, "SE": 82.0, "Ca": 0.04, "P": 0.25, "price": 230.0},
                "دخن محلي غزير": {"CP": 11.0, "lys": 0.30, "met": 0.22, "DC": 0.75, "SE": 68.0, "Ca": 0.05, "P": 0.32, "price": 230.0},
                "شوفان علفي": {"CP": 11.0, "lys": 0.40, "met": 0.18, "DC": 0.76, "SE": 62.0, "Ca": 0.10, "P": 0.35, "price": 230.0},
            },
            "🌱 الأكساب وأمبازات مصادر البروتين العالي": {
                "أمباز الفول السوداني (كسب)": {"CP": 46.0, "lys": 1.60, "met": 0.52, "DC": 0.88, "SE": 73.0, "Ca": 0.20, "P": 0.60, "price": 460.0},
                "كسب فول صويا 44%": {"CP": 44.0, "lys": 2.70, "met": 0.62, "DC": 0.90, "SE": 74.0, "Ca": 0.29, "P": 0.65, "price": 440.0},
                "كسب فول صويا 48%": {"CP": 48.0, "lys": 2.90, "met": 0.67, "DC": 0.91, "SE": 76.0, "Ca": 0.30, "P": 0.68, "price": 480.0},
                "كسب عباد الشمس 36%": {"CP": 36.0, "lys": 1.20, "met": 0.75, "DC": 0.76, "SE": 42.0, "Ca": 0.40, "P": 0.90, "price": 310.0},
                "كسب بذور القطن (مقشور)": {"CP": 41.0, "lys": 1.75, "met": 0.64, "DC": 0.78, "SE": 55.0, "Ca": 0.25, "P": 0.95, "price": 290.0},
                "كسب بذور الكتان": {"CP": 32.0, "lys": 1.15, "met": 0.60, "DC": 0.82, "SE": 65.0, "Ca": 0.40, "P": 0.85, "price": 350.0},
                "كسب السمسم المحسن": {"CP": 42.0, "lys": 1.25, "met": 1.10, "DC": 0.84, "SE": 70.0, "Ca": 2.00, "P": 1.10, "price": 350.0},
                "كسب جلوتين الذرة 60%": {"CP": 60.0, "lys": 1.02, "met": 1.45, "DC": 0.92, "SE": 85.0, "Ca": 0.05, "P": 0.50, "price": 350.0},
                "كسب نواة النخيل": {"CP": 16.0, "lys": 0.62, "met": 0.31, "DC": 0.65, "SE": 52.0, "Ca": 0.25, "P": 0.60, "price": 350.0},
            },
            "🚜 المخلفات الزراعية والصناعية والمواد المالئة": {
                "نخالة قمح (ردة)": {"CP": 15.0, "lys": 0.58, "met": 0.23, "DC": 0.72, "SE": 45.0, "Ca": 0.14, "P": 1.20, "price": 150.0},
                "البرسيم الجاف (الدريس)": {"CP": 16.5, "lys": 0.75, "met": 0.28, "DC": 0.60, "SE": 35.0, "Ca": 1.40, "P": 0.25, "price": 170.0},
                "مولاس قصب السكر": {"CP": 4.0, "lys": 0.05, "met": 0.02, "DC": 0.95, "SE": 50.0, "Ca": 0.80, "P": 0.10, "price": 120.0},
                "تبن قمح ناعم": {"CP": 3.2, "lys": 0.08, "met": 0.04, "DC": 0.35, "SE": 18.0, "Ca": 0.18, "P": 0.06, "price": 230.0},
                "قشر فول سوداني مطحون": {"CP": 5.0, "lys": 0.12, "met": 0.05, "DC": 0.30, "SE": 15.0, "Ca": 0.12, "P": 0.08, "price": 230.0},
                "سرسة الأرز المطحونة": {"CP": 2.5, "lys": 0.06, "met": 0.03, "DC": 0.25, "SE": 12.0, "Ca": 0.08, "P": 0.10, "price": 230.0},
                "بقايا تفل البنجر المجفف": {"CP": 8.0, "lys": 0.42, "met": 0.12, "DC": 0.75, "SE": 58.0, "Ca": 0.70, "P": 0.10, "price": 230.0},
                "مخلفات مصانع البسكويت": {"CP": 9.5, "lys": 0.28, "met": 0.15, "DC": 0.88, "SE": 76.0, "Ca": 0.05, "P": 0.30, "price": 230.0},
                "سيلاج ذرة كامل متكامل": {"CP": 8.0, "lys": 0.22, "met": 0.14, "DC": 0.68, "SE": 50.0, "Ca": 0.25, "P": 0.22, "price": 230.0},
            },
            "🧬 مصادر البروتين الحيواني والمركزات دقيقة الخلط": {
                "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "lys": 4.50, "met": 1.65, "DC": 0.85, "SE": 65.0, "Ca": 5.00, "P": 3.00, "price": 850.0},
                "مسحوق أسماك فاخر (72%)": {"CP": 72.0, "lys": 5.40, "met": 2.10, "DC": 0.90, "SE": 72.0, "Ca": 4.50, "P": 2.80, "price": 850.0},
                "مسحوق اللحم والعظم": {"CP": 50.0, "lys": 2.60, "met": 0.70, "DC": 0.75, "SE": 50.0, "Ca": 10.00, "P": 5.00, "price": 850.0},
                "مركزات دواجن وسمان": {"CP": 40.0, "lys": 2.50, "met": 1.20, "DC": 0.85, "SE": 60.0, "Ca": 4.00, "P": 2.00, "price": 650.0},
                "مركزات خيول ومجترات": {"CP": 36.0, "lys": 1.80, "met": 0.65, "DC": 0.80, "SE": 55.0, "Ca": 3.00, "P": 1.50, "price": 600.0},
            },
            "🧪 الأحماض الأمينية البلورية النقية": {
                "ليسين نقي (L-Lysine)": {"CP": 94.0, "lys": 78.0, "met": 0.0, "DC": 1.00, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 230.0},
                "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "lys": 0.0, "met": 99.0, "DC": 1.00, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 230.0},
                "ثريونين نقي (L-Threonine)": {"CP": 72.0, "lys": 0.0, "met": 0.0, "DC": 1.00, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 230.0},
                "تريبتوفان نقي (L-Tryptophan)": {"CP": 85.0, "lys": 0.0, "met": 0.0, "DC": 1.00, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 230.0},
                "فالين نقي (L-Valine)": {"CP": 90.0, "lys": 0.0, "met": 0.0, "DC": 1.00, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 230.0},
            },
            "🔬 الإنزيمات والبريمكسات والإضافات التخصصية": {
                "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 230.0},
                "بريمكس بياض وبشاير": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 230.0},
                "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 230.0},
                "بريمكس خيول وفروسية": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 230.0},
                "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 230.0},
                "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 230.0},
                "كبريتات الحديدوز (معادل الجوسيبول)": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 230.0},
                "مستخلص الخمائر والجدر الخلوية (MOS)": {"CP": 12.0, "lys": 0.30, "met": 0.10, "DC": 0.50, "SE": 10.0, "Ca": 0.0, "P": 0.0, "price": 230.0},
            },
            "🪨 الأملاح والمعادن ومنظمات الهضم": {
                "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "Ca": 38.0, "P": 0.0, "price": 40.0},
                "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "Ca": 22.0, "P": 18.0, "price": 280.0},
                "ملح الطعام": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 30.0},
                "مضاد سموم فطرية": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 950.0},
                "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 340.0},
                "أكسيد المغنيسيوم العلفي": {"CP": 0.0, "lys": 0.0, "met": 0.0, "DC": 0.0, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 230.0},
                "يوريا علفية محصنة (المجترات فقط)": {"CP": 287.0, "lys": 0.0, "met": 0.0, "DC": 0.95, "SE": 0.0, "Ca": 0.0, "P": 0.0, "price": 230.0},
            }
        }
        for cat, items in raw_library.items():
            for name, nut in items.items():
                cursor.execute("INSERT OR IGNORE INTO Ingredients (name, category, price_per_ton) VALUES (?, ?, ?)", (name, cat, nut["price"]))
                ing_id = cursor.lastrowid if cursor.lastrowid else cursor.execute("SELECT id FROM Ingredients WHERE name=?", (name,)).fetchone()[0]
                cursor.execute("INSERT INTO Nutrient_Matrix VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (ing_id, nut["CP"], nut["lys"], nut["met"], nut["DC"], nut["SE"], nut["Ca"], nut["P"]))
        conn.commit()
    conn.close()

init_database()

def load_feeds_from_db():
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT i.name, i.category, i.price_per_ton, i.max_limit, i.min_limit,
           n.crude_protein, n.lysine, n.methionine, n.digestibility_coeff, n.starch_equivalent, n.calcium, n.phosphorus
    FROM Ingredients i JOIN Nutrient_Matrix n ON i.id = n.ingredient_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    structured_library = {}
    for cat in df['category'].unique():
        structured_library[cat] = {}
        sub_df = df[df['category'] == cat]
        for _, row in sub_df.iterrows():
            structured_library[cat][row['name']] = {
                "CP": row['crude_protein'], "lys": row['lysine'], "met": row['methionine'],
                "DC": row['digestibility_coeff'], "SE": row['starch_equivalent'], 
                "Ca": row['calcium'], "P": row['phosphorus'],
                "price": row['price_per_ton'], "max": row['max_limit'], "min": row['min_limit']
            }
    return structured_library

# ==========================================
# 1. إعدادات المنصة الرسمية والمظهر
# ==========================================
st.set_page_config(
    page_title="منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف",
    page_icon="🌾",
    layout="wide",
)

CODES_DB = {
    "202687": "owner",  
    "2020": "specialist",  
    "2026": "breeder",  
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
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg["Subject"] = "🌾 السورس كود الكامل والمطور - منصة تاور العلمية"
    body = "السلام عليكم م. عبد القادر،\n\nمرفق النسخة المستقرة المحدثة برمجياً وفنياً لعام 2026.\n\nتحياتي الهندسية."
    msg.attach(MIMEText(body, "plain", "utf-8"))
    try:
        current_file = __file__
        with open(current_file, "r", encoding="utf-8") as f:
            code_content = f.read()
        attachment = MIMEText(code_content, "plain", "utf-8")
        attachment.add_header("Content-Disposition", "attachment", filename="tower_scientific_platform.py")
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
    return get_display(reshaped_text)

def generate_pdf_report(formula, target_protein, breed, cost, city, local_cost, local_sym, computed_se, mode_label):
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
    p.drawString(100, 800, fix_arabic_text("تقرير: منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف"))
    p.setFont(font_name, 12)
    p.drawString(100, 760, fix_arabic_text(f"المشرف العام: الاختصاصي م. عبد القادر إسماعيل تاور"))
    p.drawString(100, 740, fix_arabic_text(f"الموقع / السوق الجغرافي المستهدف: {city}"))
    p.drawString(100, 720, fix_arabic_text(f"الفصيل / السلالة الحيوانية: {breed}"))
    p.drawString(100, 700, fix_arabic_text(f"معيار حساب البروتين المستهدف: {mode_label}"))
    p.drawString(100, 680, fix_arabic_text(f"نسبة البروتين المستهدفة المحققة: {target_protein}%"))
    p.drawString(100, 660, fix_arabic_text(f"إجمالي معادل النشاء المحقق (SE): {computed_se:.2f} وحدة طاقة"))
    p.drawString(100, 640, fix_arabic_text(f"التكلفة المحسوبة للطن: ${cost:.2f} ({local_cost:,.2f} {local_sym})"))

    p.setFont(font_name, 14)
    p.drawString(100, 600, fix_arabic_text("المقادير الدقيقة المعتمدة لتركيب خلطة الطن الواحدة:"))
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
    p.drawString(100, 50, fix_arabic_text("تم التوليد تلقائياً بواسطة منصة تاور العلمية © 2026 تحت إشراف م. عبد القادر إسماعيل تاور"))
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
# 2. بوابة الدخول وحماية النظام
# ==========================================
if "approved" not in st.session_state:
    st.session_state["approved"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "login_welcome_shown" not in st.session_state:
    st.session_state["login_welcome_shown"] = False

if not st.session_state["approved"]:
    st.markdown('<div class="main-box" style="max-width: 500px; margin: 100px auto; direction: rtl;">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #2E7D32; text-align:center;'>🔒 بوابـة الدخـول الذكيـة</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</p>", unsafe_allow_html=True)

    input_code = st.text_input("🔑 أدخل كود الدخول الخاص بك:", type="password")

    if st.button("تسجيل الدخول 🔓", type="primary", use_container_width=True):
        input_code_stripped = input_code.strip()
        if input_code_stripped in CODES_DB:
            st.session_state["approved"] = True
            st.session_state["user_role"] = CODES_DB[input_code_stripped]
            st.session_state["login_welcome_shown"] = False
            st.rerun()
        else:
            st.error("❌ الكود الذي أدخلته غير صحيح! يرجى المحاولة مرة أخرى.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

if not st.session_state["login_welcome_shown"]:
    if st.session_state["user_role"] == "owner":
        st.toast("👋 مرحباً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور", icon="👑")
    elif st.session_state["user_role"] == "specialist":
        st.toast("🔬 أهلاً بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني.", icon="👨‍🔬")
    elif st.session_state["user_role"] == "breeder":
        st.toast("🚜 أهلاً وسهلاً بإخواننا المربين، شركاء النجاح.", icon="🌾")
    st.session_state["login_welcome_shown"] = True

BIG_FEEDS_LIBRARY = load_feeds_from_db()

if "inventory" not in st.session_state:
    st.session_state["inventory"] = {}
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        for ing in items:
            st.session_state["inventory"][ing] = 25.0

if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين / محسن ($)": 1350.0,
        "أبقار كنانة وبطانة محلية ($)": 900.0,
        "ضأن وستيرلنغ / محلي ($)": 180.0,
        "ماعز نوبي وصحراوي ($)": 130.0,
        "خيول عربية أصيلة وهجين ($)": 4500.0,
        "كتكوت لاحم عمر يوم ($)": 0.65,
        "دجاج بياض عمر البشاير ($)": 5.50,
    }

if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري صافي ($)": 7.50,
        "كيلو لحم ضأن طازج ($)": 9.00,
        "كيلو لحم دجاج لاحم صافي ($)": 3.80,
        "طبق بيض مائدة 30 بيضة ($)": 4.20,
        "رطل / لتر حليب خام ($)": 0.90,
        "كيلو جبن أبيض محلي ($)": 5.00,
        "كيلو جبن جاف / شيدر ($)": 8.50,
    }

if "shared_comments" not in st.session_state:
    st.session_state["shared_comments"] = (
        "• [توجيه الاختصاصي م. عبد القادر إسماعيل تاور]: يرجى من جميع الزملاء إضافة تعليقاتهم هنا لتبادل الخبرات التركيبية.\n"
        "• [ملاحظة مختص]: تم مراجعة جودة كسب زهرة الشمس المتاح حالياً بالأسواق ونوصي بضبط ألياف الخيل بناءً عليه.\n"
    )

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "LIBYA": {"rate": 4.80, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"},
    "باقي دول العالم / البورصة المفتوحة": {"rate": 1.0, "sym": "USD"},
}

def get_adjusted_market_data(country, state_or_region, city):
    feed_prices = {}
    for cat in BIG_FEEDS_LIBRARY.values():
        for ing, data in cat.items():
            feed_prices[ing] = data["price"]

    multiplier = 1.0
    if country == "السودان":
        multiplier = 1.15
        if "كردفان" in state_or_region or state_or_region == "إقليم النيل الأزرق":
            multiplier = 1.20
            if "سورجم (فتريتة)" in feed_prices: feed_prices["سورجم (فتريتة)"] *= 0.85
            if "أمباز الفول السوداني (كسب)" in feed_prices: feed_prices["أمباز الفول السوداني (كسب)"] *= 0.85
        elif state_or_region in ["ولاية القضارف", "ولاية الجزيرة"]:
            if "سورجم (فتريتة)" in feed_prices: feed_prices["سورجم (فتريتة)"] *= 0.82
            if "أمباز الفول السوداني (كسب)" in feed_prices: feed_prices["أمباز الفول السوداني (كسب)"] *= 0.88
    elif country == "LIBYA":
        multiplier = 1.10
        if city == "طبرق":
            multiplier = 1.06
    elif country == "مصر":
        multiplier = 1.04

    for k in feed_prices:
        feed_prices[k] *= multiplier
    return feed_prices

ANIMAL_IMAGES_RESOURCES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600",
    "سمان": "https://images.unsplash.com/photo-1516467508483-a7212febe31a?q=80&w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600",
}

if "active_formula" not in st.session_state:
    st.session_state["active_formula"] = {"ذرة صفراء": 60.0, "كسب فول صويا 44%": 35.0}
if "active_cp_tag" not in st.session_state:
    st.session_state["active_cp_tag"] = 12.0
if "active_se_tag" not in st.session_state:
    st.session_state["active_se_tag"] = 65.0
if "active_breed_tag" not in st.session_state:
    st.session_state["active_breed_tag"] = "سلالة عامة"
if "active_animal_img" not in st.session_state:
    st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES["عام"]
if "active_stage_title" not in st.session_state:
    st.session_state["active_stage_title"] = "إنتاج عام"
if "computed_ton_cost" not in st.session_state:
    st.session_state["computed_ton_cost"] = 280.0

# ==========================================
# 4. بناء الواجهة الرئيسية للمنصة
# ==========================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

col_logout_space, col_user_status = st.columns([0.7, 0.3])
with col_user_status:
    role_arabic = {
        "owner": "الاختصاصي م. عبد القادر إسماعيل تاور 👑",
        "specialist": "المختص والزملاء 👨‍🔬",
        "breeder": "المربي 🌾",
    }[st.session_state["user_role"]]
    st.markdown(f"<div style='text-align: left; font-size:0.9rem; color:#555;'>الحساب: <b>{role_arabic}</b></div>", unsafe_allow_html=True)
    if st.button("تسجيل الخروج 🚪", use_container_width=True):
        st.session_state["approved"] = False
        st.session_state["user_role"] = None
        st.rerun()

col_logo, col_title = st.columns([0.3, 0.7])
with col_logo:
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" class="profile-img-style">', unsafe_allow_html=True)
    else:
        st.markdown(f'<img src="{ANIMAL_IMAGES_RESOURCES["عام"]}" class="profile-img-style">', unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='color: #1b5e20; text-align:right; margin-bottom:0;'>منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1565C0; text-align:right; font-size:1.2rem; margin-top:5px; margin-bottom:0;'>محرك الاستمثال الخطي المتقدم القائم على البروتين المهضوم (DP) ومعادل النشاء (SE)</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #c62828; text-align:right; font-weight: bold; margin-top: 5px;'>الاختصاصي م. عبد القادر إسماعيل تاور</h3>", unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)

if st.session_state["user_role"] == "owner":
    st.markdown("<div style='background-color: #eff6ff; padding: 15px; border-radius: 8px; border-right: 5px solid #1d4ed8; text-align: right; direction: rtl; margin-bottom: 20px;'><b>👑 أهلاً بك في منصتك، الاختصاصي م. عبد القادر إسماعيل تاور. نظام التوازن الدقيق بالبروتين المهضوم ومعادل النشاء قيد التشغيل الآن بكفاءة متناهية.</b></div>", unsafe_allow_html=True)
elif st.session_state["user_role"] == "specialist":
    st.markdown("<div style='background-color: #f0fdf4; padding: 15px; border-radius: 8px; border-right: 5px solid #16a34a; text-align: right; direction: rtl; margin-bottom: 20px;'><b>🔬 مرحباً بكم في منصة تركيب وتحليل الأعلاف الذكية. يسعد الاختصاصي م. عبد القادر إسماعيل تاور بالترحيب بالزملاء من الأطباء البيطريين ومختصي الإنتاج الحيواني.</b></div>", unsafe_allow_html=True)
elif st.session_state["user_role"] == "breeder":
    st.markdown("<div style='background-color: #fffbeb; padding: 15px; border-radius: 8px; border-right: 5px solid #d97706; text-align: right; direction: rtl; margin-bottom: 20px;'><b>🚜 أهلاً وسهلاً بكم في منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف. نرحب بإخواننا المربين.</b></div>", unsafe_allow_html=True)

if st.session_state["user_role"] in ["owner", "specialist"]:
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية الكبرى",
        "📊 بورصة الأسعار وإدارة الخامات",
        "🏭 إدارة المستودعات والخصم التلقائي",
        "🧾 التسويق وفواتير حركة البيع",
        "🖨️ مصمم بطاقات الديباجة والدعاية",
        "💬 خانة تعليقات المختصين والزملاء",
        "📖 دليل المستخدم (الكتيب الرقمي)",
    ]
else:
    tabs_titles = [
        "🔬 النمذجة والحسابات العلفية الكبرى",
        "📖 دليل المستخدم (الكتيب الرقمي)",
    ]

tabs = st.tabs(tabs_titles)

# -------------------------------------------------------------------------
# التبويب الأول: الحسابات والتركيبات
# -------------------------------------------------------------------------
with tabs[0]:
    sub_tab_formulator, sub_tab_analyzer = st.tabs([
        "🎯 تركيب علفة نموذجية (أقل تكلفة بالبروتين المهضوم)",
        "🔬 مختبر تحليل وفحص الأعلاف الجاهزة",
    ])

    with sub_tab_formulator:
        st.markdown('<div class="section-title">🌍 أولاً: تحديد الموقع الجغرافي وبورصة الأسعار</div>', unsafe_allow_html=True)
        col_country, col_state, col_city = st.columns(3)
        with col_country:
            user_country = st.selectbox("اختر دولة المربي:", ["السودان", "LIBYA", "مصر", "باقي دول العالم / البورصة المفتوحة"])

        c_info = EXCHANGE_RATES.get(user_country, {"rate": 1.0, "sym": "USD"})
        local_rate = c_info["rate"]
        local_sym = c_info["sym"]

        chosen_state = "عام"
        with col_state:
            if user_country == "السودان":
                chosen_state = st.selectbox("اختر الولاية السودانية المحدثة:", ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف", "ولاية شمال كردفان", "ولاية جنوب كردفان", "ولاية غرب كردفان", "إقليم النيل الأزرق", "ولاية البحر الأحمر", "ولاية نهر النيل"])
            elif user_country == "LIBYA":
                chosen_state = st.selectbox("اختر الإقليم الجغرافي:", ["المنطقة الشرقية", "المنطقة الغربية", "المنطقة الجنوبية"])
            else:
                chosen_state = st.selectbox("الإقليم الإداري:", ["المركز الرئيسي العالمي", "الأسواق المفتوحة"])

        with col_city:
            if user_country == "السودان":
                if chosen_state == "ولاية الخرطوم":
                    user_city = st.selectbox("اختر المدينة:", ["الخرطوم", "أم درمان", "بحري"])
                elif chosen_state == "ولاية الجزيرة":
                    user_city = st.selectbox("اختر المدينة:", ["ود مدني", "الحصاحيصا", "المناقل"])
                elif chosen_state == "ولاية القضارف":
                    user_city = st.selectbox("اختر المدينة:", ["القضارف المدينة", "الفاو"])
                else:
                    user_city = st.selectbox("اختر المدينة:", ["شندي", "عطبرة", "الأبيض"])
            elif user_country == "LIBYA":
                if chosen_state == "المنطقة الشرقية":
                    user_city = st.selectbox("اختر المدينة الليبية:", ["طبرق", "بنغازي", "البيضاء", "درنة"])
                elif chosen_state == "المنطقة الغربية":
                    user_city = st.selectbox("اختر المدينة الليبية:", ["طرابلس", "مصراتة", "الزاوية"])
                else:
                    user_city = st.selectbox("اختر المدينة الليبية:", ["سبها", "مرزق", "غات"])
            else:
                user_city = st.text_input("اكتب اسم المدينة العالمية يدوياً:", "طبرق")

        live_prices = get_adjusted_market_data(user_country, chosen_state, user_city)

        st.markdown('<div class="section-title">⚖️ ثانياً: اختيار القطاع والنوع والإنتاجية المستهدفة</div>', unsafe_allow_html=True)
        col_sec, col_sub, col_prod = st.columns(3)
        with col_sec:
            main_sector = st.selectbox("اختر القطاع الإنتاجي الرئيسي:", ["الأغنام وسلالاتها 🐏", "الماعز وسلالاتها", "الأبقار وسلالاتها", "الخيول والفروسية", "الطيور والسمان", "الأسماك والأحياء المائية"])

        show_measurements, weight_factor, feed_factor, default_dp, default_se, dynamic_img_key, chosen_concentrate = False, 10000, 0.02, 11.0, 60.0, "عام", None
        default_lys, default_met = 1.10, 0.45  

        gender_option = "إناث"
        if main_sector in ["الأغنام وسلالاتها 🐏", "الماعز وسلالاتها"]:
            with col_sec:
                gender_option = st.radio("حدد الجنس:", ["ذكور (تسمين)", "إناث (حليب / أمهات)"], horizontal=True)

        with col_sub:
            if main_sector == "الأغنام وسلالاتها 🐏":
                sub_type = st.selectbox("السلالة المستهدفة:", ["الضأن الصحراوي السوداني", "البربري", "النعيمي", "سلالات محلية / هجين"])
                dynamic_img_key = "أغنام"
                show_measurements = True; weight_factor = 15500; feed_factor = 0.035; chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الماعز وسلالاتها":
                sub_type = st.selectbox("السلالة المستهدفة:", ["الماعز النوبي السوداني", "الماعز الصحراوي", "بور / محسن"])
                dynamic_img_key = "ماعز"
                show_measurements = True; weight_factor = 15000; feed_factor = 0.032; chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الأبقار وسلالاتها":
                sub_type = st.selectbox("السلالة المستهدفة:", ["كنانة (سوداني)", "بطانة (مدر)", "هولشتاين / محسن"])
                dynamic_img_key = "أبقار"
                show_measurements = True; weight_factor = 10838; feed_factor = 0.025; chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الخيول والفروسية":
                sub_type = st.selectbox("السلالة المستهدفة:", ["خيل عربي أصيل", "ثوروبريد", "خيول محلية هجين"])
                dynamic_img_key = "خيول"
                show_measurements = True; weight_factor = 11877; feed_factor = 0.022; chosen_concentrate = "مركزات خيول ومجترات"
            elif main_sector == "الطيور والسمان":
                sub_type = st.selectbox("نوع الطيور:", ["طائر السمان (Quail)", "دواجن لاحم (Broiler)", "دواجن بياض (Layer)"])
                dynamic_img_key = "سمان" if "السمان" in sub_type else "دواجن"; chosen_concentrate = "مركزات دواجن وسمان"
            else:
                sub_type = st.selectbox("نوع الأسماك:", ["البلطي النيلي (Tilapia)", "القرموط"])
                dynamic_img_key = "أسماك"; chosen_concentrate = "مسحوق أسماك (Fishmeal 60%)"

        with col_prod:
            if main_sector == "الأغنام وسلالاتها 🐏":
                if gender_option == "ذكور (تسمين)":
                    prod_stage = st.selectbox("خط إنتاج الذكور:", ["تسمين حملان مكثف (نمو سريع)", "حملان تيد / كباش جاهزة"])
                    default_dp = 12.0 if "مكثف" in prod_stage else 9.5; default_se = 64.0 if "مكثف" in prod_stage else 58.0
                else:
                    prod_stage = st.selectbox("خط إنتاج الإناث والأمهات:", ["نعاج مرضعات (إدرار عالي)", "نعاج حامل (الفترة الأخيرة)", "نعاج جافة / صيانة"])
                    default_dp = 12.8 if "مرضعات" in prod_stage else (10.5 if "حامل" in prod_stage else 8.0)
                    default_se = 66.0 if "مرضعات" in prod_stage else (60.0 if "حامل" in prod_stage else 50.0)
            elif main_sector == "الأبقار وسلالاتها":
                prod_stage = st.selectbox("نوع الإنتاج:", ["إنتاج حليب وغزارة إدرار", "تسمين عجول مكثف"])
                default_dp = 12.5 if "حليب" in prod_stage else 10.0; default_se = 68.0 if "حليب" in prod_stage else 65.0
            else:
                prod_stage = st.text_input("مرحلة الإنتاج الحالية:", "إنتاج عام")

        if show_measurements:
            st.markdown('<div class="section-title">📐 Critical Measurements Area | تقدير الأوزان والاحتياجات حَقلياً</div>', unsafe_allow_html=True)
            col_h, col_l, col_ag = st.columns(3)
            with col_h: h_girth = st.number_input("📏 محيط الصدر خلف الكوع (سم):", value=150.0 if "الأبقار" in main_sector else 75.0)
            with col_l: b_length = st.number_input("📏 طول الجسم الجسدي (سم):", value=130.0 if "الأبقار" in main_sector else 65.0)
            with col_ag: a_months = st.number_input("⏳ عمر الحيوان التقديري (أشهر):", value=12)
            calc_weight = (h_girth**2 * b_length) / weight_factor
            req_feed_kg = calc_weight * feed_factor
            st.success(f"📊 الوزن الحيوي المتوقع: **{calc_weight:.1f} كجم** | احتياج المادة الجافة اليومي: **{req_feed_kg:.2f} كجم**")

        st.markdown('<div class="section-title">⚙️ نظام الحساب والتحسين النشط بالمنصة</div>', unsafe_allow_html=True)
        calc_mode = st.radio("اختر أساس صياغة واستمثال العلف الفني:", ["صياغة بناءً على البروتين والأحماض الخام (كيميائياً مجرداً)", "صياغة بناءً على البروتين والأحماض المهضومة فعلياً (حيوياً ممتصاً)"], index=1, horizontal=True)
        is_digestible_mode = True if "المهضومة" in calc_mode else False
        mode_key = "digestible" if is_digestible_mode else "crude"

        st.markdown('<div class="section-title">📋 رابعاً: حدود الموازنة الذكية للتركيبة العلفية</div>', unsafe_allow_html=True)
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        with col_p1:
            override_dp = st.checkbox("⚙️ تعديل فني للبروتين")
            final_target_dp = st.slider("نسبة البروتين المستهدفة:", 5.0, 40.0, value=float(default_dp)) if override_dp else default_dp
        with col_p2:
            override_se = st.checkbox("⚙️ تعديل فني للـ SE")
            final_target_se = st.slider("حد الـ SE المستهدف:", 10.0, 90.0, value=float(default_se)) if override_se else default_se
        with col_p3:
            override_lys = st.checkbox("⚙️ تعديل فني لليسين")
            final_target_lys = st.slider("حد الليسين المستهدف:", 0.1, 5.0, value=float(default_lys)) if override_lys else default_lys
        with col_p4:
            override_met = st.checkbox("⚙️ تعديل فني للميثيونين")
            final_target_met = st.slider("حد الميثيونين المستهدف:", 0.05, 3.0, value=float(default_met)) if override_met else default_met

        # المضافات الثابتة
        fixed_additives = {
            "ملح الطعام": 0.5,
            "مضاد سموم فطرية": 0.2,
            "الحجر الجيري (بودرة بلاط)": 2.5 if "بياض" in prod_stage else 1.5,
            "فوسفات ثنائي الكالسيوم (DCP)": 1.0,
        }
        if main_sector in ["الأبقار وسلالاتها", "الماعز وسلالاتها", "الأغنام وسلالاتها 🐏"]:
            fixed_additives["بيكربونات الصوديوم (الصودا)"] = 0.75
        elif main_sector == "الطيور والسمان":
            fixed_additives["بيكربونات الصوديوم (الصودا)"] = 0.20
            fixed_additives["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05

        total_fixed_pct = sum(fixed_additives.values())

        selected_ingredients = []
        ingredient_prices = {}

        st.markdown("### 🌾 اختر الخامات الأساسية المتاحة لديك لتدخل في الحساب الخطي:")
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            with st.expander(f"📁 {cat_name}", expanded=True if "الحبوب" in cat_name or "الأكساب" in cat_name else False):
                sub_cols = st.columns(3)
                for idx, (ing_name, ing_data) in enumerate(items.items()):
                    if ing_name in fixed_additives:
                        continue
                    with sub_cols[idx % 3]:
                        is_def = True if ing_name in ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)"] else False
                        checked = st.checkbox(ing_name, value=is_def, key=f"feed_{ing_name}")
                        current_live_price = live_prices.get(ing_name, ing_data["price"])
                        price_input = current_live_price
                        if checked:
                            selected_ingredients.append(ing_name)
                            ingredient_prices[ing_name] = price_input

        st.markdown("---")

        if st.button("🚀 تشغيل محرك الاستمثال الخطي للأعلاف", type="primary", use_container_width=True):
            if not selected_ingredients:
                st.error("⚠️ يرجى اختيار مادة علفية كبرى واحدة على الأقل (مثل الذرة أو الصويا) بجانب المضافات الدقيقة.")
            else:
                # مصفوفة الاستمثال
                c_vector = [ingredient_prices[ing] for ing in selected_ingredients]
                bounds = []
                for ing in selected_ingredients:
                    for cat in BIG_FEEDS_LIBRARY.values():
                        if ing in cat:
                            bounds.append((cat[ing]["min"], cat[ing]["max"]))
                            break

                # قيد المجموع الكلي للخامات الكبرى ليقفل الطن تماماً (100% - المضافات)
                A_eq = [[1.0 for _ in selected_ingredients]]
                b_eq = [100.0 - total_fixed_pct]

                protein_row = []
                lys_row = []
                met_row = []
                se_row = []
                ca_row = []
                p_row = []

                # حساب مساهمة المضافات الثابتة أولاً في محتوى النيتروجين والمعادن
                fixed_protein_contribution = 0.0
                fixed_lys_contribution = 0.0
                fixed_met_contribution = 0.0
                fixed_se_contribution = 0.0
                fixed_ca_contribution = 0.0
                fixed_p_contribution = 0.0

                for f_ing, f_val in fixed_additives.items():
                    for cat in BIG_FEEDS_LIBRARY.values():
                        if f_ing in cat:
                            f_cp = cat[f_ing].get("CP", 0.0)
                            f_dc = cat[f_ing].get("DC", 1.0) if mode_key == "digestible" else 1.0
                            fixed_protein_contribution += (f_val / 100.0) * f_cp * f_dc
                            fixed_lys_contribution += (f_val / 100.0) * cat[f_ing].get("lys", 0.0) * f_dc
                            fixed_met_contribution += (f_val / 100.0) * cat[f_ing].get("met", 0.0) * f_dc
                            fixed_se_contribution += (f_val / 100.0) * cat[f_ing].get("SE", 0.0)
                            fixed_ca_contribution += (f_val / 100.0) * cat[f_ing].get("Ca", 0.0)
                            fixed_p_contribution += (f_val / 100.0) * cat[f_ing].get("P", 0.0)

                for ing in selected_ingredients:
                    cp_val = 0.0; lys_val = 0.0; met_val = 0.0; se_val = 0.0; ca_val = 0.0; p_val = 0.0; dc_val = 1.0
                    for cat in BIG_FEEDS_LIBRARY.values():
                        if ing in cat:
                            cp_val = cat[ing].get("CP", 0.0)
                            lys_val = cat[ing].get("lys", 0.0)
                            met_val = cat[ing].get("met", 0.0)
                            se_val = cat[ing].get("SE", 0.0)
                            ca_val = cat[ing].get("Ca", 0.0)
                            p_val = cat[ing].get("P", 0.0)
                            dc_val = cat[ing].get("DC", 1.0)

                    base_dc = dc_val if mode_key == "digestible" else 1.0
                    protein_row.append(cp_val * base_dc)
                    lys_row.append(lys_val * base_dc)
                    met_row.append(met_val * base_dc)
                    se_row.append(se_val)
                    ca_row.append(ca_val)
                    p_row.append(p_val)

                # قيد المطابقة للبروتين المستهدف بعد طرح مساهمة المضافات الثابتة
                A_eq.append(protein_row)
                b_eq.append((final_target_dp - fixed_protein_contribution) * 100.0)

                # القيود غير المتساوية (الأحماض الأمينية والطاقة)
                A_ub = []
                b_ub = []

                A_ub.append([-1.0 * x for x in lys_row])
                b_ub.append(-1.0 * (final_target_lys - fixed_lys_contribution) * 100.0)

                A_ub.append([-1.0 * x for x in met_row])
                b_ub.append(-1.0 * (final_target_met - fixed_met_contribution) * 100.0)

                A_ub.append([-1.0 * x for x in se_row])
                b_ub.append(-1.0 * (final_target_se - fixed_se_contribution) * 100.0)

                # 🧬 القيد البيطري الحيوي المتقدم: موازنة نسبة الكالسيوم إلى الفسفور (Ca:P)
                # نضمن أن Ca >= 1.5 * P (أي Ca - 1.5 P >= 0) وتكتب برمجياً كـ: -Ca + 1.5P <= 0
                ca_p_ratio_row = [-1.0 * ca_row[i] + 1.5 * p_row[i] for i in range(len(selected_ingredients))]
                fixed_ca_p_contribution = -1.0 * fixed_ca_contribution + 1.5 * fixed_p_contribution
                A_ub.append(ca_p_ratio_row)
                b_ub.append(-1.0 * fixed_ca_p_contribution * 100.0)

                res = linprog(c_vector, A_ub=A_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

                if res.success:
                    formula_results = {}
                    # دمج المضافات الثابتة أولاً في النتيجة النهائية الفعالة لتقفل 100%
                    for k, v in fixed_additives.items():
                        formula_results[k] = v

                    for idx, ing in enumerate(selected_ingredients):
                        if res.x[idx] > 0.0001:
                            formula_results[ing] = res.x[idx]

                    st.session_state["active_formula"] = formula_results
                    st.session_state["active_cp_tag"] = final_target_dp
                    st.session_state["active_breed_tag"] = sub_type
                    st.session_state["active_animal_img"] = ANIMAL_IMAGES_RESOURCES.get(dynamic_img_key, ANIMAL_IMAGES_RESOURCES["عام"])
                    st.session_state["active_stage_title"] = f"{main_sector} - {prod_stage}"

                    st.success("🎯 تم الوصول للتركيبة الاقتصادية المثالية المتزنة معدنياً وأمينياً بنجاح!")
                    
                    res_col1, res_col2 = st.columns([0.6, 0.4])
                    with res_col1:
                        st.write("#### 📝 المقادير النهائية الدقيقة المعتمدة لتركيب طن واحد (1000 كجم):")
                        for k, v in formula_results.items():
                            st.markdown(f'<div class="formula-item">▪️ <b>{k}:</b> {v:.2f} % ➡️ ({v*10:.1f} كجم / طن)</div>', unsafe_allow_html=True)
                        
                        ton_cost = (res.fun / 100.0) + sum([(ingredient_prices.get(x, BIG_FEEDS_LIBRARY["🪨 الأملاح والمعادن ومنظمات الهضم"].get(x, {}).get("price", 40.0)) * (y/100.0)) for x, y in fixed_additives.items()])
                        st.session_state["computed_ton_cost"] = ton_cost
                        st.metric("💰 التكلفة الكلية الصافية لإنتاج الطن:", f"${ton_cost:.2f} (أو {ton_cost*local_rate:,.1f} {local_sym})")
                    with res_col2:
                        st.bar_chart(pd.Series(formula_results))
                else:
                    st.error("❌ تعذر إيجاد حل رياضي متزن تماماً ضمن المحددات الحالية الضيقة. يرجى إتاحة وتفعيل خامات بروتينية إضافية ككسب فول صويا أو أمباز الفول لتوسيع مساحة الحل للمعالج الخطي.")

    # --- مختبر فحص وتحليل الأعلاف الجاهزة يدوياً ---
    with sub_tab_analyzer:
        st.markdown('<div class="section-title">🔬 مختبر فحص وتحليل الخلطات الجاهزة يدوياً وتأكيد السلامة البيطرية</div>', unsafe_allow_html=True)
        st.subheader("📥 أدخل أوزان المكونات بالكيلوجرام (الخلاط اليدوي حَقلياً):")

        lab_user_inputs = {}
        all_library_ingredients = []
        for cat_name, items in BIG_FEEDS_LIBRARY.items():
            for ing_name in items.keys():
                all_library_ingredients.append(ing_name)

        col_input1, col_input2, col_input3 = st.columns(3)
        segment = len(all_library_ingredients) // 3 + 1

        with col_input1:
            for ing_name in all_library_ingredients[:segment]:
                lab_user_inputs[ing_name] = st.number_input(f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0, step=10.0, key=f"lab_in_{ing_name}")
        with col_input2:
            for ing_name in all_library_ingredients[segment : segment * 2]:
                lab_user_inputs[ing_name] = st.number_input(f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0, step=10.0, key=f"lab_in_{ing_name}")
        with col_input3:
            for ing_name in all_library_ingredients[segment * 2 :]:
                lab_user_inputs[ing_name] = st.number_input(f"وزن {ing_name} (كجم):", min_value=0.0, value=0.0, step=10.0, key=f"lab_in_{ing_name}")

        if st.button("🧪 تشغيل التحليل الفوري وتأكيد السلامة الحقلية", type="primary", use_container_width=True):
            lab_total_weight = sum(lab_user_inputs.values())
            if lab_total_weight <= 0:
                st.warning("⚠️ يرجى إدخال أوزان صحيحة للمكونات لبدء الفحص.")
            else:
                calculated_total_dp = 0.0; calculated_total_se = 0.0; calculated_total_ca = 0.0; calculated_total_p = 0.0
                for ing_name, weight in lab_user_inputs.items():
                    if weight > 0:
                        pct = weight / lab_total_weight
                        for cat, items in BIG_FEEDS_LIBRARY.items():
                            if ing_name in items:
                                calculated_total_dp += pct * (items[ing_name]["CP"] * items[ing_name]["DC"])
                                calculated_total_se += pct * items[ing_name]["SE"]
                                calculated_total_ca += pct * items[ing_name]["Ca"]
                                calculated_total_p += pct * items[ing_name]["P"]

                st.markdown(f"### 📊 النتيجة المخبرية الحيوية للعلائق الجاهزة (إجمالي العينة: {lab_total_weight} كجم):")
                st.info(f"🧬 نسبة البروتين المهضوم الحيوي: **{calculated_total_dp:.2f}%** | 🌽 معادل النشاء الإجمالي: **{calculated_total_se:.2f} وحدة**")
                
                # إشعار تشخيصي طبي بيطري من واقع الخبرة السريرية
                if calculated_total_p > 0:
                    ca_p_ratio = calculated_total_ca / calculated_total_p
                    st.write(f"🧬 نسبة الكالسيوم إلى الفسفور الفعلية في خلاطك اليدوي: **{ca_p_ratio:.2f} : 1**")
                    if ca_p_ratio < 1.2:
                        st.markdown('<div class="warning-card">⚠️ <b>تحذير عيادي حرج (خطر طبي):</b> نسبة الكالسيوم منخفضة جداً بالنسبة للفسفور! هذا الخلل يعرض ذكور التسمين لخطر تشكل <b>الحصوات البولية الحادة (Urinary Calculi)</b>، ويعرض الأبقار لمرض <b>حمى اللبن</b>. يرجى زيادة بودرة البلاط فوراً.</div>', unsafe_allow_html=True)
                    else:
                        st.success("✅ النسبة المعدنية للكالسيوم والفسفور تقع ضمن النطاق البيولوجي الآمن حَقلياً.")

# ====================================================================
# التبويبات الإدارية (محمية ومحسنة بـ st.form لمنع إعادة التحميل العشوائي)
# ====================================================================
if st.session_state["user_role"] in ["owner", "specialist"]:
    with tabs[1]:
        st.markdown('<div class="section-title">📊 لوحة التحكم وقاعدة بيانات الأعلاف المركزية</div>', unsafe_allow_html=True)
        
        # استخدام st.form لمنع تجميد الشاشة أثناء تعديل الأسعار
        with st.form("prices_form"):
            st.write("### 💰 تحديث أسعار بورصة الماشية والمنتجات دفعة واحدة:")
            col_le1, col_le2 = st.columns(2)
            updated_livestock = {}
            updated_products = {}
            
            with col_le1:
                st.write("🐓 بورصة الماشية الحية:")
                for animal, price in st.session_state["global_livestock_prices"].items():
                    updated_livestock[animal] = st.number_input(f"سعر {animal} ($):", min_value=0.0, value=float(price), key=f"form_live_{animal}")
            with col_le2:
                st.write("🥛 بورصة اللحوم والألبان:")
                for product, price in st.session_state["global_products_prices"].items():
                    updated_products[product] = st.number_input(f"سعر {product} ($):", min_value=0.0, value=float(price), key=f"form_prod_{product}")
            
            submit_prices = st.form_submit_with_colored_button = st.form_submit_button("💾 حفظ وتحديث أسعار البورصة فورياً", type="primary", use_container_width=True)
            if submit_prices:
                st.session_state["global_livestock_prices"] = updated_livestock
                st.session_state["global_products_prices"] = updated_products
                st.success("🔥 تم تحديث البورصة المركزية بنجاح دون أي تجميد للواجهة!")

    with tabs[2]:
        st.markdown('<div class="section-title">🏭 لوحة التحكم الذكية بالمخازن (الخصم والتحديث دفعة واحدة)</div>', unsafe_allow_html=True)
        with st.form("inventory_form"):
            inv_cols = st.columns(3)
            updated_inventory = {}
            for idx, (ing_name, qty) in enumerate(list(st.session_state["inventory"].items())):
                with inv_cols[idx % 3]:
                    updated_inventory[ing_name] = st.number_input(f"رصيد {ing_name} (طن):", min_value=0.0, value=float(qty), key=f"form_inv_{ing_name}")
            
            submit_inventory = st.form_submit_button("💾 حفظ وتحديث جرد المستودعات بالكامل", type="primary", use_container_width=True)
            if submit_inventory:
                st.session_state["inventory"] = updated_inventory
                st.success("🔥 تم حفظ جرد المخازن وتحديث الأرصدة بنجاح!")

    with tabs[3]:
        st.markdown('<div class="section-title">💰 نظام تسويق المنتجات وإصدار الفواتير مع الخصم التلقائي</div>', unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: client_name = st.text_input("اسم العميل / المزرعة المستلمة:", "مزارع الإنتاج المتكاملة")
        with col_c2: required_tons = st.number_input("الكمية المطلوبة (بالطن):", min_value=0.1, value=2.0, step=0.5)
        with col_c3: added_profit = st.number_input("هامش الربح الصافي المضاف لكل طن ($):", min_value=0.0, value=50.0)
        
        selling_price = st.session_state["computed_ton_cost"] + added_profit
        total_bill = selling_price * required_tons
        st.markdown(f"### 💰 إجمالي القيمة المستحقة للفاتورة: `${total_bill:.2f}` (أو تعادل `{total_bill*local_rate:,.1f}` {local_sym})")

        if st.button("✅ تأكيد عملية البيع وخصم المكونات من المستودع"):
            can_deduct = True
            for name, pct in st.session_state["active_formula"].items():
                if st.session_state["inventory"].get(name, 0.0) < ((pct / 100) * required_tons):
                    can_deduct = False
                    st.error(f"❌ رصيد غير كافي في المخزن للمكون: {name}!")
                    break
            if can_deduct:
                for name, pct in st.session_state["active_formula"].items():
                    st.session_state["inventory"][name] -= (pct / 100) * required_tons
                st.success("🔥 تم الخصم التلقائي وتحديث المخازن بنجاح!")
                time.sleep(1)
                st.rerun()

    with tabs[4]:
        st.markdown('<div class="section-title">👑 مُصمم ديباجات الطباعة الفنية على جوالات الأعلاف</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sack-tag">
            <img src="{st.session_state['active_animal_img']}" class="animal-banner-img">
            <h2 style="text-align: center; margin-top:0;">🌟 منصة تاور العلمية للأعلاف 🌟</h2>
            <h3 style="text-align: center; color: #c62828; margin-top:0; font-weight: bold;">الاختصاصي م. عبد القادر إسماعيل تاور</h3>
            <p style="text-align: center; font-weight: bold; background-color:#e8f5e9; padding:6px; color:#1b5e20;">🎯 علف مخصص لـ: {st.session_state['active_stage_title']} | نسبة البروتين: {st.session_state['active_cp_tag']:.1f}% </p>
        </div>
        """, unsafe_allow_html=True)

    with tabs[5]:
        st.markdown('<div class="section-title">💬 قناة التواصل والتعليقات الخاصة بالزملاء والمختصين</div>', unsafe_allow_html=True)
        st.text_area("التعليقات الحالية:", value=st.session_state["shared_comments"], height=200, disabled=True)
        new_comment = st.text_input("✍️ أكتب تعليقك الفني أو ملاحظتك التركيبية هنا لجهازك:")
        if st.button("📌 حفظ ونشر التعليق للزملاء"):
            if new_comment.strip():
                prefix = "• [توجيه الاختصاصي م. عبد القادر إسماعيل تاور]" if st.session_state["user_role"] == "owner" else "• [ملاحظة مختص]"
                st.session_state["shared_comments"] += f"{prefix}: {new_comment.strip()}\n"
                st.success("تمت إضافة الملاحظة بنجاح!")
                time.sleep(0.5)
                st.rerun()

# ====================================================================
# 🗂️ دليل المستخدم في شكل كتيب رقمي
# ====================================================================
support_tab_index = 6 if st.session_state["user_role"] in ["owner", "specialist"] else 1
with tabs[support_tab_index]:
    st.markdown('<div class="section-title">📖 كتيب دليل المستخدم والتقانة الفنية للمنصة</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="manual-book">
        <h3 style="color: #2e7d32;">📖 الدليل المهني التشغيلي - إصدار 2026 المطور</h3>
        <p>تم تفعيل نظام الحماية المعدنية لتفادي الأمراض الاستقلابية حَقلياً (الحصاوي البولية وحمى اللبن) عبر ربط نسب المكونات الكبرى بالحدود الدقيقة للـ <b>Calcium & Phosphorus Ratio</b> تلقائياً عند طلب الاستمثال.</p>
    </div>
    """, unsafe_allow_html=True)

# ====================================================================
# 1. نظام حفظ وأرشفة السورس كود
# ====================================================================
if st.session_state["user_role"] == "owner":
    st.markdown("<br><hr style='border-top: 1px dashed #2e7d32;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #1565C0; text-align:right;'>📨 أرشفة شفرة المصدر البرمجية للمنصة</h3>", unsafe_allow_html=True)
    if st.button("إرسال نسخة الكود للمالك 🚀", use_container_width=True, type="secondary"):
        with st.spinner("جاري تأمين الاتصال السحابي بالخادم وإرسال السورس كود..."):
            if send_code_to_mail(OWNER_EMAIL):
                st.success(f"📥 تم إرسال السورس كود المحدث بأمان إلى بريدك المعتمد يا باشمهندس عبد القادر.")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown('<div class="mini-left-signature">👨‍🔬 الاختصاصي م. عبد القادر إسماعيل تاور © 2026 | منصة تاور العلمية للإنتاج الحيواني وتركيب الأعلاف</div>', unsafe_allow_html=True)
