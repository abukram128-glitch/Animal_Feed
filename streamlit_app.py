# ============================================================================
# تاور نولجي Tawornology العلمية - الإصدار النهائي المتكامل 18.0
# ============================================================================
# 🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله
# ============================================================================
# الميزات في v18.0:
# 1. قاعدة بيانات Thread-Safe (WAL + Indexes + Row Factory)
# 2. إصلاح مصفوفة linprog (المكونات الإلزامية قبل البناء)
# 3. إصلاح send_code_to_email (Streamlit-safe)
# 4. OCR مع Cache + Lazy Load
# 5. تصدير Excel + لوحة إدارة
# 6. ختم PDF رسمي مع QR
# 7. البسملة في ترويسة كل PDF
# 8. توصيات ذكية مطابقة لكل خلطة (كمية + شرح)
# 9. دعم 100+ مستخدم متزامن
# 10. التعليقات المشتركة في قاعدة البيانات
# المشرف العام: اختصاصي تغذية الحيوان. م. عبدالقادر إسماعيل تاور
# ============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import json, os, base64, smtplib, time, urllib.parse, threading, shutil
import hashlib, secrets, io, sqlite3, warnings, re, math, random
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from scipy.optimize import linprog
from scipy.spatial import ConvexHull
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

try:
    import pytesseract
    from PIL import Image as PILImage
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4, landscape, letter
from reportlab.lib.units import inch, mm, cm
from reportlab.lib.colors import HexColor, black, white, grey, blue, red, green, orange, purple, teal, gold
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
import arabic_reshaper
from bidi.algorithm import get_display
import qrcode
from PIL import Image as PILImage_module
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle

warnings.filterwarnings('ignore')

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# =====================================================================
# ثوابت النظام
# =====================================================================
SUPERVISOR_NAME = "اختصاصي تغذية الحيوان. م. عبدالقادر إسماعيل تاور"
SUPERVISOR_TITLE = "اختصاصي تغذية الحيوان"
BRAND = "تاور نولجي Tawornology العلمية"
BASMALA = "بسم الله الرحمن الرحيم"

st.set_page_config(
    page_title="تاور نولجي Tawornology العلمية - للانتاج الحيواني وتركيب الاعلاف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def init_caching_system():
    return {"cache_hits": 0, "cache_misses": 0, "last_cleanup": datetime.now()}
CACHE_SYSTEM = init_caching_system()

CODES_DB = {
    "202687": {"role": "owner", "name": SUPERVISOR_NAME, "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2024": {"role": "veterinarian", "name": "الطبيب البيطري", "level": 2},
    "2025": {"role": "nutritionist", "name": "أخصائي التغذية", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"

PHOTO_OPTIONS = ["14686.jpg", "1000069464.jpg", "14686.JPG", "1000069464.JPG"]

@st.cache_data(ttl=3600)
def get_image_base64(paths):
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                pass
    return None

img_base64 = get_image_base64(tuple(PHOTO_OPTIONS))
# =====================================================================
# DatabaseManager v18.0 - Thread-Safe + WAL + Indexes
# =====================================================================
class DatabaseManager:
    _write_lock = threading.Lock()
    _init_done = False

    def __init__(self, db_path="tawornology_platform.db"):
        self.db_path = db_path
        if not DatabaseManager._init_done:
            with DatabaseManager._write_lock:
                if not DatabaseManager._init_done:
                    self._init_db()
                    DatabaseManager._init_done = True

    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0,
                                check_same_thread=False, isolation_level=None)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA busy_timeout=30000;")
            conn.execute("PRAGMA foreign_keys=ON;")
            conn.execute("PRAGMA temp_store=MEMORY;")
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, role TEXT, full_name TEXT, email TEXT, phone TEXT, specialty TEXT, experience_years INTEGER, created_date TEXT, last_login TEXT, is_active INTEGER DEFAULT 1, is_public INTEGER DEFAULT 0)''')
            c.execute('''CREATE TABLE IF NOT EXISTS farms (farm_id TEXT PRIMARY KEY, farm_name TEXT UNIQUE, farm_type TEXT, owner_name TEXT, owner_phone TEXT, location TEXT, area REAL, created_date TEXT, last_updated TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS production_cycles (cycle_id TEXT PRIMARY KEY, farm_id TEXT, cycle_type TEXT, start_date TEXT, end_date TEXT, initial_count INTEGER, breed TEXT, target_weight REAL, target_age INTEGER, status TEXT, notes TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS daily_records (record_id TEXT PRIMARY KEY, cycle_id TEXT, record_date TEXT, age_days INTEGER, live_birds INTEGER, avg_weight REAL, min_weight REAL, max_weight REAL, feed_consumed REAL, water_consumed REAL, dead_count INTEGER, culled_count INTEGER, temperature REAL, humidity REAL, ventilation_status TEXT, litter_quality TEXT, feed_conversion REAL, mortality_rate REAL, notes TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS health_records (health_id TEXT PRIMARY KEY, cycle_id TEXT, record_date TEXT, age_days INTEGER, treatment_type TEXT, treatment_name TEXT, dose REAL, dose_unit TEXT, administration_route TEXT, administered_by TEXT, notes TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS performance_comparisons (comparison_id TEXT PRIMARY KEY, cycle_id TEXT, comparison_date TEXT, metric_type TEXT, farm_value REAL, standard_value REAL, deviation REAL, status TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS vaccine_alerts (alert_id TEXT PRIMARY KEY, cycle_id TEXT, alert_date TEXT, scheduled_date TEXT, vaccine_name TEXT, vaccine_type TEXT, dose TEXT, route TEXT, status TEXT, sent INTEGER DEFAULT 0)''')
            c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas (formula_id TEXT PRIMARY KEY, formula_name TEXT, animal_type TEXT, breed TEXT, stage TEXT, target_dp REAL, target_se REAL, ingredients TEXT, total_cost REAL, cost_per_ton REAL, created_by TEXT, created_date TEXT, is_approved INTEGER DEFAULT 0, usage_count INTEGER DEFAULT 0, requester_name TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS invoices (invoice_id TEXT PRIMARY KEY, customer_name TEXT, customer_phone TEXT, customer_address TEXT, formula_id TEXT, quantity_ton REAL, unit_price REAL, total_price REAL, discount REAL DEFAULT 0, tax REAL DEFAULT 0, final_price REAL, status TEXT, payment_method TEXT, created_by TEXT, created_date TEXT, due_date TEXT, notes TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS price_history (record_id TEXT PRIMARY KEY, ingredient_name TEXT, price REAL, currency TEXT, country TEXT, city TEXT, record_date TEXT, recorded_by TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS inventory (item_id TEXT PRIMARY KEY, item_name TEXT UNIQUE, quantity REAL, min_threshold REAL, unit TEXT, last_updated TEXT, supplier TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS inventory_movements (movement_id TEXT PRIMARY KEY, item_name TEXT, quantity REAL, movement_type TEXT, reference TEXT, movement_date TEXT, notes TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS customers (customer_id TEXT PRIMARY KEY, customer_name TEXT, phone TEXT, email TEXT, address TEXT, tax_number TEXT, notes TEXT, created_date TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS suppliers (supplier_id TEXT PRIMARY KEY, supplier_name TEXT, phone TEXT, email TEXT, address TEXT, tax_number TEXT, notes TEXT, created_date TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS milk_replacers (replacer_id TEXT PRIMARY KEY, animal_type TEXT, age_days INTEGER, formula_name TEXT, ingredients TEXT, instructions TEXT, created_by TEXT, created_date TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS dose_reminders (reminder_id TEXT PRIMARY KEY, animal_type TEXT, dose_type TEXT, dose_name TEXT, dose_amount REAL, dose_unit TEXT, administration_route TEXT, frequency_days INTEGER, start_date TEXT, next_dose_date TEXT, notes TEXT, active INTEGER DEFAULT 1, created_by TEXT, created_date TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS lab_results (result_id TEXT PRIMARY KEY, sample_name TEXT, sample_type TEXT, cp REAL, dc REAL, se REAL, ndf REAL, adf REAL, ee REAL, ash REAL, moisture REAL, analysis_date TEXT, analyzed_by TEXT, notes TEXT, image_path TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS shared_comments (comment_id TEXT PRIMARY KEY, author TEXT, role TEXT, comment TEXT, created_at TEXT)''')
            for idx_sql in [
                "CREATE INDEX IF NOT EXISTS idx_daily_cycle ON daily_records(cycle_id)",
                "CREATE INDEX IF NOT EXISTS idx_health_cycle ON health_records(cycle_id)",
                "CREATE INDEX IF NOT EXISTS idx_alerts_cycle ON vaccine_alerts(cycle_id, status)",
                "CREATE INDEX IF NOT EXISTS idx_price_ing ON price_history(ingredient_name, record_date DESC)",
                "CREATE INDEX IF NOT EXISTS idx_formula_animal ON feed_formulas(animal_type, created_date DESC)",
                "CREATE INDEX IF NOT EXISTS idx_lab_date ON lab_results(analysis_date DESC)",
                "CREATE INDEX IF NOT EXISTS idx_comments_date ON shared_comments(created_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_users_login ON users(username, is_active)",
            ]:
                c.execute(idx_sql)

    def execute_query(self, query, params=()):
        with self._get_conn() as conn:
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    def execute_write(self, query, params=()):
        with DatabaseManager._write_lock:
            with self._get_conn() as conn:
                cur = conn.execute(query, params)
                return cur.lastrowid

    def insert_record(self, table, data):
        cols = ', '.join(data.keys())
        ph = ', '.join(['?' for _ in data])
        self.execute_write(f"INSERT INTO {table} ({cols}) VALUES ({ph})", list(data.values()))
        return True

    def get_records(self, table, conditions=None, limit=None):
        if conditions:
            where = ' AND '.join([f"{k}=?" for k in conditions.keys()])
            q = f"SELECT * FROM {table} WHERE {where}"
            params = list(conditions.values())
        else:
            q = f"SELECT * FROM {table}"
            params = []
        if limit:
            q += f" LIMIT {int(limit)}"
        return self.execute_query(q, params)

    def update_record(self, table, data, condition):
        set_clause = ', '.join([f"{k}=?" for k in data.keys()])
        where = ' AND '.join([f"{k}=?" for k in condition.keys()])
        self.execute_write(f"UPDATE {table} SET {set_clause} WHERE {where}",
                           list(data.values()) + list(condition.values()))
        return True

    def delete_record(self, table, condition):
        where = ' AND '.join([f"{k}=?" for k in condition.keys()])
        self.execute_write(f"DELETE FROM {table} WHERE {where}", list(condition.values()))
        return True

@st.cache_resource
def get_db():
    return DatabaseManager()

# =====================================================================
# دوال الصوت
# =====================================================================
@st.cache_data(ttl=3600)
def text_to_speech_base64(text, lang="ar"):
    if not GTTS_AVAILABLE or not text:
        return None
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()
    except Exception:
        return None

def play_audio_b64(audio_b64):
    if audio_b64:
        st.components.v1.html(
            f'<audio autoplay><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mpeg"></audio>',
            height=0)
        return True
    return False

def voice_guide(message, lang="ar"):
    if not GTTS_AVAILABLE or not message:
        return
    audio_b64 = text_to_speech_base64(message, lang)
    if audio_b64:
        play_audio_b64(audio_b64)

def voice_welcome(role):
    msgs = {
        "owner": f"مرحباً بك في تاور نولجي، {SUPERVISOR_NAME}.",
        "specialist": "مرحباً أيها المختص.",
        "veterinarian": "مرحباً أيها الطبيب البيطري.",
        "nutritionist": "مرحباً أيها أخصائي التغذية.",
        "breeder": "مرحباً أيها المربي.",
        "public": "مرحباً بك زائراً."
    }
    voice_guide(msgs.get(role, "مرحباً بك."))

def play_full_guide_audio():
    for msg in ["مرحباً بك في منصة تاور نولجي Tawornology العلمية.",
                "هذه المنصة متخصصة في الانتاج الحيواني وتركيب الاعلاف.",
                "تتضمن أقساماً للقطاع الحيواني، والمختبر الذكي، وإدارة المزارع، وبدائل الحليب، وبورصة الأسعار."]:
        voice_guide(msg)
        time.sleep(3)

# =====================================================================
# إرسال الكود (Streamlit-safe)
# =====================================================================
def send_code_to_email(receiver_email, smtp_password):
    if not smtp_password:
        return False, "⚠️ كلمة المرور مطلوبة."
    if receiver_email.strip().lower() != OWNER_EMAIL.strip().lower():
        return False, f"❌ الإرسال مسموح فقط إلى: {OWNER_EMAIL}"
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception:
        code_content = "# تعذر قراءة الكود"
    file_hash = hashlib.md5(code_content.encode()).hexdigest()
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = f"🌾 السورس كود - {BRAND} v18.0"
    body = f"السلام عليكم،\n\nمرفق السورس كود الكامل.\n📅 {datetime.now():%Y-%m-%d %H:%M}\n🔑 التوقيع: {file_hash}\n\n{SUPERVISOR_NAME}\n"
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    att = MIMEText(code_content, 'plain', 'utf-8')
    att.add_header('Content-Disposition', 'attachment',
                   filename=f"tawornology_v18_{datetime.now():%Y%m%d}.py")
    msg.attach(att)
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.starttls()
        server.login(SENDER_EMAIL, smtp_password)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True, f"✅ تم الإرسال إلى {receiver_email}"
    except smtplib.SMTPAuthenticationError:
        return False, "❌ كلمة مرور البريد غير صحيحة (استخدم App Password)"
    except Exception as e:
        return False, f"❌ فشل: {type(e).__name__}: {e}"

# =====================================================================
# معالج النصوص العربية
# =====================================================================
class ArabicTextProcessor:
    @staticmethod
    @lru_cache(maxsize=2000)
    def fix(text):
        if not text:
            return ""
        return get_display(arabic_reshaper.reshape(str(text)))

arabic_processor = ArabicTextProcessor()

# =====================================================================
# التوصيات الذكية (جديد v18.0)
# =====================================================================
def generate_smart_recommendations(animal_type, stage, formula, dp, se,
                                    cost_per_ton, physiological_state="طبيعي",
                                    target_dp_standard=None, target_se_standard=None):
    """يولّد توصيات مطابقة للخلطة والحيوان والكمية المطلوبة."""
    recs = []
    daily_intake = {}
    animal_key = animal_type

    # متوسط الاستهلاك اليومي لكل حيوان (كجم)
    consumption = {
        "أبقار": {"تسمين عجول": 10.0, "حليب/إدرار": 12.0, "حمل/دفع غذائي": 11.0,
                  "صيانة": 8.0, "تسمين مكثف": 12.0},
        "أغنام": {"تسمين حملان": 1.8, "نعاج مرضعات": 2.2, "نعاج حامل": 1.8, "نعاج جافة": 1.4},
        "ماعز": {"تسمين جديان": 1.3, "عنزات حلابة": 2.0, "عنزات حامل": 1.6, "صيانة": 1.2},
        "خيول": {"راحة/صيانة": 7.0, "عمل خفيف": 8.0, "عمل متوسط": 9.0, "عمل مكثف": 11.0,
                 "سباق": 12.0, "أمهار نامية": 6.0, "فرسات مرضعات": 10.0},
        "إبل": {"راحة/صيانة": 6.0, "حمل/رضاعة": 8.0, "إنتاج حليب": 10.0,
                "تسمين": 9.0, "عمل/نقل": 8.0},
        "دواجن": {"بادي (0-14 يوم)": 0.030, "نامي (15-28 يوم)": 0.070,
                  "ناهي (29-42 يوم)": 0.120, "ناهي متقدم (43+ يوم)": 0.140},
        "أسماك": {"زريعة/بادئ": 0.015, "نمو": 0.025, "تسمين نهائي": 0.030}
    }

    intake = 5.0
    if "دواجن" in animal_type and "بادي" in stage:
        intake = 0.030
    elif "دواجن" in animal_type and "نامي" in stage:
        intake = 0.070
    elif "دواجن" in animal_type and "ناهي" in stage:
        intake = 0.120
    elif "أسماك" in animal_type:
        intake = 0.020
    else:
        for cat, stages in consumption.items():
            if cat in animal_type:
                intake = stages.get(stage, 5.0)
                break

    if physiological_state == "حامل":
        intake *= 1.15
    elif physiological_state == "مرضع":
        intake *= 1.30
    elif physiological_state == "نشاط مكثف":
        intake *= 1.20
    elif physiological_state == "نمو سريع":
        intake *= 1.30

    # ===== التوصيات =====
    recs.append(f"📊 الكمية اليومية الموصى بها: {intake:.3f} كجم/رأس/يوم")

    if intake < 1:
        cost_day = intake * (cost_per_ton / 1000) if cost_per_ton else 0
        recs.append(f"💰 تكلفة التغذية اليومية: ${cost_day:.4f} لكل رأس")
        recs.append(f"📦 الطن الواحد يكفي حوالي {int(1000 / intake):,} رأس × يوم")
    else:
        cost_day = intake * (cost_per_ton / 1000) if cost_per_ton else 0
        recs.append(f"💰 تكلفة التغذية اليومية: ${cost_day:.3f} لكل رأس")
        recs.append(f"📦 الطن الواحد يكفي {int(1000 / intake)} رأس × يوم")

    # توصيات حسب الحيوان
    if "دواجن" in animal_type:
        recs.append("💧 يجب توفير مياه نظيفة بمعدل 1.8-2.0 ضعف وزن العلف المستهلك")
        recs.append("🌡️ الالتزام بجدول الحرارة والتهوية (33°م في الأسبوع الأول تنقص 3° كل أسبوع)")
        recs.append("⏰ تقديم العلف على 3-4 وجبات مع تحريك العلف يدوياً لتحفيز الأكل")
        if "بادي" in stage:
            recs.append("🥣 طحن العلف ناعم (شكل حبيبات صغيرة) للكتاكيت الصغيرة")
        recs.append("🧪 إضافة فيتامين AD3E والكهرمان لمقاومة الإجهاد الحراري")
    elif "أبقار" in animal_type:
        recs.append("🐄 تقديم العلف على وجبتين: الصباح (6-8) والمساء (5-7)")
        recs.append("🌾 خلط العلف المركز جيداً مع الأعلاف الخشنة قبل التقديم")
        recs.append("💧 توفير مياه عذبة على مدار الساعة (70-100 لتر/رأس/يوم)")
        if "إدرار" in stage or "حليب" in stage:
            recs.append("🥛 إضافة ملح الطعام بتركيز لا يزيد عن 0.5% للخلطة لتحسين الإدرار")
        recs.append("🧂 استخدام بيكربونات الصوديوم (Buffers) بنسبة 1-1.5% لتقليل الحموضة")
    elif "أغنام" in animal_type or "ماعز" in animal_type:
        recs.append("🐑 تقديم العلف على 3 وجبات مع توفير الأعلاف الخشنة بحرية")
        recs.append("🌿 توفير القش الجاف أو الدريس بجانب الخلطة المركزة")
        recs.append("💧 مياه نظيفة بمعدل 4-6 لتر/رأس/يوم")
    elif "خيول" in animal_type:
        recs.append("🐴 تقديم العلف المركز قبل التمرين بساعتين على الأقل")
        recs.append("🌾 تقسيم العلف على 3-4 وجبات مع قش بحرية")
        if "سباق" in stage or "عمل مكثف" in stage:
            recs.append("⚡ زيادة الشوفان أو الذرة بنسبة 5% لتحسين الأداء العضلي")
    elif "إبل" in animal_type:
        recs.append("🐫 تقديم العلف في ساعات الصباح الباكر والمساء لتفادي الحرارة")
        recs.append("💧 الإبل تتحمل العطش لكن يجب توفير ماء كل 2-3 أيام على الأقل")
    elif "أسماك" in animal_type:
        recs.append("🐟 تقديم العلف على 3-4 وجبات لضمان عدم تلوث المياه")
        recs.append("💧 مراقبة جودة المياه (الأكسجين، الحرارة، الأمونيا) يومياً")

    # توصيات الجودة
    if target_dp_standard and dp:
        dp_ratio = (dp / target_dp_standard) * 100
        if dp_ratio < 85:
            recs.append(f"⚠️ نسبة البروتين ({dp_ratio:.1f}% من المعيار) منخفضة — يوصى برفع كسب الصويا 2-3%")
        elif dp_ratio > 115:
            recs.append(f"⚠️ نسبة البروتين ({dp_ratio:.1f}% من المعيار) مرتفعة — هدر اقتصادي محتمل")
        else:
            recs.append(f"✅ نسبة البروتين مطابقة للمعايير ({dp_ratio:.1f}%)")

    if target_se_standard and se:
        se_ratio = (se / target_se_standard) * 100
        if se_ratio < 85:
            recs.append(f"⚠️ نسبة الطاقة ({se_ratio:.1f}% من المعيار) منخفضة — أضف الذرة 3-5%")
        elif se_ratio > 115:
            recs.append(f"⚠️ نسبة الطاقة مرتفعة ({se_ratio:.1f}%) — راقب الوزن والسمنة")
        else:
            recs.append(f"✅ نسبة الطاقة مطابقة للمعايير ({se_ratio:.1f}%)")

    # توصيات المكونات
    ing_names = list(formula.keys()) if formula else []
    if any("يوريا" in i for i in ing_names) and "أبقار" not in animal_type and "أغنام" not in animal_type:
        recs.append("🚨 تحذير: اليوريا ممنوعة لغير المجترات — أعد النظر في الخلطة!")

    if any("يوريا" in i for i in ing_names):
        recs.append("⚠️ اليوريا: يجب خلطها جيداً ومنع الوصول المباشر — سامة بجرعات عالية")

    if any("ذرة" in i for i in ing_names) and "دواجن" in animal_type:
        recs.append("🌽 الذرة: تحقق من خلوها من الأفلاتوكسين (فحص معمل)")

    # التوصيات العامة
    recs.append("🏭 يُحفظ العلف في مكان جاف جيد التهوية بعيداً عن الرطوبة وأشعة الشمس")
    recs.append("📆 صلاحية الخلطة: 30-45 يوم في الظروف العادية")
    recs.append("⚖️ يُخلط العلف في خلاط أفقي لمدة 5-7 دقائق لضمان التجانس")
    recs.append("🧪 يُنصح بتحليل عينة دورية كل 500 طن من الإنتاج")

    return recs
                                  # =====================================================================
# تحميل الخط العربي
# =====================================================================
@st.cache_resource
def download_arabic_font():
    font_path = "Amiri-Regular.ttf"
    if os.path.exists(font_path):
        return font_path
    try:
        import requests
        r = requests.get("https://raw.githubusercontent.com/aliftype/amiri/master/fonts/Amiri-Regular.ttf",
                         timeout=30)
        if r.status_code == 200:
            with open(font_path, "wb") as f:
                f.write(r.content)
            return font_path
    except Exception:
        pass
    for f in ["/usr/share/fonts/truetype/arabic/Amiri-Regular.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "C:/Windows/Fonts/arial.ttf"]:
        if os.path.exists(f):
            return f
    return None

def ensure_arabic_font():
    fp = download_arabic_font()
    if fp and os.path.exists(fp):
        try:
            pdfmetrics.registerFont(TTFont('ArabicFont', fp))
            return 'ArabicFont'
        except Exception:
            pass
    try:
        pdfmetrics.registerFont(TTFont('ArabicFont', 'Helvetica'))
    except Exception:
        pass
    return 'Helvetica'

# =====================================================================
# ختم PDF رسمي
# =====================================================================
def generate_official_stamp():
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5)
    ax.axis('off')
    ax.add_patch(plt.Circle((0, 0), 1.35, color='#1b5e20', fill=False, linewidth=4))
    ax.add_patch(plt.Circle((0, 0), 1.20, color='#2e7d32', fill=False, linewidth=2, linestyle='--'))
    ax.text(0, 0.65, "🌾 تاور نولجي", ha='center', fontsize=11, fontweight='bold', color='#1b5e20')
    ax.text(0, 0.35, "Tawornology", ha='center', fontsize=9, color='#2e7d32')
    ax.text(0, 0.02, "معتمد رسمياً", ha='center', fontsize=10, fontweight='bold', color='#c62828')
    ax.text(0, -0.30, "م. عبدالقادر إسماعيل تاور", ha='center', fontsize=7, color='#333')
    ax.text(0, -0.55, "اختصاصي تغذية الحيوان", ha='center', fontsize=7, color='#555')
    ax.text(0, -0.85, datetime.now().strftime('%Y-%m-%d'), ha='center', fontsize=7, color='#777')
    try:
        qr = qrcode.QRCode(version=1, box_size=3, border=1)
        qr.add_data(f"Tawornology|{SUPERVISOR_NAME}|{datetime.now().isoformat()}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#1b5e20", back_color="white").convert('L')
        ax.imshow(np.array(qr_img), extent=(0.4, 0.85, -1.35, -0.9), cmap='Greens')
    except Exception:
        pass
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200, transparent=True, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

# =====================================================================
# PDF Generator مع البسملة + الترويسة + التوصيات + الختم
# =====================================================================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.font_name = ensure_arabic_font()
        self.styles = self._create_styles()

    def _create_styles(self):
        return {
            'basmala': ParagraphStyle('basmala', fontName=self.font_name, fontSize=20,
                                       alignment=TA_CENTER, textColor=HexColor('#1b5e20'),
                                       spaceAfter=15, leading=28),
            'title': ParagraphStyle('title', fontName=self.font_name, fontSize=20,
                                     alignment=TA_CENTER, textColor=HexColor('#1b5e20'),
                                     spaceAfter=15, leading=26),
            'subtitle': ParagraphStyle('subtitle', fontName=self.font_name, fontSize=14,
                                        alignment=TA_CENTER, textColor=HexColor('#2e7d32'),
                                        spaceAfter=12, leading=20),
            'heading': ParagraphStyle('heading', fontName=self.font_name, fontSize=13,
                                       alignment=TA_RIGHT, textColor=HexColor('#1b5e20'),
                                       spaceAfter=10, leading=18),
            'body': ParagraphStyle('body', fontName=self.font_name, fontSize=11,
                                    alignment=TA_RIGHT, textColor=HexColor('#333333'),
                                    spaceAfter=6, leading=16),
            'rec': ParagraphStyle('rec', fontName=self.font_name, fontSize=10.5,
                                   alignment=TA_RIGHT, textColor=HexColor('#2c3e50'),
                                   spaceAfter=5, leading=15, rightIndent=15),
            'footer': ParagraphStyle('footer', fontName=self.font_name, fontSize=8,
                                      alignment=TA_CENTER, textColor=HexColor('#999999'),
                                      spaceAfter=0, leading=10),
        }

    def _p(self, text, style='body'):
        return Paragraph(arabic_processor.fix(str(text)),
                         self.styles.get(style, self.styles['body']))

    def _add_stamp_and_footer(self, story):
        story.append(Spacer(1, 25))
        try:
            stamp_buf = generate_official_stamp()
            stamp_img = Image(stamp_buf, width=2.8*cm, height=2.8*cm)
            stamp_img.hAlign = 'CENTER'
            story.append(stamp_img)
        except Exception:
            pass
        story.append(Spacer(1, 8))
        story.append(self._p(f"تم التوليد بواسطة {BRAND} © {datetime.now().year}", 'footer'))

    def generate_comprehensive_report(self, formula, target_dp, breed, cost, city,
                                       local_cost, local_sym, computed_se, user_name,
                                       requester_name="", standard=None,
                                       recommendations=None, extra_info=None):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=45, leftMargin=45,
                                 topMargin=40, bottomMargin=40)
        story = []

        # البسملة أولاً
        story.append(self._p(BASMALA, 'basmala'))
        story.append(Spacer(1, 5))

        # الترويسة
        story.append(self._p(f"🌾 {BRAND} - للانتاج الحيواني وتركيب الاعلاف", 'title'))
        story.append(self._p("📄 تقرير التركيب الفني الشامل", 'subtitle'))
        story.append(Spacer(1, 8))

        for line in [f"👨‍💼 المشرف العام: {SUPERVISOR_NAME}",
                     f"📌 الموقع: {city}",
                     f"🐾 الفصيل: {breed}",
                     f"📅 التاريخ: {datetime.now():%Y-%m-%d %H:%M}"]:
            story.append(self._p(line))
        if requester_name:
            story.append(self._p(f"👤 طالب العلف: {requester_name}"))
        story.append(Spacer(1, 12))

        # جدول المعايير
        tdata = [['المعيار', 'القيمة'],
                 ['البروتين المهضوم (DP)', f'{target_dp:.2f}%'],
                 ['معادل النشاء (SE)', f'{computed_se:.2f} وحدة'],
                 ['التكلفة للطن', f'${cost:.2f} ({local_cost:,.2f} {local_sym})']]
        t = Table([[arabic_processor.fix(c) for c in row] for row in tdata],
                  colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#2e7d32')),
        ]))
        story.append(t)

        if standard and 'DP' in standard:
            story.append(Spacer(1, 10))
            story.append(self._p("📏 مقارنة مع المعايير القياسية:", 'heading'))
            comp = [['المقياس', 'المحسوب', 'القياسي', 'الانحراف %', 'التقييم']]
            dev = ((target_dp - standard['DP']) / standard['DP']) * 100 if standard['DP'] > 0 else 0
            grade = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
            comp.append(['DP', f"{target_dp:.2f}%", f"{standard['DP']:.2f}%", f"{dev:.1f}", grade])
            if 'SE' in standard:
                dev = ((computed_se - standard['SE']) / standard['SE']) * 100 if standard['SE'] > 0 else 0
                grade = "✅" if abs(dev) <= 5 else ("⚠️" if abs(dev) <= 10 else "❌")
                comp.append(['SE', f"{computed_se:.2f}", f"{standard['SE']:.2f}", f"{dev:.1f}", grade])
            tc = Table([[arabic_processor.fix(c) for c in row] for row in comp],
                       colWidths=[110, 90, 90, 90, 80])
            tc.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
            ]))
            story.append(tc)

        story.append(PageBreak())
        story.append(self._p("📋 المقادير المعتمدة لتركيب الطن الواحد:", 'heading'))
        ing_data = [['المكون', 'النسبة %', 'كجم/طن']]
        for ing, pct in formula.items():
            ing_data.append([ing, f'{pct:.2f}%', f'{pct*10:.1f}'])
        t2 = Table([[arabic_processor.fix(c) for c in row] for row in ing_data],
                   colWidths=[180, 150, 150])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [HexColor('#ffffff'), HexColor('#f5f5f5')]),
        ]))
        story.append(t2)

        # 🆕 التوصيات الذكية
        if recommendations:
            story.append(Spacer(1, 15))
            story.append(self._p("📌 التوصيات الفنية والكميات الموصى بها:", 'heading'))
            for rec in recommendations:
                story.append(self._p(f"• {rec}", 'rec'))

        # معلومات إضافية
        if extra_info:
            story.append(Spacer(1, 12))
            story.append(self._p("ℹ️ معلومات إضافية:", 'heading'))
            for k, v in extra_info.items():
                if v:
                    story.append(self._p(f"• {k}: {v}", 'rec'))

        # رسم بياني
        try:
            fig, ax = plt.subplots(figsize=(6, 3.2))
            names = list(formula.keys()); vals = list(formula.values())
            colors = ['#1b5e20', '#2e7d32', '#388e3c', '#43a047', '#4caf50', '#66bb6a']
            ax.pie(vals, labels=None, autopct='%1.1f%%', colors=colors[:len(names)])
            ax.legend([arabic_processor.fix(n) for n in names],
                      title=arabic_processor.fix("المكونات"),
                      loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=7)
            ax.set_title(arabic_processor.fix('📊 توزيع المكونات'), fontsize=11)
            buf2 = io.BytesIO()
            plt.savefig(buf2, format='png', dpi=110, bbox_inches='tight')
            plt.close()
            buf2.seek(0)
            story.append(Spacer(1, 10))
            story.append(Image(buf2, width=400, height=210))
        except Exception:
            pass

        # التوقيع
        story.append(Spacer(1, 20))
        story.append(self._p("مع خالص التحية والتقدير،", 'body'))
        story.append(self._p(SUPERVISOR_NAME, 'body'))
        story.append(self._p(SUPERVISOR_TITLE, 'body'))

        # الختم + التذييل
        self._add_stamp_and_footer(story)

        doc.build(story)
        buf.seek(0)
        return buf.getvalue()

    def generate_lab_report(self, analysis_results, animal_type, stage, user_name,
                             standard=None, evaluation=None, recommendations=None):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=45, leftMargin=45,
                                 topMargin=40, bottomMargin=40)
        story = []

        story.append(self._p(BASMALA, 'basmala'))
        story.append(Spacer(1, 5))
        story.append(self._p(f"🔬 تقرير التحليل المخبري المتقدم - {BRAND}", 'title'))
        story.append(self._p(f"👨‍💼 المشرف العام: {SUPERVISOR_NAME}", 'subtitle'))
        story.append(Spacer(1, 8))
        story.append(self._p(f"🐾 الحيوان: {animal_type} | المرحلة: {stage}", 'body'))
        story.append(self._p(f"📅 التاريخ: {datetime.now():%Y-%m-%d %H:%M}", 'body'))
        story.append(Spacer(1, 12))

        if analysis_results:
            if 'components' in analysis_results and analysis_results['components']:
                story.append(self._p("📦 المكونات المدخلة:", 'heading'))
                comp_data = [['المادة', 'الوزن (كجم)', 'النسبة %']]
                tw = sum(analysis_results['components'].values()) or 1
                for name, w in analysis_results['components'].items():
                    if w > 0:
                        comp_data.append([name, f"{w:.1f}", f"{(w/tw)*100:.2f}"])
                tc = Table([[arabic_processor.fix(c) for c in r] for r in comp_data],
                           colWidths=[180, 120, 120])
                tc.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2e7d32')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
                ]))
                story.append(tc)

            story.append(Spacer(1, 10))
            story.append(self._p("📊 النتائج المحسوبة:", 'heading'))
            rd = [['العنصر', 'القيمة']]
            for k, label in [('cp', 'البروتين الخام (CP)'),
                              ('dp', 'البروتين المهضوم (DP)'),
                              ('se', 'معادل النشاء (SE)')]:
                if k in analysis_results:
                    unit = '%' if k in ('cp', 'dp') else ' وحدة'
                    rd.append([label, f"{analysis_results[k]:.2f}{unit}"])
            tr = Table([[arabic_processor.fix(c) for c in r] for r in rd],
                       colWidths=[250, 250])
            tr.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1565C0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#1565C0')),
            ]))
            story.append(tr)

        if recommendations:
            story.append(Spacer(1, 15))
            story.append(self._p("📌 التوصيات الفنية:", 'heading'))
            for rec in recommendations:
                story.append(self._p(f"• {rec}", 'rec'))

        story.append(Spacer(1, 20))
        story.append(self._p(SUPERVISOR_NAME, 'body'))
        story.append(self._p(SUPERVISOR_TITLE, 'body'))
        self._add_stamp_and_footer(story)

        doc.build(story)
        buf.seek(0)
        return buf.getvalue()

    def generate_milk_replacer_report(self, formula, animal_type, age_days,
                                       instructions, user_name, recommendations=None):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=45, leftMargin=45,
                                 topMargin=40, bottomMargin=40)
        story = []

        story.append(self._p(BASMALA, 'basmala'))
        story.append(Spacer(1, 5))
        story.append(self._p(f"🍼 تقرير تركيب بديل الحليب - {BRAND}", 'title'))
        story.append(self._p(f"👨‍💼 المشرف العام: {SUPERVISOR_NAME}", 'subtitle'))
        story.append(Spacer(1, 8))
        story.append(self._p(f"🐾 نوع الحيوان: {animal_type}", 'body'))
        story.append(self._p(f"📅 العمر: {age_days} يوم", 'body'))
        story.append(self._p(f"📅 التاريخ: {datetime.now():%Y-%m-%d %H:%M}", 'body'))
        story.append(Spacer(1, 12))

        story.append(self._p("📋 مكونات بديل الحليب:", 'heading'))
        ing_data = [['المكون', 'النسبة %', 'جم/لتر']]
        for ing, pct in formula.items():
            ing_data.append([ing, f'{pct:.2f}%', f'{pct*10:.1f}'])
        t = Table([[arabic_processor.fix(c) for c in r] for r in ing_data],
                  colWidths=[200, 130, 130])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1b5e20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdbdbd')),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))
        story.append(self._p("📌 تعليمات التقديم:", 'heading'))
        for line in instructions.split('\n'):
            if line.strip():
                story.append(self._p(f"• {line.strip()}", 'rec'))

        if recommendations:
            story.append(Spacer(1, 12))
            story.append(self._p("📌 التوصيات الفنية:", 'heading'))
            for rec in recommendations:
                story.append(self._p(f"• {rec}", 'rec'))

        story.append(Spacer(1, 20))
        story.append(self._p(SUPERVISOR_NAME, 'body'))
        story.append(self._p(SUPERVISOR_TITLE, 'body'))
        self._add_stamp_and_footer(story)
        doc.build(story)
        buf.seek(0)
        return buf.getvalue()

pdf_generator = ProfessionalPDFGenerator()
# =====================================================================
# مكتبة الأعلاف الكبرى
# =====================================================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "ADF": 3.2, "EE": 3.8, "ASH": 1.3},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "ADF": 3.5, "EE": 3.5, "ASH": 1.4},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "ADF": 7.5, "EE": 2.2, "ASH": 2.5},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0, "NDF": 12.5, "ADF": 5.5, "EE": 3.0, "ASH": 1.8},
        "قمح محلي": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "ADF": 3.8, "EE": 2.0, "ASH": 1.6},
        "جريش أرز": {"CP": 7.8, "DC": 0.82, "SE": 82.0, "NDF": 5.5, "ADF": 2.5, "EE": 8.5, "ASH": 4.2},
        "دخن": {"CP": 11.0, "DC": 0.75, "SE": 68.0, "NDF": 15.5, "ADF": 6.5, "EE": 4.0, "ASH": 2.2},
        "شوفان": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "ADF": 13.5, "EE": 5.0, "ASH": 3.0},
        "تفل العنب المجفف": {"CP": 12.0, "DC": 0.50, "SE": 45.0, "NDF": 45.0, "ADF": 30.0, "EE": 5.0, "ASH": 8.0},
        "نخالة الأرز الدهنية": {"CP": 12.5, "DC": 0.70, "SE": 55.0, "NDF": 30.0, "ADF": 15.0, "EE": 15.0, "ASH": 8.0},
        "علف الشعير المستنبت": {"CP": 15.0, "DC": 0.75, "SE": 60.0, "NDF": 25.0, "ADF": 12.0, "EE": 3.0, "ASH": 5.0}
    },
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "ADF": 8.5, "EE": 1.5, "ASH": 5.5},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "ADF": 8.0, "EE": 1.8, "ASH": 6.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0, "NDF": 12.0, "ADF": 7.0, "EE": 1.5, "ASH": 6.2},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "ADF": 25.5, "EE": 2.5, "ASH": 6.5},
        "كسب بذور القطن": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "ADF": 15.5, "EE": 1.2, "ASH": 6.5},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0, "NDF": 18.5, "ADF": 10.5, "EE": 2.8, "ASH": 5.8},
        "كسب السمسم": {"CP": 42.0, "DC": 0.84, "SE": 70.0, "NDF": 14.5, "ADF": 9.5, "EE": 8.5, "ASH": 12.5},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0, "NDF": 8.5, "ADF": 5.5, "EE": 2.5, "ASH": 3.5},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0, "NDF": 55.5, "ADF": 35.5, "EE": 6.5, "ASH": 4.5},
        "كسب بذور اللفت (كانولا)": {"CP": 38.0, "DC": 0.82, "SE": 62.0, "NDF": 28.0, "ADF": 18.0, "EE": 3.5, "ASH": 7.5}
    },
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "ADF": 12.5, "EE": 3.5, "ASH": 5.5},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "ADF": 32.5, "EE": 2.0, "ASH": 10.5},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "ADF": 0.8, "EE": 0.5, "ASH": 8.5},
        "تبن قمح": {"CP": 3.2, "DC": 0.35, "SE": 18.0, "NDF": 72.5, "ADF": 45.5, "EE": 1.5, "ASH": 8.5},
        "قشر فول سوداني": {"CP": 5.0, "DC": 0.30, "SE": 15.0, "NDF": 65.5, "ADF": 42.5, "EE": 1.0, "ASH": 5.5},
        "سرسة الأرز": {"CP": 2.5, "DC": 0.25, "SE": 12.0, "NDF": 68.5, "ADF": 48.5, "EE": 12.5, "ASH": 15.5},
        "مخلفات مصانع البسكويت": {"CP": 10.0, "DC": 0.80, "SE": 65.0, "NDF": 8.0, "ADF": 4.0, "EE": 12.0, "ASH": 3.0},
        "قش الأرز المعالج": {"CP": 4.0, "DC": 0.40, "SE": 25.0, "NDF": 65.0, "ADF": 40.0, "EE": 1.5, "ASH": 12.0}
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "ADF": 1.5, "EE": 8.5, "ASH": 22.5},
        "مسحوق أسماك فاخر 72%": {"CP": 72.0, "DC": 0.90, "SE": 72.0, "NDF": 2.0, "ADF": 1.0, "EE": 9.5, "ASH": 18.5},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0, "NDF": 3.5, "ADF": 2.5, "EE": 10.5, "ASH": 32.5},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0, "NDF": 8.5, "ADF": 4.5, "EE": 3.5, "ASH": 12.5},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "ADF": 8.5, "EE": 3.0, "ASH": 15.5},
        "بروتين مصل الحليب (WPC)": {"CP": 80.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 3.0, "ASH": 3.0},
        "بروتين الدم المجفف": {"CP": 85.0, "DC": 0.92, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.5, "ASH": 5.0}
    },
    "🧪 الأحماض الأمينية": {
        "ليسين (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.5},
        "ميثيونين (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.3},
        "ثريونين (L-Threonine)": {"CP": 72.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.2},
        "تريبتوفان": {"CP": 85.0, "DC": 1.00, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 0.1}
    },
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس بياض": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بريمكس مجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "إنزيم الفايتيز (Phytase)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 5.0},
        "إنزيم NSP": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 3.0},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 85.0},
        "خميرة الخبز": {"CP": 45.0, "DC": 0.85, "SE": 35.0, "NDF": 5.0, "ADF": 2.0, "EE": 2.5, "ASH": 7.0}
    },
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 98.5},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.9},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.0},
        "أكسيد المغنيسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 99.5},
        "يوريا علفية": {"CP": 287.0, "DC": 0.95, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 1.0},
        "كلوريد الكولين": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 75.0}
    },
    "🍼 مكونات بدائل الحليب": {
        "مصل الحليب المجفف": {"CP": 12.0, "DC": 0.95, "SE": 35.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.0},
        "حليب مجفف خالي الدسم": {"CP": 34.0, "DC": 0.95, "SE": 40.0, "NDF": 0.0, "ADF": 0.0, "EE": 1.0, "ASH": 8.5},
        "دهن نباتي": {"CP": 0.0, "DC": 0.0, "SE": 10.0, "NDF": 0.0, "ADF": 0.0, "EE": 99.0, "ASH": 0.0},
        "ليسيثين الصويا": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 95.0, "ASH": 0.5},
        "فيتامينات ومعادن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "ADF": 0.0, "EE": 0.0, "ASH": 100.0},
        "بروتين الصويا المركز": {"CP": 65.0, "DC": 0.90, "SE": 30.0, "NDF": 2.0, "ADF": 1.0, "EE": 1.0, "ASH": 5.5}
    }
}

FLAT_FEED_DB = {}
for cat, items in BIG_FEEDS_LIBRARY.items():
    for name, nut in items.items():
        FLAT_FEED_DB[name] = nut

# =====================================================================
# المعايير القياسية
# =====================================================================
STANDARD_VALUES = {
    "أبقار": {
        "تسمين عجول": {"DP": 12.0, "SE": 68.0, "CP": 15.0, "Energy": 2.8},
        "حليب/إدرار": {"DP": 14.0, "SE": 70.0, "CP": 17.5, "Energy": 3.0},
        "حمل/دفع غذائي": {"DP": 11.0, "SE": 65.0, "CP": 13.8, "Energy": 2.7},
        "صيانة": {"DP": 9.0, "SE": 60.0, "CP": 11.3, "Energy": 2.5},
        "تسمين مكثف": {"DP": 13.0, "SE": 72.0, "CP": 16.3, "Energy": 2.9}
    },
    "أغنام": {
        "تسمين حملان": {"DP": 13.0, "SE": 66.0, "CP": 16.3, "Energy": 2.7},
        "نعاج مرضعات": {"DP": 14.5, "SE": 68.0, "CP": 18.1, "Energy": 2.9},
        "نعاج حامل": {"DP": 11.5, "SE": 62.0, "CP": 14.4, "Energy": 2.6},
        "نعاج جافة": {"DP": 8.5, "SE": 58.0, "CP": 10.6, "Energy": 2.4}
    },
    "ماعز": {
        "تسمين جديان": {"DP": 12.5, "SE": 64.0, "CP": 15.6, "Energy": 2.7},
        "عنزات حلابة": {"DP": 14.0, "SE": 66.0, "CP": 17.5, "Energy": 2.8},
        "عنزات حامل": {"DP": 11.0, "SE": 60.0, "CP": 13.8, "Energy": 2.6},
        "صيانة": {"DP": 8.0, "SE": 56.0, "CP": 10.0, "Energy": 2.4}
    },
    "خيول": {
        "راحة/صيانة": {"DP": 9.0, "SE": 58.0, "CP": 11.3, "Energy": 2.4},
        "عمل خفيف": {"DP": 10.0, "SE": 60.0, "CP": 12.5, "Energy": 2.5},
        "عمل متوسط": {"DP": 11.0, "SE": 62.0, "CP": 13.8, "Energy": 2.6},
        "عمل مكثف": {"DP": 13.0, "SE": 65.0, "CP": 16.3, "Energy": 2.8},
        "سباق": {"DP": 14.0, "SE": 68.0, "CP": 17.5, "Energy": 3.0},
        "أمهار نامية": {"DP": 13.0, "SE": 64.0, "CP": 16.3, "Energy": 2.7},
        "فرسات مرضعات": {"DP": 14.0, "SE": 66.0, "CP": 17.5, "Energy": 2.9}
    },
    "إبل": {
        "راحة/صيانة": {"DP": 8.0, "SE": 55.0, "CP": 10.0, "Energy": 2.3},
        "حمل/رضاعة": {"DP": 10.0, "SE": 58.0, "CP": 12.5, "Energy": 2.5},
        "إنتاج حليب": {"DP": 12.0, "SE": 60.0, "CP": 15.0, "Energy": 2.7},
        "تسمين": {"DP": 11.0, "SE": 62.0, "CP": 13.8, "Energy": 2.6},
        "عمل/نقل": {"DP": 10.0, "SE": 58.0, "CP": 12.5, "Energy": 2.5}
    },
    "دواجن": {
        "بادي (0-14 يوم)": {"DP": 22.0, "SE": 76.0, "CP": 27.5, "Energy": 3.0},
        "نامي (15-28 يوم)": {"DP": 20.0, "SE": 74.0, "CP": 25.0, "Energy": 3.1},
        "ناهي (29-42 يوم)": {"DP": 18.0, "SE": 72.0, "CP": 22.5, "Energy": 3.2},
        "ناهي متقدم (43+ يوم)": {"DP": 16.0, "SE": 70.0, "CP": 20.0, "Energy": 3.0}
    },
    "أسماك": {
        "زريعة/بادئ": {"DP": 32.0, "SE": 70.0, "CP": 40.0, "Energy": 3.2},
        "نمو": {"DP": 28.0, "SE": 68.0, "CP": 35.0, "Energy": 3.0},
        "تسمين نهائي": {"DP": 26.0, "SE": 66.0, "CP": 32.5, "Energy": 2.9},
        "زريعة متقدمة": {"DP": 30.0, "SE": 69.0, "CP": 37.5, "Energy": 3.1}
    }
}

ANIMAL_IMAGES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?q=80&w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?q=80&w=600",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?q=80&w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?q=80&w=600",
    "إبل": "https://images.unsplash.com/photo-1502175353174-a7a70e73b362?q=80&w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?q=80&w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?q=80&w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600"
}

EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "ليبيا": {"rate": 4.80, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"},
    "دولار أمريكي": {"rate": 1.0, "sym": "USD"}
}
# =====================================================================
# AuthManager
# =====================================================================
class AuthManager:
    def __init__(self):
        self.db = get_db()
        self._init_users()

    def _init_users(self):
        defaults = [
            ('admin', 'admin123', 'owner', SUPERVISOR_NAME, 'admin@tawornology.com',
             '+249123456789', 'تغذية حيوان', 10),
            ('specialist', 'spec123', 'specialist', 'المختص العام',
             'specialist@tawornology.com', '+249123456788', 'تغذية', 8),
            ('nutritionist', 'nutri123', 'nutritionist', 'أخصائي التغذية',
             'nutrition@tawornology.com', '+249123456786', 'تغذية', 7),
            ('veterinarian', 'vet123', 'veterinarian', 'الطبيب البيطري',
             'vet@tawornology.com', '+249123456785', 'طب بيطري', 9),
        ]
        for u, p, r, n, e, ph, sp, exp in defaults:
            if not self.db.execute_query("SELECT 1 FROM users WHERE username=?", (u,)):
                self.create_user(u, p, r, n, e, ph, sp, exp)
        if not self.db.execute_query("SELECT 1 FROM users WHERE username='public'"):
            self.create_user('public', 'public123', 'public', 'زائر',
                             'public@tawornology.com', '+249123456780', 'عام', 0)

    def create_user(self, username, password, role, full_name, email, phone,
                     specialty="", experience=0):
        uid = secrets.token_hex(16)
        h = hashlib.sha256(password.encode()).hexdigest()
        self.db.insert_record('users', {
            'user_id': uid, 'username': username, 'password_hash': h,
            'role': role, 'full_name': full_name, 'email': email, 'phone': phone,
            'specialty': specialty, 'experience_years': experience,
            'created_date': datetime.now().isoformat(), 'last_login': '',
            'is_active': 1, 'is_public': 1 if role == 'public' else 0
        })
        return uid

    def authenticate(self, username, password):
        users = self.db.execute_query(
            "SELECT * FROM users WHERE username=? AND is_active=1", (username,))
        if users:
            u = users[0]
            if u['password_hash'] == hashlib.sha256(password.encode()).hexdigest():
                self.db.update_record('users',
                                       {'last_login': datetime.now().isoformat()},
                                       {'user_id': u['user_id']})
                return {'user_id': u['user_id'], 'username': u['username'],
                        'role': u['role'], 'full_name': u['full_name'],
                        'email': u['email'], 'phone': u['phone'],
                        'specialty': u['specialty'], 'experience_years': u['experience_years']}
        return None

    def login_public(self):
        users = self.db.execute_query("SELECT * FROM users WHERE username='public'")
        if users:
            u = users[0]
            return {'user_id': u['user_id'], 'username': 'public', 'role': 'public',
                    'full_name': 'زائر', 'email': u['email'], 'phone': u['phone'],
                    'specialty': 'عام', 'experience_years': 0}
        return None

# =====================================================================
# PricePredictor
# =====================================================================
class PricePredictor:
    def __init__(self):
        self.db = get_db()

    def get_price_trend(self, name, days=30):
        rows = self.db.execute_query(
            "SELECT price FROM price_history WHERE ingredient_name=? "
            "ORDER BY record_date DESC LIMIT ?", (name, days))
        if len(rows) < 3:
            return {'trend': 'stable', 'change_percent': 0, 'volatility': 0,
                    'current_price': rows[0]['price'] if rows else None}
        prices = [r['price'] for r in rows]
        x = np.arange(len(prices)).reshape(-1, 1)
        model = LinearRegression().fit(x, np.array(prices))
        slope = model.coef_[0]
        trend = 'up' if slope > 0.5 else 'down' if slope < -0.5 else 'stable'
        return {'trend': trend,
                'change_percent': ((prices[0] - prices[-1]) / prices[-1]) * 100 if prices[-1] else 0,
                'volatility': float(np.std(prices) / np.mean(prices)) if np.mean(prices) else 0,
                'current_price': prices[0]}

    def predict_price(self, name, days_ahead=7):
        rows = self.db.execute_query(
            "SELECT price FROM price_history WHERE ingredient_name=? "
            "ORDER BY record_date DESC LIMIT 30", (name,))
        if len(rows) < 5:
            t = self.get_price_trend(name)
            return {'prediction': t.get('current_price'), 'confidence': 0.3,
                    'current_price': t.get('current_price'), 'trend': t['trend']}
        prices = [r['price'] for r in rows]
        weights = np.arange(1, len(prices) + 1)
        wavg = np.average(prices, weights=weights)
        trend = (prices[0] - prices[-1]) / len(prices)
        return {'prediction': max(0, wavg + trend * days_ahead),
                'confidence': min(1, len(prices) / 30),
                'current_price': prices[0], 'trend': self.get_price_trend(name)['trend']}

# =====================================================================
# SmartLabSystem
# =====================================================================
class SmartLabSystem:
    def __init__(self):
        self.db = get_db()
        self._reader = None
        self._lock = threading.Lock()

    @property
    def reader(self):
        if self._reader is None:
            with self._lock:
                if self._reader is None:
                    if EASYOCR_AVAILABLE:
                        try:
                            self._reader = easyocr.Reader(['ar', 'en'], gpu=False, verbose=False)
                        except Exception:
                            self._reader = False
                    else:
                        self._reader = False
        return self._reader if self._reader else None

    def analyze_image(self, image):
        if not OCR_AVAILABLE and not EASYOCR_AVAILABLE:
            return None, "مكتبات OCR غير مثبتة."
        try:
            buf = io.BytesIO()
            image.save(buf, format='PNG')
            return self._analyze_cached(buf.getvalue())
        except Exception as e:
            return None, str(e)

    @lru_cache(maxsize=32)
    def _analyze_cached(self, img_bytes):
        try:
            img = PILImage_module.open(io.BytesIO(img_bytes))
            results = []
            reader = self.reader
            if reader:
                for _, text, prob in reader.readtext(np.array(img)):
                    if prob > 0.3:
                        results.append(text)
            elif OCR_AVAILABLE:
                results = pytesseract.image_to_string(img, lang='ara+eng').split('\n')
            return self._parse(results), None
        except Exception as e:
            return None, str(e)

    def _parse(self, texts):
        data = {'sample_name': '', 'cp': None, 'dc': None, 'se': None, 'ndf': None,
                'adf': None, 'ee': None, 'ash': None, 'moisture': None}
        patterns = {
            'cp': [r'بروتين\s*خام\s*[:=]?\s*([\d.]+)', r'CP\s*[:=]?\s*([\d.]+)'],
            'dc': [r'معامل\s*الهضم\s*[:=]?\s*([\d.]+)', r'DC\s*[:=]?\s*([\d.]+)'],
            'se': [r'معادل\s*النشاء\s*[:=]?\s*([\d.]+)', r'SE\s*[:=]?\s*([\d.]+)'],
            'ndf': [r'NDF\s*[:=]?\s*([\d.]+)'], 'adf': [r'ADF\s*[:=]?\s*([\d.]+)'],
            'ee': [r'دهن\s*خام\s*[:=]?\s*([\d.]+)', r'EE\s*[:=]?\s*([\d.]+)'],
            'ash': [r'رماد\s*[:=]?\s*([\d.]+)', r'ASH\s*[:=]?\s*([\d.]+)'],
            'moisture': [r'رطوبة\s*[:=]?\s*([\d.]+)']
        }
        for t in texts:
            t = t.strip()
            if 'اسم' in t and not data['sample_name']:
                parts = t.split(':')
                if len(parts) > 1:
                    data['sample_name'] = parts[1].strip()
            for k, pl in patterns.items():
                if data[k] is None:
                    for p in pl:
                        m = re.search(p, t, re.IGNORECASE)
                        if m:
                            try:
                                data[k] = float(m.group(1))
                                break
                            except Exception:
                                pass
        return data

    def save_lab_result(self, d):
        rid = secrets.token_hex(16)
        self.db.insert_record('lab_results', {
            'result_id': rid, 'sample_name': d.get('sample_name', ''),
            'sample_type': d.get('sample_type', ''),
            'cp': d.get('cp', 0.0), 'dc': d.get('dc', 0.0), 'se': d.get('se', 0.0),
            'ndf': d.get('ndf', 0.0), 'adf': d.get('adf', 0.0), 'ee': d.get('ee', 0.0),
            'ash': d.get('ash', 0.0), 'moisture': d.get('moisture', 0.0),
            'analysis_date': datetime.now().isoformat(),
            'analyzed_by': d.get('analyzed_by', ''), 'notes': d.get('notes', ''),
            'image_path': d.get('image_path', '')
        })
        return rid

    def get_lab_results(self, limit=50):
        return self.db.execute_query(
            "SELECT * FROM lab_results ORDER BY analysis_date DESC LIMIT ?", (limit,))

# =====================================================================
# FarmManagementSystem
# =====================================================================
class FarmManagementSystem:
    def __init__(self):
        self.db = get_db()

    def create_farm(self, name, ftype, owner, phone, location="", area=0.0):
        fid = secrets.token_hex(16)
        self.db.insert_record('farms', {
            'farm_id': fid, 'farm_name': name, 'farm_type': ftype,
            'owner_name': owner, 'owner_phone': phone, 'location': location,
            'area': area, 'created_date': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        })
        return fid

    def create_cycle(self, farm_id, ctype, count, breed, tw=0.0, ta=0):
        cid = secrets.token_hex(16)
        self.db.insert_record('production_cycles', {
            'cycle_id': cid, 'farm_id': farm_id, 'cycle_type': ctype,
            'start_date': datetime.now().isoformat(), 'end_date': '',
            'initial_count': count, 'breed': breed, 'target_weight': tw,
            'target_age': ta, 'status': 'active', 'notes': ''
        })
        return cid

# =====================================================================
# InventoryManager
# =====================================================================
class InventoryManager:
    @staticmethod
    def check_stock_levels():
        warnings = {}
        inv = st.session_state.get("inventory", {})
        for item, data in inv.items():
            qty = data["quantity"] if isinstance(data, dict) else data
            thr = data.get("min_threshold", 5.0) if isinstance(data, dict) else 5.0
            if qty <= 0:
                warnings[item] = {"status": "نفذ", "level": "critical"}
            elif qty < thr:
                warnings[item] = {"status": "منخفض", "level": "warning"}
        return warnings

    @staticmethod
    def get_summary():
        inv = st.session_state.get("inventory", {})
        total_items = len(inv)
        total_qty = sum((d["quantity"] if isinstance(d, dict) else d) for d in inv.values())
        low = sum(1 for d in inv.values()
                   if (d["quantity"] if isinstance(d, dict) else d) <
                      (d.get("min_threshold", 5.0) if isinstance(d, dict) else 5.0))
        return {"total_items": total_items, "total_quantity": total_qty, "low_stock": low}

# =====================================================================
# Excel Export
# =====================================================================
def export_to_excel(data, sheet_name="Report"):
    if not OPENPYXL_AVAILABLE:
        return None
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name
        ws.sheet_view.rightToLeft = True
        ws.append([f"{BRAND} - تقرير رسمي"])
        ws.merge_cells('A1:D1')
        ws['A1'].font = Font(size=14, bold=True, color="1B5E20")
        ws['A1'].alignment = Alignment(horizontal="center")
        ws.append([f"التاريخ: {datetime.now():%Y-%m-%d %H:%M}"])
        ws.append([])

        if isinstance(data, dict):
            for k, v in data.items():
                ws.append([k, str(v)])
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            headers = list(data[0].keys())
            ws.append(headers)
            for cell in ws[ws.max_row]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill("solid", fgColor="2E7D32")
            for row in data:
                ws.append([row.get(h, "") for h in headers])

        for col in ws.columns:
            ml = max((len(str(c.value)) for c in col if c.value), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(ml + 4, 50)

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        st.error(f"خطأ Excel: {e}")
        return None

# =====================================================================
# ScientificReferenceSystem
# =====================================================================
class ScientificReferenceSystem:
    REFERENCES = {
        "general": {"title": "تغذية عامة", "icon": "📚", "references": [
            {"id": "REF001", "authors": "McDonald et al.", "year": 2011,
             "title": "Animal Nutrition", "publisher": "Pearson",
             "summary": "المرجع الأساسي في تغذية الحيوان."}]},
        "poultry": {"title": "تغذية الدواجن", "icon": "🐔", "references": [
            {"id": "REF010", "authors": "Leeson & Summers", "year": 2009,
             "title": "Commercial Poultry Nutrition", "publisher": "Nottingham",
             "summary": "المرجع العملي في تغذية الدواجن."}]},
        "ruminants": {"title": "تغذية المجترات", "icon": "🐄", "references": [
            {"id": "REF012", "authors": "Church", "year": 1993,
             "title": "The Ruminant Animal", "publisher": "Waveland",
             "summary": "فسيولوجيا الهضم والتغذية للمجترات."}]},
        "milk_replacers": {"title": "بدائل الحليب", "icon": "🍼", "references": [
            {"id": "REF040", "authors": "Davis & Drackley", "year": 1998,
             "title": "The Development, Nutrition, and Management of the Young Calf",
             "publisher": "Iowa State", "summary": "تغذية العجول الصغيرة."}]}
    }

    KNOWLEDGE_BASE = {
        "البروتين المهضوم": "البروتين المهضوم هو كمية البروتين التي يستطيع الحيوان هضمها وامتصاصها فعلياً.",
        "معادل النشاء": "معادل النشاء (SE) مقياس لكمية الطاقة التي يوفرها العلف.",
        "تركيب العلف": "يتم باستخدام محرك الاستمثال الخطي (Linear Programming).",
        "EPEF": "مؤشر الأداء الأوروبي = (الحيوية × الوزن الحي) / (العمر × معامل التحويل) × 100.",
    }

    @staticmethod
    def get_knowledge_answer(q):
        ql = q.lower()
        for k, v in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            if k in ql:
                return {"answer": v, "simplified": v}
        return None
        # =====================================================================
# Session State
# =====================================================================
defaults = {
    "approved": False, "user_role": None, "login_welcome_shown": False,
    "login_attempts": 0, "last_login_time": None, "session_token": None,
    "broiler_farms": {}, "selected_farm": None, "whatsapp_alerts_sent": {},
    "query_history": [], "analysis_results": None,
    "analysis_animal": "غير محدد", "analysis_stage": "غير محدد",
    "daily_production_log": [], "basmala_played": False, "welcome_played": False,
    "guide_played": {}, "active_formula": {}, "active_cp_tag": 12.0,
    "active_se_tag": 65.0, "active_breed_tag": "سلالة عامة",
    "active_animal_img": ANIMAL_IMAGES["عام"],
    "active_stage_title": "إنتاج عام", "computed_ton_cost": 280.0,
    "lab_sample_name": "", "lab_cp": 0.0, "lab_dc": 0.0, "lab_se": 0.0,
    "lab_ndf": 0.0, "lab_adf": 0.0, "lab_ee": 0.0, "lab_ash": 0.0, "lab_moisture": 0.0,
    "lab_notes": "",
    "global_livestock_prices": {
        "عجول تسمين ($)": 1350.0, "أبقار محلية ($)": 900.0,
        "ضأن ($)": 180.0, "ماعز نوبي ($)": 130.0,
        "خيول عربية ($)": 4500.0, "إبل عربية ($)": 2500.0},
    "global_products_prices": {
        "كيلو لحم بقري ($)": 7.50, "كيلو لحم ضأن ($)": 9.00,
        "كيلو لحم دجاج ($)": 3.80, "طبق بيض ($)": 4.20,
        "لتر حليب خام ($)": 0.90, "لتر حليب إبل ($)": 1.50},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if "inventory" not in st.session_state:
    st.session_state["inventory"] = {
        name: {"quantity": 25.0, "min_threshold": 5.0, "unit": "طن",
               "last_updated": datetime.now().isoformat(), "supplier": "غير محدد"}
        for name in FLAT_FEED_DB.keys()}

if "smart_lab_system" not in st.session_state:
    st.session_state["smart_lab_system"] = SmartLabSystem()

@st.cache_resource
def get_farm_system():
    return FarmManagementSystem()
farm_system = get_farm_system()

# =====================================================================
# شريط الدعاء + CSS
# =====================================================================
def render_dua_bar():
    st.markdown("""
    <style>
    @keyframes scrollDua {
        0% { transform: translateX(100%); opacity: 0; }
        5% { transform: translateX(0%); opacity: 1; }
        85% { transform: translateX(0%); opacity: 1; }
        95% { transform: translateX(-100%); opacity: 0; }
        100% { transform: translateX(-100%); opacity: 0; }
    }
    @keyframes pulseHeart {
        0%, 100% { transform: scale(1); color: #ff6b6b; }
        50% { transform: scale(1.5); color: #ff1744; }
    }
    .dua-container {
        background: linear-gradient(135deg, #0d1b2a, #1a237e, #4a148c, #0d1b2a);
        padding: 22px 0; border-radius: 24px; margin-bottom: 20px;
        overflow: hidden; border: 3px solid #ffd700;
        box-shadow: 0 8px 40px rgba(255,215,0,0.5); direction: rtl;
    }
    .dua-text {
        display: inline-block; white-space: nowrap;
        animation: scrollDua 24s ease-in-out infinite;
        font-size: 1.7rem; font-weight: 800; color: #ffd700;
        padding: 0 25px; direction: rtl; letter-spacing: 2px;
    }
    .dua-text .emoji-heart { display: inline-block; animation: pulseHeart 1.2s infinite; margin: 0 8px; }
    .dua-text .name-highlight { color: #ffab40; font-weight: 900;
        background: rgba(255,215,0,0.15); padding: 0 10px; border-radius: 8px; }
    </style>
    <div class="dua-container">
        <div class="dua-text">
            ❤️ اللهم اغفر لـ <span class="name-highlight">إسماعيل تاور</span> و <span class="name-highlight">ابتسام</span>
            وارحمهما وأدخلهما فسيح جناتك ❤️ اللهم اجعل قبرهما روضة من رياض الجنة ❤️
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
* { font-family: 'Cairo', sans-serif; }
.main-box {
    background: rgba(255,255,255,0.92); padding: 35px; border-radius: 24px;
    box-shadow: 0 25px 70px rgba(0,0,0,0.15); margin-bottom: 35px;
}
.section-title {
    color: #1b5e20; border-right: 6px solid #2e7d32; padding: 14px 22px;
    text-align: right; font-size: 1.6rem; font-weight: 700;
    margin: 25px 0 20px 0; border-radius: 14px;
    background: linear-gradient(to left, rgba(46,125,50,0.12), transparent);
}
.formula-item {
    background: linear-gradient(135deg, #ffffff, #e8f5e9);
    padding: 16px 22px; border-radius: 14px; margin-bottom: 10px;
    font-weight: 600; color: #1b5e20;
    border-right: 5px solid #2e7d32;
    display: flex; justify-content: space-between;
}
.metric-card {
    background: white; padding: 22px; border-radius: 18px;
    box-shadow: 0 6px 30px rgba(0,0,0,0.08); text-align: center;
}
.metric-card .number { font-size: 2.2rem; font-weight: 900; color: #1b5e20; }
.metric-card .label { font-size: 0.95rem; color: #666; }
</style>
""", unsafe_allow_html=True)

def guide_section(name, text):
    with st.expander(f"📘 دليل استخدام {name}", expanded=False):
        st.markdown(f"<div style='background:#f0f8ff; padding:15px; border-radius:10px; direction:rtl;'>{text}</div>",
                    unsafe_allow_html=True)
        if st.button(f"🔊 تشغيل الدليل ({name})", key=f"vg_{name}"):
            voice_guide(text)

# =====================================================================
# شاشة الدخول
# =====================================================================
if not st.session_state["approved"]:
    render_dua_bar()
    st.markdown('<div class="main-box" style="max-width:550px; margin:80px auto; direction:rtl;">',
                unsafe_allow_html=True)
    if img_base64:
        st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" style="width:100px; height:100px; border-radius:50%; border:3px solid #d4af37; display:block; margin:0 auto;">',
                    unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:#1a237e; text-align:center;'>🌾 {BRAND}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#555;'>{SUPERVISOR_NAME}</p>", unsafe_allow_html=True)

    if st.button("🔊 الشرح الصوتي الكامل", use_container_width=True):
        play_full_guide_audio()

    if st.button("👤 دخول كزائر", type="primary", use_container_width=True):
        auth = AuthManager()
        user = auth.login_public()
        if user:
            st.session_state["approved"] = True
            st.session_state["user_role"] = "public"
            st.session_state["login_welcome_shown"] = False
            st.session_state["user"] = user
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    option = st.radio("طريقة الدخول:", ["كود سري", "مستخدم/كلمة"], horizontal=True)

    if option == "كود سري":
        code = st.text_input("🔑 الكود:", type="password")
        if st.button("🔓 دخول", use_container_width=True):
            if code.strip() in CODES_DB:
                st.session_state["approved"] = True
                st.session_state["user_role"] = CODES_DB[code.strip()]["role"]
                st.session_state["login_welcome_shown"] = False
                st.session_state["user"] = {'full_name': CODES_DB[code.strip()]['name']}
                st.rerun()
            else:
                st.error("❌ كود خاطئ")
    else:
        u = st.text_input("المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("🔓 دخول", use_container_width=True):
            auth = AuthManager()
            user = auth.authenticate(u, p)
            if user:
                st.session_state["approved"] = True
                st.session_state["user_role"] = user['role']
                st.session_state["login_welcome_shown"] = False
                st.session_state["user"] = user
                st.rerun()
            else:
                st.error("❌ بيانات خاطئة")
        st.caption("💡 admin / admin123")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

if not st.session_state["login_welcome_shown"]:
    st.toast(f"مرحباً بك في {BRAND}", icon="🌾")
    voice_welcome(st.session_state["user_role"])
    st.session_state["login_welcome_shown"] = True

render_dua_bar()

# =====================================================================
# الواجهة الرئيسية
# =====================================================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)
col_u, col_out = st.columns([0.8, 0.2])
with col_out:
    if st.button("🚪 خروج", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k not in ["inventory", "email_password", "smart_lab_system"]:
                del st.session_state[k]
        st.session_state["approved"] = False
        st.rerun()

st.markdown(f"<h1 style='color:#1a237e; text-align:right;'>🌾 {BRAND}</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='color:#c62828; text-align:right;'>{SUPERVISOR_NAME}</h3>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# =====================================================================
# دالة التركيب الرئيسية
# =====================================================================
def render_feed_formulation(animal_key, display_name, icon, breeds, stages,
                             default_dp, default_se, img_key, has_measurements=True):
    st.markdown(f'<div class="section-title">{icon} {display_name} - تركيب العلف</div>',
                unsafe_allow_html=True)
    requester = st.text_input("👤 اسم طالب العلف:", key=f"{animal_key}_req")

    adjusted_dp, adjusted_se = default_dp, default_se
    if has_measurements:
        c1, c2, c3 = st.columns(3)
        with c1:
            g = st.number_input("محيط الصدر (سم)", 20.0, 300.0, 150.0, key=f"{animal_key}_g")
        with c2:
            l = st.number_input("طول الجسم (سم)", 20.0, 300.0, 130.0, key=f"{animal_key}_l")
        with c3:
            a = st.number_input("العمر (شهر)", 1, 120, 12, key=f"{animal_key}_a")
        wf = {"cattle": 10838, "sheep": 15500, "goat": 15000, "horse": 11877, "camel": 13000}.get(animal_key, 12000)
        weight = (g ** 2 * l) / wf
        st.info(f"**الوزن التقديري:** {weight:.1f} كجم")

    c_b, c_s = st.columns(2)
    with c_b:
        breed = st.selectbox("السلالة:", breeds, key=f"{animal_key}_br")
    with c_s:
        stage = st.selectbox("المرحلة:", stages, key=f"{animal_key}_st")

    c_a, c_p = st.columns(2)
    with c_a:
        age = st.number_input("العمر (شهر)", 1, 240, 24, key=f"{animal_key}_age")
    with c_p:
        phys = st.selectbox("الحالة الفسيولوجية:",
                             ["طبيعي", "حامل", "مرضع", "صائم", "نشاط مكثف", "استشفاء", "نمو سريع"],
                             key=f"{animal_key}_ph")

    basis = st.radio("أساس البروتين:", ["DP", "CP"], horizontal=True, key=f"{animal_key}_b")
    if basis == "DP":
        target_protein = st.number_input("نسبة DP (%)", 5.0, 50.0, float(adjusted_dp), key=f"{animal_key}_dp")
        actual_dp = target_protein
    else:
        target_protein = st.number_input("نسبة CP (%)", 5.0, 60.0, float(default_dp/0.8), key=f"{animal_key}_cp")
        actual_dp = target_protein * 0.80

    target_se = st.number_input("معادل النشاء (SE):", 10.0, 90.0, float(adjusted_se), key=f"{animal_key}_se")

    state_mult = {"طبيعي": 1.0, "حامل": 1.15, "مرضع": 1.30, "صائم": 0.85,
                  "نشاط مكثف": 1.25, "استشفاء": 1.20, "نمو سريع": 1.35}
    mult = state_mult.get(phys, 1.0)
    actual_dp *= mult
    target_se *= mult

    st.markdown("#### 🌾 المكونات")
    default_ings = {
        "cattle": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                   "أمباز الفول السوداني", "مركزات خيول ومجترات", "ملح الطعام",
                   "الحجر الجيري", "فوسفات ثنائي الكالسيوم (DCP)", "بيكربونات الصوديوم (الصودا)"],
        "sheep": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                  "أمباز الفول السوداني", "مركزات خيول ومجترات", "ملح الطعام",
                  "الحجر الجيري", "فوسفات ثنائي الكالسيوم (DCP)", "بيكربونات الصوديوم (الصودا)"],
        "goat": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                 "أمباز الفول السوداني", "مركزات خيول ومجترات", "ملح الطعام",
                 "الحجر الجيري", "فوسفات ثنائي الكالسيوم (DCP)", "بيكربونات الصوديوم (الصودا)"],
        "horse": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                  "أمباز الفول السوداني", "مولاس قصب السكر", "مركزات خيول ومجترات",
                  "ملح الطعام", "الحجر الجيري", "فوسفات ثنائي الكالسيوم (DCP)"],
        "camel": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)", "كسب فول صويا 44%",
                  "أمباز الفول السوداني", "البرسيم الجاف (الدريس)", "مركزات خيول ومجترات",
                  "ملح الطعام", "الحجر الجيري", "فوسفات ثنائي الكالسيوم (DCP)"],
        "poultry": ["ذرة صفراء", "سورجم (فتريتة)", "كسب فول صويا 44%", "كسب جلوتين الذرة 60%",
                    "مركزات دواجن وسمان", "بريمكس تسمين دواجن", "ملح الطعام",
                    "الحجر الجيري", "فوسفات ثنائي الكالسيوم (DCP)", "إنزيم الفايتيز (Phytase)"],
        "fish": ["ذرة صفراء", "كسب فول صويا 44%", "مسحوق أسماك 60%",
                 "كسب جلوتين الذرة 60%", "مركزات دواجن وسمان", "ملح الطعام",
                 "فوسفات ثنائي الكالسيوم (DCP)", "إنزيم الفايتيز (Phytase)"]
    }
    defaults = default_ings.get(animal_key, [])

    selected, prices = [], {}
    for cat, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat}", expanded=False):
            cols = st.columns(3)
            for idx, (name, _) in enumerate(items.items()):
                with cols[idx % 3]:
                    if st.checkbox(name, value=name in defaults, key=f"{animal_key}_f_{name}"):
                        p = st.number_input(f"سعر {name} ($/طن)", 5.0,
                                             float(250.0 if "نخالة" in name or "ملح" in name else 350.0),
                                             key=f"{animal_key}_p_{name}")
                        selected.append(name)
                        prices[name] = p

    if st.button(f"🚀 تشغيل المحرك ({display_name})", type="primary",
                 use_container_width=True, key=f"{animal_key}_run"):
        if len(selected) < 3:
            st.warning("اختر 3 مكونات على الأقل.")
            return

        # ═══ إضافة المكونات الإلزامية قبل بناء المصفوفات ═══
        if animal_key in ["cattle", "sheep", "goat", "camel"]:
            key_i = "بيكربونات الصوديوم (الصودا)"
            if key_i not in selected:
                selected.append(key_i)
                prices.setdefault(key_i, 340.0)
        if animal_key in ["poultry", "fish"]:
            key_i = "إنزيم الفايتيز (Phytase)"
            if key_i not in selected:
                selected.append(key_i)
                prices.setdefault(key_i, 1200.0)

        n = len(selected)
        c_vec = [prices[i] for i in selected]
        bounds = [(0.0, 100.0)] * n
        if animal_key in ["cattle", "sheep", "goat", "camel"]:
            idx = selected.index("بيكربونات الصوديوم (الصودا)")
            bounds[idx] = (0.5, 0.5)
        if animal_key in ["poultry", "fish"]:
            idx = selected.index("إنزيم الفايتيز (Phytase)")
            bounds[idx] = (0.05, 0.05)

        cp_row = [FLAT_FEED_DB.get(i, {}).get("CP", 0) * FLAT_FEED_DB.get(i, {}).get("DC", 0)
                  for i in selected]
        se_row = [FLAT_FEED_DB.get(i, {}).get("SE", 0) for i in selected]
        ndf_row = [FLAT_FEED_DB.get(i, {}).get("NDF", 0) for i in selected]
        adf_row = [FLAT_FEED_DB.get(i, {}).get("ADF", 0) for i in selected]

        A_eq = [[1.0] * n, cp_row]
        b_eq = [100.0, actual_dp * 100.0]
        A_ub = [[-x for x in se_row]]
        b_ub = [-target_se * 100.0]
        if animal_key in ["cattle", "sheep", "goat", "camel"]:
            A_ub.append(ndf_row); b_ub.append(35.0 * 100.0)
            A_ub.append(adf_row); b_ub.append(20.0 * 100.0)
        elif animal_key == "horse":
            A_ub.append(ndf_row); b_ub.append(40.0 * 100.0)

        try:
            res = linprog(c_vec, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=bounds, method='highs')
            if not res.success:
                st.error(f"❌ تعذر إيجاد حل: {res.message}")
                return

            formula_results = {}
            comp_se = 0.0
            for i, ing in enumerate(selected):
                if res.x[i] > 0.0001:
                    formula_results[ing] = res.x[i]
                    comp_se += (res.x[i] / 100.0) * FLAT_FEED_DB.get(ing, {}).get("SE", 0)
            ton_cost = res.fun / 100.0

            standard = STANDARD_VALUES.get(display_name, {}).get(stage, {})

            # ═══ التوصيات الذكية ═══
            recommendations = generate_smart_recommendations(
                animal_type=display_name, stage=stage, formula=formula_results,
                dp=actual_dp, se=comp_se, cost_per_ton=ton_cost,
                physiological_state=phys,
                target_dp_standard=standard.get('DP'),
                target_se_standard=standard.get('SE'))

            # عرض النتائج
            st.success(f"✅ تم توليد الخلطة! التكلفة: ${ton_cost:.2f}/طن")
            col_r1, col_r2 = st.columns([0.6, 0.4])
            with col_r1:
                st.write("#### 📝 المقادير للطن:")
                for k, v in formula_results.items():
                    st.markdown(f'<div class="formula-item"><span>{k}</span><span>{v:.2f}% ({v*10:.1f} كجم)</span></div>',
                                unsafe_allow_html=True)
                st.metric("💰 تكلفة الطن", f"${ton_cost:.2f}")
                st.metric("🧬 DP المحقق", f"{actual_dp:.2f}%")
                st.metric("🌽 SE المحقق", f"{comp_se:.2f}")
                if requester:
                    st.info(f"👤 طالب العلف: {requester}")

                st.markdown("### 📌 التوصيات الذكية:")
                for r in recommendations:
                    st.markdown(f"<div style='background:#e8f5e9; padding:8px 14px; border-radius:8px; border-right:4px solid #2e7d32; margin:5px 0; direction:rtl;'>{r}</div>",
                                unsafe_allow_html=True)

                if st.button("💾 حفظ الخلطة", use_container_width=True, key=f"{animal_key}_save"):
                    try:
                        get_db().insert_record('feed_formulas', {
                            'formula_id': secrets.token_hex(16),
                            'formula_name': f"{display_name} - {breed} - {stage}",
                            'animal_type': display_name, 'breed': breed, 'stage': stage,
                            'target_dp': actual_dp, 'target_se': comp_se,
                            'ingredients': json.dumps(formula_results, ensure_ascii=False),
                            'total_cost': ton_cost * 1000, 'cost_per_ton': ton_cost,
                            'created_by': st.session_state.get("user", {}).get("full_name", "مستخدم"),
                            'created_date': datetime.now().isoformat(),
                            'requester_name': requester
                        })
                        st.success("✅ تم الحفظ")
                    except Exception as e:
                        st.error(f"❌ {e}")

                try:
                    pdf_bytes = pdf_generator.generate_comprehensive_report(
                        formula_results, actual_dp, f"{breed} - {stage} ({phys})",
                        ton_cost, "المدينة", ton_cost * 600, "SDG", comp_se,
                        st.session_state.get("user", {}).get("full_name", "مستخدم"),
                        requester_name=requester, standard=standard,
                        recommendations=recommendations,
                        extra_info={"السلالة": breed, "المرحلة": stage,
                                    "الحالة": phys, "العمر": f"{age} شهر"})
                    st.download_button("📥 تحميل PDF", pdf_bytes,
                                        file_name=f"Tawornology_{display_name}_{datetime.now():%Y%m%d_%H%M}.pdf",
                                        mime="application/pdf", use_container_width=True,
                                        key=f"{animal_key}_pdf")
                except Exception as e:
                    st.warning(f"⚠️ {e}")

            with col_r2:
                if len(formula_results) > 1:
                    fig = px.pie(values=list(formula_results.values()),
                                 names=list(formula_results.keys()),
                                 title="توزيع المكونات",
                                 color_discrete_sequence=px.colors.sequential.Greens)
                    st.plotly_chart(fig, use_container_width=True, key=f"{animal_key}_pie")

            st.session_state["active_formula"] = formula_results
            st.session_state["active_cp_tag"] = actual_dp
            st.session_state["active_se_tag"] = comp_se
            st.session_state["computed_ton_cost"] = ton_cost
        except Exception as e:
            st.error(f"❌ خطأ: {e}")

# =====================================================================
# التبويبات
# =====================================================================
tabs_titles = [
    "🐾 القطاع الحيواني", "🧪 المختبر الذكي", "🔬 المختبر المتقدم",
    "🐔 إدارة المزارع", "🍼 بدائل الحليب", "🕌 مواقيت الصلاة",
    "💊 منبه الجرعات", "📊 بورصة الأسعار", "🏭 المستودعات",
    "📈 الإنتاج اليومي", "🔔 التنبيهات", "📈 التحليلات",
    "💬 تعليقات المختصين", "🖨️ مصمم الديباجة", "📚 المراجع العلمية",
    "🛡️ لوحة الإدارة"
]
if st.session_state["user_role"] == "owner":
    tabs_titles.append("📧 إرسال الكود")

tabs = st.tabs(tabs_titles)

# تبويب 0: القطاع الحيواني
with tabs[0]:
    guide_section("القطاع الحيواني", "تركيب أعلاف لجميع الحيوانات.")
    a_tabs = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐴 خيول", "🐫 إبل", "🐔 دواجن", "🐟 أسماك"])
    with a_tabs[0]:
        render_feed_formulation("cattle", "أبقار", "🐄",
                                 ["كنانة", "بطانة", "هولشتاين"],
                                 ["تسمين عجول", "حليب/إدرار", "حمل/دفع غذائي", "صيانة", "تسمين مكثف"],
                                 12.0, 65.0, "أبقار", True)
    with a_tabs[1]:
        render_feed_formulation("sheep", "أغنام", "🐏",
                                 ["الضأن الصحراوي", "البربري", "النعيمي"],
                                 ["تسمين حملان", "نعاج مرضعات", "نعاج حامل", "نعاج جافة"],
                                 11.5, 62.0, "أغنام", True)
    with a_tabs[2]:
        render_feed_formulation("goat", "ماعز", "🐐",
                                 ["النوبي", "الصحراوي", "بور"],
                                 ["تسمين جديان", "عنزات حلابة", "عنزات حامل", "صيانة"],
                                 11.0, 60.0, "ماعز", True)
    with a_tabs[3]:
        render_feed_formulation("horse", "خيول", "🐴",
                                 ["عربي أصيل", "ثوروبريد", "محلي"],
                                 ["راحة/صيانة", "عمل خفيف", "عمل متوسط", "عمل مكثف", "سباق",
                                  "أمهار نامية", "فرسات مرضعات"],
                                 11.0, 62.0, "خيول", True)
    with a_tabs[4]:
        render_feed_formulation("camel", "إبل", "🐫",
                                 ["عربية", "باختري", "هجين"],
                                 ["راحة/صيانة", "حمل/رضاعة", "إنتاج حليب", "تسمين", "عمل/نقل"],
                                 10.0, 58.0, "إبل", True)
    with a_tabs[5]:
        render_feed_formulation("poultry", "دواجن", "🐔",
                                 ["لاحم (Broiler)", "بياض (Layer)", "سمان"],
                                 ["بادي (0-14 يوم)", "نامي (15-28 يوم)", "ناهي (29-42 يوم)",
                                  "ناهي متقدم (43+ يوم)"],
                                 18.0, 72.0, "دواجن", False)
    with a_tabs[6]:
        render_feed_formulation("fish", "أسماك", "🐟",
                                 ["البلطي", "القرموط"],
                                 ["زريعة/بادئ", "نمو", "تسمين نهائي", "زريعة متقدمة"],
                                 28.0, 68.0, "أسماك", False)

# تبويب 1: المختبر الذكي
with tabs[1]:
    st.markdown('<div class="section-title">🧪 المختبر الذكي (OCR)</div>', unsafe_allow_html=True)
    if not OCR_AVAILABLE and not EASYOCR_AVAILABLE:
        st.warning("⚠️ ثبّت easyocr أو pytesseract")
    f = st.file_uploader("ارفع صورة:", type=['png', 'jpg', 'jpeg'], key="lab_upload")
    if f and st.session_state.get("smart_lab_system"):
        img = PILImage_module.open(f)
        st.image(img, use_container_width=True)
        if st.button("🔍 تحليل", type="primary"):
            with st.spinner("جاري التحليل..."):
                result, err = st.session_state["smart_lab_system"].analyze_image(img)
            if err:
                st.error(err)
            else:
                st.success("✅ تم")
                for k in ['cp', 'dc', 'se', 'ndf', 'adf', 'ee', 'ash', 'moisture']:
                    st.session_state[f"lab_{k}"] = result.get(k) or 0.0
                st.session_state["lab_sample_name"] = result.get('sample_name', '')
                st.rerun()

    st.markdown("#### إدخال البيانات")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("اسم العينة:", key="lab_sample_name")
        st.number_input("CP %:", 0.0, key="lab_cp", step=0.1)
        st.number_input("DC:", 0.0, 1.0, key="lab_dc", step=0.01)
        st.number_input("SE:", 0.0, key="lab_se", step=0.1)
    with c2:
        st.number_input("NDF %:", 0.0, key="lab_ndf", step=0.1)
        st.number_input("ADF %:", 0.0, key="lab_adf", step=0.1)
        st.number_input("EE %:", 0.0, key="lab_ee", step=0.1)
        st.number_input("ASH %:", 0.0, key="lab_ash", step=0.1)
        st.number_input("رطوبة:", 0.0, key="lab_moisture", step=0.1)

    if st.button("💾 حفظ في قاعدة البيانات"):
        if st.session_state.get("smart_lab_system"):
            rid = st.session_state["smart_lab_system"].save_lab_result({
                'sample_name': st.session_state.get('lab_sample_name', ''),
                'cp': st.session_state.get('lab_cp', 0.0),
                'dc': st.session_state.get('lab_dc', 0.0),
                'se': st.session_state.get('lab_se', 0.0),
                'ndf': st.session_state.get('lab_ndf', 0.0),
                'adf': st.session_state.get('lab_adf', 0.0),
                'ee': st.session_state.get('lab_ee', 0.0),
                'ash': st.session_state.get('lab_ash', 0.0),
                'moisture': st.session_state.get('lab_moisture', 0.0),
                'analyzed_by': st.session_state.get("user", {}).get("full_name", "مستخدم"),
            })
            st.success(f"✅ تم الحفظ (ID: {rid[:8]})")

    st.markdown("### 📋 النتائج السابقة")
    if st.session_state.get("smart_lab_system"):
        results = st.session_state["smart_lab_system"].get_lab_results(20)
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True)

# تبويب 2: المختبر المتقدم
with tabs[2]:
    st.markdown('<div class="section-title">🔬 المختبر المتقدم</div>', unsafe_allow_html=True)
    lab_animal = st.selectbox("الفصيل:", list(STANDARD_VALUES.keys()))
    lab_stage = st.selectbox("المرحلة:", list(STANDARD_VALUES[lab_animal].keys()))
    standard = STANDARD_VALUES[lab_animal][lab_stage]
    st.info(f"📊 المعايير: DP={standard['DP']}% | SE={standard['SE']} | CP={standard['CP']}%")

    lab_inputs = {}
    cols = st.columns(3)
    for i, ing in enumerate(FLAT_FEED_DB.keys()):
        with cols[i % 3]:
            lab_inputs[ing] = st.number_input(f"{ing} (كجم)", 0.0, key=f"labadv_{ing}", step=5.0)

    if st.button("🧪 تحليل", type="primary"):
        total = sum(lab_inputs.values())
        if total <= 0:
            st.warning("أدخل أوزاناً.")
        else:
            cp_t = dp_t = se_t = 0.0
            comps = []
            for ing, w in lab_inputs.items():
                if w > 0:
                    pct = w / total
                    fd = FLAT_FEED_DB.get(ing, {})
                    cp_t += pct * fd.get("CP", 0)
                    dp_t += pct * fd.get("CP", 0) * fd.get("DC", 0)
                    se_t += pct * fd.get("SE", 0)
                    comps.append({"المادة": ing, "الوزن (كجم)": w, "النسبة %": f"{pct*100:.2f}"})
            st.dataframe(pd.DataFrame(comps), use_container_width=True)
            st.table(pd.DataFrame([
                {"العنصر": "CP", "القيمة": f"{cp_t:.2f}%"},
                {"العنصر": "DP", "القيمة": f"{dp_t:.2f}%"},
                {"العنصر": "SE", "القيمة": f"{se_t:.2f}"}]))

            recs = generate_smart_recommendations(
                lab_animal, lab_stage, lab_inputs, dp_t, se_t, 300.0,
                target_dp_standard=standard.get('DP'),
                target_se_standard=standard.get('SE'))
            st.markdown("### 📌 التوصيات:")
            for r in recs:
                st.markdown(f"<div style='background:#e8f5e9; padding:8px; border-radius:8px; margin:5px 0; direction:rtl;'>{r}</div>",
                            unsafe_allow_html=True)

            try:
                pdf_bytes = pdf_generator.generate_lab_report(
                    {'cp': cp_t, 'dp': dp_t, 'se': se_t, 'components': lab_inputs},
                    lab_animal, lab_stage,
                    st.session_state.get("user", {}).get("full_name", "مستخدم"),
                    standard, None, recs)
                st.download_button("📥 تحميل PDF", pdf_bytes,
                                    file_name=f"Lab_{datetime.now():%Y%m%d_%H%M}.pdf",
                                    mime="application/pdf")
            except Exception as e:
                st.warning(f"⚠️ {e}")

# تبويبات 3-15 (اختصار)
with tabs[3]:  # إدارة المزارع
    st.markdown('<div class="section-title">🐔 إدارة المزارع</div>', unsafe_allow_html=True)
    if st.session_state["user_role"] in ["owner", "specialist", "breeder"]:
        with st.expander("➕ دورة جديدة"):
            fname = st.text_input("اسم المزرعة")
            cnt = st.number_input("عدد الكتاكيت", 1, value=1000)
            br = st.selectbox("السلالة", ["Ross 308", "Cobb 500", "محلية"])
            if st.button("إنشاء"):
                cid = secrets.token_hex(8)
                st.session_state["broiler_farms"][cid] = {
                    "farm_name": fname, "initial_birds": cnt, "breed": br,
                    "start_date": datetime.now().isoformat(), "age_days": 0,
                    "current_weight": 0.045, "total_feed": 0, "dead_count": 0}
                st.success("✅"); st.rerun()
    for cid, farm in st.session_state.get("broiler_farms", {}).items():
        with st.expander(f"🏠 {farm['farm_name']}"):
            st.metric("العدد", farm['initial_birds'])
            st.metric("العمر", farm['age_days'])

with tabs[4]:  # بدائل الحليب
    st.markdown('<div class="section-title">🍼 بدائل الحليب</div>', unsafe_allow_html=True)
    at = st.selectbox("نوع الحيوان:", ["عجل بقري", "حملان", "جديان", "مهرات", "أطفال إبل"])
    ad = st.slider("العمر (يوم)", 1, 120, 30)
    if st.button("🍼 تشغيل"):
        st.info(f"سيتم تركيب بديل لـ {at} بعمر {ad} يوم")

with tabs[5]:  # الصلاة
    st.markdown('<div class="section-title">🕌 مواقيت الصلاة</div>', unsafe_allow_html=True)
    city = st.selectbox("المدينة:", ["مكة", "المدينة", "الخرطوم", "طرابلس", "القاهرة", "دبي"])
    cols = st.columns(3)
    for i, (n, t) in enumerate({"الفجر": "05:00", "الشروق": "06:30", "الظهر": "12:00",
                                 "العصر": "15:30", "المغرب": "18:00", "العشاء": "19:30"}.items()):
        with cols[i % 3]:
            st.metric(n, t)

with tabs[6]:  # منبه الجرعات
    st.markdown('<div class="section-title">💊 منبه الجرعات</div>', unsafe_allow_html=True)
    st.info("نظام تذكير اللقاحات والفيتامينات")
    at = st.selectbox("نوع الحيوان", ["أبقار", "أغنام", "ماعز", "خيول", "إبل", "دواجن"])
    dn = st.text_input("اسم الجرعة")
    da = st.number_input("الجرعة", 0.0, value=1.0)
    if st.button("حفظ"):
        st.success("✅ تم")

with tabs[7]:  # بورصة الأسعار
    st.markdown('<div class="section-title">📊 بورصة الأسعار</div>', unsafe_allow_html=True)
    for n, p in list(st.session_state["global_livestock_prices"].items()):
        st.number_input(n, value=float(p), key=f"lp_{n}")

with tabs[8]:  # المستودعات
    st.markdown('<div class="section-title">🏭 المستودعات</div>', unsafe_allow_html=True)
    inv = [{"المادة": k, "الكمية": (v["quantity"] if isinstance(v, dict) else v),
            "الحد الأدنى": (v.get("min_threshold", 5) if isinstance(v, dict) else 5)}
           for k, v in st.session_state["inventory"].items()]
    st.dataframe(pd.DataFrame(inv), use_container_width=True)

with tabs[9]:  # الإنتاج اليومي
    st.markdown('<div class="section-title">📈 الإنتاج اليومي</div>', unsafe_allow_html=True)
    st.info("سجل يومي للإنتاج")

with tabs[10]:  # التنبيهات
    st.markdown('<div class="section-title">🔔 التنبيهات</div>', unsafe_allow_html=True)
    warns = InventoryManager.check_stock_levels()
    if warns:
        for i, info in warns.items():
            st.warning(f"{i}: {info['status']}")
    else:
        st.success("✅ لا تنبيهات")

with tabs[11]:  # التحليلات
    st.markdown('<div class="section-title">📈 التحليلات</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl in [(c1, "1,247", "الخلطات"), (c2, "$285", "متوسط التكلفة"),
                          (c3, "18%", "التوفير"), (c4, "96%", "الرضا")]:
        col.markdown(f'<div class="metric-card"><div class="number">{val}</div><div class="label">{lbl}</div></div>',
                     unsafe_allow_html=True)
    st.markdown("#### 🔮 التنبؤ بالأسعار")
    pred = PricePredictor()
    for ing in ["ذرة صفراء", "كسب فول صويا 44%"]:
        p = pred.predict_price(ing, 7)
        if p.get('prediction'):
            st.metric(ing, f"${p['prediction']:.2f}")

with tabs[12]:  # التعليقات
    st.markdown('<div class="section-title">💬 تعليقات المختصين</div>', unsafe_allow_html=True)
    db = get_db()
    comments = db.execute_query(
        "SELECT author, role, comment, created_at FROM shared_comments ORDER BY created_at DESC LIMIT 100")
    for c in comments:
        st.markdown(f"<div style='background:#f8f9fa; padding:10px; border-radius:8px; margin:5px 0; border-right:4px solid #2e7d32; direction:rtl;'><b>{c['author']}</b> ({c['role']}) — <small>{c['created_at'][:16]}</small><br>{c['comment']}</div>",
                    unsafe_allow_html=True)
    nc = st.text_area("إضافة تعليق:", key="nc_input")
    if st.button("نشر"):
        if nc.strip():
            db.insert_record('shared_comments', {
                'comment_id': secrets.token_hex(16),
                'author': st.session_state.get("user", {}).get("full_name", "مستخدم"),
                'role': st.session_state.get("user_role", "public"),
                'comment': nc.strip(),
                'created_at': datetime.now().isoformat()})
            st.success("✅"); st.rerun()

with tabs[13]:  # الديباجة
    st.markdown('<div class="section-title">🖨️ مصمم الديباجة</div>', unsafe_allow_html=True)
    bn = st.text_input("اسم البراند:", BRAND)
    st.markdown(f"""
    <div style='border:3px dashed #1b5e20; padding:30px; border-radius:15px; text-align:center; direction:rtl;'>
        <h2>{bn}</h2>
        <h3 style='color:#c62828;'>{SUPERVISOR_NAME}</h3>
        <p>DP: {st.session_state.get('active_cp_tag', 12):.1f}% | SE: {st.session_state.get('active_se_tag', 65):.1f}</p>
    </div>""", unsafe_allow_html=True)

with tabs[14]:  # المراجع
    st.markdown('<div class="section-title">📚 المراجع العلمية</div>', unsafe_allow_html=True)
    for cat in ScientificReferenceSystem.REFERENCES.values():
        with st.expander(f"{cat['icon']} {cat['title']}"):
            for ref in cat['references']:
                st.markdown(f"**{ref['title']}** — {ref['authors']} ({ref['year']})")

with tabs[15]:  # لوحة الإدارة
    if st.session_state["user_role"] != "owner":
        st.warning("🔒 للمالك فقط")
    else:
        st.markdown('<div class="section-title">🛡️ لوحة الإدارة</div>', unsafe_allow_html=True)
        db = get_db()
        stats = {
            "المستخدمون": len(db.execute_query("SELECT 1 FROM users")),
            "المزارع": len(db.execute_query("SELECT 1 FROM farms")),
            "الخلطات": len(db.execute_query("SELECT 1 FROM feed_formulas")),
            "التحاليل": len(db.execute_query("SELECT 1 FROM lab_results")),
        }
        c1, c2, c3, c4 = st.columns(4)
        for col, (k, v) in zip([c1, c2, c3, c4], stats.items()):
            col.markdown(f'<div class="metric-card"><div class="number">{v}</div><div class="label">{k}</div></div>',
                         unsafe_allow_html=True)

        formulas = db.execute_query(
            "SELECT formula_name, animal_type, target_dp, cost_per_ton, created_date "
            "FROM feed_formulas ORDER BY created_date DESC LIMIT 50")
        if formulas:
            df = pd.DataFrame(formulas)
            st.dataframe(df, use_container_width=True)
            excel = export_to_excel(formulas, "Formulas")
            if excel:
                st.download_button("📥 تصدير Excel", excel,
                                    file_name=f"formulas_{datetime.now():%Y%m%d}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# تبويب إرسال الكود
if st.session_state["user_role"] == "owner" and len(tabs) > 16:
    with tabs[16]:
        st.markdown('<div class="section-title">📧 إرسال السورس كود</div>', unsafe_allow_html=True)
        email = st.text_input("البريد المستلم:", value=OWNER_EMAIL, key="em_r")
        smtp_pwd = st.text_input("App Password:", type="password", key="smtp_pwd")
        if st.button("📤 إرسال", type="primary", use_container_width=True):
            if '@' in email:
                with st.spinner("..."):
                    ok, msg = send_code_to_email(email, smtp_pwd)
                (st.success if ok else st.error)(msg)

# تذييل
st.markdown(f"""
<div style='text-align:center; padding:20px; margin-top:30px; border-top:2px solid #e0e0e0; color:#888;'>
🌾 <b>{BRAND}</b> v18.0<br>© 2026 | {SUPERVISOR_NAME}<br>
🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b>
</div>""", unsafe_allow_html=True)

if st.button("🔊 اختبار الصوت"):
    voice_guide("بسم الله الرحمن الرحيم، اختبار النظام الصوتي.")
