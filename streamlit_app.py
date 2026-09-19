# ============================================================================
# منصة تاور نولجي Tawornology العلمية - الإصدار 19.3 النهائي
# محرك التركيب التلقائي الشامل: طاقة + بروتين + أملاح + ألياف
# ============================================================================
# 🕊️ إهداء إلى روح والدي إسماعيل تاور وأختي ابتسام - رحمهما الله
# المشرف: الاختصاصي م. عبد القادر إسماعيل تاور - اختصاصي تغذية الحيوان
# ============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import json, os, base64, smtplib, time, urllib.parse
import hashlib, hmac, secrets, io, sqlite3, warnings, re, random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scipy.optimize import linprog
from sklearn.linear_model import LinearRegression
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from functools import lru_cache

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

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (Table, TableStyle, Paragraph, Spacer, Image,
                                 SimpleDocTemplate, PageBreak)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image as PILImage_module
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

warnings.filterwarnings('ignore')

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

st.set_page_config(
    page_title="تاور نولجي Tawornology v19.3",
    page_icon="🌾", layout="wide", initial_sidebar_state="collapsed"
)

# =====================================================================
# معالج النص العربي
# =====================================================================
def ar(text) -> str:
    if text is None:
        return ""
    s = str(text)
    if not s.strip():
        return s
    try:
        return get_display(arabic_reshaper.reshape(s))
    except Exception:
        return s


@st.cache_resource
def _setup_matplotlib_arabic() -> str:
    candidates = [
        "Amiri-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/arabic/Amiri-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf"]
    chosen = "DejaVu Sans"
    for p in candidates:
        if os.path.exists(p):
            try:
                fm.fontManager.addfont(p)
                chosen = fm.FontProperties(fname=p).get_name()
                break
            except Exception:
                continue
    plt.rcParams['font.family'] = chosen
    plt.rcParams['axes.unicode_minus'] = False
    return chosen


_MAT_FONT = _setup_matplotlib_arabic()


def get_current_user_name() -> str:
    user = st.session_state.get("user") or {}
    return user.get("full_name", "مستخدم غير معروف")


def get_current_user_role() -> str:
    return st.session_state.get("user_role", "public")


def get_or_create_device_id() -> str:
    if "device_id" not in st.session_state:
        st.session_state["device_id"] = secrets.token_hex(16)
    return st.session_state["device_id"]


CODES_DB = {
    "202687": {"role": "owner",
               "name": "الاختصاصي م. عبد القادر إسماعيل تاور",
               "level": 3},
    "2020": {"role": "specialist", "name": "المختص والزملاء", "level": 2},
    "2024": {"role": "veterinarian", "name": "الطبيب البيطري", "level": 2},
    "2025": {"role": "nutritionist", "name": "أخصائي التغذية", "level": 2},
    "2026": {"role": "breeder", "name": "المربي", "level": 1}
}


def validate_access_code(input_code):
    if not input_code:
        return None
    clean = input_code.strip()
    if len(clean) < 4:
        return None
    for stored, data in CODES_DB.items():
        try:
            if hmac.compare_digest(clean, stored):
                return data
        except Exception:
            continue
    return None


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "abukram128@gmail.com"
OWNER_EMAIL = "abukram128@gmail.com"
WHATSAPP_NUMBER = "+249123533489"

if "email_password" not in st.session_state:
    try:
        st.session_state["email_password"] = st.secrets["email"]["password"]
    except Exception:
        st.session_state["email_password"] = None

PHOTO_OPTIONS_TUPLE = ("14686.jpg", "1000069464.jpg",
                       "14686.JPG", "1000069464.JPG")


@st.cache_data(ttl=3600)
def get_image_base64(paths_tuple):
    for path in paths_tuple:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                pass
    return None


img_base64 = get_image_base64(PHOTO_OPTIONS_TUPLE)


@st.cache_data(ttl=3600)
def tts_base64(text, lang="ar"):
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


def play_audio_b64(b64):
    if b64:
        st.components.v1.html(
            f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" '
            f'type="audio/mpeg"></audio>', height=0)


def voice_guide(msg, lang="ar"):
    if not GTTS_AVAILABLE or not msg:
        return
    b = tts_base64(msg, lang)
    if b:
        play_audio_b64(b)


def voice_welcome(role):
    msgs = {
        "owner": "مرحباً بك، أيها الاختصاصي.",
        "specialist": "مرحباً أيها المختص.",
        "veterinarian": "مرحباً أيها الطبيب.",
        "nutritionist": "مرحباً أيها الأخصائي.",
        "breeder": "مرحباً أيها المربي.",
        "public": "مرحباً بك زائراً."}
    voice_guide(msgs.get(role, "مرحباً بك."))


def play_welcome_audio():
    voice_guide("السلام عليكم ورحمة الله، مرحباً بكم في تاور نولجي.")


def play_dua_audio():
    voice_guide("اللهم اغفر لإسماعيل تاور وابتسام.")


def send_code_to_email(receiver_email):
    if receiver_email.strip().lower() != OWNER_EMAIL.strip().lower():
        return False, "❌ الإرسال مسموح فقط للبريد: " + OWNER_EMAIL
    if not st.session_state.get("email_password"):
        return False, "⚠️ أعد كلمة مرور البريد."
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception:
        code = "# تعذر القراءة"
    h = hashlib.md5(code.encode()).hexdigest()
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = "🌾 تاور نولجي v19.3"
    msg.attach(MIMEText(f"السلام عليكم\nالتوقيع: {h}", 'plain', 'utf-8'))
    att = MIMEText(code, 'plain', 'utf-8')
    att.add_header('Content-Disposition', 'attachment',
                    filename="tawornology_v19_3.py")
    msg.attach(att)
    try:
        s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        s.starttls()
        s.login(SENDER_EMAIL, st.session_state["email_password"])
        s.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        s.quit()
        return True, "✅ تم الإرسال"
    except Exception as e:
        return False, f"❌ {e}"


# =====================================================================
# قاعدة البيانات
# =====================================================================
class UserIsolatedDB:
    _DIR = "tawor_user_data"

    @staticmethod
    def _ensure():
        os.makedirs(UserIsolatedDB._DIR, exist_ok=True)

    @staticmethod
    def get_path() -> str:
        UserIsolatedDB._ensure()
        user = st.session_state.get("user") or {}
        uid = (user.get("user_id") or
               st.session_state.get("device_id") or "guest")
        safe = re.sub(r'[^a-zA-Z0-9_\-]', '', str(uid))[:40] or "guest"
        return os.path.join(UserIsolatedDB._DIR, f"tawor_{safe}.db")


class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = UserIsolatedDB.get_path()
        self.db_path = db_path
        self._init()

    def _init(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT,
            role TEXT, full_name TEXT, email TEXT, phone TEXT, specialty TEXT,
            experience_years INTEGER, created_date TEXT, last_login TEXT,
            is_active INTEGER DEFAULT 1, is_public INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS feed_formulas (
            formula_id TEXT PRIMARY KEY, formula_name TEXT, animal_type TEXT,
            breed TEXT, stage TEXT, target_dp REAL, target_se REAL,
            ingredients TEXT, total_cost REAL, cost_per_ton REAL,
            created_by TEXT, created_date TEXT, is_approved INTEGER DEFAULT 0,
            usage_count INTEGER DEFAULT 0, requester_name TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS lab_results (
            result_id TEXT PRIMARY KEY, sample_name TEXT, cp REAL, dc REAL,
            se REAL, ndf REAL, adf REAL, ee REAL, ash REAL, moisture REAL,
            analysis_date TEXT, analyzed_by TEXT, notes TEXT,
            requester_name TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS price_history (
            record_id TEXT PRIMARY KEY, ingredient_name TEXT, price REAL,
            currency TEXT, country TEXT, city TEXT, record_date TEXT,
            recorded_by TEXT)''')
        conn.commit()
        conn.close()

    def execute_query(self, q, params=()):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        r = c.execute(q, params)
        conn.commit()
        d = r.fetchall()
        conn.close()
        return d

    def insert_record(self, table, data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        cols = ', '.join(data.keys())
        ph = ', '.join(['?' for _ in data])
        c.execute(f"INSERT INTO {table} ({cols}) VALUES ({ph})",
                  list(data.values()))
        conn.commit()
        conn.close()
        return True

    def update_record(self, table, data, condition):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        s = ', '.join([f"{k}=?" for k in data])
        w = ' AND '.join([f"{k}=?" for k in condition])
        c.execute(f"UPDATE {table} SET {s} WHERE {w}",
                  list(data.values()) + list(condition.values()))
        conn.commit()
        conn.close()


@st.cache_resource
def get_db_manager():
    return DatabaseManager()


def seed_price_history():
    try:
        db = get_db_manager()
        cnt = db.execute_query("SELECT COUNT(*) FROM price_history")[0][0]
        if cnt > 0:
            return
        bases = {"ذرة صفراء": 230.0, "كسب فول صويا 44%": 440.0,
                  "نخالة قمح (ردة)": 150.0, "شعير مطحون": 210.0,
                  "كسب عباد الشمس 36%": 310.0,
                  "أمباز الفول السوداني (كسب)": 460.0,
                  "مسحوق أسماك (Fishmeal 60%)": 850.0,
                  "الحجر الجيري (بودرة بلاط)": 40.0,
                  "فوسفات ثنائي الكالسيوم (DCP)": 280.0,
                  "ملح الطعام": 30.0}
        rng = random.Random(42)
        for ing, b in bases.items():
            for d in range(30, 0, -1):
                dt = (datetime.now() - timedelta(days=d)).isoformat()
                n = rng.uniform(-0.05, 0.05)
                tr = (30 - d) * 0.003
                p = b * (1 + n + tr)
                db.insert_record('price_history', {
                    'record_id': secrets.token_hex(16),
                    'ingredient_name': ing, 'price': round(p, 2),
                    'currency': 'USD', 'country': 'السودان',
                    'city': 'الخرطوم', 'record_date': dt,
                    'recorded_by': 'system'})
    except Exception:
        pass


class AuthManager:
    def __init__(self):
        self.db = get_db_manager()
        self._defaults()
        self._public()

    def _defaults(self):
        ds = [('admin', 'admin123', 'owner',
               'الاختصاصي م. عبد القادر إسماعيل تاور',
               'admin@tawornology.com', '+249123456789', 'تغذية', 10),
              ('specialist', 'spec123', 'specialist', 'المختص',
               'spec@tawornology.com', '+249123456788', 'تغذية', 8),
              ('nutritionist', 'nutri123', 'nutritionist', 'الأخصائي',
               'nutri@tawornology.com', '+249123456786', 'تغذية', 7),
              ('veterinarian', 'vet123', 'veterinarian', 'الطبيب',
               'vet@tawornology.com', '+249123456785', 'بيطري', 9)]
        for u, p, r, fn, e, ph, sp, ex in ds:
            if not self.db.execute_query(
                    "SELECT * FROM users WHERE username=?", (u,)):
                self.create(u, p, r, fn, e, ph, sp, ex)

    def _public(self):
        if not self.db.execute_query(
                "SELECT * FROM users WHERE username='public'"):
            self.create('public', 'public123', 'public', 'زائر',
                        'public@tawornology.com', '+249123456780', 'عام', 0)

    def create(self, u, p, r, fn, e, ph, sp="", ex=0):
        uid = secrets.token_hex(16)
        h = hashlib.sha256(p.encode()).hexdigest()
        self.db.insert_record('users', {
            'user_id': uid, 'username': u, 'password_hash': h,
            'role': r, 'full_name': fn, 'email': e, 'phone': ph,
            'specialty': sp, 'experience_years': ex,
            'created_date': datetime.now().isoformat(), 'last_login': '',
            'is_active': 1, 'is_public': 1 if r == 'public' else 0})
        return uid

    def authenticate(self, u, p):
        rows = self.db.execute_query(
            "SELECT * FROM users WHERE username=? AND is_active=1", (u,))
        if not rows:
            return None
        user = rows[0]
        if user[2] != hashlib.sha256(p.encode()).hexdigest():
            return None
        self.db.update_record('users',
            {'last_login': datetime.now().isoformat()}, {'user_id': user[0]})
        return {'user_id': user[0], 'username': user[1], 'role': user[3],
                'full_name': user[4], 'email': user[5], 'phone': user[6]}

    def login_public(self):
        rows = self.db.execute_query(
            "SELECT * FROM users WHERE username='public' AND is_active=1")
        if rows:
            u = rows[0]
            return {'user_id': u[0], 'username': u[1], 'role': 'public',
                    'full_name': 'زائر', 'email': u[5], 'phone': u[6]}
        self._public()
        return self.login_public()


# =====================================================================
# مكتبة الأعلاف
# =====================================================================
BIG_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0},
        "سورجم (فتريتة)": {"CP": 10.0, "DC": 0.78, "SE": 70.0},
        "قمح محلي مصنّع": {"CP": 12.0, "DC": 0.85, "SE": 75.0},
        "جريش أرز رزاز": {"CP": 7.8, "DC": 0.82, "SE": 82.0},
        "دخن محلي غزير": {"CP": 11.0, "DC": 0.75, "SE": 68.0},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0}},
    "🌱 الأكساب ومصادر البروتين": {
        "أمباز الفول السوداني (كسب)": {"CP": 46.0, "DC": 0.88, "SE": 73.0},
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0},
        "كسب فول صويا 48%": {"CP": 48.0, "DC": 0.91, "SE": 76.0},
        "كسب عباد الشمس 36%": {"CP": 36.0, "DC": 0.76, "SE": 42.0},
        "كسب بذور القطن (مقشور)": {"CP": 41.0, "DC": 0.78, "SE": 55.0},
        "كسب بذور الكتان": {"CP": 32.0, "DC": 0.82, "SE": 65.0},
        "كسب السمسم المحسن": {"CP": 42.0, "DC": 0.84, "SE": 70.0},
        "كسب جلوتين الذرة 60%": {"CP": 60.0, "DC": 0.92, "SE": 85.0},
        "كسب نواة النخيل": {"CP": 16.0, "DC": 0.65, "SE": 52.0},
        "كسب بذور اللفت (كانولا)": {"CP": 38.0, "DC": 0.82, "SE": 62.0}},
    "🚜 المخلفات الزراعية": {
        "نخالة قمح (ردة)": {"CP": 15.0, "DC": 0.72, "SE": 45.0},
        "البرسيم الجاف (الدريس)": {"CP": 16.5, "DC": 0.60, "SE": 35.0},
        "مولاس قصب السكر": {"CP": 4.0, "DC": 0.95, "SE": 50.0},
        "تبن قمح ناعم": {"CP": 3.2, "DC": 0.35, "SE": 18.0},
        "قشر فول سوداني مطحون": {"CP": 5.0, "DC": 0.30, "SE": 15.0},
        "سرسة الأرز المطحونة": {"CP": 2.5, "DC": 0.25, "SE": 12.0},
        "مخلفات مصانع البسكويت": {"CP": 10.0, "DC": 0.80, "SE": 65.0},
        "قش الأرز المعالج": {"CP": 4.0, "DC": 0.40, "SE": 25.0}},
    "🧬 البروتين الحيواني": {
        "مسحوق أسماك (Fishmeal 60%)": {"CP": 60.0, "DC": 0.85, "SE": 65.0},
        "مسحوق اللحم والعظم": {"CP": 50.0, "DC": 0.75, "SE": 50.0},
        "مركزات دواجن وسمان": {"CP": 40.0, "DC": 0.85, "SE": 60.0},
        "مركزات خيول ومجترات": {"CP": 36.0, "DC": 0.80, "SE": 55.0},
        "بروتين مصل الحليب (WPC)": {"CP": 80.0, "DC": 0.95, "SE": 40.0}},
    "🧪 الأحماض الأمينية": {
        "ليسين نقي (L-Lysine)": {"CP": 94.0, "DC": 1.00, "SE": 0.0},
        "ميثيونين نقي (DL-Methionine)": {"CP": 58.0, "DC": 1.00, "SE": 0.0},
        "ثريونين نقي (L-Threonine)": {"CP": 72.0, "DC": 1.00, "SE": 0.0}},
    "🔬 الإنزيمات والبريمكسات": {
        "بريمكس تسمين دواجن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "بريمكس بياض وبشاير": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "بريمكس أبقار حلابة ومجترات": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "إنزيم الفايتيز الزامي (Phytase Super-D)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "كبريتات الحديدوز (معادل الجوسيبول)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "خميرة الخبز (Yeast)": {"CP": 45.0, "DC": 0.85, "SE": 35.0}},
    "🪨 الأملاح والمعادن": {
        "الحجر الجيري (بودرة بلاط)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "فوسفات ثنائي الكالسيوم (DCP)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "مضاد سموم فطرية": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "بيكربونات الصوديوم (الصودا)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "أكسيد المغنيسيوم العلفي": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "يوريا علفية محصنة (المجترات فقط)": {"CP": 287.0, "DC": 0.95, "SE": 0.0},
        "كلوريد الكولين (Choline Chloride)": {"CP": 0.0, "DC": 0.0, "SE": 0.0}},
    "🍼 مكونات بدائل الحليب": {
        "مصل الحليب المجفف (Whey)": {"CP": 12.0, "DC": 0.95, "SE": 35.0},
        "حليب مجفف خالي الدسم": {"CP": 34.0, "DC": 0.95, "SE": 40.0},
        "دهن نباتي (زيت نباتي)": {"CP": 0.0, "DC": 0.0, "SE": 10.0},
        "ليسيثين الصويا": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "فيتامينات ومعادن (Premix)": {"CP": 0.0, "DC": 0.0, "SE": 0.0},
        "بروتين الصويا المركز": {"CP": 65.0, "DC": 0.90, "SE": 30.0}}
}

FLAT_FEED_DB = {}
for cat, items in BIG_FEEDS_LIBRARY.items():
    for name, nut in items.items():
        FLAT_FEED_DB[name] = nut


# =====================================================================
# قاعدة بيانات المعادن والألياف
# =====================================================================
_DEFAULT_MF = {"Ca":0.0,"P":0.0,"Na":0.0,"K":0.0,"Mg":0.0,"Cl":0.0,"S":0.0,
               "NDF":0.0,"ADF":0.0,"CF":0.0,"Ash":0.0}

MINERALS_FIBER_DB = {
    "ذرة صفراء": {"Ca":0.03,"P":0.28,"Na":0.02,"K":0.35,"Mg":0.11,"Cl":0.05,"S":0.12,"NDF":9.5,"ADF":3.2,"CF":2.2,"Ash":1.3},
    "ذرة بيضاء": {"Ca":0.03,"P":0.27,"Na":0.02,"K":0.33,"Mg":0.10,"Cl":0.05,"S":0.11,"NDF":10.2,"ADF":3.5,"CF":2.4,"Ash":1.4},
    "شعير مطحون": {"Ca":0.06,"P":0.35,"Na":0.03,"K":0.55,"Mg":0.13,"Cl":0.15,"S":0.15,"NDF":18.5,"ADF":7.5,"CF":5.5,"Ash":2.5},
    "سورجم (فتريتة)": {"Ca":0.04,"P":0.32,"Na":0.02,"K":0.40,"Mg":0.12,"Cl":0.06,"S":0.11,"NDF":12.5,"ADF":5.5,"CF":3.0,"Ash":1.8},
    "قمح محلي مصنّع": {"Ca":0.05,"P":0.36,"Na":0.02,"K":0.45,"Mg":0.13,"Cl":0.06,"S":0.14,"NDF":11.5,"ADF":3.8,"CF":2.8,"Ash":1.6},
    "جريش أرز رزاز": {"Ca":0.05,"P":1.10,"Na":0.05,"K":1.20,"Mg":0.55,"Cl":0.05,"S":0.20,"NDF":5.5,"ADF":2.5,"CF":2.0,"Ash":4.2},
    "دخن محلي غزير": {"Ca":0.05,"P":0.30,"Na":0.03,"K":0.42,"Mg":0.13,"Cl":0.05,"S":0.12,"NDF":15.5,"ADF":6.5,"CF":5.0,"Ash":2.2},
    "شوفان علفي": {"Ca":0.10,"P":0.35,"Na":0.04,"K":0.50,"Mg":0.15,"Cl":0.10,"S":0.18,"NDF":27.5,"ADF":13.5,"CF":10.5,"Ash":3.0},
    "أمباز الفول السوداني (كسب)": {"Ca":0.20,"P":0.60,"Na":0.05,"K":1.30,"Mg":0.25,"Cl":0.05,"S":0.28,"NDF":15.5,"ADF":8.5,"CF":7.0,"Ash":5.5},
    "كسب فول صويا 44%": {"Ca":0.35,"P":0.65,"Na":0.03,"K":2.05,"Mg":0.28,"Cl":0.05,"S":0.42,"NDF":13.5,"ADF":8.0,"CF":6.5,"Ash":6.0},
    "كسب فول صويا 48%": {"Ca":0.38,"P":0.70,"Na":0.03,"K":2.20,"Mg":0.30,"Cl":0.05,"S":0.45,"NDF":12.0,"ADF":7.0,"CF":5.5,"Ash":6.2},
    "كسب عباد الشمس 36%": {"Ca":0.35,"P":1.00,"Na":0.03,"K":1.20,"Mg":0.60,"Cl":0.05,"S":0.30,"NDF":38.5,"ADF":25.5,"CF":20.0,"Ash":6.5},
    "كسب بذور القطن (مقشور)": {"Ca":0.20,"P":0.85,"Na":0.03,"K":1.35,"Mg":0.40,"Cl":0.05,"S":0.25,"NDF":24.5,"ADF":15.5,"CF":12.5,"Ash":6.5},
    "كسب بذور الكتان": {"Ca":0.25,"P":0.80,"Na":0.05,"K":1.30,"Mg":0.55,"Cl":0.05,"S":0.28,"NDF":18.5,"ADF":10.5,"CF":8.5,"Ash":5.8},
    "كسب السمسم المحسن": {"Ca":2.00,"P":1.20,"Na":0.05,"K":1.10,"Mg":0.35,"Cl":0.05,"S":0.30,"NDF":14.5,"ADF":9.5,"CF":7.5,"Ash":12.5},
    "كسب جلوتين الذرة 60%": {"Ca":0.05,"P":0.45,"Na":0.03,"K":0.40,"Mg":0.15,"Cl":0.05,"S":0.60,"NDF":8.5,"ADF":5.5,"CF":4.0,"Ash":3.5},
    "كسب نواة النخيل": {"Ca":0.30,"P":0.55,"Na":0.03,"K":0.85,"Mg":0.30,"Cl":0.05,"S":0.15,"NDF":55.5,"ADF":35.5,"CF":28.0,"Ash":4.5},
    "كسب بذور اللفت (كانولا)": {"Ca":0.65,"P":1.00,"Na":0.05,"K":1.30,"Mg":0.55,"Cl":0.05,"S":0.85,"NDF":28.0,"ADF":18.0,"CF":14.0,"Ash":7.5},
    "نخالة قمح (ردة)": {"Ca":0.13,"P":1.15,"Na":0.05,"K":1.20,"Mg":0.50,"Cl":0.06,"S":0.20,"NDF":35.5,"ADF":12.5,"CF":9.5,"Ash":5.5},
    "البرسيم الجاف (الدريس)": {"Ca":1.30,"P":0.25,"Na":0.10,"K":2.20,"Mg":0.35,"Cl":0.30,"S":0.28,"NDF":42.5,"ADF":32.5,"CF":25.0,"Ash":10.5},
    "مولاس قصب السكر": {"Ca":0.80,"P":0.08,"Na":0.10,"K":3.50,"Mg":0.30,"Cl":1.50,"S":0.35,"NDF":1.5,"ADF":0.8,"CF":0.5,"Ash":8.5},
    "تبن قمح ناعم": {"Ca":0.30,"P":0.08,"Na":0.05,"K":1.20,"Mg":0.10,"Cl":0.20,"S":0.12,"NDF":72.5,"ADF":45.5,"CF":38.0,"Ash":8.5},
    "قشر فول سوداني مطحون": {"Ca":0.20,"P":0.06,"Na":0.05,"K":0.80,"Mg":0.10,"Cl":0.05,"S":0.08,"NDF":65.5,"ADF":42.5,"CF":35.0,"Ash":5.5},
    "سرسة الأرز المطحونة": {"Ca":0.10,"P":0.10,"Na":0.05,"K":0.30,"Mg":0.05,"Cl":0.05,"S":0.05,"NDF":68.5,"ADF":48.5,"CF":40.0,"Ash":15.5},
    "مخلفات مصانع البسكويت": {"Ca":0.20,"P":0.15,"Na":0.30,"K":0.25,"Mg":0.10,"Cl":0.50,"S":0.10,"NDF":8.0,"ADF":4.0,"CF":3.0,"Ash":3.0},
    "قش الأرز المعالج": {"Ca":0.15,"P":0.08,"Na":0.05,"K":1.50,"Mg":0.10,"Cl":0.10,"S":0.08,"NDF":65.0,"ADF":40.0,"CF":32.0,"Ash":12.0},
    "مسحوق أسماك (Fishmeal 60%)": {"Ca":5.50,"P":3.00,"Na":0.80,"K":0.90,"Mg":0.15,"Cl":1.20,"S":0.80,"NDF":2.5,"ADF":1.5,"CF":1.0,"Ash":22.5},
    "مسحوق اللحم والعظم": {"Ca":9.00,"P":4.50,"Na":0.80,"K":0.60,"Mg":0.20,"Cl":1.00,"S":0.60,"NDF":3.5,"ADF":2.5,"CF":1.5,"Ash":32.5},
    "مركزات دواجن وسمان": {"Ca":6.00,"P":3.50,"Na":0.60,"K":0.80,"Mg":0.30,"Cl":1.00,"S":0.40,"NDF":8.5,"ADF":4.5,"CF":3.0,"Ash":12.5},
    "مركزات خيول ومجترات": {"Ca":8.00,"P":4.00,"Na":0.80,"K":1.00,"Mg":0.50,"Cl":1.20,"S":0.50,"NDF":15.5,"ADF":8.5,"CF":6.0,"Ash":15.5},
    "بروتين مصل الحليب (WPC)": {"Ca":0.60,"P":0.45,"Na":0.70,"K":1.20,"Mg":0.08,"Cl":1.00,"S":0.28,"NDF":0.0,"ADF":0.0,"CF":0.0,"Ash":3.0},
    "ليسين نقي (L-Lysine)": {"Ca":0.0,"P":0.0,"Na":0.0,"K":0.0,"Mg":0.0,"Cl":0.30,"S":0.0,"NDF":0,"ADF":0,"CF":0,"Ash":0.5},
    "ميثيونين نقي (DL-Methionine)": {"Ca":0.0,"P":0.0,"Na":0.0,"K":0.0,"Mg":0.0,"Cl":0.0,"S":21.0,"NDF":0,"ADF":0,"CF":0,"Ash":0.3},
    "ثريونين نقي (L-Threonine)": {"Ca":0.0,"P":0.0,"Na":0.0,"K":0.0,"Mg":0.0,"Cl":0.0,"S":0.0,"NDF":0,"ADF":0,"CF":0,"Ash":0.2},
    "بريمكس تسمين دواجن (Premix)": {"Ca":20.0,"P":5.0,"Na":3.0,"K":2.0,"Mg":1.5,"Cl":4.0,"S":1.0,"NDF":0,"ADF":0,"CF":0,"Ash":100.0},
    "بريمكس بياض وبشاير": {"Ca":25.0,"P":5.5,"Na":3.5,"K":2.5,"Mg":1.8,"Cl":4.5,"S":1.2,"NDF":0,"ADF":0,"CF":0,"Ash":100.0},
    "بريمكس أبقار حلابة ومجترات": {"Ca":18.0,"P":6.0,"Na":4.0,"K":3.0,"Mg":2.5,"Cl":5.0,"S":1.5,"NDF":0,"ADF":0,"CF":0,"Ash":100.0},
    "إنزيم الفايتيز الزامي (Phytase Super-D)": {"Ca":0,"P":0,"Na":0,"K":0,"Mg":0,"Cl":0,"S":0,"NDF":0,"ADF":0,"CF":0,"Ash":5.0},
    "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": {"Ca":0,"P":0,"Na":0,"K":0,"Mg":0,"Cl":0,"S":0,"NDF":0,"ADF":0,"CF":0,"Ash":3.0},
    "كبريتات الحديدوز (معادل الجوسيبول)": {"Ca":0,"P":0,"Na":0,"K":0,"Mg":0,"Cl":0,"S":18.0,"NDF":0,"ADF":0,"CF":0,"Ash":98.0},
    "خميرة الخبز (Yeast)": {"Ca":0.10,"P":1.40,"Na":0.10,"K":1.80,"Mg":0.20,"Cl":0.10,"S":0.35,"NDF":5.0,"ADF":2.0,"CF":1.5,"Ash":7.0},
    "الحجر الجيري (بودرة بلاط)": {"Ca":38.0,"P":0.02,"Na":0.05,"K":0.10,"Mg":1.50,"Cl":0.02,"S":0.05,"NDF":0,"ADF":0,"CF":0,"Ash":99.5},
    "فوسفات ثنائي الكالسيوم (DCP)": {"Ca":24.0,"P":18.5,"Na":0.10,"K":0.05,"Mg":0.20,"Cl":0.10,"S":0.10,"NDF":0,"ADF":0,"CF":0,"Ash":98.5},
    "ملح الطعام": {"Ca":0.02,"P":0.0,"Na":39.0,"K":0.0,"Mg":0.02,"Cl":59.0,"S":0.05,"NDF":0,"ADF":0,"CF":0,"Ash":99.9},
    "مضاد سموم فطرية": {"Ca":2.50,"P":0.0,"Na":0.10,"K":0.05,"Mg":3.0,"Cl":0.05,"S":0.10,"NDF":0,"ADF":0,"CF":0,"Ash":85.0},
    "بيكربونات الصوديوم (الصودا)": {"Ca":0.0,"P":0.0,"Na":27.4,"K":0.0,"Mg":0.0,"Cl":0.0,"S":0.0,"NDF":0,"ADF":0,"CF":0,"Ash":99.0},
    "أكسيد المغنيسيوم العلفي": {"Ca":0.0,"P":0.0,"Na":0.0,"K":0.0,"Mg":60.0,"Cl":0.0,"S":0.0,"NDF":0,"ADF":0,"CF":0,"Ash":99.5},
    "يوريا علفية محصنة (المجترات فقط)": {"Ca":0,"P":0,"Na":0,"K":0,"Mg":0,"Cl":0,"S":0,"NDF":0,"ADF":0,"CF":0,"Ash":1.0},
    "كلوريد الكولين (Choline Chloride)": {"Ca":0,"P":0,"Na":0,"K":0,"Mg":0,"Cl":26.0,"S":0,"NDF":0,"ADF":0,"CF":0,"Ash":75.0},
    "مصل الحليب المجفف (Whey)": {"Ca":0.90,"P":0.70,"Na":1.10,"K":1.60,"Mg":0.10,"Cl":1.80,"S":0.25,"NDF":0,"ADF":0,"CF":0,"Ash":8.0},
    "حليب مجفف خالي الدسم": {"Ca":1.30,"P":1.00,"Na":0.50,"K":1.70,"Mg":0.12,"Cl":1.10,"S":0.35,"NDF":0,"ADF":0,"CF":0,"Ash":8.5},
    "دهن نباتي (زيت نباتي)": {"Ca":0,"P":0,"Na":0,"K":0,"Mg":0,"Cl":0,"S":0,"NDF":0,"ADF":0,"CF":0,"Ash":0.0},
    "ليسيثين الصويا": {"Ca":0,"P":2.30,"Na":0,"K":0,"Mg":0,"Cl":0,"S":0,"NDF":0,"ADF":0,"CF":0,"Ash":0.5},
    "فيتامينات ومعادن (Premix)": {"Ca":15.0,"P":7.0,"Na":3.0,"K":2.0,"Mg":1.5,"Cl":4.0,"S":1.0,"NDF":0,"ADF":0,"CF":0,"Ash":100.0},
    "بروتين الصويا المركز": {"Ca":0.40,"P":0.80,"Na":0.05,"K":2.10,"Mg":0.30,"Cl":0.05,"S":0.42,"NDF":2.0,"ADF":1.0,"CF":0.5,"Ash":5.5},
}


def calculate_minerals_fibers(formula):
    totals = {k: 0.0 for k in _DEFAULT_MF}
    missing = []
    for ing, pct in formula.items():
        mf = MINERALS_FIBER_DB.get(ing)
        if mf is None:
            missing.append(ing)
            mf = _DEFAULT_MF
        f = pct / 100.0
        for k in totals:
            totals[k] += f * mf.get(k, 0.0)
    ratios = {}
    if totals["P"] > 0:
        ratios["Ca_P_ratio"] = totals["Ca"] / totals["P"]
    if totals["Na"] > 0:
        ratios["K_Na_ratio"] = totals["K"] / totals["Na"]
    return {"values": totals, "ratios": ratios,
            "missing_ingredients": missing}


def evaluate_against_standard(computed, standard):
    result = {}
    for key, std_val in standard.items():
        calc = computed.get(key, 0.0)
        if std_val <= 0:
            result[key] = {"calculated": calc, "standard": std_val,
                           "deviation": 0.0, "grade": "-",
                           "status": "neutral"}
            continue
        dev = ((calc - std_val) / std_val) * 100
        tol = 10.0 if key in ["Ca","P","Na","Cl"] else 15.0
        if abs(dev) <= tol * 0.5:
            g, s = "✅ ممتاز", "excellent"
        elif abs(dev) <= tol:
            g, s = "👍 جيد", "good"
        elif dev > 0:
            g, s = "🔺 مرتفع", "high"
        else:
            g, s = "🔻 منخفض", "low"
        result[key] = {"calculated": calc, "standard": std_val,
                       "deviation": dev, "grade": g, "status": s}
    return result


def get_ideal_ca_p_ratio(animal):
    m = {"أبقار":1.5,"أغنام":2.0,"ماعز":2.0,"خيول":1.8,"إبل":1.5,
         "دواجن لاحم":2.0,"دواجن بياض":4.0,"سمان":2.0,"أسماك":1.2}
    return m.get(animal, 2.0)


# =====================================================================
# المعايير
# =====================================================================
STANDARD_VALUES = {
    "أبقار": {
        "تسمين عجول": {"DP": 12.0, "SE": 68.0, "CP": 15.0},
        "حليب/إدرار": {"DP": 14.0, "SE": 70.0, "CP": 17.5},
        "حمل/دفع غذائي": {"DP": 11.0, "SE": 65.0, "CP": 13.8},
        "صيانة": {"DP": 9.0, "SE": 60.0, "CP": 11.3}},
    "أغنام": {
        "تسمين حملان": {"DP": 13.0, "SE": 66.0, "CP": 16.3},
        "حليب/إدرار": {"DP": 14.5, "SE": 68.0, "CP": 18.1},
        "حمل/دفع غذائي": {"DP": 11.5, "SE": 62.0, "CP": 14.4},
        "صيانة": {"DP": 8.5, "SE": 58.0, "CP": 10.6}},
    "ماعز": {
        "تسمين جديان": {"DP": 12.5, "SE": 64.0, "CP": 15.6},
        "حليب/إدرار": {"DP": 14.0, "SE": 66.0, "CP": 17.5},
        "حمل/دفع غذائي": {"DP": 11.0, "SE": 60.0, "CP": 13.8},
        "صيانة": {"DP": 8.0, "SE": 56.0, "CP": 10.0}},
    "خيول": {
        "راحة/صيانة": {"DP": 9.0, "SE": 58.0, "CP": 11.3},
        "عمل خفيف": {"DP": 10.0, "SE": 60.0, "CP": 12.5},
        "عمل متوسط": {"DP": 11.0, "SE": 62.0, "CP": 13.8},
        "عمل مكثف": {"DP": 13.0, "SE": 65.0, "CP": 16.3},
        "سباق": {"DP": 14.0, "SE": 68.0, "CP": 17.5},
        "أمهار نامية": {"DP": 13.0, "SE": 64.0, "CP": 16.3},
        "فرسات مرضعات": {"DP": 14.0, "SE": 66.0, "CP": 17.5}},
    "إبل": {
        "راحة/صيانة": {"DP": 8.0, "SE": 55.0, "CP": 10.0},
        "حمل/رضاعة": {"DP": 10.0, "SE": 58.0, "CP": 12.5},
        "إنتاج حليب": {"DP": 12.0, "SE": 60.0, "CP": 15.0},
        "تسمين": {"DP": 11.0, "SE": 62.0, "CP": 13.8},
        "عمل/نقل": {"DP": 10.0, "SE": 58.0, "CP": 12.5}},
    "دواجن لاحم": {
        "بادي (0-14 يوم)": {"DP": 22.0, "SE": 76.0, "CP": 27.5},
        "نامي (15-28 يوم)": {"DP": 20.0, "SE": 74.0, "CP": 25.0},
        "ناهي (29-42 يوم)": {"DP": 18.0, "SE": 72.0, "CP": 22.5},
        "ناهي متقدم (43+ يوم)": {"DP": 16.0, "SE": 70.0, "CP": 20.0}},
    "دواجن بياض": {
        "بادي (0-6 أسبوع)": {"DP": 20.0, "SE": 72.0, "CP": 25.0},
        "نامي (7-14 أسبوع)": {"DP": 18.0, "SE": 70.0, "CP": 22.5},
        "قبل الإنتاج (15-18 أسبوع)": {"DP": 16.5, "SE": 68.0, "CP": 20.6},
        "بياض إنتاجي": {"DP": 16.0, "SE": 66.0, "CP": 20.0}},
    "سمان": {
        "بادي": {"DP": 24.0, "SE": 74.0, "CP": 30.0},
        "نامي": {"DP": 22.0, "SE": 72.0, "CP": 27.5},
        "بياض": {"DP": 18.0, "SE": 68.0, "CP": 22.5}},
    "أسماك": {
        "زريعة/بادئ": {"DP": 32.0, "SE": 70.0, "CP": 40.0},
        "نمو": {"DP": 28.0, "SE": 68.0, "CP": 35.0},
        "تسمين نهائي": {"DP": 26.0, "SE": 66.0, "CP": 32.5},
        "زريعة متقدمة": {"DP": 30.0, "SE": 69.0, "CP": 37.5}}
}


MINERAL_FIBER_STANDARDS = {
    "أبقار": {
        "تسمين عجول": {"Ca":0.60,"P":0.30,"Na":0.15,"K":0.65,"Mg":0.20,"Cl":0.25,"S":0.20,"NDF":35.0,"ADF":20.0,"CF":15.0,"Ash":6.5},
        "حليب/إدرار": {"Ca":0.75,"P":0.45,"Na":0.20,"K":0.90,"Mg":0.25,"Cl":0.30,"S":0.22,"NDF":30.0,"ADF":18.0,"CF":13.0,"Ash":7.0},
        "حمل/دفع غذائي": {"Ca":0.50,"P":0.28,"Na":0.12,"K":0.55,"Mg":0.18,"Cl":0.20,"S":0.18,"NDF":40.0,"ADF":25.0,"CF":18.0,"Ash":6.0},
        "صيانة": {"Ca":0.40,"P":0.22,"Na":0.10,"K":0.50,"Mg":0.15,"Cl":0.18,"S":0.15,"NDF":45.0,"ADF":28.0,"CF":22.0,"Ash":6.0}},
    "أغنام": {
        "تسمين حملان": {"Ca":0.55,"P":0.30,"Na":0.15,"K":0.60,"Mg":0.20,"Cl":0.22,"S":0.20,"NDF":35.0,"ADF":22.0,"CF":16.0,"Ash":7.0},
        "حليب/إدرار": {"Ca":0.70,"P":0.40,"Na":0.20,"K":0.85,"Mg":0.25,"Cl":0.28,"S":0.22,"NDF":32.0,"ADF":20.0,"CF":15.0,"Ash":7.5},
        "حمل/دفع غذائي": {"Ca":0.48,"P":0.26,"Na":0.12,"K":0.55,"Mg":0.18,"Cl":0.20,"S":0.18,"NDF":42.0,"ADF":28.0,"CF":20.0,"Ash":6.5},
        "صيانة": {"Ca":0.40,"P":0.20,"Na":0.10,"K":0.50,"Mg":0.15,"Cl":0.18,"S":0.15,"NDF":48.0,"ADF":32.0,"CF":24.0,"Ash":6.5}},
    "ماعز": {
        "تسمين جديان": {"Ca":0.60,"P":0.32,"Na":0.15,"K":0.65,"Mg":0.22,"Cl":0.22,"S":0.20,"NDF":38.0,"ADF":24.0,"CF":17.0,"Ash":7.0},
        "حليب/إدرار": {"Ca":0.75,"P":0.42,"Na":0.20,"K":0.90,"Mg":0.28,"Cl":0.28,"S":0.22,"NDF":34.0,"ADF":22.0,"CF":16.0,"Ash":7.5},
        "حمل/دفع غذائي": {"Ca":0.52,"P":0.28,"Na":0.12,"K":0.58,"Mg":0.20,"Cl":0.20,"S":0.18,"NDF":44.0,"ADF":30.0,"CF":22.0,"Ash":6.5},
        "صيانة": {"Ca":0.42,"P":0.22,"Na":0.10,"K":0.52,"Mg":0.16,"Cl":0.18,"S":0.15,"NDF":50.0,"ADF":34.0,"CF":26.0,"Ash":6.5}},
    "خيول": {
        "راحة/صيانة": {"Ca":0.45,"P":0.28,"Na":0.15,"K":0.55,"Mg":0.18,"Cl":0.25,"S":0.18,"NDF":45.0,"ADF":30.0,"CF":22.0,"Ash":7.0},
        "عمل خفيف": {"Ca":0.50,"P":0.30,"Na":0.18,"K":0.60,"Mg":0.20,"Cl":0.28,"S":0.20,"NDF":42.0,"ADF":28.0,"CF":20.0,"Ash":6.8},
        "عمل متوسط": {"Ca":0.55,"P":0.32,"Na":0.20,"K":0.65,"Mg":0.22,"Cl":0.30,"S":0.20,"NDF":40.0,"ADF":26.0,"CF":18.0,"Ash":6.5},
        "عمل مكثف": {"Ca":0.65,"P":0.38,"Na":0.25,"K":0.75,"Mg":0.25,"Cl":0.35,"S":0.22,"NDF":35.0,"ADF":22.0,"CF":15.0,"Ash":6.5},
        "سباق": {"Ca":0.75,"P":0.45,"Na":0.30,"K":0.85,"Mg":0.28,"Cl":0.40,"S":0.25,"NDF":30.0,"ADF":18.0,"CF":12.0,"Ash":6.0},
        "أمهار نامية": {"Ca":0.80,"P":0.45,"Na":0.22,"K":0.80,"Mg":0.28,"Cl":0.30,"S":0.22,"NDF":32.0,"ADF":20.0,"CF":14.0,"Ash":6.5},
        "فرسات مرضعات": {"Ca":0.85,"P":0.50,"Na":0.25,"K":0.90,"Mg":0.30,"Cl":0.35,"S":0.25,"NDF":34.0,"ADF":22.0,"CF":16.0,"Ash":7.0}},
    "إبل": {
        "راحة/صيانة": {"Ca":0.40,"P":0.25,"Na":0.15,"K":0.55,"Mg":0.18,"Cl":0.22,"S":0.18,"NDF":48.0,"ADF":32.0,"CF":24.0,"Ash":7.0},
        "حمل/رضاعة": {"Ca":0.55,"P":0.32,"Na":0.20,"K":0.70,"Mg":0.22,"Cl":0.28,"S":0.20,"NDF":40.0,"ADF":26.0,"CF":20.0,"Ash":7.2},
        "إنتاج حليب": {"Ca":0.65,"P":0.40,"Na":0.22,"K":0.80,"Mg":0.25,"Cl":0.30,"S":0.22,"NDF":35.0,"ADF":22.0,"CF":16.0,"Ash":7.5},
        "تسمين": {"Ca":0.50,"P":0.30,"Na":0.18,"K":0.65,"Mg":0.20,"Cl":0.25,"S":0.20,"NDF":38.0,"ADF":24.0,"CF":18.0,"Ash":7.0},
        "عمل/نقل": {"Ca":0.48,"P":0.28,"Na":0.20,"K":0.60,"Mg":0.20,"Cl":0.28,"S":0.18,"NDF":42.0,"ADF":28.0,"CF":20.0,"Ash":7.0}},
    "دواجن لاحم": {
        "بادي (0-14 يوم)": {"Ca":1.00,"P":0.45,"Na":0.20,"K":0.85,"Mg":0.20,"Cl":0.25,"S":0.25,"NDF":8.0,"ADF":4.0,"CF":3.0,"Ash":6.0},
        "نامي (15-28 يوم)": {"Ca":0.90,"P":0.42,"Na":0.18,"K":0.80,"Mg":0.18,"Cl":0.22,"S":0.22,"NDF":9.0,"ADF":4.5,"CF":3.5,"Ash":5.8},
        "ناهي (29-42 يوم)": {"Ca":0.85,"P":0.40,"Na":0.16,"K":0.75,"Mg":0.17,"Cl":0.20,"S":0.20,"NDF":10.0,"ADF":5.0,"CF":4.0,"Ash":5.5},
        "ناهي متقدم (43+ يوم)": {"Ca":0.80,"P":0.38,"Na":0.15,"K":0.72,"Mg":0.16,"Cl":0.20,"S":0.20,"NDF":10.0,"ADF":5.5,"CF":4.5,"Ash":5.5}},
    "دواجن بياض": {
        "بادي (0-6 أسبوع)": {"Ca":0.95,"P":0.42,"Na":0.18,"K":0.80,"Mg":0.20,"Cl":0.22,"S":0.22,"NDF":9.0,"ADF":4.5,"CF":3.5,"Ash":6.0},
        "نامي (7-14 أسبوع)": {"Ca":0.85,"P":0.38,"Na":0.15,"K":0.75,"Mg":0.18,"Cl":0.20,"S":0.20,"NDF":11.0,"ADF":6.0,"CF":5.0,"Ash":6.5},
        "قبل الإنتاج (15-18 أسبوع)": {"Ca":2.00,"P":0.42,"Na":0.18,"K":0.75,"Mg":0.20,"Cl":0.22,"S":0.22,"NDF":11.0,"ADF":6.0,"CF":5.0,"Ash":8.0},
        "بياض إنتاجي": {"Ca":3.80,"P":0.45,"Na":0.18,"K":0.75,"Mg":0.25,"Cl":0.22,"S":0.22,"NDF":10.0,"ADF":5.5,"CF":4.5,"Ash":11.5}},
    "سمان": {
        "بادي": {"Ca":1.10,"P":0.50,"Na":0.20,"K":0.85,"Mg":0.20,"Cl":0.25,"S":0.25,"NDF":7.0,"ADF":3.5,"CF":2.5,"Ash":6.5},
        "نامي": {"Ca":1.00,"P":0.45,"Na":0.18,"K":0.80,"Mg":0.18,"Cl":0.22,"S":0.22,"NDF":8.0,"ADF":4.0,"CF":3.0,"Ash":6.5},
        "بياض": {"Ca":2.80,"P":0.45,"Na":0.18,"K":0.75,"Mg":0.22,"Cl":0.22,"S":0.22,"NDF":9.0,"ADF":4.5,"CF":3.5,"Ash":11.0}},
    "أسماك": {
        "زريعة/بادئ": {"Ca":1.00,"P":0.85,"Na":0.20,"K":0.80,"Mg":0.20,"Cl":0.30,"S":0.25,"NDF":5.0,"ADF":2.5,"CF":2.0,"Ash":10.0},
        "نمو": {"Ca":0.90,"P":0.75,"Na":0.18,"K":0.75,"Mg":0.18,"Cl":0.28,"S":0.22,"NDF":6.0,"ADF":3.0,"CF":2.5,"Ash":9.0},
        "تسمين نهائي": {"Ca":0.80,"P":0.65,"Na":0.15,"K":0.70,"Mg":0.16,"Cl":0.25,"S":0.20,"NDF":7.0,"ADF":3.5,"CF":3.0,"Ash":8.5},
        "زريعة متقدمة": {"Ca":0.95,"P":0.80,"Na":0.20,"K":0.78,"Mg":0.18,"Cl":0.28,"S":0.22,"NDF":5.5,"ADF":2.8,"CF":2.2,"Ash":9.5}}
}


# =====================================================================
# 🆕 محرك التركيب الشامل التلقائي (v19.3) - قلب النظام
# =====================================================================
SUPPLEMENT_RANGES = {
    "الحجر الجيري (بودرة بلاط)": (0.0, 3.5),
    "فوسفات ثنائي الكالسيوم (DCP)": (0.0, 2.5),
    "ملح الطعام": (0.20, 0.80),
    "مضاد سموم فطرية": (0.10, 0.30),
    "بيكربونات الصوديوم (الصودا)": (0.30, 1.20),
    "يوريا علفية محصنة (المجترات فقط)": (0.0, 1.0),
    "إنزيم الفايتيز الزامي (Phytase Super-D)": (0.03, 0.10),
    "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": (0.05, 0.15),
    "كبريتات الحديدوز (معادل الجوسيبول)": (0.05, 0.25),
    "بريمكس تسمين دواجن (Premix)": (0.20, 0.50),
    "بريمكس بياض وبشاير": (0.20, 0.50),
    "بريمكس أبقار حلابة ومجترات": (0.20, 0.50),
    "فيتامينات ومعادن (Premix)": (0.20, 1.00),
    "خميرة الخبز (Yeast)": (0.0, 2.0),
    "مولاس قصب السكر": (0.0, 10.0),
    "أكسيد المغنيسيوم العلفي": (0.0, 0.30),
    "كلوريد الكولين (Choline Chloride)": (0.0, 0.30),
    "دهن نباتي (زيت نباتي)": (0.0, 5.0),
    "ليسيثين الصويا": (0.0, 2.0),
    "مسحوق أسماك (Fishmeal 60%)": (0.0, 10.0),
    "مسحوق اللحم والعظم": (0.0, 8.0),
    "كسب جلوتين الذرة 60%": (0.0, 15.0),
    "ليسين نقي (L-Lysine)": (0.0, 0.40),
    "ميثيونين نقي (DL-Methionine)": (0.0, 0.30),
    "ثريونين نقي (L-Threonine)": (0.0, 0.20),
    "كسب نواة النخيل": (0.0, 15.0),
    "كسب بذور اللفت (كانولا)": (0.0, 10.0),
    "تبن قمح ناعم": (0.0, 15.0),
    "قشر فول سوداني مطحون": (0.0, 10.0),
    "سرسة الأرز المطحونة": (0.0, 10.0),
    "قش الأرز المعالج": (0.0, 10.0),
    "مخلفات مصانع البسكويت": (0.0, 12.0),
    "بروتين مصل الحليب (WPC)": (0.0, 5.0),
    "حليب مجفف خالي الدسم": (0.0, 30.0),
    "مصل الحليب المجفف (Whey)": (0.0, 30.0),
    "بروتين الصويا المركز": (0.0, 15.0),
    "جريش أرز رزاز": (0.0, 20.0),
    "نخالة قمح (ردة)": (0.0, 25.0),
    "البرسيم الجاف (الدريس)": (0.0, 30.0),
}


def _build_vectors(selected):
    vecs = {k: [] for k in ["CP","DP","SE","Ca","P","Na","K","Mg","Cl","S",
                             "NDF","ADF","CF","Ash"]}
    for ing in selected:
        fd = FLAT_FEED_DB.get(ing, {})
        mf = MINERALS_FIBER_DB.get(ing, _DEFAULT_MF)
        cp = fd.get("CP", 0.0)
        dc = fd.get("DC", 0.0)
        vecs["CP"].append(cp)
        vecs["DP"].append(cp * dc)
        vecs["SE"].append(fd.get("SE", 0.0))
        for k in ["Ca","P","Na","K","Mg","Cl","S","NDF","ADF","CF","Ash"]:
            vecs[k].append(mf.get(k, 0.0))
    return vecs


def _build_bounds(selected):
    bounds = []
    for ing in selected:
        if ing in SUPPLEMENT_RANGES:
            lo, hi = SUPPLEMENT_RANGES[ing]
            bounds.append((max(0.0, lo), min(100.0, hi)))
        else:
            bounds.append((0.0, 100.0))
    return bounds


def auto_formulate_full(selected, prices, animal_key, display_name,
                          stage, use_cp=False, tolerance=0.25):
    """محرك LP يشمل كل القيود"""
    n = len(selected)
    if n < 3:
        return None, "اختر 3 مواد على الأقل"

    std = STANDARD_VALUES.get(display_name, {}).get(stage, {})
    mf_std = MINERAL_FIBER_STANDARDS.get(display_name, {}).get(stage, {})
    if not std and not mf_std:
        return None, "لا توجد معايير لهذه المرحلة"

    vecs = _build_vectors(selected)
    bounds = _build_bounds(selected)

    A_eq = [[1.0]*n]
    b_eq = [100.0]
    A_ub, b_ub = [], []

    # 1. الطاقة
    tgt_se = std.get("SE", 60.0)
    A_ub.append([-x for x in vecs["SE"]])
    b_ub.append(-tgt_se * 100.0)

    # 2. البروتين
    if use_cp:
        tgt_p = std.get("CP", 15.0)
        pv = vecs["CP"]
    else:
        tgt_p = std.get("DP", 12.0)
        pv = vecs["DP"]
    A_ub.append([-x for x in pv])
    b_ub.append(-tgt_p * 100.0)

    # 3. الأملاح
    for key in ["Ca","P","Na","K","Mg","Cl","S"]:
        if key not in mf_std or mf_std[key] <= 0:
            continue
        sv = mf_std[key]
        tol = tolerance * 1.5 if key in ("Na","Cl") else tolerance
        mn = max(0.0, sv * (1 - tol))
        mx = sv * (1 + tol)
        v = vecs[key]
        A_ub.append([-x for x in v])
        b_ub.append(-mn * 100.0)
        A_ub.append([x for x in v])
        b_ub.append(mx * 100.0)

    # 4. نسبة Ca:P
    if "Ca" in mf_std and "P" in mf_std:
        ideal = get_ideal_ca_p_ratio(display_name)
        rmin = max(0.8, ideal * 0.7)
        rmax = ideal * 1.4
        A_ub.append([-vecs["Ca"][i] + rmin * vecs["P"][i] for i in range(n)])
        b_ub.append(0.0)
        A_ub.append([vecs["Ca"][i] - rmax * vecs["P"][i] for i in range(n)])
        b_ub.append(0.0)

    # 5. الألياف
    for key in ["NDF","ADF","CF","Ash"]:
        if key not in mf_std or mf_std[key] <= 0:
            continue
        sv = mf_std[key]
        mx = sv * (1 + tolerance)
        A_ub.append([x for x in vecs[key]])
        b_ub.append(mx * 100.0)
        if animal_key in ("cattle","sheep","goat","camel","horse") \
                and key in ("NDF","ADF","CF"):
            mn = sv * (1 - tolerance)
            A_ub.append([-x for x in vecs[key]])
            b_ub.append(-mn * 100.0)

    c = [prices[i] for i in selected]
    try:
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                       bounds=bounds, method='highs')
    except Exception as e:
        return None, f"خطأ: {e}"
    ctx = {'std_vals': std, 'mf_std': mf_std, 'vecs': vecs}
    return res, ctx


def auto_formulate_relaxed(selected, prices, animal_key, display_name,
                             stage, use_cp=False):
    attempts = [(0.15, "دقيق ⭐"), (0.25, "متوسط ✅"),
                (0.40, "مرن 🔄"), (0.60, "واسع ⚠️"),
                (0.90, "شامل 🆘")]
    last = "لم يُوجد حل"
    for tol, label in attempts:
        res, ctx = auto_formulate_full(selected, prices, animal_key,
                                         display_name, stage, use_cp, tol)
        if res is not None and getattr(res, 'success', False):
            return res, ctx, label
        if isinstance(ctx, str):
            last = ctx
    return None, last, None


def compute_achieved(formula, selected, ctx):
    vecs = ctx['vecs']
    result = {k: 0.0 for k in vecs}
    for i, ing in enumerate(selected):
        if ing not in formula:
            continue
        p = formula[ing] / 100.0
        for k in vecs:
            result[k] += p * vecs[k][i]
    return result


# =====================================================================
# الأسعار
# =====================================================================
class MarketPriceEngine:
    @staticmethod
    @lru_cache(maxsize=128)
    def get_adjusted_market_data(country, state, city):
        base = {
            "ذرة صفراء": 230.0, "ذرة بيضاء": 225.0, "شعير مطحون": 210.0,
            "سورجم (فتريتة)": 195.0, "قمح محلي مصنّع": 240.0,
            "أمباز الفول السوداني (كسب)": 460.0,
            "كسب فول صويا 44%": 440.0, "كسب فول صويا 48%": 480.0,
            "كسب عباد الشمس 36%": 310.0,
            "كسب بذور القطن (مقشور)": 290.0,
            "نخالة قمح (ردة)": 150.0,
            "البرسيم الجاف (الدريس)": 170.0,
            "مولاس قصب السكر": 120.0,
            "مسحوق أسماك (Fishmeal 60%)": 850.0,
            "مركزات دواجن وسمان": 650.0,
            "مركزات خيول ومجترات": 600.0,
            "الحجر الجيري (بودرة بلاط)": 40.0,
            "فوسفات ثنائي الكالسيوم (DCP)": 280.0,
            "ملح الطعام": 30.0, "مضاد سموم فطرية": 950.0,
            "بيكربونات الصوديوم (الصودا)": 340.0,
            "خميرة الخبز (Yeast)": 450.0,
            "مصل الحليب المجفف (Whey)": 1200.0,
            "حليب مجفف خالي الدسم": 1800.0,
            "دهن نباتي (زيت نباتي)": 800.0,
            "ليسيثين الصويا": 1500.0,
            "بروتين الصويا المركز": 2000.0,
            "بريمكس تسمين دواجن (Premix)": 700.0,
            "بريمكس بياض وبشاير": 700.0,
            "بريمكس أبقار حلابة ومجترات": 650.0,
            "إنزيم الفايتيز الزامي (Phytase Super-D)": 1200.0,
            "إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)": 1100.0,
            "كبريتات الحديدوز (معادل الجوسيبول)": 500.0,
            "جريش أرز رزاز": 180.0, "دخن محلي غزير": 200.0,
            "شوفان علفي": 220.0, "كسب بذور الكتان": 400.0,
            "كسب السمسم المحسن": 420.0,
            "كسب جلوتين الذرة 60%": 620.0,
            "كسب نواة النخيل": 280.0,
            "كسب بذور اللفت (كانولا)": 380.0,
            "تبن قمح ناعم": 60.0,
            "قشر فول سوداني مطحون": 55.0,
            "سرسة الأرز المطحونة": 50.0,
            "مخلفات مصانع البسكويت": 180.0,
            "قش الأرز المعالج": 65.0,
            "مسحوق اللحم والعظم": 700.0,
            "بروتين مصل الحليب (WPC)": 2200.0,
            "ليسين نقي (L-Lysine)": 1600.0,
            "ميثيونين نقي (DL-Methionine)": 2400.0,
            "ثريونين نقي (L-Threonine)": 1800.0,
            "أكسيد المغنيسيوم العلفي": 550.0,
            "يوريا علفية محصنة (المجترات فقط)": 450.0,
            "كلوريد الكولين (Choline Chloride)": 900.0}
        prices = {ing: base.get(ing, 300.0)
                  for cat in BIG_FEEDS_LIBRARY.values() for ing in cat}
        m = 1.0
        if country == "السودان":
            m = 1.15
        elif country == "LIBYA":
            m = 1.10
        elif country == "مصر":
            m = 1.04
        return {k: v*m for k, v in prices.items()}


EXCHANGE_RATES = {
    "السودان": {"rate": 600.0, "sym": "SDG"},
    "LIBYA": {"rate": 4.80, "sym": "LYD"},
    "مصر": {"rate": 48.0, "sym": "EGP"},
    "دولار أمريكي": {"rate": 1.0, "sym": "USD"}}


# =====================================================================
# الخطوط والمولد
# =====================================================================
@st.cache_resource
def download_arabic_font():
    fp = "Amiri-Regular.ttf"
    if os.path.exists(fp):
        return fp
    try:
        import requests
        url = ("https://raw.githubusercontent.com/aliftype/amiri/"
               "master/fonts/Amiri-Regular.ttf")
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            with open(fp, "wb") as f:
                f.write(r.content)
            return fp
    except Exception:
        pass
    for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
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


class ProfessionalPDFGenerator:
    def __init__(self):
        self.fn = ensure_arabic_font()
        self.styles = self._styles()

    def _styles(self):
        s = {}
        s['title'] = ParagraphStyle('t', fontName=self.fn, fontSize=22,
            alignment=TA_CENTER, textColor=HexColor('#1b5e20'),
            spaceAfter=12, leading=28)
        s['subtitle'] = ParagraphStyle('st', fontName=self.fn, fontSize=15,
            alignment=TA_CENTER, textColor=HexColor('#2e7d32'),
            spaceAfter=10, leading=20)
        s['heading'] = ParagraphStyle('h', fontName=self.fn, fontSize=13,
            alignment=TA_RIGHT, textColor=HexColor('#1b5e20'),
            spaceAfter=8, leading=18)
        s['body'] = ParagraphStyle('b', fontName=self.fn, fontSize=11,
            alignment=TA_RIGHT, textColor=HexColor('#333'),
            spaceAfter=5, leading=16)
        s['footer'] = ParagraphStyle('f', fontName=self.fn, fontSize=8,
            alignment=TA_CENTER, textColor=HexColor('#999'),
            spaceAfter=0, leading=10)
        return s

    def _p(self, text, style='body'):
        return Paragraph(ar(str(text)),
                         self.styles.get(style, self.styles['body']))

    def _bismala(self, story):
        st_ = ParagraphStyle('b', fontName=self.fn, fontSize=22,
            alignment=TA_CENTER, textColor=HexColor('#1b5e20'),
            spaceAfter=6, leading=30)
        story.append(Paragraph(ar("﷽"), st_))
        story.append(Spacer(1, 6))
        bar = Table([[""]], colWidths=[520], rowHeights=[6])
        bar.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#2e7d32'))]))
        story.append(bar)
        story.append(Spacer(1, 12))
        return story

    def _section(self, story, text, color):
        st_ = ParagraphStyle('s', fontName=self.fn, fontSize=13,
            alignment=TA_CENTER, textColor=white,
            backColor=HexColor(color), borderPadding=(8, 12, 8, 12),
            leading=20)
        story.append(Paragraph(ar(text), st_))
        story.append(Spacer(1, 8))
        return story

    def _table(self, rows, color, widths=None):
        if widths is None:
            widths = [110, 90, 90, 90, 120]
        t = Table(rows, colWidths=widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), self.fn),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#bdbdbd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [HexColor('#f9f9f9'), HexColor('#ffffff')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
        return t

    def _recommendations(self, ev):
        recs = []
        if not ev:
            return ["لا توجد معايير."]
        for k, e in ev.items():
            s = e.get("status", "neutral")
            d = e.get("deviation", 0)
            if s == "high":
                m = {"Ca": "الكالسيوم مرتفع - قلل الحجر الجيري",
                     "P": "الفسفور مرتفع - راجع DCP",
                     "Na": "الصوديوم مرتفع - قلل الملح",
                     "NDF": "NDF مرتفع - يقلل الاستساغة",
                     "ADF": "ADF مرتفع - انخفاض الهضم"}
                recs.append(m.get(k, f"{k} مرتفع ({d:+.1f}%)"))
            elif s == "low":
                m = {"Ca": "الكالسيوم منخفض - أضف الحجر الجيري",
                     "P": "الفسفور منخفض - أضف DCP",
                     "Na": "الصوديوم منخفض - أضف الملح",
                     "K": "البوتاسيوم منخفض - أضف مولاس",
                     "NDF": "NDF منخفض - قد يسبب اضطراب الكرش",
                     "CF": "الألياف الخام منخفضة - زد الأعلاف الخشنة"}
                recs.append(m.get(k, f"{k} منخفض ({d:+.1f}%)"))
        return recs[:10] if recs else ["✅ جميع القيم ضمن النطاق"]

    def _chart(self, story, computed, standard, keys):
        try:
            ck = [k for k in keys if k in standard]
            if not ck:
                return
            fig, ax = plt.subplots(figsize=(7, 4))
            x = np.arange(len(ck))
            w = 0.35
            ax.bar(x - w/2, [computed.get(k, 0) for k in ck], w,
                   label=ar('المحقق'), color='#2e7d32')
            ax.bar(x + w/2, [standard.get(k, 0) for k in ck], w,
                   label=ar('القياسي'), color='#1565C0')
            ax.set_xticks(x)
            ax.set_xticklabels(ck, fontsize=10)
            ax.set_ylabel(ar('النسبة %'))
            ax.set_title(ar('مقارنة الأملاح والألياف'),
                          fontsize=12, fontweight='bold')
            ax.legend(loc='upper right', fontsize=9,
                       prop={'family': _MAT_FONT})
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=130, bbox_inches='tight',
                        facecolor='white')
            plt.close()
            buf.seek(0)
            story.append(Spacer(1, 10))
            story.append(Image(buf, width=440, height=250))
        except Exception:
            pass

    def _signature(self, story, requester=""):
        story.append(Spacer(1, 20))
        story.append(self._p("مع خالص التحية والتقدير،"))
        st_ = ParagraphStyle('s', fontName=self.fn, fontSize=12,
            alignment=TA_RIGHT, textColor=HexColor('#c62828'),
            spaceAfter=4, leading=18)
        story.append(Paragraph(
            ar("الاختصاصي م. عبد القادر إسماعيل تاور - "
               "اختصاصي تغذية الحيوان"), st_))
        if requester:
            story.append(self._p(f"طالب العلفة: {requester}"))
        story.append(Spacer(1, 12))
        story.append(self._p("🌾 تاور نولجي v19.3 © 2026", 'footer'))

    def generate_comprehensive_report(self, formula, dp, breed, cost, city,
                                       local_cost, local_sym, se, user,
                                       requester="", standard=None,
                                       extra_info=None, mineral_data=None,
                                       mf_standard=None, mf_evaluation=None,
                                       ratios=None):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=45,
            leftMargin=45, topMargin=25, bottomMargin=35)
        story = []
        story = self._bismala(story)
        story.append(self._p("🌾 تاور نولجي Tawornology", 'title'))
        story.append(self._p("📄 تقرير فني شامل - v19.3", 'subtitle'))
        story.append(Spacer(1, 10))

        info = [[ar("👨‍💻 المشرف"),
                 ar("الاختصاصي م. عبد القادر إسماعيل تاور")],
                [ar("👤 طالب العلفة"), ar(requester or '-')],
                [ar("🐾 الفصيل"), ar(breed)],
                [ar("📌 الموقع"), ar(city)],
                [ar("📅 التاريخ"),
                 ar(datetime.now().strftime('%Y-%m-%d %H:%M'))]]
        it = Table(info, colWidths=[140, 360])
        it.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e9')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), self.fn),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#a5d6a7')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
        story.append(it)
        story.append(Spacer(1, 15))

        story = self._section(story, "📋 المقادير لطن واحد", '#2e7d32')
        rows = [[ar('المكون'), ar('النسبة %'), ar('كجم/طن')]]
        for i, p in formula.items():
            rows.append([ar(i), f'{p:.2f}%', f'{p*10:.1f}'])
        story.append(self._table(rows, '#2e7d32', [220, 130, 130]))

        if mineral_data and mf_standard:
            story.append(PageBreak())
            story = self._section(story, "🧂 الأملاح", '#00838f')
            names = {"Ca":"كالسيوم","P":"فسفور","Na":"صوديوم",
                      "K":"بوتاسيوم","Mg":"مغنيسيوم","Cl":"كلور","S":"كبريت"}
            rows = [[ar('المعدن'), ar('المحقق %'), ar('القياسي %'),
                     ar('الانحراف %'), ar('التقييم')]]
            for k, n in names.items():
                if k in mf_standard:
                    e = mf_evaluation.get(k, {})
                    rows.append([ar(f"{n} ({k})"),
                        f"{e.get('calculated', 0):.3f}",
                        f"{e.get('standard', 0):.3f}",
                        f"{e.get('deviation', 0):+.1f}",
                        e.get("grade", "-")])
            story.append(self._table(rows, '#00838f'))
            story.append(Spacer(1, 15))

            story = self._section(story, "🌾 الألياف", '#6a1b9a')
            fn = {"NDF":"NDF","ADF":"ADF","CF":"CF","Ash":"رماد"}
            rows = [[ar('نوع الليف'), ar('المحقق %'), ar('القياسي %'),
                     ar('الانحراف %'), ar('التقييم')]]
            for k, n in fn.items():
                if k in mf_standard:
                    e = mf_evaluation.get(k, {})
                    rows.append([ar(n),
                        f"{e.get('calculated', 0):.2f}",
                        f"{e.get('standard', 0):.2f}",
                        f"{e.get('deviation', 0):+.1f}",
                        e.get("grade", "-")])
            story.append(self._table(rows, '#6a1b9a'))

            self._chart(story, mineral_data, mf_standard,
                ["Ca","P","Na","K","Mg","NDF","ADF","CF"])

            if ratios:
                story.append(Spacer(1, 12))
                story = self._section(story, "⚖️ النسب والتوصيات", '#c62828')
                ca_p = ratios.get("Ca_P_ratio", 0)
                k_na = ratios.get("K_Na_ratio", 0)
                ideal = get_ideal_ca_p_ratio(breed.split()[0] if breed else "")
                story.append(self._p(f"• Ca : P = {ca_p:.2f} (مثالي ≈ {ideal:.1f})"))
                story.append(self._p(f"• K : Na = {k_na:.2f} (مثالي ≈ 3.0)"))
                for r in self._recommendations(mf_evaluation):
                    story.append(self._p(f"• {r}"))

        self._signature(story, requester)
        doc.build(story)
        buf.seek(0)
        return buf.getvalue()

    def generate_lab_report(self, analysis, animal, stage, user, std,
                             evaluation=None, requester="",
                             mineral_fiber_data=None, mf_standard=None,
                             mf_evaluation=None, ratios=None):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40,
            leftMargin=40, topMargin=25, bottomMargin=35)
        story = []
        story = self._bismala(story)
        story.append(self._p("🔬 تقرير المختبر - v19.3", 'title'))
        story.append(Spacer(1, 10))

        if analysis and 'components' in analysis:
            story = self._section(story, "📦 المكونات", '#1565C0')
            rows = [[ar('المادة'), ar('الوزن (كجم)'), ar('النسبة %')]]
            tw = sum(analysis['components'].values())
            for n, w in analysis['components'].items():
                if w > 0:
                    p = (w/tw*100) if tw > 0 else 0
                    rows.append([ar(n), f"{w:.1f}", f"{p:.2f}"])
            story.append(self._table(rows, '#1565C0', [240, 130, 130]))
            story.append(Spacer(1, 15))

            story = self._section(story, "📊 النتائج", '#2e7d32')
            rows = [[ar('العنصر'), ar('القيمة')]]
            if 'cp' in analysis:
                rows.append([ar('CP'), f"{analysis['cp']:.2f}%"])
            if 'dp' in analysis:
                rows.append([ar('DP'), f"{analysis['dp']:.2f}%"])
            if 'se' in analysis:
                rows.append([ar('SE'), f"{analysis['se']:.2f}"])
            story.append(self._table(rows, '#2e7d32', [300, 200]))

        if mineral_fiber_data and mf_standard:
            story.append(PageBreak())
            story = self._section(story, "🧂 الأملاح", '#00838f')
            names = {"Ca":"كالسيوم","P":"فسفور","Na":"صوديوم",
                      "K":"بوتاسيوم","Mg":"مغنيسيوم","Cl":"كلور","S":"كبريت"}
            rows = [[ar('المعدن'), ar('المحقق %'), ar('القياسي %'),
                     ar('الانحراف %'), ar('التقييم')]]
            for k, n in names.items():
                if k in mf_standard:
                    e = mf_evaluation.get(k, {})
                    rows.append([ar(f"{n} ({k})"),
                        f"{e.get('calculated', 0):.3f}",
                        f"{e.get('standard', 0):.3f}",
                        f"{e.get('deviation', 0):+.1f}",
                        e.get("grade", "-")])
            story.append(self._table(rows, '#00838f'))
            story.append(Spacer(1, 15))

            story = self._section(story, "🌾 الألياف", '#6a1b9a')
            fn = {"NDF":"NDF","ADF":"ADF","CF":"CF","Ash":"رماد"}
            rows = [[ar('نوع الليف'), ar('المحقق %'), ar('القياسي %'),
                     ar('الانحراف %'), ar('التقييم')]]
            for k, n in fn.items():
                if k in mf_standard:
                    e = mf_evaluation.get(k, {})
                    rows.append([ar(n),
                        f"{e.get('calculated', 0):.2f}",
                        f"{e.get('standard', 0):.2f}",
                        f"{e.get('deviation', 0):+.1f}",
                        e.get("grade", "-")])
            story.append(self._table(rows, '#6a1b9a'))

            self._chart(story, mineral_fiber_data, mf_standard,
                ["Ca","P","Na","K","Mg","NDF","ADF","CF"])

        self._signature(story, requester)
        doc.build(story)
        buf.seek(0)
        return buf.getvalue()

    def generate_milk_replacer_report(self, formula, animal, age, instr, user):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=45,
            leftMargin=45, topMargin=25, bottomMargin=35)
        story = []
        story = self._bismala(story)
        story.append(self._p("🍼 تقرير بديل الحليب", 'title'))
        story.append(Spacer(1, 10))
        story.append(self._p(f"🐾 النوع: {animal}"))
        story.append(self._p(f"📅 العمر: {age} يوم"))
        story.append(Spacer(1, 15))
        story = self._section(story, "📋 المكونات", '#2e7d32')
        rows = [[ar('المكون'), ar('النسبة %'), ar('جم/كجم')]]
        for i, p in formula.items():
            rows.append([ar(i), f'{p:.2f}%', f'{p*10:.1f}'])
        story.append(self._table(rows, '#1b5e20', [200, 130, 130]))
        story.append(Spacer(1, 15))
        story = self._section(story, "📌 التعليمات", '#e65100')
        for line in instr.split('\n'):
            if line.strip():
                story.append(self._p(f"• {line.strip()}"))
        self._signature(story)
        doc.build(story)
        buf.seek(0)
        return buf.getvalue()


pdf_generator = ProfessionalPDFGenerator()


class PricePredictor:
    def __init__(self):
        self.db = get_db_manager()

    def get_trend(self, ing, days=30):
        rows = self.db.execute_query(
            "SELECT * FROM price_history WHERE ingredient_name=? "
            "ORDER BY record_date DESC LIMIT ?", (ing, days))
        if len(rows) < 3:
            return {'trend': 'stable', 'change_percent': 0,
                    'volatility': 0, 'current_price': 0}
        prices = [r[2] for r in rows]
        x = np.array(range(len(prices))).reshape(-1, 1)
        y = np.array(prices)
        m = LinearRegression()
        m.fit(x, y)
        s = m.coef_[0]
        c = ((prices[0] - prices[-1]) / prices[-1] * 100
             if prices[-1] > 0 else 0)
        t = 'up' if s > 0.5 else 'down' if s < -0.5 else 'stable'
        return {'trend': t, 'change_percent': c,
                'volatility': np.std(prices) / np.mean(prices)
                if np.mean(prices) > 0 else 0,
                'current_price': prices[0]}

    def predict_price(self, ing, days_ahead=7):
        rows = self.db.execute_query(
            "SELECT price FROM price_history WHERE ingredient_name=? "
            "ORDER BY record_date DESC LIMIT 30", (ing,))
        if len(rows) < 5:
            return {'prediction': None, 'current_price': None,
                    'trend': 'stable'}
        prices = [r[0] for r in rows]
        weights = np.array(range(1, len(prices) + 1))
        wa = np.average(prices, weights=weights)
        tr = ((prices[0] - prices[-1]) / len(prices) if len(prices) > 1 else 0)
        pred = wa + tr * days_ahead
        return {'prediction': max(0, pred),
                'current_price': prices[0] if prices else None,
                'trend': self.get_trend(ing)['trend']}


class SmartLabSystem:
    def __init__(self):
        self.db = get_db_manager()
        self.ocr = OCR_AVAILABLE or EASYOCR_AVAILABLE
        self.reader = None
        if EASYOCR_AVAILABLE:
            try:
                self.reader = easyocr.Reader(['ar', 'en'], gpu=False)
            except Exception:
                pass

    def analyze_image(self, image):
        if not self.ocr:
            return None, "OCR غير مثبت."
        results = []
        try:
            if EASYOCR_AVAILABLE and self.reader:
                for (_, text, prob) in self.reader.readtext(np.array(image)):
                    if prob > 0.3:
                        results.append(text)
            elif OCR_AVAILABLE:
                img = (PILImage.open(image)
                       if not isinstance(image, PILImage_module.Image)
                       else image)
                results = pytesseract.image_to_string(
                    img, lang='ara+eng').split('\n')
            return self._parse(results), None
        except Exception as e:
            return None, str(e)

    def _parse(self, texts):
        data = {k: None for k in ['cp','dc','se','ndf','adf','ee','ash',
                                    'moisture','ca','p','na','k']}
        data['sample_name'] = ''
        pats = {
            'cp': [r'بروتين\s*خام\s*[:=]?\s*([\d.]+)', r'CP\s*[:=]?\s*([\d.]+)'],
            'dc': [r'معامل\s*الهضم\s*[:=]?\s*([\d.]+)', r'DC\s*[:=]?\s*([\d.]+)'],
            'se': [r'معادل\s*النشاء\s*[:=]?\s*([\d.]+)', r'SE\s*[:=]?\s*([\d.]+)'],
            'ndf': [r'NDF\s*[:=]?\s*([\d.]+)'],
            'adf': [r'ADF\s*[:=]?\s*([\d.]+)'],
            'ee': [r'دهن\s*خام\s*[:=]?\s*([\d.]+)'],
            'ash': [r'رماد\s*[:=]?\s*([\d.]+)'],
            'moisture': [r'رطوبة\s*[:=]?\s*([\d.]+)'],
            'ca': [r'Ca\s*[:=]?\s*([\d.]+)'],
            'p': [r'P\s*[:=]?\s*([\d.]+)'],
            'na': [r'Na\s*[:=]?\s*([\d.]+)'],
            'k': [r'K\s*[:=]?\s*([\d.]+)']}
        for t in texts:
            tc = t.strip()
            if 'اسم' in tc and not data['sample_name']:
                parts = tc.split(':')
                if len(parts) > 1:
                    data['sample_name'] = parts[1].strip()
            for key, ps in pats.items():
                if data[key] is None:
                    for p in ps:
                        m = re.search(p, tc, re.IGNORECASE)
                        if m:
                            try:
                                data[key] = float(m.group(1))
                                break
                            except Exception:
                                pass
        return data

    def save(self, data):
        rid = secrets.token_hex(16)
        self.db.insert_record('lab_results', {
            'result_id': rid,
            'sample_name': data.get('sample_name', ''),
            'cp': data.get('cp') or 0.0, 'dc': data.get('dc') or 0.0,
            'se': data.get('se') or 0.0, 'ndf': data.get('ndf') or 0.0,
            'adf': data.get('adf') or 0.0, 'ee': data.get('ee') or 0.0,
            'ash': data.get('ash') or 0.0,
            'moisture': data.get('moisture') or 0.0,
            'analysis_date': datetime.now().isoformat(),
            'analyzed_by': data.get('analyzed_by', ''),
            'notes': data.get('notes', ''),
            'requester_name': data.get('requester_name', '')})
        return rid


class ScientificReferenceSystem:
    REFERENCES = {
        "general": {"title": "تغذية الحيوان العامة", "icon": "📚",
            "references": [{"id": "R1", "authors": "McDonald, P., et al.",
                "year": 2011, "title": "Animal Nutrition",
                "publisher": "Pearson",
                "summary": "المرجع الأساسي في تغذية الحيوان."}]},
        "minerals": {"title": "المعادن والفيتامينات", "icon": "🪨",
            "references": [{"id": "R2", "authors": "Underwood",
                "year": 1999, "title": "Mineral Nutrition of Livestock",
                "publisher": "CABI", "summary": "تغذية المعادن."}]},
        "poultry": {"title": "تغذية الدواجن", "icon": "🐔",
            "references": [{"id": "R3", "authors": "Leeson & Summers",
                "year": 2009, "title": "Commercial Poultry Nutrition",
                "publisher": "Nottingham",
                "summary": "تغذية الدواجن."}]},
        "fiber": {"title": "الألياف", "icon": "🌾",
            "references": [{"id": "R4", "authors": "Mertens, D.R.",
                "year": 1997, "title": "Fiber Requirements",
                "publisher": "JDS", "summary": "متطلبات الألياف."}]},
        "milk": {"title": "بدائل الحليب", "icon": "🍼",
            "references": [{"id": "R5", "authors": "Davis & Drackley",
                "year": 1998, "title": "Young Calf",
                "publisher": "Iowa",
                "summary": "تغذية العجول."}]}}

    KNOWLEDGE_BASE = {
        "البروتين المهضوم": {
            "answer": "البروتين الذي يستطيع الحيوان هضمه وامتصاصه فعلياً.",
            "simplified": "الجزء المفيد من البروتين."},
        "معادل النشاء": {
            "answer": "مقياس الطاقة مقارنة بالنشاء النقي.",
            "simplified": "مقياس طاقة العلف."},
        "NDF": {
            "answer": "الألياف المتعادلة - السليلوز + الهيميسليلوز + اللجنين.",
            "simplified": "الألياف الكلية."},
        "ADF": {
            "answer": "الألياف الحمضية - السليلوز + اللجنين.",
            "simplified": "صعوبة هضم الألياف."},
        "الكالسيوم": {
            "answer": "Ca:P مثالي: أبقار 1.5، أغنام 2، خيول 1.8، بياض 4.",
            "simplified": "نسبة الكالسيوم للفسفور."}}

    @staticmethod
    def get_answer(q):
        for k, v in ScientificReferenceSystem.KNOWLEDGE_BASE.items():
            if k in q:
                return v
        return None


ANIMAL_IMAGES_RESOURCES = {
    "أبقار": "https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?w=600",
    "ماعز": "https://images.unsplash.com/photo-1524388680868-377a2e6bbb1c?w=600",
    "أغنام": "https://images.unsplash.com/photo-1484557985045-edf25e08da73?w=600",
    "خيول": "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?w=600",
    "إبل": "https://images.unsplash.com/photo-1502175353174-a7a70e73b362?w=600",
    "دواجن": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?w=600",
    "أسماك": "https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?w=600",
    "عام": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1600"
}


class InventoryManager:
    @staticmethod
    def init():
        if "inventory" not in st.session_state:
            st.session_state["inventory"] = {}
            for cat in BIG_FEEDS_LIBRARY.values():
                for ing in cat:
                    st.session_state["inventory"][ing] = {
                        "quantity": 25.0, "min_threshold": 5.0, "unit": "طن"}

    @staticmethod
    def check_levels():
        w = {}
        for item, d in st.session_state["inventory"].items():
            qty = d["quantity"] if isinstance(d, dict) else d
            thr = d.get("min_threshold", 5.0) if isinstance(d, dict) else 5.0
            if qty <= 0:
                w[item] = {"status": "نفذ"}
            elif qty < thr:
                w[item] = {"status": "منخفض"}
        return w

    @staticmethod
    def summary():
        t = len(st.session_state["inventory"])
        q = sum(d["quantity"] if isinstance(d, dict) else d
                for d in st.session_state["inventory"].values())
        l = sum(1 for d in st.session_state["inventory"].values()
                if (d["quantity"] if isinstance(d, dict) else d)
                < (d.get("min_threshold", 5.0) if isinstance(d, dict) else 5.0))
        return {"total_items": t, "total_quantity": q, "low_stock": l}


InventoryManager.init()

# =====================================================================
# State
# =====================================================================
defaults = {
    "approved": False, "user_role": None, "login_welcome_shown": False,
    "login_attempts": 0, "last_login_time": None, "session_token": None,
    "broiler_farms": {}, "analysis_results": None,
    "analysis_animal": "غير محدد", "analysis_stage": "غير محدد",
    "daily_production_log": [], "dose_reminders": [],
    "active_formula": {}, "active_cp_tag": 12.0, "active_se_tag": 65.0,
    "active_animal_img": ANIMAL_IMAGES_RESOURCES["عام"],
    "active_stage_title": "إنتاج عام", "computed_ton_cost": 280.0,
    "lab_sample": None, "lab_sample_name": "", "lab_cp": 0.0,
    "lab_dc": 0.0, "lab_se": 0.0, "lab_ndf": 0.0, "lab_adf": 0.0,
    "lab_ee": 0.0, "lab_ash": 0.0, "lab_moisture": 0.0,
    "lab_notes": "", "lab_ca": 0.0, "lab_p": 0.0, "lab_na": 0.0,
    "lab_k": 0.0, "user": None, "device_id": None,
    "shared_comments": "• [توجيه الاختصاصي]: يرجى إضافة تعليقاتكم.\n"}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

get_or_create_device_id()
seed_price_history()

if "smart_lab_system" not in st.session_state:
    try:
        st.session_state["smart_lab_system"] = SmartLabSystem()
    except Exception:
        st.session_state["smart_lab_system"] = None

if "global_livestock_prices" not in st.session_state:
    st.session_state["global_livestock_prices"] = {
        "عجول تسمين هولشتاين ($)": 1350.0,
        "أبقار كنانة محلية ($)": 900.0,
        "ضأن وستيرلنغ ($)": 180.0,
        "ماعز نوبي ($)": 130.0,
        "خيول عربية أصيلة ($)": 4500.0,
        "إبل عربية ($)": 2500.0,
        "كتكوت لاحم ($)": 0.65}
if "global_products_prices" not in st.session_state:
    st.session_state["global_products_prices"] = {
        "كيلو لحم بقري ($)": 7.50, "كيلو لحم ضأن ($)": 9.00,
        "كيلو لحم دجاج ($)": 3.80,
        "طبق بيض 30 بيضة ($)": 4.20,
        "لتر حليب خام ($)": 0.90,
        "لتر حليب إبل ($)": 1.50}


# =====================================================================
# عرض الجداول العربية
# =====================================================================
def show_arabic_table(rows, color="#2e7d32", widths=None):
    if not rows:
        st.info("لا توجد بيانات.")
        return
    n = len(rows[0])
    if widths is None:
        widths = [f"{100/n:.1f}%" for _ in range(n)]
    html = f"""<div dir="rtl" style="overflow-x:auto; margin:12px 0;">
    <table style="width:100%; border-collapse:collapse;
                  font-family:'Cairo','Tajawal',sans-serif;
                  direction:rtl; text-align:right; font-size:0.92rem;
                  box-shadow:0 4px 20px rgba(0,0,0,0.08);
                  border-radius:12px; overflow:hidden;">
    <thead><tr style="background:{color}; color:white; font-weight:700;">"""
    for i, h in enumerate(rows[0]):
        html += (f'<th style="padding:12px 14px; text-align:center; '
                  f'width:{widths[i] if i < len(widths) else "auto"};">'
                  f'{h}</th>')
    html += "</tr></thead><tbody>"
    for ri, row in enumerate(rows[1:]):
        bg = "#ffffff" if ri % 2 == 0 else "#f8faf8"
        html += f'<tr style="background:{bg};">'
        for i, cell in enumerate(row):
            al = "right" if i == 0 else "center"
            cs = str(cell)
            tc = "#333"
            if "✅" in cs or "ممتاز" in cs:
                tc = "#2e7d32"
            elif "⚠️" in cs or "مرتفع" in cs:
                tc = "#c62828"
            elif "🔻" in cs or "منخفض" in cs:
                tc = "#e65100"
            elif "👍" in cs or "جيد" in cs:
                tc = "#1565C0"
            html += (f'<td style="padding:10px 14px; text-align:{al}; '
                      f'color:{tc}; border-bottom:1px solid #e8ece8; '
                      f'font-weight:{"600" if i == 0 else "400"};">'
                      f'{cell}</td>')
        html += "</tr>"
    html += "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)


def render_dua_bar():
    st.markdown("""
    <style>
    @keyframes scrollDuaLR {
        0% { transform: translateX(-100%); opacity: 0.2; }
        8% { opacity: 1; } 50% { opacity: 1; }
        92% { opacity: 1; }
        100% { transform: translateX(100%); opacity: 0.2; }
    }
    @keyframes glowTextDua {
        0%,100% { text-shadow: 0 0 8px #ffd700, 0 0 16px #ffd700, 0 0 30px #ff8c00; }
        50% { text-shadow: 0 0 20px #ffd700, 0 0 40px #ff8c00, 0 0 70px #ff4500; }
    }
    @keyframes pulseHeartDua {
        0%,100% { transform: scale(1); color: #ff6b6b; }
        50% { transform: scale(1.4); color: #ff1744; }
    }
    @keyframes bgShiftDua {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .dua-container {
        background: linear-gradient(90deg, #0d1b2a, #1a237e, #4a148c, #1a237e, #0d1b2a);
        background-size: 300% 300%;
        animation: bgShiftDua 14s ease infinite;
        padding: 24px 0; border-radius: 24px 24px 0 0;
        overflow: hidden; border: 3px solid #ffd700; border-bottom: none;
        box-shadow: 0 8px 40px rgba(255, 215, 0, 0.5);
        direction: ltr; position: relative; min-height: 90px;
    }
    .dua-track {
        display: inline-block; white-space: nowrap;
        animation: scrollDuaLR 35s linear infinite, glowTextDua 3s ease-in-out infinite;
        font-size: 1.75rem; font-weight: 800; color: #ffd700;
        padding: 0 30px;
        font-family: 'Cairo', 'Tajawal', sans-serif;
    }
    .dua-track .emoji-heart { display: inline-block;
        animation: pulseHeartDua 1.2s ease-in-out infinite; margin: 0 10px; }
    .dua-track .name-highlight {
        color: #ffab40; font-weight: 900;
        background: rgba(255, 215, 0, 0.18);
        padding: 2px 12px; border-radius: 8px;
    }
    .dua-static {
        background: linear-gradient(90deg, #1b2a4a, #2a1b4a, #1b2a4a);
        padding: 14px 20px; border-radius: 0 0 20px 20px;
        text-align: center; color: #e1bee7;
        font-size: 1.15rem; font-weight: 700;
        border: 3px solid #ffd700;
        direction: rtl; line-height: 1.9; margin-bottom: 20px;
    }
    .dua-static .name-highlight-static {
        color: #ffd700; font-weight: 900;
        background: rgba(255, 215, 0, 0.12);
        padding: 1px 10px; border-radius: 6px;
    }
    .dua-static .heart-sm {
        color: #ff6b6b; font-size: 1rem; margin: 0 6px;
        display: inline-block;
    }
    </style>
    <div class="dua-container">
        <div class="dua-track">
            ❤️ اللهم اغفر لـ <span class="name-highlight">إسماعيل تاور</span>
            و <span class="name-highlight">ابتسام</span>
            وارحمهما وأدخلهما فسيح جناتك ❤️
            اللهم اجعل قبرهما روضة من رياض الجنة ❤️
        </div>
    </div>
    <div class="dua-static">
        🕊️ <span class="name-highlight-static">اللهم اغفر لإسماعيل تاور وابتسام</span>
        <span class="heart-sm">❤️</span> وارحمهما وأدخلهما فسيح جناتك 🕊️
    </div>
    """, unsafe_allow_html=True)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
* { font-family: 'Cairo', 'Tajawal', sans-serif; }
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 50%, #f5f7fa 100%);
    background-attachment: fixed;
}
.main-box {
    background: rgba(255,255,255,0.92); padding: 35px; border-radius: 24px;
    box-shadow: 0 25px 70px rgba(0,0,0,0.15); margin-bottom: 35px;
}
.section-title {
    color: #1b5e20; border-right: 6px solid #2e7d32;
    text-align: right; font-size: 1.7rem; font-weight: 700;
    margin: 30px 0 25px 0;
    background: linear-gradient(to left, rgba(46,125,50,0.12), transparent);
    padding: 14px 22px; border-radius: 14px;
}
.formula-item {
    background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(232,245,233,0.95));
    padding: 16px 22px; border-radius: 14px; margin-bottom: 10px;
    font-weight: 600; color: #1b5e20 !important;
    border-right: 5px solid #2e7d32;
    box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    display: flex; justify-content: space-between; align-items: center;
}
.profile-img-style {
    width: 160px; height: 160px; border-radius: 50%; object-fit: cover;
    border: 4px solid #d4af37; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
.metric-card {
    background: white; padding: 22px; border-radius: 18px;
    box-shadow: 0 6px 30px rgba(0,0,0,0.08); text-align: center;
}
.metric-card .number { font-size: 2.2rem; font-weight: 900;
    color: #1b5e20; margin: 5px 0; }
.metric-card .label { font-size: 0.95rem; color: #666; font-weight: 600; }
.warning-card {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    padding: 15px; border-radius: 12px;
    border-right: 5px solid #f57c00;
    margin-bottom: 15px; direction: rtl; text-align: right;
    color: #e65100 !important;
}
.manual-book { background:#fff; padding:30px; border-radius:16px;
    box-shadow:0 8px 35px rgba(0,0,0,0.08); }
.book-chapter { background:linear-gradient(135deg,#1a237e,#283593);
    color:white; padding:15px 20px; border-radius:10px;
    font-weight:bold; margin-top:20px; }
.book-body { padding:20px 25px; font-size:1.05rem; line-height:1.8;
    color:#2c3e50; border-left:4px solid #3498db;
    background:#f8f9fa; border-radius:0 10px 10px 0; }
</style>
""", unsafe_allow_html=True)


def generate_formula_image(formula_data, dp, se, breed, stage, user):
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_facecolor('#f5f5f5')
    fig.patch.set_facecolor('#ffffff')
    title = ar(f"🧬 خلطة علفية - تاور نولجي\n"
               f"المشرف: {user}\n"
               f"الفصيل: {breed} | المرحلة: {stage}\n"
               f"DP: {dp:.1f}% | SE: {se:.1f}")
    ax.set_title(title, fontsize=14, fontweight='bold', pad=25)
    ings = list(formula_data.keys())
    kg = [p*10 for p in formula_data.values()]
    y = np.arange(len(ings))
    ax.barh(y, kg, color='#2e7d32', alpha=0.8, edgecolor='#1b5e20')
    ax.set_yticks(y)
    ax.set_yticklabels([ar(i) for i in ings], fontsize=11)
    ax.set_xlabel(ar('الكمية (كجم/طن)'), fontsize=12)
    for i, v in enumerate(kg):
        ax.text(v+3, i, ar(f'{v:.1f} كجم'), va='center', fontsize=10)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight',
                facecolor='white')
    plt.close()
    buf.seek(0)
    return buf


def send_image_to_whatsapp(image_buf, caption, phone=WHATSAPP_NUMBER):
    try:
        img_b64 = base64.b64encode(image_buf.getvalue()).decode()
        enc = urllib.parse.quote(caption)
        url = f"https://wa.me/{phone}?text={enc}"
        st.markdown(f"""
        <div style='background:#e8f5e9; padding:20px; border-radius:14px;
                    direction:rtl; text-align:center;'>
            <img src="data:image/png;base64,{img_b64}"
                 style="max-width:100%; border-radius:10px;
                        margin:15px 0; border:3px solid #2e7d32;">
            <br>
            <a href='{url}' target='_blank'>
                <button style='background:#25D366; color:white;
                                padding:14px 40px; border:none;
                                border-radius:35px; font-size:17px;
                                font-weight:bold; cursor:pointer;'>
                    📲 إرسال عبر واتساب
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        return True
    except Exception as e:
        st.error(f"❌ {e}")
        return False


def guide_section(name, text):
    with st.expander(f"📘 دليل استخدام {name}", expanded=False):
        st.markdown(f"<div style='background:#f0f8ff; padding:15px; "
                     f"border-radius:10px; direction:rtl;'>{text}</div>",
                     unsafe_allow_html=True)


# =====================================================================
# دالة التركيب الرئيسية (v19.3 - المحرك الشامل)
# =====================================================================
def render_feed_formulation(animal_key, display_name, icon, breeds, stages,
                             default_dp, default_se, img_key,
                             has_measurements=True):
    st.markdown(
        f'<div class="section-title">{icon} {display_name} - تركيب العلف</div>',
        unsafe_allow_html=True)

    st.success("🤖 **الوضع التلقائي الشامل (v19.3):** "
                "اختر المواد المتاحة، والنظام يحسب النسب تلقائياً "
                "وفقاً لكل الاحتياجات (طاقة + بروتين + أملاح + ألياف)")

    requester = st.text_input("👤 اسم طالب العلف:",
        placeholder="أدخل اسم المربي", key=f"{animal_key}_req")

    # الموقع
    st.markdown('<div class="section-title">🌍 الموقع الجغرافي</div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        country = st.selectbox("الدولة:",
            ["السودان", "LIBYA", "مصر", "دولار أمريكي"],
            key=f"{animal_key}_country")
    ci = EXCHANGE_RATES.get(country, {"rate": 1.0, "sym": "USD"})
    lr, ls = ci["rate"], ci["sym"]

    with c2:
        states_map = {
            "السودان": ["ولاية الخرطوم", "ولاية الجزيرة", "ولاية القضارف",
                        "ولاية شمال كردفان", "ولاية جنوب كردفان",
                        "ولاية غرب كردفان", "إقليم النيل الأزرق",
                        "ولاية البحر الأحمر", "ولاية نهر النيل"],
            "LIBYA": ["المنطقة الشرقية", "المنطقة الغربية",
                       "المنطقة الجنوبية"]}
        opts = states_map.get(country, ["المركز الرئيسي"])
        state = st.selectbox("الولاية:", opts, key=f"{animal_key}_state")

    with c3:
        cmap = {
            "ولاية الخرطوم": ["الخرطوم", "أم درمان", "بحري"],
            "ولاية الجزيرة": ["ود مدني", "الحصاحيصا", "المناقل"],
            "ولاية القضارف": ["القضارف", "الفاو"],
            "ولاية شمال كردفان": ["الأبيض", "بارا"],
            "ولاية جنوب كردفان": ["كادوقلي", "الدلنج"],
            "ولاية غرب كردفان": ["الفوله", "النهود"],
            "إقليم النيل الأزرق": ["الدمازين", "الروصيرص"],
            "ولاية البحر الأحمر": ["بورتسودان", "سواكن"],
            "ولاية نهر النيل": ["شندي", "عطبرة"],
            "المنطقة الشرقية": ["طبرق", "بنغازي", "البيضاء"],
            "المنطقة الغربية": ["طرابلس", "مصراتة"],
            "المنطقة الجنوبية": ["سبها", "مرزق"]}
        cities = cmap.get(state, ["عام"])
        city = st.selectbox("المدينة:", cities, key=f"{animal_key}_city")

    live_prices = MarketPriceEngine.get_adjusted_market_data(
        country, state, city)

    # السلالة والمرحلة
    st.markdown('<div class="section-title">🎯 السلالة والمرحلة</div>',
                unsafe_allow_html=True)
    cb, cs, ca = st.columns(3)
    with cb:
        breed = st.selectbox("السلالة:", breeds, key=f"{animal_key}_breed")
    with cs:
        stage = st.selectbox("المرحلة:", stages, key=f"{animal_key}_stage")
    with ca:
        age = st.number_input("العمر (شهر):", 1, 240, 24,
                               key=f"{animal_key}_age")

    if has_measurements:
        st.markdown('<div class="section-title">📐 القياسات</div>',
                    unsafe_allow_html=True)
        ch, cl = st.columns(2)
        wf_map = {"cattle": 10838, "sheep": 15500, "goat": 15000,
                  "horse": 11877, "camel": 13000}
        ff_map = {"cattle": 0.025, "sheep": 0.035, "goat": 0.032,
                  "horse": 0.022, "camel": 0.020}
        with ch:
            girth = st.number_input("محيط الصدر (سم):",
                value=150.0 if animal_key in ["cattle","horse"] else 75.0,
                key=f"{animal_key}_girth")
        with cl:
            length = st.number_input("طول الجسم (سم):",
                value=130.0 if animal_key in ["cattle","horse"] else 65.0,
                key=f"{animal_key}_length")
        wf = wf_map.get(animal_key, 12000)
        ff = ff_map.get(animal_key, 0.03)
        ew = (girth ** 2 * length) / wf
        st.success(f"⚖️ الوزن التقديري: **{ew:.1f} كجم** | "
                   f"الاحتياج اليومي: **{ew*ff:.2f} كجم مادة جافة**")

    # المعايير
    std_v = STANDARD_VALUES.get(display_name, {}).get(stage, {})
    mf_std_v = MINERAL_FIBER_STANDARDS.get(display_name, {}).get(stage, {})

    st.markdown(
        '<div class="section-title">📋 الاحتياجات الغذائية القياسية '
        '(تُطبَّق تلقائياً)</div>', unsafe_allow_html=True)
    st.info("🎯 النظام سيلتزم بهذه القيم أثناء حساب النسب:")

    cm1, cm2, cm3 = st.columns(3)
    cm1.metric("🧬 DP", f"{std_v.get('DP', default_dp):.2f}%")
    cm2.metric("⚡ SE", f"{std_v.get('SE', default_se):.2f}")
    cm3.metric("📊 CP", f"{std_v.get('CP', 0):.2f}%")

    if mf_std_v:
        with st.expander("🔬 الأملاح والألياف المطلوبة (تُطبَّق تلقائياً)",
                          expanded=False):
            rows = [["المقياس", "القيمة القياسية %"]]
            for k, v in mf_std_v.items():
                rows.append([k, f"{v:.3f}"])
            show_arabic_table(rows, "#00838f", ["50%","50%"])

    use_cp = st.checkbox("⚡ استخدم البروتين الخام (CP) بدلاً من المهضوم (DP)",
                          value=False, key=f"{animal_key}_cp_basis")

    # المواد المتاحة
    st.markdown(
        '<div class="section-title">🌾 المواد المتاحة في بيئتك</div>',
        unsafe_allow_html=True)
    st.info("✅ اختر المواد المتاحة عندك — النظام سيتكفل بتحديد النسب المثالية")

    qc1, qc2, qc3 = st.columns(3)
    with qc1:
        if st.button("✅ تحديد الكل", use_container_width=True,
                      key=f"{animal_key}_all"):
            for cat in BIG_FEEDS_LIBRARY.values():
                for ing in cat:
                    st.session_state[f"{animal_key}_feed_{ing}"] = True
            st.rerun()
    with qc2:
        if st.button("❌ إلغاء الكل", use_container_width=True,
                      key=f"{animal_key}_none"):
            for cat in BIG_FEEDS_LIBRARY.values():
                for ing in cat:
                    st.session_state[f"{animal_key}_feed_{ing}"] = False
            st.rerun()
    with qc3:
        if st.button("⭐ توصيات افتراضية", use_container_width=True,
                      key=f"{animal_key}_def"):
            dmap = {
                "cattle": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)",
                           "كسب فول صويا 44%",
                           "أمباز الفول السوداني (كسب)",
                           "مركزات خيول ومجترات", "ملح الطعام",
                           "الحجر الجيري (بودرة بلاط)",
                           "فوسفات ثنائي الكالسيوم (DCP)",
                           "بيكربونات الصوديوم (الصودا)"],
                "sheep": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)",
                          "كسب فول صويا 44%",
                          "أمباز الفول السوداني (كسب)",
                          "مركزات خيول ومجترات", "ملح الطعام",
                          "الحجر الجيري (بودرة بلاط)",
                          "فوسفات ثنائي الكالسيوم (DCP)",
                          "بيكربونات الصوديوم (الصودا)"],
                "goat": ["ذرة صفراء", "شعير مطحون", "نخالة قمح (ردة)",
                         "كسب فول صويا 44%",
                         "أمباز الفول السوداني (كسب)",
                         "مركزات خيول ومجترات", "ملح الطعام",
                         "الحجر الجيري (بودرة بلاط)",
                         "فوسفات ثنائي الكالسيوم (DCP)",
                         "بيكربونات الصوديوم (الصودا)"],
                "horse": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)",
                          "كسب فول صويا 44%",
                          "أمباز الفول السوداني (كسب)",
                          "مولاس قصب السكر",
                          "مركزات خيول ومجترات", "ملح الطعام",
                          "الحجر الجيري (بودرة بلاط)",
                          "فوسفات ثنائي الكالسيوم (DCP)"],
                "camel": ["شعير مطحون", "ذرة صفراء", "نخالة قمح (ردة)",
                          "كسب فول صويا 44%",
                          "أمباز الفول السوداني (كسب)",
                          "البرسيم الجاف (الدريس)",
                          "مركزات خيول ومجترات", "ملح الطعام",
                          "الحجر الجيري (بودرة بلاط)",
                          "فوسفات ثنائي الكالسيوم (DCP)",
                          "بيكربونات الصوديوم (الصودا)"],
                "poultry": ["ذرة صفراء", "سورجم (فتريتة)",
                            "كسب فول صويا 44%",
                            "كسب جلوتين الذرة 60%",
                            "مركزات دواجن وسمان",
                            "بريمكس تسمين دواجن (Premix)",
                            "ملح الطعام",
                            "الحجر الجيري (بودرة بلاط)",
                            "فوسفات ثنائي الكالسيوم (DCP)",
                            "إنزيم الفايتيز الزامي (Phytase Super-D)"],
                "fish": ["ذرة صفراء", "كسب فول صويا 44%",
                         "مسحوق أسماك (Fishmeal 60%)",
                         "كسب جلوتين الذرة 60%",
                         "مركزات دواجن وسمان", "ملح الطعام",
                         "فوسفات ثنائي الكالسيوم (DCP)",
                         "إنزيم الفايتيز الزامي (Phytase Super-D)"]}
            dset = set(dmap.get(animal_key, []))
            for cat in BIG_FEEDS_LIBRARY.values():
                for ing in cat:
                    st.session_state[f"{animal_key}_feed_{ing}"] = (
                        ing in dset)
            st.rerun()

    selected = []
    prices = {}
    for cat_name, items in BIG_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {cat_name}", expanded=False):
            cols = st.columns(3)
            for idx, ing in enumerate(items.keys()):
                with cols[idx % 3]:
                    if f"{animal_key}_feed_{ing}" not in st.session_state:
                        st.session_state[f"{animal_key}_feed_{ing}"] = False
                    ch = st.checkbox(ing, key=f"{animal_key}_feed_{ing}")
                    cp = live_prices.get(ing, 350.0)
                    if ch:
                        if get_current_user_role() == "owner":
                            pr = st.number_input(
                                "💰 $/طن", min_value=5.0,
                                value=float(cp), step=5.0,
                                key=f"{animal_key}_price_{ing}")
                        else:
                            st.caption(f"💰 ${cp:.2f}/طن")
                            pr = cp
                        selected.append(ing)
                        prices[ing] = pr

    if not selected:
        st.warning("⚠️ **يرجى اختيار المواد المتاحة في بيئتك**")
        return

    # الإضافات الإلزامية (تُضاف تلقائياً إذا لم تُختر)
    mandatory = {
        "ملح الطعام": 0.5, "مضاد سموم فطرية": 0.2,
        "الحجر الجيري (بودرة بلاط)": 1.5,
        "فوسفات ثنائي الكالسيوم (DCP)": 1.0}
    auto_add = {}
    warns = []

    if animal_key in ["cattle", "sheep", "goat", "camel"]:
        auto_add["بيكربونات الصوديوم (الصودا)"] = 0.75
        warns.append("🚨 <b>بيكربونات الصوديوم 0.75%</b> — "
                     "حماية الكرش من التحمض.")
    elif animal_key == "poultry":
        auto_add["بيكربونات الصوديوم (الصودا)"] = 0.20

    if animal_key in ["poultry", "fish"]:
        auto_add["إنزيم الفايتيز الزامي (Phytase Super-D)"] = 0.05
        warns.append("🚨 <b>إنزيم الفايتيز 0.05%</b> — "
                     "لتحرير الفسفور النباتي.")

    if ("كسب بذور القطن (مقشور)" in selected
            and animal_key == "poultry"):
        auto_add["كبريتات الحديدوز (معادل الجوسيبول)"] = 0.15
        warns.append("⚠️ <b>معادل الجوسيبول 0.15%</b>.")

    if animal_key == "poultry" and any(
            x in selected for x in ["شعير مطحون", "قمح محلي مصنّع"]):
        auto_add["إنزيم الـ NSP (زيلاناز + بيتا جلوكاناز)"] = 0.08
        warns.append("⚠️ <b>إنزيمات NSP 0.08%</b>.")

    all_auto = {**mandatory, **auto_add}
    for it in all_auto:
        if it not in selected:
            selected.append(it)
            prices[it] = live_prices.get(it, 40.0)

    # زر التشغيل
    st.markdown("---")
    st.info(f"🎯 **جاهز للتشغيل** — {len(selected)} مادة مختارة | "
            f"الاحتياجات ستُطبَّق تلقائياً: DP={std_v.get('DP', default_dp):.1f}%, "
            f"SE={std_v.get('SE', default_se):.1f}")

    if st.button(f"🚀 تشغيل المحرك الشامل ({display_name})",
                  type="primary", use_container_width=True,
                  key=f"{animal_key}_run"):
        if len(selected) < 3:
            st.warning("⚠️ اختر 3 مكونات على الأقل.")
        else:
            with st.spinner("🔄 حل شامل: طاقة + بروتين + أملاح + ألياف..."):
                res, ctx, level = auto_formulate_relaxed(
                    selected, prices, animal_key, display_name,
                    stage, use_cp)

                if res is None or not res.success:
                    st.error(f"❌ تعذر إيجاد حل: {ctx}")
                    st.info("💡 **جرّب:**\n"
                            "- إضافة مصدر بروتين (كسب صويا/فول/أسماك)\n"
                            "- إضافة مصدر طاقة (ذرة/شعير/سورجم)\n"
                            "- إضافة مصدر Ca (حجر جيري) و P (DCP)\n"
                            "- إضافة مصدر ألياف (نخالة/دريس/تبن)")
                else:
                    formula = {}
                    for i, ing in enumerate(selected):
                        if res.x[i] > 0.0001:
                            formula[ing] = res.x[i]
                    ton_cost = res.fun / 100.0

                    st.success(f"🎯 تم التركيب الشامل بنجاح في: {city} "
                                f"| مستوى: **{level}**")
                    voice_guide(f"تم التركيب بتكلفة {ton_cost:.2f} دولار.")

                    if warns:
                        st.markdown("### 🔬 التعديلات الإلزامية المدمجة:")
                        for w in warns:
                            st.markdown(
                                f'<div class="warning-card">{w}</div>',
                                unsafe_allow_html=True)

                    st.markdown("#### 📝 النسب المعتمدة:")
                    rows = [["المكون", "النسبة %", "كجم/طن", "الحالة"]]
                    for k, v in sorted(formula.items(),
                                        key=lambda x: -x[1]):
                        st_ = ("🔒 إضافي" if k in all_auto
                               else "🟢 أساسي" if v >= 20
                               else "🟡 ثانوي" if v >= 5
                               else "⚪ مكمل")
                        rows.append([k, f"{v:.2f}%", f"{v*10:.1f}", st_])
                    show_arabic_table(rows, "#2e7d32",
                                      ["40%","18%","18%","24%"])

                    # التحقق الشامل
                    achieved = compute_achieved(formula, selected, ctx)
                    std_a = ctx['std_vals']
                    mf_std = ctx['mf_std']

                    st.markdown("#### ✅ التحقق من تحقيق كل الاحتياجات:")

                    mc1, mc2, mc3 = st.columns(3)
                    with mc1:
                        tgt = std_a.get("DP", 12.0)
                        d = achieved["DP"] - tgt
                        mc1.metric("🧬 DP %", f"{achieved['DP']:.2f}",
                                    delta=f"{d:+.2f} | هدف {tgt:.1f}")
                    with mc2:
                        tgt = std_a.get("SE", 65.0)
                        d = achieved["SE"] - tgt
                        mc2.metric("⚡ SE", f"{achieved['SE']:.2f}",
                                    delta=f"{d:+.2f} | هدف {tgt:.1f}")
                    with mc3:
                        mc3.metric("📊 CP %", f"{achieved['CP']:.2f}",
                                    delta=f"مرجعي {std_a.get('CP', 0):.1f}")

                    st.markdown("##### 🧂 الأملاح (المعادن):")
                    mrows = [["المعدن", "المحقق %", "القياسي %",
                              "الانحراف", "الحالة"]]
                    mnames = {"Ca": "كالسيوم", "P": "فسفور", "Na": "صوديوم",
                               "K": "بوتاسيوم", "Mg": "مغنيسيوم",
                               "Cl": "كلور", "S": "كبريت"}
                    for k, n in mnames.items():
                        if k not in mf_std:
                            continue
                        tgt = mf_std[k]
                        act = achieved[k]
                        dev = ((act - tgt) / tgt * 100) if tgt > 0 else 0
                        if abs(dev) <= 10:
                            g = "✅ ممتاز"
                        elif abs(dev) <= 20:
                            g = "👍 جيد"
                        elif dev > 0:
                            g = "🔺 مرتفع"
                        else:
                            g = "🔻 منخفض"
                        mrows.append([n, f"{act:.3f}", f"{tgt:.3f}",
                                       f"{dev:+.1f}%", g])
                    show_arabic_table(mrows, "#00838f",
                                      ["25%","20%","20%","17%","18%"])

                    st.markdown("##### 🌾 الألياف:")
                    frows = [["نوع الليف", "المحقق %", "القياسي %",
                              "الانحراف", "الحالة"]]
                    fnames = {"NDF": "ألياف متعادلة NDF",
                               "ADF": "ألياف حمضية ADF",
                               "CF": "ألياف خام CF", "Ash": "رماد Ash"}
                    for k, n in fnames.items():
                        if k not in mf_std:
                            continue
                        tgt = mf_std[k]
                        act = achieved[k]
                        dev = ((act - tgt) / tgt * 100) if tgt > 0 else 0
                        if abs(dev) <= 15:
                            g = "✅ ممتاز"
                        elif abs(dev) <= 25:
                            g = "👍 جيد"
                        elif dev > 0:
                            g = "🔺 مرتفع"
                        else:
                            g = "🔻 منخفض"
                        frows.append([n, f"{act:.2f}", f"{tgt:.2f}",
                                       f"{dev:+.1f}%", g])
                    show_arabic_table(frows, "#6a1b9a",
                                      ["30%","18%","18%","17%","17%"])

                    ca_p = (achieved["Ca"] / achieved["P"]
                             if achieved["P"] > 0 else 0)
                    k_na = (achieved["K"] / achieved["Na"]
                             if achieved["Na"] > 0 else 0)
                    ideal = get_ideal_ca_p_ratio(display_name)
                    n1, n2 = st.columns(2)
                    n1.metric("⚖️ Ca : P", f"{ca_p:.2f}",
                               delta=f"المثالي ≈ {ideal:.1f}")
                    n2.metric("⚖️ K : Na", f"{k_na:.2f}",
                               delta="المثالي ≈ 3.0")

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("💰 التكلفة/طن", f"${ton_cost:.2f}")
                    c2.metric("🧬 DP", f"{achieved['DP']:.2f}%")
                    c3.metric("⚡ SE", f"{achieved['SE']:.2f}")
                    c4.metric("📊 مكونات", len(formula))

                    if len(formula) > 1:
                        fig = px.pie(values=list(formula.values()),
                            names=list(formula.keys()),
                            title="توزيع المكونات",
                            color_discrete_sequence=
                                px.colors.sequential.Greens)
                        fig.update_layout(height=400,
                            font=dict(family="Cairo, Tajawal, sans-serif"))
                        st.plotly_chart(fig, use_container_width=True)

                    ck = [k for k in ["Ca","P","Na","K","Mg","NDF","ADF","CF"]
                          if k in mf_std]
                    if ck:
                        fig2 = go.Figure()
                        fig2.add_trace(go.Bar(
                            x=ck, y=[achieved.get(k, 0) for k in ck],
                            name="المحقق", marker_color="#2e7d32"))
                        fig2.add_trace(go.Bar(
                            x=ck, y=[mf_std.get(k, 0) for k in ck],
                            name="القياسي", marker_color="#1565C0"))
                        fig2.update_layout(
                            title="مقارنة التحقق مع المعايير",
                            barmode="group",
                            font=dict(family=
                                "Cairo, Tajawal, sans-serif"),
                            height=400)
                        st.plotly_chart(fig2, use_container_width=True)

                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("💾 حفظ الخلطة",
                                      use_container_width=True,
                                      key=f"{animal_key}_save"):
                            db = get_db_manager()
                            try:
                                db.insert_record('feed_formulas', {
                                    'formula_id': secrets.token_hex(16),
                                    'formula_name':
                                        f"{display_name}-{breed}-{stage}",
                                    'animal_type': display_name,
                                    'breed': breed, 'stage': stage,
                                    'target_dp': achieved['DP'],
                                    'target_se': achieved['SE'],
                                    'ingredients': json.dumps(
                                        formula, ensure_ascii=False),
                                    'total_cost': ton_cost*1000,
                                    'cost_per_ton': ton_cost,
                                    'created_by': get_current_user_name(),
                                    'created_date':
                                        datetime.now().isoformat(),
                                    'requester_name': requester})
                                st.success("✅ تم الحفظ!")
                            except Exception as e:
                                st.error(f"❌ {e}")
                    with b2:
                        if st.button("📲 مشاركة كصورة",
                                      use_container_width=True,
                                      key=f"{animal_key}_share"):
                            img = generate_formula_image(
                                formula, achieved["DP"],
                                achieved["SE"], breed, stage,
                                get_current_user_name())
                            cap = (f"خلطة {display_name} | "
                                    f"DP:{achieved['DP']:.1f}% | "
                                    f"SE:{achieved['SE']:.0f} | "
                                    f"${ton_cost:.2f}/طن")
                            send_image_to_whatsapp(img, cap)

                    # PDF
                    try:
                        mf_r = calculate_minerals_fibers(formula)
                        mf_ev = evaluate_against_standard(
                            mf_r["values"], mf_std) if mf_std else {}
                        pdf_data = pdf_generator.generate_comprehensive_report(
                            formula, achieved["DP"],
                            f"{breed} - {stage}", ton_cost, city,
                            ton_cost*lr, ls, achieved["SE"],
                            user_name=get_current_user_name(),
                            requester_name=requester,
                            standard=std_a,
                            extra_info={"السلالة": breed,
                                        "المرحلة": stage,
                                        "العمر": f"{age} شهر",
                                        "الدولة": country,
                                        "المدينة": city},
                            mineral_data=mf_r["values"],
                            mf_standard=mf_std,
                            mf_evaluation=mf_ev,
                            ratios=mf_r["ratios"])
                        st.download_button(
                            "📥 تحميل PDF الشامل", pdf_data,
                            file_name=f"Tawor_{display_name}_"
                                      f"{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            use_container_width=True)
                    except Exception as e:
                        st.warning(f"⚠️ PDF: {e}")

                    if st.button("🔬 إرسال للمختبر",
                                  use_container_width=True,
                                  key=f"{animal_key}_lab"):
                        st.session_state["lab_sample"] = {
                            'formula': formula,
                            'animal': display_name, 'breed': breed,
                            'stage': stage, 'age': age,
                            'dp': achieved["DP"],
                            'se': achieved["SE"],
                            'cp': achieved["CP"],
                            'requester': requester}
                        st.success("✅ تم الإرسال للمختبر.")

                    st.session_state["active_formula"] = formula
                    st.session_state["active_cp_tag"] = achieved["DP"]
                    st.session_state["active_se_tag"] = achieved["SE"]
                    st.session_state["computed_ton_cost"] = ton_cost
                    st.session_state["active_animal_img"] = \
                        ANIMAL_IMAGES_RESOURCES.get(
                            img_key, ANIMAL_IMAGES_RESOURCES["عام"])
                    st.session_state["active_stage_title"] = stage


# =====================================================================
# المختبر المتقدم
# =====================================================================
def render_advanced_lab():
    st.markdown('<div class="section-title">🔬 المختبر المتقدم</div>',
                unsafe_allow_html=True)

    if st.session_state.get("lab_sample"):
        s = st.session_state["lab_sample"]
        st.success(f"📥 عينة من {s['animal']} - {s['breed']}")
        if st.button("🗑️ مسح"):
            st.session_state["lab_sample"] = None
            st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        animal = st.selectbox("الفصيل:",
            ["أبقار", "أغنام", "ماعز", "خيول", "إبل",
             "دواجن لاحم", "دواجن بياض", "سمان", "أسماك"])
        stage = st.selectbox("المرحلة:",
            list(STANDARD_VALUES.get(animal, {}).keys()))
        std = STANDARD_VALUES.get(animal, {}).get(stage, {})
        mf_std = MINERAL_FIBER_STANDARDS.get(animal, {}).get(stage, {})
    with c2:
        st.selectbox("نظام البروتين:", ["DP", "CP"])
        st.selectbox("نظام الطاقة:", ["SE", "ME"])

    inputs = {}
    cols = st.columns(3)
    for idx, ing in enumerate(FLAT_FEED_DB.keys()):
        with cols[idx % 3]:
            inputs[ing] = st.number_input(f"وزن {ing} (كجم)",
                min_value=0.0, value=0.0, step=5.0, key=f"lab_{ing}")

    req = st.text_input("👤 اسم الطالب:", key="lab_req")

    if st.button("🧪 تشغيل التحليل", type="primary",
                  use_container_width=True):
        total = sum(inputs.values())
        if total <= 0:
            st.warning("⚠️ أدخل أوزاناً.")
        else:
            cp_t = dp_t = se_t = 0.0
            comps = []
            for ing, w in inputs.items():
                if w > 0:
                    p = w / total
                    fd = FLAT_FEED_DB.get(ing, {})
                    cp = fd.get("CP", 0.0)
                    dc = fd.get("DC", 0.0)
                    se = fd.get("SE", 0.0)
                    cp_t += p * cp
                    dp_t += p * (cp * dc)
                    se_t += p * se
                    comps.append([ing, f"{w:.1f}", f"{p*100:.2f}"])

            pcts = {i: (w/total*100) for i, w in inputs.items() if w > 0}
            mf_r = calculate_minerals_fibers(pcts)
            mf_ev = (evaluate_against_standard(mf_r["values"], mf_std)
                     if mf_std else {})

            st.session_state["analysis_results"] = {
                'components': inputs, 'cp': cp_t, 'dp': dp_t, 'se': se_t}
            st.session_state["analysis_animal"] = animal
            st.session_state["analysis_stage"] = stage

            st.success("🔬 تم التحليل!")
            st.markdown(f"### إجمالي الوزن: **{total:.1f} كجم**")

            t1, t2, t3 = st.tabs(["📋 المكونات", "🧬 بروتين",
                                    "🧂 أملاح وألياف"])
            with t1:
                show_arabic_table([["المادة", "الوزن", "النسبة %"]] + comps,
                                   "#1565C0", ["50%","25%","25%"])
            with t2:
                rows = [["العنصر", "القيمة"],
                        ["CP", f"{cp_t:.2f}%"],
                        ["DP", f"{dp_t:.2f}%"],
                        ["SE", f"{se_t:.2f}"]]
                show_arabic_table(rows, "#2e7d32", ["60%","40%"])
            with t3:
                mv = mf_r["values"]
                mrows = [["المعدن", "المحقق %", "القياسي %",
                          "الانحراف", "الحالة"]]
                mnames = {"Ca": "كالسيوم", "P": "فسفور", "Na": "صوديوم",
                           "K": "بوتاسيوم", "Mg": "مغنيسيوم",
                           "Cl": "كلور", "S": "كبريت"}
                for k, n in mnames.items():
                    if k not in mf_std:
                        continue
                    tgt = mf_std[k]
                    act = mv.get(k, 0)
                    dev = ((act-tgt)/tgt*100) if tgt > 0 else 0
                    g = ("✅" if abs(dev) <= 10
                         else "👍" if abs(dev) <= 20
                         else "🔺" if dev > 0 else "🔻")
                    mrows.append([n, f"{act:.3f}", f"{tgt:.3f}",
                                   f"{dev:+.1f}%", g])
                show_arabic_table(mrows, "#00838f")

                frows = [["الليف", "المحقق %", "القياسي %",
                          "الانحراف", "الحالة"]]
                fnames = {"NDF": "NDF", "ADF": "ADF", "CF": "CF",
                           "Ash": "رماد"}
                for k, n in fnames.items():
                    if k not in mf_std:
                        continue
                    tgt = mf_std[k]
                    act = mv.get(k, 0)
                    dev = ((act-tgt)/tgt*100) if tgt > 0 else 0
                    g = ("✅" if abs(dev) <= 15
                         else "👍" if abs(dev) <= 25
                         else "🔺" if dev > 0 else "🔻")
                    frows.append([n, f"{act:.2f}", f"{tgt:.2f}",
                                   f"{dev:+.1f}%", g])
                show_arabic_table(frows, "#6a1b9a")

            try:
                pdf_data = pdf_generator.generate_lab_report(
                    st.session_state["analysis_results"], animal, stage,
                    get_current_user_name(), std, None, requester_name=req,
                    mineral_fiber_data=mf_r["values"],
                    mf_standard=mf_std, mf_evaluation=mf_ev,
                    ratios=mf_r["ratios"])
                st.download_button("📥 تحميل تقرير المختبر", pdf_data,
                    file_name=f"Lab_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ {e}")


# =====================================================================
# المختبر الذكي
# =====================================================================
def render_smart_lab():
    st.markdown('<div class="section-title">🧪 المختبر الذكي</div>',
                unsafe_allow_html=True)
    if not OCR_AVAILABLE and not EASYOCR_AVAILABLE:
        st.warning("pip install easyocr")

    up = st.file_uploader("ارفع صورة", type=['png','jpg','jpeg'])
    img = None
    if up:
        try:
            img = PILImage_module.open(up)
            st.image(img, use_container_width=True)
        except Exception:
            img = None
        if (st.session_state.get("smart_lab_system") and img and
                st.button("🔍 تحليل")):
            with st.spinner("..."):
                r, e = st.session_state[
                    "smart_lab_system"].analyze_image(img)
                if e:
                    st.error(e)
                else:
                    st.success("✅")
                    for k, v in [('lab_sample_name','sample_name'),
                                  ('lab_cp','cp'), ('lab_dc','dc'),
                                  ('lab_se','se'), ('lab_ndf','ndf'),
                                  ('lab_adf','adf')]:
                        st.session_state[k] = r.get(v) or ""

    c1, c2 = st.columns(2)
    with c1:
        st.text_input("اسم العينة:", key="lab_sample_name")
        st.number_input("CP:", value=float(st.session_state.get("lab_cp") or 0),
                         key="lab_cp", step=0.1)
        st.number_input("DC:", value=float(st.session_state.get("lab_dc") or 0),
                         key="lab_dc", step=0.01)
    with c2:
        st.number_input("SE:", value=float(st.session_state.get("lab_se") or 0),
                         key="lab_se", step=0.1)
        st.number_input("NDF:", value=float(st.session_state.get("lab_ndf") or 0),
                         key="lab_ndf", step=0.1)
        st.number_input("ADF:", value=float(st.session_state.get("lab_adf") or 0),
                         key="lab_adf", step=0.1)

    st.text_area("ملاحظات:", key="lab_notes")
    req = st.text_input("👤 الطالب:", key="smart_req")

    if st.button("💾 حفظ", type="secondary"):
        if st.session_state.get("smart_lab_system"):
            data = {k: st.session_state.get(k) for k in
                    ['lab_sample_name','lab_cp','lab_dc','lab_se',
                     'lab_ndf','lab_adf','lab_notes']}
            data['sample_name'] = st.session_state.get('lab_sample_name','')
            data['analyzed_by'] = get_current_user_name()
            data['requester_name'] = req
            rid = st.session_state["smart_lab_system"].save(data)
            st.success(f"✅ {rid[:8]}")


# =====================================================================
# شاشة الدخول
# =====================================================================
MAX_LOGIN = 5
LOCKOUT = 300

if st.session_state.get("user") and \
        st.session_state["user"].get("role") == "owner" and \
        st.session_state.get("session_token"):
    st.session_state["approved"] = True

if not st.session_state.get("approved", False):
    render_dua_bar()
    if st.session_state.get("login_attempts", 0) >= MAX_LOGIN:
        if st.session_state.get("last_login_time"):
            dt = (datetime.now() -
                  st.session_state["last_login_time"]).seconds
            if dt < LOCKOUT:
                st.error(f"🔒 قفل مؤقت. بعد {LOCKOUT - dt} ثانية")
                st.stop()
            else:
                st.session_state["login_attempts"] = 0

    st.markdown('<div class="main-box" style="max-width:550px; '
                'margin:80px auto; direction:rtl;">', unsafe_allow_html=True)
    if img_base64:
        st.markdown(
            f'<img src="data:image/jpeg;base64,{img_base64}" '
            f'style="width:100px; height:100px; border-radius:50%; '
            f'border:3px solid #d4af37; display:block; margin:0 auto;">',
            unsafe_allow_html=True)
    st.markdown(
        "<h2 style='color:#1a237e; text-align:center;'>"
        "🌾 تاور نولجي Tawornology</h2>",
        unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555;'>"
                "للانتاج الحيواني وتركيب الاعلاف - v19.3</p>",
                unsafe_allow_html=True)

    cs1, cs2 = st.columns(2)
    with cs1:
        if st.button("🔊 ترحيب", use_container_width=True):
            play_welcome_audio()
    with cs2:
        if st.button("🕊️ دعاء", use_container_width=True):
            play_dua_audio()

    if st.button("👤 دخول كزائر", type="primary",
                  use_container_width=True):
        auth = AuthManager()
        u = auth.login_public()
        if u:
            st.session_state["approved"] = True
            st.session_state["user_role"] = "public"
            st.session_state["login_welcome_shown"] = False
            st.session_state["last_login_time"] = datetime.now()
            st.session_state["session_token"] = secrets.token_urlsafe(32)
            st.session_state["user"] = u
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    opt = st.radio("طريقة الدخول:", ["كود سري", "اسم المستخدم"],
                    horizontal=True)

    if opt == "كود سري":
        code = st.text_input("🔑 الكود:", type="password")
        if st.button("دخول 🔓", type="secondary", use_container_width=True):
            ud = validate_access_code(code)
            if ud:
                st.session_state["approved"] = True
                st.session_state["user_role"] = ud["role"]
                st.session_state["login_welcome_shown"] = False
                st.session_state["last_login_time"] = datetime.now()
                st.session_state["session_token"] = \
                    secrets.token_urlsafe(32)
                st.session_state["user"] = {
                    "full_name": ud["name"], "role": ud["role"],
                    "user_id": f"code_{ud['role']}"}
                st.rerun()
            else:
                st.session_state["login_attempts"] = \
                    st.session_state.get("login_attempts", 0) + 1
                rem = MAX_LOGIN - st.session_state["login_attempts"]
                st.error(f"❌ كود خاطئ! متبقي {rem}")
    else:
        un = st.text_input("👤 المستخدم")
        pw = st.text_input("🔑 كلمة المرور", type="password")
        if st.button("دخول 🔓", type="primary", use_container_width=True):
            auth = AuthManager()
            u = auth.authenticate(un, pw)
            if u:
                st.session_state["approved"] = True
                st.session_state["user_role"] = u['role']
                st.session_state["login_welcome_shown"] = False
                st.session_state["last_login_time"] = datetime.now()
                st.session_state["session_token"] = \
                    secrets.token_urlsafe(32)
                st.session_state["user"] = u
                st.rerun()
            else:
                st.session_state["login_attempts"] = \
                    st.session_state.get("login_attempts", 0) + 1
                rem = MAX_LOGIN - st.session_state["login_attempts"]
                st.error(f"❌ خطأ! متبقي {rem}")
        st.caption("💡 admin / admin123")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


if not st.session_state.get("login_welcome_shown"):
    rmsgs = {"owner": "👑 مرحباً، الاختصاصي",
             "specialist": "🔬 أهلاً بالمختصين",
             "veterinarian": "💊 أهلاً بالطبيب",
             "nutritionist": "🧬 أهلاً بالأخصائي",
             "breeder": "🌾 أهلاً بالمربي",
             "public": "👤 مرحباً زائراً"}
    st.toast(rmsgs.get(st.session_state.get("user_role"), "مرحباً"),
             icon="🌾")
    voice_welcome(st.session_state.get("user_role", "public"))
    st.session_state["login_welcome_shown"] = True

render_dua_bar()

# =====================================================================
# الواجهة الرئيسية
# =====================================================================
st.markdown('<div class="main-box">', unsafe_allow_html=True)

c_logout, c_status = st.columns([0.7, 0.3])
with c_status:
    rnames = {"owner": "المالك 👑", "specialist": "المختص 👨‍🔬",
              "veterinarian": "الطبيب 💊",
              "nutritionist": "التغذية 🧬",
              "breeder": "المربي 🌾", "public": "زائر 👤"}
    un = get_current_user_name()
    ur = get_current_user_role()
    st.markdown(f"""
    <div style='text-align:left; background:linear-gradient(135deg,#f5f5f5,#e0e0e0);
                padding:14px; border-radius:14px;'>
        <div style='font-weight:700;'>{un}</div>
        <div style='font-size:0.85rem; color:#555;'>
            {rnames.get(ur, "مستخدم")}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 خروج", use_container_width=True):
        keep = ["inventory", "broiler_farms", "analysis_results",
                "email_password", "device_id", "smart_lab_system"]
        for k in list(st.session_state.keys()):
            if k not in keep:
                del st.session_state[k]
        st.session_state["approved"] = False
        st.rerun()

c1, c2 = st.columns([0.2, 0.8])
with c1:
    src = (f"data:image/jpeg;base64,{img_base64}"
           if img_base64 else ANIMAL_IMAGES_RESOURCES["عام"])
    st.markdown(f'<img src="{src}" class="profile-img-style">',
                 unsafe_allow_html=True)
with c2:
    st.markdown("<h1 style='color:#1a237e; text-align:right;'>"
                "🌾 تاور نولجي Tawornology</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='color:#1565C0; text-align:right; "
                "font-size:1.2rem;'>"
                "للانتاج الحيواني وتركيب الاعلاف - v19.3</p>",
                unsafe_allow_html=True)
    st.markdown("<h3 style='color:#c62828; text-align:right;'>"
                "الاختصاصي م. عبد القادر إسماعيل تاور</h3>",
                unsafe_allow_html=True)

st.markdown("<hr style='border-top:3px solid #2e7d32;'>",
             unsafe_allow_html=True)

st.markdown("### 📊 لوحة التحكم")
cs = InventoryManager.summary()
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"<div class='metric-card'><div class='number'>"
             f"{cs['total_items']}</div><div class='label'>"
             f"إجمالي المواد</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='metric-card'><div class='number'>"
             f"{cs['total_quantity']:.1f}</div><div class='label'>"
             f"المخزون (طن)</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='metric-card'><div class='number'>"
             f"{cs['low_stock']}</div><div class='label'>"
             f"مواد منخفضة</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='metric-card'><div class='number'>"
             f"{len(st.session_state.get('broiler_farms', {}))}</div>"
             f"<div class='label'>مزارع</div></div>",
             unsafe_allow_html=True)
st.markdown("---")


# =====================================================================
# التبويبات
# =====================================================================
tt = [
    "🐾 القطاع الحيواني", "🧪 المختبر الذكي", "🔬 المختبر المتقدم",
    "🐔 إدارة المزارع", "🍼 بدائل الحليب", "🕌 مواقيت الصلاة",
    "💊 منبه الجرعات", "📊 بورصة الأسعار", "🏭 المستودعات",
    "📈 الإنتاج اليومي", "🔔 التنبيهات", "📈 التحليلات",
    "💬 التعليقات", "🖨️ الديباجة", "📚 المراجع",
    "💡 المساعدة", "📖 دليل"]
if st.session_state.get("user_role") == "owner":
    tt.append("📧 إرسال الكود")

tabs = st.tabs(tt)

with tabs[0]:
    at = st.tabs(["🐄 أبقار", "🐏 أغنام", "🐐 ماعز", "🐴 خيول", "🐫 إبل",
                   "🐔 دواجن", "🐟 أسماك"])
    with at[0]:
        render_feed_formulation("cattle", "أبقار", "🐄",
            ["كنانة (سوداني)", "بطانة (مدر)", "هولشتاين / محسن"],
            ["تسمين عجول", "حليب/إدرار", "حمل/دفع غذائي", "صيانة"],
            12.0, 65.0, "أبقار", True)
    with at[1]:
        render_feed_formulation("sheep", "أغنام", "🐏",
            ["الضأن الصحراوي", "البربري", "النعيمي"],
            ["تسمين حملان", "حليب/إدرار", "حمل/دفع غذائي", "صيانة"],
            11.5, 62.0, "أغنام", True)
    with at[2]:
        render_feed_formulation("goat", "ماعز", "🐐",
            ["الماعز النوبي", "الماعز الصحراوي", "بور / محسن"],
            ["تسمين جديان", "حليب/إدرار", "حمل/دفع غذائي", "صيانة"],
            11.0, 60.0, "ماعز", True)
    with at[3]:
        render_feed_formulation("horse", "خيول", "🐴",
            ["خيل عربي أصيل", "ثوروبريد", "خيول محلية"],
            ["راحة/صيانة", "عمل خفيف", "عمل متوسط", "عمل مكثف", "سباق",
             "أمهار نامية", "فرسات مرضعات"],
            11.0, 62.0, "خيول", True)
    with at[4]:
        render_feed_formulation("camel", "إبل", "🐫",
            ["عربية", "باختري", "هجين"],
            ["راحة/صيانة", "حمل/رضاعة", "إنتاج حليب", "تسمين", "عمل/نقل"],
            10.0, 58.0, "إبل", True)
    with at[5]:
        render_feed_formulation("poultry", "دواجن", "🐔",
            ["دواجن لاحم", "دواجن بياض", "سمان"],
            ["بادي (0-14 يوم)", "نامي (15-28 يوم)", "ناهي (29-42 يوم)",
             "ناهي متقدم (43+ يوم)"],
            18.0, 72.0, "دواجن", False)
    with at[6]:
        render_feed_formulation("fish", "أسماك", "🐟",
            ["البلطي النيلي", "القرموط"],
            ["زريعة/بادئ", "نمو", "تسمين نهائي", "زريعة متقدمة"],
            28.0, 68.0, "أسماك", False)

with tabs[1]:
    render_smart_lab()

with tabs[2]:
    render_advanced_lab()

with tabs[3]:
    st.markdown('<div class="section-title">🐔 إدارة المزارع</div>',
                unsafe_allow_html=True)
    if get_current_user_role() in ["owner","specialist","veterinarian",
                                     "nutritionist","breeder"]:
        with st.expander("➕ إضافة دورة"):
            c1, c2 = st.columns(2)
            with c1:
                fn = st.text_input("اسم الدورة")
                ib = st.number_input("عدد الكتاكيت", 1, 100000, 1000, 100)
            with c2:
                br = st.selectbox("السلالة", ["Ross 308","Cobb 500","محلية"])
                sd = st.date_input("تاريخ البدء", datetime.now())
            if st.button("💾 إنشاء"):
                if fn:
                    cid = secrets.token_hex(8)
                    st.session_state["broiler_farms"][cid] = {
                        "farm_name": fn, "initial_birds": ib, "breed": br,
                        "start_date": sd.isoformat(), "age_days": 0,
                        "current_weight": 0.045, "total_feed": 0,
                        "dead_count": 0}
                    st.success(f"✅ {fn}")
                    st.rerun()

    if st.session_state["broiler_farms"]:
        for cid, farm in st.session_state["broiler_farms"].items():
            with st.expander(f"🏠 {farm['farm_name']} - {farm['breed']}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("العدد", farm['initial_birds'])
                c1.metric("العمر", farm['age_days'])
                c2.metric("الوزن", f"{farm['current_weight']:.3f}")
                c2.metric("العلف", f"{farm['total_feed']:.1f}")
                mort = ((farm['dead_count']/farm['initial_birds'])*100
                        if farm['initial_birds'] > 0 else 0)
                c3.metric("النفوق %", f"{mort:.1f}")
                c3.metric("النافق", farm['dead_count'])
                u1, u2 = st.columns(2)
                with u1:
                    nw = st.number_input("الوزن", 0.01,
                        value=float(farm['current_weight']), step=0.01,
                        key=f"w_{cid}")
                    nf = st.number_input("العلف", 0.0,
                        value=float(farm['total_feed']), step=1.0,
                        key=f"f_{cid}")
                with u2:
                    nd = st.number_input("النافق", 0, value=0, step=1,
                                          key=f"d_{cid}")
                    na = st.number_input("العمر", 0,
                        value=int(farm['age_days']), step=1, key=f"a_{cid}")
                if st.button("📊 تحديث", key=f"up_{cid}"):
                    farm['current_weight'] = nw
                    farm['total_feed'] = nf
                    farm['dead_count'] += nd
                    farm['age_days'] = na
                    st.rerun()

with tabs[4]:
    st.markdown('<div class="section-title">🍼 بدائل الحليب</div>',
                unsafe_allow_html=True)
    at = st.selectbox("نوع الحيوان:",
        ["عجل بقري", "حملان أغنام", "جديان ماعز", "مهرات خيول", "أطفال إبل"])
    age = st.slider("العمر (يوم)", 1, 120, 30)
    needs = {"عجل بقري": {"protein": 22, "fat": 18, "volume": 8},
             "حملان أغنام": {"protein": 24, "fat": 20, "volume": 4},
             "جديان ماعز": {"protein": 23, "fat": 19, "volume": 3},
             "مهرات خيول": {"protein": 20, "fat": 15, "volume": 5},
             "أطفال إبل": {"protein": 21, "fat": 17, "volume": 6}}
    af = 1.2 if age < 14 else 1.0 if age < 30 else 0.85 if age < 60 else 0.70
    tp = needs[at]["protein"] * af
    tf = needs[at]["fat"] * af
    dv = needs[at]["volume"] * af
    st.info(f"📊 بروتين {tp:.1f}% | دهون {tf:.1f}% | حجم {dv:.1f} ل")

    replacer = {
        "حليب مجفف خالي الدسم": {"CP": 34.0, "Fat": 1.0, "Cost": 18.0},
        "مصل الحليب المجفف (Whey)": {"CP": 12.0, "Fat": 1.0, "Cost": 12.0},
        "دهن نباتي (زيت نباتي)": {"CP": 0.0, "Fat": 99.0, "Cost": 8.0},
        "ليسيثين الصويا": {"CP": 0.0, "Fat": 95.0, "Cost": 15.0},
        "بروتين الصويا المركز": {"CP": 65.0, "Fat": 1.0, "Cost": 20.0},
        "فيتامينات ومعادن (Premix)": {"CP": 0.0, "Fat": 0.0, "Cost": 25.0}}
    selected = []
    prices = {}
    cols = st.columns(3)
    for i, (ing, d) in enumerate(replacer.items()):
        with cols[i % 3]:
            if st.checkbox(ing, value=(i < 4), key=f"rep_{ing}"):
                selected.append(ing)
                prices[ing] = st.number_input(
                    f"سعر {ing}", 1.0, value=float(d["Cost"]), step=0.5,
                    key=f"repp_{ing}")
    if st.button("🍼 تشغيل", type="primary"):
        if len(selected) < 3:
            st.warning("⚠️ اختر 3+")
        else:
            with st.spinner("..."):
                c = [prices[i] for i in selected]
                b = [(0, 100) for _ in selected]
                Ae = [[1]*len(selected)]
                be = [100]
                Ae.append([replacer[i]["CP"] for i in selected])
                be.append(tp)
                Au = [[-replacer[i]["Fat"] for i in selected]]
                bu = [-tf]
                r = linprog(c, A_ub=Au, b_ub=bu, A_eq=Ae, b_eq=be,
                            bounds=b, method='highs')
                if r.success:
                    f = {selected[i]: r.x[i]
                         for i in range(len(selected)) if r.x[i] > 0.0001}
                    ck = r.fun / 100.0
                    st.success(f"✅ ${ck:.2f}/كجم")
                    rows = [["المكون","النسبة %","جم/كجم"]]
                    for k, v in f.items():
                        rows.append([k, f"{v:.1f}%", f"{v*10:.1f}"])
                    show_arabic_table(rows, "#2e7d32",
                                      ["50%","25%","25%"])
                    st.info(f"📌 الجرعة: {dv:.1f} لتر/يوم")

with tabs[5]:
    st.markdown("### 🕌 مواقيت الصلاة")
    city = st.selectbox("المدينة:",
        ["مكة المكرمة", "المدينة المنورة", "الخرطوم", "طرابلس",
         "القاهرة", "دبي", "الرياض"])
    times = {"الفجر": "05:00", "الشروق": "06:30", "الظهر": "12:00",
             "العصر": "15:30", "المغرب": "18:00", "العشاء": "19:30"}
    st.markdown(f"#### 📍 {city}")
    rows = [["الصلاة", "الوقت"]]
    for n, t in times.items():
        rows.append([n, t])
    show_arabic_table(rows, "#1565C0", ["50%","50%"])

with tabs[6]:
    st.markdown("### 💊 منبه الجرعات")
    with st.expander("➕ إضافة"):
        c1, c2, c3 = st.columns(3)
        with c1:
            at = st.selectbox("الحيوان",
                ["أبقار","أغنام","ماعز","خيول","إبل","دواجن","أسماك"])
            dt = st.selectbox("النوع",
                ["لقاح","فيتامين","دواء","مضاد طفيليات"])
            dn = st.text_input("الاسم")
        with c2:
            da = st.number_input("الجرعة", 0.0, value=1.0, step=0.1)
            du = st.selectbox("الوحدة", ["مل","جم","مجم","قطرة"])
            ar_ = st.selectbox("الطريقة",
                ["عضل","تحت الجلد","فموي","مياه الشرب"])
        with c3:
            fd = st.number_input("كل (أيام)", 1, value=7)
            sd = st.date_input("البدء", datetime.now())
            notes = st.text_area("ملاحظات")
        if st.button("💾"):
            if dn:
                st.session_state["dose_reminders"].append({
                    'id': secrets.token_hex(8), 'animal': at, 'type': dt,
                    'name': dn, 'amount': da, 'unit': du, 'route': ar_,
                    'freq': fd, 'start': sd.isoformat(),
                    'next': (sd + timedelta(days=fd)).isoformat()})
                st.rerun()
    if st.session_state["dose_reminders"]:
        rows = [["الاسم","الحيوان","الجرعة","التكرار","القادم"]]
        for r in st.session_state["dose_reminders"]:
            rows.append([r['name'], r['animal'],
                          f"{r['amount']} {r['unit']}",
                          f"كل {r['freq']} يوم", r['next'][:10]])
        show_arabic_table(rows, "#c62828")

with tabs[7]:
    st.markdown('<div class="section-title">📊 بورصة الأسعار</div>',
                unsafe_allow_html=True)
    if get_current_user_role() in ["owner","specialist"]:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🐄 المواشي")
            for n in list(st.session_state["global_livestock_prices"].keys()):
                p = st.session_state["global_livestock_prices"][n]
                np_ = st.number_input(n, value=float(p), step=5.0,
                                        key=f"pl_{n}")
                st.session_state["global_livestock_prices"][n] = np_
        with c2:
            st.subheader("🥩 المنتجات")
            for n in list(st.session_state["global_products_prices"].keys()):
                p = st.session_state["global_products_prices"][n]
                np_ = st.number_input(n, value=float(p), step=0.5,
                                        key=f"pp_{n}")
                st.session_state["global_products_prices"][n] = np_
    else:
        rows = [["المنتج", "السعر ($)"]]
        for n, p in st.session_state["global_livestock_prices"].items():
            rows.append([n, f"{p:.2f}"])
        show_arabic_table(rows, "#2e7d32", ["60%","40%"])

with tabs[8]:
    st.markdown('<div class="section-title">🏭 المستودعات</div>',
                unsafe_allow_html=True)
    rows = [["المادة","الكمية (طن)","الحد الأدنى","الحالة"]]
    for item, data in st.session_state["inventory"].items():
        qty = data["quantity"] if isinstance(data, dict) else data
        thr = (data.get("min_threshold", 5.0)
               if isinstance(data, dict) else 5.0)
        st_ = ("🔴 نفذ" if qty <= 0
               else "🟡 منخفض" if qty < thr else "🟢 آمن")
        rows.append([item, f"{qty:.1f}", f"{thr:.1f}", st_])
    show_arabic_table(rows, "#2e7d32")

with tabs[9]:
    st.markdown('<div class="section-title">📈 الإنتاج اليومي</div>',
                unsafe_allow_html=True)
    with st.form("daily"):
        c1, c2, c3 = st.columns(3)
        with c1:
            f = st.text_input("المزرعة")
            d = st.date_input("التاريخ", datetime.now())
        with c2:
            mk = st.number_input("حليب (لتر)", 0.0)
            eg = st.number_input("بيض (عدد)", 0)
        with c3:
            wg = st.number_input("زيادة الوزن (كجم)", 0.0)
            mo = st.number_input("النافق", 0)
        if st.form_submit_button("💾 حفظ"):
            st.session_state["daily_production_log"].append({
                "farm": f, "date": d.isoformat(), "milk": mk,
                "eggs": eg, "weight_gain": wg, "mortality": mo})
            st.success("✅")
    if st.session_state["daily_production_log"]:
        rows = [["المزرعة","التاريخ","حليب","بيض","وزن","نافق"]]
        for r in st.session_state["daily_production_log"]:
            rows.append([r['farm'], r['date'][:10], r['milk'],
                          r['eggs'], r['weight_gain'], r['mortality']])
        show_arabic_table(rows, "#2e7d32")

with tabs[10]:
    st.markdown("### 🔔 التنبيهات")
    warns = InventoryManager.check_levels()
    if warns:
        rows = [["المادة", "الحالة"]]
        for item, info in warns.items():
            rows.append([item, info['status']])
        show_arabic_table(rows, "#c62828", ["60%","40%"])
    else:
        st.success("✅ لا توجد تنبيهات")

with tabs[11]:
    st.markdown('<div class="section-title">📈 التحليلات</div>',
                unsafe_allow_html=True)
    p = PricePredictor()
    for ing in ["ذرة صفراء", "كسب فول صويا 44%", "نخالة قمح (ردة)"]:
        pred = p.predict_price(ing, 7)
        if pred.get('prediction'):
            ic = ("📈" if pred.get('trend') == 'up'
                  else "📉" if pred.get('trend') == 'down' else "➡️")
            cp = pred.get('current_price') or 0
            st.metric(f"{ic} {ing}", f"${pred['prediction']:.2f}",
                      delta=f"{pred['prediction'] - cp:.2f}")

    dates = pd.date_range(start='2024-01-01', periods=12, freq='ME')
    df = pd.DataFrame({
        'التاريخ': dates,
        'الذرة': [220,225,230,228,235,240,238,242,245,248,250,252],
        'الصويا': [440,445,442,448,450,455,452,458,460,462,465,468]})
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['التاريخ'], y=df['الذرة'],
        mode='lines+markers', name='الذرة',
        line=dict(color='#2e7d32', width=2)))
    fig.add_trace(go.Scatter(x=df['التاريخ'], y=df['الصويا'],
        mode='lines+markers', name='الصويا',
        line=dict(color='#1565C0', width=2)))
    fig.update_layout(title='اتجاه أسعار المواد الخام',
                      font=dict(family="Cairo, Tajawal, sans-serif"))
    st.plotly_chart(fig, use_container_width=True)

with tabs[12]:
    st.markdown('<div class="section-title">💬 التعليقات</div>',
                unsafe_allow_html=True)
    st.text_area("الحالية:", value=st.session_state["shared_comments"],
                 height=200, disabled=True)
    nc = st.text_area("جديد:")
    if st.button("➕ نشر"):
        if nc:
            role = ("المالك" if st.session_state["user_role"] == "owner"
                    else "مختص")
            st.session_state["shared_comments"] += \
                f"\n• [{role} {datetime.now().strftime('%H:%M')}]: {nc}"
            st.rerun()

with tabs[13]:
    st.markdown('<div class="section-title">🖨️ الديباجة</div>',
                unsafe_allow_html=True)
    brand = st.text_input("البراند:",
                           "منصة تاور نولجي Tawornology العلمية")
    st.markdown(f"""
    <div style='border:3px dashed #1b5e20; padding:30px;
                border-radius:15px;
                background:linear-gradient(135deg,#f1f8e9,#e8f5e9);
                direction:rtl; text-align:center;'>
        <h2 style='color:#1b5e20;'>🌟 {brand} 🌟</h2>
        <h3 style='color:#c62828;'>
            الاختصاصي م. عبد القادر إسماعيل تاور</h3>
        <p style='background:#e8f5e9; padding:10px; border-radius:8px;'>
        🎯 {st.session_state.get('active_stage_title','إنتاج عام')} |
        DP: {st.session_state.get('active_cp_tag', 12):.1f}% |
        SE: {st.session_state.get('active_se_tag', 65):.1f}</p>
    </div>
    """, unsafe_allow_html=True)

with tabs[14]:
    st.markdown('<div class="section-title">📚 المراجع</div>',
                unsafe_allow_html=True)
    for ck, cd in ScientificReferenceSystem.REFERENCES.items():
        with st.expander(f"{cd['icon']} {cd['title']}"):
            for ref in cd["references"]:
                st.markdown(f"""
                <div style='background:#f8f9fa; padding:12px;
                            border-radius:8px; margin-bottom:8px;
                            border-right:4px solid #2e7d32;'>
                    <b>{ref['title']}</b><br>
                    👤 {ref['authors']} | 📅 {ref['year']}<br>
                    <small>{ref['summary']}</small>
                </div>
                """, unsafe_allow_html=True)
    q = st.text_input("اسأل:")
    if q:
        a = ScientificReferenceSystem.get_answer(q)
        if a:
            st.success(f"📖 {a['answer']}")
            st.info(f"🔹 {a['simplified']}")

with tabs[15]:
    st.markdown("""
    ### 🌟 خطوات الاستخدام:
    1. اختر نوع الحيوان
    2. حدد الموقع والسلالة والمرحلة
    3. **النظام يعرض الاحتياجات القياسية تلقائياً** (DP, SE, أملاح, ألياف)
    4. اختر **المواد المتاحة عندك** فقط
    5. اضغط **تشغيل المحرك الشامل**
    6. النظام يحسب النسب التي تحقق **كل** الاحتياجات معاً

    ### 🧪 المختبر:
    - CP, DP, SE + أملاح + ألياف
    - مقارنة تلقائية مع المعايير
    - تقرير PDF مفصل
    """)

with tabs[16]:
    st.markdown("""
    <div class="manual-book">
    <div class="book-chapter">📘 مقدمة v19.3</div>
    <div class="book-body">
    محرك التركيب الشامل v19.3 يحل مشكلة القيود المتعددة عبر خوارزمية
    البرمجة الخطية التي تأخذ كل الاحتياجات في الاعتبار في آن واحد.
    </div>
    <div class="book-chapter">🎯 المحرك الشامل</div>
    <div class="book-body">
    عند اختيار المواد المتاحة، يقوم النظام بـ:<br>
    1. بناء 15+ قيداً غذائياً (طاقة، بروتين، 7 معادن، 4 ألياف، Ca:P)<br>
    2. حل المعادلة بأقل تكلفة<br>
    3. التحقق من تحقيق كل قيد<br>
    4. تخفيف المرونة تلقائياً إذا فشل الحل الدقيق
    </div>
    <div class="book-chapter">📊 التحقق</div>
    <div class="book-body">
    بعد الحل، يعرض النظام جدولين:<br>
    - جدول الأملاح: القيمة المحققة vs القياسية<br>
    - جدول الألياف: القيمة المحققة vs القياسية
    </div>
    </div>
    """, unsafe_allow_html=True)

if get_current_user_role() == "owner" and len(tabs) > 17:
    with tabs[17]:
        st.markdown('<div class="section-title">📧 إرسال الكود</div>',
                    unsafe_allow_html=True)
        em = st.text_input("البريد:", value=OWNER_EMAIL)
        if st.button("📤 إرسال"):
            if em and '@' in em:
                with st.spinner("..."):
                    ok, msg = send_code_to_email(em)
                    st.success(msg) if ok else st.error(msg)


st.markdown("""
<div style='text-align:center; padding:20px; margin-top:30px;
            border-top:2px solid #e0e0e0; color:#888;'>
🌾 <b>تاور نولجي Tawornology v19.3</b><br>
© 2026 | الاختصاصي م. عبد القادر إسماعيل تاور<br>
🕊️ إهداء إلى روح والدي <b>إسماعيل تاور</b> وأختي <b>ابتسام</b>
</div>
""", unsafe_allow_html=True)

if st.button("🔊 اختبار الصوت"):
    voice_guide("بسم الله، اختبار النظام.")

# ============================================================================
# نهاية v19.3 - محرك التركيب الشامل
# ============================================================================
